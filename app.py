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
        "modo_edicion": "--- MODO EDICIÓN ---"
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
        "error_cred": "Error en connectar amb el full Credencials",
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
        "modo_edicion": "--- MODE EDICIÓ ---"
    }
}

# --- LECTURA DE DATOS Y SINCRONIZACIÓN ---
@st.cache_data(ttl=600)
def cargar_catalogo_cursos_y_modulos():
    # URL NUEVA ACTUALIZADA PARA CURSOS Y MÓDULOS
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
    # URL original de textos / datos del sistema
    url_script = "https://script.google.com/macros/s/AKfycbzZDkU6ZfAK1tdy502iEVlQ3j42GWlVBh5DW1_XCD1BxpEI0NZ7Pss3MV0BMGYDikwR/exec"
    try:
        response = requests.get(url_script, timeout=20)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return {item["Titulo"]: item["Contenido"] for item in data}
        return {}
    except Exception as e:
        st.error(f"Error de lectura: {e}")
        return {}

def refrescar_app():
    """Limpia caché, recarga los datos de Sheets y actualiza el estado"""
    st.cache_data.clear()
    nuevos_datos = cargar_datos_de_google()
    
    st.session_state.texto_documentos = nuevos_datos.get("Información del sistema", "Bienvenido al área de consulta.")
    st.session_state.contenido_funcionalidad = {key: nuevos_datos.get(key, "") for key in ["Argumentos M-Zero", "¿Por qué ser Asociado o Colaborador?", "Metodología M0", "El sello M-Zero 'Certificación de calidad'"]}
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
    st.session_state.contenido_funcionalidad = {key: datos_iniciales.get(key, "") for key in ["Argumentos M-Zero", "¿Por qué ser Asociado o Colaborador?", "Metodología M0", "El sello M-Zero 'Certificación de calidad'"]}

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
    
    # --- SELECTOR DE IDIOMA (BANDERA) ---
    idioma_seleccionado = st.radio("Idioma", ["🇪🇸 Castellano", "🏴󠁥󠁮󠁧󠁿 Català"], horizontal=True, label_visibility="collapsed")
    lang = "ca" if "Català" in idioma_seleccionado else "es"
    
    T = TEXTOS[lang] # Diccionario rápido para el idioma activo
    
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
            # URL original de credenciales
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
        
        # --- BLOQUE 1: ASOCIADOS ---
        st.markdown(f"<h4 style='color: #0066cc; margin-top: 20px;'>{T['asociados']}</h4>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        columnas_asociados = [col1, col2, col3]
        
        titulos_asociados = [
            ["Mecanizado", "Climatización", "Fontanería", "Empresas de trabajo temporal"],
            ["Electricidad", "Obra", "Electromecánica", "Renovables"],
            ["Hidráulica", "Construcción Mecánica", "Asociaciones y Gremios"]
        ]

        for i, col in enumerate(columnas_asociados):
            with col:
                for titulo in titulos_asociados[i]:
                    with st.expander(titulo):
                        if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
                            st.write(T["modo_edicion"])
                            nuevo_text = st.text_area(f"Editar {titulo}:", value=st.session_state.contenido_exp.get(titulo, ""), height=150, key=f"edit_{titulo}")
                            img_file = st.file_uploader(f"Subir imagen para {titulo}", type=['png', 'jpg'], key=f"img_{titulo}")
                            
                            if st.button(f"Guardar {titulo}", key=f"btn_{titulo}"):
                                if guardar_en_sheets(titulo, nuevo_text):
                                    st.session_state.contenido_exp[titulo] = nuevo_text
                                    refrescar_app()
                        
                        st.markdown(st.session_state.contenido_exp.get(titulo, ""), unsafe_allow_html=True)

        st.divider()

        # --- BLOQUE 2: COLABORADORES ---
        st.markdown(f"<h4 style='color: #0066cc;'>{T['colaboradores']}</h4>", unsafe_allow_html=True)
        
        col_c1, col_c2, col_c3 = st.columns(3)
        columnas_colaboradores = [col_c1, col_c2, col_c3]
        
        titulos_colaboradores = [
            "Centros de formación", 
            "Gremios", 
            "Asociaciones"
        ]
        
        for i, col in enumerate(columnas_colaboradores):
            with col:
                titulo = titulos_colaboradores[i]
                with st.expander(titulo):
                    if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
                        st.write(T["modo_edicion"])
                        nuevo_text = st.text_area(f"Editar {titulo}:", value=st.session_state.contenido_exp.get(titulo, ""), height=150, key=f"edit_col_{titulo}")
                        img_file = st.file_uploader(f"Subir imagen para {titulo}", type=['png', 'jpg'], key=f"img_col_{titulo}")
                        
                        if st.button(f"Guardar {titulo}", key=f"btn_col_{titulo}"):
                            if guardar_en_sheets(titulo, nuevo_text):
                                st.session_state.contenido_exp[titulo] = nuevo_text
                                refrescar_app()
                    
                    st.markdown(st.session_state.contenido_exp.get(titulo, ""), unsafe_allow_html=True)

    # --- BLOQUE 2: FUNCIONALIDAD ---
    if 'contenido_funcionalidad' not in st.session_state or not st.session_state.contenido_funcionalidad:
        st.session_state.contenido_funcionalidad = cargar_datos_de_google()

    st.markdown(f"<h3 style='color: #0066cc;'><b>{T['funcionalidad']}</b></h3>", unsafe_allow_html=True)
    titulos_func = ["Argumentos M-Zero", "¿Por qué ser Asociado o Colaborador?", "Metodología M0", "El sello M-Zero 'Certificación de calidad'"]

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

            st.markdown(st.session_state.contenido_funcionalidad.get(titulo, ""))

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

    cp1, cp2, cp3 = st.columns(3)
    columnas_participar = [
        (cp1, "Asociados"),
        (cp2, "Colaboradores"),
        (cp3, "Candidatos")
    ]

    for col, titulo in columnas_participar:
        with col:
            with st.expander(titulo):
                sesion_ok = (
                    st.session_state.autenticado 
                    and st.session_state.usuario_actual == "mzerojc"
                )
                if sesion_ok:
                    st.write(T["modo_edicion"])
                    nuevo_text = st.text_area(
                        f"Editar {titulo}:", 
                        value=st.session_state.contenido_exp.get(
                            titulo, ""
                        ), 
                        height=150, 
                        key=f"edit_part_{titulo}"
                    )
                    btn_guardar = st.button(
                        f"Guardar {titulo}", 
                        key=f"btn_part_{titulo}"
                    )
                    if btn_guardar:
                        if guardar_en_sheets(titulo, nuevo_text):
                            st.session_state.contenido_exp[titulo] = nuevo_text
                            refrescar_app()
                
                st.markdown(
                    st.session_state.contenido_exp.get(
                        titulo, ""
                    ), 
                    unsafe_allow_html=True
                )

    # --- ESLOGAN FUERA DE LAS COLUMNAS (VISIBLE SIEMPRE) ---
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

        descripciones_rubrica = {}
        try:
            # URL original de la rúbrica
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
                # URL original para enviar las evaluaciones
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
