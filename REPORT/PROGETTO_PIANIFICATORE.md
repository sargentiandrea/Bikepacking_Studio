# Progettazione UX del Pianificatore Percorso

Documento di progettazione (Passo 2). Costruisce sulle due fonti:

- `REPORT/VISIONE_PIANIFICATORE.md` — dove si vuole arrivare
- `REPORT/ANALISI_PIANIFICATORE.md` — dove siamo oggi
- `REPORT/FIRST_PRINCIPLES.md` — i principi che non si negoziano

Non modifica alcun file di codice: qui si decide **cosa** fare, poi nel
Passo 3 si decide **come**.

---

## 0. Principi di progettazione

Prima delle soluzioni, cinque regole che valgono per tutto il documento.

| # | Principio | Da dove viene |
|---|---|---|
| P1 | **L'utente non deve mai essere incerto** su cosa sta succedendo o su cosa può fare dopo | Visione cap. 1 |
| P2 | **Ogni azione dice cosa farà prima di farlo** (niente calcoli a sorpresa) | Visione cap. 1 |
| P3 | **Il percorso è un'ipotesi, non un vincolo**: si deve poter deviare senza perdere il lavoro fatto | First Principles 2 |
| P4 | **Le funzionalità fondamentali funzionano offline** | First Principles 9 |
| P5 | **Non si offrono opzioni per dati che non abbiamo** | Visione cap. 8.1 |

### Traduzione in scelte progettuali

| Principio | Scelta che ne deriva |
|---|---|
| P1 | Nessun salvataggio senza una conferma esplicita che mostri **cosa** verrà salvato e **dove** |
| P2 | Ogni operazione lunga mostra: cosa sta facendo → cosa ha fatto → cosa posso fare ora |
| P3 | Nessuna azione distruttiva irreversibile senza uscita (annulla / modifica percorso) |
| P4 | La ricerca GeoNames resta il primo livello; POI e GPS sono miglioramenti, non prerequisiti |
| P5 | Il pannello opzioni mostra solo i controlli per cui esiste il dato |

---

## 1. Flusso utente

### 1.1 Visione generale: dal sogno alla tappa salvata

```
FASE A - CONTESTO
  L'utente sceglie cosa sta creando
  [ Tappa unica ] [ Percorso ] [ Parte di viaggio ] [ Test ]
                    |
FASE B - ROTTA
  Inserisce partenza e arrivo, eventualmente con punti di passaggio
  vede l'anteprima e i dati tecnici
                    |
FASE C - SUDDIVISIONE (solo se "Percorso")
  Sceglie km per tappa OPPURE giorni per tappa
  vede quante tappe verranno create e dove finiscono
                    |
FASE D - CONFERMA
  Vede il riepilogo: N tappe, X km, Y giorni
  [ Salva ] [ Modifica ] [ Annulla ]
                    |
FASE E - DOPO
  Il percorso si apre; da li in poi si torna al pianificatore con
  "Modifica percorso"
```

Le fasi C e D si saltano quando il contesto non e "Percorso".

### 1.2 FASE A - Contesto

**Quando parte**: quando l'utente clicca "Pianificatore" **senza** un
percorso aperto, oppure quando preme "Salva" e non ha ancora scelto.

**Cosa vede**: quattro card cliccabili, una sola selezionata.

| Card | Cosa significa | Cosa succede dopo |
|---|---|---|
| **Tappa singola** | Una tappa isolata, es. Modena-Napoli | Salva e basta. Chiede: "Vuoi suddividere?" |
| **Percorso** | Un viaggio da suddividere in tappe | Apre la Fase C (suddivisione) |
| **Parte di viaggio** | Un blocco di un viaggio piu grande | Si integra nel blocco esistente |
| **Test** | Una prova, non un percorso reale | Salva come bozza, fuori dal DB principale |

**Perche qui**: e la decisione che oggi non viene mai presa ed e la radice
di quasi tutti i problemi elencati nell'analisi (cap. 3.1).

### 1.3 FASE B - Rotta

Invariata rispetto a oggi, con tre aggiunte.

```
1. Inserisce partenza   [GPS] [⌨ nome o coordinate]
2. Inserisce arrivo     [GPS] [⌨ nome o coordinate]
3. (opzionale) aggiunge punti di passaggio
                    |
4. L'anteprima si calcola da sola, senza dover salvare
                    |
5. Vede: km, dislivello, pendenza, superfici, quote
   e una riga di stato che dice cosa puo fare adesso
```

Le tre aggiunte rispetto a oggi:

| Aggiunta | Perche |
|---|---|
| Il pulsone GPS accanto a **partenza e arrivo** (oggi esiste solo per i waypoint) | Le 4 modalita di input della visione cap. 3 non sono soddisfatte: il click esiste solo per i punti |
| Il riepilogo mostra **anche i giorni stimati**, non solo i km | E il dato necessario per la Fase C |
| La riga di stato cambia forma: da semplice testo a **"cosa puo fare ora"** | Principio P1 |

### 1.4 FASE C - Suddivisione in tappe

**Quando parte**: solo se il contesto e "Percorso".

**Cosa vede**: due campi affiancati, uno attivo alla volta.

| Campo | Esempio | Significato |
|---|---|---|
| Km per tappa | `120` | Tanti km in ogni tappa |
| Giorni per tappa | `1` | Un giorno di pedalata per tappa |

