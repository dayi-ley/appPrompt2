# UI Elements para PyQt6
# Este archivo contiene widgets personalizados para PyQt6

from PyQt6.QtWidgets import QLabel, QPushButton, QFrame, QLineEdit, QComboBox, QTextEdit
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

class CustomLabel(QLabel):
    """Label personalizado con estilos consistentes"""
    def __init__(self, text="", parent=None, **kwargs):
        super().__init__(text, parent)
        self.setup_styles()
        
    def setup_styles(self):
        self.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-family: 'Segoe UI';
            }
        """)

class CustomButton(QPushButton):
    """Botón personalizado con estilos consistentes"""
    def __init__(self, text="", parent=None, **kwargs):
        super().__init__(text, parent)
        self.setup_styles()
        
    def setup_styles(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
            QPushButton:pressed {
                background-color: #3730a3;
            }
        """)

class CustomFrame(QFrame):
    """Frame personalizado con estilos consistentes"""
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.setup_styles()
        
    def setup_styles(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border: 1px solid #404040;
                border-radius: 8px;
            }
        """)

class CustomInput(QLineEdit):
    """Input personalizado con estilos consistentes"""
    def __init__(self, parent=None, placeholder="", **kwargs):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setup_styles()
        
    def setup_styles(self):
        self.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                border: 1px solid #404040;
                border-radius: 6px;
                color: #e0e0e0;
                padding: 6px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 1px solid #6366f1;
            }
        """)

class CustomDropdown(QComboBox):
    """Dropdown personalizado con estilos consistentes"""
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.setup_styles()
        
    def setup_styles(self):
        self.setStyleSheet("""
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

class CustomTextEdit(QTextEdit):
    """TextEdit personalizado con estilos consistentes"""
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.setup_styles()
        
    def setup_styles(self):
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                border: 1px solid #404040;
                border-radius: 6px;
                color: #e0e0e0;
                padding: 8px;
                font-family: 'Courier New';
                font-size: 11px;
            }
            QTextEdit:focus {
                border: 1px solid #6366f1;
            }
        """)

class TagChip(QLabel):
    """Chip de tag personalizado"""
    def __init__(self, text="", parent=None, **kwargs):
        super().__init__(text, parent)
        self.setup_styles()
        
    def setup_styles(self):
        self.setStyleSheet("""
            QLabel {
                background-color: #404040;
                border: 1px solid #6366f1;
                border-radius: 12px;
                padding: 4px 8px;
                color: #e0e0e0;
                font-size: 10px;
            }
        """)
