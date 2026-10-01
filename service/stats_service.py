import sqlite3
import os
import json
import math
import xml.etree.ElementTree as ET
from shapely.geometry import Point, shape
from shapely.strtree import STRtree

from service.config import DB_NAME

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COASTLINE_FILE = os.path.join(PROJECT_ROOT, "world_coastlines_10m.geojson")

_COASTLINE_TREE = None
_COASTLINE_GEOMS = None


def _haversine_distance_m(lat1, lon1, lat2, lon2):
    """Calcola la distanza reale sulla superficie terrestre in metri tra due punti GPS."""
    R = 6371008.8  # Raggio medio terrestre in metri
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def _inizializza_motore_costa():
    global _COASTLINE_TREE, _COASTLINE_GEOMS
    if _COASTLINE_TREE is not None:
        return

    if not os.path.isfile(COASTLINE_FILE):
        raise FileNotFoundError(
            f"Dataset locale della linea costiera non trovato: {COASTLINE_FILE}"
        )

    lines = []
    try:
        with open(COASTLINE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for feature in data.get('features', []):
                geom = shape(feature['geometry'])
                if geom.geom_type == 'LineString':
                    lines.append(geom)
                elif geom.geom_type == 'MultiLineString':
                    lines.extend(list(geom.geoms))
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as errore:
        raise RuntimeError(
            f"Impossibile caricare il dataset locale della costa: {COASTLINE_FILE}"
        ) from errore
    if not lines:
        raise ValueError(
            f"Il dataset locale della costa non contiene linee valide: {COASTLINE_FILE}"
        )

    _COASTLINE_GEOMS = lines
    _COASTLINE_TREE = STRtree(lines)


def calcola_distanza_mare_m(lat, lon):
    """Calcola la distanza geodesica esatta in metri dal mare per una coordinata Lat/Lon."""
    if lat is None or lon is None or (lat == 0 and lon == 0):
        return 99999.0

    _inizializza_motore_costa()
    p_wgs84 = Point(lon, lat)

    # Trova la linea di costa geograficamente più vicina
    nearest_idx = _COASTLINE_TREE.nearest(p_wgs84)
    nearest_line = _COASTLINE_GEOMS[nearest_idx]

    # Trova il punto sulla linea di costa più vicino alla coordinata
    p_nearest_on_line = nearest_line.interpolate(nearest_line.project(p_wgs84))

    # Calcolo Haversine reale tra coordinata e punto di costa
    dist_metri = _haversine_distance_m(lat, lon, p_nearest_on_line.y, p_nearest_on_line.x)
    return round(dist_metri, 1)


def assegna_fascia_costiera_metri(dist_m):
    if dist_m <= 500.0:
        return "🏖️ Da 0 a 500 metri (0 - 0.5 km)"
    elif dist_m <= 2500.0:
        return "🌊 Da 501 a 2500 metri (0.51 - 2.5 km)"
    elif dist_m <= 5000.0:
        return "🏞️ Da 2501 a 5000 metri (2.51 - 5 km)"
    else:
        return "🏜️ Oltre 5000 metri (> 5 km)"


# -------------------------------------------------------------------
# PARSING GPX
# -------------------------------------------------------------------
def _trova_percorso_gpx(nome_file):
    if not nome_file:
        return None
    percorsi = [
        nome_file,
        os.path.join("gpx", nome_file),
        os.path.join("uploads", nome_file),
        os.path.join("tracks", nome_file)
    ]
    for p in percorsi:
        if os.path.exists(p):
            return p
    return None


def _estrai_punti_gpx(nome_file):
    filepath = _trova_percorso_gpx(nome_file)
    if not filepath:
        return []

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}

        punti = []
        for trkpt in root.findall('.//gpx:trkpt', ns):
            lat = float(trkpt.attrib['lat'])
            lon = float(trkpt.attrib['lon'])
            ele_elem = trkpt.find('gpx:ele', ns)
            ele = float(ele_elem.text) if (ele_elem is not None and ele_elem.text) else 0.0
            punti.append((lat, lon, ele))

        if not punti:
            for elem in root.iter():
                if elem.tag.endswith('trkpt'):
                    lat = float(elem.attrib['lat'])
                    lon = float(elem.attrib['lon'])
                    ele = 0.0
                    for child in elem:
                        if child.tag.endswith('ele') and child.text:
                            ele = float(child.text)
                    punti.append((lat, lon, ele))

        return punti
    except Exception:
        return []


