import ast
import json
import os
import re
from collections import defaultdict


EXCLUDED_DIRS = {".git", "__pycache__", "venv", ".venv", ".idea", ".mypy_cache", ".pytest_cache"}
LOCAL_PREFIXES = ("gui", "service", "database", "db", "model", "core", "api", "routes", "app", "src")
FRAMEWORK_IMPORT_PATTERNS = ("PyQt5", "PyQt6", "PySide2", "PySide6", "tkinter", "flask", "fastapi", "django")


def normalize_name(name):
    return re.sub(r"[^a-zA-Z0-9_]", "", name or "")


class AnalizzatoreIntelligente(ast.NodeVisitor):
    def __init__(self, filename, tutti_i_contenuti):
        self.filename = filename
        self.tutti_i_contenuti = tutti_i_contenuti

        self.classi = []
        self.funzioni_globali = []
        self.import_interni = set()
        self.import_esterni = set()
        self.chiamate_funzioni = set()
        self.chiamate_esterne = set()
        self.tabelle_create = set()
        self.tabelle_interrogate = set()
        self.rotte_flask = []
        self.anomalie = []
        self.nomi_globali = set()
        self.variabili_globali = set()
        self.strings_rilevate = []

    def _add_anomaly(self, message):
        if message not in self.anomalie:
            self.anomalie.append(message)

    def _summary_from_doc(self, docstring):
        if not docstring:
            return ""
        summary = docstring.strip().split(".")[0].strip()
        return summary[:120] if summary else ""

    def _is_internal_module(self, nome_modulo):
        if not nome_modulo:
            return False
        nome = nome_modulo.replace(".", "/")
        return any(nome.startswith(prefix) or nome.startswith(f"./{prefix}") for prefix in LOCAL_PREFIXES)

    def visit_Import(self, node):
        for alias in node.names:
            nome = alias.name
            if any(p in nome for p in ("PyQt5", "PyQt6", "PySide2", "PySide6")):
                self._add_anomaly(
                    f"Incoerenza Framework: rilevato import `{nome}` (richiesto PySide6)"
                )
            if self._is_internal_module(nome):
                self.import_interni.add(nome)
            else:
                self.import_esterni.add(nome)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        modulo = node.module or ""
        if any(p in modulo for p in ("PyQt5", "PyQt6", "PySide2", "PySide6")):
            self._add_anomaly(
                f"Incoerenza Framework: rilevato import da `{modulo}` (richiesto PySide6)"
            )

        if any(modulo.startswith(prefix) for prefix in ("gui", "service", "database", "db", "core", "api", "routes", ".")):
            for alias in node.names:
                full_name = f"{modulo}.{alias.name}" if modulo else alias.name
                self.import_interni.add(full_name)
        elif modulo:
            self.import_esterni.add(modulo)

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        metodi = []
        self.nomi_globali.add(node.name)

        for subnode in node.body:
            if isinstance(subnode, ast.FunctionDef):
                docstring = ast.get_docstring(subnode) or ""
                metodi.append({
                    "nome": subnode.name,
                    "doc": self._summary_from_doc(docstring),
                })
                self.nomi_globali.add(subnode.name)

        doc_classe = ast.get_docstring(node) or ""
        self.classi.append({
            "nome": node.name,
            "doc": self._summary_from_doc(doc_classe),
            "metodi": metodi,
        })
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.nomi_globali.add(node.name)

        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                func = decorator.func
                is_flask_route = (
                    isinstance(func, ast.Attribute) and func.attr == "route"
                ) or (
                    isinstance(func, ast.Name) and func.id == "route"
                )
                if is_flask_route:
                    percorso_rotta = None
                    metodi_rotta = ["GET"]
                    if decorator.args and isinstance(decorator.args[0], ast.Constant):
                        percorso_rotta = decorator.args[0].value
                    for kw in decorator.keywords:
                        if kw.arg == "methods" and isinstance(kw.value, (ast.List, ast.Tuple)):
                            metodi_rotta = [
                                elt.value for elt in kw.value.elts if isinstance(elt, ast.Constant)
                            ]
                    if percorso_rotta:
                        self.rotte_flask.append({
                            "funzione": node.name,
                            "rotta": percorso_rotta,
                            "metodi": metodi_rotta,
                        })

        docstring = ast.get_docstring(node) or ""
        self.funzioni_globali.append({
            "nome": node.name,
            "doc": self._summary_from_doc(docstring),
        })
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variabili_globali.add(target.id)
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            nome = node.func.id
            self.chiamate_funzioni.add(nome)
            if nome not in self.nomi_globali:
                self.chiamate_esterne.add(nome)
        elif isinstance(node.func, ast.Attribute):
            nome = node.func.attr
            self.chiamate_funzioni.add(nome)
            if nome not in self.nomi_globali:
                self.chiamate_esterne.add(nome)
        self.generic_visit(node)

    def visit_Constant(self, node):
        if not isinstance(node.value, str):
            self.generic_visit(node)
            return

        valore = node.value
        self.strings_rilevate.append(valore)
        valore_upper = valore.upper()

        if "CREATE TABLE" in valore_upper:
            match = re.search(
                r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z0-9_]+)",
                valore,
                re.IGNORECASE,
            )
            if match:
                self.tabelle_create.add(match.group(1))

        if any(kw in valore_upper for kw in ("SELECT ", "INSERT INTO ", "UPDATE ", "DELETE FROM ")):
            self.tabelle_interrogate.update(re.findall(r"FROM\s+([a-zA-Z0-9_]+)", valore, re.IGNORECASE))
            self.tabelle_interrogate.update(re.findall(r"INSERT\s+INTO\s+([a-zA-Z0-9_]+)", valore, re.IGNORECASE))
            self.tabelle_interrogate.update(re.findall(r"UPDATE\s+([a-zA-Z0-9_]+)", valore, re.IGNORECASE))
            self.tabelle_interrogate.update(re.findall(r"DELETE\s+FROM\s+([a-zA-Z0-9_]+)", valore, re.IGNORECASE))

        if any(token in valore_upper for token in ("@APP.ROUTE", "/API/", "localhost", "127.0.0.1", "sqlite")):
            self._add_anomaly(f"Stringa di servizio/endpoint rilevata: `{valore[:100]}`")

        self.generic_visit(node)


