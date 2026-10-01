"""Calcolo locale della proiezione temporale dei blocchi di un progetto."""

from __future__ import annotations

import sqlite3
from collections import Counter
from contextlib import closing
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import quote

from service.config import DB_NAME


def _connetti_sola_lettura() -> sqlite3.Connection:
    percorso_db = Path(DB_NAME).resolve()
    uri_db = f"file:{quote(percorso_db.as_posix(), safe='/:')}?mode=ro"
    connessione = sqlite3.connect(uri_db, uri=True)
    connessione.row_factory = sqlite3.Row
    connessione.execute("PRAGMA query_only = ON")
    return connessione


def _colonne_tabella(
    connessione: sqlite3.Connection, nome_tabella: str
) -> set[str]:
    return {
        riga["name"]
        for riga in connessione.execute(f"PRAGMA table_info({nome_tabella})")
    }


def _carica_blocchi(progetto_id: int) -> list[dict[str, object]]:
    with closing(_connetti_sola_lettura()) as connessione:
        tabelle = {
            riga["name"]
            for riga in connessione.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        if "tappe" not in tabelle:
            raise RuntimeError("La tabella 'tappe' non esiste nel database.")

        colonne_tappe = _colonne_tabella(connessione, "tappe")
        colonne_obbligatorie = {"id", "id_progetto", "blocco"}
        colonne_mancanti = colonne_obbligatorie - colonne_tappe
        if colonne_mancanti:
            nomi = ", ".join(sorted(colonne_mancanti))
            raise RuntimeError(f"Mancano colonne obbligatorie in 'tappe': {nomi}.")

        colonna_sequenza = (
            "t.sequenza" if "sequenza" in colonne_tappe else "t.id"
        )
        colonna_stato = (
            "(t.stato = 'ATTIVA' OR t.stato IS NULL)"
            if "stato" in colonne_tappe
            else "1 = 1"
        )
        colonna_nome_blocco = (
            "COALESCE(NULLIF(TRIM(t.blocco), ''), 'Generale')"
        )
        colonna_distanza_tappa = (
            "t.distanza_km" if "distanza_km" in colonne_tappe else "NULL"
        )

        join_analisi = ""
        colonna_distanza = f"COALESCE({colonna_distanza_tappa}, 0.0)"
        if "tappa_analisi" in tabelle:
            colonne_analisi = _colonne_tabella(connessione, "tappa_analisi")
            if {"tappa_id", "distanza_km"} <= colonne_analisi:
                join_analisi = (
                    "LEFT JOIN tappa_analisi a ON a.tappa_id = t.id"
                )
                colonna_distanza = (
                    f"COALESCE(a.distanza_km, {colonna_distanza_tappa}, 0.0)"
                )

        righe_tappe = connessione.execute(
            f"""
            SELECT
                {colonna_nome_blocco} AS nome_blocco,
                t.id AS tappa_id,
                {colonna_sequenza} AS sequenza,
                {colonna_distanza} AS distanza_km
            FROM tappe t
            {join_analisi}
            WHERE t.id_progetto = ?
              AND {colonna_stato}
            ORDER BY
                nome_blocco,
                CASE WHEN {colonna_sequenza} IS NULL THEN 1 ELSE 0 END,
                {colonna_sequenza},
                t.id
            """,
            (progetto_id,),
        ).fetchall()

        ordine_salvato: dict[str, int] = {}
        if "blocchi_ordine" in tabelle:
            colonne_ordine = _colonne_tabella(connessione, "blocchi_ordine")
            if {
                "id",
                "id_progetto",
                "nome_blocco",
                "ordine",
            } <= colonne_ordine:
                righe_ordine = connessione.execute(
                    """
                    SELECT nome_blocco, ordine
                    FROM blocchi_ordine
                    WHERE id_progetto = ?
                    ORDER BY
                        CASE WHEN ordine IS NULL THEN 1 ELSE 0 END,
                        ordine,
                        id
                    """,
                    (progetto_id,),
                ).fetchall()
                for riga in righe_ordine:
                    nome = riga["nome_blocco"]
                    if nome is not None:
                        ordine_salvato.setdefault(
                            nome,
                            riga["ordine"]
                            if riga["ordine"] is not None
                            else 999,
                        )

    gruppi_tappe: dict[str, list[sqlite3.Row]] = {}
    for riga in righe_tappe:
        gruppi_tappe.setdefault(riga["nome_blocco"], []).append(riga)

    nomi_blocchi = set(ordine_salvato) | set(gruppi_tappe)
    blocchi: list[dict[str, object]] = []
    for nome in sorted(
        nomi_blocchi,
        key=lambda nome_blocco: (
            ordine_salvato.get(nome_blocco, 999),
            nome_blocco.casefold(),
        ),
    ):
        tappe = gruppi_tappe.get(nome, [])
        avvisi: list[str] = []
        if nome not in ordine_salvato:
            avvisi.append(
                "Blocco non presente in blocchi_ordine: usato ordine 999."
            )
        if not tappe:
            avvisi.append("Nessuna tappa attiva associata al blocco.")

        blocchi.append(
            {
                "nome_blocco": nome,
                "ordine": ordine_salvato.get(nome, 999),
                "tappe": tappe,
                "avviso": " ".join(avvisi),
            }
        )

    return blocchi


def _normalizza_data(data_partenza: date | datetime) -> date:
    if isinstance(data_partenza, datetime):
        return data_partenza.date()
    if isinstance(data_partenza, date):
        return data_partenza
    raise TypeError("data_partenza deve essere un datetime.date o datetime.datetime.")


def _calcola_da_blocchi(
    blocchi: list[dict[str, object]],
    data_partenza: date,
    modificatore_riposo: int,
    ordine_blocchi: list[str],
) -> list[dict[str, object]]:
    blocchi_per_nome = {
        str(blocco["nome_blocco"]): blocco for blocco in blocchi
    }
    risultati: list[dict[str, object]] = []
    data_corrente = data_partenza

    for posizione, nome_blocco in enumerate(ordine_blocchi, start=1):
        blocco = blocchi_per_nome[nome_blocco]
        tappe = blocco["tappe"]
        numero_tappe = len(tappe)
        km_totali = sum(
            (tappa["distanza_km"] or 0.0) for tappa in tappe
        )
        giorni_pedalata = numero_tappe
        giorni_riposo = max(
            0, (numero_tappe // 5) + modificatore_riposo
        )
        giorni_base = giorni_pedalata + giorni_riposo

        if giorni_base:
            data_fine_base = data_corrente + timedelta(days=giorni_base - 1)
            mesi_attraversati = (
                (data_fine_base.year - data_corrente.year) * 12
                + data_fine_base.month
                - data_corrente.month
                + 1
            )
            # I buffer si calcolano sulla sola durata base e non generano altri buffer.
            buffer_mesi = 5 * mesi_attraversati
            buffer_quadrimestri = 7 * (mesi_attraversati // 4)
        else:
            mesi_attraversati = 0
            buffer_mesi = 0
            buffer_quadrimestri = 0

        giorni_extra = buffer_mesi + buffer_quadrimestri
        giorni_totali = giorni_base + giorni_extra
        data_uscita = (
            data_corrente + timedelta(days=giorni_totali - 1)
            if giorni_totali
            else data_corrente
        )

        risultati.append(
            {
                "ordine": posizione,
                "nome_blocco": nome_blocco,
                "numero_tappe": numero_tappe,
                "km_totali": km_totali,
                "giorni_pedalata": giorni_pedalata,
                "giorni_riposo": giorni_riposo,
                "giorni_extra": giorni_extra,
                "giorni_buffer_mese": buffer_mesi,
                "giorni_buffer_quadrimestre": buffer_quadrimestri,
                "giorni_totali": giorni_totali,
                "data_ingresso": data_corrente.isoformat(),
                "data_uscita": data_uscita.isoformat(),
                "mesi_attraversati_base": mesi_attraversati,
                "avviso": blocco["avviso"],
            }
        )
        data_corrente = data_uscita + timedelta(days=1)

    return risultati


def calcola_catena(
    progetto_id: int,
    data_partenza: date | datetime,
    modificatore_riposo: int,
) -> list[dict[str, object]]:
    """Calcola la catena datata senza scrivere nel database."""
    data_iniziale = _normalizza_data(data_partenza)
    blocchi = _carica_blocchi(progetto_id)
    ordine = [str(blocco["nome_blocco"]) for blocco in blocchi]
    return _calcola_da_blocchi(
        blocchi, data_iniziale, modificatore_riposo, ordine
    )


def proponi_scenario(
    progetto_id: int,
    modifiche_ordine: list[str],
    data_partenza: date | datetime | None = None,
    modificatore_riposo: int = 0,
) -> list[dict[str, object]]:
    """Ricalcola uno scenario dato l'ordine completo proposto, senza salvarlo."""
    data_iniziale = _normalizza_data(data_partenza or date.today())
    blocchi = _carica_blocchi(progetto_id)
    ordine_originale = [str(blocco["nome_blocco"]) for blocco in blocchi]

    ordine_proposto = list(modifiche_ordine)
    if Counter(ordine_proposto) != Counter(ordine_originale):
        raise ValueError(
            "L'ordine proposto deve contenere ogni blocco esattamente una volta."
        )

    return _calcola_da_blocchi(
        blocchi, data_iniziale, modificatore_riposo, ordine_proposto
    )
