# Endpoint osservati nel sorgente Python

Scansione `c68e5bf3741dde1f` · 2026-10-09T20:29:39.639501+00:00 · script 4.1

Documento generato: fatti osservati e limiti dichiarati. Non certifica l’esecuzione dell’app.

Nessun servizio contattato. Una URL non prova una connessione o un servizio disponibile.
Credenziali URL, query e frammenti omessi. Parole come redis o Martin non sono prove di servizi.

| Endpoint | Ambito | Origine | Prova |
|---|---|---|---|
| https://download.geonames.org/export/dump/allCountries.zip | remoto | stringa; non prova connessione | installa_geonames.py:20 |
| https://download.geonames.org/export/dump/alternateNamesV2.zip | remoto | stringa; non prova connessione | installa_geonames.py:25 |
| https://creativecommons.org/licenses/by/4.0/ | remoto | stringa; non prova connessione | installa_geonames.py:322 |
| https://www.geonames.org/ | remoto | stringa; non prova connessione | installa_geonames.py:322 |
| http://127.0.0.1:8080/map | locale | argomento di chiamata setUrl | gui/mappa.py:92 |
| http://127.0.0.1:8080/map | locale | stringa; non prova connessione | gui/mappa.py:92 |
| http://127.0.0.1:8080/api/map-interactions | locale | argomento di chiamata get | gui/mappa.py:210 |
| http://127.0.0.1:8080/api/map-interactions | locale | stringa; non prova connessione | gui/mappa.py:211 |
| http://127.0.0.1:8080/api/set-gpx-data | locale | argomento di chiamata post | gui/mappa.py:431 |
| http://127.0.0.1:8080/api/set-gpx-data | locale | stringa; non prova connessione | gui/mappa.py:431 |
| http://127.0.0.1:8080/api/set-gpx-data | locale | argomento di chiamata post | gui/mappa.py:564 |
| http://127.0.0.1:8080/api/set-gpx-data | locale | stringa; non prova connessione | gui/mappa.py:564 |
| https://os.unil.cloud.switch.ch/chelsa02 | remoto | stringa; non prova connessione | service/clima_estrattore.py:25 |
| https://www.chelsa-climate.org/datasets/chelsa_monthly | remoto | stringa; non prova connessione | service/clima_estrattore.py:26 |
| http://s3.amazonaws.com/doc/2006-03-01/ | remoto | stringa; non prova connessione | service/clima_estrattore.py:30 |
| http://{dinamico}:{dinamico}/brouter | parametrizzato | stringa parametrizzata | service/config.py:9 |
| https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_north.mbtiles | remoto | stringa; non prova connessione | service/map_manager_service.py:17 |
| https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_center.mbtiles | remoto | stringa; non prova connessione | service/map_manager_service.py:25 |
| https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_south.mbtiles | remoto | stringa; non prova connessione | service/map_manager_service.py:33 |
| https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_islands.mbtiles | remoto | stringa; non prova connessione | service/map_manager_service.py:41 |
| http://localhost:3000 | locale | stringa; non prova connessione | service/map_server.py:86 |
| http://www.topografix.com/GPX/1/1 | remoto | stringa; non prova connessione | service/stats_service.py:118 |
| https://example.org/maps | remoto | stringa; non prova connessione | tests/test_analisi_profonda.py:107 |
| https://example.org/maps | remoto | stringa; non prova connessione | tests/test_analisi_profonda.py:108 |
