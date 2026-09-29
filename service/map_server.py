import os
import subprocess
import threading
import urllib.parse
from collections import deque
from flask import Flask, Response, jsonify, render_template, request, send_from_directory, send_file
from flask_cors import CORS

# --- 1. CONFIGURAZIONE E PERCORSI GLOBALI ---
SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SERVICE_DIR, '..'))
MAPS_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, 'data', 'maps'))
BIN_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, 'bin'))
FONTS_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, 'fonts'))

# Memoria globale per le tracce GPX e il processo di Martin
current_gpx_geojson = {"type": "FeatureCollection", "features": []}
martin_process = None
map_interaction_events = deque(maxlen=200)
map_interaction_lock = threading.Lock()
map_interaction_sequence = 0

# --- 2. INIZIALIZZAZIONE FLASK ---
app = Flask(__name__, 
            template_folder=os.path.join(PROJECT_ROOT, 'templates'),
            static_folder=os.path.join(PROJECT_ROOT, 'static'),
            static_url_path='/static')
CORS(app)

@app.route('/sprite<path:filename>')

def serve_sprite(filename):
    # Se per qualche motivo arriva un nome che inizia con il punto (es. .json), lo prefissiamo con 'sprite'
    if filename.startswith('.'):
        filename = 'sprite' + filename
        
    # Ora che abbiamo tutti e 4 i file reali, serviamo direttamente il file richiesto dalla cartella!
    return send_from_directory(PROJECT_ROOT, filename)

# --- 3. GESTIONE AUTOMATICA SERVER MARTIN (Rust) ---

def start_martin_server():
    global martin_process
    martin_exe = os.path.join(BIN_DIR, 'martin.exe' if os.name == 'nt' else 'martin')
    
    if not os.path.exists(martin_exe):
        print(f"❌ [Martin] Eseguibile non trovato in: {martin_exe}")
        return None

    if not os.path.exists(MAPS_DIR):
        os.makedirs(MAPS_DIR, exist_ok=True)

    try:
        cmd = [martin_exe, MAPS_DIR]
        
        # 1. Impostiamo l'ambiente per limitare i log di Rust al livello "warn"
        env_martin = os.environ.copy()
        env_martin["RUST_LOG"] = "warn"

        martin_process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True,
            env=env_martin  # Passiamo l'ambiente configurato
        )
        print("🚀 [Martin] Server di tile vettoriali nativo avviato su http://localhost:3000")
        
        def log_output(process):
            for line in process.stdout:
                riga = line.strip()
                # 2. Stampiamo solo se è un avviso o un errore, filtrando il rumore di fondo dei singoli paesi
                if "WARN" in riga or "ERROR" in riga or "active" in riga:
                    print(f"🗺️ [Martin] {riga}")
                # Se vuoi silenziare totalmente i log normali, basta questo filtro.
                
        threading.Thread(target=log_output, args=(martin_process,), daemon=True).start()
    except Exception as e:
        print(f"❌ [Martin] Errore durante l'avvio del processo: {e}")
                
# --- 4. ROTTA PER I FONT LOCAL PBF (100% OFFLINE CON FALLBACK INTELLIGENTE) ---

@app.route('/fonts/<path:fontstack>/<range_pbf>')
def serve_fonts(fontstack, range_pbf):
    fontstack_decoded = urllib.parse.unquote(fontstack)
    first_font = fontstack_decoded.split(',')[0].strip()
    font_dir = os.path.join(FONTS_DIR, first_font)
    
    if not os.path.exists(font_dir) and os.path.exists(FONTS_DIR):
        subdirs = [d for d in os.listdir(FONTS_DIR) if os.path.isdir(os.path.join(FONTS_DIR, d))]
        if subdirs:
            font_dir = os.path.join(FONTS_DIR, subdirs[0])
    
    if os.path.exists(font_dir):
        file_path = os.path.join(font_dir, range_pbf)
        if os.path.exists(file_path):
            return send_from_directory(font_dir, range_pbf, mimetype='application/x-protobuf')
            
    return Response(b'', status=200, mimetype='application/x-protobuf')

