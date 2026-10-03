"""Finestra di gestione delle mappe regionali offline (catalogo e download).

Usa service/map_manager_service per elencare e scaricare le mappe. Non
dipende da gui/mappa.py.
"""

import os

from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMessageBox, QProgressBar, QPushButton, QVBoxLayout,
)

from service.map_manager_service import DownloadWorker, MapManagerService


class MapManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestione Mappe Regionali Offline")
        self.resize(600, 450)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<strong>Catalogo Mappe Regionali (Vettoriali OpenMapTiles):</strong>"))
        
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.lbl_description = QLabel("")
        self.lbl_description.setWordWrap(True)
        self.lbl_description.setStyleSheet("color: #94a3b8; font-size: 11px; margin: 4px 0;")
        layout.addWidget(self.lbl_description)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        btn_layout = QHBoxLayout()
        self.btn_download = QPushButton("Scarica Mappa Selezionata")
        self.btn_download.clicked.connect(self.start_download)
        btn_layout.addWidget(self.btn_download)

        self.btn_close = QPushButton("Chiudi")
        self.btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)
        
        self.list_widget.currentItemChanged.connect(self.on_item_selected)
        self.refresh_catalog()

    def refresh_catalog(self):
        self.list_widget.clear()
        catalog = MapManagerService.get_available_catalog()
        
        for item in catalog:
            status = "✅ Installata" if item["is_installed"] else "⬇️ Scaricabile"
            text = f"[{item['region']}] {item['name']} — ~{item['size_mb']} MB ({status})"
            widget_item = QListWidgetItem(text)
            widget_item.setData(32, item)
            self.list_widget.addItem(widget_item)

    def on_item_selected(self, current, previous):
        if current:
            data = current.data(32)
            self.lbl_description.setText(f"ℹ️ {data['description']}")
        else:
            self.lbl_description.setText("")

    def start_download(self):
        selected_item = self.list_widget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Attenzione", "Seleziona una regione da scaricare.")
            return

        item_data = selected_item.data(32)
        if item_data["is_installed"]:
            QMessageBox.information(self, "Info", "Questa regione è già installata nella cartella data/maps/.")
            return

        if not item_data["url"]:
            QMessageBox.warning(self, "URL Mancante", "La sorgente di download per questa specifica regione sarà collegata a breve.")
            return

        dest_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'data', 'maps', item_data["filename"]
        ))

        self.btn_download.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

        self.worker = DownloadWorker(item_data["url"], dest_path)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_download_finished)
        self.worker.start()

    def on_download_finished(self, success, message):
        self.btn_download.setEnabled(True)
        self.progress_bar.setVisible(False)
        if success:
            QMessageBox.information(self, "Successo", message)
            self.refresh_catalog()
        else:
            QMessageBox.critical(self, "Errore Download", message)
