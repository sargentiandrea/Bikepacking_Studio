# Piano di refactor — `gui/mappa.py`

Documento di **sola analisi**: nessun file di codice è stato modificato.
Data analisi: 2026-10-03. File analizzato: `gui/mappa.py` (2379 righe, 9 classi, 87 funzioni).

## 0. Cosa è stato letto e cosa no (onestà sui limiti)

| Fonte | Esito |
|---|---|
| `gui/mappa.py` | Letto per intero in modo mirato: elenco completo di classi/funzioni, e lettura integrale di `MappaWidget`, dei 4 worker, del salvataggio, della sincronizzazione, dei flussi nomi/superfici/altimetria. **Non letto riga per riga**: la costruzione grafica in `PannelloPianificazioneWidget.__init__` (circa righe 215-462) e alcuni metodi di sola grafica (righe ~965-1180). Per la proposta bastano nomi, firme e posizione. |
| `REPORT/FIRST_PRINCIPLES.md` | Letto. Non parla di struttura del codice, ma due principi guidano il refactor: **9** (offline: i dati locali devono continuare a funzionare) e **13** (non un semplice pianificatore GPX: la mappa deve poter crescere). |
| `REPORT/PIANO_PRECALCOLO.md` | Letto per ricerca: **non contiene una sezione sul refactor** di `mappa.py`. Cita solo che il salvataggio mappa e la lettura delle geometrie semplificate passano da `gui/mappa.py`. |
| Test automatici | Cercati (`test*.py`): **non ce ne sono**. Ogni fase va quindi verificata a mano e con script di prova (vedi §3). |
| Proiezione globo | **Non è in `mappa.py`**: sta nel JavaScript dei template (`templates/`, `static/`). Quindi non rientra in questo refactor. |

## 1. Inventario

### 1.1 Classi

| Classe | Righe (circa) | Cosa fa (in parole semplici) | Chi la usa |
|---|---|---|---|
| `BarraSuperfici` | 39-80 (42) | Disegna la barra colorata con la ripartizione di asfalto/sterrato ecc. | Solo il pannello pianificatore |
| `MapManagerDialog` | 81-173 (93) | Finestra "Gestisci mappe offline": elenco mappe, download con barra di avanzamento. Usa `MapManagerService` e `DownloadWorker` (già in `service/`). | Solo `MappaWidget.open_map_manager` |
| `PannelloPianificazioneWidget` | 174-1404 (**1231**) | Pannello fluttuante sopra la mappa: partenza/destinazione/punti di passaggio, anteprima rotta, salvataggio tappa, elenco tappe, dettagli tecnici, nomi luoghi, superfici, altimetria. | Solo `MappaWidget` (lo crea in `setup_ui`) |
| `MappaWidget` | 1405-1872 (468) | Pagina principale: barra pulsanti, vista web MapLibre, cache per progetto, ricarica mappa, lettura click dalla mappa. | `app_desktop.py` riga 631 (`MappaWidget(self)`), **unico import esterno** |
| `WorkerAnalisiSuperficiOffline` | 1884-1916 | Thread: calcola le superfici da mappe locali (`service/superfici_service`). | Pannello |
| `WorkerNomiLuoghi` | 1917-1950 | Thread: trova il nome del luogo da coordinate (`service/geocodifica_offline_service`). | Pannello |
| `WorkerAltimetria` | 1951-1998 | Thread: legge i GPX per quota massima/minima. | Pannello |
| `PianificazionePercorsoWorker` | 1999-2100 | Thread: geocodifica + chiamata BRouter + statistiche rotta. | Pannello |
| `WorkerCaricamentoMappa` | 2102-2379 (278) | Thread: legge tappe, geometrie, nomi luoghi e trasferimenti dal DB/GPX e costruisce il GeoJSON; lo invia a Flask. | `MappaWidget.rigenera_mappa` |

### 1.2 Funzioni — `PannelloPianificazioneWidget` (38 metodi)

| Gruppo | Metodi | Cosa fanno | Chi li chiama |
|---|---|---|---|
| Costruzione | `__init__` (~290 righe di grafica e stato), `showEvent`, `_adatta_altezza_al_contenuto` | Crea tutti i campi e i pulsanti; adatta l'altezza | Qt / `MappaWidget` |
| Form punti | `_aggiungi_punto_passaggio`, `_rimuovi_punto_passaggio`, `_rinumera_punti_passaggio`, `_etichetta_punto`, `_aggiungi_waypoint_da_coordinate`, `_prepara_modifica_tappa` | Gestione dei punti di passaggio; gli ultimi due sono chiamati **da `MappaWidget`** quando l'utente clicca/trascina sulla mappa | Pulsanti del pannello e `MappaWidget._leggi_interazioni_mappa` |
| Rotta | `_firma_pianificazione`, `_valida_pianificazione`, `_avvia_worker_rotta`, `_completamento_worker_pianificazione`, `_worker_pianificazione_terminato`, `_ricalcola_anteprima`, `_anteprima_rotta_completata`, `_aggiorna_dettagli_rotta` | Valida il form, lancia `PianificazionePercorsoWorker`, mostra l'anteprima | Pulsanti e catena di callback interna |
| Salvataggio | `_gestisci_salvataggio_percorso`, `_salvataggio_percorso_completato` (~200 righe) | Scrive il GPX, inserisce/aggiorna `tappe` in SQLite, lancia `precalcola_tappa`, cancella il GPX precedente, aggiorna audit/allarmi/dashboard e mappa | Pulsante "Salva Percorso" |
| Sincronizzazione | `sincronizza_stato_percorso` (~145 righe) | Quando cambia progetto: svuota il pannello, invalida i token, ferma i worker, legge le tappe e precompila il form | **`MappaWidget.showEvent`** (via `QTimer`) |
| Nomi luoghi | `_avvia_risoluzione_nomi_luoghi`, `_avvia_worker_nomi_luoghi`, `_ripulisci_worker_nomi`, `_fine_risoluzione_nomi_luoghi` | Ciclo di vita del worker nomi + applicazione del risultato ai campi | `sincronizza_stato_percorso` |
| Superfici | `_avvia_analisi_superfici_offline`, `_avvia_worker_superfici`, `_ripulisci_worker_superfici`, `_fine_analisi_superfici_offline`, `_popola_legenda_superfici` | Idem per le superfici + legenda | `sincronizza_stato_percorso` |
| Altimetria | `_avvia_analisi_altimetria`, `_avvia_worker_altimetria`, `_ripulisci_worker_altimetria`, `_fine_analisi_altimetria` | Idem per le quote | `sincronizza_stato_percorso` |
| Elenco tappe | `_toggle_elenco_tappe_intermedie`, `_costruisci_riga_tappa_intermedia`, `_popola_tappe_intermedie`, `_aggiorna_testo_tappe_intermedie`, `_evidenzia_tappa_su_mappa` | Elenco consultabile delle tappe intermedie; il click evidenzia la tappa sulla mappa | Pannello |

