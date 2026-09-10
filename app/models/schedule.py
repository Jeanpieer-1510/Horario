"""
Modelos de datos para la aplicación de horarios universitarios.
"""
from dataclasses import dataclass, field
from datetime import time, date
from typing import Optional


@dataclass
class ClassSession:
    """Representa una sesión de clase."""
    id: int
    floor: str              # "Primer Piso" / "Segundo Piso"
    room: str               # Nombre del ambiente
    session_name: str       # Nombre de la sesión
    start_time: time        # Hora de inicio
    end_time: time          # Hora de fin
    lead_teacher: str       # Docente líder
    collab_teachers: str    # Docentes colaboradores
    standardized_patients: str  # Pacientes estandarizados
    date: Optional[date] = None  # Fecha (si viene en el Excel)

    @property
    def duration_minutes(self) -> int:
        """Duración en minutos."""
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        return max(0, end_minutes - start_minutes)

    @property
    def start_minutes_from_midnight(self) -> int:
        """Minutos desde medianoche para cálculo de posición."""
        return self.start_time.hour * 60 + self.start_time.minute


# Definición de ambientes por piso
FLOOR_1_ROOMS = [
    "Sala de Microbiología",
    "LAB. TECNOLOGÍA MÉDICA",
    "SALA DE HABILIDADES 4",
    "SALA ALTA FIDEL 4-Parto",
    "SALA DE HOSPITALIZ 2",
    "SALA ALTA FIDEL 3-EMG",
    "SALA ALTA FIDEL 2 - UCI",
    "SALA DE HOSPITALIZACIÓN 1",
    "SALA ALTA FIDEL OPERACIONES",
    "SALA ALTA FIDEL SHOCK TRAUMA",
    "CONSULTORIO 01",
    "CONSULTORIO 02",
    "CONSULTORIO 03",
    "CONSULTORIO 04",
]

FLOOR_2_ROOMS = [
    "AUDITORIO",
    "SALA DE HABILIDADES 5",
    "SALA DE HABILIDADES 1",
    "SALA DE HABILIDADES 2",
    "SALA DE HABILIDADES 3",
    "SALA DE IMÁGENES",
    "SALA DE ECOGRAFÍAS",
    "CONSULTORIO 5 - L 213",
    "CONSULTORIO 6 - L 214",
    "CONSULTORIO 7",
    "CONSULTORIO 8",
    "SALA DE OBS. ECOE",
    "ECOE 01",
    "ECOE 02",
    "ECOE 03",
    "ECOE 04",
    "ECOE 05",
    "ECOE 06",
    "ECOE 07",
    "ECOE 08",
    "ECOE 09",
    "ECOE 10",
]


FLOORS = {
    "Primer Piso": FLOOR_1_ROOMS,
    "Segundo Piso": FLOOR_2_ROOMS,
}

# Colores por carrera / tipo de curso
# 1. Medicina Humana -> Naranja
# 2. Enfermería -> Celeste
# 3. Obstetricia -> Violeta

COLOR_MEDICINA = "#F97316"     # Naranja
COLOR_ENFERMERIA = "#0EA5E9"   # Celeste
COLOR_OBSTETRICIA = "#8B5CF6"  # Violeta
COLOR_DEFAULT = "#10B981"      # Verde (otros)

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


