"""Funzioni geometriche pure (senza GUI né database) condivise dal progetto."""

import math

# Raggio usato storicamente da audit, dashboard, mappa e gap tra tappe.
RAGGIO_TERRA_KM = 6371.0
# Raggio medio WGS84 usato dalle metriche GPX precalcolate: cambiarlo
# altererebbe i valori già salvati, quindi resta un valore distinto.
RAGGIO_TERRA_MEDIO_KM = 6371.0088


def calcola_distanza_haversine(lat1, lon1, lat2, lon2, raggio_km=RAGGIO_TERRA_KM):
    """Distanza in linea d'aria, in chilometri, tra due coordinate (formula di Haversine).

    Parametri: latitudine e longitudine in gradi dei due punti; `raggio_km` è
    il raggio della Terra da usare (di default 6371.0 km).
    Se una delle coordinate è None restituisce 0.0 (comportamento storico
    dell'audit, che confronta tappe con coordinate mancanti).
    """
    if None in (lat1, lon1, lat2, lon2):
        return 0.0
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    valore = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(delta_lon / 2) ** 2
    )
    # Il limite evita errori di arrotondamento vicino ai punti antipodali.
    valore = min(1.0, max(0.0, valore))
    return 2 * raggio_km * math.asin(math.sqrt(valore))
