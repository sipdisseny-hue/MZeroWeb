import streamlit as st
import pandas as pd
import requests
from io import StringIO

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
        "candidatos": "Candidatos",
        "escribir_peticion": "Escribe tu petición:",
        "enviar": "Enviar",
        "peticion_enviada": "Petición enviada correctamente.",
        "error_peticion": "No se pudo enviar la petición. Inténtalo de nuevo.",
        "campo_vacio_peticion": "Escribe algo antes de enviar.",
        "acceso_concedido": "Acceso concedido:",
        "error_acceso_participar": "Usuario o contraseña incorrectos, o no estás inscrito.",
        "solicitar_alta": "¿Todavía no estás dado de alta? Solicita el registro",
        "enviar_solicitud": "Enviar solicitud",
        "solicitud_enviada": "Solicitud enviada correctamente.",
        "error_solicitud": "No se pudo enviar la solicitud. Inténtalo de nuevo.",
        "campo_vacio_empresa": "Escribe al menos el nombre de la empresa.",
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
        "subt_puntuacion": "Puntuació (1=Insuficient, 3=Suficient, 5=Excel·lent)",
        "que_se_mide": "Què es mesura aquí?",
        "nivel_rubrica": "Nivell de Rúbrica:",
        "nota_final": "NOTA FINAL",
        "guardar_alumno": "GUARDAR ALUMNE",
        "resumen_alumnos": "Resum d'Alumnes",
        "gestionar_alumnos": "Gestionar alumnes (Eliminar)",
        "enviar_sheets": "ENVIAR TOT A GOOGLE SHEETS",
        "exito_envio": "Enviat amb èxit a Google Sheets",
        "modo_edicion": "--- MODE EDICIÓ ---",
        "candidatos": "Candidats",
        "escribir_peticion": "Escriu la teva petició:",
        "enviar": "Enviar",
        "peticion_enviada": "Petició enviada correctament.",
        "error_peticion": "No s'ha pogut enviar la petició. Torna-ho a provar.",
        "campo_vacio_peticion": "Escriu alguna cosa abans d'enviar.",
        "acceso_concedido": "Accés concedit:",
        "error_acceso_participar": "Usuari o contrasenya incorrectes, o no estàs inscrit.",
        "solicitar_alta": "Encara no estàs donat d'alta? Sol·licita el registre",
        "enviar_solicitud": "Enviar sol·licitud",
        "solicitud_enviada": "Sol·licitud enviada correctament.",
        "error_solicitud": "No s'ha pogut enviar la sol·licitud. Torna-ho a provar.",
        "campo_vacio_empresa": "Escriu com a mínim el nom de l'empresa.",
        "titulos_func": ["Arguments M-Zero", "Per què ser Associat o Colaborador?", "Metodologia M0", "El segell M-Zero 'Certificació de qualitat'"]
    }
}

# --- LECTURA DE DATOS Y SINCRONIZACIÓN ---
@st.cache_data(ttl=600)
def cargar_catalogo_cursos_y_modulos():
    url_script = "https://script.google.com/macros/s/AKfycbzAfnmO33bANwUsvDRkeMzLjLgLWZeSdzLNduleZ9UYDLEtIqe4YIb-gHSWmJaaFBYY/exec"
    try:
        response = requests.get(url_script, timeout=20)
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict):
                    return data.get("cursos", []), data.get("modulos", [])
            except Exception:
                st.error(f"El script no devolvió un JSON válido. Respuesta recibida: {response.text[:200]}")
    except Exception as e:
        st.error(f"Error de conexión al cargar cursos y módulos: {e}")
    return [], []

@st.cache_data(ttl=600)
def cargar_datos_de_google():
    url_script = "https://script.google.com/macros/s/AKfycbzZDkU6ZfAK1tdy502iEVlQ3j42GWlVBh5DW1_XCD1BxpEI0NZ7Pss3MV0BMGYDikwR/exec"
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

