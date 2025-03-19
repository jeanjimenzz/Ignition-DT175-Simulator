import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Ignition Timing Pro - DT175 Simulator", layout="wide")

# Logo de bienvenida
st.markdown(
    """
    <div style="text-align:center; margin-top: 30px;">
        <img src="https://raw.githubusercontent.com/jeanjimenzz/Ignition-DT175-Simulator/main/logo_dt175_pro.png" width="400">
        <h1 style="color:#F0F0F0;">Ignition Timing Pro — DT175 Simulator</h1>
    </div>
    """",
    unsafe_allow_html=True
)

st.sidebar.header("🔧 Parámetros de simulación")
temp_amb = st.sidebar.slider("Temperatura ambiente (°C)", 20, 40, 25)
altitud = st.sidebar.slider("Altitud (m)", 0, 2000, 500)
combustible_octanaje = st.sidebar.slider("Octanaje del combustible", 90, 100, 95)
rpm = st.sidebar.slider("RPM máximo del motor", 5000, 11000, 8500)

st.sidebar.header("⚙️ Configuración del motor")
diametro_cilindro = st.sidebar.number_input("Diámetro de cilindro (mm)", 60.0, 70.0, 66.0)
carrera = st.sidebar.number_input("Carrera (mm)", 58.0, 66.0, 60.0)
relacion_compresion = st.sidebar.slider("Relación de compresión", 6.0, 8.5, 7.2)
mufla_diametro = st.sidebar.number_input("Diámetro de la panza de mufla (mm)", 110.0, 150.0, 125.0)

if st.sidebar.button("Ejecutar simulación"):
    st.success("✅ Simulación ejecutada")

    rpm_values = np.linspace(1000, rpm, 100)
    avance_ideal = (
        15 + (0.003 * (rpm_values - 1000))
        - (0.002 * (temp_amb - 25))
        - (0.0005 * altitud)
        + (0.05 * (combustible_octanaje - 95))
        + (0.01 * (relacion_compresion - 7.2))
        - (0.0004 * (mufla_diametro - 125))
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rpm_values, y=avance_ideal, mode='lines', name='Avance Óptimo'))
    fig.update_layout(title="Curva de Avance de Encendido Recomendado", xaxis_title="RPM", yaxis_title="Avance (grados)")

    st.plotly_chart(fig, use_container_width=True)

    st.download_button("📥 Descargar reporte", "Reporte generado con parámetros ingresados.", "reporte.txt")

st.sidebar.markdown("---")
st.sidebar.write("Proyecto Jean Pablo — Optimización DT175 Racing")