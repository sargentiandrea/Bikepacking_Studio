# Piano di migrazione da BRouter a GraphHopper

Documento di sola analisi. **Nessun file di codice è stato modificato.**

Data: 03/10/2026
Riferimenti: `service/config.py`, `gui/mappa_worker.py`, `service/stats_service.py`

---

## Perché migrare

Il motivo è misurato, non ipotizzato. Su questo servizio locale:

| Percorso | BRouter trekking | BRouter fastbike |
|---|---|---|
| Bologna-Modena (~56 km) | 0,84 s | 1,00 s |
| Bologna-Firenze (~121 km) | 7,69 s | 6,55 s |
| Bologna-Napoli (~706 km) | 83,92 s | 56,19 s |

Il tempo cresce più che linearmente con la lunghezza: 100 km → 7,7 s,
700 km → 84 s (11× la distanza, 11× il tempo). Oltre i ~1000 km la
situazione degenererebbe. La sotto-fase 5.1 ha già dovuto alzare il tetto
di attesa a 110 s per Napoli: è una soluzione di contorno, non una risposta.

GraphHopper agisce sulla causa: usa **Contraction Hierarchies**, una
pre-elaborazione del grafo che rende la ricerca del percorso quasi costante
rispetto alla lunghezza.

| | BRouter | GraphHopper |
|---|---|---|
| 100 km | 7,7 s | attesi < 100 ms |
| 700 km | 84 s | attesi < 300 ms |
| Profili bici | trekking, fastbike | bike, racingbike, mtb (nativi) |
| Licenza | GPL (BRouter) | Apache 2.0 |
| Altimetria | SRTM integrata | SRTM, va scaricata a parte |

**Attenzione:** i tempi GraphHopper sopra sono attese basate sul design di
CH, **non misure**. La sotto-fase 6.0 li verificherà realmente.

---

## 1. Requisiti per installare GraphHopper

### Software

| Requisito | Serve | Situazione su questa macchina |
|---|---|---|
| Java | 17 o 21 (JDK) | **Java 25.0.4.1 LTS installato** |
| RAM | 2 GB (Italia) – 8 GB (Europa) | 15,6 GB totali |
| CPU | 2+ core per l'import | 12 thread logici |
| Disco | 1 GB (Italia) – 15 GB (Europa) | 111,7 GB liberi |

**Attenzione a Java 25:** è più recente di quanto GraphHopper 11.1 testi.
Il progetto documenta ufficialmente Java 17/21. Con Java 25 il server
*potrebbe* funzionare, ma non è una configurazione verificata: va provata
prima di investire il resto del lavoro. Se fallisce, la soluzione è
installare un JDK 21 in parallelo, senza disinstallare il 25. È la prima
verifica della sotto-fase 6.0.

La macchina ha risorse abbondanti: nessun vincolo di memoria o disco.

### Versione

**GraphHopper 11.1**, rilasciata il 29 settembre 2026 (verificato su
GitHub). È l'ultima stabile; 11.0 e 10.2 restano come fallback.

Nota: dalla versione 10 GraphHopper ha rimosso le vecchie `flagEncoders` in
favore dei **custom model** in JSON. Le configurazioni trovate online con
`graph.flagEncoders: bike|foot` sono **obsolete** e non funzioneranno. Il
piano qui sotto usa il formato attuale.

---

## 2. Dati OSM: cosa scaricare

### La scelta

| Area | PBF | Grafo (Italia) | Import | Serve per |
|---|---|---|---|---|
| **Italia** | ~1,5 GB | ~400 MB | ~5-15 min | **consigliato** |
| Europa | ~25 GB | ~6 GB | ~1-3 ore | espansione futura |
| Pianeta | ~80 GB | ~20 GB | 6-12 ore | eccessivo |

**Raccomando: Italia.** Motivi:

1. Il 90% dell'uso è in Italia (i progetti sono italiani).
2. Import 10-20 volte più rapido: il ciclo di prova dura giorni, non settimane.
3. Un errore di configurazione si scopre subito, non dopo 6 ore.
4. Se un giorno serve l'Europa si aggiunge un'area più grande: è una
   questione di spazio e tempo, non di architettura.

Per il bikepacking extraeuropeo si può scaricare il **Paese specifico**
anziché l'intera Europa: molto più leggero.

