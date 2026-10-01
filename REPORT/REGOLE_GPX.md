# Regole per il calcolo dei dati GPX

**Versione:** 1.0
**Data:** 2026-10-01
**Stato:** Attivo

Questo documento definisce le **regole comuni** che tutti i calcoli sui GPX
devono rispettare. È il contratto di riferimento per:
- Calcolo della distanza
- Calcolo del dislivello e della pendenza
- Calcolo della distanza dalla costa
- Estrazione della geometria per la mappa
- Qualsiasi altro calcolo futuro sui GPX

Nessun calcolo può violare queste regole. Se serve una nuova regola, va
aggiunta qui prima di essere implementata.

---

## 1. Un GPX = una traccia

**Regola**: nel nostro progetto, un file GPX rappresenta **una sola traccia**,
con un punto di partenza (A) e un punto di arrivo (B).

**Caso anomalo**: se un file GPX contiene **più di una traccia** (`<trk>`
multipli), è considerato un **file anomalo**. Va segnalato all'utente, non
gestito automaticamente.

**Motivo**: il nostro flusso di lavoro (dashboard, pianificatore, audit) è
progettato per una traccia per file. Gestire più tracce automaticamente
creerebbe ambiguità su cosa contare e come.

**Eccezione**: i file GPX possono contenere **più segmenti** (`<trkseg>`) della
stessa traccia. Questo è normale (perdita di segnale GPS) e va gestito secondo
la regola 2.

---

## 2. I segmenti si tengono separati

**Regola**: se una traccia contiene **più segmenti** (`<trkseg>`), la distanza
si calcola **solo all'interno di ogni segmento**. La distanza tra la fine di
un segmento e l'inizio del successivo **non va contata**.

**Motivo**: la bicicletta non vola. Se c'è un buco tra due segmenti, significa
che il GPS ha perso il segnale (galleria, sottopasso, bosco fitto), non che
l'utente ha pedalato in linea retta.

**Gestione del gap**: il gap tra segmenti è un dato separato. È già gestito
dalla sezione **Audit**, che segnala i gap e permette di "risolverli" creando
un raccordo.

**Conseguenza sui numeri**: un GPX con segmenti separati avrà una **distanza
totale inferiore** rispetto a un GPX con la stessa traccia ma senza interruzioni.
Questo è corretto: la distanza rappresenta solo ciò che è stato effettivamente
pedalato.

---

## 3. Punti duplicati o ravvicinati

**Regola**: i punti consecutivi con distanza **inferiore a 1 metro** vengono
considerati **duplicati** e scartati dal calcolo della distanza.

