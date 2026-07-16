import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN ---
PASSWORD = "TuClaveSecreta" 
st.set_page_config(page_title="MZero Web", layout="wide")

if 'lista_alumnos' not in st.session_state: st.session_state.lista_alumnos = []
if 'form_key' not in st.session_state: st.session_state.form_key = 0

# --- LOGO ---
try: st.sidebar.image("logo_mzero.png")
except: st.sidebar.warning("Logo no encontrado.")

if st.sidebar.text_input("Contraseña:", type="password") != PASSWORD:
    st.stop()

st.title("M-Zero Pro - Evaluación")

# Formulario
with st.container():
    c1, c2 = st.columns(2)
    # Campos fijos (sin key dinámica para que no se borren al guardar)
    profesor = c1.text_input("Profesor", key="f_prof")
    curso = c1.text_input("Curso", key="f_cur")
    modulo = c2.text_input("Módulo", key="f_mod")
    nivel = c2.text_input("Nivel", key="f_niv")
    # Campo alumno con key dinámica para borrarse al guardar
    alumno = st.text_input("Nombre del Alumno", key=f"f_alu_{st.session_state.form_key}")

pesos = {
    "1. Tasa de eficiencia": 12, "2. Precisión geométrica": 5, "3. Autonomía": 12, 
    "4. Índice de mermas": 5, "5. Mantenimiento": 3, "6. Desempeño temporal": 10,
    "7. Escenarios prácticas": 10, "8. Escenarios averías": 10, "9. Precisión conceptual": 5, 
    "10. Seguridad": 5, "11. Fiabilidad": 10, "12. Aprendizaje": 8, "13. Comunicación": 5
}

st.subheader("Puntuación (1=Insuficiente, 3=Suficiente, 5=Excelente)")
notas = {}
for crit, p in pesos.items():
    # index=None asegura que no haya nada marcado al iniciar
    notas[crit] = st.radio(f"{crit} ({p}%)", [1, 2, 3, 4, 5], horizontal=True, 
                           key=f"rad_{crit}_{st.session_state.form_key}", index=None)

# Cálculo solo si todos los criterios están marcados
if None not in notas.values():
    total = sum(((notas[crit] - 1) * 2.5) * (pesos[crit] / 100) for crit in pesos)
    nota_final = round(total, 1)

    if notas["10. Seguridad"] == 1:
        nota_final, resultado = 4.0, "SUSPENSO (Línea Roja)"
    else:
        resultado = "APROBADO" if nota_final >= 5 else "SUSPENSO"

    st.metric("NOTA FINAL", f"{nota_final} - {resultado}")
else:
    nota_final, resultado = None, None
    st.warning("Selecciona una puntuación en todos los criterios.")

# Botón Guardar
if st.button("GUARDAR ALUMNO"):
    if nota_final is not None and alumno:
        st.session_state.lista_alumnos.append({"Alumno": alumno, "Nota": nota_final, "Estado": resultado})
        st.session_state.form_key += 1 
        st.rerun()
    else:
        st.error("Completa el nombre del alumno y todas las puntuaciones.")

# Tabla
st.divider()
if st.session_state.lista_alumnos:
    st.table(pd.DataFrame(st.session_state.lista_alumnos))
    if st.button("ENVIAR Y LIMPIAR SESIÓN"):
        st.session_state.lista_alumnos = []
        st.session_state.form_key += 100 
        st.rerun()
