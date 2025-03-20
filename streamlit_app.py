import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import plotly.graph_objects as go
import time
from fpdf import FPDF

st.set_page_config(page_title="Ignition Master DT175", layout="wide")

# Animación de bienvenida y efecto sonoro con experiencia completa
def play_startup_sound():
    with open("engine_start.mp3", "rb") as sound_file:
        sound_bytes = sound_file.read()
    encoded_sound = base64.b64encode(sound_bytes).decode()
    st.markdown(f"""
    <audio autoplay>
      <source src="data:audio/mp3;base64,{encoded_sound}" type="audio/mp3">
    </audio>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
    .main {
        background-color: #1c1c1c;
        color: #f0f0f0;
        font-family: 'Helvetica', sans-serif;
    }
    h1, h2, h3 {
        color: #ffcc00;
    }
    .stButton button {
        background-color: #ffcc00;
        color: black;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏁 IGNITION MASTER SYSTEM - DT175 PRO")
play_startup_sound()
st.image("logo_ignition_dt175.png", use_column_width=True)
st.markdown("---")

st.sidebar.header("Parámetros completos de simulación")
temp_ambiente = st.sidebar.slider("Temperatura Ambiente (°C)", 20, 40, 28)
temp_pista = st.sidebar.slider("Temperatura Pista (°C)", 25, 60, 35)
humedad_relativa = st.sidebar.slider("Humedad Relativa (%)", 20, 90, 50)
carga_motor = st.sidebar.slider("Carga del motor (%)", 30, 100, 75)
diametro_carb = st.sidebar.slider("Diámetro de carburador (mm)", 26, 36, 30)
diametro_admision = st.sidebar.slider("Diámetro de admisión (mm)", 24, 36, 30)
diametro_escape = st.sidebar.slider("Diámetro de escape (mm)", 22, 36, 28)
cubicaje_cupula = st.sidebar.slider("Cubicaje de cúpula (cc)", 12, 25, 15)
bujia_grado = st.sidebar.selectbox("Grado de bujía", ["NGK7", "NGK8", "NGK9", "NGK10"])
tipo_mufla = st.sidebar.radio("Tipo de mufla", ["Arriba", "Abajo"])
diametro_panza_mufla = st.sidebar.slider("Diámetro panza mufla (mm)", 60, 90, 70)
boquilla_alta = st.sidebar.slider("Boquilla Alta", 170, 210, 180)
boquilla_baja = st.sidebar.slider("Boquilla Baja", 45, 60, 50)
aguja_aire = st.sidebar.slider("Vueltas aguja de aire", 1, 4, 2)

rpm_range = np.linspace(1500, 10000, 100)

from funciones_ignition_dt175 import simulate_ignition_advance, generate_recommendations, show_3d_map

if st.sidebar.button("Ejecutar simulación integral"):
    with st.spinner("Ejecutando cálculos precisos..."):
        results = simulate_ignition_advance(
            rpm_range, 1000, temp_pista, temp_ambiente, humedad_relativa, carga_motor,
            diametro_carb, diametro_admision, diametro_escape, cubicaje_cupula, bujia_grado,
            tipo_mufla, diametro_panza_mufla, boquilla_alta, boquilla_baja, aguja_aire
        )

        fig, ax = plt.subplots()
        ax.plot(results['rpm_range'], results['advance_values'], color='#ffcc00')
        ax.set_xlabel("RPM")
        ax.set_ylabel("Avance de encendido (°)")
        ax.set_title("Curva calculada de avance de encendido vs RPM")
        st.pyplot(fig)

        recommendations = generate_recommendations(results)
        st.info(recommendations)

        fig3d = show_3d_map(results)
        st.plotly_chart(fig3d, use_container_width=True)

st.markdown("---")
st.caption("Desarrollado por Jean Pablo — Proyecto Integral DT175 Pro, sin simplificaciones.")
