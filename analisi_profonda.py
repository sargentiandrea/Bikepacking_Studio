# ============================================================
# analisi_profonda.py
# ------------------------------------------------------------
# Ispettore automatico del progetto Bikepacking_Studio.
#
# Cosa fa, in parole semplici:
#   1. Cammina in tutte le cartelle del progetto (tranne quelle escluse)
#   2. Apre ogni file Python e capisce classi, funzioni, import, rotte, SQL
#   3. Analizza anche HTML, JS, CSS
#   4. Trova simboli "orfani" (definiti ma mai usati) - senza falsi positivi
#   5. Calcola un livello di rischio e propone un piano d'azione
#   6. Aggiorna i report correnti nella cartella REPORT/
#   7. Salva ULTIMO_RUN.json per le analisi successive
#   8. Analizza database, configurazioni e servizi esterni
#
# Come si usa:
#   Doppio click su analisi_profonda.bat (sul Desktop)
#   oppure, da terminale, dentro la cartella del progetto:
#       python analisi_profonda.py
# ============================================================

import ast
import json
import os
import re
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Forza stdout/stderr in UTF-8 (evita problemi con lettere accentate)
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# ------------------------------------------------------------
# COSTANTI DI CONFIGURAZIONE
# ------------------------------------------------------------

# Cartelle da NON analizzare mai (dati, ambiente, cache, git)
CARTELLE_ESCLUSE = {
    ".git", "__pycache__", "venv", ".venv", ".idea",
    ".mypy_cache", ".pytest_cache", "build", "dist",
    "node_modules", ".vscode", "REPORT",           # non analizzare i nostri stessi report
    "basemap-styles-master",                        # cartella esterna pesante
    "data", "fonts", "gpx",                         # dati, non codice
}

NOMI_FILE_CONFIGURAZIONE = {
    "requirements.txt", "package.json", "pyproject.toml",
    "setup.py", "setup.cfg",
}

ESTENSIONI_CONFIGURAZIONE = {".json", ".yaml", ".yml", ".ini", ".cfg"}
DIMENSIONE_MASSIMA_CONFIG = 100_000
LUNGHEZZA_MASSIMA_ESTRATTO_CONFIG = 20_000

KEYWORD_SERVIZI_ESTERNI = {
    "martin": r"(?<!\w)martin(?!\w)",
    "tileserver": r"tileserver",
    "tile_server": r"tile_server",
    "osmium": r"(?<!\w)osmium(?!\w)",
    "ogr2ogr": r"ogr2ogr",
    "gdal": r"(?<!\w)gdal(?!\w)",
    "docker": r"docker",
    "docker-compose": r"docker[-_]compose",
    "nginx": r"nginx",
    "apache": r"apache",
    "uwsgi": r"uwsgi",
    "gunicorn": r"gunicorn",
    "redis": r"redis",
    "postgres": r"postgres",
    "postgis": r"postgis",
}

REGEX_URL = re.compile(r"https?://[^\s\"'<>),]+", re.IGNORECASE)

# Prefissi che indicano moduli interni al progetto
# (usati solo come fallback: la fonte di verità è la lista dei file .py reali)
PREFISSI_INTERNI_FALLBACK = (
    "gui", "service", "database", "db", "model", "core",
    "api", "routes", "app", "src", "utils", "helpers",
)

# Framework noti: se troviamo import di questi, segnaliamo anomalia
FRAMEWORK_NOTI = ("PyQt5", "PyQt6", "PySide2", "PySide6", "tkinter", "flask", "fastapi", "django")

# Framework UI richiesto dal progetto (verrà segnalato se ne troviamo altri)
FRAMEWORK_UI_RICHIESTO = "PySide6"
FRAMEWORK_UI_VIETATI = ("PyQt5", "PyQt6", "PySide2", "tkinter")

# Nomi di funzioni/metodi che NON devono mai essere considerati "orfani"
# (callback di framework, entry point, metodi magici, metodi Qt comuni)
NOMI_SEMPRE_USATI = {
    # entry point
    "main", "run", "start", "app", "salva", "carica", "init", "init_ui", "setup_ui",
    # metodi magici Python
    "__init__", "__main__", "__str__", "__repr__", "__eq__", "__hash__",
    "__enter__", "__exit__", "__iter__", "__next__", "__len__", "__getitem__",
    "__setitem__", "__delitem__", "__contains__", "__call__", "__bool__",
    # callback Qt più comuni (li chiama Qt, non il tuo codice)
    "closeEvent", "showEvent", "hideEvent", "paintEvent", "resizeEvent",
    "mousePressEvent", "mouseReleaseEvent", "mouseMoveEvent",
    "keyPressEvent", "keyReleaseEvent", "wheelEvent",
    "dragEnterEvent", "dragMoveEvent", "dragLeaveEvent", "dropEvent",
    "focusInEvent", "focusOutEvent", "changeEvent", "contextMenuEvent",
    "enterEvent", "leaveEvent", "moveEvent", "timerEvent",
    "on_click", "on_change", "on_submit", "on_select", "on_close",
    "cliccato", "premuto", "selezionato", "aggiorna", "refresh",
}

# Suffissi che indicano un callback/slot/handler (probabilmente chiamati da un framework)
SUFFISSI_CALLBACK = (
    "Event", "Slot", "Signal", "Handler", "Callback", "Listener",
    "_clicked", "_changed", "_pressed", "_released", "_toggled",
)

# Nome dell'ultimo snapshot
NOME_ULTIMO_SNAPSHOT = "ULTIMO_RUN.json"

FILE_REPORT_SEMPRE_PRESENTI = {
    "AI_BRIEF.md",
    "analisi.json",
    "report.md",
    "riepilogo.txt",
    "DB_SCHEMA.md",
    "CONFIG_FILES.md",
    "EXTERNAL_SERVICES.md",
    NOME_ULTIMO_SNAPSHOT,
}

FILE_REPORT_OBSOLETI = {"CHANGELOG.md", "prompt_agente.md"}


# ------------------------------------------------------------
# FUNZIONI DI SUPPORTO
# ------------------------------------------------------------

def normalizza_nome(nome):
    """Pulisce un nome rimuovendo caratteri strani."""
    return re.sub(r"[^a-zA-Z0-9_]", "", nome or "")


def riassunto_docstring(docstring):
    """Prende la prima frase della docstring, max 120 caratteri."""
    if not docstring:
        return ""
    frase = docstring.strip().split(".")[0].strip()
    return frase[:120] if frase else ""


