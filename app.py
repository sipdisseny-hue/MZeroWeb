import streamlit as st
import pandas as pd
import requests

PASSWORD = "TuClaveSecreta" 
st.set_page_config(page_title="MZero Web", layout="wide")

# Inicialización
if 'lista_alumnos' not in st.session_state: 
    st.session_state.lista_alumnos = []
if 'form_key' not in st.session_state: 
    st.session_state.form_key = 0

# --- LOGO ---
try: st.sidebar.image("logo_mzero.png")
except: st.sidebar.warning("Logo no encontrado.")

if st.sidebar.text_input("Contraseña:", type="password") != PASSWORD:
    st.stop()

st.title("M-Zero Pro - Evaluación")

# Formulario
with st.container():
    c1, c2 = st.columns(2)
    # Sin 'value' para evitar bucles de estado. Usaremos el form_key para refrescarlos todos.
    profesor = c1.text_input("Profesor", key=f"f_prof_{st.session_state.form_key}")
    curso = c1.text_input("Curso", key=f"f_cur_{st.session_state.form_key}")
    modulo = c2.text_input("Módulo", key=f"f_mod_{st.session_state.form_key}")
    nivel = c2.text_input("Nivel", key=f"f_niv_{st.session_state.form_key}")
    alumno = c1.text_input("Nombre del Alumno", key=f"f_alu_{st.session_state.form_key}")

pesos = {
    "1. Tasa de eficiencia": 12, "2. Precisión geométrica": 5, "3. Autonomía": 12, 
    "4. Índice de mermas": 5, "5. Mantenimiento": 3, "6. Desempeño temporal": 10,
    "7. Escenarios prácticas": 10, "8. Escenarios averías": 10, "9. Precisión conceptual": 5, 
    "10. Seguridad": 5, "11. Fiabilidad": 10, "12. Aprendizaje": 8, "13. Comunicación": 5
}

notas = {}
for crit, p in pesos.items():
    notas[crit] = st.radio(f"{crit} ({p}%)", [1, 2, 3, 4, 5], horizontal=True, 
                           key=f"rad_{crit}_{st.session_state.form_key}", index=None)

# Cálculo
if None not in notas.values():
    total = sum(((notas[crit] - 1) * 2.5) * (pesos[crit] / 100) for crit in pesos)
    nota_final = round(total, 1)
    res = "SUSPENSO (Línea Roja)" if notas["10. Seguridad"] == 1 else ("APROBADO" if nota_final >= 5 else "SUSPENSO")
    st.metric("NOTA FINAL", f"{nota_final} - {res}")
else:
    nota_final, res = None, None

# Botón Guardar
if st.button("GUARDAR ALUMNO"):
    if nota_final is not None and alumno:
        # Guardamos datos incluyendo los fijos actuales
        st.session_state.lista_alumnos.append({
            "Alumno": alumno, "Profesor": profesor, "Curso": curso, 
            "Modulo": modulo, "Nivel": nivel, "Nota": nota_final, "Estado": res
        })
        st.session_state.form_key += 1 
        st.rerun()
    else:
        st.error("Completa el nombre y todas las puntuaciones.")

# Tabla y Envío
st.divider()
if st.session_state.lista_alumnos:
    st.table(pd.DataFrame(st.session_state.lista_alumnos))
    if st.button("ENVIAR TODO A GOOGLE SHEETS"):
        url = "https://script.google.com/macros/s/AKfycbw1PNXaXT23jXJdKPOO9vbwrx6tnBI-hvlJrJFMNKZiy7G1JsNkTY-C6Ql7Wym_l-GG-Q/exec"
        try:
            requests.post(url, json=st.session_state.lista_alumnos, timeout=15)
            st.success("Enviado.")
            # Borrado total: reiniciamos el estado
            st.session_state.lista_alumnos = []
            st.session_state.form_key += 100 
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
