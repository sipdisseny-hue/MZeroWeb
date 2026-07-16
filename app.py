import streamlit as st
import pandas as pd
import requests

PASSWORD = "TuClaveSecreta" # Asegúrate de que esta sea la que usabas antes
st.set_page_config(page_title="MZero Web", layout="wide")

if 'lista_alumnos' not in st.session_state: st.session_state.lista_alumnos = []
if 'alumno_key' not in st.session_state: st.session_state.alumno_key = 0
if 'reset_todo' not in st.session_state: st.session_state.reset_todo = 0

# --- SIDEBAR ---
with st.sidebar:
    try: st.image("logo_mzero.png")
    except: st.warning("Logo no encontrado.")
    st.markdown("## M-Zero Pro - Evaluación")
    if st.text_input("Contraseña:", type="password") != PASSWORD:
        st.stop()

# --- FORMULARIO ---
with st.container():
    c1, c2, c3 = st.columns(3)
    profesor = c1.text_input("Profesor", key=f"f_prof_{st.session_state.reset_todo}")
    curso = c2.text_input("Curso", key=f"f_cur_{st.session_state.reset_todo}")
    modulo = c3.text_input("Módulo", key=f"f_mod_{st.session_state.reset_todo}")
    
    c4, c5 = st.columns(2)
    nivel = c4.text_input("Nivel del Bloque", key=f"f_niv_{st.session_state.reset_todo}")
    alumno = c5.text_input("Nombre del Alumno", key=f"f_alu_{st.session_state.alumno_key}")

criterios = [
    "1. Tasa de eficiencia", "2. Precisión geométrica y mecánica", "3. Autonomía ejecutiva",
    "4. Índice de mermas", "5. Mantenimiento de utillaje y entorno", "6. Factor de desempeño temporal",
    "7. Resolución escenarios de prácticas", "8. Resolución escenarios de averías",
    "9. Precisión conceptual y terminología", "10. Seguridad y normativas",
    "11. Fiabilidad y compromiso operativo", "12. Capacidad de aprendizaje",
    "13. Comunicación y respeto al superior"
]

st.subheader("Puntuación (1=Insuficiente, 3=Suficiente, 5=Excelente)")

cols = st.columns(4)
notas = {}
for i, crit in enumerate(criterios):
    with cols[i % 4]:
        with st.container(border=True):
            st.markdown(f"**{crit}**")
            notas[crit] = st.radio("puntuacion", [1, 2, 3, 4, 5], horizontal=True, key=f"rad_{crit}_{st.session_state.alumno_key}", index=None, label_visibility="collapsed")

if None not in notas.values() and alumno:
    nota_final = round(sum((notas[c] - 1) * 2.5 for c in criterios) / len(criterios), 1)
    res = "SUSPENSO (Línea Roja)" if notas["10. Seguridad y normativas"] == 1 else ("APROBADO" if nota_final >= 5 else "SUSPENSO")
    st.metric("NOTA FINAL", f"{nota_final} - {res}")
else:
    nota_final, res = None, None

if st.button("GUARDAR ALUMNO"):
    if nota_final is not None:
        registro = {"Alumno": alumno, "Profesor": profesor, "Curso": curso, "Modulo": modulo, "Nivel": nivel, "Nota": nota_final, "Estado": res}
        registro.update(notas)
        st.session_state.lista_alumnos.append(registro)
        st.session_state.alumno_key += 1
        st.rerun()

if st.session_state.lista_alumnos:
    st.table(pd.DataFrame(st.session_state.lista_alumnos))
    if st.button("ENVIAR TODO A GOOGLE SHEETS"):
        url = "https://script.google.com/macros/s/AKfycbw1PNXaXT23jXJdKPOO9vbwrx6tnBI-hvlJrJFMNKZiy7G1JsNkTY-C6Ql7Wym_l-GG-Q/exec"
        try:
            requests.post(url, json={"evaluaciones": st.session_state.lista_alumnos}, timeout=20)
            st.session_state.lista_alumnos = []
            st.session_state.reset_todo += 1
            st.session_state.alumno_key += 1
            st.rerun()
        except Exception as e: st.error(f"Error: {e}")
