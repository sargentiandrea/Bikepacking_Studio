"""Widget di pianificazione del percorso; non importa gui.mappa per evitare cicli."""

import os
import sqlite3

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QButtonGroup,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QDoubleSpinBox,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from gui.mappa_dettagli import PannelloDettagliRotta
from gui.mappa_worker import (
    PianificazionePercorsoWorker,
    WorkerAltimetria,
    WorkerAnalisiSuperficiOffline,
    WorkerNomiLuoghi,
)
from gui.mappa_worker_manager import GestoreWorkerSingolo
from service.config import BASE_DIR, DB_NAME
from service.dettagli_rotta_service import (
    testo_stato_annullato,
    testo_stato_anteprima_pronta,
    testo_stato_calcolo,
    testo_stato_campi_cambiati,
    testo_stato_errore_routing,
    testo_stato_percorso_lungo,
)
from service.geo_utils import calcola_distanza_haversine
from service.mappa_dati_service import carica_coordinate_tappa, carica_tappe_attive
from service.planning_context_service import (
    CONTESTI_PIANIFICAZIONE,
    carica_blocchi_progetto,
    stato_da_contesto,
    valida_nome_nuovo_blocco,
)
from service.punti_service import (
    aggiorna_testi_tappe,
    estremi_tappa,
    etichetta_punto,
    firma_pianificazione,
    indice_primo_punto_vuoto,
    prepara_tappe_intermedie,
    testo_coordinate,
    testo_intestazione_tappe_intermedie,
    testo_riga_tappa_intermedia,
    testo_segnaposto_punto,
    valida_pianificazione,
)
from service.salvataggio_tappa_service import (
    rimuovi_gpx_se_esiste,
    salva_percorso_suddiviso,
    salva_tappa_pianificata,
)
from service.suddivisione_percorso_service import (
    calcola_suddivisione_numero_tappe,
    calcola_suddivisione_percorso,
)
from service.waypoint_service import classifica_punto


GPX_DIR = os.path.join(BASE_DIR, "gpx")


