import json
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal

class CategorySection(QWidget):
    category_selected = pyqtSignal(str)  # Señal para cuando se selecciona una categoría
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_category = None
        self.category_buttons = {}
        self.category_mapping = {}
        self.load_categories()
        self.setup_ui()
    
    def load_categories(self):
        """Carga las categorías dinámicamente desde el archivo JSON"""
        try:
            # Construir ruta al archivo JSON
            current_dir = os.path.dirname(__file__)
            categories_path = os.path.join(current_dir, '..', '..', 'data', 'sugeprompt', 'prompt_categories.json')
            categories_path = os.path.normpath(categories_path)
            
            with open(categories_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Crear mapeo dinámico desde el JSON
            for category_id, category_data in data['categorias'].items():
                # Solo agregar categorías que tengan label en español
                if 'label' in category_data and 'es' in category_data['label']:
                    display_name = category_data['label']['es']
                    self.category_mapping[display_name] = category_id
                else:
                    # Para categorías sin label, usar el ID como nombre
                    display_name = category_id.replace('_', ' ').title()
                    self.category_mapping[display_name] = category_id
                    
            print(f"Categorías cargadas: {list(self.category_mapping.keys())}")
            
        except Exception as e:
            print(f"Error cargando categorías: {e}")
            # Fallback a categorías por defecto si hay error
            self.category_mapping = {
                "Vestuario General": "vestuario_general",
                "Vestuario Superior": "vestuario_superior", 
                "Vestuario Inferior": "vestuario_inferior",
                "Ángulos de Cámara": "angulos_camara",
                "Poses": "poses",
                "Cuerpo": "cuerpo",
                "Expresiones": "expresiones"
            }
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)
        
        # Título pequeño
        title = QLabel("Categorías")
        title.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #e0e0e0;
                margin-bottom: 3px;
            }
        """)
        layout.addWidget(title)
        
        # Contenedor para los botones
        buttons_container = QFrame()
        buttons_container.setMaximumHeight(60)
        buttons_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        
        # Layout horizontal para los botones
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(8)
        
        # Crear botones dinámicamente basado en self.category_mapping
        for display_name, category_id in self.category_mapping.items():
            button = QPushButton(display_name)
            button.setMaximumHeight(35)
            button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            button.clicked.connect(lambda checked, cat_id=category_id, name=display_name: self.on_category_clicked(cat_id, name))
            button.setStyleSheet("""
                QPushButton {
                    background-color: #6a4c93;
                    color: #ffffff;
                    border: 1px solid #8b5fbf;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 10px;
                    font-weight: bold;
                    text-align: center;
                    min-width: 0px;
                }
                QPushButton:hover {
                    background-color: #7a5ca3;
                    border-color: #9b6fcf;
                }
                QPushButton:pressed {
                    background-color: #5a3c83;
                }
                QPushButton:checked {
                    background-color: #28a745;
                    border-color: #34ce57;
                    color: #ffffff;
                }
            """)
            button.setCheckable(True)
            
            self.category_buttons[display_name] = button
            buttons_layout.addWidget(button)
        
        buttons_layout.addStretch()
        layout.addWidget(buttons_container)
    
    def on_category_clicked(self, category_id, display_name):
        """Maneja el clic en una categoría"""
        # Desmarcar otros botones
        for name, btn in self.category_buttons.items():
            btn.setChecked(name == display_name)
        
        self.selected_category = category_id
        self.category_selected.emit(category_id)  # Enviar el ID interno
        print(f"Categoría seleccionada: {display_name} (ID: {category_id})")