# service/config.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(BASE_DIR, "data", "bikepacking_app.db")

BROUTER_HOST = "127.0.0.1"
BROUTER_PORT = 17777
BROUTER_URL = f"http://{BROUTER_HOST}:{BROUTER_PORT}/brouter"

_APP_DATA_DIR = os.environ.get("LOCALAPPDATA") or os.path.join(
    os.path.expanduser("~"), ".local", "share"
)
BROUTER_HOME = os.environ.get(
    "BIKEPACKING_BROUTER_HOME",
    os.path.join(_APP_DATA_DIR, "BikepackingStudio", "brouter", "brouter-1.7.10"),
)

GEONAMES_HOME = os.environ.get(
    "BIKEPACKING_GEONAMES_HOME",
    os.path.join(_APP_DATA_DIR, "BikepackingStudio", "geonames"),
)
GEONAMES_DB = os.path.join(GEONAMES_HOME, "geonames.sqlite")