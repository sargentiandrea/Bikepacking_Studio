# ============================================================
# superfici_service.py
# ------------------------------------------------------------
# Calcola, in modo 100% OFFLINE, la ripartizione delle superfici
# (asfalto/sterrato/sentiero...) e gli eventuali tratti vietati
# alle biciclette di un percorso, confrontando i punti dei file
# GPX con le mappe vettoriali già scaricate in data/maps/.
#
# Nessuna chiamata di rete: i dati stradali (surface, bicycle,
# access, class) vengono letti direttamente dai file .mbtiles
# locali usati anche per disegnare la mappa (layer "transportation").
# Se per una zona non è stata scaricata la mappa, il tratto viene
# segnalato come "non coperto" invece di tentare una richiesta online.
#
# I risultati vengono salvati nella tabella 'superfici_tappa' così
# il calcolo (che legge file di grandi dimensioni) viene fatto una
# sola volta per tappa e riletto istantaneamente da mappa, statistiche
# e audit.
#
# Creato: 2026-09-29
# ============================================================

import os
import sqlite3
import gzip
import glob
import json
import math
import threading
from datetime import datetime, timezone

import gpxpy
import mapbox_vector_tile
from shapely.geometry import LineString, Point

from service.config import BASE_DIR, DB_NAME
from service.audit_service import calcola_distanza_haversine

MAPS_DIR = os.path.join(BASE_DIR, "data", "maps")
GPX_DIR = os.path.join(BASE_DIR, "gpx")

# Il layer "transportation" delle mappe locali (schema OpenMapTiles) è
# generato fino a questo livello di zoom: oltre non ci sono più dettagli.
ZOOM_ANALISI = 14

# Tolleranza di aggancio tra un punto della traccia GPX e la strada nota
# più vicina nelle mappe locali (in metri).
DISTANZA_MASSIMA_SNAP_M = 30.0

# Passo di campionamento della traccia GPX (in metri): non serve controllare
# ogni singolo punto del GPX, uno ogni 50 metri è già molto preciso.
PASSO_CAMPIONAMENTO_M = 50.0

CATEGORIE_COLORI = {
    "Asfalto / pavimentato": "#64748b",
    "Pista ciclabile": "#22c55e",
    "Sentiero": "#f59e0b",
    "Sterrato": "#a16207",
    "Non specificata": "#94a3b8",
}

_SUPERFICI_PAVIMENTATE = {"paved", "asphalt", "concrete", "concrete:lanes", "concrete:plates", "paving_stones", "sett", "cobblestone"}
_SUPERFICI_STERRATE = {"unpaved", "gravel", "fine_gravel", "compacted", "ground", "dirt", "earth", "grass", "sand", "mud"}

_cache_bounds_mbtiles = None
_cache_tile_strade = {}

# Connessioni .mbtiles tenute aperte per la durata del thread che le usa
# (worker mappa/superfici o worker nomi luogo): aprire e chiudere una
# connessione sqlite per ogni singolo tile, moltiplicato per centinaia o
# migliaia di tappe, era il principale collo di bottiglia nei percorsi
# molto lunghi. I file sono aperti in sola lettura (mode=ro): nessun
# rischio di corromperli, e ogni thread ha le proprie connessioni.
_connessioni_mbtiles_per_thread = threading.local()


def _connessione_mbtiles(mbtiles_path):
    """Restituisce una connessione .mbtiles aperta in sola lettura, riutilizzata
    per tutta la durata del thread corrente invece di aprirne una nuova ogni volta."""
    cache = getattr(_connessioni_mbtiles_per_thread, "connessioni", None)
    if cache is None:
        cache = {}
        _connessioni_mbtiles_per_thread.connessioni = cache

    conn = cache.get(mbtiles_path)
    if conn is None:
        uri = f"file:{mbtiles_path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True, check_same_thread=False)
        cache[mbtiles_path] = conn
    return conn


