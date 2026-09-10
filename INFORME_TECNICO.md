# Informe Técnico de Arquitectura y Lógica del Sistema 📐🏥

## 1. Resumen Ejecutivo
El **Sistema de Visualización de Horarios** es una aplicación de escritorio diseñada para resolver el problema de la gestión y seguimiento visual de ocupación de ambientes clínicos (salas de simulación, consultorios y estaciones ECOE) en entornos universitarios. 

Transforma datos tabulares no estructurados provenientes de hojas de cálculo Excel en un canvas gráfico interactivo en tiempo real con codificación por colores, filtrado modular por pisos y posicionamiento temporal milimétrico.

---

## 2. Arquitectura General del Sistema

El software sigue una arquitectura basada en capas desacopladas con patrón **MVC adaptado a PyQt6 (Model-View-Service)**:

```
┌─────────────────────────────────────────────────────────────┐
│                       INTERFAZ (UI)                         │
│  MainWindow  ───►  TimelineView (Canvas)  ───►  FloorPanel  │
└───────────────┬─────────────────────────────┬───────────────┘
                │                             │
                ▼                             ▼
┌──────────────────────────────┐    ┌─────────────────────────┐
│     SERVICIOS (Services)     │    │     MODELOS (Models)    │
│       excel_reader.py        │───►│       schedule.py       │
└──────────────────────────────┘    └─────────────────────────┘
```

### Componentes y Roles:
1. **`app/models/schedule.py` (Capa de Dominio)**:
   - Define la entidad `ClassSession` (dataclass).
   - Almacena el catálogo maestro de salas de 1er y 2do Piso.
   - Contiene los diccionarios de reglas para la clasificación de cursos y colores.

2. **`app/services/excel_reader.py` (Capa de Ingesta y Parsing)**:
   - Carga el archivo `.xlsx` o `.xls`.
   - Identifica columnas dinámicamente sin depender de nombres rígidos.
   - Parsea formatos heterogéneos de horas y maneja excepciones fila por fila.

3. **`app/ui/timeline_view.py` (Capa Gráfica Vectorial)**:
   - Implementa un widget personalizado `TimelineCanvas` con renderizado mediante `QPainter`.
   - Transforma coordenadas temporales a píxeles en pantalla (eje X) y ambientes a filas (eje Y).
   - Dibuja en vivo la línea de tiempo actual y los tooltips interactivos.

4. **`app/ui/floor_panel.py` (Capa de Control de Filtros)**:
   - Controla las pestañas inferiores para alternar entre "Piso 1", "Piso 2" y "Todos".
   - Notifica a la vista central mediante señales (`pyqtSignal`) para reconstruir la grilla.

5. **`app/ui/main_window.py` (Capa Orquestadora)**:
   - Integra la barra superior, navegador de fechas, reloj digital, timeline y panel de pisos.

---

## 3. Lógica de Interpretación y Diferencias Horarias

### A. Parsing de Tiempos Heterogéneos (`parse_time`)
Los archivos Excel pueden almacenar las horas en diferentes formatos internos:
1. **Texto plano** (ej: `"07:00"`, `"7:30"`, `"14:00:00"`).
2. **Objetos nativos `time` / `datetime`** de Python.
3. **Números en coma flotante (Serial de Excel)**: Excel almacena las horas como una fracción decimal de un día de 24 horas (ej: `0.291666...` = `07:00`).

**Algoritmo implementado en `excel_reader.py`**:
```python
def parse_time(value) -> Optional[time]:
    # 1. Si ya es tipo time o datetime
    if hasattr(value, 'hour'):
        return time(value.hour, value.minute)

    # 2. Si es string -> Expresión regular
    if isinstance(value, str):
        match = re.match(r'^(\d{1,2}):(\d{2})', value.strip())
        if match:
            return time(int(match.group(1)), int(match.group(2)))

    # 3. Si es float (Serial de Excel)
    if isinstance(value, float):
        total_minutes = int(round(value * 24 * 60))
        return time((total_minutes // 60) % 24, total_minutes % 60)
```

