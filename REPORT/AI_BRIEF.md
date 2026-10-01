# AI Brief - Bikepacking_Studio

*Aggiornato: 2026-10-01 09:04*

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

- Moduli Python: 23
- Classi: 19
- Funzioni: 250
- Rotte Flask: 7
- Tabelle DB: 21
- Simboli orfani: 56
- **Livello rischio: alto**

## File critici (score più alto)

- `gui/mappa.py` - score 454 - 9 classi, 84 funzioni, 0 anomalie
- `app_desktop.py` - score 331 - 5 classi, 52 funzioni, 0 anomalie
- `gui/dashboard.py` - score 162 - 2 classi, 20 funzioni, 0 anomalie
- `service/stats_service.py` - score 92 - 0 classi, 12 funzioni, 0 anomalie
- `service/superfici_service.py` - score 90 - 0 classi, 15 funzioni, 0 anomalie

## Endpoint Flask

- `/sprite<path:filename>` [GET] -> `serve_sprite()` in `service/map_server.py`
- `/fonts/<path:fontstack>/<range_pbf>` [GET] -> `serve_fonts()` in `service/map_server.py`
- `/api/set-gpx-data` [POST] -> `set_gpx_data()` in `service/map_server.py`
- `/api/get-gpx-data` [GET] -> `get_gpx_data()` in `service/map_server.py`
- `/api/map-interactions` [GET] -> `leggi_interazioni_mappa()` in `service/map_server.py`
- `/api/maps/list` [GET] -> `list_maps()` in `service/map_server.py`
- `/map` [GET] -> `show_map()` in `service/map_server.py`

## Simboli orfani (top 15)

- `DoganeSignals` (classe) in `app_desktop.py`
- `ClimaSignals` (classe) in `app_desktop.py`
- `DropAreaGPX` (classe) in `app_desktop.py`
- `GestoreBlocchiWidget` (classe) in `app_desktop.py`
- `BikepackingStudioApp` (classe) in `app_desktop.py`
- `determina_blocco_da_nome_file` (funzione) in `app_desktop.py`
- `carica_blocchi` (funzione) in `app_desktop.py`
- `apri_selettore_file` (funzione) in `app_desktop.py`
- `esegui_backup_progetto` (funzione) in `backup.py`
- `WizardNuovoPercorsoDialog` (classe) in `gui/dashboard.py`
- `carica_tappe_progetto` (funzione) in `gui/dashboard.py`
- `BarraSuperfici` (classe) in `gui/mappa.py`
- `MapManagerDialog` (classe) in `gui/mappa.py`
- `PannelloPianificazioneWidget` (classe) in `gui/mappa.py`
- `WorkerAnalisiSuperficiOffline` (classe) in `gui/mappa.py`
- ... e altri 41 (vedi report completo)

## Duplicazioni rilevate

*14 funzioni/metodi definiti in più file:*

- `calcola_distanza_haversine` (4 copie) → `app_desktop.py`, `gui/dashboard.py`, `service/audit_service.py`, `service/gpx_metrics_service.py`
- `init_ui` (3 copie) → `app_desktop.py`, `gui/dashboard.py`, `gui/wizard_percorso.py`
- `carica_lista_percorsi` (2 copie) → `app_desktop.py`, `gui/dashboard.py`
- `apri_percorso_selezionato` (2 copie) → `app_desktop.py`, `gui/dashboard.py`
- `crea_nuovo_progetto_dialog` (2 copie) → `app_desktop.py`, `gui/dashboard.py`
- `elabora_files_gpx` (2 copie) → `app_desktop.py`, `gui/dashboard.py`
- `aggiorna_tabella_tappe` (2 copie) → `app_desktop.py`, `gui/dashboard.py`
- `aggiorna_blocco_tappa` (2 copie) → `app_desktop.py`, `gui/dashboard.py`
- `toggle_pausa_tappa` (2 copie) → `app_desktop.py`, `gui/dashboard.py`
- `cambia_ruolo_tappa` (2 copie) → `app_desktop.py`, `gui/dashboard.py`
- `elimina_singola_tappa` (2 copie) → `app_desktop.py`, `gui/dashboard.py`
- `elimina_percorso_corrente` (2 copie) → `app_desktop.py`, `gui/dashboard.py`
- `conferma_creazione` (2 copie) → `gui/dashboard.py`, `gui/wizard_percorso.py`
- `_trova_percorso_gpx` (2 copie) → `service/stats_service.py`, `service/superfici_service.py`

## Database

- Percorso: `data/bikepacking_app.db`
- Numero di tabelle: 17
- `allarmi_percorso`: 27 righe
- `anagrafica_paesi`: 198 righe
- `anagrafica_paesi_mondo`: 12 righe
- `blocchi_ordine`: 23 righe
- `blocchi_stagione`: 18 righe
- `cache_geo_paesi`: 2 righe
- `cache_nomi_luoghi`: 993 righe
- `confini_box`: 11 righe
- `dogane_percorso`: 0 righe
- `dogane_progetto`: 67 righe
- `progetti`: 4 righe
- `progetto_stagione`: 1 righe
- `superfici_tappa`: 992 righe
- `tappa_analisi`: 1 righe
- `tappa_segmenti`: 1 righe
- `tappe`: 994 righe
- `trasferimenti`: 28 righe

## Servizi esterni rilevati

- `http://127.0.0.1:8080/api/map-interactions`
- `http://127.0.0.1:8080/api/set-gpx-data`
- `http://127.0.0.1:8080/map`
- `http://localhost:3000`
- `http://www.topografix.com/GPX/1/1`
- `http://{BROUTER_HOST}:{BROUTER_PORT}`
- `http://{BROUTER_HOST}:{BROUTER_PORT}/brouter`
- `http://{host}:{port}`
- `https://creativecommons.org/licenses/by/4.0/\n`
- `https://download.geonames.org/export/dump/allCountries.zip`
- `https://download.geonames.org/export/dump/alternateNamesV2.zip`
- `https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_center.mbtiles`
- `https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_islands.mbtiles`
- `https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_north.mbtiles`
- `https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_south.mbtiles`
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

- `gui/mappa.py`: 9 classi, 84 funzioni
- `app_desktop.py`: 5 classi, 52 funzioni
- `gui/dashboard.py`: 2 classi, 20 funzioni
- `service/superfici_service.py`: 0 classi, 15 funzioni
- `service/map_server.py`: 0 classi, 14 funzioni
- `service/stats_service.py`: 0 classi, 12 funzioni
- `installa_geonames.py`: 0 classi, 8 funzioni
- `service/gpx_metrics_service.py`: 0 classi, 7 funzioni
- `service/map_manager_service.py`: 2 classi, 4 funzioni
- `service/audit_service.py`: 0 classi, 5 funzioni

## Azioni consigliate

- Rivedere i simboli orfani e decidere se integrarli, rimuoverli o spostarli.
- Prioritizzare i file con score più alto per refactor e verifica.
- Usare PROGETTO_INDEX.json come contesto minimo per ridurre i token richiesti alle IA.

---

*Per approfondire: vedi `analisi.json` (dataset completo) o `report.md` (versione umana).*
