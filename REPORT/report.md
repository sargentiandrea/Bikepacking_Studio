# Analisi del progetto: Bikepacking_Studio

*Generato il 2026-10-03 alle 21:54:03*

## 1. Sintesi

- Moduli Python: **47**
- Classi: **23**
- Funzioni globali: **384**
- Rotte Flask: **8**
- Tabelle rilevate: **27**
- Simboli orfani: **50**

## Database

- Percorso: `data/bikepacking_app.db`
- Tabelle: 23

| Tabella | Righe | Colonne chiave |
|---|---:|---|
| `allarmi_percorso` | 5 | id (PK), id_progetto (FK → progetti.id) |
| `anagrafica_paesi` | 198 | codice_iso2 (PK) |
| `anagrafica_paesi_mondo` | 12 | codice_iso2 (PK) |
| `blocchi_ordine` | 24 | id (PK), id_progetto (FK → progetti.id) |
| `blocchi_stagione` | 18 | id (PK) |
| `cache_geo_paesi` | 2 | lat_griglia (PK), lon_griglia (PK) |
| `cache_nomi_luoghi` | 999 | lat_arrotondata (PK), lon_arrotondata (PK) |
| `clima_blocco_mese` | 288 | id_progetto (PK), nome_blocco (PK), mese (PK) |
| `clima_paese_mese` | 540 | id_progetto (PK), paese (PK), mese (PK) |
| `confini_box` | 11 | id (PK) |
| `dogane_percorso` | 0 | id (PK) |
| `dogane_progetto` | 67 | id (PK), id_progetto (FK → progetti.id) |
| `impostazioni_semaforo` | 0 | id_progetto (PK) |
| `progetti` | 3 | id (PK) |
| `progetto_stagione` | 1 | id_progetto (PK) |
| `scenari` | 0 | id (PK) |
| `superfici_tappa` | 984 | id (PK), tappa_id (FK → tappe.id) |
| `tappa_analisi` | 985 | tappa_id (PK), tappa_id (FK → tappe.id) |
| `tappa_costa_riepilogo` | 985 | tappa_id (PK), tappa_id (FK → tappe.id) |
| `tappa_geometrie` | 984 | tappa_id (PK), tappa_id (FK → tappe.id) |
| `tappa_segmenti` | 986 | tappa_id (PK), track_index (PK), segment_index (PK), tappa_id (FK → tappe.id) |
| `tappe` | 982 | id (PK), id_progetto (FK → progetti.id) |
| `trasferimenti` | 28 | id (PK), id_progetto (FK → progetti.id) |

## File di configurazione

- `paesi_mondo.json`
- `resources/sprite.json`
- `resources/sprite@2x.json`
- `static/Spite OLD/old_sprite.json`
- `static/Spite OLD/old_sprite@2x.json`
- `static/sprite.json`
- `static/sprite@2x.json`

## Servizi esterni

- `http://127.0.0.1:8080/api/map-interactions`
- `http://127.0.0.1:8080/api/set-gpx-data`
- `http://127.0.0.1:8080/map`
- `http://localhost:3000`
- `http://s3.amazonaws.com/doc/2006-03-01/`
- `http://www.topografix.com/GPX/1/1`
- `http://{BROUTER_HOST}:{BROUTER_PORT}`
- `http://{BROUTER_HOST}:{BROUTER_PORT}/brouter`
- `http://{host}:{port}`
- `https://creativecommons.org/licenses/by/4.0/\n`
- `https://download.geonames.org/export/dump/allCountries.zip`
- `https://download.geonames.org/export/dump/alternateNamesV2.zip`
- `https://os.unil.cloud.switch.ch/chelsa02`
- `https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_center.mbtiles`
- `https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_islands.mbtiles`
- `https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_north.mbtiles`
- `https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_south.mbtiles`
- `https://www.chelsa-climate.org/datasets/chelsa_monthly`
- `https://www.geonames.org/\n`
- `martin`
- `redis`

## 2. Architettura (per strato)

**ui** (12 file)
- `gui/dashboard.py`
- `gui/drop_area_gpx.py`
- `gui/mappa.py`
- `gui/mappa_barra_superfici.py`
- `gui/mappa_cache.py`
- `gui/mappa_dettagli.py`
- `gui/mappa_manager.py`
- `gui/mappa_pianificatore.py`
- ... e altri 4

**database** (1 file)
- `database/database_setup.py`

**api** (1 file)
- `service/map_server.py`

**core** (28 file)
- `service/__init__.py`
- `service/audit_service.py`
- `service/catena_stagionale_service.py`
- `service/clima_estrattore.py`
- `service/clima_service.py`
- `service/config.py`
- `service/costa_service.py`
- `service/dettagli_rotta_service.py`
- ... e altri 20

**altro** (5 file)
- `app_desktop.py`
- `backup.py`
- `installa_geonames.py`
- `resources/genera_catalogo_sprite.py`
- `static/aggiorna_sprite.py`

