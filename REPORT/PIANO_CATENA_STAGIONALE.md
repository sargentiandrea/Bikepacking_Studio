# Piano di progettazione — Catena Stagionale

Questo documento traduce la visione della Catena Stagionale in una proposta
di progettazione a fasi. Non introduce codice, non approva in modo definitivo
dataset o servizi e non sostituisce le decisioni ancora aperte.

## Contesto di partenza

L'analisi attuale mostra che la pagina calcola una catena deterministica
usando il conteggio delle tappe, una stima dei giorni di riposo e regole
geografiche per i mesi ideali. Non usa dati meteorologici reali. La tabella
attuale consente di impostare data di partenza e modificatore di riposo; il
servizio contiene già parametri per giorni extra e mesi personalizzati per
blocco, ma la schermata non li espone.

Il database usa `blocchi_ordine` per l'ordine dei blocchi e `tappe` per
sequenza, nome del blocco, coordinate iniziali/finali, distanza e stato.
`tappa_analisi` contiene anche distanze e quote calcolate, mentre
`tappa_geometrie` conserva geometrie complete e semplificate. Il modello
attuale non ha un identificatore stabile dedicato al blocco: alcune relazioni
sono basate sul nome.

Il piano considera WorldClim 2.1 o CHELSA come candidati offline, e
OpenWeatherMap come candidato per aggiornamenti online, come indicato nel
contesto. Prima di adottarli occorre verificare licenze, condizioni d'uso,
copertura, periodi disponibili, formato e peso effettivo dei dati.

## 1. Architettura dei dati climatici offline

### Scelta iniziale di risoluzione

Per un primo prototipo globale è ragionevole provare una risoluzione di
**10 minuti d'arco (10m)**, mantenendo i raster originali fuori dal normale
percorso di avvio dell'app. È una scelta iniziale da misurare, non una
decisione definitiva: la visione richiede contenere lo spazio e la pagina
deve dare una lettura stagionale su blocchi estesi, non una previsione
puntuale di ogni tratto.

Non si deve scaricare o includere nel pacchetto dell'app un archivio globale
ad alta risoluzione senza prima misurarne dimensioni, copertura e costo di
distribuzione. Le risoluzioni 30s, 2.5m e 5m possono essere confrontate su
una piccola area campione per vedere se migliorano davvero l'esito dei
blocchi rispetto all'aumento di spazio.

Il prototipo deve produrre una misura documentata di:

- spazio del dataset sorgente richiesto e spazio effettivamente installato;
- numero di celle e valori estratti per il viaggio;
- tempo di estrazione e di aggiornamento;
- differenze tra risoluzioni nelle aree attraversate.

Il totale indicativo attuale dell'app è 107 GB, in gran parte occupato dalle
mappe. Non è ancora definito un budget massimo per il clima: va concordato
prima di distribuire i dati.

### Integrazione proposta

Separare tre elementi:

1. **Dataset sorgente**: raster climatici, opzionali o installabili a parte,
   con nome, versione, licenza, periodo coperto, risoluzione e variabili.
2. **Estrazione per viaggio**: valori mensili campionati lungo le tappe e
   riepiloghi compatti necessari alla schermata.
3. **Interfaccia**: legge i riepiloghi locali senza aprire o analizzare i
   raster durante la navigazione normale.

Un piccolo strumento di importazione/preparazione può usare `rasterio` per
aprire un raster, trasformare la coordinata nel sistema di riferimento
richiesto e leggere la cella corrispondente. La disponibilità e le
condizioni di distribuzione di `rasterio` sulle piattaforme supportate
devono essere verificate. Per non appesantire la versione mobile, la
lettura dei raster potrebbe rimanere una fase di preparazione desktop e il
risultato condiviso essere un pacchetto locale compatto; questa è una
proposta da validare, non una scelta già presa.

### Dati per una coordinata e copertura del percorso

Un singolo campionamento sul punto medio di un blocco è leggero ma non
rappresenta bene un blocco lungo o che attraversa zone climatiche diverse.
La proposta è:

- campionare la geometria delle tappe lungo il tracciato, evitando di
  conservare ogni punto del raster;
- riutilizzare, se la qualità e il formato lo consentono, le geometrie già
  presenti in `tappa_geometrie`;
