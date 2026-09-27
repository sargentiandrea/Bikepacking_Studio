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
        # Pagina 1: Dashboard (Caricata dal nuovo modulo esterno)
        self.page_dashboard = DashboardPage(self)

        # Colleghi il segnale della dashboard a una funzione di coordinamento pulita
        self.page_dashboard.progetto_selezionato_signal.connect(self.gestisci_cambio_progetto)        
        
        self.stacked_widget.addWidget(self.page_dashboard) # Indice 0
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
                
                print(f"✨ Creato percorso '{nome}' | Bici: {combo_bici.currentText()} | Strade: {combo_strada.currentText()}")
                
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
            current_widget = self.stack.currentWidget()
            
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

        nome_raccordo, dist_raccordo, is_linea_retta = service.audit_service.genera_raccordo_gpx(
            self.current_progetto_id, t1_id, t2_id, t1_nome, t2_nome
        )

        if not nome_raccordo:
            return

        self.esegui_audit_automatico()
        self.mappa_necessita_aggiornamento = True
        self.aggiorna_tabella_tappe()
        self.aggiorna_tabella_trasferimenti()
        if hasattr(self, 'aggiorna_tabella_allarmi'):
            self.aggiorna_tabella_allarmi()

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
            btn_trasferimento.clicked.connect(lambda _, e_lat=end_lat, e_lon=end_lon, s_lat=start_lat, s_lon=start_lon, aid=allarme_id: self.avvia