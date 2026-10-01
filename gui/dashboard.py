import os
import sqlite3
import gpxpy
import shutil
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem, 
    QTableWidget, QTableWidgetItem, QHeaderView, 
    QComboBox, QMessageBox, QInputDialog, QStackedWidget, QLineEdit
)
from PySide6.QtCore import Qt, Signal as pyqtSignal
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from service.config import DB_NAME
from service.precalcolo_service import precalcola_tappa
try:
    from service.config import calcola_distanza_haversine
except ImportError:
    def calcola_distanza_haversine(lat1, lon1, lat2, lon2):
        from math import radians, sin, cos, sqrt, atan2
        R = 6371.0
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
        return R * (2 * atan2(sqrt(a), sqrt(1 - a)))

class DashboardPage(QWidget):
    """
    Modulo GUI per la Dashboard (Pagina 1):
    Gestisce la Lobby dei percorsi e la Vista Dettaglio con la gestione tappe/GPX.
    """
    # Definiamo il segnale che trasporta l'ID del progetto e il suo nome
    progetto_selezionato_signal = pyqtSignal(int, str)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_progetto_id = None
        self.init_ui()
        self.carica_lista_percorsi()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)

        self.stack_archivio = QStackedWidget()
        
        # ==========================================
        # VISTA 0: LOBBY (Elenco Percorsi)
        # ==========================================
        self.vista_lobby = QWidget()
        lobby_layout = QVBoxLayout(self.vista_lobby)
        
        top_lobby = QHBoxLayout()
        
        # 1. Titolo di sinistra (I Tuoi Percorsi Salvati)
        lbl_lobby_titolo = QLabel("🗂️ I Tuoi Percorsi Salvati")
        lbl_lobby_titolo.setFont(QFont("Arial", 16, QFont.Bold))
        lbl_lobby_titolo.setStyleSheet("color: #0e639c;")
        
        # 2. Titolo centrale dell'applicazione nello spazio vuoto
        lbl_app_titolo = QLabel("🚴 Bikepacking Studio")
        lbl_app_titolo.setFont(QFont("Arial", 14, QFont.Bold))
        lbl_app_titolo.setStyleSheet("color: #858585;")
        
        # 3. Pulsante di destra (Crea Nuovo Percorso)
        btn_crea_nuovo = QPushButton("➕ Crea Nuovo Percorso")
        btn_crea_nuovo.setFont(QFont("Arial", 10, QFont.Bold))
        btn_crea_nuovo.setStyleSheet("background-color: #28a745; color: white; padding: 10px 15px; border-radius: 5px;")
        btn_crea_nuovo.clicked.connect(self.crea_nuovo_progetto_dialog)

        # Assemblaggio del layout orizzontale con doppi stretch per centrare la scritta
        top_lobby.addWidget(lbl_lobby_titolo)
        top_lobby.addStretch()
        top_lobby.addWidget(lbl_app_titolo)
        top_lobby.addStretch()
        top_lobby.addWidget(btn_crea_nuovo)
        
        lobby_layout.addLayout(top_lobby)

        # La lista dei percorsi (dove prima c'era l'AttributeError)
        self.list_percorsi = QListWidget()
        self.list_percorsi.setStyleSheet("""
            QListWidget { background-color: #252526; border: 1px solid #3e3e42; border-radius: 8px; padding: 10px; }
            QListWidget::item { background-color: #2d2d30; color: white; margin-bottom: 8px; padding: 15px; border-radius: 6px; }
            QListWidget::item:hover { background-color: #3e3e42; }
        """)
        self.list_percorsi.itemDoubleClicked.connect(self.apri_percorso_selezionato)
        lobby_layout.addWidget(self.list_percorsi)

        btn_apri_selezionato = QPushButton("📂 Apri Percorso Selezionato")
        # CORRETTO:
        btn_apri_selezionato.setStyleSheet("background-color: #0e639c; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")        
        btn_apri_selezionato.clicked.connect(lambda: self.apri_percorso_selezionato(self.list_percorsi.currentItem()))
        lobby_layout.addWidget(btn_apri_selezionato)
                
        # ==========================================
        # VISTA 1: DETTAGLIO PERCORSO & IMPORT GPX
        # ==========================================
        self.vista_dettaglio = QWidget()
        dettaglio_layout = QVBoxLayout(self.vista_dettaglio)

        top_dettaglio = QHBoxLayout()
        btn_back = QPushButton("⬅️ Torna ai Percorsi")
        btn_back.setStyleSheet("background-color: #3e3e42; color: white; padding: 8px 12px; border-radius: 4px; font-weight: bold;")
        
        # MODIFICA QUI: Quando clicchi, torna alla lista, azzera il progetto attivo e ripulisce la mappa
        btn_back.clicked.connect(lambda: (
            self.stack_archivio.setCurrentIndex(0),
            setattr(self.window(), 'current_progetto_id', None),
            self.window().page_mappa.rigenera_mappa(None, DB_NAME, force=True)
            if hasattr(self.window(), 'page_mappa') else None
        ))

        self.lbl_nome_percorso_attivo = QLabel("Percorso: Non Selezionato")
        self.lbl_nome_percorso_attivo.setFont(QFont("Arial", 14, QFont.Bold))
        self.lbl_nome_percorso_attivo.setStyleSheet("color: #28a745;")

        lbl_profilo = QLabel(" 🚲 Profilo Bici:")
        lbl_profilo.setStyleSheet("color: #aaaaaa; font-weight: bold;")
        
        self.combo_profilo_bici = QComboBox()
        self.combo_profilo_bici.addItems(["Gravel / Bici da Viaggio", "Bici da Strada", "Mountain Bike (MTB)", "E-Bike Tourer"])
        self.combo_profilo_bici.setStyleSheet("background-color: #3e3e42; color: white; padding: 5px; border-radius: 4px;")

        btn_elimina_progetto = QPushButton("🗑️ Elimina Percorso")
        btn_elimina_progetto.setStyleSheet("background-color: #a93226; color: white; padding: 8px 12px; border-radius: 4px; font-weight: bold;")
        btn_elimina_progetto.clicked.connect(self.elimina_percorso_corrente)

        top_dettaglio.addWidget(btn_back)
        top_dettaglio.addSpacing(10)
        top_dettaglio.addWidget(self.lbl_nome_percorso_attivo)
        top_dettaglio.addSpacing(15)
        top_dettaglio.addWidget(lbl_profilo)
        top_dettaglio.addWidget(self.combo_profilo_bici)
        top_dettaglio.addStretch()
        top_dettaglio.addWidget(btn_elimina_progetto)
        dettaglio_layout.addLayout(top_dettaglio)

        dettaglio_layout.addSpacing(10)

        top_bar = QHBoxLayout()
        
        btn_modifica_multipla = QPushButton("✏️ Modifica Blocco Selezionati")
        btn_modifica_multipla.setFont(QFont("Arial", 10, QFont.Bold))
        btn_modifica_multipla.setStyleSheet("QPushButton { background-color: #d97706; color: white; padding: 10px 15px; border: none; border-radius: 6px; } QPushButton:hover { background-color: #b45309; }")
        btn_modifica_multipla.clicked.connect(self.modifica_blocco_multiplo)
        
        btn_sfoglia = QPushButton("📁 Importa File GPX")
        btn_sfoglia.setFont(QFont("Arial", 10, QFont.Bold))
        btn_sfoglia.setStyleSheet("QPushButton { background-color: #0e639c; color: white; padding: 15px 20px; border: none; border-radius: 6px; } QPushButton:hover { background-color: #1177bb; }")
        btn_sfoglia.clicked.connect(self.chiama_selettore_gpx)

        # AGGIUNTI ALLA BARRA ORIZZONTALE
        top_bar.addWidget(btn_modifica_multipla)
        top_bar.addStretch()
        top_bar.addWidget(btn_sfoglia)
        dettaglio_layout.addLayout(top_bar)

        dettaglio_layout.addSpacing(15)

        self.table_tappe = QTableWidget()
        self.table_tappe.setColumnCount(7)
        self.table_tappe.setHorizontalHeaderLabels(["Seq", "Blocco / Area", "Traccia GPX", "Km", "Ruolo / Tipo", "Stato", "Azioni"])
        self.table_tappe.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # ABILITA LA SELEZIONE MULTIPLA DELLE RIGHE
        self.table_tappe.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_tappe.setSelectionMode(QTableWidget.ExtendedSelection)

        self.table_tappe.setStyleSheet("""
            QTableWidget { background-color: #252526; gridline-color: #3e3e42; color: #ffffff; border: 1px solid #3e3e42; border-radius: 5px; }
            QHeaderView::section { background-color: #2d2d30; color: #0e639c; font-weight: bold; padding: 6px; }
        """)
        dettaglio_layout.addWidget(self.table_tappe)

        self.stack_archivio.addWidget(self.vista_lobby)
        self.stack_archivio.addWidget(self.vista_dettaglio)
        
        layout.addWidget(self.stack_archivio)
    
    
        # ==========================================
        # GESTIONE DATI E TABELLA TAPPE
        # ==========================================

    def aggiorna_tabella_tappe(self):
        """Carica le tappe associate al progetto e popola la tabella con widget interattivi."""
        if not self.current_progetto_id:
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sequenza, blocco, nome_file, distanza_km, stato, id 
            FROM tappe 
            WHERE id_progetto = ? AND nome_file IS NOT NULL AND sequenza IS NOT NULL 
            ORDER BY sequenza ASC
        """, (self.current_progetto_id,))
        rows = cursor.fetchall()
        conn.close()

        self.table_tappe.setRowCount(len(rows))
        for row_idx, data in enumerate(rows):
            seq_val, blocco_val, nome_file_val, km_val, stato_val, tappa_id = data

            blocco_val = str(blocco_val) if blocco_val else "Generale"
            nome_file_val = str(nome_file_val) if nome_file_val else ""
            stato_val = str(stato_val) if stato_val else "ATTIVA"

            # 1. Colonna Seq
            item_seq = QTableWidgetItem(str(seq_val))
            item_seq.setTextAlignment(Qt.AlignCenter)
            self.table_tappe.setItem(row_idx, 0, item_seq)

            # 2. Colonna Blocco / Area (QLineEdit protetto)
            txt_blocco = QLineEdit(blocco_val)
            txt_blocco.setStyleSheet("background-color: #3e3e42; color: white; border-radius: 3px; padding: 3px;")
            txt_blocco.editingFinished.connect(lambda t_id=tappa_id, w=txt_blocco: self.aggiorna_blocco_tappa(t_id, w.text()))
            self.table_tappe.setCellWidget(row_idx, 1, txt_blocco)

            # 3. Colonna Traccia GPX
            item_nome = QTableWidgetItem(nome_file_val)
            self.table_tappe.setItem(row_idx, 2, item_nome)

            # 4. Colonna Km
            item_km = QTableWidgetItem(f"{km_val:.1f} km" if km_val is not None else "-")
            item_km.setTextAlignment(Qt.AlignCenter)
            self.table_tappe.setItem(row_idx, 3, item_km)

            # 5. Colonna Ruolo / Tipo (ComboBox)
            combo_ruolo = QComboBox()
            combo_ruolo.addItems(["Traccia Principale (ATTIVA)", "Variante Opzionale (VARIANTE)", "Sospesa / Pausa (SOSPESA)"])
            
            if stato_val == 'ATTIVA':
                combo_ruolo.setCurrentIndex(0)
            elif stato_val == 'VARIANTE':
                combo_ruolo.setCurrentIndex(1)
            else:
                combo_ruolo.setCurrentIndex(2)

            combo_ruolo.currentIndexChanged.connect(lambda idx, t_id=tappa_id: self.cambia_ruolo_tappa(t_id, idx))
            self.table_tappe.setCellWidget(row_idx, 4, combo_ruolo)

            # 6. Colonna Stato testuale
            item_stato = QTableWidgetItem(stato_val)
            item_stato.setTextAlignment(Qt.AlignCenter)
            self.table_tappe.setItem(row_idx, 5, item_stato)

            # 7. Colonna Azioni (Pulsanti Pausa ed Elimina)
            panel = QWidget()
            layout_btns = QHBoxLayout(panel)
            layout_btns.setContentsMargins(2, 2, 2, 2)
            layout_btns.setSpacing(4)

            is_pausa = (stato_val == 'SOSPESA')
            btn_pausa = QPushButton("▶️ Attiva" if is_pausa else "⏸️ Pausa")
            btn_pausa.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold; font-size: 11px;")
            btn_pausa.clicked.connect(lambda _, t_id=tappa_id, p=is_pausa: self.toggle_pausa_tappa(t_id, p))

            btn_elimina = QPushButton("❌ Elimina")
            btn_elimina.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; font-size: 11px;")
            btn_elimina.clicked.connect(lambda _, t_id=tappa_id, nf=nome_file_val: self.elimina_singola_tappa(t_id, nf))

            layout_btns.addWidget(btn_pausa)
            layout_btns.addWidget(btn_elimina)
            self.table_tappe.setCellWidget(row_idx, 6, panel)

    def carica_tappe_progetto(self, id_progetto):
        """Alias di compatibilità"""
        self.aggiorna_tabella_tappe()
        
    def elabora_files_gpx(self, filepaths):
        print(f"DEBUG - Progetto ID attivo: {self.current_progetto_id}")
        print(f"DEBUG - File selezionati: {filepaths}")
        """Elabora i file GPX selezionati, evita i duplicati e aggiorna la tabella immediatamente."""
        if not self.current_progetto_id:
            QMessageBox.warning(self, "Attenzione", "Apri prima un percorso salvato per aggiungere tappe!")
            return
        
        file_list = sorted(filepaths, key=lambda x: os.path.basename(x).upper())
        
        cartella_gpx = os.path.join(os.getcwd(), "gpx")
        if not os.path.exists(cartella_gpx):
            os.makedirs(cartella_gpx)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        tappe_da_precalcolare = []

        # Controllo file già presenti per evitare duplicati
        cursor.execute("SELECT nome_file FROM tappe WHERE id_progetto = ?", (self.current_progetto_id,))
        file_esistenti = {row[0] for row in cursor.fetchall()}

        cursor.execute("SELECT MAX(sequenza) FROM tappe WHERE id_progetto = ?", (self.current_progetto_id,))
        max_seq = cursor.fetchone()[0]
        seq_attuale = (max_seq if max_seq is not None else 0) + 1

        for path in file_list:
            nome_file = os.path.basename(path)
            
            if nome_file in file_esistenti:
                continue

            destinazione = os.path.join(cartella_gpx, nome_file)
            try:
                shutil.copy2(path, destinazione)
            except Exception as e:
                print(f"Errore copia {nome_file}: {e}")
                continue

            blocco_rilevato = "Generale"

            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    gpx = gpxpy.parse(f)
                    pts = []
                    for t in gpx.tracks:
                        for s in t.segments:
                            for p in s.points:
                                pts.append((p.latitude, p.longitude))

                    if pts:
                        s_lat, s_lon = pts[0]
                        e_lat, e_lon = pts[-1]
                        
                        # Calcolo distanza
                        dist_km = sum(calcola_distanza_haversine(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1]) for i in range(len(pts)-1))
                        
                        cursor.execute('''
                            INSERT INTO tappe (id_progetto, sequenza, blocco, nome_file, start_lat, start_lon, end_lat, end_lon, distanza_km, stato)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'ATTIVA')
                        ''', (self.current_progetto_id, seq_attuale, blocco_rilevato, nome_file, s_lat, s_lon, e_lat, e_lon, round(dist_km, 2)))
                        tappe_da_precalcolare.append(
                            (cursor.lastrowid, destinazione)
                        )
                        seq_attuale += 1
            except Exception as e:
                print(f"Errore lettura GPX {nome_file}: {e}")

        conn.commit()

        # Riordinamento sequenziale in base al nome file
        cursor.execute("""
            SELECT id FROM tappe 
            WHERE id_progetto = ? AND nome_file IS NOT NULL 
            ORDER BY nome_file ASC
        """, (self.current_progetto_id,))
        tappe_ordinate = cursor.fetchall()

        for nuova_seq, (t_id,) in enumerate(tappe_ordinate, start=1):
            cursor.execute("UPDATE tappe SET sequenza = ? WHERE id = ?", (nuova_seq, t_id))

        conn.commit()
        conn.close()

        for tappa_id, percorso_gpx in tappe_da_precalcolare:
            try:
                precalcola_tappa(tappa_id, percorso_gpx, DB_NAME)
            except Exception as e:
                print(f"Errore precalcolo tappa {tappa_id}: {e}")

        # Aggiornamento immediato della vista
        self.aggiorna_tabella_tappe()
        self.carica_lista_percorsi()
        if hasattr(self.main_window, 'esegui_audit_automatico'):
            self.main_window.esegui_audit_automatico()
        if hasattr(self.main_window, 'aggiorna_tabella_allarmi'):
            self.main_window.aggiorna_tabella_allarmi()

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

        self.aggiorna_tabella_tappe()

    def cambia_ruolo_tappa(self, tappa_id, index):
        mappa_stati = {0: 'ATTIVA', 1: 'VARIANTE', 2: 'SOSPESA'}
        nuovo_stato = mappa_stati[index]

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE tappe SET stato = ? WHERE id = ?", (nuovo_stato, tappa_id))
        conn.commit()
        conn.close()

        self.aggiorna_tabella_tappe()

    def elimina_singola_tappa(self, tappa_id, nome_file=None):
        reply = QMessageBox.question(self, "Conferma", "Vuoi rimuovere questa traccia dal percorso?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tappe WHERE id = ?", (tappa_id,))
                conn.commit()
                conn.close()

                if nome_file:
                    filepath = os.path.join(os.getcwd(), "gpx", os.path.basename(nome_file))
                    if os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                        except Exception as e:
                            print("Errore rimozione file fisico:", e)

                if self.current_progetto_id:
                    self.aggiorna_tabella_tappe()
                    self.carica_lista_percorsi()
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile eliminare la traccia: {e}")

    def carica_lista_percorsi(self):
        self.list_percorsi.clear()
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome_progetto, data_creazione, stato FROM progetti ORDER BY data_creazione DESC")

            rows = cursor.fetchall()

            for row in rows:
                id_prog, nome, data, stato = row
                cursor.execute("SELECT SUM(distanza_km) FROM tappe WHERE id_progetto = ?", (id_prog,))
                res_km = cursor.fetchone()
                km_totali = res_km[0] if res_km and res_km[0] is not None else 0.0

                item_text = f"📍 {nome}   |   Creato il: {data}   |   KM: {km_totali:.1f}   |   Stato: {stato}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, id_prog)
                self.list_percorsi.addItem(item)

            conn.close()
        except Exception as e:
            print(f"Errore caricamento percorsi: {e}")

    def crea_nuovo_progetto_dialog(self):
        """
        Apre un dialog modale (WizardNuovoPercorsoDialog) per la creazione guidata 
        di un nuovo itinerario. Gestisce sia la scelta di disegnare da zero sulla mappa 
        sia l'importazione di file GPX esterni.
        """
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QFormLayout
        
        class WizardNuovoPercorsoDialog(QDialog):
            """Dialog interno per la raccolta dei metadati iniziali del percorso."""
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Pianificatore Nuovo Percorso - Bikepacking Studio")
                self.setMinimumWidth(500)
                self.setStyleSheet("background-color: #1e1e1e; color: white;")
                self.risultato_dati = None  # Dizionario che conterrà le scelte dell'utente
                self.init_ui()

            def init_ui(self):
                """Inizializza e dispone tutti gli elementi grafici del wizard."""
                layout = QVBoxLayout(self)
                
                # Titolo descrittivo in cima al wizard
                lbl_titolo = QLabel("✨ Crea Nuovo Itinerario Interattivo")
                lbl_titolo.setFont(QFont("Arial", 14, QFont.Bold))
                lbl_titolo.setStyleSheet("color: #28a745; margin-bottom: 10px;")
                layout.addWidget(lbl_titolo)

                form_layout = QFormLayout()
                
                # --- IL BIVIO: Scelta della modalità di creazione ---
                self.combo_modalita = QComboBox()
                self.combo_modalita.addItems([
                    "🗺️ Disegna da zero sulla Mappa (Nuovo Percorso)", 
                    "📂 Importa file GPX esistenti (Tracce Esterne)"
                ])
                self.combo_modalita.setStyleSheet("background-color: #2d2d30; color: #4EC9B0; padding: 8px; border: 1px solid #569CD6; border-radius: 4px; font-weight: bold;")
                form_layout.addRow(QLabel("<b>Metodo di Creazione:</b>"), self.combo_modalita)
                # ----------------------------------------------------

                # Input testuale per il nome del percorso
                self.input_nome = QLineEdit()
                self.input_nome.setPlaceholderText("Es. Avventura in Gravel sui Monti")
                self.input_nome.setStyleSheet("background-color: #2d2d30; color: white; padding: 8px; border: 1px solid #3e3e42; border-radius: 4px;")
                form_layout.addRow(QLabel("<b>Nome Percorso:</b>"), self.input_nome)

                # Selezione del profilo della bicicletta (influenza l'instradamento)
                self.combo_bici = QComboBox()
                self.combo_bici.addItems([
                    "Gravel / Bici da Viaggio", 
                    "Bici da Strada (Asfalto)", 
                    "Mountain Bike (Sterrato / Trail)", 
                    "E-Bike Tourer"
                ])
                self.combo_bici.setStyleSheet("background-color: #2d2d30; color: white; padding: 8px; border: 1px solid #3e3e42; border-radius: 4px;")
                form_layout.addRow(QLabel("<b>Profilo Bici:</b>"), self.combo_bici)

                # Preferenze sulle tipologie di strada da privilegiare o evitare
                self.combo_strada = QComboBox()
                self.combo_strada.addItems([
                    "Bilanciato (Consigliato)", 
                    "Evita traffico pesante", 
                    "Preferisci strade sterrate / ciclabili", 
                    "Massima velocità (Asfalto prioritario)"
                ])
                self.combo_strada.setStyleSheet("background-color: #2d2d30; color: white; padding: 8px; border: 1px solid #3e3e42; border-radius: 4px;")
                form_layout.addRow(QLabel("<b>Preferenza Strade:</b>"), self.combo_strada)

                # Durata stimata del viaggio a tappe
                self.combo_durata = QComboBox()
                self.combo_durata.addItems([
                    "Escursione in Giornata", 
                    "Weekend (2-3 giorni)", 
                    "Viaggio a tappe (Bikepacking Lunga Durata)"
                ])
                self.combo_durata.setStyleSheet("background-color: #2d2d30; color: white; padding: 8px; border: 1px solid #3e3e42; border-radius: 4px;")
                form_layout.addRow(QLabel("<b>Durata Prevista:</b>"), self.combo_durata)

                layout.addLayout(form_layout)
                layout.addSpacing(20)

                # Pulsantiera inferiore (Annulla / Conferma)
                btn_layout = QHBoxLayout()
                btn_Annulla = QPushButton("Annulla")
                btn_Annulla.setStyleSheet("background-color: #3e3e42; color: white; padding: 10px 15px; border-radius: 5px; font-weight: bold;")
                btn_Annulla.clicked.connect(self.reject)

                btn_Crea = QPushButton("🚀 Apri sulla Mappa e Procedi")
                btn_Crea.setStyleSheet("background-color: #28a745; color: white; padding: 10px 15px; border-radius: 5px; font-weight: bold;")
                btn_Crea.clicked.connect(self.conferma_creazione)

                btn_layout.addStretch()
                btn_layout.addWidget(btn_Annulla)
                btn_layout.addWidget(btn_Crea)

                layout.addLayout(btn_layout)

            def conferma_creazione(self):
                """Estrae i dati inseriti nei widget e chiude il dialog con successo."""
                self.risultato_dati = {
                    "nome": self.input_nome.text().strip() or "Nuovo Percorso Senza Nome",
                    "modalita": self.combo_modalita.currentText(),  # Cattura la scelta del bivio
                    "profilo_bici": self.combo_bici.currentText(),
                    "preferenza_strada": self.combo_strada.currentText(),
                    "durata": self.combo_durata.currentText()
                }
                self.accept()

        # Esecuzione effettiva del dialog modale
        wizard = WizardNuovoPercorsoDialog(self)
        if wizard.exec() == QDialog.Accepted:
            dati = wizard.risultato_dati
            nome_progetto = dati["nome"]
            modalita_scelta = dati["modalita"]
            
            try:
                # Scrittura del nuovo progetto nel database SQLite principale
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO progetti (nome_progetto, stato, data_creazione) "
                    "VALUES (?, ?, CURRENT_TIMESTAMP)",
                    (nome_progetto, 'ATTIVO')
                )
                id_progetto = cursor.lastrowid
                conn.commit()
                conn.close()

                # Aggiorna la lista visibile dei percorsi nella dashboard
                self.carica_lista_percorsi()
                
                # --- SMISTAMENTO AL BIVIO LOGICO ---
                if "Mappa" in modalita_scelta:
                    # CASO B: L'utente vuole disegnare da zero -> Salta alla pagina della Mappa (Indice 2)
                    self.current_progetto_id = id_progetto
                    self.lbl_nome_percorso_attivo.setText(f"Percorso: {nome_progetto}")
                    
                    if hasattr(self, 'progetto_selezionato_signal'):
                        self.progetto_selezionato_signal.emit(id_progetto, nome_progetto)
                    
                    main_window = self.window()
                    if hasattr(main_window, 'cambia_pagina'):
                        main_window.cambia_pagina(2)  # Sposta la vista principale sulla mappa interattiva
                        
                    print(f"✨ Percorso '{nome_progetto}' creato. Apertura diretta sulla Mappa Interattiva!")
                else:
                    # CASO A: Importazione GPX esterni -> Apre la gestione blocchi classica
                    self.apri_progetto_per_id(id_progetto, nome_progetto)
                    print(f"📂 Percorso '{nome_progetto}' creato. Apertura gestione blocchi per GPX esterni.")
                # -----------------------------------
                
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile creare il progetto: {e}")
                                    
    def apri_percorso_selezionato(self, item):
        """Apre il percorso selezionato dall'utente tramite clic nella lista della dashboard."""
        if not item:
            QMessageBox.warning(self, "Attenzione", "Seleziona un percorso dall'elenco.")
            return
        id_progetto = item.data(Qt.UserRole)
        nome_progetto = item.text().split("   |")[0].replace("📍 ", "")
        self.apri_progetto_per_id(id_progetto, nome_progetto)

    def apri_progetto_per_id(self, id_progetto, nome_percorso):
        """Imposta il progetto attivo in memoria, emette il segnale e carica le tappe."""
        self.current_progetto_id = id_progetto
        self.lbl_nome_percorso_attivo.setText(f"Percorso: {nome_percorso}")
        
        # Emette il segnale pulito per notificare l'avvenuta selezione del progetto
        self.progetto_selezionato_signal.emit(id_progetto, nome_percorso)
        self.stack_archivio.setCurrentIndex(1)
        self.aggiorna_tabella_tappe()
    
    def chiama_selettore_gpx(self):
        """Apre un dialog nativo di sistema per la scelta dei file GPX da importare."""
        from PySide6.QtWidgets import QFileDialog
        
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Seleziona File GPX", 
            "", 
            "File GPX (*.gpx);;Tutti i file (*.*)"
        )
        
        if files:
            self.elabora_files_gpx(files)
    
    def elimina_percorso_corrente(self):
        """Elimina permanentemente il progetto attivo e tutte le tappe collegate dal database."""
        if not self.current_progetto_id:
            return
        reply = QMessageBox.question(self, "Conferma", "Sei sicuro di voler eliminare questo percorso?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM progetti WHERE id = ?", (self.current_progetto_id,))
                cursor.execute("DELETE FROM tappe WHERE id_progetto = ?", (self.current_progetto_id,))
                conn.commit()
                conn.close()

                self.current_progetto_id = None
                self.carica_lista_percorsi()
                self.stack_archivio.setCurrentIndex(0)
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore durante l'eliminazione: {e}")
                
    def modifica_blocco_multiplo(self):
        """Modifica in blocco l'attributo 'blocco' per tutte le tappe selezionate nella tabella."""
        righe_selezionate = self.table_tappe.selectionModel().selectedRows()
        if not righe_selezionate:
            QMessageBox.warning(self, "Attenzione", "Seleziona almeno una riga dalla tabella cliccando sulla colonna dei numeri (Seq).")
            return

        nuovo_blocco, ok = QInputDialog.getText(self, "Modifica Blocco Multiplo", "Inserisci il nuovo nome del Blocco/Area per le tracce selezionate:")
        if ok and nuovo_blocco.strip():
            blocco_pulito = nuovo_blocco.strip()
            
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            
            for index in righe_selezionate:
                row_idx = index.row()
                item_seq = self.table_tappe.item(row_idx, 0)
                if item_seq:
                    seq_val = int(item_seq.text())
                    cursor.execute("""
                        UPDATE tappe SET blocco = ? 
                        WHERE id_progetto = ? AND sequenza = ?
                    """, (blocco_pulito, self.current_progetto_id, seq_val))
            
            conn.commit()
            conn.close()
            self.aggiorna_tabella_tappe()