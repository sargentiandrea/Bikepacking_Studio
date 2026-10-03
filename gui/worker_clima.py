"""Worker e gestore del ciclo di vita dell'estrazione climatica CHELSA.

`EstrazioneClimaWorker` esegue la lettura dei raster fuori dal thread
dell'interfaccia; `GestoreEstrazioneClima` incapsula il `QThread` che lo ospita
e i collegamenti dei segnali, così la finestra non deve più ripetere quel
codice a ogni estrazione.

Perché non si riusa `GestoreWorkerSingolo` di `gui/mappa_worker_manager.py`:
quel gestore è progettato per worker che sono essi stessi `QThread` e che
accettano `request_stop()`, con una semantica di "richiesta in sospeso" e
"token" che scarta i risultati superati (tipica del cambio percorso durante
un'analisi). L'estrazione clima è invece un `QObject` spostato su un
`QThread` dedicato, senza possibilità di interruzione: adottare quel gestore
introduirebbe un annullamento automatico e una riavvio automatico che oggi
non esistono, quindi cambierebbe il comportamento dell'applicazione.

Il modulo non conosce `app_desktop.py`: riceve solo callback e oggetti
d'interfaccia già costruiti.
"""

from PySide6.QtCore import QObject, QThread, Signal


class EstrazioneClimaWorker(QObject):
    """Esegue la lettura COG fuori dal thread dell'interfaccia."""

    progresso = Signal(str)
    completata = Signal(dict)
    fallita = Signal(str)

    def __init__(self, db_name, progetto_id):
        """Prepara l'estrazione per il database e il progetto indicati."""
        super().__init__()
        self.db_name = db_name
        self.progetto_id = progetto_id

    def run(self):
        """Avvia l'estrazione e segnala esito o errore tramite i segnali."""
        try:
            # Import ritardato come prima: il modulo di estrazione è pesante.
            import service.clima_estrattore

            risultato = service.clima_estrattore.estrai_clima_per_tappe(
                self.db_name,
                self.progetto_id,
                progress_callback=self.progresso.emit,
            )
        except Exception as errore:
            self.fallita.emit(str(errore))
        else:
            self.completata.emit(risultato)


class GestoreEstrazioneClima:
    """Gestisce thread, worker e collegamenti di una singola estrazione clima."""

    def __init__(
        self,
        parent,
        db_name,
        al_progresso,
        alla_fine,
        al_fallimento,
        alla_chiusura,
    ):
        """Registra il contesto e le quattro callback del ciclo di estrazione.

        :param parent: widget usato come parent del `QThread`.
        :param db_name: percorso del database da interrogare.
        :param al_progresso: riceve il testo di avanzamento.
        :param alla_fine: riceve il dizionario restituito dall'estrazione.
        :param al_fallimento: riceve il messaggio d'errore.
        :param alla_chiusura: chiamata a estrazione conclusa, in ogni esito.
        """
        self._parent = parent
        self._db_name = db_name
        self._al_progresso = al_progresso
        self._alla_fine = alla_fine
        self._al_fallimento = al_fallimento
        self._alla_chiusura = alla_chiusura
        self.thread = None
        self.worker = None

    @property
    def attiva(self):
        """Indica se è in corso un'estrazione."""
        return self.thread is not None

    def avvia(self, progetto_id):
        """Crea il thread, il worker, collega i segnali e parte.

        :return: `True` se l'estrazione è stata avviata, `False` se era già
            in corso un'estrazione (nessun duplicato avviato).
        """
        if self.attiva:
            return False
        self.thread = QThread(self._parent)
        self.worker = EstrazioneClimaWorker(self._db_name, progetto_id)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progresso.connect(self._al_progresso)
        self.worker.completata.connect(self._alla_fine)
        self.worker.fallita.connect(self._al_fallimento)
        self.worker.completata.connect(self.thread.quit)
        self.worker.fallita.connect(self.thread.quit)
        self.worker.completata.connect(self.worker.deleteLater)
        self.worker.fallita.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self._chiusa)
        self.thread.start()
        return True

    def _chiusa(self):
        """Azzera i riferimenti e notifica la fine dell'estrazione."""
        self.thread = None
        self.worker = None
        self._alla_chiusura()