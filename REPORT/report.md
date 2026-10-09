# Analisi tecnica verificabile

Scansione `c68e5bf3741dde1f` · 2026-10-09T20:29:39.639501+00:00 · script 4.1

Documento generato: fatti osservati e limiti dichiarati. Non certifica l’esecuzione dell’app.

## Errori e copertura

Nessun errore di lettura o sintassi Python rilevato nelle fonti incluse.

## Moduli

| File | Area | Righe | Classi | Funzioni | Metodi |
|---|---|---|---|---|---|
| app_desktop.py | strumento_o_avvio | 600 | 1 | 0 | 42 |
| backup.py | strumento_o_avvio | 68 | 0 | 1 | 0 |
| import_clima_mondiale.py | strumento_o_avvio | 147 | 0 | 3 | 0 |
| installa_geonames.py | strumento_o_avvio | 348 | 0 | 8 | 0 |
| database/database_setup.py | database | 172 | 0 | 1 | 0 |
| gui/dashboard.py | interfaccia | 632 | 2 | 0 | 19 |
| gui/dialog_clima_soglie.py | interfaccia | 92 | 1 | 0 | 3 |
| gui/dialog_elenco_paesi.py | interfaccia | 79 | 0 | 1 | 0 |
| gui/dialog_nuovo_progetto.py | interfaccia | 98 | 0 | 1 | 0 |
| gui/dialog_wizard_trasferimento.py | interfaccia | 103 | 0 | 1 | 0 |
| gui/drop_area_gpx.py | interfaccia | 42 | 1 | 0 | 3 |
| gui/mappa.py | interfaccia | 573 | 2 | 0 | 26 |
| gui/mappa_barra_superfici.py | interfaccia | 52 | 1 | 0 | 3 |
| gui/mappa_cache.py | interfaccia | 30 | 1 | 0 | 5 |
| gui/mappa_dettagli.py | interfaccia | 190 | 1 | 0 | 11 |
| gui/mappa_manager.py | interfaccia | 107 | 1 | 0 | 6 |
| gui/mappa_pianificatore.py | interfaccia | 1652 | 1 | 0 | 44 |
| gui/mappa_worker.py | interfaccia | 340 | 4 | 0 | 17 |
| gui/mappa_worker_manager.py | interfaccia | 124 | 1 | 0 | 7 |
| gui/widget_blocchi.py | interfaccia | 125 | 1 | 0 | 6 |
| gui/widget_timeline_catena.py | interfaccia | 93 | 1 | 0 | 3 |
| gui/wizard_percorso.py | interfaccia | 95 | 1 | 0 | 3 |
| gui/worker_clima.py | interfaccia | 117 | 2 | 0 | 6 |
| gui/pagine/controller_clima.py | interfaccia | 552 | 1 | 0 | 23 |
| gui/pagine/pagina_audit.py | interfaccia | 202 | 1 | 1 | 4 |
| gui/pagine/pagina_clima.py | interfaccia | 176 | 1 | 0 | 5 |
| gui/pagine/pagina_dogane.py | interfaccia | 95 | 1 | 0 | 4 |
| gui/pagine/pagina_statistiche.py | interfaccia | 227 | 1 | 1 | 5 |
| gui/pagine/pagina_trasporti.py | interfaccia | 192 | 1 | 2 | 3 |
| gui/pagine/stile_pagina.py | interfaccia | 38 | 0 | 2 | 0 |
| resources/genera_catalogo_sprite.py | strumento_o_avvio | 147 | 0 | 2 | 0 |
| service/__init__.py | servizio | 0 | 0 | 0 | 0 |
| service/audit_service.py | servizio | 351 | 0 | 5 | 0 |
| service/blocchi_ordine_service.py | servizio | 82 | 0 | 2 | 0 |
| service/catena_stagionale_service.py | servizio | 1268 | 0 | 26 | 0 |
| service/clima_estrattore.py | servizio | 438 | 0 | 4 | 0 |
| service/clima_service.py | servizio | 241 | 0 | 4 | 0 |
| service/config.py | servizio | 23 | 0 | 0 | 0 |
| service/costa_service.py | servizio | 331 | 0 | 8 | 0 |
| service/dettagli_rotta_service.py | servizio | 158 | 0 | 13 | 0 |
| service/dogane_service.py | servizio | 133 | 0 | 4 | 0 |
| service/geo_utils.py | servizio | 32 | 0 | 1 | 0 |
| service/geocodifica_offline_service.py | servizio | 194 | 0 | 5 | 0 |
| service/geometria_service.py | servizio | 197 | 0 | 7 | 0 |
| service/geonames_service.py | servizio | 58 | 0 | 1 | 0 |
| service/gpx_metrics_service.py | servizio | 310 | 0 | 7 | 0 |
| service/gpx_paths.py | servizio | 52 | 0 | 2 | 0 |
| service/map_manager_service.py | servizio | 117 | 2 | 0 | 4 |
| service/map_server.py | servizio | 378 | 0 | 13 | 0 |
| service/mappa_dati_service.py | servizio | 375 | 0 | 4 | 0 |
| service/migrazione_catena_stagionale.py | servizio | 102 | 0 | 3 | 0 |
| service/migrazione_clima.py | servizio | 99 | 0 | 2 | 0 |
| service/migrazione_tappa_analisi.py | servizio | 126 | 0 | 3 | 0 |
| service/migrazione_tappa_costa.py | servizio | 109 | 0 | 3 | 0 |
| service/migrazione_tappa_costa_metadati.py | servizio | 110 | 0 | 3 | 0 |
| service/migrazione_tappa_geometrie.py | servizio | 84 | 0 | 3 | 0 |
| service/planning_context_service.py | servizio | 60 | 0 | 3 | 0 |
| service/precalcolo_batch_service.py | servizio | 313 | 0 | 9 | 0 |
| service/precalcolo_service.py | servizio | 461 | 0 | 8 | 0 |
| service/progetti_service.py | servizio | 104 | 0 | 3 | 0 |
| service/punti_service.py | servizio | 179 | 0 | 13 | 0 |
| service/routing_timeout_service.py | servizio | 93 | 0 | 2 | 0 |
| service/salvataggio_tappa_service.py | servizio | 580 | 0 | 7 | 0 |
| service/sprite_bandiere_service.py | servizio | 89 | 0 | 4 | 0 |
| service/stats_service.py | servizio | 768 | 0 | 14 | 0 |
| service/suddivisione_percorso_service.py | servizio | 185 | 0 | 6 | 0 |
| service/superfici_service.py | servizio | 506 | 0 | 15 | 0 |
| service/tappe_service.py | servizio | 132 | 0 | 8 | 0 |
| service/trasferimenti_service.py | servizio | 167 | 0 | 4 | 0 |
| service/waypoint_service.py | servizio | 186 | 0 | 5 | 0 |
| static/aggiorna_sprite.py | strumento_o_avvio | 137 | 0 | 1 | 0 |
| tests/test_analisi_profonda.py | test | 223 | 2 | 1 | 20 |
| tests/test_coda_routing.py | test | 141 | 2 | 0 | 8 |
| tests/test_pianificatore_5_1.py | test | 196 | 6 | 0 | 22 |
| tests/test_pianificatore_5_1_gui.py | test | 70 | 1 | 0 | 8 |
| tests/test_pianificatore_5_2.py | test | 217 | 3 | 0 | 14 |
| tests/test_pianificatore_5_3.py | test | 460 | 4 | 0 | 17 |
| tests/test_pianificatore_5_4.py | test | 153 | 2 | 0 | 7 |

