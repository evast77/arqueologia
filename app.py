import streamlit as st
import folium
from streamlit_folium import folium_static
import sqlite3
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
password_correcta = os.getenv("APP_PASSWORD")

# Inicializar base de datos
DB_FILE = "petroglifos.db"

def inicializar_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS registros (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        clasificacion TEXT,
                        latitud REAL,
                        longitud REAL,
                        profundidad REAL
                    )''')
    conn.commit()
    conn.close()

# Función para guardar datos
def guardar_datos(clasificacion, latitud, longitud, profundidad):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO registros (clasificacion, latitud, longitud, profundidad) VALUES (?, ?, ?, ?)",
                   (clasificacion, latitud, longitud, profundidad))
    conn.commit()
    conn.close()
    st.success("📌 Registro guardado con éxito!")

# Interfaz de usuario
st.set_page_config(page_title="GeoFoto App", layout="centered")
st.title("📍 GeoFoto App - Registro de Petroglifos y Artefactos")

# Verificación de contraseña
password = st.text_input("🔒 Introduce la contraseña para acceder", type="password")

if password == password_correcta:
    st.success("✅ Acceso concedido")

    # Ingreso de datos
    st.write("### 📝 Información del hallazgo")

    clasificacion = st.selectbox("Tipo de artefacto:", ["Petroglifo", "Hacha", "Cerámica", "Otro"])

    latitud = st.number_input("Latitud", format="%.6f")
    longitud = st.number_input("Longitud", format="%.6f")
    profundidad = st.number_input("Profundidad del grabado (mm)", min_value=0.0, step=0.1)

    if st.button("Guardar Registro"):
        guardar_datos(clasificacion, latitud, longitud, profundidad)
        st.write(f"**Registro guardado:**\n- 📌 Tipo: {clasificacion}\n- 📍 Ubicación: {latitud}, {longitud}\n- 🔎 Profundidad: {profundidad} mm")

    # Visualización en mapa
    st.write("### 🌍 Mapa de ubicaciones registradas")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT latitud, longitud, clasificacion FROM registros")
    ubicaciones = cursor.fetchall()
    conn.close()

    if ubicaciones:
        mapa = folium.Map(location=[ubicaciones[0][0], ubicaciones[0][1]], zoom_start=10)
        for lat, lon, tipo in ubicaciones:
            folium.Marker([lat, lon], popup=f"{tipo}").add_to(mapa)
        folium_static(mapa)
    else:
        st.write("⚠️ No hay ubicaciones registradas.")
else:
    st.error("❌ Acceso denegado. Introduce la contraseña correcta.")

# Inicializar base de datos
inicializar_db()
