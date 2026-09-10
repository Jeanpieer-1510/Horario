"""
Vista principal de línea de tiempo (timeline) para mostrar los horarios de clase.
Diseño: tema claro igual a la imagen de referencia (UCS Actividades).
- Fondo blanco / gris muy claro
- Columna izquierda con nombres de salas sobre fondo gris
- Encabezado superior con horas
- Bloques de colores naranja, verde, amarillo, etc.
- Separadores de piso tipo banner azul oscuro
"""
from datetime import time
from typing import List, Dict, Optional

from PyQt6.QtWidgets import (
    QWidget, QScrollArea, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QSizePolicy, QToolTip, QApplication
)
from PyQt6.QtCore import (
    Qt, QRect, QPoint, QSize, pyqtSignal, QRectF, QTimer
)
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QFontMetrics, QPen, QBrush,
    QLinearGradient, QPainterPath, QCursor
)

from app.models.schedule import (
    ClassSession, FLOOR_1_ROOMS, FLOOR_2_ROOMS, FLOORS, get_session_color,
    get_course_short_name
)

# ─── Constantes de layout ─────────────────────────────────────────────────────
ROOM_LABEL_WIDTH = 190      # Ancho de la columna de nombres de ambiente
HOUR_WIDTH = 110            # Píxeles por hora
ROW_HEIGHT = 52             # Alto de cada fila de ambiente
HEADER_HEIGHT = 44          # Alto del encabezado de horas
SEP_HEIGHT = 26             # Alto de la fila separadora de piso
START_HOUR = 7              # Hora de inicio del timeline (7:00 AM)
END_HOUR = 22               # Hora de fin del timeline (22:00)
TOTAL_HOURS = END_HOUR - START_HOUR
BLOCK_V_MARGIN = 3          # Margen vertical de los bloques

# ─── Paleta de colores (tema claro, igual a la imagen) ────────────────────────
C_BG            = QColor("#FFFFFF")      # Fondo blanco del área de tiempo
C_BG_ALT        = QColor("#F8F9FC")      # Fila alternada levemente gris
C_HEADER_BG     = QColor("#F1F3F9")      # Fondo del encabezado de horas
C_HEADER_TEXT   = QColor("#6B7280")      # Texto de horas (gris medio)
C_GRID_H        = QColor("#E5E7EB")      # Líneas de hora (gris claro)
C_GRID_HALF     = QColor("#F3F4F6")      # Líneas de media hora (más suaves)
C_GRID_ROW      = QColor("#E9EBF0")      # Líneas horizontales entre filas
C_ROOM_BG       = QColor("#F1F3F9")      # Fondo columna salas
C_ROOM_BG_ALT   = QColor("#E8EBF5")      # Fondo alternado salas
C_ROOM_TEXT     = QColor("#374151")      # Texto de nombre de sala
C_ROOM_BORDER   = QColor("#D1D5E8")      # Borde derecho de la columna
C_SEP_BG        = QColor("#2D4270")      # Fondo separador de piso (azul oscuro)
C_SEP_TEXT      = QColor("#A8C0F0")      # Texto separador de piso
C_TIME_LINE     = QColor("#EF4444")      # Línea de hora actual (rojo)

# Paletas por carrera / curso: (color_base, color_acento)
THEME_MEDICINA    = ("#F97316", "#FFEDD5")  # Naranja
THEME_ENFERMERIA  = ("#0EA5E9", "#E0F2FE")  # Celeste
THEME_OBSTETRICIA = ("#8B5CF6", "#EDE9FE")  # Violeta
THEME_DEFAULT     = ("#F97316", "#FFEDD5")  # Naranja por defecto

MEDICINA_PREFIXES = [
    "SIMPED", "SIMQX", "SIMGO", "SCI", "SBS", "MED SBS", "MED-SBS",
    "PAX", "EXT CIRG", "EXT CIRUGIA", "EXT. CIRG", "EXT CIR",
    "EXT GYO", "EXT GY O", "EXT G Y O", "EXT. GYO", "EXT G&O",
    "EXT MED", "EXT. MED", "EXT PED", "EXT. PED",
    "ECOGRAFIA", "ECOGRAFÍA", "ECOGRAF"
]