**Regola calcolata e mostrata in tempo reale**: sotto ai campi, il sistema
mostra sempre la conseguenza.

| Situazione | Cosa deve succedere | Cosa vede l'utente |
|---|---|---|
| 500 km, 120 km/tappa | 5 tappe | "5 tappe: 120 km, 120, 120, 120, 20" |
| 500 km, 550 km/tappa | **1 tappa** | "Il percorso e piu corto di una tappa: 1 tappa sola" |
| 500 km, 1 giorno/tappa | **1 tappa** | "1 giorno basta per 500 km: 1 tappa sola" |
| 500 km, 0 giorni | Errore | "Indica almeno 1 giorno" |
| Test, nessun campo | disabilitati | grigi, con tooltip "Disponibile solo per i percorsi" |

Il caso "550 km su 500 km = tappa unica" e la regola esplicita della visione
cap. 5: **non e un errore, e il risultato corretto**. Il sistema non deve
chiedere scuse, deve dirlo e basta.

### 1.5 FASE D - Conferma

**Cosa vede**: un riepilogo in chiaro prima di scrivere.

```
Salverai:
---

## 2. Interfaccia (cosa vede l'utente)

### 2.1 Struttura a schermata

```
+---------------------------------------------------------------+
| BARRA LATERALE (85px)      |  MAPPA                            |
|                            |                                  |
|  📂                        |   +---------------------------+  |
|  🧩                        |   |  TOOLBAR: 3 pulsanti     |  |
|  🗺️                        |   +---------------------------+  |
|  ⚠️                        |                                  |
|  🚢                        |   [ web view MapLibre ]        |
|  🛂                        |                                  |
|  🗓️                        |   +------------------+          |
|  📊                        |   | PIANIFICATORE    |          |
|  💰                        |   | (pannello       |          |
|                            |   |  scorrevole)    |          |
|  (solo icone + tooltip)    |   +------------------+          |
+---------------------------------------------------------------+
```

Il pianificatore resta un pannello flottante sopra la mappa, come oggi.
Non diventa una pagina a se: la mappa e il piano devono stare insieme.

### 2.2 Il pannello, sezione per sezione

Oggi il pannello e un'unica colonna affollata. La progettazione lo divide
in zone con pesi diversi.

```
+--------------------------------------+
| 🗺️ Il tuo percorso        [⚙] [✕]   |   <- intestazione
+--------------------------------------+
| COSA STAI CREANDO                    |   <- solo se non scelto
| ┌────────┐ ┌────────┐                |
| │ Tappa  │ │Percorso│  ...           |   <- FASE A
| └────────┘ └────────┘                |
|                                      |
| [≡] Percorso attivo: Le Coste  [✕]  |   <- indicatore di contesto
|                                      |
| PARTENZA                    [GPS][🟢] |
| [ Modena                          ]  |
|                                      |
| 📍 PUNTI DI PASSAGGIO               |
| [ A  Firenze                      ]  |
### 2.4 Pannello opzioni (separato)

La visione chiede (cap. 2.3 e 8) che non sia nel pannello principale.
Progettazione: un **pannello separato**, richiamato da un'icona ⚙
nell'intestazione del pianificatore.

```
+------------------------------+
| ⚙ Opzioni percorso       [✕] |
+------------------------------+
| PROFILO BICI                 |
| [ Gravel / Viaggio       v ] |
|                              |
| VELOCITA MEDIA               |
| [ 22 ] km/h                   |
| ℹ Stima: 500 km = 23 ore     |
|                              |
| CONTENUTO MAPPA              |
| ☑ Superfici                  |
| ☑ Strade vietate alle bici   |
| ☐ Punti di interesse         |
|   ℹ Non ancora disponibili   |
|                              |
| MAPPA                        |
| [ Stradale              v ]   |
+------------------------------+
```

**Applicazione del principio P5**: la voce "Punti di interesse" appare
**spuntata ma con nota "non ancora disponibili"** invece di essere nascosta.
Motivo: se l'utente non la vede, non la chiedera; se la vede disabilitata,
capisce che e prevista e che manca. E un segnale utile.

### 2.5 La riga "cosa puo fare ora"

E l'elemento piu importante per il principio P1. Sostituisce il testo di
stato libero con un messaggio strutturato.

| Situazione | Messaggio | Azioni disponibili |
|---|---|---|
| Campi vuoti | "Inserisci partenza e arrivo per iniziare" | nessuna |
| Campi completati, in calcolo | "Sto calcolando il percorso..." (con animazione) | nessuna |
| Anteprima pronta | "Percorso calcolato: 500 km, 5 giorni" | **Salva il percorso** |
| Errore rete | "Non riesco a contattare il servizio di routing" | **Riprova** |
| Tappa in modifica | "Stai modificando la tappa 3 di 5" | **Annulla modifica** |
| Punto gia sulla rotta | "Questo punto e gia sulla tua rotta" | **Aggiungi come tappa** / **Ignora** |
| Punto lontano da ogni tappa | "Questo punto devia l'intero percorso" | **Devia tutto** / **Aggiungi come tappa** |

### 2.6 Coerenza visiva

| Elemento | Scelta | Nota |
|---|---|---|
| Tema | scuro (quello attuale) | **La visione dice "chiaro, minimale" ma il progetto e scuro**: da decidere |
| Font | 12-13 px, come oggi | Gia leggibile |
| Colori | blu `#0284c7` primario, verde `#22c55e` conferma, rosso `#ef4444` pericolo | Coerenti col pannello attuale |
| Icone | emoji, come oggi | Coerenti con la barra laterale |