- mantenere il legame tra campione, tappa, coordinata e versione dei dati;
- calcolare riepiloghi del blocco pesati lungo la distanza percorsa, non
  solo una media delle coordinate d'inizio.

Il numero e la distanza tra i campioni devono essere scelti dopo un test su
un blocco breve e uno molto esteso. Una rotta senza geometria o con
coordinate mancanti deve essere segnalata come copertura incompleta, non
completata con valori inventati.

La lettura raster richiede di verificare per ciascuna variabile:
unità di misura, calendario dei mesi, valori mancanti, sistema di
riferimento e trattamento di terra/mare. Occorre inoltre verificare quali
variabili siano effettivamente disponibili nel dataset scelto. In
particolare, il piano non presume che WorldClim o CHELSA forniscano tutti
vento e neve nel formato e nella copertura richiesti.

### Dove conservare i valori

Non è consigliato inserire i raster globali grezzi nel database SQLite
principale: renderebbe più pesante il database applicativo e le sue copie di
backup. La proposta è conservare:

- i raster sorgente in un pacchetto dati separato, facoltativo e
  versionato;
- in SQLite, i metadati del dataset e i soli campioni/riepiloghi necessari
  ai progetti installati;
- nessun dato climatico duplicato per ogni apertura della pagina.

Un'eventuale cache si invalida se cambia la geometria della tappa, il
dataset, la risoluzione o la versione dell'algoritmo di aggregazione.

### Schema proposto per i dati

Le tabelle seguenti sono una proposta concettuale: i nomi e i campi vanno
consolidati prima di una migrazione.

| Tabella proposta | Campi essenziali | Scopo |
|---|---|---|
| `clima_dataset` | `dataset_id`, `nome`, `versione`, `periodo_inizio`, `periodo_fine`, `risoluzione`, `licenza`, `installato_il`, `metadati_json` | Identificare con precisione i dati climatici installati |
| `clima_tappa_mese` | `tappa_id`, `dataset_id`, `mese`, `variabile`, `media`, `minimo`, `massimo`, `copertura_pct`, `campioni`, `versione_algoritmo` | Conservare valori aggregati della tappa per mese e variabile |
| `clima_blocco_mese` | `id_progetto`, `nome_blocco` o futuro `blocco_id`, `dataset_id`, `mese`, `variabile`, `media_pesata`, `percentile_basso`, `percentile_alto`, `copertura_pct` | Dare una lettura compatta del profilo climatico del blocco per mese |
| `clima_cache_online` | `area_o_coordinate`, `servizio`, `richiesto_il`, `valido_fino`, `variabile`, `periodo`, `valore`, `unita`, `risposta_metadati` | Cache delle risposte online e indicazione della loro freschezza |

La chiave naturale dei riepiloghi di blocco non dovrebbe dipendere
unicamente dal nome del blocco, perché il nome può essere modificato.
Prima della persistenza definitiva va valutato un ID stabile per blocco e
una strategia di migrazione delle relazioni correnti basate su
`nome_blocco`.

Il database esistente non documenta tabelle climatiche. La migrazione dovrà
essere incrementale, accompagnata da backup e compatibile con progetti che
non hanno ancora dati climatici estratti.

## 2. Flusso della pagina

### Caricamento della catena

1. Leggere il progetto attivo.
2. Leggere i blocchi ordinati da `blocchi_ordine`, con un ordinamento
   esplicito e un valore di fallback per eventuali blocchi senza ordine.
3. Associare ogni blocco alle tappe attive, rispettando la sequenza dei file
   GPX. L'analisi attuale mostra che i nomi tra `blocchi_ordine.nome_blocco`
   e `tappe.blocco` possono non coincidere esattamente; l'interfaccia deve
   segnalare i blocchi non associati invece di nasconderli.
4. Caricare distanze, geometrie e dati di durata disponibili. Separare
   chiaramente valori registrati, valori calcolati e ipotesi.
5. Applicare la data di partenza, il modello di pedalata/riposo e i margini
   per imprevisti per determinare ingresso e uscita di tutti i blocchi.
6. Per ciascun blocco, consultare il riepilogo climatico locale relativo ai
   mesi in cui il blocco è previsto.
7. Valutare i fattori coperti dai dati e preparare semaforo, spiegazione,
   copertura e incertezza.
