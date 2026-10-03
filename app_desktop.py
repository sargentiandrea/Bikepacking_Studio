import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sqlite3
from contextlib import closing
import service.audit_service
import service.catena_stagionale_service
import service.clima_service
import service.migrazione_clima
import service.migrazione_catena_stagionale
from service.gpx_paths import trova_percorso_gpx
from service.geo_utils import calcola_distanza_haversine
import math
import json

from service.map_server import start_local_map_server
# Avvia il server delle mappe locale su porta 8080
start_local_map_server(port=8080)
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import (
    Signal,
    QObject,
    QThread,
    Qt,
    QDate,
    QSize,
)
from datetime import datetime
# -- Nuovi Moduli GUI --
from gui.dashboard import DashboardPage
from gui.mappa import MappaWidget
from gui.widget_blocchi import GestoreBlocchiWidget
from gui.widget_timeline_catena import TimelineCatenaWidget
from gui.worker_clima import GestoreEstrazioneClima
from gui.dialog_clima_soglie import ClimaSoglieDialog
from gui import dialog_elenco_paesi
from gui import dialog_nuovo_progetto
from gui import dialog_wizard_trasferimento
from service import trasferimenti_service


# Import dei moduli interni del progetto
import database.database_setup as database
database.inizializza_database()
from service.dogane_service import analizza_dogane_progetto, recupera_dogane_salvate

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QLabel, QStackedWidget, 
                             QFrame, QFileDialog, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QDialog, QFormLayout, 
                             QLineEdit, QComboBox, QTextEdit,
                             QDateEdit, QSpinBox, QTabWidget, QScrollArea,
                             QDoubleSpinBox, QDialogButtonBox)
from PySide6.QtGui import (
    QColor,
    QFont,
    QIcon,
    QPixmap,
)
# --- FORZATURA ACCELERAZIONE HARDWARE (ANTI-SCHERMO BIANCO) ---
os.environ["QT_WEBENGINE_DISABLE_GPU"] = "0"
QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
# --------------------------------------------------------------