def analizza_template_html(percorso_html):
    risultati = {"endpoint_chiamati": set(), "layer_mappa": set(), "librerie_esterne": set()}
    if not os.path.exists(percorso_html):
        return risultati

    with open(percorso_html, "r", encoding="utf-8", errors="ignore") as file:
        contenuto = file.read()

    risultati["endpoint_chiamati"].update(re.findall(r"['\"](/api/[^'\"]+|http[^'\"]+)['\"]", contenuto))
    risultati["layer_mappa"].update(re.findall(r"id:\s*['\"]([^'\"]+)['\"]", contenuto))
    risultati["librerie_esterne"].update(re.findall(r"<script[^>]+src=['\"]([^'\"]+)['\"]", contenuto))
    return risultati


def trova_file_progetto(root_dir):
    file_python = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            if file.endswith(".py"):
                percorso = os.path.join(root, file).replace("\\", "/")
                if percorso.startswith("./"):
                    percorso = percorso[2:]
                file_python.append(percorso)
    return sorted(set(file_python))


def costruisci_call_graph(moduli_analizzati, tutti_i_codici):
    definizioni = {}
    for f_path, modulo in moduli_analizzati.items():
        for cls in modulo.classi:
            definizioni[(f_path, cls["nome"])] = "classe"
        for fn in modulo.funzioni_globali:
            definizioni[(f_path, fn["nome"])] = "funzione"

    call_graph = defaultdict(set)
    for f_path, modulo in moduli_analizzati.items():
        for nome_chiamata in modulo.chiamate_funzioni:
            for altro_file, altro_modulo in moduli_analizzati.items():
                if f_path == altro_file:
                    if nome_chiamata in {x["nome"] for x in altro_modulo.funzioni_globali}:
                        call_graph[f_path].add((altro_file, nome_chiamata))
                    if nome_chiamata in {x["nome"] for x in altro_modulo.classi}:
                        call_graph[f_path].add((altro_file, nome_chiamata))
                else:
                    if nome_chiamata in {x["nome"] for x in altro_modulo.funzioni_globali}:
                        call_graph[f_path].add((altro_file, nome_chiamata))
                    if nome_chiamata in {x["nome"] for x in altro_modulo.classi}:
                        call_graph[f_path].add((altro_file, nome_chiamata))

    return {k: sorted(v) for k, v in call_graph.items()}


