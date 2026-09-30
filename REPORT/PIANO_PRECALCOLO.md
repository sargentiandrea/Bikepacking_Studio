# Piano di precalcolo dei dati delle tappe

## Scopo e stato delle informazioni

Questo documento propone un'architettura per calcolare i dati una sola volta
quando un GPX entra o cambia nel progetto e renderli poi disponibili alle
pagine tramite SQLite. È un piano, non una modifica del codice o del database.

Le proposte si basano sul brief e sullo schema attuali e sui flussi verificati
in `gui/dashboard.py`, `gui/mappa.py`, `service/stats_service.py`,
`service/superfici_service.py`, `service/audit_service.py`,
`service/clima_service.py` e `service/geocodifica_offline_service.py`.
Le decisioni non verificabili dai file disponibili sono indicate come
**da confermare**.

### Situazione attuale rilevante

- `tappe` contiene 983 righe e ha già `distanza_km`, coordinate di partenza e
  arrivo, file, progetto e sequenza. L'importazione dalla dashboard calcola
  già una distanza Haversine, ma arrotonda a due decimali e non salva gli altri
  KPI.
- `service/stats_service.py` rilegge i file GPX per dislivello e pendenza.
  La pendenza media attuale usa un passo fisso di 50 metri per punto, non la
  distanza effettiva tra i punti; va quindi definita e validata prima di
  considerarla un dato attendibile.
- La ripartizione costiera attuale campiona circa 40 punti per tappa, legge i
  GPX durante l'apertura delle statistiche e distribuisce i km in quattro
  fasce. Non corrisponde al requisito futuro di 5000+ campioni né a una
  certificazione.
- `superfici_tappa` contiene già JSON con superfici, copertura e tratti
  probabilmente vietati. La cache non registra però l'hash del GPX né la
  revisione delle mappe usate, quindi non può stabilire con certezza se sia
  ancora valida.
- `cache_nomi_luoghi` è una cache globale basata su coordinate arrotondate.
  La risoluzione è offline e usa le mappe locali; un risultato vuoto può
  significare che la località non è disponibile nelle mappe installate.
- L'apertura della mappa rilegge i GPX per ricostruire la geometria completa.
  Il pianificatore riceve già da BRouter una rotta e alcune statistiche, ma
  l'anteprima non è ancora una garanzia che tutti i risultati siano
  persistiti in un unico flusso di precalcolo.
- L'audit delle strade vietate legge la cache delle superfici. Clima/stagioni
  usa soprattutto distanze e coordinate già in `tappe`, mentre la pagina
  statistiche ricalcola alcuni KPI dai GPX.

---

## 1. Schema del database proposto

La proposta riusa `tappe`, `superfici_tappa` e `cache_nomi_luoghi`, aggiungendo
metadati di versione e alcune tabelle per risultati distinti. I dati derivati
non andrebbero aggiunti tutti come colonne a `tappe`: una riga analitica
separata rende più chiari stato, provenienza e ricalcolo.

### Tabelle da aggiungere

