# GitHub Copilot — Bikepacking Studio

## Ruolo e direzione

Lavora sul codice dell'app e sulla sua integrazione con i dati. Bikepacking
Studio nasce per preparare e accompagnare viaggi reali in bicicletta;
la direzione futura è un ecosistema consumer desktop, web, iOS e Android.
L'app presente nel repository è desktop Python/PySide6 con mappa Flask,
MapLibre e persistenza SQLite. Non presentare la visione futura come già realizzata.

L'utente guida il progetto e comunica obiettivi funzionali. Parla in italiano
semplice. Prima di intervenire spiega brevemente obiettivo e file coinvolti;
poi procedi nel perimetro richiesto, senza conferme ripetute per lavoro già
autorizzato. Chiedi chiarimenti solo quando manca una decisione necessaria.

Cline ha un ruolo distinto: produzione di mappe, grafi e dati geografici su
Hetzner e distribuzione Cloudflare R2. La sua preparazione di un pacchetto
non dimostra che l'app lo supporti. Non avviare operazioni infrastrutturali
come conseguenza implicita di una modifica al codice.

## Orientamento a inizio attività

Gli hook di `.github/hooks/continuita.json` richiamano il motore comune
di continuità. Controlla il suo messaggio e `REPORT/CONTINUITA.md`; se il
client non li esegue, usa `node scripts/continuita-hook.cjs sync` prima
e dopo il compito, dichiarando il fallback. Vedi `CONTINUITA.md` per
attivazione e limiti: un file di hook presente non prova che sia abilitato.

1. Leggi `REPORT/AI_BRIEF.md`: fotografia generata da `analisi_profonda.py`,
   con data, commit e limiti. Non modificarla manualmente.
2. Controlla `git status --short` e il commit corrente. Se il brief precede
   modifiche rilevanti, verifica i sorgenti coinvolti; non considerarlo attuale
   solo perché è il report più recente disponibile.
3. Leggi `REPORT/FIRST_PRINCIPLES.md`. Consulta `STORIA_PROGETTO.md` per
   motivazioni, decisioni e storia, soprattutto quando inizi un nuovo filone.
4. Leggi codice e documenti specifici del compito prima di cambiarli.

Codice, Git e prove di esecuzione descrivono aspetti diversi. Un titolo di
commit, una chat o un piano non certificano il funzionamento di una funzione.
Gli indizi dell'analizzatore non provano codice inutilizzato. Evita di
ricopiare nelle istruzioni conteggi, liste di bug o priorità destinati a scadere.

## Mappa del codice

- `app_desktop.py`: avvio e coordinamento desktop.
- `gui/`: dashboard, mappa, pianificatore, pagine e worker PySide6.
- `service/`: dominio, GPX, routing, clima, catena stagionale, precalcolo,
  statistiche, server mappa e gestione dati offline.
- `database/database_setup.py`: schema e inizializzazione SQLite.
- `templates/`, `static/`, `resources/`: mappa web, stile, icone e risorse.
- `tests/`: verifiche disponibili; scegli quelle pertinenti al cambiamento.

Rispettare i moduli esistenti e fare modifiche circoscritte. Non ricominciare
refactor già affrontati sulla base di vecchie descrizioni: controlla lo stato
dei file. Il motore di routing effettivo va verificato in `service/config.py`
e nei chiamanti; un piano GraphHopper non autorizza a sostituire BRouter.

## Principi e vincoli

- Il viaggio è centrale, il GPX è una guida, la realtà prevale sul piano;
  le scelte appartengono al viaggiatore e la conoscenza va preservata.
- Funzionalità fondamentali disponibili offline. Un servizio remoto può
  arricchirle, non diventare una dipendenza obbligatoria senza una decisione.
- UI solo PySide6; non introdurre PyQt5, PyQt6, PySide2 o tkinter.
- `basemap-styles-master/` è codice esterno: non modificarlo.
- Preservare dati dell'utente in `data/`, `fonts/`, `gpx/` e le altre
  raccolte GPX. La lettura necessaria al compito è consentita; modifiche,
  migrazioni o cancellazioni richiedono un incarico esplicito.
- `blocchi_ordine` rappresenta l'ordine ufficiale del viaggio: non modificarlo
  senza autorizzazione. Prima di intervenire su `database/database_setup.py`
  prepara il backup pertinente e chiarisci gli effetti sui dati.
- Nuove dipendenze e cancellazioni di file richiedono autorizzazione.
- Non esporre credenziali, chiavi o configurazioni private nei report o in Git.

## Documenti da consultare per argomento

| Argomento | Fonti |
|---|---|
| Database | `REPORT/DB_SCHEMA.md`, schema e query effettive |
| Configurazioni e URL | `REPORT/CONFIG_FILES.md`, `REPORT/EXTERNAL_SERVICES.md`, sorgenti |
| GPX e precalcolo | `REPORT/REGOLE_GPX.md`, `REPORT/PIANO_PRECALCOLO.md` |
| Clima e stagionalità | `REPORT/VISIONE_CATENA_STAGIONALE.md`, `REPORT/PIANO_CATENA_STAGIONALE.md`, `REPORT/ANALISI_CLIMA.md` |
| Pianificatore | `REPORT/VISIONE_PIANIFICATORE.md`, `REPORT/PROGETTO_PIANIFICATORE.md`, `REPORT/ANALISI_PIANIFICATORE.md` |
| Mappe e routing futuro | `REPORT/PROGETTO_MAPPE_OFFLINE.md`, `REPORT/PIANO_MIGRAZIONE_GRAPHHOPPER.md` |
| Prove statiche e Git | `REPORT/report.md`, `REPORT/PERCORSO.md`; `REPORT/analisi.json` solo per dettagli necessari |

Visioni, piani e analisi storiche possono essere superati. Confrontali con
codice e prove; non usarli come una lista automatica di lavori da eseguire.
`REPORT/ARCHIVIO` e contesti datati servono solo a ricerche storiche richieste.

## Verifica e continuità

Esegui verifiche pertinenti al cambiamento e riferisci cosa è passato, cosa
non è stato eseguito e perché. Non installare dipendenze per aggirare un
ambiente non funzionante senza autorizzazione.

Dopo modifiche significative al codice, se Python è disponibile, rigenera
la fotografia con `python -B analisi_profonda.py`. `--check` analizza senza
scrivere; `--no-db` esclude SQLite. L'analizzatore non sostituisce i test
dell'app. Non mantenere a mano i suoi dieci output: sono elencati in
`(ananlisi_profonda)-LEGGIMI.txt`. Gli altri file in REPORT sono documenti
di progetto, non tutti output automatici.

Prima della chiusura prepara il resoconto JSON nel percorso comunicato
dal hook, secondo `CONTINUITA.md`, anche `[]` se non ci sono nuovi risultati.
Le decisioni richiedono una citazione esatta e la ricevuta della richiesta;
risultati, proposte e tentativi abbandonati restano distinti. Il motore
importa il resoconto e aggiorna la sezione automatica di `STORIA_PROGETTO.md`.
Preserva la ricostruzione originale e non modificare a mano le parti generate.
Concludi con cambiamenti, verifiche e limiti. Non fare commit o push automatici
senza un incarico dell'utente che comprenda quelle operazioni.
