"""Dialogo di modifica delle soglie del semaforo climatico.

Il modulo espone la classe :class:`ClimaSoglieDialog`, usata dalla pagina clima
per raccogliere i limiti di temperatura, pioggia e vento e la priorità del
fattore preferito. Il dialogo non conosce il database: si limita a validare e
restituire i valori, la persistenza resta responsabilità della finestra.
"""

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QMessageBox,
)


class ClimaSoglieDialog(QDialog):
    """Finestra modale per la configurazione delle soglie climatiche."""

    def __init__(self, soglie, parent=None):
        """Crea il dialogo popolando i campi con i valori delle `soglie`."""
        super().__init__(parent)
        self.setWindowTitle("Soglie del semaforo climatico")
        form = QFormLayout(self)
        etichette = {
            "temp_min_giallo": "Limite freddo giallo (°C)",
            "temp_min_verde": "Temperatura verde minima (°C)",
            "temp_max_verde": "Temperatura verde massima (°C)",
            "temp_max_giallo": "Limite caldo giallo (°C)",
            "pioggia_max_verde": "Pioggia verde fino a (mm/mese)",
            "pioggia_max_giallo": "Pioggia gialla fino a (mm/mese)",
            "vento_max_verde": "Vento verde fino a (km/h)",
            "vento_max_giallo": "Vento giallo fino a (km/h)",
        }
        self.campi = {}
        for chiave, etichetta in etichette.items():
            campo = QDoubleSpinBox()
            if chiave.startswith("temp_"):
                campo.setRange(-50, 70)
            elif chiave.startswith("pioggia_"):
                campo.setRange(0, 1000)
            else:
                campo.setRange(0, 300)
            campo.setDecimals(1)
            campo.setValue(float(soglie[chiave]))
            self.campi[chiave] = campo
            form.addRow(etichetta, campo)

        self.combo_priorita = QComboBox()
        self.combo_priorita.addItem("Caldo prioritario", 1)
        self.combo_priorita.addItem("Pioggia prioritaria", 0)
        indice_priorita = self.combo_priorita.findData(
            int(soglie.get("priorita_caldo", 1))
        )
        self.combo_priorita.setCurrentIndex(max(0, indice_priorita))
        form.addRow("Fattore preferito", self.combo_priorita)

        pulsanti = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        pulsanti.accepted.connect(self.accept)
        pulsanti.rejected.connect(self.reject)
        form.addRow(pulsanti)

    def accept(self):
        """Accetta il dialogo solo se le soglie sono in ordine crescente."""
        valori = self.valori()
        if (
            valori["temp_min_giallo"] >= valori["temp_min_verde"]
            or valori["temp_min_verde"] >= valori["temp_max_verde"]
            or valori["temp_max_verde"] >= valori["temp_max_giallo"]
            or valori["pioggia_max_verde"] >= valori["pioggia_max_giallo"]
            or valori["vento_max_verde"] >= valori["vento_max_giallo"]
        ):
            QMessageBox.warning(
                self,
                "Soglie non valide",
                "Le soglie devono essere in ordine crescente.",
            )
            return
        super().accept()

    def valori(self):
        """Restituisce il dizionario dei valori inseriti dall'utente."""
        valori = {
            chiave: campo.value() for chiave, campo in self.campi.items()
        }
        valori["priorita_caldo"] = int(self.combo_priorita.currentData())
        return valori