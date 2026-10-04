"""Classificazione geometrica dei punti di passaggio rispetto a una rotta."""

import math
from collections.abc import Sequence

from service.geo_utils import calcola_distanza_haversine


SOGLIA_GIA_SUL_PERCORSO_METRI = 100.0
SOGLIA_TAPPA_VICINA_KM = 5.0
_RAGGIO_TERRA_METRI = 6_371_000.0


def _valida_coordinate(coordinate):
    """Converte una coordinata Lat/Lon e ne verifica intervalli e valori finiti."""
    if not isinstance(coordinate, Sequence) or len(coordinate) < 2:
        raise ValueError("Ogni coordinata deve contenere latitudine e longitudine.")
    try:
        latitudine, longitudine = float(coordinate[0]), float(coordinate[1])
    except (TypeError, ValueError) as errore:
        raise ValueError("La coordinata contiene valori non numerici.") from errore
    if (
        not math.isfinite(latitudine)
        or not math.isfinite(longitudine)
        or not -90 <= latitudine <= 90
        or not -180 <= longitudine <= 180
    ):
        raise ValueError("La coordinata è fuori dagli intervalli Lat/Lon validi.")
    return latitudine, longitudine


def _normalizza_linee(coordinate):
    """Raccoglie una linea o più segmenti in liste di coordinate Lat/Lon."""
    if not coordinate:
        return []
    prima = coordinate[0]
    if (
        isinstance(prima, Sequence)
        and len(prima) >= 2
        and isinstance(prima[0], (int, float))
    ):
        linee = [coordinate]
    else:
        linee = coordinate
    risultato = []
    for linea in linee:
        coordinate_valide = [_valida_coordinate(punto) for punto in linea]
        if coordinate_valide:
            risultato.append(coordinate_valide)
    return risultato


def _distanza_punto_segmento_km(punto, inizio, fine):
    """Stima la proiezione più vicina sul segmento e misura il residuo con Haversine."""
    latitudine_punto, longitudine_punto = punto
    latitudine_inizio, longitudine_inizio = inizio
    latitudine_fine, longitudine_fine = fine
    cos_latitudine = max(
        1e-6, abs(math.cos(math.radians(latitudine_punto)))
    )

    def proietta(latitudine, longitudine):
        delta_lon = (longitudine - longitudine_punto + 180) % 360 - 180
        return (
            math.radians(delta_lon) * _RAGGIO_TERRA_METRI * cos_latitudine,
            math.radians(latitudine - latitudine_punto) * _RAGGIO_TERRA_METRI,
        )

    x_inizio, y_inizio = proietta(latitudine_inizio, longitudine_inizio)
    x_fine, y_fine = proietta(latitudine_fine, longitudine_fine)
    delta_x = x_fine - x_inizio
    delta_y = y_fine - y_inizio
    lunghezza_quadrata = delta_x * delta_x + delta_y * delta_y
    if lunghezza_quadrata == 0:
        fattore = 0.0
    else:
        fattore = max(
            0.0,
            min(
                1.0,
                -(x_inizio * delta_x + y_inizio * delta_y)
                / lunghezza_quadrata,
            ),
        )

    latitudine_proiettata = latitudine_inizio + fattore * (
        latitudine_fine - latitudine_inizio
    )
    delta_lon = (longitudine_fine - longitudine_inizio + 180) % 360 - 180
    longitudine_proiettata = (
        longitudine_inizio + fattore * delta_lon + 180
    ) % 360 - 180
    return calcola_distanza_haversine(
        latitudine_punto,
        longitudine_punto,
        latitudine_proiettata,
        longitudine_proiettata,
    )


def _distanza_punto_linee_km(punto, linee):
    """Restituisce la distanza minima in chilometri tra un punto e più linee."""
    distanze = []
    for linea in linee:
        if len(linea) == 1:
            distanze.append(
                calcola_distanza_haversine(*punto, *linea[0])
            )
        else:
            distanze.extend(
                _distanza_punto_segmento_km(punto, inizio, fine)
                for inizio, fine in zip(linea, linea[1:])
            )
    return min(distanze) if distanze else None


def classifica_punto(coordinate_rotta, tappe, punto):
    """Classifica un punto come già sulla rotta, vicino a una tappa o lontano.

    Le coordinate e le geometrie delle tappe sono espresse come (latitudine,
    longitudine). Il campo ``coordinate`` di ciascuna tappa può contenere una
    linea oppure più segmenti; la geometria della rotta accetta la stessa forma.
    """
    punto_valido = _valida_coordinate(punto)
    linee_rotta = _normalizza_linee(coordinate_rotta)
    tappe_valide = []
    for tappa in tappe:
        linee_tappa = _normalizza_linee(tappa.get("coordinate", []))
        if linee_tappa:
            tappe_valide.append(
                {
                    "id": tappa.get("id"),
                    "sequenza": tappa.get("sequenza"),
                    "linee": linee_tappa,
                }
            )

    if not linee_rotta:
        linee_rotta = [
            linea
            for tappa in tappe_valide
            for linea in tappa["linee"]
        ]
    if not linee_rotta:
        raise ValueError("Non ci sono geometrie di rotta da confrontare.")

    distanza_rotta_km = _distanza_punto_linee_km(punto_valido, linee_rotta)
    if distanza_rotta_km is None:
        raise ValueError("La rotta non contiene coordinate confrontabili.")
    if distanza_rotta_km * 1000 < SOGLIA_GIA_SUL_PERCORSO_METRI:
        return {
            "classificazione": "gia_sul_percorso",
            "distanza_rotta_m": distanza_rotta_km * 1000,
            "distanza_tappa_km": None,
            "tappa_id": None,
        }

    vicina = None
    for tappa in tappe_valide:
        distanza_tappa_km = _distanza_punto_linee_km(
            punto_valido, tappa["linee"]
        )
        if distanza_tappa_km is None:
            continue
        if vicina is None or distanza_tappa_km < vicina["distanza_tappa_km"]:
            vicina = {
                "distanza_tappa_km": distanza_tappa_km,
                "tappa_id": tappa["id"],
                "tappa_sequenza": tappa["sequenza"],
            }

    if vicina and vicina["distanza_tappa_km"] < SOGLIA_TAPPA_VICINA_KM:
        return {
            "classificazione": "vicino_a_tappa",
            "distanza_rotta_m": distanza_rotta_km * 1000,
            **vicina,
        }
    return {
        "classificazione": "lontano",
        "distanza_rotta_m": distanza_rotta_km * 1000,
        "distanza_tappa_km": (
            vicina["distanza_tappa_km"] if vicina else None
        ),
        "tappa_id": vicina["tappa_id"] if vicina else None,
        "tappa_sequenza": vicina["tappa_sequenza"] if vicina else None,
    }
