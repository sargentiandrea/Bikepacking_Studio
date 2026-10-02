"""Migrazione SQLite per preferenze e scenari della catena stagionale."""

from __future__ import annotations

from contextlib import closing
from datetime import datetime
from pathlib import Path
import sqlite3


def _crea_backup(percorso_database: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    percorso_backup = percorso_database.with_name(
        f"{percorso_database.name}.backup_catena_fase3_{timestamp}"
    )
    with closing(sqlite3.connect(percorso_database)) as origine:
        with closing(sqlite3.connect(percorso_backup)) as copia:
            origine.backup(copia)
    return percorso_backup


def _colonne(connessione: sqlite3.Connection, tabella: str) -> set[str]:
    return {
        riga[1]
        for riga in connessione.execute(f"PRAGMA table_info({tabella})")
    }


def assicura_schema_catena_stagionale(
    percorso_database: str | Path,
) -> Path | None:
    """Crea le tabelle Fase 3 dopo un backup SQLite, senza migrare due volte."""
    percorso = Path(percorso_database).resolve()
    if not percorso.is_file():
        raise FileNotFoundError(f"Database non trovato: {percorso}")

    with closing(sqlite3.connect(percorso)) as connessione:
        tabelle = {
            riga[0]
            for riga in connessione.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type = 'table'
                  AND name IN ('impostazioni_semaforo', 'scenari')
                """
            )
        }
        colonne_scenari = (
            _colonne(connessione, "scenari") if "scenari" in tabelle else set()
        )

    migrazione_necessaria = (
        tabelle != {"impostazioni_semaforo", "scenari"}
        or not {"ordine_precedente_json", "annullato"} <= colonne_scenari
    )
    backup = _crea_backup(percorso) if migrazione_necessaria else None

    with closing(sqlite3.connect(percorso)) as connessione:
        connessione.execute("BEGIN IMMEDIATE")
        connessione.execute(
            """
            CREATE TABLE IF NOT EXISTS impostazioni_semaforo (
                id_progetto INTEGER PRIMARY KEY,
                temp_min_verde REAL DEFAULT 15.0,
                temp_max_verde REAL DEFAULT 28.0,
                temp_min_giallo REAL DEFAULT 5.0,
                temp_max_giallo REAL DEFAULT 35.0,
                pioggia_max_verde REAL DEFAULT 50.0,
                pioggia_max_giallo REAL DEFAULT 100.0,
                vento_max_verde REAL DEFAULT 20.0,
                vento_max_giallo REAL DEFAULT 35.0,
                priorita_caldo INTEGER DEFAULT 1,
                aggiornato_il TEXT
            )
            """
        )
        connessione.execute(
            """
            CREATE TABLE IF NOT EXISTS scenari (
                id INTEGER PRIMARY KEY,
                id_progetto INTEGER NOT NULL,
                nome TEXT NOT NULL,
                ordine_json TEXT NOT NULL,
                creato_il TEXT NOT NULL,
                applicato INTEGER DEFAULT 0,
                ordine_precedente_json TEXT,
                annullato INTEGER DEFAULT 0
            )
            """
        )

        colonne_scenari = _colonne(connessione, "scenari")
        if "ordine_precedente_json" not in colonne_scenari:
            connessione.execute(
                "ALTER TABLE scenari ADD COLUMN ordine_precedente_json TEXT"
            )
        if "annullato" not in colonne_scenari:
            connessione.execute(
                "ALTER TABLE scenari ADD COLUMN annullato INTEGER DEFAULT 0"
            )
        connessione.commit()
    return backup