from service.config import DB_NAME


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
        self._clima_progetto_id = None
        self._clima_ordine_base = []
        self._clima_ordine_scenario = None
        self._clima_scenario_id = None
        self._clima_ultima_applicazione_id = None
        self._clima_risultati_correnti = []
        # Il gestore incapsula thread e worker dell'estrazione clima.
        self._clima_estrazione = GestoreEstrazioneClima(
            self,
            DB_NAME,
            self._al_progresso_clima,
            self._estrazione_clima_completata,
            self._estrazione_clima_fallita,
            self._estrazione_clima_terminata,
        )

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setFixedWidth(85)
        sidebar.setStyleSheet(
            "background-color: #252526; border-right: 1px solid #3e3e42;"
            "QPushButton { font-size: 20px; padding: 10px; }"
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
        self.page_dashboard = DashboardPage(self)
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

    def cambia_pagina(self, indice):
        self.stacked_widget.setCurrentIndex(indice)
        if indice == 1:
            self.page_blocchi.carica_blocchi()
        elif indice == 3:
            self.aggiorna_tabella_allarmi()
        elif indice == 4:
            self.aggiorna_pagina_trasporti()
        elif indice == 5:
            self.aggiorna_pagina_dogane()
        elif indice == 6:
            self.aggiorna_pagina_clima()
        elif indice == 7:
            self.aggiorna_pagina_statistiche()

    def gestisci_cambio_progetto(self, id_progetto, nome_percorso):
        """Aggiorna lo stato globale della finestra principale quando la dashboard cambia progetto."""
        self.current_progetto_id = id_progetto
        self.current_progetto_nome = nome_percorso
        self.mappa_necessita_aggiornamento = True
            
    def crea_bottone_navigazione(self, testo):
        btn = QPushButton(testo)
        btn.setFont(QFont("Segoe UI Emoji", 20))
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

    def _stile_pagina_servizio(self, widget):
        widget.setStyleSheet("""
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
        """)
        for table in widget.findChildren(QTableWidget):
            table.verticalHeader().setDefaultSectionSize(55)

    def crea_pagina_trasporti(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 25, 25, 25)
        lbl = QLabel("🚢 Logistica e Trasferimenti Intermodali")
        lbl.setFont(QFont("Arial", 16, QFont.Bold))
        lbl.setStyleSheet("color: #0e639c;")
        layout.addWidget(lbl)

        self.lbl_stato_trasporti = QLabel("Seleziona un percorso per visualizzare trasferimenti e interruzioni.")
        layout.addWidget(self.lbl_stato_trasporti)

        tabs = QTabWidget()
        self.table_trasferimenti = QTableWidget()
        self.table_trasferimenti.setColumnCount(7)
        self.table_trasferimenti.setHorizontalHeaderLabels([
            "Mezzo", "Vettore", "Da", "A", "Durata", "Costo EUR", "Note"
        ])
        self.table_trasferimenti.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabs.addTab(self.table_trasferimenti, "Trasferimenti salvati")

        gap_page = QWidget()
        gap_layout = QVBoxLayout(gap_page)
        self.table_gap_trasporti = QTableWidget()
        self.table_gap_trasporti.setColumnCount(3)
        self.table_gap_trasporti.setHorizontalHeaderLabels(["Tipo", "Tappa di partenza", "Dettaglio"])
        self.table_gap_trasporti.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        gap_layout.addWidget(self.table_gap_trasporti)
        btn_raccorda_gap = QPushButton("🔗 Genera raccordo GPX per il gap selezionato")
        btn_raccorda_gap.clicked.connect(self.raccorda_gap_selezionato)
        gap_layout.addWidget(btn_raccorda_gap)
        tabs.addTab(gap_page, "Interruzioni rilevate")
        layout.addWidget(tabs)

        btn_aggiorna = QPushButton("🔄 Aggiorna dati logistici")
        btn_aggiorna.clicked.connect(self.aggiorna_pagina_trasporti)
        layout.addWidget(btn_aggiorna)
        self._stile_pagina_servizio(widget)
        return widget

    def crea_pagina_dogane(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 25, 25, 25)
        lbl = QLabel("🛂 Dogane & Requisiti di Ingresso")
        lbl.setFont(QFont("Arial", 16, QFont.Bold))
        lbl.setStyleSheet("color: #0e639c;")
        layout.addWidget(lbl)

        self.lbl_stato_dogane = QLabel("Seleziona un percorso per visualizzare i dati doganali salvati.")
        layout.addWidget(self.lbl_stato_dogane)
        self.table_dogane = QTableWidget()
        self.table_dogane.setColumnCount(9)
        self.table_dogane.setHorizontalHeaderLabels([
            "Ordine", "ISO", "Paese", "Area", "Passaporto", "Visto",
            "Valuta", "Roaming", "Drone"
        ])
        self.table_dogane.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_dogane.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table_dogane)

        btn_aggiorna = QPushButton("🔄 Ricarica dati doganali")
        btn_aggiorna.clicked.connect(self.aggiorna_pagina_dogane)
        layout.addWidget(btn_aggiorna)
        self._stile_pagina_servizio(widget)
        return widget

    def crea_pagina_clima(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 25, 25, 25)
        lbl = QLabel("🗓️ Catena Stagionale & Clima")
        lbl.setFont(QFont("Arial", 16, QFont.Bold))
        lbl.setStyleSheet("color: #0e639c;")
        layout.addWidget(lbl)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Data di partenza"))
        self.input_data_partenza = QDateEdit()
        self.input_data_partenza.setCalendarPopup(True)
        self.input_data_partenza.setDisplayFormat("dd/MM/yyyy")
        self.input_data_partenza.setDate(QDate.currentDate())
        controls.addWidget(self.input_data_partenza)
        controls.addWidget(QLabel("Modificatore giorni di riposo"))
        self.input_riposo = QSpinBox()
        self.input_riposo.setRange(-10, 10)
        controls.addWidget(self.input_riposo)
        btn_calcola = QPushButton("Calcola")
        btn_calcola.clicked.connect(self.calcola_pagina_clima)
        controls.addWidget(btn_calcola)
        btn_salva = QPushButton("Salva impostazioni")
        btn_salva.clicked.connect(self.salva_impostazioni_clima)
        controls.addWidget(btn_salva)
        layout.addLayout(controls)

        controlli_clima = QHBoxLayout()
        self.btn_estrai_clima = QPushButton(
            "Estrai/aggiorna dati CHELSA per paese"
        )
        self.btn_estrai_clima.clicked.connect(self.avvia_estrazione_clima)
        controlli_clima.addWidget(self.btn_estrai_clima)
        self.btn_soglie_clima = QPushButton("Impostazioni semaforo")
        self.btn_soglie_clima.clicked.connect(self.apri_soglie_clima)
        controlli_clima.addWidget(self.btn_soglie_clima)
        controlli_clima.addWidget(
            QLabel(
                "Internet serve per l’estrazione; i riepiloghi restano poi offline."
            )
        )
        controlli_clima.addStretch(1)
        layout.addLayout(controlli_clima)

        controlli_scenario = QHBoxLayout()
        controlli_scenario.addWidget(QLabel("Sposta nello scenario"))
        self.combo_blocco_scenario = QComboBox()
        self.combo_blocco_scenario.setMinimumWidth(180)
        controlli_scenario.addWidget(self.combo_blocco_scenario)
        controlli_scenario.addWidget(QLabel("nuova posizione"))
        self.combo_posizione_scenario = QComboBox()
        controlli_scenario.addWidget(self.combo_posizione_scenario)
        self.btn_applica_scenario = QPushButton("Prova spostamento")
        self.btn_applica_scenario.clicked.connect(self.sposta_blocco_scenario)
        controlli_scenario.addWidget(self.btn_applica_scenario)
        self.btn_ripristina_scenario = QPushButton("Ripristina ordine")
        self.btn_ripristina_scenario.clicked.connect(self.ripristina_ordine_scenario)
        controlli_scenario.addWidget(self.btn_ripristina_scenario)
        self.btn_conferma_scenario = QPushButton("Conferma scenario")
        self.btn_conferma_scenario.clicked.connect(
            self.conferma_scenario_clima
        )
        controlli_scenario.addWidget(self.btn_conferma_scenario)
        self.btn_annulla_scenario = QPushButton(
            "Annulla ultima applicazione"
        )
        self.btn_annulla_scenario.clicked.connect(
            self.annulla_ultima_applicazione_scenario
        )
        controlli_scenario.addWidget(self.btn_annulla_scenario)
        layout.addLayout(controlli_scenario)

        self.lbl_stato_clima = QLabel(
            "Stima con margini: la proiezione non è una probabilità matematica."
        )
        layout.addWidget(self.lbl_stato_clima)
        self.lbl_regole_clima = QLabel(
            "1 tappa = 1 giorno; 1 riposo ogni 5 tappe; buffer: 5 giorni per "
            "mese di calendario attraversato e 7 giorni ogni 4 mesi. "
            "I buffer non ne generano altri."
        )
        self.lbl_regole_clima.setWordWrap(True)
        layout.addWidget(self.lbl_regole_clima)

        lbl_timeline = QLabel("Timeline del viaggio")
        lbl_timeline.setStyleSheet("font-weight: bold; color: #cccccc;")
        layout.addWidget(lbl_timeline)
        self.timeline_clima = TimelineCatenaWidget()
        self.area_timeline_clima = QScrollArea()
        self.area_timeline_clima.setWidgetResizable(True)
        self.area_timeline_clima.setMaximumHeight(190)
        self.area_timeline_clima.setWidget(self.timeline_clima)
        layout.addWidget(self.area_timeline_clima)

        lbl_tabella = QLabel("Dettaglio per blocco e paese")
        lbl_tabella.setStyleSheet("font-weight: bold; color: #cccccc;")
        layout.addWidget(lbl_tabella)
        self.table_clima = QTableWidget()
        self.table_clima.setColumnCount(12)
        self.table_clima.setHorizontalHeaderLabels([
            "Blocco / paese", "Tappe", "Km", "Pedalata", "Riposo", "Buffer",
            "Totale giorni", "Ingresso", "Uscita", "Semaforo",
            "Motivazione climatica", "Nota"
        ])
        self.table_clima.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_clima.horizontalHeader().setStretchLastSection(True)
        self.table_clima.setMaximumHeight(450)
        layout.addWidget(self.table_clima)
        self._aggiorna_controlli_scenario([])
        self._stile_pagina_servizio(widget)
        return widget

    def crea_pagina_statistiche(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 20, 25, 20)
        lbl = QLabel("📊 Totali & Statistiche Avanzate")
        lbl.setFont(QFont("Arial", 16, QFont.Bold))
        lbl.setStyleSheet("color: #0e639c;")
        layout.addWidget(lbl)

        self.lbl_stato_statistiche = QLabel("Seleziona un percorso per calcolare le statistiche.")
        layout.addWidget(self.lbl_stato_statistiche)

        kpi_layout = QHBoxLayout()
        card_style = """
            QLabel {
                background-color: #252526;
                color: #ffffff;
                border: 1px solid #3e3e42;
                border-radius: 6px;
                padding: 10px;
            }
        """
        self.card_stats_km = QLabel("<b>KM TOTALI</b><br><span style='font-size:18pt;'>-</span>")
        self.card_stats_dplus = QLabel("<b>DISLIVELLO +</b><br><span style='font-size:18pt;'>-</span>")
        self.card_stats_dminus = QLabel("<b>DISLIVELLO -</b><br><span style='font-size:18pt;'>-</span>")
        self.card_stats_quota = QLabel("<b>QUOTA MAX</b><br><span style='font-size:18pt;'>-</span>")
        self.card_stats_pendenza = QLabel("<b>PENDENZA MEDIA</b><br><span style='font-size:18pt;'>-</span>")
        for card in (
            self.card_stats_km,
            self.card_stats_dplus,
            self.card_stats_dminus,
            self.card_stats_quota,
            self.card_stats_pendenza,
        ):
            card.setStyleSheet(card_style)
            card.setAlignment(Qt.AlignCenter)
            kpi_layout.addWidget(card)
        layout.addLayout(kpi_layout)

        paesi_layout = QVBoxLayout()
        self.card_stats_paesi = QLabel("<b>PAESI ATTRAVERSATI</b><br><span style='font-size:14pt;'>-</span>")
        self.card_stats_paesi.setStyleSheet(card_style)
        self.card_stats_paesi.setAlignment(Qt.AlignCenter)
        self.card_stats_paesi.setMaximumWidth(440)
        self.card_stats_paesi.setMinimumHeight(62)
        paesi_layout.addWidget(self.card_stats_paesi, alignment=Qt.AlignCenter)
        self.btn_apri_paesi = QPushButton("🌐 Visualizza paesi e bandiere")
        self.btn_apri_paesi.setStyleSheet("background-color: #0e639c; color: white; font-weight: bold; padding: 8px 16px; border-radius: 4px;")
        self.btn_apri_paesi.clicked.connect(self.apri_finestra_elenco_paesi)
        paesi_layout.addWidget(self.btn_apri_paesi, alignment=Qt.AlignCenter)
        layout.addLayout(paesi_layout)

        tabs = QTabWidget()
        self.table_statistiche_blocchi = QTableWidget()
        self.table_statistiche_blocchi.setColumnCount(8)
        self.table_statistiche_blocchi.setHorizontalHeaderLabels([
            "Ordine", "Blocco", "Tappe", "Distanza", "Dislivello +",
            "Dislivello -", "Quota max", "Pendenza media"
        ])
        self.table_statistiche_blocchi.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabs.addTab(self.table_statistiche_blocchi, "Per blocco")

        self.table_statistiche_costa = QTableWidget()
        self.table_statistiche_costa.setColumnCount(4)
        self.table_statistiche_costa.setHorizontalHeaderLabels([
            "Fascia costiera", "Tappe coinvolte", "Km totali", "Percentuale viaggio"
        ])
        self.table_statistiche_costa.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabs.addTab(self.table_statistiche_costa, "Distanza dalla costa")
        layout.addWidget(tabs)

        btn_aggiorna = QPushButton("🔄 Ricalcola statistiche")
        btn_aggiorna.clicked.connect(self.aggiorna_pagina_statistiche)
        layout.addWidget(btn_aggiorna)
        self._stile_pagina_servizio(widget)
        for table in (self.table_statistiche_blocchi, self.table_statistiche_costa):
            table.setStyleSheet("""
                QTableWidget { background-color: #252526; alternate-background-color: #2a2a2d; gridline-color: #3e3e42; color: #ffffff; border: 1px solid #3e3e42; border-radius: 5px; }
                QTableWidget::item { padding: 4px 6px; }
                QHeaderView::section { background-color: #2d2d30; color: #0e639c; font-weight: bold; padding: 7px; border: 1px solid #3e3e42; }
            """)
            table.setAlternatingRowColors(True)
            table.verticalHeader().setDefaultSectionSize(40)
        return widget

    def apri_finestra_elenco_paesi(self):
        """Mostra il dialogo con l'elenco dei paesi attraversati dal percorso."""
        if not self.current_progetto_id:
            QMessageBox.information(self, "Percorso richiesto", "Apri un percorso per visualizzare i paesi attraversati.")
            return

        from service import stats_service
        lista_paesi, totale_paesi, _ = stats_service.get_paesi_attraversati_stats(self.current_progetto_id)
        dialog_elenco_paesi.crea_elenco_paesi(self, lista_paesi, totale_paesi)

    def _imposta_righe_tabella(self, tabella, righe):
        tabella.setRowCount(len(righe))
        for row_index, riga in enumerate(righe):
            for col_index, valore in enumerate(riga):
                testo = "" if valore is None else str(valore)
                tabella.setItem(row_index, col_index, QTableWidgetItem(testo))

    def aggiorna_pagina_trasporti(self):
        if not self.current_progetto_id:
            self.lbl_stato_trasporti.setText("Apri un percorso per visualizzare i dati logistici.")
            self._imposta_righe_tabella(self.table_trasferimenti, [])
            self._imposta_righe_tabella(self.table_gap_trasporti, [])
            return

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tipo_mezzo, vettore, da_luogo, a_luogo, durata, costo_eur, note
                FROM trasferimenti WHERE id_progetto = ? ORDER BY id
            """, (self.current_progetto_id,))
            trasferimenti = cursor.fetchall()
            conn.close()

            gaps = service.audit_service.rileva_gap_progetto(self.current_progetto_id)
            strade_vietate = service.audit_service.rileva_strade_vietate_progetto(self.current_progetto_id)
            allarmi = gaps + strade_vietate
            self._imposta_righe_tabella(self.table_trasferimenti, trasferimenti)
            self.table_gap_trasporti.setRowCount(len(allarmi))
            for row_index, gap in enumerate(allarmi):
                item_tipo = QTableWidgetItem(gap["tipo"])
                item_tipo.setData(Qt.UserRole, (gap["id_tappa_origine"], gap["id_tappa_destinazione"]))
                self.table_gap_trasporti.setItem(row_index, 0, item_tipo)
                self.table_gap_trasporti.setItem(row_index, 1, QTableWidgetItem(str(gap["id_tappa_origine"])))
                self.table_gap_trasporti.setItem(row_index, 2, QTableWidgetItem(gap["messaggio"]))

            self.lbl_stato_trasporti.setText(
                f"{len(trasferimenti)} trasferimenti salvati; {len(gaps)} interruzioni e "
                f"{len(strade_vietate)} tratti vietati alle bici da valutare."
            )
        except Exception as errore:
            self.lbl_stato_trasporti.setText(f"Errore durante il caricamento logistico: {errore}")

    def raccorda_gap_selezionato(self):
        row = self.table_gap_trasporti.currentRow()
        if row < 0:
            QMessageBox.information(self, "Selezione richiesta", "Seleziona prima un'interruzione.")
            return

        tipo_selezionato = self.table_gap_trasporti.item(row, 0).text()
        if not tipo_selezionato.startswith("GAP_"):
            QMessageBox.information(
                self, "Raccordo non disponibile",
                "Questo allarme non è un'interruzione di percorso: non prevede la generazione automatica di un raccordo GPX."
            )
            return

        ids = self.table_gap_trasporti.item(row, 0).data(Qt.UserRole)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT nome_file FROM tappe WHERE id = ?", (ids[0],))
        origine = cursor.fetchone()
        cursor.execute("SELECT nome_file FROM tappe WHERE id = ?", (ids[1],))
        destinazione = cursor.fetchone()
        conn.close()
        if origine and destinazione:
            self.raccorda_traccia_istantaneo(ids[0], ids[1], origine[0], destinazione[0])

    def aggiorna_pagina_dogane(self):
        if not self.current_progetto_id:
            self.lbl_stato_dogane.setText("Apri un percorso per visualizzare i dati doganali salvati.")
            self._imposta_righe_tabella(self.table_dogane, [])
            return

        try:
            righe = analizza_dogane_progetto(self.current_progetto_id)
            self._imposta_righe_tabella(self.table_dogane, righe)
            if righe:
                self.lbl_stato_dogane.setText(f"{len(righe)} attraversamenti doganali salvati.")
            else:
                self.lbl_stato_dogane.setText("Nessun dato doganale salvato per questo percorso.")
        except Exception as errore:
            self.lbl_stato_dogane.setText(f"Errore durante il caricamento dogane: {errore}")

    def aggiorna_pagina_clima(self):
        if not self.current_progetto_id:
            self._clima_progetto_id = None
            self._clima_ordine_base = []
            self._clima_ordine_scenario = None
            self._clima_scenario_id = None
            self._clima_ultima_applicazione_id = None
            self._clima_risultati_correnti = []
            self.btn_estrai_clima.setEnabled(False)
            self.lbl_stato_clima.setText("Apri un percorso per calcolare la catena.")
            self._imposta_righe_tabella(self.table_clima, [])
            self.timeline_clima.imposta_righe([])
            self._aggiorna_controlli_scenario([])
            return

        try:
            self._clima_progetto_id = self.current_progetto_id
            self._clima_ordine_base = []
            self._clima_ordine_scenario = None
            self._clima_scenario_id = None
            self._clima_risultati_correnti = []
            self.btn_estrai_clima.setEnabled(not self._clima_estrazione.attiva)
            service.migrazione_catena_stagionale.assicura_schema_catena_stagionale(
                DB_NAME
            )
            service.migrazione_clima.assicura_schema_clima(DB_NAME)
            service.clima_service.assicura_tabelle_clima()
            scenario_sospeso = (
                service.catena_stagionale_service.ottieni_scenario_in_sospeso(
                    self.current_progetto_id
                )
            )
            if scenario_sospeso:
                self._clima_ordine_scenario = list(
                    scenario_sospeso["ordine"]
                )
                self._clima_scenario_id = int(scenario_sospeso["id"])
            self._clima_ultima_applicazione_id = (
                service.catena_stagionale_service
                .ottieni_ultima_applicazione_scenario(
                    self.current_progetto_id
                )
            )
            with closing(sqlite3.connect(DB_NAME)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT data_partenza, modificatore_riposo
                    FROM progetto_stagione
                    WHERE id_progetto = ?
                    """,
                    (self.current_progetto_id,),
                )
                impostazioni = cursor.fetchone()

            data_corrente = QDate.currentDate()
            self.input_data_partenza.setDate(data_corrente)
            self.input_riposo.setValue(0)
            if impostazioni:
                if impostazioni[0]:
                    data = datetime.strptime(impostazioni[0], "%Y-%m-%d").date()
                    self.input_data_partenza.setDate(
                        QDate(data.year, data.month, data.day)
                    )
                self.input_riposo.setValue(impostazioni[1] or 0)
            self.calcola_pagina_clima()
        except Exception as errore:
            self.lbl_stato_clima.setText(
                f"Errore durante il caricamento clima: {errore}"
            )

    def calcola_pagina_clima(self):
        if not self.current_progetto_id:
            return
        data = self.input_data_partenza.date()
        data_partenza = datetime(data.year(), data.month(), data.day()).date()
        try:
            risultati_base = service.catena_stagionale_service.calcola_catena(
                self.current_progetto_id,
                data_partenza,
                self.input_riposo.value(),
            )
            ordine_base = [
                risultato["nome_blocco"] for risultato in risultati_base
            ]

            self._clima_ordine_base = ordine_base
            if (
                self._clima_ordine_scenario is None
                or self._clima_ordine_scenario == ordine_base
            ):
                if (
                    self._clima_scenario_id is not None
                    and self.current_progetto_id
                ):
                    service.catena_stagionale_service.scarta_scenario_in_sospeso(
                        self.current_progetto_id
                    )
                self._clima_ordine_scenario = list(ordine_base)
                self._clima_scenario_id = None
                risultati = risultati_base
            else:
                risultati = service.catena_stagionale_service.proponi_scenario(
                    self.current_progetto_id,
                    self._clima_ordine_scenario,
                    data_partenza,
                    self.input_riposo.value(),
                )
                scenario_sospeso = (
                    service.catena_stagionale_service
                    .ottieni_scenario_in_sospeso(self.current_progetto_id)
                )
                self._clima_scenario_id = (
                    int(scenario_sospeso["id"])
                    if scenario_sospeso is not None
                    else None
                )

            risultati = service.catena_stagionale_service.calcola_semaforo(
                self.current_progetto_id,
                risultati,
            )
            self._clima_risultati_correnti = risultati
            righe_tabella = []
            stile_righe = []
            for blocco in risultati:
                for indice_riga, risultato in enumerate(
                    [blocco, *blocco.get("paesi", [])]
                ):
                    paese = indice_riga > 0
                    etichetta = (
                        f"  ↳ {risultato['codice_paese']} - "
                        f"{risultato['nome_paese']}"
                        if paese
                        else risultato["nome_blocco"]
                    )
                    righe_tabella.append(
                        [
                            etichetta,
                            risultato["numero_tappe"],
                            f"{risultato['km_totali']:.1f}",
                            risultato["giorni_pedalata"],
                            risultato["giorni_riposo"],
                            risultato["giorni_extra"],
                            risultato["giorni_totali"],
                            datetime.strptime(
                                risultato["data_ingresso"], "%Y-%m-%d"
                            ).strftime("%d/%m/%Y"),
                            datetime.strptime(
                                risultato["data_uscita"], "%Y-%m-%d"
                            ).strftime("%d/%m/%Y"),
                            risultato.get("semaforo", "N/D"),
                            risultato.get("spiegazione_clima", ""),
                            risultato.get("avviso") or "—",
                        ]
                    )
                    stile_righe.append((risultato, paese))

            self._imposta_righe_tabella(self.table_clima, righe_tabella)
            for indice, (risultato, paese) in enumerate(stile_righe):
                for colonna in range(self.table_clima.columnCount()):
                    cella = self.table_clima.item(indice, colonna)
                    if cella is None:
                        continue
                    if not paese:
                        carattere = cella.font()
                        carattere.setBold(True)
                        cella.setFont(carattere)
                    if colonna == 9:
                        cella.setForeground(
                            QColor(risultato.get("semaforo_colore", "#555555"))
                        )
                    if colonna in (9, 10):
                        cella.setToolTip(
                            str(risultato.get("spiegazione_clima", ""))
                        )
            self.timeline_clima.imposta_righe(risultati)
            ordine_attivo = [
                risultato["nome_blocco"] for risultato in risultati
            ]
            self._aggiorna_controlli_scenario(ordine_attivo)

            scenario_attivo = ordine_attivo != self._clima_ordine_base
            avvisi = sum(
                bool(risultato["avviso"]) for risultato in risultati
            )
            paesi_risultati = [
                paese
                for risultato in risultati
                for paese in risultato.get("paesi", [])
            ]
            descrizione = (
                f"Stima con margini per {len(risultati)} blocchi e "
                f"{len(paesi_risultati)} passaggi di paese."
                if risultati
                else "Il percorso non contiene blocchi con tappe attive."
            )
            if scenario_attivo:
                descrizione += " Scenario temporaneo non applicato."
            if avvisi:
                descrizione += f" Attenzione: {avvisi} blocchi richiedono verifica."
            numero_clima = sum(
                paese["semaforo"] in {"verde", "giallo", "rosso"}
                for paese in paesi_risultati
            )
            numero_parziali = sum(
                paese["semaforo"] == "Parziale"
                for paese in paesi_risultati
            )
            if numero_clima:
                descrizione += (
                    f" Semafori climatici disponibili per {numero_clima} "
                    "passaggi di paese."
                )
                if numero_parziali:
                    descrizione += (
                        f" Dati incompleti per altri {numero_parziali} "
                        "passaggi di paese."
                    )
            elif numero_parziali:
                descrizione += (
                    f" Dati climatici incompleti per {numero_parziali} "
                    "passaggi di paese; "
                    "controlla la copertura."
                )
            else:
                descrizione += (
                    " Dati CHELSA non ancora disponibili o incompleti: "
                    "avvia l’estrazione per questo progetto."
                )
            self.lbl_stato_clima.setText(descrizione)
        except Exception as errore:
            self._imposta_righe_tabella(self.table_clima, [])
            self.timeline_clima.imposta_righe([])
            self.lbl_stato_clima.setText(f"Errore durante il calcolo stagionale: {errore}")

    def _carica_soglie_clima(self):
        if not self.current_progetto_id:
            return dict(
                service.catena_stagionale_service.SOGLIE_CLIMA_DEFAULT
            )
        return (
            service.catena_stagionale_service.carica_impostazioni_semaforo(
                self.current_progetto_id
            )
        )

    def apri_soglie_clima(self):
        if not self.current_progetto_id:
            QMessageBox.information(
                self,
                "Percorso richiesto",
                "Apri un percorso prima di modificare le soglie.",
            )
            return
        dialogo = ClimaSoglieDialog(self._carica_soglie_clima(), self)
        if dialogo.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            service.catena_stagionale_service.salva_impostazioni_semaforo(
                self.current_progetto_id, dialogo.valori()
            )
            self.calcola_pagina_clima()
            self.lbl_stato_clima.setText(
                "Preferenze del semaforo salvate per questo percorso. "
                + self.lbl_stato_clima.text()
            )
        except Exception as errore:
            QMessageBox.critical(
                self,
                "Impostazioni non salvate",
                f"Non è stato possibile salvare le soglie: {errore}",
            )

    def avvia_estrazione_clima(self):
        """Avvia l'estrazione climatica CHELSA in background."""
        if not self.current_progetto_id:
            QMessageBox.information(
                self,
                "Percorso richiesto",
                "Apri un percorso prima di estrarre i dati climatici.",
            )
            return
        if self._clima_estrazione.attiva:
            return

        self.btn_estrai_clima.setEnabled(False)
        self.lbl_stato_clima.setText(
            "Estrazione CHELSA avviata. La prima lettura richiede internet; "
            "l’interfaccia resta utilizzabile."
        )
        self._clima_estrazione.avvia(self.current_progetto_id)

    def _al_progresso_clima(self, messaggio):
        """Mostra l'avanzamento dell'estrazione nella barra di stato."""
        self.lbl_stato_clima.setText(messaggio)

    def _estrazione_clima_completata(self, risultato):
        """Ricalcola la pagina clima e comunica quante finestre sono state lette."""
        self.calcola_pagina_clima()
        self.lbl_stato_clima.setText(
            self.lbl_stato_clima.text()
            + f" CHELSA aggiornato: {risultato['file_chelsa_letti']} "
            "finestre raster lette."
        )

    def _estrazione_clima_fallita(self, messaggio):
        """Mostra l'errore avvenuto durante l'estrazione."""
        self.lbl_stato_clima.setText(
            f"Errore nell’estrazione CHELSA: {messaggio}"
        )

    def _estrazione_clima_terminata(self):
        """Riabilita il pulsante di estrazione al termine del thread."""
        self.btn_estrai_clima.setEnabled(bool(self.current_progetto_id))

    def _aggiorna_controlli_scenario(self, ordine_blocchi):
        nome_selezionato = self.combo_blocco_scenario.currentData()
        self.combo_blocco_scenario.clear()
        self.combo_posizione_scenario.clear()

        for nome_blocco in ordine_blocchi:
            self.combo_blocco_scenario.addItem(nome_blocco, nome_blocco)
        for posizione, nome_blocco in enumerate(ordine_blocchi, start=1):
            self.combo_posizione_scenario.addItem(
                f"{posizione}. {nome_blocco}", posizione
            )

        indice_selezionato = self.combo_blocco_scenario.findData(nome_selezionato)
        if indice_selezionato >= 0:
            self.combo_blocco_scenario.setCurrentIndex(indice_selezionato)

        ci_sono_blocchi = len(ordine_blocchi) > 1
        self.combo_blocco_scenario.setEnabled(ci_sono_blocchi)
        self.combo_posizione_scenario.setEnabled(ci_sono_blocchi)
        self.btn_applica_scenario.setEnabled(ci_sono_blocchi)
        self.btn_ripristina_scenario.setEnabled(
            ci_sono_blocchi
            and self._clima_ordine_scenario != self._clima_ordine_base
        )
        self.btn_conferma_scenario.setEnabled(
            self._clima_scenario_id is not None
            and self._clima_ordine_scenario != self._clima_ordine_base
        )
        self.btn_annulla_scenario.setEnabled(
            self._clima_ultima_applicazione_id is not None
        )

    def sposta_blocco_scenario(self):
        ordine_corrente = [
            risultato["nome_blocco"]
            for risultato in self._clima_risultati_correnti
        ]
        nome_blocco = self.combo_blocco_scenario.currentData()
        nuova_posizione = self.combo_posizione_scenario.currentData()
        if (
            not ordine_corrente
            or nome_blocco not in ordine_corrente
            or nuova_posizione is None
        ):
            return

        ordine_proposto = list(ordine_corrente)
        indice_corrente = ordine_proposto.index(nome_blocco)
        blocco = ordine_proposto.pop(indice_corrente)
        ordine_proposto.insert(int(nuova_posizione) - 1, blocco)
        self._clima_ordine_scenario = ordine_proposto
        self.calcola_pagina_clima()

    def ripristina_ordine_scenario(self):
        if self.current_progetto_id:
            service.catena_stagionale_service.scarta_scenario_in_sospeso(
                self.current_progetto_id
            )
        self._clima_ordine_scenario = list(self._clima_ordine_base)
        self._clima_scenario_id = None
        self.calcola_pagina_clima()

    def conferma_scenario_clima(self):
        scenario_id = self._clima_scenario_id
        if scenario_id is None or not self.current_progetto_id:
            return

        ordine_precedente = " → ".join(self._clima_ordine_base)
        ordine_proposto = " → ".join(self._clima_ordine_scenario or [])
        risposta = QMessageBox.question(
            self,
            "Confermare lo scenario?",
            "L'ordine ufficiale in Gestione blocchi verrà aggiornato.\n\n"
            f"Prima: {ordine_precedente}\n\nDopo: {ordine_proposto}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if risposta != QMessageBox.Yes:
            return

        try:
            risultato = (
                service.catena_stagionale_service.conferma_scenario(
                    scenario_id
                )
            )
            self._clima_scenario_id = None
            self._clima_ordine_scenario = None
            self.page_blocchi.carica_blocchi()
            self.aggiorna_pagina_clima()
            QMessageBox.information(
                self,
                "Scenario applicato",
                "L'ordine è stato aggiornato e l'ordine precedente è "
                "conservato per poterlo ripristinare.\n\n"
                f"Nuova sequenza: {' → '.join(risultato['ordine'])}",
            )
        except Exception as errore:
            QMessageBox.critical(
                self,
                "Scenario non applicato",
                f"L'ordine ufficiale non è stato modificato: {errore}",
            )

    def annulla_ultima_applicazione_scenario(self):
        if not self.current_progetto_id:
            return
        scenario_id = (
            service.catena_stagionale_service
            .ottieni_ultima_applicazione_scenario(self.current_progetto_id)
        )
        if scenario_id is None:
            QMessageBox.information(
                self,
                "Nessuna applicazione",
                "Non ci sono scenari da annullare.",
            )
            return
        risposta = QMessageBox.question(
            self,
            "Annullare l'ultima applicazione?",
            "Verrà ripristinato l'ordine dei blocchi precedente allo "
            "scenario. Eventuali modifiche successive all'ordine "
            "impediranno il ripristino.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if risposta != QMessageBox.Yes:
            return
        try:
            risultato = service.catena_stagionale_service.annulla_scenario(
                scenario_id
            )
            self._clima_ordine_scenario = None
            self._clima_scenario_id = None
            self.page_blocchi.carica_blocchi()
            self.aggiorna_pagina_clima()
            QMessageBox.information(
                self,
                "Ordine ripristinato",
                "È stato ripristinato l'ordine precedente:\n"
                f"{' → '.join(risultato['ordine'])}",
            )
        except Exception as errore:
            QMessageBox.critical(
                self,
                "Ripristino non riuscito",
                f"L'ordine non è stato modificato: {errore}",
            )

    def salva_impostazioni_clima(self):
        if not self.current_progetto_id:
            QMessageBox.information(self, "Percorso richiesto", "Apri un percorso prima di salvare le impostazioni.")
            return
        data = self.input_data_partenza.date()
        data_partenza = f"{data.year():04d}-{data.month():02d}-{data.day():02d}"
        try:
            service.clima_service.salva_impostazioni_stagione(
                self.current_progetto_id, data_partenza, self.input_riposo.value()
            )
            self.calcola_pagina_clima()
            self.lbl_stato_clima.setText(
                "Data e riposo salvati. " + self.lbl_stato_clima.text()
            )
        except Exception as errore:
            self.lbl_stato_clima.setText(f"Errore durante il salvataggio clima: {errore}")

    def aggiorna_pagina_statistiche(self):
        if not self.current_progetto_id:
            self.lbl_stato_statistiche.setText("Apri un percorso per calcolare le statistiche.")
            self.card_stats_km.setText("<b>KM TOTALI</b><br><span style='font-size:18pt;'>-</span>")
            self.card_stats_dplus.setText("<b>DISLIVELLO +</b><br><span style='font-size:18pt;'>-</span>")
            self.card_stats_dminus.setText("<b>DISLIVELLO -</b><br><span style='font-size:18pt;'>-</span>")
            self.card_stats_quota.setText("<b>QUOTA MAX</b><br><span style='font-size:18pt;'>-</span>")
            self.card_stats_pendenza.setText("<b>PENDENZA MEDIA</b><br><span style='font-size:18pt;'>-</span>")
            self.card_stats_paesi.setText("<b>PAESI ATTRAVERSATI</b><br><span style='font-size:14pt;'>-</span>")
            self._imposta_righe_tabella(self.table_statistiche_blocchi, [])
            self._imposta_righe_tabella(self.table_statistiche_costa, [])
            return

        try:
            from service import stats_service
            kpi = stats_service.ottieni_kpi_totali_progetto(self.current_progetto_id)
            blocchi = stats_service.ottieni_statistiche_per_blocco(self.current_progetto_id)
            _, totale_paesi, descrizione_paesi = stats_service.get_paesi_attraversati_stats(self.current_progetto_id)
            costa = stats_service.ottieni_ripartizione_fasce_mare(self.current_progetto_id)

            self.card_stats_km.setText(
                f"<b>KM TOTALI</b><br><span style='font-size:18pt; color:#4ec9b0;'>{kpi['km_totali']} km</span>"
            )
            self.card_stats_dplus.setText(
                f"<b>DISLIVELLO +</b><br><span style='font-size:18pt; color:#ce9178;'>{kpi['dislivello_pos']} m</span>"
            )
            self.card_stats_dminus.setText(
                f"<b>DISLIVELLO -</b><br><span style='font-size:18pt; color:#ce9178;'>{kpi['dislivello_neg']} m</span>"
            )
            self.card_stats_quota.setText(
                f"<b>QUOTA MAX</b><br><span style='font-size:18pt; color:#569cd6;'>{kpi['quota_max']} m</span>"
            )
            self.card_stats_pendenza.setText(
                f"<b>PENDENZA MEDIA</b><br><span style='font-size:18pt; color:#dcdcaa;'>{kpi['pendenza_media']} %</span>"
            )
            self.card_stats_paesi.setText(
                f"<b>PAESI ATTRAVERSATI ({totale_paesi})</b><br><span style='font-size:14pt; color:#4ec9b0;'>{descrizione_paesi}</span>"
            )

            self._imposta_righe_tabella(self.table_statistiche_blocchi, blocchi)
            self._imposta_righe_tabella(self.table_statistiche_costa, costa)
            self.table_statistiche_blocchi.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.table_statistiche_costa.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.lbl_stato_statistiche.setText("Statistiche aggiornate.")
        except Exception as errore:
            self.lbl_stato_statistiche.setText(f"Errore durante il calcolo statistiche: {errore}")

    def crea_pagina_placeholder(self, titolo, desc):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 25, 25, 25)
        lbl_titolo = QLabel(titolo)
        lbl_titolo.setFont(QFont("Arial", 16, QFont.Bold))
        lbl_desc = QLabel(desc)
        lbl_desc.setStyleSheet("color: #aaaaaa;")
        layout.addWidget(lbl_titolo)
        layout.addWidget(lbl_desc)
        layout.addStretch()
        return widget

    def apri_pagina_clima(self):
        self.cambia_pagina(6)

    def apri_pagina_statistiche(self):
        self.cambia_pagina(7)

    def verifica_progetto_attivo(self):
        return self.current_progetto_id is not None

    def carica_lista_percorsi(self):
        """Reindirizza al nuovo modulo DashboardPage."""
        self.page_dashboard.carica_lista_percorsi()
    
    def apri_percorso_selezionato(self, item):
        pid, nome = item.data(Qt.UserRole)
        self.current_progetto_id = pid
        self.current_progetto_nome = nome
        self.mappa_necessita_aggiornamento = True
        self.esegui_audit_automatico()
        self.aggiorna_tabella_tappe()
        self.aggiorna_tabella_allarmi()

    def crea_nuovo_progetto_dialog(self):
        """Apre il pianificatore guidato per creare un nuovo percorso."""
        def on_creato(nuovo_id, nome):
            self.carica_lista_percorsi()
            self.current_progetto_id = nuovo_id
            self.current_progetto_nome = nome
            self.aggiorna_tabella_tappe()

        dialog_nuovo_progetto.crea_nuovo_progetto_dialog(self, on_creato)
        
    def apri_selettore_file(self):
        """Apre il file dialog e passa i file selezionati alla pagina Dashboard attiva."""
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Seleziona File GPX", 
            "", 
            "File GPX (*.gpx);;Tutti i file (*.*)"
        )
        
        if files:
            current_widget = self.stacked_widget.currentWidget()
            if hasattr(current_widget, 'elabora_files_gpx'):
                current_widget.elabora_files_gpx(files)
            elif hasattr(self, 'page_dashboard') and self.page_dashboard:
                self.page_dashboard.elabora_files_gpx(files)    
    
    def elabora_files_gpx(self, filepaths):
        """Reindirizza l'elaborazione dei file GPX alla pagina Dashboard modulare."""
        if hasattr(self, 'page_dashboard') and self.page_dashboard:
            self.page_dashboard.elabora_files_gpx(filepaths)
    
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
            self.current_progetto_id, t1_id, t2_id, t1_nome, t2_nome, DB_NAME
        )

        if not nome_raccordo:
            return

        self.esegui_audit_automatico()
        self.mappa_necessita_aggiornamento = True
        self.aggiorna_tabella_tappe()
        if hasattr(self, 'aggiorna_tabella_trasferimenti'):
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
            
        if hasattr(self, 'page_dashboard') and self.page_dashboard:
            self.page_dashboard.aggiorna_tabella_tappe()
    
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
        cursor.execute("SELECT id_progetto FROM tappe WHERE id = ?", (tappa_id,))
        riga = cursor.fetchone()
        id_progetto = riga[0] if riga else self.current_progetto_id
        cursor.execute("DELETE FROM tappe WHERE id = ?", (tappa_id,))
        conn.commit()
        conn.close()

        filepath = trova_percorso_gpx(
            nome_file, id_progetto, directory_gpx=os.path.join(os.getcwd(), "gpx")
        )
        if filepath is not None:
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

    def mostra_mappa_gap(self, end_lat, end_lon, start_lat, start_lon, t1_nome, t2_nome):
        QMessageBox.information(
            self,
            "Mappa GAP",
            f"Coordinate GAP tra:\n{t1_nome} -> ({end_lat}, {end_lon})\n{t2_nome} -> ({start_lat}, {start_lon})"
        )

    def avvia_wizard_trasferimento(self, allarme_id):
        """Apre il wizard per registrare il trasferimento che copre un gap."""
        if not self.verifica_progetto_attivo():
            return

        try:
            allarme = trasferimenti_service.carica_allarme_gap(
                self.current_progetto_id, allarme_id
            )
        except sqlite3.Error as errore:
            QMessageBox.critical(
                self,
                "Lettura del gap non riuscita",
                f"Non riesco a leggere l'allarme dal database:\n{errore}",
            )
            return

        if allarme is None:
            QMessageBox.warning(
                self,
                "Gap non disponibile",
                "L'allarme selezionato non è più attivo nel percorso aperto. "
                "Aggiorno l'elenco degli allarmi.",
            )
            self.esegui_audit_automatico()
            self.aggiorna_tabella_allarmi()
            return

        coordinate, errore = trasferimenti_service.valida_coordinate_gap(allarme)
        if coordinate is None:
            titolo, messaggio = errore.split("\n", 1)
            QMessageBox.warning(self, titolo, messaggio)
            return

        origine_lat, origine_lon, destinazione_lat, destinazione_lon = coordinate
        nome_origine, nome_destinazione = trasferimenti_service.nomi_tappe_gap(allarme)
        dati = dialog_wizard_trasferimento.chiedi_dati_trasferimento(
            self, nome_origine, nome_destinazione, coordinate
        )
        if dati is None:
            return
        if not dati["da"] or not dati["a"]:
            QMessageBox.warning(
                self,
                "Dati incompleti",
                "Inserisci i luoghi di partenza e di arrivo.",
            )
            return

        try:
            gia_coperto = not trasferimenti_service.salva_trasferimento(
                self.current_progetto_id, dati, coordinate
            )
        except sqlite3.Error as errore:
            QMessageBox.critical(
                self,
                "Salvataggio trasferimento non riuscito",
                f"Il database ha rifiutato il trasferimento:\n{errore}",
            )
            return

        if gia_coperto:
            QMessageBox.information(
                self,
                "Gap già coperto",
                "Esiste già un trasferimento con questi estremi. "
                "Aggiorno l'audit senza crearne un duplicato.",
            )

        self.esegui_audit_automatico()
        self.aggiorna_tabella_allarmi()
        self.aggiorna_pagina_trasporti()
        self.mappa_necessita_aggiornamento = True
        QMessageBox.information(
            self,
            "Logistica aggiornata",
            (
                "Il trasferimento è stato registrato e l'audit è stato "
                "ricalcolato. Se il gap non compare più nell'elenco, risulta "
                "coperto."
                if not gia_coperto
                else "Il trasferimento esistente è stato riconosciuto e "
                "l'audit è stato ricalcolato."
            ),
        )

    def aggiorna_tabella_allarmi(self):
        if not self.verifica_progetto_attivo():
            if hasattr(self, 'table_allarmi'):
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
            btn_trasferimento.clicked.connect(lambda _, aid=allarme_id: self.avvia_wizard_trasferimento(aid))

            layout_azioni.addWidget(btn_mappa_gap)
            layout_azioni.addWidget(btn_raccorda)
            layout_azioni.addWidget(btn_trasferimento)
            self.table_allarmi.setCellWidget(row_idx, 3, panel_azioni)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BikepackingStudioApp()
    window.show()
    sys.exit(app.exec())