8. Presentare la catena nella tabella, timeline e mappa.

Il calcolo del percorso deve restare una simulazione locale: aprire la
pagina non deve avviare richieste internet né ricaricare raster globali.

### Proiezione temporale

La visione fissa le regole di riferimento:

- una tappa equivale a un giorno di pedalata;
- un giorno di riposo ogni cinque tappe;
- cinque giorni extra per ogni mese;
- una settimana aggiuntiva ogni quattro mesi;
- data di partenza configurabile.

La pagina deve mostrare separatamente durata di pedalata, riposo e margini.
Le date successive devono tenere conto della durata completa del blocco e
del margine accumulato, così da rendere visibile l'effetto su tutto il
viaggio.

La definizione di “mese” per i cinque giorni extra non è specificata: può
significare mese di calendario attraversato o periodo convenzionale di 30
giorni. Anche la regola se il giorno di riposo scatta dopo ogni quinto
giorno, compreso l'ultimo del blocco, deve essere decisa. La stessa
definizione va usata in ogni vista e in ogni scenario.

La regola attuale del servizio clima è più semplice e non coincide
necessariamente con questa proiezione: non va mantenuta in parallelo come
seconda fonte di date. Si propone un unico motore di simulazione riusato
dalla tabella, timeline e mappa.

### Semaforo stagionale

Per ogni tratto temporale del blocco, il motore confronta il mese di
calendario con i profili climatici mensili delle località campionate sul
percorso. Un blocco che attraversa più mesi o più aree deve essere valutato
sull'intero transito, non soltanto sul mese di ingresso e di uscita.

Il risultato mostrato dovrebbe contenere:

- colore e giudizio sintetico;
- fattori disponibili e valori/range che hanno influito;
- soglie e preferenze applicate;
- percentuale del percorso e del periodo coperta dai dati;
- segnalazione esplicita di fattori mancanti.

Se un fattore non è disponibile, non va trattato come favorevole né come
sfavorevole per default. Il giudizio deve indicare la copertura ridotta e
applicare una regola di incertezza ancora da definire.

### Effetto delle modifiche

Ogni modifica a data di partenza, durata, ordine, spostamento o salto crea
una nuova simulazione dell'intera catena. La UI deve mostrare prima/dopo,
almeno per:

- data di ingresso e uscita di ogni blocco interessato;
- differenze del semaforo e delle relative motivazioni;
- data finale stimata del viaggio;
- trasferimenti o inversioni di direzione che la proposta potrebbe
  richiedere.

La simulazione non deve riscrivere subito `blocchi_ordine`. Il risultato è
una bozza finché l'utente non lo conferma.

## 3. Integrazione con la pagina Gestione blocchi

### Scenario proposto

La catena stagionale può proporre:

- anticipare o posticipare l'intera partenza;
- spostare un blocco prima o dopo un altro;
- saltare temporaneamente un blocco nello scenario;
- ripianificare il blocco saltato in una posizione successiva, se
  compatibile con l'obiettivo di procedere in avanti.

Ogni proposta deve avere una ragione leggibile, il suo impatto su tutti i
blocchi successivi e l'indicazione dei dati climatici usati. “Saltare” deve
essere definito con precisione: può significare non pedalare quel blocco
ora, non cancellare le tappe dal progetto.

### Conferma e salvataggio

Proposta di separare:

1. **Scenario temporaneo**: ordinamento, salti, date e parametri di
   simulazione; non modifica i dati ufficiali.
2. **Conferma dell'utente**: riepilogo esplicito delle differenze e avviso
   che l'ordine del viaggio verrà aggiornato.
3. **Applicazione**: scrittura atomica dell'ordine confermato in
   `blocchi_ordine`, seguita dall'aggiornamento delle pagine collegate.
4. **Recupero**: conservazione del precedente ordine o possibilità di
   annullare l'ultima applicazione, così da non perdere la pianificazione
   esistente.

Prima di applicare l'ordine, il sistema deve verificare che ogni blocco sia
identificato una sola volta e che le tappe contenute siano quelle attese.
I blocchi non riconosciuti o privi di tappe vanno presentati per una
correzione manuale.

