# modulos/conductores_ac.py
import math
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tablas.tablas_ac import (
    PROPIEDADES_CONDUCTORES, AMPACIDAD_BASE, K1_SUELO, K1_AIRE,
    K2_AGRUPAMIENTO_D2, K2_AGRUPAMIENTO_F, K3_PROFUNDIDAD, K4_RESISTIVIDAD,
    CONSTANTE_K_CC
)

# 1. CÁLCULO DUAL DE FACTOR K1 (Interpolación de Temperatura)
def calcular_k1(temp_c, aislamiento="XLPE", metodo="D2"):
    tabla = K1_SUELO[aislamiento] if "D2" in metodo else K1_AIRE[aislamiento]
    temps = sorted(tabla.keys())
    if temp_c <= temps[0]: return tabla[temps[0]]
    if temp_c >= temps[-1]: return tabla[temps[-1]]
    for i in range(len(temps) - 1):
        if temps[i] <= temp_c <= temps[i + 1]:
            t1, t2 = temps[i], temps[i + 1]
            v1, v2 = tabla[t1], tabla[t2]
            return round(v1 + (temp_c - t1) * (v2 - v1) / (t2 - t1), 4)

# 2. CÁLCULO DE FACTOR K2 (Agrupamiento)
def calcular_k2(num_circuitos, espaciado="0.5 m", metodo="D2"):
    if "D2" in metodo:
        ctos = sorted(K2_AGRUPAMIENTO_D2.keys())
        c_val = min(ctos, key=lambda x: abs(x - num_circuitos))
        return K2_AGRUPAMIENTO_D2[c_val].get(espaciado, 0.80)
    else:
        ctos = sorted(K2_AGRUPAMIENTO_F.keys())
        c_val = min(ctos, key=lambda x: abs(x - num_circuitos))
        return K2_AGRUPAMIENTO_F[c_val]

# 3. CÁLCULO DE FACTOR K3 (Profundidad - Solo D2)
def calcular_k3(profundidad_m):
    profs = sorted(K3_PROFUNDIDAD.keys())
    if profundidad_m <= profs[0]: return K3_PROFUNDIDAD[profs[0]]
    if profundidad_m >= profs[-1]: return K3_PROFUNDIDAD[profs[-1]]
    for i in range(len(profs) - 1):
        if profs[i] <= profundidad_m <= profs[i + 1]:
            p1, p2 = profs[i], profs[i + 1]
            v1, v2 = K3_PROFUNDIDAD[p1], K3_PROFUNDIDAD[p2]
            return round(v1 + (profundidad_m - p1) * (v2 - v1) / (p2 - p1), 4)

# 4. CÁLCULO DE FACTOR K4 (Resistividad Térmica - Solo D2)
def calcular_k4(resistividad_k_m_w, tipo_subterraneo="Ductos Subterráneos"):
    tabla = K4_RESISTIVIDAD.get(tipo_subterraneo, K4_RESISTIVIDAD["Ductos Subterráneos"])
    res_list = sorted(tabla.keys())
    if resistividad_k_m_w <= res_list[0]: return tabla[res_list[0]]
    if resistividad_k_m_w >= res_list[-1]: return tabla[res_list[-1]]
    for i in range(len(res_list) - 1):
        if res_list[i] <= resistividad_k_m_w <= res_list[i + 1]:
            r1, r2 = res_list[i], res_list[i + 1]
            v1, v2 = tabla[r1], tabla[r2]
            return round(v1 + (resistividad_k_m_w - r1) * (v2 - v1) / (r2 - r1), 4)

# --- CÁLCULOS ELÉCTRICOS PRINCIPALES ---
def calcular_corriente_diseno(i_max_inversor, factor_seguridad=1.25):
    """Id = Imax * 1.25"""
    return i_max_inversor * factor_seguridad

def calcular_resistencia_temperatura(seccion_mm2, material="Aluminio", aislamiento="XLPE"):
    props = PROPIEDADES_CONDUCTORES.get(material, {}).get(seccion_mm2, (0.100, 0.090))
    r_20, x_km = props
    t_max = 90.0 if aislamiento == "XLPE" else 70.0
    alpha = 0.00407 if material == "Aluminio" else 0.00393
    r_t = r_20 * (1.0 + alpha * (t_max - 20.0))
    return r_20, r_t, x_km

def obtener_ampacidad_corregida(seccion_mm2, metodo="D2", material="Aluminio", aislamiento="XLPE", k1=1.0, k2=1.0, k3=1.0, k4=1.0):
    met_key = "D2" if "D2" in metodo else "F"
    i_z = AMPACIDAD_BASE.get(aislamiento, {}).get(material, {}).get(met_key, {}).get(seccion_mm2, 300)
    i_z_corregida = i_z * k1 * k2 * k3 * k4 if met_key == "D2" else i_z * k1 * k2
    return i_z, i_z_corregida

def calcular_caida_tension(corriente, longitud_m, r_t_km, x_km, voltaje_nominal, cos_phi=1.0):
    r_total = (r_t_km / 1000.0) * longitud_m
    x_total = (x_km / 1000.0) * longitud_m
    sen_phi = math.sqrt(max(0.0, 1.0 - cos_phi**2))
    caida_v = math.sqrt(3) * corriente * (r_total * cos_phi + x_total * sen_phi)
    caida_porcentaje = (caida_v / voltaje_nominal) * 100.0
    return caida_v, caida_porcentaje

def calcular_perdidas_potencia(corriente, longitud_m, r_t_km):
    r_total = (r_t_km / 1000.0) * longitud_m
    return 3.0 * r_total * (corriente ** 2)

def calcular_longitud_maxima(corriente, r_t_km, x_km, voltaje_nominal, caida_obj=3.0, cos_phi=1.0):
    sen_phi = math.sqrt(max(0.0, 1.0 - cos_phi**2))
    z_eff_km = (r_t_km * cos_phi) + (x_km * sen_phi)
    return (caida_obj * voltaje_nominal * 1000.0) / (math.sqrt(3) * corriente * z_eff_km * 100.0)

def calcular_tiempo_cortocircuito(seccion_mm2, i_cc_ka, material="Aluminio", aislamiento="XLPE"):
    k_const = CONSTANTE_K_CC.get((material, aislamiento), 94)
    i_cc_a = i_cc_ka * 1000.0
    tm = ((seccion_mm2 ** 2) * (k_const ** 2)) / (i_cc_a ** 2)
    return tm, k_const