### B. Cálculo de Duración y Minutos desde Medianoche
Cada sesión convierte sus horas en magnitudes continuas en minutos para facilitar cálculos trigonométricos/lineales:

$$\text{Minutos Inicio} = (\text{Hora} \times 60) + \text{Minuto}$$

$$\text{Minutos Fin} = (\text{Hora} \times 60) + \text{Minuto}$$

$$\text{Duración en Minutos} = \text{Minutos Fin} - \text{Minutos Inicio}$$

*Ejemplo*: Una clase de `07:00` a `08:40`:
- $\text{Inicio} = (7 \times 60) + 0 = 420\text{ min}$
- $\text{Fin} = (8 \times 60) + 40 = 520\text{ min}$
- $\text{Duración} = 520 - 420 = 100\text{ minutos}$.

---

## 4. Lógica de Clasificación de Cursos y Asignación de Colores

El sistema debe decidir qué color le corresponde a una sesión analizando el texto del campo `Sesión`.

### A. Normalización del Texto (`clean_text`)
El texto recibido puede incluir corchetes, prefijos o caracteres especiales: `"[SimQx] - Taller de Cirugía"`, `"EXT GYO: PEDIATRIA"`, etc.
El método de limpieza elimina signos de puntuación y unifica espacios para evaluar palabras completas:

```python
def clean_text(text: str) -> str:
    cleaned = text.upper().replace("[", " ").replace("]", " ").replace(":", " ").replace("-", " ")
    return " ".join(cleaned.split())
```

### B. Matriz de Prioridad de Clasificación

El sistema ejecuta una evaluación por jerarquía en orden estricto:

```
[Texto de la sesión] 
       │
       ├─► ¿Contiene prefijo de ENFERMERÍA (ENF)? ──────► [🟦 CELESTE]
       │
       ├─► ¿Contiene prefijo de OBSTETRICIA (OBST)? ────► [🟪 VIOLETA]
       │
       ├─► ¿Contiene prefijo de MEDICINA HUMANA? ───────► [🟧 NARANJA]
       │     (SimPed, SimQx, SimGO, SCI, SBS, PAX,
       │      Ext Cirg, Ext GyO, Ext Med, Ext Ped, Ecografia)
       │
       └─► Si no coincide con ninguno ──────────────────► [🟧 NARANJA (Default)]
```

Cada color define un par **`(Color Base, Color Acento)`**:
- **Medicina Humana**: Base `#F97316` (Naranja), Acento `#FFEDD5`
- **Enfermería**: Base `#0EA5E9` (Celeste), Acento `#E0F2FE`
- **Obstetricia**: Base `#8B5CF6` (Violeta), Acento `#EDE9FE`

---

## 5. Lógica de Posicionamiento Espacial en el Canvas

El área de dibujo transforma los datos abstractos (Tiempo y Sala) en un rectángulo 2D definido por:
$$\text{Rectángulo} = (X, Y, \text{Ancho}, \text{Alto})$$

### Constantes de Layout:
- $\text{ROOM\_LABEL\_WIDTH} = 190\text{ px}$ (Ancho de la columna izquierda de salas)
- $\text{HOUR\_WIDTH} = 110\text{ px}$ (Píxeles asignados a cada hora de 60 minutos)
- $\text{ROW\_HEIGHT} = 52\text{ px}$ (Alto de cada fila de ambiente)
- $\text{HEADER\_HEIGHT} = 44\text{ px}$ (Alto del encabezado de horas)
- $\text{START\_HOUR} = 7$ ($07:00\text{ AM}$)

### A. Cálculo del Eje Horizontal ($X$ y $\text{Ancho}$)
La coordenada $X$ se calcula a partir del desplazamiento respecto a las 07:00 AM:

$$X = \text{ROOM\_LABEL\_WIDTH} + \left( \frac{\text{Minutos Inicio} - (7 \times 60)}{60} \right) \times \text{HOUR\_WIDTH}$$

$$\text{Ancho (Width)} = \left( \frac{\text{Duración en Minutos}}{60} \right) \times \text{HOUR\_WIDTH}$$

