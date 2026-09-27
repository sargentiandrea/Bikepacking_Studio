import json
import os
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def genera_singolo_pdf(file_png, file_json, file_output, titolo_pdf):
    if not os.path.exists(file_png) or not os.path.exists(file_json):
        print(
            f"Salto: Impossibile trovare {file_png} o {file_json} in questa cartella."
        )
        return

    # Carica lo sprite sheet e i relativi dati JSON
    sprite_img = Image.open(file_png)
    with open(file_json, "r", encoding="utf-8") as f:
        sprite_data = json.load(f)

    # Crea una cartella temporanea per i ritagli
    os.makedirs("temp_icons", exist_ok=True)

    # Inizializza il PDF (Formato A4)
    c = canvas.Canvas(file_output, pagesize=A4)
    width, height = A4

    # Impostazioni di layout della pagina (3 Colonne ottimizzate)
    margine_x = 35
    margine_y = 40
    spazio_colonna = 185  # Larghezza colonna aumentata per fare spazio alle dimensioni
    altezza_riga = 32  # Spazio verticale per elemento

    x_iniziale = margine_x
    y_iniziale = height - margine_y - 25

    curr_x = x_iniziale
    curr_y = y_iniziale
    colonna_corrente = 0

    # Scrivi il titolo principale della prima pagina
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margine_x, height - 30, titolo_pdf)
    c.setLineWidth(0.5)
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.line(margine_x, height - 35, width - margine_x, height - 35)

    print(f"Generazione in corso: {file_output}...")

    for name, info in sprite_data.items():
        # Controllo cambio colonna / cambio pagina
        if curr_y < margine_y + 20:
            colonna_corrente += 1
            if colonna_corrente > 2:  # Crea una nuova pagina
                c.showPage()
                c.setFont("Helvetica-Bold", 10)
                c.drawString(
                    margine_x, height - 25, f"{titolo_pdf} (Continua)"
                )
                c.setStrokeColorRGB(0.5, 0.5, 0.5)
                c.line(margine_x, height - 28, width - margine_x, height - 28)
                colonna_corrente = 0
                curr_y = y_iniziale
                curr_x = x_iniziale
            else:
                # Muoviti alla colonna di destra
                curr_x = x_iniziale + (colonna_corrente * spazio_colonna)
                curr_y = y_iniziale

        # Estrai i dati geometrici dal JSON
        x, y = info["x"], info["y"]
        w_orig, h_orig = info["width"], info["height"]

        # Ritaglia l'icona dallo sprite di origine
        box = (x, y, x + w_orig, y + h_orig)
        icon_cropped = sprite_img.crop(box)

        # Ridimensiona l'anteprima solo se è troppo enorme per la griglia del PDF
        w_render, h_render = w_orig, h_orig
        max_size = 20
        if w_render > max_size or h_render > max_size:
            ratio = min(max_size / w_render, max_size / h_render)
            w_render = int(w_render * ratio)
            h_render = int(h_render * ratio)

        temp_icon_path = f"temp_icons/{name}.png"
        icon_cropped.save(temp_icon_path)

        # Calcola l'allineamento verticale dell'icona sulla riga
        offset_y_img = curr_y - (altezza_riga / 2) - (h_render / 2) + 5
        c.drawImage(
            temp_icon_path,
            curr_x,
            offset_y_img,
            width=w_render,
            height=h_render,
            mask="auto",
        )

        # Crea la stringa includendo la dimensione dell'immagine (w x h)
        testo_coordinate = f'[{w_orig}x{h_orig}px] x:{x}, y:{y} = "{name}"'
        c.setFont("Helvetica", 7.5)
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.drawString(curr_x + 24, curr_y - 12, testo_coordinate)

        # Disegna la linea tratteggiata di sfondo (griglia di separazione)
        c.setStrokeColorRGB(0.85, 0.85, 0.85)
        c.setLineWidth(0.3)
        c.line(curr_x, curr_y - 22, curr_x + spazio_colonna - 10, curr_y - 22)

        curr_y -= altezza_riga

    c.save()
    print(f"Catalogo salvato con successo: '{file_output}'")

    # Pulizia file temporanei
    for file in os.listdir("temp_icons"):
        os.remove(os.path.join("temp_icons", file))
    os.rmdir("temp_icons")


# --- FUNZIONE PRINCIPALE DI AVVIO ---
def compila_tutti_i_cataloghi(nome_base="sprite"):
    print("=== AVVIO GENERAZIONE CATALOGHI SPRITE ===")

    # 1. Elabora la versione Standard (1x)
    genera_singolo_pdf(
        file_png=f"{nome_base}.png",
        file_json=f"{nome_base}.json",
        file_output=f"Catalogo_{nome_base}_1x.pdf",
        titolo_pdf=f"Catalogo Sprite Standard (1x) - {nome_base}",
    )

    print("-" * 40)

    # 2. Elabora la versione Retina (2x)
    genera_singolo_pdf(
        file_png=f"{nome_base}@2x.png",
        file_json=f"{nome_base}@2x.json",
        file_output=f"Catalogo_{nome_base}_2x.pdf",
        titolo_pdf=f"Catalogo Sprite Alta Risoluzione (@2x) - {nome_base}",
    )

    print("\n=== PROCESSO COMPLETATO! ===")


# Avvia l'elaborazione globale
compila_tutti_i_cataloghi("sprite")
