"""Stile e helper condivisi dalle pagine di servizio dell'applicazione.

Le pagine Dogane, Trasporti, Audit, Statistiche e Clima condividono lo stesso
foglio di stile scuro e lo stesso riempimento delle tabelle. Questi helper
vivono qui per evitare di duplicarli in ogni pagina.
"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

# Foglio di stile comune a tutte le pagine di servizio.
STILE_PAGINA_SERVIZIO = """
    QLabel { font-family: Arial; color: #cccccc; }
    QTableWidget { background-color: #252526; gridline-color: #3e3e42; color: #ffffff; border: 1px solid #3e3e42; border-radius: 5px; }
    QTableWidget::item { padding: 6px; }
    QHeaderView::section { background-color: #2d2d30; color: #a93226; font-weight: bold; padding: 8px; }
    QDateEdit, QSpinBox { background-color: #3e3e42; color: #ffffff; border: 1px solid #555555; padding: 5px; }
    QPushButton { background-color: #3e3e42; color: #ffffff; border: 1px solid #555555; padding: 8px 10px; border-radius: 4px; }
    QPushButton:hover { background-color: #0e639c; border-color: #0e639c; }
    QTabWidget::pane { border: 1px solid #3e3e42; background-color: #252526; }
    QTabBar::tab { background-color: #2d2d30; color: #cccccc; padding: 8px 12px; border: 1px solid #3e3e42; }
    QTabBar::tab:selected { background-color: #0e639c; color: #ffffff; }
"""


def applica_stile_servizio(widget):
    """Applica lo stile comune a `widget` e a tutte le sue tabelle annidate."""
    widget.setStyleSheet(STILE_PAGINA_SERVIZIO)
    for tabella in widget.findChildren(QTableWidget):
        tabella.verticalHeader().setDefaultSectionSize(55)


def imposta_righe_tabella(tabella, righe):
    """Riempe `tabella` con `righe`, usando la stringa vuota per i `None`."""
    tabella.setRowCount(len(righe))
    for row_index, riga in enumerate(righe):
        for col_index, valore in enumerate(riga):
            testo = "" if valore is None else str(valore)
            tabella.setItem(row_index, col_index, QTableWidgetItem(testo))