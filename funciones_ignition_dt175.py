import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import streamlit as st

# Función principal para simular el avance de encendido y métricas del motor
def simulate_ignition_advance(rpm_range, track_length, temp_pista, temp_ambiente, humedad_relativa, carga_motor,
                              diametro_carb, diametro_admision, diametro_escape, cubicaje_cupula, bujia_grado,
                              tipo_mufla, diametro_panza_mufla, boquilla_alta, boquilla_baja, aguja_aire):

    base_speed = np.linspace(20, 140, len(rpm_range))
    env_factor = (1 - (humedad_relativa / 200)) * (1 + (carga_motor / 200))

    engine_factor = 1.0
    intake_exhaust_ratio = diametro_admision / diametro_escape
    carb_factor = min(1.2, max(0.8, diametro_carb / 30))
    flow_factor = min(1.15, max(0.9, intake_exhaust_ratio))

    boquilla_factor = 1 + ((boquilla_alta - 180) / 1000) - ((boquilla_baja - 50) / 500) + ((aguja_aire - 2) * 0.02)

    mufla_factor = 1.05 if tipo_mufla.lower() == 'abajo' else 0.98
    panza_factor = min(1.1, max(0.9, diametro_panza_mufla / 70))

    engine_factor *= carb_factor * flow_factor * mufla_factor * panza_factor * boquilla_factor

    speed_range = base_speed * env_factor * engine_factor

    temp_culata = np.array([temp_ambiente + (s / 2) for s in speed_range])
    temp_culata *= min(1.15, max(0.9, 20 / cubicaje_cupula))

    advance_values = []
    for rpm, speed, temp_head in zip(rpm_range, speed_range, temp_culata):
        advance = ignition_advance_calculation(rpm, temp_head, temp_pista, carga_motor, diametro_carb,
                                               diametro_admision, diametro_escape, cubicaje_cupula, bujia_grado,
                                               tipo_mufla, diametro_panza_mufla, boquilla_alta, boquilla_baja, aguja_aire)
        advance_values.append(advance)

    return {'rpm_range': rpm_range, 'speed_range': speed_range, 'temp_culata': temp_culata, 'advance_values': advance_values}


def ignition_advance_calculation(rpm, temp_culata, temp_pista, carga_motor, diametro_carb, diametro_admision,
                                 diametro_escape, cubicaje_cupula, bujia_grado, tipo_mufla, diametro_panza_mufla,
                                 boquilla_alta, boquilla_baja, aguja_aire):

    base_advance = 10 if rpm < 3000 else min(22, 10 + (rpm - 3000) * 0.003)

    temp_correction = -0.01 * (temp_culata - 120) if temp_culata > 120 else 0
    pista_correction = -0.005 * (temp_pista - 30) if temp_pista > 30 else 0
    carga_correction = 0.002 * (carga_motor - 50) if carga_motor > 50 else 0

    carb_correction = 0.5 * (diametro_carb - 30) / 10
    flow_ratio = diametro_admision / diametro_escape
    flow_correction = -0.3 if flow_ratio > 1.2 else (0.3 if flow_ratio < 0.8 else 0)

    compression_correction = 0.02 * (cubicaje_cupula - 15)

    try:
        grade_numeric = int(''.join(filter(str.isdigit, bujia_grado)))
        plug_correction = 0.1 * (grade_numeric - 8)
    except (ValueError, TypeError):
        plug_correction = 0

    mufla_type_correction = 0.3 if tipo_mufla.lower() == 'abajo' else -0.2
    panza_correction = 0.02 * (diametro_panza_mufla - 70)
    rpm_specific_mufla = 0.2 if 4000 <= rpm <= 7000 else -0.1

    boquilla_correction = ((boquilla_alta - 180) / 50) - ((boquilla_baja - 50) / 20) + ((aguja_aire - 2) * 0.1)

    final_advance = base_advance + temp_correction + pista_correction + carga_correction + carb_correction + \
                    flow_correction + compression_correction + plug_correction + mufla_type_correction + \
                    panza_correction + rpm_specific_mufla + boquilla_correction

    final_advance = max(5, min(25, final_advance))

    return final_advance


def generate_recommendations(results):
    avg_temp = np.mean(results['temp_culata'])
    avg_speed = np.mean(results['speed_range'])
    recommendation = ""

    if avg_temp > 140:
        recommendation += "⚠ La temperatura es alta. Considere usar bujía de mayor grado o mejorar refrigeración.\n"

    if avg_speed < 80:
        recommendation += "🚀 Puede mejorar el flujo de admisión/escape o revisar la relación de compresión.\n"

    if recommendation == "":
        recommendation = "✅ El motor está configurado óptimamente para estas condiciones."

    return recommendation


def show_3d_map(results):
    fig = go.Figure(data=[go.Surface(z=[results['advance_values']], x=[results['rpm_range']], y=[results['temp_culata']])])
    fig.update_layout(title='Mapa 3D de Avance de Encendido', scene=dict(
        xaxis_title='RPM', yaxis_title='Temperatura de Culata (°C)', zaxis_title='Avance (°)',
        bgcolor="rgba(0,0,0,0)"
    ))
    fig.update_traces(contours_z=dict(show=True, usecolormap=True))
    st.plotly_chart(fig, use_container_width=True)