| Tabella | Colonne principali proposte | Contenuto e collegamenti |
|---|---|---|
| `tappa_analisi` | `tappa_id INTEGER PRIMARY KEY`; `gpx_sha256 TEXT NOT NULL`; `versione_algoritmi TEXT NOT NULL`; `distanza_km REAL`; `dislivello_pos_m REAL`; `dislivello_neg_m REAL`; `quota_min_m REAL`; `quota_max_m REAL`; `pendenza_media_pct REAL`; `pendenza_max_pct REAL`; `bbox_min_lon REAL`; `bbox_min_lat REAL`; `bbox_max_lon REAL`; `bbox_max_lat REAL`; `stato TEXT NOT NULL`; `errore TEXT`; `aggiornato_il TEXT` | Risultato sintetico e stato dell'analisi della singola tappa. PK/FK verso `tappe.id`; un record per tappa. Distinguere `NON_CALCOLATO`, `IN_CODA`, `IN_CORSO`, `PARZIALE`, `COMPLETO`, `ERRORE`. |
| `tappa_segmenti` | `tappa_id INTEGER`; `track_index INTEGER`; `segment_index INTEGER`; `punti INTEGER`; `distanza_km REAL`; `dislivello_pos_m REAL`; `dislivello_neg_m REAL`; `quota_min_m REAL`; `quota_max_m REAL`; `versione_algoritmi TEXT`; PK composta (`tappa_id`, `track_index`, `segment_index`) | Misure per ogni segmento GPX, senza fondere pause o gap tra segmenti. FK verso `tappe.id`. Necessaria se la certificazione considera singoli segmenti o richiede tracciabilità delle distanze. |
| `tappa_costa_campioni` | `tappa_id INTEGER`; `campione_index INTEGER`; `track_index INTEGER`; `segment_index INTEGER`; `lat REAL`; `lon REAL`; `distanza_progressiva_m REAL`; `distanza_costa_m REAL`; `fascia_id INTEGER`; `punto_costa_lon REAL`; `punto_costa_lat REAL`; `fonte_costa_versione TEXT`; `metodo_versione TEXT`; PK composta (`tappa_id`, `campione_index`) | Campioni costieri verificabili: coordinate originali o interpolabili, distanza lungo traccia, distanza dalla costa, fascia e punto costiero più vicino. FK verso `tappe.id`; indice su `(tappa_id, campione_index)` e, se serve ricerca geografica, un indice spaziale scelto dopo un prototipo. |
| `tappa_geometrie` | `tappa_id INTEGER`; `gpx_sha256 TEXT`; `profilo_zoom INTEGER`; `formato TEXT`; `geometria_compressa BLOB`; `numero_punti_originali INTEGER`; `numero_punti_semplificati INTEGER`; `algoritmo_versione TEXT`; PK composta (`tappa_id`, `profilo_zoom`) | Geometrie semplificate della mappa, conservate in forma compatta. FK verso `tappe.id`. Si possono avere profili distinti per panoramica e dettaglio oppure un solo profilo iniziale da validare. |
| `precalcolo_lavori` | `id INTEGER PRIMARY KEY`; `tappa_id INTEGER`; `tipo TEXT`; `gpx_sha256 TEXT`; `versione_algoritmi TEXT`; `stato TEXT`; `progresso INTEGER`; `tentativi INTEGER DEFAULT 0`; `errore TEXT`; `avviato_il TEXT`; `aggiornato_il TEXT` | Coda persistente e riprendibile. FK verso `tappe.id`; UNIQUE (`tappa_id`, `tipo`, `gpx_sha256`, `versione_algoritmi`) per evitare lavori duplicati. |
| `versioni_dataset` | `id INTEGER PRIMARY KEY`; `tipo TEXT UNIQUE`; `identificativo TEXT`; `sha256 TEXT`; `percorso_locale TEXT`; `aggiornato_il TEXT`; `metadati_json TEXT` | Versioni di dataset condivisi, per esempio Natural Earth o ciascun file MBTiles installato. Consente di confrontare il risultato salvato con la fonte del calcolo. |
| `progetto_analisi` | `id_progetto INTEGER PRIMARY KEY`; `versione_ordine INTEGER`; `distanza_totale_km REAL`; `distanza_progressiva_versione TEXT`; `stato TEXT`; `aggiornato_il TEXT` | Aggregati di progetto e versione dell'ordine delle tappe. FK verso `progetti.id`. La distanza progressiva dipende dall'ordine del progetto, non soltanto dal GPX. |

**Vincoli comuni:** FK con `ON DELETE CASCADE` solo dove la cancellazione della
tappa deve eliminare senza ambiguità i derivati; CHECK sugli stati; indici su
`tappe(id_progetto, sequenza)`, `precalcolo_lavori(stato, tipo)` e sulle
colonne usate dai join. Il comportamento delle FK va verificato perché SQLite
richiede che `PRAGMA foreign_keys=ON` sia attivo per ogni connessione. Le
migrazioni dovranno essere versionate e precedute da backup del database.

### Modifiche alle tabelle esistenti