## Rotte HTTP dichiarate

Ogni decorator è conservato anche a parità di indirizzo.

| Indirizzo | Metodi | Funzione | Prova |
|---|---|---|---|
| /sprite<path:filename> | GET | serve_sprite | service/map_server.py:49 |
| /fonts/<path:fontstack>/<range_pbf> | GET | serve_fonts | service/map_server.py:208 |
| /api/set-gpx-data | POST | set_gpx_data | service/map_server.py:228 |
| /api/get-gpx-data | GET | get_gpx_data | service/map_server.py:237 |
| /api/tappe/<int:tappa_id>/geometria-completa | GET | get_geometria_completa_tappa | service/map_server.py:243 |
| /api/map-interactions | POST | ricevi_interazione_mappa | service/map_server.py:291 |
| /api/map-interactions | GET | leggi_interazioni_mappa | service/map_server.py:335 |
| /api/maps/list | GET | list_maps | service/map_server.py:350 |
| /map | GET | show_map | service/map_server.py:357 |

## Segnalazioni

Gli indizi non autorizzano cancellazioni automatiche.

| Tipo | Certezza | Simbolo o import | Prova |
|---|---|---|---|
| nessun_riferimento_statico | indizio | DropAreaGPX | gui/drop_area_gpx.py:17 |
| nessun_riferimento_statico | indizio | WizardNuovoPercorso | gui/wizard_percorso.py:7 |
| nessun_riferimento_statico | indizio | registra_trasferimento_gap | service/audit_service.py:223 |
| nessun_riferimento_statico | indizio | applica_semafori | service/catena_stagionale_service.py:1262 |
| nessun_riferimento_statico | indizio | calcola_catena_stagionale | service/clima_service.py:116 |
| nessun_riferimento_statico | indizio | testo_stato_in_modifica | service/dettagli_rotta_service.py:137 |
| nessun_riferimento_statico | indizio | inizializza_tabelle_dogane | service/dogane_service.py:6 |
| nessun_riferimento_statico | indizio | stima_tempo_precalcolo | service/precalcolo_batch_service.py:267 |
| nessun_riferimento_statico | indizio | ottieni_stato_batch | service/precalcolo_batch_service.py:298 |
| nessun_riferimento_statico | indizio | interrompi_batch | service/precalcolo_batch_service.py:304 |
| nessun_riferimento_statico | indizio | ottieni_copertura_precalcolo_progetto | service/stats_service.py:726 |

