from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os
import json
import re
from datetime import datetime

class NewCharacterDialog(QDialog):
    """Diálogo para crear un nuevo personaje"""
    
    def __init__(self, parent=None, category_grid=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Personaje")
        self.setModal(True)
        self.setFixedSize(400, 220)
        self.character_name = None
        self.category_grid = category_grid  # Referencia al grid de categorías
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
        """)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 25)
        
        # Título
        title_label = QLabel("Crear Nuevo Personaje")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: white;")
        layout.addWidget(title_label)
        
        # Instrucción
        instruction_label = QLabel("Ingresa un nombre para tu personaje:")
        instruction_label.setFont(QFont("Segoe UI", 11))
        instruction_label.setStyleSheet("color: white; margin-bottom: px;")
        layout.addWidget(instruction_label)
        
        # Campo de texto
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ejemplo: Aria, Kobayashi, etc.")
        self.name_input.setFont(QFont("Segoe UI", 11))
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 2px solid #555;
                border-radius: 6px;
                font-size: 11px;
                background-color: #404040;
                color: white;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
                outline: none;
            }
            QLineEdit::placeholder {
                color: #aaa;
            }
        """)
        self.name_input.returnPressed.connect(self.save_character)
        layout.addWidget(self.name_input)
        
        # Espacio flexible
        layout.addStretch()
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Botón Cancelar
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setFixedSize(100, 35)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #555;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QPushButton:pressed {
                background-color: #444;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        
        # Botón Guardar Personaje
        self.save_btn = QPushButton("Guardar Personaje")
        self.save_btn.setFixedSize(140, 35)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #666;
                color: #aaa;
            }
        """)
        self.save_btn.clicked.connect(self.save_character)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_btn)
        
        layout.addLayout(buttons_layout)
        
        # Enfocar el campo de texto al abrir
        self.name_input.setFocus()
    
    def save_character(self):
        """Valida y guarda el nuevo personaje"""
        name = self.name_input.text().strip()
        
        # Validaciones existentes
        if not name:
            QMessageBox.warning(self, "Error", "Por favor ingresa un nombre para el personaje.")
            self.name_input.setFocus()
            return
        
        if not re.match(r'^[a-zA-Z0-9\s_-]+$', name):
            QMessageBox.warning(self, "Error", "El nombre solo puede contener letras, números, espacios, guiones y guiones bajos.")
            self.name_input.setFocus()
            return
        
        if self.character_exists(name):
            QMessageBox.warning(self, "Error", f"Ya existe un personaje con el nombre '{name}'.\nPor favor elige otro nombre.")
            self.name_input.setFocus()
            return
        
        # Guardar el personaje
        try:
            self.save_character_data(name)
            QMessageBox.information(self, "Éxito", f"Personaje '{name}' guardado exitosamente.")
            self.character_name = name
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar el personaje: {str(e)}")
    
    def save_character_data(self, name):
        """Guarda los datos del personaje en el archivo JSON"""
        # Crear directorio de personajes si no existe
        characters_dir = os.path.join("data", "characters")
        os.makedirs(characters_dir, exist_ok=True)
        
        # Normalizar nombre para el archivo
        normalized_name = name.lower().replace(" ", "_")
        character_folder = os.path.join(characters_dir, normalized_name)
        
        # Crear carpeta del personaje
        os.makedirs(character_folder, exist_ok=True)
        
        # Obtener valores actuales de las categorías
        if self.category_grid:
            current_values = self.category_grid.get_current_values()
            
            # Convertir nombres de categorías al formato snake_case
            category_data = {}
            for display_name, value in current_values.items():
                # Convertir "Cabello forma" -> "cabello_forma"
                snake_case_name = display_name.lower().replace(" ", "_")
                category_data[snake_case_name] = value
        else:
            category_data = {}
        
        # Crear estructura de datos con metadatos
        character_data = {
            "metadata": {
                "character_name": name,
                "display_name": name,
                "created_date": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "version": "1.0",
                "type": "character",
                "description": f"Personaje {name} creado desde la aplicación"
            },
            "categories": category_data
        }
        
        # Guardar archivo JSON en la carpeta del personaje
        json_file_path = os.path.join(character_folder, f"{normalized_name}.json")
        
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(character_data, f, ensure_ascii=False, indent=2)
        
        print(f"Personaje guardado en: {json_file_path}")
    
    def character_exists(self, name):
        """Verifica si ya existe un personaje con ese nombre"""
        characters_dir = os.path.join("data", "characters")
        if not os.path.exists(characters_dir):
            return False
        
        # Normalizar nombre para comparación
        normalized_name = name.lower().replace(" ", "_")
        character_folder = os.path.join(characters_dir, normalized_name)
        
        return os.path.exists(character_folder)
    
    def get_character_name(self):
        """Retorna el nombre del personaje ingresado"""
        return self.character_name