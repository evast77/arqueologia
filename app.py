import streamlit as st
import geopy
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import folium_static
from PIL import Image
import io
import base64
import requests
import pandas as pd
import os
import sqlite3
import piexif
import piexif.helper
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
password_correcta = os.getenv("APP_PASSWORD")

# Configurar la app
st.set_page_config(page_title="GeoFoto App", layout="centered")
st.title("📍 GeoFoto App - Registro de Petroglifos y Artefactos")

# Verificación de contraseña
password = st.text_input("Introduce la contraseña para acceder", type="password")
if password != password_correcta:
    st.warning("Acceso denegado. Introduce la contraseña correcta.")
    st.stop()

# Función para extraer coordenadas GPS de una imagen
def obtener_gps_de_imagen(image_file):
    try:
        img = Image.open(image_file)
        exif_data = piexif.load(img.info["exif"])
        gps_info = exif_data.get(piexif.IFD.GPS, {})
        
        if gps_info:
            lat = gps_info.get(2)
            lon = gps_info.get(4)
            
            if lat and lon:
                lat = lat[0] + lat[1] / 60 + lat[2] / 3600
                lon = lon[0] + lon[1] / 60 + lon[2] / 3600
                
                if gps_info[1] == b'S':
                    lat = -lat
                if gps_info[3] == b'W':
                    lon = -lon
                
                return lat, lon
        
    except Exception as e:
        print("Error al extraer GPS de la imagen:", e)
    return None, None

# Obtener la ubicación GPS real
def obtener_ubicacion_real():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        lat, lon = map(float, data["loc"].split(","))
        return lat, lon
    except:
        return None, None

latitude, longitude = None, None

# Captura de imagen desde la cámara o subida
st.write("## 📷 Captura de imagen")
image_file = st.file_uploader("Sube una foto del petroglifo o artefacto", type=["jpg", "png", "jpeg"])

if image_file is not None:
    image = Image.open(image_file)
    st.image(image, caption="Imagen cargada", use_column_width=True)
    
    # Intentar obtener GPS desde la imagen
    latitude, longitude = obtener_gps_de_imagen(image_file)
    if not latitude or not longitude:
        latitude, longitude = obtener_ubicacion_real()
    
    st.success("Imagen guardada correctamente")

if latitude and longitude:
    st.write(f"**Ubicación estimada:** {latitude}, {longitude}")
else:
    st.write("⚠️ No se pudo obtener la ubicación. Asegúrate de que tienes conexión a Internet.")

# Mostrar un mapa con la ubicación
if latitude and longitude:
    mapa = folium.Map(location=[latitude, longitude], zoom_start=15)
    folium.Marker([latitude, longitude], popup="Ubicación actual").add_to(mapa)
    folium_static(mapa)

# Clasificación del objeto
st.write("## 🏺 Clasificación del hallazgo")
clasificacion = st.selectbox(
    "Selecciona el tipo de hallazgo:",
    ["Petroglifo", "Hacha", "Punta de proyectil", "Utensilio de piedra", "Otro"]
)

# Profundidad del grabado
st.write("## 📏 Profundidad del grabado (si aplica)")
profundidad = st.number_input("Introduce la profundidad en mm", min_value=0.0, step=0.1)

# Longitud del grabado
st.write("## 📏 Longitud del grabado (si aplica)")
longitud_grabado = st.number_input("Introduce la longitud en mm", min_value=0.0, step=0.1)

# Tipo de soporte rocoso
st.write("## 🪨 Tipo de soporte rocoso")
soporte = st.text_input("Describe el tipo de roca donde está el grabado")

# Presencia de patrones
st.write("## 🔍 Presencia de patrones reconocibles")
presencia_patrones = st.checkbox("¿El petroglifo tiene patrones identificables?")

# Número de patrones
num_patrones = 0
if presencia_patrones:
    num_patrones = st.number_input("Número de patrones identificables", min_value=1, step=1)

# Presencia de líneas rectas
st.write("## 📐 Presencia de líneas rectas")
presencia_lineas = st.checkbox("¿El petroglifo tiene líneas rectas?")

# Observaciones adicionales
st.write("## 📝 Observaciones adicionales")
observaciones = st.text_area("Añade cualquier comentario relevante")

# Configurar base de datos SQLite
DB_FILE = "petroglifos.db"
def inicializar_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS registros (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        latitud REAL,
                        longitud REAL,
                        clasificacion TEXT,
                        profundidad REAL,
                        longitud_grabado REAL,
                        soporte TEXT,
                        presencia_patrones BOOLEAN,
                        num_patrones INTEGER,
                        presencia_lineas BOOLEAN,
                        observaciones TEXT)''')
    conn.commit()
    conn.close()

def guardar_datos():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO registros (latitud, longitud, clasificacion, profundidad, longitud_grabado, soporte, presencia_patrones, num_patrones, presencia_lineas, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (latitude, longitude, clasificacion, profundidad, longitud_grabado, soporte, presencia_patrones, num_patrones, presencia_lineas, observaciones))
    conn.commit()
    conn.close()
    st.success("Registro guardado con éxito!")

# Inicializar base de datos
inicializar_db()

# Botón para guardar la información
if st.button("Guardar Registro"):
    guardar_datos()
    st.write(f"**Registro guardado:**\n - Tipo: {clasificacion}\n - Ubicación: {latitude}, {longitude}\n - Profundidad: {profundidad} mm\n - Longitud: {longitud_grabado} mm\n - Soporte Rocoso: {soporte}\n - Presencia de patrones: {presencia_patrones}\n - Número de patrones: {num_patrones}\n - Presencia de líneas rectas: {presencia_lineas}\n - Observaciones: {observaciones}")
