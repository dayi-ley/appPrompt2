from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QFrame, QSizePolicy, QTabWidget)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
from ui.variations_panel import VariationsPanel
from logic.variations_manager import VariationsManager
import os
import json

class SidebarFrame(QFrame):
    character_defaults_selected = pyqtSignal(dict)
    variation_applied = pyqtSignal(dict)  # Nueva señal para aplicar variaciones
    
    def __init__(self, prompt_generator):
        super().__init__()
        self.prompt_generator = prompt_generator
        self.is_collapsed = False
        self.expanded_width = 280  # Aumentado para acomodar el panel de variaciones
        self.collapsed_width = 60
        
        # Inicializar el manager de variaciones
        self.variations_manager = VariationsManager()
        
        # Sistema de tracking de cambios
        self.original_values_snapshot = {}  # Valores cuando se cargó la variación
        self.changes_tracker = {}  # Registro de cambios específicos
        
        self.setup_ui()
        self.setup_styles()
        self.setup_data()
        self.connect_variation_signals()

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
        
        # Contenedor para el contenido con pestañas
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        
        # Widget de pestañas
        self.tab_widget = QTabWidget()
        
        # Pestaña de Personajes
        self.character_tab = QWidget()
        self.setup_character_tab()
        self.tab_widget.addTab(self.character_tab, "Personajes")
        
        # Pestaña de Variaciones
        self.variations_panel = VariationsPanel(self.variations_manager, self.prompt_generator)
        self.tab_widget.addTab(self.variations_panel, "Variaciones")
        
        content_layout.addWidget(self.tab_widget)
        layout.addWidget(self.content_widget)

    def setup_character_tab(self):
        """Configura la pestaña de personajes"""
        layout = QVBoxLayout(self.character_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Selector de personaje
        self.character_label = QLabel("Personaje")
        self.character_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(self.character_label)
        
        self.character_dropdown = QComboBox()
        self.character_dropdown.addItems([
            "Seleccionar personaje...",
            "kobayashi",
            "aria",
            "Personaje 1",
            "Personaje 2",
            "Personaje 3"
        ])
        self.character_dropdown.currentTextChanged.connect(self.on_character_change)
        layout.addWidget(self.character_dropdown)
        
        # Descripción del personaje
        self.character_desc = QLabel("Selecciona un personaje para ver su descripción")
        self.character_desc.setFont(QFont("Segoe UI", 9))
        self.character_desc.setStyleSheet("color: #a0a0a0;")
        self.character_desc.setWordWrap(True)
        layout.addWidget(self.character_desc)
        
        # Selector de escena
        self.scene_label = QLabel("Escena")
        self.scene_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(self.scene_label)
        
        self.scene_dropdown = QComboBox()
        self.scene_dropdown.addItems(["Seleccionar escena...", "Escena 1", "Escena 2", "Escena 3"])
        self.scene_dropdown.currentTextChanged.connect(self.on_scene_change)
        layout.addWidget(self.scene_dropdown)
        
        # Descripción de la escena
        self.scene_desc = QLabel("Selecciona una escena para ver su configuración")
        self.scene_desc.setFont(QFont("Segoe UI", 9))
        self.scene_desc.setStyleSheet("color: #a0a0a0;")
        self.scene_desc.setWordWrap(True)
        layout.addWidget(self.scene_desc)
        
        # Botón para gestionar personajes
        self.edit_character_btn = QPushButton("Gestionar personajes")
        self.edit_character_btn.setFixedHeight(32)
        layout.addWidget(self.edit_character_btn)
        
        # Botón para guardar el personaje actual
        self.save_character_btn = QPushButton("Guardar personaje actual")
        self.save_character_btn.setFixedHeight(32)
        self.save_character_btn.clicked.connect(self.save_current_character)
        layout.addWidget(self.save_character_btn)
        
        # Espaciador
        layout.addStretch()

    def connect_variation_signals(self):
        """Conecta las señales del panel de variaciones"""
        self.variations_panel.variation_loaded.connect(self.on_variation_loaded)
        self.variations_panel.variation_saved.connect(self.on_variation_saved)

    def on_variation_loaded(self, variation_data):
        """Maneja cuando se carga una variación"""
        # Guardar snapshot de los valores originales
        self.original_values_snapshot = variation_data.get('values', {}).copy()
        self.changes_tracker = {}  # Limpiar tracker de cambios
        
        # Emitir señal para que el main_window aplique la variación
        self.variation_applied.emit(variation_data)
        
        # Actualizar la descripción del personaje si es necesario
        character_name = variation_data.get('character', '')
        if character_name:
            current_char = self.character_dropdown.currentText()
            if current_char != character_name:
                index = self.character_dropdown.findText(character_name)
                if index >= 0:
                    self.character_dropdown.setCurrentIndex(index)
    
    def track_category_change(self, category_name, old_value, new_value):
        """Registra un cambio específico en una categoría"""
        if category_name not in self.original_values_snapshot:
            self.original_values_snapshot[category_name] = ""
        
        original = self.original_values_snapshot[category_name]
        
        # Calcular qué se añadió específicamente
        original_items = set(item.strip() for item in original.split(',') if item.strip())
        new_items = set(item.strip() for item in new_value.split(',') if item.strip())
        
        added_items = new_items - original_items
        removed_items = original_items - new_items
        
        if added_items or removed_items:
            self.changes_tracker[category_name] = {
                'added': list(added_items),
                'removed': list(removed_items),
                'original': original,
                'current': new_value
            }
        elif category_name in self.changes_tracker:
            # Si no hay cambios, remover del tracker
            del self.changes_tracker[category_name]

    def on_variation_saved(self, character_name, variation_name):
        """Maneja cuando se guarda una variación"""
        # Actualizar el panel de variaciones para mostrar la nueva variación
        self.variations_panel.refresh_variations()
        
        # Mostrar mensaje de confirmación
        self.character_desc.setText(f"Variación '{variation_name}' guardada para {character_name}")

    def get_current_character(self):
        """Obtiene el personaje actualmente seleccionado"""
        current = self.character_dropdown.currentText()
        if current == "Seleccionar personaje...":
            return None
        return current

    def set_current_character(self, character_name):
        """Establece el personaje actual en el dropdown"""
        index = self.character_dropdown.findText(character_name)
        if index >= 0:
            self.character_dropdown.setCurrentIndex(index)
        else:
            # Añadir el personaje si no existe
            self.character_dropdown.addItem(character_name)
            self.character_dropdown.setCurrentText(character_name)

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

    def save_current_variation(self, current_values, changes=None):
        """Guarda la variación actual usando el diálogo de guardado"""
        from .variations_panel import SaveVariationDialog
        
        # Obtener el personaje actual
        current_character = self.get_current_character()
        if not current_character:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, 
                "Sin personaje", 
                "Debe seleccionar un personaje antes de guardar una variación."
            )
            return
        
        # Abrir diálogo para guardar variación (pasando también los cambios)
        dialog = SaveVariationDialog(current_character, current_values, self, changes)
        if dialog.exec() == dialog.DialogCode.Accepted:
            variation_data = dialog.get_variation_data()
            
            # Guardar usando VariationsManager
            success = self.variations_manager.save_variation(
                current_character,
                variation_data['name'],
                variation_data
            )
            
            if success:
                # Actualizar el panel de variaciones
                # En lugar de:
                self.variations_panel.load_variations(current_character)
                
                # Usar:
                self.variations_panel.load_variations()  # Sin parámetros
                
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self, 
                    "Variación guardada", 
                    f"La variación '{variation_data['name']}' se ha guardado correctamente."
                )
            else:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(
                    self, 
                    "Error", 
                    "No se pudo guardar la variación. Inténtelo de nuevo."
                )