Per conservare scenari multipli si può introdurre una tabella di testata
scenario e una tabella di righe scenario con blocco, posizione e stato
(incluso/saltato). Lo schema definitivo è da stabilire. `blocchi_ordine`
resta la sequenza ufficiale, aggiornata soltanto dopo la conferma.

Attualmente `blocchi_ordine` memorizza progetto, nome e ordine; lo schema
non mostra un campo per salti, motivazioni o revisioni. La conferma di uno
scenario richiede quindi una scelta su come rappresentare i salti e su come
garantire il ripristino dell'ordine.

## 4. Semaforo e soglie

### Fattori

La visione indica temperatura, pioggia, vento e neve. Il dataset offline
selezionato deve essere verificato variabile per variabile: non è garantito
che un unico dataset fornisca tutti e quattro i fattori per gli stessi
luoghi e periodi.

| Fattore | Possibile uso nella valutazione | Verifica necessaria |
|---|---|---|
| Temperatura | Preferenza per condizioni calde e individuazione di freddo/caldo eccessivo | Definizione di soglie, statistiche mensili e variabili disponibili |
| Pioggia | Penalità o rischio di periodi piovosi | Unità, cumulata mensile e significato per le tappe |
| Vento | Esposizione al vento e disagio atteso | Copertura storica del dataset e scala temporale |
| Neve | Rischio in quota o stagionale | Copertura del dataset e relazione con quota/percorso |

Per WorldClim 2.1 o CHELSA occorre verificare esattamente le variabili
distribuite e le condizioni di licenza. Il piano non dà per scontati vento e
neve nei dati candidati. Se non sono disponibili offline, l'interfaccia
dovrà indicare “non valutato”, oppure la funzione potrà essere rinviata
finché non si seleziona una fonte adeguata.

### Personalizzazione

Proposta di configurare:

- soglie per fattore, con unità sempre visibile;
- priorità o peso relativo dei fattori;
- preferenza esplicita, per esempio caldo prioritario rispetto alla
  pioggia;
- soglie predefinite accessibili e profili utente salvabili.

La combinazione dei fattori (pesi, regole di esclusione e passaggio tra
verde/giallo/rosso) non è definita dalla visione. Deve essere decisa e
provata con esempi reali prima di essere presentata come valutazione
affidabile.

### Spiegazione del giudizio

Ogni esito deve poter essere letto senza conoscere la formula interna:

- mostrare i fattori che hanno peggiorato o migliorato il giudizio;
- mostrare il valore o l'intervallo confrontato con la soglia;
- indicare i fattori mancanti e la percentuale di copertura;
- distinguere clima storico, dato online recente e ipotesi di durata;
- non produrre un verde pieno quando i dati essenziali sono assenti.

Il linguaggio deve esprimere una valutazione indicativa, non una garanzia di
sicurezza o una previsione meteo certa.

## 5. Requisiti di leggerezza

### Gestione di 2.000 tappe

La vista globale deve caricare una riga per blocco, non tutte le coordinate
e tutti i punti GPX come widget distinti. Le tappe dettagliate vanno caricate
quando si apre un blocco o si chiede il dettaglio. La timeline e la mappa
possono aggregare la vista a livello blocco e caricare dettagli solo su
selezione o ingrandimento.

Il calcolo delle date e degli indicatori deve essere lineare rispetto al
numero di blocchi e tappe, senza leggere i raster durante ogni aggiornamento
della GUI. I profili climatici mensili vanno precalcolati/cachati per le
geometrie del viaggio e riutilizzati quando cambia soltanto una data o una
soglia.

Il limite di 2.000 tappe va verificato con un test sintetico che misuri
tempo di aggiornamento, memoria, dimensione del database e fluidità della
UI. Il criterio di accettazione deve essere concordato prima
dell'implementazione; non è definito in questo documento.

### Spazio e distribuzione

- Tenere i raster originali separati dal database applicativo.
- Installare solo la risoluzione e le variabili approvate.
- Conservare nel database i campioni e gli aggregati necessari, non copie
  delle immagini raster.
- Rendere possibile rimuovere e reinstallare un dataset senza perdere
  progetti, geometrie o pianificazioni.
- Mostrare lo spazio richiesto prima di scaricare o installare un pacchetto.

Il peso reale non può essere stimato senza selezionare i file e le
variabili dei dataset. Va misurato su un prototipo prima di fissare un
limite.

