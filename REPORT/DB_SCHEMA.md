# Schema SQLite applicativo

Scansione `558e703d664c0e3f` · 2026-10-09T18:57:49.096857+00:00 · script 4.0

Documento generato: fatti osservati e limiti dichiarati. Non certifica l’esecuzione dell’app.

Database: `data/bikepacking_app.db`. Stato: letto_in_sola_lettura.

## `allarmi_percorso`

Righe: 5.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| id | INTEGER | False | 1 | None |
| id_progetto | INTEGER | False | 0 | None |
| tappa_origine_id | INTEGER | False | 0 | None |
| tappa_destinazione_id | INTEGER | False | 0 | None |
| tipo_allarme | TEXT | False | 0 | None |
| messaggio | TEXT | False | 0 | None |
| risolto | INTEGER | False | 0 | 0 |

| Indice | Univoco | Colonne |
|---|---|---|

| FK | Destinazione | ON DELETE |
|---|---|---|
| id_progetto | progetti.id | NO ACTION |

## `anagrafica_paesi`

Righe: 198.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| codice_iso2 | TEXT | False | 1 | None |
| nome_paese | TEXT | False | 0 | None |
| regione_area | TEXT | False | 0 | None |
| passaporto | TEXT | False | 0 | None |
| visto | TEXT | False | 0 | None |
| valuta | TEXT | False | 0 | None |
| roaming | TEXT | False | 0 | None |
| drone | TEXT | False | 0 | None |
| bici | INTEGER | False | 0 | None |

| Indice | Univoco | Colonne |
|---|---|---|
| sqlite_autoindex_anagrafica_paesi_1 | True | codice_iso2 |

| FK | Destinazione | ON DELETE |
|---|---|---|

## `anagrafica_paesi_mondo`

Righe: 12.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| codice_iso2 | TEXT | False | 1 | None |
| nome | TEXT | False | 0 | None |
| regione | TEXT | False | 0 | None |
| passaporto | TEXT | False | 0 | None |
| visto | TEXT | False | 0 | None |
| valuta | TEXT | False | 0 | None |
| roaming | TEXT | False | 0 | None |
| drone | TEXT | False | 0 | None |
| bici | INTEGER | False | 0 | None |

| Indice | Univoco | Colonne |
|---|---|---|
| sqlite_autoindex_anagrafica_paesi_mondo_1 | True | codice_iso2 |

| FK | Destinazione | ON DELETE |
|---|---|---|

## `blocchi_ordine`

Righe: 24.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| id | INTEGER | False | 1 | None |
| id_progetto | INTEGER | False | 0 | None |
| nome_blocco | TEXT | False | 0 | None |
| ordine | INTEGER | False | 0 | None |

| Indice | Univoco | Colonne |
|---|---|---|

| FK | Destinazione | ON DELETE |
|---|---|---|
| id_progetto | progetti.id | NO ACTION |

## `blocchi_stagione`

Righe: 18.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| id | INTEGER | False | 1 | None |
| id_progetto | INTEGER | False | 0 | None |
| nome_blocco | TEXT | False | 0 | None |
| giorni_extra | INTEGER | False | 0 | 0 |
| mesi_ideali | TEXT | False | 0 | '04,05,06,09,10' |
| mesi_ideali_custom | TEXT | False | 0 | NULL |

| Indice | Univoco | Colonne |
|---|---|---|
| sqlite_autoindex_blocchi_stagione_1 | True | id_progetto, nome_blocco |

| FK | Destinazione | ON DELETE |
|---|---|---|

## `cache_geo_paesi`

Righe: 2.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| lat_griglia | REAL | False | 1 | None |
| lon_griglia | REAL | False | 2 | None |
| codice_iso2 | TEXT | False | 0 | None |
| nome_paese_riconosciuto | TEXT | False | 0 | None |

| Indice | Univoco | Colonne |
|---|---|---|
| sqlite_autoindex_cache_geo_paesi_1 | True | lat_griglia, lon_griglia |

| FK | Destinazione | ON DELETE |
|---|---|---|

## `cache_nomi_luoghi`

Righe: 999.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| lat_arrotondata | REAL | True | 1 | None |
| lon_arrotondata | REAL | True | 2 | None |
| nome | TEXT | False | 0 | None |
| calcolato_il | TEXT | False | 0 | None |

