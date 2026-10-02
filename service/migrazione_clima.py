"""Migrazione incrementale delle tabelle per i riepiloghi climatici."""

from __future__ import annotations

from datetime import datetime
from contextlib import closing
from pathlib import Path
import sqlite3


def _crea_backup(percorso_database: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    percorso_backup = percorso_database.with_name(
        f"{percorso_database.name}.backup_clima_{timestamp}"
    )
    with closing(sqlite3.connect(percorso_database)) as origine:
        with closing(sqlite3.connect(percorso_backup)) as copia:
            origine.backup(copia)
    return percorso_backup


def assicura_schema_clima(percorso_database: str | Path) -> None:
    """Crea la tabella climatica, con backup prima della prima modifica."""
    percorso = Path(percorso_database).resolve()
    if not percorso.is_file():
        raise FileNotFoundError(f"Database non trovato: {percorso}")

    with closing(sqlite3.connect(percorso)) as connessione:
        esiste_tabella = connessione.execute(
            """
            SELECT 1 FROM sqlite_master
            WHERE type = 'table' AND name = 'clima_blocco_mese'
            """
        ).fetchone() is not None

    if not esiste_tabella:
        _crea_backup(percorso)

    with closing(sqlite3.connect(percorso)) as connessione:
        connessione.execute("BEGIN")
        connessione.execute(
            """
            CREATE TABLE IF NOT EXISTS clima_blocco_mese (
                id_progetto INTEGER NOT NULL,
                nome_blocco TEXT NOT NULL,
                mese INTEGER NOT NULL CHECK (mese BETWEEN 1 AND 12),
                temperatura_media REAL,
                temperatura_max REAL,
                temperatura_min REAL,
                precipitazioni_mm REAL,
                vento_media REAL,
                dataset_versione TEXT NOT NULL,
                aggiornato_il TEXT NOT NULL,
                copertura_pct REAL NOT NULL DEFAULT 0,
                campioni_validi INTEGER NOT NULL DEFAULT 0,
                campioni_totali INTEGER NOT NULL DEFAULT 0,
                anni_coperti TEXT NOT NULL DEFAULT '{}',
                PRIMARY KEY (id_progetto, nome_blocco, mese)
            )
            """
        )
        connessione.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_clima_blocco_mese_progetto
            ON clima_blocco_mese (id_progetto, nome_blocco)
            """
        )
        connessione.commit()
