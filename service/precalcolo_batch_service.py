"""Orchestrazione del precalcolo di massa delle tappe esistenti."""

from __future__ import annotations

import os
import sqlite3
import threading
import time
from typing import Any

from service.config import DB_NAME
from service.gpx_metrics_service import analizza_gpx
from service.geometria_service import VERSIONE_ALGORITMO_GEOMETRIA
from service.costa_service import (
    VERSIONE_ALGORITMO_COSTA,
    ottieni_versione_dataset_costa,
)
from service.precalcolo_service import (
    VERSIONE_ALGORITMI,
    calcola_sha256,
    precalcola_tappa,
)


_stato_lock = threading.Lock()
_batch_interrotto = False
_stato_batch: dict[str, Any] = {
    "stato": "INATTIVO",
    "elaborate": 0,
    "saltate": 0,
    "fallite": 0,
    "totale": 0,
    "progresso": "0 su 0",
    "errore": None,
}


def _percorso_gpx(nome_file: str | None) -> str | None:
    """Risolve il file GPX nelle posizioni gestite dall'app."""
    if not nome_file:
        return None

    nome = os.path.basename(nome_file)
    radice_progetto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidati = [
        nome_file,
        os.path.join(radice_progetto, nome_file),
        os.path.join(radice_progetto, "gpx", nome),
        os.path.join(radice_progetto, "uploads", nome),
        os.path.join(radice_progetto, "tracks", nome),
    ]
    for candidato in candidati:
        if os.path.isfile(candidato):
            return os.path.abspath(candidato)
    return None


def _tappe_attive(id_progetto: int | None) -> list[tuple[int, str | None]]:
    """Legge le tappe da elaborare rispettando il filtro del progetto."""
    connessione = sqlite3.connect(DB_NAME)
    try:
        if id_progetto is None:
            query = """
                SELECT id, nome_file
                FROM tappe
                WHERE stato = 'ATTIVA'
                ORDER BY id
            """
            return connessione.execute(query).fetchall()

        query = """
            SELECT id, nome_file
            FROM tappe
            WHERE stato = 'ATTIVA' AND id_progetto = ?
            ORDER BY id
        """
        return connessione.execute(query, (id_progetto,)).fetchall()
    finally:
        connessione.close()


def _ha_analisi_aggiornata(tappa_id: int, percorso_gpx: str) -> bool:
    """Verifica se l'analisi completa corrisponde al file attuale."""
    hash_gpx = calcola_sha256(percorso_gpx)
    connessione = sqlite3.connect(DB_NAME)
    try:
        record = connessione.execute(
            """
            SELECT 1
            FROM tappa_analisi AS analisi
            JOIN tappe ON tappe.id = analisi.tappa_id
            JOIN tappa_geometrie AS geometria
              ON geometria.tappa_id = analisi.tappa_id
            JOIN tappa_costa_riepilogo AS costa
              ON costa.tappa_id = analisi.tappa_id
            WHERE analisi.tappa_id = ? AND analisi.gpx_sha256 = ?
              AND analisi.versione_algoritmi = ? AND analisi.stato = 'COMPLETO'
              AND geometria.gpx_sha256 = analisi.gpx_sha256
              AND geometria.versione_algoritmo = ?
              AND costa.gpx_sha256 = analisi.gpx_sha256
              AND costa.versione_algoritmo_costa = ?
              AND costa.versione_dataset_costa = ?
              AND costa.totale_km = COALESCE(tappe.distanza_km, 0)
            """,
            (
                tappa_id,
                hash_gpx,
                VERSIONE_ALGORITMI,
                VERSIONE_ALGORITMO_GEOMETRIA,
                VERSIONE_ALGORITMO_COSTA,
                ottieni_versione_dataset_costa(),
            ),
        ).fetchone()
        return record is not None
    except sqlite3.OperationalError:
        # Se una migrazione non è ancora presente, il batch tenta il salvataggio.
        return False
    except OSError:
        # L'assenza del dataset costa non deve invalidare le metriche GPX.
        return False
    finally:
        connessione.close()


def _salva_errore_file(tappa_id: int, messaggio: str) -> None:
    """Registra un errore quando il file non può essere analizzato."""
    connessione = sqlite3.connect(DB_NAME)
    try:
        connessione.execute(
            """
            INSERT INTO tappa_analisi (
                tappa_id, gpx_sha256, versione_algoritmi, stato,
                errore, aggiornato_il
            )
            VALUES (?, ?, ?, 'ERRORE', ?, datetime('now'))
            ON CONFLICT(tappa_id) DO UPDATE SET
                gpx_sha256 = excluded.gpx_sha256,
                versione_algoritmi = excluded.versione_algoritmi,
                stato = 'ERRORE',
                errore = excluded.errore,
                aggiornato_il = excluded.aggiornato_il
            """,
            (tappa_id, "file-non-disponibile", VERSIONE_ALGORITMI, messaggio),
        )
        connessione.commit()
    finally:
        connessione.close()


