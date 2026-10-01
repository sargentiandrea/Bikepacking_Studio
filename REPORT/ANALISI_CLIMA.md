# Analisi della pagina Clima / Catena Stagionale

Analisi basata sul codice attuale di `service/clima_service.py` e
`app_desktop.py`, sullo schema riportato in `REPORT/DB_SCHEMA.md` e su una
lettura in sola modalità del database locale. Non sono stati modificati dati
del database.

## 1. Cosa fa oggi (funzionalità attuali)

La pagina **Catena Stagionale & Clima** costruisce un calendario indicativo
per i blocchi di un percorso:

- usa una data di partenza;
- considera ogni tappa attiva come un giorno di pedalata;
- aggiunge giorni di riposo in base al numero di tappe e a un modificatore;
- può includere giorni extra configurati per blocco;
- assegna a ciascun blocco una lista di mesi ideali, automatica oppure
  personalizzata se già presente nel database;
- confronta il mese d'ingresso e quello d'uscita del blocco con la lista dei
  mesi ideali e mostra un esito verde o rosso;
- se l'esito è rosso, propone di anticipare o posticipare la partenza di un
  certo numero di giorni.

È quindi una **stima deterministica basata su regole semplici**, non una
previsione meteo e non una valutazione completa del clima lungo tutto il
blocco.

Nell'interfaccia l'utente può cambiare la data di partenza e il modificatore
dei giorni di riposo, calcolare di nuovo e salvare queste due impostazioni.
Non ci sono controlli visibili per modificare i giorni extra o i mesi
personalizzati per blocco.

## 2. Come sono strutturati i dati (tabelle, campi)

Lo schema riportato è stato confrontato con quello letto in sola modalità dal
database locale.

### `progetto_stagione`

Una riga per progetto, con la configurazione generale:

| Campo | Tipo | Uso |
|---|---|---|
| `id_progetto` | INTEGER, chiave primaria | Identifica il progetto |
| `data_partenza` | TEXT | Data salvata nel formato `YYYY-MM-DD` |
| `modificatore_riposo` | INTEGER, default `0` | Correzione applicata ai giorni di riposo stimati per blocco |

La tabella non dichiara una chiave esterna verso `progetti`.

### `blocchi_stagione`

Una riga per combinazione progetto/blocco, con impostazioni del singolo
blocco:

| Campo | Tipo | Uso |
|---|---|---|
| `id` | INTEGER, chiave primaria | Identificativo della riga |
| `id_progetto` | INTEGER | Identifica il progetto |
| `nome_blocco` | TEXT | Nome del blocco, usato anche per abbinarlo alle tappe |
| `giorni_extra` | INTEGER, default `0` | Giorni aggiuntivi alla durata del blocco |
| `mesi_ideali` | TEXT, default `04,05,06,09,10` | Colonna presente nel database attuale; il servizio esaminato non la legge |
| `mesi_ideali_custom` | TEXT, default NULL | Mesi personalizzati letti dal servizio se valorizzati |

È presente un vincolo UNIQUE su `(id_progetto, nome_blocco)`. Non è
dichiarata una chiave esterna verso `progetti`.

### Dati delle tappe usati dal calcolo

`calcola_catena_stagionale` legge da `tappe`:

- `id_progetto`, `id`, `blocco`, `stato`, `distanza_km`;
- `start_lat` e `start_lon`, se le colonne esistono;
- la prima colonna altitudine trovata nell'ordine `ele_max`, `quota_max`,
  `ele_high`, `ele`.

Nel database locale ispezionato, `tappe` ha `start_lat` e `start_lon`, ma
**non** ha nessuna delle quattro colonne altitudine cercate dal servizio.
Di conseguenza il calcolo attuale riceve altitudine massima pari a zero.

Per l'ordine dei blocchi viene inoltre consultata `blocchi_ordine.ordine`.
Se non è disponibile un ordine, la query usa `999` come valore di ripiego.

### Differenza tra lo schema dichiarato dal codice e quello esistente

`assicura_tabelle_clima()` crea `blocchi_stagione` con `giorni_extra` e
`mesi_ideali_custom`, ma non crea la colonna `mesi_ideali`. Se la tabella
esiste già, il codice controlla e aggiunge solo `mesi_ideali_custom` quando
manca. Il database attuale contiene anche `mesi_ideali`, probabilmente
residuo di uno schema precedente; il servizio non lo usa. La colonna
effettivamente letta per una personalizzazione è `mesi_ideali_custom`.

