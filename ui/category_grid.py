import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QLineEdit, QFrame, QScrollArea, QSizePolicy, QPushButton, QInputDialog, QToolButton)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon

CATEGORIES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "categories.json")
TAGS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "tags.json")
ICON_EDIT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", "edit.png")
ICON_SAVE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", "save.png")

def load_categories_and_tags():
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        categories = json.load(f)["categorias"]
    with open(TAGS_PATH, "r", encoding="utf-8") as f:
        tags = json.load(f)
    # Relaciona cada categoría con sus tags (o lista vacía si no hay)
    categories_real = [
        {"name": cat.replace("_", " ").capitalize(), "icon": None, "tags": tags.get(cat, [])}
        for cat in categories
    ]
    return categories_real

DEFAULT_CARD_COLOR = "#252525"

class TagButton(QPushButton):
    def __init__(self, tag, parent_card):
        super().__init__(tag)
        self.tag = tag
        self.parent_card = parent_card
        self.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                border: 1px solid #6366f1;
                border-radius: 12px;
                padding: 4px 8px;
                color: #e0e0e0;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #6366f1;
                color: #fff;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent_card.modify_tag_importance(self.tag, increase=True)
        elif event.button() == Qt.MouseButton.RightButton:
            self.parent_card.modify_tag_importance(self.tag, increase=False)

