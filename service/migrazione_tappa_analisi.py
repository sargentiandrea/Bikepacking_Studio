"""Migrazione v1 per le tabelle del precalcolo delle tappe."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil
import sqlite3


VERSIONE_MIGRAZIONE = "v1"
PERCORSO_DATABASE = (
    Path(__file__).resolve().parent.parent / "data" / "bikepacking_app.db"
)


def crea_backup(percorso_database: Path) -> Path:
    """Crea una copia timestampata del database prima della migrazione."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    percorso_backup = percorso_database.with_name(
        f"{percorso_database.name}.backup_{timestamp}"
    )
    shutil.copy2(percorso_database, percorso_backup)
    print(f"Backup creato: {percorso_backup}")
    return percorso_backup


def esegui_migrazione(percorso_database: Path = PERCORSO_DATABASE) -> None:
    """Esegue la migrazione v1 in modo idempotente."""
    if not percorso_database.is_file():
        raise FileNotFoundError(
            f"database non trovato: {percorso_database}"
        )

    crea_backup(percorso_database)

    with sqlite3.connect(percorso_database) as connessione:
        connessione.execute("PRAGMA foreign_keys = ON")

        print("Controllo la tabella tappe...")
        tabella_tappe = connessione.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table' AND name = 'tappe'
            """
        ).fetchone()
        if tabella_tappe is None:
            raise RuntimeError(
                "la tabella tappe non esiste: migrazione annullata"
            )

        print("Creo tabella tappa_analisi (se non esiste)...")
        connessione.execute(
            """
            CREATE TABLE IF NOT EXISTS tappa_analisi (
                tappa_id INTEGER PRIMARY KEY,
                gpx_sha256 TEXT NOT NULL,
                versione_algoritmi TEXT NOT NULL,
                distanza_km REAL,
                dislivello_pos_m REAL,
                dislivello_neg_m REAL,
                quota_min_m REAL,
                quota_max_m REAL,
                pendenza_media_pct REAL,
                pendenza_max_pct REAL,
                bbox_min_lon REAL,
                bbox_min_lat REAL,
                bbox_max_lon REAL,
                bbox_max_lat REAL,
                stato TEXT NOT NULL CHECK (
                    stato IN (
                        'NON_CALCOLATO',
                        'IN_CODA',
                        'IN_CORSO',
                        'PARZIALE',
                        'COMPLETO',
                        'ERRORE'
                    )
                ),
                errore TEXT,
                aggiornato_il TEXT,
                FOREIGN KEY (tappa_id)
                    REFERENCES tappe(id)
                    ON DELETE CASCADE
            )
            """
        )

        print("Creo tabella tappa_segmenti (se non esiste)...")
        connessione.execute(
            """
            CREATE TABLE IF NOT EXISTS tappa_segmenti (
                tappa_id INTEGER NOT NULL,
                track_index INTEGER NOT NULL,
                segment_index INTEGER NOT NULL,
                punti INTEGER,
                distanza_km REAL,
                dislivello_pos_m REAL,
                dislivello_neg_m REAL,
                quota_min_m REAL,
                quota_max_m REAL,
                versione_algoritmi TEXT,
                PRIMARY KEY (tappa_id, track_index, segment_index),
                FOREIGN KEY (tappa_id)
                    REFERENCES tappe(id)
                    ON DELETE CASCADE
            )
            """
        )

        print(f"Migrazione {VERSIONE_MIGRAZIONE} completata.")


def main() -> int:
    """Punto di ingresso per l'esecuzione da terminale."""
    try:
        esegui_migrazione()
    except (FileNotFoundError, OSError, RuntimeError, sqlite3.Error) as exc:
        print(f"Migrazione fallita: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
