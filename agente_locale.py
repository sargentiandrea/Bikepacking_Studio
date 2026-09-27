import os
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELLO = "llama3"

def chiedi_all_agente(prompt_utente, contesto_file=""):
    """Invia una richiesta all'agente locale forzando l'italiano e passando il codice."""
    payload = {
        "model": MODELLO,
        "prompt": (
            "Sei un assistente esperto di programmazione Python, PySide6 e sviluppo di app desktop. "
            "Aiuti lo sviluppatore nel progetto Bikepacking Studio.\n"
            "REGOLA FONDAMENTALE: Rispondi SEMPRE e SOLO in lingua italiana, in modo tecnico, diretto e senza convenevoli inutili.\n\n"
            f"Contesto del codice:\n{contesto_file}\n\n"
            f"Richiesta dello sviluppatore: {prompt_utente}"
        ),
        "stream": False
    }
    
    try:
        print("\n🤖 L'agente sta leggendo e analizzando in locale...")
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        if response.status_code == 200:
            return response.json().get("response", "Nessuna risposta.")
        else:
            return f"Errore di connessione con Ollama: {response.status_code}"
    except Exception as e:
        return f"Impossibile contattare Ollama. Errore: {e}"

if __name__ == "__main__":
    print("==================================================")
    print("🚲 AGENTE LOCALE - Bikepacking Studio (Versione Corretta)")
    print("Incolla un percorso di file (es. C:\\...\\app_desktop.py) oppure fai una domanda.")
    print("Digita 'esci' per chiudere.")
    print("==================================================")
    
    while True:
        print("\n" + "-"*50)
        input_utente = input("Tu: ").strip()
        
        if input_utente.lower() in ["esci", "exit", "quit"]:
            print("Chiusura dell'agente. A presto!")
            break
            
        if not input_utente:
            continue
            
        # Pulisci il percorso da eventuali virgolette
        percorso_pulito = input_utente.strip('"').strip("'")
        
        contenuto_file = ""
        prompt_effettivo = input_utente
        
        # Se l'utente ha inserito un percorso di file valido, leggiamolo davvero!
        if os.path.exists(percorso_pulito) and os.path.isfile(percorso_pulito):
            print(f"[📂 Rilevato file locale, lo sto leggendo: {percorso_pulito}]")
            try:
                with open(percorso_pulito, "r", encoding="utf-8", errors="ignore") as f:
                    contenuto_file = f.read()[:8000] # Legge fino a 8000 caratteri del file
                prompt_effettivo = f"Analizza questo file del progetto ({os.path.basename(percorso_pulito)}), dimmi se vedi criticità, errori o punti da migliorare per risolvere problemi di rendering/stabilità."
            except Exception as e:
                contenuto_file = f"Errore di lettura file: {e}"
        
        risposta = chiedi_all_agente(prompt_effettivo, contenuto_file)
        print(f"\nAgente:\n{risposta}")