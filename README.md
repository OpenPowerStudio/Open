# ⚡ OpenPowerStudio - Calculadora de Conductores / Conductor Calculator (AC / DC / MT)

[**Español**](#español) | [**English**](#english)

---

## <a name="español"></a>🇪🇸 Español

### 🎯 Objetivo del Proyecto
**OpenPowerStudio** es un suite de software libre (*Open Source*) para el dimensionamiento, cálculo térmico, verificación de caída de tensión y cortocircuito en conductores eléctricos para plantas solares fotovoltaicas e instalaciones industriales.

El objetivo es automatizar las memorias de cálculo según normativas internacionales (**IEC 60364-5-52**, **IEC 60364-4-43**, **RETIE**, **NTC 2050**), proporcionando una interfaz intuitiva y reportes en Excel/PDF.

### 🚀 Estado de los Módulos
- **🟢 Cableado de Baja Tensión AC (`modulos/conductores_ac.py`) - *Completado***
  - Corriente de diseño automática ($I_d = 125\% \cdot I_{\text{max}}$).
  - Corrección de resistencia $R(T)$ a la temperatura máxima de operación ($90^\circ\text{C}$ XLPE / $70^\circ\text{C}$ PVC).
  - Interpolación dinámica e instantánea de factores de corrección IEC:
    - $k_1$: Temperatura de suelo/aire (Tablas B.52.14 / B.52.15).
    - $k_2$: Agrupamiento para canales enterrados D2 o bandejas F (Tablas B.52.18 / B.52.17).
    - $k_3$: Profundidad de enterramiento (UNE 211435).
    - $k_4$: Resistividad térmica del suelo (Tabla B.52.16).
  - Verificación de caída de tensión trifásica, pérdidas activas ($3 \cdot R \cdot I^2$) y resistencia a cortocircuito ($t_m$).
- **🟡 Cableado DC y Strings (`modulos/conductores_dc.py`) - *En Desarrollo***
- **🔴 Media Tensión (`modulos/conductores_mt.py`) - *Planeado***

### 🤝 ¡Queremos tu ayuda!
No soy un experto en programación, pero estoy aprendiendo y tratando de sacar este proyecto adelante porque sé lo útil que es para los ingenieros. **¡Cualquier ayuda es bienvenida!** 
Si quieres aportar corrigiendo errores, optimizando código, mejorando la UI o agregando nuevas funciones normativas, ¡envía tu Pull Request o abre una Discusión!

### 🛠️ Instalación y Uso
```bash
git clone [https://github.com/OpenPowerStudio/calculadora_conductores.git](https://github.com/OpenPowerStudio/calculadora_conductores.git)
cd calculadora_conductores
pip install customtkinter pandas openpyxl fpdf
python main.py

# ⚡ OpenPowerStudio - Conductor & Cable Calculator (AC / DC / MV)

**OpenPowerStudio** is an open-source software suite designed for cable sizing, thermal capacity calculation, voltage drop verification, and short-circuit analysis in photovoltaic solar plants and industrial electrical installations[cite: 1, 3, 5].

---

## 🎯 Project Overview
The main objective of OpenPowerStudio is to provide an intuitive, open-source Python tool that automates technical calculation reports following international and national standards (**IEC 60364-5-52**, **IEC 60364-4-43**, **RETIE**, **NTC 2050**)[cite: 1, 3, 5].

It features dynamic factor interpolation, real-time recalculations, and automated export capabilities to Excel and PDF.

---

## 🚀 Module Roadmap & Status

### 🟢 1. Low Voltage AC Cable Sizing (`modulos/conductores_ac.py`) — *Completed*
- **Design Current Calculation:** Automated safety margin ($I_d = 125\% \cdot I_{\text{max}}$)[cite: 1, 5].
- **Operating Temperature Adjustment:** Corrects DC resistance $R_{20}$ to operating temperature $R(T)$ ($90^\circ\text{C}$ for XLPE / $70^\circ\text{C}$ for PVC)[cite: 1, 3, 5].
- **Real-Time Dynamic Factor Interpolation (IEC 60364-5-52):**
  - $k_1$: Soil or air ambient temperature correction (Tables B.52.14 / B.52.15)[cite: 1, 3, 5].
  - $k_2$: Circuit grouping reduction factor for underground ducts D2 or cable trays F (Tables B.52.18 / B.52.17)[cite: 1, 3, 5].
  - $k_3$: Installation depth factor (UNE 211435)[cite: 1, 5].
  - $k_4$: Soil thermal resistivity correction factor (Table B.52.16)[cite: 1, 3, 5].
- **Electrical Verification:** Three-phase voltage drop, active power losses ($3 \cdot R \cdot I^2$), and maximum short-circuit withstand time ($t_m$)[cite: 1, 3, 5].
- **Reporting:** Export full technical memories to formatted Excel spreadsheets and PDF documents[cite: 1, 5].

### 🟡 2. DC Cable Sizing & Strings (`modulos/conductores_dc.py`) — *In Progress*
- Sizing solar cables for PV strings (1.5 kV DC).
- Combiner box grouping and overcurrent protection sizing.

### 🔴 3. Medium Voltage Grid & Transformers (`modulos/conductores_mt.py`) — *Planned*
- Medium Voltage (MV) cable sizing (13.2 kV / 34.5 kV).
- Transformer station losses and protection coordination.

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10 or higher.

### Quickstart
```bash
git clone [https://github.com/OpenPowerStudio/calculadora_conductores.git](https://github.com/OpenPowerStudio/calculadora_conductores.git)
cd calculadora_conductores
pip install customtkinter pandas openpyxl fpdf
python main.py

🤝 Join Us & Contribute!

I am learning Python while building this software to solve real-world electrical engineering challenges[cite: 1, 5]. All contributions are welcome!

Whether you want to fix bugs, refactor code, improve the UI, add new standards (such as NEC / IEEE), or write unit tests, please feel free to:

    Open an Issue or start a Discussion.

    Fork the repository and submit a Pull Request.