# --- NUEVO: ASOCIADOS Y COLABORADORES (Provincia -> Población -> Empresa) ---
# Lee las pestañas "Asociados" y "Colaboradores" del Excel a través del Apps
# Script de Code_AsociadosColaboradores.gs. Cada fila debe traer:
# provincia, poblacion, empresa, descripcion, enlace.
@st.cache_data(ttl=600)
def cargar_asociados_colaboradores():
    url_script = "https://script.google.com/macros/s/AKfycbyD03Ix8JF6jx8wbiu8_imQoNXDwYVGhjEvMlXTV5NaeC5fWZ-0ysRRssmlfv5YCb95tg/exec"
    try:
        response = requests.get(url_script, timeout=20)
        if response.status_code == 200:
            data = response.json()
            return data.get("asociados", []), data.get("colaboradores", [])
    except Exception as e:
        st.error(f"Error al cargar Asociados y Colaboradores: {e}")
    return [], []

# --- NUEVO: TEXTOS DE "CÓMO PARTICIPAR" (Asociados / Colaboradores / Candidato) ---
# Usa la MISMA URL que ya usan cargar_datos_de_google() y guardar_en_sheets()
# (el script de "Textos M-Zero"), simplemente con el parámetro ?tipo=participar
# para activar la rama nueva de ese mismo doGet.
@st.cache_data(ttl=600)
def cargar_instrucciones_participar():
    url_script = "https://script.google.com/macros/s/AKfycbzZDkU6ZfAK1tdy502iEVlQ3j42GWlVBh5DW1_XCD1BxpEI0NZ7Pss3MV0BMGYDikwR/exec"
    try:
        response = requests.get(url_script, params={"tipo": "participar"}, timeout=20)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error al cargar instrucciones de participación: {e}")
    return {}

# --- NUEVO: LOGIN INDEPENDIENTE DE ASOCIADO / COLABORADOR ---
# Reutiliza la misma técnica que ya usa el login general (CSV público de
# Google Sheets), pero apuntando a "Credenciales Asociados" o
# "Credenciales Colaboradores" en vez de a "Credenciales". Solo puede
# acceder quien tú hayas dado de alta manualmente en esas hojas.
def verificar_credencial_participar(usuario, contrasena, nombre_hoja):
    url = "https://docs.google.com/spreadsheets/d/1kowfDSzZw_fpIO8tbrKGWxREONDIv2EFFhOtfgn-cKs/gviz/tq"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, params={"tqx": "out:csv", "sheet": nombre_hoja}, headers=headers, timeout=10)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            df.columns = [str(c).strip() for c in df.columns]
            for _, fila in df.iterrows():
                u_hoja = str(fila.get("Usuario", "")).strip()
                p_hoja = str(fila.get("Contraseña", "")).strip()
                if u_hoja == usuario.strip() and p_hoja == contrasena.strip():
                    return fila.to_dict()
    except Exception:
        pass
    return None

# --- NUEVO: ENVÍO DE PETICIÓN (Asociado o Colaborador) ---
def enviar_peticion_participar(tipo, id_empresa, texto):
    # Misma URL que ya usa el envío de Evaluaciones — es el mismo script
    # (Code_HojaCalculoMZero_fusionado.gs), que ahora también sabe manejar
    # peticiones de Asociado/Colaborador gracias al campo "tipo".
    url_script = "https://script.google.com/macros/s/AKfycbw1PNXaXT23jXJdKPOO9vbwrx6tnBI-hvlJrJFMNKZiy7G1JsNkTY-C6Ql7Wym_l-GG-Q/exec"
    payload = {"tipo": tipo, "id_empresa": id_empresa, "texto": texto}
    try:
        response = requests.post(url_script, json=payload, timeout=20)
        return response.status_code == 200
    except Exception:
        return False

