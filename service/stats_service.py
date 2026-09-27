import sqlite3
import os
import urllib.request
import json
import math
import xml.etree.ElementTree as ET
from shapely.geometry import Point, LineString, shape
from shapely.strtree import STRtree

from service.config import DB_NAME

COASTLINE_FILE = "world_coastlines_10m.geojson"
# Mappa ad alta risoluzione 10m (molto più precisa per baie e promontori)
COASTLINE_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_coastline.geojson"

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


def _scarica_coste_alta_risoluzione():
    if not os.path.exists(COASTLINE_FILE):
        try:
            print("Download linea di costa ad ALTA RISOLUZIONE (Natural Earth 10m)...")
            urllib.request.urlretrieve(COASTLINE_URL, COASTLINE_FILE)
            print("Download completato.")
        except Exception as e:
            print(f"Errore download coste 10m: {e}")


def _inizializza_motore_costa():
    global _COASTLINE_TREE, _COASTLINE_GEOMS
    if _COASTLINE_TREE is not None:
        return

    _scarica_coste_alta_risoluzione()

    lines = []
    if os.path.exists(COASTLINE_FILE):
        try:
            with open(COASTLINE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for feature in data.get('features', []):
                    geom = shape(feature['geometry'])
                    if geom.geom_type == 'LineString':
                        lines.append(geom)
                    elif geom.geom_type == 'MultiLineString':
                        lines.extend(list(geom.geoms))
        except Exception as e:
            print(f"Errore caricamento GeoJSON coste: {e}")

    if not lines:
        lines = [LineString([(-180, 0), (180, 0)])]

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
    cursor.execute("SELECT distanza_km, nome_file FROM tappe WHERE id_progetto = ? AND stato = 'ATTIVA'", (id_progetto,))
    righe = cursor.fetchall()
    conn.close()

    if not righe:
        return {"km_totali": 0, "dislivello_pos": 0, "dislivello_neg": 0, "quota_max": 0, "pendenza_media": 0.0}

    km_tot = sum(r[0] or 0.0 for r in righe)
    dpos_tot, dneg_tot, qmax_val = 0, 0, 0
    pmed_list = []

    for _, nome_file in righe:
        dpos, dneg, qmax, pmed = _estrai_altimetria_da_gpx(nome_file)
        dpos_tot += dpos
        dneg_tot += dneg
        if qmax > qmax_val:
            qmax_val = qmax
        if pmed > 0:
            pmed_list.append(pmed)

    pmed_val = (sum(pmed_list) / len(pmed_list)) if pmed_list else 0.0

    return {
        "km_totali": round(km_tot, 1),
        "dislivello_pos": dpos_tot,
        "dislivello_neg": dneg_tot,
        "quota_max": qmax_val,
        "pendenza_media": round(pmed_val, 1)
    }


def ottieni_statistiche_per_blocco(id_progetto):
    if not id_progetto:
        return []

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = """
        SELECT blocco, distanza_km, nome_file 
        FROM tappe 
        WHERE id_progetto = ? AND stato = 'ATTIVA'
        ORDER BY sequenza ASC
    """
    cursor.execute(query, (id_progetto,))
    tappe = cursor.fetchall()
    conn.close()

    blocchi_map = {}
    for blocco_nome, km, nome_file in tappe:
        nome_b = blocco_nome if blocco_nome else "Generale"
        if nome_b not in blocchi_map:
            blocchi_map[nome_b] = []
        blocchi_map[nome_b].append((km or 0.0, nome_file))

    risultati = []
    for idx, (nome_b, t_lista) in enumerate(blocchi_map.items(), start=1):
        num_tappe = len(t_lista)
        km_tot = sum(t[0] for t in t_lista)
        
        dpos_b, dneg_b, qmax_b = 0, 0, 0
        pmed_b_list = []

        for _, nome_f in t_lista:
            dp, dn, qm, pm = _estrai_altimetria_da_gpx(nome_f)
            dpos_b += dp
            dneg_b += dn
            if qm > qmax_b:
                qmax_b = qm
            if pm > 0:
                pmed_b_list.append(pm)

        pmed_val = (sum(pmed_b_list) / len(pmed_b_list)) if pmed_b_list else 0.0

        risultati.append([
            idx,
            nome_b,
            num_tappe,
            f"{round(km_tot, 1)} km",
            f"{dpos_b} m",
            f"{dneg_b} m",
            f"{qmax_b} m",
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