**Nota di divergenza**: la visione chiede uno stile Komoot chiaro. Il progetto
ha un tema scuro coerente in tutte le 9 pagine. Cambiare tema solo al
pianificatore creerebbe disuguaglianza; cambiare tutto il progetto e fuori
scope. **Proposta**: correggere la visione su questo punto, non il codice.

### 2.7 Le 4 modalita di input (cap. 3)

| Modalita | Dove sta | Stato progettato |
|---|---|---|
| 1. Posizione attuale (GPS) | icona accanto a partenza/arrivo | Da fare: il codice per i permessi esiste gia |
| 2. Posizioni salvate | menu a tendina del campo | Da fare: serve il modello dati |
| 3. Ricerca | nel campo testo | **Gia fatto**, da arricchire |
| 4. Click sulla mappa | icona + click | Parziale: solo waypoint, va esteso a partenza/arrivo |

---

## 3. Le soluzioni in sintesi

| # | Problema (cap. analisi) | Soluzione | Sotto-fase |
|---|---|---|---|
| S1 | 3.1 Contesto assente | Selettore di contesto a 4 card | 5.2 |
| S2 | 3.2 Suddivisione assente | Motore di suddivisione km/giorni | 5.3 |
| S3 | 3.3 Waypoint non deviano | Rilevazione vicinanza + scelta comportamento | 5.4 |
| S4 | 3.4 Pannello affollato | Pannello opzioni separato + riepilogo | 5.5 |
| S5 | 3.4 "Cosa puo fare ora" assente | Riga di stato strutturata con azioni | 5.1 |
| S6 | 3.10 Timeout 320 s | Timeout progressivo + annullamento | 5.1 |
| S7 | 3.10 Worker unico sovrascritto | Gestore a coda come gli altri worker | 5.1 |
| S8 | 3.10 Firma su testi grezzi | Firma normalizzata | 5.1 |
| S9 | 3.7 Click solo per waypoint | Click per partenza e arrivo | 5.6 |
| S10 | 3.7 GPS assente | Pulsante posizione attuale | 5.6 |
| S11 | 3.6 Solo toponimi | Ricerca POI da OpenMapTiles locale | 5.7 |
| S12 | 3.7 Posizioni salvate assenti | Luoghi salvati | 5.8 |
| S13 | 3.9 Modifica percorso assente | Pulsante "Modifica percorso" | 5.9 |
| S14 | 3.8 Layer assenti | Menu stile mappa | 5.10 |
| S15 | 3.5 Tema chiaro vs scuro | Correggere la visione, non il codice | decisione |
---

## 4. Le soluzioni in dettaglio

### S1 - Selettore di contesto

**Problema**: il pannello non chiede mai cosa l'utente sta creando (analisi 3.1).

**Cosa cambia nell'interfaccia**
- In alto nel pannello, 4 card: Tappa singola / Percorso / Parte di viaggio / Test
- Una riga di contesto che riassume la scelta e permette di cambiarla
- Il pannello di suddivisione compare solo se il contesto e "Percorso"

**Cosa cambia nel comportamento**

| Contesto | Azione primaria | Extra |
|---|---|---|
| Tappa singola | "Salva tappa" | dopo il salvataggio chiede "Vuoi suddividere?" |
| Percorso | "Salva percorso" | apre la suddivisione (S2) |
| Parte di viaggio | "Salva nel blocco" | chiede in quale blocco esistente |
| Test | "Salva bozza" | stato BOZZA, escluso dai calcoli |

La scelta e **modificabile** dopo, da "Modifica percorso" (visione cap. 4).

**File coinvolti**

| File | Natura della modifica |
|---|---|
| `service/planning_context_service.py` | **nuovo**: i 4 contesti e le regole di validazione |
| `gui/mappa_pianificatore.py` | mostra le card, passa il contesto al salvataggio |
| `service/salvataggio_tappa_service.py` | accetta il contesto, scrive lo stato |
| `service/mappa_dati_service.py` | lettura dello stato |

**Rischio**: **basso**. Nessuna modifica al calcolo della rotta. Il campo
`stato` esiste gia in `tappe` con i valori `ATTIVA` / `SOSPESA` / `VARIANTE`:
serve aggiungere `BOZZA`, escludendola dai calcoli. Serve una migrazione
per il valore di default.

**Beneficio**: **molto alto**. E la decisione mancante che rende possibili
tutte le altre. Risolve il problema radice.

---

### S2 - Suddivisione in tappe per km o per giorni

**Problema**: non esiste alcun codice che suddivida (analisi 3.2).

**Cosa cambia nell'interfaccia**
- Un pannello di suddivisione con due campi alternativi: km/tappa e giorni/tappa
- Sotto, l'anteprima della divisione: "5 tappe: 120, 120, 120, 120, 20 km"
- Un'anteprima grafica sulla mappa con i punti di divisione

**Cosa cambia nel comportamento**
- Si calcola dove cade ogni divisione lungo la geometria della rotta
- Ogni tappa viene salvata come riga in `tappe` con la sequenza corretta
- Il caso "parametro maggiore della lunghezza" produce **una tappa sola**

**La regola, in dettaglio**

