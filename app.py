import streamlit as st
import pandas as pd
import requests

# CONFIGURACIÓN
st.set_page_config(page_title="MZero Web", layout="wide")

# --- LECTURA DE DATOS Y SINCRONIZACIÓN ---
@st.cache_data(ttl=600)
def cargar_datos_de_google():
    url_script = "https://script.google.com/macros/s/AKfycbzZDkU6ZfAK1tdy502iEVlQ3j42GWlVBh5DW1_XCD1BxpEI0NZ7Pss3MV0BMGYDikwR/exec"
    try:
        response = requests.get(url_script, timeout=20)
        if response.status_code == 200:
            data = response.json()
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

# --- SIDEBAR: NAVEGACIÓN Y ACCESO ---
with st.sidebar:
    st.image("logo_mzero.png")
    st.markdown("## M-Zero Pro")
    
    opcion = st.radio("Navegación", ["Documentos", "Evaluaciones"])
    st.divider()
    
    if st.session_state.autenticado:
        st.success(f"Sesión iniciada: {st.session_state.usuario_actual}")
        if st.button("CERRAR SESIÓN"):
            st.session_state.autenticado = False
            st.session_state.usuario_actual = ""
            st.rerun()
    else:
        usuario_in = st.text_input("Usuario:")
        pass_in = st.text_input("Contraseña:", type="password")
        
        if st.button("Acceder"):
            url = f"https://docs.google.com/spreadsheets/d/1kowfDSzZw_fpIO8tbrKGWxREONDIv2EFFhOtfgn-cKs/gviz/tq?tqx=out:csv&sheet=Credenciales"
            try:
                df = pd.read_csv(url)
                if ((df['Usuarios'].astype(str).str.strip() == usuario_in.strip()) &  
                    (df['Password'].astype(str).str.strip() == pass_in.strip())).any():
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = usuario_in
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
            except Exception as e:
                st.error("Error al conectar con la hoja Credenciales")

# --- LÓGICA DE PANTALLAS ---
if opcion == "Documentos":
    st.markdown("## Área de Documentación y Consultas")
    
    with st.container(border=True):
        st.markdown("<h3 style='color: #0066cc;'><b>Asociados y Colaboradores</b></h3>", unsafe_allow_html=True)
        st.image("Asociados y colaboradores.png", width=300)
        
        # --- BLOQUE 1: ASOCIADOS ---
        st.markdown("<h4 style='color: #0066cc; margin-top: 20px;'>Asociados</h4>", unsafe_allow_html=True)
        
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
                            st.write("--- MODO EDICIÓN ---")
                            nuevo_text = st.text_area(f"Editar {titulo}:", value=st.session_state.contenido_exp.get(titulo, ""), height=150, key=f"edit_{titulo}")
                            img_file = st.file_uploader(f"Subir imagen para {titulo}", type=['png', 'jpg'], key=f"img_{titulo}")
                            
                            if st.button(f"Guardar {titulo}", key=f"btn_{titulo}"):
                                if guardar_en_sheets(titulo, nuevo_text):
                                    st.session_state.contenido_exp[titulo] = nuevo_text
                                    refrescar_app()
                        
                        st.markdown(st.session_state.contenido_exp.get(titulo, ""), unsafe_allow_html=True)

        st.divider()

        # --- BLOQUE 2: COLABORADORES (En línea horizontal de 3) ---
        st.markdown("<h4 style='color: #0066cc;'>Colaboradores</h4>", unsafe_allow_html=True)
        
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
                        st.write("--- MODO EDICIÓN ---")
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

    st.markdown("<h3 style='color: #0066cc;'><b>Funcionalidad</b></h3>", unsafe_allow_html=True)
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
    st.markdown("<h3 style='color: #0066cc;'><b>Contacto</b></h3>", unsafe_allow_html=True)
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
st.markdown("## Cómo participar")

col_p1, col_p2, col_p3 = st.columns(3)

with col_p1:
    with st.expander("Asociados"):
        if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
            st.write("--- MODO EDICIÓN ---")
            nuevo_text = st.text_area("Editar Asociados:", value=st.session_state.contenido_exp.get("Asociados", ""), height=150, key="edit_part_Asociados")
            if st.button("Guardar Asociados", key="btn_part_Asociados"):
                if guardar_en_sheets("Asociados", nuevo_text):
                    st.session_state.contenido_exp["Asociados"] = nuevo_text
                    refrescar_app()
        st.markdown(st.session_state.contenido_exp.get("Asociados", ""), unsafe_allow_html=True)

with col_p2:
    with st.expander("Colaboradores"):
        if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
            st.write("--- MODO EDICIÓN ---")
            nuevo_text = st.text_area("Editar Colaboradores:", value=st.session_state.contenido_exp.get("Colaboradores", ""), height=150, key="edit_part_Colaboradores")
            if st.button("Guardar Colaboradores", key="btn_part_Colaboradores"):
                if guardar_en_sheets("Colaboradores", nuevo_text):
                    st.session_state.contenido_exp["Colaboradores"] = nuevo_text
                    refrescar_app()
        st.markdown(st.session_state.contenido_exp.get("Colaboradores", ""), unsafe_allow_html=True)

