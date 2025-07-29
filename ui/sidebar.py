from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
import os
import json

class SidebarFrame(QFrame):
    character_defaults_selected = pyqtSignal(dict)
    
    def __init__(self, prompt_generator):
        super().__init__()
        self.prompt_generator = prompt_generator
        self.is_collapsed = False
        self.expanded_width = 240
        self.collapsed_width = 60
        
        self.setup_ui()
        self.setup_styles()
        self.setup_data()

    def setup_ui(self):
        """Configura la interfaz del sidebar"""
        self.setFixedWidth(self.expanded_width)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header con botón de colapsar
        header_layout = QHBoxLayout()
        
        self.header_label = QLabel("AI Prompt Studio")
        self.header_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header_layout.addWidget(self.header_label)
        
        self.toggle_button = QPushButton("◀")
        self.toggle_button.setFixedSize(30, 25)
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        header_layout.addWidget(self.toggle_button)
        
        layout.addLayout(header_layout)
        
        # Subtítulo
        self.subtitle_label = QLabel("Generador de Prompts IA")
        self.subtitle_label.setFont(QFont("Segoe UI", 10))
        self.subtitle_label.setStyleSheet("color: #a0a0a0;")
        layout.addWidget(self.subtitle_label)
        
        # Contenedor para el contenido
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        
        # Selector de personaje
        self.character_label = QLabel("Personaje")
        self.character_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        content_layout.addWidget(self.character_label)
        
        self.character_dropdown = QComboBox()
        self.character_dropdown.addItems([
            "Seleccionar personaje...",
            "kobayashi",           # <-- Agrega aquí tu personaje real
            "Personaje 1",
            "Personaje 2",
            "Personaje 3"
        ])
        self.character_dropdown.currentTextChanged.connect(self.on_character_change)
        content_layout.addWidget(self.character_dropdown)
        
        # Descripción del personaje
        self.character_desc = QLabel("Selecciona un personaje para ver su descripción")
        self.character_desc.setFont(QFont("Segoe UI", 9))
        self.character_desc.setStyleSheet("color: #a0a0a0;")
        self.character_desc.setWordWrap(True)
        content_layout.addWidget(self.character_desc)
        
        # Selector de escena
        self.scene_label = QLabel("Escena")
        self.scene_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        content_layout.addWidget(self.scene_label)
        
        self.scene_dropdown = QComboBox()
        self.scene_dropdown.addItems(["Seleccionar escena...", "Escena 1", "Escena 2", "Escena 3"])
        self.scene_dropdown.currentTextChanged.connect(self.on_scene_change)
        content_layout.addWidget(self.scene_dropdown)
        
        # Descripción de la escena
        self.scene_desc = QLabel("Selecciona una escena para ver su configuración")
        self.scene_desc.setFont(QFont("Segoe UI", 9))
        self.scene_desc.setStyleSheet("color: #a0a0a0;")
        self.scene_desc.setWordWrap(True)
        content_layout.addWidget(self.scene_desc)
        
        # Botón para gestionar personajes
        self.edit_character_btn = QPushButton("Gestionar personajes")
        self.edit_character_btn.setFixedHeight(32)
        content_layout.addWidget(self.edit_character_btn)
        
        # Botón para guardar el personaje actual
        self.save_character_btn = QPushButton("Guardar personaje actual")
        self.save_character_btn.setFixedHeight(32)
        self.save_character_btn.clicked.connect(self.save_current_character)
        content_layout.addWidget(self.save_character_btn)
        
        # Espaciador
        content_layout.addStretch()
        
        layout.addWidget(self.content_widget)

    def setup_styles(self):
        """Configura los estilos del sidebar"""
        self.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border: 1px solid #404040;
                border-radius: 8px;
            }
            QLabel {
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
            QComboBox {
                background-color: #1a1a1a;
                border: 1px solid #404040;
                border-radius: 6px;
                color: #e0e0e0;
                padding: 6px;
                font-size: 11px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #e0e0e0;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                border: 1px solid #404040;
                color: #e0e0e0;
                selection-background-color: #6366f1;
            }
        """)

    def setup_data(self):
        """Configura los datos dummy"""
        self.characters_data = {
            "Personaje 1": "Protagonista principal con cabello rubio y ojos azules. Personalidad amigable y extrovertida.",
            "Personaje 2": "Antagonista misterioso con cabello negro y ojos verdes. Personalidad reservada y calculadora.",
            "Personaje 3": "Personaje secundario con cabello castaño y ojos marrones. Personalidad leal y protectora."
        }
        
        self.scenes_data = {
            "Escena 1": "Escena de día en un bosque mágico con iluminación suave y atmósfera pacífica.",
            "Escena 2": "Escena nocturna en una ciudad futurista con luces neón y atmósfera cyberpunk.",
            "Escena 3": "Escena de atardecer en una playa tropical con iluminación cálida y atmósfera romántica."
        }

    def toggle_sidebar(self):
        """Alterna entre sidebar colapsado y expandido"""
        if self.is_collapsed:
            self.expand_sidebar()
        else:
            self.collapse_sidebar()

    def collapse_sidebar(self):
        """Colapsa el sidebar"""
        self.is_collapsed = True
        self.setFixedWidth(self.collapsed_width)
        self.toggle_button.setText("▶")
        
        # Hacer el botón más alto para facilitar el clic
        self.toggle_button.setFixedSize(40, 120)  # Más alto cuando está colapsado
        
        # Ocultar todo el contenido
        self.content_widget.hide()
        self.subtitle_label.hide()
        self.header_label.hide()  # Ocultar completamente el título
        
        # Solo mostrar el botón de toggle
        self.toggle_button.show()

    def expand_sidebar(self):
        """Expande el sidebar"""
        self.is_collapsed = False
        self.setFixedWidth(self.expanded_width)
        self.toggle_button.setText("◀")
        
        # Restaurar el tamaño normal del botón
        self.toggle_button.setFixedSize(30, 25)  # Tamaño normal cuando está expandido
        
        # Mostrar todo el contenido
        self.header_label.setText("AI Prompt Studio")
        self.header_label.show()
        self.subtitle_label.show()
        self.content_widget.show()

    def on_character_change(self, choice):
        """Maneja el cambio de personaje"""
        if not choice or choice == "Seleccionar personaje...":
            self.character_desc.setText("Selecciona un personaje para ver su descripción")
            return
            
        # Normalizar el nombre del personaje para el archivo
        char_filename = choice.lower().replace(" ", "_") + ".json"
        char_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "characters", char_filename)
        
        # Verificar si existe el archivo del personaje
        if os.path.exists(char_path):
            # Cargar los valores existentes
            with open(char_path, "r", encoding="utf-8") as f:
                character_defaults = json.load(f)
            self.character_defaults_selected.emit(character_defaults)
            self.character_desc.setText(f"Personaje cargado: {choice}")
        else:
            # Si no existe, crear un nuevo archivo con los valores actuales
            if choice.lower() not in ["seleccionar personaje...", "personaje 1", "personaje 2", "personaje 3"]:
                # Obtener los valores actuales de las categorías
                current_values = self.prompt_generator.get_active_categories()
                
                # Guardar en un nuevo archivo JSON
                os.makedirs(os.path.dirname(char_path), exist_ok=True)
                with open(char_path, "w", encoding="utf-8") as f:
                    json.dump(current_values, f, ensure_ascii=False, indent=2)
                
                self.character_desc.setText(f"Nuevo personaje creado: {choice}")
                # No emitimos la señal porque ya tenemos los valores cargados
            elif choice in self.characters_data:
                self.character_desc.setText(self.characters_data[choice])
            else:
                self.character_desc.setText("Selecciona un personaje para ver su descripción")

    def on_scene_change(self, choice):
        """Maneja el cambio de escena"""
        if choice in self.scenes_data:
            self.scene_desc.setText(self.scenes_data[choice])
        else:
            self.scene_desc.setText("Selecciona una escena para ver su configuración")

    def save_current_character(self):
        """Guarda los valores actuales como un nuevo personaje o actualiza uno existente"""
        current_character = self.character_dropdown.currentText()
        
        if current_character == "Seleccionar personaje...":
            # Pedir al usuario que ingrese un nombre para el nuevo personaje
            from PyQt6.QtWidgets import QInputDialog
            name, ok = QInputDialog.getText(self, "Guardar personaje", "Nombre del personaje:")
            if ok and name:
                current_character = name
                # Añadir a la lista desplegable si no existe
                if self.character_dropdown.findText(name) == -1:
                    self.character_dropdown.addItem(name)
                self.character_dropdown.setCurrentText(name)
            else:
                return
        
        # Obtener los valores actuales de todas las categorías
        current_values = self.prompt_generator.get_active_categories()
        
        # Guardar en un archivo JSON
        char_filename = current_character.lower().replace(" ", "_") + ".json"
        char_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "characters", char_filename)
        
        os.makedirs(os.path.dirname(char_path), exist_ok=True)
        with open(char_path, "w", encoding="utf-8") as f:
            json.dump(current_values, f, ensure_ascii=False, indent=2)
        
        self.character_desc.setText(f"Personaje guardado: {current_character}")
