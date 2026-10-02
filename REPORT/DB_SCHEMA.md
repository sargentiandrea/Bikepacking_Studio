# Schema del database SQLite

- Percorso: `data/bikepacking_app.db`
- Tabelle trovate: 21

## `allarmi_percorso`

- Righe: 3

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `id` | INTEGER | chiave primaria |
| `id_progetto` | INTEGER | — |
| `tappa_origine_id` | INTEGER | — |
| `tappa_destinazione_id` | INTEGER | — |
| `tipo_allarme` | TEXT | — |
| `messaggio` | TEXT | — |
| `risolto` | INTEGER | DEFAULT 0 |

### Indici

Nessun indice.

### Chiavi esterne

- `id_progetto` → `progetti.id` (ON UPDATE NO ACTION, ON DELETE NO ACTION)

## `anagrafica_paesi`

- Righe: 198

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `codice_iso2` | TEXT | chiave primaria, UNIQUE |
| `nome_paese` | TEXT | — |
| `regione_area` | TEXT | — |
| `passaporto` | TEXT | — |
| `visto` | TEXT | — |
| `valuta` | TEXT | — |
| `roaming` | TEXT | — |
| `drone` | TEXT | — |
| `bici` | INTEGER | — |

### Indici

- `sqlite_autoindex_anagrafica_paesi_1` (UNIQUE): `codice_iso2`

### Chiavi esterne

Nessuna chiave esterna.

## `anagrafica_paesi_mondo`

- Righe: 12

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `codice_iso2` | TEXT | chiave primaria, UNIQUE |
| `nome` | TEXT | — |
| `regione` | TEXT | — |
| `passaporto` | TEXT | — |
| `visto` | TEXT | — |
| `valuta` | TEXT | — |
| `roaming` | TEXT | — |
| `drone` | TEXT | — |
| `bici` | INTEGER | — |

### Indici

- `sqlite_autoindex_anagrafica_paesi_mondo_1` (UNIQUE): `codice_iso2`

### Chiavi esterne

Nessuna chiave esterna.

## `blocchi_ordine`

- Righe: 24

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `id` | INTEGER | chiave primaria |
| `id_progetto` | INTEGER | — |
| `nome_blocco` | TEXT | — |
| `ordine` | INTEGER | — |

### Indici

Nessun indice.

### Chiavi esterne

- `id_progetto` → `progetti.id` (ON UPDATE NO ACTION, ON DELETE NO ACTION)

## `blocchi_stagione`

- Righe: 18

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `id` | INTEGER | chiave primaria |
| `id_progetto` | INTEGER | — |
| `nome_blocco` | TEXT | — |
| `giorni_extra` | INTEGER | DEFAULT 0 |
| `mesi_ideali` | TEXT | DEFAULT '04,05,06,09,10' |
| `mesi_ideali_custom` | TEXT | DEFAULT NULL |

### Indici

- `sqlite_autoindex_blocchi_stagione_1` (UNIQUE): `id_progetto`, `nome_blocco`

### Chiavi esterne

Nessuna chiave esterna.

## `cache_geo_paesi`

- Righe: 2

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `lat_griglia` | REAL | chiave primaria |
| `lon_griglia` | REAL | chiave primaria |
| `codice_iso2` | TEXT | — |
| `nome_paese_riconosciuto` | TEXT | — |

### Indici

- `sqlite_autoindex_cache_geo_paesi_1` (UNIQUE): `lat_griglia`, `lon_griglia`

### Chiavi esterne

Nessuna chiave esterna.

## `cache_nomi_luoghi`

- Righe: 995

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `lat_arrotondata` | REAL | chiave primaria, NOT NULL |
| `lon_arrotondata` | REAL | chiave primaria, NOT NULL |
| `nome` | TEXT | — |
| `calcolato_il` | TEXT | — |

### Indici