def infer_architettura(moduli_analizzati):
    tipi = {"ui": [], "database": [], "api": [], "core": [], "altro": []}
    for f_path, modulo in moduli_analizzati.items():
        lower = f_path.lower()
        if any(token in lower for token in ("gui", "view", "ui", "frontend", "widget")):
            tipi["ui"].append(f_path)
        elif any(token in lower for token in ("db", "database", "sql", "model")):
            tipi["database"].append(f_path)
        elif any(token in lower for token in ("api", "route", "routes", "server", "controller")):
            tipi["api"].append(f_path)
        elif any(token in lower for token in ("core", "service", "logic", "utils", "common")):
            tipi["core"].append(f_path)
        else:
            tipi["altro"].append(f_path)
    return tipi


def lista_file_per_tipo(root_dir):
    tipi = {"python": [], "html": [], "js": [], "css": [], "other": []}
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            nome = file.lower()
            if nome.endswith(".py"):
                tipi["python"].append(os.path.join(root, file).replace("\\", "/"))
            elif nome.endswith((".html", ".htm")):
                tipi["html"].append(os.path.join(root, file).replace("\\", "/"))
            elif nome.endswith(".js"):
                tipi["js"].append(os.path.join(root, file).replace("\\", "/"))
            elif nome.endswith(".css"):
                tipi["css"].append(os.path.join(root, file).replace("\\", "/"))
            else:
                tipi["other"].append(os.path.join(root, file).replace("\\", "/"))
    return tipi


def build_ai_summary(dati_json):
    sintesi = dati_json["sintesi"]
    moduli = dati_json["moduli"]
    backend_routes = dati_json["architettura"]["rotte_api"]
    orfani = dati_json["dipendenze"]["simboli_orfani"]

    summary = {
        "project_name": os.path.basename(os.getcwd()),
        "totale_moduli": sintesi["totale_moduli"],
        "totale_classi": sintesi["totale_classi"],
        "totale_funzioni": sintesi["totale_funzioni"],
        "endpoint_flask": len(backend_routes),
        "tabelle_rilevate": sintesi["totale_tabelle"],
        "simboli_orfani": len(orfani),
        "moduli_chiave": sorted(
            [f_path for f_path, data in moduli.items() if data["classi"] or data["funzioni"]]
        )[:10],
        "warning_flags": [],
    }

    if len(orfani) > 0:
        summary["warning_flags"].append("simboli_orfani")
    if summary["endpoint_flask"] == 0:
        summary["warning_flags"].append("nessuna_rotta_backend")
    if not sintesi["librerie_esterne"]:
        summary["warning_flags"].append("nessuna_libreria_estera_rilevata")
    if summary["totale_moduli"] < 5:
        summary["warning_flags"].append("progetto_piccolo")

    return summary


def build_agent_insights(dati_json):
    moduli = dati_json["moduli"]
    routes = dati_json["architettura"]["rotte_api"]
    orfani = dati_json["dipendenze"]["simboli_orfani"]
    hot_spots = []

    for f_path, data in moduli.items():
        score = (
            len(data.get("classi", [])) * 3
            + len(data.get("funzioni", [])) * 2
            + len(data.get("anomalie", [])) * 4
            + len(data.get("chiamate_funzioni", []))
        )
        hot_spots.append({
            "file": f_path,
            "score": score,
            "classi": len(data.get("classi", [])),
            "funzioni": len(data.get("funzioni", [])),
            "anomalie": len(data.get("anomalie", [])),
        })

    hot_spots = sorted(hot_spots, key=lambda item: item["score"], reverse=True)[:5]

    risk_level = "basso"
    if len(orfani) > 5 or len(routes) == 0 or any(item["anomalie"] > 0 for item in hot_spots):
        risk_level = "medio"
    if len(orfani) > 15 or any(item["score"] > 30 for item in hot_spots):
        risk_level = "alto"

    recommendations = []
    if orfani:
        recommendations.append("Rivedere i simboli orfani e decidere se integrarli, rimuoverli o spostarli in moduli più appropriati.")
    if not routes:
        recommendations.append("Controllare se il backend è davvero presente o se l'applicazione è prevalentemente frontend-only.")
    if hot_spots:
        recommendations.append("Priorizzare i file con score più alto per refactor e verifica di coerenza architetturale.")
    recommendations.append("Usare il JSON di analisi come contesto minimo per future modifiche e per ridurre il numero di token richiesti ai tool AI.")

    return {
        "risk_level": risk_level,
        "hotspots": hot_spots,
        "recommended_actions": recommendations,
        "likely_entrypoints": sorted(dati_json["architettura"].get("entry_points", [])),
        "critical_files": [item["file"] for item in hot_spots[:3]],
    }