# --- 5. ROTTE API PER LE TRACCE GPX ---

@app.route('/api/set-gpx-data', methods=['POST'])
def set_gpx_data():
    global current_gpx_geojson
    try:
        current_gpx_geojson = request.get_json(force=True)
        return jsonify({"status": "success", "count": len(current_gpx_geojson.get("features", []))})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/get-gpx-data', methods=['GET'])
def get_gpx_data():
    global current_gpx_geojson
    return jsonify(current_gpx_geojson)


@app.route('/api/map-interactions', methods=['POST'])
def ricevi_interazione_mappa():
    """Accoda un waypoint richiesto dall'utente tramite click o drag sulla mappa."""
    global map_interaction_sequence
    payload = request.get_json(silent=True) or {}
    azione = payload.get("action")
    if azione not in {"add_waypoint", "rubberband_waypoint", "cancel_interaction"}:
        return jsonify({"status": "error", "message": "Azione mappa non valida"}), 400

    try:
        id_progetto = int(payload["project_id"])
        if azione == "cancel_interaction":
            latitudine = longitudine = None
            tappa_id = None
        else:
            latitudine = float(payload["lat"])
            longitudine = float(payload["lon"])
            tappa_id = int(payload["tappa_id"]) if payload.get("tappa_id") is not None else None
    except (KeyError, TypeError, ValueError):
        return jsonify({"status": "error", "message": "Coordinate o progetto mancanti"}), 400

    if id_progetto <= 0 or (
        azione != "cancel_interaction"
        and not (-90 <= latitudine <= 90 and -180 <= longitudine <= 180)
    ):
        return jsonify({"status": "error", "message": "Coordinate o progetto fuori intervallo"}), 400
    if azione == "rubberband_waypoint" and tappa_id is None:
        return jsonify({"status": "error", "message": "Tappa da modificare non indicata"}), 400

    with map_interaction_lock:
        map_interaction_sequence += 1
        evento = {
            "id": map_interaction_sequence,
            "action": azione,
            "project_id": id_progetto,
            "tappa_id": tappa_id,
            "lat": latitudine,
            "lon": longitudine,
        }
        map_interaction_events.append(evento)

    return jsonify({"status": "queued", "event_id": evento["id"]}), 202


@app.route('/api/map-interactions', methods=['GET'])
def leggi_interazioni_mappa():
    """Restituisce gli eventi successivi al cursore gestito da MappaWidget."""
    try:
        dopo_id = max(0, int(request.args.get("after", 0)))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Cursore eventi non valido"}), 400

    with map_interaction_lock:
        eventi = [evento for evento in map_interaction_events if evento["id"] > dopo_id]
        ultimo_id = map_interaction_sequence
    return jsonify({"status": "success", "events": eventi, "latest_id": ultimo_id})

# --- 6. ROTTE UTILITÀ E DEBUG ---

@app.route('/api/maps/list')
def list_maps():
    maps = []
    if os.path.exists(MAPS_DIR):
        maps = [os.path.splitext(f)[0] for f in os.listdir(MAPS_DIR) if f.lower().endswith('.mbtiles')]
    return jsonify({"status": "success", "maps_found": maps, "count": len(maps)})

@app.route('/map')
def show_map():
    return render_template('map_view.html')

# --- 7. AVVIO DEL SERVER ---

def run_server(host='127.0.0.1', port=8080):
    start_martin_server()
    # threaded=True evita che una richiesta lenta (es. tile o dati GPX) blocchi
    # le altre richieste in coda, causando i "blocchi" temporanei dell'interfaccia.
    app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)

def start_local_map_server(host='127.0.0.1', port=8080):
    server_thread = threading.Thread(target=run_server, args=(host, port), daemon=True)
    server_thread.start()
    print(f"🚀 [MapServer] Server Flask avviato su http://{host}:{port}")
    return server_thread

if __name__ == '__main__':
    run_server()