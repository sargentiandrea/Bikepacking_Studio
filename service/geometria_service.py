"""Estrazione, semplificazione e compressione della geometria GPX."""

from __future__ import annotations

import gzip
import json
import math
from typing import Any

import gpxpy


VERSIONE_ALGORITMO_GEOMETRIA = "rdp-v1-50m"
TOLLERANZA_SEMPLIFICAZIONE_METRI = 50.0
RAGGIO_TERRESTRE_METRI = 6_371_008.8


def _proietta_coordinate(
    coordinate: list[list[float]],
) -> list[tuple[float, float]]:
    """Proietta un segmento su un piano azimutale equidistante locale."""
    latitudine_origine = math.radians(coordinate[0][1])
    longitudine_origine = math.radians(coordinate[0][0])
    cos_lat_origine = math.cos(latitudine_origine)
    sin_lat_origine = math.sin(latitudine_origine)
    proiettate = []

    for longitudine, latitudine in coordinate:
        lat = math.radians(latitudine)
        lon = math.radians(longitudine)
        delta_lon = (lon - longitudine_origine + math.pi) % (2 * math.pi) - math.pi
        cos_c = (
            sin_lat_origine * math.sin(lat)
            + cos_lat_origine * math.cos(lat) * math.cos(delta_lon)
        )
        angolo = math.acos(max(-1.0, min(1.0, cos_c)))
        sin_angolo = math.sin(angolo)
        fattore = angolo / sin_angolo if abs(sin_angolo) > 1e-12 else 1.0
        x = (
            RAGGIO_TERRESTRE_METRI
            * fattore
            * math.cos(lat)
            * math.sin(delta_lon)
        )
        y = (
            RAGGIO_TERRESTRE_METRI
            * fattore
            * (
                cos_lat_origine * math.sin(lat)
                - sin_lat_origine * math.cos(lat) * math.cos(delta_lon)
            )
        )
        proiettate.append((x, y))
    return proiettate


def _distanza_punto_segmento(
    punto: tuple[float, float],
    inizio: tuple[float, float],
    fine: tuple[float, float],
) -> float:
    dx = fine[0] - inizio[0]
    dy = fine[1] - inizio[1]
    if dx == 0 and dy == 0:
        return math.hypot(punto[0] - inizio[0], punto[1] - inizio[1])

    fattore = (
        (punto[0] - inizio[0]) * dx + (punto[1] - inizio[1]) * dy
    ) / (dx * dx + dy * dy)
    fattore = max(0.0, min(1.0, fattore))
    proiezione = (inizio[0] + fattore * dx, inizio[1] + fattore * dy)
    return math.hypot(punto[0] - proiezione[0], punto[1] - proiezione[1])


def semplifica_segmento_rdp(
    coordinate: list[list[float]],
    tolleranza_metri: float = TOLLERANZA_SEMPLIFICAZIONE_METRI,
) -> list[list[float]]:
    """Semplifica un singolo segmento con RDP, mantenendo sempre gli estremi."""
    if len(coordinate) <= 2:
        return coordinate.copy()
    if tolleranza_metri < 0:
        raise ValueError("La tolleranza di semplificazione non può essere negativa")

    proiettate = _proietta_coordinate(coordinate)
    mantenuti = {0, len(coordinate) - 1}
    intervalli = [(0, len(coordinate) - 1)]

    while intervalli:
        inizio, fine = intervalli.pop()
        distanza_massima = tolleranza_metri
        indice_massimo = None
        for indice in range(inizio + 1, fine):
            distanza = _distanza_punto_segmento(
                proiettate[indice],
                proiettate[inizio],
                proiettate[fine],
            )
            if distanza > distanza_massima:
                distanza_massima = distanza
                indice_massimo = indice

        if indice_massimo is not None:
            mantenuti.add(indice_massimo)
            intervalli.append((inizio, indice_massimo))
            intervalli.append((indice_massimo, fine))

    return [coordinate[indice] for indice in sorted(mantenuti)]


def comprimi_segmenti(segmenti: list[list[list[float]]]) -> bytes:
    """Codifica i segmenti come JSON gzip deterministico."""
    contenuto = json.dumps(
        segmenti,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return gzip.compress(contenuto, mtime=0)


def decomprimi_segmenti(dati_compressi: bytes) -> list[list[list[float]]]:
    """Decodifica la geometria compressa validando coordinate e segmenti."""
    contenuto = json.loads(gzip.decompress(dati_compressi).decode("utf-8"))
    if not isinstance(contenuto, list):
        raise ValueError("Formato geometria non valido")

    segmenti: list[list[list[float]]] = []
    for segmento in contenuto:
        if not isinstance(segmento, list):
            raise ValueError("Segmento geometrico non valido")
        coordinate_segmento = []
        for punto in segmento:
            if (
                not isinstance(punto, list)
                or len(punto) != 2
                or not all(isinstance(valore, (int, float)) for valore in punto)
                or not all(math.isfinite(valore) for valore in punto)
            ):
                raise ValueError("Coordinata geometrica non valida")
            longitudine, latitudine = punto
            if not -180 <= longitudine <= 180 or not -90 <= latitudine <= 90:
                raise ValueError("Coordinata fuori intervallo")
            coordinate_segmento.append([float(longitudine), float(latitudine)])
        segmenti.append(coordinate_segmento)
    return segmenti


def calcola_geometria_gpx(percorso_file: str) -> dict[str, Any]:
    """Estrae i punti GPX e genera geometria completa e semplificata."""
    with open(percorso_file, "r", encoding="utf-8", errors="ignore") as file_gpx:
        traccia_gpx = gpxpy.parse(file_gpx)

    segmenti = []
    for traccia in traccia_gpx.tracks:
        for segmento in traccia.segments:
            coordinate_segmento = [
                [float(punto.longitude), float(punto.latitude)]
                for punto in segmento.points
                if punto.latitude is not None and punto.longitude is not None
            ]
            if coordinate_segmento:
                segmenti.append(coordinate_segmento)

    if not segmenti:
        raise ValueError("GPX senza coordinate utilizzabili per la geometria")

    longitudini = [
        punto[0] for segmento in segmenti for punto in segmento
    ]
    latitudini = [
        punto[1] for segmento in segmenti for punto in segmento
    ]
    segmenti_semplificati = [
        semplifica_segmento_rdp(segmento)
        for segmento in segmenti
    ]
    return {
        "geometria_completa": comprimi_segmenti(segmenti),
        "geometria_semplificata": comprimi_segmenti(segmenti_semplificati),
        "versione_algoritmo": VERSIONE_ALGORITMO_GEOMETRIA,
        "bbox_min_lat": min(latitudini),
        "bbox_min_lon": min(longitudini),
        "bbox_max_lat": max(latitudini),
        "bbox_max_lon": max(longitudini),
        "numero_punti_originali": sum(len(segmento) for segmento in segmenti),
        "numero_punti_semplificati": sum(
            len(segmento) for segmento in segmenti_semplificati
        ),
    }


def geometria_geojson(segmenti: list[list[list[float]]]) -> dict[str, Any]:
    """Restituisce una geometria GeoJSON senza collegare segmenti distinti."""
    if len(segmenti) == 1:
        return {"type": "LineString", "coordinates": segmenti[0]}
    return {"type": "MultiLineString", "coordinates": segmenti}
