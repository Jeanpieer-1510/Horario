"""
Servicio de lectura de archivos Excel con el formato de horarios universitarios.

Formato esperado del Excel:
  Columna A: Piso (ej: "Primer Piso", "Segundo Piso")
  Columna B: Ambiente (ej: "SL02LA25: SALA DE HABILIDADES 4")
  Columna C: Sesión (ej: "[PAX] - VALORACION DE LA ESCENA Y CINEMATICA DEL TRAUMA")
  Columna D: Hora Inicio (ej: "07:00")
  Columna E: Hora Fin (ej: "08:40")
  Columna F: Docente Líder
  Columna G: Docentes Colaboradores
  Columna H: Pacientes Estandarizados
"""
import re
from datetime import time, date
from typing import List, Optional, Tuple

import pandas as pd

from app.models.schedule import ClassSession, find_floor_for_room


def parse_time(value) -> Optional[time]:
    """
    Parsea un valor de hora desde múltiples formatos:
    - "07:00", "7:00", "07:00:00"
    - datetime.time
    - float (Excel serial)
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None

    if isinstance(value, time):
        return value

    if hasattr(value, 'hour'):  # datetime o time
        return time(value.hour, value.minute)

    if isinstance(value, str):
        value = value.strip()
        # Formato HH:MM o H:MM
        match = re.match(r'^(\d{1,2}):(\d{2})', value)
        if match:
            h, m = int(match.group(1)), int(match.group(2))
            if 0 <= h <= 23 and 0 <= m <= 59:
                return time(h, m)

    if isinstance(value, float):
        # Excel almacena tiempos como fracciones de día
        total_minutes = int(round(value * 24 * 60))
        h = total_minutes // 60
        m = total_minutes % 60
        return time(h % 24, m)

    return None


def safe_str(value) -> str:
    """Convierte un valor a string de forma segura."""
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return str(value).strip()


def read_excel(filepath: str) -> Tuple[List[ClassSession], List[str]]:
    """
    Lee un archivo Excel y retorna (lista de sesiones, lista de errores).

    Args:
        filepath: Ruta al archivo .xlsx o .xls

    Returns:
        Tuple con lista de ClassSession y lista de mensajes de error/advertencia
    """
    sessions: List[ClassSession] = []
    errors: List[str] = []

    try:
        # Intentar leer el Excel; la primera fila puede ser encabezado
        df = pd.read_excel(filepath, header=0, dtype=str)
    except Exception as e:
        return [], [f"Error al abrir el archivo: {str(e)}"]

    # Detectar columnas por nombre o posición
    col_floor = None
    col_room = None
    col_session = None
    col_start = None
    col_end = None
    col_lead = None
    col_collab = None
    col_patients = None

    columns_lower = {col.lower().strip(): col for col in df.columns}

    # Mapeo de nombres de columna conocidos
    floor_names = ['piso', 'floor']
    room_names = ['ambiente', 'room', 'sala', 'aula']
    session_names = ['sesión', 'sesion', 'session', 'clase', 'actividad']
    start_names = ['hora inicio', 'hora_inicio', 'inicio', 'start', 'hora de inicio']
    end_names = ['hora fin', 'hora_fin', 'fin', 'end', 'hora de fin', 'hora final']
    lead_names = ['docente líder', 'docente lider', 'docente', 'lead', 'teacher']
    collab_names = ['docentes colaboradores', 'colaboradores', 'collab']
    patients_names = ['pacientes estandarizados', 'pacientes', 'patients']

    def find_col(names, default_idx):
        for name in names:
            if name in columns_lower:
                return columns_lower[name]
        # Fallback a posición
        cols = list(df.columns)
        if default_idx < len(cols):
            return cols[default_idx]
        return None

    col_floor = find_col(floor_names, 0)
    col_room = find_col(room_names, 1)
    col_session = find_col(session_names, 2)
    col_start = find_col(start_names, 3)
    col_end = find_col(end_names, 4)
    col_lead = find_col(lead_names, 5)
    col_collab = find_col(collab_names, 6)
    col_patients = find_col(patients_names, 7)

    # Re-leer el Excel para que las columnas de hora sean parseadas correctamente
    try:
        df_raw = pd.read_excel(filepath, header=0)
    except Exception:
        df_raw = df

    for idx, row in df_raw.iterrows():
        row_num = idx + 2  # +2 porque row 1 es encabezado

        try:
            floor_val = safe_str(row.get(col_floor, "")) if col_floor else ""
            room_val = safe_str(row.get(col_room, "")) if col_room else ""
            session_val = safe_str(row.get(col_session, "")) if col_session else ""
            lead_val = safe_str(row.get(col_lead, "")) if col_lead else ""
            collab_val = safe_str(row.get(col_collab, "")) if col_collab else ""
            patients_val = safe_str(row.get(col_patients, "")) if col_patients else ""

            # Parsear horas
            start_raw = row.get(col_start) if col_start else None
            end_raw = row.get(col_end) if col_end else None

            start_t = parse_time(start_raw)
            end_t = parse_time(end_raw)

            # Validaciones básicas
            if not room_val and not session_val:
                continue  # Fila vacía

            if not start_t:
                errors.append(f"Fila {row_num}: Hora de inicio no válida ('{start_raw}'). Se omite.")
                continue

            if not end_t:
                errors.append(f"Fila {row_num}: Hora de fin no válida ('{end_raw}'). Se omite.")
                continue

            # Si no viene piso, inferirlo del nombre del ambiente
            if not floor_val:
                floor_val = find_floor_for_room(room_val)

            sessions.append(ClassSession(
                id=len(sessions) + 1,
                floor=floor_val,
                room=room_val,
                session_name=session_val,
                start_time=start_t,
                end_time=end_t,
                lead_teacher=lead_val,
                collab_teachers=collab_val,
                standardized_patients=patients_val,
            ))

        except Exception as e:
            errors.append(f"Fila {row_num}: Error al procesar - {str(e)}")

    return sessions, errors
