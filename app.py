import streamlit as st
import requests

# --- CONFIGURACIÓN ---
# Reemplaza 'TuClaveSecreta' por la contraseña que quieras poner a tu web
PASSWORD = "TuClaveSecreta" 

# Protegemos el acceso
def check_password():
    st.sidebar.title("Acceso Profesorado")
    input_pass = st.sidebar.text_input("Introduce la contraseña:", type="password")
    if input_pass != PASSWORD:
        st.warning("Acceso restringido. Introduce la contraseña.")
        st.stop()

check_password()

# --- APP M-ZERO ---
st.title("M-Zero Pro - Evaluación Acumulativa")

# Estado para guardar alumnos en memoria antes de enviar
if 'lista_alumnos' not in st.session_state:
    st.session_state.lista_alumnos = []

# Datos del profesor y alumno
with st.container():
    profesor = st.text_input("Profesor")
    curso = st.text_input("Curso")
    modulo = st.text_input("Módulo")
    nivel = st.text_input("Nivel del bloque")
    alumno = st.text_input("Nombre del Alumno")

# Criterios de evaluación
criterios = [
    "1. Tasa de eficiencia", "2. Precisión geométrica y mecánica", "3. Autonomía ejecutiva",
    "4. Índice de mermas", "5. Mantenimiento de utillaje y entorno", "6. Factor de desempeño temporal",
    "7. Resolución escenarios de prácticas", "8. Resolución escenarios de averías",
    "9. Precisión conceptual y terminología", "10. Seguridad y normativas",
    "11. Fiabilidad y compromiso operativo", "12. Capacidad de aprendizaje", "13. Comunicación y respeto al superior"
]

notas = {}
st.subheader("Criterios de Evaluación")
for crit in criterios:
    # Generamos los botones 1-5 para cada criterio
    notas[crit] = st.radio(crit, ["1", "2", "3", "4", "5"], horizontal=True, key=crit)

# Cálculo de nota
valores = [int(v) for v in notas.values()]
total = sum(valores) / len(valores)
st.metric("Nota Total", f"{total:.2f}")

# Botones de acción
if st.button("GUARDAR ALUMNO Y SEGUIR"):
    if not (profesor and alumno):
        st.error("Debes rellenar Profesor y Nombre del Alumno.")
    else:
        st.session_state.lista_alumnos.append({
            "profesor": profesor, "curso": curso, "modulo": modulo,
            "nivel": nivel, "alumno": alumno, "nota_total": total, "notas": notas
        })
        st.success(f"Alumno {alumno} guardado. Total en lista: {len(st.session_state.lista_alumnos)}")

if st.button("ENVIAR TODO"):
    if not st.session_state.lista_alumnos:
        st.warning("La lista está vacía.")
    else:
        # AQUÍ PEGA TU URL DE GOOGLE APPS SCRIPT
        url = "https://script.google.com/macros/s/AKfycbw1PNXaXT23jXJdKPOO9vbwrx6tnBI-hvlJrJFMNKZiy7G1JsNkTY-C6Ql7Wym_l-GG-Q/exec"
        try:
            requests.post(url, json={"evaluaciones": st.session_state.lista_alumnos}, timeout=15)
            st.success("Enviado correctamente a Google Sheets.")
            st.session_state.lista_alumnos = []
        except Exception as e:
            st.error(f"Error al enviar: {e}")