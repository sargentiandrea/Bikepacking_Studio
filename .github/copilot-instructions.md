# Istruzioni per GitHub Copilot — Progetto Bikepacking Studio

## CHI SEI E COME DEVI COMPORTARTI

Stai assistendo un progetto Python desktop + backend Flask chiamato **Bikepacking Studio**.
L'utente che ti guida è un **regista non-tecnico**: sa cosa vuole ottenere, ma non scrive codice e non conosce i dettagli di sintassi. Il tuo compito è tradurre le sue intenzioni in modifiche concrete, **spiegando sempre cosa fai e perché**, in italiano semplice.

**Regola numero uno**: prima di modificare qualunque cosa, spiega in 2-3 righe cosa stai per fare e quali file toccherai. Poi procedi. Mai silenziosamente.

---

## PRINCIPI FONDATIVI DEL PROGETTO

Il documento `REPORT/FIRST_PRINCIPLES.md` contiene i 13 principi fondativi di Bikepacking Studio. Ogni decisione tecnica deve essere coerente con questi principi.

In particolare, ricorda sempre:
- Il viaggio non è il percorso (il GPX è una guida, non un vincolo)
- La realtà ha priorità sul piano (l'app deve adattarsi ai cambiamenti)
- L'IA è un assistente (suggerisce, non decide)
- La connessione è utile ma non obbligatoria (offline-first)
- Ogni viaggio genera conoscenza (da preservare)

Prima di ogni intervento significativo, chiediti: "Questa modifica è coerente con i principi fondativi?"

---

## CONTESTO DEL PROGETTO

- **Nome**: Bikepacking Studio
- **Tipo**: applicazione desktop con backend mappa Flask
- **Framework UI**: **PySide6** (obbligatorio)
- **Backend mappe**: Flask + MapLibre GL 5.6.2 (con proiezione globo)
- **Database**: SQLite (`data/bikepacking_app.db`)

### Architettura (rispettala sempre)

- `gui/` → interfaccia desktop (PySide6): dashboard, mappa, wizard
- `service/` → logica di dominio: audit, clima, dogane, mappa, statistiche, config, precalcolo, catena stagionale
- `database/` → setup e accesso al database
- `app_desktop.py` → entry point dell'app desktop
- `templates/` → template HTML per la mappa
- `static/` → risorse statiche (JS, CSS, sprite)
- `resources/` → risorse generate (catalogo sprite)

### File critici (da trattare con particolare cautela)

- `gui/mappa.py` (~9 classi, 87 funzioni — **God Object attuale, priorità di refactor**)
- `app_desktop.py` (~5 classi, 52 funzioni — God Object storico)
- `gui/dashboard.py` (2 classi, 20 funzioni)

Questi tre file contengono la maggior parte della logica dell'app. **Non riscriverli mai da capo in un colpo solo.** Intervieni con modifiche piccole e verificabili.

### Servizi principali (creati durante il precalcolo)

- `service/gpx_metrics_service.py` → calcolo metriche GPX (distanza, dislivello, pendenza)
- `service/precalcolo_service.py` → salvataggio metriche in `tappa_analisi`
- `service/precalcolo_batch_service.py` → precalcolo di massa (992+ tappe)
- `service/geometria_service.py` → geometria semplificata (Ramer-Douglas-Peucker)
- `service/costa_service.py` → calcolo distanza dalla costa
- `service/catena_stagionale_service.py` → catena temporale e scenari
- `service/clima_estrattore.py` → estrazione dati CHELSA
- `service/stats_service.py` → statistiche progetto (legge da `tappa_analisi`)

---

## VINCOLI TECNICI (mai violare)

1. **UI**: solo **PySide6**. Mai `PyQt5`, `PyQt6`, `PySide2` o `tkinter`. Se li trovi, segnalali come anomalia.
2. **Non modificare** la cartella `basemap-styles-master/` (è codice esterno).
3. **Non toccare** `data/`, `fonts/`, `gpx/` (sono dati dell'utente, non codice).
4. **Non toccare** `REPORT/` (sono output generati automaticamente).
5. **Non introdurre nuove dipendenze** senza chiedere esplicitamente il permesso all'utente.
6. **Non cancellare file** senza autorizzazione esplicita.
7. **Non modificare** `database/database_setup.py` senza backup preventivo.
8. **Non toccare `blocchi_ordine`** in lettura/scrittura senza autorizzazione (è l'ordine ufficiale del viaggio).
9. **Offline-first**: nessuna funzionalità fondamentale deve richiedere internet per funzionare.

---

## REGOLE OPERATIVE

1. **Prima di ogni intervento strutturale**, leggi il file `REPORT/AI_BRIEF.md` (se esiste) per capire lo stato attuale del progetto.
2. **Interventi piccoli e verificabili**: una modifica = un obiettivo chiaro. Non mescolare più cose nella stessa richiesta.
3. **Dopo ogni modifica significativa**, ricorda all'utente di lanciare `analisi_profonda.py` per verificare il changelog.
4. **Se un task è ambiguo**, fai **una domanda** all'utente prima di procedere. Non inventare.
5. **Se il task è complesso**, proponi un **piano in 2-3 passi** e attendi approvazione prima di eseguire.
6. **Non toccare file fuori dal perimetro** che ti viene indicato esplicitamente nell'ordine.
7. **Se il task è chiaro**, procedi direttamente senza chiedere ulteriori conferme.

---

## COME COMUNICARE

- Parla **italiano semplice**. Niente gergo tecnico non spiegato.
- Quando usi un termine tecnico, spiegalo in una riga.
- Dopo ogni modifica, mostra un **riepilogo**: cosa hai cambiato, in quali file, e perché.
- Se qualcosa non ti è chiaro, **dillo**. Meglio una domanda in più che un disastro silenzioso.

---

## OBIETTIVO A LUNGO TERMINE

Il progetto deve diventare un'app multi-piattaforma (desktop, web, iOS, Android) per bikepacking, con funzionalità avanzate di pianificazione percorso, analisi clima, dogane internazionali, e certificazione di viaggi intercontinentali.

Lavoriamo per passi. Preferiamo **una modifica piccola e sicura al giorno** a un refactor gigantesco che rompe tutto.

---

## PROBLEMI ARCHITETTURALI NOTI (aggiornato 2026-10-02)

### Refactor prioritario: `gui/mappa.py`
È diventato il file più grande del progetto (9 classi, 87 funzioni). Contiene:
- Rendering MapLibre
- Worker di caricamento
- Cache per progetto
- Proiezione globo
- Pianificatore percorso
- Gestione waypoint
- Superfici, nomi luoghi, altimetria

**Va spezzato in moduli più piccoli** (es. `mappa_worker.py`, `mappa_cache.py`, `mappa_pianificatore.py`). Da pianificare con calma.

### Duplicazioni tra `app_desktop.py` e `gui/dashboard.py`
10 funzioni sono duplicate. Casi critici:
- `elimina_percorso_corrente`: la versione in `app_desktop.py` cancella da più tabelle (tappe, allarmi, trasferimenti, ordine blocchi), quella in `gui/dashboard.py` solo progetto e tappe. **BUG LATENTE da risolvere.**
- `toggle_pausa_tappa`, `cambia_ruolo_tappa`, `elimina_singola_tappa`: versioni in `app_desktop.py` contengono logica aggiuntiva (audit, mappa, allarmi) non presente in `gui/dashboard.py`. Da allineare.
- `apri_percorso_selezionato`, `crea_nuovo_progetto_dialog`, `aggiorna_blocco_tappa`: copie non usate, rimovibili.

### `calcola_distanza_haversine` in 3 file
Definita in `app_desktop.py`, `gui/dashboard.py`, `service/audit_service.py`. Da centralizzare in `service/geo_utils.py`.

### Residui del database (da pulire)
- Tappa "variante" (ID 43 o 1123) con stato anomalo
- Gap ricomparso nella pagina Audit
- Blocco Italia con nome incoerente tra `blocchi_ordine` e `tappe`
- Cartella con nome generale nell'elenco percorsi
- 21 violazioni di chiavi esterne in `allarmi_percorso` (20) e `trasferimenti` (1)
- Tabelle vuote o inutilizzate (`dogane_percorso`, `anagrafica_paesi_mondo`)

### Priorità di intervento
1. Refactor `gui/mappa.py` (God Object attuale)
2. Risolvere bug `elimina_percorso_corrente` (pulizia DB incompleta)
3. Pulire i residui del database
4. Allineare `toggle_pausa_tappa`, `cambia_ruolo_tappa`, `elimina_singola_tappa`
5. Rimuovere copie morte: `apri_percorso_selezionato`, `crea_nuovo_progetto_dialog`, `aggiorna_blocco_tappa`
6. Centralizzare `calcola_distanza_haversine` in `service/geo_utils.py`

---

## COSA LEGGERE E QUANDO

All'inizio di OGNI richiesta:
- Leggi `REPORT/AI_BRIEF.md` per lo stato generale del progetto.

Prima di lavorare su DATABASE:
- Leggi `REPORT/DB_SCHEMA.md` per lo schema completo del database.

Prima di lavorare su CONFIGURAZIONE:
- Leggi `REPORT/CONFIG_FILES.md` per i file di configurazione.

Prima di lavorare su SERVIZI ESTERNI (Martin, tile server, ecc.):
- Leggi `REPORT/EXTERNAL_SERVICES.md` per l'elenco dei servizi esterni.

Prima di lavorare su CATENA STAGIONALE O CLIMA:
- Leggi `REPORT/VISIONE_CATENA_STAGIONALE.md` (la visione)
- Leggi `REPORT/PIANO_CATENA_STAGIONALE.md` (il piano)
- Leggi `REPORT/ANALISI_CLIMA.md` (cosa fa oggi)

Prima di lavorare su PRECALCOLO:
- Leggi `REPORT/PIANO_PRECALCOLO.md` (il piano)
- Leggi `REPORT/REGOLE_GPX.md` (le regole)

Se ti serve un DETTAGLIO su un modulo specifico:
- Leggi `REPORT/analisi.json` (dataset completo) oppure
- Leggi direttamente il file di codice interessato.

NON leggere:
- `aider_context.md` (specifico per Aider)
- File con timestamp nel nome (sono storico)
- `ULTIMO_RUN.json` (serve solo allo script)