import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPalette, QColor, QFont
from ui.sidebar import SidebarFrame
from ui.category_grid import CategoryGridFrame
from ui.prompt_section import PromptSectionFrame
from logic.prompt_generator import PromptGenerator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Prompt Studio")
        
        # Configurar tema oscuro
        self.set_dark_theme()
        
        # Inicializar el generador de prompts
        self.prompt_generator = PromptGenerator()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal horizontal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(8)
        
        # Sidebar izquierda
        self.sidebar = SidebarFrame(self.prompt_generator)
        main_layout.addWidget(self.sidebar)
        
        # Contenedor principal para categorías y prompt
        main_container = QWidget()
        main_layout.addWidget(main_container, 1)  # 1 = stretch factor
        
        # Layout vertical para el contenedor principal
        container_layout = QVBoxLayout(main_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(8)
        
        # Sección de categorías
        self.category_grid = CategoryGridFrame(self.prompt_generator)
        container_layout.addWidget(self.category_grid, 2)  # 2 = más espacio para categorías
        
        # Sección de prompt
        self.prompt_section = PromptSectionFrame(self.prompt_generator)
        container_layout.addWidget(self.prompt_section, 1)  # 1 = menos espacio para prompt
        
        # Conectar las señales
        self.connect_signals()
        
        # Configurar tamaño responsivo después de crear todos los widgets
        self.setup_responsive_size()

        self.sidebar.character_defaults_selected.connect(
    self.category_grid.set_defaults_for_character
)

    def setup_responsive_size(self):
        """Configura el tamaño de la ventana de manera responsiva"""
        # Obtener la pantalla disponible
        screen = self.screen()
        screen_geometry = screen.geometry()
        
        # Calcular el tamaño óptimo (80% del ancho y 85% del alto para dejar margen)
        optimal_width = int(screen_geometry.width() * 0.8)
        optimal_height = int(screen_geometry.height() * 0.80)
        
        # Tamaños mínimos
        min_width = 1300
        min_height = 600
        
        # Aplicar restricciones (solo mínimo, sin máximo para permitir maximizar)
        window_width = max(min_width, optimal_width)
        window_height = max(min_height, optimal_height)
        
        # Establecer geometría (solo mínimo)
        self.setMinimumSize(min_width, min_height)
        # Removemos setMaximumSize para permitir maximizar
        self.resize(window_width, window_height)
        
        # Centrar la ventana
        self.center_window()

    def center_window(self):
        """Posiciona la ventana en una posición fija"""
        # Posición fija (x, y) - puedes ajustar estos valores
        x = 40  # Distancia desde el borde izquierdo
        y = 40   # Distancia desde el borde superior
        
        # O si prefieres centrarla horizontalmente pero con Y fijo:
        # screen = self.screen()
        # screen_geometry = screen.geometry()
        # window_geometry = self.geometry()
        # x = (screen_geometry.width() - window_geometry.width()) // 2
        # y = 50  # Posición fija desde arriba
        
        self.move(x, y)

    def set_dark_theme(self):
        """Configura el tema oscuro"""
        palette = QPalette()
        
        # Colores del tema oscuro
        dark_bg = QColor("#1a1a1a")
        dark_secondary = QColor("#252525")
        dark_border = QColor("#404040")
        accent = QColor("#6366f1")
        text_primary = QColor("#e0e0e0")
        text_secondary = QColor("#a0a0a0")
        
        # Configurar colores
        palette.setColor(QPalette.ColorRole.Window, dark_bg)
        palette.setColor(QPalette.ColorRole.WindowText, text_primary)
        palette.setColor(QPalette.ColorRole.Base, dark_secondary)
        palette.setColor(QPalette.ColorRole.AlternateBase, dark_border)
        palette.setColor(QPalette.ColorRole.ToolTipBase, dark_secondary)
        palette.setColor(QPalette.ColorRole.ToolTipText, text_primary)
        palette.setColor(QPalette.ColorRole.Text, text_primary)
        palette.setColor(QPalette.ColorRole.Button, dark_secondary)
        palette.setColor(QPalette.ColorRole.ButtonText, text_primary)
        palette.setColor(QPalette.ColorRole.BrightText, accent)
        palette.setColor(QPalette.ColorRole.Link, accent)
        palette.setColor(QPalette.ColorRole.Highlight, accent)
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        
        self.setPalette(palette)
        
        # Configurar fuente
        font = QFont("Segoe UI", 9)
        self.setFont(font)

    def connect_signals(self):
        """Conecta las señales entre componentes"""
        # Conectar actualización de prompt desde categorías
        self.category_grid.prompt_updated.connect(self.prompt_section.update_prompt)

    def run(self):
        """Muestra la ventana"""
        self.show()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.run()
    sys.exit(app.exec())