### Dove scaricare (tutto offline, download una tantum)

| Sorgente | Contenuto | Note |
|---|---|---|
| Geofabrik | `italy-latest.osm.pbf` | il più usato |
| BBBike | estrazioni personalizzate | per sottoinsiemi |
| OSM Italia | mirror nazionale | affidabilità variabile |

Dopo l'import il PBF non serve più e si può cancellare per risparmiare 1,5 GB.

### Altimetria (SRTM): il punto spesso dimenticato

BRouter ha l'altimetria SRTM **integrata**. GraphHopper **no**: va
scaricata a parte, altrimenti le quote valgono zero e il profilo
altimetrico del pianificatore si svuota.

| Dato | Origine | Note |
|---|---|---|
| SRTM | NASA/USGS | quote al suolo, gratuiti |
| SRTMGL1 | NASA | versione più recente |

Senza questo, `imposta_altimetria` mostrerebbe `--` ovunque: una
regressione visibile all'utente. **Obbligatorio**, va messo in conto come
requisito di primo livello.

---

## 3. Configurazione dei profili bici

### I profili esistenti nell'app

Da `gui/mappa_pianificatore.py` riga 297:

```python
self.combo_profilo.addItems(["🚲 Gravel / Viaggio", "🛣️ Strada",
                              "🚵 MTB", "⚖️ Equilibrato"])
```

Oggi il worker mappa questi profili con una regola banale: se il nome
contiene "strada" usa `fastbike`, altrimenti `trekking`.

### La tabella di corrispondenza

| Profilo nell'app | Oggi (BRouter) | Proposto (GraphHopper) | Note |
|---|---|---|---|
| 🚲 Gravel / Viaggio | trekking | **`bike`** | privilegia ciclabili e strade tranquille |
| 🛣️ Strada | fastbike | **`racingbike`** | il più vicino: rifiuta sentieri e sterrato |
| 🚵 MTB | trekking | **`mtb`** | oggi finisce su trekking per caso |
| ⚖️ Equilibrato | trekking | **`bike`** + modello custom | da definire, vedi sotto |

Il profilo MTB è un **miglioramento reale**: oggi non ha un equivalente
vero, è un caso scoperto dalla regola "strada / non strada".

### Il profilo "Equilibrato" richiede una decisione

Non ha un equivalente in GraphHopper. Due strade:

| Opzione | Come | Pro | Contro |
|---|---|---|---|
| A. Mappare su `bike` | identico a Gravel | subito, zero rischio | perde il senso della voce di menu |
| B. Custom model | JSON dedicato | distingue davvero | va scritto e testato |

**Consiglio: opzione A nella prima migrazione**, valutando B in seguito.
A è un comportamento noto e collaudato; B introdurrebbe un modello non
verificato proprio mentre si cambia motore.

### Configurazione (`config.yml`)

Formato attuale (custom model, non flagEncoders):

```yaml
graphhopper:
  datareader.file: italy-latest.osm.pbf
  graph.location: graph-cache

  # SRTM: senza questo le quote sono tutte zero
  elevation: true
  elevation.cache_dir: srtm-cache
  graph.elevation: srtm

  profiles:
    - name: bike
      custom_model_files: [bike.json, bike_elevation.json]
    - name: racingbike
      custom_model_files: [racingbike.json, bike_elevation.json]
    - name: mtb
      custom_model_files: [mtb.json, bike_elevation.json]

  # Contraction Hierarchies: è QUI che nasce la velocità.
  # bike e racingbike vanno in CH; mtb no (CH su mtb è costoso e il
  # profilo serve poco: si lascia in modalità speed mode).
  profiles_ch:
    - profile: bike
    - profile: racingbike
```

**Nota sui CH:** la documentazione avverte che bike e racingbike **non**
sono in CH di default, perché la preparazione costa memoria. Proprio da
qui nasce il salto di prestazioni. Va verificato che i CH siano davvero
preparati: all'avvio GraphHopper stampa le statistiche, e vanno lette.

### Avvio

```bash
java -Xmx6g -jar graphhopper-web-11.1.jar config.yml
```

| Porta | Uso |
|---|---|
| 8989 | API routing (è quella che useremo) |
| 8990 | amministrazione |