## 3. Le funzioni di `clima_service.py` (dettaglio)

| Funzione | Input e dati letti | Cosa calcola / restituisce |
|---|---|---|
| `determina_mesi_ideali_automatici(lat_media, lon_media, altitudine_max=0)` | Latitudine media, longitudine media, altitudine massima. | Restituisce una stringa di mesi separati da virgole. La longitudine è accettata ma non viene usata. Se manca la latitudine o la longitudine restituisce `04,05,06,09,10`. Altrimenti sceglie una finestra secondo fasce di latitudine e, se disponibile, altitudine oltre 2000 m. |
| `assicura_tabelle_clima()` | Configurazione SQLite locale (`DB_NAME`); legge le colonne esistenti di `blocchi_stagione` tramite `PRAGMA table_info`. | Crea le due tabelle se mancanti e aggiunge `mesi_ideali_custom` se manca. Non calcola dati climatici. |
| `salva_impostazioni_stagione(id_progetto, data_partenza_str, modificatore_riposo, giorni_extra_dict=None, mesi_custom_dict=None)` | ID progetto, data, modificatore; opzionalmente dizionari con giorni extra e mesi personalizzati per blocco. | Inserisce o aggiorna la configurazione del progetto. Se viene passato un dizionario di giorni extra non vuoto, inserisce/aggiorna anche i record dei blocchi. Quando i mesi personalizzati passati sono `None`, conserva quelli già presenti grazie a `COALESCE`; questa funzione non offre un modo esplicito per cancellarli. |
| `calcola_catena_stagionale(id_progetto, data_partenza_dt=None, modificatore_riposo=0, giorni_extra_dict=None)` | Legge impostazioni in `progetto_stagione`, personalizzazioni in `blocchi_stagione`, tappe attive in `tappe` e ordine in `blocchi_ordine`. Usa data e modificatore forniti dal chiamante se presenti. | Raggruppa le tappe attive per blocco e restituisce una lista di dizionari con ordine, nome blocco, numero tappe, km, giorni di pedalata/riposo/extra/totali, date d'ingresso e uscita, mesi ideali ed esito semaforico. Se non ci sono tappe attive restituisce `[]`. |

### Regole implementate da `determina_mesi_ideali_automatici`

La funzione restituisce:

| Condizione | Mesi selezionati |
|---|---|
| Coordinate mancanti | `04,05,06,09,10` |
| Tropici, latitudine da 0° a 23,5° N | `11,12,01,02,03` |
| Tropici, latitudine a sud dell'equatore fino a 23,5° S | `05,06,07,08,09` |
| Emisfero sud temperato, oltre 2000 m | `12,01,02` |
| Latitudine inferiore a -40° (per esempio Patagonia) | `11,12,01,02,03` |
| Resto dell'emisfero sud temperato | `09,10,11,03,04` |
| Emisfero nord, oltre 2000 m | `06,07,08,09` |
| Emisfero nord oltre 55° | `06,07,08` |
| Latitudine tra 30° e 40° N | `03,04,05,10,11` |
| Altre latitudini dell'emisfero nord considerate temperate | `04,05,06,09,10` |

Nel calcolo per blocco la latitudine è la media di `start_lat`; la
longitudine media viene calcolata dalla query, ma la funzione di selezione
dei mesi non la usa. L'altitudine è il massimo dei campi altitudine
disponibili in `tappe`, non una media. Nel database locale attuale non è
presente alcuno di quei campi.

## 4. Il flusso della pagina (dal click alla visualizzazione)

1. Quando viene costruita la finestra, `app_desktop.py` crea la pagina
   `page_clima`, la aggiunge allo `QStackedWidget` all'indice 6 e collega il
   pulsante laterale `btn_clima` a `apri_pagina_clima()`.
2. `apri_pagina_clima()` chiama `cambia_pagina(6)`. Il metodo seleziona la
   pagina e, per l'indice 6, chiama `aggiorna_pagina_clima()`.
3. Se non c'è un progetto attivo, la pagina mostra il messaggio che invita
   ad aprire un percorso e svuota la tabella.
4. Se c'è un progetto, `aggiorna_pagina_clima()` assicura le tabelle,
   legge `data_partenza` e `modificatore_riposo` da `progetto_stagione` e,
   se trova una configurazione, aggiorna i due controlli. Poi chiama
   `calcola_pagina_clima()`.