### 1.3 Funzioni — `MappaWidget` (23 metodi)

| Gruppo | Metodi | Cosa fanno |
|---|---|---|
| Costruzione/UI | `__init__`, `setup_ui`, `toggle_pannello`, `resizeEvent`, `hideEvent`, `showEvent` | Barra pulsanti, vista web, pannello fluttuante. `showEvent` contiene anche la logica "cache valida o ricarico?" |
| Browser e permessi | `apri_mappa_nel_browser`, `_gestisci_permessi_gps`, `_pagina_mappa_caricata`, `_ridimensiona_mappa`, `_imposta_pagina_sospesa` | Interazione con `QWebEngineView` |
| Caricamento e cache | `rigenera_mappa`, `_firma_dati_mappa` (query SQL + hash), `_ripulisci_mappa_worker`, `_fine_caricamento_asincrono`, `_mostra_cache_progetto`, `reload_map` | Token anti-risultati-vecchi, cache in memoria per progetto, iniezione GeoJSON nel browser |
| Interazione mappa | `attiva_modalita_interazione`, `_leggi_interazioni_mappa` | Polling HTTP (300 ms) degli eventi click/drag dal server Flask |
| Ponte verso il pannello | `mostra_anteprima_percorso`, `cancella_anteprima_percorso`, `evidenzia_tappa` | JavaScript verso la mappa, chiamati dal pannello |
| Dialogo | `open_map_manager` | Apre `MapManagerDialog` e poi ricarica |

### 1.4 Altre funzioni

| Funzione | Cosa fa | Chiamata da |
|---|---|---|
| `_distanza_haversine_km` (globale) | Distanza in linea d'aria | Solo `_salvataggio_percorso_completato`. **Duplicato** (già noto: priorità 4 della lista architetturale, da portare in `service/geo_utils.py`) |
| `BarraSuperfici`: `__init__`, `imposta_superfici`, `paintEvent` | Disegno barra | Pannello |
| `MapManagerDialog`: `__init__`, `setup_ui`, `refresh_catalog`, `on_item_selected`, `start_download`, `on_download_finished` | Catalogo e download mappe | Qt |
| Worker: `request_stop`, `run`, `__init__`; `PianificazionePercorsoWorker._geocodifica`, `_profilo_brouter` | Logica dei thread | Qt / pannello |

### 1.5 Responsabilità presenti nel file

| # | Responsabilità | Dove |
|---|---|---|
| 1 | Vista MapLibre nel `QWebEngineView` (browser, GPS, resize, sospensione) | `MappaWidget` |
| 2 | Cache per progetto e firma dati | `MappaWidget` |
| 3 | Costruzione GeoJSON dal DB e dai GPX (con SQL e parsing GPX) | `WorkerCaricamentoMappa` |
| 4 | Polling interazioni mappa (click/drag) | `MappaWidget` |
| 5 | Form di pianificazione e anteprima rotta | Pannello + `PianificazionePercorsoWorker` |
| 6 | **Persistenza** della tappa pianificata (GPX + SQLite + precalcolo + pulizia) | Pannello (`_salvataggio_percorso_completato`) |
| 7 | Sincronizzazione del pannello con il progetto attivo | Pannello |
| 8 | Nomi luoghi / superfici / altimetria (3 cicli di vita di worker quasi identici) | Pannello + 3 worker |
| 9 | Gestione mappe offline (dialogo) | `MapManagerDialog` |
| 10 | Widget di disegno (barra superfici) | `BarraSuperfici` |

### 1.6 Problemi strutturali osservati (fatti, non opinioni)

