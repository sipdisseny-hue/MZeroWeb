import streamlit as st
import pandas as pd
import requests
import re
import hashlib
from datetime import date
from io import StringIO

try:
    from fpdf import FPDF
    FPDF_DISPONIBLE = True
except ImportError:
    FPDF_DISPONIBLE = False

try:
    from supabase import create_client
    SUPABASE_DISPONIBLE = True
except ImportError:
    SUPABASE_DISPONIBLE = False

if SUPABASE_DISPONIBLE:
    @st.cache_resource
    def obtener_cliente_supabase():
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

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
        "acceso_asociados": "Acceso Asociados",
        "acceso_colaboradores": "Acceso Colaboradores",
        "acceso_candidatos": "Acceso Candidatos",
        "colaboradores": "Colaboradores",
        "funcionalidad": "Funcionalidad",
        "contacto": "Contacto",
        "como_participar": "Cómo participar",
        "eslogan": "Conectando talento, transformando la industria",
        "aviso_login_eval": "Debes iniciar sesión en el sidebar para acceder al módulo de evaluaciones.",
        "profesor": "Profesor",
        "id_docente": "Id Docente",
        "usuario_docente": "Usuario Docente",
        "acceso_docente": "Acceso Docente",
        "aviso_id_docente": "Introduce tu Id Docente para ver los cursos asignados.",
        "aviso_sin_cursos_docente": "No hay ningún curso asignado a este Id Docente.",
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
        "campo_nombre_empresa": "Nombre Empresa",
        "campo_nombre_centro": "Nombre del Centro",
        "campo_sector": "Sector",
        "campo_provincia": "Provincia",
        "campo_poblacion": "Población",
        "campo_cp": "CP",
        "campo_razon_social": "Razón Social",
        "campo_cif_nif": "CIF/NIF",
        "campo_telefono": "Teléfono",
        "campo_email": "Email",
        "campo_nombre_contacto": "Nombre Contacto",
        "campo_web": "Web",
        "campo_usuario_deseado": "Usuario que quiero usar",
        "campo_contrasena_deseada": "Contraseña que quiero usar",
        "campo_vacio_usuario_contrasena": "Indica el usuario y la contraseña que quieres usar.",
        "solicitud_pendiente_aviso": "Solicitud enviada. En cuanto sea aprobada podrás acceder con tu usuario y contraseña.",
        "anadir_curso": "Añadir curso",
        "campo_referencia_curso": "Referencia del curso",
        "campo_nombre_curso": "Nombre del curso",
        "campo_nombre_modulo": "Nombre del módulo",
        "campo_horas_totales": "Horas totales del curso",
        "campo_competencias": "Competencias adquiridas",
        "enviar_curso": "Enviar curso",
        "curso_enviado": "Curso enviado. Quedará visible en cuanto lo aprobemos.",
        "campo_vacio_curso": "Rellena al menos la referencia y el nombre del curso.",
        "anadir_docente": "Añadir docente",
        "campo_nombre_docente": "Nombre del docente",
        "campo_curso_relacionado": "Curso al que está relacionado",
        "enviar_docente": "Enviar docente",
        "docente_enviado": "Docente enviado. En cuanto lo activemos, le enviaremos su clave de acceso por email.",
        "campo_vacio_docente": "Rellena el nombre, usuario y email del docente.",
        "sin_cursos_propios": "Primero añade un curso para poder relacionarle un docente.",
        "descargar_pdf": "📄 Descargar PDF antes de enviar",
        "fpdf_no_disponible": "Para poder descargar el PDF, añade 'fpdf2' al archivo requirements.txt de la app.",
        "titulos_func": ["Argumentos M-Zero", "¿Por qué ser Asociado o Colaborador?", "Metodología M0", "El sello M-Zero 'Certificación de calidad'"],
        "campo_nombre_alumno": "Nombre",
        "campo_apellidos_alumno": "Apellidos",
        "campo_localidad": "Localidad",
        "campo_tablas_faltan": "Faltan tablas de gestión de cursos en Supabase: {tablas}.",
        "campo_migracion_cursos": "La conexión actual con SUPABASE_URL y SUPABASE_KEY no cambia. Ejecuta el SQL de migración de cursos para crear estas tablas.",
        "estado_pendiente": "pendiente",
        "estado_activo": "activo",
        "plan_basic": "BASIC",
        "plan_standard": "STANDARD",
        "plan_basic_precio": "50 €/curso",
        "plan_standard_precio": "38 €/mes",
        "plan_promocion": "Promoción 2026",
        "plan_uso_app": "Uso indefinido de la app",
        "plan_basic_uso_app": "Uso por curso",
        "plan_etiqueta_web": "Etiqueta enlace a su web",
        "plan_impuestos": "Impuestos incluidos",
        "plan_standard_inactivo": "De momento no disponible",
        "plan_seleccionar_basic": "Seleccionar BASIC",
        "plan_standard_bloqueado": "STANDARD no disponible",
        "plan_volver": "← Volver a las opciones",
        "reg_plan_seleccionado": "Plan seleccionado: BASIC",
        "plan_subtitulo": "Selecciona una modalidad para continuar con el registro.",
        "asoc_plan_basic_precio": "70 €/informe",
        "asoc_plan_standard_precio": "100 €/mes",
        "asoc_plan_promocion": "PROMOCIÓN",
        "asoc_plan_uso_app": "Uso de la app para peticiones de candidatos o formaciones",
        "asoc_plan_etiqueta_web": "Etiqueta enlace a su web",
        "asoc_plan_informe_max": "Informe máximo de 20 alumnos",
        "asoc_plan_informe_mensual": "Informe mensual de candidatos del sector",
        "asoc_plan_standard_inactivo": "De momento no disponible",
        "asoc_plan_seleccionar_basic": "Seleccionar BASIC",
        "asoc_plan_standard_bloqueado": "STANDARD no disponible",
        "asoc_plan_volver": "← Volver a las opciones",
        "asoc_plan_subtitulo": "Selecciona una modalidad para continuar con el registro.",
        "asoc_reg_plan_seleccionado": "Plan seleccionado: BASIC",
        "gestion_cursos": 'Gestión de cursos',
        "gestion_cursos_desc": 'Crea una nueva edición de un curso, reutiliza la información que ya exista y gestiona posteriormente sus docentes y alumnos.',
        "crear_nuevo_curso": '➕ Crear nuevo curso',
        "mis_cursos": '📚 Mis cursos',
        "selecciona_curso": '1. Selecciona el curso',
        "help_codigo": 'Introduce el código del curso. Si ya existe, se reutilizará su ficha.',
        "curso_existente": '✅ Curso existente encontrado: **{ref} — {nombre}**. Se reutilizará su información y no tendrás que volver a describirlo.',
        "codigo_nuevo_info": 'Si es un código nuevo, completa la ficha del curso.',
        "docentes_edicion": '2. Docentes de esta edición',
        "docentes_reutilizables": 'Estos docentes ya están relacionados con este código de curso. Puedes reutilizarlos sin volver a introducir sus datos.',
        "sin_docentes_curso": 'Este código existe, pero todavía no tiene docentes relacionados.',
        "anadir_docentes_nuevos": 'Añadir docentes nuevos',
        "nombre_docente": 'Nombre del docente',
        "usuario_docente": 'Usuario del docente',
        "email_docente": 'Email del docente',
        "anadir_docente_nuevo": '➕ Añadir docente nuevo a la edición',
        "rellena_docente": 'Rellena nombre, usuario y email del docente.',
        "docentes_tendra": 'Docentes que tendrá esta edición: **{total}**',
        "alumnos_edicion": '3. Alumnos de la nueva edición',
        "alumnos_info": 'Los alumnos pertenecen a cada edición/grupo. Aunque reutilices el mismo código y los mismos docentes, los alumnos de esta nueva edición deben añadirse aquí.',
        "anadir_alumno_edicion": '➕ Añadir alumno a la nueva edición',
        "todos_campos_alumno": 'Todos los campos del alumno son obligatorios.',
        "enviar_peticion_curso": '4. Enviar petición del curso',
        "enviar_peticion_curso_btn": '🚀 ENVIAR PETICIÓN DEL CURSO',
        "indica_codigo": 'Indica el código del curso.',
        "codigo_nuevo_nombre": 'Al ser un código nuevo, debes indicar el nombre del curso.',
        "al_menos_docente": 'Añade o reutiliza al menos un docente para esta edición.',
        "al_menos_alumno": 'Debes añadir al menos un alumno a la nueva edición.',
        "peticion_curso_ok": "Petición del curso enviada correctamente. Puedes consultar y ampliar esta edición desde 'Mis cursos'.",
        "error_peticion_curso": 'No se pudo enviar la petición del curso: {error}',
        "mis_cursos_info": 'Todavía no tienes cursos enviados.',
        "estado": 'Estado:',
        "cerrado": '🔒 CERRADO',
        "abierto": '🟢 ABIERTO',
        "resumen_doc_alu": '{docentes} docentes · {alumnos} alumnos',
        "seccion_docentes": 'Docentes',
        "seccion_alumnos": 'Alumnos',
        "sin_alumnos": 'No hay alumnos registrados.',
        "edicion_abierta": 'Esta edición está abierta. Puedes añadir docentes o alumnos hasta que el docente envíe las evaluaciones.',
        "anadir_docente": 'Añadir docente',
        "usuario": 'Usuario',
        "email": 'Email',
        "docente_anadido": 'Docente añadido a esta edición.',
        "error_anadir_docente": 'No se pudo añadir el docente: {error}',
        "anadir_alumno": 'Añadir alumno',
        "alumno_anadido": 'Alumno añadido a esta edición.',
        "error_anadir_alumno": 'No se pudo añadir el alumno: {error}',
        "edicion_cerrada": '🔒 Esta edición está cerrada porque el docente ya ha enviado las evaluaciones. Ya no se pueden añadir docentes ni alumnos.',
        "codigo_curso_nuevo": 'Si el código ya existe, se reutilizará su ficha.',
        "legal_titulo": "Información legal y protección de datos",
        "aviso_legal": "Aviso legal",
        "politica_privacidad": "Política de privacidad",
        "politica_cookies": "Política de cookies",
        "legal_responsable": "Responsable: Joan Carles Ros (autónomo)",
        "legal_nombre_comercial": "Nombre comercial: Mzero",
        "legal_nif": "NIF: 77735854V",
        "legal_domicilio": "Domicilio: Avda. Generalitat, 14, Barcelona",
        "legal_email": "Email: contacto.mzero@gmail.com",
        "legal_aviso_texto": "Mzero es el nombre comercial bajo el que Joan Carles Ros, como profesional autónomo, presta los servicios ofrecidos mediante esta aplicación. Esta aplicación proporciona funcionalidades de documentación, gestión de cursos, gestión de docentes y alumnos y evaluación formativa o profesional, según el acceso utilizado.",
        "legal_privacidad_texto": "Los datos personales se tratarán para gestionar las solicitudes de alta, los accesos, la relación con asociados y colaboradores, la gestión de cursos, docentes y alumnos, y la realización y conservación de evaluaciones cuando corresponda. La base jurídica podrá ser la ejecución de una relación contractual o precontractual, el cumplimiento de obligaciones legales y, cuando sea necesario, el consentimiento del interesado. Solo se solicitarán los datos necesarios para cada finalidad. Los datos se conservarán durante el tiempo necesario para cumplir la finalidad y atender las obligaciones legales y posibles responsabilidades. Podrán intervenir proveedores tecnológicos necesarios para prestar el servicio, como alojamiento, base de datos y herramientas de gestión de información, aplicándose las garantías exigibles en materia de protección de datos. No se realizarán cesiones con fines comerciales ajenos a la prestación del servicio salvo obligación legal o consentimiento cuando corresponda.",
        "legal_derechos_texto": "Puedes ejercer los derechos de acceso, rectificación, supresión, oposición, limitación del tratamiento y, cuando proceda, portabilidad, escribiendo a contacto.mzero@gmail.com. También puedes presentar una reclamación ante la Agencia Española de Protección de Datos (AEPD) si consideras que el tratamiento no se ajusta a la normativa aplicable.",
        "legal_cookies_texto": "Esta aplicación utiliza únicamente las tecnologías de almacenamiento o cookies necesarias para su funcionamiento, mantenimiento de la sesión y prestación de las funcionalidades solicitadas. No se utilizarán cookies no necesarias para publicidad comportamental o seguimiento comercial sin obtener previamente el consentimiento exigible. Si en el futuro se incorporan cookies o tecnologías de terceros que requieran consentimiento, se informará de forma específica y se ofrecerán opciones equivalentes para aceptar o rechazar dicho uso.",
        "legal_actualizacion": "Esta información podrá actualizarse cuando cambien la aplicación, los tratamientos de datos o la normativa aplicable.",

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
        "acceso_asociados": "Accés Associats",
        "acceso_colaboradores": "Accés Col·laboradors",
        "acceso_candidatos": "Accés Candidats",
        "colaboradores": "Col·laboradors",
        "funcionalidad": "Funcionalitat",
        "contacto": "Contacte",
        "como_participar": "Com participar",
        "eslogan": "Connectant talent, transformant la indústria",
        "aviso_login_eval": "Has d'iniciar sessió al sidebar per accedir al mòdul d'avaluacions.",
        "profesor": "Professor",
        "id_docente": "Id Docent",
        "usuario_docente": "Usuari Docent",
        "acceso_docente": "Accés Docent",
        "aviso_id_docente": "Introdueix el teu Id Docent per veure els cursos assignats.",
        "aviso_sin_cursos_docente": "No hi ha cap curs assignat a aquest Id Docent.",
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
        "campo_nombre_empresa": "Nom Empresa",
        "campo_nombre_centro": "Nom del Centre",
        "campo_sector": "Sector",
        "campo_provincia": "Província",
        "campo_poblacion": "Població",
        "campo_cp": "CP",
        "campo_razon_social": "Raó Social",
        "campo_cif_nif": "CIF/NIF",
        "campo_telefono": "Telèfon",
        "campo_email": "Email",
        "campo_nombre_contacto": "Nom Contacte",
        "campo_web": "Web",
        "campo_usuario_deseado": "Usuari que vull utilitzar",
        "campo_contrasena_deseada": "Contrasenya que vull utilitzar",
        "campo_vacio_usuario_contrasena": "Indica l'usuari i la contrasenya que vols utilitzar.",
        "solicitud_pendiente_aviso": "Sol·licitud enviada. Quan sigui aprovada podràs accedir amb el teu usuari i contrasenya.",
        "anadir_curso": "Afegir curs",
        "campo_referencia_curso": "Referència del curs",
        "campo_nombre_curso": "Nom del curs",
        "campo_nombre_modulo": "Nom del mòdul",
        "campo_horas_totales": "Hores totals del curs",
        "campo_competencias": "Competències adquirides",
        "enviar_curso": "Enviar curs",
        "curso_enviado": "Curs enviat. Quedarà visible quan l'aprovem.",
        "campo_vacio_curso": "Omple almenys la referència i el nom del curs.",
        "anadir_docente": "Afegir docent",
        "campo_nombre_docente": "Nom del docent",
        "campo_curso_relacionado": "Curs al qual està relacionat",
        "enviar_docente": "Enviar docent",
        "docente_enviado": "Docent enviat. Quan l'activem, li enviarem la seva clau d'accés per email.",
        "campo_vacio_docente": "Omple el nom, usuari i email del docent.",
        "sin_cursos_propios": "Primer afegeix un curs per poder-hi relacionar un docent.",
        "descargar_pdf": "📄 Descarregar PDF abans d'enviar",
        "fpdf_no_disponible": "Per poder descarregar el PDF, afegeix 'fpdf2' a l'arxiu requirements.txt de l'app.",
        "titulos_func": ["Arguments M-Zero", "Per què ser Associat o Colaborador?", "Metodologia M0", "El segell M-Zero 'Certificació de qualitat'"],
        "campo_nombre_alumno": "Nom",
        "campo_apellidos_alumno": "Cognoms",
        "campo_localidad": "Localitat",
        "campo_tablas_faltan": "Falten taules de gestió de cursos a Supabase: {tablas}.",
        "campo_migracion_cursos": "La connexió actual amb SUPABASE_URL i SUPABASE_KEY no canvia. Executa l’SQL de migració de cursos per crear aquestes taules.",
        "estado_pendiente": "pendent",
        "estado_activo": "actiu",
        "plan_basic": "BASIC",
        "plan_standard": "STANDARD",
        "plan_basic_precio": "50 €/curs",
        "plan_standard_precio": "38 €/mes",
        "plan_promocion": "Promoció 2026",
        "plan_uso_app": "Ús indefinit de l'app",
        "plan_basic_uso_app": "Ús per curs",
        "plan_etiqueta_web": "Etiqueta amb enllaç al seu web",
        "plan_impuestos": "Impostos inclosos",
        "plan_standard_inactivo": "De moment no disponible",
        "plan_seleccionar_basic": "Seleccionar BASIC",
        "plan_standard_bloqueado": "STANDARD no disponible",
        "plan_volver": "← Tornar a les opcions",
        "reg_plan_seleccionado": "Pla seleccionat: BASIC",
        "plan_subtitulo": "Selecciona una modalitat per continuar amb el registre.",
        "asoc_plan_basic_precio": "70 €/informe",
        "asoc_plan_standard_precio": "100 €/mes",
        "asoc_plan_promocion": "PROMOCIÓ",
        "asoc_plan_uso_app": "Ús de l'app per a peticions de candidats o formacions",
        "asoc_plan_etiqueta_web": "Etiqueta amb enllaç al seu web",
        "asoc_plan_informe_max": "Informe màxim de 20 alumnes",
        "asoc_plan_informe_mensual": "Informe mensual de candidats del sector",
        "asoc_plan_standard_inactivo": "De moment no disponible",
        "asoc_plan_seleccionar_basic": "Seleccionar BASIC",
        "asoc_plan_standard_bloqueado": "STANDARD no disponible",
        "asoc_plan_volver": "← Tornar a les opcions",
        "asoc_plan_subtitulo": "Selecciona una modalitat per continuar amb el registre.",
        "asoc_reg_plan_seleccionado": "Pla seleccionat: BASIC",
        "gestion_cursos": 'Gestió de cursos',
        "gestion_cursos_desc": 'Crea una nova edició d’un curs, reutilitza la informació que ja existeixi i gestiona posteriorment els seus docents i alumnes.',
        "crear_nuevo_curso": '➕ Crear nou curs',
        "mis_cursos": '📚 Els meus cursos',
        "selecciona_curso": '1. Selecciona el curs',
        "help_codigo": 'Introdueix el codi del curs. Si ja existeix, se’n reutilitzarà la fitxa.',
        "curso_existente": '✅ Curs existent trobat: **{ref} — {nombre}**. Se’n reutilitzarà la informació i no hauràs de tornar a descriure’l.',
        "codigo_nuevo_info": 'Si és un codi nou, completa la fitxa del curs.',
        "docentes_edicion": '2. Docents d’aquesta edició',
        "docentes_reutilizables": 'Aquests docents ja estan relacionats amb aquest codi de curs. Pots reutilitzar-los sense tornar a introduir-ne les dades.',
        "sin_docentes_curso": 'Aquest codi existeix, però encara no té docents relacionats.',
        "anadir_docentes_nuevos": 'Afegir docents nous',
        "nombre_docente": 'Nom del docent',
        "email_docente": 'Email del docent',
        "anadir_docente_nuevo": '➕ Afegir docent nou a l’edició',
        "rellena_docente": 'Omple nom, usuari i email del docent.',
        "docentes_tendra": 'Docents que tindrà aquesta edició: **{total}**',
        "alumnos_edicion": '3. Alumnes de la nova edició',
        "alumnos_info": 'Els alumnes pertanyen a cada edició/grup. Encara que reutilitzis el mateix codi i els mateixos docents, els alumnes d’aquesta nova edició s’han d’afegir aquí.',
        "anadir_alumno_edicion": '➕ Afegir alumne a la nova edició',
        "todos_campos_alumno": 'Tots els camps de l’alumne són obligatoris.',
        "enviar_peticion_curso": '4. Enviar petició del curs',
        "enviar_peticion_curso_btn": '🚀 ENVIAR PETICIÓ DEL CURS',
        "indica_codigo": 'Indica el codi del curs.',
        "codigo_nuevo_nombre": 'En ser un codi nou, has d’indicar el nom del curs.',
        "al_menos_docente": 'Afegeix o reutilitza almenys un docent per a aquesta edició.',
        "al_menos_alumno": 'Has d’afegir almenys un alumne a la nova edició.',
        "peticion_curso_ok": 'Petició del curs enviada correctament. Pots consultar i ampliar aquesta edició des de «Els meus cursos».',
        "error_peticion_curso": 'No s’ha pogut enviar la petició del curs: {error}',
        "mis_cursos_info": 'Encara no tens cursos enviats.',
        "estado": 'Estat:',
        "cerrado": '🔒 TANCAT',
        "abierto": '🟢 OBERT',
        "resumen_doc_alu": '{docentes} docents · {alumnos} alumnes',
        "seccion_docentes": 'Docents',
        "seccion_alumnos": 'Alumnes',
        "sin_alumnos": 'No hi ha alumnes registrats.',
        "edicion_abierta": 'Aquesta edició està oberta. Pots afegir docents o alumnes fins que el docent enviï les avaluacions.',
        "email": 'Email',
        "docente_anadido": 'Docent afegit a aquesta edició.',
        "error_anadir_docente": 'No s’ha pogut afegir el docent: {error}',
        "anadir_alumno": 'Afegir alumne',
        "alumno_anadido": 'Alumne afegit a aquesta edició.',
        "error_anadir_alumno": 'No s’ha pogut afegir l’alumne: {error}',
        "edicion_cerrada": '🔒 Aquesta edició està tancada perquè el docent ja ha enviat les avaluacions. Ja no es poden afegir docents ni alumnes.',
        "codigo_curso_nuevo": 'Si el codi ja existeix, se’n reutilitzarà la fitxa.',
        "legal_titulo": "Informació legal i protecció de dades",
        "aviso_legal": "Avís legal",
        "politica_privacidad": "Política de privacitat",
        "politica_cookies": "Política de cookies",
        "legal_responsable": "Responsable: Joan Carles Ros (autònom)",
        "legal_nombre_comercial": "Nom comercial: Mzero",
        "legal_nif": "NIF: 77735854V",
        "legal_domicilio": "Domicili: Avda. Generalitat, 14, Barcelona",
        "legal_email": "Email: contacto.mzero@gmail.com",
        "legal_aviso_texto": "Mzero és el nom comercial sota el qual Joan Carles Ros, com a professional autònom, presta els serveis oferts mitjançant aquesta aplicació. Aquesta aplicació proporciona funcionalitats de documentació, gestió de cursos, gestió de docents i alumnes i avaluació formativa o professional, segons l’accés utilitzat.",
        "legal_privacidad_texto": "Les dades personals es tractaran per gestionar les sol·licituds d’alta, els accessos, la relació amb associats i col·laboradors, la gestió de cursos, docents i alumnes, i la realització i conservació d’avaluacions quan correspongui. La base jurídica podrà ser l’execució d’una relació contractual o precontractual, el compliment d’obligacions legals i, quan sigui necessari, el consentiment de la persona interessada. Només se sol·licitaran les dades necessàries per a cada finalitat. Les dades es conservaran durant el temps necessari per complir la finalitat i atendre les obligacions legals i possibles responsabilitats. Poden intervenir proveïdors tecnològics necessaris per prestar el servei, com ara allotjament, base de dades i eines de gestió d’informació, aplicant les garanties exigibles en matèria de protecció de dades. No es faran cessions amb finalitats comercials alienes a la prestació del servei excepte per obligació legal o amb el consentiment quan correspongui.",
        "legal_derechos_texto": "Pots exercir els drets d’accés, rectificació, supressió, oposició, limitació del tractament i, quan correspongui, portabilitat, escrivint a contacto.mzero@gmail.com. També pots presentar una reclamació davant l’Agència Espanyola de Protecció de Dades (AEPD) si consideres que el tractament no s’ajusta a la normativa aplicable.",
        "legal_cookies_texto": "Aquesta aplicació utilitza únicament les tecnologies d’emmagatzematge o cookies necessàries per al seu funcionament, manteniment de la sessió i prestació de les funcionalitats sol·licitades. No s’utilitzaran cookies no necessàries per a publicitat comportamental o seguiment comercial sense obtenir prèviament el consentiment exigible. Si en el futur s’incorporen cookies o tecnologies de tercers que requereixin consentiment, s’informarà de manera específica i s’oferiran opcions equivalents per acceptar o rebutjar aquest ús.",
        "legal_actualizacion": "Aquesta informació podrà actualitzar-se quan canviïn l’aplicació, els tractaments de dades o la normativa aplicable.",

    }
}