```
distanza_totale = lunghezza della rotta (da BRouter)
tempo_totale    = tempo stimato (da BRouter)

SE contesto = Percorso:
  SE km_per_tappa e valorizzato:
     numero = ceil(distanza_totale / km_per_tappa)
  SE giorni_per_tappa e valorizzato:
     km_per_tappa = (tempo_totale / 3600) / 60 / giorni_per_tappa   (in km)
     numero = ceil(distanza_totale / km_per_tappa)

  SE numero < 1: numero = 1     <- il caso "550 km su 500 km"
```

Il calcolo dei giorni usa `analizza_dati_rotta_brouter()` di
`service/stats_service.py`, che **gia restituisce** `track-length` e
`total-time`: il dato esiste gia, non serve alcuna nuova fonte.

| Caso | Parametro | risultato | numero |
|---|---|---|---|
| 500 km, 120 km/tappa | 120 km | 120,120,120,120,20 | 5 |
| 500 km, 550 km/tappa | 550 km | 500 (tutto) | **1** |
| 500 km, 1 giorno | ~83 km | tutto in un giorno | **1** |
---

### S3 - Punti di passaggio che deviano la traccia

**Problema**: si aggiunge sempre un punto e si ricalcola tutto; non si
riconosce quando il punto e gia sul percorso (analisi 3.3).

**Cosa cambia nell'interfaccia**
- Prima di ricalcolare, il sistema **classifica** il punto rispetto alla rotta
- Compare un messaggio con la classificazione e le azioni possibili

**Cosa cambia nel comportamento**

Oggi c'e un solo comportamento (ricalcolo totale). La progettazione ne
introduce tre, scelti dall'utente in base a quello che vede:

| Classificazione | Cosa vede l'utente | Cosa puo fare |
|---|---|---|
| **Gia sul percorso** | "Questo punto e gia sulla tua rotta" | Aggiungere come tappa / Ignorare |
| **Vicino a una tappa** (< 5 km) | "Questo punto e vicino alla tappa 3" | Devia la tappa 3 / Devia tutto |
| **Lontano** | "Questo punto devia l'intero percorso" | Devia tutto / Aggiungi come tappa |

**La regola di classificazione**

```
distanza_minima = distanza punto -> geometria della rotta corrente
distanza_tappa  = distanza punto -> estremi della tappa piu vicina

SE distanza_minima < 100 m   -> GIA SUL PERCORSO
SE distanza_tappa  < 5 km    -> VICINO A UNA TAPPA
ALTRIMENTI                    -> LONTANO
```

Le distanze si calcolano con `calcola_distanza_haversine()` di
`service/geo_utils.py`, gia disponibile.

**Nota importante**: questa funzionalita **si appoggia a S1**. Senza il
contesto non si puo dire "questa tappa" o "l'intero percorso": si puo solo
ricalcolare tutto. Vanno progettate insieme.

**File coinvolti**

| File | Natura della modifica |
|---|---|
| `service/waypoint_service.py` | **nuovo**: `classifica_punto(coordinate_rotta, tappe, punto)`, funzione pura |
---

### S4 - Pannello opzioni separato

**Problema**: profilo, velocita e contenuto mappa sono (o dovrebbero
essere) nel pannello principale (analisi 3.4, visione cap. 2.3 e 8).

**Cosa cambia nell'interfaccia**
- Un'icona apre un pannello opzioni separato
- Il pannello principale si alleggerisce: restano contesto, partenza,
  punti, arrivo, riepilogo e azione primaria
- Compare una riga di riepilogo sempre visibile: "5 tappe · 500 km · 6 giorni"

**Cosa cambia nel comportamento**
- Il profilo di instradamento sparisce dal pannello principale
- La velocita media diventa un dato **usabile**: influisce sul calcolo dei
  giorni e viene salvata con il percorso
- "Cosa visualizzare" controlla quali sezioni del pannello dettagli mostrare

**File coinvolti**

| File | Natura della modifica |
|---|---|
| `gui/mappa_opzioni.py` | **nuovo**: il pannello opzioni |
| `gui/mappa_pianificatore.py` | toglie il combo profilo, aggiunge il bottone |
| `gui/mappa_dettagli.py` | rispetta le scelte di "cosa visualizzare" |
| `service/planning_context_service.py` | conserva velocita media e preferenze |

**Rischio**: **basso**. Spostamento di widget esistenti, nessuna modifica al
calcolo. La velocita media e l'unica parte nuova, ma il dato (tempo totale)
e gia disponibile.

**Beneficio**: **medio-alto**. Risponde a un requisito esplicito della visione
e alleggerisce il pannello, che oggi e al limite.

---

### S5 - Riga "cosa puo fare ora"

**Problema**: il testo di stato e generico e non dice cosa fare (analisi 3.4,
principio P1).

**Cosa cambia nell'interfaccia**
- La riga di stato diventa strutturata: **messaggio + azioni**
- Messaggi in italiano semplice, senza jerga tecnica

**Cosa cambia nel comportamento**

| Prima | Dopo |
|---|---|
| "Anteprima aggiornata; premi il pulsante per salvare la tappa." | "Percorso calcolato: 500 km, 5 giorni" + bottone **Salva** |
| "Salva Percorso" | "Salva il percorso" / "Salva la tappa" / "Salva la bozza" (dipende dal contesto) |
| errore solo in MessageBox | messaggio nella riga + bottone **Riprova** |

Il vantaggio non e solo cosmetico: **gli errori non bloccano con un dialogo
modale**, l'utente vede cosa fare senza chiudere una finestra.