# --- NUEVO: PETICIÓN DE REGISTRO (alta de nuevo Asociado o Colaborador) ---
# Usa la MISMA URL que ya usa cargar_asociados_colaboradores() (el script de
# "Asociados y Colaboradores"), con accion="registro" para distinguirlo de
# las peticiones normales de datos (doGet).
def enviar_peticion_registro(tipo, campos):
    url_script = "https://script.google.com/macros/s/AKfycbyD03Ix8JF6jx8wbiu8_imQoNXDwYVGhjEvMlXTV5NaeC5fWZ-0ysRRssmlfv5YCb95tg/exec"
    payload = {"accion": "registro", "tipo": tipo, "campos": campos}
    try:
        response = requests.post(url_script, json=payload, timeout=20)
        return response.status_code == 200
    except Exception:
        return False

# --- NUEVO: RÚBRICA CACHEADA ---
# Antes esta petición se hacía en CADA rerun (es decir, en cada clic de puntuación
# dentro del módulo de Evaluaciones), lo que causaba la sensación de "envío" y la
# espera al puntuar. Al envolverla en @st.cache_data, solo se pide una vez cada
# ttl segundos (aquí 3600 = 1 hora); los siguientes clics usan el valor en caché
# y son instantáneos. Ajusta el ttl a tu gusto (ver conversación: 60=1min,
# 1800=30min, 3600=1h, 86400=1día, o quita el ttl para que no caduque nunca).
@st.cache_data(ttl=3600)
def cargar_rubrica():
    descripciones_rubrica = {}
    try:
        url_apps_script = "https://script.google.com/macros/s/AKfycbxdVRFxWRPb_F5y7yL9SvlA3OAPseJ0bG-pn7jAk9PYVZ8sXqNcVLlvBFVmun48mD1R7g/exec"
        resp_rubrica = requests.get(url_apps_script, timeout=10)
        if resp_rubrica.status_code == 200:
            data_json = resp_rubrica.json()
            for item in data_json:
                descripciones_rubrica[item["criterio"].strip()] = {
                    "que_se_mide": item["que_se_mide"],
                    "nivel_rubrica": item["nivel_rubrica"]
                }
    except Exception:
        pass
    return descripciones_rubrica

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

if 'texto_documentos' not in st.session_state: 
    st.session_state.texto_documentos = datos_iniciales.get("Información del sistema", "Bienvenido al área de consulta.")

if 'contenido_funcionalidad' not in st.session_state:
    st.session_state.contenido_funcionalidad = {key: datos_iniciales.get(key, "") for key in ["Argumentos M-Zero", "¿Por qué ser Asociado o Colaborador?", "Metodología M0", "El sello M-Zero 'Certificación de calidad'", "Arguments M-Zero", "Per què ser Associat o Colaborador?", "Metodologia M0", "El segell M-Zero 'Certificació de qualitat'"]}

if 'contenido_exp' not in st.session_state:
    st.session_state.contenido_exp = {key: datos_iniciales.get(key, "") for key in ["Mecanizado", "Climatización", "Fontanería", "Electricidad", "Obra", "Electromecánica", "Hidráulica", "Construcción Mecánica", "Asociaciones y Gremios"]}

if 'contenido_contacto' not in st.session_state:
    st.session_state.contenido_contacto = {key: datos_iniciales.get(key, "") for key in ["Móvil / WhatsApp", "Email"]}

# --- FUNCIÓN GUARDAR ---
def guardar_en_sheets(titulo, nuevo_contenido):
    url_script = "https://script.google.com/macros/s/AKfycbzZDkU6ZfAK1tdy502iEVlQ3j42GWlVBh5DW1_XCD1BxpEI0NZ7Pss3MV0BMGYDikwR/exec"
    payload = {"titulo": titulo, "contenido": nuevo_contenido}
    try:
        response = requests.post(url_script, json=payload, timeout=20)
        return response.status_code == 200
    except:
        return False

