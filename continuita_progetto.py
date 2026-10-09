"""Continuità verificabile: hook, registro immutabile, storia e fotografia.

Solo libreria standard. Nessun modello LLM, commit, upload o comando remoto
arbitrario. Le connessioni configurate eseguono esclusivamente inventari.
"""
import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
BEGIN = '<!-- CONTINUITA:INIZIO -->'
END = '<!-- CONTINUITA:FINE -->'
KINDS = {'decisione_utente', 'proposta', 'risultato_dichiarato', 'tentativo_abbandonato'}
SECRET = re.compile(r'(?i)(?:password|passwd|api[_-]?key|token|secret|authorization)\s*[:=]\s*[^\s,;]+')
START = {'SessionStart', 'sessionStart', 'TaskStart', 'TaskResume', 'UserPromptSubmit', 'userPromptSubmitted'}
STOP = {'Stop', 'agentStop', 'TaskComplete', 'TaskCancel'}


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def safe_text(value, limit=1200):
    value = re.sub(r'-----BEGIN [^-]*PRIVATE KEY-----.*?-----END [^-]*PRIVATE KEY-----', '[CHIAVE OMESSA]', str(value), flags=re.S)
    value = re.sub(r'(?im)authorization\s*[:=]\s*[^\r\n]+', '[AUTORIZZAZIONE OMESSA]', value)
    value = SECRET.sub('[SEGRETO OMESSO]', str(value))
    value = re.sub(r'https?://[^\s]+', lambda m: re.sub(r'[?#].*', '', m[0]), value)
    value = re.sub(r'(?i)https?://[^/\s]+@', 'https://[CREDENZIALI OMESSE]@', value)
    return value.replace('\x00', '')[:limit]


def inside(root, relative):
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Percorso fuori dal progetto o collegamento simbolico inatteso.')
    cursor = path
    while cursor != root and cursor != cursor.parent:
        if cursor.is_symlink():
            raise ValueError('Collegamento simbolico non consentito nei registri.')
        cursor = cursor.parent
    return path


