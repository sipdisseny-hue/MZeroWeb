import base64
import sqlite3
from io import StringIO
import pandas as pd
import requests
import streamlit as st

# CONFIGURACIÓN
st.set_page_config(page_title="MZero Web", layout="wide")

# --- DICCIONARIO DE TRADUCCIONES (IDIOMAS) ---
TEXTOS = {
    "es": {
        "nav_titulo": "Navegación",
        "menu_docs": "Documentos",
        "menu_eval": "Evaluaciones",
        "sesion_iniciada": "Sesión iniciada:",
        "cerrar_sesion": "CERRAR SESIÓN",
        "usuario": "Usuario:",
        "password": "Contraseña:",
        "btn_acceder": "Acceder",
        "error_login": "Usuario o contraseña incorrectos",
        "error_cred": "Error al conectar con la hoja Credenciales",
        "area_docs": "Área de Documentación y Consultas",
        "asoc_colab": "Asociados y Colaboradores",
        "asociados": "Asociados",
        "colaboradores": "Colaboradores",
        "funcionalidad": "Funcionalidad",
        "contacto": "Contacto",
        "como_participar": "Cómo participar",
        "eslogan": "Conectando talento, transformando la industria",
        "aviso_login_eval": "Debes iniciar sesión en el sidebar para acceder al módulo de evaluaciones.",
        "profesor": "Profesor",
        "curso": "Curso",
        "modulo": "Módulo",
        "nivel_bloque": "Nivel del Bloque",
        "alumno": "Nombre del Alumno",
        "subt_puntuacion": "Puntuación (1=Insuficiente, 3=Suficiente, 5=Excelente)",
        "que_se_mide": "¿Qué se mide aquí?",
        "nivel_rubrica": "Nivel de Rúbrica:",
        "nota_final": "NOTA FINAL",
        "guardar_alumno": "GUARDAR ALUMNO",
        "resumen_alumnos": "Resumen de Alumnos",
        "gestionar_alumnos": "Gestionar alumnos (Eliminar)",
        "enviar_sheets": "ENVIAR TODO A GOOGLE SHEETS",
        "exito_envio": "Enviado con éxito a Google Sheets",
        "modo_edicion": "--- MODO EDICIÓN ---",
        "titulos_func": ["Argumentos M-Zero", "¿Por qué ser Asociado o Colaborador?", "Metodología M0", "El sello M-Zero 'Certificación de calidad'"]
    },
    "ca": {
        "nav_titulo": "Navegació",
        "menu_docs": "Documents",
        "menu_eval": "Avaluacions",
        "sesion_iniciada": "Sessió iniciada:",
        "cerrar_sesion": "TANCAR SESSIÓ",
        "usuario": "Usuari:",
        "password": "Contrasenya:",
        "btn_acceder": "Accedir",
        "error_login": "Usuari o contrasenya incorrectes",
        "error_cred": "En connectar amb el full Credencials",
        "area_docs": "Àrea de Documentació i Consultes",
        "asoc_colab": "Associats i Col·laboradors",
        "asociados": "Associats",
        "colaboradores": "Col·laboradors",
        "funcionalidad": "Funcionalitat",
        "contacto": "Contacte",
        "como_participar": "Com participar",
        "eslogan": "Connectant talent, transformant la indústria",
        "aviso_login_eval": "Has d'iniciar sessió al sidebar per accedir al mòdul d'avaluacions.",
        "profesor": "Professor",
        "curso": "Curs",
        "modulo": "Mòdul",
        "nivel_bloque": "Nivell del Bloc",
        "alumno": "Nom de l'Alumne",
        "subt_puntuacion": "Puntuació (1=Insuficiente, 3=Suficiente, 5=Excel·lent)",
        "que_se_mide": "Què es mesura aquí?",
        "nivel_rubrica": "Nivell de Rúbrica:",
        "nota_final": "NOTA FINAL",
        "guardar_alumno": "GUARDAR ALUMNE",
        "resumen_alumnos": "Resum d'Alumnes",
        "gestionar_alumnos": "Gestionar alumnes (Eliminar)",
        "enviar_sheets": "ENVIAR TOT A GOOGLE SHEETS",
        "exito_envio": "Enviat amb èxit a Google Sheets",
        "modo_edicion": "--- MODE EDICIÓ ---",
        "titulos_func": ["Arguments M-Zero", "Per què ser Associat o Colaborador?", "Metodologia M0", "El segell M-Zero 'Certificació de qualitat'"]
    }
}

# --- LECTURA DE DATOS Y SINCRONIZACIÓN ---
@st.cache_data(ttl=600)
def cargar_catalogo_cursos_y_modulos():
    url_script = "https://google.com"
    try:
        response = requests.get(url_script, timeout=20)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                return data.get("cursos", []), data.get("modulos", [])
    except Exception as e:
        st.error(f"Error de conexión al cargar cursos y módulos: {e}")
    return [], []

@st.cache_data(ttl=600)
def cargar_datos_de_google():
    url_script = "https://google.com"
    try:
        response = requests.get(url_script, timeout=20)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                resultado = {}
                for item in data:
                    t = item.get("Títul") if item.get("Títul") is not None else item.get("Titulo")
                    c = item.get("Contingut") if item.get("Contingut") is not None else item.get("Contenido")
                    if t is not None:
                        resultado[str(t).strip()] = str(c) if c is not None else ""
                return resultado
        return {}
    except Exception as e:
        st.error(f"Error de lectura: {e}")
        return {}

