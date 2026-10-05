# AI Brief - Bikepacking_Studio

*Aggiornato: 2026-10-06 00:26*

## Come leggere il progetto

- All'inizio di ogni richiesta: `REPORT/AI_BRIEF.md`.
- Prima di lavorare sul database: `REPORT/DB_SCHEMA.md`.
- Prima di lavorare sulla configurazione: `REPORT/CONFIG_FILES.md`.
- Prima di lavorare sui servizi esterni: `REPORT/EXTERNAL_SERVICES.md`.
- Per dettagli specifici: `REPORT/analisi.json` oppure il file di codice interessato.
- Per le persone: `REPORT/report.md` (completo) e `REPORT/riepilogo.txt` (sintesi).
- `REPORT/ULTIMO_RUN.json` è riservato allo script.
- Non leggere `aider_context.md` né i file con timestamp: sono specifici o storici.

## Numeri essenziali

- Moduli Python: 77
- Classi: 48
- Funzioni: 585
- Rotte Flask: 8
- Tabelle DB: 27
- Simboli orfani: 136
- **Livello rischio: alto**

## File critici (score più alto)

- `gui/mappa_pianificatore.py` - score 286 - 1 classi, 44 funzioni, 0 anomalie
- `app_desktop.py` - score 201 - 1 classi, 43 funzioni, 0 anomalie
- `gui/dashboard.py` - score 166 - 2 classi, 19 funzioni, 0 anomalie
- `gui/mappa.py` - score 147 - 2 classi, 26 funzioni, 0 anomalie
- `service/catena_stagionale_service.py` - score 133 - 0 classi, 27 funzioni, 0 anomalie

## Endpoint Flask

- `/sprite<path:filename>` [GET] -> `serve_sprite()` in `service/map_server.py`
- `/fonts/<path:fontstack>/<range_pbf>` [GET] -> `serve_fonts()` in `service/map_server.py`
- `/api/set-gpx-data` [POST] -> `set_gpx_data()` in `service/map_server.py`
- `/api/get-gpx-data` [GET] -> `get_gpx_data()` in `service/map_server.py`
- `/api/tappe/<int:tappa_id>/geometria-completa` [GET] -> `get_geometria_completa_tappa()` in `service/map_server.py`
- `/api/map-interactions` [GET] -> `leggi_interazioni_mappa()` in `service/map_server.py`
- `/api/maps/list` [GET] -> `list_maps()` in `service/map_server.py`
- `/map` [GET] -> `show_map()` in `service/map_server.py`

## Simboli orfani (top 15)

- `BikepackingStudioApp` (classe) in `app_desktop.py`
- `esegui_backup_progetto` (funzione) in `backup.py`
- `WizardNuovoPercorsoDialog` (classe) in `gui/dashboard.py`
- `carica_tappe_progetto` (funzione) in `gui/dashboard.py`
- `DropAreaGPX` (classe) in `gui/drop_area_gpx.py`
- `WorkerCaricamentoMappa` (classe) in `gui/mappa.py`
- `carica_allarmi_attivi` (funzione) in `gui/pagine/pagina_audit.py`
- `testo_card` (funzione) in `gui/pagine/pagina_statistiche.py`
- `carica_trasferimenti` (funzione) in `gui/pagine/pagina_trasporti.py`
- `recupera_nomi_tappe` (funzione) in `gui/pagine/pagina_trasporti.py`
- `WizardNuovoPercorso` (classe) in `gui/wizard_percorso.py`
- `EstrazioneClimaWorker` (classe) in `gui/worker_clima.py`
- `righe_progetto_1` (funzione) in `import_clima_mondiale.py`
- `genera_singolo_pdf` (funzione) in `resources/genera_catalogo_sprite.py`
- `compila_tutti_i_cataloghi` (funzione) in `resources/genera_catalogo_sprite.py`
- ... e altri 121 (vedi report completo)

## Duplicazioni rilevate

*24 funzioni/metodi definiti in più file:*

