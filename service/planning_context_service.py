"""Regole del contesto scelto per una nuova pianificazione."""

import sqlite3
from contextlib import closing

from service.config import DB_NAME


CONTESTI_PIANIFICAZIONE = (
    ("tappa_unica", "Tappa unica"),
    ("percorso", "Percorso"),
    ("parte_viaggio", "Parte di un viaggio"),
    ("test", "Test tecnico"),
)


def stato_da_contesto(contesto):
    """Restituisce lo stato da salvare per il contesto selezionato."""
    contesti_validi = {valore for valore, _ in CONTESTI_PIANIFICAZIONE}
    if contesto not in contesti_validi:
        raise ValueError("Seleziona un contesto valido prima di salvare.")
    return "BOZZA" if contesto == "test" else "ATTIVA"


def carica_blocchi_progetto(id_progetto, db_name=DB_NAME):
    """Restituisce i blocchi del progetto nell'ordine ufficiale, includendo quelli non registrati."""
    with closing(sqlite3.connect(db_name)) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT nome_blocco FROM blocchi_ordine
            WHERE id_progetto = ? ORDER BY ordine ASC
            """,
            (id_progetto,),
        )
        blocchi_salvati = [riga[0] for riga in cursor.fetchall()]
        cursor.execute(
            """
            SELECT DISTINCT COALESCE(NULLIF(TRIM(blocco), ''), 'Generale')
            FROM tappe WHERE id_progetto = ?
            """,
            (id_progetto,),
        )
        blocchi_esistenti = [riga[0] for riga in cursor.fetchall()]

    blocchi_ordinati = list(blocchi_salvati)
    blocchi_ordinati.extend(
        nome for nome in blocchi_esistenti if nome not in blocchi_ordinati
    )
    return blocchi_ordinati


def valida_nome_nuovo_blocco(nome, blocchi_esistenti):
    """Normalizza il nome del blocco e rifiuta valori vuoti o duplicati."""
    nome_pulito = " ".join(str(nome or "").split())
    if not nome_pulito:
        return None, "Inserisci il nome del nuovo blocco."
    if any(nome_pulito.casefold() == str(blocco).casefold() for blocco in blocchi_esistenti):
        return None, "Esiste già un blocco con questo nome."
    return nome_pulito, None
