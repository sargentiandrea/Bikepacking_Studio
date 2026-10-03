# ============================================================
# geocodifica_offline_service.py
# ------------------------------------------------------------
# Trova il nome del luogo più vicino a una coppia di coordinate
# usando SOLO le mappe vettoriali locali già scaricate in
# data/maps/ (stesso principio di superfici_service.py: nessuna
# chiamata di rete). Legge il layer "place" (schema OpenMapTiles),
# che contiene città, paesi, frazioni e località con il loro nome.
#
# Se non viene trovato nessun luogo abbastanza vicino (mappa non
# scaricata per quella zona, oppure zona davvero isolata), la
# funzione restituisce None: chi chiama deve prevedere un
# alternativa (es. mostrare comunque le coordinate).
#
# Creato: 2026-09-29
# ============================================================

import os
import sqlite3
import gzip
import threading
from datetime import datetime, timezone

import mapbox_vector_tile

from service.config import DB_NAME
from service.geo_utils import calcola_distanza_haversine
# Riusiamo le funzioni geografiche di base già scritte per le superfici,
# per non duplicare la logica di lettura dei tile .mbtiles.
from service.superfici_service import (
    _mbtiles_candidati_per_punto,
    _deg2num,
    _num2deg_frazionario,
    _connessione_mbtiles,
)

# Precisione della cache permanente dei nomi luogo (arrotondamento delle
# coordinate): 5 decimali equivalgono a circa 1 metro, più che sufficiente
# per riconoscere lo stesso punto GPS riletto da un file GPX già analizzato.
_DECIMALI_CACHE_NOMI = 5

# Il layer "place" (OpenMapTiles) è già completo a questo livello di zoom:
# oltre non compaiono nuove località, solo maggiore dettaglio stradale.
ZOOM_RICERCA = 12

# Quanti tile adiacenti controllare oltre a quello del punto: una località
# nota potrebbe cadere nel tile confinante anche se molto vicina.
RAGGIO_TILE_ADIACENTI = 1

# Penalità (in km "equivalenti") applicata alle località meno importanti,
# così a parità di vicinanza si preferisce il nome di un paese vero e
# proprio a quello di una singola casa isolata.
_PESO_IMPORTANZA_CLASSE = {
    "city": 0.0, "town": 0.5, "village": 1.0, "hamlet": 1.5,
    "suburb": 1.5, "neighbourhood": 2.0, "isolated_dwelling": 3.0, "locality": 3.0,
}

_cache_tile_luoghi = {}


def _luoghi_del_tile(mbtiles_path, z, x, y):
    """Legge e decodifica (con cache) le località contenute in un tile locale."""
    chiave = (mbtiles_path, z, x, y)
    if chiave in _cache_tile_luoghi:
        return _cache_tile_luoghi[chiave]

    luoghi = []
    tms_row = (2 ** z - 1) - y  # i file .mbtiles usano lo schema TMS (riga 0 in basso)
    try:
        conn = _connessione_mbtiles(mbtiles_path)
        riga = conn.execute(
            "SELECT tile_data FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?",
            (z, x, tms_row),
        ).fetchone()

        if riga and riga[0]:
            dati_grezzi = riga[0]
            try:
                dati_grezzi = gzip.decompress(dati_grezzi)
            except OSError:
                pass  # tile non compresso

            tile = mapbox_vector_tile.decode(dati_grezzi)
            layer = tile.get("place")
            if layer:
                extent = layer.get("extent", 4096)
                for feature in layer.get("features", []):
                    geometria = feature.get("geometry", {})
                    tag = feature.get("properties", {})
                    if geometria.get("type") != "Point":
                        continue
                    nome = tag.get("name:it") or tag.get("name") or tag.get("name_it") or tag.get("name_en")
                    if not nome:
                        continue
                    px, py = geometria.get("coordinates", [None, None])
                    if px is None:
                        continue
                    lat_p, lon_p = _num2deg_frazionario(x + px / extent, y + py / extent, z)
                    luoghi.append((lat_p, lon_p, str(nome), str(tag.get("class", ""))))
    except Exception as errore:
        print(f"Nota: impossibile leggere le localita del tile locale {z}/{x}/{y} da {os.path.basename(mbtiles_path)}: {errore}")

    _cache_tile_luoghi[chiave] = luoghi
    return luoghi


