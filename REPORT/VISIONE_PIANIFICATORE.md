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

- Quali POI cercare? (tutti? solo alcuni?)
- Come risolvere il problema di GeoNames? (fonte più completa? 
  fallback?)
- Quali layer implementare? (satellitare? altri?)
- Quali informazioni del "Contenuto mappa" abbiamo davvero?
- Come si integra il pianificatore con il diario di bordo?
- Come si integra il pianificatore con il sito web?