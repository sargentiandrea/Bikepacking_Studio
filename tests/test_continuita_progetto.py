"""Verifiche della continuità senza connessioni o dipendenze dell'app."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('continuity', PROJECT / 'continuita_progetto.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class ContinuityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for file in ('analisi_profonda.py', 'continuita_progetto.py', 'continuita.config.json'):
            shutil.copyfile(PROJECT / file, self.root / file)
        conf = json.loads((self.root / 'continuita.config.json').read_text())
        conf['infrastruttura'].update(ssh_target=None, radici_hetzner=[])
        (self.root / 'continuita.config.json').write_text(json.dumps(conf), encoding='utf-8')
        self.original = b'# Storia iniziale\r\n\r\nDecisioni precedenti.\r\n'
        (self.root / 'STORIA_PROGETTO.md').write_bytes(self.original)
        (self.root / 'main.py').write_text('print("sample")\n', encoding='utf-8')

    def test_journal_is_idempotent_and_detects_modified_events(self):
        rows = c.journal(self.root)
        self.assertTrue(c.append(self.root, rows, 'proposta', 'test', {'titolo': 'idea'}, key='same'))
        self.assertFalse(c.append(self.root, rows, 'proposta', 'test', {'titolo': 'idea'}, key='same'))
        self.assertEqual(len(c.journal(self.root)), 1)
        file = next((self.root / 'MEMORIA/eventi').glob('*.json'))
        data = json.loads(file.read_text())
        data['dati']['titolo'] = 'altered'
        file.write_text(json.dumps(data), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Integrità'):
            c.journal(self.root)

    def test_checkpoint_detects_tail_deletion(self):
        c.sync(self.root)
        files = sorted((self.root / 'MEMORIA/eventi').glob('*.json'))
        files[-1].unlink()
        with self.assertRaisesRegex(ValueError, 'rimossi'):
            c.journal(self.root)

    def test_automatic_history_preserves_original_bytes_and_is_repeatable(self):
        c.sync(self.root)
        first = (self.root / 'STORIA_PROGETTO.md').read_bytes()
        manifest = (self.root / 'REPORT/ULTIMO_RUN.json').read_bytes()
        self.assertTrue(first.startswith(self.original))
        c.sync(self.root)
        self.assertEqual((self.root / 'STORIA_PROGETTO.md').read_bytes(), first)
        self.assertEqual((self.root / 'REPORT/ULTIMO_RUN.json').read_bytes(), manifest)

    def test_original_history_change_is_not_overwritten(self):
        c.sync(self.root)
        path = self.root / 'STORIA_PROGETTO.md'
        changed = path.read_bytes().replace(b'Decisioni precedenti', b'Nuove parole')
        path.write_bytes(changed)
        with self.assertRaisesRegex(ValueError, 'Parte storica modificata'):
            c.sync(self.root)
        self.assertEqual(path.read_bytes(), changed)

    def test_source_change_and_report_corruption_trigger_refresh(self):
        c.sync(self.root)
        (self.root / 'main.py').write_text('print("changed")\n', encoding='utf-8')
        (self.root / 'REPORT/AI_BRIEF.md').write_text('wrong', encoding='utf-8')
        c.sync(self.root)
        rows = c.journal(self.root)
        changed = [r for r in rows if r['tipo'] == 'variazione_repository']
        self.assertIn('main.py', changed[-1]['dati']['cambiamenti']['modificati'])
        self.assertNotEqual((self.root / 'REPORT/AI_BRIEF.md').read_text(encoding='utf-8'), 'wrong')

    def test_unknown_remote_access_is_never_reported_as_empty_or_ready(self):
        with patch.object(c, 'run_json') as runner:
            result = c.probes(self.root, c.configuration(self.root))
        runner.assert_not_called()
        self.assertEqual({r['stato'] for r in result.values()}, {'non_verificato'})

    def test_readonly_remote_probes_have_bounded_scope(self):
        conf = c.configuration(self.root)
        conf.update(ssh_target='root@example', radici_hetzner=['/srv/maps'])
        outputs = [dict(elementi=[dict(radice='/srv/maps', percorso='it.pmtiles', byte=9)], troncato=False, radici_mancanti=[]),
                   [dict(Path='mappe/it/it.pmtiles', Size=9, IsDir=False, Hashes={}, ModTime='2026-10-09')]]
        with patch.object(c, 'run_json', side_effect=outputs) as runner:
            result = c.probes(self.root, conf)
        self.assertEqual(result['hetzner']['stato'], 'inventario_verificato')
        self.assertEqual(result['r2']['stato'], 'inventario_verificato')
        self.assertIn('lsjson', runner.call_args_list[1].args[0][-1])
        for call in runner.call_args_list:
            self.assertIn('StrictHostKeyChecking=yes', call.args[0])
            self.assertNotIn('shell', call.kwargs)
            self.assertLessEqual(call.args[1], 10)

    def test_missing_roots_are_partial_and_failures_do_not_expose_raw_output(self):
        conf = c.configuration(self.root)
        conf.update(ssh_target='root@example', radici_hetzner=['/missing'])
        with patch.object(c, 'run_json', side_effect=[dict(elementi=[], troncato=False, radici_mancanti=['/missing']),
                                                    RuntimeError('Comando fallito')]):
            result = c.probes(self.root, conf)
        self.assertEqual(result['hetzner']['stato'], 'inventario_parziale')
        self.assertEqual(result['r2']['stato'], 'errore_verifica')
        completed = subprocess.CompletedProcess(['rclone'], 1, stdout='', stderr='secret=DO_NOT_COPY')
        with patch.object(c.subprocess, 'run', return_value=completed):
            with self.assertRaises(RuntimeError) as error:
                c.run_json(['rclone'], 1)
        self.assertNotIn('DO_NOT_COPY', str(error.exception))

    def test_command_injection_in_configuration_is_rejected(self):
        data = json.loads((self.root / 'continuita.config.json').read_text())
        data['infrastruttura']['ssh_target'] = 'root@host; rm -rf /'
        (self.root / 'continuita.config.json').write_text(json.dumps(data), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'SSH non valida'):
            c.configuration(self.root)

    def test_decisions_need_an_observed_request_and_exact_quote(self):
        rows, state = [], {}
        c.hook_event(self.root, rows, 'codex', 'UserPromptSubmit',
                     dict(session_id='s', prompt='Manteniamo il formato PMTiles.', timestamp='1'), state)
        sha = rows[0]['dati']['prompt_sha256']
        decision = dict(tipo='decisione_utente', titolo='Formato mappa', riepilogo='Manteniamo PMTiles',
                        fonte=dict(tipo='utente', riferimento='richiesta:' + sha, citazione='Manteniamo il formato PMTiles.'))
        c.record(self.root, rows, 'codex', decision)
        self.assertIn('citazione_riscontrata', rows[-1]['dati']['certezza'])
        decision['fonte']['citazione'] = 'Passiamo a MBTiles.'
        with self.assertRaisesRegex(ValueError, 'Citazione assente'):
            c.record(self.root, rows, 'codex', decision)

    def test_tool_receipts_do_not_copy_commands_or_claim_remote_results(self):
        rows, state = [], {}
        c.hook_event(self.root, rows, 'cline', 'PostToolUse',
                     dict(taskId='t', timestamp='1', postToolUse=dict(toolName='execute_command',
                          parameters=dict(command='rclone copy secret=DO_NOT_COPY'), result='uploaded', success=True)), state)
        raw = json.dumps(rows)
        self.assertNotIn('DO_NOT_COPY', raw)
        self.assertNotIn('uploaded', raw)
        self.assertEqual(rows[-1]['dati']['verifica_risultato'], 'non_deducibile_dall_hook')

    def test_missing_closure_summary_is_visible(self):
        c.sync(self.root, 'codex', 'SessionStart', dict(session_id='s'))
        c.sync(self.root, 'codex', 'Stop', dict(session_id='s', timestamp='1'))
        index = json.loads((self.root / 'MEMORIA/indice.json').read_text())
        self.assertEqual(index['chiusure_senza_resoconto'], 1)
        self.assertEqual(index['hook_osservati']['codex']['evento'], 'Stop')

    def test_structured_closure_is_imported_once_and_proofs_are_fingerprinted(self):
        result = c.sync(self.root, 'cline', 'TaskStart', dict(taskId='t'))
        report = self.root / '.continuita/resoconti' / (result['sessione'] + '.json')
        report.parent.mkdir(parents=True)
        report.write_text(json.dumps([dict(tipo='risultato_dichiarato', titolo='Lavoro', riepilogo='Test eseguito',
            fonte=dict(tipo='attivita_agente', riferimento='task t'), prove=[dict(file='main.py')])]), encoding='utf-8')
        c.sync(self.root, 'cline', 'TaskComplete', dict(taskId='t', timestamp='1'))
        c.sync(self.root, 'cline', 'TaskComplete', dict(taskId='t', timestamp='1'))
        records = [r for r in c.journal(self.root) if r['tipo'] == 'risultato_dichiarato']
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['dati']['prove'][0]['sha256'], c.digest((self.root / 'main.py').read_bytes()))

    def test_paths_cannot_escape_the_workspace(self):
        with self.assertRaisesRegex(ValueError, 'fuori dal progetto'):
            c.inside(self.root, '../private')

    def test_common_secrets_are_redacted(self):
        output = c.safe_text('password=ABC\nAuthorization: Bearer XYZ\nhttps://user:pass@host/file?token=Q')
        for secret in ('ABC', 'XYZ', 'user:pass', 'token=Q'):
            self.assertNotIn(secret, output)

    def test_node_adapters_return_valid_protocol_for_three_providers(self):
        if not shutil.which('node'):
            self.skipTest('Node non disponibile')
        scripts = self.root / 'scripts'
        scripts.mkdir()
        shutil.copyfile(PROJECT / 'scripts/continuita-hook.cjs', scripts / 'continuita-hook.cjs')
        env = dict(os.environ, BIKEPACKING_PYTHON=sys.executable)
        for actor, event in [('codex', 'SessionStart'), ('copilot', 'sessionStart'), ('cline', 'TaskStart')]:
            with self.subTest(actor=actor):
                result = subprocess.run(['node', str(scripts / 'continuita-hook.cjs'), actor, event],
                    input=json.dumps(dict(session_id='node-test', taskId='node-test')), encoding='utf-8',
                    capture_output=True, env=env, timeout=15)
                self.assertEqual(result.returncode, 0, result.stderr)
                output = json.loads(result.stdout)
                if actor == 'codex':
                    self.assertIn('additionalContext', output['hookSpecificOutput'])
                elif actor == 'copilot':
                    self.assertIn('additionalContext', output)
                else:
                    self.assertFalse(output['cancel'])
                    self.assertIn('contextModification', output)

        result = subprocess.run(['node', str(scripts / 'continuita-hook.cjs'), 'copilot', 'sessionStart'],
            input=json.dumps(dict(hook_event_name='SessionStart', session_id='local-test')), encoding='utf-8',
            capture_output=True, env=env, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('additionalContext', json.loads(result.stdout)['hookSpecificOutput'])

    def test_old_summary_does_not_cover_a_new_prompt_and_can_be_corrected(self):
        result = c.sync(self.root, 'codex', 'SessionStart', dict(session_id='s'))
        path = self.root / '.continuita/resoconti' / (result['sessione'] + '.json')
        path.parent.mkdir(parents=True)
        path.write_text('[]', encoding='utf-8')
        c.sync(self.root, 'codex', 'Stop', dict(session_id='s', timestamp='1'))
        c.sync(self.root, 'codex', 'UserPromptSubmit', dict(session_id='s', prompt='Nuovo lavoro'))
        c.sync(self.root, 'codex', 'Stop', dict(session_id='s', timestamp='2'))
        index = json.loads((self.root / 'MEMORIA/indice.json').read_text())
        self.assertEqual(index['chiusure_senza_resoconto'], 1)
        path.write_text('[]', encoding='utf-8')
        c.sync(self.root, 'codex', 'Stop', dict(session_id='s', timestamp='3'))
        index = json.loads((self.root / 'MEMORIA/indice.json').read_text())
        self.assertEqual(index['chiusure_senza_resoconto'], 0)

    def test_cline_powershell_hook_executes_the_same_engine(self):
        if os.name != 'nt' or not shutil.which('node'):
            self.skipTest('Hook Windows')
        scripts = self.root / 'scripts'
        scripts.mkdir()
        shutil.copyfile(PROJECT / 'scripts/continuita-hook.cjs', scripts / 'continuita-hook.cjs')
        hooks = self.root / '.clinerules/hooks'
        hooks.mkdir(parents=True)
        source = PROJECT / '.clinerules/hooks/TaskStart.ps1'
        shutil.copyfile(source, hooks / source.name)
        result = subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
            '-File', str(hooks / source.name)], input=json.dumps(dict(taskId='powershell-test')),
            encoding='utf-8', capture_output=True, timeout=15,
            env=dict(os.environ, BIKEPACKING_PYTHON=sys.executable))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)['cancel'])


if __name__ == '__main__':
    unittest.main()
