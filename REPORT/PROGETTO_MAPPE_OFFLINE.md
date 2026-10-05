# Progetto: Gestione Mappe Offline e struttura dati su R2

Documento di sola analisi e progettazione. **Nessun file di codice è stato
modificato.**

Data: 03/10/2026
Riferimenti: `gui/mappa_manager.py`, `service/map_manager_service.py`,
`data/maps/`, `service/clima_service.py`, `data/clima/`

---

## 0. Il quadro in una riga

Il pannello attuale mostra 4 mappe italiane. Sul disco ci sono già **61
mappe** con nomi italiani, e nessuna delle due cose combacia. Questo
disallineamento è il punto di partenza obbligatorio: prima di progettare
qualcosa di nuovo, va capito perché il codice e la realtà divergono.

---

## 1. Analisi del pannello attuale

### 1.1 Dove sta

| File | Righe | Ruolo |
|---|---|---|
| `gui/mappa_manager.py` | 107 | dialog e unione, nessuna logica dati |
| `service/map_manager_service.py` | 117 | catalogo hardcoded + worker download |
| `gui/mappa.py` riga 471 | - | punto di apertura del dialog |

Separazione corretta: la GUI non sa nulla del download, il servizio non
sa nulla di Qt (salvo il worker, che è un caso noto).

### 1.2 Cosa fa

```
selezione voce  -> descrizione in basso
pulsante Scarica -> DownloadWorker (QThread) -> requests.get(stream) -> .tmp -> rename
fine            -> MessageBox -> refresh_catalog()
```

Scaricamento in `.tmp` e rinomina finale: corretto, evita file a metà.

### 1.3 Come è strutturato

**Dati.** Una lista Python hardcoded, `AVAILABLE_MAPS`, con 4 dizionari:

| Campo | Tipo | Esempio |
|---|---|---|
| `id` | str | `italy_north_vector` |
| `name` | str | "Italia Nord & Alpi (Zoom 0-14)" |
| `region` | str | "Italia" |
| `size_mb` | int | 420 |
| `description` | str | testo libero |
| `url` | str | URL R2 |

Lo stato "installato" **non** è nel catalogo: viene calcolato a ogni
chiamata controllando se il nome file esiste in `data/maps/`.

**UI.** `QListWidget` piatto, 600x450. Ogni riga è una stringa composta:

```
[Italia] Italia Nord & Alpi (Zoom 0-14) — ~420 MB (⬇️ Scaricabile)
```

**Download.** Un solo file per volta, un solo set di dati (le `.mbtiles`).

### 1.4 Cosa non regge

| Problema | Conseguenza |
|---|---|
| Catalogo hardcoded | 4 voci, nessun'altra area del mondo |
| `region` è una stringa libera | non raggruppabile, niente albero |
| `size_mb` dichiarato a mano | può divergere dalla realtà |
| Solo `.mbtiles` | routing, ricerca e clima non c'entrano |
| Un download per volta | 3 set per area = 3 viaggi |
| Nessuna verifica integrità | download interrotto = file corrotto silenzioso |
| Nessuna ripresa | un'interruzione da 25 GB ricomincia da zero |
| URL divergenti | vedi sezione 2.1 |

---

## 2. Il disallineamento trovato

Tre cose non tornano. Le riporto perché cambiano la progettazione.

### 2.1 URL diversi

| Fonte | Endpoint |
|---|---|
| Codice (`map_manager_service.py`) | `pub-625e91d94b7f446d86e485da84fabd05.r2.dev` |
| Contesto del compito | `bb71a8ad05624cf2b434008e06f74b1b.r2.cloudflarestorage.com` |

Ho provato tutti e tre gli endpoint plausibili:

| Endpoint | Risultato |
|---|---|
| `bb71a8ad...r2.cloudflarestorage.com` | errore SSL (non raggiungibile via HTTPS) |
| `bb71a8ad...r2.dev` | HTTP 500 |
| `pub-625e91...r2.dev` | HTTP 404 |

**Nessuno dei tre è utilizzabile così com'è.** Il bucket esiste (il
`.r2.dev` risponde 500, non 404 su tutto), ma serve l'endpoint pubblico
giusto o le credenziali. Va chiarito prima della 6.1.

### 2.2 Sul disco ci sono 61 mappe, non 4

`data/maps/` contiene file con **nomi italiani** e dimensioni reali:

| File | MB | File | MB |
|---|---|---|---|
| `america-nord.mbtiles` | 25.523 | `italia.mbtiles` | 1.699 |
| `asia.mbtiles` | 25.233 | `francia.mbtiles` | 3.495 |
| `africa.mbtiles` | 7.880 | `russia.mbtiles` | 10.052 |
| `oceania.mbtiles` | 3.718 | `spagna.mbtiles` | 1.336 |
| `albania.mbtiles` | 66 | `malta.mbtiles` | 6 |
| `andorra.mbtiles` | 3 | `monaco.mbtiles` | 0,4 |

Più continentsi **e** paesi, mescolati nella stessa cartella. C'è anche
una cartella `ITALIA` che risulta **vuota**.

Il pannello attuale non ne mostra nessuna: `get_installed_maps()` le
legge ma il catalogo non le include, quindi sono **invisibili all'utente**.

### 2.3 Il clima non è un file per area

`data/clima/` contiene solo `chelsa_progetto_1.json` e
`chelsa_progetto_24.json`, che **non sono dati climatici**: sono metadati
che descrivono il dataset e dichiarano:

```json
"metodo": "Lettura COG via HTTP range; raster globali non scaricati integralmente.",
"endpoint_cog": "https://os.unil.cloud.switch.ch/chelsa02",
"righe_sqlite": 540
```

Il modello attuale è: **il clima si legge da remoto per progetto**, non si
scarica per area. Funziona, ma è incompatibile con "scarica qualsiasi
area del mondo offline".

**Non propongo di cambiarlo.** Le due cose sono diverse e possono
coesistere: R2 per GraphHopper e GeoNames, lettura COG per il clima. Ma va
detto chiaramente, perché "tre set di dati scaricabili" è una premessa
che oggi **non è vera** per il terzo.

---
## 3. Progettazione: struttura su R2

### 3.1 Principio

Un file per **paese e tipo di dato**, in cartelle che si leggono da sole.
Niente metadati dentro il nome del file, niente cataloghi duplicati.

```
v1/
├── catalog.json
├── bin/
│   └── graphhopper-web-11.1.jar
├── graphhopper/
│   ├── it/
│   │   ├── it.tar.gz
│   │   └── meta.json
│   ├── fr/
│   │   ├── fr.tar.gz
│   │   └── meta.json
│   └── ...
├── geonames/
│   ├── it/
│   │   ├── IT.zip
│   │   └── IT-admin1.zip
│   └── ...
├── clima/
│   ├── it/
│   │   └── chelsa_it.tif
│   └── ...
└── mappe/
    ├── it/
    │   └── it.mbtiles
    └── ...
```

### 3.2 Le chiavi

**Nome file = codice ISO 3166-1 alpha-2 in minuscolo** (`it`, `fr`, `af`).

| Perché ISO e non il nome italiano |
|---|
| Alfabetico, quindi i paesi si ordinano bene |
| Nessun problema con accenti (`città` contro `citta`) |
| Non dipende dalla lingua dell'interfaccia |
| È lo standard che GeoNames usa già (`IT.zip`) |

I nomi italiani per l'interfaccia stanno nel `catalog.json`, non nel nome
del file. Le due cose non si confondono.

### 3.3 Il catalog.json

Un solo file all'origine della verità. L'app lo scarica all'apertura del
pannello (sono pochi KB) e costruisce l'albero da lì.

```json
{
  "versione": 1,
  "generato_il": "2026-10-03T00:00:00Z",
  "continenti": [
    {
      "codice": "EU",
      "nome": "Europa",
      "paesi": [
        {
          "codice": "it",
          "nome": "Italia",
          "dati": {
            "graphhopper": {
              "chiave": "graphhopper/it/it.tar.gz",
              "mb": 412,
              "sha256": "...",
              "data": "2026-10-01"
            },
            "geonames": {
              "chiave": "geonames/it/IT.zip",
              "mb": 68,
              "sha256": "...",
              "data": "2026-09-15"
            },
            "mappa": {
              "chiave": "mappe/it/it.mbtiles",
              "mb": 1699,
              "sha256": "...",
              "data": "2026-10-01"
            }
          }
        }
      ]
    }
  ]
}
```

Un tipo di dato assente semplicemente **non c'è** nel dizionario: l'app
mostra grigio quel tipo, senza inventare nulla.

| Campo | Serve a |
|---|---|
| `mb` | stimare il download e lo spazio |
| `sha256` | **verificare che il download sia integro** |
| `data` | capire se i dati sono freschi |
| `versione` | compatibilità del formato grafo |

