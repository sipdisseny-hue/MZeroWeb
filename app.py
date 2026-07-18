import streamlit as st
import pandas as pd
import requests

# CONFIGURACIÓN
ID_DE_SHEET = "1kowfDSzZw_fpIO8tbrKGWxREONDIv2EFFhOtfgn-cKs"
st.set_page_config(page_title="MZero Web", layout="wide")
# --- LECTURA DE DATOS DESDE GOOGLE ---
@st.cache_data(ttl=3600)
def cargar_datos_iniciales():
    url = f"https://docs.google.com/spreadsheets/d/{ID_DE_SHEET}/gviz/tq?tqx=out:csv&sheet=Textos"
    try:
        df = pd.read_csv(url)
        return dict(zip(df['Titulo'], df['Contenido']))
    except:
        return {}

# Pre-cargamos los datos
datos_guardados = cargar_datos_iniciales()

# --- INICIALIZACIÓN DE ESTADOS ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'lista_alumnos' not in st.session_state: st.session_state.lista_alumnos = []
if 'alumno_key' not in st.session_state: st.session_state.alumno_key = 0
if 'reset_todo' not in st.session_state: st.session_state.reset_todo = 0
if 'texto_documentos' not in st.session_state: st.session_state.texto_documentos = "Bienvenido al área de consulta."
if 'usuario_actual' not in st.session_state: st.session_state.usuario_actual = ""

# --- INICIALIZACIÓN DE CONTENIDOS ---
if 'contenido_exp' not in st.session_state:
    st.session_state.contenido_exp = {
        "Mecanizado": datos_guardados.get("Mecanizado", ""),
        "Climatización": datos_guardados.get("Climatización", ""),
        "Fontanería": datos_guardados.get("Fontanería", ""),
        "Electricidad": datos_guardados.get("Electricidad", ""),
        "Obra": datos_guardados.get("Obra", ""),
        "Electromecánica": datos_guardados.get("Electromecánica", ""),
        "Hidráulica": datos_guardados.get("Hidráulica", ""),
        "Construcción Mecánica": datos_guardados.get("Construcción Mecánica", ""),
        "Asociaciones y Gremios": datos_guardados.get("Asociaciones y Gremios", "")
    }

if 'contenido_funcionalidad' not in st.session_state:
    st.session_state.contenido_funcionalidad = {
        "Argumentos M-Zero": datos_guardados.get("Argumentos M-Zero", ""),
        "¿Por qué ser Asociado o Colaborador?": datos_guardados.get("¿Por qué ser Asociado o Colaborador?", ""),
        "Metodología M0": datos_guardados.get("Metodología M0", ""),
        "El sello M-Zero": datos_guardados.get("El sello M-Zero", "")
    }

if 'contenido_contacto' not in st.session_state:
    st.session_state.contenido_contacto = {
        "Móvil / WhatsApp": datos_guardados.get("Móvil / WhatsApp", ""), 
        "Email": datos_guardados.get("Email", "")
    }

if 'contenido_participar' not in st.session_state:
    st.session_state.contenido_participar = {
        "Información del sistema": datos_guardados.get("Información del sistema", "")
    }

# --- FUNCIÓN PARA GUARDAR DATOS EN GOOGLE SHEETS ---
def guardar_en_sheet(titulo, nuevo_contenido):
    import gspread
    from google.oauth2.service_account import Credentials
    
    try:
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
        client = gspread.authorize(creds)
        sheet = client.open_by_key(ID_DE_SHEET).worksheet("Textos")
        cell = sheet.find(titulo)
        if cell:
            sheet.update_cell(cell.row, cell.col + 1, nuevo_contenido)
            st.success(f"Datos de '{titulo}' guardados correctamente.")
        else:
            st.error(f"No se encontró el título '{titulo}' en la hoja de cálculo.")
    except Exception as e:
        st.error(f"Error al guardar: {e}")

# --- FUNCIÓN AUXILIAR PARA CREAR EXPANDERS EDITABLES ---
def mostrar_expander_editable(diccionario, clave, titulo_expander, key_boton):
    with st.expander(titulo_expander):
        if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
            nuevo_texto = st.text_area(f"Editar {titulo_expander}:", value=diccionario[clave], key=f"edit_{key_boton}")
            if st.button(f"Guardar {titulo_expander}", key=f"btn_{key_boton}"):
                diccionario[clave] = nuevo_texto
                guardar_en_sheet(clave, nuevo_texto)
                st.rerun()
        st.markdown(diccionario[clave], unsafe_allow_html=True)

st.header("Gestión de Contenidos")

# 1. Sección Funcionalidad
st.subheader("Funcionalidad M-Zero")
for clave in st.session_state.contenido_funcionalidad:
    mostrar_expander_editable(st.session_state.contenido_funcionalidad, clave, clave, f"func_{clave}")

# 2. Sección Experiencia
st.subheader("Experiencia")
for clave in st.session_state.contenido_exp:
    mostrar_expander_editable(st.session_state.contenido_exp, clave, clave, f"exp_{clave}")

# 3. Sección Contacto
st.subheader("Contacto")
for clave in st.session_state.contenido_contacto:
    mostrar_expander_editable(st.session_state.contenido_contacto, clave, clave, f"cont_{clave}")

# 4. Sección Participar
st.subheader("Participar")
for clave in st.session_state.contenido_participar:
    mostrar_expander_editable(st.session_state.contenido_participar, clave, clave, f"part_{clave}")
