"""Estrazione locale dei dati CHELSA-monthly lungo le tappe attive."""

from __future__ import annotations

from collections import defaultdict
from contextlib import closing
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sqlite3
import time
from typing import Callable
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import urlopen
import xml.etree.ElementTree as ET

import numpy as np
import rasterio

from service.migrazione_clima import assicura_schema_clima


BASE_URL = "https://os.unil.cloud.switch.ch/chelsa02"
DATASET_PAGE = "https://www.chelsa-climate.org/datasets/chelsa_monthly"
VERSIONE_DATASET = "CHELSA-monthly V2.1"
VARIABILI = ("tas", "tasmax", "tasmin", "pr", "sfcWind")
ANNI_DEFAULT = tuple(range(2015, 2022))
NAMESPACE_S3 = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
TENTATIVI_LETTURA_RASTER = 3


def _lista_file_mensili(anni: tuple[int, ...]) -> dict[
    tuple[str, int, int], str
]:
    """Interroga il catalogo pubblico S3 e restituisce i GeoTIFF esistenti."""
    files: dict[tuple[str, int, int], str] = {}
    for variabile in VARIABILI:
        for anno in anni:
            prefisso = f"chelsa/global/monthly/{variabile}/{anno}/"
            url_catalogo = (
                f"{BASE_URL}?list-type=2&prefix={quote(prefisso, safe='/')}"
            )
            try:
                with urlopen(url_catalogo, timeout=45) as risposta:
                    catalogo = ET.fromstring(risposta.read())
            except (OSError, URLError, ET.ParseError) as errore:
                raise RuntimeError(
                    f"Impossibile leggere il catalogo CHELSA per "
                    f"{variabile} {anno}: {errore}"
                ) from errore

            for elemento in catalogo.findall("s3:Contents", NAMESPACE_S3):
                chiave = elemento.findtext("s3:Key", namespaces=NAMESPACE_S3)
                if not chiave or not chiave.lower().endswith(".tif"):
                    continue
                nome = Path(chiave).name.split("_")
                if len(nome) < 5 or nome[1] != variabile:
                    continue
                try:
                    mese = int(nome[2])
                except ValueError:
                    continue
                if 1 <= mese <= 12:
                    files[(variabile, anno, mese)] = (
                        f"{BASE_URL}/{quote(chiave, safe='/')}"
                    )
    return files


def _valore_fisico(
    valore_grezzo: float,
    variabile: str,
    scala: float,
    offset: float,
) -> float:
    valore = valore_grezzo * scala + offset
    if variabile in {"tas", "tasmax", "tasmin"}:
        return valore - 273.15
    if variabile == "sfcWind":
        return valore * 3.6
    return valore


