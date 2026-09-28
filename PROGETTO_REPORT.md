# Progetto: analisi architetturale

- Moduli Python: 20
- Classi: 15
- Funzioni: 136
- Rotte Flask: 6
- Tabelle rilevate: 11
- Simboli orfani: 89

## Struttura architetturale
- ui: gui/dashboard.py, gui/mappa.py, gui/wizard_percorso.py
- database: database/database_setup.py
- api: service/map_server.py
- core: service/__init__.py, service/audit_service.py, service/clima_service.py, service/config.py, service/dogane_service.py ...
- altro: agente_locale.py, analizzatore_progetto.py, app_desktop.py, backup.py, basemap-styles-master/mapboxgl/styler.py ...

## Endpoint backend
- /sprite<path:filename> -> serve_sprite (GET)
- /fonts/<path:fontstack>/<range_pbf> -> serve_fonts (GET)
- /api/set-gpx-data -> set_gpx_data (POST)
- /api/get-gpx-data -> get_gpx_data (GET)
- /api/maps/list -> list_maps (GET)
- /map -> show_map (GET)

## Frontend & mappe
- Endpoint frontend usati: /api/get-gpx-data, /api/maps/list, http://127.0.0.1:8080/fonts/{fontstack}/{range}.pbf, http://127.0.0.1:8080/static/sprite
- Librerie: /static/maplibre-gl.js

## Simboli orfani
- funzione: chiedi_all_agente (agente_locale.py)
- funzione: analizza_progetto (analizzatore_progetto.py)
- classe: DoganeSignals (app_desktop.py)
- classe: ClimaSignals (app_desktop.py)
- classe: LocalMapServer (app_desktop.py)
- classe: DropAreaGPX (app_desktop.py)
- classe: GestoreBlocchiWidget (app_desktop.py)
- classe: BikepackingStudioApp (app_desktop.py)
- funzione: determina_blocco_da_nome_file (app_desktop.py)
- funzione: ottieni_nome_localita (app_desktop.py)
- funzione: start_server (app_desktop.py)
- funzione: dragEnterEvent (app_desktop.py)
- funzione: dropEvent (app_desktop.py)
- funzione: carica_blocchi (app_desktop.py)
- funzione: sposta_su (app_desktop.py)
- funzione: sposta_giu (app_desktop.py)
- funzione: applica_riordinamento (app_desktop.py)
- funzione: gestisci_cambio_progetto (app_desktop.py)
- funzione: crea_bottone_navigazione (app_desktop.py)
- funzione: crea_pagina_mappa (app_desktop.py)

## Moduli con più segnali
- app_desktop.py: 6 classi, 46 funzioni
- gui/dashboard.py: 2 classi, 20 funzioni
- gui/mappa.py: 4 classi, 18 funzioni
- service/stats_service.py: 0 classi, 12 funzioni
- service/map_server.py: 0 classi, 10 funzioni
- service/map_manager_service.py: 2 classi, 4 funzioni
- gui/wizard_percorso.py: 1 classi, 3 funzioni
- service/audit_service.py: 0 classi, 4 funzioni
- service/clima_service.py: 0 classi, 4 funzioni
- service/dogane_service.py: 0 classi, 4 funzioni

## Insight per agente IA
- Livello di rischio: alto
- File critici: app_desktop.py, gui/dashboard.py, gui/mappa.py
- Entry point probabili: main, run
- Azione: Rivedere i simboli orfani e decidere se integrarli, rimuoverli o spostarli in moduli più appropriati.
- Azione: Priorizzare i file con score più alto per refactor e verifica di coerenza architetturale.
- Azione: Usare il JSON di analisi come contesto minimo per future modifiche e per ridurre il numero di token richiesti ai tool AI.

## Brano operativo per aider / agente AI
- Priorità: app_desktop.py, gui/dashboard.py, gui/mappa.py
- Prompt: Analizza il progetto usando il dataset di PROGETTO_INDEX.json. Priorità massima ai file critici e ai simboli orfani, poi verifica rotti o duplicati. Propone un refactor minimo ma sicuro e documenta le modifiche.
- 1. Valutazione rapida: app_desktop.py, gui/mappa.py, gui/dashboard.py
- 2. Consolidamento architettura: service/stats_service.py, service/map_server.py, gui/wizard_percorso.py
- 3. Stabilizzazione e refactor: service/map_manager_service.py, service/audit_service.py, service/clima_service.py, resources/genera_catalogo_sprite.py, service/dogane_service.py, analizzatore_progetto.py, backup.py, agente_locale.py, basemap-styles-master/mapboxgl/styler.py, export_structure.py, static/aggiorna_sprite.py, database/database_setup.py, service/config.py, service/__init__.py

## Prompt ultra-compatto
Progetto: Bikepacking_Studio. Contesto: 20 moduli, 15 classi, 136 funzioni, 6 endpoint Flask, 89 simboli orfani. Rischio: alto. File critici: app_desktop.py, gui/dashboard.py, gui/mappa.py. Priorità: correggere simboli orfani, verificare file critici e consolidare dipendenze. Usa PROGETTO_INDEX.json come fonte di verità e minimizza i cambiamenti.