5. `calcola_pagina_clima()` prende data e modificatore dai controlli e
   chiama `calcola_catena_stagionale()`, passando esplicitamente entrambi.
   La funzione costruisce la catena e restituisce i risultati.
6. La GUI riempie le 12 colonne della tabella: ordine, blocco, tappe, km,
   pedalata, riposo, extra, giorni totali, ingresso, uscita, mesi ideali ed
   esito. Un'etichetta indica quanti blocchi sono stati calcolati, oppure
   comunica che non ci sono tappe attive. Gli errori sono mostrati
   nell'etichetta di stato.
7. Il pulsante **Calcola** esegue nuovamente il punto 5 senza salvare.
8. Il pulsante **Salva impostazioni** chiama
   `salva_impostazioni_stagione()` con ID, data e modificatore. Poi ricalcola
   la catena e mostra il messaggio di avvenuto salvataggio.

La schermata espone solo data e modificatore riposo. Non passa i dizionari
opzionali `giorni_extra_dict` e `mesi_custom_dict` alla funzione di
salvataggio, quindi non consente da questa pagina di modificare i valori
per blocco.

Se un progetto non ha ancora impostazioni salvate, `aggiorna_pagina_clima()`
non reimposta esplicitamente i controlli ai valori iniziali. Passando da un
progetto a un altro nella stessa finestra, data e modificatore già presenti
nei widget possono quindi essere riutilizzati nel ricalcolo finché non
vengono sostituiti da valori salvati o modificati dall'utente.

## 5. Risposte alle domande specifiche

### Come vengono calcolati i “mesi ideali”?

Se per un blocco esiste `mesi_ideali_custom`, quella stringa viene usata
direttamente. Altrimenti il servizio applica le fasce geografiche descritte
nella sezione 3, usando la latitudine media delle tappe del blocco e
l'altitudine massima disponibile. Non consulta temperature, precipitazioni,
stagioni delle piogge effettive o previsioni.

### Cosa significa “catena stagionale” e come viene calcolata?

È una sequenza di blocchi datati uno dopo l'altro. Per ciascun blocco:

- giorni di pedalata = numero di tappe attive;
- giorni di riposo = `max(0, (numero_tappe // 5) + modificatore_riposo)`;
- giorni extra = valore salvato per quel blocco, o zero se assente;
- giorni totali = somma dei tre valori;
- l'ingresso parte dalla data corrente della catena;
- l'uscita è ingresso più `giorni_totali - 1` quando la durata è positiva;
- il blocco successivo inizia il giorno successivo all'uscita.

I chilometri vengono mostrati, ma non determinano il numero di giorni: una
tappa vale un giorno indipendentemente dalla sua lunghezza.

Il semaforo è verde se **il mese della data d'ingresso oppure quello della
data d'uscita** è tra i mesi ideali. Non verifica ogni giorno del blocco né
il passaggio in un mese intermedio. Se il semaforo è rosso, il servizio cerca
entro 365 giorni un anticipo o un ritardo che porti uno dei due estremi in un
mese ideale e lo propone come numero di giorni.

### Il calcolo tiene conto di altitudine, latitudine, longitudine o altro?

- **Latitudine:** sì, media delle latitudini iniziali delle tappe del blocco;
  seleziona le fasce geografiche.
- **Altitudine:** il codice la supporta cercando una colonna massima su
  `tappe`, ma nella tabella attuale tale colonna non esiste; nel database
  ispezionato l'altitudine effettivamente usata è pertanto zero.
- **Longitudine:** viene aggregata dalla query, ma non influenza la scelta
  dei mesi.
- **Altri fattori:** conteggio delle tappe, modificatore di riposo, giorni
  extra e date. I chilometri sono solo riportati; non sono usati per la
  durata o per i mesi ideali.

### Il calcolo è deterministico o probabilistico?

È deterministico: a parità di tappe, impostazioni e data, produce lo stesso
risultato. Non calcola probabilità, intervalli di confidenza o rischio
meteorologico.

### Da dove vengono i dati climatici?

Non risultano dati climatici o fonti meteo nel servizio: i mesi sono
selezionati da regole codificate a mano. Per i dati geografici il calcolo
usa coordinate delle tappe salvate nel database e, solo se esistessero nella
tabella `tappe`, alcune colonne di altitudine.

### Il calcolo è offline o richiede internet?

Il calcolo della catena non effettua chiamate di rete e usa SQLite e codice
locale; può quindi essere eseguito offline, purché il database e le tappe
siano disponibili.

## 6. Punti di forza, limiti, potenzialità

### Punti di forza attuali

