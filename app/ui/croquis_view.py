"""
Vista interactiva de Croquis / Plano de Distribución (Piso 1 y Piso 2).
Permite visualizar la distribución arquitectónica exacta de los ambientes,
consultar la ocupación en tiempo real o en una hora específica seleccionada,
y ver los cursos asignados a cada ambiente con interactividad dinámica.
"""
from dataclasses import dataclass, field
from datetime import time, datetime
from typing import List, Dict, Optional, Tuple

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSlider, QTimeEdit, QScrollArea, QSplitter,
    QToolTip, QDialog, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QRectF, QPointF, pyqtSignal, QTimer, QTime, QSize
)
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QFontMetrics, QPen, QBrush,
    QLinearGradient, QPainterPath, QCursor
)

from app.models.schedule import (
    ClassSession, get_course_short_name, get_session_color,
    COLOR_MEDICINA, COLOR_ENFERMERIA, COLOR_OBSTETRICIA
)


# ─── Colores del Croquis (Idénticos al diseño del plano) ───────────────────────
BG_CORRIDOR   = QColor("#FCE7D8")   # Pasadizos (peach/crema claro)
BG_CLASS_ROOM = QColor("#F5DDEC")   # Ambientes de clase (rosa pastel)
BG_ADMIN_ROOM = QColor("#D8EDF8")   # Ambientes admin / recepción / lockers (celeste pastel)
BG_GARDEN     = QColor("#C6EBC9")   # Jardín Central (verde pastel)
BG_VOID       = QColor("#0B0F19")   # Vacío / ductos / escaleras (negro)
BORDER_COLOR  = QColor("#111827")   # Borde negro limpio

TEXT_DARK     = QColor("#111827")
TEXT_MUTED    = QColor("#4B5563")


@dataclass
class CroquisRoom:
    """Definición de un ambiente dentro del croquis."""
    id: str
    label: str
    floor: str                      # "Primer Piso" / "Segundo Piso"
    rect: Tuple[float, float, float, float]  # (x, y, w, h) normalizados en 0..1000, 0..700
    room_type: str = "class"        # "class", "admin", "garden", "void"
    aliases: List[str] = field(default_factory=list)


