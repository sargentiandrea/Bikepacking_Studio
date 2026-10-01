"""
Verifica perché lo stato è PARZIALE.
Da cancellare dopo l'uso.
"""
import sqlite3
from service.config import DB_NAME

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

cur.execute("""
    SELECT tappa_id, stato, errore, distanza_km, dislivello_pos_m, 
           pendenza_media_pct, pendenza_max_pct, gpx_sha256, versione_algoritmi
    FROM tappa_analisi
    ORDER BY tappa_id
    LIMIT 5
""")

for row in cur.fetchall():
    print(f"Tappa {row[0]}:")
    print(f"  Stato: {row[1]}")
    print(f"  Errore: {row[2]}")
    print(f"  Distanza: {row[3]} km")
    print(f"  Dislivello+: {row[4]} m")
    print(f"  Pendenza media: {row[5]}%")
    print(f"  Pendenza max: {row[6]}%")
    print(f"  Hash: {row[7][:16]}...")
    print(f"  Versione: {row[8]}")
    print()

conn.close()