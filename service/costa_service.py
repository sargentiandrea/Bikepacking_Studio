"""Calcolo e persistenza del riepilogo di vicinanza alla costa."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import logging
import os
import sqlite3
from typing import Any

from service.config import BASE_DIR, DB_NAME


VERSIONE_ALGORITMO_COSTA = "costa_campionamento40_v1"
COASTLINE_FILE = os.path.join(BASE_DIR, "world_coastlines_10m.geojson")
_LOGGER = logging.getLogger(__name__)
_VERSIONE_DATASET_CACHE: tuple[int, int, str] | None = None

FASCE_COSTA = (
    (
        "🏖️ Da 0 a 500 metri (0 - 0.5 km)",
        "fascia_0_500m_km",
        "tappe_coinvolte_0_500m",
    ),
    (
        "🌊 Da 501 a 2500 metri (0.51 - 2.5 km)",
        "fascia_500_2500m_km",
        "tappe_coinvolte_500_2500m",
    ),
    (
        "🏞️ Da 2501 a 5000 metri (2.51 - 5 km)",
        "fascia_2500_5000m_km",
        "tappe_coinvolte_2500_5000m",
    ),
    (
        "🏜️ Oltre 5000 metri (> 5 km)",
        "fascia_oltre_5000m_km",
        "tappe_coinvolte_oltre_5000m",
    ),
)


def ottieni_versione_dataset_costa() -> str:
    """Restituisce l'hash del dataset, ricalcolandolo se cambia il file."""
    global _VERSIONE_DATASET_CACHE

    stato_file = os.stat(COASTLINE_FILE)
    chiave = (stato_file.st_mtime_ns, stato_file.st_size)
    if _VERSIONE_DATASET_CACHE is not None:
        if _VERSIONE_DATASET_CACHE[:2] == chiave:
            return _VERSIONE_DATASET_CACHE[2]

    digest = hashlib.sha256()
    with open(COASTLINE_FILE, "rb") as file_dataset:
        for blocco in iter(lambda: file_dataset.read(1024 * 1024), b""):
            digest.update(blocco)
    versione = digest.hexdigest()
    _VERSIONE_DATASET_CACHE = (chiave[0], chiave[1], versione)
    return versione


def calcola_sha256_gpx(percorso_gpx: str) -> str:
    """Calcola l'hash del file GPX usato per invalidare il riepilogo."""
    digest = hashlib.sha256()
    with open(percorso_gpx, "rb") as file_gpx:
        for blocco in iter(lambda: file_gpx.read(1024 * 1024), b""):
            digest.update(blocco)
    return digest.hexdigest()


def ottieni_metadati_gpx(percorso_gpx: str) -> tuple[int, float]:
    """Legge dimensione e data modifica senza aprire o leggere il GPX."""
    stato_file = os.stat(percorso_gpx)
    return stato_file.st_size, stato_file.st_mtime


def _ottieni_metadati_tappa(
    tappa_id: int, connessione: sqlite3.Connection
) -> tuple[float, tuple[float | None, float | None, float | None, float | None]]:
    record = connessione.execute(
        """
        SELECT distanza_km, start_lat, start_lon, end_lat, end_lon
        FROM tappe WHERE id = ?
        """,
        (tappa_id,),
    ).fetchone()
    if record is None:
        raise ValueError(f"tappa non trovata: {tappa_id}")
    distanza_km, start_lat, start_lon, end_lat, end_lon = record
    return (
        float(distanza_km or 0.0),
        (start_lat, start_lon, end_lat, end_lon),
    )


