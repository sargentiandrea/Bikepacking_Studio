"""Widget della pagina "Gestione Blocchi".

Estratto dalla Fase 2 del refactor di ``app_desktop.py``
(vedi REPORT/PIANO_REFACTOR_APP_DESKTOP.md).

Mostra l'elenco dei blocchi (macro-aree) del percorso attivo, permette di
riordinarli e salva il nuovo ordine. La lettura/scrittura su database è
delegata a ``service.blocchi_ordine_service``; il widget comunica con la
finestra principale (``parent_app``) solo tramite i suoi metodi pubblici
(``current_progetto_id``, ``esegui_audit_automatico``, ``aggiorna_tabella_tappe``,
``aggiorna_tabella_allarmi``, ``mappa_necessita_aggiornamento``).
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from service import blocchi_ordine_service


class GestoreBlocchiWidget(QWidget):
    """Pagina di gestione e riordino dei blocchi di un percorso."""

    def __init__(self, parent_app):
        super().__init__()
        self.parent_app = parent_app
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)

        lbl_titolo = QLabel("🧩 Gestore Sequenza Blocchi e Macro-Aree")
        lbl_titolo.setFont(QFont("Arial", 16, QFont.Bold))
        lbl_titolo.setStyleSheet("color: #0e639c;")

        lbl_desc = QLabel("Seleziona un blocco, usa le frecce per riordinare e premi 'Applica Nuova Sequenza' per salvare.")
        lbl_desc.setStyleSheet("color: #aaaaaa; margin-bottom: 10px;")

        layout.addWidget(lbl_titolo)
        layout.addWidget(lbl_desc)

        h_layout = QHBoxLayout()
        self.lista_blocchi = QListWidget()
        self.lista_blocchi.setStyleSheet("""
            QListWidget { background-color: #252526; border: 1px solid #3e3e42; border-radius: 8px; padding: 10px; font-size: 14px; }
            QListWidget::item { background-color: #2d2d30; color: white; margin-bottom: 5px; padding: 12px; border-radius: 4px; }
            QListWidget::item:selected { background-color: #0e639c; color: white; }
        """)
        h_layout.addWidget(self.lista_blocchi, stretch=3)

        v_btn_layout = QVBoxLayout()
        self.btn_su = QPushButton("⬆️ Sposta Su")
        self.btn_giu = QPushButton("⬇️ Sposta Giù")
        self.btn_applica = QPushButton("🔄 Applica Nuova Sequenza")

        self.btn_su.setStyleSheet("padding: 10px; font-weight: bold; background-color: #3e3e42; color: white; border-radius: 5px;")
        self.btn_giu.setStyleSheet("padding: 10px; font-weight: bold; background-color: #3e3e42; color: white; border-radius: 5px;")
        self.btn_applica.setStyleSheet("padding: 12px; background-color: #28a745; color: white; font-weight: bold; border-radius: 5px;")

        self.btn_su.clicked.connect(self.sposta_su)
        self.btn_giu.clicked.connect(self.sposta_giu)
        self.btn_applica.clicked.connect(self.applica_riordinamento)

        v_btn_layout.addWidget(self.btn_su)
        v_btn_layout.addWidget(self.btn_giu)
        v_btn_layout.addStretch()
        v_btn_layout.addWidget(self.btn_applica)

        h_layout.addLayout(v_btn_layout, stretch=1)
        layout.addLayout(h_layout)

    def carica_blocchi(self):
        self.lista_blocchi.clear()
        pid = self.parent_app.current_progetto_id
        if not pid:
            return

        for nome_blocco in blocchi_ordine_service.leggi_blocchi_ordinati(pid):
            icona = "📂" if nome_blocco == "Generale" else "📍"
            item = QListWidgetItem(f"{icona} {nome_blocco}")
            item.setData(Qt.UserRole, nome_blocco)
            self.lista_blocchi.addItem(item)

    def sposta_su(self):
        idx = self.lista_blocchi.currentRow()
        if idx > 0:
            item = self.lista_blocchi.takeItem(idx)
            self.lista_blocchi.insertItem(idx - 1, item)
            self.lista_blocchi.setCurrentRow(idx - 1)

    def sposta_giu(self):
        idx = self.lista_blocchi.currentRow()
        if idx >= 0 and idx < self.lista_blocchi.count() - 1:
            item = self.lista_blocchi.takeItem(idx)
            self.lista_blocchi.insertItem(idx + 1, item)
            self.lista_blocchi.setCurrentRow(idx + 1)

    def applica_riordinamento(self):
        pid = self.parent_app.current_progetto_id
        if not pid:
            QMessageBox.warning(self, "Attenzione", "Seleziona prima un percorso attivo!")
            return

        nuovo_ordine_blocchi = [self.lista_blocchi.item(i).data(Qt.UserRole) for i in range(self.lista_blocchi.count())]
        if not nuovo_ordine_blocchi:
            return

        blocchi_ordine_service.salva_ordine_blocchi(pid, nuovo_ordine_blocchi)

        QMessageBox.information(self, "Sequenza Salvata", "L'ordine dei blocchi è stato salvato definitivamente!")

        self.parent_app.esegui_audit_automatico()
        self.parent_app.mappa_necessita_aggiornamento = True
        self.parent_app.aggiorna_tabella_tappe()
        self.parent_app.aggiorna_tabella_allarmi()
