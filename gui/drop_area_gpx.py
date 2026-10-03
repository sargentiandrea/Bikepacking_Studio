"""Area di rilascio (drag & drop) per i file GPX.

Estratto da ``app_desktop.py`` durante la Fase 1.2 del refactor
(REPORT/PIANO_REFACTOR_APP_DESKTOP.md).

Oggi l'app carica i file GPX dal dialogo file (``apri_selettore_file``);
questo widget non è ancora istanziato da nessuna parte, ma è conservato
pronto all'uso qualora si voglia supportare il trascinamento dei file GPX
direttamente sulla finestra.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class DropAreaGPX(QFrame):
    files_dropped = Signal(list)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QFrame { border: 2px dashed #0e639c; border-radius: 10px; background-color: #2d2d30; }
            QFrame:hover { background-color: #3e3e42; border-color: #007acc; }
        """)
        layout = QVBoxLayout(self)
        self.label = QLabel("📥 Trascina qui i tuoi file GPX per questo percorso")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Arial", 11))
        self.label.setStyleSheet("color: #cccccc; border: none; background: transparent;")
        layout.addWidget(self.label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        filepaths = [u.toLocalFile() for u in urls if u.toLocalFile().lower().endswith('.gpx')]
        if filepaths:
            self.files_dropped.emit(filepaths)