| Indice | Univoco | Colonne |
|---|---|---|
| sqlite_autoindex_cache_nomi_luoghi_1 | True | lat_arrotondata, lon_arrotondata |

| FK | Destinazione | ON DELETE |
|---|---|---|

## `clima_blocco_mese`

Righe: 288.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| id_progetto | INTEGER | True | 1 | None |
| nome_blocco | TEXT | True | 2 | None |
| mese | INTEGER | True | 3 | None |
| temperatura_media | REAL | False | 0 | None |
| temperatura_max | REAL | False | 0 | None |
| temperatura_min | REAL | False | 0 | None |
| precipitazioni_mm | REAL | False | 0 | None |
| vento_media | REAL | False | 0 | None |
| dataset_versione | TEXT | True | 0 | None |
| aggiornato_il | TEXT | True | 0 | None |
| copertura_pct | REAL | True | 0 | 0 |
| campioni_validi | INTEGER | True | 0 | 0 |
| campioni_totali | INTEGER | True | 0 | 0 |
| anni_coperti | TEXT | True | 0 | '{}' |

| Indice | Univoco | Colonne |
|---|---|---|
| idx_clima_blocco_mese_progetto | False | id_progetto, nome_blocco |
| sqlite_autoindex_clima_blocco_mese_1 | True | id_progetto, nome_blocco, mese |

| FK | Destinazione | ON DELETE |
|---|---|---|

## `clima_paese_mese`

Righe: 3432.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| id_progetto | INTEGER | True | 1 | None |
| paese | TEXT | True | 2 | None |
| mese | INTEGER | True | 3 | None |
| temperatura_media | REAL | False | 0 | None |
| temperatura_max | REAL | False | 0 | None |
| temperatura_min | REAL | False | 0 | None |
| precipitazioni_mm | REAL | False | 0 | None |
| vento_media | REAL | False | 0 | None |
| dataset_versione | TEXT | True | 0 | None |
| aggiornato_il | TEXT | True | 0 | None |
| copertura_pct | REAL | True | 0 | 0 |
| campioni_validi | INTEGER | True | 0 | 0 |
| campioni_totali | INTEGER | True | 0 | 0 |
| anni_coperti | TEXT | True | 0 | '{}' |

| Indice | Univoco | Colonne |
|---|---|---|
| idx_clima_paese_mese_progetto | False | id_progetto, paese |
| sqlite_autoindex_clima_paese_mese_1 | True | id_progetto, paese, mese |

| FK | Destinazione | ON DELETE |
|---|---|---|

## `confini_box`

Righe: 11.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| id | INTEGER | False | 1 | None |
| codice_iso2 | TEXT | False | 0 | None |
| lat_min | REAL | False | 0 | None |
| lat_max | REAL | False | 0 | None |
| lon_min | REAL | False | 0 | None |
| lon_max | REAL | False | 0 | None |

| Indice | Univoco | Colonne |
|---|---|---|

| FK | Destinazione | ON DELETE |
|---|---|---|

## `dogane_percorso`

Righe: 0.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| id | INTEGER | False | 1 | None |
| id_progetto | INTEGER | False | 0 | None |
| paese_origine | TEXT | False | 0 | None |
| paese_destinazione | TEXT | False | 0 | None |

| Indice | Univoco | Colonne |
|---|---|---|

| FK | Destinazione | ON DELETE |
|---|---|---|

## `dogane_progetto`

Righe: 67.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| id | INTEGER | False | 1 | None |
| id_progetto | INTEGER | False | 0 | None |
| ordine_progressivo | INTEGER | False | 0 | None |
| codice_iso2 | TEXT | False | 0 | None |
| paese_nome | TEXT | False | 0 | None |
| regione_area | TEXT | False | 0 | None |
| requisito_passaporto | TEXT | False | 0 | None |
| tipo_visto | TEXT | False | 0 | None |
| valuta | TEXT | False | 0 | None |
| roaming_info | TEXT | False | 0 | None |
| drone_policy | TEXT | False | 0 | None |
| transitabile_bici | INTEGER | False | 0 | 1 |
| stato_valico | TEXT | False | 0 | None |
| valico_vicino_nome | TEXT | False | 0 | None |
| valico_vicino_dist_km | REAL | False | 0 | None |

