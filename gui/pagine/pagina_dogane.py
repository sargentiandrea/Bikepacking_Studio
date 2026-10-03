"""Pagina di servizio "Dogane & Requisiti di Ingresso".

Il widget costruisce la tabella degli attraversamenti doganali e ne cura
l'aggiornamento. Non conosce `app_desktop.py`: riceve il solo identificativo
del progetto da mostrare a ogni aggiornamento.
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from service.dogane_service import analizza_dogane_progetto

from gui.pagine.stile_pagina import applica_stile_servizio, imposta_righe_tabella

# Colonne della tabella degli attraversamenti doganali.
COLONNE_DOGANE = [
    "Ordine",
    "ISO",
    "Paese",
    "Area",
    "Passaporto",
    "Visto",
    "Valuta",
    "Roaming",
    "Drone",
]


class PaginaDogane(QWidget):
    """Mostra i dati doganali salvati per il percorso corrente."""

    def __init__(self, parent=None):
        """Costruisce la pagina e i suoi controlli."""
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        lbl = QLabel("🛂 Dogane & Requisiti di Ingresso")
        lbl.setFont(QFont("Arial", 16, QFont.Bold))
        lbl.setStyleSheet("color: #0e639c;")
        layout.addWidget(lbl)

        self.lbl_stato = QLabel(
            "Seleziona un percorso per visualizzare i dati doganali salvati."
        )
        layout.addWidget(self.lbl_stato)
        self.tabella = QTableWidget()
        self.tabella.setColumnCount(len(COLONNE_DOGANE))
        self.tabella.setHorizontalHeaderLabels(COLONNE_DOGANE)
        self.tabella.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.tabella.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.tabella)

        btn_aggiorna = QPushButton("🔄 Ricarica dati doganali")
        btn_aggiorna.clicked.connect(lambda: self.aggiorna(self.progetto_id))
        layout.addWidget(btn_aggiorna)
        applica_stile_servizio(self)

    @property
    def progetto_id(self):
        """Progetto mostrato dalla pagina, impostato dalla finestra principale."""
        return getattr(self, "_progetto_id", None)

    @progetto_id.setter
    def progetto_id(self, valore):
        """Imposta il progetto corrente senza ricaricare i dati."""
        self._progetto_id = valore

    def aggiorna(self, progetto_id):
        """Ricarica la tabella per `progetto_id` e aggiorna il messaggio di stato."""
        self._progetto_id = progetto_id
        if not progetto_id:
            self.lbl_stato.setText(
                "Apri un percorso per visualizzare i dati doganali salvati."
            )
            imposta_righe_tabella(self.tabella, [])
            return

        try:
            righe = analizza_dogane_progetto(progetto_id)
            imposta_righe_tabella(self.tabella, righe)
            if righe:
                self.lbl_stato.setText(f"{len(righe)} attraversamenti doganali salvati.")
            else:
                self.lbl_stato.setText("Nessun dato doganale salvato per questo percorso.")
        except Exception as errore:
            self.lbl_stato.setText(f"Errore durante il caricamento dogane: {errore}")