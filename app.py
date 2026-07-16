import streamlit as st
import pandas as pd
import requests

PASSWORD = "TuClaveSecreta"
st.set_page_config(page_title="MZero Web", layout="wide")

if 'lista_alumnos' not in st.session_state: st.session_state.lista_alumnos = []
if 'alumno_key' not in st.session_state: st.session_state.alumno_key = 0
if 'reset_todo' not in st.session_state: st.session_state.reset_todo = 0

try: st.sidebar.image("logo_mzero.png")
except: st.sidebar.warning("Logo no encontrado.")

if st.sidebar.text_input("Contraseña:", type="password") != PASSWORD:
    st.stop()

st.title("M-Zero Pro - Evaluación")

with st.container():
    c1, c2 = st.columns(2)
    # CLAVES FIJAS: No se borran al guardar alumno, solo al enviar (gracias a reset_todo)
    profesor = c1.text_input("Profesor", key=f"f_prof_{st.session_state.reset_todo}")
    curso = c1.text_input("Curso", key=f"f_cur_{st.session_state.reset_todo}")
    modulo = c2.text_input("Módulo", key=f"f_mod_{st.session_state.reset_todo}")
    nivel = c2.text_input("Nivel del Bloque", key=f"f_niv_{st.session_state.reset_todo}")
    alumno = st.text_input("Nombre del Alumno", key=f"f_alu_{st.session_state.alumno_key}")

criterios = [
    "1. Tasa de eficiencia", "2. Precisión geométrica y mecánica", "3. Autonomía ejecutiva",
    "4. Índice de mermas", "5. Mantenimiento de utillaje y entorno", "6. Factor de desempeño temporal",
    "7. Resolución escenarios de prácticas", "8. Resolución escenarios de averías",
    "9. Precisión conceptual y terminología", "10. Seguridad y normativas",
    "11. Fiabilidad y compromiso operativo", "12. Capacidad de aprendizaje",
    "13. Comunicación y respeto al superior"
]

st.subheader("Puntuación (1=Insuficiente, 3=Suficiente, 5=Excelente)")
notas = {c: st.radio(c, [1, 2, 3, 4, 5], horizontal=True, key=f"rad_{c}_{st.session_state.alumno_key}", index=None) for c in criterios}

# NUEVO CÁLCULO: Un 3 es un 5.0. 
# La fórmula: (puntuación - 1) * 2.5 da como resultado: 1->0, 2->2.5, 3->5.0, 4->7.5, 5->10
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
        st.session_state.alumno_key += 1 # Solo borra alumno y notas
        st.rerun()

if st.session_state.lista_alumnos:
    st.table(pd.DataFrame(st.session_state.lista_alumnos))
    if st.button("ENVIAR TODO A GOOGLE SHEETS"):
        url = "https://script.google.com/macros/s/AKfycbw1PNXaXT23jXJdKPOO9vbwrx6tnBI-hvlJrJFMNKZiy7G1JsNkTY-C6Ql7Wym_l-GG-Q/exec"
        try:
            requests.post(url, json={"evaluaciones": st.session_state.lista_alumnos}, timeout=20)
            st.session_state.lista_alumnos = []
            st.session_state.reset_todo += 1 # Borra el profesor, curso, etc.
            st.session_state.alumno_key += 1 # Borra el alumno
            st.rerun()
        except Exception as e: st.error(f"Error: {e}")
