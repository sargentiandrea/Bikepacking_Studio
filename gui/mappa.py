import os
import json
import sqlite3
import time
import uuid
import re
from contextlib import closing
import requests
import gpxpy
import gpxpy.gpx

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QListWidget, QListWidgetItem, QDialog, QProgressBar, QMessageBox,
    QFrame, QLineEdit, QComboBox, QGraphicsDropShadowEffect, QScrollArea,
    QSizePolicy, QGridLayout
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtCore import QUrl, Qt, QTimer, QThread, Signal
from PySide6.QtGui import QColor, QPainter

from service.config import BASE_DIR, DB_NAME
from service.map_manager_service import MapManagerService, DownloadWorker

GPX_DIR = os.path.join(BASE_DIR, "gpx")


class BarraSuperfici(QWidget):
    """Barra compatta che visualizza la ripartizione delle superfici BRouter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.superfici = []
        self.setMinimumHeight(22)
        self.setMaximumHeight(22)

    def imposta_superfici(self, superfici):
        self.superfici = list(superfici or [])
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        area = self.rect().adjusted(0, 0, -1, -1)

        if not self.superfici:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#3e3e42"))
            painter.drawRoundedRect(area, 5, 5)
            return

        totale = sum(max(0.0, float(voce.get("percentuale", 0))) for voce in self.superfici)
        if totale <= 0:
            return

        x = area.left()
        larghezza_rimanente = area.width()
        for indice, voce in enumerate(self.superfici):
            quota = max(0.0, float(voce.get("percentuale", 0))) / totale
            larghezza = larghezza_rimanente if indice == len(self.superfici) - 1 else round(area.width() * quota)
            if larghezza <= 0:
                continue
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(voce.get("colore", "#64748b")))
            painter.drawRect(x, area.top(), larghezza, area.height())
            x += larghezza
            larghezza_rimanente -= larghezza
        painter.end()

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


class PannelloPianificazioneWidget(QFrame):
    """Pannello fluttuante in stile Komoot / Bikemap sovrapposto alla mappa."""
    def __init__(self, parent=None, mappa_widget=None):
        super().__init__(parent)
        self.mappa_widget = mappa_widget
        self.worker_pianificazione = None
        self.punti_passaggio = []
        self.tappa_in_modifica_id = None
        self.ultima_anteprima = None
        self.firma_ultima_anteprima = None
        self.callback_worker_pianificazione = None
        self.firma_worker_pianificazione = None
        self.setFixedWidth(340)  # Imposta una larghezza fissa coerente con il layout della mappa
        self.setMaximumHeight(500)
        
        # Stile visivo generale del pannello (sfondo scuro, bordi arrotondati, font pulito)
        self.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                color: #e2e8f0;
                border-radius: 10px;
                border: 1px solid #333333;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                font-size: 12px;
            }
            QLineEdit, QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 8px 10px;
                color: #ffffff;
                font-size: 12px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #0284c7;  /* Evidenzia il bordo in azzurro quando attivo */
            }
            QLabel {
                color: #94a3b8;
                font-weight: 500;
                border: none;
                background: transparent;
            }
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 8px; background: #252525; margin: 2px; }
            QScrollBar::handle:vertical { min-height: 24px; background: #555555; border-radius: 4px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)
        
        # Applicazione di un'ombra portata per staccare visivamente il pannello dalla mappa sottostante
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        # Layout principale verticale del pannello
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        
        # --- INTESTAZIONE (Titolo + Pulsante di chiusura) ---
        header_layout = QHBoxLayout()
        lbl_title = QLabel("🗺️ Il tuo percorso")
        lbl_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        
        self.btn_chiudi_pannello = QPushButton("✕")
        self.btn_chiudi_pannello.setFixedSize(24, 24)
        self.btn_chiudi_pannello.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94a3b8;
                border: none;
                font-weight: bold;
                font-size: 14px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #333333;
                color: #ffffff;
            }
        """)
        header_layout.addWidget(self.btn_chiudi_pannello)
        layout.addLayout(header_layout)

        self.area_scorrimento = QScrollArea(self)
        self.area_scorrimento.setWidgetResizable(True)
        self.area_scorrimento.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.area_scorrimento.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        contenuto = QWidget()
        contenuto_layout = QVBoxLayout(contenuto)
        contenuto_layout.setContentsMargins(0, 0, 4, 0)
        contenuto_layout.setSpacing(12)
        contenuto_layout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        
        # --- SEZIONE PARTENZA ---
        layout_partenza = QHBoxLayout()
        layout_partenza.setSpacing(8)
        lbl_icon_a = QLabel("🟢")
        lbl_icon_a.setFixedWidth(20)
        self.input_partenza = QLineEdit()
        self.input_partenza.setPlaceholderText("Inserisci punto di partenza...")
        layout_partenza.addWidget(lbl_icon_a)
        layout_partenza.addWidget(self.input_partenza)
        contenuto_layout.addLayout(layout_partenza)

        self.contenitore_punti_passaggio = QWidget()
        self.layout_punti_passaggio = QVBoxLayout(self.contenitore_punti_passaggio)
        self.layout_punti_passaggio.setContentsMargins(0, 0, 0, 0)
        self.layout_punti_passaggio.setSpacing(8)
        contenuto_layout.addWidget(self.contenitore_punti_passaggio)

        self.btn_aggiungi_punto = QPushButton("+ Aggiungi punto di passaggio")
        self.btn_aggiungi_punto.setStyleSheet(
            "QPushButton { background: transparent; color: #38bdf8; border: 1px dashed #475569; "
            "padding: 7px; border-radius: 5px; text-align: left; } "
            "QPushButton:hover { background-color: #263746; border-color: #0284c7; }"
        )
        self.btn_aggiungi_punto.clicked.connect(self._aggiungi_punto_passaggio)
        contenuto_layout.addWidget(self.btn_aggiungi_punto)

        self.btn_waypoint_da_mappa = QPushButton("📍 Posiziona waypoint sulla mappa")
        self.btn_waypoint_da_mappa.clicked.connect(
            lambda: self.mappa_widget.attiva_modalita_interazione("add_waypoint")
        )
        contenuto_layout.addWidget(self.btn_waypoint_da_mappa)

        self.btn_rubberband = QPushButton("↗ Modifica tratta trascinando la linea")
        self.btn_rubberband.clicked.connect(
            lambda: self.mappa_widget.attiva_modalita_interazione("rubberband")
        )
        contenuto_layout.addWidget(self.btn_rubberband)
        
        # --- SEZIONE DESTINAZIONE ---
        layout_arrivo = QHBoxLayout()
        layout_arrivo.setSpacing(8)
        lbl_icon_b = QLabel("🏁")
        lbl_icon_b.setFixedWidth(20)
        self.input_destinazione = QLineEdit()
        self.input_destinazione.setPlaceholderText("Inserisci destinazione...")
        layout_arrivo.addWidget(lbl_icon_b)
        layout_arrivo.addWidget(self.input_destinazione)
        contenuto_layout.addLayout(layout_arrivo)

        lbl_superfici = QLabel("Superfici del percorso")
        lbl_superfici.setStyleSheet("color: #94a3b8; font-size: 11px; margin-top: 4px; border: none;")
        contenuto_layout.addWidget(lbl_superfici)
        self.barra_superfici = BarraSuperfici()
        contenuto_layout.addWidget(self.barra_superfici)
        self.layout_leggenda_superfici = QHBoxLayout()
        self.layout_leggenda_superfici.setContentsMargins(0, 0, 0, 0)
        self.layout_leggenda_superfici.setSpacing(8)
        contenuto_layout.addLayout(self.layout_leggenda_superfici)
        self.lbl_stato_superfici = QLabel("La ripartizione compare dopo il calcolo della rotta.")
        self.lbl_stato_superfici.setWordWrap(True)
        self.lbl_stato_superfici.setStyleSheet("font-size: 10px; color: #94a3b8;")
        contenuto_layout.addWidget(self.lbl_stato_superfici)

        lbl_dettagli = QLabel("Dettagli tecnici")
        lbl_dettagli.setStyleSheet("color: #94a3b8; font-size: 11px; margin-top: 4px; border: none;")
        contenuto_layout.addWidget(lbl_dettagli)
        dettagli_layout = QGridLayout()
        dettagli_layout.setContentsMargins(0, 0, 0, 0)
        dettagli_layout.setHorizontalSpacing(8)
        dettagli_layout.setVerticalSpacing(4)
        self.lbl_velocita_media = QLabel("Velocità media stimata: --")
        self.lbl_altitudine_massima = QLabel("Altitudine massima: --")
        self.lbl_altitudine_minima = QLabel("Altitudine minima: --")
        self.lbl_distanza_totale = QLabel("Distanza totale: --")
        dettagli_layout.addWidget(self.lbl_velocita_media, 0, 0)
        dettagli_layout.addWidget(self.lbl_altitudine_massima, 0, 1)
        dettagli_layout.addWidget(self.lbl_altitudine_minima, 1, 0)
        dettagli_layout.addWidget(self.lbl_distanza_totale, 1, 1)
        contenuto_layout.addLayout(dettagli_layout)
        
        # --- PROFILO DI INSTRADAMENTO ---
        lbl_profilo = QLabel("Profilo di instradamento")
        lbl_profilo.setStyleSheet("color: #94a3b8; font-size: 11px; margin-top: 4px; border: none;")
        contenuto_layout.addWidget(lbl_profilo)
        
        self.combo_profilo = QComboBox()
        self.combo_profilo.addItems(["🚲 Gravel / Viaggio", "🛣️ Strada", "🚵 MTB", "⚖️ Equilibrato"])
        contenuto_layout.addWidget(self.combo_profilo)
        
        # --- PULSANTE DI SALVATAGGIO / AZIONE ---
        self.btn_salva = QPushButton("Salva Percorso")
        self.btn_salva.setStyleSheet("""
            QPushButton {
                background-color: #0284c7;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0369a1;  /* Colore più scuro al passaggio del mouse */
            }
        """)
        self.btn_salva.clicked.connect(self._gestisci_salvataggio_percorso)
        contenuto_layout.addWidget(self.btn_salva)
        contenuto_layout.addStretch()
        self.area_scorrimento.setWidget(contenuto)
        layout.addWidget(self.area_scorrimento)
        self._adatta_altezza_al_contenuto()

    def _firma_pianificazione(self):
        """Crea una chiave per sapere se l'anteprima corrisponde ai campi attuali."""
        return (
            getattr(getattr(self.mappa_widget, "parent_app", None), "current_progetto_id", None),
            self.input_partenza.text().strip(),
            tuple(punto["input"].text().strip() for punto in self.punti_passaggio),
            self.input_destinazione.text().strip(),
            self.combo_profilo.currentText(),
            self.tappa_in_modifica_id,
        )

    def _valida_pianificazione(self, mostra_dialogo=True):
        """Controlla progetto e luoghi, restituendo i dati nell'ordine della rotta."""
        progetto = getattr(getattr(self.mappa_widget, "parent_app", None), "current_progetto_id", None)
        partenza = self.input_partenza.text().strip()
        destinazione = self.input_destinazione.text().strip()
        punti = [punto["input"].text().strip() for punto in self.punti_passaggio]

        messaggio = None
        titolo = "Pianificazione non valida"
        if not progetto:
            titolo, messaggio = "Percorso richiesto", "Apri o crea un percorso dalla Dashboard prima di pianificare."
        elif not partenza or not destinazione:
            titolo, messaggio = "Campi incompleti", "Inserisci sia partenza che destinazione."
        elif any(not punto for punto in punti):
            titolo, messaggio = "Punto incompleto", "Completa oppure rimuovi ogni punto di passaggio."

        if messaggio:
            if mostra_dialogo:
                QMessageBox.warning(self, titolo, messaggio)
            else:
                self.lbl_stato_superfici.setText(messaggio)
            return None
        return progetto, partenza, punti, destinazione

    def _avvia_worker_rotta(self, callback, etichetta_pulsante, mostra_dialogo=True):
        """Avvia il calcolo della rotta in background senza bloccare la mappa."""
        dati = self._valida_pianificazione(mostra_dialogo=mostra_dialogo)
        if not dati:
            return False

        progetto, partenza, punti, destinazione = dati
        firma = self._firma_pianificazione()
        self.btn_salva.setEnabled(False)
        self.btn_salva.setText(etichetta_pulsante)
        worker = PianificazionePercorsoWorker(
            progetto,
            partenza,
            destinazione,
            self.combo_profilo.currentText(),
            punti,
            tappa_id=self.tappa_in_modifica_id,
            parent=self,
        )
        self.callback_worker_pianificazione = callback
        self.firma_worker_pianificazione = firma
        worker.completato.connect(self._completamento_worker_pianificazione)
        worker.finished.connect(self._worker_pianificazione_terminato)
        self.worker_pianificazione = worker
        worker.start()
        return True

    def _completamento_worker_pianificazione(self, riuscito, risultato, errore):
        """Riporta il risultato del thread al callback Qt nel thread dell'interfaccia."""
        if self.callback_worker_pianificazione:
            self.callback_worker_pianificazione(
                riuscito,
                risultato,
                errore,
                self.firma_worker_pianificazione,
            )

    def _worker_pianificazione_terminato(self):
        self.btn_salva.setEnabled(True)
        self.btn_salva.setText("Aggiorna tappa" if self.tappa_in_modifica_id else "Salva Percorso")

    def _ricalcola_anteprima(self):
        """Ricalcola soltanto l'anteprima, senza scrivere nel database."""
        self._avvia_worker_rotta(
            self._anteprima_rotta_completata,
            "Ricalcolo anteprima...",
            mostra_dialogo=False,
        )

    def _anteprima_rotta_completata(self, riuscito, risultato, errore, firma):
        self.btn_salva.setText("Aggiorna tappa" if self.tappa_in_modifica_id else "Salva Percorso")
        if not riuscito:
            self.lbl_stato_superfici.setText(errore)
            return
        if firma != self._firma_pianificazione():
            return

        self.ultima_anteprima = risultato
        self.firma_ultima_anteprima = firma
        self._aggiorna_dettagli_rotta(risultato.get("statistiche"))
        self.mappa_widget.mostra_anteprima_percorso(risultato["coordinate"])
        self.lbl_stato_superfici.setText("Anteprima aggiornata; premi il pulsante per salvare la tappa.")

    def _aggiungi_waypoint_da_coordinate(self, latitudine, longitudine):
        """Inserisce nel form un punto ricevuto dalla mappa e aggiorna l'anteprima."""
        punto_vuoto = next((punto for punto in self.punti_passaggio if not punto["input"].text().strip()), None)
        if punto_vuoto is None:
            self._aggiungi_punto_passaggio()
            punto_vuoto = self.punti_passaggio[-1]
        punto_vuoto["input"].setText(f"{latitudine:.6f}, {longitudine:.6f}")
        self._ricalcola_anteprima()

    def _prepara_modifica_tappa(self, tappa_id, latitudine, longitudine):
        """Carica gli estremi della tappa esistente e crea una bozza rubber-band."""
        finestra_principale = getattr(self.mappa_widget, "parent_app", None)
        progetto = getattr(finestra_principale, "current_progetto_id", None)
        try:
            with sqlite3.connect(DB_NAME, timeout=15.0) as conn:
                riga = conn.execute(
                    "SELECT nome_file FROM tappe WHERE id = ? AND id_progetto = ?",
                    (tappa_id, progetto),
                ).fetchone()
            if not riga or not riga[0]:
                raise ValueError("La tappa selezionata non è più presente nel progetto attivo.")

            percorso_gpx = os.path.join(GPX_DIR, os.path.basename(riga[0]))
            with open(percorso_gpx, "r", encoding="utf-8", errors="ignore") as file_gpx:
                traccia = gpxpy.parse(file_gpx)
            coordinate = [
                (punto.latitude, punto.longitude)
                for track in traccia.tracks
                for segmento in track.segments
                for punto in segmento.points
            ]
            if len(coordinate) < 2:
                raise ValueError("La tappa non contiene abbastanza coordinate per essere ricalcolata.")

            self.input_partenza.setText(f"{coordinate[0][0]:.6f}, {coordinate[0][1]:.6f}")
            self.input_destinazione.setText(f"{coordinate[-1][0]:.6f}, {coordinate[-1][1]:.6f}")
            while self.punti_passaggio:
                self._rimuovi_punto_passaggio(self.punti_passaggio[-1]["widget"])
            self.tappa_in_modifica_id = tappa_id
            self.btn_salva.setText("Aggiorna tappa")
            self._aggiungi_waypoint_da_coordinate(latitudine, longitudine)
        except (OSError, sqlite3.Error, ValueError) as errore:
            QMessageBox.warning(self, "Modifica tratta non riuscita", str(errore))

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._adatta_altezza_al_contenuto)

    def _adatta_altezza_al_contenuto(self):
        """Ridimensiona il pannello sul contenuto rispettando il limite scrollabile."""
        contenuto = self.area_scorrimento.widget()
        if contenuto:
            self.layout_punti_passaggio.invalidate()
            self.layout_punti_passaggio.activate()
            self.contenitore_punti_passaggio.updateGeometry()
            if contenuto.layout():
                contenuto.layout().invalidate()
                contenuto.layout().activate()
            self.area_scorrimento.updateGeometry()
            contenuto.updateGeometry()
            contenuto.adjustSize()

        layout = self.layout()
        margini = layout.contentsMargins()
        altezza_intestazione = layout.itemAt(0).sizeHint().height()
        spazio_fisso = margini.top() + margini.bottom() + layout.spacing() + altezza_intestazione + 4
        altezza_massima_pannello = self.maximumHeight()
        contenitore = self.parentWidget()
        if contenitore and contenitore.isVisible() and contenitore.height() > 0:
            altezza_massima_pannello = min(
                altezza_massima_pannello,
                max(spazio_fisso + 80, contenitore.height() - 32),
            )

        altezza_scroll = min(
            contenuto.sizeHint().height() if contenuto else 0,
            max(80, altezza_massima_pannello - spazio_fisso),
        )
        self.area_scorrimento.setFixedHeight(altezza_scroll)
        self.adjustSize()
        self.updateGeometry()

    def _aggiungi_punto_passaggio(self):
        """Aggiunge un campo intermedio prima della destinazione."""
        indice = len(self.punti_passaggio)
        etichetta = self._etichetta_punto(indice)
        riga = QWidget(self.contenitore_punti_passaggio)
        riga_layout = QHBoxLayout(riga)
        riga_layout.setContentsMargins(0, 0, 0, 0)
        riga_layout.setSpacing(8)

        lbl_punto = QLabel(etichetta)
        lbl_punto.setFixedWidth(20)
        lbl_punto.setAlignment(Qt.AlignCenter)
        lbl_punto.setStyleSheet("color: #38bdf8; font-weight: bold;")

        campo = QLineEdit()
        campo.setPlaceholderText(f"Punto di passaggio {etichetta}...")

        btn_rimuovi = QPushButton("−")
        btn_rimuovi.setFixedSize(28, 28)
        btn_rimuovi.setToolTip("Rimuovi punto di passaggio")
        btn_rimuovi.clicked.connect(lambda: self._rimuovi_punto_passaggio(riga))

        riga_layout.addWidget(lbl_punto)
        riga_layout.addWidget(campo, stretch=1)
        riga_layout.addWidget(btn_rimuovi)
        self.layout_punti_passaggio.addWidget(riga)
        self.punti_passaggio.append({"widget": riga, "input": campo, "label": lbl_punto})
        self._rinumera_punti_passaggio()
        QTimer.singleShot(0, self._adatta_altezza_al_contenuto)

    def _rimuovi_punto_passaggio(self, riga):
        """Rimuove il campo selezionato e aggiorna le etichette successive."""
        self.punti_passaggio = [
            punto for punto in self.punti_passaggio if punto["widget"] is not riga
        ]
        self.layout_punti_passaggio.removeWidget(riga)
        riga.deleteLater()
        self._rinumera_punti_passaggio()
        QTimer.singleShot(0, self._adatta_altezza_al_contenuto)

    def _rinumera_punti_passaggio(self):
        """Riassegna le lettere A, B, ..., Z, AA, AB ai punti visibili."""
        for indice, punto in enumerate(self.punti_passaggio):
            etichetta = self._etichetta_punto(indice)
            punto["label"].setText(etichetta)
            punto["input"].setPlaceholderText(f"Punto di passaggio {etichetta}...")

    def _aggiorna_dettagli_rotta(self, statistiche):
        """Aggiorna barra superfici, legenda e KPI della rotta calcolata."""
        statistiche = statistiche or {}
        superfici = statistiche.get("superfici", [])
        self.barra_superfici.imposta_superfici(superfici)

        while self.layout_leggenda_superfici.count():
            elemento = self.layout_leggenda_superfici.takeAt(0)
            if elemento.widget():
                elemento.widget().deleteLater()

        for superficie in superfici:
            legenda = QLabel(f"{superficie['categoria']} {superficie['percentuale']:.0f}%")
            legenda.setStyleSheet(f"font-size: 9px; color: {superficie['colore']};")
            self.layout_leggenda_superfici.addWidget(legenda)
        self.layout_leggenda_superfici.addStretch()

        if superfici:
            non_specificata = next(
                (voce["percentuale"] for voce in superfici if voce["categoria"] == "Non specificata"),
                0,
            )
            if non_specificata >= 99:
                self.lbl_stato_superfici.setText("Il servizio di routing non ha fornito tag di superficie per questa rotta.")
            else:
                self.lbl_stato_superfici.setText("Stima da tag stradali OpenStreetMap restituiti da BRouter.")
        else:
            self.lbl_stato_superfici.setText("Superfici non disponibili.")

        velocita = statistiche.get("velocita_media_kmh")
        quota_min = statistiche.get("altitudine_min_m")
        quota_max = statistiche.get("altitudine_max_m")
        distanza = statistiche.get("distanza_km")
        self.lbl_velocita_media.setText(
            f"Velocità media stimata: {velocita:.1f} km/h" if velocita is not None
            else "Velocità media stimata: --"
        )
        self.lbl_altitudine_massima.setText(
            f"Altitudine massima: {quota_max} m" if quota_max is not None
            else "Altitudine massima: --"
        )
        self.lbl_altitudine_minima.setText(
            f"Altitudine minima: {quota_min} m" if quota_min is not None
            else "Altitudine minima: --"
        )
        self.lbl_distanza_totale.setText(
            f"Distanza totale: {distanza:.1f} km" if distanza is not None
            else "Distanza totale: --"
        )

        self._adatta_altezza_al_contenuto()

    @staticmethod
    def _etichetta_punto(indice):
        """Converte un indice zero-based nella notazione alfabetica da foglio di calcolo."""
        risultato = ""
        valore = indice + 1
        while valore:
            valore, resto = divmod(valore - 1, 26)
            risultato = chr(ord("A") + resto) + risultato
        return risultato

    def _gestisci_salvataggio_percorso(self):
        """Salva l'anteprima corrente oppure calcola la rotta prima di salvarla."""
        dati = self._valida_pianificazione()
        if not dati:
            return
        firma = self._firma_pianificazione()
        if self.ultima_anteprima and self.firma_ultima_anteprima == firma:
            self._salvataggio_percorso_completato(
                True,
                dict(self.ultima_anteprima),
                "",
                firma,
            )
            return

        self._avvia_worker_rotta(
            self._salvataggio_percorso_completato,
            "Ricerca e calcolo percorso...",
            mostra_dialogo=True,
        )

    def _salvataggio_percorso_completato(self, riuscito, risultato, errore, firma=None):
        """Scrive la traccia GPX e i relativi dati solo dopo un routing valido."""
        self.btn_salva.setEnabled(True)
        self.btn_salva.setText("Aggiorna tappa" if self.tappa_in_modifica_id else "Salva Percorso")

        if not riuscito:
            QMessageBox.warning(self, "Pianificazione non riuscita", errore)
            return
        if firma is not None and firma != self._firma_pianificazione():
            self.lbl_stato_superfici.setText("I campi sono cambiati durante il routing: ricalcola l'anteprima.")
            return

        finestra_principale = getattr(self.mappa_widget, "parent_app", None)
        id_progetto_corrente = getattr(finestra_principale, "current_progetto_id", None)
        if id_progetto_corrente != risultato["id_progetto"]:
            QMessageBox.warning(
                self,
                "Progetto cambiato",
                "Il progetto attivo è cambiato durante il calcolo. La traccia non è stata salvata.",
            )
            return

        if risultato.get("tappa_id") != self.tappa_in_modifica_id:
            QMessageBox.warning(self, "Tappa cambiata", "La tappa selezionata è cambiata durante il routing.")
            return

        partenza = risultato["partenza"]
        destinazione = risultato["destinazione"]
        coordinate = risultato["coordinate"]
        self._aggiorna_dettagli_rotta(risultato.get("statistiche"))
        distanza_km = sum(
            _distanza_haversine_km(coordinate[index][0], coordinate[index][1],
                                   coordinate[index + 1][0], coordinate[index + 1][1])
            for index in range(len(coordinate) - 1)
        )
        if distanza_km <= 0:
            QMessageBox.warning(self, "Traccia non valida", "Il percorso calcolato non contiene una distanza valida.")
            return

        conn = None
        file_gpx = None
        file_gpx_precedente = None
        stato_precedente = "ATTIVA"
        tappa_id = risultato.get("tappa_id")
        try:
            os.makedirs(GPX_DIR, exist_ok=True)
            conn = sqlite3.connect(DB_NAME, timeout=30.0)
            with closing(conn):
                with conn:
                    cursor = conn.cursor()
                    if tappa_id is not None:
                        cursor.execute(
                            "SELECT nome_file, stato FROM tappe WHERE id = ? AND id_progetto = ?",
                            (tappa_id, id_progetto_corrente),
                        )
                        tappa_esistente = cursor.fetchone()
                        if not tappa_esistente:
                            raise ValueError("La tappa da aggiornare non è più presente nel progetto.")
                        file_gpx_precedente = tappa_esistente[0]
                        stato_precedente = tappa_esistente[1] or "ATTIVA"
                    else:
                        cursor.execute(
                            "SELECT COALESCE(MAX(sequenza), 0) + 1 FROM tappe WHERE id_progetto = ?",
                            (id_progetto_corrente,),
                        )
                        sequenza = cursor.fetchone()[0]

                    nome_file = f"Pianificato_{id_progetto_corrente}_{uuid.uuid4().hex[:10]}.gpx"
                    file_gpx = os.path.join(GPX_DIR, nome_file)

                    traccia = gpxpy.gpx.GPX()
                    traccia.creator = "Bikepacking Studio"
                    segmento = gpxpy.gpx.GPXTrackSegment()
                    for punto in coordinate:
                        latitudine, longitudine = punto[:2]
                        elevazione = float(punto[2]) if len(punto) > 2 else None
                        segmento.points.append(
                            gpxpy.gpx.GPXTrackPoint(latitudine, longitudine, elevation=elevazione)
                        )
                    track = gpxpy.gpx.GPXTrack(name=f"{partenza} - {destinazione}")
                    track.segments.append(segmento)
                    traccia.tracks.append(track)

                    with open(file_gpx, "w", encoding="utf-8") as file:
                        file.write(traccia.to_xml())

                    valori_rotta = (
                        nome_file,
                        coordinate[0][0],
                        coordinate[0][1],
                        coordinate[-1][0],
                        coordinate[-1][1],
                        round(distanza_km, 2),
                    )
                    if tappa_id is not None:
                        cursor.execute(
                            """
                            UPDATE tappe SET nome_file = ?, start_lat = ?, start_lon = ?,
                                end_lat = ?, end_lon = ?, distanza_km = ?, stato = ?
                            WHERE id = ? AND id_progetto = ?
                            """,
                            (*valori_rotta, stato_precedente, tappa_id, id_progetto_corrente),
                        )
                        if cursor.rowcount != 1:
                            raise ValueError("La tappa non è stata aggiornata; verifica il progetto attivo.")
                    else:
                        cursor.execute(
                            """
                            INSERT INTO tappe (
                                id_progetto, sequenza, blocco, nome_file,
                                start_lat, start_lon, end_lat, end_lon,
                                distanza_km, stato
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'ATTIVA')
                            """,
                            (
                                id_progetto_corrente,
                                sequenza,
                                "Pianificato",
                                *valori_rotta,
                            ),
                        )

            if file_gpx_precedente:
                percorso_precedente = os.path.join(GPX_DIR, os.path.basename(file_gpx_precedente))
                if os.path.isfile(percorso_precedente):
                    try:
                        os.remove(percorso_precedente)
                    except OSError as errore_file:
                        print(f"Nota: non è stato possibile rimuovere il GPX precedente: {errore_file}")

            if hasattr(finestra_principale, "esegui_audit_automatico"):
                finestra_principale.esegui_audit_automatico()
            if hasattr(finestra_principale, "aggiorna_tabella_allarmi"):
                finestra_principale.aggiorna_tabella_allarmi()
            if hasattr(finestra_principale, "page_dashboard"):
                finestra_principale.page_dashboard.aggiorna_tabella_tappe()
            finestra_principale.mappa_necessita_aggiornamento = True
            self.tappa_in_modifica_id = None
            self.ultima_anteprima = None
            self.firma_ultima_anteprima = None
            self.btn_salva.setText("Salva Percorso")
            self.mappa_widget.ultimo_progetto_id_caricato = None
            self.mappa_widget.rigenera_mappa(id_progetto_corrente, DB_NAME, force=True)

            QMessageBox.information(
                self,
                "Percorso salvato",
                f"La tappa è stata {'aggiornata' if tappa_id is not None else 'aggiunta'} al progetto. "
                f"Distanza: {distanza_km:.1f} km.",
            )
        except Exception as errore_salvataggio:
            if file_gpx and os.path.exists(file_gpx):
                try:
                    os.remove(file_gpx)
                except OSError:
                    pass
            QMessageBox.critical(
                self,
                "Errore di salvataggio",
                f"Il percorso non è stato salvato nel database: {errore_salvataggio}",
            )

class MappaWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(None)
        self.parent_app = parent
        self.mappa_worker = None
        self.ultimo_progetto_id_caricato = None
        self._ultimo_evento_mappa_id = 0
        self._poll_interazioni_timer = QTimer(self)
        self._poll_interazioni_timer.setInterval(300)
        self._poll_interazioni_timer.timeout.connect(self._leggi_interazioni_mappa)
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Toolbar superiore
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(10, 8, 10, 8)
        
        btn_manage_maps = QPushButton("🗺️ Gestisci Mappe Offline")
        btn_manage_maps.setStyleSheet("background-color: #262626; color: #e2e8f0; border: 1px solid #404040; padding: 6px 12px; border-radius: 4px; font-weight: 500;")
        btn_manage_maps.clicked.connect(self.open_map_manager)
        toolbar.addWidget(btn_manage_maps)

        btn_refresh = QPushButton("🔄 Ricarica Mappa")
        btn_refresh.setStyleSheet("background-color: #262626; color: #e2e8f0; border: 1px solid #404040; padding: 6px 12px; border-radius: 4px; font-weight: 500;")
        btn_refresh.clicked.connect(self.reload_map)
        toolbar.addWidget(btn_refresh)

        self.btn_toggle_pannello = QPushButton("🗂️ Pianificatore")
        self.btn_toggle_pannello.setStyleSheet("background-color: #0284c7; color: white; border: none; padding: 6px 12px; border-radius: 4px; font-weight: bold;")
        self.btn_toggle_pannello.clicked.connect(self.toggle_pannello)
        toolbar.addWidget(self.btn_toggle_pannello)

        toolbar.addStretch()
        main_layout.addLayout(toolbar)

        # Contenitore centrale con mappa e pannello sovrapposto
        container_mappa = QWidget(self)
        layout_container = QVBoxLayout(container_mappa)
        layout_container.setContentsMargins(0, 0, 0, 0)
        
        self.web_view = QWebEngineView(container_mappa)
        self.web_view.setUrl("http://127.0.0.1:8080/map")
        self.web_view.page().featurePermissionRequested.connect(self._gestisci_permessi_gps)
        self.web_view.loadFinished.connect(self._pagina_mappa_caricata)
        layout_container.addWidget(self.web_view)

        # Creazione del pannello fluttuante sovrapposto
        self.pannello_pianificazione = PannelloPianificazioneWidget(
            container_mappa,
            mappa_widget=self,
        )
        self.pannello_pianificazione.move(16, 16)
        self.pannello_pianificazione.raise_() 
        self.pannello_pianificazione.btn_chiudi_pannello.clicked.connect(self.toggle_pannello)

        main_layout.addWidget(container_mappa)

    def _gestisci_permessi_gps(self, url, feature):
        feature_enum = getattr(QWebEnginePage, "Feature", None)
        permission_feature = getattr(feature_enum, "Geolocation", None)
        if permission_feature is None:
            permission_feature = getattr(QWebEnginePage, "Geolocation", None)
        if permission_feature is None or feature != permission_feature:
            return

        policy_enum = getattr(QWebEnginePage, "PermissionPolicy", None)
        granted_policy = getattr(policy_enum, "PermissionGrantedByUser", None)
        if granted_policy is None:
            granted_policy = getattr(QWebEnginePage, "PermissionGrantedByUser", None)
        if granted_policy is None:
            return

        self.web_view.page().setFeaturePermission(url, feature, granted_policy)
        print(f"🛰️ Permesso di geolocalizzazione GPS concesso con successo per: {url.toString()}")

    def _pagina_mappa_caricata(self, caricata):
        if caricata and self.isVisible():
            self._ridimensiona_mappa()

    def _ridimensiona_mappa(self):
        self.web_view.page().runJavaScript(
            "if(typeof map !== 'undefined' && map) map.resize();"
        )

    def attiva_modalita_interazione(self, modalita):
        """Attiva il click waypoint o il trascinamento di una tappa sulla mappa."""
        id_progetto = getattr(self.parent_app, "current_progetto_id", None)
        if not id_progetto:
            QMessageBox.information(self, "Percorso richiesto", "Apri un percorso prima di interagire con la rotta.")
            return

        payload_modalita = json.dumps(modalita)
        self.web_view.page().runJavaScript(
            "if(window.impostaModalitaInterazioneMappa) "
            f"window.impostaModalitaInterazioneMappa({payload_modalita}, {int(id_progetto)});"
        )
        self._poll_interazioni_timer.start()
        self.pannello_pianificazione.lbl_stato_superfici.setText(
            "Clicca sulla mappa per posizionare il punto. Esc disattiva la modalità."
            if modalita == "add_waypoint"
            else "Trascina una tappa esistente verso la nuova strada."
        )

    def _leggi_interazioni_mappa(self):
        """Preleva gli eventi Flask mentre è attiva un'interazione esplicita."""
        try:
            risposta = requests.get(
                "http://127.0.0.1:8080/api/map-interactions",
                params={"after": self._ultimo_evento_mappa_id},
                timeout=0.4,
            )
            risposta.raise_for_status()
            eventi = risposta.json().get("events", [])
        except (requests.RequestException, ValueError) as errore:
            print(f"Polling interazioni mappa temporaneamente non disponibile: {errore}")
            return

        id_progetto = getattr(self.parent_app, "current_progetto_id", None)
        for evento in eventi:
            self._ultimo_evento_mappa_id = max(self._ultimo_evento_mappa_id, evento.get("id", 0))
            if evento.get("project_id") != id_progetto:
                continue
            if evento.get("action") == "add_waypoint":
                self.pannello_pianificazione._aggiungi_waypoint_da_coordinate(
                    evento["lat"], evento["lon"]
                )
            elif evento.get("action") == "rubberband_waypoint":
                self.pannello_pianificazione._prepara_modifica_tappa(
                    evento["tappa_id"], evento["lat"], evento["lon"]
                )
            elif evento.get("action") == "cancel_interaction":
                self.web_view.page().runJavaScript(
                    "if(window.impostaModalitaInterazioneMappa) "
                    f"window.impostaModalitaInterazioneMappa(null, {int(id_progetto_corrente)});"
                )
                self.pannello_pianificazione.lbl_stato_superfici.setText("Modalità mappa disattivata.")
            self._poll_interazioni_timer.stop()

    def mostra_anteprima_percorso(self, coordinate):
        """Mostra la rotta calcolata in un layer temporaneo, senza scriverla nel DB."""
        geojson = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[punto[1], punto[0]] for punto in coordinate],
                },
                "properties": {"tipo": "anteprima_pianificazione"},
            }],
        }
        self.web_view.page().runJavaScript(
            f"if(window.aggiornaAnteprimaPercorso) window.aggiornaAnteprimaPercorso({json.dumps(geojson)});"
        )

    def cancella_anteprima_percorso(self):
        self.web_view.page().runJavaScript(
            "if(window.aggiornaAnteprimaPercorso) "
            "window.aggiornaAnteprimaPercorso({type:'FeatureCollection',features:[]});"
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "pannello_pianificazione"):
            QTimer.singleShot(0, self.pannello_pianificazione._adatta_altezza_al_contenuto)

    def _imposta_pagina_sospesa(self, sospesa):
        page = self.web_view.page()
        lifecycle_enum = getattr(QWebEnginePage, "LifecycleState", None)
        lifecycle_state = getattr(lifecycle_enum, "Frozen" if sospesa else "Active", None)
        set_lifecycle_state = getattr(page, "setLifecycleState", None)
        get_lifecycle_state = getattr(page, "lifecycleState", None)
        if lifecycle_state is None or not callable(set_lifecycle_state) or not callable(get_lifecycle_state):
            return
        if get_lifecycle_state() != lifecycle_state:
            set_lifecycle_state(lifecycle_state)

    def hideEvent(self, event):
        super().hideEvent(event)
        QTimer.singleShot(
            0,
            lambda: self._imposta_pagina_sospesa(True) if not self.isVisible() else None
        )

    def toggle_pannello(self):
        if self.pannello_pianificazione.isVisible():
            self.pannello_pianificazione.hide()
            self.btn_toggle_pannello.setText("🗂️ Apri Pianificatore")
        else:
            self.pannello_pianificazione.show()
            self.pannello_pianificazione.raise_()
            self.btn_toggle_pannello.setText("🗂️ Pianificatore")

    def reload_map(self):
        finestra_principale = self.window()
        p_id = getattr(finestra_principale, 'current_progetto_id', None)
        if p_id:
            from service.config import DB_NAME
            self.rigenera_mappa(p_id, DB_NAME, force=True)
        else:
            vuoto = {"type": "FeatureCollection", "features": []}
            js_code = f"if(window.aggiornaMappaGeoJSON) {{ window.aggiornaMappaGeoJSON({json.dumps(vuoto)}); }}"
            self.web_view.page().runJavaScript(js_code)

    def showEvent(self, event):
        super().showEvent(event)
        self._imposta_pagina_sospesa(False)
        if hasattr(self, 'pannello_pianificazione'):
            QTimer.singleShot(0, self.pannello_pianificazione._adatta_altezza_al_contenuto)
            self.pannello_pianificazione.hide()
            
        finestra_principale = self.window()
        if finestra_principale and hasattr(finestra_principale, 'current_progetto_id'):
            p_id = finestra_principale.current_progetto_id
            if p_id:
                print(f"🚀 Mappa aperta. Avvio caricamento asincrono per percorso ID: {p_id}")
                from service.config import DB_NAME
                QTimer.singleShot(100, lambda: self.rigenera_mappa(p_id, DB_NAME, force=True))
                QTimer.singleShot(400, lambda: self.pannello_pianificazione.show() if hasattr(self, 'pannello_pianificazione') else None)
                QTimer.singleShot(500, lambda: self.web_view.setZoomFactor(1.0))
                return
                
        QTimer.singleShot(100, lambda: self.pannello_pianificazione.show() if hasattr(self, 'pannello_pianificazione') else None)
        QTimer.singleShot(0, self._ridimensiona_mappa)
        QTimer.singleShot(300, lambda: self.web_view.setZoomFactor(1.0))

    def rigenera_mappa(self, current_progetto_id, db_name, force=False, mappa_necessita_aggiornamento=True):
        # Se l'utente esce dal percorso o non c'è un progetto attivo, puliamo lo schermo
        if not current_progetto_id:
            # Resettiamo la memoria del flag della cache
            if hasattr(self, 'ultimo_progetto_id_caricato'):
                self.ultimo_progetto_id_caricato = None
            vuoto = {"type": "FeatureCollection", "features": []}
            try:
                requests.post("http://127.0.0.1:8080/api/set-gpx-data", json=vuoto, timeout=2)
            except Exception:
                pass
            
            js_code = """
                if(window.aggiornaMappaGeoJSON) {
                    window.aggiornaMappaGeoJSON({'type': 'FeatureCollection', 'features': []});
                }
                if(window.centraMappaSuGpsORoma) window.centraMappaSuGpsORoma();
            """
            self.web_view.page().runJavaScript(js_code)
            return False

        # --- PROTEZIONE CACHE INTELLIGENTE ---
        # Evita di ricalcolare inutilmente migliaia di punti se il percorso è lo stesso di prima
        if hasattr(self, 'ultimo_progetto_id_caricato') and self.ultimo_progetto_id_caricato == current_progetto_id and not force:
            print(f"ℹ️ Cache Mappa: Il percorso ID {current_progetto_id} è già presente. Calcolo in background saltato.")
            return True

        if self.mappa_worker and self.mappa_worker.isRunning():
            self.mappa_worker.terminate()
            self.mappa_worker.wait()

        # RADDRIZZATO: Rimosso 'const ls' che mandava in crash il secondo tentativo di caricamento
        js_accendi = "if(document.getElementById('loading-screen')) { document.getElementById('loading-screen').style.display = 'flex'; }"
        self.web_view.page().runJavaScript(js_accendi)

        # Salviamo l'ID corrente come ultimo caricato
        self.ultimo_progetto_id_caricato = current_progetto_id

        self.mappa_worker = WorkerCaricamentoMappa(current_progetto_id, db_name)
        self.mappa_worker.elaborazione_completata.connect(self._fine_caricamento_asincrono)
        self.mappa_worker.start()
        return True
    
    def _fine_caricamento_asincrono(self, geojson_payload):
        import json
        import requests
        try:
            requests.post("http://127.0.0.1:8080/api/set-gpx-data", json=geojson_payload, timeout=10)
        except Exception as e:
            print(f"Nota: Sincronizzazione Flask in background bypassata: {e}")

        stringa_geojson = json.dumps(geojson_payload)
        js_code = f"if(window.aggiornaMappaGeoJSON) {{ window.aggiornaMappaGeoJSON({stringa_geojson}); }}"
        self.web_view.page().runJavaScript(js_code)
        print("✅ Caricamento asincrono completato ed iniettato con successo.")

    def open_map_manager(self):
        dialog = MapManagerDialog(self)
        dialog.exec()
        self.reload_map()


