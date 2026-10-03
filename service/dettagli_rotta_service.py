"""Preparazione senza Qt dei testi e dei dati mostrati nei dettagli della rotta."""

from service.routing_timeout_service import SOGLIA_PERCORSO_LUNGO_KM


def prepara_kpi_rotta(statistiche):
    """Formatta velocità, quote minima/massima e distanza con gli stessi testi della GUI."""
    statistiche = statistiche or {}
    velocita = statistiche.get("velocita_media_kmh")
    quota_min = statistiche.get("altitudine_min_m")
    quota_max = statistiche.get("altitudine_max_m")
    distanza = statistiche.get("distanza_km")
    return {
        "velocita": (
            f"Velocità media stimata: {velocita:.1f} km/h"
            if velocita is not None
            else "Velocità media stimata: --"
        ),
        "altitudine_massima": (
            f"Altitudine massima: {quota_max} m"
            if quota_max is not None
            else "Altitudine massima: --"
        ),
        "altitudine_minima": (
            f"Altitudine minima: {quota_min} m"
            if quota_min is not None
            else "Altitudine minima: --"
        ),
        "distanza": (
            f"Distanza totale: {distanza:.1f} km"
            if distanza is not None
            else "Distanza totale: --"
        ),
    }


def testo_stato_superfici_rotta(superfici):
    """Restituisce il messaggio già usato per le superfici ricevute dal routing."""
    if superfici:
        non_specificata = next(
            (
                voce["percentuale"]
                for voce in superfici
                if voce["categoria"] == "Non specificata"
            ),
            0,
        )
        if non_specificata >= 99:
            return "Il servizio di routing non ha fornito tag di superficie per questa rotta."
        return "Stima da tag stradali OpenStreetMap restituiti da BRouter."
    return "Superfici non disponibili."


def testo_stato_superfici_offline(risultato):
    """Formatta l'esito dell'analisi offline, inclusi copertura e tratti vietati."""
    if not risultato or not risultato.get("disponibile"):
        motivo = (risultato or {}).get("motivo", "Dati non disponibili.")
        return f"Superfici non calcolabili offline: {motivo}"

    copertura = risultato.get("copertura_percentuale", 0)
    numero_vietati = len(risultato.get("tratti_vietati", []))
    messaggio = (
        "Stima offline da mappe locali già scaricate "
        f"(copertura {copertura:.0f}% del percorso)."
    )
    if numero_vietati:
        messaggio += (
            f" Attenzione: {numero_vietati} tratto/i probabilmente vietati "
            "alle bici (vedi Audit)."
        )
    return messaggio


def testo_distanza_tappe(tappe):
    """Formatta la somma delle distanze delle tappe caricate, oppure '--' se è zero."""
    distanza_totale_km = sum(riga[6] or 0.0 for riga in tappe)
    return (
        f"Distanza totale: {distanza_totale_km:.1f} km"
        if distanza_totale_km > 0
        else "Distanza totale: --"
    )


def testi_altimetria(massima, minima):
    """Restituisce i testi delle quote presenti; un valore assente non va aggiornato nella GUI."""
    return (
        f"Altitudine massima: {int(massima)} m" if massima is not None else None,
        f"Altitudine minima: {round(minima)} m" if minima is not None else None,
    )


def testo_voce_legenda(superficie):
    """Formatta la dicitura della legenda per una singola categoria di superficie."""
    return f"● {superficie['categoria']} — {superficie['percentuale']:.0f}%"


# ---------------------------------------------------------------------------
# Riga di stato: "cosa puo fare ora" (sotto-fase 5.1, soluzione S5)
# ---------------------------------------------------------------------------

def testo_stato_calcolo():
    """Messaggio mostrato mentre il servizio di routing sta lavorando."""
    return "Sto calcolando il percorso..."


def testo_stato_annullato():
    """Messaggio mostrato quando l'utente annulla un calcolo in corso."""
    return "Calcolo annullato. Puoi riprovare quando vuoi."


def testo_stato_errore_routing(errore):
    """Messaggio mostrato quando il routing non riesce, con azione Riprova."""
    return f"Il percorso non e disponibile: {errore}"


def testo_stato_anteprima_pronta(distanza_km=None, giorni=None):
    """Messaggio mostrato quando la rotta e pronta e si puo salvare.

    Con la distanza si dice quanto e lungo il percorso; i giorni arrivano solo
    se disponibili (dipendono dal profilo usato dal servizio di routing).
    """
    parti = []
    if distanza_km is not None:
        parti.append(f"{distanza_km:.0f} km")
    if giorni:
        parti.append(f"{giorni} giorni")
    if not parti:
        return "Percorso calcolato."
    return "Percorso calcolato: " + ", ".join(parti) + "."


def testo_stato_campi_cambiati():
    """Messaggio mostrato quando i campi cambiano durante il calcolo."""
    return "I campi sono cambiati durante il calcolo: ricalcola l'anteprima."


def testo_stato_in_modifica(numero_tappa):
    """Messaggio mostrato mentre si sta modificando una tappa esistente."""
    return f"Stai modificando la tappa {numero_tappa}."


def testo_stato_percorso_lungo(distanza_km, testo_base):
    """Aggiunge l'avviso sul percorso lungo al messaggio di stato.

    Oltre 200 km una singola tappa e scomoda: si puo salvare e vedere tutto,
    ma non e un tratto che si percorre in giornata. L'avviso resta un
    consiglio e non blocca nulla.

    :param distanza_km: lunghezza del percorso in km.
    :param testo_base: il messaggio di stato da cui partire.
    :return: il messaggio con l'avviso, o il messaggio base se il percorso
        è sotto la soglia.
    """
    if distanza_km is None or distanza_km <= SOGLIA_PERCORSO_LUNGO_KM:
        return testo_base
    return (
        f"{testo_base} Percorso lungo: considera di spezzarlo in tappe."
    )