**File coinvolti**

| File | Natura della modifica |
|---|---|
| `gui/mappa_dettagli.py` | `imposta_stato(testo, azioni)` accetta pulsanti |
| `service/punti_service.py` | i testi dei messaggi |
| `gui/mappa_pianificatore.py` | passa le azioni corrette per ogni stato |

**Rischio**: **molto basso**. Solo presentazione.

**Beneficio**: **alto**. E il modo piu economico per rispettare il principio
P1, che e il principio guida della visione.

---

### S6 - Timeout BRouter e annullamento

**Problema**: timeout di 320 secondi, nessuna possibilita di annullare
(analisi 3.10).

**Cosa cambia nell'interfaccia**
- Durante il calcolo: "Sto calcolando il percorso..." con indicatore di
  progresso e bottone **Annulla**
- Alla fine: "Non riesco a contattare il servizio di routing" + **Riprova**

**Cosa cambia nel comportamento**

| Oggi | Progettato |
|---|---|
| Attesa fino a 320 s, nessuna via d'uscita | Attesa 60 s, poi offerta di annullare |
| Errore solo in MessageBox | Errore nella riga di stato, con **Riprova** |
| Il thread continua anche se non serve piu | `request_stop()` come gli altri worker |

I worker esistenti (`WorkerAnalisiSuperficiOffline`, `WorkerNomiLuoghi`,
`WorkerAltimetria`) hanno gia `request_stop()`. Manca solo a
`PianificazionePercorsoWorker`, che si puo aggiungere con lo stesso codice.

**File coinvolti**

| File | Natura della modifica |
|---|---|
| `gui/mappa_worker.py` | `request_stop()` e timeout 60 s su `PianificazionePercorsoWorker` |
| `gui/mappa_dettagli.py` | indicatore di progresso + bottone Annulla |
| `gui/mappa_pianificatore.py` | collega Annulla al worker |

**Rischio**: **basso**. Il worker usa gia `QThread`; aggiungere un flag e
basta. Attenzione solo a non lasciare la connessione HTTP aperta.

**Beneficio**: **alto**. Un'interfaccia che si blocca 5 minuti e non si puo
interrompere e il motivo per cui gli utenti smettono di fidarsi.

---

### S7 - Coda dei calcoli di rotta

**Problema**: un solo worker di routing attivo, sovrascritto se l'utente
clica due volte (analisi 3.10).

**Cosa cambia nell'interfaccia**
- Nulla di visibile, tranne che il ricalcolo non si perde piu

**Cosa cambia nel comportamento**

Oggi `self.worker_pianificazione` e un attributo singolo: un secondo click
sovrascrive il riferimento del primo thread, che resta vivo ma irraggiungibile
(e Qt puo crashare quando viene distrutto).

La correzione e gia pronta: `GestoreWorkerSingolo`
(`gui/mappa_worker_manager.py`) fa esattamente questo per gli altri 3 worker.
Basta adottarlo anche per il routing.

**File coinvolti**

| File | Natura della modifica |
|---|---|
| `gui/mappa_pianificatore.py` | adotta `GestoreWorkerSingolo` per il routing |
| `gui/mappa_worker.py` | il worker deve accettare `request_stop()` |

**Rischio**: **basso**. Il gestore esiste ed e testato.

**Beneficio**: **medio**. Previene crash e risultati fuori ordine.

---

### S8 - Firma normalizzata

**Problema**: `firma_pianificazione()` confronta i testi grezzi, quindi
"Modena" e "modena" sono due firme diverse (analisi 3.10).

**Cosa cambia nell'interfaccia**
- Nulla di visibile, tranne che l'anteprima non si ricalcola quando non serve

**Cosa cambia nel comportamento**

La firma viene normalizzata prima del confronto:

```
prima:  (progetto, "Modena", (), "Roma", "Gravel", None)
dopo:   (progetto, "modena", (), "roma", "gravel", None)
```

Il risultato e che digitare "modena" invece di "Modena" **non fa ricalcolare
tutto BRouter**, risparmiando una chiamata di rete che puo durare secondi.

---

### S9 - Click per partenza e arrivo

**Problema**: il click sulla mappa esiste solo per i punti di passaggio
(analisi 3.7, visione cap. 3 modalita 4).

**Cosa cambia nell'interfaccia**
- Partenza e arrivo hanno l'icona come i punti di passaggio
- Al click, il campo si riempie con le coordinate
- Un bottone "Indietro" trasforma il campo in un punto di passaggio

**Cosa cambia nel comportamento**

Una sola modalita mappa gestisce tre bersagli, scelti dall'utente prima:

| Modalita scelta | Cosa succede al click |
|---|---|
| Partenza | scrive in partenza |
| Arrivo | scrive in destinazione |
| Punto di passaggio | scrive nel primo campo vuoto (comportamento attuale) |

Il codice di `attiva_modalita_interazione()` accetta gia una stringa di
modalita: aggiungere "set_partenza" e "set_destinazione" e una riga di
gestione.

**File coinvolti**

| File | Natura della modifica |
|---|---|
| `gui/mappa.py` | due nuove modalita in `_leggi_interazioni_mappa()` |
| `gui/mappa_pianificatore.py` | imposta partenza o arrivo ricevuti |
| `service/punti_service.py` | testo delle coordinate |