### 3.4 GraphHopper: un file per paese

Ogni `tar.gz` contiene `graph-cache/` pronto, più un `meta.json`:

```json
{
  "stato": "importato",
  "nodi": 4820000,
  "archi": 7100000,
  "km": 2400,
  "graphhopper_version": "11.1",
  "profili": ["bike", "racingbike", "mtb"]
}
```

**Vincoli da rispettare**, verificati nella 6.0:

| Vincolo | Dettaglio |
|---|---|
| Importare costa memoria | 2-6 GB per l'Italia, 8+ per paesi grandi |
| Il grafo vale per un solo profilo | CH di `bike` diverso da CH di `racingbike` |
| I CH vanno dichiarati | senza `profiles_ch` si perdono le prestazioni |
| I CH vanno ripreparati al cambio | cambia un profilo e il grafo va rifatto |

Il `meta.json` serve a una cosa precisa: **non far importare all'utente**.
Un utente non ha 6 GB di RAM da dedicare a un import. Il grafo si prepara
una volta e si distribuisce già pronto.

### 3.5 Il jar: una volta sola, non per paese

`graphhopper-web-11.1.jar` pesa **45 MB** e non cambia da paese a paese.
Metterlo in ogni cartella significa 45 MB duplicati per ogni nazione.

Sta una volta sola in `v1/bin/`, e il `meta.json` dichiara la versione
richiesta. L'app scarica il jar solo se non c'è già quello giusto. Italia
e Algeria lo condividono.
### 3.6 GeoNames: il formato più semplice

GeoNames pubblica già un file per paese con sigla ISO: `IT.zip`, `FR.zip`,
`DZ.zip`. Nessuna conversione necessaria.

Ogni `IT.zip` contiene `IT.txt` (~1,5 MB compressi) con circa 50.000
località: sono i dati che `cerca_coordinate_luogo` già usa.

Va deciso se mettere anche `admin1` (regioni): serve se un giorno si vuole
"Toscana" come voce di ricerca. **Opzionale.**

### 3.7 Clima: la scelta

Tre opzioni, in ordine di raccomandazione:

| Opzione | Come | Pro | Contro |
|---|---|---|---|
| A. **Tenere il COG** | si legge online come oggi | nessun costo, nessuno spazio | non è davvero offline |
| B. Raster per paese su R2 | TIFF per area | offline vero | 10-30 MB per paese, da generare |
| C. Pre-elaborato per progetto | come i JSON attuali ma con i dati | minimo | non riusabile fra progetti |

**Consiglio: A per ora.** Il meteo non è la ragione per cui si scarica una
mappa, e B richiede un altro tipo di competenza (ritagliare i COG). Se un
giorno serve l'offline vero, B è il passo giusto e si fa senza cambiare
l'interfaccia.

---
## 4. Progettazione: l'interfaccia

### 4.1 Un albero, non una lista

Il cambiamento minimo che risolve il 90% del problema: `QTreeWidget` con
due livelli.

```
▾ Europa
    ▾ 🇮🇹 Italia                 [🗺 ✓] [🧭 ✓] [🔍 ✓]
        ▸ 🇫🇷 Francia              [🗺 ✓] [🧭 –] [🔍 –]
        ▸ 🇪🇸 Spagna               [🗺 ✓] [🧭 ✓] [🔍 ✓]
▸ Africa
    ▸ 🇩🇿 Algeria               [🗺 –] [🧭 ✓] [🔍 ✓]
    ▸ 🇿🇦 Sudafrica             [🗺 ✓] [🧭 –] [🔍 ✓]
▾ Asia
    ▸ 🇦🇫 Afghanistan           [🗺 –] [🧭 –] [🔍 ✓]
```

Tre colonne di stato, una per tipo di dato: mappa, routing, ricerca.
`**✓**` installato, `**–**` non disponibile. Si legge senza spiegazioni.

### 4.2 Il pannello

