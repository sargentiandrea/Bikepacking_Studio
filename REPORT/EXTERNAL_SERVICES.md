# Servizi esterni rilevati

## Elenco

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

## Riferimenti nel codice e nelle configurazioni

### `paesi_mondo.json`:5
- Riferimento: `redis`
- Contesto: `"nota": "Elenco dei 193 Stati membri ONU più Santa Sede e Stato di Palestina. Le condizioni di ingresso possono cambiare: per un viaggio reale verificare sempre le fonti ufficiali prima della partenza. Versione 2.0: aggiunti campi anagra...`

### `gui/mappa.py`:1436
- Riferimento: `http://127.0.0.1:8080/map`
- Contesto: `self.web_view.setUrl("http://127.0.0.1:8080/map")`

### `gui/mappa.py`:1502
- Riferimento: `http://127.0.0.1:8080/api/map-interactions`
- Contesto: `"http://127.0.0.1:8080/api/map-interactions",`

### `gui/mappa.py`:1695
- Riferimento: `http://127.0.0.1:8080/api/set-gpx-data`
- Contesto: `target=lambda: requests.post("http://127.0.0.1:8080/api/set-gpx-data", json=vuoto, timeout=5),`

### `gui/mappa.py`:2333
- Riferimento: `http://127.0.0.1:8080/api/set-gpx-data`
- Contesto: `requests.post("http://127.0.0.1:8080/api/set-gpx-data", json=payload, timeout=10)`

### `installa_geonames.py`:20
- Riferimento: `https://download.geonames.org/export/dump/allCountries.zip`
- Contesto: `"https://download.geonames.org/export/dump/allCountries.zip",`

### `installa_geonames.py`:25
- Riferimento: `https://download.geonames.org/export/dump/alternateNamesV2.zip`
- Contesto: `"https://download.geonames.org/export/dump/alternateNamesV2.zip",`

### `installa_geonames.py`:325
- Riferimento: `https://creativecommons.org/licenses/by/4.0/\n`
- Contesto: `"https://creativecommons.org/licenses/by/4.0/\n"`

### `installa_geonames.py`:326
- Riferimento: `https://www.geonames.org/\n`
- Contesto: `"https://www.geonames.org/\n"`

### `service/config.py`:9
- Riferimento: `http://{BROUTER_HOST}:{BROUTER_PORT}/brouter`
- Contesto: `BROUTER_URL = f"http://{BROUTER_HOST}:{BROUTER_PORT}/brouter"`

### `service/map_manager_service.py`:17
- Riferimento: `https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_north.mbtiles`
- Contesto: `"url": "https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_north.mbtiles"`

### `service/map_manager_service.py`:25
- Riferimento: `https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_center.mbtiles`
- Contesto: `"url": "https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_center.mbtiles"`

### `service/map_manager_service.py`:33
- Riferimento: `https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_south.mbtiles`
- Contesto: `"url": "https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_south.mbtiles"`

### `service/map_manager_service.py`:41
- Riferimento: `https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_islands.mbtiles`
- Contesto: `"url": "https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_islands.mbtiles"`

### `service/map_server.py`:33
- Riferimento: `martin`
- Contesto: `# Memoria globale per le tracce GPX e il processo di Martin`

### `service/map_server.py`:59
- Riferimento: `martin`
- Contesto: `# --- 3. GESTIONE AUTOMATICA SERVER MARTIN (Rust) ---`

### `service/map_server.py`:63
- Riferimento: `martin`
- Contesto: `martin_exe = os.path.join(BIN_DIR, 'martin.exe' if os.name == 'nt' else 'martin')`

### `service/map_server.py`:66
- Riferimento: `martin`
- Contesto: `print(f"❌ [Martin] Eseguibile non trovato in: {martin_exe}")`

### `service/map_server.py`:86
- Riferimento: `martin`, `http://localhost:3000`
- Contesto: `print("🚀 [Martin] Server di tile vettoriali nativo avviato su http://localhost:3000")`

### `service/map_server.py`:93
- Riferimento: `martin`
- Contesto: `print(f"🗺️ [Martin] {riga}")`

### `service/map_server.py`:98
- Riferimento: `martin`
- Contesto: `print(f"❌ [Martin] Errore durante l'avvio del processo: {e}")`

### `service/map_server.py`:174
- Riferimento: `http://{BROUTER_HOST}:{BROUTER_PORT}`
- Contesto: `f"http://{BROUTER_HOST}:{BROUTER_PORT}"`

### `service/map_server.py`:374
- Riferimento: `http://{host}:{port}`
- Contesto: `print(f"🚀 [MapServer] Server Flask avviato su http://{host}:{port}")`

### `service/stats_service.py`:122
- Riferimento: `http://www.topografix.com/GPX/1/1`
- Contesto: `ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}`
