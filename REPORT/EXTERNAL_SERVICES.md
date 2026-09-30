# Servizi esterni rilevati

## Elenco

- `http://127.0.0.1:8080/api/map-interactions`
- `http://127.0.0.1:8080/api/set-gpx-data`
- `http://127.0.0.1:8080/map`
- `http://localhost:3000`
- `http://router.project-osrm.org/route/v1/biking/`
- `http://www.topografix.com/GPX/1/1`
- `http://{host}:{port}`
- `https://brouter.de/brouter`
- `https://brouter.de/brouter?`
- `https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=it`
- `https://nominatim.openstreetmap.org/search`
- `https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_center.mbtiles`
- `https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_islands.mbtiles`
- `https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_north.mbtiles`
- `https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_south.mbtiles`
- `https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_coastline.geojson`
- `martin`
- `redis`

## Riferimenti nel codice e nelle configurazioni

### `paesi_mondo.json`:5
- Riferimento: `redis`
- Contesto: `"nota": "Elenco dei 193 Stati membri ONU più Santa Sede e Stato di Palestina. Le condizioni di ingresso possono cambiare: per un viaggio reale verificare sempre le fonti ufficiali prima della partenza. Versione 2.0: aggiunti campi anagra...`

### `app_desktop.py`:98
- Riferimento: `https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=it`
- Contesto: `url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=it"`

### `gui/mappa.py`:1358
- Riferimento: `http://127.0.0.1:8080/map`
- Contesto: `self.web_view.setUrl("http://127.0.0.1:8080/map")`

### `gui/mappa.py`:1424
- Riferimento: `http://127.0.0.1:8080/api/map-interactions`
- Contesto: `"http://127.0.0.1:8080/api/map-interactions",`

### `gui/mappa.py`:1561
- Riferimento: `http://127.0.0.1:8080/api/set-gpx-data`
- Contesto: `target=lambda: requests.post("http://127.0.0.1:8080/api/set-gpx-data", json=vuoto, timeout=5),`

### `gui/mappa.py`:1781
- Riferimento: `https://nominatim.openstreetmap.org/search`
- Contesto: `"https://nominatim.openstreetmap.org/search",`

### `gui/mappa.py`:1819
- Riferimento: `https://brouter.de/brouter`
- Contesto: `"https://brouter.de/brouter",`

### `gui/mappa.py`:1996
- Riferimento: `http://127.0.0.1:8080/api/set-gpx-data`
- Contesto: `requests.post("http://127.0.0.1:8080/api/set-gpx-data", json=payload, timeout=10)`

### `service/audit_service.py`:196
- Riferimento: `https://brouter.de/brouter?`
- Contesto: `f"https://brouter.de/brouter?"`

### `service/audit_service.py`:213
- Riferimento: `http://router.project-osrm.org/route/v1/biking/`
- Contesto: `f"http://router.project-osrm.org/route/v1/biking/"`

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

### `service/map_server.py`:16
- Riferimento: `martin`
- Contesto: `# Memoria globale per le tracce GPX e il processo di Martin`

### `service/map_server.py`:40
- Riferimento: `martin`
- Contesto: `# --- 3. GESTIONE AUTOMATICA SERVER MARTIN (Rust) ---`

### `service/map_server.py`:44
- Riferimento: `martin`
- Contesto: `martin_exe = os.path.join(BIN_DIR, 'martin.exe' if os.name == 'nt' else 'martin')`

### `service/map_server.py`:47
- Riferimento: `martin`
- Contesto: `print(f"❌ [Martin] Eseguibile non trovato in: {martin_exe}")`

### `service/map_server.py`:67
- Riferimento: `martin`, `http://localhost:3000`
- Contesto: `print("🚀 [Martin] Server di tile vettoriali nativo avviato su http://localhost:3000")`

### `service/map_server.py`:74
- Riferimento: `martin`
- Contesto: `print(f"🗺️ [Martin] {riga}")`

### `service/map_server.py`:79
- Riferimento: `martin`
- Contesto: `print(f"❌ [Martin] Errore durante l'avvio del processo: {e}")`

### `service/map_server.py`:199
- Riferimento: `http://{host}:{port}`
- Contesto: `print(f"🚀 [MapServer] Server Flask avviato su http://{host}:{port}")`

### `service/stats_service.py`:14
- Riferimento: `https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_coastline.geojson`
- Contesto: `COASTLINE_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_coastline.geojson"`

### `service/stats_service.py`:127
- Riferimento: `http://www.topografix.com/GPX/1/1`
- Contesto: `ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}`
