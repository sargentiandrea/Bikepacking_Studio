"""Calcolo locale della proiezione temporale dei blocchi di un progetto."""

from __future__ import annotations

import sqlite3
from collections import Counter, defaultdict
from contextlib import closing
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
import json
import math
from pathlib import Path
from urllib.parse import quote

from service.config import DB_NAME
from service.migrazione_catena_stagionale import (
    assicura_schema_catena_stagionale,
)


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
        colonna_paese = "t.paese" if "paese" in colonne_tappe else "NULL"
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
                {colonna_paese} AS codice_paese,
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
        if "paese" not in colonne_tappe:
            avvisi.append(
                "Manca tappe.paese: le sotto-righe non possono essere "
                "associate a un paese."
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


@lru_cache(maxsize=1)
def _nomi_paesi_iso3() -> dict[str, str]:
    percorso_sprite = (
        Path(__file__).resolve().parents[1] / "resources" / "sprite.json"
    )
    with percorso_sprite.open(encoding="utf-8") as file_sprite:
        sprite = json.load(file_sprite)
    return {
        str(voce.get("iso_alpha3", "")).upper(): str(voce.get("name_it", ""))
        for voce in sprite.values()
        if isinstance(voce, dict)
        and voce.get("iso_alpha3") not in (None, "", "UNKNOWN")
        and voce.get("name_it")
    }


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
    nomi_paesi = _nomi_paesi_iso3()
    blocchi_per_nome = {
        str(blocco["nome_blocco"]): blocco for blocco in blocchi
    }
    risultati: list[dict[str, object]] = []
    data_corrente = data_partenza

    for posizione, nome_blocco in enumerate(ordine_blocchi, start=1):
        blocco = blocchi_per_nome[nome_blocco]
        tappe = blocco["tappe"]
        numero_tappe = len(tappe)
        giorni_riposo = max(
            0, (numero_tappe // 5) + modificatore_riposo
        )
        giorni_pedalata = numero_tappe
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
        gruppi_paese: list[dict[str, object]] = []
        for indice_tappa, tappa in enumerate(tappe, start=1):
            codice = tappa["codice_paese"]
            codice_paese = (
                str(codice).strip().upper()
                if codice is not None and str(codice).strip()
                else None
            )
            if (
                not gruppi_paese
                or gruppi_paese[-1]["codice_paese"] != codice_paese
            ):
                gruppi_paese.append(
                    {
                        "codice_paese": codice_paese,
                        "tappe": [],
                        "giorni_riposo": 0,
                        "km_totali": 0.0,
                    }
                )
            gruppo = gruppi_paese[-1]
            gruppo["tappe"].append(tappa)
            gruppo["km_totali"] += float(tappa["distanza_km"] or 0.0)
            if (
                indice_tappa % 5 == 0
                and indice_tappa // 5 <= giorni_riposo
            ):
                gruppo["giorni_riposo"] += 1

        # Il riposo segue il paese della quinta tappa; gli aggiustamenti vanno all'ultimo.
        riposi_calendario = numero_tappe // 5
        riposi_aggiuntivi = max(0, giorni_riposo - riposi_calendario)
        riposi_rimossi = max(0, riposi_calendario - giorni_riposo)
        if gruppi_paese and riposi_aggiuntivi:
            gruppi_paese[-1]["giorni_riposo"] += riposi_aggiuntivi
        if riposi_rimossi and gruppi_paese:
            for gruppo in reversed(gruppi_paese):
                rimovibili = min(
                    int(gruppo["giorni_riposo"]), riposi_rimossi
                )
                gruppo["giorni_riposo"] -= rimovibili
                riposi_rimossi -= rimovibili
                if not riposi_rimossi:
                    break

        paesi: list[dict[str, object]] = []
        data_paese = data_corrente
        for indice_paese, gruppo in enumerate(gruppi_paese, start=1):
            tappe_paese = gruppo["tappe"]
            tappe_paese_numero = len(tappe_paese)
            pedalata_paese = tappe_paese_numero
            riposo_paese = int(gruppo["giorni_riposo"])
            buffer_paese = (
                giorni_extra if indice_paese == len(gruppi_paese) else 0
            )
            totale_paese = pedalata_paese + riposo_paese + buffer_paese
            fine_paese = (
                data_paese + timedelta(days=totale_paese - 1)
                if totale_paese
                else data_paese
            )
            codice_paese = gruppo["codice_paese"]
            paese = {
                "ordine": posizione,
                "nome_blocco": nome_blocco,
                "codice_paese": codice_paese,
                "nome_paese": nomi_paesi.get(
                    str(codice_paese), "Paese non assegnato"
                ),
                "visita_paese": indice_paese,
                "numero_tappe": tappe_paese_numero,
                "km_totali": float(gruppo["km_totali"]),
                "giorni_pedalata": pedalata_paese,
                "giorni_riposo": riposo_paese,
                "giorni_extra": buffer_paese,
                "giorni_totali": totale_paese,
                "data_ingresso": data_paese.isoformat(),
                "data_uscita": fine_paese.isoformat(),
                "avviso": (
                    "Paese non assegnato in tappe.paese."
                    if codice_paese is None
                    else ""
                ),
            }
            paesi.append(paese)
            data_paese = fine_paese + timedelta(days=1)

        giorni_totali = giorni_base + giorni_extra
        data_uscita = (
            data_paese - timedelta(days=1)
            if paesi
            else data_corrente + timedelta(days=max(0, giorni_totali - 1))
        )
        km_totali = sum(float(tappa["distanza_km"] or 0.0) for tappa in tappe)
        avviso_blocco = str(blocco["avviso"])
        if any(paese["avviso"] for paese in paesi):
            avviso_blocco = " ".join(
                parte
                for parte in (
                    avviso_blocco,
                    "Una o più tappe non hanno un paese assegnato.",
                )
                if parte
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
                "paesi": paesi,
                "avviso": avviso_blocco,
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

    risultati = _calcola_da_blocchi(
        blocchi, data_iniziale, modificatore_riposo, ordine_proposto
    )
    _salva_scenario_proposto(progetto_id, ordine_proposto)
    return risultati


def _salva_scenario_proposto(
    progetto_id: int, ordine_proposto: list[str]
) -> int:
    assicura_schema_catena_stagionale(DB_NAME)
    creato_il = datetime.now(timezone.utc).isoformat()
    ordine_json = json.dumps(ordine_proposto, ensure_ascii=False)
    nome = f"Scenario catena {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    with closing(sqlite3.connect(DB_NAME, timeout=15.0)) as connessione:
        connessione.execute("BEGIN IMMEDIATE")
        riga = connessione.execute(
            """
            SELECT id FROM scenari
            WHERE id_progetto = ? AND applicato = 0 AND annullato = 0
            ORDER BY id DESC LIMIT 1
            """,
            (progetto_id,),
        ).fetchone()
        if riga:
            scenario_id = int(riga[0])
            connessione.execute(
                """
                UPDATE scenari
                SET nome = ?, ordine_json = ?, creato_il = ?
                WHERE id = ?
                """,
                (nome, ordine_json, creato_il, scenario_id),
            )
        else:
            cursore = connessione.execute(
                """
                INSERT INTO scenari (
                    id_progetto, nome, ordine_json, creato_il
                ) VALUES (?, ?, ?, ?)
                """,
                (progetto_id, nome, ordine_json, creato_il),
            )
            scenario_id = int(cursore.lastrowid)
        connessione.commit()
    return scenario_id


def ottieni_scenario_in_sospeso(progetto_id: int) -> dict[str, object] | None:
    """Restituisce l'ultima bozza ancora non applicata del progetto."""
    with closing(_connetti_sola_lettura()) as connessione:
        presente = connessione.execute(
            """
            SELECT 1 FROM sqlite_master
            WHERE type = 'table' AND name = 'scenari'
            """
        ).fetchone()
        if presente is None:
            return None
        riga = connessione.execute(
            """
            SELECT id, nome, ordine_json, creato_il
            FROM scenari
            WHERE id_progetto = ? AND applicato = 0 AND annullato = 0
            ORDER BY id DESC LIMIT 1
            """,
            (progetto_id,),
        ).fetchone()
    if riga is None:
        return None
    ordine = json.loads(riga["ordine_json"])
    if not isinstance(ordine, list) or not all(
        isinstance(nome_blocco, str) for nome_blocco in ordine
    ):
        raise RuntimeError("L'ordine salvato nello scenario non è valido.")
    return {
        "id": int(riga["id"]),
        "nome": str(riga["nome"]),
        "ordine": ordine,
        "creato_il": str(riga["creato_il"]),
    }


def scarta_scenario_in_sospeso(progetto_id: int) -> None:
    """Segna come annullata la bozza corrente senza toccare l'ordine ufficiale."""
    with closing(sqlite3.connect(DB_NAME, timeout=15.0)) as connessione:
        presente = connessione.execute(
            """
            SELECT 1 FROM sqlite_master
            WHERE type = 'table' AND name = 'scenari'
            """
        ).fetchone()
        if presente is None:
            return
        connessione.execute(
            """
            UPDATE scenari SET annullato = 1
            WHERE id = (
                SELECT id FROM scenari
                WHERE id_progetto = ? AND applicato = 0 AND annullato = 0
                ORDER BY id DESC LIMIT 1
            )
            """,
            (progetto_id,),
        )
        connessione.commit()


def ottieni_ultima_applicazione_scenario(
    progetto_id: int,
) -> int | None:
    """Restituisce l'applicazione più recente ancora annullabile."""
    with closing(_connetti_sola_lettura()) as connessione:
        presente = connessione.execute(
            """
            SELECT 1 FROM sqlite_master
            WHERE type = 'table' AND name = 'scenari'
            """
        ).fetchone()
        if presente is None:
            return None
        riga = connessione.execute(
            """
            SELECT id FROM scenari
            WHERE id_progetto = ? AND applicato = 1 AND annullato = 0
            ORDER BY id DESC LIMIT 1
            """,
            (progetto_id,),
        ).fetchone()
    return int(riga["id"]) if riga else None


def _ordine_ufficiale(
    connessione: sqlite3.Connection, progetto_id: int
) -> list[dict[str, object]]:
    righe = connessione.execute(
        """
        SELECT id, nome_blocco, ordine
        FROM blocchi_ordine
        WHERE id_progetto = ?
        ORDER BY
            CASE WHEN ordine IS NULL THEN 1 ELSE 0 END,
            ordine,
            id
        """,
        (progetto_id,),
    ).fetchall()
    return [
        {
            "id": int(riga[0]),
            "nome_blocco": str(riga[1]),
            "ordine": riga[2],
        }
        for riga in righe
    ]


def _verifica_ordine_scenario(
    connessione: sqlite3.Connection,
    progetto_id: int,
    ordine: list[object],
) -> list[str]:
    if not all(isinstance(nome, str) and nome for nome in ordine):
        raise ValueError("Lo scenario contiene nomi di blocco non validi.")
    ordine_blocchi = [str(nome) for nome in ordine]
    if len(ordine_blocchi) != len(set(ordine_blocchi)):
        raise ValueError("Ogni blocco deve comparire una sola volta nello scenario.")
    attivi = connessione.execute(
        """
        SELECT DISTINCT COALESCE(NULLIF(TRIM(blocco), ''), 'Generale')
        FROM tappe
        WHERE id_progetto = ? AND (stato = 'ATTIVA' OR stato IS NULL)
        """,
        (progetto_id,),
    ).fetchall()
    nomi_attivi = {str(riga[0]) for riga in attivi}
    righe_ordine = _ordine_ufficiale(connessione, progetto_id)
    nomi_attesi = {str(riga["nome_blocco"]) for riga in righe_ordine} | nomi_attivi
    if Counter(ordine_blocchi) != Counter(nomi_attesi):
        raise ValueError(
            "Lo scenario non corrisponde più ai blocchi attivi del progetto. "
            "Ricalcola la catena prima di confermarlo."
        )
    return ordine_blocchi


def conferma_scenario(scenario_id: int) -> dict[str, object]:
    """Applica atomically lo scenario ai blocchi e conserva il precedente ordine."""
    assicura_schema_catena_stagionale(DB_NAME)
    with closing(sqlite3.connect(DB_NAME, timeout=15.0)) as connessione:
        connessione.execute("PRAGMA foreign_keys = ON")
        connessione.execute("BEGIN IMMEDIATE")
        try:
            scenario = connessione.execute(
                """
                SELECT id_progetto, nome, ordine_json, applicato, annullato
                FROM scenari WHERE id = ?
                """,
                (scenario_id,),
            ).fetchone()
            if scenario is None:
                raise ValueError("Lo scenario non esiste più.")
            if scenario[3] or scenario[4]:
                raise ValueError("Questo scenario è già stato applicato o annullato.")

            progetto_id = int(scenario[0])
            ordine_scenario = json.loads(scenario[2])
            if not isinstance(ordine_scenario, list):
                raise ValueError("L'ordine salvato nello scenario non è valido.")
            ordine_scenario = _verifica_ordine_scenario(
                connessione, progetto_id, ordine_scenario
            )
            ordine_precedente = _ordine_ufficiale(connessione, progetto_id)
            snapshot_precedente = json.dumps(
                ordine_precedente, ensure_ascii=False
            )

            connessione.execute(
                "DELETE FROM blocchi_ordine WHERE id_progetto = ?",
                (progetto_id,),
            )
            connessione.executemany(
                """
                INSERT INTO blocchi_ordine (id_progetto, nome_blocco, ordine)
                VALUES (?, ?, ?)
                """,
                [
                    (progetto_id, nome_blocco, posizione)
                    for posizione, nome_blocco in enumerate(
                        ordine_scenario, start=1
                    )
                ],
            )
            connessione.execute(
                """
                UPDATE scenari
                SET applicato = 1, ordine_precedente_json = ?
                WHERE id = ?
                """,
                (snapshot_precedente, scenario_id),
            )
            connessione.commit()
        except Exception:
            connessione.rollback()
            raise
    return {
        "scenario_id": scenario_id,
        "id_progetto": progetto_id,
        "ordine": ordine_scenario,
        "ordine_precedente": [
            str(riga["nome_blocco"]) for riga in ordine_precedente
        ],
    }


def annulla_scenario(scenario_id: int) -> dict[str, object]:
    """Ripristina in modo atomico l'ordine registrato prima dell'applicazione."""
    assicura_schema_catena_stagionale(DB_NAME)
    with closing(sqlite3.connect(DB_NAME, timeout=15.0)) as connessione:
        connessione.execute("PRAGMA foreign_keys = ON")
        connessione.execute("BEGIN IMMEDIATE")
        try:
            scenario = connessione.execute(
                """
                SELECT id_progetto, ordine_json, ordine_precedente_json,
                       applicato, annullato
                FROM scenari WHERE id = ?
                """,
                (scenario_id,),
            ).fetchone()
            if scenario is None:
                raise ValueError("Lo scenario non esiste più.")
            if not scenario[3] or scenario[4]:
                raise ValueError("Lo scenario non è un'applicazione annullabile.")
            if not scenario[2]:
                raise RuntimeError("Non è disponibile l'ordine precedente dello scenario.")

            progetto_id = int(scenario[0])
            ordine_applicato = json.loads(scenario[1])
            ordine_precedente = json.loads(scenario[2])
            ordine_corrente = _ordine_ufficiale(connessione, progetto_id)
            nomi_correnti = [str(riga["nome_blocco"]) for riga in ordine_corrente]
            if nomi_correnti != ordine_applicato:
                raise RuntimeError(
                    "L'ordine ufficiale è cambiato dopo l'applicazione: "
                    "il ripristino automatico è stato interrotto per non "
                    "sovrascrivere modifiche successive."
                )
            if not isinstance(ordine_precedente, list) or not all(
                isinstance(riga, dict)
                and {"id", "nome_blocco", "ordine"} <= riga.keys()
                for riga in ordine_precedente
            ):
                raise RuntimeError("La copia dell'ordine precedente non è valida.")

            connessione.execute(
                "DELETE FROM blocchi_ordine WHERE id_progetto = ?",
                (progetto_id,),
            )
            connessione.executemany(
                """
                INSERT INTO blocchi_ordine (id, id_progetto, nome_blocco, ordine)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (
                        int(riga["id"]),
                        progetto_id,
                        str(riga["nome_blocco"]),
                        riga["ordine"],
                    )
                    for riga in ordine_precedente
                ],
            )
            connessione.execute(
                "UPDATE scenari SET annullato = 1 WHERE id = ?",
                (scenario_id,),
            )
            connessione.commit()
        except Exception:
            connessione.rollback()
            raise
    return {
        "scenario_id": scenario_id,
        "id_progetto": progetto_id,
        "ordine": [
            str(riga["nome_blocco"]) for riga in ordine_precedente
        ],
    }


SOGLIE_CLIMA_DEFAULT = {
    "temp_min_verde": 15.0,
    "temp_max_verde": 28.0,
    "temp_min_giallo": 5.0,
    "temp_max_giallo": 35.0,
    "pioggia_max_verde": 50.0,
    "pioggia_max_giallo": 100.0,
    "vento_max_verde": 20.0,
    "vento_max_giallo": 35.0,
    "priorita_caldo": 1,
}


def _normalizza_soglie(
    soglie: dict[str, float | int] | None,
) -> dict[str, float | int]:
    """Unifica le vecchie chiavi UI e convalida l'insieme delle soglie."""
    normalizzate: dict[str, float | int] = dict(SOGLIE_CLIMA_DEFAULT)
    if soglie:
        alias_legacy = {
            "temperatura_verde_min": "temp_min_verde",
            "temperatura_verde_max": "temp_max_verde",
            "temperatura_rossa_bassa": "temp_min_giallo",
            "temperatura_rossa_alta": "temp_max_giallo",
            "pioggia_verde_max": "pioggia_max_verde",
            "pioggia_gialla_max": "pioggia_max_giallo",
            "vento_verde_max": "vento_max_verde",
            "vento_giallo_max": "vento_max_giallo",
        }
        for chiave, valore in soglie.items():
            normalizzate[alias_legacy.get(chiave, chiave)] = valore

    for chiave in SOGLIE_CLIMA_DEFAULT:
        if chiave != "priorita_caldo":
            valore = float(normalizzate[chiave])
            if not math.isfinite(valore):
                raise ValueError(f"La soglia '{chiave}' deve essere un numero finito.")
            normalizzate[chiave] = valore

    priorita_raw = normalizzate["priorita_caldo"]
    if priorita_raw not in (0, 1, 0.0, 1.0):
        raise ValueError("priorita_caldo deve valere 0 (pioggia) oppure 1 (caldo).")
    priorita = int(priorita_raw)
    normalizzate["priorita_caldo"] = priorita

    if not (
        float(normalizzate["temp_min_giallo"])
        < float(normalizzate["temp_min_verde"])
        < float(normalizzate["temp_max_verde"])
        < float(normalizzate["temp_max_giallo"])
        and float(normalizzate["pioggia_max_verde"])
        < float(normalizzate["pioggia_max_giallo"])
        and float(normalizzate["vento_max_verde"])
        < float(normalizzate["vento_max_giallo"])
    ):
        raise ValueError("Le soglie climatiche devono essere in ordine crescente.")
    return normalizzate


def carica_impostazioni_semaforo(
    progetto_id: int,
) -> dict[str, float | int]:
    """Legge le preferenze del progetto, oppure restituisce i valori predefiniti."""
    risultato: dict[str, float | int] = dict(SOGLIE_CLIMA_DEFAULT)
    with closing(_connetti_sola_lettura()) as connessione:
        presente = connessione.execute(
            """
            SELECT 1 FROM sqlite_master
            WHERE type = 'table' AND name = 'impostazioni_semaforo'
            """
        ).fetchone()
        if presente is None:
            return risultato
        riga = connessione.execute(
            """
            SELECT temp_min_verde, temp_max_verde, temp_min_giallo,
                   temp_max_giallo, pioggia_max_verde, pioggia_max_giallo,
                   vento_max_verde, vento_max_giallo, priorita_caldo
            FROM impostazioni_semaforo
            WHERE id_progetto = ?
            """,
            (progetto_id,),
        ).fetchone()
    if riga is None:
        return risultato
    risultato.update(
        {
            nome: riga[indice]
            for indice, nome in enumerate(SOGLIE_CLIMA_DEFAULT)
        }
    )
    return _normalizza_soglie(risultato)


def salva_impostazioni_semaforo(
    progetto_id: int, soglie: dict[str, float | int]
) -> dict[str, float | int]:
    """Convalida e salva nel database le soglie climatiche del progetto."""
    valori = _normalizza_soglie(soglie)
    assicura_schema_catena_stagionale(DB_NAME)
    aggiornato_il = datetime.now(timezone.utc).isoformat()
    with closing(sqlite3.connect(DB_NAME, timeout=15.0)) as connessione:
        connessione.execute(
            """
            INSERT INTO impostazioni_semaforo (
                id_progetto, temp_min_verde, temp_max_verde,
                temp_min_giallo, temp_max_giallo, pioggia_max_verde,
                pioggia_max_giallo, vento_max_verde, vento_max_giallo,
                priorita_caldo, aggiornato_il
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id_progetto) DO UPDATE SET
                temp_min_verde = excluded.temp_min_verde,
                temp_max_verde = excluded.temp_max_verde,
                temp_min_giallo = excluded.temp_min_giallo,
                temp_max_giallo = excluded.temp_max_giallo,
                pioggia_max_verde = excluded.pioggia_max_verde,
                pioggia_max_giallo = excluded.pioggia_max_giallo,
                vento_max_verde = excluded.vento_max_verde,
                vento_max_giallo = excluded.vento_max_giallo,
                priorita_caldo = excluded.priorita_caldo,
                aggiornato_il = excluded.aggiornato_il
            """,
            (
                progetto_id,
                valori["temp_min_verde"],
                valori["temp_max_verde"],
                valori["temp_min_giallo"],
                valori["temp_max_giallo"],
                valori["pioggia_max_verde"],
                valori["pioggia_max_giallo"],
                valori["vento_max_verde"],
                valori["vento_max_giallo"],
                valori["priorita_caldo"],
                aggiornato_il,
            ),
        )
        connessione.commit()
    return valori


def _carica_clima_progetto(
    progetto_id: int,
) -> dict[tuple[str, int], sqlite3.Row]:
    with closing(_connetti_sola_lettura()) as connessione:
        tabella = connessione.execute(
            """
            SELECT 1 FROM sqlite_master
            WHERE type = 'table' AND name = 'clima_paese_mese'
            """
        ).fetchone()
        if tabella is None:
            return {}

        colonne = _colonne_tabella(connessione, "clima_paese_mese")
        necessarie = {
            "id_progetto",
            "paese",
            "mese",
            "temperatura_media",
            "temperatura_max",
            "temperatura_min",
            "precipitazioni_mm",
            "vento_media",
            "dataset_versione",
            "aggiornato_il",
            "copertura_pct",
            "anni_coperti",
        }
        if not necessarie <= colonne:
            mancanti = ", ".join(sorted(necessarie - colonne))
            raise RuntimeError(
                f"La tabella clima_paese_mese non è aggiornata: mancano {mancanti}."
            )
        righe_mondiali = connessione.execute(
            """
            SELECT *
            FROM clima_paese_mese
            WHERE id_progetto = 0
            """,
        ).fetchall()
        righe_progetto = connessione.execute(
            """
            SELECT *
            FROM clima_paese_mese
            WHERE id_progetto = ?
            """,
            (progetto_id,),
        ).fetchall()

    # Il livello base mondiale copre ogni paese, il progetto fa da override.
    profilo: dict[tuple[str, int], sqlite3.Row] = {}
    for riga in righe_mondiali:
        profilo[(str(riga["paese"]).upper(), int(riga["mese"]))] = riga
    for riga in righe_progetto:
        profilo[(str(riga["paese"]).upper(), int(riga["mese"]))] = riga
    return profilo


def _valuta_temperatura(
    valore: float, soglie: dict[str, float | int]
) -> tuple[int, str]:
    if float(soglie["temp_min_verde"]) <= valore <= float(soglie["temp_max_verde"]):
        return 0, "verde"
    if (
        float(soglie["temp_min_giallo"])
        <= valore
        < float(soglie["temp_min_verde"])
        or float(soglie["temp_max_verde"])
        < valore
        <= float(soglie["temp_max_giallo"])
    ):
        return 1, "giallo"
    return 2, "rosso"


def _valuta_sopra_soglia(
    valore: float, soglia_verde: float, soglia_rossa: float
) -> tuple[int, str]:
    if valore < soglia_verde:
        return 0, "verde"
    if valore <= soglia_rossa:
        return 1, "giallo"
    return 2, "rosso"


def _media_pesata(
    righe: list[tuple[sqlite3.Row, int]], nome_colonna: str
) -> tuple[float | None, int]:
    somma = 0.0
    giorni_coperti = 0
    for riga, giorni in righe:
        valore = riga[nome_colonna]
        if valore is None or not math.isfinite(float(valore)):
            continue
        somma += float(valore) * giorni
        giorni_coperti += giorni
    if not giorni_coperti:
        return None, 0
    return somma / giorni_coperti, giorni_coperti


def _mesi_del_transito(
    data_ingresso: date, data_uscita: date
) -> list[tuple[int, int]]:
    """Restituisce mese e giorni del blocco ricadenti in quel mese."""
    risultato: list[tuple[int, int]] = []
    mese_corrente = date(data_ingresso.year, data_ingresso.month, 1)
    while mese_corrente <= data_uscita:
        if mese_corrente.month == 12:
            inizio_mese_successivo = date(mese_corrente.year + 1, 1, 1)
        else:
            inizio_mese_successivo = date(
                mese_corrente.year, mese_corrente.month + 1, 1
            )
        fine_mese = inizio_mese_successivo - timedelta(days=1)
        inizio_intersezione = max(data_ingresso, mese_corrente)
        fine_intersezione = min(data_uscita, fine_mese)
        giorni = (fine_intersezione - inizio_intersezione).days + 1
        if giorni > 0:
            risultato.append((mese_corrente.month, giorni))
        mese_corrente = inizio_mese_successivo
    return risultato


def calcola_semaforo(
    progetto_id: int,
    risultati: list[dict[str, object]],
    soglie: dict[str, float | int] | None = None,
) -> list[dict[str, object]]:
    """Applica le soglie climatiche salvate per il progetto."""
    soglie_attive = _normalizza_soglie(
        carica_impostazioni_semaforo(progetto_id) if soglie is None else soglie
    )

    profilo = _carica_clima_progetto(progetto_id)
    colori = {
        "verde": "#2e8b57",
        "giallo": "#d6a500",
        "rosso": "#c74634",
        "Parziale": "#777777",
        "N/D": "#555555",
    }

    def valuta_paese(risultato: dict[str, object]) -> dict[str, object]:
        riga = dict(risultato)
        codice_paese = str(riga.get("codice_paese") or "").upper()
        data_ingresso = date.fromisoformat(str(riga["data_ingresso"]))
        data_uscita = date.fromisoformat(str(riga["data_uscita"]))
        giorni_totali = max(1, (data_uscita - data_ingresso).days + 1)
        righe_mese = [
            (profilo[(codice_paese, mese)], giorni)
            for mese, giorni in _mesi_del_transito(data_ingresso, data_uscita)
            if (codice_paese, mese) in profilo
        ]

        medie = {
            "temperatura_media": _media_pesata(
                righe_mese, "temperatura_media"
            ),
            "temperatura_max": _media_pesata(
                righe_mese, "temperatura_max"
            ),
            "temperatura_min": _media_pesata(
                righe_mese, "temperatura_min"
            ),
            "precipitazioni_mm": _media_pesata(
                righe_mese, "precipitazioni_mm"
            ),
            "vento_media": _media_pesata(righe_mese, "vento_media"),
        }
        dati_fattori = {
            "Temperatura media": medie["temperatura_media"],
            "Pioggia": medie["precipitazioni_mm"],
            "Vento": medie["vento_media"],
        }
        priorita_caldo = int(soglie_attive["priorita_caldo"])
        nome_prioritario = "Temperatura media" if priorita_caldo else "Pioggia"
        nome_secondario = "Pioggia" if priorita_caldo else "Temperatura media"
        ordine_fattori = (
            [nome_prioritario, nome_secondario, "Vento"]
        )
        valori_fattori = list(dati_fattori.values())
        note_fattori: list[str] = []
        severita_per_fattore: dict[str, int] = {}
        copertura_temporale = [
            giorni_coperti / giorni_totali
            for _, giorni_coperti in valori_fattori
        ]
        for nome in ordine_fattori:
            valore, _ = dati_fattori[nome]
            if valore is None:
                note_fattori.append(f"{nome}: dato non disponibile")
                continue
            if nome == "Temperatura media":
                livello, colore = _valuta_temperatura(valore, soglie_attive)
                limiti = (
                    f"verde {float(soglie_attive['temp_min_verde']):g}-"
                    f"{float(soglie_attive['temp_max_verde']):g} °C, "
                    f"giallo {float(soglie_attive['temp_min_giallo']):g}-"
                    f"{float(soglie_attive['temp_max_giallo']):g} °C"
                )
                note_fattori.append(
                    f"Temperatura {valore:.1f} °C: {colore} ({limiti})"
                )
            elif nome == "Pioggia":
                livello, colore = _valuta_sopra_soglia(
                    valore,
                    float(soglie_attive["pioggia_max_verde"]),
                    float(soglie_attive["pioggia_max_giallo"]),
                )
                note_fattori.append(
                    f"Pioggia {valore:.1f} mm/mese: {colore} "
                    f"(verde <{float(soglie_attive['pioggia_max_verde']):g}, "
                    f"giallo fino a {float(soglie_attive['pioggia_max_giallo']):g})"
                )
            else:
                livello, colore = _valuta_sopra_soglia(
                    valore,
                    float(soglie_attive["vento_max_verde"]),
                    float(soglie_attive["vento_max_giallo"]),
                )
                note_fattori.append(
                    f"Vento {valore:.1f} km/h: {colore} "
                    f"(verde <{float(soglie_attive['vento_max_verde']):g}, "
                    f"giallo fino a {float(soglie_attive['vento_max_giallo']):g})"
                )
            severita_per_fattore[nome] = livello

        copertura_spaziale = min(
            (
                float(riga_mese["copertura_pct"] or 0.0)
                for riga_mese, _ in righe_mese
            ),
            default=0.0,
        )
        copertura_tempo = min(copertura_temporale, default=0.0) * 100
        copertura = min(copertura_spaziale, copertura_tempo)
        completo = (
            len(severita_per_fattore) == 3
            and copertura >= 99.9
            and all(giorni == giorni_totali for _, giorni in valori_fattori)
        )

        if not severita_per_fattore:
            semaforo = "N/D"
        elif not completo:
            semaforo = "Parziale"
        else:
            livello_prioritario = severita_per_fattore.get(nome_prioritario)
            livello_secondario = severita_per_fattore.get(nome_secondario)
            if (
                livello_prioritario is not None
                and livello_secondario is not None
                and livello_prioritario < livello_secondario
            ):
                # La preferenza può attenuare di un solo livello il fattore secondario.
                livello_secondario = max(0, livello_secondario - 1)
            livelli_non_prioritari = [
                livello
                for nome, livello in severita_per_fattore.items()
                if nome not in {nome_prioritario, nome_secondario}
            ]
            livello_combinato = max(
                [
                    *livelli_non_prioritari,
                    (
                        livello_prioritario
                        if livello_prioritario is not None
                        else 0
                    ),
                    livello_secondario
                    if livello_secondario is not None
                    else 0,
                ]
            )
            semaforo = ("verde", "giallo", "rosso")[livello_combinato]

        anni_per_fattore: dict[str, list[int]] = defaultdict(list)
        versioni: set[str] = set()
        for riga_mese, _ in righe_mese:
            versione = riga_mese["dataset_versione"]
            if versione:
                versioni.add(str(versione))
            try:
                anni = json.loads(riga_mese["anni_coperti"] or "{}")
            except (TypeError, json.JSONDecodeError):
                anni = {}
            for variabile in ("tas", "tasmax", "tasmin", "pr", "sfcWind"):
                conteggio_anni = len(anni.get(variabile, []))
                if conteggio_anni:
                    anni_per_fattore[variabile].append(conteggio_anni)

        estremi = ""
        temperatura_minima = medie["temperatura_min"][0]
        temperatura_massima = medie["temperatura_max"][0]
        if temperatura_minima is not None and temperatura_massima is not None:
            estremi = (
                f"; min/max medie {temperatura_minima:.1f}/"
                f"{temperatura_massima:.1f} °C"
            )
        anni_descrizione = (
            ", anni disponibili: "
            + ", ".join(
                (
                    f"{variabile} {min(anni)}-{max(anni)}"
                    if min(anni) != max(anni)
                    else f"{variabile} {anni[0]}"
                )
                for variabile, anni in sorted(anni_per_fattore.items())
                if anni
            )
            if anni_per_fattore
            else ""
        )
        fonte = next(iter(versioni), "")
        if fonte:
            fonte = f"Fonte: {fonte}. "
        spiegazione = (
            "; ".join(note_fattori)
            + (
                ". Preferenza: caldo prioritario; la pioggia può pesare un "
                "livello in meno quando la temperatura è migliore."
                if priorita_caldo
                else ". Preferenza: pioggia prioritaria; la temperatura può "
                "pesare un livello in meno quando la pioggia è migliore."
            )
            + estremi
            + f". Copertura complessiva: {copertura:.0f}%"
            + anni_descrizione
            + (f". {fonte}" if fonte else "")
        )
        riga.update(
            {
                "semaforo": semaforo,
                "semaforo_colore": colori[semaforo],
                "spiegazione_clima": spiegazione,
                "copertura_clima_pct": copertura,
            }
        )
        return riga

    valutati: list[dict[str, object]] = []
    gravita = {"verde": 1, "giallo": 2, "Parziale": 3, "rosso": 4, "N/D": 0}
    for risultato in risultati:
        blocco = dict(risultato)
        paesi = [
            valuta_paese(paese)
            for paese in risultato.get("paesi", [])
        ]
        blocco["paesi"] = paesi
        if paesi:
            peggiore = max(
                paesi,
                key=lambda paese: gravita.get(str(paese["semaforo"]), 0),
            )
            semaforo_blocco = str(peggiore["semaforo"])
            dati_mancanti = any(
                paese["semaforo"] == "N/D" for paese in paesi
            )
            if dati_mancanti and semaforo_blocco in {"verde", "giallo"}:
                semaforo_blocco = "Parziale"
            blocco["semaforo"] = semaforo_blocco
            blocco["semaforo_colore"] = colori[semaforo_blocco]
            blocco["spiegazione_clima"] = (
                f"Semaforo aggregato: peggiore tra i paesi del blocco, "
                f"{peggiore['codice_paese'] or peggiore['nome_paese']} "
                f"({peggiore['semaforo']})."
                + (
                    " Alcuni paesi non hanno dati climatici."
                    if dati_mancanti
                    else ""
                )
            )
            blocco["copertura_clima_pct"] = min(
                float(paese["copertura_clima_pct"]) for paese in paesi
            )
        else:
            blocco.update(
                {
                    "semaforo": "N/D",
                    "semaforo_colore": colori["N/D"],
                    "spiegazione_clima": (
                        "Il blocco non contiene tappe associate a paesi."
                    ),
                    "copertura_clima_pct": 0.0,
                }
            )
        valutati.append(blocco)
    return valutati


def applica_semafori(
    progetto_id: int,
    risultati: list[dict[str, object]],
    soglie: dict[str, float | int] | None = None,
) -> list[dict[str, object]]:
    """Mantiene compatibili i chiamanti precedenti al nome calcola_semaforo."""
    return calcola_semaforo(progetto_id, risultati, soglie)
