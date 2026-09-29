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
#   6. Scrive tutto nella cartella REPORT/ con data e ora nel nome
#   7. Confronta con l'esecuzione precedente e scrive un CHANGELOG
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
import sys
from collections import defaultdict
from datetime import datetime

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

# Nome del file CHANGELOG e dell'ultimo snapshot
NOME_CHANGELOG = "CHANGELOG.md"
NOME_ULTIMO_SNAPSHOT = "ULTIMO_RUN.json"


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
    """
    definizioni = {}  # nome -> (file_dove_definito, tipo)

    for percorso, modulo in moduli.items():
        for cls in modulo.classi:
            definizioni[cls["nome"]] = (percorso, "classe")
        for fn in modulo.funzioni_globali:
            definizioni[fn["nome"]] = (percorso, "funzione")

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

    # --- Prompt pronto ---
    righe.append("## Prompt pronto per agente")
    righe.append("")
    righe.append("```")
    righe.append(dati["prompt_agente"])
    righe.append("```")
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

    righe.append("## 8. Prompt per IA")
    righe.append("")
    righe.append("```")
    righe.append(dati["prompt_agente"])
    righe.append("```")
    righe.append("")

    return "\n".join(righe)


# ------------------------------------------------------------
# CHANGELOG (confronto con esecuzione precedente)
# ------------------------------------------------------------
def archivia_report_precedenti(cartella_report):
    """
    Sposta i file dell'esecuzione precedente in ARCHIVIO/<data_ora>/.
    Lascia in REPORT/ solo:
      - i file dell'esecuzione attuale (li scriveremo dopo)
      - CHANGELOG.md (sempre aggiornato)
      - ULTIMO_RUN.json (sempre aggiornato)
    """
    cartella_archivio = os.path.join(cartella_report, "ARCHIVIO")
    assicura_cartella(cartella_archivio)

    # File che NON vanno archiviati (restano sempre nella root di REPORT/)
    file_da_non_archiviare = {NOME_CHANGELOG, NOME_ULTIMO_SNAPSHOT, "AI_BRIEF.md"}

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

def carica_snapshot_precedente(percorso):
    """Carica ULTIMO_RUN.json se esiste, altrimenti None."""
    if not os.path.exists(percorso):
        return None
    try:
        with open(percorso, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def genera_changelog(vecchio, nuovo):
    """Confronta due snapshot e produce un changelog in Markdown."""
    righe = []
    righe.append(f"# Changelog analisi")
    righe.append("")
    righe.append(f"*Generato il {datetime.now().strftime('%Y-%m-%d alle %H:%M:%S')}*")
    righe.append("")

    if vecchio is None:
        righe.append("**Prima esecuzione: nessun confronto disponibile.**")
        righe.append("")
        righe.append(f"- Moduli: {nuovo['sintesi']['totale_moduli']}")
        righe.append(f"- Classi: {nuovo['sintesi']['totale_classi']}")
        righe.append(f"- Funzioni: {nuovo['sintesi']['totale_funzioni']}")
        righe.append(f"- Simboli orfani: {len(nuovo['dipendenze']['simboli_orfani'])}")
        righe.append("")
        righe.append("Dalla prossima esecuzione vedrai qui le differenze.")
        return "\n".join(righe)

    v = vecchio["sintesi"]
    n = nuovo["sintesi"]

    righe.append("## Differenze numeriche")
    righe.append("")
    righe.append(f"| Metrica | Prima | Adesso | Delta |")
    righe.append(f"|---|---|---|---|")
    righe.append(f"| Moduli | {v['totale_moduli']} | {n['totale_moduli']} | {n['totale_moduli'] - v['totale_moduli']:+d} |")
    righe.append(f"| Classi | {v['totale_classi']} | {n['totale_classi']} | {n['totale_classi'] - v['totale_classi']:+d} |")
    righe.append(f"| Funzioni | {v['totale_funzioni']} | {n['totale_funzioni']} | {n['totale_funzioni'] - v['totale_funzioni']:+d} |")
    righe.append(f"| Tabelle | {v['totale_tabelle']} | {n['totale_tabelle']} | {n['totale_tabelle'] - v['totale_tabelle']:+d} |")
    righe.append("")

    # Simboli orfani: quali sono nuovi, quali risolti
    orfani_vecchi = {o["simbolo"] for o in vecchio["dipendenze"]["simboli_orfani"]}
    orfani_nuovi = {o["simbolo"] for o in nuovo["dipendenze"]["simboli_orfani"]}

    nuovi_orfani = orfani_nuovi - orfani_vecchi
    orfani_risolti = orfani_vecchi - orfani_nuovi

    righe.append("## Simboli orfani")
    righe.append("")
    if nuovi_orfani:
        righe.append(f"**Nuovi simboli orfani ({len(nuovi_orfani)}):**")
        for s in sorted(nuovi_orfani):
            righe.append(f"- `{s}`")
        righe.append("")
    if orfani_risolti:
        righe.append(f"**Simboli orfani risolti ({len(orfani_risolti)}):**")
        for s in sorted(orfani_risolti):
            righe.append(f"- `{s}`")
        righe.append("")
    if not nuovi_orfani and not orfani_risolti:
        righe.append("Nessun cambiamento nei simboli orfani.")
        righe.append("")

    # File nuovi e scomparsi
    files_vecchi = set(vecchio["moduli"].keys())
    files_nuovi = set(nuovo["moduli"].keys())

    nuovi_files = files_nuovi - files_vecchi
    files_scomparsi = files_vecchi - files_nuovi

    righe.append("## File Python")
    righe.append("")
    if nuovi_files:
        righe.append(f"**File aggiunti ({len(nuovi_files)}):**")
        for f in sorted(nuovi_files):
            righe.append(f"- `{f}`")
        righe.append("")
    if files_scomparsi:
        righe.append(f"**File rimossi ({len(files_scomparsi)}):**")
        for f in sorted(files_scomparsi):
            righe.append(f"- `{f}`")
        righe.append("")
    if not nuovi_files and not files_scomparsi:
        righe.append("Nessun file aggiunto o rimosso.")
        righe.append("")

    return "\n".join(righe)


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
        },
        "moduli": {},
        "non_python_signals": non_python,
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
    percorso_json = os.path.join(cartella_report, f"{ts}_analisi.json")
    percorso_md = os.path.join(cartella_report, f"{ts}_report.md")
    percorso_prompt = os.path.join(cartella_report, f"{ts}_prompt_agente.md")
    percorso_aider = os.path.join(cartella_report, f"{ts}_aider_context.md")
    percorso_riepilogo = os.path.join(cartella_report, f"{ts}_riepilogo.txt")
    percorso_changelog = os.path.join(cartella_report, NOME_CHANGELOG)
    percorso_ultimo = os.path.join(cartella_report, NOME_ULTIMO_SNAPSHOT)

    # 11. Scrivi il JSON completo
    with open(percorso_json, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=2, ensure_ascii=False)
    print(f"    Scritto: {percorso_json}")

    # 12. Scrivi il report Markdown
    with open(percorso_md, "w", encoding="utf-8") as f:
        f.write(genera_report_markdown(dati))
    print(f"    Scritto: {percorso_md}")

    # 13. Scrivi il prompt agente
    with open(percorso_prompt, "w", encoding="utf-8") as f:
        f.write(dati["prompt_agente"] + "\n")
    print(f"    Scritto: {percorso_prompt}")

    # 14. Scrivi il context Aider
    with open(percorso_aider, "w", encoding="utf-8") as f:
        f.write("# Aider context\n\n")
        f.write("```json\n")
        f.write(json.dumps(dati["aider_context"], indent=2, ensure_ascii=False))
        f.write("\n```\n")
    print(f"    Scritto: {percorso_aider}")

    # 14b. Scrivi l'AI Brief (file compatto per Copilot)
    percorso_brief = os.path.join(cartella_report, f"{ts}_ai_brief.md")
    percorso_brief_ultimo = os.path.join(cartella_report, "AI_BRIEF.md")
    contenuto_brief = genera_ai_brief(dati)
    with open(percorso_brief, "w", encoding="utf-8") as f:
        f.write(contenuto_brief)
    with open(percorso_brief_ultimo, "w", encoding="utf-8") as f:
        f.write(contenuto_brief)
    print(f"    Scritto: {percorso_brief}")
    print(f"    Scritto: {percorso_brief_ultimo}")

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

    # 16. Changelog (confronto con ultimo snapshot)
    vecchio = carica_snapshot_precedente(percorso_ultimo)
    with open(percorso_changelog, "w", encoding="utf-8") as f:
        f.write(genera_changelog(vecchio, dati))
    print(f"    Scritto: {percorso_changelog}")

    # 17. Salva snapshot corrente per il prossimo confronto
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