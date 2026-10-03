"""Pagina di servizio "Catena Stagionale & Clima".

Costruisce l'interfaccia della pagina clima: parametri di calcolo, comandi
di estrazione CHELSA, controlli dello scenario, timeline del viaggio e
tabella di dettaglio. La logica di calcolo resta alla finestra principale:
questa pagina le passa i propri controlli tramite il riferimento `app`,
senza importare `app_desktop.py`.
"""

from PySide6.QtCore import QDate
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from gui.widget_timeline_catena import TimelineCatenaWidget

from gui.pagine.stile_pagina import applica_stile_servizio

# Colonne della tabella di dettaglio clima.
COLONNE_CLIMA = [
    "Blocco / paese",
    "Tappe",
    "Km",
    "Pedalata",
    "Riposo",
    "Buffer",
    "Totale giorni",
    "Ingresso",
    "Uscita",
    "Semaforo",
    "Motivazione climatica",
    "Nota",
]

# Testo che spiega le regole di calcolo della catena stagionale.
REGOLE_CATENA = (
    "1 tappa = 1 giorno; 1 riposo ogni 5 tappe; buffer: 5 giorni per "
    "mese di calendario attraversato e 7 giorni ogni 4 mesi. "
    "I buffer non ne generano altri."
)
class PaginaClima(QWidget):
    """Interfaccia della pagina clima: calcolo, estrazione e scenario."""

    def __init__(self, app, parent=None):
        """Costruisce la pagina e collega i pulsanti ai metodi di `app`.

        :param app: finestra principale che espone i metodi di calcolo,
            estrazione e gestione dello scenario. Non viene importata: è
            ricevuta come oggetto già costruito.
        """
        super().__init__(parent)
        self.app = app
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        lbl = QLabel("🗓️ Catena Stagionale & Clima")
        lbl.setFont(QFont("Arial", 16, QFont.Bold))
        lbl.setStyleSheet("color: #0e639c;")
        layout.addWidget(lbl)

        layout.addLayout(self._crea_riga_parametri())
        layout.addLayout(self._crea_riga_estrazione())
        layout.addLayout(self._crea_riga_scenario())

        self.lbl_stato = QLabel(
            "Stima con margini: la proiezione non è una probabilità matematica."
        )
        layout.addWidget(self.lbl_stato)
        self.lbl_regole = QLabel(REGOLE_CATENA)
        self.lbl_regole.setWordWrap(True)
        layout.addWidget(self.lbl_regole)

        layout.addWidget(self._etichetta_sezione("Timeline del viaggio"))
        self.timeline = TimelineCatenaWidget()
        self.area_timeline = QScrollArea()
        self.area_timeline.setWidgetResizable(True)
        self.area_timeline.setMaximumHeight(190)
        self.area_timeline.setWidget(self.timeline)
        layout.addWidget(self.area_timeline)

        layout.addWidget(self._etichetta_sezione("Dettaglio per blocco e paese"))
        self.tabella = QTableWidget()
        self.tabella.setColumnCount(len(COLONNE_CLIMA))
        self.tabella.setHorizontalHeaderLabels(COLONNE_CLIMA)
        self.tabella.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.tabella.horizontalHeader().setStretchLastSection(True)
        self.tabella.setMaximumHeight(450)
        layout.addWidget(self.tabella)

        applica_stile_servizio(self)

    def _etichetta_sezione(self, testo):
        """Crea l'etichetta di intestazione di una sezione della pagina."""
        etichetta = QLabel(testo)
        etichetta.setStyleSheet("font-weight: bold; color: #cccccc;")
        return etichetta

    def _crea_riga_parametri(self):
        """Crea la riga con data di partenza, riposo e pulsanti Calcola/Salva."""
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
        btn_calcola.clicked.connect(self.app.calcola_pagina_clima)
        controls.addWidget(btn_calcola)
        btn_salva = QPushButton("Salva impostazioni")
        btn_salva.clicked.connect(self.app.salva_impostazioni_clima)
        controls.addWidget(btn_salva)
        return controls

    def _crea_riga_estrazione(self):
        """Crea la riga con i comandi di estrazione CHELSA e semaforo."""
        controlli_clima = QHBoxLayout()
        self.btn_estrai_clima = QPushButton(
            "Estrai/aggiorna dati CHELSA per paese"
        )
        self.btn_estrai_clima.clicked.connect(self.app.avvia_estrazione_clima)
        controlli_clima.addWidget(self.btn_estrai_clima)
        self.btn_soglie_clima = QPushButton("Impostazioni semaforo")
        self.btn_soglie_clima.clicked.connect(self.app.apri_soglie_clima)
        controlli_clima.addWidget(self.btn_soglie_clima)
        controlli_clima.addWidget(
            QLabel(
                "Internet serve per l’estrazione; i riepiloghi restano poi offline."
            )
        )
        controlli_clima.addStretch(1)
        return controlli_clima

    def _crea_riga_scenario(self):
        """Crea la riga dei comandi di riordino dello scenario climatico."""
        controlli_scenario = QHBoxLayout()
        controlli_scenario.addWidget(QLabel("Sposta nello scenario"))
        self.combo_blocco_scenario = QComboBox()
        self.combo_blocco_scenario.setMinimumWidth(180)
        controlli_scenario.addWidget(self.combo_blocco_scenario)
        controlli_scenario.addWidget(QLabel("nuova posizione"))
        self.combo_posizione_scenario = QComboBox()
        controlli_scenario.addWidget(self.combo_posizione_scenario)
        self.btn_applica_scenario = QPushButton("Prova spostamento")
        self.btn_applica_scenario.clicked.connect(self.app.sposta_blocco_scenario)
        controlli_scenario.addWidget(self.btn_applica_scenario)
        self.btn_ripristina_scenario = QPushButton("Ripristina ordine")
        self.btn_ripristina_scenario.clicked.connect(
            self.app.ripristina_ordine_scenario
        )
        controlli_scenario.addWidget(self.btn_ripristina_scenario)
        self.btn_conferma_scenario = QPushButton("Conferma scenario")
        self.btn_conferma_scenario.clicked.connect(self.app.conferma_scenario_clima)
        controlli_scenario.addWidget(self.btn_conferma_scenario)
        self.btn_annulla_scenario = QPushButton("Annulla ultima applicazione")
        self.btn_annulla_scenario.clicked.connect(
            self.app.annulla_ultima_applicazione_scenario
        )
        controlli_scenario.addWidget(self.btn_annulla_scenario)
        return controlli_scenario