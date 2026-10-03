"""Thread (QThread) usati dal pannello di pianificazione della mappa.

Contiene i quattro worker che lavorano in background per non bloccare
l'interfaccia: analisi superfici offline, nomi dei luoghi, altimetria e
calcolo della rotta con BRouter. Non dipende da gui/mappa.py.
"""

import os
import re

import gpxpy
import requests
from PySide6.QtCore import QThread, Signal

from service.config import BASE_DIR, BROUTER_URL
from service.geonames_service import cerca_coordinate_luogo
from service.gpx_paths import trova_percorso_gpx

# Stessa cartella GPX usata da gui/mappa.py.
GPX_DIR = os.path.join(BASE_DIR, "gpx")


class WorkerAnalisiSuperficiOffline(QThread):
    """
    Calcola in background (fuori dal thread dell'interfaccia) la ripartizione
    superfici/divieti bici di un progetto, leggendo solo le mappe locali già
    scaricate. Nessuna chiamata di rete: usa service/superfici_service.py,
    che a sua volta rilegge la cache già salvata quando possibile.
    """
    analisi_completata = Signal(dict)

    def __init__(self, id_progetto, parent=None):
        super().__init__(parent)
        self.id_progetto = id_progetto
        self._annullato = False

    def request_stop(self):
        """Chiede al worker di interrompersi il prima possibile (es. l'utente
        ha già cambiato percorso e il risultato non servirebbe più): senza
        questo, un'analisi pesante su un percorso enorme continuava a
        girare in sottofondo anche quando ormai inutile, rallentando i
        calcoli successivi mettendosi in coda dietro di essa."""
        self._annullato = True

    def run(self):
        try:
            from service.superfici_service import analizza_superfici_progetto
            risultato = analizza_superfici_progetto(
                self.id_progetto, deve_continuare=lambda: not self._annullato
            )
        except Exception as errore:
            risultato = {"disponibile": False, "motivo": f"Errore durante l'analisi offline: {errore}"}
        self.analisi_completata.emit(risultato)


class WorkerNomiLuoghi(QThread):
    """
    Risolve in background (fuori dal thread dell'interfaccia) il nome del
    luogo più vicino a una o più coordinate, leggendo solo le mappe locali
    già scaricate (nessuna chiamata di rete). Usato dal pannello per
    mostrare "Aosta" invece di "45.737200, 7.315500".
    """
    nomi_pronti = Signal(object)

    def __init__(self, richieste, parent=None):
        super().__init__(parent)
        # richieste: lista di dict {"chiave": ..., "lat": ..., "lon": ...}
        self.richieste = list(richieste or [])
        self._annullato = False

    def request_stop(self):
        """Vedi WorkerAnalisiSuperficiOffline.request_stop: stessa logica."""
        self._annullato = True

    def run(self):
        from service.geocodifica_offline_service import nome_luogo_da_coordinate
        risultati = {}
        for richiesta in self.richieste:
            if self._annullato:
                break
            try:
                nome = nome_luogo_da_coordinate(richiesta["lat"], richiesta["lon"])
            except Exception as errore:
                print(f"Nota: geocodifica offline non riuscita: {errore}")
                nome = None
            risultati[richiesta["chiave"]] = nome or f"{richiesta['lat']:.6f}, {richiesta['lon']:.6f}"
        self.nomi_pronti.emit(risultati)


class WorkerAltimetria(QThread):
    """
    Legge in background (fuori dal thread dell'interfaccia) i file GPX di un
    percorso per calcolare altitudine massima e minima. Con percorsi molto
    lunghi (centinaia di tappe) questa lettura può richiedere parecchi
    secondi: farla sul thread principale bloccava l'intera applicazione.
    """
    altimetria_pronta = Signal(dict)

    def __init__(self, nomi_file, parent=None):
        super().__init__(parent)
        self.nomi_file = list(nomi_file or [])
        self._annullato = False

    def request_stop(self):
        """Vedi WorkerAnalisiSuperficiOffline.request_stop: stessa logica."""
        self._annullato = True

    def run(self):
        quote = []
        for nome_file, id_progetto in self.nomi_file:
            if self._annullato:
                break
            percorso_gpx = trova_percorso_gpx(
                nome_file, id_progetto, directory_gpx=GPX_DIR
            )
            if percorso_gpx is None:
                continue
            try:
                with open(percorso_gpx, "r", encoding="utf-8", errors="ignore") as file_gpx:
                    traccia = gpxpy.parse(file_gpx)
                quote.extend(
                    punto.elevation
                    for track in traccia.tracks
                    for segmento in track.segments
                    for punto in segmento.points
                    if punto.elevation is not None
                )
            except Exception as errore_lettura:
                print(f"Nota: impossibile leggere l'altimetria di {nome_file}: {errore_lettura}")

        risultato = {
            "massima": max(quote) if quote else None,
            "minima": min(quote) if quote else None,
        }
        self.altimetria_pronta.emit(risultato)