## Corpi di funzione identici

Confronto AST senza docstring o posizioni; nomi uguali da soli non sono duplicazioni.

- tests/test_coda_routing.py:54 `TestCodaRouting.setUpClass`; tests/test_pianificatore_5_1_gui.py:23 `TestPannelloDettagli.setUpClass`; tests/test_pianificatore_5_3.py:145 `TestInterfacciaSuddivisione.setUpClass`; tests/test_pianificatore_5_4.py:79 `TestGestioneWaypointMappa.setUpClass`
- gui/dashboard.py:427 `DashboardPage.crea_nuovo_progetto_dialog.WizardNuovoPercorsoDialog.__init__`; gui/wizard_percorso.py:8 `WizardNuovoPercorso.__init__`

## Dipendenze interne risolte

| Importatore | Riga | Modulo importato |
|---|---|---|
| app_desktop.py | 5 | service/audit_service.py |
| app_desktop.py | 7 | service/map_server.py |
| app_desktop.py | 12 | gui/dashboard.py |
| app_desktop.py | 13 | gui/mappa.py |
| app_desktop.py | 14 | gui/widget_blocchi.py |
| app_desktop.py | 15 | gui/pagine/controller_clima.py |
| app_desktop.py | 16 | gui/pagine/pagina_clima.py |
| app_desktop.py | 17 | gui/pagine/pagina_statistiche.py |
| app_desktop.py | 18 | gui/pagine/pagina_audit.py |
| app_desktop.py | 19 | gui/pagine/pagina_trasporti.py |
| app_desktop.py | 20 | gui/pagine/pagina_dogane.py |
| app_desktop.py | 21 | gui/dialog_elenco_paesi.py |
| app_desktop.py | 22 | gui/dialog_nuovo_progetto.py |
| app_desktop.py | 23 | gui/dialog_wizard_trasferimento.py |
| app_desktop.py | 24 | service/progetti_service.py |
| app_desktop.py | 25 | service/trasferimenti_service.py |
| app_desktop.py | 29 | database/database_setup.py |
| app_desktop.py | 42 | service/config.py |
| app_desktop.py | 289 | service/stats_service.py |
| installa_geonames.py | 14 | service/config.py |
| installa_geonames.py | 14 | service/config.py |
| gui/dashboard.py | 13 | service/progetti_service.py |
| gui/dashboard.py | 14 | service/tappe_service.py |
| gui/dashboard.py | 15 | service/config.py |
| gui/dashboard.py | 16 | service/gpx_paths.py |
| gui/dashboard.py | 17 | service/precalcolo_service.py |
| gui/dashboard.py | 18 | service/geo_utils.py |
| gui/dialog_elenco_paesi.py | 19 | service/sprite_bandiere_service.py |
| gui/dialog_nuovo_progetto.py | 16 | service/progetti_service.py |
| gui/mappa.py | 16 | service/config.py |
| gui/mappa.py | 17 | service/mappa_dati_service.py |
| gui/mappa.py | 17 | service/mappa_dati_service.py |
| gui/mappa.py | 21 | gui/mappa_pianificatore.py |
| gui/mappa.py | 24 | gui/mappa_cache.py |
| gui/mappa.py | 25 | gui/mappa_dettagli.py |
| gui/mappa.py | 26 | gui/mappa_manager.py |
| gui/mappa.py | 27 | gui/mappa_worker.py |
| gui/mappa.py | 27 | gui/mappa_worker.py |
| gui/mappa.py | 27 | gui/mappa_worker.py |
| gui/mappa.py | 27 | gui/mappa_worker.py |
| gui/mappa.py | 342 | service/config.py |
| gui/mappa.py | 360 | service/config.py |
| gui/mappa.py | 402 | service/config.py |
| gui/mappa_dettagli.py | 13 | gui/mappa_barra_superfici.py |
| gui/mappa_dettagli.py | 14 | service/dettagli_rotta_service.py |
| gui/mappa_dettagli.py | 14 | service/dettagli_rotta_service.py |
| gui/mappa_dettagli.py | 14 | service/dettagli_rotta_service.py |
| gui/mappa_dettagli.py | 14 | service/dettagli_rotta_service.py |
| gui/mappa_dettagli.py | 14 | service/dettagli_rotta_service.py |
| gui/mappa_dettagli.py | 14 | service/dettagli_rotta_service.py |
| gui/mappa_manager.py | 14 | service/map_manager_service.py |
| gui/mappa_manager.py | 14 | service/map_manager_service.py |
| gui/mappa_pianificatore.py | 27 | gui/mappa_dettagli.py |
| gui/mappa_pianificatore.py | 28 | gui/mappa_worker.py |
| gui/mappa_pianificatore.py | 28 | gui/mappa_worker.py |
| gui/mappa_pianificatore.py | 28 | gui/mappa_worker.py |
| gui/mappa_pianificatore.py | 28 | gui/mappa_worker.py |
| gui/mappa_pianificatore.py | 34 | gui/mappa_worker_manager.py |
| gui/mappa_pianificatore.py | 35 | service/config.py |
| gui/mappa_pianificatore.py | 35 | service/config.py |
| gui/mappa_pianificatore.py | 36 | service/dettagli_rotta_service.py |
| gui/mappa_pianificatore.py | 36 | service/dettagli_rotta_service.py |
| gui/mappa_pianificatore.py | 36 | service/dettagli_rotta_service.py |
| gui/mappa_pianificatore.py | 36 | service/dettagli_rotta_service.py |
| gui/mappa_pianificatore.py | 36 | service/dettagli_rotta_service.py |
| gui/mappa_pianificatore.py | 36 | service/dettagli_rotta_service.py |
| gui/mappa_pianificatore.py | 44 | service/geo_utils.py |
| gui/mappa_pianificatore.py | 45 | service/mappa_dati_service.py |
| gui/mappa_pianificatore.py | 45 | service/mappa_dati_service.py |
| gui/mappa_pianificatore.py | 46 | service/planning_context_service.py |
| gui/mappa_pianificatore.py | 46 | service/planning_context_service.py |
| gui/mappa_pianificatore.py | 46 | service/planning_context_service.py |
| gui/mappa_pianificatore.py | 46 | service/planning_context_service.py |
| gui/mappa_pianificatore.py | 52 | service/punti_service.py |
| gui/mappa_pianificatore.py | 52 | service/punti_service.py |
| gui/mappa_pianificatore.py | 52 | service/punti_service.py |
| gui/mappa_pianificatore.py | 52 | service/punti_service.py |
| gui/mappa_pianificatore.py | 52 | service/punti_service.py |
| gui/mappa_pianificatore.py | 52 | service/punti_service.py |
| gui/mappa_pianificatore.py | 52 | service/punti_service.py |
| gui/mappa_pianificatore.py | 52 | service/punti_service.py |
| gui/mappa_pianificatore.py | 52 | service/punti_service.py |
| gui/mappa_pianificatore.py | 52 | service/punti_service.py |
| gui/mappa_pianificatore.py | 52 | service/punti_service.py |
| gui/mappa_pianificatore.py | 65 | service/salvataggio_tappa_service.py |
| gui/mappa_pianificatore.py | 65 | service/salvataggio_tappa_service.py |
| gui/mappa_pianificatore.py | 65 | service/salvataggio_tappa_service.py |
| gui/mappa_pianificatore.py | 70 | service/suddivisione_percorso_service.py |
| gui/mappa_pianificatore.py | 70 | service/suddivisione_percorso_service.py |
| gui/mappa_pianificatore.py | 74 | service/waypoint_service.py |
| gui/mappa_worker.py | 15 | service/config.py |
| gui/mappa_worker.py | 15 | service/config.py |
| gui/mappa_worker.py | 16 | service/geonames_service.py |
| gui/mappa_worker.py | 17 | service/gpx_paths.py |
| gui/mappa_worker.py | 18 | service/routing_timeout_service.py |
| gui/mappa_worker.py | 18 | service/routing_timeout_service.py |
| gui/mappa_worker.py | 58 | service/superfici_service.py |
| gui/mappa_worker.py | 87 | service/geocodifica_offline_service.py |
| gui/mappa_worker.py | 302 | service/stats_service.py |
| gui/widget_blocchi.py | 27 | service/blocchi_ordine_service.py |
| gui/worker_clima.py | 41 | service/clima_estrattore.py |
| gui/pagine/controller_clima.py | 21 | service/catena_stagionale_service.py |
| gui/pagine/controller_clima.py | 22 | service/clima_service.py |
| gui/pagine/controller_clima.py | 23 | service/migrazione_catena_stagionale.py |
| gui/pagine/controller_clima.py | 24 | service/migrazione_clima.py |
| gui/pagine/controller_clima.py | 26 | gui/dialog_clima_soglie.py |
| gui/pagine/controller_clima.py | 27 | gui/pagine/stile_pagina.py |
| gui/pagine/controller_clima.py | 28 | gui/worker_clima.py |
| gui/pagine/controller_clima.py | 29 | service/config.py |
| gui/pagine/pagina_audit.py | 25 | service/config.py |
| gui/pagine/pagina_clima.py | 26 | gui/widget_timeline_catena.py |
| gui/pagine/pagina_clima.py | 28 | gui/pagine/stile_pagina.py |
| gui/pagine/pagina_dogane.py | 18 | service/dogane_service.py |
| gui/pagine/pagina_dogane.py | 20 | gui/pagine/stile_pagina.py |
| gui/pagine/pagina_dogane.py | 20 | gui/pagine/stile_pagina.py |
| gui/pagine/pagina_statistiche.py | 22 | service/stats_service.py |
| gui/pagine/pagina_statistiche.py | 24 | gui/pagine/stile_pagina.py |
| gui/pagine/pagina_statistiche.py | 24 | gui/pagine/stile_pagina.py |
| gui/pagine/pagina_trasporti.py | 25 | service/audit_service.py |
| gui/pagine/pagina_trasporti.py | 26 | service/config.py |
| gui/pagine/pagina_trasporti.py | 28 | gui/pagine/stile_pagina.py |
| gui/pagine/pagina_trasporti.py | 28 | gui/pagine/stile_pagina.py |
| service/audit_service.py | 19 | service/config.py |
| service/audit_service.py | 19 | service/config.py |
| service/audit_service.py | 20 | service/gpx_paths.py |
| service/audit_service.py | 21 | service/geo_utils.py |
| service/audit_service.py | 99 | service/superfici_service.py |
| service/blocchi_ordine_service.py | 13 | service/config.py |
| service/catena_stagionale_service.py | 15 | service/config.py |
| service/catena_stagionale_service.py | 16 | service/migrazione_catena_stagionale.py |
| service/clima_estrattore.py | 22 | service/migrazione_clima.py |
| service/clima_service.py | 4 | service/config.py |
| service/costa_service.py | 12 | service/config.py |
| service/costa_service.py | 12 | service/config.py |
| service/costa_service.py | 130 | service/stats_service.py |
| service/costa_service.py | 130 | service/stats_service.py |
| service/costa_service.py | 130 | service/stats_service.py |
| service/dettagli_rotta_service.py | 3 | service/routing_timeout_service.py |
| service/dogane_service.py | 4 | service/config.py |
| service/geocodifica_offline_service.py | 26 | service/config.py |
| service/geocodifica_offline_service.py | 27 | service/geo_utils.py |
| service/geocodifica_offline_service.py | 30 | service/superfici_service.py |
| service/geocodifica_offline_service.py | 30 | service/superfici_service.py |
| service/geocodifica_offline_service.py | 30 | service/superfici_service.py |
| service/geocodifica_offline_service.py | 30 | service/superfici_service.py |
| service/geonames_service.py | 9 | service/config.py |
| service/gpx_metrics_service.py | 14 | service/geo_utils.py |
| service/gpx_metrics_service.py | 14 | service/geo_utils.py |
| service/map_server.py | 13 | service/config.py |
| service/map_server.py | 13 | service/config.py |
| service/map_server.py | 13 | service/config.py |
| service/map_server.py | 13 | service/config.py |
| service/map_server.py | 14 | service/geometria_service.py |
| service/map_server.py | 14 | service/geometria_service.py |
| service/map_server.py | 14 | service/geometria_service.py |
| service/mappa_dati_service.py | 16 | service/config.py |
| service/mappa_dati_service.py | 17 | service/geometria_service.py |
| service/mappa_dati_service.py | 17 | service/geometria_service.py |
| service/mappa_dati_service.py | 17 | service/geometria_service.py |
| service/mappa_dati_service.py | 22 | service/gpx_paths.py |
| service/planning_context_service.py | 6 | service/config.py |
| service/precalcolo_batch_service.py | 11 | service/config.py |
| service/precalcolo_batch_service.py | 12 | service/gpx_metrics_service.py |
| service/precalcolo_batch_service.py | 13 | service/geometria_service.py |
| service/precalcolo_batch_service.py | 14 | service/costa_service.py |
| service/precalcolo_batch_service.py | 14 | service/costa_service.py |
| service/precalcolo_batch_service.py | 18 | service/precalcolo_service.py |
| service/precalcolo_batch_service.py | 18 | service/precalcolo_service.py |
| service/precalcolo_batch_service.py | 18 | service/precalcolo_service.py |
| service/precalcolo_batch_service.py | 23 | service/gpx_paths.py |
| service/precalcolo_batch_service.py | 287 | service/costa_service.py |
| service/precalcolo_service.py | 14 | service/gpx_metrics_service.py |
| service/precalcolo_service.py | 15 | service/geometria_service.py |
| service/precalcolo_service.py | 15 | service/geometria_service.py |
| service/precalcolo_service.py | 19 | service/costa_service.py |
| service/precalcolo_service.py | 19 | service/costa_service.py |
| service/precalcolo_service.py | 19 | service/costa_service.py |
| service/precalcolo_service.py | 19 | service/costa_service.py |
| service/precalcolo_service.py | 19 | service/costa_service.py |
| service/progetti_service.py | 11 | service/config.py |
| service/routing_timeout_service.py | 84 | service/geo_utils.py |
| service/salvataggio_tappa_service.py | 15 | service/config.py |
| service/salvataggio_tappa_service.py | 15 | service/config.py |
| service/salvataggio_tappa_service.py | 16 | service/gpx_paths.py |
| service/salvataggio_tappa_service.py | 16 | service/gpx_paths.py |
| service/salvataggio_tappa_service.py | 17 | service/precalcolo_service.py |
| service/stats_service.py | 10 | service/config.py |
| service/stats_service.py | 11 | service/gpx_paths.py |
| service/stats_service.py | 12 | service/geo_utils.py |
| service/stats_service.py | 12 | service/geo_utils.py |
| service/stats_service.py | 379 | service/costa_service.py |
| service/stats_service.py | 379 | service/costa_service.py |
| service/stats_service.py | 379 | service/costa_service.py |
| service/stats_service.py | 379 | service/costa_service.py |
| service/stats_service.py | 379 | service/costa_service.py |
| service/stats_service.py | 379 | service/costa_service.py |
| service/stats_service.py | 379 | service/costa_service.py |
| service/stats_service.py | 630 | service/config.py |
| service/suddivisione_percorso_service.py | 5 | service/geo_utils.py |
| service/superfici_service.py | 36 | service/config.py |
| service/superfici_service.py | 36 | service/config.py |
| service/superfici_service.py | 37 | service/gpx_paths.py |
| service/superfici_service.py | 38 | service/geo_utils.py |
| service/tappe_service.py | 11 | service/config.py |
| service/tappe_service.py | 12 | service/gpx_paths.py |
| service/trasferimenti_service.py | 12 | service/config.py |
| service/waypoint_service.py | 6 | service/geo_utils.py |
| tests/test_coda_routing.py | 18 | gui/mappa_worker_manager.py |
| tests/test_pianificatore_5_1.py | 16 | gui/mappa_worker.py |
| tests/test_pianificatore_5_1.py | 16 | gui/mappa_worker.py |
| tests/test_pianificatore_5_1.py | 17 | service/dettagli_rotta_service.py |
| tests/test_pianificatore_5_1.py | 17 | service/dettagli_rotta_service.py |
| tests/test_pianificatore_5_1.py | 17 | service/dettagli_rotta_service.py |
| tests/test_pianificatore_5_1.py | 22 | service/punti_service.py |
| tests/test_pianificatore_5_1.py | 22 | service/punti_service.py |
| tests/test_pianificatore_5_1.py | 23 | service/routing_timeout_service.py |
| tests/test_pianificatore_5_1.py | 23 | service/routing_timeout_service.py |
| tests/test_pianificatore_5_1.py | 23 | service/routing_timeout_service.py |
| tests/test_pianificatore_5_1_gui.py | 16 | gui/mappa_dettagli.py |
| tests/test_pianificatore_5_2.py | 13 | gui/mappa_pianificatore.py |
| tests/test_pianificatore_5_2.py | 14 | service/planning_context_service.py |
| tests/test_pianificatore_5_2.py | 14 | service/planning_context_service.py |
| tests/test_pianificatore_5_2.py | 14 | service/planning_context_service.py |
| tests/test_pianificatore_5_2.py | 14 | service/planning_context_service.py |
| tests/test_pianificatore_5_2.py | 20 | service/punti_service.py |
| tests/test_pianificatore_5_2.py | 21 | service/salvataggio_tappa_service.py |
| tests/test_pianificatore_5_2.py | 22 | service/tappe_service.py |
| tests/test_pianificatore_5_3.py | 13 | gui/mappa_pianificatore.py |
| tests/test_pianificatore_5_3.py | 14 | service/geo_utils.py |
| tests/test_pianificatore_5_3.py | 15 | service/salvataggio_tappa_service.py |
| tests/test_pianificatore_5_3.py | 16 | service/stats_service.py |
| tests/test_pianificatore_5_3.py | 17 | service/suddivisione_percorso_service.py |
| tests/test_pianificatore_5_3.py | 17 | service/suddivisione_percorso_service.py |
| tests/test_pianificatore_5_3.py | 17 | service/suddivisione_percorso_service.py |
| tests/test_pianificatore_5_4.py | 9 | gui/mappa_pianificatore.py |
| tests/test_pianificatore_5_4.py | 10 | service/waypoint_service.py |

