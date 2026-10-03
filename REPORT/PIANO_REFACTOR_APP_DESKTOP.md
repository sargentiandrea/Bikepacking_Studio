# Piano di refactor — `app_desktop.py`

Documento di **sola analisi**: nessun file di codice è stato modificato.
Data analisi: 2026-10-03. File analizzato: `app_desktop.py` (**2339 righe**, ~100 KB, 8 classi, 50 metodi nella classe principale + 1 funzione di modulo).
Metodo: stessa impostazione usata per `REPORT/PIANO_REFACTOR_MAPPA.md` (refactor a sotto-fasi, dal più semplice al più complesso, un commit per sotto-fase, verifica manuale).

> Obiettivo dichiarato dal regista: **riorganizzare** il file, **non riscriverlo da zero**. Ogni fase sposta codice quasi per copia, mantenendo il comportamento.

---

## 0. Cosa è stato letto e cosa no (onestà sui limiti)

| Fonte | Esito |
|---|---|
| `app_desktop.py` (2339 righe) | Letto **in modo strutturato** (AST: elenco completo di classi, metodi, intervalli di righe) e **per intero nelle parti di logica**: metodi di pagina, audit, clima, tappe, trasferimenti, dialoghi. Non letto riga per riga: alcune sezioni di pura grafica dentro `crea_pagina_clima` (~749-860), `crea_pagina_statistiche` (~862-945) e la parte centrale di `avvia_wizard_trasferimento` (2080-2200). Per la proposta bastano nomi, responsabilità e posizione. |
| `REPORT/FIRST_PRINCIPLES.md` | Letto. Non è un documento di codice, ma tre principi guidano questo refactor: **8** (il *viaggio* è l'entità centrale → la finestra principale deve orchestrar, non contenere tutto), **9** (offline: nessuna parte deve rompersi senza rete), **13** (non un semplice pianificatore GPX → l'app deve poter crescere). |
| `REPORT/AI_BRIEF.md` | Letto. Conferma: `app_desktop.py` è il **file critico n.1** (score 438), 8 classi, 70 funzioni, molti simboli segnalati **orfani**. |
| `REPORT/PIANO_REFACTOR_MAPPA.md` | Letto per intero: è il **modello** di metodo che replico qui. |
| Punto di avvio | `Avvia_Bikepacking_Studio.bat` lancia `python app_desktop.py`. Quindi `app_desktop.py` **è** l'entry point: il blocco `if __name__ == "__main__"` (righe 2334-2338) resta qui. |
| Test automatici | Cercati (`test*.py`): **non ce ne sono**. Ogni fase va verificata a mano (avvio app + prova manuale della pagina coinvolta). |

**Nota sul conteggio funzioni (verifica AST):** le classi reali sono 8 e `BikepackingStudioApp` ha 50 metodi, più 1 funzione di modulo (`determina_blocco_da_nome_file`). La differenza con le "70 funzioni" dell'AI_BRIEF dipende da come lo script di analisi conta le funzioni annidate (es. la funzione interna `salva()` dentro `crea_nuovo_progetto_dialog`, riga 1755). I simboli reali sono quelli elencati in §1.

---

## 1. Inventario

### 1.1 Le 8 classi

| # | Classe | Righe | Dim. | Cosa fa (in parole semplici) | Usata? |
|---|---|---|---|---|---|
| 1 | `DoganeSignals` | 42-43 | 2 | Segnale Qt mai usato. | ❌ **orfa** |
| 2 | `ClimaSignals` | 46-47 | 2 | Segnale Qt mai usato. | ❌ **orfa** |
| 3 | `EstrazioneClimaWorker` | 50-74 | 25 | Lavoro in background: legge i dati clima CHELSA. | ✅ |
| 4 | `ClimaSoglieDialog` | 77-145 | 69 | Finestra per le soglie del "semaforo climatico". | ✅ |
| 5 | `DropAreaGPX` | 214-239 | 26 | Riquadro "trascina qui i file GPX". | ❌ **orfa** (mai istanziata) |
| 6 | `TimelineCatenaWidget` | 242-318 | 77 | Disegna la timeline (barre colorate) dei blocchi del viaggio. | ✅ |
| 7 | `GestoreBlocchiWidget` | 321-447 | 127 | Pagina "Gestione Blocchi": elenca, riordina e riscrive l'ordine su SQLite. | ✅ |
| 8 | `BikepackingStudioApp` | 449-2332 | **1884** | **LA FINESTRA PRINCIPALE — fa tutto il resto del programma.** | ✅ (entry point) |

