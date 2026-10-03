# ============================================================
# audit_service.py
# ------------------------------------------------------------
# Servizio di audit del percorso bikepacking.
# Rileva interruzioni (gap) tra le tappe, gestisce trasferimenti
# (traghetti, treni, bus) e genera raccordi GPX automatici.
#
# Ultima revisione: 2026-09-29
# Analizzato e documentato da: GitHub Copilot
# ============================================================

import sqlite3
import math
import os
import requests
import gpxpy
import gpxpy.gpx

from service.config import BROUTER_URL, DB_NAME
from service.gpx_paths import percorso_gpx_progetto
from service.geo_utils import calcola_distanza_haversine


def rileva_gap_progetto(id_progetto):
    """
    Analizza la sequenza delle tappe e individua i GAP superiori a 3 km 
    che non sono già coperti da trasferimenti logistici registrati.
    """
    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    cursor = conn.cursor()
    
    # 1. Recupera le tappe attive ordinate
    cursor.execute("""
        SELECT t.id, t.sequenza, t.nome_file, t.start_lat, t.start_lon, t.end_lat, t.end_lon 
        FROM tappe t
        LEFT JOIN blocchi_ordine bo ON t.blocco = bo.nome_blocco AND t.id_progetto = bo.id_progetto
        WHERE t.id_progetto = ? AND t.stato = 'ATTIVA'
        ORDER BY COALESCE(bo.ordine, 999), t.sequenza ASC
    """, (id_progetto,))
    tappe = cursor.fetchall()
    
    # 2. Recupera i trasferimenti già inseriti (traghetti, treni, ecc.)
    cursor.execute("""
        SELECT start_lat, start_lon, end_lat, end_lon 
        FROM trasferimenti 
        WHERE id_progetto = ?
    """, (id_progetto,))
    trasferimenti = cursor.fetchall()
    
    conn.close()
    
    gap_rilevati = []
    
    for i in range(len(tappe) - 1):
        t_curr = tappe[i]
        t_next = tappe[i+1]
        
        end_lat, end_lon = t_curr[5], t_curr[6]
        start_lat, start_lon = t_next[3], t_next[4]
        
        if None in (end_lat, end_lon, start_lat, start_lon):
            continue
            
        gap_km = calcola_distanza_haversine(end_lat, end_lon, start_lat, start_lon)
        
        # Se c'è un'interruzione maggiore di 3 km
        if gap_km > 3.0:
            # Controlla se il buco è già coperto da un trasferimento
            coperto = any(
                abs(t[0] - end_lat) < 0.01 and abs(t[1] - end_lon) < 0.01 and
                abs(t[2] - start_lat) < 0.01 and abs(t[3] - start_lon) < 0.01
                for t in trasferimenti if t[0] and t[1] and t[2] and t[3]
            )
            
            if not coperto:
                tipo = 'GAP_TERRA' if gap_km <= 30.0 else 'GAP_AMPIO'
                msg = f"Interruzione di {round(gap_km, 1)} km tra '{t_curr[2]}' e '{t_next[2]}'."
                
                gap_rilevati.append({
                    "id_tappa_origine": t_curr[0],
                    "id_tappa_destinazione": t_next[0],
                    "tipo": tipo,
                    "messaggio": msg
                })
                
    return gap_rilevati

def rileva_strade_vietate_progetto(id_progetto):
    """
    Legge la cache locale delle superfici (calcolata offline confrontando i
    GPX con le mappe scaricate, vedi service/superfici_service.py) e segnala
    un allarme per ogni tratto del percorso che attraversa una strada
    probabilmente vietata alle biciclette (bicycle=no, access=no, autostrade...).

    Non calcola nulla al volo: se la cache per una tappa non è ancora stata
    generata (mai aperta nel pannello mappa), quella tappa viene semplicemente
    saltata, senza tentare alcuna chiamata esterna.
    """
    from service.superfici_service import carica_superfici_tappa

    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, sequenza, nome_file
        FROM tappe
        WHERE id_progetto = ? AND stato = 'ATTIVA'
        ORDER BY sequenza ASC
    """, (id_progetto,))
    tappe = cursor.fetchall()
    conn.close()

    allarmi_rilevati = []
    for tappa_id, sequenza, nome_file in tappe:
        dati_cache = carica_superfici_tappa(tappa_id)
        if not dati_cache or not dati_cache.get("disponibile"):
            continue

        tratti_vietati = dati_cache.get("tratti_vietati") or []
        if not tratti_vietati:
            continue

        primo_motivo = tratti_vietati[0].get("motivo", "tratto vietato")
        msg = (
            f"Nel file '{nome_file}' sono stati rilevati {len(tratti_vietati)} tratto/i "
            f"probabilmente vietati alle biciclette (es. {primo_motivo})."
        )
        allarmi_rilevati.append({
            "id_tappa_origine": tappa_id,
            "id_tappa_destinazione": tappa_id,
            "tipo": "STRADA_VIETATA_BICI",
            "messaggio": msg
        })

    return allarmi_rilevati

def registra_trasferimento_gap(id_progetto, id_origine, id_destinazione, tipo_trasporto, note=""):
    """Registra il trasferimento logistico per colmare il GAP."""
    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trasferimenti_logistici (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_progetto INTEGER,
            id_tappa_origine INTEGER,
            id_tappa_destinazione INTEGER,
            tipo_trasporto TEXT,
            note TEXT,
            data_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        INSERT INTO trasferimenti_logistici 
        (id_progetto, id_tappa_origine, id_tappa_destinazione, tipo_trasporto, note)
        VALUES (?, ?, ?, ?, ?)
    """, (id_progetto, id_origine, id_destinazione, tipo_trasporto, note))
    
    conn.commit()
    conn.close()
    return True