def _prepara_tappe(
    db_name: str, progetto_id: int | None, limite_tappe: int | None
) -> tuple[list[dict[str, object]], dict[tuple[int, str], int]]:
    percorso_db = Path(db_name).resolve()
    if not percorso_db.is_file():
        raise FileNotFoundError(f"Database non trovato: {percorso_db}")
    uri_db = f"file:{quote(percorso_db.as_posix(), safe='/:')}?mode=ro"
    with closing(sqlite3.connect(uri_db, uri=True)) as connessione:
        connessione.row_factory = sqlite3.Row
        colonne = {
            riga["name"]
            for riga in connessione.execute("PRAGMA table_info(tappe)")
        }
        necessarie = {
            "id",
            "id_progetto",
            "paese",
            "start_lat",
            "start_lon",
        }
        if not necessarie <= colonne:
            mancanti = ", ".join(sorted(necessarie - colonne))
            raise RuntimeError(
                f"La tabella 'tappe' non contiene le colonne richieste: {mancanti}."
            )

        filtro_progetto = "AND id_progetto = ?" if progetto_id is not None else ""
        stato = (
            "AND (stato = 'ATTIVA' OR stato IS NULL)"
            if "stato" in colonne
            else ""
        )
        sequenza = "sequenza" if "sequenza" in colonne else "id"
        parametri = (progetto_id,) if progetto_id is not None else ()
        righe = connessione.execute(
            f"""
            SELECT id, id_progetto, paese, start_lat, start_lon
            FROM tappe
            WHERE 1 = 1 {stato} {filtro_progetto}
            ORDER BY id_progetto, {sequenza}, id
            """,
            parametri,
        ).fetchall()

    numero_tappe_per_paese: dict[tuple[int, str], int] = defaultdict(int)
    tappe: list[dict[str, object]] = []
    for riga in righe:
        valore_paese = riga["paese"]
        codice_paese = (
            str(valore_paese).strip().upper()
            if valore_paese is not None
            else ""
        )
        if len(codice_paese) != 3 or not codice_paese.isascii() or not codice_paese.isalpha():
            raise RuntimeError(
                f"La tappa {riga['id']} non ha un codice ISO3 valido in tappe.paese."
            )
        chiave_paese = (int(riga["id_progetto"]), codice_paese)
        numero_tappe_per_paese[chiave_paese] += 1
        latitudine = riga["start_lat"]
        longitudine = riga["start_lon"]
        if latitudine is None or longitudine is None:
            continue
        latitudine = float(latitudine)
        longitudine = float(longitudine)
        if (
            not math.isfinite(latitudine)
            or not math.isfinite(longitudine)
            or not -90 <= latitudine <= 90
            or not -180 <= longitudine <= 180
        ):
            continue
        tappe.append(
            {
                "id": int(riga["id"]),
                "id_progetto": chiave_paese[0],
                "paese": chiave_paese[1],
                "lat": latitudine,
                "lon": longitudine,
            }
        )

    if limite_tappe is not None:
        if limite_tappe <= 0:
            raise ValueError("limite_tappe deve essere maggiore di zero.")
        tappe = tappe[:limite_tappe]
        numero_tappe_per_paese = defaultdict(int)
        for tappa in tappe:
            chiave = (int(tappa["id_progetto"]), str(tappa["paese"]))
            numero_tappe_per_paese[chiave] += 1
    return tappe, dict(numero_tappe_per_paese)


