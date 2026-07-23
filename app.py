import streamlit as st
import pandas as pd
import requests
from io import StringIO

# CONFIGURACIÓN
st.set_page_config(page_title="MZero Web", layout="wide")

# --- DICCIONARIO DE TEXTOS ESTÁTICOS PARA EL MENÚ Y ACCESOS ---
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
        "aviso_login_eval": "Debes iniciar sesión en el sidebar para acceder al módulo de evaluaciones.",
        "profesor": "Profesor",
        "curso": "Curso",
        "modulo": "Módulo",
        "nivel_bloque": "Nivel del Bloque",
        "alumno": "Nombre del Alumno",
        "subt_puntuacion": "Puntuación (de 0 a 10)",
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
        "aviso_login_eval": "Has d'iniciar sessió al sidebar per accedir al mòdul d'avaluacions.",
        "profesor": "Professor",
        "curso": "Curs",
        "modulo": "Mòdul",
        "nivel_bloque": "Nivell del Bloc",
        "alumno": "Nom de l'Alumne",
        "subt_puntuacion": "Puntuació (de 0 a 10)",
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
    url_script = "https://script.google.com/macros/s/AKfycbzAfnmO33bANwUsvDRkeMzLjLgLWZeSdzLNduleZ9UYDLEtIqe4YIb-gHSWmJaaFBYY/exec"
    try:
        response = requests.get(url_script, timeout=20)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                return data.get("cursos", []), data.get("modulos", [])
    except Exception as e:
        st.error(f"Error de conexión: {e}")
    return [], []

@st.cache_data(ttl=600)
def cargar_datos_de_google(nombre_pestana):
    url_script = f"https://script.google.com/macros/s/AKfycbzZDkU6ZfAK1tdy502iEVlQ3j42GWlVBh5DW1_XCD1BxpEI0NZ7Pss3MV0BMGYDikwR/exec?sheet={nombre_pestana}"
    try:
        response = requests.get(url_script, timeout=20)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                resultado = {}
                for item in data:
                    t = item.get("Titulo") or item.get("Títul") or item.get("título") or item.get("títul")
                    c = item.get("Contenido") or item.get("Contingut") or item.get("contenido") or item.get("contingut")
                    if t:
                        resultado[str(t).strip()] = str(c) if c else ""
                return resultado
        return {}
    except Exception as e:
        return {}

def refrescar_app():
    st.cache_data.clear()
    st.rerun()

# --- SIDEBAR ORIGINAL ---
with st.sidebar:
    st.image("logo_mzero.png")
    st.markdown("## M-Zero Pro")
    
    idioma_seleccionado = st.radio("Idioma", ["Castellano", "Català"], horizontal=True, label_visibility="collapsed")
    lang = "ca" if idioma_seleccionado == "Català" else "es"
    T = TEXTOS[lang]
    
    opcion = st.radio(T["nav_titulo"], [T["menu_docs"], T["menu_eval"]])
    
    st.divider()
    
    if 'autenticado' not in st.session_state: st.session_state.autenticado = False
    if 'usuario_actual' not in st.session_state: st.session_state.usuario_actual = ""
    
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
                    login_ok = any(str(df.iloc[i, 0]).strip() == usuario_in.strip() and str(df.iloc[i, 1]).strip() == pass_in.strip() for i in range(1, len(df)))
                    if login_ok:
                        st.session_state.autenticado = True
                        st.session_state.usuario_actual = usuario_in.strip()
                        st.rerun()
                    else:
                        st.error(T["error_login"])
                else:
                    st.error(T["error_cred"])
            except Exception as e:
                st.error(f"Error: {e}")

# --- SELECCIÓN DE PESTAÑA SEGÚN IDIOMA ---
pestana_activa = "Text" if lang == "ca" else "Textos"
datos_iniciales = cargar_datos_de_google(pestana_activa)
cursos_db, modulos_db = cargar_catalogo_cursos_y_modulos()

if 'lista_alumnos' not in st.session_state: st.session_state.lista_alumnos = []
if 'alumno_key' not in st.session_state: st.session_state.alumno_key = 0
if 'reset_todo' not in st.session_state: st.session_state.reset_todo = 0

if 'contenido_exp' not in st.session_state: st.session_state.contenido_exp = {}
if 'contenido_funcionalidad' not in st.session_state: st.session_state.contenido_funcionalidad = {}
if 'contenido_contacto' not in st.session_state: st.session_state.contenido_contacto = {}

for k, v in datos_iniciales.items():
    st.session_state.contenido_exp[k] = v
    st.session_state.contenido_funcionalidad[k] = v
    st.session_state.contenido_contacto[k] = v

