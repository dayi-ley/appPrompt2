from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class VariationChangesWidget(QWidget):
    # Señal para cuando se actualicen los cambios
    changes_updated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.changes_data = {}  # Almacenará los cambios detectados
        self.setup_ui()
    
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
    
    def load_changes(self):
        """Carga y muestra los cambios detectados"""
        # TODO: Aquí implementaremos la lógica para detectar cambios
        # Por ahora, simulamos algunos cambios para mostrar la interfaz
        
        # Limpiar el layout actual
        self.clear_changes_display()
        
        # Simular algunos cambios detectados (esto se reemplazará con lógica real)
        sample_changes = {
            "Apariencia": ["Agregado: cabello largo", "Modificado: ojos azules → ojos verdes"],
            "Personalidad": ["Eliminado: tímida", "Agregado: extrovertida"],
            "Vestimenta": ["Modificado: vestido rojo → vestido azul"]
        }
        
        if sample_changes:
            self.display_changes(sample_changes)
        else:
            self.show_no_changes()
        
        # Emitir señal de que se actualizaron los cambios
        self.changes_updated.emit()
    
    def clear_changes_display(self):
        """Limpia la visualización actual de cambios"""
        while self.changes_layout.count():
            child = self.changes_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def display_changes(self, changes_dict):
        """Muestra los cambios detectados"""
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
            
            # Lista de cambios
            for change in changes:
                change_label = QLabel(f"  • {change}")
                change_label.setStyleSheet("color: #ccc; font-size: 9px; padding-left: 10px;")
                change_label.setWordWrap(True)
                category_layout.addWidget(change_label)
            
            self.changes_layout.addWidget(category_frame)
        
        self.changes_layout.addStretch()
    
    def show_no_changes(self):
        """Muestra mensaje cuando no hay cambios"""
        self.no_changes_label = QLabel("No se detectaron cambios en las categorías.")
        self.no_changes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_changes_label.setStyleSheet("""
            color: #888;
            font-style: italic;
            font-size: 11px;
            padding: 20px;
        """)
        self.changes_layout.addWidget(self.no_changes_label)
    
    def get_changes_data(self):
        """Retorna los datos de cambios actuales"""
        return self.changes_data