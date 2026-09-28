# 🧠 DIAGNOSTICA INTELLIGENTE - MAPPA DELLA VERITÀ

> Analisi semantica avanzata, rilevamento anomalie, codice morto e coerenza architetturale.


## 📊 1. Sintesi Globale
- **Moduli Python monitorati:** `20`

## 🔍 2. Rilevamento Anomalie e Codice Orfano

- ✅ *Nessuna grave anomalia di framework o libreria rilevata nei moduli principali.*

## 🗺️ 3. Mappatura Dettagliata per Modulo

### 📄 Modulo: `agente_locale.py`
**⚙️ Funzioni:**
  - `def chiedi_all_agente()` - *Invia una richiesta all'agente locale forzando l'italiano e passando il codice*
**🌐 Endpoint / Rete:**
  - `http://localhost:11434/api/generate`

----------------------------------------

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
  - `create table`
  - `delete `
  - `sqlite`
**🌐 Endpoint / Rete:**
  - `127.0.0.1`
  - `@app.route`
  - `
✅ DIAGNOSTICA COMPLETATA! Report generato in: `

----------------------------------------

### 📄 Modulo: `analizzatore_progetto.py`
**⚙️ Funzioni:**
  - `def analizza_progetto()`
**🌐 Endpoint / Rete:**
  - `# 🗺️ REPORT BIKEPACKING STUDIO - MAPPA DELLA VERITÀ
`
  - `127.0.0.1:`
  - `
✅ REPORT_ARCHITETTURA.md generato con successo nella cartella del progetto!`

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
  - `cambia_pagina()`
  - `gestisci_cambio_progetto()` - *Aggiorna lo stato globale della finestra principale quando la dashboard cambia progetto*
  - `crea_bottone_navigazione()`
  - `crea_pagina_mappa()`
  - `crea_pagina_audit()`
  - `crea_pagina_trasporti()`
  - `crea_pagina_dogane()`
  - `crea_pagina_clima()`
  - `crea_pagina_statistiche()`
  - `crea_pagina_placeholder()`
  - `apri_pagina_clima()`
  - `apri_pagina_statistiche()`
  - `verifica_progetto_attivo()`
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
  - `mostra_mappa_gap()`
  - `avvia_wizard_trasferimento()`
  - `aggiorna_tabella_allarmi()`
**⚙️ Funzioni:**
  - `def inizializza_database()`
  - `def determina_blocco_da_nome_file()`
  - `def calcola_distanza_haversine()`
  - `def ottieni_nome_localita()`
**🗄️ Database / SQL:**
  - `INSERT INTO blocchi_ordine (id_progetto, nome_blocco, ordine) VALUES (?, ?, ?)`
  - `SELECT nome_blocco FROM blocchi_ordine WHERE id_progetto = ? ORDER BY ordine ASC`
  - `DELETE FROM trasferimenti WHERE id_progetto = ?`
