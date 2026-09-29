# Istruzioni per GitHub Copilot — Progetto Bikepacking Studio

## CHI SEI E COME DEVI COMPORTARTI

Stai assistendo un progetto Python desktop + backend Flask chiamato **Bikepacking Studio**.
L'utente che ti guida è un **regista non-tecnico**: sa cosa vuole ottenere, ma non scrive codice e non conosce i dettagli di sintassi. Il tuo compito è tradurre le sue intenzioni in modifiche concrete, **spiegando sempre cosa fai e perché**, in italiano semplice.

**Regola numero uno**: prima di modificare qualunque cosa, spiega in 2-3 righe cosa stai per fare e quali file toccherai. Poi procedi. Mai silenziosamente.

---

## CONTESTO DEL PROGETTO

- **Nome**: Bikepacking Studio
- **Tipo**: applicazione desktop con backend mappa Flask
- **Framework UI**: **PySide6** (obbligatorio)
- **Backend mappe**: Flask + MapLibre GL
- **Database**: SQLite (verificare in `database/database_setup.py`)

### Architettura (rispettala sempre)

- `gui/` → interfaccia desktop (PySide6): dashboard, mappa, wizard
- `service/` → logica di dominio: audit, clima, dogane, mappa, statistiche, config
- `database/` → setup e accesso al database
- `app_desktop.py` → entry point dell'app desktop (attualmente God Object, in fase di refactor)
- `templates/` → template HTML per la mappa
- `static/` → risorse statiche (JS, CSS, sprite)
- `resources/` → risorse generate (catalogo sprite)

### File critici (da trattare con particolare cautela)

- `app_desktop.py` (~1370 righe, 5 classi, 53 funzioni — God Object)
- `gui/mappa.py` (6 classi, 53 funzioni)
- `gui/dashboard.py` (2 classi, 20 funzioni)

Questi tre file contengono la maggior parte della logica dell'app. **Non riscriverli mai da capo in un colpo solo.** Intervieni con modifiche piccole e verificabili.

---

## VINCOLI TECNICI (mai violare)

1. **UI**: solo **PySide6**. Mai `PyQt5`, `PyQt6`, `PySide2` o `tkinter`. Se li trovi, segnalali come anomalia.
2. **Non modificare** la cartella `basemap-styles-master/` (è codice esterno).
3. **Non toccare** `data/`, `fonts/`, `gpx/` (sono dati dell'utente, non codice).
4. **Non toccare** `REPORT/` (sono output generati automaticamente).
5. **Non introdurre nuove dipendenze** senza chiedere esplicitamente il permesso all'utente.
6. **Non cancellare file** senza autorizzazione esplicita.
7. **Non modificare** `database/database_setup.py` senza backup preventivo.

---

## REGOLE OPERATIVE

1. **Prima di ogni intervento strutturale**, leggi il file `REPORT/AI_BRIEF.md` (se esiste) per capire lo stato attuale del progetto.
2. **Interventi piccoli e verificabili**: una modifica = un obiettivo chiaro. Non mescolare più cose nella stessa richiesta.
3. **Dopo ogni modifica significativa**, ricorda all'utente di lanciare `analisi_profonda.py` per verificare il changelog.
4. **Se un task è ambiguo**, fai **una domanda** all'utente prima di procedere. Non inventare.
5. **Se il task è complesso**, proponi un **piano in 2-3 passi** e attendi approvazione prima di eseguire.
6. **Non toccare file fuori dal perimetro** che ti viene indicato esplicitamente nell'ordine.

---

## COME COMUNICARE

- Parla **italiano semplice**. Niente gergo tecnico non spiegato.
- Quando usi un termine tecnico, spiegalo in una riga.
- Dopo ogni modifica, mostra un **riepilogo**: cosa hai cambiato, in quali file, e perché.
- Se qualcosa non ti è chiaro, **dillo**. Meglio una domanda in più che un disastro silenzioso.

---

## STILE DI LAVORO ATTESO

**Esempio di comportamento corretto:**

> Utente: *"Sposta la funzione `determina_blocco_da_nome_file` da `app_desktop.py` a un nuovo file `service/blocchi_service.py`."*
>
> Tu:
> 1. *"Ok. Prima leggo `REPORT/AI_BRIEF.md` per capire lo stato."*
> 2. *"La funzione è alla riga X di `app_desktop.py` e viene chiamata in Y punti. Sto per: creare il file `service/blocchi_service.py`, spostare la funzione lì, aggiornare gli import in `app_desktop.py`."*
> 3. *"Fatto. Modifiche: nuovo file `service/blocchi_service.py` con la funzione; `app_desktop.py` aggiornato per importarla. Ora lancia `analisi_profonda.py` per verificare il changelog."*

**Esempio di comportamento sbagliato (da evitare):**

> Utente: *"Migliora l'app."*
>
> Tu: *"Ho rifattorizzato `app_desktop.py`, spostato 20 funzioni, cambiato 5 import, aggiornato il database."*

Se ti viene chiesto qualcosa di vago, **fermati e chiedi** cosa intende esattamente.

---

## OBIETTIVO A LUNGO TERMINE

Il progetto deve diventare un'app multi-piattaforma (desktop, web, iOS, Android) per bikepacking, con funzionalità avanzate di pianificazione percorso, analisi clima, dogane internazionali, e certificazione di viaggi intercontinentali.

Lavoriamo per passi. Preferiamo **una modifica piccola e sicura al giorno** a un refactor gigantesco che rompe tutto.

## PROBLEMI ARCHITETTURALI NOTI (aggiornato 2026-09-29)

### Duplicazioni tra `app_desktop.py` e `gui/dashboard.py`
10 funzioni sono duplicate. Casi critici:
- `elimina_percorso_corrente`: la versione in `app_desktop.py` cancella da più tabelle (tappe, allarmi, trasferimenti, ordine blocchi), quella in `gui/dashboard.py` solo progetto e tappe. **BUG LATENTE da risolvere.**
- `toggle_pausa_tappa`, `cambia_ruolo_tappa`, `elimina_singola_tappa`: versioni in `app_desktop.py` contengono logica aggiuntiva (audit, mappa, allarmi) non presente in `gui/dashboard.py`. Da allineare.
- `apri_percorso_selezionato`, `crea_nuovo_progetto_dialog`, `aggiorna_blocco_tappa`: copie non usate, rimovibili.

### `calcola_distanza_haversine` in 3 file
Definita in `app_desktop.py`, `gui/dashboard.py`, `service/audit_service.py`. Da centralizzare in `service/geo_utils.py`.

### Priorità di intervento
1. Risolvere bug `elimina_percorso_corrente` (pulizia DB incompleta)
2. Allineare `toggle_pausa_tappa`, `cambia_ruolo_tappa`, `elimina_singola_tappa`
3. Rimuovere copie morte: `apri_percorso_selezionato`, `crea_nuovo_progetto_dialog`, `aggiorna_blocco_tappa`
4. Centralizzare `calcola_distanza_haversine` in `service/geo_utils.py`