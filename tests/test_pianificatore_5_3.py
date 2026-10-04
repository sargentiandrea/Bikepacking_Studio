"""Verifica della suddivisione in tappe per chilometri e giorni."""

import os
import sqlite3
import tempfile
import unittest
from contextlib import closing
from types import SimpleNamespace
from unittest.mock import patch

from PySide6.QtWidgets import QApplication

from gui.mappa_pianificatore import PannelloPianificazioneWidget
from service.geo_utils import calcola_distanza_haversine
from service.salvataggio_tappa_service import salva_percorso_suddiviso
from service.stats_service import analizza_dati_rotta_brouter
from service.suddivisione_percorso_service import (
    ORE_BICI_AL_GIORNO,
    calcola_suddivisione_percorso,
)


class TestCalcoloSuddivisione(unittest.TestCase):
    """Il servizio divide la linea ai chilometri o ai giorni richiesti."""

    def test_divide_per_chilometri_e_conserva_i_punti_di_confine(self):
        """Il caso da 220 km a 100 km/tappa produce due tappe e un residuo."""
        coordinate = [(0.0, 0.0, 100.0), (0.0, 1.0, 200.0), (0.0, 2.0, 300.0)]
        distanza = sum(
            calcola_distanza_haversine(*a[:2], *b[:2])
            for a, b in zip(coordinate, coordinate[1:])
        )

        risultato = calcola_suddivisione_percorso(
            coordinate,
            distanza_totale_km=distanza,
            km_per_tappa=100,
        )

        self.assertEqual(risultato["numero_tappe"], 3)
        self.assertEqual(len(risultato["punti_divisione"]), 2)
        self.assertAlmostEqual(sum(risultato["distanze_km"]), distanza, delta=0.1)
        self.assertEqual(
            risultato["tappe"][0][-1],
            risultato["tappe"][1][0],
        )
        self.assertEqual(
            risultato["tappe"][1][-1],
            risultato["tappe"][2][0],
        )
        self.assertTrue(all(len(punto) == 3 for tappa in risultato["tappe"] for punto in tappa))

    def test_parametro_superiore_alla_rotta_produce_una_tappa(self):
        """Una soglia maggiore della lunghezza non inventa tappe aggiuntive."""
        risultato = calcola_suddivisione_percorso(
            [(0.0, 0.0), (0.0, 1.0)],
            distanza_totale_km=111,
            km_per_tappa=550,
        )

        self.assertEqual(risultato["numero_tappe"], 1)
        self.assertEqual(risultato["punti_divisione"], [])

    def test_un_giorno_per_tappa_usa_tempo_e_sei_ore_giornaliere(self):
        """Una rotta da 36 ore viene ripartita in sei giornate di circa 83 km."""
        risultato = calcola_suddivisione_percorso(
            [(0.0, 0.0), (0.0, 4.5)],
            distanza_totale_km=500,
            giorni_per_tappa=1,
            tempo_totale_ore=36,
        )

        self.assertEqual(ORE_BICI_AL_GIORNO, 6)
        self.assertEqual(risultato["numero_tappe"], 6)
        self.assertAlmostEqual(risultato["distanze_km"][0], 83.4, delta=0.2)

    def test_senza_tempo_routing_i_giorni_non_si_possono_calcolare(self):
        """Non viene inventato un tempo per la modalità giorni."""
        with self.assertRaisesRegex(ValueError, "tempo totale"):
            calcola_suddivisione_percorso(
                [(0.0, 0.0), (0.0, 1.0)],
                distanza_totale_km=111,
                giorni_per_tappa=1,
                tempo_totale_ore=None,
            )

    def test_rifiuta_input_ambiguo_o_non_valido(self):
        """Una richiesta deve indicare un solo criterio positivo."""
        coordinate = [(0.0, 0.0), (0.0, 1.0)]
        for valori in (
            {"km_per_tappa": None, "giorni_per_tappa": None},
            {"km_per_tappa": 20, "giorni_per_tappa": 1},
            {"km_per_tappa": 0, "giorni_per_tappa": None},
        ):
            with self.subTest(valori=valori):
                with self.assertRaises(ValueError):
                    calcola_suddivisione_percorso(
                        coordinate,
                        distanza_totale_km=111,
                        **valori,
                    )


