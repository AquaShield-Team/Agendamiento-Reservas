# -*- coding: utf-8 -*-
"""Defectos inyectados: cada uno se aplica a una COPIA de la fuente y tiene que
hacer fallar las pruebas que nombra. El corredor exige que el texto 'viejo'
aparezca exactamente una vez y que toda prueba de la suite tenga al menos una
mutación. Ninguna mutación tiene efecto real si el arnés falla: las que tocan
red, procesos o navegador apuntan a destinos inertes (127.0.0.1:9, 192.0.2.1,
un 'cmd /c rem')."""

ARNES = "test_arnes.TestArnes."
CAND = "test_candado.TestCandado."
LANZ = "test_candado.TestLanzadores."
FIN_CANDADO = ('            _avisar_llave_config(valor)\n    except Exception:\n        pass\n    return False\n\n\n'
               'def _avisar_llave_config')
AVISO_PANEL = '    try:\n        _wlog(texto)\n    except Exception:\n        pass'
AVISO_CONSOLA = '    try:\n        print(texto, flush=True)\n    except Exception:\n        pass\n    try:\n        _wlog(texto)'
LLAVE_OTRA = CAND + "test_llave_config_con_otro_valor_no_abre_y_avisa"
LLAVE_LOG = CAND + "test_aviso_va_al_log_de_la_corrida"
LLAVE_WEB = "test_web.TestPanelRutas.test_llave_invalida_se_avisa_en_pantalla"

MUTACIONES = [
    # --- Arnés: importar no tiene efectos ---
    dict(id="importar-abre-navegador", pruebas=[ARNES + "test_importar_no_dispara_efectos"],
         viejo='VERSION = "2026.09.10"',
         nuevo='VERSION = "2026.09.10"; __import__("webbrowser").open("http://127.0.0.1:9/")'),
    dict(id="importar-lanza-proceso", pruebas=[ARNES + "test_importar_no_dispara_efectos"],
         viejo='VERSION = "2026.09.10"',
         nuevo='VERSION = "2026.09.10"; __import__("subprocess").Popen(["cmd.exe", "/c", "rem"])'),
    dict(id="importar-conecta-afuera", pruebas=[ARNES + "test_importar_no_dispara_efectos"],
         viejo='VERSION = "2026.09.10"',
         nuevo='VERSION = "2026.09.10"; __import__("socket").create_connection(("192.0.2.1", 80), 0.2)'),
    dict(id="importar-lanza-hilo", pruebas=[ARNES + "test_importar_no_dispara_efectos"],
         viejo='VERSION = "2026.09.10"',
         nuevo='VERSION = "2026.09.10"; __import__("threading").Thread(target=__import__("time").sleep, '
               'args=(3,), daemon=True).start()'),
    dict(id="importar-escribe-archivo", pruebas=[ARNES + "test_importar_no_dispara_efectos"],
         viejo='LOGS = BASE / "logs"',
         nuevo='LOGS = BASE / "logs"; (BASE / "creado_al_importar.txt").write_text("x")'),
    dict(id="perfiles-fuera-de-base", pruebas=[ARNES + "test_rutas_de_trabajo_dentro_de_la_sandbox"],
         viejo='PERFILES = BASE / "perfiles"',
         nuevo='PERFILES = Path(os.environ.get("TEMP", ".")) / "perfiles_mutante"'),
    dict(id="planilla-fuera-de-base", pruebas=[ARNES + "test_rutas_de_trabajo_dentro_de_la_sandbox"],
         viejo='    return BASE / "Reservas AQUASHIELD.xlsx"',
         nuevo='    return BASE.parent / "Reservas AQUASHIELD.xlsx"'),
    # --- Candado ---
    dict(id="candado-abierto-por-defecto",
         pruebas=[ARNES + "test_candado_cerrado_al_cargar", CAND + "test_tres_apagadas_nunca_emite"],
         viejo=FIN_CANDADO, nuevo=FIN_CANDADO.replace("    return False\n", "    return True\n")),
    dict(id="candado-abre-si-falla-config", pruebas=[ARNES + "test_candado_cerrado_sin_config"],
         viejo=FIN_CANDADO, nuevo=FIN_CANDADO.replace("        pass\n", "        return True\n")),
    dict(id="entorno-acepta-no", pruebas=[CAND + "test_tres_apagadas_nunca_emite"],
         viejo='("1", "true", "si", "yes")', nuevo='("1", "true", "si", "yes", "no")'),
    dict(id="entorno-sin-yes", pruebas=[CAND + "test_llave_entorno_sola_abre"],
         viejo='("1", "true", "si", "yes")', nuevo='("1", "true", "si")'),
    dict(id="entorno-no-abre",
         pruebas=[CAND + "test_basta_una_llave_de_tres", CAND + "test_llave_entorno_sola_abre"],
         viejo='in ("1", "true", "si", "yes"):\n        return True',
         nuevo='in ("1", "true", "si", "yes"):\n        pass'),
    dict(id="argumento-sin-guiones", pruebas=[CAND + "test_llave_argumento_sola_abre"],
         viejo='("emitir", "--emitir", "produccion", "--produccion")',
         nuevo='("emitir", "produccion", "--produccion")'),
    dict(id="config-otra-clave",
         pruebas=[CAND + "test_llave_config_abre_solo_con_true", CAND + "test_basta_una_llave_de_tres"],
         viejo='.get("emitir_reservas", False)', nuevo='.get("emitir_reserva", False)'),
    # --- La llave de config abre solo con el booleano true, y lo demás avisa ---
    dict(id="config-abre-con-cualquier-verdadero", pruebas=[LLAVE_OTRA],
         viejo='        if valor is True:\n            return True', nuevo='        if valor:\n            return True'),
    dict(id="config-sin-aviso", pruebas=[LLAVE_OTRA, LLAVE_LOG, LLAVE_WEB],
         viejo='        if valor is not False:\n            _avisar_llave_config(valor)',
         nuevo='        if False:\n            _avisar_llave_config(valor)'),
    dict(id="config-avisa-tambien-con-false", pruebas=[CAND + "test_llave_config_abre_solo_con_true"],
         viejo='        if valor is not False:\n            _avisar_llave_config(valor)',
         nuevo='        if True:\n            _avisar_llave_config(valor)'),
    dict(id="aviso-otro-texto", pruebas=[LLAVE_OTRA, LLAVE_WEB],
         viejo='y solo se abre con true (sin comillas). "', nuevo='y solo abre con true. "'),
    dict(id="aviso-sin-consola", pruebas=[LLAVE_OTRA],
         viejo=AVISO_CONSOLA, nuevo=AVISO_CONSOLA.replace("print(texto, flush=True)", "pass")),
    dict(id="aviso-sin-panel", pruebas=[LLAVE_OTRA, LLAVE_WEB],
         viejo=AVISO_PANEL, nuevo='    pass'),
    dict(id="aviso-no-va-a-la-corrida", pruebas=[LLAVE_LOG],
         viejo='    if abiertos:\n        for reg in abiertos:', nuevo='    if False:\n        for reg in abiertos:'),
    dict(id="registro-no-se-anota", pruebas=[LLAVE_LOG],
         viejo='        _REGISTROS_ABIERTOS.add(self)', nuevo='        pass'),
    dict(id="registro-cerrado-sigue-anotado", pruebas=[LLAVE_LOG],
         viejo='        _REGISTROS_ABIERTOS.discard(self)', nuevo='        pass'),
    dict(id="panel-no-consulta-candado", pruebas=[CAND + "test_llamadas_al_candado"],
         viejo='"modo_emision": es_modo_emision(),', nuevo='"modo_emision": False,'),
    dict(id="guarda-one-invertida", pruebas=[CAND + "test_guarda_one"],
         viejo='        if not es_modo_emision():\n            reg.paso("Me DETENGO en Review Booking',
         nuevo='        if es_modo_emision():\n            reg.paso("Me DETENGO en Review Booking'),
    dict(id="guarda-msc-invertida", pruebas=[CAND + "test_guarda_msc"],
         viejo='    if not es_modo_emision():\n        reg.paso("Me DETENGO en Summary',
         nuevo='    if es_modo_emision():\n        reg.paso("Me DETENGO en Summary'),
    dict(id="guarda-cosco-invertida", pruebas=[CAND + "test_guarda_cosco"],
         viejo='    if not es_modo_emision():\n        reg.paso("Me DETENGO en Booking Details',
         nuevo='    if es_modo_emision():\n        reg.paso("Me DETENGO en Booking Details'),
    dict(id="guarda-hyundai-invertida", pruebas=[CAND + "test_guarda_hyundai"],
         viejo='    if not es_modo_emision():\n        reg.paso("Me DETENGO en Review & Book',
         nuevo='    if es_modo_emision():\n        reg.paso("Me DETENGO en Review & Book'),
    dict(id="guarda-maersk-invertida", pruebas=[CAND + "test_guarda_maersk"],
         viejo='    if not es_modo_emision():\n        reg.paso("Me DETENGO en Review booking',
         nuevo='    if es_modo_emision():\n        reg.paso("Me DETENGO en Review booking'),
    dict(id="guarda-cma-invertida", pruebas=[CAND + "test_guarda_cma"],
         viejo="        if not es_modo_emision():\n            reg.paso(\"Me DETENGO en 'Envío",
         nuevo="        if es_modo_emision():\n            reg.paso(\"Me DETENGO en 'Envío"),
    # --- Lanzadores ---
    dict(id="lanzador-emision-no-enciende", archivo="AQUASHIELD_EMISION.py",
         pruebas=[LANZ + "test_lanzador_de_emision_abre_el_candado"],
         viejo='os.environ["AQUASHIELD_EMITIR"] = "1"', nuevo='os.environ["AQUASHIELD_EMITIR"] = "0"'),
    dict(id="programa-enciende-al-importar", pruebas=[LANZ + "test_programa_solo_no_abre_el_candado"],
         viejo='VERSION = "2026.09.10"',
         nuevo='VERSION = "2026.09.10"; os.environ["AQUASHIELD_EMITIR"] = "1"'),
    dict(id="bat-seguro-lanza-emision", archivo="Iniciar AQUASHIELD.bat",
         pruebas=[LANZ + "test_bat_seguro_lanza_el_programa"],
         viejo='pythonw "AQUASHIELD.py"', nuevo='pythonw "AQUASHIELD_EMISION.py"'),
    dict(id="bat-emision-lanza-seguro", archivo="Iniciar AQUASHIELD_EMISION.bat",
         pruebas=[LANZ + "test_bat_emision_lanza_el_lanzador_de_emision"],
         viejo='pythonw "AQUASHIELD_EMISION.py"', nuevo='pythonw "AQUASHIELD.py"'),
]

# --- Encargo 39 · commit 1: los lanzadores instalan holidays si falta, sin frenar el arranque sin red
# (CICLO-maersk-cuatro-puntos.md) ---
HOLIDAYS_BAT = ('python -c "import holidays" 2>nul || python -m pip install --user --disable-pip-version-check '
                '--timeout 5 --retries 0 holidays')
LANZ_BAT = "test_consola.TestLanzadores.test_instalan_holidays_sin_frenar_el_arranque"

MUTACIONES += [
    dict(id="bat-sin-holidays", archivo="Iniciar AQUASHIELD.bat", pruebas=[LANZ_BAT],
         viejo=HOLIDAYS_BAT + "\n", nuevo=""),
    dict(id="bat-emision-sin-holidays", archivo="Iniciar AQUASHIELD_EMISION.bat", pruebas=[LANZ_BAT],
         viejo=HOLIDAYS_BAT + "\n", nuevo=""),
    dict(id="bat-holidays-sin-limites", archivo="Iniciar AQUASHIELD.bat", pruebas=[LANZ_BAT],
         viejo=" --timeout 5 --retries 0 holidays", nuevo=" holidays"),
    dict(id="bat-holidays-frena", archivo="Iniciar AQUASHIELD_EMISION.bat", pruebas=[LANZ_BAT],
         viejo=HOLIDAYS_BAT + "\n", nuevo=HOLIDAYS_BAT + "\npause\n"),
    dict(id="bat-holidays-despues-del-panel", archivo="Iniciar AQUASHIELD.bat", pruebas=[LANZ_BAT],
         viejo=HOLIDAYS_BAT + '\n\nREM Abre el panel (sin ventana negra de consola)\n'
               'start "" pythonw "AQUASHIELD.py"\n',
         nuevo='REM Abre el panel (sin ventana negra de consola)\nstart "" pythonw "AQUASHIELD.py"\n\n' + HOLIDAYS_BAT
               + "\n"),
]

# --- Planilla: lectores y escritura ---
CON = "test_planilla.TestLectorConsola."
WEBL = "test_planilla.TestLectorWeb."
DIF = "test_planilla.TestDiferencias.test_diferencias_entre_lectores"
ESC = "test_planilla.TestEscritura."
FIN_ESCRIBIR = ('    except Exception as e:\n        raise ErrorEscritura(f"error inesperado al escribir en «{ruta.name}» '
                '({type(e).__name__}: {e})") from e')
ER_ = "test_consola.TestEjecutarReservas."
HOJAS_DESCARGA = "    hojas_a_procesar = [hoja] if hoja in wb.sheetnames else []"
PL_ = "test_web.TestPanelPlanilla."

MUTACIONES += [
    # Sin «ONE» en la lista, cambia el destino final de la 7. Hasta f68ce6c mordía también la trampa de título, por la
    # nave que la F le daba; desde CICLO-cola-seis-items.md la F ya no da la nave.
    dict(id="consola-sin-regla-one", pruebas=[CON + "test_consola_one", DIF],
         viejo='["MSC", "ONE", "FA", "JULIETTE", "LEILA", "VIVIENNE"]',
         nuevo='["MSC", "FA", "JULIETTE", "LEILA", "VIVIENNE"]'),
    dict(id="consola-msc-no-completa-descarga", pruebas=[CON + "test_consola_msc", DIF],
         viejo='dest_orig = val_d', nuevo='dest_orig = ""'),
    dict(id="consola-acepta-nave-con-coma", pruebas=[CON + "test_consola_cma", DIF],
         viejo='not any(c in nave for c in [",", ";"])', nuevo='not any(c in nave for c in [";"])'),
    dict(id="consola-sin-columna-nave",
         pruebas=[CON + "test_consola_cosco", CON + "test_consola_hyundai", CON + "test_consola_maersk"],
         viejo='elif "nave" in v or "buque" in v or "vessel" in v:', nuevo='elif "buque" in v or "vessel" in v:'),
    dict(id="consola-otro-contenedor", pruebas=[CON + "test_consola_one"],
         viejo='if col_map.get("tipo") else "40 HC REEFER"', nuevo='if col_map.get("tipo") else "20 DRY"'),
    dict(id="consola-no-filtra-notas", pruebas=[CON + "test_consola_one", DIF],
         viejo='"elegir siempre"', nuevo='"elegir nunca"'),
    dict(id="consola-encabezado-desde-fila-3", pruebas=[CON + "test_consola_trampa_de_titulo"],
         viejo='for r in range(1, min(ws.max_row + 1, 9)):', nuevo='for r in range(3, min(ws.max_row + 1, 9)):'),
    dict(id="consola-sin-archivo-otro-error", pruebas=[CON + "test_consola_sin_archivo"],
         viejo='raise FileNotFoundError(f"Falta el archivo Excel', nuevo='raise ValueError(f"Falta el archivo Excel'),
    dict(id="consola-hoja-faltante-vacia", pruebas=[CON + "test_consola_hoja_faltante"],
         viejo="raise ValueError(f\"La planilla no tiene la hoja para '{naviera_clave}' (buscados: {aliases}).\")",
         nuevo="return []"),
    dict(id="prioridad-de-archivos", pruebas=[CON + "test_encontrar_archivo_prioridad"],
         viejo='("Reservas AQUASHIELD.xlsx", "Planilla_Estandar_AQUASHIELD.xlsx", "Agendamientos.xlsx")',
         nuevo='("Agendamientos.xlsx", "Planilla_Estandar_AQUASHIELD.xlsx", "Reservas AQUASHIELD.xlsx")'),
    dict(id="web-conserva-completar", pruebas=[WEBL + "test_web_one", DIF],
         viejo='"completar" in nave.lower()', nuevo='"xcompletarx" in nave.lower()'),
    dict(id="web-no-salta-encabezado-repetido", pruebas=[WEBL + "test_web_msc", DIF],
         viejo='if pol.lower().startswith("pto") or nave.lower() == "nave":', nuevo='if False:'),
    dict(id="web-no-salta-filas-vacias", pruebas=[WEBL + "test_web_one"],
         viejo='if not pol and not nave:', nuevo='if False:'),
    dict(id="web-sin-destino-final",
         pruebas=[WEBL + "test_web_consolidado", WEBL + "test_web_cma", WEBL + "test_web_cosco",
                  WEBL + "test_web_hyundai", WEBL + "test_web_maersk"],
         viejo='("destino_final", ("destino final",)),', nuevo=''),
    dict(id="web-sin-columna-naviera", pruebas=[WEBL + "test_web_consolidado"],
         viejo='("naviera",       ("naviera", "linea", "carrier")),', nuevo=''),
    dict(id="web-otro-nombre-de-numero", pruebas=[WEBL + "test_web_one"],
         viejo='("reserva_emitida", (', nuevo='("reserva_emit", ('),
    dict(id="web-primer-encabezado-que-aparezca", pruebas=[WEBL + "test_web_trampa_de_titulo"],
         viejo='if len(cabec) > mejor_n:', nuevo='if len(cabec) > mejor_n and not mejor_n:'),
    dict(id="web-sin-temp", pruebas=[WEBL + "test_web_hyundai"],
         viejo='"temp": val("temp"),', nuevo=''),
    dict(id="web-sin-campo-naviera", pruebas=[WEBL + "test_web_maersk", DIF],
         viejo='"naviera": val("naviera"),', nuevo=''),
    dict(id="escribir-columna-corrida",
         pruebas=[ESC + "test_consola_escribe_sobre_la_planilla", ESC + "test_consola_cosco_usa_estado_robot"],
         viejo='ws.cell(fila, col_estado, estado)', nuevo='ws.cell(fila, col_estado + 1, estado)'),
    dict(id="escribir-guarda-en-otra-parte", pruebas=[ESC + "test_consola_escribe_sobre_la_planilla"],
         viejo="wb.save(ruta)", nuevo='wb.save(str(ruta) + ".copia.xlsx")'),
    dict(id="escribir-calla-sin-archivo", pruebas=[ESC + "test_consola_error_de_escritura_se_levanta"],
         viejo='raise ErrorEscritura(f"no encontré «{ruta.name}» junto al programa") from e', nuevo="return"),
    dict(id="escribir-calla-hoja-faltante", pruebas=[ESC + "test_consola_errores_de_escritura_en_espanol"],
         viejo='raise ErrorEscritura(f"«{ruta.name}» no tiene la hoja de', nuevo='return (f"«{ruta.name}» no tiene la hoja de'),
    dict(id="escribir-sin-encabezados-sigue", pruebas=[ESC + "test_consola_errores_de_escritura_en_espanol"],
         viejo='raise ErrorEscritura(f"no encontré la fila de encabezados en la hoja «{ws.title}»")', nuevo="fila_h = 4"),
    dict(id="escribir-calla-lo-inesperado", pruebas=[ESC + "test_consola_errores_de_escritura_en_espanol"],
         viejo=FIN_ESCRIBIR, nuevo=FIN_ESCRIBIR.split("\n")[0] + "\n        return"),
    dict(id="escribir-permiso-sin-traducir", pruebas=[ER_ + "test_error_de_escritura_se_muestra_y_queda_en_el_log"],
         viejo="    except PermissionError as e:\n", nuevo="    except () as e:\n"),
    dict(id="escribir-otro-encabezado", pruebas=[ESC + "test_consola_sin_columna_estado_crea_una"],
         viejo='ws.cell(fila_h, col, "Estado (Robot)")', nuevo='ws.cell(fila_h, col, "Estado")'),
    dict(id="escribir-otra-columna-nueva",
         pruebas=[ESC + "test_consola_sin_columna_estado_crea_una", ESC + "test_consola_columna_nueva_no_depende_de_max_column"],
         viejo='col = max(ultima + 1, COL_ESTADO_MINIMA)', nuevo='col = max(ultima + 1, COL_ESTADO_MINIMA + 1)'),
    dict(id="escribir-columna-por-max-column", pruebas=[ESC + "test_consola_columna_nueva_no_depende_de_max_column"],
         viejo='col = max(ultima + 1, COL_ESTADO_MINIMA)', nuevo='col = max(ws.max_column + 1, COL_ESTADO_MINIMA)'),
    dict(id="escribir-sin-piso-en-la-m",
         pruebas=[ESC + "test_consola_sin_columna_estado_crea_una", ESC + "test_consola_columna_nueva_no_depende_de_max_column"],
         viejo='col = max(ultima + 1, COL_ESTADO_MINIMA)', nuevo='col = ultima + 1'),
    dict(id="escribir-encabezado-en-la-fila-4", pruebas=[ESC + "test_consola_encabezado_en_otra_fila"],
         viejo='    fila_h, cols = _mapear(ws)\n', nuevo='    fila_h, cols = 4, _mapear(ws)[1]\n'),
    # El defecto tal cual era hasta d86fbca: el bucle crea celdas y corre max_column (cae en la P).
    dict(id="escribir-vuelve-el-corrimiento-a-la-p",
         pruebas=[ESC + "test_consola_sin_columna_estado_crea_una", ESC + "test_consola_columna_nueva_no_depende_de_max_column"],
         viejo='    ultima = max((c.column for c in ws[fila_h] if _txt(c.value)), default=0)\n'
               '    col = max(ultima + 1, COL_ESTADO_MINIMA)\n',
         nuevo='    for r in range(1, 7):\n        for c in range(1, min(ws.max_column + 2, 35)):\n'
               '            ws.cell(r, c)\n'
               '    col = max(ws.max_column + 1, COL_ESTADO_MINIMA)\n'),
    # El defecto tal cual era hasta 4f5f355: espejar en CONSOLIDADO con los números de fila de la hoja.
    dict(id="descarga-espeja-en-consolidado", pruebas=[ESC + "test_web_descarga_es_copia_y_solo_escribe_la_hoja_corrida"],
         viejo=HOJAS_DESCARGA,
         nuevo=HOJAS_DESCARGA + '\n    if "CONSOLIDADO" in wb.sheetnames and "CONSOLIDADO" not in hojas_a_procesar:\n'
                                '        hojas_a_procesar.append("CONSOLIDADO")'),
    dict(id="descarga-hoja-ausente-va-a-la-primera", pruebas=[ESC + "test_web_descarga_de_hoja_que_no_esta_no_escribe"],
         viejo=HOJAS_DESCARGA, nuevo=HOJAS_DESCARGA.replace("else []", "else wb.sheetnames[:1]")),
    dict(id="descarga-consolidado-reparte-a-las-hojas",
         pruebas=[ESC + "test_web_descarga_de_consolidado_solo_escribe_consolidado"],
         viejo=HOJAS_DESCARGA, nuevo=HOJAS_DESCARGA.replace("[hoja] if", 'list(wb.sheetnames) if hoja == "CONSOLIDADO" else [hoja] if')),
    # El defecto tal cual era hasta 0242321: cada fila calla su error.
    dict(id="descarga-calla-el-error-de-la-fila",
         pruebas=[ESC + "test_web_descarga_avisa_lo_que_no_escribe", PL_ + "test_descarga_avisa_en_pantalla_y_en_el_log"],
         viejo='                no_escritos.append((fila_str, f"error inesperado ({type(e).__name__}: {e})", r))',
         nuevo="                pass"),
    dict(id="descarga-hoja-ausente-sin-aviso", pruebas=[ESC + "test_web_descarga_avisa_lo_que_no_escribe"],
         viejo="    if resultados and not hojas_a_procesar:\n", nuevo="    if False:\n"),
    dict(id="descarga-sin-encabezados-sin-aviso", pruebas=[ESC + "test_web_descarga_avisa_lo_que_no_escribe"],
         viejo='            no_escritos += [(f, f"no encontré la fila de encabezados en la hoja «{h_nom}»", r)\n'
               '                            for f, r in (resultados or {}).items()]\n',
         nuevo=''),
    dict(id="descarga-no-avisa-al-final", pruebas=[ESC + "test_web_descarga_avisa_lo_que_no_escribe"],
         viejo="    if no_escritos:\n        _avisar_descarga(no_escritos)\n", nuevo=""),
    dict(id="descarga-aviso-sin-resultado",
         pruebas=[ESC + "test_web_descarga_avisa_lo_que_no_escribe", PL_ + "test_descarga_avisa_en_pantalla_y_en_el_log"],
         viejo='f"{motivo}. Anótalo a mano: {texto[:300]}")', nuevo='f"{motivo}. Anótalo a mano.")'),
    dict(id="descarga-aviso-sin-resumen",
         pruebas=[ESC + "test_web_descarga_avisa_lo_que_no_escribe", PL_ + "test_descarga_avisa_en_pantalla_y_en_el_log"],
         viejo='    lineas.append(f"⚠ {len(no_escritos)} resultado(s)', nuevo='    (f"⚠ {len(no_escritos)} resultado(s)'),
    dict(id="descarga-aviso-sin-log",
         pruebas=[ESC + "test_web_descarga_avisa_lo_que_no_escribe", PL_ + "test_descarga_avisa_en_pantalla_y_en_el_log"],
         viejo="    if carpeta:\n        reg = Registro(", nuevo="    if False:\n        reg = Registro("),
    dict(id="descarga-aviso-sin-pantalla",
         pruebas=[ESC + "test_web_descarga_avisa_lo_que_no_escribe", PL_ + "test_descarga_avisa_en_pantalla_y_en_el_log"],
         viejo='reg = Registro(Path(carpeta) / "log.txt", on_log=_wlog)', nuevo='reg = Registro(Path(carpeta) / "log.txt")'),
    dict(id="descarga-sin-corrida-calla", pruebas=[ESC + "test_web_descarga_avisa_lo_que_no_escribe"],
         viejo="                pass\n            _wlog(linea)", nuevo="                pass"),
    dict(id="descarga-otro-texto-emitida",
         pruebas=[ESC + "test_web_descarga_es_copia_y_solo_escribe_la_hoja_corrida", ESC + "test_web_descarga_crea_columna_de_numero"],
         viejo='txt_est = "EMITIDA" if (st == "EMITIDA" and bkg) else',
         nuevo='txt_est = "EMITIDA!" if (st == "EMITIDA" and bkg) else'),
    dict(id="descarga-toca-el-archivo", pruebas=[ESC + "test_web_descarga_es_copia_y_solo_escribe_la_hoja_corrida"],
         viejo='    wb.save(buf)\n    return buf.getvalue()', nuevo='    wb.save(ruta)\n    wb.save(buf)\n    return buf.getvalue()'),
    dict(id="descarga-otro-encabezado-de-numero", pruebas=[ESC + "test_web_descarga_crea_columna_de_numero"],
         viejo='c_hdr = ws.cell(fila_enc, col_num, "N° de reserva emitida")',
         nuevo='c_hdr = ws.cell(fila_enc, col_num, "N° reserva")'),
]

# --- Número de booking, ayudantes por naviera y registro ---
LI = "test_booking.TestNumeroLimpio."
AY = "test_ayudantes."
RG = "test_registro.TestRegistro."
FIN_ROBOT = '"restring", "restricted"]):\n            return True\n    except Exception:\n        pass\n    return False'
TE = "test_booking.TestNumeroTrasEnvio."
FORMA_ONE = '    "one": r"(?i:Booking\\s+Reference\\s+No\\.?)\\s*:?\\s*(SCLG\\d{8})\\b",'
FORMA_MSC = '    "msc": r"(?i:Your\\s+eBooking\\s+number\\s+is)\\s*:?\\s*(EBKG\\d{8})\\b",'

MUTACIONES += [
    # --- ONE: la forma medida y la lectura tras el envío (CICLO-numero-booking.md) ---
    dict(id="one-forma-sin-etiqueta", pruebas=[TE + "test_forma_medida_de_one"],
         viejo=FORMA_ONE, nuevo='    "one": r"(SCLG\\d{8})\\b",'),
    dict(id="one-forma-otros-digitos", pruebas=[TE + "test_forma_medida_de_one"],
         viejo=FORMA_ONE, nuevo=FORMA_ONE.replace(r"(SCLG\d{8})", r"(SCLG\d{7,9})")),
    dict(id="one-forma-otro-prefijo", pruebas=[TE + "test_forma_medida_de_one"],
         viejo=FORMA_ONE, nuevo=FORMA_ONE.replace(r"(SCLG\d{8})", r"([A-Z]{4}\d{8})")),
    dict(id="one-forma-sin-limite", pruebas=[TE + "test_forma_medida_de_one"],
         viejo=FORMA_ONE, nuevo=FORMA_ONE.replace(r"(SCLG\d{8})\b", r"(SCLG\d{8})")),
    dict(id="one-numero-sin-caja", pruebas=[TE + "test_forma_medida_de_one"],
         viejo=FORMA_ONE, nuevo=FORMA_ONE.replace(r"(SCLG\d{8})", r"((?i:SCLG)\d{8})")),
    dict(id="one-etiqueta-con-caja", pruebas=[TE + "test_forma_medida_de_one"],
         viejo=FORMA_ONE, nuevo=FORMA_ONE.replace(r"(?i:Booking\s+Reference\s+No\.?)", r"Booking\s+Reference\s+No\.?")),
    dict(id="lectura-naviera-sin-forma-igual-busca", pruebas=[TE + "test_naviera_sin_forma_medida_no_lee"],
         viejo="    patron = FORMA_BOOKING.get(naviera)\n",
         nuevo='    patron = FORMA_BOOKING.get(naviera, r"(SCLG\\d{8})")\n'),
    dict(id="lectura-solo-la-pagina", pruebas=[TE + "test_lee_los_marcos", TE + "test_un_marco_que_falla_no_tapa_a_los_demas"],
         viejo='for alcance in [page] + [f for f in (getattr(page, "frames", None) or []) if f is not page]:',
         nuevo="for alcance in [page]:"),
    dict(id="lectura-sin-reintentos", pruebas=[TE + "test_reintenta_hasta_que_aparece"],
         viejo="    for intento in range(espera + 1):", nuevo="    for intento in range(1):"),
    dict(id="lectura-otra-espera", pruebas=[TE + "test_sin_numero_espera_lo_justo"],
         viejo="BKG_ESPERA_SEG = 15", nuevo="BKG_ESPERA_SEG = 10"),
    dict(id="lectura-marco-que-falla-corta", pruebas=[TE + "test_un_marco_que_falla_no_tapa_a_los_demas"],
         viejo="                continue                   # un marco", nuevo='                return ""                   # un marco'),
    dict(id="lectura-sin-shadow", pruebas=[TE + "test_reintenta_hasta_que_aparece"],
         viejo="            if (e.shadowRoot) {\n", nuevo="            if (false) {\n"),
    dict(id="msc-forma-sin-etiqueta", pruebas=[TE + "test_forma_medida_de_msc"],
         viejo=FORMA_MSC, nuevo='    "msc": r"(EBKG\\d{8})\\b",'),
    dict(id="msc-forma-otros-digitos", pruebas=[TE + "test_forma_medida_de_msc"],
         viejo=FORMA_MSC, nuevo=FORMA_MSC.replace(r"(EBKG\d{8})", r"(EBKG\d{7,9})")),
    dict(id="msc-forma-otro-prefijo", pruebas=[TE + "test_forma_medida_de_msc"],
         viejo=FORMA_MSC, nuevo=FORMA_MSC.replace(r"(EBKG\d{8})", r"([A-Z]{4}\d{8})")),
    dict(id="msc-forma-sin-limite", pruebas=[TE + "test_forma_medida_de_msc"],
         viejo=FORMA_MSC, nuevo=FORMA_MSC.replace(r"(EBKG\d{8})\b", r"(EBKG\d{8})")),
    dict(id="msc-numero-sin-caja", pruebas=[TE + "test_forma_medida_de_msc"],
         viejo=FORMA_MSC, nuevo=FORMA_MSC.replace(r"(EBKG\d{8})", r"((?i:EBKG)\d{8})")),
    dict(id="msc-etiqueta-con-caja", pruebas=[TE + "test_forma_medida_de_msc"],
         viejo=FORMA_MSC, nuevo=FORMA_MSC.replace(r"(?i:Your\s+eBooking\s+number\s+is)", r"Your\s+eBooking\s+number\s+is")),
    dict(id="limpio-ignora-campo-booking", pruebas=[LI + "test_campo_booking_manda"],
         viejo='if bkg and bkg.upper() not in (', nuevo='if False and bkg.upper() not in ('),
    dict(id="limpio-sin-27", pruebas=[LI + "test_patrones_por_naviera"],
         viejo=r'm = _re.search(r"\b(27\d{7})\b", det)', nuevo=r'm = _re.search(r"\b(28\d{7})\b", det)'),
    dict(id="limpio-acepta-palabras-cortas", pruebas=[LI + "test_sin_numero"],
         viejo=r'(?:Bkg|Booking|Reference(?:\s*No\.?)?)[:\s]+([A-Z0-9]{6,18})',
         nuevo=r'(?:Bkg|Booking|Reference(?:\s*No\.?)?)[:\s]+([A-Z0-9]{3,18})'),
    dict(id="limpio-descarta-templates", pruebas=[LI + "test_templates_pasa_como_numero"],
         viejo='if c.upper() not in ("EN PROCESO"', nuevo='if c.upper() not in ("TEMPLATES", "EN PROCESO"'),
    dict(id="contrato-one-sin-usa", pruebas=[AY + "TestONE.test_contrato_one"],
         viejo='es_usa = any(x in d for x in ["UNITED STATES", "USA",',
         nuevo='es_usa = any(x in d for x in ["UNITED STATES", "XUSAX",'),
    dict(id="contrato-one-otros-usa-el-general", pruebas=[AY + "TestONE.test_contrato_one"],
         viejo='return creds.get("contrato_otros") or', nuevo='return creds.get("contrato_otros") or creds.get("contrato") or'),
    # Desde el encargo 25, MSC busca desde hoy (CICLO-proxima-salida.md): la que cambiaba el margen de 2 días pasa a
    # devolver el «hoy + 18» de antes.
    dict(id="msc-desde-vuelve-el-18", pruebas=[AY + "TestMSC.test_desde_msc"],
         viejo='    return _desde(reserva, ("dia_carga", "dia_retiro"))\n',
         nuevo='    return _desde(reserva, ("dia_carga", "dia_retiro")) + datetime.timedelta(days=18)\n'),
    dict(id="maersk-fecha-otro-siglo", pruebas=[AY + "TestFechas.test_fecha_maersk"],
         viejo='a = 2000 + a if a < 100 else a', nuevo='a = 1900 + a if a < 100 else a'),
    dict(id="maersk-otro-cliente-por-defecto", pruebas=[AY + "TestMAERSK.test_cliente_maersk"],
         viejo='or "AQUACHILE S.A.")', nuevo='or "AQUACHILE")'),
    dict(id="cosco-resumen-otro-separador", pruebas=[AY + "TestCOSCO.test_resumen_cosco"],
         viejo='partes.append("servicio " + " + ".join(serv))', nuevo='partes.append("servicio " + " / ".join(serv))'),
    dict(id="cosco-control-conserva-guion", pruebas=[AY + "TestCOSCO.test_normalizar_control"],
         viejo='for ch in [",", ".", ":", ";", "*", "-", "_", "/", "(", ")"]:',
         nuevo='for ch in [",", ".", ":", ";", "*", "_", "/", "(", ")"]:'),
    dict(id="puzzle-otro-metodo", pruebas=[AY + "TestCOSCO.test_puzzle_cosco_encuentra_el_hueco"],
         viejo='cv2.TM_CCOEFF_NORMED', nuevo='cv2.TM_SQDIFF_NORMED'),
    dict(id="puzzle-no-ve-la-pieza", pruebas=[AY + "TestCOSCO.test_puzzle_cosco_encuentra_el_hueco"],
         viejo='alpha > 80', nuevo='alpha > 300'),
    dict(id="puzzle-otro-valor-sin-pieza", pruebas=[AY + "TestCOSCO.test_puzzle_cosco_sin_pieza"],
         viejo='return 150, 0, orig_gw', nuevo='return 0, 0, orig_gw'),
    dict(id="robot-no-mira-url", pruebas=[AY + "TestCMA.test_robotcheck_cma"],
         viejo='if "captcha-delivery.com" in u or "datadome" in u:', nuevo='if "datadome" in u:'),
    dict(id="robot-no-mira-iframes", pruebas=[AY + "TestCMA.test_robotcheck_cma"],
         viejo='hay_ifr = bool(page.evaluate(', nuevo='hay_ifr = False and bool(page.evaluate('),
    dict(id="robot-pagina-que-falla-revienta", pruebas=[AY + "TestCMA.test_robotcheck_cma_pagina_que_falla"],
         viejo=FIN_ROBOT, nuevo=FIN_ROBOT.replace("        pass\n", "        raise\n")),
    dict(id="reefer-otra-temperatura", pruebas=[AY + "TestReefer.test_temperatura_reefer"],
         viejo='TEMP_REEFER = "-20"', nuevo='TEMP_REEFER = "-19"'),
    dict(id="reefer-ignora-la-constante", pruebas=[AY + "TestReefer.test_temperatura_reefer"],
         viejo='.strip() or _temperatura_reefer()', nuevo='.strip() or "-18"'),
    dict(id="registro-sin-login-maersk", pruebas=[RG + "test_navieras_y_reservadores"],
         viejo='"maersk":  ("MAERSK",  login_maersk),', nuevo=''),
    dict(id="registro-sin-reservador-maersk", pruebas=[RG + "test_navieras_y_reservadores"],
         viejo='"maersk": reservar_maersk,', nuevo=''),
    dict(id="registro-worker-sin-maersk", pruebas=[RG + "test_secuencia_del_worker_web"],
         viejo='navs_secuencia = ["one", "msc", "cma", "cosco", "hyundai", "maersk"]',
         nuevo='navs_secuencia = ["one", "msc", "cma", "cosco", "hyundai"]'),
    dict(id="registro-alias-cma-sin-espacio", pruebas=[RG + "test_hoja_a_naviera"],
         viejo='"cma":     ["CMA-CGM", "CMA CGM", "CMA"],', nuevo='"cma":     ["CMA-CGM", "CMA"],'),
    dict(id="registro-sin-hoja-general", pruebas=[RG + "test_hoja_a_naviera"],
         viejo='if h_clean in ("consolidado", "todas", "general"):', nuevo='if h_clean in ("consolidado", "todas"):'),
    dict(id="registro-hmm-no-es-hyundai", pruebas=[RG + "test_texto_a_naviera"],
         viejo='if "hyundai" in t or "hmm" in t: return "hyundai"', nuevo='if "hyundai" in t: return "hyundai"'),
    dict(id="registro-one-exacto", pruebas=[RG + "test_texto_a_naviera"],
         viejo='if "one" in t: return "one"', nuevo='if "one" == t: return "one"'),
]

# --- Panel web ---
RU = "test_web.TestPanelRutas."
CR = "test_web.TestPanelCredenciales."
PL = "test_web.TestPanelPlanilla."
SP = "test_web.TestPanelSinPlanilla."
CO = "test_web.TestPanelCorridas."
AR = "test_web.TestArranqueDelPanel."

MUTACIONES += [
    dict(id="web-js-como-texto", pruebas=[RU + "test_recursos_del_panel"],
         viejo='return self._env(200, "application/javascript; charset=utf-8", JS_INDEX)',
         nuevo='return self._env(200, "text/plain; charset=utf-8", JS_INDEX)'),
    dict(id="web-404-otro-texto", pruebas=[RU + "test_recursos_del_panel"],
         viejo='            self._env(404, "text/plain; charset=utf-8", "no existe")\n\n        # ---------------- POST',
         nuevo='            self._env(404, "text/plain; charset=utf-8", "nada")\n\n        # ---------------- POST'),
    dict(id="web-config-sin-reservadores", pruebas=[RU + "test_config_del_panel"],
         viejo='"reserva": k in RESERVADORES}', nuevo='"reserva": False}'),
    dict(id="web-config-ausente-otro-aviso", pruebas=[RU + "test_config_ausente_da_500"],
         viejo='raise FileNotFoundError("No existe config.json (copia config.example.json y pon tus credenciales).")',
         nuevo='raise FileNotFoundError("Falta la configuración.")'),
    dict(id="web-ruta-renombrada",
         pruebas=[RU + "test_rutas_del_js_existen_en_el_servidor", PL + "test_descarga_de_resultados"],
         viejo='if u.path == "/api/descargar":', nuevo='if u.path == "/api/descargas":'),
    dict(id="cred-expone-la-clave", pruebas=[CR + "test_credenciales_nunca_devuelven_la_clave"],
         viejo='"tiene_clave": bool((datos.get(k) or {}).get("clave"))}',
         nuevo='"tiene_clave": bool((datos.get(k) or {}).get("clave")), '
               '"guardada": (datos.get(k) or {}).get("clave")}'),
    dict(id="cred-operador-nace-incompleto", pruebas=[CR + "test_guardar_credenciales"],
         viejo='dest.setdefault(k, {"usuario": "", "clave": "", "contrato": ""})',
         nuevo='dest.setdefault("one", {"usuario": "", "clave": "", "contrato": ""})'),
    dict(id="cred-vacio-no-borra", pruebas=[CR + "test_guardar_credenciales"],
         viejo='if nueva is not None:', nuevo='if nueva:'),
    dict(id="cred-no-reemplaza-el-archivo", pruebas=[CR + "test_guardar_credenciales"],
         viejo='_reemplazar(tmp, ruta)', nuevo='_reemplazar(tmp, ruta) if False else None'),
    dict(id="planilla-otro-temporal", pruebas=[PL + "test_planilla_subida_va_al_temporal_con_nombre_fijo"],
         viejo='dest = _os.path.join(tempfile.gettempdir(), "aquashield_planilla.xlsx")',
         nuevo='dest = _os.path.join(tempfile.gettempdir(), "aquashield_planilla2.xlsx")'),
    dict(id="planilla-cuenta-mal", pruebas=[PL + "test_planilla_subida_va_al_temporal_con_nombre_fijo"],
         viejo='out.append({"hoja": h, "filas": len(filas),', nuevo='out.append({"hoja": h, "filas": len(filas) + 1,'),
    dict(id="filas-hoja-inexistente", pruebas=[PL + "test_filas_de_una_hoja"],
         viejo='    if hoja not in wb.sheetnames:\n        return []',
         nuevo='    if hoja not in wb.sheetnames:\n        return [{"fila": 0}]'),
    dict(id="descarga-otro-nombre", pruebas=[PL + "test_descarga_de_resultados"],
         viejo="f'attachment; filename=\"{nom} - resultados {marca}.xlsx\"'",
         nuevo="f'attachment; filename=\"{nom}-resultados {marca}.xlsx\"'"),
    dict(id="descarga-sin-planilla-404", pruebas=[SP + "test_descarga_sin_planilla"],
         viejo='return self._env(400, "text/plain; charset=utf-8", "No hay planilla cargada.")',
         nuevo='return self._env(404, "text/plain; charset=utf-8", "No hay planilla cargada.")'),
    dict(id="correr-otro-rechazo", pruebas=[CO + "test_correr_rechazos"],
         viejo='return self._json({"error": "ya hay una corrida en curso"}, 409)',
         nuevo='return self._json({"error": "ya hay una corrida en curso"}, 400)'),
    dict(id="worker-perfil-compartido", pruebas=[CO + "test_corrida_de_una_hoja"],
         viejo='perfil = PERFILES / usuario', nuevo='perfil = PERFILES / "comun"'),
    dict(id="worker-sin-numero-limpio", pruebas=[CO + "test_corrida_de_una_hoja"],
         viejo='bkg_limpio = _extraer_bkg_limpio({"estado": estado, "detalle": detalle})', nuevo='bkg_limpio = ""'),
    dict(id='worker-sin-filas-entra-igual', pruebas=[CO + "test_corrida_sin_filas_no_abre_el_navegador"],
         viejo='            if not sub_elegidas:\n                continue\n',
         nuevo=''),
    dict(id='worker-sin-filas-no-avisa', pruebas=[CO + "test_corrida_sin_filas_no_abre_el_navegador"],
         viejo='        if not elegidas:\n            # Hasta 42247d4',
         nuevo='        if False:\n            # Hasta 42247d4'),
    dict(id="consolidado-procesa-lineas-ajenas", pruebas=[CO + "test_consolidado_reparte_por_naviera"],
         viejo='sub_elegidas = [f for f in elegidas if _match_nav_key(f.get("naviera")) == nav]',
         nuevo='sub_elegidas = [f for f in elegidas if _match_nav_key(f.get("naviera")) in (nav, None)]'),
    dict(id="login-fallido-reserva-igual", pruebas=[CO + "test_login_fallido_no_reserva"],
         viejo='                if not logueado:\n                    reg.paso(f"No se pudo iniciar sesión en {nombre}; no proceso sus reservas.")',
         nuevo='                if False:\n                    reg.paso(f"No se pudo iniciar sesión en {nombre}; no proceso sus reservas.")'),
    dict(id="revienta-otra-captura", pruebas=[CO + "test_reservador_que_revienta"],
         viejo='try: reg.captura(page, f"error_{nav}_rsv_{i}")', nuevo='try: reg.captura(page, f"error_{nav}_fila_{i}")'),
    dict(id="pausa-otro-aviso", pruebas=[CO + "test_pausa_y_continuar"],
         viejo='_westado("Te toca a ti: resuelve el paso en el navegador")', nuevo='_westado("Pausa.")'),
    dict(id="continuar-no-libera", pruebas=[CO + "test_pausa_y_continuar"],
         viejo='                    if _WEB["pausa"]:\n                        _WEB["pausa"].set()\n                    return self._json({"ok": True})',
         nuevo='                    if _WEB["pausa"]:\n                        _WEB["pausa"].is_set()\n                    return self._json({"ok": True})'),
    dict(id="detener-no-corta-las-filas", pruebas=[CO + "test_detener"],
         viejo='                    for i, rsv in enumerate(sub_elegidas, start=1):\n                        if _WEB["detener"] and _WEB["detener"].is_set():',
         nuevo='                    for i, rsv in enumerate(sub_elegidas, start=1):\n                        if False:'),
    dict(id="detener-no-avisa", pruebas=[CO + "test_detener"],
         viejo='                    if _WEB.get("detener"):\n                        _WEB["detener"].set()',
         nuevo='                    if _WEB.get("detener"):\n                        _WEB["detener"].is_set()'),
    dict(id="login-cierra-antes", pruebas=[CO + "test_modo_login"],
         viejo='esperar_cierre=lambda: _time.sleep(6))', nuevo='esperar_cierre=lambda: _time.sleep(1))'),
    dict(id="login-acepta-navieras-desconocidas", pruebas=[CO + "test_modo_login"],
         viejo='navs = [n for n in (d.get("navieras") or []) if n in NAVIERAS]', nuevo='navs = list(d.get("navieras") or [])'),
    dict(id="puerto-mata-sin-forzar", pruebas=[AR + "test_cierra_a_la_fuerza_al_que_ocupa_el_puerto"],
         viejo='subprocess.call(f"taskkill /F /PID {pid}", shell=True)', nuevo='subprocess.call(f"taskkill /PID {pid}", shell=True)'),
    dict(id="puerto-no-busca-al-ocupante", pruebas=[AR + "test_cierra_a_la_fuerza_al_que_ocupa_el_puerto"],
         viejo='            if intento == 0:\n                _liberar_puerto(p)', nuevo='            if intento == 99:\n                _liberar_puerto(p)'),
    dict(id="previa-ociosa-no-se-apaga", pruebas=[AR + "test_instancia_previa_ociosa_se_apaga"],
         viejo='req = urllib.request.Request(f"http://127.0.0.1:{puerto}/api/apagar", data=b"{}", method="POST")',
         nuevo='req = urllib.request.Request(f"http://127.0.0.1:{puerto}/api/estado", data=b"{}", method="POST")'),
    dict(id="previa-ocupada-se-toca", pruebas=[AR + "test_instancia_previa_ocupada_no_se_toca"],
         viejo='                if d.get("corriendo"):', nuevo='                if d.get("corriendo") and False:'),
]

# --- Consola y utilitarios ---
MA = "test_consola.TestMain."
ER = "test_consola.TestEjecutarReservas."
EL = "test_consola.TestEjecutarLogin."
UT = "test_consola.TestUtilitarios."
NAVS_MAIN = '        navieras = list(NAVIERAS.keys()) if objetivo == "todas" else [objetivo]\n        if objetivo != "todas"'
COLA_SIN_EMITIR = 'cola = " · SIN EMITIR" if estado == "OK-EJEMPLO" else ""'
RESPALDO_Y_ESCRITURA = ('            if not respaldo_visto:\n'
                        '                _respaldo_de_la_corrida(corrida, reg)\n'
                        '                respaldo_visto = True\n'
                        '            escribir_estado(naviera_clave, rsv["fila"], reporte)')
AVISO_ESCRITURA = ('            reg.paso(f"⚠ No pude escribir el resultado de la fila {rsv[\'fila\']} en la planilla: {e}. "\n'
                   '                     f"Anótalo a mano: {reporte}")')

MUTACIONES += [
    dict(id="main-todas-es-una-sola", pruebas=[MA + "test_despacho_de_main"],
         viejo=NAVS_MAIN, nuevo=NAVS_MAIN.replace('list(NAVIERAS.keys()) if objetivo == "todas" else [objetivo]', '[objetivo]')),
    dict(id="main-no-pasa-a-minusculas", pruebas=[MA + "test_despacho_de_main"],
         viejo='usuario, objetivo = args[0].lower(), args[1].lower()', nuevo='usuario, objetivo = args[0], args[1].lower()'),
    dict(id="main-sin-alias-ventana", pruebas=[MA + "test_despacho_de_main"],
         viejo='elif len(args) == 1 and args[0].lower() in ("panel", "ventana"):',
         nuevo='elif len(args) == 1 and args[0].lower() in ("panel",):'),
    dict(id="main-no-limpia-argumentos-vacios", pruebas=[MA + "test_despacho_de_main"],
         viejo='args = [a for a in sys.argv[1:] if a.strip()]', nuevo='args = list(sys.argv[1:])'),
    dict(id="main-sin-singular-reserva", pruebas=[MA + "test_despacho_de_main"],
         viejo='if len(args) >= 3 and args[2].lower() in ("reservas", "reserva"):',
         nuevo='if len(args) >= 3 and args[2].lower() in ("reservas",):'),
    dict(id="main-sin-auto", pruebas=[MA + "test_despacho_de_main"],
         viejo='args[3].lower() in ("auto", "autoclose"))', nuevo='args[3].lower() in ("autoclose",))'),
    dict(id="main-otro-aviso-de-respaldo", pruebas=[MA + "test_si_el_panel_web_falla_abre_la_ventana"],
         viejo='No pude abrir el index en el navegador:', nuevo='No pude abrir el panel web:'),
    dict(id="consola-sin-aviso-sin-emitir", pruebas=[ER + "test_reservas_por_consola", ER + "test_sin_emitir_solo_si_volvio_sin_emitir"],
         viejo=COLA_SIN_EMITIR, nuevo='cola = ""'),
    dict(id="consola-sin-emitir-siempre", pruebas=[ER + "test_reservas_por_consola", ER + "test_sin_emitir_solo_si_volvio_sin_emitir"],
         viejo=COLA_SIN_EMITIR, nuevo='cola = " · SIN EMITIR"'),
    dict(id="consola-sin-emitir-salvo-emitida", pruebas=[ER + "test_sin_emitir_solo_si_volvio_sin_emitir"],
         viejo=COLA_SIN_EMITIR, nuevo='cola = " · SIN EMITIR" if estado != "EMITIDA" else ""'),
    dict(id="consola-calla-error-de-escritura", pruebas=[ER + "test_error_de_escritura_se_muestra_y_queda_en_el_log"],
         viejo=AVISO_ESCRITURA, nuevo="            pass"),
    dict(id="consola-aviso-sin-reporte", pruebas=[ER + "test_error_de_escritura_se_muestra_y_queda_en_el_log"],
         viejo='f"Anótalo a mano: {reporte}")', nuevo='f"Anótalo a mano.")'),
    dict(id="consola-sin-resumen-de-no-escritas", pruebas=[ER + "test_error_de_escritura_se_muestra_y_queda_en_el_log"],
         viejo="        if sin_escribir:\n", nuevo="        if False:\n"),
    dict(id="consola-no-cuenta-no-escritas", pruebas=[ER + "test_error_de_escritura_se_muestra_y_queda_en_el_log"],
         viejo='            sin_escribir.append(rsv["fila"])\n', nuevo="            pass\n"),
    dict(id="consola-error-de-escritura-corta-la-corrida",
         pruebas=[ER + "test_error_de_escritura_se_muestra_y_queda_en_el_log"],
         viejo='            sin_escribir.append(rsv["fila"])\n', nuevo="            raise\n"),
    dict(id="respaldo-no-se-hace", pruebas=[ER + "test_respaldo_antes_de_escribir"],
         viejo="            if not respaldo_visto:\n", nuevo="            if False:\n"),
    dict(id="respaldo-en-cada-fila", pruebas=[ER + "test_respaldo_antes_de_escribir"],
         cambios=[("                respaldo_visto = True\n", ""),
                  ('    if corrida.get("respaldo") is not None:\n', "    if False:\n")]),
    dict(id="respaldo-despues-de-escribir", pruebas=[ER + "test_respaldo_antes_de_escribir"],
         viejo=RESPALDO_Y_ESCRITURA,
         nuevo=RESPALDO_Y_ESCRITURA.split("\n")[3] + "\n" + "\n".join(RESPALDO_Y_ESCRITURA.split("\n")[:3])),
    dict(id="respaldo-sin-aviso", pruebas=[ER + "test_respaldo_antes_de_escribir"],
         viejo='reg.info(f"Dejé una copia de respaldo de la planilla: {corrida[\'respaldo\'].name}")', nuevo="pass"),
    # El defecto tal cual era hasta aaca5f1: una copia por naviera en una corrida «todas».
    dict(id="respaldo-una-por-naviera", pruebas=[ER + "test_todas_deja_una_sola_copia"],
         viejo="            _CORRIDA_CONSOLA = {}  ", nuevo="            _CORRIDA_CONSOLA = None  "),
    dict(id="respaldo-corrida-no-se-cierra", pruebas=[ER + "test_todas_deja_una_sola_copia"],
         viejo="            finally:\n                _CORRIDA_CONSOLA = None", nuevo="            finally:\n                pass"),
    dict(id="respaldo-ya-esta-sin-aviso", pruebas=[ER + "test_todas_deja_una_sola_copia"],
         viejo='reg.info(f"La copia de respaldo de esta corrida ya está: {corrida[\'respaldo\'].name}")', nuevo="pass"),
    dict(id="poda-conserva-otra-cantidad", pruebas=[ER + "test_poda_deja_las_10_mas_recientes_y_nada_mas"],
         viejo="RESPALDOS_A_CONSERVAR = 10", nuevo="RESPALDOS_A_CONSERVAR = 11"),
    dict(id="poda-borra-las-mas-recientes", pruebas=[ER + "test_poda_deja_las_10_mas_recientes_y_nada_mas"],
         viejo="respaldos[:-RESPALDOS_A_CONSERVAR]", nuevo="respaldos[RESPALDOS_A_CONSERVAR:]"),
    dict(id="poda-busca-dentro-del-nombre", pruebas=[ER + "test_poda_deja_las_10_mas_recientes_y_nada_mas"],
         viejo="re.fullmatch(PATRON_RESPALDO, e.name)", nuevo="re.search(PATRON_RESPALDO, e.name)"),
    dict(id="poda-solo-mira-el-comienzo", pruebas=[ER + "test_poda_deja_las_10_mas_recientes_y_nada_mas"],
         viejo="re.fullmatch(PATRON_RESPALDO, e.name)", nuevo="re.match(PATRON_RESPALDO, e.name)"),
    dict(id="poda-ignora-mayusculas", pruebas=[ER + "test_poda_deja_las_10_mas_recientes_y_nada_mas"],
         viejo="re.fullmatch(PATRON_RESPALDO, e.name)", nuevo="re.fullmatch(PATRON_RESPALDO, e.name, re.I)"),
    dict(id="poda-toma-carpetas", pruebas=[ER + "test_poda_deja_las_10_mas_recientes_y_nada_mas"],
         viejo="if e.is_file(follow_symlinks=False) and re.fullmatch", nuevo="if re.fullmatch"),
    dict(id="poda-entra-a-subcarpetas", pruebas=[ER + "test_poda_deja_las_10_mas_recientes_y_nada_mas"],
         viejo="    entradas = list(os.scandir(carpeta))",
         nuevo="    entradas = [e for raiz, _, _ in os.walk(carpeta) for e in os.scandir(raiz)]"),
    dict(id="poda-antiguedad-por-fecha-de-archivo", pruebas=[ER + "test_poda_deja_las_10_mas_recientes_y_nada_mas"],
         viejo="re.fullmatch(PATRON_RESPALDO, e.name)),\n                       key=lambda e: e.name)",
         nuevo="re.fullmatch(PATRON_RESPALDO, e.name)),\n                       key=lambda e: e.stat().st_mtime)"),
    dict(id="poda-calla-lo-que-no-borra", pruebas=[ER + "test_respaldo_poda_las_antiguas"],
         viejo='            errores.append(f"«{e.name}» ({type(err).__name__}: {err})")', nuevo="            pass"),
    dict(id="poda-no-se-llama", pruebas=[ER + "test_respaldo_poda_las_antiguas"],
         viejo='borrados, errores = podar_respaldos(corrida["respaldo"].parent)', nuevo="borrados, errores = [], []"),
    dict(id="poda-sin-aviso-de-borrados", pruebas=[ER + "test_respaldo_poda_las_antiguas"],
         viejo="    if borrados:\n        reg.info(f\"Borré {len(borrados)} copia(s)",
         nuevo="    if False:\n        reg.info(f\"Borré {len(borrados)} copia(s)"),
    dict(id="poda-sin-aviso-de-errores", pruebas=[ER + "test_respaldo_poda_las_antiguas"],
         viejo='reg.paso(f"⚠ No pude borrar la copia de respaldo antigua {error}; bórrala a mano si sobra.")',
         nuevo="pass"),
    dict(id="poda-fallida-corta-la-escritura", pruebas=[ER + "test_si_la_poda_falla_igual_escribe"],
         viejo="    except Exception as e:                  # la poda nunca impide escribir",
         nuevo="    except ZeroDivisionError as e:                  # la poda nunca impide escribir"),
    dict(id="respaldo-otro-nombre", pruebas=[ER + "test_respaldo_antes_de_escribir", ER + "test_respaldos_no_se_pisan"],
         viejo='destino = ruta.with_name(f"{ruta.stem} - respaldo {marca}{ruta.suffix}")',
         nuevo='destino = ruta.with_name(f"{ruta.stem} - copia {marca}{ruta.suffix}")'),
    dict(id="respaldo-copia-vacia", pruebas=[ER + "test_respaldo_antes_de_escribir"],
         viejo="        shutil.copyfile(ruta, destino)\n", nuevo='        destino.write_bytes(b"")\n'),
    dict(id="respaldo-se-pisa", pruebas=[ER + "test_respaldos_no_se_pisan"],
         viejo="    while destino.exists():", nuevo="    while False:"),
    dict(id="respaldo-fallido-igual-escribe", pruebas=[ER + "test_sin_respaldo_no_escribe"],
         viejo='        raise ErrorEscritura(f"no pude dejar la copia de respaldo',
         nuevo='        return destino\n        raise ErrorEscritura(f"no pude dejar la copia de respaldo'),
    dict(id="respaldo-fallido-otro-motivo", pruebas=[ER + "test_sin_respaldo_no_escribe"],
         viejo='f"sin respaldo no escribo encima"', nuevo='f"sigo sin respaldo"'),
    dict(id="respaldo-aunque-no-se-escriba", pruebas=[ER + "test_sin_escrituras_no_deja_respaldo"],
         viejo="    corrida = _CORRIDA_CONSOLA if _CORRIDA_CONSOLA is not None else {}",
         nuevo='    corrida = _CORRIDA_CONSOLA if _CORRIDA_CONSOLA is not None else {"respaldo": respaldar_planilla()}'),
    dict(id="consola-otra-carpeta-de-log", pruebas=[ER + "test_reservas_por_consola"],
         viejo='carpeta = carpeta_corrida(f"reservas_{naviera_clave}_{usuario}")',
         nuevo='carpeta = carpeta_corrida(f"res_{naviera_clave}_{usuario}")'),
    dict(id="consola-ignora-solo-primera", pruebas=[ER + "test_solo_primera_fila"],
         viejo='if os.environ.get("AQUASHIELD_SOLO_PRIMERA"):', nuevo='if os.environ.get("AQUASHIELD_SOLO_PRIMERAX"):'),
    dict(id="consola-reserva-sin-login", pruebas=[ER + "test_login_fallido_no_toca_la_planilla"],
         viejo='        if not logueado:\n            reg.paso("No se pudo iniciar sesión; no proceso reservas.")',
         nuevo='        if False:\n            reg.paso("No se pudo iniciar sesión; no proceso reservas.")'),
    dict(id="consola-otra-captura-de-error", pruebas=[ER + "test_reservador_que_revienta"],
         viejo="try: reg.captura(page, f\"error_fila_{rsv['fila']}\")",
         nuevo="try: reg.captura(page, f\"error_{rsv['fila']}\")"),
    dict(id="consola-otro-rechazo", pruebas=[ER + "test_rechazos"],
         viejo="raise ValueError(f\"Aún no está lista la reserva automática de '{naviera_clave}'.\")",
         nuevo="raise ValueError(f\"Naviera sin reserva: '{naviera_clave}'.\")"),
    dict(id="login-todo-ok", pruebas=[EL + "test_login_por_consola"],
         viejo='resultados[clave] = ok', nuevo='resultados[clave] = True'),
    dict(id="login-otra-carpeta", pruebas=[EL + "test_login_por_consola"],
         viejo='carpeta = carpeta_corrida(usuario)', nuevo='carpeta = carpeta_corrida(f"login_{usuario}")'),
    dict(id="login-sin-credenciales-es-falso", pruebas=[EL + "test_sin_credenciales_igual_abre_el_navegador"],
         viejo='reg.info("sin credenciales en config.json, se omite"); resultados[clave] = None; continue',
         nuevo='reg.info("sin credenciales en config.json, se omite"); resultados[clave] = False; continue'),
    dict(id="login-otra-captura-de-error", pruebas=[EL + "test_login_que_revienta"],
         viejo='try: reg.captura(page, f"{clave}_error")', nuevo='try: reg.captura(page, f"error_{clave}")'),
    dict(id="login-acepta-operador-desconocido", pruebas=[EL + "test_operador_desconocido"],
         viejo='        raise ValueError(f"Usuario \'{usuario}\' no está en config.json.")\n\n'
               '    carpeta = carpeta_corrida(usuario)',
         nuevo='        pass\n\n'
               '    carpeta = carpeta_corrida(usuario)'),
    dict(id="registro-sin-tiempo", pruebas=[UT + "test_registro"],
         viejo='texto = f"[{stamp} +{elapsed:6.1f}s] {linea}"', nuevo='texto = f"[{stamp}] {linea}"'),
    dict(id="registro-otra-vineta", pruebas=[UT + "test_registro"],
         viejo='def paso(self, msg): self._emit("· " + msg)', nuevo='def paso(self, msg): self._emit("- " + msg)'),
    dict(id="captura-siempre-completa-si-se-pide", pruebas=[UT + "test_capturas"],
         viejo='completa = bool(full) and bool(', nuevo='completa = bool(full) or bool('),
    dict(id="captura-falla-sin-aviso", pruebas=[UT + "test_capturas"],
         viejo='self._emit(f"    (no pude capturar {nombre}: {e})")', nuevo='pass'),
    dict(id="pausa-otra-espera", pruebas=[UT + "test_pausa_manual"],
         viejo='seg = int(os.environ.get("AQUASHIELD_PAUSA_SEG", "25"))',
         nuevo='seg = int(os.environ.get("AQUASHIELD_PAUSA_SEG", "20"))'),
    dict(id="pausa-no-avisa-al-panel", pruebas=[UT + "test_pausa_manual"],
         viejo='    if on_pausa:\n        on_pausa(mensaje); return', nuevo='    if on_pausa:\n        return'),
    dict(id="chrome-otro-zoom", pruebas=[UT + "test_argumentos_de_chrome"],
         viejo='zoom = float(os.environ.get("AQUASHIELD_ZOOM", "0.65"))', nuevo='zoom = float(os.environ.get("AQUASHIELD_ZOOM", "0.7"))'),
    dict(id="chrome-otro-minimo", pruebas=[UT + "test_argumentos_de_chrome"],
         viejo='zoom = min(max(zoom, 0.5), 1.0)', nuevo='zoom = min(max(zoom, 0.4), 1.0)'),
    dict(id="volcado-a-otra-carpeta", pruebas=[UT + "test_volcado_html_cae_en_la_carpeta_del_programa"],
         viejo='with open(BASE / nombre, "w", encoding="utf-8") as fh:',
         nuevo='with open(LOGS / nombre, "w", encoding="utf-8") as fh:'),
    dict(id="consola-config-ausente-otro-aviso", pruebas=[UT + "test_config_ausente"],
         viejo='raise FileNotFoundError("No existe config.json (copia config.example.json y pon tus credenciales).")',
         nuevo='raise FileNotFoundError("Falta la configuración.")'),
]

# --- Carpeta de cada corrida con nombre único (CICLO-carpetas-unicas.md) ---
CC = "test_consola.TestCarpetaCorrida."
MISMO_SEGUNDO = [CC + "test_mismo_segundo_da_carpetas_distintas", CC + "test_consola_en_el_mismo_segundo",
                 CC + "test_login_en_el_mismo_segundo", CO + "test_dos_corridas_en_el_mismo_segundo"]

MUTACIONES += [
    dict(id="carpeta-comparte-si-existe", pruebas=MISMO_SEGUNDO,
         viejo="            carpeta.mkdir()\n            return carpeta\n",
         nuevo="            carpeta.mkdir(exist_ok=True)\n            return carpeta\n"),
    dict(id="carpeta-sufijo-desde-uno", pruebas=MISMO_SEGUNDO,
         viejo="    carpeta, n = LOGS / base, 2\n", nuevo="    carpeta, n = LOGS / base, 1\n"),
    dict(id="carpeta-sufijo-sin-guion", pruebas=[CC + "test_mismo_segundo_da_carpetas_distintas"],
         viejo='carpeta = LOGS / f"{base}_{n}"', nuevo='carpeta = LOGS / f"{base}{n}"'),
    dict(id="carpeta-sin-segundos",
         pruebas=[CC + "test_mismo_segundo_da_carpetas_distintas", EL + "test_login_por_consola",
                  ER + "test_reservas_por_consola", CO + "test_corrida_de_una_hoja"],
         viejo="strftime('%Y%m%d_%H%M%S')}\"", nuevo="strftime('%Y%m%d_%H%M')}\""),
    # Cada lugar de vuelta a su nombre armado a mano, como hasta 393f504.
    dict(id="login-arma-su-carpeta", pruebas=[CC + "test_login_en_el_mismo_segundo"],
         viejo="    carpeta = carpeta_corrida(usuario)\n",
         nuevo="    carpeta = LOGS / f\"{usuario}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}\"\n"),
    dict(id="consola-arma-su-carpeta", pruebas=[CC + "test_consola_en_el_mismo_segundo"],
         viejo='    carpeta = carpeta_corrida(f"reservas_{naviera_clave}_{usuario}")\n',
         nuevo='    carpeta = LOGS / f"reservas_{naviera_clave}_{usuario}_{ts}"\n'),
    dict(id="web-arma-su-carpeta", pruebas=[CO + "test_dos_corridas_en_el_mismo_segundo"],
         viejo='        carpeta = carpeta_corrida(f"web_{nav_obj}_{usuario}")\n',
         nuevo="        carpeta = LOGS / f\"web_{nav_obj}_{usuario}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}\"\n"),
]

# --- Estado tras el envío y evidencia (CICLO-estado-tras-envio.md) ---
EN = "test_envio.TestResultadoEnvio."
EV = "test_envio.TestEvidencia."
PB = "test_envio.TestPulsarBoton."
LP = "test_envio.TestLecturaDelPanel."
EST = "test_planilla.TestEstadosNuevos."
LEE_NUMERO = ("    if pulsado is not False and not rechazo and not error_portal:\n"
              "        bkg = numero_tras_envio(page, naviera)\n")
EVIDENCIA = "    _guardar_evidencia(page, reg, evidencia)\n    if pulsado is False:\n"
AVISO_HTML = ("            reg.paso(f\"⚠ No pude guardar el HTML {'de la página' if i == 0 else f'del marco {i}'} \"\n"
              "                     f\"{momento}: {_texto_error(e)}\")")
BOOL_JS = "    return bool(alcance.evaluate(js) if arg is None else alcance.evaluate(js, arg))"
LEE_NO_ENVIADA = '  if (est.startsWith("NO ENVIADA")) return "no-enviada";\n'
LEE_ENVIADA = '  if (est.startsWith("ENVIADA")) return "revisar-portal";\n'
LEE_REVISAR = '  if (est.includes("ERROR") || est.includes("REV")) return "revisar";\n'

MUTACIONES += [
    # _resultado_envio: qué estado sale de lo que el programa vio
    dict(id="envio-lee-aunque-no-se-pulse",
         pruebas=[EN + "test_no_pulsado_es_no_enviada", EN + "test_validacion_es_no_enviada_con_los_campos",
                  EN + "test_error_del_portal_es_enviada"],
         viejo=LEE_NUMERO, nuevo=LEE_NUMERO.replace("if pulsado is not False and not rechazo and not error_portal:", "if True:")),
    dict(id="envio-no-lee-tras-falla-al-pulsar", pruebas=[EN + "test_falla_pero_la_confirmacion_esta"],
         viejo="if pulsado is not False and not rechazo", nuevo="if pulsado is True and not rechazo"),
    dict(id="envio-no-pulsado-es-enviada", pruebas=[EN + "test_no_pulsado_es_no_enviada"],
         viejo="    if pulsado is False:\n        return _no_enviada(", nuevo="    if pulsado is False and False:\n        return _no_enviada("),
    dict(id="envio-validacion-es-enviada", pruebas=[EN + "test_validacion_es_no_enviada_con_los_campos"],
         viejo="    if rechazo:\n        lista", nuevo="    if False:\n        lista"),
    dict(id="envio-validacion-sin-tope", pruebas=[EN + "test_validacion_es_no_enviada_con_los_campos"],
         viejo="for c in rechazo[:10])", nuevo="for c in rechazo)"),
    dict(id="envio-sin-evidencia", pruebas=[EN + "test_emitida_solo_con_la_forma_medida", EN + "test_no_pulsado_es_no_enviada"],
         viejo=EVIDENCIA, nuevo="    if pulsado is False:\n"),
    dict(id="envio-evidencia-antes-de-leer", pruebas=[EN + "test_evidencia_despues_de_leer"],
         cambios=[('    rechazo = [str(c) for c in (campos or [])]\n    bkg = ""\n',
                   '    rechazo = [str(c) for c in (campos or [])]\n    _guardar_evidencia(page, reg, evidencia)\n    bkg = ""\n'),
                  (EVIDENCIA, "    if pulsado is False:\n")]),
    dict(id="envio-emitida-sin-log", pruebas=[EN + "test_emitida_solo_con_la_forma_medida"],
         viejo='        reg.paso(f"🎉 {nombre}: Reserva EMITIDA con éxito. Booking: {bkg}")\n'
               '        return ("EMITIDA", f"{nombre} emitida con éxito (Booking: {bkg})")\n    if pulsado is None:',
         nuevo='        return ("EMITIDA", f"{nombre} emitida con éxito (Booking: {bkg})")\n    if pulsado is None:'),
    dict(id="envio-falla-al-pulsar-como-pulsado", pruebas=[EN + "test_falla_al_pulsar_pudo_salir"],
         viejo="    if pulsado is None:\n        que =", nuevo="    if False:\n        que ="),
    dict(id="envio-falla-tras-pulsar-callada", pruebas=[EN + "test_falla_del_programa_despues_de_pulsar"],
         viejo="    elif error is not None:\n        que =", nuevo="    elif False:\n        que ="),
    dict(id="envio-error-del-portal-callado", pruebas=[EN + "test_error_del_portal_es_enviada"],
         viejo="    elif error_portal:\n        que =", nuevo="    elif False:\n        que ="),
    dict(id="envio-sin-forma-como-medida", pruebas=[EN + "test_naviera_sin_forma_nunca_es_emitida"],
         viejo="    elif naviera in FORMA_BOOKING:\n        que =", nuevo="    elif True:\n        que ="),
    dict(id="envio-enviada-sin-log", pruebas=[EN + "test_pulsado_sin_confirmacion_es_enviada"],
         viejo='    reg.paso(f"⚠ {ENVIADA_REVISAR} · {detalle}")', nuevo="    pass"),
    dict(id="envio-no-enviada-sin-log",
         pruebas=[EN + "test_no_pulsado_es_no_enviada", EN + "test_validacion_es_no_enviada_con_los_campos"],
         viejo='    reg.paso(f"✗ {NO_ENVIADA} · {detalle}")', nuevo="    pass"),
    dict(id="envio-falla-sin-log", pruebas=[EN + "test_falla_del_programa_despues_de_pulsar"],
         viejo='        reg.info(f"falla del programa durante el envío: {_texto_error(error)}")', nuevo="        pass"),
    dict(id="envio-error-sin-aplanar", pruebas=[EN + "test_falla_del_programa_despues_de_pulsar"],
         viejo="{' '.join(str(e).split())[:150]}", nuevo="{str(e)[:150]}"),
    dict(id="envio-estado-con-guion-corto",
         pruebas=[EN + "test_pulsado_sin_confirmacion_es_enviada", EN + "test_error_del_portal_es_enviada"],
         viejo='ENVIADA_REVISAR = "ENVIADA – REVISAR EN PORTAL"', nuevo='ENVIADA_REVISAR = "ENVIADA - REVISAR EN PORTAL"'),
    dict(id="envio-no-enviada-otro-nombre", pruebas=[EN + "test_no_pulsado_es_no_enviada"],
         viejo='NO_ENVIADA = "NO ENVIADA"', nuevo='NO_ENVIADA = "NO EMITIDA"'),
    dict(id="envio-sin-pedir-revisar-el-portal", pruebas=[EN + "test_pulsado_sin_confirmacion_es_enviada"],
         viejo='_REVISA_PORTAL = "Revisa en el portal si la reserva quedó creada y, si está, anota su número en la planilla."',
         nuevo='_REVISA_PORTAL = "Revisa el portal."'),
    # _guardar_evidencia: la captura y el HTML de la página y de cada marco
    dict(id="evidencia-sin-captura", pruebas=[EV + "test_captura_y_html_de_la_pagina_y_los_marcos"],
         viejo="    reg.captura(page, nombre, full=True)\n", nuevo=""),
    dict(id="evidencia-captura-de-pagina-entera", pruebas=[EV + "test_captura_y_html_de_la_pagina_y_los_marcos"],
         viejo="    reg.captura(page, nombre, full=True)\n",
         nuevo='    page.screenshot(path=str(reg.dir_capturas / f"{nombre}.png"), full_page=True)\n'),
    dict(id="evidencia-solo-la-pagina",
         pruebas=[EV + "test_captura_y_html_de_la_pagina_y_los_marcos", EV + "test_un_html_que_falla_se_avisa_y_no_tapa_a_los_demas"],
         viejo="    for i, alcance in enumerate([page] + marcos):", nuevo="    for i, alcance in enumerate([page]):"),
    dict(id="evidencia-repite-el-principal", pruebas=[EV + "test_no_repite_el_marco_principal"],
         viejo="if f is not page and f is not principal]", nuevo="if f is not page]"),
    dict(id="evidencia-sin-html-de-playwright", pruebas=[EV + "test_sin_javascript_usa_el_html_de_playwright"],
         viejo="            if not html:                   # sin JavaScript", nuevo="            if False:                   # sin JavaScript"),
    dict(id="evidencia-sin-contar-los-sin-shadow", pruebas=[EV + "test_sin_javascript_usa_el_html_de_playwright"],
         viejo="                html = alcance.content()\n                sin_shadow += 1", nuevo="                html = alcance.content()"),
    dict(id="evidencia-falla-callada", pruebas=[EV + "test_un_html_que_falla_se_avisa_y_no_tapa_a_los_demas"],
         viejo=AVISO_HTML, nuevo="            pass"),
    dict(id="evidencia-un-fallo-corta", pruebas=[EV + "test_un_html_que_falla_se_avisa_y_no_tapa_a_los_demas"],
         viejo=AVISO_HTML, nuevo=AVISO_HTML + "\n            break"),
    dict(id="evidencia-sin-contador",
         pruebas=[EV + "test_captura_y_html_de_la_pagina_y_los_marcos", EV + "test_un_html_que_falla_se_avisa_y_no_tapa_a_los_demas"],
         viejo="evidencia del envío: {nombre}.png y {guardados} de {total} HTML",
         nuevo="evidencia del envío: {nombre}.png y {guardados} HTML"),
    dict(id="evidencia-sin-url", pruebas=[EV + "test_captura_y_html_de_la_pagina_y_los_marcos"],
         viejo="{getattr(alcance, 'url', '')} -->", nuevo=" -->"),
    dict(id="evidencia-js-sin-shadow", pruebas=[EV + "test_el_javascript_trae_las_raices_shadow"],
         viejo="html.getHTML({shadowRoots: raices})", nuevo="html.getHTML()"),
    dict(id="evidencia-js-no-baja-en-shadow", pruebas=[EV + "test_el_javascript_trae_las_raices_shadow"],
         viejo="{ raices.push(e.shadowRoot); visitar(e.shadowRoot); }", nuevo="{ raices.push(e.shadowRoot); }"),
    dict(id="evidencia-js-hace-clic", pruebas=[EV + "test_el_javascript_trae_las_raices_shadow"],
         viejo="    const raices = raicesDe(document);\n    const html = document.documentElement;",
         nuevo="    const raices = raicesDe(document);\n"
               "    document.querySelectorAll('button').forEach(b => b.click());\n"
               "    const html = document.documentElement;"),
    # _pulsar_boton: True solo si pulsó
    dict(id="pulsar-visible-no-cuenta", pruebas=[PB + "test_pulsa_el_boton_visible"],
         viejo="        btn.click()\n        return True", nuevo="        btn.click()\n        return False"),
    dict(id="pulsar-invisible-igual-pulsa",
         pruebas=[PB + "test_sin_boton_visible_usa_el_javascript", PB + "test_sin_boton_ni_javascript_no_pulsa"],
         viejo="    if btn.count() and btn.is_visible():\n        btn.click()", nuevo="    if btn.count():\n        btn.click()"),
    dict(id="pulsar-sin-javascript", pruebas=[PB + "test_sin_boton_visible_usa_el_javascript"],
         viejo="    if js is None:\n        return False", nuevo="    if True:\n        return False"),
    dict(id="pulsar-javascript-siempre-pulsa", pruebas=[PB + "test_sin_boton_visible_usa_el_javascript"],
         viejo=BOOL_JS, nuevo=BOOL_JS + " or True"),
    dict(id="pulsar-javascript-sin-argumento", pruebas=[PB + "test_sin_boton_visible_usa_el_javascript"],
         viejo=BOOL_JS, nuevo="    return bool(alcance.evaluate(js))"),
    dict(id="pulsar-javascript-sin-bool", pruebas=[PB + "test_sin_boton_visible_usa_el_javascript"],
         viejo=BOOL_JS, nuevo="    return (alcance.evaluate(js) if arg is None else alcance.evaluate(js, arg))"),
    # El panel: cómo lee cada estado y cómo pinta la fila
    dict(id="panel-sin-lectura-no-enviada", pruebas=[LP + "test_lectura_de_cada_estado"],
         viejo=LEE_NO_ENVIADA, nuevo=""),
    dict(id="panel-enviada-cae-en-revisar", pruebas=[LP + "test_lectura_de_cada_estado"],
         viejo=LEE_ENVIADA, nuevo=""),
    dict(id="panel-revisar-antes-que-enviada", pruebas=[LP + "test_lectura_de_cada_estado"],
         cambios=[(LEE_NO_ENVIADA, LEE_REVISAR + LEE_NO_ENVIADA), (LEE_ENVIADA + LEE_REVISAR, LEE_ENVIADA)]),
    dict(id="panel-no-enviada-queda-en-curso", pruebas=[LP + "test_cada_lectura_nueva_pinta_su_fila"],
         viejo='          chip(f, "rev", "no enviada");\n          if (tr) tr.classList.remove("fila-activa", "fila-emitida");\n',
         nuevo='          chip(f, "rev", "no enviada");\n'),
    dict(id="panel-revisar-portal-sin-insignia", pruebas=[LP + "test_cada_lectura_nueva_pinta_su_fila"],
         viejo='color:var(--danger)">revisar en portal</span>`;', nuevo='color:var(--danger)">revisar</span>`;'),
    dict(id="panel-sin-usar-la-lectura", pruebas=[LP + "test_cada_lectura_nueva_pinta_su_fila"],
         viejo="        const lectura = lecturaEstado(est);", nuevo='        const lectura = "otro";'),
    # Solo una EMITIDA tiene número; los lectores y la consola no cambian con los estados nuevos
    dict(id="limpio-de-cualquier-estado",
         pruebas=[LI + "test_solo_una_emitida_tiene_numero", CO + "test_corrida_con_estados_tras_el_envio"],
         viejo='    if str((r or {}).get("estado") or "") != "EMITIDA":\n        return ""\n', nuevo=""),
    dict(id="lector-web-salta-las-enviadas", pruebas=[EST + "test_web_lee_lo_mismo"],
         viejo='        if pol.lower().startswith("pto") or nave.lower() == "nave":\n',
         nuevo='        if pol.lower().startswith("pto") or nave.lower() == "nave" or "ENVIADA" in val("estado"):\n'),
    dict(id="lector-consola-salta-las-enviadas", pruebas=[EST + "test_consola_lee_lo_mismo"],
         viejo="        # Descartar notas operativas escritas en celdas sueltas\n",
         nuevo='        if "estado" in col_map and "ENVIADA" in _s(ws.cell(r, col_map["estado"]).value):\n            continue\n'
               "        # Descartar notas operativas escritas en celdas sueltas\n"),
    dict(id="consola-no-enviada-con-sin-emitir", pruebas=[ER + "test_estados_tras_el_envio_en_la_planilla"],
         viejo=COLA_SIN_EMITIR, nuevo='cola = " · SIN EMITIR" if estado in ("OK-EJEMPLO", "NO ENVIADA") else ""'),
]

# --- Cada reservador después de la guarda: el mismo botón, el error guardado, _resultado_envio ---
RS = "test_envio.TestReservadores."
PULSAR_ONE = ('            pulsado = _pulsar_boton(page, "button:has-text(\'Submit\'), button:has-text(\'Enviar\'), '
              'button[type=\'submit\']",\n')
FIN_ONE = ('        except Exception as e:\n            error = e\n'
           '        return _resultado_envio(page, reg, "one", "ONE", f"one_f{f}_11_confirmado", "Submit", pulsado, error)')

MUTACIONES += [
    dict(id="one-no-anota-si-pulso", pruebas=[RS + "test_one_decide_con_lo_que_vio"],
         viejo=PULSAR_ONE, nuevo=PULSAR_ONE.replace("pulsado = _pulsar_boton(", "_pulsar_boton(")),
    dict(id="one-pulsa-otro-boton", pruebas=[RS + "test_one_decide_con_lo_que_vio"],
         viejo=PULSAR_ONE, nuevo=PULSAR_ONE.replace(", button[type='submit']", "")),
    dict(id="one-falla-escapa", pruebas=[RS + "test_one_decide_con_lo_que_vio"],
         viejo=FIN_ONE, nuevo=FIN_ONE.replace("except Exception as e:", "except ZeroDivisionError as e:")),
    dict(id="one-falla-sin-guardar-el-error", pruebas=[RS + "test_one_decide_con_lo_que_vio"],
         viejo=FIN_ONE, nuevo=FIN_ONE.replace("            error = e\n", "            pass\n")),
    dict(id="one-vuelve-al-extractor-viejo", pruebas=[RS + "test_one_decide_con_lo_que_vio"],
         viejo=FIN_ONE, nuevo=FIN_ONE.replace(
             'return _resultado_envio(page, reg, "one", "ONE", f"one_f{f}_11_confirmado", "Submit", pulsado, error)',
             'bkg = extraer_numero_booking(page, "one")\n'
             '        return ("EMITIDA", f"ONE emitida con éxito (Booking: {bkg or \'en proceso\'})")')),
    dict(id="one-evidencia-sin-la-fila", pruebas=[RS + "test_one_decide_con_lo_que_vio"],
         viejo=FIN_ONE, nuevo=FIN_ONE.replace('f"one_f{f}_11_confirmado"', '"one_confirmado"')),
    dict(id="one-captura-aparte", pruebas=[RS + "test_one_decide_con_lo_que_vio"],
         viejo=FIN_ONE, nuevo=FIN_ONE.replace("        return _resultado_envio(",
                                              '        reg.captura(page, f"one_f{f}_11_confirmado", full=True)\n'
                                              "        return _resultado_envio(")),
]

PULSAR_MSC = ('        pulsado = _pulsar_boton(page, "button:has-text(\'Submit\'), button[type=\'submit\']", '
              '_JS_CLICK_BTN, "^(submit|enviar)$")\n')
FIN_MSC = ('    except Exception as e:\n        error = e\n'
           '    return _resultado_envio(page, reg, "msc", "MSC", f"msc_f{f}_6_confirmado", "Submit", pulsado, error)')

MUTACIONES += [
    dict(id="msc-no-anota-si-pulso", pruebas=[RS + "test_msc_decide_con_lo_que_vio"],
         viejo=PULSAR_MSC, nuevo=PULSAR_MSC.replace("pulsado = _pulsar_boton(", "_pulsar_boton(")),
    dict(id="msc-pulsa-otro-boton", pruebas=[RS + "test_msc_decide_con_lo_que_vio"],
         viejo=PULSAR_MSC, nuevo=PULSAR_MSC.replace('"^(submit|enviar)$"', '"^(submit|enviar|send)$"')),
    dict(id="msc-falla-escapa", pruebas=[RS + "test_msc_decide_con_lo_que_vio"],
         viejo=FIN_MSC, nuevo=FIN_MSC.replace("except Exception as e:", "except ZeroDivisionError as e:")),
    dict(id="msc-falla-sin-guardar-el-error", pruebas=[RS + "test_msc_decide_con_lo_que_vio"],
         viejo=FIN_MSC, nuevo=FIN_MSC.replace("        error = e\n", "        pass\n")),
    dict(id="msc-vuelve-al-extractor-viejo", pruebas=[RS + "test_msc_decide_con_lo_que_vio"],
         viejo=FIN_MSC, nuevo=FIN_MSC.replace(
             'return _resultado_envio(page, reg, "msc", "MSC", f"msc_f{f}_6_confirmado", "Submit", pulsado, error)',
             'bkg = extraer_numero_booking(page, "msc")\n'
             '    return ("EMITIDA", f"MSC emitida con éxito (Booking: {bkg or \'en proceso\'})")')),
    dict(id="msc-evidencia-sin-la-fila", pruebas=[RS + "test_msc_decide_con_lo_que_vio"],
         viejo=FIN_MSC, nuevo=FIN_MSC.replace('f"msc_f{f}_6_confirmado"', '"msc_confirmado"')),
]

# --- HYUNDAI: la forma medida (5 de 5 capturas) y el reservador después de la guarda ---
FORMA_HMM = '    "hyundai": r"(?i:Created\\s+tentative\\s+booking\\s+number)\\s*:?\\s*(SCLA\\d{8})\\b",'
PULSAR_HMM = '            pulsado = _pulsar_boton(page, "button:has-text(\'Create NOW\'), .btn:has-text(\'Create NOW\')")\n'
FIN_HMM = ('        except Exception as e:\n            error = e\n'
           '        return _resultado_envio(page, reg, "hyundai", "HYUNDAI", f"hmm_f{f}_6_confirmado", "Create NOW", '
           'pulsado, error)')

MUTACIONES += [
    dict(id="hyundai-forma-sin-etiqueta", pruebas=[TE + "test_forma_medida_de_hyundai"],
         viejo=FORMA_HMM, nuevo='    "hyundai": r"(SCLA\\d{8})\\b",'),
    dict(id="hyundai-forma-otros-digitos", pruebas=[TE + "test_forma_medida_de_hyundai"],
         viejo=FORMA_HMM, nuevo=FORMA_HMM.replace(r"(SCLA\d{8})", r"(SCLA\d{7,9})")),
    dict(id="hyundai-forma-otro-prefijo", pruebas=[TE + "test_forma_medida_de_hyundai"],
         viejo=FORMA_HMM, nuevo=FORMA_HMM.replace(r"(SCLA\d{8})", r"([A-Z]{4}\d{8})")),
    dict(id="hyundai-forma-sin-limite", pruebas=[TE + "test_forma_medida_de_hyundai"],
         viejo=FORMA_HMM, nuevo=FORMA_HMM.replace(r"(SCLA\d{8})\b", r"(SCLA\d{8})")),
    dict(id="hyundai-numero-sin-caja", pruebas=[TE + "test_forma_medida_de_hyundai"],
         viejo=FORMA_HMM, nuevo=FORMA_HMM.replace(r"(SCLA\d{8})", r"((?i:SCLA)\d{8})")),
    dict(id="hyundai-etiqueta-con-caja", pruebas=[TE + "test_forma_medida_de_hyundai"],
         viejo=FORMA_HMM, nuevo=FORMA_HMM.replace(r"(?i:Created\s+tentative\s+booking\s+number)",
                                                  r"Created\s+tentative\s+booking\s+number")),
    dict(id="hyundai-sin-forma-medida", pruebas=[TE + "test_forma_medida_de_hyundai"],
         viejo=FORMA_HMM + "  # 5 de 5 capturas\n", nuevo=""),
    dict(id="hyundai-no-anota-si-pulso", pruebas=[RS + "test_hyundai_decide_con_lo_que_vio"],
         viejo=PULSAR_HMM, nuevo=PULSAR_HMM.replace("pulsado = _pulsar_boton(", "_pulsar_boton(")),
    dict(id="hyundai-pulsa-otro-boton", pruebas=[RS + "test_hyundai_decide_con_lo_que_vio"],
         viejo=PULSAR_HMM, nuevo=PULSAR_HMM.replace(", .btn:has-text('Create NOW')", "")),
    dict(id="hyundai-falla-escapa", pruebas=[RS + "test_hyundai_decide_con_lo_que_vio"],
         viejo=FIN_HMM, nuevo=FIN_HMM.replace("except Exception as e:", "except ZeroDivisionError as e:")),
    dict(id="hyundai-falla-sin-guardar-el-error", pruebas=[RS + "test_hyundai_decide_con_lo_que_vio"],
         viejo=FIN_HMM, nuevo=FIN_HMM.replace("            error = e\n", "            pass\n")),
    dict(id="hyundai-vuelve-al-extractor-viejo", pruebas=[RS + "test_hyundai_decide_con_lo_que_vio"],
         viejo=FIN_HMM, nuevo=FIN_HMM.split("        return _resultado_envio(")[0]
         + '        bkg_num = extraer_numero_booking(page, "HYUNDAI")\n'
           '        return ("EMITIDA", f"HYUNDAI emitida exitosamente; Bkg: {bkg_num or \'Ver captura\'}; {det}")'),
    dict(id="hyundai-evidencia-sin-la-fila", pruebas=[RS + "test_hyundai_decide_con_lo_que_vio"],
         viejo=FIN_HMM, nuevo=FIN_HMM.replace('f"hmm_f{f}_6_confirmado"', '"hmm_confirmado"')),
    dict(id="hyundai-confirma-aunque-no-pulse", pruebas=[RS + "test_hyundai_decide_con_lo_que_vio"],
         viejo="            if pulsado:\n                esperar(page, 3.0)", nuevo="            if True:\n                esperar(page, 3.0)"),
]

# --- MAERSK: la forma medida (5 de 5 capturas) y el reservador después de la guarda ---
FORMA_MK = '    "maersk": r"(?i:Booking\\s+number)\\s*:?\\s*(\\d{9})\\b",'
PULSAR_MK = '            pulsado = _pulsar_boton(page, "button:has-text(\'Submit booking\'), button:has-text(\'Book now\')")\n'
FIN_MK = ('        except Exception as e:\n            error = e\n'
          '        return _resultado_envio(page, reg, "maersk", "MAERSK", f"mk_f{f}_7_confirmado", "Submit booking", '
          'pulsado, error)')

MUTACIONES += [
    dict(id="maersk-forma-sin-etiqueta", pruebas=[TE + "test_forma_medida_de_maersk"],
         viejo=FORMA_MK, nuevo='    "maersk": r"\\b(\\d{9})\\b",'),
    dict(id="maersk-forma-otros-digitos", pruebas=[TE + "test_forma_medida_de_maersk"],
         viejo=FORMA_MK, nuevo=FORMA_MK.replace(r"(\d{9})", r"(\d{8,10})")),
    dict(id="maersk-forma-letras", pruebas=[TE + "test_forma_medida_de_maersk"],
         viejo=FORMA_MK, nuevo=FORMA_MK.replace(r"(\d{9})", r"([A-Z0-9]{9,12})")),
    dict(id="maersk-forma-sin-limite", pruebas=[TE + "test_forma_medida_de_maersk"],
         viejo=FORMA_MK, nuevo=FORMA_MK.replace(r"(\d{9})\b", r"(\d{9})")),
    dict(id="maersk-etiqueta-con-caja", pruebas=[TE + "test_forma_medida_de_maersk"],
         viejo=FORMA_MK, nuevo=FORMA_MK.replace(r"(?i:Booking\s+number)", r"Booking\s+number")),
    dict(id="maersk-otra-etiqueta", pruebas=[TE + "test_forma_medida_de_maersk"],
         viejo=FORMA_MK, nuevo=FORMA_MK.replace(r"(?i:Booking\s+number)", r"(?i:Booking\s+number|Your\s+booking)")),
    dict(id="maersk-sin-forma-medida", pruebas=[TE + "test_forma_medida_de_maersk"],
         viejo=FORMA_MK + "  # 5 de 5 capturas\n", nuevo=""),
    dict(id="maersk-no-anota-si-pulso", pruebas=[RS + "test_maersk_decide_con_lo_que_vio"],
         viejo=PULSAR_MK, nuevo=PULSAR_MK.replace("pulsado = _pulsar_boton(", "_pulsar_boton(")),
    dict(id="maersk-pulsa-otro-boton", pruebas=[RS + "test_maersk_decide_con_lo_que_vio"],
         viejo=PULSAR_MK, nuevo=PULSAR_MK.replace(", button:has-text('Book now')", "")),
    dict(id="maersk-falla-escapa", pruebas=[RS + "test_maersk_decide_con_lo_que_vio"],
         viejo=FIN_MK, nuevo=FIN_MK.replace("except Exception as e:", "except ZeroDivisionError as e:")),
    dict(id="maersk-falla-sin-guardar-el-error", pruebas=[RS + "test_maersk_decide_con_lo_que_vio"],
         viejo=FIN_MK, nuevo=FIN_MK.replace("            error = e\n", "            pass\n")),
    dict(id="maersk-vuelve-al-extractor-viejo", pruebas=[RS + "test_maersk_decide_con_lo_que_vio"],
         viejo=FIN_MK, nuevo=FIN_MK.split("        return _resultado_envio(")[0]
         + '        bkg_num = extraer_numero_booking(page, "MAERSK")\n'
           '        return ("EMITIDA", f"MAERSK emitida exitosamente; Bkg: {bkg_num or \'Ver captura\'}")'),
    dict(id="maersk-evidencia-sin-la-fila", pruebas=[RS + "test_maersk_decide_con_lo_que_vio"],
         viejo=FIN_MK, nuevo=FIN_MK.replace('f"mk_f{f}_7_confirmado"', '"mk_confirmado"')),
]

# --- CMA: sin forma medida, nunca EMITIDA; el reservador después de la guarda ---
PULSAR_CMA = ('                pulsado = _pulsar_boton(page, "button:has-text(\'Enviar el booking\'), '
              'button:has-text(\'Send booking\'), "\n')
FIN_CMA = ('            except Exception as e:\n                error = e\n')
DECIDE_CMA = ('            return _resultado_envio(page, reg, "cma", "CMA", f"cma_f{f}_6_confirmado", "Enviar el booking", '
              'pulsado,\n')

MUTACIONES += [
    dict(id="cma-no-anota-si-pulso", pruebas=[RS + "test_cma_decide_con_lo_que_vio"],
         viejo=PULSAR_CMA, nuevo=PULSAR_CMA.replace("pulsado = _pulsar_boton(", "_pulsar_boton(")),
    dict(id="cma-pulsa-otro-boton", pruebas=[RS + "test_cma_decide_con_lo_que_vio"],
         viejo=PULSAR_CMA, nuevo=PULSAR_CMA.replace("button:has-text('Send booking'), ", "")),
    dict(id="cma-falla-escapa", pruebas=[RS + "test_cma_decide_con_lo_que_vio"],
         viejo=FIN_CMA, nuevo=FIN_CMA.replace("except Exception as e:", "except ZeroDivisionError as e:")),
    dict(id="cma-falla-sin-guardar-el-error", pruebas=[RS + "test_cma_decide_con_lo_que_vio"],
         viejo=FIN_CMA, nuevo=FIN_CMA.replace("                error = e\n", "                pass\n")),
    dict(id="cma-vuelve-al-extractor-viejo", pruebas=[RS + "test_cma_decide_con_lo_que_vio"],
         viejo=DECIDE_CMA + "                                    error)",
         nuevo='            bkg_num = extraer_numero_booking(page, "CMA")\n'
               '            return ("EMITIDA", f"CMA emitida exitosamente; Bkg: {bkg_num or \'Ver captura\'}")'),
    dict(id="cma-evidencia-sin-la-fila", pruebas=[RS + "test_cma_decide_con_lo_que_vio"],
         viejo=DECIDE_CMA, nuevo=DECIDE_CMA.replace('f"cma_f{f}_6_confirmado"', '"cma_confirmado"')),
    dict(id="cma-con-forma-inventada", pruebas=[RS + "test_cma_decide_con_lo_que_vio"],
         viejo='    "maersk": r"(?i:Booking\\s+number)\\s*:?\\s*(\\d{9})\\b",  # 5 de 5 capturas\n',
         nuevo='    "maersk": r"(?i:Booking\\s+number)\\s*:?\\s*(\\d{9})\\b",  # 5 de 5 capturas\n'
               '    "cma": r"(?i:Booking\\s+reference)\\s*:?\\s*([A-Z0-9]{8,16})",\n'),
]

# --- COSCO: pulsado, errores de validación contra aviso del portal, la espera sin decidir ---
CO_ = "test_envio.TestCosco."
PULSAR_CO = ('        pulsado = _pulsar_boton(frame, "button:has-text(\'Submit\'), .btn:has-text(\'Submit\')", '
             '_JS_COSCO_SUBMIT)\n')
ESPERA_CO = ("        if pulsado:\n            campos, error_portal, vio_reminder = _cosco_esperar_resultado(page, frame, reg)\n"
             "    except Exception as e:\n        error = e\n")
REMINDER_CO = ('    if campos and vio_reminder:\n'
               '        # Con la ventana Reminder ya vista no está medido si esos errores frenaron el envío.\n'
               '        error_portal = "; ".join(campos + ([error_portal] if error_portal else []))\n'
               '        campos = []\n')
DECIDE_CO = ('    return _resultado_envio(page, reg, "cosco", "COSCO", f"cosco_f{f}_6_confirmado", "Submit", pulsado, error,\n'
             '                            campos=campos, error_portal=error_portal)\n')
ERRORES_JS = "    const campos = [...new Set(visibles('.el-form-item__error'))];\n"
ALCANCES_CO = ("    for alcance in (frame, page):\n        if not alcance:\n            continue\n        try:\n"
               "            r = alcance.evaluate(_JS_COSCO_ERRORES) or {}\n")

MUTACIONES += [
    dict(id="evidencia-antes-de-la-guarda", pruebas=[RS + "test_la_evidencia_y_el_estado_solo_despues_de_la_guarda"],
         viejo='    _evidencia_antes_de_la_guarda(page, reg, f"msc_f{f}_guarda")\n    if not es_modo_emision():',
         nuevo='    _evidencia_antes_de_la_guarda(page, reg, f"msc_f{f}_guarda")\n'
               '    _guardar_evidencia(page, reg, f"msc_f{f}_5_summary")\n    if not es_modo_emision():'),
    dict(id="cosco-no-anota-si-pulso", pruebas=[RS + "test_cosco_decide_con_lo_que_vio"],
         viejo=PULSAR_CO, nuevo=PULSAR_CO.replace("pulsado = _pulsar_boton(", "_pulsar_boton(")),
    dict(id="cosco-pulsa-sin-buscar-por-texto", pruebas=[RS + "test_cosco_decide_con_lo_que_vio"],
         viejo=PULSAR_CO, nuevo=PULSAR_CO.replace(", _JS_COSCO_SUBMIT)", ")")),
    dict(id="cosco-espera-aunque-no-pulse", pruebas=[RS + "test_cosco_decide_con_lo_que_vio"],
         viejo=ESPERA_CO, nuevo=ESPERA_CO.replace("        if pulsado:\n", "        if True:\n")),
    dict(id="cosco-falla-escapa", pruebas=[RS + "test_cosco_decide_con_lo_que_vio"],
         viejo=ESPERA_CO, nuevo=ESPERA_CO.replace("except Exception as e:", "except ZeroDivisionError as e:")),
    dict(id="cosco-falla-sin-guardar-el-error", pruebas=[RS + "test_cosco_decide_con_lo_que_vio"],
         viejo=ESPERA_CO, nuevo=ESPERA_CO.replace("        error = e\n", "        pass\n")),
    dict(id="cosco-reminder-visto-igual-no-enviada", pruebas=[RS + "test_cosco_decide_con_lo_que_vio"],
         viejo=REMINDER_CO, nuevo=REMINDER_CO.replace("    if campos and vio_reminder:\n", "    if False:\n")),
    dict(id="cosco-vuelve-a-emitida", pruebas=[RS + "test_cosco_decide_con_lo_que_vio"],
         viejo=DECIDE_CO, nuevo='    return ("EMITIDA", "COSCO emitida con éxito (Booking: en proceso)")\n'),
    dict(id="cosco-evidencia-sin-la-fila", pruebas=[RS + "test_cosco_decide_con_lo_que_vio"],
         viejo=DECIDE_CO, nuevo=DECIDE_CO.replace('f"cosco_f{f}_6_confirmado"', '"cosco_confirmado"')),
    dict(id="cosco-sin-pasar-los-campos", pruebas=[RS + "test_cosco_decide_con_lo_que_vio"],
         viejo=DECIDE_CO, nuevo=DECIDE_CO.replace("campos=campos, ", "")),
    dict(id="cosco-js-submit-no-dice-si-pulso", pruebas=[CO_ + "test_js_submit_dice_si_pulso"],
         viejo="\n    if (b) { b.click(); return true; }\n", nuevo="\n    if (b) { b.click(); }\n"),
    dict(id="cosco-js-errores-mezcla-el-aviso", pruebas=[CO_ + "test_js_errores_separa_campos_y_aviso"],
         viejo=ERRORES_JS, nuevo=ERRORES_JS.replace("'.el-form-item__error'", "'.el-form-item__error, .el-message--error'")),
    dict(id="cosco-js-errores-repite", pruebas=[CO_ + "test_js_errores_separa_campos_y_aviso"],
         viejo=ERRORES_JS, nuevo="    const campos = visibles('.el-form-item__error');\n"),
    dict(id="cosco-js-errores-toma-los-ocultos", pruebas=[CO_ + "test_js_errores_separa_campos_y_aviso"],
         viejo="        .filter(e => e.offsetParent !== null)\n        .map(e => (e.textContent || '')",
         nuevo="        .map(e => (e.textContent || '')"),
    dict(id="cosco-js-errores-toma-los-informativos", pruebas=[CO_ + "test_js_errores_separa_campos_y_aviso"],
         viejo="        .filter(t => t && !esAviso(t));\n", nuevo="        .filter(t => t);\n"),
    dict(id="cosco-errores-un-alcance-tapa", pruebas=[CO_ + "test_errores_de_los_dos_alcances"],
         viejo="            r = alcance.evaluate(_JS_COSCO_ERRORES) or {}\n        except Exception:\n            continue\n",
         nuevo="            r = alcance.evaluate(_JS_COSCO_ERRORES) or {}\n        except Exception:\n            return [], \"\"\n"),
    dict(id="cosco-errores-solo-el-marco", pruebas=[CO_ + "test_errores_de_los_dos_alcances"],
         viejo=ALCANCES_CO, nuevo=ALCANCES_CO.replace("(frame, page)", "(frame,)")),
    dict(id="cosco-errores-repite", pruebas=[CO_ + "test_errores_de_los_dos_alcances"],
         viejo='        campos += [c for c in (r.get("campos") or []) if c not in campos]\n',
         nuevo='        campos += list(r.get("campos") or [])\n'),
    dict(id="cosco-espera-no-corta-con-errores",
         pruebas=[CO_ + "test_espera_corta_con_errores_de_validacion", CO_ + "test_espera_corta_con_aviso_del_portal"],
         viejo="        if campos or error_portal:\n            break\n", nuevo="        if False:\n            break\n"),
    dict(id="cosco-espera-no-anota-el-reminder",
         pruebas=[CO_ + "test_reminder_pulsa_su_submit_una_sola_vez", CO_ + "test_reminder_tardio_tambien_una_sola_vez",
                  CO_ + "test_reminder_ambiguo_no_pulsa"],
         viejo="        if _cosco_en_alguno(frame, page, _JS_COSCO_HAY_REMINDER):\n            vio_reminder = True\n",
         nuevo="        if _cosco_en_alguno(frame, page, _JS_COSCO_HAY_REMINDER):\n"),
    dict(id="cosco-espera-otro-plazo",
         pruebas=[CO_ + "test_espera_se_agota", CO_ + "test_reminder_tardio_tambien_una_sola_vez",
                  CO_ + "test_reminder_ambiguo_no_pulsa"],
         viejo="COSCO_ESPERA_CONFIRMACION_SEG = 180\n", nuevo="COSCO_ESPERA_CONFIRMACION_SEG = 150\n"),
]

# --- Clics a ciegas antes de la guarda (CICLO-clics-a-ciegas.md) ---
SC = "test_clics.TestSinClicACiegas."
EVIDENCIA_CORTE = ("                _evidencia_antes_de_la_guarda(page, reg, f\"{prefijo}_f{(reserva or {}).get('fila')}"
                   "_sin_objetivo\",\n                                              \"en el paso sin objetivo\", "
                   "completa=False)\n")
FG ="test_clics.TestFotoDeClicsGenericos.test_ningun_clic_generico_nuevo_antes_de_la_guarda"
O1 = "test_clics.TestOne."

MUTACIONES += [
    # El mecanismo: ObjetivoNoEncontrado y el decorador que lo convierte en NO ENVIADA.
    dict(id="corte-lo-traga-un-except", pruebas=[SC + "test_ningun_except_exception_se_lo_traga"],
         viejo="class ObjetivoNoEncontrado(BaseException):", nuevo="class ObjetivoNoEncontrado(Exception):"),
    dict(id="corte-sin-captura", pruebas=[SC + "test_sin_objetivo_queda_no_enviada_con_el_paso_y_lo_que_buscaba"],
         viejo=EVIDENCIA_CORTE, nuevo=""),
    dict(id="corte-sigue-como-ejemplo",
         pruebas=[SC + "test_sin_objetivo_queda_no_enviada_con_el_paso_y_lo_que_buscaba",
                  SC + "test_ningun_except_exception_se_lo_traga"],
         viejo="            except ObjetivoNoEncontrado as e:\n",
         nuevo="            except ObjetivoNoEncontrado as e:\n                return (\"OK-EJEMPLO\", str(e))\n"),
    dict(id="corte-no-dice-lo-que-buscaba",
         pruebas=[SC + "test_sin_objetivo_queda_no_enviada_con_el_paso_y_lo_que_buscaba"],
         viejo='f"{e.paso}: {pide} {e.buscaba}, así que no pulsé nada.',
         nuevo='f"{e.paso}: {pide} el objetivo, así que no pulsé nada.'),
    dict(id="corte-pierde-el-nombre", pruebas=[SC + "test_lo_demas_pasa_igual"],
         viejo="        reservar_sin_clic_a_ciegas.__name__ = reservar.__name__\n", nuevo=""),
    # ONE
    dict(id="one-sin-decorador", pruebas=[SC + "test_cada_reservador_que_corta_esta_decorado"],
         viejo='@_sin_clic_a_ciegas("one")\n', nuevo=""),
    dict(id="one-cierre-a-ciegas", pruebas=[O1 + "test_js_cerrar_modal_no_pulsa_a_ciegas", FG],
         viejo="    const x = [...dlg.querySelectorAll('[aria-label*=close i],[class*=close i]')]",
         nuevo="    const x = [...dlg.querySelectorAll('button,[aria-label*=close i],[class*=close i]')]"),
    dict(id="one-cierre-no-corta", pruebas=[O1 + "test_cerrar_modal_corta_antes_de_la_guarda_y_no_despues"],
         viejo='                raise ObjetivoNoEncontrado("Cerrar la ventana emergente de ONE", buscaba)\n',
         nuevo="                return False\n"),
    dict(id="one-cierre-corta-tras-la-guarda", pruebas=[SC + "test_lo_que_corta_no_se_llama_despues_de_la_guarda"],
         viejo="            _cerrar_modal_one(page, reg, antes_de_la_guarda=False)\n",
         nuevo="            _cerrar_modal_one(page, reg)\n"),
    dict(id="one-contrato-el-primero", pruebas=[O1 + "test_js_contrato_no_elige_el_primero", FG],
         viejo="    return 'sin-contrato';\n", nuevo="    opts[0].click(); return 'first';\n"),
    dict(id="one-contrato-no-corta", pruebas=[O1 + "test_contrato_sin_objetivo_corta"],
         viejo='        if elegido == "sin-contrato":\n            raise',
         nuevo='        if False:\n            raise'),
    dict(id="one-campo-contrato-a-ciegas", pruebas=[O1 + "test_contrato_sin_objetivo_corta", FG],
         viejo="            if not inp.count():\n                raise ObjetivoNoEncontrado(\"Contrato de ONE\"",
         nuevo="            if not inp.count():\n"
               "                inp = page.locator(\"input.mag-input__input:not(#startDate)\").first\n"
               "            if not inp.count():\n                raise ObjetivoNoEncontrado(\"Contrato de ONE\""),
]

# --- MSC: el HS Code y el Commodity ya no eligen la primera sugerencia ---
M1 = "test_clics.TestMsc."

MUTACIONES += [
    dict(id="msc-sin-decorador", pruebas=[SC + "test_cada_reservador_que_corta_esta_decorado"],
         viejo='@_sin_clic_a_ciegas("msc")\n', nuevo=""),
    dict(id="msc-hs-el-primero", pruebas=[M1 + "test_js_hs_elige_el_salmon_o_nada", FG],
         viejo="        const target = items.find(e => /atlantic salmon|salmo salar/i.test(e.textContent || ''));\n",
         nuevo="        const target = items.find(e => /atlantic salmon|salmo salar/i.test(e.textContent || '')) || items[0];\n"),
    dict(id="msc-hs-no-corta", pruebas=[M1 + "test_hs_sin_salmon_corta"],
         viejo='        if elegido == "sin-salmon":\n            raise', nuevo='        if False:\n            raise'),
    dict(id="msc-hs-corta-antes-de-tiempo", pruebas=[M1 + "test_hs_sin_salmon_corta"],
         viejo='            if elegido and elegido != "sin-salmon":\n', nuevo="            if elegido:\n"),
    dict(id="msc-kendo-la-primera", pruebas=[M1 + "test_js_kendo_elige_por_texto_o_nada", FG],
         viejo="    const el=items.find(e=>(e.textContent||'').toUpperCase().includes(txt.toUpperCase()));\n",
         nuevo="    const el=items.find(e=>(e.textContent||'').toUpperCase().includes(txt.toUpperCase())) || items[0];\n"),
    dict(id="msc-kendo-no-corta", pruebas=[M1 + "test_kendo_sin_coincidencia_corta"],
         viejo='        if picked == "sin-coincidencia":\n            raise', nuevo='        if False:\n            raise'),
    dict(id="msc-kendo-corta-antes-de-tiempo", pruebas=[M1 + "test_kendo_sin_coincidencia_corta"],
         viejo='            if picked and picked != "sin-coincidencia":\n', nuevo="            if picked:\n"),
]

# --- CMA: la sección Reefer, «Tamaño y tipo», el peso, el itinerario sin nave e «I Agree» ---
C1 = "test_clics.TestCma."
ABRE_REEFER_CMA = "        for selector in (\n            \"button:has-text('Modifique el reefer')\",\n        ):\n"
TEMPERATURA_CMA_CORTA = "        if donde != \"ok\":\n            raise ObjetivoNoEncontrado(\"Temperatura Reefer de CMA\""

MUTACIONES += [
    dict(id="cma-sin-decorador", pruebas=[SC + "test_cada_reservador_que_corta_esta_decorado"],
         viejo='@_sin_clic_a_ciegas("cma")\n', nuevo=""),
    dict(id="cma-tamano-el-primer-desplegable", pruebas=[C1 + "test_tamano_y_tipo_no_abre_el_primer_desplegable", FG],
         viejo="            \"input[placeholder*='Seleccionar' i]\",\n            \".el-form-item:has-text('Tamaño y tipo') input\",\n",
         nuevo="            \"input[placeholder*='Seleccionar' i]\",\n            \".el-select input\",\n"
               "            \".el-form-item:has-text('Tamaño y tipo') input\",\n"),
    dict(id="cma-tamano-no-corta", pruebas=[C1 + "test_tamano_y_tipo_no_abre_el_primer_desplegable"],
         viejo='        if not abierto:\n            raise ObjetivoNoEncontrado("Tamaño y tipo de CMA"',
         nuevo='        if False:\n            raise ObjetivoNoEncontrado("Tamaño y tipo de CMA"'),
    dict(id="cma-peso-cualquier-bloque", pruebas=[C1 + "test_peso_solo_por_su_etiqueta", FG],
         viejo="                \".el-form-item:has-text('Peso por contenedor') input\",\n",
         nuevo="                \".el-form-item:has-text('Peso por contenedor') input\",\n"
               "                \"div:has-text('Peso por contenedor') >> input\",\n"),
    dict(id="cma-peso-no-corta", pruebas=[C1 + "test_peso_solo_por_su_etiqueta"],
         viejo="        if not peso_ok:\n            # Hasta 83067a1",
         nuevo="        if False:\n            # Hasta 83067a1"),
    dict(id="cma-itinerario-el-primero", pruebas=[C1 + "test_itinerario_sin_nave_no_elige_el_primero", FG],
         viejo='        raise ObjetivoNoEncontrado("Itinerario de CMA"',
         nuevo="        res = page.evaluate(\"() => { const btns = [...document.querySelectorAll('button, a')]; "
               "btns[0].click(); return {ok: true, msg: 'primer itinerario seleccionado'}; }\")\n"
               "        return True, res.get(\"msg\")\n"
               '        raise ObjetivoNoEncontrado("Itinerario de CMA"'),
    dict(id="cma-reefer-abre-a-ciegas", pruebas=[C1 + "test_reefer_corta_en_cada_paso_sin_pulsar_a_ciegas", FG],
         viejo=ABRE_REEFER_CMA,
         nuevo=ABRE_REEFER_CMA.replace("        for selector in (\n",
                                       "        for selector in (\n            \"div:has-text('Reefer') button\",\n")),
    dict(id="cma-reefer-no-corta-al-abrir", pruebas=[C1 + "test_reefer_corta_en_cada_paso_sin_pulsar_a_ciegas"],
         viejo='        if not abierto:\n            raise ObjetivoNoEncontrado("Sección Reefer de CMA"',
         nuevo='        if False:\n            raise ObjetivoNoEncontrado("Sección Reefer de CMA"'),
    dict(id="cma-reefer-temperatura-el-primer-input", pruebas=[C1 + "test_reefer_corta_en_cada_paso_sin_pulsar_a_ciegas", FG],
         viejo=TEMPERATURA_CMA_CORTA,
         nuevo="        if donde != \"ok\" and page.locator(\".el-drawer input\").first.is_visible():\n"
               "            page.locator(\".el-drawer input\").first.click(timeout=2000)\n"
               "            donde = \"ok\"\n" + TEMPERATURA_CMA_CORTA),
    dict(id="cma-reefer-temperatura-en-toda-la-pagina", pruebas=[C1 + "test_reefer_corta_en_cada_paso_sin_pulsar_a_ciegas"],
         viejo=TEMPERATURA_CMA_CORTA,
         nuevo="        if donde != \"ok\" and page.locator(\"input[placeholder*='Temperature' i]\").first.is_visible():\n"
               "            page.locator(\"input[placeholder*='Temperature' i]\").first.fill(temp)\n"
               "            donde = \"ok\"\n" + TEMPERATURA_CMA_CORTA),
    dict(id="cma-reefer-temperatura-no-corta", pruebas=[C1 + "test_reefer_corta_en_cada_paso_sin_pulsar_a_ciegas"],
         viejo=TEMPERATURA_CMA_CORTA, nuevo=TEMPERATURA_CMA_CORTA.replace("if donde != \"ok\":", "if False:")),
    dict(id="cma-reefer-temperatura-sigue-sin-ok", pruebas=[C1 + "test_reefer_corta_en_cada_paso_sin_pulsar_a_ciegas"],
         viejo=TEMPERATURA_CMA_CORTA,
         nuevo=TEMPERATURA_CMA_CORTA.replace("if donde != \"ok\":", "if donde in _CMA_TEMPERATURA_NO_HALLADA:")),
    dict(id="cma-reefer-temperatura-no-dice-que-falto", pruebas=[C1 + "test_reefer_corta_en_cada_paso_sin_pulsar_a_ciegas"],
         viejo="_CMA_TEMPERATURA_NO_HALLADA.get(\n                donde, ",
         nuevo="_CMA_TEMPERATURA_NO_HALLADA.get(\n                \"sin-campo\", "),
    dict(id="cma-reefer-temperatura-primer-contenedor", pruebas=[C1 + "test_js_temperatura_solo_en_el_panel_visible"],
         viejo="    const vis = [...document.querySelectorAll('.el-drawer, [class*=\"drawer\"], [role=\"dialog\"]')]"
               ".filter(visible);\n",
         nuevo="    const vis = [document.querySelector('.el-drawer, [class*=\"drawer\"], [role=\"dialog\"]')]"
               ".filter(Boolean);\n"),
    dict(id="cma-reefer-temperatura-cuenta-ocultos", pruebas=[C1 + "test_js_temperatura_solo_en_el_panel_visible"],
         viejo="[role=\"dialog\"]')].filter(visible);\n", nuevo="[role=\"dialog\"]')];\n"),
    dict(id="cma-reefer-temperatura-cuenta-visibility-hidden",
         pruebas=[C1 + "test_js_temperatura_solo_en_el_panel_visible"],
         viejo=" && getComputedStyle(e).visibility !== 'hidden';", nuevo=";"),
    dict(id="cma-reefer-temperatura-elige-entre-varios", pruebas=[C1 + "test_js_temperatura_solo_en_el_panel_visible"],
         viejo="    if (paneles.length > 1) return 'varios-paneles';\n", nuevo=""),
    dict(id="cma-reefer-temperatura-cuenta-anidados", pruebas=[C1 + "test_js_temperatura_solo_en_el_panel_visible"],
         viejo="    const paneles = vis.filter(p => !vis.some(q => q !== p && q.contains(p)));",
         nuevo="    const paneles = vis;"),
    dict(id="cma-reefer-temperatura-sin-panel-busca-en-la-pagina",
         pruebas=[C1 + "test_js_temperatura_solo_en_el_panel_visible"],
         viejo="    if (paneles.length === 0) return 'sin-panel';\n",
         nuevo="    if (paneles.length === 0) paneles.push(document);\n"),
    dict(id="cma-i-agree-cualquier-casilla", pruebas=[C1 + "test_i_agree_solo_por_su_texto", FG],
         viejo="        \".el-checkbox:has-text('I Agree')\",\n    ]:\n",
         nuevo="        \".el-checkbox:has-text('I Agree')\",\n        \"input[type='checkbox']\",\n    ]:\n"),
    dict(id="cma-i-agree-no-corta", pruebas=[C1 + "test_i_agree_solo_por_su_texto"],
         viejo='    raise ObjetivoNoEncontrado("«I Agree» de CMA", "la casilla «I Agree» (por su texto)")\n',
         nuevo="    return False\n"),
]

# --- COSCO: los mensajes de «hecho» solo si el clic ocurrió ---
K1 = "test_clics.TestCosco."

MUTACIONES += [
    dict(id="cosco-perfil-dice-ok-aunque-falle", pruebas=[K1 + "test_js_perfil_dice_si_pulso"],
         viejo="        try { cb.click(); return 'ok'; } catch(e) { return 'fallo'; }\n",
         nuevo="        try { cb.click(); } catch(e) {}\n        return 'ok';\n"),
    dict(id="cosco-js-opcion-no-dice", pruebas=[K1 + "test_js_pulsar_opcion_dice_si_pulso"],
         viejo="if (!el) return false; el.click(); return true; }\"", nuevo="if (el) el.click(); return true; }\""),
    dict(id="cosco-opcion-dice-elegida-sin-pulsar", pruebas=[K1 + "test_opcion_solo_se_anuncia_si_se_pulso"],
         viejo="        if not pulso:\n            # Hasta 83067a1", nuevo="        if False:\n            # Hasta 83067a1"),
]

# --- COSCO: el CONTROL lee Size Type por su desplegable y, si no puede, dice «no pude leer», nunca «VACÍO» ---
K2 = "test_clics.TestControlCosco."
LEE_SIZE_TYPE = K2 + "test_size_type_dice_no_pude_leer_nunca_vacio"
JS_DESPLEGABLE = K2 + "test_js_desplegable_por_su_placeholder"

MUTACIONES += [
    dict(id="cosco-control-size-type-dice-vacio", pruebas=[LEE_SIZE_TYPE],
         viejo="        if etiqueta in _COSCO_CONTROL_POR_DESPLEGABLE and not real:\n", nuevo="        if False:\n"),
    dict(id="cosco-control-todos-no-pude-leer", pruebas=[LEE_SIZE_TYPE],
         viejo="        if etiqueta in _COSCO_CONTROL_POR_DESPLEGABLE and not real:\n", nuevo="        if not real:\n"),
    dict(id="cosco-control-sin-desplegable", pruebas=[LEE_SIZE_TYPE],
         viejo="        if etiqueta in _COSCO_CONTROL_POR_DESPLEGABLE:\n            visto = ",
         nuevo="        if False:\n            visto = "),
    dict(id="cosco-control-sin-respaldo-por-etiqueta", pruebas=[LEE_SIZE_TYPE],
         viejo="            if visto:\n                return str(visto).strip()\n",
         nuevo="            return str(visto or \"\").strip()\n"),
    dict(id="cosco-control-lectura-rota-corta", pruebas=[LEE_SIZE_TYPE],
         viejo="    except Exception:\n        return None\n    return None if real is None else str(real).strip()",
         nuevo="    except ZeroDivisionError:\n        return None\n    return None if real is None else str(real).strip()"),
    dict(id="cosco-control-sin-aviso", pruebas=[LEE_SIZE_TYPE],
         viejo="    if sin_leer:\n        reg.paso(", nuevo="    if False:\n        reg.paso("),
    dict(id="cosco-js-desplegable-el-primero", pruebas=[JS_DESPLEGABLE],
         viejo="    if (campos.length !== 1) return null;\n", nuevo="    if (!campos.length) return null;\n"),
    dict(id="cosco-js-desplegable-cuenta-ocultos", pruebas=[JS_DESPLEGABLE],
         viejo="e.offsetParent !== null && (e.placeholder || '').toUpperCase().includes(E)",
         nuevo="(e.placeholder || '').toUpperCase().includes(E)"),
    dict(id="cosco-js-desplegable-placeholder-anclado", pruebas=[JS_DESPLEGABLE],
         viejo="(e.placeholder || '').toUpperCase().includes(E)",
         nuevo="(e.placeholder || '').toUpperCase().startsWith(E)"),
    dict(id="cosco-js-desplegable-texto-vacio", pruebas=[JS_DESPLEGABLE],
         viejo="    return (campos[0].value || '').trim() || null;\n", nuevo="    return (campos[0].value || '').trim();\n"),
]

# --- HYUNDAI: los mensajes de «hecho» solo si el clic ocurrió ---
H1 = "test_clics.TestHyundai."

MUTACIONES += [
    dict(id="hmm-marcar-dice-no-sin-marcar", pruebas=[H1 + "test_los_mensajes_dicen_lo_que_paso"],
         viejo='        elif page.evaluate(_JS_HMM_MARCAR_POR_ID, id_campo):\n            reg.info(f"{nombre}: No (js)")\n'
               '        else:\n            reg.info(f"{nombre}: no encontré',
         nuevo='        else:\n            page.evaluate(_JS_HMM_MARCAR_POR_ID, id_campo)\n            reg.info(f"{nombre}: No (js)")\n'
               '        if False:\n            reg.info(f"{nombre}: no encontré'),
    dict(id="hmm-js-marcar-no-dice", pruebas=[H1 + "test_js_dicen_lo_que_hicieron"],
         viejo="    if (!el) return false;\n    el.checked = true; el.dispatchEvent(new Event('change', {bubbles:true}));\n    return true;\n",
         nuevo="    if (el) { el.checked = true; el.dispatchEvent(new Event('change', {bubbles:true})); }\n    return true;\n"),
    dict(id="hmm-correo-activado-siempre", pruebas=[H1 + "test_los_mensajes_dicen_lo_que_paso"],
         viejo="        r = page.evaluate(_JS_HMM_AVISO_CORREO)\n",
         nuevo="        page.evaluate(_JS_HMM_AVISO_CORREO)\n        r = \"marcado\"\n"),
    dict(id="hmm-js-correo-no-dice", pruebas=[H1 + "test_js_dicen_lo_que_hicieron"],
         viejo="    if (!el) return '';\n    if (el.checked) return 'ya';\n    el.click();\n    return 'marcado';\n",
         nuevo="    if (el && !el.checked) el.click();\n    return 'marcado';\n"),
    dict(id="hmm-residuo-dice-sin-marcar", pruebas=[H1 + "test_los_mensajes_dicen_lo_que_paso"],
         viejo='        elif page.evaluate(_JS_HMM_NO_RESIDUO):\n            reg.info("Scrap/Waste: Non-waste (js)")\n'
               '        else:\n            reg.info("Scrap/Waste: no encontré',
         nuevo='        else:\n            page.evaluate(_JS_HMM_NO_RESIDUO)\n            reg.info("Scrap/Waste: Non-waste (js)")\n'
               '        if False:\n            reg.info("Scrap/Waste: no encontré'),
    dict(id="hmm-js-residuo-no-dice", pruebas=[H1 + "test_js_dicen_lo_que_hicieron"],
         viejo="    if (!el) return false;\n    const inp = el.querySelector('input') || el;\n    inp.click();\n    return true;\n",
         nuevo="    if (el) { const inp = el.querySelector('input') || el; inp.click(); }\n    return true;\n"),
]

# --- La evidencia antes de la guarda (CICLO-evidencia-en-la-guarda.md) ---
EG = "test_evidencia.TestEvidenciaEnLaGuarda."
LD = "test_evidencia.TestCadaReservadorLaDeja."
CAPTURA_EG = "        png = reg.captura(page, nombre, pagina_entera=completa)\n"
HTML_EG = "        guardados, total, sin_shadow = _guardar_html_completo(page, reg, nombre, momento)\n"
FALLA_EG = ('        reg.paso(f"⚠ No pude guardar la evidencia {momento} ({nombre}): {_texto_error(e)}. '
            '{_EVIDENCIA_SIGUE}")\n')
TRY_EG = "    try:\n" + CAPTURA_EG + HTML_EG + "    except Exception as e:\n" + FALLA_EG + "        return\n"

MUTACIONES += [
    # Lo que guarda: la página completa y el HTML de la página y de cada marco.
    dict(id="guarda-captura-de-la-ventana", pruebas=[EG + "test_captura_de_la_pagina_completa_y_html_de_la_pagina_y_los_marcos",
                                                     EG + "test_solo_lee_sin_clics_ni_navegacion_ni_esperas"],
         viejo=CAPTURA_EG, nuevo="        png = reg.captura(page, nombre, full=True)\n"),
    dict(id="captura-no-fuerza-la-pagina-entera",
         pruebas=[EG + "test_captura_de_la_pagina_completa_y_html_de_la_pagina_y_los_marcos"],
         viejo="full_page=completa or bool(pagina_entera))", nuevo="full_page=completa)"),
    dict(id="guarda-sin-html", pruebas=[EG + "test_captura_de_la_pagina_completa_y_html_de_la_pagina_y_los_marcos",
                                        EG + "test_si_la_captura_falla_avisa_y_la_reserva_sigue"],
         viejo=HTML_EG, nuevo="        guardados, total, sin_shadow = 1, 1, 0\n"),
    dict(id="guarda-otro-javascript", pruebas=[EG + "test_solo_lee_sin_clics_ni_navegacion_ni_esperas"],
         viejo="html = str((alcance.evaluate(_JS_HTML_COMPLETO) or {}).get(\"html\") or \"\")",
         nuevo="html = str((alcance.evaluate(_JS_HTML_COMPLETO) or {}).get(\"html\") or \"\"); "
               "alcance.evaluate(\"window.scrollTo(0, 0)\")"),
    # Solo lee: ni esperas ni teclas.
    dict(id="guarda-con-espera", pruebas=[EG + "test_solo_lee_sin_clics_ni_navegacion_ni_esperas"],
         viejo=CAPTURA_EG, nuevo="        page.wait_for_timeout(300)\n" + CAPTURA_EG),
    dict(id="guarda-con-tecla", pruebas=[EG + "test_solo_lee_sin_clics_ni_navegacion_ni_esperas"],
         viejo=CAPTURA_EG, nuevo="        page.keyboard.press(\"Escape\")\n" + CAPTURA_EG),
    # Nunca corta el flujo, y avisa lo que falta.
    dict(id="guarda-falla-corta", pruebas=[EG + "test_si_todo_falla_no_corta_el_flujo"],
         viejo=TRY_EG, nuevo="    png = reg.captura(page, nombre, pagina_entera=completa)\n"
                             "    guardados, total, sin_shadow = _guardar_html_completo(page, reg, nombre, momento)\n"),
    dict(id="guarda-falla-callada", pruebas=[EG + "test_si_todo_falla_no_corta_el_flujo"],
         viejo=FALLA_EG, nuevo="        pass\n"),
    dict(id="guarda-incompleta-callada", pruebas=[EG + "test_si_la_captura_falla_avisa_y_la_reserva_sigue",
                                                  EG + "test_si_un_html_falla_avisa_y_la_reserva_sigue"],
         viejo="    if png and guardados == total:\n", nuevo="    if True:\n"),
    dict(id="captura-dice-que-guardo-aunque-falle", pruebas=[EG + "test_si_la_captura_falla_avisa_y_la_reserva_sigue"],
         viejo='            self._emit(f"    (no pude capturar {nombre}: {e})")\n            return False\n',
         nuevo='            self._emit(f"    (no pude capturar {nombre}: {e})")\n            return True\n'),
    dict(id="guarda-aviso-sin-que-hacer", pruebas=[EG + "test_si_todo_falla_no_corta_el_flujo",
                                                   EG + "test_si_la_captura_falla_avisa_y_la_reserva_sigue"],
         viejo='_EVIDENCIA_SIGUE = ("La reserva sigue igual; si necesitas medir esta pantalla, vuelve a correr la fila con el "\n'
               '                    "candado cerrado.")',
         nuevo='_EVIDENCIA_SIGUE = "La reserva sigue igual."'),
    # Cada reservador la deja justo antes de su guarda, con su prefijo y la fila; y solo ahí.
    dict(id="guarda-one-sin-evidencia", pruebas=[LD + "test_one", LD + "test_solo_ahi"],
         viejo='        _evidencia_antes_de_la_guarda(page, reg, f"one_f{f}_guarda")\n', nuevo=""),
    dict(id="guarda-msc-sin-evidencia", pruebas=[LD + "test_msc", LD + "test_solo_ahi"],
         viejo='    _evidencia_antes_de_la_guarda(page, reg, f"msc_f{f}_guarda")\n', nuevo=""),
    dict(id="guarda-cma-sin-evidencia", pruebas=[LD + "test_cma", LD + "test_solo_ahi"],
         viejo='        _evidencia_antes_de_la_guarda(page, reg, f"cma_f{f}_guarda")\n', nuevo=""),
    dict(id="guarda-cosco-sin-evidencia", pruebas=[LD + "test_cosco", LD + "test_solo_ahi"],
         viejo='    _evidencia_antes_de_la_guarda(page, reg, f"cosco_f{f}_guarda")\n', nuevo=""),
    dict(id="guarda-hyundai-sin-evidencia", pruebas=[LD + "test_hyundai", LD + "test_solo_ahi"],
         viejo='    _evidencia_antes_de_la_guarda(page, reg, f"hmm_f{f}_guarda")\n', nuevo=""),
    dict(id="guarda-maersk-sin-evidencia", pruebas=[LD + "test_maersk", LD + "test_solo_ahi"],
         viejo='    _evidencia_antes_de_la_guarda(page, reg, f"mk_f{f}_guarda")\n', nuevo=""),
    dict(id="guarda-msc-despues-de-la-guarda", pruebas=[LD + "test_msc"],
         viejo='    _evidencia_antes_de_la_guarda(page, reg, f"msc_f{f}_guarda")\n    if not es_modo_emision():\n',
         nuevo='    if not es_modo_emision():\n        _evidencia_antes_de_la_guarda(page, reg, f"msc_f{f}_guarda")\n'),
    dict(id="guarda-cma-sin-la-fila", pruebas=[LD + "test_cma"],
         viejo='f"cma_f{f}_guarda"', nuevo='"cma_guarda"'),
    dict(id="guarda-maersk-decide-con-la-evidencia", pruebas=[LD + "test_maersk"],
         viejo='    _evidencia_antes_de_la_guarda(page, reg, f"mk_f{f}_guarda")\n',
         nuevo='    modo = _evidencia_antes_de_la_guarda(page, reg, f"mk_f{f}_guarda") or modo\n'),
    dict(id="guarda-tambien-tras-el-envio", pruebas=[LD + "test_solo_ahi"],
         viejo=EVIDENCIA, nuevo="    _evidencia_antes_de_la_guarda(page, reg, evidencia)\n" + EVIDENCIA),
]

# --- El HTML junto a la captura del paso sin objetivo (CICLO-evidencia-en-la-guarda.md) ---
HS = "test_evidencia.TestHtmlSinObjetivo."

MUTACIONES += [
    dict(id="corte-sin-html", pruebas=[HS + "test_el_html_queda_junto_a_la_captura", LD + "test_solo_ahi"],
         viejo=EVIDENCIA_CORTE,
         nuevo="                reg.captura(page, f\"{prefijo}_f{(reserva or {}).get('fila')}_sin_objetivo\")\n"),
    dict(id="corte-captura-de-pagina-entera", pruebas=[HS + "test_el_html_queda_junto_a_la_captura"],
         viejo=EVIDENCIA_CORTE, nuevo=EVIDENCIA_CORTE.replace("completa=False", "completa=True")),
    dict(id="corte-evidencia-sin-proteger", pruebas=[HS + "test_si_la_evidencia_falla_igual_queda_no_enviada"],
         viejo=EVIDENCIA_CORTE,
         nuevo="                reg.captura(page, f\"{prefijo}_f{(reserva or {}).get('fila')}_sin_objetivo\")\n"
               "                _guardar_html_completo(page, reg, f\"{prefijo}_f{(reserva or {}).get('fila')}_sin_objetivo\","
               " \"en el paso sin objetivo\")\n"),
]

# --- La poda del HTML viejo de logs/ y las corridas de referencia (CICLO-evidencia-en-la-guarda.md) ---
PO = "test_evidencia.TestPodaHtml."
RF = "test_evidencia.TestCorridasDeReferencia."
SOLO_HTML = '            if not (a.is_file(follow_symlinks=False) and a.name.endswith(".html")):\n'
LISTA_PODA = "            archivos = sorted(os.scandir(c.path), key=lambda e: e.name)\n"
ERROR_PODA = '                errores.append(f"«{c.name}/{a.name}» ({type(err).__name__}: {err})")\n'
BORRA = "test_borra_solo_los_html_de_las_corridas_de_mas_de_30_dias"

MUTACIONES += [
    # Qué borra: solo los .html directos de la carpeta, con más de 30 días.
    dict(id="poda-borra-todo", pruebas=[PO + BORRA, RF + "test_la_poda_no_las_toca"],
         viejo=SOLO_HTML, nuevo="            if not a.is_file(follow_symlinks=False):\n"),
    dict(id="poda-recursiva", pruebas=[PO + BORRA],
         viejo=LISTA_PODA,
         nuevo="            archivos = sorted((e for d, _, _ in os.walk(c.path) for e in os.scandir(d)), key=lambda e: e.path)\n"),
    dict(id="poda-sin-antiguedad", pruebas=[PO + BORRA],
         viejo="        if ahora - fecha <= datetime.timedelta(days=HTML_DIAS):\n            continue\n", nuevo=""),
    dict(id="poda-29-dias", pruebas=[PO + BORRA], viejo="HTML_DIAS = 30\n", nuevo="HTML_DIAS = 29\n"),
    dict(id="poda-31-dias", pruebas=[PO + BORRA], viejo="HTML_DIAS = 30\n", nuevo="HTML_DIAS = 31\n"),
    # Dónde: solo carpetas de corrida directas de logs/, sin seguir uniones ni enlaces, y nunca las de referencia.
    dict(id="poda-patron-flojo", pruebas=[PO + BORRA],
         viejo=r'PATRON_CORRIDA = r"(.+)_(\d{8}_\d{6})(?:_\d+)?"', nuevo=r'PATRON_CORRIDA = r"(.+)_(\d{8}_\d{6}).*"'),
    dict(id="poda-sigue-uniones", pruebas=[PO + BORRA],
         viejo=" or c.is_junction():\n", nuevo=":\n"),
    dict(id="poda-sigue-enlaces", pruebas=[PO + BORRA],
         viejo="not c.is_dir(follow_symlinks=False)", nuevo="not c.is_dir()"),
    dict(id="poda-toca-referencia", pruebas=[RF + "test_la_poda_no_las_toca"],
         viejo=" or _es_de_referencia(c.name)", nuevo=""),
    dict(id="referencia-falta-una", pruebas=[RF + "test_son_las_que_nombran_los_generadores"],
         viejo='    "web_cosco_*_20260922_134605",\n', nuevo=""),
    # Lo que no se puede borrar queda y se cuenta; sin logs/ no hace nada.
    dict(id="poda-un-error-corta", pruebas=[PO + "test_lo_que_no_se_puede_borrar_queda_y_se_cuenta"],
         viejo=ERROR_PODA, nuevo="                raise\n"),
    dict(id="poda-error-callado", pruebas=[PO + "test_lo_que_no_se_puede_borrar_queda_y_se_cuenta"],
         viejo=ERROR_PODA, nuevo="                pass\n"),
    dict(id="poda-sin-logs-falla", pruebas=[PO + "test_sin_logs_no_hace_nada"],
         viejo="    if not logs.is_dir():\n        return borrados, errores\n", nuevo=""),
    # Al empezar cada corrida de reservas: avisa y nunca la detiene.
    dict(id="poda-corrida-no-avisa", pruebas=[PO + "test_al_empezar_la_corrida_avisa_y_nunca_la_detiene"],
         viejo="    if borrados:\n        reg.info(f\"Borré {len(borrados)} HTML", nuevo="    if False:\n        reg.info(f\"Borré {len(borrados)} HTML"),
    dict(id="poda-corrida-falla-corta", pruebas=[PO + "test_al_empezar_la_corrida_avisa_y_nunca_la_detiene"],
         viejo="    except Exception as e:                  # la poda nunca impide correr\n",
         nuevo="    except ZeroDivisionError as e:          # la poda nunca impide correr\n"),
    dict(id="poda-corrida-error-callado", pruebas=[PO + "test_al_empezar_la_corrida_avisa_y_nunca_la_detiene"],
         viejo='        reg.paso(f"⚠ No pude borrar el HTML antiguo {error}; bórralo a mano si sobra.")\n', nuevo="        pass\n"),
    dict(id="poda-no-corre-en-la-consola", pruebas=[PO + "test_corre_al_empezar_cada_corrida_de_reservas"],
         viejo='    reg.paso(f"INICIO RESERVAS · {nombre} · usuario={usuario}")\n    _podar_html_viejo(reg)\n',
         nuevo='    reg.paso(f"INICIO RESERVAS · {nombre} · usuario={usuario}")\n'),
    dict(id="poda-no-corre-en-la-web", pruebas=[PO + "test_corre_al_empezar_cada_corrida_de_reservas"],
         viejo='        reg.paso(f"INICIO · {hoja} · operador {usuario} · {len(elegidas)} reserva(s)")\n        _podar_html_viejo(reg)\n',
         nuevo='        reg.paso(f"INICIO · {hoja} · operador {usuario} · {len(elegidas)} reserva(s)")\n'),
]

# --- CMA: la evidencia dentro del panel Reefer (CICLO-cma-reefer-y-fecha-maersk.md) ---
ER_ = "test_evidencia.TestEvidenciaReefer."
PANEL_R = ('        _evidencia_antes_de_la_guarda(page, reg, f"cma_f{f}_reefer_panel", "en el panel Reefer", '
           'completa=False)\n')
GUARDADO_R = ('        _evidencia_antes_de_la_guarda(page, reg, f"cma_f{f}_reefer_guardado", "tras guardar el panel Reefer",\n'
              '                                      completa=False)\n')
PANEL_Y_GUARDADO = ER_ + "test_el_panel_abierto_y_tras_guardarlo"

MUTACIONES += [
    dict(id="reefer-sin-evidencia-del-panel", pruebas=[PANEL_Y_GUARDADO, LD + "test_solo_ahi"],
         viejo=PANEL_R, nuevo=""),
    dict(id="reefer-sin-evidencia-de-lo-guardado",
         pruebas=[PANEL_Y_GUARDADO, LD + "test_solo_ahi"],
         viejo=GUARDADO_R, nuevo=""),
    dict(id="reefer-panel-de-pagina-entera", pruebas=[PANEL_Y_GUARDADO],
         viejo=PANEL_R, nuevo=PANEL_R.replace("completa=False", "completa=True")),
    dict(id="reefer-guardado-de-pagina-entera", pruebas=[PANEL_Y_GUARDADO],
         viejo=GUARDADO_R, nuevo=GUARDADO_R.replace("completa=False", "completa=True")),
    dict(id="reefer-evidencia-con-espera", pruebas=[PANEL_Y_GUARDADO],
         viejo=PANEL_R, nuevo="        esperar(page, 0.5)\n" + PANEL_R),
    dict(id="reefer-evidencia-con-tecla", pruebas=[PANEL_Y_GUARDADO],
         viejo=PANEL_R, nuevo='        page.keyboard.press("Escape")\n' + PANEL_R),
    dict(id="reefer-guardado-antes-de-guardar", pruebas=[PANEL_Y_GUARDADO],
         cambios=[(GUARDADO_R, ""),
                  ("        # 3. Guardar: el único botón «Guardar» a la vista",
                   GUARDADO_R + "        # 3. Guardar: el único botón «Guardar» a la vista")]),
    dict(id="reefer-panel-sin-proteger", pruebas=[ER_ + "test_si_la_evidencia_falla_el_panel_se_configura_igual"],
         viejo=PANEL_R,
         nuevo='        reg.captura(page, f"cma_f{f}_reefer_panel")\n'
               '        _guardar_html_completo(page, reg, f"cma_f{f}_reefer_panel", "en el panel Reefer")\n'),
    dict(id="reefer-guardado-sin-proteger", pruebas=[ER_ + "test_si_la_evidencia_falla_el_panel_se_configura_igual"],
         viejo=GUARDADO_R,
         nuevo='        reg.captura(page, f"cma_f{f}_reefer_guardado")\n'
               '        _guardar_html_completo(page, reg, f"cma_f{f}_reefer_guardado", "tras guardar el panel Reefer")\n'),
]

# --- MAERSK: corta si no llega a la revisión, y no elige la fecha de retiro (CICLO-maersk-corta-en-la-revision.md) ---
MK = "test_clics.TestMaersk."
CORTE_MK = ('    raise ObjetivoNoEncontrado("Revisión de MAERSK", "la pantalla de revisión («Review booking»), que no "\n'
            '                                                     "apareció en 15 s", pide=_mk_lo_que_pide(page))\n')
ESPERA_MK = '    for _ in range(30):\n        esperar(page, 0.5)\n        if "/review" in page.url.lower():\n            return\n'
LLAMADA_MK = "        _mk_esperar_revision(page)\n"
DETALLES_MK = ("            # 2) La referencia de retiro, en su campo por su name (_mk_referencia_de_retiro; "
               "decisión de Marcelo,\n")

MUTACIONES += [
    dict(id="maersk-sin-decorador", pruebas=[SC + "test_cada_reservador_que_corta_esta_decorado"],
         viejo='@_sin_clic_a_ciegas("mk")\ndef reservar_maersk(', nuevo="def reservar_maersk("),
    dict(id="maersk-revision-no-corta",
         pruebas=[MK + "test_revision_que_no_aparece_corta", MK + "test_el_corte_queda_no_enviada_con_captura_y_html"],
         viejo=CORTE_MK, nuevo="    return\n"),
    dict(id="maersk-revision-otro-motivo",
         pruebas=[MK + "test_revision_que_no_aparece_corta", MK + "test_el_corte_queda_no_enviada_con_captura_y_html"],
         viejo=CORTE_MK, nuevo='    raise ObjetivoNoEncontrado("Revisión de MAERSK", "la revisión")\n'),
    dict(id="maersk-revision-mas-corta", pruebas=[MK + "test_revision_que_no_aparece_corta"],
         viejo=ESPERA_MK, nuevo=ESPERA_MK.replace("range(30)", "range(20)")),
    dict(id="maersk-revision-sin-espera",
         pruebas=[MK + "test_revision_que_no_aparece_corta", MK + "test_revision_que_aparece_sigue"],
         viejo=ESPERA_MK, nuevo=ESPERA_MK.replace("        esperar(page, 0.5)\n", "")),
    # Desde el encargo 36, reservar_maersk también corta en la fecha de retiro (_mk_fecha_de_retiro): sin esta espera,
    # igual necesita el decorador, y test_cada_reservador_que_corta_esta_decorado ya no cae.
    dict(id="maersk-espera-sin-cortar", pruebas=[MK + "test_espera_la_revision_antes_de_los_terminos"],
         viejo=LLAMADA_MK,
         nuevo='        for _ in range(30):\n            esperar(page, 0.5)\n            if "/review" in page.url.lower():\n'
               '                break\n'),
    dict(id="maersk-corta-despues-de-los-terminos", pruebas=[MK + "test_espera_la_revision_antes_de_los_terminos"],
         cambios=[(LLAMADA_MK, ""),
                  ("        corte = _mk_marcar_terminos(page, reg, f)\n        if corte:\n            return corte\n",
                   "        corte = _mk_marcar_terminos(page, reg, f)\n        if corte:\n            return corte\n"
                   + LLAMADA_MK)]),
    # Hasta el encargo 36, «maersk-vuelve-a-elegir-la-fecha» y «maersk-anuncia-la-fecha» cuidaban que no se eligiera la
    # fecha de retiro (test_no_elige_la_fecha_de_retiro). Ahora se elige, por su fecha (TestRetiroMaersk, abajo); el
    # primer día sin mirar su fecha sigue siendo un clic genérico que la foto ve.
    dict(id="maersk-vuelve-el-primer-dia", pruebas=[FG],
         viejo=DETALLES_MK,
         nuevo='            page.evaluate("() => { const dias = document.querySelectorAll(\'[role=gridcell]\'); '
               'if (dias.length) dias[0].click(); }")\n' + DETALLES_MK),
]

# --- Encargo 36 · commit 1: cuando el portal rechaza un paso, el motivo dice lo que pide, leído de la pantalla
# (CICLO-maersk-retiro-y-terminos.md) ---
PIDE_MK = MK + "test_el_corte_dice_lo_que_pide_el_portal"
PIDE_SC = SC + "test_el_motivo_dice_primero_lo_que_pide_el_portal"
JS_PIDE_MK = MK + "test_js_lo_que_pide"
LINEA_PIDE_MK = MK + "test_lo_que_pide_en_una_linea"

MUTACIONES += [
    dict(id="corte-no-dice-lo-que-pide", pruebas=[PIDE_SC, PIDE_MK],
         viejo='pide = f"el portal pide: {e.pide}. No encontré" if e.pide else "no encontré"',
         nuevo='pide = "no encontré"'),
    dict(id="corte-pierde-lo-que-pide", pruebas=[PIDE_SC, PIDE_MK],
         viejo="self.paso, self.buscaba, self.pide = paso, buscaba, pide",
         nuevo='self.paso, self.buscaba, self.pide = paso, buscaba, ""'),
    dict(id="maersk-revision-no-lee-lo-que-pide", pruebas=[PIDE_MK],
         viejo='"apareció en 15 s", pide=_mk_lo_que_pide(page))', nuevo='"apareció en 15 s")'),
    dict(id="mk-pide-sin-enlaces", pruebas=[JS_PIDE_MK], viejo="            campos.push(...enlaces);\n", nuevo=""),
    dict(id="mk-pide-sin-body", pruebas=[JS_PIDE_MK],
         viejo="const m = mkAtr(e, 'body').replace(/\\s+/g, ' ').trim() || (enlaces.length ? '' : mkTexto(e));",
         nuevo="const m = (enlaces.length ? '' : mkTexto(e));"),
    # Revisión del encargo 36: un enlace a otra página no es un campo, y el visible incluye display:contents y excluye
    # visibility:hidden.
    dict(id="mk-pide-cualquier-enlace", pruebas=[JS_PIDE_MK],
         viejo="|| mkTag(y.el) === 'a' && mkAtr(y.el, 'href').startsWith('#')))", nuevo="|| mkTag(y.el) === 'a'))"),
    dict(id="mk-visible-sin-lo-de-adentro", pruebas=[JS_PIDE_MK],
         viejo="        return hijos.some(h => mkVisible(h, prof + 1));\n", nuevo="        return false;\n"),
    dict(id="mk-visible-sin-checkvisibility", pruebas=[JS_PIDE_MK, "test_clics.TestRetiroMaersk.test_js_calendario_por_su_leyenda"],
         viejo="            return !(e.checkVisibility && !e.checkVisibility({checkOpacity: true, checkVisibilityCSS: true}));\n",
         nuevo="            return true;\n"),
    dict(id="mk-pide-tambien-ocultos", pruebas=[JS_PIDE_MK],
         viejo="mkAtr(e, 'appearance') === 'error' && mkVisible(e)", nuevo="mkAtr(e, 'appearance') === 'error'"),
    dict(id="mk-pide-tambien-avisos", pruebas=[JS_PIDE_MK],
         viejo="mkAtr(e, 'appearance') === 'error' && mkVisible(e)",
         nuevo="mkAtr(e, 'appearance') !== 'success' && mkVisible(e)"),
    dict(id="mk-pide-sin-invalidos", pruebas=[JS_PIDE_MK],
         viejo="} else if (e.hasAttribute && e.hasAttribute('invalid') && mkAtr(e, 'invalid') !== 'false' && mkVisible(e)) {",
         nuevo="} else if (false) {"),
    dict(id="mk-pide-invalid-false", pruebas=[JS_PIDE_MK], viejo=" && mkAtr(e, 'invalid') !== 'false'", nuevo=""),
    dict(id="mk-recorrer-sin-shadow", pruebas=[JS_PIDE_MK],
         viejo="                if (c.shadowRoot) w(c.shadowRoot, anc2);\n", nuevo=""),
    dict(id="mk-pide-sin-mensajes", pruebas=[LINEA_PIDE_MK],
         viejo="        return f\"{', '.join(campos)} ({'; '.join(mensajes)})\"\n", nuevo="        return \", \".join(campos)\n"),
    dict(id="mk-pide-no-es-dict", pruebas=[LINEA_PIDE_MK],
         viejo="    if not isinstance(r, dict):\n        return \"\"\n    campos = [", nuevo="    campos = ["),
    dict(id="mk-pide-sin-try", pruebas=[LINEA_PIDE_MK],
         viejo="        r = page.evaluate(_JS_MK_LO_QUE_PIDE)\n    except Exception:\n        return \"\"\n",
         nuevo="        r = page.evaluate(_JS_MK_LO_QUE_PIDE)\n    finally:\n        pass\n"),
    dict(id="mk-avance-sin-lo-que-pide", pruebas=[MK + "test_booking_information_dice_lo_que_pide"],
         viejo="    pide = _mk_lo_que_pide(page)\n    que = (", nuevo="    pide = \"\"\n    que = ("),
]

# --- Encargo 36 · commit 2: MAERSK elige la fecha de retiro con la regla de Marcelo: el primer día hábil después de hoy,
# o el siguiente habilitado, con «Choose another date», el día por su fecha y «Done» (CICLO-maersk-retiro-y-terminos.md) ---
RT = "test_clics.TestRetiroMaersk."
RT_HABIL = RT + "test_el_primer_dia_habil_despues_de_hoy"
RT_REGLA = RT + "test_elige_el_dia_con_la_regla"
RT_TRES = RT + "test_elige_con_tres_clics"
RT_SIGUIENTE = RT + "test_si_no_esta_habilitado_el_siguiente"
RT_BOTON = RT + "test_sin_un_solo_boton_no_pulsa_nada"
RT_CALENDARIO = RT + "test_calendario_que_no_aparece"
RT_SIN_DIA = RT + "test_sin_el_dia_por_su_fecha_no_pulsa_el_dia"
RT_RELEE = RT + "test_el_dia_ya_no_esta_al_volver_a_leerlo"
RT_DONE = RT + "test_done_despues_del_dia"
RT_QUEDO = RT + "test_comprueba_la_fecha_que_quedo"
RT_CARGOS = RT + "test_anota_los_avisos_de_cargos_y_sigue"
RT_ORDEN = RT + "test_reservar_maersk_la_elige_antes_de_la_referencia"
RT_JS_LEYENDA = RT + "test_js_calendario_por_su_leyenda"
RT_JS_ATRIBUTO = RT + "test_js_calendario_por_su_atributo"
RT_JS_OTROS = RT + "test_js_calendario_otros_meses_y_deshabilitados"
RT_JS_DONE = RT + "test_js_calendario_solo_con_un_done_y_28_dias"
RT_JS_TARJETA = RT + "test_js_tarjeta_y_avisos_de_cargos"
LLAMADA_RT = ("            corte = _mk_fecha_de_retiro(page, reg, det, f)\n            if corte:\n"
              "                return corte\n")

MUTACIONES += [
    # La regla del día.
    dict(id="mk-retiro-incluye-el-sabado", pruebas=[RT_HABIL],
         viejo="    return d.weekday() < 5 and d not in feriados\n",
         nuevo="    return d.weekday() < 6 and d not in feriados\n"),
    dict(id="mk-retiro-el-mismo-dia", pruebas=[RT_HABIL, RT_TRES],
         viejo="    d = hoy + datetime.timedelta(days=1)\n    while not _mk_dia_habil(d, feriados):",
         nuevo="    d = hoy\n    while not _mk_dia_habil(d, feriados):"),
    dict(id="mk-retiro-no-salta-el-deshabilitado", pruebas=[RT_REGLA, RT_SIGUIENTE],
         viejo="        if fechas[d]:\n", nuevo="        if True:\n"),
    dict(id="mk-retiro-cambia-de-mes", pruebas=[RT_REGLA, RT_SIN_DIA],
         viejo="    if not primero <= objetivo <= ultimo:\n", nuevo="    if False:\n"),
    dict(id="mk-retiro-salta-lo-no-identificado", pruebas=[RT_REGLA],
         viejo="        if d not in fechas:\n            return None, f\"no pude identificar por su fecha el",
         nuevo="        if d not in fechas:\n            d += datetime.timedelta(days=1)\n            continue\n"
               "            return None, f\"no pude identificar por su fecha el"),
    dict(id="mk-retiro-fecha-invalida-cuenta", pruebas=[RT_REGLA],
         viejo="        except ValueError:\n            continue\n    if not fechas:\n",
         nuevo="        except ValueError:\n            fechas[objetivo] = True\n    if not fechas:\n"),
    # Los tres clics y lo que corta.
    dict(id="mk-retiro-sin-boton-unico", pruebas=[RT_BOTON],
         viejo="    if boton is None or listos:\n        raise ObjetivoNoEncontrado(\"Fecha de retiro de MAERSK\"",
         nuevo="    if listos:\n        raise ObjetivoNoEncontrado(\"Fecha de retiro de MAERSK\""),
    # Revisión del encargo 36: con un «Done» antes de abrir el calendario, no se sabría cuál es el suyo; y el botón se
    # espera, no se busca una sola vez.
    dict(id="mk-retiro-no-mira-done-antes", pruebas=[RT_BOTON],
         viejo="    if boton is None or listos:\n        raise ObjetivoNoEncontrado(\"Fecha de retiro de MAERSK\"",
         nuevo="    if boton is None:\n        raise ObjetivoNoEncontrado(\"Fecha de retiro de MAERSK\""),
    dict(id="mk-retiro-no-espera-el-boton", pruebas=[RT_BOTON, RT_TRES],
         viejo="        if n:\n            break\n        esperar(page, 0.5)\n    listos = ",
         nuevo="        if n:\n            break\n    listos = "),
    # Con dos «Done» o dos «Search more sailing options», el programa mira cuántos hay antes de usar el botón: ahí tomar
    # el primero no cambia nada, y solo muerde con dos «Choose another date».
    dict(id="mk-boton-unico-el-primero", pruebas=[RT_BOTON],
         viejo="    return (vistos[0] if len(vistos) == 1 else None), len(vistos)\n",
         nuevo="    return (vistos[0] if vistos else None), len(vistos)\n"),
    dict(id="mk-retiro-sin-evidencia", pruebas=[RT_TRES, RT_CALENDARIO, LD + "test_solo_ahi"],
         viejo="    _evidencia_antes_de_la_guarda(page, reg, f\"mk_f{f}_calendario\", \"con el calendario de la fecha de "
               "retiro\",\n                                  completa=False)\n", nuevo=""),
    dict(id="mk-retiro-no-espera-el-calendario", pruebas=[RT_TRES, RT_CALENDARIO],
         viejo="    for _ in range(MK_ESPERA_CALENDARIO * 2):\n        esperar(page, 0.5)\n",
         nuevo="    for _ in range(MK_ESPERA_CALENDARIO * 2):\n"),
    dict(id="mk-retiro-espera-menos", pruebas=[RT_CALENDARIO],
         viejo="MK_ESPERA_CALENDARIO = 10 ", nuevo="MK_ESPERA_CALENDARIO = 5 "),
    dict(id="mk-retiro-sigue-sin-calendario", pruebas=[RT_CALENDARIO],
         viejo="    if not cal.get(\"raiz\"):\n        return _no_enviada(reg, f\"MAERSK: pulsé «{MK_OTRA_FECHA}»",
         nuevo="    if False:\n        return _no_enviada(reg, f\"MAERSK: pulsé «{MK_OTRA_FECHA}»"),
    dict(id="mk-retiro-sigue-sin-dia", pruebas=[RT_SIN_DIA],
         viejo="    if elegido is None:\n        return _no_enviada(reg, f\"MAERSK: abrí el calendario",
         nuevo="    if False:\n        return _no_enviada(reg, f\"MAERSK: abrí el calendario"),
    # Revisión del encargo 36: el calendario es el del único «Done» con sus días (hasta ahí, un «Done» cualquiera), y el
    # motivo dice por qué no lo encontró.
    dict(id="mk-retiro-espera-con-dos-done", pruebas=[RT_CALENDARIO],
         viejo="        if cal.get(\"raiz\") or (cal.get(\"listos\") or 0) > 1:\n", nuevo="        if cal.get(\"raiz\"):\n"),
    dict(id="mk-retiro-resumen-sin-motivo", pruebas=[RT_CALENDARIO],
         viejo="    if not cal.get(\"raiz\"):\n        return f\"no lo encontré: {_mk_sin_calendario(cal)}\"\n", nuevo=""),
    dict(id="mk-retiro-sin-calendario-una-razon", pruebas=[RT_CALENDARIO],
         viejo="    if n > 1:\n        return f\"había {n} «{MK_LISTO}» a la vista, y no sé cuál es el del calendario\"\n",
         nuevo=""),
    dict(id="mk-retiro-no-vuelve-a-leer", pruebas=[RT_RELEE],
         viejo="        if dia is None:\n            return _no_enviada(reg, f\"MAERSK: al volver a leer el calendario",
         nuevo="        if False:\n            return _no_enviada(reg, f\"MAERSK: al volver a leer el calendario"),
    dict(id="mk-retiro-otro-done-sigue", pruebas=[RT_DONE],
         viejo="        if otros:\n            return _no_enviada(", nuevo="        if False:\n            return _no_enviada("),
    dict(id="mk-retiro-done-de-cualquiera", pruebas=[RT_DONE],
         viejo="        listo = page.evaluate_handle(_JS_MK_LISTO).as_element()\n",
         nuevo="        listo = _mk_boton_unico(page, MK_LISTO)[0]\n"),
    dict(id="mk-retiro-sin-done", pruebas=[RT_TRES], viejo="            listo.click(timeout=4000)\n", nuevo="            pass\n"),
    dict(id="mk-retiro-no-lo-anota", pruebas=[RT_TRES, RT_SIGUIENTE],
         viejo="    det.append(f\"retiro={elegido:%d-%m-%Y}\")\n", nuevo=""),
    dict(id="mk-retiro-resumen-sin-rango", pruebas=[RT_TRES],
         viejo="    rango = f\", del {min(con)} al {max(con)}\" if con else \"\"\n", nuevo="    rango = \"\"\n"),
    # La fecha que quedó.
    dict(id="mk-retiro-otra-fecha-sigue", pruebas=[RT_QUEDO],
         viejo="    if otra:\n        otras = sorted(", nuevo="    if False:\n        otras = sorted("),
    dict(id="mk-retiro-sin-fecha-sigue", pruebas=[RT_QUEDO],
         viejo="    if r.get(\"vacia\"):\n        pide = _mk_lo_que_pide(page)\n",
         nuevo="    if False:\n        pide = _mk_lo_que_pide(page)\n"),
    # Revisión del encargo 36: el campo oculto cuenta, la tarjeta puede traer otras fechas además de la elegida, y se
    # espera hasta 5 s a que deje de estar vacía.
    dict(id="mk-retiro-campo-oculto-no-cuenta", pruebas=[RT_QUEDO],
         viejo="    otra = (valor and valor != iso) or (fechas and iso not in fechas)\n",
         nuevo="    otra = (fechas and iso not in fechas)\n"),
    dict(id="mk-retiro-una-sola-fecha-en-la-tarjeta", pruebas=[RT_QUEDO],
         viejo="    otra = (valor and valor != iso) or (fechas and iso not in fechas)\n",
         nuevo="    otra = (valor and valor != iso) or (fechas and fechas != {iso})\n"),
    dict(id="mk-retiro-tarjeta-sin-espera", pruebas=[RT_QUEDO],
         viejo="    for intento in range(10):\n        if intento:\n            esperar(page, 0.5)\n",
         nuevo="    for intento in range(1):\n        if intento:\n            esperar(page, 0.5)\n"),
    dict(id="mk-retiro-sin-lo-que-pide", pruebas=[RT_QUEDO],
         viejo="        pide = _mk_lo_que_pide(page)\n        return _no_enviada(reg, f\"MAERSK: elegí el",
         nuevo="        pide = \"\"\n        return _no_enviada(reg, f\"MAERSK: elegí el"),
    dict(id="mk-retiro-ilegible-como-leida", pruebas=[RT_QUEDO],
         viejo="    if not r.get(\"vacia\") and not otra and (valor == iso or iso in fechas):\n",
         nuevo="    if not r.get(\"vacia\") and not otra:\n"),
    dict(id="mk-retiro-no-dice-sin-tarjeta", pruebas=[RT_QUEDO],
         viejo="        cual = \"\" if r.get(\"tarjeta\") else \" (no la encontré)\"\n", nuevo="        cual = \"\"\n"),
    # Los avisos de cargos.
    dict(id="mk-retiro-no-anota-cargos", pruebas=[RT_CARGOS],
         viejo="            reg.info(f\"aviso de MAERSK sobre la fecha de retiro{ya}: «{t}»\")\n", nuevo="            pass\n"),
    dict(id="mk-retiro-anota-cargos-cada-vez", pruebas=[RT_CARGOS],
         viejo="        if t not in anotados:\n            anotados.add(t)\n", nuevo="        if True:\n            anotados.add(t)\n"),
    dict(id="mk-retiro-no-distingue-los-de-antes", pruebas=[RT_CARGOS],
         viejo="            ya = \" (ya estaba antes de elegirla)\" if t in antes else \"\"\n", nuevo="            ya = \"\"\n"),
    # Dónde se llama.
    dict(id="maersk-no-elige-la-fecha", pruebas=[RT_ORDEN], viejo=LLAMADA_RT, nuevo=""),
    dict(id="maersk-sigue-tras-el-corte-de-la-fecha", pruebas=[RT_ORDEN],
         viejo=LLAMADA_RT, nuevo=LLAMADA_RT.replace("                return corte\n", "                pass\n")),
    # El JavaScript del calendario.
    dict(id="mk-dias-sin-leyenda", pruebas=[RT_JS_LEYENDA, RT_JS_DONE],
         viejo="                if (claves.size === 1) return [...claves][0];\n", nuevo=""),
    dict(id="mk-dias-sin-un-solo-done", pruebas=[RT_JS_DONE],
         viejo="        if (unicos.length !== 1) return {listos: unicos.length, raiz: false, meses: [], dias: []};\n",
         nuevo=""),
    dict(id="mk-dias-done-dos-veces", pruebas=[RT_JS_LEYENDA],
         viejo="        const unicos = listos.filter(x => !x.anc.some(a => deListos.has(a)));\n",
         nuevo="        const unicos = listos;\n"),
    dict(id="mk-dias-sin-minimo", pruebas=[RT_JS_DONE], viejo="(cuenta.get(a) || 0) >= 28)", nuevo="(cuenta.get(a) || 0) >= 1)"),
    dict(id="mk-dias-cuenta-semanas", pruebas=[RT_JS_DONE], viejo="/week(?!end)/i.test(", nuevo="/semana/i.test("),
    # Revisión del encargo 36: «weekend» no es un número de semana.
    dict(id="mk-dias-semana-con-finde", pruebas=[RT_JS_OTROS], viejo="/week(?!end)/i.test(", nuevo="/week/i.test("),
    dict(id="mk-dias-atributo-de-otro-dia", pruebas=[RT_JS_ATRIBUTO],
         viejo="                if (+f.slice(8, 10) === c.dia) fs.add(f);\n", nuevo="                fs.add(f);\n"),
    dict(id="mk-dias-sin-atributo", pruebas=[RT_JS_ATRIBUTO],
         viejo="            let fecha = porAtributo(c), como = fecha ? 'atributo' : '';\n",
         nuevo="            let fecha = '', como = '';\n"),
    dict(id="mk-dias-otro-mes-toma-la-leyenda", pruebas=[RT_JS_OTROS],
         viejo="            if (!fecha && !fuera) {\n", nuevo="            if (!fecha) {\n"),
    dict(id="mk-dias-repetidas-cuentan", pruebas=[RT_JS_OTROS, RT_JS_ATRIBUTO],
         viejo="            for (const d of ds) if (propias.length !== 1 || d !== propias[0]) { d.fecha = ''; d.como = 'repetida'; }\n",
         nuevo=""),
    # Revisión del encargo 36: entre dos celdas con la misma fecha, la de su propio mes; y solo el «Done» del
    # calendario, por su botón de adentro.
    dict(id="mk-dias-repetida-sin-su-mes", pruebas=[RT_JS_ATRIBUTO],
         viejo="            const propias = ds.filter(d => mesDe(d.c) === f.slice(0, 7));\n", nuevo="            const propias = [];\n"),
    dict(id="mk-listo-ninguno", pruebas=[RT_JS_LEYENDA], viejo="    return r.raiz ? r.listo : null;\n", nuevo="    return null;\n"),
    dict(id="mk-listo-el-anfitrion", pruebas=[RT_JS_LEYENDA],
         viejo="        const listo = botones.find(b => !botones.some(o => o.el !== b.el && o.anc.includes(b.el))) || done;\n",
         nuevo="        const listo = done;\n"),
    dict(id="mk-dias-sin-clases-apagadas", pruebas=[RT_JS_OTROS, RT_JS_LEYENDA],
         viejo="const APAGADO = /disab|inact|unavailable|out-?of-?range|not-?allowed|blocked/i;",
         nuevo="const APAGADO = /nada-apagado/i;"),
    dict(id="mk-dias-sin-disabled", pruebas=[RT_JS_OTROS],
         viejo="!c.miembros.some(m => m.el.hasAttribute('disabled')", nuevo="!c.miembros.some(m => false"),
    dict(id="mk-dias-sin-aria-disabled", pruebas=[RT_JS_OTROS],
         viejo="\n                                                                         || mkAtr(m.el, 'aria-disabled') === 'true');",
         nuevo=");"),
    dict(id="mk-dia-pulsa-deshabilitado", pruebas=[RT_JS_LEYENDA],
         viejo="d.fecha === a.fecha && d.habilitado)", nuevo="d.fecha === a.fecha)"),
    dict(id="mk-dia-pulsa-la-celda", pruebas=[RT_JS_LEYENDA],
         viejo="        return b ? b.el : c.x.el;\n", nuevo="        return c.x.el;\n"),
    dict(id="mk-fechas-sin-iso", pruebas=[RT_JS_ATRIBUTO],
         viejo="        for (const x of t.matchAll(ISO)) out.push(mkIso(+x[1], +x[2] - 1, +x[3]));\n", nuevo=""),
    dict(id="mk-fechas-sin-dia-mes", pruebas=[RT_JS_ATRIBUTO, RT_JS_TARJETA],
         viejo="        for (const x of t.matchAll(DIA_MES)) if (mkMes(x[2]) >= 0) out.push(mkIso(+x[3], mkMes(x[2]), +x[1]));\n",
         nuevo=""),
    dict(id="mk-fechas-sin-mes-dia", pruebas=[RT_JS_ATRIBUTO],
         viejo="        for (const x of t.matchAll(MES_DIA)) if (mkMes(x[1]) >= 0) out.push(mkIso(+x[3], mkMes(x[1]), +x[2]));\n",
         nuevo=""),
    dict(id="mk-iso-acepta-dias-que-no-existen", pruebas=[RT_JS_LEYENDA],
         viejo="        return f.getUTCFullYear() === a && f.getUTCMonth() === m && f.getUTCDate() === d\n",
         nuevo="        return true\n"),
    # La tarjeta y los avisos.
    dict(id="mk-tarjeta-sin-dia-aparte", pruebas=[RT_JS_TARJETA],
         viejo="        const f = meses.length === 1 && sueltos.length === 1\n", nuevo="        const f = false\n"),
    dict(id="mk-tarjeta-sin-campo-oculto", pruebas=[RT_JS_TARJETA],
         viejo="    const valor = campos.length === 1 ? String(campos[0].el.value || '') : '';\n",
         nuevo="    const valor = '';\n"),
    dict(id="mk-tarjeta-nunca-vacia", pruebas=[RT_JS_TARJETA],
         viejo="    const vacia = dentro.some(x => mkAtr(x.el, 'data-test') === 'haulage-invalid-date' && mkVisible(x.el));\n",
         nuevo="    const vacia = false;\n"),
    dict(id="mk-avisos-sin-rol", pruebas=[RT_JS_TARJETA],
         viejo="        const aviso = mkTag(e) === 'mc-notification' || ['alert', 'status'].includes(mkAtr(e, 'role'));\n",
         nuevo="        const aviso = mkTag(e) === 'mc-notification';\n"),
    dict(id="mk-avisos-tambien-ocultos", pruebas=[RT_JS_TARJETA],
         viejo="        if (!aviso || !mkVisible(e)) continue;\n", nuevo="        if (!aviso) continue;\n"),
    dict(id="mk-avisos-sin-filtro", pruebas=[RT_JS_TARJETA],
         viejo="        if (CARGOS.test(t)) out.push(t.slice(0, 300));\n", nuevo="        out.push(t.slice(0, 300));\n"),
    dict(id="mk-avisos-sin-heading", pruebas=[RT_JS_TARJETA],
         viejo="[mkAtr(e, 'heading'), mkAtr(e, 'body'), mkTexto(e)]", nuevo="[mkAtr(e, 'body'), mkTexto(e)]"),
    # Revisión del encargo 36: «discharge» no es un cargo.
    dict(id="mk-avisos-charge-como-parte", pruebas=[RT_JS_TARJETA], viejo="/\\bcharges?\\b|", nuevo="/charge|"),
]

# --- Encargo 36 · commit 3: la casilla de los términos de MAERSK por su texto, no «el último checkbox»
# (CICLO-maersk-retiro-y-terminos.md) ---
TT = "test_clics.TestTerminosMaersk."
TT_MARCA = TT + "test_marca_la_casilla_por_su_texto"
TT_YA = TT + "test_ya_marcada_no_la_pulsa"
TT_UNA = TT + "test_sin_una_sola_corta_sin_pulsar"
TT_DESPUES = TT + "test_comprueba_despues_del_clic"
TT_SIN_SABER = TT + "test_sin_saber_si_estaba_marcada_no_la_pulsa"
TT_JS = TT + "test_js_casilla_por_su_texto"
TERMINOS_MK = "        corte = _mk_marcar_terminos(page, reg, f)\n        if corte:\n            return corte\n"

MUTACIONES += [
    dict(id="mk-terminos-otro-texto", pruebas=[TT + "test_el_texto_es_el_de_la_captura"],
         viejo='MK_TERMINOS = "I have read and accept all the terms and conditions of this booking"',
         nuevo='MK_TERMINOS = "I accept the terms and conditions"'),
    # El JavaScript que busca la casilla.
    dict(id="mk-casillas-sin-label", pruebas=[TT_JS],
         viejo="c.textos.push(mkAtr(e, 'label'), mkAtr(e, 'aria-label'), mkTexto(e));",
         nuevo="c.textos.push(mkAtr(e, 'aria-label'), mkTexto(e));"),
    dict(id="mk-casillas-sin-etiqueta", pruebas=[TT_JS],
         viejo="            if (etiqueta) c.textos.push(mkTexto(etiqueta));\n", nuevo=""),
    dict(id="mk-casillas-como-parte", pruebas=[TT_JS],
         viejo="c.textos.some(t => norma(t) === b)", nuevo="c.textos.some(t => norma(t) !== '' && b.startsWith(norma(t)))"),
    dict(id="mk-casillas-sin-punto-final", pruebas=[TT_JS],
         viejo=".trim().replace(/[\\s.*:]+$/, '').toLowerCase();", nuevo=".trim().toLowerCase();"),
    dict(id="mk-casillas-tambien-ocultas", pruebas=[TT_JS],
         viejo=".filter(c => mkVisible(c.el) && c.textos.some(", nuevo=".filter(c => c.textos.some("),
    dict(id="mk-casillas-cada-una-aparte", pruebas=[TT_JS],
         viejo="const ctl = mkTag(e) === 'mc-checkbox' ? e : (anfitrion || e);", nuevo="const ctl = e;"),
    dict(id="mk-casillas-sin-aria-checked", pruebas=[TT_JS],
         viejo="            if (mkAtr(e, 'aria-checked')) c.estados.push(mkAtr(e, 'aria-checked') === 'true');\n            else if",
         nuevo="            if"),
    dict(id="mk-casillas-marcada-solo-del-input", pruebas=[TT_JS],
         viejo="            else if (typeof e.checked === 'boolean') c.estados.push(e.checked);\n",
         nuevo="            else if (mkTag(e) === 'input') c.estados.push(e.checked);\n"),
    # Revisión del encargo 36: se pulsa el input de la casilla, no el centro del mc-checkbox; solo una sola, y sin
    # marcar; y si su estado no coincide en todos lados, no se sabe si está marcada.
    dict(id="mk-casillas-estados-distintos", pruebas=[TT_JS],
         viejo="c.estados.some(Boolean) ? null : false", nuevo="c.estados.some(Boolean) ? true : false"),
    dict(id="mk-terminos-pulsa-el-control", pruebas=[TT_JS],
         viejo="            if (mkTag(e) === 'input') c.objetivo = e;\n", nuevo=""),
    dict(id="mk-terminos-pulsa-con-dos", pruebas=[TT_JS],
         viejo="    if (cs.length !== 1) return false;\n    const [c] = cs;\n",
         nuevo="    if (!cs.length) return false;\n    const [c] = cs;\n"),
    dict(id="mk-terminos-pulsa-la-marcada", pruebas=[TT_JS], viejo="    if (c.marcada !== false) return false;\n", nuevo=""),
    dict(id="mk-terminos-sin-marcada", pruebas=[TT_JS],
         viejo="    return {n: cs.length, marcada: cs.length === 1 ? cs[0].marcada : null};",
         nuevo="    return {n: cs.length, marcada: null};"),
    # El paso.
    dict(id="mk-terminos-sin-bajar", pruebas=[TT_MARCA],
         viejo="        page.evaluate(\"window.scrollTo(0, document.body.scrollHeight)\")\n    except Exception:\n        pass\n"
               "    r = {}\n",
         nuevo="        pass\n    except Exception:\n        pass\n    r = {}\n"),
    dict(id="mk-terminos-sin-espera", pruebas=[TT_UNA, TT_MARCA],
         viejo="    for _ in range(MK_ESPERA_TERMINOS * 2):\n        esperar(page, 0.5)\n",
         nuevo="    for _ in range(MK_ESPERA_TERMINOS * 2):\n"),
    dict(id="mk-terminos-espera-menos", pruebas=[TT_UNA], viejo="MK_ESPERA_TERMINOS = 10 ", nuevo="MK_ESPERA_TERMINOS = 5 "),
    dict(id="mk-terminos-acepta-dos", pruebas=[TT_UNA],
         viejo="    if r.get(\"n\") != 1:\n        raise ObjetivoNoEncontrado(\"Términos de MAERSK\"",
         nuevo="    if not r.get(\"n\"):\n        raise ObjetivoNoEncontrado(\"Términos de MAERSK\""),
    dict(id="mk-terminos-desmarca-la-marcada", pruebas=[TT_YA],
         viejo="    if r.get(\"marcada\") is True:\n        reg.info(\"la casilla de los términos ya estaba marcada",
         nuevo="    if False:\n        reg.info(\"la casilla de los términos ya estaba marcada"),
    dict(id="mk-terminos-sigue-sin-pulsar", pruebas=[TT_DESPUES],
         viejo="    if not pulso:\n        return _no_enviada(", nuevo="    if False:\n        return _no_enviada("),
    dict(id="mk-terminos-no-comprueba", pruebas=[TT_DESPUES],
         viejo="    if r.get(\"n\") != 1 or r.get(\"marcada\") is not True:\n", nuevo="    if False:\n"),
    dict(id="mk-terminos-solo-dice-no-quedo", pruebas=[TT_DESPUES],
         viejo="        que = \"no quedó marcada\" if sin_marca else \"no pude comprobar que quedó marcada\"\n",
         nuevo="        que = \"no quedó marcada\"\n"),
    dict(id="mk-terminos-no-mira-la-direccion", pruebas=[TT_DESPUES], viejo="    if page.url != url:\n", nuevo="    if False:\n"),
    dict(id="mk-terminos-pulsa-sin-saber", pruebas=[TT_SIN_SABER],
         viejo="    if r.get(\"marcada\") is not False:\n        return _no_enviada(reg, f\"MAERSK: no pude leer si la casilla",
         nuevo="    if False:\n        return _no_enviada(reg, f\"MAERSK: no pude leer si la casilla"),
    dict(id="mk-terminos-sin-evidencia", pruebas=[TT_MARCA, TT_YA, LD + "test_solo_ahi"],
         viejo="    _evidencia_antes_de_la_guarda(page, reg, f\"mk_f{f}_terminos\", \"con la casilla de los términos\", "
               "completa=False)\n", nuevo=""),
    # Dónde se llama, y la forma de antes.
    dict(id="maersk-terminos-sin-cortar", pruebas=[MK + "test_espera_la_revision_antes_de_los_terminos"],
         viejo=TERMINOS_MK, nuevo="        _mk_marcar_terminos(page, reg, f)\n"),
    dict(id="maersk-vuelve-el-ultimo-checkbox", pruebas=[FG, MK + "test_espera_la_revision_antes_de_los_terminos"],
         viejo=TERMINOS_MK, nuevo='        page.locator("mc-checkbox").last.click(force=True)\n' + TERMINOS_MK),
]

# --- CMA: el abridor del panel Reefer es el botón «Modifique el reefer» (CICLO-revision-corrida-completa.md) ---
MUTACIONES += [
    dict(id="cma-reefer-vuelve-la-insignia", pruebas=[C1 + "test_reefer_corta_en_cada_paso_sin_pulsar_a_ciegas"],
         viejo=ABRE_REEFER_CMA,
         nuevo=ABRE_REEFER_CMA.replace("        for selector in (\n", "        for selector in (\n            \"text=/TO COMPLETE/i\",\n")),
    dict(id="cma-reefer-vuelve-el-boton-generico", pruebas=[C1 + "test_reefer_corta_en_cada_paso_sin_pulsar_a_ciegas"],
         viejo=ABRE_REEFER_CMA,
         nuevo=ABRE_REEFER_CMA.replace("        for selector in (\n",
                                       "        for selector in (\n            \"button:has-text('Reefer')\",\n")),
]

# --- COSCO: la ventana «Reminder»: su Submit, una sola vez; después solo se espera (CICLO-revision-corrida-completa.md) ---
SUBS_REM = "    const subs = [...ventana.querySelectorAll('button, a, span')]\n"
UNO_REM = "    if (subs.length > 1) return 'ambiguo';\n    subs[0].click();\n"
TITULO_REM = r"    const esVentana = e => /\bReminder\b/.test(e.textContent || '')" + "\n"
VIS_REM = "    const vis = e => !!e && e.getClientRects().length > 0;\n"
AVISO_REM = ('                    reg.info(f"Ventana \'Reminder\': no identifiqué su Submit sin ambigüedad ({motivo}); '
             'no pulsé nada.")\n')
PULSO_REM = ('                    reg.info("Ventana \'Reminder\': pulsé una vez su Submit, el de la ventana (por su título y '
             'su texto).")\n')
JS_REM = CO_ + "test_js_submit_del_reminder_solo_el_de_la_ventana"

MUTACIONES += [
    dict(id="cosco-reminder-el-ultimo-submit", pruebas=[JS_REM],
         cambios=[(SUBS_REM, SUBS_REM.replace("ventana.querySelectorAll", "document.querySelectorAll")),
                  (UNO_REM, "    subs[subs.length - 1].click();\n")]),
    dict(id="cosco-reminder-pulsa-lo-ambiguo", pruebas=[JS_REM],
         viejo="    if (subs.length > 1) return 'ambiguo';\n", nuevo=""),
    dict(id="cosco-reminder-sin-titulo", pruebas=[JS_REM],
         viejo=TITULO_REM, nuevo="    const esVentana = e => true\n"),
    dict(id="cosco-reminder-ve-ventanas-cerradas", pruebas=[JS_REM],
         viejo=VIS_REM, nuevo="    const vis = e => !!e;\n"),
    dict(id="cosco-reminder-vuelve-a-pulsar",
         pruebas=[CO_ + "test_reminder_pulsa_su_submit_una_sola_vez", CO_ + "test_reminder_tardio_tambien_una_sola_vez"],
         viejo="            if not rem_pulsado:\n", nuevo="            if True:\n"),
    dict(id="cosco-reminder-no-dice-que-pulso", pruebas=[CO_ + "test_reminder_pulsa_su_submit_una_sola_vez"],
         viejo=PULSO_REM, nuevo="                    pass\n"),
    dict(id="cosco-reminder-calla-que-no-pulso", pruebas=[CO_ + "test_reminder_ambiguo_no_pulsa"],
         viejo=AVISO_REM, nuevo="                    pass\n"),
    dict(id="cosco-reminder-avisa-cada-vuelta", pruebas=[CO_ + "test_reminder_ambiguo_no_pulsa"],
         viejo="                    rem_avisado = True\n", nuevo=""),
    dict(id="cosco-espera-calla-el-plazo", pruebas=[CO_ + "test_espera_se_agota"],
         viejo='        reg.info(f"Se cumplió el plazo de {COSCO_ESPERA_CONFIRMACION_SEG} s sin confirmación de COSCO.")\n',
         nuevo="        pass\n"),
]

# --- Ítem 1: MAERSK sin nave se detiene en «Select sailing» y lo dice (CICLO-cola-nueve-items.md) ---
MUTACIONES += [
    dict(id="maersk-sin-nave-sigue-a-la-guarda", pruebas=[MK + "test_sin_nave_no_llega_a_la_guarda"],
         viejo="    if not modo:\n        return _mk_sin_nave(page, reg, reserva, det, sin_nave)\n", nuevo=""),
    dict(id="maersk-sin-nave-dice-review", pruebas=[MK + "test_sin_nave_se_detiene_en_select_sailing"],
         viejo='    return ("REVISAR", f"MAERSK: me detuve en «Select sailing»: la nave',
         nuevo='    return ("REVISAR", f"MAERSK: armada hasta Review: la nave'),
    # Desde el encargo 25 la evidencia está en _mk_detenida (CICLO-proxima-salida.md): se quita su llamada.
    dict(id="maersk-sin-nave-sin-evidencia", pruebas=[MK + "test_sin_nave_se_detiene_en_select_sailing"],
         viejo='    _mk_detenida(page, reg, reserva["fila"])\n    reg.paso("Me detuve en «Select sailing»',
         nuevo='    reg.paso("Me detuve en «Select sailing»'),
    dict(id="maersk-sin-nave-calla-donde", pruebas=[MK + "test_sin_nave_se_detiene_en_select_sailing"],
         viejo='    reg.paso("Me detuve en «Select sailing»: la nave de la fila no está en los itinerarios de MAERSK.")\n',
         nuevo=""),
]

# --- Ítem 2: CMA no da la ruta por validada si el portal no respondió (CICLO-cola-nueve-items.md) ---
MUTACIONES += [
    dict(id="cma-ruta-vencida-dice-exito", pruebas=[C1 + "test_ruta_sin_respuesta_no_se_da_por_validada"],
         viejo='    if resultado in ("itinerarios", "aviso"):\n', nuevo="    if True:\n"),
    dict(id="cma-ruta-error-dice-exito", pruebas=[C1 + "test_ruta_sin_respuesta_no_se_da_por_validada"],
         viejo='    if resultado in ("itinerarios", "aviso"):\n', nuevo='    if resultado in ("itinerarios", "aviso", "error"):\n'),
    dict(id="cma-validar-no-devuelve-lo-visto", pruebas=[C1 + "test_validar_devuelve_lo_que_vio_el_portal"],
         viejo="            return _cma_esperar_resultado(page, 12, reg)\n",
         nuevo="            _cma_esperar_resultado(page, 12, reg)\n            return \"ok\"\n"),
    dict(id="cma-ruta-sin-anuncio", pruebas=[C1 + "test_validar_devuelve_lo_que_vio_el_portal"],
         viejo="        _cma_anunciar_ruta(reg, estado)\n",
         nuevo='        reg.paso("Ruta validada con éxito. Continuando con datos de carga e itinerario...")\n'),
]

# --- Ítem 5: COSCO elige el itinerario por el día de carga de la fila, nunca el primero (CICLO-cola-nueve-items.md) ---
# Desde el encargo 25, por la próxima salida (CICLO-proxima-salida.md): se borraron las 3 que miraban la comparación con
# el día de carga y la del motivo «ninguno tiene ETD», y 2 se pusieron al día.
ELIGE_COSCO = K1 + "test_itinerario_la_proxima_salida_nunca_el_primero"
AMBIGUO_COSCO = K1 + "test_itinerario_ambiguo_queda_no_enviada_con_evidencia"
NO_EL_PRIMERO_COSCO = K1 + "test_reservar_cosco_no_toma_el_primero"

MUTACIONES += [
    dict(id="cosco-itinerario-el-primero", pruebas=[NO_EL_PRIMERO_COSCO],
         viejo='    elegido, motivo = _cosco_elegir_itinerario(cand, reserva) if cand else (None, "")\n',
         nuevo='    elegido, motivo = (cand[0], "") if cand else (None, "")\n'),
    dict(id="cosco-itinerario-sigue-si-ambiguo", pruebas=[NO_EL_PRIMERO_COSCO],
         viejo="    if cand and elegido is None:\n        return _cosco_itinerario_ambiguo(page, reg, reserva, cand, motivo)\n",
         nuevo="    if cand and elegido is None:\n        elegido = cand[0]\n"),
    dict(id="cosco-itinerario-sin-evidencia", pruebas=[AMBIGUO_COSCO, LD + "test_solo_ahi"],
         viejo="    _evidencia_antes_de_la_guarda(page, reg, f\"cosco_f{reserva['fila']}_itinerarios\"",
         nuevo="    (lambda *a, **k: None)(page, reg, f\"cosco_f{reserva['fila']}_itinerarios\""),
    dict(id="cosco-itinerario-sin-lista", pruebas=[AMBIGUO_COSCO],
         viejo='    reg.info("itinerarios que calzan: " + " | ".join(_cosco_resumen(x)',
         nuevo='    str("itinerarios que calzan: " + " | ".join(_cosco_resumen(x)'),
]

# --- Ítem 6: ONE deja la captura y el HTML de la pantalla donde se detuvo (CICLO-cola-nueve-items.md) ---
O1 = "test_clics.TestOne."
DETENIDA_ONE = O1 + "test_detenida_deja_captura_y_html_sin_esperar"
CADA_REVISAR_ONE = O1 + "test_cada_revisar_deja_la_evidencia_donde_se_detuvo"

MUTACIONES += [
    dict(id="one-detenida-sin-nave-sin-evidencia", pruebas=[CADA_REVISAR_ONE],
         viejo="    if not seleccionada:\n        _one_detenida(page, reg, f)\n", nuevo="    if not seleccionada:\n"),
    dict(id="one-detenida-otro-paso-sin-evidencia", pruebas=[CADA_REVISAR_ONE],
         viejo="    else:\n        _one_detenida(page, reg, f)\n", nuevo="    else:\n"),
    dict(id="one-detenida-otro-nombre", pruebas=[DETENIDA_ONE],
         viejo='f"one_f{fila}_detenida", "donde se detuvo", completa=False)', nuevo='f"one_f{fila}_guarda", "donde se detuvo", completa=False)'),
    dict(id="one-detenida-pagina-entera", pruebas=[DETENIDA_ONE],
         viejo='f"one_f{fila}_detenida", "donde se detuvo", completa=False)', nuevo='f"one_f{fila}_detenida", "donde se detuvo", completa=True)'),
    dict(id="one-detenida-no-guarda-nada", pruebas=[DETENIDA_ONE, LD + "test_solo_ahi"],
         viejo='    _evidencia_antes_de_la_guarda(page, reg, f"one_f{fila}_detenida"',
         nuevo='    (lambda *a, **k: None)(page, reg, f"one_f{fila}_detenida"'),
]

# --- Ítem 7: ni teclado ni textarea a ciegas antes de la guarda (CICLO-cola-nueve-items.md) ---
MUTACIONES += [
    dict(id='teclado-one-autocompletar', pruebas=[O1 + "test_autocompletar_sin_sugerencia_no_elige_con_el_teclado", FG],
         viejo='            raise ObjetivoNoEncontrado(f"{etiqueta} de ONE", f"la sugerencia «{tok}» en la lista del autocompletado")\n',
         nuevo='            inp.press("ArrowDown"); esperar(page, 0.4); inp.press("Enter")\n'),
    dict(id='teclado-msc-puerto', pruebas=[M1 + "test_sin_sugerencias_no_elige_con_el_teclado", FG],
         viejo='            raise ObjetivoNoEncontrado(f"{etiqueta} de MSC", f"la sugerencia que dice «{ciudad}» entre las que ofrece "\n                                                             f"el portal")\n',
         nuevo='            inp.press("ArrowDown"); esperar(page, 0.4); inp.press("Enter")\n'),
    dict(id='teclado-msc-hs', pruebas=[M1 + "test_hs_sin_salmon_corta", FG],
         viejo='            raise ObjetivoNoEncontrado("HS Code de MSC", f"la sugerencia del salmón para \'{hscode}\': el portal no "\n                                                         f"ofreció ninguna")\n',
         nuevo='            inp.press("ArrowDown"); esperar(page, 0.4); inp.press("Enter")\n'),
    dict(id='teclado-msc-kendo', pruebas=[M1 + "test_sin_sugerencias_no_elige_con_el_teclado", FG],
         viejo='            raise ObjetivoNoEncontrado(f"{etiqueta} de MSC", f"la sugerencia que dice «{texto}»: el portal no ofreció "\n                                                             f"ninguna")\n',
         nuevo='            inp.press("ArrowDown"); esperar(page, 0.4); inp.press("Enter")\n'),
    dict(id='teclado-cma-puerto', pruebas=[C1 + "test_puerto_sin_codigo_no_elige_con_el_teclado", FG],
         viejo='        raise ObjetivoNoEncontrado(f"{etiqueta} de CMA", f"la sugerencia del puerto «{ciudad}» (por su texto) que deja "\n                                                         f"el código del puerto en el campo")\n',
         nuevo='        page.keyboard.press("ArrowDown"); esperar(page, 0.4); page.keyboard.press("Enter")\n'),
    dict(id='teclado-cma-tamano', pruebas=[C1 + "test_tamano_y_mercancia_no_eligen_con_el_teclado", FG],
         viejo='            raise ObjetivoNoEncontrado("Tamaño y tipo de CMA", "la opción «40\' Reefer High Cube» en el desplegable "\n                                                               "(por su texto)")\n',
         nuevo='            page.keyboard.press("ArrowDown"); esperar(page, 0.4); page.keyboard.press("Enter")\n'),
    dict(id='teclado-cma-mercancia', pruebas=[C1 + "test_tamano_y_mercancia_no_eligen_con_el_teclado", FG],
         viejo='            raise ObjetivoNoEncontrado("Mercancía de CMA", "la sugerencia que dice «030313» en la lista (por su "\n                                                           "texto)")\n',
         nuevo='            page.keyboard.press("ArrowDown"); esperar(page, 0.4); page.keyboard.press("Enter")\n'),
    dict(id='teclado-cosco-autocompletar', pruebas=[K1 + "test_autocompletar_no_elige_con_el_teclado", FG],
         viejo='                raise ObjetivoNoEncontrado(f"{etiqueta} de COSCO", f"la sugerencia «{txt_op}» elegida en el campo (el "\n                                                                   f"clic y los eventos de puntero no la dejaron; con el "\n                                                                   f"teclado sería a ciegas)")\n',
         nuevo='                page.keyboard.press("ArrowDown"); esperar(page, 0.4); page.keyboard.press("Enter")\n'),
    dict(id='textarea-cma-el-primero', pruebas=[C1 + "test_js_comentarios_solo_en_su_campo", FG],
         viejo='/comentario|remark/i.test(p);\n            });\n',
         nuevo='/comentario|remark/i.test(p);\n            }) || allTa[0];\n'),
    dict(id='textarea-cma-locator-cualquiera', pruebas=[FG],
         viejo='.el-form-item:has-text(\'Comentarios\') textarea").first',
         nuevo='.el-form-item:has-text(\'Comentarios\') textarea, textarea").first'),
    dict(id='textarea-cma-no-corta', pruebas=[C1 + "test_comentarios_sin_su_campo_corta"],
         viejo='        raise ObjetivoNoEncontrado("Comentarios de CMA", "el campo de comentarios (por su placeholder «facilítenos», "\n                                                         "«comentario», «comment» o «remark», o su etiqueta «Comentarios» "\n                                                         "o «remark»)")\n',
         nuevo='        return False\n'),
    dict(id='cosco-sin-decorador', pruebas=[SC + "test_cada_reservador_que_corta_esta_decorado"],
         viejo='@_sin_clic_a_ciegas("cosco")\n',
         nuevo=''),
]

# --- Ítem 8: el peso y la temperatura viven en config.json → opciones (CICLO-cola-nueve-items.md) ---
MUTACIONES += [
    dict(id='reefer-peso-no-lee-config', pruebas=[AY + "TestReefer.test_peso_y_temperatura_salen_de_config"],
         viejo='    return _opcion_reefer("peso_reefer_kg", PESO_REEFER)\n',
         nuevo='    return PESO_REEFER\n'),
    dict(id='reefer-temp-no-lee-config', pruebas=[AY + "TestReefer.test_peso_y_temperatura_salen_de_config"],
         viejo='    return _opcion_reefer("temperatura_reefer_c", TEMP_REEFER)\n',
         nuevo='    return TEMP_REEFER\n'),
    dict(id='reefer-otra-llave', pruebas=[AY + "TestReefer.test_peso_y_temperatura_salen_de_config", AY + "TestReefer.test_si_falta_o_no_es_numero_usa_el_de_siempre_y_avisa_una_vez"],
         viejo='_opcion_reefer("peso_reefer_kg", PESO_REEFER)',
         nuevo='_opcion_reefer("peso_kg", PESO_REEFER)'),
    dict(id='reefer-bool-es-numero', pruebas=[AY + "TestReefer.test_numeros_de_config"],
         viejo='    if isinstance(valor, bool):\n        return None\n',
         nuevo=''),
    dict(id='reefer-texto-no-es-numero', pruebas=[AY + "TestReefer.test_numeros_de_config"],
         viejo='        try:\n            valor = float(valor.strip().replace(",", "."))\n        except ValueError:\n            return None\n',
         nuevo='        return None\n'),
    dict(id='reefer-sin-coma-decimal', pruebas=[AY + "TestReefer.test_numeros_de_config"],
         viejo='float(valor.strip().replace(",", "."))',
         nuevo='float(valor.strip())'),
    dict(id='reefer-nan-es-numero', pruebas=[AY + "TestReefer.test_numeros_de_config"],
         viejo='valor != valor or ',
         nuevo=''),
    dict(id='reefer-infinito-es-numero', pruebas=[AY + "TestReefer.test_numeros_de_config"],
         viejo=' or valor in (float("inf"), float("-inf"))',
         nuevo=''),
    dict(id='reefer-entero-con-decimales', pruebas=[AY + "TestReefer.test_numeros_de_config"],
         viejo='    return str(int(valor)) if float(valor).is_integer() else str(valor)\n',
         nuevo='    return str(valor)\n'),
    dict(id='reefer-no-avisa', pruebas=[AY + "TestReefer.test_si_falta_o_no_es_numero_usa_el_de_siempre_y_avisa_una_vez", AY + "TestReefer.test_sin_corrida_avisa_una_vez_por_la_consola_y_el_panel"],
         viejo='        _avisar_opcion_reefer(llave, valor, por_defecto)\n',
         nuevo=''),
    dict(id='reefer-avisa-cada-vez', pruebas=[AY + "TestReefer.test_si_falta_o_no_es_numero_usa_el_de_siempre_y_avisa_una_vez"],
         viejo='            if una_vez is not None and una_vez in avisados:\n                continue\n',
         nuevo=''),
    dict(id='reefer-sin-corrida-avisa-cada-vez', pruebas=[AY + "TestReefer.test_sin_corrida_avisa_una_vez_por_la_consola_y_el_panel"],
         viejo='    if una_vez is not None and una_vez in _AVISOS_SIN_CORRIDA:\n        return\n',
         nuevo=''),
    dict(id='reefer-aviso-sin-una-vez', pruebas=[AY + "TestReefer.test_si_falta_o_no_es_numero_usa_el_de_siempre_y_avisa_una_vez", AY + "TestReefer.test_sin_corrida_avisa_una_vez_por_la_consola_y_el_panel"],
         viejo='como número.", una_vez=llave)',
         nuevo='como número.")'),
    dict(id='reefer-one-escrito-aparte', pruebas=[AY + "TestReefer.test_una_sola_fuente"],
         viejo='    peso = _peso_reefer()\n    grados = _temp_reserva(reserva)\n',
         nuevo='    peso = "22500"\n    grados = _temp_reserva(reserva)\n'),
    dict(id='reefer-msc-escrito-aparte', pruebas=[AY + "TestReefer.test_una_sola_fuente"],
         viejo='_msc_fill_id(page, "WeightPerUnit", _peso_reefer(), reg',
         nuevo='_msc_fill_id(page, "WeightPerUnit", "22500", reg'),
    dict(id='reefer-msc-respaldo-fijo', pruebas=[AY + "TestReefer.test_una_sola_fuente"],
         viejo='        t_val = t_val[:-2]\n    _msc_fill_id(page, "Temperature"',
         nuevo='        t_val = t_val[:-2]\n    if not t_val:\n        t_val = "-20"\n    _msc_fill_id(page, "Temperature"'),
    dict(id='reefer-cosco-constante', pruebas=[AY + "TestReefer.test_una_sola_fuente"],
         viejo='    peso_kg = _peso_reefer()\n    ok_gw = ',
         nuevo='    peso_kg = PESO_REEFER\n    ok_gw = '),
    dict(id='reefer-hyundai-constante', pruebas=[AY + "TestReefer.test_una_sola_fuente"],
         viejo='            peso_kg = _peso_reefer()\n            gw.fill(peso_kg)\n',
         nuevo='            peso_kg = PESO_REEFER\n            gw.fill(peso_kg)\n'),
    dict(id='reefer-maersk-constante', pruebas=[AY + "TestReefer.test_una_sola_fuente"],
         viejo='(_peso_reefer() if es_reefer else "20000")',
         nuevo='(PESO_REEFER if es_reefer else "20000")'),
    dict(id='reefer-cma-constante', pruebas=[AY + "TestReefer.test_una_sola_fuente"],
         viejo='        peso_ok = False\n        peso_kg = _peso_reefer()\n',
         nuevo='        peso_ok = False\n        peso_kg = PESO_REEFER\n'),
    dict(id='reefer-plantilla-sin-peso', archivo='config.example.json', pruebas=[AY + "TestReefer.test_la_plantilla_trae_las_llaves"],
         viejo='    "peso_reefer_kg": 22500,\n', nuevo=''),
]

# --- Ítem 9: limpieza (CICLO-cola-nueve-items.md) ---
MUTACIONES += [
    dict(id='limpieza-vuelve-el-lector-viejo', pruebas=["test_booking.TestLectorViejo.test_ya_no_existe"],
         viejo='# Forma del número en la pantalla de confirmación',
         nuevo='def extraer_numero_booking(page, naviera=""):\n    return ""\n\n\n# Forma del número en la pantalla de confirmación'),
    dict(id='limpieza-leeme-vuelve-el-exe', archivo='LEEME.md', pruebas=["test_consola.TestLeeme.test_nombra_solo_archivos_del_programa_que_existen"],
         viejo='| `AQUASHIELD.py` | El programa. |\n',
         nuevo='| `AQUASHIELD.exe` | El programa. |\n'),
]

# --- HYUNDAI deja la pantalla del Remark justo antes de escribirlo (CICLO-evidencia-remark-hyundai.md) ---
RM = "test_evidencia.TestEvidenciaRemarkHyundai."
JUSTO_ANTES_REMARK = RM + "test_va_justo_antes_del_remark_como_sentencia_suelta"
VENTANA_REMARK = RM + "test_la_ventana_y_el_html_y_despues_el_remark"
FALLA_REMARK = RM + "test_si_la_evidencia_falla_el_remark_se_escribe_igual"
EVIDENCIA_REMARK = ('    _evidencia_antes_de_la_guarda(page, reg, f"hmm_f{f}_remark", "antes de escribir el Remark", '
                    'completa=False)\n')

MUTACIONES += [
    dict(id="hmm-remark-sin-evidencia", pruebas=[JUSTO_ANTES_REMARK, VENTANA_REMARK, FALLA_REMARK, LD + "test_solo_ahi"],
         viejo=EVIDENCIA_REMARK, nuevo=""),
    dict(id="hmm-remark-pagina-completa", pruebas=[JUSTO_ANTES_REMARK, VENTANA_REMARK],
         viejo=EVIDENCIA_REMARK, nuevo=EVIDENCIA_REMARK.replace("completa=False", "completa=True")),
    # Sin el mecanismo existente, una falla al guardar corta la reserva antes del Remark.
    dict(id="hmm-remark-evidencia-sin-proteger", pruebas=[FALLA_REMARK, LD + "test_solo_ahi"],
         viejo=EVIDENCIA_REMARK,
         nuevo='    reg.captura(page, f"hmm_f{f}_remark")\n'
               '    _guardar_html_completo(page, reg, f"hmm_f{f}_remark", "antes de escribir el Remark")\n'),
    dict(id="hmm-remark-con-espera", pruebas=[JUSTO_ANTES_REMARK],
         viejo=EVIDENCIA_REMARK, nuevo="    esperar(page, 0.5)\n" + EVIDENCIA_REMARK),
]

# --- CMA: la temperatura por su etiqueta «Temperature» y el «Guardar» del panel visible, medidos en la corrida
#     del 2026-09-25 (CICLO-pendientes-con-evidencia.md) ---
MUTACIONES += [
    dict(id='cma-reefer-temperatura-el-primer-campo', pruebas=[C1 + "test_js_temperatura_solo_por_su_etiqueta", FG],
         viejo="    if (bloques.length === 0) return 'sin-campo';\n",
         nuevo="    const inps = [...paneles[0].querySelectorAll('input')];\n    if (bloques.length === 0 && inps.length) { inps[0].focus(); inps[0].click(); return 'ok'; }\n    if (bloques.length === 0) return 'sin-campo';\n"),
    dict(id='cma-reefer-temperatura-por-placeholder', pruebas=[C1 + "test_js_temperatura_solo_por_su_etiqueta"],
         viejo="        return !!etq && /^temperature$/i.test((etq.textContent || '').replace(/\\s+/g, ' ').trim());\n",
         nuevo="        return (!!etq && /^temperature$/i.test((etq.textContent || '').replace(/\\s+/g, ' ').trim()))\n            || [...b.querySelectorAll('input')].some(i => /temperature/i.test(i.placeholder || ''));\n"),
    dict(id='cma-reefer-temperatura-etiqueta-parecida', pruebas=[C1 + "test_js_temperatura_solo_por_su_etiqueta"],
         viejo='/^temperature$/i.test(',
         nuevo='/temperature|temperatura|°c/i.test('),
    dict(id='cma-reefer-temperatura-elige-entre-varios-campos', pruebas=[C1 + "test_js_temperatura_solo_por_su_etiqueta"],
         viejo="    if (bloques.length > 1) return 'varios-campos';\n",
         nuevo=''),
    dict(id='cma-reefer-guarda-a-ciegas', pruebas=[C1 + "test_reefer_corta_en_cada_paso_sin_pulsar_a_ciegas", FG],
         viejo='        if btn_g.count() != 1 or not btn_g.evaluate(_JS_CMA_REEFER_GUARDAR):\n',
         nuevo='        if not btn_g.count():\n            btn_g = page.locator(".el-drawer .el-button--primary, [role=\'dialog\'] .el-button--primary")\n        if btn_g.count() != 1 or not btn_g.evaluate(_JS_CMA_REEFER_GUARDAR):\n'),
    dict(id='cma-reefer-guarda-sin-mirar-el-panel', pruebas=[C1 + "test_reefer_corta_en_cada_paso_sin_pulsar_a_ciegas", ER_ + "test_sin_el_guardar_del_panel_no_pulsa_ni_deja_lo_guardado"],
         viejo=' or not btn_g.evaluate(_JS_CMA_REEFER_GUARDAR)',
         nuevo=''),
    dict(id='cma-reefer-guarda-otro-texto', pruebas=[C1 + "test_reefer_corta_en_cada_paso_sin_pulsar_a_ciegas"],
         viejo='has_text=_r.compile(r"^\\s*Guardar\\s*$", _r.I), visible=True)',
         nuevo='has_text=_r.compile(r"^\\s*(guardar|save|confirm|confirmar)\\s*$", _r.I), visible=True)'),
    dict(id='cma-reefer-guarda-sin-visible', pruebas=[C1 + "test_reefer_corta_en_cada_paso_sin_pulsar_a_ciegas"],
         viejo='_r.I), visible=True)',
         nuevo='_r.I))'),
    dict(id='cma-reefer-js-guardar-dice-que-si', pruebas=[C1 + "test_js_guardar_solo_si_es_del_panel_visible"],
         viejo='    return paneles.length === 1 && paneles[0].contains(boton);\n',
         nuevo='    return true;\n'),
    dict(id='cma-reefer-js-guardar-cualquier-panel', pruebas=[C1 + "test_js_guardar_solo_si_es_del_panel_visible"],
         viejo='    return paneles.length === 1 && paneles[0].contains(boton);\n',
         nuevo='    return paneles.some(q => q.contains(boton));\n'),
    dict(id='cma-reefer-paneles-con-clic-generico', pruebas=[FG],
         viejo='q.contains(p)));"""',
         nuevo='q.contains(p)));\n    if (vis.length) vis[0].click();"""'),
]

# --- HYUNDAI: el Remark en el campo de su recuadro «Remark (n / m)», medido en hmm_f<fila>_remark.html de la
#     corrida del 2026-09-25 (CICLO-pendientes-con-evidencia.md) ---
TH = "test_clics.TestHyundai."

MUTACIONES += [
    dict(id='hmm-remark-primer-textarea', pruebas=[TH + "test_js_remark_no_escribe_en_otro_campo", FG],
         viejo="    if (titulos.length === 0) return 'sin-titulo';\n",
         nuevo="    if (titulos.length === 0) { const t = [...document.querySelectorAll('textarea')].find(e => e.offsetParent !== null); if (t) { t.value = txt; return 'ok'; } return 'sin-titulo'; }\n"),
    dict(id='hmm-remark-titulo-parecido', pruebas=[TH + "test_js_remark_no_escribe_en_otro_campo"],
         viejo='/^Remark\\s*\\(\\s*\\d+\\s*\\/\\s*\\d+\\s*\\)$/',
         nuevo='/remark/i'),
    dict(id='hmm-remark-titulo-sin-contador', pruebas=[TH + "test_js_remark_no_escribe_en_otro_campo"],
         viejo='/^Remark\\s*\\(\\s*\\d+\\s*\\/\\s*\\d+\\s*\\)$/',
         nuevo='/^Remark/'),
    dict(id='hmm-remark-elige-entre-varios-titulos', pruebas=[TH + "test_js_remark_no_escribe_en_otro_campo"],
         viejo="    if (titulos.length > 1) return 'varios-titulos';\n",
         nuevo=''),
    dict(id='hmm-remark-elige-entre-varios-campos', pruebas=[TH + "test_js_remark_no_escribe_en_otro_campo"],
         viejo="    if (campos.length > 1) return 'varios-campos';\n",
         nuevo=''),
    dict(id='hmm-remark-escribe-oculto', pruebas=[TH + "test_js_remark_no_escribe_en_otro_campo"],
         viejo="    if (ta.offsetParent === null) return 'oculto';\n",
         nuevo=''),
    dict(id='hmm-remark-no-escribe', pruebas=[TH + "test_js_remark_en_el_campo_de_su_recuadro"],
         viejo='    ta.value = txt;\n',
         nuevo=''),
    dict(id='hmm-remark-sin-eventos', pruebas=[TH + "test_js_remark_en_el_campo_de_su_recuadro"],
         viejo="    ta.value = txt;\n    ta.dispatchEvent(new Event('input', {bubbles: true}));\n",
         nuevo='    ta.value = txt;\n'),
    dict(id='hmm-remark-no-corta', pruebas=[TH + "test_remark_sin_su_campo_corta_sin_escribir"],
         viejo='    if donde != "ok":\n        raise ObjetivoNoEncontrado("Remark de HYUNDAI"',
         nuevo='    if False:\n        raise ObjetivoNoEncontrado("Remark de HYUNDAI"'),
    dict(id='hmm-remark-motivo-generico', pruebas=[TH + "test_remark_sin_su_campo_corta_sin_escribir"],
         viejo='_HMM_REMARK_NO_HALLADO.get(\n            donde, ',
         nuevo='_HMM_REMARK_NO_HALLADO.get(\n            "sin-campo", '),
    dict(id='hmm-sin-decorador', pruebas=[SC + "test_cada_reservador_que_corta_esta_decorado"],
         viejo='@_sin_clic_a_ciegas("hmm")\n',
         nuevo=''),
    dict(id='hmm-remark-vuelve-el-primer-textarea', pruebas=[JUSTO_ANTES_REMARK, FG],
         viejo='    _hmm_remark(page, reg)\n',
         nuevo='    page.evaluate("(txt)=>{ const ta = [...document.querySelectorAll(\'textarea\')].find(e => e.offsetParent !== null); if (ta) ta.value = txt; }", COSCO_REMARK)\n'),
]

# --- Ítem 1: un solo lector para el día de carga, con hora y en las formas de Excel (CICLO-cola-cuatro-items.md) ---
FE = AY + "TestFechas."

MUTACIONES += [
    dict(id='fecha-sin-hora', pruebas=[FE + "test_fecha_maersk", FE + "test_fecha_cma", ELIGE_COSCO],
         viejo='(?:[ T]\\d{1,2}:\\d{2}(?::\\d{2}(?:\\.\\d+)?)?)?")',
         nuevo='")'),
    dict(id='fecha-dma-sin-hora', pruebas=[FE + "test_fecha_maersk"],
         viejo='(\\d{4}|\\d{2})(?: \\d{1,2}:\\d{2}(?::\\d{2})?)?")',
         nuevo='(\\d{4}|\\d{2})")'),
    dict(id='fecha-sin-serial', pruebas=[FE + "test_fecha_maersk", FE + "test_fecha_cma"],
         viejo='        if _FECHA_SERIAL.fullmatch(s):\n',
         nuevo='        if False:\n'),
    dict(id='fecha-serial-otro-dia-cero', pruebas=[FE + "test_fecha_maersk"],
         viejo='_DIA_CERO_EXCEL = datetime.date(1899, 12, 30)',
         nuevo='_DIA_CERO_EXCEL = datetime.date(1900, 1, 1)'),
    dict(id='fecha-mes-primero', pruebas=[FE + "test_fecha_maersk", ELIGE_COSCO, AMBIGUO_COSCO],
         viejo='            return datetime.date(a, int(m.group(2)), int(m.group(1)))\n',
         nuevo='            return datetime.date(a, int(m.group(1)), int(m.group(2)))\n'),
    dict(id='fecha-no-valida', pruebas=[FE + "test_fecha_maersk"],
         viejo='    except ValueError:\n        return None\n    return None\n',
         nuevo='    finally:\n        pass\n    return None\n'),
    dict(id='fecha-ilegible-callada', pruebas=[FE + "test_ilegible_solo_si_trae_algo", FE + "test_aviso_de_fecha_ilegible"],
         viejo='    return bool("" if valor is None else str(valor).strip()) and _fecha_planilla(valor) is None\n',
         nuevo='    return False\n'),
    dict(id='fecha-aviso-callado', pruebas=[FE + "test_aviso_de_fecha_ilegible"],
         viejo='    if _fecha_ilegible(valor):\n        reg.paso(f"⚠ El día de carga',
         nuevo='    if False:\n        reg.paso(f"⚠ El día de carga'),
    dict(id='fecha-aviso-falta-en-maersk', pruebas=[FE + "test_cada_naviera_que_usa_la_fecha_avisa_y_la_lee_con_el_mismo_lector"],
         viejo='    reg.paso(f"[MAERSK fila {f}] {reserva[\'pol\']} -> {reserva[\'destino_final\']} | NAVE: {reserva[\'nave\']}")\n    _avisar_dia_carga(reserva, reg)\n',
         nuevo='    reg.paso(f"[MAERSK fila {f}] {reserva[\'pol\']} -> {reserva[\'destino_final\']} | NAVE: {reserva[\'nave\']}")\n'),
    dict(id='fecha-lector-propio-en-cma', pruebas=[FE + "test_cada_naviera_que_usa_la_fecha_avisa_y_la_lee_con_el_mismo_lector"],
         viejo='    d = _fecha_planilla(valor)\n    return f"{d.day:02d}/{d.month:02d}/{d.year}" if d else ""\n',
         nuevo='    d = datetime.datetime.strptime(str(valor), "%Y-%m-%d").date() if valor else None\n    return f"{d.day:02d}/{d.month:02d}/{d.year}" if d else ""\n'),
    dict(id='msc-fecha-ignora-el-retiro', pruebas=[AY + "TestMSC.test_desde_msc"],
         viejo='    return _desde(reserva, ("dia_carga", "dia_retiro"))\n',
         nuevo='    return _desde(reserva)\n'),
    # Desde el encargo 25 (CICLO-proxima-salida.md), MAERSK avisa solo si no pudo escribir la fecha: la del aviso sin
    # día de carga pasa a «avisa siempre».
    # Desde el encargo 26 (CICLO-cola-siete-items.md), sin día de carga avisa que busca desde mañana y no desde hoy.
    dict(id='mk-manana-sin-avisar', pruebas=[FE + "test_maersk_avisa_cuando_no_busca_desde_hoy"],
         viejo='            if fecha:\n                reg.paso(f"⚠ MAERSK: no pude escribir el día de carga ({fecha}), así que busco '
               'las salidas desde mañana.")\n            else:\n',
         nuevo='            if False:\n                pass\n            else:\n'),
    dict(id='mk-manana-avisa-siempre', pruebas=[FE + "test_maersk_avisa_cuando_no_busca_desde_hoy"],
         viejo='            if fecha:\n                reg.paso(f"⚠ MAERSK: no pude escribir',
         nuevo='            if True:\n                reg.paso(f"⚠ MAERSK: no pude escribir'),
    dict(id='mk-hoy-sin-aviso', pruebas=[FE + "test_maersk_avisa_cuando_no_busca_desde_hoy"],
         viejo='            else:\n                reg.paso("⚠ MAERSK: busco las salidas desde mañana, no desde hoy: todavía no sé si '
               'el portal acepta la "\n                         "fecha de hoy.")\n',
         nuevo='            else:\n                pass\n'),
]

# --- Ítem 2: ONE espera sus tarjetas de itinerario y dice lo que pasó (CICLO-cola-cuatro-items.md) ---
MUTACIONES += [
    dict(id='one-espera-selector-viejo', pruebas=[O1 + "test_la_espera_mira_las_tarjetas_y_no_la_lista_del_autocompletado", O1 + "test_reservar_one_espera_las_tarjetas"],
         viejo='_ONE_TARJETAS = "[class*=\'ResultCard_card\']"',
         nuevo='_ONE_TARJETAS = "mag-card, [class*=schedule], [class*=result], [data-booking-step]"'),
    dict(id='one-espera-no-distingue', pruebas=[O1 + "test_si_la_espera_vence_dice_lo_que_paso"],
         viejo='    elif n:\n        reg.paso(f"⚠ ONE: en {dt:.0f} s llegaron',
         nuevo='    elif False:\n        reg.paso(f"⚠ ONE: en {dt:.0f} s llegaron'),
    dict(id='one-espera-cree-lo-que-hay', pruebas=[O1 + "test_si_la_espera_vence_dice_lo_que_paso"],
         viejo='        vista = bool(n) and tarjetas.first.is_visible()\n',
         nuevo='        vista = bool(n)\n'),
    dict(id='one-espera-dice-sin-senal', pruebas=[O1 + "test_si_la_espera_vence_dice_lo_que_paso"],
         viejo='        reg.paso(f"⚠ ONE: en {dt:.0f} s no apareció ninguna tarjeta de itinerario. Busco la nave igual.")\n',
         nuevo='        reg.info(f"esperando {dt:.1f}s (buscar itinerarios) [sin señal]")\n'),
    dict(id='one-sin-la-espera', pruebas=[O1 + "test_reservar_one_espera_las_tarjetas"],
         viejo='    _one_esperar_resultados(page, reg)\n',
         nuevo=''),
]

# --- Ítem 3: el reemplazo de config.json reintenta si Windows lo niega un instante (CICLO-cola-cuatro-items.md) ---
PC = "test_web.TestPanelCredenciales."

MUTACIONES += [
    # Desde el encargo 26 · ítem 7, el reemplazo vive en _escribir_config, que usan los dos paneles.
    dict(id='credenciales-sin-reintento', pruebas=[PC + "test_guardar_reintenta_si_windows_niega_el_reemplazo",
                                                   PC + "test_escribir_config_es_atomica_y_reintenta"],
         viejo='    return _reemplazar(tmp, ruta)          # Windows lo niega a veces un instante (antivirus)\n',
         nuevo='    return _os.replace(tmp, ruta)\n'),
    dict(id='reemplazar-un-solo-intento', pruebas=[PC + "test_guardar_reintenta_si_windows_niega_el_reemplazo", PC + "test_guardar_se_rinde_si_el_reemplazo_sigue_negado"],
         viejo='def _reemplazar(tmp, destino, intentos=20, pausa=0.05):',
         nuevo='def _reemplazar(tmp, destino, intentos=1, pausa=0.05):'),
    dict(id='reemplazar-reintenta-todo', pruebas=[PC + "test_reemplazar_solo_reintenta_el_acceso_denegado"],
         viejo='        except PermissionError:\n            if intento == intentos - 1:\n                raise\n',
         nuevo='        except Exception:\n            if intento == intentos - 1:\n                raise\n'),
    dict(id='reemplazar-se-traga-el-error', pruebas=[PC + "test_guardar_se_rinde_si_el_reemplazo_sigue_negado"],
         viejo='        except PermissionError:\n            if intento == intentos - 1:\n                raise\n',
         nuevo='        except PermissionError:\n            if intento == intentos - 1:\n                return intento\n'),
]

# --- Ítem 4: el nombre del operador fuera de lo versionado (CICLO-cola-cuatro-items.md) ---
CR_ = "test_evidencia.TestCorridasDeReferencia."

MUTACIONES += [
    dict(id='cosco-sesion-ignora-el-nombre', pruebas=[AY + "TestCOSCO.test_sesion_activa_por_el_nombre_de_config"],
         viejo='        n = str(nombre or "").strip().lower()\n',
         nuevo='        n = ""\n'),
    dict(id='cosco-sesion-sin-logout', pruebas=[AY + "TestCOSCO.test_sesion_activa_por_el_nombre_de_config"],
         viejo='bool((n and n in t) or "aquachile" in t) and ("logout" in t or "message center" in t)',
         nuevo='bool((n and n in t) or "aquachile" in t)'),
    dict(id='cosco-sesion-lee-siempre', pruebas=[AY + "TestCOSCO.test_sesion_activa_por_el_nombre_de_config"],
         viejo='    u = (url or "").lower()\n    if "/ebusiness/dashboard" in u:\n',
         nuevo='    u = (url or "").lower()\n    leer_texto()\n    if "/ebusiness/dashboard" in u:\n'),
    dict(id='cosco-login-sin-nombre', pruebas=[AY + "TestCOSCO.test_login_cosco_lee_el_nombre_de_config"],
         viejo='                creds.get("nombre_en_pantalla", ""))\n',
         nuevo='                "")\n'),
    dict(id='referencia-sin-comodin', pruebas=[CR_ + "test_son_las_que_nombran_los_generadores", CR_ + "test_calzan_con_cualquier_operador_y_solo_en_su_fecha"],
         viejo='    "web_cosco_*_20260922_134605",\n',
         nuevo='    "web_cosco_op_prueba_20260922_134605",\n'),
    dict(id='referencia-por-igualdad', pruebas=[CR_ + "test_calzan_con_cualquier_operador_y_solo_en_su_fecha", CR_ + "test_la_poda_no_las_toca"],
         viejo='    return any(fnmatch.fnmatchcase(nombre, p) for p in CORRIDAS_DE_REFERENCIA)\n',
         nuevo='    return nombre in CORRIDAS_DE_REFERENCIA\n'),
    dict(id='plantilla-con-un-nombre', archivo='config.example.json', pruebas=[AY + "TestPlantilla.test_la_plantilla_no_trae_nombres"],
         viejo='    "usuario1": {\n',
         nuevo='    "juanito": {\n'),
]

# --- Encargo 25: la próxima salida, decidida por Marcelo (CICLO-proxima-salida.md) ---
PSAL = AY + "TestProximaSalida."
TCOS = AY + "TestCOSCO."
JSC = K1 + "test_js_lista_lee_la_salida_y_la_llegada_de_la_tarjeta"

MUTACIONES += [
    dict(id="proxima-la-primera-de-la-lista", pruebas=[PSAL + "test_la_proxima_desde_la_fecha"],
         viejo="    primera = min(f for f, _ in futuras)\n", nuevo="    primera = futuras[0][0]\n"),
    dict(id="proxima-empate-elige-la-primera", pruebas=[PSAL + "test_la_proxima_desde_la_fecha"],
         viejo='    return (del_dia[0], "") if len(del_dia) == 1 else (None, "empate")\n',
         nuevo='    return (del_dia[0], "")\n'),
    dict(id="proxima-cuenta-las-pasadas", pruebas=[PSAL + "test_la_proxima_desde_la_fecha"],
         viejo="    futuras = [(f, o) for f, o in salidas if f >= desde]\n", nuevo="    futuras = list(salidas)\n"),
    dict(id="proxima-sin-fecha-sigue", pruebas=[PSAL + "test_la_proxima_desde_la_fecha"],
         viejo='    if any(f is None for f, _ in salidas):\n        return None, "sin-fecha"\n', nuevo=""),
    dict(id="proxima-sola-sin-fecha-no", pruebas=[PSAL + "test_la_proxima_desde_la_fecha"],
         viejo='    if len(salidas) == 1 and salidas[0][0] is None:\n        return salidas[0][1], ""\n', nuevo=""),
    dict(id="desde-sin-el-maximo", pruebas=[PSAL + "test_desde_hoy_o_el_dia_de_carga_posterior"],
         viejo="    return max(hoy, d) if d else hoy\n", nuevo="    return d if d else hoy\n"),
    dict(id="desde-sin-el-dia-de-carga", pruebas=[PSAL + "test_desde_hoy_o_el_dia_de_carga_posterior"],
         viejo="    return max(hoy, d) if d else hoy\n", nuevo="    return hoy\n"),
    dict(id="motivo-cuenta-todas", pruebas=[PSAL + "test_el_motivo_en_palabras"],
         viejo='    return (f"{sum(1 for f, _ in salidas if f == primera)} de las {n} opciones',
         nuevo='    return (f"{n} de las {n} opciones'),
    dict(id="motivo-una-sola-como-varias", pruebas=[PSAL + "test_el_motivo_en_palabras"],
         viejo="        if n < 2:\n", nuevo="        if n < 1:\n"),
    dict(id="cosco-itinerario-el-primero-de-la-lista", pruebas=[ELIGE_COSCO],
         viejo="    return _proxima_salida(_cosco_salidas(cand), _desde(reserva), _cosco_transito)\n", nuevo='    return (cand[0], "")\n'),
    dict(id="cosco-itinerario-desde-hoy-siempre", pruebas=[ELIGE_COSCO],
         viejo="    return _proxima_salida(_cosco_salidas(cand), _desde(reserva), _cosco_transito)\n",
         nuevo="    return _proxima_salida(_cosco_salidas(cand), datetime.date.today(), _cosco_transito)\n"),
    dict(id="cosco-itinerario-sin-motivo", pruebas=[AMBIGUO_COSCO],
         viejo="    por_que = _por_que_sin_salida(motivo, _cosco_salidas(cand), _desde(reserva), _cosco_transito)\n",
         nuevo="    por_que = motivo\n"),
    dict(id="cosco-itinerario-sin-salida-antes", pruebas=[NO_EL_PRIMERO_COSCO],
         viejo="    filas = _cosco_con_salida(filas)\n", nuevo=""),
    dict(id="cosco-tarjeta-anio-de-hoy", pruebas=[TCOS + "test_fecha_de_la_tarjeta_sin_anio"],
         viejo="    for anio in (hoy.year - 1, hoy.year, hoy.year + 1):\n", nuevo="    for anio in (hoy.year,):\n"),
    dict(id="cosco-tarjeta-sin-dia-de-semana", pruebas=[TCOS + "test_fecha_de_la_tarjeta_sin_anio"],
         viejo="        if d.weekday() == _COSCO_DIAS.index(m.group(3).upper()):\n", nuevo="        if True:\n"),
    dict(id="cosco-salida-del-corte", pruebas=[TCOS + "test_cada_itinerario_con_su_salida"],
         viejo='        d = _cosco_fecha_tarjeta(x.get("salida"), hoy)\n',
         nuevo='        d = _cosco_fecha_tarjeta(x.get("corte"), hoy)\n'),
    dict(id="cosco-salida-toca-la-lista", pruebas=[TCOS + "test_cada_itinerario_con_su_salida"],
         viejo='        out.append(dict(x, etd=d.isoformat() if d else ""))\n',
         nuevo='        x["etd"] = d.isoformat() if d else ""\n        out.append(x)\n'),
    dict(id="cosco-js-fechas-del-boton", pruebas=[JSC],
         viejo="const fechas=[...tarjeta(b).querySelectorAll('*')]", nuevo="const fechas=[...b.querySelectorAll('*')]"),
    dict(id="cosco-js-tarjeta-toda-la-lista", pruebas=[JSC],
         viejo="btns.filter(x=>c.parentElement.contains(x)).length===1) c=c.parentElement;",
         nuevo="btns.filter(x=>c.parentElement.contains(x)).length>=1) c=c.parentElement;"),
    dict(id="cosco-js-corte-como-salida", pruebas=[JSC],
         viejo="corte: m?m[1]:'', salida: fechas[0]||''", nuevo="corte: m?m[1]:'', salida: m?m[1]:''"),
]

# --- Encargo 25 · MSC: busca desde hoy y elige la próxima salida (CICLO-proxima-salida.md) ---
MS = "test_clics.TestMsc."

MUTACIONES += [
    dict(id="desde-solo-el-primer-campo", pruebas=[AY + "TestMSC.test_desde_msc"],
         viejo="    d = next((f for f in (_fecha_planilla((reserva or {}).get(c)) for c in campos) if f), None)\n",
         nuevo="    d = _fecha_planilla((reserva or {}).get(campos[0]))\n"),
    # Anclada con su expresión regular: MAERSK tiene la misma línea de retorno (_mk_fecha_salida).
    dict(id="msc-etd-mes-desde-cero", pruebas=[AY + "TestMSC.test_fecha_etd_msc"],
         viejo='(\\d{4})\\s*", str(texto or ""))\n    if not m or m.group(2).upper() not in _MESES_EN:\n        return None\n'
               "    try:\n        return datetime.date(int(m.group(3)), _MESES_EN.index(m.group(2).upper()) + 1, int(m.group(1)))\n",
         nuevo='(\\d{4})\\s*", str(texto or ""))\n    if not m or m.group(2).upper() not in _MESES_EN:\n        return None\n'
               "    try:\n        return datetime.date(int(m.group(3)), _MESES_EN.index(m.group(2).upper()), int(m.group(1)))\n"),
    dict(id="msc-elige-la-primera", pruebas=[MS + "test_salida_la_proxima_nunca_la_primera"],
         viejo="    return _proxima_salida(_msc_salidas(exacta), desde, _msc_transito)\n", nuevo='    return (exacta[0], "")\n'),
    dict(id="msc-salidas-sin-fecha", pruebas=[MS + "test_salida_la_proxima_nunca_la_primera"],
         viejo='    return [(_msc_fecha_etd(x.get("etd")), x) for x in exacta]\n',
         nuevo="    return [(None, x) for x in exacta]\n"),
    dict(id="msc-ambigua-sin-evidencia", pruebas=[MS + "test_salida_ambigua_queda_no_enviada_con_evidencia",
                                                  LD + "test_solo_ahi"],
         viejo="    _evidencia_antes_de_la_guarda(page, reg, f\"msc_f{reserva['fila']}_itinerarios\"",
         nuevo="    (lambda *a, **k: None)(page, reg, f\"msc_f{reserva['fila']}_itinerarios\""),
    dict(id="msc-ambigua-sin-lista", pruebas=[MS + "test_salida_ambigua_queda_no_enviada_con_evidencia"],
         viejo="    reg.info(\"itinerarios que calzan: \" + \" | \".join(f\"{x.get('nave')} ETD",
         nuevo="    str(\"itinerarios que calzan: \" + \" | \".join(f\"{x.get('nave')} ETD"),
    dict(id="msc-ambigua-sin-motivo", pruebas=[MS + "test_salida_ambigua_queda_no_enviada_con_evidencia"],
         viejo="    por_que = _por_que_sin_salida(motivo, _msc_salidas(exacta), desde, _msc_transito)\n", nuevo="    por_que = motivo\n"),
    dict(id="msc-reserva-la-primera", pruebas=[MS + "test_reservar_msc_no_toma_la_primera"],
         viejo='    elegida, motivo = _msc_elegir_salida(exacta, desde) if exacta else (None, "")\n',
         nuevo='    elegida, motivo = (exacta[0], "") if exacta else (None, "")\n'),
    dict(id="msc-sigue-sin-una", pruebas=[MS + "test_reservar_msc_no_toma_la_primera"],
         viejo="    if exacta and elegida is None:\n        return _msc_salida_ambigua(page, reg, reserva, exacta, motivo, desde)\n",
         nuevo="    if exacta and elegida is None:\n        elegida = exacta[0]\n"),
    dict(id="msc-busca-desde-otro-dia", pruebas=[MS + "test_reservar_msc_no_toma_la_primera"],
         viejo="    _msc_fecha(page, desde.isoformat(), reg)\n",
         nuevo="    _msc_fecha(page, (desde + datetime.timedelta(days=18)).isoformat(), reg)\n"),
]

# --- Encargo 25 · ONE: lee sus tarjetas y pulsa la de la próxima salida (CICLO-proxima-salida.md) ---
ON = "test_clics.TestOne."

MUTACIONES += [
    dict(id="one-tarjetas-cualquier-elemento", pruebas=[ON + "test_js_tarjetas_de_la_nave_con_su_salida"],
         viejo="    return [...document.querySelectorAll(\"[class*='ResultCard_card__']\")].map((c, i) => {",
         nuevo="    return [...document.querySelectorAll(\"div\")].map((c, i) => {"),
    dict(id="one-tarjetas-la-llegada", pruebas=[ON + "test_js_tarjetas_de_la_nave_con_su_salida"],
         viejo="salida: fechas[0] || ''", nuevo="salida: fechas[1] || ''"),
    dict(id="one-tarjetas-sin-botones", pruebas=[ON + "test_js_tarjetas_de_la_nave_con_su_salida"],
         viejo="                botones: [...c.querySelectorAll('button,a')].filter(b => reserva.test(b.textContent||'')).length,\n",
         nuevo="                botones: 1,\n"),
    dict(id="one-clic-la-primera", pruebas=[ON + "test_js_clic_solo_el_boton_de_la_tarjeta_elegida"],
         viejo="    const c = [...document.querySelectorAll(\"[class*='ResultCard_card__']\")][i];",
         nuevo="    const c = [...document.querySelectorAll(\"[class*='ResultCard_card__']\")][0];"),
    dict(id="one-clic-con-dos-botones", pruebas=[ON + "test_js_clic_solo_el_boton_de_la_tarjeta_elegida"],
         viejo="    if (btns.length !== 1) return false;", nuevo="    if (!btns.length) return false;"),
    dict(id="one-clic-sin-dialogo", pruebas=[ON + "test_js_clic_solo_el_boton_de_la_tarjeta_elegida"],
         viejo="    if (dlg) {\n        // Nunca «Next»", nuevo="    if (false) {\n        // Nunca «Next»"),
    dict(id="one-salidas-sin-fecha", pruebas=[ON + "test_salidas_de_las_tarjetas"],
         viejo='            d = datetime.date.fromisoformat(t.get("salida") or "")\n', nuevo="            d = None\n"),
    dict(id="one-sin-una-sin-evidencia", pruebas=[ON + "test_sin_una_salida_queda_no_enviada_con_evidencia"],
         viejo='    _one_detenida(page, reg, reserva["fila"])\n', nuevo="    pass\n"),
    dict(id="one-sin-una-sin-motivo", pruebas=[ON + "test_sin_una_salida_queda_no_enviada_con_evidencia"],
         viejo="    por_que = _por_que_sin_salida(motivo, _one_salidas(tarjetas), desde, _one_transito)\n", nuevo="    por_que = motivo\n"),
    dict(id="one-sin-una-sin-lista", pruebas=[ON + "test_sin_una_salida_queda_no_enviada_con_evidencia"],
         viejo='    reg.info("tarjetas que calzan: " + ', nuevo='    str("tarjetas que calzan: " + '),
    dict(id="one-reserva-la-primera", pruebas=[ON + "test_reservar_one_elige_la_proxima_salida"],
         viejo='    elegida, motivo = _proxima_salida(_one_salidas(tarjetas), desde, _one_transito) if tarjetas else (None, "")\n',
         nuevo='    elegida, motivo = (tarjetas[0], "") if tarjetas else (None, "")\n'),
    dict(id="one-sigue-sin-una", pruebas=[ON + "test_reservar_one_elige_la_proxima_salida"],
         viejo="    if tarjetas and elegida is None:\n        return _one_sin_una_salida(page, reg, reserva, tarjetas, motivo, desde)\n",
         nuevo="    if tarjetas and elegida is None:\n        elegida = tarjetas[0]\n"),
    dict(id="one-cuenta-sin-boton", pruebas=[ON + "test_reservar_one_elige_la_proxima_salida"],
         viejo='    tarjetas = [t for t in tarjetas if t.get("botones") == 1]\n', nuevo=""),
    dict(id="one-desde-otro-dia", pruebas=[ON + "test_reservar_one_elige_la_proxima_salida"],
         viejo='    tarjetas = [t for t in tarjetas if t.get("botones") == 1]\n    desde = _desde(reserva)\n',
         nuevo='    tarjetas = [t for t in tarjetas if t.get("botones") == 1]\n    desde = datetime.date.today()\n'),
    # Encargo 26 · ítem 5: ONE avisa, como las demás, el día de carga que no se entiende (CICLO-cola-siete-items.md).
    dict(id="one-sin-aviso-de-fecha",
         pruebas=[AY + "TestFechas.test_cada_naviera_que_usa_la_fecha_avisa_y_la_lee_con_el_mismo_lector"],
         viejo="    reg.paso(f\"[fila {f}] {reserva['pol']} -> {reserva['destino_final']} | NAVE: {reserva['nave']}\")\n"
               "    _avisar_dia_carga(reserva, reg)\n",
         nuevo="    reg.paso(f\"[fila {f}] {reserva['pol']} -> {reserva['destino_final']} | NAVE: {reserva['nave']}\")\n"),
]

# --- Encargo 25 · MAERSK: la próxima salida que se puede reservar en «Select sailing» (CICLO-proxima-salida.md) ---
ELIGE_MK = MK + "test_elige_la_proxima_salida_que_se_puede_reservar"
SIN_UNA_MK = MK + "test_sin_una_salida_queda_no_enviada_con_evidencia"

MUTACIONES += [
    dict(id="mk-salidas-cualquier-tarjeta", pruebas=[MK + "test_js_salidas_lee_la_salida_y_si_se_puede_reservar"],
         viejo="    const tarjetas = [...document.querySelectorAll('mc-card.new-sailings-card')];",
         nuevo="    const tarjetas = [...document.querySelectorAll('mc-card')];"),
    dict(id="mk-salidas-palabras-sin-orden", pruebas=[MK + "test_js_salidas_lee_la_salida_y_si_se_puede_reservar"],
         viejo="            const j = _palabraEn(t, x, pos);", nuevo="            const j = _palabraEn(t, x, 0);"),
    dict(id="mk-salidas-otra-etiqueta", pruebas=[MK + "test_js_salidas_lee_la_salida_y_si_se_puede_reservar"],
         viejo="(l.textContent || '').trim().toLowerCase() === 'departure'",
         nuevo="(l.textContent || '').trim().toLowerCase() === 'arrival'"),
    dict(id="mk-salidas-sin-book", pruebas=[MK + "test_js_salidas_lee_la_salida_y_si_se_puede_reservar"],
         viejo="                book: [...c.querySelectorAll(\"mc-button, button, [role='button']\")].filter(esBook).length};",
         nuevo="                book: 1};"),
    dict(id="mk-fecha-salida-entera", pruebas=[AY + "TestMAERSK.test_fecha_salida_maersk"],
         viejo='    m = _re_mk.match(r"\\s*(\\d{1,2}) ([A-Za-z]{3}) (\\d{4})\\b", str(texto or ""))',
         nuevo='    m = _re_mk.fullmatch(r"\\s*(\\d{1,2}) ([A-Za-z]{3}) (\\d{4})\\b", str(texto or ""))'),
    dict(id="mk-elige-la-primera", pruebas=[ELIGE_MK],
         viejo="            elegida, motivo = _proxima_salida(_mk_salidas(cand), desde, _mk_transito)\n",
         nuevo='            elegida, motivo = cand[0], ""\n'),
    dict(id="mk-cuenta-sin-book", pruebas=[ELIGE_MK],
         viejo='        cand = [s for s in pedidas if s.get("book") == 1]\n', nuevo="        cand = list(pedidas)\n"),
    dict(id="mk-empate-elige", pruebas=[ELIGE_MK],
         viejo='            if elegida is None:\n                return "", (cand, motivo, desde), None, None\n',
         nuevo="            if elegida is None:\n                elegida = cand[0]\n"),
    dict(id="mk-viaje-no-filtra", pruebas=[ELIGE_MK],
         viejo='        pedidas = [s for s in de_la_nave if s.get("viaje")] if viaje_solicitado else de_la_nave\n',
         nuevo="        pedidas = de_la_nave\n"),
    dict(id="mk-pulsar-otra-tarjeta", pruebas=[ELIGE_MK],
         viejo='    tarjeta = page.locator("mc-card.new-sailings-card").nth(i)\n',
         nuevo='    tarjeta = page.locator("mc-card.new-sailings-card").nth(0)\n'),
    dict(id="mk-sin-una-sin-evidencia", pruebas=[SIN_UNA_MK],
         viejo='    _mk_detenida(page, reg, reserva["fila"])\n    por_que = _por_que_sin_salida(motivo, _mk_salidas(salidas)',
         nuevo='    por_que = _por_que_sin_salida(motivo, _mk_salidas(salidas)'),
    dict(id="mk-sin-una-sin-motivo", pruebas=[SIN_UNA_MK],
         viejo="    por_que = _por_que_sin_salida(motivo, _mk_salidas(salidas), desde, _mk_transito)\n", nuevo="    por_que = motivo\n"),
    dict(id="mk-detenida-sin-evidencia", pruebas=[SIN_UNA_MK, MK + "test_sin_nave_se_detiene_en_select_sailing",
                                                  LD + "test_solo_ahi"],
         viejo='    _evidencia_antes_de_la_guarda(page, reg, f"mk_f{fila}_detenida", "donde se detuvo", completa=False)\n',
         nuevo="    pass\n"),
    dict(id="mk-reserva-sigue-sin-una", pruebas=[MK + "test_sin_una_salida_no_llega_a_la_guarda"],
         viejo="    if sin_una:\n        return _mk_sin_una_salida(page, reg, reserva, *sin_una)\n", nuevo=""),
]

# --- Encargo 26 · ítem 3: HYUNDAI y CMA dejan la evidencia de su lista de salidas (CICLO-cola-siete-items.md) ---
LH = "test_evidencia.TestEvidenciaListaHyundai."
RC = "test_evidencia.TestEvidenciaRutasCma."

MUTACIONES += [
    dict(id="hmm-lista-sin-evidencia", pruebas=[LH + "test_va_despues_de_esperar_la_lista_y_antes_de_leerla",
                                                LD + "test_solo_ahi"],
         viejo='    _evidencia_antes_de_la_guarda(page, reg, f"hmm_f{f}_naves", "en la lista de naves", completa=False)\n',
         nuevo=""),
    dict(id="hmm-lista-pagina-completa", pruebas=[LH + "test_la_ventana_y_el_html_sin_clics"],
         viejo='"en la lista de naves", completa=False)', nuevo='"en la lista de naves", completa=True)'),
    dict(id="hmm-lista-otro-momento", pruebas=[LH + "test_la_ventana_y_el_html_sin_clics",
                                               LH + "test_si_la_evidencia_falla_sigue_igual"],
         viejo='f"hmm_f{f}_naves", "en la lista de naves"', nuevo='f"hmm_f{f}_naves", "en la lista"'),
    dict(id="cma-rutas-sin-evidencia", pruebas=[RC + "test_la_lista_antes_de_leerla",
                                                RC + "test_y_otra_tras_cada_carga", LD + "test_solo_ahi"],
         viejo='        _evidencia_antes_de_la_guarda(page, reg, nombre, "en la lista de rutas", completa=False)\n',
         nuevo=""),
    dict(id="cma-rutas-un-solo-nombre", pruebas=[RC + "test_y_otra_tras_cada_carga"],
         viejo='        sufijo = "" if not cargas else "_mas" if cargas == 1 else f"_mas{cargas}"\n',
         nuevo='        sufijo = "" if not cargas else "_mas"\n'),
    # La evidencia nunca corta el flujo: una reserva sin «fila» no hace caer la elección del itinerario.
    dict(id="cma-rutas-exige-fila", pruebas=["test_clics.TestCma.test_itinerario_sin_nave_no_elige_el_primero"],
         viejo="        nombre = f\"cma_f{reserva.get('fila', '')}_rutas\"", nuevo="        nombre = f\"cma_f{reserva['fila']}_rutas\""),
]

# --- Encargo 26 · ítem 6: la sonda de secretos bloquea el nombre o el apellido del operador en lo que va al staging;
# hasta 0e15b8a solo lo informaba (CICLO-cola-siete-items.md). Mutan tests/sonda_secretos.py: el censo deja la copia
# mutada en las fuentes, y test_sonda la carga de ahí. ---
SO = "test_sonda.TestSondaNombre."
SP = "test_sonda.TestSondaDeUnaPunta."
SONDA = "tests/sonda_secretos.py"

MUTACIONES += [
    dict(id="sonda-nombre-solo-informa", archivo=SONDA,
         pruebas=[SP + "test_bloquea_el_nombre_en_el_contenido", SP + "test_bloquea_el_nombre_en_la_ruta_sin_mostrarla",
                  SP + "test_el_negativo_del_nombre_da_uno"],
         viejo="    sys.exit(codigo_de_salida(modo, hallazgos, rutas_malas, nombres, en_cuenta))\n",
         nuevo="    sys.exit(1 if hallazgos or rutas_malas else 0)\n"),
    dict(id="sonda-nombre-bloquea-en-el-almacen", archivo=SONDA, pruebas=[SO + "test_el_nombre_bloquea_salvo_en_el_almacen"],
         viejo='((nombres or cuenta) and modo != "--almacen")', nuevo="(nombres or cuenta)"),
    dict(id="sonda-nombre-en-todo", archivo=SONDA,
         pruebas=[SO + "test_encuentra_el_nombre_sin_mayusculas_ni_tildes", SP + "test_deja_pasar_el_staging_limpio"],
         viejo="        if any(t in texto for t in terminos):\n", nuevo="        if True:\n"),
    dict(id="sonda-nombre-sin-la-clave", archivo=SONDA, pruebas=[SO + "test_los_terminos_salen_de_la_clave_la_descripcion_y_cosco"],
         viejo="            fuentes.append(clave)\n", nuevo="            pass\n"),
    dict(id="sonda-nombre-con-la-clave-de-plantilla", archivo=SONDA,
         pruebas=[SO + "test_los_terminos_salen_de_la_clave_la_descripcion_y_cosco"],
         viejo="        if not CLAVE_DE_PLANTILLA.fullmatch(clave):\n", nuevo="        if True:\n"),
    dict(id="sonda-nombre-con-rellenar", archivo=SONDA,
         pruebas=[SO + "test_los_terminos_salen_de_la_clave_la_descripcion_y_cosco",
                  SP + "test_aborta_si_config_no_sabe_el_nombre"],
         viejo='        if "rellenar" not in _plano(desc):\n', nuevo="        if True:\n"),
    dict(id="sonda-nombre-sin-cosco", archivo=SONDA,
         pruebas=[SO + "test_los_terminos_salen_de_la_clave_la_descripcion_y_cosco",
                  SP + "test_bloquea_el_nombre_en_el_contenido"],
         viejo='        fuentes = [str(cosco.get("nombre_en_pantalla") or "")]\n', nuevo="        fuentes = []\n"),
    dict(id="sonda-nombre-con-palabras-cortas", archivo=SONDA,
         pruebas=[SO + "test_los_terminos_salen_de_la_clave_la_descripcion_y_cosco"],
         viejo="            if len(palabra) >= LARGO_MINIMO:\n", nuevo="            if palabra:\n"),
    dict(id="sonda-nombre-con-mayusculas", archivo=SONDA,
         pruebas=[SO + "test_los_terminos_salen_de_la_clave_la_descripcion_y_cosco",
                  SO + "test_encuentra_el_nombre_sin_mayusculas_ni_tildes"],
         viejo='    return "".join(c for c in t if not unicodedata.combining(c)).casefold()\n',
         nuevo='    return "".join(c for c in t if not unicodedata.combining(c))\n'),
    dict(id="sonda-nombre-con-tildes", archivo=SONDA,
         pruebas=[SO + "test_los_terminos_salen_de_la_clave_la_descripcion_y_cosco",
                  SO + "test_encuentra_el_nombre_sin_mayusculas_ni_tildes"],
         viejo='    return "".join(c for c in t if not unicodedata.combining(c)).casefold()\n',
         nuevo="    return t.casefold()\n"),
    dict(id="sonda-nombre-sin-utf16", archivo=SONDA, pruebas=[SO + "test_encuentra_el_nombre_sin_mayusculas_ni_tildes"],
         viejo='(ruta, b.decode("utf-8", "ignore"), b.decode("utf-16-le", "ignore"))',
         nuevo='(ruta, b.decode("utf-8", "ignore"))'),
    dict(id="sonda-nombre-sin-la-ruta", archivo=SONDA,
         pruebas=[SO + "test_encuentra_el_nombre_sin_mayusculas_ni_tildes",
                  SP + "test_bloquea_el_nombre_en_la_ruta_sin_mostrarla"],
         viejo='(ruta, b.decode("utf-8", "ignore"), b.decode("utf-16-le", "ignore"))',
         nuevo='(b.decode("utf-8", "ignore"), b.decode("utf-16-le", "ignore"))'),
    dict(id="sonda-sin-control-del-nombre", archivo=SONDA, pruebas=[SP + "test_aborta_si_config_no_sabe_el_nombre"],
         viejo='    if not terminos or any(not con_nombre([("config.json", crudo)], [t]) for t in terminos):\n',
         nuevo="    if False:\n"),
    dict(id="sonda-muestra-la-ruta-con-el-nombre", archivo=SONDA,
         pruebas=[SP + "test_bloquea_el_nombre_en_la_ruta_sin_mostrarla"],
         viejo='    return "(ruta con el nombre del operador)" if con_nombre([(ruta, b"")], terminos) else ruta\n',
         nuevo="    return ruta\n"),
    dict(id="sonda-sin-negativo-del-nombre", archivo=SONDA, pruebas=[SP + "test_el_negativo_del_nombre_da_uno"],
         viejo='            entradas.append((f"NEGATIVO/nombre_{i}.txt", f"Lo pidió {t.upper()}.".encode("utf-8")))\n',
         nuevo="            pass\n"),
]

# --- Encargo 26 · ítem 7: el panel de escritorio escribe config.json de forma atómica, con el mismo ayudante que el
# panel web; hasta 0af2d5b lo abría con open(w) (CICLO-cola-siete-items.md). ---
MUTACIONES += [
    dict(id="config-escritorio-no-atomica", pruebas=[PC + "test_los_dos_paneles_escriben_config_con_el_mismo_ayudante"],
         viejo='                    _escribir_config(self.cfg, BASE / "config.json")\n',
         nuevo='                    (BASE / "config.json").write_text(json.dumps(self.cfg, ensure_ascii=False, indent=2), '
               'encoding="utf-8")\n'),
    dict(id="config-web-no-atomica",
         pruebas=[PC + "test_los_dos_paneles_escriben_config_con_el_mismo_ayudante",
                  PC + "test_guardar_reintenta_si_windows_niega_el_reemplazo",
                  PC + "test_guardar_se_rinde_si_el_reemplazo_sigue_negado"],
         viejo='                    _escribir_config(cfg, BASE / "config.json")\n',
         nuevo='                    (BASE / "config.json").write_text(_json.dumps(cfg, ensure_ascii=False, indent=2), '
               'encoding="utf-8")\n'),
    dict(id="escribir-config-otro-formato", pruebas=[PC + "test_escribir_config_es_atomica_y_reintenta"],
         viejo="        _json.dump(cfg, f, ensure_ascii=False, indent=2)\n", nuevo="        _json.dump(cfg, f)\n"),
    dict(id="escribir-config-sin-temporal",
         pruebas=[PC + "test_escribir_config_no_toca_el_archivo_si_el_reemplazo_sigue_negado",
                  PC + "test_los_dos_paneles_escriben_config_con_el_mismo_ayudante"],
         viejo='    tmp = ruta.with_suffix(".json.tmp")\n', nuevo="    tmp = ruta\n"),
]

# --- Encargo 27 · ítem 1: una tarjeta calza con la nave solo si trae todas sus palabras, en las seis navieras; sin
# palabras de nave, ninguna (CICLO-cola-tres-items.md). ---
FOTO = "test_clics.TestFotoDeClicsGenericos.test_ningun_clic_generico_nuevo_antes_de_la_guarda"
NC = "test_ayudantes.TestNaveCompleta."

MUTACIONES += [
    dict(id="one-nave-alguna-palabra", pruebas=[ON + "test_js_tarjetas_de_la_nave_con_su_salida"],
         viejo="const calza = _traeLaNave(suNave, palabras);",
         nuevo="const calza = palabras.some(x => _palabraEn(suNave, x, 0) >= 0);"),
    dict(id="one-nave-sin-guarda-vacia", pruebas=[ON + "test_js_tarjetas_de_la_nave_con_su_salida"],
         viejo="const calza = _traeLaNave(suNave, palabras);",
         nuevo="const calza = palabras.every(x => _palabraEn(suNave, x, 0) >= 0);"),
    dict(id="one-nave-sin-el-viaje", pruebas=[ON + "test_js_tarjetas_de_la_nave_con_su_salida"],
         viejo="const calza = _traeLaNave(suNave, palabras);",
         nuevo="const calza = _traeLaNave(suNave, palabras.slice(0, -1));"),
    dict(id="one-nave-viaje-solo", pruebas=[ON + "test_js_tarjetas_de_la_nave_con_su_salida", FOTO],
         viejo="const calza = _traeLaNave(suNave, palabras);",
         nuevo="const calza = _traeLaNave(suNave, palabras) || "
               "(palabras.length > 0 && _palabraEn(suNave, palabras[palabras.length - 1], 0) >= 0);"),
    dict(id="one-nave-en-toda-la-tarjeta", pruebas=[ON + "test_js_tarjetas_de_la_nave_con_su_salida"],
         viejo="const suNave = enlace ? (enlace.textContent||'') : '';",
         nuevo="const suNave = (c.textContent||'');"),
    dict(id="one-nave-distingue-mayusculas-de-la-fila", pruebas=[ON + "test_js_tarjetas_de_la_nave_con_su_salida"],
         viejo="const palabras = nave.toUpperCase().split('/')", nuevo="const palabras = nave.split('/')"),
    dict(id="one-nave-sin-barra", pruebas=[ON + "test_js_tarjetas_de_la_nave_con_su_salida"],
         viejo="const palabras = nave.toUpperCase().split('/').join(' ').split(",
         nuevo="const palabras = nave.toUpperCase().split("),
    dict(id="hmm-nave-primera-palabra-book", pruebas=[TH + "test_js_tarjetas_con_su_1st_vessel"],
         viejo="calza: primera !== null && _traeLaNave(primera, T),",
         nuevo="calza: primera !== null && (_traeLaNave(primera, T) || (T.length > 0 && "
               "_palabraEn(primera.toUpperCase(), T[0], 0) >= 0)),"),
    dict(id="hmm-nave-primera-palabra-previa", pruebas=[TH + "test_js_nave_con_todas_sus_palabras"],
         viejo="if (_traeLaNave(v, T)) {",
         nuevo="if (_traeLaNave(v, T) || (T.length > 0 && _palabraEn(v, T[0], 0) >= 0)) {"),
    dict(id="hmm-nave-sin-guarda-vacia", pruebas=[TH + "test_js_nave_con_todas_sus_palabras"],
         viejo="    if (T.length === 0) return { idx: -1, motivo: 'sin_nave' };\n", nuevo=""),
    dict(id="cma-nave-sin-prefijos", pruebas=[C1 + "test_js_rutas_nave_con_todas_sus_palabras"],
         viejo="const matched = _traeLaNave(upperTxt, toks);",
         nuevo="const matched = _traeLaNave(upperTxt, toks.filter(tk => !['MSC', 'CMA', 'CGM', 'HMM', 'ONE', 'COSCO', "
               "'MV'].includes(tk)));"),
    dict(id="cma-nave-sin-guarda-vacia", pruebas=[C1 + "test_js_rutas_nave_con_todas_sus_palabras"],
         viejo="const matched = _traeLaNave(upperTxt, toks);",
         nuevo="const matched = toks.every(tk => _palabraEn(upperTxt, tk, 0) >= 0);"),
    # El calce de CMA como era hasta 9051f43, en sus tres lugares: las palabras sin los prefijos de naviera, que se
    # pasaban a la lectura como «sigToks» y le bastaban para calzar.
    dict(id="cma-vuelve-sin-prefijos", pruebas=[C1 + "test_itinerario_comodin_no_se_busca_como_nave"], cambios=[
        ("if nave_especificada else [])\n",
         'if nave_especificada else [])\n    sig_toks = [t for t in toks if t not in {"MSC", "CMA", "CGM", "HMM", "ONE", '
         '"COSCO", "MV"}] or toks\n'),
        ('res = page.evaluate(_JS_CMA_RUTAS, {"toks": toks})',
         'res = page.evaluate(_JS_CMA_RUTAS, {"toks": toks, "sigToks": sig_toks})'),
        ("const matched = _traeLaNave(upperTxt, toks);",
         "const matched = _traeLaNave(upperTxt, toks) || _traeLaNave(upperTxt, args.sigToks || []);")]),
    dict(id="cma-comodin-se-busca", pruebas=[C1 + "test_itinerario_comodin_no_se_busca_como_nave"],
         viejo="nave_pedida.upper()) if len(t) > 1]\n            if nave_especificada else [])\n",
         nuevo="nave_pedida.upper()) if len(t) > 1])\n"),
    dict(id="trae-la-nave-sin-palabras", pruebas=[NC + "test_trae_la_nave"],
         viejo="    return bool(palabras) and all(_palabra_en(t, p) >= 0 for p in palabras)\n",
         nuevo="    return all(_palabra_en(t, p) >= 0 for p in palabras)\n"),
    dict(id="trae-la-nave-con-mayusculas", pruebas=[NC + "test_trae_la_nave"],
         viejo='    t = str(texto or "").upper()\n', nuevo='    t = str(texto or "")\n'),
    dict(id="msc-calce-sin-el-ayudante", pruebas=[NC + "test_msc_y_cosco_calzan_con_el_ayudante"],
         viejo='_trae_la_nave(_norm(n.get("nave")), toks)', nuevo='all(t in _norm(n.get("nave")) for t in toks)'),
    dict(id="cosco-calce-sin-el-ayudante", pruebas=[NC + "test_msc_y_cosco_calzan_con_el_ayudante"],
         viejo="    cand = _cosco_calzan(filas, toks_nave, toks_todos)\n",
         nuevo='    cand = [x for x in filas if all(t in (x.get("texto") or "").upper() for t in toks_todos)]\n'),
    dict(id="cosco-calza-sin-nave", pruebas=[NC + "test_cosco_calza_en_una_de_sus_naves"],
         viejo="    if not toks_nave:\n        return []\n", nuevo=""),
    dict(id="cosco-calza-en-toda-la-fila", pruebas=[NC + "test_cosco_calza_en_una_de_sus_naves"],
         viejo='return any(_trae_la_nave(n, palabras) for n in x.get("naves") or [])',
         nuevo='return _trae_la_nave(" ".join(x.get("naves") or []), palabras)'),
    dict(id="cosco-calza-sin-el-viaje", pruebas=[NC + "test_cosco_calza_en_una_de_sus_naves"],
         viejo="return [x for x in filas if _cosco_trae(x, toks_todos)] or [x for x in filas if _cosco_trae(x, toks_nave)]",
         nuevo="return [x for x in filas if _cosco_trae(x, toks_nave)]"),
    dict(id="mk-salidas-en-toda-la-tarjeta", pruebas=[MK + "test_js_salidas_lee_la_salida_y_si_se_puede_reservar"],
         viejo="const t = suNave.toUpperCase()", nuevo="const t = (c.textContent || '').toUpperCase()"),
    dict(id="mk-salidas-otro-campo", pruebas=[MK + "test_js_salidas_lee_la_salida_y_si_se_puede_reservar"],
         viejo="=== 'vessel/voyage') suNave", nuevo="=== 'arrival') suNave"),
]

# --- Encargo 27 · ítem 2: entre salidas del mismo día, la de menor tiempo de tránsito; si siguen empatadas, NO ENVIADA con
# la lista, como antes. Los transbordos no cuentan (CICLO-cola-tres-items.md). ---
PS = "test_ayudantes.TestProximaSalida."
DESEMPATE = PS + "test_desempate_por_el_menor_tiempo_de_transito"
MOTIVO_TT = PS + "test_el_motivo_con_el_tiempo_de_transito"

MUTACIONES += [
    dict(id="proxima-sin-desempate", pruebas=[DESEMPATE, ON + "test_transito_y_desempate", MS + "test_transito_y_desempate",
                                              K1 + "test_transito_y_desempate",
                                              MK + "test_desempata_por_el_menor_tiempo_de_transito"],
         viejo="    if len(del_dia) > 1 and transito:\n        return _menor_transito(del_dia, transito)\n", nuevo=""),
    dict(id="transito-el-mayor", pruebas=[DESEMPATE], viejo="    menor = min(tiempos)\n", nuevo="    menor = max(tiempos)\n"),
    dict(id="transito-elige-en-empate", pruebas=[DESEMPATE],
         viejo='return (las_menores[0], "") if len(las_menores) == 1 else (None, "empate")',
         nuevo='return (las_menores[0], "")'),
    dict(id="transito-sin-mirar-los-ilegibles", pruebas=[DESEMPATE],
         viejo='    if not all(_transito_legible(x) for x in tiempos):\n        return None, "empate"\n', nuevo=""),
    dict(id="transito-de-todas-las-salidas", pruebas=[DESEMPATE],
         viejo="        return _menor_transito(del_dia, transito)\n",
         nuevo="        return _menor_transito([o for _, o in futuras], transito)\n"),
    dict(id="motivo-sin-el-transito", pruebas=[MOTIVO_TT, ON + "test_sin_una_salida_queda_no_enviada_con_evidencia"],
         viejo="        return _por_que_sin_salida(motivo, salidas, desde) + _y_el_transito(salidas, desde, transito)\n",
         nuevo="        return _por_que_sin_salida(motivo, salidas, desde)\n"),
    dict(id="motivo-transito-cuenta-mal-los-ilegibles", pruebas=[MOTIVO_TT],
         viejo="    ilegibles = sum(1 for x in tiempos if not _transito_legible(x))\n",
         nuevo="    ilegibles = sum(1 for x in tiempos if x is None)\n"),
    dict(id="motivo-transito-de-todas-las-salidas", pruebas=[MOTIVO_TT],
         # Anclada con la línea de antes: _anotar_desempate repite la de los tiempos.
         viejo="    fechas = [f for f, _ in salidas if f >= desde]\n    tiempos = [transito(o) for f, o in salidas if f == min(fechas)]\n",
         nuevo="    fechas = [f for f, _ in salidas if f >= desde]\n    tiempos = [transito(o) for f, o in salidas if f is not None]\n"),
    dict(id="texto-transito-sin-horas", pruebas=[MOTIVO_TT],
         viejo='    return texto + (f" y {horas} hora" + ("" if horas == 1 else "s") if horas else "")\n',
         nuevo="    return texto\n"),
    dict(id="texto-transito-sin-singular", pruebas=[MOTIVO_TT],
         viejo='    texto = f"{dias} día" + ("" if dias == 1 else "s")\n', nuevo='    texto = f"{dias} días"\n'),
    dict(id="one-llegada-la-salida", pruebas=[ON + "test_js_tarjetas_de_la_nave_con_su_salida"],
         viejo="llegada: fechas.length === 2 ? fechas[1] : '',", nuevo="llegada: fechas[0] || '',"),
    dict(id="one-llegada-sin-exigir-dos", pruebas=[ON + "test_js_tarjetas_de_la_nave_con_su_salida"],
         viejo="llegada: fechas.length === 2 ?", nuevo="llegada: fechas.length >= 1 ?"),
    dict(id="one-transito-al-reves", pruebas=[ON + "test_transito_y_desempate"],
         viejo="datetime.date.fromisoformat(llegada) - datetime.date.fromisoformat(salida)",
         nuevo="datetime.date.fromisoformat(salida) - datetime.date.fromisoformat(llegada)"),
    dict(id="one-transito-negativo", pruebas=[ON + "test_transito_y_desempate"],
         viejo="        return None\n    return tiempo if tiempo.days > 0 else None\n",
         nuevo="        return None\n    return tiempo\n"),
    dict(id="one-elige-sin-transito", pruebas=[ON + "test_reservar_one_elige_la_proxima_salida"],
         viejo="_proxima_salida(_one_salidas(tarjetas), desde, _one_transito) if tarjetas",
         nuevo="_proxima_salida(_one_salidas(tarjetas), desde) if tarjetas"),
    dict(id="one-sin-una-sin-transito", pruebas=[ON + "test_sin_una_salida_queda_no_enviada_con_evidencia"],
         viejo="_por_que_sin_salida(motivo, _one_salidas(tarjetas), desde, _one_transito)",
         nuevo="_por_que_sin_salida(motivo, _one_salidas(tarjetas), desde)"),
    dict(id="msc-eta-de-la-etd", pruebas=[MS + "test_js_naves_lee_la_etd_y_la_eta"],
         viejo="eta:(etas.length === 1 ? etas[0].slice(4) : '')", nuevo="eta:(e?e[1]:'')"),
    dict(id="msc-transito-negativo", pruebas=[MS + "test_transito_y_desempate"],
         viejo="    if not etd or not eta or eta <= etd:\n", nuevo="    if not etd or not eta:\n"),
    dict(id="msc-elige-sin-transito", pruebas=[MS + "test_transito_y_desempate"],
         viejo="_proxima_salida(_msc_salidas(exacta), desde, _msc_transito)",
         nuevo="_proxima_salida(_msc_salidas(exacta), desde)"),
    dict(id="msc-ambigua-sin-transito", pruebas=[MS + "test_salida_ambigua_queda_no_enviada_con_evidencia"],
         viejo="_por_que_sin_salida(motivo, _msc_salidas(exacta), desde, _msc_transito)",
         nuevo="_por_que_sin_salida(motivo, _msc_salidas(exacta), desde)"),
    dict(id="cosco-transito-sin-guarda", pruebas=[K1 + "test_transito_y_desempate"],
         viejo='    if not llegada or not x.get("etd"):\n        return None\n', nuevo=""),
    dict(id="cosco-transito-negativo", pruebas=[K1 + "test_transito_y_desempate"],
         viejo='x.get("etd"))\n    return tiempo if tiempo.days > 0 else None\n', nuevo='x.get("etd"))\n    return tiempo\n'),
    dict(id="cosco-elige-sin-transito", pruebas=[K1 + "test_transito_y_desempate"],
         viejo="_proxima_salida(_cosco_salidas(cand), _desde(reserva), _cosco_transito)",
         nuevo="_proxima_salida(_cosco_salidas(cand), _desde(reserva))"),
    dict(id="cosco-ambiguo-sin-transito", pruebas=[AMBIGUO_COSCO],
         viejo="_por_que_sin_salida(motivo, _cosco_salidas(cand), _desde(reserva), _cosco_transito)",
         nuevo="_por_que_sin_salida(motivo, _cosco_salidas(cand), _desde(reserva))"),
    dict(id="mk-transito-otra-etiqueta", pruebas=[MK + "test_js_salidas_lee_la_salida_y_si_se_puede_reservar"],
         viejo="=== 'transit time') transito", nuevo="=== 'arrival') transito"),
    dict(id="mk-transito-sin-horas", pruebas=[MK + "test_transito_de_la_salida"],
         viejo="hours=int(m.group(2) or 0)", nuevo="hours=0"),
    dict(id="mk-elige-sin-transito", pruebas=[MK + "test_desempata_por_el_menor_tiempo_de_transito"],
         viejo="_proxima_salida(_mk_salidas(cand), desde, _mk_transito)", nuevo="_proxima_salida(_mk_salidas(cand), desde)"),
    dict(id="mk-sin-una-sin-transito", pruebas=[SIN_UNA_MK],
         viejo="_por_que_sin_salida(motivo, _mk_salidas(salidas), desde, _mk_transito)",
         nuevo="_por_que_sin_salida(motivo, _mk_salidas(salidas), desde)"),
]

# --- Encargo 27 · ítem 2, tras la revisión adversarial: el tránsito de cero o menos no sirve, el log del desempate, MSC
# con una sola ETA, COSCO con exactamente dos fechas, y los casos que la red no fijaba (CICLO-cola-tres-items.md). ---
ANOTA = PS + "test_anota_el_desempate"
ANOTAN = PS + "test_cada_naviera_anota_el_desempate"

MUTACIONES += [
    dict(id="transito-acepta-el-cero", pruebas=[DESEMPATE],
         viejo="    return tiempo is not None and tiempo > datetime.timedelta(0)\n", nuevo="    return tiempo is not None\n"),
    dict(id="motivo-transito-cuenta-las-pasadas", pruebas=[MOTIVO_TT],
         viejo="    fechas = [f for f, _ in salidas if f >= desde]\n    tiempos = [transito(o)",
         nuevo="    fechas = [f for f, _ in salidas]\n    tiempos = [transito(o)"),
    dict(id="anotar-sin-desempate-real", pruebas=[ANOTA],
         viejo="    if len(tiempos) < 2 or not all(_transito_legible(x) for x in tiempos):\n        return\n",
         nuevo="    if not tiempos or None in tiempos:\n        return\n"),
    dict(id="anotar-sin-las-otras", pruebas=[ANOTA],
         viejo=" (las otras: {', '.join(_texto_transito(x) for x in tiempos[1:])})", nuevo=""),
    dict(id="anotar-de-otro-dia", pruebas=[ANOTA],
         viejo="    fechas = [f for f, _ in salidas if f is not None and f >= desde]\n",
         nuevo="    fechas = [f for f, _ in salidas if f is not None]\n"),
    dict(id="one-sin-anotar-el-desempate", pruebas=[ANOTAN],
         viejo="            _anotar_desempate(reg, _one_salidas(tarjetas), desde, _one_transito)\n", nuevo=""),
    dict(id="msc-sin-anotar-el-desempate", pruebas=[ANOTAN],
         viejo="        _anotar_desempate(reg, _msc_salidas(exacta), desde, _msc_transito)\n", nuevo=""),
    dict(id="cosco-sin-anotar-el-desempate", pruebas=[ANOTAN],
         viejo="        _anotar_desempate(reg, _cosco_salidas(cand), _desde(reserva), _cosco_transito)\n", nuevo=""),
    dict(id="mk-sin-anotar-el-desempate", pruebas=[ANOTAN, MK + "test_desempata_por_el_menor_tiempo_de_transito"],
         viejo="                _anotar_desempate(reg, _mk_salidas(cand), desde, _mk_transito)\n", nuevo=""),
    dict(id="one-llegada-con-tres", pruebas=[ON + "test_js_tarjetas_de_la_nave_con_su_salida"],
         viejo="llegada: fechas.length === 2 ?", nuevo="llegada: fechas.length >= 2 ?"),
    dict(id="msc-eta-sin-exigir-una", pruebas=[MS + "test_js_naves_lee_la_etd_y_la_eta"],
         viejo="eta:(etas.length === 1 ?", nuevo="eta:(etas.length >= 1 ?"),
    dict(id="cosco-js-llegada-sin-exigir-dos", pruebas=[K1 + "test_js_lista_lee_la_salida_y_la_llegada_de_la_tarjeta"],
         viejo="llegada: fechas.length===2 ?", nuevo="llegada: fechas.length>=2 ?"),
    dict(id="cosco-transito-cuenta-transbordos", pruebas=[K1 + "test_transito_y_desempate"],
         viejo='    tiempo = llegada - datetime.date.fromisoformat(x.get("etd"))\n',
         nuevo='    tiempo = llegada - datetime.date.fromisoformat(x.get("etd")) + datetime.timedelta(days=30 * len(x.get("naves") '
               'or []))\n'),
    dict(id="mk-transito-acepta-mas", pruebas=[MK + "test_transito_de_la_salida"],
         viejo='fullmatch(r"\\s*(\\d+) days?', nuevo='match(r"\\s*(\\d+) days?'),
    dict(id="one-sin-una-con-otro-transito", pruebas=[ON + "test_sin_una_salida_con_el_mismo_tiempo_de_transito"],
         viejo="_por_que_sin_salida(motivo, _one_salidas(tarjetas), desde, _one_transito)",
         nuevo="_por_que_sin_salida(motivo, _one_salidas(tarjetas), desde, _msc_transito)"),
    dict(id="msc-ambigua-con-otro-transito", pruebas=[MS + "test_salida_ambigua_con_el_mismo_tiempo_de_transito"],
         viejo="_por_que_sin_salida(motivo, _msc_salidas(exacta), desde, _msc_transito)",
         nuevo="_por_que_sin_salida(motivo, _msc_salidas(exacta), desde, _one_transito)"),
    dict(id="cosco-ambiguo-con-otro-transito", pruebas=[AMBIGUO_COSCO],
         viejo="_por_que_sin_salida(motivo, _cosco_salidas(cand), _desde(reserva), _cosco_transito)",
         nuevo="_por_que_sin_salida(motivo, _cosco_salidas(cand), _desde(reserva), _msc_transito)"),
    dict(id="mk-sin-una-con-otro-transito", pruebas=[MK + "test_sin_una_salida_con_el_mismo_tiempo_de_transito"],
         viejo="_por_que_sin_salida(motivo, _mk_salidas(salidas), desde, _mk_transito)",
         nuevo="_por_que_sin_salida(motivo, _mk_salidas(salidas), desde, _one_transito)"),
]

# --- Encargo 27 · ítem 3: CMA deja la evidencia de la pantalla al terminar la espera de «Validar ruta», después de leer
# su aviso (CICLO-cola-tres-items.md). ---
VR = "test_evidencia.TestEvidenciaValidarRutaCma."
EV_VR = '        _evidencia_antes_de_la_guarda(page, reg, f"cma_f{f}_validar_{modo}", "tras «Validar ruta»", completa=False)\n'
COMENTARIO_VR = ("        # Lo que dejó «Validar ruta» al terminar la espera que ya existe, respondiera o no el portal: la captura de la\n"
                 "        # ventana y el HTML, sin clics, teclas, esperas ni navegación. Va después de leer el aviso, para que esa lectura,\n"
                 "        # que decide el camino, siga en el mismo instante (decisión de Marcelo, CICLO-cola-tres-items.md).\n")

MUTACIONES += [
    dict(id="cma-validar-sin-evidencia",
         pruebas=[VR + "test_va_al_terminar_la_espera_y_tras_leer_el_aviso", VR + "test_la_ventana_y_el_html_sin_clics",
                  LD + "test_solo_ahi"],
         viejo=EV_VR, nuevo=""),
    dict(id="cma-validar-pagina-completa", pruebas=[VR + "test_la_ventana_y_el_html_sin_clics"],
         viejo=EV_VR, nuevo=EV_VR.replace("completa=False", "completa=True")),
    # Sin el modo: los dos intentos se pisarían. Conserva «_validar_», para que la prueba siga viendo la llamada.
    dict(id="cma-validar-un-solo-nombre", pruebas=[VR + "test_la_ventana_y_el_html_sin_clics"],
         viejo='f"cma_f{f}_validar_{modo}"', nuevo='f"cma_f{f}_validar_"'),
    dict(id="cma-validar-otro-momento", pruebas=[VR + "test_si_la_evidencia_falla_sigue_igual"],
         viejo='"tras «Validar ruta»", completa=False', nuevo='"en la lista de rutas", completa=False'),
    # La evidencia antes de leer el aviso (movida, no repetida): esa lectura, que decide el camino, se correría.
    dict(id="cma-validar-antes-del-aviso", pruebas=[VR + "test_va_al_terminar_la_espera_y_tras_leer_el_aviso"],
         viejo="        ultimo_aviso = _cma_aviso(page)\n" + COMENTARIO_VR + EV_VR,
         nuevo=COMENTARIO_VR + EV_VR + "        ultimo_aviso = _cma_aviso(page)\n"),
    # Con un mecanismo que corta si falla: la reserva no seguiría.
    dict(id="cma-validar-evidencia-sin-proteger", pruebas=[VR + "test_si_la_evidencia_falla_sigue_igual"],
         viejo=EV_VR, nuevo='        _guardar_evidencia(page, reg, f"cma_f{f}_validar_{modo}")\n'),
    dict(id="cma-validar-con-una-espera", pruebas=[VR + "test_va_al_terminar_la_espera_y_tras_leer_el_aviso"],
         viejo=EV_VR, nuevo=EV_VR + "        esperar(page, 1.0)\n"),
]

# --- Encargo 28 · ítem 1: una fila sin nave (vacía o con un comodín) queda NO ENVIADA sin abrir el portal; una sola
# lista de comodines para las seis navieras (CICLO-solo-la-nave-pedida.md). ---
FSN = "test_ayudantes.TestFilaSinNave."
SIN_NAVE_WEB = CO + "test_fila_sin_nave_no_abre_el_portal"
SIN_NAVE_CONSOLA = ER + "test_fila_sin_nave_no_abre_el_portal"
REGLA_SIN_NAVE = ('    return "COMPLETAR" in t or _fila_manual(t) or all(p in NAVES_COMODIN or p in NAVES_PREFIJO for p '
                  'in palabras)\n')
DECORADOR_SIN_NAVE = ('        if _fila_sin_nave((reserva or {}).get("nave")):\n'
                      '            return _sin_nave(reg, (reserva or {}).get("fila"), (reserva or {}).get("nave"))\n')

MUTACIONES += [
    dict(id="sin-nave-sin-comodines", pruebas=[FSN + "test_fila_sin_nave", SIN_NAVE_WEB, SIN_NAVE_CONSOLA],
         viejo=REGLA_SIN_NAVE, nuevo='    return "COMPLETAR" in t or _fila_manual(t) or not palabras\n'),
    dict(id="sin-nave-sin-completar", pruebas=[FSN + "test_fila_sin_nave", FSN + "test_ningun_reservador_abre_el_portal_sin_nave"],
         viejo=REGLA_SIN_NAVE, nuevo="    return _fila_manual(t) or all(p in NAVES_COMODIN or p in NAVES_PREFIJO for p in palabras)\n"),
    dict(id="sin-nave-basta-un-comodin", pruebas=[FSN + "test_fila_sin_nave"],
         viejo=REGLA_SIN_NAVE,
         nuevo='    return "COMPLETAR" in t or _fila_manual(t) or any(p in NAVES_COMODIN for p in palabras) '
               'or all(p in NAVES_COMODIN or p in NAVES_PREFIJO for p in palabras)\n'),
    # Las palabras separadas solo por espacios, con sus signos: «AUTO.» o «(AUTO)» pedirían una nave.
    dict(id="sin-nave-cuenta-los-signos", pruebas=[FSN + "test_fila_sin_nave"],
         viejo='    palabras = _re_mk.findall(r"[0-9A-ZÑÁÉÍÓÚÜ]{2,}", t)\n', nuevo="    palabras = t.split()\n"),
    # Las de una letra cuentan: «AUTO X» o «X» pedirían una nave, aunque ninguna naviera las busca.
    dict(id="sin-nave-cuenta-una-letra", pruebas=[FSN + "test_fila_sin_nave"],
         viejo='    palabras = _re_mk.findall(r"[0-9A-ZÑÁÉÍÓÚÜ]{2,}", t)\n',
         nuevo='    palabras = _re_mk.findall(r"[0-9A-ZÑÁÉÍÓÚÜ]{1,}", t)\n'),
    dict(id="sin-nave-con-mayusculas", pruebas=[FSN + "test_fila_sin_nave"],
         viejo='    t = str(nave or "").upper()\n    palabras = _re_mk', nuevo='    t = str(nave or "")\n    palabras = _re_mk'),
    dict(id="comodines-sin-los-de-hyundai", pruebas=[FSN + "test_fila_sin_nave", SIN_NAVE_WEB],
         viejo='"NONE", "PRIMERA", "DISPONIBLE")', nuevo='"NONE")'),
    dict(id="comodines-sin-los-de-cma", pruebas=[FSN + "test_fila_sin_nave"],
         viejo='"LIBRE", "NINGUNA", "NONE"', nuevo='"LIBRE"'),
    dict(id="sin-nave-otro-motivo", pruebas=[FSN + "test_fila_sin_nave", FSN + "test_ningun_reservador_abre_el_portal_sin_nave",
                                             SIN_NAVE_WEB, SIN_NAVE_CONSOLA],
         viejo='FILA_SIN_NAVE = "la fila no trae una nave para reservar"', nuevo='FILA_SIN_NAVE = "sin nave"'),
    dict(id="sin-nave-sin-aviso", pruebas=[FSN + "test_ningun_reservador_abre_el_portal_sin_nave", SIN_NAVE_WEB,
                                           SIN_NAVE_CONSOLA],
         viejo='    reg.paso(f"✗ fila {fila}: {NO_ENVIADA} · {FILA_SIN_NAVE}. No entro al portal por ella: escribe la nave en la "\n'
               '             f"planilla y vuelve a armar la reserva.")\n', nuevo=""),
    # El estado de antes, OMITIDO, en lugar de NO ENVIADA.
    dict(id="sin-nave-omitida", pruebas=[FSN + "test_ningun_reservador_abre_el_portal_sin_nave", SIN_NAVE_WEB, SIN_NAVE_CONSOLA],
         viejo="    return (NO_ENVIADA, FILA_SIN_NAVE)\n", nuevo='    return ("OMITIDO", FILA_SIN_NAVE)\n'),
    dict(id="sin-nave-el-decorador-deja-pasar", pruebas=[FSN + "test_ningun_reservador_abre_el_portal_sin_nave"],
         viejo=DECORADOR_SIN_NAVE, nuevo=""),
] + [
    dict(id=f"sin-nave-{nav}-sin-decorador", pruebas=[FSN + "test_ningun_reservador_abre_el_portal_sin_nave",
                                             SC + "test_cada_reservador_que_corta_esta_decorado"],
         viejo=f'@_con_la_nave_de_la_fila\n@_con_la_ruta_de_la_fila\n@_sin_clic_a_ciegas("{pref}")\n',
         nuevo=f'@_con_la_ruta_de_la_fila\n@_sin_clic_a_ciegas("{pref}")\n')
    for nav, pref in (("one", "one"), ("msc", "msc"), ("cosco", "cosco"), ("hyundai", "hmm"), ("maersk", "mk"), ("cma", "cma"))
] + [
    # CMA con su propia lista, como hasta a198645.
    dict(id="sin-nave-cma-con-su-lista", pruebas=[FSN + "test_una_sola_regla"],
         viejo="    nave_especificada = not _fila_sin_nave(nave_pedida)",
         nuevo='    nave_especificada = bool(nave_pedida and nave_pedida.upper() not in ("AUTO", "CUALQUIERA", "LIBRE", "N/A", '
               '"NINGUNA", "-", "NONE"))'),
    # HYUNDAI con su propia regla, como hasta a198645 (queda detrás del decorador, pero es otra regla).
    dict(id="sin-nave-hyundai-con-su-regla", pruebas=[FSN + "test_una_sola_regla"],
         viejo='    nave_pedida = (reserva.get("nave") or "").strip()\n',
         nuevo='    nave_pedida = (reserva.get("nave") or "").strip()\n    if not nave_pedida or "completar" in nave_pedida.lower():\n'
               '        return ("OMITIDO", "sin nave en planilla")\n'),
    # El panel web: la fila sin nave va al portal, se abre el navegador sin filas, no queda el resultado, o solo mira la
    # celda vacía (no los comodines).
    dict(id="sin-nave-web-va-al-portal", pruebas=[SIN_NAVE_WEB],
         viejo='            sub_elegidas = [f for f in sub_elegidas if not _fila_sin_nave(f.get("nave"))]\n', nuevo=""),
    dict(id="sin-nave-web-abre-el-navegador", pruebas=[SIN_NAVE_WEB],
         viejo="            if not sub_elegidas:\n                reg.paso(f\"Ninguna fila de {nombre} trae una nave",
         nuevo="            if False:\n                reg.paso(f\"Ninguna fila de {nombre} trae una nave"),
    dict(id="sin-nave-web-sin-resultado", pruebas=[SIN_NAVE_WEB],
         viejo='_sin_nave(reg, rsv["fila"], rsv.get("nave"))\n                with _LOCK:\n'
               '                    _WEB["resultados"][str(rsv["fila"])] = {\n',
         nuevo='_sin_nave(reg, rsv["fila"], rsv.get("nave"))\n                with _LOCK:\n'
               '                    _ = {\n'),
    dict(id="sin-nave-web-solo-la-vacia", pruebas=[SIN_NAVE_WEB], cambios=[
        ('            for rsv in [f for f in sub_elegidas if _fila_sin_nave(f.get("nave"))]:\n',
         '            for rsv in [f for f in sub_elegidas if not f.get("nave")]:\n'),
        ('            sub_elegidas = [f for f in sub_elegidas if not _fila_sin_nave(f.get("nave"))]\n',
         '            sub_elegidas = [f for f in sub_elegidas if f.get("nave")]\n')]),
    # La consola: la fila sin nave no queda en la planilla, va al portal, se abre el navegador sin filas, o sin resumen.
    dict(id="sin-nave-consola-no-anota", pruebas=[SIN_NAVE_CONSOLA],
         viejo='            anotar(i, rsv, *_sin_nave(reg, rsv["fila"], rsv["nave"]))\n', nuevo="            pass\n"),
    dict(id="sin-nave-consola-va-al-portal", pruebas=[SIN_NAVE_CONSOLA],
         viejo='    con_nave = [(i, rsv) for i, rsv in numeradas if not _fila_sin_nave(rsv["nave"])]\n',
         nuevo="    con_nave = list(numeradas)\n"),
    dict(id="sin-nave-consola-abre-el-navegador", pruebas=[SIN_NAVE_CONSOLA],
         viejo="    if not con_nave:\n        reg.paso(f\"Ninguna fila de {nombre} trae una nave",
         nuevo="    if False:\n        reg.paso(f\"Ninguna fila de {nombre} trae una nave"),
    dict(id="sin-nave-consola-sin-resumen", pruebas=[SIN_NAVE_CONSOLA],
         viejo='trae una nave para reservar: no abro el navegador ni entro al portal.")\n        resumen()\n',
         nuevo='trae una nave para reservar: no abro el navegador ni entro al portal.")\n'),
]

# --- Encargo 28 · ítem 1, tras la revisión: el decorador deja pasar la fila con nave tal cual, la consola respeta
# AQUASHIELD_SOLO_PRIMERA y el orden de la hoja, el panel web marca y cuenta con la regla del programa, CONSOLIDADO marca
# cada fila una sola vez, y HYUNDAI ya no quita sus comodines. ---
SIN_NAVE_CONSOLA_2 = ER + "test_fila_sin_nave_con_login_fallido_o_solo_la_primera"
SIN_NAVE_CONSOLIDADO = CO + "test_fila_sin_nave_en_consolidado"
PANEL_MARCA = "test_envio.TestLecturaDelPanel.test_marca_por_defecto_tambien_las_filas_sin_nave"
MARCA = "    return dict(fila, sin_nave=_fila_sin_nave(nave) and not _fila_manual(nave), manual=_fila_manual(nave),\n"
PASA_EL_DECORADOR = ('            return _sin_nave(reg, (reserva or {}).get("fila"), (reserva or {}).get("nave"))\n'
                     '        return reservar(page, reserva, creds, reg, on_pausa=on_pausa)\n')

MUTACIONES += [
    # El decorador corta toda fila (lee otra llave) o la deja pasar sin on_pausa, o sin su nombre.
    dict(id="sin-nave-decorador-corta-todo", pruebas=[FSN + "test_con_nave_pasa_igual"],
         viejo='        if _fila_sin_nave((reserva or {}).get("nave")):\n            return _sin_nave(',
         nuevo='        if _fila_sin_nave((reserva or {}).get("Nave")):\n            return _sin_nave('),
    dict(id="sin-nave-decorador-sin-on-pausa", pruebas=[FSN + "test_con_nave_pasa_igual"],
         viejo=PASA_EL_DECORADOR, nuevo=PASA_EL_DECORADOR.replace(", on_pausa=on_pausa)", ")")),
    dict(id="sin-nave-decorador-sin-nombre", pruebas=[FSN + "test_con_nave_pasa_igual"],
         viejo="    reservar_con_la_nave.__name__ = reservar.__name__\n", nuevo=""),
    # La consola: con AQUASHIELD_SOLO_PRIMERA escribe todas las filas sin nave; el resumen, en el orden de las anotaciones.
    dict(id="sin-nave-consola-solo-primera-toca-todas", pruebas=[SIN_NAVE_CONSOLA_2],
         viejo="        numeradas = numeradas[:1]\n", nuevo=""),
    dict(id="sin-nave-consola-resumen-desordenado", pruebas=[SIN_NAVE_CONSOLA],
         viejo="        resultados.clear()\n        resultados.update(orden)\n", nuevo=""),
    # La consola, con el login fallido: la fila sin nave no queda en la planilla (se anotaría después del login).
    dict(id="sin-nave-consola-despues-del-login", pruebas=[SIN_NAVE_CONSOLA_2], cambios=[
        ('            anotar(i, rsv, *_sin_nave(reg, rsv["fila"], rsv["nave"]))\n', "            pass\n"),
        ('            for i, rsv in con_nave:\n',
         '            for i, rsv in numeradas:\n                if _fila_sin_nave(rsv["nave"]):\n'
         '                    anotar(i, rsv, *_sin_nave(reg, rsv["fila"], rsv["nave"]))\n            for i, rsv in con_nave:\n')]),
    # ERROR con «SIN EMITIR»: la prueba volvió a tener su fila ERROR (la 10, con una nave).
    dict(id="consola-error-con-sin-emitir", pruebas=[ER + "test_sin_emitir_solo_si_volvio_sin_emitir"],
         viejo=COLA_SIN_EMITIR, nuevo='cola = " · SIN EMITIR" if estado in ("OK-EJEMPLO", "ERROR") else ""'),
    # El panel web: en CONSOLIDADO marca las filas sin nave de todas las navieras en cada vuelta.
    dict(id="sin-nave-web-marca-en-cada-naviera", pruebas=[SIN_NAVE_CONSOLIDADO],
         viejo='            for rsv in [f for f in sub_elegidas if _fila_sin_nave(f.get("nave"))]:\n',
         nuevo='            for rsv in [f for f in elegidas if _fila_sin_nave(f.get("nave"))]:\n'),
    # /api/filas sin la marca, o con la celda vacía en vez de la regla.
    dict(id="filas-sin-la-marca", pruebas=[CO + "test_filas_dicen_si_traen_nave"],
         viejo=MARCA, nuevo="    return dict(fila, manual=_fila_manual(nave),\n"),
    dict(id="filas-con-la-celda-vacia", pruebas=[CO + "test_filas_dicen_si_traen_nave"],
         viejo=MARCA, nuevo="    return dict(fila, sin_nave=not nave, manual=_fila_manual(nave),\n"),
    # El panel: como hasta a198645, la fila vacía sin marcar, o con MANUAL marcada; la tabla, «Todas», la etiqueta y el
    # aviso con su propia regla.
    dict(id="panel-no-marca-las-vacias", pruebas=[PANEL_MARCA],
         viejo="  return !f.manual;\n", nuevo="  return !!f.nave && !f.manual;\n"),
    dict(id="panel-marca-manual", pruebas=[PANEL_MARCA],
         viejo="  return !f.manual;\n", nuevo="  return true;\n"),
    dict(id="panel-tabla-con-otra-regla", pruebas=[PANEL_MARCA],
         viejo='const chk = marcadaPorDefecto(f) ? "checked" : "";',
         nuevo='const chk = f.nave && marcadaPorDefecto(f) ? "checked" : "";'),
    dict(id="panel-todas-con-otra-regla", pruebas=[PANEL_MARCA],
         viejo="c.checked = marcadaPorDefecto(FILAS[i]);", nuevo="c.checked = !!FILAS[i].nave && marcadaPorDefecto(FILAS[i]);"),
    dict(id="panel-cuenta-las-vacias", pruebas=[PANEL_MARCA],
         viejo="const sin = FILAS.filter(f => f.sin_nave).length;", nuevo="const sin = FILAS.filter(f => !f.nave).length;"),
    dict(id="panel-etiqueta-de-la-vacia", pruebas=[PANEL_MARCA],
         viejo="${f.sin_nave ? \"<span class='sin-nave'>sin nave</span> \" + esc(f.nave) : esc(f.nave)}",
         nuevo="${esc(f.nave) || \"<span class='sin-nave'>sin nave</span>\"}"),
    dict(id="panel-aviso-se-omiten", pruebas=[PANEL_MARCA],
         viejo='" reserva(s) no traen una nave para reservar: quedan NO ENVIADA, sin entrar al portal. "',
         nuevo='" reserva(s) sin nave: esas se omiten "'),
    # HYUNDAI vuelve a quitar sus comodines de la nave antes de calzar.
    dict(id="hmm-vuelve-sus-comodines", pruebas=[TH + "test_js_nave_con_todas_sus_palabras", FSN + "test_una_sola_regla"],
         viejo="    const T = (toks || []).map(s => s.toUpperCase()).filter(s => s.length > 1);\n",
         nuevo="    const ignore = ['AUTO', 'PRIMERA', 'DISPONIBLE', 'CUALQUIERA'];\n"
               "    const T = (toks || []).map(s => s.toUpperCase()).filter(s => !ignore.includes(s) && s.length > 1);\n"),
]

# --- Encargo 28 · ítem 2: ningún atajo reserva una salida sin calzar la nave de la fila (CICLO-solo-la-nave-pedida.md).
# Cada mutación vuelve a poner el atajo como era hasta a198645. ---
T_HMM = "    const T = (toks || []).map(s => s.toUpperCase()).filter(s => s.length > 1);\n"
VESSEL_INFO = "    if (/passed the cut-off date|select a new vessel/i.test(text)) return 'vessel-info';\n"
VESSEL_INFO_HASTA_A198645 = (
    "    if (/passed the cut-off date|select a new vessel/i.test(text)) {\n"
    "        const btn = [...dlg.querySelectorAll('button')].find(b => /^\\\\s*(cancel|cancelar|next|siguiente|close|cerrar)"
    "\\\\s*$/i.test(b.textContent.trim()));\n"
    "        if (btn) { btn.click(); return 'vessel-info-dismiss'; }\n"
    "    }\n")
CARTA_MK = '        cand = [s for s in de_la_nave if s.get("book") == 1]\n'

MUTACIONES += [
    # MAERSK con AQUASHIELD_PRIMERA_NAVE: la primera salida que se puede reservar, fuera la nave que fuera.
    dict(id="mk-vuelve-la-primera-nave", pruebas=[ELIGE_MK],
         viejo='                     f"reservarlas")\n        if cand:\n',
         nuevo='                     f"reservarlas")\n        if not cand and os.environ.get("AQUASHIELD_PRIMERA_NAVE"):\n'
               '            cand = [s for s in salidas if s.get("book") == 1][:1]\n        if cand:\n'),
    # HYUNDAI con su lista «ignore», la que quedó tras el ítem 1: «HMM NW2» calzaba con cualquier nave HMM.
    dict(id="hmm-vuelve-la-lista-ignore", pruebas=[TH + "test_js_nave_con_todas_sus_palabras"],
         viejo=T_HMM, nuevo="    const ignore = ['NW2', 'VIAJE', 'V.', 'VOY'];\n"
                            "    const T = (toks || []).map(s => s.toUpperCase()).filter(s => !ignore.includes(s) && s.length > 1);\n"),
    dict(id="hmm-vuelve-la-lista-ignore-sin-nw2", pruebas=[TH + "test_js_nave_con_todas_sus_palabras"],
         viejo=T_HMM, nuevo="    const ignore = ['VIAJE', 'V.', 'VOY'];\n"
                            "    const T = (toks || []).map(s => s.toUpperCase()).filter(s => !ignore.includes(s) && s.length > 1);\n"),
    # ONE pulsa «Next» en «Vessel Information», en cada uno de los dos lugares que cierran ese diálogo.
    dict(id="one-vessel-info-pulsa-next", pruebas=[O1 + "test_js_vessel_information_nunca_next"],
         viejo=VESSEL_INFO, nuevo=VESSEL_INFO_HASTA_A198645),
    # ONE cierra «Vessel Information» con «Cancel» y sigue.
    dict(id="one-vessel-info-cierra", pruebas=[O1 + "test_js_vessel_information_nunca_next"],
         viejo=VESSEL_INFO, nuevo=VESSEL_INFO_HASTA_A198645.replace("cancel|cancelar|next|siguiente|close|cerrar",
                                                                    "cancel|cancelar|close|cerrar")),
    dict(id="one-vessel-info-sigue", pruebas=[O1 + "test_vessel_information_corta_antes_de_la_guarda"],
         viejo='            if antes_de_la_guarda:\n                raise ObjetivoNoEncontrado("«Vessel Information» de ONE"',
         nuevo='            if False:\n                raise ObjetivoNoEncontrado("«Vessel Information» de ONE"'),
    dict(id="one-clic-tarjeta-pulsa-siguiente", pruebas=[ON + "test_js_clic_solo_el_boton_de_la_tarjeta_elegida"],
         viejo="const dBtn = [...dlg.querySelectorAll('button')].find(b => /^\\\\s*(cancel|cancelar|close|cerrar)",
         nuevo="const dBtn = [...dlg.querySelectorAll('button')].find(b => /^\\\\s*(cancel|cancelar|siguiente|close|cerrar)"),
    dict(id="one-clic-tarjeta-pulsa-next", pruebas=[ON + "test_js_clic_solo_el_boton_de_la_tarjeta_elegida"],
         viejo="const dBtn = [...dlg.querySelectorAll('button')].find(b => /^\\\\s*(cancel|cancelar|close|cerrar)",
         nuevo="const dBtn = [...dlg.querySelectorAll('button')].find(b => /^\\\\s*(cancel|cancelar|next|siguiente|close|cerrar)"),
    # MSC compara con los primeros 40 caracteres de la tarjeta si no lee «Vessel / Voyage».
    dict(id="msc-nave-del-texto-de-la-tarjeta", pruebas=[MS + "test_js_naves_lee_la_etd_y_la_eta"],
         viejo="nave:(m?m[1]:'').trim()", nuevo="nave:(m?m[1]:t.slice(0,40)).trim()"),
    # COSCO lee el octavo ancestro sin comprobar que sea la fila.
    dict(id="cosco-fila-con-otros-botones", pruebas=[K1 + "test_js_lista_lee_la_salida_y_la_llegada_de_la_tarjeta"],
         viejo="{ hallada=btns.filter(x=>row.contains(x)).length===1; break; }", nuevo="{ hallada=true; break; }"),
    dict(id="cosco-fila-sin-comprobar", pruebas=[K1 + "test_js_lista_lee_la_salida_y_la_llegada_de_la_tarjeta"],
         viejo="        if(!hallada) row=null;\n", nuevo=""),
]

# --- Encargo 28 · ítem 3: HYUNDAI no pulsa nada en el modal «Alternate Vessel Option»: deja la captura y el HTML, y la
# reserva queda NO ENVIADA con el motivo (CICLO-solo-la-nave-pedida.md). ---
# Desde el encargo 32 marca «I do not want to choose an alternate vessel» y pulsa OK (CICLO-ampliar-la-busqueda.md):
# estas mutaciones son las de _hmm_mantener_nave.
ON3 = "test_evidencia.TestModalHyundai."
EV_OTRA = ('    _evidencia_antes_de_la_guarda(page, reg, f"hmm_f{f}_otra_nave", "con el modal «Alternate Vessel Option»",\n'
           '                                  completa=False)\n')
MIRA_OTRA = '        visible = page.locator("#vesselOptionSubmit").first.is_visible(timeout=3000)\n'
CORTE_ELEGIR = "    esperar(page, 1.5)\n    modal = _hmm_mantener_nave(page, reg, f)\n    if isinstance(modal, tuple):\n        return modal\n"
MARCA_HMM = ON3 + "test_marca_mantener_la_nave_y_pulsa_ok"

MUTACIONES += [
    # La opción: sin marcarla; otra opción; con otro texto que la contenga; sin ella, sigue; con otro motivo.
    dict(id="hmm-modal-ok-sin-marcar", pruebas=[MARCA_HMM], viejo="    opcion.first.click(timeout=4000)\n", nuevo=""),
    dict(id="hmm-modal-marca-any", pruebas=[MARCA_HMM],
         viejo="_re_mk.escape(HMM_OPCION_MANTENER)", nuevo='_re_mk.escape("Book on next Available Vessel. (Any)")'),
    dict(id="hmm-modal-texto-como-parte", pruebas=[ON3 + "test_sin_la_opcion_no_pulsa_y_no_envia"],
         viejo='has_text=_re_mk.compile(r"^\\s*" + _re_mk.escape(HMM_OPCION_MANTENER) + r"\\s*$"))',
         nuevo="has_text=_re_mk.compile(_re_mk.escape(HMM_OPCION_MANTENER)))"),
    dict(id="hmm-modal-sin-opcion-sigue", pruebas=[ON3 + "test_sin_la_opcion_no_pulsa_y_no_envia"],
         viejo="    if opcion.count() != 1:\n        return _no_enviada(reg, HMM_SIN_OPCION)\n",
         nuevo="    if opcion.count() != 1:\n        return None\n"),
    dict(id="hmm-modal-otro-motivo", pruebas=[ON3 + "test_sin_la_opcion_no_pulsa_y_no_envia"],
         viejo='HMM_SIN_OPCION = "HYUNDAI no ofreció la opción de mantener la nave pedida; la reserva no se envió"',
         nuevo='HMM_SIN_OPCION = "HYUNDAI no ofreció la opción"'),
    # Sin verificar que quedó marcada; el OK sin su texto.
    dict(id="hmm-modal-sin-verificar-la-marca", pruebas=[ON3 + "test_si_el_clic_no_la_marca_o_no_hay_ok"],
         viejo='    if not opcion.first.locator("input[type=radio]").is_checked():\n', nuevo="    if False:\n"),
    dict(id="hmm-modal-ok-sin-su-texto", pruebas=[ON3 + "test_si_el_clic_no_la_marca_o_no_hay_ok"],
         viejo='.filter(has_text=_re_mk.compile(r"^\\s*OK\\s*$"))', nuevo=""),
    # Después del OK, con el modal todavía a la vista: vuelve a marcar y pulsar; o sigue sin cortar; u otro motivo.
    dict(id="hmm-modal-ya-pulsa-otra-vez", pruebas=[ON3 + "test_si_el_modal_sigue_despues_del_ok_no_pulsa_mas"],
         viejo="    if ya:\n", nuevo="    if False:\n"),
    dict(id="hmm-modal-ya-sigue", pruebas=[ON3 + "test_si_el_modal_sigue_despues_del_ok_no_pulsa_mas"],
         viejo="        return _no_enviada(reg, HMM_NO_AVANZO)\n", nuevo="        return None\n"),
    dict(id="hmm-modal-ya-otro-motivo", pruebas=[ON3 + "test_si_el_modal_sigue_despues_del_ok_no_pulsa_mas"],
         viejo='"choose an alternate vessel» y pulsar OK; no pulsé nada más y la reserva no se envió")',
         nuevo='"choose an alternate vessel» y pulsar OK")'),
    # La evidencia: sin ella; de la página completa; con un mecanismo que corta si falla; sin el aviso en pantalla.
    dict(id="hmm-modal-sin-evidencia", pruebas=[MARCA_HMM, LD + "test_solo_ahi"], viejo=EV_OTRA, nuevo=""),
    dict(id="hmm-modal-pagina-completa", pruebas=[MARCA_HMM],
         viejo=EV_OTRA, nuevo=EV_OTRA.replace("completa=False", "completa=True")),
    dict(id="hmm-modal-evidencia-sin-proteger", pruebas=[ON3 + "test_si_la_evidencia_falla_igual_marca"],
         viejo=EV_OTRA, nuevo='    _guardar_evidencia(page, reg, f"hmm_f{f}_otra_nave")\n'),
    dict(id="hmm-modal-sin-aviso", pruebas=[MARCA_HMM],
         viejo='    reg.paso("HYUNDAI mostró el modal «Alternate Vessel Option»: marco que no quiero otra nave y pulso OK.")\n',
         nuevo=""),
    # No lo mira; corta sin modal; corta si no pudo mirarlo.
    dict(id="hmm-modal-no-mira", pruebas=[MARCA_HMM], viejo=MIRA_OTRA, nuevo="        visible = False\n"),
    dict(id="hmm-modal-corta-sin-modal", pruebas=[ON3 + "test_sin_el_modal_sigue_sin_evidencia"],
         viejo="        reg.info(\"modal 'Alternate Vessel Option': no apareció\")\n        return None\n",
         nuevo="        reg.info(\"modal 'Alternate Vessel Option': no apareció\")\n        return _no_enviada(reg, \"x\")\n"),
    dict(id="hmm-modal-corta-si-no-mira", pruebas=[ON3 + "test_sin_el_modal_sigue_sin_evidencia"],
         viejo="no pude mirarlo ({str(e)[:50]})\")\n        return None\n",
         nuevo="no pude mirarlo ({str(e)[:50]})\")\n        return _no_enviada(reg, \"x\")\n"),
    # El reservador: mira antes de la espera; sigue sin cortar; la segunda vez no sabe si ya marcó.
    dict(id="hmm-modal-mira-antes-de-esperar", pruebas=[ON3 + "test_los_lugares_en_el_reservador"],
         viejo=CORTE_ELEGIR,
         nuevo="    modal = _hmm_mantener_nave(page, reg, f)\n    if isinstance(modal, tuple):\n        return modal\n"
               "    esperar(page, 1.5)\n"),
    dict(id="hmm-modal-sigue-tras-elegir", pruebas=[ON3 + "test_los_lugares_en_el_reservador"],
         viejo=CORTE_ELEGIR, nuevo="    esperar(page, 1.5)\n    modal = _hmm_mantener_nave(page, reg, f)\n"),
    dict(id="hmm-modal-segunda-sin-saber", pruebas=[ON3 + "test_los_lugares_en_el_reservador"],
         viejo='        modal = _hmm_mantener_nave(page, reg, f, ya=modal == "marcada")\n',
         nuevo="        modal = _hmm_mantener_nave(page, reg, f)\n"),
    # La tercera mirada (revisión del encargo 32): no está; no sabe que ya marcó; se mira aunque no haya marcado.
    dict(id="hmm-modal-sin-la-tercera", pruebas=[ON3 + "test_los_lugares_en_el_reservador"],
         viejo='        if not ok_step3 and modal == "marcada":\n            modal = _hmm_mantener_nave(page, reg, f, ya=True)\n'
               '            if isinstance(modal, tuple):\n                return modal\n', nuevo=""),
    dict(id="hmm-modal-tercera-sin-saber", pruebas=[ON3 + "test_los_lugares_en_el_reservador"],
         viejo="            modal = _hmm_mantener_nave(page, reg, f, ya=True)\n",
         nuevo="            modal = _hmm_mantener_nave(page, reg, f)\n"),
    dict(id="hmm-modal-tercera-siempre", pruebas=[ON3 + "test_los_lugares_en_el_reservador"],
         viejo='        if not ok_step3 and modal == "marcada":\n', nuevo="        if not ok_step3:\n"),
]

# --- Encargo 29 · ítem 1: una fila con solo el prefijo de la naviera («MSC», «HMM», «CMA-CGM»…), solo o con comodines,
# queda NO ENVIADA como fila sin nave (CICLO-cola-seis-items.md). ---
PREFIJOS = 'NAVES_PREFIJO = ("MSC", "CMA", "CGM", "HMM", "ONE", "COSCO", "MV", "HYUNDAI", "MAERSK", "CSCL", "SHIPPING")\n'

MUTACIONES += [
    # Los prefijos no cuentan, como hasta f68ce6c: «MSC» pide una nave y calza con toda nave cuyo campo trae «MSC».
    dict(id="sin-nave-sin-prefijos", pruebas=[FSN + "test_fila_sin_nave", FSN + "test_ningun_reservador_abre_el_portal_sin_nave",
                                             SIN_NAVE_CONSOLA, CO + "test_fila_con_solo_el_prefijo_no_abre_el_portal"],
         viejo=REGLA_SIN_NAVE, nuevo='    return "COMPLETAR" in t or _fila_manual(t) or all(p in NAVES_COMODIN for p in palabras)\n'),
    # Basta un prefijo: «MSC NAVE» ya no pediría su nave.
    dict(id="sin-nave-basta-un-prefijo", pruebas=[FSN + "test_fila_sin_nave"],
         viejo=REGLA_SIN_NAVE,
         nuevo='    return "COMPLETAR" in t or _fila_manual(t) or all(p in NAVES_COMODIN for p in palabras) '
               'or any(p in NAVES_PREFIJO for p in palabras)\n'),
    # Sin uno de los prefijos medidos: el de HYUNDAI, o los nombres de HOJA_ALIAS.
    dict(id="prefijos-sin-hmm", pruebas=[FSN + "test_fila_sin_nave", FSN + "test_ningun_reservador_abre_el_portal_sin_nave"],
         viejo=PREFIJOS, nuevo=PREFIJOS.replace('"HMM", ', "")),
    dict(id="prefijos-sin-los-de-hoja-alias", pruebas=[FSN + "test_fila_sin_nave"],
         viejo=PREFIJOS, nuevo=PREFIJOS.replace(', "HYUNDAI", "MAERSK"', "")),
]

# --- Encargo 29 · ítem 2: la nave calza por palabra entera, sin distinguir mayúsculas, en las seis navieras, con un solo
# ayudante: _trae_la_nave en Python (MSC y COSCO) y _JS_TRAE_LA_NAVE en el JavaScript de ONE, HYUNDAI, MAERSK y CMA
# (CICLO-cola-seis-items.md). Hasta f68ce6c bastaba que cada palabra fuera parte del texto. ---
MISMA_REGLA = NC + "test_la_misma_regla_en_javascript"
CON_EL_AYUDANTE = NC + "test_las_navieras_de_javascript_con_el_ayudante"
MIRA = "        if (not antes or antes not in _LETRAS_DE_NAVE) and (not despues or despues not in _LETRAS_DE_NAVE):\n"
JS_MIRA = "            if (!_letraDeNave(t.charAt(j - 1)) && !_letraDeNave(t.charAt(j + x.length))) return j;"

MUTACIONES += [
    # El ayudante de Python: como parte del texto, sin mirar lo pegado antes o después, o sin buscar la siguiente vez.
    dict(id="trae-la-nave-parte-del-texto", pruebas=[NC + "test_trae_la_nave", NC + "test_cosco_calza_en_una_de_sus_naves"],
         viejo="    return bool(palabras) and all(_palabra_en(t, p) >= 0 for p in palabras)\n",
         nuevo="    return bool(palabras) and all(p in t for p in palabras)\n"),
    dict(id="palabra-en-sin-mirar-antes", pruebas=[NC + "test_trae_la_nave", MISMA_REGLA],
         viejo=MIRA, nuevo="        if not despues or despues not in _LETRAS_DE_NAVE:\n"),
    dict(id="palabra-en-sin-mirar-despues", pruebas=[NC + "test_trae_la_nave"],
         viejo=MIRA, nuevo="        if not antes or antes not in _LETRAS_DE_NAVE:\n"),
    dict(id="palabra-en-solo-la-primera", pruebas=[NC + "test_trae_la_nave", MISMA_REGLA],
         viejo="        j = texto.find(palabra, j + 1)\n    return -1\n", nuevo="        return -1\n    return -1\n"),
    # Sin la Ñ entre las letras: «ANDÚ» calzaría dentro de «ÑANDÚ», en Python y en el JavaScript.
    dict(id="letras-sin-enie", pruebas=[NC + "test_trae_la_nave", MISMA_REGLA],
         viejo='_LETRAS_DE_NAVE = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZÑÁÉÍÓÚÜ"',
         nuevo='_LETRAS_DE_NAVE = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÜ"'),
    # El ayudante de JavaScript, con los mismos defectos, sin la guarda de las palabras vacías, o con el borde del texto
    # como si fuera una letra.
    dict(id="js-palabra-sin-mirar-antes", pruebas=[MISMA_REGLA],
         viejo=JS_MIRA, nuevo="            if (!_letraDeNave(t.charAt(j + x.length))) return j;"),
    dict(id="js-palabra-sin-mirar-despues", pruebas=[MISMA_REGLA, ON + "test_js_tarjetas_de_la_nave_con_su_salida"],
         viejo=JS_MIRA, nuevo="            if (!_letraDeNave(t.charAt(j - 1))) return j;"),
    dict(id="js-palabra-solo-la-primera", pruebas=[MISMA_REGLA],
         viejo="        for (let j = t.indexOf(x, desde); j >= 0; j = t.indexOf(x, j + 1)) {",
         nuevo="        for (let j = t.indexOf(x, desde); j >= 0; j = -1) {"),
    dict(id="js-palabra-sin-guarda-vacia", pruebas=[MISMA_REGLA, ON + "test_js_tarjetas_de_la_nave_con_su_salida",
                                                    C1 + "test_js_rutas_nave_con_todas_sus_palabras"],
         viejo="        return palabras.length > 0 && palabras.every(x => _palabraEn(u, x, 0) >= 0);",
         nuevo="        return palabras.every(x => _palabraEn(u, x, 0) >= 0);"),
    # Sin pasar el texto a mayúsculas, como _trae_la_nave.
    dict(id="js-trae-la-nave-con-mayusculas", pruebas=[MISMA_REGLA],
         viejo="        const u = (t || '').toUpperCase();", nuevo="        const u = (t || '');"),
    dict(id="js-letra-vacia-cuenta", pruebas=[MISMA_REGLA],
         viejo="    const _letraDeNave = c => c !== '' && '", nuevo="    const _letraDeNave = c => '"),
    # Cada naviera de JavaScript, sin el ayudante al principio de su función, o calzando otra vez como parte del texto.
    dict(id="one-sin-el-ayudante", pruebas=[CON_EL_AYUDANTE, ON + "test_js_tarjetas_de_la_nave_con_su_salida"],
         viejo='_JS_ONE_TARJETAS_NAVE = """(nave) => {""" + _JS_TRAE_LA_NAVE + """',
         nuevo='_JS_ONE_TARJETAS_NAVE = """(nave) => {""" + """'),
    dict(id="hmm-sin-el-ayudante", pruebas=[CON_EL_AYUDANTE, TH + "test_js_nave_con_todas_sus_palabras"],
         viejo='_JS_HMM_INDICE_NAVE = """(toks)=>{""" + _JS_TRAE_LA_NAVE + """',
         nuevo='_JS_HMM_INDICE_NAVE = """(toks)=>{""" + """'),
    dict(id="mk-sin-el-ayudante", pruebas=[CON_EL_AYUDANTE, MK + "test_js_salidas_lee_la_salida_y_si_se_puede_reservar"],
         viejo='_JS_MK_SALIDAS = """(args) => {""" + _JS_TRAE_LA_NAVE + _JS_HTML_ENTERO + """',
         nuevo='_JS_MK_SALIDAS = """(args) => {""" + _JS_HTML_ENTERO + """'),
    dict(id="cma-sin-el-ayudante", pruebas=[CON_EL_AYUDANTE, C1 + "test_js_rutas_nave_con_todas_sus_palabras"],
         viejo='_JS_CMA_RUTAS = r"""(args)=>{""" + _JS_TRAE_LA_NAVE + r"""',
         nuevo='_JS_CMA_RUTAS = r"""(args)=>{""" + r"""'),
    dict(id="one-nave-parte-del-texto", pruebas=[CON_EL_AYUDANTE, ON + "test_js_tarjetas_de_la_nave_con_su_salida"],
         viejo="const calza = _traeLaNave(suNave, palabras);",
         nuevo="const calza = palabras.length > 0 && palabras.every(x => suNave.includes(x));"),
    dict(id="hmm-nave-parte-del-texto-book", pruebas=[CON_EL_AYUDANTE, TH + "test_js_tarjetas_con_su_1st_vessel"],
         viejo="calza: primera !== null && _traeLaNave(primera, T),",
         nuevo="calza: primera !== null && T.length > 0 && T.every(x => primera.toUpperCase().includes(x)),"),
    dict(id="hmm-nave-parte-del-texto-previa", pruebas=[CON_EL_AYUDANTE, TH + "test_js_nave_con_todas_sus_palabras"],
         viejo="if (_traeLaNave(v, T)) {", nuevo="if (T.every(x => v.includes(x))) {"),
    dict(id="mk-nave-parte-del-texto", pruebas=[CON_EL_AYUDANTE, MK + "test_js_salidas_lee_la_salida_y_si_se_puede_reservar"],
         viejo="            const j = _palabraEn(t, x, pos);", nuevo="            const j = t.indexOf(x, pos);"),
    dict(id="cma-nave-parte-del-texto", pruebas=[CON_EL_AYUDANTE, C1 + "test_js_rutas_nave_con_todas_sus_palabras"],
         viejo="const matched = _traeLaNave(upperTxt, toks);",
         nuevo="const matched = toks.length > 0 && toks.every(tk => upperTxt.includes(tk));"),
    # MSC: el aviso de «ese barco con otro viaje», como parte del texto.
    dict(id="msc-parecidas-parte-del-texto", pruebas=[NC + "test_msc_y_cosco_calzan_con_el_ayudante"],
         viejo='parecidas = [n["nave"] for n in naves if _trae_la_nave(_norm(n.get("nave")), toks[:2])]',
         nuevo='parecidas = [n["nave"] for n in naves if " ".join(toks[:2]) in _norm(n.get("nave"))]'),
]

# --- Encargo 29 · ítem 2, tras la revisión: la palabra vacía, la clase de letras compartida y las palabras de CMA con
# la Ñ y las tildes. ---
MUTACIONES += [
    dict(id="palabra-en-sin-guarda-de-la-vacia", pruebas=[MISMA_REGLA],
         viejo="    if not palabra:\n        return -1\n    j = texto.find(palabra, desde)\n",
         nuevo="    j = texto.find(palabra, desde)\n"),
    dict(id="js-palabra-sin-guarda-de-la-vacia", pruebas=[MISMA_REGLA],
         viejo="        if (!x) return -1;\n", nuevo=""),
    # Otra clase de letras que la de _fila_sin_nave.
    dict(id="letras-distintas-de-la-regla", pruebas=[MISMA_REGLA],
         viejo='_LETRAS_DE_NAVE = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZÑÁÉÍÓÚÜ"',
         nuevo='_LETRAS_DE_NAVE = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZÑÁÉÍÓÚ"'),
    # CMA parte otra vez las palabras en la Ñ y las tildes: «PIÑA» da «PI», que como palabra entera ya no calza.
    dict(id="cma-palabras-sin-enie", pruebas=[C1 + "test_itinerario_comodin_no_se_busca_como_nave"],
         viejo='_re_mk.findall(r"[0-9A-ZÑÁÉÍÓÚÜ]+", nave_pedida.upper())',
         nuevo='_re_mk.sub(r"[^A-Z0-9]+", " ", nave_pedida.upper()).split()'),
]

# --- Encargo 29 · ítem 3: «MANUAL» es un comodín con su propio motivo, «la fila está marcada para hacerse a mano»; el
# panel la sigue dejando sin marcar, ahora con la marca de /api/filas (CICLO-cola-seis-items.md). ---
MANUAL_RESERVADORES = FSN + "test_ningun_reservador_abre_el_portal_con_manual"
MANUAL_WEB = CO + "test_fila_manual_corrida_igual_queda_no_enviada"
MANUAL_CONSOLA = ER + "test_fila_manual_queda_no_enviada"
AVISO_MANUAL = ('        reg.paso(f"✗ fila {fila}: {NO_ENVIADA} · {FILA_MANUAL}. No entro al portal por ella: hazla a mano en el '
                '"\n                 f"portal, o escribe en la celda solo la nave, sin MANUAL, si quieres que la arme '
                'yo.")\n')

MUTACIONES += [
    # MANUAL pide una nave, como hasta f68ce6c: se corre y va al portal.
    dict(id="manual-no-es-comodin", pruebas=[FSN + "test_fila_sin_nave", MANUAL_RESERVADORES, MANUAL_WEB, MANUAL_CONSOLA],
         viejo=REGLA_SIN_NAVE,
         nuevo='    return "COMPLETAR" in t or all(p in NAVES_COMODIN or p in NAVES_PREFIJO for p in palabras)\n'),
    # MANUAL como parte del texto, como hasta c4df3ab: «MANUALMENTE» o «SEMIMANUAL» serían MANUAL
    # (CICLO-inicio-de-todas.md).
    dict(id="manual-como-parte", pruebas=[FSN + "test_fila_manual", FSN + "test_fila_sin_nave"],
         viejo='    return _palabra_en(str(nave or "").upper(), "MANUAL") >= 0\n',
         nuevo='    return "MANUAL" in str(nave or "").upper()\n'),
    # MANUAL como palabra de letras solas: las cifras y la Ñ no contarían como parte de la palabra («MANUAL2», «MANUALÑ»).
    dict(id="manual-por-palabra-sin-cifras", pruebas=[FSN + "test_fila_manual"],
         viejo='    return _palabra_en(str(nave or "").upper(), "MANUAL") >= 0\n',
         nuevo='    return "MANUAL" in _re_mk.findall(r"[A-Z]+", str(nave or "").upper())\n'),
    # Las vocales con tilde y la Ü no contarían como letras: «MANUALÉ» o «ÚMANUAL» serían MANUAL.
    dict(id="manual-por-palabra-sin-tildes", pruebas=[FSN + "test_fila_manual"],
         viejo='    return _palabra_en(str(nave or "").upper(), "MANUAL") >= 0\n',
         nuevo='    return "MANUAL" in _re_mk.findall(r"[0-9A-ZÑ]+", str(nave or "").upper())\n'),
    # Solo algunas vocales con tilde como letras: «MANUALÁ», «ÍMANUAL» o «MANUALÓ» serían MANUAL.
    dict(id="manual-por-palabra-con-algunas-tildes", pruebas=[FSN + "test_fila_manual"],
         viejo='    return _palabra_en(str(nave or "").upper(), "MANUAL") >= 0\n',
         nuevo='    return "MANUAL" in _re_mk.findall(r"[0-9A-ZÑÉÚÜ]+", str(nave or "").upper())\n'),
    # Solo la primera vez que aparece: «SEMIMANUAL MANUAL» dejaría de ser MANUAL.
    dict(id="manual-solo-la-primera-vez", pruebas=[FSN + "test_fila_manual"],
         viejo='    return _palabra_en(str(nave or "").upper(), "MANUAL") >= 0\n',
         nuevo='    t = str(nave or "").upper(); j = t.find("MANUAL")\n'
               '    return j >= 0 and _palabra_en(t[max(j - 1, 0):j + 7], "MANUAL") >= 0\n'),
    # El guion bajo como letra: «NAVE_MANUAL» dejaría de ser MANUAL, aunque _fila_sin_nave lo separa como signo.
    dict(id="manual-guion-bajo-es-letra", pruebas=[FSN + "test_fila_manual"],
         viejo='    return _palabra_en(str(nave or "").upper(), "MANUAL") >= 0\n',
         nuevo='    return _palabra_en(str(nave or "").upper().replace("_", "X"), "MANUAL") >= 0\n'),
    # Con el motivo de la fila sin nave, otro motivo, o sin el aviso.
    dict(id="manual-con-el-otro-motivo", pruebas=[MANUAL_RESERVADORES, MANUAL_WEB, MANUAL_CONSOLA],
         viejo="    if _fila_manual(nave):\n        reg.paso(", nuevo="    if False:\n        reg.paso("),
    dict(id="manual-otro-motivo", pruebas=[FSN + "test_fila_manual", MANUAL_RESERVADORES, MANUAL_WEB, MANUAL_CONSOLA],
         viejo='FILA_MANUAL = "la fila está marcada para hacerse a mano"', nuevo='FILA_MANUAL = "fila manual"'),
    dict(id="manual-sin-aviso", pruebas=[MANUAL_RESERVADORES, MANUAL_WEB, MANUAL_CONSOLA],
         viejo=AVISO_MANUAL, nuevo=""),
    # El decorador, la web o la consola no le pasan la nave a _sin_nave: queda con el motivo de la fila sin nave.
    dict(id="manual-decorador-sin-la-nave", pruebas=[MANUAL_RESERVADORES],
         viejo='            return _sin_nave(reg, (reserva or {}).get("fila"), (reserva or {}).get("nave"))\n',
         nuevo='            return _sin_nave(reg, (reserva or {}).get("fila"))\n'),
    dict(id="manual-web-sin-la-nave", pruebas=[MANUAL_WEB],
         viejo='                estado, detalle = _sin_nave(reg, rsv["fila"], rsv.get("nave"))\n',
         nuevo='                estado, detalle = _sin_nave(reg, rsv["fila"])\n'),
    dict(id="manual-consola-sin-la-nave", pruebas=[MANUAL_CONSOLA],
         viejo='            anotar(i, rsv, *_sin_nave(reg, rsv["fila"], rsv["nave"]))\n',
         nuevo='            anotar(i, rsv, *_sin_nave(reg, rsv["fila"]))\n'),
    # /api/filas: la MANUAL contada como sin nave, o sin su marca.
    dict(id="filas-manual-cuenta-como-sin-nave", pruebas=[MANUAL_WEB],
         viejo=MARCA, nuevo="    return dict(fila, sin_nave=_fila_sin_nave(nave), manual=_fila_manual(nave),\n"),
    dict(id="filas-sin-la-marca-manual", pruebas=[MANUAL_WEB],
         viejo=MARCA, nuevo="    return dict(fila, sin_nave=_fila_sin_nave(nave) and not _fila_manual(nave),\n"),
    # El panel vuelve a su propia regla, como hasta f68ce6c.
    dict(id="panel-vuelve-a-su-regla", pruebas=[PANEL_MARCA, FSN + "test_una_sola_regla"],
         viejo="  return !f.manual;\n", nuevo="  return !(f.nave || '').toUpperCase().includes('MANUAL');\n"),
]

# --- Encargo 29 · ítem 4: la consola deja de tomar la nave de la columna F en ONE y MSC cuando la celda de la nave viene
# vacía; esa fila queda sin nave, y lo demás del lector no cambia (CICLO-cola-seis-items.md). ---
LA_F = ER + "test_la_nave_no_sale_de_la_columna_f"

MUTACIONES += [
    # La F vuelve a ser la nave: en ONE, en MSC, o en las dos.
    dict(id="consola-nave-de-la-f-one", pruebas=[CON + "test_consola_one", CON + "test_consola_trampa_de_titulo", LA_F],
         viejo="                nave_de_la_f = True\n                dest_final = dest_orig",
         nuevo="                dest_final = dest_orig"),
    dict(id="consola-nave-de-la-f-msc", pruebas=[CON + "test_consola_msc", LA_F],
         viejo='["MSC", "NX", "LEILA"]):\n                nave = val_f\n                nave_de_la_f = True\n',
         nuevo='["MSC", "NX", "LEILA"]):\n                nave = val_f\n'),
    dict(id="consola-la-f-sigue-siendo-la-nave", pruebas=[CON + "test_consola_one", CON + "test_consola_msc", DIF, LA_F],
         viejo='                "nave": "" if nave_de_la_f else nave,\n', nuevo='                "nave": nave,\n'),
    # La F deja de decidir qué filas entran y cuáles son notas, en ONE o en MSC.
    dict(id="consola-f-no-decide-las-filas-one", pruebas=[CON + "test_la_f_sigue_decidiendo_las_filas"],
         viejo="                nave = val_f\n                nave_de_la_f = True\n                dest_final = dest_orig",
         nuevo="                nave_de_la_f = True\n                dest_final = dest_orig"),
    dict(id="consola-f-no-decide-las-filas-msc", pruebas=[CON + "test_la_f_sigue_decidiendo_las_filas"],
         viejo='["MSC", "NX", "LEILA"]):\n                nave = val_f\n                nave_de_la_f = True\n',
         nuevo='["MSC", "NX", "LEILA"]):\n                nave_de_la_f = True\n'),
    dict(id="consola-sin-mirar-la-f-msc", pruebas=[CON + "test_la_f_sigue_decidiendo_las_filas"],
         viejo='            if not nave and any(w in val_f.upper() for w in ["MSC", "NX", "LEILA"]):\n',
         nuevo="            if False:\n"),
    # La F deja de mirarse en ONE: cambia otra columna, el destino final de la 7, y las filas que entran.
    dict(id="consola-sin-mirar-la-f-one", pruebas=[CON + "test_consola_one", DIF, CON + "test_la_f_sigue_decidiendo_las_filas"],
         viejo='            if any(w in val_f.upper() for w in ["MSC", "ONE", "FA", "JULIETTE", "LEILA", "VIVIENNE"]):\n',
         nuevo="            if False:\n"),
]

# --- Encargo 29 · ítem 5: COSCO, sin el puerto de carga de la fila, corta como objetivo no encontrado en vez de buscar
# desde el puerto fijo del código (CICLO-cola-seis-items.md). ---
K5 = "test_clics.TestCosco."
ORIGEN = K5 + "test_puerto_de_carga_sin_sugerencia_corta"
# Encargo 46: la línea que quita el país al final del puerto de COSCO («CHILE» o «CL», PAIS_DEL_PUERTO).
SIN_PAIS_AL_FINAL = '    while palabras and palabras[-1] in PAIS_DEL_PUERTO:\n'
# Desde el encargo 41, con la evidencia de la lista (CICLO-origen-y-destino.md).
AUTO_ORIGEN = ('_cosco_autocomplete(frame, "origin ci", pol_ciudad, pol_ciudad, reg, "Origin City", '
               'preferir_chile=True,\n'
               '                               evidencia=f"cosco_f{reserva.get(\'fila\')}_origen")')
SIN_SUGERENCIA = ("    if not " + AUTO_ORIGEN + ":\n"
                  '        en_la_fila = "" if celda.upper() == pol_ciudad.upper() else f" (en la fila, «{celda}»)"\n'
                  '        raise ObjetivoNoEncontrado("Origin City de COSCO",\n')

# El puerto de la celda normalizado (encargo 30 · ítem 5, CICLO-inicio-de-todas.md).
NORMALIZA = '    palabras = _re_mk.sub(r"[^0-9A-Z]+", " ", _norm_ctrl(str(celda or "").split(",")[0])).split()\n'

MUTACIONES += [
    # Vuelve el respaldo de hasta f68ce6c: sin sugerencia, busca «Lirquen» y sigue.
    dict(id="cosco-origen-vuelve-al-fijo", pruebas=[ORIGEN], cambios=[
        (SIN_SUGERENCIA, "    if not " + AUTO_ORIGEN + ":\n        pol_ciudad = \"Lirquen\"\n        " + AUTO_ORIGEN
         + "\n    if False:\n        en_la_fila = \"\"\n        raise ObjetivoNoEncontrado(\"Origin City de COSCO\",\n")]),
    # Sin sugerencia, lo anota y sigue con el texto escrito.
    dict(id="cosco-origen-sigue-sin-sugerencia", pruebas=[ORIGEN],
         viejo=SIN_SUGERENCIA, nuevo=SIN_SUGERENCIA.replace('_origen"):\n', '_origen") and False:\n', 1)),
    # La celda en el motivo aunque sea el mismo puerto, en otras mayúsculas.
    dict(id="cosco-origen-celda-con-mayusculas", pruebas=[ORIGEN],
         viejo='en_la_fila = "" if celda.upper() == pol_ciudad.upper() else', nuevo='en_la_fila = "" if celda == pol_ciudad else'),
    # Con la celda vacía, busca igual: cualquier sugerencia de Chile calza con el texto vacío.
    dict(id="cosco-origen-vacio-busca", pruebas=[ORIGEN],
         viejo="    if not pol_ciudad:\n        raise ObjetivoNoEncontrado(", nuevo="    if False:\n        raise ObjetivoNoEncontrado("),
    # Otro campo, o cualquier país: escribiría el puerto en «Destination», o elegiría un «SAN ANTONIO» de otro país.
    dict(id="cosco-origen-otro-campo", pruebas=[ORIGEN],
         viejo=SIN_SUGERENCIA, nuevo=SIN_SUGERENCIA.replace('"origin ci"', '"destinati"')),
    dict(id="cosco-origen-sin-chile", pruebas=[ORIGEN],
         viejo=SIN_SUGERENCIA, nuevo=SIN_SUGERENCIA.replace("preferir_chile=True", "preferir_chile=False")),
    # El mapa, consultado en otras mayúsculas que sus claves: «CORONEL» dejaría de ser «Lirquen».
    dict(id="cosco-origen-mapa-con-mayusculas", pruebas=[ORIGEN],
         viejo="    pol_ciudad = MAPA_PUERTOS_COSCO.get(puerto, puerto)\n",
         nuevo="    pol_ciudad = MAPA_PUERTOS_COSCO.get(puerto.title(), puerto)\n"),
    # Sin normalizar, como hasta c4df3ab: la celda entera en el mapa y su primera parte tal cual; ni «CORONEL, CHILE»
    # ni «Lirquén» serían «Lirquen», y «puerto alfa» se buscaría en minúsculas (CICLO-inicio-de-todas.md).
    dict(id="cosco-origen-sin-normalizar", pruebas=[ORIGEN],
         viejo="    pol_ciudad = MAPA_PUERTOS_COSCO.get(puerto, puerto)\n",
         nuevo='    pol_ciudad = MAPA_PUERTOS_COSCO.get(celda.upper(), celda.split(",")[0].strip())\n'),
    # El motivo sin la celda de la fila, cuando el mapa la tradujo.
    dict(id="cosco-origen-sin-la-celda", pruebas=[ORIGEN],
         viejo='else f" (en la fila, «{celda}»)"', nuevo='else ""'),
    # La normalización sin quitar las tildes; sin quitar «CHILE» al final; sin quitarlo cuando es la única palabra
    # (buscaría «CHILE»); quitándolo también en medio del nombre; quitándolo una sola vez («CHILE CHILE» buscaría
    # «CHILE»); con solo los signos que quita _norm_ctrl («CORONEL–CHILE» o «CORONEL — CHILE» no se traducirían); o sin
    # cortar en la coma («San Vicente, Talcahuano» no se traduciría).
    dict(id="cosco-origen-con-tildes", pruebas=[ORIGEN],
         viejo=NORMALIZA, nuevo='    palabras = _re_mk.sub(r"[^0-9A-ZÁÉÍÓÚ]+", " ", str(celda or "").split(",")[0].upper()).split()\n'),
    dict(id="cosco-origen-con-el-pais", pruebas=[ORIGEN], viejo=SIN_PAIS_AL_FINAL, nuevo='    while False:\n'),
    dict(id="cosco-origen-busca-el-pais-solo", pruebas=[ORIGEN], viejo=SIN_PAIS_AL_FINAL,
         nuevo='    while len(palabras) > 1 and palabras[-1] in PAIS_DEL_PUERTO:\n'),
    dict(id="cosco-origen-quita-chile-en-medio", pruebas=[ORIGEN],
         viejo=SIN_PAIS_AL_FINAL + '        palabras = palabras[:-1]\n',
         nuevo='    palabras = [p for p in palabras if p not in PAIS_DEL_PUERTO]\n'),
    dict(id="cosco-origen-un-solo-chile", pruebas=[ORIGEN], viejo=SIN_PAIS_AL_FINAL,
         nuevo='    if palabras and palabras[-1] in PAIS_DEL_PUERTO:\n'),
    # Encargo 46: al final quita solo «CHILE», como hasta ahí: «CORONEL CL» buscaría «CORONEL CL».
    dict(id="cosco-origen-quita-solo-chile", pruebas=[ORIGEN], viejo=SIN_PAIS_AL_FINAL,
         nuevo='    while palabras and palabras[-1] == "CHILE":\n'),
    dict(id="cosco-origen-solo-los-signos-de-norm-ctrl", pruebas=[ORIGEN],
         viejo=NORMALIZA, nuevo='    palabras = _norm_ctrl(str(celda or "").split(",")[0]).split()\n'),
    dict(id="cosco-origen-sin-coma", pruebas=[ORIGEN],
         viejo=NORMALIZA, nuevo='    palabras = _re_mk.sub(r"[^0-9A-Z]+", " ", _norm_ctrl(str(celda or ""))).split()\n'),
    # reservar_cosco arma el puerto sin el ayudante, que es el que corta.
    dict(id="cosco-origen-sin-el-ayudante", pruebas=[K5 + "test_reservar_cosco_elige_el_puerto_de_carga_con_el_ayudante"],
         viejo="    pol_ciudad = _cosco_puerto_de_carga(frame, reserva, reg)\n",
         nuevo='    pol_ciudad = MAPA_PUERTOS_COSCO.get((reserva.get("pol") or "").strip().upper(), reserva.get("pol") or "")\n'),
]

# --- Encargo 29 · ítem 6: antes de la guarda, el asistente de ONE avanza con el «Next» identificado por su texto
# (_JS_ONE_SIGUIENTE, _one_siguiente); si no hay uno solo, si está en una ventana emergente o si el asistente no está en
# esa pantalla, corta. El envío después de la guarda no se toca (CICLO-cola-seis-items.md). ---
SIGUIENTE_JS = ON + "test_js_siguiente_solo_el_de_la_pantalla"
SIGUIENTE_CORTA = ON + "test_siguiente_sin_uno_solo_corta"
SIGUIENTE_EN_ONE = ON + "test_reservar_one_avanza_con_el_siguiente_identificado"
FALLA_SIGUIENTE = ('            raise ObjetivoNoEncontrado(objetivo,\n'
                   '                                       f"un solo botón «Next» a la vista (no pude buscarlo: {str(e)[:60]})")\n')
FILTRO_SIGUIENTE = "        .filter(b => !b.closest('header, nav, [role=\"navigation\"]') && vis(b))\n"

MUTACIONES += [
    # El JavaScript: toma el primero entre varios, cuenta los ocultos o los del encabezado, acepta otros textos, pulsa
    # el de una ventana emergente, o mira una sola de las dos señales de «a la vista».
    dict(id="one-siguiente-toma-el-primero", pruebas=[SIGUIENTE_JS],
         viejo="    if (botones.length !== 1) return botones.length;\n", nuevo="    if (botones.length === 0) return 0;\n"),
    dict(id="one-siguiente-cuenta-ocultos", pruebas=[SIGUIENTE_JS],
         viejo=FILTRO_SIGUIENTE, nuevo=FILTRO_SIGUIENTE.replace(" && vis(b)", "")),
    dict(id="one-siguiente-en-el-encabezado", pruebas=[SIGUIENTE_JS],
         viejo=FILTRO_SIGUIENTE, nuevo="        .filter(b => vis(b))\n"),
    dict(id="one-siguiente-otros-textos", pruebas=[SIGUIENTE_JS],
         viejo="/^(next|siguiente)$/i", nuevo="/^(next|siguiente|continue|continuar|review|revisar)$/i"),
    dict(id="one-siguiente-pulsa-en-la-ventana", pruebas=[SIGUIENTE_JS],
         viejo="    if (botones.some(b => b.closest(dialogo))) return -1;\n", nuevo=""),
    dict(id="one-siguiente-vis-solo-tamano", pruebas=[SIGUIENTE_JS],
         viejo="        return e.offsetParent !== null && r.width > 0 && r.height > 0;\n    };\n    const botones",
         nuevo="        return r.width > 0 && r.height > 0;\n    };\n    const botones"),
    dict(id="one-siguiente-vis-solo-lugar", pruebas=[SIGUIENTE_JS],
         viejo="        return e.offsetParent !== null && r.width > 0 && r.height > 0;\n    };\n    const botones",
         nuevo="        return e.offsetParent !== null;\n    };\n    const botones"),
    # El ayudante: no corta, reintenta con dos o con la ventana, no mira la pantalla, o dice «había 0» sin haber podido
    # buscar.
    dict(id="one-siguiente-no-corta", pruebas=[SIGUIENTE_CORTA],
         viejo='    raise ObjetivoNoEncontrado(objetivo, f"un solo botón «Next» a la vista (había {n})")\n',
         nuevo='    reg.info(f"no encontré \'Next\' en {pantalla} (había {n})")\n'),
    dict(id="one-siguiente-reintenta-sin-cero", pruebas=[SIGUIENTE_CORTA],
         viejo="        if n != 0:\n            break\n", nuevo=""),
    dict(id="one-siguiente-sin-mirar-la-pantalla", pruebas=[SIGUIENTE_CORTA],
         viejo='    if not _one_esta_en_paso(page, paso):\n        raise ObjetivoNoEncontrado(objetivo, f"la pantalla «{pantalla}»: el '
               'asistente no está en ella")\n',
         nuevo=""),
    dict(id="one-siguiente-ventana-como-cero", pruebas=[SIGUIENTE_CORTA],
         viejo="    if n == -1:\n", nuevo="    if n == -2:\n"),
    dict(id="one-siguiente-no-dice-que-no-pudo", pruebas=[SIGUIENTE_CORTA],
         viejo=FALLA_SIGUIENTE, nuevo=FALLA_SIGUIENTE.replace("no pude buscarlo: {str(e)[:60]}", "había {n}")),
    # Tras una falla de la búsqueda, reintenta: el clic pudo haber salido, y pulsaría el «Next» de la pantalla siguiente.
    dict(id="one-siguiente-reintenta-tras-una-falla", pruebas=[SIGUIENTE_CORTA],
         viejo=FALLA_SIGUIENTE, nuevo="            continue\n"),
    # Cada pantalla vuelve al clic genérico de hasta f68ce6c.
    dict(id="one-parties-generico", pruebas=[SIGUIENTE_EN_ONE],
         viejo='        _one_siguiente(page, reg, "Booking Parties", "booking-parties")\n',
         nuevo='        page.evaluate(_JS_CLICK_BTN, "^(next|siguiente|continue|continuar)$")\n'),
    dict(id="one-carga-generico", pruebas=[SIGUIENTE_EN_ONE],
         viejo='    _one_siguiente(page, reg, "Container & Cargo", "container-cargo-details")\n',
         nuevo='    page.evaluate(_JS_CLICK_BTN, "^(next|siguiente|continue|continuar)$")\n'),
    dict(id="one-adicional-generico", pruebas=[SIGUIENTE_EN_ONE],
         viejo='    _one_siguiente(page, reg, "Additional Info", "additional-information")\n',
         nuevo='    page.evaluate(_JS_CLICK_BTN, "^(next|siguiente|review|revisar|continue|continuar)$")\n'),
]

# --- Encargo 30 · ítem 1: CSCL y COSCO SHIPPING son prefijos de naviera; COSCO SHIPPING, como sus dos palabras, igual que
# CMA CGM (CICLO-inicio-de-todas.md). ---
MUTACIONES += [
    # Sin CSCL, como hasta c4df3ab: «CSCL» pediría una nave y calzaría con toda nave que la trae.
    dict(id="prefijos-sin-cscl", pruebas=[FSN + "test_fila_sin_nave"],
         viejo=PREFIJOS, nuevo=PREFIJOS.replace(', "CSCL"', "")),
    # Sin SHIPPING: «COSCO SHIPPING», «SHIPPING» o «SHIPPING COSCO» pedirían una nave.
    dict(id="prefijos-sin-shipping", pruebas=[FSN + "test_fila_sin_nave"],
         viejo=PREFIJOS, nuevo=PREFIJOS.replace(', "SHIPPING"', "")),
    # COSCO SHIPPING solo como frase, en su orden y seguida (la primera versión del ítem, que se descartó): «COSCO
    # SHIPPING» no pediría una nave, pero «SHIPPING», «SHIPPING COSCO», «COSCO AUTO SHIPPING» y «COSCO-SHIPPING» sí.
    dict(id="prefijos-cosco-shipping-como-frase", pruebas=[FSN + "test_fila_sin_nave"], cambios=[
        (PREFIJOS, PREFIJOS.replace(', "SHIPPING"', "")),
        ('    palabras = _re_mk.findall(r"[0-9A-ZÑÁÉÍÓÚÜ]{2,}", t)\n',
         '    palabras = _re_mk.findall(r"[0-9A-ZÑÁÉÍÓÚÜ]{2,}", t.replace("COSCO SHIPPING", "COSCO"))\n')]),
]

# --- Encargo 30 · ítem 3: el viaje de MAERSK calza por palabra entera en el valor de «Vessel/voyage»
# (CICLO-inicio-de-todas.md). ---
MUTACIONES += [
    # Como hasta c4df3ab: «541W» calzaría dentro de «1541W» y de «541WA».
    dict(id="mk-viaje-como-parte", pruebas=["test_clics.TestMaersk.test_js_salidas_lee_la_salida_y_si_se_puede_reservar"],
         viejo="viaje: !!V && _palabraEn(t, V, 0) >= 0,", nuevo="viaje: !!V && t.includes(V),"),
    # Sin límite después: «541WA» sería el viaje «541W».
    dict(id="mk-viaje-sin-limite-despues", pruebas=["test_clics.TestMaersk.test_js_salidas_lee_la_salida_y_si_se_puede_reservar"],
         viejo="viaje: !!V && _palabraEn(t, V, 0) >= 0,",
         nuevo="viaje: !!V && t.split(/[^0-9A-ZÑÁÉÍÓÚÜ]/).some(w => w.startsWith(V)),"),
    # Sin límite antes: «1541W» sería el viaje «541W».
    dict(id="mk-viaje-sin-limite-antes", pruebas=["test_clics.TestMaersk.test_js_salidas_lee_la_salida_y_si_se_puede_reservar"],
         viejo="viaje: !!V && _palabraEn(t, V, 0) >= 0,",
         nuevo="viaje: !!V && t.split(/[^0-9A-ZÑÁÉÍÓÚÜ]/).some(w => w.endsWith(V)),"),
    # El viaje de la fila tal como viene: «541w» no calzaría con «541W».
    dict(id="mk-viaje-distingue-mayusculas", pruebas=["test_clics.TestMaersk.test_js_salidas_lee_la_salida_y_si_se_puede_reservar"],
         viejo="    const V = (args.viaje || '').toUpperCase();\n", nuevo="    const V = (args.viaje || '');\n"),
]

# --- Encargo 30 · ítem 4: MSC pierde su clic genérico (_JS_CLICK_BTN) antes de la guarda: en su login y en «Search
# Schedule» (_msc_buscar_itinerarios). La foto de test_clics ve el de «Search Schedule»; el del login, que no está en el
# universo de ningún reservador, lo vigila test_login_sin_clic_generico (CICLO-inicio-de-todas.md). ---
MSC_LOGIN = "test_clics.TestMsc.test_login_sin_clic_generico"
MSC_BUSCA = "test_clics.TestMsc.test_search_schedule_sin_boton_corta"
FOTO = "test_clics.TestFotoDeClicsGenericos.test_ningun_clic_generico_nuevo_antes_de_la_guarda"
SIN_NEXT = '        reg.info("no encontré el botón «Next» ni «Siguiente» del login de MSC; no pulsé nada")\n'
SIN_ENTRAR = '        reg.info("no encontré el botón para entrar a MSC (Login, Sign In, Next o Iniciar); no pulsé nada")\n'
SIN_BUSCAR = ('        raise ObjetivoNoEncontrado("Search Schedule de MSC", "el botón «Search Schedule» o «Buscar» (por su '
              'texto)")\n')
BUSCA_SELECTOR = ('    if not click_si_existe(page, "button:has-text(\'Search Schedule\'), button:has-text(\'Buscar\')", 6000, '
                  'reg):\n        raise ObjetivoNoEncontrado(')

MUTACIONES += [
    # Vuelve el clic genérico de hasta c4df3ab, en cada uno de los tres lugares.
    dict(id="msc-login-next-generico", pruebas=[MSC_LOGIN],
         viejo=SIN_NEXT, nuevo='        page.evaluate(_JS_CLICK_BTN, "^(next|siguiente)$")\n'),
    dict(id="msc-login-entrar-generico", pruebas=[MSC_LOGIN],
         viejo=SIN_ENTRAR, nuevo='        page.evaluate(_JS_CLICK_BTN, "^(login|sign in|next|iniciar|siguiente|log in)$")\n'),
    dict(id="msc-busca-generico", pruebas=[MSC_BUSCA, FOTO],
         viejo=SIN_BUSCAR, nuevo='        page.evaluate(_JS_CLICK_BTN, "search schedule|buscar")\n'),
    # El «Next» del login con el primer botón de la página, cualquiera.
    dict(id="msc-login-next-cualquier-boton", pruebas=[MSC_LOGIN],
         viejo=('    if not click_si_existe(page, "button:has-text(\'Next\'), button:has-text(\'Siguiente\')", 5000, reg):\n'
                '        reg.info('),
         nuevo='    if not click_si_existe(page, "button", 5000, reg):\n        reg.info('),
    # Otro clic a ciegas en el login, que no nombra _JS_CLICK_BTN: Enter en lo que tenga el foco.
    dict(id="msc-login-entrar-a-ciegas", pruebas=[MSC_LOGIN],
         viejo=SIN_ENTRAR, nuevo='        page.keyboard.press("Enter")\n'),
    # Sin el botón, lo anota y sigue: leería los itinerarios de una búsqueda que no se hizo.
    dict(id="msc-busca-no-corta", pruebas=[MSC_BUSCA],
         viejo=SIN_BUSCAR, nuevo='        reg.info("no encontré Search Schedule")\n'),
    # El primer botón de la página, cualquiera.
    dict(id="msc-busca-cualquier-boton", pruebas=[MSC_BUSCA],
         viejo=BUSCA_SELECTOR, nuevo='    if not click_si_existe(page, "button", 6000, reg):\n        raise ObjetivoNoEncontrado('),
    # reservar_msc pulsa sin el ayudante, y no corta.
    dict(id="msc-busca-sin-el-ayudante", pruebas=[MSC_BUSCA],
         viejo="    _msc_buscar_itinerarios(page, reg)\n",
         nuevo='    click_si_existe(page, "button:has-text(\'Search Schedule\')", 6000, reg)\n'),
]

# --- Encargo 31 · ítem 1: el botón de entrar del login de MSC va solo por su texto (decisión de Marcelo,
# CICLO-cierre-de-frenos.md). Las mutaciones del reintento tras un 502 salieron en el encargo 45. ---
MUTACIONES += [
    # El de entrar vuelve a aceptar el primer botón de envío de la página, como hasta 4948e16.
    dict(id="msc-entrar-con-submit", pruebas=[MSC_LOGIN],
         viejo="""            "button:has-text('Iniciar')", 5000, reg):\n""",
         nuevo="""            "button:has-text('Iniciar'), button[type='submit']", 5000, reg):\n"""),
]

# --- Encargo 45: el login de MSC termina cada espera con lo primero que llegue, ante el error va una sola vez a eBooking
# y no reintenta, reconoce la sesión por su página y el error también por la página de error del propio MSC; sin la
# sesión, la fila de MSC queda NO ENVIADA (decisiones de Marcelo, CICLO-login-msc-y-maersk.md). Reemplazan las del
# encargo 31 sobre el reintento tras un 502 (MSC_REINTENTOS_502) y _msc_error_502. ---
MSC_ERR = "test_clics.TestMsc.test_error_del_portal"
MSC_SES = "test_clics.TestMsc.test_sesion_solo_en_su_pagina"
MSC_ESP = "test_clics.TestMsc.test_login_termina_con_lo_primero_que_llega"
MSC_TRAS = "test_clics.TestMsc.test_ante_el_error_va_una_vez_a_ebooking_y_no_reintenta"
TEXTOS_ERR = 'MSC_TEXTOS_DE_ERROR = ("502", "no puede procesar", "unable to complete your request")\n'
SESION = '    return u.netloc.lower() == "www.mymsc.com" and u.path.lower().rstrip("/") in MSC_PAGINAS_CON_SESION\n'
A_EBOOKING = ('        page.goto(MSC_EBOOKING, wait_until="domcontentloaded")\n    except Exception as e:\n'
              '        reg.info(f"no pude ir a eBooking')

MUTACIONES += [
    # _msc_error sin la página de error de MSC, sin la de Chrome por su dirección o por uno de sus textos, o que da el
    # error cuando no pudo leer la página.
    dict(id="msc-error-sin-la-de-msc", pruebas=[MSC_ERR],
         viejo=TEXTOS_ERR, nuevo='MSC_TEXTOS_DE_ERROR = ("502", "no puede procesar")\n'),
    dict(id="msc-error-sin-chrome-error", pruebas=[MSC_ERR],
         viejo='        if str(page.url).lower().startswith("chrome-error://"):\n            return True\n',
         nuevo='        if str(page.url).lower().startswith("chrome-error://"):\n            pass\n'),
    dict(id="msc-error-sin-502", pruebas=[MSC_ERR],
         viejo=TEXTOS_ERR, nuevo='MSC_TEXTOS_DE_ERROR = ("no puede procesar", "unable to complete your request")\n'),
    dict(id="msc-error-sin-no-puede-procesar", pruebas=[MSC_ERR],
         viejo=TEXTOS_ERR, nuevo='MSC_TEXTOS_DE_ERROR = ("502", "unable to complete your request")\n'),
    dict(id="msc-error-sin-leer", pruebas=[MSC_ERR],
         viejo="    txt = texto_pagina(page)\n    return any(t in txt for t in MSC_TEXTOS_DE_ERROR)\n",
         nuevo='    txt = texto_pagina(page) or "502"\n    return any(t in txt for t in MSC_TEXTOS_DE_ERROR)\n'),
    # _msc_sesion como hasta el encargo 45 (cualquier página de mymsc.com), sin eBooking, de cualquier servidor, sin
    # quitar la barra del final o distinguiendo mayúsculas.
    dict(id="msc-sesion-como-antes", pruebas=[MSC_SES], viejo=SESION,
         nuevo='    return "mymsc.com" in str(page.url).lower()\n'),
    dict(id="msc-sesion-sin-ebooking", pruebas=[MSC_SES],
         viejo='MSC_PAGINAS_CON_SESION = ("/mymsc/welcome", "/mymsc/booking/main")\n',
         nuevo='MSC_PAGINAS_CON_SESION = ("/mymsc/welcome",)\n'),
    dict(id="msc-sesion-cualquier-servidor", pruebas=[MSC_SES], viejo=SESION,
         nuevo='    return u.path.lower().rstrip("/") in MSC_PAGINAS_CON_SESION\n'),
    dict(id="msc-sesion-con-la-barra", pruebas=[MSC_SES], viejo=SESION,
         nuevo='    return u.netloc.lower() == "www.mymsc.com" and u.path.lower() in MSC_PAGINAS_CON_SESION\n'),
    dict(id="msc-sesion-con-mayusculas", pruebas=[MSC_SES], viejo=SESION,
         nuevo='    return u.netloc.lower() == "www.mymsc.com" and u.path.rstrip("/") in MSC_PAGINAS_CON_SESION\n'),
    # Las esperas: sin mirar la sesión, sin terminar con el campo, con otro tope, con la espera fija de antes tras el
    # «Next», sin la pausa de la validación, o sin mirar si ya había sesión al abrir.
    dict(id="msc-espera-sin-la-sesion", pruebas=[MSC_ESP],
         viejo='        if _msc_sesion(page):\n            return "sesión"\n', nuevo=""),
    dict(id="msc-espera-sin-el-campo", pruebas=[MSC_ESP],
         viejo='        if campo and _msc_a_la_vista(page, campo):\n            return "campo"\n', nuevo=""),
    dict(id="msc-espera-otro-tope", pruebas=[MSC_ESP], viejo="MSC_SONDEOS = 60\n", nuevo="MSC_SONDEOS = 61\n"),
    dict(id="msc-espera-fija-tras-el-next", pruebas=[MSC_ESP],
         viejo="    _msc_cookies(page, reg)\n    paso = _msc_esperar(",
         nuevo='    esperar(page, 3, reg, "esperar contraseña")\n    _msc_cookies(page, reg)\n    paso = _msc_esperar('),
    dict(id="msc-sin-la-pausa", pruebas=[MSC_ESP],
         viejo="        if validar and not pauso and any(", nuevo="        if False and not pauso and any("),
    dict(id="msc-ya-habia-sin-mirar", pruebas=[MSC_ESP],
         viejo='    if _msc_sesion(page):\n        reg.paso("Ya había una sesión activa.")',
         nuevo='    if False:\n        reg.paso("Ya había una sesión activa.")'),
    # Ante el error: sin mirar el error en la espera, sin ir a eBooking, yendo dos veces, volviendo a entrar, dándola
    # por iniciada sin mirar, sin mirar el error al abrir, sin su captura o sin decirlo.
    dict(id="msc-espera-sin-el-error", pruebas=[MSC_TRAS],
         viejo='        if _msc_error(page):\n            return "error"\n', nuevo=""),
    dict(id="msc-error-sin-ir-a-ebooking", pruebas=[MSC_TRAS],
         viejo=A_EBOOKING, nuevo=A_EBOOKING.replace('page.goto(MSC_EBOOKING, wait_until="domcontentloaded")', "pass")),
    dict(id="msc-error-dos-veces-a-ebooking", pruebas=[MSC_TRAS],
         viejo=A_EBOOKING, nuevo='        page.goto(MSC_EBOOKING, wait_until="domcontentloaded")\n' + A_EBOOKING),
    dict(id="msc-error-reintenta-el-login", pruebas=[MSC_TRAS],
         viejo='    desenlace = _msc_esperar(page, reg, "la sesión en eBooking",\n',
         nuevo='    _msc_entrar(page, {"usuario": "u", "clave": "c"}, reg)\n'
               '    desenlace = _msc_esperar(page, reg, "la sesión en eBooking",\n'),
    dict(id="msc-error-sin-mirar-la-sesion", pruebas=[MSC_TRAS],
         viejo='    ok = desenlace == "sesión"\n    reg.paso("Sesión iniciada." if ok else "⚠ Después',
         nuevo='    ok = True\n    reg.paso("Sesión iniciada." if ok else "⚠ Después'),
    dict(id="msc-error-al-abrir-sin-mirar", pruebas=[MSC_TRAS],
         viejo='    desenlace = "error" if _msc_error(page) else _msc_entrar(page, creds, reg, on_pausa)\n',
         nuevo="    desenlace = _msc_entrar(page, creds, reg, on_pausa)\n"),
    dict(id="msc-error-sin-su-captura", pruebas=[MSC_TRAS],
         viejo='    reg.url(page); reg.captura(page, "msc_error")\n', nuevo="    reg.url(page)\n"),
    dict(id="msc-error-sin-aviso", pruebas=[MSC_TRAS],
         viejo='    reg.paso("⚠ MSC mostró una página de error al iniciar sesión.',
         nuevo='    reg.info("⚠ MSC mostró una página de error al iniciar sesión.'),
    # Sin la sesión de MSC, la fila queda sin estado, como antes, en el panel o en la consola; o NO ENVIADA con
    # cualquier naviera.
    dict(id="msc-sin-sesion-panel-sin-estado", pruebas=[CO + "test_login_fallido_de_msc_queda_no_enviada"],
         viejo="                    for rsv in (sub_elegidas if nav in SIN_SESION else ()):\n",
         nuevo="                    for rsv in ():\n"),
    dict(id="msc-sin-sesion-consola-sin-estado", pruebas=[ER + "test_login_fallido_de_msc_queda_no_enviada"],
         viejo="            for i, rsv in (con_nave if naviera_clave in SIN_SESION else ()):\n",
         nuevo="            for i, rsv in ():\n"),
    dict(id="sin-sesion-cualquier-naviera",
         pruebas=[CO + "test_login_fallido_no_reserva", ER + "test_login_fallido_no_toca_la_planilla"],
         viejo='SIN_SESION = {"msc": MSC_SIN_SESION}\n',
         nuevo='SIN_SESION = {k: MSC_SIN_SESION for k in ("one", "msc", "cma", "cosco", "hyundai", "maersk")}\n'),
]

# --- Encargo 31 · ítem 2: ONE espera, después del login, la dirección que su portal usa hoy (decisión de Marcelo,
# CICLO-cierre-de-frenos.md). ---
ONE_LOGIN = "test_clics.TestOne.test_login_espera_la_direccion_de_hoy"
ONE_GLOB = 'ONE_TRAS_LOGIN = "**://www.one-line.com/one-ecom/**"\n'

MUTACIONES += [
    # La de hasta 4948e16, o una que calza también con el login.
    dict(id="one-login-espera-la-vieja", pruebas=[ONE_LOGIN],
         viejo=ONE_GLOB, nuevo='ONE_TRAS_LOGIN = "**ecomm.one-line.com/one-ecom**"\n'),
    dict(id="one-login-cualquier-pagina", pruebas=[ONE_LOGIN],
         viejo=ONE_GLOB, nuevo='ONE_TRAS_LOGIN = "**one-line.com/**"\n'),
    # login_one no usa la constante, espera menos, o no anota que venció.
    dict(id="one-login-sin-la-constante", pruebas=[ONE_LOGIN],
         viejo="    try: page.wait_for_url(ONE_TRAS_LOGIN, timeout=25000)\n",
         nuevo='    try: page.wait_for_url("**ecomm.one-line.com/one-ecom**", timeout=25000)\n'),
    dict(id="one-login-espera-menos", pruebas=[ONE_LOGIN],
         viejo="    try: page.wait_for_url(ONE_TRAS_LOGIN, timeout=25000)\n",
         nuevo="    try: page.wait_for_url(ONE_TRAS_LOGIN, timeout=5000)\n"),
    dict(id="one-login-sin-aviso", pruebas=[ONE_LOGIN],
         viejo='    except Exception: reg.info("no confirmé redirect en 25s")\n', nuevo="    except Exception: pass\n"),
]

# --- Encargo 31 · ítem 3: CMA reconoce el aviso de mantenimiento, y sus filas quedan NO ENVIADA con «el portal de CMA
# está en mantenimiento» (decisión de Marcelo, CICLO-cierre-de-frenos.md). ---
CMA_MANT = "test_clics.TestCma.test_en_mantenimiento_la_fila_queda_no_enviada"
CMA_AVISO = "test_clics.TestCma.test_aviso_de_mantenimiento"
MIRA_MANT = ("        if _cma_en_mantenimiento(page):\n            reg.captura(page, f\"cma_f{f}_mantenimiento\")\n"
             "            return _no_enviada(reg, CMA_MANTENIMIENTO)\n")

MUTACIONES += [
    # No lo mira, como hasta 4948e16; lo mira pero sigue; o corta sin la captura.
    dict(id="cma-mant-no-mira", pruebas=[CMA_MANT], viejo=MIRA_MANT, nuevo=""),
    dict(id="cma-mant-sigue", pruebas=[CMA_MANT], viejo=MIRA_MANT,
         nuevo="        if _cma_en_mantenimiento(page):\n            reg.info(CMA_MANTENIMIENTO)\n"),
    dict(id="cma-mant-sin-captura", pruebas=[CMA_MANT],
         viejo='            reg.captura(page, f"cma_f{f}_mantenimiento")\n', nuevo=""),
    # Otro motivo, u otro estado.
    dict(id="cma-mant-otro-motivo", pruebas=[CMA_MANT],
         viejo='CMA_MANTENIMIENTO = "el portal de CMA está en mantenimiento"\n',
         nuevo='CMA_MANTENIMIENTO = "CMA en mantenimiento"\n'),
    dict(id="cma-mant-revisar", pruebas=[CMA_MANT],
         viejo="            return _no_enviada(reg, CMA_MANTENIMIENTO)\n",
         nuevo='            return ("REVISAR", CMA_MANTENIMIENTO)\n'),
    # Lo mira después de buscar el Origen: cortaría allí, como antes (desde el encargo 42, con ObjetivoNoEncontrado).
    dict(id="cma-mant-despues-del-origen", pruebas=[CMA_MANT], cambios=[
        (MIRA_MANT, ""),
        ('            raise ObjetivoNoEncontrado("Origen de CMA", _sugerencia_que_elegir(reserva["pol"]))\n',
         '            raise ObjetivoNoEncontrado("Origen de CMA", _sugerencia_que_elegir(reserva["pol"]))\n'
         + MIRA_MANT)]),
    # El ayudante: con otro texto, distinguiendo mayúsculas o saltos, o dando el aviso cuando no pudo leer.
    dict(id="cma-mant-otro-texto", pruebas=[CMA_AVISO],
         viejo='    return "we are improving the ebusiness area" in',
         nuevo='    return "we are improving" in'),
    dict(id="cma-mant-con-saltos", pruebas=[CMA_AVISO],
         viejo='" ".join(texto_pagina(page).split())\n', nuevo="texto_pagina(page)\n"),
    dict(id="cma-mant-sin-leer", pruebas=[CMA_AVISO],
         viejo='" ".join(texto_pagina(page).split())\n',
         nuevo='(" ".join(texto_pagina(page).split()) or "we are improving the ebusiness area")\n'),
]

# --- Encargo 31 · ítem 4: si la fila trae viaje y ninguna salida de la nave lo trae, MAERSK y COSCO cortan con motivo en
# vez de elegir entre todas (decisión de Marcelo, CICLO-cierre-de-frenos.md). ---
MK_VIAJE = "test_clics.TestMaersk.test_sin_el_viaje_de_la_fila_no_elige"
CO_VIAJE = "test_clics.TestCosco.test_sin_el_viaje_de_la_fila_corta"
MOTIVO_VIAJE = "test_ayudantes.TestProximaSalida.test_el_motivo_en_palabras"
MK_CORTE = '        pedidas = [s for s in de_la_nave if s.get("viaje")] if viaje_solicitado else de_la_nave\n'
CO_CORTE = ('    if _cosco_sin_el_viaje(cand, toks_todos):\n'
            '        return _cosco_itinerario_ambiguo(page, reg, reserva, cand, "sin-viaje")\n')

MUTACIONES += [
    # MAERSK: elige entre todas las de la nave, como hasta 4948e16; corta aunque la nave no esté; con otro motivo.
    dict(id="mk-viaje-elige-entre-todas", pruebas=[MK_VIAJE], viejo=MK_CORTE, nuevo="        pedidas = de_la_nave\n"),
    dict(id="mk-viaje-corta-sin-la-nave", pruebas=[MK_VIAJE],
         viejo="    if de_la_nave:\n        # El motivo de la NO ENVIADA no dice",
         nuevo="    if de_la_nave or viaje_solicitado:\n        # El motivo de la NO ENVIADA no dice"),
    dict(id="mk-viaje-otro-motivo", pruebas=[MK_VIAJE],
         viejo='"sin-viaje" if viaje_solicitado else "no-reservable"',
         nuevo='"empate" if viaje_solicitado else "no-reservable"'),
    # Filtra por el viaje aunque la fila no lo traiga (toda salida de la nave, sin la marca del viaje).
    dict(id="mk-viaje-corta-sin-viaje-en-la-fila", pruebas=["test_clics.TestMaersk.test_elige_la_proxima_salida_que_se_puede_reservar"],
         viejo='] if viaje_solicitado else de_la_nave\n', nuevo="]\n"),
    # El motivo en palabras: otro texto, o siempre en plural.
    dict(id="motivo-sin-viaje-otro-texto", pruebas=[MOTIVO_VIAJE],
         viejo='        return (f"ninguna de las {n} opciones de la nave trae el viaje de la fila" if n > 1\n',
         nuevo='        return (f"ninguna de las {n} opciones trae el viaje" if n > 1\n'),
    dict(id="motivo-sin-viaje-siempre-plural", pruebas=[MOTIVO_VIAJE],
         viejo='trae el viaje de la fila" if n > 1\n', nuevo='trae el viaje de la fila" if n > 0\n'),
    dict(id="motivo-sin-viaje-como-empate", pruebas=[MOTIVO_VIAJE],
         viejo='    if motivo == "sin-viaje":\n', nuevo='    if motivo == "sin-viaje" and not transito:\n'),
    # COSCO: elige entre los de la nave con otro viaje, como hasta 4948e16; o corta sin la lista, o con otro motivo.
    dict(id="cosco-viaje-elige-entre-todos", pruebas=[CO_VIAJE], viejo=CO_CORTE, nuevo=""),
    dict(id="cosco-viaje-sin-evidencia", pruebas=[CO_VIAJE],
         viejo='        return _cosco_itinerario_ambiguo(page, reg, reserva, cand, "sin-viaje")\n',
         nuevo='        return _no_enviada(reg, "COSCO: ningún itinerario trae el viaje")\n'),
    dict(id="cosco-viaje-otro-motivo", pruebas=[CO_VIAJE],
         viejo='        return _cosco_itinerario_ambiguo(page, reg, reserva, cand, "sin-viaje")\n',
         nuevo='        return _cosco_itinerario_ambiguo(page, reg, reserva, cand, "empate")\n'),
    # El ayudante: sin la nave también corta; o el viaje como parte del texto.
    dict(id="cosco-sin-viaje-sin-la-nave", pruebas=[CO_VIAJE],
         viejo="    return bool(cand) and not any(_cosco_trae(x, toks_todos) for x in cand)\n",
         nuevo="    return not any(_cosco_trae(x, toks_todos) for x in cand)\n"),
    dict(id="cosco-sin-viaje-como-parte", pruebas=[CO_VIAJE],
         viejo="    return bool(cand) and not any(_cosco_trae(x, toks_todos) for x in cand)\n",
         nuevo='    return bool(cand) and not any(all(t in " ".join(x.get("naves") or []) for t in toks_todos) for x in cand)\n'),
]

# --- Encargo 32 · commit 1: la búsqueda ampliada y MAERSK (decisiones de Marcelo, CICLO-ampliar-la-busqueda.md). MAERSK
# pide más salidas con «Search more sailing options» hasta encontrar la salida pedida o hasta que el portal no deje ampliar
# más, y entonces el REVISAR dice hasta qué fecha buscó; la salida pedida sin «Book» queda NO ENVIADA. ---
HASTA = "test_ayudantes.TestProximaSalida.test_hasta_donde_busque"
MK_HASTA = MK + "test_sin_nave_dice_hasta_donde_busco"
MK_NO_RES = MK + "test_la_salida_pedida_ya_no_se_puede_reservar"
MK_AMPLIA = MK + "test_amplia_hasta_que_el_portal_no_deja_mas"
MK_ANOTA = MK + "test_anota_por_que_dejo_de_ampliar"

MUTACIONES += [
    # El ayudante común: la primera salida en vez de la última; sin decir por qué; sin fechas, revienta; otro texto.
    dict(id="hasta-donde-la-primera", pruebas=[HASTA, MK_HASTA],
         viejo='busqué hasta el {max(legibles):%d-%m-%Y}', nuevo='busqué hasta el {min(legibles):%d-%m-%Y}'),
    dict(id="hasta-donde-sin-por-que", pruebas=[HASTA, MK_HASTA],
         viejo='    return f"{hasta}, y {por_que}"\n', nuevo="    return hasta\n"),
    dict(id="hasta-donde-sin-fechas-revienta", pruebas=[HASTA],
         viejo='la última salida que mostró el portal" if legibles\n',
         nuevo='la última salida que mostró el portal" if True\n'),
    dict(id="hasta-donde-otro-no-amplia", pruebas=[HASTA, MK_HASTA],
         viejo='NO_AMPLIA_MAS = "el portal no deja ampliar más la búsqueda"', nuevo='NO_AMPLIA_MAS = "no hay más"'),
    # MAERSK sin nave: el REVISAR calla hasta dónde buscó, o el reservador no se lo pasa.
    dict(id="mk-sin-nave-calla-hasta-donde", pruebas=[MK_HASTA],
         viejo='    donde = f": {_hasta_donde_busque(*busqueda)}" if busqueda else ""\n', nuevo='    donde = ""\n'),
    dict(id="mk-reserva-no-pasa-la-busqueda", pruebas=[MK + "test_sin_nave_no_llega_a_la_guarda"],
         viejo="        return _mk_sin_nave(page, reg, reserva, det, sin_nave)\n",
         nuevo="        return _mk_sin_nave(page, reg, reserva, det)\n"),
    # El motivo «no-reservable»: otro texto, o como un empate.
    dict(id="motivo-no-reservable-otro-texto", pruebas=[MOTIVO_VIAJE, MK_NO_RES],
         viejo='SALIDA_NO_RESERVABLE = "la salida pedida ya no se puede reservar"',
         nuevo='SALIDA_NO_RESERVABLE = "la salida ya no se reserva"'),
    dict(id="motivo-no-reservable-como-empate", pruebas=[MOTIVO_VIAJE, MK_NO_RES],
         viejo='    if motivo == "no-reservable":\n        return SALIDA_NO_RESERVABLE\n', nuevo=""),
    # La salida pedida sin «Book»: amplía como si no estuviera; sin viaje en la fila, otro motivo; o el motivo de siempre.
    dict(id="mk-no-reservable-amplia", pruebas=[MK_NO_RES],
         viejo=('        if viaje_solicitado and pedidas:\n'
                '            return "", (pedidas, "no-reservable", desde), None, None\n'),
         nuevo=""),
    dict(id="mk-no-reservable-sin-viaje-otro-motivo", pruebas=[MK_NO_RES],
         viejo='"sin-viaje" if viaje_solicitado else "no-reservable"',
         nuevo='"sin-viaje" if viaje_solicitado else "empate"'),
    dict(id="mk-no-reservable-motivo-de-siempre", pruebas=[MK_NO_RES],
         viejo="""    if motivo == "no-reservable":\n        return _no_enviada(reg, f"MAERSK: {por_que} ('{reserva['nave']}')")\n""",
         nuevo=""),
    # Sin el viaje de la fila, corta con el primer lote, sin ampliar (como hasta 4cae528).
    dict(id="mk-viaje-corta-sin-ampliar", pruebas=[MK_VIAJE],
         viejo="        if viaje_solicitado and pedidas:\n",
         nuevo='        if viaje_solicitado and de_la_nave and not pedidas:\n'
               '            return "", (de_la_nave, "sin-viaje", desde), None, None\n'
               '        if viaje_solicitado and pedidas:\n'),
    # Cómo amplía: sin esperar a que se habilite; con dos botones; sin esperar las salidas nuevas; sin tope; sin contar;
    # buscando otro texto.
    dict(id="mk-mas-sin-esperar", pruebas=[MK_AMPLIA],
         viejo="        listo = n == 1 and boton.is_enabled()\n", nuevo="        listo = n == 1\n"),
    dict(id="mk-mas-con-varios", pruebas=[MK_AMPLIA],
         viejo='    if n > 1:\n        return f"no pude ampliar la búsqueda: había {n} botones',
         nuevo='    if False:\n        return f"no pude ampliar la búsqueda: había {n} botones'),
    dict(id="mk-mas-sin-esperar-las-nuevas", pruebas=[MK_AMPLIA],
         viejo='        if len(_mk_leer_salidas(page, [], "", reg)) > antes:\n            return ""\n',
         nuevo='        return ""\n'),
    dict(id="mk-mas-sin-tope", pruebas=[MK_AMPLIA],
         viejo="        if ampliadas >= AMPLIAR_MAX:\n", nuevo="        if False:\n"),
    dict(id="mk-mas-tope-sin-contar", pruebas=[MK_AMPLIA],
         viejo="        ampliadas += 1\n", nuevo=""),
    # Con la nave, pero sin la salida pedida, no anota por qué dejó de ampliar (revisión del encargo 32).
    dict(id="mk-mas-no-anota-por-que", pruebas=[MK_ANOTA],
         viejo='        reg.info(f"dejé de ampliar la búsqueda: {por_que}")\n', nuevo=""),
    dict(id="mk-mas-otro-texto", pruebas=[MK_AMPLIA, ELIGE_MK],
         viejo='MK_BOTON_MAS = "Search more sailing options"', nuevo='MK_BOTON_MAS = "Search more"'),
    dict(id="mk-mas-nombre-como-parte", pruebas=[MK_AMPLIA, ELIGE_MK],
         viejo='    b = page.get_by_role("button", name=nombre, exact=True)\n',
         nuevo='    b = page.get_by_role("button", name=nombre)\n'),
]

# --- Encargo 32 · commit 2: COSCO amplía «Sailing Within» a lo más largo y vuelve a buscar si la nave, o su viaje, no
# está en lo que muestra de entrada; si tampoco aparece, el REVISAR dice hasta qué fecha buscó
# (CICLO-ampliar-la-busqueda.md). ---
CO_AMPLIA = K1 + "test_reservar_cosco_amplia_antes_de_cortar"
CO_SEMANAS = K1 + "test_amplia_sailing_within"
CO_JS_SEMANAS = K1 + "test_js_semanas_lee_el_campo_y_las_opciones"
CO_LEER = K1 + "test_leer_itinerarios_espera_los_nuevos"

MUTACIONES += [
    # El reservador: no amplía; amplía solo sin la nave (no por el viaje); no vuelve a buscar; el REVISAR calla hasta
    # dónde buscó.
    dict(id="cosco-amplia-nunca", pruebas=[CO_AMPLIA],
         viejo="        por_que = _cosco_ampliar(page, frame, reg)\n", nuevo='        por_que = "no amplío"\n'),
    dict(id="cosco-amplia-solo-sin-la-nave", pruebas=[CO_AMPLIA],
         viejo="        if ampliada or (cand and not _cosco_sin_el_viaje(cand, toks_todos)):\n",
         nuevo="        if ampliada or cand:\n"),
    dict(id="cosco-amplia-sin-buscar-de-nuevo", pruebas=[CO_AMPLIA],
         viejo='        _cosco_click_btn(frame, "search service", reg)\n        esperar(page, 2.0)\n',
         nuevo="        esperar(page, 2.0)\n"),
    dict(id="cosco-amplia-calla-por-que-no", pruebas=[CO_AMPLIA],
         viejo='            reg.info(f"no amplié la búsqueda: {por_que}")\n', nuevo=""),
    dict(id="cosco-amplia-sin-parar", pruebas=[CO_AMPLIA],
         viejo="        ampliada, por_que = True, NO_AMPLIA_MAS\n", nuevo="        por_que = NO_AMPLIA_MAS\n"),
    dict(id="cosco-revisar-calla-hasta-donde", pruebas=[CO_AMPLIA],
         viejo='        donde = "" if cand else f": {_hasta_donde_busque([d for d, _ in _cosco_salidas(filas)], por_que)}"\n',
         nuevo='        donde = ""\n'),
    # La ampliación: sin mirar si ya está en la más larga; sin verificar que quedó; con clic sintético; con varios campos.
    dict(id="cosco-ampliar-sin-mirar-el-tope", pruebas=[CO_SEMANAS],
         viejo='    if r.get("mayor") is not None and r["mayor"] <= antes:\n        return NO_AMPLIA_MAS\n', nuevo=""),
    dict(id="cosco-ampliar-sin-verificar", pruebas=[CO_SEMANAS],
         viejo='    if quedo != r["mayor"]:\n', nuevo="    if False:\n"),
    dict(id="cosco-ampliar-clic-sintetico", pruebas=[CO_SEMANAS],
         viejo='        frame.click("[data-aq-semanas]", timeout=4000)\n',
         nuevo='        frame.evaluate("() => document.querySelector(\'[data-aq-semanas]\').click()")\n'),
    dict(id="cosco-ampliar-varios-campos", pruebas=[CO_SEMANAS],
         viejo='    if r.get("campos") != 1:\n        return f"no pude ampliar la búsqueda: había {r.get(\'campos\', 0)} campos',
         nuevo='    if not r.get("campos"):\n        return f"no pude ampliar la búsqueda: había {r.get(\'campos\', 0)} campos'),
    dict(id="cosco-ampliar-no-mira-la-marca", pruebas=[CO_SEMANAS],
         viejo='        if not r.get("marcada"):\n', nuevo="        if False:\n"),
    # El JavaScript: la opción más corta; sin mirar si el campo o la opción se ven; cualquier «N Weeks».
    dict(id="cosco-semanas-la-menor", pruebas=[CO_JS_SEMANAS],
         viejo="               mayor: Math.max(...opciones", nuevo="               mayor: Math.min(...opciones"),
    dict(id="cosco-semanas-campo-oculto", pruebas=[CO_JS_SEMANAS],
         viejo="        .filter(e => vis(e) && listas.some(u => e.getAttribute('aria-controls') === u.id));",
         nuevo="        .filter(e => listas.some(u => e.getAttribute('aria-controls') === u.id));"),
    dict(id="cosco-semanas-opcion-oculta", pruebas=[CO_JS_SEMANAS],
         viejo="        const la = opciones.filter(li => vis(li) && semanas(li.textContent) === r.mayor);",
         nuevo="        const la = opciones.filter(li => semanas(li.textContent) === r.mayor);"),
    # Encargo 32 · commit 6: el campo por su lista y la elegida por su marca. Una lista mezclada cuenta; sin la marca de
    # clase o sin aria-selected; el campo por su valor, como en el commit anterior; sin mirar si hay una elegida.
    dict(id="cosco-semanas-lista-mezclada", pruebas=[CO_JS_SEMANAS],
         viejo="lis.every(li => rx.test(li.textContent || ''))", nuevo="lis.some(li => rx.test(li.textContent || ''))"),
    dict(id="cosco-semanas-sin-la-clase", pruebas=[CO_JS_SEMANAS],
         viejo="li.classList.contains('selected')\n        || li.getAttribute", nuevo="li.getAttribute"),
    dict(id="cosco-semanas-sin-aria", pruebas=[CO_JS_SEMANAS],
         viejo="\n        || li.getAttribute('aria-selected') === 'true');", nuevo=");"),
    dict(id="cosco-semanas-por-el-valor", pruebas=[CO_JS_SEMANAS],
         viejo="        .filter(e => vis(e) && listas.some(u => e.getAttribute('aria-controls') === u.id));",
         nuevo="        .filter(e => vis(e) && rx.test(e.value || ''));"),
    dict(id="cosco-ampliar-sin-la-elegida", pruebas=[CO_SEMANAS],
         viejo='    if antes is None:\n        return "no pude ampliar la búsqueda: no pude leer qué opción de «Sailing Within» está elegida"\n',
         nuevo=""),
    dict(id="cosco-semanas-cualquier-texto", pruebas=[CO_JS_SEMANAS],
         viejo="    const rx = /^\\\\s*Sailing Within (\\\\d+) Weeks?\\\\s*$/i;",
         nuevo="    const rx = /(\\\\d+) Weeks?\\\\s*$/i;"),
    # La lectura después de ampliar: no espera los itinerarios nuevos.
    dict(id="cosco-leer-no-espera-los-nuevos", pruebas=[CO_LEER],
         viejo="        if filas and len(filas) > antes:\n", nuevo="        if filas:\n"),
]

# --- Encargo 32 · commit 3: ONE decía hasta qué fecha buscó (CICLO-ampliar-la-busqueda.md). Encargo 33 · commit 1: ONE no
# pasa de 8 semanas; se quitaron su ampliación y sus mutaciones (CICLO-ampliar-msc-y-cma.md). ---
ON_NO_AMPLIA = ON + "test_reservar_one_no_amplia"
ON_FECHAS = ON + "test_fechas_de_todas_las_tarjetas"

MUTACIONES += [
    # El reservador: vuelve a leer las tarjetas si no está; el REVISAR calla hasta dónde buscó, o dice otro motivo;
    # «hay nave» después del filtro; otro texto del motivo.
    dict(id="one-vuelve-a-buscar", pruebas=[ON_NO_AMPLIA],
         viejo="    hay_nave = bool(tarjetas)\n",
         nuevo="    if not tarjetas:\n        tarjetas = _one_tarjetas(page, reg, reserva[\"nave\"])\n    hay_nave = bool(tarjetas)\n"),
    dict(id="one-revisar-calla-hasta-donde", pruebas=[ON_NO_AMPLIA],
         viejo="""        donde = "" if hay_nave else f": {_hasta_donde_busque(_one_fechas(page), ONE_SOLO_8)}"\n""",
         nuevo='        donde = ""\n'),
    dict(id="one-revisar-otro-motivo", pruebas=[ON_NO_AMPLIA],
         viejo="_hasta_donde_busque(_one_fechas(page), ONE_SOLO_8)", nuevo="_hasta_donde_busque(_one_fechas(page), NO_AMPLIA_MAS)"),
    dict(id="one-hay-nave-despues-del-filtro", pruebas=[ON_NO_AMPLIA],
         viejo="    hay_nave = bool(tarjetas)\n",
         nuevo="    hay_nave = bool([t for t in tarjetas if t.get(\"botones\") == 1])\n"),
    dict(id="one-solo-8-otro-texto", pruebas=[ON_NO_AMPLIA],
         viejo='ONE_SOLO_8 = "no amplío más allá de las 8 semanas', nuevo='ONE_SOLO_8 = "no amplío más allá de 8 semanas'),
    # Las fechas de todas las tarjetas: solo las de la nave; la última fecha en vez de la salida.
    dict(id="one-fechas-la-llegada", pruebas=[ON_FECHAS],
         viejo="        .find(x => /^\\\\d{4}-\\\\d{2}-\\\\d{2}$/.test(x)) || '')",
         nuevo="        .filter(x => /^\\\\d{4}-\\\\d{2}-\\\\d{2}$/.test(x)).pop() || '')"),
    dict(id="one-fechas-sin-convertir", pruebas=[ON_FECHAS],
         viejo='    return [d for d, _ in _one_salidas([{"salida": t} for t in textos])]\n', nuevo="    return textos\n"),
]

# --- Encargo 32 · commit 4: HYUNDAI calza la nave con su «1st Vessel», amplía «Duration» si no está, elige la próxima
# salida entre las que la traen, y si tampoco aparece, el REVISAR dice hasta qué fecha buscó
# (decisiones de Marcelo, CICLO-ampliar-la-busqueda.md). ---
TH_JS = TH + "test_js_tarjetas_con_su_1st_vessel"
TH_DIR = TH + "test_prefiere_la_directa"
TH_JS_DIR = TH + "test_js_directa_o_con_transbordo"
TH_CLIC = TH + "test_js_clic_en_la_tarjeta_elegida"
TH_DUR_JS = TH + "test_js_duration"
TH_ELIGE = TH + "test_elige_la_1st_vessel_y_la_proxima_salida"
TH_AMPLIA = TH + "test_amplia_duration_si_no_esta"
TH_DUR = TH + "test_duration_elige_la_mas_larga"
TH_TT = TH + "test_transito_y_salidas"
TH_RES = TH + "test_reservar_hyundai_elige_con_su_1st_vessel"

MUTACIONES += [
    # El JavaScript de las tarjetas: con toda la tarjeta, o con «Main Vessel»; la tarjeta hasta la lista; la llegada; la
    # disponibilidad; el «Book Now» oculto.
    dict(id="hmm-calza-con-toda-la-tarjeta", pruebas=[TH_JS],
         viejo="        const primera = campo(card, '1st vessel');\n",
         nuevo="        const primera = (card.textContent || '').replace(/\\\\s+/g, ' ');\n"),
    dict(id="hmm-calza-con-main-vessel", pruebas=[TH_JS],
         viejo="campo(card, '1st vessel')", nuevo="campo(card, 'main vessel')"),
    # Sube hasta la lista: sin exigir un solo «Book Now» y sin el tope del li (las dos piezas se tapan entre sí).
    dict(id="hmm-tarjeta-hasta-la-lista", pruebas=[TH_JS], cambios=[
        ("               && [...card.parentElement.querySelectorAll('button, a')].filter(esBook).length === 1) {",
         "               && [...card.parentElement.querySelectorAll('button, a')].filter(esBook).length > 0) {"),
        ("        while (card.tagName !== 'LI' && card.parentElement", "        while (card.parentElement")]),
    dict(id="hmm-tarjeta-pasa-del-li", pruebas=[TH_JS],
         viejo="        while (card.tagName !== 'LI' && card.parentElement", nuevo="        while (card.parentElement"),
    dict(id="hmm-tarjeta-llegada-la-salida", pruebas=[TH_JS],
         viejo="        const llegada = fechas.length === 2 ? fechas[1] : '';",
         nuevo="        const llegada = fechas.length === 2 ? fechas[0] : '';"),
    dict(id="hmm-tarjeta-siempre-disponible", pruebas=[TH_JS],
         viejo="                disponible: isAvail(card), book:", nuevo="                disponible: true, book:"),
    dict(id="hmm-tarjeta-book-oculto", pruebas=[TH_JS],
         viejo="    return [...document.querySelectorAll('button, a')].filter(b => vis(b) && esBook(b)).map((btn, i) => {",
         nuevo="    return [...document.querySelectorAll('button, a')].filter(b => esBook(b)).map((btn, i) => {"),
    # El clic: el primero, o contando los ocultos.
    dict(id="hmm-clic-el-primero", pruebas=[TH_CLIC],
         viejo="        .filter(x => vis(x) && /^\\\\s*book\\\\s*now\\\\s*$/i.test(x.textContent || ''))[args.i];",
         nuevo="        .filter(x => vis(x) && /^\\\\s*book\\\\s*now\\\\s*$/i.test(x.textContent || ''))[0];"),
    dict(id="hmm-clic-cuenta-ocultos", pruebas=[TH_CLIC],
         viejo="        .filter(x => vis(x) && /^\\\\s*book\\\\s*now\\\\s*$/i.test(x.textContent || ''))[args.i];",
         nuevo="        .filter(x => /^\\\\s*book\\\\s*now\\\\s*$/i.test(x.textContent || ''))[args.i];"),
    # Al pulsar, vuelve a leer la tarjeta (revisión del encargo 32): no la vuelve a mirar; acepta otra salida, otra nave o
    # una cerrada; el reservador no le pasa la nave o la salida.
    dict(id="hmm-clic-sin-releer", pruebas=[TH_CLIC],
         viejo="    if (!t || !t.calza || !t.disponible || t.salida !== args.salida || t.directa !== args.directa) return false;\n",
         nuevo=""),
    dict(id="hmm-clic-otra-salida", pruebas=[TH_CLIC],
         viejo=" || !t.disponible || t.salida !== args.salida ||", nuevo=" || !t.disponible ||"),
    dict(id="hmm-clic-otra-directa", pruebas=[TH_CLIC],
         viejo=" || t.directa !== args.directa) return false;\n    const vis", nuevo=") return false;\n    const vis"),
    dict(id="hmm-clic-otra-nave", pruebas=[TH_CLIC], viejo="    if (!t || !t.calza || !t.disponible ||",
         nuevo="    if (!t || !t.disponible ||"),
    dict(id="hmm-clic-cerrada", pruebas=[TH_CLIC], viejo=" || !t.calza || !t.disponible || t.salida",
         nuevo=" || !t.calza || t.salida"),
    dict(id="hmm-clic-sin-la-nave", pruebas=[TH + "test_elige_la_1st_vessel_y_la_proxima_salida"],
         viejo='_JS_HMM_CLIC_TARJETA, {"i": elegida["i"], "toks": toks,', nuevo='_JS_HMM_CLIC_TARJETA, {"i": elegida["i"], "toks": [],'),
    dict(id="hmm-clic-sin-la-salida", pruebas=[TH + "test_elige_la_1st_vessel_y_la_proxima_salida"],
         viejo='"toks": toks,\n                                                          "salida": elegida.get("salida", ""),\n',
         nuevo='"toks": toks,\n                                                          "salida": "",\n'),
    dict(id="hmm-clic-sin-la-directa", pruebas=[TH + "test_prefiere_la_directa"],
         viejo='"directa": elegida.get("directa")}))\n        if not pulso:', nuevo='"directa": None}))\n        if not pulso:'),
    # «Duration» en JavaScript: siempre a la vista; la primera opción como elegida.
    dict(id="hmm-duration-siempre-visible", pruebas=[TH_DUR_JS],
         viejo="    return {visible: s.offsetParent !== null, actual:", nuevo="    return {visible: true, actual:"),
    dict(id="hmm-duration-la-primera", pruebas=[TH_DUR_JS],
         viejo="    const elegida = s.options[s.selectedIndex];", nuevo="    const elegida = s.options[0];"),
    # La elección: la primera en la página; sin tránsito; sin mirar si se puede reservar; sin pulsar.
    dict(id="hmm-elige-la-primera", pruebas=[TH_ELIGE],
         viejo="    elegida, motivo = _proxima_salida(_hmm_salidas(disponibles), desde, _hmm_transito)\n",
         nuevo='    elegida, motivo = disponibles[0], ""\n'),
    dict(id="hmm-elige-sin-transito", pruebas=[TH_ELIGE],
         viejo="    elegida, motivo = _proxima_salida(_hmm_salidas(disponibles), desde, _hmm_transito)\n",
         nuevo="    elegida, motivo = _proxima_salida(_hmm_salidas(disponibles), desde)\n"),
    dict(id="hmm-elige-cerradas", pruebas=[TH_ELIGE],
         viejo='    disponibles = [t for t in de_la_nave if t.get("disponible") and t.get("book") == 1]\n',
         nuevo="    disponibles = de_la_nave\n"),
    dict(id="hmm-elige-sin-la-interfaz-anterior", pruebas=[TH_ELIGE],
         viejo="    if not tarjetas:\n        return _hmm_indice_anterior(page, toks, reg)\n",
         nuevo='    if not tarjetas:\n        return {"idx": -1, "motivo": "no_encontrada"}\n'),
    dict(id="hmm-sin-anotar-el-desempate",
         pruebas=[TH_ELIGE, "test_ayudantes.TestProximaSalida.test_cada_naviera_anota_el_desempate"],
         viejo="        _anotar_desempate(reg, _hmm_salidas(disponibles), desde, _hmm_transito)\n", nuevo=""),
    # La ampliación: nunca; sin buscar de nuevo; sin la evidencia de la lista ampliada; sin decir hasta dónde.
    dict(id="hmm-amplia-nunca", pruebas=[TH_AMPLIA],
         viejo="        por_que = _hmm_ampliar(page, reg)\n", nuevo='        por_que = "no amplío"\n'),
    dict(id="hmm-amplia-sin-buscar", pruebas=[TH_AMPLIA],
         viejo='            if not _hmm_realclick(page, "Retrieve", reg, "buscar itinerarios"):\n'
               '                _hmm_next(page, "retrieve", reg, "buscar itinerarios (js)")\n'
               '            tarjetas = _hmm_leer_tarjetas(page, toks, reg, antes=len(tarjetas))\n',
         nuevo=""),
    dict(id="hmm-amplia-sin-evidencia", pruebas=[TH_AMPLIA, LD + "test_solo_ahi"],
         viejo='            _evidencia_antes_de_la_guarda(page, reg, f"hmm_f{reserva[\'fila\']}_naves_mas",\n'
               '                                          "en la lista ampliada de naves", completa=False)\n',
         nuevo=""),
    dict(id="hmm-amplia-calla-hasta-donde", pruebas=[TH_AMPLIA],
         viejo='        return {"idx": -1, "motivo": "no_encontrada", "busqueda": (fechas, por_que)}\n',
         nuevo='        return {"idx": -1, "motivo": "no_encontrada", "busqueda": ([], por_que)}\n'),
    # «Duration»: sin mirar si ya está en la más larga; la más corta; sin verificar.
    dict(id="hmm-duration-sin-mirar-el-tope", pruebas=[TH_DUR, TH_AMPLIA],
         viejo='    if mayor["n"] <= r["actual"]:\n        return NO_AMPLIA_MAS\n', nuevo=""),
    dict(id="hmm-duration-la-mas-corta", pruebas=[TH_DUR],
         viejo='    mayor = max(r["opciones"], key=lambda o: o["n"])\n', nuevo='    mayor = min(r["opciones"], key=lambda o: o["n"])\n'),
    dict(id="hmm-duration-sin-verificar", pruebas=[TH_DUR],
         viejo='    if quedo != mayor["n"]:\n', nuevo="    if False:\n"),
    # El tránsito y las salidas.
    dict(id="hmm-transito-al-reves", pruebas=[TH_TT],
         viejo="    return tiempo if tiempo > datetime.timedelta(0) else None\n", nuevo="    return tiempo\n"),
    dict(id="hmm-salidas-sin-fecha-revienta", pruebas=[TH_TT],
         viejo="        except ValueError:\n            out.append((None, t))\n",
         nuevo="        except KeyError:\n            out.append((None, t))\n"),
    # El reservador: sin cortar con una sola salida; el REVISAR calla hasta dónde.
    dict(id="hmm-reserva-sin-corte", pruebas=[TH_RES],
         viejo='    if res_nave.get("corte"):\n        return res_nave["corte"]\n', nuevo=""),
    dict(id="hmm-reserva-calla-hasta-donde", pruebas=[TH_RES],
         viejo="""            donde = f": {_hasta_donde_busque(*res_nave['busqueda'])}" if res_nave.get("busqueda") else ""\n""",
         nuevo='            donde = ""\n'),
]

# --- Encargo 33 · commit 2: HYUNDAI prefiere la directa entre las salidas del mismo día con la nave de la fila; solo si
# todas tienen transbordo, decide el tránsito (CICLO-ampliar-msc-y-cma.md). ---
MUTACIONES += [
    # La preferencia: no se aplica; la que no dice cuenta como directa; en cualquier día; calla; descarta las directas;
    # descarta aunque todas sean directas.
    dict(id="hmm-directa-no-se-aplica", pruebas=[TH_DIR],
         viejo="    disponibles = _directas_primero(disponibles, desde, reg, _hmm_salidas)\n", nuevo=""),
    dict(id="hmm-directa-desconocida-cuenta", pruebas=[TH_DIR],
         viejo='    directas = [t for t in del_dia if t.get("directa") is True]\n',
         nuevo='    directas = [t for t in del_dia if t.get("directa") is not False]\n'),
    dict(id="hmm-directa-en-cualquier-dia", pruebas=[TH_DIR],
         viejo="    del_dia = [t for f, t in futuras if f == dia]\n", nuevo="    del_dia = [t for f, t in futuras]\n"),
    dict(id="hmm-directa-calla", pruebas=[TH_DIR],
         viejo='    reg.info(f"{len(del_dia)} salidas de la nave salen el {dia:%d-%m-%Y}: prefiero "',
         nuevo='    (f"{len(del_dia)} salidas de la nave salen el {dia:%d-%m-%Y}: prefiero "'),
    dict(id="hmm-directa-descarta-las-directas", pruebas=[TH_DIR],
         viejo='    descartadas = [t for t in del_dia if t.get("directa") is not True]\n',
         nuevo='    descartadas = [t for t in del_dia if t.get("directa") is True]\n'),
    dict(id="hmm-directa-aunque-todas", pruebas=[TH_DIR],
         viejo="    if not directas or len(directas) == len(del_dia):\n", nuevo="    if not directas:\n"),
    # El JavaScript: «direct» como parte del texto; con varios .mid-state, el primero; sin recortar; el transbordo no
    # se lee.
    dict(id="hmm-js-directa-por-parte", pruebas=[TH_JS_DIR],
         viejo="(e.textContent || '').trim());\n        const directa = tipo.length !== 1 ? null : /^direct$/i.test(tipo[0])",
         nuevo="(e.textContent || '').trim());\n        const directa = tipo.length !== 1 ? null : /direct/i.test(tipo[0])"),
    dict(id="hmm-js-directa-varias", pruebas=[TH_JS_DIR],
         viejo="(e.textContent || '').trim());\n        const directa = tipo.length !== 1 ? null :",
         nuevo="(e.textContent || '').trim());\n        const directa = !tipo.length ? null :"),
    dict(id="hmm-js-directa-sin-recortar", pruebas=[TH_JS_DIR],
         viejo=".map(e => (e.textContent || '').trim());\n        const directa",
         nuevo=".map(e => e.textContent || '');\n        const directa"),
    dict(id="hmm-js-transbordo-no-se-lee", pruebas=[TH_JS_DIR],
         viejo=": /^transshipment$/i.test(tipo[0]) ? false : null;\n        return {i: i, primera:",
         nuevo=": null;\n        return {i: i, primera:"),
]

# --- Encargo 33 · commit 3: MSC baja por la lista (no es un clic) si la nave no está, hasta encontrarla o hasta que no
# lleguen tarjetas nuevas; si no aparece, el REVISAR dice hasta qué fecha buscó (CICLO-ampliar-msc-y-cma.md). ---
MS_BAJA = MS + "test_reservar_msc_baja_si_no_esta"
MS_BAJAR = MS + "test_baja_por_la_lista"
MS_JS_BAJAR = MS + "test_js_bajar"

MUTACIONES += [
    # El reservador: no baja; sin tope; el REVISAR calla hasta dónde buscó.
    dict(id="msc-no-baja", pruebas=[MS_BAJA],
         viejo='    while not any(x.get("sel") and _trae_la_nave(_norm(x.get("nave")), toks) for x in naves):\n',
         nuevo="    while False:\n"),
    dict(id="msc-baja-sin-tope", pruebas=[MS_BAJA],
         viejo="        if bajadas >= AMPLIAR_MAX:\n            por_que = f\"bajé por la lista",
         nuevo="        if False:\n            por_que = f\"bajé por la lista"),
    dict(id="msc-revisar-calla-hasta-donde", pruebas=[MS_BAJA],
         viejo="""        donde = "" if exacta else f": {_hasta_donde_busque([_msc_fecha_etd(n.get('etd')) for n in naves], por_que)}"\n""",
         nuevo='        donde = ""\n'),
    # Bajar: con las mismas tarjetas ya cuenta; sin mirar si encontró la lista; una sola espera.
    dict(id="msc-bajar-con-las-mismas", pruebas=[MS_BAJAR],
         viejo="        if n > antes:\n            reg.info(f\"búsqueda ampliada: {antes} -> {n} itinerarios\")",
         nuevo="        if n >= antes:\n            reg.info(f\"búsqueda ampliada: {antes} -> {n} itinerarios\")"),
    dict(id="msc-bajar-sin-mirar-la-lista", pruebas=[MS_BAJAR],
         viejo="        if not page.evaluate(_JS_MSC_BAJAR):\n", nuevo="        if not page.evaluate(_JS_MSC_BAJAR) and False:\n"),
    dict(id="msc-bajar-una-sola-espera", pruebas=[MS_BAJAR],
         viejo="    for _ in range(MSC_ESPERA_MAS):\n", nuevo="    for _ in range(1):\n"),
    # El JavaScript: no baja la lista; no baja la ventana; no dice cuántas había.
    dict(id="msc-js-bajar-sin-la-lista", pruebas=[MS_JS_BAJAR],
         viejo="        if(e.scrollHeight>e.clientHeight) e.scrollTop=e.scrollHeight;\n", nuevo=""),
    dict(id="msc-js-bajar-sin-la-ventana", pruebas=[MS_JS_BAJAR],
         viejo="    window.scrollTo(0, document.documentElement.scrollHeight);\n    return cards.length;",
         nuevo="    return cards.length;"),
    dict(id="msc-js-bajar-cuenta-mal", pruebas=[MS_JS_BAJAR],
         viejo="    window.scrollTo(0, document.documentElement.scrollHeight);\n    return cards.length;",
         nuevo="    window.scrollTo(0, document.documentElement.scrollHeight);\n    return 1;"),
]

# --- Encargo 33 · commit 4: CMA pulsa «Cargar N siguientes resultados», por su texto, hasta encontrar la nave o hasta que
# el enlace desaparezca, y el aviso dice hasta qué fecha buscó (CICLO-ampliar-msc-y-cma.md). ---
C_CARGA = C1 + "test_itinerario_carga_mas_hasta_encontrarla"
C_CARGAR = C1 + "test_cargar_mas_por_su_texto"
C_FECHAS = C1 + "test_fechas_de_las_rutas"
C_CONTAR = C1 + "test_js_contar_rutas"
RC_CARGA = RC + "test_y_otra_tras_cada_carga"
RC_FIN = RC + "test_hasta_que_el_enlace_desaparece"

MUTACIONES += [
    # El bucle: no carga más; sin tope; carga aunque la fila no traiga palabras; el aviso calla hasta dónde buscó.
    dict(id="cma-no-carga-mas", pruebas=[C_CARGA, RC_CARGA],
         viejo="        por_que = _cma_ampliar(page, reg, _cma_contar_rutas(page))\n", nuevo="        por_que = NO_AMPLIA_MAS\n"),
    dict(id="cma-carga-sin-tope", pruebas=[C_CARGA],
         viejo="        if cargas >= AMPLIAR_MAX:\n", nuevo="        if False:\n"),
    dict(id="cma-carga-sin-palabras", pruebas=[C_CARGA],
         viejo='        if not toks:\n            por_que = "la fila no trae palabras de nave que buscar"\n            break\n',
         nuevo=""),
    dict(id="cma-aviso-calla-hasta-donde", pruebas=[C_CARGA, RC_FIN],
         viejo="    donde = _hasta_donde_busque(_cma_fechas(page), por_que)\n", nuevo='    donde = ""\n'),
    # El enlace: cualquier texto con «Cargar»; sin el número; también los ocultos; sin mirar si hay uno solo.
    dict(id="cma-cargar-cualquier-texto", pruebas=[C_CARGAR],
         viejo='CMA_CARGAR_MAS = r"^\\s*Cargar\\s+\\d+\\s+siguientes\\s+resultados\\s*$"',
         nuevo='CMA_CARGAR_MAS = r"Cargar"'),
    dict(id="cma-cargar-sin-numero", pruebas=[C_CARGAR],
         viejo='CMA_CARGAR_MAS = r"^\\s*Cargar\\s+\\d+\\s+siguientes',
         nuevo='CMA_CARGAR_MAS = r"^\\s*Cargar\\s+(\\d+\\s+)?siguientes'),
    dict(id="cma-cargar-sin-el-final", pruebas=[C_CARGAR],
         viejo='siguientes\\s+resultados\\s*$"', nuevo='siguientes\\s+resultados"'),
    dict(id="cma-cargar-tambien-ocultos", pruebas=[C_CARGAR],
         viejo="    vistos = [e.nth(j) for j in range(e.count()) if e.nth(j).is_visible()]\n",
         nuevo="    vistos = [e.nth(j) for j in range(e.count())]\n"),
    dict(id="cma-cargar-con-varios", pruebas=[C_CARGAR],
         viejo="    return (vistos[0] if len(vistos) == 1 else None, len(vistos))\n",
         nuevo="    return (vistos[0] if vistos else None, 1 if vistos else 0)\n"),
    # La espera: con las mismas rutas ya cuenta; una sola; el clic que falla sigue.
    dict(id="cma-cargar-con-las-mismas", pruebas=[C_CARGAR],
         viejo="        if rutas > antes:\n", nuevo="        if rutas >= antes:\n"),
    dict(id="cma-cargar-una-sola-espera", pruebas=[C_CARGAR],
         viejo="    for _ in range(CMA_ESPERA_MAS):\n", nuevo="    for _ in range(1):\n"),
    # Los motivos (revisión del informe): los dos cortes con el mismo texto de antes.
    dict(id="cma-cargar-sin-enlace-generico", pruebas=[C_CARGAR, RC_FIN],
         viejo="        return CMA_SIN_ENLACE\n", nuevo="        return NO_AMPLIA_MAS\n"),
    dict(id="cma-cargar-sin-rutas-generico", pruebas=[C_CARGAR],
         viejo='    return f"pulsé «Cargar … siguientes resultados» y no llegaron rutas nuevas en {CMA_ESPERA_MAS} s"\n',
         nuevo="    return NO_AMPLIA_MAS\n"),
    dict(id="cma-cargar-falla-y-sigue", pruebas=[C_CARGAR],
         viejo='        return f"no pude ampliar la búsqueda: el clic en «Cargar … siguientes resultados» falló ({str(e)[:50]})"\n',
         nuevo="        pass\n"),
    # Las fechas: el mes en inglés; la última fecha de la tarjeta; las que no existen.
    dict(id="cma-fecha-meses-en-ingles", pruebas=[C_FECHAS],
         viejo="    if not m or m.group(2).upper()[:3] not in _MESES_ES:\n        return None\n    try:\n"
               "        return datetime.date(int(m.group(3)), _MESES_ES.index(",
         nuevo="    if not m or m.group(2).upper()[:3] not in _MESES_EN:\n        return None\n    try:\n"
               "        return datetime.date(int(m.group(3)), _MESES_EN.index("),
    dict(id="cma-fechas-la-ultima", pruebas=[C_FECHAS],
         viejo="    const d = c.querySelector('.date');\n", nuevo="    const d = [...c.querySelectorAll('.date')].pop();\n"),
    dict(id="cma-fecha-sin-try", pruebas=[C_FECHAS],
         viejo="        return datetime.date(int(m.group(3)), _MESES_ES.index(m.group(2).upper()[:3]) + 1, int(m.group(1)))\n"
               "    except ValueError:\n        return None\n",
         nuevo="        return datetime.date(int(m.group(3)), _MESES_ES.index(m.group(2).upper()[:3]) + 1, int(m.group(1)))\n"
               "    except KeyError:\n        return None\n"),
    # Contar: también las ocultas; cualquier texto con «seleccionar».
    dict(id="cma-contar-ocultas", pruebas=[C_CONTAR],
         viejo="    return e.offsetParent !== null && r.width > 0 && r.height > 0\n        && /^\\s*(seleccionar|select|deseleccionar",
         nuevo="    return true\n        && /^\\s*(seleccionar|select|deseleccionar"),
    dict(id="cma-contar-cualquier-texto", pruebas=[C_CONTAR],
         viejo="/^\\s*(seleccionar|select|deseleccionar|deselect)\\s*$/i.test((e.textContent || '').trim());\n}).length",
         nuevo="/(seleccionar|select|deseleccionar|deselect)/i.test((e.textContent || '').trim());\n}).length"),
]

# --- Encargo 34 · commit 1: el «Book» de MAERSK se cuenta por su atributo label, porque su texto está dentro de la raíz
# shadow del mc-button (medido en los 6 mk_f*_detenida.html; CICLO-one-y-maersk-eligen-la-nave.md). ---
MK_BOOK = MK + "test_js_book_por_su_label"
MK_BOOK_ANCLA = ".test((b.getAttribute && b.getAttribute('label')) || b.textContent || '');"
MUTACIONES += [
    # Solo por el texto, como hasta el encargo 34 (0 en todas); solo por el label (el texto deja de contar).
    dict(id="mk-book-solo-por-texto", pruebas=[MK_BOOK, MK + "test_js_salidas_lee_la_salida_y_si_se_puede_reservar"],
         viejo=MK_BOOK_ANCLA, nuevo=".test(b.textContent || '');"),
    dict(id="mk-book-solo-por-label", pruebas=[MK_BOOK],
         viejo=MK_BOOK_ANCLA, nuevo=".test((b.getAttribute && b.getAttribute('label')) || '');"),
]

# --- Encargo 34 · commit 2: ONE prefiere la directa entre las salidas del mismo día (la regla de HYUNDAI, decisión de
# Marcelo), y su clic vuelve a leer la tarjeta elegida (CICLO-one-y-maersk-eligen-la-nave.md). ---
ON_DIR = ON + "test_prefiere_la_directa"
ON_JS_DIR = ON + "test_js_directa_o_con_transbordo"
ON_CLIC = ON + "test_js_clic_solo_el_boton_de_la_tarjeta_elegida"
ON_ELIGE = ON + "test_reservar_one_elige_la_proxima_salida"
ON_LLAMA = "    tarjetas = _directas_primero(tarjetas, desde, reg, _one_salidas)\n"
ON_ELEGIDA = ('    elegida, motivo = _proxima_salida(_one_salidas(tarjetas), desde, _one_transito) if tarjetas else '
              '(None, "")\n')
ON_RELEE = "    if (!t || t.salida !== args.salida || t.directa !== args.directa) return false;\n    const i = args.i;"
ON_TIPO = "            .map(e => (e.textContent||'').trim());\n        const directa = tipo.length !== 1 ? null :"
ON_DIRECTA = ("        const directa = tipo.length !== 1 ? null : /^direct$/i.test(tipo[0]) ? true\n"
              "            : /^transshipment$/i.test(tipo[0]) ? false : null;\n        return {i: i, calza: !!calza,")
MUTACIONES += [
    # reservar_one: sin la directa primero; o después de elegir.
    dict(id="one-directa-no-se-aplica", pruebas=[ON_ELIGE], viejo=ON_LLAMA, nuevo=""),
    dict(id="one-directa-despues-de-elegir", pruebas=[ON_ELIGE],
         cambios=[(ON_LLAMA, ""), (ON_ELEGIDA, ON_ELEGIDA + ON_LLAMA)]),
    # El ayudante común, con ONE: la que no dice cuenta como directa; en cualquier día; calla.
    dict(id="one-directa-desconocida-cuenta", pruebas=[ON_DIR],
         viejo='    directas = [t for t in del_dia if t.get("directa") is True]\n',
         nuevo='    directas = [t for t in del_dia if t.get("directa") is not False]\n'),
    dict(id="one-directa-en-cualquier-dia", pruebas=[ON_DIR],
         viejo="    del_dia = [t for f, t in futuras if f == dia]\n", nuevo="    del_dia = [t for f, t in futuras]\n"),
    dict(id="one-directa-calla", pruebas=[ON_DIR],
         viejo='    reg.info(f"{len(del_dia)} salidas de la nave salen el {dia:%d-%m-%Y}: prefiero "',
         nuevo='    (f"{len(del_dia)} salidas de la nave salen el {dia:%d-%m-%Y}: prefiero "'),
    # El JavaScript de las tarjetas: sin el elemento que lo dice; el primero de varios; cualquier texto con «direct»; sin
    # devolverla.
    dict(id="one-js-directa-sin-su-elemento", pruebas=[ON_JS_DIR],
         viejo="c.querySelectorAll(\"[class*='TransshipmentInfo_transshipment-container']\")",
         nuevo="c.querySelectorAll(\"[class*='TransshipmentInfo_no-existe']\")"),
    dict(id="one-js-directa-el-primero", pruebas=[ON_JS_DIR],
         viejo=ON_TIPO, nuevo=ON_TIPO.replace("tipo.length !== 1 ? null", "tipo.length < 1 ? null")),
    dict(id="one-js-directa-cualquier-texto", pruebas=[ON_JS_DIR],
         viejo=ON_DIRECTA, nuevo=ON_DIRECTA.replace("/^direct$/i", "/direct/i")),
    dict(id="one-js-sin-directa", pruebas=[ON_JS_DIR, ON + "test_js_tarjetas_de_la_nave_con_su_salida"],
         viejo="                directa: directa};\n    }).filter(x => x.calza);",
         nuevo="                };\n    }).filter(x => x.calza);"),
    # El clic: sin volver a leer la tarjeta; sin mirar si es directa, su salida o su nave.
    dict(id="one-clic-no-vuelve-a-leer", pruebas=[ON_CLIC], viejo=ON_RELEE, nuevo="    const i = args.i;"),
    dict(id="one-clic-no-mira-directa", pruebas=[ON_CLIC],
         viejo=ON_RELEE, nuevo=ON_RELEE.replace(" || t.directa !== args.directa", "")),
    dict(id="one-clic-no-mira-salida", pruebas=[ON_CLIC],
         viejo=ON_RELEE, nuevo=ON_RELEE.replace(" || t.salida !== args.salida", "")),
    dict(id="one-clic-otra-nave", pruebas=[ON_CLIC],
         viejo=")(args.nave).find(x => x.i === args.i);", nuevo=")('ONE').find(x => x.i === args.i);"),
]

# --- Encargo 34 · commit 3: con el candado cerrado, la OK-EJEMPLO dice «lista para emitir» en la columna «N° de reserva
# emitida», igual en el panel y en la planilla, y el panel la cuenta aparte de las emitidas; «Confirmada», nunca
# (CICLO-one-y-maersk-eligen-la-nave.md). ---
LP_LISTA = LP + "test_lista_para_emitir_no_es_emitida"
PL_NRES = PL + "test_numero_de_reserva_igual_en_el_panel_y_en_la_planilla"
ESC_COPIA = ESC + "test_web_descarga_es_copia_y_solo_escribe_la_hoja_corrida"
MUTACIONES += [
    # La lectura: la OK-EJEMPLO otra vez como emitida.
    dict(id="panel-ok-ejemplo-es-emitida", pruebas=[LP + "test_lectura_de_cada_estado"],
         viejo='  if (est.startsWith("EMIT")) return "emitida";\n  if (est.startsWith("OK")) return "lista";\n',
         nuevo='  if (est.startsWith("EMIT") || est.startsWith("OK")) return "emitida";\n'),
    # La columna del panel: «✓ Confirmada» otra vez; sin el texto del programa; la lista contada como emitida.
    dict(id="panel-lista-dice-confirmada", pruebas=[LP_LISTA],
         viejo='${esc(nres || "—")}</span>`;', nuevo='✓ Confirmada</span>`;'),
    dict(id="panel-columna-sin-n-reserva", pruebas=[LP_LISTA],
         viejo='const nres = (typeof r === "object" && r) ? (r.n_reserva || "") : "";',
         nuevo='const nres = (typeof r === "object" && r) ? ("") : "";'),
    dict(id="panel-lista-cuenta-como-emitida", pruebas=[LP_LISTA],
         viejo="if (lista) totalListas++; else totalEmitidas++;", nuevo="totalEmitidas++;"),
    # La cuenta de la corrida: sin las listas; las listas como emitidas.
    dict(id="panel-cuenta-sin-listas", pruebas=[LP_LISTA],
         viejo="  if (listas) partes.push(`${listas} de ${total} listas para emitir`);\n", nuevo=""),
    dict(id="panel-cuenta-listas-como-emitidas", pruebas=[LP_LISTA],
         viejo="  if (emitidas || !listas) partes.push(`${emitidas} de ${total} emitidas`);\n",
         nuevo="  partes.push(`${emitidas + listas} de ${total} emitidas`);\n"),
    dict(id="panel-estado-final-emitidas", pruebas=[LP_LISTA],
         viejo="estado(`Terminó: ${cuentaCorrida(totalEmitidas, totalListas, selCount)}`);",
         nuevo="estado(`${totalEmitidas + totalListas} de ${selCount} reserva(s) emitidas con éxito`);"),
    # La fuente única: sin «lista para emitir»; la planilla sin ella; /api/estado sin ella.
    dict(id="n-reserva-sin-lista", pruebas=[LP_LISTA, PL_NRES, ESC_COPIA],
         viejo='    return LISTA_PARA_EMITIR if str((r or {}).get("estado") or "") == "OK-EJEMPLO" else ""\n',
         nuevo='    return ""\n'),
    dict(id="planilla-numero-sin-el-texto", pruebas=[PL_NRES, ESC_COPIA],
         viejo="                c_n = ws.cell(f_idx, col_num, _texto_n_reserva(r))\n",
         nuevo="                c_n = ws.cell(f_idx, col_num, bkg)\n"),
    dict(id="estado-sin-n-reserva", pruebas=[PL_NRES],
         viejo="dict(r, n_reserva=_texto_n_reserva(r)) if isinstance(r, dict) else r",
         nuevo="dict(r, n_reserva='') if isinstance(r, dict) else r"),
]

# --- Encargo 37 · commit 1: «Booking Information» que no avanzó queda NO ENVIADA con su motivo, y deja su evidencia
# (decisión de Marcelo, CICLO-maersk-ultimos-puntos.md; hasta ahí, REVISAR) ---
BOOKING_MK = MK + "test_booking_information_dice_lo_que_pide"

MUTACIONES += [
    dict(id="maersk-booking-vuelve-a-revisar", pruebas=[BOOKING_MK],
         viejo=("    return _no_enviada(reg, f\"MAERSK: en «Booking Information», {que}; {_MK_NADA_MAS} "
                "({', '.join(det)})\")\n"),
         nuevo="    return (\"REVISAR\", f\"MAERSK: {que} ({', '.join(det)})\")\n"),
    dict(id="maersk-booking-sin-evidencia", pruebas=[BOOKING_MK, LD + "test_solo_ahi"],
         viejo=("    _evidencia_antes_de_la_guarda(page, reg, f\"mk_f{f}_booking\", \"en «Booking Information», "
                "sin avanzar\",\n                                  completa=False)\n"), nuevo=""),
    dict(id="maersk-booking-sigue", pruebas=[MK + "test_booking_information_no_avanza_corta"],
         viejo="    if not avanzo:\n        return _mk_booking_sin_avanzar(page, reg, det, f)\n",
         nuevo="    if not avanzo:\n        pass\n"),
]

# --- Encargo 37 · commit 2: si no se puede leer qué fecha quedó en la tarjeta, MAERSK corta con NO ENVIADA (decisión de
# Marcelo, CICLO-maersk-ultimos-puntos.md; hasta ahí seguía con un aviso) ---
ILEGIBLE_MK = ("    return _no_enviada(reg, f\"MAERSK: elegí el {elegido:%d-%m-%Y} en el calendario, pero no pude "
               "leer qué fecha \"")

MUTACIONES += [
    dict(id="mk-retiro-ilegible-sigue", pruebas=[RT_QUEDO], viejo=ILEGIBLE_MK, nuevo="    return None\n" + ILEGIBLE_MK),
    dict(id="mk-retiro-sin-evidencia-de-la-tarjeta", pruebas=[RT_QUEDO, LD + "test_solo_ahi"],
         viejo=("    _evidencia_antes_de_la_guarda(page, reg, f\"mk_f{f}_retiro\", \"después de elegir la fecha de "
                "retiro\",\n                                  completa=False)\n"), nuevo=""),
]

# --- Encargo 37 · commit 3: la fecha de retiro nunca es sábado ni domingo; si el primer día hábil no está
# habilitado, el siguiente día hábil habilitado (decisión de Marcelo, CICLO-maersk-ultimos-puntos.md) ---
MUTACIONES += [
    dict(id="mk-retiro-vuelve-el-fin-de-semana", pruebas=[RT_REGLA, RT_SIGUIENTE],
         viejo="        if not _mk_dia_habil(d, feriados):\n            d += datetime.timedelta(days=1)\n"
               "            continue\n",
         nuevo=""),
    dict(id="mk-retiro-el-sabado-cuenta", pruebas=[RT_REGLA],
         viejo="        if not _mk_dia_habil(d, feriados):\n            d += datetime.timedelta(days=1)\n",
         nuevo="        if d.weekday() >= 6 or d in feriados:\n            d += datetime.timedelta(days=1)\n"),
]

# --- Encargo 37 · commit 4: la referencia de retiro de MAERSK en su campo, por su name, no en «el primer textarea»
# (decisión de Marcelo, CICLO-maersk-ultimos-puntos.md) ---
REF_MK = "test_clics.TestReferenciaMaersk."
LLAMADA_REF = ("            corte = _mk_referencia_de_retiro(page, reg, det, ref_txt)\n            if corte:\n"
               "                return corte\n")
FALLA_REF = "        return _no_enviada(reg, f\"MAERSK: falló la escritura de la referencia de retiro"

MUTACIONES += [
    dict(id="mk-referencia-el-primer-textarea", pruebas=[REF_MK + "test_el_campo_es_el_medido", FG],
         viejo="MK_REFERENCIA = \"textarea[name='haulageReference']\"\n",
         nuevo="MK_REFERENCIA = \"mc-textarea textarea, textarea\"\n"),
    dict(id="mk-referencia-sin-unico", pruebas=[REF_MK + "test_sin_un_solo_campo_no_escribe"],
         viejo="    if len(vistos) != 1:\n        cuantos = ", nuevo="    if not vistos:\n        cuantos = "),
    dict(id="mk-referencia-cuenta-los-ocultos",
         pruebas=[REF_MK + "test_escribe_en_el_unico_a_la_vista", REF_MK + "test_sin_un_solo_campo_no_escribe"],
         viejo="        vistos = [campos.nth(i) for i in range(campos.count()) if campos.nth(i).is_visible()]\n",
         nuevo="        vistos = [campos.nth(i) for i in range(campos.count())]\n"),
    dict(id="mk-referencia-rota-sin-try", pruebas=[REF_MK + "test_sin_un_solo_campo_no_escribe"],
         viejo="    except Exception as e:\n        vistos, error = [], _texto_error(e)\n",
         nuevo="    except ZeroDivisionError as e:\n        vistos, error = [], _texto_error(e)\n"),
    dict(id="mk-referencia-falla-sigue", pruebas=[REF_MK + "test_si_no_se_puede_escribir_corta"],
         viejo=FALLA_REF, nuevo="        return None\n" + FALLA_REF),
    dict(id="mk-referencia-no-la-anota", pruebas=[REF_MK + "test_escribe_en_el_unico_a_la_vista"],
         viejo="    det.append(\"haulageRef=\" + texto)\n", nuevo=""),
    dict(id="maersk-referencia-no-corta", pruebas=[REF_MK + "test_reservar_maersk_la_escribe_y_corta"],
         viejo=LLAMADA_REF, nuevo="            _mk_referencia_de_retiro(page, reg, det, ref_txt)\n"),
]

# --- Encargo 37 · commit 5: el Shipper de MAERSK por su tarjeta «Shipper»; si no trae a la empresa, corta sin pulsar
# nada (FRENO: elegirla no está medido). La foto ve también «.last» sin paréntesis (decisiones de Marcelo,
# CICLO-maersk-ultimos-puntos.md) ---
SH_MK = "test_clics.TestShipperMaersk."
LLAMADA_SH = "            corte = _mk_shipper(page, reg, det, f)\n"
EVALUA_SH = "            r, error = page.evaluate(_JS_MK_SHIPPER, _MK_ARGS_SHIPPER), \"\"\n"

MUTACIONES += [
    # La foto: «.last» sin paréntesis delante (hasta el encargo 37 no lo veía).
    dict(id="mk-shipper-vuelve-el-ultimo", pruebas=[FG],
         viejo=LLAMADA_SH, nuevo=LLAMADA_SH + "            tarjetas = page.locator(\"mc-c-party-card\")\n"
                                              "            tarjetas.last.click(timeout=4000)\n"),
    dict(id="maersk-shipper-no-se-mira", pruebas=[SH_MK + "test_reservar_maersk_elige_el_shipper_y_corta"],
         viejo=LLAMADA_SH, nuevo=""),
    dict(id="mk-shipper-sin-una-sola-tarjeta", pruebas=[SH_MK + "test_sin_una_sola_tarjeta_corta"],
         viejo="    if r.get(\"n\") != 1:\n        cuantas = ", nuevo="    if False:\n        cuantas = "),
    dict(id="mk-shipper-sin-la-empresa-sigue", pruebas=[SH_MK + "test_elige_a_la_empresa_con_dos_clics"],
         viejo="    return _mk_elegir_shipper(page, reg, det, f)\n", nuevo="    return None\n"),
    dict(id="mk-shipper-sin-try", pruebas=[SH_MK + "test_sin_una_sola_tarjeta_corta"],
         viejo=EVALUA_SH + "        except Exception as e:\n",
         nuevo=EVALUA_SH + "        except ZeroDivisionError as e:\n"),
    dict(id="mk-shipper-no-lo-anota", pruebas=[SH_MK + "test_con_la_empresa_no_pulsa_nada"],
         viejo="ya viene en la tarjeta «{MK_SHIPPER}»; no pulsé nada\")\n"
               "        det.append(\"shipper=\" + MK_EMPRESA)\n",
         nuevo="ya viene en la tarjeta «{MK_SHIPPER}»; no pulsé nada\")\n"),
    dict(id="mk-shipper-otro-titulo", pruebas=[SH_MK + "test_la_empresa_y_el_titulo_son_los_medidos"],
         viejo="MK_SHIPPER = \"Shipper\"\n", nuevo="MK_SHIPPER = \"Booked By\"\n"),
    dict(id="mk-shipper-otra-empresa", pruebas=[SH_MK + "test_la_empresa_y_el_titulo_son_los_medidos"],
         viejo="MK_EMPRESA = \"AQUACHILE\"\n", nuevo="MK_EMPRESA = \"AQUACHILE S.A.\"\n"),
    # El JavaScript: por su title, a la vista, con su raíz shadow y sin distinguir mayúsculas.
    dict(id="mk-shipper-js-cualquier-tarjeta", pruebas=[SH_MK + "test_js_shipper"],
         viejo=" && mkAtr(x.el, 'title') === a.titulo", nuevo=""),
    dict(id="mk-shipper-js-tambien-invisibles", pruebas=[SH_MK + "test_js_shipper"],
         viejo="&& mkVisible(x.el)).map(x => x.el);", nuevo=").map(x => x.el);"),
    dict(id="mk-shipper-js-sin-sombra", pruebas=[SH_MK + "test_js_shipper"],
         viejo="[...((e.shadowRoot && e.shadowRoot.childNodes) || []), ", nuevo="["),
    dict(id="mk-shipper-js-con-mayusculas", pruebas=[SH_MK + "test_js_shipper"],
         viejo="partes.join(' ').replace(/\\s+/g, ' ').trim().toUpperCase();",
         nuevo="partes.join(' ').replace(/\\s+/g, ' ').trim();"),
]

# --- Encargo 37 · commit 6: lo que encontró la revisión de código (CICLO-maersk-ultimos-puntos.md) ---
SC_TRAGA = SC + "test_nada_se_traga_el_corte"
SH_ESPERA = SH_MK + "test_espera_la_tarjeta_con_la_empresa"

MUTACIONES += [
    # Nada se traga un corte (la revisión armó así el defecto de antes con otros nombres, y la red no lo veía).
    dict(id="maersk-shipper-se-traga-el-corte", pruebas=[SC_TRAGA],
         viejo=LLAMADA_SH, nuevo="            try:\n                corte = _mk_shipper(page, reg, det, f)\n"
                                 "            except ObjetivoNoEncontrado:\n                corte = None\n"),
    dict(id="maersk-referencia-se-traga-todo", pruebas=[SC_TRAGA],
         viejo=LLAMADA_REF, nuevo="            try:\n" + LLAMADA_REF.replace("            ", "                ")
                                  + "            except BaseException:\n                pass\n"),
    # La foto ve «.nth(-1)».
    dict(id="mk-referencia-la-ultima-por-nth", pruebas=[FG],
         viejo="        campos = page.locator(MK_REFERENCIA)\n",
         nuevo="        campos = page.locator(MK_REFERENCIA)\n        campos.nth(-1).focus()\n"),
    # El Shipper espera, y dice si no pudo leer la página.
    dict(id="mk-shipper-sin-espera", pruebas=[SH_ESPERA],
         viejo="    for intento in range(seg * 2):\n        if intento:\n            esperar(page, 0.5)\n"
               "        try:\n            r, error = page.evaluate(_JS_MK_SHIPPER",
         nuevo="    for intento in range(1):\n        if intento:\n            esperar(page, 0.5)\n"
               "        try:\n            r, error = page.evaluate(_JS_MK_SHIPPER"),
    dict(id="mk-shipper-espera-menos", pruebas=[SH_MK + "test_sin_un_solo_add_corta_sin_pulsar"],
         viejo="MK_ESPERA_SHIPPER = 5 ", nuevo="MK_ESPERA_SHIPPER = 2 "),
    dict(id="mk-shipper-error-sin-motivo", pruebas=[SH_MK + "test_sin_una_sola_tarjeta_corta"],
         viejo="        cuantas = f\"no pude leer la página: {error}\" if error else f\"había {r.get('n') or 0}\"\n",
         nuevo="        cuantas = f\"había {r.get('n') or 0}\"\n"),
    dict(id="mk-referencia-error-sin-motivo", pruebas=[REF_MK + "test_sin_un_solo_campo_no_escribe"],
         viejo="        cuantos = f\"no pude leer la página: {error}\" if error else f\"había {len(vistos)}\"\n",
         nuevo="        cuantos = f\"había {len(vistos)}\"\n"),
    # La tarjeta de la fecha: espera también cuando está ilegible, y dice si no pudo leer la página.
    dict(id="mk-retiro-no-espera-la-ilegible", pruebas=[RT_QUEDO],
         viejo="        if r.get(\"tarjeta\") and not r.get(\"vacia\") and (r.get(\"fechas\") or r.get(\"valor\")):\n",
         nuevo="        if not r.get(\"vacia\"):\n"),
    dict(id="mk-retiro-error-sin-motivo", pruebas=[RT_QUEDO],
         viejo="    if error:\n        cual = f\" (no pude leer la página: {error})\"\n    else:\n",
         nuevo="    if False:\n        cual = f\" (no pude leer la página: {error})\"\n    else:\n"),
]

# --- Encargo 38 · commit 1: «Review booking» por su texto, sin el respaldo que pulsaba <html>
# (CICLO-maersk-shipper-y-cortes.md); rehecho en el commit 6 (la revisión de código): el único mc-button a la vista, con
# el corte que dice si no estaba o no aceptó el clic ---
REV_MK = MK + "test_review_booking_por_su_texto"
SIN_REV_MK = MK + "test_sin_review_booking_corta"
REV_CLIC = MK + "test_review_booking_que_no_acepta_el_clic"
REV_YA = MK + "test_la_revision_ya_aparecio"
REV_LLAMADA = MK + "test_reservar_maersk_pulsa_la_revision_sin_respaldo"
LLAMADA_REV = "            corte = _mk_pulsar_revision(page, reg, f)\n"
CUANTOS_REV = "    cuantos = f\"no pude leer la página: {leer}\" if leer else f\"había {vistos}\"\n"

MUTACIONES += [
    dict(id="mk-revision-vuelve-el-respaldo", pruebas=[SIN_REV_MK],
         viejo=CUANTOS_REV, nuevo="    page.evaluate(\"() => document.documentElement.click()\")\n" + CUANTOS_REV),
    # Con su try, como estaba: la página falsa lo anota aunque el programa se trague el error (revisión del encargo 38).
    dict(id="mk-revision-respaldo-con-try", pruebas=[SIN_REV_MK],
         viejo=CUANTOS_REV, nuevo="    try:\n        page.evaluate(\"() => document.documentElement.click()\")\n"
                                  "    except Exception:\n        pass\n" + CUANTOS_REV),
    dict(id="mk-revision-sin-corte", pruebas=[SIN_REV_MK],
         viejo="    raise ObjetivoNoEncontrado(\"Review booking de MAERSK\",\n",
         nuevo="    return None\n    raise ObjetivoNoEncontrado(\"Review booking de MAERSK\",\n"),
    dict(id="mk-revision-espera-menos", pruebas=[SIN_REV_MK],
         viejo="MK_INTENTOS_REVISION = 15 ", nuevo="MK_INTENTOS_REVISION = 5 "),
    dict(id="mk-revision-sin-lo-que-pide", pruebas=[SIN_REV_MK],
         viejo="intentos ({cuantos})\", pide=_mk_lo_que_pide(page))", nuevo="intentos ({cuantos})\")"),
    dict(id="mk-revision-la-invisible-sirve", pruebas=[REV_MK],
         viejo="for i in range(botones.count()) if botones.nth(i).is_visible()]",
         nuevo="for i in range(botones.count())]"),
    dict(id="mk-revision-otro-texto", pruebas=[REV_MK],
         viejo="MK_REVISION = \"Review booking\"\n", nuevo="MK_REVISION = \"Review\"\n"),
    dict(id="mk-revision-distingue-mayusculas", pruebas=[REV_MK],
         viejo="filter(has_text=_re_mk.compile(MK_REVISION, _re_mk.I))",
         nuevo="filter(has_text=_re_mk.compile(MK_REVISION))"),
    dict(id="mk-revision-cualquier-boton", pruebas=[REV_MK],
         viejo="botones = page.locator(\"mc-button\").filter(",
         nuevo="botones = page.locator(\"mc-button, button\").filter("),
    dict(id="mk-revision-varios-sirven", pruebas=[SIN_REV_MK],
         viejo="        if len(a_la_vista) != 1:\n            continue\n        [boton] = a_la_vista\n",
         nuevo="        if not a_la_vista:\n            continue\n        boton = a_la_vista[0]\n"),
    dict(id="mk-revision-un-solo-intento", pruebas=[REV_MK],
         viejo="            clic = _texto_error(e)\n            continue\n",
         nuevo="            clic = _texto_error(e)\n            break\n"),
    dict(id="mk-revision-sin-mirar-si-ya-aparecio", pruebas=[REV_YA],
         viejo="        if \"/review\" in page.url.lower():\n            reg.info(f\"la revisión ya apareció",
         nuevo="        if False:\n            reg.info(f\"la revisión ya apareció"),
    dict(id="mk-revision-clic-sin-evidencia", pruebas=[REV_CLIC],
         viejo="        _evidencia_antes_de_la_guarda(page, reg, f\"mk_f{f}_revision\", ",
         nuevo="        (lambda *a, **k: None)(page, reg, f\"mk_f{f}_revision\", "),
    dict(id="mk-revision-clic-dice-no-encontre", pruebas=[REV_CLIC],
         viejo="    if clic:\n        _evidencia_antes_de_la_guarda(",
         nuevo="    if False:\n        _evidencia_antes_de_la_guarda("),
    dict(id="mk-revision-no-la-llama", pruebas=[REV_LLAMADA], viejo=LLAMADA_REV, nuevo=""),
    dict(id="mk-revision-respaldo-en-reservar", pruebas=[REV_LLAMADA],
         viejo=LLAMADA_REV, nuevo=LLAMADA_REV + "            page.evaluate(\"() => 'Review booking'\")\n"),
    dict(id="mk-revision-no-corta", pruebas=[REV_LLAMADA],
         viejo=LLAMADA_REV + "            if corte:\n                return corte\n",
         nuevo="            _mk_pulsar_revision(page, reg, f)\n"),
    # La foto ve el primer elemento cuyo textContent calza (revisión del encargo 38).
    dict(id="mk-foto-ve-el-primero-por-textcontent", pruebas=[FG],
         viejo=CUANTOS_REV,
         nuevo="    page.evaluate(\"() => [...document.querySelectorAll('*')].find(e => { const t = "
               "(e.textContent || ''); return /Review booking/.test(t); }).click()\")\n" + CUANTOS_REV),
]

# --- Encargo 38 · commit 2: sin la tecla Escape después del Shipper (CICLO-maersk-shipper-y-cortes.md) ---
CAPTURA_5C = "            reg.captura(page, f\"mk_f{f}_5c_details\", full=True)\n"

MUTACIONES += [
    dict(id="mk-shipper-vuelve-el-escape", pruebas=[SH_MK + "test_despues_del_shipper_no_pulsa_escape"],
         viejo=CAPTURA_5C, nuevo="            page.keyboard.press(\"Escape\")\n" + CAPTURA_5C),
]

# --- Encargo 38 · commit 3: los REVISAR de MAERSK antes del botón final, NO ENVIADA; REVISAR solo para la nave que no
# está (CICLO-maersk-shipper-y-cortes.md) ---
CORTES_MK = MK + "test_los_cortes_antes_de_la_nave_son_no_enviada"
REVISAR_MK = MK + "test_revisar_solo_si_la_nave_no_esta"
INCOMPLETO_MK = MK + "test_formulario_incompleto_dice_lo_que_pide"

MUTACIONES += [
    dict(id="mk-sin-formulario-vuelve-a-revisar", pruebas=[CORTES_MK, REVISAR_MK],
         viejo="        return _no_enviada(reg, \"MAERSK: no se abrió el formulario /book/\" "
               "+ f\"; {_MK_NADA_MAS}\")\n",
         nuevo="        return (\"REVISAR\", \"MAERSK: no se abrió el formulario /book/\")\n"),
    dict(id="mk-incompleto-vuelve-a-revisar", pruebas=[CORTES_MK, REVISAR_MK],
         viejo="        return _mk_formulario_incompleto(page, reg, det, f)\n",
         nuevo="        return (\"REVISAR\", f\"MAERSK: formulario incompleto ({', '.join(det)})\")\n"),
    dict(id="mk-incompleto-ayudante-revisar", pruebas=[REVISAR_MK, INCOMPLETO_MK],
         viejo="    return _no_enviada(reg, f\"MAERSK: formulario incompleto{que}; {_MK_NADA_MAS} "
               "({', '.join(det)})\")\n",
         nuevo="    return (\"REVISAR\", f\"MAERSK: formulario incompleto{que}; {_MK_NADA_MAS} "
               "({', '.join(det)})\")\n"),
    dict(id="mk-incompleto-sin-lo-que-pide", pruebas=[INCOMPLETO_MK],
         viejo="    que = f\", y el portal pide: {pide}\" if pide else ", nuevo="    que = f\"\" if pide else "),
]

# --- Encargo 38 · commit 4: los feriados de Chile no son días hábiles para el retiro de MAERSK
# (CICLO-maersk-shipper-y-cortes.md) ---
RT_FERIADOS = RT + "test_los_feriados_no_son_dias_habiles"
RT_CAL_FERIADOS = RT + "test_el_calendario_salta_los_feriados"
RT_LIBRERIA = RT + "test_los_feriados_son_los_de_chile_de_la_libreria"
RT_SIN_LIBRERIA = RT + "test_sin_la_libreria_avisa_una_vez_y_sigue_de_lunes_a_viernes"
RT_USA = RT + "test_la_fecha_de_retiro_usa_los_feriados"

MUTACIONES += [
    dict(id="mk-feriados-son-habiles", pruebas=[RT_FERIADOS, RT_CAL_FERIADOS],
         viejo="    return d.weekday() < 5 and d not in feriados\n", nuevo="    return d.weekday() < 5\n"),
    dict(id="mk-feriados-calendario-sin-feriados", pruebas=[RT_CAL_FERIADOS],
         viejo="        if not _mk_dia_habil(d, feriados):\n            d += datetime.timedelta(days=1)\n",
         nuevo="        if d.weekday() >= 5:\n            d += datetime.timedelta(days=1)\n"),
    dict(id="mk-feriados-otro-pais", pruebas=[RT_LIBRERIA],
         viejo="        return dict(holidays.country_holidays(\"CL\", years=",
         nuevo="        return dict(holidays.country_holidays(\"AR\", years="),
    dict(id="mk-feriados-sin-aviso", pruebas=[RT_SIN_LIBRERIA],
         viejo="        _avisar_en_pantalla_y_log(\n            f\"⚠ No pude usar los feriados de Chile",
         nuevo="        (lambda *a, **k: None)(\n            f\"⚠ No pude usar los feriados de Chile"),
    dict(id="mk-feriados-avisa-cada-vez", pruebas=[RT_SIN_LIBRERIA],
         viejo="            una_vez=\"feriados\")\n", nuevo="            una_vez=None)\n"),
    dict(id="mk-feriados-la-fecha-no-los-usa", pruebas=[RT_USA],
         viejo="    objetivo = _mk_dia_de_retiro(hoy, feriados)\n", nuevo="    objetivo = _mk_dia_de_retiro(hoy)\n"),
    dict(id="mk-feriados-el-calendario-no-los-usa", pruebas=[RT_USA],
         viejo="_mk_elegir_dia_de_retiro(cal.get(\"dias\"), objetivo, feriados)\n",
         nuevo="_mk_elegir_dia_de_retiro(cal.get(\"dias\"), objetivo)\n"),
    dict(id="mk-feriados-no-lo-dice", pruebas=[RT_USA],
         viejo="({_DIAS_ES[objetivo.weekday()]}){_mk_feriados_saltados(hoy, objetivo, feriados)}.\")\n",
         nuevo="({_DIAS_ES[objetivo.weekday()]}).\")\n"),
    dict(id="mk-feriados-saltados-tambien-sabados", pruebas=[RT_FERIADOS],
         viejo="for d in dias if d.weekday() < 5 and d in feriados]", nuevo="for d in dias if d in feriados]"),
    dict(id="mk-feriados-saltados-mal-plural", pruebas=[RT_FERIADOS],
         viejo="{'es feriado' if len(saltados) == 1 else 'son feriados'}", nuevo="es feriado"),
]

# --- Encargo 38 · commit 5: el Shipper de MAERSK con dos clics, el «Add» de su tarjeta y el único resultado con la
# empresa en el buscador, y su comprobación (CICLO-maersk-shipper-y-cortes.md) ---
SH_DOS = SH_MK + "test_elige_a_la_empresa_con_dos_clics"
SH_CORTA = SH_MK + "test_si_no_queda_elegido_corta_sin_otro_clic"
SH_JS = SH_MK + "test_js_shipper"
SH_SIN_ADD = SH_MK + "test_sin_un_solo_add_corta_sin_pulsar"

MUTACIONES += [
    dict(id="mk-shipper-otro-texto-del-add", pruebas=[SH_MK + "test_la_empresa_y_el_titulo_son_los_medidos"],
         viejo="MK_AGREGAR = \"Add\"\n", nuevo="MK_AGREGAR = \"+ Add\"\n"),
    dict(id="mk-shipper-espera-buscador-menos", pruebas=[SH_CORTA],
         viejo="MK_ESPERA_BUSCADOR = 10 ", nuevo="MK_ESPERA_BUSCADOR = 5 "),
    dict(id="mk-shipper-sin-add-pulsa", pruebas=[SH_SIN_ADD],
         viejo="    if r.get(\"agregar\") != 1:\n        raise ObjetivoNoEncontrado(",
         nuevo="    if False:\n        raise ObjetivoNoEncontrado("),
    dict(id="mk-shipper-elegido-no-lo-anota", pruebas=[SH_DOS],
         viejo="y la tarjeta «{MK_SHIPPER}» lo muestra\")\n    det.append(\"shipper=\" + MK_EMPRESA)\n",
         nuevo="y la tarjeta «{MK_SHIPPER}» lo muestra\")\n"),
    dict(id="mk-shipper-no-deja-el-buscador", pruebas=[SH_DOS],
         viejo="    _evidencia_antes_de_la_guarda(page, reg, f\"mk_f{f}_buscador\", ",
         nuevo="    (lambda *a, **k: None)(page, reg, f\"mk_f{f}_buscador\", "),
    dict(id="mk-shipper-no-espera-el-buscador", pruebas=[SH_DOS],
         viejo="_mk_leer_shipper(page, _mk_resultados_quietos(), MK_ESPERA_BUSCADOR)",
         nuevo="_mk_leer_shipper(page, lambda x: True, MK_ESPERA_BUSCADOR)"),
    dict(id="mk-shipper-espera-solo-un-resultado", pruebas=[SH_MK + "test_espera_el_resultado_con_la_empresa"],
         viejo="_mk_leer_shipper(page, _mk_resultados_quietos(), MK_ESPERA_BUSCADOR)",
         nuevo="_mk_leer_shipper(page, lambda x: x.get(\"resultados\"), MK_ESPERA_BUSCADOR)"),
    dict(id="mk-shipper-pulsa-sin-decir-que", pruebas=[SH_DOS],
         viejo="dict(_MK_ARGS_SHIPPER, que=que)", nuevo="dict(_MK_ARGS_SHIPPER)"),
    dict(id="mk-shipper-sin-titulo-sigue", pruebas=[SH_CORTA],
         viejo="    if not r.get(\"titulo\"):\n        return _mk_shipper_corte(",
         nuevo="    if False:\n        return _mk_shipper_corte("),
    dict(id="mk-shipper-varios-resultados-sirven", pruebas=[SH_CORTA],
         viejo="    if r.get(\"con_empresa\") != 1:\n", nuevo="    if not r.get(\"con_empresa\"):\n"),
    dict(id="mk-shipper-no-comprueba-la-tarjeta", pruebas=[SH_CORTA],
         viejo="    if not _mk_shipper_puesto(r):\n        que = (", nuevo="    if False:\n        que = ("),
    dict(id="mk-shipper-no-mira-si-se-cerro", pruebas=[SH_CORTA],
         viejo="    if r.get(\"abierto\"):\n        corte = _mk_cerrar_buscador(",
         nuevo="    if False:\n        corte = _mk_cerrar_buscador("),
    dict(id="mk-shipper-corte-sin-evidencia", pruebas=[SH_CORTA],
         viejo="    _evidencia_antes_de_la_guarda(page, reg, f\"mk_f{f}_shipper\", ",
         nuevo="    (lambda *a, **k: None)(page, reg, f\"mk_f{f}_shipper\", "),
    dict(id="mk-shipper-corte-sin-motivo", pruebas=[SH_CORTA],
         viejo="    return _no_enviada(reg, f\"MAERSK: {que}; {_MK_NADA_MAS}\")\n",
         nuevo="    return _no_enviada(reg, f\"MAERSK: {_MK_NADA_MAS}\")\n"),
    dict(id="mk-shipper-pulsa-sin-releer", pruebas=[SH_CORTA],
         viejo="        if el is None:\n            return _mk_shipper_corte(",
         nuevo="        if False:\n            return _mk_shipper_corte("),
    dict(id="mk-shipper-clic-sin-try", pruebas=[SH_CORTA],
         viejo="    except Exception as e:\n        return _mk_shipper_corte(page, reg, f, f\"falló el clic en "
               "{nombre}",
         nuevo="    except ZeroDivisionError as e:\n        return _mk_shipper_corte(page, reg, f, f\"falló el clic en "
               "{nombre}"),
    dict(id="maersk-shipper-no-corta", pruebas=[SH_MK + "test_reservar_maersk_elige_el_shipper_y_corta"],
         viejo=LLAMADA_SH + "            if corte:\n                return corte\n",
         nuevo="            _mk_shipper(page, reg, det, f)\n"),
    # El JavaScript: el «Add» de esa tarjeta, a la vista y con ese texto entero; los resultados del buscador, a la vista
    # y con su tarjeta; su título; la empresa como palabra entera, con el texto nodo por nodo; y lo que pulsa.
    dict(id="mk-shipper-js-add-otro-texto", pruebas=[SH_JS],
         viejo="mkTexto(x.el) === a.agregar", nuevo="mkTexto(x.el).includes(a.agregar)"),
    dict(id="mk-shipper-js-add-invisible", pruebas=[SH_JS],
         viejo="=== a.agregar && mkVisible(x.el));", nuevo="=== a.agregar);"),
    dict(id="mk-shipper-js-add-de-cualquier-tarjeta", pruebas=[SH_JS],
         viejo="todos.filter(x => x.anc.includes(t)\n", nuevo="todos.filter(x => true\n"),
    dict(id="mk-shipper-js-resultados-fuera-del-buscador", pruebas=[SH_JS],
         viejo="mkTag(x.el) === 'label' && enBuscador(x) && mkVisible(x.el)",
         nuevo="mkTag(x.el) === 'label' && mkVisible(x.el)"),
    dict(id="mk-shipper-js-resultados-invisibles", pruebas=[SH_JS],
         viejo="mkTag(x.el) === 'label' && enBuscador(x) && mkVisible(x.el)",
         nuevo="mkTag(x.el) === 'label' && enBuscador(x)"),
    dict(id="mk-shipper-js-resultado-sin-tarjeta", pruebas=[SH_JS],
         viejo="\n                                             && conTarjeta(x));", nuevo=");"),
    dict(id="mk-shipper-js-titulo-cualquiera", pruebas=[SH_JS],
         viejo="encabezados.some(x => _palabraEn(mkTextoHondo(x.el), String(a.titulo).toUpperCase(), 0) >= 0)",
         nuevo="encabezados.length > 0"),
    dict(id="mk-shipper-js-pulsa-sin-titulo", pruebas=[SH_JS],
         viejo="(s.titulo ? s.conEmpresa : [])", nuevo="s.conEmpresa"),
    dict(id="mk-shipper-js-pulsa-varios", pruebas=[SH_JS],
         viejo="    return lista.length === 1 ? uno : null;\n", nuevo="    return uno || null;\n"),
    dict(id="mk-shipper-js-empresa-parte-de-palabra", pruebas=[SH_JS],
         viejo="nombres(e).some(y => _palabraEn(mkTextoHondo(y.el), String(a.empresa).toUpperCase(),\n"
               "                                                                0) >= 0);",
         nuevo="nombres(e).some(y => mkTextoHondo(y.el).includes(String(a.empresa).toUpperCase()));"),
    dict(id="mk-shipper-js-sin-sombra-adentro", pruebas=[SH_JS],
         viejo="                    if (c.shadowRoot) w(c.shadowRoot);\n", nuevo=""),
    dict(id="mk-shipper-js-texto-pegado", pruebas=[SH_JS],
         viejo="return partes.join(' ').replace(", nuevo="return partes.join('').replace("),
]

# --- Encargo 38 · commit 6: lo que encontró la revisión de código (CICLO-maersk-shipper-y-cortes.md) ---
INCOMPLETO_MK6 = MK + "test_formulario_incompleto_dice_lo_que_pide"
RT_PEREZOSA = RT + "test_la_libreria_que_falla_al_calcular_avisa"

MUTACIONES += [
    # «Booking Information» incompleta: su evidencia, y «no vi» (sin avisos, o sin poder leerlos).
    dict(id="mk-incompleto-sin-evidencia", pruebas=[INCOMPLETO_MK6],
         viejo="    _evidencia_antes_de_la_guarda(page, reg, f\"mk_f{f}_booking\", "
               "\"en «Booking Information», incompleto\",",
         nuevo="    (lambda *a, **k: None)(page, reg, f\"mk_f{f}_booking\", \"en «Booking Information», incompleto\","),
    # Los feriados, copiados dentro del try, de este año y del siguiente.
    dict(id="mk-feriados-sin-copiar", pruebas=[RT_PEREZOSA],
         viejo="        return dict(holidays.country_holidays(\"CL\", years=(hoy.year, hoy.year + 1)))\n",
         nuevo="        return holidays.country_holidays(\"CL\", years=(hoy.year, hoy.year + 1))\n"),
    dict(id="mk-feriados-un-solo-ano", pruebas=[RT + "test_los_feriados_son_los_de_chile_de_la_libreria"],
         viejo="years=(hoy.year, hoy.year + 1)", nuevo="years=(hoy.year,)"),
    # El Shipper: la empresa en el nombre de la parte; el buscador abierto por su encabezado; la lista quieta; el
    # motivo dice que pulsó; y la página falsa anota lo que no se permite, aunque vaya en un try.
    dict(id="mk-shipper-js-empresa-en-la-direccion", pruebas=[SH_JS],
         viejo="mkAtr(y.el, 'class').split(/\\s+/).includes('party__info')", nuevo="true"),
    dict(id="mk-shipper-js-cerrado-sin-encabezado", pruebas=[SH_JS],
         viejo="abierto: encabezados.length > 0 || resultados.length > 0,", nuevo="abierto: resultados.length > 0,"),
    dict(id="mk-shipper-cerrado-solo-sin-resultados", pruebas=[SH_CORTA],
         viejo="    if r.get(\"abierto\"):\n        corte = _mk_cerrar_buscador(",
         nuevo="    if r.get(\"resultados\"):\n        corte = _mk_cerrar_buscador("),
    dict(id="mk-shipper-no-espera-que-se-quede-quieta", pruebas=[SH_MK + "test_espera_que_la_lista_se_quede_quieta"],
         viejo="_mk_leer_shipper(page, _mk_resultados_quietos(), MK_ESPERA_BUSCADOR)",
         nuevo="_mk_leer_shipper(page, lambda x: x.get(\"con_empresa\"), MK_ESPERA_BUSCADOR)"),
    dict(id="mk-shipper-quieta-sin-el-titulo", pruebas=[SH_MK + "test_la_lista_quieta_tambien_con_su_titulo"],
         viejo="for k in (\"resultados\", \"con_empresa\", \"titulo\"))",
         nuevo="for k in (\"resultados\", \"con_empresa\"))"),
    dict(id="mk-shipper-dice-elegi", pruebas=[SH_CORTA],
         viejo="f\"pulsé {pulsado}, pero {que}\"",
         nuevo="f\"elegí a {MK_EMPRESA} en el buscador, pero {que}\""),
    dict(id="mk-shipper-escape-con-try", pruebas=[SH_DOS],
         viejo="        el.click(timeout=4000)\n    except Exception as e:\n        return _mk_shipper_corte(",
         nuevo="        el.click(timeout=4000)\n        try:\n            page.keyboard.press(\"Escape\")\n"
               "        except Exception:\n            pass\n"
               "    except Exception as e:\n        return _mk_shipper_corte("),
    dict(id="mk-shipper-cierra-con-close", pruebas=[SH_CORTA],
         viejo="    _evidencia_antes_de_la_guarda(page, reg, f\"mk_f{f}_shipper\", ",
         nuevo="    try:\n        page.get_by_role(\"button\", name=\"Close\").click()\n"
               "    except Exception:\n        pass\n"
               "    _evidencia_antes_de_la_guarda(page, reg, f\"mk_f{f}_shipper\", "),
]

# --- Encargo 39 · commit 2: la búsqueda de salidas no corta a los 45 s, sin la rama a NO ENVIADA que nunca se
# alcanzaba (CICLO-maersk-cuatro-puntos.md) ---
SALIDAS_MK = MK + "test_la_busqueda_de_salidas_no_corta"
A_LOS_45_MK = MK + "test_a_los_45_s_sigue_a_buscar_la_nave"

MUTACIONES += [
    # Desde el encargo 41, el motivo lo arma _mk_motivo_sin_cupo: la rama va después de la línea de SIN-CUPO.
    dict(id="mk-zarpes-vuelve-la-rama", pruebas=[SALIDAS_MK],
         viejo="        return (\"SIN-CUPO\", _mk_motivo_sin_cupo(aviso, det, origen, destino))\n",
         nuevo="        return (\"SIN-CUPO\", _mk_motivo_sin_cupo(aviso, det, origen, destino))\n"
               "    if desenlace != \"con-zarpes\":\n"
               "        return _no_enviada(reg, \"MAERSK: el portal no terminó de buscar zarpes\")\n"),
    dict(id="mk-zarpes-corta-a-los-45", pruebas=[SALIDAS_MK, A_LOS_45_MK],
         viejo="procedo a buscar naves\")\n    return \"con-zarpes\", \"\"\n",
         nuevo="procedo a buscar naves\")\n    return \"indefinido\", \"\"\n"),
]

# --- Encargo 39 · commit 3: «Continue» de «Recommended services», solo si hay exactamente uno a la vista
# (CICLO-maersk-cuatro-puntos.md) ---
CONT = "test_clics.TestContinuarMaersk."
NAVE = "test_clics.TestContinuarALaNaveMaersk."
NAVE_JS = NAVE + "test_js_con_los_dos_textos"
LLAMADA_CONT = "            corte = _mk_continuar_servicios(page, reg, f)\n"

MUTACIONES += [
    # Desde el encargo 40, mkContinuar busca una lista de textos (a.textos): su test de «Booking Information» también.
    dict(id="mk-continuar-cualquier-texto", pruebas=[CONT + "test_js_continuar", NAVE_JS],
         viejo="buscados.includes(texto(x.el)) && mkVisible(x.el)",
         nuevo="buscados.some(b => texto(x.el).includes(b)) && mkVisible(x.el)"),
    dict(id="mk-continuar-distingue-mayusculas", pruebas=[CONT + "test_js_continuar", NAVE_JS],
         cambios=[("'label')) || mkTexto(e)).trim().toLowerCase();", "'label')) || mkTexto(e)).trim();"),
                  ("const buscados = a.textos.map(t => t.toLowerCase());", "const buscados = a.textos;")]),
    dict(id="mk-continuar-sin-mirar-si-se-ve", pruebas=[CONT + "test_js_continuar", NAVE_JS],
         viejo="buscados.includes(texto(x.el)) && mkVisible(x.el));",
         nuevo="buscados.includes(texto(x.el)));"),
    dict(id="mk-continuar-cuenta-el-interno", pruebas=[CONT + "test_js_continuar"],
         viejo="return vistos.filter(x => !vistos.some(y => y !== x && x.anc.includes(y.el))).map(x => x.el);",
         nuevo="return vistos.map(x => x.el);"),
    dict(id="mk-continuar-sin-enlaces", pruebas=[CONT + "test_js_continuar"],
         viejo="['mc-button', 'button', 'a'].includes(mkTag(e))", nuevo="['mc-button', 'button'].includes(mkTag(e))"),
    dict(id="mk-continuar-sin-role", pruebas=[CONT + "test_js_continuar"],
         viejo="['mc-button', 'button', 'a'].includes(mkTag(e)) || mkAtr(e, 'role') === 'button';",
         nuevo="['mc-button', 'button', 'a'].includes(mkTag(e));"),
    dict(id="mk-continuar-sin-label", pruebas=[CONT + "test_js_continuar"],
         viejo="((mkTag(e) === 'mc-button' && mkAtr(e, 'label')) || mkTexto(e)).trim()", nuevo="(mkTexto(e)).trim()"),
    dict(id="mk-continuar-pulsa-el-primero", pruebas=[CONT + "test_js_continuar"],
         viejo="    return uno && !otros.length ? uno : null;", nuevo="    return uno || null;"),
    dict(id="mk-continuar-con-alguno", pruebas=[CONT + "test_sin_uno_solo_corta", NAVE + "test_sin_uno_solo_corta"],
         viejo="        if vistos != 1:\n            continue\n",
         nuevo="        if vistos < 1:\n            continue\n"),
    dict(id="mk-continuar-no-mira-si-avanzo",
         pruebas=[CONT + "test_ya_en_additional_details", CONT + "test_clic_que_fallo_pero_avanzo",
                  NAVE + "test_ya_en_la_seleccion_de_nave", NAVE + "test_clic_que_fallo_pero_avanzo"],
         viejo="        if ya in page.url.lower():\n", nuevo="        if False:\n"),
    dict(id="mk-continuar-no-espera", pruebas=[CONT + "test_espera_que_aparezca"],
         viejo="        if intento:\n            esperar(page, 1.0)\n        if ya in page.url.lower():",
         nuevo="        if ya in page.url.lower():"),
    dict(id="mk-continuar-no-anota", pruebas=[CONT + "test_continue_uno_a_la_vista"],
         viejo="        reg.info(f\"pulsado '{MK_CONTINUAR}' en Recommended services\")\n", nuevo=""),
    dict(id="mk-continuar-sin-evidencia", pruebas=[CONT + "test_no_acepta_el_clic", LD + "test_solo_ahi"],
         viejo="        _evidencia_antes_de_la_guarda(page, reg, f\"mk_f{f}_servicios\", ",
         nuevo="        (lambda *a, **k: None)(page, reg, f\"mk_f{f}_servicios\", "),
    dict(id="mk-continuar-no-dice-lo-que-pide", pruebas=[CONT + "test_sin_uno_solo_corta"],
         viejo="buscaba, pide=_mk_lo_que_pide(page))", nuevo="buscaba)"),
    dict(id="mk-continuar-sigue-sin-cortar", pruebas=[CONT + "test_sin_uno_solo_corta"],
         viejo="    raise ObjetivoNoEncontrado(\"Recommended services de MAERSK\",",
         nuevo="    return None\n    raise ObjetivoNoEncontrado(\"Recommended services de MAERSK\","),
    dict(id="mk-continuar-pulsa-sin-releer", pruebas=[CONT + "test_releido_ya_no_es_uno"],
         viejo="            if el is None:\n                cambio = True\n                continue\n", nuevo=""),
    dict(id="mk-continuar-releido-sin-motivo", pruebas=[CONT + "test_releido_ya_no_es_uno"],
         viejo="\", pero al volver a leer ya no era uno solo\"", nuevo="\"\""),
    dict(id="mk-continuar-no-corta-en-reservar", pruebas=[CONT + "test_reservar_maersk_continua_sin_respaldo"],
         viejo=LLAMADA_CONT + "            if corte:\n                return corte\n",
         nuevo="            _mk_continuar_servicios(page, reg, f)\n"),
    dict(id="mk-continuar-vuelve-el-respaldo", pruebas=[CONT + "test_reservar_maersk_continua_sin_respaldo"],
         viejo=LLAMADA_CONT, nuevo=LLAMADA_CONT + "            getAllDeep = None\n"),
    # La foto ya no permite el respaldo en JavaScript: si vuelve a reservar_maersk, cae.
    dict(id="mk-continuar-vuelve-el-respaldo-js", pruebas=[FG],
         viejo=LLAMADA_CONT,
         nuevo=LLAMADA_CONT + "            page.evaluate(\"() => [...document.querySelectorAll('*')].find(e => { "
                              "const t = (e.textContent || '').trim(); return /^Continue$/i.test(t); })\")\n"),
    dict(id="mk-continuar-intentos", pruebas=[CONT + "test_continuar_es_el_medido"],
         viejo="MK_INTENTOS_CONTINUAR = 15 ", nuevo="MK_INTENTOS_CONTINUAR = 5 "),
]

# --- Encargo 39 · commit 4: el «Close» del buscador del Shipper, solo si la tarjeta ya muestra a AQUACHILE
# (CICLO-maersk-cuatro-puntos.md) ---
SH_CIERRA = SH_MK + "test_cierra_el_buscador_si_la_tarjeta_ya_lo_muestra"
SH_CIERRA_CORTE = SH_MK + "test_si_el_close_no_lo_deja_elegido_corta"
LLAMADA_CERRAR = "        corte = _mk_cerrar_buscador(page, reg, f, r)\n        if corte:\n            return corte\n"

MUTACIONES += [
    dict(id="mk-shipper-cerrar-fuera-del-buscador", pruebas=[SH_JS],
         viejo="const cerrar = todos.filter(x => enBuscador(x) && mkTag(x.el) === 'mc-button'",
         nuevo="const cerrar = todos.filter(x => mkTag(x.el) === 'mc-button'"),
    dict(id="mk-shipper-cerrar-sin-mirar-si-se-ve", pruebas=[SH_JS],
         viejo="&& mkAtr(x.el, 'label') === a.cerrar && mkVisible(x.el));",
         nuevo="&& mkAtr(x.el, 'label') === a.cerrar);"),
    dict(id="mk-shipper-cerrar-otro-label", pruebas=[SH_JS],
         viejo="&& mkAtr(x.el, 'label') === a.cerrar && mkVisible(x.el));",
         nuevo="&& mkAtr(x.el, 'label') !== '' && mkVisible(x.el));"),
    dict(id="mk-shipper-cerrar-sin-la-empresa", pruebas=[SH_JS],
         viejo="a.que === 'cerrar' ? (s.empresa === true ? s.cerrar : [])", nuevo="a.que === 'cerrar' ? s.cerrar"),
    dict(id="mk-shipper-cerrar-no-lo-llama", pruebas=[SH_CIERRA, SH_CORTA],
         viejo=LLAMADA_CERRAR, nuevo="        pass\n"),
    dict(id="mk-shipper-cerrar-con-varios", pruebas=[SH_CIERRA_CORTE],
         viejo="    if r.get(\"cerrar\") != 1:\n", nuevo="    if not r.get(\"cerrar\"):\n"),
    dict(id="mk-shipper-cerrar-sin-comprobar", pruebas=[SH_CIERRA_CORTE],
         viejo="\n    r, error = _mk_leer_shipper(page, _mk_shipper_listo, MK_ESPERA_SHIPPER)\n    if error:\n",
         nuevo="\n    return None\n    r, error = _mk_leer_shipper(page, _mk_shipper_listo, MK_ESPERA_SHIPPER)\n"
               "    if error:\n"),
    dict(id="mk-shipper-cerrar-sin-la-tarjeta", pruebas=[SH_CORTA],
         viejo="    if not _mk_shipper_puesto(r):\n        que = (",
         nuevo="    if not _mk_shipper_puesto(r) and not r.get(\"abierto\"):\n        que = ("),
    dict(id="mk-shipper-cerrar-otro-texto", pruebas=[SH_MK + "test_la_empresa_y_el_titulo_son_los_medidos"],
         viejo="MK_CERRAR = \"Close\"\n", nuevo="MK_CERRAR = \"Cerrar\"\n"),
]

# --- Encargo 39 · commit 5: lo que encontró la revisión de código (CICLO-maersk-cuatro-puntos.md) ---
MUTACIONES += [
    dict(id="mk-shipper-cerrar-sin-una-tarjeta", pruebas=[SH_JS],
         viejo="(s.empresa === true ? s.cerrar : [])", nuevo="(s.empresa !== false ? s.cerrar : [])"),
    dict(id="mk-shipper-empresa-con-dos-tarjetas", pruebas=[SH_JS],
         viejo="empresa: tarjetas.length === 1 ? conEmpresa(t) : null};",
         nuevo="empresa: tarjetas.some(conEmpresa) ? true : (tarjetas.length === 1 ? false : null)};"),
    dict(id="mk-shipper-cerrar-releido-sin-motivo", pruebas=[SH_CIERRA_CORTE],
         viejo="return _mk_shipper_corte(page, reg, f, releido or\n", nuevo="return _mk_shipper_corte(page, reg, f,\n"),
    dict(id="mk-shipper-cerrar-sin-evidencia", pruebas=[SH_CIERRA, LD + "test_solo_ahi"],
         viejo="    _evidencia_antes_de_la_guarda(page, reg, f\"mk_f{f}_cerrar\", ",
         nuevo="    (lambda *a, **k: None)(page, reg, f\"mk_f{f}_cerrar\", "),
]

# --- Encargo 40 · commit 1: el detector de salidas cuenta solo el «Book» de una tarjeta de salida, como la lista, y
# SIN-CUPO deja la evidencia de «Select sailing» (CICLO-maersk-busqueda-vacia.md) ---
DET_ENCABEZADO = MK + "test_el_book_del_encabezado_no_termina_la_busqueda"
DET_TARJETA = MK + "test_una_tarjeta_con_su_book_termina_la_busqueda"
DET_SIN_BOOK = MK + "test_tarjetas_sin_book_no_terminan_la_busqueda"
DET_SIN_LEER = MK + "test_si_no_puede_leer_las_tarjetas_sigue_esperando"
SINCUPO = MK + "test_sin_cupo_deja_la_evidencia_de_select_sailing"
LECTURA_DET = "            salidas = page.evaluate(_JS_MK_SALIDAS, {\"toks\": [], \"viaje\": \"\"}) or []\n"

MUTACIONES += [
    dict(id="mk-detector-cualquier-book", pruebas=[DET_ENCABEZADO],
         viejo=LECTURA_DET,
         nuevo="            if page.locator(\"mc-button, button, [role='button'], a\").filter(has_text=\"Book\")"
               ".count():\n                return \"con-zarpes\", \"\"\n" + LECTURA_DET),
    dict(id="mk-detector-tarjetas-sin-book", pruebas=[DET_SIN_BOOK],
         viejo="            if any(s.get(\"book\") for s in salidas):\n", nuevo="            if salidas:\n"),
    dict(id="mk-detector-otra-lectura", pruebas=[DET_TARJETA],
         viejo=LECTURA_DET, nuevo=LECTURA_DET.replace("\"toks\": []", "\"toks\": [\"BOOK\"]")),
    dict(id="mk-detector-sin-esperar-la-lectura", pruebas=[DET_SIN_LEER],
         viejo="                return \"con-zarpes\", \"\"\n        except Exception:\n            pass\n"
               "        esperar(page, 1.0)\n",
         nuevo="                return \"con-zarpes\", \"\"\n        except KeyError:\n            pass\n"
               "        esperar(page, 1.0)\n"),
    dict(id="mk-sincupo-sin-evidencia", pruebas=[SINCUPO],
         viejo="        _mk_detenida(page, reg, f)\n        reg.paso(f\"MAERSK: {aviso}\")\n",
         nuevo="        reg.paso(f\"MAERSK: {aviso}\")\n"),
]

# --- Encargo 40 · commit 2: «Continue to book» o «Continue» de «Booking Information», solo si hay exactamente uno a
# la vista, con el ayudante de «Continue» de «Recommended services» (CICLO-maersk-busqueda-vacia.md) ---
NAVE_RESERVAR = NAVE + "test_reservar_maersk_sigue_solo_con_el_ayudante"
LLAMADA_NAVE = "    corte = _mk_continuar_a_la_nave(page, reg, det, f, (\"Continue to book\", MK_CONTINUAR))\n"

MUTACIONES += [
    dict(id="mk-nave-continuar-un-texto", pruebas=[NAVE_RESERVAR],
         viejo=LLAMADA_NAVE, nuevo=LLAMADA_NAVE.replace(", MK_CONTINUAR))", ",))")),
    dict(id="mk-nave-continuar-no-corta-en-reservar", pruebas=[NAVE_RESERVAR],
         viejo=LLAMADA_NAVE + "    if corte:\n        return corte\n",
         nuevo="    _mk_continuar_a_la_nave(page, reg, det, f, (\"Continue to book\", MK_CONTINUAR))\n"),
    dict(id="mk-nave-continuar-vuelve-el-primero", pruebas=[NAVE_RESERVAR],
         viejo=LLAMADA_NAVE,
         nuevo="    cont_ok = page.get_by_role(\"button\", name=\"Continue\", exact=False).first\n" + LLAMADA_NAVE),
    dict(id="mk-nave-continuar-sigue-sin-cortar", pruebas=[NAVE + "test_sin_uno_solo_corta"],
         viejo="    raise ObjetivoNoEncontrado(\"Booking Information de MAERSK\",\n",
         nuevo="    return None\n    raise ObjetivoNoEncontrado(\"Booking Information de MAERSK\",\n"),
    dict(id="mk-nave-continuar-no-dice-lo-que-pide", pruebas=[NAVE + "test_sin_uno_solo_corta"],
         viejo="f\"({que})\", pide=_mk_lo_que_pide(page))", nuevo="f\"({que})\")"),
    dict(id="mk-nave-continuar-otra-pantalla",
         pruebas=[NAVE + "test_ya_en_la_seleccion_de_nave", NAVE + "test_clic_que_fallo_pero_avanzo"],
         viejo="_mk_pulsar_unico(page, textos, \"/sailings\")",
         nuevo="_mk_pulsar_unico(page, textos, \"/additional\")"),
    dict(id="mk-nave-continuar-sin-captura", pruebas=[NAVE + "test_no_acepta_el_clic_es_formulario_incompleto"],
         viejo="        reg.captura(page, f\"mk_f{f}_4_sailing\", full=True)\n        reg.paso(f\"No pude continuar",
         nuevo="        reg.paso(f\"No pude continuar"),
    dict(id="mk-nave-continuar-no-anota", pruebas=[NAVE + "test_uno_a_la_vista"],
         viejo="        reg.info(f\"pulsado el único {nombres} a la vista\")\n", nuevo=""),
    dict(id="mk-continuar-un-solo-texto", pruebas=[NAVE_JS],
         viejo="const buscados = a.textos.map(t => t.toLowerCase());",
         nuevo="const buscados = a.textos.slice(0, 1).map(t => t.toLowerCase());"),
]

# --- Encargo 40 · commit 3: la casilla del resultado con AQUACHILE, si el clic en el resultado no lo eligió, solo si su
# posición y las cifras del código de su id apuntan a la misma (CICLO-maersk-busqueda-vacia.md) ---
SH_CASILLA = SH_MK + "test_si_el_resultado_no_lo_elige_pulsa_su_casilla"
SH_CASILLA_NO = SH_MK + "test_si_la_casilla_no_coincide_corta_como_hoy"
SH_CASILLA_CORTA = SH_MK + "test_si_la_casilla_no_lo_deja_elegido_corta"
SH_CASILLA_JS = SH_MK + "test_js_casilla"
RELEER_TRAS_CASILLA = "        r, error = _mk_leer_shipper(page, _mk_shipper_listo, MK_ESPERA_SHIPPER)\n"

MUTACIONES += [
    dict(id="mk-casilla-sin-mirar-la-posicion", pruebas=[SH_CASILLA_JS],
         viejo="return porCodigo === hijos[hijos.indexOf(lb) - 1] ? {el: porCodigo, por: 'coinciden'}",
         nuevo="return true ? {el: porCodigo, por: 'coinciden'}"),
    dict(id="mk-casilla-cifras-como-parte", pruebas=[SH_CASILLA_JS],
         viejo="mkAtr(h, 'id').endsWith(cifras)", nuevo="mkAtr(h, 'id').includes(cifras)"),
    dict(id="mk-casilla-sin-alternar", pruebas=[SH_CASILLA_JS],
         viejo="            if (!alternados) return {el: null, por: 'posicion'};\n", nuevo=""),
    dict(id="mk-casilla-cualquier-input", pruebas=[SH_CASILLA_JS],
         viejo="mkTag(e) === 'input' && mkAtr(e, 'type').toLowerCase() === 'radio'", nuevo="mkTag(e) === 'input'"),
    dict(id="mk-casilla-sin-titulo", pruebas=[SH_CASILLA_JS],
         viejo="            if (!titulo) return {el: null, por: 'titulo'};\n", nuevo=""),
    dict(id="mk-casilla-con-varios-resultados", pruebas=[SH_CASILLA_JS],
         viejo="if (conLaEmpresa.length !== 1) return", nuevo="if (!conLaEmpresa.length) return"),
    dict(id="mk-casilla-sin-codigo", pruebas=[SH_CASILLA_JS],
         viejo="            if (!cifras) return {el: null, por: 'codigo'};\n", nuevo=""),
    dict(id="mk-casilla-varias-cifras", pruebas=[SH_CASILLA_JS],
         viejo="            if (porCifras.length !== 1) return {el: null, por: 'cifras'};\n", nuevo=""),
    dict(id="mk-casilla-marcar-sin-la-empresa", pruebas=[SH_CASILLA_JS],
         viejo="if (s.empresa !== false || !s.casilla) return false;", nuevo="if (!s.casilla) return false;"),
    dict(id="mk-casilla-marcada-siempre-no", pruebas=[SH_CASILLA_JS],
         viejo="marcada: s.casilla ? s.casilla.checked === true : null", nuevo="marcada: s.casilla ? false : null"),
    dict(id="mk-casilla-no-la-intenta", pruebas=[SH_CASILLA],
         viejo="    if r.get(\"empresa\") is False:\n", nuevo="    if False:\n"),
    dict(id="mk-casilla-sin-coinciden", pruebas=[SH_CASILLA_NO],
         viejo="    if c.get(\"casilla\") != \"coinciden\":\n", nuevo="    if False:\n"),
    dict(id="mk-casilla-no-la-pulsa", pruebas=[SH_CASILLA],
         viejo="pulso = page.evaluate(_JS_MK_SHIPPER_MARCAR, _MK_ARGS_SHIPPER) is True", nuevo="pulso = True"),
    dict(id="mk-casilla-sin-evidencia", pruebas=[SH_CASILLA, LD + "test_solo_ahi"],
         viejo="    _evidencia_antes_de_la_guarda(page, reg, f\"mk_f{f}_casilla\", ",
         nuevo="    (lambda *a, **k: None)(page, reg, f\"mk_f{f}_casilla\", "),
    dict(id="mk-casilla-no-vuelve-a-leer", pruebas=[SH_CASILLA],
         viejo="            return corte\n" + RELEER_TRAS_CASILLA, nuevo="            return corte\n"),
    dict(id="mk-casilla-no-dice-que-la-pulso", pruebas=[SH_CASILLA_CORTA],
         viejo="    return None, f\"{pulsado} y su casilla\"\n", nuevo="    return None, pulsado\n"),
    dict(id="mk-casilla-no-anota", pruebas=[SH_CASILLA],
         viejo="    reg.info(f\"Shipper: pulsé la casilla del resultado con {MK_EMPRESA}; antes del clic, marcada: "
               "{marcada}\")\n", nuevo=""),
    dict(id="mk-casilla-releido-sin-motivo", pruebas=[SH_CASILLA_CORTA],
         viejo="f\"{no_la}: al volver a leer la página, su posición", nuevo="f\"{no_la}: su posición"),
    dict(id="mk-casilla-sin-el-porque", pruebas=[SH_CASILLA_NO, SH_CORTA],
         viejo="        return _mk_shipper_corte(page, reg, f, f\"{no_la}: {razon}\"), pulsado\n",
         nuevo="        return _mk_shipper_corte(page, reg, f, no_la), pulsado\n"),
    dict(id="mk-casilla-sigue-si-no-la-lee", pruebas=[SH_CASILLA_NO],
         viejo="        return _mk_shipper_corte(page, reg, f, f\"{no_la}: no pude leer la página "
               "({_texto_error(e)})\"), pulsado\n",
         nuevo="        c = {\"casilla\": \"coinciden\"}\n"),
]

# --- Encargo 40 · commit 4: lo que encontró la revisión de código (CICLO-maersk-busqueda-vacia.md) ---
SH_YA = SH_MK + "test_si_al_volver_a_leer_ya_lo_muestra_no_pulsa_la_casilla"
SH_MARCADA = SH_MK + "test_anota_si_la_casilla_estaba_marcada"

MUTACIONES += [
    dict(id="mk-casilla-sin-pares", pruebas=[SH_CASILLA_JS],
         viejo="hijos.length > 0 && hijos.length % 2 === 0", nuevo="hijos.length > 0"),
    dict(id="mk-casilla-marcar-con-dos-tarjetas", pruebas=[SH_CASILLA_JS],
         viejo="if (s.empresa !== false || !s.casilla) return false;",
         nuevo="if (s.empresa === true || !s.casilla) return false;"),
    dict(id="mk-casilla-marcada-al-reves", pruebas=[SH_CASILLA, SH_MARCADA],
         viejo="{True: \"sí\", False: \"no\"}", nuevo="{True: \"no\", False: \"sí\"}"),
    dict(id="mk-casilla-marcada-sin-leer", pruebas=[SH_MARCADA],
         viejo=".get(c.get(\"marcada\"), \"no pude leerlo\")", nuevo=".get(c.get(\"marcada\"), \"no\")"),
    dict(id="mk-shipper-listo-sin-mirar-si-se-cerro", pruebas=[SH_CIERRA],
         viejo="    return _mk_shipper_puesto(r) and not r.get(\"abierto\")\n",
         nuevo="    return _mk_shipper_puesto(r)\n"),
    dict(id="mk-casilla-corta-aunque-ya-lo-muestre", pruebas=[SH_YA],
         viejo="        if _mk_shipper_puesto(r):\n"
               "            reg.info(f\"Shipper: la tarjeta «{MK_SHIPPER}» ya muestra a {MK_EMPRESA}; no pulsé la "
               "casilla del resultado\")\n            return None, pulsado\n",
         nuevo=""),
]

# --- Encargo 40 · commit 5: el panel pinta SIN-CUPO, que el detector nuevo vuelve alcanzable (revisión del informe,
# CICLO-maersk-busqueda-vacia.md) ---
MUTACIONES += [
    dict(id="panel-sin-cupo-queda-en-otro", pruebas=[LP + "test_lectura_de_cada_estado"],
         viejo="  if (est.startsWith(\"SIN-CUPO\")) return \"sin-cupo\";\n", nuevo=""),
    dict(id="panel-sin-cupo-queda-en-curso", pruebas=[LP + "test_cada_lectura_nueva_pinta_su_fila"],
         viejo="          chip(f, \"rev\", \"sin cupo\");\n          if (tr) tr.classList.remove(",
         nuevo="          chip(f, \"rev\", \"sin cupo\");\n          if (false) tr.classList.remove("),
]

# --- Encargo 41 · commits 1 y 4: antes de elegir una sugerencia de origen o de destino, las seis navieras dejan la
# lista (la captura de la ventana y el HTML); ONE, MSC, HYUNDAI y COSCO la leen con su mismo JavaScript, que pulsa solo
# con la marca true; y después del clic avisan si pulsaron sin dejarla o si la lista cambió mientras la guardaban
# (CICLO-origen-y-destino.md; el commit 4, de la revisión de código) ---
SUG = "test_evidencia.TestListaDeSugerencias."
SUG_DEJA = SUG + "test_deja_la_lista_justo_antes_de_pulsar"
SUG_SIN = SUG + "test_sin_evidencia_elige_igual_y_no_deja_nada"
SUG_NADA = SUG + "test_sin_sugerencias_deja_la_evidencia_igual"
SUG_UNA = SUG + "test_una_sola_vez_aunque_el_primer_clic_falle"
SUG_LEE = SUG + "test_si_no_puede_leer_la_lista_elige_igual_y_lo_avisa"
SUG_AL_PULSAR = SUG + "test_si_la_lista_aparece_al_pulsar_lo_avisa"
SUG_CAMBIA = SUG + "test_si_la_lista_cambia_mientras_la_guarda_lo_avisa"
SUG_REINTENTO = SUG + "test_maersk_si_vuelve_a_escribir_deja_la_del_reintento"
SUG_REINTENTO_COSCO = SUG + "test_cosco_si_vuelve_a_escribir_deja_la_del_reintento"
SUG_RESERVADORES = SUG + "test_cada_reservador_la_pide_para_su_origen_y_su_destino"
SUG_JS = SUG + "test_js_pulsa_solo_con_la_marca_true"
SUG_TEXTO_ONE = SUG + "test_one_compara_solo_el_texto_de_la_sugerencia"
SUG_SOLO_AHI = "test_evidencia.TestCadaReservadorLaDeja.test_solo_ahi"
LEE_ONE = ("                vista = \" \".join(str(_sugerencia_sin_pulsar(page, _JS_PICK_SUGGESTION, [tok])).split())\n"
           "                if vista:\n")
LEE_MSC = ("            esperar(page, 0.4)\n            if pendiente:\n"
           "                vista = \" \".join(str(_sugerencia_sin_pulsar(page, js, [ciudad])).split())\n"
           "                if vista:\n")
LEE_HMM = LEE_MSC.replace("esperar(page, 0.4)", "esperar(page, 0.5)")
EVIDENCIA_SUG = ("                    _evidencia_antes_de_la_guarda(page, reg, evidencia, "
                 "f\"con las sugerencias de {etiqueta}\",\n")
SIN_EVIDENCIA = ("_evidencia_antes_de_la_guarda(", "(lambda *a, **k: None)(")
CONTINUA_ONE = "                                                  completa=False)\n"
PULSA_ONE = "            try:\n                info = page.evaluate(_JS_PICK_SUGGESTION, [tok, True])"
EVIDENCIA_MK = ("                        _evidencia_antes_de_la_guarda(page, reg, nombre, "
                "f\"con las sugerencias de {etiqueta}\",\n"
                "                                                      completa=False)\n")
VISTA_MK = "                        _, vista, falta = la_exacta(cand)\n"
VISTA_CMA = "                        vista = \" \".join((li.first.text_content() or \"\").split())\n"
EVIDENCIA_CMA = ("                        _evidencia_antes_de_la_guarda(page, reg, evidencia, "
                 "f\"con las sugerencias de {etiqueta}\",\n")
AVISO_PENDIENTE = "    if pendiente:\n        reg.paso(f\"⚠ {etiqueta}: pulsé una sugerencia sin dejar la evidencia"

MUTACIONES += [
    # Sin la evidencia, en cada ayudante.
    dict(id="sug-one-sin-evidencia", pruebas=[SUG_DEJA, SUG_SOLO_AHI],
         viejo=LEE_ONE + EVIDENCIA_SUG, nuevo=LEE_ONE + EVIDENCIA_SUG.replace(*SIN_EVIDENCIA)),
    dict(id="sug-msc-sin-evidencia", pruebas=[SUG_DEJA, SUG_SOLO_AHI],
         viejo=LEE_MSC + EVIDENCIA_SUG, nuevo=LEE_MSC + EVIDENCIA_SUG.replace(*SIN_EVIDENCIA)),
    dict(id="sug-hmm-sin-evidencia", pruebas=[SUG_DEJA, SUG_SOLO_AHI],
         viejo=LEE_HMM + EVIDENCIA_SUG, nuevo=LEE_HMM + EVIDENCIA_SUG.replace(*SIN_EVIDENCIA)),
    dict(id="sug-cosco-sin-evidencia", pruebas=[SUG_DEJA, SUG_SOLO_AHI],
         viejo="_evidencia_antes_de_la_guarda(getattr(frame, \"page\", frame), reg, nombre,",
         nuevo="(lambda *a, **k: None)(getattr(frame, \"page\", frame), reg, nombre,"),
    dict(id="sug-mk-sin-evidencia", pruebas=[SUG_DEJA, SUG_REINTENTO, SUG_SOLO_AHI],
         viejo=EVIDENCIA_MK, nuevo=EVIDENCIA_MK.replace(*SIN_EVIDENCIA)),
    dict(id="sug-cma-sin-evidencia", pruebas=[SUG_DEJA, SUG_SOLO_AHI],
         viejo=EVIDENCIA_CMA, nuevo=EVIDENCIA_CMA.replace(*SIN_EVIDENCIA)),
    dict(id="sug-cma-entrega-sin-evidencia", pruebas=[SUG_DEJA, SUG_SOLO_AHI],
         viejo="_evidencia_antes_de_la_guarda(page, reg, evidencia, \"con las sugerencias del lugar de entrega\",",
         nuevo="(lambda *a, **k: None)(page, reg, evidencia, \"con las sugerencias del lugar de entrega\","),
    # La lectura que pulsa: con la marca true, o sin la marca y un JavaScript que pulsa si no es false.
    dict(id="sug-sin-pulsar-pulsa", pruebas=[SUG_DEJA],
         viejo="return alcance.evaluate(js, list(args) + [False]) or \"\"",
         nuevo="return alcance.evaluate(js, list(args) + [True]) or \"\""),
    dict(id="sug-js-one-sin-marca-pulsa", pruebas=[SUG_JS],
         viejo="[a[0], a[1] === true]", nuevo="[a[0], a[1] !== false]"),
    dict(id="sug-js-msc-sin-marca-pulsa", pruebas=[SUG_JS],
         viejo="if(pulsar===true) items[0].click();", nuevo="if(pulsar!==false) items[0].click();"),
    dict(id="sug-js-hmm-sin-marca-pulsa", pruebas=[SUG_JS],
         viejo="if(pulsar===true) o[0].click();", nuevo="if(pulsar!==false) o[0].click();"),
    dict(id="sug-js-cosco-sin-marca-pulsa", pruebas=[SUG_JS],
         viejo="const pulsar = Array.isArray(args) ? args[2] === true : true;",
         nuevo="const pulsar = Array.isArray(args) ? args[2] !== false : true;"),
    # El JavaScript: pulsa también al solo leer, dice algo sin sugerencias, no dice el texto, o no pulsa con el texto
    # solo.
    dict(id="sug-js-one-pulsa-igual", pruebas=[SUG_JS],
         viejo="        if (pulsar) cand[0].click();\n", nuevo="        cand[0].click();\n"),
    dict(id="sug-js-one-sin-cual", pruebas=[SUG_JS],
         viejo="    return pulsar ? 'CLICK[' + clicked + '] CANDS[' + dump + ']' : clicked;\n",
         nuevo="    return 'CLICK[' + clicked + '] CANDS[' + dump + ']';\n"),
    dict(id="sug-js-one-sin-texto", pruebas=[SUG_JS],
         viejo="\n            + ' «' + (cand[0].textContent||'').trim().slice(0,45) + '»';\n", nuevo=";\n"),
    dict(id="sug-js-msc-pulsa-igual", pruebas=[SUG_JS],
         viejo="if(items.length){ if(pulsar===true) items[0].click();", nuevo="if(items.length){ items[0].click();"),
    dict(id="sug-js-hmm-pulsa-igual", pruebas=[SUG_JS],
         viejo="if(o.length){if(pulsar===true) o[0].click();", nuevo="if(o.length){o[0].click();"),
    dict(id="sug-js-cosco-chile-pulsa-igual", pruebas=[SUG_JS],
         viejo="if (ch) { if (pulsar) ch.click();", nuevo="if (ch) { ch.click();"),
    dict(id="sug-js-cosco-exacta-pulsa-igual", pruebas=[SUG_JS],
         viejo="if (exactStart) { if (pulsar) exactStart.click();", nuevo="if (exactStart) { exactStart.click();"),
    dict(id="sug-js-cosco-primera-pulsa-igual", pruebas=[SUG_JS],
         viejo="    if (pulsar) opts[0].click();\n", nuevo="    opts[0].click();\n"),
    dict(id="sug-js-cosco-texto-solo-no-pulsa", pruebas=[SUG_JS],
         viejo="? args[2] === true : true;", nuevo="? args[2] === true : false;"),
    # Antes de la evidencia, nada: ni una espera, ni una tecla, ni otro clic; la de la ventana, no la página completa; y
    # la evidencia antes del clic.
    dict(id="sug-msc-espera-antes-de-la-lista", pruebas=[SUG_DEJA],
         viejo=LEE_MSC + EVIDENCIA_SUG, nuevo=LEE_MSC + "                    esperar(page, 2.0)\n" + EVIDENCIA_SUG),
    dict(id="sug-hmm-clic-antes-de-la-lista", pruebas=[SUG_DEJA],
         viejo=LEE_HMM + EVIDENCIA_SUG,
         nuevo=LEE_HMM + "                    page.locator(\"#cerrarAviso\").first.click()\n" + EVIDENCIA_SUG),
    dict(id="sug-cma-tecla-antes-de-la-lista", pruebas=[SUG_DEJA],
         viejo=VISTA_CMA + EVIDENCIA_CMA,
         nuevo=VISTA_CMA + "                        page.keyboard.press(\"Escape\")\n" + EVIDENCIA_CMA),
    dict(id="sug-mk-pagina-entera", pruebas=[SUG_DEJA],
         viejo=EVIDENCIA_MK, nuevo=EVIDENCIA_MK.replace("completa=False", "completa=True")),
    dict(id="sug-cma-despues-del-clic", pruebas=[SUG_DEJA],
         viejo="                    vista = \"\"\n                    if pendiente:\n" + VISTA_CMA,
         nuevo="                    li.first.click(timeout=3000)\n                    vista = \"\"\n"
               "                    if pendiente:\n" + VISTA_CMA),
    # Una vez por lista: sin marcarla como dejada, el clic que falla la vuelve a dejar.
    dict(id="sug-una-vez-one", pruebas=[SUG_UNA],
         viejo=EVIDENCIA_SUG + CONTINUA_ONE + "                    pendiente = False\n" + PULSA_ONE,
         nuevo=EVIDENCIA_SUG + CONTINUA_ONE + PULSA_ONE),
    dict(id="sug-una-vez-mk", pruebas=[SUG_UNA],
         viejo=EVIDENCIA_MK + "                        pendiente = False\n", nuevo=EVIDENCIA_MK),
    # Sin 'evidencia', la deja igual (sin nombre); la deja sin mirar si hay lista; o si la lectura falla, la da por
    # leída.
    dict(id="sug-cma-siempre", pruebas=[SUG_SIN],
         viejo="    pendiente = bool(evidencia)\n    # 1) clic real", nuevo="    pendiente = True\n    # 1) clic real"),
    dict(id="sug-msc-sin-mirar-la-lista", pruebas=[SUG_NADA],
         viejo=LEE_MSC, nuevo=LEE_MSC.replace("                if vista:\n", "                if True:\n")),
    dict(id="sug-sin-pulsar-traga", pruebas=[SUG_LEE],
         viejo="        return alcance.evaluate(js, list(args) + [False]) or \"\"\n    except Exception:\n"
               "        return \"\"\n",
         nuevo="        return alcance.evaluate(js, list(args) + [False]) or \"\"\n    except Exception:\n"
               "        return \"x\"\n"),
    # MAERSK y COSCO, al volver a escribir la ciudad: con el mismo nombre, o sin dejar esa lista.
    dict(id="sug-mk-reintento-mismo-nombre", pruebas=[SUG_REINTENTO],
         viejo="nombre = evidencia + (\"_reintento\" if intento and evidencia else \"\")", nuevo="nombre = evidencia"),
    dict(id="sug-mk-reintento-sin-lista", pruebas=[SUG_REINTENTO],
         viejo="        pendiente = bool(evidencia)\n        nombre = evidencia + (",
         nuevo="        pendiente = bool(evidencia) and not intento\n        nombre = evidencia + ("),
    dict(id="sug-cosco-reintento-mismo-nombre", pruebas=[SUG_REINTENTO_COSCO],
         viejo="nombre = evidencia + (\"_reintento\" if reintento and evidencia else \"\")",
         nuevo="nombre = evidencia"),
    dict(id="sug-cosco-reintento-sin-lista", pruebas=[SUG_REINTENTO_COSCO],
         viejo="pendiente, vista = bool(evidencia), \"\"",
         nuevo="pendiente, vista = bool(evidencia) and not reintento, \"\""),
    # COSCO: la evidencia del marco, que no sabe capturar, en vez de su página; o la lectura en la página, que no ve la
    # lista del marco.
    dict(id="sug-cosco-evidencia-del-marco", pruebas=[SUG_DEJA],
         viejo="_evidencia_antes_de_la_guarda(getattr(frame, \"page\", frame), reg, nombre,",
         nuevo="_evidencia_antes_de_la_guarda(frame, reg, nombre,"),
    dict(id="sug-cosco-lee-en-la-pagina", pruebas=[SUG_DEJA],
         viejo="str(_sugerencia_sin_pulsar(frame, _JS_COSCO_AUTO_PICK,",
         nuevo="str(_sugerencia_sin_pulsar(getattr(frame, \"page\", frame), _JS_COSCO_AUTO_PICK,"),
    # Los avisos después del clic: sin el de pulsar sin dejarla, sin el de la lista que cambió, sin la llamada, o con lo
    # que pulsaría leído después de la evidencia.
    dict(id="sug-avisa-sin-pendiente", pruebas=[SUG_LEE, SUG_AL_PULSAR],
         viejo=AVISO_PENDIENTE, nuevo=AVISO_PENDIENTE.replace("    if pendiente:\n", "    if False:\n")),
    dict(id="sug-avisa-sin-cambio", pruebas=[SUG_CAMBIA],
         viejo="    elif vista and pulsada and vista != pulsada:\n", nuevo="    elif False:\n"),
    dict(id="sug-msc-no-avisa", pruebas=[SUG_CAMBIA, SUG_AL_PULSAR],
         viejo="        _avisar_lista_distinta(reg, etiqueta, evidencia, vista, \" \".join(picked.split()), "
               "pendiente)\n        esperar(page, 0.6)\n",
         nuevo="        esperar(page, 0.6)\n"),
    dict(id="sug-mk-no-avisa", pruebas=[SUG_CAMBIA],
         viejo="                    _avisar_lista_distinta(reg, etiqueta, nombre, vista, txt, False)\n", nuevo=""),
    dict(id="sug-mk-lee-despues-de-la-evidencia", pruebas=[SUG_CAMBIA],
         viejo=VISTA_MK + EVIDENCIA_MK, nuevo=EVIDENCIA_MK + VISTA_MK),
    dict(id="sug-cma-entrega-no-avisa", pruebas=[SUG_CAMBIA],
         viejo="                _avisar_lista_distinta(reg, \"Lugar de entrega\", evidencia, vista, "
               "\" \".join(bruto.split()), False)\n",
         nuevo=""),
    # ONE no anota cuál pulsó.
    dict(id="sug-one-no-anota-cual", pruebas=[SUG_DEJA],
         viejo="sugerencia seleccionada: {pulsada}\")", nuevo="sugerencia seleccionada\")"),
    # Cada reservador: con otro nombre, los nombres cruzados, sin la evidencia, sin el modo o con la del commodity.
    dict(id="sug-one-origen-otro-nombre", pruebas=[SUG_RESERVADORES],
         viejo="evidencia=f\"one_f{f}_origen\"", nuevo="evidencia=f\"one_f{f}_destino\""),
    dict(id="sug-hmm-nombres-cruzados", pruebas=[SUG_RESERVADORES], cambios=[
        ("\"#schOriginText\", reserva[\"pol\"], reg, \"Origen\", evidencia=f\"hmm_f{f}_origen\"",
         "\"#schOriginText\", reserva[\"pol\"], reg, \"Origen\", evidencia=f\"hmm_f{f}_destino\""),
        ("\"#schDestinationText\", dest, reg, \"Destino\", evidencia=f\"hmm_f{f}_destino\"",
         "\"#schDestinationText\", dest, reg, \"Destino\", evidencia=f\"hmm_f{f}_origen\"")]),
    dict(id="sug-one-commodity-con-evidencia", pruebas=[SUG_RESERVADORES],
         viejo="        commodity, reg, \"Commodity\")\n",
         nuevo="        commodity, reg, \"Commodity\", evidencia=f\"one_f{f}_commodity\")\n"),
    dict(id="sug-fill-port-no-la-pasa", pruebas=[SUG_DEJA, SUG_RESERVADORES],
         viejo="reg, etiqueta, evidencia=evidencia)\n", nuevo="reg, etiqueta)\n"),
    dict(id="sug-msc-destino-sin-evidencia", pruebas=[SUG_RESERVADORES],
         viejo="reg, \"Port of Discharge\", evidencia=f\"msc_f{f}_destino\")", nuevo="reg, \"Port of Discharge\")"),
    dict(id="sug-cosco-destino-sin-evidencia", pruebas=[SUG_RESERVADORES],
         viejo="\"Destination\",\n                               evidencia=f\"cosco_f{f}_destino\")",
         nuevo="\"Destination\")"),
    dict(id="sug-mk-destino-otro-nombre", pruebas=[SUG_RESERVADORES],
         viejo="evidencia=f\"mk_f{f}_destino\"", nuevo="evidencia=f\"mk_f{f}_origen\""),
    dict(id="sug-cma-origen-sin-modo", pruebas=[SUG_RESERVADORES],
         viejo="evidencia=f\"cma_f{f}_origen_{modo}\"", nuevo="evidencia=f\"cma_f{f}_origen\""),
    dict(id="sug-cma-entrega-sin-modo", pruebas=[SUG_RESERVADORES],
         viejo="ent = _cma_entrega(page, dest_fin, reg, evidencia=f\"cma_f{f}_entrega_{modo}\")",
         nuevo="ent = _cma_entrega(page, dest_fin, reg)"),
]

# --- Encargo 41 · commits 2 y 4: el motivo de SIN-CUPO dice el origen y el destino con que buscó MAERSK: de cada
# campo, la sugerencia que pulsó _mk_ciudad y, si el campo no quedó con ella, lo que quedó (CICLO-origen-y-destino.md;
# el commit 4, de la revisión de código) ---
RUTA_MK = SUG + "test_maersk_devuelve_la_sugerencia_y_lo_que_quedo_en_el_campo"
SINCUPO_RUTA = MK + "test_sin_cupo_dice_el_origen_y_el_destino_con_que_busco"
SINCUPO_VERDE = MK + "test_el_motivo_de_sin_cupo_no_se_pinta_de_verde"
TXT_MK = "    textos = [\" \".join((t or \"\").split()) for t in cy.all_text_contents()]\n"
SUG_EXACTA = SUG + "test_maersk_elige_la_unica_container_yard_que_dice_lo_escrito"

MUTACIONES += [
    # _mk_ciudad devuelve si eligió, como hasta el encargo 41; sin lo que quedó en el campo; el texto cortado a 45 o en
    # varias líneas; la sugerencia aunque no haya quedado en el campo; o el log.txt con el texto entero.
    dict(id="mk-ruta-devuelve-si-eligio", pruebas=[RUTA_MK],
         viejo="    return (picked, quedo)\n", nuevo="    return bool(picked)\n"),
    dict(id="mk-ruta-cortada-a-45", pruebas=[RUTA_MK],
         viejo=TXT_MK, nuevo="    textos = [(t or \"\").strip()[:45] for t in cy.all_text_contents()]\n"),
    dict(id="mk-ruta-en-varias-lineas", pruebas=[RUTA_MK],
         viejo=TXT_MK, nuevo="    textos = [(t or \"\").strip() for t in cy.all_text_contents()]\n"),
    dict(id="mk-ruta-campo-en-varias-lineas", pruebas=[RUTA_MK],
         viejo="quedo = en_una_linea(loc.input_value(timeout=2000))",
         nuevo="quedo = (loc.input_value(timeout=2000) or \"\").strip()"),
    dict(id="mk-ruta-aunque-no-quede", pruebas=[RUTA_MK],
         viejo="else \"vacío\")\n                        picked = \"\"\n",
         nuevo="else \"vacío\")\n                        picked = txt\n"),
    dict(id="mk-ruta-log-entera", pruebas=[RUTA_MK],
         viejo="{picked[:45] or 'sin sugerencia'}", nuevo="{picked or 'sin sugerencia'}"),
    # El texto: sin lo que quedó en el campo, sin las comillas, o con «elegida», que el panel pinta de verde.
    dict(id="mk-ruta-buscada-sin-el-campo", pruebas=[SINCUPO_RUTA],
         viejo="        if quedo and quedo != sugerencia:\n", nuevo="        if False:\n"),
    dict(id="mk-ruta-buscada-sin-comillas", pruebas=[SINCUPO_RUTA],
         viejo="        return f\"{nombre} «{sugerencia}»\"\n", nuevo="        return f\"{nombre} {sugerencia}\"\n"),
    dict(id="mk-ruta-buscada-elegida", pruebas=[SINCUPO_RUTA, SINCUPO_VERDE],
         viejo="f\"{nombre} (ninguna sugerencia quedó en el campo)\"",
         nuevo="f\"{nombre} sin una sugerencia elegida\""),
    # El motivo de SIN-CUPO sin la ruta, con el origen y el destino al revés (en el motivo o en la llamada), o sin
    # guardar lo que devuelve _mk_ciudad.
    dict(id="mk-sincupo-sin-ruta", pruebas=[SINCUPO_RUTA],
         viejo="busqué con {_mk_ruta_buscada(origen, destino)} \"\n", nuevo="\"\n"),
    dict(id="mk-sincupo-ruta-al-reves", pruebas=[SINCUPO_RUTA],
         viejo="{_mk_ruta_buscada(origen, destino)}", nuevo="{_mk_ruta_buscada(destino, origen)}"),
    dict(id="mk-sincupo-llamada-al-reves", pruebas=[SINCUPO_RUTA],
         viejo="_mk_motivo_sin_cupo(aviso, det, origen, destino))\n",
         nuevo="_mk_motivo_sin_cupo(aviso, det, destino, origen))\n"),
    dict(id="mk-origen-sin-guardar", pruebas=[SINCUPO_RUTA],
         viejo="    origen = _mk_ciudad(page, reserva[\"pol\"]",
         nuevo="    origen = \"\"\n    _mk_ciudad(page, reserva[\"pol\"]"),
]

# --- Encargo 41 · commit 5 (revisión del informe): el aviso de ONE compara solo el texto de la sugerencia, no su
# etiqueta, su clase ni su posición (_texto_de_la_sugerencia); y vuelve la de HYUNDAI sin la evidencia del origen
# (CICLO-origen-y-destino.md) ---
AVISO_ONE = ("        _avisar_lista_distinta(reg, etiqueta, evidencia, _texto_de_la_sugerencia(vista),\n"
             "                               _texto_de_la_sugerencia(pulsada), pendiente)\n")

MUTACIONES += [
    # La descripción entera, como hasta la revisión del informe; el ayudante que la devuelve entera; o el texto con sus
    # comillas.
    dict(id="sug-one-compara-la-descripcion", pruebas=[SUG_TEXTO_ONE, SUG_CAMBIA],
         viejo=AVISO_ONE,
         nuevo="        _avisar_lista_distinta(reg, etiqueta, evidencia, vista, pulsada, pendiente)\n"),
    dict(id="sug-one-texto-entero", pruebas=[SUG_TEXTO_ONE, SUG_CAMBIA],
         viejo="    return descripcion[i + 2:-1] if i >= 0 and descripcion.endswith(\"»\") else descripcion\n",
         nuevo="    return descripcion\n"),
    dict(id="sug-one-texto-con-comillas", pruebas=[SUG_CAMBIA],
         viejo="    return descripcion[i + 2:-1] if i >= 0",
         nuevo="    return descripcion[i + 1:] if i >= 0"),
    # HYUNDAI sin la evidencia del origen: el commit 4 la quitó sin reemplazo, y su ancla seguía en el código (revisión
    # del informe, B5).
    dict(id="sug-hmm-origen-sin-evidencia", pruebas=[SUG_RESERVADORES],
         viejo=", evidencia=f\"hmm_f{f}_origen\")", nuevo=")"),
]

# --- Encargo 41 · commit 6 (segunda revisión del informe): el JavaScript de ONE, llamado con el texto solo, pulsa, como
# antes; el commit 4 quitó esta mutación sin reemplazo (CICLO-origen-y-destino.md) ---
MUTACIONES += [
    dict(id="sug-js-one-texto-solo-no-pulsa", pruebas=[SUG_JS], viejo=": [a, true];", nuevo=": [a, false];"),
]

# --- Encargo 42 · commit 1: la fila con nave y sin puerto de carga o sin destino queda NO ENVIADA sin entrar al
# portal, en el panel web, en la consola y con un decorador en cada reservador, como la fila sin nave
# (CICLO-maersk-y-fila-sin-ruta.md) ---
FSR = "test_ayudantes.TestFilaSinRuta."
FSR_DECORADOR = FSR + "test_ningun_reservador_abre_el_portal_sin_ruta"
SIN_RUTA_WEB = CO + "test_fila_sin_puerto_o_sin_destino_no_abre_el_portal"
SIN_RUTA_CONSOLIDADO = CO + "test_fila_sin_puerto_en_consolidado"
SIN_RUTA_CONSOLA = ER + "test_fila_sin_puerto_o_sin_destino_no_abre_el_portal"
REGLA_PUERTO = '    if not _puerto_de_carga(pol):\n        return FILA_SIN_PUERTO\n'
REGLA_DESTINO = '    if not _ciudad_de(destino):\n        return FILA_SIN_DESTINO\n'
DESTINO_DE_LA_FILA = '    destino = (reserva or {}).get("destino_final") or (reserva or {}).get("destino_orig")\n'
PASA_LA_RUTA = ('            return _sin_ruta(reg, (reserva or {}).get("fila"), falta)\n'
                '        return reservar(page, reserva, creds, reg, on_pausa=on_pausa)\n')

MUTACIONES += [
    # La regla: sin una de sus dos comprobaciones, con la celda entera en vez de lo que se escribe («, CHILE»
    # traería el puerto), con un solo destino, o el destino antes que el puerto.
    dict(id="ruta-sin-puerto-pasa", pruebas=[FSR + "test_falta_en_la_fila", FSR_DECORADOR, SIN_RUTA_WEB,
                                             SIN_RUTA_CONSOLA],
         viejo=REGLA_PUERTO, nuevo=""),
    dict(id="ruta-sin-destino-pasa", pruebas=[FSR + "test_falta_en_la_fila", FSR_DECORADOR, SIN_RUTA_WEB,
                                              SIN_RUTA_CONSOLA],
         viejo=REGLA_DESTINO, nuevo=""),
    dict(id="ruta-puerto-con-la-celda-entera", pruebas=[FSR + "test_falta_en_la_fila", FSR_DECORADOR, SIN_RUTA_WEB],
         viejo=REGLA_PUERTO, nuevo=REGLA_PUERTO.replace("_puerto_de_carga(pol)", 'str(pol or "").strip()')),
    dict(id="ruta-destino-con-la-celda-entera", pruebas=[FSR + "test_falta_en_la_fila"],
         viejo=REGLA_DESTINO, nuevo=REGLA_DESTINO.replace("_ciudad_de(destino)", 'str(destino or "").strip()')),
    dict(id="ruta-destino-solo-el-final", pruebas=[FSR + "test_falta_en_la_fila"],
         viejo=DESTINO_DE_LA_FILA, nuevo='    destino = (reserva or {}).get("destino_final")\n'),
    dict(id="ruta-destino-solo-el-original", pruebas=[FSR + "test_falta_en_la_fila"],
         viejo=DESTINO_DE_LA_FILA, nuevo='    destino = (reserva or {}).get("destino_orig")\n'),
    dict(id="ruta-el-destino-primero", pruebas=[FSR + "test_falta_en_la_fila"],
         cambios=[(REGLA_PUERTO, ""), (REGLA_DESTINO, REGLA_DESTINO + REGLA_PUERTO)]),
    # Los motivos y el aviso.
    dict(id="ruta-motivo-puerto", pruebas=[FSR + "test_falta_en_la_fila", FSR_DECORADOR, SIN_RUTA_WEB,
                                           SIN_RUTA_CONSOLA],
         viejo='FILA_SIN_PUERTO = "a la fila le falta el puerto de carga"', nuevo='FILA_SIN_PUERTO = "sin puerto"'),
    dict(id="ruta-motivo-destino", pruebas=[FSR + "test_falta_en_la_fila", FSR_DECORADOR, SIN_RUTA_WEB,
                                            SIN_RUTA_CONSOLA],
         viejo='FILA_SIN_DESTINO = "a la fila le falta el destino"', nuevo='FILA_SIN_DESTINO = "sin destino"'),
    dict(id="ruta-sin-aviso", pruebas=[FSR_DECORADOR, SIN_RUTA_WEB, SIN_RUTA_CONSOLA],
         viejo='    reg.paso(f"✗ fila {fila}: {NO_ENVIADA} · {falta}. No entro al portal por ella: escribe {que} '
               'en la planilla y "\n             f"vuelve a armar la reserva.")\n', nuevo=""),
    dict(id="ruta-aviso-siempre-el-puerto", pruebas=[FSR_DECORADOR, SIN_RUTA_WEB, SIN_RUTA_CONSOLA],
         viejo='    que = "el puerto de carga" if falta == FILA_SIN_PUERTO else "el destino"\n',
         nuevo='    que = "el puerto de carga"\n'),
    dict(id="ruta-omitida", pruebas=[FSR_DECORADOR, SIN_RUTA_WEB, SIN_RUTA_CONSOLA],
         viejo="    return (NO_ENVIADA, falta)\n", nuevo='    return ("OMITIDO", falta)\n'),
    # El decorador: deja pasar la fila sin ruta, o la con ruta sin on_pausa, su nombre o su documentación.
    dict(id="ruta-el-decorador-deja-pasar", pruebas=[FSR_DECORADOR],
         viejo="        if falta:\n            return _sin_ruta(",
         nuevo="        if False:\n            return _sin_ruta("),
    dict(id="ruta-decorador-sin-on-pausa", pruebas=[FSR + "test_con_la_ruta_pasa_igual"],
         viejo=PASA_LA_RUTA, nuevo=PASA_LA_RUTA.replace(", on_pausa=on_pausa)", ")")),
    dict(id="ruta-decorador-sin-nombre", pruebas=[FSR + "test_con_la_ruta_pasa_igual"],
         viejo="    reservar_con_la_ruta.__name__ = reservar.__name__\n", nuevo=""),
    dict(id="ruta-decorador-sin-documentacion", pruebas=[FSR + "test_con_la_ruta_pasa_igual"],
         viejo="    reservar_con_la_ruta.__doc__ = reservar.__doc__\n", nuevo=""),
    # Por fuera del de la nave: a la fila sin nave le diría que le falta el puerto.
    dict(id="ruta-por-fuera-de-la-nave", pruebas=[FSR + "test_sin_nave_dice_sin_nave"],
         viejo='@_con_la_nave_de_la_fila\n@_con_la_ruta_de_la_fila\n@_sin_clic_a_ciegas("one")\n',
         nuevo='@_con_la_ruta_de_la_fila\n@_con_la_nave_de_la_fila\n@_sin_clic_a_ciegas("one")\n'),
] + [
    dict(id=f"ruta-{nav}-sin-decorador", pruebas=[FSR_DECORADOR, SC + "test_cada_reservador_que_corta_esta_decorado"],
         viejo=f'@_con_la_ruta_de_la_fila\n@_sin_clic_a_ciegas("{pref}")\n', nuevo=f'@_sin_clic_a_ciegas("{pref}")\n')
    for nav, pref in (("one", "one"), ("msc", "msc"), ("cosco", "cosco"), ("hyundai", "hmm"), ("maersk", "mk"), ("cma", "cma"))
] + [
    # El panel web: la fila sin ruta va al portal, se abre el navegador sin filas, no queda el resultado, o en
    # CONSOLIDADO se anota en cada naviera.
    dict(id="ruta-web-va-al-portal", pruebas=[SIN_RUTA_WEB, SIN_RUTA_CONSOLIDADO],
         viejo="            sub_elegidas = [f for f in sub_elegidas if not _falta_en_la_fila(f)]\n", nuevo=""),
    dict(id="ruta-web-abre-el-navegador", pruebas=[SIN_RUTA_WEB, SIN_RUTA_CONSOLIDADO],
         viejo='            if not sub_elegidas:\n                reg.paso(f"Ninguna fila de {nombre} con nave',
         nuevo='            if False:\n                reg.paso(f"Ninguna fila de {nombre} con nave'),
    dict(id="ruta-web-sin-resultado", pruebas=[SIN_RUTA_WEB],
         viejo='_sin_ruta(reg, rsv["fila"], _falta_en_la_fila(rsv))\n                with _LOCK:\n'
               '                    _WEB["resultados"][str(rsv["fila"])] = {\n',
         nuevo='_sin_ruta(reg, rsv["fila"], _falta_en_la_fila(rsv))\n                with _LOCK:\n'
               '                    _ = {\n'),
    dict(id="ruta-web-marca-en-cada-naviera", pruebas=[SIN_RUTA_CONSOLIDADO],
         viejo="            for rsv in [f for f in sub_elegidas if _falta_en_la_fila(f)]:\n",
         nuevo="            for rsv in [f for f in elegidas if _falta_en_la_fila(f)]:\n"),
    # La consola: no la anota, va al portal, se abre el navegador sin filas, o sin resumen.
    dict(id="ruta-consola-no-anota", pruebas=[SIN_RUTA_CONSOLA],
         viejo='            anotar(i, rsv, *_sin_ruta(reg, rsv["fila"], _falta_en_la_fila(rsv)))\n',
         nuevo="            pass\n"),
    dict(id="ruta-consola-va-al-portal", pruebas=[SIN_RUTA_CONSOLA],
         viejo="    con_nave = [(i, rsv) for i, rsv in con_nave if not _falta_en_la_fila(rsv)]\n", nuevo=""),
    dict(id="ruta-consola-abre-el-navegador", pruebas=[SIN_RUTA_CONSOLA],
         viejo='    if not con_nave:\n        reg.paso(f"Ninguna fila de {nombre} con nave',
         nuevo='    if False:\n        reg.paso(f"Ninguna fila de {nombre} con nave'),
    dict(id="ruta-consola-sin-resumen", pruebas=[SIN_RUTA_CONSOLA],
         viejo='                 f"entro al portal.")\n        resumen()\n',
         nuevo='                 f"entro al portal.")\n'),
]

# --- Encargo 42 · commit 2: sin una sugerencia elegida en el origen, el destino o el lugar de entrega, NO ENVIADA, y
# ninguna naviera sigue; ningún ayudante escribe ni pulsa nada con el texto vacío (CICLO-maersk-y-fila-sin-ruta.md) ---
TSN = "test_clics.TestSinSugerenciaNoSigue.test_sin_sugerencia_ninguna_naviera_sigue"
VACIO = SUG + "test_con_el_texto_vacio_no_escribe_ni_pulsa"
POD_PUERTO = ('                raise ObjetivoNoEncontrado("POD de CMA", _sugerencia_que_elegir(dest_p))\n'
              '            det.append("POD=" + dest_p)\n        elif modo == "ramp":\n')
POD_RAMP = ('                raise ObjetivoNoEncontrado("POD de CMA", _sugerencia_que_elegir(dest_p))\n'
            '            det.append("POD=" + dest_p)\n            esperar(page, 0.8)\n')
CIUDAD = '    texto = str(celda or "").split(",")[0].strip()\n'

MUTACIONES += [
    # Cada corte de los reservadores, sin su raise: la reserva seguiría sin el campo, como hasta el encargo 42.
    dict(id=f"sin-sugerencia-{i}-sigue", pruebas=[TSN], viejo=v, nuevo=v.split("raise")[0] + "pass\n")
    for i, v in enumerate([
        '        raise ObjetivoNoEncontrado("Origen de ONE", _sugerencia_que_elegir(reserva["pol"]))\n',
        '        raise ObjetivoNoEncontrado("Destino de ONE", _sugerencia_que_elegir(dest))\n',
        '        raise ObjetivoNoEncontrado("Port of Load de MSC", _sugerencia_que_elegir(reserva["pol"]))\n',
        '        raise ObjetivoNoEncontrado("Port of Discharge de MSC", _sugerencia_que_elegir(dest))\n',
        '        raise ObjetivoNoEncontrado("Destination de COSCO", _sugerencia_que_elegir(dest_ciudad))\n',
        '        raise ObjetivoNoEncontrado("Origen de HYUNDAI", _sugerencia_que_elegir(reserva["pol"]))\n',
        '        raise ObjetivoNoEncontrado("Destino de HYUNDAI", _sugerencia_que_elegir(dest))\n',
        '            raise ObjetivoNoEncontrado("Origen de CMA", _sugerencia_que_elegir(reserva["pol"]))\n',
        '                raise ObjetivoNoEncontrado("POD de CMA", _sugerencia_que_elegir(dest_orig))\n',
        '                raise ObjetivoNoEncontrado("Lugar de entrega de CMA", _sugerencia_que_elegir(dest_fin))\n',
        '                raise ObjetivoNoEncontrado("Lugar de entrega de CMA", '
        '_sugerencia_que_elegir(dest_p) + aviso)\n',
    ])
] + [
    dict(id="sin-sugerencia-cma-pod-puerto-sigue", pruebas=[TSN], viejo=POD_PUERTO,
         nuevo=POD_PUERTO.replace('raise ObjetivoNoEncontrado("POD de CMA", _sugerencia_que_elegir(dest_p))', "pass")),
    dict(id="sin-sugerencia-cma-pod-ramp-sigue", pruebas=[TSN], viejo=POD_RAMP,
         nuevo=POD_RAMP.replace('raise ObjetivoNoEncontrado("POD de CMA", _sugerencia_que_elegir(dest_p))', "pass")),
    # El motivo: otro texto, o la celda entera.
    dict(id="sin-sugerencia-otro-motivo", pruebas=[TSN, CMA_MANT],
         viejo='    return f"una sugerencia que elegir para «{_ciudad_de(celda)}»"\n',
         nuevo='    return f"la sugerencia de «{_ciudad_de(celda)}»"\n'),
    dict(id="ciudad-con-la-celda-entera", pruebas=[TSN, FSR + "test_falta_en_la_fila", FSR + "test_ciudad_de"],
         viejo=CIUDAD, nuevo='    texto = str(celda or "").strip()\n'),
    # (Desde el commit 4, sin los espacios de los extremos solo cambia el texto: la palabra se pide igual.)
    dict(id="ciudad-sin-quitar-los-espacios", pruebas=[FSR + "test_ciudad_de"],
         viejo=CIUDAD, nuevo='    texto = str(celda or "").split(",")[0]\n'),
] + [
    # Los siete ayudantes, sin el tope del texto vacío: escribirían y pulsarían la sugerencia a la vista.
    dict(id=f"vacio-{nombre}-escribe", pruebas=[VACIO], nuevo="",
         viejo=si + "        raise ObjetivoNoEncontrado(" + corte)
    for nombre, si, corte in (
        ("one", "    if not _ciudad_de(keyword):\n", 'f"{etiqueta} de ONE", _TEXTO_DE_LA_FILA)\n'),
        ("msc", "    if not _ciudad_de(ciudad):\n", 'f"{etiqueta} de MSC", _TEXTO_DE_LA_FILA)\n'),
        ("cosco", '    if not str(match_texto or "").strip():\n', 'f"{etiqueta} de COSCO", _TEXTO_DE_LA_FILA)\n'),
        ("hmm", "    if not _ciudad_de(texto):\n", 'f"{etiqueta} de HYUNDAI", _TEXTO_DE_LA_FILA)\n'),
        ("mk", "    if not ciudad:\n", 'f"{etiqueta} de MAERSK", _TEXTO_DE_LA_FILA)\n'),
        ("cma-puerto", "    if not ciudad:\n", 'f"{etiqueta} de CMA", _TEXTO_DE_LA_FILA)\n'),
        ("cma-entrega", "    if not ciudad:\n", '"Lugar de entrega de CMA", _TEXTO_DE_LA_FILA)\n'),
    )
] + [
    dict(id="vacio-otro-motivo", pruebas=[VACIO],
         viejo='_TEXTO_DE_LA_FILA = "en la celda de la planilla, antes de su primera coma, el texto para buscar en la '
               'lista"',
         nuevo='_TEXTO_DE_LA_FILA = "el texto de la fila"'),
]

# --- Encargo 42 · commit 3: sin una sugerencia que elegir, la evidencia de la lista queda igual, con el mismo nombre,
# al terminar la espera que el ayudante ya tenía (_evidencia_sin_sugerencia; CICLO-maersk-y-fila-sin-ruta.md) ---
SIN_LISTA_ONE = ('            if pendiente:\n'
                 '                _evidencia_sin_sugerencia(page, reg, evidencia, etiqueta)\n'
                 '            raise ObjetivoNoEncontrado(f"{etiqueta} de ONE", ')
SIN_LISTA_MSC = ('            if pendiente:\n'
                 '                _evidencia_sin_sugerencia(page, reg, evidencia, etiqueta)\n'
                 '            raise ObjetivoNoEncontrado(f"{etiqueta} de MSC", ')
SIN_LISTA_COSCO = ('            if not picked and pendiente:\n'
                   '                _evidencia_sin_sugerencia(getattr(frame, "page", frame), reg, nombre, etiqueta)\n')
SIN_LISTA_HMM = ('        if not picked and pendiente:\n'
                 '            _evidencia_sin_sugerencia(page, reg, evidencia, etiqueta)\n')
SIN_LISTA_MK = '        if pendiente:\n            _evidencia_sin_sugerencia(page, reg, nombre, etiqueta)\n'
SIN_LISTA_CMA = ('        if pendiente:\n'
                 '            _evidencia_sin_sugerencia(page, reg, evidencia, etiqueta)\n'
                 '        val = _valor()\n')
SIN_LISTA_ENTREGA = ('    if pendiente:\n'
                     '        _evidencia_sin_sugerencia(page, reg, evidencia, "el lugar de entrega")\n')
SIN_LISTA = ('    _evidencia_antes_de_la_guarda(page, reg, nombre, f"sin una sugerencia que elegir en {etiqueta}", '
             'completa=False)\n')

MUTACIONES += [
    # Cada ayudante, sin dejarla: como hasta el encargo 42.
    dict(id="sin-lista-one-no-deja", pruebas=[SUG_NADA], viejo=SIN_LISTA_ONE,
         nuevo='            raise ObjetivoNoEncontrado(f"{etiqueta} de ONE", '),
    dict(id="sin-lista-msc-no-deja", pruebas=[SUG_NADA], viejo=SIN_LISTA_MSC,
         nuevo='            raise ObjetivoNoEncontrado(f"{etiqueta} de MSC", '),
    dict(id="sin-lista-cosco-no-deja", pruebas=[SUG_NADA, SUG_REINTENTO_COSCO], viejo=SIN_LISTA_COSCO, nuevo=""),
    dict(id="sin-lista-hmm-no-deja", pruebas=[SUG_NADA], viejo=SIN_LISTA_HMM, nuevo=""),
    dict(id="sin-lista-mk-no-deja", pruebas=[SUG_NADA], viejo=SIN_LISTA_MK, nuevo=""),
    dict(id="sin-lista-cma-no-deja", pruebas=[SUG_NADA], viejo=SIN_LISTA_CMA, nuevo="        val = _valor()\n"),
    dict(id="sin-lista-entrega-no-deja", pruebas=[SUG_NADA], viejo=SIN_LISTA_ENTREGA, nuevo=""),
    # MAERSK y COSCO, al volver a escribir, con el nombre de la primera.
    dict(id="sin-lista-mk-reintento-mismo-nombre", pruebas=[SUG_NADA], viejo=SIN_LISTA_MK,
         nuevo=SIN_LISTA_MK.replace("reg, nombre, etiqueta", "reg, evidencia, etiqueta")),
    dict(id="sin-lista-cosco-reintento-mismo-nombre", pruebas=[SUG_NADA], viejo=SIN_LISTA_COSCO,
         nuevo=SIN_LISTA_COSCO.replace("reg, nombre, etiqueta", "reg, evidencia, etiqueta")),
    # El puerto de CMA, después del Tab: ya no sería lo que mostraba al terminar la espera.
    dict(id="sin-lista-cma-despues-del-tab", pruebas=[SUG_NADA], cambios=[
        (SIN_LISTA_CMA, "        val = _valor()\n"),
        ('    val = _valor() or val\n',
         '    if pendiente:\n'
         '        _evidencia_sin_sugerencia(page, reg, evidencia, etiqueta)\n'
         '    val = _valor() or val\n')]),
    # La de la página entera (dispara un «resize», que podría cerrar la lista), u otro momento en log.txt.
    dict(id="sin-lista-pagina-entera", pruebas=[SUG_NADA], viejo=SIN_LISTA,
         nuevo=SIN_LISTA.replace("completa=False", "completa=True")),
    dict(id="sin-lista-otro-momento", pruebas=[SUG_NADA], viejo=SIN_LISTA,
         nuevo=SIN_LISTA.replace("sin una sugerencia que elegir en", "con las sugerencias de")),
]

# --- Encargo 42 · commit 4: lo que encontró la revisión de código. Sin una palabra antes de la primera coma
# (_ciudad_de), o con solo el país en el puerto de carga, tampoco hay ruta; cada ayudante que no elige lo dice; en el
# modo ramp de CMA, el motivo conserva el aviso del puerto; y después del ayudante que no eligió, nada en la página
# (CICLO-maersk-y-fila-sin-ruta.md) ---
CIUDAD_DE = FSR + "test_ciudad_de"
SIN_PALABRA = "test_clics.TestSinSugerenciaNoSigue.test_sin_una_palabra_corta_el_ayudante"
CAMPO_FALLA = SUG + "test_si_el_campo_falla_no_elige"
PALABRA = '    return texto if _re_mk.search(r"[^\\W_]{2,}", texto) else ""\n'
AVISO_RAMP = '                aviso = f" (con el puerto, CMA avisó: «{ultimo_aviso}»)" if ultimo_aviso else ""\n'
EN_UN_TRY = ('                try:\n                    {}\n'
             '                except Exception:\n                    pass\n')
FIN_DEL_AYUDANTE = ('        return bool(picked)\n    except Exception as e:\n'
                    '        reg.info(f"{etiqueta}: err {str(e)[:70]}")\n        return False\n\n\n')
COSCO_FIN = FIN_DEL_AYUDANTE + "def esperar_frame"
HMM_FIN = FIN_DEL_AYUDANTE + "# Devuelve el índice"

MUTACIONES += [
    # La palabra: sin pedirla, con una letra, solo con letras ASCII, o con el guion bajo como letra.
    dict(id="ciudad-sin-pedir-una-palabra", pruebas=[CIUDAD_DE, FSR + "test_falta_en_la_fila", VACIO, SIN_PALABRA],
         viejo=PALABRA, nuevo="    return texto\n"),
    dict(id="ciudad-una-letra-basta", pruebas=[CIUDAD_DE, FSR + "test_falta_en_la_fila", VACIO],
         viejo=PALABRA, nuevo=PALABRA.replace("{2,}", "{1,}")),
    dict(id="ciudad-palabra-solo-ascii", pruebas=[CIUDAD_DE], viejo=PALABRA,
         nuevo=PALABRA.replace("[^\\W_]", "[A-Za-z0-9]")),
    dict(id="ciudad-guion-bajo-es-letra", pruebas=[CIUDAD_DE], viejo=PALABRA, nuevo=PALABRA.replace("[^\\W_]", "\\w")),
    # El puerto de carga con solo el país: «CHILE» pasaría.
    dict(id="ruta-puerto-solo-el-pais-pasa", pruebas=[FSR + "test_falta_en_la_fila"], viejo=REGLA_PUERTO,
         nuevo=REGLA_PUERTO.replace("_puerto_de_carga(pol)", "_ciudad_de(pol)")),
] + [
    # Cada tope, con la parte antes de la coma y sin pedir la palabra: escribiría «-» o «X».
    dict(id=f"vacio-{nombre}-sin-pedir-una-palabra", pruebas=[VACIO] + extra, viejo=mira + corte,
         nuevo=sin_palabra + corte)
    for nombre, mira, sin_palabra, corte, extra in (
        ("one", "    if not _ciudad_de(keyword):\n", '    if not keyword.split(",")[0].strip():\n',
         '        raise ObjetivoNoEncontrado(f"{etiqueta} de ONE"', []),
        ("msc", "    if not _ciudad_de(ciudad):\n", '    if not ciudad.split(",")[0].strip():\n',
         '        raise ObjetivoNoEncontrado(f"{etiqueta} de MSC"', []),
        ("hmm", "    if not _ciudad_de(texto):\n", '    if not texto.split(",")[0].strip():\n',
         '        raise ObjetivoNoEncontrado(f"{etiqueta} de HYUNDAI"', []),
        ("mk", "    ciudad = _ciudad_de(texto)\n    if not ciudad:\n",
         '    ciudad = texto.split(",")[0].strip()\n    if not ciudad:\n',
         '        raise ObjetivoNoEncontrado(f"{etiqueta} de MAERSK"', []),
        ("cma-puerto", "    ciudad = _ciudad_de(texto)\n    if not ciudad:\n",
         '    ciudad = texto.split(",")[0].strip()\n    if not ciudad:\n',
         '        raise ObjetivoNoEncontrado(f"{etiqueta} de CMA"', [SIN_PALABRA]),
        ("cma-entrega", "    ciudad = _ciudad_de(texto)\n    if not ciudad:\n",
         '    ciudad = texto.split(",")[0].strip()\n    if not ciudad:\n',
         '        raise ObjetivoNoEncontrado("Lugar de entrega de CMA"', []),
    )
] + [
    # COSCO, en quien llama a su ayudante (que sirve también al contrato y corta solo con el texto vacío).
    dict(id="cosco-origen-sin-pedir-una-palabra", pruebas=[SIN_PALABRA],
         viejo="    puerto = _puerto_de_carga(celda)\n",
         nuevo="    puerto = _cosco_puerto_de_la_celda(celda)\n"),
    dict(id="cosco-destino-sin-pedir-una-palabra", pruebas=[SIN_PALABRA],
         viejo='    dest_ciudad = _ciudad_de(reserva.get("destino_final") or reserva.get("destino_orig"))\n',
         nuevo='    dest_ciudad = (reserva.get("destino_final") or reserva.get("destino_orig") or "")'
               '.split(",")[0].strip()\n'),
    # Lo que devuelve el ayudante que no vio ninguna sugerencia: diría que eligió.
    dict(id="no-eligio-cosco-sin-lista-dice-que-si", pruebas=[SUG_NADA], viejo=COSCO_FIN,
         nuevo=COSCO_FIN.replace("        return bool(picked)\n", "        return True\n")),
    dict(id="no-eligio-hmm-sin-lista-dice-que-si", pruebas=[SUG_NADA], viejo=HMM_FIN,
         nuevo=HMM_FIN.replace("        return bool(picked)\n", "        return True\n")),
    dict(id="no-eligio-mk-sin-sugerencia-dice-que-si", pruebas=[SUG_NADA, RUTA_MK, SUG_EXACTA],
         viejo='        raise ObjetivoNoEncontrado(f"{etiqueta} de MAERSK", por_que)\n',
         nuevo='        return ("X", "X")\n'),
    dict(id="no-eligio-entrega-sin-sugerencia-dice-que-si", pruebas=[SUG_NADA],
         viejo='    reg.info("lugar de entrega: sin sugerencia")\n    return ""\n',
         nuevo='    reg.info("lugar de entrega: sin sugerencia")\n    return "X"\n'),
    # Y el que no pudo usar el campo.
    dict(id="no-eligio-one-campo-falla-dice-que-si", pruebas=[CAMPO_FALLA],
         viejo='        reg.info(f"{etiqueta}: error {str(e)[:80]}")\n        return False\n\n\ndef _fill_port',
         nuevo='        reg.info(f"{etiqueta}: error {str(e)[:80]}")\n        return True\n\n\ndef _fill_port'),
    dict(id="no-eligio-msc-campo-falla-dice-que-si", pruebas=[CAMPO_FALLA],
         viejo='        reg.info(f"{etiqueta}: {str(e)[:70]}")\n        return False\n',
         nuevo='        reg.info(f"{etiqueta}: {str(e)[:70]}")\n        return True\n'),
    dict(id="no-eligio-cosco-campo-no-esta-dice-que-si", pruebas=[CAMPO_FALLA],
         viejo='                reg.info(f"{etiqueta}: {r}"); return False\n',
         nuevo='                reg.info(f"{etiqueta}: {r}"); return True\n'),
    dict(id="no-eligio-cosco-campo-falla-dice-que-si", pruebas=[CAMPO_FALLA], viejo=COSCO_FIN,
         nuevo=COSCO_FIN.replace("        return False\n", "        return True\n")),
    dict(id="no-eligio-hmm-campo-falla-dice-que-si", pruebas=[CAMPO_FALLA], viejo=HMM_FIN,
         nuevo=HMM_FIN.replace("        return False\n", "        return True\n")),
    dict(id="no-eligio-mk-campo-falla-dice-que-si", pruebas=[CAMPO_FALLA, RUTA_MK],
         viejo='        raise ObjetivoNoEncontrado(f"{etiqueta} de MAERSK", f"el campo donde escribir «{ciudad}»")\n',
         nuevo='        return ("X", "X")\n'),
    dict(id="no-eligio-entrega-campo-falla-dice-que-si", pruebas=[CAMPO_FALLA],
         viejo='        reg.info(f"entrega: err campo ({str(e)[:40]})"); return ""\n',
         nuevo='        reg.info(f"entrega: err campo ({str(e)[:40]})"); return "X"\n'),
    dict(id="no-eligio-entrega-sin-abrir-dice-que-si", pruebas=[CAMPO_FALLA],
         viejo='            reg.info(f"entrega: no pude abrir el campo ({str(e)[:40]})"); return ""\n',
         nuevo='            reg.info(f"entrega: no pude abrir el campo ({str(e)[:40]})"); return "X"\n'),
    # CMA en el modo ramp: sin el aviso del puerto, o siguiendo a la cotización antes de cortar (así pasaba sin que la
    # prueba lo viera, hasta que la página falsa anotó sus acciones).
    dict(id="cma-ramp-sin-el-aviso-del-puerto", pruebas=[TSN], viejo=AVISO_RAMP, nuevo='                aviso = ""\n'),
    dict(id="sin-sugerencia-cma-ramp-sigue-a-la-cotizacion", pruebas=[TSN], viejo=AVISO_RAMP,
         nuevo="                _cotizacion()\n" + AVISO_RAMP),
]

# --- Encargo 42 · commit 5: lo que encontró la revisión del informe. La palabra del puerto de carga se pide al puerto
# sin el país (con «X CHILE», la del commit 4 era «CHILE», y COSCO buscaba «X»), y la página falsa de
# TestSinSugerenciaNoSigue anota también el JavaScript y los get_by_* (CICLO-maersk-y-fila-sin-ruta.md) ---
MUTACIONES += [
    # La palabra, pedida antes de quitar el país, como en el commit 4.
    dict(id="ruta-puerto-palabra-antes-del-pais", pruebas=[FSR + "test_falta_en_la_fila"], viejo=REGLA_PUERTO,
         nuevo=REGLA_PUERTO.replace("_puerto_de_carga(pol)",
                                    "_ciudad_de(pol) or not _cosco_puerto_de_la_celda(pol)")),
    dict(id="cosco-origen-palabra-antes-del-pais", pruebas=[SIN_PALABRA],
         viejo="    puerto = _puerto_de_carga(celda)\n",
         nuevo="    puerto = _cosco_puerto_de_la_celda(_ciudad_de(celda))\n"),
    # CMA en el modo ramp, siguiendo antes de cortar con un JavaScript o con un localizador por su texto.
    dict(id="sin-sugerencia-cma-ramp-sigue-con-javascript", pruebas=[TSN], viejo=AVISO_RAMP,
         nuevo='                page.evaluate("window.scrollTo(0, 0)")\n' + AVISO_RAMP),
    # (Desde el commit 6, en un try, como el código real: sin él caía también con la página de antes, que no tenía
    # get_by_text, por el AttributeError.)
    dict(id="sin-sugerencia-cma-ramp-sigue-por-su-texto", pruebas=[TSN], viejo=AVISO_RAMP,
         nuevo=EN_UN_TRY.format('page.get_by_text("Validar ruta").click()') + AVISO_RAMP),
]

# --- Encargo 42 · commit 6: lo que encontró la revisión final. La palabra del puerto de carga se mide en la celda y en
# el puerto sin «CHILE» en ninguna posición (_puerto_de_carga: «CHILE X» y «№» pasaban), y la página falsa de
# TestSinSugerenciaNoSigue anota también el teclado, el mouse, las acciones de la página y el marco de COSCO
# (CICLO-maersk-y-fila-sin-ruta.md) ---
COSCO_PUERTO = "test_clics.TestCosco.test_puerto_de_carga_sin_sugerencia_corta"
SIN_PAIS = '    sin_pais = " ".join(p for p in puerto.split() if p not in PAIS_DEL_PUERTO)\n'
PUERTO_SI = '    return puerto if _ciudad_de(celda) and _ciudad_de(sin_pais) else ""\n'
CORTE_DESTINO_COSCO = ('        raise ObjetivoNoEncontrado("Destination de COSCO", '
                       '_sugerencia_que_elegir(dest_ciudad))\n')

MUTACIONES += [
    # El puerto: «CHILE» solo al final, como hasta el commit 5 («CHILE X» pasaría); sin mirar la celda («№» daría la
    # palabra «NO»); o la celda sin normalizar, que COSCO escribiría con su coma y su país.
    dict(id="puerto-chile-solo-al-final", pruebas=[FSR + "test_falta_en_la_fila", SIN_PALABRA], viejo=SIN_PAIS,
         nuevo="    sin_pais = puerto\n"),
    dict(id="puerto-sin-mirar-la-celda", pruebas=[FSR + "test_falta_en_la_fila"], viejo=PUERTO_SI,
         nuevo=PUERTO_SI.replace("_ciudad_de(celda) and ", "")),
    dict(id="puerto-de-carga-sin-normalizar", pruebas=[COSCO_PUERTO], viejo=PUERTO_SI,
         nuevo=PUERTO_SI.replace("return puerto if", "return celda if")),
] + [
    # CMA en el modo ramp, siguiendo antes de cortar con el teclado, el mouse o una acción de la página, en un try como
    # el código real: con la página de antes, todas pasaban (las midió la revisión final).
    dict(id=f"sin-sugerencia-cma-ramp-sigue-{via}", pruebas=[TSN], viejo=AVISO_RAMP,
         nuevo=EN_UN_TRY.format(accion) + AVISO_RAMP)
    for via, accion in (("con-el-teclado", 'page.keyboard.type("x")'), ("con-el-mouse", "page.mouse.click(0, 0)"),
                        ("con-select-option", 'page.select_option("select", "x")'))
] + [
    # COSCO, siguiendo en su marco antes de cortar el destino.
    dict(id="sin-sugerencia-cosco-destino-sigue-en-el-marco", pruebas=[TSN], viejo=CORTE_DESTINO_COSCO,
         nuevo='        frame.evaluate("document.body.click()")\n' + CORTE_DESTINO_COSCO),
]

# --- Encargo 43 · commit 1: MAERSK elige el origen y el destino con la regla de Marcelo, la única sugerencia Container
# Yard cuya parte antes de la primera coma, sin lo que va entre paréntesis, es lo escrito (sin distinguir mayúsculas ni
# tildes); comprueba que el campo quedó con su texto entero y, si no, corta él mismo (CICLO-maersk-elige-exacto.md).
# Hasta ahí, la primera Container Yard o, si no había, la primera, y bastaba que el campo trajera lo tecleado. Las de
# los cortes de reservar_maersk (sin-sugerencia-maersk-*) se fueron con ellos; mk-ruta-sin-el-campo quedó equivalente.
# ---
FORMA_MK = "test_ayudantes.TestMAERSK.test_la_forma_de_la_regla_de_origen_y_destino"
CY_MK = "    cy = cand.filter(has_text=_re_mk.compile(_re_mk.escape(MK_CONTAINER_YARD), _re_mk.I))\n"
EXACTAS_MK = "    return cy, textos, [i for i, t in enumerate(textos) if _mk_base(t) == escrita]\n"
PLANO_MK = '    return " ".join("".join(c for c in t if not unicodedata.combining(c)).upper().split())\n'
DEJO_MK = ("                        if not vista:\n                            por_que = falta\n"
           "                            break\n")

MUTACIONES += [
    # Sin mirar el tipo de lugar; con la primera Container Yard, como hasta el encargo 43; o con la primera de varias.
    dict(id="mk-exacta-sin-container-yard", pruebas=[SUG_EXACTA], viejo=CY_MK, nuevo="    cy = cand\n"),
    dict(id="mk-exacta-la-primera-container-yard", pruebas=[SUG_EXACTA], viejo=EXACTAS_MK,
         nuevo="    return cy, textos, list(range(len(textos)))[:1]\n"),
    dict(id="mk-exacta-la-primera-de-varias", pruebas=[SUG_EXACTA],
         viejo="        if len(exactas) == 1:\n", nuevo="        if exactas:\n"),
    # La forma: con lo que va entre paréntesis, sin cortar en la primera coma, con tildes, con mayúsculas o con los
    # espacios como vienen.
    dict(id="mk-base-con-parentesis", pruebas=[FORMA_MK, SUG_EXACTA],
         viejo='        sin = _re_mk.sub(r"\\([^()]*\\)", " ", t)\n', nuevo="        sin = t\n"),
    dict(id="mk-base-sin-cortar-en-la-coma", pruebas=[FORMA_MK, SUG_EXACTA],
         viejo='    t = str(sugerencia or "").split(",")[0]\n', nuevo='    t = str(sugerencia or "")\n'),
    dict(id="mk-plano-con-tildes", pruebas=[FORMA_MK, SUG_EXACTA], viejo=PLANO_MK,
         nuevo='    return " ".join(t.upper().split())\n'),
    dict(id="mk-plano-con-mayusculas", pruebas=[FORMA_MK], viejo=PLANO_MK,
         nuevo='    return " ".join("".join(c for c in t if not unicodedata.combining(c)).split())\n'),
    dict(id="mk-plano-con-los-espacios", pruebas=[FORMA_MK], viejo=PLANO_MK,
         nuevo='    return "".join(c for c in t if not unicodedata.combining(c)).upper()\n'),
    # Elige aunque al dejar la evidencia no hubiera una sola (la lista cambió mientras la guardaba); sin anotar cuántas
    # calzan; o el motivo sin cuántas había.
    dict(id="mk-elige-de-una-lista-que-no-dejo", pruebas=[SUG_EXACTA], viejo=DEJO_MK, nuevo=""),
    dict(id="mk-exacta-no-lo-anota", pruebas=[SUG_EXACTA],
         viejo='        reg.info(f"{etiqueta}: {len(exactas)} de las',
         nuevo='        (lambda *a: None)(f"{etiqueta}: {len(exactas)} de las'),
    dict(id="mk-sin-una-exacta-sin-cuantas", pruebas=[SUG_EXACTA],
         viejo="{f'hay {n}' if n else 'no hay ninguna'}", nuevo="{n}"),
    # El campo: basta lo tecleado, como hasta el encargo 43; o el motivo de cada corte, otro.
    dict(id="mk-campo-con-lo-tecleado", pruebas=[RUTA_MK],
         viejo="                        calza = _mk_plano(quedo) == _mk_plano(txt)\n",
         nuevo="                        calza = ciudad[:4] in quedo\n"),
    dict(id="mk-campo-otro-motivo", pruebas=[RUTA_MK],
         viejo='por_que = f"la sugerencia «{txt}» en el campo, que quedó " + ',
         nuevo='por_que = f"la sugerencia «{txt}», que quedó " + '),
    dict(id="mk-sin-lista-otro-motivo", pruebas=[RUTA_MK],
         viejo='    por_que = f"una sugerencia para «{ciudad}»"         # si la lista no aparece\n',
         nuevo='    por_que = f"una sugerencia que elegir para «{ciudad}»"\n'),
    dict(id="mk-campo-falla-otro-motivo", pruebas=[RUTA_MK],
         viejo='f"el campo donde escribir «{ciudad}»")\n', nuevo='f"una sugerencia para «{ciudad}»")\n'),
]

# --- Encargo 43 · commit 2: las tarjetas de «Select sailing» de MAERSK con el HTML entero idéntico cuentan como una
# sola salida (su «igual», de _JS_MK_SALIDAS con 'iguales'; _mk_sin_repetidas), y se pulsa el «Book» de la primera; si
# difieren en cualquier cosa, el empate sigue. El HTML entero lo arman la evidencia y la lectura con lo mismo
# (_JS_HTML_ENTERO; CICLO-maersk-elige-exacto.md) ---
IGUAL_JS = MK + "test_js_salidas_dice_la_primera_con_su_mismo_html"
IGUAL_MK = MK + "test_las_tarjetas_identicas_cuentan_como_una_sola"
ENTERO_MK = "        try { return abreDe(c) + c.getHTML({shadowRoots: raicesDe(c)}); } catch (x) { return ''; }\n"

MUTACIONES += [
    # La lectura: sin las raíces shadow, sin la etiqueta con sus atributos, sin la raíz propia de la tarjeta, con las
    # que no se leen como iguales entre sí, sin buscar la primera igual, o con «igual» aunque no se pida.
    dict(id="mk-iguales-sin-raices-shadow", pruebas=[IGUAL_JS], viejo=ENTERO_MK,
         nuevo="        try { return abreDe(c) + c.getHTML(); } catch (x) { return ''; }\n"),
    dict(id="mk-iguales-sin-la-etiqueta", pruebas=[IGUAL_JS], viejo=ENTERO_MK,
         nuevo="        try { return c.getHTML({shadowRoots: raicesDe(c)}); } catch (x) { return ''; }\n"),
    dict(id="html-entero-sin-la-raiz-propia", pruebas=[IGUAL_JS],
         viejo="        if (desde.shadowRoot) { raices.push(desde.shadowRoot); "
               "visitar(desde.shadowRoot); }\n", nuevo=""),
    dict(id="mk-iguales-sin-leer-juntas", pruebas=[IGUAL_JS],
         viejo="{igual: enteros[i] ? enteros.indexOf(enteros[i]) : i}", nuevo="{igual: enteros.indexOf(enteros[i])}"),
    dict(id="mk-iguales-cada-una-la-suya", pruebas=[IGUAL_JS],
         viejo="{igual: enteros[i] ? enteros.indexOf(enteros[i]) : i}", nuevo="{igual: i}"),
    dict(id="mk-iguales-sin-pedirlo", pruebas=[IGUAL_JS],
         viejo="    }).map((s, i) => (args.iguales ? Object.assign(",
         nuevo="    }).map((s, i) => (true ? Object.assign("),
    # La elección: sin pedir «igual», sin descartar las copias, o sin anotarlo.
    dict(id="mk-elegir-sin-iguales", pruebas=[IGUAL_MK],
         viejo="        salidas = _mk_leer_salidas(page, toks, viaje_solicitado, reg, iguales=True)\n",
         nuevo="        salidas = _mk_leer_salidas(page, toks, viaje_solicitado, reg)\n"),
    dict(id="mk-leer-sin-iguales", pruebas=[IGUAL_MK],
         viejo='            args["iguales"] = True\n', nuevo="            pass\n"),
    dict(id="mk-sin-repetidas-no-descarta", pruebas=[IGUAL_MK],
         viejo='    unicas = [s for s in salidas if s.get("igual", s.get("i")) == s.get("i")]\n',
         nuevo="    unicas = list(salidas)\n"),
    dict(id="mk-sin-repetidas-sin-igual-descarta", pruebas=[IGUAL_MK],
         viejo='    unicas = [s for s in salidas if s.get("igual", s.get("i")) == s.get("i")]\n',
         nuevo='    unicas = [s for s in salidas if s.get("igual", -1) == s.get("i")]\n'),
    dict(id="mk-sin-repetidas-sin-anotar", pruebas=[IGUAL_MK],
         viejo='            reg.info(f"{len(de_la_nave) + repetidas} tarjetas de la nave; {copias} de otra',
         nuevo='            (lambda *a: None)(f"{len(de_la_nave) + repetidas} tarjetas de la nave; {copias} de otra'),
]

# --- Encargo 43 · commit 3: el panel marca la fila con nave y sin puerto de carga o sin destino antes de correr y la
# cuenta aparte, como la fila sin nave (_con_su_marca, JS_INDEX y CSS_INDEX; CICLO-maersk-elige-exacto.md) ---
RUTA_API = "test_web.TestPanelCorridas.test_filas_dicen_si_traen_la_ruta"
RUTA_PANEL = "test_envio.TestLecturaDelPanel.test_marca_y_cuenta_aparte_las_filas_sin_ruta"
MARCAS = "                sin_puerto=falta == FILA_SIN_PUERTO, sin_destino=falta == FILA_SIN_DESTINO)\n"

MUTACIONES += [
    # /api/filas: sin una de las dos marcas, o con las marcas también en la fila sin nave.
    dict(id="panel-sin-marca-de-puerto", pruebas=[RUTA_API], viejo=MARCAS,
         nuevo="                sin_puerto=False, sin_destino=falta == FILA_SIN_DESTINO)\n"),
    dict(id="panel-sin-marca-de-destino", pruebas=[RUTA_API], viejo=MARCAS,
         nuevo="                sin_puerto=falta == FILA_SIN_PUERTO, sin_destino=False)\n"),
    dict(id="panel-ruta-tambien-sin-nave", pruebas=[RUTA_API],
         viejo='    falta = "" if _fila_sin_nave(nave) else _falta_en_la_fila(fila)\n',
         nuevo="    falta = _falta_en_la_fila(fila)\n"),
    # El panel: sin la marca en la tabla, sin el aviso, sin marcarla para correr, o sin su estilo.
    dict(id="panel-sin-marca-de-puerto-en-la-tabla", pruebas=[RUTA_PANEL],
         viejo="<span class='sin-ruta'>sin puerto de carga</span> ", nuevo=""),
    dict(id="panel-sin-marca-de-destino-en-la-tabla", pruebas=[RUTA_PANEL],
         viejo="<span class='sin-ruta'>sin destino</span> ", nuevo=""),
    dict(id="panel-sin-aviso-de-ruta", pruebas=[RUTA_PANEL],
         viejo="  const sinRuta = FILAS.filter(f => f.sin_puerto || f.sin_destino).length;\n",
         nuevo="  const sinRuta = 0;\n"),
    dict(id="panel-sin-ruta-sin-marcar", pruebas=[RUTA_PANEL],
         viejo="function marcadaPorDefecto(f) {\n  return !f.manual;\n}\n",
         nuevo="function marcadaPorDefecto(f) {\n  return !f.manual && !f.sin_puerto && !f.sin_destino;\n}\n"),
    dict(id="panel-sin-estilo-de-ruta", pruebas=[RUTA_PANEL],
         viejo=".sin-nave, .sin-ruta { color: var(--text-muted); font-style: italic; }\n",
         nuevo=".sin-nave { color: var(--text-muted); font-style: italic; }\n"),
]

# --- Encargo 43 · commit 4: «CL» solo en el puerto de carga cuenta como solo el país, igual que «CHILE»
# (PAIS_DEL_PUERTO; CICLO-maersk-elige-exacto.md) ---
MUTACIONES += [
    dict(id="puerto-cl-pasa", pruebas=[FSR + "test_falta_en_la_fila"], viejo=SIN_PAIS,
         nuevo="    sin_pais = \" \".join(p for p in puerto.split() if p != \"CHILE\")\n"),
]

# --- Encargo 43 · commit 5: «-» en el destino final se trata igual que esa celda vacía, en los dos lectores
# (_destino_final_de; CICLO-maersk-elige-exacto.md) ---
GUION = "test_planilla.TestDestinoFinalConGuion.test_un_guion_en_el_destino_final_es_la_celda_vacia"
DESTINO_FINAL_DE = '    return "" if str(celda or "").strip() == "-" else celda\n'

MUTACIONES += [
    # «-» sigue siendo el destino; sin los espacios de los extremos; o también otro texto, como «--».
    dict(id="guion-es-destino", pruebas=[GUION], viejo=DESTINO_FINAL_DE, nuevo="    return celda\n"),
    dict(id="guion-sin-espacios", pruebas=[GUION], viejo=DESTINO_FINAL_DE,
         nuevo='    return "" if str(celda or "") == "-" else celda\n'),
    dict(id="guion-tambien-dos", pruebas=[GUION], viejo=DESTINO_FINAL_DE,
         nuevo='    return "" if not str(celda or "").strip(" -") else celda\n'),
    # Un lector sin la regla.
    dict(id="guion-consola-sin-regla", pruebas=[GUION],
         viejo="        dest_final = _destino_final_de(dest_final)", nuevo="        pass"),
    dict(id="guion-web-sin-regla", pruebas=[GUION],
         viejo='            "destino_final": _destino_final_de(val("destino_final")) or val("destino_orig"),\n',
         nuevo='            "destino_final": val("destino_final") or val("destino_orig"),\n'),
]

# --- Encargo 43 · commit 6: lo que encontró la revisión de código en _mk_ciudad: decide con la lista quieta, compara
# el campo como la regla y lo lee hasta MK_LECTURAS_CAMPO veces, y toma el prefijo con los espacios de a uno
# (CICLO-maersk-elige-exacto.md) ---
SUG_QUIETA = SUG + "test_maersk_decide_con_la_lista_quieta"
SUG_CAMPO = SUG + "test_maersk_lee_el_campo_como_la_regla"
SUG_ESPACIOS = SUG + "test_maersk_escribe_y_compara_con_los_espacios_de_a_uno"
# Desde el encargo 46, el prefijo sale de _mk_plano: sin tildes y con los espacios de a uno.
PREFIJO_MK = "    plano = _mk_plano(ciudad)\n"
CALZA_MK = "                        calza = _mk_plano(quedo) == _mk_plano(txt)\n"

MUTACIONES += [
    # Decide con la primera lectura, como hasta la revisión.
    dict(id="mk-decide-con-la-primera-lectura", pruebas=[SUG_QUIETA],
         viejo="                    if lectura != anterior and vuelta < 13:\n",
         nuevo="                    if False:\n"),
    # El campo: una sola lectura, o exacto en vez de como la regla; o basta lo tecleado, como hasta el encargo 43.
    dict(id="mk-campo-una-lectura", pruebas=[SUG_CAMPO],
         viejo="                    for lectura_campo in range(MK_LECTURAS_CAMPO):\n",
         nuevo="                    for lectura_campo in range(1):\n"),
    dict(id="mk-campo-exacto", pruebas=[SUG_CAMPO], viejo=CALZA_MK,
         nuevo="                        calza = quedo == txt\n"),
    # El prefijo con los espacios como vienen.
    dict(id="mk-prefijo-con-los-espacios", pruebas=[SUG_ESPACIOS], viejo=PREFIJO_MK,
         nuevo='    plano = "".join(_mk_plano(ch) or ch for ch in str(ciudad or ""))\n'),
    # Lo que quedó en el campo, devuelto como la sugerencia: desde que el campo se compara como la regla pueden
    # diferir, y esta mutación, que el commit 1 quitó por equivalente, vuelve a morder.
    dict(id="mk-ruta-sin-el-campo", pruebas=[SUG_CAMPO],
         viejo="    return (picked, quedo)\n", nuevo="    return (picked, picked)\n"),
]

# --- Encargo 44: el logo quedó fuera del repo, y la sonda no deja entrar ninguna imagen ---
MUTACIONES += [
    dict(id="sonda-vuelve-el-logo", archivo=SONDA, pruebas=["test_sonda.TestSondaImagenes.test_ninguna_imagen_entra"],
         viejo="IMAGENES_PERMITIDAS = set()", nuevo='IMAGENES_PERMITIDAS = {"logo_aquachile_dark.png"}'),
]

# --- Encargo 44: los contratos por defecto salen del programa a config.json (CICLO-publicar-el-repo.md) ---
CD = AY + "TestContratosPorDefecto."
CD_AVISO = CD + "test_sin_la_llave_o_sin_texto_queda_vacio_y_avisa_una_vez"
CD_NO_LOS_TRAE = CD + "test_el_programa_ya_no_los_trae"
CD_HMM = CD + "test_hyundai_sin_contrato_no_elige_a_ciegas"
CD_PLANTILLA = CD + "test_la_plantilla_trae_las_llaves_vacias"
CD_ONE = AY + "TestONE.test_contrato_one"
# La línea que sigue al «return» en _contrato_por_defecto, para que sus mutaciones anclen solo ahí.
LECTOR_CONTRATO = '    que = (f"config.json no trae «{clave}»'

MUTACIONES += [
    dict(id="contrato-defecto-sin-strip", pruebas=[CD + "test_salen_de_config"],
         viejo="    if isinstance(valor, str):\n        return valor.strip()\n" + LECTOR_CONTRATO,
         nuevo="    if isinstance(valor, str):\n        return valor\n" + LECTOR_CONTRATO),
    dict(id="contrato-defecto-otra-llave", pruebas=[CD + "test_salen_de_config"],
         viejo='.get("contratos_por_defecto", {}).get(clave, _FALTA)',
         nuevo='.get("contratos", {}).get(clave, _FALTA)'),
    dict(id="contrato-defecto-sin-aviso", pruebas=[CD_AVISO],
         viejo='    _avisar_en_pantalla_y_log(f"⚠ {que}: sigo sin contrato por defecto. Si quieres uno, escríbelo '
               'ahí.",\n                              una_vez="contrato_" + clave)\n', nuevo=''),
    dict(id="contrato-defecto-avisa-siempre", pruebas=[CD_AVISO],
         viejo='una_vez="contrato_" + clave)', nuevo='una_vez=None)'),
    dict(id="contrato-defecto-cualquier-cosa", pruebas=[CD_AVISO],
         viejo="    if isinstance(valor, str):\n        return valor.strip()\n" + LECTOR_CONTRATO,
         nuevo="    if valor is not _FALTA:\n        return str(valor).strip()\n" + LECTOR_CONTRATO),
    dict(id="contrato-defecto-avisa-el-vacio", pruebas=[CD_AVISO],
         viejo="    if isinstance(valor, str):\n        return valor.strip()\n" + LECTOR_CONTRATO,
         nuevo="    if isinstance(valor, str) and valor.strip():\n        return valor.strip()\n" + LECTOR_CONTRATO),
    dict(id="contrato-one-usa-fijo", pruebas=[CD_ONE, CD_NO_LOS_TRAE],
         viejo='or _contrato_por_defecto("one_usa")', nuevo='or "XX12345678"'),
    dict(id="contrato-one-otros-fijo", pruebas=[CD_ONE, CD_NO_LOS_TRAE],
         viejo='or _contrato_por_defecto("one_otros")', nuevo='or "XX12345679"'),
    dict(id="contrato-msc-fijo", pruebas=[CD_NO_LOS_TRAE],
         viejo='or _contrato_por_defecto("msc"))', nuevo='or "XX12345680")'),
    dict(id="contrato-hyundai-fijo", pruebas=[CD_NO_LOS_TRAE],
         viejo='    ctto = creds.get("contrato", "") or _contrato_por_defecto("hyundai")\n    if not ctto:\n',
         nuevo='    ctto = creds.get("contrato", "") or "XX12345681"\n    if not ctto:\n'),
    dict(id="contrato-comentario-con-codigo", pruebas=[CD_NO_LOS_TRAE],
         viejo="    # Contrato inteligente: USA u Otros Mercados (_determinar_contrato_one).\n",
         nuevo="    # Contrato inteligente (USA = XX12345682, Otros Mercados = XX12345683)\n"),
    dict(id="hyundai-paso2-sin-guarda", pruebas=[CD_HMM],
         viejo='    ctto = creds.get("contrato", "") or _contrato_por_defecto("hyundai")\n    if ctto:\n',
         nuevo='    ctto = creds.get("contrato", "") or _contrato_por_defecto("hyundai")\n    if True:\n'),
    dict(id="hyundai-detalles-sin-corte", pruebas=[CD_HMM],
         viejo='    if not ctto:\n        raise ObjetivoNoEncontrado("Contract No de HYUNDAI"',
         nuevo='    if False:\n        raise ObjetivoNoEncontrado("Contract No de HYUNDAI"'),
    dict(id="plantilla-sin-un-contrato", archivo="config.example.json", pruebas=[CD_PLANTILLA],
         viejo='      "msc": "",\n', nuevo=''),
    dict(id="plantilla-con-un-contrato", archivo="config.example.json", pruebas=[CD_PLANTILLA],
         viejo='      "hyundai": ""\n', nuevo='      "hyundai": "XX1"\n'),
]

# --- Encargo 44, revisión de código: el código de Shipper de HYUNDAI a config.json, y la sonda con los datos de la
# cuenta y los generadores ---
SC = "test_sonda.TestSondaCuenta."
CD_SHIPPER = CD + "test_el_codigo_shipper_de_hyundai_sale_de_config"
CD_SHIPPER_AVISO = CD + "test_sin_el_codigo_shipper_queda_vacio_y_avisa_una_vez"

MUTACIONES += [
    dict(id="shipper-hyundai-fijo", pruebas=[CD_NO_LOS_TRAE],
         viejo='([codigo_shipper] if codigo_shipper else [])', nuevo='["SHIP9999"]'),
    dict(id="shipper-hyundai-sin-lector", pruebas=[CD_NO_LOS_TRAE],
         viejo="        codigo_shipper = _codigo_shipper_hyundai()", nuevo='        codigo_shipper = ""'),
    dict(id="shipper-defecto-sin-strip", pruebas=[CD_SHIPPER],
         viejo='    if isinstance(valor, str):\n        return valor.strip()\n'
               '    que = ("config.json no trae «codigo_shipper',
         nuevo='    if isinstance(valor, str):\n        return valor\n    que = ("config.json no trae «codigo_shipper'),
    dict(id="shipper-defecto-sin-aviso", pruebas=[CD_SHIPPER_AVISO],
         viejo='una_vez="codigo_shipper_hyundai")', nuevo='una_vez=None)'),
    dict(id="plantilla-sin-codigo-shipper", archivo="config.example.json", pruebas=[CD_PLANTILLA],
         viejo='    "codigo_shipper_hyundai": ""\n', nuevo='    "codigo_shipper_hyundai": "XX99"\n'),
    dict(id="sonda-cuenta-sin-contratos", archivo=SONDA,
         pruebas=[SC + "test_los_datos_de_la_cuenta_salen_de_config", SP + "test_bloquea_un_contrato_sin_mostrarlo"],
         viejo='                    if tipo.startswith("contrato"):\n',
         nuevo='                    if tipo == "nada":\n'),
    dict(id="sonda-cuenta-sin-opciones", archivo=SONDA, pruebas=[SC + "test_los_datos_de_la_cuenta_salen_de_config"],
         viejo='    agregar("opciones", "codigo_shipper_hyundai", opciones.get("codigo_shipper_hyundai"))\n', nuevo=''),
    dict(id="sonda-cuenta-solo-informa", archivo=SONDA,
         pruebas=[SC + "test_la_cuenta_bloquea_salvo_en_el_almacen", SP + "test_bloquea_un_contrato_sin_mostrarlo"],
         viejo='((nombres or cuenta) and modo != "--almacen")', nuevo='(nombres and modo != "--almacen")'),
    dict(id="sonda-cuenta-bloquea-en-el-almacen", archivo=SONDA,
         pruebas=[SC + "test_la_cuenta_bloquea_salvo_en_el_almacen"],
         viejo='((nombres or cuenta) and modo != "--almacen")', nuevo='(cuenta or (nombres and modo != "--almacen"))'),
    dict(id="sonda-generadores-entran", archivo=SONDA, pruebas=[SC + "test_los_generadores_no_entran"],
         viejo='"*.tmp", "crear_*.py", "generar_manuales.py"]', nuevo='"*.tmp"]'),
]

# --- Encargo 46: MAERSK trae la tarjeta de la salida elegida a la vista antes de mirar la altura de su «Book», y si
# aun así no lo pulsa, NO ENVIADA con su propio motivo; el prefijo de su lista, sin tildes
# (CICLO-maersk-pulsa-el-book.md) ---
BOOK_MK = MK + "test_trae_la_tarjeta_a_la_vista_antes_de_mirar_el_book"
BOOK_VUELVE = MK + "test_el_book_que_no_pudo_pulsar_vuelve_con_la_salida_y_el_porque"
BOOK_NO_ENVIADA = MK + "test_el_book_sin_pulsar_queda_no_enviada_con_evidencia"
BOOK_RAMA = MK + "test_el_book_sin_pulsar_no_sigue_por_la_nave_que_no_esta"
SUG_TILDES = SUG + "test_maersk_reconoce_la_lista_con_una_tilde_en_las_primeras_letras"
TRAE_TARJETA = ("    try:\n        tarjeta.scroll_into_view_if_needed(timeout=3000)\n    except Exception as e:\n"
                "        return f\"no pude traer su tarjeta a la vista ({_texto_error(e)})\"\n")
CLIC_BOOK = ("                try:\n                    btn.scroll_into_view_if_needed(timeout=3000)\n"
             "                    btn.click(timeout=4000)\n                except Exception as e:\n"
             "                    return f\"el clic en el «Book» falló ({_texto_error(e)})\"\n")

MUTACIONES += [
    # Mira la altura sin traer la tarjeta, como hasta ahí; o la trae sin atrapar su falla.
    dict(id="mk-book-sin-traer-la-tarjeta", pruebas=[BOOK_MK], viejo=TRAE_TARJETA, nuevo=""),
    dict(id="mk-book-traer-sin-atrapar", pruebas=[BOOK_MK], viejo=TRAE_TARJETA,
         nuevo="    tarjeta.scroll_into_view_if_needed(timeout=3000)\n"),
    # Sin la regla de los 100 px, o con el borde incluido.
    dict(id="mk-book-sin-la-regla", pruebas=[BOOK_MK], viejo="            if box and box['y'] > 100:\n",
         nuevo="            if box:\n"),
    dict(id="mk-book-regla-con-el-borde", pruebas=[BOOK_MK], viejo="            if box and box['y'] > 100:\n",
         nuevo="            if box and box['y'] >= 100:\n"),
    # El clic que falla: sin atraparlo, o probando el otro elemento del mismo control (un clic nuevo).
    dict(id="mk-book-clic-sin-atrapar", pruebas=[BOOK_MK], viejo=CLIC_BOOK,
         nuevo=("                btn.scroll_into_view_if_needed(timeout=3000)\n"
                "                btn.click(timeout=4000)\n")),
    dict(id="mk-book-reintenta-el-clic", pruebas=[BOOK_MK],
         viejo='                    return f"el clic en el «Book» falló ({_texto_error(e)})"\n',
         nuevo="                    continue\n"),
    # _mk_elegir_nave devuelve el «Book» sin pulsar como la nave que no está, o sin decir por qué en log.txt.
    dict(id="mk-elegir-book-como-sin-nave", pruebas=[BOOK_VUELVE],
         viejo="            return \"\", None, None, (elegida, sin_pulsar)\n",
         nuevo="            return \"\", None, None, None\n"),
    dict(id="mk-elegir-book-sin-el-porque", pruebas=[BOOK_VUELVE],
         viejo='            reg.info(f"no pude pulsar el «Book» de la salida elegida: {sin_pulsar}")\n',
         nuevo='            reg.info("no pude pulsar el «Book» de la salida elegida")\n'),
    # El motivo: sin la evidencia, o REVISAR.
    dict(id="mk-book-sin-evidencia", pruebas=[BOOK_NO_ENVIADA],
         viejo='    _mk_detenida(page, reg, reserva["fila"])\n    return _no_enviada(reg, f"MAERSK: la nave',
         nuevo='    return _no_enviada(reg, f"MAERSK: la nave'),
    dict(id="mk-book-revisar", pruebas=[BOOK_NO_ENVIADA, MK + "test_revisar_solo_si_la_nave_no_esta"],
         viejo="    return _no_enviada(reg, f\"MAERSK: la nave '{reserva['nave']}' estaba en «Select sailing» y elegí",
         nuevo="    return (\"REVISAR\", f\"MAERSK: la nave '{reserva['nave']}' estaba en «Select sailing» y elegí"),
    # reservar_maersk sin la rama: seguiría por la de la nave que no está.
    dict(id="mk-reserva-sigue-sin-book", pruebas=[BOOK_RAMA],
         viejo="    if sin_book:\n        return _mk_book_sin_pulsar(page, reg, reserva, *sin_book)\n", nuevo=""),
    # El prefijo como hasta ahí: la letra con tilde y la ñ se caen.
    dict(id="mk-prefijo-quita-las-tildes",
         pruebas=[SUG_TILDES, SUG + "test_cma_reconoce_la_lista_con_una_tilde_en_las_primeras_letras"],
         viejo=PREFIJO_MK,
         nuevo='    plano = " ".join(str(ciudad or "").split())\n'),
]

# --- Encargo 47: vuelve la recarga de la página de error que sale tras el «Next» del login de MSC, una sola vez, sin
# reenviar la clave ni otro intento de inicio de sesión (decisión de Marcelo, CICLO-msc-recarga-y-corrida-02-10.md) ---
MSC_REC = "test_clics.TestMsc.test_tras_el_error_del_next_recarga_una_vez"
RECARGA = ('        page.reload(wait_until="domcontentloaded")\n    except Exception as e:\n'
           '        reg.info(f"no pude recargar la página')
TRAS_EL_NEXT = "    if paso == \"error\":\n        paso = _msc_recargar(page, reg)\n"
ESPERA = ('    paso = _msc_esperar(page, reg, "la contraseña, la sesión o el error tras la recarga", '
          'campo="input[type=password]")\n')

MUTACIONES += [
    # Sin recargar, sin llamarla tras el «Next», dos veces, o también tras el error del botón de entrar.
    dict(id="msc-recarga-sin-recargar", pruebas=[MSC_REC],
         viejo=RECARGA, nuevo=RECARGA.replace('page.reload(wait_until="domcontentloaded")', "pass")),
    dict(id="msc-recarga-no-tras-el-next", pruebas=[MSC_REC], viejo=TRAS_EL_NEXT, nuevo=""),
    dict(id="msc-recarga-dos-veces", pruebas=[MSC_REC], viejo=TRAS_EL_NEXT, nuevo=TRAS_EL_NEXT + TRAS_EL_NEXT),
    dict(id="msc-recarga-tras-cualquier-error", pruebas=[MSC_TRAS],
         viejo=('    return _msc_esperar(page, reg, "la sesión o el error tras el botón de entrar", on_pausa=on_pausa, '
                'validar=True)\n'),
         nuevo=('    paso = _msc_esperar(page, reg, "la sesión o el error tras el botón de entrar", on_pausa=on_pausa, '
                'validar=True)\n    return _msc_recargar(page, reg) if paso == "error" else paso\n')),
    # La pausa: sin ella, o con otra.
    dict(id="msc-recarga-sin-la-pausa", pruebas=[MSC_REC], viejo="    esperar(page, MSC_PAUSA_RECARGA)\n", nuevo=""),
    dict(id="msc-recarga-otra-pausa", pruebas=[MSC_REC], viejo="MSC_PAUSA_RECARGA = 20\n",
         nuevo="MSC_PAUSA_RECARGA = 3\n"),
    # Tras la recarga: vuelve a escribir el usuario, o espera también su campo (y en la portada escribe la clave).
    dict(id="msc-recarga-vuelve-a-escribir-el-usuario", pruebas=[MSC_REC], viejo=ESPERA,
         nuevo='    rellenar(page, "#UserName, input[type=email]", "u", 12000, reg)\n' + ESPERA),
    dict(id="msc-recarga-espera-tambien-el-usuario", pruebas=[MSC_REC], viejo=ESPERA,
         nuevo=ESPERA.replace('campo="input[type=password]"', 'campo="input[type=password], #UserName"')),
    # Sin decirlo en pantalla, o sin su captura.
    dict(id="msc-recarga-sin-aviso", pruebas=[MSC_REC],
         viejo='    reg.paso(f"⚠ MSC mostró una página de error al pulsar «Next».',
         nuevo='    reg.info(f"⚠ MSC mostró una página de error al pulsar «Next».'),
    dict(id="msc-recarga-sin-captura", pruebas=[MSC_REC],
         viejo='    reg.url(page); reg.captura(page, "msc_error_next")\n', nuevo="    reg.url(page)\n"),
]

# --- Encargo 48: MAERSK toma el mes y el año del calendario de su cabecera; COSCO sin formulario, NO ENVIADA con
# evidencia, y REVISAR solo para la nave no encontrada; CMA arma su prefijo como MAERSK (decisiones de Marcelo,
# CICLO-calendario-cosco-y-cma.md) ---
RT_JS_CABECERA = RT + "test_js_calendario_por_su_cabecera"
COSCO_SIN_FORM = "test_clics.TestCosco.test_sin_formulario_queda_no_enviada_con_evidencia"
COSCO_REVISAR = "test_clics.TestCosco.test_revisar_solo_si_la_nave_no_esta"
CMA_TILDES = SUG + "test_cma_reconoce_la_lista_con_una_tilde_en_las_primeras_letras"
CAB_USA = "        const cab = leyendas.length ? '' : cabecera();\n"
CAB_VALIDA = ("            return numeros.length === ultimo && numeros.every((n, i) => n === i + 1)\n"
              "                ? anio + '-' + String(mkMes(mes) + 1).padStart(2, '0') : '';\n")
COSCO_EVID = ('    _evidencia_antes_de_la_guarda(page, reg, f"cosco_f{f}_sin_formulario", "sin el formulario de New '
              'Booking",\n                                  completa=False)\n')
COSCO_NO_ENVIADA = ('    return _no_enviada(reg, f"COSCO: abrí New Booking y {que} en {segundos:.0f} s; no pulsé '
                    'nada y la ')
SIN_MARCO = ('        return _cosco_sin_formulario(page, reg, f, "no apareció el marco de su formulario (bkg2)", '
             'desde)\n')
SIN_CAMPOS = ('        return _cosco_sin_formulario(page, reg, f, "su formulario (el marco bkg2) no mostró sus campos '
              '(«Origin City»)",\n                                     desde)\n')
PREF_VIEJO = '    pref = "".join(ch for ch in ciudad if ord(ch) < 128).strip()[:5] or ciudad[:4]\n'

MUTACIONES += [
    # La cabecera: sin usarla, también con una leyenda, con dos meses, oculta, con cualquier número por año, sin mirar
    # los días, contando los de otro mes, o diciendo que la fecha salió de la leyenda.
    dict(id="mk-cabecera-no-se-usa", pruebas=[RT_JS_CABECERA], viejo=CAB_USA, nuevo="        const cab = '';\n"),
    dict(id="mk-cabecera-aunque-haya-leyenda", pruebas=[RT_JS_CABECERA], viejo=CAB_USA,
         nuevo="        const cab = cabecera();\n"),
    dict(id="mk-cabecera-con-dos-meses", pruebas=[RT_JS_CABECERA],
         viejo="                return afuera.length === 1 ? nombre(afuera[0].el) : '';\n",
         nuevo="                return afuera.length >= 1 ? nombre(afuera[0].el) : '';\n"),
    dict(id="mk-cabecera-oculta", pruebas=[RT_JS_CABECERA],
         viejo="            const botones = todos.filter(x => enRaiz(x) && esBoton(x.el) && mkVisible(x.el));\n",
         nuevo="            const botones = todos.filter(x => enRaiz(x) && esBoton(x.el));\n"),
    dict(id="mk-cabecera-anio-cualquier-numero", pruebas=[RT_JS_CABECERA],
         viejo="anio = unico(t => /^\\d{4}$/.test(t));", nuevo="anio = unico(t => /^\\d+$/.test(t));"),
    dict(id="mk-cabecera-sin-mirar-los-dias", pruebas=[RT_JS_CABECERA], viejo=CAB_VALIDA,
         nuevo="            return anio + '-' + String(mkMes(mes) + 1).padStart(2, '0');\n"),
    dict(id="mk-cabecera-cuenta-los-de-otro-mes", pruebas=[RT_JS_CABECERA],
         viejo="celdas.filter(c => enRaiz(c.x) && !fueraDe(c)).map(c => c.dia)",
         nuevo="celdas.filter(c => enRaiz(c.x)).map(c => c.dia)"),
    dict(id="mk-cabecera-dice-mes", pruebas=[RT_JS_CABECERA],
         viejo="como = fecha ? (cab ? 'cabecera' : 'mes') : '';", nuevo="como = fecha ? 'mes' : '';"),
    # COSCO sin formulario: REVISAR, sin la evidencia, con la captura de la página entera o sin los segundos; y en
    # reservar_cosco, los dos cortes de vuelta en REVISAR.
    dict(id="cosco-sin-formulario-revisar", pruebas=[COSCO_SIN_FORM], viejo=COSCO_NO_ENVIADA,
         nuevo=COSCO_NO_ENVIADA.replace("return _no_enviada(reg, ", 'return ("REVISAR", ')),
    dict(id="cosco-sin-formulario-sin-evidencia", pruebas=[COSCO_SIN_FORM], viejo=COSCO_EVID, nuevo=""),
    dict(id="cosco-sin-formulario-pagina-entera", pruebas=[COSCO_SIN_FORM], viejo=COSCO_EVID,
         nuevo=COSCO_EVID.replace("completa=False", "completa=True")),
    dict(id="cosco-sin-formulario-sin-segundos", pruebas=[COSCO_SIN_FORM], viejo=COSCO_NO_ENVIADA,
         nuevo=COSCO_NO_ENVIADA.replace(" en {segundos:.0f} s", "")),
    dict(id="cosco-sin-marco-revisar", pruebas=[COSCO_SIN_FORM, COSCO_REVISAR], viejo=SIN_MARCO,
         nuevo='        return ("REVISAR", "no cargó el formulario de booking")\n'),
    dict(id="cosco-sin-campos-revisar", pruebas=[COSCO_SIN_FORM, COSCO_REVISAR], viejo=SIN_CAMPOS,
         nuevo='        return ("REVISAR", "el formulario de COSCO no cargó los campos a tiempo")\n'),
    # CMA: el puerto o el lugar de entrega con el prefijo de antes, con la letra con tilde y la ñ caídas.
    dict(id="cma-puerto-prefijo-con-tildes-caidas", pruebas=[CMA_TILDES],
         viejo="    pref = _prefijo_de_la_lista(ciudad)\n    rx = _r.compile(_r.escape(pref), _r.I)\n",
         nuevo=PREF_VIEJO + "    rx = _r.compile(_r.escape(pref), _r.I)\n"),
    dict(id="cma-entrega-prefijo-con-tildes-caidas", pruebas=[CMA_TILDES],
         viejo="    pref = _prefijo_de_la_lista(ciudad)\n    sel = ",
         nuevo=PREF_VIEJO + "    sel = "),
]