def _chiave_cache(lat, lon):
    """Arrotonda le coordinate per usarle come chiave della cache permanente."""
    return round(lat, _DECIMALI_CACHE_NOMI), round(lon, _DECIMALI_CACHE_NOMI)


def _leggi_nome_da_cache(lat, lon):
    """Cerca il nome già risolto in precedenza per questo punto. Restituisce
    (trovato: bool, nome: str|None): 'trovato' distingue 'mai cercato prima'
    da 'cercato ma nessun luogo abbastanza vicino' (nome vuoto salvato)."""
    lat_r, lon_r = _chiave_cache(lat, lon)
    try:
        with sqlite3.connect(DB_NAME, timeout=15.0) as conn:
            riga = conn.execute(
                "SELECT nome FROM cache_nomi_luoghi WHERE lat_arrotondata = ? AND lon_arrotondata = ?",
                (lat_r, lon_r),
            ).fetchone()
    except sqlite3.Error as errore:
        print(f"Nota: impossibile leggere la cache nomi luogo: {errore}")
        return False, None

    if riga is None:
        return False, None
    return True, (riga[0] or None)


def _scrivi_nome_in_cache(lat, lon, nome):
    """Salva il nome risolto (o l'assenza di risultato) nella cache permanente,
    così le prossime aperture dello stesso percorso non rifanno la ricerca."""
    lat_r, lon_r = _chiave_cache(lat, lon)
    try:
        with sqlite3.connect(DB_NAME, timeout=15.0) as conn:
            conn.execute(
                """
                INSERT INTO cache_nomi_luoghi (lat_arrotondata, lon_arrotondata, nome, calcolato_il)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(lat_arrotondata, lon_arrotondata) DO UPDATE SET
                    nome = excluded.nome, calcolato_il = excluded.calcolato_il
                """,
                (lat_r, lon_r, nome or "", datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()
    except sqlite3.Error as errore:
        print(f"Nota: impossibile salvare la cache nomi luogo: {errore}")


def nome_luogo_da_coordinate(lat, lon):
    """
    Cerca, tra le mappe locali già scaricate, il nome della località più
    vicina alle coordinate indicate. Restituisce None se non trova nulla
    (mappa non scaricata per quella zona, oppure punto davvero isolato):
    in quel caso chi chiama deve mostrare comunque le coordinate grezze.

    Il risultato viene tenuto in una cache permanente su database: la stessa
    coppia di coordinate (es. la partenza di una tappa già vista) non viene
    più ricalcolata riaprendo lo stesso percorso.
    """
    if lat is None or lon is None:
        return None

    trovato_in_cache, nome_cache = _leggi_nome_da_cache(lat, lon)
    if trovato_in_cache:
        return nome_cache

    candidati_mbtiles = _mbtiles_candidati_per_punto(lat, lon)
    if not candidati_mbtiles:
        _scrivi_nome_in_cache(lat, lon, None)
        return None

    x_centro, y_centro = _deg2num(lat, lon, ZOOM_RICERCA)

    migliore_nome = None
    migliore_punteggio = None
    for mbtiles_path in candidati_mbtiles:
        trovato_in_questo_file = False
        for dx in range(-RAGGIO_TILE_ADIACENTI, RAGGIO_TILE_ADIACENTI + 1):
            for dy in range(-RAGGIO_TILE_ADIACENTI, RAGGIO_TILE_ADIACENTI + 1):
                for lat_p, lon_p, nome, classe in _luoghi_del_tile(mbtiles_path, ZOOM_RICERCA, x_centro + dx, y_centro + dy):
                    distanza_km = calcola_distanza_haversine(lat, lon, lat_p, lon_p)
                    punteggio = distanza_km + _PESO_IMPORTANZA_CLASSE.get(classe, 2.0)
                    if migliore_punteggio is None or punteggio < migliore_punteggio:
                        migliore_punteggio = punteggio
                        migliore_nome = nome
                        trovato_in_questo_file = True
        if trovato_in_questo_file:
            break  # il file .mbtiles più specifico ha già dato un risultato valido

    _scrivi_nome_in_cache(lat, lon, migliore_nome)
    return migliore_nome
