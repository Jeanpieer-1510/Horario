# SimClic - Sistema de Visualización de Horarios Universitarios 🏥📅

**SimClic** es una aplicación de escritorio nativa para Windows diseñada para la gestión y visualización dinámica de la ocupación de salas, laboratorios y consultorios clínicos universitarios en una línea de tiempo diaria.

---

## 🛠️ Tecnologías Utilizadas

La aplicación fue desarrollada utilizando un stack moderno, robusto y de alto rendimiento en Python:

- **Lenguaje Principal**: [Python 3.11+](https://www.python.org/)
- **Interfaz Gráfica (GUI)**: [PyQt6](https://pypi.org/project/PyQt6/) (Bindings oficiales de Qt 6 para Python, renderizado vectorial mediante `QPainter` y `QGraphics/QWidget` nativos).
- **Procesamiento de Datos**: 
  - [pandas](https://pandas.pydata.org/): Normalización, filtrado y estructura de datos tabulares.
  - [openpyxl](https://openpyxl.readthedocs.io/): Lectura e interpretación de archivos Excel `.xlsx` / `.xls`.
- **Empaquetado y Distribución**:
  - [PyInstaller](https://pyinstaller.org/): Generación del binario ejecutable independiente (`SimClic.exe`) sin necesidad de que el usuario final tenga Python instalado.
  - [Inno Setup](https://jrsoftware.org/isinfo.php): Generador del instalador formal de Windows con asistente de instalación, accesos directos y compatibilidad con actualizaciones automáticas.

---

## ✨ Características y Funcionalidades

### 1. 📊 Vista de Línea de Tiempo Diaria (Timeline)
- **Rango Horario Completo**: Visualización continua desde las **07:00 hasta las 22:00 hrs** con subdivisiones visuales cada 30 minutos.
- **Reloj e Indicador en Tiempo Real**: Línea vertical roja que marca en vivo la hora actual del día y se actualiza minuto a minuto.
- **Bloques Dinámicos de Clase**: Los bloques se posicionan y dimensionan automáticamente en píxeles según la hora de inicio y duración exacta de cada sesión.
- **Detalle al Pasar el Mouse (Hover)**: Tooltip interactivo con información completa (carrera, docente líder, colaboradores, pacientes estandarizados, ambiente y duración).
- **Diálogo Modal al Clic**: Al hacer clic en cualquier bloque se despliega una ficha completa de la sesión.

### 2. 🎨 Código de Colores por Carrera / Especialidad
El software identifica automáticamente el tipo de curso a partir del nombre o código de la sesión y le asigna su color temático correspondiente:

| Carrera / Área | Color | Prefijos y Cursos Reconocidos |
|---|:---:|---|
| **Medicina Humana** | 🟧 **Naranja** | `SimPed`, `SimQx`, `SimGO`, `SCI`, `SBS`, `MED SBS`, `PAX`, `Ext Cirg`, `Ext GyO`, `Ext Med`, `Ext Ped`, `Ecografia` |
| **Enfermería** | 🟦 **Celeste** | `ENF`, `ENFERMERIA` |
| **Obstetricia** | 🟪 **Violeta** | `OBST`, `OBSTETRICIA` |

### 3. 🏢 Filtrado Dinámico por Piso
Ubicado en la barra inferior, permite alternar la vista central entre:
- **Piso 1**: Muestra los 14 ambientes clínicos del primer piso.
- **Piso 2**: Muestra los 21 ambientes clínicos del segundo piso (incluyendo ECOE 01 al 10 y Salas de Habilidades 1 al 5).
- **Todos los Pisos**: Despliega la totalidad de salas agrupadas con separadores visuales.
- **Contador Automático**: Muestra en tiempo real cuántas clases programadas hay en el piso seleccionado.

### 4. 📂 Importación Inteligente de Excel
- Botón **"Cargar Excel"** con selector de archivos del sistema.
- **Detección Flexible de Columnas**: Mapea automáticamente nombres de columnas por encabezado o posición (`Piso`, `Ambiente`, `Sesión`, `Hora Inicio`, `Hora Fin`, `Docente Líder`, etc.).
- **Tolerancia a Formatos de Ambiente**: Reconoce nombres de salas tanto si vienen con código institucional (`SL02LA25: SALA DE HABILIDADES 4`, `SL02TA24: CONSULTORIO 5 - L 213`) como con el nombre directo.
- **Botón Recargar**: Permite refrescar los datos del archivo en un solo clic tras hacer modificaciones en Excel.

---

## 🏛️ Estructura de Ambientes Clínicos

### 🏥 1er Piso (14 Ambientes)
1. Sala de Microbiología
2. LAB. TECNOLOGÍA MÉDICA
3. SALA DE HABILIDADES 4
4. SALA ALTA FIDEL 4-Parto
5. SALA DE HOSPITALIZ 2
6. SALA ALTA FIDEL 3-EMG
7. SALA ALTA FIDEL 2 - UCI
8. SALA DE HOSPITALIZACIÓN 1
9. SALA ALTA FIDEL OPERACIONES
10. SALA ALTA FIDEL SHOCK TRAUMA
11. CONSULTORIO 01
12. CONSULTORIO 02
13. CONSULTORIO 03
14. CONSULTORIO 04

### 🏢 2do Piso (21 Ambientes)
1. SALA DE HABILIDADES 5
2. SALA DE HABILIDADES 1
3. SALA DE HABILIDADES 2
4. SALA DE HABILIDADES 3
5. SALA DE IMÁGENES
6. SALA DE ECOGRAFÍAS
7. CONSULTORIO 5 - L 213
8. CONSULTORIO 6 - L 214
9. CONSULTORIO 7
10. CONSULTORIO 8
11. SALA DE OBS. ECOE
12. ECOE 01 al ECOE 10 (10 estaciones)

---

## 📁 Estructura del Proyecto

```
Simclic/
├── main.py                     # Punto de entrada de la aplicación
├── requirements.txt            # Dependencias del entorno Python
├── build.spec                  # Configuración de compilación con PyInstaller
├── installer.iss               # Script de empaquetado para Inno Setup
├── create_test_excel.py        # Generador del archivo Excel de prueba
├── datos_prueba.xlsx           # Excel de demostración con 15 sesiones
├── app/
│   ├── models/
│   │   └── schedule.py         # Modelos de datos, salas por piso y reglas de colores
│   ├── services/
│   │   └── excel_reader.py     # Lector y parseador robusto de Excel
│   └── ui/
│       ├── main_window.py      # Ventana principal, barra superior y diálogos
│       ├── timeline_view.py    # Canvas gráfico de la línea de tiempo
│       └── floor_panel.py      # Barra selectora y filtro por pisos
└── dist/
    └── SimClic/
        └── SimClic.exe         # Ejecutable independiente compilado
```

---

## 🚀 Guía de Uso y Ejecución

### 1. Ejecución en Modo Desarrollo
Si tienes Python instalado y quieres correr el código fuente:
```powershell
# Instalar dependencias
pip install -r requirements.txt

# Iniciar la aplicación
python main.py
```

### 2. Compilación del Ejecutable (.exe)
Para generar el archivo ejecutable portátil:
```powershell
python -m PyInstaller --clean --noconfirm build.spec
```
El resultado se generará en: `dist\SimClic\SimClic.exe`.

### 3. Creación del Instalador de Windows
1. Descarga e instala [Inno Setup Compiler](https://jrsoftware.org/isdl.php).
2. Abre el archivo `installer.iss`.
3. Haz clic en **Build / Compile** (o presiona `Ctrl + F9`).
4. El instalador final quedará listo en la carpeta `dist_installer\`.