class PannelloPianificazioneWidget(QFrame):
    """Pannello fluttuante in stile Komoot / Bikemap sovrapposto alla mappa."""
    def __init__(self, parent=None, mappa_widget=None):
        """Crea il pannello e collega le sue azioni al widget mappa proprietario."""
        super().__init__(parent)
        self.mappa_widget = mappa_widget
        self.punti_passaggio = []
        self.tappa_in_modifica_id = None
        self.ultima_anteprima = None
        self.firma_ultima_anteprima = None
        self._contesto_selezionato = None
        self._blocchi_disponibili = []
        self._errore_caricamento_blocchi = False
        self._suddivisione_anteprima = None
        self._tappe_ids_da_sostituire = None
        self._waypoint_devia_tappa_singola = False
        self._progetto_sincronizzato_id = "non_ancora_verificato"  # sentinella diversa da None/ID reali
        # Ciclo di vita del worker analisi-superfici nel gestore unico.
        self._gestore_superfici = GestoreWorkerSingolo(
            WorkerAnalisiSuperficiOffline, "analisi_completata", self._fine_analisi_superfici_offline
        )
        # Ciclo di vita del worker nomi-luoghi nel gestore unico.
        self._gestore_nomi = GestoreWorkerSingolo(
            WorkerNomiLuoghi, "nomi_pronti", self._fine_risoluzione_nomi_luoghi
        )
        # Ciclo di vita del worker altimetria (token, coda, sopravvivenza) nel gestore unico.
        self._gestore_altimetria = GestoreWorkerSingolo(
            WorkerAltimetria, "altimetria_pronta", self._fine_analisi_altimetria
        )
        # Ciclo di vita del worker di routing: anche lui va nel gestore unico,
        # così una nuova richiesta durante un calcolo mette in coda invece di
        # lasciare due thread BRouter contemporanei.
        self._gestore_rotta = GestoreWorkerSingolo(
            self._crea_worker_rotta, "esito", self._risultato_worker_rotta
        )
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

        lbl_contesto = QLabel("Cosa stai creando?")
        lbl_contesto.setStyleSheet("color: #f8fafc; font-size: 13px; font-weight: bold;")
        contenuto_layout.addWidget(lbl_contesto)

        gruppo_righe_contesto = QVBoxLayout()
        gruppo_righe_contesto.setSpacing(6)
        self.gruppo_contesti = QButtonGroup(self)
        self.gruppo_contesti.setExclusive(True)
        self.pulsanti_contesto = {}
        for riga_contesti in (CONTESTI_PIANIFICAZIONE[:2], CONTESTI_PIANIFICAZIONE[2:]):
            layout_riga = QHBoxLayout()
            layout_riga.setSpacing(6)
            for valore_contesto, etichetta_contesto in riga_contesti:
                pulsante = QPushButton(etichetta_contesto)
                pulsante.setCheckable(True)
                pulsante.setCursor(Qt.PointingHandCursor)
                pulsante.setMinimumHeight(38)
                pulsante.setStyleSheet(
                    "QPushButton { background: #2d2d2d; color: #cbd5e1; "
                    "border: 1px solid #475569; border-radius: 6px; padding: 6px; } "
                    "QPushButton:checked { background: #075985; color: white; "
                    "border: 1px solid #38bdf8; font-weight: bold; }"
                )
                pulsante.clicked.connect(
                    lambda selezionato, valore=valore_contesto: (
                        self._imposta_contesto(valore) if selezionato else None
                    )
                )
                self.gruppo_contesti.addButton(pulsante)
                self.pulsanti_contesto[valore_contesto] = pulsante
                layout_riga.addWidget(pulsante)
            gruppo_righe_contesto.addLayout(layout_riga)
        contenuto_layout.addLayout(gruppo_righe_contesto)

        self.lbl_riepilogo_contesto = QLabel(
            "Scegli una delle quattro opzioni prima di salvare."
        )
        self.lbl_riepilogo_contesto.setWordWrap(True)
        contenuto_layout.addWidget(self.lbl_riepilogo_contesto)

        self.pannello_blocco_contesto = QWidget()
        layout_blocco_contesto = QVBoxLayout(self.pannello_blocco_contesto)
        layout_blocco_contesto.setContentsMargins(0, 0, 0, 0)
        layout_blocco_contesto.setSpacing(6)
        self.combo_blocco_contesto = QComboBox()
        self.combo_blocco_contesto.currentIndexChanged.connect(
            self._aggiorna_nuovo_blocco_visibile
        )
        self.input_nuovo_blocco = QLineEdit()
        self.input_nuovo_blocco.setPlaceholderText("Nome del nuovo blocco...")
        layout_blocco_contesto.addWidget(QLabel("A quale blocco appartiene?"))
        layout_blocco_contesto.addWidget(self.combo_blocco_contesto)
        layout_blocco_contesto.addWidget(self.input_nuovo_blocco)
        self.pannello_blocco_contesto.setVisible(False)
        contenuto_layout.addWidget(self.pannello_blocco_contesto)

        self.pannello_suddivisione = QWidget()
        layout_suddivisione = QVBoxLayout(self.pannello_suddivisione)
        layout_suddivisione.setContentsMargins(0, 0, 0, 0)
        layout_suddivisione.setSpacing(6)
        lbl_suddivisione = QLabel("Suddividi il percorso in tappe")
        lbl_suddivisione.setStyleSheet(
            "color: #f8fafc; font-size: 12px; font-weight: bold;"
        )
        layout_suddivisione.addWidget(lbl_suddivisione)

        riga_km = QHBoxLayout()
        self.radio_km_per_tappa = QRadioButton("Km per tappa")
        self.radio_km_per_tappa.setChecked(True)
        self.spin_km_per_tappa = QDoubleSpinBox()
        self.spin_km_per_tappa.setRange(1.0, 10000.0)
        self.spin_km_per_tappa.setDecimals(1)
        self.spin_km_per_tappa.setValue(120.0)
        self.spin_km_per_tappa.setSuffix(" km")
        riga_km.addWidget(self.radio_km_per_tappa)
        riga_km.addStretch()
        riga_km.addWidget(self.spin_km_per_tappa)
        layout_suddivisione.addLayout(riga_km)

        riga_giorni = QHBoxLayout()
        self.radio_giorni_per_tappa = QRadioButton("Giorni per tappa")
        self.spin_giorni_per_tappa = QSpinBox()
        self.spin_giorni_per_tappa.setRange(1, 365)
        self.spin_giorni_per_tappa.setValue(1)
        self.spin_giorni_per_tappa.setSuffix(" giorni")
        riga_giorni.addWidget(self.radio_giorni_per_tappa)
        riga_giorni.addStretch()
        riga_giorni.addWidget(self.spin_giorni_per_tappa)
        layout_suddivisione.addLayout(riga_giorni)
        lbl_stima_giornata = QLabel("La stima considera 6 ore effettive di bici al giorno.")
        lbl_stima_giornata.setWordWrap(True)
        layout_suddivisione.addWidget(lbl_stima_giornata)

        self.lbl_anteprima_suddivisione = QLabel(
            "L'anteprima della suddivisione comparirà dopo il calcolo della rotta."
        )
        self.lbl_anteprima_suddivisione.setWordWrap(True)
        layout_suddivisione.addWidget(self.lbl_anteprima_suddivisione)
        self.pannello_suddivisione.setVisible(False)
        contenuto_layout.addWidget(self.pannello_suddivisione)

        self.radio_km_per_tappa.toggled.connect(
            self._modalita_suddivisione_modificata
        )
        self.radio_giorni_per_tappa.toggled.connect(
            self._modalita_suddivisione_modificata
        )
        self.spin_km_per_tappa.valueChanged.connect(
            self._aggiorna_anteprima_suddivisione
        )
        self.spin_giorni_per_tappa.valueChanged.connect(
            self._aggiorna_anteprima_suddivisione
        )

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

        self.dettagli_rotta = PannelloDettagliRotta()
        contenuto_layout.addWidget(self.dettagli_rotta)
        
        # --- PROFILO DI INSTRADAMENTO ---
        lbl_profilo = QLabel("Profilo di instradamento")
        lbl_profilo.setStyleSheet("color: #94a3b8; font-size: 11px; margin-top: 4px; border: none;")
        contenuto_layout.addWidget(lbl_profilo)
        
        self.combo_profilo = QComboBox()
        self.combo_profilo.addItems(["🚲 Gravel / Viaggio", "🛣️ Strada", "🚵 MTB", "⚖️ Equilibrato"])
        contenuto_layout.addWidget(self.combo_profilo)
        
        # --- PULSANTE DI SALVATAGGIO / AZIONE ---
        self.btn_salva = QPushButton("Scegli cosa creare")
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
        self.adatta_altezza()

    def _imposta_contesto(self, contesto):
        """Aggiorna il contesto selezionato e mostra solo i campi che gli servono."""
        if (
            self._tappe_ids_da_sostituire is not None
            and contesto != "percorso"
        ):
            risposta = QMessageBox.question(
                self,
                "Annullare la deviazione completa?",
                "Se cambi contesto, la modifica di tutte le tappe attive "
                "verrà annullata. Vuoi continuare?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if risposta != QMessageBox.Yes:
                self.pulsanti_contesto["percorso"].setChecked(True)
                return
            self._azzera_sostituzione_percorso()

        self._contesto_selezionato = contesto
        etichette = dict(CONTESTI_PIANIFICAZIONE)
        descrizioni = {
            "tappa_unica": "Una sola tappa, senza suddivisione automatica.",
            "percorso": "Un percorso completo, pronto per la successiva suddivisione.",
            "parte_viaggio": "Una tappa da aggiungere a un blocco del viaggio.",
            "test": "Una bozza tecnica, non conteggiata come tappa attiva.",
        }
        self.lbl_riepilogo_contesto.setText(
            f"{etichette[contesto]}: {descrizioni[contesto]}"
        )
        if hasattr(self, "btn_salva"):
            self.btn_salva.setText(self._testo_pulsante_salvataggio())
        mostra_blocchi = contesto == "parte_viaggio"
        self.pannello_blocco_contesto.setVisible(mostra_blocchi)
        mostra_suddivisione = contesto == "percorso"
        self.pannello_suddivisione.setVisible(mostra_suddivisione)
        if mostra_blocchi:
            self._carica_blocchi_contesto()
        self._aggiorna_anteprima_suddivisione()

    def _modalita_suddivisione_modificata(self, selezionata):
        """Ricalcola l'anteprima solo quando cambia la modalità selezionata."""
        if selezionata:
            self._aggiorna_anteprima_suddivisione()

    def _aggiorna_anteprima_suddivisione(self):
        """Aggiorna il riepilogo e i punti di divisione sulla mappa."""
        anteprima = self.ultima_anteprima
        if self._contesto_selezionato != "percorso" or not anteprima:
            self._suddivisione_anteprima = None
            if hasattr(self, "lbl_anteprima_suddivisione"):
                self.lbl_anteprima_suddivisione.setText(
                    "L'anteprima della suddivisione comparirà dopo il calcolo della rotta."
                )
            if anteprima and self.mappa_widget:
                self.mappa_widget.mostra_anteprima_percorso(
                    anteprima["coordinate"],
                    adatta_visuale=False,
                )
            return

        statistiche = anteprima.get("statistiche") or {}
        opzioni = {
            "distanza_totale_km": statistiche.get("distanza_km"),
        }
        if self.radio_km_per_tappa.isChecked():
            opzioni["km_per_tappa"] = self.spin_km_per_tappa.value()
        else:
            opzioni["giorni_per_tappa"] = self.spin_giorni_per_tappa.value()
            opzioni["tempo_totale_ore"] = statistiche.get("tempo_totale_ore")

        try:
            if self._tappe_ids_da_sostituire is not None:
                self._suddivisione_anteprima = calcola_suddivisione_numero_tappe(
                    anteprima["coordinate"],
                    distanza_totale_km=opzioni["distanza_totale_km"],
                    numero_tappe=len(self._tappe_ids_da_sostituire),
                )
            else:
                self._suddivisione_anteprima = calcola_suddivisione_percorso(
                    anteprima["coordinate"],
                    **opzioni,
                )
        except ValueError as errore:
            self._suddivisione_anteprima = None
            self.lbl_anteprima_suddivisione.setText(str(errore))
            self.mappa_widget.mostra_anteprima_percorso(
                anteprima["coordinate"],
                adatta_visuale=False,
            )
            return

        divisione = self._suddivisione_anteprima
        distanze = ", ".join(f"{km:g}" for km in divisione["distanze_km"])
        if self._tappe_ids_da_sostituire is not None:
            testo_divisione = (
                f'{divisione["numero_tappe"]} tappe esistenti: {distanze} km. '
                "Saranno mantenuti ordine e blocchi attuali."
            )
        else:
            unita = (
                "km per tappa"
                if divisione["modalita"] == "km"
                else "km al giorno"
            )
            testo_divisione = (
                f'{divisione["numero_tappe"]} tappe: {distanze} km ({unita}). '
                "I punti di divisione sono evidenziati sulla mappa."
            )
        self.lbl_anteprima_suddivisione.setText(testo_divisione)
        self.mappa_widget.mostra_anteprima_percorso(
            anteprima["coordinate"],
            divisione["punti_divisione"],
            adatta_visuale=False,
        )

    def _carica_blocchi_contesto(self):
        """Carica i blocchi del progetto per l'assegnazione della nuova tappa."""
        progetto = getattr(
            getattr(self.mappa_widget, "parent_app", None),
            "current_progetto_id",
            None,
        )
        self.combo_blocco_contesto.clear()
        self._blocchi_disponibili = []
        self._errore_caricamento_blocchi = False
        if not progetto:
            self.lbl_riepilogo_contesto.setText(
                "Apri prima un percorso per scegliere o creare un blocco."
            )
            return
        try:
            self._blocchi_disponibili = carica_blocchi_progetto(progetto, DB_NAME)
        except sqlite3.Error as errore:
            self._errore_caricamento_blocchi = True
            self.combo_blocco_contesto.setEnabled(False)
            QMessageBox.critical(
                self,
                "Blocchi non disponibili",
                f"Non è stato possibile leggere i blocchi del percorso: {errore}",
            )
            return

        self.combo_blocco_contesto.setEnabled(True)
        self.combo_blocco_contesto.addItems(self._blocchi_disponibili)
        self.combo_blocco_contesto.addItem("+ Crea un nuovo blocco...")
        if not self._blocchi_disponibili:
            self.combo_blocco_contesto.setCurrentIndex(0)
        self._aggiorna_nuovo_blocco_visibile()

    def _aggiorna_nuovo_blocco_visibile(self):
        """Mostra il campo nome solo quando è selezionata la creazione di un blocco."""
        crea_nuovo = (
            self._contesto_selezionato == "parte_viaggio"
            and self.combo_blocco_contesto.currentIndex()
            == len(self._blocchi_disponibili)
        )
        self.input_nuovo_blocco.setVisible(crea_nuovo)

    def _dati_contesto_salvataggio(self, mostra_dialogo=True):
        """Valida la scelta e restituisce stato, blocco e modalità di creazione."""
        if self._contesto_selezionato is None:
            if mostra_dialogo:
                QMessageBox.warning(
                    self,
                    "Contesto richiesto",
                    "Scegli cosa stai creando prima di salvare.",
                )
            return None

        blocco = None
        crea_blocco = False
        if self._contesto_selezionato == "parte_viaggio":
            if self._errore_caricamento_blocchi:
                if mostra_dialogo:
                    QMessageBox.warning(
                        self,
                        "Blocchi non disponibili",
                        "Riprova dopo aver verificato il database del percorso.",
                    )
                return None
            indice = self.combo_blocco_contesto.currentIndex()
            if indice == len(self._blocchi_disponibili):
                blocco, errore = valida_nome_nuovo_blocco(
                    self.input_nuovo_blocco.text(),
                    self._blocchi_disponibili,
                )
                crea_blocco = True
            elif 0 <= indice < len(self._blocchi_disponibili):
                blocco = self._blocchi_disponibili[indice]
                errore = None
            else:
                blocco = None
                errore = "Scegli un blocco esistente o creane uno nuovo."
            if errore:
                if mostra_dialogo:
                    QMessageBox.warning(self, "Blocco richiesto", errore)
                return None

        return stato_da_contesto(self._contesto_selezionato), blocco, crea_blocco

    def _firma_pianificazione(self):
        """Crea una chiave per sapere se l'anteprima corrisponde ai campi attuali."""
        blocco = None
        if self._contesto_selezionato == "parte_viaggio":
            indice = self.combo_blocco_contesto.currentIndex()
            blocco = (
                self.input_nuovo_blocco.text()
                if indice == len(self._blocchi_disponibili)
                else self.combo_blocco_contesto.currentText()
            )
        return firma_pianificazione(
            getattr(getattr(self.mappa_widget, "parent_app", None), "current_progetto_id", None),
            self.input_partenza.text(),
            [punto["input"].text() for punto in self.punti_passaggio],
            self.input_destinazione.text(),
            self.combo_profilo.currentText(),
            self.tappa_in_modifica_id,
            self._contesto_selezionato,
            blocco,
        )

    def _valida_pianificazione(self, mostra_dialogo=True):
        """Controlla progetto e luoghi, restituendo i dati nell'ordine della rotta."""
        progetto = getattr(getattr(self.mappa_widget, "parent_app", None), "current_progetto_id", None)
        # Le regole di validazione stanno nel servizio; qui si mostra solo l'errore.
        dati, errore = valida_pianificazione(
            progetto,
            self.input_partenza.text(),
            self.input_destinazione.text(),
            [punto["input"].text() for punto in self.punti_passaggio],
        )
        if errore:
            titolo, messaggio = errore
            if mostra_dialogo:
                QMessageBox.warning(self, titolo, messaggio)
            else:
                self.dettagli_rotta.imposta_stato(messaggio)
            return None
        return dati

    def _avvia_worker_rotta(self, callback, etichetta_pulsante, mostra_dialogo=True):
        """Avvia il calcolo della rotta in background senza bloccare la mappa."""
        dati = self._valida_pianificazione(mostra_dialogo=mostra_dialogo)
        if not dati:
            return False

        progetto, partenza, punti, destinazione = dati
        richiesta = {
            "progetto": progetto,
            "partenza": partenza,
            "punti": punti,
            "destinazione": destinazione,
            "callback": callback,
            "firma": self._firma_pianificazione(),
        }
        self.btn_salva.setEnabled(False)
        self.btn_salva.setText(etichetta_pulsante)
        self.dettagli_rotta.imposta_stato_con_azioni(
            testo_stato_calcolo(),
            [("Annulla", self._annulla_calcolo_rotta)],
        )
        # Il gestore mette in coda la richiesta se un calcolo è ancora in corso,
        # invece di sovrascrivere il riferimento al thread precedente.
        self._gestore_rotta.richiedi(richiesta)
        return True

    def _crea_worker_rotta(self, richiesta):
        """Costruisce il worker di routing per la richiesta ricevuta.

        Callback e firma viaggiano con il worker: servono a chiudere la richiesta
        giusta quando il risultato torna, anche se nel frattempo ne è partita
        un'altra.
        """
        worker = PianificazionePercorsoWorker(
            richiesta["progetto"],
            richiesta["partenza"],
            richiesta["destinazione"],
            self.combo_profilo.currentText(),
            richiesta["punti"],
            tappa_id=self.tappa_in_modifica_id,
            parent=self,
        )
        worker.callback = richiesta["callback"]
        worker.firma = richiesta["firma"]
        return worker

    def _risultato_worker_rotta(self, esito):
        """Consegna alla GUI il risultato del calcolo, se non è stato annullato."""
        if esito.get("annullato"):
            return
        callback = esito.get("callback")
        if callback is None:
            return
        callback(
            esito.get("riuscito", False),
            esito.get("risultato", {}),
            esito.get("errore", ""),
            esito.get("firma"),
        )

    def _annulla_calcolo_rotta(self):
        """Annulla il calcolo in corso e rimette il pulsante in uno stato utile."""
        self._gestore_rotta.invalida()
        self._ripristina_pulsante_salvataggio()
        self.dettagli_rotta.imposta_stato_con_azioni(
            testo_stato_annullato(),
            [("Riprova", self._ricalcola_anteprima)],
        )

    def _ripristina_pulsante_salvataggio(self):
        """Rende il pulsante Salva di nuovo attivo con la dicitura giusta."""
        self.btn_salva.setEnabled(True)
        self.btn_salva.setText(self._testo_pulsante_salvataggio())

    def _worker_pianificazione_terminato(self):
        """Ripristina il pulsante quando il worker di routing termina."""
        self._ripristina_pulsante_salvataggio()

    def _ricalcola_anteprima(self):
        """Ricalcola soltanto l'anteprima, senza scrivere nel database."""
        self._avvia_worker_rotta(
            self._anteprima_rotta_completata,
            "Ricalcolo anteprima...",
            mostra_dialogo=False,
        )

    def _anteprima_rotta_completata(self, riuscito, risultato, errore, firma):
        """Aggiorna anteprima e dettagli dopo il completamento del routing."""
        self.btn_salva.setText(self._testo_pulsante_salvataggio())
        if not riuscito:
            self.dettagli_rotta.imposta_stato_con_azioni(
                testo_stato_errore_routing(errore),
                [("Riprova", self._ricalcola_anteprima)],
            )
            return
        if firma != self._firma_pianificazione():
            self.dettagli_rotta.imposta_stato_con_azioni(
                testo_stato_campi_cambiati(),
                [("Riprova", self._ricalcola_anteprima)],
            )
            return

        self.ultima_anteprima = risultato
        self.firma_ultima_anteprima = firma
        self._aggiorna_dettagli_rotta(risultato.get("statistiche"))
        self.mappa_widget.mostra_anteprima_percorso(risultato["coordinate"])
        statistiche = risultato.get("statistiche") or {}
        distanza_km = statistiche.get("distanza_km")
        self.dettagli_rotta.imposta_stato(
            testo_stato_percorso_lungo(
                distanza_km,
                testo_stato_anteprima_pronta(distanza_km),
            )
        )
        self._aggiorna_anteprima_suddivisione()

    def aggiungi_waypoint(self, latitudine, longitudine):
        """Inserisce nel form un punto ricevuto dalla mappa e aggiorna l'anteprima."""
        indice_vuoto = indice_primo_punto_vuoto([punto["input"].text() for punto in self.punti_passaggio])
        if indice_vuoto is None:
            self._aggiungi_punto_passaggio()
            indice_vuoto = len(self.punti_passaggio) - 1
        self.punti_passaggio[indice_vuoto]["input"].setText(testo_coordinate(latitudine, longitudine))
        self._ricalcola_anteprima()

    def _imposta_sostituzione_percorso(
        self,
        tappe,
        latitudine_waypoint,
        longitudine_waypoint,
        tappa_vicina_id,
    ):
        """Prepara il ricalcolo completo preservando le tappe e le soste correnti."""
        if not tappe:
            return True
        id_tappe_mappa = [tappa["id"] for tappa in tappe]
        if any(id_tappa is None for id_tappa in id_tappe_mappa):
            QMessageBox.warning(
                self,
                "Percorso non aggiornabile",
                "La mappa non contiene l'identificativo di tutte le tappe attive.",
            )
            return False
        try:
            id_tappe_database = [
                riga[0] for riga in carica_tappe_attive(
                    getattr(
                        getattr(self.mappa_widget, "parent_app", None),
                        "current_progetto_id",
                        None,
                    ),
                    DB_NAME,
                )
            ]
        except sqlite3.Error as errore:
            QMessageBox.warning(
                self,
                "Percorso non aggiornabile",
                f"Non è stato possibile verificare le tappe attive: {errore}",
            )
            return False
        if id_tappe_database != id_tappe_mappa:
            QMessageBox.warning(
                self,
                "Mappa non aggiornata",
                "Le tappe mostrate non corrispondono a tutte quelle attive. "
                "Ricarica la mappa e riprova.",
            )
            return False

        self._tappe_ids_da_sostituire = id_tappe_mappa
        self._waypoint_devia_tappa_singola = False
        self.pulsanti_contesto["percorso"].setChecked(True)
        self._imposta_contesto("percorso")
        for controllo in (
            self.radio_km_per_tappa,
            self.radio_giorni_per_tappa,
            self.spin_km_per_tappa,
            self.spin_giorni_per_tappa,
        ):
            controllo.setEnabled(False)

        if tappa_vicina_id not in {tappa["id"] for tappa in tappe}:
            self._azzera_sostituzione_percorso()
            QMessageBox.warning(
                self,
                "Tappa non disponibile",
                "Non è stato possibile determinare l'ordine del waypoint "
                "nel percorso attivo.",
            )
            return False

        coordinate_tappe = [
            [
                punto
                for segmento in tappa["coordinate"]
                for punto in segmento
            ]
            for tappa in tappe
        ]
        self.input_partenza.setText(testo_coordinate(*coordinate_tappe[0][0]))
        self.input_destinazione.setText(testo_coordinate(*coordinate_tappe[-1][-1]))
        punti_intermedi = []
        for indice, (tappa, coordinate) in enumerate(zip(tappe, coordinate_tappe)):
            if tappa["id"] == tappa_vicina_id:
                punti_intermedi.append(
                    testo_coordinate(latitudine_waypoint, longitudine_waypoint)
                )
            if indice < len(tappe) - 1:
                punto_fine = testo_coordinate(*coordinate[-1])
                if not punti_intermedi or punti_intermedi[-1] != punto_fine:
                    punti_intermedi.append(punto_fine)

        while self.punti_passaggio:
            self._rimuovi_punto_passaggio(self.punti_passaggio[-1]["widget"])
        for testo in punti_intermedi:
            self._aggiungi_punto_passaggio()
            self.punti_passaggio[-1]["input"].setText(testo)
        self._ricalcola_anteprima()
        return True

    def _azzera_sostituzione_percorso(self):
        """Riabilita contesto e divisione dopo aver completato la sostituzione."""
        self._tappe_ids_da_sostituire = None
        for pulsante in self.pulsanti_contesto.values():
            pulsante.setEnabled(True)
        for controllo in (
            self.radio_km_per_tappa,
            self.radio_giorni_per_tappa,
            self.spin_km_per_tappa,
            self.spin_giorni_per_tappa,
        ):
            controllo.setEnabled(True)

    def gestisci_waypoint_da_mappa(self, latitudine, longitudine):
        """Classifica il click e devia la tappa più vicina o l'intera rotta."""
        progetto = getattr(
            getattr(self.mappa_widget, "parent_app", None),
            "current_progetto_id",
            None,
        )
        tappe = (
            self.mappa_widget.geometrie_tappe_per_waypoint(progetto)
            if progetto and hasattr(self.mappa_widget, "geometrie_tappe_per_waypoint")
            else None
        )

        if tappe is None:
            if self.ultima_anteprima:
                coordinate = self.ultima_anteprima["coordinate"]
                tappa_id = self.tappa_in_modifica_id
                tappe = (
                    [{"id": tappa_id, "coordinate": coordinate}]
                    if tappa_id is not None
                    else []
                )
            else:
                QMessageBox.information(
                    self,
                    "Mappa in caricamento",
                    "Attendi che il percorso sia caricato sulla mappa, poi riprova.",
                )
                return
        else:
            coordinate = [
                segmento
                for tappa in tappe
                for segmento in tappa["coordinate"]
            ]
            if not coordinate and self.ultima_anteprima:
                coordinate = [self.ultima_anteprima["coordinate"]]
                if self.tappa_in_modifica_id is not None:
                    tappe = [
                        {
                            "id": self.tappa_in_modifica_id,
                            "coordinate": coordinate,
                        }
                    ]

        if not coordinate:
            self.aggiungi_waypoint(latitudine, longitudine)
            return

        try:
            classificazione = classifica_punto(
                coordinate,
                tappe,
                (latitudine, longitudine),
            )
        except ValueError as errore:
            QMessageBox.warning(
                self,
                "Waypoint non classificabile",
                f"Non è stato possibile confrontare il punto con la rotta: {errore}",
            )
            return

        if classificazione["classificazione"] == "gia_sul_percorso":
            QMessageBox.information(
                self,
                "Punto già sulla rotta",
                "Questo punto è già sulla tua rotta: non è stato aggiunto.",
            )
            return

        tappa_id = classificazione["tappa_id"]
        if (
            classificazione["classificazione"] == "vicino_a_tappa"
            and tappa_id is not None
        ):
            numero_tappa = classificazione["tappa_sequenza"] or tappa_id
            dialogo = QMessageBox(self)
            dialogo.setIcon(QMessageBox.Question)
            dialogo.setWindowTitle("Punto vicino a una tappa")
            dialogo.setText(
                f"Il punto è vicino alla tappa {numero_tappa}. "
                "Vuoi deviare solo quella tappa o ricalcolare tutto il percorso?"
            )
            devia_tappa = dialogo.addButton(
                "Devia questa tappa", QMessageBox.AcceptRole
            )
            devia_tutto = dialogo.addButton(
                "Devia tutto il percorso", QMessageBox.DestructiveRole
            )
            dialogo.addButton("Annulla", QMessageBox.RejectRole)
            dialogo.exec()
            if dialogo.clickedButton() is devia_tappa:
                self._azzera_sostituzione_percorso()
                self._waypoint_devia_tappa_singola = True
                self.prepara_modifica_tappa(tappa_id, latitudine, longitudine)
            elif dialogo.clickedButton() is devia_tutto:
                if tappe:
                    self._imposta_sostituzione_percorso(
                        tappe, latitudine, longitudine, tappa_id
                    )
                else:
                    self.aggiungi_waypoint(latitudine, longitudine)
            return

        dialogo = QMessageBox(self)
        dialogo.setIcon(QMessageBox.Question)
        dialogo.setWindowTitle("Deviazione dell'intero percorso")
        dialogo.setText(
            "Questo punto è lontano dalla rotta: per raggiungerlo "
            "è necessario ricalcolare tutto il percorso."
        )
        ricalcola = dialogo.addButton(
            "Ricalcola tutto", QMessageBox.AcceptRole
        )
        dialogo.addButton("Annulla", QMessageBox.RejectRole)
        dialogo.exec()
        if dialogo.clickedButton() is ricalcola:
            if tappe:
                self._imposta_sostituzione_percorso(
                    tappe,
                    latitudine,
                    longitudine,
                    classificazione["tappa_id"],
                )
            else:
                self.aggiungi_waypoint(latitudine, longitudine)

    def prepara_modifica_tappa(self, tappa_id, latitudine, longitudine):
        """Carica gli estremi della tappa esistente e crea una bozza rubber-band."""
        finestra_principale = getattr(self.mappa_widget, "parent_app", None)
        progetto = getattr(finestra_principale, "current_progetto_id", None)
        try:
            coordinate = carica_coordinate_tappa(
                tappa_id, progetto, DB_NAME, directory_gpx=GPX_DIR
            )

            testo_partenza, testo_destinazione = estremi_tappa(coordinate)
            self.input_partenza.setText(testo_partenza)
            self.input_destinazione.setText(testo_destinazione)
            while self.punti_passaggio:
                self._rimuovi_punto_passaggio(self.punti_passaggio[-1]["widget"])
            self.tappa_in_modifica_id = tappa_id
            self.btn_salva.setText(self._testo_pulsante_salvataggio())
            self.aggiungi_waypoint(latitudine, longitudine)
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
            if self._tappe_ids_da_sostituire is not None:
                self._azzera_sostituzione_percorso()
            self._waypoint_devia_tappa_singola = False
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
                self.dettagli_rotta.reset()
                # Invalida eventuali analisi/geocodifiche del percorso precedente
                # ancora in corso in background: senza questo, un risultato
                # tardivo potrebbe ripopolare i campi appena svuotati.
                self._gestore_superfici.invalida()
                self._gestore_nomi.invalida()
                self._gestore_altimetria.invalida()
                # Chiediamo anche ai worker eventualmente ancora in esecuzione
                # di fermarsi subito invece di continuare a girare a vuoto in
                # sottofondo: senza questo, un'analisi pesante su un percorso
                # enorme restava attiva anche dopo essere diventata inutile,
                # e la richiesta per il nuovo percorso doveva aspettare in
                # coda che finisse, rallentando ogni cambio successivo.




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
        tappe_intermedie, richieste_tappe = prepara_tappe_intermedie(tappe)
        richieste_nomi.extend(richieste_tappe)
        self._popola_tappe_intermedie(tappe_intermedie)

        if richieste_nomi:
            self._avvia_risoluzione_nomi_luoghi(richieste_nomi)

        self.dettagli_rotta.imposta_distanza_tappe(tappe)

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
        self.adatta_altezza()

    def _avvia_risoluzione_nomi_luoghi(self, richieste):
        """
        Risolve in un thread separato il nome del luogo più vicino (offline,
        dalle mappe locali) per partenza/arrivo/tappe intermedie, così
        l'interfaccia non si blocca nemmeno con percorsi molto lunghi.
        Finché il nome non è pronto restano visibili le coordinate.
        """
        self._gestore_nomi.richiedi(richieste)

    def _fine_risoluzione_nomi_luoghi(self, risultati):
        """Scrive i nomi trovati; il gestore li consegna solo se il risultato è ancora attuale."""
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
        self.dettagli_rotta.imposta_stato(
            "Analisi offline delle superfici in corso (mappe locali già scaricate)..."
        )
        # Se un'analisi è già in corso il gestore mette la richiesta in coda e ferma la vecchia.
        self._gestore_superfici.richiedi(id_progetto)

    def _fine_analisi_superfici_offline(self, risultato):
        """Mostra le superfici; il gestore le consegna solo se il risultato è ancora attuale."""
        if not self.dettagli_rotta.imposta_superfici_offline(risultato):
            return

        self.adatta_altezza()

    def _avvia_analisi_altimetria(self, nomi_file):
        """
        Calcola in un thread separato altitudine massima/minima leggendo i
        file GPX del percorso: farlo sul thread dell'interfaccia bloccava
        l'intera app (anche a lungo, con percorsi di centinaia di tappe).
        """
        self._gestore_altimetria.richiedi(nomi_file)

    def _fine_analisi_altimetria(self, risultato):
        """Mostra l'altimetria; il gestore la consegna solo se il risultato è ancora attuale."""
        self.dettagli_rotta.imposta_altimetria(
            risultato.get("massima"), risultato.get("minima")
        )

    def showEvent(self, event):
        """Ricalcola l'altezza del pannello quando viene mostrato."""
        super().showEvent(event)
        QTimer.singleShot(0, self.adatta_altezza)

    def adatta_altezza(self):
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

    def imposta_stato(self, testo):
        """Aggiorna il messaggio del pannello dettagli, anche per le interazioni mappa."""
        self.dettagli_rotta.imposta_stato(testo)

    def _aggiungi_punto_passaggio(self):
        """Aggiunge un campo intermedio prima della destinazione."""
        indice = len(self.punti_passaggio)
        etichetta = etichetta_punto(indice)
        riga = QWidget(self.contenitore_punti_passaggio)
        riga_layout = QHBoxLayout(riga)
        riga_layout.setContentsMargins(0, 0, 0, 0)
        riga_layout.setSpacing(8)

        lbl_punto = QLabel(etichetta)
        lbl_punto.setFixedWidth(20)
        lbl_punto.setAlignment(Qt.AlignCenter)
        lbl_punto.setStyleSheet("color: #38bdf8; font-weight: bold;")

        campo = QLineEdit()
        campo.setPlaceholderText(testo_segnaposto_punto(etichetta))

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
        QTimer.singleShot(0, self.adatta_altezza)

    def _rimuovi_punto_passaggio(self, riga):
        """Rimuove il campo selezionato e aggiorna le etichette successive."""
        self.punti_passaggio = [
            punto for punto in self.punti_passaggio if punto["widget"] is not riga
        ]
        self.layout_punti_passaggio.removeWidget(riga)
        riga.deleteLater()
        self._rinumera_punti_passaggio()
        QTimer.singleShot(0, self.adatta_altezza)

    def _rinumera_punti_passaggio(self):
        """Riassegna le lettere A, B, ..., Z, AA, AB ai punti visibili."""
        for indice, punto in enumerate(self.punti_passaggio):
            etichetta = etichetta_punto(indice)
            punto["label"].setText(etichetta)
            punto["input"].setPlaceholderText(testo_segnaposto_punto(etichetta))

    def _toggle_elenco_tappe_intermedie(self):
        """Apre/chiude l'elenco a scorrimento delle tappe intermedie del percorso caricato."""
        aperto = self.btn_toggle_tappe_intermedie.isChecked()
        self.area_scorrimento_tappe_intermedie.setVisible(aperto)
        numero = len(self._dati_tappe_intermedie)
        self.btn_toggle_tappe_intermedie.setText(testo_intestazione_tappe_intermedie(numero, aperto))
        QTimer.singleShot(0, self.adatta_altezza)

    def _costruisci_riga_tappa_intermedia(self, indice, tappa_id, testo):
        """Crea una riga cliccabile dell'elenco: il click evidenzia la tappa sulla mappa."""
        riga = QPushButton(testo_riga_tappa_intermedia(indice, testo))
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
            QTimer.singleShot(0, self.adatta_altezza)
            return

        for indice, tappa in enumerate(self._dati_tappe_intermedie):
            riga = self._costruisci_riga_tappa_intermedia(indice, tappa["id"], tappa["testo"])
            self.layout_lista_tappe_intermedie.addWidget(riga)

        aperto = self.btn_toggle_tappe_intermedie.isChecked()
        self.btn_toggle_tappe_intermedie.setText(testo_intestazione_tappe_intermedie(numero, aperto))
        self.area_scorrimento_tappe_intermedie.setVisible(aperto)
        QTimer.singleShot(0, self.adatta_altezza)

    def _aggiorna_testo_tappe_intermedie(self, testi_per_id):
        """Aggiorna solo il testo (es. nome del luogo appena risolto) senza ricostruire le righe."""
        # La logica dei testi sta nel servizio; qui si aggiornano solo i widget cambiati.
        for indice in aggiorna_testi_tappe(self._dati_tappe_intermedie, testi_per_id):
            elemento = self.layout_lista_tappe_intermedie.itemAt(indice)
            widget = elemento.widget() if elemento else None
            if widget:
                widget.setText(testo_riga_tappa_intermedia(indice, self._dati_tappe_intermedie[indice]["testo"]))

    def _aggiorna_dettagli_rotta(self, statistiche):
        """Aggiorna il widget dedicato e ricalcola l'altezza complessiva del pannello."""
        self.dettagli_rotta.imposta_dettagli_rotta(statistiche)
        self.adatta_altezza()

    def _evidenzia_tappa_su_mappa(self, tappa_id):
        """Evidenzia o deseleziona una tappa e centra il relativo tratto."""
        if self.mappa_widget:
            self.mappa_widget.evidenzia_tappa(tappa_id)

    def _gestisci_salvataggio_percorso(self):
        """Salva l'anteprima corrente oppure calcola la rotta prima di salvarla."""
        if self._dati_contesto_salvataggio() is None:
            return
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
        self.btn_salva.setText(self._testo_pulsante_salvataggio())

        if not riuscito:
            # L'errore va nella riga di stato con la sua azione Riprova: un
            # MessageBox interrompe il lavoro e non dice come proseguire.
            self.dettagli_rotta.imposta_stato_con_azioni(
                testo_stato_errore_routing(errore),
                [("Riprova", self._gestisci_salvataggio_percorso)],
            )
            return
        if firma is not None and firma != self._firma_pianificazione():
            self.dettagli_rotta.imposta_stato_con_azioni(
                testo_stato_campi_cambiati(),
                [("Riprova", self._ricalcola_anteprima)],
            )
            return

        dati_contesto = self._dati_contesto_salvataggio()
        if dati_contesto is None:
            return
        stato_contesto, blocco_contesto, crea_blocco = dati_contesto

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

        suddivisione = None
        sostituzione_percorso = self._tappe_ids_da_sostituire is not None
        if not self._waypoint_devia_tappa_singola and (
            sostituzione_percorso or self._contesto_selezionato == "percorso"
        ):
            self._aggiorna_anteprima_suddivisione()
            suddivisione = self._suddivisione_anteprima
            if suddivisione is None:
                QMessageBox.warning(
                    self,
                    "Suddivisione non disponibile",
                    self.lbl_anteprima_suddivisione.text(),
                )
                return
            riepilogo = ", ".join(
                f"{km:g} km" for km in suddivisione["distanze_km"]
            )
            testo_conferma = (
                f"Sostituirai tutte le {len(self._tappe_ids_da_sostituire)} "
                "tappe attive, mantenendo ID, ordine e blocchi."
                if sostituzione_percorso
                else "Procedere?"
            )
            conferma = QMessageBox.question(
                self,
                (
                    "Conferma deviazione completa"
                    if sostituzione_percorso
                    else "Conferma suddivisione"
                ),
                f"Salverai {suddivisione['numero_tappe']} tappe "
                f"({distanza_km:.1f} km): {riepilogo}.\n\n{testo_conferma}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if conferma != QMessageBox.Yes:
                return

        # Il file GPX appena scritto serve a ripulire se un passo successivo della GUI fallisce.
        stato_salvataggio = {}
        salvataggio_database_completato = False
        try:
            if suddivisione is not None:
                tappe_da_salvare = []
                coordinate_per_tappa = suddivisione["tappe"]
                distanze_per_tappa = suddivisione["distanze_km"]
                for coordinate_tappa, distanza_tappa in zip(
                    coordinate_per_tappa, distanze_per_tappa
                ):
                    tappe_da_salvare.append(
                        {
                            "coordinate": coordinate_tappa,
                            "distanza_km": distanza_tappa,
                        }
                    )
                esito = salva_percorso_suddiviso(
                    id_progetto_corrente,
                    tappe_da_salvare,
                    partenza,
                    destinazione,
                    tappa_id=risultato.get("tappa_id"),
                    db_name=DB_NAME,
                    directory_gpx=GPX_DIR,
                    esito=stato_salvataggio,
                    tappe_ids_da_sostituire=self._tappe_ids_da_sostituire,
                )
            else:
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
                    stato=stato_contesto,
                    blocco=blocco_contesto,
                    crea_blocco=crea_blocco,
                )
            salvataggio_database_completato = True
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
            self._azzera_sostituzione_percorso()
            self._waypoint_devia_tappa_singola = False
            self.ultima_anteprima = None
            self.firma_ultima_anteprima = None
            self.btn_salva.setText(self._testo_pulsante_salvataggio())
            self.mappa_widget.rigenera_mappa(
                id_progetto_corrente,
                DB_NAME,
                force=True,
                adatta_visuale=False,
            )
            if suddivisione is not None:
                self.mappa_widget.cancella_anteprima_percorso()

            messaggi_salvataggio = {
                "tappa_unica": ("Tappa salvata", "La tappa è stata salvata."),
                "percorso": (
                    "Percorso suddiviso e salvato",
                    f"Il percorso è stato suddiviso in {esito['numero_tappe']} tappe.",
                ),
                "parte_viaggio": (
                    "Tappa aggiunta al blocco",
                    f"La tappa è stata aggiunta al blocco «{blocco_contesto}».",
                ),
                "test": (
                    "Bozza tecnica salvata",
                    "La traccia è stata salvata come bozza e non è inclusa nei calcoli.",
                ),
            }
            titolo, messaggio = messaggi_salvataggio[self._contesto_selezionato]
            if esito.get("sostituito_percorso"):
                messaggio = (
                    f"Tutte le {esito['numero_tappe']} tappe attive sono state "
                    "aggiornate mantenendo ordine e blocchi."
                )
            elif tappa_in_aggiornamento:
                messaggio = "La tappa è stata aggiornata. " + messaggio
            QMessageBox.information(
                self,
                titolo,
                f"{messaggio} Distanza: {distanza_km:.1f} km.",
            )
            if not precalcolo_riuscito and not esito.get("precalcolo_saltato"):
                QMessageBox.warning(
                    self,
                    "Precalcolo non completato",
                    "La rotta è stata salvata, ma il precalcolo delle metriche "
                    f"non è riuscito: {errore_precalcolo}. "
                    "Il GPX precedente è stato conservato.",
                )
        except Exception as errore_salvataggio:
            if not salvataggio_database_completato:
                rimuovi_gpx_se_esiste(stato_salvataggio.get("file_gpx"))
            QMessageBox.critical(
                self,
                "Errore di salvataggio",
                (
                    "Il percorso è stato salvato, ma non è stato possibile aggiornare "
                    f"tutti i pannelli: {errore_salvataggio}"
                    if salvataggio_database_completato
                    else f"Il percorso non è stato salvato nel database: {errore_salvataggio}"
                ),
            )

    def _testo_pulsante_salvataggio(self):
        """Restituisce la dicitura coerente con contesto e modalità di modifica."""
        if self._tappe_ids_da_sostituire is not None:
            return "Aggiorna percorso"
        if self.tappa_in_modifica_id:
            return "Aggiorna tappa"
        etichette = {
            "tappa_unica": "Salva tappa",
            "percorso": "Salva percorso",
            "parte_viaggio": "Salva nel blocco",
            "test": "Salva bozza",
        }
        return etichette.get(self._contesto_selezionato, "Salva Percorso")