- `aggiorna` (5 copie) → `gui/pagine/controller_clima.py`, `gui/pagine/pagina_audit.py`, `gui/pagine/pagina_dogane.py`, `gui/pagine/pagina_statistiche.py`, `gui/pagine/pagina_trasporti.py`
- `crea_backup` (4 copie) → `service/migrazione_tappa_analisi.py`, `service/migrazione_tappa_costa.py`, `service/migrazione_tappa_costa_metadati.py`, `service/migrazione_tappa_geometrie.py`
- `esegui_migrazione` (4 copie) → `service/migrazione_tappa_analisi.py`, `service/migrazione_tappa_costa.py`, `service/migrazione_tappa_costa_metadati.py`, `service/migrazione_tappa_geometrie.py`
- `setUpClass` (4 copie) → `tests/test_coda_routing.py`, `tests/test_pianificatore_5_1_gui.py`, `tests/test_pianificatore_5_3.py`, `tests/test_pianificatore_5_4.py`
- `crea_nuovo_progetto_dialog` (3 copie) → `app_desktop.py`, `gui/dashboard.py`, `gui/dialog_nuovo_progetto.py`
- `init_ui` (3 copie) → `gui/dashboard.py`, `gui/widget_blocchi.py`, `gui/wizard_percorso.py`
- `setUp` (3 copie) → `tests/test_pianificatore_5_1_gui.py`, `tests/test_pianificatore_5_2.py`, `tests/test_pianificatore_5_3.py`
- `raccorda_gap_selezionato` (2 copie) → `app_desktop.py`, `gui/pagine/pagina_trasporti.py`
- `carica_lista_percorsi` (2 copie) → `app_desktop.py`, `gui/dashboard.py`
- `elabora_files_gpx` (2 copie) → `app_desktop.py`, `gui/dashboard.py`
- `aggiorna_tabella_tappe` (2 copie) → `app_desktop.py`, `gui/dashboard.py`
- `elimina_percorso_corrente` (2 copie) → `app_desktop.py`, `gui/dashboard.py`
- `conferma_creazione` (2 copie) → `gui/dashboard.py`, `gui/wizard_percorso.py`
- `salva` (2 copie) → `gui/dialog_nuovo_progetto.py`, `gui/mappa_cache.py`
- `setup_ui` (2 copie) → `gui/mappa.py`, `gui/mappa_manager.py`
- `showEvent` (2 copie) → `gui/mappa.py`, `gui/mappa_pianificatore.py`
- `imposta_superfici` (2 copie) → `gui/mappa_barra_superfici.py`, `gui/mappa_dettagli.py`
- `paintEvent` (2 copie) → `gui/mappa_barra_superfici.py`, `gui/widget_timeline_catena.py`
- `imposta_stato` (2 copie) → `gui/mappa_dettagli.py`, `gui/mappa_pianificatore.py`
- `request_stop` (2 copie) → `gui/mappa_worker.py`, `tests/test_coda_routing.py`
- ... e altre 4

## Database

- Percorso: `data/bikepacking_app.db`
- Numero di tabelle: 23
- `allarmi_percorso`: 5 righe
- `anagrafica_paesi`: 198 righe
- `anagrafica_paesi_mondo`: 12 righe
- `blocchi_ordine`: 24 righe
- `blocchi_stagione`: 18 righe
- `cache_geo_paesi`: 2 righe
- `cache_nomi_luoghi`: 999 righe
- `clima_blocco_mese`: 288 righe
- `clima_paese_mese`: 3432 righe
- `confini_box`: 11 righe
- `dogane_percorso`: 0 righe
- `dogane_progetto`: 67 righe
- `impostazioni_semaforo`: 0 righe
- `progetti`: 3 righe
- `progetto_stagione`: 1 righe
- `scenari`: 1 righe
- `superfici_tappa`: 984 righe
- `tappa_analisi`: 986 righe
- `tappa_costa_riepilogo`: 986 righe
- `tappa_geometrie`: 985 righe
- `tappa_segmenti`: 987 righe
- `tappe`: 982 righe
- `trasferimenti`: 28 righe

## Servizi esterni rilevati

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

## File di configurazione

- `paesi_mondo.json`
- `resources/sprite.json`
- `resources/sprite@2x.json`
- `static/Spite OLD/old_sprite.json`
- `static/Spite OLD/old_sprite@2x.json`
- `static/sprite.json`
- `static/sprite@2x.json`

## Moduli principali

- `gui/mappa_pianificatore.py`: 1 classi, 44 funzioni
- `app_desktop.py`: 1 classi, 43 funzioni
- `gui/mappa.py`: 2 classi, 26 funzioni
- `tests/test_pianificatore_5_1.py`: 6 classi, 22 funzioni
- `service/catena_stagionale_service.py`: 0 classi, 27 funzioni
- `gui/pagine/controller_clima.py`: 1 classi, 23 funzioni
- `tests/test_pianificatore_5_3.py`: 4 classi, 18 funzioni
- `gui/dashboard.py`: 2 classi, 19 funzioni
- `gui/mappa_worker.py`: 4 classi, 17 funzioni
- `tests/test_pianificatore_5_2.py`: 3 classi, 14 funzioni

## Azioni consigliate

- Rivedere i simboli orfani e decidere se integrarli, rimuoverli o spostarli.
- Prioritizzare i file con score più alto per refactor e verifica.
- Usare PROGETTO_INDEX.json come contesto minimo per ridurre i token richiesti alle IA.

---

*Per approfondire: vedi `analisi.json` (dataset completo) o `report.md` (versione umana).*
