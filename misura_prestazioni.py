#!/usr/bin/env python
"""Misura i tempi dei principali passaggi di elaborazione dei file GPX.

Lo script non apre il database, non importa moduli della GUI e non richiede
MapLibre o le mappe offline. Usa solo la libreria standard di Python.

Le misure seguono le logiche trovate nel progetto:
- gui/dashboard.py: parsing dei punti traccia e distanza Haversine;
- service/stats_service.py: dislivello e stima della pendenza media;
- gui/mappa.py / WorkerCaricamentoMappa: coordinate, linea, marker e GeoJSON.

TODO: l'analisi completa dell'audit (gap e allarmi) è legata ai dati del
database e non è misurabile qui senza violare il requisito di lavorare solo
sui GPX.
TODO: la distanza dalla costa richiede i dati Natural Earth; le superfici e
le strade vietate richiedono le mappe vettoriali .mbtiles. Sono elaborazioni
separate e non vengono incluse in questo benchmark senza quelle risorse.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_GPX_DIR = ROOT_DIR / "gpx"
OPERATIONS = (
    "lettura_gpx",
    "parsing_coordinate",
    "distanza",
    "dislivello",
    "pendenza_media",
    "lettura_mappa",
    "parsing_mappa",
    "geometria_mappa",
    "costruzione_geojson",
)
IMPORT_OPERATIONS = ("lettura_gpx", "parsing_coordinate", "distanza", "dislivello", "pendenza_media")
DISPLAY_OPERATIONS = (
    "lettura_mappa",
    "parsing_mappa",
    "geometria_mappa",
    "costruzione_geojson",
)


def _local_name(tag: str) -> str:
    """Restituisce il nome XML senza namespace."""
    return tag.rsplit("}", 1)[-1]


def _iter_children_named(element: ET.Element, name: str):
    return (child for child in element if _local_name(child.tag) == name)


def _extract_tracks(root: ET.Element):
    """Estrae coordinate e quote seguendo l'ordine tracce/segmenti dell'app."""
    coordinates = []
    elevations = []
    for track in (element for element in root.iter() if _local_name(element.tag) == "trk"):
        for segment in _iter_children_named(track, "trkseg"):
            for point in _iter_children_named(segment, "trkpt"):
                lat = float(point.attrib["lat"])
                lon = float(point.attrib["lon"])
                elevation_element = next(_iter_children_named(point, "ele"), None)
                elevation = (
                    float(elevation_element.text)
                    if elevation_element is not None and elevation_element.text
                    else 0.0
                )
                coordinates.append((lat, lon))
                elevations.append(elevation)
    return coordinates, elevations


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Equivalente della funzione Haversine usata durante l'importazione."""
    earth_radius_km = 6371.0
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    value = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(delta_lon / 2) ** 2
    )
    return earth_radius_km * (2 * math.asin(math.sqrt(value)))


def _calculate_distance(coordinates) -> float:
    """Somma le distanze consecutive come in gui/dashboard.py."""
    return sum(
        _haversine_km(*coordinates[index], *coordinates[index + 1])
        for index in range(len(coordinates) - 1)
    )


def _calculate_elevation(elevations):
    """Replica la logica di service/stats_service.py per dislivelli e quota max."""
    valid_elevations = [elevation for elevation in elevations if elevation != 0.0]
    if not valid_elevations:
        return 0, 0, 0, 0

    ascent = 0.0
    descent = 0.0
    for previous, current in zip(valid_elevations, valid_elevations[1:]):
        difference = current - previous
        if difference > 0:
            ascent += difference
        else:
            descent += abs(difference)
    return ascent, descent, max(valid_elevations), len(valid_elevations)


def _calculate_average_grade(ascent: float, elevation_count: int) -> float:
    """Replica la stima esistente: salita / (punti validi * 50 m) * 100."""
    if elevation_count <= 1:
        return 0.0
    return (ascent / (elevation_count * 50)) * 100


def _extract_map_coordinates(root: ET.Element):
    """Replica le coordinate LineString del WorkerCaricamentoMappa."""
    coordinates = []
    for track in (element for element in root.iter() if _local_name(element.tag) == "trk"):
        for segment in _iter_children_named(track, "trkseg"):
            for point in _iter_children_named(segment, "trkpt"):
                coordinates.append([float(point.attrib["lon"]), float(point.attrib["lat"])])
    return coordinates


