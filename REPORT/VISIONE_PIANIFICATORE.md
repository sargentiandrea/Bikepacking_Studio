# Visione — Pianificatore Percorso

Questo documento descrive la direzione desiderata del pianificatore 
percorso. Non è un piano tecnico né un'analisi del codice attuale. 
Le funzionalità non ancora definite restano fuori, e verranno 
aggiunte quando le sezioni collegate saranno chiare.

## 1. Il principio guida

Il pianificatore serve a creare, modificare e gestire percorsi.
Deve essere **chiaro**, **fluido**, e deve **capire cosa l'utente 
sta facendo**. Non deve mai lasciare l'utente incerto su cosa sta 
succedendo o su cosa può fare dopo.

## 2. Interfaccia

### 2.1 Pulsanti laterali
- Ridotti a **icone** (con tooltip al passaggio del mouse)
- Il tooltip mostra il nome della pagina/funzione
- Stile coerente con Komoot (chiaro, minimale)

#### Chiarimento: il tema chiaro è previsto, ma è un progetto a parte

Il passaggio dal tema scuro attuale al tema chiaro **è desiderato**, ma
**non va mescolato con il redesign del pianificatore**.

**Perché separare i due lavori**

| Motivo | Spiegazione |
|---|---|
| Diverso ambito | Il redesign del pianificatore cambia il *cosa* si fa; il tema cambia il *come si vede*. Toccano cose diverse |
| Verifica indipendente | Se il tema viene fatto insieme, un problema di leggibilita si confonde con un problema di funzionalita |
| Rollback possibile | Se il tema chiaro non convince, si torna indietro senza perdere il lavoro sul pianificatore |
| Impatto trasversale | Il tema tocca tutte le pagine, non solo il pianificatore |

**Quali pagine tocca**

Il restyling riguarda **tutta l'applicazione**, non una sola pagina:

| Ambito | Cosa va cambiato |
|---|---|
| Le 9 pagine principali | Sfondo, colori dei testi e delle tabelle |
| La barra laterale di navigazione | Icone, hover, colore attivo |
| Il pianificatore e i suoi pannelli | Pannello principale, pannello opzioni, dettagli rotta |
| I dialog | Sfondo, pulsanti, campi di testo |
| La tabella delle tappe (dashboard) | Righe, intestazioni, alternanza |
| I message box | Sfondo e pulsanti |

**In quale momento farlo**

**Dopo** che il pianificatore e funzionalmente completo. La sequenza
consigliata e:

1. Prima si completa il pianificatore (contesto, suddivisione, deviazione)
2. Poi si fa un giro di coerenza visiva sul pianificatore da solo
3. **Solo dopo** si affronta il tema chiaro per tutta l'applicazione

**Regola pratica**: il tema chiaro non deve mai essere mescolato a una
funzionalita nuova. Se una modifica serve per far funzionare qualcosa, va
fatta nel tema corrente e il tema si affronta dopo, cosi un problema di
colore non maschera un problema di logica.

### 2.2 Pannello principale
- Più chiaro: **font leggibili**, **colori coerenti**, **spaziature 
  adeguate**