# -------------------------------------------------------------------
# LETTURA MAPPE LOCALI (.mbtiles)
# -------------------------------------------------------------------
def _carica_bounds_mbtiles():
    """Legge una sola volta i confini geografici di ogni mappa scaricata."""
    global _cache_bounds_mbtiles
    if _cache_bounds_mbtiles is not None:
        return _cache_bounds_mbtiles

    bounds = {}
    if os.path.isdir(MAPS_DIR):
        for percorso in glob.glob(os.path.join(MAPS_DIR, "*.mbtiles")):
            try:
                with sqlite3.connect(percorso) as conn:
                    riga = conn.execute(
                        "SELECT value FROM metadata WHERE name = 'bounds'"
                    ).fetchone()
                if riga and riga[0]:
                    minlon, minlat, maxlon, maxlat = (float(v) for v in riga[0].split(","))
                    bounds[percorso] = (minlon, minlat, maxlon, maxlat)
            except Exception as errore:
                print(f"Nota: impossibile leggere i confini di {percorso}: {errore}")

    _cache_bounds_mbtiles = bounds
    return bounds


def _mbtiles_candidati_per_punto(lat, lon):
    """
    Restituisce i file .mbtiles locali che coprono il punto, dal più piccolo
    (più specifico, es. una singola nazione) al più esteso (es. un intero
    continente). Alcuni estratti continentali dichiarano confini molto più
    ampi del loro contenuto reale (per includere isole lontane): provare
    prima il file più piccolo evita di "agganciarsi" per errore a un file
    sbagliato che in quella zona non contiene alcuna strada.
    """
    candidati = []
    for percorso, (minlon, minlat, maxlon, maxlat) in _carica_bounds_mbtiles().items():
        if minlon <= lon <= maxlon and minlat <= lat <= maxlat:
            area = (maxlon - minlon) * (maxlat - minlat)
            candidati.append((area, percorso))
    candidati.sort(key=lambda coppia: coppia[0])
    return [percorso for _, percorso in candidati]


def _deg2num(lat, lon, zoom):
    """Converte coordinate geografiche nell'indice del tile (x, y) alla zoom indicata."""
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    x = (lon + 180.0) / 360.0 * n
    y = (1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0 * n
    return int(x), int(y)


def _num2deg_frazionario(gx, gy, zoom):
    """Converte coordinate frazionarie di tile (x, y non interi) in lat/lon."""
    n = 2.0 ** zoom
    lon_deg = gx / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1.0 - 2.0 * gy / n)))
    return math.degrees(lat_rad), lon_deg


def _strade_del_tile(mbtiles_path, z, x, y):
    """Legge e decodifica (una sola volta, con cache) le strade contenute in un tile locale."""
    chiave = (mbtiles_path, z, x, y)
    if chiave in _cache_tile_strade:
        return _cache_tile_strade[chiave]

    strade = []
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
            layer = tile.get("transportation")
            if layer:
                extent = layer.get("extent", 4096)
                for feature in layer.get("features", []):
                    geometria = feature.get("geometry", {})
                    tag = feature.get("properties", {})
                    tipo = geometria.get("type")
                    if tipo == "LineString":
                        linee = [geometria.get("coordinates", [])]
                    elif tipo == "MultiLineString":
                        linee = geometria.get("coordinates", [])
                    else:
                        continue

                    for linea in linee:
                        punti_geo = []
                        for px, py in linea:
                            lat_p, lon_p = _num2deg_frazionario(x + px / extent, y + py / extent, z)
                            punti_geo.append((lon_p, lat_p))
                        if len(punti_geo) >= 2:
                            strade.append((LineString(punti_geo), tag))
    except Exception as errore:
        print(f"Nota: impossibile leggere il tile locale {z}/{x}/{y} da {os.path.basename(mbtiles_path)}: {errore}")

    _cache_tile_strade[chiave] = strade
    return strade