class TestStatisticheTemporaliRouting(unittest.TestCase):
    """Le statistiche espongono il tempo ricevuto dal routing."""

    def test_riporta_tempo_totale_in_ore(self):
        """Il tempo BRouter in secondi diventa ore utilizzabili dal pianificatore."""
        statistiche = analizza_dati_rotta_brouter(
            {"track-length": 500_000, "total-time": 36 * 3600},
            [(0.0, 0.0), (0.0, 4.5)],
        )

        self.assertEqual(statistiche["tempo_totale_ore"], 36)


class TestInterfacciaSuddivisione(unittest.TestCase):
    """La suddivisione appare solo nel contesto Percorso."""

    @classmethod
    def setUpClass(cls):
        """Crea l'applicazione Qt condivisa dai test dell'interfaccia."""
        cls.app = QApplication.instance() or QApplication([])

    def test_il_pannello_e_visibile_solo_per_il_contesto_percorso(self):
        """La scelta di un altro contesto nasconde il pannello di suddivisione."""
        pannello = PannelloPianificazioneWidget(
            mappa_widget=SimpleNamespace(
                parent_app=SimpleNamespace(current_progetto_id=1)
            )
        )
        self.assertTrue(pannello.pannello_suddivisione.isHidden())
        pannello.pulsanti_contesto["percorso"].click()
        self.assertFalse(pannello.pannello_suddivisione.isHidden())
        pannello.pulsanti_contesto["tappa_unica"].click()
        self.assertTrue(pannello.pannello_suddivisione.isHidden())
        pannello.close()

    def test_i_cambi_km_o_giorni_aggiornano_testo_e_punti_mappa(self):
        """La preview si aggiorna senza ricalcolare la rotta."""
        chiamate_mappa = []

        def mostra_anteprima(coordinate, punti=None, adatta_visuale=True):
            """Registra i dati passati dal pannello alla mappa temporanea."""
            chiamate_mappa.append((coordinate, punti or [], adatta_visuale))

        pannello = PannelloPianificazioneWidget(
            mappa_widget=SimpleNamespace(
                parent_app=SimpleNamespace(current_progetto_id=1),
                mostra_anteprima_percorso=mostra_anteprima,
            )
        )
        pannello.ultima_anteprima = {
            "coordinate": [(0.0, 0.0), (0.0, 4.5)],
            "statistiche": {
                "distanza_km": 500,
                "tempo_totale_ore": 36,
            },
        }

        pannello._imposta_contesto("percorso")
        pannello.radio_giorni_per_tappa.setChecked(True)
        self.assertIn("6 tappe", pannello.lbl_anteprima_suddivisione.text())
        pannello.spin_giorni_per_tappa.setValue(2)
        self.assertIn("3 tappe", pannello.lbl_anteprima_suddivisione.text())
        self.assertEqual(len(chiamate_mappa[-1][1]), 2)
        pannello.close()