**Motivo**: il GPS registra frequentemente punti identici o quasi identici
(quando l'utente è fermo, o per rumore del segnale). Se non vengono scartati,
gonfiano artificialmente la distanza con valori prossimi a zero.

**Soglia**: 1 metro. Sotto questa soglia, il contributo alla distanza è
trascurabile e il punto è considerato rumore.

**Nota**: i punti duplicati **non vengono eliminati dal file GPX**. Sono solo
scartati dal calcolo della distanza. Il file originale resta intatto.

---

## 4. Quote mancanti o inaffidabili

**Regola**: le quote altimetriche vengono trattate come **dato opzionale**.

- **Distanza**: si calcola **sempre**, indipendentemente dalla presenza di quote.
- **Dislivello e pendenza**: si calcolano **solo se le quote sono presenti e
  credibili**. Se mancano o sono inaffidabili, il dato è segnato come
  "non disponibile" per quel tratto.

**Motivo**: il problema delle quote GPS è noto a livello globale. Le quote
barometriche e GPS sono spesso imprecise, specialmente all'inizio della
registrazione o con VDOP (Vertical Dilution of Precision) scadente. App come
Strava hanno costruito basemap di altitudini raccolte dalla community per
supplire a questo problema.

**Non si interpolano quote da fonti esterne** (Google Earth, SRTM, ecc.) in
modo automatico. Se in futuro si vorrà farlo, sarà una scelta esplicita e
documentata.

**Conseguenza sui numeri**: una tappa con quote mancanti mostrerà "dislivello
non disponibile" invece di un valore inventato. Questo è corretto: meglio un
dato assente che un dato falso.

---

## 5. Stati della tappa durante il precalcolo

Ogni tappa ha uno **stato di precalcolo** che indica a che punto è l'analisi
dei suoi dati. Gli stati sono:

| Stato | Significato |
|---|---|
| `NON_CALCOLATO` | La tappa è stata importata, ma il precalcolo non è ancora iniziato |
| `IN_CODA` | Il precalcolo è stato richiesto, ma non è ancora partito |
| `IN_CORSO` | Il precalcolo è in esecuzione |
| `PARZIALE` | Alcuni calcoli sono completati, altri no (es. distanza sì, costa no) |
| `COMPLETO` | Tutti i calcoli richiesti sono completati con successo |
| `ERRORE` | Il precalcolo è fallito (con messaggio di errore specifico) |

**Nota**: lo stato è **globale** per la tappa, ma ogni calcolo ha il suo
sotto-stato. Una tappa può essere `PARZIALE` perché la distanza è pronta ma la
costa no. Questo è normale e va mostrato all'utente in modo chiaro.

---

## 6. Distanza: come si calcola

**Formula**: la distanza è la **somma delle distanze geodetiche** tra punti
consecutivi, calcolate con la formula di Haversine (o equivalente).

**Vincoli**:
- Non si somma la distanza tra segmenti separati (regola 2)
- Non si contano i punti duplicati (regola 3)
- Si usa la distanza geodetica, non la distanza euclidea in gradi

**Precisione**: il risultato va salvato con **almeno 3 decimali** (metri).
L'arrotondamento a 2 decimali (attuale) è insufficiente per la certificazione.

---

## 7. Dislivello e pendenza: come si calcolano

**Dislivello positivo/negativo**: somma dei dislivelli positivi e negativi tra
punti consecutivi con quota valida.

**Pendenza media**: calcolata come **dislivello / distanza effettiva** tra i
punti, non con un passo fisso. Il metodo attuale (passo fisso di 50 metri) è
impreciso e va sostituito.

**Pendenza massima**: da definire in una versione futura. Per ora, si calcola
solo la pendenza media.

**Filtro del rumore**: le quote anomale (salti improvvisi) vanno filtrate. La
soglia e il metodo di filtro vanno definiti prima dell'implementazione.

---

## 8. Geometria per la mappa

**Regola**: la geometria originale (tutti i punti del GPX) va **conservata
intatta**. Per la visualizzazione sulla mappa, si genera una **versione
semplificata** separata, che non viene mai usata per statistiche o
certificazione.

**Semplificazione**: si usa un algoritmo standard (es. Ramer-Douglas-Peucker)
con tolleranza variabile in base al livello di zoom. La versione semplificata
è un **derivato**, non sostituisce l'originale.

**Motivo**: il GPX originale è la **fonte probatoria** (per il Guinness e per
qualsiasi verifica futura). La geometria semplificata è solo per il rendering.

---

## 9. Invalidazione

Ogni risultato di calcolo è valido **solo se** i suoi input non sono cambiati:

- **Hash del GPX**: SHA-256 dei byte del file. Se cambia, tutti i calcoli
  derivati vanno rifatti.
- **Versione dell'algoritmo**: se cambia il metodo di calcolo (es. nuova
  formula di distanza), i risultati vanno rifatti.
- **Versione delle fonti esterne**: se cambiano le mappe offline o il dataset
  costiero, i calcoli dipendenti vanno rifatti.

**Regola**: un risultato senza queste informazioni è considerato **non
verificabile** e va ricalcolato.

---

## 10. Note finali

Queste regole sono **vincolanti** per tutti i calcoli futuri. Se un calcolo
non può rispettarle, va discussa una modifica esplicita a questo documento.

Le regole sono state definite il **2026-10-01** e saranno aggiornate solo
quando emergeranno nuovi requisiti (es. protocollo Guinness).

---

*Documento di riferimento per `analisi_profonda.py`, `tappa_analisi` e tutti
i servizi di precalcolo.*