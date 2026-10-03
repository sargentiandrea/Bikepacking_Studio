"""Operazioni di dominio sui trasferimenti logistici che colmano i GAP.

Il modulo si occupa di leggere l'allarme di audit associato al gap,
validare le coordinate delle due tappe e registrare il trasferimento
evitando i duplicati. Non contiene riferimenti all'interfaccia grafica.
"""

import math
import sqlite3
from contextlib import closing

from service.config import DB_NAME


def carica_allarme_gap(id_progetto, allarme_id):
    """Restituisce la riga dell'allarme di gap aperto, oppure `None`.

    :param id_progetto: progetto attualmente aperto.
    :param allarme_id: identificativo dell'allarme da esaminare.
    :raises sqlite3.Error: in caso di errore di lettura dal database.
    """
    with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            """
            SELECT
                a.id,
                a.id_progetto,
                a.tappa_origine_id,
                a.tappa_destinazione_id,
                t1.nome_file AS nome_origine,
                t1.end_lat AS origine_lat,
                t1.end_lon AS origine_lon,
                t2.nome_file AS nome_destinazione,
                t2.start_lat AS destinazione_lat,
                t2.start_lon AS destinazione_lon
            FROM allarmi_percorso a
            LEFT JOIN tappe t1 ON t1.id = a.tappa_origine_id
            LEFT JOIN tappe t2 ON t2.id = a.tappa_destinazione_id
            WHERE a.id = ? AND a.id_progetto = ? AND a.risolto = 0
            """,
            (allarme_id, id_progetto),
        ).fetchone()


def valida_coordinate_gap(allarme):
    """Estrae e valida le coordinate di inizio e fine del gap.

    :return: la tupla ``(origine_lat, origine_lon, destinazione_lat,
        destinazione_lon)`` con valori `float` validi, oppure
        ``(None, messaggio_errore)`` se i dati non sono utilizzabili. Il
        messaggio è destinato a un avviso all'utente.
    """
    coordinate = (
        allarme["origine_lat"],
        allarme["origine_lon"],
        allarme["destinazione_lat"],
        allarme["destinazione_lon"],
    )
    if any(valore is None for valore in coordinate):
        return None, (
            "Coordinate mancanti\n"
            "Non posso associare il trasferimento al gap perché una delle "
            "due tappe non contiene le coordinate necessarie."
        )
    try:
        origine_lat, origine_lon, destinazione_lat, destinazione_lon = (
            float(valore) for valore in coordinate
        )
    except (TypeError, ValueError, OverflowError):
        return None, (
            "Coordinate non valide\n"
            "Le coordinate delle tappe non sono numeri validi; il "
            "trasferimento non è stato salvato."
        )
    valori = (origine_lat, origine_lon, destinazione_lat, destinazione_lon)
    if not all(math.isfinite(valore) for valore in valori):
        return None, (
            "Coordinate non valide\n"
            "Le coordinate delle tappe non sono valide; il trasferimento "
            "non è stato salvato."
        )
    if (
        not -90 <= origine_lat <= 90
        or not -180 <= origine_lon <= 180
        or not -90 <= destinazione_lat <= 90
        or not -180 <= destinazione_lon <= 180
    ):
        return None, (
            "Coordinate non valide\n"
            "Le coordinate delle tappe sono fuori dai limiti geografici "
            "consentiti; il trasferimento non è stato salvato."
        )
    return valori, None


def nomi_tappe_gap(allarme):
    """Restituisce i nomi delle due tappe del gap, con fallback sull'id."""
    nome_origine = allarme["nome_origine"] or (
        f"Tappa {allarme['tappa_origine_id']}"
    )
    nome_destinazione = allarme["nome_destinazione"] or (
        f"Tappa {allarme['tappa_destinazione_id']}"
    )
    return nome_origine, nome_destinazione


def salva_trasferimento(id_progetto, dati, coordinate):
    """Registra il trasferimento, evitando duplicati sulle stesse coordinate.

    :param dati: dizionario con le chiavi `mezzo`, `vettore`, `da`, `a`,
        `durata`, `costo` e `note`.
    :param coordinate: tupla con le coordinate del gap.
    :return: `True` se il trasferimento è stato inserito, `False` se ne esiste
        già uno equivalente.
    :raises sqlite3.Error: in caso di errore di scrittura sul database.
    """
    origine_lat, origine_lon, destinazione_lat, destinazione_lon = coordinate
    with closing(sqlite3.connect(DB_NAME, timeout=30.0)) as conn:
        conn.execute("BEGIN IMMEDIATE")
        trasferimenti = conn.execute(
            """
            SELECT start_lat, start_lon, end_lat, end_lon
            FROM trasferimenti
            WHERE id_progetto = ?
            """,
            (id_progetto,),
        ).fetchall()
        gia_coperto = any(
            start_lat is not None
            and start_lon is not None
            and end_lat is not None
            and end_lon is not None
            and abs(start_lat - origine_lat) < 0.01
            and abs(start_lon - origine_lon) < 0.01
            and abs(end_lat - destinazione_lat) < 0.01
            and abs(end_lon - destinazione_lon) < 0.01
            for start_lat, start_lon, end_lat, end_lon in trasferimenti
        )
        if gia_coperto:
            conn.rollback()
            return False
        conn.execute(
            """
            INSERT INTO trasferimenti (
                id_progetto, tipo_mezzo, vettore, da_luogo, a_luogo,
                durata, costo_eur, note, start_lat, start_lon,
                end_lat, end_lon
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                id_progetto,
                dati["mezzo"],
                dati["vettore"],
                dati["da"],
                dati["a"],
                dati["durata"],
                dati["costo"],
                dati["note"],
                origine_lat,
                origine_lon,
                destinazione_lat,
                destinazione_lon,
            ),
        )
        conn.commit()
    return True