| Tabella | Modifica suggerita | Motivo |
|---|---|---|
| `tappe` | Aggiungere `gpx_sha256 TEXT`, `precalcolo_stato TEXT` e `precalcolo_versione TEXT`, oppure mantenere questi campi solo in `tappa_analisi` | La prima opzione semplifica filtri e interfaccia; la seconda evita duplicare lo stato. Scegliere una sola fonte autorevole. `nome_file` resta il riferimento al file, non la sua identità. |
| `superfici_tappa` | Aggiungere `gpx_sha256 TEXT`, `versione_algoritmo TEXT`, `versione_mappe TEXT`, `copertura_percentuale REAL` (se non già dentro `dati_json`) | La cache esistente resta utilizzabile, ma può essere validata e invalidata in modo deterministico. |
| `cache_nomi_luoghi` | Aggiungere `versione_mappe TEXT` oppure lasciare la cache globale e creare un'associazione specifica tappa-punto | Il nome dipende dalle mappe place installate. La chiave per coordinate può continuare a riusare risultati, ma va chiarito come distinguere risultati non trovati da risultati trovati. |
| `tappe` o nuova tabella dedicata | Aggiungere `distanza_progressiva_inizio_km` e `distanza_progressiva_fine_km` solo se serve lettura immediata per singola tappa | Questi valori dipendono da sequenza/stato e vanno invalidati quando l'ordine cambia. In alternativa restano un'aggregazione SQL o in `progetto_analisi`. |

**Raccomandazione:** introdurre prima `tappa_analisi` come unica fonte per i KPI
per tappa. Lasciare in `tappe.distanza_km` un periodo di compatibilità, poi
decidere se rimuoverne l'uso solo dopo aver migrato tutte le pagine.

### Dati e derivazioni

- **Distanza per tappa:** somma geodetica delle distanze consecutive all'interno
  di ciascun segmento GPX. Non sommare la distanza tra due segmenti separati.
- **Distanza progressiva:** somma delle tappe in sequenza secondo la regola
  concordata per tappe attive, sospese e trasferimenti. È un dato del progetto,
  non intrinseco al file.
- **Distanza per segmento:** distanza per ogni `<trk>/<trkseg>` GPX. Se
  “segmento Guinness” significa invece una suddivisione certificativa definita
  dall'utente, la tabella dovrà riflettere quella diversa definizione.
- **Altimetria e pendenze:** salvare risultati sintetici e versione del metodo.
  Definire come trattare quote mancanti, valori anomali, rumore del GPS,
  distanze quasi nulle e filtri di smoothing.
- **Costa:** salvare il riepilogo aggregato in `tappa_analisi` o una tabella
  `tappa_costa_riepilogo`, mantenendo i campioni dettagliati in
  `tappa_costa_campioni`.
- **Superfici e divieti:** mantenere il JSON attuale in `superfici_tappa`, ma
  versionarlo. Tenere i tratti vietati con motivazione e copertura, non solo
  una percentuale aggregata.
- **Nomi:** partenza e arrivo sono coordinate della tappa; eventuali tappe
  intermedie vanno modellate quando esiste un'entità che le identifica.
  Conservare nome, coordinate, fonte e versione mappa usata.
- **Geometria semplificata:** conservare originale immutato nel GPX; generare
  una copia derivata per disegno, mai usarla per statistiche o certificazione.

### Diagramma testuale delle relazioni

```text
progetti 1 ─── N tappe
   │                ├── 1 tappa_analisi
   │                ├── N tappa_segmenti
   │                ├── N tappa_costa_campioni
   │                ├── N tappa_geometrie (profili di zoom)
   │                ├── 0..1 superfici_tappa (cache esistente, versionata)
   │                └── N precalcolo_lavori
   └── 1 progetto_analisi (aggregati e versione ordine)

versioni_dataset ─── versiona le mappe offline e la fonte costiera
cache_nomi_luoghi ─── cache globale per coordinate/versione delle mappe
```

---

## 2. Flusso di precalcolo

### Importazione manuale dalla dashboard

1. Copiare il GPX nella cartella gestita dall'app e verificare che la copia
   sia riuscita. Calcolare SHA-256 sul file effettivamente conservato, non sul
   solo nome o sul file temporaneo selezionato.
2. Validare GPX e coordinate, rilevare track e segmenti senza unirli
   implicitamente, leggere una sola volta punti e quote.
3. Creare la riga `tappe` e registrare `tappa_analisi` con stato `IN_CODA`
   nella stessa transazione SQLite. Assegnare ID prima di avviare i lavori.
