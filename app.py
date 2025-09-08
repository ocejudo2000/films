import streamlit as st
import os
import tempfile
import time
from pathlib import Path
import numpy as np
from PIL import Image
from moviepy.editor import *
import moviepy.video.fx.all as vfx

# Configuración de la página
st.set_page_config(
    page_title="Editor de Videos",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .upload-section {
        border: 2px dashed #cccccc;
        border-radius: 5px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    .filter-preview {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Inicialización de variables de sesión
def init_session_state():
    if 'video_files' not in st.session_state:
        st.session_state.video_files = []
    if 'audio_file' not in st.session_state:
        st.session_state.audio_file = None
    if 'output_width' not in st.session_state:
        st.session_state.output_width = 1280
    if 'output_height' not in st.session_state:
        st.session_state.output_height = 720
    if 'selected_filter' not in st.session_state:
        st.session_state.selected_filter = 'Ninguno'
    if 'selected_transition' not in st.session_state:
        st.session_state.selected_transition = 'Ninguna'
    if 'export_format' not in st.session_state:
        st.session_state.export_format = 'mp4'
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'output_file' not in st.session_state:
        st.session_state.output_file = None
    if 'temp_dir' not in st.session_state:
        st.session_state.temp_dir = tempfile.TemporaryDirectory()

init_session_state()

# Función para aplicar filtros a los videos
def apply_filter(clip, filter_name):
    if filter_name == 'Blanco y Negro':
        return clip.fx(vfx.blackwhite)
    elif filter_name == 'Sepia':
        return clip.fx(vfx.sepia)
    elif filter_name == 'Colorizar':
        return clip.fx(vfx.colorx, 1.5)
    elif filter_name == 'Invertir':
        return clip.fx(vfx.invert_colors)
    elif filter_name == 'Brillo':
        return clip.fx(vfx.colorx, 1.2)
    else:  # Ninguno
        return clip

# Función para aplicar transiciones entre clips
def apply_transition(clips, transition_name):
    if len(clips) <= 1:
        return clips[0] if clips else None
    
    if transition_name == 'Fade':
        final_clips = []
        for i, clip in enumerate(clips):
            if i < len(clips) - 1:
                final_clips.append(clip.crossfadeout(1.0))
            else:
                final_clips.append(clip)
        return concatenate_videoclips(final_clips)
    
    elif transition_name == 'Slide':
        # Implementación simple de transición de deslizamiento
        final_clips = []
        for i, clip in enumerate(clips):
            if i < len(clips) - 1:
                duration = clip.duration
                clip = clip.set_position(lambda t: (0, 0) if t < duration - 1 else (-(t - (duration - 1)) * clip.w, 0))
                final_clips.append(clip)
            else:
                final_clips.append(clip)
        return concatenate_videoclips(final_clips, method="compose")
    
    else:  # Ninguna
        return concatenate_videoclips(clips)

# Función para procesar los videos
def process_videos():
    if not st.session_state.video_files:
        st.error("Por favor, carga al menos un video.")
        return
    
    with st.spinner('Procesando videos...'):
        try:
            # Cargar clips de video
            video_clips = []
            for video_file in st.session_state.video_files:
                temp_file = os.path.join(st.session_state.temp_dir.name, video_file.name)
                with open(temp_file, 'wb') as f:
                    f.write(video_file.getbuffer())
                clip = VideoFileClip(temp_file)
                
                # Redimensionar al tamaño de salida deseado
                clip = clip.resize(width=st.session_state.output_width, height=st.session_state.output_height)
                
                # Aplicar filtro seleccionado
                clip = apply_filter(clip, st.session_state.selected_filter)
                
                video_clips.append(clip)
            
            # Aplicar transiciones y concatenar clips
            final_clip = apply_transition(video_clips, st.session_state.selected_transition)
            
            # Agregar audio si está disponible
            if st.session_state.audio_file:
                temp_audio_file = os.path.join(st.session_state.temp_dir.name, st.session_state.audio_file.name)
                with open(temp_audio_file, 'wb') as f:
                    f.write(st.session_state.audio_file.getbuffer())
                
                audio_clip = AudioFileClip(temp_audio_file)
                
                # Ajustar la duración del audio para que coincida con el video
                video_duration = final_clip.duration
                if audio_clip.duration < video_duration:
                    # Repetir el audio hasta que sea suficientemente largo
                    repeats = int(np.ceil(video_duration / audio_clip.duration))
                    audio_clip = concatenate_audioclips([audio_clip] * repeats)
                
                # Recortar el audio para que coincida exactamente con la duración del video
                audio_clip = audio_clip.subclip(0, video_duration)
                
                # Establecer el audio en el clip final
                final_clip = final_clip.set_audio(audio_clip)
            
            # Guardar el video procesado
            output_filename = f"video_procesado_{int(time.time())}.{st.session_state.export_format}"
            output_path = os.path.join(st.session_state.temp_dir.name, output_filename)
            
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=os.path.join(st.session_state.temp_dir.name, 'temp_audio.m4a'),
                remove_temp=True,
                fps=24
            )
            
            # Guardar la ruta del archivo de salida en el estado de la sesión
            st.session_state.output_file = output_path
            st.session_state.processing_complete = True
            
            # Cerrar clips para liberar recursos
            for clip in video_clips:
                clip.close()
            final_clip.close()
            if st.session_state.audio_file:
                audio_clip.close()
                
            return output_path
            
        except Exception as e:
            st.error(f"Error al procesar los videos: {str(e)}")
            return None

# Interfaz de usuario
st.title("Editor de Videos")

# Sidebar para configuración
with st.sidebar:
    st.header("Configuración")
    
    # Dimensiones del video de salida
    st.subheader("Dimensiones de salida")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.output_width = st.number_input("Ancho", min_value=320, max_value=3840, value=st.session_state.output_width, step=10)
    with col2:
        st.session_state.output_height = st.number_input("Alto", min_value=240, max_value=2160, value=st.session_state.output_height, step=10)
    
    # Filtros visuales
    st.subheader("Filtros visuales")
    st.session_state.selected_filter = st.selectbox(
        "Selecciona un filtro",
        ["Ninguno", "Blanco y Negro", "Sepia", "Colorizar", "Invertir", "Brillo"]
    )
    
    # Transiciones
    st.subheader("Transiciones")
    st.session_state.selected_transition = st.selectbox(
        "Selecciona una transición",
        ["Ninguna", "Fade", "Slide"]
    )
    
    # Formato de exportación
    st.subheader("Formato de exportación")
    st.session_state.export_format = st.selectbox(
        "Selecciona un formato",
        ["mp4", "avi", "mov"]
    )

# Sección principal
tabs = st.tabs(["Carga de Videos", "Música", "Procesamiento", "Exportación"])

# Pestaña de carga de videos
with tabs[0]:
    st.header("Carga de Videos")
    
    # Sección de arrastrar y soltar
    st.markdown("<div class='upload-section'>Arrastra y suelta archivos MP4 aquí</div>", unsafe_allow_html=True)
    
    # Selector de archivos
    uploaded_videos = st.file_uploader(
        "O selecciona archivos manualmente",
        type=["mp4"],
        accept_multiple_files=True
    )
    
    if uploaded_videos:
        st.session_state.video_files = uploaded_videos
        st.success(f"Se han cargado {len(uploaded_videos)} videos.")
        
        # Mostrar miniaturas de los videos cargados
        st.subheader("Videos cargados:")
        cols = st.columns(3)
        for i, video_file in enumerate(st.session_state.video_files):
            with cols[i % 3]:
                st.video(video_file)
                st.caption(video_file.name)

# Pestaña de música
with tabs[1]:
    st.header("Agregar Música")
    
    uploaded_audio = st.file_uploader(
        "Selecciona un archivo de audio MP3",
        type=["mp3"]
    )
    
    if uploaded_audio:
        st.session_state.audio_file = uploaded_audio
        st.success(f"Audio cargado: {uploaded_audio.name}")
        st.audio(uploaded_audio)
        
        st.info("Si la duración del audio es menor que la del video, se repetirá automáticamente y se recortará al finalizar el video.")

# Pestaña de procesamiento
with tabs[2]:
    st.header("Procesamiento de Videos")
    
    if st.session_state.video_files:
        st.info(f"Se procesarán {len(st.session_state.video_files)} videos con las siguientes configuraciones:")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Dimensiones", f"{st.session_state.output_width}x{st.session_state.output_height}")
        with col2:
            st.metric("Filtro", st.session_state.selected_filter)
        with col3:
            st.metric("Transición", st.session_state.selected_transition)
        
        if st.button("Procesar Videos", key="process_button"):
            output_path = process_videos()
            if output_path:
                st.success("¡Procesamiento completado con éxito!")
                st.video(output_path)
    else:
        st.warning("No hay videos cargados para procesar. Por favor, carga al menos un video en la pestaña 'Carga de Videos'.")

# Pestaña de exportación
with tabs[3]:
    st.header("Exportación Final")
    
    if st.session_state.processing_complete and st.session_state.output_file:
        st.success("¡El video está listo para descargar!")
        
        # Mostrar una vista previa del video procesado
        st.subheader("Vista previa del video procesado:")
        st.video(st.session_state.output_file)
        
        # Botón de descarga
        with open(st.session_state.output_file, "rb") as file:
            output_filename = os.path.basename(st.session_state.output_file)
            st.download_button(
                label="Descargar Video",
                data=file,
                file_name=output_filename,
                mime=f"video/{st.session_state.export_format}"
            )
    else:
        st.warning("No hay un video procesado disponible para exportar. Por favor, procesa tus videos en la pestaña 'Procesamiento'.")

# Pie de página
st.markdown("---")
st.markdown("<div style='text-align: center'>© 2023 Editor de Videos | Desarrollado con Streamlit</div>", unsafe_allow_html=True)