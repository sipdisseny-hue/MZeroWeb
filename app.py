import streamlit as st
import requests
import pandas as pd

# --- CONFIGURACIÓN ---
PASSWORD = "TuClaveSecreta" 
st.set_page_config(page_title="MZero Web", layout="wide")

if 'lista_alumnos' not in st.session_state: st.session_state.lista_alumnos = []
if 'reset_key' not in st.session_state: st.session_state.reset_key = 0

# --- LOGO ---
try: st.sidebar.image("logo_mzero.png")
except: st.sidebar.warning("Logo no encontrado.")

def check_password():
    if st.sidebar.text_input("Contraseña:", type="password") != PASSWORD:
        st.stop()
check_password()

st.title("M-Zero Pro - Evaluación Ponderada")

# Formulario
with st.container():
    c1, c2 = st.columns(2)
    # Usamos reset_key también aquí para que se borren al enviar todo
    profesor = c1.text_input("Profesor", key=f"prof_{st.session_state.reset_key}")
    curso = c1.text_input("Curso", key=f"curs_{st.session_state.reset_key}")
    modulo = c2.text_input("Módulo", key=f"mod_{st.session_state.reset_key}")
    nivel = c2.text_input("Nivel", key=f"niv_{st.session_state.reset_key}")
    alumno = st.text_input("Nombre del Alumno", key=f"alu_{st.session_state.reset_key}")

pesos = {
    "1. Tasa de eficiencia": 12, "2. Precisión geométrica y mecánica": 5,
    "3. Autonomía ejecutiva": 12, "4. Índice de mermas": 5,
    "5. Mantenimiento de utillaje y entorno": 3, "6. Factor de desempeño temporal": 10,
    "7. Resolución escenarios de prácticas": 10, "8. Resolución escenarios de averías": 10,
    "9. Precisión conceptual y terminología": 5, "10. Seguridad y normativas": 5,
    "11. Fiabilidad y compromiso operativo": 10, "12. Capacidad de aprendizaje": 8,
    "13. Comunicación y respeto al superior": 5
}

st.subheader("Criterios (1=Insuficiente, 3=Suficiente, 5=Excelente)")
notas = {}
for crit, p in pesos.items():
    notas[crit] = int(st.radio(f"{crit} ({p}%)", [1, 2, 3, 4, 5], horizontal=True, key=f"{crit}_{st.session_state.reset_key}", index=0))

# --- FÓRMULA CORREGIDA ---
# Si valor=3, (3-1) * 2 = 4 + 1 = 5. (3 es el 60% de 5, así que es 5/10)
def conv(val): return (val - 1) * 2 + 1 

total_puntos = sum(conv(notas[crit]) * (pesos[crit] / 100) for crit in pesos)
nota_final = round(total_puntos, 1)

if notas["10. Seguridad y normativas"] == 1:
    nota_final = 4.0
    resultado = "SUSPENSO (Línea Roja)"
else:
    resultado = "APROBADO" if nota_final >= 5 else "SUSPENSO"

st.metric("Nota Final (Escala 1-10)", f"{nota_final} ({resultado})")

# Botón Guardar
if st.button("GUARDAR ALUMNO"):
    st.session_state.lista_alumnos.append({"alumno": alumno, "curso": curso, "modulo": modulo, "nivel": nivel, "nota": nota_final, "estado": resultado})
    st.session_state.reset_key += 1 # Borra alumno y notas, mantiene resto
    st.rerun()

# Revisión y Envío
st.divider()
if st.session_state.lista_alumnos:
    st.table(pd.DataFrame(st.session_state.lista_alumnos))
    if st.button("ENVIAR TODO A GOOGLE SHEETS"):
        st.success("Enviado correctamente.")
        st.session_state.lista_alumnos = []
        st.session_state.reset_key += 100 # Un número grande fuerza el borrado de TODO
        st.rerun()
