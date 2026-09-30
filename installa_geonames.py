"""Scarica e indicizza GeoNames solo quando questo script viene avviato."""

import argparse
import csv
import io
import os
import sqlite3
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from service.config import GEONAMES_DB, GEONAMES_HOME


ARCHIVI = (
    (
        "allCountries.zip",
        "https://download.geonames.org/export/dump/allCountries.zip",
        "allCountries.txt",
    ),
    (
        "alternateNamesV2.zip",
        "https://download.geonames.org/export/dump/alternateNamesV2.zip",
        "alternateNamesV2.txt",
    ),
)
LINGUE_NON_NOMINATIVE = {"post", "link", "wkdt", "iata", "icao", "faac"}
DIMENSIONE_BLOCCO = 50_000


def _scarica_archivio(nome, url, membro, cartella, forza):
    destinazione = cartella / nome
    if destinazione.is_file() and not forza:
        with zipfile.ZipFile(destinazione) as archivio:
            if membro in archivio.namelist():
                print(f"Archivio gia presente: {nome}")
                return destinazione

    temporaneo = destinazione.with_suffix(destinazione.suffix + ".part")
    richiesta = urllib.request.Request(
        url,
        headers={"User-Agent": "BikepackingStudio GeoNames installer"},
    )
    scaricati = 0
    prossima_percentuale = 10

    print(f"Download esplicito: {nome}")
    with urllib.request.urlopen(richiesta, timeout=60) as risposta:
        dimensione_attesa = int(risposta.headers.get("Content-Length", "0"))
        with open(temporaneo, "wb") as file_locale:
            while True:
                blocco = risposta.read(1024 * 1024)
                if not blocco:
                    break
                file_locale.write(blocco)
                scaricati += len(blocco)
                if dimensione_attesa:
                    percentuale = scaricati * 100 // dimensione_attesa
                    if percentuale >= prossima_percentuale:
                        print(f"  {percentuale}%")
                        prossima_percentuale = (percentuale // 10 + 1) * 10
            file_locale.flush()
            os.fsync(file_locale.fileno())

    if dimensione_attesa and scaricati != dimensione_attesa:
        raise IOError(
            f"Download incompleto di {nome}: {scaricati}/{dimensione_attesa} byte."
        )

    with zipfile.ZipFile(temporaneo) as archivio:
        if membro not in archivio.namelist():
            raise ValueError(f"{nome} non contiene il file atteso {membro}.")

    os.replace(temporaneo, destinazione)
    print(f"Download completato: {nome} ({scaricati:,} byte)")
    return destinazione


def _apri_riga_zip(archivio, membro):
    file_zip = archivio.open(membro, "r")
    return file_zip, io.TextIOWrapper(file_zip, encoding="utf-8", newline="")


def _salva_blocco(conn, luoghi, nomi):
    if luoghi:
        conn.executemany(
            """
            INSERT OR REPLACE INTO geonames (
                geonameid, name, asciiname, latitude, longitude,
                feature_class, feature_code, country_code, population
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            luoghi,
        )
        luoghi.clear()
    if nomi:
        conn.executemany(
            """
            INSERT OR IGNORE INTO geonames_names (
                geonameid, name, language, is_preferred, is_primary
            ) VALUES (?, ?, ?, ?, ?)
            """,
            nomi,
        )
        nomi.clear()
    conn.commit()


def _carica_luoghi(conn, percorso_zip):
    righe_lette = 0
    luoghi = []
    nomi = []
    with zipfile.ZipFile(percorso_zip) as archivio:
        file_zip, testo = _apri_riga_zip(archivio, "allCountries.txt")
        with file_zip, testo:
            lettore = csv.reader(testo, delimiter="\t")
            for campi in lettore:
                righe_lette += 1
                if len(campi) < 19:
                    raise ValueError(
                        f"Riga {righe_lette} non valida in allCountries.txt."
                    )
                try:
                    geonameid = int(campi[0])
                    latitudine = float(campi[4])
                    longitudine = float(campi[5])
                    popolazione = int(campi[14] or 0)
                except ValueError as errore:
                    raise ValueError(
                        f"Coordinate o identificativo non validi alla riga {righe_lette}."
                    ) from errore

                nome = campi[1].strip()
                nome_ascii = campi[2].strip()
                luoghi.append((
                    geonameid,
                    nome or nome_ascii,
                    nome_ascii,
                    latitudine,
                    longitudine,
                    campi[6],
                    campi[7],
                    campi[8],
                    popolazione,
                ))
                if nome:
                    nomi.append((geonameid, nome, "", 0, 1))
                if nome_ascii and nome_ascii.casefold() != nome.casefold():
                    nomi.append((geonameid, nome_ascii, "", 0, 0))

                if len(luoghi) >= DIMENSIONE_BLOCCO:
                    _salva_blocco(conn, luoghi, nomi)
                if righe_lette % 500_000 == 0:
                    print(f"  Localita lette: {righe_lette:,}")

    _salva_blocco(conn, luoghi, nomi)
    print(f"Localita caricate: {righe_lette:,}")
    return righe_lette


def _carica_nomi_alternativi(conn, percorso_zip):
    righe_lette = 0
    nomi = []
    with zipfile.ZipFile(percorso_zip) as archivio:
        file_zip, testo = _apri_riga_zip(archivio, "alternateNamesV2.txt")
        with file_zip, testo:
            lettore = csv.reader(testo, delimiter="\t")
            for campi in lettore:
                righe_lette += 1
                if len(campi) < 8:
                    raise ValueError(
                        f"Riga {righe_lette} non valida in alternateNamesV2.txt."
                    )
                nome = campi[3].strip()
                lingua = campi[2].strip().casefold()
                if not nome or lingua in LINGUE_NON_NOMINATIVE or campi[7] == "1":
                    continue
                try:
                    geonameid = int(campi[1])
                except ValueError as errore:
                    raise ValueError(
                        f"Identificativo non valido alla riga {righe_lette} "
                        "di alternateNamesV2.txt."
                    ) from errore

                nomi.append((
                    geonameid,
                    nome,
                    lingua,
                    int(campi[4] == "1"),
                    0,
                ))
                if len(nomi) >= DIMENSIONE_BLOCCO:
                    _salva_blocco(conn, [], nomi)
                if righe_lette % 1_000_000 == 0:
                    print(f"  Nomi alternativi letti: {righe_lette:,}")

    _salva_blocco(conn, [], nomi)
    print(f"Nomi alternativi esaminati: {righe_lette:,}")
    return righe_lette


def _crea_indice(percorso_db, archivio_luoghi, archivio_nomi):
    if os.path.exists(percorso_db):
        os.remove(percorso_db)

    conn = sqlite3.connect(percorso_db, timeout=60.0)
    try:
        conn.execute("PRAGMA journal_mode = OFF")
        conn.execute("PRAGMA synchronous = OFF")
        conn.execute("PRAGMA temp_store = MEMORY")
        conn.executescript(
            """
            CREATE TABLE geonames (
                geonameid INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                asciiname TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                feature_class TEXT,
                feature_code TEXT,
                country_code TEXT,
                population INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE geonames_names (
                id INTEGER PRIMARY KEY,
                geonameid INTEGER NOT NULL,
                name TEXT NOT NULL,
                language TEXT NOT NULL,
                is_preferred INTEGER NOT NULL DEFAULT 0,
                is_primary INTEGER NOT NULL DEFAULT 0,
                UNIQUE (geonameid, name, language)
            );
            CREATE TABLE metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )

        righe_luoghi = _carica_luoghi(conn, archivio_luoghi)
        righe_nomi = _carica_nomi_alternativi(conn, archivio_nomi)
        print("Creazione indici di ricerca FTS5...")
        conn.execute(
            "CREATE INDEX geonames_names_id_idx ON geonames_names(geonameid)"
        )
        conn.execute(
            """
            CREATE VIRTUAL TABLE geonames_names_fts USING fts5(
                name,
                content='geonames_names',
                content_rowid='id',
                tokenize='unicode61 remove_diacritics 2'
            )
            """
        )
        conn.execute(
            "INSERT INTO geonames_names_fts(geonames_names_fts) VALUES ('rebuild')"
        )
        conn.executemany(
            "INSERT INTO metadata (key, value) VALUES (?, ?)",
            (
                ("installed_at_utc", datetime.now(timezone.utc).isoformat()),
                ("source", "GeoNames allCountries + alternateNamesV2"),
                ("license", "Creative Commons Attribution 4.0"),
                ("allcountries_rows", str(righe_luoghi)),
                ("alternate_names_rows", str(righe_nomi)),
            ),
        )
        conn.commit()
        conn.execute("PRAGMA optimize")
        luoghi_indicizzati = conn.execute(
            "SELECT COUNT(*) FROM geonames"
        ).fetchone()[0]
        nomi_indicizzati = conn.execute(
            "SELECT COUNT(*) FROM geonames_names"
        ).fetchone()[0]
        if luoghi_indicizzati == 0 or nomi_indicizzati == 0:
            raise ValueError("L'indice GeoNames e vuoto.")
        print(
            f"Indice pronto: {luoghi_indicizzati:,} localita, "
            f"{nomi_indicizzati:,} nomi."
        )
    finally:
        conn.close()


def installa_geonames(forza=False):
    cartella = Path(GEONAMES_HOME)
    cartella_archivi = cartella / "source"
    cartella_archivi.mkdir(parents=True, exist_ok=True)

    if os.path.isfile(GEONAMES_DB) and not forza:
        print(
            f"Indice GeoNames gia installato in {GEONAMES_DB}. "
            "Usa --force per aggiornarlo."
        )
        return

    archivi_locali = [
        _scarica_archivio(nome, url, membro, cartella_archivi, forza)
        for nome, url, membro in ARCHIVI
    ]
    temporaneo = GEONAMES_DB + ".tmp"
    for suffisso in ("", "-journal", "-wal", "-shm"):
        residuo = temporaneo + suffisso
        if os.path.isfile(residuo):
            os.remove(residuo)

    try:
        _crea_indice(temporaneo, archivi_locali[0], archivi_locali[1])
        os.replace(temporaneo, GEONAMES_DB)
    finally:
        for suffisso in ("", "-journal", "-wal", "-shm"):
            residuo = temporaneo + suffisso
            if os.path.isfile(residuo):
                os.remove(residuo)

    attribuzione = (
        "GeoNames Gazetteer\n"
        "Dati: GeoNames\n"
        "Licenza: Creative Commons Attribution 4.0 (CC BY 4.0)\n"
        "https://creativecommons.org/licenses/by/4.0/\n"
        "https://www.geonames.org/\n"
        "Dati trasformati in un indice SQLite locale per la ricerca di luoghi.\n"
    )
    with open(cartella / "ATTRIBUTION.txt", "w", encoding="utf-8") as file_attribuzione:
        file_attribuzione.write(attribuzione)
    print(f"Installazione completata: {GEONAMES_DB}")


def main():
    parser = argparse.ArgumentParser(
        description="Scarica e installa l'indice offline GeoNames."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="riscarica i dati e ricostruisce l'indice offline",
    )
    argomenti = parser.parse_args()
    installa_geonames(forza=argomenti.force)


if __name__ == "__main__":
    main()
