import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN ---
PASSWORD = "TuClaveSecreta" 
st.set_page_config(page_title="MZero Web", layout="wide")

if 'lista_alumnos' not in st.session_state: st.session_state.lista_alumnos = []

# --- LOGO ---
try: st.sidebar.image("logo_mzero.png")
except: st.sidebar.warning("Logo no encontrado.")

if st.sidebar.text_input("Contraseña:", type="password") != PASSWORD:
    st.stop()

st.title("M-Zero Pro - Evaluación")

# Formulario
with st.container():
    c1, c2 = st.columns(2)
    profesor = c1.text_input("Profesor", key="f_prof")
    curso = c1.text_input("Curso", key="f_cur")
    modulo = c2.text_input("Módulo", key="f_mod")
    nivel = c2.text_input("Nivel", key="f_niv")
    alumno = st.text_input("Nombre del Alumno", key="f_alu")

# IMPORTANTE: Estos nombres deben coincidir exactamente con los del if de abajo
pesos = {
    "1. Tasa de eficiencia": 12, "2. Precisión geométrica": 5, "3. Autonomía": 12, 
    "4. Índice de mermas": 5, "5. Mantenimiento": 3, "6. Desempeño temporal": 10,
    "7. Escenarios prácticas": 10, "8. Escenarios averías": 10, "9. Precisión conceptual": 5, 
    "10. Seguridad": 5, "11. Fiabilidad": 10, "12. Aprendizaje": 8, "13. Comunicación": 5
}

st.subheader("Puntuación (1=Insuficiente, 3=Suficiente, 5=Excelente)")
notas = {}
for crit, p in pesos.items():
    notas[crit] = int(st.radio(f"{crit} ({p}%)", [1, 2, 3, 4, 5], horizontal=True, index=2))

# --- FÓRMULA CORREGIDA ---
# (val-1) * 2.5: Si marcas 3, (2 * 2.5) = 5.0 (Aprobado exacto)
total = sum(((notas[crit] - 1) * 2.5) * (pesos[crit] / 100) for crit in pesos)
nota_final = round(total, 1)

# Lógica de Seguridad (Nombre exacto: "10. Seguridad")
if notas["10. Seguridad"] == 1:
    nota_final, resultado = 4.0, "SUSPENSO (Línea Roja)"
else:
    resultado = "APROBADO" if nota_final >= 5 else "SUSPENSO"

st.metric("NOTA FINAL", f"{nota_final} - {resultado}")

# Botón Guardar
if st.button("GUARDAR ALUMNO"):
    st.session_state.lista_alumnos.append({"Alumno": alumno, "Nota": nota_final, "Estado": resultado})
    st.rerun()

# Tabla
st.divider()
if st.session_state.lista_alumnos:
    st.table(pd.DataFrame(st.session_state.lista_alumnos))
    if st.button("ENVIAR Y LIMPIAR"):
        st.session_state.lista_alumnos = []
        st.rerun()
