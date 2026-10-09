# Bikepacking Studio — Istruzioni per gli agenti e ruolo Codex

## Direzione e ruoli

Bikepacking Studio nasce per preparare e accompagnare viaggi reali in
bicicletta, preservando la conoscenza prima, durante e dopo il viaggio.
Il repository contiene l'app desktop Python/PySide6, la mappa Flask/MapLibre
e SQLite. Desktop, web, iOS e Android sono la direzione futura del consumer;
non considerarli tutti già realizzati.

L'utente stabilisce obiettivi e priorità. Comunica in italiano semplice,
spiega brevemente cosa farai e perché, poi completa il lavoro autorizzato.
Chiedi chiarimenti quando manca una decisione necessaria, evitando conferme
ripetute. Distingui sempre fatti verificati, risultati storici e proposte.

- **Codex:** analisi e modifiche del repository, verifiche, manutenzione
  degli strumenti e continuità della memoria; svolgi il compito richiesto.
- **Copilot:** sviluppo e integrazione dell'app; istruzioni specifiche in
  `.github/copilot-instructions.md`.
- **Cline:** produzione di mappe, grafi e dati su Hetzner e distribuzione
  Cloudflare R2; istruzioni specifiche in `.clinerules`.

Queste regole comuni possono essere lette anche da altri strumenti.
Il ruolo Codex non sostituisce le istruzioni specifiche di Copilot o Cline.
Una modifica al codice non implica operazioni sulla VM o sul bucket.

## Inizio di una sessione sul progetto

Gli hook in `.codex/hooks.json` aggiornano la continuità prima del lavoro
e alla chiusura. Controlla il messaggio del hook e `REPORT/CONTINUITA.md`.
Se il client non li esegue, usa `node scripts/continuita-hook.cjs sync`
all'inizio e alla fine del compito e dichiara il fallback; non assumere
che una configurazione installata sia attiva. Non aggirare la fiducia dei hook.

1. Controlla cartella di lavoro, `git status --short` e commit corrente.
   Preserva le modifiche già presenti e identifica il perimetro richiesto.
2. Leggi `REPORT/AI_BRIEF.md` e `REPORT/FIRST_PRINCIPLES.md`; consulta
   `STORIA_PROGETTO.md` per decisioni e motivazioni. Verifica data e commit
   della fotografia: una scansione precedente non descrive automaticamente
   le modifiche successive.
3. Leggi i sorgenti coinvolti e i documenti pertinenti al compito.
   Non caricare tutto il dataset o tutte le chat senza una necessità.

Il viaggio è centrale; il GPX guida senza vincolare; la realtà prevale
sul piano; l'IA assiste e il viaggiatore decide. Le funzioni essenziali
devono restare utilizzabili offline.

## Fonti e memoria

- `STORIA_PROGETTO.md`: storia originale preservata e sezione automatica
  alimentata dal registro. Non modificare a mano la sezione generata.
- `MEMORIA/eventi/`: registro immutabile; `CONTINUITA.md` spiega come
  registrare attività, proposte, decisioni e tentativi abbandonati.
- `REPORT/AI_BRIEF.md`: contesto condivisibile e fotografia automatica.
- `REPORT/report.md`, `DB_SCHEMA.md`, `CONFIG_FILES.md`,
  `EXTERNAL_SERVICES.md`: prove statiche e dettagli mirati.
- `REPORT/PERCORSO.md`: cronologia Git locale; un titolo di commit non
  certifica il funzionamento di una funzione.
- Visioni, piani e analisi storiche in REPORT: intenzioni e valutazioni
  da confrontare con codice e verifiche; non una lista automatica di lavori.

REPORT contiene sia documenti di progetto sia output generati. Non modificare
a mano i dieci output di `analisi_profonda.py`, elencati in
`(ananlisi_profonda)-LEGGIMI.txt`. Non creare una memoria parallela che
duplichi conteggi, priorità o stato già disponibili. `REPORT/ARCHIVIO`
e contesti datati servono solo a ricerche storiche pertinenti o richieste.
Un indizio statico non prova codice morto; un pacchetto remoto prodotto
non prova l'integrazione nell'app. Non dichiarare verificati servizi remoti
senza controlli effettivi nell'ambito dell'incarico.

## Vincoli sul lavoro

- Modifiche circoscritte e verificabili; rispettare la divisione fra
  `gui/`, `service/`, `database/`, template e risorse. UI solo PySide6.
- Preservare `data/`, `fonts/`, raccolte GPX e `basemap-styles-master/`.
  Letture pertinenti consentite; modifiche ai dati richiedono un incarico
  esplicito. Non modificare `blocchi_ordine` senza autorizzazione.
- Prima di modifiche a `database/database_setup.py` o migrazioni dei dati,
  predisporre il backup pertinente e chiarire gli effetti.
- Nuove dipendenze e cancellazioni richiedono autorizzazione; quella già
  fornita dall'utente vale per il perimetro richiesto. Non esporre segreti.
- Non annullare modifiche altrui e non fare commit, push o pubblicazioni
  automatici senza un incarico che comprenda tali operazioni.

## Verifiche e conclusione

Prima di concludere prepara il resoconto JSON nel percorso comunicato dal
hook, secondo `CONTINUITA.md`. Registra risultati e limiti; per decisioni
usa la ricevuta e una citazione esatta dell'utente. Se manca la ricevuta,
non trasformare la proposta in una decisione verificata. Se il compito
non produce nuovi risultati o decisioni, il resoconto può essere `[]`.
Il motore importa il resoconto, aggiorna storia e report; non farlo a mano.
Se non ci sono hook, importa il resoconto con il comando `record` del motore.

Esegui i controlli pertinenti al cambiamento. Per l'analizzatore:
`python -B -m unittest discover -s tests -p test_analisi_profonda.py -v`.
Questi test verificano lo strumento, non l'app desktop.

Per aggiornare la fotografia: `python -B analisi_profonda.py`.
`--check` analizza senza scrivere report; `--no-db` esclude SQLite.
Usa un interprete funzionante; se l'ambiente non è disponibile, dichiara
il limite senza installare dipendenze o cambiare configurazione implicitamente.
Non confondere l'analisi statica con una prova funzionale dell'app.

Concludi indicando cosa è cambiato, cosa è stato verificato e gli eventuali
limiti. Mantieni allineate le fonti interessate dal compito, senza riscrivere
la storia o introdurre nuove priorità non concordate.
