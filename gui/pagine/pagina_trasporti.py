"""Pagina di servizio "Logistica e Trasferimenti Intermodali".

Mostra i trasferimenti salvati e le interruzioni (GAP e tratti vietati)
rilevate dall'audit, offrendo il comando per generare il raccordo GPX.
Il widget non conosce `app_desktop.py`: il raccordo viene delegato a una
callback ricevuta in costruzione.
"""

import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

import service.audit_service
from service.config import DB_NAME

from gui.pagine.stile_pagina import applica_stile_servizio, imposta_righe_tabella

# Colonne delle due tabelle della pagina.
COLONNE_TRASFERIMENTI = [
    "Mezzo",
    "Vettore",
    "Da",
    "A",
    "Durata",
    "Costo EUR",
    "Note",
]
COLONNE_INTERRUZIONI = ["Tipo", "Tappa di partenza", "Dettaglio"]


def carica_trasferimenti(progetto_id):
    """Restituisce i trasferimenti logistici salvati per il progetto.

    :param progetto_id: identificativo del percorso.
    :return: lista di tuple con i dati mostrati nella tabella.
    :raises sqlite3.Error: in caso di errore di lettura dal database.
    """
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT tipo_mezzo, vettore, da_luogo, a_luogo, durata, costo_eur, note
            FROM trasferimenti WHERE id_progetto = ? ORDER BY id
            """,
            (progetto_id,),
        )
        return cursor.fetchall()
    finally:
        conn.close()


def recupera_nomi_tappe(id_origine, id_destinazione):
    """Restituisce i nomi delle due tappe che delimitano un GAP.

    :return: la coppia `(nome_origine, nome_destinazione)`; ogni elemento è
        `None` se la tappa non esiste più.
    :raises sqlite3.Error: in caso di errore di lettura dal database.
    """
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT nome_file FROM tappe WHERE id = ?", (id_origine,))
        origine = cursor.fetchone()
        cursor.execute("SELECT nome_file FROM tappe WHERE id = ?", (id_destinazione,))
        destinazione = cursor.fetchone()
    finally:
        conn.close()
    return (
        origine[0] if origine else None,
        destinazione[0] if destinazione else None,
    )
class PaginaTrasporti(QWidget):
    """Mostra trasferimenti logistici e interruzioni del percorso."""

    def __init__(self, al_raccordo_gap, parent=None):
        """Costruisce la pagina.

        :param al_raccordo_gap: callback
            `(id_origine, id_destinazione, nome_origine, nome_destinazione)`
            invocata quando l'utente chiede il raccordo GPX di un GAP.
        """
        super().__init__(parent)
        self._al_raccordo_gap = al_raccordo_gap
        self._progetto_id = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        lbl = QLabel("🚢 Logistica e Trasferimenti Intermodali")
        lbl.setFont(QFont("Arial", 16, QFont.Bold))
        lbl.setStyleSheet("color: #0e639c;")
        layout.addWidget(lbl)

        self.lbl_stato = QLabel(
            "Seleziona un percorso per visualizzare trasferimenti e interruzioni."
        )
        layout.addWidget(self.lbl_stato)

        tabs = QTabWidget()
        self.tabella_trasferimenti = QTableWidget()
        self.tabella_trasferimenti.setColumnCount(len(COLONNE_TRASFERIMENTI))
        self.tabella_trasferimenti.setHorizontalHeaderLabels(COLONNE_TRASFERIMENTI)
        self.tabella_trasferimenti.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        tabs.addTab(self.tabella_trasferimenti, "Trasferimenti salvati")

        gap_page = QWidget()
        gap_layout = QVBoxLayout(gap_page)
        self.tabella_gap = QTableWidget()
        self.tabella_gap.setColumnCount(len(COLONNE_INTERRUZIONI))
        self.tabella_gap.setHorizontalHeaderLabels(COLONNE_INTERRUZIONI)
        self.tabella_gap.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        gap_layout.addWidget(self.tabella_gap)
        btn_raccorda_gap = QPushButton("🔗 Genera raccordo GPX per il gap selezionato")
        btn_raccorda_gap.clicked.connect(self.raccorda_gap_selezionato)
        gap_layout.addWidget(btn_raccorda_gap)
        tabs.addTab(gap_page, "Interruzioni rilevate")
        layout.addWidget(tabs)

        btn_aggiorna = QPushButton("🔄 Aggiorna dati logistici")
        btn_aggiorna.clicked.connect(lambda: self.aggiorna(self._progetto_id))
        layout.addWidget(btn_aggiorna)
        applica_stile_servizio(self)

    def aggiorna(self, progetto_id):
        """Ricarica trasferimenti e interruzioni per `progetto_id`."""
        self._progetto_id = progetto_id
        if not progetto_id:
            self.lbl_stato.setText("Apri un percorso per visualizzare i dati logistici.")
            imposta_righe_tabella(self.tabella_trasferimenti, [])
            imposta_righe_tabella(self.tabella_gap, [])
            return

        try:
            trasferimenti = carica_trasferimenti(progetto_id)
            gaps = service.audit_service.rileva_gap_progetto(progetto_id)
            strade_vietate = service.audit_service.rileva_strade_vietate_progetto(progetto_id)
            allarmi = gaps + strade_vietate
            imposta_righe_tabella(self.tabella_trasferimenti, trasferimenti)
            self.tabella_gap.setRowCount(len(allarmi))
            for row_index, gap in enumerate(allarmi):
                item_tipo = QTableWidgetItem(gap["tipo"])
                item_tipo.setData(
                    Qt.ItemDataRole.UserRole,
                    (gap["id_tappa_origine"], gap["id_tappa_destinazione"]),
                )
                self.tabella_gap.setItem(row_index, 0, item_tipo)
                self.tabella_gap.setItem(
                    row_index, 1, QTableWidgetItem(str(gap["id_tappa_origine"]))
                )
                self.tabella_gap.setItem(row_index, 2, QTableWidgetItem(gap["messaggio"]))

            self.lbl_stato.setText(
                f"{len(trasferimenti)} trasferimenti salvati; {len(gaps)} interruzioni e "
                f"{len(strade_vietate)} tratti vietati alle bici da valutare."
            )
        except Exception as errore:
            self.lbl_stato.setText(f"Errore durante il caricamento logistico: {errore}")

    def raccorda_gap_selezionato(self):
        """Chiede il raccordo GPX per l'interruzione selezionata, se è un GAP."""
        row = self.tabella_gap.currentRow()
        if row < 0:
            QMessageBox.information(self, "Selezione richiesta", "Seleziona prima un'interruzione.")
            return

        tipo_selezionato = self.tabella_gap.item(row, 0).text()
        if not tipo_selezionato.startswith("GAP_"):
            QMessageBox.information(
                self, "Raccordo non disponibile",
                "Questo allarme non è un'interruzione di percorso: non prevede la generazione automatica di un raccordo GPX."
            )
            return

        ids = self.tabella_gap.item(row, 0).data(Qt.ItemDataRole.UserRole)
        origine, destinazione = recupera_nomi_tappe(ids[0], ids[1])
        if origine and destinazione:
            self._al_raccordo_gap(ids[0], ids[1], origine, destinazione)