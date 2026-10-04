"""Salvataggio di una tappa pianificata: GPX su disco, riga in SQLite e precalcolo.

Il modulo non dipende da Qt: la GUI (gui/mappa.py) si occupa di validazioni
e messaggi, qui c'è solo la parte dati.
"""

import os
import sqlite3
import uuid
from contextlib import closing

import gpxpy
import gpxpy.gpx

from service.config import BASE_DIR, DB_NAME
from service.gpx_paths import percorso_gpx_progetto, trova_percorso_gpx
from service.precalcolo_service import precalcola_tappa

# Stessa cartella GPX usata finora dalla GUI.
GPX_DIR = os.path.join(BASE_DIR, "gpx")


def salva_tappa_pianificata(
    id_progetto,
    coordinate,
    partenza,
    destinazione,
    distanza_km,
    tappa_id=None,
    db_name=DB_NAME,
    directory_gpx=GPX_DIR,
    esito=None,
    stato=None,
    blocco=None,
    crea_blocco=False,
):
    """Scrive il GPX della tappa, la registra in SQLite e lancia il precalcolo.

    Parametri:
    - coordinate: lista di punti (lat, lon) o (lat, lon, quota)
    - tappa_id: se indicato la tappa esistente viene aggiornata, altrimenti
      ne viene creata una nuova in coda al progetto
    - esito: dizionario opzionale che il servizio aggiorna man mano con
      "file_gpx"; serve al chiamante per ripulire il file se un passaggio
      successivo (non di questo servizio) fallisce.
    - stato: stato da salvare; `BOZZA` evita il precalcolo delle metriche
    - blocco: blocco del progetto a cui assegnare la tappa
    - crea_blocco: registra `blocco` in fondo all'ordine del progetto

    Restituisce un dizionario con: tappa_id, file_gpx (Path del nuovo GPX),
    aggiornata (True se era una modifica), precalcolo_riuscito,
    errore_precalcolo.

    Il GPX precedente viene cancellato solo se il precalcolo riesce. Se il
    salvataggio fallisce, il GPX appena scritto viene rimosso e l'eccezione
    (ValueError, OSError, sqlite3.Error...) viene rilanciata al chiamante.
    """
    if esito is None:
        esito = {}
    file_gpx = None
    file_gpx_precedente = None
    stato_precedente = "ATTIVA"
    stato_salvataggio = stato
    tappa_in_aggiornamento = tappa_id is not None
    precalcolo_riuscito = True
    errore_precalcolo = None
    precalcolo_saltato = stato_salvataggio == "BOZZA"
    if stato_salvataggio is not None and stato_salvataggio not in {
        "ATTIVA", "SOSPESA", "VARIANTE", "BOZZA"
    }:
        raise ValueError("Lo stato della tappa non è valido.")
    if crea_blocco and not blocco:
        raise ValueError("Il nome del nuovo blocco è obbligatorio.")
    try:
        os.makedirs(directory_gpx, exist_ok=True)
        conn = sqlite3.connect(db_name, timeout=30.0)
        with closing(conn):
            with conn:
                cursor = conn.cursor()
                if blocco is not None:
                    _completa_ordine_blocchi(cursor, id_progetto)
                    _valida_blocco(cursor, id_progetto, blocco, crea_blocco)
                    if crea_blocco:
                        _aggiungi_blocco_ordine(cursor, id_progetto, blocco)
                if tappa_id is not None:
                    cursor.execute(
                        "SELECT nome_file, stato FROM tappe WHERE id = ? AND id_progetto = ?",
                        (tappa_id, id_progetto),
                    )
                    riga_tappa_esistente = cursor.fetchone()
                    if not riga_tappa_esistente:
                        raise ValueError("La tappa da aggiornare non è più presente nel progetto.")
                    file_gpx_precedente = riga_tappa_esistente[0]
                    stato_precedente = riga_tappa_esistente[1] or "ATTIVA"
                else:
                    cursor.execute(
                        "SELECT COALESCE(MAX(sequenza), 0) + 1 FROM tappe WHERE id_progetto = ?",
                        (id_progetto,),
                    )
                    sequenza = cursor.fetchone()[0]

                nome_file = f"Pianificato_{id_progetto}_{uuid.uuid4().hex[:10]}.gpx"
                file_gpx = percorso_gpx_progetto(
                    id_progetto,
                    nome_file,
                    directory_gpx=directory_gpx,
                )
                esito["file_gpx"] = file_gpx
                os.makedirs(file_gpx.parent, exist_ok=True)

                traccia = gpxpy.gpx.GPX()
                traccia.creator = "Bikepacking Studio"
                segmento = gpxpy.gpx.GPXTrackSegment()
                for punto in coordinate:
                    latitudine, longitudine = punto[:2]
                    elevazione = float(punto[2]) if len(punto) > 2 else None
                    segmento.points.append(
                        gpxpy.gpx.GPXTrackPoint(latitudine, longitudine, elevation=elevazione)
                    )
                track = gpxpy.gpx.GPXTrack(name=f"{partenza} - {destinazione}")
                track.segments.append(segmento)
                traccia.tracks.append(track)

                with open(file_gpx, "w", encoding="utf-8") as file:
                    file.write(traccia.to_xml())

                valori_rotta = (
                    nome_file,
                    coordinate[0][0],
                    coordinate[0][1],
                    coordinate[-1][0],
                    coordinate[-1][1],
                    round(distanza_km, 2),
                )
                if tappa_id is not None:
                    nuovo_stato = stato_salvataggio or stato_precedente
                    cursor.execute(
                        """
                        UPDATE tappe SET nome_file = ?, start_lat = ?, start_lon = ?,
                            end_lat = ?, end_lon = ?, distanza_km = ?, stato = ?,
                            blocco = COALESCE(?, blocco)
                        WHERE id = ? AND id_progetto = ?
                        """,
                        (*valori_rotta, nuovo_stato, blocco, tappa_id, id_progetto),
                    )
                    if cursor.rowcount != 1:
                        raise ValueError("La tappa non è stata aggiornata; verifica il progetto attivo.")
                else:
                    cursor.execute(
                        """
                        INSERT INTO tappe (
                            id_progetto, sequenza, blocco, nome_file,
                            start_lat, start_lon, end_lat, end_lon,
                            distanza_km, stato
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            id_progetto,
                            sequenza,
                            blocco or "Pianificato",
                            *valori_rotta,
                            stato_salvataggio or "ATTIVA",
                        ),
                    )
                    tappa_id = cursor.lastrowid
                if blocco is not None:
                    cursor.execute(
                        """
                        SELECT COALESCE(MAX(sequenza), 0) + 1 FROM tappe
                        WHERE id_progetto = ?
                        """,
                        (id_progetto,),
                    )
                    nuova_sequenza = cursor.fetchone()[0]
                    cursor.execute(
                        "UPDATE tappe SET sequenza = ? WHERE id = ?",
                        (nuova_sequenza, tappa_id),
                    )
                    _riordina_tappe_per_blocco(cursor, id_progetto)

        if not precalcolo_saltato:
            # Il precalcolo avviene a salvataggio concluso: se fallisce la tappa resta salvata.
            try:
                # precalcola_tappa vuole il percorso come testo: un Path farebbe fallire il binding SQLite.
                risultato_precalcolo = precalcola_tappa(tappa_id, str(file_gpx), db_name)
                if risultato_precalcolo.get("stato") == "ERRORE":
                    precalcolo_riuscito = False
                    errore_precalcolo = risultato_precalcolo.get(
                        "errore", "errore durante il precalcolo"
                    )
            except Exception as errore:
                precalcolo_riuscito = False
                errore_precalcolo = str(errore)
                print(f"Errore precalcolo tappa {tappa_id}: {errore}")

        # Il vecchio GPX si cancella solo se il nuovo è stato precalcolato con successo.
        if file_gpx_precedente and precalcolo_riuscito:
            percorso_precedente = trova_percorso_gpx(
                file_gpx_precedente,
                id_progetto,
                directory_gpx=directory_gpx,
            )
            if percorso_precedente is not None:
                try:
                    os.remove(percorso_precedente)
                except OSError as errore_file:
                    print(f"Nota: non è stato possibile rimuovere il GPX precedente: {errore_file}")
    except Exception:
        rimuovi_gpx_se_esiste(file_gpx)
        raise

    return {
        "tappa_id": tappa_id,
        "file_gpx": file_gpx,
        "aggiornata": tappa_in_aggiornamento,
        "precalcolo_riuscito": precalcolo_riuscito,
        "precalcolo_saltato": precalcolo_saltato,
        "errore_precalcolo": errore_precalcolo,
    }


def _completa_ordine_blocchi(cursor, id_progetto):
    """Registra in coda eventuali blocchi già usati ma assenti dall'ordine salvato."""
    cursor.execute(
        """
        SELECT nome_blocco FROM blocchi_ordine
        WHERE id_progetto = ? ORDER BY ordine ASC
        """,
        (id_progetto,),
    )
    blocchi_ordinati = [riga[0] for riga in cursor.fetchall()]
    cursor.execute(
        """
        SELECT COALESCE(NULLIF(TRIM(blocco), ''), 'Generale'), MIN(sequenza)
        FROM tappe WHERE id_progetto = ?
        GROUP BY COALESCE(NULLIF(TRIM(blocco), ''), 'Generale')
        ORDER BY MIN(sequenza) ASC
        """,
        (id_progetto,),
    )
    for nome_blocco, _ in cursor.fetchall():
        if nome_blocco not in blocchi_ordinati:
            _aggiungi_blocco_ordine(cursor, id_progetto, nome_blocco)
            blocchi_ordinati.append(nome_blocco)


def _aggiungi_blocco_ordine(cursor, id_progetto, nome_blocco):
    """Aggiunge un blocco in fondo all'ordine del progetto."""
    cursor.execute(
        "SELECT COALESCE(MAX(ordine), 0) + 1 FROM blocchi_ordine WHERE id_progetto = ?",
        (id_progetto,),
    )
    ordine = cursor.fetchone()[0]
    cursor.execute(
        """
        INSERT INTO blocchi_ordine (id_progetto, nome_blocco, ordine)
        VALUES (?, ?, ?)
        """,
        (id_progetto, nome_blocco, ordine),
    )


def _valida_blocco(cursor, id_progetto, nome_blocco, crea_blocco):
    """Verifica che il blocco esista o che il nuovo nome sia libero."""
    cursor.execute(
        """
        SELECT 1 FROM blocchi_ordine
        WHERE id_progetto = ? AND lower(nome_blocco) = lower(?)
        UNION
        SELECT 1 FROM tappe
        WHERE id_progetto = ? AND lower(COALESCE(NULLIF(TRIM(blocco), ''), 'Generale')) = lower(?)
        LIMIT 1
        """,
        (id_progetto, nome_blocco, id_progetto, nome_blocco),
    )
    esiste = cursor.fetchone() is not None
    if crea_blocco and esiste:
        raise ValueError("Esiste già un blocco con questo nome.")
    if not crea_blocco and not esiste:
        raise ValueError("Il blocco selezionato non è più presente nel progetto.")


def _riordina_tappe_per_blocco(cursor, id_progetto):
    """Rinumera le tappe mantenendo insieme i blocchi nel loro ordine ufficiale."""
    cursor.execute(
        """
        SELECT nome_blocco FROM blocchi_ordine
        WHERE id_progetto = ? ORDER BY ordine ASC
        """,
        (id_progetto,),
    )
    blocchi = [riga[0] for riga in cursor.fetchall()]
    cursor.execute(
        """
        SELECT id, COALESCE(NULLIF(TRIM(blocco), ''), 'Generale'), sequenza
        FROM tappe WHERE id_progetto = ? ORDER BY sequenza ASC
        """,
        (id_progetto,),
    )
    tappe = cursor.fetchall()
    tappe_per_blocco = {}
    for riga in tappe:
        tappe_per_blocco.setdefault(riga[1], []).append(riga[0])
        if riga[1] not in blocchi:
            blocchi.append(riga[1])

    sequenza = 1
    for nome_blocco in blocchi:
        for id_tappa in tappe_per_blocco.get(nome_blocco, []):
            cursor.execute(
                "UPDATE tappe SET sequenza = ? WHERE id = ?",
                (sequenza, id_tappa),
            )
            sequenza += 1


def rimuovi_gpx_se_esiste(file_gpx):
    """Cancella un GPX appena scritto; ignora gli errori di cancellazione."""
    if file_gpx and os.path.exists(file_gpx):
        try:
            os.remove(file_gpx)
        except OSError:
            pass
