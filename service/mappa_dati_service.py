"""Dati per la mappa: letture da SQLite e dai file GPX, senza dipendenze da Qt.

Il modulo è usato dalla GUI (gui/mappa.py) ma non importa nulla di grafico,
quindi può essere provato con un database temporaneo e riusato da altre
interfacce (web, mobile).
"""

import hashlib
import math
import os
import sqlite3
from contextlib import closing

import gpxpy

from service.config import BASE_DIR
from service.geometria_service import (
    VERSIONE_ALGORITMO_GEOMETRIA,
    decomprimi_segmenti,
    geometria_geojson,
)
from service.gpx_paths import trova_percorso_gpx

# Stessa cartella GPX usata finora dalla GUI.
GPX_DIR = os.path.join(BASE_DIR, "gpx")


def firma_dati_mappa(id_progetto, db_name):
    """Crea una firma rapida (hash SHA-256) dei dati DB usati per disegnare il progetto.

    Legge tappe e trasferimenti del progetto. Restituisce l'hash in esadecimale,
    oppure None se il database     non è leggibile. Serve a capire se la cache
        in memoria della mappa è ancora valida.
    """
    try:
        with closing(sqlite3.connect(db_name)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, nome_file, sequenza, stato, blocco,
                       start_lat, start_lon, end_lat, end_lon
                FROM tappe
                WHERE id_progetto = ?
                ORDER BY sequenza ASC, id ASC
                """,
                (id_progetto,),
            )
            tappe = cursor.fetchall()
            cursor.execute(
                """
                SELECT tipo_mezzo, vettore, da_luogo, a_luogo,
                       start_lat, start_lon, end_lat, end_lon
                FROM trasferimenti
                WHERE id_progetto = ?
                ORDER BY id ASC
                """,
                (id_progetto,),
            )
            trasferimenti = cursor.fetchall()
        contenuto = repr((tappe, trasferimenti)).encode("utf-8")
        return hashlib.sha256(contenuto).hexdigest()
    except sqlite3.Error as errore:
        print(f"Impossibile verificare la cache della mappa: {errore}")
        return None


def carica_tappe_attive(id_progetto, db_name):
    """Legge le tappe ATTIVE con un file GPX, in ordine di sequenza.

    Restituisce una lista di tuple (id, nome_file, start_lat, start_lon,
    end_lat, end_lon, distanza_km). Gli errori del database (sqlite3.Error)
    sono lasciati al chiamante, che decide cosa mostrare.
    """
    with sqlite3.connect(db_name, timeout=15.0) as conn:
        return conn.execute(
            """
            SELECT id, nome_file, start_lat, start_lon, end_lat, end_lon, distanza_km
            FROM tappe
            WHERE id_progetto = ? AND stato = 'ATTIVA' AND nome_file IS NOT NULL
            ORDER BY sequenza ASC
            """,
            (id_progetto,),
        ).fetchall()


def carica_coordinate_tappa(tappa_id, id_progetto, db_name, directory_gpx=GPX_DIR):
    """Legge dal GPX della tappa l'elenco dei punti come tuple (latitudine, longitudine).

    Solleva ValueError se la tappa non esiste nel progetto o ha meno di due
    punti, FileNotFoundError se il GPX non si trova, sqlite3.Error o OSError
    per problemi di database e file.
    """
    with sqlite3.connect(db_name, timeout=15.0) as conn:
        riga = conn.execute(
            "SELECT nome_file FROM tappe WHERE id = ? AND id_progetto = ?",
            (tappa_id, id_progetto),
        ).fetchone()
    if not riga or not riga[0]:
        raise ValueError("La tappa selezionata non è più presente nel progetto attivo.")

    percorso_gpx = trova_percorso_gpx(
        riga[0], id_progetto, directory_gpx=directory_gpx
    )
    if percorso_gpx is None:
        raise FileNotFoundError(f"File GPX non trovato: {riga[0]}")
    with open(percorso_gpx, "r", encoding="utf-8", errors="ignore") as file_gpx:
        traccia = gpxpy.parse(file_gpx)
    coordinate = [
        (punto.latitude, punto.longitude)
        for track in traccia.tracks
        for segmento in track.segments
        for punto in segmento.points
    ]
    if len(coordinate) < 2:
        raise ValueError("La tappa non contiene abbastanza coordinate per essere ricalcolata.")
    return coordinate


def costruisci_geojson_progetto(id_progetto, db_name, directory_gpx=GPX_DIR):
    """Costruisce il GeoJSON del progetto (tappe, marker e trasferimenti) per MapLibre.

    Usa le geometrie precalcolate (tabella tappa_geometrie) quando sono valide
    e ripiega sul file GPX altrimenti. Restituisce un dizionario con "type",
    "features" e "bbox" (None se non ci sono punti). Gli errori del database
    vengono stampati e il payload parziale è restituito, come prima.
    """
    payload = {"type": "FeatureCollection", "features": [], "bbox": None}
    bbox_progetto = None

    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # 1. ESTRAZIONE TAPPE GPX REALI
        cursor.execute(
            """
            SELECT id, nome_file, sequenza, stato, blocco,
                   start_lat, start_lon, end_lat, end_lon
            FROM tappe
            WHERE id_progetto = ?
            ORDER BY sequenza ASC
            """,
            (id_progetto,),
        )
        tappe = cursor.fetchall()
        geometrie_precalcolate = {}
        try:
            cursor.execute(
                """
                SELECT geometria.tappa_id, geometria.geometria_semplificata,
                       geometria.bbox_min_lon, geometria.bbox_min_lat,
                       geometria.bbox_max_lon, geometria.bbox_max_lat
                FROM tappe
                JOIN tappa_geometrie AS geometria
                  ON geometria.tappa_id = tappe.id
                JOIN tappa_analisi AS analisi
                  ON analisi.tappa_id = geometria.tappa_id
                 AND analisi.gpx_sha256 = geometria.gpx_sha256
                WHERE tappe.id_progetto = ?
                  AND geometria.versione_algoritmo = ?
                """,
                (id_progetto, VERSIONE_ALGORITMO_GEOMETRIA),
            )
            geometrie_precalcolate = {
                riga[0]: (riga[1], riga[2], riga[3], riga[4], riga[5])
                for riga in cursor.fetchall()
            }
        except sqlite3.OperationalError as errore_geometria:
            print(
                "Geometrie precalcolate non disponibili; "
                f"uso il fallback GPX: {errore_geometria}"
            )

        cursor.execute(
            """
            SELECT lat_arrotondata, lon_arrotondata, nome
            FROM cache_nomi_luoghi
            WHERE nome IS NOT NULL AND nome != ''
            """
        )
        nomi_luoghi = {
            (round(lat, 5), round(lon, 5)): nome
            for lat, lon, nome in cursor.fetchall()
        }
        coordinate_nomi_luoghi = list(nomi_luoghi.items())

        def nome_luogo(lat, lon, lat_salvata, lon_salvata):
            for latitudine, longitudine in (
                (lat, lon),
                (lat_salvata, lon_salvata),
            ):
                if latitudine is None or longitudine is None:
                    continue
                nome = nomi_luoghi.get(
                    (round(float(latitudine), 5), round(float(longitudine), 5))
                )
                if nome:
                    return str(nome)
            latitudine = float(lat)
            longitudine = float(lon)
            fattore_longitudine = 111320 * max(
                0.01, abs(math.cos(math.radians(latitudine)))
            )
            distanza_minima = 250 ** 2
            nome_piu_vicino = None
            for (lat_cache, lon_cache), nome in coordinate_nomi_luoghi:
                distanza_quadrata = (
                    ((lat_cache - latitudine) * 111320) ** 2
                    + ((lon_cache - longitudine) * fattore_longitudine) ** 2
                )
                if distanza_quadrata < distanza_minima:
                    distanza_minima = distanza_quadrata
                    nome_piu_vicino = nome
            if nome_piu_vicino:
                return str(nome_piu_vicino)
            return f"{float(lat):.6f}, {float(lon):.6f}"

        for (
            tappa_id, nome_file_db, seq, stato, blocco,
            start_lat, start_lon, end_lat, end_lon,
        ) in tappe:
            if not nome_file_db: continue
            solo_nome = os.path.basename(nome_file_db)
            filepath = trova_percorso_gpx(
                solo_nome, id_progetto, directory_gpx=directory_gpx
            )
            segmenti_coordinate = None
            bbox_tappa = None

            geometria_salvata = geometrie_precalcolate.get(tappa_id)
            if geometria_salvata:
                try:
                    segmenti_coordinate = decomprimi_segmenti(
                        geometria_salvata[0]
                    )
                    bbox_tappa = list(geometria_salvata[1:])
                except (OSError, ValueError, TypeError) as errore:
                    print(
                        f"Geometria salvata non valida per la tappa "
                        f"{tappa_id}; uso il GPX: {errore}"
                    )

            if segmenti_coordinate is None and filepath is not None and os.path.exists(filepath):
                try:
                    with open(
                        filepath, 'r', encoding='utf-8', errors='ignore'
                    ) as gpx_file:
                        gpx = gpxpy.parse(gpx_file)
                        segmenti_coordinate = []
                        for track in gpx.tracks:
                            for segment in track.segments:
                                coords_segmento = [
                                    [point.longitude, point.latitude]
                                    for point in segment.points
                                ]
                                if coords_segmento:
                                    segmenti_coordinate.append(coords_segmento)
                except Exception as errore:
                    print(
                        f"Errore lettura GPX per la tappa {tappa_id} "
                        f"({solo_nome}): {errore}"
                    )

            punti_tappa = [
                punto
                for segmento in (segmenti_coordinate or [])
                for punto in segmento
            ]
            if punti_tappa:
                if bbox_tappa is None:
                    bbox_tappa = [
                        min(punto[0] for punto in punti_tappa),
                        min(punto[1] for punto in punti_tappa),
                        max(punto[0] for punto in punti_tappa),
                        max(punto[1] for punto in punti_tappa),
                    ]
                coordinate_partenza = punti_tappa[0]
                coordinate_arrivo = punti_tappa[-1]
                nome_partenza = nome_luogo(
                    coordinate_partenza[1],
                    coordinate_partenza[0],
                    start_lat,
                    start_lon,
                )
                nome_arrivo = nome_luogo(
                    coordinate_arrivo[1],
                    coordinate_arrivo[0],
                    end_lat,
                    end_lon,
                )
                if bbox_progetto is None:
                    bbox_progetto = bbox_tappa.copy()
                else:
                    bbox_progetto = [
                        min(bbox_progetto[0], bbox_tappa[0]),
                        min(bbox_progetto[1], bbox_tappa[1]),
                        max(bbox_progetto[2], bbox_tappa[2]),
                        max(bbox_progetto[3], bbox_tappa[3]),
                    ]
                payload["features"].append({
                    "type": "Feature",
                    "geometry": geometria_geojson(segmenti_coordinate),
                    "properties": {
                        "tipo": "tappa", "tappa_id": tappa_id, "sequenza": seq,
                        "blocco": str(blocco), "stato": str(stato),
                        "nome_file": solo_nome,
                        "nome_luogo_partenza": nome_partenza,
                        "nome_luogo_arrivo": nome_arrivo,
                    }
                })
                payload["features"].append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": coordinate_partenza,
                    },
                    "properties": {
                        "tipo": "marker_inizio",
                        "tappa_id": tappa_id,
                        "sequenza": seq,
                        "nome": f"Tappa {seq} - inizio",
                        "nome_luogo": nome_partenza,
                        "nome_file": solo_nome,
                    }
                })
                payload["features"].append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": coordinate_arrivo,
                    },
                    "properties": {
                        "tipo": "marker_fine",
                        "tappa_id": tappa_id,
                        "sequenza": seq,
                        "nome": f"Tappa {seq} - fine",
                        "nome_luogo": nome_arrivo,
                        "nome_file": solo_nome,
                    }
                })

        # 2. ESTRAZIONE TRASFERIMENTI MANCANTI (Aereo, Nave, Treno)
        cursor.execute("SELECT id, tipo_mezzo, vettore, da_luogo, a_luogo, start_lat, start_lon, end_lat, end_lon FROM trasferimenti WHERE id_progetto = ?", (id_progetto,))
        trasferimenti = cursor.fetchall()

        for t_id, mezzo, vettore, da, a, s_lat, s_lon, e_lat, e_lon in trasferimenti:
            if s_lat and s_lon and e_lat and e_lon:
                payload["features"].append({
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[s_lon, s_lat], [e_lon, e_lat]]
                    },
                    "properties": {
                        "tipo": "trasferimento", "mezzo": str(mezzo),
                        "vettore": str(vettore), "da": str(da), "a": str(a), "nome_file": f"Trasferimento: {mezzo}"
                    }
                })
                for longitudine, latitudine in ((s_lon, s_lat), (e_lon, e_lat)):
                    if bbox_progetto is None:
                        bbox_progetto = [
                            longitudine, latitudine, longitudine, latitudine
                        ]
                    else:
                        bbox_progetto[0] = min(bbox_progetto[0], longitudine)
                        bbox_progetto[1] = min(bbox_progetto[1], latitudine)
                        bbox_progetto[2] = max(bbox_progetto[2], longitudine)
                        bbox_progetto[3] = max(bbox_progetto[3], latitudine)

        payload["bbox"] = bbox_progetto
        conn.close()
    except Exception as err:
        print(f"Errore database nel worker: {err}")

    return payload
