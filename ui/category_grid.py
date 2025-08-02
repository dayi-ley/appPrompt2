import os
import json
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLineEdit, QScrollArea, QPushButton, QInputDialog, QMessageBox,
    QDialog, QLabel, QTextEdit  # Agregar estos imports
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from .components import CategoryCard, AddCategoryCard
from .utils.category_utils import (
    load_categories_and_tags, 
    normalize_category,
    update_categories_json,
    update_tags_json,
    rename_category_in_files,
    DEFAULT_CARD_COLOR
)
from .save_manager import SaveManager  # Mover la importación aquí

class CategoryGridFrame(QWidget):
    prompt_updated = pyqtSignal(str)
    category_value_changed = pyqtSignal(str, str, str)  # (category_name, old_value, new_value)
    character_saved = pyqtSignal(str)  # Nueva señal: (character_name)
    
    def __init__(self, prompt_generator):
        super().__init__()
        self.prompt_generator = prompt_generator
        self.cards = []
        self.previous_values = {}
        self.previous_values_snapshot = {}
        
        # Inicializar SaveManager con referencia a self
        self.save_manager = SaveManager(self, self)
        
        self.setup_ui()
        self.create_cards()

    def setup_ui(self):
        """Configura la interfaz del grid"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 0, 16, 16)
        self.main_layout.setSpacing(0)
        
        # --- Layout horizontal para buscador y botones ---
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)
        
        # Buscador
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Buscar categoría...")
        self.search_box.textChanged.connect(self.filter_cards)
        search_layout.addWidget(self.search_box)
        
        # Botón para importar datos
        self.import_data_btn = QPushButton("Importar Datos")
        self.import_data_btn.clicked.connect(self.import_data_dialog)
        search_layout.addWidget(self.import_data_btn)
        
        # Nuevo botón para guardar
        self.save_btn = QPushButton("Guardar")
        self.save_btn.clicked.connect(self.show_save_options)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #446879;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #acc8d7;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """)
        search_layout.addWidget(self.save_btn)
        
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
        # Crear mapeo inverso: formato capitalizado -> formato snake_case
        with open("c:\\Users\\LENOVO\\Desktop\\AppPrompts\\data\\categories.json", "r", encoding="utf-8") as f:
            original_categories = json.load(f)["categorias"]
        
        category_reverse_mapping = {}
        for orig_cat in original_categories:
            formatted_cat = orig_cat.replace("_", " ").capitalize()
            category_reverse_mapping[formatted_cat] = orig_cat
        
        # Detectar qué categoría cambió y notificar al sidebar
        current_values = self.get_current_values()
        
        for category_name, current_value in current_values.items():
            previous_value = self.previous_values.get(category_name, "")
            if previous_value != current_value:
                # Emitir señal de cambio específico
                self.category_value_changed.emit(category_name, previous_value, current_value)
                
                # Actualizar el prompt_generator con el nombre correcto
                snake_case_name = category_reverse_mapping.get(category_name, category_name.lower().replace(" ", "_"))
                if self.prompt_generator:
                    self.prompt_generator.update_category(snake_case_name, current_value)
        
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

    def show_save_options(self):
        """Muestra las opciones de guardado"""
        # Verificar que hay datos para guardar
        current_values = self.get_current_values()
        
        # Contar cuántas categorías tienen datos
        categories_with_data = 0
        for category_name, value in current_values.items():
            if value and value.strip():  # Si el valor no está vacío
                categories_with_data += 1
        
        # Si no hay datos en ninguna categoría, mostrar mensaje de advertencia
        if categories_with_data == 0:
            QMessageBox.warning(
                self, 
                "Sin datos para guardar", 
                "No se puede guardar porque no hay datos en ninguna categoría.\n\n"
                "Por favor, ingresa algunos valores en las categorías antes de guardar."
            )
            return
        
        # Si hay al menos una categoría con datos, proceder con el guardado
        self.save_manager.show_save_options()

    def save_current_as_variation(self):
        """Muestra el diálogo para seleccionar el tipo de guardado"""
        # Verificar que hay datos para guardar
        variation_data = {}
        for card in self.cards:
            if hasattr(card, 'input_field') and hasattr(card, 'category_name'):
                value = card.input_field.text().strip()
                if value:
                    variation_data[card.category_name] = value
        
        if not variation_data:
            QMessageBox.information(self, "Información", "No hay datos para guardar")
            return
        
        # Mostrar diálogo de selección
        dialog = SaveTypeDialog(self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            if dialog.save_type == "new_character":
                self.save_as_new_character(variation_data)
            elif dialog.save_type == "variation":
                # Mantener la funcionalidad original para variaciones
                current_values = self.get_current_values()
                changes = self.calculate_changes(self.previous_values_snapshot, current_values)
                self.save_variation_requested.emit(variation_data, changes)
    
    def save_as_new_character(self, variation_data):
        """Guarda los valores actuales como un nuevo personaje"""
        # Solicitar nombre del personaje
        name, ok = QInputDialog.getText(
            self, 
            "Nuevo Personaje", 
            "Ingresa el nombre del personaje:"
        )
        
        if not ok or not name.strip():
            return
        
        name = name.strip()
        
        # Verificar si ya existe
        characters_dir = "data/characters"
        if not os.path.exists(characters_dir):
            os.makedirs(characters_dir)
        
        character_file = os.path.join(characters_dir, f"{name}.json")
        if os.path.exists(character_file):
            reply = QMessageBox.question(
                self,
                "Personaje existente",
                f"El personaje '{name}' ya existe. ¿Deseas sobrescribirlo?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        try:
            # Guardar archivo del personaje
            with open(character_file, "w", encoding="utf-8") as f:
                json.dump(variation_data, f, ensure_ascii=False, indent=2)
            
            # Emitir señal para actualizar el dropdown de personajes
            self.character_saved.emit(name)
            
            QMessageBox.information(
                self, 
                "Éxito", 
                f"Personaje '{name}' guardado exitosamente."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Error al guardar el personaje: {str(e)}"
            )
    
    def import_data_dialog(self):
        """Muestra el diálogo para importar datos"""
        dialog = ImportDataDialog(self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            imported_data = dialog.get_imported_data()
            if imported_data:
                self.load_imported_data(imported_data)
    
    def load_imported_data(self, data):
        """Carga los datos importados en las tarjetas"""
        # Eliminar: print(f"[DEBUG] load_imported_data llamado con datos: {data}")
        if not data:
            # Eliminar: print("[DEBUG] No hay datos para cargar")
            return
            
        loaded_count = 0
        for card in self.cards:
            if hasattr(card, 'category_name') and hasattr(card, 'input_field'):
                category_name = card.category_name.lower().replace(' ', '_')
                if category_name in data:
                    card.input_field.setText(data[category_name])
                    loaded_count += 1
                    # Eliminar: print(f"[DEBUG] Cargado {category_name}: {data[category_name]}")
        
        self.update_prompt()
        # Eliminar: print(f"[DEBUG] Se cargaron {loaded_count} categorías")
        
        if loaded_count > 0:
            QMessageBox.information(
                self, 
                "Datos importados", 
                f"Se han cargado {loaded_count} categorías."
            )

    def apply_character_defaults(self, character_data):
        """Aplica los valores por defecto de un personaje a las tarjetas"""
        # Eliminar: print(f"[DEBUG] apply_character_defaults llamado con: {character_data}")
        if not character_data:
            # Eliminar: print("[DEBUG] No hay datos de personaje para aplicar")
            return
            
        loaded_count = 0
        for card in self.cards:
            if hasattr(card, 'category_name') and hasattr(card, 'input_field'):
                # Normalizar el nombre de la categoría para buscar en los datos
                category_name = card.category_name.lower().replace(' ', '_')
                
                if category_name in character_data:
                    card.input_field.setText(character_data[category_name])
                    loaded_count += 1
                    # Eliminar: print(f"[DEBUG] Aplicado {category_name}: {character_data[category_name]}")
        
        # Actualizar el prompt después de cargar los datos
        self.update_prompt()
        # Eliminar: print(f"[DEBUG] Se aplicaron {loaded_count} valores por defecto")
        
        # Opcional: mostrar mensaje de confirmación
        if loaded_count > 0:
            QMessageBox.information(
                self, 
                "Personaje cargado", 
                f"Se han cargado {loaded_count} categorías del personaje."
            )


class ImportDataDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Importar Datos")
        self.setModal(True)
        self.setFixedSize(600, 400)
        self.imported_data = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Instrucciones
        instructions = QLabel("Pega aquí los datos del personaje (formato: categoría: valor):")
        layout.addWidget(instructions)
        
        # Área de texto para pegar datos
        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText('Ejemplo:\n\nangulo: ((low angle)),\ncalidad_tecnica: masterpiece, best quality,\n ...\n')
        layout.addWidget(self.text_area)
        
        # Botones
        button_layout = QHBoxLayout()
        
        validate_btn = QPushButton("Validar y Cargar")
        validate_btn.clicked.connect(self.validate_and_load)
        button_layout.addWidget(validate_btn)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def validate_and_load(self):
        """Valida y procesa los datos ingresados"""
        text = self.text_area.toPlainText().strip()
        
        # 1. Validar que hay contenido
        if not text:
            QMessageBox.warning(self, "Sin datos", "No hay datos para validar o cargar.\n\nPor favor ingresa algunos datos en el área de texto.")
            return
        
        try:
            # 2. Procesar el texto línea por línea
            lines = text.split('\n')
            mapped_data = {}
            categories_with_values = []
            categories_empty = []
            
            # Obtener todas las categorías disponibles del sistema
            from .utils.category_utils import load_categories_and_tags
            all_categories = load_categories_and_tags()
            system_categories = [cat["name"].lower().replace(" ", "_") for cat in all_categories]
            
            for line in lines:
                line = line.strip()
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        category = parts[0].strip().lower().replace(" ", "_")
                        value = parts[1].strip()
                        
                        # 3. Validar y agregar coma al final si no la tiene
                        if value and not value.endswith(','):
                            value = value + ','
                        
                        mapped_data[category] = value
                        
                        # Clasificar categorías con y sin valores
                        if value and value.strip() and value.strip() != ',':
                            categories_with_values.append(category)
                        else:
                            categories_empty.append(category)
            
            # 4. Agregar categorías del sistema que no están en los datos (como vacías)
            for sys_cat in system_categories:
                if sys_cat not in mapped_data:
                    mapped_data[sys_cat] = ""
                    categories_empty.append(sys_cat)
            
            if not mapped_data:
                QMessageBox.warning(self, "Error", "No se encontraron datos válidos en el formato esperado.\n\nFormato: categoria: valor")
                return
            
            # 5. Mostrar información sobre categorías vacías
            if categories_empty:
                empty_list = "\n• ".join(categories_empty)
                message = f"Se detectaron {len(categories_empty)} categorías sin valores:\n\n• {empty_list}\n\n"
                message += f"Categorías con datos: {len(categories_with_values)}\n"
                message += "¿Deseas continuar con la carga?"
                
                reply = QMessageBox.question(
                    self, 
                    "Categorías vacías detectadas", 
                    message,
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Ok
                )
                
                if reply == QMessageBox.StandardButton.Cancel:
                    return
            
            # 6. Si todo está bien, proceder con la carga
            self.imported_data = mapped_data
            
            success_message = f"Datos validados correctamente.\n\n"
            success_message += f"• Categorías con valores: {len(categories_with_values)}\n"
            success_message += f"• Categorías vacías: {len(categories_empty)}\n"
            success_message += f"• Total de categorías: {len(mapped_data)}"
            
            QMessageBox.information(self, "Validación exitosa", success_message)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error inesperado durante la validación: {str(e)}")
    
    def get_imported_data(self):
        """Retorna los datos importados"""
        return self.imported_data


def capture_initial_snapshot(self):
    """Captura el snapshot de valores iniciales para detectar cambios posteriores"""
    # Obtener referencia al sidebar desde main_window
    main_window = self.parent()
    while main_window and not hasattr(main_window, 'sidebar'):
        main_window = main_window.parent()
    
    if main_window and hasattr(main_window, 'sidebar'):
        current_values = self.get_current_values()
        main_window.sidebar.original_values_snapshot = current_values.copy()
        main_window.sidebar.changes_tracker = {}  # Limpiar tracker
        print(f"Snapshot inicial capturado: {len(current_values)} categorías")