*Ejemplo (07:00 a 08:40, Duración 100 min)*:
- $X = 190 + \left( \frac{420 - 420}{60} \right) \times 110 = 190\text{ px}$
- $\text{Ancho} = \left( \frac{100}{60} \right) \times 110 = 183.33\text{ px}$

### B. Cálculo del Eje Vertical ($Y$ y $\text{Alto}$) y Mapeo de Salas
Para ubicar la fila $Y$ correcta, el sistema implementa un motor de resolución difusa (`_get_room_row`):

1. **Búsqueda Exacta Directa**: Si el nombre coincide al 100% con la lista del piso activo.
2. **Remoción de Códigos de Ambiente**: Si el Excel incluye códigos como `SL02TA24: CONSULTORIO 5 - L 213`, se extrae la parte posterior a los dos puntos (`:`).
3. **Normalización de Ceros en Números (Zero-Padding Ignorance)**:
   - `ECOE 1` $\leftrightarrow$ `ECOE 01`
   - `CONSULTORIO 5` $\leftrightarrow$ `CONSULTORIO 05`
   Mediante expresiones regulares se homologa cualquier número a su valor entero.

Una vez obtenido el índice de fila $i$:
$$Y = \text{HEADER\_HEIGHT} + (i \times \text{ROW\_HEIGHT}) + \text{BLOCK\_V\_MARGIN}$$
$$\text{Alto (Height)} = \text{ROW\_HEIGHT} - (2 \times \text{BLOCK\_V\_MARGIN})$$

---

## 6. Lógica de Filtrado por Pisos

Cuando el usuario hace clic en **"Piso 1"**, **"Piso 2"** o **"Todos"**:

1. **Emisión de Señal**: `FloorPanel` emite `floor_selected("Primer Piso")`.
2. **Redefinición de Lista Activa**: `TimelineView` actualiza su variable `active_rooms`:
   - Si es Piso 1: Únicamente 14 salas de primer piso.
   - Si es Piso 2: Únicamente 21 salas de segundo piso.
   - Si es Todos: Ambas listas concatenadas con separadores azules.
3. **Reindexación y Filtrado Automático**:
   - Al iterar las sesiones, aquellas cuyo ambiente no pertenezca al piso seleccionado retornan $\text{Fila} = -1$ en `_get_room_row` y no se dibujan.
4. **Recálculo de Dimensiones del Canvas**:
   $$\text{Alto Total} = \text{HEADER\_HEIGHT} + (\text{Cantidad de Salas Activas} \times \text{ROW\_HEIGHT})$$
   El widget ajusta su tamaño y las barras de desplazamiento (scroll) se adaptan de inmediato.

---

## 7. Lógica de Interacción en Tiempo Real

### A. Línea de Hora Actual (Indicador Rojo)
- Un `QTimer` se ejecuta cada 60 segundos.
- Obtiene la hora del sistema: $\text{Hora Actual}$.
- Si $\text{Hora Actual} \in [07:00, 22:00]$:
  Calcula su $X_{\text{actual}}$ y dibuja una línea vertical roja de 2px con un círculo en el encabezado.

### B. Detección de Hover y Tooltip
En el evento `mouseMoveEvent(event)`:
- El canvas almacena en memoria una lista de tuplas `(QRectF, ClassSession)` con las coordenadas exactas de cada bloque dibujado.
- Se ejecuta la función de intersección geométrica:
  $$\text{if } \text{rect}.\text{contains}(\text{posicion\_mouse}):$$
- Si hay colisión, cambia el cursor a mano interactiva (`PointingHandCursor`), ilumina el bloque y despliega el `QToolTip` flotante formateado en HTML.

---

## 8. Conclusiones
La arquitectura implementada garantiza:
1. **Rendimiento**: Renderizado vectorial directo por hardware sin sobrecarga de widgets individuales por cada bloque de clase.
2. **Tolerancia a Fallos**: Admite variaciones comunes en archivos Excel universitarios (celdas combinadas, códigos de ambiente, horas en texto o números).
3. **Mantenibilidad**: La separación entre catálogo de salas (`schedule.py`), motor de dibujo (`timeline_view.py`) y lectura de datos (`excel_reader.py`) permite modificar salas o colores sin afectar la estructura central.
