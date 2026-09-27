import os

def analizza_progetto():
    print("Avvio scansione del progetto Bikepacking_Studio...")
    report = []
    report.append("# 🗺️ REPORT BIKEPACKING STUDIO - MAPPA DELLA VERITÀ\n")
    
    # Cartelle da verificare
    cartelle_target = ['gui', 'service', 'templates']
    
    # Controlla se siamo nella cartella giusta
    trovata = False
    for c in cartelle_target:
        if os.path.exists(c):
            trovata = True
            
    if not trovata:
        report.append("❌ ERRORE: Sposta questo script nella cartella principale (Bikepacking_Studio).\n")
        print("Errore: Cartelle non trovate. Verifica la posizione del file.")
        with open("REPORT_ARCHITETTURA.md", "w", encoding="utf-8") as f:
            f.write("\n".join(report))
        return

    # Scansione file
    for root, dirs, files in os.walk('.'):
        # Escludi cartelle di sistema o ambienti virtuali
        if any(p.startswith('.') or p in ['venv', '__pycache__', 'env', 'temp_svg_1x', 'temp_svg_2x'] for p in root.split(os.sep)):
            continue
            
        for file in files:
            if file.endswith(('.py', '.html', '.json')) and file != 'analizzatore_progetto.py':
                strada_file = os.path.join(root, file)
                print(f"Esamino: {strada_file}")
                report.append(f"## 📄 File: {strada_file}\n")
                
                try:
                    with open(strada_file, 'r', encoding='utf-8', errors='ignore') as f:
                        righe = f.readlines()
                    
                    funzioni = []
                    classi = []
                    connessioni = []
                    
                    for riga in righe:
                        riga_pulita = riga.strip()
                        
                        # Trova le funzioni Python
                        if riga_pulita.startswith("def "):
                            nome_fun = riga_pulita.split("def ")[1].split("(")[0].strip()
                            funzioni.append(nome_fun)
                            
                        # Trova le classi Python
                        if riga_pulita.startswith("class "):
                            nome_cls = riga_pulita.split("class ")[1].split("(")[0].split(":")[0].strip()
                            classi.append(nome_cls)
                            
                        # Trova riferimenti a porte o server locali
                        if "127.0.0.1:" in riga_pulita or "localhost:" in riga_pulita:
                            connessioni.append(riga_pulita)
                    
                    # Aggiunge i dati al report se trovati
                    if classi:
                        report.append("**Classi individuate:**")
                        for c in classi:
                            report.append(f"- `class {c}`")
                    
                    if funzioni:
                        report.append("**Funzioni individuate:**")
                        for f in funzioni:
                            report.append(f"- `def {f}()`")
                            
                    if connessioni:
                        report.append("**Riferimenti di rete / Porte:**")
                        for conn in set(connessioni[:5]):  # Limita a 5 righe per non intasare
                            report.append(f"- Cerca di connettersi: `{conn[:80]}`")
                            
                    report.append("\n" + "-"*40 + "\n")
                    
                except Exception as e:
                    report.append(f"❌ Impossibile leggere il file: {e}\n")

    # Scrittura finale del file markdown
    with open("REPORT_ARCHITETTURA.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    
    print("\n✅ REPORT_ARCHITETTURA.md generato con successo nella cartella del progetto!")

if __name__ == "__main__":
    analizza_progetto()
