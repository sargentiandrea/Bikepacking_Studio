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
            nome_progetto TEXT NOT NULL,
            descrizione TEXT,
            km_totali REAL DEFAULT 0,
            stato TEXT DEFAULT 'ATTIVO',
            data_creazione TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("PRAGMA table_info(progetti)")
    colonne_progetti = {riga[1] for riga in cursor.fetchall()}

    if "nome_progetto" not in colonne_progetti:
        if "nome" in colonne_progetti:
            cursor.execute("ALTER TABLE progetti RENAME COLUMN nome TO nome_progetto")
        else:
            cursor.execute(
                "ALTER TABLE progetti ADD COLUMN nome_progetto TEXT NOT NULL DEFAULT ''"
            )
        colonne_progetti.add("nome_progetto")

    colonne_aggiuntive = {
        "km_totali": "REAL DEFAULT 0",
        "stato": "TEXT DEFAULT 'ATTIVO'",
        "data_creazione": "TEXT",
    }
    for nome_colonna, definizione in colonne_aggiuntive.items():
        if nome_colonna not in colonne_progetti:
            cursor.execute(
                f"ALTER TABLE progetti ADD COLUMN {nome_colonna} {definizione}"
            )

    cursor.execute(
        "UPDATE progetti SET data_creazione = CURRENT_TIMESTAMP "
        "WHERE data_creazione IS NULL"
    )

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

    # Cache locale (100% offline) della ripartizione superfici/divieti bici
    # calcolata confrontando i file GPX con le mappe vettoriali già scaricate
    # in data/maps/. Vedi service/superfici_service.py.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS superfici_tappa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tappa_id INTEGER UNIQUE,
            dati_json TEXT,
            calcolato_il TEXT,
            FOREIGN KEY (tappa_id) REFERENCES tappe(id)
        )
    """)

    # Cache locale (100% offline) dei nomi luogo risolti da coordinate GPS,
    # usata dal pannello di pianificazione sulla mappa per non dover rileggere
    # le mappe .mbtiles ogni volta che si riapre lo stesso percorso.
    # La chiave è la coppia di coordinate arrotondate a 5 decimali (~1 metro
    # di precisione): punti già visti in precedenza vengono riletti all'istante.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache_nomi_luoghi (
            lat_arrotondata REAL NOT NULL,
            lon_arrotondata REAL NOT NULL,
            nome TEXT,
            calcolato_il TEXT,
            PRIMARY KEY (lat_arrotondata, lon_arrotondata)
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    inizializza_database()
    print("Database e tabella 'dogane_progetto' inizializzati con successo!")