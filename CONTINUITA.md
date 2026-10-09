# Continuità automatica di Bikepacking Studio

Un motore comune (`continuita_progetto.py`) aggiorna fotografia locale,
registro delle attività, sezione automatica della storia e inventari remoti.
Non usa LLM, non modifica dati dell'app e non esegue commit, upload o cancellazioni.

## Cosa avviene automaticamente

Gli hook di Codex, Copilot e Cline richiamano `scripts/continuita-hook.cjs`:

1. A inizio attività o alla richiesta successiva verificano le fonti,
   le impronte dei report e le modifiche rispetto all'ultimo passaggio.
2. Registrano avvio, richieste (impronta), strumenti invocati e chiusura.
   Il successo di uno strumento non diventa una certificazione del risultato.
3. Eseguono gli inventari SSH/rclone configurati, al massimo ogni 30 minuti
   durante le attività. I risultati hanno data e validità; errori e assenza
   di accessi restano visibili. Il sistema non opera mentre nessun hook gira.
4. Importano il resoconto strutturato preparato dall'agente a fine lavoro.
5. Aggiornano la sezione automatica di `STORIA_PROGETTO.md`, preservando
   esattamente i byte della ricostruzione iniziale, e rigenerano i report
   dell'analizzatore quando necessario.

Se un agente dimentica il resoconto, la chiusura viene registrata come
incompleta sul piano della memoria. Le modifiche ai file vengono rilevate
comunque; motivazioni e decisioni non vengono inventate.

## Fonti e punto di ingresso

- `MEMORIA/eventi/*.json`: eventi immutabili con numero e impronte concatenate.
  La rimozione di eventi intermedi e le alterazioni vengono rilevate. Il
  checkpoint privato rileva anche rimozioni dalla coda su questa macchina.
  Questo protegge da errori; non è una firma crittografica contro chi riscrive
  insieme tutto il registro e i checkpoint. Git conserva ulteriori versioni.
- `MEMORIA/origine_storia.json`: impronta della ricostruzione storica originale.
- `MEMORIA/indice.json`: indice generato, verificato prima di usarlo nel brief.
- `REPORT/CONTINUITA.md`: salute del registro e hook effettivamente osservati.
- `REPORT/STATO_INFRASTRUTTURA.md`: ultimo controllo delle destinazioni configurate.
- `REPORT/REGISTRO_ATTIVITA.md`: vista leggibile degli eventi.
- `REPORT/AI_BRIEF.md`: ingresso comune per nuove sessioni e chat esterne.

Non modificare gli eventi già registrati o le sezioni generate. Per correggere
una dichiarazione registra un nuovo evento che la rettifica, citandone la fonte.

## Attivazione degli strumenti

Le configurazioni sono versionate; l'attivazione dipende anche dallo strumento:

- **Codex:** `.codex/hooks.json`. In una nuova sessione usa `/hooks` per
  controllare e autorizzare i hook del progetto quando Codex richiede fiducia.
  Non aggirare il controllo di fiducia. Se il client non espone `/hooks`,
  controlla il supporto ai hook del client e usa il comando comune come fallback.
- **Copilot:** `.github/hooks/continuita.json`, formato compatibile con CLI,
  cloud agent e parser Local di VS Code. In VS Code controlla Hooks e la fiducia
  nel workspace; per Local `chat.useHooks` deve essere attivo. Eventi e capacità
  dipendono dal client. L'automazione riguarda le sessioni agente, non le
  semplici completazioni inline.
- **Cline:** `.clinerules/01-progetto.md` e `.clinerules/hooks/*.ps1`.
  Cline 4.1.23 installato qui riconosce hook PowerShell su Windows. Abilita
  Enable Hooks nelle impostazioni Cline e controlla la scheda Hooks.
  La vecchia regola singola è stata trasferita nella cartella, senza duplicarla.

La presenza di un file non prova l'esecuzione. `REPORT/CONTINUITA.md` mostra
per ogni strumento l'ultimo evento realmente ricevuto. In questa installazione
i hook appena aggiunti non sono automaticamente una prova di attivazione UI.

## Python e comandi comuni

Il lanciatore usa Node già disponibile. Cerca `BIKEPACKING_PYTHON`, poi su
Windows il runtime isolato `.continuita/runtime/python.exe`, quindi gli
interpreti disponibili. In questa macchina è stato predisposto il runtime
Python portabile già usato per i test, senza modificare la `.venv` dell'app.
Runtime e stato macchina sono esclusi da Git. Su un'altra macchina servono
Node e Python 3.10+ funzionanti, oppure `BIKEPACKING_PYTHON`.

```text
node scripts/continuita-hook.cjs sync
node scripts/continuita-hook.cjs doctor
node scripts/continuita-hook.cjs sync --remote
```

