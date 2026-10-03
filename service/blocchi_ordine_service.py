"""Servizio per l'ordine dei blocchi (macro-aree) di un progetto.

Estratto dalla Fase 2 del refactor di ``app_desktop.py``
(vedi REPORT/PIANO_REFACTOR_APP_DESKTOP.md).

Contiene la logica di lettura e scrittura dell'ordine dei blocchi di un
percorso, senza alcuna dipendenza da Qt: è quindi verificabile a parte,
senza aprire la finestra dell'applicazione.
"""

import sqlite3

from service.config import DB_NAME


def leggi_blocchi_ordinati(id_progetto):
    """Restituisce i blocchi del progetto nel loro ordine effettivo.

    Unisce i blocchi realmente presenti nelle tappe con l'ordine salvato in
    ``blocchi_ordine``: i blocchi salvati e ancora esistenti vengono tenuti
    nell'ordine registrato, mentre eventuali blocchi nuovi vengono aggiunti
    in coda.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT DISTINCT blocco FROM tappe WHERE id_progetto = ?",
        (id_progetto,),
    )
    blocchi_reali = [r[0] if r[0] else "Generale" for r in cursor.fetchall()]

    cursor.execute(
        "SELECT nome_blocco FROM blocchi_ordine WHERE id_progetto = ? ORDER BY ordine ASC",
        (id_progetto,),
    )
    blocchi_salvati = [r[0] for r in cursor.fetchall()]

    conn.close()

    blocchi_ordinati = [b for b in blocchi_salvati if b in blocchi_reali]
    for b in blocchi_reali:
        if b not in blocchi_ordinati:
            blocchi_ordinati.append(b)

    return blocchi_ordinati


def salva_ordine_blocchi(id_progetto, nuovo_ordine_blocchi):
    """Salva l'ordine dei blocchi e rinumera la sequenza delle tappe.

    Riscrive interamente la tabella ``blocchi_ordine`` con il nuovo ordine e
    aggiorna il campo ``sequenza`` delle tappe in base all'ordine dei blocchi.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM blocchi_ordine WHERE id_progetto = ?", (id_progetto,))

    for pos, nome_blocco in enumerate(nuovo_ordine_blocchi, start=1):
        cursor.execute(
            "INSERT INTO blocchi_ordine (id_progetto, nome_blocco, ordine) VALUES (?, ?, ?)",
            (id_progetto, nome_blocco, pos),
        )

    nuova_seq = 1
    for nome_blocco in nuovo_ordine_blocchi:
        cursor.execute(
            "SELECT id FROM tappe WHERE id_progetto = ? AND "
            "(blocco = ? OR (blocco IS NULL AND ? = 'Generale')) ORDER BY sequenza ASC",
            (id_progetto, nome_blocco, nome_blocco),
        )
        tappe_blocco = cursor.fetchall()
        for t in tappe_blocco:
            cursor.execute(
                "UPDATE tappe SET sequenza = ? WHERE id = ?",
                (nuova_seq, t[0]),
            )
            nuova_seq += 1

    conn.commit()
    conn.close()
