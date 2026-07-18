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
        # Configuración de credenciales (asegúrate de que los secrets estén configurados en Streamlit)
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
        client = gspread.authorize(creds)
        
        # Acceso a la hoja
        sheet = client.open_by_key(ID_DE_SHEET).worksheet("Textos")
        
        # Buscar el título y actualizar la celda de al lado
        cell = sheet.find(titulo)
        if cell:
            # Asumiendo que la columna B (col + 1) tiene el contenido
            sheet.update_cell(cell.row, cell.col + 1, nuevo_contenido)
            st.success(f"Datos de '{titulo}' guardados correctamente.")
        else:
            st.error(f"No se encontró el título '{titulo}' en la hoja de cálculo.")
            
    except Exception as e:
        st.error(f"Error al guardar: {e}")

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
            url = f"https://docs.google.com/spreadsheets/d/{ID_DE_SHEET}/gviz/tq?tqx=out:csv&sheet=Credenciales"
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
        
        # Tres columnas para los desplegables con lógica de edición para el admin
        col1, col2, col3 = st.columns(3)
        columnas = [col1, col2, col3]
        titulos = [
            ["Mecanizado", "Climatización", "Fontanería"],
            ["Electricidad", "Obra", "Electromecánica"],
            ["Hidráulica", "Construcción Mecánica", "Asociaciones y Gremios"]
        ]

        for i, col in enumerate(columnas):
            with col:
                for titulo in titulos[i]:
                    with st.expander(titulo):
                        # Lógica de edición (solo admin)
                        if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
                            st.write("--- MODO EDICIÓN ---")
                            nuevo_text = st.text_area(f"Editar {titulo}:", value=st.session_state.contenido_exp[titulo], height=150, key=f"edit_{titulo}")
                            img_file = st.file_uploader(f"Subir imagen para {titulo}", type=['png', 'jpg'], key=f"img_{titulo}")
                            
                            if st.button(f"Guardar {titulo}", key=f"btn_{titulo}"):
                                st.session_state.contenido_exp[titulo] = nuevo_text
                                st.rerun()
                        
                        # Visualización del contenido
                        st.markdown(st.session_state.contenido_exp[titulo], unsafe_allow_html=True)

       # --- BLOQUE 2: FUNCIONALIDAD ---
        st.markdown("<h3 style='color: #0066cc;'><b>Funcionalidad</b></h3>", unsafe_allow_html=True)
        
        # Lista de títulos para el bucle
        titulos_func = [
            "Argumentos M-Zero", 
            "¿Por qué ser Asociado o Colaborador?", 
            "Metodología M0", 
            "El sello M-Zero 'Certificación de calidad'"
        ]
        
        for titulo in titulos_func:
            with st.expander(titulo):
                # Modo edición (Solo ADMIN)
                if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
                    st.session_state.contenido_funcionalidad[titulo] = st.text_area(
                        f"Editar {titulo}:", 
                        value=st.session_state.contenido_funcionalidad.get(titulo, ""), 
                        height=150, 
                        key=f"func_{titulo}"
                    )
                # Visualización
                st.markdown(st.session_state.contenido_funcionalidad.get(titulo, ""), unsafe_allow_html=True)

        st.divider()

        # --- BLOQUE 3: CONTACTO ---
        st.markdown("<h3 style='color: #0066cc;'><b>Contacto</b></h3>", unsafe_allow_html=True)
        titulos_cont = ["Móvil / WhatsApp", "Email"]
        
        for titulo in titulos_cont:
            with st.expander(titulo):
                if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
                    st.session_state.contenido_contacto[titulo] = st.text_area(
                        f"Editar {titulo}:", 
                        value=st.session_state.contenido_contacto.get(titulo, ""), 
                        height=70, 
                        key=f"cont_{titulo}"
                    )
                st.markdown(st.session_state.contenido_contacto.get(titulo, ""), unsafe_allow_html=True)

        # --- BLOQUE 4: CÓMO PARTICIPAR ---
        st.markdown("<h3 style='color: #0066cc;'><b>Cómo participar</b></h3>", unsafe_allow_html=True)
        
        with st.expander("Información del sistema"):
            # Modo edición (Solo ADMIN)
            if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
                st.session_state.texto_documentos = st.text_area(
                    "Editar información:", 
                    value=st.session_state.texto_documentos, 
                    height=150, 
                    key="edit_participar"
                )
            # Visualización
            st.markdown(st.session_state.texto_documentos, unsafe_allow_html=True)

    # --- ESLOGAN DESTACADO ---
    st.markdown("""
        <div style="text-align: center; font-size: 1.6em; font-weight: bold; color: #0066cc; 
                    padding: 25px; border: 3px solid #0066cc; border-radius: 15px; 
                    margin-top: 40px; background-color: #f8fbff;">
            "Conectando talento, transformando la industria"
        </div>
    """, unsafe_allow_html=True)

elif opcion == "Evaluaciones":
    if not st.session_state.autenticado:
        st.warning("Debes iniciar sesión en el sidebar para acceder al módulo de evaluaciones.")
    else:
        # --- FORMULARIO PRINCIPAL ---
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
