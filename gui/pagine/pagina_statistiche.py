"""Pagina di servizio "Totali & Statistiche Avanzate".

Mostra i KPI aggregati del percorso, l'elenco dei paesi attraversati e due
tabelle di dettaglio (per blocco e per fascia costiera). Il pulsante di
apertura dell'elenco paesi è delegato a una callback, così il modulo non
conosce `app_desktop.py`.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from service import stats_service

from gui.pagine.stile_pagina import applica_stile_servizio, imposta_righe_tabella

# Colonne delle due tabelle di dettaglio.
COLONNE_BLOCCHI = [
    "Ordine",
    "Blocco",
    "Tappe",
    "Distanza",
    "Dislivello +",
    "Dislivello -",
    "Quota max",
    "Pendenza media",
]
COLONNE_COSTA = [
    "Fascia costiera",
    "Tappe coinvolte",
    "Km totali",
    "Percentuale viaggio",
]

# Testo delle cinque card KPI, in ordine di creazione.
KPI_TOTALE = ("KM TOTALI", "18pt", "-")
KPI_DISLIVELLO_POS = ("DISLIVELLO +", "18pt", "-")
KPI_DISLIVELLO_NEG = ("DISLIVELLO -", "18pt", "-")
KPI_QUOTA = ("QUOTA MAX", "18pt", "-")
KPI_PENDENZA = ("PENDENZA MEDIA", "18pt", "-")
KPI_PAESI = ("PAESI ATTRAVERSATI", "14pt", "-")

# Stile delle card KPI.
STILE_CARD = """
    QLabel {
        background-color: #252526;
        color: #ffffff;
        border: 1px solid #3e3e42;
        border-radius: 6px;
        padding: 10px;
    }