ENFERMERIA_PREFIXES = [
    "ENF", "ENFERMERIA", "ENFERMERÍA"
]

OBSTETRICIA_PREFIXES = [
    "OBST", "OBSTETRICIA"
]


def clean_text(text: str) -> str:
    """Limpia caracteres como corchetes y signos para facilitar búsqueda de prefijo."""
    if not text:
        return ""
    cleaned = text.upper().replace("[", " ").replace("]", " ").replace(":", " ").replace("-", " ")
    return " ".join(cleaned.split())


def minutes_to_x(minutes_from_midnight: int) -> float:
    """Convierte minutos desde medianoche a coordenada X en el canvas."""
    offset = minutes_from_midnight - START_HOUR * 60
    return (offset / 60.0) * HOUR_WIDTH


def get_block_colors(session_name: str, index: int = 0) -> tuple:
    """
    Retorna (color_base, color_acento) según la carrera solicitada:
    - Medicina Humana -> Naranja
    - Enfermería -> Celeste
    - Obstetricia -> Violeta
    """
    if not session_name:
        return THEME_MEDICINA

    norm = clean_text(session_name)

    # 1. Enfermería -> Celeste (ENF)
    for pref in ENFERMERIA_PREFIXES:
        if norm.startswith(pref) or f" {pref} " in f" {norm} ":
            return THEME_ENFERMERIA

    # 2. Obstetricia -> Violeta (OBST)
    for pref in OBSTETRICIA_PREFIXES:
        if norm.startswith(pref) or f" {pref} " in f" {norm} ":
            return THEME_OBSTETRICIA

    # 3. Medicina Humana -> Naranja (SimPed, SimQx, SimGO, SCI, SBS, PAX, Ext Cirg, Ext GyO, Ext Med, Ext Ped, Ecografia)
    for pref in MEDICINA_PREFIXES:
        if norm.startswith(pref) or f" {pref} " in f" {norm} ":
            return THEME_MEDICINA

    return THEME_MEDICINA



