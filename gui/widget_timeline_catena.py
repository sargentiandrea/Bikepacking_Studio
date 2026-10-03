"""Widget della timeline della catena stagionale.

Estratto dalla Fase 2 del refactor di ``app_desktop.py``
(vedi REPORT/PIANO_REFACTOR_APP_DESKTOP.md).

Disegna una timeline compatta delle date previste per i blocchi del viaggio:
una barra colorata (colore del semaforo climatico) per ogni blocco e per
ogni passaggio di paese.
"""

from datetime import datetime

from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class TimelineCatenaWidget(QWidget):
    """Disegna una timeline compatta delle date previste per i blocchi."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._righe = []
        self._altezza_riga = 26
        self.setMinimumWidth(520)
        self.setMinimumHeight(70)
        self.setStyleSheet("background-color: #252526;")

    def imposta_righe(self, righe):
        self._righe = [
            paese
            for blocco in righe
            for paese in blocco.get("paesi", [])
        ]
        self.setMinimumHeight(44 + max(1, len(self._righe)) * self._altezza_riga)
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(_event.rect(), QColor("#252526"))

        if not self._righe:
            painter.setPen(QColor("#aaaaaa"))
            painter.drawText(12, 30, "La timeline apparirà dopo il calcolo della catena.")
            return

        date_ingressi = [
            datetime.strptime(riga["data_ingresso"], "%Y-%m-%d").date()
            for riga in self._righe
        ]
        date_uscite = [
            datetime.strptime(riga["data_uscita"], "%Y-%m-%d").date()
            for riga in self._righe
        ]
        data_iniziale = min(date_ingressi)
        data_finale = max(date_uscite)
        intervallo_giorni = max(1, (data_finale - data_iniziale).days + 1)

        margine_sinistro = 205
        margine_destro = 12
        larghezza_traccia = max(1, self.width() - margine_sinistro - margine_destro)
        painter.setPen(QPen(QColor("#aaaaaa")))
        painter.drawText(margine_sinistro, 18, data_iniziale.strftime("%d/%m/%Y"))
        painter.drawText(
            self.width() - margine_destro - 82,
            18,
            data_finale.strftime("%d/%m/%Y"),
        )

        for indice, riga in enumerate(self._righe):
            y = 28 + indice * self._altezza_riga
            data_riga = datetime.strptime(
                riga["data_ingresso"], "%Y-%m-%d"
            ).date()
            offset_giorni = (data_riga - data_iniziale).days
            durata = max(0, int(riga["giorni_totali"]))
            x = margine_sinistro + round(
                offset_giorni / intervallo_giorni * larghezza_traccia
            )
            larghezza = max(
                4,
                round(durata / intervallo_giorni * larghezza_traccia),
            )

            nome = (
                f"{riga.get('codice_paese', '')} "
                f"{riga.get('nome_paese', 'Paese non assegnato')} "
                f"({durata} gg)"
            ).strip()
            painter.setPen(QColor("#eeeeee"))
            painter.drawText(8, y + 16, nome[:28])
            painter.setBrush(QColor(riga.get("semaforo_colore", "#0e639c")))
            painter.drawRoundedRect(x, y + 5, larghezza, 14, 4, 4)