**Fatto chiave:** la classe 8 è l'**80% del file**. Tutto il resto sono piccoli widget/dialoghi/worker che le girano attorno.

### 1.2 Funzioni di modulo e script di supporto

| Funzione | Righe | Cosa fa | Usata? |
|---|---|---|---|
| `determina_blocco_da_nome_file(nome_file)` | 207-212 | Dal nome file GPX ricava il blocco (usa `MAPPA_PREFISSI_BLOCCHI`). | ❌ **orfa** |
| Blocco `if __name__ == "__main__"` | 2334-2338 | Crea `QApplication`, mostra la finestra, avvia l'event loop. | ✅ (entry point) |

**Import collaterali importanti (righe 23-25):**
```python
from service.map_server import start_local_map_server
start_local_map_server(port=8080)   # <-- effetto collaterale all'import!
```
Il server Flask delle mappe parte **all'import del modulo** (non dentro `main`). Va tenuto presente: nessun nuovo modulo deve avviare un secondo server.

**Costanti di modulo (righe 180-205), verificate con ricerca su tutto il progetto:**
- `MAPPA_PREFISSI_BLOCCHI` (180-198): usata **solo** dalla funzione orfana `determina_blocco_da_nome_file` → di fatto morta.
- `STILI_TRASPORTI` (199-205): compare **una sola volta** nel progetto (la sua definizione), e i suoi valori (`#00a8ff`, `dashArray`, ...) **non sono referenziati** da nessun `.py`, `.html` o `.js` → **codice morto**.

### 1.3 I 50 metodi di `BikepackingStudioApp`, raggruppati per responsabilità

| # | Gruppo | Metodi (righe) | Cosa fanno |
|---|---|---|---|
| A | **Costruzione finestra** | `__init__` (451-577), `crea_bottone_navigazione` (600-621), `cambia_pagina` (579-592) | Sidebar a icone, `QStackedWidget`, creazione delle 9 pagine, instradamento dei pulsanti. |
| B | **Costruzione pagine** | `crea_pagina_mappa` (623), `crea_pagina_audit` (627-664), `_stile_pagina_servizio` (666-680), `crea_pagina_trasporti` (682-720), `crea_pagina_dogane` (722-747), `crea_pagina_clima` (749-860), `crea_pagina_statistiche` (862-945), `crea_pagina_placeholder` (1669-1680) | Costruiscono la grafica di ogni pagina di servizio. |
| C | **Elenco paesi** | `apri_finestra_elenco_paesi` (947-1042) | Finestra con bandierine (sprite) + nomi paesi. |
| D | **Trasporti / logistica** | `aggiorna_pagina_trasporti` (1051-1085), `raccorda_gap_selezionato` (1087-1110), `avvia_wizard_trasferimento` (1999-2262) | Tabella trasferimenti; finestra per registrare un mezzo che copre un "gap". |
| E | **Dogane** | `aggiorna_pagina_dogane` (1112-1126) | Riempie la tabella dogane (usa `service.dogane_service`). |
| F | **Clima / catena stagionale** | `aggiorna_pagina_clima` (1128-1197), `calcola_pagina_clima` (1199-1362), `_carica_soglie_clima` (1364-1373), `apri_soglie_clima` (1375-1400), `avvia_estrazione_clima` (1402-1435), `_estrazione_clima_completata/_fallita/_terminata` (1437-1453), `_aggiorna_controlli_scenario` (1455-1485), `sposta_blocco_scenario` (1487-1506), `ripristina_ordine_scenario` (1508-1515), `conferma_scenario_clima` (1517-1557), `annulla_ultima_applicazione_scenario` (1559-1603), `salva_impostazioni_clima` (1605-1620) | La più grande area di logica: calcolo catena, scenari, worker CHELSA. |
| G | **Statistiche** | `aggiorna_pagina_statistiche` (1622-1667) | Riempie KPI e tabelle (usa `service.stats_service`). |
| H | **Gestione progetto/percorsi** | `gestisci_cambio_progetto` (594-598), `verifica_progetto_attivo` (1688-1689), `carica_lista_percorsi` (1691-1693), `apri_percorso_selezionato` (1695-1702), `crea_nuovo_progetto_dialog` (1704-1779), `apri_selettore_file` (1781-1795), `elabora_files_gpx` (1797-1800), `elimina_percorso_corrente` (1974-1990) | Stato del progetto attivo e dialogo "nuovo percorso". |
| I | **Audit / integrità** | `esegui_audit_automatico` (1802-1870), `raccorda_traccia_istantaneo` (1872-1904) | Controlla i "gap" tra le tappe, crea allarmi, genera il raccordo GPX. |
| J | **Gestione tappe (tabella)** | `aggiorna_tabella_tappe` (1906-1912), `aggiorna_blocco_tappa` (1914-1920), `toggle_pausa_tappa` (1922-1933), `cambia_ruolo_tappa` (1935-1948), `elimina_singola_tappa` (1950-1972), `mostra_mappa_gap` (1992-1997) | Operazioni sulle singole tappe dal DB. |
| K | **Tabella allarmi** | `aggiorna_tabella_allarmi` (2264-2332) | Riempie la tabella allarmi con i pulsanti "Mappa GAP", "Raccorda GPX", "Logistica". |
| L | **Utility** | `_imposta_righe_tabella` (1044-1049), `apri_pagina_clima` (1682-1683), `apri_pagina_statistiche` (1685-1686) | Helper vari. |