def calcola_costa_tappa(
    tappa_id: int,
    percorso_gpx: str | None,
    percorso_database: str = DB_NAME,
    *,
    connessione: sqlite3.Connection | None = None,
    distanza_km: float | None = None,
    coordinate_inizio_fine: tuple[
        float | None, float | None, float | None, float | None
    ] | None = None,
    gpx_sha256: str | None = None,
) -> dict[str, Any]:
    """Calcola la distribuzione dei km nelle fasce costiere della tappa."""
    if distanza_km is None or coordinate_inizio_fine is None:
        if connessione is not None:
            metadati = _ottieni_metadati_tappa(tappa_id, connessione)
        else:
            connessione_db = sqlite3.connect(percorso_database)
            try:
                metadati = _ottieni_metadati_tappa(tappa_id, connessione_db)
            finally:
                connessione_db.close()
        distanza_km = metadati[0] if distanza_km is None else distanza_km
        coordinate_inizio_fine = (
            metadati[1]
            if coordinate_inizio_fine is None
            else coordinate_inizio_fine
        )

    if percorso_gpx and gpx_sha256 is None:
        gpx_sha256 = calcola_sha256_gpx(percorso_gpx)

    # Riusa il parser, il motore costiero e le soglie già adottati dalle Statistiche.
    from service.stats_service import (
        _estrai_punti_gpx,
        assegna_fascia_costiera_metri,
        calcola_distanza_mare_m,
    )

    punti = _estrai_punti_gpx(percorso_gpx) if percorso_gpx else []
    conteggi = {colonna_km: 0 for _, colonna_km, _ in FASCE_COSTA}

    if len(punti) >= 2:
        # Mantiene il campionamento storico: circa 40 misure per GPX.
        passo = max(1, len(punti) // 40)
        campioni = punti[::passo]
        if punti[-1] not in campioni:
            campioni.append(punti[-1])
        for punto in campioni:
            fascia = assegna_fascia_costiera_metri(
                calcola_distanza_mare_m(punto[0], punto[1])
            )
            for etichetta, colonna_km, _ in FASCE_COSTA:
                if fascia == etichetta:
                    conteggi[colonna_km] += 1
                    break
        totale_campioni = len(campioni)
        coinvolte = {
            colonna_tappe: int(conteggi[colonna_km] > 0)
            for _, colonna_km, colonna_tappe in FASCE_COSTA
        }
        riepilogo = {
            colonna_km: (
                conteggi[colonna_km] / totale_campioni * float(distanza_km)
            )
            for _, colonna_km, _ in FASCE_COSTA
        }
    else:
        start_lat, start_lon, end_lat, end_lon = coordinate_inizio_fine
        distanza_inizio = calcola_distanza_mare_m(start_lat, start_lon)
        distanza_fine = calcola_distanza_mare_m(end_lat, end_lon)
        fascia = assegna_fascia_costiera_metri(
            (distanza_inizio + distanza_fine) / 2.0
        )
        riepilogo = {
            colonna_km: (
                float(distanza_km)
                if fascia == etichetta
                else 0.0
            )
            for etichetta, colonna_km, _ in FASCE_COSTA
        }
        coinvolte = {
            colonna_tappe: int(fascia == etichetta)
            for etichetta, _, colonna_tappe in FASCE_COSTA
        }

    metadati_file = (
        ottieni_metadati_gpx(percorso_gpx)
        if percorso_gpx and os.path.isfile(percorso_gpx)
        else None
    )
    dati: dict[str, Any] = {
        "tappa_id": tappa_id,
        "gpx_sha256": gpx_sha256,
        "versione_algoritmo_costa": VERSIONE_ALGORITMO_COSTA,
        "versione_dataset_costa": ottieni_versione_dataset_costa(),
        "totale_km": float(distanza_km),
        "gpx_size_bytes": metadati_file[0] if metadati_file else None,
        "gpx_mtime": metadati_file[1] if metadati_file else None,
        **riepilogo,
        **coinvolte,
    }
    return dati


def riepilogo_costa_aggiornato(
    connessione: sqlite3.Connection, tappa_id: int, gpx_sha256: str
) -> bool:
    """Verifica hash GPX e versioni di algoritmo e dataset."""
    record = connessione.execute(
        """
        SELECT 1
        FROM tappa_costa_riepilogo AS costa
        JOIN tappe ON tappe.id = costa.tappa_id
        WHERE costa.tappa_id = ? AND costa.gpx_sha256 = ?
          AND costa.versione_algoritmo_costa = ?
          AND costa.versione_dataset_costa = ?
          AND costa.totale_km = COALESCE(tappe.distanza_km, 0)
        """,
        (
            tappa_id,
            gpx_sha256,
            VERSIONE_ALGORITMO_COSTA,
            ottieni_versione_dataset_costa(),
        ),
    ).fetchone()
    return record is not None


def aggiorna_metadati_riepilogo_costa(
    connessione: sqlite3.Connection,
    tappa_id: int,
    gpx_size_bytes: int,
    gpx_mtime: float,
) -> bool:
    """Aggiorna i metadati rapidi solo se le colonne v4 sono disponibili."""
    colonne = {
        riga[1]
        for riga in connessione.execute(
            "PRAGMA table_info(tappa_costa_riepilogo)"
        ).fetchall()
    }
    if not {"gpx_size_bytes", "gpx_mtime"}.issubset(colonne):
        return False

    cursore = connessione.execute(
        """
        UPDATE tappa_costa_riepilogo
        SET gpx_size_bytes = ?, gpx_mtime = ?
        WHERE tappa_id = ?
        """,
        (gpx_size_bytes, gpx_mtime, tappa_id),
    )
    return cursore.rowcount > 0


def salva_riepilogo_costa(
    connessione: sqlite3.Connection, dati: dict[str, Any]
) -> None:
    """Inserisce o aggiorna il riepilogo costiero della tappa."""
    if not dati.get("gpx_sha256"):
        _LOGGER.warning(
            "Riepilogo costa non salvato per la tappa %s: GPX non disponibile",
            dati.get("tappa_id"),
        )
        return

    colonne = [
        "fascia_0_500m_km",
        "fascia_500_2500m_km",
        "fascia_2500_5000m_km",
        "fascia_oltre_5000m_km",
        "tappe_coinvolte_0_500m",
        "tappe_coinvolte_500_2500m",
        "tappe_coinvolte_2500_5000m",
        "tappe_coinvolte_oltre_5000m",
    ]
    colonne_tabella = {
        riga[1]
        for riga in connessione.execute(
            "PRAGMA table_info(tappa_costa_riepilogo)"
        ).fetchall()
    }
    metadati_presenti = {
        "gpx_size_bytes",
        "gpx_mtime",
    }.issubset(colonne_tabella)
    colonne_insert = [
        "tappa_id",
        "gpx_sha256",
        "versione_algoritmo_costa",
        "versione_dataset_costa",
        *colonne,
    ]
    valori = [
        dati["tappa_id"],
        dati["gpx_sha256"],
        dati["versione_algoritmo_costa"],
        dati["versione_dataset_costa"],
        *(dati[colonna] for colonna in colonne),
    ]
    aggiornamenti = [
        "gpx_sha256 = excluded.gpx_sha256",
        "versione_algoritmo_costa = excluded.versione_algoritmo_costa",
        "versione_dataset_costa = excluded.versione_dataset_costa",
        *(f"{colonna} = excluded.{colonna}" for colonna in colonne),
    ]
    if metadati_presenti:
        colonne_insert.extend(("gpx_size_bytes", "gpx_mtime"))
        valori.extend((dati.get("gpx_size_bytes"), dati.get("gpx_mtime")))
        aggiornamenti.extend(
            (
                "gpx_size_bytes = excluded.gpx_size_bytes",
                "gpx_mtime = excluded.gpx_mtime",
            )
        )
    colonne_insert.append("totale_km")
    valori.append(dati["totale_km"])
    colonne_insert.append("calcolato_il")
    valori.append(datetime.now(timezone.utc).isoformat())
    aggiornamenti.extend(
        (
            "totale_km = excluded.totale_km",
            "calcolato_il = excluded.calcolato_il",
        )
    )

    connessione.execute(
        f"INSERT INTO tappa_costa_riepilogo ({', '.join(colonne_insert)}) "
        f"VALUES ({', '.join('?' for _ in valori)}) "
        "ON CONFLICT(tappa_id) DO UPDATE SET "
        + ", ".join(aggiornamenti),
        valori,
    )
