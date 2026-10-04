"""Verifica della sotto-fase 5.2: contesto, bozze tecniche e blocchi di viaggio."""

import os
import sqlite3
import tempfile
import unittest
from contextlib import closing
from types import SimpleNamespace
from unittest.mock import patch

from PySide6.QtWidgets import QApplication

from gui.mappa_pianificatore import PannelloPianificazioneWidget
from service.planning_context_service import (
    CONTESTI_PIANIFICAZIONE,
    carica_blocchi_progetto,
    stato_da_contesto,
    valida_nome_nuovo_blocco,
)
from service.punti_service import firma_pianificazione
from service.salvataggio_tappa_service import salva_tappa_pianificata
from service.tappe_service import stato_da_ruolo


class TestContestoPianificazione(unittest.TestCase):
    """Le quattro scelte hanno valori e stati espliciti."""

    def test_sono_disponibili_i_quattro_contesti_previsti(self):
        """Il servizio espone tappa, percorso, viaggio e test."""
        self.assertEqual(
            [valore for valore, _ in CONTESTI_PIANIFICAZIONE],
            ["tappa_unica", "percorso", "parte_viaggio", "test"],
        )

    def test_il_test_tecnico_diventa_una_bozza(self):
        """Solo il test tecnico viene salvato con stato BOZZA."""
        self.assertEqual(stato_da_contesto("test"), "BOZZA")
        self.assertEqual(stato_da_contesto("tappa_unica"), "ATTIVA")
        self.assertEqual(stato_da_contesto("percorso"), "ATTIVA")
        self.assertEqual(stato_da_contesto("parte_viaggio"), "ATTIVA")

    def test_contesto_sconosciuto_viene_rifiutato(self):
        """Un contesto non previsto non può raggiungere il salvataggio."""
        with self.assertRaises(ValueError):
            stato_da_contesto("altro")

    def test_la_firma_distingue_contesto_e_blocco(self):
        """Una scelta diversa invalida l'anteprima precedente."""
        base = firma_pianificazione(1, "Modena", (), "Roma", "Gravel", None)
        self.assertNotEqual(
            base,
            firma_pianificazione(
                1, "Modena", (), "Roma", "Gravel", None, "test", None
            ),
        )
        self.assertNotEqual(
            firma_pianificazione(
                1, "Modena", (), "Roma", "Gravel", None, "parte_viaggio", "Alpi"
            ),
            firma_pianificazione(
                1, "Modena", (), "Roma", "Gravel", None, "parte_viaggio", "Sicilia"
            ),
        )

    def test_il_ruolo_bozza_e_riconoscibile_dalla_dashboard(self):
        """Il quarto ruolo della tabella mantiene lo stato BOZZA."""
        self.assertEqual(stato_da_ruolo(3), "BOZZA")

    def test_il_pannello_chiede_il_contesto_prima_di_salvare(self):
        """Il pulsante di salvataggio richiede la scelta e riflette il contesto."""
        app = QApplication.instance() or QApplication([])
        self.assertIsNotNone(app)
        pannello = PannelloPianificazioneWidget(
            mappa_widget=SimpleNamespace(
                parent_app=SimpleNamespace(current_progetto_id=1)
            )
        )
        self.assertIsNone(pannello._dati_contesto_salvataggio(mostra_dialogo=False))

        pannello.pulsanti_contesto["test"].click()
        self.assertEqual(pannello._contesto_selezionato, "test")
        self.assertEqual(pannello.btn_salva.text(), "Salva bozza")
        self.assertEqual(pannello._dati_contesto_salvataggio(), ("BOZZA", None, False))
        pannello.close()