## Risorse web

Inventario di HTML, JavaScript e CSS; include librerie distribuite nel repository.

| File | Tipo | Byte |
|---|---|---|
| static/maplibre-gl.css | css | 69430 |
| static/maplibre-gl.js | js | 937395 |
| templates/map_view.html | html | 48313 |

## Documenti di progetto

Inventario, non valutazione del completamento dei piani. ARCHIVIO escluso.

| Documento | Ruolo |
|---|---|
| .clinerules | istruzioni_settore_da_leggere_nello_strumento |
| .github/copilot-instructions.md | istruzioni_settore_da_leggere_nello_strumento |
| AGENTS.md | istruzioni_settore_da_leggere_nello_strumento |
| REPORT/2026-10-06_00-26-21_aider_context.md | contesto_generato_legacy |
| REPORT/ANALISI_CLIMA.md | analisi_storica_da_confrontare_col_codice |
| REPORT/ANALISI_PIANIFICATORE.md | analisi_storica_da_confrontare_col_codice |
| REPORT/FIRST_PRINCIPLES.md | principi_o_regole |
| REPORT/PIANO_CATENA_STAGIONALE.md | piano_non_prova_di_completamento |
| REPORT/PIANO_MIGRAZIONE_GRAPHHOPPER.md | piano_non_prova_di_completamento |
| REPORT/PIANO_PRECALCOLO.md | piano_non_prova_di_completamento |
| REPORT/PIANO_REFACTOR_APP_DESKTOP.md | piano_non_prova_di_completamento |
| REPORT/PIANO_REFACTOR_MAPPA.md | piano_non_prova_di_completamento |
| REPORT/PROGETTO_MAPPE_OFFLINE.md | piano_non_prova_di_completamento |
| REPORT/PROGETTO_PIANIFICATORE.md | piano_non_prova_di_completamento |
| REPORT/REGOLE_GPX.md | principi_o_regole |
| REPORT/VISIONE_CATENA_STAGIONALE.md | visione |
| REPORT/VISIONE_PIANIFICATORE.md | visione |
| STORIA_PROGETTO.md | memoria_storica_da_chat_e_fonti |

