"""Persistenza delle metriche precalcolate di una tappa."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import sqlite3
from typing import Any

from service.gpx_metrics_service import analizza_gpx


VERSIONE_ALGORITMI = "gpx_metrics_v1"


def calcola_sha256(percorso_file: str) -> str:
    """Calcola l'hash del file GPX conservato sul disco."""
    digest = hashlib.sha256()
    with open(percorso_file, "rb") as file_gpx:
        for blocco in iter(lambda: file_gpx.read(1024 * 1024), b""):
            digest.update(blocco)
    return digest.hexdigest()


def _ora_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


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
                return {"stato": "COMPLETO", "saltato": True}

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
            return {"stato": "COMPLETO", "saltato": True}

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

            stato = "PARZIALE" if risultato["anomalie"] else "COMPLETO"
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
            return risultato
        except Exception as exc:
            _salva_errore(connessione, tappa_id, gpx_sha256, str(exc))
            return {
                "stato": "ERRORE",
                "errore": str(exc),
                "anomalie": [],
            }
