import os
import requests
from PySide6.QtCore import QThread, Signal as pyqtSignal

# Cartella di destinazione per i file .mbtiles
MAPS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'maps'))

# Catalogo Strutturato Mappe (Server Privato Cloudflare R2)
# Catalogo Strutturato Mappe Vettoriali Italia (Server Privato Cloudflare R2)
AVAILABLE_MAPS = [
    {
        "id": "italy_north_vector",
        "name": "Italia Nord & Alpi (Zoom 0-14)",
        "region": "Italia",
        "size_mb": 420,
        "description": "Copertura vettoriale ad alta definizione per Arco Alpino, Pianura Padana e Appennino Settentrionale.",
        "url": "https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_north.mbtiles"
    },
    {
        "id": "italy_center_vector",
        "name": "Italia Centro & Appennini (Zoom 0-14)",
        "region": "Italia",
        "size_mb": 310,
        "description": "Mappa vettoriale per Toscana, Umbria, Marche, Lazio e Appennino Abruzzese.",
        "url": "https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_center.mbtiles"
    },
    {
        "id": "italy_south_vector",
        "name": "Italia Sud & Costa Adriatica/Tirrenica (Zoom 0-14)",
        "region": "Italia",
        "size_mb": 260,
        "description": "Copertura vettoriale completa per Campania, Puglia, Basilicata e Calabria.",
        "url": "https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_south.mbtiles"
    },
    {
        "id": "italy_islands_vector",
        "name": "Sardegna e Sicilia Vettoriale (Zoom 0-14)",
        "region": "Italia",
        "size_mb": 280,
        "description": "Dettaglio completo dei sentieri e percorsi bikepacking delle due Isole Maggiori.",
        "url": "https://pub-625e91d94b7f446d86e485da84fabd05.r2.dev/maps/italy_islands.mbtiles"
    }
]

import time

class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, url, destination_path):
        super().__init__()
        self.url = url
        self.destination_path = destination_path

    def run(self):
        if not self.url:
            self.finished.emit(False, "URL di download non ancora configurato per questa regione.")
            return

        try:
            headers = {'User-Agent': 'BikepackingStudio/1.0'}
            response = requests.get(self.url, stream=True, headers=headers, timeout=60, allow_redirects=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            os.makedirs(os.path.dirname(self.destination_path), exist_ok=True)
            temp_path = self.destination_path + ".tmp"

            with open(temp_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=65536):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = int((downloaded / total_size) * 100)
                            self.progress.emit(percent)

            if os.path.exists(self.destination_path):
                os.remove(self.destination_path)
            os.rename(temp_path, self.destination_path)

            self.finished.emit(True, "Mappa scaricata con successo!")
        except requests.exceptions.ConnectionError:
            self.finished.emit(False, "Impossibile connettersi al server. Verifica la connessione internet o le impostazioni del Firewall.")
        except Exception as e:
            self.finished.emit(False, f"Errore durante il download: {str(e)}")

class MapManagerService:
    @staticmethod
    def get_installed_maps():
        """Analizza la cartella data/maps/ e restituisce le mappe presenti su disco"""
        os.makedirs(MAPS_DIR, exist_ok=True)
        files = [f for f in os.listdir(MAPS_DIR) if f.endswith('.mbtiles')]
        installed = []
        for f in files:
            file_path = os.path.join(MAPS_DIR, f)
            size_mb = round(os.path.getsize(file_path) / (1024 * 1024), 2)
            installed.append({"filename": f, "size_mb": size_mb, "path": file_path})
        return installed

    @staticmethod
    def get_available_catalog():
        """Combina il catalogo remoto con lo stato di installazione locale"""
        installed_files = [m["filename"] for m in MapManagerService.get_installed_maps()]
        catalog = []
        for item in AVAILABLE_MAPS:
            # Estrae il nome file reale direttamente dall'URL (es. sardegna.mbtiles)
            expected_filename = item["url"].split("/")[-1]
            catalog.append({
                **item,
                "filename": expected_filename,
                "is_installed": expected_filename in installed_files
            })
        return catalog