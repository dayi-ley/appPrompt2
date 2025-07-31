from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from .new_character_dialog import NewCharacterDialog  # Importar la nueva ventana

class SaveOptionsDialog(QDialog):
    """Diálogo para seleccionar el tipo de guardado"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Guardar Configuración")
        self.setModal(True)
        self.setFixedSize(450, 200)  # Aumentar altura para que se vea todo
        self.selected_option = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(30, 30, 30, 20)
        
        # Título más visible
        title_label = QLabel("Guardar configuración actual")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #FFFFFF; margin-bottom: 5px;")
        layout.addWidget(title_label)
        
        # Descripción más grande y visible
        desc_label = QLabel("¿Deseas crear un nuevo personaje o guardar como\nvariación de un personaje existente?")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setFont(QFont("Segoe UI", 11))  # Aumentar tamaño de fuente
        desc_label.setStyleSheet("color: #FFFFFF; line-height: 1.5; margin-bottom: 10px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Espacio adicional
        layout.addSpacing(10)
        
        # Botones de opciones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Botón Nuevo Personaje
        self.new_character_btn = QPushButton("Nuevo Personaje")
        self.new_character_btn.setFixedSize(150, 40)
        self.new_character_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.new_character_btn.clicked.connect(self.select_new_character)
        buttons_layout.addWidget(self.new_character_btn)
        
        # Botón Variación
        self.variation_btn = QPushButton("Variación de un Personaje")
        self.variation_btn.setFixedSize(150, 40)
        self.variation_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        self.variation_btn.clicked.connect(self.select_variation)
        buttons_layout.addWidget(self.variation_btn)
        
        layout.addLayout(buttons_layout)
        
        # Espacio flexible para empujar el botón cancelar hacia abajo
        layout.addStretch()
        
        # Botón cancelar en la esquina inferior derecha
        cancel_layout = QHBoxLayout()
        cancel_layout.addStretch()  # Empuja el botón hacia la derecha
        
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setFixedSize(80, 30)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
                color: #333;
                border-color: #bbb;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        cancel_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(cancel_layout)
    
    def select_new_character(self):
        """Abre la ventana para crear nuevo personaje"""
        dialog = NewCharacterDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            character_name = dialog.get_character_name()
            if character_name:
                # Aquí se implementará la lógica de guardado
                QMessageBox.information(self, "Éxito", f"Personaje '{character_name}' creado exitosamente.")
                self.selected_option = "new_character"
                self.character_name = character_name  # Guardar el nombre para uso posterior
                self.accept()
    
    def select_variation(self):
        self.selected_option = "variation"
        self.accept()
    
    def get_selected_option(self):
        """Retorna la opción seleccionada"""
        return self.selected_option

class SaveManager:
    """Clase para manejar todas las funcionalidades de guardado"""
    
    def __init__(self, parent=None, category_grid=None):
        self.parent = parent
        self.category_grid = category_grid
    
    def show_save_options(self):
        """Muestra la ventana de opciones de guardado"""
        dialog = SaveOptionsDialog(self.parent, self.category_grid)
        dialog.exec()

class SaveOptionsDialog(QDialog):
    def __init__(self, parent=None, category_grid=None):
        super().__init__(parent)
        self.category_grid = category_grid
        self.setWindowTitle("Guardar Configuración")
        self.setModal(True)
        self.setFixedSize(450, 200)  # Aumentar altura para que se vea todo
        self.selected_option = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(30, 30, 30, 20)
        
        # Título más visible
        title_label = QLabel("Guardar configuración actual")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #FFFFFF; margin-bottom: 5px;")
        layout.addWidget(title_label)
        
        # Descripción más grande y visible
        desc_label = QLabel("¿Deseas crear un nuevo personaje o guardar como\nvariación de un personaje existente?")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setFont(QFont("Segoe UI", 11))  # Aumentar tamaño de fuente
        desc_label.setStyleSheet("color: #FFFFFF; line-height: 1.5; margin-bottom: 10px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Espacio adicional
        layout.addSpacing(10)
        
        # Botones de opciones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Botón Nuevo Personaje
        self.new_character_btn = QPushButton("Nuevo Personaje")
        self.new_character_btn.setFixedSize(150, 40)
        self.new_character_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.new_character_btn.clicked.connect(self.select_new_character)
        buttons_layout.addWidget(self.new_character_btn)
        
        # Botón Variación
        self.variation_btn = QPushButton("Variación de un personaje")
        self.variation_btn.setFixedSize(150, 40)
        self.variation_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        self.variation_btn.clicked.connect(self.select_variation)
        buttons_layout.addWidget(self.variation_btn)
        
        layout.addLayout(buttons_layout)
        
        # Espacio flexible para empujar el botón cancelar hacia abajo
        layout.addStretch()
        
        # Botón cancelar en la esquina inferior derecha
        cancel_layout = QHBoxLayout()
        cancel_layout.addStretch()  # Empuja el botón hacia la derecha
        
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setFixedSize(80, 30)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
                color: #333;
                border-color: #bbb;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        cancel_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(cancel_layout)
    
    def select_new_character(self):
        """Muestra el diálogo para crear nuevo personaje"""
        from .new_character_dialog import NewCharacterDialog
        dialog = NewCharacterDialog(self, self.category_grid)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            character_name = dialog.get_character_name()
            if character_name:
                self.selected_option = "new_character"
                self.character_name = character_name  # Guardar el nombre para uso posterior
                self.accept()  # Cerrar la ventana de opciones
        # Si el usuario cancela o cierra la ventana, no hacer nada
        # La ventana de opciones permanece abierta
        self.accept()
    
    def select_variation(self):
        self.selected_option = "variation"
        self.accept()
    
    def get_selected_option(self):
        """Retorna la opción seleccionada"""
        return self.selected_option