1. **Il pannello è l'82% delle classi di UI** (1231 righe su 1500 circa) e mescola grafica, rete, database e scrittura file.
2. **Il salvataggio tappa è logica di dominio nella GUI**: scrive su `tappe`, crea GPX, chiama `precalcola_tappa`, poi richiama `esegui_audit_automatico`, `aggiorna_tabella_allarmi`, `page_dashboard.aggiorna_tabella_tappe` della finestra principale.
3. **Stesso schema copiato 3 volte** (superfici, nomi, altimetria): `_avvia_*`, `_avvia_worker_*`, `_ripulisci_*`, `_fine_*`, più coppia "token + richiesta in sospeso + lista worker attivi". Un bug corretto in uno (es. riferimento a thread già distrutto) va ricordato in tutti e tre.
4. **Accoppiamento a doppio senso**: `MappaWidget` accede a campi interni del pannello (`lbl_stato_superfici`, `btn_chiudi_pannello`, metodi con underscore); il pannello accede a `mappa_widget.parent_app`, `rigenera_mappa`, `mostra_anteprima_percorso`. Non c'è un'interfaccia.
5. **SQL dentro i widget e dentro un `QThread`**: `_firma_dati_mappa`, `sincronizza_stato_percorso`, `_prepara_modifica_tappa`, `WorkerCaricamentoMappa.run`.
6. **Import locali e ripetuti** (`from service.config import DB_NAME` dentro metodi, `import json` dentro un metodo che già lo importa in cima).
7. **Dipendenza dal server Flask hardcoded** (`http://127.0.0.1:8080`) in `MappaWidget` e nel worker.
8. **Comportamento da preservare (non è un bug)**: in `_leggi_interazioni_mappa` il `self._poll_interazioni_timer.stop()` sta **dentro** il ciclo di proposito. Il JavaScript (`inviaInterazioneMappa` in `templates/map_view.html`) azzera la modalità mappa dopo aver inviato un solo evento, quindi dopo averlo gestito il polling non serve più; `attiva_modalita_interazione` lo riavvia. Verificato il 2026-10-03: spostare `stop()` fuori dal ciclo fermerebbe il timer prima del click dell'utente. Nel refactor questa regola ("un evento, poi stop; nessun evento, il timer continua") va mantenuta e scritta nel codice spostato.
9. **Nessun test automatico**.

## 2. Proposta di divisione

Principio: **prima spostare codice che non dipende dall'interfaccia**, poi la grafica. Il file `gui/mappa.py` resta il punto d'ingresso (`from gui.mappa import MappaWidget` continua a funzionare), perché `app_desktop.py` è in refactor a sua volta.

### 2.1 Mappa dei moduli

| Modulo | Contiene | Usato da | Dipendenze |
|---|---|---|---|
| `service/mappa_dati_service.py` **(nuovo, senza Qt)** | Logica di `WorkerCaricamentoMappa.run`: `costruisci_geojson_progetto(id, db)`; `firma_dati_mappa(id, db)` (oggi `_firma_dati_mappa`); ricerca nome luogo più vicino | `gui/mappa_worker.py`, `gui/mappa.py` | `sqlite3`, `gpxpy`, `geometria_service`, `gpx_paths`, `config` |
| `service/salvataggio_tappa_service.py` **(nuovo, senza Qt)** | Logica di `_salvataggio_percorso_completato`: scrive GPX, insert/update `tappe`, precalcolo, pulizia GPX precedente. Restituisce un esito (ok / errore / avviso precalcolo) | Pannello | `sqlite3`, `gpxpy`, `precalcolo_service`, `gpx_paths`, `geo_utils` |
| `service/geo_utils.py` **(nuovo, già pianificato)** | `calcola_distanza_haversine` unica (oggi 4 copie: `app_desktop.py`, `gui/dashboard.py`, `service/audit_service.py`, `gui/mappa.py`) | Tutti i precedenti | Solo `math` |
| `gui/mappa_worker.py` | I 5 `QThread`: `WorkerCaricamentoMappa` (ora solo guscio che chiama il servizio e invia a Flask), `WorkerAnalisiSuperficiOffline`, `WorkerNomiLuoghi`, `WorkerAltimetria`, `PianificazionePercorsoWorker` | Mappa e pannello | `PySide6.QtCore`, servizi |
| `gui/mappa_cache.py` | Cache per progetto: `CacheMappaProgetto` (dizionario `{id: {firma, geojson}}`, "è valida?", "salva", "invalida") — **senza Qt** | `MappaWidget` | `service/mappa_dati_service` |
| `gui/mappa_worker_manager.py` | Classe generica `GestoreWorkerSingolo` che incapsula token + richiesta in sospeso + lista worker attivi + pulizia (sostituisce le 3 copie) | Pannello | `PySide6.QtCore` |
| `gui/mappa_widget_barra_superfici.py` → meglio `gui/mappa_barra_superfici.py` | `BarraSuperfici` | Pannello | `PySide6.QtGui` |
| `gui/mappa_dialogo_offline.py` | `MapManagerDialog` | `MappaWidget` | `service/map_manager_service` |
| `gui/mappa_pianificatore.py` | `PannelloPianificazioneWidget` ridotto: form, anteprima, avvio worker rotta, elenco tappe | `MappaWidget` | worker, servizio salvataggio, gestore worker |
| `gui/mappa_waypoint.py` | Metodi del form punti (`_aggiungi_punto_passaggio`, `_rimuovi...`, `_rinumera...`, `_etichetta_punto`, `_aggiungi_waypoint_da_coordinate`, `_prepara_modifica_tappa`) come **mixin o classe di supporto** | Pannello | `PySide6.QtWidgets` |
| `gui/mappa_dettagli.py` (nomi, superfici, altimetria) | Parte "pannello informativo": `_popola_legenda_superfici`, `_aggiorna_dettagli_rotta`, risultati di nomi/superfici/altimetria applicati ai campi, tappe intermedie | Pannello | `mappa_barra_superfici`, gestore worker |
| `gui/mappa.py` | Solo `MappaWidget` (vista web, toolbar, ponte JS, polling) + re-export dei nomi pubblici | `app_desktop.py` | Tutti i moduli sopra |

**Nota sui nomi proposti dall'utente** (`mappa_superfici`, `mappa_nomi`, `mappa_altimetria`): sono stati **riuniti** in `gui/mappa_dettagli.py` + `GestoreWorkerSingolo`, perché i tre flussi sono lo stesso schema con un worker diverso; tre file quasi identici riproporrebbero la duplicazione del punto 1.6.3. Se si preferisce un file per tema, è fattibile dopo l'introduzione del gestore generico (sarebbero file molto piccoli).

### 2.2 Struttura finale

