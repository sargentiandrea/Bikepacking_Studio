# Visione — Catena Stagionale

Questo documento descrive la direzione desiderata della pagina, non
l'implementazione attuale né un piano tecnico. Le fonti climatiche, le API e
le modalità di rappresentazione dei dati restano decisioni aperte: non sono
indicate come già scelte.

## 1. Il principio guida

> Il viaggio segue le coste, procede sempre in avanti (meno trasferimenti
> possibile), e sfrutta le stagioni. L'obiettivo è pedalare sempre al caldo:
> nel mondo c'è sempre un posto dove è estate.

La pagina aiuta a mettere in scena il viaggio nel tempo e nello spazio.
Mostra le conseguenze delle scelte e aiuta a trovare una sequenza stagionale
più adatta, ma non prende decisioni al posto del viaggiatore.

“Sempre al caldo” è l'orientamento del progetto, non una garanzia
meteorologica: le condizioni e l'incertezza dei dati dovranno essere visibili.

## 2. La struttura del viaggio

Il viaggio è rappresentato come una sequenza ordinata di blocchi geografici,
per esempio Italia, Africa, India e Sud-Est asiatico.

| Livello | Significato |
|---|---|
| Viaggio | L'insieme dei blocchi del progetto |
| Blocco | Una sezione geografica che può essere pianificata e spostata come unità |
| Tappa | Un file GPX, collocato nell'ordine previsto all'interno del blocco |

La sequenza dei blocchi è definita nella pagina **Gestione blocchi** e
registrata in `blocchi_ordine`. La sequenza delle tappe dentro un blocco
segue l'ordine dei file GPX.

La catena stagionale parte da questa struttura invece di crearne una
parallela. Può proporre di spostare, anticipare, posticipare o saltare un
blocco per ragioni climatiche; le conseguenze sull'intero viaggio devono
essere mostrate prima di confermare una modifica.

La preferenza è mantenere il viaggio in avanti e ridurre trasferimenti e
ritorni. Se una proposta comporta un'eccezione, per esempio un salto o un
trasferimento, la pagina deve renderla evidente e spiegare il compromesso.

## 3. La proiezione temporale

La durata pianificata di ogni blocco si costruisce con queste regole guida:

| Regola | Durata aggiunta |
|---|---:|
| Tappa | 1 giorno di pedalata |
| Riposo ordinario | 1 giorno ogni 5 tappe |
| Imprevisti ordinari | 5 giorni per ogni mese di viaggio |
| Imprevisti maggiori | 1 settimana ogni 4 mesi |

La persona può configurare la data di partenza. La proiezione assegna a ogni
blocco una data di ingresso e una data di uscita, propagando le durate
attraverso tutta la sequenza.

Gli imprevisti sono margini di pianificazione, non giorni di pedalata.
L'interfaccia dovrebbe distinguerli dalla durata base e rendere chiaro come
contribuiscono alle date mostrate. La regola precisa per conteggiare mesi e
settimane, soprattutto ai confini tra blocchi, va definita prima
dell'implementazione.

Ogni modifica alla sequenza, alla data di partenza o alle durate ricalcola
l'intera catena. La persona deve poter confrontare lo scenario aggiornato
con quello precedente, senza perdere il contesto del viaggio.

## 4. La catena stagionale

La pagina deve rappresentare **tutto il viaggio**, sia che contenga 10 tappe
sia che ne contenga 2.000, come una catena di blocchi datati.

Per ogni blocco mostra:

- nome e posizione nella sequenza;
- date previste di ingresso e uscita;
- condizioni climatiche attese per il periodo e l'area attraversata;
- semaforo verde, giallo o rosso;
- motivi leggibili del giudizio, per esempio temperatura, pioggia, vento o
  neve, se i dati disponibili consentono di valutarli;
- eventuali margini o incertezze dei dati.

Il colore non deve essere un verdetto opaco. Deve essere accompagnato da una
spiegazione concreta: quali condizioni hanno contribuito al risultato,
quali soglie sono state applicate e quali dati sono mancanti o incerti.

La pagina può suggerire di anticipare, posticipare o saltare un blocco per
incastrare meglio il clima. Deve inoltre mostrare l'effetto della proposta
sui blocchi successivi, sulle date finali e sui trasferimenti richiesti.
L'utente sceglie se applicarla.

Una modifica proposta è uno scenario: non cambia silenziosamente l'ordine
ufficiale di **Gestione blocchi**. La relazione tra scenario e sequenza
ufficiale dovrà essere definita, inclusa la modalità con cui un cambiamento
confermato viene riportato nella pagina di gestione.

## 5. I dati climatici

### Modalità offline — predefinita

La visione prevede statistiche climatiche locali, derivate da medie storiche
degli ultimi **30–50 anni** e conservate sul dispositivo. Devono poter
supportare l'analisi stagionale anche senza connessione.

Non è ancora stato deciso quale dataset usare, quale periodo storico
adottare, quale dettaglio geografico sia sufficiente o come distribuire e
aggiornare i dati. Questi elementi non vanno considerati disponibili finché
non saranno scelti e verificati.

### Modalità online — su richiesta

Quando lo decide l'utente, la pagina potrà richiedere informazioni
aggiornate per:

- il blocco successivo;
- il blocco in corso;
- l'intero viaggio.

