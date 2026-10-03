"""Operazioni di dominio sulla tabella `progetti`.

Il modulo incapsula la creazione di un nuovo percorso in modo che i
dialoghi di interfaccia non contengano direttamente istruzioni SQL.
"""

import sqlite3

from service.config import DB_NAME


def crea_progetto(nome, descrizione=""):
    """Crea un nuovo percorso e restituisce il suo identificativo.

    :param nome: nome del percorso (non vuoto).
    :param descrizione: note opzionali.
    :return: l'id numerico del progetto appena creato.
    """
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO progetti (nome_progetto, descrizione, data_creazione) "
            "VALUES (?, ?, CURRENT_TIMESTAMP)",
            (nome, descrizione),
        )
        nuovo_id = cursor.lastrowid
        conn.commit()
    finally:
        conn.close()
    return nuovo_id