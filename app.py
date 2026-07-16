import streamlit as st
import pandas as pd
import requests

PASSWORD = "TuClaveSecreta"
st.set_page_config(page_title="MZero Web", layout="wide")

# Gestión de estado
if 'lista_alumnos' not in st.session_state: st.session_state.lista_alumnos = []
if 'form_reset' not in st.session_state: st.session_state.form_reset = 0

# --- LOGO ---
try: st.sidebar.image("logo_mzero.png")
except: st.sidebar.warning("Logo no encontrado.")

if st.sidebar.text_input("Contraseña:", type="password") != PASSWORD:
    st.stop()

st.title("M-Zero Pro - Evaluación")

# Formulario
with st.container():
    c1, c2 = st.columns(2)
    # Estas keys dependen de form_reset, así que se vaciarán al enviar
    profesor = c1.text_input("Profesor", key=f"prof_{st.session_state.form_reset}")
    curso = c1.text_input("Curso", key=f"curs_{st.session_state.form_reset}")
    modulo = c2.text_input("Módulo", key=f"mod_{st.session_state.form_reset}")
    nivel = c2.text_input("Nivel del Bloque", key=f"niv_{st.session_state.form_reset}")
    alumno = st.text_input("Nombre del Alumno", key=f"alu_{st.session_state.form_reset}")

# Textos criterios completos
criterios = [
    "Tasa de eficiencia", "Precisión geométrica y mecánica", "Autonomía ejecutiva",
    "Índice de mermas", "Mantenimiento de utillaje y entorno", "Factor de desempeño temporal",
    "Resolución escenarios de prácticas", "Resolución escenarios de averías",
    "Precisión conceptual y terminología", "Seguridad y normativas",
    "Fiabilidad y compromiso operativo", "Capacidad de aprendizaje",
    "Comunicación y respeto al superior"
]

pesos = {
    "Tasa de eficiencia": 12, "Precisión geométrica y mecánica": 5, "Autonomía ejecutiva": 12,
    "Índice de mermas": 5, "Mantenimiento de utillaje y entorno": 3, "Factor de desempeño temporal": 10,
    "Resolución escenarios de prácticas": 10, "Resolución escenarios de averías": 10,
    "Precisión conceptual y terminología": 5, "Seguridad y normativas": 5,
    "Fiabilidad y compromiso operativo": 10, "Capacidad de aprendizaje": 8,
    "Comunicación y respeto al superior": 5
}

st.subheader("Puntuación (1=Insuficiente, 3=Suficiente, 5=Excelente)")
notas = {}
for crit in criterios:
    notas[crit] = st.radio(crit, [1, 2, 3, 4, 5], horizontal=True, key=f"rad_{crit}_{st.session_state.form_reset}", index=None)

# Cálculo
if None not in notas.values():
    total = sum(((notas[crit] - 1) * 2.5) * (pesos[crit] / 100) for crit in criterios)
    nota_final = round(total, 1)
    res = "SUSPENSO (Línea Roja)" if notas["Seguridad y normativas"] == 1 else ("APROBADO" if nota_final >= 5 else "SUSPENSO")
    st.metric("NOTA FINAL", f"{nota_final} - {res}")
else:
    nota_final, res = None, None

# Guardar alumno
if st.button("GUARDAR ALUMNO"):
    if nota_final is not None and alumno:
        st.session_state.lista_alumnos.append({
            "Alumno": alumno, "Profesor": profesor, "Curso": curso, 
            "Modulo": modulo, "Nivel": nivel, "Nota": nota_final, "Estado": res
        })
        # Al sumar 1, solo borramos el nombre del alumno y las notas (al tener diferente key base)
        st.session_state.form_reset += 1 
        st.rerun()
    else:
        st.error("Completa el nombre y todas las puntuaciones.")

# Envío (Google Sheets)
if st.session_state.lista_alumnos:
    st.table(pd.DataFrame(st.session_state.lista_alumnos))
    if st.button("ENVIAR TODO A GOOGLE SHEETS"):
        url = "https://script.google.com/macros/s/AKfycbw1PNXaXT23jXJdKPOO9vbwrx6tnBI-hvlJrJFMNKZiy7G1JsNkTY-C6Ql7Wym_l-GG-Q/exec"
        try:
            # ESTRUCTURA ANTIGUA RESTAURADA: {"evaluaciones": ...}
            payload = {"evaluaciones": st.session_state.lista_alumnos}
            resp = requests.post(url, json=payload, timeout=20)
            if resp.status_code == 200:
                st.success("Enviado correctamente.")
                st.session_state.lista_alumnos = []
                st.session_state.form_reset += 100 # BORRADO TOTAL
                st.rerun()
            else:
                st.error(f"Error {resp.status_code}: Revisa tu Google Script.")
        except Exception as e:
            st.error(f"Error al enviar: {e}")