# ─── Definición de Ambientes - PISO 1 ─────────────────────────────────────────
PISO_1_ROOMS = [
    # Fila Superior
    CroquisRoom("alta_5", "Alta 5", "Primer Piso", (0, 0, 220, 160), "class",
                ["ALTA 5", "SALA ALTA FIDEL 5", "SALA ALTA FIDEL SHOCK TRAUMA", "SHOCK TRAUMA", "SALA DE ALTA 5"]),
    CroquisRoom("bano_doc", "Baño\nDocentes", "Primer Piso", (125, 105, 95, 55), "static", []),
    CroquisRoom("recep_top", "Recepción", "Primer Piso", (220, 0, 438, 105), "static", []),
    CroquisRoom("lockers_top", "Lockers", "Primer Piso", (220, 105, 218, 55), "static", []),
    CroquisRoom("void_top", "", "Primer Piso", (532, 105, 126, 55), "void", []),
    CroquisRoom("lab_micro", "Lab. Microbiología", "Primer Piso", (658, 0, 188, 40), "class",
                ["LAB. MICROBIOLOGÍA", "LAB MICROBIOLOGIA", "SALA DE MICROBIOLOGÍA", "MICROBIOLOGÍA", "MICROBIOLOGIA"]),
    CroquisRoom("lab_toma", "Lab. Toma de\nMuestra", "Primer Piso", (720, 40, 126, 68), "class",
                ["LAB. TOMA DE MUESTRA", "TOMA DE MUESTRA", "LAB. TECNOLOGÍA MÉDICA", "LAB TECNOLOGIA MEDICA"]),
    CroquisRoom("lab_gen", "Lab", "Primer Piso", (720, 108, 126, 52), "static", []),
    CroquisRoom("hab_4", "Habilidades 4", "Primer Piso", (846, 0, 154, 160), "class",
                ["HABILIDADES 4", "SALA DE HABILIDADES 4"]),

    # Columna Izquierda Central
    CroquisRoom("alta_1", "Sala de Alta 1", "Primer Piso", (0, 200, 156, 120), "class",
                ["SALA DE ALTA 1", "SALA ALTA 1", "ALTA 1", "SALA ALTA FIDEL OPERACIONES", "SALA ALTA FIDEL 1", "OPERACIONES"]),
    CroquisRoom("hosp_1", "Sala de Hospitalización 1", "Primer Piso", (0, 320, 156, 80), "class",
                ["SALA DE HOSPITALIZACIÓN 1", "SALA DE HOSPITALIZACION 1", "SALA DE HOSPITALIZ 1", "HOSPITALIZACION 1"]),
    CroquisRoom("alta_2", "Sala de Alta 2", "Primer Piso", (0, 400, 156, 120), "class",
                ["SALA DE ALTA 2", "SALA ALTA 2", "ALTA 2", "SALA ALTA FIDEL 2 - UCI", "SALA ALTA FIDEL 2", "UCI"]),

    # Centro
    CroquisRoom("jardin", "Jardín Central", "Primer Piso", (218, 200, 564, 265), "garden", []),
    CroquisRoom("recep_mid", "Recepción", "Primer Piso", (218, 465, 282, 55), "static", []),

    # Columna Derecha Central
    CroquisRoom("alta_4", "Sala de Alta 4", "Primer Piso", (846, 200, 154, 120), "class",
                ["SALA DE ALTA 4", "SALA ALTA 4", "ALTA 4", "SALA ALTA FIDEL 4-PARTO", "SALA ALTA FIDEL 4", "PARTO"]),
    CroquisRoom("hosp_2", "Sala de Hospitalización 2", "Primer Piso", (846, 320, 154, 80), "class",
                ["SALA DE HOSPITALIZACIÓN 2", "SALA DE HOSPITALIZACION 2", "SALA DE HOSPITALIZ 2", "HOSPITALIZACION 2"]),
    CroquisRoom("alta_3", "Sala de Alta 3", "Primer Piso", (846, 400, 154, 120), "class",
                ["SALA DE ALTA 3", "SALA ALTA 3", "ALTA 3", "SALA ALTA FIDEL 3-EMG", "SALA ALTA FIDEL 3", "EMG"]),

    # Fila Inferior
    CroquisRoom("cons_2", "Consultorio 2", "Primer Piso", (0, 572, 125, 68), "class",
                ["CONSULTORIO 2", "CONSULTORIO 02"]),
    CroquisRoom("cons_3", "Consultorio 3", "Primer Piso", (0, 640, 125, 60), "class",
                ["CONSULTORIO 3", "CONSULTORIO 03"]),
    CroquisRoom("cons_1", "Consultorio 1", "Primer Piso", (190, 572, 124, 68), "class",
                ["CONSULTORIO 1", "CONSULTORIO 01"]),
    CroquisRoom("cons_4", "Consultorio 4", "Primer Piso", (190, 640, 124, 60), "class",
                ["CONSULTORIO 4", "CONSULTORIO 04"]),
    CroquisRoom("lockers_banos", "Lockers + Baños público en general", "Primer Piso", (376, 572, 530, 128), "static", []),
    CroquisRoom("void_bot", "", "Primer Piso", (906, 572, 94, 128), "void", []),
]