### 1.4 Responsabilità trasversali presenti nel file

| # | Responsabilità | Dove vive oggi |
|---|---|---|
| 1 | **Bootstrap / entry point** | Blocco `__main__` + `start_local_map_server()` all'import |
| 2 | **Shell dell'app** (sidebar, stacked, cambio pagina) | `BikepackingStudioApp.__init__`, `cambia_pagina` |
| 3 | **Stato globale progetto** (`current_progetto_id`, `current_progetto_nome`, `mappa_necessita_aggiornamento`) | campi della finestra, letti anche da `gui/dashboard.py` e `gui/mappa.py` |
| 4 | **Costruzione grafica** pagine di servizio | metodi `crea_pagina_*` |
| 5 | **Logica di dominio con SQL** (audit gap, tappe, ordine blocchi, trasferimenti, creazione progetto) | metodi misti nella finestra + `GestoreBlocchiWidget` |
| 6 | **Ciclo di vita di un worker** (clima) | `avvia_estrazione_clima` + 3 callback |
| 7 | **Dialoghi** (nuovo progetto, soglie clima, wizard trasferimento, elenco paesi) | metodi/dialog locali |
| 8 | **Utility di presentazione** (sprite bandiere, tabelle, stili) | `apri_finestra_elenco_paesi`, `_imposta_righe_tabella`, `_stile_pagina_servizio` |

### 1.5 Collegamenti (accoppiamenti) da conoscere prima di toccare

| Da → a | Cosa | Perché conta |
|---|---|---|
| `gui/dashboard.py` → app | Riceve `main_window`; usa `self.main_window.current_progetto_id`, `.aggiorna_tabella_allarmi()`, `.carica_lista_percorsi()`, ecc. | La finestra **è** l'interfaccia di fatto per la dashboard. |
| `gui/mappa.py` → app | `MappaWidget(self)`; usa `parent_app` (progetto, audit, allarmi, dashboard, `mappa_necessita_aggiornamento`). | Idem (già noto dal piano mappa, domanda 6.7.4). |
| `GestoreBlocchiWidget` → app | Chiama `self.parent_app.esegui_audit_automatico()`, `.aggiorna_tabella_tappe()`, `.aggiorna_tabella_allarmi()`, `.mappa_necessita_aggiornamento`. | Se si sposta il widget, servono metodi pubblici stabili sulla finestra. |
| App → `EstrazioneClimaWorker` | Crea `QThread` + worker, collega 6 segnali. | Fase 4: estrarre il ciclo di vita. |
| Metodi tappe (gruppo J) ↔ `gui/dashboard.py` | **Duplicati**: `aggiorna_tabella_tappe`, `aggiorna_blocco_tappa`, `toggle_pausa_tappa`, `cambia_ruolo_tappa`, `elimina_singola_tappa`, `carica_lista_percorsi`, `apri_percorso_selezionato`, `elimina_percorso_corrente`, `crea_nuovo_progetto_dialog`. | Già segnalati in `AI_BRIEF.md`. Fase 6: portare la logica in `service/` e farla usare a entrambi. |