class TimelineCanvas(QWidget):
    """
    Canvas principal que renderiza la cuadrícula de tiempo y los bloques de clase.
    Tema claro idéntico a la imagen de referencia UCS Actividades.
    """
    session_clicked = pyqtSignal(ClassSession)
    session_hovered = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sessions: List[ClassSession] = []
        self.rooms: List[str] = []
        self.floor_separators: List[int] = []
        self.floor_labels: Dict[int, str] = {}
        self._hovered_session: Optional[ClassSession] = None
        self._color_cache: Dict[str, tuple] = {}   # key → (base_hex, accent_hex)
        self._room_index_cache: Dict[str, int] = {}
        self._session_rects: List[tuple] = []       # (QRectF, ClassSession)
        self._row_y_cache: List[int] = []           # y de cada fila (incluyendo seps)

        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), C_BG)
        self.setPalette(palette)

    # ──────────────────────────────────────────────────────────────────────────
    def set_data(self, sessions: List[ClassSession], active_rooms: List[str],
                 floor_separators: List[int], floor_labels: Dict[int, str]):
        self.sessions = sessions
        self.rooms = active_rooms
        self.floor_separators = floor_separators
        self.floor_labels = floor_labels
        self._rebuild_caches()
        self._update_size()
        self.update()

    def _rebuild_caches(self):
        self._room_index_cache = {room: idx for idx, room in enumerate(self.rooms)}
        self._color_cache = {}
        color_idx = 0
        for s in self.sessions:
            key = (s.session_name[:15] if s.session_name else "?") + str(s.room[:8])
            if key not in self._color_cache:
                self._color_cache[key] = get_block_colors(s.session_name, color_idx)
                color_idx += 1

        # Pre-calcular Y de cada fila
        self._row_y_cache = []
        y = HEADER_HEIGHT
        for i in range(len(self.rooms)):
            self._row_y_cache.append(y)
            if i in self.floor_separators:
                y += SEP_HEIGHT
            else:
                y += ROW_HEIGHT

    def _update_size(self):
        total_width = ROOM_LABEL_WIDTH + TOTAL_HOURS * HOUR_WIDTH + 1
        total_height = self._calc_total_height()
        self.setMinimumSize(total_width, total_height)
        self.resize(total_width, total_height)

    def _calc_total_height(self) -> int:
        h = HEADER_HEIGHT
        for i in range(len(self.rooms)):
            h += SEP_HEIGHT if i in self.floor_separators else ROW_HEIGHT
        return h

    # ──────────────────────────────────────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self._draw_background(painter)
        self._draw_hour_header(painter)
        self._draw_rows_and_grid(painter)
        self._draw_sessions(painter)
        self._draw_room_labels(painter)
        self._draw_current_time_line(painter)

        painter.end()

    # ── Background ──────────────────────────────────────────────────────────
    def _draw_background(self, painter: QPainter):
        painter.fillRect(self.rect(), C_BG)

    # ── Encabezado de horas ─────────────────────────────────────────────────
    def _draw_hour_header(self, painter: QPainter):
        total_w = self.width()

        # Fondo del header completo
        painter.fillRect(QRect(0, 0, total_w, HEADER_HEIGHT), C_HEADER_BG)

        # Fondo de la zona de etiquetas (izquierda)
        painter.fillRect(QRect(0, 0, ROOM_LABEL_WIDTH, HEADER_HEIGHT), C_ROOM_BG)

        # Línea inferior del header
        painter.setPen(QPen(C_GRID_H, 1))
        painter.drawLine(0, HEADER_HEIGHT - 1, total_w, HEADER_HEIGHT - 1)

        # Borde derecho de la columna de salas en el header
        painter.setPen(QPen(C_ROOM_BORDER, 1))
        painter.drawLine(ROOM_LABEL_WIDTH, 0, ROOM_LABEL_WIDTH, HEADER_HEIGHT)

        font = QFont("Segoe UI", 8, QFont.Weight.Medium)
        painter.setFont(font)

        for h in range(START_HOUR, END_HOUR + 1):
            x = ROOM_LABEL_WIDTH + (h - START_HOUR) * HOUR_WIDTH

            # Línea vertical de hora en el header
            painter.setPen(QPen(C_GRID_H, 1))
            painter.drawLine(x, 0, x, HEADER_HEIGHT)

            # Texto de la hora
            painter.setPen(C_HEADER_TEXT)
            label = f"{h:02d}:00"
            painter.drawText(x + 5, HEADER_HEIGHT - 10, label)

            # Tick de media hora
            x_half = x + HOUR_WIDTH // 2
            painter.setPen(QPen(C_GRID_H, 1))
            painter.drawLine(x_half, HEADER_HEIGHT - 10, x_half, HEADER_HEIGHT)

    # ── Filas y cuadrícula ──────────────────────────────────────────────────
    def _draw_rows_and_grid(self, painter: QPainter):
        total_w = self.width()
        total_h = self._calc_total_height()

        for i, room in enumerate(self.rooms):
            y = self._row_y_cache[i]
            is_sep = i in self.floor_separators
            row_h = SEP_HEIGHT if is_sep else ROW_HEIGHT

            # Separador de piso
            if is_sep:
                painter.fillRect(QRect(0, y, total_w, row_h), C_SEP_BG)
                continue

            # Fondo de fila alternado (solo área de tiempo, no la columna de salas)
            row_color = C_BG if i % 2 == 0 else C_BG_ALT
            painter.fillRect(QRect(ROOM_LABEL_WIDTH, y,
                                   total_w - ROOM_LABEL_WIDTH, row_h), row_color)

        # Líneas verticales de hora
        painter.setPen(QPen(C_GRID_H, 1))
        for h in range(START_HOUR, END_HOUR + 1):
            x = ROOM_LABEL_WIDTH + (h - START_HOUR) * HOUR_WIDTH
            painter.drawLine(x, HEADER_HEIGHT, x, total_h)

        # Líneas de media hora (más suaves)
        painter.setPen(QPen(C_GRID_HALF, 1))
        for h in range(START_HOUR, END_HOUR):
            x = ROOM_LABEL_WIDTH + (h - START_HOUR) * HOUR_WIDTH + HOUR_WIDTH // 2
            painter.drawLine(x, HEADER_HEIGHT, x, total_h)

        # Líneas horizontales entre filas
        painter.setPen(QPen(C_GRID_ROW, 1))
        for i in range(len(self.rooms)):
            y = self._row_y_cache[i]
            row_h = SEP_HEIGHT if i in self.floor_separators else ROW_HEIGHT
            painter.drawLine(ROOM_LABEL_WIDTH, y + row_h,
                             total_w, y + row_h)

    # ── Bloques de clase ────────────────────────────────────────────────────
    def _draw_sessions(self, painter: QPainter):
        self._session_rects = []

        for session in self.sessions:
            row_idx = self._get_room_row(session.room)
            if row_idx < 0:
                continue

            y_row = self._row_y_cache[row_idx]
            x = ROOM_LABEL_WIDTH + minutes_to_x(session.start_minutes_from_midnight)
            w = (session.duration_minutes / 60.0) * HOUR_WIDTH
            y = y_row + BLOCK_V_MARGIN
            h = ROW_HEIGHT - BLOCK_V_MARGIN * 2

            if w < 4:
                w = 4

            rect = QRectF(x + 1, y, w - 2, h)
            self._session_rects.append((rect, session))

            key = (session.session_name[:15] if session.session_name else "?") + str(session.room[:8])
            base_hex, accent_hex = self._color_cache.get(key, ("#F59E0B", "#FDE68A"))
            is_hovered = session is self._hovered_session

            self._draw_block(painter, rect,
                             QColor(base_hex), QColor(accent_hex),
                             session, is_hovered)

    def _draw_block(self, painter: QPainter, rect: QRectF,
                    base: QColor, accent: QColor,
                    session: ClassSession, hovered: bool):
        """
        Dibuja un bloque de clase al estilo de la imagen:
        - Fondo sólido del color base
        - Borde del mismo color base pero más oscuro
        - Barra de acento a la izquierda más brillante
        - Texto blanco en negrita
        """
        # Fondo sólido con leve gradiente
        grad = QLinearGradient(rect.left(), rect.top(), rect.left(), rect.bottom())
        if hovered:
            grad.setColorAt(0, base.lighter(115))
            grad.setColorAt(1, base.darker(108))
        else:
            grad.setColorAt(0, base.lighter(108))
            grad.setColorAt(1, base.darker(112))

        path = QPainterPath()
        path.addRoundedRect(rect, 3, 3)

        painter.fillPath(path, QBrush(grad))

        # Borde
        border = base.darker(130) if not hovered else base.darker(115)
        painter.setPen(QPen(border, 1))
        painter.drawPath(path)

        # Barra vertical izquierda (acento más oscuro)
        accent_bar = QRectF(rect.left(), rect.top() + 1, 4, rect.height() - 2)
        accent_path = QPainterPath()
        accent_path.addRoundedRect(accent_bar, 2, 2)
        painter.fillPath(accent_path, QBrush(base.darker(140)))

        # Texto
        text_rect = rect.adjusted(7, 2, -3, -2)
        if text_rect.width() > 16 and text_rect.height() > 8:
            # Nombre del curso (solo curso, sin tema completo)
            font = QFont("Segoe UI", 7, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QColor("#FFFFFF"))
            fm = QFontMetrics(font)
            session_text = get_course_short_name(session.session_name) or "(Sin curso)"
            elided = fm.elidedText(session_text, Qt.TextElideMode.ElideRight,
                                   int(text_rect.width()))

            top_half = QRectF(text_rect.left(), text_rect.top(),
                              text_rect.width(), text_rect.height() * 0.55)
            painter.drawText(top_half,
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                             elided)

            # Hora en la línea inferior
            if text_rect.height() > 26:
                font2 = QFont("Segoe UI", 6)
                painter.setFont(font2)
                painter.setPen(QColor(255, 255, 255, 210))
                time_str = (f"{session.start_time.strftime('%H:%M')}-"
                            f"{session.end_time.strftime('%H:%M')}")
                bot_half = QRectF(text_rect.left(),
                                  text_rect.top() + text_rect.height() * 0.55,
                                  text_rect.width(),
                                  text_rect.height() * 0.45)
                painter.drawText(bot_half,
                                 Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                                 time_str)

    # ── Columna de salas ────────────────────────────────────────────────────
    def _draw_room_labels(self, painter: QPainter):
        total_h = self._calc_total_height()

        # Fondo de la columna de salas
        painter.fillRect(QRect(0, HEADER_HEIGHT, ROOM_LABEL_WIDTH,
                               total_h - HEADER_HEIGHT), C_ROOM_BG)

        # Borde derecho
        painter.setPen(QPen(C_ROOM_BORDER, 1))
        painter.drawLine(ROOM_LABEL_WIDTH, HEADER_HEIGHT,
                         ROOM_LABEL_WIDTH, total_h)

        font_room = QFont("Segoe UI", 8)
        font_sep = QFont("Segoe UI", 8, QFont.Weight.Bold)

        for i, room in enumerate(self.rooms):
            y = self._row_y_cache[i]
            is_sep = i in self.floor_separators
            row_h = SEP_HEIGHT if is_sep else ROW_HEIGHT

            if is_sep:
                # Separador de piso: banner azul oscuro
                painter.setFont(font_sep)
                painter.setPen(C_SEP_TEXT)
                icon = "▾"
                label_txt = f"  {icon}  {self.floor_labels.get(i, '')}"
                painter.drawText(
                    QRect(0, y, ROOM_LABEL_WIDTH, row_h),
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                    label_txt
                )
                continue

            # Fondo alternado de sala
            bg = C_ROOM_BG if i % 2 == 0 else C_ROOM_BG_ALT
            painter.fillRect(QRect(0, y, ROOM_LABEL_WIDTH, row_h), bg)

            # Punto de color a la izquierda (indicador)
            dot_color = QColor("#6B7CB8")
            painter.fillRect(QRect(0, y + 4, 3, row_h - 8), dot_color)

            # Nombre de sala
            painter.setFont(font_room)
            painter.setPen(C_ROOM_TEXT)
            fm = QFontMetrics(font_room)
            elided = fm.elidedText(room, Qt.TextElideMode.ElideRight,
                                   ROOM_LABEL_WIDTH - 14)
            painter.drawText(
                QRect(6, y, ROOM_LABEL_WIDTH - 10, row_h),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                elided
            )

            # Línea inferior de la sala (coincide con la cuadrícula)
            painter.setPen(QPen(C_GRID_ROW, 1))
            painter.drawLine(0, y + row_h, ROOM_LABEL_WIDTH, y + row_h)

    # ── Línea de hora actual ─────────────────────────────────────────────────
    def _draw_current_time_line(self, painter: QPainter):
        from datetime import datetime
        now = datetime.now().time()
        now_minutes = now.hour * 60 + now.minute

        if not (START_HOUR * 60 <= now_minutes <= END_HOUR * 60):
            return

        x = int(ROOM_LABEL_WIDTH + minutes_to_x(now_minutes))
        total_h = self._calc_total_height()

        painter.setPen(QPen(C_TIME_LINE, 2))
        painter.drawLine(x, HEADER_HEIGHT, x, total_h)

        # Círculo indicador en el header
        painter.setBrush(QBrush(C_TIME_LINE))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(x - 5, HEADER_HEIGHT - 7, 10, 10)

    # ── Helpers ──────────────────────────────────────────────────────────────
    def _get_room_row(self, room_name: str) -> int:
        if not room_name:
            return -1

        # 1. Búsqueda exacta directa
        if room_name in self._room_index_cache:
            idx = self._room_index_cache[room_name]
            if idx not in self.floor_separators:
                return idx

        # 2. Normalización básica
        room_upper = room_name.upper().strip()
        if ":" in room_upper:
            room_upper = room_upper.split(":", 1)[1].strip()

        # 3. Búsqueda exacta normalizada
        for room, idx in self._room_index_cache.items():
            if idx in self.floor_separators:
                continue
            if room_upper == room.upper().strip():
                return idx

        # 4. Búsqueda flexible con ceros normalizados (e.g. ECOE 1 == ECOE 01, CONSULTORIO 5 == CONSULTORIO 5 - L 213)
        import re
        def simplify(s: str) -> str:
            s_clean = s.upper().replace("-", " ").replace(":", " ")
            s_clean = re.sub(r'\b0+(\d+)\b', r'\1', s_clean)
            return " ".join(s_clean.split())

        target_simple = simplify(room_upper)

        for room, idx in self._room_index_cache.items():
            if idx in self.floor_separators:
                continue
            r_simple = simplify(room)
            if target_simple == r_simple or target_simple in r_simple or r_simple in target_simple:
                return idx

        return -1


    def mouseMoveEvent(self, event):
        pos = event.position()
        found = None
        for rect, session in self._session_rects:
            if rect.contains(pos):
                found = session
                break

        if found != self._hovered_session:
            self._hovered_session = found
            self.update()
            self.session_hovered.emit(found)

        if found:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            course_name = get_course_short_name(found.session_name)
            tooltip = (
                f"<b>Curso:</b> {course_name}<br>"
                f"<b>Ambiente:</b> {found.room}<br>"
                f"<b>Horario:</b> {found.start_time.strftime('%H:%M')} - "
                f"{found.end_time.strftime('%H:%M')}<br>"
                f"<b>Duración:</b> {found.duration_minutes} min<br>"
                f"<b>Docente líder:</b> {found.lead_teacher or 'N/A'}<br>"
                f"<b>Colaboradores:</b> {found.collab_teachers or 'N/A'}"
            )
            QToolTip.showText(
                QCursor.pos(), tooltip, self,
                QRect(int(pos.x()) - 2, int(pos.y()) - 2, 4, 4), 8000
            )
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            QToolTip.hideText()

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        pos = event.position()
        for rect, session in self._session_rects:
            if rect.contains(pos):
                self.session_clicked.emit(session)
                break
        super().mousePressEvent(event)


