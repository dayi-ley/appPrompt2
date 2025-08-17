from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt

class ResultsSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)
        
        # Título pequeño
        title = QLabel("Historial y Resultados")
        title.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #e0e0e0;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(title)
        
        # Área de resultados
        results_frame = QFrame()
        results_frame.setStyleSheet("""
            QFrame {
                background-color: #383838;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        
        results_layout = QVBoxLayout(results_frame)
        
        # TODO: Implementar historial de prompts generados
        todo_label = QLabel("TODO: Implementar historial de prompts\n\nAquí se mostrarán:\n• Prompts generados anteriormente\n• Configuraciones guardadas\n• Resultados favoritos")
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
        results_layout.addWidget(todo_label)
        
        layout.addWidget(results_frame)
        layout.addStretch()