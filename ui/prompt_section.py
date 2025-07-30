from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QFrame, QSizePolicy, QFileDialog)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
import pyperclip
import json
import os
from datetime import datetime
from config.settings import AppSettings

class PromptSectionFrame(QFrame):
    def __init__(self, prompt_generator):
        super().__init__()
        self.prompt_generator = prompt_generator
        self.settings = AppSettings()
        
        self.setup_ui()
        self.setup_styles()
        self.setup_shortcuts()

    def setup_ui(self):
        """Configura la interfaz de la sección de prompt"""
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)  # Reducido de 16 a 12
        layout.setSpacing(8)  # Reducido de 10 a 8
        
        # Título - tamaño reducido
        title_label = QLabel("Prompt generado")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))  # Reducido de 14 a 12
        layout.addWidget(title_label)
        
        # Textarea para el prompt - altura y fuente reducidas
        self.prompt_text = QTextEdit()
        self.prompt_text.setFixedHeight(80)  # Reducido de 120 a 80
        self.prompt_text.setFont(QFont("Courier New", 10))  # Reducido de 11 a 10
        self.prompt_text.setPlaceholderText("Aquí aparecerá el prompt generado...")
        self.prompt_text.setReadOnly(False)  # Permitir edición manual
        layout.addWidget(self.prompt_text)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)  # Reducido de 10 a 8
        
        self.copy_btn = QPushButton("Copiar")
        self.copy_btn.setFixedSize(100, 32)
        self.copy_btn.clicked.connect(self.copy_prompt)
        buttons_layout.addWidget(self.copy_btn)
        
        self.save_btn = QPushButton("Guardar")
        self.save_btn.setFixedSize(100, 32)
        self.save_btn.clicked.connect(self.save_prompt)
        buttons_layout.addWidget(self.save_btn)
        
        self.export_btn = QPushButton("Exportar")
        self.export_btn.setFixedSize(100, 32)
        self.export_btn.clicked.connect(self.export_prompt)
        buttons_layout.addWidget(self.export_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Sección de negative prompt
        self.setup_negative_prompt(layout)

    def setup_negative_prompt(self, layout):
        """Configura la sección de negative prompt colapsable"""
        # Frame para negative prompt
        self.negative_frame = QFrame()
        negative_layout = QVBoxLayout(self.negative_frame)
        negative_layout.setContentsMargins(0, 0, 0, 0)
        negative_layout.setSpacing(4)  # Reducido de 6 a 4
        
        # Botón para expandir/contraer
        self.negative_toggle = QPushButton("Negative Prompt ►")
        self.negative_toggle.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #e0e0e0;
                font-weight: bold;
                font-size: 11px;  /* Reducido de 12px a 11px */
                text-align: left;
                padding: 6px;  /* Reducido de 8px a 6px */
            }
            QPushButton:hover {
                background-color: #252525;
                border-radius: 6px;
            }
        """)
        self.negative_toggle.clicked.connect(self.toggle_negative)
        negative_layout.addWidget(self.negative_toggle)
        
        # Textarea para negative prompt - altura reducida
        self.negative_text = QTextEdit()
        self.negative_text.setFixedHeight(60)  # Reducido de 80 a 60
        self.negative_text.setFont(QFont("Courier New", 9))  # Reducido de 10 a 9
        default_negative = self.settings.get_setting("default_negative_prompt", 
                                                   "blurry, low quality, distorted, deformed, ugly, bad anatomy")
        self.negative_text.setPlainText(default_negative)
        negative_layout.addWidget(self.negative_text)
        
        # Inicialmente oculto
        self.negative_text.hide()
        self.negative_expanded = False
        
        layout.addWidget(self.negative_frame)

    def setup_styles(self):
        """Configura los estilos de la sección"""
        self.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border: 1px solid #404040;
                border-radius: 8px;
            }
            QTextEdit {
                background-color: #1a1a1a;
                border: 1px solid #404040;
                border-radius: 6px;
                color: #e0e0e0;
                padding: 8px;
            }
            QTextEdit:focus {
                border: 1px solid #6366f1;
            }
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
            QPushButton:pressed {
                background-color: #3730a3;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)

    def setup_shortcuts(self):
        """Configura los atajos de teclado"""
        # Ctrl+C para copiar
        copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        copy_shortcut.activated.connect(self.copy_prompt)
        
        # Ctrl+S para guardar
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_prompt)
        
        # Ctrl+E para exportar
        export_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        export_shortcut.activated.connect(self.export_prompt)

    def toggle_negative(self):
        """Alterna la visibilidad del negative prompt"""
        if self.negative_expanded:
            self.negative_text.hide()
            self.negative_toggle.setText("Negative Prompt ►")
            self.negative_expanded = False
        else:
            self.negative_text.show()
            self.negative_toggle.setText("Negative Prompt ▼")
            self.negative_expanded = True

    def copy_prompt(self):
        """Copia el prompt al portapapeles"""
        prompt_content = self.prompt_text.toPlainText()
        if prompt_content and prompt_content != "Aquí aparecerá el prompt generado...":
            pyperclip.copy(prompt_content)
            self.show_feedback(self.copy_btn, "¡Copiado!")

    def save_prompt(self):
        """Guarda el prompt en el historial"""
        prompt_content = self.prompt_text.toPlainText()
        negative_content = self.negative_text.toPlainText()
        
        if prompt_content and prompt_content != "Aquí aparecerá el prompt generado...":
            self.settings.add_prompt_to_history(prompt_content, negative_content)
            self.show_feedback(self.save_btn, "¡Guardado!")

    def export_prompt(self):
        """Exporta el prompt en formato TXT con diálogo de guardado"""
        prompt_content = self.prompt_text.toPlainText()
        negative_content = self.negative_text.toPlainText()
        
        if prompt_content and prompt_content != "Aquí aparecerá el prompt generado...":
            try:
                # Generar nombre de archivo por defecto
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                default_filename = f"prompt_export_{timestamp}.txt"
                
                # Mostrar diálogo de guardado
                filename, _ = QFileDialog.getSaveFileName(
                    self,
                    "Exportar Prompt",
                    default_filename,
                    "Archivos de texto (*.txt);;Todos los archivos (*.*)"
                )
                
                if filename:  # Si el usuario no canceló
                    # Asegurar que tenga extensión .txt
                    if not filename.lower().endswith('.txt'):
                        filename += '.txt'
                    
                    # Escribir el archivo
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"Prompt: {prompt_content}\n\n")
                        if negative_content:
                            f.write(f"Negative Prompt: {negative_content}\n\n")
                        f.write(f"Exportado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    
                    self.show_feedback(self.export_btn, "¡Exportado!")
                    print(f"Prompt exportado a: {filename}")
                
            except Exception as e:
                print(f"Error al exportar: {e}")
                self.show_feedback(self.export_btn, "Error", error=True)

    def show_feedback(self, button, text, error=False):
        """Muestra feedback visual en un botón"""
        original_text = button.text()
        original_style = button.styleSheet()
        
        if error:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 11px;
                }
            """)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #10b981;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 11px;
                }
            """)
        
        button.setText(text)
        
        # Restaurar después de 2 segundos
        QTimer.singleShot(2000, lambda: self.restore_button(button, original_text, original_style))

    def restore_button(self, button, text, style):
        """Restaura el estado original de un botón"""
        button.setText(text)
        button.setStyleSheet(style)

    def update_prompt(self, prompt_text):
        """Actualiza el prompt generado"""
        if prompt_text:
            self.prompt_text.setPlainText(prompt_text)
        else:
            self.prompt_text.setPlainText("Aquí aparecerá el prompt generado...")

    def get_negative_prompt(self):
        """Obtiene el contenido del negative prompt"""
        return self.negative_text.toPlainText()
