"""
Verifica lo stato delle tappe (per capire se ci sono varianti o sospese).
Da cancellare dopo l'uso.
"""
import sqlite3

DB = "data/bikepacking_app.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()

# Conta per stato
cur.execute("SELECT stato, COUNT(*) FROM tappe GROUP BY stato")
print("Tappe per stato:")
for stato, conteggio in cur.fetchall():
    print(f"  {stato}: {conteggio}")
print()

# Conta per ruolo
cur.execute("SELECT ruolo, COUNT(*) FROM tappe GROUP BY ruolo")
print("Tappe per ruolo:")
for ruolo, conteggio in cur.fetchall():
    print(f"  {ruolo}: {conteggio}")
print()

# Tappe NON attive o con ruolo diverso da "Traccia Principale (ATTIVA)"
cur.execute("""
    SELECT id, nome_file, stato, ruolo 
    FROM tappe 
    WHERE stato != 'ATTIVA' 
       OR (ruolo IS NOT NULL AND ruolo != 'Traccia Principale (ATTIVA)')
    LIMIT 20
""")
print("Prime 20 tappe con stato o ruolo diverso dal default:")
for row in cur.fetchall():
    print(f"  ID={row[0]}, file={row[1]}, stato={row[2]}, ruolo={row[3]}")
print()

# Pendenza media in tappa_analisi
cur.execute("SELECT AVG(pendenza_media_pct), MIN(pendenza_media_pct), MAX(pendenza_media_pct) FROM tappa_analisi WHERE pendenza_media_pct IS NOT NULL")
print(f"Pendenza media in tappa_analisi: {cur.fetchone()}")

cur.execute("SELECT COUNT(*) FROM tappa_analisi WHERE pendenza_media_pct IS NULL")
print(f"Tappe con pendenza NULL: {cur.fetchone()[0]}")

conn.close()