class TestSalvataggioSuddivisione(unittest.TestCase):
    """Le tappe vengono registrate in ordine e i relativi GPX vengono creati."""

    def setUp(self):
        """Prepara un database e una cartella GPX temporanei."""
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
                    """
                )

    def test_salva_tutte_le_tappe_e_le_metriche_nell_ordine(self):
        """Una suddivisione completa crea una riga e un GPX per ogni segmento."""
        tappe = [
            {
                "coordinate": [(44.0, 11.0), (44.5, 11.5)],
                "distanza_km": 70.25,
            },
            {
                "coordinate": [(44.5, 11.5), (45.0, 12.0)],
                "distanza_km": 70.25,
            },
        ]
        with patch(
            "service.salvataggio_tappa_service.precalcola_tappa",
            return_value={"stato": "OK"},
        ) as precalcolo:
            esito = salva_percorso_suddiviso(
                9,
                tappe,
                "Modena",
                "Roma",
                db_name=self.db_name,
                directory_gpx=self.directory_gpx,
            )

        self.assertEqual(esito["numero_tappe"], 2)
        self.assertEqual(len(esito["tappe_ids"]), 2)
        self.assertEqual(precalcolo.call_count, 2)
        with closing(sqlite3.connect(self.db_name)) as conn:
            righe = conn.execute(
                """
                SELECT sequenza, distanza_km, stato, nome_file
                FROM tappe WHERE id_progetto = ? ORDER BY sequenza
                """,
                (9,),
            ).fetchall()
        self.assertEqual(
            [riga[:3] for riga in righe],
            [(1, 70.25, "ATTIVA"), (2, 70.25, "ATTIVA")],
        )
        self.assertTrue(
            all(
                os.path.isfile(
                    os.path.join(self.directory_gpx, "9", riga[3])
                )
                for riga in righe
            )
        )
        self.assertEqual(len(os.listdir(os.path.join(self.directory_gpx, "9"))), 2)

    def test_modifica_tappa_inserisce_i_segmenti_successivi_subito_dopo(self):
        """Le righe successive si spostano e restano dopo tutti i nuovi segmenti."""
        with closing(sqlite3.connect(self.db_name)) as conn:
            with conn:
                conn.execute(
                    """
                    INSERT INTO tappe (
                        id, id_progetto, sequenza, blocco, stato
                    ) VALUES (10, 9, 1, 'Pianificato', 'ATTIVA')
                    """
                )
                conn.execute(
                    """
                    INSERT INTO tappe (
                        id, id_progetto, sequenza, blocco, stato
                    ) VALUES (11, 9, 2, 'Pianificato', 'ATTIVA')
                    """
                )
        tappe = [
            {"coordinate": [(44.0, 11.0), (44.2, 11.2)], "distanza_km": 30},
            {"coordinate": [(44.2, 11.2), (44.5, 11.5)], "distanza_km": 40},
        ]
        with patch(
            "service.salvataggio_tappa_service.precalcola_tappa",
            return_value={"stato": "OK"},
        ):
            esito = salva_percorso_suddiviso(
                9,
                tappe,
                "Modena",
                "Roma",
                tappa_id=10,
                db_name=self.db_name,
                directory_gpx=self.directory_gpx,
            )

        with closing(sqlite3.connect(self.db_name)) as conn:
            righe = conn.execute(
                """
                SELECT id, sequenza FROM tappe
                WHERE id_progetto = ? ORDER BY sequenza
                """,
                (9,),
            ).fetchall()
        self.assertEqual(
            righe,
            [(10, 1), (esito["tappe_ids"][1], 2), (11, 3)],
        )

    def test_input_vuoto_non_crea_gpx_o_righe(self):
        """Una suddivisione vuota viene rifiutata senza effetti collaterali."""
        with self.assertRaisesRegex(ValueError, "non contiene tappe"):
            salva_percorso_suddiviso(
                9,
                [],
                "Modena",
                "Roma",
                db_name=self.db_name,
                directory_gpx=self.directory_gpx,
            )
        with closing(sqlite3.connect(self.db_name)) as conn:
            conteggio = conn.execute("SELECT COUNT(*) FROM tappe").fetchone()[0]
        self.assertEqual(conteggio, 0)

    def test_errore_database_rimuove_i_gpx_temporanei(self):
        """Un errore di scrittura SQL non lascia GPX orfani sul disco."""
        tappe = [
            {
                "coordinate": [(44.0, 11.0), (44.5, 11.5)],
                "distanza_km": 70,
            }
        ]
        with self.assertRaises(sqlite3.Error):
            salva_percorso_suddiviso(
                9,
                tappe,
                "Modena",
                "Roma",
                db_name=os.path.join(self.cartella.name, "database_inesistente.db"),
                directory_gpx=self.directory_gpx,
            )
        self.assertEqual(os.listdir(os.path.join(self.directory_gpx, "9")), [])


if __name__ == "__main__":
    unittest.main()
