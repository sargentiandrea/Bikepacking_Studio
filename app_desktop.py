import io
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sqlite3
import folium
import service.audit_service
import service.clima_service
import gpxpy
import gpxpy.gpx
import threading
import http.server
import socketserver
import webbrowser
import shutil
import math
import requests
import json
import urllib.request

from service.map_server import start_local_map_server
# Avvia il server delle mappe locale su porta 8080
start_local_map_server(port=8080)
from PySide6.QtCore import Signal, QTimer, QObject, Qt, QUrl
from datetime import datetime
# -- Nuovi Moduli GUI --
from gui.dashboard import DashboardPage
from gui.mappa import MappaWidget

class DoganeSignals(QObject):
    finito = Signal(list)
class ClimaSignals(QObject):
    finito = Signal(list)

# Import dei moduli interni del progetto
import database.database_setup as database
database.inizializza_database()
from service.dogane_service import analizza_dogane_progetto, recupera_dogane_salvate

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QLabel, QStackedWidget, 
                             QFrame, QFileDialog, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QDialog, QFormLayout, 
                             QLineEdit, QListWidget, QListWidgetItem, QComboBox, QTextEdit, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QFont, QDragEnterEvent, QDropEvent
from PySide6.QtWebEngineWidgets import QWebEngineView
# --- FORZATURA ACCELERAZIONE HARDWARE (ANTI-SCHERMO BIANCO) ---
os.environ["QT_WEBENGINE_DISABLE_GPU"] = "0"
QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
# --------------------------------------------------------------


from service.config import DB_NAME
PORT = 8055

MAPPA_PREFISSI_BLOCCHI = {
    "ITA": "Italia (ITA)",
    "MED": "Mediterraneo (MED)",
    "AFR": "Africa (AFR)",
    "TUR": "Turchia (TUR)",
    "EUR": "Europa (EUR)",
    "ASI": "Asia (ASI)",
    "AME": "America (AME)",
    "CINA": "Cina (CINA)",
    "GIAP": "Giappone (GIAP)",
    "CORE": "Corea del sud (CORE)",
    "IND": "India (IND)",
    "HAIN": "Isola di Hainan (HAIN)",
    "MALE": "Malesia (MALE)",
    "SRI": "Srilanka (SRI)",
    "SUMA": "Sumatra (SUMA)",
    "AUS": "Australia (AUS)",
    "NWZ": "Nuova Zelanda (NWZ)"
}
STILI_TRASPORTI = {
    "Traghetto / Nave": {"color": "#00a8ff", "dashArray": "8, 8", "icon": "🚢"},
    "Aereo":            {"color": "#9b59b6", "dashArray": "5, 10", "icon": "✈️"},
    "Treno":            {"color": "#f39c12", "dashArray": "10, 5", "icon": "🚆"},
    "Bus / Pick-up":    {"color": "#f1c40f", "dashArray": "6, 6",  "icon": "🚌"},
    "Altro / Personale":{"color": "#1abc9c", "dashArray": "4, 4",  "icon": "🚚"}
}

def inizializza_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # ... resto del codice ...
    cursor.execute('''
        
        CREATE TABLE IF NOT EXISTS progetti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descrizione TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tappe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_progetto INTEGER,
            sequenza INTEGER,
            blocco TEXT,
            nome_file TEXT,
            start_lat REAL,
            start_lon REAL,
            end_lat REAL,
            end_lon REAL,
            distanza_km REAL,
            stato TEXT DEFAULT 'ATTIVA',
            FOREIGN KEY (id_progetto) REFERENCES progetti(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocchi_ordine (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_progetto INTEGER,
            nome_blocco TEXT,
            ordine INTEGER,
            FOREIGN KEY (id_progetto) REFERENCES progetti(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS allarmi_percorso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_progetto INTEGER,
            tappa_origine_id INTEGER,
            tappa_destinazione_id INTEGER,
            tipo_allarme TEXT,
            messaggio TEXT,
            risolto INTEGER DEFAULT 0,
            FOREIGN KEY (id_progetto) REFERENCES progetti(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trasferimenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_progetto INTEGER,
            tipo_mezzo TEXT,
            vettore TEXT,
            da_luogo TEXT,
            a_luogo TEXT,
            durata TEXT,
            costo_eur REAL,
            note TEXT,
            start_lat REAL,
            start_lon REAL,
            end_lat REAL,
            end_lon REAL,
            FOREIGN KEY (id_progetto) REFERENCES progetti(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dogane_progetto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_progetto INTEGER,
            ordine_progressivo INTEGER,
            codice_iso2 TEXT,
            paese_nome TEXT,
            regione_area TEXT,
            requisito_passaporto TEXT,
            tipo_visto TEXT,
            valuta TEXT,
            roaming_info TEXT,
            drone_policy TEXT,
            transitabile_bici INTEGER,
            stato_valico TEXT,
            valico_vicino_nome TEXT,
            valico_vicino_dist_km REAL,
            FOREIGN KEY (id_progetto) REFERENCES progetti(id)
        )
    ''')
    
def determina_blocco_da_nome_file(nome_file):
    clean_name = os.path.basename(nome_file).upper().strip()
    if len(clean_name) >= 3 and clean_name[:3].isalpha():
        prefisso = clean_name[:3]
        return MAPPA_PREFISSI_BLOCCHI.get(prefisso, f"Area {prefisso}")
    return "Generale"