def _estrai_altimetria_da_gpx(nome_file):
    punti = _estrai_punti_gpx(nome_file)
    if not punti:
        return 0, 0, 0, 0.0

    ele_list = [p[2] for p in punti if p[2] != 0.0]
    if not ele_list:
        return 0, 0, 0, 0.0

    dpos, dneg = 0.0, 0.0
    qmax = max(ele_list)

    for i in range(1, len(ele_list)):
        diff = ele_list[i] - ele_list[i - 1]
        if diff > 0:
            dpos += diff
        else:
            dneg += abs(diff)

    pmed = (dpos / (len(ele_list) * 50)) * 100 if len(ele_list) > 1 else 0.0
    return int(dpos), int(dneg), int(qmax), round(pmed, 1)


# -------------------------------------------------------------------
# ESTRAZIONE STATISTICHE E FASCE MARE
# -------------------------------------------------------------------
def ottieni_kpi_totali_progetto(id_progetto):
    if not id_progetto:
        return {"km_totali": 0, "dislivello_pos": 0, "dislivello_neg": 0, "quota_max": 0, "pendenza_media": 0.0}

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM tappe WHERE id_progetto = ? AND stato = 'ATTIVA'",
        (id_progetto,),
    )
    righe = cursor.fetchall()
    conn.close()

    if not righe:
        return {"km_totali": 0, "dislivello_pos": 0, "dislivello_neg": 0, "quota_max": 0, "pendenza_media": 0.0}

    analisi = _leggi_analisi_tappe([riga[0] for riga in righe])
    km_tot = 0.0
    dpos_tot = 0.0
    dneg_tot = 0.0
    qmax_val = None
    pendenza_pesata = 0.0
    distanza_pendenza = 0.0

    for tappa_id in [riga[0] for riga in righe]:
        dati = analisi.get(tappa_id)
        if not dati or dati["stato"] == "ERRORE":
            continue

        distanza = dati["distanza_km"]
        if distanza is not None:
            km_tot += distanza
        if dati["dislivello_pos_m"] is not None:
            dpos_tot += dati["dislivello_pos_m"]
        if dati["dislivello_neg_m"] is not None:
            dneg_tot += dati["dislivello_neg_m"]
        if dati["quota_max_m"] is not None:
            qmax_val = (
                dati["quota_max_m"]
                if qmax_val is None
                else max(qmax_val, dati["quota_max_m"])
            )
        if (
            distanza is not None
            and distanza > 0
            and dati["pendenza_media_pct"] is not None
        ):
            pendenza_pesata += dati["pendenza_media_pct"] * distanza
            distanza_pendenza += distanza

    pmed_val = (
        pendenza_pesata / distanza_pendenza if distanza_pendenza > 0 else 0.0
    )

    return {
        "km_totali": round(km_tot, 1),
        "dislivello_pos": round(dpos_tot),
        "dislivello_neg": round(dneg_tot),
        "quota_max": round(qmax_val) if qmax_val is not None else 0,
        "pendenza_media": round(pmed_val, 1)
    }


