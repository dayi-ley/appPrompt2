import sys
from PyQt6.QtWidgets import QApplication

def main():
    print("Creando QApplication...")
    app = QApplication(sys.argv)
    print("QApplication creada exitosamente")
    
    print("Importando MainWindow...")
    from ui.main_window import MainWindow
    print("MainWindow importada exitosamente")
    
    print("Creando MainWindow...")
    window = MainWindow()
    print("MainWindow creada exitosamente")
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()