# Cronologia Git del ramo corrente

Scansione `558e703d664c0e3f` · 2026-10-09T18:57:49.096857+00:00 · script 4.0

Documento generato: fatti osservati e limiti dichiarati. Non certifica l’esecuzione dell’app.

Titoli dei commit riportati come dichiarazioni degli autori, non verifiche funzionali.
Ultimi 80 commit raggiungibili da HEAD. La storia dalle chat è in `STORIA_PROGETTO.md`.

| Data | Commit | Titolo |
|---|---|---|
| 2026-10-06T23:02:35+02:00 | 6361027b837f | Aggiorna memoria progetto (osservatore automatico) |
| 2026-10-06T00:54:12+02:00 | ad2a0d19561c | Lettura grafo mondo, report. |
| 2026-10-04T19:51:28+02:00 | 1b1e2addc44a | feat: devia le tracce con waypoint (5.4) |
| 2026-10-04T18:06:49+02:00 | 696e82d14727 | feat: suddivide i percorsi in tappe (5.3) |
| 2026-10-04T17:40:50+02:00 | 9ceb3b1550aa | feat: implementa il contesto del pianificatore (5.2) |
| 2026-10-04T02:16:31+02:00 | ea63ddfef25d | docs: piano di migrazione da BRouter a GraphHopper |
| 2026-10-04T01:47:51+02:00 | 05787480a9b1 | Chiusura sotto-fase 5.1: timeout differenziato e correzione della coda. |
| 2026-10-04T00:48:23+02:00 | 044271666db0 | Sotto-fase 5.1 del redesign del pianificatore: timeout, feedback, coda, firma. |
| 2026-10-04T00:22:09+02:00 | 12ec723e6b20 | docs: chiarimenti alla visione su 'parte di viaggio' e tema chiaro |
| 2026-10-04T00:08:31+02:00 | 8809198184c0 | docs: progettazione UX del pianificatore percorso |
| 2026-10-03T23:45:29+02:00 | 1846c7c74835 | docs: analisi del pianificatore percorso |
| 2026-10-03T23:33:19+02:00 | 0ebb844d8b80 | docs: rigenera i report dopo il refactor completo di app_desktop |
| 2026-10-03T23:25:55+02:00 | 5f54da7d48bf | refactor: BikepackingStudioApp ridotta a shell (Fase 7) |
| 2026-10-03T22:59:16+02:00 | f62d30528e70 | refactor: deduplica i metodi tappe/progetti tra app e dashboard (Fase 6) |
| 2026-10-03T22:45:31+02:00 | 20e095893dd2 | refactor: pagine di servizio in gui/pagine/ (Fase 5) |
| 2026-10-03T22:27:16+02:00 | 6428987ccf25 | refactor: EstrazioneClimaWorker in gui/worker_clima.py (Fase 4) |
| 2026-10-03T22:16:51+02:00 | 0200ce47ed54 | refactor: sposta i dialoghi in moduli dedicati (Fase 3) |
| 2026-10-03T22:00:17+02:00 | 27b21e9cb81f | Fase 2 refactor app_desktop.py: widget Blocchi e Timeline in moduli gui/ dedicati (SQL in service/blocchi_ordine_service.py) |
| 2026-10-03T21:56:01+02:00 | b315600263c5 | Fase 1 refactor app_desktop.py: rimosso codice morto e import inutilizzati (-82 righe) |
| 2026-10-03T12:19:56+02:00 | bc3fc48ac05e | Report |
| 2026-10-03T12:12:38+02:00 | cde6dd5611d7 | Fase 3.5: pannello pianificatore in mappa_pianificatore.py |
| 2026-10-03T11:57:54+02:00 | b1785b5b2250 | Refactor mappa Fase 3.4: estrai pannello dettagli rotta |
| 2026-10-03T11:40:30+02:00 | 7ca0afa394a7 | Refactor mappa Fase 3.3c: ciclo analisi superfici nel GestoreWorkerSingolo |
| 2026-10-03T11:39:59+02:00 | d45d4a564778 | Refactor mappa Fase 3.3b: ciclo nomi dei luoghi nel GestoreWorkerSingolo |
| 2026-10-03T11:39:05+02:00 | a103df317520 | Refactor mappa Fase 3.3a: GestoreWorkerSingolo e ciclo altimetria |
| 2026-10-03T11:28:34+02:00 | 5e773f97a454 | Refactor mappa Fase 3.2: logica del form punti di passaggio in service/punti_service.py |
| 2026-10-03T11:25:34+02:00 | ad1c23cbb315 | Aggiornato piano refactor: sezione Fase 3 con dettaglio sotto-fasi |
| 2026-10-03T11:09:05+02:00 | ecfbbd3bf039 | Refactor mappa Fase 3.1: etichette punti e testi elenco tappe intermedie in service/punti_service.py |
| 2026-10-03T11:06:20+02:00 | 418e4ddfa375 | 3.1: etichetta_punto come funzione pura, poi elenco tappe intermedie. Rischio: basso |
| 2026-10-03T10:55:18+02:00 | 6301dedd6cd1 | Refactor mappa Fase 3.0: worker, barra superfici, dialogo mappe e cache in moduli dedicati |
| 2026-10-03T10:37:08+02:00 | a9c9ac5c300f | parte 2 refactor mappa.py |
| 2026-10-03T10:24:42+02:00 | 9cf2d74860ce | Fix: trascinamento traccia, distanza in pixel al posto di LngLat.dist |
| 2026-10-03T10:13:18+02:00 | 5f01818f10e8 | Fix: import mancante di calcola_distanza_haversine in app_desktop |
| 2026-10-03T09:54:16+02:00 | 2f555b1a954e | Refactor mappa Fase 2: servizi dati mappa e salvataggio tappa |
| 2026-10-03T09:45:22+02:00 | 542f124cc2bd | Fase 1 refactor: geo_utils.py (6 copie rimosse, 3 funzioni in meno) |
| 2026-10-03T09:27:49+02:00 | 6ba8db078a80 | Refactor mappa Fase 1.1: centralizza haversine in service/geo_utils.py |
| 2026-10-03T09:23:35+02:00 | 8976c16b17a4 | Fix timer polling: ferma anche quando scarta eventi di altri progetti |
| 2026-10-03T09:03:36+02:00 | a6b7e6f0ccc7 | Fix bug in cancel_interaction: Esc sulla mappa non crasha più |
| 2026-10-03T01:25:07+02:00 | 4903917f137f | Fase 3 Catena Stagionale completata: soglie, scenari, conferma |
| 2026-10-02T23:42:10+02:00 | 502f0f1a8b10 | Pulizia DB e risolto bug sui trasferimenti. |
| 2026-10-02T21:31:04+02:00 | 956f990274ec | Catena stagionale per paese: semafori granulari, estrazione CHELSA per ISO3 |
| 2026-10-02T14:41:49+02:00 | 47ed738cfaa2 | Aggiornate istruzioni Copilot: nuovi servizi, problemi noti, principi fondativi |
| 2026-10-02T01:24:49+02:00 | 3df71ca6ae4e | Fase 1 Catena Stagionale: catena temporale con timeline e scenari in sola lettura |
| 2026-10-02T00:31:41+02:00 | 7a2783624fbb | Visione e piano Catena Stagionale: documento di riferimento per la nuova pagina |
| 2026-10-01T19:30:55+02:00 | 9cf0bd827c24 | Globo 3D attivo (MapLibre 5.6.2): proiezione dinamica sotto zoom 3, debounce 200ms |
| 2026-10-01T18:42:43+02:00 | 313724843340 | Ripristinato pulsante "Apri nel browser" nella mappa |
| 2026-10-01T18:15:06+02:00 | 36f5685e4d39 | Capitolo precalcolo chiuso: mappa veloce, statistiche istantanee, cache funzionante |
| 2026-10-01T13:19:28+02:00 | 61865ebf7ebb | Precalcolo costa completo (992 tappe, 72s): Statistiche da 14s a 0,65s |
| 2026-10-01T09:25:42+02:00 | 5736cf8cd95a | Migrato stats_service a tappa_analisi (Step 6.1): lettore comune, copertura, pendenza ponderata |
| 2026-10-01T09:05:14+02:00 | bc8abc134144 | Collegato precalcolo al salvataggio da pianificatore (Step 5) |
| 2026-10-01T08:44:58+02:00 | c2366346c2b2 | Collegato precalcolo all'importazione (Step 4): gpx_metrics_service esteso, precalcolo_service creato, dashboard collegata |
| 2026-10-01T08:17:08+02:00 | 7590208ffe0a | Aggiunto gpx_metrics_service e migrazione DB (tappa_analisi, tappa_segmenti) |
| 2026-10-01T02:39:44+02:00 | c1285bd6aa1e | Fase_1 implementazione precalcolo |
| 2026-09-30T23:11:36+02:00 | 09ba1f7c9b11 | Passaggio a Broute e geonames in locale |
| 2026-09-30T15:31:16+02:00 | 242cc0af0d14 | Copilot evoluzione analisi profonda e aggiornamento file istruzioni. |
| 2026-09-29T23:32:24+02:00 | 3e38dc5741ec | Copilot - intervento creazione percorsi |
| 2026-09-29T20:08:26+02:00 | 589dd16a76ba | Aggiornamento istruzioni x Copilot |
| 2026-09-29T18:29:35+02:00 | efc6a3d75670 | Aggiunte duplicazioni a AI_BRIEF.md → Commit → Push |
| 2026-09-29T17:08:32+02:00 | 075f4fbe9e76 | Update audit_service.py |
| 2026-09-29T16:03:02+02:00 | e9ba2b9d1a28 | Aggiunto AI_BRIEF.md e istruzioni Copilot per il flusso di lavoro |
| 2026-09-28T15:07:24+02:00 | 5d35455b61cb | refactor: semplifica analisi AST in analizza_progetto_definitivo.py |
| 2026-09-28T15:07:20+02:00 | ba6f875b3740 | feat: aggiungi esportazione contesto JSONL e filtro per file |
| 2026-09-28T12:12:42+02:00 | 9ee9596445c9 | Modifiche effettuate con copilot il 2870972026 |
| 2026-09-27T20:28:21+02:00 | 4cccaaa3affc | fix: correggi sintassi lambda per wizard trasferimento |
| 2026-09-27T20:22:46+02:00 | 5eb5beb6112f | feat: gestisci permessi GPS direttamente in MappaWidget |
| 2026-09-27T19:59:24+02:00 | a9e61da213e8 | refactor: rimuovi metodi duplicati in WorkerCaricamentoMappa |
| 2026-09-27T17:47:18+02:00 | 314e960597d1 | Architettura Bikepacking Studio completa |