def ottieni_statistiche_per_blocco(id_progetto):
    if not id_progetto:
        return []

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = """
        SELECT id, blocco
        FROM tappe 
        WHERE id_progetto = ? AND stato = 'ATTIVA'
        ORDER BY sequenza ASC
    """
    cursor.execute(query, (id_progetto,))
    tappe = cursor.fetchall()
    conn.close()

    blocchi_map = {}
    for tappa_id, blocco_nome in tappe:
        nome_b = blocco_nome if blocco_nome else "Generale"
        if nome_b not in blocchi_map:
            blocchi_map[nome_b] = []
        blocchi_map[nome_b].append(tappa_id)

    analisi = _leggi_analisi_tappe([tappa[0] for tappa in tappe])
    risultati = []
    for idx, (nome_b, t_lista) in enumerate(blocchi_map.items(), start=1):
        num_tappe = len(t_lista)
        km_tot = 0.0
        dpos_b = 0.0
        dneg_b = 0.0
        qmax_b = None
        pendenza_pesata = 0.0
        distanza_pendenza = 0.0

        for tappa_id in t_lista:
            dati = analisi.get(tappa_id)
            if not dati or dati["stato"] == "ERRORE":
                continue

            distanza = dati["distanza_km"]
            if distanza is not None:
                km_tot += distanza
            if dati["dislivello_pos_m"] is not None:
                dpos_b += dati["dislivello_pos_m"]
            if dati["dislivello_neg_m"] is not None:
                dneg_b += dati["dislivello_neg_m"]
            if dati["quota_max_m"] is not None:
                qmax_b = (
                    dati["quota_max_m"]
                    if qmax_b is None
                    else max(qmax_b, dati["quota_max_m"])
                )
            if (
                distanza is not None
                and distanza > 0
                and dati["pendenza_media_pct"] is not None
            ):
                pendenza_pesata += dati["pendenza_media_pct"] * distanza
                distanza_pendenza += distanza

        pmed_val = (
            pendenza_pesata / distanza_pendenza
            if distanza_pendenza > 0
            else 0.0
        )

        risultati.append([
            idx,
            nome_b,
            num_tappe,
            f"{round(km_tot, 1)} km",
            f"{round(dpos_b)} m",
            f"{round(dneg_b)} m",
            f"{round(qmax_b) if qmax_b is not None else 0} m",
            f"{round(pmed_val, 1)} %"
        ])

    return risultati


