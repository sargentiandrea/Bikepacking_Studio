"""Calcolo locale della proiezione temporale dei blocchi di un progetto."""

from __future__ import annotations

import sqlite3
from collections import Counter, defaultdict
from contextlib import closing
from datetime import date, datetime, timedelta
from functools import lru_cache
import json
import math
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

    return _calcola_da_blocchi(
        blocchi, data_iniziale, modificatore_riposo, ordine_proposto
    )


SOGLIE_CLIMA_DEFAULT = {
    "temperatura_rossa_bassa": 5.0,
    "temperatura_verde_min": 15.0,
    "temperatura_verde_max": 28.0,
    "temperatura_rossa_alta": 35.0,
    "pioggia_verde_max": 50.0,
    "pioggia_gialla_max": 100.0,
    "vento_verde_max": 20.0,
    "vento_giallo_max": 35.0,
}


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
        righe = connessione.execute(
            """
            SELECT *
            FROM clima_paese_mese
            WHERE id_progetto = ?
            """,
            (progetto_id,),
        ).fetchall()
    return {
        (str(riga["paese"]).upper(), int(riga["mese"])): riga
        for riga in righe
    }


def _valuta_temperatura(
    valore: float, soglie: dict[str, float]
) -> tuple[int, str]:
    if soglie["temperatura_verde_min"] <= valore <= soglie["temperatura_verde_max"]:
        return 0, "verde"
    if (
        soglie["temperatura_rossa_bassa"]
        <= valore
        < soglie["temperatura_verde_min"]
        or soglie["temperatura_verde_max"]
        < valore
        <= soglie["temperatura_rossa_alta"]
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


def applica_semafori(
    progetto_id: int,
    risultati: list[dict[str, object]],
    soglie: dict[str, float] | None = None,
) -> list[dict[str, object]]:
    """Aggiunge alla catena gli indicatori del transito e le relative motivazioni."""
    soglie_attive = dict(SOGLIE_CLIMA_DEFAULT)
    if soglie:
        soglie_attive.update(soglie)
    if (
        soglie_attive["temperatura_rossa_bassa"]
        >= soglie_attive["temperatura_verde_min"]
        or soglie_attive["temperatura_verde_min"]
        >= soglie_attive["temperatura_verde_max"]
        or soglie_attive["temperatura_verde_max"]
        >= soglie_attive["temperatura_rossa_alta"]
        or soglie_attive["pioggia_verde_max"]
        >= soglie_attive["pioggia_gialla_max"]
        or soglie_attive["vento_verde_max"]
        >= soglie_attive["vento_giallo_max"]
    ):
        raise ValueError("Le soglie climatiche devono essere crescenti.")

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
        valori_fattori = [
            medie["temperatura_media"],
            medie["precipitazioni_mm"],
            medie["vento_media"],
        ]
        note_fattori: list[str] = []
        severita: list[int] = []
        copertura_temporale = [
            giorni_coperti / giorni_totali
            for _, giorni_coperti in valori_fattori
        ]
        for nome, (valore, _) in zip(
            ("Temperatura media", "Pioggia", "Vento"), valori_fattori
        ):
            if valore is None:
                note_fattori.append(f"{nome}: dato non disponibile")
                continue
            if nome == "Temperatura media":
                livello, colore = _valuta_temperatura(valore, soglie_attive)
                note_fattori.append(
                    f"Temperatura {valore:.1f} °C: {colore}"
                )
            elif nome == "Pioggia":
                livello, colore = _valuta_sopra_soglia(
                    valore,
                    soglie_attive["pioggia_verde_max"],
                    soglie_attive["pioggia_gialla_max"],
                )
                note_fattori.append(
                    f"Pioggia {valore:.1f} mm/mese: {colore}"
                )
            else:
                livello, colore = _valuta_sopra_soglia(
                    valore,
                    soglie_attive["vento_verde_max"],
                    soglie_attive["vento_giallo_max"],
                )
                note_fattori.append(f"Vento {valore:.1f} km/h: {colore}")
            severita.append(livello)

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
            len(severita) == 3
            and copertura >= 99.9
            and all(giorni == giorni_totali for _, giorni in valori_fattori)
        )

        if not severita:
            semaforo = "N/D"
        elif not completo:
            semaforo = "Parziale"
        else:
            semaforo = ("verde", "giallo", "rosso")[max(severita)]

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