"""

# Stile delle due tabelle di dettaglio.
STILE_TABELLA_DETTAGLIO = """
    QTableWidget { background-color: #252526; alternate-background-color: #2a2a2d; gridline-color: #3e3e42; color: #ffffff; border: 1px solid #3e3e42; border-radius: 5px; }
    QTableWidget::item { padding: 4px 6px; }
    QHeaderView::section { background-color: #2d2d30; color: #0e639c; font-weight: bold; padding: 7px; border: 1px solid #3e3e42; }
"""

# Colore associato a ogni valore KPI.
COLORI_KPI = {
    KPI_TOTALE: "#4ec9b0",
    KPI_DISLIVELLO_POS: "#ce9178",
    KPI_DISLIVELLO_NEG: "#ce9178",
    KPI_QUOTA: "#569cd6",
    KPI_PENDENZA: "#dcdcaa",
}


def testo_card(titolo, valore, dimensione="18pt", colore=None):
    """Compone l'HTML di una card KPI con o senza valore colorato."""
    if colore:
        valore_html = f"<span style='font-size:{dimensione}; color:{colore};'>{valore}</span>"
    else:
        valore_html = f"<span style='font-size:{dimensione};'>{valore}</span>"
    return f"<b>{titolo}</b><br>{valore_html}"
class PaginaStatistiche(QWidget):
    """Mostra i KPI e i dettagli statistici del percorso."""

    def __init__(self, apri_elenco_paesi, parent=None):
        """Costruisce la pagina.

        :param apri_elenco_paesi: callback senza argomenti che apre il dialogo
            con l'elenco dei paesi attraversati.
        """
        super().__init__(parent)
        self._apri_elenco_paesi = apri_elenco_paesi
        self._progetto_id = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        lbl = QLabel("📊 Totali & Statistiche Avanzate")
        lbl.setFont(QFont("Arial", 16, QFont.Bold))
        lbl.setStyleSheet("color: #0e639c;")
        layout.addWidget(lbl)

        self.lbl_stato = QLabel("Seleziona un percorso per calcolare le statistiche.")
        layout.addWidget(self.lbl_stato)

        kpi_layout = QHBoxLayout()
        self.card_km = self._crea_card(KPI_TOTALE)
        self.card_dplus = self._crea_card(KPI_DISLIVELLO_POS)
        self.card_dminus = self._crea_card(KPI_DISLIVELLO_NEG)
        self.card_quota = self._crea_card(KPI_QUOTA)
        self.card_pendenza = self._crea_card(KPI_PENDENZA)
        for card in (
            self.card_km,
            self.card_dplus,
            self.card_dminus,
            self.card_quota,
            self.card_pendenza,
        ):
            kpi_layout.addWidget(card)
        layout.addLayout(kpi_layout)

        paesi_layout = QVBoxLayout()
        self.card_paesi = self._crea_card(KPI_PAESI)
        self.card_paesi.setMaximumWidth(440)
        self.card_paesi.setMinimumHeight(62)
        paesi_layout.addWidget(self.card_paesi, alignment=Qt.AlignmentFlag.AlignCenter)
        btn_apri_paesi = QPushButton("🌐 Visualizza paesi e bandiere")
        btn_apri_paesi.setStyleSheet("background-color: #0e639c; color: white; font-weight: bold; padding: 8px 16px; border-radius: 4px;")
        btn_apri_paesi.clicked.connect(self._apri_elenco_paesi)
        paesi_layout.addWidget(btn_apri_paesi, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(paesi_layout)

        tabs = QTabWidget()
        self.tabella_blocchi = self._crea_tabella(COLONNE_BLOCCHI)
        tabs.addTab(self.tabella_blocchi, "Per blocco")
        self.tabella_costa = self._crea_tabella(COLONNE_COSTA)
        tabs.addTab(self.tabella_costa, "Distanza dalla costa")
        layout.addWidget(tabs)

        btn_aggiorna = QPushButton("🔄 Ricalcola statistiche")
        btn_aggiorna.clicked.connect(lambda: self.aggiorna(self._progetto_id))
        layout.addWidget(btn_aggiorna)

        applica_stile_servizio(self)
        for tabella in (self.tabella_blocchi, self.tabella_costa):
            tabella.setStyleSheet(STILE_TABELLA_DETTAGLIO)
            tabella.setAlternatingRowColors(True)
            tabella.verticalHeader().setDefaultSectionSize(40)

    def _crea_card(self, specifica):
        """Crea una card KPI inizializzata con il segno di valore vuoto."""
        titolo, dimensione, vuoto = specifica
        card = QLabel(testo_card(titolo, vuoto, dimensione))
        card.setStyleSheet(STILE_CARD)
        card.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return card

    def _crea_tabella(self, colonne):
        """Crea una tabella di dettaglio con le colonne indicate."""
        tabella = QTableWidget()
        tabella.setColumnCount(len(colonne))
        tabella.setHorizontalHeaderLabels(colonne)
        tabella.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        return tabella

    def _azzera(self):
        """Riporta tutte le card e le tabelle allo stato vuoto."""
        for card, specifica in (
            (self.card_km, KPI_TOTALE),
            (self.card_dplus, KPI_DISLIVELLO_POS),
            (self.card_dminus, KPI_DISLIVELLO_NEG),
            (self.card_quota, KPI_QUOTA),
            (self.card_pendenza, KPI_PENDENZA),
        ):
            titolo, dimensione, vuoto = specifica
            card.setText(testo_card(titolo, vuoto, dimensione))
        titolo, dimensione, vuoto = KPI_PAESI
        self.card_paesi.setText(testo_card(titolo, vuoto, dimensione))
        imposta_righe_tabella(self.tabella_blocchi, [])
        imposta_righe_tabella(self.tabella_costa, [])

    def aggiorna(self, progetto_id):
        """Ricalcola KPI e tabelle per `progetto_id`."""
        self._progetto_id = progetto_id
        if not progetto_id:
            self.lbl_stato.setText("Apri un percorso per calcolare le statistiche.")
            self._azzera()
            return

        try:
            kpi = stats_service.ottieni_kpi_totali_progetto(progetto_id)
            blocchi = stats_service.ottieni_statistiche_per_blocco(progetto_id)
            _, totale_paesi, descrizione_paesi = stats_service.get_paesi_attraversati_stats(progetto_id)
            costa = stats_service.ottieni_ripartizione_fasce_mare(progetto_id)

            valori = (
                (self.card_km, KPI_TOTALE, f"{kpi['km_totali']} km"),
                (self.card_dplus, KPI_DISLIVELLO_POS, f"{kpi['dislivello_pos']} m"),
                (self.card_dminus, KPI_DISLIVELLO_NEG, f"{kpi['dislivello_neg']} m"),
                (self.card_quota, KPI_QUOTA, f"{kpi['quota_max']} m"),
                (self.card_pendenza, KPI_PENDENZA, f"{kpi['pendenza_media']} %"),
            )
            for card, specifica, valore in valori:
                titolo, dimensione, _ = specifica
                card.setText(
                    testo_card(titolo, valore, dimensione, COLORI_KPI[specifica])
                )

            titolo, dimensione, _ = KPI_PAESI
            self.card_paesi.setText(testo_card(
                f"{titolo} ({totale_paesi})", descrizione_paesi, dimensione, "#4ec9b0"
            ))

            imposta_righe_tabella(self.tabella_blocchi, blocchi)
            imposta_righe_tabella(self.tabella_costa, costa)
            self.tabella_blocchi.setEditTriggers(
                QTableWidget.EditTrigger.NoEditTriggers
            )
            self.tabella_costa.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.lbl_stato.setText("Statistiche aggiornate.")
        except Exception as errore:
            self.lbl_stato.setText(f"Errore durante il calcolo statistiche: {errore}")