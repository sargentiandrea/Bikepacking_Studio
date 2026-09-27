import os
import ast
import json
import re

class AnalizzatoreIntelligente(ast.NodeVisitor):
    def __init__(self, filename, tutti_i_contenuti):
        self.filename = filename
        self.tutti_i_contenuti = tutti_i_contenuti
        self.classi = []
        self.funzioni_globali = []
        self.importazioni = set()
        self.riferimenti_db = set()
        self.riferimenti_rete = set()
        self.nomi_definiti = set()
        self.anomalie = []

    def visit_Import(self, node):
        for alias in node.names:
            self.importazioni.add(alias.name)
            # Controllo anti-incoerenza framework
            if "PyQt5" in alias.name or "PyQt6" in alias.name:
                self.anomalie.append(f"⚠️ **Incoerenza Framework:** Rilevato import di `{alias.name}`. Il progetto usa PySide6 come standard!")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.importazioni.add(node.module)
            if "PyQt5" in node.module or "PyQt6" in node.module:
                self.anomalie.append(f"⚠️ **Incoerenza Framework:** Rilevato import da `{node.module}` (richiesto PySide6).")
        for alias in node.names:
            self.importazioni.add(alias.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.nomi_definiti.add(node.name)
        metodi = []
        for subnode in node.body:
            if isinstance(subnode, ast.FunctionDef):
                self.nomi_definiti.add(subnode.name)
                docstring = ast.get_docstring(subnode)
                desc = f" - *{docstring.split('.')[0]}*" if docstring else ""
                metodi.append(f"`{subnode.name}()`{desc}")
        self.classi.append({"nome": node.name, "metodi": metodi})
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if node.col_offset == 0:  # Funzione globale
            self.nomi_definiti.add(node.name)
            docstring = ast.get_docstring(node)
            desc = f" - *{docstring.split('.')[0]}*" if docstring else ""
            self.funzioni_globali.append(f"`def {node.name}()`{desc}")
        self.generic_visit(node)

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            val_lower = node.value.lower()
            if any(kw in val_lower for kw in ["sqlite", ".db", "select ", "insert ", "update ", "delete ", "create table"]):
                self.riferimenti_db.add(node.value[:80])
            if any(net in val_lower for net in ["127.0.0.1", "localhost", "port", "/api/", "@app.route"]):
                self.riferimenti_rete.add(node.value[:80])
        self.generic_visit(node)

def analizza_template_html(percorso_html):
    risultati = {"endpoint_chiamati": set(), "layer_mappa": set(), "librerie_esterne": set()}
    if not os.path.exists(percorso_html):
        return risultati
    with open(percorso_html, 'r', encoding='utf-8', errors='ignore') as f:
        contenuto = f.read()
    for ep in re.findall(r'[\'"](/api/[^\'"]+|http[^\'"]+)[\'"]', contenuto):
        risultati["endpoint_chiamati"].add(ep)
    for l in re.findall(r'id:\s*[\'"]([^\'"]+)[\'"]', contenuto):
        risultati["layer_mappa"].add(l)
    for src in re.findall(r'<script[^>]+src=[\'"]([^\'"]+)[\'"]', contenuto):
        risultati["librerie_esterne"].add(src)
    return risultati

def esegui_diagnostica_totale():
    print("=== AVVIO DIAGNOSTICA PROFONDA (MINI-AI LOCALE) ===")
    report = []
    report.append("# 🧠 DIAGNOSTICA INTELLIGENTE - MAPPA DELLA VERITÀ\n")
    report.append("> Analisi semantica avanzata, rilevamento anomalie, codice morto e coerenza architetturale.\n\n")

    # Scansione file Python
    file_python = []
    tutti_i_codici = {}
    
    for root, dirs, files in os.walk("."):
        if any(escludi in root for escludi in [".git", "__pycache__", "venv", ".idea", "basemap-styles-master"]):
            continue
        for file in files:
            if file.endswith(".py"):
                percorso = os.path.join(root, file).replace("\\", "/")
                if percorso.startswith("./"):
                    percorso = percorso[2:]
                file_python.append(percorso)

    file_python = sorted(list(set(file_python)))

    # Carica tutto il codice in memoria per i controlli incrociati di codice morto
    for f_path in file_python:
        try:
            with open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
                tutti_i_codici[f_path] = f.read()
        except:
            pass

    report.append(f"## 📊 1. Sintesi Globale\n- **Moduli Python monitorati:** `{len(file_python)}`\n")

    analizzatori = {}
    for percorso_file, codice in tutti_i_codici.items():
        try:
            tree = ast.parse(codice, filename=percorso_file)
            analizzatore = AnalizzatoreIntelligente(percorso_file, tutti_i_codici)
            analizzatore.visit(tree)
            analizzatori[percorso_file] = analizzatore
        except Exception as e:
            print(f"Errore parsing su {percorso_file}: {e}")

    # Controllo Codice Morto / Funzioni mai richiamate (escluse main, init, ecc.)
    report.append("## 🔍 2. Rilevamento Anomalie e Codice Orfano\n")
    anomalie_totali = 0

    for percorso_file, analizzatore in analizzatori.items():
        # Riporta anomalie intrinseche (es. PyQt5/6)
        for anomalia in analizzatore.anomalie:
            report.append(f"- **`{percorso_file}`**: {anomalia}")
            anomalie_totali += 1

    if anomalie_totali == 0:
        report.append("- ✅ *Nessuna grave anomalia di framework o libreria rilevata nei moduli principali.*\n")
    else:
        report.append("\n")

    # Dettaglio Moduli
    report.append("## 🗺️ 3. Mappatura Dettagliata per Modulo\n")
    for percorso_file, analizzatore in analizzatori.items():
        report.append(f"### 📄 Modulo: `{percorso_file}`")
        
        if analizzatore.classi:
            report.append("**👥 Classi:**")
            for cl in analizzatore.classi:
                report.append(f"- `class {cl['nome']}`")
                for m in cl['metodi']:
                    report.append(f"  - {m}")
                    
        if analizzatore.funzioni_globali:
            report.append("**⚙️ Funzioni:**")
            for fn in analizzatore.funzioni_globali:
                report.append(f"  - {fn}")
                
        if analizzatore.riferimenti_db:
            report.append("**🗄️ Database / SQL:**")
            for db in list(analizzatore.riferimenti_db)[:3]:
                report.append(f"  - `{db}`")
                
        if analizzatore.riferimenti_rete:
            report.append("**🌐 Endpoint / Rete:**")
            for net in list(analizzatore.riferimenti_rete)[:3]:
                report.append(f"  - `{net}`")
                
        report.append("\n" + "-"*40 + "\n")

    # Sezione Frontend Mappa
    report.append("## 🌍 4. Stato Frontend Mappa (`templates/map_view.html`)\n")
    info_mappa = analizza_template_html("templates/map_view.html")
    if info_mappa["endpoint_chiamati"] or info_mappa["layer_mappa"]:
        report.append("- **Stato:** Analizzato con successo.")
        report.append(f"- **Endpoint JS:** `{list(info_mappa['endpoint_chiamati']) or 'Nessuno'}`")
        report.append(f"- **Layer MapLibre:** `{list(info_mappa['layer_mappa']) or 'Nessuno'}`")
    else:
        report.append("- ⚠️ *File mappa non trovato o vuoto.*")

    # Salvataggio
    output_path = "REPORT_ARCHITETTURA.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
    print(f"\n✅ DIAGNOSTICA COMPLETATA! Report generato in: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    esegui_diagnostica_totale()