"""
Verifica lo stato delle tabelle di precalcolo.
Da cancellare dopo l'uso.
"""
import sqlite3

DB = "data/bikepacking_app.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()

# Quante tappe ci sono in totale
cur.execute("SELECT COUNT(*) FROM tappe")
print(f"Tappe totali: {cur.fetchone()[0]}")

# Quante hanno un record in tappa_analisi
cur.execute("SELECT COUNT(*) FROM tappa_analisi")
print(f"Record in tappa_analisi: {cur.fetchone()[0]}")

# Quanti per stato
cur.execute("SELECT stato, COUNT(*) FROM tappa_analisi GROUP BY stato")
print("\nDistribuzione stati in tappa_analisi:")
for stato, conteggio in cur.fetchall():
    print(f"  {stato}: {conteggio}")

# Quante tappe hanno distanza_km > 0 in tappe
cur.execute("SELECT COUNT(*) FROM tappe WHERE distanza_km > 0")
print(f"\nTappe con distanza_km > 0 in tappe: {cur.fetchone()[0]}")

# Quante tappe hanno stato ATTIVA
cur.execute("SELECT COUNT(*) FROM tappe WHERE stato = 'ATTIVA'")
print(f"Tappe con stato ATTIVA: {cur.fetchone()[0]}")

# Esempio di una tappa (per debug)
cur.execute("SELECT t.id, t.nome_file, t.stato, t.distanza_km, a.stato, a.distanza_km FROM tappe t LEFT JOIN tappa_analisi a ON t.id = a.tappa_id LIMIT 5")
print("\nPrime 5 tappe (con stato analisi):")
for row in cur.fetchall():
    print(f"  ID={row[0]}, file={row[1]}, stato_tappa={row[2]}, dist_tappa={row[3]}, stato_analisi={row[4]}, dist_analisi={row[5]}")

conn.close()