**Rischio**: **basso**. Il canale esiste gia, il JavaScript accetta gia un
parametro di modalita generico.

**Beneficio**: **medio**. Chiude una delle 4 modalita di input della visione
senza lavoro di fondo.

---

### S10 - Posizione attuale (GPS)

**Problema**: la modalita 1 della visione non esiste (analisi 3.7).

**Cosa cambia nell'interfaccia**
- Un'icona GPS accanto a partenza e arrivo
- Se il permesso non e concesso: "Il browser ha chiesto il permesso per la
  posizione" con il link per concederlo

**Cosa cambia nel comportamento**

Il codice c'e gia: `MappaWidget._gestisci_permessi_gps()` intercetta
`featurePermissionRequested`. Serve solo un modo per chiedere la posizione e
riceverla indietro, come si fa gia per gli eventi di interazione.

**File coinvolti**

| File | Natura della modifica |
|---|---|
| `gui/mappa.py` | richiesta posizione e nuovo evento |
| `service/map_server.py` | nuovo endpoint per l'evento posizione |
| `gui/mappa_pianificatore.py` | riempie il campo |

**Rischio**: **medio-basso**. Il permesso e gia gestito; il punto delicato e
la disponibilita del GPS, che non e garantita.

**Beneficio**: **medio-alto**. E la modalita 1 della visione, utile a chi
inizia il viaggio sul posto.

---

### S11 - Ricerca di POI

**Problema**: GeoNames contiene solo toponimi, non POI (analisi 3.6).

**Cosa cambia nell'interfaccia**
- La ricerca diventa a due stadi: prima i luoghi, poi i POI vicini
- "Ristoranti vicini", "Campeggi qui", "Hotel a Modena"
- Risultati con distanza e icona per categoria

**Cosa cambia nel comportamento**

Il progetto ha gia il layer **POI** di OpenMapTiles: lo usa gia
`service/geocodifica_offline_service.py` per il layer `place`. Lo stesso
approccio (leggere i tile locali) puo servire per i POI del layer `poi`,
senza dipendere da servizi esterni.

Questo risolve anche il "problema noto" di copertura di GeoNames citato
dalla visione: i POI vengono dalle mappe locali, non da GeoNames.

**File coinvolti**

| File | Natura della modifica |
|---|---|
| `service/ricerca_poi_service.py` | **nuovo**: ricerca per categoria e distanza |
| `service/geonames_service.py` | resta il primo livello (toponimi) |
| `gui/mappa_pianificatore.py` | lista risultati sotto il campo |

**Rischio**: **medio-alto**. Il layer POI e molto piu voluminoso di `place`:
una ricerca per raggio puo essere lenta. Va limitato il raggio e il numero
di risultati, e va fatto in background come gli altri worker.

**Beneficio**: **alto**. Chiude il cap. 3.1 della visione e il "problema
noto" sui paesi non trovati, perche non dipende piu solo da GeoNames.


### S12 - Posizioni salvate

**Problema**: la modalita 2 della visione non esiste (analisi 3.7).

**Cosa cambia nell'interfaccia**
- Un menu a tendina accanto ai campi partenza e arrivo con i luoghi salvati
- Campi per aggiungere: nome, indirizzo, tipo (casa, lavoro, meccanico, altro)
- Un segnaposto per la posizione attuale, "salvata al volo"

**Cosa cambia nel comportamento**

| Azione | Effetto |
|---|---|
| Salva posizione attuale | crea un luogo con coordinate e nome |
| Salva da un punto della mappa | idem, da un punto gia scelto |
| Usa un luogo salvato | riempie il campo; la rotta si ricalcola |

**File coinvolti**

| File | Natura della modifica |
|---|---|
| `service/luoghi_salvati_service.py` | **nuovo**: salvataggio e recupero |
| `service/migrazione_luoghi_salvati.py` | **nuovo**: tabella e schema |
| `gui/mappa_pianificatore.py` | il menu a tendina |
| `service/mappa_dati_service.py` | lettura per la firma |

**Rischio**: **medio-basso**. E una tabella nuova, ma il pattern e gia
usato (`blocchi_ordine`, `progetto_stagione`). Nessuna logica complessa.

**Beneficio**: **medio-alto**. E la modalita 2 della visione, e un
risparmio di tempo quotidiano: chi parte da casa non riscrive l'indirizzo
ogni volta.

---

### S13 - "Modifica percorso"

**Problema**: si puo modificare una tappa alla volta, non il percorso
(analisi 3.9, visione cap. 7).

**Cosa cambia nell'interfaccia**
- Nel pianificatore, con un percorso gia salvato: un pulsante
  **"Modifica percorso"** che ricarica partenza, arrivo e punti
- Il contesto salvato viene ripristinato e rimane modificabile (visione cap. 4)

**Cosa cambia nel comportamento**

| Azione | Effetto |
|---|---|
| Modifica percorso | ricarica il form dal percorso salvato |
| Cambia la suddivisione | ricalcola e propone la nuova divisione |
| Salva | aggiorna, senza perdere le tappe esistenti |

Il codice di ricarica esiste gia: `sincronizza_stato_percorso()` carica
automaticamente partenza, arrivo e tappe all'apertura del pannello.

**File coinvolti**

| File | Natura della modifica |
|---|---|
| `gui/mappa_pianificatore.py` | il pulsante e il flusso di modifica |
| `service/mappa_dati_service.py` | lettura dei punti di passaggio salvati |
| `service/salvataggio_tappa_service.py` | aggiornamento della suddivisione |