def get_course_short_name(session_name: str) -> str:
    """
    Extrae únicamente el nombre/código del curso al que pertenece la sesión,
    sin mostrar el tema completo.
    Ejemplo: '[SimPed] - Paro Cardiorrespiratorio' -> 'SimPed'
    """
    if not session_name:
        return ""

    raw = session_name.strip()
    norm = clean_text(raw)

    # 1. Enfermería -> ENF
    for pref in ENFERMERIA_PREFIXES:
        if norm.startswith(pref) or f" {pref} " in f" {norm} ":
            return "ENF"

    # 2. Obstetricia -> OBST
    for pref in OBSTETRICIA_PREFIXES:
        if norm.startswith(pref) or f" {pref} " in f" {norm} ":
            return "OBST"

    # 3. Medicina Humana (prefijos específicos)
    med_mappings = [
        ("SIMPED", "SimPed"),
        ("SIMQX", "SimQx"),
        ("SIMGO", "SimGO"),
        ("MED SBS", "MED SBS"),
        ("MED-SBS", "MED SBS"),
        ("SBS", "MED SBS"),
        ("SCI", "SCI"),
        ("PAX", "PAX"),
        ("EXT CIRG", "Ext Cirg"),
        ("EXT CIRUGIA", "Ext Cirg"),
        ("EXT CIR", "Ext Cirg"),
        ("EXT GYO", "Ext GyO"),
        ("EXT GY O", "Ext GyO"),
        ("EXT G Y O", "Ext GyO"),
        ("EXT. GYO", "Ext GyO"),
        ("EXT G&O", "Ext GyO"),
        ("EXT MED", "Ext Med"),
        ("EXT. MED", "Ext Med"),
        ("EXT PED", "Ext Ped"),
        ("EXT. PED", "Ext Ped"),
        ("ECOGRAFIA", "Ecografía"),
        ("ECOGRAFÍA", "Ecografía"),
        ("ECOGRAF", "Ecografía"),
    ]

    for pref, display in med_mappings:
        if norm.startswith(pref) or f" {pref} " in f" {norm} ":
            return display

    # 4. Si viene entre corchetes ej. [Curso ABC]
    if "[" in raw and "]" in raw:
        start = raw.find("[") + 1
        end = raw.find("]")
        inside = raw[start:end].strip()
        if inside:
            return inside

    # 5. Si viene con guión o dos puntos ej. "Curso - Tema"
    for sep in [" - ", ": ", " – "]:
        if sep in raw:
            return raw.split(sep, 1)[0].strip()

    # Si no tiene separador, tomar las 2 primeras palabras
    parts = raw.split()
    if len(parts) <= 2:
        return raw
    return " ".join(parts[:2])


def get_session_color(session_name: str, index: int = 0) -> str:
    """Retorna el color basado en la carrera o prefijo del curso."""
    if not session_name:
        return COLOR_MEDICINA

    norm = clean_text(session_name)

    # Revisar Enfermería (Celeste)
    for pref in ENFERMERIA_PREFIXES:
        if norm.startswith(pref) or f" {pref} " in f" {norm} ":
            return COLOR_ENFERMERIA

    # Revisar Obstetricia (Violeta)
    for pref in OBSTETRICIA_PREFIXES:
        if norm.startswith(pref) or f" {pref} " in f" {norm} ":
            return COLOR_OBSTETRICIA

    # Revisar Medicina Humana (Naranja)
    for pref in MEDICINA_PREFIXES:
        if norm.startswith(pref) or f" {pref} " in f" {norm} ":
            return COLOR_MEDICINA

    return COLOR_MEDICINA


def normalize_room_name(raw_name: str) -> str:
    """
    Normaliza el nombre del ambiente para compararlo con la lista maestra.
    El Excel puede traer 'SL02LA25: SALA DE HABILIDADES 4' → 'SALA DE HABILIDADES 4'
    """
    if not raw_name:
        return ""
    # Quitar código si viene en formato "CODIGO: NOMBRE"
    if ":" in raw_name:
        parts = raw_name.split(":", 1)
        return parts[1].strip().upper()
    return raw_name.strip().upper()


def find_floor_for_room(raw_room: str) -> str:
    """Determina el piso a partir del nombre del ambiente."""
    normalized = normalize_room_name(raw_room).lower()

    for room in FLOOR_1_ROOMS:
        if room.lower() in normalized or normalized in room.lower():
            return "Primer Piso"

    for room in FLOOR_2_ROOMS:
        if room.lower() in normalized or normalized in room.lower():
            return "Segundo Piso"

    return "Primer Piso"  # fallback