| Indice | Univoco | Colonne |
|---|---|---|

| FK | Destinazione | ON DELETE |
|---|---|---|
| id_progetto | progetti.id | NO ACTION |

## `impostazioni_semaforo`

Righe: 0.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| id_progetto | INTEGER | False | 1 | None |
| temp_min_verde | REAL | False | 0 | 15.0 |
| temp_max_verde | REAL | False | 0 | 28.0 |
| temp_min_giallo | REAL | False | 0 | 5.0 |
| temp_max_giallo | REAL | False | 0 | 35.0 |
| pioggia_max_verde | REAL | False | 0 | 50.0 |
| pioggia_max_giallo | REAL | False | 0 | 100.0 |
| vento_max_verde | REAL | False | 0 | 20.0 |
| vento_max_giallo | REAL | False | 0 | 35.0 |
| priorita_caldo | INTEGER | False | 0 | 1 |
| aggiornato_il | TEXT | False | 0 | None |

| Indice | Univoco | Colonne |
|---|---|---|

| FK | Destinazione | ON DELETE |
|---|---|---|

## `progetti`

Righe: 3.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| id | INTEGER | False | 1 | None |
| nome_progetto | TEXT | True | 0 | None |
| descrizione | TEXT | False | 0 | None |
| km_totali | REAL | False | 0 | 0 |
| stato | TEXT | False | 0 | 'ATTIVO' |
| data_creazione | TEXT | False | 0 | None |

| Indice | Univoco | Colonne |
|---|---|---|

| FK | Destinazione | ON DELETE |
|---|---|---|

## `progetto_stagione`

Righe: 1.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| id_progetto | INTEGER | False | 1 | None |
| data_partenza | TEXT | False | 0 | None |
| modificatore_riposo | INTEGER | False | 0 | 0 |

| Indice | Univoco | Colonne |
|---|---|---|

| FK | Destinazione | ON DELETE |
|---|---|---|

## `scenari`

Righe: 1.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| id | INTEGER | False | 1 | None |
| id_progetto | INTEGER | True | 0 | None |
| nome | TEXT | True | 0 | None |
| ordine_json | TEXT | True | 0 | None |
| creato_il | TEXT | True | 0 | None |
| applicato | INTEGER | False | 0 | 0 |
| ordine_precedente_json | TEXT | False | 0 | None |
| annullato | INTEGER | False | 0 | 0 |

| Indice | Univoco | Colonne |
|---|---|---|

| FK | Destinazione | ON DELETE |
|---|---|---|

## `superfici_tappa`

Righe: 984.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| id | INTEGER | False | 1 | None |
| tappa_id | INTEGER | False | 0 | None |
| dati_json | TEXT | False | 0 | None |
| calcolato_il | TEXT | False | 0 | None |

| Indice | Univoco | Colonne |
|---|---|---|
| sqlite_autoindex_superfici_tappa_1 | True | tappa_id |

| FK | Destinazione | ON DELETE |
|---|---|---|
| tappa_id | tappe.id | NO ACTION |

## `tappa_analisi`

Righe: 986.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| tappa_id | INTEGER | False | 1 | None |
| gpx_sha256 | TEXT | True | 0 | None |
| versione_algoritmi | TEXT | True | 0 | None |
| distanza_km | REAL | False | 0 | None |
| dislivello_pos_m | REAL | False | 0 | None |
| dislivello_neg_m | REAL | False | 0 | None |
| quota_min_m | REAL | False | 0 | None |
| quota_max_m | REAL | False | 0 | None |
| pendenza_media_pct | REAL | False | 0 | None |
| pendenza_max_pct | REAL | False | 0 | None |
| bbox_min_lon | REAL | False | 0 | None |
| bbox_min_lat | REAL | False | 0 | None |
| bbox_max_lon | REAL | False | 0 | None |
| bbox_max_lat | REAL | False | 0 | None |
| stato | TEXT | True | 0 | None |
| errore | TEXT | False | 0 | None |
| aggiornato_il | TEXT | False | 0 | None |

| Indice | Univoco | Colonne |
|---|---|---|

| FK | Destinazione | ON DELETE |
|---|---|---|
| tappa_id | tappe.id | CASCADE |