`doctor` legge e verifica senza modificare il registro. `sync --remote` forza
gli inventari già configurati, sempre in sola lettura. Un errore viene segnalato
dal comando e dal hook; i fallimenti del lanciatore sono in `.continuita/errori.log`.

## Collegamento Hetzner e R2

`continuita.config.json` contiene solo destinazioni e limiti, mai credenziali.
Usa le connessioni SSH/rclone già configurate per Cline. Inserisci:

- `ssh_target`: alias SSH esistente oppure `utente@host` effettivo.
- `radici_hetzner`: directory assolute dove si trovano i risultati da inventariare.
- `rclone_remote`: alias e bucket effettivi; il valore iniziale è quello
  dichiarato nelle precedenti istruzioni, `r2:bikepacking-studio-maps`.
- `rclone_su_ssh`: true se rclone è configurato sulla VM, false se è locale.

`BIKEPACKING_SSH_TARGET` e `BIKEPACKING_R2_REMOTE` possono sostituire le
destinazioni senza modificare il file versionato. SSH usa BatchMode e verifica
la chiave host già conosciuta: non mostra richieste di password né accetta
automaticamente chiavi nuove. La VM deve avere Python 3 per l'inventario file.

Le destinazioni iniziali sono state recuperate dalle sessioni Cline locali:
`root@2.29.57.35`, `/work/maps`, `/work/graph`, `/work/geonames`, `/work/clima`.
Sono riferimenti storici, non prove di disponibilità attuale. L'autenticazione
non è stata copiata dalle chat. Se SSH non dispone di un accesso non interattivo
valido, il controllo fallisce esplicitamente, senza inventariare un server
vuoto. Cline deve confermare percorsi e autenticazione effettivi prima di
usarli come stato verificato; non indovinare directory o chiavi dei pacchetti.

Gli inventari sono limitati per profondità, quantità e tempo. I risultati
parziali sono dichiarati. Elencare un oggetto R2 non certifica integrità,
download pubblico o compatibilità con l'app. Le prove del consumer restano
verifiche specifiche, da documentare nel resoconto.

## Resoconto a cura dell'agente, senza manutenzione dell'utente

Il hook comunica all'agente il percorso `.continuita/resoconti/<sessione>.json`
e la ricevuta `richiesta:<sha256>`. Prima della chiusura l'agente scrive una
lista JSON, anche vuota se non ci sono nuove decisioni o risultati:

Il resoconto va scritto dopo la richiesta corrente. Un file rimasto da un
turno precedente non viene considerato una nuova chiusura valida.

```json
[
  {
    "tipo": "risultato_dichiarato",
    "titolo": "Titolo concreto del lavoro",
    "riepilogo": "Cosa è cambiato, verifiche svolte e limiti residui",
    "fonte": {"tipo": "attivita_agente", "riferimento": "sessione o compito"},
    "prove": [{"file": "percorso/di/un/file/pubblico"}]
  }
]
```

Tipi: `risultato_dichiarato`, `proposta`, `tentativo_abbandonato`,
`decisione_utente`. Quest'ultimo richiede `fonte.tipo = "utente"`, il riferimento
alla ricevuta della richiesta e `fonte.citazione` presente testualmente
nell'input del hook. La corrispondenza della citazione viene verificata;
la sua interpretazione rimane responsabilità dell'agente. Le prove locali
vengono associate alle impronte effettive dei file, non a nomi inventati.

Per importare subito un resoconto nel lavoro corrente, l'agente può eseguire:

```text
node scripts/continuita-hook.cjs record --actor codex --file .continuita/resoconti/esempio.json
```

I hook non leggono tutte le vecchie chat e non ricostruiscono automaticamente
decisioni mancanti. Non vengono salvati comandi né output grezzi degli strumenti.
Le richieste sono conservate localmente, con redazione dei segreti comuni,
solo per riscontrare le citazioni; non vengono pubblicate in Git. Non inserire
credenziali nei prompt o nei resoconti.

## Verifica del sistema

```text
python -B -m unittest discover -s tests -p test_continuita_progetto.py -v
python -B -m unittest discover -s tests -p test_analisi_profonda.py -v
```

I test coprono registri, fonti, isolamento e collegamenti simulati; la prova
degli accessi reali e dell'attivazione nei client resta distinta e visibile.

Fonti dei formati: [Codex](https://learn.chatgpt.com/docs/hooks),
[Copilot](https://docs.github.com/en/copilot/reference/hooks-reference),
[VS Code](https://code.visualstudio.com/docs/agent-customization/hooks).
Per Cline su Windows è stato controllato anche il codice dell'estensione
4.1.23 installata, perché la pagina storica dei hook non riflette tale supporto.