def _classifica_tag_strada(tag):
    """Determina la categoria di superficie e un eventuale divieto per le biciclette dai tag OSM di una strada."""
    superficie = str(tag.get("surface", "")).casefold()
    classe = str(tag.get("class", "")).casefold()
    sottoclasse = str(tag.get("subclass", "")).casefold()
    bicycle = str(tag.get("bicycle", "")).casefold()
    access = str(tag.get("access", "")).casefold()

    if sottoclasse == "cycleway":
        categoria = "Pista ciclabile"
    elif superficie in _SUPERFICI_PAVIMENTATE:
        categoria = "Asfalto / pavimentato"
    elif superficie in _SUPERFICI_STERRATE:
        categoria = "Sterrato"
    elif classe == "path":
        categoria = "Sentiero"
    else:
        categoria = "Non specificata"

    vietato = False
    motivo = None
    if bicycle in {"no", "dismount", "private"}:
        vietato = True
        motivo = f"bicycle={bicycle}"
    elif access in {"no", "private"} and bicycle not in {"yes", "designated", "permissive"}:
        vietato = True
        motivo = f"access={access}"
    elif classe in {"motorway", "trunk"}:
        vietato = True
        motivo = f"strada di classe '{classe}', normalmente vietata alle biciclette"

    return categoria, vietato, motivo


# -------------------------------------------------------------------
# LETTURA GPX E CAMPIONAMENTO
# -------------------------------------------------------------------
def _trova_percorso_gpx(nome_file):
    if not nome_file:
        return None
    candidati = [nome_file, os.path.join(GPX_DIR, os.path.basename(nome_file))]
    for candidato in candidati:
        if os.path.exists(candidato):
            return candidato
    return None


def _leggi_punti_gpx(nome_file):
    filepath = _trova_percorso_gpx(nome_file)
    if not filepath:
        return []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as file_gpx:
            traccia = gpxpy.parse(file_gpx)
        return [
            (punto.latitude, punto.longitude)
            for track in traccia.tracks
            for segmento in track.segments
            for punto in segmento.points
        ]
    except Exception as errore:
        print(f"Nota: impossibile leggere il file GPX {nome_file}: {errore}")
        return []


def _campiona_punti(punti, passo_metri=PASSO_CAMPIONAMENTO_M):
    """Riduce il numero di punti da analizzare, mantenendone uno circa ogni 'passo_metri'."""
    if len(punti) <= 2:
        return list(punti)

    campione = [punti[0]]
    distanza_accumulata = 0.0
    for i in range(1, len(punti)):
        lat_prec, lon_prec = punti[i - 1]
        lat_cur, lon_cur = punti[i]
        distanza_accumulata += calcola_distanza_haversine(lat_prec, lon_prec, lat_cur, lon_cur) * 1000.0
        if distanza_accumulata >= passo_metri:
            campione.append(punti[i])
            distanza_accumulata = 0.0
    if campione[-1] != punti[-1]:
        campione.append(punti[-1])
    return campione


