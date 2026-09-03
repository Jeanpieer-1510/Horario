"""
SimClic - Aplicación de Horarios Universitarios
Punto de entrada principal.
"""
import sys
import os

# Asegurar que el directorio raíz está en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.ui.main_window import MainWindow


def main():
    # Habilitar soporte para HiDPI
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("SimClic")
    app.setApplicationDisplayName("SimClic - Horarios Universitarios")
    app.setOrganizationName("Universidad")

    # Fuente global
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Estilo oscuro global
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
