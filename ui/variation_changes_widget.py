import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QScrollArea, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

class VariationChangesWidget(QWidget):
    # Señal para cuando se actualicen los cambios
    changes_updated = pyqtSignal()
    
    def __init__(self, parent=None, sidebar=None, category_grid=None):
        super().__init__(parent)
        self.sidebar = sidebar
        self.category_grid = category_grid  # Añadir referencia a category_grid
        self.changes_data = {}  # Agregar esta línea para almacenar los cambios
        self.setup_ui()
    
    def load_changes(self):
        """Carga y muestra los cambios detectados comparando con el personaje seleccionado"""
        # Limpiar el layout actual
        self.clear_changes_display()
        
        # Obtener el personaje seleccionado del diálogo padre
        selected_character = None
        if hasattr(self.parent(), 'selected_character'):
            selected_character = self.parent().selected_character
        
        print(f"DEBUG: Personaje seleccionado: {selected_character}")  # DEBUG
        
        if not selected_character:
            self.show_message("Selecciona un personaje para comparar los cambios.")
            return
        
        # Comparar valores actuales con el personaje seleccionado
        try:
            changes = self.compare_with_character(selected_character)
            
            print(f"DEBUG: Cambios detectados: {changes}")  # DEBUG
            
            if changes:
                self.changes_data = changes
                self.display_changes(changes)
            else:
                self.show_no_changes()
                
        except Exception as e:
            print(f"DEBUG: Error en load_changes: {e}")  # DEBUG
            self.show_message(f"Error al comparar con {selected_character}: {str(e)}")
        
        # Emitir señal de que se actualizaron los cambios
        self.changes_updated.emit()
    
    def compare_with_character(self, character_name):
        """Compara los valores actuales con los del personaje seleccionado"""
        changes = {}
        
        # Obtener valores actuales y del personaje
        current_values = self.get_current_values()
        character_values = self.load_character_values(character_name)
        
        print(f"DEBUG: Valores actuales: {current_values}")
        print(f"DEBUG: Valores del personaje: {character_values}")
        
        # SOLUCIÓN: Normalizar nombres de categorías a minúsculas
        for category_name in current_values.keys():
            current_items = current_values.get(category_name, [])
            
            # Buscar la categoría en el personaje usando nombre normalizado
            normalized_name = category_name.lower().replace(' ', '_')
            original_items = character_values.get(normalized_name, [])
            
            print(f"DEBUG: Categoría {category_name}:")
            print(f"  - Nombre normalizado: {normalized_name}")
            print(f"  - Original: {original_items}")
            print(f"  - Actual: {current_items}")
            
            category_changes = self.detect_category_changes(original_items, current_items)
            print(f"  - Cambios detectados: {category_changes}")
            print(f"  - Tiene cambios: {len(category_changes) > 0}")
            
            if category_changes and len(category_changes) > 0:
                changes[category_name] = category_changes
                print(f"  - ✅ Agregando {category_name} porque tiene {len(category_changes)} cambios")
            else:
                print(f"  - ❌ NO agregando {category_name} porque no tiene cambios")
        
        return changes
    
    def detect_category_changes(self, original_items, current_items):
        """Detecta los cambios entre los elementos originales y actuales"""
        changes = []
        
        # Convertir a listas si no lo son y limpiar
        if isinstance(original_items, str):
            original_items = [item.strip() for item in original_items.split(',') if item.strip()]
        if isinstance(current_items, str):
            current_items = [item.strip() for item in current_items.split(',') if item.strip()]
        
        # Asegurar que sean listas
        if not isinstance(original_items, list):
            original_items = []
        if not isinstance(current_items, list):
            current_items = []
        
        original_set = set(original_items)
        current_set = set(current_items)
        
        # CAMBIO CLAVE: Si son exactamente iguales, retornar lista vacía inmediatamente
        if original_set == current_set:
            return []  # No hay cambios
        
        # Solo si hay diferencias, calcular los cambios
        added = current_set - original_set
        removed = original_set - current_set
        
        for item in added:
            changes.append(f"➕ Agregado: {item}")
        
        for item in removed:
            changes.append(f"➖ Eliminado: {item}")
        
        return changes
    
    def get_current_values(self):
        """Obtiene los valores actuales de todas las categorías"""
        print(f"DEBUG get_current_values: category_grid = {self.category_grid}")  # DEBUG
        
        if not self.category_grid:
            print("DEBUG: category_grid es None")
            return {}
        
        current_values = {}
        
        print(f"DEBUG: category_grid.cards = {hasattr(self.category_grid, 'cards')}")  # DEBUG
        
        if hasattr(self.category_grid, 'cards'):
            print(f"DEBUG: Número de cards: {len(self.category_grid.cards)}")  # DEBUG
            
            # Iterar sobre las cards del category_grid
            for i, card in enumerate(self.category_grid.cards):
                print(f"DEBUG: Card {i}: {card}")
                print(f"DEBUG: Card {i} tiene category_name: {hasattr(card, 'category_name')}")
                print(f"DEBUG: Card {i} tiene input_field: {hasattr(card, 'input_field')}")
                
                if hasattr(card, 'category_name'):
                    print(f"DEBUG: Card {i} category_name: {card.category_name}")
                
                if hasattr(card, 'input_field'):
                    print(f"DEBUG: Card {i} input_field.text(): {card.input_field.text()}")
                
                if hasattr(card, 'category_name') and hasattr(card, 'input_field'):
                    category_name = card.category_name
                    # Obtener el texto del input field
                    text_value = card.input_field.text().strip()
                    
                    print(f"DEBUG: Procesando categoría {category_name} con valor: '{text_value}'")
                    
                    # Convertir el texto en una lista de elementos (separados por comas)
                    if text_value:
                        # Dividir por comas y limpiar espacios
                        selected_items = [item.strip() for item in text_value.split(',') if item.strip()]
                    else:
                        selected_items = []
                    
                    current_values[category_name] = selected_items
                    print(f"DEBUG: Agregado {category_name}: {selected_items}")
        else:
            print("DEBUG: category_grid no tiene atributo 'cards'")
            # Intentar otros atributos posibles
            print(f"DEBUG: Atributos de category_grid: {dir(self.category_grid)}")
        
        print(f"DEBUG: current_values final: {current_values}")
        return current_values
    
    def load_character_values(self, character_name):
        """Carga los valores del personaje desde su archivo JSON"""
        import os
        import json
        
        # Construir la ruta al archivo del personaje
        character_dir = os.path.join("data", "characters", character_name)
        character_file = os.path.join(character_dir, f"{character_name}.json")
        
        print(f"DEBUG load_character_values: Buscando archivo: {character_file}")
        
        if not os.path.exists(character_file):
            print(f"DEBUG: Archivo no encontrado: {character_file}")
            return {}
        
        try:
            with open(character_file, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
                print(f"DEBUG: Datos cargados del JSON: {character_data}")
            
            # CAMBIO CLAVE: Acceder a los datos dentro de 'categories'
            if 'categories' not in character_data:
                print(f"DEBUG: No se encontró 'categories' en el JSON")
                return {}
            
            categories_data = character_data['categories']
            print(f"DEBUG: Datos de categories: {categories_data}")
            
            character_values = {}
            
            # Extraer valores de las categorías
            for category_name, category_value in categories_data.items():
                print(f"DEBUG: Procesando categoría {category_name} con valor: '{category_value}'")
                
                # Los valores en el JSON son strings separados por comas
                if isinstance(category_value, str):
                    # Dividir por comas y limpiar espacios
                    if category_value.strip():  # Si no está vacío
                        items = [item.strip() for item in category_value.split(',') if item.strip()]
                    else:
                        items = []  # Si está vacío
                    print(f"DEBUG: Categoría {category_name} - items procesados: {items}")
                else:
                    items = []
                    print(f"DEBUG: Categoría {category_name} - formato inesperado: {type(category_value)}")
                
                character_values[category_name] = items
            
            print(f"DEBUG: character_values final: {character_values}")
            return character_values
            
        except Exception as e:
            print(f"DEBUG: Error cargando {character_file}: {e}")
            return {}
    
    def show_message(self, message):
        """Muestra un mensaje en el área de cambios"""
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("""
            color: #ffa500;
            font-style: italic;
            font-size: 11px;
            padding: 20px;
        """)
        self.changes_layout.addWidget(message_label)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Título y botón de actualizar
        header_layout = QHBoxLayout()
        
        title = QLabel("Cambios Realizados")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #FFFFFF;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botón para actualizar/cargar cambios
        self.update_btn = QPushButton("🔄 Actualizar Cambios")
        self.update_btn.setFixedSize(150, 30)
        self.update_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2968a3;
            }
        """)
        self.update_btn.clicked.connect(self.load_changes)
        header_layout.addWidget(self.update_btn)
        
        layout.addLayout(header_layout)
        
        # Área de scroll para mostrar los cambios
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(150)  # Altura mínima
        scroll_area.setMaximumHeight(350)  # Aumentar de 200 a 350
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #555;
                border-radius: 6px;
                background-color: #2a2a2a;
            }
            QScrollBar:vertical {
                background-color: #3a3a3a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666;
            }
        """)
        
        # Widget contenedor para los cambios
        self.changes_container = QWidget()
        self.changes_layout = QVBoxLayout(self.changes_container)
        self.changes_layout.setSpacing(8)
        
        # Mensaje inicial
        self.no_changes_label = QLabel("No hay cambios detectados.\nPresiona 'Actualizar Cambios' para cargar.")
        self.no_changes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_changes_label.setStyleSheet("""
            color: #888;
            font-style: italic;
            font-size: 11px;
            padding: 20px;
        """)
        self.changes_layout.addWidget(self.no_changes_label)
        
        scroll_area.setWidget(self.changes_container)
        layout.addWidget(scroll_area)
    
    def clear_changes_display(self):
        """Limpia la visualización actual de cambios"""
        while self.changes_layout.count():
            child = self.changes_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def display_changes(self, changes_dict):
        """Muestra los cambios detectados en la interfaz"""
        self.clear_changes_display()
        
        # Guardar los cambios para get_changes_data()
        self.changes_data = changes_dict
        
        if not changes_dict:
            self.show_no_changes()
            return
        
        for category, changes in changes_dict.items():
            # Frame para cada categoría
            category_frame = QFrame()
            category_frame.setStyleSheet("""
                QFrame {
                    background-color: #333;
                    border: 1px solid #555;
                    border-radius: 6px;
                    margin: 2px;
                }
            """)
            
            category_layout = QVBoxLayout(category_frame)
            category_layout.setSpacing(4)
            
            # Nombre de la categoría
            category_label = QLabel(f"📁 {category}")
            category_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            category_label.setStyleSheet("color: #4a90e2; padding: 4px;")
            category_layout.addWidget(category_label)
            
            # Container para los tags
            tags_container = QWidget()
            tags_layout = QHBoxLayout(tags_container)
            tags_layout.setSpacing(4)
            tags_layout.setContentsMargins(10, 0, 10, 0)
            
            # Crear tags clickeables para cada cambio
            for change in changes:
                # Extraer el texto del cambio y determinar el tipo
                if change.startswith("➕ Agregado: "):
                    tag_text = change.replace("➕ Agregado: ", "")
                    tag_color = "#28a745"  # Verde para agregado
                    change_type = "added"
                elif change.startswith("➖ Eliminado: "):
                    tag_text = change.replace("➖ Eliminado: ", "")
                    tag_color = "#dc3545"  # Rojo para eliminado
                    change_type = "removed"
                else:
                    tag_text = change
                    tag_color = "#6c757d"  # Gris para otros
                    change_type = "other"
                
                # Crear el tag como un QPushButton clickeable
                tag_button = QPushButton(tag_text)
                tag_button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {tag_color};
                        color: white;
                        padding: 4px 8px;
                        border-radius: 12px;
                        font-size: 9px;
                        font-weight: bold;
                        margin: 2px;
                        border: none;
                    }}
                    QPushButton:hover {{
                        background-color: {self._get_hover_color(tag_color)};
                    }}
                    QPushButton:pressed {{
                        background-color: {self._get_pressed_color(tag_color)};
                    }}
                """)
                
                # Conectar el clic del botón con la funcionalidad correspondiente
                tag_button.clicked.connect(
                    lambda checked, cat=category, text=tag_text, ctype=change_type: 
                    self._handle_tag_click(cat, text, ctype)
                )
                
                tags_layout.addWidget(tag_button)
            
            # Agregar stretch para alinear tags a la izquierda
            tags_layout.addStretch()
            
            category_layout.addWidget(tags_container)
            self.changes_layout.addWidget(category_frame)
        
        self.changes_layout.addStretch()
    
    def _get_hover_color(self, base_color):
        """Retorna un color más claro para el hover"""
        color_map = {
            "#28a745": "#34ce57",  # Verde más claro
            "#dc3545": "#e74c3c",  # Rojo más claro
            "#6c757d": "#868e96"   # Gris más claro
        }
        return color_map.get(base_color, base_color)
    
    def _get_pressed_color(self, base_color):
        """Retorna un color más oscuro para el pressed"""
        color_map = {
            "#28a745": "#1e7e34",  # Verde más oscuro
            "#dc3545": "#bd2130",  # Rojo más oscuro
            "#6c757d": "#545b62"   # Gris más oscuro
        }
        return color_map.get(base_color, base_color)
    
    def _handle_tag_click(self, category, tag_text, change_type):
        """Maneja el clic en un tag según su tipo"""
        if change_type == "added":
            # Tag verde: guardar automáticamente
            success = self._save_tag_to_json(category, tag_text)
            if success:
                self._show_auto_close_message(f"✅ Tag '{tag_text}' guardado en {category}")
        elif change_type == "removed":
            # Tag rojo: mostrar popup de confirmación
            self._show_tag_action_dialog(category, tag_text)
    
    def _clean_tag_text(self, tag_text):
        """Limpia el texto del tag removiendo símbolos y caracteres especiales"""
        # Remover paréntesis, comas, espacios extra y otros símbolos
        cleaned = tag_text.strip()
        cleaned = cleaned.replace('(', '').replace(')', '')
        cleaned = cleaned.replace(',', '')
        cleaned = cleaned.replace('[', '').replace(']', '')
        cleaned = cleaned.replace('{', '').replace('}', '')
        cleaned = cleaned.strip()
        return cleaned
    
    def _save_tag_to_json(self, category, tag_text):
        """Guarda un tag en el archivo tags.json"""
        try:
            # Limpiar el texto del tag ANTES de todo
            cleaned_tag = self._clean_tag_text(tag_text)
            
            tags_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'tags.json')
            
            # Leer el archivo actual
            with open(tags_file_path, 'r', encoding='utf-8') as f:
                tags_data = json.load(f)
            
            # Normalizar el nombre de la categoría
            normalized_category = category.lower().replace(' ', '_')
            
            # Agregar el tag si no existe
            if normalized_category not in tags_data:
                tags_data[normalized_category] = []
            
            # Verificar duplicados con el texto LIMPIO
            if cleaned_tag not in tags_data[normalized_category]:
                tags_data[normalized_category].append(cleaned_tag)  # Guardar el texto limpio
                
                # Guardar el archivo
                with open(tags_file_path, 'w', encoding='utf-8') as f:
                    json.dump(tags_data, f, indent=2, ensure_ascii=False)
                
                print(f"DEBUG: Tag '{cleaned_tag}' guardado en categoría '{normalized_category}'")
                self._show_auto_close_message(f"✅ Tag '{cleaned_tag}' guardado en {category}")
                return True
            else:
                # Tag ya existe - preguntar si quiere guardarlo de todas formas
                print(f"DEBUG: Tag '{cleaned_tag}' ya existe en '{normalized_category}'")
                return self._ask_duplicate_confirmation(category, cleaned_tag, tags_data, tags_file_path, normalized_category)
                
        except Exception as e:
            print(f"ERROR: No se pudo guardar el tag: {e}")
            self._show_error_message(f"Error al guardar: {e}")
            return False
    
    def _ask_duplicate_confirmation(self, category, tag_text, tags_data, tags_file_path, normalized_category):
        """Pregunta al usuario si quiere guardar un tag duplicado"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle("Tag Duplicado")
        msg_box.setText(f"El tag '{tag_text}' ya existe en la categoría '{category}'.\n\n¿Deseas guardarlo de todas formas?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        result = msg_box.exec()
        
        if result == QMessageBox.StandardButton.Yes:
            # Usuario confirmó - guardar de todas formas (agregar duplicado)
            tags_data[normalized_category].append(tag_text)
            
            try:
                with open(tags_file_path, 'w', encoding='utf-8') as f:
                    json.dump(tags_data, f, indent=2, ensure_ascii=False)
                
                print(f"DEBUG: Tag duplicado '{tag_text}' guardado en categoría '{normalized_category}'")
                self._show_auto_close_message(f"✅ Tag '{tag_text}' guardado en {category} (duplicado)")
                return True
            except Exception as e:
                print(f"ERROR: No se pudo guardar el tag duplicado: {e}")
                self._show_error_message(f"Error al guardar: {e}")
                return False
        else:
            # Usuario canceló - no mostrar ningún mensaje
            print(f"DEBUG: Guardado cancelado para '{tag_text}'")
            return False
    
    def _show_tag_action_dialog(self, category, tag_text):
        """Muestra un diálogo para confirmar la acción en tags eliminados"""
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Acción en Tag")
        msg_box.setText(f"¿Qué desea hacer con el tag '{tag_text}'?")
        msg_box.setInformativeText(f"Categoría: {category}")
        
        # Botones personalizados
        add_button = msg_box.addButton("Agregar a lista", QMessageBox.ButtonRole.AcceptRole)
        remove_button = msg_box.addButton("Eliminar de lista", QMessageBox.ButtonRole.DestructiveRole)
        cancel_button = msg_box.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == add_button:
            success = self._save_tag_to_json(category, tag_text)
            if success:
                self._show_auto_close_message(f"✅ Tag '{tag_text}' agregado a {category}")
        elif msg_box.clickedButton() == remove_button:
            success = self._remove_tag_from_json(category, tag_text)
            if success:
                self._show_auto_close_message(f"🗑️ Tag '{tag_text}' eliminado de {category}")
    
    def _remove_tag_from_json(self, category, tag_text):
        """Elimina un tag del archivo tags.json"""
        try:
            tags_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'tags.json')
            
            # Leer el archivo actual
            with open(tags_file_path, 'r', encoding='utf-8') as f:
                tags_data = json.load(f)
            
            # Normalizar el nombre de la categoría
            normalized_category = category.lower().replace(' ', '_')
            
            # Eliminar el tag si existe
            if normalized_category in tags_data and tag_text in tags_data[normalized_category]:
                tags_data[normalized_category].remove(tag_text)
                
                # Guardar el archivo
                with open(tags_file_path, 'w', encoding='utf-8') as f:
                    json.dump(tags_data, f, indent=2, ensure_ascii=False)
                
                print(f"DEBUG: Tag '{tag_text}' eliminado de categoría '{normalized_category}'")
                return True
            else:
                print(f"DEBUG: Tag '{tag_text}' no encontrado en '{normalized_category}'")
                self._show_auto_close_message(f"⚠️ Tag '{tag_text}' no encontrado en {category}")
                return False
                
        except Exception as e:
            print(f"ERROR: No se pudo eliminar el tag: {e}")
            self._show_error_message(f"Error al eliminar: {e}")
            return False
    
    def _show_tag_action_dialog(self, category, tag_text):
        """Muestra un diálogo para confirmar la acción en tags eliminados"""
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Acción en Tag")
        msg_box.setText(f"¿Qué desea hacer con el tag '{tag_text}'?")
        msg_box.setInformativeText(f"Categoría: {category}")
        
        # Botones personalizados
        add_button = msg_box.addButton("Agregar a lista", QMessageBox.ButtonRole.AcceptRole)
        remove_button = msg_box.addButton("Eliminar de lista", QMessageBox.ButtonRole.DestructiveRole)
        cancel_button = msg_box.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == add_button:
            success = self._save_tag_to_json(category, tag_text)
            if success:
                self._show_auto_close_message(f"✅ Tag '{tag_text}' agregado a {category}")
        elif msg_box.clickedButton() == remove_button:
            success = self._remove_tag_from_json(category, tag_text)
            if success:
                self._show_auto_close_message(f"🗑️ Tag '{tag_text}' eliminado de {category}")
    
    def _remove_tag_from_json(self, category, tag_text):
        """Elimina un tag del archivo tags.json"""
        try:
            tags_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'tags.json')
            
            # Leer el archivo actual
            with open(tags_file_path, 'r', encoding='utf-8') as f:
                tags_data = json.load(f)
            
            # Normalizar el nombre de la categoría
            normalized_category = category.lower().replace(' ', '_')
            
            # Eliminar el tag si existe
            if normalized_category in tags_data and tag_text in tags_data[normalized_category]:
                tags_data[normalized_category].remove(tag_text)
                
                # Guardar el archivo
                with open(tags_file_path, 'w', encoding='utf-8') as f:
                    json.dump(tags_data, f, indent=2, ensure_ascii=False)
                
                print(f"DEBUG: Tag '{tag_text}' eliminado de categoría '{normalized_category}'")
                return True
            else:
                print(f"DEBUG: Tag '{tag_text}' no encontrado en '{normalized_category}'")
                self._show_auto_close_message(f"⚠️ Tag '{tag_text}' no encontrado en {category}")
                return False
                
        except Exception as e:
            print(f"ERROR: No se pudo eliminar el tag: {e}")
            self._show_error_message(f"Error al eliminar: {e}")
            return False
    
    def _show_auto_close_message(self, message):
        """Muestra un mensaje de notificación con botón OK"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("Notificación")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        
        # Mostrar el mensaje
        msg_box.show()
        
        # Timer para cerrar automáticamente después de 2 segundos
        timer = QTimer()
        timer.timeout.connect(msg_box.close)
        timer.setSingleShot(True)
        timer.start(2000)  # 2000 ms = 2 segundos
        
        # Mantener referencia al timer para evitar que sea recolectado por el garbage collector
        msg_box._timer = timer
    
    def _show_error_message(self, message):
        """Muestra un mensaje de error"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.exec()
    
    def _show_error_message(self, message):
        """Muestra un mensaje de error"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.exec()
    
    def get_changes_data(self):
        """Retorna los datos de cambios actuales"""
        return getattr(self, 'changes_data', {})