- Deve comunicare cosa sta succedendo (es. "Sto calcolando il 
  percorso...", "Percorso calcolato: 295 km")
- Non deve mai lasciare l'utente incerto

### 2.3 Pannello opzioni (separato)
- Non nel pannello principale
- Contiene: contenuto mappa, profilo bici, velocità media, cosa 
  visualizzare

## 3. Partenza e arrivo

Quattro modalità di input:
1. **Posizione attuale** (da GPS)
2. **Posizioni salvate** (Casa, Lavoro, Meccanico, ...)
3. **Ricerca** (nome città, luogo, POI)
4. **Click sulla mappa**

### 3.1 Ricerca
- Deve trovare **città**, **luoghi**, **POI** (ristoranti, hotel, 
  campeggi, fontane, ...)
- **Non** deve trovare indirizzi specifici (via Ferrari n. 46) — se 
  ci riesce, meglio, ma non è un requisito
- **Problema noto**: GeoNames non copre tutto (es. alcuni paesi non 
  vengono trovati). Serve una fonte più completa o un fallback.

## 4. Contesto (cosa stai creando)

Prima di creare una traccia, l'utente deve specificare **cosa sta 
creando**:
- **Tappa unica** (una tappa singola, es. Modena-Napoli)
- **Percorso** (un percorso completo, da suddividere in tappe)
- **Parte di un viaggio** (un blocco di un viaggio più grande)
- **Test tecnico** (una prova, non un percorso reale)

**La scelta avviene al momento della creazione** (o del salvataggio):
- Se "tappa unica": nessuna suddivisione, si salva e basta
- Se "percorso": si apre il pannello di suddivisione in tappe
- Se "parte di un viaggio": si integra nella struttura esistente
- Se "test": si salva come bozza, non nel database principale

**La scelta può essere modificata in un secondo momento** (in 
"Modifica percorso").

### 4.1 Chiarimento: cosa significa operativamente "parte di un viaggio"

Il blocco è un insieme di tappe **contigue e ordinate** all'interno di un
percorso: si usa per raggruppare ("Tappa 1-2: Sardegna", "Tappa 3: Sicilia")
e serve al calcolo della catena stagionale (clima per blocco).

I blocchi esistono già nel modello dati: la tabella `blocchi_ordine`
associa a ogni progetto una lista ordinata di blocchi (nome e posizione),
e ogni tappa ha il campo `blocco` che ne indica l'appartenenza.

Quando l'utente sceglie **"parte di un viaggio"**, il sistema deve
chiedergli **a quale blocco appartiene**, offrendo due possibilità:

| Scelta | Quando si usa | Cosa fa il sistema |
|---|---|---|
| **Aggiungi a un blocco esistente** | Il blocco c'è già (es. lo ha creato prima con "gestione blocchi", o c'è già una tappa con quel nome) | Il menu propone i blocchi già presenti nel percorso; la nuova tappa viene accodata in fondo a quel blocco, con la sequenza corretta |
| **Crea un nuovo blocco** | L'utente raggruppa per la prima volta | Il sistema chiede il nome del blocco, lo inserisce in `blocchi_ordine` e vi mette dentro la tappa |

**Regole**:

- Se il percorso non ha ancora blocchi, si propone direttamente
  "Crea un nuovo blocco" (non si parte da una scelta vuota)
- Il nome del blocco è **obbligatorio** e viene mostrato nella tabella
  delle tappe, così l'utente vede subito a cosa ha assegnato la tappa
- La scelta "aggiungi a un blocco esistente" o "creane uno nuovo" è
  ricordata per le tappe successive: non va riscritta ogni volta
- Il blocco così creato è **modificabile e riordinabile** in seguito dalla
  pagina "Gestione blocchi", che già esiste

**Perché è importante**: senza questa chiarezza, "parte di un viaggio"
non è implementabile. Il sistema deve sapere *dove* mettere la tappa, e la
risposta è il blocco.

### 4.2 Chiarimento: il contesto "tappa unica" e la suddivisione

La suddivisione non e disponibile solo per "percorso": anche dopo aver
salvato una "tappa unica" il sistema puo chiedere "Vuoi suddividere il
percorso in tappe?" (vedi sezione 7). In quel caso il contesto passa da
"tappa unica" a "percorso" e si applica la sezione 5.

## 5. Suddivisione in tappe

- **Km medi per tappa** E **numero di giorni** (entrambi)
- L'utente sceglie quale usare (per opportunità, non perché serva 
  veramente)
- Se l'utente imposta 550 km su un percorso di 500 km, sarà **una 
  tappa unica**
- Se l'utente imposta 1 giorno su un percorso di 500 km, sarà **una 
  tappa unica** (di 500 km)
- Komoot funziona così: l'utente ragiona a km o a giorni

## 6. Punti di passaggio

- **Aggiungere un punto di passaggio** = **deviare la traccia** 
  esistente (non creare una nuova traccia)
