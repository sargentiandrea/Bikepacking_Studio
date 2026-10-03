# Analisi del Pianificatore Percorso

Documento di sola analisi: descrive **cosa fa oggi** il pianificatore,
**come lo fa**, **dove ha problemi** rispetto a
`VISIONE_PIANIFICATORE.md`, e **cosa manca**.

Non contiene proposte di soluzione: quelle sono oggetto del Passo 2.

Fonti analizzate:

| File | Righe | Ruolo |
|---|---|---|
| `gui/mappa_pianificatore.py` | 878 | Il pannello di pianificazione (tutto il workflow) |
| `gui/mappa.py` | 504 | Il widget mappa (WebEngine + interazioni) |
| `gui/mappa_worker.py` | 238 | I 4 worker in background |
| `service/punti_service.py` | 142 | Funzioni pure del form (etichette, firma, validazione) |
| `service/salvataggio_tappa_service.py` | ~200 | Scrittura GPX + SQLite + precalcolo |
| `service/geonames_service.py` | 55 | Ricerca luoghi offline |
| `service/map_server.py` | ~380 | API Flask che fa da ponte con la mappa |
| `gui/mappa_dettagli.py` | ~130 | KPI e legenda della rotta |

---

## 1. Cosa fa oggi

### 1.1 Funzionalità presenti

| Funzionalità | Stato | Dove |
|---|---|---|
| Inserire partenza e arrivo come testo | funzionante | `mappa_pianificatore.py` |
| Accettare coordinate come testo (`lat, lon`) | funzionante | `mappa_worker.py:152` |
| Ricerca luogo per nome (GeoNames offline) | funzionante | `geonames_service.py` |
| Punti di passaggio intermedi | funzionante | `_aggiungi_punto_passaggio` |
| Punti di passaggio da click sulla mappa | funzionante | `mappa.py:186` |
| Modifica di una tappa esistente (trascinamento) | funzionante | `prepara_modifica_tappa` |
| Calcolo rotta con BRouter | funzionante | `PianificazionePercorsoWorker` |
| Anteprima della rotta prima di salvare | funzionante | `mostra_anteprima_percorso` |
| Salvataggio GPX + SQLite + precalcolo | funzionante | `salvataggio_tappa_service.py` |
| KPI tecnici della rotta (km, dislivello, pendenza) | funzionante | `mappa_dettagli.py` |
| Ripartizione superfici (asfalto/strada sterrata) | funzionante | `superfici_service.py` |
| Altimetria min/max del percorso | funzionante | `WorkerAltimetria` |
| Geocodifica inversa (coordinate → nome luogo) | funzionante | `WorkerNomiLuoghi` |
| Elenco tappe esistenti (sola lettura) | funzionante | `_popola_tappe_intermedie` |
| Evidenziazione tappa sulla mappa | funzionante | `_evidenzia_tappa_su_mappa` |
| 4 profili di instradamento | funzionante | `combo_profilo` |
| Riconoscimento percorsi vietati alle bici | funzionante | `rileva_strade_vietate_progetto` |

### 1.2 Struttura del codice

La separazione e **buona** e merita nota positiva:

```
gui/mappa_pianificatore.py   <- solo orchestrazione GUI
    |- service/punti_service.py             <- funzioni PURE (testabili senza Qt)
    |- service/salvataggio_tappa_service.py <- scrittura dati, senza Qt
    |- service/geonames_service.py          <- ricerca, senza Qt
    |- gui/mappa_worker.py                  <- 4 QThread

gui/mappa.py                 <- WebEngine + polling Flask
service/map_server.py        <- API: /api/set-gpx-data, /api/map-interactions
```

`punti_service.py` e un esempio di buona separazione: `valida_pianificazione()`,
`firma_pianificazione()`, `etichetta_punto()` sono funzioni pure che non
importano Qt e potrebbero essere testate isolatamente.