```
gui/
  mappa.py                  → MappaWidget (+ re-export)
  mappa_pianificatore.py    → PannelloPianificazioneWidget
  mappa_waypoint.py         → gestione punti di passaggio
  mappa_dettagli.py         → nomi / superfici / altimetria / tappe intermedie
  mappa_worker.py           → 5 QThread
  mappa_worker_manager.py   → GestoreWorkerSingolo (generico)
  mappa_cache.py            → cache per progetto (senza Qt)
  mappa_barra_superfici.py  → BarraSuperfici
  mappa_dialogo_offline.py  → MapManagerDialog
service/
  mappa_dati_service.py         → GeoJSON + firma (senza Qt)
  salvataggio_tappa_service.py  → persistenza tappa (senza Qt)
  geo_utils.py                  → haversine unica
```

Effetto atteso (stima da righe attuali): `gui/mappa.py` da 2379 a ~500 righe; il pannello da 1231 a ~600 (di cui ~290 di sola grafica); nessun file oltre ~600 righe.

### 2.3 Regole di dipendenza da rispettare

- `service/*` **non importa mai** `PySide6` né `gui/`. Questo rende i servizi riutilizzabili da web/iOS/Android (obiettivo a lungo termine) e testabili senza finestra.
- `gui/mappa_worker.py` importa solo servizi; non conosce i widget.
- Pannello e `MappaWidget` comunicano con **segnali Qt** o metodi pubblici documentati, non con campi privati (`lbl_stato_superfici`, `btn_chiudi_pannello`, ecc.).
- `gui/mappa.py` non importa `app_desktop.py` (oggi usa `parent_app` per `current_progetto_id`; vedi domanda 4.3).

## 3. Piano di implementazione a fasi

Regola per ogni fase: **un solo obiettivo**, backup, sintassi + Pylance, prova su DB temporaneo, poi `analisi_profonda.py`. Dopo ogni fase l'app deve avviarsi e la pagina Mappa deve caricare un progetto.

### Fase 1 — Spostare il codice senza interfaccia grafica (rischio basso)

| Passo | Cosa | File coinvolti | Rischio | Beneficio |
|---|---|---|---|---|
| 1.1 | Creare `service/geo_utils.py` con l'haversine unica; far importare `gui/mappa.py` (e, in passi separati, le altre 3 copie) | `service/geo_utils.py`, `gui/mappa.py` | **Basso**: funzione pura, 1 solo chiamante in `mappa.py` | Chiude la priorità 4 della lista architetturale |
| 1.2 | Spostare i 4 worker semplici (`WorkerAnalisiSuperficiOffline`, `WorkerNomiLuoghi`, `WorkerAltimetria`, `PianificazionePercorsoWorker`) in `gui/mappa_worker.py`; re-export in `mappa.py` | `gui/mappa_worker.py`, `gui/mappa.py` | **Basso**: classi quasi autonome, copia esatta | -300 righe, nessun cambio di comportamento |
| 1.3 | Spostare `BarraSuperfici` e `MapManagerDialog` nei propri file | 2 file nuovi, `gui/mappa.py` | **Basso** | -135 righe |

Verifica: avvio app, apertura pagina Mappa, apertura "Gestisci mappe offline", calcolo anteprima rotta (richiede BRouter attivo), visualizzazione barra superfici.

### Fase 2 — Estrarre la logica dai widget (rischio medio)

| Passo | Cosa | File coinvolti | Rischio | Beneficio |
|---|---|---|---|---|
| 2.1 | Estrarre `WorkerCaricamentoMappa.run` e `_firma_dati_mappa` in `service/mappa_dati_service.py`; il worker diventa un guscio | `service/mappa_dati_service.py`, `gui/mappa_worker.py`, `gui/mappa.py` | **Medio**: è il codice più delicato (percorso GPX, geometrie precalcolate, bbox, token). **Prova obbligatoria**: confrontare il GeoJSON prodotto prima e dopo su un progetto reale (stesso `repr`/hash) | Funzione testabile senza finestra; i dati mappa diventano riusabili da web/mobile |
| 2.2 | Estrarre `_salvataggio_percorso_completato` in `service/salvataggio_tappa_service.py`; la GUI mostra solo i messaggi e richiama audit/allarmi/dashboard | `service/salvataggio_tappa_service.py`, `gui/mappa.py` (pannello) | **Medio-alto**: scrive su DB e file; coinvolge `precalcola_tappa` e la cancellazione del GPX precedente. Prova su DB temporaneo con tappa nuova, aggiornata e con precalcolo in errore | La regola "non cancellare il vecchio GPX se il precalcolo fallisce" diventa verificabile |
| 2.3 | Estrarre `_cache_per_progetto` in `gui/mappa_cache.py` (senza Qt) | `gui/mappa_cache.py`, `gui/mappa.py` | **Basso-medio** | Logica "cache valida?" di `showEvent` isolata e testabile |

### Fase 3 — Scomporre il pannello e il widget (rischio medio-alto, dopo le fasi 1-2)

| Passo | Cosa | File coinvolti | Rischio | Beneficio |
|---|---|---|---|---|
| 3.1 | Introdurre `GestoreWorkerSingolo` e sostituire i 3 cicli (nomi, superfici, altimetria) **uno alla volta** (prima altimetria, poi nomi, poi superfici) | `gui/mappa_worker_manager.py`, pannello | **Medio**: i token e le richieste in sospeso prevengono crash noti ("Internal C++ object already deleted"); non vanno persi | Un solo punto in cui vive la correzione del ciclo di vita |
| 3.2 | Separare il form dei punti (`mappa_waypoint.py`) e il blocco "dettagli" (`mappa_dettagli.py`) | 2 file nuovi, pannello | **Medio** | Pannello sotto ~600 righe |
| 3.3 | Spostare il pannello ridotto in `gui/mappa_pianificatore.py` | file nuovo, `gui/mappa.py` | **Medio** | `gui/mappa.py` contiene solo `MappaWidget` |
| 3.4 | Sostituire l'accesso diretto ai campi privati con segnali/metodi pubblici (`messaggio_stato`, `chiudi_richiesto`, ecc.) | pannello e `MappaWidget` | **Medio** | Disaccoppiamento tra i due widget |