with col_p3:
    with st.expander("Candidatos"):
        if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
            st.write("--- MODO EDICIÓN ---")
            nuevo_text = st.text_area("Editar Candidatos:", value=st.session_state.contenido_exp.get("Candidatos", ""), height=150, key="edit_part_Candidatos")
            if st.button("Guardar Candidatos", key="btn_part_Candidatos"):
                if guardar_en_sheets("Candidatos", nuevo_text):
                    st.session_state.contenido_exp["Candidatos"] = nuevo_text
                    refrescar_app()
        st.markdown(st.session_state.contenido_exp.get("Candidatos", ""), unsafe_allow_html=True)

# --- ESLOGAN FUERA DE LAS COLUMNAS (VISIBLE SIEMPRE) ---
st.markdown("""<div style="text-align: center; font-size: 1.6em; font-weight: bold; color: #0066cc; padding: 25px; border: 3px solid #0066cc; border-radius: 15px; margin-top: 20px; background-color: #f8fbff;">"Conectando talento, transformando la industria"</div>""", unsafe_allow_html=True)

elif opcion == "Evaluaciones":
    if not st.session_state.autenticado:
        st.warning("Debes iniciar sesión en el sidebar para acceder al módulo de evaluaciones.")
    else:
        with st.container():
            c1, c2, c3 = st.columns(3)
            profesor = c1.text_input("Profesor", key=f"f_prof_{st.session_state.reset_todo}")
            curso = c2.text_input("Curso", key=f"f_cur_{st.session_state.reset_todo}")
            modulo = c3.text_input("Módulo", key=f"f_mod_{st.session_state.reset_todo}")
            
            c4, c5 = st.columns(2)
            nivel = c4.text_input("Nivel del Bloque", key=f"f_niv_{st.session_state.reset_todo}")
            alumno = c5.text_input("Nombre del Alumno", key=f"f_alu_{st.session_state.alumno_key}")

        criterios = [
            "1. Tasa de eficiencia", "2. Precisión geométrica y mecánica", "3. Autonomía ejecutiva",
            "4. Índice de mermas", "5. Mantenimiento de utillaje y entorno", "6. Factor de desempeño temporal",
            "7. Resolución escenarios de prácticas", "8. Resolución escenarios de averías",
            "9. Precisión conceptual y terminología", "10. Seguridad y normativas",
            "11. Fiabilidad y compromiso operativo", "12. Capacidad de aprendizaje",
            "13. Comunicación y respeto al superior"
        ]

        st.subheader("Puntuación (1=Insuficiente, 3=Suficiente, 5=Excelente)")
        cols = st.columns(4)
        notas = {}
        for i, crit in enumerate(criterios):
            with cols[i % 4]:
                with st.container(border=True):
                    st.markdown(f"**{crit}**")
                    notas[crit] = st.radio("p", [1, 2, 3, 4, 5], horizontal=True, key=f"rad_{crit}_{st.session_state.alumno_key}", index=None, label_visibility="collapsed")

        if None not in notas.values() and alumno:
            nota_final = round(sum((notas[c] - 1) * 2.5 for c in criterios) / len(criterios), 1)
            res = "SUSPENSO (Línea Roja)" if notas["10. Seguridad y normativas"] == 1 else ("APROBADO" if nota_final >= 5 else "SUSPENSO")
            st.metric("NOTA FINAL", f"{nota_final} - {res}")
        else:
            nota_final, res = None, None

        if st.button("GUARDAR ALUMNO"):
            if nota_final is not None:
                registro = {"Alumno": alumno, "Profesor": profesor, "Curso": curso, "Modulo": modulo, "Nivel": nivel, "Nota": nota_final, "Estado": res}
                registro.update(notas)
                st.session_state.lista_alumnos.append(registro)
                st.session_state.alumno_key += 1
                st.rerun()

        if st.session_state.lista_alumnos:
            st.subheader("Resumen de Alumnos")
            df_resumen = pd.DataFrame(st.session_state.lista_alumnos)
            st.table(df_resumen)
            
            with st.expander("Gestionar alumnos (Eliminar)"):
                for i, reg in enumerate(st.session_state.lista_alumnos):
                    if st.button(f"🗑️ Eliminar a {reg['Alumno']}", key=f"del_{i}"):
                        st.session_state.lista_alumnos.pop(i)
                        st.rerun()

            if st.button("ENVIAR TODO A GOOGLE SHEETS", type="primary"):
                url_script = "https://script.google.com/macros/s/AKfycbw1PNXaXT23jXJdKPOO9vbwrx6tnBI-hvlJrJFMNKZiy7G1JsNkTY-C6Ql7Wym_l-GG-Q/exec"
                try:
                    response = requests.post(url_script, json={"evaluaciones": st.session_state.lista_alumnos}, timeout=20)
                    if response.status_code == 200:
                        st.success("Enviado con éxito a Google Sheets")
                        st.session_state.lista_alumnos = []
                        st.session_state.reset_todo += 1
                        st.rerun()
                    else:
                        st.error(f"Error en el servidor: {response.status_code}")
                except Exception as e: 
                    st.error(f"Error crítico de conexión: {e}")