def refrescar_app():
    st.cache_data.clear()
    nuevos_datos = cargar_datos_de_google()
    es_catalan = any(k in nuevos_datos for k in ["Arguments M-Zero", "Per què ser Associat o Colaborador?"])
    
    if es_catalan:
        st.session_state.texto_documentos = nuevos_datos.get("Informació del sistema", "Benvingut a l'àrea de consulta.")
        claves_funcionalidad = ["Arguments M-Zero", "Per què ser Associat o Colaborador?", "Metodologia M0", "El segell M-Zero 'Certificació de qualitat'"]
    else:
        st.session_state.texto_documentos = nuevos_datos.get("Información del sistema", "Bienvenido al área de consulta.")
        claves_funcionalidad = ["Argumentos M-Zero", "¿Por qué ser Asociado o Colaborador?", "Metodología M0", "El sello M-Zero 'Certificación de calidad'"]

    st.session_state.contenido_funcionalidad = {key: nuevos_datos.get(key, "") for key in claves_funcionalidad}
    st.session_state.contenido_exp = {key: nuevos_datos.get(key, "") for key in ["Mecanizado", "Climatización", "Fontanería", "Electricidad", "Obra", "Electromecánica", "Hidráulica", "Construcción Mecánica", "Asociaciones y Gremios"]}
    st.session_state.contenido_contacto = {key: nuevos_datos.get(key, "") for key in ["Móvil / WhatsApp", "Email"]}
    st.rerun()

# --- INICIALIZACIÓN DE ESTADOS ---
datos_iniciales = cargar_datos_de_google()
cursos_db, modulos_db = cargar_catalogo_cursos_y_modulos()

if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'lista_alumnos' not in st.session_state: st.session_state.lista_alumnos = []
if 'alumno_key' not in st.session_state: st.session_state.alumno_key = 0
if 'reset_todo' not in st.session_state: st.session_state.reset_todo = 0
if 'usuario_actual' not in st.session_state: st.session_state.usuario_actual = ""
if 'idioma' not in st.session_state: st.session_state.idioma = "es"

if 'texto_documentos' not in st.session_state: 
    st.session_state.texto_documentos = datos_iniciales.get("Información del sistema", "Bienvenido al área de consulta.")

if 'contenido_funcionalidad' not in st.session_state:
    st.session_state.contenido_funcionalidad = {key: datos_iniciales.get(key, "") for key in ["Argumentos M-Zero", "¿Por qué ser Asociado o Colaborador?", "Metodología M0", "El sello M-Zero 'Certificación de calidad'", "Arguments M-Zero", "Per què ser Associat o Colaborador?", "Metodologia M0", "El segell M-Zero 'Certificació de qualitat'"]}

# --- CONFIGURACIÓN DE NAVEGACIÓN ---
idioma_seleccionado = st.sidebar.selectbox("Idioma / Idioma", ["es", "ca"], index=0)
st.session_state.idioma = idioma_seleccionado
t = TEXTOS[st.session_state.idioma]

opcion_menu = st.sidebar.radio(t["nav_titulo"], [t["menu_docs"], t["menu_eval"]])

# --- SECCIÓN: EVALUACIONES CORREGIDA CON FORMULARIO ---
if opcion_menu == t["menu_eval"]:
    st.title(t["menu_eval"])
    
    # Validación de sesión según el diccionario de idiomas
    if 'autenticado' in st.session_state and not st.session_state.autenticado:
        st.warning(t["aviso_login_eval"])
    else:
        # El formulario congela los clics del 1 al 5 y evita las micro-recargas molestas
        with st.form(key="formulario_evaluacion_bloque"):
            st.subheader(t["alumno"])
            nombre_alumno = st.text_input("Nombre completo", key="input_alumno_nombre")
            
            col1, col2 = st.columns(2)
            with col1:
                curso_sel = st.selectbox(t["curso"], cursos_db if cursos_db else ["---"])
            with col2:
                modulo_sel = st.selectbox(t["modulo"], modulos_db if modulos_db else ["---"])
                
            st.markdown(f"### {t['subt_puntuacion']}")
            st.markdown(f"**{t['que_se_mide']}**")
            
            # Criterios con botones de opción horizontales
            crit1 = st.radio("Criterio A: Conocimientos y Aplicación", [1, 2, 3, 4, 5], index=2, horizontal=True)
            crit2 = st.radio("Criterio B: Habilidades Técnicas", [1, 2, 3, 4, 5], index=2, horizontal=True)
            crit3 = st.radio("Criterio C: Actitud y Autonomía", [1, 2, 3, 4, 5], index=2, horizontal=True)
            
            # Botón único que procesa el envío del alumno
            boton_guardar = st.form_submit_button(label=t["guardar_alumno"])
            
            if boton_guardar:
                if not nombre_alumno.strip():
                    st.error("Por favor, introduce el nombre del alumno antes de guardar.")
                else:
                    # Cálculo de la nota de la rúbrica al enviar
                    nota_final = (crit1 + crit2 + crit3) / 3
                    
                    nuevo_registro = {