**Rischio**: **medio-alto**. Ricalcolare la suddivisione significa
**riscrivere le tappe esistenti**, con il rischio di perdere modifiche
locali. Va richiesta conferma esplicita e va mostrato cosa verra
sostituito.

**Beneficio**: **molto alto**. E la terza azione della sezione 7 della
visione, oggi completamente assente.

---

### S14 - Stile della mappa

**Problema**: un solo stile disponibile (analisi 3.8, visione cap. 9).

**Cosa cambia nell'interfaccia**
- Nel pannello opzioni, un menu "Mappa" con gli stili disponibili
- Satellitare per il pianificatore, stradale per la navigazione

**Cosa cambia nel comportamento**
Nessun calcolo: e puramente di visualizzazione.

**File coinvolti**

| File | Natura della modifica |
|---|---|
| `gui/mappa_opzioni.py` | il menu stili |
| `templates/` (JS della mappa) | applicazione dello stile |
| `service/mappa_manager_service.py` | elenco degli stili disponibili |

**Rischio**: **basso** se si usano gli stili gia presenti in
`basemap-styles-master`; **medio** se serve scaricare dati satellitari.

**Beneficio**: **medio**. Utile per leggere il territorio, meno per
pianificare. **Per la visione non e prioritario**: la sezione 9 lo indica
come "domani".

---

### S15 - Tema chiaro o scuro (decisione, non codice)

**Problema**: la visione chiede uno stile Komoot chiaro; il progetto e scuro
(analisi 3.5).

**Le due opzioni**

| Opzione | Cosa comporta | Conviene se |
|---|---|---|
| A - correggere la visione | si documenta che il tema scuro e una decisione del progetto | si vuole evitare di rifare 9 pagine |
| B - cambiare il tema | si ritocca tutto il progetto | si crede che il tema chiaro riduca le paure |

**Raccomandazione**: opzione **A**. Il tema scuro e gia uniforme su tutte le
pagine, le tabelle e il pianificatore; cambiarlo e un lavoro cosmetico molto
ampio con un beneficio incerto. La visione andrebbe aggiornata su questo
punto, non il codice.

**Rischio**: nessuno (e una correzione documentale).

**Beneficio**: evita un lavoro di 9 pagine per un risultato estetico
opinabile.
**Attenzione al principio P4**: se il GPS non e disponibile la funzione deve
fallire in modo chiaro, non bloccare. Per questo e in una sotto-fase separata.
---

## 5. Casi d'uso

Quattro percorsi reali, dal principio alla fine.

### Caso 1 - "Voglio fare Modena-Napoli come tappa singola"

| Passo | Cosa fa l'utente | Cosa vede |
|---|---|---|
| 1 | Apre la Mappa, clicca "Pianificatore" | Le 4 card di contesto |
| 2 | Sceglie **Tappa singola** | La card si evidenzia, sparisce il pannello suddivisione |
| 3 | Scrive "Modena" e "Napoli" | "Sto cercando i nomi..." poi l'anteprima |
| 4 | Vede km, dislivello, superfici | "Percorso calcolato: 640 km, 4 giorni" + **Salva** |
| 5 | Clicka **Salva** | Riepilogo: "Salverai 1 tappa, 640 km" |
| 6 | Conferma | MessageBox "Percorso salvato" |
| 7 | Il sistema chiede | "Vuoi suddividere il percorso in tappe?" |
| 8a | Risponde **No** | Resta una tappa, fine |
| 8b | Risponde **Si** | Si apre la Fase C (S2) |

**Sottopasso 7**: e il comportamento esplicitamente richiesto dalla visione
cap. 7. Oggi non esiste.

### Caso 2 - "Il mio viaggio di 3 settimane, 900 km, voglio 5 tappe"

| Passo | Cosa fa l'utente | Cosa vede |
|---|---|---|
| 1 | Apre il pianificatore | Le 4 card |
| 2 | Sceglie **Percorso** | Compare il pannello suddivisione |
| 3 | Scrive partenza e arrivo | Anteprima: 900 km |
| 4 | Scrive `180` in "km per tappa" | "5 tappe: 180, 180, 180, 180, 180 km" |
| 5 | Vede l'anteprima sulla mappa | 5 punti di divisione evidenziati |
| 6 | Clicka **Salva il percorso** | Riepilogo: "5 tappe, 900 km, 7 giorni" |
| 7 | Conferma | 5 tappe create, la mappa si aggiorna |

**Alternativa al passo 4**: scrive `1` in "giorni per tappa" e ottiene
"15 tappe, 60 km per giorno".

### Caso 3 - "Il punto che ho aggiunto e gia sulla rotta"

| Passo | Cosa fa l'utente | Cosa vede |
|---|---|---|
| 1 | Ha pianificato Modena-Roma | Anteprima 320 km |
| 2 | Clicka "Posiziona waypoint sulla mappa" | "Clicca sulla mappa per posizionare il punto" |
| 3 | Clicka su Firenze, gia sulla rotta | **"Questo punto e gia sulla tua rotta"** |
| 4 | Vede due azioni | **Aggiungi come tappa** / **Ignora** |
| 5a | Sceglie **Ignora** | Nessun ricalcolo, l'anteprima resta |
| 5b | Sceglie **Aggiungi come tappa** | Si apre la Fase C con la rotta divisa in 2 |