# ─────────────────────────────────────────────────────────────────────────────

class TimelineView(QWidget):
    """
    Vista completa de línea de tiempo con scroll horizontal y vertical.
    Permite filtrar por piso seleccionado (Piso 1, Piso 2 o Todos).
    """
    session_clicked = pyqtSignal(ClassSession)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._sessions: List[ClassSession] = []
        self._current_floor: str = "Primer Piso"
        self._setup_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_time_line)
        self._timer.start(60_000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(False)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #FFFFFF;
            }
            QScrollBar:horizontal {
                height: 10px;
                background: #F3F4F6;
                border-radius: 5px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #CBD5E1;
                border-radius: 5px;
                min-width: 40px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #94A3B8;
            }
            QScrollBar:vertical {
                width: 10px;
                background: #F3F4F6;
                border-radius: 5px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 5px;
                min-height: 40px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                background: none;
                border: none;
                height: 0px;
                width: 0px;
            }
        """)

        self._canvas = TimelineCanvas()
        self._canvas.session_clicked.connect(self.session_clicked)
        self._scroll.setWidget(self._canvas)

        layout.addWidget(self._scroll)

        # Scroll inicial hacia la hora actual
        from datetime import datetime
        now_h = datetime.now().hour
        start_offset = max(0, now_h - START_HOUR - 1) * HOUR_WIDTH
        QTimer.singleShot(150, lambda: self._scroll.horizontalScrollBar().setValue(
            int(start_offset)))

    def load_sessions(self, sessions: List[ClassSession]):
        self._sessions = sessions
        self._refresh_canvas()

    def set_selected_floor(self, floor_name: str):
        """Cambia el piso activo ('Primer Piso', 'Segundo Piso', o 'all')."""
        self._current_floor = floor_name
        self._refresh_canvas()

    def _refresh_canvas(self):
        active_rooms = []
        floor_separators = {}
        floor_labels = {}

        if self._current_floor == "Primer Piso":
            active_rooms = list(FLOOR_1_ROOMS)
        elif self._current_floor == "Segundo Piso":
            active_rooms = list(FLOOR_2_ROOMS)
        else:
            # Todos los pisos
            for floor_name, rooms in FLOORS.items():
                sep_idx = len(active_rooms)
                floor_separators[sep_idx] = True
                floor_labels[sep_idx] = floor_name.upper()
                active_rooms.append(f"__sep__{floor_name}")
                for room in rooms:
                    active_rooms.append(room)

        self._canvas.set_data(
            self._sessions,
            active_rooms,
            list(floor_separators.keys()),
            floor_labels,
        )

    def _refresh_time_line(self):
        self._canvas.update()

