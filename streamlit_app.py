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
        <p style="color:#CCCCCC;">Optimizado para condiciones de pista en Parque Viva 🇨🇷</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.header("🔧 Parámetros ambientales y del motor")
temp_amb = st.sidebar.slider("🌡 Temperatura ambiente (°C)", 20, 40, 25)
altitud = st.sidebar.slider("🗻 Altitud (m)", 0, 2000, 500)
combustible_octanaje = st.sidebar.slider("⛽ Octanaje del combustible", 90, 100, 95)
rpm = st.sidebar.slider("🌀 RPM máximo del motor", 5000, 11000, 8500)

st.sidebar.header("⚙️ Especificaciones técnicas")
diametro_cilindro = st.sidebar.number_input("📏 Diámetro de cilindro (mm)", 60.0, 70.0, 66.0)
carrera = st.sidebar.number_input("📐 Carrera (mm)", 58.0, 66.0, 60.0)
relacion_compresion = st.sidebar.slider("⚖️ Relación de compresión", 6.0, 8.5, 7.2)
mufla_diametro = st.sidebar.number_input("🔊 Diámetro de la panza de mufla (mm)", 110.0, 150.0, 125.0)

if st.sidebar.button("🚀 Ejecutar simulación"):
    st.success("✅ Simulación completada exitosamente.")

    rpm_values = np.linspace(1000, rpm, 200)
    avance_ideal = (
        15 + (0.003 * (rpm_values - 1000))
        - (0.002 * (temp_amb - 25))
        - (0.0005 * altitud)
        + (0.05 * (combustible_octanaje - 95))
        + (0.01 * (relacion_compresion - 7.2))
        - (0.0004 * (mufla_diametro - 125))
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rpm_values, y=avance_ideal, mode='lines+markers', name='Avance Óptimo'))
    fig.update_layout(title="Curva Recomendada de Avance de Encendido", xaxis_title="RPM", yaxis_title="Avance (grados)", template="plotly_dark")

    st.plotly_chart(fig, use_container_width=True)

    st.info("📥 El reporte incluye recomendaciones ajustadas a las condiciones ambientales y la configuración de tu DT175.")

    reporte = f"""
    🔎 **Reporte de Simulación - DT175 PRO**

    👉 Temperatura ambiente: {temp_amb} °C
    👉 Altitud: {altitud} m
    👉 Octanaje del combustible: {combustible_octanaje}
    👉 RPM máximo simulado: {rpm}
    👉 Diámetro de cilindro: {diametro_cilindro} mm
    👉 Carrera: {carrera} mm
    👉 Relación de compresión: {relacion_compresion}
    👉 Diámetro de mufla: {mufla_diametro} mm

    📈 Curva generada y recomendaciones disponibles en la plataforma.

    🎯 Gracias por utilizar la herramienta, cualquier ajuste adicional se puede hacer vía GitHub o contacto directo.
    """
    st.download_button("📥 Descargar reporte detallado", reporte, file_name="reporte_dt175_pro.txt")

st.sidebar.markdown("---")
st.sidebar.write("Proyecto de Jean Pablo Jiménez — Optimizador Racing DT175 🚀")
st.sidebar.write("Versión extendida con gráficos, reporte descargable, visualización profesional y logo integrado.")