# --- TRADUCCIÓN SOLO VISUAL (Català) de campos y criterios de Evaluaciones ---
# No afecta a los datos que se envían al Excel ni a las claves internas
# (Alumno, Curso, "1. Tasa de eficiencia"...); solo se usa para mostrar en
# pantalla (tabla resumen) y en el PDF descargable.
TRADUCCION_EVAL_CA = {
    "Alumno": "Alumne", "Profesor": "Professor", "Usuario": "Usuari",
    "Curso": "Curs", "Modulo": "Mòdul", "Nivel": "Nivell",
    "Nota": "Nota", "Estado": "Estat",
    "1. Tasa de eficiencia": "1. Taxa d'eficiència",
    "2. Precisión geométrica y mecánica": "2. Precisió geomètrica i mecànica",
    "3. Autonomía ejecutiva": "3. Autonomia executiva",
    "4. Índice de mermas": "4. Índex de minves",
    "5. Mantenimiento de utillaje y entorno": "5. Manteniment de l'utillatge i l'entorn",
    "6. Factor de desempeño temporal": "6. Factor d'acompliment temporal",
    "7. Resolución escenarios de prácticas": "7. Resolució d'escenaris de pràctiques",
    "8. Resolución escenarios de averías": "8. Resolució d'escenaris d'avaries",
    "9. Precisión conceptual y terminología": "9. Precisió conceptual i terminologia",
    "10. Seguridad y normativas": "10. Seguretat i normatives",
    "11. Fiabilidad y compromiso operativo": "11. Fiabilitat i compromís operatiu",
    "12. Capacidad de aprendizaje": "12. Capacitat d'aprenentatge",
    "13. Comunicación y respeto al superior": "13. Comunicació i respecte al superior"
}

# --- TRADUCCIÓN SOLO VISUAL (Català) de las categorías de Asociados/Colaboradores ---
# El filtrado sigue comparando contra el texto original en castellano (columna
# Sector/Categoría del Excel); esto solo cambia la etiqueta que se ve en pantalla.
TRADUCCION_CATEGORIAS_CA = {
    "Mecanizado": "Mecanitzat",
    "Climatización": "Climatització",
    "Fontanería": "Fontaneria",
    "Empresas de trabajo temporal": "Empreses de treball temporal",
    "Electricidad": "Electricitat",
    "Obra": "Obra",
    "Electromecánica": "Electromecànica",
    "Renovables": "Renovables",
    "Hidráulica": "Hidràulica",
    "Construcción Mecánica": "Construcció Mecànica",
    "Asociaciones y Gremios": "Associacions i Gremis",
    "Centros de formación": "Centres de formació",
    "Gremios": "Gremis",
    "Asociaciones": "Associacions"
}