# ─── Definición de Ambientes - PISO 2 ─────────────────────────────────────────
PISO_2_ROOMS = [
    # Fila Superior
    CroquisRoom("auditorio", "Auditorio", "Segundo Piso", (0, 0, 220, 160), "class",
                ["AUDITORIO"]),
    CroquisRoom("oficina_admin", "Oficina Administrativa", "Segundo Piso", (220, 0, 375, 160), "static", []),
    CroquisRoom("hab_5", "Sala de Habilidades 5", "Segundo Piso", (658, 0, 188, 160), "class",
                ["SALA DE HABILIDADES 5", "HABILIDADES 5"]),
    CroquisRoom("almacen", "Almacen", "Segundo Piso", (846, 0, 154, 160), "static", []),

    # Columna Izquierda Central
    CroquisRoom("hab_3", "Sala de Habilidades 3", "Segundo Piso", (0, 200, 156, 120), "class",
                ["SALA DE HABILIDADES 3", "HABILIDADES 3"]),
    CroquisRoom("hab_2", "Sala de Habilidades 2", "Segundo Piso", (0, 320, 156, 100), "class",
                ["SALA DE HABILIDADES 2", "HABILIDADES 2"]),
    CroquisRoom("hab_1", "Sala de Habilidades 1", "Segundo Piso", (0, 420, 156, 100), "class",
                ["SALA DE HABILIDADES 1", "HABILIDADES 1"]),

    # Centro: Vacío Central
    CroquisRoom("void_center", "", "Segundo Piso", (218, 200, 564, 320), "void", []),

    # Bloque ECOE (Derecha)
    CroquisRoom("ecoe_ctrl", "Sala de Control ECOEs", "Segundo Piso", (846, 200, 154, 55), "class",
                ["SALA DE CONTROL ECOES", "SALA DE CONTROL ECOE", "SALA DE OBS. ECOE", "OBS. ECOE", "CONTROL ECOES"]),
    CroquisRoom("ecoe_9", "ECOE 9", "Segundo Piso", (846, 255, 124, 40), "class",
                ["ECOE 9", "ECOE 09"]),
    CroquisRoom("ecoe_10", "ECOE 10", "Segundo Piso", (970, 255, 30, 97), "class",
                ["ECOE 10"]),
    CroquisRoom("ecoe_2", "ECOE 2", "Segundo Piso", (846, 320, 94, 32), "class",
                ["ECOE 2", "ECOE 02"]),
    CroquisRoom("ecoe_3", "ECOE 3", "Segundo Piso", (940, 320, 60, 32), "class",
                ["ECOE 3", "ECOE 03"]),
    CroquisRoom("ecoe_1", "ECOE 1", "Segundo Piso", (846, 352, 65, 68), "class",
                ["ECOE 1", "ECOE 01"]),
    CroquisRoom("ecoe_4", "ECOE 4", "Segundo Piso", (940, 352, 60, 68), "class",
                ["ECOE 4", "ECOE 04"]),
    CroquisRoom("ecoe_8", "ECOE 8", "Segundo Piso", (846, 420, 65, 68), "class",
                ["ECOE 8", "ECOE 08"]),
    CroquisRoom("ecoe_5", "ECOE 5", "Segundo Piso", (940, 420, 60, 68), "class",
                ["ECOE 5", "ECOE 05"]),
    CroquisRoom("ecoe_7", "ECOE 7", "Segundo Piso", (846, 488, 94, 32), "class",
                ["ECOE 7", "ECOE 07"]),
    CroquisRoom("ecoe_6", "ECOE 6", "Segundo Piso", (940, 488, 60, 32), "class",
                ["ECOE 6", "ECOE 06"]),

    # Fila Inferior
    CroquisRoom("imagenes", "Sala de Imágenes", "Segundo Piso", (0, 572, 156, 128), "class",
                ["SALA DE IMÁGENES", "SALA DE IMAGENES", "IMÁGENES", "IMAGENES"]),
    CroquisRoom("cons_6", "Consultorio 6", "Segundo Piso", (248, 572, 190, 64), "class",
                ["CONSULTORIO 6 - L 214", "CONSULTORIO 6", "CONSULTORIO 06"]),
    CroquisRoom("cons_7", "Consultorio 7", "Segundo Piso", (248, 636, 190, 64), "class",
                ["CONSULTORIO 7", "CONSULTORIO 07"]),
    CroquisRoom("cons_5", "Consultorio 5", "Segundo Piso", (532, 572, 190, 64), "class",
                ["CONSULTORIO 5 - L 213", "CONSULTORIO 5", "CONSULTORIO 05"]),
    CroquisRoom("cons_8", "Consultorio 8", "Segundo Piso", (532, 636, 190, 64), "class",
                ["CONSULTORIO 8", "CONSULTORIO 08"]),
    CroquisRoom("ecografia", "Sala de Ecografía", "Segundo Piso", (814, 572, 186, 128), "class",
                ["SALA DE ECOGRAFÍAS", "SALA DE ECOGRAFIA", "SALA DE ECOGRAFÍA", "SALA DE ECOGRAFIAS", "ECOGRAFÍA", "ECOGRAFIA"]),
]


# ─── Función de coincidencia de ambientes ─────────────────────────────────────
def is_room_match(session_room: str, croquis_room: CroquisRoom) -> bool:
    """Verifica si la sesión de clase pertenece a este ambiente del croquis."""
    if not session_room or not croquis_room.aliases:
        return False

    raw = session_room.upper().strip()
    if ":" in raw:
        raw = raw.split(":", 1)[1].strip()

    import re
    def simplify(s: str) -> str:
        s_clean = s.upper().replace("-", " ").replace(":", " ").replace(".", " ")
        s_clean = re.sub(r'\b0+(\d+)\b', r'\1', s_clean)
        return " ".join(s_clean.split())

    s_target = simplify(raw)

    for alias in croquis_room.aliases:
        s_alias = simplify(alias)
        if s_target == s_alias or s_alias in s_target or s_target in s_alias:
            return True

    return False


