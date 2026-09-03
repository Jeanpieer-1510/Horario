"""
Ventana principal de la aplicación de Horarios Universitarios.
Diseño basado en la imagen de referencia UCS Actividades:
- Header azul oscuro con logo y reloj
- Toolbar con botones de carga y navegación de fecha
- Vista de línea de tiempo con tema claro
- Panel inferior de pisos
"""
import os
from datetime import date, datetime
from typing import List, Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QSplitter,
    QFrame, QDialog, QTextEdit, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor

from app.models.schedule import ClassSession
from app.services.excel_reader import read_excel
from app.ui.timeline_view import TimelineView
from app.ui.floor_panel import FloorPanel


# ─── Paleta de la UI principal ────────────────────────────────────────────────
HEADER_BG   = "#1E2B4A"   # Azul muy oscuro para el header (como UCS)
TOOLBAR_BG  = "#FFFFFF"   # Toolbar blanco
TOOLBAR_BRD = "#E5E7EB"   # Borde inferior del toolbar
BTN_PRIMARY = "#2563EB"   # Azul para botones primarios (Hoy, Cargar)
BTN_SUCCESS = "#16A34A"   # Verde para Cargar Excel
BTN_RELOAD  = "#4F46E5"   # Violeta para Recargar
BTN_NAV_BG  = "#F3F4F6"   # Fondo botones de navegación
BTN_NAV_BRD = "#D1D5DB"   # Borde botones de navegación
TEXT_DARK   = "#111827"   # Texto principal oscuro
TEXT_MID    = "#6B7280"   # Texto secundario gris
TEXT_LIGHT  = "#FFFFFF"   # Texto blanco
ACCENT      = "#3B82F6"   # Azul acento


class DateNavigator(QWidget):
    """Widget de navegación de fechas — estilo toolbar de la imagen."""
    date_changed = pyqtSignal(date)

    DAYS_ES   = ["Lunes", "Martes", "Miércoles", "Jueves",
                 "Viernes", "Sábado", "Domingo"]
    MONTHS_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                 "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_date = date.today()
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        nav_btn_style = f"""
            QPushButton {{
                background: {BTN_NAV_BG};
                color: {TEXT_DARK};
                border: 1px solid {BTN_NAV_BRD};
                border-radius: 5px;
                font-family: 'Segoe UI';
                font-size: 13px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background: #E5E7EB;
                border-color: #9CA3AF;
            }}
            QPushButton:pressed {{ background: #D1D5DB; }}
        """

        self._btn_prev = QPushButton("‹")
        self._btn_prev.setFixedSize(28, 28)
        self._btn_prev.clicked.connect(self._go_prev)
        self._btn_prev.setStyleSheet(nav_btn_style)

        self._btn_next = QPushButton("›")
        self._btn_next.setFixedSize(28, 28)
        self._btn_next.clicked.connect(self._go_next)
        self._btn_next.setStyleSheet(nav_btn_style)

        self._date_label = QLabel()
        self._date_label.setFixedWidth(200)
        self._date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._date_label.setStyleSheet(f"""
            color: {TEXT_DARK};
            font-family: 'Segoe UI';
            font-size: 13px;
            font-weight: 600;
            background: {BTN_NAV_BG};
            border: 1px solid {BTN_NAV_BRD};
            border-radius: 5px;
            padding: 4px 8px;
        """)

        self._btn_today = QPushButton("Hoy")
        self._btn_today.setFixedHeight(28)
        self._btn_today.setFixedWidth(52)
        self._btn_today.clicked.connect(self._go_today)
        self._btn_today.setStyleSheet(f"""
            QPushButton {{
                background: {BTN_PRIMARY};
                color: {TEXT_LIGHT};
                border: none;
                border-radius: 5px;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: #1D4ED8; }}
            QPushButton:pressed {{ background: #1E40AF; }}
        """)

        layout.addWidget(self._btn_prev)
        layout.addWidget(self._btn_next)
        layout.addWidget(self._date_label)
        layout.addSpacing(6)
        layout.addWidget(self._btn_today)

        self._update_label()

    def _update_label(self):
        d = self._current_date
        day_name = self.DAYS_ES[d.weekday()]
        month = self.MONTHS_ES[d.month - 1]
        self._date_label.setText(f"{day_name}, {d.day} {month} {d.year}")

    def _go_prev(self):
        from datetime import timedelta
        self._current_date -= timedelta(days=1)
        self._update_label()
        self.date_changed.emit(self._current_date)

    def _go_next(self):
        from datetime import timedelta
        self._current_date += timedelta(days=1)
        self._update_label()
        self.date_changed.emit(self._current_date)

    def _go_today(self):
        self._current_date = date.today()
        self._update_label()
        self.date_changed.emit(self._current_date)

    @property
    def current_date(self) -> date:
        return self._current_date


