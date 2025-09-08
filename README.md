# Editor de Videos con Streamlit

Aplicación web para edición y procesamiento de videos desarrollada con Streamlit. Permite cargar videos, añadir música, aplicar filtros, agregar transiciones y exportar el resultado final.

## Características

- **Carga de videos**: Soporte para drag & drop y selección manual de archivos MP4.
- **Módulo de música**: Añade archivos de audio MP3 con ajuste automático de duración.
- **Procesamiento de videos**: Concatenación automática de clips y configuración personalizable.
- **Herramientas de edición**: Filtros visuales predefinidos y transiciones entre clips.
- **Exportación**: Descarga del video final con todos los elementos procesados.

## Requisitos

```
streamlit>=1.22.0
python-ffmpeg>=2.0.0
moviepy>=1.0.3
pillow>=9.0.0
numpy>=1.22.0
pandas>=1.4.0
watchdog>=2.1.0
```

## Instalación

1. Clona este repositorio:
   ```
   git clone https://github.com/tu-usuario/streamlit-video-editor.git
   cd streamlit-video-editor
   ```

2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

3. Ejecuta la aplicación:
   ```
   streamlit run app.py
   ```

## Uso

1. **Carga de Videos**: Arrastra y suelta archivos MP4 o selecciónalos manualmente.
2. **Música**: Añade un archivo de audio MP3 opcional.
3. **Procesamiento**: Configura dimensiones, filtros y transiciones, luego procesa los videos.
4. **Exportación**: Descarga el video final procesado.

## Despliegue en Streamlit Cloud

1. Sube el código a un repositorio de GitHub.
2. Accede a [Streamlit Cloud](https://streamlit.io/cloud).
3. Conecta tu repositorio de GitHub.
4. Configura la aplicación y despliégala.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para más detalles.