La gestione della concorrenza e fatta bene: `GestoreWorkerSingolo`
(`gui/mappa_worker_manager.py`) incapsula token, code e lista di sopravvivenza
per 3 worker, evitando crash e risultati obsoleti.
---

## 2. Come lo fa (flusso utente)

### 2.1 Flusso attuale: creare una tappa

```
1. L'utente apre un percorso dalla Dashboard
                    |
2. Va alla pagina Mappa e clicca "Pianificatore"
                    |
3. Il pannello si apre e si AUTO-COMPILA (se il percorso ha gia tappe)
   - partenza = coordinate inizio prima tappa
   - destinazione = coordinate fine ultima tappa
   - elenco tappe intermedie (sola lettura)
   - avvio in background: nomi luoghi, altimetria, superfici
                    |
4. L'utente compila i campi (o clicca "Posiziona waypoint sulla mappa")
                    |
5. Clicca "Salva Percorso"
                    |
6. Validazione (punti_service.valida_pianificazione)
   - serve un percorso aperto?
   - partenza E destinazione compilate?
   - nessun punto di passaggio a meta?
                    |
7. Se l'anteprima e valida -> salta al passo 9
   Altrimenti -> lancia PianificazionePercorsoWorker
                    |
8. Worker: geocodifica (GeoNames o coordinate) -> chiama BRouter -> traccia
                    |
9. _salvataggio_percorso_completato:
   - scrive GPX su disco
   - inserisce/aggiorna riga in SQLite
   - lancia precalcolo metriche
   - riesegue audit automatico
   - aggiorna tabelle tappe e allarmi
   - rigenera la mappa
                    |
10. MessageBox "Percorso salvato" con i km
```

### 2.2 Come si aggiunge un punto di passaggio

Ci sono **tre modi**, tutti convergenti:

| Modo | Azione | Cosa succede |
|---|---|---|
| Testuale | "+ Aggiungi punto di passaggio" | Apre un campo vuoto con etichetta A, B, C... |
| Da mappa | "Posiziona waypoint sulla mappa" poi click | Riempi il primo campo vuoto con le coordinate |
| Drag | "Modifica tratta trascinando la linea" | Vedi 2.3 |

Dopo l'inserimento scatta **automaticamente** `_ricalcola_anteprima()`:
parte un worker BRouter e l'anteprima sulla mappa si aggiorna.

Punti noti:

- Le etichette sono **A, B, C... Z, AA, AB** (`etichetta_punto`)
- Il primo campo vuoto viene riempito, senza crearne uno nuovo
- Non esiste il concetto di "tappa" nel form: esistono solo "punti"

### 2.3 Come si modifica una tappa

```
1. Utente clicca "Modifica tratta trascinando la linea"
                    |
2. La mappa attiva la modalita "rubberband"
                    |
3. L'utente trascina una tappa esistente verso la nuova strada
                    |
4. _leggi_interazioni_mappa riceve l'evento da Flask
                    |
5. prepara_modifica_tappa():
   - carica le coordinate della tappa da GPX
   - mette il primo punto in partenza e l'ultimo in destinazione
   - cancella tutti i punti di passaggio
   - mette il punto trascinato come waypoint
   - il pulsante diventa "Aggiorna tappa"
                    |
6. Salva -> _salvataggio_percorso_completato con tappa_id valorizzato
   -> salva_tappa_pianificata fa UPDATE invece di INSERT
```

### 2.4 Cosa comunica l'interfaccia

| Momento | Messaggio | Dove |
|---|---|---|
| Attesa utente | "Clicca sulla mappa per posizionare il punto. Esc disattiva" | pannello dettagli |
| Routing in corso | Pulsante "Ricerca e calcolo percorso..." (disabilitato) | pulsante Salva |
---

## 3. Dove sono i problemi (rispetto alla visione)

### 3.1 Il problema di fondo: non esiste il concetto di "contesto"

La visione (cap. 4) chiede che **prima di creare una traccia** l'utente specifichi
cosa sta creando:

