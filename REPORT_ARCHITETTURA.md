# 🧠 DIAGNOSTICA INTELLIGENTE - MAPPA DELLA VERITÀ

> Analisi semantica avanzata, rilevamento anomalie, codice morto e coerenza architetturale.


## 📊 1. Sintesi Globale
- **Moduli Python monitorati:** `19`

## 🔍 2. Rilevamento Anomalie e Codice Orfano

- ✅ *Nessuna grave anomalia di framework o libreria rilevata nei moduli principali.*

## 🗺️ 3. Mappatura Dettagliata per Modulo

### 📄 Modulo: `analizza_progetto_definitivo.py`
**👥 Classi:**
- `class AnalizzatoreIntelligente`
  - `__init__()`
  - `visit_Import()`
  - `visit_ImportFrom()`
  - `visit_ClassDef()`
  - `visit_FunctionDef()`
  - `visit_Constant()`
**⚙️ Funzioni:**
  - `def analizza_template_html()`
  - `def esegui_diagnostica_totale()`
**🗄️ Database / SQL:**
  - `insert `
  - `select `
  - `create table`
**🌐 Endpoint / Rete:**
  - `127.0.0.1`
  - `localhost`
  - `/api/`

----------------------------------------

### 📄 Modulo: `analizzatore_progetto.py`
**⚙️ Funzioni:**
  - `def analizza_progetto()`
**🌐 Endpoint / Rete:**
  - `
✅ REPORT_ARCHITETTURA.md generato con successo nella cartella del progetto!`
  - `127.0.0.1:`
  - `# 🗺️ REPORT BIKEPACKING STUDIO - MAPPA DELLA VERITÀ
`

----------------------------------------

### 📄 Modulo: `app_desktop.py`
**👥 Classi:**
- `class DoganeSignals`
- `class ClimaSignals`
- `class LocalMapServer`
  - `start_server()`
- `class DropAreaGPX`
  - `__init__()`
  - `dragEnterEvent()`
  - `dropEvent()`
- `class GestoreBlocchiWidget`
  - `__init__()`
  - `init_ui()`
  - `carica_blocchi()`
  - `sposta_su()`
  - `sposta_giu()`
  - `applica_riordinamento()`
- `class BikepackingStudioApp`
  - `__init__()`
  - `gestisci_cambio_progetto()` - *Aggiorna lo stato globale della finestra principale quando la dashboard cambia progetto*
  - `crea_bottone_navigazione()`
  - `crea_pagina_mappa()`
  - `crea_pagina_audit()`
  - `carica_lista_percorsi()` - *Reindirizza al nuovo modulo DashboardPage*
  - `apri_percorso_selezionato()`
  - `crea_nuovo_progetto_dialog()`
  - `apri_selettore_file()` - *Apre il file dialog e passa i file selezionati alla pagina Dashboard attiva*
  - `elabora_files_gpx()` - *Reindirizza l'elaborazione dei file GPX alla pagina Dashboard modulare*
  - `esegui_audit_automatico()` - *Esegue il controllo dell'integrità del percorso attivo*
  - `raccorda_traccia_istantaneo()` - *Richiama il servizio esterno per generare il raccordo e aggiorna la UI*
  - `aggiorna_tabella_tappe()` - *Reindirizza l'aggiornamento della tabella tappe alla pagina Dashboard modulare*
  - `aggiorna_blocco_tappa()`
  - `toggle_pausa_tappa()`
  - `cambia_ruolo_tappa()`
  - `elimina_singola_tappa()`
  - `elimina_percorso_corrente()`
  - `aggiorna_tabella_allarmi()`
  - `_coordinate_in_nome_luogo()` - *Converte Lat/Lon nel nome della città/località tramite OpenStreetMap Nominatim*
  - `rigenera_mappa()` - *Delega il lavoro pesante e la gestione dati al modulo gui/mappa*
  - `apri_in_browser()`
  - `crea_pagina_dogane()`
  - `esegui_analisi_doganale()`
  - `carica_o_analizza_dogane_automatico()` - *Controlla se ci sono dati doganali salvati usando il servizio centralizzato*
  - `_worker_analisi_doganale()`
  - `aggiorna_ui_dogane()` - *Popola la tabella nel thread principale della GUI*
  - `crea_pagina_trasporti()`
  - `crea_pagina_clima()` - *Crea la pagina grafica per la Catena Stagionale & Simulatore Meteo*
  - `esegui_analisi_clima()`
  - `_worker_analisi_clima()` - *Worker eseguito in background*
  - `aggiorna_ui_clima()` - *Aggiorna la tabella GUI con i risultati calcolati e rende editabile la colonna Extra*
  - `su_modifica_cella_clima()` - *Rileva la modifica dei Giorni Extra e ricalcola la catena per tutti i blocchi*
  - `apri_pagina_clima()` - *Apre la pagina Clima e avvia il calcolo della catena stagionale*
  - `crea_pagina_statistiche()` - *Crea la pagina con le KPI Card e le tabelle di metriche altimetriche e fasce costiere*
  - `apri_pagina_statistiche()` - *Passa alla pagina statistiche e aggiorna i dati del progetto corrente*
  - `apri_finestra_elenco_paesi()` - *Apre la finestra dei paesi con ricerca robusta tramite ISO2 e chiavi standard*
  - `carica_statistiche_progetto()` - *Metodo di caricamento sicuro e ottimizzato delle statistiche*
  - `crea_pagina_placeholder()`
  - `verifica_progetto_attivo()` - *Controlla se l'utente ha selezionato un percorso dalla Dashboard*
  - `mostra_avviso_nessun_progetto()` - *Crea la schermata di avviso quando non c'è un percorso aperto*
  - `mostra_mappa_gap()` - *Apre un popup con la mappa del tratto mancante e poi apre la logistica con nomi leggibili*
  - `_coordinate_in_nome_luogo_leggibile()` - *Converte le coordinate in un nome leggibile o usa le coordinate pulite se la lingua non è occidentale*
  - `cambia_pagina()`
  - `aggiorna_tabella_trasferimenti()`
  - `elimina_trasferimento()`
  - `apri_dialog_trasporto()` - *Ponte di sicurezza per la mappa*
  - `apri_dialogo_trasferimento()` - *Ponte di sicurezza alternativo per la mappa*
  - `avvia_dialog_logistica_con_geocoding()` - *Metodo blindato: impedisce doppi avvii e garantisce nomi leggibili*
  - `apri_dialog_trasferimento()`
  - `salva_trasferimento()`
  - `on_progetto_selezionato()` - *Gestisce la selezione o la creazione di un progetto, impostandolo come attivo*