def estrai_clima_per_tappe(
    db_name: str,
    progetto_id: int | None = None,
    anni: tuple[int, ...] = ANNI_DEFAULT,
    limite_tappe: int | None = None,
    progress_callback: Callable[[str], None] | None = None,
) -> dict[str, object]:
    """Campiona i COG CHELSA e salva riepiloghi mensili per paese in SQLite.

    I GeoTIFF globali sono letti via richieste COG a intervalli; non vengono
    scaricati integralmente, perché il periodo completo pesa decine di GB.
    """
    anni_validi = tuple(sorted(set(int(anno) for anno in anni)))
    if not anni_validi or any(anno < 1979 or anno > 2021 for anno in anni_validi):
        raise ValueError("Gli anni devono essere compresi tra 1979 e 2021.")

    tappe, numero_tappe_per_paese = _prepara_tappe(
        db_name, progetto_id, limite_tappe
    )
    if not tappe:
        raise RuntimeError(
            "Nel progetto non ci sono tappe attive con coordinate di partenza valide."
        )

    files = _lista_file_mensili(anni_validi)
    anni_per_variabile_mese: dict[tuple[str, int], set[int]] = defaultdict(set)
    for variabile, anno, mese in files:
        anni_per_variabile_mese[(variabile, mese)].add(anno)

    for variabile in VARIABILI:
        if not any(nome_variabile == variabile for nome_variabile, _, _ in files):
            raise RuntimeError(
                f"Il catalogo CHELSA non contiene file per la variabile {variabile}."
            )

    somme: dict[tuple[int, str, int, str], float] = defaultdict(float)
    conteggi: dict[tuple[int, str, int, str], int] = defaultdict(int)
    tappe_valide: dict[tuple[int, str, int, str], set[int]] = defaultdict(set)
    punti = [(float(tappa["lon"]), float(tappa["lat"])) for tappa in tappe]
    totale_file = len(files)
    dimensioni: tuple[int, int] | None = None
    risoluzione_raster: tuple[float, float] | None = None

    with rasterio.Env(
        GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
        CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
        GDAL_HTTP_MAX_RETRY="3",
        GDAL_HTTP_RETRY_DELAY="2",
        VSI_CACHE="TRUE",
    ):
        for indice, ((variabile, anno, mese), url) in enumerate(
            sorted(files.items()), start=1
        ):
            messaggio = (
                f"CHELSA: {indice}/{totale_file} file — "
                f"{variabile}, {mese:02d}/{anno}"
            )
            if progress_callback:
                progress_callback(messaggio)

            for tentativo in range(1, TENTATIVI_LETTURA_RASTER + 1):
                campioni_file: list[
                    tuple[tuple[int, str, int, str], int, float]
                ] = []
                dimensioni_file: tuple[int, int] | None = None
                risoluzione_file: tuple[float, float] | None = None
                try:
                    with rasterio.open("/vsicurl/" + url) as raster:
                        dimensioni_file = (raster.width, raster.height)
                        risoluzione_file = tuple(
                            float(valore) for valore in raster.res
                        )
                        scala = raster.scales[0] if raster.scales else 1.0
                        offset = raster.offsets[0] if raster.offsets else 0.0
                        campioni = raster.sample(punti, masked=True)
                        for tappa, campione in zip(tappe, campioni):
                            valore_grezzo = campione[0]
                            if np.ma.is_masked(valore_grezzo):
                                continue
                            valore_float = float(valore_grezzo)
                            if not math.isfinite(valore_float):
                                continue
                            if (
                                raster.nodata is not None
                                and valore_float == raster.nodata
                            ):
                                continue
                            valore = _valore_fisico(
                                valore_float, variabile, scala, offset
                            )
                            chiave = (
                                int(tappa["id_progetto"]),
                                str(tappa["paese"]),
                                mese,
                                variabile,
                            )
                            campioni_file.append(
                                (chiave, int(tappa["id"]), valore)
                            )
                except (OSError, rasterio.errors.RasterioError) as errore:
                    if tentativo == TENTATIVI_LETTURA_RASTER:
                        raise RuntimeError(
                            f"Errore leggendo CHELSA {variabile} "
                            f"{mese:02d}/{anno} dopo "
                            f"{TENTATIVI_LETTURA_RASTER} tentativi: {errore}"
                        ) from errore
                    if progress_callback:
                        progress_callback(
                            f"{messaggio} — tentativo {tentativo} non riuscito; "
                            "nuovo tentativo in corso."
                        )
                    time.sleep(2 ** (tentativo - 1))
                    continue

                if dimensioni is None:
                    dimensioni = dimensioni_file
                    risoluzione_raster = risoluzione_file
                for chiave, id_tappa, valore in campioni_file:
                    somme[chiave] += valore
                    conteggi[chiave] += 1
                    tappe_valide[chiave].add(id_tappa)
                break

    aggiornato_il = datetime.now(timezone.utc).isoformat(timespec="seconds")
    valori_per_variabile = {
        "tas": "temperatura_media",
        "tasmax": "temperatura_max",
        "tasmin": "temperatura_min",
        "pr": "precipitazioni_mm",
        "sfcWind": "vento_media",
    }
    risultati: list[tuple[object, ...]] = []
    paesi_progetto = sorted(numero_tappe_per_paese)
    for id_progetto, codice_paese in paesi_progetto:
        tappe_totali = numero_tappe_per_paese[(id_progetto, codice_paese)]
        for mese in range(1, 13):
            valori: dict[str, float | None] = {
                nome_colonna: None
                for nome_colonna in valori_per_variabile.values()
            }
            conteggi_tappe_mese: list[int] = []
            for variabile, nome_colonna in valori_per_variabile.items():
                chiave = (id_progetto, codice_paese, mese, variabile)
                conteggio = conteggi.get(chiave, 0)
                if conteggio:
                    valori[nome_colonna] = somme[chiave] / conteggio
                validi = len(tappe_valide.get(chiave, set()))
                if validi or anni_per_variabile_mese.get((variabile, mese)):
                    conteggi_tappe_mese.append(validi)

            campioni_validi = (
                min(conteggi_tappe_mese) if conteggi_tappe_mese else 0
            )
            copertura = (
                100.0 * campioni_validi / tappe_totali
                if tappe_totali
                else 0.0
            )
            anni_coperti = {
                variabile: sorted(
                    anni_per_variabile_mese.get((variabile, mese), set())
                )
                for variabile in VARIABILI
            }
            periodo = (
                str(anni_validi[0])
                if len(anni_validi) == 1
                else f"{anni_validi[0]}-{anni_validi[-1]}"
            )
            risoluzione_arcsec = (
                round(max(risoluzione_raster) * 3600)
                if risoluzione_raster
                else 30
            )
            versione = (
                f"{VERSIONE_DATASET}, {periodo}; {risoluzione_arcsec} arcsec; "
                f"{DATASET_PAGE}; CC0 1.0"
            )
            risultati.append(
                (
                    id_progetto,
                    codice_paese,
                    mese,
                    valori["temperatura_media"],
                    valori["temperatura_max"],
                    valori["temperatura_min"],
                    valori["precipitazioni_mm"],
                    valori["vento_media"],
                    versione,
                    aggiornato_il,
                    copertura,
                    campioni_validi,
                    tappe_totali,
                    json.dumps(anni_coperti, sort_keys=True),
                )
            )

    assicura_schema_clima(db_name)
    percorso_db = Path(db_name).resolve()
    with closing(sqlite3.connect(percorso_db)) as connessione:
        connessione.execute("BEGIN")
        progetti = sorted({int(riga[0]) for riga in risultati})
        if progetti:
            segnaposti = ",".join("?" for _ in progetti)
            connessione.execute(
                f"DELETE FROM clima_paese_mese WHERE id_progetto IN ({segnaposti})",
                progetti,
            )
        connessione.executemany(
            """
            INSERT INTO clima_paese_mese (
                id_progetto, paese, mese, temperatura_media,
                temperatura_max, temperatura_min, precipitazioni_mm,
                vento_media, dataset_versione, aggiornato_il, copertura_pct,
                campioni_validi, campioni_totali, anni_coperti
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            risultati,
        )
        connessione.commit()

    cartella_clima = percorso_db.parent / "clima"
    cartella_clima.mkdir(parents=True, exist_ok=True)
    manifest = {
        "dataset": "CHELSA-monthly",
        "versione": "2.1",
        "licenza": "CC0 1.0",
        "fonte": DATASET_PAGE,
        "endpoint_cog": BASE_URL,
        "anni_richiesti": list(anni_validi),
        "variabili": list(VARIABILI),
        "dimensioni_raster": list(dimensioni) if dimensioni else None,
        "risoluzione_gradi": list(risoluzione_raster)
        if risoluzione_raster
        else None,
        "metodo": "Lettura COG via HTTP range; raster globali non scaricati integralmente.",
        "aggiornato_il": aggiornato_il,
        "righe_sqlite": len(risultati),
    }
    if progetto_id is not None:
        manifest["id_progetto"] = progetto_id
    nome_manifest = (
        f"chelsa_progetto_{progetto_id}.json"
        if progetto_id is not None
        else "chelsa_progetti.json"
    )
    percorso_manifest = cartella_clima / nome_manifest
    file_temporaneo = percorso_manifest.with_suffix(".json.tmp")
    file_temporaneo.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    file_temporaneo.replace(percorso_manifest)

    return {
        "righe_salvate": len(risultati),
        "tappe_lette": len(tappe),
        "file_chelsa_letti": totale_file,
        "aggiornato_il": aggiornato_il,
        "manifest": str(percorso_manifest),
    }