def _distanza_haversine_km(lat1, lon1, lat2, lon2):
    """Restituisce la distanza in linea d'aria tra due coordinate, in km."""
    from math import asin, cos, radians, sin, sqrt

    raggio_terra_km = 6371.0
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    a = sin(delta_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(delta_lon / 2) ** 2
    return 2 * raggio_terra_km * asin(sqrt(a))


class PianificazionePercorsoWorker(QThread):
    """Geocodifica partenza e arrivo e richiede a BRouter il tracciato GPX."""

    completato = Signal(bool, dict, str)

    def __init__(self, id_progetto, partenza, destinazione, profilo, punti_passaggio=None, parent=None, tappa_id=None):
        super().__init__(parent)
        self.id_progetto = id_progetto
        self.partenza = partenza
        self.destinazione = destinazione
        self.profilo = profilo
        self.punti_passaggio = list(punti_passaggio or [])
        self.tappa_id = tappa_id

    def _geocodifica(self, luogo, sessione):
        coordinate = re.fullmatch(
            r"\s*([-+]?\d+(?:\.\d+)?)\s*[,;]\s*([-+]?\d+(?:\.\d+)?)\s*",
            luogo,
        )
        if coordinate:
            latitudine, longitudine = map(float, coordinate.groups())
            if -90 <= latitudine <= 90 and -180 <= longitudine <= 180:
                return latitudine, longitudine
            raise ValueError(f"Coordinate fuori intervallo: '{luogo}'.")

        risposta = sessione.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": luogo, "format": "jsonv2", "limit": 1},
            headers={
                "User-Agent": "BikepackingStudioApp/2.0",
                "Accept-Language": "it",
            },
            timeout=12,
        )
        risposta.raise_for_status()
        risultati = risposta.json()
        if not risultati:
            raise ValueError(f"Non trovo una posizione per '{luogo}'. Prova a specificare meglio il luogo.")
        return float(risultati[0]["lat"]), float(risultati[0]["lon"])

    def _profilo_brouter(self):
        if "strada" in self.profilo.casefold():
            return "fastbike"
        return "trekking"

    def run(self):
        sessione = requests.Session()
        try:
            luoghi = [self.partenza, *self.punti_passaggio, self.destinazione]
            coordinate_luoghi = []
            for indice, luogo in enumerate(luoghi):
                if indice:
                    time.sleep(1)
                coordinate_luoghi.append(self._geocodifica(luogo, sessione))

            if len(set(coordinate_luoghi)) != len(coordinate_luoghi):
                raise ValueError("Due o più punti inseriti corrispondono alla stessa posizione.")

            lonlats = "|".join(
                f"{longitudine},{latitudine}"
                for latitudine, longitudine in coordinate_luoghi
            )

            risposta = sessione.get(
                "https://brouter.de/brouter",
                params={
                    "lonlats": lonlats,
                    "profile": self._profilo_brouter(),
                    "alternativeidx": 0,
                    "format": "geojson",
                },
                timeout=25,
            )
            risposta.raise_for_status()
            dati = risposta.json()
            features = dati.get("features", [])
            if not features:
                raise ValueError("BRouter non ha trovato un percorso ciclabile tra i due luoghi.")

            feature_rotta = features[0]
            proprieta_rotta = feature_rotta.get("properties", {})
            coordinate_geojson = feature_rotta.get("geometry", {}).get("coordinates", [])
            coordinate = []
            for punto in coordinate_geojson:
                if len(punto) < 2:
                    continue
                longitudine, latitudine = float(punto[0]), float(punto[1])
                if not (-180 <= longitudine <= 180 and -90 <= latitudine <= 90):
                    continue
                punto_gpx = (latitudine, longitudine)
                if len(punto) > 2:
                    try:
                        punto_gpx += (float(punto[2]),)
                    except (TypeError, ValueError):
                        pass
                coordinate.append(punto_gpx)

            if len(coordinate) < 2:
                raise ValueError("La risposta del servizio non contiene una geometria valida.")

            from service.stats_service import analizza_dati_rotta_brouter
            statistiche = analizza_dati_rotta_brouter(proprieta_rotta, coordinate)

            self.completato.emit(True, {
                "id_progetto": self.id_progetto,
                "partenza": self.partenza,
                "destinazione": self.destinazione,
                "coordinate": coordinate,
                "profilo": self.profilo,
                "tappa_id": self.tappa_id,
                "statistiche": statistiche,
            }, "")
        except (requests.RequestException, ValueError, KeyError, TypeError) as errore:
            self.completato.emit(False, {}, str(errore))
        except Exception as errore:
            self.completato.emit(False, {}, f"Errore imprevisto durante il calcolo: {errore}")
        finally:
            sessione.close()