### Fase 4 (facoltativa) — Rifinitura

Rimuovere gli import locali ridondanti, centralizzare l'URL di Flask in `service/config.py`, valutare di trasformare `gui/mappa.py` in un pacchetto `gui/mappa/`. Rischio basso, beneficio estetico: non urgente.

### Ordine consigliato e criteri di stop

1. Fase 1 intera, poi pausa di uso reale.
2. Fase 2.1 e 2.3, poi 2.2 (la più rischiosa).
3. Fase 3 solo se le fasi precedenti sono stabili.

Fermarsi e tornare al backup se: la mappa non carica, l'anteprima rotta non compare, il salvataggio tappa produce una tappa senza GPX/precalcolo, o compaiono crash sui thread alla chiusura.

## 4. Domande aperte (decisioni richieste)

| # | Questione | Opzioni / trade-off | Mia raccomandazione |
|---|---|---|---|
| 4.1 | **Nomi dei moduli**: file separati per superfici, nomi e altimetria, oppure `mappa_dettagli.py` unico | Separati = rispetta la tua proposta ma 3 file simili; unico = meno duplicazione, file più grande | Unico `mappa_dettagli.py` + gestore generico (§2.1) |
| 4.2 | **Il salvataggio tappa va nel servizio?** | Sì = testabile e riusabile da web/mobile, ma tocca il flusso più delicato; no = file più grandi ma zero rischio sui dati | Sì, in Fase 2.2, con DB temporaneo e backup |
| 4.3 | **`parent_app`**: oggi la mappa legge `current_progetto_id` dalla finestra principale e richiama `esegui_audit_automatico`, `aggiorna_tabella_allarmi`, `page_dashboard...` | Mantenere `parent_app` (semplice) oppure introdurre segnali (`tappa_salvata`, `progetto_richiesto`) che `app_desktop.py` ascolta | Mantenere `parent_app` ora; segnali dopo il refactor di `app_desktop.py` (altrimenti si rifanno due refactor intrecciati) |
| 4.4 | ~~Bug timer~~ **Chiusa**: non è un bug (vedi §1.6 punto 8). Il timer si ferma dopo il primo evento perché la modalità mappa è "usa e getta" | — | Nessun intervento prima del refactor; durante lo spostamento di `_leggi_interazioni_mappa` (Fase 3.4) conservare il comportamento e il commento esplicativo già presente nel codice |
| 4.5 | **Compatibilità `from gui.mappa import ...`**: oggi solo `MappaWidget` è importato fuori | Mantenere re-export di tutti i nomi pubblici oppure solo `MappaWidget` | Solo `MappaWidget` + i worker spostati (per sicurezza durante la transizione) |
| 4.6 | **Test automatici**: non ne esistono | Introdurre una piccola cartella `tests/` (nuova dipendenza `pytest`? richiede permesso) oppure script di verifica manuali su DB temporaneo come finora | Script manuali (nessuna nuova dipendenza); valutare `pytest` solo con tuo permesso |
| 4.4b | **`WorkerCaricamentoMappa` invia i dati a Flask** (`requests.post`) | Tenerlo nel worker (comportamento attuale) o spostarlo nel servizio | Lasciarlo nel guscio del worker: la rete resta separata dal calcolo |
| 4.7 | **Informazioni mancanti**: la parte di grafica del pannello (righe ~215-462 e ~965-1180) non è stata letta riga per riga | Prima della Fase 3 occorre rileggerla per decidere i confini esatti di `mappa_waypoint.py` e `mappa_dettagli.py` | Rimandare la definizione finale dei confini alla vigilia della Fase 3 |

## 5. Rischi trasversali

| Rischio | Perché | Mitigazione |
|---|---|---|
| Rottura silenziosa dei thread | I worker usano token e liste di sopravvivenza per evitare crash di Qt | Spostare le classi **senza modificarle** (Fase 1); sostituire i cicli uno alla volta (Fase 3.1) |
| Perdita di dati nel salvataggio | Scrive GPX e DB insieme | Backup SQLite prima di ogni prova su dati reali; prove su DB temporaneo |
| Regressione del percorso GPX | I GPX ora stanno in `gpx/{id_progetto}/` e `gpx_paths.py` è nuovo e non ancora committato | Eseguire il refactor **dopo** il commit delle modifiche GPX attualmente in sospeso, per avere un punto di ritorno pulito |
| Mancanza di test | Non esistono | Confronto prima/dopo del GeoJSON (hash) e prove manuali per ogni fase |
| Conflitto con il refactor di `app_desktop.py` | Entrambi toccano `parent_app` | Non cambiare l'interfaccia verso `app_desktop.py` finché non è stabilizzato |


---

## 6. Fase 3 — dettaglio (analisi del 2026-10-03)

> Stato: **solo analisi, nessun codice modificato.** Righe riferite a `gui/mappa.py` dopo i commit `6ba8db0`, `2f555b1`, `5f01818`, `9cf2d74` (1970 righe; il pannello occupa le righe 181-1277, circa 1097).

### 6.0 Cosa è cambiato rispetto al piano originale