4. Mettere in coda i calcoli locali: distanza, progressiva (dopo aver
   aggiornato l'ordine), elevazione, pendenza e geometria semplificata.
5. Avviare costa, superfici/divieti e nomi in base alla disponibilità delle
   rispettive fonti locali. I calcoli pesanti devono essere worker in
   background, non sul thread dell'interfaccia.
6. Salvare ciascun risultato e la sua versione in transazioni brevi. Completare
   un risultato non deve dipendere dal completamento degli altri: un problema
   con un `.mbtiles` non deve cancellare la distanza già calcolata.
7. Aggiornare gli aggregati del progetto e notificare la GUI con stato di
   avanzamento; le pagine leggono i record DB e mostrano chiaramente dati
   mancanti o in aggiornamento.

### GPX creato dal pianificatore mappa

Il worker BRouter fornisce già coordinate e statistiche provvisorie. Quando la
tappa viene salvata, il GPX viene scritto e inserito/aggiornato in SQLite.
Il flusso proposto calcola SHA-256 sul GPX scritto, registra la tappa e passa
al medesimo servizio di precalcolo dell'import manuale. Le statistiche BRouter
possono essere conservate come provenienza o confronto, ma non sostituiscono le
metriche calcolate con la stessa regola usata per GPX esterni.

### GPX modificato o sostituito

Calcolare il nuovo hash. Se è identico al precedente e le versioni degli
algoritmi e delle fonti non sono cambiate, non ricalcolare. Se è diverso,
registrare l'invalidazione e mettere in coda i derivati dipendenti. Non
mostrare i vecchi risultati come aggiornati durante l'elaborazione: marcarli
`OBSOLETO` o conservarli con il vecchio hash fino al commit del nuovo risultato.

### Aggiornamento delle mappe offline

`MapManagerService` scarica oggi i `.mbtiles` e li sostituisce sul disco.
Prima del completamento di un aggiornamento, acquisire versione/hash del file
nuovo e registrare una nuova revisione solo quando il download è completo e
valido. Invalidare soltanto analisi che dipendono dai layer modificati:

- `transportation` → superfici, copertura e tratti probabilmente vietati;
- `place` → nuovi nomi o ricalcolo esplicito dei nomi non trovati;
- altri layer cartografici → geometria base solo se quella geometria usa tali
  layer, non la geometria GPX semplificata.

Le cache tile in memoria dei servizi devono essere ricreate o versionate.
Un update MBTiles non deve invalidare distanza, elevazione o progressiva.

### Moduli responsabili proposti

| Responsabilità | Punto d'integrazione consigliato |
|---|---|
| Coordinamento e stato dei lavori | Nuovo `service/precalcolo_service.py` (da progettare/implementare), indipendente dalla GUI |
| Import GPX | `gui/dashboard.py` chiama il servizio dopo import e commit; in seguito unificare le copie della logica GPX |
| GPX pianificato/sostituito | Callback di salvataggio nel pianificatore in `gui/mappa.py`, poi stesso servizio |
| Metriche e segmenti | Nuovo servizio puro, per esempio `service/gpx_metrics_service.py`, testabile senza PySide6 |
| Costa | Evoluzione di `service/stats_service.py` o estrazione in `service/coastline_service.py` |
| Superfici/divieti | `service/superfici_service.py`, estendendo la cache esistente con hash e revisione mappe |
| Nomi luoghi | `service/geocodifica_offline_service.py`, legato alla versione delle mappe |
| Geometria semplificata | Nuovo servizio puro di geometria; la mappa legge la geometria salvata e non apre il GPX |
| Schermata di avanzamento | GUI/dashboard, con segnali dei worker; SQLite resta la fonte persistente dello stato |

---

## 3. Invalidazione intelligente

Ogni risultato deve registrare input e metodo che l'hanno prodotto. Una cache
è valida solo se coincidono: hash del GPX, versione algoritmo, versione delle
fonti esterne/locali necessarie e parametri di calcolo.

### Tabella "Se cambia X, ricalcola Y"

| Evento o modifica | Dati da invalidare/aggiornare | Dati da conservare |
|---|---|---|
| File GPX sostituito o contenuto modificato | Distanza tappa e segmenti, dislivelli, quote, pendenze, costa, superfici/divieti, nomi se cambiano le coordinate, geometrie; progressiva e aggregati del progetto | Dati di altre tappe non coinvolte |
| Solo nome del file | Riferimento visuale e metadati; verificare collisioni/duplicati. Non invalidare misure se l'hash è uguale | Tutti i calcoli con input invariato |
| Sequenza tappe cambiata | Distanza progressiva e statistiche aggregate dipendenti dall'ordine; audit dei gap e dati di progetto | Analisi per-tappa, costa, superfici, geometria |
| Stato attiva/sospesa o ruolo modificato | Totali e progressiva solo secondo le regole del progetto; audit/allarmi correlati | Geometria e misure intrinseche al GPX |
| Blocco della tappa modificato | Aggregati per blocco e pianificazione climatica stagionale | Analisi per-tappa che non dipende dal blocco |
| Mappa MBTiles transportation aggiornata | Superfici, copertura e tratti vietati nelle zone coperte dalla mappa interessata | Distanza, altimetria, costa Natural Earth e geometria GPX |
| Mappa MBTiles place aggiornata | Nomi dei punti coperti o precedentemente non trovati, secondo politica di refresh | Metriche numeriche |
| Dataset costiero o metodo geodetico aggiornato | Tutte le distanze costiere e distribuzioni in fascia | Altre metriche |
| Algoritmo distanza/altimetria/pendenza aggiornato | Solo i risultati prodotti da quell'algoritmo, poi aggregati dipendenti | Risultati di altri servizi |
| Semplificazione o profilo zoom aggiornato | `tappa_geometrie` | GPX originale e metriche precise |
| Luogo manualmente corretto dall'utente | Nome/override e relative schermate | Coordinate e altre metriche |
| Trasferimento aggiunto, eliminato o spostato | Inquadratura/aggregati di progetto e audit di continuità; non le metriche GPX delle tappe | Analisi per-tappa non coinvolte |

### Versioni da registrare

- **Input GPX:** SHA-256 dei byte del file conservato; dimensione e data file
  possono essere metadati diagnostici, ma non sostituiscono l'hash.
- **Algoritmi:** identificatore esplicito per metrica, per esempio
  `distanza-v1`, `pendenza-v1`, `semplificazione-v1`. Aggiornare la versione
  solo quando cambia il significato o il calcolo.
- **Mappe:** hash SHA-256 calcolato al download/validazione per ogni MBTiles;
  non ricalcolare il checksum completo per ogni tappa.
- **Costa:** fonte, release/data, checksum del file, CRS e versione del
  procedimento di misura. La versione Natural Earth da sola non è una
  garanzia di accuratezza certificativa.
- **Campionamento:** versione e parametri (passo, numero minimo, regole
  d'interpolazione), memorizzati nei metadati di calcolo.

### Esempio: sostituzione di un GPX

1. Il sistema importa il nuovo contenuto e calcola il suo SHA-256.
2. Confronta l'hash con quello memorizzato. Se coincide e tutti i metodi/fonti
   sono alle versioni richieste, mantiene i risultati.
3. Se differisce, marca come obsoleti i risultati derivati dalla vecchia
   versione e crea i lavori richiesti per il nuovo hash.
4. Aggiorna in una transazione il file associato e gli estremi nel record
   `tappe`; registra lo stato `IN_CODA`.
5. I worker calcolano e salvano i moduli indipendenti. Ogni risultato porta
   l'hash nuovo; un worker tardivo con hash vecchio non può sovrascriverlo.
6. Aggiorna progressiva, aggregati e audit dopo che la distanza della tappa è
   valida. Se le mappe richieste non sono presenti, salva il dato come non
   disponibile/non coperto, senza fingere un risultato completo.

---

## 4. Elaborazione una tantum per progetti esistenti

### Procedura per le 983 tappe attuali

1. Fare un backup verificato del database e controllare che i file GPX
   referenziati esistano, siano leggibili e non abbiano collisioni di nome.
2. Creare tabelle/migrazione senza alterare o cancellare subito le colonne
   attuali. Calcolare hash e stato per ciascuna tappa.
3. Inserire lavori idempotenti per il solo risultato assente, obsoleto o
   incompatibile. Riutilizzare `superfici_tappa` se è possibile attribuirle
   con certezza lo stesso hash GPX e la stessa versione delle mappe; altrimenti
   marcarla da ricalcolare.
4. Processare una tappa alla volta, o con concorrenza limitata e misurata.
   Fare commit per tappa o piccolo lotto, non un'unica transazione di ore.
5. Calcolare gli aggregati di progetto e verificare campioni manuali, totali,
   coordinate e quantità di punti.

Il numero 983 è quello dello snapshot letto; il numero effettivo sarà
ricontrollato al momento della migrazione. Il fatto che le tabelle cache abbiano
rispettivamente 935 e 983 righe non dimostra da solo che tutte le cache siano
valide.

### Avanzamento e interruzione

- Mostrare `completate / totali`, tappa corrente, fase corrente, errori e
  percentuale di copertura. Separare avanzamento per modulo (per esempio
  superficie o costa) dal progresso complessivo.
- Aggiungere pulsanti **Interrompi** e **Riprendi**. L'interruzione ferma
  l'assegnazione di nuovi lavori e permette al lavoro corrente di concludere o
  fermarsi a un confine sicuro.
- Conservare in `precalcolo_lavori` gli stati e i messaggi d'errore. Al riavvio
  riprendere i lavori `IN_CODA` e quelli rimasti `IN_CORSO` senza heartbeat,
  verificando nuovamente hash e versioni prima di ripeterli.
- Rendere ogni lavoro idempotente: ripeterlo con gli stessi input produce lo
  stesso risultato logico e sostituisce in modo atomico la relativa cache.
- Se l'app si chiude, i risultati già salvati restano; il lavoro non concluso
  torna in coda al successivo avvio. Nessun file GPX originale o risultato
  valido deve essere eliminato per il solo arresto del programma.

---

## 5. Architettura per il calcolo della costa (Guinness-ready)

### Campionamento e calcolo

1. Conservare il GPX originale e hash immutabili come fonte probatoria.
2. Campionare per distanza lungo la geometria, non ogni N-esimo punto per
   indice: GPX diversi hanno densità di punti molto diversa. Interpolare
   coordinate lungo ogni segmento e rispettare i confini tra segmenti.
3. Supportare almeno 5000 campioni per tappa, con passo e regole documentati.
   Un requisito “5000+” non definisce da solo la precisione: una traccia lunga
   1000 km con 5000 campioni produce circa 200 m tra campioni. Per maggiore
   precisione serve un passo massimo, oltre al numero minimo, e valutare una
   misura continua o adattiva vicino a costa, baie e soglie di fascia.
4. Calcolare la distanza tra ciascun campione e la costa più vicina usando
   geometrie indicizzate in un CRS/procedimento adatto a distanze metriche o
   geodetiche. Evitare di misurare direttamente in gradi di longitudine e
   latitudine. Gestire antimeridiano, poli, isole, geometrie invalide e
   segmenti costieri discontinui.
5. Conservare distanza lungo traccia, distanza costa, fascia e coordinate del
   punto costiero più vicino. Il riepilogo per fasce deve derivare dai campioni
   ponderati per la lunghezza realmente rappresentata, non dal solo conteggio
   grezzo se il passo varia.
6. Registrare fonte, versione, CRS, algoritmo, soglie, data del calcolo, hash
   dell'input e checksum del dataset. Per una certificazione, esportare anche
   un rapporto riproducibile dei campioni e una traccia della provenienza.

### Dataset costiero locale

`stats_service.py` usa oggi Natural Earth 10m e può scaricare
`ne_10m_coastline.geojson` se il file `world_coastlines_10m.geojson` non è
presente nella directory di lavoro. Il file attuale è un GeoJSON di linee e
viene indicizzato in memoria con `STRtree`; mancano gestione robusta di
versione/checksum e garanzia di disponibilità offline al primo uso.

Proposta:

- scaricare una sola volta un dataset versionato tramite un flusso esplicito
  di installazione/aggiornamento, verificarne il checksum e salvarlo in una
  directory dati definita;
- registrarne la release e il checksum in `versioni_dataset`;
- costruire l'indice spaziale una volta per processo e riusarlo;
- non sostituire il dataset in uso durante un calcolo; attivare la nuova
  versione solo dopo la verifica completa.

Natural Earth è utile per analisi e prototipi ma è generalizzato e non va
definito **certificativamente preciso** senza l'accettazione dell'ente che
valuta la prova Guinness. Prima di dichiarare la funzione “Guinness-ready”
occorre concordare fonte costiera autorevole, datum, metodo di distanza e
protocollo di campionamento. La documentazione disponibile non specifica le
regole ufficiali richieste dalla certificazione: non vanno inventate.

### Stima orientativa dello spazio

Per 983 tappe × 5000 campioni si ottengono circa **4,9 milioni di campioni**.
Stime indicative, da verificare con un prototipo su campioni rappresentativi:

| Rappresentazione | Stima indicativa per 4,9 milioni | Note |
|---|---:|---|
| Righe SQLite normalizzate con coordinate, distanza, progressiva e indici | circa 0,8–2,0 GB | La dimensione dipende da indici, encoding e pagine SQLite; scrittura e backup più pesanti. |
| Blocchi compatti per tappa, compressi e memorizzati come BLOB | circa 100–400 MB | Dimensione molto dipendente dai delta e dalla compressione; query parziali meno comode. |
| Solo riepiloghi per tappa, senza dettaglio campione | pochi MB | Non basta per audit dettagliato o prova riproducibile. |

Sono stime, non misurazioni. Il dataset costiero Natural Earth va contabilizzato
a parte; la sua dimensione varia per versione e formato. Va misurato il rapporto
di compressione reale, lasciando spazio anche per WAL temporaneo, indici e
backup. Una via pratica è memorizzare i record di campione in blocchi compressi
per segmento/tappa mantenendo un riepilogo SQL; scegliere dopo aver misurato
query, export e verificabilità. Per una certificazione, non ottimizzare lo
spazio eliminando i dati necessari a riprodurre il calcolo.

---

## 6. Considerazioni sull'offline

| Funzione | Funziona senza Internet? | Dipendenza |
|---|---|---|
| Distanza, progressiva, segmenti, quota e pendenza | Sì | GPX locale |
| Geometria semplificata | Sì | GPX locale e algoritmo locale |
| Superfici e divieti | Sì, solo nelle aree coperte | `.mbtiles` locali; fuori copertura il risultato deve dichiararsi incompleto |
| Nomi di località | Sì, con copertura limitata | Layer `place` delle mappe locali; coordinate come fallback |
| Costa | Sì dopo il download iniziale | Dataset costiero locale, versione e checksum |
| Geocodifica del pianificatore | Non sempre | Nominatim quando l'utente inserisce un nome non già risolvibile localmente |
| Creazione rotta pianificata/raccordo | Non sempre | BRouter e, in alcuni flussi, OSRM |
| Clima/stagioni attuale | Per la logica stagionale sì | Distanza, blocco, coordinate e impostazioni salvate; non equivale a previsione meteo in tempo reale |
| Dogane | In buona parte sì | Dati locali/anagrafica; l'accuratezza normativa richiede aggiornamenti e verifica delle fonti ufficiali |

Per minimizzare chiamate esterne: eseguire geocodifica solo quando manca un
nome e la mappa locale non basta; rispettare limiti e condizioni dei servizi;
non chiamare servizi online da ogni pagina. Natural Earth deve essere un
download esplicito o gestito con errore visibile, non un download nascosto
durante l'apertura delle statistiche. Le mappe `.mbtiles` già vengono scaricate
su richiesta e usate localmente per superfici, divieti e nomi.

La promessa “le pagine leggono solo dal database” deve distinguere:

- **calcoli dei dati GPX:** nessuna riapertura o ricalcolo da file nella pagina;
- **aggregazioni SQL e visualizzazione:** query aggregate e formattazione
  restano lecite, ma devono essere rapide e non rianalizzare coordinate;
- **assenza di dati:** mostrare stato, copertura o richiesta di precalcolo,
  anziché calcolare silenziosamente in fase di visualizzazione.

---

## 7. Piano di implementazione a fasi

| Fase | Contenuto e file indicativi | Rischio | Beneficio |
|---|---|---|---|
| **1 — Fondamenta e metriche GPX** | Backup e migrazione DB versionata; nuovo servizio di metriche GPX; hash, stato e `tappa_analisi`/`tappa_segmenti`; integrare prima l'import manuale in `gui/dashboard.py`, poi il salvataggio mappa in `gui/mappa.py`; test su GPX piccoli, segmentati, senza quota e malformati. | Medio | Elimina le letture ripetute per distanza/altimetria e definisce una fonte unica dei KPI. |
| **2 — Cache e pagine consumatrici** | Versionare `superfici_tappa`; integrare hash/revisione mappe in `superfici_service.py`; aggiornare `geocodifica_offline_service.py`; leggere i dati precomputati da `stats_service.py`, audit e clima; generare geometrie semplificate e farle leggere a `gui/mappa.py`; stato UI per dati incompleti. | Medio-alto | Evita ricalcoli di superfici/nome/KPI all'apertura e riduce lavoro della mappa; chiarisce copertura offline. |
| **3 — Costa e migrazione completa** | Nuovo motore costiero, installazione dataset versionato, 5000+ campioni e riepiloghi; pipeline batch riprendibile in `precalcolo_service.py`; schermata progresso/interruzione; confronto con misure di riferimento, export di audit e test di antimeridiano/baie/soglie. | Alto | Permette analisi costiera ripetibile, scalabile e verificabile; rende possibile il percorso verso i requisiti Guinness, subordinato alla validazione della fonte e del protocollo. |

**Primo intervento sensato:** fase 1 limitata al contratto di `tappa_analisi`,
hash del GPX e metriche distanza/segmenti/altimetria, senza cambiare tutte le
pagine insieme. È la base comune, misurabile e reversibile; prepara
l'invalidazione e permette di confrontare risultati nuovi e attuali prima di
farli diventare la fonte unica.

---

## 8. Domande aperte

1. **Che cosa definisce un “segmento Guinness”?** Un `<trkseg>` originale,
   una tappa, un tratto certificativo stabilito dall'utente o altro?
2. **Quali sono le tre fasce costiere definitive?** Il testo richiede tre
   fasce; l'app oggi ne mostra quattro (0–500 m, 501–2500 m, 2501–5000 m,
   oltre 5000 m). Quali soglie e inclusività usare?
3. **Qual è il protocollo Guinness?** Serve la fonte costiera ammessa, datum,
   definizione di “distanza dalla costa”, passo massimo, accuratezza e formato
   probatorio. Natural Earth 10m non va assunto sufficiente.
4. **Come trattare le tappe sospese e i trasferimenti?** Definiscono o no la
   distanza progressiva e i km certificati? I trasferimenti devono restare
   esclusi dalla distanza ciclabile?
5. **Come trattare GPX con più track/segmenti, punti duplicati e quote
   mancanti?** Serve una regola esplicita per non creare distanze artificiali
   tra segmenti separati.
6. **Quale definizione di pendenza?** Pendenza media firmata, media assoluta,
   massima istantanea o per tratto; filtro del rumore, distanza minima e
   arrotondamento da concordare. Il calcolo corrente non usa la distanza reale
   dei campioni.
7. **Quali categorie di superficie definitive?** Il codice attuale include
   “Pista ciclabile”, “Sentiero” e “Non specificata”, oltre a pavimentato e
   sterrato; l'elenco prodotto richiama anche “misto” e “single track”.
   Stabilire tassonomia e mappatura dei tag OSM/BRouter.
8. **Quanto devono essere dettagliati i campioni costieri persistiti?**
   Tutti i punti e le distanze favoriscono audit; blocchi compressi riducono
   spazio ma richiedono un formato d'accesso e export da definire.
9. **Quando un nome luogo non trovato diventa da ricalcolare?** Solo quando
   cambia il dataset locale, quando si installa una nuova mappa place o anche
   su richiesta dell'utente?
10. **Quale politica per errori parziali?** Una tappa può essere “pronta” per
    statistiche ma non coperta da mappe per superfici? È preferibile uno stato
    per ogni modulo (raccomandato) invece di un solo stato globale.
11. **Dove conservare l'eventuale cache geometrica?** SQLite compressa è
    semplice da rendere atomica, mentre file separati possono essere più
    efficienti per payload grandi. La scelta richiede un test con il percorso
    da 958 tappe e misure di memoria/tempo.
12. **Quale garanzia normativa per dogane e divieti?** Un risultato offline
    basato su dati locali può essere datato o incompleto; va mostrata data,
    fonte e copertura senza presentarlo come parere legale o certezza assoluta.

---

## Esito

Il progetto ha già componenti riutilizzabili (distanza all'import,
`superfici_tappa`, cache nomi, mappe locali e worker Qt), ma oggi non esiste un
registro comune che provi che ogni risultato appartenga alla precisa versione
del GPX e delle fonti usate. Il nucleo del lavoro è quindi: definire metriche e
provenienza, rendere il precalcolo riprendibile e fare sì che ogni schermata
mostri dati DB con uno stato di validità esplicito. La precisione Guinness
richiede inoltre una decisione esterna sul dataset e sul protocollo di misura;
non è garantibile dal solo aumento del numero di campioni.