def leggi_file(percorso):
    """Legge un file di testo. Restituisce None se non riesce."""
    try:
        with open(percorso, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().lstrip("\ufeff")
    except Exception:
        return None


def timestamp_leggibile():
    """Restituisce una stringa tipo 2026-09-29_14-30-05 (adatta a nomi file)."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def assicura_cartella(percorso):
    """Crea una cartella se non esiste."""
    os.makedirs(percorso, exist_ok=True)


def _percorso_relativo(percorso, root_dir):
    """Restituisce un percorso relativo al progetto con separatori uniformi."""
    return os.path.relpath(percorso, root_dir).replace("\\", "/")


def analizza_database_sqlite(percorso_db):
    """Legge schema e conteggi del database senza consentire modifiche."""
    risultato = {"percorso": percorso_db.replace("\\", "/"), "errore": None, "tabelle": []}
    if not os.path.isfile(percorso_db):
        risultato["errore"] = f"Database non trovato: {percorso_db}"
        return risultato

    connessione = None
    try:
        uri_lettura = f"{Path(percorso_db).resolve().as_uri()}?mode=ro"
        connessione = sqlite3.connect(uri_lettura, uri=True)
        cursore = connessione.cursor()
        nomi_tabelle = [
            riga[0] for riga in cursore.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]

        for nome_tabella in nomi_tabelle:
            nome_sql = nome_tabella.replace('"', '""')
            tabella = {
                "nome": nome_tabella,
                "righe": None,
                "errore_conteggio": None,
                "colonne": [],
                "indici": [],
                "chiavi_esterne": [],
            }
            try:
                cursore.execute(f'PRAGMA table_info("{nome_sql}")')
                colonne = cursore.fetchall()
                indici_unici = set()
                cursore.execute(f'PRAGMA index_list("{nome_sql}")')
                for indice in cursore.fetchall():
                    nome_indice, univoco = indice[1], indice[2]
                    cursore.execute(f'PRAGMA index_info("{nome_indice.replace(chr(34), chr(34) * 2)}")')
                    colonne_indice = [dettaglio[2] for dettaglio in cursore.fetchall()]
                    tabella["indici"].append({
                        "nome": nome_indice,
                        "univoco": bool(univoco),
                        "colonne": colonne_indice,
                    })
                    if univoco and len(colonne_indice) == 1:
                        indici_unici.update(colonna for colonna in colonne_indice if colonna)

                for colonna in colonne:
                    _, nome, tipo, not_null, valore_default, chiave_primaria = colonna
                    vincoli = []
                    if chiave_primaria:
                        vincoli.append("chiave primaria")
                    if not_null:
                        vincoli.append("NOT NULL")
                    if nome in indici_unici:
                        vincoli.append("UNIQUE")
                    if valore_default is not None:
                        vincoli.append(f"DEFAULT {valore_default}")
                    tabella["colonne"].append({
                        "nome": nome,
                        "tipo": tipo or "non specificato",
                        "vincoli": vincoli,
                    })

                cursore.execute(f'PRAGMA foreign_key_list("{nome_sql}")')
                for chiave in cursore.fetchall():
                    tabella["chiavi_esterne"].append({
                        "colonna": chiave[3],
                        "tabella_riferita": chiave[2],
                        "colonna_riferita": chiave[4],
                        "azione_update": chiave[5],
                        "azione_delete": chiave[6],
                    })

                cursore.execute(f'SELECT COUNT(*) FROM "{nome_sql}"')
                tabella["righe"] = cursore.fetchone()[0]
            except sqlite3.Error as errore:
                tabella["errore_conteggio"] = str(errore)
            risultato["tabelle"].append(tabella)
    except (sqlite3.Error, OSError, ValueError) as errore:
        risultato["errore"] = f"Impossibile leggere il database in sola lettura: {errore}"
    finally:
        if connessione is not None:
            connessione.close()
    return risultato


def trova_file_configurazione(root_dir):
    """Trova i file di configurazione non contenuti in cartelle escluse."""
    trovati = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [cartella for cartella in dirs if cartella not in CARTELLE_ESCLUSE]
        for nome_file in files:
            nome_lower = nome_file.lower()
            estensione = os.path.splitext(nome_lower)[1]
            if nome_lower in NOMI_FILE_CONFIGURAZIONE or estensione in ESTENSIONI_CONFIGURAZIONE:
                trovati.append(os.path.join(root, nome_file))
    return sorted(trovati, key=lambda percorso: percorso.lower())


def analizza_file_configurazione(root_dir, percorsi=None):
    """Legge file di configurazione e limita gli estratti dei file grandi."""
    risultati = []
    percorsi = percorsi if percorsi is not None else trova_file_configurazione(root_dir)
    for percorso in percorsi:
        relativo = _percorso_relativo(percorso, root_dir)
        nota = ""
        nome_lower = os.path.basename(percorso).lower()
        if nome_lower == "requirements.txt":
            nota = "Dichiara le dipendenze Python."
        elif nome_lower == "package.json":
            nota = "Dichiara metadati, script e dipendenze Node.js."
        elif nome_lower in {"pyproject.toml", "setup.py", "setup.cfg"}:
            nota = "Contiene configurazione o metadati del progetto Python."
        elif os.path.splitext(nome_lower)[1] in {".yaml", ".yml", ".ini", ".cfg"}:
            nota = "File di configurazione strutturato."
        else:
            nota = "File JSON: verificare dal contenuto se è configurazione o dato."

        try:
            dimensione = os.path.getsize(percorso)
            with open(percorso, "r", encoding="utf-8", errors="replace") as file_config:
                contenuto = file_config.read(DIMENSIONE_MASSIMA_CONFIG + 1)
            troncato = dimensione > DIMENSIONE_MASSIMA_CONFIG or len(contenuto) > DIMENSIONE_MASSIMA_CONFIG
            if troncato:
                contenuto = contenuto[:LUNGHEZZA_MASSIMA_ESTRATTO_CONFIG]
                contenuto += "\n\n[Contenuto abbreviato: file oltre il limite di lettura.]"
            risultati.append({
                "file": relativo,
                "nota": nota,
                "contenuto": contenuto,
                "errore": None,
                "troncato": troncato,
            })
        except OSError as errore:
            risultati.append({
                "file": relativo,
                "nota": nota,
                "contenuto": "",
                "errore": f"Impossibile leggere il file: {errore}",
                "troncato": False,
            })
    return risultati


def rileva_servizi_esterni(root_dir, file_python, file_configurazione):
    """Cerca riferimenti a servizi esterni nel codice Python e nelle configurazioni."""
    percorsi = set(file_python)
    percorsi.update(file_configurazione)
    riferimenti = []
    servizi = set()

    for percorso in sorted(percorsi):
        if os.path.basename(percorso).lower() == "analisi_profonda.py":
            continue
        contenuto = leggi_file(percorso)
        if contenuto is None:
            continue
        relativo = _percorso_relativo(percorso, root_dir)
        for numero_riga, riga in enumerate(contenuto.splitlines(), start=1):
            termini = [
                nome for nome, pattern in KEYWORD_SERVIZI_ESTERNI.items()
                if re.search(pattern, riga, re.IGNORECASE)
            ]
            urls = REGEX_URL.findall(riga)
            if not termini and not urls:
                continue
            servizi.update(termini)
            servizi.update(urls)
            contesto = riga.strip()
            if len(contesto) > 240:
                contesto = contesto[:237] + "..."
            riferimenti.append({
                "file": relativo,
                "riga": numero_riga,
                "termini": termini,
                "url": urls,
                "contesto": contesto,
            })

    return {"servizi": sorted(servizi, key=str.lower), "riferimenti": riferimenti}


def genera_report_database(analisi):
    """Formatta lo schema SQLite in Markdown."""
    righe = [
        "# Schema del database SQLite", "",
        f"- Percorso: `{analisi['percorso']}`",
        f"- Tabelle trovate: {len(analisi['tabelle'])}", "",
    ]
    if analisi["errore"]:
        righe.extend([f"> {analisi['errore']}", ""])
    elif not analisi["tabelle"]:
        righe.extend(["Nessuna tabella trovata.", ""])

    for tabella in analisi["tabelle"]:
        totale = tabella["righe"] if tabella["righe"] is not None else "non disponibile"
        righe.extend([f"## `{tabella['nome']}`", "", f"- Righe: {totale}", ""])
        if tabella["errore_conteggio"]:
            righe.extend([f"- Errore durante l'analisi: {tabella['errore_conteggio']}", ""])
        righe.extend(["### Colonne", "", "| Nome | Tipo | Vincoli |", "|---|---|---|"])
        for colonna in tabella["colonne"]:
            vincoli = ", ".join(colonna["vincoli"]) or "—"
            righe.append(f"| `{colonna['nome']}` | {colonna['tipo']} | {vincoli} |")
        if not tabella["colonne"]:
            righe.append("| — | — | Nessuna colonna leggibile |")
        righe.extend(["", "### Indici", ""])
        if tabella["indici"]:
            for indice in tabella["indici"]:
                univoco = "UNIQUE" if indice["univoco"] else "non univoco"
                colonne = ", ".join(f"`{colonna}`" for colonna in indice["colonne"]) or "colonne non disponibili"
                righe.append(f"- `{indice['nome']}` ({univoco}): {colonne}")
        else:
            righe.append("Nessun indice.")
        righe.extend(["", "### Chiavi esterne", ""])
        if tabella["chiavi_esterne"]:
            for chiave in tabella["chiavi_esterne"]:
                righe.append(
                    f"- `{chiave['colonna']}` → "
                    f"`{chiave['tabella_riferita']}.{chiave['colonna_riferita']}` "
                    f"(ON UPDATE {chiave['azione_update']}, ON DELETE {chiave['azione_delete']})"
                )
        else:
            righe.append("Nessuna chiave esterna.")
        righe.append("")
    return "\n".join(righe)


def genera_report_configurazioni(file_configurazione):
    """Formatta elenco e contenuti dei file di configurazione in Markdown."""
    righe = ["# File di configurazione", ""]
    if not file_configurazione:
        righe.extend(["Nessun file di configurazione trovato.", ""])
        return "\n".join(righe)

    righe.extend(["## Elenco", ""])
    for file_config in file_configurazione:
        righe.append(f"- `{file_config['file']}` — {file_config['nota']}")
    righe.append("")
    for file_config in file_configurazione:
        righe.extend([
            f"## `{file_config['file']}`", "",
            f"Nota: {file_config['nota']}", "",
        ])
        if file_config["errore"]:
            righe.extend([f"> {file_config['errore']}", ""])
            continue
        righe.extend(["```text", file_config["contenuto"], "```", ""])
    return "\n".join(righe)


def genera_report_servizi_esterni(analisi):
    """Formatta i riferimenti a servizi esterni in Markdown."""
    righe = ["# Servizi esterni rilevati", "", "## Elenco", ""]
    if analisi["servizi"]:
        righe.extend(f"- `{servizio}`" for servizio in analisi["servizi"])
    else:
        righe.append("Nessun servizio o URL esterno rilevato.")
    righe.extend(["", "## Riferimenti nel codice e nelle configurazioni", ""])
    if not analisi["riferimenti"]:
        righe.append("Nessun riferimento trovato.")
    else:
        for riferimento in analisi["riferimenti"]:
            indicatori = riferimento["termini"] + riferimento["url"]
            contesto = riferimento["contesto"].replace("`", "\\`")
            righe.extend([
                f"### `{riferimento['file']}`:{riferimento['riga']}",
                f"- Riferimento: {', '.join(f'`{voce}`' for voce in indicatori)}",
                f"- Contesto: `{contesto}`",
                "",
            ])
    return "\n".join(righe)


# ------------------------------------------------------------
# CLASSE PRINCIPALE: L'ANALIZZATORE
# ------------------------------------------------------------
# Questa classe "visita" il codice Python e ne estrae le informazioni.
# Eredita da ast.NodeVisitor: Python le passa ogni "nodo" del codice
# e noi scegliamo cosa fare quando troviamo un import, una classe, ecc.

class AnalizzatoreModulo(ast.NodeVisitor):

    def __init__(self, filename, percorsi_progetto):
        self.filename = filename
        # Insieme di tutti i moduli .py del progetto (per capire cosa è interno)
        # es: {"service/dogane_service.py", "gui/mappa.py", ...}
        self.percorsi_progetto = percorsi_progetto

        # Cosa raccogliamo durante la visita
        self.classi = []
        self.funzioni_globali = []
        self.import_interni = set()
        self.import_esterni = set()
        self.chiamate_funzioni = set()
        self.tabelle_create = set()
        self.tabelle_interrogate = set()
        self.rotte_flask = []
        self.anomalie = []
        self.nomi_definiti_locali = set()

    # ---------- AGGIUNTA ANOMALIA (senza duplicati) ----------
    def _aggiungi_anomalia(self, messaggio):
        if messaggio not in self.anomalie:
            self.anomalie.append(messaggio)

    # ---------- CAPISCE SE UN MODULO E' INTERNO AL PROGETTO ----------
    def _e_modulo_interno(self, nome_modulo):
        """
        Restituisce True se il modulo importato corrisponde a un file .py
        del progetto. Es: 'service.dogane_service' -> esiste service/dogane_service.py
        """
        if not nome_modulo:
            return False

        # Trasforma 'service.dogane_service' in 'service/dogane_service'
        come_percorso = nome_modulo.replace(".", "/")
        # Trasforma './service' in 'service'
        come_percorso = come_percorso.lstrip("./")

        # Cerca una corrispondenza con i file reali del progetto
        for percorso in self.percorsi_progetto:
            percorso_norm = percorso.replace("\\", "/")
            # rimuove estensione .py e cartella ./ iniziale
            if percorso_norm.startswith("./"):
                percorso_norm = percorso_norm[2:]
            if percorso_norm.endswith(".py"):
                percorso_norm = percorso_norm[:-3]

            # corrispondenza esatta o come prefisso (per __init__.py)
            if percorso_norm == come_percorso:
                return True
            if percorso_norm.endswith("/" + come_percorso):
                return True
            # se il modulo è la cartella di un __init__
            if percorso_norm.endswith("/__init__") and percorso_norm[:-9] == come_percorso:
                return True

        # fallback: se inizia con prefissi tipici, consideralo interno
        return any(come_percorso.startswith(p) for p in PREFISSI_INTERNI_FALLBACK)

    # ---------- VISITA: import X ----------
    def visit_Import(self, node):
        for alias in node.names:
            nome = alias.name
            # Anomalia framework
            if any(fw in nome for fw in FRAMEWORK_UI_VIETATI):
                self._aggiungi_anomalia(
                    f"Incoerenza Framework: import `{nome}` vietato (richiesto {FRAMEWORK_UI_RICHIESTO})"
                )
            # Interno o esterno?
            if self._e_modulo_interno(nome):
                self.import_interni.add(nome)
            else:
                self.import_esterni.add(nome)
        self.generic_visit(node)

    # ---------- VISITA: from X import Y ----------
    def visit_ImportFrom(self, node):
        modulo = node.module or ""
        # Anomalia framework
        if any(fw in modulo for fw in FRAMEWORK_UI_VIETATI):
            self._aggiungi_anomalia(
                f"Incoerenza Framework: import da `{modulo}` vietato (richiesto {FRAMEWORK_UI_RICHIESTO})"
            )
        # Interno o esterno?
        if self._e_modulo_interno(modulo):
            for alias in node.names:
                nome_completo = f"{modulo}.{alias.name}" if modulo else alias.name
                self.import_interni.add(nome_completo)
        elif modulo:
            self.import_esterni.add(modulo)
        self.generic_visit(node)

    # ---------- VISITA: class X ----------
    def visit_ClassDef(self, node):
        metodi = []
        self.nomi_definiti_locali.add(node.name)

        for subnode in node.body:
            if isinstance(subnode, ast.FunctionDef):
                docstring = ast.get_docstring(subnode) or ""
                metodi.append({
                    "nome": subnode.name,
                    "doc": riassunto_docstring(docstring),
                })
                self.nomi_definiti_locali.add(subnode.name)

        doc_classe = ast.get_docstring(node) or ""
        self.classi.append({
            "nome": node.name,
            "doc": riassunto_docstring(doc_classe),
            "metodi": metodi,
        })
        self.generic_visit(node)

    # ---------- VISITA: def X ----------
    def visit_FunctionDef(self, node):
        self.nomi_definiti_locali.add(node.name)

        # Controlla se è una rotta Flask
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                func = decorator.func
                e_rotta = (
                    isinstance(func, ast.Attribute) and func.attr == "route"
                ) or (
                    isinstance(func, ast.Name) and func.id == "route"
                )
                if e_rotta:
                    percorso = None
                    metodi = ["GET"]
                    if decorator.args and isinstance(decorator.args[0], ast.Constant):
                        percorso = decorator.args[0].value
                    for kw in decorator.keywords:
                        if kw.arg == "methods" and isinstance(kw.value, (ast.List, ast.Tuple)):
                            metodi = [
                                elt.value for elt in kw.value.elts
                                if isinstance(elt, ast.Constant)
                            ]
                    if percorso:
                        self.rotte_flask.append({
                            "funzione": node.name,
                            "rotta": percorso,
                            "metodi": metodi,
                        })

        docstring = ast.get_docstring(node) or ""
        self.funzioni_globali.append({
            "nome": node.name,
            "doc": riassunto_docstring(docstring),
        })
        self.generic_visit(node)

    # ---------- VISITA: chiamate a funzione ----------
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.chiamate_funzioni.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.chiamate_funzioni.add(node.func.attr)
        self.generic_visit(node)

    # ---------- VISITA: stringhe (per SQL e URL) ----------
    def visit_Constant(self, node):
        if not isinstance(node.value, str):
            self.generic_visit(node)
            return

        valore = node.value
        valore_upper = valore.upper()

        # --- CREATE TABLE ---
        if "CREATE TABLE" in valore_upper:
            match = re.search(
                r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z0-9_]+)",
                valore, re.IGNORECASE,
            )
            if match:
                self.tabelle_create.add(match.group(1))

        # --- Query SELECT / INSERT / UPDATE / DELETE ---
        # Solo se la stringa sembra davvero una query SQL:
        # inizia con la keyword (eventualmente dopo spazi) o contiene una forma chiara
        e_query = False
        for kw in ("SELECT", "INSERT", "UPDATE", "DELETE"):
            # La keyword deve apparire all'inizio (dopo eventuali spazi) o subito dopo '('
            pattern = r"(^|[\s\(])" + kw + r"\s"
            if re.search(pattern, valore_upper):
                e_query = True
                break

        if e_query:
            self.tabelle_interrogate.update(
                re.findall(r"FROM\s+([a-zA-Z0-9_]+)", valore, re.IGNORECASE)
            )
            self.tabelle_interrogate.update(
                re.findall(r"INSERT\s+INTO\s+([a-zA-Z0-9_]+)", valore, re.IGNORECASE)
            )
            self.tabelle_interrogate.update(
                re.findall(r"UPDATE\s+([a-zA-Z0-9_]+)", valore, re.IGNORECASE)
            )
            self.tabelle_interrogate.update(
                re.findall(r"DELETE\s+FROM\s+([a-zA-Z0-9_]+)", valore, re.IGNORECASE)
            )

        self.generic_visit(node)
        

# ------------------------------------------------------------
# ANALISI DI FILE NON-PYTHON (HTML, JS, CSS)
# ------------------------------------------------------------

def analizza_template_html(percorso):
    """Legge un file HTML e cerca endpoint API, script JS e id mappa."""
    risultati = {
        "endpoint_chiamati": set(),
        "layer_mappa": set(),
        "librerie_esterne": set(),
    }
    contenuto = leggi_file(percorso)
    if contenuto is None:
        return risultati

    risultati["endpoint_chiamati"].update(
        re.findall(r"['\"](/api/[^'\"]+|http[^'\"]+)['\"]", contenuto)
    )
    risultati["layer_mappa"].update(
        re.findall(r"id:\s*['\"]([^'\"]+)['\"]", contenuto)
    )
    risultati["librerie_esterne"].update(
        re.findall(r"<script[^>]+src=['\"]([^'\"]+)['\"]", contenuto)
    )
    return risultati


def scansiona_file_non_python(root_dir):
    """Cammina nel progetto e cerca segnali in HTML/JS/CSS."""
    risultati = {
        "html": {"endpoints": set(), "scripts": set(), "ids": set()},
        "js":   {"endpoints": set(), "fetch": set()},
        "css":  {"selettori": set()},
    }

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in CARTELLE_ESCLUSE]
        for nome_file in files:
            nome_lower = nome_file.lower()
            if not nome_lower.endswith((".html", ".htm", ".js", ".css")):
                continue

            percorso = os.path.join(root, nome_file).replace("\\", "/")
            contenuto = leggi_file(percorso)
            if contenuto is None:
                continue

            if nome_lower.endswith((".html", ".htm")):
                risultati["html"]["endpoints"].update(
                    re.findall(r"['\"](/api/[^'\"]+|http[^'\"]+)['\"]", contenuto)
                )
                risultati["html"]["scripts"].update(
                    re.findall(r"<script[^>]+src=['\"]([^'\"]+)['\"]", contenuto)
                )
                risultati["html"]["ids"].update(
                    re.findall(r"id:\s*['\"]([^'\"]+)['\"]", contenuto)
                )
            elif nome_lower.endswith(".js"):
                risultati["js"]["endpoints"].update(
                    re.findall(r"['\"](/api/[^'\"]+|http[^'\"]+)['\"]", contenuto)
                )
                risultati["js"]["fetch"].update(
                    re.findall(
                        r"(?:fetch|axios\.(?:get|post|put|delete))\s*\(\s*['\"]([^'\"]+)['\"]",
                        contenuto,
                    )
                )
            elif nome_lower.endswith(".css"):
                risultati["css"]["selettori"].update(
                    re.findall(r"\.([A-Za-z0-9_-]+)|#([A-Za-z0-9_-]+)", contenuto)
                )

    # Converti i set in liste ordinate (JSON non gestisce i set)
    return {
        k: {subk: sorted(v) for subk, v in vdict.items()}
        for k, vdict in risultati.items()
    }


# ------------------------------------------------------------
# SCOPERTA DEI FILE DEL PROGETTO
# ------------------------------------------------------------

def trova_file_python(root_dir):
    """Restituisce la lista di tutti i file .py nel progetto (tranne esclusi)."""
    trovati = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in CARTELLE_ESCLUSE]
        for nome_file in files:
            if nome_file.endswith(".py"):
                percorso = os.path.join(root, nome_file).replace("\\", "/")
                if percorso.startswith("./"):
                    percorso = percorso[2:]
                trovati.append(percorso)
    return sorted(set(trovati))


# ------------------------------------------------------------
# RILEVAMENTO SIMBOLI ORFANI (senza falsi positivi)
# ------------------------------------------------------------

def e_callback_di_framework(nome):
    """True se il nome sembra un callback/slot/handler chiamato da un framework."""
    return any(nome.endswith(suffisso) for suffisso in SUFFISSI_CALLBACK)


def trova_simboli_orfani(moduli, tutti_i_codici):
    """
    Un simbolo è 'orfano' se è definito in un file ma il suo nome non appare
    in NESSUN altro file del progetto, e non è un nome noto come sempre-usato
    (entry point, metodo magico, callback Qt, ecc.).

    IMPORTANTE: i metodi chiamati con self.nome() sono considerati USATI,
    anche se non appaiono in altri file. Questo elimina la maggior parte
    dei falsi positivi (metodi di classe chiamati internamente).
    """
    definizioni = {}  # nome -> (file_dove_definito, tipo)

    for percorso, modulo in moduli.items():
        for cls in modulo.classi:
            definizioni[cls["nome"]] = (percorso, "classe")
        for fn in modulo.funzioni_globali:
            definizioni[fn["nome"]] = (percorso, "funzione")

    # NUOVO: raccogli tutti i nomi di metodo chiamati con self.
    metodi_chiamati_con_self = analizza_chiamate_self(moduli, tutti_i_codici)

    orfani = []
    for nome, (file_def, tipo) in definizioni.items():
        # Salta nomi universalmente noti
        if nome in NOMI_SEMPRE_USATI:
            continue
        # Salta callback di framework
        if e_callback_di_framework(nome):
            continue
        # Salta nomi che iniziano con _ (privati)
        if nome.startswith("_") and not nome.startswith("__"):
            continue
        # NUOVO: salta metodi chiamati con self.nome()
        if nome in metodi_chiamati_con_self:
            continue

        # Cerca il nome in tutti gli ALTRI file del progetto
        citato_altrove = False
        for percorso, codice in tutti_i_codici.items():
            if percorso == file_def:
                continue
            if re.search(r"\b" + re.escape(nome) + r"\b", codice):
                citato_altrove = True
                break

        if not citato_altrove:
            orfani.append({
                "simbolo": nome,
                "tipo": tipo,
                "file": file_def,
            })

    return orfani

# ------------------------------------------------------------
# CLASSIFICAZIONE ARCHITETTURALE
# ------------------------------------------------------------

def classifica_architettura(moduli):
    """Divide i file del progetto in ui / database / api / core / altro."""
    strati = {"ui": [], "database": [], "api": [], "core": [], "altro": []}

    for percorso in moduli.keys():
        lower = percorso.lower()
        if any(tok in lower for tok in ("gui", "view", "ui", "frontend", "widget", "dashboard", "mappa")):
            strati["ui"].append(percorso)
        elif any(tok in lower for tok in ("db", "database", "sql", "model")):
            strati["database"].append(percorso)
        elif any(tok in lower for tok in ("api", "route", "routes", "server", "controller", "map_server")):
            strati["api"].append(percorso)
        elif any(tok in lower for tok in ("core", "service", "logic", "utils", "common", "config")):
            strati["core"].append(percorso)
        else:
            strati["altro"].append(percorso)

    return strati


# ------------------------------------------------------------
# SINTESI PER IA (JSON compatto + prompt)
# ------------------------------------------------------------

def costruisci_ai_summary(dati):
    """Costruisce un riassunto compatto pensato per essere letto da un'IA."""
    s = dati["sintesi"]
    moduli = dati["moduli"]
    orfani = dati["dipendenze"]["simboli_orfani"]
    rotte = dati["architettura"]["rotte_api"]

    moduli_chiave = sorted(
        [
            p for p, d in moduli.items()
            if (len(d.get("classi", [])) + len(d.get("funzioni", []))) > 0
        ],
        key=lambda p: len(moduli[p].get("classi", [])) + len(moduli[p].get("funzioni", [])),
        reverse=True,
    )[:10]

    flags = []
    if orfani:
        flags.append("simboli_orfani_presenti")
    if not rotte:
        flags.append("nessuna_rotta_backend")
    if s["totale_moduli"] < 5:
        flags.append("progetto_molto_piccolo")
    if s["totale_moduli"] > 50:
        flags.append("progetto_grande")

    return {
        "nome_progetto": os.path.basename(os.getcwd()),
        "totale_moduli": s["totale_moduli"],
        "totale_classi": s["totale_classi"],
        "totale_funzioni": s["totale_funzioni"],
        "endpoint_flask": len(rotte),
        "tabelle_rilevate": s["totale_tabelle"],
        "simboli_orfani": len(orfani),
        "moduli_chiave": moduli_chiave,
        "warning_flags": flags,
    }


def costruisci_agent_insights(dati):
    """Produce hotspot, livello di rischio e azioni consigliate."""
    moduli = dati["moduli"]
    rotte = dati["architettura"]["rotte_api"]
    orfani = dati["dipendenze"]["simboli_orfani"]

    hotspots = []
    for percorso, d in moduli.items():
        score = (
            len(d.get("classi", [])) * 3
            + len(d.get("funzioni", [])) * 2
            + len(d.get("anomalie", [])) * 4
            + len(d.get("chiamate_funzioni", []))
        )
        hotspots.append({
            "file": percorso,
            "score": score,
            "classi": len(d.get("classi", [])),
            "funzioni": len(d.get("funzioni", [])),
            "anomalie": len(d.get("anomalie", [])),
        })
    hotspots = sorted(hotspots, key=lambda x: x["score"], reverse=True)[:5]

    # Livello di rischio
    rischio = "basso"
    if len(orfani) > 5 or len(rotte) == 0 or any(h["anomalie"] > 0 for h in hotspots):
        rischio = "medio"
    if len(orfani) > 15 or any(h["score"] > 30 for h in hotspots):
        rischio = "alto"

    azioni = []
    if orfani:
        azioni.append(
            "Rivedere i simboli orfani e decidere se integrarli, rimuoverli o spostarli."
        )
    if not rotte:
        azioni.append("Nessuna rotta Flask rilevata: verificare il backend o confermare frontend-only.")
    if hotspots:
        azioni.append("Prioritizzare i file con score più alto per refactor e verifica.")
    azioni.append("Usare PROGETTO_INDEX.json come contesto minimo per ridurre i token richiesti alle IA.")

    return {
        "livello_rischio": rischio,
        "hotspots": hotspots,
        "azioni_consigliate": azioni,
        "file_critici": [h["file"] for h in hotspots[:3]],
    }


def costruisci_prompt_agente(dati):
    """Prompt ultra-compatto pronto da dare a un'IA."""
    nome_progetto = os.path.basename(os.getcwd())
    s = dati["sintesi"]
    agent = dati["agent_insights"]
    critici = ", ".join(agent["file_critici"]) if agent["file_critici"] else "nessuno"

    return (
        f"Progetto: {nome_progetto}. "
        f"Contesto: {s['totale_moduli']} moduli, {s['totale_classi']} classi, "
        f"{s['totale_funzioni']} funzioni, {len(dati['architettura']['rotte_api'])} endpoint Flask, "
        f"{len(dati['dipendenze']['simboli_orfani'])} simboli orfani. "
        f"Rischio: {agent['livello_rischio']}. "
        f"File critici: {critici}. "
        f"Priorità: correggere simboli orfani, verificare file critici e consolidare dipendenze. "
        f"Usa PROGETTO_INDEX.json come fonte di verità e minimizza i cambiamenti."
    )


def costruisci_aider_context(dati):
    """Blocco di contesto pensato per Aider."""
    agent = dati["agent_insights"]
    s = dati["sintesi"]
    moduli = dati["moduli"]

    prioritari = []
    for percorso, d in moduli.items():
        score = len(d.get("anomalie", [])) * 5 + len(d.get("chiamate_funzioni", []))
        prioritari.append({"file": percorso, "score": score})
    prioritari = sorted(prioritari, key=lambda x: x["score"], reverse=True)[:5]

    return {
        "titolo": f"Brief per agente - {os.path.basename(os.getcwd())}",
        "riepilogo": {
            "moduli": s["totale_moduli"],
            "classi": s["totale_classi"],
            "funzioni": s["totale_funzioni"],
            "rotte": len(dati["architettura"]["rotte_api"]),
            "rischio": agent["livello_rischio"],
        },
        "osservazioni_chiave": [
            f"Rischio architetturale: {agent['livello_rischio']}",
            f"Simboli orfani: {len(dati['dipendenze']['simboli_orfani'])}",
            f"File critici: {', '.join(agent['file_critici']) if agent['file_critici'] else 'nessuno'}",
        ],
        "ordine_priorita": [p["file"] for p in prioritari],
        "prossimi_passi": agent["azioni_consigliate"],
        "prompt_agente": costruisci_prompt_agente(dati),
    }
def trova_duplicazioni(moduli):
    """
    Trova funzioni/metodi con lo stesso nome definiti in file diversi.
    Es: 'calcola_distanza_haversine' esiste sia in audit_service.py
    che in app_desktop.py -> probabile duplicazione.
    """
    # Mappa: nome_funzione -> lista di file dove è definita
    nomi_a_file = defaultdict(list)

    for percorso, modulo in moduli.items():
        for fn in modulo.funzioni_globali:
            nomi_a_file[fn["nome"]].append(percorso)
        for cls in modulo.classi:
            for metodo in cls["metodi"]:
                nomi_a_file[metodo["nome"]].append(percorso)

    # Trova solo quelli che appaiono in più di un file
    duplicazioni = []
    for nome, files in nomi_a_file.items():
        # Rimuovi duplicati (stesso file, ma definizione multipla)
        files_unici = sorted(set(files))
        if len(files_unici) > 1:
            # Salta nomi troppo generici
            if nome in {"__init__", "run", "main", "start", "setup", "update", "get", "set"}:
                continue
            duplicazioni.append({
                "nome": nome,
                "file": files_unici,
                "numero_copie": len(files_unici),
            })

    # Ordina per numero di copie decrescente
    duplicazioni.sort(key=lambda x: x["numero_copie"], reverse=True)
    return duplicazioni


def analizza_chiamate_self(moduli, tutti_i_codici):
    """
    Cerca chiamate a metodi interni del tipo 'self.nome_metodo()' nel codice.
    Restituisce l'insieme di tutti i nomi di metodo chiamati con self.
    Serve per ridurre i falsi positivi nei simboli orfani: un metodo
    chiamato con self.nome() NON è orfano, è usato internamente.
    """
    metodi_chiamati_con_self = set()

    for percorso, codice in tutti_i_codici.items():
        # Cerca pattern 'self.nome_metodo' (seguito da '(' o meno)
        trovate = re.findall(r"self\.([a-zA-Z_][a-zA-Z0-9_]*)", codice)
        for nome in trovate:
            metodi_chiamati_con_self.add(nome)

    return metodi_chiamati_con_self


def costruisci_mappa_dipendenze(moduli):
    """
    Costruisce una mappa delle dipendenze tra moduli del progetto.
    Per ogni modulo, dice quali altri moduli lo importano.
    """
    # Mappa: modulo_destinazione -> insieme di moduli che lo importano
    chi_importa_chi = defaultdict(set)

    # Per ogni modulo sorgente, guarda i suoi import interni
    for percorso_sorgente, modulo in moduli.items():
        # Normalizza il nome del sorgente (senza .py)
        sorgente_norm = percorso_sorgente.replace("\\", "/").replace(".py", "")

        for imp in modulo.import_interni:
            # Normalizza il nome dell'import (es: 'service.audit_service' -> 'service/audit_service')
            imp_norm = imp.replace(".", "/")

            # Trova il modulo di destinazione reale
            for percorso_dest, _ in moduli.items():
                dest_norm = percorso_dest.replace("\\", "/").replace(".py", "")
                if dest_norm.endswith(imp_norm):
                    chi_importa_chi[percorso_dest].add(sorgente_norm)
                    break

    # Converti in un formato ordinato
    risultato = {}
    for destinazione, importatori in chi_importa_chi.items():
        risultato[destinazione] = sorted(importatori)

    return risultato



# ------------------------------------------------------------
# REPORT MARKDOWN PER L'UMANO
# ------------------------------------------------------------
def genera_ai_brief(dati):
    """
    Genera un file COMPATTO (pochi KB) pensato per essere letto da Copilot
    o da un altro agente. Contiene solo l'essenziale per orientarsi, non
    tutto il dataset.
    """
    s = dati["sintesi"]
    agent = dati["agent_insights"]
    arch = dati["architettura"]
    dep = dati["dipendenze"]
    moduli = dati["moduli"]

    righe = []
    righe.append(f"# AI Brief - {os.path.basename(os.getcwd())}")
    righe.append("")
    righe.append(f"*Aggiornato: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    righe.append("")

    righe.append("## Come leggere il progetto")
    righe.append("")
    righe.append("- All'inizio di ogni richiesta: `REPORT/AI_BRIEF.md`.")
    righe.append("- Prima di lavorare sul database: `REPORT/DB_SCHEMA.md`.")
    righe.append("- Prima di lavorare sulla configurazione: `REPORT/CONFIG_FILES.md`.")
    righe.append("- Prima di lavorare sui servizi esterni: `REPORT/EXTERNAL_SERVICES.md`.")
    righe.append("- Per dettagli specifici: `REPORT/analisi.json` oppure il file di codice interessato.")
    righe.append("- Per le persone: `REPORT/report.md` (completo) e `REPORT/riepilogo.txt` (sintesi).")
    righe.append("- `REPORT/ULTIMO_RUN.json` è riservato allo script.")
    righe.append("- Non leggere `aider_context.md` né i file con timestamp: sono specifici o storici.")
    righe.append("")

    # --- Numeri essenziali ---
    righe.append("## Numeri essenziali")
    righe.append("")
    righe.append(f"- Moduli Python: {s['totale_moduli']}")
    righe.append(f"- Classi: {s['totale_classi']}")
    righe.append(f"- Funzioni: {s['totale_funzioni']}")
    righe.append(f"- Rotte Flask: {len(arch['rotte_api'])}")
    righe.append(f"- Tabelle DB: {s['totale_tabelle']}")
    righe.append(f"- Simboli orfani: {len(dep['simboli_orfani'])}")
    righe.append(f"- **Livello rischio: {agent['livello_rischio']}**")
    righe.append("")

    # --- File critici ---
    righe.append("## File critici (score più alto)")
    righe.append("")
    for h in agent["hotspots"]:
        righe.append(f"- `{h['file']}` - score {h['score']} - {h['classi']} classi, {h['funzioni']} funzioni, {h['anomalie']} anomalie")
    righe.append("")

    # --- Rotte Flask ---
    righe.append("## Endpoint Flask")
    righe.append("")
    for rotta, info in arch["rotte_api"].items():
        metodi = ",".join(info["metodi"])
        righe.append(f"- `{rotta}` [{metodi}] -> `{info['funzione']}()` in `{info['file']}`")
    righe.append("")

    # --- Top 15 orfani (non tutti, solo i primi) ---
    righe.append("## Simboli orfani (top 15)")
    righe.append("")
    for orf in dep["simboli_orfani"][:15]:
        righe.append(f"- `{orf['simbolo']}` ({orf['tipo']}) in `{orf['file']}`")
    if len(dep["simboli_orfani"]) > 15:
        righe.append(f"- ... e altri {len(dep['simboli_orfani']) - 15} (vedi report completo)")
    righe.append("")

    # --- Moduli principali ---

        # --- Duplicazioni ---
    duplicazioni = dati["dipendenze"].get("duplicazioni", [])
    if duplicazioni:
        righe.append("## Duplicazioni rilevate")
        righe.append("")
        righe.append(f"*{len(duplicazioni)} funzioni/metodi definiti in più file:*")
        righe.append("")
        for dup in duplicazioni[:20]:
            files_str = ", ".join(f"`{f}`" for f in dup["file"])
            righe.append(f"- `{dup['nome']}` ({dup['numero_copie']} copie) → {files_str}")
        if len(duplicazioni) > 20:
            righe.append(f"- ... e altre {len(duplicazioni) - 20}")
        righe.append("")

    database = dati["database_analysis"]
    righe.append("## Database")
    righe.append("")
    righe.append(f"- Percorso: `{database['percorso']}`")
    righe.append(f"- Numero di tabelle: {len(database['tabelle'])}")
    if database["errore"]:
        righe.append(f"- Stato: {database['errore']}")
    for tabella in database["tabelle"]:
        righe.append(f"- `{tabella['nome']}`: {tabella['righe']} righe")
    righe.append("")

    servizi_esterni = dati["external_services_analysis"]["servizi"]
    righe.append("## Servizi esterni rilevati")
    righe.append("")
    if servizi_esterni:
        righe.extend(f"- `{servizio}`" for servizio in servizi_esterni)
    else:
        righe.append("- Nessun servizio o URL esterno rilevato.")
    righe.append("")

    configurazioni = dati["configuration_analysis"]
    righe.append("## File di configurazione")
    righe.append("")
    if configurazioni:
        righe.extend(f"- `{file_config['file']}`" for file_config in configurazioni)
    else:
        righe.append("- Nessun file di configurazione trovato.")
    righe.append("")

    righe.append("## Moduli principali")
    righe.append("")
    ordinati = sorted(
        moduli.items(),
        key=lambda x: len(x[1].get("classi", [])) + len(x[1].get("funzioni", [])),
        reverse=True,
    )[:10]
    for percorso, d in ordinati:
        righe.append(f"- `{percorso}`: {len(d['classi'])} classi, {len(d['funzioni'])} funzioni")
    righe.append("")

    # --- Azioni consigliate ---
    righe.append("## Azioni consigliate")
    righe.append("")
    for azione in agent["azioni_consigliate"]:
        righe.append(f"- {azione}")
    righe.append("")

    righe.append("---")
    righe.append("")
    righe.append("*Per approfondire: vedi `analisi.json` (dataset completo) o `report.md` (versione umana).*")
    righe.append("")

    return "\n".join(righe)



def genera_report_markdown(dati):
    """Report leggibile, pensato per te (non per le IA)."""
    s = dati["sintesi"]
    arch = dati["architettura"]
    dep = dati["dipendenze"]
    moduli = dati["moduli"]
    agent = dati["agent_insights"]

    righe = []
    righe.append(f"# Analisi del progetto: {os.path.basename(os.getcwd())}")
    righe.append("")
    righe.append(f"*Generato il {datetime.now().strftime('%Y-%m-%d alle %H:%M:%S')}*")
    righe.append("")

    righe.append("## 1. Sintesi")
    righe.append("")
    righe.append(f"- Moduli Python: **{s['totale_moduli']}**")
    righe.append(f"- Classi: **{s['totale_classi']}**")
    righe.append(f"- Funzioni globali: **{s['totale_funzioni']}**")
    righe.append(f"- Rotte Flask: **{len(arch['rotte_api'])}**")
    righe.append(f"- Tabelle rilevate: **{s['totale_tabelle']}**")
    righe.append(f"- Simboli orfani: **{len(dep['simboli_orfani'])}**")
    righe.append("")

    # Database
    database = dati["database_analysis"]
    righe.append("## Database")
    righe.append("")
    righe.append(f"- Percorso: `{database['percorso']}`")
    righe.append(f"- Tabelle: {len(database['tabelle'])}")
    if database["errore"]:
        righe.append(f"- Stato: {database['errore']}")
    if database["tabelle"]:
        righe.extend([
            "",
            "| Tabella | Righe | Colonne chiave |",
            "|---|---:|---|",
        ])
        for tabella in database["tabelle"]:
            colonne_chiave = []
            for colonna in tabella["colonne"]:
                if "chiave primaria" in colonna["vincoli"]:
                    colonne_chiave.append(f"{colonna['nome']} (PK)")
            for chiave in tabella["chiavi_esterne"]:
                colonne_chiave.append(
                    f"{chiave['colonna']} (FK → {chiave['tabella_riferita']}.{chiave['colonna_riferita']})"
                )
            righe.append(
                f"| `{tabella['nome']}` | {tabella['righe'] if tabella['righe'] is not None else 'n/d'} "
                f"| {', '.join(colonne_chiave) if colonne_chiave else '—'} |"
            )
    elif not database["errore"]:
        righe.append("- Nessuna tabella trovata.")
    righe.append("")

    # File di configurazione
    righe.append("## File di configurazione")
    righe.append("")
    configurazioni = dati["configuration_analysis"]
    if configurazioni:
        righe.extend(f"- `{file_config['file']}`" for file_config in configurazioni)
    else:
        righe.append("- Nessun file trovato.")
    righe.append("")

    # Servizi esterni
    righe.append("## Servizi esterni")
    righe.append("")
    servizi = dati["external_services_analysis"]["servizi"]
    if servizi:
        righe.extend(f"- `{servizio}`" for servizio in servizi)
    else:
        righe.append("- Nessun servizio o URL rilevato.")
    righe.append("")

    righe.append("## 2. Architettura (per strato)")
    righe.append("")
    for strato, files in arch["strati"].items():
        if files:
            righe.append(f"**{strato}** ({len(files)} file)")
            for f in files[:8]:
                righe.append(f"- `{f}`")
            if len(files) > 8:
                righe.append(f"- ... e altri {len(files) - 8}")
            righe.append("")

    righe.append("## 3. Endpoint Flask")
    righe.append("")
    if arch["rotte_api"]:
        for rotta, info in arch["rotte_api"].items():
            metodi = ", ".join(info["metodi"])
            righe.append(f"- `{rotta}` → `{info['funzione']}()` [{metodi}] in `{info['file']}`")
    else:
        righe.append("- Nessuna rotta Flask rilevata.")
    righe.append("")

    righe.append("## 4. Frontend & Mappa")
    righe.append("")
    fm = arch["frontend_mappa"]
    if fm["endpoint_utilizzati"]:
        righe.append(f"**Endpoint usati dal frontend:**")
        for ep in fm["endpoint_utilizzati"][:15]:
            righe.append(f"- `{ep}`")
        righe.append("")
    if fm["layer_mappa"]:
        righe.append(f"**Layer mappa:** {', '.join(fm['layer_mappa'][:10])}")
        righe.append("")
    if fm["librerie_esterne"]:
        righe.append(f"**Librerie esterne:**")
        for lib in fm["librerie_esterne"][:10]:
            righe.append(f"- `{lib}`")
        righe.append("")

    righe.append("## 5. Simboli orfani")
    righe.append("")
    if dep["simboli_orfani"]:
        righe.append(f"*{len(dep['simboli_orfani'])} simboli definiti ma mai citati altrove:*")
        righe.append("")
        for orf in dep["simboli_orfani"][:30]:
            righe.append(f"- **{orf['tipo']}** `{orf['simbolo']}` in `{orf['file']}`")
        if len(dep["simboli_orfani"]) > 30:
            righe.append(f"- ... e altri {len(dep['simboli_orfani']) - 30}")
    else:
        righe.append("- Nessun simbolo orfano: ottimo segno.")
    righe.append("")

    righe.append("## 6. Moduli con più contenuto")
    righe.append("")
    ordinati = sorted(
        moduli.items(),
        key=lambda x: len(x[1].get("classi", [])) + len(x[1].get("funzioni", [])),
        reverse=True,
    )[:10]
    for percorso, d in ordinati:
        righe.append(
            f"- `{percorso}`: {len(d['classi'])} classi, {len(d['funzioni'])} funzioni"
        )
    righe.append("")

    righe.append("## 7. Livello di rischio e file critici")
    righe.append("")
    righe.append(f"**Livello di rischio:** `{agent['livello_rischio']}`")
    righe.append("")
    if agent["file_critici"]:
        righe.append("**File critici (da guardare per primi):**")
        for f in agent["file_critici"]:
            righe.append(f"- `{f}`")
        righe.append("")
    righe.append("**Azioni consigliate:**")
    for azione in agent["azioni_consigliate"]:
        righe.append(f"- {azione}")
    righe.append("")

    return "\n".join(righe)


# ------------------------------------------------------------
# ARCHIVIAZIONE REPORT PRECEDENTI
# ------------------------------------------------------------
def archivia_report_precedenti(cartella_report):
    """
    Sposta i file dell'esecuzione precedente in ARCHIVIO/<data_ora>/.
    Mantiene nella cartella principale i report correnti e l'ultimo snapshot.
    """
    cartella_archivio = os.path.join(cartella_report, "ARCHIVIO")
    assicura_cartella(cartella_archivio)

    # File che NON vanno archiviati (restano sempre nella root di REPORT/)
    file_da_non_archiviare = FILE_REPORT_SEMPRE_PRESENTI

    # Raccogli i file da archiviare, raggruppati per prefisso data-ora
    gruppi = defaultdict(list)

    for nome_file in os.listdir(cartella_report):
        percorso_completo = os.path.join(cartella_report, nome_file)

        # Salta le cartelle (es. ARCHIVIO stesso)
        if os.path.isdir(percorso_completo):
            continue

        # Salta i file che devono restare
        if nome_file in file_da_non_archiviare:
            continue

        # Estrae il prefisso "2026-09-29_11-32-45" dal nome file
        # (i nostri file hanno sempre questo formato all'inizio)
        match = re.match(r"^(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})_", nome_file)
        if match:
            prefisso = match.group(1)
            gruppi[prefisso].append(nome_file)
        elif nome_file in FILE_REPORT_OBSOLETI:
            prefisso = datetime.fromtimestamp(
                os.path.getmtime(percorso_completo)
            ).strftime("%Y-%m-%d_%H-%M-%S")
            gruppi[prefisso].append(nome_file)
        else:
            # File senza prefisso riconoscibile: li lasciamo dove sono
            pass

    # Sposta ogni gruppo nella sua sottocartella
    for prefisso, files in gruppi.items():
        sottocartella = os.path.join(cartella_archivio, prefisso)
        assicura_cartella(sottocartella)
        for nome_file in files:
            origine = os.path.join(cartella_report, nome_file)
            destinazione = os.path.join(sottocartella, nome_file)
            try:
                os.replace(origine, destinazione)
            except Exception as e:
                print(f"    ATTENZIONE: impossibile archiviare {nome_file}: {e}")

# ------------------------------------------------------------
# FUNZIONE PRINCIPALE
# ------------------------------------------------------------

def esegui_analisi():
    """Esegue tutta l'analisi e scrive i report nella cartella REPORT/."""

    print("=" * 60)
    print("ANALISI PROFONDA - Bikepacking Studio")
    print("=" * 60)
    print()

    # 1. Trova tutti i file Python del progetto
    print("1. Scansione file di progetto...")
    file_python = trova_file_python(".")
    print(f"   Trovati {len(file_python)} file Python.")
    print()

    # 2. Leggi tutti i file in memoria
    print("2. Lettura file in memoria...")
    tutti_i_codici = {}
    for f in file_python:
        # Salta lo script di analisi stesso
        if os.path.basename(f) == "analisi_profonda.py":
            continue
        contenuto = leggi_file(f)
        if contenuto is not None:
            tutti_i_codici[f] = contenuto
    print(f"   Letti {len(tutti_i_codici)} file.")
    print()

    # 3. Analizza ogni file con l'AST
    print("3. Analisi sintattica (AST)...")
    moduli = {}
    for percorso, codice in tutti_i_codici.items():
        try:
            tree = ast.parse(codice, filename=percorso)
            analizzatore = AnalizzatoreModulo(percorso, set(tutti_i_codici.keys()))
            analizzatore.visit(tree)
            moduli[percorso] = analizzatore
        except SyntaxError as e:
            print(f"   ATTENZIONE: errore di sintassi in {percorso} (riga {e.lineno})")
        except Exception as e:
            print(f"   ERRORE su {percorso}: {e}")
    print(f"   Analizzati {len(moduli)} moduli.")
    print()

    # 4. Aggrega i dati globali
    print("4. Aggregazione dati globali...")
    tutte_tabelle_create = set()
    tutte_tabelle_interrogate = set()
    tutte_rotte = {}
    tutti_import_esterni = set()

    for percorso, modulo in moduli.items():
        tutte_tabelle_create.update(modulo.tabelle_create)
        tutte_tabelle_interrogate.update(modulo.tabelle_interrogate)
        tutti_import_esterni.update(modulo.import_esterni)
        for r in modulo.rotte_flask:
            tutte_rotte[r["rotta"]] = {
                "file": percorso,
                "funzione": r["funzione"],
                "metodi": r["metodi"],
            }

    # 5. Trova simboli orfani
    print("5. Ricerca simboli orfani...")
    simboli_orfani = trova_simboli_orfani(moduli, tutti_i_codici)
    print(f"   Trovati {len(simboli_orfani)} simboli orfani.")
    print()

    # 6. Classifica architettura
    print("6. Classificazione architetturale...")
    strati = classifica_architettura(moduli)
    print()

    # 7. Analizza template HTML e file non-Python
    print("7. Analisi file non-Python (HTML/JS/CSS)...")
    template_path = os.path.join("templates", "map_view.html")
    info_mappa = analizza_template_html(template_path)
    non_python = scansiona_file_non_python(".")
    print()

    # 7b. Trova duplicazioni tra file
    print("7b. Ricerca duplicazioni tra file...")
    duplicazioni = trova_duplicazioni(moduli)
    print(f"    Trovate {len(duplicazioni)} funzioni/metodi duplicati.")
    print()

    # 7c. Analisi aggiuntive: database, configurazioni e servizi esterni
    print("7c. Analisi database SQLite in sola lettura...")
    analisi_database = analizza_database_sqlite(
        os.path.join("data", "bikepacking_app.db")
    )
    if analisi_database["errore"]:
        print(f"    {analisi_database['errore']}")
    else:
        print(f"    Trovate {len(analisi_database['tabelle'])} tabelle.")

    print("7d. Scansione file di configurazione...")
    percorsi_configurazione = trova_file_configurazione(".")
    file_configurazione = analizza_file_configurazione(".", percorsi_configurazione)
    print(f"    Trovati {len(file_configurazione)} file.")

    print("7e. Rilevamento servizi esterni...")
    analisi_servizi_esterni = rileva_servizi_esterni(
        ".", file_python, percorsi_configurazione
    )
    print(f"    Trovati {len(analisi_servizi_esterni['riferimenti'])} riferimenti.")
    print()

    # 7c. Costruisci mappa delle dipendenze
    print("7f. Costruzione mappa dipendenze...")
    mappa_dipendenze = costruisci_mappa_dipendenze(moduli)
    print(f"    Mappati {len(mappa_dipendenze)} moduli con importatori.")
    print()

    # 8. Costruisci il JSON completo
    print("8. Costruzione dataset JSON...")
    dati = {
        "meta": {
            "data_analisi": datetime.now().isoformat(),
            "nome_progetto": os.path.basename(os.getcwd()),
            "versione_script": "v3.0",
        },
        "sintesi": {
            "totale_moduli": len(moduli),
            "totale_classi": sum(len(m.classi) for m in moduli.values()),
            "totale_funzioni": sum(len(m.funzioni_globali) for m in moduli.values()),
            "totale_rotte_flask": len(tutte_rotte),
            "totale_tabelle": len(tutte_tabelle_create | tutte_tabelle_interrogate),
            "tabelle_create": sorted(tutte_tabelle_create),
            "tabelle_interrogate": sorted(tutte_tabelle_interrogate),
            "librerie_esterne": sorted(tutti_import_esterni),
        },
        "architettura": {
            "strati": strati,
            "rotte_api": tutte_rotte,
            "frontend_mappa": {
                "endpoint_utilizzati": sorted(info_mappa["endpoint_chiamati"]),
                "layer_mappa": sorted(info_mappa["layer_mappa"]),
                "librerie_esterne": sorted(info_mappa["librerie_esterne"]),
            },
        },
        "dipendenze": {
            "simboli_orfani": simboli_orfani,
            "duplicazioni": duplicazioni,
            "mappa_dipendenze": mappa_dipendenze,
        },
        "moduli": {},
        "non_python_signals": non_python,
        "database_analysis": analisi_database,
        "configuration_analysis": file_configurazione,
        "external_services_analysis": analisi_servizi_esterni,
    }

    for percorso, modulo in moduli.items():
        dati["moduli"][percorso] = {
            "classi": [c["nome"] for c in modulo.classi],
            "funzioni": [f["nome"] for f in modulo.funzioni_globali],
            "import_interni": sorted(modulo.import_interni),
            "import_esterni": sorted(modulo.import_esterni),
            "tabelle_usate": sorted(modulo.tabelle_interrogate | modulo.tabelle_create),
            "anomalie": modulo.anomalie,
            "chiamate_funzioni": sorted(modulo.chiamate_funzioni),
        }

    # 9. Arricchisci con insights per IA
    print("9. Generazione insights per IA...")
    dati["ai_summary"] = costruisci_ai_summary(dati)
    dati["agent_insights"] = costruisci_agent_insights(dati)
    dati["aider_context"] = costruisci_aider_context(dati)
    dati["prompt_agente"] = costruisci_prompt_agente(dati)
    print()

    # 10. Prepara la cartella REPORT e i nomi file
    print("10. Scrittura report in REPORT/...")
    cartella_report = os.path.join(os.getcwd(), "REPORT")
    assicura_cartella(cartella_report)

    # 10a. Archivia i report della esecuzione precedente
    archivia_report_precedenti(cartella_report)

    ts = timestamp_leggibile()
    percorso_json = os.path.join(cartella_report, "analisi.json")
    percorso_md = os.path.join(cartella_report, "report.md")
    percorso_aider = os.path.join(cartella_report, f"{ts}_aider_context.md")
    percorso_riepilogo = os.path.join(cartella_report, "riepilogo.txt")
    percorso_ultimo = os.path.join(cartella_report, NOME_ULTIMO_SNAPSHOT)

    # 11. Scrivi il JSON completo
    with open(percorso_json, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=2, ensure_ascii=False)
    print(f"    Scritto: {percorso_json}")

    # 12. Scrivi il report Markdown
    with open(percorso_md, "w", encoding="utf-8") as f:
        f.write(genera_report_markdown(dati))
    print(f"    Scritto: {percorso_md}")

    # 13. Scrivi il context Aider
    with open(percorso_aider, "w", encoding="utf-8") as f:
        f.write("# Aider context\n\n")
        f.write("```json\n")
        f.write(json.dumps(dati["aider_context"], indent=2, ensure_ascii=False))
        f.write("\n```\n")
    print(f"    Scritto: {percorso_aider}")

    # 14b. Scrivi l'AI Brief (file compatto per Copilot)
    percorso_brief_ultimo = os.path.join(cartella_report, "AI_BRIEF.md")
    contenuto_brief = genera_ai_brief(dati)
    with open(percorso_brief_ultimo, "w", encoding="utf-8") as f:
        f.write(contenuto_brief)
    print(f"    Scritto: {percorso_brief_ultimo}")

    # 14c. Scrivi i report di database, configurazioni e servizi esterni
    percorsi_report_aggiuntivi = {
        "DB_SCHEMA.md": genera_report_database(analisi_database),
        "CONFIG_FILES.md": genera_report_configurazioni(file_configurazione),
        "EXTERNAL_SERVICES.md": genera_report_servizi_esterni(analisi_servizi_esterni),
    }
    for nome_report, contenuto_report in percorsi_report_aggiuntivi.items():
        percorso_report = os.path.join(cartella_report, nome_report)
        with open(percorso_report, "w", encoding="utf-8") as f:
            f.write(contenuto_report)
        print(f"    Scritto: {percorso_report}")

    # 15. Scrivi riepilogo testuale
    riepilogo = []
    riepilogo.append("RIEPILOGO ANALISI")
    riepilogo.append("=" * 50)
    riepilogo.append("")
    riepilogo.append(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    riepilogo.append(f"Progetto: {os.path.basename(os.getcwd())}")
    riepilogo.append("")
    riepilogo.append(f"Moduli Python: {dati['sintesi']['totale_moduli']}")
    riepilogo.append(f"Classi: {dati['sintesi']['totale_classi']}")
    riepilogo.append(f"Funzioni: {dati['sintesi']['totale_funzioni']}")
    riepilogo.append(f"Rotte Flask: {dati['sintesi']['totale_rotte_flask']}")
    riepilogo.append(f"Tabelle: {dati['sintesi']['totale_tabelle']}")
    riepilogo.append(f"Simboli orfani: {len(simboli_orfani)}")
    riepilogo.append("")
    riepilogo.append(f"Livello rischio: {dati['agent_insights']['livello_rischio']}")
    riepilogo.append(f"File critici: {', '.join(dati['agent_insights']['file_critici'])}")
    with open(percorso_riepilogo, "w", encoding="utf-8") as f:
        f.write("\n".join(riepilogo))
    print(f"    Scritto: {percorso_riepilogo}")

    # 16. Salva lo snapshot corrente per lo script
    with open(percorso_ultimo, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=2, ensure_ascii=False)
    print(f"    Scritto: {percorso_ultimo}")
    print()

    # 18. Riepilogo a schermo
    print("=" * 60)
    print("ANALISI COMPLETATA")
    print("=" * 60)
    print(f"Moduli Python:    {dati['sintesi']['totale_moduli']}")
    print(f"Classi:           {dati['sintesi']['totale_classi']}")
    print(f"Funzioni:         {dati['sintesi']['totale_funzioni']}")
    print(f"Rotte Flask:      {dati['sintesi']['totale_rotte_flask']}")
    print(f"Tabelle:          {dati['sintesi']['totale_tabelle']}")
    print(f"Simboli orfani:   {len(simboli_orfani)}")
    print(f"Livello rischio:  {dati['agent_insights']['livello_rischio']}")
    print()
    print(f"Tutti i report sono in: {cartella_report}")
    print()


# ------------------------------------------------------------
# AVVIO
# ------------------------------------------------------------

if __name__ == "__main__":
    esegui_analisi()