def ottieni_ripartizione_fasce_mare(id_progetto):
    """Ripartizione chilometrica esatta basata su campionamento continuo e calcolo Haversine."""
    if not id_progetto:
        return []

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = """
        SELECT distanza_km, start_lat, start_lon, end_lat, end_lon, nome_file 
        FROM tappe 
        WHERE id_progetto = ? AND stato = 'ATTIVA'
    """
    cursor.execute(query, (id_progetto,))
    tappe = cursor.fetchall()
    conn.close()

    if not tappe:
        return []

    fasce_stat = {
        "🏖️ Da 0 a 500 metri (0 - 0.5 km)": {"km": 0.0, "tappe_coinvolte": set()},
        "🌊 Da 501 a 2500 metri (0.51 - 2.5 km)": {"km": 0.0, "tappe_coinvolte": set()},
        "🏞️ Da 2501 a 5000 metri (2.51 - 5 km)": {"km": 0.0, "tappe_coinvolte": set()},
        "🏜️ Oltre 5000 metri (> 5 km)": {"km": 0.0, "tappe_coinvolte": set()}
    }

    km_totali_viaggio = 0.0

    for idx, (km_tappa, s_lat, s_lon, e_lat, e_lon, nome_file) in enumerate(tappe):
        km_val = km_tappa or 0.0
        km_totali_viaggio += km_val

        punti = _estrai_punti_gpx(nome_file)

        if len(punti) >= 2:
            step = max(1, len(punti) // 40)
            punti_campione = punti[::step]
            if punti[-1] not in punti_campione:
                punti_campione.append(punti[-1])

            dist_conteggi = {}
            for pt in punti_campione:
                d_m = calcola_distanza_mare_m(pt[0], pt[1])
                fascia = assegna_fascia_costiera_metri(d_m)
                dist_conteggi[fascia] = dist_conteggi.get(fascia, 0) + 1

            tot_punti = len(punti_campione)
            for fascia, count in dist_conteggi.items():
                quota_km = (count / tot_punti) * km_val
                fasce_stat[fascia]["km"] += quota_km
                fasce_stat[fascia]["tappe_coinvolte"].add(idx)

        else:
            d1 = calcola_distanza_mare_m(s_lat, s_lon)
            d2 = calcola_distanza_mare_m(e_lat, e_lon)
            d_media = (d1 + d2) / 2.0
            fascia = assegna_fascia_costiera_metri(d_media)
            fasce_stat[fascia]["km"] += km_val
            fasce_stat[fascia]["tappe_coinvolte"].add(idx)

    tabella_finale = []
    for nome_fascia, dati in fasce_stat.items():
        percentuale = (dati["km"] / km_totali_viaggio * 100) if km_totali_viaggio > 0 else 0.0
        tabella_finale.append([
            nome_fascia,
            len(dati["tappe_coinvolte"]),
            f"{round(dati['km'], 1)} km",
            f"{round(percentuale, 1)} %"
        ])

    return tabella_finale


def analizza_dati_rotta_brouter(proprieta, coordinate):
    """Estrae KPI e categorie di superficie dai metadati GeoJSON di BRouter."""
    proprieta = proprieta or {}
    coordinate = coordinate or []

    try:
        distanza_totale_km = float(proprieta.get("track-length", 0)) / 1000.0
    except (TypeError, ValueError):
        distanza_totale_km = 0.0

    try:
        tempo_totale_secondi = float(proprieta.get("total-time", 0))
    except (TypeError, ValueError):
        tempo_totale_secondi = 0.0

    velocita_media_kmh = (
        distanza_totale_km / (tempo_totale_secondi / 3600.0)
        if distanza_totale_km > 0 and tempo_totale_secondi > 0
        else None
    )

    quote = []
    for punto in coordinate:
        if len(punto) > 2:
            try:
                quota = float(punto[2])
                if math.isfinite(quota):
                    quote.append(quota)
            except (TypeError, ValueError):
                continue

    categorie = {
        "Asfalto / pavimentato": {"km": 0.0, "colore": "#64748b"},
        "Pista ciclabile": {"km": 0.0, "colore": "#22c55e"},
        "Sentiero": {"km": 0.0, "colore": "#f59e0b"},
        "Sterrato": {"km": 0.0, "colore": "#a16207"},
        "Non specificata": {"km": 0.0, "colore": "#64748b"},
    }
    pavimentate = {"asphalt", "paved", "concrete", "concrete:lanes", "paving_stones", "sett", "cobblestone"}
    sterrate = {"gravel", "fine_gravel", "compacted", "ground", "dirt", "earth", "unpaved", "grass", "sand", "mud"}

    messaggi = proprieta.get("messages") or []
    if messaggi:
        intestazioni = [str(valore).strip().casefold() for valore in messaggi[0]]
        indice_distanza = intestazioni.index("distance") if "distance" in intestazioni else None
        indice_waytags = intestazioni.index("waytags") if "waytags" in intestazioni else None
        for riga in messaggi[1:]:
            try:
                distanza_m = float(riga[indice_distanza]) if indice_distanza is not None else 0.0
            except (IndexError, TypeError, ValueError):
                distanza_m = 0.0
            if distanza_m <= 0:
                continue

            waytags = str(riga[indice_waytags]) if indice_waytags is not None and len(riga) > indice_waytags else ""
            tags = {}
            for elemento in waytags.split():
                chiave, separatore, valore = elemento.partition("=")
                if separatore:
                    tags[chiave.casefold()] = valore.casefold()

            superficie = tags.get("surface", "")
            strada = tags.get("highway", "")
            if strada == "cycleway":
                categoria = "Pista ciclabile"
            elif superficie in pavimentate:
                categoria = "Asfalto / pavimentato"
            elif superficie in sterrate:
                categoria = "Sterrato"
            elif strada in {"path", "track", "bridleway", "footway"}:
                categoria = "Sentiero"
            else:
                categoria = "Non specificata"
            categorie[categoria]["km"] += distanza_m / 1000.0

    totale_superfici_km = sum(categoria["km"] for categoria in categorie.values())
    if totale_superfici_km <= 0 and distanza_totale_km > 0:
        categorie["Non specificata"]["km"] = distanza_totale_km
        totale_superfici_km = distanza_totale_km

    distribuzione = []
    for nome, dati in categorie.items():
        if dati["km"] <= 0:
            continue
        distribuzione.append({
            "categoria": nome,
            "km": round(dati["km"], 2),
            "percentuale": round(dati["km"] / totale_superfici_km * 100, 1),
            "colore": dati["colore"],
        })

    return {
        "distanza_km": round(distanza_totale_km, 2),
        "velocita_media_kmh": round(velocita_media_kmh, 1) if velocita_media_kmh is not None else None,
        "altitudine_min_m": round(min(quote)) if quote else None,
        "altitudine_max_m": round(max(quote)) if quote else None,
        "superfici": distribuzione,
    }


import sqlite3
import os
import json
from service.config import DB_NAME

def get_paesi_attraversati_stats(id_progetto):
    """Estrae i paesi basandosi rigorosamente sui codici ISO2 salvati nel database."""
    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    cursor = conn.cursor()
    
    paesi_visti = set()
    lista_finale = []
    
    try:
        cursor.execute("""
            SELECT codice_iso2, paese_nome 
            FROM dogane_progetto 
            WHERE id_progetto = ? 
            ORDER BY ordine_progressivo ASC
        """, (id_progetto,))
        
        for row in cursor.fetchall():
            iso2 = row[0]
            p_nome = row[1]
            
            if iso2 and len(iso2.strip()) == 2:
                iso2_clean = iso2.strip().upper()
                
                # Unicità basata sull'ISO2: niente più conflitti di nomi testuali
                if iso2_clean not in paesi_visti:
                    paesi_visti.add(iso2_clean)
                    
                    code = iso2_clean
                    flag = "".join(chr(127397 + ord(c)) for c in code)
                    display_nome = p_nome.strip() if p_nome else iso2_clean
                    
                    # Restituiamo la tupla strutturata: (iso2_clean, display_nome, stringa_display)
                    lista_finale.append((iso2_clean, display_nome, f"{flag} {display_nome}"))
                    
    except Exception as e:
        print(f"Errore lettura dogane per stats: {e}")
    
    conn.close()

    if not lista_finale:
        lista_finale = [("IT", "Italia", "🇮🇹 Italia")]

    totale = len(lista_finale)
    stringa_bandiere = f"{totale} Paesi registrati"
    
    return lista_finale, totale, stringa_bandiere


def _leggi_analisi_tappe(tappa_ids):
    """Legge le metriche persistite senza ricalcolare i GPX."""
    ids = list(dict.fromkeys(tappa_ids))
    if not ids:
        return {}

    segnaposto = ", ".join("?" for _ in ids)
    conn = sqlite3.connect(DB_NAME)
    try:
        righe = conn.execute(
            f"""
            SELECT tappa_id, stato, distanza_km, dislivello_pos_m,
                   dislivello_neg_m, quota_min_m, quota_max_m,
                   pendenza_media_pct, pendenza_max_pct,
                   bbox_min_lon, bbox_min_lat, bbox_max_lon, bbox_max_lat,
                   errore
            FROM tappa_analisi
            WHERE tappa_id IN ({segnaposto})
            """,
            ids,
        ).fetchall()
    finally:
        conn.close()

    campi = (
        "tappa_id",
        "stato",
        "distanza_km",
        "dislivello_pos_m",
        "dislivello_neg_m",
        "quota_min_m",
        "quota_max_m",
        "pendenza_media_pct",
        "pendenza_max_pct",
        "bbox_min_lon",
        "bbox_min_lat",
        "bbox_max_lon",
        "bbox_max_lat",
        "errore",
    )
    return {
        riga[0]: dict(zip(campi, riga))
        for riga in righe
    }


def ottieni_copertura_precalcolo_progetto(id_progetto):
    """Restituisce lo stato del precalcolo delle tappe attive del progetto."""
    if not id_progetto:
        return {
            "totale_tappe": 0,
            "tappe_complete": 0,
            "tappe_parziali": 0,
            "tappe_precalcolate": 0,
            "tappe_senza_precalcolo": 0,
            "tappe_con_errore": 0,
            "messaggio": "0 tappe su 0 precalcolate",
        }

    conn = sqlite3.connect(DB_NAME)
    try:
        righe = conn.execute(
            """
            SELECT ta.stato
            FROM tappe AS t
            LEFT JOIN tappa_analisi AS ta ON ta.tappa_id = t.id
            WHERE t.id_progetto = ? AND t.stato = 'ATTIVA'
            """,
            (id_progetto,),
        ).fetchall()
    finally:
        conn.close()

    totale = len(righe)
    complete = sum(riga[0] == "COMPLETO" for riga in righe)
    parziali = sum(riga[0] == "PARZIALE" for riga in righe)
    errori = sum(riga[0] == "ERRORE" for riga in righe)
    precalcolate = complete + parziali
    senza_precalcolo = totale - precalcolate - errori

    return {
        "totale_tappe": totale,
        "tappe_complete": complete,
        "tappe_parziali": parziali,
        "tappe_precalcolate": precalcolate,
        "tappe_senza_precalcolo": senza_precalcolo,
        "tappe_con_errore": errori,
        "messaggio": f"{precalcolate} tappe su {totale} precalcolate",
    }