### Desktop e mobile

La UI desktop corrente usa PySide6; la visione richiede anche iOS e Android,
ma non è documentata qui un'interfaccia mobile già disponibile. Perciò la
portabilità non va data per acquisita.

La logica della catena, lo schema esportabile e i riepiloghi climatici
dovrebbero essere separati dalla UI, così da poterli riutilizzare. La
strategia concreta per mobile, distribuzione dei dataset e sincronizzazione
offline richiede una decisione architetturale futura. Su mobile la prima
vista può privilegiare lista/timeline compatta e aprire la mappa o i
dettagli su richiesta.

## 6. Dati online (OpenWeatherMap)

OpenWeatherMap è il candidato indicato per gli aggiornamenti online, ma
prima di implementarlo vanno verificati piano, prezzi, licenza, quota,
attribuzione richiesta, copertura geografica e orizzonte delle informazioni
effettivamente acquistate/consentite. Il riferimento a un piano gratuito e
al suo limite di chiamate è un'informazione da ricontrollare alla data di
adozione, non una garanzia permanente.

### Richiesta su iniziativa dell'utente

L'aggiornamento parte solo da un'azione esplicita, per esempio:

- “Aggiorna blocco attuale”;
- “Aggiorna blocco successivo”;
- “Aggiorna i blocchi per cui il servizio ha dati disponibili”.

Prima della richiesta, si può mostrare quanti punti o aree saranno
interrogati. Per contenere richieste e dati, campionare un numero limitato
di località rappresentative per blocco, non ogni punto GPX, e riusare la
cache finché le risposte sono considerate valide.

Le API online non devono bloccare l'interfaccia. Se la richiesta fallisce,
la pagina conserva i dati offline e mostra chiaramente l'errore e la data
dell'ultimo aggiornamento riuscito.

### Cosa mostrare e cosa non promettere

La UI può confrontare, per il blocco in corso o successivo, statistiche
offline e informazioni online recenti se il servizio selezionato copre le
date richieste. Una previsione a breve orizzonte non può essere estesa
artificialmente a un viaggio lontano nel tempo o a tutta la catena.

Per una richiesta “intero viaggio”, il sistema deve mostrare quali blocchi
sono coperti e quali no. Non deve sostituire i dati mancanti con una
previsione inventata, né presentare medie offline come previsioni aggiornate.

Ogni dato online deve mostrare fonte, orario di richiesta, periodo valido,
variabili e stato della cache. Le chiavi API non vanno inserite nel
repository o nei log; modalità di conservazione e gestione sicura della
chiave sono da definire per desktop e mobile.

## 7. Piano di implementazione a fasi

Le fasi sono una proposta ordinata per contenere il rischio. Ogni fase deve
avere test mirati, dati dimostrativi e un criterio di completamento prima di
procedere alla successiva.

| Fase | Contenuto e risultato verificabile | File/aree potenzialmente coinvolti | Rischio | Beneficio |
|---|---|---|---|---|
| **1 — Catena temporale e scenari in sola lettura** | Estrarre la logica di proiezione in un servizio riusabile; allinearla alle regole di durata dopo aver chiarito i conteggi; leggere ordine e tappe senza modificarli; mostrare tabella/timeline, gestire tappe o blocchi mancanti e provare scenari di spostamento/salto senza salvarli. Aggiungere test con blocchi piccoli, lunghi, vuoti e casi di date a cavallo d'anno. | `service/clima_service.py` o nuovo servizio di pianificazione; `app_desktop.py` e/o pagina GUI clima; test dedicati. | Medio: le regole temporali cambiano il comportamento esistente, ma la modalità sola lettura evita di alterare l'ordine ufficiale. | Catena completa e verificabile senza dipendenze climatiche né modifiche permanenti alla Gestione blocchi. |
| **2 — Dataset offline pilota e semaforo storico** | Confrontare un'area campione e un viaggio reale; selezionare WorldClim 2.1 o CHELSA e risoluzione solo dopo la verifica di variabili, licenza e peso; importare i raster fuori dal normale caricamento GUI; campionare la rotta, salvare i metadati e i riepiloghi mensili; introdurre spiegazione e copertura del semaforo. | Nuovo servizio/importatore climatico; nuovo schema e migrazione SQLite; `service/clima_service.py` o servizio separato; UI clima; test di estrazione e invalidazione. Eventuale `rasterio` va approvato prima di aggiungerlo alle dipendenze. | Alto: dati globali, licenze, qualità geografica, migrazioni e nuove dipendenze. Ridurre il rischio con un solo paese/blocco pilota e backup. | Prima valutazione basata su dati climatici locali disponibile offline, con peso e qualità misurati. |
| **3 — Conferma ordini, dati online e preparazione mobile** | Salvare scenari separatamente; aggiungere conferma esplicita, applicazione atomica a `blocchi_ordine` e possibilità di recupero; collegare la UI alla Gestione blocchi; integrare OpenWeatherMap solo dopo verifica di licenza, quote, copertura e credenziali; adattare presentazione e pacchetto dati all'obiettivo mobile. | `blocchi_ordine` e migrazione/schema scenari; `service/clima_service.py` e nuovo servizio online; `app_desktop.py`/Gestione blocchi; impostazioni sicure; futura UI mobile e distribuzione dati. | Alto: modifica dell'ordine ufficiale, credenziali, condizioni del fornitore e piattaforme non ancora presenti. | Flusso completo da scenario a scelta confermata, aggiornamenti a richiesta e base progettuale per la portabilità. |