def build_aider_context(dati_json):
    agent = dati_json["agent_insights"]
    sintesi = dati_json["sintesi"]
    moduli = dati_json["moduli"]

    risky = []
    for f_path, data in moduli.items():
        score = len(data.get("anomalie", [])) * 5 + len(data.get("chiamate_funzioni", []))
        risky.append({"file": f_path, "score": score})
    risky.sort(key=lambda x: x["score"], reverse=True)

    brief = {
        "title": "Project agent brief",
        "summary": {
            "modules": sintesi["totale_moduli"],
            "classes": sintesi["totale_classi"],
            "functions": sintesi["totale_funzioni"],
            "routes": len(dati_json["architettura"]["rotte_api"]),
            "risk": agent["risk_level"],
        },
        "key_findings": [
            f"Rischio architetturale: {agent['risk_level']}",
            f"Simboli orfani: {len(dati_json['dipendenze']['simboli_orfani'])}",
            f"File critici: {', '.join(agent['critical_files']) if agent['critical_files'] else 'nessuno'}",
        ],
        "priority_order": [item["file"] for item in risky[:5]],
        "next_steps": agent["recommended_actions"],
        "agent_prompt": (
            "Analizza il progetto usando il dataset di PROGETTO_INDEX.json. "
            "Priorità massima ai file critici e ai simboli orfani, poi verifica rotti o duplicati. "
            "Propone un refactor minimo ma sicuro e documenta le modifiche."
        ),
    }
    return brief


def build_priority_plan(dati_json):
    moduli = dati_json["moduli"]
    critici = []
    for f_path, data in moduli.items():
        score = (
            len(data.get("anomalie", [])) * 5
            + len(data.get("classi", [])) * 2
            + len(data.get("funzioni", []))
            + len(data.get("chiamate_funzioni", []))
        )
        critici.append({"file": f_path, "score": score})
    critici.sort(key=lambda item: item["score"], reverse=True)

    phases = [
        {
            "phase": "1. Valutazione rapida",
            "focus": [item["file"] for item in critici[:3]],
            "goal": "Identificare i file più critici da leggere per prima.",
        },
        {
            "phase": "2. Consolidamento architettura",
            "focus": [item["file"] for item in critici[3:6]],
            "goal": "Ridurre duplicazioni, simboli orfani e dipendenze confuse.",
        },
        {
            "phase": "3. Stabilizzazione e refactor",
            "focus": [item["file"] for item in critici[6:]],
            "goal": "Rendere il sistema più coerente e più semplice da mantenere.",
        },
    ]

    return {
        "summary": "Piano d'azione per interventi mirati e minimali.",
        "phases": phases,
        "immediate_actions": [
            "Verifica moduli critici con più anomalie e chiamate.",
            "Riduci simboli orfani e import non usati.",
            "Consolida le rotte/entry point e controlla backend/frontend coupling.",
        ],
    }


def scan_non_python_files(root_dir):
    findings = {"html": {"endpoints": set(), "scripts": set(), "ids": set()}, "js": {"endpoints": set(), "calls": set()}, "css": {"selectors": set()}}
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            lower = file.lower()
            if not lower.endswith((".html", ".htm", ".js", ".css")):
                continue
            path = os.path.join(root, file).replace("\\", "/")
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                    content = handle.read()
            except Exception:
                continue

            if lower.endswith((".html", ".htm")):
                findings["html"]["endpoints"].update(re.findall(r"['\"](/api/[^'\"]+|http[^'\"]+)['\"]", content))
                findings["html"]["scripts"].update(re.findall(r"<script[^>]+src=['\"]([^'\"]+)['\"]", content))
                findings["html"]["ids"].update(re.findall(r"id:\s*['\"]([^'\"]+)['\"]", content))
            elif lower.endswith(".js"):
                findings["js"]["endpoints"].update(re.findall(r"['\"](/api/[^'\"]+|http[^'\"]+)['\"]", content))
                findings["js"]["calls"].update(re.findall(r"(?:fetch|axios\.(?:get|post|put|delete))\s*\(\s*['\"]([^'\"]+)['\"]", content))
            elif lower.endswith(".css"):
                findings["css"]["selectors"].update(re.findall(r"\.([A-Za-z0-9_-]+)|#([A-Za-z0-9_-]+)", content))

    return {k: {subk: sorted(v) for subk, v in vdict.items()} for k, vdict in findings.items()}