| Scelta richiesta dalla visione | Esiste oggi |
|---|---|
| Tappa unica | no |
| Percorso (da suddividere) | no |
| Parte di un viaggio | no |
| Test tecnico | no |

Il pannello oggi ha **un solo pulsante** ("Salva Percorso") e non chiede
mai nulla all'utente. La scelta e implicita ed e sempre la stessa: **la traccia
viene aggiunta in coda al progetto aperto**.

Questo e il divario piu grande fra visione e realta.

### 3.2 Manca la suddivisione in tappe (cap. 5)

La visione chiede: km medi per tappa **e** numero di giorni, con
l'utente che sceglie quale usare, e il caso "550 km su un percorso di 500 km
= tappa unica".

Oggi **non esiste alcun codice di suddivisione automatica**. L'unica
suddivisione esistente e la catena stagionale in `controller_clima.py`, che
lavora su un altro piano (blocchi per clima) e non ha a che fare con il
pianificatore.

L'utente deve creare le tappe una a una, manualmente.

### 3.3 I punti di passaggio non "deviano" la traccia (cap. 6)

La visione descrive 4 comportamenti distinti:

| Caso descritto nella visione | Comportamento oggi |
|---|---|
| Punto gia sulla tappa: non serve crearlo | Assente: viene comunque aggiunto come punto |
| Punto vicino a una tappa: devia la tappa **piu vicina** | Parziale: si puo usare "Modifica tratta", ma non e automatico ne suggerito |
| Punto che stravolge il percorso: ricalcola **tutto** | Si: BRouter ricalcola da partenza a destinazione |
| Comportamento fluido (Komoot) | Ogni aggiunta ricalcola tutto da capo |

Il caso piu vicino al comportamento desiderato e il terzo (ricalcolo
totale), ma gli altri tre non ci sono. In particolare **non esiste alcuna
rilevazione** di "questo punto e gia sulla tua rotta": il sistema aggiunge
sempre un punto e ricalcola, anche se il punto e a 200 metri dalla traccia
esistente.

### 3.4 Il pannello principale e troppo pieno (cap. 2.3)

La visione chiede esplicitamente che il pannello opzioni (profilo bici,
velocita media, cosa visualizzare) sia **separato** dal pannello principale.

Oggi il pannello principale contiene, in un'unica colonna:

| Contenuto attuale | Dove dovrebbe stare |
|---|---|
| Partenza + 2 pulsanti | corretto |
| Elenco tappe intermedie | commodo ma rumoroso |
| Punti di passaggio | corretto |
| Profilo di instradamento | pannello opzioni (cap. 2.3 e 8) |
| Pannello dettagli rotta (KPI) | dovrebbe essere secondario |
| Pulsante Salva | corretto |
| Velocita media | assente |
| Contenuto mappa / POI | assente |

Il pannello e gia al limite della larghezza (320-420 px) e dell'altezza,
e usa `adatta_altezza()` con calcoli manuali.

### 3.5 I pulsanti laterali non sono ancora "a icona con tooltip"

La visione (cap. 2.1) chiede icone con tooltip. Lo stato attuale:

| Requisito | Stato |
|---|---|
| Icone | si: sono solo emoji (9 icone) |
| Tooltip con il nome | presente |
| Stile Komoot chiaro e minimale | no: tema scuro (#252526) |

Il tema scuro contraddice la visione, ma e una scelta estetica coerente con
il resto dell'app: **va deciso se la visione va aggiornata o il tema cambiato**.

### 3.6 La ricerca e limitata a GeoNames (cap. 3.1)

| Requisito | Stato |
|---|---|
| Trovare citta | si |
| Trovare luoghi | si |
| Trovare POI (ristoranti, hotel, campeggi, fontane) | no: GeoNames contiene soprattutto toponimi |
| Non serve trovare indirizzi | coerente |
| Problema noto: copertura incompleta | confermato e non risolto |
---

## 4. Cosa manca (rispetto alla visione)

### 4.1 Funzionalita assenti

| Funzionalita | Cap. visione | Note |
|---|---|---|
| **Scelta del contesto** (tappa / percorso / viaggio / test) | 4 | Il bivio piu importante, assente |
| **Suddivisione automatica in tappe** | 5 | Per km o per giorni |
| **Conferma "Vuoi suddividere?"** dopo una tappa unica | 7 | |
| **Posizione attuale da GPS** | 3 | Il widget ha gia il codice per i permessi GPS (`_gestisci_permessi_gps`) ma non lo usa per il pianificatore |
| **Posizioni salvate** | 3 | |
| **Click sulla mappa per partenza/arrivo** | 3 | Esiste solo per i waypoint |
| **Ricerca POI** | 3.1 | GeoNames e solo toponimi |
| **Pannello opzioni separato** | 2.3, 8 | Profilo bici, velocita media, contenuto mappa |
| **Velocita media** (per stimare tempi) | 8 | Assente |
| **Scelta dei layer** | 9 | Assente (previsto come "domani") |
| **Modifica del percorso intero** (non solo tappa singola) | 7 | |

### 4.2 Cosa NON manca ma va notato

Non e un requisito assente, ma un dettaglio importante:

- Il **salvataggio come bozza** (cap. 4, "test tecnico") non esiste, ma
  c'e gia un meccanismo di `stato` nella tabella `tappe`
  (`ATTIVA` / `VARIANTE` / `SOSPESA`) che potrebbe ospitare il concetto.

### 4.3 Informazioni che abbiamo davvero (cap. 8.1)

La visione chiede di sapere quali dati del "contenuto mappa" abbiamo, per non
offrire opzioni vuote. Lo stato reale:

| Informazione Komoot | Abbiamo? | Dove |
|---|---|---|
| Superfici (asfalto/sterrato) | si | `superfici_service.py` |
| Quote min/max | si | `WorkerAltimetria` |
| Distanza | si | statistiche BRouter |
| Punti di passaggio | si | `punti_passaggio` |
| Nomi dei luoghi | si | GeoNames + geocodifica offline |
| Strade vietate alle bici | si | `audit_service.py` |
| POI (ristoranti, campeggi...) | no | |
| Alloggi, rifornitori | no | |
| Punti salienti | no | |
| Trail View | no | |

### 4.4 Domande aperte ereditate dalla visione

Dalla sezione 11 della visione, con lo stato odierno:

| Domanda | Stato |
|---|---|
| Quali POI cercare? | non affrontata |
| Come risolvere il problema di GeoNames? | non affrontata (gap confermato) |
| Quali layer implementare? | non affrontata |
| Quali informazioni del "contenuto mappa" abbiamo? | **rispondibile** (vedi 4.3) |
| Come si integra con il diario di bordo? | non affrontata |
| Come si integra con il sito web? | non affrontata |

---

## 5. Sintesi

| Area | Stato rispetto alla visione |
|---|---|
| Infrastruttura tecnica (separazione moduli, worker, servizi) | **Solida** |
| Calcolo rotta e feedback all'utente | **Buono** |
| Inserimento punti e modifica tappa | **Funziona ma rigido** |
| Modello di dominio ("contesto", "tappe") | **Assente** |
| Suddivisione in tappe | **Assente** |
| Ricerca luoghi | **Solo toponimi** |
| Pannello opzioni separato | **Assente** |
| Layer e contenuto mappa | **Assente** (previsto come "domani") |

**Il pianificatore attuale e un buon motore di calcolo di rotte con
risposta visiva chiara, ma non e ancora un pianificatore di viaggi**:
non sa cosa l'utente sta creando, non sa suddividere un percorso in
tappe, e obbliga a costruire ogni tappa a mano.

L'infrastruttura su cui costruire e pero buona: i servizi sono separati
dalla GUI, le funzioni pure esistono gia in `punti_service.py`, e la
gestione dei thread e solida.

---

## 6. Informazioni non disponibili

Non ho potuto verificare questi aspetti con la sola lettura del codice:

| Punto | Perche |
|---|---|
| Comportamento reale del JavaScript della mappa | Il file non e tra quelli analizzati (probabilmente in un template statico) |
| Velocita effettiva del polling Flask | Richiederebbe misurazioni a runtime |
| Quale sorgente di POI sia effettivamente disponibile | Dipende da dati esterni (OSM?) |
| Uso della geolocalizzazione in altre schermate | Serve verificare se il GPS e usato altrove |
| Uso reale del pulsante "Modifica tratta" | Il percorso di trascinamento dipende dal JS |

Il worker gestisce bene l'errore: se GeoNames non trova nulla suggerisce
"Prova con un nome piu noto oppure inserisci le coordinate", quindi
l'utente non resta bloccato, ma la ricerca resta povera.

Nota: esiste anche una **geocodifica inversa** (`WorkerNomiLuoghi`) che funziona
solo offline e sulle mappe locali scaricate.

### 3.7 Le 4 modalita di input della visione (cap. 3)

| Modalita richiesta | Esiste oggi |
|---|---|
| 1. Posizione attuale (GPS) | no |
| 2. Posizioni salvate (Casa, Lavoro...) | no |
| 3. Ricerca | si (solo nomi) |
| 4. Click sulla mappa | si (solo waypoint, non per partenza/arrivo) |

Il click sulla mappa esiste **solo per i punti di passaggio**: partenza e
destinazione si inseriscono esclusivamente a tastiera.

### 3.8 I layer mappa (cap. 9)

Oggi c'e **un solo stile** (OpenMapTiles/OpenStreetMap). Non esiste alcun
meccanismo di scelta dello stile, ne un menu per il contenuto della mappa.
Non e un problema rispetto a oggi: la visione dice esplicitamente che i
layer sono "domani".

### 3.9 Le azioni dopo la creazione (cap. 7)

| Azione richiesta | Esiste oggi |
|---|---|
| Salva percorso (nella struttura giusta) | Il salvataggio esiste, ma **la struttura non e scelta** (vedi 3.1) |
| Modifica percorso | Solo per una singola tappa (trascinamento), non per il percorso intero |
| Suddividi in tappe | assente |

### 3.10 Rischi tecnici rilevati

| Problema | Dove | Gravita |
|---|---|---|
| Timeout BRouter di **320 secondi** | `mappa_worker.py:193` | Se BRouter non risponde, l'interfaccia resta occupata per 5 minuti |
| Polling Flask durante l'interazione | `mappa.py:167` | Accettabile, ma accoppia Qt, Flask e JavaScript |
| Un solo worker di routing attivo | `mappa_pianificatore.py:62` | Se l'utente clicca Salva due volte, il secondo thread sovrascrive il riferimento del primo |
| La firma confronta **testi grezzi** | `punti_service.py:91` | "Modena" e "modena" sono firme diverse = ricalcolo inutile |
| Routing riuscito | KPI tecnici + "Anteprima aggiornata; premi il pulsante per salvare" | pannello dettagli |
| Routing fallito | MessageBox "Pianificazione non riuscita" + errore BRouter | dialogo |
| Campi cambiati durante il routing | "I campi sono cambiati durante il routing: ricalcola l'anteprima" | pannello dettagli |
| Salvataggio | MessageBox "Percorso salvato" con km | dialogo |
| Precalcolo fallito | MessageBox "Precalcolo non completato" (la rotta e comunque salvata) | dialogo |
| Errore salvataggio | MessageBox "Errore di salvataggio" + rimozione GPX | dialogo |
| Nessuna rotta calcolata | "La ripartizione compare dopo il calcolo della rotta." | pannello dettagli |
| Nessun percorso aperto | "Apri o crea un percorso dalla Dashboard prima di pianificare" | dialogo |

**Nota**: quasi tutte le comunicazioni sono **modali** (`QMessageBox`), tranne
quelle del pannello dettagli, che sono persistenti.