# ─── Widget Canvas del Croquis ────────────────────────────────────────────────
class CroquisCanvas(QWidget):
    """Canvas interactivo que dibuja el plano arquitectónico con ocupación de salas."""
    room_selected = pyqtSignal(object, list)  # (CroquisRoom, active_and_daily_sessions)

    def __init__(self, floor_name: str = "Primer Piso", parent=None):
        super().__init__(parent)
        self.floor_name = floor_name
        self.rooms: List[CroquisRoom] = PISO_1_ROOMS if "1" in floor_name or "Primer" in floor_name else PISO_2_ROOMS
        self.sessions: List[ClassSession] = []
        self.current_query_time: time = datetime.now().time()
        self._hovered_room: Optional[CroquisRoom] = None
        self._selected_room: Optional[CroquisRoom] = None

        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumSize(700, 480)

    def set_data(self, sessions: List[ClassSession], query_time: time):
        self.sessions = sessions
        self.current_query_time = query_time
        self.update()

    def set_floor(self, floor_name: str):
        self.floor_name = floor_name
        self.rooms = PISO_1_ROOMS if "1" in floor_name or "Primer" in floor_name else PISO_2_ROOMS
        self._hovered_room = None
        self._selected_room = None
        self.update()

    def set_query_time(self, query_time: time):
        self.current_query_time = query_time
        self.update()
        if self._selected_room:
            self._emit_selection(self._selected_room)

    # ── Métodos de consulta ───────────────────────────────────────────────────
    def get_room_sessions(self, room: CroquisRoom) -> List[ClassSession]:
        """Obtiene todas las sesiones del día para este ambiente."""
        return [s for s in self.sessions if is_room_match(s.room, room)]

    def get_active_session_at(self, room: CroquisRoom, q_time: time) -> Optional[ClassSession]:
        """Obtiene la sesión activa en el ambiente en la hora especificada."""
        q_minutes = q_time.hour * 60 + q_time.minute
        for s in self.get_room_sessions(room):
            s_start = s.start_time.hour * 60 + s.start_time.minute
            s_end = s.end_time.hour * 60 + s.end_time.minute
            if s_start <= q_minutes < s_end:
                return s
        return None

    # ── Coordenadas Escaladas ────────────────────────────────────────────────
    def _scale_rect(self, norm_rect: Tuple[float, float, float, float]) -> QRectF:
        cw = self.width()
        ch = self.height()
        nx, ny, nw, nh = norm_rect
        return QRectF(
            (nx / 1000.0) * cw,
            (ny / 700.0) * ch,
            (nw / 1000.0) * cw,
            (nh / 700.0) * ch
        )

    # ── Pintado del Croquis ──────────────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cw = self.width()
        ch = self.height()

        # 1. Fondo general de pasadizos (color durazno/crema)
        painter.fillRect(self.rect(), BG_CORRIDOR)

        # 2. Etiquetas de PASADIZO en los corredores
        self._draw_corridor_labels(painter, cw, ch)

        # 3. Dibujar cada ambiente
        for room in self.rooms:
            r = self._scale_rect(room.rect)
            active_sess = self.get_active_session_at(room, self.current_query_time)
            is_hover = (room == self._hovered_room)
            is_selected = (room == self._selected_room)

            self._draw_room(painter, room, r, active_sess, is_hover, is_selected)

        painter.end()

    def _draw_corridor_labels(self, painter: QPainter, cw: float, ch: float):
        """Dibuja las etiquetas sutiles de PASADIZO idénticas al croquis."""
        painter.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        painter.setPen(QColor("#4A3B32"))

        # Puntos de pasadizo según piso
        if "1" in self.floor_name or "Primer" in self.floor_name:
            pts = [
                (cw * 0.52, ch * 0.25, "PASADIZO"),
                (cw * 0.18, ch * 0.55, "PASADIZO"),
                (cw * 0.81, ch * 0.51, "PASADIZO"),
                (cw * 0.50, ch * 0.78, "PASADIZO"),
            ]
        else:
            pts = [
                (cw * 0.52, ch * 0.25, "PASADIZO"),
                (cw * 0.18, ch * 0.55, "PASADIZO"),
                (cw * 0.81, ch * 0.51, "PASADIZO"),
                (cw * 0.50, ch * 0.78, "PASADIZO"),
                (cw * 0.20, ch * 0.91, "PASADIZO"),
                (cw * 0.48, ch * 0.91, "PASADIZO"),
                (cw * 0.77, ch * 0.91, "PASADIZO"),
            ]

        for px, py, text in pts:
            painter.drawText(int(px - 30), int(py), 60, 20, Qt.AlignmentFlag.AlignCenter, text)

    def _draw_room(self, painter: QPainter, room: CroquisRoom, rect: QRectF,
                   active_sess: Optional[ClassSession], is_hover: bool, is_selected: bool):
        """Renderiza un ambiente con estilo idéntico al croquis y resalta si tiene clase."""
        # 1. Color base según tipo
        if room.room_type == "void":
            fill_color = BG_VOID
        elif room.room_type == "garden":
            fill_color = BG_GARDEN
        elif room.room_type in ("admin", "static"):
            fill_color = BG_ADMIN_ROOM
        else:
            # Sala de clase
            if active_sess:
                # Color del curso activo (Naranja / Celeste / Violeta)
                hex_col = get_session_color(active_sess.session_name)
                fill_color = QColor(hex_col)
            else:
                fill_color = BG_CLASS_ROOM

        # Efecto hover / selección (solo para salas de clase)
        if room.room_type == "class":
            if is_selected:
                fill_color = fill_color.lighter(120) if active_sess else QColor("#FBCFE8")
            elif is_hover:
                fill_color = fill_color.lighter(110)

        # 2. Dibujar fondo
        painter.fillRect(rect, fill_color)

        # 3. Dibujar borde
        border_pen = QPen(BORDER_COLOR, 2 if (is_selected and room.room_type == "class") else 1.2)
        if room.room_type == "garden":
            border_pen = QPen(QColor("#15803D"), 2)

        painter.setPen(border_pen)
        painter.drawRect(rect)

        # 4. Texto / Etiqueta del ambiente
        if room.room_type == "void":
            return

        # Calcular tamaño y color del texto
        text_color = QColor("#FFFFFF") if (active_sess and room.room_type == "class") else TEXT_DARK
        painter.setPen(text_color)

        # Ajuste vertical
        is_small = (rect.height() < 40 or rect.width() < 50)
        is_vertical_ecoe = (room.id == "ecoe_10")

        font_size = 6 if is_small else (8 if rect.width() > 100 and rect.height() > 50 else 7)
        font = QFont("Segoe UI", font_size, QFont.Weight.Bold if (active_sess or is_selected) else QFont.Weight.Medium)
        painter.setFont(font)

        if is_vertical_ecoe:
            # Dibujar texto vertical para ECOE 10
            painter.save()
            painter.translate(rect.center().x(), rect.center().y())
            painter.rotate(90)
            painter.drawText(QRectF(-rect.height()/2, -rect.width()/2, rect.height(), rect.width()),
                             Qt.AlignmentFlag.AlignCenter, room.label)
            painter.restore()
            return

        if active_sess:
            # Mostrar nombre de ambiente + CURSO ACTIVO
            course_name = get_course_short_name(active_sess.session_name)
            time_str = f"{active_sess.start_time.strftime('%H:%M')}-{active_sess.end_time.strftime('%H:%M')}"

            # Badge superior de curso
            h_split = rect.height() * 0.45
            top_rect = QRectF(rect.left() + 2, rect.top() + 2, rect.width() - 4, h_split)
            bot_rect = QRectF(rect.left() + 2, rect.top() + h_split, rect.width() - 4, rect.height() - h_split - 2)

            font_course = QFont("Segoe UI", max(7, font_size), QFont.Weight.Bold)
            painter.setFont(font_course)
            painter.drawText(top_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, f"📌 {course_name}")

            font_sub = QFont("Segoe UI", max(6, font_size - 1))
            painter.setFont(font_sub)
            painter.drawText(bot_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, f"{room.label}\n({time_str})")
        else:
            # Texto normal del ambiente
            painter.drawText(rect.adjusted(2, 2, -2, -2), Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, room.label)

    # ── Eventos de Mouse ─────────────────────────────────────────────────────
    def mouseMoveEvent(self, event):
        pos = event.position()
        found = None
        for room in self.rooms:
            r = self._scale_rect(room.rect)
            if r.contains(pos) and room.room_type == "class":
                found = room
                break

        if found != self._hovered_room:
            self._hovered_room = found
            self.update()

        if found:
            active_sess = self.get_active_session_at(found, self.current_query_time)
            time_str = self.current_query_time.strftime('%H:%M')
            if active_sess:
                course = get_course_short_name(active_sess.session_name)
                tip = (
                    f"<b>{found.label}</b><br>"
                    f"<b style='color:#F97316;'>🔴 Ocupado a las {time_str}</b><br>"
                    f"<b>Curso:</b> {course}<br>"
                    f"<b>Horario:</b> {active_sess.start_time.strftime('%H:%M')} - {active_sess.end_time.strftime('%H:%M')}<br>"
                    f"<b>Docente Líder:</b> {active_sess.lead_teacher or 'N/A'}<br>"
                    f"<i>(Clic para ver detalle y horarios del día)</i>"
                )
            else:
                daily = self.get_room_sessions(found)
                tip = (
                    f"<b>{found.label}</b><br>"
                    f"<b style='color:#10B981;'>🟢 Disponible a las {time_str}</b><br>"
                    f"<i>Clases hoy: {len(daily)} programada(s)</i><br>"
                    f"<i>(Clic para ver detalle)</i>"
                )
            QToolTip.showText(QCursor.pos(), tip, self)
        else:
            QToolTip.hideText()

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        pos = event.position()
        for room in self.rooms:
            r = self._scale_rect(room.rect)
            if r.contains(pos) and room.room_type == "class":
                self._selected_room = room
                self.update()
                self._emit_selection(room)
                break
        super().mousePressEvent(event)

    def _emit_selection(self, room: CroquisRoom):
        daily = self.get_room_sessions(room)
        self.room_selected.emit(room, daily)


