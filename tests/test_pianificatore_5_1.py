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

from gui.mappa_worker import TIMEOUT_ROUTING_MASSIMO_SECONDI, PianificazionePercorsoWorker
from service.dettagli_rotta_service import (
    testo_stato_anteprima_pronta,
    testo_stato_errore_routing,
    testo_stato_percorso_lungo,
)
from service.punti_service import firma_pianificazione, normalizza_luogo
from service.routing_timeout_service import (
    SOGLIA_PERCORSO_LUNGO_KM,
    stima_distanza_rotta_km,
    timeout_routing_secondi,
)


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

    def test_annullamento_preventivo_notifica_comunque(self):
        """Annullato prima di partire, il worker notifica l'annullamento.

        Non deve restare in silenzio: il gestore avvia la richiesta successiva
        proprio da questo esito, e un worker muto lascerebbe la coda ferma.
        """
        app = QApplication.instance() or QApplication([])
        self.addCleanup(app.quit)
        worker = PianificazionePercorsoWorker(1, "44.6,10.9", "44.5,11.0", "Gravel")
        esiti = []
        worker.esito.connect(esiti.append)
        worker.request_stop()
        self.assertTrue(worker.e_annullato())
        worker.run()  # esecuzione sincrona: non parte un vero thread
        self.assertEqual(len(esiti), 1)
        self.assertTrue(esiti[0]["annullato"])
        self.assertFalse(esiti[0]["riuscito"])

    def test_timeout_massimo_dichiarato(self):
        """Il tetto massimo deve essere dichiarato in un solo punto."""
        self.assertEqual(TIMEOUT_ROUTING_MASSIMO_SECONDI, 180)


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


class TestTimeoutDifferenziato(unittest.TestCase):
    """Il tetto di attesa deve crescere con la lunghezza del percorso."""

    def test_percorso_breve_usa_il_tetto_base(self):
        """Sotto i 200 km il tetto resta quello base di 60 secondi."""
        self.assertEqual(timeout_routing_secondi(0), 60)
        self.assertEqual(timeout_routing_secondi(100), 60)
        self.assertEqual(timeout_routing_secondi(200), 60)

    def test_percorso_medio_cresce_di_10_su_100_km(self):
        """Oltre la soglia il tetto cresce di 10 secondi ogni 100 km."""
        self.assertEqual(timeout_routing_secondi(300), 70)
        self.assertEqual(timeout_routing_secondi(400), 80)

    def test_bologna_napoli_ha_margine_su_il_tempo_misurato(self):
        """Bologna-Napoli misura 83,9 s: il tetto calcolato deve superarlo.

        È il caso che ha rotto l'applicazione con il tetto fisso a 60 s.
        """
        distanza_stimata = stima_distanza_rotta_km(
            [(44.4949, 11.3426), (40.8518, 14.2681)]
        )
        tetto = timeout_routing_secondi(distanza_stimata)
        self.assertGreater(distanza_stimata, 600)  # circa 700 km stimati
        self.assertGreater(tetto, 83.92)

    def test_il_tetto_ha_un_massimo(self):
        """Nessun percorso può superare il massimo assoluto."""
        self.assertEqual(timeout_routing_secondi(5000), 180)
        self.assertEqual(timeout_routing_secondi(100000), 180)

    def test_valori_assenti_usano_il_massimo(self):
        """Una distanza non calcolabile non deve troncare il calcolo."""
        self.assertEqual(timeout_routing_secondi(None), 180)
        self.assertEqual(timeout_routing_secondi("non un numero"), 180)


class TestStimaDistanza(unittest.TestCase):
    """La stima della lunghezza deve reggere casi limite."""

    def test_punti_insufficienti_danno_zero(self):
        """Meno di due punti non danno nulla su cui ragionare."""
        self.assertEqual(stima_distanza_rotta_km([]), 0.0)
        self.assertEqual(stima_distanza_rotta_km([(44.0, 11.0)]), 0.0)

    def test_punti_senza_coordinate_ignored(self):
        """I punti privi di coordinate vengono saltati, non rompono tutto."""
        distanza = stima_distanza_rotta_km(
            [(44.0, 11.0), (None, None), (44.1, 11.1)]
        )
        self.assertGreater(distanza, 0)

    def test_la_stima_correge_la_distanza_aerea(self):
        """La stima deve essere maggiore della somma dei segmenti aerei.

        Il tracciato reale segue strade e sentieri, quindi è più lungo della
        linea retta: senza la correzione i tempi sarebbero sottovalutati.
        """
        punti = [(44.0, 11.0), (44.1, 11.1)]
        solo_aerea = stima_distanza_rotta_km(punti) / 1.5
        self.assertGreater(stima_distanza_rotta_km(punti), solo_aerea)


class TestAvvisoPercorsoLungo(unittest.TestCase):
    """Oltre la soglia l'utente va avvertito che il percorso è lungo."""

    def test_avviso_sotto_soglia_assente(self):
        """Un percorso normale non genera l'avviso."""
        testo = testo_stato_percorso_lungo(50, "Percorso calcolato: 50 km.")
        self.assertEqual(testo, "Percorso calcolato: 50 km.")

    def test_avviso_oltre_soglia_presente(self):
        """Un percorso da oltre 200 km va avvertito."""
        testo = testo_stato_percorso_lungo(
            650, "Percorso calcolato: 650 km."
        )
        self.assertIn("Percorso lungo", testo)
        self.assertIn("spezzarlo in tappe", testo)

    def test_avviso_tolera_distanza_ignota(self):
        """Senza distanza non si deve inventare l'avviso."""
        self.assertEqual(
            testo_stato_percorso_lungo(None, "Percorso calcolato."),
            "Percorso calcolato.",
        )

    def test_soglia_di_200_km(self):
        """La soglia dell'avviso è quella dichiarata."""
        self.assertEqual(SOGLIA_PERCORSO_LUNGO_KM, 200)


if __name__ == "__main__":
    sys.exit(unittest.main())