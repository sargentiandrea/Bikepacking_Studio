"""Verifica che il pannello di pianificazione si costruisca e accetti i cambi.

Non chiama la rete: si controlla solo il cablagggio introdotto dalla
sotto-fase 5.1 (gestore unico del routing, riga di stato con azioni).
"""

import os
import sys
import unittest

# I test vivono in tests/ ma il codice sta nella radice del progetto.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication

from gui.mappa_dettagli import PannelloDettagliRotta


class TestPannelloDettagli(unittest.TestCase):
    """Il pannello dei dettagli deve mostrare messaggi e azioni contestuali."""

    @classmethod
    def setUpClass(cls):
        """Crea una sola applicazione Qt per tutti i test di questa classe."""
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        """Ogni test parte da un pannello pulito."""
        self.pannello = PannelloDettagliRotta()

    def _azioni(self):
        """Restituisce le etichette dei pulsanti attualmente mostrati."""
        return [
            self.pannello.layout_azioni.itemAt(i).widget().text()
            for i in range(self.pannello.layout_azioni.count())
        ]

    def test_azioni_iniziali_assenti(self):
        """All'avvio non ci sono azioni: la riga resta pulita."""
        self.assertEqual(self._azioni(), [])

    def test_messaggio_con_azione(self):
        """Un messaggio con azione mostra il testo e il pulsante."""
        self.pannello.imposta_stato_con_azioni("Errore di rete", [("Riprova", lambda: None)])
        self.assertEqual(self.pannello.lbl_stato.text(), "Errore di rete")
        self.assertEqual(self._azioni(), ["Riprova"])

    def test_azioni_sostituite_non_accumulano(self):
        """Chiamare due volte non deve lasciare pulsanti obsoleti."""
        self.pannello.imposta_stato_con_azioni("Primo", [("Annulla", lambda: None)])
        self.pannello.imposta_stato_con_azioni("Secondo", [("Riprova", lambda: None)])
        self.assertEqual(self._azioni(), ["Riprova"])

    def test_reset_pulisce_azioni_e_stato(self):
        """Il reset riporta il pannello allo stato iniziale."""
        self.pannello.imposta_stato_con_azioni("Errore", [("Riprova", lambda: None)])
        self.pannello.reset()
        self.assertEqual(self._azioni(), [])
        self.assertEqual(self.pannello.lbl_stato.text(), "")

    def test_pulsante_aziona_chiamata(self):
        """Il pulsante deve chiamare la funzione passata con le azioni."""
        chiamate = []
        self.pannello.imposta_stato_con_azioni("Prova", [("Riprova", lambda: chiamate.append(1))])
        self.pannello.layout_azioni.itemAt(0).widget().click()
        self.assertEqual(chiamate, [1])


if __name__ == "__main__":
    sys.exit(unittest.main())