// Adattatore unico per Codex, Copilot e Cline. Nessun pacchetto npm.
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');
const args = process.argv.slice(2);
const providers = new Set(['codex', 'copilot', 'cline']);
const hook = providers.has(args[0]);
const actor = hook ? args[0] : 'manuale';
const event = hook ? args[1] : null;

function failure(message, emit = true) {
  const directory = path.join(root, '.continuita');
  if (!fs.existsSync(directory)) fs.mkdirSync(directory);
  if (fs.lstatSync(directory).isSymbolicLink()) throw new Error('Directory privata non valida');
  fs.appendFileSync(path.join(directory, 'errori.log'), new Date().toISOString() + ' ' + message + '\n');
  if (hook && emit) {
    const output = actor === 'cline'
      ? { cancel: false, contextModification: message, errorMessage: message }
      : { systemMessage: message, additionalContext: message };
    process.stdout.write(JSON.stringify(output));
  } else if (!hook) process.stderr.write(message + '\n');
  process.exitCode = 1;
}

try {
  if (hook && !/^[A-Za-z]+$/.test(event || '')) throw new Error('Evento non valido');
  let input = '';
  if (hook) {
    input = fs.readFileSync(0, 'utf8');
    if (Buffer.byteLength(input) > 8 * 1024 * 1024) throw new Error('Input hook troppo grande');
    const parsed = JSON.parse(input.trim() || '{}');
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) throw new Error('Input hook non valido');
    input = JSON.stringify(parsed);
  }
  const privateRoot = path.join(root, '.continuita');
  if (fs.existsSync(privateRoot) && fs.lstatSync(privateRoot).isSymbolicLink()) throw new Error('Directory privata non valida');
  const candidates = [];
  if (process.env.BIKEPACKING_PYTHON) candidates.push([process.env.BIKEPACKING_PYTHON, []]);
  if (process.platform === 'win32') {
    candidates.push([path.join(privateRoot, 'runtime', 'python.exe'), []]);
    candidates.push([path.join(root, '.venv', 'Scripts', 'python.exe'), []]);
    candidates.push(['py', ['-3']], ['python', []]);
  } else candidates.push(['python3', []], ['python', []]);
  const interpreter = candidates.find(([cmd, prefix]) => {
    const probe = spawnSync(cmd, [...prefix, '-B', '-c', 'import sys;sys.exit(0 if sys.version_info >= (3,10) else 1)'],
      { cwd: root, windowsHide: true, timeout: 2000, stdio: 'ignore' });
    return !probe.error && probe.status === 0;
  });
  if (!interpreter) throw new Error('Python 3.10+ non disponibile: configurare BIKEPACKING_PYTHON');
  const taskArgs = hook ? ['hook', '--actor', actor, '--event', event] : args;
  const result = spawnSync(interpreter[0], [...interpreter[1], '-B', path.join(root, 'continuita_progetto.py'), ...taskArgs],
    { cwd: root, input, encoding: 'utf8', windowsHide: true, timeout: 25000, maxBuffer: 2 * 1024 * 1024 });
  if (result.error) throw new Error('Motore continuità non eseguito o timeout');
  if (result.stdout) process.stdout.write(result.stdout);
  if (result.status !== 0) {
    // Lo stderr grezzo non viene salvato: può includere dati del chiamante.
    failure('Continuità non aggiornata; controllare configurazione, registro e interprete.', !result.stdout);
  }
} catch (error) {
  failure('Continuità non aggiornata: input o runtime non valido. Controllare CONTINUITA.md.');
}