# --- LECTURA DE DATOS Y SINCRONIZACIÓN ---
@st.cache_data(ttl=120)
def cargar_catalogo_cursos_y_modulos():
    url_script = "https://script.google.com/macros/s/AKfycbzAfnmO33bANwUsvDRkeMzLjLgLWZeSdzLNduleZ9UYDLEtIqe4YIb-gHSWmJaaFBYY/exec"
    try:
        response = requests.get(url_script, timeout=30)
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
    resultado = {}
    # Pedimos las dos pestañas (Textos=es, Text=ca) y las fusionamos en un
    # único diccionario. Antes solo se pedía la de castellano (por defecto),
    # así que los títulos en catalán ("Arguments M-Zero", etc.) nunca llegaban.
    for idioma_param in ["es", "ca"]:
        try:
            response = requests.get(url_script, params={"lang": idioma_param}, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    for item in data:
                        t = item.get("Títul") if item.get("Títul") is not None else item.get("Titulo")
                        c = item.get("Contingut") if item.get("Contingut") is not None else item.get("Contenido")
                        if t is not None:
                            resultado[str(t).strip()] = str(c) if c is not None else ""
        except Exception as e:
            st.error(f"Error de lectura ({idioma_param}): {e}")
    return resultado

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
        response = requests.get(url_script, params={"tipo": "participar"}, timeout=30)
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
    # Nueva URL: script del Excel "Cómo participar" (Code_ComoParticipar_Peticiones.gs)
    url_script = "https://script.google.com/macros/s/AKfycbwTg1YZU4jcfhZOvQEwUJzW8CusvQbmHzpyDen8FENx_iAIPhHV8OjAiwAGGvzIrvu0/exec"
    payload = {"tipo": tipo, "id_empresa": id_empresa, "texto": texto}
    try:
        response = requests.post(url_script, json=payload, timeout=20)
        if response.status_code != 200:
            st.error(f"El servidor respondió con un error ({response.status_code}) al enviar la petición.")
            return False
        try:
            data = response.json()
        except Exception:
            # El script devolvió texto plano (p. ej. "OK"), lo damos por válido
            return True
        if isinstance(data, dict) and data.get("ok") is False:
            st.error(f"No se pudo guardar la petición: {data.get('error', 'error desconocido')}")
            return False
        return True
    except Exception as e:
        st.error(f"Error de conexión al enviar la petición: {e}")
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

# --- NUEVO: NOTIFICACIONES (en la app + email) ---
# --- NUEVO: VALIDADOR DE DNI / NIE / CIF (algoritmo oficial español) ---
def validar_dni_nie_cif(valor):
    """Devuelve (es_valido: bool|None, tipo: str|None). None si el campo
    está vacío o no coincide con ningún formato reconocido."""
    valor = valor.strip().upper().replace(" ", "").replace("-", "")
    if not valor:
        return None, None

    letras_dni = "TRWAGMYFPDXBNJZSQVHLCKE"

    # DNI: 8 dígitos + letra de control
    if re.fullmatch(r"\d{8}[A-Z]", valor):
        letra_esperada = letras_dni[int(valor[:8]) % 23]
        return valor[8] == letra_esperada, "DNI"

    # NIE: X/Y/Z + 7 dígitos + letra de control
    if re.fullmatch(r"[XYZ]\d{7}[A-Z]", valor):
        prefijo = {"X": "0", "Y": "1", "Z": "2"}[valor[0]]
        letra_esperada = letras_dni[int(prefijo + valor[1:8]) % 23]
        return valor[8] == letra_esperada, "NIE"

    # CIF: letra + 7 dígitos + dígito o letra de control
    if re.fullmatch(r"[A-HJNPQRSUVW]\d{7}[0-9A-J]", valor):
        digitos = valor[1:8]
        suma_par = sum(int(d) for i, d in enumerate(digitos) if i % 2 == 1)
        suma_impar = 0
        for i, d in enumerate(digitos):
            if i % 2 == 0:
                doble = int(d) * 2
                suma_impar += doble // 10 + doble % 10
        digito_control = (10 - (suma_par + suma_impar) % 10) % 10
        letra_control = "JABCDEFGHI"[digito_control]
        control = valor[8]
        return control == str(digito_control) or control == letra_control, "CIF"

    return False, None


def enviar_email(destinatario, asunto, mensaje):
    """Envía un email si hay credenciales configuradas en Secrets
    (EMAIL_USER, EMAIL_PASSWORD). Si no están configuradas, o falla el
    envío, no rompe el flujo de la app — devuelve True/False para que
    quien llame pueda avisar si quiere."""
    if "EMAIL_USER" not in st.secrets or "EMAIL_PASSWORD" not in st.secrets:
        return False
    try:
        import smtplib
        from email.mime.text import MIMEText
        msg = MIMEText(mensaje)
        msg["Subject"] = asunto
        msg["From"] = st.secrets["EMAIL_USER"]
        msg["To"] = destinatario
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(st.secrets["EMAIL_USER"], st.secrets["EMAIL_PASSWORD"])
            server.send_message(msg)
        return True
    except Exception:
        return False


def crear_notificacion(tipo, mensaje):
    """Guarda el aviso en Supabase (para el badge dentro de la app) y
    además intenta mandarlo por email al administrador."""
    if SUPABASE_DISPONIBLE:
        try:
            obtener_cliente_supabase().table("notificaciones").insert({"tipo": tipo, "mensaje": mensaje}).execute()
        except Exception:
            pass
    destinatario_admin = st.secrets.get("EMAIL_NOTIFY_TO", st.secrets.get("EMAIL_USER", ""))
    if destinatario_admin:
        enviar_email(destinatario_admin, "M-Zero: nueva petición", mensaje)


# --- NUEVO: REGISTRO Y LOGIN DE EMPRESAS (Colaboradores) CONTRA SUPABASE ---
def enviar_peticion_registro_supabase(tipo, campos, usuario, contrasena):
    if not SUPABASE_DISPONIBLE:
        return False
    try:
        cliente = obtener_cliente_supabase()
        fila = dict(campos)
        fila["tipo"] = tipo
        fila["estado"] = "pendiente"
        fila["usuario"] = usuario
        fila["contrasena"] = contrasena
        cliente.table("empresas").insert(fila).execute()
        nombre_mostrar = campos.get("nombre_centro") or campos.get("nombre_empresa") or usuario
        crear_notificacion("registro", f"Nueva solicitud de registro ({tipo}): {nombre_mostrar}")
        return True
    except Exception as e:
        st.error(f"Error al enviar la solicitud: {e}")
        return False


def verificar_credencial_supabase(usuario, contrasena, tipo):
    if not SUPABASE_DISPONIBLE:
        return None
    try:
        cliente = obtener_cliente_supabase()
        resultado = (
            cliente.table("empresas").select("*")
            .eq("usuario", usuario.strip())
            .eq("contrasena", contrasena.strip())
            .eq("tipo", tipo)
            .eq("estado", "activo")
            .execute()
        )
        if resultado.data:
            return resultado.data[0]
    except Exception:
        pass
    return None


# --- NUEVO: EL COLABORADOR PROPONE CURSO+MÓDULO Y DOCENTE ---
def enviar_curso_modulo_supabase(empresa_id, nombre_empresa, referencia, nombre_curso, nombre_modulo, nivel, horas, competencias):
    if not SUPABASE_DISPONIBLE:
        return False
    try:
        cliente = obtener_cliente_supabase()

        existe_curso = cliente.table("cursos").select("codigo_curso").eq("codigo_curso", referencia).execute().data
        if not existe_curso:
            cliente.table("cursos").insert({
                "codigo_curso": referencia,
                "nombre_es": nombre_curso,
                "empresa_id": empresa_id,
                "estado": "pendiente",
                "horas_totales": horas or None,
                "competencias": competencias
            }).execute()

        modulos_existentes = cliente.table("modulos").select("subcodigo").eq("codigo_curso", referencia).execute().data
        subcodigo = f"{referencia}-M{len(modulos_existentes) + 1}"
        cliente.table("modulos").insert({
            "subcodigo": subcodigo,
            "codigo_curso": referencia,
            "descripcion_es": nombre_modulo,
            "nivel_bloque": nivel or None,
            "estado": "pendiente"
        }).execute()

        crear_notificacion("curso", f"Nuevo curso propuesto por {nombre_empresa}: {referencia} - {nombre_curso}")
        return True
    except Exception as e:
        st.error(f"Error al enviar el curso: {e}")
        return False


def enviar_docente_supabase(empresa_id, nombre_empresa, nombre_docente, usuario_docente, email_docente, codigo_curso):
    if not SUPABASE_DISPONIBLE:
        return False
    try:
        cliente = obtener_cliente_supabase()

        existente = cliente.table("docentes").select("id_docente").eq("usuario", usuario_docente).execute().data
        if existente:
            id_docente = existente[0]["id_docente"]
        else:
            id_docente = usuario_docente
            cliente.table("docentes").insert({
                "id_docente": id_docente,
                "nombre": nombre_docente,
                "usuario": usuario_docente,
                "email": email_docente,
                "estado": "pendiente",
                "empresa_id": empresa_id
            }).execute()

        ya_vinculado = (
            cliente.table("curso_docente").select("id_docente")
            .eq("id_docente", id_docente).eq("codigo_curso", codigo_curso).execute().data
        )
        if not ya_vinculado:
            cliente.table("curso_docente").insert({"id_docente": id_docente, "codigo_curso": codigo_curso}).execute()

        crear_notificacion("docente", f"Nuevo docente propuesto por {nombre_empresa}: {nombre_docente} ({usuario_docente}) para {codigo_curso}")
        return True
    except Exception as e:
        st.error(f"Error al enviar el docente: {e}")
        return False

# --- NUEVO: PDF DEL RESUMEN DE ALUMNOS (antes de enviar) ---
def _pdf_texto_seguro(valor):
    """Los tipos de letra base de fpdf2 solo soportan Latin-1. Cualquier
    carácter fuera de ese rango (comillas curvas, guiones largos, emojis...)
    se sustituye por el más parecido en vez de romper la generación del PDF."""
    return str(valor).encode("latin-1", "replace").decode("latin-1")


def _edition_ref_corta(valor):
    """Referencia visual de 5 dígitos; no modifica el EditionId real."""
    if valor is None or str(valor).strip() == "":
        return ""
    digest = hashlib.sha256(str(valor).encode("utf-8")).hexdigest()
    return f"{int(digest[:12], 16) % 100000:05d}"

def _alumno_ref_corta(valor):
    """Referencia visual estable de 5 dígitos para el alumno; no modifica su ID real."""
    if valor is None or str(valor).strip() == "":
        return ""
    digest = hashlib.sha256(str(valor).encode("utf-8")).hexdigest()
    return f"{int(digest[:12], 16) % 100000:05d}"

def generar_pdf_resumen(lista_alumnos, lang="es"):
    criterios = [
        "1. Tasa de eficiencia", "2. Precisión geométrica y mecánica", "3. Autonomía ejecutiva",
        "4. Índice de mermas", "5. Mantenimiento de utillaje y entorno", "6. Factor de desempeño temporal",
        "7. Resolución escenarios de prácticas", "8. Resolución escenarios de averías",
        "9. Precisión conceptual y terminología", "10. Seguridad y normativas",
        "11. Fiabilidad y compromiso operativo", "12. Capacidad de aprendizaje",
        "13. Comunicación y respeto al superior"
    ]

    # Etiquetas visibles: en catalán si corresponde, siempre buscando los
    # VALORES con la clave original en castellano (eso no cambia).
    def etiqueta(clave):
        return TRADUCCION_EVAL_CA.get(clave, clave) if lang == "ca" else clave

    titulo_pdf = "Resum d'Avaluacions - M-Zero" if lang == "ca" else "Resumen de Evaluaciones - M-Zero"

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, titulo_pdf, ln=True, align="C")
    pdf.ln(4)

    ancho_pagina = pdf.w - pdf.l_margin - pdf.r_margin
    ancho_criterio = ancho_pagina / 2

    for idx, reg in enumerate(lista_alumnos):
        alumno = _pdf_texto_seguro(reg.get("Alumno", ""))
        curso = _pdf_texto_seguro(reg.get("Curso", ""))
        modulo = _pdf_texto_seguro(reg.get("Modulo", ""))
        profesor = _pdf_texto_seguro(reg.get("Profesor", ""))
        usuario = _pdf_texto_seguro(reg.get("Usuario", ""))
        nivel = _pdf_texto_seguro(reg.get("Nivel", ""))
        nota = _pdf_texto_seguro(reg.get("Nota", ""))
        estado = _pdf_texto_seguro(reg.get("Estado", ""))

        # Si a un alumno no le cabe ni la cabecera antes del margen inferior,
        # saltamos de página nosotros mismos para no partirla a la mitad.
        if pdf.get_y() > pdf.h - 60:
            pdf.add_page()

        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, f"{alumno} - {curso} / {modulo}"[:100], ln=True)

        pdf.set_font("Helvetica", "", 9)
        linea_datos = (
            f"{etiqueta('Profesor')}: {profesor}    {etiqueta('Usuario')}: {usuario}    "
            f"{etiqueta('Nivel')}: {nivel}    {etiqueta('Nota')}: {nota}    {etiqueta('Estado')}: {estado}"
        )
        pdf.cell(0, 6, linea_datos[:150], ln=True)
        pdf.ln(1)

        pdf.set_font("Helvetica", "", 8)
        for i, crit in enumerate(criterios):
            valor = _pdf_texto_seguro(reg.get(crit, ""))
            texto = f"{etiqueta(crit)}: {valor}"
            pdf.cell(ancho_criterio, 5.5, texto[:70], border=1)
            if i % 2 == 1:
                pdf.ln()
        if len(criterios) % 2 == 1:
            pdf.ln()

        if idx < len(lista_alumnos) - 1:
            pdf.ln(5)

    salida = pdf.output()
    return bytes(salida)

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
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'lista_alumnos' not in st.session_state: st.session_state.lista_alumnos = []
if 'alumno_key' not in st.session_state: st.session_state.alumno_key = 0
if 'reset_todo' not in st.session_state: st.session_state.reset_todo = 0
if 'usuario_actual' not in st.session_state: st.session_state.usuario_actual = ""
if 'acceso_panel' not in st.session_state: st.session_state.acceso_panel = None

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
    
    def _abrir_acceso(tipo):
        # Callback ejecutado antes de que se creen los widgets del siguiente rerun.
        # Así evitamos modificar la session_state de un radio ya instanciado.
        st.session_state["navegacion"] = T["menu_docs"]
        st.session_state["acceso_panel"] = tipo

    def _cambiar_navegacion():
        # Al navegar manualmente entre Documentación/Evaluaciones se cierra
        # cualquier pantalla de acceso independiente.
        st.session_state["acceso_panel"] = None

    opcion = st.radio(
        T["nav_titulo"],
        [T["menu_docs"], T["menu_eval"]],
        key="navegacion",
        index=0,
        on_change=_cambiar_navegacion
    )

    st.divider()
    st.markdown(
        """<style>
        section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
            min-height: 46px;
            border-radius: 10px;
            font-weight: 600;
            text-align: left;
            padding-left: 16px;
            margin-bottom: 8px;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    st.markdown("### 🔐 Accesos")

    # Estos botones sustituyen ÚNICAMENTE al antiguo usuario/contraseña del sidebar.
    # Cada uno abre la funcionalidad que ya existía en 'Cómo participar'.
    st.button(
        f"👥  {T['acceso_asociados']}",
        key="btn_acceso_asociados",
        use_container_width=True,
        on_click=_abrir_acceso,
        args=("asociado",),
    )
    st.button(
        f"🏢  {T['acceso_colaboradores']}",
        key="btn_acceso_colaboradores",
        use_container_width=True,
        on_click=_abrir_acceso,
        args=("colaborador",),
    )
    st.button(
        f"🎓  {T['acceso_candidatos']}",
        key="btn_acceso_candidatos",
        use_container_width=True,
        on_click=_abrir_acceso,
        args=("candidato",),
    )

    # El antiguo acceso administrativo no se elimina: se conserva aquí para no
    # romper la edición de contenidos ni el panel de administración.
    with st.expander("⚙️ Administración", expanded=False):
        if st.session_state.autenticado:
            st.success(f"{T['sesion_iniciada']} {st.session_state.usuario_actual}")
            if st.button(T["cerrar_sesion"], key="admin_logout_sidebar"):
                st.session_state.autenticado = False
                st.session_state.usuario_actual = ""
                st.rerun()
        else:
            usuario_admin = st.text_input(T["usuario"], key="admin_user_sidebar")
            pass_admin = st.text_input(T["password"], type="password", key="admin_pass_sidebar")
            if st.button(T["btn_acceder"], key="admin_login_sidebar"):
                url = "https://docs.google.com/spreadsheets/d/1kowfDSzZw_fpIO8tbrKGWxREONDIv2EFFhOtfgn-cKs/gviz/tq?tqx=out:csv&sheet=Credenciales"
                try:
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        df = pd.read_csv(StringIO(response.text), header=None)
                        login_ok = any(
                            str(df.iloc[i, 0]).strip() == usuario_admin.strip()
                            and str(df.iloc[i, 1]).strip() == pass_admin.strip()
                            for i in range(1, len(df))
                        )
                        if login_ok:
                            st.session_state.autenticado = True
                            st.session_state.usuario_actual = usuario_admin.strip()
                            st.rerun()
                        else:
                            st.error(T["error_login"])
                    else:
                        st.error(T["error_cred"])
                except Exception as e:
                    st.error(f"Error de acceso: {e}")

    # --- NUEVO: PANEL DE APROBACIÓN DE PETICIONES PENDIENTES -------------------
    if SUPABASE_DISPONIBLE and st.session_state.autenticado:
        st.divider()
        try:
            cliente_pend = obtener_cliente_supabase()
            pendientes_empresas = cliente_pend.table("empresas").select("*").eq("estado", "pendiente").execute().data
            pendientes_cursos = cliente_pend.table("cursos").select("*").eq("estado", "pendiente").execute().data
            pendientes_modulos = cliente_pend.table("modulos").select("*").eq("estado", "pendiente").execute().data
            pendientes_docentes = cliente_pend.table("docentes").select("*").eq("estado", "pendiente").execute().data
        except Exception as e:
            pendientes_empresas, pendientes_cursos, pendientes_modulos, pendientes_docentes = [], [], [], []
            st.error(f"Error al cargar pendientes: {e}")

        total_pendientes = len(pendientes_empresas) + len(pendientes_cursos) + len(pendientes_modulos) + len(pendientes_docentes)
        etiqueta_panel = f"🔔 Peticiones pendientes ({total_pendientes})" if total_pendientes else "🔔 Peticiones pendientes"

        with st.expander(etiqueta_panel):
            if total_pendientes == 0:
                st.caption("No hay peticiones pendientes.")

            # --- Empresas (Asociados/Colaboradores) ---
            if pendientes_empresas:
                st.markdown("**Empresas / Colaboradores**")
                for emp in pendientes_empresas:
                    nombre_mostrar = emp.get("nombre_centro") or emp.get("nombre_empresa") or emp.get("usuario", "")
                    st.write(f"**{nombre_mostrar}** — {emp.get('tipo', '')}")
                    st.caption(f"Usuario propuesto: {emp.get('usuario', '')} · Email: {emp.get('email', '')}")
                    if st.button("✅ Activar", key=f"activar_emp_{emp['id']}"):
                        try:
                            cliente_pend.table("empresas").update({"estado": "activo"}).eq("id", emp["id"]).execute()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al activar: {e}")
                    st.divider()

            # --- Cursos (con sus módulos pendientes asociados, si los tiene) ---
            if pendientes_cursos:
                st.markdown("**Cursos nuevos**")
                for curso in pendientes_cursos:
                    modulos_de_este_curso = [m for m in pendientes_modulos if m["codigo_curso"] == curso["codigo_curso"]]
                    st.write(f"**{curso['codigo_curso']} - {curso.get('nombre_es', '')}**")
                    st.caption(f"Horas: {curso.get('horas_totales', '')} · Competencias: {curso.get('competencias', '')}")
                    for m in modulos_de_este_curso:
                        st.caption(f"↳ Módulo: {m['subcodigo']} - {m.get('descripcion_es', '')} (Nivel {m.get('nivel_bloque', '')})")
                    if st.button("✅ Activar curso" + (" + módulo(s)" if modulos_de_este_curso else ""), key=f"activar_curso_{curso['codigo_curso']}"):
                        try:
                            cliente_pend.table("cursos").update({"estado": "activo"}).eq("codigo_curso", curso["codigo_curso"]).execute()
                            for m in modulos_de_este_curso:
                                cliente_pend.table("modulos").update({"estado": "activo"}).eq("subcodigo", m["subcodigo"]).execute()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al activar: {e}")
                    st.divider()

            # --- Módulos pendientes de cursos que YA estaban activos ---
            modulos_sueltos = [m for m in pendientes_modulos if m["codigo_curso"] not in [c["codigo_curso"] for c in pendientes_cursos]]
            if modulos_sueltos:
                st.markdown("**Módulos nuevos (de cursos ya activos)**")
                for m in modulos_sueltos:
                    st.write(f"**{m['subcodigo']}** - {m.get('descripcion_es', '')} (Curso {m['codigo_curso']}, Nivel {m.get('nivel_bloque', '')})")
                    if st.button("✅ Activar módulo", key=f"activar_modulo_{m['subcodigo']}"):
                        try:
                            cliente_pend.table("modulos").update({"estado": "activo"}).eq("subcodigo", m["subcodigo"]).execute()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al activar: {e}")
                    st.divider()

            # --- Docentes: aquí se les asigna la contraseña y se les avisa por email ---
            if pendientes_docentes:
                st.markdown("**Docentes nuevos**")
                for doc in pendientes_docentes:
                    cursos_del_docente = cliente_pend.table("curso_docente").select("codigo_curso").eq("id_docente", doc["id_docente"]).execute().data
                    codigos_cursos_doc = ", ".join(c["codigo_curso"] for c in cursos_del_docente) or "—"
                    st.write(f"**{doc.get('nombre', '')}** (usuario: {doc.get('usuario', '')})")
                    st.caption(f"Email: {doc.get('email', '')} · Cursos: {codigos_cursos_doc}")
                    contrasena_nueva = st.text_input("Contraseña a asignar", key=f"pass_doc_{doc['id_docente']}", type="password")
                    if st.button("✅ Activar y enviar email", key=f"activar_doc_{doc['id_docente']}"):
                        if not contrasena_nueva.strip():
                            st.warning("Escribe una contraseña antes de activar.")
                        else:
                            try:
                                cliente_pend.table("docentes").update({
                                    "contrasena": contrasena_nueva.strip(), "estado": "activo"
                                }).eq("id_docente", doc["id_docente"]).execute()

                                if doc.get("email"):
                                    enviado = enviar_email(
                                        doc["email"],
                                        "M-Zero: acceso a Evaluaciones",
                                        f"Hola {doc.get('nombre', '')},\n\nYa tienes acceso al sistema de evaluación de M-Zero.\n\nUsuario: {doc.get('usuario', '')}\nContraseña: {contrasena_nueva.strip()}\n\nAccede desde la pestaña Evaluaciones de la app."
                                    )
                                    if not enviado:
                                        st.warning("Docente activado, pero no se pudo enviar el email (revisa la configuración de EMAIL_USER/EMAIL_PASSWORD en Secrets).")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al activar: {e}")
                    st.divider()

# --- LÓGICA DE PANTALLAS ---
def bloque_solicitud_alta(tipo, key_prefix, incluir_centro=False, usar_supabase=False, mostrar_en_expander=True):
    """Formulario para pedir el alta como Asociado o Colaborador nuevo.

    Para Colaboradores, el formulario se muestra después de seleccionar el plan BASIC.
    """
    version = st.session_state.get(f"{key_prefix}_reg_version", 0)

    contenedor = st.expander(T["solicitar_alta"]) if mostrar_en_expander else st.container()
    with contenedor:
        nombre_empresa = st.text_input(T["campo_nombre_empresa"], key=f"{key_prefix}_reg_empresa_{version}")

        nombre_centro = ""
        if incluir_centro:
            nombre_centro = st.text_input(T["campo_nombre_centro"], key=f"{key_prefix}_reg_centro_{version}")

        sector = st.text_input(T["campo_sector"], key=f"{key_prefix}_reg_sector_{version}")

        c1, c2 = st.columns(2)
        provincia = c1.text_input(T["campo_provincia"], key=f"{key_prefix}_reg_prov_{version}")
        poblacion = c2.text_input(T["campo_poblacion"], key=f"{key_prefix}_reg_pob_{version}")

        c3, c4 = st.columns(2)
        cp = c3.text_input(T["campo_cp"], key=f"{key_prefix}_reg_cp_{version}")
        razon_social = c4.text_input(T["campo_razon_social"], key=f"{key_prefix}_reg_razon_{version}")

        c5, c6 = st.columns(2)
        cif_nif = c5.text_input(T["campo_cif_nif"], key=f"{key_prefix}_reg_cif_{version}")
        telefono = c6.text_input(T["campo_telefono"], key=f"{key_prefix}_reg_tel_{version}")

        c7, c8 = st.columns(2)
        email = c7.text_input(T["campo_email"], key=f"{key_prefix}_reg_email_{version}")
        nombre_contacto = c8.text_input(T["campo_nombre_contacto"], key=f"{key_prefix}_reg_contacto_{version}")

        web = st.text_input(T["campo_web"], key=f"{key_prefix}_reg_web_{version}")

        usuario_deseado = ""
        contrasena_deseada = ""
        if usar_supabase:
            c9, c10 = st.columns(2)
            usuario_deseado = c9.text_input(T["campo_usuario_deseado"], key=f"{key_prefix}_reg_usuario_{version}")
            contrasena_deseada = c10.text_input(T["campo_contrasena_deseada"], type="password", key=f"{key_prefix}_reg_contrasena_{version}")

        if st.button(T["enviar_solicitud"], key=f"{key_prefix}_reg_btn_enviar"):
            if not nombre_empresa.strip():
                st.warning(T["campo_vacio_empresa"])
            elif usar_supabase and (cif_nif.strip() and not validar_documento_fiscal(cif_nif.strip())):
                st.warning("El CIF/NIF/DNI indicado no supera la comprobación. Revísalo antes de enviar la solicitud.")
            elif usar_supabase and (not usuario_deseado.strip() or not contrasena_deseada.strip()):
                st.warning(T["campo_vacio_usuario_contrasena"])
            elif usar_supabase:
                campos = {
                    "nombre_empresa": nombre_empresa.strip(),
                    "sector": sector.strip(),
                    "provincia": provincia.strip(),
                    "poblacion": poblacion.strip(),
                    "cp": cp.strip(),
                    "razon_social": razon_social.strip(),
                    "cif_nif": cif_nif.strip(),
                    "telefono": telefono.strip(),
                    "email": email.strip(),
                    "nombre_contacto": nombre_contacto.strip(),
                    "web": web.strip(),
                }
                if incluir_centro:
                    campos["nombre_centro"] = nombre_centro.strip()

                if enviar_peticion_registro_supabase(tipo, campos, usuario_deseado.strip(), contrasena_deseada.strip()):
                    st.success(T["solicitud_pendiente_aviso"])
                    st.session_state[f"{key_prefix}_reg_version"] = version + 1
                    st.rerun()
                else:
                    st.error(T["error_solicitud"])
            else:
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

def validar_documento_fiscal(valor):
    """Comprobación básica de DNI/NIE/CIF español. No sustituye una validación oficial."""
    v = re.sub(r"[^A-Za-z0-9]", "", str(valor or "").upper())
    if not v:
        return False
    if re.fullmatch(r"\d{8}[A-Z]", v):
        letras = "TRWAGMYFPDXBNJZSQVHLCKE"
        return letras[int(v[:8]) % 23] == v[-1]
    if re.fullmatch(r"[XYZ]\d{7}[A-Z]", v):
        pref = {"X": "0", "Y": "1", "Z": "2"}[v[0]]
        letras = "TRWAGMYFPDXBNJZSQVHLCKE"
        return letras[int(pref + v[1:8]) % 23] == v[-1]
    if re.fullmatch(r"[ABCDEFGHJNPQRSUVW]\d{7}[0-9A-J]", v):
        # Control CIF
        pares = sum(int(v[i]) for i in range(2, 8, 2))
        impares = 0
        for i in range(1, 8, 2):
            n = int(v[i]) * 2
            impares += n // 10 + n % 10
        control = (10 - ((pares + impares) % 10)) % 10
        esperado = v[-1]
        if esperado.isdigit():
            return control == int(esperado)
        letras = "JABCDEFGHI"
        return letras[control] == esperado
    return False


def _sb_table_exists(nombre):
    if not SUPABASE_DISPONIBLE:
        return False
    try:
        obtener_cliente_supabase().table(nombre).select("*").limit(1).execute()
        return True
    except Exception:
        return False


def _cargar_curso_por_codigo(codigo):
    if not SUPABASE_DISPONIBLE or not codigo.strip():
        return None
    try:
        rows = obtener_cliente_supabase().table("cursos").select("*").eq("codigo_curso", codigo.strip()).limit(1).execute().data
        return rows[0] if rows else None
    except Exception:
        return None


def _cargar_docentes_curso(codigo):
    if not SUPABASE_DISPONIBLE:
        return []
    try:
        links = obtener_cliente_supabase().table("curso_docente").select("id_docente").eq("codigo_curso", codigo).execute().data
        ids = [x.get("id_docente") for x in links if x.get("id_docente")]
        if not ids:
            return []
        return obtener_cliente_supabase().table("docentes").select("*").in_("id_docente", ids).execute().data
    except Exception:
        return []


def _crear_o_reutilizar_curso(empresa_id, referencia, nombre_curso, nombre_modulo, nivel, horas, competencias, nombre_empresa):
    """
    Relación de catálogo por código de curso.

    Si el código ya existe, se reutiliza exactamente la ficha existente: el
    colaborador NO tiene que volver a introducir la descripción del curso.
    Si no existe, se crea con los datos facilitados.
    """
    cliente = obtener_cliente_supabase()
    curso = _cargar_curso_por_codigo(referencia)
    if curso:
        return curso

    if not nombre_curso.strip():
        return None

    ok = enviar_curso_modulo_supabase(
        empresa_id, nombre_empresa, referencia, nombre_curso, nombre_modulo,
        nivel, horas, competencias
    )
    if not ok:
        return None
    return _cargar_curso_por_codigo(referencia)


def _crear_edicion_curso(empresa_id, referencia, nombre_curso):
    """Crea una nueva edición del curso en curso_ediciones.

    No utiliza .single(), porque la versión del cliente Supabase usada por
    esta aplicación puede no exponer ese método en el builder de inserción.
    """
    cliente = obtener_cliente_supabase()

    if not _sb_table_exists("curso_ediciones"):
        raise RuntimeError(
            "Falta la tabla curso_ediciones. "
            "Ejecuta el SQL de actualización de la base de datos."
        )

    datos_edicion = {
        "empresa_id": empresa_id,
        "codigo_curso": str(referencia).strip(),
        "nombre_curso": str(nombre_curso).strip(),
        "estado": "pendiente",
    }

    resultado = cliente.table("curso_ediciones").insert(datos_edicion).execute()

    if not resultado.data:
        raise RuntimeError("Supabase no devolvió la edición creada.")

    return resultado.data[0]


def _crear_o_reutilizar_docente(empresa_id, nombre, usuario, email, codigo_curso):
    """Busca un docente existente o crea uno nuevo y mantiene curso_docente."""
    cliente = obtener_cliente_supabase()

    nombre = str(nombre).strip()
    usuario = str(usuario).strip()
    email = str(email).strip()
    codigo_curso = str(codigo_curso).strip()

    if not nombre or not usuario or not email:
        raise ValueError("Nombre, usuario y email del docente son obligatorios.")

    existente = (
        cliente.table("docentes")
        .select("*")
        .eq("usuario", usuario)
        .limit(1)
        .execute()
        .data
    )

    if existente:
        docente = existente[0]
        id_docente = docente["id_docente"]
    else:
        id_docente = usuario
        datos_docente = {
            "id_docente": id_docente,
            "nombre": nombre,
            "usuario": usuario,
            "email": email,
            "estado": "pendiente",
            "empresa_id": empresa_id,
        }

        resultado = cliente.table("docentes").insert(datos_docente).execute()

        if not resultado.data:
            raise RuntimeError("Supabase no devolvió el docente creado.")

        docente = resultado.data[0]

    # Mantener la relación histórica del docente con el código del curso.
    if codigo_curso:
        ya = (
            cliente.table("curso_docente")
            .select("id_docente")
            .eq("id_docente", id_docente)
            .eq("codigo_curso", codigo_curso)
            .execute()
            .data
        )
        if not ya:
            cliente.table("curso_docente").insert({
                "id_docente": id_docente,
                "codigo_curso": codigo_curso,
            }).execute()

    return docente


def _vincular_docente_edicion(edition_id, docente_id):
    """Relaciona un docente con una edición concreta."""
    cliente = obtener_cliente_supabase()

    if not _sb_table_exists("curso_edicion_docente"):
        raise RuntimeError(
            "Falta la tabla curso_edicion_docente. "
            "Ejecuta el SQL de actualización de la base de datos."
        )

    ya = (
        cliente.table("curso_edicion_docente")
        .select("id_edicion")
        .eq("id_edicion", edition_id)
        .eq("id_docente", docente_id)
        .execute()
        .data
    )

    if not ya:
        cliente.table("curso_edicion_docente").insert({
            "id_edicion": edition_id,
            "id_docente": docente_id,
        }).execute()


def _anadir_alumno_edicion(edition_id, datos):
    """Añade un alumno a curso_alumnos para una edición concreta.

    IMPORTANTE: la aplicación utiliza curso_alumnos, NO alumnos_cursos.
    """
    cliente = obtener_cliente_supabase()

    if not _sb_table_exists("curso_alumnos"):
        raise RuntimeError(
            "Falta la tabla curso_alumnos. "
            "Ejecuta el SQL de actualización de la base de datos."
        )

    campos_obligatorios = [
        "nombre",
        "apellidos",
        "provincia",
        "localidad",
        "telefono",
        "email",
    ]

    for campo in campos_obligatorios:
        if not str(datos.get(campo, "")).strip():
            raise ValueError(f"El campo '{campo}' del alumno es obligatorio.")

    datos_alumno = {
        "id_edicion": edition_id,
        "nombre": str(datos["nombre"]).strip(),
        "apellidos": str(datos["apellidos"]).strip(),
        "provincia": str(datos["provincia"]).strip(),
        "localidad": str(datos["localidad"]).strip(),
        "telefono": str(datos["telefono"]).strip(),
        "email": str(datos["email"]).strip(),
        "estado": "pendiente",
    }

    resultado = cliente.table("curso_alumnos").insert(datos_alumno).execute()

    if not resultado.data:
        raise RuntimeError("Supabase no devolvió el alumno creado.")

    return resultado.data[0]


def _cargar_ediciones_colaborador(empresa_id):
    if not SUPABASE_DISPONIBLE or not _sb_table_exists("curso_ediciones"):
        return []
    try:
        return (
            obtener_cliente_supabase()
            .table("curso_ediciones")
            .select("*")
            .eq("empresa_id", empresa_id)
            .order("created_at", desc=True)
            .execute()
            .data
        )
    except Exception:
        return []


def _render_formulario_alumno(prefix, version, titulo=None):
    titulo = titulo or ("Añadir alumno" if lang == "es" else "Afegir alumne")
    st.markdown(f"### {titulo}")
    a1, a2 = st.columns(2)
    nombre = a1.text_input(T["campo_nombre_alumno"], key=f"{prefix}_nombre_{version}")
    apellidos = a2.text_input(T["campo_apellidos_alumno"], key=f"{prefix}_apellidos_{version}")
    a3, a4 = st.columns(2)
    provincia = a3.text_input(T["campo_provincia"], key=f"{prefix}_provincia_{version}")
    localidad = a4.text_input(T["campo_localidad"], key=f"{prefix}_localidad_{version}")
    a5, a6 = st.columns(2)
    telefono = a5.text_input(T["campo_telefono"], key=f"{prefix}_telefono_{version}")
    email = a6.text_input(T["campo_email"], key=f"{prefix}_email_{version}")
    return {"nombre": nombre, "apellidos": apellidos, "provincia": provincia, "localidad": localidad, "telefono": telefono, "email": email}


def _alumno_valido(datos):
    return all(str(datos.get(k, "")).strip() for k in ["nombre", "apellidos", "provincia", "localidad", "telefono", "email"])


def _render_colaborador_logueado(empresa_id, nombre_empresa, key_prefix):
    """Gestión de cursos del colaborador.

    - Cada edición/grupo queda relacionada con un código de curso del catálogo.
    - Si el código ya existe, se reutiliza su ficha y sus docentes existentes.
    - En una nueva edición los alumnos siempre deben introducirse de nuevo.
    - Una vez que el docente envía las evaluaciones de esa edición, ésta pasa
      a cerrada y el colaborador ya no puede añadir docentes/alumnos.
    """
    st.markdown(f"## {T['gestion_cursos']}")
    st.caption(
        T["gestion_cursos_desc"]
    )

    tablas_necesarias = ["curso_ediciones", "curso_alumnos", "curso_edicion_docente"]
    faltan_tablas = [t for t in tablas_necesarias if not _sb_table_exists(t)]
    if faltan_tablas:
        st.error(T["campo_tablas_faltan"].format(tablas=", ".join(faltan_tablas)))
        st.info(T["campo_migracion_cursos"])
        return

    tab_crear, tab_mis = st.tabs([T["crear_nuevo_curso"], T["mis_cursos"]])

    # ---------------------------------------------------------------
    # CREAR NUEVA EDICIÓN
    # ---------------------------------------------------------------
    with tab_crear:
        st.markdown(f"### {T['selecciona_curso']}")
        cv = st.session_state.get(f"{key_prefix}_nuevo_version", 0)

        referencia = st.text_input(
            T["campo_referencia_curso"],
            key=f"{key_prefix}_nuevo_ref_{cv}",
            help=T["help_codigo"]
        )

        curso_existente = _cargar_curso_por_codigo(referencia.strip()) if referencia.strip() else None

        if curso_existente:
            nombre_catalogo = curso_existente.get("nombre_es") or curso_existente.get("nombre_ca") or referencia.strip()
            st.success(
                T["curso_existente"].format(ref=referencia.strip(), nombre=nombre_catalogo)
            )
        else:
            st.info(T["codigo_nuevo_info"])
            nombre_curso = st.text_input(
                T["campo_nombre_curso"], key=f"{key_prefix}_nuevo_nombre_{cv}"
            )
            c1, c2 = st.columns(2)
            nombre_modulo = c1.text_input(T["campo_nombre_modulo"], key=f"{key_prefix}_nuevo_modulo_{cv}")
            nivel = c2.text_input(T["nivel_bloque"], key=f"{key_prefix}_nuevo_nivel_{cv}")
            c3, c4 = st.columns(2)
            horas = c3.text_input(T["campo_horas_totales"], key=f"{key_prefix}_nuevo_horas_{cv}")
            competencias = c4.text_area(T["campo_competencias"], key=f"{key_prefix}_nuevo_comp_{cv}")

        # -----------------------------------------------------------
        # DOCENTES
        # -----------------------------------------------------------
        st.markdown(f"### {T['docentes_edicion']}")

        docentes_existentes = _cargar_docentes_curso(referencia.strip()) if curso_existente else []
        docentes_seleccionados = []

        if curso_existente and docentes_existentes:
            st.caption(
                T["docentes_reutilizables"]
            )
            for i, d in enumerate(docentes_existentes):
                nombre_d = d.get("nombre") or d.get("usuario") or T["nombre_docente"]
                usuario_d = d.get("usuario") or ""
                email_d = d.get("email") or ""
                marcado = st.checkbox(
                    f"{nombre_d} · {usuario_d} · {email_d}",
                    value=True,
                    key=f"{key_prefix}_reuse_doc_{referencia.strip()}_{d.get('id_docente', i)}_{cv}"
                )
                if marcado:
                    docentes_seleccionados.append({
                        "id_docente": d.get("id_docente"),
                        "nombre": nombre_d,
                        "usuario": usuario_d,
                        "email": email_d,
                        "existente": True,
                    })
        elif curso_existente:
            st.info(T["sin_docentes_curso"])

        st.markdown(f"#### {T['anadir_docentes_nuevos']}")
        if f"{key_prefix}_draft_docentes" not in st.session_state:
            st.session_state[f"{key_prefix}_draft_docentes"] = []
        docentes_draft = st.session_state[f"{key_prefix}_draft_docentes"]
        dv = st.session_state.get(f"{key_prefix}_docente_draft_version", 0)

        d1, d2, d3 = st.columns(3)
        dn = d1.text_input(T["nombre_docente"], key=f"{key_prefix}_draft_doc_nombre_{dv}")
        du = d2.text_input(T["usuario_docente"], key=f"{key_prefix}_draft_doc_usuario_{dv}")
        de = d3.text_input(T["email_docente"], key=f"{key_prefix}_draft_doc_email_{dv}")
        if st.button(T["anadir_docente_nuevo"], key=f"{key_prefix}_draft_doc_btn_{dv}"):
            if dn.strip() and du.strip() and de.strip():
                docentes_draft.append({"nombre": dn.strip(), "usuario": du.strip(), "email": de.strip()})
                st.session_state[f"{key_prefix}_docente_draft_version"] = dv + 1
                st.rerun()
            else:
                st.warning(T["rellena_docente"])

        for i, d in enumerate(docentes_draft):
            cc1, cc2 = st.columns([0.9, 0.1])
            cc1.write(f"**{d['nombre']}** · {d['usuario']} · {d['email']}")
            if cc2.button("🗑️", key=f"{key_prefix}_draft_doc_del_{i}"):
                docentes_draft.pop(i)
                st.rerun()

        total_docentes = len(docentes_seleccionados) + len(docentes_draft)
        st.caption(T["docentes_tendra"].format(total=total_docentes))

        # -----------------------------------------------------------
        # ALUMNOS: SIEMPRE NUEVOS PARA CADA EDICIÓN
        # -----------------------------------------------------------
        st.markdown(f"### {T['alumnos_edicion']}")
        st.info(
            T["alumnos_info"]
        )

        if f"{key_prefix}_draft_alumnos" not in st.session_state:
            st.session_state[f"{key_prefix}_draft_alumnos"] = []
        alumnos_draft = st.session_state[f"{key_prefix}_draft_alumnos"]
        av = st.session_state.get(f"{key_prefix}_alumno_draft_version", 0)
        datos_alumno = _render_formulario_alumno(f"{key_prefix}_draft_alumno", av)

        if st.button(T["anadir_alumno_edicion"], key=f"{key_prefix}_draft_alu_btn_{av}"):
            if _alumno_valido(datos_alumno):
                alumnos_draft.append({k: v.strip() for k, v in datos_alumno.items()})
                st.session_state[f"{key_prefix}_alumno_draft_version"] = av + 1
                st.rerun()
            else:
                st.warning(T["todos_campos_alumno"])

        for i, a in enumerate(alumnos_draft):
            cc1, cc2 = st.columns([0.9, 0.1])
            cc1.write(
                f"**{a['nombre']} {a['apellidos']}** · "
                f"{a['provincia']} / {a['localidad']} · {a['telefono']} · {a['email']}"
            )
            if cc2.button("🗑️", key=f"{key_prefix}_draft_alu_del_{i}"):
                alumnos_draft.pop(i)
                st.rerun()
 # -----------------------------------------------------------
        # ENVIAR NUEVA EDICIÓN
        # -----------------------------------------------------------
        st.markdown(f"### {T['enviar_peticion_curso']}")
        if st.button(
            T["enviar_peticion_curso_btn"],
            type="primary",
            key=f"{key_prefix}_crear_edicion_btn"
        ):
            if not referencia.strip():
                st.warning(T["indica_codigo"])
            elif not curso_existente and not nombre_curso.strip():
                st.warning(T["codigo_nuevo_nombre"])
            elif total_docentes == 0:
                st.warning(T["al_menos_docente"])
            elif not alumnos_draft:
                st.warning(T["al_menos_alumno"])
            else:
                try:
                    if curso_existente:
                        # Reutilización real: no se vuelve a crear ni modificar el catálogo.
                        curso = curso_existente
                        nombre_edicion = (
                            curso.get("nombre_es")
                            or curso.get("nombre_ca")
                            or referencia.strip()
                        )
                    else:
                        curso = _crear_o_reutilizar_curso(
                            empresa_id,
                            referencia.strip(),
                            nombre_curso.strip(),
                            nombre_modulo.strip(),
                            nivel.strip(),
                            horas.strip(),
                            competencias.strip(),
                            nombre_empresa,
                        )
                        if not curso:
                            raise RuntimeError("No se pudo crear el curso." if lang == "es" else "No s’ha pogut crear el curs.")
                        nombre_edicion = nombre_curso.strip()

                    edicion = _crear_edicion_curso(
                        empresa_id,
                        referencia.strip(),
                        nombre_edicion,
                    )

                    # Docentes ya existentes del mismo código: se reutilizan.
                    for d in docentes_seleccionados:
                        if not d.get("id_docente"):
                            continue
                        _vincular_docente_edicion(edicion["id"], d["id_docente"])

                    # Docentes nuevos: se crean/reutilizan en la tabla de docentes
                    # y se relacionan tanto con el curso catálogo como con la edición.
                    for d in docentes_draft:
                        docente = _crear_o_reutilizar_docente(
                            empresa_id,
                            d["nombre"],
                            d["usuario"],
                            d["email"],
                            referencia.strip(),
                        )
                        _vincular_docente_edicion(edicion["id"], docente["id_docente"])

                    # Los alumnos siempre son propios de esta nueva edición.
                    for a in alumnos_draft:
                        _anadir_alumno_edicion(edicion["id"], a)

                    crear_notificacion(
                        "curso",
                        f"Nueva edición de curso propuesta por {nombre_empresa}: "
                        f"{referencia.strip()} ({len(alumnos_draft)} alumnos, {total_docentes} docentes)"
                    )

                    st.success(
                        T["peticion_curso_ok"]
                    )
                    st.session_state[f"{key_prefix}_draft_docentes"] = []
                    st.session_state[f"{key_prefix}_draft_alumnos"] = []
                    st.session_state[f"{key_prefix}_nuevo_version"] = cv + 1
                    st.session_state[f"{key_prefix}_docente_draft_version"] = 0
                    st.session_state[f"{key_prefix}_alumno_draft_version"] = 0
                    st.rerun()
                except Exception as e:
                    st.error(T["error_peticion_curso"].format(error=e))

    # ---------------------------------------------------------------
    # MIS CURSOS
    # ---------------------------------------------------------------
    with tab_mis:
        ediciones = _cargar_ediciones_colaborador(empresa_id)
        if not ediciones:
            st.info(T["mis_cursos_info"])

        for ed in ediciones:
            eid = ed.get("id")
            estado = (ed.get("estado") or "pendiente").lower()
            cerrado = estado == "cerrado"
            titulo_estado = T["cerrado"] if cerrado else T["abierto"]

            with st.expander(
                f"{ed.get('codigo_curso', '')} · {ed.get('nombre_curso', '')} · {titulo_estado}",
                expanded=False,
            ):
                estado_visible = {
                    "pendiente": T["estado_pendiente"],
                    "activo": T["estado_activo"],
                    "cerrado": T["cerrado"].replace("🔒 ", "").lower(),
                }.get(estado, estado)
                st.write(f"**{T['estado']}** {estado_visible}")

                try:
                    alumnos = (
                        obtener_cliente_supabase()
                        .table("curso_alumnos")
                        .select("*")
                        .eq("id_edicion", eid)
                        .order("created_at")
                        .execute().data
                    )
                except Exception:
                    alumnos = []

                try:
                    links = (
                        obtener_cliente_supabase()
                        .table("curso_edicion_docente")
                        .select("id_docente")
                        .eq("id_edicion", eid)
                        .execute().data
                    )
                    ids = [x.get("id_docente") for x in links if x.get("id_docente")]
                    docentes = (
                        obtener_cliente_supabase()
                        .table("docentes")
                        .select("*")
                        .in_("id_docente", ids)
                        .execute().data
                        if ids else []
                    )
                except Exception:
                    docentes = []

                st.markdown(T["resumen_doc_alu"].format(docentes=len(docentes), alumnos=len(alumnos)))

                st.markdown(f"#### {T['seccion_docentes']}")
                for d in docentes:
                    st.write(
                        f"• {d.get('nombre', '')} — {d.get('email', '')} — {d.get('estado', '')}"
                    )

                st.markdown(f"#### {T['seccion_alumnos']}")
                if alumnos:
                    columnas = [
                        "nombre", "apellidos", "provincia", "localidad", "telefono", "email"
                    ]
                    st.dataframe(
                        pd.DataFrame(alumnos)[columnas],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info(T["sin_alumnos"])

                if not cerrado:
                    st.success(
                        T["edicion_abierta"]
                    )

                    st.markdown(f"### {T['anadir_docente']}")
                    mv = st.session_state.get(f"{key_prefix}_manage_doc_{eid}", 0)
                    m1, m2, m3 = st.columns(3)
                    mn = m1.text_input(T["nombre_docente"], key=f"{key_prefix}_mdn_{eid}_{mv}")
                    mu = m2.text_input(T["usuario"], key=f"{key_prefix}_mdu_{eid}_{mv}")
                    me = m3.text_input(T["email"], key=f"{key_prefix}_mde_{eid}_{mv}")

                    if st.button("➕ " + T["anadir_docente"], key=f"{key_prefix}_mdb_{eid}_{mv}"):
                        if mn.strip() and mu.strip() and me.strip():
                            try:
                                docente = _crear_o_reutilizar_docente(
                                    empresa_id,
                                    mn,
                                    mu,
                                    me,
                                    ed.get("codigo_curso"),
                                )
                                _vincular_docente_edicion(eid, docente["id_docente"])
                                st.session_state[f"{key_prefix}_manage_doc_{eid}"] = mv + 1
                                st.success(T["docente_anadido"])
                                st.rerun()
                            except Exception as e:
                                st.error(T["error_anadir_docente"].format(error=e))
                        else:
                            st.warning(T["rellena_docente"])

                    st.markdown(f"### {T['anadir_alumno']}")
                    mav = st.session_state.get(f"{key_prefix}_manage_alu_{eid}", 0)
                    datos_nuevo = _render_formulario_alumno(
                        f"{key_prefix}_manage_alumno_{eid}", mav
                    )
                    if st.button("➕ " + T["anadir_alumno"], key=f"{key_prefix}_mab_{eid}_{mav}"):
                        if _alumno_valido(datos_nuevo):
                            try:
                                _anadir_alumno_edicion(eid, datos_nuevo)
                                st.session_state[f"{key_prefix}_manage_alu_{eid}"] = mav + 1
                                st.success(T["alumno_anadido"])
                                st.rerun()
                            except Exception as e:
                                st.error(T["error_anadir_alumno"].format(error=e))
                        else:
                            st.warning(T["todos_campos_alumno"])
                else:
                    st.warning(
                        T["edicion_cerrada"]
                    )

# === PLANES ASOCIADOS: BASIC / STANDARD ===
def bloque_seleccion_plan_asociado(key_prefix):
    """Muestra el selector de planes antes del formulario de alta de Asociados."""
    plan_key = f"{key_prefix}_plan_registro"
    if plan_key not in st.session_state:
        st.session_state[plan_key] = None

    if st.session_state.get(plan_key) == "basic":
        st.markdown(
            f"<div style=\"padding:10px 14px;border-radius:10px;background:#eef6ff;border:1px solid #b8d8ff;margin:10px 0 16px 0;\"><b>{T['asoc_reg_plan_seleccionado']}</b></div>",
            unsafe_allow_html=True,
        )
        if st.button(T["asoc_plan_volver"], key=f"{key_prefix}_plan_volver"):
            st.session_state[plan_key] = None
            st.rerun()
        return True

    st.markdown(
        f"<div style=\"margin:10px 0 18px 0;\"><h3 style=\"margin-bottom:4px;\">{T['solicitar_alta']}</h3><p style=\"color:#667085;margin-top:0;\">{T['asoc_plan_subtitulo']}</p></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """<style>
        .asoc-plan-card { border:1px solid #d0d5dd; border-radius:12px; overflow:hidden; background:white; min-height:355px; box-shadow:0 2px 8px rgba(16,24,40,.08); }
        .asoc-plan-head-basic { background:#252525; color:white; padding:10px; text-align:center; font-weight:700; }
        .asoc-plan-head-standard { background:#e6b800; color:white; padding:10px; text-align:center; font-weight:700; }
        .asoc-plan-price { font-size:26px; font-weight:800; text-align:center; padding:14px 8px 8px; color:#111827; }
        .asoc-plan-divider { border-top:2px solid #d0d5dd; margin:4px 20px 10px; }
        .asoc-plan-promo { text-align:center; color:red; font-weight:700; font-size:14px; padding:0 8px 4px; }
        .asoc-plan-list { padding:4px 20px 14px 34px; color:#111827; line-height:1.55; }
        .asoc-plan-list li { margin-bottom:6px; }
        .asoc-plan-disabled { opacity:.78; }
        </style>""", unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"""<div class=\"asoc-plan-card\"><div class=\"asoc-plan-head-basic\">{T['plan_basic']}</div><div class=\"asoc-plan-price\">{T['asoc_plan_basic_precio']}</div><div class=\"asoc-plan-divider\"></div><div class=\"asoc-plan-promo\">{T['asoc_plan_promocion']}</div><ul class=\"asoc-plan-list\"><li>{T['asoc_plan_uso_app']}</li><li>{T['asoc_plan_etiqueta_web']}</li><li>{T['asoc_plan_informe_max']}</li><li>{T['plan_impuestos']}</li></ul></div>""",
            unsafe_allow_html=True,
        )
        if st.button(T["asoc_plan_seleccionar_basic"], key=f"{key_prefix}_plan_basic", type="primary", use_container_width=True):
            st.session_state[plan_key] = "basic"
            st.rerun()

    with c2:
        st.markdown(
            f"""<div class=\"asoc-plan-card asoc-plan-disabled\"><div class=\"asoc-plan-head-standard\">{T['plan_standard']}</div><div class=\"asoc-plan-price\">{T['asoc_plan_standard_precio']}</div><div class=\"asoc-plan-divider\"></div><div class=\"asoc-plan-promo\">{T['asoc_plan_standard_inactivo']}</div><ul class=\"asoc-plan-list\"><li>{T['asoc_plan_uso_app']}</li><li>{T['asoc_plan_etiqueta_web']}</li><li>{T['asoc_plan_informe_mensual']}</li><li>{T['plan_impuestos']}</li></ul></div>""",
            unsafe_allow_html=True,
        )
        st.button(T["asoc_plan_standard_bloqueado"], key=f"{key_prefix}_plan_standard", disabled=True, use_container_width=True)

    return False


def bloque_seleccion_plan_colaborador(key_prefix):
    """Muestra el selector de planes antes del formulario de alta de Colaboradores."""
    plan_key = f"{key_prefix}_plan_registro"
    if plan_key not in st.session_state:
        st.session_state[plan_key] = None

    if st.session_state.get(plan_key) == "basic":
        st.markdown(
            f"<div style=\"padding:10px 14px;border-radius:10px;background:#eef6ff;border:1px solid #b8d8ff;margin:10px 0 16px 0;\"><b>{T['reg_plan_seleccionado']}</b></div>",
            unsafe_allow_html=True,
        )
        if st.button(T["plan_volver"], key=f"{key_prefix}_plan_volver"):
            st.session_state[plan_key] = None
            st.rerun()
        return True

    st.markdown(
        f"<div style=\"margin:10px 0 18px 0;\"><h3 style=\"margin-bottom:4px;\">{T['solicitar_alta']}</h3><p style=\"color:#667085;margin-top:0;\">{T['plan_subtitulo']}</p></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """<style>
        .plan-card { border:1px solid #d0d5dd; border-radius:12px; overflow:hidden; background:white; min-height:315px; box-shadow:0 2px 8px rgba(16,24,40,.08); }
        .plan-head-basic { background:#252525; color:white; padding:10px; text-align:center; font-weight:700; }
        .plan-head-standard { background:#e6b800; color:white; padding:10px; text-align:center; font-weight:700; }
        .plan-price { font-size:26px; font-weight:800; text-align:center; padding:14px 8px 4px; color:#111827; }
        .plan-promo { text-align:center; color:red; font-weight:700; font-size:14px; padding-bottom:6px; }
        .plan-list { padding:4px 20px 14px 34px; color:#111827; line-height:1.6; }
        .plan-list li { margin-bottom:5px; }
        .plan-disabled { opacity:.78; }
        </style>""", unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"""<div class=\"plan-card\"><div class=\"plan-head-basic\">{T['plan_basic']}</div><div class=\"plan-price\">{T['plan_basic_precio']}</div><div class=\"plan-promo\">{T['plan_promocion']}</div><ul class=\"plan-list\"><li>{T['plan_basic_uso_app']}</li><li>{T['plan_etiqueta_web']}</li><li>{T['plan_impuestos']}</li></ul></div>""",
            unsafe_allow_html=True,
        )
        if st.button(T["plan_seleccionar_basic"], key=f"{key_prefix}_plan_basic", type="primary", use_container_width=True):
            st.session_state[plan_key] = "basic"
            st.rerun()

    with c2:
        st.markdown(
            f"""<div class=\"plan-card plan-disabled\"><div class=\"plan-head-standard\">{T['plan_standard']}</div><div class=\"plan-price\">{T['plan_standard_precio']}</div><div class=\"plan-promo\">{T['plan_standard_inactivo']}</div><ul class=\"plan-list\"><li>{T['plan_uso_app']}</li><li>{T['plan_etiqueta_web']}</li><li>{T['plan_impuestos']}</li></ul></div>""",
            unsafe_allow_html=True,
        )
        st.button(T["plan_standard_bloqueado"], key=f"{key_prefix}_plan_standard", disabled=True, use_container_width=True)

    return False


def bloque_acceso_y_peticion(tipo, nombre_hoja_credenciales, key_prefix, incluir_centro_registro=False, usar_supabase=False):
    login_key = f"{key_prefix}_login_ok"
    id_key = f"{key_prefix}_id_empresa"
    nombre_key = f"{key_prefix}_nombre_empresa"
    peticion_version_key = f"{key_prefix}_peticion_version"

    st.markdown("---")

    if not st.session_state.get(login_key):
        usuario_in = st.text_input(T["usuario"], key=f"{key_prefix}_user_in")
        pass_in = st.text_input(T["password"], type="password", key=f"{key_prefix}_pass_in")
        if st.button(T["btn_acceder"], key=f"{key_prefix}_btn_acceder"):
            if usar_supabase:
                fila = verificar_credencial_supabase(usuario_in, pass_in, tipo)
                if fila:
                    st.session_state[login_key] = True
                    st.session_state[id_key] = fila.get("id")
                    st.session_state[nombre_key] = fila.get("nombre_centro") or fila.get("nombre_empresa") or fila.get("usuario", "")
                    st.rerun()
                else:
                    st.error(T["error_acceso_participar"])
            else:
                fila = verificar_credencial_participar(usuario_in, pass_in, nombre_hoja_credenciales)
                if fila:
                    st.session_state[login_key] = True
                    st.session_state[id_key] = str(fila.get("Id. Empresa", "")).strip()
                    st.session_state[nombre_key] = str(fila.get("Nombre Empresa", "")).strip()
                    st.rerun()
                else:
                    st.error(T["error_acceso_participar"])

        if tipo == "colaborador" and usar_supabase:
            mostrar_formulario_registro = bloque_seleccion_plan_colaborador(key_prefix)
            if mostrar_formulario_registro:
                bloque_solicitud_alta(tipo, key_prefix, incluir_centro=incluir_centro_registro, usar_supabase=usar_supabase, mostrar_en_expander=False)
        elif tipo == "asociado":
            mostrar_formulario_registro = bloque_seleccion_plan_asociado(key_prefix)
            if mostrar_formulario_registro:
                bloque_solicitud_alta(tipo, key_prefix, incluir_centro=incluir_centro_registro, usar_supabase=usar_supabase, mostrar_en_expander=False)
        else:
            bloque_solicitud_alta(tipo, key_prefix, incluir_centro=incluir_centro_registro, usar_supabase=usar_supabase)
    else:
        nombre_empresa = st.session_state.get(nombre_key, "")
        id_empresa = st.session_state.get(id_key, "")
        st.success(f"{T['acceso_concedido']} {nombre_empresa}")

        if tipo == "colaborador" and usar_supabase:
            _render_colaborador_logueado(id_empresa, nombre_empresa, key_prefix)
        else:
            version = st.session_state.get(peticion_version_key, 0)
            texto_peticion = st.text_area(T["escribir_peticion"], key=f"{key_prefix}_peticion_{version}")
            if st.button(T["enviar"], key=f"{key_prefix}_btn_enviar"):
                if texto_peticion.strip():
                    enviado = False
                    if usar_supabase and SUPABASE_DISPONIBLE:
                        try:
                            obtener_cliente_supabase().table("peticiones_participar").insert({"id_empresa": id_empresa, "texto": texto_peticion.strip()}).execute()
                            crear_notificacion("peticion", f"Nuevo mensaje de {nombre_empresa} ({tipo}): {texto_peticion.strip()[:200]}")
                            enviado = True
                        except Exception as e:
                            st.error(f"Error al enviar: {e}")
                    else:
                        enviado = enviar_peticion_participar(tipo, id_empresa, texto_peticion.strip())
                    if enviado:
                        st.success(T["peticion_enviada"])
                        st.session_state[peticion_version_key] = version + 1
                        st.rerun()
                    else:
                        st.error(T["error_peticion"])
                else:
                    st.warning(T["campo_vacio_peticion"])

        if st.button(T["cerrar_sesion"], key=f"{key_prefix}_btn_cerrar_sesion"):
            st.session_state[login_key] = False
            st.session_state[id_key] = ""
            st.session_state[nombre_key] = ""
            st.rerun()



if st.session_state.get("acceso_panel"):
    acceso_panel = st.session_state["acceso_panel"]

    # Pantallas independientes: al entrar aquí NO se renderiza el bloque
    # Documentación / Cómo participar. Cada acceso ocupa su propia pantalla.
    st.markdown(
        """<style>
        .access-page {
            padding: 12px 0 24px 0;
        }
        .access-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 4px;
        }
        .access-subtitle {
            color: #667085;
            font-size: 1rem;
            margin-bottom: 22px;
        }
        </style>""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="access-page">', unsafe_allow_html=True)

    if acceso_panel == "asociado":
        st.markdown(f'<div class="access-title">👥 {T["acceso_asociados"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="access-subtitle">Acceso y gestión para Asociados</div>', unsafe_allow_html=True)
        bloque_acceso_y_peticion("asociado", "Credenciales Asociados", "asoc_part")
        if st.button("← Volver a Documentación", key="volver_desde_asociados", use_container_width=False):
            st.session_state["acceso_panel"] = None
            st.rerun()

    elif acceso_panel == "colaborador":
        st.markdown(f'<div class="access-title">🏢 {T["acceso_colaboradores"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="access-subtitle">Acceso y gestión para Colaboradores</div>', unsafe_allow_html=True)
        bloque_acceso_y_peticion(
            "colaborador",
            "Credenciales Colaboradores",
            "colab_part",
            incluir_centro_registro=True,
            usar_supabase=True
        )
        if st.button("← Volver a Documentación", key="volver_desde_colaboradores", use_container_width=False):
            st.session_state["acceso_panel"] = None
            st.rerun()

    elif acceso_panel == "candidato":
        st.markdown(f'<div class="access-title">🎓 {T["acceso_candidatos"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="access-subtitle">Área de acceso para Candidatos</div>', unsafe_allow_html=True)
        st.info("Este acceso estará disponible próximamente.")
        if st.button("← Volver a Documentación", key="volver_desde_candidatos", use_container_width=False):
            st.session_state["acceso_panel"] = None
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

elif opcion == T["menu_docs"]:

    # Estos datos solo hacen falta en esta pestaña, así que se cargan aquí
    # (y solo una vez por sesión) en vez de en cada carga de la app, para no
    # frenar la pestaña de Evaluaciones cuando no se necesitan.
    if 'texto_documentos' not in st.session_state or 'contenido_funcionalidad' not in st.session_state:
        datos_iniciales = cargar_datos_de_google()

        if 'texto_documentos' not in st.session_state:
            st.session_state.texto_documentos = datos_iniciales.get("Información del sistema", "Bienvenido al área de consulta.")

        if 'contenido_funcionalidad' not in st.session_state:
            st.session_state.contenido_funcionalidad = {key: datos_iniciales.get(key, "") for key in ["Argumentos M-Zero", "¿Por qué ser Asociado o Colaborador?", "Metodología M0", "El sello M-Zero 'Certificación de calidad'", "Arguments M-Zero", "Per què ser Associat o Colaborador?", "Metodologia M0", "El segell M-Zero 'Certificació de qualitat'"]}

        if 'contenido_exp' not in st.session_state:
            st.session_state.contenido_exp = {key: datos_iniciales.get(key, "") for key in ["Mecanizado", "Climatización", "Fontanería", "Electricidad", "Obra", "Electromecánica", "Hidráulica", "Construcción Mecánica", "Asociaciones y Gremios"]}

        if 'contenido_contacto' not in st.session_state:
            st.session_state.contenido_contacto = {key: datos_iniciales.get(key, "") for key in ["Móvil / WhatsApp", "Email"]}

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
                        st.markdown(
                            f"<div style='color:#ffffff !important; font-size:1.15rem; font-weight:700; margin:8px 0 18px 0;'>{empresa_html}</div>",
                            unsafe_allow_html=True
                        )

                    if lang == "ca":
                        descripcion = emp.get("descripcion_ca", "").strip() or emp.get("descripcion", "").strip()
                    else:
                        descripcion = emp.get("descripcion", "").strip()
                    if descripcion:
                        st.markdown(descripcion, unsafe_allow_html=True)
                    enlace = emp.get("enlace", "").strip()
                    if enlace:
                        st.markdown(
                            f"<div style='margin-top:14px;'><a href='{enlace}' target='_blank' style='color:#ffffff !important; text-decoration:underline;'>🔗 Visitar web</a></div>",
                            unsafe_allow_html=True
                        )

        def mostrar_bloque_categorias(datos, titulos_por_columna, key_prefix):
            """Pinta los títulos de categoría en columnas (como antes) y,
            al desplegar cada uno, muestra el buscador Provincia/Población/Empresa
            filtrado a esa categoría."""
            columnas = st.columns(len(titulos_por_columna))
            for i, col in enumerate(columnas):
                with col:
                    for titulo in titulos_por_columna[i]:
                        etiqueta_visible = TRADUCCION_CATEGORIAS_CA.get(titulo, titulo) if lang == "ca" else titulo
                        with st.expander(etiqueta_visible):
                            if lang == "ca":
                                # Filtramos por la columna "Sector cat" del Excel,
                                # comparándola con la etiqueta catalana mostrada
                                # (para que coincida, esa celda debe llevar el
                                # mismo texto catalán que ves en el título).
                                objetivo = etiqueta_visible.strip().lower()
                                datos_categoria = [
                                    d for d in datos
                                    if d.get("categoria_ca", "").strip().lower() == objetivo
                                ]
                            else:
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

    # --- ESTILO DE FUNCIONALIDAD Y CONTACTO ---
    # Los títulos "Funcionalidad" y "Contacto" mantienen su color azul.
    # Los desplegables vuelven al aspecto anterior: fondo blanco.
    # El texto interior NO se fuerza a ningún color para respetar
    # los colores que vienen del Excel.
    st.markdown(
        """
        <style>
        .st-key-funcionalidad-contacto div[data-testid="stExpander"],
        .st-key-funcionalidad-contacto div[data-testid="stExpander"] details,
        .st-key-funcionalidad-contacto div[data-testid="stExpander"] summary,
        .st-key-funcionalidad-contacto div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
            background: #ffffff !important;
        }

        .st-key-funcionalidad-contacto div[data-testid="stExpander"] summary,
        .st-key-funcionalidad-contacto div[data-testid="stExpander"] summary p,
        .st-key-funcionalidad-contacto div[data-testid="stExpander"] summary span {
            color: #222222 !important;
        }

        .st-key-funcionalidad-contacto div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
            color: inherit !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.container(key="funcionalidad_contacto"):
        # --- BLOQUE 2: FUNCIONALIDAD ---
        if 'contenido_funcionalidad' not in st.session_state or not st.session_state.contenido_funcionalidad:
            st.session_state.contenido_funcionalidad = cargar_datos_de_google()

        st.markdown(
            f"<h3 style='color: #0066cc;'><b>{T['funcionalidad']}</b></h3>",
            unsafe_allow_html=True
        )
        titulos_func = T["titulos_func"]

        for titulo in titulos_func:
            with st.expander(titulo):
                if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
                    temp_text = st.text_area(
                        f"Editar {titulo}:",
                        value=st.session_state.contenido_funcionalidad.get(titulo, ""),
                        height=150,
                        key=f"input_{titulo}"
                    )

                    if st.button(f"Guardar {titulo}", key=f"btn_save_{titulo}"):
                        st.session_state.contenido_funcionalidad[titulo] = temp_text

                        if guardar_en_sheets(titulo, temp_text):
                            st.success("Guardado en Google y localmente")
                        else:
                            st.warning("Guardado solo localmente (Error en Sheets)")

                        st.rerun()

                # Se mantiene exactamente el contenido/color que llega del Excel.
                st.markdown(
                    st.session_state.contenido_funcionalidad.get(titulo, ""),
                    unsafe_allow_html=True
                )

        # --- BLOQUE 3: CONTACTO ---
        st.markdown(
            f"<h3 style='color: #0066cc;'><b>{T['contacto']}</b></h3>",
            unsafe_allow_html=True
        )
        titulos_cont = ["Móvil / WhatsApp", "Email"]

        for titulo in titulos_cont:
            with st.expander(titulo):
                if st.session_state.autenticado and st.session_state.usuario_actual == "mzerojc":
                    nuevo_cont = st.text_area(
                        f"Editar {titulo}:",
                        value=st.session_state.contenido_contacto.get(titulo, ""),
                        height=70,
                        key=f"cont_{titulo}"
                    )
                    if st.button(f"Guardar {titulo}", key=f"btn_save_cont_{titulo}"):
                        if guardar_en_sheets(titulo, nuevo_cont):
                            st.session_state.contenido_contacto[titulo] = nuevo_cont
                            refrescar_app()

                # También aquí se respeta el color definido en el Excel.
                st.markdown(
                    st.session_state.contenido_contacto.get(titulo, ""),
                    unsafe_allow_html=True
                )

    # --- BLOQUE: CÓMO PARTICIPAR ---
    st.markdown(f"## {T['como_participar']}")

    instrucciones_participar = cargar_instrucciones_participar()

    def texto_instruccion(clave):
        bloque = instrucciones_participar.get(clave, {})
        return bloque.get(lang, "")

    # Los accesos se muestran en pantallas independientes desde el sidebar.

    # ============================================================
    # BLOQUE LEGAL INFERIOR
    # ============================================================
    st.markdown(
        """
        <style>
        .st-key-bloque-legal {
            background: #172033;
            padding: 18px 24px 10px 24px;
            margin-top: 18px;
            margin-bottom: 0;
        }

        .st-key-bloque-legal div[data-testid="stExpander"],
        .st-key-bloque-legal div[data-testid="stExpander"] details,
        .st-key-bloque-legal div[data-testid="stExpander"] summary,
        .st-key-bloque-legal div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
            background: #172033 !important;
            border-color: rgba(255,255,255,0.18) !important;
        }

        .st-key-bloque-legal div[data-testid="stExpander"] summary,
        .st-key-bloque-legal div[data-testid="stExpander"] summary p,
        .st-key-bloque-legal div[data-testid="stExpander"] summary span {
            color: #ffffff !important;
        }

        .mzero-legal-heading {
            color: #ffffff;
            text-align: center;
            font-size: 18px;
            font-weight: 700;
            padding-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.container(key="bloque_legal"):
        st.markdown(
            f"<div class='mzero-legal-heading'>{T['legal_titulo']}</div>",
            unsafe_allow_html=True
        )

        # Cerrados al cargar. El usuario solo ve el título hasta que clica.
        with st.expander(T["aviso_legal"], expanded=False):
            st.markdown(f"**{T['legal_nombre_comercial']}**")
            st.markdown(f"**{T['legal_responsable']}**")
            st.markdown(f"**{T['legal_nif']}**")
            st.markdown(f"**{T['legal_domicilio']}**")
            st.markdown(f"**{T['legal_email']}**")
            st.write(T["legal_aviso_texto"])

        with st.expander(T["politica_privacidad"], expanded=False):
            st.markdown("### Responsable del tratamiento")
            st.write(f"{T['legal_responsable']}. {T['legal_email']}")
            st.markdown("### Finalidades")
            st.write(T["legal_privacidad_texto"])
            st.markdown("### Derechos")
            st.write(T["legal_derechos_texto"])
            st.markdown("### Actualización")
            st.write(T["legal_actualizacion"])

        with st.expander(T["politica_cookies"], expanded=False):
            st.write(T["legal_cookies_texto"])
            st.write(T["legal_actualizacion"])

elif opcion == T["menu_eval"]:
    if 'envio_resultado' in st.session_state:
        tipo_msg, texto_msg = st.session_state.pop('envio_resultado')
        if tipo_msg == "success":
            st.success(texto_msg)
        else:
            st.error(texto_msg)

    if not SUPABASE_DISPONIBLE:
        st.warning("Añade 'supabase' a requirements.txt para poder acceder a Evaluaciones.")
    else:
        cliente_sb = obtener_cliente_supabase()

        # --- NUEVO: login real de docente (usuario/contraseña contra Supabase) ---
        # Sustituye al antiguo campo "Id Docente" de texto libre, que no
        # verificaba nada. Este acceso es independiente del login del sidebar.
        if not st.session_state.get("docente_login_ok"):
            st.subheader(T["acceso_docente"])
            cd1, cd2 = st.columns(2)
            usuario_docente_input = cd1.text_input(T["usuario_docente"], key="docente_user_in")
            pass_docente_input = cd2.text_input(T["password"], type="password", key="docente_pass_in")
            if st.button(T["btn_acceder"], key="docente_btn_acceder"):
                try:
                    resultado = (
                        cliente_sb.table("docentes").select("*")
                        .eq("usuario", usuario_docente_input.strip())
                        .eq("contrasena", pass_docente_input.strip())
                        .eq("estado", "activo")
                        .execute()
                    )
                    if resultado.data:
                        st.session_state.docente_login_ok = True
                        st.session_state.docente_info = resultado.data[0]
                        st.rerun()
                    else:
                        st.error(T["error_acceso_participar"])
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
        else:
            docente_info = st.session_state.docente_info
            nombre_docente = docente_info.get("nombre") or docente_info.get("usuario")

            col_bienv, col_cerrar = st.columns([0.8, 0.2])
            col_bienv.success(f"{T['acceso_concedido']} {nombre_docente}")
            if col_cerrar.button(T["cerrar_sesion"], key="docente_btn_cerrar"):
                st.session_state.docente_login_ok = False
                st.session_state.docente_info = None
                st.rerun()

            # --- Cursos asignados a este docente (vía curso_docente) ---
            try:
                filas_curso_docente = (
                    cliente_sb.table("curso_docente").select("codigo_curso")
                    .eq("id_docente", docente_info["id_docente"]).execute().data
                )
                codigos_permitidos = [f["codigo_curso"] for f in filas_curso_docente]
                cursos_permitidos = []
                if codigos_permitidos:
                    cursos_permitidos = (
                        cliente_sb.table("cursos").select("*")
                        .in_("codigo_curso", codigos_permitidos)
                        .eq("estado", "activo")
                        .execute().data
                    )
            except Exception as e:
                st.error(f"Error al cargar tus cursos: {e}")
                cursos_permitidos = []

            curso_seleccionado_full = None
            curso_codigo_actual = None
            modulo_seleccionado_full = None
            modulo_codigo_actual = None
            modulos_filtrados = []
            nivel = ""
            alumno = ""
            edition_id_actual = None
            alumnos_edicion = []

            if not cursos_permitidos:
                st.info(T["aviso_sin_cursos_docente"])
            else:
                c2, c3 = st.columns(2)

                campo_nombre_curso = "nombre_ca" if lang == "ca" else "nombre_es"
                opciones_cursos_display = [f"{c['codigo_curso']} - {c.get(campo_nombre_curso) or c.get('nombre_es') or ''}" for c in cursos_permitidos]
                curso_seleccionado_full = c2.selectbox(T["curso"], opciones_cursos_display, key=f"f_cur_{st.session_state.reset_todo}")
                curso_codigo_actual = curso_seleccionado_full.split(" - ")[0] if " - " in curso_seleccionado_full else curso_seleccionado_full

                # Si el colaborador ha creado ediciones/grupos, el docente entra en
                # la edición concreta y recibe automáticamente el listado de alumnos.
                ediciones_docente = []
                if _sb_table_exists("curso_ediciones") and _sb_table_exists("curso_edicion_docente"):
                    try:
                        links_ed = cliente_sb.table("curso_edicion_docente").select("id_edicion").eq("id_docente", docente_info["id_docente"]).execute().data
                        ids_ed = [x.get("id_edicion") for x in links_ed if x.get("id_edicion")]
                        if ids_ed:
                            ediciones_docente = (cliente_sb.table("curso_ediciones").select("*")
                                                 .in_("id", ids_ed).eq("codigo_curso", curso_codigo_actual)
                                                 .neq("estado", "cerrado").execute().data)
                    except Exception:
                        ediciones_docente = []

                if ediciones_docente:
                    # El UUID de la edición es un identificador interno y NO se muestra
                    # al docente. Si solo existe un grupo, se selecciona automáticamente.
                    if len(ediciones_docente) == 1:
                        edicion_actual = ediciones_docente[0]
                        edition_id_actual = edicion_actual.get("id")
                    else:
                        ed1, _ = st.columns([0.45, 0.55])
                        opciones_ed = []
                        mapa_ediciones = {}

                        for indice_ed, ed in enumerate(ediciones_docente, start=1):
                            estado_ed = str(ed.get("estado", "pendiente")).strip().lower()
                            estado_visible = "Cerrado" if estado_ed == "cerrado" else "Activo"
                            etiqueta = f"Grupo {indice_ed:02d} · {estado_visible}"
                            opciones_ed.append(etiqueta)
                            mapa_ediciones[etiqueta] = ed

                        edicion_display = ed1.selectbox(
                            "Grupo",
                            opciones_ed,
                            key=f"f_ed_{st.session_state.reset_todo}"
                        )
                        edition_id_actual = mapa_ediciones[edicion_display].get("id")

                    try:
                        alumnos_edicion = (
                            cliente_sb.table("curso_alumnos")
                            .select("*")
                            .eq("id_edicion", edition_id_actual)
                            .order("created_at")
                            .execute()
                            .data
                        )
                    except Exception:
                        alumnos_edicion = []

                try:
                    modulos_filtrados = (
                        cliente_sb.table("modulos").select("*")
                        .eq("codigo_curso", curso_codigo_actual)
                        .eq("estado", "activo")
                        .execute().data
                    )
                except Exception as e:
                    st.error(f"Error al cargar los módulos: {e}")
                    modulos_filtrados = []

                campo_descripcion_modulo = "descripcion_ca" if lang == "ca" else "descripcion_es"
                opciones_modulos_display = [f"{m['subcodigo']} - {m.get(campo_descripcion_modulo) or m.get('descripcion_es') or ''}" for m in modulos_filtrados] if modulos_filtrados else ["Selecciona un curso válido"]
                modulo_seleccionado_full = c3.selectbox(T["modulo"], opciones_modulos_display, key=f"f_mod_{st.session_state.reset_todo}")
                modulo_codigo_actual = modulo_seleccionado_full.split(" - ")[0] if " - " in modulo_seleccionado_full else modulo_seleccionado_full

                nivel_sugerido = ""
                for m in modulos_filtrados:
                    if m["subcodigo"] == modulo_codigo_actual:
                        nivel_sugerido = str(m.get("nivel_bloque", ""))
                        break

                c4, c5 = st.columns(2)
                nivel = c4.text_input(T["nivel_bloque"], value=nivel_sugerido, key=f"f_niv_{st.session_state.reset_todo}")
                if alumnos_edicion:
                    opciones_alumnos = [f"{_alumno_ref_corta(a.get('id'))} · {a.get('nombre', '')} {a.get('apellidos', '')}" for a in alumnos_edicion]
                    alumno_display = c5.selectbox(T["alumno"], opciones_alumnos, key=f"f_alu_sel_{st.session_state.reset_todo}")
                    alumno = alumno_display.split(" · ", 1)[1] if " · " in alumno_display else alumno_display
                else:
                    alumno = c5.text_input(T["alumno"], key=f"f_alu_{st.session_state.alumno_key}")

            if curso_codigo_actual is not None:
                criterios = [
                    "1. Tasa de eficiencia", "2. Precisión geométrica y mecánica", "3. Autonomía ejecutiva",
                    "4. Índice de mermas", "5. Mantenimiento de utillaje y entorno", "6. Factor de desempeño temporal",
                    "7. Resolución escenarios de prácticas", "8. Resolución escenarios de averías",
                    "9. Precisión conceptual y terminología", "10. Seguridad y normativas",
                    "11. Fiabilidad y compromiso operativo", "12. Capacidad de aprendizaje",
                    "13. Comunicación y respeto al superior"
                ]

                # --- NUEVO: traducción SOLO VISUAL de las cabeceras de la tabla resumen ---
                traduccion_columnas_ca = TRADUCCION_EVAL_CA

                descripciones_rubrica = cargar_rubrica()

                st.subheader(T["subt_puntuacion"])

                # Solo el bloque de criterios se ejecuta al cambiar una puntuación.
                # Así cada clic NO vuelve a ejecutar el resto de la aplicación ni
                # repite las consultas lentas a Supabase.
                @st.fragment
                def _bloque_criterios_evaluacion():
                    cols = st.columns(4)
                    resultado_key = f"resultado_eval_{st.session_state.alumno_key}"
                    if resultado_key not in st.session_state:
                        st.session_state[resultado_key] = None

                    def _limpiar_resultado():
                        st.session_state[resultado_key] = None

                    def _mostrar_resultado_al_marcar_13():
                        valores = {
                            crit: st.session_state.get(f"rad_{crit}_{st.session_state.alumno_key}")
                            for crit in criterios
                        }
                        if None not in valores.values() and alumno:
                            nota = round(
                                sum((valores[c] - 1) * 2.5 for c in criterios)
                                / len(criterios),
                                1
                            )
                            estado = (
                                "SUSPENSO (Línea Roja)"
                                if valores["10. Seguridad y normativas"] == 1
                                else ("APROBADO" if nota >= 5 else "SUSPENSO")
                            )
                            st.session_state[resultado_key] = (nota, estado)

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
                                        st.markdown(
                                            f"**{T['que_se_mide']}**\n\n"
                                            f"{info_crit['que_se_mide']}"
                                        )
                                        st.markdown("---")
                                        st.markdown(f"**{T['nivel_rubrica']}**")
                                        st.markdown(info_crit["nivel_rubrica"])

                                st.radio(
                                    "p", [1, 2, 3, 4, 5], horizontal=True,
                                    key=f"rad_{crit}_{st.session_state.alumno_key}",
                                    index=None, label_visibility="collapsed",
                                    on_change=_mostrar_resultado_al_marcar_13 if i == 12 else _limpiar_resultado
                                )

                    if st.session_state[resultado_key] is not None:
                        nota, estado = st.session_state[resultado_key]
                        st.metric(T["nota_final"], f"{nota} - {estado}")

                _bloque_criterios_evaluacion()

                resultado_eval_key = f"resultado_eval_{st.session_state.alumno_key}"
                if st.session_state.get(resultado_eval_key) is not None:
                    nota_final, res = st.session_state[resultado_eval_key]
                else:
                    nota_final, res = None, None

                guardar_evaluacion = st.button(
                    T["guardar_alumno"],
                    type="primary",
                    use_container_width=False
                )

                if guardar_evaluacion:
                    if nota_final is None:
                        st.warning(
                            "Debes seleccionar una puntuación del 1 al 5 "
                            "en los 13 criterios antes de guardar."
                        )
                    elif not alumno:
                        st.warning("Debes seleccionar un alumno antes de guardar.")
                    else:
                        registro = {
                            "Alumno": alumno,
                            "AlumnoId": next((a.get("id") for a in alumnos_edicion if f"{_alumno_ref_corta(a.get('id'))} · {a.get('nombre', '')} {a.get('apellidos', '')}" == alumno_display), None) if alumnos_edicion else None,
                            "Profesor": nombre_docente,
                            "Usuario": docente_info.get("usuario", ""),
                            "Curso": curso_seleccionado_full,
                            "CursoCodigo": curso_codigo_actual,
                            "Modulo": modulo_codigo_actual,
                            "Nivel": nivel,
                            "Nota": nota_final,
                            "Estado": res,
                            "EditionId": edition_id_actual
                        }
                        registro.update({crit: st.session_state.get(f"rad_{crit}_{st.session_state.alumno_key}") for crit in criterios})
                        st.session_state.lista_alumnos = [
                            r for r in st.session_state.lista_alumnos
                            if r.get("Alumno") != alumno
                        ]
                        st.session_state.lista_alumnos.append(registro)
                        st.session_state.alumno_key += 1
                        st.rerun()
                
                if st.session_state.lista_alumnos:
                    st.subheader(T["resumen_alumnos"])
                    df_resumen = pd.DataFrame(st.session_state.lista_alumnos).drop(columns=["CursoCodigo", "AlumnoId"], errors="ignore")
                    if st.session_state.lista_alumnos and any(r.get("AlumnoId") for r in st.session_state.lista_alumnos):
                        df_resumen.insert(0, "Ref. alumno", [_alumno_ref_corta(r.get("AlumnoId")) for r in st.session_state.lista_alumnos])
                    if "EditionId" in df_resumen.columns:
                        df_resumen["EditionId"] = df_resumen["EditionId"].apply(_edition_ref_corta)
                    if lang == "ca":
                        df_resumen = df_resumen.rename(columns=traduccion_columnas_ca)
                    st.table(df_resumen)

                    with st.expander(T["gestionar_alumnos"]):
                        for i, reg in enumerate(st.session_state.lista_alumnos):
                            if st.button(f"🗑️ Eliminar a {reg['Alumno']}", key=f"del_{i}"):
                                st.session_state.lista_alumnos.pop(i)
                                st.rerun()

                    if FPDF_DISPONIBLE:
                        pdf_bytes = generar_pdf_resumen(st.session_state.lista_alumnos, lang=lang)
                        st.download_button(
                            label=T["descargar_pdf"],
                            data=pdf_bytes,
                            file_name="resumen_evaluaciones.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.info(T["fpdf_no_disponible"])

                    if st.button(T["enviar_sheets"], type="primary"):
                        try:
                            # Para las nuevas ediciones, el envío final solo se permite
                            # cuando TODOS los alumnos de la clase han sido evaluados.
                            if edition_id_actual and alumnos_edicion:
                                alumnos_clase = {f"{a.get('nombre', '')} {a.get('apellidos', '')}".strip() for a in alumnos_edicion}
                                alumnos_evaluados = {str(r.get("Alumno", "")).strip() for r in st.session_state.lista_alumnos if r.get("EditionId") == edition_id_actual}
                                faltan = sorted(alumnos_clase - alumnos_evaluados)
                                if faltan:
                                    st.warning("No se puede cerrar el curso todavía. Faltan por evaluar: " + ", ".join(faltan))
                                    st.stop()

                            filas_supabase = []
                            for reg in st.session_state.lista_alumnos:
                                fila = {
                                    "fecha": date.today().isoformat(),
                                    "usuario": reg.get("Usuario", ""),
                                    "alumno": reg.get("Alumno", ""),
                                    "profesor": reg.get("Profesor", ""),
                                    "codigo_curso": reg.get("CursoCodigo", ""),
                                    "subcodigo": reg.get("Modulo", ""),
                                    "nivel": reg.get("Nivel", ""),
                                    "nota": reg.get("Nota"),
                                    "estado": reg.get("Estado", "")
                                }
                                if reg.get("EditionId"):
                                    fila["edition_id"] = reg.get("EditionId")
                                for idx_crit, crit in enumerate(criterios, start=1):
                                    fila[f"crit_{idx_crit}"] = reg.get(crit)
                                filas_supabase.append(fila)

                            # Si la base todavía no tiene edition_id, conservamos la
                            # inserción antigua para no romper instalaciones existentes.
                            try:
                                cliente_sb.table("evaluaciones").insert(filas_supabase).execute()
                            except Exception:
                                filas_sin_edition = [{k: v for k, v in f.items() if k != "edition_id"} for f in filas_supabase]
                                cliente_sb.table("evaluaciones").insert(filas_sin_edition).execute()

                            if edition_id_actual and _sb_table_exists("curso_ediciones"):
                                cliente_sb.table("curso_ediciones").update({
                                    "estado": "cerrado",
                                    "bloqueado": True,
                                    "cerrado_at": date.today().isoformat()
                                }).eq("id", edition_id_actual).execute()

                            st.session_state.envio_resultado = ("success", T["exito_envio"] + (" El curso ha quedado cerrado y ya no admite cambios." if edition_id_actual else ""))
                            st.session_state.lista_alumnos = []
                            st.session_state.reset_todo += 1
                            st.rerun()
                        except Exception as e:
                            st.session_state.envio_resultado = ("error", f"Error al guardar en la base de datos: {e}")
                            st.rerun()
