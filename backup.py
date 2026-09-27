import os
import shutil
from datetime import datetime


def esegui_backup_progetto():
    print("=== 🛡️ AVVIO SCRIPT DI BACKUP SICUREZZA - BIKEPACKING STUDIO ===")
    
    # 1. Configurazione percorsi
    cartella_progetto = os.getcwd()
    nome_cartella_progetto = os.path.basename(cartella_progetto)
    
    # Crea una cartella di backup sul Desktop chiamata "Backup_Bikepacking_Studio"
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    cartella_destinazione_madre = os.path.join(desktop, "Backup_Bikepacking_Studio")
    
    # Genera un sotto-archivio con la data e l'ora esatta di adesso
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cartella_backup_attuale = os.path.join(cartella_destinazione_madre, f"Backup_Studio_{timestamp}")
    
    # Estensioni e file vitali da salvare obbligatoriamente
    estensioni_valide = ('.py', '.html', '.json', '.css', '.js', '.bat', '.db', '.md')
    cartelle_da_salvare = ['gui', 'templates', 'service', 'database', 'static']
    
    print(f" -> Origine dati: {cartella_progetto}")
    print(f" -> Destinazione sul tuo Desktop: {cartella_backup_attuale}")
    
    # Crea le cartelle di destinazione se non esistono
    if not os.path.exists(cartella_backup_attuale):
        os.makedirs(cartella_backup_attuale)

    file_salvati = 0
    cartelle_salvate = set()

    # 2. Scansione e copia selettiva (Esclude GPX pesanti e Font)
    for root, dirs, files in os.walk(cartella_progetto):
        # Ignora e salta completamente le cartelle pesanti di geodati, font e ambienti virtuali
        if 'gpx' in root or 'fonts' in root or 'venv' in root or '.git' in root or '__pycache__' in root:
            continue
            
        for file in files:
            if file.endswith(estensioni_valide):
                percorso_sorgente = os.path.join(root, file)
                
                # Calcola il percorso relativo per ricreare la stessa struttura ad albero
                percorso_relativo = os.path.relpath(percorso_sorgente, cartella_progetto)
                percorso_destinazione = os.path.join(cartella_backup_attuale, percorso_relativo)
                
                # Crea le sotto-cartelle necessarie (gui, service, templates...)
                os.makedirs(os.path.dirname(percorso_destinazione), exist_ok=True)
                
                # Copia fisica del file mantenendo le date originali
                shutil.copy2(percorso_sorgente, percorso_destinazione)
                file_salvati += 1
                
                # Traccia le cartelle strutturali salvate
                parti_percorso = percorso_relativo.split(os.sep)
                if len(parti_percorso) > 1:
                    cartelle_salvate.add(parti_percorso[0])

    print("\n=== STATUS REPORT BACKUP ===")
    print(f" ✅ Copia completata con successo sul tuo Desktop!")
    print(f" 📦 Totale file sorgente messi in sicurezza: {file_salvati}")
    print(f" 🗂️ Cartelle strutturali archiviate: {', '.join(cartelle_salvate) if cartelle_salvate else 'Nessuna (Solo radice)'}")
    print("============================================================\n")

if __name__ == "__main__":
    esegui_backup_progetto()