| Punto del piano | Stato reale |
|---|---|
| Fase 1.1 `geo_utils.py` | **Fatto** |
| Fase 2.1 / 2.2 (servizi dati e salvataggio) | **Fatto**, in `service/mappa_dati_service.py` e `service/salvataggio_tappa_service.py` |
| Fase 1.2 (spostare i 4 worker in `gui/mappa_worker.py`) | **Non fatta** |
| Fase 1.3 (`BarraSuperfici`, `MapManagerDialog` in file propri) | **Non fatta** |
| Fase 2.3 (cache in `gui/mappa_cache.py`) | **Non fatta** |

Il pannello non è più "da ~1230 righe": dopo la Fase 2 ha 38 metodi e circa 1097 righe, di cui **287 sono solo costruzione grafica** (`__init__`, righe 183-469).

### 6.1 Metodo per metodo

Legenda "tocca": **W** = widget, **DB** = SQLite, **F** = file, **T** = thread/worker, **M** = `MappaWidget`/mappa, **—** = niente.

| # | Metodo | Righe | Cosa fa | Tocca | Chiamato da → chiama |
|---|---|---|---|---|---|
| 1 | `__init__` | 183-469 | Crea stato (token, worker, punti), stile, tutti i campi e pulsanti | W | Qt → `_adatta_altezza_al_contenuto` |
| 2 | `_firma_pianificazione` | 470 | Chiave "l'anteprima corrisponde ai campi?" | W, M (`parent_app`) | rotta, salvataggio |
| 3 | `_valida_pianificazione` | 481 | Controlla progetto e campi; mostra avviso | W, M | salvataggio, `_avvia_worker_rotta` |
| 4 | `_avvia_worker_rotta` | 505 | Lancia `PianificazionePercorsoWorker` | W, T | `_ricalcola_anteprima`, salvataggio |
| 5 | `_completamento_worker_pianificazione` | 532 | Inoltra l'esito al callback corrente | — | worker → callback |
| 6 | `_worker_pianificazione_terminato` | 542 | Riabilita il pulsante salva | W | `finished` del worker |
| 7 | `_ricalcola_anteprima` | 546 | Anteprima senza scrivere nel DB | T | `_aggiungi_waypoint_da_coordinate` |
| 8 | `_anteprima_rotta_completata` | 554 | Mostra l'anteprima sulla mappa | W, M | worker |
| 9 | `_aggiungi_waypoint_da_coordinate` | 568 | Inserisce un punto ricevuto dalla mappa | W | **`MappaWidget._leggi_interazioni_mappa`**, `_prepara_modifica_tappa` |
| 10 | `_prepara_modifica_tappa` | 577 | Carica gli estremi della tappa trascinata (usa `carica_coordinate_tappa`) | W, DB/F (via servizio), M | **`MappaWidget._leggi_interazioni_mappa`** |
| 11 | `sincronizza_stato_percorso` | 596-730 | Al cambio progetto svuota il pannello, invalida token, ferma worker, legge le tappe, precompila | W, DB (via servizio), T, M | **`MappaWidget.showEvent`** (QTimer) |
| 12-15 | `_avvia_risoluzione_nomi_luoghi`, `_avvia_worker_nomi_luoghi`, `_ripulisci_worker_nomi`, `_fine_risoluzione_nomi_luoghi` | 731-801 | Ciclo di vita del worker nomi + applicazione ai campi | T, W | `sincronizza_stato_percorso` |
| 16-19 | `_avvia_analisi_superfici_offline`, `_avvia_worker_superfici`, `_ripulisci_worker_superfici`, `_fine_analisi_superfici_offline` | 802-879 | Idem per le superfici | T, W | `sincronizza_stato_percorso` |
| 20-23 | `_avvia_analisi_altimetria`, `_avvia_worker_altimetria`, `_ripulisci_worker_altimetria`, `_fine_analisi_altimetria` | 880-939 | Idem per le quote | T, W | `sincronizza_stato_percorso` |
| 24 | `showEvent` | 940 | Adatta l'altezza dopo la visualizzazione | W | Qt |
| 25 | `_adatta_altezza_al_contenuto` | 944 | Calcola l'altezza del pannello | W | ovunque, **anche `MappaWidget`** (righe 1478, 1522) |
| 26-28 | `_aggiungi_punto_passaggio`, `_rimuovi_punto_passaggio`, `_rinumera_punti_passaggio` | 978-1024 | Form dei punti di passaggio | W | pulsanti, #9, #10, #11 |
| 29 | `_toggle_elenco_tappe_intermedie` | 1025 | Apre/chiude l'elenco | W | pulsante |
| 30-32 | `_costruisci_riga_tappa_intermedia`, `_popola_tappe_intermedie`, `_aggiorna_testo_tappe_intermedie` | 1033-1083 | Elenco consultabile delle tappe | W | #11, #15 |
| 33 | `_popola_legenda_superfici` | 1084 | Griglia legenda | W | #8, #11, #16, #34 |
| 34 | `_evidenzia_tappa_su_mappa` | 1102 | Chiede alla mappa di evidenziare una tappa | M | pulsanti, #11, #30 |
| 35 | `_aggiorna_dettagli_rotta` | 1107 | Barra superfici, legenda, KPI | W | #8, `_salvataggio_percorso_completato` |
| 36 | `_etichetta_punto` (statico) | 1150 | Indice → A, B, ..., AA | — (funzione pura) | #26 |
| 37 | `_gestisci_salvataggio_percorso` | 1159 | Salva l'anteprima o calcola la rotta | W, T | pulsante "Salva" |
| 38 | `_salvataggio_percorso_completato` | 1180-1277 | Validazioni, chiama `salva_tappa_pianificata`, poi aggiorna audit/allarmi/dashboard/mappa e mostra i messaggi | W, M, `parent_app` | worker/#37 |

### 6.2 Responsabilità del pannello (fatti verificati)