# --- SIDEBAR: NAVEGACIÓN, IDIOMA Y ACCESO ---
with st.sidebar:
    st.image("logo_mzero.png")
    st.markdown("## M-Zero Pro")
    
    idioma_seleccionado = st.radio("Idioma", ["Castellano", "Català"], horizontal=True, label_visibility="collapsed")
    lang = "ca" if idioma_seleccionado == "Català" else "es"
    T = TEXTOS[lang]
    
    opcion = st.radio(T["nav_titulo"], [T["menu_docs"], T["menu_eval"]])
    
    st.divider()
    
    if st.session_state.autenticado:
        st.success(f"{T['sesion_iniciada']} {st.session_state.usuario_actual}")
        if st.button(T["cerrar_sesion"]):
            st.session_state.autenticado = False
            st.session_state.usuario_actual = ""
            st.rerun()
    else:
        usuario_in = st.text_input(T["usuario"])
        pass_in = st.text_input(T["password"], type="password")
        
        if st.button(T["btn_acceder"]):
            url = "https://docs.google.com/spreadsheets/d/1kowfDSzZw_fpIO8tbrKGWxREONDIv2EFFhOtfgn-cKs/gviz/tq?tqx=out:csv&sheet=Credenciales"
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    df = pd.read_csv(StringIO(response.text), header=None)
                    
                    login_ok = False
                    for i in range(1, len(df)):
                        u_excel = str(df.iloc[i, 0]).strip()
                        p_excel = str(df.iloc[i, 1]).strip()
                        if u_excel == usuario_in.strip() and p_excel == pass_in.strip():
                            login_ok = True
                            break
                            
                    if login_ok:
                        st.session_state.autenticado = True
                        st.session_state.usuario_actual = usuario_in.strip()
                        st.rerun()
                    else:
                        st.error(T["error_login"])
                else:
                    st.error(T["error_cred"])
            except Exception as e:
                st.error(f"Error de acceso: {e}")

