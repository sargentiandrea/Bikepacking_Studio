import sqlite3

DB_NAME = "data/bikepacking_app.db"

def inizializza_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progetto_stagione (
            id_progetto INTEGER PRIMARY KEY,
            data_partenza TEXT,
            modificatore_riposo INTEGER DEFAULT 0
        )
    """)

    # Tabella per salvare i giorni extra/cuscinetto e i mesi ideali per ogni blocco
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blocchi_stagione (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_progetto INTEGER,
            nome_blocco TEXT,
            giorni_extra INTEGER DEFAULT 0,
            mesi_ideali TEXT DEFAULT '04,05,06,09,10',
            UNIQUE(id_progetto, nome_blocco)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progetti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descrizione TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tappe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_progetto INTEGER,
            sequenza INTEGER,
            blocco TEXT,
            nome_file TEXT,
            start_lat REAL,
            start_lon REAL,
            end_lat REAL,
            end_lon REAL,
            distanza_km REAL,
            stato TEXT DEFAULT 'ATTIVA',
            FOREIGN KEY (id_progetto) REFERENCES progetti(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS allarmi_percorso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_progetto INTEGER,
            tappa_origine_id INTEGER,
            tappa_destinazione_id INTEGER,
            tipo_allarme TEXT,
            messaggio TEXT,
            risolto INTEGER DEFAULT 0,
            FOREIGN KEY (id_progetto) REFERENCES progetti(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trasferimenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_progetto INTEGER,
            tipo_mezzo TEXT,
            vettore TEXT,
            da_luogo TEXT,
            a_luogo TEXT,
            durata TEXT,
            costo_eur REAL,
            note TEXT,
            start_lat REAL,
            start_lon REAL,
            end_lat REAL,
            end_lon REAL,
            FOREIGN KEY (id_progetto) REFERENCES progetti(id)
        )
    """)

    cursor.execute("""
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
            transitabile_bici INTEGER DEFAULT 1,
            stato_valico TEXT,
            valico_vicino_nome TEXT,
            valico_vicino_dist_km REAL,
            FOREIGN KEY(id_progetto) REFERENCES progetti(id)
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    inizializza_database()
    print("Database e tabella 'dogane_progetto' inizializzati con successo!")