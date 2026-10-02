"""Risoluzione dei percorsi GPX organizzati per progetto."""

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
GPX_DIR = ROOT_DIR / "gpx"


def percorso_gpx_progetto(
    id_progetto: int | str,
    nome_file: str,
    directory_gpx: str | Path | None = None,
) -> Path:
    """Costruisce il percorso di destinazione di un GPX appartenente al progetto."""
    nome = Path(nome_file).name
    if not nome or nome in {".", ".."}:
        raise ValueError("Il nome del file GPX non è valido.")
    radice_gpx = Path(directory_gpx) if directory_gpx is not None else GPX_DIR
    return radice_gpx / str(id_progetto) / nome


def trova_percorso_gpx(
    nome_file: str | Path | None,
    id_progetto: int | str | None = None,
    directory_gpx: str | Path | None = None,
) -> Path | None:
    """Cerca un GPX prima nella cartella del progetto e poi nella posizione legacy."""
    if not nome_file:
        return None

    percorso_input = Path(nome_file)
    if percorso_input.is_absolute() and percorso_input.is_file():
        return percorso_input

    nome = percorso_input.name
    if not nome or nome in {".", ".."}:
        return None

    radice_gpx = Path(directory_gpx) if directory_gpx is not None else GPX_DIR
    candidati = []
    if id_progetto is not None:
        candidati.append(radice_gpx / str(id_progetto) / nome)
    candidati.append(radice_gpx / nome)

    if percorso_input.is_file():
        candidati.append(percorso_input)

    for candidato in candidati:
        if candidato.is_file():
            return candidato
    return None
