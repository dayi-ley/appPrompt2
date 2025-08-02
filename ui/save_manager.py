from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QMessageBox, QComboBox, QLineEdit, 
    QFormLayout, QFrame, QCompleter
)
from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QFont
import os
import json
from .new_character_dialog import NewCharacterDialog
from .variation_changes_widget import VariationChangesWidget

class SaveOptionsDialog(QDialog):
    """Diálogo para seleccionar el tipo de guardado"""
    
    def __init__(self, parent=None, category_grid=None):
        super().__init__(parent)
        self.category_grid = category_grid
        self.setWindowTitle("Guardar Configuración")
        self.setModal(True)
        self.setFixedSize(450, 200)
        self.selected_option = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(30, 30, 30, 20)
        
        # Título
        title_label = QLabel("Guardar configuración actual")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #FFFFFF; margin-bottom: 5px;")
        layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel("¿Deseas crear un nuevo personaje o guardar como\nvariación de un personaje existente?")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setFont(QFont("Segoe UI", 11))
        desc_label.setStyleSheet("color: #FFFFFF; line-height: 1.5; margin-bottom: 10px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addSpacing(10)
        
        # Botones
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
        layout.addStretch()
        
        # Botón cancelar
        cancel_layout = QHBoxLayout()
        cancel_layout.addStretch()
        
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
                QMessageBox.information(self, "Éxito", f"Personaje '{character_name}' creado exitosamente.")
                self.selected_option = "new_character"
                self.character_name = character_name
                self.accept()
    
    def select_variation(self):
        """Muestra el diálogo para crear variación de personaje"""
        # Obtener referencia al sidebar desde el parent
        sidebar = None
        if hasattr(self.parent, 'sidebar'):
            sidebar = self.parent.sidebar
            
            # IMPORTANTE: Establecer snapshot de valores actuales antes de abrir la ventana
            if hasattr(self.parent, 'category_grid'):
                current_values = self.parent.category_grid.get_current_values()
                sidebar.original_values_snapshot = current_values.copy()
                sidebar.changes_tracker = {}  # Limpiar tracker de cambios
        
        # Línea 147 - Correcto
        dialog = VariationDialog(self, sidebar, self.category_grid)#Pasar sidebar y category_grid
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            variation_data = dialog.get_variation_data()
            if variation_data:
                self.selected_option = "variation"
                self.character_name = variation_data['character']
                self.variation_name = variation_data['variation_name']
                self.accept()
    
    def get_selected_option(self):
        """Retorna la opción seleccionada"""
        return self.selected_option

class VariationDialog(QDialog):
    """Diálogo para crear una nueva variación de personaje"""
    
    def __init__(self, parent=None, sidebar=None, category_grid=None):
        super().__init__(parent)
        self.sidebar = sidebar
        self.category_grid = category_grid  # Añadir referencia
        self.setWindowTitle("Crear Variación de Personaje")
        self.setModal(True)
        self.setFixedSize(500, 550)
        self.selected_character = None
        self.variation_name = None
        self.setup_ui()
        self.load_available_characters()
        
        # Establecer snapshot de valores actuales al abrir la ventana
        self.capture_current_state()
    
    def capture_current_state(self):
        """Captura el estado actual de las categorías como punto de referencia"""
        if self.sidebar and hasattr(self.parent, 'category_grid'):
            current_values = self.parent.category_grid.get_current_values()
            self.sidebar.original_values_snapshot = current_values.copy()
            self.sidebar.changes_tracker = {}  # Limpiar tracker de cambios
            print(f"Snapshot capturado: {len(current_values)} categorías")
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        
        # Selector de personaje
        character_layout = QVBoxLayout()
        
        character_label = QLabel("Seleccionar el personaje para esta variacion:")
        character_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        character_label.setStyleSheet("color: #FFFFFF;")
        character_layout.addWidget(character_label)
        
        # ComboBox con buscador mejorado
        self.character_combo = QComboBox()
        self.character_combo.setEditable(True)
        self.character_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.character_combo.setFixedHeight(35)
        
        # Configurar el completer para búsqueda
        self.completer = QCompleter()
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.character_combo.setCompleter(self.completer)
        
        self.character_combo.setStyleSheet("""
            QComboBox {
                background-color: #3a3a3a;
                border: 2px solid #555;
                border-radius: 6px;
                padding: 5px 10px;
                color: #ffffff;
                font-size: 12px;
            }
            QComboBox:focus {
                border-color: #4a90e2;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
                background-color: #4a4a4a;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }
            QComboBox::drop-down:hover {
                background-color: #5a5a5a;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid #ffffff;
                margin: 0px;
            }
            QComboBox::down-arrow:hover {
                border-top-color: #4a90e2;
            }
            QComboBox QAbstractItemView {
                background-color: #3a3a3a;
                border: 1px solid #555;
                selection-background-color: #4a90e2;
                color: #ffffff;
            }
        """)
        
        # Conectar eventos mejorados
        self.character_combo.currentTextChanged.connect(self.on_character_text_changed)
        self.character_combo.activated.connect(self.on_character_selected)
        character_layout.addWidget(self.character_combo)
        
        layout.addLayout(character_layout)
        
        # Campo de nombre de variación
        variation_layout = QVBoxLayout()
        
        variation_label = QLabel("Nombre de variación:")
        variation_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        variation_label.setStyleSheet("color: #FFFFFF;")
        variation_layout.addWidget(variation_label)
        
        self.variation_input = QLineEdit()
        self.variation_input.setFixedHeight(35)
        self.variation_input.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                border: 2px solid #555;
                border-radius: 6px;
                padding: 5px 10px;
                color: #ffffff;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
            }
        """)
        variation_layout.addWidget(self.variation_input)
        
        layout.addLayout(variation_layout)
        
        # Sección de cambios detectados
        self.changes_widget = VariationChangesWidget(self, self.sidebar, self.category_grid)  # Usar self.sidebar y self.category_grid
        layout.addWidget(self.changes_widget)
        
        # Conectar señal para cuando se actualicen los cambios
        self.changes_widget.changes_updated.connect(self.on_changes_updated)
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Botón Cancelar
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setFixedSize(100, 35)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888;
                border: 2px solid #555;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #444;
                border-color: #666;
                color: #fff;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        
        # Botón Crear
        self.create_btn = QPushButton("Crear Variación")
        self.create_btn.setFixedSize(130, 35)
        self.create_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #666;
                color: #aaa;
            }
        """)
        self.create_btn.clicked.connect(self.create_variation)
        self.create_btn.setEnabled(False)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.create_btn)
        
        layout.addLayout(buttons_layout)
    
    def detect_current_character(self):
        """Intenta detectar y preseleccionar el personaje actual"""
        try:
            # Aquí podrías implementar lógica para detectar el personaje actual
            # Por ejemplo, desde el sidebar o algún estado global
            # Por ahora, simplemente no preselecciona nada
            pass
        except Exception as e:
            print(f"Error detectando personaje actual: {e}")
    
    def load_available_characters(self):
        """Carga los personajes disponibles en el ComboBox"""
        try:
            characters_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "characters")
            
            if not os.path.exists(characters_dir):
                return
            
            characters = []
            
            for item in os.listdir(characters_dir):
                item_path = os.path.join(characters_dir, item)
                if os.path.isdir(item_path):
                    # Buscar archivo JSON con el mismo nombre que la carpeta
                    json_filename = f"{item}.json"
                    character_file = os.path.join(item_path, json_filename)
                    if os.path.exists(character_file):
                        try:
                            with open(character_file, 'r', encoding='utf-8') as f:
                                character_data = json.load(f)
                                if "metadata" in character_data and "character_name" in character_data["metadata"]:
                                    character_name = character_data["metadata"]["character_name"]
                                    characters.append(character_name)
                        except Exception as e:
                            print(f"Error cargando personaje {item}: {e}")
            
            characters.sort()
            
            # Limpiar y agregar personajes (SIN texto placeholder)
            self.character_combo.clear()
            for character in characters:
                self.character_combo.addItem(character)
            
            # Configurar el completer con la lista de personajes
            from PyQt6.QtCore import QStringListModel
            model = QStringListModel(characters)
            self.completer.setModel(model)
            
            # Establecer placeholder text en lugar de un item
            self.character_combo.setCurrentText("")
            self.character_combo.lineEdit().setPlaceholderText("🔍 Buscar personaje...")
            
            self.detect_current_character()
            
        except Exception as e:
            print(f"Error cargando personajes: {e}")
    
    def on_character_text_changed(self, text):
        """Maneja cambios en el texto del selector"""
        # Solo procesar si el texto no está vacío
        if text and text.strip():
            # Verificar si el texto coincide exactamente con un personaje
            index = self.character_combo.findText(text, Qt.MatchFlag.MatchExactly)
            if index >= 0:
                self.handle_character_selection(text)
        else:
            # Si está vacío, limpiar selección
            self.selected_character = None
            self.variation_input.clear()
            self.create_btn.setEnabled(False)
    
    def on_character_selected(self, index):
        """Maneja la selección de personaje por índice (desde activated signal)"""
        # Obtener el texto del elemento seleccionado usando el índice
        character_name = self.character_combo.itemText(index)
        self.handle_character_selection(character_name)
    
    def handle_character_selection(self, character_name):
        """Maneja la selección de personaje y genera nombre de variación"""
        if character_name and character_name.strip():
            self.selected_character = character_name
            self.generate_variation_name(character_name)
            self.create_btn.setEnabled(True)
            
            # Asegurar que el texto del combo sea exactamente el nombre del personaje
            self.character_combo.setCurrentText(character_name)
        else:
            self.selected_character = None
            self.variation_input.clear()
            self.create_btn.setEnabled(False)
    
    def generate_variation_name(self, character_name):
        """Genera automáticamente el nombre de la variación"""
        try:
            from logic.variations_manager import VariationsManager
            variations_manager = VariationsManager()
            
            character_data = variations_manager.get_character_variations(character_name)
            existing_variations = character_data.get("variations", {})
            
            base_name = f"{character_name}_var"
            counter = 1
            
            while f"{base_name}{counter}" in existing_variations:
                counter += 1
            
            variation_name = f"{base_name}{counter}"
            self.variation_input.setText(variation_name)
            
        except Exception as e:
            self.variation_input.setText(f"{character_name}_var1")
            print(f"Error generando nombre de variación: {e}")
    
    def on_changes_updated(self):
        """Maneja cuando se actualizan los cambios detectados"""
        print("Cambios actualizados en VariationDialog")
        
        # Opcional: habilitar el botón de crear variación si hay cambios
        try:
            changes_data = self.changes_widget.get_changes_data()
            if changes_data:
                print(f"Se detectaron cambios en {len(changes_data)} categorías")
        except Exception as e:
            print(f"Error obteniendo cambios: {e}")

    def create_variation(self):
        """Crea la variación y cierra el diálogo"""
        character = self.selected_character
        variation = self.variation_input.text().strip()
        
        if not character or not variation:
            QMessageBox.warning(self, "Error", "Selecciona un personaje y especifica un nombre de variación.")
            return
        
        if not variation.replace('_', '').replace('-', '').isalnum():
            QMessageBox.warning(self, "Error", "El nombre de variación solo puede contener letras, números, guiones y guiones bajos.")
            return
        
        self.selected_character = character
        self.variation_name = variation
        self.accept()
    
    def get_variation_data(self):
        """Retorna los datos de la variación creada"""
        return {
            'character': self.selected_character,
            'variation_name': self.variation_name
        }

class SaveManager:
    """Clase para manejar todas las funcionalidades de guardado"""
    
    def __init__(self, parent=None, category_grid=None):
        self.parent = parent
        self.category_grid = category_grid
    
    def show_save_options(self):
        """Muestra la ventana de opciones de guardado"""
        dialog = SaveOptionsDialog(self.parent, self.category_grid)
        dialog.exec()

    
    def on_changes_updated(self):
        """Maneja cuando se actualizan los cambios detectados"""
        print("Cambios actualizados en VariationDialog")
        
        # Opcional: habilitar el botón de crear variación si hay cambios
        changes_data = self.changes_widget.get_changes_data()
        if changes_data:
            print(f"Se detectaron cambios en {len(changes_data)} categorías")