- `sqlite_autoindex_cache_nomi_luoghi_1` (UNIQUE): `lat_arrotondata`, `lon_arrotondata`

### Chiavi esterne

Nessuna chiave esterna.

## `clima_blocco_mese`

- Righe: 288

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `id_progetto` | INTEGER | chiave primaria, NOT NULL |
| `nome_blocco` | TEXT | chiave primaria, NOT NULL |
| `mese` | INTEGER | chiave primaria, NOT NULL |
| `temperatura_media` | REAL | — |
| `temperatura_max` | REAL | — |
| `temperatura_min` | REAL | — |
| `precipitazioni_mm` | REAL | — |
| `vento_media` | REAL | — |
| `dataset_versione` | TEXT | NOT NULL |
| `aggiornato_il` | TEXT | NOT NULL |
| `copertura_pct` | REAL | NOT NULL, DEFAULT 0 |
| `campioni_validi` | INTEGER | NOT NULL, DEFAULT 0 |
| `campioni_totali` | INTEGER | NOT NULL, DEFAULT 0 |
| `anni_coperti` | TEXT | NOT NULL, DEFAULT '{}' |

### Indici

- `idx_clima_blocco_mese_progetto` (non univoco): `id_progetto`, `nome_blocco`
- `sqlite_autoindex_clima_blocco_mese_1` (UNIQUE): `id_progetto`, `nome_blocco`, `mese`

### Chiavi esterne

Nessuna chiave esterna.

## `clima_paese_mese`

- Righe: 540

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `id_progetto` | INTEGER | chiave primaria, NOT NULL |
| `paese` | TEXT | chiave primaria, NOT NULL |
| `mese` | INTEGER | chiave primaria, NOT NULL |
| `temperatura_media` | REAL | — |
| `temperatura_max` | REAL | — |
| `temperatura_min` | REAL | — |
| `precipitazioni_mm` | REAL | — |
| `vento_media` | REAL | — |
| `dataset_versione` | TEXT | NOT NULL |
| `aggiornato_il` | TEXT | NOT NULL |
| `copertura_pct` | REAL | NOT NULL, DEFAULT 0 |
| `campioni_validi` | INTEGER | NOT NULL, DEFAULT 0 |
| `campioni_totali` | INTEGER | NOT NULL, DEFAULT 0 |
| `anni_coperti` | TEXT | NOT NULL, DEFAULT '{}' |

### Indici

- `idx_clima_paese_mese_progetto` (non univoco): `id_progetto`, `paese`
- `sqlite_autoindex_clima_paese_mese_1` (UNIQUE): `id_progetto`, `paese`, `mese`

### Chiavi esterne

Nessuna chiave esterna.

## `confini_box`

- Righe: 11

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `id` | INTEGER | chiave primaria |
| `codice_iso2` | TEXT | — |
| `lat_min` | REAL | — |
| `lat_max` | REAL | — |
| `lon_min` | REAL | — |
| `lon_max` | REAL | — |

### Indici

Nessun indice.

### Chiavi esterne

Nessuna chiave esterna.

## `dogane_percorso`

- Righe: 0

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `id` | INTEGER | chiave primaria |
| `id_progetto` | INTEGER | — |
| `paese_origine` | TEXT | — |
| `paese_destinazione` | TEXT | — |

### Indici

Nessun indice.

### Chiavi esterne

Nessuna chiave esterna.

## `dogane_progetto`

- Righe: 67

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `id` | INTEGER | chiave primaria |
| `id_progetto` | INTEGER | — |
| `ordine_progressivo` | INTEGER | — |
| `codice_iso2` | TEXT | — |
| `paese_nome` | TEXT | — |
| `regione_area` | TEXT | — |
| `requisito_passaporto` | TEXT | — |
| `tipo_visto` | TEXT | — |
| `valuta` | TEXT | — |
| `roaming_info` | TEXT | — |
| `drone_policy` | TEXT | — |
| `transitabile_bici` | INTEGER | DEFAULT 1 |
| `stato_valico` | TEXT | — |
| `valico_vicino_nome` | TEXT | — |
| `valico_vicino_dist_km` | REAL | — |

