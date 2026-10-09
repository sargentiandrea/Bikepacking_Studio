"""Regressioni del generatore: fonti finte e DB temporaneo, mai dati di viaggio."""
import ast
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('analisi_profonda', Path(__file__).resolve().parents[1] / 'analisi_profonda.py')
analysis = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(analysis)


def module(source, file='sample.py'):
    visitor = analysis.Inspector(file)
    visitor.visit(ast.parse(source))
    return {'simboli': visitor.symbols, 'import': visitor.imports, 'riferimenti': visitor.refs,
            'rotte': visitor.routes, 'sql': visitor.sql, 'endpoint': visitor.urls}


class InspectorTests(unittest.TestCase):
    def test_scoped_counts_include_async_and_nested_functions(self):
        result = module('''async def top():
    def nested():
        pass
class Outer:
    async def method(self):
        def inner():
            pass
    class Inner:
        def method(self):
            pass
''')
        symbols = result['simboli']
        self.assertEqual([s['tipo'] for s in symbols],
                         ['funzione_modulo', 'funzione_annidata', 'classe', 'metodo',
                          'funzione_annidata', 'classe', 'metodo'])
        self.assertEqual(sum(s['asincrona'] for s in symbols), 2)
        self.assertIn('Outer.Inner.method', [s['qualificato'] for s in symbols])

    def test_same_file_calls_and_framework_routes_are_not_dead_code(self):
        result = module('''class Used:
    pass
def helper():
    pass
@app.route('/map')
def callback():
    return 'ok'
helper()
Used()
''')
        issues, _ = analysis.findings({'sample.py': result})
        self.assertEqual(issues, [])

    def test_comments_do_not_hide_unused_symbols(self):
        result = module('def unused():\n    pass\n# unused()\n')
        issues, _ = analysis.findings({'sample.py': result})
        self.assertEqual(issues[0]['certezza'], 'indizio')
        self.assertEqual(issues[0]['prova']['nome'], 'unused')

    def test_test_entrypoints_are_not_reported_as_unused_app_code(self):
        result = module('class TestPlanner:\n    def test_routing(self): pass\n', 'tests/test_planner.py')
        self.assertEqual(analysis.findings({'tests/test_planner.py': result})[0], [])

    def test_http_methods_are_preserved_for_same_path(self):
        result = module("@app.route('/events', methods=['GET'])\ndef read(): pass\n"
                        "@app.route('/events', methods=['POST'])\ndef write(): pass\n"
                        "@app.post('/other')\nasync def other(): pass\n")
        self.assertEqual([(r['percorso'], r['metodi']) for r in result['rotte']],
                         [('/events', ['GET']), ('/events', ['POST']), ('/other', ['POST'])])

    def test_from_function_relative_alias_and_external_imports(self):
        modules = {'service/__init__.py': module('', 'service/__init__.py'),
                   'service/geo.py': module('def distance(): pass', 'service/geo.py'),
                   'service/map.py': module('from .geo import distance as d\nimport requests\n'
                                            'import helpers_external\n', 'service/map.py'),
                   'app.py': module('from service.geo import distance', 'app.py')}
        edges = analysis.dependencies(modules)
        self.assertEqual({(e['file'], e['destinazione']) for e in edges},
                         {('service/map.py', 'service/geo.py'), ('app.py', 'service/geo.py')})
        self.assertEqual(modules['service/map.py']['import'][1]['ambito'], 'esterno_o_non_risolto')
        self.assertEqual(modules['service/map.py']['import'][2]['ambito'], 'esterno_o_non_risolto')

    def test_same_name_different_code_is_not_duplicate(self):
        a = module('def calculate(x):\n    y = x + 1\n    return y * 2\n', 'a.py')
        b = module('def calculate(x):\n    y = x + 99\n    return y * 3\n', 'b.py')
        self.assertEqual(analysis.findings({'a.py': a, 'b.py': b})[1], [])
        c = module('def renamed(x):\n    y = x + 1\n    return y * 2\n', 'c.py')
        self.assertEqual(len(analysis.findings({'a.py': a, 'c.py': c})[1]), 1)

    def test_sql_only_from_executed_arguments_and_join(self):
        result = module('''description = 'SELECT * FROM fictional'
conn.execute('SELECT * FROM tappe JOIN progetti ON tappe.id_progetto=progetti.id')
conn.execute('INSERT INTO tappe VALUES (?) ON CONFLICT(id) DO UPDATE SET name=?')
conn.execute(f'SELECT * FROM {table_name}')
''')
        self.assertEqual(result['sql'][0]['tabelle_candidate'], ['progetti', 'tappe'])
        self.assertNotIn('SET', result['sql'][1]['tabelle_candidate'])
        self.assertTrue(result['sql'][2]['dinamica'])
        self.assertNotIn('fictional', str(result['sql']))

    def test_url_credentials_and_configuration_values_are_not_exported(self):
        clean = analysis.clean_url('https://user:private@example.org/maps?token=private#private')
        self.assertEqual(clean, 'https://example.org/maps')
        result = analysis.configuration(Path('config.json'), Path('.'),
                                        b'{"password":"private", "items":[1,2]}')
        self.assertNotIn('private', json.dumps(result))
        self.assertEqual(result['collezioni'], {'items': 2})


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'main.py').write_text('class Used: pass\nUsed()\n', encoding='utf-8')
        (self.root / 'STORIA_PROGETTO.md').write_text('Memoria storica da preservare.', encoding='utf-8')

    def scan(self, db=False):
        return analysis.scan(self.root, read_db=db)

    def test_syntax_errors_are_recorded_and_counted(self):
        (self.root / 'broken.py').write_text('def unfinished(', encoding='utf-8')
        data = self.scan()
        self.assertEqual(data['sintesi']['file_python_trovati'], 2)
        self.assertEqual(data['sintesi']['moduli_python'], 1)
        self.assertEqual(data['errori'][0]['file'], 'broken.py')
        self.assertEqual(data['errori'][0]['riga'], 1)

    def test_manifest_delta_and_interrupted_report_detection(self):
        first = self.scan()
        analysis.write_reports(first, self.root)
        before = (self.root / 'STORIA_PROGETTO.md').read_bytes()
        second = self.scan()
        self.assertTrue(second['confronto']['disponibile'])
        self.assertEqual(second['confronto']['modificati'], [])
        (self.root / 'main.py').write_text('print("changed")', encoding='utf-8')
        (self.root / 'REPORT' / 'AI_BRIEF.md').write_text('interrupted', encoding='utf-8')
        third = self.scan()
        self.assertEqual(third['confronto']['modificati'], ['main.py'])
        self.assertEqual(third['confronto']['report_precedenti_modificati_o_mancanti'], ['AI_BRIEF.md'])
        self.assertEqual((self.root / 'STORIA_PROGETTO.md').read_bytes(), before)
        manifest = json.loads((self.root / 'REPORT' / 'ULTIMO_RUN.json').read_text())
        for file, expected in manifest['report_sha256'].items():
            if file != 'AI_BRIEF.md':
                self.assertEqual(analysis.sha((self.root / 'REPORT' / file).read_bytes()), expected)

    def test_invalid_manifest_cannot_read_outside_generated_reports(self):
        analysis.write_reports(self.scan(), self.root)
        path = self.root / 'REPORT' / 'ULTIMO_RUN.json'
        manifest = json.loads(path.read_text())
        manifest['report_sha256'] = {'../STORIA_PROGETTO.md': 'unexpected'}
        path.write_text(json.dumps(manifest), encoding='utf-8')
        comparison = self.scan()['confronto']
        self.assertFalse(comparison['disponibile'])
        self.assertIn('Manifest non valido', comparison['motivo'])

    def test_instruction_changes_are_part_of_the_snapshot(self):
        (self.root / '.github').mkdir()
        copilot = self.root / '.github/copilot-instructions.md'
        copilot.write_text('app rules', encoding='utf-8')
        (self.root / '.clinerules').write_text('pipeline rules', encoding='utf-8')
        first = self.scan()
        self.assertIn('.clinerules', first['file_sha256'])
        self.assertIn('.github/copilot-instructions.md', first['file_sha256'])
        analysis.write_reports(first, self.root)
        copilot.write_text('updated app rules', encoding='utf-8')
        comparison = self.scan()['confronto']
        self.assertEqual(comparison['modificati'], ['.github/copilot-instructions.md'])

    def test_shared_brief_is_regenerated_with_new_chat_context(self):
        brief = analysis.render(self.scan())['AI_BRIEF.md']
        self.assertIn('Contesto per una nuova chat', brief)
        self.assertIn('DeepSeek, Gemini, ChatGPT', brief)
        self.assertIn('non modificandolo a mano', brief)
        self.assertIn('La scansione Python non verifica le connessioni remote', brief)

    def test_check_writes_nothing(self):
        before = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob('*'))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(analysis.main(['--root', str(self.root), '--check', '--no-db']), 0)
        self.assertEqual(sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob('*')), before)

    def test_database_is_read_without_sidecars_or_content_changes(self):
        (self.root / 'data').mkdir()
        db = self.root / 'data' / 'bikepacking_app.db'
        with sqlite3.connect(db) as conn:
            conn.execute('CREATE TABLE tappe(id INTEGER PRIMARY KEY, nome TEXT)')
            conn.execute("INSERT INTO tappe VALUES(1, 'test')")
        conn.close()
        before = db.read_bytes()
        result = analysis.database_snapshot(self.root, True)
        self.assertEqual(result['stato'], 'letto_in_sola_lettura')
        self.assertEqual(result['tabelle'][0]['righe'], 1)
        self.assertEqual(db.read_bytes(), before)
        self.assertFalse(Path(str(db) + '-shm').exists())
        self.assertFalse(Path(str(db) + '-wal').exists())

    def test_wal_is_not_silently_ignored(self):
        (self.root / 'data').mkdir()
        db = self.root / 'data' / 'bikepacking_app.db'
        db.write_bytes(b'not a database')
        Path(str(db) + '-wal').write_bytes(b'pending transactions')
        result = analysis.database_snapshot(self.root, True)
        self.assertEqual(result['stato'], 'non_verificato')
        self.assertIn('WAL', result['motivo'])

    def test_excluded_sources_and_archives_are_never_parsed(self):
        for directory in ['.venv', 'REPORT/ARCHIVIO', 'data', 'gpx']:
            path = self.root / directory
            path.mkdir(parents=True, exist_ok=True)
            (path / 'broken.py').write_text('invalid (', encoding='utf-8')
        data = self.scan()
        self.assertEqual(data['sintesi']['file_python_trovati'], 1)
        self.assertEqual(data['errori'], [])


if __name__ == '__main__':
    unittest.main()