## `tappa_costa_riepilogo`

Righe: 986.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| tappa_id | INTEGER | False | 1 | None |
| gpx_sha256 | TEXT | True | 0 | None |
| versione_algoritmo_costa | TEXT | True | 0 | None |
| versione_dataset_costa | TEXT | True | 0 | None |
| fascia_0_500m_km | REAL | True | 0 | 0 |
| fascia_500_2500m_km | REAL | True | 0 | 0 |
| fascia_2500_5000m_km | REAL | True | 0 | 0 |
| fascia_oltre_5000m_km | REAL | True | 0 | 0 |
| tappe_coinvolte_0_500m | INTEGER | True | 0 | 0 |
| tappe_coinvolte_500_2500m | INTEGER | True | 0 | 0 |
| tappe_coinvolte_2500_5000m | INTEGER | True | 0 | 0 |
| tappe_coinvolte_oltre_5000m | INTEGER | True | 0 | 0 |
| totale_km | REAL | True | 0 | 0 |
| calcolato_il | TEXT | True | 0 | None |
| gpx_size_bytes | INTEGER | False | 0 | None |
| gpx_mtime | REAL | False | 0 | None |

| Indice | Univoco | Colonne |
|---|---|---|

| FK | Destinazione | ON DELETE |
|---|---|---|
| tappa_id | tappe.id | CASCADE |

## `tappa_geometrie`

Righe: 985.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| tappa_id | INTEGER | False | 1 | None |
| gpx_sha256 | TEXT | True | 0 | None |
| versione_algoritmo | TEXT | True | 0 | None |
| geometria_completa | BLOB | True | 0 | None |
| geometria_semplificata | BLOB | True | 0 | None |
| bbox_min_lat | REAL | True | 0 | None |
| bbox_min_lon | REAL | True | 0 | None |
| bbox_max_lat | REAL | True | 0 | None |
| bbox_max_lon | REAL | True | 0 | None |
| numero_punti_originali | INTEGER | True | 0 | None |
| numero_punti_semplificati | INTEGER | True | 0 | None |
| aggiornato_il | TEXT | True | 0 | None |

| Indice | Univoco | Colonne |
|---|---|---|

| FK | Destinazione | ON DELETE |
|---|---|---|
| tappa_id | tappe.id | CASCADE |

## `tappa_segmenti`

Righe: 987.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| tappa_id | INTEGER | True | 1 | None |
| track_index | INTEGER | True | 2 | None |
| segment_index | INTEGER | True | 3 | None |
| punti | INTEGER | False | 0 | None |
| distanza_km | REAL | False | 0 | None |
| dislivello_pos_m | REAL | False | 0 | None |
| dislivello_neg_m | REAL | False | 0 | None |
| quota_min_m | REAL | False | 0 | None |
| quota_max_m | REAL | False | 0 | None |
| versione_algoritmi | TEXT | False | 0 | None |

| Indice | Univoco | Colonne |
|---|---|---|
| sqlite_autoindex_tappa_segmenti_1 | True | tappa_id, track_index, segment_index |

| FK | Destinazione | ON DELETE |
|---|---|---|
| tappa_id | tappe.id | CASCADE |

## `tappe`

Righe: 982.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| id | INTEGER | False | 1 | None |
| id_progetto | INTEGER | False | 0 | None |
| sequenza | INTEGER | False | 0 | None |
| blocco | TEXT | False | 0 | None |
| nome_file | TEXT | False | 0 | None |
| start_lat | REAL | False | 0 | None |
| start_lon | REAL | False | 0 | None |
| end_lat | REAL | False | 0 | None |
| end_lon | REAL | False | 0 | None |
| distanza_km | REAL | False | 0 | None |
| stato | TEXT | False | 0 | 'ATTIVA' |
| blocco_area | TEXT | False | 0 | None |
| nome_file_gpx | TEXT | False | 0 | None |
| km | REAL | False | 0 | 0 |
| ruolo | TEXT | False | 0 | None |
| paese | TEXT | False | 0 | None |

| Indice | Univoco | Colonne |
|---|---|---|

| FK | Destinazione | ON DELETE |
|---|---|---|
| id_progetto | progetti.id | NO ACTION |

