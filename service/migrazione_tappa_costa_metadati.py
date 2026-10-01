"""Migrazione v4 per i metadati rapidi dei file GPX della costa."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sqlite3


VERSIONE_MIGRAZIONE = "v4"
PERCORSO_DATABASE = (
    Path(__file__).resolve().parent.parent / "data" / "bikepacking_app.db"
)


def crea_backup(percorso_database: Path) -> Path:
    """Crea una copia coerente del database tramite l'API SQLite."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    percorso_backup = percorso_database.with_name(
        f"{percorso_database.name}.backup_costa_metadati_{timestamp}"
    )
    origine = sqlite3.connect(percorso_database)
    destinazione = sqlite3.connect(percorso_backup)
    try:
        origine.backup(destinazione)
    finally:
        destinazione.close()
        origine.close()
    return percorso_backup


def esegui_migrazione(
    percorso_database: Path = PERCORSO_DATABASE,
) -> Path | None:
    """Aggiunge le colonne dei metadati, creando il backup solo se necessario."""
    if not percorso_database.is_file():
        raise FileNotFoundError(f"database non trovato: {percorso_database}")

    connessione = sqlite3.connect(percorso_database)
    try:
        tabella_esistente = connessione.execute(
            """
            SELECT 1 FROM sqlite_master
            WHERE type = 'table' AND name = 'tappa_costa_riepilogo'
            """
        ).fetchone()
        if tabella_esistente is None:
            raise RuntimeError(
                "la tabella tappa_costa_riepilogo non esiste: "
                "eseguire prima la migrazione v3"
            )

        colonne = {
            riga[1]
            for riga in connessione.execute(
                "PRAGMA table_info(tappa_costa_riepilogo)"
            ).fetchall()
        }
    finally:
        connessione.close()

    colonne_da_aggiungere = {
        "gpx_size_bytes": "INTEGER",
        "gpx_mtime": "REAL",
    }
    mancanti = {
        nome: definizione
        for nome, definizione in colonne_da_aggiungere.items()
        if nome not in colonne
    }
    if not mancanti:
        return None

    percorso_backup = crea_backup(percorso_database)
    connessione = sqlite3.connect(percorso_database)
    try:
        with connessione:
            colonne_correnti = {
                riga[1]
                for riga in connessione.execute(
                    "PRAGMA table_info(tappa_costa_riepilogo)"
                ).fetchall()
            }
            for nome, definizione in colonne_da_aggiungere.items():
                if nome not in colonne_correnti:
                    connessione.execute(
                        f"ALTER TABLE tappa_costa_riepilogo "
                        f"ADD COLUMN {nome} {definizione}"
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
        print(f"Migrazione {VERSIONE_MIGRAZIONE}: colonne già presenti.")
    else:
        print(f"Backup SQLite creato: {backup}")
        print(f"Migrazione {VERSIONE_MIGRAZIONE} completata.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
