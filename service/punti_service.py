"""
Funzioni pure (senza Qt) sui punti del percorso: etichette dei punti di
passaggio e testi dell'elenco delle tappe intermedie.

Estratte da PannelloPianificazioneWidget (gui/mappa.py) per poterle provare
senza interfaccia grafica. Il comportamento è identico a quello originale.
"""

import unicodedata


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


# ---------------------------------------------------------------------------
# Form dei punti di passaggio (sotto-fase 3.2)
# ---------------------------------------------------------------------------

def testo_segnaposto_punto(etichetta):
    """Testo guida (placeholder) di un campo punto di passaggio, es. 'Punto di passaggio B...'."""
    return f"Punto di passaggio {etichetta}..."


def pulisci_testi(testi):
    """Restituisce i testi dei campi senza spazi iniziali/finali, nello stesso ordine."""
    return [testo.strip() for testo in testi]


def normalizza_luogo(testo):
    """
    Normalizza un testo di luogo per confrontarlo senza falsi differimenti.

    Rimuove gli spazi iniziali e finali, riduce gli spazi interni ripetuti a
    uno solo, passa a minuscolo e sostituisce i caratteri accentuati con il
    equivalente non accentato. Serve alla firma dell'anteprima: senza questo,
    digitare "modena" invece di "Modena" fa ricalcolare tutta la rotta.
    """
    testo = str(testo or "")
    testo = " ".join(testo.split()).casefold()
    # Scompono i caratteri accentuati e scarto il segno di combinazione: cosi
    # una citta con accento e una senza danno la stessa firma.
    testo = "".join(
        carattere
        for carattere in unicodedata.normalize("NFD", testo)
        if not unicodedata.combining(carattere)
    )
    return testo


def firma_pianificazione(
    progetto,
    partenza,
    punti,
    destinazione,
    profilo,
    tappa_in_modifica_id,
    contesto=None,
    blocco=None,
):
    """
    Crea la chiave che dice se un'anteprima calcolata corrisponde ancora ai campi
    del form: se cambia anche solo un campo, la chiave e diversa.
    I testi vengono normalizzati (spazi, maiuscole, accenti): cosi "Modena" e
    "modena" non fanno ricalcolare inutilmente la rotta.
    Contesto e blocco fanno parte della chiave per non salvare una rotta con
    una scelta diversa da quella presente quando e stata calcolata.
    """
    return (
        progetto,
        normalizza_luogo(partenza),
        tuple(normalizza_luogo(punto) for punto in punti),
        normalizza_luogo(destinazione),
        normalizza_luogo(profilo),
        tappa_in_modifica_id,
        normalizza_luogo(contesto),
        normalizza_luogo(blocco),
    )


def valida_pianificazione(progetto, partenza, destinazione, punti):
    """
    Controlla progetto e luoghi del form. I testi vengono ripuliti dagli spazi.

    Restituisce (dati, errore):
    - se tutto è valido: dati = (progetto, partenza, punti, destinazione), errore = None
    - se non è valido: dati = None, errore = (titolo, messaggio) da mostrare all'utente
    """
    partenza = partenza.strip()
    destinazione = destinazione.strip()
    punti = pulisci_testi(punti)

    if not progetto:
        return None, ("Percorso richiesto", "Apri o crea un percorso dalla Dashboard prima di pianificare.")
    if not partenza or not destinazione:
        return None, ("Campi incompleti", "Inserisci sia partenza che destinazione.")
    if any(not punto for punto in punti):
        return None, ("Punto incompleto", "Completa oppure rimuovi ogni punto di passaggio.")
    return (progetto, partenza, punti, destinazione), None


def indice_primo_punto_vuoto(testi):
    """Indice del primo campo vuoto (spazi compresi) tra i testi dei punti di passaggio, o None se sono tutti pieni."""
    for indice, testo in enumerate(testi):
        if not testo.strip():
            return indice
    return None


def estremi_tappa(coordinate):
    """
    Dalle coordinate [(lat, lon), ...] di una tappa esistente ricava i testi di
    partenza e destinazione per il form: (testo_partenza, testo_destinazione).
    Solleva IndexError se la lista è vuota.
    """
    return testo_coordinate(*coordinate[0][:2]), testo_coordinate(*coordinate[-1][:2])