```
┌────────────────────────────────────────────────────────┐
│ 🔍 [ cerca un paese…            ]      Aggiorna elenco  │
├──────────────────────────────┬─────────────────────────┤
│  Europa                      │  🇦🇫 Afghanistan         │
│  ▾ 🇮🇹 Italia      🗺✓ 🧭✓ 🔍✓│  Asia                    │
│    🇫🇷 Francia    🗺✓ 🧭– 🔍–│  ─────────────────────   │
│    🇪🇸 Spagna       🗺✓ 🧭✓ 🔍✓│  Mappa        non dispon.│
│  ▸ Africa                    │  Routing      non dispon.│
│  ▸ Asia                      │  Ricerca       68 MB    │
│  ▸ America                   │                         │
│  ▸ Oceania                   │  [Scarica ricerca]       │
│  ▸ Antartide                 │                         │
├──────────────────────────────┴─────────────────────────┤
│ Spazio libero: 42,3 GB                                    │
│ ███████████████░░░░░░░░  Italia / Routing   184 MB       │
└────────────────────────────────────────────────────────┘
```

Tre zone con una funzione ciascuna: **scegliere** (albero), **capire**
(destra), **scaricare** (in basso). Niente altri pulsanti.

### 4.3 Le regole dell'interfaccia

| Regola | Perché |
|---|---|
| Massimo **3** tipi di dato per paese | sono quelli che servono; altro è rumore |
| Un tipo assente è grigio, non assente | si vede che il pannello funziona |
| Spazio libero sempre visibile | evita il "disco pieno" a metà download |
| Un download alla volta | oggi è così, e semplifica molto |
| Nessun doppio click nascosto | ogni azione ha un pulsante visibile |
| Un pulsante solo: **Scarica** | se serve altro, si vede dopo il click |

L'ultima è la più importante. Tre icone nella colonna di stato, **un**
pulsante a destra. Se un utente clicca "Ritira", non deve comparire una
finestra con quattro opzioni.

### 4.4 Scaricare tutto il paese in un colpo

Il caso più frequente è "sto andando in bici in Francia e voglio tutto
pronto". Un pulsante secondario, sotto quello principale:

```
[ Scarica ]              [ Scarica tutto (214 MB) ]
```

La differenza è 1 click e fa risparmiare tre viaggi separati.

### 4.5 I 61 file già sul disco

Non si cancellano. Si **adottano**: al primo avvio il pannello cerca i
file esistenti in `data/maps/` e, se il nome corrisponde a un paese del
catalogo, lo segna come installato anche senza `sha256`.

I file che non corrispondono a nessun paese (i continentali, la cartella
`ITALIA` vuota) restano sul disco e semplicemente non compaiono. Non li
cancello: non mi è stato chiesto e non è il mio posto.

---

## 5. Progettazione: come finiscono i dati sul PC

### 5.1 Dove vanno

Oggi `data/maps/` sta dentro il progetto. La nuova struttura va in
`%LOCALAPPDATA%\BikepackingStudio\`, come già fanno BRouter e GeoNames.

| Tipo | Cartella | Nota |
|---|---|---|
| Cataloghi | `catalog/` | json scaricati |
| Mappe | `mappe/` | `.mbtiles` |
| GraphHopper | `graphhopper/` | una cartella per paese + jar |
| GeoNames | `geonames/` | gli `IT.zip` |
| Logs | `log/` | scaricamenti falliti |

È la stessa impostazione già presente in `service/config.py` per
`BROUTER_HOME` e `GEONAMES_HOME`: una sola convenzione, non due.

**Perché spostare:** `data/maps/` è dentro la cartella del progetto, che
finisce spesso dentro git o su una chiavetta. 61 file da 110 GB in una
cartella di sviluppo è una fonte di problemi.

### 5.2 Come si evita il file scaricato a metà

Il `.tmp` di oggi va bene, ma mancano due cose.

**Verifica finale.** Dopo il download si calcola lo `sha256` e si
confronta con il catalogo. Se non coincide, il file si cancella.

```
### 5.3 Spazio necessario

Dati reali misurati su `data/maps/`:

| Area | Mappa | Routing (stima) | Ricerca |
|---|---|---|---|
| Italia | 1,7 GB | 0,4 GB | 68 MB |
| Francia | 3,5 GB | 0,5 GB | 90 MB |
| Spagna | 1,3 GB | 0,4 GB | 70 MB |
| Algeria | 0,1 GB | 0,3 GB | 40 MB |

Per il solo Italia: circa **2,2 GB**. Per l'Europa intera: circa
**25-30 GB**. Su una macchina con 111 GB liberi è gestibile, ma va detto
all'utente prima, non dopo.

---


## 6. Piano di lavoro

Cinque passi, ognuno utile da solo.

