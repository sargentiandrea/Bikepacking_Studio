import os
import json
import threading
import math
import requests

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QMessageBox,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtCore import QTimer, QThread, Signal
from PySide6.QtGui import QDesktopServices

from service.config import BASE_DIR
from service.mappa_dati_service import (
    costruisci_geojson_progetto,
    firma_dati_mappa,
)
from gui.mappa_pianificatore import PannelloPianificazioneWidget

# Componenti spostati in moduli dedicati (Fase 3.0 del refactor).
from gui.mappa_cache import CacheMappaProgetto
from gui.mappa_dettagli import PannelloDettagliRotta
from gui.mappa_manager import MapManagerDialog
from gui.mappa_worker import (
    PianificazionePercorsoWorker,
    WorkerAltimetria,
    WorkerAnalisiSuperficiOffline,
    WorkerNomiLuoghi,
)

GPX_DIR = os.path.join(BASE_DIR, "gpx")



class MappaWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(None)
        self.parent_app = parent
        self.mappa_worker = None
        self._token_caricamento_mappa = 0
        self._mappa_workers_attivi = []  # tiene in vita i worker finché non finiscono davvero (vedi rigenera_mappa)
        self.ultimo_progetto_id_caricato = None
        self._firma_dati_mappa_caricati = None
        self._cache_mappa = CacheMappaProgetto()
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
        self.pannello_pianificazione.imposta_stato(
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
                self.pannello_pianificazione.aggiungi_waypoint(
                    evento["lat"], evento["lon"]
                )
            elif evento.get("action") == "rubberband_waypoint":
                self.pannello_pianificazione.prepara_modifica_tappa(
                    evento["tappa_id"], evento["lat"], evento["lon"]
                )
            elif evento.get("action") == "cancel_interaction":
                self.web_view.page().runJavaScript(
                    "if(window.impostaModalitaInterazioneMappa) "
                    f"window.impostaModalitaInterazioneMappa(null, {int(id_progetto)});"
                )
                self.pannello_pianificazione.imposta_stato(
                    "Modalità mappa disattivata."
                )
            # Volutamente dentro il ciclo: ogni modalità mappa è "usa e getta".
            # Il JavaScript (inviaInterazioneMappa) la azzera subito dopo aver
            # inviato UN solo evento, quindi dopo averlo gestito il polling non serve più.
            # Con zero eventi il timer resta attivo in attesa del click: non spostare fuori dal for.
            self._poll_interazioni_timer.stop()

    def mostra_anteprima_percorso(
        self,
        coordinate,
        punti_divisione=None,
        adatta_visuale=True,
    ):
        """Mostra la rotta e gli eventuali confini tra tappe senza scriverli nel DB."""
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [punto[1], punto[0]] for punto in coordinate
                        ],
                    },
                    "properties": {"tipo": "anteprima_pianificazione"},
                },
                *[
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [punto[1], punto[0]],
                        },
                        "properties": {
                            "tipo": "divisione_tappa",
                            "sequenza": indice,
                        },
                    }
                    for indice, punto in enumerate(punti_divisione or [], start=1)
                ],
            ],
        }
        self.web_view.page().runJavaScript(
            "if(window.aggiornaAnteprimaPercorso) "
            f"window.aggiornaAnteprimaPercorso({json.dumps(geojson)}, "
            f"{json.dumps(adatta_visuale)});"
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
            QTimer.singleShot(0, self.pannello_pianificazione.adatta_altezza)

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
            QTimer.singleShot(0, self.pannello_pianificazione.adatta_altezza)
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
                cache_progetto = self._cache_mappa.ottieni(p_id)
                cache_valida = self._cache_mappa.e_valida(p_id, firma_corrente)

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
            self._cache_mappa.salva(id_progetto, firma_dati, geojson_payload)
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