## 3. Endpoint Flask

- `/sprite<path:filename>` → `serve_sprite()` [GET] in `service/map_server.py`
- `/fonts/<path:fontstack>/<range_pbf>` → `serve_fonts()` [GET] in `service/map_server.py`
- `/api/set-gpx-data` → `set_gpx_data()` [POST] in `service/map_server.py`
- `/api/get-gpx-data` → `get_gpx_data()` [GET] in `service/map_server.py`
- `/api/tappe/<int:tappa_id>/geometria-completa` → `get_geometria_completa_tappa()` [GET] in `service/map_server.py`
- `/api/map-interactions` → `leggi_interazioni_mappa()` [GET] in `service/map_server.py`
- `/api/maps/list` → `list_maps()` [GET] in `service/map_server.py`
- `/map` → `show_map()` [GET] in `service/map_server.py`

## 4. Frontend & Mappa

**Endpoint usati dal frontend:**
- `/api/get-gpx-data`
- `/api/map-interactions`
- `/api/maps/list`
- `http://127.0.0.1:8080/fonts/{fontstack}/{range}.pbf`
- `http://127.0.0.1:8080/static/sprite`

**Librerie esterne:**
- `/static/maplibre-gl.js`

## 5. Simboli orfani

*50 simboli definiti ma mai citati altrove:*

- **classe** `EstrazioneClimaWorker` in `app_desktop.py`
- **classe** `ClimaSoglieDialog` in `app_desktop.py`
- **classe** `TimelineCatenaWidget` in `app_desktop.py`
- **classe** `GestoreBlocchiWidget` in `app_desktop.py`
- **classe** `BikepackingStudioApp` in `app_desktop.py`
- **funzione** `imposta_righe` in `app_desktop.py`
- **funzione** `carica_blocchi` in `app_desktop.py`
- **funzione** `esegui_backup_progetto` in `backup.py`
- **classe** `WizardNuovoPercorsoDialog` in `gui/dashboard.py`
- **funzione** `carica_tappe_progetto` in `gui/dashboard.py`
- **classe** `DropAreaGPX` in `gui/drop_area_gpx.py`
- **classe** `WorkerCaricamentoMappa` in `gui/mappa.py`
- **funzione** `cancella_anteprima_percorso` in `gui/mappa.py`
- **classe** `WizardNuovoPercorso` in `gui/wizard_percorso.py`
- **funzione** `genera_singolo_pdf` in `resources/genera_catalogo_sprite.py`
- **funzione** `compila_tutti_i_cataloghi` in `resources/genera_catalogo_sprite.py`
- **funzione** `registra_trasferimento_gap` in `service/audit_service.py`
- **funzione** `valuta_paese` in `service/catena_stagionale_service.py`
- **funzione** `applica_semafori` in `service/catena_stagionale_service.py`
- **funzione** `determina_mesi_ideali_automatici` in `service/clima_service.py`
- **funzione** `calcola_catena_stagionale` in `service/clima_service.py`
- **funzione** `inizializza_tabelle_dogane` in `service/dogane_service.py`
- **funzione** `popola_database_mondiale_completo` in `service/dogane_service.py`
- **funzione** `semplifica_segmento_rdp` in `service/geometria_service.py`
- **funzione** `comprimi_segmenti` in `service/geometria_service.py`
- **funzione** `get_installed_maps` in `service/map_manager_service.py`
- **funzione** `serve_sprite` in `service/map_server.py`
- **funzione** `start_martin_server` in `service/map_server.py`
- **funzione** `log_output` in `service/map_server.py`
- **funzione** `start_brouter_server` in `service/map_server.py`
- ... e altri 20

## 6. Moduli con più contenuto

- `app_desktop.py`: 5 classi, 66 funzioni
- `gui/mappa_pianificatore.py`: 1 classi, 31 funzioni
- `gui/mappa.py`: 2 classi, 25 funzioni
- `service/catena_stagionale_service.py`: 0 classi, 27 funzioni
- `gui/dashboard.py`: 2 classi, 19 funzioni
- `gui/mappa_worker.py`: 4 classi, 13 funzioni
- `service/map_server.py`: 0 classi, 15 funzioni
- `service/superfici_service.py`: 0 classi, 15 funzioni
- `service/stats_service.py`: 0 classi, 14 funzioni
- `service/punti_service.py`: 0 classi, 12 funzioni

## 7. Livello di rischio e file critici

**Livello di rischio:** `alto`

**File critici (da guardare per primi):**
- `app_desktop.py`
- `gui/mappa_pianificatore.py`
- `gui/dashboard.py`

**Azioni consigliate:**
- Rivedere i simboli orfani e decidere se integrarli, rimuoverli o spostarli.
- Prioritizzare i file con score più alto per refactor e verifica.
- Usare PROGETTO_INDEX.json come contesto minimo per ridurre i token richiesti alle IA.