## Stato Git locale prima dei report

| Stato | File |
|---|---|
|  M | .clinerules |
|  M | .github/copilot-instructions.md |
|  M | REPORT/AI_BRIEF.md |
|  M | REPORT/CONFIG_FILES.md |
|  M | REPORT/DB_SCHEMA.md |
|  M | REPORT/EXTERNAL_SERVICES.md |
|  M | REPORT/PERCORSO.md |
|  M | REPORT/STATO_ATTUALE.md |
|  M | REPORT/ULTIMO_RUN.json |
|  M | REPORT/analisi.json |
|  M | REPORT/report.md |
|  M | REPORT/riepilogo.txt |
|  M | analisi_profonda.py |
|  M | tests/test_analisi_profonda.py |
| ?? | AGENTS.md |

## Confronto

```json
{
  "disponibile": true,
  "run_precedente": "6dfdd697d454dfb0",
  "aggiunti": [
    "AGENTS.md"
  ],
  "rimossi": [],
  "modificati": [],
  "script_modificato": true,
  "git_head_modificato": false,
  "report_precedenti_modificati_o_mancanti": []
}
```

## Limiti

- Nessun test dell’app eseguito; comportamento runtime non certificato.
- Servizi, server e contenuti R2 non contattati.
- Riferimenti basati su nomi AST: alias, omonimie e uso dinamico limitano la precisione.
- I riferimenti SQL non stabiliscono a quale database appartenga una tabella.
- Decorator HTTP rilevati staticamente: registrazione e prefissi Blueprint non verificati.
- HTML/JS/CSS inventariati, incluse librerie esterne; sintassi e comportamento non verificati.
- Storia, visioni e piani sono fonti documentali, non prove di implementazione.
- Cartelle escluse: .agents, .aws, .codex, .git, .idea, .mypy_cache, .pytest_cache, .venv, .vscode, GPX CORSICA, REPORT, __pycache__, basemap-styles-master, build, data, dist, fonts, gpx, node_modules, venv
