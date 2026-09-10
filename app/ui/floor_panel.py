"""
Panel inferior con selector de vistas y pisos:
- Horario Piso 1 (Línea de tiempo)
- Horario Piso 2 (Línea de tiempo)
- Croquis Piso 1 (Mapa interactivo)
- Croquis Piso 2 (Mapa interactivo)
"""
from typing import List, Optional

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QFrame, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal

from app.models.schedule import ClassSession


class FloorPanel(QWidget):
    """
    Barra inferior con pestañas para Línea de Tiempo y Croquis interactivo.
    Emite view_changed('horario_p1' | 'horario_p2' | 'croquis_p1' | 'croquis_p2').
    """
    view_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_view = "horario_p1"
        self._sessions: List[ClassSession] = []
        self._setup_ui()

    def _setup_ui(self):
        self.setFixedHeight(46)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 6)
        layout.setSpacing(10)

        self.setStyleSheet("""
            FloorPanel {
                background: #F1F5F9;
                border-top: 1px solid #CBD5E1;
            }
        """)

        # Etiqueta indicadora
        lbl_vistas = QLabel("VISTAS:")
        lbl_vistas.setStyleSheet("""
            color: #64748B;
            font-family: 'Segoe UI';
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(lbl_vistas)

        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)

        tab_style = """
            QPushButton {
                background: #E2E8F0;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 5px 16px;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: 600;
                min-height: 22px;
            }
            QPushButton:hover {
                background: #DBEAFE;
                color: #1E40AF;
                border-color: #93C5FD;
            }
            QPushButton:checked {
                background: #2563EB;
                color: #FFFFFF;
                border: 1px solid #1D4ED8;
                font-weight: 700;
            }
        """

        # 1. Horario Piso 1
        self._btn_h_p1 = QPushButton("📅  HORARIO PISO 1")
        self._btn_h_p1.setCheckable(True)
        self._btn_h_p1.setChecked(True)
        self._btn_h_p1.setStyleSheet(tab_style)
        self._btn_h_p1.clicked.connect(lambda: self._on_tab_clicked("horario_p1"))
        self._btn_group.addButton(self._btn_h_p1)
        layout.addWidget(self._btn_h_p1)

        # 2. Horario Piso 2
        self._btn_h_p2 = QPushButton("📅  HORARIO PISO 2")
        self._btn_h_p2.setCheckable(True)
        self._btn_h_p2.setStyleSheet(tab_style)
        self._btn_h_p2.clicked.connect(lambda: self._on_tab_clicked("horario_p2"))
        self._btn_group.addButton(self._btn_h_p2)
        layout.addWidget(self._btn_h_p2)

        # Separador visual
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedHeight(22)
        sep.setStyleSheet("color: #CBD5E1; background: #CBD5E1; width: 1px;")
        layout.addWidget(sep)

        # 3. Croquis Piso 1
        self._btn_c_p1 = QPushButton("🗺️  CROQUIS PISO 1")
        self._btn_c_p1.setCheckable(True)
        self._btn_c_p1.setStyleSheet(tab_style)
        self._btn_c_p1.clicked.connect(lambda: self._on_tab_clicked("croquis_p1"))
        self._btn_group.addButton(self._btn_c_p1)
        layout.addWidget(self._btn_c_p1)

        # 4. Croquis Piso 2
        self._btn_c_p2 = QPushButton("🗺️  CROQUIS PISO 2")
        self._btn_c_p2.setCheckable(True)
        self._btn_c_p2.setStyleSheet(tab_style)
        self._btn_c_p2.clicked.connect(lambda: self._on_tab_clicked("croquis_p2"))
        self._btn_group.addButton(self._btn_c_p2)
        layout.addWidget(self._btn_c_p2)

        layout.addStretch()

        # Contador de resumen
        self._lbl_count = QLabel("")
        self._lbl_count.setStyleSheet("""
            color: #64748B;
            font-family: 'Segoe UI';
            font-size: 11px;
            font-weight: 500;
        """)
        layout.addWidget(self._lbl_count)

    def _on_tab_clicked(self, view_key: str):
        self._current_view = view_key
        self._update_counter()
        self.view_changed.emit(view_key)

    def update_class_indicators(self, sessions: List[ClassSession]):
        """Actualiza el contador de clases por piso."""
        self._sessions = sessions
        self._update_counter()

    def _update_counter(self):
        if not self._sessions:
            self._lbl_count.setText("")
            return

        p1_count = sum(1 for s in self._sessions if "1" in s.floor or "primer" in s.floor.lower())
        p2_count = sum(1 for s in self._sessions if "2" in s.floor or "segundo" in s.floor.lower())

        if self._current_view in ("horario_p1", "croquis_p1"):
            self._lbl_count.setText(f"Piso 1: {p1_count} clase(s) programada(s)")
        else:
            self._lbl_count.setText(f"Piso 2: {p2_count} clase(s) programada(s)")