def _imposta_stato(**valori: Any) -> None:
    with _stato_lock:
        _stato_batch.update(valori)


def precalcola_tutte_le_tappe(id_progetto: int | None = None) -> dict[str, Any]:
    """Precalcola tutte le tappe attive, continuando dopo gli errori."""
    global _batch_interrotto

    tappe = _tappe_attive(id_progetto)
    with _stato_lock:
        _batch_interrotto = False
        _stato_batch.update(
            {
                "stato": "IN_CORSO",
                "elaborate": 0,
                "saltate": 0,
                "fallite": 0,
                "totale": len(tappe),
                "progresso": f"0 su {len(tappe)}",
                "errore": None,
            }
        )

    inizio = time.perf_counter()
    elaborate = 0
    saltate = 0
    fallite = 0
    errori: list[dict[str, Any]] = []

    for indice, (tappa_id, nome_file) in enumerate(tappe, start=1):
        with _stato_lock:
            interrotto = _batch_interrotto
        if interrotto:
            _imposta_stato(
                stato="INTERROTTO",
                progresso=f"{indice - 1} su {len(tappe)}",
            )
            break

        percorso_gpx = _percorso_gpx(nome_file)
        try:
            if percorso_gpx is None:
                raise FileNotFoundError(
                    f"GPX non trovato per la tappa {tappa_id}: {nome_file or '(vuoto)'}"
                )

            if _ha_analisi_aggiornata(tappa_id, percorso_gpx):
                saltate += 1
            else:
                risultato = precalcola_tappa(tappa_id, percorso_gpx, DB_NAME)
                if risultato.get("stato") == "ERRORE":
                    fallite += 1
                    errori.append(
                        {
                            "tappa_id": tappa_id,
                            "errore": risultato.get("errore", "errore di analisi"),
                        }
                    )
                elif risultato.get("costa_errore"):
                    fallite += 1
                    errori.append(
                        {
                            "tappa_id": tappa_id,
                            "errore": risultato["costa_errore"],
                        }
                    )
                else:
                    elaborate += 1
        except Exception as errore:
            fallite += 1
            messaggio = str(errore)
            errori.append({"tappa_id": tappa_id, "errore": messaggio})
            try:
                _salva_errore_file(tappa_id, messaggio)
            except sqlite3.Error as errore_db:
                errori[-1]["errore_db"] = str(errore_db)

        _imposta_stato(
            elaborate=elaborate,
            saltate=saltate,
            fallite=fallite,
            progresso=f"{indice} su {len(tappe)}",
        )

    with _stato_lock:
        interrotto = _batch_interrotto
    stato_finale = "INTERROTTO" if interrotto else "COMPLETATO"
    tempo_totale = time.perf_counter() - inizio
    riepilogo = {
        "stato": stato_finale,
        "elaborate": elaborate,
        "saltate": saltate,
        "fallite": fallite,
        "totale": len(tappe),
        "tempo_totale_secondi": round(tempo_totale, 3),
        "errori": errori,
    }
    _imposta_stato(
        stato=stato_finale,
        errore=errori[-1]["errore"] if errori and stato_finale == "INTERROTTO" else None,
    )
    return riepilogo


def stima_tempo_precalcolo(id_progetto: int | None = None) -> float:
    """Stima in secondi il tempo necessario per le tappe non aggiornate."""
    tappe = _tappe_attive(id_progetto)
    mancanti: list[tuple[int, str]] = []
    for tappa_id, nome_file in tappe:
        percorso_gpx = _percorso_gpx(nome_file)
        if percorso_gpx is None:
            continue
        try:
            if not _ha_analisi_aggiornata(tappa_id, percorso_gpx):
                mancanti.append((tappa_id, percorso_gpx))
        except (OSError, sqlite3.Error):
            mancanti.append((tappa_id, percorso_gpx))

    campione = mancanti[:5]
    tempi: list[float] = []
    for tappa_id, percorso_gpx in campione:
        inizio = time.perf_counter()
        try:
            analizza_gpx(percorso_gpx)
            from service.costa_service import calcola_costa_tappa

            calcola_costa_tappa(tappa_id, percorso_gpx)
        except (OSError, ValueError):
            continue
        tempi.append(time.perf_counter() - inizio)

    tempo_medio = sum(tempi) / len(tempi) if tempi else 0.0
    return round(tempo_medio * len(mancanti), 3)


def ottieni_stato_batch() -> dict[str, Any]:
    """Restituisce una copia dello stato corrente del batch."""
    with _stato_lock:
        return dict(_stato_batch)


def interrompi_batch() -> None:
    """Richiede l'interruzione dopo la tappa attualmente in elaborazione."""
    global _batch_interrotto
    with _stato_lock:
        _batch_interrotto = True


if __name__ == "__main__":
    risultato_batch = precalcola_tutte_le_tappe()
    print(risultato_batch)
