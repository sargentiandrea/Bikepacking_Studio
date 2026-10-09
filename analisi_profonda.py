"""Fotografia locale verificabile di Bikepacking Studio (solo libreria standard).

python analisi_profonda.py             aggiorna i report correnti
python analisi_profonda.py --check     analizza senza scrivere
python analisi_profonda.py --no-db     non apre il database
Il progetto predefinito è la cartella dello script, non quella del terminale.
Nessun modulo applicativo viene importato. Nessuna chiamata a servizi o push.
"""
import argparse
import ast
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit, urlunsplit

VERSION = '4.1'
SCHEMA = 4
ROOT = Path(__file__).resolve().parent
EXCLUDED = {'.git', '__pycache__', 'venv', '.venv', '.idea', '.agents', '.codex',
            '.aws', '.mypy_cache', '.pytest_cache', 'build', 'dist', 'node_modules',
            '.vscode', 'REPORT', 'basemap-styles-master', 'data', 'fonts', 'gpx', 'GPX CORSICA'}
GENERATED = {'analisi.json', 'AI_BRIEF.md', 'report.md', 'DB_SCHEMA.md', 'CONFIG_FILES.md',
             'EXTERNAL_SERVICES.md', 'riepilogo.txt', 'STATO_ATTUALE.md', 'PERCORSO.md', 'ULTIMO_RUN.json'}
CONFIG_EXT = {'.json', '.yaml', '.yml', '.ini', '.cfg', '.toml'}
FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)
FORBIDDEN_UI = {'PyQt5', 'PyQt6', 'PySide2', 'tkinter'}
URL_RE = re.compile(r'https?://[^\s\"\'<>`\\)]+')
SECRET_RE = re.compile(r'(?i)(api[_-]?key|secret|password|passwd|token|credential)')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def text(path):
    return path.read_text(encoding='utf-8-sig')


def proof(file, line, **values):
    return dict(file=file, riga=line, **values)


def sources(root):
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED and not Path(directory, d).is_symlink())
        for name in sorted(files):
            path = Path(directory, name)
            if not path.is_symlink() and name != Path(__file__).name:
                yield path


