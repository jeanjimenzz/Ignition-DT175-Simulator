import numpy as np
import plotly.graph_objects as go

# Funciones completas y listas para insertar en tu archivo `funciones_ignition_dt175.py`.

# Simulación de avance de encendido con explicaciones completas para la aplicación Streamlit
def simulate_ignition_advance(
    rpm_range, track_length, temp_pista, temp_ambiente, humedad_relativa, carga_motor,
    diametro_carb, diametro_admision, diametro_escape, cubicaje_cupula, bujia_grado,
    tipo_mufla, diametro_panza_mufla, boquilla_alta, boquilla_baja, aguja_aire
):
    base_speed = np.linspace(20, 140, len(rpm_range))
    env_factor = (1 - (humedad_relativa / 200)) * (1 + (carga_motor / 200))

    engine_factor = 1.0
    intake_exhaust_ratio = diametro_admision / diametro_escape
    carb_factor = min(1.3, max(0.7, diametro_carb / 30))
    flow_factor = min(1.2, max(0.85, intake_exhaust_ratio))
    engine_factor *= carb_factor * flow_factor

    mufla_factor = 1.05 if tipo_mufla.lower() == 'abajo' else 0.98
    panza_factor = min(1.1, max(0.9, diametro_panza_mufla / 70))
    engine_factor *= mufla_factor * panza_factor

    speed_range = base_speed * env_factor * engine_factor
    temp_culata = np.array([temp_ambiente + (s / 2) for s in speed_range])
    temp_culata *= min(1.15, max(0.9, 20 / cubicaje_cupula))

    advance_values = []
    explanations = []

    for rpm, speed, temp_head in zip(rpm_range, speed_range, temp_culata):
        advance, explanation = ignition_advance_calculation(
            rpm, temp_head, temp_pista, carga_motor,
            diametro_carb, diametro_admision, diametro_escape,
            cubicaje_cupula, bujia_grado, tipo_mufla, diametro_panza_mufla,
            boquilla_alta, boquilla_baja, aguja_aire
        )
        advance_values.append(advance)
        explanations.append(explanation)

    return {
        'rpm_range': rpm_range,
        'speed_range': speed_range,
        'temp_culata': temp_culata,
        'advance_values': advance_values,
        'explanations': explanations
    }

# Cálculo detallado con explicación paso a paso para mostrar en la aplicación Streamlit
def ignition_advance_calculation(
    rpm, temp_culata, temp_pista, carga_motor,
    diametro_carb, diametro_admision, diametro_escape,
    cubicaje_cupula, bujia_grado, tipo_mufla, diametro_panza_mufla,
    boquilla_alta, boquilla_baja, aguja_aire
):
    explanation = f"\nRPM: {rpm} | Temp Culata: {temp_culata}°C"

    base_advance = 10 if rpm < 3000 else min(22, 10 + (rpm - 3000) * 0.003)
    explanation += f"\nBase advance calculado: {base_advance:.2f}°"

    temp_correction = -0.01 * (temp_culata - 120) if temp_culata > 120 else 0
    explanation += f"\nCorrección por temperatura: {temp_correction:.2f}°"

    pista_correction = -0.005 * (temp_pista - 30) if temp_pista > 30 else 0
    explanation += f"\nCorrección por temperatura de pista: {pista_correction:.2f}°"

    carga_correction = 0.002 * (carga_motor - 50) if carga_motor > 50 else 0
    explanation += f"\nCorrección por carga de motor: {carga_correction:.2f}°"

    carb_correction = 0.4 * (diametro_carb - 30) / 10
    explanation += f"\nAjuste por diámetro de carburador: {carb_correction:.2f}°"

    flow_ratio = diametro_admision / diametro_escape
    flow_correction = -0.3 if flow_ratio > 1.2 else (0.3 if flow_ratio < 0.8 else 0)
    explanation += f"\nCorrección por relación admisión/escape: {flow_correction:.2f}°"

    compression_correction = 0.02 * (cubicaje_cupula - 15)
    explanation += f"\nCorrección por cubicaje de cúpula: {compression_correction:.2f}°"

    grade_numeric = int(''.join(filter(str.isdigit, bujia_grado)))
    plug_correction = 0.1 * (grade_numeric - 8)
    explanation += f"\nAjuste por grado térmico de bujía: {plug_correction:.2f}°"

    mufla_type_correction = 0.3 if tipo_mufla.lower() == 'abajo' else -0.2
    explanation += f"\nCorrección por tipo de mufla: {mufla_type_correction:.2f}°"

    panza_correction = 0.02 * (diametro_panza_mufla - 70)
    explanation += f"\nCorrección por diámetro de panza de mufla: {panza_correction:.2f}°"

    jetting_factor = (boquilla_alta - 180) * 0.01 - (boquilla_baja - 50) * 0.005 + (aguja_aire - 2) * 0.2
    explanation += f"\nAjuste por configuración de carburador (boquillas y aguja): {jetting_factor:.2f}°"

    final_advance = (base_advance + temp_correction + pista_correction + carga_correction +
                     carb_correction + flow_correction + compression_correction + plug_correction +
                     mufla_type_correction + panza_correction + jetting_factor)

    explanation += f"\nAvance final recomendado: {final_advance:.2f}°\n-----"

    return max(5, min(25, final_advance)), explanation

# Generación automática de recomendaciones para mostrar con st.info
def generate_recommendations(results):
    avg_advance = np.mean(results['advance_values'])
    recommendation = "**Resumen de recomendaciones automáticas:**\n"

    if avg_advance > 20:
        recommendation += "- Se recomienda reducir el avance o usar bujía más fría.\n"
    elif avg_advance < 12:
        recommendation += "- Puede aumentarse el avance; revise admisión y escape.\n"

    if np.max(results['temp_culata']) > 180:
        recommendation += "- Atención: Temperatura alta de culata, revise mezcla y refrigeración.\n"

    if np.max(results['speed_range']) < 90:
        recommendation += "- La velocidad máxima es baja, verificar escape o restricción.\n"

    recommendation += "- Configuración revisada y adaptada a condiciones actuales."
    return recommendation

# Mapa 3D interactivo para visualizar los resultados en Streamlit
def show_3d_map(results):
    fig = go.Figure(data=[go.Scatter3d(
        x=results['rpm_range'],
        y=results['speed_range'],
        z=results['advance_values'],
        mode='markers',
        marker=dict(size=4, color=results['advance_values'], colorscale='Viridis', opacity=0.9)
    )])
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=40),
        title='Mapa 3D: RPM vs Velocidad vs Avance de Encendido',
        scene=dict(
            xaxis_title='RPM',
            yaxis_title='Velocidad (km/h)',
            zaxis_title='Avance (°)'
        )
    )
    return fig

