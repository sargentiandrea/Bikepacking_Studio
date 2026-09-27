import os
import json
import sqlite3
import requests
import gpxpy

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QListWidget, QListWidgetItem, QDialog, QProgressBar, QMessageBox,
    QFrame, QLineEdit, QComboBox, QGraphicsDropShadowEffect
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtCore import QUrl, Qt, QTimer, QThread, Signal


from service.config import DB_NAME
from service.map_manager_service import MapManagerService, DownloadWorker

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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(340)  # Imposta una larghezza fissa coerente con il layout della mappa
        
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
        layout.setSizeConstraint(QVBoxLayout.SetFixedSize)  # Mantiene l'altezza fissa basata sui widget interni
        
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
        
        # --- SEZIONE PARTENZA ---
        layout_partenza = QHBoxLayout()
        layout_partenza.setSpacing(8)
        lbl_icon_a = QLabel("🟢")  # Icona a pallino verde per indicare l'inizio
        lbl_icon_a.setFixedWidth(16)
        self.input_partenza = QLineEdit()
        self.input_partenza.setPlaceholderText("Inserisci punto di partenza...")
        layout_partenza.addWidget(lbl_icon_a)
        layout_partenza.addWidget(self.input_partenza)
        layout.addLayout(layout_partenza)
        
        # --- SEZIONE DESTINAZIONE ---
        layout_arrivo = QHBoxLayout()
        layout_arrivo.setSpacing(8)
        lbl_icon_b = QLabel("🏁")  # Icona bandierina per indicare l'arrivo
        lbl_icon_b.setFixedWidth(16)
        self.input_destinazione = QLineEdit()
        self.input_destinazione.setPlaceholderText("Inserisci destinazione...")
        layout_arrivo.addWidget(lbl_icon_b)
        layout_arrivo.addWidget(self.input_destinazione)
        layout.addLayout(layout_arrivo)
        
        # --- PROFILO DI INSTRADAMENTO ---
        lbl_profilo = QLabel("Profilo di instradamento")
        lbl_profilo.setStyleSheet("color: #94a3b8; font-size: 11px; margin-top: 4px; border: none;")
        layout.addWidget(lbl_profilo)
        
        self.combo_profilo = QComboBox()
        self.combo_profilo.addItems(["🚲 Gravel / Viaggio", "🛣️ Strada", "🚵 MTB", "⚖️ Equilibrato"])
        layout.addWidget(self.combo_profilo)
        
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
        layout.addWidget(self.btn_salva)

class MappaWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(None)
        self.parent_app = parent
        self.mappa_worker = None
        self.ultimo_progetto_id_caricato = None
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
        layout_container.addWidget(self.web_view)

        # Creazione del pannello fluttuante sovrapposto
        self.pannello_pianificazione = PannelloPianificazioneWidget(container_mappa)
        self.pannello_pianificazione.move(16, 16)
        self.pannello_pianificazione.raise_() 
        self.pannello_pianificazione.btn_chiudi_pannello.clicked.connect(self.toggle_pannello)

        main_layout.addWidget(container_mappa)

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
        if hasattr(self, 'pannello_pianificazione'):
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
        QTimer.singleShot(50, lambda: self.web_view.page().runJavaScript("if(typeof map !== 'undefined') map.resize();"))
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
                    if(typeof map !== 'undefined' && map) {
                        map.flyTo({ center: [12.5674, 41.8719], zoom: 6, duration: 1200 });
                    }
                }
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


# --- IL WORKER ASINCRONO IN BACKGROUND ESTERNO E CORRETTAMENTE ALLINEATO ---
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
                filepath = os.path.join(os.getcwd(), "gpx", solo_nome)
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
