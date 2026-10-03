"""Verifica se GestoreWorkerSingolo blocca il calcolo del routing.

Simula due richieste ravvicinate e verifica che la seconda non venga persa
e che il risultato consegnato corrisponda alla richiesta piu recente.
Non chiama la rete: il worker e un doppione sincrono.
"""

import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication

from gui.mappa_worker_manager import GestoreWorkerSingolo


class WorkerFalso(QThread):
    """Worker finto: dorme un poco e poi emette la sua etichetta."""

    finito = Signal(dict)

    def __init__(self, etichetta, durata=0.05, emette_sempre=True, parent=None):
        super().__init__(parent)
        self.etichetta = etichetta
        self.durata = durata
        self.emette_sempre = emette_sempre
        self._annullato = False

    def request_stop(self):
        """Simula l'annullamento richiesto dal gestore."""
        self._annullato = True

    def run(self):
        """Attende la durata impostata e poi notifica l'esito.

        Se `emette_sempre` è falso e il gestore ha chiesto l'annullamento,
        il worker esce senza emettere nulla: è ciò che fa
        PianificazionePercorsoWorker quando l'utente preme Annulla.
        """
        time.sleep(self.durata)
        if self._annullato and not self.emette_sempre:
            return
        self.finito.emit({"etichetta": self.etichetta})


class TestCodaRouting(unittest.TestCase):
    """La coda deve consegnare l'ultima richiesta senza perdere risultati."""

    @classmethod
    def setUpClass(cls):
        """Crea una sola applicazione Qt per la classe."""
        cls.app = QApplication.instance() or QApplication([])

    def test_richieste_in_successione_non_si_pierdono(self):
        """Tre richieste ravvicinate: l'ultima arriva e le altre sono scartate."""
        ricevuti = []
        gestore = GestoreWorkerSingolo(
            lambda richiesta: WorkerFalso(richiesta, 0.05, emette_sempre=True),
            "finito",
            ricevuti.append,
        )
        for etichetta in ("a", "b", "c"):
            gestore.richiedi(etichetta)
            time.sleep(0.01)

        for _ in range(120):
            self.app.processEvents()
            time.sleep(0.02)
            if gestore.worker is None and gestore.in_sospeso is None:
                break

        self.assertEqual(ricevuti, [{"etichetta": "c"}])

    def test_worker_annullato_non_blocca_la_coda(self):
        """Se il worker in corso esce senza emettere, la coda si svuota comunque.

        Prima della correzione la richiesta in sospeso restava ferma per
        sempre: il gestore avviava il seguito dall'esito del worker, che non
        arrivava mai. Ora `finished` fa da garanzia.
        """
        ricevuti = []
        gestore = GestoreWorkerSingolo(
            lambda richiesta: WorkerFalso(richiesta, 0.05, emette_sempre=False),
            "finito",
            ricevuti.append,
        )
        gestore.richiedi("a")
        time.sleep(0.01)
        gestore.richiedi("b")

        for _ in range(120):
            self.app.processEvents()
            time.sleep(0.02)
            if gestore.worker is None and gestore.in_sospeso is None:
                break

        # "a" annullato non emette nulla, ma "b" deve partire e completarsi.
        self.assertEqual(ricevuti, [{"etichetta": "b"}])
        self.assertIsNone(gestore.in_sospeso)

    def test_invalida_scarta_il_risultato_in_arrivo(self):
        """Dopo invalida() il risultato tardivo non deve più arrivare."""
        ricevuti = []
        gestore = GestoreWorkerSingolo(
            lambda richiesta: WorkerFalso(richiesta, 0.15),
            "finito",
            ricevuti.append,
        )
        gestore.richiedi("a")
        gestore.invalida()

        for _ in range(80):
            self.app.processEvents()
            time.sleep(0.02)

        self.assertEqual(ricevuti, [])

    def test_gestore_preserva_i_worker_vivi(self):
        """Il gestore deve tenere vivo il worker finché non finisce."""
        gestore = GestoreWorkerSingolo(
            lambda richiesta: WorkerFalso(richiesta, 0.10),
            "finito",
            lambda esito: None,
        )
        gestore.richiedi("a")
        self.assertEqual(len(gestore.attivi), 1)

        for _ in range(80):
            self.app.processEvents()
            time.sleep(0.02)
            if not gestore.attivi:
                break
        self.assertEqual(gestore.attivi, [])


if __name__ == "__main__":
    sys.exit(unittest.main())