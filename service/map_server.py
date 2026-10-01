import os
import shutil
import socket
import sqlite3
import subprocess
import threading
import time
import urllib.parse
from collections import deque
from flask import Flask, Response, jsonify, render_template, request, send_from_directory, send_file
from flask_cors import CORS

from service.config import BROUTER_HOME, BROUTER_HOST, BROUTER_PORT, DB_NAME
from service.geometria_service import (
    VERSIONE_ALGORITMO_GEOMETRIA,
    decomprimi_segmenti,
    geometria_geojson,
)

# --- 1. CONFIGURAZIONE E PERCORSI GLOBALI ---
SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SERVICE_DIR, '..'))
MAPS_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, 'data', 'maps'))
BIN_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, 'bin'))
FONTS_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, 'fonts'))
BROUTER_SEGMENTS_DIR = os.path.join(BROUTER_HOME, "segments4")
BROUTER_DATA_MARKER = os.path.join(BROUTER_SEGMENTS_DIR, ".world-data-complete")
BROUTER_JAR = os.path.join(BROUTER_HOME, "brouter-1.7.10-all.jar")
BROUTER_PROFILES_DIR = os.path.join(BROUTER_HOME, "profiles2")
BROUTER_LIB_DIR = os.path.join(BROUTER_HOME, "lib")
BROUTER_CUSTOM_PROFILES_DIR = os.path.join(BROUTER_HOME, "customprofiles")

# Memoria globale per le tracce GPX e il processo di Martin
current_gpx_geojson = {"type": "FeatureCollection", "features": []}
martin_process = None
brouter_process = None
brouter_start_lock = threading.Lock()
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


def start_brouter_server():
    """Avvia il routing BRouter locale usando i segmenti già installati."""
    global brouter_process
    with brouter_start_lock:
        if brouter_process is not None and brouter_process.poll() is None:
            return brouter_process

        try:
            with socket.create_connection((BROUTER_HOST, BROUTER_PORT), timeout=0.2):
                print(f"[BRouter] Servizio locale già attivo su {BROUTER_HOST}:{BROUTER_PORT}")
                return None
        except OSError:
            pass

        java_exe = shutil.which("java")
        if not java_exe:
            print("[BRouter] ERRORE: Java non trovato; necessario per il routing offline.")
            return None
        if not os.path.isfile(BROUTER_JAR):
            print(f"[BRouter] ERRORE: programma non trovato: {BROUTER_JAR}")
            return None
        if not os.path.isfile(BROUTER_DATA_MARKER):
            print(
                "[BRouter] ERRORE: dati routing globali assenti o incompleti; "
                "manca il marcatore di installazione verificata."
            )
            return None
        if (
            not os.path.isdir(BROUTER_LIB_DIR)
            or not os.path.isfile(os.path.join(BROUTER_PROFILES_DIR, "trekking.brf"))
            or not os.path.isfile(os.path.join(BROUTER_PROFILES_DIR, "fastbike.brf"))
        ):
            print(f"[BRouter] ERRORE: profili o librerie mancanti in: {BROUTER_HOME}")
            return None

        os.makedirs(BROUTER_CUSTOM_PROFILES_DIR, exist_ok=True)
        classpath = os.pathsep.join((
            BROUTER_JAR,
            os.path.join(BROUTER_LIB_DIR, "*"),
        ))
        comando = [
            java_exe,
            "-Xmx512M",
            "-DmaxRunningTime=300",
            "-cp",
            classpath,
            "btools.server.RouteServer",
            BROUTER_SEGMENTS_DIR,
            BROUTER_PROFILES_DIR,
            BROUTER_CUSTOM_PROFILES_DIR,
            str(BROUTER_PORT),
            "2",
            BROUTER_HOST,
        ]

        try:
            brouter_process = subprocess.Popen(
                comando,
                cwd=BROUTER_HOME,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except OSError as errore:
            print(f"[BRouter] ERRORE: avvio del router locale non riuscito: {errore}")
            brouter_process = None
            return None

        print(
            f"[BRouter] Routing offline in avvio su "
            f"http://{BROUTER_HOST}:{BROUTER_PORT}"
        )

        def log_output(process):
            for line in process.stdout:
                riga = line.strip()
                if riga:
                    print(f"[BRouter] {riga.encode('ascii', 'replace').decode('ascii')}")

        threading.Thread(
            target=log_output,
            args=(brouter_process,),
            daemon=True,
        ).start()

        scadenza = time.monotonic() + 15
        while time.monotonic() < scadenza:
            if brouter_process.poll() is not None:
                print("[BRouter] ERRORE: il processo locale si è chiuso durante l'avvio.")
                return None
            try:
                with socket.create_connection(
                    (BROUTER_HOST, BROUTER_PORT), timeout=0.25
                ):
                    print("[BRouter] Router locale pronto.")
                    return brouter_process
            except OSError:
                time.sleep(0.25)

        print("[BRouter] ATTENZIONE: avvio lento; il servizio non risponde ancora.")
        return brouter_process
                
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


@app.route('/api/tappe/<int:tappa_id>/geometria-completa', methods=['GET'])
def get_geometria_completa_tappa(tappa_id):
    """Restituisce la geometria completa solo per la tappa richiesta."""
    try:
        with sqlite3.connect(DB_NAME) as connessione:
            record = connessione.execute(
                """
                SELECT geometria.geometria_completa,
                       geometria.bbox_min_lon, geometria.bbox_min_lat,
                       geometria.bbox_max_lon, geometria.bbox_max_lat
                FROM tappa_geometrie AS geometria
                JOIN tappa_analisi AS analisi
                  ON analisi.tappa_id = geometria.tappa_id
                 AND analisi.gpx_sha256 = geometria.gpx_sha256
                WHERE geometria.tappa_id = ?
                  AND geometria.versione_algoritmo = ?
                """,
                (tappa_id, VERSIONE_ALGORITMO_GEOMETRIA),
            ).fetchone()
    except sqlite3.Error as errore:
        app.logger.exception(
            "Lettura geometria completa fallita per la tappa %s", tappa_id
        )
        return jsonify({"status": "error", "message": str(errore)}), 503

    if record is None:
        return jsonify(
            {"status": "error", "message": "Geometria completa non disponibile"}
        ), 404

    try:
        segmenti = decomprimi_segmenti(record[0])
        geometria = geometria_geojson(segmenti)
    except (OSError, ValueError, TypeError) as errore:
        app.logger.exception(
            "Geometria completa non valida per la tappa %s", tappa_id
        )
        return jsonify({"status": "error", "message": str(errore)}), 500

    return jsonify(
        {
            "status": "success",
            "geometry": geometria,
            "bbox": [record[1], record[2], record[3], record[4]],
        }
    )


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
    start_brouter_server()
    # threaded=True evita che una richiesta lenta (es. tile o dati GPX) blocchi
    # le altre richieste in coda, causando i "blocchi" temporanei dell'interfaccia.
    app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)

def start_local_map_server(host='127.0.0.1', port=8080):
    start_brouter_server()
    server_thread = threading.Thread(target=run_server, args=(host, port), daemon=True)
    server_thread.start()
    print(f"🚀 [MapServer] Server Flask avviato su http://{host}:{port}")
    return server_thread

if __name__ == '__main__':
    run_server()