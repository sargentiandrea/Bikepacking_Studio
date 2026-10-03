"""Widget grafico per barra superfici, legenda, stato e KPI della rotta."""

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout

from gui.mappa_barra_superfici import BarraSuperfici
from service.dettagli_rotta_service import (
    prepara_kpi_rotta,
    testo_distanza_tappe,
    testo_stato_superfici_offline,
    testo_stato_superfici_rotta,
    testi_altimetria,
    testo_voce_legenda,
)


class PannelloDettagliRotta(QFrame):
    """Raggruppa la presentazione grafica dei dettagli tecnici della rotta."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        lbl_superfici = QLabel("Superfici del percorso")
        lbl_superfici.setStyleSheet(
            "color: #cbd5e1; font-size: 12px; font-weight: 600; "
            "margin-top: 4px; border: none;"
        )
        layout.addWidget(lbl_superfici)

        self.barra_superfici = BarraSuperfici()
        layout.addWidget(self.barra_superfici)

        self.layout_leggenda_superfici = QGridLayout()
        self.layout_leggenda_superfici.setContentsMargins(0, 4, 0, 0)
        self.layout_leggenda_superfici.setHorizontalSpacing(12)
        self.layout_leggenda_superfici.setVerticalSpacing(3)
        layout.addLayout(self.layout_leggenda_superfici)

        self.lbl_stato = QLabel("La ripartizione compare dopo il calcolo della rotta.")
        self.lbl_stato.setWordWrap(True)
        self.lbl_stato.setStyleSheet(
            "font-size: 11px; color: #cbd5e1; line-height: 1.4;"
        )
        layout.addWidget(self.lbl_stato)

        lbl_dettagli = QLabel("Dettagli tecnici")
        lbl_dettagli.setStyleSheet(
            "color: #cbd5e1; font-size: 12px; font-weight: 600; "
            "margin-top: 4px; border: none;"
        )
        layout.addWidget(lbl_dettagli)

        layout_kpi = QVBoxLayout()
        layout_kpi.setContentsMargins(0, 0, 0, 0)
        layout_kpi.setSpacing(5)
        stile_kpi = (
            "font-size: 12px; color: #f1f5f9; font-weight: 500; border: none;"
        )
        self.lbl_velocita_media = QLabel("Velocità media stimata: --")
        self.lbl_altitudine_massima = QLabel("Altitudine massima: --")
        self.lbl_altitudine_minima = QLabel("Altitudine minima: --")
        self.lbl_distanza_totale = QLabel("Distanza totale: --")
        for etichetta in (
            self.lbl_velocita_media,
            self.lbl_altitudine_massima,
            self.lbl_altitudine_minima,
            self.lbl_distanza_totale,
        ):
            etichetta.setStyleSheet(stile_kpi)
            etichetta.setWordWrap(True)
            layout_kpi.addWidget(etichetta)
        layout.addLayout(layout_kpi)

    def imposta_stato(self, testo):
        """Aggiorna il messaggio di stato mostrato sotto la legenda."""
        self.lbl_stato.setText(testo)

    def imposta_distanza_tappe(self, tappe):
        """Mostra la somma delle distanze delle tappe già caricate."""
        self.lbl_distanza_totale.setText(testo_distanza_tappe(tappe))

    def imposta_altimetria(self, massima, minima):
        """Aggiorna le quote che il worker di altimetria è riuscito a calcolare."""
        testo_massima, testo_minima = testi_altimetria(massima, minima)
        if testo_massima is not None:
            self.lbl_altitudine_massima.setText(testo_massima)
        if testo_minima is not None:
            self.lbl_altitudine_minima.setText(testo_minima)

    def imposta_superfici(self, superfici):
        """Aggiorna barra e legenda con la distribuzione ricevuta."""
        self.barra_superfici.imposta_superfici(superfici)
        self._popola_legenda(superfici)

    def imposta_kpi(self, testi):
        """Applica ai quattro widget i testi KPI già formattati dal servizio."""
        self.lbl_velocita_media.setText(testi["velocita"])
        self.lbl_altitudine_massima.setText(testi["altitudine_massima"])
        self.lbl_altitudine_minima.setText(testi["altitudine_minima"])
        self.lbl_distanza_totale.setText(testi["distanza"])

    def imposta_dettagli_rotta(self, statistiche):
        """Mostra superfici, messaggio e KPI restituiti dal worker di routing."""
        statistiche = statistiche or {}
        superfici = statistiche.get("superfici", [])
        self.imposta_superfici(superfici)
        self.imposta_stato(testo_stato_superfici_rotta(superfici))
        self.imposta_kpi(prepara_kpi_rotta(statistiche))

    def imposta_superfici_offline(self, risultato):
        """Mostra superfici offline e relativo stato; restituisce se l'analisi è disponibile."""
        disponibile = bool(risultato and risultato.get("disponibile"))
        self.imposta_stato(testo_stato_superfici_offline(risultato))
        if disponibile:
            self.imposta_superfici(risultato.get("superfici", []))
        return disponibile

    def reset(self):
        """Ripristina stato, barra, legenda e KPI ai valori iniziali."""
        self.imposta_superfici([])
        self.imposta_stato("La ripartizione compare dopo il calcolo della rotta.")
        self.imposta_kpi(prepara_kpi_rotta({}))

    def _popola_legenda(self, superfici):
        """Ricostruisce la legenda a due colonne mantenendo lo stile attuale."""
        while self.layout_leggenda_superfici.count():
            elemento = self.layout_leggenda_superfici.takeAt(0)
            if elemento.widget():
                elemento.widget().deleteLater()

        colonne = 2
        for indice, superficie in enumerate(superfici or []):
            legenda = QLabel(testo_voce_legenda(superficie))
            legenda.setStyleSheet(
                f"font-size: 11px; color: {superficie['colore']}; font-weight: 600;"
            )
            legenda.setWordWrap(True)
            self.layout_leggenda_superfici.addWidget(
                legenda, indice // colonne, indice % colonne
            )