def guardar_en_sheets(titulo, nuevo_contenido):
    url_script = f"https://script.google.com/macros/s/AKfycbzZDkU6ZfAK1tdy502iEVlQ3j42GWlVBh5DW1_XCD1BxpEI0NZ7Pss3MV0BMGYDikwR/exec?sheet={pestana_activa}"
    payload = {"titulo": titulo, "contenido": nuevo_contenido}
    try:
        response = requests.post(url_script, json=payload, timeout=20)
        return response.status_code == 200
    except:
        return False


# ==========================================
# PANTALLA 1: DOCUMENTOS EN CASTELLANO
# ==========================================
if opcion == T["menu_docs"] and lang == "es":
    st.markdown("## Área de Documentación y Consultas")
    
    with st.container(border=True):
        st.markdown("<h3 style='color: #0066cc;'><b>Asociados y Colaboradores</b></h3>", unsafe_allow_html=True)
        st.image("Asociados y colaboradores.png", width=300)
        
        st.markdown("<h4 style='color: #0066cc; margin-top: 20px;'>Asociados</h4>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        titulos_asociados = [
            ["Mecanizado", "Climatización", "Fontanería", "Empresas de trabajo temporal"],
            ["Electricidad", "Obra", "Electromecánica", "Renovables"],
            ["Hidráulica", "Construcción Mecánica", "Asociaciones y Gremios"]
        ]

        for i, col in enumerate([col1, col2, col3]):
            with col:
                for titulo in titulos_asociados[i]:
                    with st.expander(titulo):
                        if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
                            st.write(T["modo_edicion"])
                            nuevo_text = st.text_area(f"Editar {titulo}:", value=datos_iniciales.get(titulo, st.session_state.contenido_exp.get(titulo, "")), height=150, key=f"es_edit_{titulo}")
                            if st.button(f"Guardar {titulo}", key=f"es_btn_{titulo}"):
                                if guardar_en_sheets(titulo, nuevo_text):
                                    st.session_state.contenido_exp[titulo] = nuevo_text
                                    refrescar_app()
                        st.markdown(datos_iniciales.get(titulo, st.session_state.contenido_exp.get(titulo, "")), unsafe_allow_html=True)

        st.divider()
        st.markdown("<h4 style='color: #0066cc;'>Colaboradores</h4>", unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns(3)
        for i, col in enumerate([col_c1, col_c2, col_c3]):
            titulo = ["Centros de formación", "Gremios", "Asociaciones"][i]
            with col:
                with st.expander(titulo):
                    if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
                        st.write(T["modo_edicion"])
                        nuevo_text = st.text_area(f"Editar {titulo}:", value=datos_iniciales.get(titulo, st.session_state.contenido_exp.get(titulo, "")), height=150, key=f"es_edit_col_{titulo}")
                        if st.button(f"Guardar {titulo}", key=f"es_btn_col_{titulo}"):
                            if guardar_en_sheets(titulo, nuevo_text):
                                st.session_state.contenido_exp[titulo] = nuevo_text
                                refrescar_app()
                    st.markdown(datos_iniciales.get(titulo, st.session_state.contenido_exp.get(titulo, "")), unsafe_allow_html=True)

    st.markdown("<h3 style='color: #0066cc;'><b>Funcionalidad</b></h3>", unsafe_allow_html=True)
    for titulo in ["Argumentos M-Zero", "¿Por qué ser Asociado o Colaborador?", "Metodología M0", "El sello M-Zero 'Certificación de calidad'"]:
        with st.expander(titulo):
            if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
                temp_text = st.text_area(f"Editar {titulo}:", value=datos_iniciales.get(titulo, st.session_state.contenido_funcionalidad.get(titulo, "")), height=150, key=f"es_func_{titulo}")
                if st.button(f"Guardar {titulo}", key=f"es_save_func_{titulo}"):
                    if guardar_en_sheets(titulo, temp_text):
                        st.session_state.contenido_funcionalidad[titulo] = temp_text
                        refrescar_app()
            st.markdown(datos_iniciales.get(titulo, st.session_state.contenido_funcionalidad.get(titulo, "")), unsafe_allow_html=True)

    st.markdown("<h3 style='color: #0066cc;'><b>Contacto</b></h3>", unsafe_allow_html=True)
    for titulo in ["Móvil / WhatsApp", "Email"]:
        with st.expander(titulo):
            if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
                nuevo_cont = st.text_area(f"Editar {titulo}:", value=datos_iniciales.get(titulo, st.session_state.contenido_contacto.get(titulo, "")), height=70, key=f"es_cont_{titulo}")
                if st.button(f"Guardar {titulo}", key=f"es_save_cont_{titulo}"):
                    if guardar_en_sheets(titulo, nuevo_cont):
                        st.session_state.contenido_contacto[titulo] = nuevo_cont
                        refrescar_app()
            st.markdown(datos_iniciales.get(titulo, st.session_state.contenido_contacto.get(titulo, "")), unsafe_allow_html=True)

    st.markdown("## Cómo participar")
    cp1, cp2, cp3 = st.columns(3)
    for col, titulo in [(cp1, "Asociados"), (cp2, "Colaboradores"), (cp3, "Candidatos")]:
        with col:
            with st.expander(titulo):
                if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
                    st.write(T["modo_edicion"])
                    nuevo_text = st.text_area(f"Editar {titulo}:", value=datos_iniciales.get(titulo, st.session_state.contenido_exp.get(titulo, "")), height=150, key=f"es_part_{titulo}")
                    if st.button(f"Guardar {titulo}", key=f"es_btn_part_{titulo}"):
                        if guardar_en_sheets(titulo, nuevo_text):
                            st.session_state.contenido_exp[titulo] = nuevo_text
                            refrescar_app()
                st.markdown(datos_iniciales.get(titulo, st.session_state.contenido_exp.get(titulo, "")), unsafe_allow_html=True)

    st.markdown("<h3 align='center' style='color: #0066cc; margin-top: 30px;'><b>Conectando talento, transformando la industria</b></h3>", unsafe_allow_html=True)


# ==========================================
# PANTALLA 2: DOCUMENTOS EN CATALÁN
# ==========================================
elif opcion == T["menu_docs"] and lang == "ca":
    st.markdown("## Àrea de Documentació i Consultes")
    
    with st.container(border=True):
        st.markdown("<h3 style='color: #0066cc;'><b>Associats i Col·laboradors</b></h3>", unsafe_allow_html=True)
        st.image("Asociados y colaboradores.png", width=300)
        
        st.markdown("<h4 style='color: #0066cc; margin-top: 20px;'>Associats</h4>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        titulos_asociados_ca = [
            ["Mecanitzat", "Climatització", "Fontaneria", "Empreses de treball temporal"],
            ["Electricitat", "Obra", "Electromecànica", "Renovables"],
            ["Hidràulica", "Construcció Mecànica", "Associacions i Gremis"]
        ]

        for i, col in enumerate([col1, col2, col3]):
            with col:
                for titulo in titulos_asociados_ca[i]:
                    with st.expander(titulo):
                        if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
                            st.write(T["modo_edicion"])
                            nuevo_text = st.text_area(f"Editar {titulo}:", value=datos_iniciales.get(titulo, st.session_state.contenido_exp.get(titulo, "")), height=150, key=f"ca_edit_{titulo}")
                            if st.button(f"Guardar {titulo}", key=f"ca_btn_{titulo}"):
                                if guardar_en_sheets(titulo, nuevo_text):
                                    st.session_state.contenido_exp[titulo] = nuevo_text
                                    refrescar_app()
                        st.markdown(datos_iniciales.get(titulo, st.session_state.contenido_exp.get(titulo, "")), unsafe_allow_html=True)

        st.divider()
        st.markdown("<h4 style='color: #0066cc;'>Col·laboradors</h4>", unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns(3)
        for i, col in enumerate([col_c1, col_c2, col_c3]):
            titulo = ["Centres de formació", "Gremis", "Associacions"][i]
            with col:
                with st.expander(titulo):
                    if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
                        st.write(T["modo_edicion"])
                        nuevo_text = st.text_area(f"Editar {titulo}:", value=datos_iniciales.get(titulo, st.session_state.contenido_exp.get(titulo, "")), height=150, key=f"ca_edit_col_{titulo}")
                        if st.button(f"Guardar {titulo}", key=f"ca_btn_col_{titulo}"):
                            if guardar_en_sheets(titulo, nuevo_text):
                                st.session_state.contenido_exp[titulo] = nuevo_text
                                refrescar_app()
                    st.markdown(datos_iniciales.get(titulo, st.session_state.contenido_exp.get(titulo, "")), unsafe_allow_html=True)

    st.markdown("<h3 style='color: #0066cc;'><b>Funcionalitat</b></h3>", unsafe_allow_html=True)
    for titulo in ["Arguments M-Zero", "Per què ser Associat o Col·laborador?", "Metodologia M0", "El segell M-Zero 'Certificació de qualitat'"]:
        with st.expander(titulo):
            if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
                temp_text = st.text_area(f"Editar {titulo}:", value=datos_iniciales.get(titulo, st.session_state.contenido_funcionalidad.get(titulo, "")), height=150, key=f"ca_func_{titulo}")
                if st.button(f"Guardar {titulo}", key=f"ca_save_func_{titulo}"):
                    if guardar_en_sheets(titulo, temp_text):
                        st.session_state.contenido_funcionalidad[titulo] = temp_text
                        refrescar_app()
            st.markdown(datos_iniciales.get(titulo, st.session_state.contenido_funcionalidad.get(titulo, "")), unsafe_allow_html=True)

    st.markdown("<h3 style='color: #0066cc;'><b>Contacte</b></h3>", unsafe_allow_html=True)
    for titulo in ["Mòbil / WhatsApp", "Email"]:
        with st.expander(titulo):
            if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
                nuevo_cont = st.text_area(f"Editar {titulo}:", value=datos_iniciales.get(titulo, st.session_state.contenido_contacto.get(titulo, "")), height=70, key=f"ca_cont_{titulo}")
                if st.button(f"Guardar {titulo}", key=f"ca_save_cont_{titulo}"):
                    if guardar_en_sheets(titulo, nuevo_cont):
                        st.session_state.contenido_contacto[titulo] = nuevo_cont
                        refrescar_app()
            st.markdown(datos_iniciales.get(titulo, st.session_state.contenido_contacto.get(titulo, "")), unsafe_allow_html=True)

    st.markdown("## Com participar")
    cp1, cp2, cp3 = st.columns(3)
    for col, titulo in [(cp1, "Associats"), (cp2, "Col·laboradors"), (cp3, "Candidats")]:
        with col:
            with st.expander(titulo):
                if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
                    st.write(T["modo_edicion"])
                    nuevo_text = st.text_area(f"Editar {titulo}:", value=datos_iniciales.get(titulo, st.session_state.contenido_exp.get(titulo, "")), height=150, key=f"ca_part_{titulo}")
                    if st.button(f"Guardar {titulo}", key=f"ca_btn_part_{titulo}"):
                        if guardar_en_sheets(titulo, nuevo_text):
                            st.session_state.contenido_exp[titulo] = nuevo_text
                            refrescar_app()
                st.markdown(datos_iniciales.get(titulo, st.session_state.contenido_exp.get(titulo, "")), unsafe_allow_html=True)

    st.markdown("<h3 align='center' style='color: #0066cc; margin-top: 30px;'><b>Connectant talent, transformant la indústria</b></h3>", unsafe_allow_html=True)


# ==========================================
# PANTALLA DE EVALUACIONES
# ==========================================
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

            nivel_sugerido = next((str(m["nivel_bloque"]) for m in modulos_filtrados if m["subcodigo"] == modulo_codigo_actual), "")

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

        nombre_pestana_rubrica = "Rubrica CAT" if lang == "ca" else "Rubrica"
        descripciones_rubrica = {}
        try:
            url_apps_script = f"https://script.google.com/macros/s/AKfycbxdVRFxWRPb_F5y7yL9SvlA3OAPseJ0bG-pn7jAk9PYVZ8sXqNcVLlvBFVmun48mD1R7g/exec?sheet={nombre_pestana_rubrica}"
            resp_rubrica = requests.get(url_apps_script, timeout=10)
            if resp_rubrica.status_code == 200:
                for item in resp_rubrica.json():
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
                        info_crit = descripciones_rubrica.get(crit, {"que_se_mide": "En desarrollo.", "nivel_rubrica": "Pendiente."})
                        with st.popover("ℹ️", help="Ver rúbrica"):
                            st.markdown(f"**{T['que_se_mide']}**\n\n{info_crit['que_se_mide']}")
                            st.markdown("---")
                            st.markdown(f"**{T['nivel_rubrica']}**")
                            st.markdown(info_crit['nivel_rubrica'])

                    notas[crit] = st.radio("p", [1, 2, 3, 4, 5], horizontal=True, key=f"rad_{crit}_{st.session_state.alumno_key}", index=None, label_visibility="collapsed")

        if None not in notas.values() and alumno:
            suma_notas = sum(notas[c] for c in criterios)
            nota_final = round((suma_notas / (len(criterios) * 5)) * 10, 1)
            res = "SUSPENSO (Línea Roja)" if notas["10. Seguridad y normativas"] < 3 else ("APROBADO" if nota_final >= 5 else "SUSPENSO")
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
            st.table(pd.DataFrame(st.session_state.lista_alumnos))
            
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
                        st.error(f"Error en servidor: {response.status_code}")
                except Exception as e: 
                    st.error(f"Error de conexión: {e}")
