"""Dialogo di creazione di un nuovo percorso (Pianificatore Itinerario).

Il dialogo raccoglie nome, profilo bici, preferenza strade, durata e note.
La persistenza è delegata a `service.progetti_service`; al salvataggio
avviene tramite la callback `on_creato` ricevuta in costruzione.
"""

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QLineEdit,
    QPushButton,
)

from service import progetti_service

# Opzioni proposte nei menu a tendina del pianificatore.
PROFILI_BICI = [
    "Gravel / Bici da Viaggio",
    "Bici da Strada (Asfalto)",
    "Mountain Bike (Sterrato / Trail)",
    "E-Bike Tourer",
]
PREFERENZE_STRADE = [
    "Bilanciato (Consigliato)",
    "Evita traffico pesante",
    "Preferisci strade sterrate / ciclabili",
    "Massima velocità (Asfalto prioritario)",
]
DURATE_PREVISTE = [
    "Escursione in Giornata",
    "Weekend (2-3 giorni)",
    "Viaggio a tappe (Bikepacking Lunga Durata)",
]

_STILE_CAMPO = "background-color: #3e3e42; padding: 6px; color: white; border: 1px solid #555;"


def crea_nuovo_progetto_dialog(parent, on_creato):
    """Mostra il dialogo di creazione percorso e invoca `on_creato`.

    :param parent: finestra padre del dialogo.
    :param on_creato: callback ``(nuovo_id, nome, profilo, preferenze)`` chiamata
        dopo la creazione del percorso nel database.
    """
    dialog = QDialog(parent)
    dialog.setWindowTitle("✨ Pianificatore Nuovo Itinerario Interattivo")
    dialog.setFixedWidth(450)
    dialog.setStyleSheet("background-color: #2d2d30; color: white;")
    layout = QFormLayout(dialog)
    layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

    txt_nome = QLineEdit()
    txt_nome.setPlaceholderText("Es. Avventura Gravel sui Monti")
    txt_nome.setStyleSheet(_STILE_CAMPO)

    combo_bici = QComboBox()
    combo_bici.addItems(PROFILI_BICI)
    combo_bici.setStyleSheet(_STILE_CAMPO)

    combo_strada = QComboBox()
    combo_strada.addItems(PREFERENZE_STRADE)
    combo_strada.setStyleSheet(_STILE_CAMPO)

    combo_durata = QComboBox()
    combo_durata.addItems(DURATE_PREVISTE)
    combo_durata.setStyleSheet(_STILE_CAMPO)

    txt_desc = QLineEdit()
    txt_desc.setPlaceholderText("Note opzionali...")
    txt_desc.setStyleSheet(_STILE_CAMPO)

    layout.addRow("<b>Nome Percorso:</b>", txt_nome)
    layout.addRow("<b>Profilo Bici:</b>", combo_bici)
    layout.addRow("<b>Preferenza Strade:</b>", combo_strada)
    layout.addRow("<b>Durata Prevista:</b>", combo_durata)
    layout.addRow("<b>Note / Descrizione:</b>", txt_desc)

    btn_salva = QPushButton("🚀 Crea e Apri sulla Mappa")
    btn_salva.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold; border-radius: 4px; margin-top: 10px;")

    def salva():
        """Crea il percorso con i dati raccolti e notifica il chiamante."""
        nome = txt_nome.text().strip()
        if not nome:
            return
        nuovo_id = progetti_service.crea_progetto(nome, txt_desc.text().strip())
        dialog.accept()
        print(
            f"✨ Creato percorso '{nome}' | Bici: {combo_bici.currentText()} | "
            f"Strade: {combo_strada.currentText()}"
        )
        on_creato(nuovo_id, nome)

    btn_salva.clicked.connect(salva)
    layout.addRow(btn_salva)
    dialog.exec()