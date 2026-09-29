# AI Brief - Bikepacking_Studio

*Aggiornato: 2026-09-29 15:37*

## Numeri essenziali

- Moduli Python: 16
- Classi: 16
- Funzioni: 175
- Rotte Flask: 7
- Tabelle DB: 11
- Simboli orfani: 78
- **Livello rischio: alto**

## File critici (score più alto)

- `gui/mappa.py` - score 346 - 6 classi, 53 funzioni, 0 anomalie
- `app_desktop.py` - score 332 - 5 classi, 53 funzioni, 0 anomalie
- `gui/dashboard.py` - score 161 - 2 classi, 20 funzioni, 0 anomalie
- `service/stats_service.py` - score 91 - 0 classi, 13 funzioni, 0 anomalie
- `service/map_server.py` - score 63 - 0 classi, 12 funzioni, 0 anomalie

## Endpoint Flask

- `/sprite<path:filename>` [GET] -> `serve_sprite()` in `service/map_server.py`
- `/fonts/<path:fontstack>/<range_pbf>` [GET] -> `serve_fonts()` in `service/map_server.py`
- `/api/set-gpx-data` [POST] -> `set_gpx_data()` in `service/map_server.py`
- `/api/get-gpx-data` [GET] -> `get_gpx_data()` in `service/map_server.py`
- `/api/map-interactions` [GET] -> `leggi_interazioni_mappa()` in `service/map_server.py`
- `/api/maps/list` [GET] -> `list_maps()` in `service/map_server.py`
- `/map` [GET] -> `show_map()` in `service/map_server.py`

## Simboli orfani (top 15)

- `DoganeSignals` (classe) in `app_desktop.py`
- `ClimaSignals` (classe) in `app_desktop.py`
- `DropAreaGPX` (classe) in `app_desktop.py`
- `GestoreBlocchiWidget` (classe) in `app_desktop.py`
- `determina_blocco_da_nome_file` (funzione) in `app_desktop.py`
- `ottieni_nome_localita` (funzione) in `app_desktop.py`
- `carica_blocchi` (funzione) in `app_desktop.py`
- `sposta_su` (funzione) in `app_desktop.py`
- `sposta_giu` (funzione) in `app_desktop.py`
- `applica_riordinamento` (funzione) in `app_desktop.py`
- `gestisci_cambio_progetto` (funzione) in `app_desktop.py`
- `crea_bottone_navigazione` (funzione) in `app_desktop.py`
- `crea_pagina_mappa` (funzione) in `app_desktop.py`
- `crea_pagina_audit` (funzione) in `app_desktop.py`
- `crea_pagina_trasporti` (funzione) in `app_desktop.py`
- ... e altri 63 (vedi report completo)

## Moduli principali

- `gui/mappa.py`: 6 classi, 53 funzioni
- `app_desktop.py`: 5 classi, 53 funzioni
- `gui/dashboard.py`: 2 classi, 20 funzioni
- `service/stats_service.py`: 0 classi, 13 funzioni
- `service/map_server.py`: 0 classi, 12 funzioni
- `service/map_manager_service.py`: 2 classi, 4 funzioni
- `gui/wizard_percorso.py`: 1 classi, 3 funzioni
- `service/audit_service.py`: 0 classi, 4 funzioni
- `service/clima_service.py`: 0 classi, 4 funzioni
- `service/dogane_service.py`: 0 classi, 4 funzioni

## Azioni consigliate

- Rivedere i simboli orfani e decidere se integrarli, rimuoverli o spostarli.
- Prioritizzare i file con score più alto per refactor e verifica.
- Usare PROGETTO_INDEX.json come contesto minimo per ridurre i token richiesti alle IA.

## Prompt pronto per agente

```
Progetto: Bikepacking_Studio. Contesto: 16 moduli, 16 classi, 175 funzioni, 7 endpoint Flask, 78 simboli orfani. Rischio: alto. File critici: gui/mappa.py, app_desktop.py, gui/dashboard.py. Priorità: correggere simboli orfani, verificare file critici e consolidare dipendenze. Usa PROGETTO_INDEX.json come fonte di verità e minimizza i cambiamenti.
```

---

*Per approfondire: vedi `analisi.json` (dataset completo) o `report.md` (versione umana).*