### Indici

Nessun indice.

### Chiavi esterne

- `id_progetto` → `progetti.id` (ON UPDATE NO ACTION, ON DELETE NO ACTION)

## `progetti`

- Righe: 1

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `id` | INTEGER | chiave primaria |
| `nome_progetto` | TEXT | NOT NULL |
| `descrizione` | TEXT | — |
| `km_totali` | REAL | DEFAULT 0 |
| `stato` | TEXT | DEFAULT 'ATTIVO' |
| `data_creazione` | TEXT | — |

### Indici

Nessun indice.

### Chiavi esterne

Nessuna chiave esterna.

## `progetto_stagione`

- Righe: 1

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `id_progetto` | INTEGER | chiave primaria |
| `data_partenza` | TEXT | — |
| `modificatore_riposo` | INTEGER | DEFAULT 0 |

### Indici

Nessun indice.

### Chiavi esterne

Nessuna chiave esterna.

## `superfici_tappa`

- Righe: 958

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `id` | INTEGER | chiave primaria |
| `tappa_id` | INTEGER | UNIQUE |
| `dati_json` | TEXT | — |
| `calcolato_il` | TEXT | — |

### Indici

- `sqlite_autoindex_superfici_tappa_1` (UNIQUE): `tappa_id`

### Chiavi esterne

- `tappa_id` → `tappe.id` (ON UPDATE NO ACTION, ON DELETE NO ACTION)

## `tappa_analisi`

- Righe: 958

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `tappa_id` | INTEGER | chiave primaria |
| `gpx_sha256` | TEXT | NOT NULL |
| `versione_algoritmi` | TEXT | NOT NULL |
| `distanza_km` | REAL | — |
| `dislivello_pos_m` | REAL | — |
| `dislivello_neg_m` | REAL | — |
| `quota_min_m` | REAL | — |
| `quota_max_m` | REAL | — |
| `pendenza_media_pct` | REAL | — |
| `pendenza_max_pct` | REAL | — |
| `bbox_min_lon` | REAL | — |
| `bbox_min_lat` | REAL | — |
| `bbox_max_lon` | REAL | — |
| `bbox_max_lat` | REAL | — |
| `stato` | TEXT | NOT NULL |
| `errore` | TEXT | — |
| `aggiornato_il` | TEXT | — |

### Indici

Nessun indice.

### Chiavi esterne

- `tappa_id` → `tappe.id` (ON UPDATE NO ACTION, ON DELETE CASCADE)

## `tappa_costa_riepilogo`

- Righe: 957

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `tappa_id` | INTEGER | chiave primaria |
| `gpx_sha256` | TEXT | NOT NULL |
| `versione_algoritmo_costa` | TEXT | NOT NULL |
| `versione_dataset_costa` | TEXT | NOT NULL |
| `fascia_0_500m_km` | REAL | NOT NULL, DEFAULT 0 |
| `fascia_500_2500m_km` | REAL | NOT NULL, DEFAULT 0 |
| `fascia_2500_5000m_km` | REAL | NOT NULL, DEFAULT 0 |
| `fascia_oltre_5000m_km` | REAL | NOT NULL, DEFAULT 0 |
| `tappe_coinvolte_0_500m` | INTEGER | NOT NULL, DEFAULT 0 |
| `tappe_coinvolte_500_2500m` | INTEGER | NOT NULL, DEFAULT 0 |
| `tappe_coinvolte_2500_5000m` | INTEGER | NOT NULL, DEFAULT 0 |
| `tappe_coinvolte_oltre_5000m` | INTEGER | NOT NULL, DEFAULT 0 |
| `totale_km` | REAL | NOT NULL, DEFAULT 0 |
| `calcolato_il` | TEXT | NOT NULL |
| `gpx_size_bytes` | INTEGER | — |
| `gpx_mtime` | REAL | — |

