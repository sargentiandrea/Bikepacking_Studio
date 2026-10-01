"""Persistenza delle metriche precalcolate di una tappa."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import logging
import os
import sqlite3
from typing import Any

from shapely.errors import ShapelyError

from service.gpx_metrics_service import analizza_gpx
from service.geometria_service import (
    VERSIONE_ALGORITMO_GEOMETRIA,
    calcola_geometria_gpx,
)
from service.costa_service import (
    calcola_costa_tappa,
    aggiorna_metadati_riepilogo_costa,
    ottieni_metadati_gpx,
    riepilogo_costa_aggiornato,
    salva_riepilogo_costa,
)


VERSIONE_ALGORITMI = "gpx_metrics_v1"
_LOGGER = logging.getLogger(__name__)
_ANOMALIE_GESTITE = (
    "misure di pendenza scartate come anomale",
    "punti duplicati rimossi",
)


def calcola_sha256(percorso_file: str) -> str:
    """Calcola l'hash del file GPX conservato sul disco."""
    digest = hashlib.sha256()
    with open(percorso_file, "rb") as file_gpx:
        for blocco in iter(lambda: file_gpx.read(1024 * 1024), b""):
            digest.update(blocco)
    return digest.hexdigest()


def _ora_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _geometria_aggiornata(
    connessione: sqlite3.Connection,
    tappa_id: int,
    gpx_sha256: str,
) -> bool:
    try:
        record = connessione.execute(
            """
            SELECT 1 FROM tappa_geometrie
            WHERE tappa_id = ? AND gpx_sha256 = ?
              AND versione_algoritmo = ?
            """,
            (tappa_id, gpx_sha256, VERSIONE_ALGORITMO_GEOMETRIA),
        ).fetchone()
    except sqlite3.OperationalError:
        return False
    return record is not None


def _salva_costa_se_necessario(
    connessione: sqlite3.Connection,
    tappa_id: int,
    percorso_file: str,
    gpx_sha256: str,
) -> str | None:
    """Salva la costa se manca o se il GPX/dataset è cambiato."""
    try:
        gpx_size_bytes, gpx_mtime = ottieni_metadati_gpx(percorso_file)
        if riepilogo_costa_aggiornato(connessione, tappa_id, gpx_sha256):
            aggiorna_metadati_riepilogo_costa(
                connessione,
                tappa_id,
                gpx_size_bytes,
                gpx_mtime,
            )
            return None
        dati_costa = calcola_costa_tappa(
            tappa_id,
            percorso_file,
            connessione=connessione,
            gpx_sha256=gpx_sha256,
        )
        salva_riepilogo_costa(connessione, dati_costa)
        return None
    except (
        OSError,
        ValueError,
        RuntimeError,
        sqlite3.Error,
        ShapelyError,
    ) as errore:
        _LOGGER.exception("Precalcolo costa fallito per la tappa %s", tappa_id)
        return str(errore)


def _salva_geometria(
    connessione: sqlite3.Connection,
    tappa_id: int,
    percorso_file: str,
    gpx_sha256: str,
) -> bool:
    """Salva i due livelli geometrici senza invalidare le metriche se fallisce."""
    try:
        geometria = calcola_geometria_gpx(percorso_file)
        connessione.execute(
            """
            INSERT INTO tappa_geometrie (
                tappa_id, gpx_sha256, versione_algoritmo,
                geometria_completa, geometria_semplificata,
                bbox_min_lat, bbox_min_lon, bbox_max_lat, bbox_max_lon,
                numero_punti_originali, numero_punti_semplificati,
                aggiornato_il
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(tappa_id) DO UPDATE SET
                gpx_sha256 = excluded.gpx_sha256,
                versione_algoritmo = excluded.versione_algoritmo,
                geometria_completa = excluded.geometria_completa,
                geometria_semplificata = excluded.geometria_semplificata,
                bbox_min_lat = excluded.bbox_min_lat,
                bbox_min_lon = excluded.bbox_min_lon,
                bbox_max_lat = excluded.bbox_max_lat,
                bbox_max_lon = excluded.bbox_max_lon,
                numero_punti_originali = excluded.numero_punti_originali,
                numero_punti_semplificati = excluded.numero_punti_semplificati,
                aggiornato_il = excluded.aggiornato_il
            """,
            (
                tappa_id,
                gpx_sha256,
                geometria["versione_algoritmo"],
                geometria["geometria_completa"],
                geometria["geometria_semplificata"],
                geometria["bbox_min_lat"],
                geometria["bbox_min_lon"],
                geometria["bbox_max_lat"],
                geometria["bbox_max_lon"],
                geometria["numero_punti_originali"],
                geometria["numero_punti_semplificati"],
                _ora_utc(),
            ),
        )
        return True
    except (OSError, ValueError, sqlite3.Error):
        _LOGGER.exception("Salvataggio geometria fallito per la tappa %s", tappa_id)
        return False


