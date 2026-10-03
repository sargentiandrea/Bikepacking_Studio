"""Barra compatta che mostra la ripartizione delle superfici di un percorso.

Widget di sola grafica: riceve una lista di voci (categoria, percentuale,
colore) e le disegna come segmenti colorati. Non dipende da gui/mappa.py.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget


class BarraSuperfici(QWidget):
    """Barra compatta che visualizza la ripartizione delle superfici BRouter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.superfici = []
        self.setMinimumHeight(22)
        self.setMaximumHeight(22)

    def imposta_superfici(self, superfici):
        self.superfici = list(superfici or [])
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        area = self.rect().adjusted(0, 0, -1, -1)

        if not self.superfici:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#3e3e42"))
            painter.drawRoundedRect(area, 5, 5)
            return

        totale = sum(max(0.0, float(voce.get("percentuale", 0))) for voce in self.superfici)
        if totale <= 0:
            return

        x = area.left()
        larghezza_rimanente = area.width()
        for indice, voce in enumerate(self.superfici):
            quota = max(0.0, float(voce.get("percentuale", 0))) / totale
            larghezza = larghezza_rimanente if indice == len(self.superfici) - 1 else round(area.width() * quota)
            if larghezza <= 0:
                continue
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(voce.get("colore", "#64748b")))
            painter.drawRect(x, area.top(), larghezza, area.height())
            x += larghezza
            larghezza_rimanente -= larghezza
        painter.end()
