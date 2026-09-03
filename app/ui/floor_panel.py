"""
Panel inferior con selector de pisos (Piso 1 / Piso 2) — tema claro y limpio.
Permite cambiar el piso activo para filtrar la vista central.
"""
from typing import List, Optional

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QFrame, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal

from app.models.schedule import ClassSession


class FloorPanel(QWidget):
    """
    Barra inferior con pestañas/botones de Piso 1 y Piso 2.
    Emite floor_selected('Primer Piso') o floor_selected('Segundo Piso').
    """
    floor_selected = pyqtSignal(str)  # 'Primer Piso', 'Segundo Piso', o 'all'

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_floor = "Primer Piso"
        self._sessions: List[ClassSession] = []
        self._setup_ui()

    def _setup_ui(self):
        self.setFixedHeight(44)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 6)
        layout.setSpacing(10)

        # Contenedor de barra inferior con fondo
        self.setStyleSheet("""
            FloorPanel {
                background: #F1F5F9;
                border-top: 1px solid #CBD5E1;
            }
        """)

        # Etiqueta indicadora
        lbl_piso = QLabel("🏢 PISOS:")
        lbl_piso.setStyleSheet("""
            color: #64748B;
            font-family: 'Segoe UI';
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(lbl_piso)

        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)

        tab_style = """
            QPushButton {
                background: #E2E8F0;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 5px 22px;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: 600;
                min-height: 20px;
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

        # Botón Piso 1
        self._btn_piso1 = QPushButton("🏥  PISO 1")
        self._btn_piso1.setCheckable(True)
        self._btn_piso1.setChecked(True)
        self._btn_piso1.setStyleSheet(tab_style)
        self._btn_piso1.clicked.connect(lambda: self._on_tab_clicked("Primer Piso"))
        self._btn_group.addButton(self._btn_piso1)
        layout.addWidget(self._btn_piso1)

        # Botón Piso 2
        self._btn_piso2 = QPushButton("🏢  PISO 2")
        self._btn_piso2.setCheckable(True)
        self._btn_piso2.setStyleSheet(tab_style)
        self._btn_piso2.clicked.connect(lambda: self._on_tab_clicked("Segundo Piso"))
        self._btn_group.addButton(self._btn_piso2)
        layout.addWidget(self._btn_piso2)

        # Botón Todos los Pisos
        self._btn_todos = QPushButton("🌐  TODOS LOS PISOS")
        self._btn_todos.setCheckable(True)
        self._btn_todos.setStyleSheet(tab_style)
        self._btn_todos.clicked.connect(lambda: self._on_tab_clicked("all"))
        self._btn_group.addButton(self._btn_todos)
        layout.addWidget(self._btn_todos)

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

    def _on_tab_clicked(self, floor_name: str):
        self._current_floor = floor_name
        self._update_counter()
        self.floor_selected.emit(floor_name)

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

        if self._current_floor == "Primer Piso":
            self._lbl_count.setText(f"Mostrando Piso 1 ({p1_count} clases programadas)")
        elif self._current_floor == "Segundo Piso":
            self._lbl_count.setText(f"Mostrando Piso 2 ({p2_count} clases programadas)")
        else:
            self._lbl_count.setText(f"Total: {len(self._sessions)} clases en todos los pisos")
