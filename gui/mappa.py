import os
import json
import sqlite3
import threading
import math
import re
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
from PySide6.QtGui import QColor, QDesktopServices, QPainter

from service.config import BASE_DIR, BROUTER_URL, DB_NAME
from service.geometria_service import (
    VERSIONE_ALGORITMO_GEOMETRIA,
    decomprimi_segmenti,
    geometria_geojson,
)
from service.geonames_service import cerca_coordinate_luogo
from service.map_manager_service import MapManagerService, DownloadWorker
from service.mappa_dati_service import (
    carica_coordinate_tappa,
    carica_tappe_attive,
    costruisci_geojson_progetto,
    firma_dati_mappa,
)
from service.salvataggio_tappa_service import (
    rimuovi_gpx_se_esiste,
    salva_tappa_pianificata,
)
from service.gpx_paths import trova_percorso_gpx
from service.geo_utils import calcola_distanza_haversine

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
        self._progetto_sincronizzato_id = "non_ancora_verificato"  # sentinella diversa da None/ID reali
        self._worker_superfici_offline = None
        self._workers_superfici_attivi = []  # tiene in vita i worker finché non finiscono davvero
        self._richiesta_superfici_in_sospeso = None
        self._token_analisi_superfici = 0
        self._worker_nomi_luoghi = None
        self._workers_nomi_attivi = []  # stesso principio dei worker superfici: mai perdere il riferimento a un thread vivo
        self._richiesta_nomi_in_sospeso = None
        self._token_nomi_luoghi = 0
        self._worker_altimetria = None
        self._workers_altimetria_attivi = []  # stesso principio degli altri worker: mai perdere il riferimento a un thread vivo
        self._richiesta_altimetria_in_sospeso = None
        self._token_altimetria = 0
        self._id_tappa_inizio = None
        self._id_tappa_fine = None
        self._dati_tappe_intermedie = []  # elenco di sola consultazione delle tappe di un percorso già caricato
        self.setMinimumWidth(320)
        self.setMaximumWidth(420)
        
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
        self.btn_seleziona_inizio = QPushButton("🟢")
        self.btn_seleziona_inizio.setFixedSize(24, 30)
        self.btn_seleziona_inizio.setToolTip("Centra sulla tappa iniziale; clicca di nuovo per deselezionarla")
        self.btn_seleziona_inizio.setStyleSheet("QPushButton { background: transparent; border: none; padding: 0; }")
        self.btn_seleziona_inizio.clicked.connect(
            lambda: self._evidenzia_tappa_su_mappa(self._id_tappa_inizio)
        )
        self.input_partenza = QLineEdit()
        self.input_partenza.setPlaceholderText("Localita o coordinate di partenza...")
        layout_partenza.addWidget(self.btn_seleziona_inizio)
        layout_partenza.addWidget(self.input_partenza)
        contenuto_layout.addLayout(layout_partenza)

        # --- ELENCO TAPPE INTERMEDIE (percorso già caricato: sola consultazione) ---
        # Diverso dai "punti di passaggio" manuali più sotto: qui non si edita
        # nulla, si vedono solo le tappe del percorso aperto e si può cliccare
        # una riga per evidenziarla sulla mappa.
        self.contenitore_tappe_intermedie = QWidget()
        layout_tappe_intermedie_esterno = QVBoxLayout(self.contenitore_tappe_intermedie)
        layout_tappe_intermedie_esterno.setContentsMargins(0, 0, 0, 0)
        layout_tappe_intermedie_esterno.setSpacing(4)

        self.btn_toggle_tappe_intermedie = QPushButton("▾ 0 tappe intermedie")
        self.btn_toggle_tappe_intermedie.setCheckable(True)
        self.btn_toggle_tappe_intermedie.setChecked(True)
        self.btn_toggle_tappe_intermedie.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_tappe_intermedie.setStyleSheet(
            "QPushButton { background: transparent; color: #7dd3fc; border: none; text-align: left; "
            "padding: 2px 0; font-size: 12px; font-weight: 600; } "
            "QPushButton:hover { color: #bae6fd; }"
        )
        self.btn_toggle_tappe_intermedie.clicked.connect(self._toggle_elenco_tappe_intermedie)
        layout_tappe_intermedie_esterno.addWidget(self.btn_toggle_tappe_intermedie)

        self.area_scorrimento_tappe_intermedie = QScrollArea()
        self.area_scorrimento_tappe_intermedie.setWidgetResizable(True)
        self.area_scorrimento_tappe_intermedie.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.area_scorrimento_tappe_intermedie.setMaximumHeight(170)
        self.area_scorrimento_tappe_intermedie.setStyleSheet(
            "QScrollArea { background-color: #161616; border: 1px solid #2d2d2d; border-radius: 6px; }"
        )
        contenuto_lista_tappe = QWidget()
        self.layout_lista_tappe_intermedie = QVBoxLayout(contenuto_lista_tappe)
        self.layout_lista_tappe_intermedie.setContentsMargins(4, 4, 4, 4)
        self.layout_lista_tappe_intermedie.setSpacing(2)
        self.area_scorrimento_tappe_intermedie.setWidget(contenuto_lista_tappe)
        layout_tappe_intermedie_esterno.addWidget(self.area_scorrimento_tappe_intermedie)

        self.contenitore_tappe_intermedie.setVisible(False)  # compare solo se il percorso caricato ha tappe intermedie
        contenuto_layout.addWidget(self.contenitore_tappe_intermedie)

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
        self.btn_seleziona_fine = QPushButton("🏁")
        self.btn_seleziona_fine.setFixedSize(24, 30)
        self.btn_seleziona_fine.setToolTip("Centra sulla tappa finale; clicca di nuovo per deselezionarla")
        self.btn_seleziona_fine.setStyleSheet("QPushButton { background: transparent; border: none; padding: 0; }")
        self.btn_seleziona_fine.clicked.connect(
            lambda: self._evidenzia_tappa_su_mappa(self._id_tappa_fine)
        )
        self.input_destinazione = QLineEdit()
        self.input_destinazione.setPlaceholderText("Localita o coordinate di destinazione...")
        layout_arrivo.addWidget(self.btn_seleziona_fine)
        layout_arrivo.addWidget(self.input_destinazione)
        contenuto_layout.addLayout(layout_arrivo)
        lbl_attribuzione_geonames = QLabel(
            "Ricerca locale GeoNames - dati CC BY 4.0 "
            "(geonames.org, creativecommons.org/licenses/by/4.0/)"
        )
        lbl_attribuzione_geonames.setWordWrap(True)
        lbl_attribuzione_geonames.setStyleSheet(
            "font-size: 10px; color: #94a3b8; border: none;"
        )
        contenuto_layout.addWidget(lbl_attribuzione_geonames)

        lbl_superfici = QLabel("Superfici del percorso")
        lbl_superfici.setStyleSheet("color: #cbd5e1; font-size: 12px; font-weight: 600; margin-top: 4px; border: none;")
        contenuto_layout.addWidget(lbl_superfici)
        self.barra_superfici = BarraSuperfici()
        contenuto_layout.addWidget(self.barra_superfici)
        # Griglia (non una singola riga) per la legenda: con molte categorie di
        # superficie una sola riga orizzontale tagliava il testo delle ultime voci.
        self.layout_leggenda_superfici = QGridLayout()
        self.layout_leggenda_superfici.setContentsMargins(0, 4, 0, 0)
        self.layout_leggenda_superfici.setHorizontalSpacing(12)
        self.layout_leggenda_superfici.setVerticalSpacing(3)
        contenuto_layout.addLayout(self.layout_leggenda_superfici)
        self.lbl_stato_superfici = QLabel("La ripartizione compare dopo il calcolo della rotta.")
        self.lbl_stato_superfici.setWordWrap(True)
        self.lbl_stato_superfici.setStyleSheet("font-size: 11px; color: #cbd5e1; line-height: 1.4;")
        contenuto_layout.addWidget(self.lbl_stato_superfici)

        lbl_dettagli = QLabel("Dettagli tecnici")
        lbl_dettagli.setStyleSheet("color: #cbd5e1; font-size: 12px; font-weight: 600; margin-top: 4px; border: none;")
        contenuto_layout.addWidget(lbl_dettagli)
        # Una colonna sola (non più una griglia 2x2): con nomi lunghi come
        # "Velocità media stimata" la griglia a due colonne tagliava il testo.
        dettagli_layout = QVBoxLayout()
        dettagli_layout.setContentsMargins(0, 0, 0, 0)
        dettagli_layout.setSpacing(5)
        stile_dettaglio = "font-size: 12px; color: #f1f5f9; font-weight: 500; border: none;"
        self.lbl_velocita_media = QLabel("Velocità media stimata: --")
        self.lbl_altitudine_massima = QLabel("Altitudine massima: --")
        self.lbl_altitudine_minima = QLabel("Altitudine minima: --")
        self.lbl_distanza_totale = QLabel("Distanza totale: --")
        for etichetta in (self.lbl_velocita_media, self.lbl_altitudine_massima,
                          self.lbl_altitudine_minima, self.lbl_distanza_totale):
            etichetta.setStyleSheet(stile_dettaglio)
            etichetta.setWordWrap(True)
            dettagli_layout.addWidget(etichetta)
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
            coordinate = carica_coordinate_tappa(
                tappa_id, progetto, DB_NAME, directory_gpx=GPX_DIR
            )

            self.input_partenza.setText(f"{coordinate[0][0]:.6f}, {coordinate[0][1]:.6f}")
            self.input_destinazione.setText(f"{coordinate[-1][0]:.6f}, {coordinate[-1][1]:.6f}")
            while self.punti_passaggio:
                self._rimuovi_punto_passaggio(self.punti_passaggio[-1]["widget"])
            self.tappa_in_modifica_id = tappa_id
            self.btn_salva.setText("Aggiorna tappa")
            self._aggiungi_waypoint_da_coordinate(latitudine, longitudine)
        except (OSError, sqlite3.Error, ValueError) as errore:
            QMessageBox.warning(self, "Modifica tratta non riuscita", str(errore))

    def sincronizza_stato_percorso(self):
        """
        Riconosce lo stato del percorso attivo: se il progetto caricato ha già
        delle tappe (file GPX importati o creati in precedenza), precompila
        automaticamente Partenza, Destinazione, eventuali tappe intermedie e i
        dettagli tecnici disponibili (distanza, altitudine). Non tocca nulla se
        l'utente ha già iniziato a pianificare manualmente un nuovo tratto.
        """
        finestra_principale = getattr(self.mappa_widget, "parent_app", None)
        id_progetto = getattr(finestra_principale, "current_progetto_id", None)

        if id_progetto != self._progetto_sincronizzato_id:
            # Cambio di progetto (o percorso chiuso): puliamo il pannello prima di
            # ripopolarlo, ma solo se non c'è già una modifica manuale in corso.
            self._progetto_sincronizzato_id = id_progetto
            if self.tappa_in_modifica_id is None:
                self.input_partenza.clear()
                self.input_destinazione.clear()
                while self.punti_passaggio:
                    self._rimuovi_punto_passaggio(self.punti_passaggio[-1]["widget"])
                self._popola_tappe_intermedie([])
                self._evidenzia_tappa_su_mappa(None)
                self._id_tappa_inizio = None
                self._id_tappa_fine = None
                self.btn_seleziona_inizio.setEnabled(False)
                self.btn_seleziona_fine.setEnabled(False)
                self.lbl_velocita_media.setText("Velocità media stimata: --")
                self.lbl_altitudine_massima.setText("Altitudine massima: --")
                self.lbl_altitudine_minima.setText("Altitudine minima: --")
                self.lbl_distanza_totale.setText("Distanza totale: --")
                self.barra_superfici.imposta_superfici([])
                self._popola_legenda_superfici([])
                self.lbl_stato_superfici.setText("La ripartizione compare dopo il calcolo della rotta.")
                # Invalida eventuali analisi/geocodifiche del percorso precedente
                # ancora in corso in background: senza questo, un risultato
                # tardivo potrebbe ripopolare i campi appena svuotati.
                self._token_analisi_superfici += 1
                self._token_nomi_luoghi += 1
                self._token_altimetria += 1
                # Chiediamo anche ai worker eventualmente ancora in esecuzione
                # di fermarsi subito invece di continuare a girare a vuoto in
                # sottofondo: senza questo, un'analisi pesante su un percorso
                # enorme restava attiva anche dopo essere diventata inutile,
                # e la richiesta per il nuovo percorso doveva aspettare in
                # coda che finisse, rallentando ogni cambio successivo.
                if self._worker_superfici_offline is not None:
                    try:
                        self._worker_superfici_offline.request_stop()
                    except RuntimeError:
                        pass
                if self._worker_nomi_luoghi is not None:
                    try:
                        self._worker_nomi_luoghi.request_stop()
                    except RuntimeError:
                        pass
                if self._worker_altimetria is not None:
                    try:
                        self._worker_altimetria.request_stop()
                    except RuntimeError:
                        pass

        if not id_progetto or self.tappa_in_modifica_id is not None:
            return
        if self.input_partenza.text().strip() or self.input_destinazione.text().strip():
            return  # l'utente ha già iniziato a compilare i campi manualmente

        try:
            tappe = carica_tappe_attive(id_progetto, DB_NAME)
        except sqlite3.Error as errore:
            print(f"Nota: impossibile leggere le tappe del progetto per il wizard: {errore}")
            return

        if not tappe:
            return

        self._id_tappa_inizio = tappe[0][0]
        self._id_tappa_fine = tappe[-1][0]
        self.btn_seleziona_inizio.setEnabled(True)
        self.btn_seleziona_fine.setEnabled(True)

        _, primo_file, primo_lat, primo_lon, _, _, _ = tappe[0]
        _, _, _, _, ultimo_lat, ultimo_lon, _ = tappe[-1]
        self.btn_seleziona_inizio.setToolTip(
            f"Centra sulla tappa iniziale (ID {self._id_tappa_inizio}); clicca di nuovo per deselezionarla"
        )
        self.btn_seleziona_fine.setToolTip(
            f"Centra sulla tappa finale (ID {self._id_tappa_fine}); clicca di nuovo per deselezionarla"
        )

        # Mostriamo subito le coordinate (nessuna attesa): il nome del luogo,
        # se le mappe locali lo contengono, arriva poco dopo in background
        # (vedi _avvia_risoluzione_nomi_luoghi) senza bloccare l'interfaccia.
        richieste_nomi = []
        if primo_lat is not None and primo_lon is not None:
            self.input_partenza.setText(f"{primo_lat:.6f}, {primo_lon:.6f}")
            richieste_nomi.append({"chiave": "partenza", "lat": primo_lat, "lon": primo_lon})
        if ultimo_lat is not None and ultimo_lon is not None:
            self.input_destinazione.setText(f"{ultimo_lat:.6f}, {ultimo_lon:.6f}")
            richieste_nomi.append({"chiave": "destinazione", "lat": ultimo_lat, "lon": ultimo_lon})

        # Le tappe intermedie (se il percorso caricato ne ha più di una) vengono
        # mostrate in un elenco a scorrimento separato e di sola consultazione:
        # cliccandone una si evidenzia il tratto corrispondente sulla mappa.
        tappe_intermedie = []
        for tappa_id, _, start_lat, start_lon, _, _, _ in tappe[1:-1]:
            if start_lat is None or start_lon is None:
                continue
            testo_iniziale = f"{start_lat:.6f}, {start_lon:.6f}"
            tappe_intermedie.append({"id": tappa_id, "testo": testo_iniziale})
            richieste_nomi.append({"chiave": tappa_id, "lat": start_lat, "lon": start_lon})
        self._popola_tappe_intermedie(tappe_intermedie)

        if richieste_nomi:
            self._avvia_risoluzione_nomi_luoghi(richieste_nomi)

        distanza_totale_km = sum(riga[6] or 0.0 for riga in tappe)
        self.lbl_distanza_totale.setText(
            f"Distanza totale: {distanza_totale_km:.1f} km" if distanza_totale_km > 0 else "Distanza totale: --"
        )

        # L'altimetria (min/max) legge e fa il parsing XML di ogni file GPX del
        # percorso: con percorsi molto lunghi (centinaia di tappe) farlo qui,
        # in modo sincrono sul thread dell'interfaccia, bloccava l'intera app
        # per minuti. Ora viene calcolata in un thread separato, come già
        # avviene per superfici e nomi luogo.
        nomi_file = [
            (nome_file, id_progetto)
            for _, nome_file, *_ in tappe
            if nome_file
        ]
        self._avvia_analisi_altimetria(nomi_file)

        self._avvia_analisi_superfici_offline(id_progetto)
        self._adatta_altezza_al_contenuto()

    def _avvia_risoluzione_nomi_luoghi(self, richieste):
        """
        Risolve in un thread separato il nome del luogo più vicino (offline,
        dalle mappe locali) per partenza/arrivo/tappe intermedie, così
        l'interfaccia non si blocca nemmeno con percorsi molto lunghi.
        Finché il nome non è pronto restano visibili le coordinate.
        """
        self._token_nomi_luoghi += 1

        try:
            worker_ancora_attivo = self._worker_nomi_luoghi is not None and self._worker_nomi_luoghi.isRunning()
        except RuntimeError:
            # Difesa aggiuntiva: se per qualche motivo il riferimento non è
            # stato azzerato in tempo, trattiamo il worker come già finito
            # invece di far esplodere l'intera sincronizzazione del pannello.
            worker_ancora_attivo = False
            self._worker_nomi_luoghi = None

        if worker_ancora_attivo:
            self._richiesta_nomi_in_sospeso = richieste
            # Il vecchio worker non serve più (la richiesta è già superata):
            # gli chiediamo di fermarsi subito, così quello nuovo può partire
            # appena possibile invece di aspettare che finisca tutto da solo.
            self._worker_nomi_luoghi.request_stop()
            return

        self._avvia_worker_nomi_luoghi(richieste)

    def _avvia_worker_nomi_luoghi(self, richieste):
        token_corrente = self._token_nomi_luoghi
        worker = WorkerNomiLuoghi(richieste)
        self._worker_nomi_luoghi = worker
        self._workers_nomi_attivi.append(worker)
        worker.nomi_pronti.connect(
            lambda risultati, token=token_corrente: self._fine_risoluzione_nomi_luoghi(risultati, token)
        )
        worker.finished.connect(lambda worker=worker: self._ripulisci_worker_nomi(worker))
        worker.start()

    def _ripulisci_worker_nomi(self, worker):
        """Rimuove dalla lista di sopravvivenza un worker di geocodifica che ha finito, e lo elimina."""
        if worker in self._workers_nomi_attivi:
            self._workers_nomi_attivi.remove(worker)
        if self._worker_nomi_luoghi is worker:
            # Fondamentale: senza questo azzeramento il riferimento rimaneva
            # puntato al worker distrutto, e la prossima chiamata a isRunning()
            # falliva con "Internal C++ object already deleted" interrompendo
            # tutta la sincronizzazione del pannello a metà.
            self._worker_nomi_luoghi = None
        worker.deleteLater()

    def _fine_risoluzione_nomi_luoghi(self, risultati, token):
        richiesta_in_sospeso = self._richiesta_nomi_in_sospeso
        self._richiesta_nomi_in_sospeso = None
        if richiesta_in_sospeso is not None:
            self._avvia_worker_nomi_luoghi(richiesta_in_sospeso)

        if token != self._token_nomi_luoghi:
            return  # nel frattempo l'utente ha cambiato percorso: risultato superato

        if "partenza" in risultati:
            self.input_partenza.setText(risultati["partenza"])
        if "destinazione" in risultati:
            self.input_destinazione.setText(risultati["destinazione"])
        testi_tappe_intermedie = {
            chiave: testo for chiave, testo in risultati.items()
            if chiave not in ("partenza", "destinazione")
        }
        if testi_tappe_intermedie:
            self._aggiorna_testo_tappe_intermedie(testi_tappe_intermedie)

    def _avvia_analisi_superfici_offline(self, id_progetto):
        """
        Calcola in un thread separato (per non bloccare l'interfaccia) la
        ripartizione delle superfici confrontando i GPX con le mappe locali
        già scaricate. Nessuna chiamata di rete: se il calcolo è già stato
        fatto in precedenza, viene semplicemente riletto dalla cache locale.
        """
        self.lbl_stato_superfici.setText("Analisi offline delle superfici in corso (mappe locali già scaricate)...")
        self._token_analisi_superfici += 1

        try:
            worker_ancora_attivo = self._worker_superfici_offline is not None and self._worker_superfici_offline.isRunning()
        except RuntimeError:
            worker_ancora_attivo = False
            self._worker_superfici_offline = None

        if worker_ancora_attivo:
            # Un'analisi è già in corso (es. la pagina è stata riaperta velocemente):
            # non ne lanciamo una seconda in parallelo, la mettiamo in coda e
            # partirà appena l'attuale sarà terminata (vedi _fine_analisi_superfici_offline).
            # Il vecchio calcolo non serve più: gli chiediamo di fermarsi subito
            # invece di lasciarlo continuare a girare a vuoto in sottofondo
            # (con percorsi enormi restava attivo per minuti anche se inutile).
            self._richiesta_superfici_in_sospeso = id_progetto
            self._worker_superfici_offline.request_stop()
            return

        self._avvia_worker_superfici(id_progetto)

    def _avvia_worker_superfici(self, id_progetto):
        token_corrente = self._token_analisi_superfici
        worker = WorkerAnalisiSuperficiOffline(id_progetto)
        self._worker_superfici_offline = worker
        self._workers_superfici_attivi.append(worker)
        worker.analisi_completata.connect(
            lambda risultato, token=token_corrente: self._fine_analisi_superfici_offline(risultato, token)
        )
        worker.finished.connect(lambda worker=worker: self._ripulisci_worker_superfici(worker))
        worker.start()

    def _ripulisci_worker_superfici(self, worker):
        """Rimuove dalla lista di sopravvivenza un worker di analisi superfici che ha finito, e lo elimina."""
        if worker in self._workers_superfici_attivi:
            self._workers_superfici_attivi.remove(worker)
        if self._worker_superfici_offline is worker:
            # Stesso bug del worker nomi-luoghi: senza azzerare il riferimento,
            # il prossimo controllo isRunning() punterebbe a un thread già
            # distrutto e farebbe crashare la sincronizzazione del pannello.
            self._worker_superfici_offline = None
        worker.deleteLater()

    def _fine_analisi_superfici_offline(self, risultato, token):
        # Se nel frattempo è arrivata una nuova richiesta (messa in coda perché
        # un'analisi era già in corso), la avviamo ora che il worker è libero.
        richiesta_in_sospeso = self._richiesta_superfici_in_sospeso
        self._richiesta_superfici_in_sospeso = None
        if richiesta_in_sospeso is not None:
            self._avvia_worker_superfici(richiesta_in_sospeso)

        if token != self._token_analisi_superfici:
            return  # nel frattempo l'utente ha cambiato percorso: risultato superato

        if not risultato or not risultato.get("disponibile"):
            motivo = (risultato or {}).get("motivo", "Dati non disponibili.")
            self.lbl_stato_superfici.setText(f"Superfici non calcolabili offline: {motivo}")
            return

        self.barra_superfici.imposta_superfici(risultato.get("superfici", []))
        self._popola_legenda_superfici(risultato.get("superfici", []))

        copertura = risultato.get("copertura_percentuale", 0)
        n_vietati = len(risultato.get("tratti_vietati", []))
        messaggio = f"Stima offline da mappe locali già scaricate (copertura {copertura:.0f}% del percorso)."
        if n_vietati:
            messaggio += f" Attenzione: {n_vietati} tratto/i probabilmente vietati alle bici (vedi Audit)."
        self.lbl_stato_superfici.setText(messaggio)
        self._adatta_altezza_al_contenuto()

    def _avvia_analisi_altimetria(self, nomi_file):
        """
        Calcola in un thread separato altitudine massima/minima leggendo i
        file GPX del percorso: farlo sul thread dell'interfaccia bloccava
        l'intera app (anche a lungo, con percorsi di centinaia di tappe).
        """
        self._token_altimetria += 1

        try:
            worker_ancora_attivo = self._worker_altimetria is not None and self._worker_altimetria.isRunning()
        except RuntimeError:
            worker_ancora_attivo = False
            self._worker_altimetria = None

        if worker_ancora_attivo:
            self._richiesta_altimetria_in_sospeso = nomi_file
            # Come per gli altri worker: il calcolo precedente non serve più,
            # meglio interromperlo subito invece di aspettare che finisca.
            self._worker_altimetria.request_stop()
            return

        self._avvia_worker_altimetria(nomi_file)

    def _avvia_worker_altimetria(self, nomi_file):
        token_corrente = self._token_altimetria
        worker = WorkerAltimetria(nomi_file)
        self._worker_altimetria = worker
        self._workers_altimetria_attivi.append(worker)
        worker.altimetria_pronta.connect(
            lambda risultato, token=token_corrente: self._fine_analisi_altimetria(risultato, token)
        )
        worker.finished.connect(lambda worker=worker: self._ripulisci_worker_altimetria(worker))
        worker.start()

    def _ripulisci_worker_altimetria(self, worker):
        """Rimuove dalla lista di sopravvivenza un worker di altimetria che ha finito, e lo elimina."""
        if worker in self._workers_altimetria_attivi:
            self._workers_altimetria_attivi.remove(worker)
        if self._worker_altimetria is worker:
            # Stesso bug degli altri worker: senza azzerare il riferimento,
            # il prossimo isRunning() punterebbe a un thread già distrutto.
            self._worker_altimetria = None
        worker.deleteLater()

    def _fine_analisi_altimetria(self, risultato, token):
        richiesta_in_sospeso = self._richiesta_altimetria_in_sospeso
        self._richiesta_altimetria_in_sospeso = None
        if richiesta_in_sospeso is not None:
            self._avvia_worker_altimetria(richiesta_in_sospeso)

        if token != self._token_altimetria:
            return  # nel frattempo l'utente ha cambiato percorso: risultato superato

        massima = risultato.get("massima")
        minima = risultato.get("minima")
        if massima is not None:
            self.lbl_altitudine_massima.setText(f"Altitudine massima: {int(massima)} m")
        if minima is not None:
            self.lbl_altitudine_minima.setText(f"Altitudine minima: {round(minima)} m")

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

    def _toggle_elenco_tappe_intermedie(self):
        """Apre/chiude l'elenco a scorrimento delle tappe intermedie del percorso caricato."""
        aperto = self.btn_toggle_tappe_intermedie.isChecked()
        self.area_scorrimento_tappe_intermedie.setVisible(aperto)
        numero = len(self._dati_tappe_intermedie)
        self.btn_toggle_tappe_intermedie.setText(f"{'▾' if aperto else '▸'} {numero} tappa/e intermedia/e")
        QTimer.singleShot(0, self._adatta_altezza_al_contenuto)

    def _costruisci_riga_tappa_intermedia(self, indice, tappa_id, testo):
        """Crea una riga cliccabile dell'elenco: il click evidenzia la tappa sulla mappa."""
        riga = QPushButton(f"📍 {indice + 1}.  {testo}")
        riga.setCursor(Qt.PointingHandCursor)
        riga.setStyleSheet(
            "QPushButton { background: transparent; color: #e2e8f0; border: none; text-align: left; "
            "padding: 6px 6px; border-radius: 4px; font-size: 12px; } "
            "QPushButton:hover { background-color: #263746; color: #7dd3fc; }"
        )
        riga.clicked.connect(lambda checked=False, tid=tappa_id: self._evidenzia_tappa_su_mappa(tid))
        return riga

    def _popola_tappe_intermedie(self, tappe):
        """
        Ricostruisce l'elenco a scorrimento delle tappe intermedie del percorso
        caricato. 'tappe' è una lista di dict con chiavi 'id' e 'testo' (nome
        del luogo, o coordinate se il nome non è disponibile offline).
        """
        while self.layout_lista_tappe_intermedie.count():
            elemento = self.layout_lista_tappe_intermedie.takeAt(0)
            if elemento.widget():
                elemento.widget().deleteLater()

        self._dati_tappe_intermedie = list(tappe or [])
        numero = len(self._dati_tappe_intermedie)
        self.contenitore_tappe_intermedie.setVisible(numero > 0)
        if numero == 0:
            QTimer.singleShot(0, self._adatta_altezza_al_contenuto)
            return

        for indice, tappa in enumerate(self._dati_tappe_intermedie):
            riga = self._costruisci_riga_tappa_intermedia(indice, tappa["id"], tappa["testo"])
            self.layout_lista_tappe_intermedie.addWidget(riga)

        aperto = self.btn_toggle_tappe_intermedie.isChecked()
        self.btn_toggle_tappe_intermedie.setText(f"{'▾' if aperto else '▸'} {numero} tappa/e intermedia/e")
        self.area_scorrimento_tappe_intermedie.setVisible(aperto)
        QTimer.singleShot(0, self._adatta_altezza_al_contenuto)

    def _aggiorna_testo_tappe_intermedie(self, testi_per_id):
        """Aggiorna solo il testo (es. nome del luogo appena risolto) senza ricostruire le righe."""
        for indice in range(self.layout_lista_tappe_intermedie.count()):
            widget = self.layout_lista_tappe_intermedie.itemAt(indice).widget()
            if not widget or indice >= len(self._dati_tappe_intermedie):
                continue
            tappa_id = self._dati_tappe_intermedie[indice]["id"]
            nuovo_testo = testi_per_id.get(tappa_id)
            if nuovo_testo:
                self._dati_tappe_intermedie[indice]["testo"] = nuovo_testo
                widget.setText(f"📍 {indice + 1}.  {nuovo_testo}")

    def _popola_legenda_superfici(self, superfici):
        """
        Ricostruisce la legenda delle superfici (usata sia dal calcolo offline
        sia dal routing manuale) su una griglia a 2 colonne invece di un'unica
        riga orizzontale: con molte categorie una riga sola tagliava il testo.
        """
        while self.layout_leggenda_superfici.count():
            elemento = self.layout_leggenda_superfici.takeAt(0)
            if elemento.widget():
                elemento.widget().deleteLater()

        colonne = 2
        for indice, superficie in enumerate(superfici or []):
            legenda = QLabel(f"● {superficie['categoria']} — {superficie['percentuale']:.0f}%")
            legenda.setStyleSheet(f"font-size: 11px; color: {superficie['colore']}; font-weight: 600;")
            legenda.setWordWrap(True)
            self.layout_leggenda_superfici.addWidget(legenda, indice // colonne, indice % colonne)

    def _evidenzia_tappa_su_mappa(self, tappa_id):
        """Evidenzia o deseleziona una tappa e centra il relativo tratto."""
        if self.mappa_widget:
            self.mappa_widget.evidenzia_tappa(tappa_id)

    def _aggiorna_dettagli_rotta(self, statistiche):
        """Aggiorna barra superfici, legenda e KPI della rotta calcolata."""
        statistiche = statistiche or {}
        superfici = statistiche.get("superfici", [])
        self.barra_superfici.imposta_superfici(superfici)
        self._popola_legenda_superfici(superfici)

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
            calcola_distanza_haversine(coordinate[index][0], coordinate[index][1],
                                       coordinate[index + 1][0], coordinate[index + 1][1])
            for index in range(len(coordinate) - 1)
        )
        if distanza_km <= 0:
            QMessageBox.warning(self, "Traccia non valida", "Il percorso calcolato non contiene una distanza valida.")
            return

        # Il file GPX appena scritto serve a ripulire se un passo successivo della GUI fallisce.
        stato_salvataggio = {}
        try:
            # Scrittura GPX, SQLite e precalcolo: tutta la parte dati sta nel servizio.
            esito = salva_tappa_pianificata(
                id_progetto_corrente,
                coordinate,
                partenza,
                destinazione,
                distanza_km,
                tappa_id=risultato.get("tappa_id"),
                db_name=DB_NAME,
                directory_gpx=GPX_DIR,
                esito=stato_salvataggio,
            )
            tappa_in_aggiornamento = esito["aggiornata"]
            precalcolo_riuscito = esito["precalcolo_riuscito"]
            errore_precalcolo = esito["errore_precalcolo"]

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
            self.mappa_widget.rigenera_mappa(
                id_progetto_corrente,
                DB_NAME,
                force=True,
                adatta_visuale=False,
            )

            QMessageBox.information(
                self,
                "Percorso salvato",
                f"La tappa è stata {'aggiornata' if tappa_in_aggiornamento else 'aggiunta'} al progetto. "
                f"Distanza: {distanza_km:.1f} km.",
            )
            if not precalcolo_riuscito:
                QMessageBox.warning(
                    self,
                    "Precalcolo non completato",
                    "La rotta è stata salvata, ma il precalcolo delle metriche "
                    f"non è riuscito: {errore_precalcolo}. "
                    "Il GPX precedente è stato conservato.",
                )
        except Exception as errore_salvataggio:
            rimuovi_gpx_se_esiste(stato_salvataggio.get("file_gpx"))
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
        self._token_caricamento_mappa = 0
        self._mappa_workers_attivi = []  # tiene in vita i worker finché non finiscono davvero (vedi rigenera_mappa)
        self.ultimo_progetto_id_caricato = None
        self._firma_dati_mappa_caricati = None
        self._cache_per_progetto = {}
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

        btn_apri_browser = QPushButton("🌐 Apri nel browser")
        btn_apri_browser.setStyleSheet("background-color: #262626; color: #e2e8f0; border: 1px solid #404040; padding: 6px 12px; border-radius: 4px; font-weight: 500;")
        btn_apri_browser.clicked.connect(self.apri_mappa_nel_browser)
        toolbar.addWidget(btn_apri_browser)

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

    def apri_mappa_nel_browser(self):
        """Apre la stessa pagina locale visualizzata nella WebView."""
        if not QDesktopServices.openUrl(self.web_view.url()):
            QMessageBox.warning(
                self,
                "Impossibile aprire il browser",
                "Windows non è riuscito ad aprire la pagina della mappa.",
            )

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
                # Evento di un altro progetto (l'utente ha cambiato percorso prima del click):
                # la modalità mappa è comunque già stata azzerata dal JavaScript,
                # quindi fermiamo il polling per non interrogare il server inutilmente.
                self._poll_interazioni_timer.stop()
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
                    f"window.impostaModalitaInterazioneMappa(null, {int(id_progetto)});"
                )
                self.pannello_pianificazione.lbl_stato_superfici.setText("Modalità mappa disattivata.")
            # Volutamente dentro il ciclo: ogni modalità mappa è "usa e getta".
            # Il JavaScript (inviaInterazioneMappa) la azzera subito dopo aver
            # inviato UN solo evento, quindi dopo averlo gestito il polling non serve più.
            # Con zero eventi il timer resta attivo in attesa del click: non spostare fuori dal for.
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

    def evidenzia_tappa(self, tappa_id):
        """Evidenzia (colore e centratura) il tratto GPX della tappa selezionata nell'elenco del pannello."""
        self.web_view.page().runJavaScript(
            f"if(window.evidenziaTappa) window.evidenziaTappa({json.dumps(tappa_id)});"
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
                from service.config import DB_NAME
                firma_corrente = self._firma_dati_mappa(p_id, DB_NAME)
                progetto_cambiato = self.ultimo_progetto_id_caricato != p_id
                aggiornamento_richiesto = getattr(
                    finestra_principale,
                    "mappa_necessita_aggiornamento",
                    True,
                )
                cache_progetto = self._cache_per_progetto.get(p_id)
                firma_in_cache = (
                    cache_progetto.get("firma")
                    if cache_progetto is not None
                    else None
                )
                cache_valida = (
                    firma_corrente is not None
                    and firma_corrente == firma_in_cache
                )

                if cache_valida and (not aggiornamento_richiesto or progetto_cambiato):
                    # La firma uguale dimostra che la richiesta globale di aggiornamento
                    # deriva solo dal cambio progetto, non da dati mappa modificati.
                    if aggiornamento_richiesto:
                        setattr(
                            finestra_principale,
                            "mappa_necessita_aggiornamento",
                            False,
                        )
                    if progetto_cambiato:
                        self._mostra_cache_progetto(p_id, cache_progetto["geojson"])
                    self.ultimo_progetto_id_caricato = p_id
                    self._firma_dati_mappa_caricati = firma_corrente
                else:
                    if progetto_cambiato:
                        print(f"🚀 Mappa aperta. Avvio caricamento asincrono per percorso ID: {p_id}")
                    QTimer.singleShot(
                        100,
                        lambda: self.rigenera_mappa(
                            p_id,
                            DB_NAME,
                            force=True,
                            adatta_visuale=progetto_cambiato,
                            firma_dati=firma_corrente,
                        ),
                    )
                QTimer.singleShot(400, lambda: self.pannello_pianificazione.show() if hasattr(self, 'pannello_pianificazione') else None)
                QTimer.singleShot(450, lambda: self.pannello_pianificazione.sincronizza_stato_percorso() if hasattr(self, 'pannello_pianificazione') else None)
                QTimer.singleShot(500, lambda: self.web_view.setZoomFactor(1.0))
                return

        from service.config import DB_NAME
        # Se non c'è un progetto attivo, svuota sia la mappa visibile sia i dati in Flask.
        self.rigenera_mappa(None, DB_NAME)
        QTimer.singleShot(100, lambda: self.pannello_pianificazione.show() if hasattr(self, 'pannello_pianificazione') else None)
        QTimer.singleShot(150, lambda: self.pannello_pianificazione.sincronizza_stato_percorso() if hasattr(self, 'pannello_pianificazione') else None)
        QTimer.singleShot(0, self._ridimensiona_mappa)
        QTimer.singleShot(300, lambda: self.web_view.setZoomFactor(1.0))

    def rigenera_mappa(
        self,
        current_progetto_id,
        db_name,
        force=False,
        mappa_necessita_aggiornamento=True,
        adatta_visuale=True,
        firma_dati=None,
    ):
        # Se l'utente esce dal percorso o non c'è un progetto attivo, puliamo lo schermo
        if not current_progetto_id:
            # Invalida i worker ancora in esecuzione per evitare invii di dati vecchi.
            self._token_caricamento_mappa += 1
            # Azzera solo il progetto visualizzato: la cache per progetto resta valida.
            if hasattr(self, 'ultimo_progetto_id_caricato'):
                self.ultimo_progetto_id_caricato = None
            self._firma_dati_mappa_caricati = None
            vuoto = {"type": "FeatureCollection", "features": []}
            # Invio in background: una richiesta di rete sincrona qui bloccherebbe
            # l'interfaccia se il server Flask locale è occupato con un'altra richiesta.
            threading.Thread(
                target=lambda: requests.post("http://127.0.0.1:8080/api/set-gpx-data", json=vuoto, timeout=5),
                daemon=True,
            ).start()

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

        if firma_dati is None:
            firma_dati = self._firma_dati_mappa(current_progetto_id, db_name)

        # NOTA: in precedenza qui si forzava la chiusura del worker precedente con
        # terminate()+wait(), un'operazione pericolosa che può bloccare l'interfaccia
        # per tempi imprevedibili. Ora lasciamo che il vecchio worker finisca da solo
        # e scartiamo il suo risultato tramite un "token" se nel frattempo ne è
        # partito uno più recente.
        self._token_caricamento_mappa += 1
        token_corrente = self._token_caricamento_mappa

        # RADDRIZZATO: Rimosso 'const ls' che mandava in crash il secondo tentativo di caricamento
        js_accendi = "if(document.getElementById('loading-screen')) { document.getElementById('loading-screen').style.display = 'flex'; }"
        self.web_view.page().runJavaScript(js_accendi)

        self.mappa_worker = WorkerCaricamentoMappa(
            current_progetto_id,
            db_name,
            token_corrente,
            lambda: self._token_caricamento_mappa,
        )
        self._mappa_workers_attivi.append(self.mappa_worker)
        self.mappa_worker.elaborazione_completata.connect(
            lambda payload, token=token_corrente, pid=current_progetto_id,
            firma=firma_dati, adatta=adatta_visuale: self._fine_caricamento_asincrono(
                payload, token, pid, firma, adatta
            )
        )
        self.mappa_worker.finished.connect(
            lambda worker=self.mappa_worker: self._ripulisci_mappa_worker(worker)
        )
        self.mappa_worker.start()
        return True

    def _firma_dati_mappa(self, id_progetto, db_name):
        """Crea una firma rapida dei campi DB usati per disegnare il progetto."""
        return firma_dati_mappa(id_progetto, db_name)

    def _ripulisci_mappa_worker(self, worker):
        """Rimuove dalla lista di sopravvivenza un worker di caricamento mappa che ha finito, e lo elimina."""
        if worker in self._mappa_workers_attivi:
            self._mappa_workers_attivi.remove(worker)
        worker.deleteLater()
    
    def _fine_caricamento_asincrono(
        self,
        geojson_payload,
        token=None,
        id_progetto=None,
        firma_dati=None,
        adatta_visuale=True,
    ):
        if token is not None and token != self._token_caricamento_mappa:
            print("ℹ️ Cache Mappa: risultato di caricamento superato da una richiesta più recente, scartato.")
            return
        if id_progetto != getattr(self.parent_app, "current_progetto_id", None):
            print("Cache Mappa: risultato ignorato perché il progetto attivo è cambiato.")
            return
        import json
        # NOTA: l'invio dati al server Flask (requests.post) è stato spostato dentro
        # WorkerCaricamentoMappa, così questa funzione, eseguita sul thread
        # dell'interfaccia, non fa più chiamate di rete bloccanti.
        stringa_geojson = json.dumps(geojson_payload)
        js_code = (
            "if(window.aggiornaMappaGeoJSON) "
            f"{{ window.aggiornaMappaGeoJSON({stringa_geojson}, "
            f"{str(adatta_visuale).lower()}); }}"
        )
        self.web_view.page().runJavaScript(js_code)
        self.ultimo_progetto_id_caricato = id_progetto
        self._firma_dati_mappa_caricati = firma_dati
        if firma_dati is not None:
            self._cache_per_progetto[id_progetto] = {
                "firma": firma_dati,
                "geojson": geojson_payload,
            }
        setattr(self.parent_app, "mappa_necessita_aggiornamento", False)
        print("✅ Caricamento asincrono completato ed iniettato con successo.")

    def _mostra_cache_progetto(self, id_progetto, geojson_payload):
        """Ripristina nel browser il GeoJSON in memoria senza avviare un worker."""
        payload = json.dumps(geojson_payload)
        # Usa il bbox del payload per ricentrare come nel caricamento dal worker.
        self.web_view.page().runJavaScript(
            "if(window.aggiornaMappaGeoJSON) "
            f"{{ window.aggiornaMappaGeoJSON({payload}, true); }}"
        )
        print(
            f"ℹ️ Cache Mappa: dati del progetto {id_progetto} "
            "ripristinati senza ricalcolo."
        )

    def open_map_manager(self):
        dialog = MapManagerDialog(self)
        dialog.exec()
        self.reload_map()


class WorkerAnalisiSuperficiOffline(QThread):
    """
    Calcola in background (fuori dal thread dell'interfaccia) la ripartizione
    superfici/divieti bici di un progetto, leggendo solo le mappe locali già
    scaricate. Nessuna chiamata di rete: usa service/superfici_service.py,
    che a sua volta rilegge la cache già salvata quando possibile.
    """
    analisi_completata = Signal(dict)

    def __init__(self, id_progetto, parent=None):
        super().__init__(parent)
        self.id_progetto = id_progetto
        self._annullato = False

    def request_stop(self):
        """Chiede al worker di interrompersi il prima possibile (es. l'utente
        ha già cambiato percorso e il risultato non servirebbe più): senza
        questo, un'analisi pesante su un percorso enorme continuava a
        girare in sottofondo anche quando ormai inutile, rallentando i
        calcoli successivi mettendosi in coda dietro di essa."""
        self._annullato = True

    def run(self):
        try:
            from service.superfici_service import analizza_superfici_progetto
            risultato = analizza_superfici_progetto(
                self.id_progetto, deve_continuare=lambda: not self._annullato
            )
        except Exception as errore:
            risultato = {"disponibile": False, "motivo": f"Errore durante l'analisi offline: {errore}"}
        self.analisi_completata.emit(risultato)


class WorkerNomiLuoghi(QThread):
    """
    Risolve in background (fuori dal thread dell'interfaccia) il nome del
    luogo più vicino a una o più coordinate, leggendo solo le mappe locali
    già scaricate (nessuna chiamata di rete). Usato dal pannello per
    mostrare "Aosta" invece di "45.737200, 7.315500".
    """
    nomi_pronti = Signal(object)

    def __init__(self, richieste, parent=None):
        super().__init__(parent)
        # richieste: lista di dict {"chiave": ..., "lat": ..., "lon": ...}
        self.richieste = list(richieste or [])
        self._annullato = False

    def request_stop(self):
        """Vedi WorkerAnalisiSuperficiOffline.request_stop: stessa logica."""
        self._annullato = True

    def run(self):
        from service.geocodifica_offline_service import nome_luogo_da_coordinate
        risultati = {}
        for richiesta in self.richieste:
            if self._annullato:
                break
            try:
                nome = nome_luogo_da_coordinate(richiesta["lat"], richiesta["lon"])
            except Exception as errore:
                print(f"Nota: geocodifica offline non riuscita: {errore}")
                nome = None
            risultati[richiesta["chiave"]] = nome or f"{richiesta['lat']:.6f}, {richiesta['lon']:.6f}"
        self.nomi_pronti.emit(risultati)


class WorkerAltimetria(QThread):
    """
    Legge in background (fuori dal thread dell'interfaccia) i file GPX di un
    percorso per calcolare altitudine massima e minima. Con percorsi molto
    lunghi (centinaia di tappe) questa lettura può richiedere parecchi
    secondi: farla sul thread principale bloccava l'intera applicazione.
    """
    altimetria_pronta = Signal(dict)

    def __init__(self, nomi_file, parent=None):
        super().__init__(parent)
        self.nomi_file = list(nomi_file or [])
        self._annullato = False

    def request_stop(self):
        """Vedi WorkerAnalisiSuperficiOffline.request_stop: stessa logica."""
        self._annullato = True

    def run(self):
        quote = []
        for nome_file, id_progetto in self.nomi_file:
            if self._annullato:
                break
            percorso_gpx = trova_percorso_gpx(
                nome_file, id_progetto, directory_gpx=GPX_DIR
            )
            if percorso_gpx is None:
                continue
            try:
                with open(percorso_gpx, "r", encoding="utf-8", errors="ignore") as file_gpx:
                    traccia = gpxpy.parse(file_gpx)
                quote.extend(
                    punto.elevation
                    for track in traccia.tracks
                    for segmento in track.segments
                    for punto in segmento.points
                    if punto.elevation is not None
                )
            except Exception as errore_lettura:
                print(f"Nota: impossibile leggere l'altimetria di {nome_file}: {errore_lettura}")

        risultato = {
            "massima": max(quote) if quote else None,
            "minima": min(quote) if quote else None,
        }
        self.altimetria_pronta.emit(risultato)


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

    def _geocodifica(self, luogo):
        coordinate = re.fullmatch(
            r"\s*([-+]?\d+(?:\.\d+)?)\s*[,;]\s*([-+]?\d+(?:\.\d+)?)\s*",
            luogo,
        )
        if coordinate:
            latitudine, longitudine = map(float, coordinate.groups())
            if -90 <= latitudine <= 90 and -180 <= longitudine <= 180:
                return latitudine, longitudine
            raise ValueError(f"Coordinate fuori intervallo: '{luogo}'.")

        return cerca_coordinate_luogo(luogo)

    def _profilo_brouter(self):
        if "strada" in self.profilo.casefold():
            return "fastbike"
        return "trekking"

    def run(self):
        try:
            luoghi = [self.partenza, *self.punti_passaggio, self.destinazione]
            coordinate_luoghi = [
                self._geocodifica(luogo) for luogo in luoghi
            ]

            if len(set(coordinate_luoghi)) != len(coordinate_luoghi):
                raise ValueError("Due o più punti inseriti corrispondono alla stessa posizione.")

            lonlats = "|".join(
                f"{longitudine},{latitudine}"
                for latitudine, longitudine in coordinate_luoghi
            )

            risposta = requests.get(
                BROUTER_URL,
                params={
                    "lonlats": lonlats,
                    "profile": self._profilo_brouter(),
                    "alternativeidx": 0,
                    "format": "geojson",
                },
                timeout=320,
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


# Worker che legge i GPX esistenti e prepara le geometrie per MapLibre.
class WorkerCaricamentoMappa(QThread):
    elaborazione_completata = Signal(dict)

    def __init__(self, p_id, db_n, token_caricamento, leggi_token_corrente):
        super().__init__()
        self.p_id = p_id
        self.db_n = db_n
        self.token_caricamento = token_caricamento
        self.leggi_token_corrente = leggi_token_corrente

    def run(self):
        # La lettura di DB e GPX e la costruzione del GeoJSON stanno nel servizio (senza Qt).
        payload = costruisci_geojson_progetto(self.p_id, self.db_n, directory_gpx=GPX_DIR)

        # I worker superati non devono sovrascrivere i dati correnti sul server Flask.
        if self.leggi_token_corrente() == self.token_caricamento:
            # La richiesta resta nel thread in background per non bloccare la GUI.
            try:
                requests.post("http://127.0.0.1:8080/api/set-gpx-data", json=payload, timeout=10)
            except Exception as errore_rete:
                print(f"Nota: Sincronizzazione Flask in background bypassata: {errore_rete}")
        else:
            print(
                f"Cache Mappa: invio Flask del percorso ID {self.p_id} "
                "saltato perché il worker è superato."
            )

        self.elaborazione_completata.emit(payload)
