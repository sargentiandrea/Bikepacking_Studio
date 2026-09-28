import os
import ast
import json
import re

class AnalizzatoreModulo(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.classi = []
        self.funzioni_globali = []
        self.import_interni = set()
        self.import_esterni = set()
        self.chiamate_funzioni = set()
        self.tabelle_create = set()
        self.tabelle_interrogate = set()
        self.rotte_flask = []
        self.anomalie = []

    def visit_Import(self, node):
        for alias in node.names:
            nome = alias.name
            if "PyQt5" in nome or "PyQt6" in nome:
                self.anomalie.append(f"Incoerenza Framework: Rilevato import `{nome}` (richiesto PySide6)")
            if any(nome.startswith(prefix) for prefix in ["gui", "service", "database", "core", "model"]):
                self.import_interni.add(nome)
            else:
                self.import_esterni.add(nome)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        modulo = node.module or ""
        if "PyQt5" in modulo or "PyQt6" in modulo:
            self.anomalie.append(f"Incoerenza Framework: Rilevato import da `{modulo}` (richiesto PySide6)")
            
        full_module = modulo
        if any(full_module.startswith(prefix) for prefix in ["gui", "service", "database", "core", "model", "."]):
            for alias in node.names:
                self.import_interni.add(f"{full_module}.{alias.name}" if full_module else alias.name)
        else:
            self.import_esterni.add(modulo)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        metodi = []
        for subnode in node.body:
            if isinstance(subnode, ast.FunctionDef):
                docstring = ast.get_docstring(subnode)
                desc = docstring.split('.')[0].strip() if docstring else ""
                metodi.append({"nome": subnode.name, "doc": desc})
        doc_classe = ast.get_docstring(node)
        self.classi.append({
            "nome": node.name,
            "doc": doc_classe.split('.')[0].strip() if doc_classe else "",
            "metodi": metodi
        })
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                func = decorator.func
                if (isinstance(func, ast.Attribute) and func.attr == 'route') or \
                   (isinstance(func, ast.Name) and func.id == 'route'):
                    percorso_rotta = None
                    metodi_rotta = ["GET"]
                    if decorator.args and isinstance(decorator.args[0], ast.Constant):
                        percorso_rotta = decorator.args[0].value
                    for kw in decorator.keywords:
                        if kw.arg == "methods" and isinstance(kw.value, (ast.List, ast.Tuple)):
                            metodi_rotta = [elt.value for elt in kw.value.elts if isinstance(elt, ast.Constant)]
                    if percorso_rotta:
                        self.rotte_flask.append({
                            "funzione": node.name,
                            "rotta": percorso_rotta,
                            "metodi": metodi_rotta
                        })

        if node.col_offset == 0:
            docstring = ast.get_docstring(node)
            desc = docstring.split('.')[0].strip() if docstring else ""
            self.funzioni_globali.append({"nome": node.name, "doc": desc})
            
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.chiamate_funzioni.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.chiamate_funzioni.add(node.func.attr)
        self.generic_visit(node)

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            val = node.value
            val_upper = val.upper()
            
            if "CREATE TABLE" in val_upper:
                match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z0-9_]+)', val, re.IGNORECASE)
                if match:
                    self.tabelle_create.add(match.group(1))

            if any(sql_kw in val_upper for sql_kw in ["SELECT ", "INSERT INTO ", "UPDATE ", "DELETE FROM "]):
                tabelle_select = re.findall(r'FROM\s+([a-zA-Z0-9_]+)', val, re.IGNORECASE)
                tabelle_insert = re.findall(r'INSERT\s+INTO\s+([a-zA-Z0-9_]+)', val, re.IGNORECASE)
                tabelle_update = re.findall(r'UPDATE\s+([a-zA-Z0-9_]+)', val, re.IGNORECASE)
                tabelle_delete = re.findall(r'DELETE\s+FROM\s+([a-zA-Z0-9_]+)', val, re.IGNORECASE)
                
                for tab in (tabelle_select + tabelle_insert + tabelle_update + tabelle_delete):
                    if tab.upper() not in ["SELECT", "WHERE", "JOIN", "GROUP", "ORDER", "SET", "VALUES", "AS"]:
                        self.tabelle_interrogate.add(tab)

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

def scansiona_file_progetto():
    file_python = []
    ignora_cartelle = [".git", "__pycache__", "venv", ".idea", "build", "dist"]
    
    for root, dirs, files in os.walk("."):
        if any(escludi in root for escludi in ignora_cartelle):
            continue
        for file in files:
            if file.endswith(".py"):
                percorso = os.path.join(root, file).replace("\\", "/")
                if percorso.startswith("./"):
                    percorso = percorso[2:]
                file_python.append(percorso)
    return sorted(list(set(file_python)))

def esegui_diagnostica_totale():
    print("=== AVVIO DIAGNOSTICA PROFONDA STRUTTURATA ===")
    
    file_python = scansiona_file_progetto()
    moduli_analizzati = {}
    tutti_i_codici = {}
    
    for f_path in file_python:
        try:
            with open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
                codice = f.read()
                tutti_i_codici[f_path] = codice
                tree = ast.parse(codice, filename=f_path)
                analizzatore = AnalizzatoreModulo(f_path)
                analizzatore.visit(tree)
                moduli_analizzati[f_path] = analizzatore
        except Exception as e:
            print(f"Errore parsing su {f_path}: {e}")

    tutte_le_tabelle_create = set()
    tutte_le_tabelle_interrogate = set()
    tutte_le_rotte_backend = {}
    tutti_i_nomi_globali = {}
    tutte_le_chiamate = set()

    for f_path, mod in moduli_analizzati.items():
        tutte_le_tabelle_create.update(mod.tabelle_create)
        tutte_le_tabelle_interrogate.update(mod.tabelle_interrogate)
        for r in mod.rotte_flask:
            tutte_le_rotte_backend[r["rotta"]] = {
                "file": f_path,
                "funzione": r["funzione"],
                "metodi": r["metodi"]
            }
        for cl in mod.classi:
            tutti_i_nomi_globali[cl["nome"]] = (f_path, "classe")
        for fn in mod.funzioni_globali:
            tutti_i_nomi_globali[fn["nome"]] =