# Worker che legge i GPX esistenti e prepara le geometrie per MapLibre.
class WorkerCaricamentoMappa(QThread):
    elaborazione_completata = Signal(dict)

    def __init__(self, p_id, db_n):
        super().__init__()
        self.p_id = p_id
        self.db_n = db_n

    def run(self):
        import sqlite3
        import os
        import gpxpy
        
        payload = {"type": "FeatureCollection", "features": []}
        
        try:
            conn = sqlite3.connect(self.db_n)
            cursor = conn.cursor()
            
            # 1. ESTRAZIONE TAPPE GPX REALI
            cursor.execute("SELECT id, nome_file, sequenza, stato, blocco FROM tappe WHERE id_progetto = ? ORDER BY sequenza ASC", (self.p_id,))
            tappe = cursor.fetchall()
            
            for tappa_id, nome_file_db, seq, stato, blocco in tappe:
                if not nome_file_db: continue
                solo_nome = os.path.basename(nome_file_db)
                filepath = os.path.join(GPX_DIR, solo_nome)
                if os.path.exists(filepath):
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as gpx_file:
                            gpx = gpxpy.parse(gpx_file)
                            coords = []
                            for track in gpx.tracks:
                                for segment in track.segments:
                                    for point in segment.points:
                                        coords.append([point.longitude, point.latitude])
                            
                            if coords:
                                payload["features"].append({
                                    "type": "Feature",
                                    "geometry": {"type": "LineString", "coordinates": coords},
                                    "properties": {
                                        "tipo": "tappa", "tappa_id": tappa_id, "sequenza": seq,
                                        "blocco": str(blocco), "stato": str(stato),
                                        "nome_file": solo_nome
                                    }
                                })
                                # --- MARKER INIZIO TAPPA ---
                                payload["features"].append({
                                    "type": "Feature",
                                    "geometry": {"type": "Point", "coordinates": coords[0]},
                                    "properties": {"tipo": "marker_inizio", "sequenza": seq, "nome": f"Partenza Tappa {seq}", "nome_file": solo_nome}
                                })
                                # --- MARKER FINE TAPPA (NUOVO!) ---
                                payload["features"].append({
                                    "type": "Feature",
                                    "geometry": {"type": "Point", "coordinates": coords[-1]},
                                    "properties": {"tipo": "marker_fine", "sequenza": seq, "nome": f"Arrivo Tappa {seq}", "nome_file": solo_nome}
                                })
                                
                    except Exception:
                        pass

            # 2. ESTRAZIONE TRASFERIMENTI MANCANTI (Aereo, Nave, Treno)
            cursor.execute("SELECT id, tipo_mezzo, vettore, da_luogo, a_luogo, start_lat, start_lon, end_lat, end_lon FROM trasferimenti WHERE id_progetto = ?", (self.p_id,))
            trasferimenti = cursor.fetchall()
            
            for t_id, mezzo, vettore, da, a, s_lat, s_lon, e_lat, e_lon in trasferimenti:
                if s_lat and s_lon and e_lat and e_lon:
                    payload["features"].append({
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [[s_lon, s_lat], [e_lon, e_lat]]
                        },
                        "properties": {
                            "tipo": "trasferimento", "mezzo": str(mezzo),
                            "vettore": str(vettore), "da": str(da), "a": str(a), "nome_file": f"Trasferimento: {mezzo}"
                        }
                    })
                    
            conn.close()
        except Exception as err:
            print(f"Errore database nel worker: {err}")
            
        self.elaborazione_completata.emit(payload)
