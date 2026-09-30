"""Ricerca locale dei nomi geografici indicizzati da GeoNames."""

import os
import re
import sqlite3
from contextlib import closing
from pathlib import Path

from service.config import GEONAMES_DB


def cerca_coordinate_luogo(testo):
    """Restituisce latitudine e longitudine del luogo piu pertinente."""
    if not os.path.isfile(GEONAMES_DB):
        raise ValueError(
            "Indice GeoNames offline non installato. Esegui installa_geonames.py."
        )

    query = str(testo or "").split(",", 1)[0].strip()
    tokens = re.findall(r"\w+", query, flags=re.UNICODE)
    if not tokens:
        raise ValueError("Inserisci un nome di luogo valido.")

    query_fts = " AND ".join(f'"{token}"*' for token in tokens)
    database_uri = Path(GEONAMES_DB).resolve().as_uri() + "?mode=ro"
    try:
        with closing(sqlite3.connect(database_uri, uri=True, timeout=20.0)) as conn:
            risultato = conn.execute(
                """
                SELECT luoghi.latitude, luoghi.longitude
                FROM geonames_names_fts AS ricerca
                JOIN geonames_names AS nomi ON nomi.id = ricerca.rowid
                JOIN geonames AS luoghi ON luoghi.geonameid = nomi.geonameid
                WHERE geonames_names_fts MATCH ?
                ORDER BY
                    (nomi.name = ? COLLATE NOCASE) DESC,
                    (luoghi.feature_code = 'PCLI') DESC,
                    (luoghi.feature_class = 'P') DESC,
                    luoghi.population DESC,
                    nomi.is_preferred DESC,
                    nomi.is_primary DESC,
                    bm25(geonames_names_fts)
                LIMIT 1
                """,
                (query_fts, query),
            ).fetchone()
    except sqlite3.Error as errore:
        raise RuntimeError(
            f"Indice GeoNames locale non leggibile: {GEONAMES_DB}"
        ) from errore

    if risultato is None:
        raise ValueError(
            f"Non trovo '{query}' nell'indice locale. Prova con un nome piu noto "
            "oppure inserisci le coordinate."
        )

    return float(risultato[0]), float(risultato[1])