**⚙️ Funzioni:**
  - `def inizializza_database()`
  - `def determina_blocco_da_nome_file()`
  - `def calcola_distanza_haversine()`
  - `def ottieni_nome_localita()`
**🗄️ Database / SQL:**
  - `UPDATE tappe SET sequenza = ? WHERE id = ?`
  - `
            SELECT a.tipo_allarme, a.messaggio, a.risolto, a.tappa_origine_id, `
  - `SELECT nome_blocco FROM blocchi_ordine WHERE id_progetto = ? ORDER BY ordine ASC`
**🌐 Endpoint / Rete:**
  - `
        CREATE TABLE IF NOT EXISTS dogane_progetto (
            id INTEGER PRI`
  - `Mezzo di Trasporto:`
  - `🔍 Cerca Soluzioni di Trasporto Online`

----------------------------------------

### 📄 Modulo: `backup.py`
**⚙️ Funzioni:**
  - `def esegui_backup_progetto()`
**🗄️ Database / SQL:**
  - `.db`
**🌐 Endpoint / Rete:**
  - `
=== STATUS REPORT BACKUP ===`

----------------------------------------

### 📄 Modulo: `database/database_setup.py`
**⚙️ Funzioni:**
  - `def inizializza_database()`
**🗄️ Database / SQL:**
  - `
        CREATE TABLE IF NOT EXISTS dogane_progetto (
            id INTEGER PRI`
  - `
        CREATE TABLE IF NOT EXISTS trasferimenti (
            id INTEGER PRIMA`
  - `
        CREATE TABLE IF NOT EXISTS tappe (
            id INTEGER PRIMARY KEY A`
**🌐 Endpoint / Rete:**
  - `
        CREATE TABLE IF NOT EXISTS dogane_progetto (
            id INTEGER PRI`

----------------------------------------

### 📄 Modulo: `export_structure.py`
**⚙️ Funzioni:**
  - `def build_tree()` - *Scansiona ricorsivamente la cartella e genera la struttura ad albero formattata*
  - `def main()`
**🌐 Endpoint / Rete:**
  - `✅ Struttura del progetto esportata con successo in: `

----------------------------------------

### 📄 Modulo: `gui/dashboard.py`
**👥 Classi:**
- `class DashboardPage`
  - `__init__()`
  - `init_ui()`
  - `aggiorna_tabella_tappe()` - *Carica le tappe associate al progetto e popola la tabella con widget interattivi*
  - `carica_tappe_progetto()` - *Alias di compatibilità*
  - `elabora_files_gpx()`
  - `aggiorna_blocco_tappa()`
  - `toggle_pausa_tappa()`
  - `cambia_ruolo_tappa()`
  - `elimina_singola_tappa()`
  - `carica_lista_percorsi()`
  - `crea_nuovo_progetto_dialog()`
  - `apri_percorso_selezionato()`
  - `apri_progetto_per_id()`
  - `chiama_selettore_gpx()` - *Apre direttamente la finestra per scegliere i file GPX e li elabora subito*
  - `elimina_percorso_corrente()`
  - `modifica_blocco_multiplo()` - *Permette di cambiare il blocco a tutte le tappe selezionate contemporaneamente*
