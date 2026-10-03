"""Calcolo del tempo di attesa concesso al servizio di routing.

Il timeout non può essere un numero fisso:BRouter è locale, ma il tempo di
elaborazione cresce forte con la lunghezza. Misure reali su questo servizio
(vedi la diagnostica della sotto-fase 5.1):

    Bologna-Modena    0,8 s
    Bologna-Firenze    7,7 s
    Bologna-Napoli   83,9 s   (profilo trekking)

Un tetto di 60 secondi faceva fallire percorsi che invece si calcolano
correttamente. Qui il tetto cresce con la lunghezza stimata, mantenendo
pero un massimo: oltre, non e un'interfaccia che si aspetta, e un'attesa
infinita peggiorerebbe il problema che il timeout doveva risolvere.
"""

# Fattore che collega la distanza in linea d'aria alla lunghezza reale del
# tracciato. I percorsi ciclisti non vanno in linea d'aria: la 1,5 e una
# stima conservativa misurata su tracciati italiani (Napoli-Bologna reale
# circa 700 km contro circa 470 km in linea d'aria, rapporto 1,49).
FATTORE_ROUTING_SU_AEREA = 1.5

# Tetto di partenza: basta e avanza per qualsiasi percorso entro 200 km,
# che si risolvono in pochi secondi.
TIMEOUT_BASE_SECONDI = 60
SOGLIA_CHILOMETRI_BASE = 200

# Oltre la soglia il tetto cresce di 10 secondi ogni 100 km stimati.
# Con 10 (e non 5) il margine su Bologna-Napoli passa da ~0 secondi a
# circa 25: un timeout che scatta di poco è indistinguibile da un errore.
TIMEOUT_SECONDI_PER_100_KM = 10

# Mai oltre questo valore, per quanto lungo sia il percorso.
TIMEOUT_MASSIMO_SECONDI = 180

# Oltre questa distanza l'utente viene avvertito che una singola tappa
# lunga è scomoda da gestire nel pianificatore.
SOGLIA_PERCORSO_LUNGO_KM = 200


def timeout_routing_secondi(distanza_stimata_km):
    """Restituisce i secondi di attesa concessi per una data lunghezza stimata.

    Fino a 200 km il tetto resta quello base; oltre cresce di 10 secondi ogni
    100 km, con un massimo assoluto. Un valore assente o non valido ricade sul
    tetto massimo, per non troncare un calcolo che potrebbe riuscire.

    :param distanza_stimata_km: lunghezza stimata del tracciato in km.
    :return: i secondi di attesa da passare alla richiesta HTTP.
    """
    try:
        distanza = float(distanza_stimata_km)
    except (TypeError, ValueError):
        return TIMEOUT_MASSIMO_SECONDI
    if distanza <= 0:
        return TIMEOUT_BASE_SECONDI

    if distanza <= SOGLIA_CHILOMETRI_BASE:
        return TIMEOUT_BASE_SECONDI

    eccedenza = distanza - SOGLIA_CHILOMETRI_BASE
    secondi = TIMEOUT_BASE_SECONDI + (eccedenza / 100.0) * TIMEOUT_SECONDI_PER_100_KM
    return int(min(secondi, TIMEOUT_MASSIMO_SECONDI))


def stima_distanza_rotta_km(coordinate):
    """Stima la lunghezza del tracciato a partire dalle coordinate dei punti.

    La somma dei segmenti in linea d'aria sottostima il tracciato reale, che
    segue strade e sentieri; si compensa con il fattore di correzione.

    :param coordinate: lista di coppie o terne (latitudine, longitudine, ...).
    :return: la lunghezza stimata in chilometri, 0 se i punti non bastano.
    """
    punti = [
        (punto[0], punto[1])
        for punto in (coordinate or [])
        if punto and punto[0] is not None and punto[1] is not None
    ]
    if len(punti) < 2:
        return 0.0

    # Import ritardato: il modulo resta utilizzabile anche senza Qt installata.
    from service.geo_utils import calcola_distanza_haversine

    somma = sum(
        calcola_distanza_haversine(
            punti[indice][0], punti[indice][1],
            punti[indice + 1][0], punti[indice + 1][1],
        )
        for indice in range(len(punti) - 1)
    )
    return somma * FATTORE_ROUTING_SU_AEREA