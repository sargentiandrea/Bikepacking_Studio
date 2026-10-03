"""Cache in memoria dei dati della mappa, uno per progetto (senza Qt).

Per ogni progetto conserva l'ultimo GeoJSON mostrato e la "firma" dei dati
del database con cui ? stato costruito. Se la firma attuale coincide, la
mappa pu? riusare il GeoJSON senza rileggere i GPX.
"""


class CacheMappaProgetto:
    """Dizionario {id_progetto: {"firma": ..., "geojson": ...}} con metodi dedicati."""

    def __init__(self):
        self._dati = {}

    def ottieni(self, id_progetto):
        """Restituisce la voce di cache del progetto ({"firma", "geojson"}) oppure None."""
        return self._dati.get(id_progetto)

    def firma(self, id_progetto):
        """Restituisce la firma salvata per il progetto, o None se non c'?."""
        voce = self._dati.get(id_progetto)
        return voce.get("firma") if voce is not None else None

    def salva(self, id_progetto, firma, geojson):
        """Memorizza GeoJSON e firma del progetto, sostituendo la voce precedente."""
        self._dati[id_progetto] = {"firma": firma, "geojson": geojson}

    def e_valida(self, id_progetto, firma_corrente):
        """True se la firma corrente esiste ed ? uguale a quella in cache."""
        return firma_corrente is not None and firma_corrente == self.firma(id_progetto)
