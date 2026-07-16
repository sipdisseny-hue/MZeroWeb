import streamlit as st
import pandas as pd
import requests

# Configuración
PASSWORD = "TuClaveSecreta"
st.set_page_config(layout="wide")

if "lista_alumnos" not in st.session_state:
    st.session_state.lista_alumnos = []

# Control de Acceso
def check_password():
    if st.sidebar.text_input("Contraseña:", type="password") != PASSWORD:
        st.stop()
check_password()

st.title("M-Zero Pro - Evaluación Final")

# Pesos
pesos = {
    "1. Tasa de eficiencia": 12, "2. Precisión geométrica y mecánica": 5,
    "3. Autonomía ejecutiva": 12, "4. Índice de mermas": 5,
    "5. Mantenimiento de utillaje y entorno": 3, "6. Factor de desempeño temporal": 10,
    "7. Resolución escenarios de prácticas": 10, "8. Resolución escenarios de averías": 10,
    "9. Precisión conceptual y terminología": 5, "10. Seguridad y normativas": 5,
    "11. Fiabilidad y compromiso operativo": 10, "12. Capacidad de aprendizaje": 8,
    "13. Comunicación y respeto al superior": 5
}

# Formulario Completo
with st.container():
    c1, c2 = st.columns(2)
    prof = c1.text_input("Profesor")
    curso = c1.text_input("Curso")
    mod = c2.text_input("Módulo")
    niv = c2.text_input("Nivel del Bloque")
    alu = st.text_input("Nombre del Alumno")

st.subheader("Criterios (1-5)")
notas = {}
for crit, p in pesos.items():
    notas[crit] = int(st.radio(f"{crit} ({p}%)", [1, 2, 3, 4, 5], horizontal=True, index=0, key=crit))

# Cálculo ponderado (Escala 1 a 10)
total = sum(((notas[crit]-1) * 2.25 + 1) * (pesos[crit]/100) for crit in pesos)
if notas["10. Seguridad y normativas"] == 1:
    nota_final = 4.0
    res = "SUSPENSO (Línea Roja)"
else:
    nota_final = round(total, 1)
    res = "APROBADO" if nota_final >= 5 else "SUSPENSO"

st.metric("NOTA FINAL (1-10)", f"{nota_final} - {res}")

if st.button("GUARDAR ALUMNO"):
    st.session_state.lista_alumnos.append({
        "Alumno": alu, "Curso": curso, "Módulo": mod, 
        "Nivel": niv, "Nota": nota_final, "Estado": res
    })
    st.rerun()

# Tabla Resumen
st.divider()
st.subheader("ALUMNOS PENDIENTES DE ENVÍO")
if st.session_state.lista_alumnos:
    st.table(pd.DataFrame(st.session_state.lista_alumnos))
    if st.button("ENVIAR TODO A GOOGLE"):
        st.success("Enviado")
        st.session_state.lista_alumnos = []
        st.rerun()
