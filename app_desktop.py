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
from gui.pagine.pagina_clima import PaginaClima
from gui.pagine.pagina_statistiche import PaginaStatistiche
from gui.pagine.pagina_audit import PaginaAudit
from gui.pagine.pagina_trasporti import PaginaTrasporti
from gui.pagine.pagina_dogane import PaginaDogane
from gui.pagine.stile_pagina import imposta_righe_tabella
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
        """Crea la pagina Audit e la registra come `page_audit`."""
        self.page_audit = PaginaAudit(
            self.mostra_mappa_gap,
            self.raccorda_traccia_istantaneo,
            self.avvia_wizard_trasferimento,
            self,
        )
        return self.page_audit

    def _imposta_righe_tabella(self, tabella, righe):
        """Delega al helper condiviso il riempimento di una tabella."""
        imposta_righe_tabella(tabella, righe)

    def crea_pagina_trasporti(self):
        """Crea la pagina Trasporti e la registra come `page_trasporti`."""
        self.page_trasporti = PaginaTrasporti(
            self.raccorda_traccia_istantaneo, self
        )
        return self.page_trasporti

    def crea_pagina_dogane(self):
        """Crea la pagina Dogane e la registra come `page_dogane`."""
        self.page_dogane = PaginaDogane(self)
        return self.page_dogane

    def crea_pagina_clima(self):
        """Crea la pagina Clima, la registra come `page_clima` e ne espone i controlli.

        I controlli restano raggiungibili anche come attributi della finestra
        (`lbl_stato_clima`, `table_clima`, ...): la logica esistente li usa
        senza modifiche, mentre costruzione e layout vivono nel modulo.
        """
        self.page_clima = PaginaClima(self, self)
        self._esporta_controlli_clima(self.page_clima)
        self._aggiorna_controlli_scenario([])
        return self.page_clima

    def _esporta_controlli_clima(self, pagina):
        """Collega alla finestra i controlli della pagina clima.

        :param pagina: istanza di `PaginaClima` già costruita.
        """
        coppie = (
            ("lbl_stato_clima", pagina.lbl_stato),
            ("lbl_regole_clima", pagina.lbl_regole),
            ("timeline_clima", pagina.timeline),
            ("area_timeline_clima", pagina.area_timeline),
            ("table_clima", pagina.tabella),
            ("input_data_partenza", pagina.input_data_partenza),
            ("input_riposo", pagina.input_riposo),
            ("btn_estrai_clima", pagina.btn_estrai_clima),
            ("btn_soglie_clima", pagina.btn_soglie_clima),
            ("combo_blocco_scenario", pagina.combo_blocco_scenario),
            ("combo_posizione_scenario", pagina.combo_posizione_scenario),
            ("btn_applica_scenario", pagina.btn_applica_scenario),
            ("btn_ripristina_scenario", pagina.btn_ripristina_scenario),
            ("btn_conferma_scenario", pagina.btn_conferma_scenario),
            ("btn_annulla_scenario", pagina.btn_annulla_scenario),
        )
        for nome, controllo in coppie:
            setattr(self, nome, controllo)

    def crea_pagina_statistiche(self):
        """Crea la pagina Statistiche e la registra come `page_stats`."""
        self.page_stats = PaginaStatistiche(
            self.apri_finestra_elenco_paesi, self
        )
        return self.page_stats

    def apri_finestra_elenco_paesi(self):
        """Mostra il dialogo con l'elenco dei paesi attraversati dal percorso."""
        if not self.current_progetto_id:
            QMessageBox.information(self, "Percorso richiesto", "Apri un percorso per visualizzare i paesi attraversati.")
            return

        from service import stats_service
        lista_paesi, totale_paesi, _ = stats_service.get_paesi_attraversati_stats(self.current_progetto_id)
        dialog_elenco_paesi.crea_elenco_paesi(self, lista_paesi, totale_paesi)

    def aggiorna_pagina_trasporti(self):
        """Ricarica la pagina Trasporti per il percorso corrente."""
        self.page_trasporti.aggiorna(self.current_progetto_id)

    def raccorda_gap_selezionato(self):
        """Delega alla pagina Trasporti la generazione del raccordo GPX."""
        self.page_trasporti.raccorda_gap_selezionato()

    def aggiorna_pagina_dogane(self):
        """Ricarica la pagina Dogane per il percorso corrente."""
        self.page_dogane.aggiorna(self.current_progetto_id)

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
        """Ricalcola la pagina Statistiche per il percorso corrente."""
        self.page_stats.aggiorna(self.current_progetto_id)

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
        """Ricarica la tabella degli allarmi per il percorso corrente."""
        self.page_audit.aggiorna(self.current_progetto_id)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BikepackingStudioApp()
    window.show()
    sys.exit(app.exec())