def _build_map_features(coordinates, sequence: int, filename: str):
    """Costruisce una linea GPX e i due marker analoghi a quelli della mappa."""
    if not coordinates:
        return []

    return [
        {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coordinates},
            "properties": {
                "tipo": "tappa",
                "tappa_id": sequence,
                "sequenza": sequence,
                "blocco": "Benchmark",
                "stato": "ATTIVA",
                "nome_file": filename,
            },
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": coordinates[0]},
            "properties": {
                "tipo": "marker_inizio",
                "sequenza": sequence,
                "nome": f"Partenza Tappa {sequence}",
                "nome_file": filename,
            },
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": coordinates[-1]},
            "properties": {
                "tipo": "marker_fine",
                "sequenza": sequence,
                "nome": f"Arrivo Tappa {sequence}",
                "nome_file": filename,
            },
        },
    ]


def _stratified_sample(files, count: int):
    """Seleziona file piccoli, medi e grandi in modo deterministico."""
    ordered = sorted(files, key=lambda path: (path.stat().st_size, path.name.casefold()))
    count = min(count, len(ordered))
    if count <= 0:
        return []
    if count < 3 or len(ordered) < 3:
        return [
            ordered[min(len(ordered) - 1, int((index + 0.5) * len(ordered) / count))]
            for index in range(count)
        ]

    remainder = len(ordered) % 3
    first_end = len(ordered) // 3 + (1 if remainder > 0 else 0)
    second_end = first_end + len(ordered) // 3 + (1 if remainder > 1 else 0)
    groups = (ordered[:first_end], ordered[first_end:second_end], ordered[second_end:])

    quotas = [count // 3] * 3
    for index in range(count % 3):
        quotas[index] += 1

    selected = []
    for group, quota in zip(groups, quotas):
        for index in range(quota):
            position = min(len(group) - 1, int((index + 0.5) * len(group) / quota))
            selected.append(group[position])
    return selected


def _measure_file(path: Path, sequence: int):
    """Misura le fasi separatamente e restituisce tempi, contatori e risultati."""
    timings = {operation: None for operation in OPERATIONS}
    result = {
        "file": path.name,
        "size_bytes": path.stat().st_size,
        "points": 0,
        "distance_km": None,
        "ascent_m": None,
        "descent_m": None,
        "average_grade_percent": None,
        "error": None,
    }

    try:
        start = time.perf_counter()
        xml_text = path.read_text(encoding="utf-8", errors="ignore")
        timings["lettura_gpx"] = time.perf_counter() - start

        start = time.perf_counter()
        root = ET.fromstring(xml_text)
        coordinates, elevations = _extract_tracks(root)
        timings["parsing_coordinate"] = time.perf_counter() - start
        result["points"] = len(coordinates)

        start = time.perf_counter()
        distance = _calculate_distance(coordinates)
        timings["distanza"] = time.perf_counter() - start
        result["distance_km"] = distance

        start = time.perf_counter()
        ascent, descent, max_elevation, elevation_count = _calculate_elevation(elevations)
        timings["dislivello"] = time.perf_counter() - start
        result["ascent_m"] = round(ascent)
        result["descent_m"] = round(descent)
        result["max_elevation_m"] = round(max_elevation)

        start = time.perf_counter()
        grade = _calculate_average_grade(ascent, elevation_count)
        timings["pendenza_media"] = time.perf_counter() - start
        result["average_grade_percent"] = round(grade, 1)

        start = time.perf_counter()
        map_xml_text = path.read_text(encoding="utf-8", errors="ignore")
        timings["lettura_mappa"] = time.perf_counter() - start

        start = time.perf_counter()
        map_root = ET.fromstring(map_xml_text)
        timings["parsing_mappa"] = time.perf_counter() - start

        start = time.perf_counter()
        map_coordinates = _extract_map_coordinates(map_root)
        features = _build_map_features(map_coordinates, sequence, path.name)
        timings["geometria_mappa"] = time.perf_counter() - start

        start = time.perf_counter()
        payload = {"type": "FeatureCollection", "features": features}
        geojson = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        timings["costruzione_geojson"] = time.perf_counter() - start
        result["geojson_bytes"] = len(geojson.encode("utf-8"))
    except (OSError, ET.ParseError, KeyError, ValueError, OverflowError) as error:
        result["error"] = f"{type(error).__name__}: {error}"

    result["timings"] = timings
    return result


def _format_duration(seconds):
    return f"{seconds:.6f} s"


def _print_results(results, total_files: int):
    valid_results = [result for result in results if result["error"] is None]
    print(f"\nFile misurati: {len(valid_results)} validi su {len(results)} selezionati.")
    print(
        "Le fasi sono separate: la visualizzazione include la seconda lettura "
        "e il secondo parsing eseguiti dal worker mappa."
    )
    print("Non sono inclusi database, GUI, invio a Flask o mappe offline.")

    for phase_name, operations in (
        ("TEMPI DI IMPORTAZIONE (misure separate)", IMPORT_OPERATIONS),
        ("TEMPI DI VISUALIZZAZIONE (misure separate)", DISPLAY_OPERATIONS),
    ):
        print(f"\n{phase_name}")
        for result in results:
            if result["error"]:
                continue
            timings = result["timings"]
            values = " | ".join(
                f"{operation}: {_format_duration(timings[operation])}"
                for operation in operations
            )
            print(
                f"  {result['file']} ({result['size_bytes']:,} byte, "
                f"{result['points']:,} punti) - {values}"
            )
            if phase_name.startswith("TEMPI DI IMPORTAZIONE"):
                print(
                    f"    distanza {result['distance_km']:.2f} km; "
                    f"dislivello +{result['ascent_m']} m / -{result['descent_m']} m; "
                    f"pendenza media {result['average_grade_percent']:.1f}%"
                )
            else:
                print(f"    GeoJSON serializzato: {result.get('geojson_bytes', 0):,} byte")

    errors = [result for result in results if result["error"]]
    if errors:
        print("\nFILE NON MISURATI")
        for result in errors:
            print(f"  {result['file']}: {result['error']}")

    print("\nTABELLA RIASSUNTIVA")
    print(f"{'Nome operazione':<28} {'Tempo medio':>14} {'Tempo massimo':>14} {'Tempo minimo':>14}")
    print("-" * 74)

    means = {}
    for operation in OPERATIONS:
        values = [
            result["timings"][operation]
            for result in valid_results
            if result["timings"][operation] is not None
        ]
        if not values:
            print(f"{operation:<28} {'n/d':>14} {'n/d':>14} {'n/d':>14}")
            continue
        mean_value = statistics.fmean(values)
        means[operation] = mean_value
        print(
            f"{operation:<28} {_format_duration(mean_value):>14} "
            f"{_format_duration(max(values)):>14} {_format_duration(min(values)):>14}"
        )

    import_mean = sum(means.get(operation, 0.0) for operation in IMPORT_OPERATIONS)
    display_mean = sum(means.get(operation, 0.0) for operation in DISPLAY_OPERATIONS)
    total_mean = import_mean + display_mean
    print("\nSTIMA LINEARE PER 1000 GPX (basata sui tempi medi del campione)")
    print(f"  Importazione misurata:       {import_mean * 1000:.2f} secondi")
    print(f"  Visualizzazione misurata:    {display_mean * 1000:.2f} secondi")
    print(f"  Totale delle fasi misurate:  {total_mean * 1000:.2f} secondi")
    if total_files and valid_results:
        estimated_all = total_mean * total_files
        print(
            f"  Per i {total_files:,} GPX trovati nella cartella: "
            f"{estimated_all:.2f} secondi"
        )
    print(
        "\nNota: la stima e una moltiplicazione lineare delle fasi misurate, "
        "non il tempo complessivo dell'app. La mappa reale deve inoltre inviare "
        "la geometria a Flask/MapLibre e visualizzarla."
    )


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Misura separatamente parsing, calcoli GPX e preparazione GeoJSON."
    )
    parser.add_argument(
        "-n",
        "--campione",
        type=int,
        default=10,
        help="numero di GPX da campionare (default: 10)",
    )
    parser.add_argument(
        "--cartella",
        type=Path,
        default=DEFAULT_GPX_DIR,
        help=f"cartella GPX (default: {DEFAULT_GPX_DIR})",
    )
    args = parser.parse_args(argv)

    if args.campione <= 0:
        parser.error("--campione deve essere maggiore di zero.")
    if not args.cartella.is_dir():
        print(f"Errore: cartella GPX non trovata: {args.cartella}", file=sys.stderr)
        return 1

    files = sorted(args.cartella.glob("*.gpx"))
    if not files:
        print(f"Nessun file .gpx trovato in: {args.cartella}", file=sys.stderr)
        return 1

    sample = _stratified_sample(files, args.campione)
    print(f"Cartella GPX: {args.cartella}")
    print(f"File GPX trovati: {len(files):,}; campione richiesto: {args.campione}; selezionati: {len(sample)}")
    print("Campione distribuito tra file piccoli, medi e grandi per dimensione.")

    results = []
    for sequence, path in enumerate(sample, start=1):
        print(f"\n[{sequence}/{len(sample)}] Misuro {path.name}...")
        results.append(_measure_file(path, sequence))

    _print_results(results, len(files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