# --- LÓGICA DE PANTALLAS ---
if opcion == T["menu_docs"]:
    st.markdown(f"## {T['area_docs']}")
    
    with st.container(border=True):
        st.markdown(f"<h3 style='color: #0066cc;'><b>{T['asoc_colab']}</b></h3>", unsafe_allow_html=True)
        st.image("Asociados y colaboradores.png", width=300)

        asociados_db, colaboradores_db = cargar_asociados_colaboradores()

        def mostrar_provincia_poblacion_empresa(datos_categoria, key_prefix):
            """Desplegable en cascada Provincia -> Población -> Empresa,
            ya filtrado de antemano por la categoría que lo llama."""
            if not datos_categoria:
                st.info("Todavía no hay datos cargados para esta categoría.")
                return

            provincias = sorted({
                d.get("provincia", "").strip() for d in datos_categoria if d.get("provincia", "").strip()
            })
            if not provincias:
                st.info("No hay provincias registradas todavía para esta categoría.")
                return

            provincia_sel = st.selectbox("Provincia", provincias, key=f"{key_prefix}_prov")

            poblaciones = sorted({
                d.get("poblacion", "").strip() for d in datos_categoria
                if d.get("provincia", "").strip() == provincia_sel and d.get("poblacion", "").strip()
            })
            if not poblaciones:
                st.info("No hay poblaciones registradas para esta provincia.")
                return

            poblacion_sel = st.selectbox("Población", poblaciones, key=f"{key_prefix}_pob")

            empresas = [
                d for d in datos_categoria
                if d.get("provincia", "").strip() == provincia_sel
                and d.get("poblacion", "").strip() == poblacion_sel
            ]
            if not empresas:
                st.info("No hay empresas registradas en esta población.")
                return

            for emp in empresas:
                nombre = emp.get("empresa", "").strip() or "(Sin nombre)"
                with st.expander(nombre):
                    logo_url = emp.get("logo", "").strip()
                    if logo_url:
                        st.image(logo_url, width=150)

                    empresa_html = emp.get("empresa_html", "").strip()
                    if empresa_html:
                        st.markdown(f"#### {empresa_html}", unsafe_allow_html=True)

                    descripcion = emp.get("descripcion", "").strip()
                    if descripcion:
                        st.markdown(descripcion, unsafe_allow_html=True)
                    enlace = emp.get("enlace", "").strip()
                    if enlace:
                        st.markdown(f"🔗 [Visitar web]({enlace})")

        def mostrar_bloque_categorias(datos, titulos_por_columna, key_prefix):
            """Pinta los títulos de categoría en columnas (como antes) y,
            al desplegar cada uno, muestra el buscador Provincia/Población/Empresa
            filtrado a esa categoría."""
            columnas = st.columns(len(titulos_por_columna))
            for i, col in enumerate(columnas):
                with col:
                    for titulo in titulos_por_columna[i]:
                        with st.expander(titulo):
                            datos_categoria = [
                                d for d in datos
                                if d.get("categoria", "").strip().lower() == titulo.strip().lower()
                            ]
                            mostrar_provincia_poblacion_empresa(datos_categoria, f"{key_prefix}_{titulo}")

        # --- BLOQUE 1: ASOCIADOS ---
        st.markdown(f"<h4 style='color: #0066cc; margin-top: 20px;'>{T['asociados']}</h4>", unsafe_allow_html=True)

        titulos_asociados = [
            ["Mecanizado", "Climatización", "Fontanería", "Empresas de trabajo temporal"],
            ["Electricidad", "Obra", "Electromecánica", "Renovables"],
            ["Hidráulica", "Construcción Mecánica", "Asociaciones y Gremios"]
        ]

        mostrar_bloque_categorias(asociados_db, titulos_asociados, "asoc")

        st.divider()

        # --- BLOQUE 2: COLABORADORES ---
        st.markdown(f"<h4 style='color: #0066cc;'>{T['colaboradores']}</h4>", unsafe_allow_html=True)

        titulos_colaboradores = [
            ["Centros de formación"],
            ["Gremios"],
            ["Asociaciones"]
        ]

        mostrar_bloque_categorias(colaboradores_db, titulos_colaboradores, "colab")

    # --- BLOQUE 2: FUNCIONALIDAD ---
    if 'contenido_funcionalidad' not in st.session_state or not st.session_state.contenido_funcionalidad:
        st.session_state.contenido_funcionalidad = cargar_datos_de_google()

    st.markdown(f"<h3 style='color: #0066cc;'><b>{T['funcionalidad']}</b></h3>", unsafe_allow_html=True)
    titulos_func = T["titulos_func"]

    for titulo in titulos_func:
        with st.expander(titulo):
            if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
                temp_text = st.text_area(f"Editar {titulo}:", value=st.session_state.contenido_funcionalidad.get(titulo, ""), height=150, key=f"input_{titulo}")
            
                if st.button(f"Guardar {titulo}", key=f"btn_save_{titulo}"):
                    st.session_state.contenido_funcionalidad[titulo] = temp_text
                
                    if guardar_en_sheets(titulo, temp_text):
                        st.success("Guardado en Google y localmente")
                    else:
                        st.warning("Guardado solo localmente (Error en Sheets)")
                
                    st.rerun()

            st.markdown(st.session_state.contenido_funcionalidad.get(titulo, ""), unsafe_allow_html=True)

    # --- BLOQUE 3: CONTACTO ---
    st.markdown(f"<h3 style='color: #0066cc;'><b>{T['contacto']}</b></h3>", unsafe_allow_html=True)
    titulos_cont = ["Móvil / WhatsApp", "Email"]
    for titulo in titulos_cont:
        with st.expander(titulo):
            if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
                nuevo_cont = st.text_area(f"Editar {titulo}:", value=st.session_state.contenido_contacto.get(titulo, ""), height=70, key=f"cont_{titulo}")
                if st.button(f"Guardar {titulo}", key=f"btn_save_cont_{titulo}"):
                    if guardar_en_sheets(titulo, nuevo_cont):
                        st.session_state.contenido_contacto[titulo] = nuevo_cont
                        refrescar_app()
            st.markdown(st.session_state.contenido_contacto.get(titulo, ""), unsafe_allow_html=True)

    # --- BLOQUE: CÓMO PARTICIPAR ---
    st.markdown(f"## {T['como_participar']}")

    instrucciones_participar = cargar_instrucciones_participar()

    def texto_instruccion(clave):
        bloque = instrucciones_participar.get(clave, {})
        return bloque.get(lang, "")

    def bloque_solicitud_alta(tipo, key_prefix, incluir_centro=False):
        """Formulario para pedir el alta como Asociado o Colaborador nuevo
        (usuario todavía no inscrito en Credenciales Asociados/Colaboradores)."""
        version = st.session_state.get(f"{key_prefix}_reg_version", 0)

        with st.expander(T["solicitar_alta"]):
            nombre_empresa = st.text_input("Nombre Empresa", key=f"{key_prefix}_reg_empresa_{version}")

            nombre_centro = ""
            if incluir_centro:
                nombre_centro = st.text_input("Nombre del Centro", key=f"{key_prefix}_reg_centro_{version}")

            sector = st.text_input("Sector", key=f"{key_prefix}_reg_sector_{version}")

            c1, c2 = st.columns(2)
            provincia = c1.text_input("Provincia", key=f"{key_prefix}_reg_prov_{version}")
            poblacion = c2.text_input("Población", key=f"{key_prefix}_reg_pob_{version}")

            c3, c4 = st.columns(2)
            cp = c3.text_input("CP", key=f"{key_prefix}_reg_cp_{version}")
            razon_social = c4.text_input("Razón Social", key=f"{key_prefix}_reg_razon_{version}")

            c5, c6 = st.columns(2)
            cif_nif = c5.text_input("CIF/NIF", key=f"{key_prefix}_reg_cif_{version}")
            telefono = c6.text_input("Teléfono", key=f"{key_prefix}_reg_tel_{version}")

            c7, c8 = st.columns(2)
            email = c7.text_input("Email", key=f"{key_prefix}_reg_email_{version}")
            nombre_contacto = c8.text_input("Nombre Contacto", key=f"{key_prefix}_reg_contacto_{version}")

            web = st.text_input("Web", key=f"{key_prefix}_reg_web_{version}")

            if st.button(T["enviar_solicitud"], key=f"{key_prefix}_reg_btn_enviar"):
                if nombre_empresa.strip():
                    campos = {
                        "Nombre empresa": nombre_empresa.strip(),
                        "Sector": sector.strip(),
                        "Provincia": provincia.strip(),
                        "Población": poblacion.strip(),
                        "CP": cp.strip(),
                        "Razón Social": razon_social.strip(),
                        "CIF/NIF": cif_nif.strip(),
                        "Telefono": telefono.strip(),
                        "Email": email.strip(),
                        "Nombre Contacto": nombre_contacto.strip(),
                        "Web": web.strip(),
                    }
                    if incluir_centro:
                        campos["Nombre del Centro"] = nombre_centro.strip()

                    if enviar_peticion_registro(tipo, campos):
                        st.success(T["solicitud_enviada"])
                        st.session_state[f"{key_prefix}_reg_version"] = version + 1
                        st.rerun()
                    else:
                        st.error(T["error_solicitud"])
                else:
                    st.warning(T["campo_vacio_empresa"])

    def bloque_acceso_y_peticion(tipo, nombre_hoja_credenciales, key_prefix, incluir_centro_registro=False):
        """Login independiente contra 'Credenciales Asociados' / 'Credenciales
        Colaboradores' + formulario de petición una vez autenticado."""
        login_key = f"{key_prefix}_login_ok"
        id_key = f"{key_prefix}_id_empresa"
        nombre_key = f"{key_prefix}_nombre_empresa"
        peticion_version_key = f"{key_prefix}_peticion_version"

        st.markdown("---")

        if not st.session_state.get(login_key):
            usuario_in = st.text_input(T["usuario"], key=f"{key_prefix}_user_in")
            pass_in = st.text_input(T["password"], type="password", key=f"{key_prefix}_pass_in")
            if st.button(T["btn_acceder"], key=f"{key_prefix}_btn_acceder"):
                fila = verificar_credencial_participar(usuario_in, pass_in, nombre_hoja_credenciales)
                if fila:
                    st.session_state[login_key] = True
                    st.session_state[id_key] = str(fila.get("Id. Empresa", "")).strip()
                    st.session_state[nombre_key] = str(fila.get("Nombre Empresa", "")).strip()
                    st.rerun()
                else:
                    st.error(T["error_acceso_participar"])

            bloque_solicitud_alta(tipo, key_prefix, incluir_centro=incluir_centro_registro)
        else:
            nombre_empresa = st.session_state.get(nombre_key, "")
            st.success(f"{T['acceso_concedido']} {nombre_empresa}")

            version = st.session_state.get(peticion_version_key, 0)
            texto_peticion = st.text_area(
                T["escribir_peticion"], key=f"{key_prefix}_peticion_{version}"
            )
            if st.button(T["enviar"], key=f"{key_prefix}_btn_enviar"):
                if texto_peticion.strip():
                    id_empresa = st.session_state.get(id_key, "")
                    if enviar_peticion_participar(tipo, id_empresa, texto_peticion.strip()):
                        st.success(T["peticion_enviada"])
                        st.session_state[peticion_version_key] = version + 1
                        st.rerun()
                    else:
                        st.error(T["error_peticion"])
                else:
                    st.warning(T["campo_vacio_peticion"])

    cp1, cp2, cp3 = st.columns(3)

    with cp1:
        with st.expander(T["asociados"]):
            st.markdown(texto_instruccion("asociados"), unsafe_allow_html=True)
            bloque_acceso_y_peticion("asociado", "Credenciales Asociados", "asoc_part")

    with cp2:
        with st.expander(T["colaboradores"]):
            st.markdown(texto_instruccion("colaboradores"), unsafe_allow_html=True)
            bloque_acceso_y_peticion("colaborador", "Credenciales Colaboradores", "colab_part", incluir_centro_registro=True)

    with cp3:
        with st.expander(T["candidatos"]):
            st.markdown(texto_instruccion("candidato"), unsafe_allow_html=True)

    st.markdown(f"<h3 align='center' style='color: #0066cc; margin-top: 30px;'><b>{T['eslogan']}</b></h3>", unsafe_allow_html=True)

