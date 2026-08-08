# main.py - OpenPowerStudio
import customtkinter as ctk
import pandas as pd
from fpdf import FPDF
import math

from modulos.conductores_ac import (
    calcular_corriente_diseno,
    calcular_resistencia_temperatura,
    calcular_k1, calcular_k2, calcular_k3, calcular_k4,
    obtener_ampacidad_corregida,
    calcular_caida_tension,
    calcular_perdidas_potencia,
    calcular_longitud_maxima,
    calcular_tiempo_cortocircuito
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class OpenPowerStudioApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("OpenPowerStudio - Suite de Ingeniería Fotovoltaica y Eléctrica")
        self.geometry("950x850")

        # Configuración de Grid Principal (Sidebar a la izquierda, Contenido a la derecha)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # 1. BARRA LATERAL (SIDEBAR DE NAVEGACIÓN)
        # -------------------------------------------------------------
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="OpenPowerStudio", font=ctk.CTkFont(size=18, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=15, pady=(20, 5))
        
        self.sub_label = ctk.CTkLabel(self.sidebar_frame, text="v1.0.0 Open Source", font=ctk.CTkFont(size=11), text_color="gray")
        self.sub_label.grid(row=1, column=0, padx=15, pady=(0, 20))

        # Botones de navegación entre módulos
        self.btn_ac = ctk.CTkButton(self.sidebar_frame, text="⚡ Cableado AC (BT)", anchor="w", command=self.mostrar_modulo_ac)
        self.btn_ac.grid(row=2, column=0, padx=15, pady=8, sticky="ew")

        self.btn_dc = ctk.CTkButton(self.sidebar_frame, text="🔌 Cableado DC (Strings)", anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), command=self.mostrar_modulo_dc)
        self.btn_dc.grid(row=3, column=0, padx=15, pady=8, sticky="ew")

        self.btn_mt = ctk.CTkButton(self.sidebar_frame, text="🏭 Media Tensión (MT)", anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), command=self.mostrar_modulo_mt)
        self.btn_mt.grid(row=4, column=0, padx=15, pady=8, sticky="ew")

        self.btn_about = ctk.CTkButton(self.sidebar_frame, text="ℹ️ Sobre el Proyecto", anchor="w", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), command=self.mostrar_modulo_about)
        self.btn_about.grid(row=6, column=0, padx=15, pady=15, sticky="ew")

        # -------------------------------------------------------------
        # 2. CONTENEDORES DE CADA MÓDULO (PÁGINAS)
        # -------------------------------------------------------------
        self.frame_ac = ctk.CTkScrollableFrame(self, corner_radius=0)
        self.frame_dc = ctk.CTkFrame(self, corner_radius=0)
        self.frame_mt = ctk.CTkFrame(self, corner_radius=0)
        self.frame_about = ctk.CTkFrame(self, corner_radius=0)

        # Construir la interfaz del Módulo AC
        self._construir_modulo_ac()
        self._construir_modulo_dc()
        self._construir_modulo_mt()
        self._construir_modulo_about()

        # Mostrar por defecto el módulo AC
        self.mostrar_modulo_ac()

    # --- NAVEGACIÓN ---
    def reset_btn_styles(self):
        btn_active_color = ["#3a7ebf", "#1f538d"]
        btn_inactive_color = "transparent"
        for btn in [self.btn_ac, self.btn_dc, self.btn_mt, self.btn_about]:
            btn.configure(fg_color=btn_inactive_color)

    def ocultar_frames(self):
        for frame in [self.frame_ac, self.frame_dc, self.frame_mt, self.frame_about]:
            frame.grid_forget()

    def mostrar_modulo_ac(self):
        self.ocultar_frames()
        self.reset_btn_styles()
        self.btn_ac.configure(fg_color=["#3a7ebf", "#1f538d"])
        self.frame_ac.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    def mostrar_modulo_dc(self):
        self.ocultar_frames()
        self.reset_btn_styles()
        self.btn_dc.configure(fg_color=["#3a7ebf", "#1f538d"])
        self.frame_dc.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    def mostrar_modulo_mt(self):
        self.ocultar_frames()
        self.reset_btn_styles()
        self.btn_mt.configure(fg_color=["#3a7ebf", "#1f538d"])
        self.frame_mt.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    def mostrar_modulo_about(self):
        self.ocultar_frames()
        self.reset_btn_styles()
        self.btn_about.configure(fg_color=["#3a7ebf", "#1f538d"])
        self.frame_about.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    # -------------------------------------------------------------
    # 3. MÓDULO BAJA TENSIÓN AC (CÓDIGO IEC 60364-5-52 COMPLETO)
    # -------------------------------------------------------------
    def _construir_modulo_ac(self):
        f = self.frame_ac
        
        ctk.CTkLabel(f, text="Verificación de Conductores AC (Baja Tensión)", font=("Arial", 16, "bold")).pack(pady=10)

        # PANEL 1: Inversor
        f_sys = ctk.CTkFrame(f); f_sys.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(f_sys, text="1. Parámetros Eléctricos del Inversor", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5, padx=10, sticky="w")
        
        ctk.CTkLabel(f_sys, text="Tensión Nominal Output (V):").grid(row=1, column=0, padx=10, pady=2, sticky="e")
        self.ent_voltaje = ctk.CTkEntry(f_sys, width=160); self.ent_voltaje.insert(0, "800"); self.ent_voltaje.grid(row=1, column=1, padx=10, pady=2, sticky="w")

        ctk.CTkLabel(f_sys, text="Potencia Nominal (VA):").grid(row=2, column=0, padx=10, pady=2, sticky="e")
        self.ent_potencia = ctk.CTkEntry(f_sys, width=160); self.ent_potencia.insert(0, "330000"); self.ent_potencia.grid(row=2, column=1, padx=10, pady=2, sticky="w")

        ctk.CTkLabel(f_sys, text="Corriente Máx Inversor Imax (A):").grid(row=3, column=0, padx=10, pady=2, sticky="e")
        self.ent_i_inv = ctk.CTkEntry(f_sys, width=160); self.ent_i_inv.insert(0, "238.2"); self.ent_i_inv.grid(row=3, column=1, padx=10, pady=2, sticky="w")

        # PANEL 2: Conductor
        f_cond = ctk.CTkFrame(f); f_cond.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(f_cond, text="2. Especificación Técnica del Conductor", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5, padx=10, sticky="w")

        ctk.CTkLabel(f_cond, text="Material Conductor:").grid(row=1, column=0, padx=10, pady=2, sticky="e")
        self.combo_material = ctk.CTkOptionMenu(f_cond, values=["Aluminio", "Cobre"], width=160, command=self.auto_actualizar_resistencia)
        self.combo_material.set("Aluminio"); self.combo_material.grid(row=1, column=1, padx=10, pady=2, sticky="w")

        ctk.CTkLabel(f_cond, text="Material Aislamiento:").grid(row=2, column=0, padx=10, pady=2, sticky="e")
        self.combo_aislamiento = ctk.CTkOptionMenu(f_cond, values=["XLPE", "PVC"], width=160, command=self.auto_actualizar_resistencia)
        self.combo_aislamiento.set("XLPE"); self.combo_aislamiento.grid(row=2, column=1, padx=10, pady=2, sticky="w")

        ctk.CTkLabel(f_cond, text="Sección Conductor (mm²):").grid(row=3, column=0, padx=10, pady=2, sticky="e")
        self.combo_seccion = ctk.CTkOptionMenu(f_cond, values=["25", "35", "50", "70", "95", "120", "150", "185", "240", "300", "400", "500"], width=160, command=self.auto_actualizar_resistencia)
        self.combo_seccion.set("300"); self.combo_seccion.grid(row=3, column=1, padx=10, pady=2, sticky="w")

        ctk.CTkLabel(f_cond, text="Resistencia R20°C (Ω/km):").grid(row=4, column=0, padx=10, pady=2, sticky="e")
        self.ent_r20 = ctk.CTkEntry(f_cond, width=160); self.ent_r20.insert(0, "0.1000"); self.ent_r20.grid(row=4, column=1, padx=10, pady=2, sticky="w")

        ctk.CTkLabel(f_cond, text="Longitud del Tramo (m):").grid(row=5, column=0, padx=10, pady=2, sticky="e")
        self.ent_longitud = ctk.CTkEntry(f_cond, width=160); self.ent_longitud.insert(0, "132.741"); self.ent_longitud.grid(row=5, column=1, padx=10, pady=2, sticky="w")

        # PANEL 3: Canalización
        f_inst = ctk.CTkFrame(f); f_inst.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(f_inst, text="3. Parámetros del Entorno para Cálculo de Factores", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5, padx=10, sticky="w")

        ctk.CTkLabel(f_inst, text="Método de Instalación:").grid(row=1, column=0, padx=10, pady=2, sticky="e")
        self.combo_metodo = ctk.CTkOptionMenu(f_inst, values=["D2 (Ductos Subterráneos)", "D2 (Directamente Enterrado)", "F (Bandeja Portacables)"], width=200, command=self.recalcular_factores_en_vivo)
        self.combo_metodo.set("D2 (Ductos Subterráneos)"); self.combo_metodo.grid(row=1, column=1, padx=10, pady=2, sticky="w")

        ctk.CTkLabel(f_inst, text="Temperatura Suelo/Aire (°C):").grid(row=2, column=0, padx=10, pady=2, sticky="e")
        self.ent_temp = ctk.CTkEntry(f_inst, width=160); self.ent_temp.insert(0, "33.87"); self.ent_temp.grid(row=2, column=1, padx=10, pady=2, sticky="w")
        self.ent_temp.bind("<KeyRelease>", self.recalcular_factores_en_vivo)

        ctk.CTkLabel(f_inst, text="Número de Circuitos:").grid(row=3, column=0, padx=10, pady=2, sticky="e")
        self.ent_num_ctos = ctk.CTkEntry(f_inst, width=160); self.ent_num_ctos.insert(0, "6"); self.ent_num_ctos.grid(row=3, column=1, padx=10, pady=2, sticky="w")
        self.ent_num_ctos.bind("<KeyRelease>", self.recalcular_factores_en_vivo)

        ctk.CTkLabel(f_inst, text="Espaciado (para D2):").grid(row=4, column=0, padx=10, pady=2, sticky="e")
        self.combo_espaciado = ctk.CTkOptionMenu(f_inst, values=["Tocándose", "Un diámetro", "0.125 m", "0.25 m", "0.5 m"], width=160, command=self.recalcular_factores_en_vivo)
        self.combo_espaciado.set("0.5 m"); self.combo_espaciado.grid(row=4, column=1, padx=10, pady=2, sticky="w")

        ctk.CTkLabel(f_inst, text="Profundidad m (para D2):").grid(row=5, column=0, padx=10, pady=2, sticky="e")
        self.ent_profundidad = ctk.CTkEntry(f_inst, width=160); self.ent_profundidad.insert(0, "1.2"); self.ent_profundidad.grid(row=5, column=1, padx=10, pady=2, sticky="w")
        self.ent_profundidad.bind("<KeyRelease>", self.recalcular_factores_en_vivo)

        ctk.CTkLabel(f_inst, text="Resistividad K.m/W (para D2):").grid(row=6, column=0, padx=10, pady=2, sticky="e")
        self.ent_resistividad = ctk.CTkEntry(f_inst, width=160); self.ent_resistividad.insert(0, "1.2"); self.ent_resistividad.grid(row=6, column=1, padx=10, pady=2, sticky="w")
        self.ent_resistividad.bind("<KeyRelease>", self.recalcular_factores_en_vivo)

        # PANEL 4: Factores Vivos
        f_factores = ctk.CTkFrame(f, fg_color="#1a232a"); f_factores.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(f_factores, text="Factores de Corrección Calculados (IEC 60364-5-52)", font=("Arial", 11, "bold"), text_color="#3399ff").pack(pady=3, padx=10)
        self.lbl_k_detalles = ctk.CTkLabel(f_factores, text="", font=("Consolas", 11), text_color="cyan", justify="center")
        self.lbl_k_detalles.pack(pady=5, padx=10)

        # PANEL 5: Cortocircuito
        f_cc = ctk.CTkFrame(f); f_cc.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(f_cc, text="4. Parámetros de Cortocircuito", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5, padx=10, sticky="w")

        ctk.CTkLabel(f_cc, text="Corriente Falla Icc (kA):").grid(row=1, column=0, padx=10, pady=2, sticky="e")
        self.ent_icc = ctk.CTkEntry(f_cc, width=160); self.ent_icc.insert(0, "25.87"); self.ent_icc.grid(row=1, column=1, padx=10, pady=2, sticky="w")

        # BOTONES DE ACCIÓN
        f_btn = ctk.CTkFrame(f, fg_color="transparent"); f_btn.pack(pady=10)
        ctk.CTkButton(f_btn, text="Calcular y Verificar", command=self.ejecutar_evaluacion, fg_color="#1f538d", width=160).pack(side="left", padx=5)
        ctk.CTkButton(f_btn, text="Exportar Excel", command=self.exportar_excel, fg_color="green", hover_color="darkgreen", width=120).pack(side="left", padx=5)
        ctk.CTkButton(f_btn, text="Exportar PDF", command=self.exportar_pdf, fg_color="darkred", hover_color="red", width=120).pack(side="left", padx=5)

        # RESULTADOS
        self.lbl_resultado = ctk.CTkLabel(f, text="Ajuste los parámetros y presione 'Calcular y Verificar'.", font=("Consolas", 11), text_color="yellow", justify="left")
        self.lbl_resultado.pack(pady=10, padx=15)

        self.recalcular_factores_en_vivo()

    def recalcular_factores_en_vivo(self, *args):
        try:
            metodo = self.combo_metodo.get()
            aislamiento = self.combo_aislamiento.get()
            temp_c = float(self.ent_temp.get()) if self.ent_temp.get() else 20.0
            num_ctos = int(self.ent_num_ctos.get()) if self.ent_num_ctos.get() else 1
            espaciado = self.combo_espaciado.get()
            prof_m = float(self.ent_profundidad.get()) if self.ent_profundidad.get() else 0.7
            res_k_m_w = float(self.ent_resistividad.get()) if self.ent_resistividad.get() else 2.5

            k1 = calcular_k1(temp_c, aislamiento, metodo)
            k2 = calcular_k2(num_ctos, espaciado, metodo)

            if "D2" in metodo:
                self.ent_profundidad.configure(state="normal")
                self.ent_resistividad.configure(state="normal")
                self.combo_espaciado.configure(state="normal")
                k3 = calcular_k3(prof_m)
                tipo_sub = "Ductos Subterráneos" if "Ductos" in metodo else "Directamente Enterrado"
                k4 = calcular_k4(res_k_m_w, tipo_sub)
                k_total = k1 * k2 * k3 * k4
                self.lbl_k_detalles.configure(
                    text=f"k1 (Temp {temp_c}°C): {k1:.4f}  |  k2 (Group {num_ctos} ctos): {k2:.2f}\n"
                         f"k3 (Prof {prof_m}m): {k3:.2f}  |  k4 (Resist {res_k_m_w} K.m/W): {k4:.3f}\n"
                         f"---> FACTOR DE CORRECCIÓN TOTAL: {k_total:.4f}"
                )
            else:
                self.ent_profundidad.configure(state="disabled")
                self.ent_resistividad.configure(state="disabled")
                self.combo_espaciado.configure(state="disabled")
                k3, k4 = 1.0, 1.0
                k_total = k1 * k2
                self.lbl_k_detalles.configure(
                    text=f"k1 (Temp Aire {temp_c}°C): {k1:.4f}  |  k2 (Tray Group {num_ctos} ctos): {k2:.2f}\n"
                         f"k3 (N/A Aire): 1.0000  |  k4 (N/A Aire): 1.0000\n"
                         f"---> FACTOR DE CORRECCIÓN TOTAL: {k_total:.4f}"
                )
            return k1, k2, k3, k4, k_total
        except Exception:
            return 1.0, 1.0, 1.0, 1.0, 1.0

    def auto_actualizar_resistencia(self, *args):
        mat = self.combo_material.get()
        sec = int(self.combo_seccion.get())
        r20, _, _ = calcular_resistencia_temperatura(sec, mat, self.combo_aislamiento.get())
        self.ent_r20.configure(state="normal")
        self.ent_r20.delete(0, "end")
        self.ent_r20.insert(0, f"{r20:.4f}")
        self.recalcular_factores_en_vivo()

    def ejecutar_evaluacion(self):
        try:
            v_nom = float(self.ent_voltaje.get())
            pot_va = float(self.ent_potencia.get())
            i_max_inv = float(self.ent_i_inv.get())
            material = self.combo_material.get()
            aislamiento = self.combo_aislamiento.get()
            seccion = int(self.combo_seccion.get())
            r20 = float(self.ent_r20.get())
            longitud = float(self.ent_longitud.get())
            icc_ka = float(self.ent_icc.get())

            k1, k2, k3, k4, k_total = self.recalcular_factores_en_vivo()
            metodo_raw = self.combo_metodo.get()

            i_diseno = calcular_corriente_diseno(i_max_inv)
            r20, r_t, x_km = calcular_resistencia_temperatura(seccion, material, aislamiento)
            i_z, i_z_corregida = obtener_ampacidad_corregida(seccion, metodo_raw, material, aislamiento, k1, k2, k3, k4)
            caida_v, caida_p = calcular_caida_tension(i_diseno, longitud, r_t, x_km, v_nom)
            perdidas_w = calcular_perdidas_potencia(i_diseno, longitud, r_t)
            porc_perdidas = (perdidas_w / pot_va) * 100.0
            l_max = calcular_longitud_maxima(i_diseno, r_t, x_km, v_nom, 3.0)
            tm, k_const = calcular_tiempo_cortocircuito(seccion, icc_ka, material, aislamiento)

            est_amp = "✅ CUMPLE" if i_z_corregida >= i_diseno else "❌ SOBRECARGADO"
            est_caida = "✅ CUMPLE (<3%)" if caida_p <= 3.0 else "❌ ALERTA (>3%)"
            est_cc = "✅ CUMPLE (>150ms)" if tm >= 0.15 else "❌ NO CUMPLE"

            res_texto = (
                f"=== EVALUACIÓN TÉCNICA NORMATIVA ===\n\n"
                f"• Corriente Imax Inversor: {i_max_inv:.2f} A  -->  Corriente de Diseño (125%): {i_diseno:.2f} A\n"
                f"• Resistencia R20°C: {r20:.4f} Ω/km  -->  R(T) Corregida a Operación: {r_t:.4f} Ω/km\n"
                f"• Reactancia X: {x_km:.4f} Ω/km\n\n"
                f"1. AMPACIDAD TÉRMICA (IEC 60364-5-52):\n"
                f"   - Ampacidad Base Tabla (Iz): {i_z} A\n"
                f"   - Factor de Corrección Total: {k_total:.4f}\n"
                f"   - Ampacidad Corregida (I'z): {i_z_corregida:.2f} A  [{est_amp}]\n\n"
                f"2. CAÍDA DE TENSIÓN Y PÉRDIDAS ({longitud} m):\n"
                f"   - Caída de Tensión: {caida_v:.2f} V ({caida_p:.3f}%)  [{est_caida}]\n"
                f"   - Pérdidas Activas BT: {perdidas_w:.2f} W ({porc_perdidas:.3f}%)\n"
                f"   - Longitud Máxima Permitida (3.0%): {l_max:.2f} m\n\n"
                f"3. RESISTENCIA A CORTOCIRCUITO (IEC 60364-4-43):\n"
                f"   - Icc Falla: {icc_ka} kA | Constante K: {k_const}\n"
                f"   - Tiempo Máx Admisible (tm): {tm:.3f} s  [{est_cc}]"
            )
            self.lbl_resultado.configure(text=res_texto)

            return {
                "Voltaje (V)": v_nom, "Potencia (VA)": pot_va, "Imax Inversor (A)": i_max_inv,
                "Id (A)": round(i_diseno, 2), "Material": material, "Aislamiento": aislamiento,
                "Sección (mm2)": seccion, "Método": metodo_raw, "R20 (Ω/km)": r20,
                "R_T (Ω/km)": round(r_t, 4), "X (Ω/km)": x_km, "k1": k1, "k2": k2, "k3": k3, "k4": k4,
                "k_total": round(k_total, 4), "Iz Base (A)": i_z, "I'z Corregida (A)": round(i_z_corregida, 2),
                "Longitud (m)": longitud, "Caída (V)": round(caida_v, 2), "Caída (%)": round(caida_p, 3),
                "Pérdidas (W)": round(perdidas_w, 2), "Pérdidas (%)": round(porc_perdidas, 3),
                "Longitud Máx (m)": round(l_max, 2), "Icc (kA)": icc_ka, "Tm Cortocircuito (s)": round(tm, 3)
            }
        except ValueError:
            self.lbl_resultado.configure(text="⚠️ Error: Revisa que todas las casillas tengan datos numéricos.")
            return None

    def exportar_excel(self):
        datos = self.ejecutar_evaluacion()
        if datos:
            pd.DataFrame([datos]).to_excel("Reporte_Conductores_AC.xlsx", index=False)
            self.lbl_resultado.configure(text="✅ Exportado a Excel exitosamente: Reporte_Conductores_AC.xlsx")

    def exportar_pdf(self):
        datos = self.ejecutar_evaluacion()
        if datos:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=14, style="B")
            pdf.cell(200, 10, txt="Memoria de Cálculo de Cable AC - OpenPowerStudio", ln=True, align='C')
            pdf.ln(5)
            pdf.set_font("Arial", size=10)
            for k, v in datos.items():
                pdf.cell(200, 6, txt=f"{k}: {v}", ln=True)
            pdf.output("Reporte_Conductores_AC.pdf")
            self.lbl_resultado.configure(text="✅ Exportado a PDF exitosamente: Reporte_Conductores_AC.pdf")

    # -------------------------------------------------------------
    # 4. PLANTILLAS PARA FUTUROS MÓDULOS (DC, MT, ABOUT)
    # -------------------------------------------------------------
    def _construir_modulo_dc(self):
        f = self.frame_dc
        ctk.CTkLabel(f, text="🔌 Módulo: Cableado DC y Strings Fotovoltaicos", font=("Arial", 16, "bold")).pack(pady=20)
        ctk.CTkLabel(f, text="¡Próximamente en OpenPowerStudio!\n\nEste módulo permitirá calcular cables Solar 1.5kV DC,\nprotección de sobrecorriente por string e incompatibilidades de tensión.", font=("Arial", 12), text_color="gray").pack(pady=10)

    def _construir_modulo_mt(self):
        f = self.frame_mt
        ctk.CTkLabel(f, text="🏭 Módulo: Cableado e Infraestructura de Media Tensión", font=("Arial", 16, "bold")).pack(pady=20)
        ctk.CTkLabel(f, text="¡Próximamente en OpenPowerStudio!\n\nEste módulo permitirá dimensionar circuitos en 13.2 kV / 34.5 kV,\npérdidas en transformadores Skid y coordinación de protecciones.", font=("Arial", 12), text_color="gray").pack(pady=10)

    def _construir_modulo_about(self):
        f = self.frame_about
        ctk.CTkLabel(f, text="OpenPowerStudio Project", font=("Arial", 18, "bold")).pack(pady=15)
        text = (
            "OpenPowerStudio es un proyecto de código abierto diseñado para automatizar\n"
            "las memorias de cálculo fotovoltaicas y eléctricas bajo estándares IEC e IEEE.\n\n"
            "• Organización: github.com/OpenPowerStudio\n"
            "• Licencia: MIT License (Código Libre)\n\n"
            "¡Buscamos colaboradores! Si deseas agregar soporte para normas NEC,\n"
            "crear pruebas unitarias o desarrollar nuevos módulos, envía tu Pull Request en GitHub."
        )
        ctk.CTkLabel(f, text=text, font=("Arial", 12), text_color="cyan", justify="center").pack(pady=10)

if __name__ == "__main__":
    app = OpenPowerStudioApp()
    app.mainloop()