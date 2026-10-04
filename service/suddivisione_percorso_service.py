"""Calcolo della suddivisione di una geometria di percorso in tappe."""

import math

from service.geo_utils import calcola_distanza_haversine


ORE_BICI_AL_GIORNO = 6.0


def calcola_suddivisione_percorso(
    coordinate,
    *,
    distanza_totale_km,
    km_per_tappa=None,
    giorni_per_tappa=None,
    tempo_totale_ore=None,
):
    """Divide la geometria in tappe a distanza o durata giornaliera obiettivo.

    Per la modalità giorni, la durata di ogni tappa viene stimata con il tempo
    complessivo restituito dal routing e sei ore effettive di bici al giorno.
    """
    if (km_per_tappa is None) == (giorni_per_tappa is None):
        raise ValueError("Scegli km per tappa oppure giorni per tappa.")
    if len(coordinate) < 2:
        raise ValueError("La rotta deve contenere almeno due punti.")

    distanza_route = _numero_positivo(distanza_totale_km, "distanza del percorso")
    lunghezze_segmenti = [
        calcola_distanza_haversine(*punto_a[:2], *punto_b[:2])
        for punto_a, punto_b in zip(coordinate, coordinate[1:])
    ]
    distanza_geometria = sum(lunghezze_segmenti)
    if distanza_geometria <= 0:
        raise ValueError("La geometria del percorso non ha una lunghezza valida.")

    if km_per_tappa is not None:
        km_obiettivo = _numero_positivo(km_per_tappa, "km per tappa")
        numero_tappe = max(1, math.ceil(distanza_route / km_obiettivo))
        km_geometria_obiettivo = (
            km_obiettivo * distanza_geometria / distanza_route
        )
        distanze_divisione = [
            min(indice * km_geometria_obiettivo, distanza_geometria)
            for indice in range(1, numero_tappe)
        ]
        modalita = "km"
    else:
        giorni = _numero_positivo(giorni_per_tappa, "giorni per tappa")
        ore_totali = _numero_positivo(tempo_totale_ore, "tempo totale del percorso")
        numero_tappe = max(1, math.ceil(ore_totali / (ORE_BICI_AL_GIORNO * giorni)))
        distanze_divisione = [
            distanza_geometria * indice / numero_tappe
            for indice in range(1, numero_tappe)
        ]
        modalita = "giorni"

    tappe = _taglia_geometria(coordinate, lunghezze_segmenti, distanze_divisione)
    distanze_tappe = [round(_distanza_geometria(tappa), 2) for tappa in tappe]
    return {
        "tappe": tappe,
        "distanze_km": distanze_tappe,
        "punti_divisione": [tappa[-1] for tappa in tappe[:-1]],
        "distanza_totale_km": round(distanza_route, 1),
        "numero_tappe": len(tappe),
        "modalita": modalita,
    }


def _numero_positivo(valore, nome):
    """Converte e convalida un valore numerico strettamente positivo."""
    try:
        numero = float(valore)
    except (TypeError, ValueError) as errore:
        raise ValueError(f"Indica un valore valido per {nome}.") from errore
    if not math.isfinite(numero) or numero <= 0:
        raise ValueError(f"Indica un valore maggiore di zero per {nome}.")
    return numero


def _taglia_geometria(coordinate, lunghezze_segmenti, distanze_divisione):
    """Taglia una geometria ai chilometri indicati mantenendo i punti di giunzione."""
    tappe = []
    tappa_corrente = [tuple(coordinate[0])]
    prossima_divisione = 0
    distanza_cumulativa = 0.0

    for indice, lunghezza in enumerate(lunghezze_segmenti):
        punto_inizio = tuple(coordinate[indice])
        punto_fine = tuple(coordinate[indice + 1])
        distanza_fine_segmento = distanza_cumulativa + lunghezza

        while (
            prossima_divisione < len(distanze_divisione)
            and distanze_divisione[prossima_divisione] <= distanza_fine_segmento
        ):
            target = distanze_divisione[prossima_divisione]
            if lunghezza <= 0:
                punto_taglio = punto_fine
            else:
                frazione = min(
                    1.0,
                    max(0.0, (target - distanza_cumulativa) / lunghezza),
                )
                punto_taglio = _interpola_punto(punto_inizio, punto_fine, frazione)
            if punto_taglio != tappa_corrente[-1]:
                tappa_corrente.append(punto_taglio)
            tappe.append(tappa_corrente)
            tappa_corrente = [punto_taglio]
            prossima_divisione += 1

        if punto_fine != tappa_corrente[-1]:
            tappa_corrente.append(punto_fine)
        distanza_cumulativa = distanza_fine_segmento

    if len(tappa_corrente) >= 2:
        tappe.append(tappa_corrente)
    if not tappe:
        raise ValueError("Non è stato possibile suddividere la geometria del percorso.")
    return tappe


def _interpola_punto(punto_a, punto_b, frazione):
    """Interpola latitudine, longitudine e quota ai confini tra tappe."""
    latitudine = punto_a[0] + (punto_b[0] - punto_a[0]) * frazione
    longitudine = punto_a[1] + (punto_b[1] - punto_a[1]) * frazione
    if len(punto_a) > 2 and len(punto_b) > 2:
        elevazione = punto_a[2] + (punto_b[2] - punto_a[2]) * frazione
        return latitudine, longitudine, elevazione
    return latitudine, longitudine


def _distanza_geometria(coordinate):
    """Calcola la lunghezza di una porzione di geometria in chilometri."""
    return sum(
        calcola_distanza_haversine(*punto_a[:2], *punto_b[:2])
        for punto_a, punto_b in zip(coordinate, coordinate[1:])
    )