# -------------------------------------------------------------------
# ANALISI PRINCIPALE
# -------------------------------------------------------------------
def analizza_superfici_gpx(nome_file):
    """
    Analizza un singolo file GPX confrontandolo con le mappe locali già
    scaricate. Restituisce un dizionario con la ripartizione delle
    superfici (compatibile con il pannello mappa/statistiche) e l'elenco
    degli eventuali tratti probabilmente vietati alle biciclette.

    Non effettua MAI chiamate di rete: se una zona non è coperta dalle
    mappe scaricate, quel tratto viene semplicemente segnalato come
    "non coperto".
    """
    punti = _leggi_punti_gpx(nome_file)
    if len(punti) < 2:
        return {
            "disponibile": False,
            "motivo": "File GPX non trovato o senza punti traccia.",
        }

    campione = _campiona_punti(punti)

    categorie_km = {}
    tratti_vietati = []
    km_non_coperti = 0.0
    km_totali = 0.0
    punto_precedente = None

    for lat, lon in campione:
        if punto_precedente is not None:
            tratto_km = calcola_distanza_haversine(punto_precedente[0], punto_precedente[1], lat, lon)
        else:
            tratto_km = 0.0
        punto_precedente = (lat, lon)
        km_totali += tratto_km

        mbtiles_candidati = _mbtiles_candidati_per_punto(lat, lon)
        if not mbtiles_candidati:
            km_non_coperti += tratto_km
            continue

        x, y = _deg2num(lat, lon, ZOOM_ANALISI)
        strade_vicine = []
        for candidato in mbtiles_candidati:
            strade_candidato = _strade_del_tile(candidato, ZOOM_ANALISI, x, y)
            if strade_candidato:
                strade_vicine = strade_candidato
                break

        punto_geom = Point(lon, lat)
        migliore_tag = None
        migliore_dist_m = DISTANZA_MASSIMA_SNAP_M
        for linea, tag in strade_vicine:
            dist_m = linea.distance(punto_geom) * 111320.0  # approssimazione: 1° ≈ 111.32 km
            if dist_m < migliore_dist_m:
                migliore_dist_m = dist_m
                migliore_tag = tag

        if migliore_tag is None:
            categorie_km["Non specificata"] = categorie_km.get("Non specificata", 0.0) + tratto_km
            continue

        categoria, vietato, motivo = _classifica_tag_strada(migliore_tag)
        categorie_km[categoria] = categorie_km.get(categoria, 0.0) + tratto_km
        if vietato:
            # Raggruppa punti consecutivi con lo stesso motivo (es. lo stesso
            # attraversamento di un'autostrada) in un solo tratto segnalato,
            # invece di contare ogni singolo campione separatamente.
            if tratti_vietati and tratti_vietati[-1]["motivo"] == motivo:
                tratti_vietati[-1]["lat_fine"] = lat
                tratti_vietati[-1]["lon_fine"] = lon
            else:
                tratti_vietati.append({"lat": lat, "lon": lon, "lat_fine": lat, "lon_fine": lon, "motivo": motivo})

    superfici = []
    if km_totali > 0:
        for nome_categoria, km in categorie_km.items():
            if km <= 0:
                continue
            superfici.append({
                "categoria": nome_categoria,
                "km": round(km, 2),
                "percentuale": round((km / km_totali) * 100.0, 1),
                "colore": CATEGORIE_COLORI.get(nome_categoria, "#94a3b8"),
            })

    copertura_percentuale = round(((km_totali - km_non_coperti) / km_totali) * 100.0, 1) if km_totali > 0 else 0.0

    return {
        "disponibile": True,
        "superfici": superfici,
        "tratti_vietati": tratti_vietati,
        "copertura_percentuale": copertura_percentuale,
        "km_non_coperti": round(km_non_coperti, 2),
    }


# -------------------------------------------------------------------
# CACHE SU DATABASE (calcolo una sola volta per tappa)
# -------------------------------------------------------------------
def carica_superfici_tappa(tappa_id):
    """Rilegge dalla cache locale il risultato già calcolato per una tappa, se esiste."""
    try:
        with sqlite3.connect(DB_NAME, timeout=15.0) as conn:
            riga = conn.execute(
                "SELECT dati_json FROM superfici_tappa WHERE tappa_id = ?", (tappa_id,)
            ).fetchone()
    except sqlite3.Error as errore:
        print(f"Nota: impossibile leggere la cache superfici della tappa {tappa_id}: {errore}")
        return None
    if not riga or not riga[0]:
        return None
    try:
        return json.loads(riga[0])
    except (TypeError, ValueError):
        return None


