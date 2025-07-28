# AI Prompt Studio

Un generador/organizador de prompts, diseñado específicamente para Stable Diffusion y otros modelos de generación de imágenes.

## 🎨 Características Principales

### Interfaz de Usuario
- **Layout de tres secciones**: Sidebar izquierda (280px), grid de categorías superior, y sección de prompt inferior
- **Tema oscuro moderno** con paleta de colores consistente
- **Grid responsivo** con scroll vertical para las categorías
- **Efectos hover suaves** y transiciones animadas

### Sistema de Categorías
- **40+ categorías organizadas** en tarjetas individuales
- **Tags visuales** para valores comunes en cada categoría
- **Inputs editables** con validación automática
- **Generación en tiempo real** con debounce de 300ms

### Generación de Prompts
- **Combinación automática** de todas las categorías activas
- **Eliminación de duplicados** automática
- **Orden lógico** de términos (Calidad → Estilo → Sujeto → Detalles → Composición)
- **Validación de inputs** y limpieza automática

### Gestión de Datos
- **Persistencia local** de configuraciones y datos
- **Historial de prompts** con límite configurable
- **Exportación** en formatos JSON y TXT
- **Gestión de personajes y escenas** con descripciones

### Funcionalidades Avanzadas
- **Atajos de teclado**: Ctrl+C (copiar), Ctrl+S (guardar), Ctrl+E (exportar)
- **Negative prompt colapsable** con animación suave
- **Feedback visual** en todas las acciones
- **Navegación con Tab** entre inputs

## 🛠️ Requisitos del Sistema

### Software
- Python 3.8 o superior
- CustomTkinter 5.2.2
- Pillow (PIL)
- pyperclip

### Hardware
- Resolución mínima: 1280x720
- Memoria RAM: 200MB mínimo
- Espacio en disco: 50MB

## 📦 Instalación

1. **Clonar el repositorio**:
```bash
git clone <repository-url>
cd AppPrompts
```

2. **Crear entorno virtual**:
```bash
python -m venv appPrompt
```

3. **Activar el entorno virtual**:
```bash
# Windows
appPrompt\Scripts\activate

# Linux/Mac
source appPrompt/bin/activate
```

4. **Instalar dependencias**:
```bash
pip install customtkinter pillow pyperclip
```

5. **Ejecutar la aplicación**:
```bash
python main.py
```

## 🎯 Uso de la Aplicación

### Interfaz Principal
1. **Sidebar izquierda**: Selecciona personajes y escenas predefinidas
2. **Grid de categorías**: Completa los campos para generar tu prompt
3. **Sección de prompt**: Visualiza el resultado en tiempo real

### Generando Prompts
1. **Selecciona categorías**: Haz clic en los inputs de las categorías que desees usar
2. **Escribe valores**: Ingresa términos específicos o usa los tags sugeridos
3. **Observa en tiempo real**: El prompt se actualiza automáticamente
4. **Ajusta el negative prompt**: Expande la sección para personalizar

### Guardando y Exportando
- **Copiar**: Ctrl+C o botón "Copiar" para portapapeles
- **Guardar**: Ctrl+S o botón "Guardar" para historial local
- **Exportar**: Ctrl+E o botón "Exportar" para archivo JSON/TXT

## 📁 Estructura del Proyecto

```
AppPrompts/
├── main.py                 # Punto de entrada de la aplicación
├── ui/                     # Componentes de interfaz
│   ├── main_window.py      # Ventana principal
│   ├── sidebar.py          # Panel lateral
│   ├── category_grid.py    # Grid de categorías
│   ├── prompt_section.py   # Sección de prompt
│   └── ui_elements.py      # Elementos UI personalizados
├── logic/                  # Lógica de negocio
│   └── prompt_generator.py # Generador de prompts
├── config/                 # Configuración
│   └── settings.py         # Gestión de datos y configuraciones
├── data/                   # Datos persistentes (se crea automáticamente)
│   ├── settings.json       # Configuraciones de la app
│   ├── characters.json     # Personajes guardados
│   ├── scenes.json         # Escenas guardadas
│   └── prompt_history.json # Historial de prompts
└── assets/                 # Recursos (iconos, imágenes)
```

## 🎨 Paleta de Colores

- **Fondo principal**: `#1a1a1a`
- **Fondo secundario**: `#252525`
- **Bordes**: `#404040`
- **Acentos**: `#6366f1`
- **Hover**: `#4f46e5`
- **Éxito**: `#10b981`
- **Error**: `#ef4444`

## ⌨️ Atajos de Teclado

| Acción | Atajo |
|--------|-------|
| Copiar prompt | `Ctrl+C` |
| Guardar prompt | `Ctrl+S` |
| Exportar prompt | `Ctrl+E` |
| Navegar inputs | `Tab` |
| Expandir negative prompt | `Enter` en el título |

## 🔧 Configuración

### Archivo de Configuración
La aplicación crea automáticamente un archivo `data/settings.json` con las siguientes opciones:

```json
{
  "theme": "dark",
  "window_size": "1400x900",
  "sidebar_width": 280,
  "auto_save": true,
  "max_history": 100,
  "default_negative_prompt": "blurry, low quality, distorted, deformed, ugly, bad anatomy"
}
```

### Personalización
- **Tema**: Cambiar entre "dark" y "light"
- **Tamaño de ventana**: Ajustar resolución inicial
- **Ancho del sidebar**: Modificar el ancho del panel lateral
- **Auto-guardado**: Habilitar/deshabilitar guardado automático
- **Máximo historial**: Número máximo de prompts en el historial
- **Negative prompt por defecto**: Texto predeterminado para negative prompts

## 🚀 Características Técnicas

### Rendimiento
- **Debounce de 300ms** para generación de prompts
- **Respuesta <100ms** para interacciones de UI
- **Uso de memoria <200MB** en uso normal
- **Virtual scrolling** para grandes cantidades de categorías

### Arquitectura
- **Componentes modulares** y reutilizables
- **Separación clara** entre lógica y presentación
- **Manejo de errores** consistente
- **Patrones de diseño** limpios

### Persistencia
- **JSON** para intercambio y almacenamiento
- **Retrocompatibilidad** en formatos de datos
- **Validación de integridad** al cargar configuraciones
- **Backup automático** de datos críticos



## 🐛 Reportar Problemas

Si encuentras algún problema o tienes una sugerencia, por favor:

1. Revisa los issues existentes
2. Crea un nuevo issue con:
   - Descripción detallada del problema
   - Pasos para reproducir
   - Información del sistema
   - Capturas de pantalla (si aplica)

## 📞 Soporte

Para soporte técnico o preguntas:

- 📧 Email: [tu-email@ejemplo.com]
- 💬 Discord: [enlace-al-servidor]
- 📖 Documentación: [enlace-a-la-doc]

