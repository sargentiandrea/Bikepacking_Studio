"""Migrazione v3 per il riepilogo precalcolato della costa."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sqlite3


VERSIONE_MIGRAZIONE = "v3"
PERCORSO_DATABASE = (
    Path(__file__).resolve().parent.parent / "data" / "bikepacking_app.db"
)


def crea_backup(percorso_database: Path) -> Path:
    """Crea il backup tramite SQLite, includendo correttamente eventuale WAL."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    percorso_backup = percorso_database.with_name(
        f"{percorso_database.name}.backup_costa_{timestamp}"
    )
    origine = sqlite3.connect(percorso_database)
    destinazione = sqlite3.connect(percorso_backup)
    try:
        origine.backup(destinazione)
    finally:
        destinazione.close()
        origine.close()
    return percorso_backup


def esegui_migrazione(percorso_database: Path = PERCORSO_DATABASE) -> Path | None:
    """Crea la tabella dei riepiloghi; se è già presente non modifica il DB."""
    if not percorso_database.is_file():
        raise FileNotFoundError(f"database non trovato: {percorso_database}")

    connessione = sqlite3.connect(percorso_database)
    try:
        tabella_tappe = connessione.execute(
            """
            SELECT 1 FROM sqlite_master
            WHERE type = 'table' AND name = 'tappe'
            """
        ).fetchone()
        if tabella_tappe is None:
            raise RuntimeError(
                "la tabella tappe non esiste: migrazione annullata"
            )

        tabella_esistente = connessione.execute(
            """
            SELECT 1 FROM sqlite_master
            WHERE type = 'table' AND name = 'tappa_costa_riepilogo'
            """
        ).fetchone()
        if tabella_esistente is not None:
            return None
    finally:
        connessione.close()

    percorso_backup = crea_backup(percorso_database)
    connessione = sqlite3.connect(percorso_database)
    try:
        connessione.execute("PRAGMA foreign_keys = ON")
        with connessione:
            connessione.execute(
                """
                CREATE TABLE IF NOT EXISTS tappa_costa_riepilogo (
                    tappa_id INTEGER PRIMARY KEY,
                    gpx_sha256 TEXT NOT NULL,
                    versione_algoritmo_costa TEXT NOT NULL,
                    versione_dataset_costa TEXT NOT NULL,
                    fascia_0_500m_km REAL NOT NULL DEFAULT 0,
                    fascia_500_2500m_km REAL NOT NULL DEFAULT 0,
                    fascia_2500_5000m_km REAL NOT NULL DEFAULT 0,
                    fascia_oltre_5000m_km REAL NOT NULL DEFAULT 0,
                    tappe_coinvolte_0_500m INTEGER NOT NULL DEFAULT 0,
                    tappe_coinvolte_500_2500m INTEGER NOT NULL DEFAULT 0,
                    tappe_coinvolte_2500_5000m INTEGER NOT NULL DEFAULT 0,
                    tappe_coinvolte_oltre_5000m INTEGER NOT NULL DEFAULT 0,
                    totale_km REAL NOT NULL DEFAULT 0,
                    calcolato_il TEXT NOT NULL,
                    FOREIGN KEY (tappa_id)
                        REFERENCES tappe(id)
                        ON DELETE CASCADE
                )
                """
            )
    finally:
        connessione.close()
    return percorso_backup


def main() -> int:
    try:
        backup = esegui_migrazione()
    except (FileNotFoundError, OSError, RuntimeError, sqlite3.Error) as errore:
        print(f"Migrazione fallita: {errore}")
        return 1
    if backup is None:
        print(f"Migrazione {VERSIONE_MIGRAZIONE}: tabella già presente.")
    else:
        print(f"Backup SQLite creato: {backup}")
        print(f"Migrazione {VERSIONE_MIGRAZIONE} completata.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