### Criteri minimi prima di passare alla fase seguente

- **Dopo la fase 1:** le date risultano coerenti in tabella e timeline; lo
  spostamento o il salto di un blocco ricalcola tutta la catena e non cambia
  `blocchi_ordine` finché non si conferma.
- **Dopo la fase 2:** un viaggio campione è valutabile offline; ogni
  risultato identifica dataset e copertura; il peso installato e i tempi
  sono misurati; i fattori non disponibili restano dichiarati come tali.
- **Dopo la fase 3:** la conferma modifica l'ordine una sola volta in modo
  recuperabile; la richiesta online è esplicita e non blocca la UI; dati
  scaduti o non coperti sono distinguibili; il comportamento mobile è
  verificato su dispositivi/ambienti supportati prima di dichiararlo
  disponibile.

## 8. Domande aperte

1. **Dataset:** si sceglie WorldClim 2.1 o CHELSA? Quali variabili sono
   necessarie e quali sono realmente offerte con una licenza compatibile?
2. **Risoluzione e spazio:** 10m è sufficiente per il primo prodotto? Qual
   è il budget massimo di installazione e download per i dati climatici?
3. **Variabili mancanti:** come si valutano vento e neve se il dataset
   offline selezionato non li fornisce con copertura adeguata?
4. **Campionamento:** si accetta una media pesata lungo il tracciato? Quale
   granularità minima deve avere la valutazione di un blocco lungo?
5. **Durata:** il giorno di riposo scatta dopo ogni gruppo di cinque tappe o
   si arrotonda in altro modo? Come si conteggiano i cinque giorni extra per
   mese: mesi di calendario o periodi di 30 giorni?
6. **Semaforo:** quali soglie e pesi iniziali distinguono verde, giallo e
   rosso? Quanto deve pesare la preferenza caldo/pioggia?
7. **Dati insufficienti:** quale copertura minima è necessaria per
   assegnare un colore, e quando va mostrato “non valutabile”?
8. **Blocchi saltati:** significa rinviare il blocco, escluderlo dal viaggio
   o segnalarlo come trasferimento senza pedalata? Come si conserva e
   ripristina l'ordine precedente?
9. **Identità dei blocchi:** si introduce un ID stabile per non basare
   scenari e dati climatici sui soli nomi?
10. **OpenWeatherMap:** quali piano, orizzonte e variabili sono effettivamente
    necessari? Chi fornisce e conserva la chiave API nell'uso personale o
    nella distribuzione?
11. **Mobile:** quali sistemi/dispositivi sono prioritari e quale parte
    dell'esperienza deve funzionare offline senza raster sorgente?
12. **Accettazione:** quali limiti di tempo, memoria, spazio e ritardo della
    UI definiscono “leggera” su desktop e mobile?

Finché queste risposte non sono concordate, le scelte di dataset, semaforo,
durata esatta e sincronizzazione con l'ordine ufficiale restano proposte da
validare, non requisiti tecnici già chiusi.