**🌐 Endpoint / Rete:**
  - `
        CREATE TABLE IF NOT EXISTS dogane_progetto (
            id INTEGER PRI`

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
        CREATE TABLE IF NOT EXISTS tappe (
            id INTEGER PRIMARY KEY A`
  - `
        CREATE TABLE IF NOT EXISTS trasferimenti (
            id INTEGER PRIMA`
  - `data/bikepacking_app.db`
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
  - `crea_nuovo_progetto_dialog()` - *Apre un dialog modale (WizardNuovoPercorsoDialog) per la creazione guidata 
di un nuovo itinerario*
  - `apri_percorso_selezionato()` - *Apre il percorso selezionato dall'utente tramite clic nella lista della dashboard*
  - `apri_progetto_per_id()` - *Imposta il progetto attivo in memoria, emette il segnale e carica le tappe*
  - `chiama_selettore_gpx()` - *Apre un dialog nativo di sistema per la scelta dei file GPX da importare*
  - `elimina_percorso_corrente()` - *Elimina permanentemente il progetto attivo e tutte le tappe collegate dal database*
  - `modifica_blocco_multiplo()` - *Modifica in blocco l'attributo 'blocco' per tutte le tappe selezionate nella tabella*
- `class WizardNuovoPercorsoDialog`
  - `__init__()`
  - `init_ui()` - *Inizializza e dispone tutti gli elementi grafici del wizard*
  - `conferma_creazione()` - *Estrae i dati inseriti nei widget e chiude il dialog con successo*
**🗄️ Database / SQL:**
  - `
                            INSERT INTO tappe (id_progetto, sequenza, blocco, n`
  - `SELECT nome_file FROM tappe WHERE id_progetto = ?`
  - `
                        UPDATE tappe SET blocco = ? 
                        WH`
**🌐 Endpoint / Rete:**
  - `📂 Importa file GPX esistenti (Tracce Esterne)`
  - `Apre un dialog nativo di sistema per la scelta dei file GPX da importare.`
  - `
        Apre un dialog modale (WizardNuovoPercorsoDialog) per la creazione guid`

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
  - `_gestisci_permessi_gps()`
  - `toggle_pannello()`
  - `reload_map()`
  - `showEvent()`
  - `rigenera_mappa()`
  - `_fine_caricamento_asincrono()`
  - `open_map_manager()`
- `class WorkerCaricamentoMappa`
  - `__init__()`
  - `run()`
**🗄️ Database / SQL:**
  - `SELECT id, nome_file, sequenza, stato, blocco FROM tappe WHERE id_progetto = ? O`
  - `SELECT id, tipo_mezzo, vettore, da_luogo, a_luogo, start_lat, start_lon, end_lat`
**🌐 Endpoint / Rete:**
  - `http://127.0.0.1:8080/map`
  - `http://127.0.0.1:8080/api/set-gpx-data`

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
  - `SELECT start_lat, start_lon FROM tappe WHERE id = ?`
  - `
        SELECT start_lat, start_lon, end_lat, end_lon 
        FROM trasferimen`
  - `
        INSERT INTO trasferimenti_logistici 
        (id_progetto, id_tappa_ori`
**🌐 Endpoint / Rete:**
  - `
        INSERT INTO trasferimenti_logistici 
        (id_progetto, id_tappa_ori`
  - `
        CREATE TABLE IF NOT EXISTS trasferimenti_logistici (
            id INT`

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
  - `
        SELECT 
            COALESCE(t.blocco, 'Generico') as nome_blocco,
    `
  - `SELECT nome_blocco, giorni_extra, mesi_ideali_custom FROM blocchi_stagione WHERE`
  - `
        CREATE TABLE IF NOT EXISTS blocchi_stagione (
            id INTEGER PR`

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
        CREATE TABLE IF NOT EXISTS anagrafica_paesi (
            codice_iso2 T`
  - `
        CREATE TABLE IF NOT EXISTS dogane_progetto (
            id INTEGER PRI`
**🌐 Endpoint / Rete:**
  - `
        CREATE TABLE IF NOT EXISTS anagrafica_paesi (
            codice_iso2 T`
  - `Passaporto valido (6+ mesi)`
  - `
                    INSERT OR REPLACE INTO anagrafica_paesi 
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
  - `/api/maps/list`
  - `127.0.0.1`
  - `/api/set-gpx-data`

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
            SELECT codice_iso2, paese_nome 
            FROM dogane_progetto 
 `
  - `
        SELECT distanza_km, start_lat, start_lon, end_lat, end_lon, nome_file 
`
  - `SELECT distanza_km, nome_file FROM tappe WHERE id_progetto = ? AND stato = 'ATTI`

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
- **Endpoint JS:** `['/api/maps/list', 'http://127.0.0.1:8080/fonts/{fontstack}/{range}.pbf', 'http://127.0.0.1:8080/static/sprite', '/api/get-gpx-data']`
- **Layer MapLibre:** `Nessuno`