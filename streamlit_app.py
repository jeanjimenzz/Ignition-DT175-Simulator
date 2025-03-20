import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# Funciones de simulación y cálculo de avance de encendido
def simulate_ignition_advance(
    rpm_range, track_length, temp_pista, temp_ambiente, humedad_relativa, carga_motor,
    diametro_carb=None, diametro_admision=None, diametro_escape=None, 
    cubicaje_cupula=None, bujia_grado=None, tipo_mufla=None, diametro_panza_mufla=None,
    boquilla_alta=None, boquilla_baja=None, aguja_aire=None
):
    base_speed = np.linspace(20, 140, len(rpm_range))
    env_factor = (1 - (humedad_relativa / 200)) * (1 + (carga_motor / 200))

    engine_factor = 1.0
    if diametro_carb and diametro_admision and diametro_escape:
        intake_exhaust_ratio = diametro_admision / diametro_escape
        carb_factor = min(1.2, max(0.8, diametro_carb / 30))
        flow_factor = min(1.15, max(0.9, intake_exhaust_ratio))
        engine_factor *= carb_factor * flow_factor

    if boquilla_alta and boquilla_baja and aguja_aire:
        jetting_factor = 1 + ((boquilla_alta - 180) * 0.001 + (boquilla_baja - 50) * 0.002 + (aguja_aire - 2) * 0.01)
        engine_factor *= jetting_factor

    if tipo_mufla and diametro_panza_mufla:
        mufla_factor = 1.05 if tipo_mufla.lower() == 'abajo' else 0.98
        panza_factor = min(1.1, max(0.9, diametro_panza_mufla / 70))
        engine_factor *= mufla_factor * panza_factor

    speed_range = base_speed * env_factor * engine_factor
    temp_culata = np.array([temp_ambiente + (s / 2) for s in speed_range])

    if cubicaje_cupula:
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
    diametro_carb=None, diametro_admision=None, diametro_escape=None, 
    cubicaje_cupula=None, bujia_grado=None, tipo_mufla=None, diametro_panza_mufla=None,
    boquilla_alta=None, boquilla_baja=None, aguja_aire=None
):
    base_advance = 10 if rpm < 3000 else min(22, 10 + (rpm - 3000) * 0.003)
    temp_correction = -0.01 * (temp_culata - 120) if temp_culata > 120 else 0
    pista_correction = -0.005 * (temp_pista - 30) if temp_pista > 30 else 0
    carga_correction = 0.002 * (carga_motor - 50) if carga_motor > 50 else 0

    component_correction = 0
    if diametro_carb and diametro_admision and diametro_escape:
        carb_correction = 0.5 * (diametro_carb - 30) / 10
        flow_ratio = diametro_admision / diametro_escape
        flow_correction = -0.3 if flow_ratio > 1.2 else (0.3 if flow_ratio < 0.8 else 0)
        component_correction += carb_correction + flow_correction

    if cubicaje_cupula:
        compression_correction = 0.02 * (cubicaje_cupula - 15)
        component_correction += compression_correction

    if bujia_grado:
        try:
            grade_numeric = int(''.join(filter(str.isdigit, bujia_grado)))
            plug_correction = 0.1 * (grade_numeric - 8)
            component_correction += plug_correction
        except (ValueError, TypeError):
            pass

    if boquilla_alta and boquilla_baja and aguja_aire:
        jetting_correction = (boquilla_alta - 180) * 0.02 + (boquilla_baja - 50) * 0.05 + (aguja_aire - 2) * 0.1
        component_correction += jetting_correction

    if tipo_mufla and diametro_panza_mufla:
        mufla_type_correction = 0.3 if tipo_mufla.lower() == 'abajo' else -0.2
        panza_correction = 0.02 * (diametro_panza_mufla - 70)
        rpm_specific_mufla = 0.2 if 4000 <= rpm <= 7000 else -0.1
        component_correction += mufla_type_correction + panza_correction + rpm_specific_mufla

    final_advance = base_advance + temp_correction + pista_correction + carga_correction + component_correction
    return max(5, min(25, final_advance))
