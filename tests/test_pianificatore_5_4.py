"""Test della classificazione e della gestione dei waypoint sulla rotta."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from PySide6.QtWidgets import QApplication

from gui.mappa_pianificatore import PannelloPianificazioneWidget
from service.waypoint_service import classifica_punto


class TestClassificazioneWaypoint(unittest.TestCase):
    """La distanza dalla rotta determina il comportamento del waypoint."""

    def test_punto_gia_sulla_rotta_viene_riconosciuto(self):
        """Un punto entro 100 metri dalla geometria non richiede una tappa."""
        risultato = classifica_punto(
            [(44.0, 10.0), (44.0, 11.0)],
            [{"id": 3, "coordinate": [(44.0, 10.0), (44.0, 11.0)]}],
            (44.0005, 10.5),
        )

        self.assertEqual(risultato["classificazione"], "gia_sul_percorso")
        self.assertLess(risultato["distanza_rotta_m"], 100)

    def test_punto_vicino_sceglie_la_tappa_geometricamente_piu_vicina(self):
        """Un punto fuori dalla rotta entro 5 km identifica la tappa più vicina."""
        tappe = [
            {
                "id": 70,
                "sequenza": 7,
                "coordinate": [(44.0, 10.0), (44.0, 11.0)],
            },
            {
                "id": 80,
                "sequenza": 8,
                "coordinate": [(44.04, 10.0), (44.04, 11.0)],
            },
        ]

        risultato = classifica_punto(
            [[(44.0, 10.0), (44.0, 11.0)], [(44.04, 10.0), (44.04, 11.0)]],
            tappe,
            (44.01, 10.5),
        )

        self.assertEqual(risultato["classificazione"], "vicino_a_tappa")
        self.assertEqual(risultato["tappa_id"], 70)
        self.assertEqual(risultato["tappa_sequenza"], 7)
        self.assertAlmostEqual(risultato["distanza_tappa_km"], 1.11, delta=0.03)

    def test_punto_lontano_non_collega_linee_disgiunte(self):
        """La distanza non inventa una linea tra tappe che non sono connesse."""
        geometrie = [
            [(44.0, 10.0), (44.0, 10.01)],
            [(44.0, 11.0), (44.0, 11.01)],
        ]

        risultato = classifica_punto(geometrie, [], (44.0, 10.5))

        self.assertEqual(risultato["classificazione"], "lontano")
        self.assertGreater(risultato["distanza_rotta_m"], 10_000)

    def test_rifiuta_geometria_non_valida(self):
        """Coordinate fuori intervallo non vengono accettate come geometrie."""
        with self.assertRaisesRegex(ValueError, "intervalli Lat/Lon"):
            classifica_punto(
                [(91.0, 10.0), (44.0, 11.0)],
                [],
                (44.0, 10.5),
            )


class TestGestioneWaypointMappa(unittest.TestCase):
    """Il click sulla rotta evita di aggiungere un waypoint già presente."""

    @classmethod
    def setUpClass(cls):
        """Crea l'applicazione Qt condivisa dai test dell'interfaccia."""
        cls.app = QApplication.instance() or QApplication([])

    def test_punto_sulla_rotta_non_crea_un_campo_intermedio(self):
        """Il messaggio informa che il punto esistente non è stato duplicato."""
        mappa = SimpleNamespace(
            parent_app=SimpleNamespace(current_progetto_id=12),
            geometrie_tappe_per_waypoint=lambda _progetto: [
                {
                    "id": 5,
                    "coordinate": [[(44.0, 10.0), (44.0, 11.0)]],
                }
            ],
        )
        pannello = PannelloPianificazioneWidget(mappa_widget=mappa)
        self.addCleanup(pannello.close)

        with patch(
            "gui.mappa_pianificatore.QMessageBox.information"
        ) as messaggio:
            pannello.gestisci_waypoint_da_mappa(44.0005, 10.5)

        self.assertEqual(pannello.punti_passaggio, [])
        messaggio.assert_called_once()

    def test_devia_tutto_mantiene_tappe_e_inserisce_il_waypoint_nella_posizione(self):
        """Il ricalcolo completo conserva le soste e sostituisce le righe esistenti."""
        mappa = SimpleNamespace(
            parent_app=SimpleNamespace(current_progetto_id=12)
        )
        pannello = PannelloPianificazioneWidget(mappa_widget=mappa)
        self.addCleanup(pannello.close)
        tappe = [
            {
                "id": 101,
                "sequenza": 1,
                "coordinate": [[(44.0, 11.0), (44.5, 11.5)]],
            },
            {
                "id": 202,
                "sequenza": 2,
                "coordinate": [[(44.5, 11.5), (45.0, 12.0)]],
            },
        ]
        righe_database = [
            (101, "a.gpx", 44.0, 11.0, 44.5, 11.5, 50.0),
            (202, "b.gpx", 44.5, 11.5, 45.0, 12.0, 60.0),
        ]
        with patch(
            "gui.mappa_pianificatore.carica_tappe_attive",
            return_value=righe_database,
        ):
            with patch.object(pannello, "_ricalcola_anteprima") as ricalcola:
                riuscito = pannello._imposta_sostituzione_percorso(
                    tappe,
                    44.7,
                    11.7,
                    202,
                )

        self.assertTrue(riuscito)
        self.assertEqual(pannello._tappe_ids_da_sostituire, [101, 202])
        self.assertEqual(pannello.input_partenza.text(), "44.000000, 11.000000")
        self.assertEqual(pannello.input_destinazione.text(), "45.000000, 12.000000")
        self.assertEqual(
            [punto["input"].text() for punto in pannello.punti_passaggio],
            ["44.500000, 11.500000", "44.700000, 11.700000"],
        )
        self.assertEqual(pannello.btn_salva.text(), "Aggiorna percorso")
        ricalcola.assert_called_once()


if __name__ == "__main__":
    unittest.main()