L'obiettivo non è mostrare una previsione giorno per giorno. L'utente
controlla quando aggiornare i dati. Quali servizi possano fornire
informazioni aggiornate, per quale orizzonte temporale e con quali limiti
resta da decidere.

La schermata dovrà distinguere chiaramente:

| Tipo di informazione | Cosa rappresenta |
|---|---|
| Clima storico offline | Andamento statistico tipico di un periodo e di un'area |
| Informazione online aggiornata | Dato recente richiesto dall'utente, con copertura e validità dichiarate |
| Scenario di viaggio | Date e sequenza ipotizzate per i blocchi |

Le medie storiche non sono previsioni per l'anno specifico. I dati online
non devono essere presentati come disponibili oltre l'orizzonte che il
servizio scelto può sostenere.

## 6. Cosa conta per un periodo “buono”

La valutazione deve poter considerare una combinazione di:

- temperatura;
- pioggia;
- vento;
- neve.

Le soglie devono essere personalizzabili. Per esempio, una persona può
preferire il caldo anche se questo comporta più pioggia; un'altra può
considerare la pioggia il fattore più importante. La pagina deve rendere
visibile questa preferenza e spiegare come influisce sul semaforo.

Non sono ancora definite soglie, pesi o formule. Non vanno quindi
interpretati i colori come una classificazione già stabilita. Qualunque
criterio scelto dovrà spiegare:

1. quali fattori sono stati valutati;
2. quali limiti sono stati applicati;
3. quali fattori hanno pesato di più;
4. se mancano dati o se la valutazione è incerta.

## 7. Come deve apparire

La pagina è un punto di regia con tre viste coordinate:

| Vista | Scopo |
|---|---|
| Tabella | Elencare i blocchi con date, semafori e spiegazioni sintetiche |
| Calendario / timeline | Mostrare la successione e la durata dei blocchi nel tempo |
| Mappa | Mostrare i blocchi colorati in base alle condizioni del periodo pianificato |

Una selezione o una modifica in una vista dovrebbe mantenere coerenti le
altre, così che l'utente possa passare dalla visione d'insieme al dettaglio
senza perdere il punto del viaggio.

La presentazione deve rimanere leggibile anche quando la catena è lunga.
Su desktop può dare spazio alla vista d'insieme e ai dettagli; su iOS e
Android deve offrire una versione semplificata, mantenendo almeno sequenza,
date, semaforo, motivazione e possibilità di consultare gli scenari.

Le modalità precise di sincronizzazione tra viste e le interazioni mobile
non sono ancora definite.

## 8. Requisiti tecnici

I requisiti di prodotto sono:

- gestire l'intero viaggio, da 10 a 2.000 tappe;
- restare leggera e non appesantire l'app;
- funzionare offline come comportamento predefinito;
- aggiornare i dati online solo su richiesta;
- essere portabile su desktop, iOS e Android, con interfaccia mobile
  semplificata.

Il contesto segnala un'occupazione complessiva di circa **107 GB**, di cui
circa **80 GB** di mappe. Questi numeri sono un vincolo da considerare nella
progettazione dello spazio per i dati climatici; non stabiliscono da soli
quanto spazio possa essere assegnato né quale formato o tecnologia usare.

La visione non sceglie formati, architetture, dataset o servizi: la priorità
è definire cosa deve vedere e poter decidere l'utente, senza imporre ora una
soluzione tecnica non verificata.

## 9. Cosa NON è questa pagina

- Non è un semplice calcolatore di mesi ideali per singolo blocco.
- Non è una previsione meteorologica giorno per giorno.
- Non è uno strumento che decide la sequenza al posto dell'utente.
- Non presenta un semaforo senza spiegare le condizioni che lo determinano.
- Non confonde le medie climatiche storiche con una previsione certa per
  l'anno del viaggio.
- Non è una copia della pagina **Gestione blocchi**: usa la sequenza del
  viaggio come base per costruire e confrontare scenari.

È uno strumento di **regia**: rende visibili il viaggio, le stagioni e le
conseguenze delle opzioni, lasciando la decisione finale alla persona.

## 10. Domande aperte

| Tema | Decisione ancora necessaria |
|---|---|
| Clima offline | Quali dataset usare? Quali anni coprire, quale dettaglio geografico e quale spazio locale richiedere? |
| Dati online | Quali API o servizi usare, che copertura e orizzonte offrono, e come dichiararne i limiti? |
| Soglie | Come combinare temperatura, pioggia, vento e neve? L'utente imposta soglie, priorità o entrambe? |
| Semaforo | Quali regole distinguono verde, giallo e rosso? Come mostrare dati mancanti e incertezza? |
| Viaggio lungo | Come mantenere leggibile una catena di 2.000 tappe, soprattutto su mobile, senza appesantire l'app? |
| Blocchi e scenari | Come una proposta della catena stagionale interagisce con l'ordine ufficiale in **Gestione blocchi**? Quando e come viene confermata? |
| Imprevisti | Come conteggiare i 5 giorni per mese e la settimana ogni 4 mesi ai confini tra blocchi e nel confronto tra scenari? |
| “Sempre al caldo” | Quali condizioni minime definiscono “caldo” e come rappresentare i casi in cui il clima o i dati disponibili non permettono di raggiungere l'obiettivo? |

Queste decisioni sono parte della definizione della funzione. Finché restano
aperte, la pagina può mostrare ipotesi e scenari, ma non dovrebbe presentare
le relative valutazioni come una verità climatica assoluta.