class SessionDetailDialog(QDialog):
    """Diálogo con detalle completo de una sesión de clase."""

    def __init__(self, session: ClassSession, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detalle de Sesión")
        self.setMinimumSize(520, 360)
        self.setStyleSheet("""
            QDialog { background: #FFFFFF; }
            QLabel { font-family: 'Segoe UI'; color: #111827; }
            QPushButton {
                background: #2563EB; color: white; border: none;
                border-radius: 6px; padding: 8px 22px;
                font-family: 'Segoe UI'; font-weight: bold;
            }
            QPushButton:hover { background: #1D4ED8; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(14)

        # Título
        title = QLabel(session.session_name or "Sin nombre")
        title.setStyleSheet("""
            font-size: 15px; font-weight: bold; color: #1E40AF;
            padding: 10px 14px;
            background: #EFF6FF;
            border-radius: 8px;
            border-left: 5px solid #3B82F6;
        """)
        title.setWordWrap(True)
        layout.addWidget(title)

        # Grilla de información
        info = QFrame()
        info.setStyleSheet("""
            QFrame {
                background: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
            }
        """)
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(16, 12, 16, 12)
        info_layout.setSpacing(10)

        fields = [
            ("🏥 Ambiente",        session.room),
            ("🕐 Horario",         f"{session.start_time.strftime('%H:%M')} → "
                                   f"{session.end_time.strftime('%H:%M')}  "
                                   f"({session.duration_minutes} min)"),
            ("🏢 Piso",            session.floor),
            ("👨‍🏫 Docente Líder",   session.lead_teacher or "N/A"),
            ("👥 Colaboradores",   session.collab_teachers or "N/A"),
            ("🧑‍⚕️ Pacientes",      session.standardized_patients or "N/A"),
        ]

        for lbl, val in fields:
            row = QHBoxLayout()
            row.setSpacing(10)
            l = QLabel(lbl)
            l.setFixedWidth(160)
            l.setStyleSheet("color: #6B7280; font-size: 12px;")
            v = QLabel(val)
            v.setStyleSheet("color: #111827; font-size: 12px;")
            v.setWordWrap(True)
            row.addWidget(l)
            row.addWidget(v, 1)
            info_layout.addLayout(row)

        layout.addWidget(info)

        btn = QPushButton("Cerrar")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignRight)


class ImportResultDialog(QDialog):
    """Muestra el resultado de la importación del Excel."""

    def __init__(self, errors: List[str], count: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Resultado de Importación")
        self.setMinimumSize(480, 280)
        self.setStyleSheet("""
            QDialog { background: #FFFFFF; }
            QLabel { font-family: 'Segoe UI'; }
            QTextEdit {
                background: #F9FAFB; color: #374151;
                border: 1px solid #E5E7EB; border-radius: 6px;
                font-family: 'Consolas'; font-size: 11px;
            }
            QPushButton {
                background: #2563EB; color: white; border: none;
                border-radius: 6px; padding: 8px 22px;
                font-family: 'Segoe UI'; font-weight: bold;
            }
            QPushButton:hover { background: #1D4ED8; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(12)

        ok_lbl = QLabel(f"✅  {count} sesiones importadas exitosamente.")
        ok_lbl.setStyleSheet("color: #16A34A; font-size: 14px; font-weight: bold;")
        layout.addWidget(ok_lbl)

        if errors:
            warn = QLabel(f"⚠️  {len(errors)} advertencia(s):")
            warn.setStyleSheet("color: #D97706; font-size: 12px;")
            layout.addWidget(warn)
            txt = QTextEdit()
            txt.setReadOnly(True)
            txt.setPlainText("\n".join(errors))
            layout.addWidget(txt)
        else:
            no_warn = QLabel("Sin advertencias. Todos los datos se importaron correctamente.")
            no_warn.setStyleSheet("color: #6B7280; font-size: 12px;")
            layout.addWidget(no_warn)

        btn = QPushButton("Aceptar")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignRight)


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación SimClic."""

    def __init__(self):
        super().__init__()
        self._sessions: List[ClassSession] = []
        self._current_file: str = ""
        self._setup_window()
        self._setup_ui()
        self._setup_statusbar()

    def _setup_window(self):
        self.setWindowTitle("SimClic · Horarios Universitarios")
        self.setMinimumSize(1200, 700)
        self.resize(1440, 860)
        # Fondo general blanco
        self.setStyleSheet("""
            QMainWindow { background: #F1F3F9; }
            QToolTip {
                background: #1F2937;
                color: #F9FAFB;
                border: 1px solid #374151;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
        """)

    def _setup_ui(self):
        central = QWidget()
        central.setStyleSheet("background: #F1F3F9;")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        main_layout.addWidget(self._build_header())
        # Toolbar
        main_layout.addWidget(self._build_toolbar())

        # Timeline central (ocupa todo el espacio principal)
        self._timeline = TimelineView()
        self._timeline.session_clicked.connect(self._show_session_detail)
        main_layout.addWidget(self._timeline, 1)

        # Panel / Barra inferior de pisos
        self._floor_panel = FloorPanel()
        self._floor_panel.floor_selected.connect(self._on_floor_changed)
        main_layout.addWidget(self._floor_panel)


    # ── Header ──────────────────────────────────────────────────────────────
    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setFixedHeight(52)
        header.setStyleSheet(f"""
            QFrame {{
                background: {HEADER_BG};
                border-bottom: 1px solid #152035;
            }}
        """)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(10)

        # Logo
        logo = QLabel("UCS")
        logo.setStyleSheet("""
            color: #FFFFFF;
            font-family: 'Segoe UI';
            font-size: 20px;
            font-weight: 800;
            letter-spacing: 1px;
        """)

        sep = QLabel("|")
        sep.setStyleSheet("color: #4B5E80; font-size: 18px;")

        subtitle = QLabel("Actividades")
        subtitle.setStyleSheet("""
            color: #A8C0E8;
            font-family: 'Segoe UI';
            font-size: 15px;
            font-weight: 400;
        """)

        layout.addWidget(logo)
        layout.addWidget(sep)
        layout.addWidget(subtitle)
        layout.addStretch()

        # Reloj
        self._clock_label = QLabel()
        self._clock_label.setStyleSheet("""
            color: #A8C0E8;
            font-family: 'Segoe UI';
            font-size: 15px;
            font-weight: 600;
        """)
        self._update_clock()
        timer = QTimer(self)
        timer.timeout.connect(self._update_clock)
        timer.start(1000)
        layout.addWidget(self._clock_label)

        return header

    # ── Toolbar ─────────────────────────────────────────────────────────────
    def _build_toolbar(self) -> QWidget:
        toolbar = QFrame()
        toolbar.setFixedHeight(50)
        toolbar.setStyleSheet(f"""
            QFrame {{
                background: {TOOLBAR_BG};
                border-bottom: 1px solid {TOOLBAR_BRD};
            }}
        """)
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(10)

        # Botón Cargar Excel
        self._btn_load = QPushButton("📂  Cargar Excel")
        self._btn_load.setFixedHeight(34)
        self._btn_load.clicked.connect(self._load_excel)
        self._btn_load.setStyleSheet(f"""
            QPushButton {{
                background: {BTN_SUCCESS};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 0px 16px;
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: #15803D; }}
            QPushButton:pressed {{ background: #166534; }}
        """)

        # Botón Recargar
        self._btn_reload = QPushButton("🔄  Recargar")
        self._btn_reload.setFixedHeight(34)
        self._btn_reload.clicked.connect(self._reload_excel)
        self._btn_reload.setEnabled(False)
        self._btn_reload.setStyleSheet(f"""
            QPushButton {{
                background: {BTN_RELOAD};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 0px 14px;
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: #4338CA; }}
            QPushButton:disabled {{
                background: #E5E7EB;
                color: #9CA3AF;
            }}
        """)

        layout.addWidget(self._btn_load)
        layout.addWidget(self._btn_reload)

        # Separador visual
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedHeight(28)
        sep.setStyleSheet("color: #E5E7EB; background: #E5E7EB; width: 1px;")
        layout.addWidget(sep)

        # Navegación de fecha
        self._date_nav = DateNavigator()
        self._date_nav.date_changed.connect(self._on_date_changed)
        layout.addWidget(self._date_nav)

        # Etiqueta "Línea de Tiempo Diaria"
        view_label = QLabel("Línea de Tiempo · Salas")
        view_label.setStyleSheet(f"""
            color: {ACCENT};
            font-family: 'Segoe UI';
            font-size: 12px;
            font-weight: 600;
            background: #EFF6FF;
            border: 1px solid #BFDBFE;
            border-radius: 12px;
            padding: 3px 12px;
        """)
        layout.addWidget(view_label)

        layout.addStretch()

        # Nombre del archivo activo
        self._file_label = QLabel("Sin archivo cargado")
        self._file_label.setStyleSheet(f"""
            color: {TEXT_MID};
            font-family: 'Segoe UI';
            font-size: 11px;
            font-style: italic;
        """)
        layout.addWidget(self._file_label)

        # Badge de sesiones
        self._sessions_label = QLabel("")
        self._sessions_label.setStyleSheet(f"""
            color: {BTN_PRIMARY};
            font-family: 'Segoe UI';
            font-size: 11px;
            font-weight: 700;
            background: #EFF6FF;
            border: 1px solid #BFDBFE;
            border-radius: 10px;
            padding: 2px 10px;
        """)
        self._sessions_label.hide()
        layout.addWidget(self._sessions_label)

        return toolbar

    # ── Barra de estado ──────────────────────────────────────────────────────
    def _setup_statusbar(self):
        sb = self.statusBar()
        sb.setStyleSheet("""
            QStatusBar {
                background: #F9FAFB;
                color: #6B7280;
                border-top: 1px solid #E5E7EB;
                font-family: 'Segoe UI';
                font-size: 11px;
            }
        """)
        sb.showMessage("Listo  ·  Cargue un archivo Excel para comenzar")

    # ── Lógica de la app ─────────────────────────────────────────────────────
    def _update_clock(self):
        self._clock_label.setText(datetime.now().strftime("%H:%M:%S"))

    def _load_excel(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de horarios",
            os.path.expanduser("~"),
            "Archivos Excel (*.xlsx *.xls);;Todos los archivos (*)"
        )
        if filepath:
            self._current_file = filepath
            self._import_file(filepath)

    def _reload_excel(self):
        if self._current_file and os.path.exists(self._current_file):
            self._import_file(self._current_file)
        else:
            QMessageBox.warning(self, "Error", "El archivo ya no existe en la ruta original.")

    def _import_file(self, filepath: str):
        self.statusBar().showMessage(f"Importando: {os.path.basename(filepath)}...")
        QApplication.processEvents()

        sessions, errors = read_excel(filepath)

        if not sessions and errors:
            QMessageBox.critical(
                self, "Error de importación",
                f"No se pudo importar el archivo:\n{errors[0]}"
            )
            return

        self._sessions = sessions
        self._update_view(sessions)

        fname = os.path.basename(filepath)
        self._file_label.setText(f"📄 {fname}")
        self._file_label.setStyleSheet(f"""
            color: {BTN_PRIMARY};
            font-family: 'Segoe UI';
            font-size: 11px;
        """)
        self._btn_reload.setEnabled(True)
        self._sessions_label.setText(f"{len(sessions)} sesiones")
        self._sessions_label.show()
        self.statusBar().showMessage(
            f"✅  {len(sessions)} sesiones importadas  ·  {fname}"
        )

        dlg = ImportResultDialog(errors, len(sessions), self)
        dlg.exec()

    def _update_view(self, sessions: List[ClassSession]):
        self._timeline.load_sessions(sessions)
        self._floor_panel.update_class_indicators(sessions)

    def _on_date_changed(self, new_date: date):
        self.statusBar().showMessage(
            f"Fecha: {new_date.strftime('%d/%m/%Y')}  ·  "
            f"{len(self._sessions)} sesiones cargadas"
        )

    def _show_session_detail(self, session: ClassSession):
        dlg = SessionDetailDialog(session, self)
        dlg.exec()

    def _on_floor_changed(self, floor_name: str):
        self._timeline.set_selected_floor(floor_name)
        if floor_name == "all":
            self.statusBar().showMessage("Mostrando todos los pisos")
        else:
            self.statusBar().showMessage(f"Mostrando ambientes de: {floor_name}")