- Il calcolo è locale, veloce e ripetibile; non dipende da un servizio
  esterno.
- I blocchi sono ordinati secondo `blocchi_ordine` e le tappe non attive
  vengono escluse (`stato = 'ATTIVA'` oppure `stato IS NULL`).
- Le impostazioni generali di partenza e riposo sono persistite per
  progetto.
- Il servizio prevede già giorni extra e mesi personalizzati per blocco,
  anche se la pagina non espone i relativi controlli.
- La finestra mesi tiene conto almeno della latitudine e ha regole
  specifiche per alcune fasce tropicali, australi, mediterranee, montane e
  settentrionali.

### Limiti attuali

- I mesi sono euristiche ampie, non dati climatici locali: due località
  diverse nella stessa fascia ricevono la stessa finestra.
- La longitudine non viene usata, quindi non distingue regioni climatiche
  diverse alla stessa latitudine.
- L'altitudine non è disponibile nella tabella `tappe` del database
  attuale, quindi le regole per alta montagna non vengono attivate dal
  calcolo corrente.
- Il fallback per coordinate mancanti è una finestra fissa etichettata nel
  codice come Europa temperata; può essere inadatto fuori dall'Europa.
- Ogni tappa equivale a un giorno di pedalata. La distanza non influenza la
  durata e non ci sono velocità, giorni settimanali di riposo o giorni
  indisponibili.
- Il semaforo valuta soltanto il mese d'ingresso o d'uscita del blocco; può
  segnalare verde anche se gran parte del transito cade fuori finestra.
- Il semaforo non misura temperature, piogge, vento, neve, estremi,
  altitudine di tutto il tracciato o variabilità annuale.
- L'interfaccia non permette di impostare giorni extra o mesi ideali per
  singolo blocco, nonostante il servizio e il database li supportino.
- La tabella `mesi_ideali` presente nel database attuale non è usata; il
  codice legge `mesi_ideali_custom`.
- Se si seleziona un progetto senza preferenze salvate, i controlli della
  schermata non vengono riportati esplicitamente ai default; possono
  mantenere i valori precedenti nella finestra.

### Potenzialità

- Aggiungere nell'interfaccia editor per giorni extra e mesi personalizzati
  per blocco, collegandoli ai parametri già previsti dal servizio.
- Usare i chilometri già disponibili per stimare la durata con una velocità
  configurabile, lasciando chiara la differenza tra stima e dato reale.
- Valutare l'intero intervallo di transito, non solo i mesi alle due
  estremità, e mostrare quanti giorni ricadono nella finestra scelta.
- Rendere esplicito quando mancano coordinate o quote e consentire una
  correzione manuale.
- Separare l'attuale “finestra stagionale euristica” da una futura
  valutazione climatica basata su dati mensili, medie storiche e
  variabilità.
- Se si decide di introdurre dati climatici, associare ogni risultato a
  fonte, periodo, risoluzione geografica e data di aggiornamento; valutare
  caching locale e uso offline.

### Cosa manca per un viaggio intercontinentale

Servono almeno dati climatici affidabili a scala locale e per mese,
valutazioni che seguano le località attraversate e non una sola media di
latitudine per blocco, gestione dell'altitudine realmente disponibile,
stime realistiche di durata, e un'indicazione dell'incertezza. Per un uso
operativo andrebbero inoltre distinti clima medio e condizioni attese
dell'anno specifico: la pagina attuale non fornisce previsioni né avvisi
meteorologici.

## 7. Domande aperte (cose su cui serve una decisione)

1. I “mesi ideali” devono restare una guida semplice basata su regole o
   diventare una valutazione basata su dati climatici con fonti verificabili?
2. Quali condizioni contano per definire un periodo adatto: temperatura,
   pioggia, vento, neve, rischio di caldo o una combinazione?
3. Il semaforo deve richiedere che tutto il blocco sia nella finestra
   favorevole, una percentuale minima di giorni o soltanto un inizio
   favorevole?
4. Come si vuole stimare la durata: una tappa al giorno, km/giorno
   configurabili, o un calendario giornaliero con riposi manuali?
5. Le impostazioni per blocco (giorni extra e mesi personalizzati) devono
   essere modificabili direttamente da questa pagina?
6. Per coprire i viaggi intercontinentali si accettano download o
   aggiornamenti online, oppure la funzione deve restare interamente offline?
7. Quale comportamento desiderato va applicato se mancano coordinate,
   quota o dati climatici per una regione?
