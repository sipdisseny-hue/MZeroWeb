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

# Formulario (KEYS FIJAS para que no se borren al guardar)
with st.container():
    c1, c2 = st.columns(2)
    profesor = c1.text_input("Profesor", key="f_prof")
    curso = c1.text_input("Curso", key="f_cur")
    modulo = c2.text_input("Módulo", key="f_mod")
    nivel = c2.text_input("Nivel", key="f_niv")
    alumno = st.text_input("Nombre del Alumno", key="f_alu")

pesos = {
    "1. Tasa de eficiencia": 12, "2. Precisión geométrica": 5, "3. Autonomía": 12, 
    "4. Índice de mermas": 5, "5. Mantenimiento": 3, "6. Desempeño temporal": 10,
    "7. Escenarios prácticas": 10, "8. Escenarios averías": 10, "9. Precisión conceptual": 5, 
    "10. Seguridad": 5, "11. Fiabilidad": 10, "12. Aprendizaje": 8, "13. Comunicación": 5
}

st.subheader("Puntuación (1=Insuficiente, 3=Suficiente, 5=Excelente)")
notas = {}
for crit, p in pesos.items():
    notas[crit] = int(st.radio(f"{crit} ({p}%)", [1, 2, 3, 4, 5], horizontal=True, key=f"rad_{crit}", index=2)) # index 2 es el '3'

# --- FÓRMULA DE PONDERACIÓN ---
# Convertimos 1-5 a escala de 0-10, donde 3 equivale a 5.0
def calcular_nota(dict_notas):
    total = 0
    for crit, val in dict_notas.items():
        # Valor convertido: 1->0, 3->5, 5->10
        valor_escala = (val - 1) * 2.5 
        total += valor_escala * (pesos[crit] / 100)
    return round(total, 1)

nota_final = calcular_nota(notas)
if notas["10. Seguridad y normativas"] == 1:
    nota_final, resultado = 4.0, "SUSPENSO (Línea Roja)"
else:
    resultado = "APROBADO" if nota_final >= 5 else "SUSPENSO"

st.metric("NOTA FINAL", f"{nota_final} - {resultado}")

# Botón Guardar
if st.button("GUARDAR ALUMNO"):
    st.session_state.lista_alumnos.append({"Alumno": alumno, "Nota": nota_final, "Estado": resultado})
    # Resetear solo nombre alumno y notas
    st.text_input("Nombre del Alumno", value="", key="f_alu_clear") # Truco para limpiar
    st.rerun()

# Tabla y Borrado Total
st.divider()
if st.session_state.lista_alumnos:
    st.table(pd.DataFrame(st.session_state.lista_alumnos))
    if st.button("ENVIAR TODO Y BORRAR SESIÓN"):
        st.session_state.lista_alumnos = []
        st.rerun() # Al recargar sin nada en la lista, se limpia la tabla
