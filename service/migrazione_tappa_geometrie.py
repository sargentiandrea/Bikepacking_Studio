"""Migrazione v2 per la geometria GPX compressa delle tappe."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil
import sqlite3


VERSIONE_MIGRAZIONE = "v2"
PERCORSO_DATABASE = (
    Path(__file__).resolve().parent.parent / "data" / "bikepacking_app.db"
)


def crea_backup(percorso_database: Path) -> Path:
    """Crea una copia timestampata prima di modificare il database."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    percorso_backup = percorso_database.with_name(
        f"{percorso_database.name}.backup_geometrie_{timestamp}"
    )
    shutil.copy2(percorso_database, percorso_backup)
    print(f"Backup creato: {percorso_backup}")
    return percorso_backup


def esegui_migrazione(percorso_database: Path = PERCORSO_DATABASE) -> None:
    """Crea la tabella geometrie senza alterare le tabelle esistenti."""
    if not percorso_database.is_file():
        raise FileNotFoundError(
            f"database non trovato: {percorso_database}"
        )

    crea_backup(percorso_database)
    with sqlite3.connect(percorso_database) as connessione:
        connessione.execute("PRAGMA foreign_keys = ON")
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

        print("Creo tabella tappa_geometrie (se non esiste)...")
        connessione.execute(
            """
            CREATE TABLE IF NOT EXISTS tappa_geometrie (
                tappa_id INTEGER PRIMARY KEY,
                gpx_sha256 TEXT NOT NULL,
                versione_algoritmo TEXT NOT NULL,
                geometria_completa BLOB NOT NULL,
                geometria_semplificata BLOB NOT NULL,
                bbox_min_lat REAL NOT NULL,
                bbox_min_lon REAL NOT NULL,
                bbox_max_lat REAL NOT NULL,
                bbox_max_lon REAL NOT NULL,
                numero_punti_originali INTEGER NOT NULL,
                numero_punti_semplificati INTEGER NOT NULL,
                aggiornato_il TEXT NOT NULL,
                FOREIGN KEY (tappa_id)
                    REFERENCES tappe(id)
                    ON DELETE CASCADE
            )
            """
        )
        print(f"Migrazione {VERSIONE_MIGRAZIONE} completata.")


def main() -> int:
    try:
        esegui_migrazione()
    except (FileNotFoundError, OSError, RuntimeError, sqlite3.Error) as errore:
        print(f"Migrazione fallita: {errore}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