def _anomalie_bloccanti(anomalie: list[str]) -> list[str]:
    """Separa i filtri gestiti dalle anomalie che rendono incompleti i dati."""
    anomalie_gestite = [
        anomalia
        for anomalia in anomalie
        if any(tipo in anomalia.casefold() for tipo in _ANOMALIE_GESTITE)
    ]
    if anomalie_gestite:
        _LOGGER.info("Filtri GPX gestiti: %s", anomalie_gestite)

    anomalie_bloccanti = [
        anomalia
        for anomalia in anomalie
        if not any(tipo in anomalia.casefold() for tipo in _ANOMALIE_GESTITE)
    ]
    if anomalie_bloccanti:
        _LOGGER.warning(
            "Anomalie GPX che rendono parziale l'analisi: %s",
            anomalie_bloccanti,
        )

    return anomalie_bloccanti


def _salva_errore(
    connessione: sqlite3.Connection,
    tappa_id: int,
    gpx_sha256: str,
    messaggio: str,
) -> None:
    """Salva un errore di analisi senza modificare la distanza della tappa."""
    connessione.execute(
        """
        INSERT INTO tappa_analisi (
            tappa_id, gpx_sha256, versione_algoritmi, stato, errore, aggiornato_il
        )
        VALUES (?, ?, ?, 'ERRORE', ?, ?)
        ON CONFLICT(tappa_id) DO UPDATE SET
            gpx_sha256 = excluded.gpx_sha256,
            versione_algoritmi = excluded.versione_algoritmi,
            stato = 'ERRORE',
            errore = excluded.errore,
            aggiornato_il = excluded.aggiornato_il
        """,
        (tappa_id, gpx_sha256, VERSIONE_ALGORITMI, messaggio, _ora_utc()),
    )