def load(path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    if path.exists() and path.read_text(encoding='utf-8') == payload:
        return
    tmp = path.with_name(path.name + f'.{os.getpid()}.tmp')
    try:
        with tmp.open('w', encoding='utf-8', newline='\n') as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


@contextmanager
def locked(root):
    directory = inside(root, '.continuita')
    directory.mkdir(exist_ok=True)
    with (directory / 'lock').open('a+b') as f:
        f.seek(0, 2)
        if not f.tell():
            f.write(b'0')
            f.flush()
        acquired = False
        deadline = time.monotonic() + 10
        while not acquired:
            f.seek(0)
            try:
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
            except OSError:
                if time.monotonic() >= deadline:
                    raise TimeoutError('Aggiornamento già in corso; riprovare.')
                time.sleep(.05)
        try:
            yield
        finally:
            f.seek(0)
            if os.name == 'nt':
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(f, fcntl.LOCK_UN)


def journal(root):
    """Rifiuta buchi, sostituzioni e alterazioni: non ripara silenziosamente."""
    directory = inside(root, 'MEMORIA/eventi')
    result, previous = [], '0' * 64
    for path in sorted(directory.glob('*.json')):
        row = load(inside(root, path.relative_to(root)))
        if not isinstance(row, dict):
            raise ValueError('Evento non valido: ' + path.name)
        payload = {k: v for k, v in row.items() if k != 'sha256'}
        if row.get('numero') != len(result) + 1 or row.get('precedente_sha256') != previous or row.get('sha256') != digest(encoded(payload)):
            raise ValueError('Integrità del registro compromessa: ' + path.name)
        if path.name != f"{row['numero']:08d}-{row['sha256'][:16]}.json":
            raise ValueError('Nome evento incoerente: ' + path.name)
        result.append(row)
        previous = row['sha256']
    checkpoint = load(inside(root, '.continuita/checkpoint.json'), {})
    if checkpoint.get('numero', 0) > len(result):
        raise ValueError('Eventi rimossi rispetto al checkpoint locale.')
    index = checkpoint.get('numero', 0)
    if index and result[index - 1]['sha256'] != checkpoint.get('sha256'):
        raise ValueError('Registro differente dal checkpoint locale.')
    return result


def append(root, rows, kind, actor, payload, key=None):
    payload = json.loads(encoded(payload))
    key = key or digest(encoded([kind, actor, payload]))
    if any(row['chiave'] == key for row in rows):
        return False
    row = dict(schema_version=1, numero=len(rows) + 1, data_utc=now(), tipo=kind,
               autore=safe_text(actor, 80), dati=payload, chiave=key,
               precedente_sha256=rows[-1]['sha256'] if rows else '0' * 64)
    row['sha256'] = digest(encoded(row))
    path = inside(root, f"MEMORIA/eventi/{row['numero']:08d}-{row['sha256'][:16]}.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(row, f, ensure_ascii=False, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    rows.append(row)
    return True


def analyzer(root):
    spec = importlib.util.spec_from_file_location('bikepacking_analisi', root / 'analisi_profonda.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inputs(root, audit):
    hashes = {}
    for path in audit.sources(root):
        if path.suffix.lower() in ({'.py', '.html', '.htm', '.js', '.css', '.ps1', '.cjs'} | audit.CONFIG_EXT) or path.name == 'requirements.txt':
            hashes[path.relative_to(root).as_posix()] = digest(path.read_bytes())
    for doc in audit.documents(root):
        hashes[doc['file']] = doc['sha256']
    hashes['analisi_profonda.py'] = digest((root / 'analisi_profonda.py').read_bytes())
    db = root / 'data/bikepacking_app.db'
    if db.is_file():
        # L'impronta rileva cambiamenti; la coerenza SQLite è verificata dall'analizzatore.
        hashes['data/bikepacking_app.db'] = digest(db.read_bytes())
        for suffix in ('-wal', '-journal'):
            path = Path(str(db) + suffix)
            if path.exists():
                hashes['data/bikepacking_app.db' + suffix] = digest(path.read_bytes())
    return hashes


def delta(before, after):
    return dict(aggiunti=sorted(after.keys() - before.keys()), rimossi=sorted(before.keys() - after.keys()),
                modificati=sorted(f for f in before.keys() & after.keys() if before[f] != after[f]))


def configuration(root):
    data = load(inside(root, 'continuita.config.json'))
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        raise ValueError('Configurazione continuità assente o incompatibile.')
    c = dict(data['infrastruttura'])
    c['ssh_target'] = os.environ.get('BIKEPACKING_SSH_TARGET') or c.get('ssh_target')
    c['rclone_remote'] = os.environ.get('BIKEPACKING_R2_REMOTE') or c.get('rclone_remote')
    if c['ssh_target'] and not re.fullmatch(r'[A-Za-z0-9_.@][A-Za-z0-9_.@-]{0,200}', c['ssh_target']):
        raise ValueError('Destinazione SSH non valida.')
    if c['rclone_remote'] and not re.fullmatch(r'[A-Za-z0-9_.-]+:[A-Za-z0-9_./-]+', c['rclone_remote']):
        raise ValueError('Destinazione rclone non valida.')
    for key, lo, hi in [('timeout_secondi', 1, 10), ('max_elementi', 1, 10000),
                        ('profondita_r2', 1, 6), ('validita_verifica_ore', 1, 168),
                        ('intervallo_verifica_secondi', 30, 86400)]:
        if type(c.get(key)) is not int or not lo <= c[key] <= hi:
            raise ValueError('Valore configurazione non valido: ' + key)
    roots = c.get('radici_hetzner')
    if not isinstance(roots, list) or len(roots) > 8 or any(not isinstance(p, str) or not p.startswith('/') or '\x00' in p or '\n' in p for p in roots):
        raise ValueError('Radici Hetzner non valide.')
    return c


def run_json(argv, timeout):
    completed = subprocess.run(argv, capture_output=True, timeout=timeout, encoding='utf-8', errors='strict')
    if completed.returncode:
        # Non pubblicare stderr: può contenere configurazioni o segreti.
        raise RuntimeError(f'Comando di inventario fallito (codice {completed.returncode}).')
    if len(completed.stdout) > 3_000_000:
        raise ValueError('Inventario troppo grande: restringere le radici o la profondità.')
    return json.loads(completed.stdout)


REMOTE_FILES = '''import os,json,sys
roots=json.loads(sys.argv[1]); limit=int(sys.argv[2]); rows=[]; truncated=False; missing=[]
for root in roots:
 if not os.path.isdir(root): missing.append(root); continue
 for base,dirs,files in os.walk(root,followlinks=False):
  dirs[:]=sorted(d for d in dirs if not os.path.islink(os.path.join(base,d)))
  for name in sorted(files):
   path=os.path.join(base,name)
   if os.path.islink(path): continue
   if len(rows)>=limit: truncated=True; break
   st=os.stat(path); rows.append(dict(radice=root,percorso=os.path.relpath(path,root),byte=st.st_size,mtime=st.st_mtime))
  if truncated: break
 if truncated: break
print(json.dumps(dict(elementi=rows,troncato=truncated,radici_mancanti=missing)))
'''


def probes(root, c):
    result = {}
    ssh = ['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=3', c['ssh_target']] if c['ssh_target'] else None
    for sector in ('hetzner', 'r2'):
        row = dict(stato='non_verificato', data_utc=now(), elementi=[], limite='Inventario; non prova compatibilità con il consumer o disponibilità pubblica.')
        try:
            if sector == 'hetzner':
                if not ssh or not c['radici_hetzner']:
                    row['motivo'] = 'Configurare ssh_target e radici_hetzner con i percorsi effettivi usati da Cline.'
                    result[sector] = row
                    continue
                command = shlex.join(['python3', '-c', REMOTE_FILES, json.dumps(c['radici_hetzner']), str(c['max_elementi'])])
                data = run_json(ssh + [command], c['timeout_secondi'])
                if not isinstance(data, dict) or not isinstance(data.get('elementi'), list):
                    raise ValueError('Risposta inventario Hetzner non valida.')
                row.update(data)
                row['stato'] = 'inventario_parziale' if data.get('troncato') or data.get('radici_mancanti') else 'inventario_verificato'
            else:
                if not c['rclone_remote'] or (c.get('rclone_su_ssh') and not ssh):
                    row['motivo'] = 'Configurare la connessione SSH per rclone sulla VM, oppure un alias rclone locale.'
                    result[sector] = row
                    continue
                args = ['rclone', 'lsjson', c['rclone_remote'], '--recursive', '--max-depth', str(c['profondita_r2']), '--hash']
                command = ssh + [shlex.join(args)] if c.get('rclone_su_ssh') else args
                data = run_json(command, c['timeout_secondi'])
                if not isinstance(data, list):
                    raise ValueError('Risposta inventario R2 non valida.')
                row['elementi'] = [dict(percorso=safe_text(i['Path'], 500), byte=i['Size'],
                                       data_modifica=i.get('ModTime'), hash_disponibili=i.get('Hashes', {}))
                                   for i in data[:c['max_elementi']] if isinstance(i, dict) and not i.get('IsDir')]
                row['troncato'] = len(data) > c['max_elementi']
                row['profondita_massima'] = c['profondita_r2']
                row['stato'] = 'inventario_parziale' if row['troncato'] else 'inventario_verificato'
                row['limite'] += ' ETag e hash non disponibili non sono checksum verificati.'
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
            row.update(stato='errore_verifica', motivo=safe_text(str(exc), 250))
        result[sector] = row
    return result


def infrastructure(root, rows, c, force=False):
    path = inside(root, '.continuita/infrastruttura.json')
    old = load(path, {})
    signature = digest(encoded(c))
    elapsed = time.time() - old.get('controllo_epoch', 0)
    if force or old.get('config_sha256') != signature or elapsed >= c['intervallo_verifica_secondi']:
        result = probes(root, c)
        for sector, row in result.items():
            append(root, rows, 'verifica_infrastruttura', 'sonda', dict(settore=sector, **row),
                   key=digest(encoded(['sonda', sector, row])))
        old = dict(schema_version=1, config_sha256=signature, controllo_epoch=time.time(), settori=result)
        write(path, old)
    for row in old.get('settori', {}).values():
        row['superato'] = time.time() - old.get('controllo_epoch', 0) > c['validita_verifica_ore'] * 3600
    return old


def table(columns, rows):
    escape = lambda v: safe_text(v, 1500).replace('|', '\\|').replace('\n', ' ').replace('\r', '')
    return '\n'.join(['| ' + ' | '.join(columns) + ' |', '|' + '---|' * len(columns)] +
                     ['| ' + ' | '.join(escape(v) for v in row) + ' |' for row in rows]) + '\n'


def history(root, rows):
    path = inside(root, 'STORIA_PROGETTO.md')
    if not path.is_file():
        return
    raw = path.read_bytes()
    marker = BEGIN.encode()
    if raw.count(marker) > 1 or raw.count(END.encode()) > 1 or (marker in raw) != (END.encode() in raw):
        raise ValueError('Sezione automatica della storia non valida; nessuna riscrittura.')
    base = raw.split(marker)[0]
    if marker in raw and raw.split(END.encode(), 1)[1].strip():
        raise ValueError('Testo dopo la sezione automatica: preservarlo prima della rigenerazione.')
    origin = inside(root, 'MEMORIA/origine_storia.json')
    prior = load(origin)
    if prior and prior['base_sha256'] != digest(base):
        raise ValueError('Parte storica modificata: richiede riallineamento esplicito, nessuna riscrittura automatica.')
    if not prior:
        write(origin, dict(schema_version=1, base_sha256=digest(base), byte=len(base)))
    lines = [BEGIN, '', '## Continuità automatica dal registro delle attività', '',
             'Sezione generata da `MEMORIA/eventi/`; la ricostruzione precedente è preservata.',
             'Le dichiarazioni degli agenti non certificano risultati; le decisioni riportano la fonte indicata.', '']
    selected = [r for r in rows if r['tipo'] in KINDS or r['tipo'] == 'variazione_repository']
    for r in selected:
        d = r['dati']
        lines += [f"### {r['data_utc']} — {r['tipo']} — evento {r['numero']}", '',
                  safe_text(d.get('titolo', 'Variazione delle fonti locali rilevata')), '',
                  safe_text(d.get('riepilogo', json.dumps(d.get('cambiamenti', {}), ensure_ascii=False))), '',
                  'Fonte: `' + r['sha256'] + '` nel registro; autore: ' + r['autore'] + '.', '']
        if d.get('fonte'):
            lines += ['Fonte dichiarata: ' + safe_text(json.dumps(d['fonte'], ensure_ascii=False)), '']
    lines += [END, '']
    content = base + ('\n'.join(lines)).encode('utf-8')
    if content != raw:
        # Preserva esattamente i byte della ricostruzione iniziale (anche CRLF).
        tmp = path.with_suffix('.md.continuita.tmp')
        try:
            with tmp.open('wb') as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)
        finally:
            if tmp.exists():
                tmp.unlink()


def report_memory(root, rows, infra, state):
    header = '# Continuità del progetto\n\nDocumento generato da `continuita_progetto.py`.\n\n'
    sectors = infra.get('settori', {})
    overview = header + f"Registro: **{len(rows)} eventi**, catena di impronte verificata.\n\n"
    overview += table(['Settore', 'Stato', 'Ultimo controllo'],
                      [(name, row['stato'] + ('; superato' if row.get('superato') else ''), row['data_utc']) for name, row in sectors.items()])
    overview += '\n## Avvii degli strumenti osservati\n\n'
    overview += table(['Strumento', 'Ultimo hook ricevuto', 'Evento'], [(a, d['data_utc'], d['evento']) for a, d in sorted(state.get('hook', {}).items())])
    overview += '\nUna configurazione presente non prova che gli hook siano abilitati. Se uno strumento non compare, il suo avvio automatico non è stato osservato.\n'
    latest_closures = {r['dati']['sessione']: r for r in rows if r['tipo'] == 'sessione_conclusa'}
    pending = [r for r in latest_closures.values() if not r['dati'].get('resoconto_strutturato')]
    overview += f'\nChiusure senza resoconto strutturato: **{len(pending)}**. La variazione dei file viene comunque registrata; le motivazioni restano non documentate.\n'
    write(inside(root, 'REPORT/CONTINUITA.md'), overview)
    lines = ['# Stato infrastruttura', '', 'Inventari in sola lettura. Non attestano upload storici, download pubblico o integrazione nel consumer.', '']
    for name, row in sectors.items():
        lines += [f'## {name}', '', f"Stato: **{row['stato']}**. Controllo: {row['data_utc']}.", '',
                  safe_text(row.get('motivo', row.get('limite', ''))), '']
        items = row.get('elementi', [])
        lines += [f'Elementi osservati: **{len(items)}**. Elenco completo negli eventi di verifica in `MEMORIA/eventi/`.', '']
        if name == 'hetzner':
            lines += [table(['Radice', 'File'], sorted(Counter(i['radice'] for i in items).items()))]
        lines += ['### Fino a 20 elementi più grandi', '',
                  table(['Percorso', 'Byte'], [(i.get('radice', '') + '/' + i['percorso'], i['byte'])
                         for i in sorted(items, key=lambda i: (-i['byte'], i['percorso']))[:20]])]
    write(inside(root, 'REPORT/STATO_INFRASTRUTTURA.md'), '\n'.join(lines))
    log = '# Registro delle attività\n\nVista generata dal registro immutabile `MEMORIA/eventi/`. Nessuna ricostruzione automatica delle intenzioni.\n\n'
    log += table(['Evento', 'Data UTC', 'Autore', 'Tipo', 'Riepilogo'],
                 [(r['numero'], r['data_utc'], r['autore'], r['tipo'], r['dati'].get('titolo', r['dati'].get('settore', r['dati'].get('evento', '')))) for r in rows])
    write(inside(root, 'REPORT/REGISTRO_ATTIVITA.md'), log)
    summary = dict(schema_version=1, registro_eventi=len(rows), ultimo_evento_sha256=rows[-1]['sha256'] if rows else None,
                   integrita='verificata', infrastruttura={n: {k: r[k] for k in ('stato', 'data_utc', 'superato') if k in r} for n, r in sectors.items()},
                   chiusure_senza_resoconto=len(pending), hook_osservati=state.get('hook', {}))
    write(inside(root, 'MEMORIA/indice.json'), summary)


def record(root, rows, actor, data):
    if not isinstance(data, dict) or data.get('tipo') not in KINDS:
        raise ValueError('Tipo resoconto non valido.')
    if not all(isinstance(data.get(k), str) and data[k].strip() for k in ('titolo', 'riepilogo')):
        raise ValueError('Titolo e riepilogo obbligatori.')
    source = data.get('fonte')
    if not isinstance(source, dict) or not source.get('riferimento'):
        raise ValueError('Fonte obbligatoria; non dedurre decisioni dal codice.')
    if data['tipo'] == 'decisione_utente' and (source.get('tipo') != 'utente' or not source.get('citazione')):
        raise ValueError('Una decisione richiede una citazione esplicita dell’utente.')
    payload = {k: safe_text(data[k]) for k in ('titolo', 'riepilogo')}
    payload['fonte'] = {k: safe_text(v, 500) for k, v in source.items() if k in {'tipo', 'riferimento', 'citazione'}}
    payload['certezza'] = 'fonte_utente_dichiarata' if data['tipo'] == 'decisione_utente' else 'dichiarazione_agente'
    if data['tipo'] == 'decisione_utente':
        reference = source['riferimento']
        if not re.fullmatch(r'richiesta:[0-9a-f]{64}', reference):
            raise ValueError('Decisione priva di ricevuta della richiesta utente; registrarla come proposta.')
        prompt_hash = reference.split(':', 1)[1]
        receipt = load(inside(root, f'.continuita/richieste/{prompt_hash}.json'))
        if not receipt or not any(r['tipo'] == 'richiesta_ricevuta' and r['dati']['prompt_sha256'] == prompt_hash for r in rows):
            raise ValueError('Richiesta utente non osservata dagli hook.')
        if source['citazione'] not in receipt['testo_redatto'] or safe_text(source['citazione'], 500) != source['citazione']:
            raise ValueError('Citazione assente dalla richiesta o contenente dati da omettere.')
        payload['certezza'] = 'citazione_riscontrata_nell_input_hook; interpretazione_agente'
    if 'prove' in data:
        if not isinstance(data['prove'], list) or len(data['prove']) > 30:
            raise ValueError('Elenco prove non valido.')
        payload['prove'] = []
        for evidence in data['prove']:
            if not isinstance(evidence, dict) or not isinstance(evidence.get('file'), str):
                raise ValueError('Prova non valida.')
            path = inside(root, evidence['file'])
            if not path.is_file() or path.is_relative_to(root / '.continuita'):
                raise ValueError('La prova deve essere un file pubblico del progetto.')
            actual = digest(path.read_bytes())
            if evidence.get('sha256') and evidence['sha256'] != actual:
                raise ValueError('Impronta della prova diversa dal file.')
            payload['prove'].append(dict(file=path.relative_to(root).as_posix(), sha256=actual))
    append(root, rows, data['tipo'], actor, payload)


def hook_event(root, rows, actor, event, payload, state):
    session = safe_text(payload.get('session_id') or payload.get('sessionId') or payload.get('taskId') or 'non_identificata', 120)
    sid = digest(encoded([actor, session]))[:24]
    state.setdefault('hook', {})[actor] = dict(data_utc=now(), evento=event)
    prompt = payload.get('prompt') or payload.get('userPromptSubmit', {}).get('prompt') or payload.get('taskStart', {}).get('taskMetadata', {}).get('initialTask')
    if prompt:
        prompt_hash = digest(str(prompt).encode())
        write(inside(root, f'.continuita/richieste/{prompt_hash}.json'),
              dict(sha256_originale=prompt_hash, testo_redatto=safe_text(prompt, 64000)))
        append(root, rows, 'richiesta_ricevuta', actor, dict(sessione=sid, prompt_sha256=digest(str(prompt).encode()), evento=event),
               key=digest(encoded([actor, sid, 'prompt', prompt])))
    if event in START:
        state.setdefault('sessioni', {}).setdefault(sid, {})['resoconto_min_mtime_ns'] = time.time_ns()
        append(root, rows, 'sessione_avviata', actor, dict(sessione=sid, evento=event), key=f'avvio:{sid}')
    if event in {'PostToolUse', 'postToolUse'}:
        info = payload.get('postToolUse') or payload
        name = safe_text(info.get('toolName') or info.get('tool_name') or payload.get('tool_call', {}).get('name', 'non_identificato'), 120)
        args = info.get('parameters') or info.get('toolArgs') or info.get('tool_input') or payload.get('tool_call', {}).get('input') or {}
        success = info.get('success') if isinstance(info.get('success'), bool) else None
        # Nessun comando o risultato grezzo viene conservato.
        append(root, rows, 'tool_osservato', actor, dict(sessione=sid, strumento=name, successo_tool=success,
               argomenti_sha256=digest(encoded(args)), verifica_risultato='non_deducibile_dall_hook'),
               key=digest(encoded([actor, sid, event, payload.get('timestamp'), name, args])))
    if event in STOP:
        report = inside(root, f'.continuita/resoconti/{sid}.json')
        minimum = state.get('sessioni', {}).get(sid, {}).get('resoconto_min_mtime_ns', 0)
        structured = report.exists() and report.stat().st_mtime_ns >= minimum
        if structured:
            data = load(report)
            if not isinstance(data, list) or len(data) > 30:
                raise ValueError('Resoconto di chiusura non valido.')
            for item in data:
                record(root, rows, actor, item)
        append(root, rows, 'sessione_conclusa', actor, dict(sessione=sid, evento=event, resoconto_strutturato=structured),
               key=digest(encoded(['chiusura', sid, event, payload.get('timestamp'), structured])))
    return sid


def sync(root, actor='manuale', event=None, payload=None, force_remote=False, records=None):
    with locked(root):
        rows = journal(root)
        state_path = inside(root, '.continuita/state.json')
        state = load(state_path, {})
        sid = hook_event(root, rows, actor, event, payload or {}, state) if event else None
        for data in records or []:
            record(root, rows, actor, data)
        audit = analyzer(root)
        current = inputs(root, audit)
        old = state.get('file_sha256')
        changes = delta(old or {}, current)
        if old is not None and any(changes.values()):
            append(root, rows, 'variazione_repository', 'scansione', dict(cambiamenti=changes,
                   titolo='Fonti locali cambiate', limite='Le impronte non spiegano intenzioni o correttezza funzionale.'),
                   key=digest(encoded(['fonti', current])))
        elif old is None:
            append(root, rows, 'continuita_inizializzata', actor, dict(titolo='Prima fotografia della continuità', file_osservati=len(current)))
        infra = infrastructure(root, rows, configuration(root),
                               force=force_remote or (actor == 'cline' and event == 'TaskComplete'))
        history(root, rows)
        report_memory(root, rows, infra, state)
        scan = audit.scan(root)
        comparison = scan['confronto']
        needs = (not comparison['disponibile'] or any(comparison.get(k) for k in ('aggiunti', 'rimossi', 'modificati', 'script_modificato', 'git_head_modificato', 'report_precedenti_modificati_o_mancanti')))
        # Confronta anche il DB, i registri e i report di continuità, fuori dalla vecchia baseline.
        signature = digest(encoded([inputs(root, audit), digest(encoded(rows)), digest(encoded(infra)), scan['git'].get('head')]))
        if needs or state.get('fotografia_firma') != signature:
            audit.write_reports(scan, root)
        state.update(file_sha256=inputs(root, audit), fotografia_firma=signature, ultima_sincronizzazione=now(),
                     errori_scansione=scan['errori'], database=scan['database']['stato'])
        write(state_path, state)
        if rows:
            write(inside(root, '.continuita/checkpoint.json'), dict(numero=rows[-1]['numero'], sha256=rows[-1]['sha256']))
        message = f"Continuità aggiornata: {len(rows)} eventi, {len(scan['errori'])} errori di scansione."
        message += ' Infrastruttura: ' + ', '.join(n + '=' + r['stato'] for n, r in infra['settori'].items()) + '.'
        if sid:
            message += f' Per registrare decisioni e risultati, scrivi il resoconto strutturato in `.continuita/resoconti/{sid}.json` prima della chiusura. Schema in `CONTINUITA.md`.'
            requests = [r for r in rows if r['tipo'] == 'richiesta_ricevuta' and r['dati']['sessione'] == sid]
            if requests:
                message += ' Fonte della richiesta utente: `richiesta:' + requests[-1]['dati']['prompt_sha256'] + '`.'
        return dict(messaggio=message, sessione=sid, errori=scan['errori'], database=scan['database']['stato'])


def response(actor, event, message, error=False):
    if actor == 'cline':
        return dict(cancel=False, contextModification=message, errorMessage=message if error else '')
    if actor == 'copilot' and event and event[0].islower():
        return dict(additionalContext=message)
    if event in {'SessionStart', 'UserPromptSubmit', 'PostToolUse', 'PreCompact'}:
        return dict(hookSpecificOutput=dict(hookEventName=event, additionalContext=message))
    return dict(systemMessage=message)


def doctor(root):
    rows = journal(root)
    state = load(inside(root, '.continuita/state.json'), {})
    c = configuration(root)
    return dict(registro_eventi=len(rows), integrita='verificata', python=sys.executable,
                ssh_disponibile=bool(shutil.which('ssh')), ssh_configurato=bool(c['ssh_target']),
                rclone_locale_disponibile=bool(shutil.which('rclone')), rclone_su_ssh=c.get('rclone_su_ssh'),
                radici_hetzner_configurate=bool(c['radici_hetzner']), hook_osservati=state.get('hook', {}),
                limite='Hook installati e hook realmente abilitati sono aspetti distinti.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('azione', choices=['sync', 'hook', 'record', 'doctor'])
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--actor', default='manuale', choices=['manuale', 'codex', 'copilot', 'cline'])
    parser.add_argument('--event')
    parser.add_argument('--file', type=Path)
    parser.add_argument('--remote', action='store_true', help='Forza inventari in sola lettura')
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.azione == 'doctor':
            result = doctor(root)
        else:
            payload = json.loads(sys.stdin.read() or '{}') if args.azione == 'hook' else {}
            if not isinstance(payload, dict):
                raise ValueError('Input hook non valido.')
            if args.azione == 'hook':
                # Copilot Local mappa gli eventi camelCase ai payload PascalCase.
                actual_event = payload.get('hook_event_name')
                if actual_event in START | STOP | {'PostToolUse', 'PreCompact'}:
                    args.event = actual_event
            records = None
            if args.azione == 'record':
                if args.file is None:
                    parser.error('record richiede --file')
                record_path = inside(root, args.file if not args.file.is_absolute() else args.file.relative_to(root))
                data = load(record_path)
                records = data if isinstance(data, list) else [data]
            result = sync(root, args.actor, args.event if args.azione == 'hook' else None, payload, args.remote, records)
            if args.azione == 'hook':
                result = response(args.actor, args.event, result['messaggio'])
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if args.azione != 'hook' and isinstance(result, dict) and result.get('errori') else 0
    except (OSError, ValueError, KeyError, TypeError, TimeoutError) as exc:
        message = 'Continuità NON aggiornata: ' + safe_text(str(exc), 400)
        if args.azione == 'hook':
            print(json.dumps(response(args.actor, args.event, message, True), ensure_ascii=False))
        else:
            print(message, file=sys.stderr)
        return 1


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    raise SystemExit(main())
