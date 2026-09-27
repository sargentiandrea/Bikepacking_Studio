from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QLineEdit, QPushButton, QGroupBox, QFormLayout
)
from PySide6.QtGui import QFont

class WizardNuovoPercorso(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pianificatore Nuovo Percorso - Bikepacking Studio")
        self.setMinimumWidth(500)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        
        self.risultato_dati = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Titolo del Wizard
        lbl_titolo = QLabel("✨ Crea Nuovo Itinerario Interattivo")
        lbl_titolo.setFont(QFont("Arial", 14, QFont.Bold))
        lbl_titolo.setStyleSheet("color: #28a745; margin-bottom: 10px;")
        layout.addWidget(lbl_titolo)

        # Form dei parametri
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft if 'Qt' in globals() else 0)

        # 1. Nome del percorso
        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Es. Avventura in Gravel sui Monti")
        self.input_nome.setStyleSheet("background-color: #2d2d30; color: white; padding: 8px; border: 1px solid #3e3e42; border-radius: 4px;")
        form_layout.addRow(QLabel("<b>Nome Percorso:</b>"), self.input_nome)

        # 2. Profilo di Mobilità / Bici
        self.combo_bici = QComboBox()
        self.combo_bici.addItems([
            "Gravel / Bici da Viaggio", 
            "Bici da Strada (Asfalto)", 
            "Mountain Bike (Sterrato / Trail)", 
            "E-Bike Tourer"
        ])
        self.combo_bici.setStyleSheet("background-color: #2d2d30; color: white; padding: 8px; border: 1px solid #3e3e42; border-radius: 4px;")
        form_layout.addRow(QLabel("<b>Profilo Bici:</b>"), self.combo_bici)

        # 3. Preferenze di Strada
        self.combo_strada = QComboBox()
        self.combo_strada.addItems([
            "Bilanciato (Consigliato)", 
            "Evita traffico pesante", 
            "Preferisci strade sterrate / ciclabili", 
            "Massima velocità (Asfalto prioritario)"
        ])
        self.combo_strada.setStyleSheet("background-color: #2d2d30; color: white; padding: 8px; border: 1px solid #3e3e42; border-radius: 4px;")
        form_layout.addRow(QLabel("<b>Preferenza Strade:</b>"), self.combo_strada)

        # 4. Durata / Tipologia Temporale
        self.combo_durata = QComboBox()
        self.combo_durata.addItems([
            "Escursione in Giornata", 
            "Weekend (2-3 giorni)", 
            "Viaggio a tappe (Bikepacking Lunga Durata)"
        ])
        self.combo_durata.setStyleSheet("background-color: #2d2d30; color: white; padding: 8px; border: 1px solid #3e3e42; border-radius: 4px;")
        form_layout.addRow(QLabel("<b>Durata Prevista:</b>"), self.combo_durata)

        layout.addLayout(form_layout)
        layout.addSpacing(20)

        # Pulsanti di azione (Conferma / Annulla)
        btn_layout = QHBoxLayout()
        btn_Annulla = QPushButton("Annulla")
        btn_Annulla.setStyleSheet("background-color: #3e3e42; color: white; padding: 10px 15px; border-radius: 5px; font-weight: bold;")
        btn_Annulla.clicked.connect(self.reject)

        btn_Crea = QPushButton("🚀 Apri sulla Mappa e Procedi")
        btn_Crea.setStyleSheet("background-color: #28a745; color: white; padding: 10px 15px; border-radius: 5px; font-weight: bold;")
        btn_Crea.clicked.connect(self.conferma_creazione)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_Annulla)
        btn_layout.addWidget(btn_Crea)

        layout.addLayout(btn_layout)

    def conferma_creazione(self):
        # Raccogliamo i dati inseriti dall'utente
        self.risultato_dati = {
            "nome": self.input_nome.text().strip() or "Nuovo Percorso Senza Nome",
            "profilo_bici": self.combo_bici.currentText(),
            "preferenza_strada": self.combo_strada.currentText(),
            "durata": self.combo_durata.currentText()
        }
        self.accept()