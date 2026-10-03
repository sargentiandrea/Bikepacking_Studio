"""Verifica della sotto-fase 5.1 del pianificatore: firma, annullamento e coda.

Non chiama la rete: il worker di routing viene costruito e pilotato
localmente, cosi il test resta offline e deterministico.
"""

import os
import sys
import unittest

# I test vivono in tests/ ma il codice sta nella radice del progetto.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication

from gui.mappa_worker import TIMEOUT_ROUTING_SECONDI, PianificazionePercorsoWorker
from service.dettagli_rotta_service import (
    testo_stato_anteprima_pronta,
    testo_stato_errore_routing,
)
from service.punti_service import firma_pianificazione, normalizza_luogo


class TestFirmaNormalizzata(unittest.TestCase):
    """La firma non deve cambiare se il testo è solo diverso nella forma."""

    def test_maiuscole_spazi_e_accenti_non_contano(self):
        """Stessi luoghi scritti diversamente producono la stessa firma."""
        a = firma_pianificazione(1, "  Modena ", (), "Roma", "Gravel / Viaggio", None)
        b = firma_pianificazione(1, "modena", (), "roma", "gravel / viaggio", None)
        self.assertEqual(a, b)

    def test_luoghi_diversi_restano_diversi(self):
        """Luoghi realmente diversi devono dare firme diverse."""
        a = firma_pianificazione(1, "Modena", (), "Roma", "Gravel", None)
        b = firma_pianificazione(1, "Bologna", (), "Roma", "Gravel", None)
        self.assertNotEqual(a, b)

    def test_profilo_e_progetto_contano(self):
        """Profilo, progetto e tappa in modifica fanno parte della firma."""
        base = firma_pianificazione(1, "Modena", (), "Roma", "Gravel", None)
        self.assertNotEqual(base, firma_pianificazione(2, "Modena", (), "Roma", "Gravel", None))
        self.assertNotEqual(base, firma_pianificazione(1, "Modena", (), "Roma", "Strada", None))
        self.assertNotEqual(base, firma_pianificazione(1, "Modena", (), "Roma", "Gravel", 7))

    def test_normalizza_luogo_rimuove_gli_accenti(self):
        """Le lettere accentuate diventano il carattere semplice equivalente."""
        self.assertEqual(normalizza_luogo("Citta"), normalizza_luogo("Città"))

    def test_normalizza_luogo_tolera_none(self):
        """Un valore assente non deve far fallire la firma."""
        self.assertEqual(normalizza_luogo(None), "")


class TestWorkerAnnullabile(unittest.TestCase):
    """Il worker di routing deve poter essere annullato come gli altri."""

    def test_annullamento_preventivo(self):
        """Annullato prima di partire, il worker non emette alcun esito."""
        app = QApplication.instance() or QApplication([])
        self.addCleanup(app.quit)
        worker = PianificazionePercorsoWorker(1, "44.6,10.9", "44.5,11.0", "Gravel")
        esiti = []
        worker.esito.connect(esiti.append)
        worker.request_stop()
        self.assertTrue(worker.e_annullato())
        worker.run()  # esecuzione sincrona: non parte un vero thread
        self.assertEqual(esiti, [])

    def test_timeout_dichiarato(self):
        """Il timeout deve essere breve e dichiarato in un solo punto."""
        self.assertEqual(TIMEOUT_ROUTING_SECONDI, 60)


class TestTestiStato(unittest.TestCase):
    """I messaggi della riga di stato devono dire che cosa fare."""

    def test_errore_mostra_il_motivo(self):
        """Il testo d'errore contiene il motivo restituito dal servizio."""
        testo = testo_stato_errore_routing("BRouter non ha trovato un percorso")
        self.assertIn("BRouter non ha trovato un percorso", testo)

    def test_anteprima_pronta_mostra_la_distanza(self):
        """Con la distanza disponibile il messaggio la riporta."""
        self.assertIn("120 km", testo_stato_anteprima_pronta(120.4))

    def test_anteprima_pronta_senza_distanza(self):
        """Senza distanza il messaggio resta comunque leggibile."""
        self.assertEqual(testo_stato_anteprima_pronta(), "Percorso calcolato.")


if __name__ == "__main__":
    sys.exit(unittest.main())