class PianificazionePercorsoWorker(QThread):
    """Geocodifica partenza e arrivo e richiede a BRouter il tracciato GPX."""

    completato = Signal(bool, dict, str)

    def __init__(self, id_progetto, partenza, destinazione, profilo, punti_passaggio=None, parent=None, tappa_id=None):
        super().__init__(parent)
        self.id_progetto = id_progetto
        self.partenza = partenza
        self.destinazione = destinazione
        self.profilo = profilo
        self.punti_passaggio = list(punti_passaggio or [])
        self.tappa_id = tappa_id

    def _geocodifica(self, luogo):
        coordinate = re.fullmatch(
            r"\s*([-+]?\d+(?:\.\d+)?)\s*[,;]\s*([-+]?\d+(?:\.\d+)?)\s*",
            luogo,
        )
        if coordinate:
            latitudine, longitudine = map(float, coordinate.groups())
            if -90 <= latitudine <= 90 and -180 <= longitudine <= 180:
                return latitudine, longitudine
            raise ValueError(f"Coordinate fuori intervallo: '{luogo}'.")

        return cerca_coordinate_luogo(luogo)

    def _profilo_brouter(self):
        if "strada" in self.profilo.casefold():
            return "fastbike"
        return "trekking"

    def run(self):
        try:
            luoghi = [self.partenza, *self.punti_passaggio, self.destinazione]
            coordinate_luoghi = [
                self._geocodifica(luogo) for luogo in luoghi
            ]

            if len(set(coordinate_luoghi)) != len(coordinate_luoghi):
                raise ValueError("Due o più punti inseriti corrispondono alla stessa posizione.")

            lonlats = "|".join(
                f"{longitudine},{latitudine}"
                for latitudine, longitudine in coordinate_luoghi
            )

            risposta = requests.get(
                BROUTER_URL,
                params={
                    "lonlats": lonlats,
                    "profile": self._profilo_brouter(),
                    "alternativeidx": 0,
                    "format": "geojson",
                },
                timeout=320,
            )
            risposta.raise_for_status()
            dati = risposta.json()
            features = dati.get("features", [])
            if not features:
                raise ValueError("BRouter non ha trovato un percorso ciclabile tra i due luoghi.")

            feature_rotta = features[0]
            proprieta_rotta = feature_rotta.get("properties", {})
            coordinate_geojson = feature_rotta.get("geometry", {}).get("coordinates", [])
            coordinate = []
            for punto in coordinate_geojson:
                if len(punto) < 2:
                    continue
                longitudine, latitudine = float(punto[0]), float(punto[1])
                if not (-180 <= longitudine <= 180 and -90 <= latitudine <= 90):
                    continue
                punto_gpx = (latitudine, longitudine)
                if len(punto) > 2:
                    try:
                        punto_gpx += (float(punto[2]),)
                    except (TypeError, ValueError):
                        pass
                coordinate.append(punto_gpx)

            if len(coordinate) < 2:
                raise ValueError("La risposta del servizio non contiene una geometria valida.")

            from service.stats_service import analizza_dati_rotta_brouter
            statistiche = analizza_dati_rotta_brouter(proprieta_rotta, coordinate)

            self.completato.emit(True, {
                "id_progetto": self.id_progetto,
                "partenza": self.partenza,
                "destinazione": self.destinazione,
                "coordinate": coordinate,
                "profilo": self.profilo,
                "tappa_id": self.tappa_id,
                "statistiche": statistiche,
            }, "")
        except (requests.RequestException, ValueError, KeyError, TypeError) as errore:
            self.completato.emit(False, {}, str(errore))
        except Exception as errore:
            self.completato.emit(False, {}, f"Errore imprevisto durante il calcolo: {errore}")
