import sqlite3
import reverse_geocoder as rg

from service.config import DB_NAME

def inizializza_tabelle_dogane():
    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dogane_progetto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_progetto INTEGER,
            ordine_progressivo INTEGER,
            codice_iso2 TEXT,
            paese_nome TEXT,
            regione_area TEXT,
            requisito_passaporto TEXT,
            tipo_visto TEXT,
            valuta TEXT,
            roaming_info TEXT,
            drone_policy TEXT,
            transitabile_bici INTEGER,
            stato_valico TEXT,
            valico_vicino_nome TEXT,
            valico_vicino_dist_km REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS anagrafica_paesi (
            codice_iso2 TEXT PRIMARY KEY,
            nome_paese TEXT,
            regione_area TEXT,
            passaporto TEXT,
            visto TEXT,
            valuta TEXT,
            roaming TEXT,
            drone TEXT,
            bici INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    
    popola_database_mondiale_completo()


import os
import json

def popola_database_mondiale_completo():
    """Legge direttamente il file paesi_mondo.json per popolare l'anagrafica con tutti i paesi del mondo."""
    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    cursor = conn.cursor()
    
    json_path = "paesi_mondo.json"
    if not os.path.exists(json_path):
        conn.close()
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            paesi_righe = data.get("paesi", [])
            
            tutti_i_paesi_del_mondo = []
            for row in paesi_righe:
                # Verifichiamo che la riga abbia abbastanza colonne nel JSON
                # Indipendentemente dal formato esatto, mappiamo i campi principali in sicurezza:
                if len(row) > 1 and row[1]:
                    iso2 = row[0].strip().upper() if row[0] else "XX"
                    nome = row[1].strip()
                    regione = row[2].strip() if len(row) > 2 and row[2] else "Internazionale"
                    passaporto = row[3].strip() if len(row) > 3 and row[3] else "Passaporto valido (6+ mesi)"
                    visto = row[4].strip() if len(row) > 4 and row[4] else "Verificare visto o eVisa"
                    valuta = row[5].strip() if len(row) > 5 and row[5] else "Valuta locale"
                    roaming = row[6].strip() if len(row) > 6 and row[6] else "EXTRA-UE"
                    drone = row[7].strip() if len(row) > 7 and row[7] else "Verificare normative locali"
                    bici = 1
                    
                    tutti_i_paesi_del_mondo.append((iso2, nome, regione, passaporto, visto, valuta, roaming, drone, bici))

            if tutti_i_paesi_del_mondo:
                cursor.executemany('''
                    INSERT OR REPLACE INTO anagrafica_paesi 
                    (codice_iso2, nome_paese, regione_area, passaporto, visto, valuta, roaming, drone, bici)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', tutti_i_paesi_del_mondo)
                
        conn.commit()
    except Exception as e:
        print(f"Errore caricamento paesi_mondo.json in anagrafica: {e}")
    finally:
        conn.close()

def recupera_dogane_salvate(id_progetto):
    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            ordine_progressivo,
            codice_iso2,
            paese_nome,
            regione_area,
            requisito_passaporto,
            tipo_visto,
            valuta,
            roaming_info,
            drone_policy
        FROM dogane_progetto
        WHERE id_progetto = ?
        ORDER BY ordine_progressivo ASC
    """, (id_progetto,))
    righe = cursor.fetchall()
    conn.close()

    risultati_puliti = []
    ultimo_iso = None
    for riga in righe:
        iso2 = riga[1]
        if iso2 != ultimo_iso:
            risultati_puliti.append(riga)
            ultimo_iso = iso2

    return risultati_puliti


def analizza_dogane_progetto(id_progetto):
    """Restituisce direttamente i dati già salvati ripuliti dai doppioni."""
    return recupera_dogane_salvate(id_progetto)