| Responsabilità | Metodi | Nota |
|---|---|---|
| A. Grafica statica e dimensioni | #1, #24, #25 | 287 righe di `__init__` |
| B. Form punti di passaggio | #9, #26-28, #36 | |
| C. Modifica tratta (partenza dalla mappa) | #10 | Il **trascinamento vero e proprio non è nel pannello**: è in JavaScript (`templates/map_view.html`) e nel polling di `MappaWidget._leggi_interazioni_mappa`. Il pannello riceve solo l'esito (#9, #10) |
| D. Calcolo rotta (BRouter) | #2-8 | La chiamata di rete sta nel worker `PianificazionePercorsoWorker`, non nel pannello |
| E. Salvataggio tappa | #37, #38 | La parte dati è già nel servizio; resta la parte GUI |
| F. Sincronizzazione con il progetto attivo | #11 | Contiene la logica più intrecciata |
| G. Tre cicli di worker quasi identici | #12-23 | ~210 righe copiate 3 volte |
| H. Elenco tappe intermedie | #29-32, #34 | |
| I. Dettagli rotta (barra superfici, legenda, KPI) | #33, #35 | |

**Cosa NON c'è nel pannello** (importante per le divisioni proposte dall'utente): nessuna chiamata a Flask (`requests`), nessun `runJavaScript`, nessun accesso diretto a BRouter. Tutto questo vive in `MappaWidget` e nei worker. Quindi **non servono** moduli "comunicazione con Flask" o "comunicazione con JavaScript" per il pannello, e `mappa_trascinamento.py` sarebbe un modulo quasi vuoto lato pannello (vedi domanda 6.5.1).

### 6.3 Accoppiamenti da conoscere prima di toccare

| Da → a | Cosa | Perché conta |
|---|---|---|
| `MappaWidget` → pannello | `btn_chiudi_pannello`, `lbl_stato_superfici`, `_aggiungi_waypoint_da_coordinate`, `_prepara_modifica_tappa`, `_adatta_altezza_al_contenuto`, `sincronizza_stato_percorso`, `show/hide/raise_` | Sono **l'interfaccia di fatto**: se si spostano o rinominano, il polling e `showEvent` si rompono |
| Pannello → `MappaWidget` | `parent_app` (progetto, audit, allarmi, dashboard), `mostra_anteprima_percorso`, `cancella_anteprima_percorso`, `evidenzia_tappa`, `attiva_modalita_interazione`, `rigenera_mappa` | Letti con `getattr(..., "parent_app")` in 6 punti |
| #11 → tre cicli worker | Incrementa direttamente i token e chiama `request_stop()` sui tre worker | Un gestore generico deve esporre "invalida e ferma" |
| Cicli → stato | 4 campi per ciclo: worker corrente, lista di sopravvivenza, richiesta in sospeso, token | Nei tre cicli la richiesta in sospeso ha tipi diversi (superfici: id progetto; nomi e quote: liste) |

### 6.4 Proposta di divisione (rivista)

**Scelta di struttura:** composizione (classi di supporto che il pannello possiede), **non** ereditarietà multipla/mixin. I mixin spezzerebbero il file ma non l'accoppiamento: tutti i metodi continuerebbero a toccare lo stesso `self`. Il pannello resta il proprietario dei widget.

| Modulo | Contiene | Tocca Qt? | Usato da | Dipende da |
|---|---|---|---|---|
| `gui/mappa_worker_manager.py` | `GestoreWorkerSingolo`: worker corrente, lista di sopravvivenza, richiesta in sospeso, token; metodi `richiedi(dati)`, `invalida()` (token+stop), `e_corrente(token)` | Sì (`QThread`) | pannello (3 istanze) | `PySide6.QtCore` |
| `gui/mappa_dettagli.py` | `PannelloDettagliRotta` (widget): barra superfici, legenda, 4 KPI, messaggio di stato; metodi `imposta_statistiche()`, `azzera()`, `imposta_stato(testo)`, `imposta_altimetria(max,min)`, `imposta_distanza()` | Sì | pannello e (via `imposta_stato`) `MappaWidget` | `BarraSuperfici` |
| `gui/mappa_tappe_intermedie.py` | `ElencoTappeIntermedie` (widget): toggle, scroll, righe; segnale `tappa_selezionata(id)` | Sì | pannello | — |
| `gui/mappa_waypoint.py` | `FormPuntiPassaggio` (widget): lista campi, aggiungi/rimuovi/rinumera, `testi()`, `aggiungi_da_coordinate()`; `etichetta_punto()` come funzione pura | Sì | pannello | — |
| `gui/mappa_pianificatore.py` | `PannelloPianificazioneWidget` ridotto: assemblaggio dei sotto-widget, validazione, rotta, salvataggio (parte GUI), sincronizzazione | Sì | `MappaWidget` | tutti i precedenti, servizi |
| `gui/mappa_worker.py` | I 4 worker (Fase 1.2, ancora da fare) | Sì | pannello | servizi |
| `gui/mappa.py` | `MappaWidget` + re-export | Sì | `app_desktop.py` | tutto |

Stima righe dopo la Fase 3: pannello ~450, dettagli ~160, tappe intermedie ~110, waypoint ~120, gestore ~80. Nessun file oltre ~500.

**Non proposti** (e perché): `mappa_trascinamento.py` (la logica è JS + `MappaWidget`, vedi 6.2.C), `mappa_comunicazione_*` (il pannello non comunica né con Flask né con JS).

### 6.5 Piano a sotto-fasi (dal più semplice)