Il server va su `localhost` e non va esposto: non è pensato per essere
pubblico così com'è.

---

## 4. Integrazione nel pianificatore

### Come funziona oggi

```
gui/mappa_worker.py :: PianificazionePercorsoWorker
    |- requests.get(BROUTER_URL, params={lonlats, profile, format: geojson})
    |     "- "lonlats": "lon,lat|lon,lat"   <- formato proprietario BRouter
    |- legge risposta -> features[0].geometry.coordinates
    |- passa a service/stats_service.py :: analizza_dati_rotta_brouter()
```

### Cosa cambia con GraphHopper

| Punto | BRouter | GraphHopper |
|---|---|---|
| Endpoint | `/brouter` | `/route` |
| URL | `127.0.0.1:17777` | `127.0.0.1:8989` |
| Punti | `lonlats=l,l;l,l` | `points=lat,lon;lat,lon` |
| Profilo | `trekking` / `fastbike` | `bike` / `racingbike` / `mtb` |
| Coordinate | `geometry.coordinates` | percorso dentro `paths[0]` |
| Distanza | `properties["track-length"]` (metri) | `paths[0].distance` (metri) |
| Tempo | `properties["total-time"]` (secondi) | `paths[0].time` (**millisecondi**) |
| Altimetria | terzo valore del punto | `elevation=true` |
| Superfici | `properties.messages` (tabella custom) | **`path_details=surface,track_type`** |

### Tre cose da non sottovalutare

**1. Ordine delle coordinate invertito.**
BRouter usa `lon,lat`, GraphHopper usa `lat,lon`. Un errore qui non
produce un errore: produce percorsi in Antartide, con numeri plausibili.
Le tabelle sopra servono proprio a non sbagliare.

**2. Le superfici richiedono codice nuovo.**
È il punto più serio. Oggi `analizza_dati_rotta_brouter` legge la tabella
`properties.messages` con le colonne `distance` e `waytags`, e classifica in
Asfalto / Pista ciclabile / Sentiero / Sterrato.

**GraphHopper non ha `messages`.** Va richiesto esplicitamente:

```
path_details=surface,track_type
```

che restituisce segmenti con `distance`, `surface`, `track_type`. La
classificazione esistente va riscritta per leggere `track_type` al posto di
`waytags`. Senza questo, la barra "Superfici del percorso" resta grigia e
l'utente perde una funzionalità che ha oggi.

**3. Le unità del tempo sono diverse.**
`time` è in millisecondi, `total-time` in secondi. Un errore dà
"velocità media 3600 km/h": si nota subito, ma conviene evitarlo.

### L'architettura che consiglio

Oggi l'analisi dei dati di rotta conosce il formato BRouter e la GUI non
sa nulla del motore. La migrazione è l'occasione per separare le due cose:

| Livello | Responsabilità |
|---|---|
| `service/routing_*.py` | parla col motore, restituisce dati normalizzati |
| `service/stats_service.py` | calcola KPI e superfici da dati normalizzati |
| `gui/` | non sa quale motore è sotto |

Con un **formato interno unico**, sostituire il motore in futuro non
toccherebbe né la GUI né le statistiche. Un solo contratto, due
## 5. Piano a sotto-fasi

Ogni sotto-fase è autonoma, verificabile e reversibile. Il pianificatore
continua a funzionare in ogni punto.

### 6.0 · Prova di fattibilità (mezza giornata)

**Obiettivo:** rispondere a due domande sì/no prima di scrivere codice.

| Attività | Durata |
|---|---|
| Avviare GH 11.1 con Java 25 su area minuscola | 30 min |
| Se Java 25 fallisce, installare JDK 21 e riprovare | 30 min |
| Misurare i tempi reali su Napoli con CH attivi | 15 min |
| Confronto tempi BRouter vs GraphHopper | 15 min |

**Criterio di uscita:** GraphHopper risponde e Napoli si calcola in meno di
1 secondo. **Se qui si fallisce, il progetto si ferma** e si resta con
BRouter. Costa un pomeriggio e decide tutto il resto.

> Questa sotto-fase ripete esattamente la verifica che nella 5.1 ho
> dichiarato "non benchmarkata" e che ha prodotto il timeout di Napoli.
> Le misure vanno prese prima, non dopo.

### 6.1 · Installazione e dati

