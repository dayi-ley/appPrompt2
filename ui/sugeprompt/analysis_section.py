from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QTextEdit, QScrollArea
)
from PyQt6.QtCore import Qt

class AnalysisSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)
        
        # Título pequeño
        title = QLabel("Análisis y Generación")
        title.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #e0e0e0;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(title)
        
        # Layout horizontal para dividir en dos partes
        main_horizontal = QHBoxLayout()
        main_horizontal.setSpacing(10)
        
        # PARTE IZQUIERDA: Sugerencias de Prompts
        left_frame = self.create_suggestions_section()
        main_horizontal.addWidget(left_frame, 2)  # 2/3 del espacio
        
        # PARTE DERECHA: Generación de Prompt
        right_frame = self.create_prompt_generation_section()
        main_horizontal.addWidget(right_frame, 1)  # 1/3 del espacio
        
        layout.addLayout(main_horizontal)
    
    def create_suggestions_section(self):
        """Crea la sección izquierda para sugerencias de prompts"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #383838;
                border: 1px solid #555;
                border-radius: 6px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Subtítulo
        subtitle = QLabel("Sugerencias de Prompts")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-weight: bold;
                color: #e0e0e0;
                margin-bottom: 3px;
            }
        """)
        layout.addWidget(subtitle)
        
        # Área de scroll para las columnas de sugerencias
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2b2b2b;
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
        
        # Contenido de sugerencias (TODO)
        suggestions_content = QWidget()
        suggestions_layout = QVBoxLayout(suggestions_content)
        
        # TODO: Implementar columnas de sugerencias
        todo_label = QLabel("TODO: Implementar columnas de sugerencias\n\nAquí aparecerán:\n• Columna 1: Sugerencias básicas\n• Columna 2: Sugerencias avanzadas\n• Columna 3: Sugerencias contextuales")
        todo_label.setStyleSheet("""
            QLabel {
                color: #ffa500;
                font-size: 10px;
                padding: 15px;
                background-color: #4a4a4a;
                border: 1px dashed #666;
                border-radius: 4px;
            }
        """)
        suggestions_layout.addWidget(todo_label)
        suggestions_layout.addStretch()
        
        scroll_area.setWidget(suggestions_content)
        layout.addWidget(scroll_area)
        
        return frame
    
    def create_prompt_generation_section(self):
        """Crea la sección derecha para generación de prompt"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #383838;
                border: 1px solid #555;
                border-radius: 6px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Subtítulo
        subtitle = QLabel("Generación de Prompt")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-weight: bold;
                color: #e0e0e0;
                margin-bottom: 3px;
            }
        """)
        layout.addWidget(subtitle)
        
        # Área de texto para el prompt generado
        self.prompt_text = QTextEdit()
        self.prompt_text.setPlaceholderText("El prompt generado aparecerá aquí...")
        self.prompt_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
                font-size: 10px;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        self.prompt_text.setMaximumHeight(120)
        layout.addWidget(self.prompt_text)
        
        # Contenedor para los 4 botones pequeños
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(4)
        
        # Los 4 botones pequeños
        button_names = ["Copiar", "Guardar", "Limpiar", "Generar"]
        self.action_buttons = {}
        
        for button_name in button_names:
            button = QPushButton(button_name)
            button.setMaximumHeight(25)
            button.clicked.connect(lambda checked, name=button_name: self.on_action_button_clicked(name))
            button.setStyleSheet("""
                QPushButton {
                    background-color: #404040;
                    color: #e0e0e0;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #505050;
                    border-color: #666;
                }
                QPushButton:pressed {
                    background-color: #606060;
                }
            """)
            
            self.action_buttons[button_name] = button
            buttons_layout.addWidget(button)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        return frame
    
    def on_action_button_clicked(self, action):
        """Maneja los clics en los botones de acción - TODO: Implementar funcionalidades"""
        print(f"TODO: Implementar acción '{action}' para el prompt")
        
        if action == "Limpiar":
            self.prompt_text.clear()
        elif action == "Generar":
            # TODO: Implementar generación de prompt
            self.prompt_text.setPlainText("TODO: Generar prompt basado en selecciones...")
        
        layout.addStretch()