### 1.6 Problemi strutturali osservati (fatti, non opinioni)

1. **God-object**: 1884 righe su 2339 (80%) in una sola classe, che mescola shell, grafica, SQL, thread e file.
2. **SQL dentro la GUI**: audit (`esegui_audit_automatico`), tappe (`DELETE/UPDATE tappe`), ordine blocchi, creazione progetto, trasferimenti. Non testabili senza avviare la finestra.
3. **Duplicazione con `gui/dashboard.py`**: ~9 metodi con lo stesso nome e logica simile.
4. **Simboli orfani** (codice morto): `DoganeSignals`, `ClimaSignals`, `DropAreaGPX`, `determina_blocco_da_nome_file`, e le costanti `MAPPA_PREFISSI_BLOCCHI` (usata solo dall'orfana) e `STILI_TRASPORTI` (mai usata).
5. **Effetto collaterale all'import**: il server Flask (porta 8080) parte importando il file, non dentro `main`.
6. **Import locali e ripetuti**: `from service import stats_service` dentro i metodi (righe 952, 1636).
7. **`sqlite3.connect(DB_NAME)` ripetuto a mano** in decine di punti, a volte senza `contextlib.closing` (rischio connessioni non chiuse).
8. **Nessun test automatico.**

---

## 2. Proposta di divisione in moduli

Principio guida (ereditato dal piano mappa): **sposto prima ciò che non dipende dall'interfaccia e ciò che è "foglia" (widget/dialoghi autosufficienti), poi la logica di dominio, infine riduco la finestra a sola orchestration.**

`app_desktop.py` **resta il punto d'ingresso** (`Avvia_Bikepacking_Studio.bat` lo lancia). Alla fine conterrà solo: import, avvio server Flask, `BikepackingStudioApp` ridotta (shell + stato + wiring) e `main`.

### 2.1 Mappa dei moduli di destinazione

| Nuovo modulo | Contiene | Tocca Qt? | Beneficio |
|---|---|---|---|
| `gui/costanti_ui.py` | *(forse non serve)* `MAPPA_PREFISSI_BLOCCHI`, `STILI_TRASPORTI` | No | Entrambe le costanti risultano **morte**: probabilmente basta rimuoverle (Fase 1.1), senza creare il modulo |
| `gui/worker_clima.py` | `EstrazioneClimaWorker` | Sì | Riusa il pattern di `gui/mappa_worker.py` |
| `gui/dialog_clima_soglie.py` | `ClimaSoglieDialog` | Sì | Dialog isolato |
| `gui/dialog_elenco_paesi.py` | `apri_finestra_elenco_paesi` + helper sprite | Sì | Toglie ~95 righe |
| `gui/wizard_trasferimento.py` | La parte *dialogo* di `avvia_wizard_trasferimento` | Sì | Toglie ~260 righe |
| `gui/widget_timeline_catena.py` | `TimelineCatenaWidget` | Sì | Widget autonomo |
| `gui/widget_blocchi.py` | `GestoreBlocchiWidget` | Sì | Pagina autonoma |
| `gui/pagine/pagina_audit.py` | grafica di `crea_pagina_audit` + `aggiorna_tabella_allarmi` | Sì | Isola la pagina |
| `gui/pagine/pagina_trasporti.py` | `crea_pagina_trasporti` + `aggiorna_pagina_trasporti` + `raccorda_gap_selezionato` | Sì | Isola la pagina |
| `gui/pagine/pagina_dogane.py` | `crea_pagina_dogane` + `aggiorna_pagina_dogane` | Sì | Isola la pagina |
| `gui/pagine/pagina_clima.py` | `crea_pagina_clima` + tutto il gruppo F | Sì | Isola la pagina più grande (~450 righe) |
| `gui/pagine/pagina_statistiche.py` | `crea_pagina_statistiche` + `aggiorna_pagina_statistiche` | Sì | Isola la pagina |
| `gui/dialog_nuovo_progetto.py` | `crea_nuovo_progetto_dialog` (o fusione con `gui/wizard_percorso.py`) | Sì | Dedup con `gui/dashboard.py` |
| `service/audit_gap_service.py` | Logica di `esegui_audit_automatico` (senza Qt) | **No** | Testabile, riusabile |
| `service/tappe_command_service.py` | `elimina_singola_tappa`, `toggle_pausa_tappa`, `cambia_ruolo_tappa`, `aggiorna_blocco_tappa` (senza Qt) | **No** | Dedup con `gui/dashboard.py` |
| `service/trasferimenti_service.py` | Inserimento trasferimento da `avvia_wizard_trasferimento` (senza Qt) | **No** | Testabile |
| `service/blocchi_ordine_service.py` | SQL di riordino blocchi da `GestoreBlocchiWidget` | **No** | Testabile |
| `app_desktop.py` (finale) | import + `start_local_map_server` + `BikepackingStudioApp` ridotta + `main` | Sì | Firma chiara e stabile per gli altri moduli |

**Stima a fine refactor:** `app_desktop.py` da 2339 righe a **~350-450 righe** (solo shell + stato + wiring). Nessun nuovo file oltre ~500 righe.

**Cosa NON propongo** (e perché):
- **Non sposto** `BikepackingStudioApp` stessa: resta in `app_desktop.py` perché è l'entry point e le altre classi la importano. Diventa solo **più piccola**.
- **Non tocco** `gui/mappa.py` in questo refactor (ha il suo piano): qui si usano solo i suoi metodi pubblici già esistenti.
- **Non creo** un `service/` per la logica clima: vive già in `service/catena_stagionale_service.py` e `service/clima_service.py`. Il gruppo F è quasi tutto *wiring*, quindi va nel widget `pagina_clima.py`, non in un nuovo servizio.

---

## 3. Piano a sotto-fasi (dal più semplice al più complesso)

Regola operativa (come nel piano mappa): **un commit per sotto-fase**. Dopo ogni sotto-fase: avviare l'app, provare la funzione coinvolta, e solo se tutto funziona passare alla successiva.

### Fase 0 — Prerequisiti (rischio nullo)

| Cosa | File | Perché |
|---|---|---|
| Sincronizzare lo stato git pulito e creare un punto di ripristino (commit/tag) | — | Non ci sono test: il "paracadute" è il controllo di versione |
| Confermare che l'app parte da `Avvia_Bikepacking_Studio.bat` | — | È la verifica manuale di base di ogni fase |
| Annotare che il server Flask parte all'import (riga 25) | — | Non duplicarlo nei nuovi moduli |

### Fase 1 — Pulizia: codice morto e costanti (rischio **basso**)

| Sotto-fase | Cosa | File coinvolti | Rischio | Beneficio | Come verificare |
|---|---|---|---|---|---|
| **1.1** | Rimuovere i simboli orfani: `DoganeSignals`, `ClimaSignals`, `determina_blocco_da_nome_file` e le costanti `MAPPA_PREFISSI_BLOCCHI` / `STILI_TRASPORTI` (verificati morti) | `app_desktop.py` | **Basso** (non usati da nessuno) | -85 righe, meno rumore | Ricerca che i nomi non compaiano altrove (già fatta: nessun uso); avvio app |
| **1.2** | `DropAreaGPX`: decidere se spostarla in `gui/drop_area_gpx.py` (drag&drop GPX futuro) o rimuoverla | `gui/drop_area_gpx.py` (nuovo) o `app_desktop.py` | Basso | -26 righe | Avvio app |

> Nota su 1.2: `DropAreaGPX` **non è istanziata da nessuno**. Non è "morta per errore": è pronta per il drag&drop dei file GPX (funzione oggi gestita da `apri_selettore_file`). Il regista decide se conservarla (spostandola) o rimuoverla.

### Fase 2 — Widget autonomi (rischio **basso**)

| Sotto-fase | Cosa | File coinvolti | Rischio | Beneficio | Come verificare |
|---|---|---|---|---|---|
| **2.1** | `TimelineCatenaWidget` → `gui/widget_timeline_catena.py` (copia esatta + import) | `gui/widget_timeline_catena.py` (nuovo), `app_desktop.py` | Basso | -77 righe | Pagina Clima: la timeline si disegna |
| **2.2** | `GestoreBlocchiWidget` → `gui/widget_blocchi.py`; estrarre l'SQL di riordino in `service/blocchi_ordine_service.py` | 2 nuovi file, `app_desktop.py` | Basso-medio (SQL) | -127 righe, logica ordinamento testabile | Pagina Blocchi: riordino, salvataggio, effetto su audit |

> 2.2 va fatta **dopo** aver reso pubblici i metodi che il widget chiama sulla finestra (`esegui_audit_automatico`, `aggiorna_tabella_tappe`, `aggiorna_tabella_allarmi`, `mappa_necessita_aggiornamento`). Sono già pubblici: basta non rinominarli.

### Fase 3 — Dialoghi e finestre (rischio **medio-basso**)

| Sotto-fase | Cosa | File coinvolti | Rischio | Beneficio | Come verificare |
|---|---|---|---|---|---|
| **3.1** | `ClimaSoglieDialog` → `gui/dialog_clima_soglie.py` | nuovo file, `app_desktop.py` | Basso | -69 righe | Pulsante "Soglie clima": apre, valida, salva |
| **3.2** | `apri_finestra_elenco_paesi` + helper sprite → `gui/dialog_elenco_paesi.py` | nuovo file, `app_desktop.py` | Basso-medio (legge `sprite.json`) | -95 righe | Pulsante statistiche: apre l'elenco con le bandiere |
| **3.3** | `crea_nuovo_progetto_dialog` → `gui/dialog_nuovo_progetto.py`, **valutando** la fusione con `gui/wizard_percorso.py` (che ha già `WizardNuovoPercorsoDialog` + `conferma_creazione`, duplicati) | nuovo file, `app_desktop.py`, `gui/dashboard.py` | Medio (dedup) | -75 righe + una sola copia del wizard | Creare un nuovo percorso: ID, nome, apertura mappa |
| **3.4** | Parte *dialogo* di `avvia_wizard_trasferimento` → `gui/wizard_trasferimento.py`; la scrittura su DB va in `service/trasferimenti_service.py` (fase 6.3). Il metodo sulla finestra resta come "orchestratore" | nuovo file, `app_desktop.py` | Medio (form grande, ~260 righe) | -260 righe | Tabella audit: "Logistica/Mezzo" → inserisce trasferimento, il gap sparisce |

### Fase 4 — Worker clima (rischio **medio**)

| Sotto-fase | Cosa | File coinvolti | Rischio | Beneficio | Come verificare |
|---|---|---|---|---|---|
| **4.1** | `EstrazioneClimaWorker` → `gui/worker_clima.py` | nuovo file, `app_desktop.py` | Basso (copia) | -25 righe, coerenza con `gui/mappa_worker.py` | Avvio estrazione CHELSA |
| **4.2** | Estrarre il ciclo di vita `QThread` (attiva/ferma/finally) dal metodo `avvia_estrazione_clima` + 3 callback. **Riusare** `gui/mappa_worker_manager.py` `GestoreWorkerSingolo` (già scritto nel refactor mappa) | `app_desktop.py`, `gui/mappa_worker_manager.py` | **Medio**: è un thread con segnali | -40 righe, un solo pattern di thread | Estrazione con cambio progetto nel mezzo; chiusura app con worker attivo |

### Fase 5 — Pagine di servizio (rischio **medio**)

| Sotto-fase | Cosa | File coinvolti | Rischio | Beneficio | Come verificare |
|---|---|---|---|---|---|
| **5.1** | `pagina_audit.py` (`crea_pagina_audit` + `aggiorna_tabella_allarmi`) | nuovo file, `app_desktop.py` | Medio | -90 righe | Pagina Audit: tabella allarmi + i 3 pulsanti |
| **5.2** | `pagina_trasporti.py` (`crea_pagina_trasporti` + `aggiorna_pagina_trasporti` + `raccorda_gap_selezionato`) | nuovo file, `app_desktop.py` | Medio | -100 righe | Pagina Trasporti: 2 tab, aggiorna, raccorda |
| **5.3** | `pagina_dogane.py` (`crea_pagina_dogane` + `aggiorna_pagina_dogane`) | nuovo file, `app_desktop.py` | Basso-medio | -40 righe | Pagina Dogane: tabella popolata |
| **5.4** | `pagina_statistiche.py` (`crea_pagina_statistiche` + `aggiorna_pagina_statistiche`) | nuovo file, `app_desktop.py` | Medio | -85 righe | Pagina Statistiche: KPI e tabelle |
| **5.5** | `pagina_clima.py` (`crea_pagina_clima` + **tutto** il gruppo F: calcolo, scenari, soglie, estrazione, salvataggio) | nuovo file, `app_desktop.py` | **Medio-alto** (è la più grande e intrecciata: tocca `page_blocchi`, worker, DB) | -450 righe | Pagina Clima: calcolo, scenario sposta/ripristina/conferma/annulla, salva, estrai |

> **Ordine consigliato dentro la Fase 5:** 5.3 → 5.2 → 5.1 → 5.4 → 5.5 (dal più semplice al più complesso). La 5.5 va per ultima perché è la più densa di stato (`_clima_*`) e di interazioni.

### Fase 6 — Logica di dominio → `service/` (rischio **medio-alto**)

| Sotto-fase | Cosa | File coinvolti | Rischio | Beneficio | Come verificare |
|---|---|---|---|---|---|
| **6.1** | `esegui_audit_automatico` → `service/audit_gap_service.py` (senza Qt) | nuovo file, `app_desktop.py` | Medio-alto (SQL + haversine) | Testabile senza finestra | Dopo ogni operazione tappa: gli allarmi si ricalcolano |
| **6.2** | Operazioni tappa (`elimina_singola_tappa`, `toggle_pausa_tappa`, `cambia_ruolo_tappa`, `aggiorna_blocco_tappa`) → `service/tappe_command_service.py`; farle usare **anche** a `gui/dashboard.py` (dedup) | nuovo file, `app_desktop.py`, `gui/dashboard.py` | **Alto** (tocca due moduli) | -60 righe + una sola copia | Elimina/pausa/ruolo tappa da Dashboard e da app |
| **6.3** | Inserimento trasferimento → `service/trasferimenti_service.py` | nuovo file, `app_desktop.py` | Medio (SQL, già scritto) | Testabile | Wizard trasferimento + controllo duplicati |

### Fase 7 — Shell finale (rischio **alto**, ma è l'obiettivo)

| Sotto-fase | Cosa | File coinvolti | Rischio | Beneficio | Come verificare |
|---|---|---|---|---|---|
| **7.1** | `BikepackingStudioApp` ridotta a: stato progetto, sidebar + stacked, wiring pagine, cambio pagina, orchestrazione. Rimuovere dalla finestra i metodi spostati e importare i nuovi widget/pagine | `app_desktop.py` | Alto (è il cuore) | File da 2339 → ~400 righe | Giro completo: tutte le 9 pagine, cambio progetto, chiusura |

**Ordine obbligato:** 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7. Un commit per sotto-fase; la verifica manuale è obbligatoria dopo ognuna.

---

## 4. Verifica (cosa si può e non si può controllare)

| Verifica | Possibile? |
|---|---|
| Sintassi, Pylance, import, `git diff --check`, `python -c "import ast; ast.parse(open('app_desktop.py').read())"` | Sì |
| Import dei nuovi moduli senza avviare la GUI (es. `python -c "import gui.widget_timeline_catena"`) | Sì, ma `app_desktop.py` avvia il server Flask all'import: verificare i moduli **senza** importare l'app |
| Funzioni di servizio pure (`service/audit_gap_service`, `service/tappe_command_service`) su un **DB temporaneo di prova** | Sì |
| Creazione dei widget con `QT_QPA_PLATFORM=offscreen` | Sì, ma non copre mouse e rendering reale |
| Giro completo dell'app, cambio progetto, chiusura pulita, thread con finestra aperta | **No** da terminale: serve la prova manuale dell'utente |

## 5. Criteri di stop (quando una fase non è buona)

Fermarsi e tornare indietro se dopo una sotto-fase:
- l'app non parte da `Avvia_Bikepacking_Studio.bat`;
- una delle 9 pagine non si apre o resta vuota;
- il cambio progetto non aggiorna la pagina attiva;
- l'app va in crash alla chiusura o dopo un cambio rapido di progetto (thread ancora attivo);
- compaiono errori di import circolare (sintomo tipico: `app_desktop` ↔ `gui/*`).

## 6. Domande aperte

| # | Questione | Opzioni / trade-off | Raccomandazione |
|---|---|---|---|
| 6.1 | **`DropAreaGPX` è codice morto**: eliminare o conservare? | Eliminare = meno rumore; spostare in `gui/drop_area_gpx.py` = pronta se servirà il drag&drop GPX | Chiedere al regista; se non c'è un piano d'uso, spostarla (non cancellarla) |
| 6.2 | **`DoganeSignals` / `ClimaSignals`**: erano per un worker dogane/clima mai completato? | Rimuovere = pulizia; sono il segno di una feature incompleta | Rimuovere, ma segnalarlo come "feature possibile in futuro" |
| 6.3 | **Dedup tappe con `gui/dashboard.py`**: unificare ora o dopo? | Ora (fase 6.2) = più veloce ma tocca due moduli; dopo = più sicuro | Dopo aver stabilizzato `app_desktop.py` (fase 6.2 come previsto), un commit dedicato |
| 6.4 | **`gui/wizard_percorso.py` vs `crea_nuovo_progetto_dialog`**: fondere o tenere separati? | Fondare = una sola copia; tenere = meno rischio ora | Valutare alla vigilia della 3.3, leggendo entrambi |
| 6.5 | **Interfaccia finestra ↔ pagine**: metodi pubblici o segnali Qt? | Metodi pubblici = semplice, poca modifica; segnali = più pulito | Metodi pubblici ora (coerente con il piano mappa, domanda 6.7.4); segnali eventualmente dopo |
| 6.6 | ~~**`STILI_TRASPORTI` è usato anche dalla mappa?**~~ | **RISOLTA (2026-10-03):** la ricerca su tutto il progetto mostra che `STILI_TRASPORTI` (e le sue chiavi `color`/`dashArray`) compare **solo** in `app_desktop.py` e **solo come definizione** | **Codice morto**: rimuoverlo in 1.1; `gui/costanti_ui.py` (modulo costanti) **potrebbe non servire più** |
| 6.7 | **Effetto collaterale all'import (server Flask)**: spostare dentro `main`? | Spostare = più pulito ma può cambiare l'ordine di avvio; lasciare = invariato | Non toccare in questo refactor; intervento separato |
| 6.8 | **Test automatici**: script manuali su DB temporaneo o `pytest` (nuova dipendenza)? | `pytest` = meglio ma serve approvazione | Script manuali ora (come nel piano mappa) |

## 7. Legame con i principi fondativi

| Principio (`FIRST_PRINCIPLES.md`) | Come guida il refactor |
|---|---|
| **8** — Il viaggio è l'entità centrale | La finestra principale deve **orchestrare**, non contenere tutta la logica: separare pagine e servizi rende esplicito dove vive ogni informazione del viaggio. |
| **9** — La connessione è utile ma non obbligatoria | Le funzioni di servizio estratte (audit, tappe, trasferimenti) devono restare funzionanti **offline**: nessuna dipendenza di rete introdotta durante lo spostamento. |
| **13** — Non un semplice pianificatore GPX | Un `app_desktop.py` snello e modulare è la base perché l'ecosistema possa **crescere** (diario, sito, condivisione) senza toccare un file da 2300 righe. |

---

*Documento di sola analisi. Nessun file di codice è stato modificato. Per approfondire una fase, rileggere il blocco di codice interessato prima di agire (i confini delle righe possono variare dopo ogni sotto-fase).*