Import dell'Italia, verifica dell'altimetria SRTM, profili bike e
racingbike con CH preparati. Nessun codice Python.

**Verifica:** tre richieste dirette a `localhost:8989` con `curl` restituiscono
tracciati validi con quote non nulle.

### 6.2 · Adapter GraphHopper

Nuovo modulo `service/routing_graphhopper.py` che parla con GH e restituisce
**il formato interno normalizzato**. Parallelamente un adapter BRouter che
produce lo stesso formato.

**Verifica:** entrambi producono lo stesso tipo di dato; un test li confronta
sullo stesso percorso. BRouter resta il default.

### 6.3 · Statistiche su formato normalizzato

Riscrivere l'analisi dei dati di rotta per leggere il formato interno,
includendo le superfici da `track_type`.

**Verifica:** la barra superfici mostra Asfalto / Pista / Sterrato come oggi.
Test con valori noti, senza dipendere dalla rete.

### 6.4 · Dietro un interruttore

`ROUTING_ENGINE = "brouter" | "graphhopper"` in `service/config.py`. La GUI
non cambia: sceglie il motore a seconda del flag.

**Verifica:** l'app funziona identica in entrambe le modalità.

### 6.5 · Confronto su percorsi reali

Stessi percorsi, due motori, tabella affiancata: distanza, tempo, quote,
superfici. Serve a capire **quanto diversi sono i percorsi**, non solo quanto
sono veloci: `racingbike` evita il sentiero che `trekking` accettava. Sono
scelte legittime, ma l'utente deve saperlo.

### 6.6 · GraphHopper come default

Solo dopo che 6.5 ha mostrato risultati buoni. BRouter resta nel codice come
fallback.

### 6.7 · Rimozione di BRouter (facoltativa, non subito)

Solo a distanza di mesi e con il motore nuovo stabile. **Consigliata una
decisione separata**: tenere il codice morto costa poco e compra la
possibilità di tornare indietro.

### Riepilogo

| Sotto-fase | Rischio | Tempo | App funziona |
|---|---|---|---|
| 6.0 fattibilità | nullo | mezzo giorno | sì |
| 6.1 installazione | basso | 1 giorno | sì |
| 6.2 adapter | basso | 2 giorni | sì |
| 6.3 statistiche | **medio** | 2 giorni | sì |
| 6.4 interruttore | basso | 1 giorno | sì |
| 6.5 confronto | nullo | 1 giorno | sì |
| 6.6 default | medio | 1 giorno | sì |

Totale realistico: **8-9 giorni** di lavoro effettivo, senza toccare la GUI.

---

## 6. Rischi e mitigazioni

| # | Rischio | Probabilità | Impatto | Mitigazione |
|---|---|---|---|---|
| 1 | **Java 25 incompatibile** con GH 11.1 | media | alto | 6.0 lo verifica per prima; JDK 21 in parallelo |
| 2 | **Superfici non funzionanti** senza `path_details` | **certa** | alto | `track_type` esplicito in 6.3 + test con valori noti |
| 3 | Coordinate invertite (lat/lon) | media | alto | una sola funzione di conversione, test dedicato |
| 4 | CH non preparati: tempi deludenti | media | alto | leggere le statistiche all'avvio; `profiles_ch` esplicito |
| 5 | Percorsi diversi da BRouter | **certa** | medio | è atteso: confrontare in 6.5 e spiegare all'utente |
| 6 | Import dell'Italia fallisce | bassa | medio | 1,5 GB di PBF, 5-15 min di import, recuperabile |
| 7 | Quote a zero (SRTM mancante) | media | medio | SRTM nella 6.1 come requisito, verifica esplicita |
| 8 | Modelli JSON sbagliati | media | medio | partire dai modelli built-in, non scriverli da zero |
| 9 | Profilo MTB più permissivo di prima | alta | basso | era trekking per caso: miglioramento, ma da comunicare |
| 10 | Consumo RAM durante l'import | bassa | basso | 15,6 GB disponibili, `-Xmx6g` basta |

### Il rischio numero 2 è quello vero

Gli altri si scoprono con un test. La perdita delle superfici si scopre
guardando l'app, e a quel punto è un difetto visibile. Per questo la 6.3 ha
test con valori noti e non dipende dalla rete.

### Sul rischio 5, una nota di equità

