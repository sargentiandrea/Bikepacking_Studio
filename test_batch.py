"""
Test del batch di precalcolo su un piccolo campione.
Da cancellare dopo il test.
"""
import sqlite3
from service.precalcolo_batch_service import (
    precalcola_tutte_le_tappe,
    stima_tempo_precalcolo,
    ottieni_stato_batch,
)
from service.config import DB_NAME

# Pulisci i record esistenti per le tappe di test
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()
cur.execute("DELETE FROM tappa_analisi WHERE tappa_id IN (1, 2, 3, 4, 5)")
cur.execute("DELETE FROM tappa_segmenti WHERE tappa_id IN (1, 2, 3, 4, 5)")
conn.commit()
conn.close()
print("Record delle tappe 1-5 cancellati per il test")
print()

# Prima: stato attuale
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM tappa_analisi")
print(f"Record in tappa_analisi PRIMA: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM tappa_analisi WHERE stato = 'COMPLETO'")
print(f"Record COMPLETO PRIMA: {cur.fetchone()[0]}")
conn.close()
print()

# Stima tempo
print("=== STIMA TEMPO ===")
stima = stima_tempo_precalcolo()
print(f"Stima per tutte le tappe: {stima:.1f} secondi")
print()

# Precalcola SOLO 5 tappe
# Usiamo id_progetto per limitare, oppure modifichiamo la funzione
print("=== PRECALCOLO SU 5 TAPPE (manuale) ===")
from service.precalcolo_batch_service import _tappe_attive, _percorso_gpx
from service.precalcolo_service import precalcola_tappa

tappe = _tappe_attive(None)[:5]
print(f"Testando {len(tappe)} tappe...")
print()

for tappa_id, nome_file in tappe:
    percorso = _percorso_gpx(nome_file)
    if percorso is None:
        print(f"  Tappa {tappa_id}: GPX non trovato ({nome_file})")
        continue
    risultato = precalcola_tappa(tappa_id, percorso, DB_NAME)
    print(f"  Tappa {tappa_id} ({nome_file}): stato={risultato.get('stato')}, distanza={risultato.get('distanza_km')} km")

print()

# Dopo: stato
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM tappa_analisi")
print(f"Record in tappa_analisi DOPO: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM tappa_analisi WHERE stato = 'COMPLETO'")
print(f"Record COMPLETO DOPO: {cur.fetchone()[0]}")
cur.execute("SELECT stato, COUNT(*) FROM tappa_analisi GROUP BY stato")
print("Distribuzione stati:")
for stato, conteggio in cur.fetchall():
    print(f"  {stato}: {conteggio}")
conn.close()