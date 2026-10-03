"""Controller della pagina Clima: stato, calcolo e scenario.

La pagina clima e' l'unica parte della finestra con una macchina a stati
non triviali (ordine dei blocchi, scenario temporaneo, estrazione CHELSA in
background). Tutta quella logica vive qui, insieme al proprio stato, cosi'
la finestra principale non deve portarsela dietro.

Il controller non importa `app_desktop.py`: riceve la finestra come oggetto
`app` e usa i suoi metodi pubblici per lo stato condiviso (progetto corrente,
audit, tabelle) e per i ricalcoli che richiedono altre pagine.
"""

import sqlite3
from contextlib import closing
from datetime import datetime

from PySide6.QtCore import QDate
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QDialog, QMessageBox

import service.catena_stagionale_service
import service.clima_service
import service.migrazione_catena_stagionale
import service.migrazione_clima

from gui.dialog_clima_soglie import ClimaSoglieDialog
from gui.pagine.stile_pagina import imposta_righe_tabella
from gui.worker_clima import GestoreEstrazioneClima
from service.config import DB_NAME


class ControllerClima:
    """Gestisce stato, calcolo, scenario ed estrazione della pagina clima."""

    def __init__(self, app):
        """Crea il controller agganciandosi alla finestra `app`.

        :param app: finestra principale, usata per lo stato del progetto
            corrente e per ricalcolare le altre pagine.
        """
        self.app = app
        self.progetto_id = None
        self.ordine_base = []
        self.ordine_scenario = None
        self.scenario_id = None
        self.ultima_applicazione_id = None
        self.risultati_correnti = []
        self.estrazione = GestoreEstrazioneClima(
            app,
            DB_NAME,
            self._al_progresso,
            self._estrazione_completata,
            self._estrazione_fallita,
            self._estrazione_terminata,
        )

    # ---------------------------------------------------------------- stato

    def azzera_stato(self):
        """Riporta il controller allo stato senza progetto attivo."""
        self.progetto_id = None
        self.ordine_base = []
        self.ordine_scenario = None
        self.scenario_id = None
        self.ultima_applicazione_id = None
        self.risultati_correnti = []

    def _prepara_progetto(self, progetto_id):
        """Azzera lo stato del calcolo in vista di un nuovo progetto."""
        self.progetto_id = progetto_id
        self.ordine_base = []
        self.ordine_scenario = None
        self.scenario_id = None
        self.risultati_correnti = []

    def _carica_impostazioni_stagione(self):
        """Legge data di partenza e modificatore di riposo dal database."""
        with closing(sqlite3.connect(DB_NAME)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT data_partenza, modificatore_riposo
                FROM progetto_stagione
                WHERE id_progetto = ?
                """,
                (self.app.current_progetto_id,),
            )
            return cursor.fetchone()

    def _applica_impostazioni_stagione(self, impostazioni):
        """Porta i controlli sui valori salvati, o sui valori di default."""
        app = self.app
        app.input_data_partenza.setDate(QDate.currentDate())
        app.input_riposo.setValue(0)
        if not impostazioni:
            return
        if impostazioni[0]:
            data = datetime.strptime(impostazioni[0], "%Y-%m-%d").date()
            app.input_data_partenza.setDate(QDate(data.year, data.month, data.day))
        app.input_riposo.setValue(impostazioni[1] or 0)

    # -------------------------------------------------------------- carica

    def aggiorna(self):
        """Ricarica la pagina clima per il progetto corrente."""
        app = self.app
        if not app.current_progetto_id:
            self.azzera_stato()
            app.btn_estrai_clima.setEnabled(False)
            app.lbl_stato_clima.setText("Apri un percorso per calcolare la catena.")
            imposta_righe_tabella(app.table_clima, [])
            app.timeline_clima.imposta_righe([])
            app._aggiorna_controlli_scenario([])
            return

        try:
            self._prepara_progetto(app.current_progetto_id)
            app.btn_estrai_clima.setEnabled(not self.estrazione.attiva)
            service.migrazione_catena_stagionale.assicura_schema_catena_stagionale(
                DB_NAME
            )
            service.migrazione_clima.assicura_schema_clima(DB_NAME)
            service.clima_service.assicura_tabelle_clima()
            scenario_sospeso = (
                service.catena_stagionale_service.ottieni_scenario_in_sospeso(
                    app.current_progetto_id
                )
            )
            if scenario_sospeso:
                self.ordine_scenario = list(scenario_sospeso["ordine"])
                self.scenario_id = int(scenario_sospeso["id"])
            self.ultima_applicazione_id = (
                service.catena_stagionale_service
                .ottieni_ultima_applicazione_scenario(app.current_progetto_id)
            )
            self._applica_impostazioni_stagione(
                self._carica_impostazioni_stagione()
            )
            self.calcola()
        except Exception as errore:
            app.lbl_stato_clima.setText(
                f"Errore durante il caricamento clima: {errore}"
            )

    # ------------------------------------------------------------- calcolo

    def calcola(self):
        """Ricalcola la catena stagionale e aggiorna tabella, timeline e stato."""
        app = self.app
        if not app.current_progetto_id:
            return
        data = app.input_data_partenza.date()
        data_partenza = datetime(data.year(), data.month(), data.day()).date()
        try:
            risultati = self._calcola_risultati(data_partenza)
            self.risultati_correnti = risultati
            imposta_righe_tabella(app.table_clima, self._righe_tabella(risultati))
            self._applica_stile_celle(risultati)
            app.timeline_clima.imposta_righe(risultati)
            ordine_attivo = [
                risultato["nome_blocco"] for risultato in risultati
            ]
            app._aggiorna_controlli_scenario(ordine_attivo)
            app.lbl_stato_clima.setText(
                self._descrizione_stato(risultati, ordine_attivo)
            )
        except Exception as errore:
            imposta_righe_tabella(app.table_clima, [])
            app.timeline_clima.imposta_righe([])
            app.lbl_stato_clima.setText(
                f"Errore durante il calcolo stagionale: {errore}"
            )

    def _calcola_risultati(self, data_partenza):
        """Calcola la catena, applicando lo scenario temporaneo se attivo."""
        app = self.app
        risultati_base = service.catena_stagionale_service.calcola_catena(
            app.current_progetto_id,
            data_partenza,
            app.input_riposo.value(),
        )
        ordine_base = [risultato["nome_blocco"] for risultato in risultati_base]
        self.ordine_base = ordine_base

        if self.ordine_scenario is None or self.ordine_scenario == ordine_base:
            if self.scenario_id is not None and app.current_progetto_id:
                service.catena_stagionale_service.scarta_scenario_in_sospeso(
                    app.current_progetto_id
                )
            self.ordine_scenario = list(ordine_base)
            self.scenario_id = None
            risultati = risultati_base
        else:
            risultati = service.catena_stagionale_service.proponi_scenario(
                app.current_progetto_id,
                self.ordine_scenario,
                data_partenza,
                app.input_riposo.value(),
            )
            scenario_sospeso = (
                service.catena_stagionale_service.ottieni_scenario_in_sospeso(
                    app.current_progetto_id
                )
            )
            self.scenario_id = (
                int(scenario_sospeso["id"])
                if scenario_sospeso is not None
                else None
            )

        return service.catena_stagionale_service.calcola_semaforo(
            app.current_progetto_id, risultati
        )

    def _righe_tabella(self, risultati):
        """Applica in righe di tabella i blocchi e i loro passaggi di paese."""
        righe = []
        for blocco in risultati:
            for indice_riga, risultato in enumerate(
                [blocco, *blocco.get("paesi", [])]
            ):
                paese = indice_riga > 0
                etichetta = (
                    f"  ↳ {risultato['codice_paese']} - "
                    f"{risultato['nome_paese']}"
                    if paese
                    else risultato["nome_blocco"]
                )
                righe.append([
                    etichetta,
                    risultato["numero_tappe"],
                    f"{risultato['km_totali']:.1f}",
                    risultato["giorni_pedalata"],
                    risultato["giorni_riposo"],
                    risultato["giorni_extra"],
                    risultato["giorni_totali"],
                    datetime.strptime(
                        risultato["data_ingresso"], "%Y-%m-%d"
                    ).strftime("%d/%m/%Y"),
                    datetime.strptime(
                        risultato["data_uscita"], "%Y-%m-%d"
                    ).strftime("%d/%m/%Y"),
                    risultato.get("semaforo", "N/D"),
                    risultato.get("spiegazione_clima", ""),
                    risultato.get("avviso") or "—",
                ])
        return righe

    def _applica_stile_celle(self, risultati):
        """Applica grassetto, colore del semaforo e tooltip alle celle."""
        tabella = self.app.table_clima
        indice = 0
        for blocco in risultati:
            for posizione, risultato in enumerate(
                [blocco, *blocco.get("paesi", [])]
            ):
                paese = posizione > 0
                for colonna in range(tabella.columnCount()):
                    cella = tabella.item(indice, colonna)
                    if cella is None:
                        continue
                    if not paese:
                        carattere = cella.font()
                        carattere.setBold(True)
                        cella.setFont(carattere)
                    if colonna == 9:
                        cella.setForeground(
                            QColor(risultato.get("semaforo_colore", "#555555"))
                        )
                    if colonna in (9, 10):
                        cella.setToolTip(
                            str(risultato.get("spiegazione_clima", ""))
                        )
                indice += 1

    def _descrizione_stato(self, risultati, ordine_attivo):
        """Compone il riepilogo mostrato sotto la tabella clima."""
        scenario_attivo = ordine_attivo != self.ordine_base
        avvisi = sum(bool(risultato["avviso"]) for risultato in risultati)
        paesi_risultati = [
            paese
            for risultato in risultati
            for paese in risultato.get("paesi", [])
        ]
        descrizione = (
            f"Stima con margini per {len(risultati)} blocchi e "
            f"{len(paesi_risultati)} passaggi di paese."
            if risultati
            else "Il percorso non contiene blocchi con tappe attive."
        )
        if scenario_attivo:
            descrizione += " Scenario temporaneo non applicato."
        if avvisi:
            descrizione += f" Attenzione: {avvisi} blocchi richiedono verifica."
        numero_clima = sum(
            paese["semaforo"] in {"verde", "giallo", "rosso"}
            for paese in paesi_risultati
        )
        numero_parziali = sum(
            paese["semaforo"] == "Parziale" for paese in paesi_risultati
        )
        if numero_clima:
            descrizione += (
                f" Semafori climatici disponibili per {numero_clima} "
                "passaggi di paese."
            )
            if numero_parziali:
                descrizione += (
                    f" Dati incompleti per altri {numero_parziali} "
                    "passaggi di paese."
                )
        elif numero_parziali:
            descrizione += (
                f" Dati climatici incompleti per {numero_parziali} "
                "passaggi di paese; controlla la copertura."
            )
        else:
            descrizione += (
                " Dati CHELSA non ancora disponibili o incompleti: "
                "avvia l’estrazione per questo progetto."
            )
        return descrizione

    # --------------------------------------------------- soglie ed estrazione

    def _carica_soglie(self):
        """Restituisce le soglie del semaforo del progetto, o quelle di default."""
        if not self.app.current_progetto_id:
            return dict(
                service.catena_stagionale_service.SOGLIE_CLIMA_DEFAULT
            )
        return (
            service.catena_stagionale_service.carica_impostazioni_semaforo(
                self.app.current_progetto_id
            )
        )

    def apri_soglie(self):
        """Apre il dialogo delle soglie e le salva per il progetto corrente."""
        app = self.app
        if not app.current_progetto_id:
            QMessageBox.information(
                app,
                "Percorso richiesto",
                "Apri un percorso prima di modificare le soglie.",
            )
            return
        dialogo = ClimaSoglieDialog(self._carica_soglie(), app)
        if dialogo.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            service.catena_stagionale_service.salva_impostazioni_semaforo(
                app.current_progetto_id, dialogo.valori()
            )
            self.calcola()
            app.lbl_stato_clima.setText(
                "Preferenze del semaforo salvate per questo percorso. "
                + app.lbl_stato_clima.text()
            )
        except Exception as errore:
            QMessageBox.critical(
                app,
                "Impostazioni non salvate",
                f"Non è stato possibile salvare le soglie: {errore}",
            )

    def avvia_estrazione(self):
        """Avvia l'estrazione climatica CHELSA in background."""
        app = self.app
        if not app.current_progetto_id:
            QMessageBox.information(
                app,
                "Percorso richiesto",
                "Apri un percorso prima di estrarre i dati climatici.",
            )
            return
        if self.estrazione.attiva:
            return

        app.btn_estrai_clima.setEnabled(False)
        app.lbl_stato_clima.setText(
            "Estrazione CHELSA avviata. La prima lettura richiede internet; "
            "l’interfaccia resta utilizzabile."
        )
        self.estrazione.avvia(app.current_progetto_id)

    def _al_progresso(self, messaggio):
        """Mostra l'avanzamento dell'estrazione nella barra di stato."""
        self.app.lbl_stato_clima.setText(messaggio)

    def _estrazione_completata(self, risultato):
        """Ricalcola la pagina clima e comunica quante finestre sono state lette."""
        app = self.app
        self.calcola()
        app.lbl_stato_clima.setText(
            app.lbl_stato_clima.text()
            + f" CHELSA aggiornato: {risultato['file_chelsa_letti']} "
            "finestre raster lette."
        )

    def _estrazione_fallita(self, messaggio):
        """Mostra l'errore avvenuto durante l'estrazione."""
        self.app.lbl_stato_clima.setText(
            f"Errore nell’estrazione CHELSA: {messaggio}"
        )

    def _estrazione_terminata(self):
        """Riabilita il pulsante di estrazione al termine del thread."""
        self.app.btn_estrai_clima.setEnabled(bool(self.app.current_progetto_id))
# --------------------------------------------------------------- scenario

    def sposta_blocco(self):
        """Sposta il blocco selezionato nella posizione scelta."""
        app = self.app
        ordine_corrente = [
            risultato["nome_blocco"] for risultato in self.risultati_correnti
        ]
        nome_blocco = app.combo_blocco_scenario.currentData()
        nuova_posizione = app.combo_posizione_scenario.currentData()
        if (
            not ordine_corrente
            or nome_blocco not in ordine_corrente
            or nuova_posizione is None
        ):
            return

        ordine_proposto = list(ordine_corrente)
        indice_corrente = ordine_proposto.index(nome_blocco)
        blocco = ordine_proposto.pop(indice_corrente)
        ordine_proposto.insert(int(nuova_posizione) - 1, blocco)
        self.ordine_scenario = ordine_proposto
        self.calcola()

    def ripristina_ordine(self):
        """Scarta lo scenario temporaneo e torna all'ordine ufficiale."""
        app = self.app
        if app.current_progetto_id:
            service.catena_stagionale_service.scarta_scenario_in_sospeso(
                app.current_progetto_id
            )
        self.ordine_scenario = list(self.ordine_base)
        self.scenario_id = None
        self.calcola()

    def conferma_scenario(self):
        """Applica all'ordine ufficiale lo scenario temporaneo."""
        app = self.app
        scenario_id = self.scenario_id
        if scenario_id is None or not app.current_progetto_id:
            return

        ordine_precedente = " → ".join(self.ordine_base)
        ordine_proposto = " → ".join(self.ordine_scenario or [])
        risposta = QMessageBox.question(
            app,
            "Confermare lo scenario?",
            "L'ordine ufficiale in Gestione blocchi verrà aggiornato.\n\n"
            f"Prima: {ordine_precedente}\n\nDopo: {ordine_proposto}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if risposta != QMessageBox.Yes:
            return

        try:
            risultato = (
                service.catena_stagionale_service.conferma_scenario(scenario_id)
            )
            self.scenario_id = None
            self.ordine_scenario = None
            app.page_blocchi.carica_blocchi()
            app.aggiorna_pagina_clima()
            QMessageBox.information(
                app,
                "Scenario applicato",
                "L'ordine è stato aggiornato e l'ordine precedente è "
                "conservato per poterlo ripristinare.\n\n"
                f"Nuova sequenza: {' → '.join(risultato['ordine'])}",
            )
        except Exception as errore:
            QMessageBox.critical(
                app,
                "Scenario non applicato",
                f"L'ordine ufficiale non è stato modificato: {errore}",
            )

    def annulla_ultima_applicazione(self):
        """Ripristina l'ordine precedente all'ultimo scenario applicato."""
        app = self.app
        if not app.current_progetto_id:
            return
        scenario_id = (
            service.catena_stagionale_service
            .ottieni_ultima_applicazione_scenario(app.current_progetto_id)
        )
        if scenario_id is None:
            QMessageBox.information(
                app,
                "Nessuna applicazione",
                "Non ci sono scenari da annullare.",
            )
            return
        risposta = QMessageBox.question(
            app,
            "Annullare l'ultima applicazione?",
            "Verrà ripristinato l'ordine dei blocchi precedente allo "
            "scenario. Eventuali modifiche successive all'ordine "
            "impediranno il ripristino.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if risposta != QMessageBox.Yes:
            return
        try:
            risultato = service.catena_stagionale_service.annulla_scenario(
                scenario_id
            )
            self.ordine_scenario = None
            self.scenario_id = None
            app.page_blocchi.carica_blocchi()
            app.aggiorna_pagina_clima()
            QMessageBox.information(
                app,
                "Ordine ripristinato",
                "È stato ripristinato l'ordine precedente:\n"
                f"{' → '.join(risultato['ordine'])}",
            )
        except Exception as errore:
            QMessageBox.critical(
                app,
                "Ripristino non riuscito",
                f"L'ordine non è stato modificato: {errore}",
            )

    def salva_impostazioni(self):
        """Salva data di partenza e modificatore di riposo per il progetto."""
        app = self.app
        if not app.current_progetto_id:
            QMessageBox.information(app, "Percorso richiesto", "Apri un percorso prima di salvare le impostazioni.")
            return
        data = app.input_data_partenza.date()
        data_partenza = f"{data.year():04d}-{data.month():02d}-{data.day():02d}"
        try:
            service.clima_service.salva_impostazioni_stagione(
                app.current_progetto_id, data_partenza, app.input_riposo.value()
            )
            self.calcola()
            app.lbl_stato_clima.setText(
                "Data e riposo salvati. " + app.lbl_stato_clima.text()
            )
        except Exception as errore:
            app.lbl_stato_clima.setText(f"Errore durante il salvataggio clima: {errore}")
