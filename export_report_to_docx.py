"""
Script para convertir el INFORME_TECNICO.md a un documento de Word (.docx)
con diseño profesional y formateado de tablas, títulos y bloques de código.
"""
import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, color_hex):
    """Establece el color de fondo de una celda."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    """Establece los márgenes internos de una celda en twips."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_report_docx():
    doc = Document()

    # Configuración de página (A4 con márgenes de 2.5 cm)
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Colores institucionales
    COLOR_PRIMARY = RGBColor(30, 43, 74)     # Azul oscuro (#1E2B4A)
    COLOR_SECONDARY = RGBColor(37, 99, 235)  # Azul acento (#2563EB)
    COLOR_TEXT = RGBColor(31, 41, 55)        # Gris oscuro (#1F2937)
    COLOR_MUTED = RGBColor(107, 114, 128)    # Gris medio (#6B7280)

    # Estilos base
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Segoe UI'
    style_normal.font.size = Pt(10.5)
    style_normal.font.color.rgb = COLOR_TEXT

    # ── TÍTULO PRINCIPAL ──
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(4)
    run_title = title_p.add_run("INFORME TÉCNICO DE ARQUITECTURA Y LÓGICA DEL SISTEMA")
    run_title.font.name = 'Segoe UI'
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = COLOR_PRIMARY

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_before = Pt(0)
    sub_p.paragraph_format.space_after = Pt(20)
    run_sub = sub_p.add_run("Sistema de Visualización de Horarios Universitarios · Especificación de Sistemas y Algoritmos")
    run_sub.font.size = Pt(11.5)
    run_sub.font.color.rgb = COLOR_SECONDARY
    run_sub.font.bold = True

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Segoe UI'
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Segoe UI'
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = COLOR_SECONDARY
        return p

    def add_p(text, bold_prefix=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.bold = True
            r_b.font.color.rgb = COLOR_PRIMARY
        p.add_run(text)
        return p

    def add_bullet(bold_part, normal_part):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        r_b = p.add_run(bold_part)
        r_b.bold = True
        r_b.font.color.rgb = COLOR_PRIMARY
        p.add_run(normal_part)
        return p

    def add_code_block(code_text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.right_indent = Inches(0.2)
        
        # Tabla de 1 celda para simular caja de código
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        set_cell_background(cell, "F3F4F6")
        set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
        
        cp = cell.paragraphs[0]
        cp.paragraph_format.space_before = Pt(0)
        cp.paragraph_format.space_after = Pt(0)
        c_run = cp.add_run(code_text)
        c_run.font.name = 'Consolas'
        c_run.font.size = Pt(9.5)
        c_run.font.color.rgb = RGBColor(30, 41, 59)
        
        doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # ── 1. RESUMEN EJECUTIVO ──
    add_h1("1. Resumen Ejecutivo")
    add_p("El Sistema de Visualización de Horarios es una aplicación de escritorio de alto rendimiento diseñada para la gestión, control y seguimiento visual de ocupación de ambientes clínicos universitarios (salas de simulación, consultorios médicos y estaciones ECOE) sobre una línea de tiempo diaria interactiva.")
    add_p("El software procesa de forma automática hojas de cálculo Excel heterogéneas, normaliza la información de salas y cursos, clasifica las sesiones por carrera profesional mediante códigos de colores, y proyecta las sesiones en un canvas gráfico 2D con precisión al minuto y actualización en tiempo real.")

    # ── 2. ARQUITECTURA GENERAL ──
    add_h1("2. Arquitectura General del Sistema")
    add_p("La arquitectura se basa en un patrón desacoplado MVC (Model-View-Service) adaptado al framework PyQt6:")
    
    add_bullet("Capa de Dominio y Modelos (app/models/schedule.py): ", "Define la estructura de datos ClassSession, el catálogo maestro de salas de 1er y 2do piso, y los diccionarios de asignación de colores por carrera.")
    add_bullet("Capa de Ingesta y Servicios (app/services/excel_reader.py): ", "Lector tolerante a fallos que procesa archivos .xlsx / .xls, detecta columnas de manera flexible y traduce formatos de tiempo (texto, datetime y números de serie de Excel).")
    add_bullet("Capa Gráfica Vectorial (app/ui/timeline_view.py): ", "Canvas gráfico desarrollado sobre QPainter que realiza el cálculo de coordenadas bidimensionales (X, Y, Ancho, Alto), dibuja los bloques de clase, cuadrículas de tiempo y la línea de tiempo real.")
    add_bullet("Capa de Control y Filtros (app/ui/floor_panel.py): ", "Barra selectora que emite eventos de filtrado para alternar de manera instantánea entre Piso 1, Piso 2 o la vista consolidada.")
    add_bullet("Capa de Ventana Principal (app/ui/main_window.py): ", "Orquestador de la interfaz, encargado de la barra superior, reloj digital, navegador de fechas y modales de detalle de clase.")

    # ── 3. LÓGICA DE INTERPRETACIÓN Y DIFERENCIAS HORARIAS ──
    add_h1("3. Lógica de Interpretación y Diferencias Horarias")
    add_p("Uno de los desafíos principales en la integración con Excel radica en que los usuarios ingresan los horarios en formatos dispares. El sistema resuelve esto mediante un parser multinivel:")

    add_h2("A. Algoritmo de Parsing de Horas (parse_time)")
    add_bullet("Paso 1 (Objetos nativos): ", "Si la celda ya es un objeto time o datetime de Python, extrae directamente hour y minute.")
    add_bullet("Paso 2 (Cadenas de texto): ", "Si es un string ('07:00', '7:30', '07:00:00'), aplica expresiones regulares ^(\\d{1,2}):(\\d{2}) para capturar horas y minutos con o sin ceros.")
    add_bullet("Paso 3 (Serial decimal de Excel): ", "Si la celda es un número flotante (ej: 0.291666), Excel almacena las horas como una fracción de un día de 24 horas. Se calcula: total_minutos = round(valor * 24 * 60).")

    add_h2("B. Fórmulas Matemáticas de Duración y Desplazamiento")
    add_p("Cada hora se convierte a una magnitud escalar continua en minutos desde medianoche (00:00):")
    add_code_block("Minutos_Inicio = (Hora_Inicio * 60) + Minuto_Inicio\nMinutos_Fin    = (Hora_Fin * 60) + Minuto_Fin\nDuracion_Minutos = Minutos_Fin - Minutos_Inicio")
    add_p("Ejemplo práctico (Sesión de 07:00 a 08:40):")
    add_bullet("Inicio: ", "(7 * 60) + 0 = 420 minutos")
    add_bullet("Fin: ", "(8 * 60) + 40 = 520 minutos")
    add_bullet("Duración: ", "520 - 420 = 100 minutos de clase")

    # ── 4. LÓGICA DE CLASIFICACIÓN DE CURSOS Y COLORES ──
    add_h1("4. Lógica de Clasificación de Cursos y Asignación de Colores")
    add_p("Para asignar el color exacto a cada bloque, el sistema analiza el nombre de la sesión mediante un pipeline de normalización y concordancia léxica:")

    add_h2("A. Pipeline de Normalización (clean_text)")
    add_p("Elimina corchetes, guiones, dos puntos y espacios redundantes (ejemplo: '[SimQx] - Taller de Cirugía' se transforma en 'SIMQX TALLER DE CIRUGIA').")

    add_h2("B. Tabla de Clasificación por Carrera")
    
    # Tabla de colores
    tbl_col = doc.add_table(rows=4, cols=3)
    tbl_col.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Carrera / Especialidad", "Color Asignado", "Prefijos y Cursos Identificados"]
    for i, h in enumerate(headers):
        c = tbl_col.cell(0, i)
        set_cell_background(c, "1E2B4A")
        set_cell_margins(c, 100, 100, 120, 120)
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(10)

    rows_data = [
        ("Medicina Humana", "Naranja (#F97316)", "SimPed, SimQx, SimGO, SCI, SBS, MED SBS, PAX, Ext Cirg, Ext GyO, Ext Med, Ext Ped, Ecografia"),
        ("Enfermería", "Celeste (#0EA5E9)", "ENF, ENFERMERIA, ENFERMERÍA"),
        ("Obstetricia", "Violeta (#8B5CF6)", "OBST, OBSTETRICIA"),
    ]

    for row_idx, (carrera, color, prefijos) in enumerate(rows_data, 1):
        c0 = tbl_col.cell(row_idx, 0)
        c1 = tbl_col.cell(row_idx, 1)
        c2 = tbl_col.cell(row_idx, 2)
        
        bg = "F9FAFB" if row_idx % 2 == 1 else "FFFFFF"
        for c in [c0, c1, c2]:
            set_cell_background(c, bg)
            set_cell_margins(c, 80, 80, 100, 100)

        c0.paragraphs[0].add_run(carrera).font.bold = True
        c1.paragraphs[0].add_run(color)
        c2.paragraphs[0].add_run(prefijos)

    add_p("")

    # ── 5. LÓGICA DE POSICIONAMIENTO ESPACIAL 2D ──
    add_h1("5. Lógica de Posicionamiento Espacial en el Canvas (X, Y, Ancho, Alto)")
    add_p("Cada clase se proyecta en el canvas 2D mediante un rectángulo geométrico QRectF(X, Y, Ancho, Alto).")

    add_h2("A. Parámetros de Escala Gráfica")
    add_bullet("ROOM_LABEL_WIDTH = 190 px: ", "Ancho fijo asignado a la columna de salas a la izquierda.")
    add_bullet("HOUR_WIDTH = 110 px: ", "Escala horizontal que representa 60 minutos de tiempo (1.83 px por minuto).")
    add_bullet("ROW_HEIGHT = 52 px: ", "Alto de cada fila de ambiente clínico.")
    add_bullet("HEADER_HEIGHT = 44 px: ", "Alto de la cabecera superior con las marcas horarias.")
    add_bullet("START_HOUR = 7 (07:00 AM): ", "Origen del eje temporal horizontal.")

    add_h2("B. Fórmulas de Transformación 2D")
    add_code_block(
        "Coordenada X:\n"
        "X = ROOM_LABEL_WIDTH + ((Minutos_Inicio - (7 * 60)) / 60.0) * HOUR_WIDTH\n\n"
        "Ancho (Width):\n"
        "Ancho = (Duracion_Minutos / 60.0) * HOUR_WIDTH\n\n"
        "Coordenada Y:\n"
        "Y = HEADER_HEIGHT + (Indice_Fila_Sala * ROW_HEIGHT) + MARGEN_VERTICAL\n\n"
        "Alto (Height):\n"
        "Alto = ROW_HEIGHT - (2 * MARGEN_VERTICAL)"
    )

    add_h2("C. Motor de Resolución de Filas de Ambiente (_get_room_row)")
    add_p("Permite enlazar cualquier nombre de sala proveniente del Excel con el catálogo del sistema:")
    add_bullet("1. Búsqueda exacta: ", "Si el texto coincide idénticamente con el nombre de la sala.")
    add_bullet("2. Limpieza de prefijos: ", "Si el Excel incluye códigos como 'SL02TA24: CONSULTORIO 5 - L 213', extrae la parte posterior a los dos puntos.")
    add_bullet("3. Tolerancia a ceros: ", "Equipara mediante expresiones regulares números con y sin ceros a la izquierda (ej: 'ECOE 1' se mapea automáticamente a 'ECOE 01').")

    # ── 6. LÓGICA DE FILTRADO POR PISOS ──
    add_h1("6. Lógica de Filtrado Dinámico por Pisos")
    add_p("Cuando el usuario selecciona una pestaña en el panel inferior:")
    add_bullet("1. Emisión de Evento: ", "FloorPanel emite la señal floor_selected('Primer Piso') o floor_selected('Segundo Piso').")
    add_bullet("2. Conmutación de Ambientes Activos: ", "TimelineView restringe la lista de salas visibles únicamente a las del piso seleccionado (14 salas en Piso 1, 21 salas en Piso 2).")
    add_bullet("3. Descarte de Sesiones Fuera de Rango: ", "Las clases de otros pisos devuelven Fila = -1 en la resolución de ambientes y no se dibujan.")
    add_bullet("4. Redimensionamiento Inmediato: ", "El canvas recalcula su altura total: Alto_Total = HEADER_HEIGHT + (Cantidad_Salas_Activas * ROW_HEIGHT), ajustando automáticamente las barras de desplazamiento.")

    # ── 7. LÓGICA DE INTERACCIÓN EN TIEMPO REAL ──
    add_h1("7. Lógica de Interactividad y Tiempo Real")
    add_bullet("Línea de Hora Actual (Indicador Rojo): ", "Un temporizador de 60 segundos actualiza la coordenada X de la hora actual en vivo si el reloj se encuentra en el rango de 07:00 a 22:00 hrs.")
    add_bullet("Detección de Cursor y Tooltips: ", "El canvas guarda las posiciones de todos los bloques. Al mover el cursor, evalúa rect.contains(mouse_pos) para activar el tooltip flotante con información del docente, colaboradores y pacientes.")
    add_bullet("Detalle al Clic: ", "Abre una ventana modal con el desglose institucional completo de la sesión.")

    # Guardar archivo
    output_path = os.path.join(os.path.dirname(__file__), "INFORME_TECNICO.docx")
    doc.save(output_path)
    print(f"Documento Word generado exitosamente: {output_path}")

if __name__ == "__main__":
    create_report_docx()