def dotted(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted(node.value)
        return base + '.' + node.attr if base else node.attr
    return ''


def string(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return ''.join(n.value if isinstance(n, ast.Constant) and isinstance(n.value, str)
                       else '{dinamico}' for n in node.values)
    return None


def clean_url(value):
    """Omettere credenziali, parametri e frammenti; non esportare valori segreti."""
    try:
        u = urlsplit(value.rstrip('.,;'))
        path = '/[percorso omesso]' if SECRET_RE.search(u.path) else u.path
        return urlunsplit((u.scheme, u.netloc.rsplit('@', 1)[-1], path, '', ''))
    except ValueError:
        return '[URL non interpretabile]'


def url_scope(url):
    if '{' in url:
        return 'parametrizzato'
    try:
        host = urlsplit(url).hostname or ''
        if host == 'localhost' or ipaddress.ip_address(host).is_loopback:
            return 'locale'
    except ValueError:
        pass
    return 'remoto'


class Inspector(ast.NodeVisitor):
    def __init__(self, file):
        self.file = file
        self.scope = []
        self.symbols, self.imports, self.refs, self.routes, self.sql, self.urls = [], [], [], [], [], []

    def definition(self, node, kind):
        name = '.'.join([n for n, _ in self.scope] + [node.name])
        row = proof(self.file, node.lineno, nome=node.name, qualificato=name, tipo=kind,
                    fine_riga=node.end_lineno, asincrona=isinstance(node, ast.AsyncFunctionDef),
                    decoratori=[dotted(d.func if isinstance(d, ast.Call) else d) for d in node.decorator_list],
                    id=f'{self.file}:{name}:{node.lineno}')
        if isinstance(node, FUNCTIONS):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                if isinstance(body[0].value.value, str):
                    body = body[1:]
            if sum(1 for s in body for _ in ast.walk(s)) >= 12:
                row['corpo_sha256'] = sha('\n'.join(ast.dump(s, include_attributes=False) for s in body).encode())
        self.symbols.append(row)
        return row

    def visit_ClassDef(self, node):
        self.definition(node, 'classe')
        self.scope.append((node.name, 'classe'))
        self.generic_visit(node)
        self.scope.pop()

    def visit_FunctionDef(self, node):
        kind = 'funzione_modulo' if not self.scope else ('metodo' if self.scope[-1][1] == 'classe' else 'funzione_annidata')
        row = self.definition(node, kind)
        for d in node.decorator_list:
            if not isinstance(d, ast.Call):
                continue
            target = dotted(d.func)
            verb = target.rsplit('.', 1)[-1]
            if verb not in {'route', 'get', 'post', 'put', 'patch', 'delete', 'head', 'options'}:
                continue
            path = string(d.args[0]) if d.args else None
            if path is None:
                continue
            methods = [verb.upper()] if verb != 'route' else ['GET']
            for kw in d.keywords:
                if kw.arg == 'methods':
                    try:
                        methods = ast.literal_eval(kw.value)
                    except (ValueError, TypeError, SyntaxError):
                        methods = ['DINAMICO']
            if not isinstance(methods, (list, tuple)) or not all(isinstance(v, str) for v in methods):
                methods = ['DINAMICO']
            self.routes.append(proof(self.file, d.lineno, percorso=path, metodi=sorted(set(v.upper() for v in methods)),
                                     funzione=row['qualificato'], decoratore=target))
        self.scope.append((node.name, 'funzione'))
        self.generic_visit(node)
        self.scope.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.refs.append(proof(self.file, node.lineno, nome=node.id, tipo='nome'))

    def visit_Attribute(self, node):
        if isinstance(node.ctx, ast.Load):
            self.refs.append(proof(self.file, node.lineno, nome=node.attr, tipo='attributo', espressione=dotted(node)))
        self.generic_visit(node)

    def visit_Import(self, node):
        for a in node.names:
            self.imports.append(proof(self.file, node.lineno, modulo=a.name, simbolo=None, alias=a.asname, livello=0))

    def visit_ImportFrom(self, node):
        for a in node.names:
            self.imports.append(proof(self.file, node.lineno, modulo=node.module or '', simbolo=a.name,
                                      alias=a.asname, livello=node.level))

    def add_url(self, value, line, origin):
        url = clean_url(value)
        self.urls.append(proof(self.file, line, url=url, ambito=url_scope(url), origine=origin,
                               disponibilita='non verificata'))

    def visit_Call(self, node):
        leaf = dotted(node.func).rsplit('.', 1)[-1]
        if leaf in {'execute', 'executemany', 'executescript'} and node.args:
            value = string(node.args[0])
            if value is not None:
                names = re.findall(r'\b(?:FROM|JOIN|INTO|UPDATE|TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?)\s+["`\[]?([A-Za-z_][A-Za-z_0-9]*)',
                                   value, re.I)
                names = sorted(set(n for n in names if n.upper() not in {'SET', 'SELECT', 'VALUES', 'IF', 'WHERE'}))
                self.sql.append(proof(self.file, node.lineno, tabelle_candidate=names, dinamica='{dinamico}' in value))
        if leaf in {'get', 'post', 'put', 'delete', 'patch', 'request', 'setUrl', 'urlopen'}:
            for arg in node.args[:2]:
                value = string(arg)
                if value and value.startswith(('http://', 'https://')):
                    self.add_url(value, node.lineno, 'argomento di chiamata ' + leaf)
        self.generic_visit(node)

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            for match in URL_RE.finditer(node.value):
                self.add_url(match.group(), node.lineno, 'stringa; non prova connessione')

    def visit_JoinedStr(self, node):
        value = string(node)
        if value and value.startswith(('http://', 'https://')):
            self.add_url(value, node.lineno, 'stringa parametrizzata')
        for n in node.values:
            if isinstance(n, ast.FormattedValue):
                self.visit(n.value)


def module_name(file):
    return file[:-3].replace('/', '.').removesuffix('.__init__')


def dependencies(modules):
    index = {module_name(f): f for f in modules}
    edges = []
    for file, m in modules.items():
        current = module_name(file)
        package = current if file.endswith('/__init__.py') else current.rpartition('.')[0]
        for imp in m['import']:
            name = imp['modulo']
            if imp['livello']:
                parts = package.split('.') if package else []
                keep = len(parts) - imp['livello'] + 1
                name = '.'.join((parts[:keep] if keep >= 0 else []) + ([name] if name else []))
            full = name + '.' + imp['simbolo'] if imp['simbolo'] else name
            target = index.get(full) or index.get(name)
            imp.update(destinazione=target, ambito='interno' if target else 'esterno_o_non_risolto')
            if target:
                edges.append(proof(file, imp['riga'], destinazione=target, importazione=full))
    return edges


def findings(modules):
    refs, bodies = defaultdict(list), defaultdict(list)
    issues = []
    for m in modules.values():
        for ref in m['riferimenti']:
            refs[ref['nome']].append(ref)
        for imp in m['import']:
            if imp['simbolo']:
                refs[imp['simbolo']].append(imp)
            if imp['modulo'].split('.')[0] in FORBIDDEN_UI:
                issues.append(dict(tipo='framework_ui_vietato', certezza='fatto', prova=imp))
        for symbol in m['simboli']:
            if symbol.get('corpo_sha256'):
                bodies[symbol['corpo_sha256']].append(symbol)
    for file, m in modules.items():
        if file.startswith('tests/'):
            continue
        for symbol in m['simboli']:
            if symbol['tipo'] not in {'classe', 'funzione_modulo'}:
                continue
            name = symbol['nome']
            if name.startswith('_') or name in {'main', 'run', 'app'} or symbol['decoratori']:
                continue
            if not refs.get(name):
                issues.append(dict(tipo='nessun_riferimento_statico', certezza='indizio', prova=symbol,
                                   limite='Non prova codice morto: possibili import dinamici, callback o uso esterno.'))
    duplicates = [dict(corpo_sha256=h, definizioni=items) for h, items in sorted(bodies.items())
                  if len({s['file'] for s in items}) > 1]
    return issues, duplicates


def git_snapshot(root):
    def git(*args, optional=False):
        r = subprocess.run(['git', '--no-optional-locks', *args], cwd=root, capture_output=True,
                           encoding='utf-8', errors='replace', timeout=20)
        if r.returncode and not optional:
            raise RuntimeError('git ' + args[0] + ': ' + r.stderr.strip())
        return r.stdout
    try:
        head = git('rev-parse', 'HEAD').strip()
        branch = git('symbolic-ref', '--short', '-q', 'HEAD', optional=True).strip() or 'HEAD scollegato'
        changes = []
        entries = iter(git('status', '--porcelain=v1', '-z', '--untracked-files=normal').split('\0'))
        for entry in entries:
            if entry:
                row = dict(stato=entry[:2], file=entry[3:])
                if 'R' in entry[:2] or 'C' in entry[:2]:
                    row['origine'] = next(entries, '')
                changes.append(row)
        commits = []
        for line in git('log', '-80', '--format=%H%x09%cI%x09%s').splitlines():
            commit, date, subject = line.split('\t', 2)
            commits.append(dict(commit=commit, data=date, titolo=subject))
        return dict(disponibile=True, head=head, ramo=branch, modifiche_locali=changes, commit_recenti=commits,
                    limite='Stato locale prima della scrittura dei report; nessun fetch o controllo remoto.')
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        return dict(disponibile=False, errore=str(exc))


def database_snapshot(root, enabled):
    result = dict(percorso='data/bikepacking_app.db', stato='non_verificato', tabelle=[])
    path = root / result['percorso']
    if not enabled or not path.is_file():
        result['motivo'] = 'Lettura disabilitata.' if not enabled else 'Database non presente.'
        return result
    wal = Path(str(path) + '-wal')
    if wal.exists() and wal.stat().st_size:
        result['motivo'] = 'WAL presente: chiudere l’app per leggere una fotografia coerente senza scritture.'
        return result
    connection = None
    try:
        before = (path.stat().st_size, path.stat().st_mtime_ns)
        connection = sqlite3.connect(path.resolve().as_uri() + '?mode=ro&immutable=1', uri=True)
        connection.execute('BEGIN')
        quote = lambda name: '"' + name.replace('"', '""') + '"'
        names = [r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        for name in names:
            q = quote(name)
            columns = [dict(nome=r[1], tipo=r[2], not_null_dichiarato=bool(r[3]), default=r[4], posizione_pk=r[5])
                       for r in connection.execute(f'PRAGMA table_info({q})')]
            indexes = [dict(nome=r[1], univoco=bool(r[2]), colonne=[c[2] for c in connection.execute(f'PRAGMA index_info({quote(r[1])})')])
                       for r in connection.execute(f'PRAGMA index_list({q})')]
            keys = [dict(colonna=r[3], tabella=r[2], colonna_destinazione=r[4], on_update=r[5], on_delete=r[6])
                    for r in connection.execute(f'PRAGMA foreign_key_list({q})')]
            result['tabelle'].append(dict(nome=name, righe=connection.execute(f'SELECT COUNT(*) FROM {q}').fetchone()[0],
                                          colonne=columns, indici=indexes, chiavi_esterne=keys))
        if before != (path.stat().st_size, path.stat().st_mtime_ns) or (wal.exists() and wal.stat().st_size):
            result.update(stato='non_verificato', motivo='Database cambiato durante la lettura.', tabelle=[])
        else:
            result.update(stato='letto_in_sola_lettura', user_version=connection.execute('PRAGMA user_version').fetchone()[0])
    except (sqlite3.Error, OSError) as exc:
        result.update(stato='errore', motivo=str(exc))
    finally:
        if connection is not None:
            connection.close()
    return result


def configuration(path, root, raw):
    row = dict(file=path.relative_to(root).as_posix(), byte=len(raw), sha256=sha(raw))
    if path.suffix.lower() != '.json':
        row['stato'] = 'inventariato_formato_non_validato'
        return row
    try:
        value = json.loads(raw.decode('utf-8-sig'))
        row['stato'] = 'JSON_valido'
        if isinstance(value, dict):
            row['struttura'] = dict(tipo='oggetto', numero_chiavi=len(value),
                                    chiavi_esempio=sorted(k for k in value if not SECRET_RE.search(k))[:12])
            row['collezioni'] = {k: len(v) for k, v in value.items() if isinstance(v, (dict, list)) and not SECRET_RE.search(k)}
        elif isinstance(value, list):
            row['struttura'] = dict(tipo='lista', elementi=len(value))
        else:
            row['struttura'] = dict(tipo=type(value).__name__)
    except (ValueError, UnicodeError) as exc:
        row.update(stato='errore', errore=str(exc))
    return row


def documents(root, errors=None):
    result = []
    paths = list(root.glob('*.md')) + list((root / 'REPORT').glob('*.md'))
    paths += [p for p in (root / '.github/copilot-instructions.md', root / '.clinerules') if p.is_file()]
    for path in sorted(paths):
        name = path.name
        if path.is_symlink() or name in GENERATED or name.startswith('.aider'):
            continue
        role = 'documento_progetto'
        if name in {'AGENTS.md', 'copilot-instructions.md', '.clinerules'}:
            role = 'istruzioni_settore_da_leggere_nello_strumento'
        elif name == 'STORIA_PROGETTO.md':
            role = 'memoria_storica_da_chat_e_fonti'
        elif name in {'FIRST_PRINCIPLES.md', 'REGOLE_GPX.md'}:
            role = 'principi_o_regole'
        elif name.startswith('VISIONE_'):
            role = 'visione'
        elif name.startswith(('PIANO_', 'PROGETTO_')):
            role = 'piano_non_prova_di_completamento'
        elif name.startswith('ANALISI_'):
            role = 'analisi_storica_da_confrontare_col_codice'
        elif 'aider_context' in name:
            role = 'contesto_generato_legacy'
        try:
            result.append(dict(file=path.relative_to(root).as_posix(), ruolo=role, sha256=sha(path.read_bytes()),
                               stato_implementazione='non_dedotto_dal_documento'))
        except OSError as exc:
            if errors is None:
                raise
            errors.append(proof(path.relative_to(root).as_posix(), None, tipo=type(exc).__name__, messaggio=str(exc)))
    return result


def scan(root, read_db=True):
    started = datetime.now(timezone.utc).isoformat()
    modules, configs, assets, errors, hashes = {}, [], [], [], {}
    paths = list(sources(root))
    for path in paths:
        file, suffix = path.relative_to(root).as_posix(), path.suffix.lower()
        if suffix not in ({'.py', '.html', '.htm', '.js', '.css'} | CONFIG_EXT) and path.name != 'requirements.txt':
            continue
        try:
            raw = path.read_bytes()
            hashes[file] = sha(raw)
            if suffix == '.py':
                source = raw.decode('utf-8-sig')
                v = Inspector(file)
                v.visit(ast.parse(source, filename=file))
                category = 'test' if file.startswith('tests/') else ('interfaccia' if file.startswith('gui/') else
                            ('servizio' if file.startswith('service/') else ('database' if file.startswith('database/') else 'strumento_o_avvio')))
                modules[file] = dict(sha256=hashes[file], righe=len(source.splitlines()), categoria=category,
                                     simboli=v.symbols, riferimenti=v.refs, rotte=v.routes, sql=v.sql, endpoint=v.urls)
                modules[file]['import'] = v.imports
            elif suffix in CONFIG_EXT or path.name == 'requirements.txt':
                c = configuration(path, root, raw)
                configs.append(c)
                if c['stato'] == 'errore':
                    errors.append(proof(file, None, tipo='ConfigurazioneJSON', messaggio=c['errore']))
            else:
                assets.append(dict(file=file, byte=len(raw), sha256=hashes[file], tipo=suffix[1:],
                                   verifica='inventariato; sintassi e comportamento non verificati'))
        except (OSError, UnicodeError, SyntaxError, ValueError, RecursionError) as exc:
            errors.append(proof(file, getattr(exc, 'lineno', None), tipo=type(exc).__name__, messaggio=str(exc)))
    edges = dependencies(modules)
    issues, duplicates = findings(modules)
    routes = [r for m in modules.values() for r in m['rotte']]
    endpoints = [e for m in modules.values() for e in m['endpoint']]
    counts = Counter(s['tipo'] for m in modules.values() for s in m['simboli'])
    git, db = git_snapshot(root), database_snapshot(root, read_db)
    docs = documents(root, errors)
    for d in docs:
        hashes[d['file']] = d['sha256']
    comparison = dict(disponibile=False, motivo='Prima scansione v4; baseline precedente incompatibile.')
    baseline = root / 'REPORT' / 'ULTIMO_RUN.json'
    if baseline.exists():
        try:
            old = json.loads(text(baseline))
            if old.get('schema_version') == SCHEMA:
                previous = old.get('file_sha256', {})
                reports = old.get('report_sha256', {})
                if not isinstance(previous, dict) or not isinstance(reports, dict) or any(f not in GENERATED for f in reports):
                    raise ValueError('Manifest non valido: impronte o nomi report inattesi.')
                mismatch = [f for f, h in reports.items()
                            if not (root / 'REPORT' / f).is_file() or sha((root / 'REPORT' / f).read_bytes()) != h]
                comparison = dict(disponibile=True, run_precedente=old.get('run_id'),
                                  aggiunti=sorted(hashes.keys() - previous.keys()), rimossi=sorted(previous.keys() - hashes.keys()),
                                  modificati=sorted(f for f in hashes.keys() & previous.keys() if hashes[f] != previous[f]),
                                  script_modificato=old.get('script_sha256') != sha(Path(__file__).read_bytes()),
                                  git_head_modificato=old.get('git_head') != git.get('head'),
                                  report_precedenti_modificati_o_mancanti=mismatch)
        except (OSError, ValueError, UnicodeError, AttributeError) as exc:
            comparison['motivo'] = 'Baseline illeggibile: ' + str(exc)
    run_id = sha((started + json.dumps(hashes, sort_keys=True)).encode())[:16]
    return dict(meta=dict(schema_version=SCHEMA, versione_script=VERSION, run_id=run_id, data_utc=started,
                          progetto=root.name, script_sha256=sha(Path(__file__).read_bytes()),
                          metodo='Analisi statica; nessun modulo applicativo importato o eseguito.'),
                sintesi=dict(moduli_python=len(modules), file_python_trovati=sum(p.suffix.lower() == '.py' for p in paths),
                             classi=counts['classe'], funzioni_modulo=counts['funzione_modulo'], metodi=counts['metodo'],
                             funzioni_annidate=counts['funzione_annidata'], funzioni_async=sum(s['asincrona'] for m in modules.values() for s in m['simboli']),
                             percorsi_http=len({r['percorso'] for r in routes}), operazioni_http=len({(r['percorso'], v) for r in routes for v in r['metodi']}),
                             tabelle_db_app=len(db['tabelle']) if db['stato'] == 'letto_in_sola_lettura' else None,
                             errori_scansione=len(errors), indizi_da_verificare=sum(i['certezza'] == 'indizio' for i in issues)),
                git=git, moduli=modules, dipendenze=edges, rotte=routes, endpoint=endpoints, database=db,
                configurazioni=configs, risorse_web=assets, documenti=docs, segnalazioni=issues, corpi_identici=duplicates,
                errori=errors, confronto=comparison, file_sha256=hashes,
                limiti=['Nessun test dell’app eseguito; comportamento runtime non certificato.',
                        'Servizi, server e contenuti R2 non contattati.',
                        'Riferimenti basati su nomi AST: alias, omonimie e uso dinamico limitano la precisione.',
                        'I riferimenti SQL non stabiliscono a quale database appartenga una tabella.',
                        'Decorator HTTP rilevati staticamente: registrazione e prefissi Blueprint non verificati.',
                        'HTML/JS/CSS inventariati, incluse librerie esterne; sintassi e comportamento non verificati.',
                        'Storia, visioni e piani sono fonti documentali, non prove di implementazione.',
                        'Cartelle escluse: ' + ', '.join(sorted(EXCLUDED))])


def header(data, title):
    m = data['meta']
    return [f'# {title}', '', f"Scansione `{m['run_id']}` · {m['data_utc']} · script {VERSION}", '',
            'Documento generato: fatti osservati e limiti dichiarati. Non certifica l’esecuzione dell’app.', '']


def table(lines, columns, rows):
    def cell(v):
        return str(v).replace('|', '\\|').replace('\n', ' ').replace('\r', ' ')
    lines.extend(['| ' + ' | '.join(columns) + ' |', '|' + '---|' * len(columns)])
    lines.extend('| ' + ' | '.join(cell(v) for v in row) + ' |' for row in rows)
    lines.append('')


def render(data):
    s, g, db = data['sintesi'], data['git'], data['database']
    brief = header(data, 'Fotografia del progetto — ' + data['meta']['progetto'])
    brief += ['## Contesto per una nuova chat', '',
              'Bikepacking Studio nasce per preparare e accompagnare viaggi reali in bicicletta, conservando la conoscenza raccolta prima, durante e dopo il viaggio.',
              'Il repository contiene l’app desktop Python/PySide6, una mappa web servita da Flask/MapLibre e SQLite. La direzione futura comprende un’app consumer desktop, web, iOS e Android; questa scansione non ne certifica la realizzazione.',
              'Principi: il viaggio è centrale; il GPX guida senza vincolare; la realtà prevale sul piano; l’IA assiste e il viaggiatore decide; le funzioni essenziali devono funzionare offline.', '',
              'Ruoli: Codex segue analisi, modifiche, verifiche e continuità del repository (`AGENTS.md`); Copilot segue il codice e l’integrazione dell’app (`.github/copilot-instructions.md`); Cline segue soprattutto la produzione di mappe, routing e dati su Hetzner e la distribuzione Cloudflare R2 (`.clinerules`). Gli accessi remoti configurati per Cline non sono verificati da questo report.', '',
              '**Uso con DeepSeek, Gemini, ChatGPT o altre chat:** allega questo file e indica l’obiettivo della sessione. Il brief fornisce il contesto iniziale; allega poi i sorgenti o i documenti necessari al compito. Una chat senza accesso ai file non può considerarli letti né verificare lo stato corrente.',
              'Puoi accompagnarlo con: «Parliamo in italiano semplice. Usa la fotografia e i suoi limiti, distingui fatti, storia e proposte; chiedimi le fonti mancanti prima di formulare diagnosi o modifiche. Obiettivo di questa sessione: …».', '',
              'Questo file si aggiorna eseguendo `python -B analisi_profonda.py`, non modificandolo a mano. La data e il commit sotto descrivono il momento della scansione. Prima di una nuova chat rigeneralo se il progetto è cambiato; se non puoi, dichiara che la fotografia può essere superata.', '']
    brief += ['## Come orientarsi', '', '- Questo brief: fotografia automatica corrente.',
              '- `STORIA_PROGETTO.md`: origini, motivazioni e storia dalle chat; non viene riscritta.',
              '- `REPORT/FIRST_PRINCIPLES.md` e `REPORT/REGOLE_GPX.md`: principi e regole.',
              '- `REPORT/report.md`: struttura, prove, errori e indizi.',
              '- `REPORT/PERCORSO.md`: cronologia Git locale senza interpretazioni di completamento.',
              '- `REPORT/DB_SCHEMA.md`, `CONFIG_FILES.md`, `EXTERNAL_SERVICES.md`: dettagli mirati.',
              '- `REPORT/analisi.json`: dataset completo. `ULTIMO_RUN.json`: manifest per il confronto.', '', '## Stato della lettura', '']
    if g['disponibile']:
        brief += [f"- Ramo: `{g['ramo']}`; commit: `{g['head'][:12]}`.",
                  f"- Modifiche locali prima dei report: {len(g['modifiche_locali'])}."]
    else:
        brief += ['- Git non verificato: ' + g['errore']]
    brief += [f"- Python: {s['moduli_python']} file analizzati su {s['file_python_trovati']}.",
              f"- Classi: {s['classi']}; funzioni di modulo: {s['funzioni_modulo']}; metodi: {s['metodi']}; funzioni annidate: {s['funzioni_annidate']}.",
              f"- HTTP: {s['percorsi_http']} indirizzi, {s['operazioni_http']} coppie indirizzo/metodo dichiarate.",
              f"- Database: {db['stato']}; tabelle applicative: {s['tabelle_db_app'] if s['tabelle_db_app'] is not None else 'non verificate'}.",
              f"- Errori di scansione: {len(data['errori'])}; indizi statici: {s['indizi_da_verificare']}.", '']
    if db.get('motivo'):
        brief += ['Database: ' + db['motivo'], '']
    brief += ['## Struttura osservata', '']
    table(brief, ['Area', 'Moduli Python'], sorted(Counter(m['categoria'] for m in data['moduli'].values()).items()))
    brief += ['## Componenti presenti nel codice', '', 'Questa mappa indica dove leggere il codice; la presenza dei file non certifica il completamento.', '']
    components = {
        'Avvio desktop e dashboard': ['app_desktop.py', 'gui/dashboard.py'],
        'Mappa e pianificatore': ['gui/mappa.py', 'gui/mappa_pianificatore.py', 'service/map_server.py'],
        'Progetti, tappe e GPX': ['service/progetti_service.py', 'service/tappe_service.py', 'service/salvataggio_tappa_service.py', 'service/gpx_metrics_service.py'],
        'Routing e superfici': ['service/dettagli_rotta_service.py', 'service/routing_timeout_service.py', 'service/superfici_service.py'],
        'Clima': ['service/clima_service.py', 'service/clima_estrattore.py', 'gui/pagine/controller_clima.py'],
        'Catena stagionale e precalcolo': ['service/catena_stagionale_service.py', 'service/precalcolo_service.py', 'service/precalcolo_batch_service.py'],
        'Mappe e geocodifica offline': ['service/map_manager_service.py', 'service/geocodifica_offline_service.py', 'service/geonames_service.py'],
        'Trasferimenti, dogane e statistiche': ['service/trasferimenti_service.py', 'service/dogane_service.py', 'service/stats_service.py'],
        'Persistenza e audit': ['database/database_setup.py', 'service/audit_service.py'],
    }
    table(brief, ['Componente', 'File osservati'], [(area, ', '.join(f'`{f}`' for f in files if f in data['moduli']))
          for area, files in components.items() if any(f in data['moduli'] for f in files)])
    brief += ['## Moduli più estesi', '', 'La dimensione orienta la lettura; non misura rischio o qualità.', '']
    table(brief, ['File', 'Righe', 'Definizioni'], [(f, m['righe'], len(m['simboli']))
          for f, m in sorted(data['moduli'].items(), key=lambda p: (-p[1]['righe'], p[0]))[:8]])
    brief += ['## Cambiamenti dalla precedente scansione', '']
    c = data['confronto']
    if c['disponibile']:
        brief += [f'- {k.capitalize()}: {len(c[k])}.' for k in ('aggiunti', 'rimossi', 'modificati')]
        brief += [f"- Analizzatore modificato: {'sì' if c['script_modificato'] else 'no'}."]
        brief += [f"- Commit Git cambiato: {'sì' if c['git_head_modificato'] else 'no'}; i cambiamenti alle fonti sono conteggiati separatamente."]
        if c['report_precedenti_modificati_o_mancanti']:
            brief += ['- Report precedenti modificati/mancanti: ' + ', '.join(c['report_precedenti_modificati_o_mancanti'])]
    else:
        brief += [c['motivo']]
    brief += ['', '## Limiti', ''] + ['- ' + v for v in data['limiti']]

    report = header(data, 'Analisi tecnica verificabile') + ['## Errori e copertura', '']
    if data['errori']:
        table(report, ['File', 'Riga', 'Errore'], [(e['file'], e['riga'], e['messaggio']) for e in data['errori']])
    else:
        report += ['Nessun errore di lettura o sintassi Python rilevato nelle fonti incluse.', '']
    report += ['## Moduli', '']
    table(report, ['File', 'Area', 'Righe', 'Classi', 'Funzioni', 'Metodi'],
          [(f, m['categoria'], m['righe'], sum(x['tipo'] == 'classe' for x in m['simboli']),
            sum(x['tipo'] == 'funzione_modulo' for x in m['simboli']), sum(x['tipo'] == 'metodo' for x in m['simboli']))
           for f, m in data['moduli'].items()])
    report += ['## Rotte HTTP dichiarate', '', 'Ogni decorator è conservato anche a parità di indirizzo.', '']
    table(report, ['Indirizzo', 'Metodi', 'Funzione', 'Prova'],
          [(r['percorso'], ', '.join(r['metodi']), r['funzione'], f"{r['file']}:{r['riga']}") for r in data['rotte']])
    report += ['## Segnalazioni', '', 'Gli indizi non autorizzano cancellazioni automatiche.', '']
    table(report, ['Tipo', 'Certezza', 'Simbolo o import', 'Prova'], [(i['tipo'], i['certezza'],
          i['prova'].get('qualificato', i['prova'].get('modulo', '')), f"{i['prova']['file']}:{i['prova']['riga']}") for i in data['segnalazioni']])
    report += ['## Corpi di funzione identici', '', 'Confronto AST senza docstring o posizioni; nomi uguali da soli non sono duplicazioni.', '']
    for group in data['corpi_identici']:
        report += ['- ' + '; '.join(f"{v['file']}:{v['riga']} `{v['qualificato']}`" for v in group['definizioni'])]
    report += ['', '## Dipendenze interne risolte', '']
    table(report, ['Importatore', 'Riga', 'Modulo importato'], [(e['file'], e['riga'], e['destinazione']) for e in data['dipendenze']])
    report += ['## Risorse web', '', 'Inventario di HTML, JavaScript e CSS; include librerie distribuite nel repository.', '']
    table(report, ['File', 'Tipo', 'Byte'], [(a['file'], a['tipo'], a['byte']) for a in data['risorse_web']])
    report += ['## Documenti di progetto', '', 'Inventario, non valutazione del completamento dei piani. ARCHIVIO escluso.', '']
    table(report, ['Documento', 'Ruolo'], [(d['file'], d['ruolo']) for d in data['documenti']])
    report += ['## Stato Git locale prima dei report', '']
    table(report, ['Stato', 'File'], [(x['stato'], x['file']) for x in g.get('modifiche_locali', [])])
    report += ['## Confronto', '', '```json', json.dumps(c, indent=2, ensure_ascii=False), '```', '', '## Limiti', ''] + ['- ' + v for v in data['limiti']]

    schema = header(data, 'Schema SQLite applicativo') + [f"Database: `{db['percorso']}`. Stato: {db['stato']}.", '']
    if db.get('motivo'):
        schema += [db['motivo'], '']
    for t in db['tabelle']:
        schema += [f"## `{t['nome']}`", '', f"Righe: {t['righe']}.", '']
        table(schema, ['Colonna', 'Tipo', 'NOT NULL dichiarato', 'Posizione PK', 'Default'],
              [(c['nome'], c['tipo'], c['not_null_dichiarato'], c['posizione_pk'], c['default']) for c in t['colonne']])
        table(schema, ['Indice', 'Univoco', 'Colonne'], [(i['nome'], i['univoco'], ', '.join(str(c) for c in i['colonne'])) for i in t['indici']])
        table(schema, ['FK', 'Destinazione', 'ON DELETE'], [(k['colonna'], f"{k['tabella']}.{k['colonna_destinazione']}", k['on_delete']) for k in t['chiavi_esterne']])
    schema += ['## Riferimenti SQL nel codice', '', 'Possono riguardare altri database; non sono il conteggio delle tabelle applicative.', '']
    table(schema, ['Prova', 'Tabelle candidate', 'SQL dinamico'],
          [(f"{r['file']}:{r['riga']}", ', '.join(r['tabelle_candidate']), r['dinamica']) for m in data['moduli'].values() for r in m['sql']])

    config = header(data, 'Configurazioni e dati strutturati') + ['Valori non copiati; JSON validato integralmente. Altri formati solo inventariati.', '']
    table(config, ['File', 'Byte', 'Stato', 'Struttura'], [(r['file'], r['byte'], r['stato'], json.dumps(r.get('struttura', {}), ensure_ascii=False)) for r in data['configurazioni']])
    for row in data['configurazioni']:
        if row.get('errore'):
            config += [f"- Errore in `{row['file']}`: {row['errore']}"]
    services = header(data, 'Endpoint osservati nel sorgente Python') + ['Nessun servizio contattato. Una URL non prova una connessione o un servizio disponibile.',
                'Credenziali URL, query e frammenti omessi. Parole come redis o Martin non sono prove di servizi.', '']
    table(services, ['Endpoint', 'Ambito', 'Origine', 'Prova'], [(e['url'], e['ambito'], e['origine'], f"{e['file']}:{e['riga']}") for e in data['endpoint']])
    state = header(data, 'Stato corrente osservato') + ['La storia e le decisioni restano in `STORIA_PROGETTO.md` e nei documenti di progetto.', '']
    state += brief[brief.index('## Stato della lettura'):]
    state += ['', '## Funzionalità e infrastruttura', '', 'Il completamento funzionale richiede prove di esecuzione. R2, server e download remoti non verificati.',
              'Questo strumento non sceglie automaticamente il prossimo lavoro del progetto.']
    history = header(data, 'Cronologia Git del ramo corrente') + ['Titoli dei commit riportati come dichiarazioni degli autori, non verifiche funzionali.',
                'Ultimi 80 commit raggiungibili da HEAD. La storia dalle chat è in `STORIA_PROGETTO.md`.', '']
    table(history, ['Data', 'Commit', 'Titolo'], [(r['data'], r['commit'][:12], r['titolo']) for r in g.get('commit_recenti', [])])
    if not g['disponibile']:
        history += ['Git non verificato: ' + g['errore']]
    summary = ['FOTOGRAFIA DEL PROGETTO', f"Run: {data['meta']['run_id']}", f"Data UTC: {data['meta']['data_utc']}",
               f"Python: {s['moduli_python']}/{s['file_python_trovati']} file analizzati", f"Errori: {len(data['errori'])}",
               'Servizi remoti e comportamento dell’app non verificati.', 'Punto di ingresso: REPORT/AI_BRIEF.md']
    return {f: '\n'.join(lines).rstrip() + '\n' for f, lines in {'AI_BRIEF.md': brief, 'report.md': report,
            'DB_SCHEMA.md': schema, 'CONFIG_FILES.md': config, 'EXTERNAL_SERVICES.md': services,
            'STATO_ATTUALE.md': state, 'PERCORSO.md': history, 'riepilogo.txt': summary}.items()}


def atomic_write(path, content):
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n', dir=path.parent,
                                         prefix='.analisi-', suffix='.tmp', delete=False) as stream:
            tmp = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if tmp and tmp.exists():
            tmp.unlink()


def write_reports(data, root):
    directory = root / 'REPORT'
    directory.mkdir(exist_ok=True)
    reports = render(data)
    reports['analisi.json'] = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    for file, content in reports.items():
        atomic_write(directory / file, content)
    manifest = dict(schema_version=SCHEMA, run_id=data['meta']['run_id'], data_utc=data['meta']['data_utc'],
                    git_head=data['git'].get('head'), file_sha256=data['file_sha256'], script_sha256=data['meta']['script_sha256'],
                    report_sha256={f: sha(t.encode()) for f, t in reports.items()})
    # Manifest per ultimo: una scrittura interrotta viene rilevata dalla prossima scansione.
    atomic_write(directory / 'ULTIMO_RUN.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return sorted(reports) + ['ULTIMO_RUN.json']


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT, help='Cartella da fotografare')
    parser.add_argument('--check', action='store_true', help='Analizza senza scrivere report')
    parser.add_argument('--no-db', action='store_true', help='Non apre il database')
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if not root.is_dir():
        parser.error('La cartella del progetto non esiste.')
    data = scan(root, read_db=not args.no_db)
    print(json.dumps(dict(meta=data['meta'], sintesi=data['sintesi'], database=data['database']['stato'], errori=data['errori'], confronto=data['confronto']),
                     indent=2, ensure_ascii=False))
    if not args.check:
        print('Report aggiornati: ' + ', '.join(write_reports(data, root)))
    return 1 if data['errori'] or data['database']['stato'] == 'errore' else 0


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    raise SystemExit(main())
