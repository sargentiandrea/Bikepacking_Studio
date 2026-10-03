"""
Funzioni pure (senza Qt) sui punti del percorso: etichette dei punti di
passaggio e testi dell'elenco delle tappe intermedie.

Estratte da PannelloPianificazioneWidget (gui/mappa.py) per poterle provare
senza interfaccia grafica. Il comportamento è identico a quello originale.
"""


def etichetta_punto(indice):
    """
    Converte un indice (che parte da 0) nella notazione alfabetica da foglio
    di calcolo: 0 -> "A", 25 -> "Z", 26 -> "AA", 27 -> "AB", ...
    """
    risultato = ""
    valore = indice + 1
    while valore:
        valore, resto = divmod(valore - 1, 26)
        risultato = chr(ord("A") + resto) + risultato
    return risultato


def testo_coordinate(lat, lon):
    """Testo mostrato quando il nome del luogo non è (ancora) noto: 'lat, lon' a 6 decimali."""
    return f"{lat:.6f}, {lon:.6f}"


def prepara_tappe_intermedie(tappe):
    """
    Dalla lista delle tappe del percorso caricato (tuple con id, ordine,
    start_lat, start_lon, ...) ricava le tappe INTERMEDIE, cioè tutte tranne
    la prima e l'ultima, saltando quelle senza coordinate di partenza.

    Restituisce (tappe_intermedie, richieste_nomi):
    - tappe_intermedie: lista di dict {"id", "testo"} per l'elenco a scorrimento
    - richieste_nomi: lista di dict {"chiave", "lat", "lon"} per risolvere
      in background il nome del luogo di ciascuna
    """
    tappe_intermedie = []
    richieste_nomi = []
    for tappa in tappe[1:-1]:
        tappa_id, start_lat, start_lon = tappa[0], tappa[2], tappa[3]
        if start_lat is None or start_lon is None:
            continue
        tappe_intermedie.append({"id": tappa_id, "testo": testo_coordinate(start_lat, start_lon)})
        richieste_nomi.append({"chiave": tappa_id, "lat": start_lat, "lon": start_lon})
    return tappe_intermedie, richieste_nomi


def testo_riga_tappa_intermedia(indice, testo):
    """Testo di una riga dell'elenco: '📍 1.  nome' (la numerazione parte da 1)."""
    return f"📍 {indice + 1}.  {testo}"


def testo_intestazione_tappe_intermedie(numero, aperto):
    """Testo del pulsante che apre/chiude l'elenco: freccia giù se aperto, destra se chiuso."""
    return f"{'▾' if aperto else '▸'} {numero} tappa/e intermedia/e"


def aggiorna_testi_tappe(dati_tappe, testi_per_id):
    """
    Aggiorna in place il campo 'testo' delle tappe indicate in 'testi_per_id'
    (id tappa -> nuovo testo; i testi vuoti vengono ignorati).

    Restituisce la lista degli indici modificati, così la GUI aggiorna
    solo le righe cambiate.
    """
    modificati = []
    for indice, tappa in enumerate(dati_tappe):
        nuovo_testo = testi_per_id.get(tappa["id"])
        if nuovo_testo:
            tappa["testo"] = nuovo_testo
            modificati.append(indice)
    return modificati