| Passo | Cosa | Rischio | Perché prima |
|---|---|---|---|
| **A** | Chiarire l'endpoint R2 | nullo | senza, nient'altro si può testare |
| **B** | `catalog.json` su R2 con l'Italia | basso | dato minimo per far funzionare il pannello |
| **C** | Pannello ad albero + adozione dei 61 file | basso | il salto di interfaccia vero |
| **D** | Download con `sha256` e ripresa | medio | affidabilità |
| **E** | Migrazione su `LOCALAPPDATA` | medio | da fare presto, prima che ci siano molti GB |

Il passo A è bloccante e non è tecnico: **è una domanda, non un lavoro.**

### Ordine consigliato

A, poi B e C insieme (il pannello nuovo vale quanto i dati che mostra), poi
D, poi E.

---

## 7. Rischi e mitigazioni

| # | Rischio | Probabilità | Impatto | Mitigazione |
|---|---|---|---|---|
| 1 | **Endpoint R2 non raggiungibile** | **certa** | alto | passo A prima di tutto; va chiarito con chi gestisce il bucket |
| 2 | 61 file già scaricati non nel catalogo | certa | medio | passo C li adotta invece di ignorarli |
| 3 | 110 GB di `.mbtiles` non spostati | alta | alto | passo E, prima che crescano |
| 4 | Import GraphHopper per ogni paese | media | alto | si distribuisce il grafo pronto, non si importa sul PC |
| 5 | Profili diversi richiedono grafi diversi | media | medio | `profili` nel meta.json; l'app avvisa se non c'è il profilo |
| 6 | `sha256` assente per i file vecchi | certa | basso | si accetta l'installato senza verifica, con un segno diverso |
| 7 | Chiusa di R2 (S3 API) non va bene | media | alto | usare l'endpoint pubblico `.r2.dev`, non l'S3 |
| 8 | Un paese senza GeoNames | bassa | basso | la colonna resta grigia, il resto funziona |
| 9 | Clima non offline | **certa** | basso | è una scelta dichiarata, non un bug |
| 10 | L'albero con 200 paesi è rumoroso | media | basso | ricerca testuale e paesi recenti in cima |

Il rischio 1 è l'unico che blocca davvero, e non è risolvibile con codice.

---

## 8. Cosa non so

| # | Domanda | Perché è importante |
|---|---|---|
| 1 | **Quale endpoint R2 funziona?** | Nessun download è possibile senza. |
| 2 | **Chi prepara i grafi GraphHopper?** | Se sei solo tu, ogni paese costa un import da 2-6 GB |
| 3 | **Come si genera `catalog.json`?** | A mano, da uno script, o con un upload? |
| 4 | **Il clima deve diventare offline?** | Oggi non lo è. Va deciso, non lasciato in sospeso |
| 5 | **Le 61 mappe sono tutte utili?** | Continenti da 25 GB e paesi da 3 MB nello stesso elenco |
| 6 | **Chi ha scaricato quei file?** | Se erano un test, potrebbero non servire tutti |
| 7 | **Quant'è lo spazio su R2?** | 200 paesi con grafi potrebbe non entrare nel piano |

Le domande 1 e 2 bloccano. Le altre si possono rispondere strada facendo.

---

## 9. Conclusione

Il lavoro è fattibile, ma non inizia dal pannello: **inizia dai dati**.

Tre scelte da fare subito, in quest'ordine:

1. **Chiarire l'endpoint R2.** Tutto il resto dipende da questo.
2. **Un solo `catalog.json`** al posto del catalogo hardcoded. È la
   differenza fra 4 mappe e tutto il mondo.
3. **Un albero a due livoli** con tre colonne di stato. Non un elenco.

E una constatazione che vale più delle altre: il codice e la realtà
divergono già. Sul disco ci sono 61 mappe che l'interfaccia non mostra, e
i tre URL R2 provati non funzionano. Rimettere in sincrono codice e dati
è il primo lavoro, ed è meno IMPORTANTE di quanto sembri solo perché
nessuno se ne accorge: le mappe ci sono, l'utente non le vede e non lo
sa.

Nessun file di codice è stato modificato.
scarica -> .part -> sha256 -> conforme? -> rinomina in finale
                                     no -> cancella e avvisa
```

**Ripresa.** Si scrive in `.part` con richieste HTTP `Range`, e al
riavvio si chiede `HEAD` per sapere quanto manca. Un'interruzione su
`asia.mbtiles` (25 GB) non deve costringere a ricominciare.