class TestSalvataggioContesto(unittest.TestCase):
    """Le scelte agiscono su un database temporaneo, senza toccare i dati utente."""

    def setUp(self):
        """Prepara tappe e blocchi in un database isolato."""
        self.cartella = tempfile.TemporaryDirectory()
        self.addCleanup(self.cartella.cleanup)
        self.db_name = os.path.join(self.cartella.name, "test.db")
        self.directory_gpx = os.path.join(self.cartella.name, "gpx")
        with closing(sqlite3.connect(self.db_name)) as conn:
            with conn:
                conn.executescript(
                    """
                    CREATE TABLE tappe (
                        id INTEGER PRIMARY KEY,
                        id_progetto INTEGER,
                        sequenza INTEGER,
                        blocco TEXT,
                        nome_file TEXT,
                        start_lat REAL,
                        start_lon REAL,
                        end_lat REAL,
                        end_lon REAL,
                        distanza_km REAL,
                        stato TEXT
                    );
                    CREATE TABLE blocchi_ordine (
                        id INTEGER PRIMARY KEY,
                        id_progetto INTEGER,
                        nome_blocco TEXT,
                        ordine INTEGER
                    );
                    INSERT INTO blocchi_ordine (id_progetto, nome_blocco, ordine)
                        VALUES (1, 'Alpi', 1), (1, 'Sicilia', 2);
                    INSERT INTO tappe (id, id_progetto, sequenza, blocco, stato)
                        VALUES (1, 1, 1, 'Alpi', 'ATTIVA'),
                               (2, 1, 2, 'Sicilia', 'ATTIVA');
                    """
                )

    def _salva(self, **opzioni):
        """Salva una rotta di prova in file temporanei."""
        return salva_tappa_pianificata(
            1,
            [(44.0, 11.0), (45.0, 12.0)],
            "Modena",
            "Roma",
            123,
            db_name=self.db_name,
            directory_gpx=self.directory_gpx,
            **opzioni,
        )

    def test_test_tecnico_non_calcola_le_metriche(self):
        """La bozza viene scritta con stato BOZZA senza invocare il precalcolo."""
        with patch("service.salvataggio_tappa_service.precalcola_tappa") as precalcolo:
            esito = self._salva(stato="BOZZA")

        precalcolo.assert_not_called()
        self.assertTrue(esito["precalcolo_saltato"])
        with closing(sqlite3.connect(self.db_name)) as conn:
            stato = conn.execute(
                "SELECT stato FROM tappe WHERE id = ?", (esito["tappa_id"],)
            ).fetchone()[0]
        self.assertEqual(stato, "BOZZA")

    def test_tappa_nuova_si_accoda_al_blocco_selezionato(self):
        """La nuova tappa entra in coda al blocco e i blocchi restano contigui."""
        with patch(
            "service.salvataggio_tappa_service.precalcola_tappa",
            return_value={"stato": "OK"},
        ):
            esito = self._salva(stato="ATTIVA", blocco="Alpi")

        with closing(sqlite3.connect(self.db_name)) as conn:
            righe = conn.execute(
                "SELECT blocco, sequenza FROM tappe ORDER BY sequenza"
            ).fetchall()
        self.assertEqual(
            righe,
            [("Alpi", 1), ("Alpi", 2), ("Sicilia", 3)],
        )
        self.assertEqual(carica_blocchi_progetto(1, self.db_name), ["Alpi", "Sicilia"])
        self.assertIsNotNone(esito["tappa_id"])

    def test_nuovo_blocco_viene_aggiunto_in_coda_all_ordine(self):
        """La creazione del blocco aggiunge una voce senza sostituire quelle esistenti."""
        with patch(
            "service.salvataggio_tappa_service.precalcola_tappa",
            return_value={"stato": "OK"},
        ):
            self._salva(stato="ATTIVA", blocco="Appennini", crea_blocco=True)

        self.assertEqual(
            carica_blocchi_progetto(1, self.db_name),
            ["Alpi", "Sicilia", "Appennini"],
        )

    def test_tappa_esistente_viene_accodata_al_blocco_scelto(self):
        """Modificare una tappa in una parte di viaggio la sposta in coda al blocco."""
        with patch(
            "service.salvataggio_tappa_service.precalcola_tappa",
            return_value={"stato": "OK"},
        ):
            self._salva(stato="ATTIVA", blocco="Alpi", tappa_id=2)

        with closing(sqlite3.connect(self.db_name)) as conn:
            righe = conn.execute(
                "SELECT id, blocco, sequenza FROM tappe ORDER BY sequenza"
            ).fetchall()
        self.assertEqual(righe, [(1, "Alpi", 1), (2, "Alpi", 2)])


class TestNomeNuovoBlocco(unittest.TestCase):
    """Il nome del blocco è obbligatorio e non può duplicarne uno esistente."""

    def test_normalizza_spazi_e_accetta_nome_univoco(self):
        """Gli spazi superflui vengono ridotti prima del salvataggio."""
        self.assertEqual(
            valida_nome_nuovo_blocco("  Dolomiti   Nord ", ["Alpi"]),
            ("Dolomiti Nord", None),
        )

    def test_rifiuta_nome_vuoto_o_duplicato(self):
        """Il nome vuoto e un duplicato non vengono accettati."""
        self.assertIsNotNone(valida_nome_nuovo_blocco("  ", [])[1])
        self.assertIsNotNone(valida_nome_nuovo_blocco("alpi", ["Alpi"])[1])


if __name__ == "__main__":
    unittest.main()
