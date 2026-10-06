# PERCORSO

## Settimana 1
- Migrazione GraphHopper avviata
- Implementazione contesto pianificatore
- Chiusura sotto-fase 5.1: timeout differenziato e correzione della coda
- Refactor BikepackingStudioApp ridotta a shell (Fase 7)
- Refactor deduplica i metodi tappe/progetti tra app e dashboard (Fase 6)
- Refactor pagine di servizio in gui/pagine/ (Fase 5)

## Settimana 2
- Refactor EstrazioneClimaWorker in gui/worker_clima.py (Fase 4)
- Refactor sposta i dialoghi in moduli dedicati (Fase 3)
- Refactor app_desktop.py: rimosso codice morto e import inutilizzati (-82 righe)
- Refactor mappa Fase 3.4: estrai pannello dettagli rotta
- Refactor mappa Fase 3.3c: ciclo analisi superfici nel GestoreWorkerSingolo
- Refactor mappa Fase 3.3b: ciclo nomi dei luoghi nel GestoreWorkerSingolo
- Refactor mappa Fase 3.3a: GestoreWorkerSingolo e ciclo altimetria

## Settimana 3
- Refactor mappa Fase 3.2: logica del form punti di passaggio in service/punti_service.py
- Aggiornato piano refactor: sezione Fase 3 con dettaglio sotto-fasi
- Refactor mappa Fase 3.1: etichette punti e testi elenco tappe intermedie in service/punti_service.py
- Etichetta_punto come funzione pura, poi elenco tappe intermedie. Rischio: basso
- Refactor mappa Fase 3.0: worker, barra superfici, dialogo mappe e cache in moduli dedicati
- Parte 2 refactor mappa.py

## Settimana 4
- Report
- Chiarimenti alla visione su 'parte di viaggio' e tema chiaro
- Progettazione UX del pianificatore percorso
- Analisi del pianificatore percorso
- Rigenera i report dopo il refactor completo di app_desktop
