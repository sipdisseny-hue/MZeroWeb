import streamlit as st
import pandas as pd
import requests

# CONFIGURACIÓN
ID_DE_SHEET = "1kowfDSzZw_fpIO8tbrKGWxREONDIv2EFFhOtfgn-cKs"
st.set_page_config(page_title="MZero Web", layout="wide")

# INICIALIZACIÓN DE ESTADO
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'lista_alumnos' not in st.session_state: st.session_state.lista_alumnos = []
if 'alumno_key' not in st.session_state: st.session_state.alumno_key = 0
if 'reset_todo' not in st.session_state: st.session_state.reset_todo = 0
if 'texto_documentos' not in st.session_state: st.session_state.texto_documentos = "Bienvenido al área de consulta."
if 'usuario_actual' not in st.session_state: st.session_state.usuario_actual = ""

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
        
        if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
            texto_temp = st.text_area("Editar notas (Solo para ti):", value=st.session_state.texto_documentos, height=300)
            if st.button("💾 GUARDAR NOTAS"):
                st.session_state.texto_documentos = texto_temp
                st.success("Notas guardadas correctamente.")
                st.rerun()
        else:
            st.info(st.session_state.texto_documentos)

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
            "1. Tasa de eficiencia", "2. Precisión geométrica y mecánica", "3. Atonomia ejecutiva",
            "4. indice de mermas", "5. Mantenimiento de utillaje y entorno", "6. Factor de desempeño temporal",
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
            st.table(pd.DataFrame(st.session_state.lista_alumnos))
            
            if st.button("ENVIAR TODO A GOOGLE SHEETS", type="primary"):
                # URL de despliegue con /exec al final
                requests.post("https://script.google.com/macros/s/AKfycbw1PNXaXT23jXJdKPOO9vbwrx6tnBI-hvlJrJFMNKZiy7G1JsNkTY-C6Ql7Wym_l-GG-Q/exec", 
                              json={"evaluaciones": st.session_state.lista_alumnos})
                st.session_state.lista_alumnos = []
                st.session_state.reset_todo += 1
                st.rerun()