class CategoryCard(QFrame):
    request_rename = pyqtSignal(str, str)  # (old_name, new_name)
    value_changed = pyqtSignal()  # Nueva señal para cuando cambie el valor

    def __init__(self, name, icon=None, tags=None, prompt_generator=None, bg_color=DEFAULT_CARD_COLOR):
        super().__init__()
        self.prompt_generator = prompt_generator
        self.category_name = name
        self.bg_color = bg_color
        self.icon = icon
        self.is_editing = False
        self.unsaved_changes = False
        self.tags = tags or []
        self.setup_ui(name, tags)
        self.setup_styles()
        self.setup_debounce()

    def setup_ui(self, name, tags):
        """Configura la interfaz de la tarjeta"""
        # Hacer la tarjeta responsiva
        self.setMinimumSize(300, 100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)
        
        # --- Título con icono e ícono de editar/guardar ---
        title_layout = QHBoxLayout()
        title_layout.setSpacing(6)
    
        # Icono pequeño a la izquierda SOLO para "Angulo"
        icon_label = QLabel()
        icon_label.setFixedSize(20, 20)
        if name.strip().lower() == "angulo":
            angle_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", "angle.png")
            icon_label.setPixmap(QPixmap(angle_icon_path).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        title_layout.addWidget(icon_label)
    
        # Título de la categoría (editable solo si is_editing)
        self.title_label = QLabel(name)
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("color: #e0e0e0;")  # Asegura que el texto sea visible
        title_layout.addWidget(self.title_label, 1)
    
        # Campo de edición oculto por defecto
        self.title_edit = QLineEdit(name)
        self.title_edit.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.title_edit.hide()
        self.title_edit.returnPressed.connect(self.save_category_name)
        self.title_edit.textChanged.connect(self.on_title_edited)
        title_layout.addWidget(self.title_edit, 1)
    
        # Botón de editar/guardar
        self.edit_btn = QToolButton()
        self.edit_btn.setIcon(QIcon(ICON_EDIT))
        self.edit_btn.setToolTip("Editar nombre de la categoría")
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_btn.setFixedSize(22, 22)
        self.edit_btn.clicked.connect(self.toggle_edit_mode)
        title_layout.addWidget(self.edit_btn)
    
        layout.addLayout(title_layout)
        
        # Input para el valor
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Añadir valor...")
        self.input_field.textChanged.connect(self.on_input_change)
        layout.addWidget(self.input_field)
        
        # Guardar los tags para poder actualizarlos después
        self.tags = tags or []
        self.tag_click_counts = {}
        
        # Crear la interfaz de tags
        self.update_tags_ui()

    def update_tags_ui(self, tags=None):
        """Actualiza la interfaz de los tags en la tarjeta"""
        # Limpiar el layout de tags existente
        layout = self.layout()
        
        # Buscar el layout de tags (último layout en la tarjeta)
        # Pero asegurarse de no eliminar el layout del título
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            # Solo eliminar el layout de tags, no el del título ni el input
            if isinstance(item, QHBoxLayout) and i > 1:  # El título está en la posición 0, el input en 1
                tags_layout = item
                # Limpiar este layout
                while tags_layout.count():
                    widget_item = tags_layout.takeAt(0)
                    if widget_item.widget():
                        widget_item.widget().setParent(None)
                # Eliminar el layout vacío
                layout.removeItem(tags_layout)
                break
        
        # Crear nuevo layout para los tags
        tags_layout = QHBoxLayout()
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.setSpacing(6)
        
        # Si se proporcionan nuevos tags, actualizar la lista interna
        if tags is not None:
            self.tags = tags
            
        # Recrear los botones de tags
        self.tag_click_counts = {}
        if self.tags:
            # Solo muestra los dos primeros tags
            for tag in self.tags[:2]:
                btn = TagButton(tag, self)
                tags_layout.addWidget(btn)
                self.tag_click_counts[tag] = 0
    
            # Botón "ver tags"
            view_tags_btn = QPushButton("ver tags")
            view_tags_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6366f1;
                    color: #fff;
                    border-radius: 10px;
                    padding: 2px 10px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #4f46e5;
                }
            """)
            view_tags_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            view_tags_btn.clicked.connect(self.show_tags_dialog)
            tags_layout.addWidget(view_tags_btn)
    
        tags_layout.addStretch()
        layout.addLayout(tags_layout)

    def show_tags_dialog(self):
        import json
        import os
        from .tags_dialog import TagsDialog

        TAGS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "tags.json")
        key = self.category_name.lower().replace(" ", "_")
        with open(TAGS_PATH, "r", encoding="utf-8") as f:
            tags_data = json.load(f)
            tags = tags_data.get(key, [])
        dlg = TagsDialog(self.category_name, tags, self)
        if dlg.exec():
            # Si el diálogo se cerró con aceptar, actualizar los tags en la UI
            self.update_tags_ui(tags)

    def setup_styles(self):
        """Configura los estilos de la tarjeta"""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.bg_color};
                border: 1px solid #404040;
                border-radius: 8px;
            }}
            QLineEdit {{
                background-color: #1a1a1a;
                border: 1px solid #404040;
                border-radius: 6px;
                color: #e0e0e0;
                padding: 6px;
                font-size: 11px;
            }}
            QLineEdit:focus {{
                border: 1px solid #6366f1;
            }}
            QLabel {{
                color: #e0e0e0;
            }}
        """)

    def setup_debounce(self):
        """Configura el debounce para el input"""
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.update_prompt)

    def on_input_change(self):
        """Maneja cambios en el input con debounce"""
        self.debounce_timer.start(500)  # 500ms debounce

    def update_prompt(self):
        """Actualiza el prompt basado en el valor del input"""
        if not self.prompt_generator:
            return
        
        value = self.input_field.text()
        if self.prompt_generator:
            validated_value = self.prompt_generator.validate_input(value)
            self.prompt_generator.update_category(self.category_name, validated_value)
            self.value_changed.emit()  # Emitir señal cuando cambie el valor

    def toggle_edit_mode(self):
        if not self.is_editing:
            # Cambia a modo edición
            self.is_editing = True
            self.unsaved_changes = False
            self.title_label.hide()
            self.title_edit.show()
            self.title_edit.setFocus()
            self.edit_btn.setIcon(QIcon(ICON_SAVE))
            self.edit_btn.setToolTip("Guardar nombre de la categoría")
            self.title_edit.setStyleSheet("")  # Quita subrayado si lo hubiera
        else:
            # Intenta guardar
            self.save_category_name()

    def save_category_name(self):
        new_name = self.title_edit.text().strip()
        if new_name and new_name != self.category_name:
            self.request_rename.emit(self.category_name, new_name)
        self.is_editing = False
        self.unsaved_changes = False
        self.title_label.setText(new_name)
        self.category_name = new_name
        self.title_label.show()
        self.title_edit.hide()
        self.edit_btn.setIcon(QIcon(ICON_EDIT))
        self.edit_btn.setToolTip("Editar nombre de la categoría")
        self.title_edit.setStyleSheet("")

    def on_title_edited(self):
        # Si el usuario edita pero no guarda, subraya en rojo
        if self.title_edit.text().strip() != self.category_name:
            self.unsaved_changes = True
            self.title_edit.setStyleSheet("border-bottom: 2px solid red;")
        else:
            self.unsaved_changes = False
            self.title_edit.setStyleSheet("")

    def modify_tag_importance(self, tag, increase=True):
        count = self.tag_click_counts.get(tag, 0)
        if increase:
            count += 1
        else:
            count -= 1
        count = max(0, count)
        self.tag_click_counts[tag] = count

        import re
        # Quita versiones anteriores del tag en el input_field
        current = self.input_field.text()
        pattern = re.compile(rf"\(*\s*{re.escape(tag)}\s*\)*,")
        current = pattern.sub("", current).strip()

        # Si la importancia es 0, no agregues el tag
        if count > 0:
            tag_text = f"{'(' * count}{tag}{')' * count},"
            if current:
                new_text = f"{current} {tag_text}"
            else:
                new_text = tag_text
            self.input_field.setText(new_text.strip())
        else:
            self.input_field.setText(current)

    def show_tags_dialog(self):
        import json
        import os
        from .tags_dialog import TagsDialog

        TAGS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "tags.json")
        key = self.category_name.lower().replace(" ", "_")
        with open(TAGS_PATH, "r", encoding="utf-8") as f:
            tags_data = json.load(f)
            tags = tags_data.get(key, [])
        dlg = TagsDialog(self.category_name, tags, self)
        dlg.exec()

