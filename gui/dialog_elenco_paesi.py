"""Dialogo modale con l'elenco dei paesi attraversati da un percorso.

Il modulo contiene la sola costruzione dell'interfaccia (tabella con
bandiera e nome del paese); il recupero dei dati resta al chiamante e la
ricerca delle bandiere è delegata a `service.sprite_bandiere_service`.
"""

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from service import sprite_bandiere_service

# Dimensione (px) delle bandiere mostrate nella tabella.
ICON_SIZE = 32


def crea_elenco_paesi(parent, lista_paesi, totale_paesi):
    """Costruisce e mostra il dialogo con l'elenco dei paesi attraversati.

    :param parent: finestra padre usata come parent del dialogo.
    :param lista_paesi: lista di tuple `(iso2, nome_fallback, display_name)`.
    :param totale_paesi: numero totale di paesi mostrato nel titolo.
    """
    finestra = QDialog(parent)
    finestra.setWindowTitle(f"Elenco Paesi Attraversati ({totale_paesi})")
    finestra.resize(480, 550)
    finestra.setStyleSheet("background-color: #1e1e1e; color: white;")
    layout_popup = QVBoxLayout(finestra)

    titolo = QLabel(f"<b>Totale Paesi Attraversati: {totale_paesi}</b>")
    titolo.setStyleSheet("font-size: 14pt; color: #4ec9b0; margin-bottom: 10px;")
    layout_popup.addWidget(titolo)

    sprite_data = sprite_bandiere_service.carica_dati_sprite()
    sprite_pixmap = sprite_bandiere_service.carica_pixmap_sprite()

    tabella = QTableWidget()
    tabella.setColumnCount(2)
    tabella.setHorizontalHeaderLabels(["Bandiera", "Paese"])
    tabella.horizontalHeader().setStretchLastSection(True)
    tabella.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    tabella.setRowCount(len(lista_paesi))
    tabella.verticalHeader().setDefaultSectionSize(ICON_SIZE + 14)
    tabella.setIconSize(QSize(ICON_SIZE, ICON_SIZE))

    for row_index, (iso2_code, nome_fallback, display_name) in enumerate(lista_paesi):
        trovato, nome_paese = sprite_bandiere_service.risolvi_paese_sprite(
            iso2_code, nome_fallback, sprite_data
        )

        item_bandiera = QTableWidgetItem()
        if sprite_pixmap and trovato:
            x, y = trovato.get("x", 0), trovato.get("y", 0)
            width, height = trovato.get("width", 48), trovato.get("height", 48)
            if width > 0 and height > 0:
                flag = sprite_pixmap.copy(x, y, width, height).scaled(
                    ICON_SIZE, ICON_SIZE, Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                item_bandiera.setIcon(QIcon(flag))
        if item_bandiera.icon().isNull():
            item_bandiera.setText(str(display_name).split(" ", 1)[0])
        item_bandiera.setTextAlignment(Qt.AlignCenter)
        tabella.setItem(row_index, 0, item_bandiera)
        tabella.setItem(row_index, 1, QTableWidgetItem(nome_paese))

    layout_popup.addWidget(tabella)
    btn_chiudi = QPushButton("Chiudi")
    btn_chiudi.clicked.connect(finestra.accept)
    layout_popup.addWidget(btn_chiudi)
    finestra.exec()