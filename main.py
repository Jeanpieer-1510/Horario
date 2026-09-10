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
from PyQt6.QtGui import QFont, QIcon

from app.ui.main_window import MainWindow


def main():
    # Identificador de aplicación para Windows (fuerza ícono en barra de tareas y administrador de tareas)
    try:
        import ctypes
        myappid = 'simclic.horarios.visualizador.v2'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    # Habilitar soporte para HiDPI
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("SimClic")
    app.setApplicationDisplayName("SimClic - Horarios Universitarios")
    app.setOrganizationName("Universidad")

    # Ícono de la aplicación
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ico_path = os.path.join(base_dir, "assets", "app_icon.ico")
    png_path = os.path.join(base_dir, "assets", "app_icon.png")

    app_icon = QIcon()
    if os.path.exists(ico_path):
        app_icon.addFile(ico_path)
    if os.path.exists(png_path):
        app_icon.addFile(png_path)

    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

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