def build_ultra_compact_prompt(dati_json):
    agent = dati_json["agent_insights"]
    summary = dati_json["ai_summary"]
    project = os.path.basename(os.getcwd())
    prompt = (
        f"Progetto: {project}. "
        f"Contesto: {summary['totale_moduli']} moduli, {summary['totale_classi']} classi, {summary['totale_funzioni']} funzioni, "
        f"{summary['endpoint_flask']} endpoint Flask, {summary['simboli_orfani']} simboli orfani. "
        f"Rischio: {agent['risk_level']}. "
        f"File critici: {', '.join(agent['critical_files']) if agent['critical_files'] else 'nessuno'}. "
        f"Priorità: correggere simboli orfani, verificare file critici e consolidare dipendenze. "
        f"Usa PROGETTO_INDEX.json come fonte di verità e minimizza i cambiamenti."
    )
    return prompt


def genera_report_markdown(dati_json):
    sintesi = dati_json["sintesi"]
    arch = dati_json["architettura"]
    dep = dati_json["dipendenze"]
    routes = arch["rotte_api"]
    moduli = dati_json["moduli"]

    lines = []
    lines.append("# Progetto: analisi architetturale")
    lines.append("")
    lines.append(f"- Moduli Python: {sintesi['totale_moduli']}")
    lines.append(f"- Classi: {sintesi['totale_classi']}")
    lines.append(f"- Funzioni: {sintesi['totale_funzioni']}")
    lines.append(f"- Rotte Flask: {len(routes)}")
    lines.append(f"- Tabelle rilevate: {sintesi['totale_tabelle']}")
    lines.append(f"- Simboli orfani: {len(dep['simboli_orfani'])}")
    lines.append("")

    lines.append("## Struttura architetturale")
    for layer_name, items in arch["strati"].items():
        if items:
            lines.append(f"- {layer_name}: {', '.join(items[:5]) + (' ...' if len(items) > 5 else '')}")
    lines.append("")

    lines.append("## Endpoint backend")
    if routes:
        for rotta, info in routes.items():
            lines.append(f"- {rotta} -> {info['funzione']} ({', '.join(info['metodi'])})")
    else:
        lines.append("- Nessuna rotta Flask rilevata")
    lines.append("")

    lines.append("## Frontend & mappe")
    frontend = arch["frontend_mappa"]
    if frontend["endpoint_utilizzati"]:
        lines.append(f"- Endpoint frontend usati: {', '.join(frontend['endpoint_utilizzati'][:10])}")
    if frontend["layer_mappa"]:
        lines.append(f"- Layer mappa: {', '.join(frontend['layer_mappa'][:10])}")
    if frontend["librerie_esterne"]:
        lines.append(f"- Librerie: {', '.join(frontend['librerie_esterne'][:10])}")
    lines.append("")

    lines.append("## Simboli orfani")
    if dep["simboli_orfani"]:
        for symbol in dep["simboli_orfani"][:20]:
            lines.append(f"- {symbol['tipo']}: {symbol['simbolo']} ({symbol['file']})")
    else:
        lines.append("- Nessun simbolo orfano rilevato")
    lines.append("")

    lines.append("## Moduli con più segnali")
    ranked = sorted(
        moduli.items(),
        key=lambda item: (len(item[1].get("classi", [])) + len(item[1].get("funzioni", []))),
        reverse=True,
    )[:10]
    for f_path, data in ranked:
        lines.append(f"- {f_path}: {len(data['classi'])} classi, {len(data['funzioni'])} funzioni")
    lines.append("")

    lines.append("## Insight per agente IA")
    agent = build_agent_insights(dati_json)
    lines.append(f"- Livello di rischio: {agent['risk_level']}")
    if agent["critical_files"]:
        lines.append(f"- File critici: {', '.join(agent['critical_files'])}")
    if agent["likely_entrypoints"]:
        lines.append(f"- Entry point probabili: {', '.join(agent['likely_entrypoints'])}")
    for action in agent["recommended_actions"]:
        lines.append(f"- Azione: {action}")
    lines.append("")

    lines.append("## Brano operativo per aider / agente AI")
    context = build_aider_context(dati_json)
    priority = build_priority_plan(dati_json)
    lines.append(f"- Priorità: {', '.join(context['priority_order'][:3]) if context['priority_order'] else 'nessuna'}")
    lines.append(f"- Prompt: {context['agent_prompt']}")
    for phase in priority["phases"]:
        lines.append(f"- {phase['phase']}: {', '.join(phase['focus'])}")
    lines.append("")

    lines.append("## Prompt ultra-compatto")
    lines.append(build_ultra_compact_prompt(dati_json))
    lines.append("")

    return "\n".join(lines)