def salva_superfici_tappa(tappa_id, dati):
    """Salva (o aggiorna) il risultato dell'analisi offline di una tappa nella cache locale."""
    try:
        with sqlite3.connect(DB_NAME, timeout=15.0) as conn:
            conn.execute(
                """
                INSERT INTO superfici_tappa (tappa_id, dati_json, calcolato_il)
                VALUES (?, ?, ?)
                ON CONFLICT(tappa_id) DO UPDATE SET dati_json = excluded.dati_json, calcolato_il = excluded.calcolato_il
                """,
                (tappa_id, json.dumps(dati), datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()
    except sqlite3.Error as errore:
        print(f"Nota: impossibile salvare la cache superfici della tappa {tappa_id}: {errore}")


def analizza_o_carica_superficie_tappa(tappa_id, nome_file, forza_ricalcolo=False):
    """Restituisce l'analisi offline di una tappa: dalla cache se già calcolata, altrimenti la calcola e la salva."""
    if not forza_ricalcolo:
        dati_cache = carica_superfici_tappa(tappa_id)
        if dati_cache is not None:
            return dati_cache

    dati = analizza_superfici_gpx(nome_file)
    salva_superfici_tappa(tappa_id, dati)
    return dati


def analizza_superfici_progetto(id_progetto, forza_ricalcolo=False, deve_continuare=None):
    """
    Calcola (o rilegge dalla cache) la ripartizione superfici per tutte le
    tappe attive di un progetto e restituisce un risultato aggregato,
    compatibile con il pannello mappa (chiavi 'superfici', 'tratti_vietati').

    'deve_continuare', se fornito, è una funzione senza argomenti che
    restituisce False quando il calcolo va interrotto subito (es. l'utente
    ha già cambiato percorso e questo risultato non servirebbe più):
    evita di continuare a "macinare" tappe inutilmente in sottofondo.
    """
    try:
        with sqlite3.connect(DB_NAME, timeout=15.0) as conn:
            tappe = conn.execute(
                """
                SELECT id, nome_file FROM tappe
                WHERE id_progetto = ? AND stato = 'ATTIVA' AND nome_file IS NOT NULL
                ORDER BY sequenza ASC
                """,
                (id_progetto,),
            ).fetchall()
    except sqlite3.Error as errore:
        print(f"Nota: impossibile leggere le tappe del progetto {id_progetto}: {errore}")
        return {"disponibile": False, "motivo": "Errore di lettura del database."}

    if not tappe:
        return {"disponibile": False, "motivo": "Nessuna tappa con file GPX in questo progetto."}

    categorie_km = {}
    tratti_vietati = []
    km_totali = 0.0
    km_non_coperti = 0.0

    for tappa_id, nome_file in tappe:
        if deve_continuare is not None and not deve_continuare():
            return {"disponibile": False, "motivo": "Calcolo interrotto: percorso cambiato.", "annullato": True}
        dati_tappa = analizza_o_carica_superficie_tappa(tappa_id, nome_file, forza_ricalcolo=forza_ricalcolo)
        if not dati_tappa.get("disponibile"):
            continue
        for voce in dati_tappa.get("superfici", []):
            categorie_km[voce["categoria"]] = categorie_km.get(voce["categoria"], 0.0) + voce["km"]
            km_totali += voce["km"]
        km_non_coperti += dati_tappa.get("km_non_coperti", 0.0)
        for tratto in dati_tappa.get("tratti_vietati", []):
            tratti_vietati.append({**tratto, "tappa_id": tappa_id, "nome_file": nome_file})

    km_totali += km_non_coperti  # i km non coperti fanno comunque parte della distanza totale

    superfici = []
    if km_totali > 0:
        for nome_categoria, km in categorie_km.items():
            if km <= 0:
                continue
            superfici.append({
                "categoria": nome_categoria,
                "km": round(km, 2),
                "percentuale": round((km / km_totali) * 100.0, 1),
                "colore": CATEGORIE_COLORI.get(nome_categoria, "#94a3b8"),
            })

    return {
        "disponibile": True,
        "superfici": superfici,
        "tratti_vietati": tratti_vietati,
        "copertura_percentuale": round(((km_totali - km_non_coperti) / km_totali) * 100.0, 1) if km_totali > 0 else 0.0,
    }
