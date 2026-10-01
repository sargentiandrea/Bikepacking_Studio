"""
Esegue il precalcolo batch su tutte le tappe.
Da cancellare dopo l'uso.
"""
import time
from service.precalcolo_batch_service import (
    precalcola_tutte_le_tappe,
    stima_tempo_precalcolo,
)

print("=== STIMA TEMPO ===")
stima = stima_tempo_precalcolo()
print(f"Stima: {stima:.1f} secondi ({stima/60:.1f} minuti)")
print()

input("Premi INVIO per avviare il precalcolo completo...")

print()
print("=== PRECALCOLO COMPLETO ===")
print("(puoi interrompere con Ctrl+C)")
print()

inizio = time.time()
risultato = precalcola_tutte_le_tappe()
durata = time.time() - inizio

print()
print("=== RISULTATO FINALE ===")
print(f"  Stato: {risultato['stato']}")
print(f"  Tappe elaborate: {risultato['elaborate']}")
print(f"  Tappe saltate: {risultato['saltate']}")
print(f"  Tappe fallite: {risultato['fallite']}")
print(f"  Totale: {risultato['totale']}")
print(f"  Tempo: {risultato['tempo_totale_secondi']:.1f} secondi")
print()

if risultato['errori']:
    print(f"Errori (primi 10):")
    for err in risultato['errori'][:10]:
        print(f"  Tappa {err['tappa_id']}: {err['errore']}")
    if len(risultato['errori']) > 10:
        print(f"  ... e altri {len(risultato['errori']) - 10}")