def genera_raccordo_gpx(id_progetto, t1_id, t2_id, t1_nome, t2_nome, db_name="bikepacking_app.db"):
    """
    Esegue il routing (BRouter o OSRM), crea il file GPX del raccordo,
    aggiorna la sequenza delle tappe, inserisce la nuova tappa e registra il trasferimento.
    """
    conn = sqlite3.connect(db_name, timeout=30.0)
    cursor = conn.cursor()
    
    cursor.execute("SELECT end_lat, end_lon, sequenza, blocco FROM tappe WHERE id = ?", (t1_id,))
    p1 = cursor.fetchone()
    cursor.execute("SELECT start_lat, start_lon FROM tappe WHERE id = ?", (t2_id,))
    p2 = cursor.fetchone()

    if not p1 or not p2:
        conn.close()
        return None, 0.0, False

    end_lat, end_lon, seq_t1, blocco_t1 = p1
    start_lat, start_lon = p2

    punti_strada = []

    # Prova il servizio BRouter locale
    try:
        resp = requests.get(
            BROUTER_URL,
            params={
                "lonlats": f"{end_lon},{end_lat}|{start_lon},{start_lat}",
                "profile": "trekking",
                "format": "geojson",
            },
            timeout=320,
        )
        if resp.status_code == 200:
            data = resp.json()
            if "features" in data and len(data["features"]) > 0:
                coords = data["features"][0]["geometry"]["coordinates"]
                punti_strada = [(c[1], c[0]) for c in coords]
    except Exception as e:
        print("Routing BRouter locale fallito:", e)

    is_linea_retta = False
    if not punti_strada:
        punti_strada = [(end_lat, end_lon), (start_lat, start_lon)]
        is_linea_retta = True

    dist_raccordo = sum(
        calcola_distanza_haversine(
            punti_strada[i][0], punti_strada[i][1],
            punti_strada[i+1][0], punti_strada[i+1][1]
        ) for i in range(len(punti_strada)-1)
    )
    
    nome_raccordo = f"Raccordo_{t1_nome[:8]}_{t2_nome[:8]}.gpx"

    # Generazione file GPX fisico
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    for lat, lon in punti_strada:
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(lat, lon))

    path_raccordo = percorso_gpx_progetto(id_progetto, nome_raccordo)
    os.makedirs(path_raccordo.parent, exist_ok=True)
    
    with open(path_raccordo, 'w', encoding='utf-8') as f:
        f.write(gpx.to_xml())

    # Aggiornamento database
    cursor.execute(
        "UPDATE tappe SET sequenza = sequenza + 1 WHERE id_progetto = ? AND sequenza > ?",
        (id_progetto, seq_t1)
    )

    cursor.execute('''
        INSERT INTO tappe (id_progetto, sequenza, blocco, nome_file, start_lat, start_lon, end_lat, end_lon, distanza_km, stato)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'ATTIVA')
    ''', (id_progetto, seq_t1 + 1, blocco_t1, nome_raccordo, end_lat, end_lon, start_lat, start_lon, round(dist_raccordo, 2)))

    tipo_mezzo_default = "Linea Retta / Raccordo" if is_linea_retta else "Bicicletta / Tratto Ciclabile"
    cursor.execute('''
        INSERT INTO trasferimenti (id_progetto, tipo_mezzo, vettore, da_luogo, a_luogo, durata, costo_eur, note, start_lat, start_lon, end_lat, end_lon)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        id_progetto, 
        tipo_mezzo_default, 
        "Autogenerato", 
        t1_nome, 
        t2_nome, 
        "N.D.", 
        0.0, 
        "Raccordo automatico da Mappa GAP", 
        end_lat, end_lon, start_lat, start_lon
    ))

    conn.commit()
    conn.close()

    return nome_raccordo, dist_raccordo, is_linea_retta