- `class WizardNuovoPercorsoDialog`
  - `__init__()`
  - `init_ui()`
  - `conferma_creazione()`
**🗄️ Database / SQL:**
  - `UPDATE tappe SET sequenza = ? WHERE id = ?`
  - `SELECT nome_file FROM tappe WHERE id_progetto = ?`
  - `UPDATE tappe SET stato = ? WHERE id = ?`
**🌐 Endpoint / Rete:**
  - `📂 Importa file GPX esistenti (Tracce Esterne)`
  - `📁 Importa File GPX`

----------------------------------------

### 📄 Modulo: `gui/mappa.py`
**👥 Classi:**
- `class MapManagerDialog`
  - `__init__()`
  - `setup_ui()`
  - `refresh_catalog()`
  - `on_item_selected()`
  - `start_download()`
  - `on_download_finished()`
- `class PannelloPianificazioneWidget`
  - `__init__()`
- `class MappaWidget`
  - `__init__()`
  - `setup_ui()`
  - `toggle_pannello()`
  - `reload_map()`
  - `showEvent()`
  - `rigenera_mappa()`
  - `_fine_caricamento_asincrono()`
  - `open_map_manager()`
- `class WorkerCaricamentoMappa`
  - `__init__()`
  - `run()`
  - `open_map_manager()`
  - `reload_map()`
**🗄️ Database / SQL:**
  - `SELECT id, tipo_mezzo, vettore, da_luogo, a_luogo, start_lat, start_lon, end_lat`
  - `SELECT id, nome_file, sequenza, stato, blocco FROM tappe WHERE id_progetto = ? O`
**🌐 Endpoint / Rete:**
  - `http://127.0.0.1:8080/api/set-gpx-data`
  - `http://127.0.0.1:8080/map`

----------------------------------------

### 📄 Modulo: `gui/wizard_percorso.py`
**👥 Classi:**
- `class WizardNuovoPercorso`
  - `__init__()`
  - `init_ui()`
  - `conferma_creazione()`

----------------------------------------

### 📄 Modulo: `resources/genera_catalogo_sprite.py`
**⚙️ Funzioni:**
  - `def genera_singolo_pdf()`
  - `def compila_tutti_i_cataloghi()`

----------------------------------------

### 📄 Modulo: `service/__init__.py`

----------------------------------------

### 📄 Modulo: `service/audit_service.py`
**⚙️ Funzioni:**
  - `def calcola_distanza_haversine()` - *Calcola la distanza in chilometri tra due punti geografici usando la formula di Haversine*
  - `def rileva_gap_progetto()` - *Analizza la sequenza delle tappe e individua i GAP superiori a 3 km 
che non sono già coperti da trasferimenti logistici registrati*
  - `def registra_trasferimento_gap()` - *Registra il trasferimento logistico per colmare il GAP*
  - `def genera_raccordo_gpx()` - *Esegue il routing (BRouter o OSRM), crea il file GPX del raccordo,
aggiorna la sequenza delle tappe, inserisce la nuova tappa e registra il trasferimento*
**🗄️ Database / SQL:**
  - `
        SELECT start_lat, start_lon, end_lat, end_lon 
        FROM trasferimen`
  - `UPDATE tappe SET sequenza = sequenza + 1 WHERE id_progetto = ? AND sequenza > ?`
  - `
        INSERT INTO tappe (id_progetto, sequenza, blocco, nome_file, start_lat,`
**🌐 Endpoint / Rete:**
  - `
        CREATE TABLE IF NOT EXISTS trasferimenti_logistici (
            id INT`
  - `
        INSERT INTO trasferimenti_logistici 
        (id_progetto, id_tappa_ori`

----------------------------------------

### 📄 Modulo: `service/clima_service.py`
**⚙️ Funzioni:**
  - `def determina_mesi_ideali_automatici()` - *Determina AUTOMATICAMENTE i mesi ideali per il ciclismo in base alla 
posizione geografica e all'altitudine della tappa/blocco*
  - `def assicura_tabelle_clima()` - *Garantisce l'esistenza delle tabelle e aggiorna le colonne mancanti se necessario*
  - `def salva_impostazioni_stagione()` - *Salva le impostazioni modificate dall'utente nell'interfaccia*
  - `def calcola_catena_stagionale()` - *Calcola la sequenza temporale con rilevamento DINAMICO dei mesi ideali
