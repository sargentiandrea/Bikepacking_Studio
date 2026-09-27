import sqlite3
from datetime import datetime, timedelta

from service.config import DB_NAME

def determina_mesi_ideali_automatici(lat_media, lon_media, altitudine_max=0):
    """
    Determina AUTOMATICAMENTE i mesi ideali per il ciclismo in base alla 
    posizione geografica e all'altitudine della tappa/blocco.
    
    Restituisce una stringa con i mesi raccomandati (es. '05,06,07,08,09').
    """
    if lat_media is None or lon_media is None:
        return "04,05,06,09,10" # Fallback Europa temperata

    # 1. ZONA TROPICALE ED EQUATORIALE (-23.5° < Lat < 23.5°)
    # Evita la stagione delle piogge intense / monsoni principali (solitamente Nov-Marz o Giu-Sett a seconda)
    if -23.5 <= lat_media <= 23.5:
        if lat_media >= 0:
            return "11,12,01,02,03" # Stagione secca emisfero nord tropicale
        else:
            return "05,06,07,08,09" # Stagione secca emisfero sud tropicale

    # 2. EMISFERO SUD TEMPERATO (Lat < -23.5°)
    # Le stagioni sono invertite: l'estate va da Dicembre a Febbraio
    elif lat_media < -23.5:
        if altitudine_max > 2000:
            return "12,01,02" # Alta montagna Emisfero Sud (solo piena estate)
        elif lat_media < -40.0: # Es. Patagonia
            return "11,12,01,02,03" # Estate e mezze stagioni
        else:
            return "09,10,11,03,04" # Primavera e Autunno australe

    # 3. EMISFERO NORD TEMPERATO E BOREALE (Lat > 23.5°)
    else:
        # Alta montagna / Passi Alpini (> 2000m)
        if altitudine_max > 2000:
            return "06,07,08,09" # Solo mesi estivi per evitare neve/passi chiusi
        # Nord Europa / Zone fredde (> 55° N, es. Scandinavia, Islanda)
        elif lat_media > 55.0:
            return "06,07,08" # Finestra estiva stretta
        # Europa del Sud / Mediterraneo / Nord Africa temperato (35° < Lat < 45°)
        elif 30.0 <= lat_media <= 40.0:
            return "03,04,05,10,11" # Evita il caldo estremo estivo (Luglio/Agosto)
        # Europa Centrale / Standard Temperato
        else:
            return "04,05,06,09,10" # Primavera e Autunno ideali

def assicura_tabelle_clima():
    """Garantisce l'esistenza delle tabelle e aggiorna le colonne mancanti se necessario."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Tabella impostazioni generali progetto
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progetto_stagione (
            id_progetto INTEGER PRIMARY KEY,
            data_partenza TEXT,
            modificatore_riposo INTEGER DEFAULT 0
        )
    """)

    # Tabella blocchi stagione
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blocchi_stagione (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_progetto INTEGER,
            nome_blocco TEXT,
            giorni_extra INTEGER DEFAULT 0,
            mesi_ideali_custom TEXT DEFAULT NULL,
            UNIQUE(id_progetto, nome_blocco)
        )
    """)

    # VERIFICA MIGRAZIONE: Se la colonna 'mesi_ideali_custom' non esiste (perché creata con il vecchio schema), la aggiungiamo al volo
    cursor.execute("PRAGMA table_info(blocchi_stagione)")
    colonne = [info[1] for info in cursor.fetchall()]

    if "mesi_ideali_custom" not in colonne:
        try:
            cursor.execute("ALTER TABLE blocchi_stagione ADD COLUMN mesi_ideali_custom TEXT DEFAULT NULL")
        except Exception as e:
            print(f"[MIGRAZIONE DB] Impossibile aggiungere colonna mesi_ideali_custom: {e}")

    conn.commit()
    conn.close()

def salva_impostazioni_stagione(id_progetto, data_partenza_str, modificatore_riposo, giorni_extra_dict=None, mesi_custom_dict=None):
    """Salva le impostazioni modificate dall'utente nell'interfaccia."""
    assicura_tabelle_clima()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO progetto_stagione (id_progetto, data_partenza, modificatore_riposo)
        VALUES (?, ?, ?)
        ON CONFLICT(id_progetto) DO UPDATE SET
            data_partenza = excluded.data_partenza,
            modificatore_riposo = excluded.modificatore_riposo
    """, (id_progetto, data_partenza_str, modificatore_riposo))

    if giorni_extra_dict:
        for b_nome, g_extra in giorni_extra_dict.items():
            m_custom = mesi_custom_dict.get(b_nome) if mesi_custom_dict else None
            cursor.execute("""
                INSERT INTO blocchi_stagione (id_progetto, nome_blocco, giorni_extra, mesi_ideali_custom)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id_progetto, nome_blocco) DO UPDATE SET
                    giorni_extra = excluded.giorni_extra,
                    mesi_ideali_custom = COALESCE(excluded.mesi_ideali_custom, blocchi_stagione.mesi_ideali_custom)
            """, (id_progetto, b_nome, g_extra, m_custom))

    conn.commit()
    conn.close()