def precalcola_tappa(
    tappa_id: int,
    percorso_file: str,
    percorso_database: str,
) -> dict[str, Any]:
    """Calcola e salva una volta le metriche del GPX associato alla tappa."""
    gpx_sha256 = calcola_sha256(percorso_file)

    with sqlite3.connect(percorso_database) as connessione:
        connessione.execute("PRAGMA foreign_keys = ON")
        # Un GPX sostituito invalida i riepiloghi di tutte le tappe che lo condividono.
        tabella_costa = connessione.execute(
            """
            SELECT 1 FROM sqlite_master
            WHERE type = 'table' AND name = 'tappa_costa_riepilogo'
            """
        ).fetchone()
        if tabella_costa is not None:
            connessione.execute(
                """
                DELETE FROM tappa_costa_riepilogo
                WHERE tappa_id IN (
                    SELECT id FROM tappe
                    WHERE nome_file IN (?, ?)
                )
                  AND gpx_sha256 != ?
                """,
                (
                    percorso_file,
                    os.path.basename(percorso_file),
                    gpx_sha256,
                ),
            )

        record = connessione.execute(
            """
            SELECT gpx_sha256, versione_algoritmi, stato
            FROM tappa_analisi
            WHERE tappa_id = ?
            """,
            (tappa_id,),
        ).fetchone()
        if record and record[0] == gpx_sha256 and record[1] == VERSIONE_ALGORITMI:
            if record[2] == "COMPLETO":
                if not _geometria_aggiornata(connessione, tappa_id, gpx_sha256):
                    _salva_geometria(
                        connessione, tappa_id, percorso_file, gpx_sha256
                    )
                errore_costa = _salva_costa_se_necessario(
                    connessione, tappa_id, percorso_file, gpx_sha256
                )
                return {
                    "stato": "COMPLETO",
                    "saltato": True,
                    "costa_errore": errore_costa,
                }

        analisi_esistente = connessione.execute(
            """
            SELECT tappa_id
            FROM tappa_analisi
            WHERE gpx_sha256 = ? AND versione_algoritmi = ?
              AND stato = 'COMPLETO' AND tappa_id != ?
            LIMIT 1
            """,
            (gpx_sha256, VERSIONE_ALGORITMI, tappa_id),
        ).fetchone()
        if analisi_esistente:
            tappa_origine_id = analisi_esistente[0]
            connessione.execute(
                """
                INSERT INTO tappa_analisi (
                    tappa_id, gpx_sha256, versione_algoritmi, distanza_km,
                    dislivello_pos_m, dislivello_neg_m, quota_min_m, quota_max_m,
                    pendenza_media_pct, pendenza_max_pct, bbox_min_lon,
                    bbox_min_lat, bbox_max_lon, bbox_max_lat, stato, errore,
                    aggiornato_il
                )
                SELECT ?, gpx_sha256, versione_algoritmi, distanza_km,
                       dislivello_pos_m, dislivello_neg_m, quota_min_m, quota_max_m,
                       pendenza_media_pct, pendenza_max_pct, bbox_min_lon,
                       bbox_min_lat, bbox_max_lon, bbox_max_lat, stato, errore,
                       ?
                FROM tappa_analisi
                WHERE tappa_id = ?
                ON CONFLICT(tappa_id) DO UPDATE SET
                    gpx_sha256 = excluded.gpx_sha256,
                    versione_algoritmi = excluded.versione_algoritmi,
                    distanza_km = excluded.distanza_km,
                    dislivello_pos_m = excluded.dislivello_pos_m,
                    dislivello_neg_m = excluded.dislivello_neg_m,
                    quota_min_m = excluded.quota_min_m,
                    quota_max_m = excluded.quota_max_m,
                    pendenza_media_pct = excluded.pendenza_media_pct,
                    pendenza_max_pct = excluded.pendenza_max_pct,
                    bbox_min_lon = excluded.bbox_min_lon,
                    bbox_min_lat = excluded.bbox_min_lat,
                    bbox_max_lon = excluded.bbox_max_lon,
                    bbox_max_lat = excluded.bbox_max_lat,
                    stato = excluded.stato,
                    errore = excluded.errore,
                    aggiornato_il = excluded.aggiornato_il
                """,
                (tappa_id, _ora_utc(), tappa_origine_id),
            )
            connessione.execute(
                "DELETE FROM tappa_segmenti WHERE tappa_id = ?", (tappa_id,)
            )
            connessione.execute(
                """
                INSERT INTO tappa_segmenti (
                    tappa_id, track_index, segment_index, punti, distanza_km,
                    dislivello_pos_m, dislivello_neg_m, quota_min_m,
                    quota_max_m, versione_algoritmi
                )
                SELECT ?, track_index, segment_index, punti, distanza_km,
                       dislivello_pos_m, dislivello_neg_m, quota_min_m,
                       quota_max_m, versione_algoritmi
                FROM tappa_segmenti
                WHERE tappa_id = ?
                """,
                (tappa_id, tappa_origine_id),
            )
            connessione.execute(
                """
                UPDATE tappe
                SET distanza_km = (
                    SELECT distanza_km FROM tappa_analisi WHERE tappa_id = ?
                )
                WHERE id = ?
                """,
                (tappa_id, tappa_id),
            )
            if not _geometria_aggiornata(connessione, tappa_id, gpx_sha256):
                _salva_geometria(
                    connessione, tappa_id, percorso_file, gpx_sha256
                )
            errore_costa = _salva_costa_se_necessario(
                connessione, tappa_id, percorso_file, gpx_sha256
            )
            return {
                "stato": "COMPLETO",
                "saltato": True,
                "costa_errore": errore_costa,
            }

        connessione.execute(
            """
            INSERT INTO tappa_analisi (
                tappa_id, gpx_sha256, versione_algoritmi, stato, aggiornato_il
            )
            VALUES (?, ?, ?, 'IN_CODA', ?)
            ON CONFLICT(tappa_id) DO UPDATE SET
                gpx_sha256 = excluded.gpx_sha256,
                versione_algoritmi = excluded.versione_algoritmi,
                stato = 'IN_CODA',
                errore = NULL,
                aggiornato_il = excluded.aggiornato_il
            """,
            (tappa_id, gpx_sha256, VERSIONE_ALGORITMI, _ora_utc()),
        )
        connessione.execute(
            """
            UPDATE tappa_analisi
            SET stato = 'IN_CORSO', aggiornato_il = ?
            WHERE tappa_id = ?
            """,
            (_ora_utc(), tappa_id),
        )

        try:
            risultato = analizza_gpx(percorso_file)
            if risultato["stato"] == "ERRORE":
                _salva_errore(
                    connessione,
                    tappa_id,
                    gpx_sha256,
                    risultato["errore"] or "errore sconosciuto nell'analisi GPX",
                )
                return risultato

            anomalie = risultato.get("anomalie", [])
            stato = "PARZIALE" if _anomalie_bloccanti(anomalie) else "COMPLETO"
            risultato["stato"] = stato
            bbox = risultato["bbox"] or {}
            connessione.execute(
                """
                UPDATE tappa_analisi
                SET distanza_km = ?, dislivello_pos_m = ?, dislivello_neg_m = ?,
                    quota_min_m = ?, quota_max_m = ?, pendenza_media_pct = ?,
                    pendenza_max_pct = ?, bbox_min_lon = ?, bbox_min_lat = ?,
                    bbox_max_lon = ?, bbox_max_lat = ?, stato = ?, errore = NULL,
                    aggiornato_il = ?
                WHERE tappa_id = ?
                """,
                (
                    risultato["distanza_km"],
                    risultato["dislivello_pos_m"],
                    risultato["dislivello_neg_m"],
                    risultato["quota_min_m"],
                    risultato["quota_max_m"],
                    risultato["pendenza_media_pct"],
                    risultato["pendenza_max_pct"],
                    bbox.get("min_lon"),
                    bbox.get("min_lat"),
                    bbox.get("max_lon"),
                    bbox.get("max_lat"),
                    stato,
                    _ora_utc(),
                    tappa_id,
                ),
            )
            connessione.execute(
                "DELETE FROM tappa_segmenti WHERE tappa_id = ?", (tappa_id,)
            )
            for segmento in risultato["segmenti"]:
                connessione.execute(
                    """
                    INSERT INTO tappa_segmenti (
                        tappa_id, track_index, segment_index, punti, distanza_km,
                        dislivello_pos_m, dislivello_neg_m, quota_min_m,
                        quota_max_m, versione_algoritmi
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        tappa_id,
                        segmento["track_index"],
                        segmento["segment_index"],
                        segmento["punti"],
                        segmento["distanza_km"],
                        segmento["dislivello_pos_m"],
                        segmento["dislivello_neg_m"],
                        segmento["quota_min_m"],
                        segmento["quota_max_m"],
                        VERSIONE_ALGORITMI,
                    ),
                )
            connessione.execute(
                "UPDATE tappe SET distanza_km = ? WHERE id = ?",
                (risultato["distanza_km"], tappa_id),
            )
            _salva_geometria(
                connessione, tappa_id, percorso_file, gpx_sha256
            )
            errore_costa = _salva_costa_se_necessario(
                connessione, tappa_id, percorso_file, gpx_sha256
            )
            risultato["costa_errore"] = errore_costa
            return risultato
        except Exception as exc:
            _salva_errore(connessione, tappa_id, gpx_sha256, str(exc))
            return {
                "stato": "ERRORE",
                "errore": str(exc),
                "anomalie": [],
            }
