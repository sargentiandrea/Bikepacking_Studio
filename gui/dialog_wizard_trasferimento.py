"""Dialogo di registrazione del trasferimento logistico che copre un GAP.

Il modulo costruisce il form di raccolta dati (mezzo, vettore, luoghi,
durata, costo, note) mostrando le coordinate degli estremi delle tappe.
Restituisce i dati raccolti oppure `None` se l'utente annulla.
"""

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
)

# Mezzi di trasporto proposti dal wizard.
MEZZI = [
    "Traghetto / Nave",
    "Treno",
    "Bus / Pick-up",
    "Aereo",
    "Altro / Personale",
    "Bicicletta / Tratto Ciclabile",
]


def chiedi_dati_trasferimento(parent, nome_origine, nome_destinazione, coordinate):
    """Mostra il form del wizard e restituisce i dati inseriti.

    :param coordinate: tupla `(origine_lat, origine_lon, dest_lat, dest_lon)`.
    :return: dizionario con `mezzo`, `vettore`, `da`, `a`, `durata`, `costo`
        e `note`, oppure `None` se il dialogo viene annullato.
    """
    origine_lat, origine_lon, destinazione_lat, destinazione_lon = coordinate
    dialogo = QDialog(parent)
    dialogo.setWindowTitle("Registra trasferimento per il gap")
    dialogo.setMinimumWidth(480)
    form = QFormLayout(dialogo)

    form.addRow(
        QLabel(
            f"Collega '{nome_origine}' a '{nome_destinazione}'. "
            "Le coordinate sono prese dagli estremi delle tappe per "
            "rimuovere questo gap dall'audit."
        )
    )
    combo_mezzo = QComboBox()
    combo_mezzo.addItems(MEZZI)
    form.addRow("Mezzo", combo_mezzo)

    vettore = QLineEdit()
    vettore.setPlaceholderText("Compagnia, linea o operatore (facoltativo)")
    form.addRow("Vettore", vettore)
    campo_da = QLineEdit(nome_origine)
    campo_a = QLineEdit(nome_destinazione)
    form.addRow("Da", campo_da)
    form.addRow("A", campo_a)

    durata = QLineEdit()
    durata.setPlaceholderText("Es. 2 ore (facoltativo)")
    form.addRow("Durata", durata)
    costo = QDoubleSpinBox()
    costo.setRange(0, 10000000)
    costo.setDecimals(2)
    costo.setSuffix(" €")
    form.addRow("Costo", costo)

    note = QTextEdit()
    note.setPlaceholderText("Note facoltative")
    note.setMaximumHeight(80)
    form.addRow("Note", note)

    form.addRow(
        "Partenza gap",
        QLabel(f"{origine_lat:.6f}, {origine_lon:.6f}"),
    )
    form.addRow(
        "Arrivo gap",
        QLabel(f"{destinazione_lat:.6f}, {destinazione_lon:.6f}"),
    )
    pulsanti = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Save
        | QDialogButtonBox.StandardButton.Cancel
    )
    pulsanti.accepted.connect(dialogo.accept)
    pulsanti.rejected.connect(dialogo.reject)
    form.addRow(pulsanti)

    if dialogo.exec() != QDialog.DialogCode.Accepted:
        return None

    return {
        "mezzo": combo_mezzo.currentText(),
        "vettore": vettore.text().strip(),
        "da": campo_da.text().strip(),
        "a": campo_a.text().strip(),
        "durata": durata.text().strip(),
        "costo": costo.value(),
        "note": note.toPlainText().strip(),
    }