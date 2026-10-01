"""Metriche pure per file GPX.

Il modulo non dipende dalla GUI: legge il GPX, conserva la separazione dei
segmenti e restituisce metriche pronte per il successivo salvataggio.
"""

from __future__ import annotations

import math
from typing import Any

import gpxpy


STATI_ANALISI = frozenset(
    {"NON_CALCOLATO", "IN_CODA", "IN_CORSO", "PARZIALE", "COMPLETO", "ERRORE"}
)

_SOGLIA_DUPLICATO_M = 1.0
_QUOTA_MIN_PLAUSIBILE_M = -500.0
_QUOTA_MAX_PLAUSIBILE_M = 10000.0


def calcola_distanza_haversine(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Restituisce la distanza geodetica in chilometri tra due coordinate."""
    raggio_terra_km = 6371.0088
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    valore = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(delta_lon / 2) ** 2
    )
    valore = min(1.0, max(0.0, valore))
    return 2 * raggio_terra_km * math.asin(math.sqrt(valore))


def _risultato_errore(messaggio: str) -> dict[str, Any]:
    """Costruisce una risposta coerente per gli errori non recuperabili."""
    return {
        "stato": "ERRORE",
        "errore": messaggio,
        "distanza_km": 0.0,
        "dislivello_pos_m": None,
        "dislivello_neg_m": None,
        "quota_min_m": None,
        "quota_max_m": None,
        "pendenza_media_pct": None,
        "pendenza_max_pct": None,
        "bbox": None,
        "numero_punti": 0,
        "numero_punti_originali": 0,
        "numero_segmenti": 0,
        "numero_tracce": 0,
        "anomalie": [],
    }


def _coordinate_valide(latitudine: Any, longitudine: Any) -> bool:
    """Controlla che le coordinate siano numeriche e nel loro intervallo."""
    if not isinstance(latitudine, (int, float)) or not isinstance(
        longitudine, (int, float)
    ):
        return False
    return (
        math.isfinite(float(latitudine))
        and math.isfinite(float(longitudine))
        and -90.0 <= float(latitudine) <= 90.0
        and -180.0 <= float(longitudine) <= 180.0
    )


def _quota_valida(quota: Any) -> bool:
    """Accetta solo quote finite e comprese in un intervallo plausibile."""
    return (
        isinstance(quota, (int, float))
        and math.isfinite(float(quota))
        and _QUOTA_MIN_PLAUSIBILE_M <= float(quota) <= _QUOTA_MAX_PLAUSIBILE_M
    )


def _punto_senza_duplicati(segmento: list[Any]) -> list[Any]:
    """Scarta solo i punti consecutivi distanti meno di un metro."""
    punti_puliti: list[Any] = []
    for punto in segmento:
        if not _coordinate_valide(punto.latitude, punto.longitude):
            continue
        if not punti_puliti:
            punti_puliti.append(punto)
            continue
        precedente = punti_puliti[-1]
        distanza_m = calcola_distanza_haversine(
            precedente.latitude,
            precedente.longitude,
            punto.latitude,
            punto.longitude,
        ) * 1000
        if distanza_m >= _SOGLIA_DUPLICATO_M:
            punti_puliti.append(punto)
    return punti_puliti


def _arrotonda_metriche(risultato: dict[str, Any]) -> dict[str, Any]:
    """Applica precisioni stabili alle metriche numeriche."""
    for chiave in ("distanza_km", "pendenza_media_pct", "pendenza_max_pct"):
        if risultato[chiave] is not None:
            risultato[chiave] = round(float(risultato[chiave]), 3)
    for chiave in ("dislivello_pos_m", "dislivello_neg_m", "quota_min_m", "quota_max_m"):
        if risultato[chiave] is not None:
            risultato[chiave] = round(float(risultato[chiave]), 3)
    return risultato


def analizza_gpx(percorso_file: str) -> dict[str, Any]:
    """Legge un GPX e restituisce distanza, altimetria, pendenza e anomalie."""
    try:
        with open(percorso_file, "r", encoding="utf-8") as file_gpx:
            gpx = gpxpy.parse(file_gpx)
    except FileNotFoundError:
        return _risultato_errore(f"file GPX non trovato: {percorso_file}")
    except (OSError, UnicodeError) as exc:
        return _risultato_errore(f"impossibile leggere il file GPX: {exc}")
    except Exception as exc:
        return _risultato_errore(f"file GPX non valido: {exc}")

    tracce = list(gpx.tracks)
    segmenti = [segmento for traccia in tracce for segmento in traccia.segments]
    punti_originali = [
        punto for segmento in segmenti for punto in segmento.points
    ]
    if not tracce or not segmenti or not punti_originali:
        return _risultato_errore("GPX vuoto: nessuna traccia con punti")

    anomalie: list[str] = []
    if len(tracce) > 1:
        anomalie.append("file con più tracce")

    segmenti_puliti = [_punto_senza_duplicati(segmento.points) for segmento in segmenti]
    punti_puliti = [punto for segmento in segmenti_puliti for punto in segmento]
    if not punti_puliti:
        return _risultato_errore("GPX senza coordinate valide")

    distanza_totale_km = 0.0
    incrementi_quota: list[tuple[float, float]] = []
    quote_valide: list[float] = []
    quote_incomplete = False
    coordinate = [
        (float(punto.latitude), float(punto.longitude)) for punto in punti_puliti
    ]

    for segmento in segmenti_puliti:
        for precedente, corrente in zip(segmento, segmento[1:]):
            distanza_km = calcola_distanza_haversine(
                precedente.latitude,
                precedente.longitude,
                corrente.latitude,
                corrente.longitude,
            )
            distanza_totale_km += distanza_km

            quota_precedente = precedente.elevation
            quota_corrente = corrente.elevation
            if _quota_valida(quota_precedente) and _quota_valida(quota_corrente):
                quota_precedente_float = float(quota_precedente)
                quota_corrente_float = float(quota_corrente)
                quote_valide.extend((quota_precedente_float, quota_corrente_float))
                incrementi_quota.append(
                    (quota_corrente_float - quota_precedente_float, distanza_km)
                )
            else:
                quote_incomplete = True

    if any(not _quota_valida(punto.elevation) for punto in punti_puliti):
        quote_incomplete = True
    if quote_incomplete:
        anomalie.append("quote mancanti o inaffidabili")

    bbox = {
        "min_lat": min(latitudine for latitudine, _ in coordinate),
        "min_lon": min(longitudine for _, longitudine in coordinate),
        "max_lat": max(latitudine for latitudine, _ in coordinate),
        "max_lon": max(longitudine for _, longitudine in coordinate),
    }
    risultato: dict[str, Any] = {
        "stato": "PARZIALE" if anomalie else "COMPLETO",
        "errore": None,
        "distanza_km": distanza_totale_km,
        "dislivello_pos_m": None,
        "dislivello_neg_m": None,
        "quota_min_m": None,
        "quota_max_m": None,
        "pendenza_media_pct": None,
        "pendenza_max_pct": None,
        "bbox": bbox,
        "numero_punti": len(punti_puliti),
        "numero_punti_originali": len(punti_originali),
        "numero_segmenti": len(segmenti),
        "numero_tracce": len(tracce),
        "anomalie": anomalie,
    }

    if not quote_incomplete and quote_valide:
        misure_pendenza_scartate = 0
        dislivello_pos = sum(
            delta for delta, _ in incrementi_quota if delta > 0
        )
        dislivello_neg = sum(
            abs(delta) for delta, _ in incrementi_quota if delta < 0
        )
        misure_valide = []
        for delta, distanza in incrementi_quota:
            # Escludi tratti troppo brevi o con pendenze incompatibili con la bici.
            pendenza = abs(delta / (distanza * 1000) * 100) if distanza > 0 else 0.0
            if distanza * 1000 < 5 or pendenza > 35:
                misure_pendenza_scartate += 1
                continue
            misure_valide.append((delta, distanza, pendenza))
        distanza_quote_km = sum(distanza for _, distanza, _ in misure_valide)
        pendenze = [pendenza for _, _, pendenza in misure_valide]
        if misure_pendenza_scartate:
            anomalie.append(
                f"{misure_pendenza_scartate} misure di pendenza scartate come anomale"
            )
        risultato.update(
            {
                "dislivello_pos_m": dislivello_pos,
                "dislivello_neg_m": dislivello_neg,
                "quota_min_m": min(quote_valide),
                "quota_max_m": max(quote_valide),
                "pendenza_media_pct": (
                    sum(delta for delta, _, _ in misure_valide)
                    / (distanza_quote_km * 1000)
                    * 100
                    if distanza_quote_km > 0
                    else 0.0
                ),
                "pendenza_max_pct": max(pendenze) if pendenze else 0.0,
            }
        )

    return _arrotonda_metriche(risultato)