def calcola_catena_stagionale(id_progetto, data_partenza_dt=None, modificatore_riposo=0, giorni_extra_dict=None):
    """
    Calcola la sequenza temporale con rilevamento DINAMICO dei mesi ideali
    basato sulle coordinate reali delle tappe del progetto.
    """
    assicura_tabelle_clima()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Recupera data di partenza e modificatore riposo salvati
    cursor.execute("SELECT data_partenza, modificatore_riposo FROM progetto_stagione WHERE id_progetto = ?", (id_progetto,))
    row_proj = cursor.fetchone()

    if data_partenza_dt is None:
        if row_proj and row_proj[0]:
            try:
                data_partenza_dt = datetime.strptime(row_proj[0], "%Y-%m-%d")
            except ValueError:
                data_partenza_dt = datetime.now()
        else:
            data_partenza_dt = datetime.now()

    if row_proj and modificatore_riposo == 0:
        modificatore_riposo = row_proj[1] or 0

    # 2. Recupera impostazioni custom salvate per blocco
    cursor.execute("SELECT nome_blocco, giorni_extra, mesi_ideali_custom FROM blocchi_stagione WHERE id_progetto = ?", (id_progetto,))
    blocchi_saved = {r[0]: {"extra": r[1], "custom_mesi": r[2]} for r in cursor.fetchall()}

    if giorni_extra_dict is None:
        giorni_extra_dict = {b: data["extra"] for b, data in blocchi_saved.items()}

    # 3. Verifica quali colonne esistono nella tabella 'tappe' per evitare OperationalError
    cursor.execute("PRAGMA table_info(tappe)")
    colonne_tappe = [info[1] for info in cursor.fetchall()]
    
    col_lat = "t.start_lat" if "start_lat" in colonne_tappe else "0"
    col_lon = "t.start_lon" if "start_lon" in colonne_tappe else "0"
    
    # Rilevamento dinamico colonna altitudine massima
    col_ele = "0"
    for possibile_col in ["ele_max", "quota_max", "ele_high", "ele"]:
        if possibile_col in colonne_tappe:
            col_ele = f"COALESCE(t.{possibile_col}, 0)"
            break

    query = f"""
        SELECT 
            COALESCE(t.blocco, 'Generico') as nome_blocco,
            COUNT(t.id) as num_tappe,
            COALESCE(SUM(t.distanza_km), 0.0) as km_totali,
            AVG({col_lat}) as lat_media,
            AVG({col_lon}) as lon_media,
            MAX({col_ele}) as ele_max
        FROM tappe t
        LEFT JOIN blocchi_ordine bo ON t.blocco = bo.nome_blocco AND t.id_progetto = bo.id_progetto
        WHERE t.id_progetto = ? AND (t.stato = 'ATTIVA' OR t.stato IS NULL)
        GROUP BY COALESCE(t.blocco, 'Generico')
        ORDER BY COALESCE(bo.ordine, 999)
    """

    cursor.execute(query, (id_progetto,))
    blocchi_db = cursor.fetchall()
    conn.close()

    if not blocchi_db:
        return []

    risultati = []
    data_corrente = data_partenza_dt

    for idx, (b_name, g_ped, km_tot, lat_med, lon_med, ele_max) in enumerate(blocchi_db):
        g_rip = max(0, (g_ped // 5) + modificatore_riposo)
        g_extra = int(giorni_extra_dict.get(b_name, blocchi_saved.get(b_name, {}).get("extra", 0)))
        g_tot = g_ped + g_rip + g_extra

        dt_in = data_corrente
        dt_out = dt_in + timedelta(days=max(0, g_tot - 1)) if g_tot > 0 else dt_in

        # Se l'utente ha inserito mesi ideali personalizzati usa quelli, altrimenti CALCOLA AUTOMATICAMENTE in base alle coordinate
        m_custom = blocchi_saved.get(b_name, {}).get("custom_mesi")
        if m_custom:
            m_ideali_str = m_custom
        else:
            m_ideali_str = determina_mesi_ideali_automatici(lat_med, lon_med, ele_max)

        mesi_ammessi = [int(m.strip()) for m in m_ideali_str.split(",") if m.strip().isdigit()]

        # Verifica se il periodo di transito copre i mesi ideali
        in_verde = (dt_in.month in mesi_ammessi) or (dt_out.month in mesi_ammessi)

        suggerimento = ""
        if in_verde:
            semaforo = "🟢 VERDE"
        else:
            semaforo = "🔴 ROSSO"
            delta_ottimale = None
            for offset in range(1, 366):
                if ((dt_in - timedelta(days=offset)).month in mesi_ammessi) or ((dt_out - timedelta(days=offset)).month in mesi_ammessi):
                    delta_ottimale = -offset
                    break
                if ((dt_in + timedelta(days=offset)).month in mesi_ammessi) or ((dt_out + timedelta(days=offset)).month in mesi_ammessi):
                    delta_ottimale = offset
                    break

            if delta_ottimale is not None:
                suggerimento = f" ({delta_ottimale:+d}gg per VERDE)"

        risultati.append({
            "ordine": idx + 1,
            "blocco": b_name,
            "tappe": g_ped,
            "km_totali": round(km_tot, 1),
            "giorni_pedalata": g_ped,
            "giorni_riposo": g_rip,
            "giorni_extra": g_extra,
            "giorni_totali": g_tot,
            "data_ingresso": dt_in.strftime("%d/%m/%Y"),
            "data_uscita": dt_out.strftime("%d/%m/%Y"),
            "mesi_ideali": m_ideali_str,
            "semaforo": f"{semaforo}{suggerimento}"
        })

        data_corrente = dt_out + timedelta(days=1)

    return risultati