BRouter e GraphHopper produrranno percorsi diversi. Non è un difetto di
nessuno dei due: sono modelli diversi. `racingbike` rifiuta i sentieri,
`trekking` li accetta. L'utente deve poter scegliere, e va informato del
cambio. Presentare GraphHopper come "più veloce e basta" sarebbe disonesto:
è anche più severo, in meglio per il profilo scelto.

---

implementazioni: BRouter (durante) e GraphHopper (dopo). Il rollback di cui
al punto 7 è gratis.
## 7. Rollback

### Principio

Il rollback deve essere **una riga di configurazione**, non un'operazione.
Da qui la scelta dell'adapter nella 6.2: due motori, stesso contratto.

```python
# service/config.py
ROUTING_ENGINE = "graphhopper"   # oppure "brouter"
```

Cambiare la riga e riavviare l'app. Nessuna modifica al database, nessuna
perdita di dati: le tappe salvate contengono il GPX, non il motore che le ha
prodotte.

### Quando fare rollback

| Sintomo | Azione |
|---|---|
| Percorsi peggiori o assurdi | rollback immediato |
| Superfici non più disponibili | rollback (bug 6.3) |
| Tempi non migliorati | rollback (CH non preparati: problema 6.1) |
| Crash o errori ricorrenti | rollback |
| Percorsi diversi dagli attesi | **non è rollback**: è 6.5, va comunicato |

L'ultima riga è la più importante: una differenza di percorso non è un
guasto. Se si fa rollback per quello, si butta via un miglioramento reale.

### Come si esegue

1. `ROUTING_ENGINE = "brouter"` in `service/config.py`
2. Riavvio dell'app
3. BRouter riattivo su porta 17777 (era già lì, non si tocca)
4. Verifica su tre percorsi noti

### Rollback dell'ambiente

Se GraphHopper consuma troppe risorse, si termina il processo Java e si
cancella `graph-cache`. **BRouter non è stato toccato**: continua a
funzionare perché è un servizio separato, su un'altra porta, con un'altra
cartella.

### Cosa NON fare

| Azione | Perché no |
|---|---|
| Cancellare BRouter insieme a GraphHopper | distrugge il fallback |
| Migrare i dati su GraphHopper | le tappe sono GPX, il motore non le tocca |
| Rimuovere il codice BRouter "per fare pulizia" | il rollback diventa un lavoro di settimane |

---

## Cosa non so

Onesto su quello che **non** ho verificato:

1. **I tempi di GraphHopper sono attese, non misure.** Vengono dalla
   documentazione sul funzionamento di CH. La 6.0 li misura. Se reali
   fossero 3 secondi su Napoli, la migrazione varrebbe comunque (il salto
   da 84 s a 3 s resta enorme), ma il numero da comunicare sarebbe un altro.

2. **Non ho verificato se GH 11.1 gira su Java 25.** Il progetto documenta
   17/21. È la domanda aperta numero uno.

3. **Non ho verificato la qualità dei percorsi.** Solo la velocità. Due
   motori possono essere veloci e diversi; la 6.5 serve a misurarlo.

4. **Il formato esatto dei `path_details`** va letto nella documentazione
   della 11.1 al momento dell'implementazione. Ho indicato il parametro ma
   non ho verificato la struttura della risposta nel dettaglio.

5. **Il modello JSON per MTB** va valutato: potrebbe servire un custom
   model dedicato.

6. **Le dimensioni indicate** per PBF e grafo sono stime di ordine di
   grandezza, non misurate.

---

## Conclusione

La migrazione è **fattibile e consigliata**, con un ordine che mette le
verifiche prima del codice:

1. Verificare che GraphHopper giri e sia veloce (6.0)
2. Installare dati e profili (6.1)
3. Costruire l'adapter con un formato interno unico (6.2, 6.3)
4. Attivare dietro interruttore e confrontare (6.4, 6.5)

Le due decisioni che contano di più:

- **Il formato interno normalizzato**, che rende il rollback gratuito e la
  prossima migrazione banale.
- **La sotto-fase 6.0 prima di tutto il resto**, che evita di costruire
  settimane di lavoro su una premessa non verificata. È esattamente la lezione
  della sotto-fase 5.1.

Nessuna modifica al codice è stata fatta.