class CategoryGridFrame(QWidget):
    prompt_updated = pyqtSignal(str)
    
    def __init__(self, prompt_generator):
        super().__init__()
        self.prompt_generator = prompt_generator
        
        self.setup_ui()
        self.setup_styles()
        self.create_cards()

    def setup_ui(self):
        """Configura la interfaz del grid"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 0, 16, 16)
        self.main_layout.setSpacing(0)
        
        # --- Buscador ---
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Buscar categoría...")
        self.search_box.textChanged.connect(self.filter_cards)
        self.main_layout.addWidget(self.search_box)

        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Widget contenedor para el grid
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(8)
        
        # Configurar el grid para ser responsivo
        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setColumnStretch(1, 1)
        self.grid_layout.setColumnStretch(2, 1)
        
        self.scroll_area.setWidget(self.grid_widget)
        self.main_layout.addWidget(self.scroll_area)


    def setup_styles(self):
        """Configura los estilos del grid"""
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 8px;
            }
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #6366f1;
                border-radius: 6px;
                color: #e0e0e0;
                padding: 6px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1.5px solid #a5b4fc;
                background-color: #353535;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #252525;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #404040;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #6366f1;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

    @staticmethod
    def normalize_category(name):
        return name.lower().replace(" ", "").replace("(", "").replace(")", "").replace("_", "")

    def create_cards(self):
        self.cards = []
        categories = load_categories_and_tags()
        for idx, cat in enumerate(categories):
            row = idx // 3
            col = idx % 3
            card = CategoryCard(
                name=cat["name"],
                icon=cat["icon"],
                tags=cat["tags"],
                prompt_generator=self.prompt_generator,
                bg_color=DEFAULT_CARD_COLOR
            )
            card.request_rename.connect(self.rename_category)
            card.value_changed.connect(self.on_card_update)  # Conectar nueva señal
            self.grid_layout.addWidget(card, row, col)
            self.cards.append(card)
        # Agrega la tarjeta especial al final
        add_row = len(categories) // 3
        add_col = len(categories) % 3
        add_card = AddCategoryCard(self.show_add_category_dialog)
        self.grid_layout.addWidget(add_card, add_row, add_col)

    def on_card_update(self):
        """Maneja la actualización de una tarjeta"""
        if self.prompt_generator:
            new_prompt = self.prompt_generator.generate_prompt()
            self.prompt_updated.emit(new_prompt)

    def set_defaults_for_character(self, defaults_dict):
        """Llena los QLineEdit de las tarjetas con los valores por defecto del personaje"""
        def normalize(name):
            return name.lower().replace(" ", "").replace("(", "").replace(")", "").replace("_", "")
        for i in range(self.grid_layout.count()):
            card = self.grid_layout.itemAt(i).widget()
            if not card or not isinstance(card, CategoryCard):
                continue
            card_norm = normalize(card.category_name)
            for key, value in defaults_dict.items():
                if normalize(key) == card_norm:
                    card.input_field.setText(value)
                    # Actualizar el prompt_generator directamente sin validate_input para preservar símbolos
                    if self.prompt_generator:
                        self.prompt_generator.update_category(card.category_name, value)
                    break
        
        # Emitir señal para actualizar el prompt después de cargar todos los valores
        self.on_card_update()

    def show_add_category_dialog(self):
        name, ok = QInputDialog.getText(self, "Nueva categoría", "Nombre de la categoría:")
        if ok and name:
            tags, ok2 = QInputDialog.getText(self, "Tags", "Tags separados por coma:")
            if ok2:
                self.add_custom_category(name, [t.strip() for t in tags.split(",") if t.strip()])

    def add_custom_category(self, name, tags):
        # Actualiza categories.json
        with open(CATEGORIES_PATH, "r+", encoding="utf-8") as f:
            data = json.load(f)
            if name not in data["categorias"]:
                data["categorias"].append(name)
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.truncate()
        # Actualiza tags.json
        with open(TAGS_PATH, "r+", encoding="utf-8") as f:
            tags_data = json.load(f)
            tags_data[name] = tags
            f.seek(0)
            json.dump(tags_data, f, ensure_ascii=False, indent=2)
            f.truncate()
        self.reload_categories()

    def reload_categories(self):
        # Limpia el grid y vuelve a cargar las categorías
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        # Recarga los datos y vuelve a crear las tarjetas
        self.create_cards()

    def rename_category(self, old_name, new_name):
        # Normaliza los nombres para buscar en el JSON
        old_key = old_name.replace(" ", "_").lower()
        new_key = new_name.replace(" ", "_").lower()

        # Actualiza categories.json
        with open(CATEGORIES_PATH, "r+", encoding="utf-8") as f:
            data = json.load(f)
            if old_key in data["categorias"]:
                data["categorias"].remove(old_key)
            if new_key not in data["categorias"]:
                data["categorias"].append(new_key)
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()

        # Actualiza tags.json (renombra la clave si existe)
        with open(TAGS_PATH, "r+", encoding="utf-8") as f:
            tags_data = json.load(f)
            if old_key in tags_data:
                tags_data[new_key] = tags_data.pop(old_key)
            f.seek(0)
            json.dump(tags_data, f, ensure_ascii=False, indent=2)
            f.truncate()

        self.reload_categories()
        
        
    def filter_cards(self, text):
        text = text.lower().strip()
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            # Solo filtra CategoryCard, no la tarjeta de agregar
            if isinstance(widget, CategoryCard):
                visible = text in widget.category_name.lower()
                widget.setVisible(visible)
            elif isinstance(widget, AddCategoryCard):
                # Siempre muestra la tarjeta de agregar si no hay filtro, o si hay coincidencias
                widget.setVisible(text == "" or any(
                    w.isVisible() for w in self.cards
                ))    

class AddCategoryCard(QFrame):
    def __init__(self, on_add_callback):
        super().__init__()
        self.setMinimumSize(300, 100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("""
            QFrame {
                background-color: #7c3aed;
                border: 2px dashed #fff;
                border-radius: 8px;
            }
            QLabel {
                color: #fff;
                font-size: 48px;
                font-weight: bold;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        plus_label = QLabel("+")
        plus_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(plus_label)
        self.mousePressEvent = lambda event: on_add_callback()

