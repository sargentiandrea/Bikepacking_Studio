import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sqlite3
import service.audit_service

from service.map_server import start_local_map_server
# Avvia il server delle mappe locale su porta 8080
start_local_map_server(port=8080)
from PySide6.QtCore import Qt
# -- Moduli GUI --
from gui.dashboard import DashboardPage
from gui.mappa import MappaWidget
from gui.widget_blocchi import GestoreBlocchiWidget
from gui.pagine.controller_clima import ControllerClima
from gui.pagine.pagina_clima import PaginaClima
from gui.pagine.pagina_statistiche import PaginaStatistiche
from gui.pagine.pagina_audit import PaginaAudit
from gui.pagine.pagina_trasporti import PaginaTrasporti
from gui.pagine.pagina_dogane import PaginaDogane
from gui import dialog_elenco_paesi
from gui import dialog_nuovo_progetto
from gui import dialog_wizard_trasferimento
from service import progetti_service
from service import trasferimenti_service


# Import dei moduli interni del progetto
import database.database_setup as database
database.inizializza_database()

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QLabel, QStackedWidget, 
                             QFrame, QFileDialog, QMessageBox)
from PySide6.QtGui import QFont
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
        # Il controller possiede stato, calcolo e scenario della pagina clima.
        self._clima = ControllerClima(self)

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
        """Ricarica la pagina clima delegando al controller."""
        self._clima.aggiorna()

    def _aggiorna_controlli_scenario(self, ordine_blocchi):
        """Abilita e popola i controlli dello scenario in base ai blocchi."""
        controller = self._clima
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
            and controller.ordine_scenario != controller.ordine_base
        )
        self.btn_conferma_scenario.setEnabled(
            controller.scenario_id is not None
            and controller.ordine_scenario != controller.ordine_base
        )
        self.btn_annulla_scenario.setEnabled(
            controller.ultima_applicazione_id is not None
        )

    def calcola_pagina_clima(self):
        """Ricalcola la catena stagionale delegando al controller clima."""
        self._clima.calcola()

    def _carica_soglie_clima(self):
        """Restituisce le soglie del semaforo del progetto corrente."""
        return self._clima.carica_soglie()

    def apri_soglie_clima(self):
        """Apre il dialogo delle soglie climatiche del progetto."""
        self._clima.apri_soglie()

    def avvia_estrazione_clima(self):
        """Avvia l'estrazione climatica CHELSA in background."""
        self._clima.avvia_estrazione()

    def sposta_blocco_scenario(self):
        """Sposta il blocco selezionato nello scenario temporaneo."""
        self._clima.sposta_blocco()

    def ripristina_ordine_scenario(self):
        """Scarta lo scenario temporaneo e torna all'ordine ufficiale."""
        self._clima.ripristina_ordine()

    def conferma_scenario_clima(self):
        """Applica all'ordine ufficiale lo scenario temporaneo."""
        self._clima.conferma_scenario()

    def annulla_ultima_applicazione_scenario(self):
        """Ripristina l'ordine precedente all'ultimo scenario applicato."""
        self._clima.annulla_ultima_applicazione()

    def salva_impostazioni_clima(self):
        """Salva data di partenza e modificatore di riposo del progetto."""
        self._clima.salva_impostazioni()

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
        service.audit_service.ricalcola_allarmi_percorso(self.current_progetto_id)
    
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
    
    def elimina_percorso_corrente(self):
        """Chiede conferma e elimina il percorso attivo con tutti i suoi dati."""
        if not self.current_progetto_id:
            return
        conf = QMessageBox.question(self, "Elimina Percorso", f"Sei sicuro di voler eliminare l'intero percorso '{self.current_progetto_nome}'?", QMessageBox.Yes | QMessageBox.No)
        if conf == QMessageBox.Yes:
            progetti_service.elimina_progetto_completo(self.current_progetto_id)

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