**Comportamento attuale**: il punto verrebbe aggiunto comunque e BRouter
ricalcolerebbe tutto, senza dire nulla. E la differenza che S3 introduce.

**Variante**: se il punto e a 20 km dalla rotta, il messaggio diventa
"Questo punto e vicino alla tappa 2" e le azioni sono **Devia la tappa 2**
/ **Devia tutto**.

### Caso 4 - "Devo cambiare il percorso che ho gia salvato"

| Passo | Cosa fa l'utente | Cosa vede |
|---|---|---|
| 1 | Ha un percorso salvato in 5 tappe | Il pianificatore si apre con i dati |
| 2 | Clicka **Modifica percorso** | Partenza, arrivo e punti ricaricati |
| 3 | Cambia la destinazione | Si ricalcola l'anteprima |
| 4 | Riscrive "4 giorni per tappa" | "5 tappe: 180 km, 1 giorno in ciascuna" |
| 5 | Clicka **Salva** | Avviso: "Veranno sostituite 5 tappe. Continuare?" |
| 6 | Conferma | Le 5 tappe vengono riscritte |

**Il passo 5 e obbligatorio**: senza conferma esplicita si rischierebbe di
---

## 6. Piano di implementazione

Dodici sotto-fasi, ordinate dal semplice al complesso. Ogni sotto-fase e un
commit. Il criterio di ordinamento e il **rischio**, non l'importanza.

### Blocco A - Risolvere i problemi tecnici (basso rischio, alto beneficio)

| Sotto-fase | Contenuto | Soluzioni | Rischio |
|---|---|---|---|
| **5.1** | Feedback, timeout, coda, firma | S5, S6, S7, S8 | basso |
| **5.2** | Contesto | S1 | basso |

**Motivazione**: la 5.1 non aggiunge funzionalita ma rende il pianificatore
affidabile. Un utente che aspetta 5 minuti e non puo annullare non usera
niente di tutto il resto.

### Blocco B - Il nucleo del pianificatore (rischio medio)

| Sotto-fase | Contenuto | Soluzioni | Rischio |
|---|---|---|---|
| **5.3** | Suddivisione in tappe | S2 | medio-alto |
| **5.4** | Waypoint che deviano | S3 | medio |
| **5.5** | Pannello opzioni | S4 | basso |

**Attenzione**: 5.3 e 5.4 dipendono da 5.2. Non si possono fare prima.

### Blocco C - Completezza dell'interfaccia (rischio basso-medio)

| Sotto-fase | Contenuto | Soluzioni | Rischio |
|---|---|---|---|
| **5.6** | Click per partenza/arrivo e GPS | S9, S10 | basso-medio |
| **5.7** | Ricerca POI | S11 | medio-alto |
| **5.8** | Posizioni salvate | S12 | medio-basso |
| **5.9** | Modifica percorso | S13 | medio-alto |

### Blocco D - Ritocchi (rischio basso, bassa priorita)

| Sotto-fase | Contenuto | Soluzioni | Rischio |
|---|---|---|---|
| **5.10** | Stile mappa | S14 | basso |
| **5.11** | Decisione sul tema | S15 | nessuno (documentale) |

### Come NON procederei

| Scelta | Motivo |
|---|---|
| Suddivisione (5.3) prima del contesto (5.2) | La suddivisione ha senso solo nel contesto "Percorso" |
| POI (5.7) prima del pannello opzioni (5.5) | I POI servono soprattutto per i luoghi salvati (5.8) |
| Tutto insieme | Un errore in 5.3 (scrittura multi-tappa) renderebbe illeggibile quale di 10 modifiche ha rotto il salvataggio |
| Saltare la 5.1 | Sembra no-op ma e il prerequisito per fidarsi del resto |

### Il percorso minimo

Se si vuole il **minimo** per avere un pianificatore coerente con la visione:

```
5.1  ->  5.2  ->  5.3  ->  5.4
```

Quattro sotto-fasi. Alla fine il pianificatore chiede **cosa** stai creando,
**sa suddividere** in tappe e **devia** la traccia quando serve: le tre cose
mancanti che l'analisi ha identificato come problema principale.

Tutto il resto (opzioni, GPS, POI, luoghi salvati, stili) e miglioramento
successivo.

---

## 7. Informazioni che mancano

Non ho potuto verificare questi punti, che influenzano la progettazione:

| Punto | Perche | Come risolverlo |
|---|---|---|
| Velocita reale di BRouter | Non misurata; il timeout di 60 s e una stima | Misurare su 3-4 percorsi reali |
| Reale costo di una ricerca POI | Il layer `poi` non e mai stato interrogato | Prototipo di benchmark prima di 5.7 |
| Formato del JavaScript della mappa | Non analizzato | Leggere i template prima di 5.6 e 5.9 |
| Uso reale del trascinamento | Dipende dal JS non letto | Verifica manuale prima di 5.4 |
| Se "Parte di viaggio" ha gia un modello | Il blocco esiste (`blocchi_ordine`) ma il caso d'uso non e definito nella visione | **Decisione da prendere prima di 5.2** |

L'ultimo punto e il piu importante: la visione chiede "Parte di un viaggio"
come uno dei 4 contesti, ma **non dice cosa succede operativamente**. Prima
di implementare 5.2 va chiarito se significa "aggiungo a un blocco esistente"
o qualcos'altro.
perdere modifiche fatte a mano sulle tappe.