| Sotto-fase | Cosa | File | Rischio | Beneficio | Come verificare |
|---|---|---|---|---|---|
| **3.0** *(prerequisito)* | Eseguire Fase 1.2/1.3: spostare i 4 worker, `BarraSuperfici`, `MapManagerDialog` in file propri | `gui/mappa_worker.py` e altri 2, `gui/mappa.py` | Basso (copia esatta) | -430 righe; i nuovi moduli potranno importare i worker senza cicli | Import, Pylance, apertura pagina Mappa |
| **3.1** | `etichetta_punto` → funzione pura in `mappa_waypoint.py` (con test su A…Z, AA, AB); poi `ElencoTappeIntermedie` | `gui/mappa_waypoint.py`, `gui/mappa_tappe_intermedie.py` | Basso (solo widget, nessun thread) | Primi ~110 righe fuori, sperimentazione del metodo | Elenco vuoto/pieno, click riga → evidenzia, toggle |
| **3.2** | `FormPuntiPassaggio` (punti di passaggio) | `gui/mappa_waypoint.py` | Medio-basso: `_firma_pianificazione`, `_valida_pianificazione` e `sincronizza_stato_percorso` leggono `punti_passaggio` | -120 righe | Aggiungere/rimuovere punti, firma anteprima, waypoint da mappa |
| **3.3** | `GestoreWorkerSingolo` e sostituzione dei 3 cicli **uno per volta**: altimetria → nomi → superfici (un commit ciascuno) | `gui/mappa_worker_manager.py`, pannello | **Medio-alto**: token e richieste in sospeso prevengono crash noti | -150 righe, una sola copia della logica "ciclo di vita" | Cambio rapido di progetto più volte; chiusura app con worker attivo |
| **3.4** | `PannelloDettagliRotta` (barra, legenda, KPI, stato) | `gui/mappa_dettagli.py`, pannello, `MappaWidget` (usa `lbl_stato_superfici`) | Medio: tocca anche `MappaWidget` (righe 1397, 1439) | -160 righe, ultimo accesso diretto a un campo privato rimosso | Anteprima, salvataggio, modalità mappa on/off |
| **3.5** | Spostare il pannello ridotto in `gui/mappa_pianificatore.py`; sostituire gli accessi privati da `MappaWidget` con metodi pubblici (`aggiungi_waypoint`, `prepara_modifica_tappa`, `imposta_stato`, `adatta_altezza`) | `gui/mappa_pianificatore.py`, `gui/mappa.py` | Medio | `gui/mappa.py` = solo `MappaWidget` | Flusso completo: crea percorso, waypoint, trascinamento, salva |

**Ordine obbligato:** 3.0 → 3.1 → 3.2 → 3.3 → 3.4 → 3.5. Un commit per sotto-fase (3.3: uno per ciclo). Dopo ciascuna, avvio app e prova manuale.

**Criteri di stop (ereditati da §3 e aggiornati):** la pagina Mappa non carica; l'anteprima non compare; un click sulla mappa in modalità waypoint non aggiunge il punto; il trascinamento non apre la modifica; crash alla chiusura o dopo un cambio rapido di progetto ("Internal C++ object already deleted").

### 6.6 Cosa si può e non si può verificare

| Verifica | Possibile? |
|---|---|
| Sintassi, Pylance, import, `git diff --check` | Sì |
| Funzioni pure (`etichetta_punto`) e logica del gestore con thread finti | Sì, senza finestra |
| Widget con `QT_QPA_PLATFORM=offscreen` (creazione, aggiungi/rimuovi punti, popola elenco/legenda) | Sì, ma non copre mouse e rendering reale |
| Flusso con mappa visibile, trascinamento, polling dal browser, crash alla chiusura | **No** da terminale: serve la prova manuale dell'utente |

### 6.7 Domande aperte

| # | Questione | Opzioni / trade-off | Raccomandazione |
|---|---|---|---|
| 6.7.1 | **Modulo `mappa_trascinamento.py`**: nel pannello non c'è logica di trascinamento (è JS + polling in `MappaWidget`) | Non crearlo; oppure estrarre il polling (`attiva_modalita_interazione`, `_leggi_interazioni_mappa`) in un modulo della mappa | Non crearlo ora; valutare l'estrazione del polling in una fase separata sulla parte `MappaWidget` |
| 6.7.2 | **Eseguire prima la 3.0** (Fase 1.2/1.3 mai fatta)? | Sì = più passi ma meno rischi di import circolari; no = nuovi moduli importano ancora da `gui/mappa.py` | Sì |
| 6.7.3 | **Composizione o mixin** | Composizione = interfacce chiare, più lavoro; mixin = meno lavoro, l'accoppiamento resta | Composizione |
| 6.7.4 | **Interfaccia `MappaWidget` ↔ pannello**: metodi pubblici o segnali Qt | Metodi pubblici = semplice; segnali = più pulito ma più modifiche | Metodi pubblici ora, segnali dopo il refactor di `app_desktop.py` (coerente con 4.3) |
| 6.7.5 | **`GestoreWorkerSingolo` accetta anche la "richiesta in sospeso" con tipi diversi** (id progetto vs liste) | Un solo gestore con payload generico, oppure sottoclassi | Un gestore con payload generico |
| 6.7.6 | **Ordine in `_fine_*`**: oggi la richiesta in sospeso viene riavviata **prima** di controllare il token | Preservare esattamente (come il timer, non cambiare comportamento) o correggere dopo | Preservare; eventuale ottimizzazione in un intervento separato |
| 6.7.7 | **Test automatici** (già 4.6) | Script manuali su DB temporaneo, o `pytest` (nuova dipendenza: serve permesso) | Script manuali; per i widget `offscreen` |
| 6.7.8 | **Informazioni mancanti** | Non ho letto riga per riga `__init__` (righe 183-345) né l'inizio di `_valida_pianificazione` fuori da quanto riportato; i confini esatti dei widget (3.1-3.4) vanno confermati alla vigilia di ciascuna sotto-fase | Rileggere il blocco interessato prima di ogni sotto-fase |