- **I km e i dati tecnici** si aggiornano di conseguenza
- **Se il punto è già sulla tappa**: non serve crearlo
- **Se il punto è vicino a una tappa**: devia la **tappa più vicina**
- **Se il punto stravolge il percorso** (es. Modena-Roma con Firenze 
  in mezzo): ricalcola **tutto il percorso** (diventa Modena-Firenze-Roma)
- Il comportamento deve essere **fluido** (come Komoot)

## 7. Azioni dopo la creazione

Dopo aver creato una traccia, l'utente può:
- **Salva percorso** (nella struttura giusta: tappa, percorso, parte 
  di viaggio)
- **Modifica percorso** (torna al pianificatore)
- **Suddividi in tappe** (se non l'ha fatto)

**Se l'utente sceglie "tappa unica" e salva**: 
- Possibile conferma: "Vuoi suddividere il percorso in tappe?"
- Se sì: si apre il pannello di suddivisione
- Se no: si salva come tappa unica

**Se l'utente sceglie "percorso" e salva**:
- Si apre il pannello di suddivisione in tappe

## 8. Pannello opzioni (separato)

Contiene:
- **Contenuto mappa** (layer, POI, ...)
- **Profilo bici** (gravel, bici da viaggio, ...)
- **Velocità media** (per stimare i tempi)
- **Cosa visualizzare** (solo se i dati esistono)

### 8.1 Contenuto mappa (riferimento Komoot)
Komoot offre:
- Immagini Trail View
- Luoghi salvati
- Indicatori di distanza
- Punti salienti (Punti Salienti, Punti Salienti del Segmento)
- Luoghi (Alloggi, Aree per bambini, Bancomat, Bar e ristoranti, 
  Campeggi, Fontane pubbliche, Funivie e seggiovie, Hotspot, 
  Luoghi di interesse naturale, Negozi, Officine per bici, Panchine 
  e aree picnic, Parcheggi, Parchi, Passi di montagna, Per cani, 
  Punti di interesse, Punti di timbratura credenziali, Rifugi, 
  Servizi pubblici, Spiagge e piscine, Stazioni di ricarica per 
  e-bike, Stazioni di servizio, Stazioni e fermate)

**Noi dobbiamo capire quali di queste informazioni abbiamo o 
potremo avere.** È inutile dare la possibilità di visualizzarle 
se non le abbiamo.

## 9. Layer mappa

- **Oggi**: solo OpenStreetMap
- **Domani**: mappa satellitare + altre (come GPX Studio)
- **I layer NON vanno nel pannello principale** (vanno in un menu 
  separato, o nelle impostazioni)
- **Non vogliamo implementarli tutti** (come GPX Studio), ma quasi

## 10. Cosa manca (da definire in futuro)

- **Trasferire il percorso a un navigatore** (Garmin, Wahoo, ...)
- **Collegare il percorso a un sito web** e al **diario di bordo** 
  dell'app
- **Condividere il percorso** (condividi, invita un amico a pedalare 
  con te)
- Altre funzionalità non ancora definite

**Non vanno implementate ora**: verranno affrontate quando le 
sezioni collegate saranno chiare.

## 11. Domande aperte

**Risolte** (si veda `PROGETTO_PIANIFICATORE.md` per i dettagli):
- ~~Cosa significa "parte di un viaggio"?~~ → **risolto nella sezione 4.1**:
  blocco esistente o nuovo blocco
- ~~Il tema deve essere chiaro?~~ → **risolto nella sezione 2.1**: sì,
  ma come progetto separato e successivo al redesign del pianificatore

**Ancora aperte:**
- Quali POI cercare? (tutti? solo alcuni?)
- Come risolvere il problema di GeoNames? (fonte più completa? 
  fallback?)
- Quali layer implementare? (satellitare? altri?)
- Quali informazioni del "Contenuto mappa" abbiamo davvero?
- Come si integra il pianificatore con il diario di bordo?
- Come si integra il pianificatore con il sito web?