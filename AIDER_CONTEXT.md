# Aider context

{
  "aider_context": {
    "title": "Project agent brief",
    "summary": {
      "modules": 20,
      "classes": 15,
      "functions": 136,
      "routes": 6,
      "risk": "alto"
    },
    "key_findings": [
      "Rischio architetturale: alto",
      "Simboli orfani: 89",
      "File critici: app_desktop.py, gui/dashboard.py, gui/mappa.py"
    ],
    "priority_order": [
      "app_desktop.py",
      "gui/dashboard.py",
      "gui/mappa.py",
      "service/stats_service.py",
      "service/map_server.py"
    ],
    "next_steps": [
      "Rivedere i simboli orfani e decidere se integrarli, rimuoverli o spostarli in moduli più appropriati.",
      "Priorizzare i file con score più alto per refactor e verifica di coerenza architetturale.",
      "Usare il JSON di analisi come contesto minimo per future modifiche e per ridurre il numero di token richiesti ai tool AI."
    ],
    "agent_prompt": "Analizza il progetto usando il dataset di PROGETTO_INDEX.json. Priorità massima ai file critici e ai simboli orfani, poi verifica rotti o duplicati. Propone un refactor minimo ma sicuro e documenta le modifiche."
  },
  "priority_plan": {
    "summary": "Piano d'azione per interventi mirati e minimali.",
    "phases": [
      {
        "phase": "1. Valutazione rapida",
        "focus": [
          "app_desktop.py",
          "gui/mappa.py",
          "gui/dashboard.py"
        ],
        "goal": "Identificare i file più critici da leggere per prima."
      },
      {
        "phase": "2. Consolidamento architettura",
        "focus": [
          "service/stats_service.py",
          "service/map_server.py",
          "gui/wizard_percorso.py"
        ],
        "goal": "Ridurre duplicazioni, simboli orfani e dipendenze confuse."
      },
      {
        "phase": "3. Stabilizzazione e refactor",
        "focus": [
          "service/map_manager_service.py",
          "service/audit_service.py",
          "service/clima_service.py",
          "resources/genera_catalogo_sprite.py",
          "service/dogane_service.py",
          "analizzatore_progetto.py",
          "backup.py",
          "agente_locale.py",
          "basemap-styles-master/mapboxgl/styler.py",
          "export_structure.py",
          "static/aggiorna_sprite.py",
          "database/database_setup.py",
          "service/config.py",
          "service/__init__.py"
        ],
        "goal": "Rendere il sistema più coerente e più semplice da mantenere."
      }
    ],
    "immediate_actions": [
      "Verifica moduli critici con più anomalie e chiamate.",
      "Riduci simboli orfani e import non usati.",
      "Consolida le rotte/entry point e controlla backend/frontend coupling."
    ]
  },
  "ultra_compact_prompt": "Progetto: Bikepacking_Studio. Contesto: 20 moduli, 15 classi, 136 funzioni, 6 endpoint Flask, 89 simboli orfani. Rischio: alto. File critici: app_desktop.py, gui/dashboard.py, gui/mappa.py. Priorità: correggere simboli orfani, verificare file critici e consolidare dipendenze. Usa PROGETTO_INDEX.json come fonte di verità e minimizza i cambiamenti."
}