## `trasferimenti`

Righe: 28.

| Colonna | Tipo | NOT NULL dichiarato | Posizione PK | Default |
|---|---|---|---|---|
| id | INTEGER | False | 1 | None |
| id_progetto | INTEGER | False | 0 | None |
| tipo_mezzo | TEXT | False | 0 | None |
| vettore | TEXT | False | 0 | None |
| da_luogo | TEXT | False | 0 | None |
| a_luogo | TEXT | False | 0 | None |
| durata | TEXT | False | 0 | None |
| costo_eur | REAL | False | 0 | None |
| note | TEXT | False | 0 | None |
| start_lat | REAL | False | 0 | None |
| start_lon | REAL | False | 0 | None |
| end_lat | REAL | False | 0 | None |
| end_lon | REAL | False | 0 | None |

| Indice | Univoco | Colonne |
|---|---|---|

| FK | Destinazione | ON DELETE |
|---|---|---|
| id_progetto | progetti.id | NO ACTION |

## Riferimenti SQL nel codice

Possono riguardare altri database; non sono il conteggio delle tabelle applicative.

| Prova | Tabelle candidate | SQL dinamico |
|---|---|---|
| import_clima_mondiale.py:87 |  | False |
| import_clima_mondiale.py:135 |  | False |
| installa_geonames.py:88 | geonames | False |
| installa_geonames.py:99 | geonames_names | False |
| installa_geonames.py:211 |  | False |
| installa_geonames.py:212 |  | False |
| installa_geonames.py:213 |  | False |
| installa_geonames.py:214 |  | False |
| installa_geonames.py:246 |  | False |
| installa_geonames.py:249 |  | False |
| installa_geonames.py:259 | geonames_names_fts | False |
| installa_geonames.py:262 | metadata | False |
| installa_geonames.py:273 |  | False |
| installa_geonames.py:274 | geonames | False |
| installa_geonames.py:277 | geonames_names | False |
| database/database_setup.py:9 |  | False |
| database/database_setup.py:18 |  | False |
| database/database_setup.py:29 |  | False |
| database/database_setup.py:40 |  | False |
| database/database_setup.py:45 |  | False |
| database/database_setup.py:47 |  | False |
| database/database_setup.py:59 |  | True |
| database/database_setup.py:63 | progetti | False |
| database/database_setup.py:68 |  | False |
| database/database_setup.py:85 |  | False |
| database/database_setup.py:98 |  | False |
| database/database_setup.py:117 |  | False |
| database/database_setup.py:141 |  | False |
| database/database_setup.py:156 |  | False |
| gui/dashboard.py:286 | tappe | False |
| gui/dashboard.py:289 | tappe | False |
| gui/dashboard.py:327 | tappe | False |
| gui/dashboard.py:339 | tappe | False |
| gui/dashboard.py:347 | tappe | False |
| gui/pagine/controller_clima.py:80 | progetto_stagione | False |
| gui/pagine/pagina_audit.py:54 | allarmi_percorso, tappe | False |
| gui/pagine/pagina_trasporti.py:53 | trasferimenti | False |
| gui/pagine/pagina_trasporti.py:75 | tappe | False |
| gui/pagine/pagina_trasporti.py:77 | tappe | False |
| service/audit_service.py:33 | blocchi_ordine, tappe | False |
| service/audit_service.py:43 | trasferimenti | False |
| service/audit_service.py:103 | tappe | False |
| service/audit_service.py:153 | tappe | False |
| service/audit_service.py:162 | allarmi_percorso | False |
| service/audit_service.py:170 | trasferimenti | False |
| service/audit_service.py:178 | allarmi_percorso | False |
| service/audit_service.py:211 | allarmi_percorso | False |
| service/audit_service.py:228 |  | False |
| service/audit_service.py:240 | trasferimenti_logistici | False |
| service/audit_service.py:258 | tappe | False |
| service/audit_service.py:260 | tappe | False |
| service/audit_service.py:322 | tappe | False |
| service/audit_service.py:327 | tappe | False |
| service/audit_service.py:333 | trasferimenti | False |
| service/blocchi_ordine_service.py:27 | tappe | False |
| service/blocchi_ordine_service.py:33 | blocchi_ordine | False |
| service/blocchi_ordine_service.py:58 | blocchi_ordine | False |
| service/blocchi_ordine_service.py:61 | blocchi_ordine | False |
| service/blocchi_ordine_service.py:68 | tappe | False |
| service/blocchi_ordine_service.py:75 | tappe | False |
| service/catena_stagionale_service.py:26 |  | False |
| service/catena_stagionale_service.py:35 |  | True |
| service/catena_stagionale_service.py:43 | sqlite_master | False |
| service/catena_stagionale_service.py:85 | tappe | True |
| service/catena_stagionale_service.py:115 | blocchi_ordine | False |
| service/catena_stagionale_service.py:415 |  | False |
| service/catena_stagionale_service.py:416 | scenari | False |
| service/catena_stagionale_service.py:426 | scenari | False |
| service/catena_stagionale_service.py:435 | scenari | False |
| service/catena_stagionale_service.py:451 | sqlite_master | False |
| service/catena_stagionale_service.py:459 | scenari | False |
| service/catena_stagionale_service.py:486 | sqlite_master | False |
| service/catena_stagionale_service.py:494 | scenari | False |
| service/catena_stagionale_service.py:513 | sqlite_master | False |
| service/catena_stagionale_service.py:521 | scenari | False |
| service/catena_stagionale_service.py:535 | blocchi_ordine | False |
| service/catena_stagionale_service.py:567 | tappe | False |
| service/catena_stagionale_service.py:590 |  | False |
| service/catena_stagionale_service.py:591 |  | False |
| service/catena_stagionale_service.py:593 | scenari | False |
| service/catena_stagionale_service.py:617 | blocchi_ordine | False |
| service/catena_stagionale_service.py:621 | blocchi_ordine | False |
| service/catena_stagionale_service.py:633 | scenari | False |
| service/catena_stagionale_service.py:659 |  | False |
| service/catena_stagionale_service.py:660 |  | False |
| service/catena_stagionale_service.py:662 | scenari | False |
| service/catena_stagionale_service.py:695 | blocchi_ordine | False |
| service/catena_stagionale_service.py:699 | blocchi_ordine | False |
| service/catena_stagionale_service.py:714 | scenari | False |
| service/catena_stagionale_service.py:796 | sqlite_master | False |
| service/catena_stagionale_service.py:804 | impostazioni_semaforo | False |
| service/catena_stagionale_service.py:833 | impostazioni_semaforo | False |
| service/catena_stagionale_service.py:875 | sqlite_master | False |
| service/catena_stagionale_service.py:904 | clima_paese_mese | False |
| service/catena_stagionale_service.py:911 | clima_paese_mese | False |
| service/clima_estrattore.py:97 |  | False |
| service/clima_estrattore.py:120 | tappe | True |
| service/clima_estrattore.py:379 |  | False |
| service/clima_estrattore.py:383 | clima_paese_mese | True |
| service/clima_estrattore.py:387 | clima_paese_mese | False |
| service/clima_service.py:55 |  | False |
| service/clima_service.py:64 |  | False |
| service/clima_service.py:76 |  | False |
| service/clima_service.py:81 |  | False |
| service/clima_service.py:94 | progetto_stagione | False |
| service/clima_service.py:105 | blocchi_stagione | False |
| service/clima_service.py:126 | progetto_stagione | False |
| service/clima_service.py:142 | blocchi_stagione | False |
| service/clima_service.py:149 |  | False |
| service/costa_service.py:81 | tappe | False |
| service/costa_service.py:207 | tappa_costa_riepilogo, tappe | False |
| service/costa_service.py:236 |  | False |
| service/costa_service.py:243 | tappa_costa_riepilogo | False |
| service/costa_service.py:277 |  | False |
| service/dogane_service.py:8 |  | False |
| service/dogane_service.py:11 |  | False |
| service/dogane_service.py:31 |  | False |
| service/dogane_service.py:86 | anagrafica_paesi | False |
| service/dogane_service.py:102 | dogane_progetto | False |
| service/geocodifica_offline_service.py:71 | tiles | False |
| service/geocodifica_offline_service.py:119 | cache_nomi_luoghi | False |
| service/geocodifica_offline_service.py:138 | cache_nomi_luoghi | False |
| service/geonames_service.py:28 | geonames, geonames_names, geonames_names_fts | False |
| service/map_server.py:248 | tappa_analisi, tappa_geometrie | False |
| service/mappa_dati_service.py:38 | tappe | False |
| service/mappa_dati_service.py:49 | trasferimenti | False |
| service/mappa_dati_service.py:75 | tappe | False |
| service/mappa_dati_service.py:94 | tappe | False |
| service/mappa_dati_service.py:135 | tappe | False |
| service/mappa_dati_service.py:148 | tappa_analisi, tappa_geometrie, tappe | False |
| service/mappa_dati_service.py:174 | cache_nomi_luoghi | False |
| service/mappa_dati_service.py:343 | trasferimenti | False |
| service/migrazione_catena_stagionale.py:25 |  | True |
| service/migrazione_catena_stagionale.py:40 | sqlite_master | False |
| service/migrazione_catena_stagionale.py:59 |  | False |
| service/migrazione_catena_stagionale.py:60 |  | False |
| service/migrazione_catena_stagionale.py:77 |  | False |
| service/migrazione_catena_stagionale.py:94 |  | False |
| service/migrazione_catena_stagionale.py:98 |  | False |
| service/migrazione_clima.py:31 | sqlite_master | False |
| service/migrazione_clima.py:44 |  | False |
| service/migrazione_clima.py:45 |  | False |
| service/migrazione_clima.py:66 |  | False |
| service/migrazione_clima.py:87 |  | False |
| service/migrazione_clima.py:93 |  | False |
| service/migrazione_tappa_analisi.py:38 |  | False |
| service/migrazione_tappa_analisi.py:41 | sqlite_master | False |
| service/migrazione_tappa_analisi.py:54 |  | False |
| service/migrazione_tappa_analisi.py:91 |  | False |
| service/migrazione_tappa_costa.py:39 | sqlite_master | False |
| service/migrazione_tappa_costa.py:50 | sqlite_master | False |
| service/migrazione_tappa_costa.py:64 |  | False |
| service/migrazione_tappa_costa.py:66 |  | False |
| service/migrazione_tappa_costa_metadati.py:41 | sqlite_master | False |
| service/migrazione_tappa_costa_metadati.py:55 |  | False |
| service/migrazione_tappa_costa_metadati.py:80 |  | False |
| service/migrazione_tappa_costa_metadati.py:86 |  | True |
| service/migrazione_tappa_geometrie.py:37 |  | False |
| service/migrazione_tappa_geometrie.py:38 | sqlite_master | False |
| service/migrazione_tappa_geometrie.py:50 |  | False |
| service/planning_context_service.py:29 | blocchi_ordine | False |
| service/planning_context_service.py:37 | tappe | False |
| service/precalcolo_batch_service.py:99 | tappa_analisi, tappa_costa_riepilogo, tappa_geometrie, tappe | False |
| service/precalcolo_batch_service.py:141 | tappa_analisi | False |
| service/precalcolo_service.py:55 | tappa_geometrie | False |
| service/precalcolo_service.py:113 | tappa_geometrie | False |
| service/precalcolo_service.py:188 | tappa_analisi | False |
| service/precalcolo_service.py:214 |  | False |
| service/precalcolo_service.py:216 | sqlite_master | False |
| service/precalcolo_service.py:223 | tappa_costa_riepilogo, tappe | False |
| service/precalcolo_service.py:239 | tappa_analisi | False |
| service/precalcolo_service.py:262 | tappa_analisi | False |
| service/precalcolo_service.py:274 | tappa_analisi | False |
| service/precalcolo_service.py:310 | tappa_segmenti | False |
| service/precalcolo_service.py:313 | tappa_segmenti | False |
| service/precalcolo_service.py:328 | tappa_analisi, tappe | False |
| service/precalcolo_service.py:351 | tappa_analisi | False |
| service/precalcolo_service.py:366 | tappa_analisi | False |
| service/precalcolo_service.py:390 | tappa_analisi | False |
| service/precalcolo_service.py:417 | tappa_segmenti | False |
| service/precalcolo_service.py:421 | tappa_segmenti | False |
| service/precalcolo_service.py:443 | tappe | False |
| service/progetti_service.py:34 | progetti | False |
| service/progetti_service.py:40 | progetti | False |
| service/progetti_service.py:61 | progetti | False |
| service/progetti_service.py:68 | tappe | False |
| service/progetti_service.py:97 | progetti | False |
| service/progetti_service.py:99 |  | True |
| service/salvataggio_tappa_service.py:86 | tappe | False |
| service/salvataggio_tappa_service.py:96 | tappe | False |
| service/salvataggio_tappa_service.py:137 | tappe | False |
| service/salvataggio_tappa_service.py:149 | tappe | False |
| service/salvataggio_tappa_service.py:167 | tappe | False |
| service/salvataggio_tappa_service.py:175 | tappe | False |
| service/salvataggio_tappa_service.py:304 | tappe | False |
| service/salvataggio_tappa_service.py:323 | tappe | False |
| service/salvataggio_tappa_service.py:343 | tappe | False |
| service/salvataggio_tappa_service.py:351 | tappe | False |
| service/salvataggio_tappa_service.py:375 | tappe | False |
| service/salvataggio_tappa_service.py:390 | tappe | False |
| service/salvataggio_tappa_service.py:404 | tappe | False |
| service/salvataggio_tappa_service.py:477 | blocchi_ordine | False |
| service/salvataggio_tappa_service.py:485 | tappe | False |
| service/salvataggio_tappa_service.py:502 | blocchi_ordine | False |
| service/salvataggio_tappa_service.py:507 | blocchi_ordine | False |
| service/salvataggio_tappa_service.py:518 | blocchi_ordine, tappe | False |
| service/salvataggio_tappa_service.py:538 | blocchi_ordine | False |
| service/salvataggio_tappa_service.py:546 | tappe | False |
| service/salvataggio_tappa_service.py:563 | tappe | False |
| service/stats_service.py:176 | tappe | False |
| service/stats_service.py:326 | sqlite_master | False |
| service/stats_service.py:335 |  | False |
| service/stats_service.py:355 | tappa_costa_riepilogo | True |
| service/stats_service.py:498 | tappa_costa_riepilogo | False |
| service/stats_service.py:641 | dogane_progetto | False |
| service/stats_service.py:689 | tappa_analisi | True |
| service/stats_service.py:741 | tappa_analisi, tappe | False |
| service/superfici_service.py:108 | metadata | False |
| service/superfici_service.py:166 | tiles | False |
| service/superfici_service.py:391 | superfici_tappa | False |
| service/superfici_service.py:409 | superfici_tappa | False |
| service/superfici_service.py:449 | tappe | False |
| service/tappe_service.py:31 | tappe | False |
| service/tappe_service.py:48 | tappe | False |
| service/tappe_service.py:61 | tappe | False |
| service/tappe_service.py:89 | tappe | False |
| service/tappe_service.py:92 | tappe | False |
| service/tappe_service.py:126 | tappe | False |
| service/trasferimenti_service.py:24 | allarmi_percorso, tappe | False |
| service/trasferimenti_service.py:120 |  | False |
| service/trasferimenti_service.py:121 | trasferimenti | False |
| service/trasferimenti_service.py:143 | trasferimenti | False |
| tests/test_analisi_profonda.py:172 |  | False |
| tests/test_analisi_profonda.py:173 | tappe | False |
| tests/test_pianificatore_5_2.py:98 | blocchi_ordine, tappe | False |
| tests/test_pianificatore_5_2.py:148 | tappe | False |
| tests/test_pianificatore_5_2.py:162 | tappe | False |
| tests/test_pianificatore_5_2.py:194 | tappe | False |
| tests/test_pianificatore_5_3.py:205 |  | False |
| tests/test_pianificatore_5_3.py:252 | tappe | False |
| tests/test_pianificatore_5_3.py:277 | tappe | False |
| tests/test_pianificatore_5_3.py:284 | tappe | False |
| tests/test_pianificatore_5_3.py:310 | tappe | False |
| tests/test_pianificatore_5_3.py:332 | tappe | False |
| tests/test_pianificatore_5_3.py:369 | tappe | False |
| tests/test_pianificatore_5_3.py:400 | tappe | False |
| tests/test_pianificatore_5_3.py:419 | tappe | False |
| tests/test_pianificatore_5_3.py:436 | tappe | False |
