"""Ricerca delle bandiere dei paesi nello sprite delle risorse grafiche.

Il modulo carica ``resources/sprite.png`` e ``resources/sprite.json`` e
mette a disposizione le funzioni di ricerca usate dal dialogo dell'elenco
paesi per associare a ogni codice ISO2 l'informazione dello sprite e la
denominazione italiana. Non contiene riferimenti all'interfaccia grafica.
"""

import json
import os

# Codici ISO2 il cui nome nello sprite non coincide con la nomenclatura standard.
TAGLIE_ISO_SPRITE = {
    "TR": "Turkey",
    "TW": "Taiwan",
    "VN": "Vietnam",
    "TH": "Thailand",
    "TZ": "Tanzania",
    "TG": "Togo",
    "TM": "Turkmenistan",
}


def percorso_risorsa(nome):
    """Restituisce il percorso assoluto di una risorsa nella cartella `resources`."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "resources", nome)


def carica_dati_sprite():
    """Carica `sprite.json`; in caso di errore restituisce un dizionario vuoto."""
    percorso = percorso_risorsa("sprite.json")
    if not os.path.exists(percorso):
        return {}
    try:
        with open(percorso, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as errore:
        print(f"Errore caricamento sprite.json: {errore}")
        return {}


def carica_pixmap_sprite():
    """Restituisce il `QPixmap` dello sprite, oppure `None` se non esiste."""
    from PySide6.QtGui import QPixmap

    percorso = percorso_risorsa("sprite.png")
    return QPixmap(percorso) if os.path.exists(percorso) else None


def risolvi_paese_sprite(iso2_code, nome_fallback, sprite_data):
    """Cerca l'informazione dello sprite per un paese.

    La ricerca avviene prima per codice ISO2, poi tramite i tagli noti e
    infine per corrispondenza del nome. Restituisce la tupla
    ``(informazione_sprite, nome_paese)``.
    """
    iso2_code = str(iso2_code).strip().upper()
    trovato = None
    nome_paese = str(nome_fallback)
    for sprite_key, info in sprite_data.items():
        if isinstance(info, dict) and str(info.get("iso_alpha2", "")).strip().upper() == iso2_code:
            trovato = info
            nome_paese = info.get("name_it", nome_paese)
            break

    if trovato is None:
        sprite_key = TAGLIE_ISO_SPRITE.get(iso2_code)
        candidato = sprite_data.get(sprite_key) if sprite_key else None
        if isinstance(candidato, dict):
            trovato = candidato
            nome_paese = candidato.get("name_it", nome_paese)

    if trovato is None:
        nome_pulito = nome_paese.strip().lower()
        for sprite_key, info in sprite_data.items():
            if not isinstance(info, dict):
                continue
            nomi = (
                sprite_key.lower().replace("_", " "),
                str(info.get("name_it", "")).strip().lower(),
                str(info.get("name_en", "")).strip().lower(),
            )
            if nome_pulito in nomi:
                trovato = info
                nome_paese = info.get("name_it", nome_paese)
                break

    return trovato, nome_paese