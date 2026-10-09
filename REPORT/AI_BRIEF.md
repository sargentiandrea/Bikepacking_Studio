# Fotografia del progetto — Bikepacking_Studio

Scansione `c68e5bf3741dde1f` · 2026-10-09T20:29:39.639501+00:00 · script 4.1

Documento generato: fatti osservati e limiti dichiarati. Non certifica l’esecuzione dell’app.

## Contesto per una nuova chat

Bikepacking Studio nasce per preparare e accompagnare viaggi reali in bicicletta, conservando la conoscenza raccolta prima, durante e dopo il viaggio.
Il repository contiene l’app desktop Python/PySide6, una mappa web servita da Flask/MapLibre e SQLite. La direzione futura comprende un’app consumer desktop, web, iOS e Android; questa scansione non ne certifica la realizzazione.
Principi: il viaggio è centrale; il GPX guida senza vincolare; la realtà prevale sul piano; l’IA assiste e il viaggiatore decide; le funzioni essenziali devono funzionare offline.

Ruoli: Codex segue analisi, modifiche, verifiche e continuità del repository (`AGENTS.md`); Copilot segue il codice e l’integrazione dell’app (`.github/copilot-instructions.md`); Cline segue soprattutto la produzione di mappe, routing e dati su Hetzner e la distribuzione Cloudflare R2 (`.clinerules`). Gli accessi remoti configurati per Cline non sono verificati da questo report.

**Uso con DeepSeek, Gemini, ChatGPT o altre chat:** allega questo file e indica l’obiettivo della sessione. Il brief fornisce il contesto iniziale; allega poi i sorgenti o i documenti necessari al compito. Una chat senza accesso ai file non può considerarli letti né verificare lo stato corrente.
Puoi accompagnarlo con: «Parliamo in italiano semplice. Usa la fotografia e i suoi limiti, distingui fatti, storia e proposte; chiedimi le fonti mancanti prima di formulare diagnosi o modifiche. Obiettivo di questa sessione: …».

Questo file si aggiorna eseguendo `python -B analisi_profonda.py`, non modificandolo a mano. La data e il commit sotto descrivono il momento della scansione. Prima di una nuova chat rigeneralo se il progetto è cambiato; se non puoi, dichiara che la fotografia può essere superata.

## Come orientarsi

- Questo brief: fotografia automatica corrente.
- `STORIA_PROGETTO.md`: origini, motivazioni e storia dalle chat; non viene riscritta.
- `REPORT/FIRST_PRINCIPLES.md` e `REPORT/REGOLE_GPX.md`: principi e regole.
- `REPORT/report.md`: struttura, prove, errori e indizi.
- `REPORT/PERCORSO.md`: cronologia Git locale senza interpretazioni di completamento.
- `REPORT/DB_SCHEMA.md`, `CONFIG_FILES.md`, `EXTERNAL_SERVICES.md`: dettagli mirati.
- `REPORT/analisi.json`: dataset completo. `ULTIMO_RUN.json`: manifest per il confronto.

## Stato della lettura

- Ramo: `main`; commit: `0c4a46595729`.
- Modifiche locali prima dei report: 15.
- Python: 78 file analizzati su 78.
- Classi: 50; funzioni di modulo: 250; metodi: 348; funzioni annidate: 8.
- HTTP: 8 indirizzi, 9 coppie indirizzo/metodo dichiarate.
- Database: letto_in_sola_lettura; tabelle applicative: 23.
- Errori di scansione: 0; indizi statici: 11.

## Struttura osservata

| Area | Moduli Python |
|---|---|
| database | 1 |
| interfaccia | 25 |
| servizio | 39 |
| strumento_o_avvio | 6 |
| test | 7 |

## Componenti presenti nel codice

Questa mappa indica dove leggere il codice; la presenza dei file non certifica il completamento.

| Componente | File osservati |
|---|---|
| Avvio desktop e dashboard | `app_desktop.py`, `gui/dashboard.py` |
| Mappa e pianificatore | `gui/mappa.py`, `gui/mappa_pianificatore.py`, `service/map_server.py` |
| Progetti, tappe e GPX | `service/progetti_service.py`, `service/tappe_service.py`, `service/salvataggio_tappa_service.py`, `service/gpx_metrics_service.py` |
| Routing e superfici | `service/dettagli_rotta_service.py`, `service/routing_timeout_service.py`, `service/superfici_service.py` |
| Clima | `service/clima_service.py`, `service/clima_estrattore.py`, `gui/pagine/controller_clima.py` |
| Catena stagionale e precalcolo | `service/catena_stagionale_service.py`, `service/precalcolo_service.py`, `service/precalcolo_batch_service.py` |
| Mappe e geocodifica offline | `service/map_manager_service.py`, `service/geocodifica_offline_service.py`, `service/geonames_service.py` |
| Trasferimenti, dogane e statistiche | `service/trasferimenti_service.py`, `service/dogane_service.py`, `service/stats_service.py` |
| Persistenza e audit | `database/database_setup.py`, `service/audit_service.py` |

## Moduli più estesi

La dimensione orienta la lettura; non misura rischio o qualità.

| File | Righe | Definizioni |
|---|---|---|
| gui/mappa_pianificatore.py | 1652 | 45 |
| service/catena_stagionale_service.py | 1268 | 27 |
| service/stats_service.py | 768 | 14 |
| gui/dashboard.py | 632 | 21 |
| app_desktop.py | 600 | 44 |
| service/salvataggio_tappa_service.py | 580 | 7 |
| gui/mappa.py | 573 | 28 |
| gui/pagine/controller_clima.py | 552 | 24 |

## Cambiamenti dalla precedente scansione

- Aggiunti: 1.
- Rimossi: 0.
- Modificati: 0.
- Analizzatore modificato: sì.
- Commit Git cambiato: no; i cambiamenti alle fonti sono conteggiati separatamente.

## Limiti

- Nessun test dell’app eseguito; comportamento runtime non certificato.
- Servizi, server e contenuti R2 non contattati.
- Riferimenti basati su nomi AST: alias, omonimie e uso dinamico limitano la precisione.
- I riferimenti SQL non stabiliscono a quale database appartenga una tabella.
- Decorator HTTP rilevati staticamente: registrazione e prefissi Blueprint non verificati.
- HTML/JS/CSS inventariati, incluse librerie esterne; sintassi e comportamento non verificati.
- Storia, visioni e piani sono fonti documentali, non prove di implementazione.
- Cartelle escluse: .agents, .aws, .codex, .git, .idea, .mypy_cache, .pytest_cache, .venv, .vscode, GPX CORSICA, REPORT, __pycache__, basemap-styles-master, build, data, dist, fonts, gpx, node_modules, venv
