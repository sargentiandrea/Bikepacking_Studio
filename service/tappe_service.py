"""Operazioni di dominio sulla tabella `tappe`.

Il modulo raccoglie le query condivise dalla finestra principale e dalla
dashboard, che prima le duplicava identiche. Ogni funzione esegue una sola
responsabilita' e lascia ai chiamanti il messaggio e il ricalcolo della UI.
"""

import os
import sqlite3

from service.config import DB_NAME
from service.gpx_paths import trova_percorso_gpx

# Traduzione degli indici del menu a tendina negli stati della tappa.
STATI_PER_RUOLO = {0: 'ATTIVA', 1: 'VARIANTE', 2: 'SOSPESA'}

# Blocco assegnato quando l'utente lascia vuoto il campo.
BLOCCO_PREDEFINITO = "Generale"


def carica_tappe_elenco(id_progetto):
    """Restituisce le tappe da elencare nella tabella, ordinate per sequenza.

    :param id_progetto: identificativo del percorso.
    :return: righe con `sequenza, blocco, nome_file, distanza_km, stato, id`.
    :raises sqlite3.Error: in caso di errore di lettura dal database.
    """
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sequenza, blocco, nome_file, distanza_km, stato, id
            FROM tappe
            WHERE id_progetto = ? AND nome_file IS NOT NULL AND sequenza IS NOT NULL
            ORDER BY sequenza ASC
        """, (id_progetto,))
        return cursor.fetchall()
    finally:
        conn.close()


def imposta_blocco_tappa(tappa_id, nuovo_blocco):
    """Assegna il blocco di una tappa, usando `Generale` se il testo e' vuoto."""
    blocco_val = nuovo_blocco.strip() if nuovo_blocco.strip() else BLOCCO_PREDEFINITO
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tappe SET blocco = ? WHERE id = ?", (blocco_val, tappa_id)
        )
        conn.commit()
    finally:
        conn.close()


def imposta_stato_tappa(tappa_id, stato):
    """Imposta lo stato della tappa (`ATTIVA`, `SOSPESA` o `VARIANTE`)."""
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tappe SET stato = ? WHERE id = ?", (stato, tappa_id)
        )
        conn.commit()
    finally:
        conn.close()


def stato_da_ruolo(indice_ruolo):
    """Converte l'indice del menu a tendina nello stato della tappa."""
    return STATI_PER_RUOLO[indice_ruolo]


def stato_da_pausa(in_pausa):
    """Converte il flag di pausa nello stato della tappa."""
    return 'ATTIVA' if in_pausa else 'SOSPESA'


def elimina_tappa(tappa_id, progetto_di_fallback=None):
    """Elimina una tappa dal database e restituisce il suo progetto.

    :return: l'identificativo del progetto di appartenenza della tappa, o
        `progetto_di_fallback` se la tappa non esiste piu'.
    :raises sqlite3.Error: in caso di errore durante la cancellazione.
    """
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_progetto FROM tappe WHERE id = ?", (tappa_id,))
        riga = cursor.fetchone()
        id_progetto = riga[0] if riga else progetto_di_fallback
        cursor.execute("DELETE FROM tappe WHERE id = ?", (tappa_id,))
        conn.commit()
    finally:
        conn.close()
    return id_progetto


def elimina_file_gpx(nome_file, id_progetto):
    """Rimuove il file GPX della tappa, se presente.

    :return: `True` se il file e' stato rimosso.
    """
    if not nome_file:
        return False
    filepath = trova_percorso_gpx(
        nome_file, id_progetto, directory_gpx=os.path.join(os.getcwd(), "gpx")
    )
    if filepath is None:
        return False
    try:
        os.remove(filepath)
    except Exception as errore:
        print("Errore rimozione file:", errore)
        return False
    return True


def aggiorna_blocco_per_sequenze(id_progetto, sequenze, nuovo_blocco):
    """Assegna lo stesso blocco a tutte le tappe con le sequenze indicate."""
    blocco_pulito = nuovo_blocco.strip()
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        for sequenza in sequenze:
            cursor.execute("""
                UPDATE tappe SET blocco = ?
                WHERE id_progetto = ? AND sequenza = ?
            """, (blocco_pulito, id_progetto, sequenza))
        conn.commit()
    finally:
        conn.close()