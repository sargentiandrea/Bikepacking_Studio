#!/usr/bin/env python3
"""Importa clima_mondiale.db in bikepacking_app.db come livello base id 0.

Le righe esistenti con id_progetto = 1 (viaggio dell'utente) NON vengono toccate.
Operazione transazionale: in caso di errore viene eseguito il rollback.
"""

import sqlite3
import sys
from contextlib import closing
from pathlib import Path

BASE = Path(r"C:\Users\sarge\Desktop\Bikepacking_Studio\data")
SOURCE = BASE / "clima_mondiale.db"
DEST = BASE / "bikepacking_app.db"
TABELLA = "clima_paese_mese"
ID_BASE = 0


def conteggi(conn):
    tot = conn.execute("SELECT COUNT(*) FROM " + TABELLA).fetchone()[0]
    zero = conn.execute(
        "SELECT COUNT(*) FROM " + TABELLA + " WHERE id_progetto = 0"
    ).fetchone()[0]
    uno = conn.execute(
        "SELECT COUNT(*) FROM " + TABELLA + " WHERE id_progetto = 1"
    ).fetchone()[0]
    altri = conn.execute(
        "SELECT COUNT(*) FROM " + TABELLA + " WHERE id_progetto NOT IN (0, 1)"
    ).fetchone()[0]
    return {"totale": tot, "id0": zero, "id1": uno, "altri": altri}


def righe_progetto_1(conn):
    return conn.execute(
        "SELECT * FROM " + TABELLA + " WHERE id_progetto = 1 "
        "ORDER BY id_progetto, paese, mese"
    ).fetchall()


def main():
    if not SOURCE.exists():
        print("ERRORE: sorgente assente: " + str(SOURCE))
        return 1
    if not DEST.exists():
        print("ERRORE: destinazione assente: " + str(DEST))
        return 1

    print("Sorgente (sola lettura): " + str(SOURCE))
    print("Destinazione (scrittura): " + str(DEST))

    with closing(sqlite3.connect(
            "file:" + str(SOURCE).replace("\\", "/") + "?mode=ro", uri=True)
    ) as src:
        src.row_factory = sqlite3.Row
        colonne_src = [r[1] for r in src.execute(
            "PRAGMA table_info(" + TABELLA + ")")]
        righe = src.execute(
            "SELECT * FROM " + TABELLA + " ORDER BY paese, mese"
        ).fetchall()
    print("Righe lette dalla sorgente: " + str(len(righe)))
    if not righe:
        print("ERRORE: sorgente vuota, interrotto.")
        return 1

    conn = sqlite3.connect(str(DEST))
    conn.row_factory = sqlite3.Row
    try:
        colonne_dst = [r[1] for r in conn.execute(
            "PRAGMA table_info(" + TABELLA + ")")]
        comuni = [c for c in colonne_src if c in colonne_dst]
        if len(comuni) != len(colonne_src) or len(comuni) != len(colonne_dst):
            print("ERRORE: schema non allineato.")
            print("  solo sorgente: " + str(
                [c for c in colonne_src if c not in colonne_dst]))
            print("  solo destinazione: " + str(
                [c for c in colonne_dst if c not in colonne_src]))
            return 1
        print("Schema allineato: " + str(len(comuni)) + " colonne")

        prima = conteggi(conn)
        print("PRIMA  -> totale: %(totale)d  id0: %(id0)d  id1: %(id1)d  "
              "altri: %(altri)d" % prima)
        snapshot_1 = righe_progetto_1(conn)

        try:
            conn.execute("BEGIN IMMEDIATE")
            sql = ("INSERT OR REPLACE INTO " + TABELLA + " ("
                   + ", ".join(comuni) + ") VALUES ("
                   + ", ".join(["?"] * len(comuni)) + ")")
            valori = []
            for r in righe:
                t = [r[c] for c in comuni]
                t[comuni.index("id_progetto")] = ID_BASE
                valori.append(tuple(t))
            cur = conn.executemany(sql, valori)
            inserite = cur.rowcount
            conn.commit()
            print("INSERT OR REPLACE eseguite: " + str(inserite))
        except Exception as e:
            conn.rollback()
            print("ERRORE durante l'import, ROLLBACK eseguito: " + str(e))
            return 1

        dopo = conteggi(conn)
        print("DOPO   -> totale: %(totale)d  id0: %(id0)d  id1: %(id1)d  "
              "altri: %(altri)d" % dopo)
        print("id1 invariato: " + str(righe_progetto_1(conn) == snapshot_1))

        print("\n--- VERIFICA ---")
        ok = True
        if dopo["id0"] != 2892:
            print("FALLITO: id0 = " + str(dopo["id0"]) + " (atteso 2892)")
            ok = False
        else:
            print("OK: COUNT(*) WHERE id_progetto=0 -> 2892")
        if dopo["id1"] != 540:
            print("FALLITO: id1 = " + str(dopo["id1"]) + " (atteso 540)")
            ok = False
        else:
            print("OK: COUNT(*) WHERE id_progetto=1 -> 540 (invariato)")
        if dopo["totale"] != 3432:
            print("FALLITO: totale = " + str(dopo["totale"]) +
                  " (atteso 3432)")
            ok = False
        else:
            print("OK: COUNT(*) totale -> 3432")

        npaesi = conn.execute(
            "SELECT COUNT(DISTINCT paese) FROM " + TABELLA +
            " WHERE id_progetto = 0").fetchone()[0]
        nmesi = conn.execute(
            "SELECT COUNT(DISTINCT mese) FROM " + TABELLA +
            " WHERE id_progetto = 0").fetchone()[0]
        integ = conn.execute("PRAGMA integrity_check").fetchone()[0]
        print("Paesi distinti (id0): " + str(npaesi))
        print("Mesi distinti (id0): " + str(nmesi))
        print("integrity_check: " + str(integ))

        print("\nESITO: " + ("OK" if ok else "FALLITO"))
        return 0 if ok else 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())