def calcola_distanza_haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def ottieni_nome_localita(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=it"
        headers = {'User-Agent': 'BikepackingStudioApp/2.0'}
        resp = requests.get(url, headers=headers, timeout=4)
        if resp.status_code == 200:
            data = resp.json().get('address', {})
            citta = data.get('city') or data.get('town') or data.get('village') or data.get('county') or "Località sconosciuta"
            stato = data.get('country', '')
            return f"{citta} ({stato})" if stato else citta
    except Exception as e:
        print("Errore Reverse Geocoding:", e)
    return f"{round(lat, 3)}, {round(lon, 3)}"

class LocalMapServer:
    _thread = None

    @classmethod
    def start_server(cls):
        if cls._thread is None:
            handler = http.server.SimpleHTTPRequestHandler
            def run():
                try:
                    with socketserver.TCPServer(("", PORT), handler) as httpd:
                        httpd.serve_forever()
                except Exception as e:
                    print("Server già attivo:", e)
            cls._thread = threading.Thread(target=run, daemon=True)
            cls._thread.start()

class DropAreaGPX(QFrame):
    files_dropped = Signal(list)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QFrame { border: 2px dashed #0e639c; border-radius: 10px; background-color: #2d2d30; }
            QFrame:hover { background-color: #3e3e42; border-color: #007acc; }
        """)
        layout = QVBoxLayout(self)
        self.label = QLabel("📥 Trascina qui i tuoi file GPX per questo percorso")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Arial", 11))
        self.label.setStyleSheet("color: #cccccc; border: none; background: transparent;")
        layout.addWidget(self.label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        filepaths = [u.toLocalFile() for u in urls if u.toLocalFile().lower().endswith('.gpx')]
        if filepaths:
            self.files_dropped.emit(filepaths)

class GestoreBlocchiWidget(QWidget):
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

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT blocco FROM tappe WHERE id_progetto = ?", (pid,))
        blocchi_reali = [r[0] if r[0] else "Generale" for r in cursor.fetchall()]

        cursor.execute("SELECT nome_blocco FROM blocchi_ordine WHERE id_progetto = ? ORDER BY ordine ASC", (pid,))
        blocchi_salvati = [r[0] for r in cursor.fetchall()]

        blocchi_ordinati = [b for b in blocchi_salvati if b in blocchi_reali]
        for b in blocchi_reali:
            if b not in blocchi_ordinati:
                blocchi_ordinati.append(b)

        conn.close()

        for nome_blocco in blocchi_ordinati:
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

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM blocchi_ordine WHERE id_progetto = ?", (pid,))

        for pos, nome_blocco in enumerate(nuovo_ordine_blocchi, start=1):
            cursor.execute("INSERT INTO blocchi_ordine (id_progetto, nome_blocco, ordine) VALUES (?, ?, ?)", (pid, nome_blocco, pos))

        nuova_seq = 1
        for nome_blocco in nuovo_ordine_blocchi:
            cursor.execute("SELECT id FROM tappe WHERE id_progetto = ? AND (blocco = ? OR (blocco IS NULL AND ? = 'Generale')) ORDER BY sequenza ASC", (pid, nome_blocco, nome_blocco))
            tappe_blocco = cursor.fetchall()
            for t in tappe_blocco:
                cursor.execute("UPDATE tappe SET sequenza = ? WHERE id = ?", (nuova_seq, t[0]))
                nuova_seq += 1

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Sequenza Salvata", "L'ordine dei blocchi è stato salvato definitivamente!")
        
        self.parent_app.esegui_audit_automatico()
        self.parent_app.mappa_necessita_aggiornamento = True
        self.parent_app.aggiorna_tabella_tappe()
        self.parent_app.aggiorna_tabella_allarmi()

class BikepackingStudioApp(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bikepacking Studio - Native Control Room")
        
        # Rileva lo schermo del PC e calcola una dimensione proporzionata (85%)
        screen = QApplication.primaryScreen().availableGeometry()
        app_width = int(screen.width() * 0.90)
        app_height = int(screen.height() * 0.90)
        
        # Centra la finestra nello schermo
        x = screen.x() + (screen.width() - app_width) // 2
        y = screen.y() + (screen.height() - app_height) // 2
        
        self.setGeometry(x, y, app_width, app_height)
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")

        self.current_progetto_id = None
        self.current_progetto_nome = ""
        self.mappa_necessita_aggiornamento = True

        LocalMapServer.start_server()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setFixedWidth(85)
        sidebar.setStyleSheet(
            "background-color: #252526; border-right: 1px solid #3e3e42;"
            "QPushButton { font-size: 20px; padding: 10px; }"  # <-- Ingrandisce le emoji e dà respiro ai click
        )
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)


        # 1. Pulsanti di navigazione ridotti a icone/compatti con Tooltip
        self.btn_dashboard = self.crea_bottone_navigazione("📂")
        self.btn_dashboard.setToolTip("Spedizioni & Archivio")
        
        self.btn_blocchi = self.crea_bottone_navigazione("🧩")
        self.btn_blocchi.setToolTip("Gestione Blocchi")
        
        self.btn_mappa = self.crea_bottone_navigazione("🗺️")
        self.btn_mappa.setToolTip("Hub Mappa & Territorio")
        
        self.btn_audit = self.crea_bottone_navigazione("⚠️")
        self.btn_audit.setToolTip("Audit & Control Room")
        
        self.btn_trasporti = self.crea_bottone_navigazione("🚢")
        self.btn_trasporti.setToolTip("Logistica & Trasferimenti")
        
        self.btn_dogane = self.crea_bottone_navigazione("🛂")
        self.btn_dogane.setToolTip("Dogane & Confini")
        
        self.btn_clima = self.crea_bottone_navigazione("🗓️")
        self.btn_clima.setToolTip("Catena Stagionale & Clima")
        
        self.btn_stats = self.crea_bottone_navigazione("📊")
        self.btn_stats.setToolTip("Totali & Statistiche")
        
        self.btn_budget = self.crea_bottone_navigazione("💰")
        self.btn_budget.setToolTip("Budget & Attrezzatura")

        # 2. Inserimento dei pulsanti nel menu laterale
        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_blocchi)
        sidebar_layout.addWidget(self.btn_mappa)
        sidebar_layout.addWidget(self.btn_audit)
        sidebar_layout.addWidget(self.btn_trasporti)
        sidebar_layout.addWidget(self.btn_dogane)
        sidebar_layout.addWidget(self.btn_clima)
        sidebar_layout.addWidget(self.btn_stats)
        sidebar_layout.addWidget(self.btn_budget)
        sidebar_layout.addStretch()

        # 3. Creazione del contenitore unico per le pagine
        self.stacked_widget = QStackedWidget()

        # 4. Creazione fisica delle pagine
        # --- Stacked Widget (Contenitore Pagine) ---
        self.stacked_widget = QStackedWidget()
        self.page_blocchi = GestoreBlocchiWidget(self)
        self.page_mappa = self.crea_pagina_mappa()
        self.page_audit = self.crea_pagina_audit()
        self.page_trasporti = self.crea_pagina_trasporti()
        self.page_dogane = self.crea_pagina_dogane()
        self.page_clima = self.crea_pagina_clima()
        self.page_stats = self.crea_pagina_statistiche()
        self.page_budget = self.crea_pagina_placeholder(
            "💰 Financial & Equipment Manager",
            "Calcolo spese e ammortamento.",
        )

        # 5. Registrazione ordinata delle pagine nello QStackedWidget
        # --- Stacked Widget (Contenitore Pagine) ---
        self.stacked_widget = QStackedWidget()

        # Pagina 1: Dashboard (Caricata dal nuovo modulo esterno)
        # Inizializzi la dashboard
        self.page_dashboard = DashboardPage(self)

        # Colleghi il segnale della dashboard a una funzione di coordinamento pulita
        self.page_dashboard.progetto_selezionato_signal.connect(self.gestisci_cambio_progetto)        
        
        self.stacked_widget.addWidget(self.page_dashboard) # <--- La aggiungiamo allo stack

        # ... (il resto del tuo init_ui che aggiunge le altre pagine)
        self.stacked_widget.addWidget(self.page_blocchi)    # Indice 1
        self.stacked_widget.addWidget(self.page_mappa)      # Indice 2
        self.stacked_widget.addWidget(self.page_audit)      # Indice 3
        self.stacked_widget.addWidget(self.page_trasporti)  # Indice 4
        self.stacked_widget.addWidget(self.page_dogane)     # Indice 5
        self.stacked_widget.addWidget(self.page_clima)      # Indice 6
        self.stacked_widget.addWidget(self.page_stats)      # Indice 7
        self.stacked_widget.addWidget(self.page_budget)     # Indice 8
        
        # 6. Collegamento dei click dei pulsanti
        self.btn_dashboard.clicked.connect(lambda: self.cambia_pagina(0))
        self.btn_blocchi.clicked.connect(lambda: self.cambia_pagina(1))
        self.btn_mappa.clicked.connect(lambda: self.cambia_pagina(2))
        self.btn_audit.clicked.connect(lambda: self.cambia_pagina(3))
        self.btn_trasporti.clicked.connect(lambda: self.cambia_pagina(4))
        self.btn_dogane.clicked.connect(lambda: self.cambia_pagina(5))
        self.btn_clima.clicked.connect(self.apri_pagina_clima)
        self.btn_stats.clicked.connect(self.apri_pagina_statistiche)
        self.btn_budget.clicked.connect(lambda: self.cambia_pagina(8))
        
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget)

    
    def gestisci_cambio_progetto(self, id_progetto, nome_percorso):
        """Aggiorna lo stato globale della finestra principale quando la dashboard cambia progetto."""
        self.current_progetto_id = id_progetto
        # Segnamo che la mappa dovrà essere aggiornata quando l'utente aprirà la pagina dedicata
        self.mappa_necessita_aggiornamento = True
            
    def crea_bottone_navigazione(self, testo):
        btn = QPushButton(testo)
        btn.setFont(QFont("Segoe UI Emoji", 20))  # Font grande per le icone
        btn.setStyleSheet("""
            QPushButton { 
                background-color: transparent; 
                color: #cccccc; 
                text-align: center; 
                padding: 12px 0px; 
                border: none; 
                border-radius: 5px; 
            }
            QPushButton:hover { 
                background-color: #37373d; 
                color: #ffffff; 
            }
            QPushButton:pressed { 
                background-color: #0e639c; 
                color: #ffffff; 
            }
        """)
        return btn
    
    def crea_pagina_mappa(self):
        # Istanziamo direttamente il widget modulare corretto e pulito dal file gui/mappa.py
        self.page_mappa = MappaWidget(self)
        return self.page_mappa
    
    def crea_pagina_audit(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 25, 25, 25)

        lbl_titolo = QLabel("⚠️ Control Room & Audit Qualità Percorso")
        lbl_titolo.setFont(QFont("Arial", 16, QFont.Bold))
        lbl_titolo.setStyleSheet("color: #0e639c;")
        layout.addWidget(lbl_titolo)

        self.lbl_stato_health = QLabel("Seleziona un percorso per verificare gli allarmi.")
        self.lbl_stato_health.setFont(QFont("Arial", 11))
        layout.addWidget(self.lbl_stato_health)

        layout.addSpacing(10)

        self.table_allarmi = QTableWidget()
        self.table_allarmi.setColumnCount(4)
        self.table_allarmi.setHorizontalHeaderLabels(["Tipo Criticità", "Messaggio / Dettaglio Completo", "Stato", "Opzioni & Soluzioni Proposte"])
        
        self.table_allarmi.verticalHeader().setDefaultSectionSize(55)
        header = self.table_allarmi.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Interactive)

        self.table_allarmi.setColumnWidth(0, 160)
        self.table_allarmi.setColumnWidth(2, 90)
        self.table_allarmi.setColumnWidth(3, 380)

        self.table_allarmi.setStyleSheet("""
            QTableWidget { background-color: #252526; gridline-color: #3e3e42; color: #ffffff; border: 1px solid #3e3e42; border-radius: 5px; }
            QTableWidget::item { padding: 6px; }
            QHeaderView::section { background-color: #2d2d30; color: #a93226; font-weight: bold; padding: 8px; }
        """)
        layout.addWidget(self.table_allarmi)
        return widget

    def carica_lista_percorsi(self):
        """Reindirizza al nuovo modulo DashboardPage."""
        # Se il programma prova a chiamare il vecchio metodo, 
        # diciamo al nuovo modulo di eseguire la sua funzione.
        self.page_dashboard.carica_lista_percorsi()
    
    def apri_percorso_selezionato(self, item):
        pid, nome = item.data(Qt.UserRole)
        self.current_progetto_id = pid
        self.current_progetto_nome = nome
        self.lbl_nome_percorso_attivo.setText(f"Percorso: {nome}")
        
        self.stack_archivio.setCurrentIndex(1)
        self.mappa_necessita_aggiornamento = True
        self.esegui_audit_automatico()
        self.aggiorna_tabella_tappe()
        self.aggiorna_tabella_allarmi()

    def crea_nuovo_progetto_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("✨ Pianificatore Nuovo Itinerario Interattivo")
        dialog.setFixedWidth(450)
        dialog.setStyleSheet("background-color: #2d2d30; color: white;")
        layout = QFormLayout(dialog)
        layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        # 1. Nome Percorso
        txt_nome = QLineEdit()
        txt_nome.setPlaceholderText("Es. Avventura Gravel sui Monti")
        txt_nome.setStyleSheet("background-color: #3e3e42; padding: 6px; color: white; border: 1px solid #555;")
        
        # 2. Profilo Bici
        combo_bici = QComboBox()
        combo_bici.addItems([
            "Gravel / Bici da Viaggio", 
            "Bici da Strada (Asfalto)", 
            "Mountain Bike (Sterrato / Trail)", 
            "E-Bike Tourer"
        ])
        combo_bici.setStyleSheet("background-color: #3e3e42; padding: 6px; color: white; border: 1px solid #555;")

        # 3. Preferenze Strada
        combo_strada = QComboBox()
        combo_strada.addItems([
            "Bilanciato (Consigliato)", 
            "Evita traffico pesante", 
            "Preferisci strade sterrate / ciclabili", 
            "Massima velocità (Asfalto prioritario)"
        ])
        combo_strada.setStyleSheet("background-color: #3e3e42; padding: 6px; color: white; border: 1px solid #555;")

        # 4. Durata Prevista
        combo_durata = QComboBox()
        combo_durata.addItems([
            "Escursione in Giornata", 
            "Weekend (2-3 giorni)", 
            "Viaggio a tappe (Bikepacking Lunga Durata)"
        ])
        combo_durata.setStyleSheet("background-color: #3e3e42; padding: 6px; color: white; border: 1px solid #555;")

        # 5. Note / Descrizione opzionale
        txt_desc = QLineEdit()
        txt_desc.setPlaceholderText("Note opzionali...")
        txt_desc.setStyleSheet("background-color: #3e3e42; padding: 6px; color: white; border: 1px solid #555;")

        layout.addRow("<b>Nome Percorso:</b>", txt_nome)
        layout.addRow("<b>Profilo Bici:</b>", combo_bici)
        layout.addRow("<b>Preferenza Strade:</b>", combo_strada)
        layout.addRow("<b>Durata Prevista:</b>", combo_durata)
        layout.addRow("<b>Note / Descrizione:</b>", txt_desc)

        btn_salva = QPushButton("🚀 Crea e Apri sulla Mappa")
        btn_salva.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold; border-radius: 4px; margin-top: 10px;")
        
        def salva():
            nome = txt_nome.text().strip()
            if nome:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                # Salviamo il progetto di base (se vuoi puoi estendere la tabella in seguito per salvare anche le preferenze)
                cursor.execute(
                    "INSERT INTO progetti (nome, descrizione) VALUES (?, ?)", 
                    (nome, txt_desc.text().strip())
                )
                new_id = cursor.lastrowid
                conn.commit()
                conn.close()
                dialog.accept()
                
                self.carica_lista_percorsi()
                self.current_progetto_id = new_id
                self.current_progetto_nome = nome
                self.lbl_nome_percorso_attivo.setText(f"Percorso: {nome}")
                
                # Stampiamo i dati raccolti per conferma
                print(f"✨ Creato percorso '{nome}' | Bici: {combo_bici.currentText()} | Strade: {combo_strada.currentText()}")
                
                # Per ora manteniamo il flusso standard finché non colleghiamo il salto pulito alla mappa
                self.stack_archivio.setCurrentIndex(1)
                self.aggiorna_tabella_tappe()

        btn_salva.clicked.connect(salva)
        layout.addRow(btn_salva)
        dialog.exec()
        
    def apri_selettore_file(self):
        """Apre il file dialog e passa i file selezionati alla pagina Dashboard attiva."""
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Seleziona File GPX", 
            "", 
            "File GPX (*.gpx);;Tutti i file (*.*)"
        )
        
        if files:
            # Prende la pagina attiva sullo schermo
            current_widget = self.stack.currentWidget()
            
            # Invia i file alla dashboard
            if hasattr(current_widget, 'elabora_files_gpx'):
                current_widget.elabora_files_gpx(files)
            elif hasattr(self, 'dashboard_page') and self.dashboard_page:
                self.dashboard_page.elabora_files_gpx(files)    
    
    def elabora_files_gpx(self, filepaths):
        """Reindirizza l'elaborazione dei file GPX alla pagina Dashboard modulare."""
        if hasattr(self, 'dashboard_page') and self.dashboard_page:
            self.dashboard_page.elabora_files_gpx(filepaths)
    
    def esegui_audit_automatico(self):
        """Esegue il controllo dell'integrità del percorso attivo."""
        if not self.current_progetto_id:
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Recupero tappe attive ordinate
        cursor.execute("""
            SELECT id, sequenza, nome_file, start_lat, start_lon, end_lat, end_lon 
            FROM tappe 
            WHERE id_progetto = ? AND stato = 'ATTIVA' 
            ORDER BY sequenza ASC
        """, (self.current_progetto_id,))
        tappe = cursor.fetchall()

        # Recupero allarmi già segnati come risolti dall'utente
        cursor.execute("""
            SELECT tappa_origine_id, tappa_destinazione_id 
            FROM allarmi_percorso 
            WHERE id_progetto = ? AND risolto = 1
        """, (self.current_progetto_id,))
        risolti_set = set(cursor.fetchall())

        # Recupero i trasferimenti già inseriti (traghetti, treni, ecc.)
        cursor.execute("""
            SELECT start_lat, start_lon, end_lat, end_lon 
            FROM trasferimenti 
            WHERE id_progetto = ?
        """, (self.current_progetto_id,))
        trasferimenti = cursor.fetchall()

        # Pulisce i vecchi allarmi non risolti per ricalcolarli
        cursor.execute("DELETE FROM allarmi_percorso WHERE id_progetto = ?", (self.current_progetto_id,))

        for i in range(len(tappe) - 1):
            t_curr = tappe[i]
            t_next = tappe[i+1]
            
            end_lat, end_lon = t_curr[5], t_curr[6]
            start_lat, start_lon = t_next[3], t_next[4]

            if None in (end_lat, end_lon, start_lat, start_lon):
                continue

            gap_km = calcola_distanza_haversine(end_lat, end_lon, start_lat, start_lon)

            # Se c'è un'interruzione maggiore di 3 km
            if gap_km > 3.0:
                # Controlla se il buco è già coperto da un trasferimento navale/ferroviario
                coperto = any(
                    abs(t[0] - end_lat) < 0.01 and abs(t[1] - end_lon) < 0.01 and
                    abs(t[2] - start_lat) < 0.01 and abs(t[3] - start_lon) < 0.01
                    for t in trasferimenti if t[0] and t[1] and t[2] and t[3]
                )

                if not coperto:
                    tipo = 'GAP_TERRA' if gap_km <= 30.0 else 'GAP_AMPIO'
                    msg = f"Interruzione di {round(gap_km, 1)} km tra '{t_curr[2]}' e '{t_next[2]}'."
                    is_risolto = 1 if (t_curr[0], t_next[0]) in risolti_set else 0

                    cursor.execute("""
                        INSERT INTO allarmi_percorso 
                        (id_progetto, tappa_origine_id, tappa_destinazione_id, tipo_allarme, messaggio, risolto)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (self.current_progetto_id, t_curr[0], t_next[0], tipo, msg, is_risolto))

        conn.commit()
        conn.close()
    
    def raccorda_traccia_istantaneo(self, t1_id, t2_id, t1_nome, t2_nome):
        """Richiama il servizio esterno per generare il raccordo e aggiorna la UI."""
        if not self.current_progetto_id:
            return

        # Sfruttiamo il modulo esterno per fare tutto il lavoro pesante (routing, file GPX, DB)
        nome_raccordo, dist_raccordo, is_linea_retta = service.audit_service.genera_raccordo_gpx(
            self.current_progetto_id, t1_id, t2_id, t1_nome, t2_nome
        )

        if not nome_raccordo:
            return

        # Aggiornamenti dell'interfaccia grafica
        self.esegui_audit_automatico()
        self.mappa_necessita_aggiornamento = True
        self.aggiorna_tabella_tappe()
        self.aggiorna_tabella_trasferimenti()
        if hasattr(self, 'aggiorna_tabella_allarmi'):
            self.aggiorna_tabella_allarmi()

        # Messaggi di feedback per l'utente
        if is_linea_retta:
            QMessageBox.warning(
                self, 
                "Raccordo Generato (Linea Retta)", 
                f"Impossibile trovare strade ciclabili tra i due punti.\n"
                f"È stata tracciata una linea retta ({round(dist_raccordo, 1)} km) e registrata nella logistica. Verificare manualmente!"
            )
        else:
            QMessageBox.information(
                self, 
                "Raccordo Ciclabile Creato", 
                f"Raccordo generato e registrato nella logistica con successo!\nLunghezza: {round(dist_raccordo, 1)} km"
            )    
    
    def aggiorna_tabella_tappe(self):
        """Reindirizza l'aggiornamento della tabella tappe alla pagina Dashboard modulare."""
        if not self.current_progetto_id:
            return
            
        if hasattr(self, 'dashboard_page') and self.dashboard_page:
            self.dashboard_page.aggiorna_tabella_tappe()
    
    def aggiorna_blocco_tappa(self, tappa_id, nuovo_blocco):
        blocco_val = nuovo_blocco.strip() if nuovo_blocco.strip() else "Generale"
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE tappe SET blocco = ? WHERE id = ?", (blocco_val, tappa_id))
        conn.commit()
        conn.close()

    def toggle_pausa_tappa(self, tappa_id, in_pausa):
        nuovo_stato = 'ATTIVA' if in_pausa else 'SOSPESA'
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE tappe SET stato = ? WHERE id = ?", (nuovo_stato, tappa_id))
        conn.commit()
        conn.close()

        self.esegui_audit_automatico()
        self.mappa_necessita_aggiornamento = True
        self.aggiorna_tabella_tappe()
        self.aggiorna_tabella_allarmi()

    def cambia_ruolo_tappa(self, tappa_id, index):
        mappa_stati = {0: 'ATTIVA', 1: 'VARIANTE', 2: 'SOSPESA'}
        nuovo_stato = mappa_stati[index]

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE tappe SET stato = ? WHERE id = ?", (nuovo_stato, tappa_id))
        conn.commit()
        conn.close()

        self.esegui_audit_automatico()
        self.mappa_necessita_aggiornamento = True
        self.aggiorna_tabella_tappe()
        self.aggiorna_tabella_allarmi()

    def elimina_singola_tappa(self, tappa_id, nome_file):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tappe WHERE id = ?", (tappa_id,))
        conn.commit()
        conn.close()

        filepath = os.path.join(os.getcwd(), "gpx", os.path.basename(nome_file))
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                print("Errore rimozione file:", e)

        self.esegui_audit_automatico()
        self.mappa_necessita_aggiornamento = True
        self.aggiorna_tabella_tappe()
        self.aggiorna_tabella_allarmi()

    def elimina_percorso_corrente(self):
        if not self.current_progetto_id:
            return
        conf = QMessageBox.question(self, "Elimina Percorso", f"Sei sicuro di voler eliminare l'intero percorso '{self.current_progetto_nome}'?", QMessageBox.Yes | QMessageBox.No)
        if conf == QMessageBox.Yes:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM progetti WHERE id = ?", (self.current_progetto_id,))
            cursor.execute("DELETE FROM tappe WHERE id_progetto = ?", (self.current_progetto_id,))
            cursor.execute("DELETE FROM allarmi_percorso WHERE id_progetto = ?", (self.current_progetto_id,))
            cursor.execute("DELETE FROM trasferimenti WHERE id_progetto = ?", (self.current_progetto_id,))
            cursor.execute("DELETE FROM blocchi_ordine WHERE id_progetto = ?", (self.current_progetto_id,))
            conn.commit()
            conn.close()
            
            self.current_progetto_id = None
            self.carica_lista_percorsi()
            self.stack_archivio.setCurrentIndex(0)

    def aggiorna_tabella_allarmi(self):
        if not self.verifica_progetto_attivo():
            if hasattr(self, 'tabella_allarmi'):
                self.tabella_allarmi.setRowCount(0)
            elif hasattr(self, 'table_allarmi'):
                self.table_allarmi.setRowCount(0)
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.tipo_allarme, a.messaggio, a.risolto, a.tappa_origine_id, a.tappa_destinazione_id,
                   t1.nome_file, t2.nome_file, a.id, t1.end_lat, t1.end_lon, t2.start_lat, t2.start_lon
            FROM allarmi_percorso a
            LEFT JOIN tappe t1 ON a.tappa_origine_id = t1.id
            LEFT JOIN tappe t2 ON a.tappa_destinazione_id = t2.id
            WHERE a.id_progetto = ? AND a.risolto = 0
        """, (self.current_progetto_id,))
        rows = cursor.fetchall()
        conn.close()

        if hasattr(self, 'lbl_stato_health'):
            if not rows:
                self.lbl_stato_health.setText("🟢 Nessun allarme attivo: la rotta è continua o coperta da logistica!")
                self.lbl_stato_health.setStyleSheet("color: #28a745; font-weight: bold;")
            else:
                self.lbl_stato_health.setText(f"🔴 Rilevati {len(rows)} GAP/Interruzioni da risolvere lungo il tracciato!")
                self.lbl_stato_health.setStyleSheet("color: #e74c3c; font-weight: bold;")

        self.table_allarmi.setRowCount(len(rows))
        for row_idx, data in enumerate(rows):
            tipo, msg, risolto, t1_id, t2_id, t1_nome, t2_nome, allarme_id, end_lat, end_lon, start_lat, start_lon = data

            item_tipo = QTableWidgetItem("🔗 TERRA" if tipo == 'GAP_TERRA' else "⚠️ GAP AMPIO")
            item_tipo.setTextAlignment(Qt.AlignCenter)
            self.table_allarmi.setItem(row_idx, 0, item_tipo)

            item_msg = QTableWidgetItem(msg)
            item_msg.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table_allarmi.setItem(row_idx, 1, item_msg)

            item_st = QTableWidgetItem("Attivo")
            item_st.setTextAlignment(Qt.AlignCenter)
            self.table_allarmi.setItem(row_idx, 2, item_st)

            panel_azioni = QWidget()
            layout_azioni = QHBoxLayout(panel_azioni)
            layout_azioni.setContentsMargins(2, 2, 2, 2)
            layout_azioni.setSpacing(4)

            # 1. NUOVO PULSANTE: Visualizza Mappa GAP
            btn_mappa_gap = QPushButton("👁️ Mappa GAP")
            btn_mappa_gap.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold; font-size: 11px; padding: 4px;")
            btn_mappa_gap.clicked.connect(lambda _, e_l=end_lat, e_o=end_lon, s_l=start_lat, s_o=start_lon, n1=t1_nome, n2=t2_nome: 
                self.mostra_mappa_gap(e_l, e_o, s_l, s_o, n1, n2)
            )

            # 2. PULSANTE: Raccorda GPX
            btn_raccorda = QPushButton("🔗 Raccorda GPX")
            btn_raccorda.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; font-size: 11px; padding: 4px;")
            btn_raccorda.clicked.connect(lambda _, id1=t1_id, id2=t2_id, n1=t1_nome, n2=t2_nome: self.raccorda_traccia_istantaneo(id1, id2, n1, n2))

            # 3. PULSANTE: Logistica
            btn_trasferimento = QPushButton("🚢 Logistica/Mezzo")
            btn_trasferimento.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; font-size: 11px; padding: 4px;")
            btn_trasferimento.clicked.connect(lambda _, e_lat=end_lat, e_lon=end_lon, s_lat=start_lat, s_lon=start_lon, aid=allarme_id: self.avvia_dialog_logistica_con_geocoding(e_lat, e_lon, s_lat, s_lon, aid))

            # Inseriamo i 3 pulsanti affiancati
            layout_azioni.addWidget(btn_mappa_gap)
            layout_azioni.addWidget(btn_raccorda)
            layout_azioni.addWidget(btn_trasferimento)

            self.table_allarmi.setCellWidget(row_idx, 3, panel_azioni)
    
    def _coordinate_in_nome_luogo(self, lat, lon):
        """Converte Lat/Lon nel nome della città/località tramite OpenStreetMap Nominatim."""
        if not lat or not lon:
            return ""
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}"
            req = urllib.request.Request(url, headers={'User-Agent': 'BikepackingStudioApp/1.0'})
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode())
                address = data.get('address', {})
                citta = address.get('city') or address.get('town') or address.get('village') or address.get('county') or data.get('display_name', '')
                return citta if citta else f"{lat:.4f}, {lon:.4f}"
        except Exception:
            return f"{lat:.4f}, {lon:.4f}"

        self.apri_dialog_trasferimento(
            da_prefill=da_luogo, 
            a_prefill=a_luogo, 
            allarme_id=allarme_id, 
            lat1=end_lat, 
            lon1=end_lon, 
            lat2=start_lat, 
            lon2=start_lon
        )
    
    def rigenera_mappa(self, force=False):
        """
        Delega il lavoro pesante e la gestione dati al modulo gui/mappa.py
        """
        if hasattr(self, 'page_mappa') and hasattr(self.page_mappa, 'rigenera_mappa'):
            self.mappa_necessita_aggiornamento = self.page_mappa.rigenera_mappa(
                current_progetto_id=getattr(self, 'current_progetto_id', None),
                db_name=DB_NAME,
                force=force,
                mappa_necessita_aggiornamento=getattr(self, 'mappa_necessita_aggiornamento', True)
            )

    def apri_in_browser(self):
        self.rigenera_mappa(force=True)
        webbrowser.open("http://127.0.0.1:8080/map")    
    
    def crea_pagina_dogane(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        """Crea la pagina grafica per i Requisiti Doganali con indicatore di stato."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)

        # Titolo della pagina
        lbl_titolo = QLabel("🛂 Requisiti Doganali & Passaggi di Confine")
        lbl_titolo.setFont(QFont("Arial", 18, QFont.Bold))
        lbl_titolo.setStyleSheet("color: #0e639c;")
        layout.addWidget(lbl_titolo)

        # Pulsante per avviare l'analisi
        self.btn_analizza_dogane = QPushButton("🔍 Analizza Confini e Requisiti Doganali")
        self.btn_analizza_dogane.setStyleSheet(
            "padding: 8px 15px; font-weight: bold; background-color: #0e639c; color: white;"
        )
        self.btn_analizza_dogane.clicked.connect(self.esegui_analisi_doganale)
        layout.addWidget(self.btn_analizza_dogane)

        # Label per mostrare lo stato dell'operazione (es. "Analisi in corso...")
        self.lbl_stato_dogane = QLabel("Pronto per l'analisi.")
        self.lbl_stato_dogane.setStyleSheet("color: #aaaaaa; font-style: italic; margin-top: 5px;")
        layout.addWidget(self.lbl_stato_dogane)

        # Tabella per mostrare i dati
        self.tabella_dogane = QTableWidget()
        colonne = [
            "#",
            "Paese",
            "Regione / Area",
            "Passaporto",
            "Tipo Visto",
            "Valuta",
            "Roaming",
            "Drone Policy",
        ]
        self.tabella_dogane.setColumnCount(len(colonne))
        self.tabella_dogane.setHorizontalHeaderLabels(colonne)
        self.tabella_dogane.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabella_dogane)

        return widget

    def esegui_analisi_doganale(self):
        
        # 1. Verifica se un progetto reale è attivo (senza forzare l'ID 1)
        id_progetto = getattr(self, "current_progetto_id", None)

        if not id_progetto:
            self.lbl_stato_dogane.setText("⚠️ Seleziona prima un progetto o un percorso valido!")
            self.tabella_dogane.setRowCount(0)
            return

        # Aggiorna lo stato visivo
        self.btn_analizza_dogane.setEnabled(False)
        self.lbl_stato_dogane.setText("⏳ Analisi GPX e scansione confini in corso...")
        self.tabella_dogane.setRowCount(0)

        # Inizializza il segnale PySide6
        self.sig_dogane = DoganeSignals()
        self.sig_dogane.finito.connect(self.aggiorna_ui_dogane)

        # Avvia il calcolo in un thread separato
        import threading
        threading.Thread(
            target=self._worker_analisi_doganale,
            args=(id_progetto,),
            daemon=True
        ).start()


    def carica_o_analizza_dogane_automatico(self):
        """Controlla se ci sono dati doganali salvati usando il servizio centralizzato."""
        id_progetto = getattr(self, "current_progetto_id", None)
        if not id_progetto:
            return

        # Sfruttiamo il servizio centrale che gestisce il recupero e la pulizia dei dati
        dati_salvati = recupera_dogane_salvate(id_progetto)
        
        if dati_salvati and len(dati_salvati) > 0:
            print(f">>> PAGINA DOGANE: Trovate {len(dati_salvati)} dogane salvate. Caricamento in corso...")
            self.aggiorna_ui_dogane(dati_salvati)
        else:
            print(">>> PAGINA DOGANE: Tabella vuota o nessun dato, avvio analisi automatica...")
            self.esegui_analisi_doganale()                
    
    def _worker_analisi_doganale(self, id_progetto):
        print(">>> THREAD AVVIATO: Sto calcolando i paesi...")
        
        import service.dogane_service

        risultati = service.dogane_service.analizza_dogane_progetto(id_progetto)
        print(f">>> CALCOLO FINITO: Trovati {len(risultati)} risultati. Invio alla GUI...")

        # Invia i dati alla tabella tramite il segnale PySide6
        self.sig_dogane.finito.emit(risultati)

    def aggiorna_ui_dogane(self, dati_dogane):
        """Popola la tabella nel thread principale della GUI."""
        print(">>> AGGIORNAMENTO GUI: Ricevuti dati, riempimento tabella...")
        from PySide6.QtWidgets import QTableWidgetItem
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QFont

        self.tabella_dogane.setRowCount(0)
        
        if not getattr(self, "current_progetto_id", None):
            self.lbl_stato_dogane.setText("⚠️ Nessun percorso o progetto selezionato.")
            self.btn_analizza_dogane.setEnabled(True)
            return

        # Definiamo il font emoji correttamente in cima alla funzione
        font_emoji_cella = QFont("Segoe UI Emoji", 10)

        if dati_dogane:
            for row_idx, riga in enumerate(dati_dogane):
                self.tabella_dogane.insertRow(row_idx)
                for col_idx, valore in enumerate(riga):
                    item = QTableWidgetItem(str(valore) if valore is not None else "")
                    
                    # Applichiamo il font emoji a ogni cella
                    item.setFont(font_emoji_cella)
                    
                    # Rendiamo la tabella non modificabile dall'utente
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    
                    # Centriamo le colonne con testo breve
                    if col_idx in [0, 1, 3, 4, 5, 6]:
                        item.setTextAlignment(Qt.AlignCenter)

                    self.tabella_dogane.setItem(row_idx, col_idx, item)
                    
            self.lbl_stato_dogane.setText(f"✅ Analisi completata. Trovati {len(dati_dogane)} paesi/transiti.")
        else:
            self.lbl_stato_dogane.setText("⚠️ Nessuna traccia o confine trovato per il progetto attivo.")
        
        self.btn_analizza_dogane.setEnabled(True)    
    
    def crea_pagina_trasporti(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)

        lbl_titolo = QLabel("🚢 Logistica & Trasferimenti (Gap Tra Tappe)")
        lbl_titolo.setFont(QFont("Arial", 18, QFont.Bold))
        lbl_titolo.setStyleSheet("color: #0e639c;")
        layout.addWidget(lbl_titolo)

        btn_aggiungi = QPushButton("➕ Aggiungi Nuovo Trasferimento / Logistica")
        btn_aggiungi.setFont(QFont("Arial", 10, QFont.Bold))
        btn_aggiungi.setStyleSheet("background-color: #0e639c; color: white; padding: 10px; border-radius: 5px;")
        btn_aggiungi.clicked.connect(lambda: self.apri_dialog_trasferimento())
        layout.addWidget(btn_aggiungi)

        self.table_trasporti = QTableWidget()
        self.table_trasporti.setColumnCount(8)
        self.table_trasporti.setHorizontalHeaderLabels(["ID", "Mezzo", "Vettore", "Da (Città/Stato)", "A (Città/Stato)", "Durata", "Costo (€)", "Azione"])
        self.table_trasporti.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_trasporti.setStyleSheet("""
            QTableWidget { background-color: #252526; gridline-color: #3e3e42; color: #ffffff; border: 1px solid #3e3e42; border-radius: 5px; }
            QHeaderView::section { background-color: #2d2d30; color: #0e639c; font-weight: bold; padding: 6px; }
        """)
        layout.addWidget(self.table_trasporti)
        return widget

    def crea_pagina_clima(self):
        """Crea la pagina grafica per la Catena Stagionale & Simulatore Meteo."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(15, 15, 15, 15)

        # Intestazione
        lbl_title = QLabel("🗓️ Catena Stagionale & Simulatore Meteo")
        font_title = QFont()
        font_title.setPointSize(14)
        font_title.setBold(True)
        lbl_title.setFont(font_title)
        layout.addWidget(lbl_title)

        # Pannello Controlli
        frame_ctrl = QFrame()
        frame_ctrl.setFrameShape(QFrame.StyledPanel)
        layout_ctrl = QHBoxLayout(frame_ctrl)

        layout_ctrl.addWidget(QLabel("📅 Data Partenza:"))
        from PySide6.QtWidgets import QDateEdit
        from PySide6.QtCore import QDate
        self.date_partenza = QDateEdit()
        self.date_partenza.setCalendarPopup(True)
        self.date_partenza.setDate(QDate.currentDate())
        self.date_partenza.dateChanged.connect(self.esegui_analisi_clima)
        layout_ctrl.addWidget(self.date_partenza)

        layout_ctrl.addSpacing(20)

        layout_ctrl.addWidget(QLabel("💤 Modificatore Riposo (+/- gg):"))
        from PySide6.QtWidgets import QSpinBox
        self.spin_riposo = QSpinBox()
        self.spin_riposo.setRange(-10, 30)
        self.spin_riposo.setValue(0)
        self.spin_riposo.valueChanged.connect(self.esegui_analisi_clima)
        layout_ctrl.addWidget(self.spin_riposo)

        layout_ctrl.addStretch()

        self.btn_rifiata_clima = QPushButton("🔄 Ricalcola Catena")
        self.btn_rifiata_clima.clicked.connect(self.esegui_analisi_clima)
        layout_ctrl.addWidget(self.btn_rifiata_clima)

        layout.addWidget(frame_ctrl)

        # Label Stato
        self.lbl_stato_clima = QLabel("Pronto per l'analisi della catena stagionale.")
        layout.addWidget(self.lbl_stato_clima)

        # Tabella Risultati
        self.tabella_clima = QTableWidget()
        headers = [
            "#", "Blocco", "Tappe", "Km Tot", 
            "Pedalata", "Riposo", "Extra", "Tot GG", 
            "Ingresso", "Uscita", "Mesi Ideali", "Semaforo"
        ]
        self.tabella_clima.setColumnCount(len(headers))
        self.tabella_clima.setHorizontalHeaderLabels(headers)
        self.tabella_clima.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.tabella_clima)
        # Collega la modifica manuale delle celle (es. colonna Extra) al ricalcolo della catena
        self.tabella_clima.cellChanged.connect(self.su_modifica_cella_clima)
        
        return page
    
    def esegui_analisi_clima(self):
        # Se nessun percorso è selezionato, pulisce la tabella e si ferma subito
        if not self.verifica_progetto_attivo():
            self.lbl_stato_clima.setText("⚠️ Nessuna spedizione attiva. Seleziona un percorso dalla Dashboard.")
            self.tabella_clima.setRowCount(0)
            return
        """Avvia il calcolo della catena stagionale in un thread separato."""
        id_progetto = getattr(self, "current_progetto_id", 1) or 1
        
        # Recupera parametri dalla UI
        qdate = self.date_partenza.date()
        dt_partenza = datetime(qdate.year(), qdate.month(), qdate.day())
        mod_riposo = self.spin_riposo.value()

        self.lbl_stato_clima.setText("⏳ Calcolo finestre stagionali e transiti in corso...")
        
        # Segnale per thread-safety
        self.sig_clima = ClimaSignals()
        self.sig_clima.finito.connect(self.aggiorna_ui_clima)

        threading.Thread(
            target=self._worker_analisi_clima,
            args=(id_progetto, dt_partenza, mod_riposo),
            daemon=True
        ).start()

    def _worker_analisi_clima(self, id_progetto, dt_partenza, mod_riposo):
        """Worker eseguito in background."""
        import service.clima_service
        risultati = service.clima_service.calcola_catena_stagionale(
            id_progetto=id_progetto, 
            data_partenza_dt=dt_partenza, 
            modificatore_riposo=mod_riposo
        )
        self.sig_clima.finito.emit(risultati)

    def aggiorna_ui_clima(self, risultati):
        """Aggiorna la tabella GUI con i risultati calcolati e rende editabile la colonna Extra."""
        # Disattiviamo temporaneamente il segnale di modifica per evitare loop durante il caricamento
        self.tabella_clima.blockSignals(True)
        self.tabella_clima.setRowCount(0)
        
        if not risultati:
            self.lbl_stato_clima.setText("⚠️ Nessun blocco/tappa trovata per il progetto attivo.")
            self.tabella_clima.blockSignals(False)
            return

        for row_idx, data in enumerate(risultati):
            self.tabella_clima.insertRow(row_idx)
            
            valori = [
                data["ordine"],
                data["blocco"],
                data["tappe"],
                f"{data['km_totali']} km",
                f"{data['giorni_pedalata']} gg",
                f"{data['giorni_riposo']} gg",
                data["giorni_extra"],  # Salviamo il numero puro per la colonna Extra
                f"{data['giorni_totali']} gg",
                data["data_ingresso"],
                data["data_uscita"],
                data["mesi_ideali"],
                data["semaforo"]
            ]

            for col_idx, val in enumerate(valori):
                item = QTableWidgetItem(str(val))
                
                # Se è la colonna "Extra" (indice 6), la rendiamo modificabile dall'utente
                if col_idx == 6:
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
                    item.setToolTip("Doppio clic per modificare i giorni extra del blocco")
                else:
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

                # Allineamento centrale
                if col_idx in [0, 2, 4, 5, 6, 7, 8, 9, 10]:
                    item.setTextAlignment(Qt.AlignCenter)
                    
                self.tabella_clima.setItem(row_idx, col_idx, item)

        self.tabella_clima.blockSignals(False)
        self.lbl_stato_clima.setText(f"✅ Analisi completata per {len(risultati)} blocchi/aree.")
        
    def su_modifica_cella_clima(self, row, column):
        """Rileva la modifica dei Giorni Extra e ricalcola la catena per tutti i blocchi."""
        # Se è stata modificata la colonna "Extra" (indice 6)
        if column == 6:
            giorni_extra_dict = {}
            for r in range(self.tabella_clima.rowCount()):
                b_item = self.tabella_clima.item(r, 1) # Nome Blocco
                e_item = self.tabella_clima.item(r, 6) # Giorni Extra
                if b_item and e_item:
                    try:
                        val_extra = int(e_item.text().strip())
                    except ValueError:
                        val_extra = 0
                    giorni_extra_dict[b_item.text()] = val_extra

            id_progetto = getattr(self, "current_progetto_id", 1) or 1
            qdate = self.date_partenza.date()
            dt_partenza = datetime(qdate.year(), qdate.month(), qdate.day())
            mod_riposo = self.spin_riposo.value()

            # Salva le nuove impostazioni nel DB ed esegui il ricalcolo a cascata
            import service.clima_service
            service.clima_service.salva_impostazioni_stagione(
                id_progetto=id_progetto,
                data_partenza_str=dt_partenza.strftime("%Y-%m-%d"),
                modificatore_riposo=mod_riposo,
                giorni_extra_dict=giorni_extra_dict
            )

            # Rilancia il ricalcolo per aggiornare le date di tutti i blocchi successivi
            self.esegui_analisi_clima()
    
    def apri_pagina_clima(self):
        """Apre la pagina Clima e avvia il calcolo della catena stagionale."""
        self.stacked_widget.setCurrentWidget(self.page_clima)
        self.esegui_analisi_clima()
    
    def crea_pagina_statistiche(self):
        """Crea la pagina con le KPI Card e le tabelle di metriche altimetriche e fasce costiere."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)

        # Titolo della pagina
        lbl_titolo = QLabel("📊 Totali, Statistiche Avanzate & Fasce Costiere")
        lbl_titolo.setFont(QFont("Arial", 18, QFont.Bold))
        lbl_titolo.setStyleSheet("color: #0e639c;")
        layout.addWidget(lbl_titolo)

        # --- SEZIONE 1: TOP KPI CARDS ---
        kpi_layout = QHBoxLayout()

        self.card_km = QLabel("<b>KM TOTALI</b><br><span style='font-size:20pt;'>0 km</span>")
        self.card_dplus = QLabel("<b>DISLIVELLO +</b><br><span style='font-size:20pt;'>0 m</span>")
        self.card_qmax = QLabel("<b>QUOTA MAX</b><br><span style='font-size:20pt;'>0 m</span>")
        self.card_pendenza = QLabel("<b>PENDENZA MEDIA</b><br><span style='font-size:20pt;'>0 %</span>")

        card_style = """
            QLabel {
                background-color: #252526;
                color: #ffffff;
                border: 1px solid #3e3e42;
                border-radius: 8px;
                padding: 12px;
                text-align: center;
            }
        """

        for card in [self.card_km, self.card_dplus, self.card_qmax, self.card_pendenza]:
            card.setStyleSheet(card_style)
            card.setAlignment(Qt.AlignCenter)
            kpi_layout.addWidget(card)

        layout.addLayout(kpi_layout)

        # --- SEZIONE 1.5: CARD E PULSANTE PAESI ---
        paesi_layout = QVBoxLayout()
        
        self.card_paesi = QLabel("<b>PAESI ATTRAVERSATI</b><br><span style='font-size:16pt;'>Caricamento...</span>")
        self.card_paesi.setStyleSheet(card_style)
        self.card_paesi.setAlignment(Qt.AlignCenter)
        paesi_layout.addWidget(self.card_paesi)

        self.btn_apri_paesi = QPushButton("🔍 Visualizza Elenco Completo Paesi e Bandiere")
        self.btn_apri_paesi.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)
        self.btn_apri_paesi.clicked.connect(self.apri_finestra_elenco_paesi)
        paesi_layout.addWidget(self.btn_apri_paesi)

        layout.addLayout(paesi_layout)
             
        # --- SEZIONE 2: TABELLA METRICHE PER BLOCCO ---
        lbl_sub_blocchi = QLabel("🏔️ Dettaglio Altimetrico per Blocco / Area")
        lbl_sub_blocchi.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_sub_blocchi.setStyleSheet("margin-top: 15px; color: #dcdcdc;")
        layout.addWidget(lbl_sub_blocchi)

        self.tabella_stats_blocchi = QTableWidget()
        colonne_b = ["#", "Blocco / Area", "Tappe", "KM Totali", "D+ (m)", "D- (m)", "Quota Max", "Pendenza Med."]
        self.tabella_stats_blocchi.setColumnCount(len(colonne_b))
        self.tabella_stats_blocchi.setHorizontalHeaderLabels(colonne_b)
        self.tabella_stats_blocchi.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabella_stats_blocchi.setStyleSheet("""
            QTableWidget { background-color: #252526; gridline-color: #3e3e42; color: #ffffff; border: 1px solid #3e3e42; border-radius: 5px; }
            QHeaderView::section { background-color: #2d2d30; color: #0e639c; font-weight: bold; padding: 6px; }
        """)
        layout.addWidget(self.tabella_stats_blocchi)

        # --- SEZIONE 3: TABELLA FASCE COSTIERE ---
        lbl_sub_costa = QLabel("🏖️ Ripartizione Prossimità dal Mare (Fasce Costiere)")
        lbl_sub_costa.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_sub_costa.setStyleSheet("margin-top: 15px; color: #dcdcdc;")
        layout.addWidget(lbl_sub_costa)

        self.tabella_stats_costa = QTableWidget()
        colonne_c = ["Fascia Costiera", "Tappe Coinvolte", "KM Totali", "Percentuale Viaggio"]
        self.tabella_stats_costa.setColumnCount(len(colonne_c))
        self.tabella_stats_costa.setHorizontalHeaderLabels(colonne_c)
        self.tabella_stats_costa.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabella_stats_costa.setStyleSheet("""
            QTableWidget { background-color: #252526; gridline-color: #3e3e42; color: #ffffff; border: 1px solid #3e3e42; border-radius: 5px; }
            QHeaderView::section { background-color: #2d2d30; color: #0e639c; font-weight: bold; padding: 6px; }
        """)
        layout.addWidget(self.tabella_stats_costa)

        return widget

    def apri_pagina_statistiche(self):
        """Passa alla pagina statistiche e aggiorna i dati del progetto corrente."""
        self.cambia_pagina(7)  # Indice della pagina delle statistiche nello stacked_widget
        self.carica_statistiche_progetto()

    def apri_finestra_elenco_paesi(self):
        """Apre la finestra dei paesi con ricerca robusta tramite ISO2 e chiavi standard."""
        id_progetto = getattr(self, "current_progetto_id", None)
        if not id_progetto:
            return

        import json
        import os
        import service.stats_service
        lista_paesi, totale_paesi, _ = service.stats_service.get_paesi_attraversati_stats(id_progetto)

        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QPushButton
        from PySide6.QtGui import QPixmap, QIcon
        from PySide6.QtCore import Qt, QSize
                
        finestra = QDialog()
        finestra.setWindowTitle(f"Elenco Paesi Attraversati ({totale_paesi})")
        finestra.resize(480, 550)
        finestra.setStyleSheet("background-color: #1e1e1e; color: white;")

        layout_popup = QVBoxLayout(finestra)

        titolo_popup = QLabel(f"<b>Totale Paesi Attraversati: {totale_paesi}</b>")
        titolo_popup.setStyleSheet("font-size: 14pt; color: #4ec9b0; margin-bottom: 10px;")
        layout_popup.addWidget(titolo_popup)

        sprite_img_path = "resources/sprite.png"
        sprite_json_path = "resources/sprite.json"

        sprite_data = {}
        sprite_pixmap = None

        if os.path.exists(sprite_img_path) and os.path.exists(sprite_json_path):
            sprite_pixmap = QPixmap(sprite_img_path)
            try:
                with open(sprite_json_path, 'r', encoding='utf-8') as f:
                    sprite_data = json.load(f)
            except Exception as e:
                print(f"Errore caricamento sprite.json: {e}")

        tabella = QTableWidget()
        tabella.setColumnCount(2)
        tabella.setHorizontalHeaderLabels(["Bandiera", "Paese"])
        tabella.horizontalHeader().setStretchLastSection(True)
        tabella.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabella.setRowCount(len(lista_paesi))
        
        icon_size = 32
        tabella.verticalHeader().setDefaultSectionSize(icon_size + 14)
        tabella.setIconSize(QSize(icon_size, icon_size))

        # Mappatura universale ISO2 -> Nome chiave inglese nello sprite (per sicurezza assoluta)
        iso_to_sprite_key = {
            "TR": "Turkey",
            "TW": "Taiwan",
            "VN": "Vietnam",
            "TH": "Thailand",
            "TZ": "Tanzania",
            "TG": "Togo",
            "TM": "Turkmenistan"
        }

        for row_idx, item_tuple in enumerate(lista_paesi):
            if len(item_tuple) >= 3:
                iso2_code = str(item_tuple[0]).strip().upper()
                nome_fallback = str(item_tuple[1])
            else:
                iso2_code = ""
                nome_fallback = str(item_tuple[0])
            
            item_bandiera = QTableWidgetItem()
            trovato_coords = None
            nome_paese_it = nome_fallback

            # Tentativo 1: Ricerca tramite il campo iso_alpha2 dentro il JSON
            for paese_key, info in sprite_data.items():
                if isinstance(info, dict):
                    sprite_iso = str(info.get("iso_alpha2", "")).strip().upper()
                    if iso2_code and sprite_iso == iso2_code:
                        trovato_coords = info
                        nome_paese_it = info.get("name_it", nome_fallback)
                        break

            # Tentativo 2: Se fallisce, usa la chiave inglese standard associata all'ISO2 nello sprite
            if not trovato_coords and iso2_code in iso_to_sprite_key:
                target_key = iso_to_sprite_key[iso2_code]
                if target_key in sprite_data:
                    trovato_coords = sprite_data[target_key]
                    if isinstance(trovato_coords, dict):
                        nome_paese_it = trovato_coords.get("name_it", nome_fallback)

            # Tentativo 3: Fallback finale per nome testuale (case-insensitive)
            if not trovato_coords:
                clean_name = nome_fallback.strip().lower()
                for paese_key, info in sprite_data.items():
                    if isinstance(info, dict):
                        s_name_it = str(info.get("name_it", "")).strip().lower()
                        s_name_en = str(info.get("name_en", "")).strip().lower()
                        if paese_key.lower().replace("_", " ") == clean_name or s_name_it == clean_name or s_name_en == clean_name:
                            trovato_coords = info
                            nome_paese_it = info.get("name_it", nome_fallback)
                            break

            item_nome = QTableWidgetItem(nome_paese_it)

            if sprite_pixmap and trovato_coords:
                x = trovato_coords.get("x", 0)
                y = trovato_coords.get("y", 0)
                w = trovato_coords.get("width", 48)
                h = trovato_coords.get("height", 48)
                
                if w > 0 and h > 0:
                    flag_pixmap = sprite_pixmap.copy(x, y, w, h).scaled(
                        icon_size, icon_size, 
                        Qt.AspectRatioMode.KeepAspectRatio, 
                        Qt.TransformationMode.SmoothTransformation
                    )
                    item_bandiera.setIcon(QIcon(flag_pixmap))

            item_bandiera.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            tabella.setItem(row_idx, 0, item_bandiera)
            tabella.setItem(row_idx, 1, item_nome)

        layout_popup.addWidget(tabella)

        btn_chiudi = QPushButton("Chiudi")
        btn_chiudi.setStyleSheet("background-color: #333333; color: white; padding: 8px; border-radius: 4px;")
        btn_chiudi.clicked.connect(finestra.close)
        layout_popup.addWidget(btn_chiudi)

        finestra.exec()
                                        
    def carica_statistiche_progetto(self):
        """Metodo di caricamento sicuro e ottimizzato delle statistiche."""
        id_progetto = getattr(self, "current_progetto_id", None)

        # Controlliamo che un progetto valido sia stato selezionato
        if not id_progetto:
            self.card_km.setText("<b>KM TOTALI</b><br><span style='font-size:20pt;'>-</span>")
            self.card_dplus.setText("<b>DISLIVELLO +</b><br><span style='font-size:20pt;'>-</span>")
            self.card_qmax.setText("<b>QUOTA MAX</b><br><span style='font-size:20pt;'>-</span>")
            self.card_pendenza.setText("<b>PENDENZA MEDIA</b><br><span style='font-size:20pt;'>-</span>")
            if hasattr(self, "card_paesi"):
                self.card_paesi.setText("<b>PAESI ATTRAVERSATI (0)</b><br><span style='font-size:16pt;'>🏳️</span>")
            
            self.tabella_stats_blocchi.setRowCount(0)
            self.tabella_stats_costa.setRowCount(0)
            return

        # Se abbiamo già caricato questo progetto in questa sessione, evitiamo ricalcoli inutili
        if getattr(self, "_cached_stats_id", None) == id_progetto and self.tabella_stats_blocchi.rowCount() > 0:
            return

        import service.stats_service

        # 1. Recupero paesi e bandierine
        _, totale_paesi, stringa_bandierine = service.stats_service.get_paesi_attraversati_stats(id_progetto)

        # 2. Aggiorna KPI Top e la card dei paesi
        kpi = service.stats_service.ottieni_kpi_totali_progetto(id_progetto)
        self.card_km.setText(f"<b>KM TOTALI</b><br><span style='font-size:20pt; color:#4ec9b0;'>{kpi['km_totali']} km</span>")
        self.card_dplus.setText(f"<b>DISLIVELLO +</b><br><span style='font-size:20pt; color:#ce9178;'>{kpi['dislivello_pos']} m</span>")
        self.card_qmax.setText(f"<b>QUOTA MAX</b><br><span style='font-size:20pt; color:#569cd6;'>{kpi['quota_max']} m</span>")
        self.card_pendenza.setText(f"<b>PENDENZA MEDIA</b><br><span style='font-size:20pt; color:#dcdcaa;'>{kpi['pendenza_media']} %</span>")
        
        if hasattr(self, "card_paesi"):
            self.card_paesi.setText(f"<b>PAESI ATTRAVERSATI ({totale_paesi})</b><br><span style='font-size:18pt;'>{stringa_bandierine}</span>")

        # 3. Popola Tabella Dettaglio per Blocco
        self.tabella_stats_blocchi.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        blocchi_data = service.stats_service.ottieni_statistiche_per_blocco(id_progetto)
        self.tabella_stats_blocchi.setRowCount(0)
        if blocchi_data:
            for row_idx, riga in enumerate(blocchi_data):
                self.tabella_stats_blocchi.insertRow(row_idx)
                for col_idx, val in enumerate(riga):
                    item = QTableWidgetItem(str(val))
                    if col_idx in [0, 2, 3, 4, 5, 6, 7]:
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabella_stats_blocchi.setItem(row_idx, col_idx, item)

        # 4. Popola Tabella Fasce Costiere
        self.tabella_stats_costa.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        costa_data = service.stats_service.ottieni_ripartizione_fasce_mare(id_progetto)
        self.tabella_stats_costa.setRowCount(0)
        if costa_data:
            for row_idx, riga in enumerate(costa_data):
                self.tabella_stats_costa.insertRow(row_idx)
                for col_idx, val in enumerate(riga):
                    item = QTableWidgetItem(str(val))
                    if col_idx in [1, 2, 3]:
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabella_stats_costa.setItem(row_idx, col_idx, item)

        # Memorizziamo il progetto corrente
        self._cached_stats_id = id_progetto        
        
        # Controlliamo che un progetto valido sia stato selezionato
        if not id_progetto:
            self.card_km.setText("<b>KM TOTALI</b><br><span style='font-size:20pt;'>-</span>")
            self.card_dplus.setText("<b>DISLIVELLO +</b><br><span style='font-size:20pt;'>-</span>")
            self.card_qmax.setText("<b>QUOTA MAX</b><br><span style='font-size:20pt;'>-</span>")
            self.card_pendenza.setText("<b>PENDENZA MEDIA</b><br><span style='font-size:20pt;'>-</span>")
            
            self.tabella_stats_blocchi.setRowCount(0)
            self.tabella_stats_costa.setRowCount(0)
            return

        import service.stats_service

        # 1. Recupero paesi e bandierine dal JSON/DB e stampiamoli in console per verifica
        lista_paesi, totale_paesi, stringa_bandierine = service.stats_service.get_paesi_attraversati_stats(id_progetto)

        # 2. Aggiorna KPI Top
        kpi = service.stats_service.ottieni_kpi_totali_progetto(id_progetto)
        self.card_km.setText(f"<b>KM TOTALI</b><br><span style='font-size:20pt; color:#4ec9b0;'>{kpi['km_totali']} km</span>")
        self.card_dplus.setText(f"<b>DISLIVELLO +</b><br><span style='font-size:20pt; color:#ce9178;'>{kpi['dislivello_pos']} m</span>")
        self.card_qmax.setText(f"<b>QUOTA MAX</b><br><span style='font-size:20pt; color:#569cd6;'>{kpi['quota_max']} m</span>")
        self.card_pendenza.setText(f"<b>PENDENZA MEDIA</b><br><span style='font-size:14pt; color:#dcdcaa;'>{kpi['pendenza_media']} %</span>")

        # 3. Popola Tabella Dettaglio per Blocco
        blocchi_data = service.stats_service.ottieni_statistiche_per_blocco(id_progetto)
        self.tabella_stats_blocchi.setRowCount(0)
        if blocchi_data:
            for row_idx, riga in enumerate(blocchi_data):
                self.tabella_stats_blocchi.insertRow(row_idx)
                for col_idx, val in enumerate(riga):
                    item = QTableWidgetItem(str(val))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    if col_idx in [0, 2, 3, 4, 5, 6, 7]:
                        item.setTextAlignment(Qt.AlignCenter)
                    self.tabella_stats_blocchi.setItem(row_idx, col_idx, item)

        # 4. Popola Tabella Fasce Costiere
        costa_data = service.stats_service.ottieni_ripartizione_fasce_mare(id_progetto)
        self.tabella_stats_costa.setRowCount(0)
        if costa_data:
            for row_idx, riga in enumerate(costa_data):
                self.tabella_stats_costa.insertRow(row_idx)
                for col_idx, val in enumerate(riga):
                    item = QTableWidgetItem(str(val))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    if col_idx in [1, 2, 3]:
                        item.setTextAlignment(Qt.AlignCenter)
                    self.tabella_stats_costa.setItem(row_idx, col_idx, item)    
    
    def crea_pagina_placeholder(self, titolo, descrizione):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        lbl_titolo = QLabel(titolo)
        lbl_titolo.setFont(QFont("Arial", 20, QFont.Bold))
        lbl_titolo.setStyleSheet("color: #0e639c;")
        lbl_desc = QLabel(descrizione)
        lbl_desc.setFont(QFont("Arial", 12))
        lbl_desc.setStyleSheet("color: #aaaaaa; margin-top: 10px;")
        layout.addWidget(lbl_titolo)
        layout.addWidget(lbl_desc)
        layout.addStretch()
        return widget

    def verifica_progetto_attivo(self) -> bool:
        """Controlla se l'utente ha selezionato un percorso dalla Dashboard."""
        id_proj = getattr(self, "current_progetto_id", None)
        return id_proj is not None and id_proj > 0

    def mostra_avviso_nessun_progetto(self, titolo="⚠️ Nessun Percorso Selezionato") -> QWidget:
        """Crea la schermata di avviso quando non c'è un percorso aperto."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignCenter)

        lbl_icona = QLabel("🗺️")
        lbl_icona.setStyleSheet("font-size: 48px;")
        lbl_icona.setAlignment(Qt.AlignCenter)

        lbl_titolo = QLabel(f"<h3>{titolo}</h3>")
        lbl_titolo.setAlignment(Qt.AlignCenter)

        lbl_msg = QLabel(
            "Per visualizzare ed elaborare i dati di questo modulo, torna alla "
            "<b>Dashboard Spedizioni</b> e seleziona o crea un percorso di viaggio."
        )
        lbl_msg.setWordWrap(True)
        lbl_msg.setAlignment(Qt.AlignCenter)
        lbl_msg.setStyleSheet("color: #888888; font-size: 13px; max-width: 450px;")

        btn_vai_dash = QPushButton("🏠 Torna alla Dashboard Spedizioni")
        btn_vai_dash.setCursor(Qt.PointingHandCursor)
        btn_vai_dash.setStyleSheet("padding: 8px 16px; font-weight: bold; margin-top: 10px;")
        btn_vai_dash.clicked.connect(lambda: self.cambia_pagina(0))

        layout.addWidget(lbl_icona)
        layout.addWidget(lbl_titolo)
        layout.addWidget(lbl_msg)
        layout.addWidget(btn_vai_dash, alignment=Qt.AlignCenter)

        return container    
    
    def mostra_mappa_gap(self, end_lat, end_lon, start_lat, start_lon, t1_nome="", t2_nome="", allarme_id=None):
        """Apre un popup con la mappa del tratto mancante e poi apre la logistica con nomi leggibili."""
        if not (end_lat and end_lon and start_lat and start_lon):
            QMessageBox.warning(self, "Attenzione", "Coordinate non disponibili per questo allarme.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Mappa GAP: {t1_nome} ➔ {t2_nome}")
        dialog.resize(700, 500)
        layout = QVBoxLayout(dialog)

        # Calcolo punto medio per centrare la mappa
        mid_lat = (end_lat + start_lat) / 2.0
        mid_lon = (end_lon + start_lon) / 2.0

        # Mappa Folium di dettaglio
        m = folium.Map(location=[mid_lat, mid_lon], zoom_start=12)

        # Punto Fine Tappa Precedente
        folium.Marker(
            location=[end_lat, end_lon],
            popup=f"Fine: {t1_nome}",
            icon=folium.Icon(color="red", icon="flag")
        ).add_to(m)
       
        # Punto Inizio Tappa Successiva
        folium.Marker(
            location=[start_lat, start_lon],
            popup=f"Inizio: {t2_nome}",
            icon=folium.Icon(color="green", icon="play")
        ).add_to(m)
        
        # Linea tratteggiata rossa del GAP
        folium.PolyLine(
            locations=[[end_lat, end_lon], [start_lat, start_lon]],
            color="red",
            weight=4,
            opacity=0.8,
            dash_array="10",
            popup="Tratto Mancante / GAP"
        ).add_to(m)

        # Rendering nel QWebEngineView
        web_view = QWebEngineView()
        html_data = io.BytesIO()
        m.save(html_data, close_file=False)
        web_view.setHtml(html_data.getvalue().decode('utf-8'))
        
        layout.addWidget(web_view)
        dialog.exec()

        # Traduzione delle coordinate in nomi leggibili (forzando caratteri latini/inglesi)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        da_luogo = self._coordinate_in_nome_luogo_leggibile(end_lat, end_lon) if end_lat and end_lon else ""
        a_luogo = self._coordinate_in_nome_luogo_leggibile(start_lat, start_lon) if start_lat and start_lon else ""
        QApplication.restoreOverrideCursor()

        # Apertura della finestra di logistica con i dati pronti
        if hasattr(self, 'apri_dialog_trasferimento'):
            self.apri_dialog_trasferimento(
                da_prefill=da_luogo, 
                a_prefill=a_luogo, 
                allarme_id=allarme_id, 
                lat1=end_lat, 
                lon1=end_lon, 
                lat2=start_lat, 
                lon2=start_lon
            )
        elif hasattr(self, 'apri_dialog_trasporto'):
            self.apri_dialog_trasporto(
                da_prefill=da_luogo, 
                a_prefill=a_luogo, 
                allarme_id=allarme_id, 
                lat1=end_lat, 
                lon1=end_lon, 
                lat2=start_lat, 
                lon2=start_lon
            )
        elif hasattr(self, 'apri_dialogo_trasferimento'):
            self.apri_dialogo_trasferimento(
                da_prefill=da_luogo, 
                a_prefill=a_luogo, 
                allarme_id=allarme_id, 
                lat1=end_lat, 
                lon1=end_lon, 
                lat2=start_lat, 
                lon2=start_lon
            )
        else:
            self.apri_dialog_trasferimento(
                da_prefill=da_luogo, 
                a_prefill=a_luogo, 
                allarme_id=allarme_id, 
                lat1=end_lat, 
                lon1=end_lon, 
                lat2=start_lat, 
                lon2=start_lon
            )    
    
    def _coordinate_in_nome_luogo_leggibile(self, lat, lon):
        """Converte le coordinate in un nome leggibile o usa le coordinate pulite se la lingua non è occidentale."""
        try:
            import urllib.request
            import json
            
            url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}&accept-language=en"
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'BikepackingStudioApp/1.0'}
            )
            
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode('utf-8'))
                address = data.get('address', {})
                
                luogo = (
                    address.get('city') or 
                    address.get('town') or 
                    address.get('village') or 
                    address.get('county') or 
                    address.get('state') or 
                    address.get('country')
                )
                
                if luogo:
                    # Controllo di sicurezza: se il nome contiene caratteri non latini (es. arabo/cinese), usiamo le coordinate
                    try:
                        luogo.encode('ascii')
                        return luogo
                    except UnicodeEncodeError:
                        return f"Località ({lat:.3f}, {lon:.3f})"
                else:
                    return f"Località ({lat:.3f}, {lon:.3f})"
        except Exception:
            return f"Località ({lat:.3f}, {lon:.3f})"    
    
    def cambia_pagina(self, index):
        self.stacked_widget.setCurrentIndex(index)

        # 1. Se siamo sulla Dashboard (Indice 0), ricarichiamo la lista
        if index == 0:
            # Chiamiamo il metodo del nuovo oggetto dashboard
            self.page_dashboard.carica_lista_percorsi() 
            return
        # ... (resto del codice)
        # 2. Per tutte le altre pagine, verifichiamo che ci sia un percorso aperto
        if not self.verifica_progetto_attivo():
            return

        # 3. Se il percorso c'è, eseguiamo i caricamenti specifici di ciascuna pagina
        if index == 1:
            self.page_blocchi.carica_blocchi()
        elif index == 2:
            #self.rigenera_mappa(force=False)
            pass
        elif index == 3:
            self.aggiorna_tabella_allarmi()
        elif index == 4:
            self.aggiorna_tabella_trasferimenti()
        elif index == 5:
            self.carica_o_analizza_dogane_automatico()
        elif index == 6:
            self.esegui_analisi_clima()
        elif index == 7:
            self.carica_statistiche_progetto()
    
    def aggiorna_tabella_trasferimenti(self):
        if not self.verifica_progetto_attivo():
            if hasattr(self, 'table_trasporti'):
                self.table_trasporti.setRowCount(0)
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, tipo_mezzo, vettore, da_luogo, a_luogo, durata, costo_eur 
            FROM trasferimenti 
            WHERE id_progetto = ?
        """, (self.current_progetto_id,))
        rows = cursor.fetchall()
        conn.close()

        self.table_trasporti.setRowCount(len(rows))
        for row_idx, data in enumerate(rows):
            trasf_id = data[0]
            # Inserisce i dati nelle colonne della tabella
            for col_idx, value in enumerate(data):
                item = QTableWidgetItem(str(value) if value is not None else "-")
                item.setTextAlignment(Qt.AlignCenter)
                self.table_trasporti.setItem(row_idx, col_idx, item)

            # Pulsante Elimina per ogni riga
            btn_elimina = QPushButton("❌ Elimina")
            btn_elimina.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; padding: 4px;")
            btn_elimina.clicked.connect(lambda _, tid=trasf_id: self.elimina_trasferimento(tid))
            
            # Assicurati che l'indice di colonna (es. 7) corrisponda alla colonna delle azioni
            colonne_totali = self.table_trasporti.columnCount()
            col_azione = colonne_totali - 1 if colonne_totali > 0 else 7
            self.table_trasporti.setCellWidget(row_idx, col_azione, btn_elimina)

    def elimina_trasferimento(self, trasf_id):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM trasferimenti WHERE id = ?", (trasf_id,))
        conn.commit()
        conn.close()

        if hasattr(self, 'esegui_audit_automatico'):
            self.esegui_audit_automatico()
        self.mappa_necessita_aggiornamento = True
        self.aggiorna_tabella_trasferimenti()
        if hasattr(self, 'aggiorna_tabella_allarmi'):
            self.aggiorna_tabella_allarmi()

    def apri_dialog_trasporto(self, *args, **kwargs):
        """Ponte di sicurezza per la mappa."""
        if hasattr(self, 'apri_dialog_trasferimento'):
            return self.apri_dialog_trasferimento(*args, **kwargs)

    def apri_dialogo_trasferimento(self, *args, **kwargs):
        """Ponte di sicurezza alternativo per la mappa."""
        if hasattr(self, 'apri_dialog_trasferimento'):
            return self.apri_dialog_trasferimento(*args, **kwargs)
    
    def avvia_dialog_logistica_con_geocoding(self, end_lat, end_lon, start_lat, start_lon, allarme_id=None):
        """Metodo blindato: impedisce doppi avvii e garantisce nomi leggibili."""
        # Evitiamo che si apra due volte per errore di doppio click sul pulsante
        if getattr(self, '_gia_in_apertura', False):
            return
        self._gia_in_apertura = True

        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            # Traduzione forzata e pulita per entrambi i punti
            da_luogo = self._coordinate_in_nome_luogo_leggibile(end_lat, end_lon) if end_lat and end_lon else ""
            a_luogo = self._coordinate_in_nome_luogo_leggibile(start_lat, start_lon) if start_lat and start_lon else ""
            
            QApplication.restoreOverrideCursor()
            
            # Apriamo la finestra una sola volta (e basta!)
            self.apri_dialog_trasferimento(
                da_prefill=da_luogo, 
                a_prefill=a_luogo, 
                allarme_id=allarme_id, 
                lat1=end_lat, 
                lon1=end_lon, 
                lat2=start_lat, 
                lon2=start_lon
            )
        finally:
            # Sblocchiamo la protezione dopo l'apertura
            self._gia_in_apertura = False
    
    def apri_dialog_trasferimento(self, da_prefill="", a_prefill="", allarme_id=None, lat1=None, lon1=None, lat2=None, lon2=None):
        if not self.current_progetto_id:
            QMessageBox.warning(self, "Attenzione", "Seleziona prima un percorso attivo!")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Registra & Cerca Soluzioni Trasferimento")
        dialog.setFixedWidth(520)
        dialog.setStyleSheet("background-color: #2d2d30; color: white;")
        layout = QFormLayout(dialog)
        
        combo_mezzo = QComboBox()
        combo_mezzo.addItems(["Traghetto / Nave", "Aereo", "Treno", "Bus / Pick-up", "Altro / Personale"])
        combo_mezzo.setStyleSheet("background-color: #3e3e42; padding: 5px;")
        
        txt_vettore = QLineEdit()
        txt_vettore.setPlaceholderText("Es. Grimaldi Lines, Trenitalia, Pegasus")
        txt_vettore.setStyleSheet("background-color: #3e3e42; padding: 5px; color: white;")
        
        txt_da = QLineEdit(da_prefill)
        txt_da.setStyleSheet("background-color: #3e3e42; padding: 5px; color: white;")
        
        txt_a = QLineEdit(a_prefill)
        txt_a.setStyleSheet("background-color: #3e3e42; padding: 5px; color: white;")
        
        txt_durata = QLineEdit()
        txt_durata.setPlaceholderText("Es. 4h 30m / 12h")
        txt_durata.setStyleSheet("background-color: #3e3e42; padding: 5px; color: white;")

        txt_costo = QLineEdit()
        txt_costo.setStyleSheet("background-color: #3e3e42; padding: 5px; color: white;")

        txt_note = QTextEdit()
        txt_note.setFixedHeight(50)
        txt_note.setPlaceholderText("Note, prenotazione o dettagli trasporto bici...")
        txt_note.setStyleSheet("background-color: #3e3e42; color: white;")

        btn_cerca_soluzione = QPushButton("🔍 Cerca Soluzioni di Trasporto Online")
        btn_cerca_soluzione.setStyleSheet("background-color: #8e44ad; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        btn_cerca_soluzione.clicked.connect(lambda: webbrowser.open(f"https://www.rome2rio.com/s/{txt_da.text()}/{txt_a.text()}"))

        layout.addRow("Mezzo di Trasporto:", combo_mezzo)
        layout.addRow("Compagnia / Vettore:", txt_vettore)
        layout.addRow("Partenza Da:", txt_da)
        layout.addRow("Arrivo A:", txt_a)
        layout.addRow("Durata Stimata:", txt_durata)
        layout.addRow("Costo (€):", txt_costo)
        layout.addRow("Note / Bici a Bordo:", txt_note)
        layout.addRow(btn_cerca_soluzione)

        btn_salva = QPushButton("💾 Salva Logistica e Risolvi GAP")
        btn_salva.setStyleSheet("background-color: #0e639c; color: white; padding: 10px; font-weight: bold; margin-top: 10px;")
        btn_salva.clicked.connect(lambda: self.salva_trasferimento(
            dialog, combo_mezzo.currentText(), txt_vettore.text(), 
            txt_da.text(), txt_a.text(), txt_durata.text(), txt_costo.text(), txt_note.toPlainText(),
            allarme_id, lat1, lon1, lat2, lon2
        ))
        layout.addRow(btn_salva)
        dialog.exec()

    def salva_trasferimento(self, dialog, mezzo, vettore, da_luogo, a_luogo, durata, costo, note, allarme_id=None, lat1=None, lon1=None, lat2=None, lon2=None):
        try:
            valore_costo = float(costo) if costo else 0.0
        except ValueError:
            valore_costo = 0.0

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Salvataggio del trasferimento
        cursor.execute('''
            INSERT INTO trasferimenti (id_progetto, tipo_mezzo, vettore, da_luogo, a_luogo, durata, costo_eur, note, start_lat, start_lon, end_lat, end_lon)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (self.current_progetto_id, mezzo, vettore, da_luogo, a_luogo, durata, valore_costo, note, lat1, lon1, lat2, lon2))

        # Risoluzione dell'allarme associato se presente
        if allarme_id:
            cursor.execute("UPDATE allarmi_percorso SET risolto = 1 WHERE id = ?", (allarme_id,))

        conn.commit()
        conn.close()

        dialog.accept()
        self.mappa_necessita_aggiornamento = True
        self.aggiorna_tabella_trasferimenti()
        
        if hasattr(self, 'aggiorna_tabella_allarmi'):
            self.aggiorna_tabella_allarmi()
        if hasattr(self, 'carica_allarmi_percorso'):
            self.carica_allarmi_percorso()

        QMessageBox.information(self, "Logistica Salvata", "Trasferimento salvato correttamente e allarme risolto.")

    def on_progetto_selezionato(self, id_progetto, nome_progetto):
        """Gestisce la selezione o la creazione di un progetto, impostandolo come attivo."""
        self.current_progetto_id = id_progetto
        print(f"Progetto attivo impostato: {nome_progetto} (ID: {id_progetto})")
        
        # Sposta la visuale alla pagina successiva (es. Gestione Blocchi/Tracce, Indice 1)
        self.stacked_widget.setCurrentIndex(1)
        
        # Se la pagina successiva ha un metodo per ricaricare i dati del progetto, lo richiamiamo
        if hasattr(self, "page_blocchi") and hasattr(self.page_blocchi, "carica_blocchi"):
            self.page_blocchi.carica_blocchi()

if __name__ == "__main__":
    # Forza l'accelerazione hardware e le performance massime per QWebEngine
    import os
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--enable-gpu --ignore-gpu-blocklist --enable-accelerated-2d-canvas"
    
    # Inizializziamo QApplication una sola volta, prima di tutto
    app = QApplication(sys.argv)
    
    # Inizializza il database
    inizializza_database()
    
    # Forza il font di Windows per visualizzare correttamente le emoji a colori
    font_emoji = QFont("Segoe UI Emoji", 10)
    app.setFont(font_emoji)
    
    window = BikepackingStudioApp()
    window.show()
    sys.exit(app.exec())