# ─── Panel Lateral de Información del Ambiente ───────────────────────────────
class RoomDetailPanel(QFrame):
    """Panel lateral elegante que muestra la información detallada del ambiente seleccionado."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(340)
        self.setStyleSheet("""
            RoomDetailPanel {
                background: #FFFFFF;
                border-left: 1px solid #E5E7EB;
            }
            QLabel {
                font-family: 'Segoe UI';
            }
        """)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Encabezado
        self._title = QLabel("Detalle del Ambiente")
        self._title.setStyleSheet("font-size: 15px; font-weight: bold; color: #1E293B;")
        layout.addWidget(self._title)

        self._subtitle = QLabel("Haga clic en una sala del croquis para consultar.")
        self._subtitle.setStyleSheet("font-size: 12px; color: #64748B;")
        self._subtitle.setWordWrap(True)
        layout.addWidget(self._subtitle)

        # Tarjeta de Estado a la hora consultada
        self._card_status = QFrame()
        self._card_status.setStyleSheet("""
            QFrame {
                background: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
            }
        """)
        card_layout = QVBoxLayout(self._card_status)
        card_layout.setContentsMargins(12, 10, 12, 10)
        card_layout.setSpacing(6)

        self._lbl_badge = QLabel("ESTADO A LAS --:--")
        self._lbl_badge.setStyleSheet("""
            font-size: 11px; font-weight: bold;
            padding: 3px 8px; border-radius: 4px;
            background: #E2E8F0; color: #475569;
        """)
        card_layout.addWidget(self._lbl_badge)

        self._lbl_active_course = QLabel("Sin selección")
        self._lbl_active_course.setStyleSheet("font-size: 14px; font-weight: bold; color: #0F172A;")
        self._lbl_active_course.setWordWrap(True)
        card_layout.addWidget(self._lbl_active_course)

        self._lbl_active_info = QLabel("")
        self._lbl_active_info.setStyleSheet("font-size: 12px; color: #334155;")
        self._lbl_active_info.setWordWrap(True)
        card_layout.addWidget(self._lbl_active_info)

        layout.addWidget(self._card_status)

        # Título de agenda del día
        lbl_agenda = QLabel("📅 Programación del Día en este Ambiente:")
        lbl_agenda.setStyleSheet("font-size: 12px; font-weight: bold; color: #1E293B; margin-top: 6px;")
        layout.addWidget(lbl_agenda)

        # Scroll con lista de clases del día
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._list_widget = QWidget()
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(6)
        self._list_layout.addStretch()

        self._scroll.setWidget(self._list_widget)
        layout.addWidget(self._scroll, 1)

    def display_room_info(self, room: CroquisRoom, daily_sessions: List[ClassSession], query_time: time):
        self._title.setText(room.label)
        self._subtitle.setText(f"Piso: {room.floor} · {len(daily_sessions)} clase(s) programada(s) hoy")

        time_str = query_time.strftime("%H:%M")
        q_minutes = query_time.hour * 60 + query_time.minute

        active_sess = None
        for s in daily_sessions:
            s_start = s.start_time.hour * 60 + s.start_time.minute
            s_end = s.end_time.hour * 60 + s.end_time.minute
            if s_start <= q_minutes < s_end:
                active_sess = s
                break

        if active_sess:
            course = get_course_short_name(active_sess.session_name)
            col = get_session_color(active_sess.session_name)
            self._lbl_badge.setText(f"🔴 EN CURSO A LAS {time_str}")
            self._lbl_badge.setStyleSheet(f"""
                font-size: 11px; font-weight: bold;
                padding: 3px 8px; border-radius: 4px;
                background: {col}; color: #FFFFFF;
            """)
            self._lbl_active_course.setText(f"Curso: {course}")
            self._lbl_active_info.setText(
                f"🕐 Horario: {active_sess.start_time.strftime('%H:%M')} → {active_sess.end_time.strftime('%H:%M')} ({active_sess.duration_minutes} min)\n"
                f"👨‍🏫 Docente Líder: {active_sess.lead_teacher or 'N/A'}\n"
                f"👥 Colaboradores: {active_sess.collab_teachers or 'N/A'}"
            )
        else:
            self._lbl_badge.setText(f"🟢 AMBIENTE DISPONIBLE A LAS {time_str}")
            self._lbl_badge.setStyleSheet("""
                font-size: 11px; font-weight: bold;
                padding: 3px 8px; border-radius: 4px;
                background: #DCFCE7; color: #15803D;
            """)
            self._lbl_active_course.setText("Sin clase en esta hora")
            self._lbl_active_info.setText("El ambiente se encuentra libre a la hora seleccionada.")

        # Reconstruir lista del día
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not daily_sessions:
            lbl_empty = QLabel("No hay clases programadas para este ambiente hoy.")
            lbl_empty.setStyleSheet("color: #94A3B8; font-size: 11px; font-style: italic; padding: 8px;")
            self._list_layout.insertWidget(0, lbl_empty)
            return

        sorted_sessions = sorted(daily_sessions, key=lambda s: s.start_time)
        for idx, s in enumerate(sorted_sessions):
            is_cur = (s == active_sess)
            course = get_course_short_name(s.session_name)
            col = get_session_color(s.session_name)

            item_frame = QFrame()
            item_frame.setStyleSheet(f"""
                QFrame {{
                    background: {'#FEF3C7' if is_cur else '#F8FAFC'};
                    border: 1px solid {'#F59E0B' if is_cur else '#E2E8F0'};
                    border-left: 4px solid {col};
                    border-radius: 6px;
                }}
            """)
            i_layout = QVBoxLayout(item_frame)
            i_layout.setContentsMargins(10, 6, 10, 6)
            i_layout.setSpacing(2)

            header_txt = f"{s.start_time.strftime('%H:%M')} - {s.end_time.strftime('%H:%M')}  ·  {course}"
            lbl_h = QLabel(header_txt)
            lbl_h.setStyleSheet(f"font-size: 11px; font-weight: {'bold' if is_cur else '600'}; color: #1E293B;")
            i_layout.addWidget(lbl_h)

            lbl_doc = QLabel(f"Docente: {s.lead_teacher or 'N/A'}")
            lbl_doc.setStyleSheet("font-size: 10px; color: #64748B;")
            i_layout.addWidget(lbl_doc)

            self._list_layout.insertWidget(idx, item_frame)


# ─── Vista Completa de Croquis con Controles de Tiempo ─────────────────────────
class CroquisView(QWidget):
    """
    Vista completa con barra superior de control horario,
    canvas del croquis interactivo y panel lateral de detalle.
    """

    def __init__(self, floor_name: str = "Primer Piso", parent=None):
        super().__init__(parent)
        self.floor_name = floor_name
        self._sessions: List[ClassSession] = []
        self._is_live_clock: bool = True
        self._setup_ui()

        # Timer para reloj en vivo
        self._live_timer = QTimer(self)
        self._live_timer.timeout.connect(self._on_live_tick)
        self._live_timer.start(10_000)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Barra de Control de Hora
        main_layout.addWidget(self._build_time_control_bar())

        # 2. Contenedor Central Splitter (Canvas Croquis + Panel Lateral)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background: #E2E8F0;
                width: 1px;
            }
        """)

        # Canvas con Scroll
        self._canvas = CroquisCanvas(self.floor_name)
        self._canvas.room_selected.connect(self._on_room_selected)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self._canvas)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: #F8FAFC; }")
        splitter.addWidget(scroll_area)

        # Panel lateral
        self._detail_panel = RoomDetailPanel()
        splitter.addWidget(self._detail_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter, 1)

    def _build_time_control_bar(self) -> QWidget:
        bar = QFrame()
        bar.setFixedHeight(48)
        bar.setStyleSheet("""
            QFrame {
                background: #FFFFFF;
                border-bottom: 1px solid #E2E8F0;
            }
        """)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 4, 14, 4)
        layout.setSpacing(10)

        # Indicador de Modo / Hora
        lbl_icon = QLabel("🕒")
        lbl_icon.setStyleSheet("font-size: 16px;")
        layout.addWidget(lbl_icon)

        self._lbl_time_display = QLabel("Hora seleccionada: --:--")
        self._lbl_time_display.setStyleSheet("""
            font-size: 13px; font-weight: bold; color: #1E40AF;
            background: #EFF6FF; border: 1px solid #BFDBFE;
            border-radius: 6px; padding: 4px 10px;
        """)
        layout.addWidget(self._lbl_time_display)

        # Slider de Horario (07:00 a 22:00 -> 420 a 1320 minutos)
        layout.addWidget(QLabel("07:00"))
        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(7 * 60, 22 * 60)
        self._slider.setSingleStep(15)
        self._slider.setPageStep(30)
        self._slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #E2E8F0;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #3B82F6;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #2563EB;
                border: 2px solid #FFFFFF;
                width: 16px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #1D4ED8;
            }
        """)
        now = datetime.now().time()
        init_min = min(22 * 60, max(7 * 60, now.hour * 60 + now.minute))
        self._slider.setValue(init_min)
        self._slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self._slider, 1)
        layout.addWidget(QLabel("22:00"))

        # Botón "Hora Actual"
        self._btn_now = QPushButton("⚡ Hora Actual")
        self._btn_now.setFixedHeight(28)
        self._btn_now.setStyleSheet("""
            QPushButton {
                background: #EFF6FF;
                color: #2563EB;
                border: 1px solid #BFDBFE;
                border-radius: 5px;
                font-weight: 600;
                font-size: 11px;
                padding: 0 10px;
            }
            QPushButton:hover { background: #DBEAFE; }
        """)
        self._btn_now.clicked.connect(self._set_to_now)
        layout.addWidget(self._btn_now)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedHeight(24)
        sep.setStyleSheet("color: #CBD5E1; background: #CBD5E1; width: 1px;")
        layout.addWidget(sep)

        # Leyenda Rápida
        lbl_leg = QLabel("Leyenda:")
        lbl_leg.setStyleSheet("font-size: 11px; font-weight: bold; color: #64748B;")
        layout.addWidget(lbl_leg)

        for name, col in [("Medicina", COLOR_MEDICINA), ("Enfermería", COLOR_ENFERMERIA), ("Obstetricia", COLOR_OBSTETRICIA), ("Libre", "#F5DDEC")]:
            dot = QLabel(f"● {name}")
            dot.setStyleSheet(f"color: {col}; font-size: 11px; font-weight: bold;")
            layout.addWidget(dot)

        self._update_time_label(time(init_min // 60, init_min % 60))
        return bar

    def load_sessions(self, sessions: List[ClassSession]):
        self._sessions = sessions
        cur_time = self._get_selected_time()
        self._canvas.set_data(sessions, cur_time)

    def set_floor(self, floor_name: str):
        self.floor_name = floor_name
        self._canvas.set_floor(floor_name)

    def _get_selected_time(self) -> time:
        val = self._slider.value()
        return time(val // 60, val % 60)

    def _update_time_label(self, q_time: time):
        self._lbl_time_display.setText(f"⏰ Hora seleccionada: {q_time.strftime('%H:%M')}")

    def _on_slider_changed(self, value: int):
        self._is_live_clock = False
        q_time = time(value // 60, value % 60)
        self._update_time_label(q_time)
        self._canvas.set_query_time(q_time)

    def _set_to_now(self):
        now = datetime.now().time()
        init_min = min(22 * 60, max(7 * 60, now.hour * 60 + now.minute))
        self._is_live_clock = True
        self._slider.setValue(init_min)

    def _on_live_tick(self):
        if self._is_live_clock:
            self._set_to_now()

    def _on_room_selected(self, room: CroquisRoom, daily_sessions: List[ClassSession]):
        self._detail_panel.display_room_info(room, daily_sessions, self._get_selected_time())
