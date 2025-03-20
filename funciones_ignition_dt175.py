import numpy as np
import plotly.graph_objects as go

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
    for rpm, speed, temp_head in zip(rpm_range, speed_range, temp_culata):
        advance = ignition_advance_calculation(
            rpm, temp_head, temp_pista, carga_motor,
            diametro_carb, diametro_admision, diametro_escape,
            cubicaje_cupula, bujia_grado, tipo_mufla, diametro_panza_mufla,
            boquilla_alta, boquilla_baja, aguja_aire
        )
        advance_values.append(advance)

    return {
        'rpm_range': rpm_range,
        'speed_range': speed_range,
        'temp_culata': temp_culata,
        'advance_values': advance_values,
    }

def ignition_advance_calculation(
    rpm, temp_culata, temp_pista, carga_motor,
    diametro_carb, diametro_admision, diametro_escape,
    cubicaje_cupula, bujia_grado, tipo_mufla, diametro_panza_mufla,
    boquilla_alta, boquilla_baja, aguja_aire
):
    base_advance = 10 if rpm < 3000 else min(22, 10 + (rpm - 3000) * 0.003)
    temp_correction = -0.01 * (temp_culata - 120) if temp_culata > 120 else 0
    pista_correction = -0.005 * (temp_pista - 30) if temp_pista > 30 else 0
    carga_correction = 0.002 * (carga_motor - 50) if carga_motor > 50 else 0

    carb_correction = 0.4 * (diametro_carb - 30) / 10
    flow_ratio = diametro_admision / diametro_escape
    flow_correction = -0.3 if flow_ratio > 1.2 else (0.3 if flow_ratio < 0.8 else 0)

    compression_correction = 0.02 * (cubicaje_cupula - 15)

    grade_numeric = int(''.join(filter(str.isdigit, bujia_grado)))
    plug_correction = 0.1 * (grade_numeric - 8)

    mufla_type_correction = 0.3 if tipo_mufla.lower() == 'abajo' else -0.2
    panza_correction = 0.02 * (diametro_panza_mufla - 70)

    jetting_factor = (boquilla_alta - 180) * 0.01 - (boquilla_baja - 50) * 0.005 + (aguja_aire - 2) * 0.2

    final_advance = (base_advance + temp_correction + pista_correction + carga_correction +
                     carb_correction + flow_correction + compression_correction + plug_correction +
                     mufla_type_correction + panza_correction + jetting_factor)

    return max(5, min(25, final_advance))

def generate_recommendations(results):
    avg_advance = np.mean(results['advance_values'])
    recommendation = ""

    if avg_advance > 20:
        recommendation += "\n👉 Se recomienda reducir ligeramente el avance de encendido o usar bujía más fría."
    elif avg_advance < 12:
        recommendation += "\n👉 Podría aprovecharse un poco más el avance, revise configuración de admisión."

    if np.max(results['temp_culata']) > 180:
        recommendation += "\n⚠️ Temperatura de culata alta, revisar mezcla y refrigeración."

    if np.max(results['speed_range']) < 90:
        recommendation += "\n⚠️ La velocidad máxima es baja, posible restricción en escape o admisión."

    recommendation += "\n✅ Ajustes completos recomendados según condiciones de pista y carga."

    return recommendation

def show_3d_map(results):
    fig = go.Figure(data=[go.Scatter3d(
        x=results['rpm_range'],
        y=results['speed_range'],
        z=results['advance_values'],
        mode='markers',
        marker=dict(size=5, color=results['advance_values'], colorscale='Viridis', opacity=0.8)
    )])
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=40),
        title='Mapa 3D: RPM vs Velocidad vs Avance de Encendido',
        scene=dict(
            xaxis_title='RPM',
            yaxis_title='Velocidad (km/h)',
            zaxis_title='Avance de encendido (°)'
        )
    )
    fig.show()