def esegui_diagnostica_totale():
    print("=== AVVIO DIAGNOSTICA PROFONDA (MINI-AI LOCALE) ===")

    base_dir = "."
    file_python = trova_file_progetto(base_dir)
    tutti_i_codici = {}

    for f_path in file_python:
        if os.path.basename(f_path) == "analizza_progetto_definitivo.py":
            continue
        try:
            with open(f_path, "r", encoding="utf-8", errors="ignore") as file:
                contenuto = file.read().lstrip("\ufeff")
                tutti_i_codici[f_path] = contenuto
        except Exception:
            pass

    moduli_analizzati = {}
    for percorso_file, codice in tutti_i_codici.items():
        try:
            tree = ast.parse(codice, filename=percorso_file)
            analizzatore = AnalizzatoreIntelligente(percorso_file, tutti_i_codici)
            analizzatore.visit(tree)
            moduli_analizzati[percorso_file] = analizzatore
        except Exception as exc:
            print(f"Errore parsing su {percorso_file}: {exc}")

    tutte_le_tabelle_create = set()
    tutte_le_tabelle_interrogate = set()
    tutte_le_rotte_backend = {}
    tutti_i_nomi_globali = {}
    tutte_le_chiamate = set()
    tutte_le_import_esterni = set()
    tutti_i_moduli = defaultdict(set)

    for f_path, modulo in moduli_analizzati.items():
        tutte_le_tabelle_create.update(modulo.tabelle_create)
        tutte_le_tabelle_interrogate.update(modulo.tabelle_interrogate)
        tutte_le_import_esterni.update(modulo.import_esterni)

        for rotta in modulo.rotte_flask:
            tutte_le_rotte_backend[rotta["rotta"]] = {
                "file": f_path,
                "funzione": rotta["funzione"],
                "metodi": rotta["metodi"],
            }

        for classe in modulo.classi:
            nome = classe["nome"]
            tutti_i_nomi_globali[nome] = (f_path, "classe")
            tutti_i_moduli[f_path].add(nome)

        for funzione in modulo.funzioni_globali:
            nome = funzione["nome"]
            tutti_i_nomi_globali[nome] = (f_path, "funzione")
            tutti_i_moduli[f_path].add(nome)

        tutte_le_chiamate.update(modulo.chiamate_funzioni)

    simboli_orfani = []
    for nome_simbolo, (file_def, tipo_simbolo) in tutti_i_nomi_globali.items():
        if nome_simbolo in {"__init__", "main", "init_ui", "setup_ui", "run", "salva"}:
            continue

        conteggio_citazioni = 0
        for f_path, codice in tutti_i_codici.items():
            if f_path != file_def and re.search(r"\b" + re.escape(nome_simbolo) + r"\b", codice):
                conteggio_citazioni += 1

        if conteggio_citazioni == 0:
            simboli_orfani.append({
                "simbolo": nome_simbolo,
                "tipo": tipo_simbolo,
                "file": file_def,
            })

    graph = costruisci_call_graph(moduli_analizzati, tutti_i_codici)
    struttura = infer_architettura(moduli_analizzati)

    percorso_template = os.path.join("templates", "map_view.html")
    info_mappa = analizza_template_html(percorso_template)

    dati_json = {
        "sintesi": {
            "totale_moduli": len(moduli_analizzati),
            "totale_classi": sum(len(modulo.classi) for modulo in moduli_analizzati.values()),
            "totale_funzioni": sum(len(modulo.funzioni_globali) for modulo in moduli_analizzati.values()),
            "totale_rotte_flask": len(tutte_le_rotte_backend),
            "totale_tabelle": len(tutte_le_tabelle_create | tutte_le_tabelle_interrogate),
            "tabelle_create": sorted(tutte_le_tabelle_create),
            "tabelle_interrogate": sorted(tutte_le_tabelle_interrogate),
            "librerie_esterne": sorted(tutte_le_import_esterni),
        },
        "architettura": {
            "strati": struttura,
            "entry_points": sorted({name for name, (_, tipo) in tutti_i_nomi_globali.items() if tipo == "funzione" and name.lower() in {"main", "run", "start", "app"}}),
            "rotte_api": tutte_le_rotte_backend,
            "frontend_mappa": {
                "endpoint_utilizzati": sorted(info_mappa["endpoint_chiamati"]),
                "layer_mappa": sorted(info_mappa["layer_mappa"]),
                "librerie_esterne": sorted(info_mappa["librerie_esterne"]),
            },
        },
        "dipendenze": {
            "call_graph": graph,
            "simboli_orfani": simboli_orfani,
            "chiamate_globali": sorted(tutte_le_chiamate),
        },
        "moduli": {},
    }

    for f_path, modulo in moduli_analizzati.items():
        dati_json["moduli"][f_path] = {
            "classi": [classe["nome"] for classe in modulo.classi],
            "funzioni": [funzione["nome"] for funzione in modulo.funzioni_globali],
            "import_interni": sorted(modulo.import_interni),
            "import_esterni": sorted(modulo.import_esterni),
            "tabelle_usate": sorted(modulo.tabelle_interrogate | modulo.tabelle_create),
            "anomalie": modulo.anomalie,
            "chiamate_funzioni": sorted(modulo.chiamate_funzioni),
        }

    ai_summary = build_ai_summary(dati_json)
    dati_json["ai_summary"] = ai_summary
    dati_json["files_by_type"] = lista_file_per_tipo(".")
    dati_json["non_python_signals"] = scan_non_python_files(".")

    agent_insights = build_agent_insights(dati_json)
    dati_json["agent_insights"] = agent_insights
    dati_json["aider_context"] = build_aider_context(dati_json)
    dati_json["priority_plan"] = build_priority_plan(dati_json)
    dati_json["ultra_compact_prompt"] = build_ultra_compact_prompt(dati_json)

    with open("PROGETTO_INDEX.json", "w", encoding="utf-8") as file:
        json.dump(dati_json, file, indent=2, ensure_ascii=False)

    report_markdown = genera_report_markdown(dati_json)
    with open("PROGETTO_REPORT.md", "w", encoding="utf-8") as file:
        file.write(report_markdown)

    with open("AIDER_CONTEXT.md", "w", encoding="utf-8") as file:
        file.write(
            "# Aider context\n\n"
            + json.dumps(
                {
                    "aider_context": dati_json["aider_context"],
                    "priority_plan": dati_json["priority_plan"],
                    "ultra_compact_prompt": dati_json["ultra_compact_prompt"],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        )

    with open("PROMPT_AGENTE.md", "w", encoding="utf-8") as file:
        file.write(dati_json["ultra_compact_prompt"] + "\n")

    print(f"Moduli Python scanditi: {len(moduli_analizzati)}")
    print(f"Classi rilevate: {sum(len(m.classi) for m in moduli_analizzati.values())}")
    print(f"Funzioni rilevate: {sum(len(m.funzioni_globali) for m in moduli_analizzati.values())}")
    print(f"Endpoint Flask rilevati: {len(tutte_le_rotte_backend)}")
    print(f"Tabelle trovate: {len(tutte_le_tabelle_create | tutte_le_tabelle_interrogate)}")
    print(f"Simboli orfani: {len(simboli_orfani)}")
    print("JSON generato: PROGETTO_INDEX.json")
    print("Report generato: PROGETTO_REPORT.md")
    print("Context AI generato: AIDER_CONTEXT.md")


if __name__ == "__main__":
    esegui_diagnostica_totale()
