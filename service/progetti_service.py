"""Operazioni di dominio sulla tabella `progetti`.

Il modulo incapsula creazione, elenco ed eliminazione di un percorso in
modo che i dialoghi e le pagine GUI non contengano direttamente istruzioni
SQL. `elimina_progetto_completo` sostituisce le due versioni diverse che
finestra principale e dashboard avevano duplicato.
"""

import sqlite3

from service.config import DB_NAME

# Tabelle figlie eliminate unitamente al progetto.
TABELLE_COLLEGATE = (
    "tappe",
    "allarmi_percorso",
    "trasferimenti",
    "blocchi_ordine",
)


def crea_progetto(nome, descrizione="", stato=None):
    """Crea un nuovo percorso e restituisce il suo identificativo.

    :param nome: nome del percorso (non vuoto).
    :param descrizione: note opzionali.
    :param stato: stato iniziale; se `None` la colonna resta quella di default.
    :return: l'id numerico del progetto appena creato.
    """
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        if stato is None:
            cursor.execute(
                "INSERT INTO progetti (nome_progetto, descrizione, data_creazione) "
                "VALUES (?, ?, CURRENT_TIMESTAMP)",
                (nome, descrizione),
            )
        else:
            cursor.execute(
                "INSERT INTO progetti (nome_progetto, stato, data_creazione) "
                "VALUES (?, ?, CURRENT_TIMESTAMP)",
                (nome, stato),
            )
        nuovo_id = cursor.lastrowid
        conn.commit()
    finally:
        conn.close()
    return nuovo_id


def carica_progetti_con_km():
    """Restituisce l'elenco dei percorsi con i chilometri totali di ciascuno.

    :return: lista di dizionari con le chiavi `id`, `nome`, `data`, `stato`
        e `km_totali`, dal più recente al più vecchio.
    """
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nome_progetto, data_creazione, stato "
            "FROM progetti ORDER BY data_creazione DESC"
        )
        progetti = cursor.fetchall()
        risultati = []
        for id_prog, nome, data, stato in progetti:
            cursor.execute(
                "SELECT SUM(distanza_km) FROM tappe WHERE id_progetto = ?",
                (id_prog,),
            )
            res_km = cursor.fetchone()
            km_totali = res_km[0] if res_km and res_km[0] is not None else 0.0
            risultati.append({
                "id": id_prog,
                "nome": nome,
                "data": data,
                "stato": stato,
                "km_totali": km_totali,
            })
        return risultati
    finally:
        conn.close()


def elimina_progetto_completo(id_progetto, tabelle=None):
    """Elimina un percorso e le tabelle a esso collegate.

    :param tabelle: tabelle figlie da pulire; se `None` usa `TABELLE_COLLEGATE`.
        Serve a mantenere le due varianti storiche di eliminazione, che
        pulivano insiemi diversi di tabelle.
    """
    tabelle = TABELLE_COLLEGATE if tabelle is None else tabelle
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM progetti WHERE id = ?", (id_progetto,))
        for tabella in tabelle:
            cursor.execute(
                f"DELETE FROM {tabella} WHERE id_progetto = ?", (id_progetto,)
            )
        conn.commit()
    finally:
        conn.close()