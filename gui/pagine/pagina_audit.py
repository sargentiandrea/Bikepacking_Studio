"""Pagina di servizio "Control Room & Audit Qualità Percorso".

Mostra gli allarmi ancora attivi sul percorso e, per ciascuno, i tre
comandi di risoluzione: mappa del GAP, raccordo GPX e registrazione del
trasferimento logistico. Le azioni sono delegate alla finestra principale
tramite callback ricevute in costruzione, così il modulo non conosce
`app_desktop.py`.
"""

import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from service.config import DB_NAME

# Colonne della tabella degli allarmi.
COLONNE_ALLARMI = [
    "Tipo Criticità",
    "Messaggio / Dettaglio Completo",
    "Stato",
    "Opzioni & Soluzioni Proposte",
]

# Stile dedicato alla tabella degli allarmi.
STILE_TABELLA_ALLARMI = """
    QTableWidget { background-color: #252526; gridline-color: #3e3e42; color: #ffffff; border: 1px solid #3e3e42; border-radius: 5px; }
    QTableWidget::item { padding: 6px; }
    QHeaderView::section { background-color: #2d2d30; color: #a93226; font-weight: bold; padding: 8px; }
"""


def carica_allarmi_attivi(progetto_id):
    """Restituisce gli allarmi non risolti del percorso con i dati delle tappe.

    :param progetto_id: identificativo del percorso.
    :return: lista di righe con tipo, messaggio, stato, id e nomi delle tappe
        e le coordinate dei due estremi.
    :raises sqlite3.Error: in caso di errore di lettura dal database.
    """
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.tipo_allarme, a.messaggio, a.risolto, a.tappa_origine_id, a.tappa_destinazione_id,
                   t1.nome_file, t2.nome_file, a.id, t1.end_lat, t1.end_lon, t2.start_lat, t2.start_lon
            FROM allarmi_percorso a
            LEFT JOIN tappe t1 ON a.tappa_origine_id = t1.id
            LEFT JOIN tappe t2 ON a.tappa_destinazione_id = t2.id
            WHERE a.id_progetto = ? AND a.risolto = 0
        """, (progetto_id,))
        return cursor.fetchall()
    finally:
        conn.close()
class PaginaAudit(QWidget):
    """Mostra gli allarmi attivi del percorso e i relativi comandi."""

    def __init__(
        self,
        al_mappa_gap,
        al_raccordo_traccia,
        al_wizard_trasferimento,
        parent=None,
    ):
        """Costruisce la pagina.

        :param al_mappa_gap: callback con i due estremi del GAP per mostrarne
            le coordinate.
        :param al_raccordo_traccia: callback
            `(id_origine, id_destinazione, nome_origine, nome_destinazione)`
            per generare il raccordo GPX.
        :param al_wizard_trasferimento: callback con l'id dell'allarme per
            aprire il wizard logistico.
        """
        super().__init__(parent)
        self._al_mappa_gap = al_mappa_gap
        self._al_raccordo_traccia = al_raccordo_traccia
        self._al_wizard_trasferimento = al_wizard_trasferimento
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)

        lbl_titolo = QLabel("⚠️ Control Room & Audit Qualità Percorso")
        lbl_titolo.setFont(QFont("Arial", 16, QFont.Bold))
        lbl_titolo.setStyleSheet("color: #0e639c;")
        layout.addWidget(lbl_titolo)

        self.lbl_stato = QLabel("Seleziona un percorso per verificare gli allarmi.")
        self.lbl_stato.setFont(QFont("Arial", 11))
        layout.addWidget(self.lbl_stato)

        layout.addSpacing(10)

        self.tabella = QTableWidget()
        self.tabella.setColumnCount(len(COLONNE_ALLARMI))
        self.tabella.setHorizontalHeaderLabels(COLONNE_ALLARMI)
        self.tabella.verticalHeader().setDefaultSectionSize(55)
        header = self.tabella.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.tabella.setColumnWidth(0, 160)
        self.tabella.setColumnWidth(2, 90)
        self.tabella.setColumnWidth(3, 380)
        self.tabella.setStyleSheet(STILE_TABELLA_ALLARMI)
        layout.addWidget(self.tabella)

    def aggiorna(self, progetto_id):
        """Ricarica gli allarmi attivi di `progetto_id` nella tabella."""
        if not progetto_id:
            self.tabella.setRowCount(0)
            return

        rows = carica_allarmi_attivi(progetto_id)

        if not rows:
            self.lbl_stato.setText("🟢 Nessun allarme attivo: la rotta è continua o coperta da logistica!")
            self.lbl_stato.setStyleSheet("color: #28a745; font-weight: bold;")
        else:
            self.lbl_stato.setText(f"🔴 Rilevati {len(rows)} GAP/Interruzioni da risolvere lungo il tracciato!")
            self.lbl_stato.setStyleSheet("color: #e74c3c; font-weight: bold;")

        self._popola_righe(rows)

    def _popola_righe(self, rows):
        """Riempie la tabella con gli allarmi e i loro pulsanti d'azione."""
        self.tabella.setRowCount(len(rows))
        for row_idx, data in enumerate(rows):
            tipo, msg, risolto, t1_id, t2_id, t1_nome, t2_nome, allarme_id, end_lat, end_lon, start_lat, start_lon = data

            item_tipo = QTableWidgetItem("🔗 TERRA" if tipo == 'GAP_TERRA' else "⚠️ GAP AMPIO")
            item_tipo.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabella.setItem(row_idx, 0, item_tipo)

            item_msg = QTableWidgetItem(msg)
            item_msg.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            self.tabella.setItem(row_idx, 1, item_msg)

            item_st = QTableWidgetItem("Attivo")
            item_st.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabella.setItem(row_idx, 2, item_st)

            self.tabella.setCellWidget(
                row_idx,
                3,
                self._pannello_azioni(
                    end_lat, end_lon, start_lat, start_lon, t1_nome, t2_nome,
                    t1_id, t2_id, allarme_id,
                ),
            )

    def _pannello_azioni(
        self,
        end_lat,
        end_lon,
        start_lat,
        start_lon,
        nome_origine,
        nome_destinazione,
        id_origine,
        id_destinazione,
        allarme_id,
    ):
        """Crea il pannello con i tre pulsanti di risoluzione di un allarme."""
        panel_azioni = QWidget()
        layout_azioni = QHBoxLayout(panel_azioni)
        layout_azioni.setContentsMargins(2, 2, 2, 2)
        layout_azioni.setSpacing(4)

        # 1. Visualizza la mappa del GAP.
        btn_mappa_gap = QPushButton("👁️ Mappa GAP")
        btn_mappa_gap.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold; font-size: 11px; padding: 4px;")
        btn_mappa_gap.clicked.connect(lambda _, e_l=end_lat, e_o=end_lon, s_l=start_lat, s_o=start_lon, n1=nome_origine, n2=nome_destinazione:
            self._al_mappa_gap(e_l, e_o, s_l, s_o, n1, n2)
        )

        # 2. Genera il raccordo GPX.
        btn_raccorda = QPushButton("🔗 Raccorda GPX")
        btn_raccorda.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; font-size: 11px; padding: 4px;")
        btn_raccorda.clicked.connect(lambda _, id1=id_origine, id2=id_destinazione, n1=nome_origine, n2=nome_destinazione: self._al_raccordo_traccia(id1, id2, n1, n2))

        # 3. Registra il trasferimento logistico.
        btn_trasferimento = QPushButton("🚢 Logistica/Mezzo")
        btn_trasferimento.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; font-size: 11px; padding: 4px;")
        btn_trasferimento.clicked.connect(lambda _, aid=allarme_id: self._al_wizard_trasferimento(aid))

        layout_azioni.addWidget(btn_mappa_gap)
        layout_azioni.addWidget(btn_raccorda)
        layout_azioni.addWidget(btn_trasferimento)
        return panel_azioni