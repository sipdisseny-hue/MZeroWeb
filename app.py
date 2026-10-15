)

                if guardar_evaluacion:
                    if nota_final is None:
                        st.warning(T["aviso_puntuaciones_evaluacion"])
                    elif not alumno:
                        st.warning(T["aviso_selecciona_alumno"])
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
                                    st.warning(T["aviso_faltan_evaluaciones"].format(alumnos=", ".join(faltan)))
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