basato sulle coordinate reali delle tappe del progetto*
**🗄️ Database / SQL:**
  - `SELECT data_partenza, modificatore_riposo FROM progetto_stagione WHERE id_proget`
  - `
        INSERT INTO progetto_stagione (id_progetto, data_partenza, modificatore`
  - `SELECT nome_blocco, giorni_extra, mesi_ideali_custom FROM blocchi_stagione WHERE`

----------------------------------------

### 📄 Modulo: `service/config.py`
**🗄️ Database / SQL:**
  - `bikepacking_app.db`

----------------------------------------

### 📄 Modulo: `service/dogane_service.py`
**⚙️ Funzioni:**
  - `def inizializza_tabelle_dogane()`
  - `def popola_database_mondiale_completo()` - *Legge direttamente il file paesi_mondo*
  - `def recupera_dogane_salvate()`
  - `def analizza_dogane_progetto()` - *Restituisce direttamente i dati già salvati ripuliti dai doppioni*
**🗄️ Database / SQL:**
  - `
        SELECT 
            ordine_progressivo,
            codice_iso2,
      `
  - `
                    INSERT OR REPLACE INTO anagrafica_paesi 
                  `
  - `
        CREATE TABLE IF NOT EXISTS anagrafica_paesi (
            codice_iso2 T`
**🌐 Endpoint / Rete:**
  - `Passaporto valido (6+ mesi)`
  - `
        CREATE TABLE IF NOT EXISTS anagrafica_paesi (
            codice_iso2 T`
  - `
        SELECT 
            ordine_progressivo,
            codice_iso2,
      `

----------------------------------------

### 📄 Modulo: `service/map_manager_service.py`
**👥 Classi:**
- `class DownloadWorker`
  - `__init__()`
  - `run()`
- `class MapManagerService`
  - `get_installed_maps()` - *Analizza la cartella data/maps/ e restituisce le mappe presenti su disco*
  - `get_available_catalog()` - *Combina il catalogo remoto con lo stato di installazione locale*

----------------------------------------

### 📄 Modulo: `service/map_server.py`
**⚙️ Funzioni:**
  - `def serve_sprite()`
  - `def start_martin_server()`
  - `def serve_fonts()`
  - `def set_gpx_data()`
  - `def get_gpx_data()`
  - `def list_maps()`
  - `def show_map()`
  - `def run_server()`
  - `def start_local_map_server()`
**🌐 Endpoint / Rete:**
  - `/api/set-gpx-data`
  - `/api/get-gpx-data`
  - `127.0.0.1`

----------------------------------------

### 📄 Modulo: `service/stats_service.py`
**⚙️ Funzioni:**
  - `def _haversine_distance_m()` - *Calcola la distanza reale sulla superficie terrestre in metri tra due punti GPS*
  - `def _scarica_coste_alta_risoluzione()`
  - `def _inizializza_motore_costa()`
  - `def calcola_distanza_mare_m()` - *Calcola la distanza geodesica esatta in metri dal mare per una coordinata Lat/Lon*
  - `def assegna_fascia_costiera_metri()`
  - `def _trova_percorso_gpx()`
  - `def _estrai_punti_gpx()`
  - `def _estrai_altimetria_da_gpx()`
  - `def ottieni_kpi_totali_progetto()`
  - `def ottieni_statistiche_per_blocco()`
  - `def ottieni_ripartizione_fasce_mare()` - *Ripartizione chilometrica esatta basata su campionamento continuo e calcolo Haversine*
  - `def get_paesi_attraversati_stats()` - *Estrae i paesi basandosi rigorosamente sui codici ISO2 salvati nel database*
**🗄️ Database / SQL:**
  - `
        SELECT distanza_km, start_lat, start_lon, end_lat, end_lon, nome_file 
`
  - `
        SELECT blocco, distanza_km, nome_file 
        FROM tappe 
        WHER`
  - `
            SELECT codice_iso2, paese_nome 
            FROM dogane_progetto 
 `

----------------------------------------

### 📄 Modulo: `static/aggiorna_sprite.py`
**⚙️ Funzioni:**
  - `def get_props()`
**🌐 Endpoint / Rete:**
  - `sport`
  - `sports`
  - `sports_centre`

----------------------------------------

## 🌍 4. Stato Frontend Mappa (`templates/map_view.html`)

- **Stato:** Analizzato con successo.
- **Endpoint JS:** `['/api/get-gpx-data', 'http://127.0.0.1:8080/fonts/{fontstack}/{range}.pbf', '/api/maps/list', 'http://127.0.0.1:8080/static/sprite']`
- **Layer MapLibre:** `Nessuno`