elif opcion == T["menu_eval"]:
    if not st.session_state.autenticado:
        st.warning(T["aviso_login_eval"])
    else:
        with st.container():
            c1, c2, c3 = st.columns(3)
            profesor = c1.text_input(T["profesor"], key=f"f_prof_{st.session_state.reset_todo}")
            
            opciones_cursos_display = [f"{c['codigo_curso']} - {c['nombre_curso']}" for c in cursos_db] if cursos_db else ["MZ-M - Mecanizados"]
            curso_seleccionado_full = c2.selectbox(T["curso"], opciones_cursos_display, key=f"f_cur_{st.session_state.reset_todo}")
            curso_codigo_actual = curso_seleccionado_full.split(" - ")[0] if " - " in curso_seleccionado_full else curso_seleccionado_full

            modulos_filtrados = [m for m in modulos_db if m["curso_asociado"] == curso_codigo_actual]
            opciones_modulos_display = [f"{m['subcodigo']} - {m['descripcion']}" for m in modulos_filtrados] if modulos_filtrados else ["Selecciona un curso válido"]
            modulo_seleccionado_full = c3.selectbox(T["modulo"], opciones_modulos_display, key=f"f_mod_{st.session_state.reset_todo}")
            modulo_codigo_actual = modulo_seleccionado_full.split(" - ")[0] if " - " in modulo_seleccionado_full else modulo_seleccionado_full

            nivel_sugerido = ""
            for m in modulos_filtrados:
                if m["subcodigo"] == modulo_codigo_actual:
                    nivel_sugerido = str(m["nivel_bloque"])
                    break

            c4, c5 = st.columns(2)
            nivel = c4.text_input(T["nivel_bloque"], value=nivel_sugerido, key=f"f_niv_{st.session_state.reset_todo}")
            alumno = c5.text_input(T["alumno"], key=f"f_alu_{st.session_state.alumno_key}")

        criterios = [
            "1. Tasa de eficiencia", "2. Precisión geométrica y mecánica", "3. Autonomía ejecutiva",
            "4. Índice de mermas", "5. Mantenimiento de utillaje y entorno", "6. Factor de desempeño temporal",
            "7. Resolución escenarios de prácticas", "8. Resolución escenarios de averías",
            "9. Precisión conceptual y terminología", "10. Seguridad y normativas",
            "11. Fiabilidad y compromiso operativo", "12. Capacidad de aprendizaje",
            "13. Comunicación y respeto al superior"
        ]

        # --- ANTES: la petición GET a la rúbrica se hacía aquí, sin caché, ---
        # --- así que se repetía en cada rerun (cada clic de puntuación).   ---
        # --- AHORA: se usa la versión cacheada, se pide una vez por hora.  ---
        descripciones_rubrica = cargar_rubrica()

        st.subheader(T["subt_puntuacion"])
        cols = st.columns(4)
        notas = {}
        
        for i, crit in enumerate(criterios):
            with cols[i % 4]:
                with st.container(border=True):
                    col_t, col_b = st.columns([0.82, 0.18])
                    
                    with col_t:
                        st.markdown(f"**{crit}**")
                        
                    with col_b:
                        info_crit = descripciones_rubrica.get(crit, {
                            "que_se_mide": "Información detallada en desarrollo.",
                            "nivel_rubrica": "Pendiente de definir rúbrica."
                        })
                        
                        with st.popover("ℹ️", help="Ver rúbrica"):
                            st.markdown(f"**{T['que_se_mide']}**\n\n{info_crit['que_se_mide']}")
                            st.markdown("---")
                            st.markdown(f"**{T['nivel_rubrica']}**")
                            st.markdown(info_crit['nivel_rubrica'])

                    notas[crit] = st.radio("p", [1, 2, 3, 4, 5], horizontal=True, key=f"rad_{crit}_{st.session_state.alumno_key}", index=None, label_visibility="collapsed")

        if None not in notas.values() and alumno:
            nota_final = round(sum((notas[c] - 1) * 2.5 for c in criterios) / len(criterios), 1)
            res = "SUSPENSO (Línea Roja)" if notas["10. Seguridad y normativas"] == 1 else ("APROBADO" if nota_final >= 5 else "SUSPENSO")
            st.metric(T["nota_final"], f"{nota_final} - {res}")
        else:
            nota_final, res = None, None

        if st.button(T["guardar_alumno"]):
            if nota_final is not None:
                registro = {"Alumno": alumno, "Profesor": profesor, "Curso": curso_seleccionado_full, "Modulo": modulo_codigo_actual, "Nivel": nivel, "Nota": nota_final, "Estado": res}
                registro.update(notas)
                st.session_state.lista_alumnos.append(registro)
                st.session_state.alumno_key += 1
                st.rerun()

        if st.session_state.lista_alumnos:
            st.subheader(T["resumen_alumnos"])
            df_resumen = pd.DataFrame(st.session_state.lista_alumnos)
            st.table(df_resumen)
            
            with st.expander(T["gestionar_alumnos"]):
                for i, reg in enumerate(st.session_state.lista_alumnos):
                    if st.button(f"🗑️ Eliminar a {reg['Alumno']}", key=f"del_{i}"):
                        st.session_state.lista_alumnos.pop(i)
                        st.rerun()

            if st.button(T["enviar_sheets"], type="primary"):
                url_script = "https://script.google.com/macros/s/AKfycbw1PNXaXT23jXJdKPOO9vbwrx6tnBI-hvlJrJFMNKZiy7G1JsNkTY-C6Ql7Wym_l-GG-Q/exec"
                try:
                    response = requests.post(url_script, json={"evaluaciones": st.session_state.lista_alumnos}, timeout=20)
                    if response.status_code == 200:
                        st.success(T["exito_envio"])
                        st.session_state.lista_alumnos = []
                        st.session_state.reset_todo += 1
                        st.rerun()
                    else:
                        st.error(f"Error en el servidor: {response.status_code}")
                except Exception as e: 
                    st.error(f"Error crítico de conexión: {e}")
