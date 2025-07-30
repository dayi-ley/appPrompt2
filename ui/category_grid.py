import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLineEdit, QScrollArea, QPushButton, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

# Importar componentes y utilidades
from .components import CategoryCard, AddCategoryCard
from .utils.category_utils import (
    load_categories_and_tags, 
    normalize_category,
    update_categories_json,
    update_tags_json,
    rename_category_in_files,
    DEFAULT_CARD_COLOR
)

class CategoryGridFrame(QWidget):
    prompt_updated = pyqtSignal(str)
    save_variation_requested = pyqtSignal(dict, dict)  # (variation_data, changes)
    category_value_changed = pyqtSignal(str, str, str)  # Nueva señal: (category_name, old_value, new_value)
    
    def __init__(self, prompt_generator):
        super().__init__()
        self.prompt_generator = prompt_generator
        self.cards = []
        self.previous_values = {}  # Para trackear valores anteriores
        self.previous_values_snapshot = {}  # Para el snapshot inicial
        self.setup_ui()
        self.reload_categories()  # Cambiar de load_categories a reload_categories

    def setup_ui(self):
        """Configura la interfaz del grid"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 0, 16, 16)
        self.main_layout.setSpacing(0)
        
        # --- Layout horizontal para buscador y botón ---
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)
        
        # Buscador
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Buscar categoría...")
        self.search_box.textChanged.connect(self.filter_cards)
        search_layout.addWidget(self.search_box)
        
        # Botón para guardar como variación
        self.save_variation_btn = QPushButton("Guardar como Variación")
        self.save_variation_btn.clicked.connect(self.save_current_as_variation)
        search_layout.addWidget(self.save_variation_btn)
        
        self.main_layout.addLayout(search_layout)

        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Widget contenedor para el grid
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(8)
        
        # Hacer el grid responsivo
        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setColumnStretch(1, 1)
        self.grid_layout.setColumnStretch(2, 1)
        
        self.scroll_area.setWidget(self.grid_widget)
        self.main_layout.addWidget(self.scroll_area)
        
    def setup_styles(self):
        """Configura los estilos del grid"""
        self.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                border: 1px solid #404040;
                border-radius: 6px;
                color: #e0e0e0;
                padding: 8px;
                font-size: 12px;
                margin-bottom: 8px;
            }
            QLineEdit:focus {
                border: 1px solid #6366f1;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                margin-top: 8px;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
        """)

    def create_cards(self):
        """Crea las tarjetas de categorías"""
        categories = load_categories_and_tags()
        
        row, col = 0, 0
        for category in categories:
            card = CategoryCard(
                category["name"], 
                category["icon"], 
                category["tags"], 
                self.prompt_generator
            )
            card.request_rename.connect(self.handle_category_rename)
            card.value_changed.connect(self.update_prompt)
            
            self.cards.append(card)
            self.grid_layout.addWidget(card, row, col)
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        # Tarjeta para añadir nueva categoría
        add_card = AddCategoryCard(self.add_custom_category)
        self.grid_layout.addWidget(add_card, row, col)

    def filter_cards(self, text):
        """Filtra las tarjetas según el texto de búsqueda"""
        text = text.lower()
        for card in self.cards:
            if hasattr(card, 'category_name'):
                visible = text in card.category_name.lower()
                card.setVisible(visible)

    def update_prompt(self):
        """Actualiza el prompt cuando cambian los valores de las tarjetas"""
        # Detectar qué categoría cambió y notificar al sidebar
        current_values = self.get_current_values()
        
        for category_name, current_value in current_values.items():
            previous_value = self.previous_values.get(category_name, "")
            if previous_value != current_value:
                # Emitir señal de cambio específico
                self.category_value_changed.emit(category_name, previous_value, current_value)
        
        # Actualizar valores anteriores
        self.previous_values = current_values.copy()
        
        # Usar el prompt_generator en lugar de generar el prompt manualmente
        prompt = self.prompt_generator.generate_prompt()
        self.prompt_updated.emit(prompt)
    
    def get_current_values(self):
        """Obtiene los valores actuales de todas las categorías"""
        current_values = {}
        for card in self.cards:
            if hasattr(card, 'category_name') and hasattr(card, 'input_field'):
                current_values[card.category_name] = card.input_field.text()
        return current_values
    
    def set_previous_values_snapshot(self, values):
        """Establece el snapshot de valores previos"""

        self.previous_values_snapshot = values

    def handle_category_rename(self, old_name, new_name):
        """Maneja el renombrado de categorías"""
        try:
            rename_category_in_files(old_name, new_name)
            QMessageBox.information(self, "Éxito", f"Categoría renombrada de '{old_name}' a '{new_name}'")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al renombrar categoría: {str(e)}")

    def add_custom_category(self):
        """Añade una nueva categoría personalizada"""
        name, ok = QInputDialog.getText(self, "Nueva Categoría", "Nombre de la categoría:")
        if ok and name.strip():
            try:
                normalized_name = normalize_category(name.strip())
                update_categories_json(normalized_name)
                update_tags_json(normalized_name, [])
                
                # Recrear las tarjetas
                self.clear_grid()
                self.create_cards()
                
                QMessageBox.information(self, "Éxito", f"Categoría '{name}' añadida correctamente")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error al añadir categoría: {str(e)}")

    def clear_grid(self):
        """Limpia el grid de tarjetas"""
        for card in self.cards:
            card.setParent(None)
        self.cards.clear()
        
        # Limpiar el grid layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

    def save_current_as_variation(self):
        """Guarda el estado actual como una variación"""
        # Capturar cambios antes de guardar
        current_values = self.get_current_values()
        changes = self.calculate_changes(self.previous_values_snapshot, current_values)
        
        variation_data = {}
        for card in self.cards:
            if hasattr(card, 'input_field') and hasattr(card, 'category_name'):
                value = card.input_field.text().strip()
                if value:
                    variation_data[card.category_name] = value
        
        if variation_data:
            # Pasar también los cambios detectados
            self.save_variation_requested.emit(variation_data, changes)
        else:
            QMessageBox.information(self, "Información", "No hay datos para guardar como variación")
    
    def calculate_changes(self, original_values, current_values):
        """Calcula los cambios entre valores originales y actuales"""
        
        changes = {}
        
        for category, current_value in current_values.items():
            original_value = original_values.get(category, "")
            
            if original_value != current_value:
                # Calcular valores añadidos y eliminados
                original_set = set(original_value.split(", ")) if original_value else set()
                current_set = set(current_value.split(", ")) if current_value else set()
                
                added = current_set - original_set
                removed = original_set - current_set
                
                if added or removed:
                    changes[category] = {
                        'added': list(added),
                        'removed': list(removed)
                    }
        
        return changes

    def apply_variation(self, variation_data):
        """Aplica una variación a las tarjetas"""
        for card in self.cards:
            if hasattr(card, 'input_field') and hasattr(card, 'category_name'):
                category_name = card.category_name
                if category_name in variation_data:
                    card.input_field.setText(variation_data[category_name])
                else:
                    card.input_field.clear()
        
        self.update_prompt()

    def set_defaults_for_character(self, defaults_dict):
        """Llena los QLineEdit de las tarjetas con los valores por defecto del personaje"""
        def normalize(name):
            return name.lower().replace(" ", "").replace("(", "").replace(")", "").replace("_", "")
        
        for card in self.cards:
            if not isinstance(card, CategoryCard):
                continue
            card_norm = normalize(card.category_name)
            for key, value in defaults_dict.items():
                if normalize(key) == card_norm:
                    card.input_field.setText(value)
                    # Actualizar el prompt_generator directamente
                    if self.prompt_generator:
                        self.prompt_generator.update_category(card.category_name, value)
                    break
        
        # AÑADIR al final:
        # Establecer snapshot después de cargar valores
        self.set_previous_values_snapshot(self.get_current_values())
        
        # Emitir señal para actualizar el prompt después de cargar todos los valores
        self.update_prompt()

    def reload_categories(self):
        """Recarga las categorías desde los archivos"""
        self.clear_grid()
        self.create_cards()