### Indici

Nessun indice.

### Chiavi esterne

- `tappa_id` → `tappe.id` (ON UPDATE NO ACTION, ON DELETE CASCADE)

## `tappa_geometrie`

- Righe: 957

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `tappa_id` | INTEGER | chiave primaria |
| `gpx_sha256` | TEXT | NOT NULL |
| `versione_algoritmo` | TEXT | NOT NULL |
| `geometria_completa` | BLOB | NOT NULL |
| `geometria_semplificata` | BLOB | NOT NULL |
| `bbox_min_lat` | REAL | NOT NULL |
| `bbox_min_lon` | REAL | NOT NULL |
| `bbox_max_lat` | REAL | NOT NULL |
| `bbox_max_lon` | REAL | NOT NULL |
| `numero_punti_originali` | INTEGER | NOT NULL |
| `numero_punti_semplificati` | INTEGER | NOT NULL |
| `aggiornato_il` | TEXT | NOT NULL |

### Indici

Nessun indice.

### Chiavi esterne

- `tappa_id` → `tappe.id` (ON UPDATE NO ACTION, ON DELETE CASCADE)

## `tappa_segmenti`

- Righe: 958

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `tappa_id` | INTEGER | chiave primaria, NOT NULL |
| `track_index` | INTEGER | chiave primaria, NOT NULL |
| `segment_index` | INTEGER | chiave primaria, NOT NULL |
| `punti` | INTEGER | — |
| `distanza_km` | REAL | — |
| `dislivello_pos_m` | REAL | — |
| `dislivello_neg_m` | REAL | — |
| `quota_min_m` | REAL | — |
| `quota_max_m` | REAL | — |
| `versione_algoritmi` | TEXT | — |

### Indici

- `sqlite_autoindex_tappa_segmenti_1` (UNIQUE): `tappa_id`, `track_index`, `segment_index`

### Chiavi esterne

- `tappa_id` → `tappe.id` (ON UPDATE NO ACTION, ON DELETE CASCADE)

## `tappe`

- Righe: 958

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `id` | INTEGER | chiave primaria |
| `id_progetto` | INTEGER | — |
| `sequenza` | INTEGER | — |
| `blocco` | TEXT | — |
| `nome_file` | TEXT | — |
| `start_lat` | REAL | — |
| `start_lon` | REAL | — |
| `end_lat` | REAL | — |
| `end_lon` | REAL | — |
| `distanza_km` | REAL | — |
| `stato` | TEXT | DEFAULT 'ATTIVA' |
| `blocco_area` | TEXT | — |
| `nome_file_gpx` | TEXT | — |
| `km` | REAL | DEFAULT 0 |
| `ruolo` | TEXT | — |
| `paese` | TEXT | — |

### Indici

Nessun indice.

### Chiavi esterne

- `id_progetto` → `progetti.id` (ON UPDATE NO ACTION, ON DELETE NO ACTION)

## `trasferimenti`

- Righe: 28

### Colonne

| Nome | Tipo | Vincoli |
|---|---|---|
| `id` | INTEGER | chiave primaria |
| `id_progetto` | INTEGER | — |
| `tipo_mezzo` | TEXT | — |
| `vettore` | TEXT | — |
| `da_luogo` | TEXT | — |
| `a_luogo` | TEXT | — |
| `durata` | TEXT | — |
| `costo_eur` | REAL | — |
| `note` | TEXT | — |
| `start_lat` | REAL | — |
| `start_lon` | REAL | — |
| `end_lat` | REAL | — |
| `end_lon` | REAL | — |

### Indici

Nessun indice.

### Chiavi esterne

- `id_progetto` → `progetti.id` (ON UPDATE NO ACTION, ON DELETE NO ACTION)
