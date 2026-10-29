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
# Desde el encargo 51, las llaves las mira _llaves_abiertas, y es_modo_emision dice si encontró una: las mutaciones del
# candado, sobre ese código, con las mismas pruebas de test_candado, que no cambia.
FIN_CANDADO = ('            _avisar_llave_config(valor)\n    except Exception:\n        pass\n'
               '    return abiertas\n\n\ndef _avisar_llave_config')
AVISO_PANEL = '    try:\n        _wlog(texto)\n    except Exception:\n        pass'
AVISO_CONSOLA = '    try:\n        print(texto, flush=True)\n    except Exception:\n        pass\n    try:\n        _wlog(texto)'
LLAVE_OTRA = CAND + "test_llave_config_con_otro_valor_no_abre_y_avisa"
LLAVE_LOG = CAND + "test_aviso_va_al_log_de_la_corrida"
LLAVE_WEB = "test_web.TestPanelRutas.test_llave_invalida_se_avisa_en_pantalla"
# El decorador _sin_clic_a_ciegas de cada reservador, como está escrito: desde el encargo 55, el de CMA guarda con plazo
# el HTML del paso sin objetivo.
SIN_CLIC = {p: f'@_sin_clic_a_ciegas("{p}")\n' for p in ("one", "msc", "cosco", "hmm", "mk")}
SIN_CLIC["cma"] = '@_sin_clic_a_ciegas("cma", plazo_ms=CMA_PLAZO_MS)\n'

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
         viejo=FIN_CANDADO,
         nuevo=FIN_CANDADO.replace("    return abiertas\n", "    return abiertas or ['una llave']\n")),
    dict(id="candado-abre-si-falla-config", pruebas=[ARNES + "test_candado_cerrado_sin_config"],
         viejo=FIN_CANDADO, nuevo=FIN_CANDADO.replace("        pass\n", "        return ['una llave']\n")),
    dict(id="entorno-acepta-no", pruebas=[CAND + "test_tres_apagadas_nunca_emite"],
         viejo='("1", "true", "si", "yes")', nuevo='("1", "true", "si", "yes", "no")'),
    dict(id="entorno-sin-yes", pruebas=[CAND + "test_llave_entorno_sola_abre"],
         viejo='("1", "true", "si", "yes")', nuevo='("1", "true", "si")'),
    dict(id="entorno-no-abre",
         pruebas=[CAND + "test_basta_una_llave_de_tres", CAND + "test_llave_entorno_sola_abre"],
         viejo='in ("1", "true", "si", "yes"):\n        abiertas.append(',
         nuevo='in ("1", "true", "si", "yes") and False:\n        abiertas.append('),
    dict(id="argumento-sin-guiones", pruebas=[CAND + "test_llave_argumento_sola_abre"],
         viejo='("emitir", "--emitir", "produccion", "--produccion")',
         nuevo='("emitir", "produccion", "--produccion")'),
    dict(id="config-otra-clave",
         pruebas=[CAND + "test_llave_config_abre_solo_con_true", CAND + "test_basta_una_llave_de_tres"],
         viejo='.get("emitir_reservas", False)', nuevo='.get("emitir_reserva", False)'),
    # --- La llave de config abre solo con el booleano true, y lo demás avisa ---
    dict(id="config-abre-con-cualquier-verdadero", pruebas=[LLAVE_OTRA],
         viejo='        if valor is True:\n            abiertas.append(',
         nuevo='        if valor:\n            abiertas.append('),
    dict(id="config-sin-aviso", pruebas=[LLAVE_OTRA, LLAVE_LOG, LLAVE_WEB],
         viejo='        elif valor is not False and not abiertas:\n            _avisar_llave_config(valor)',
         nuevo='        elif False:\n            _avisar_llave_config(valor)'),
    dict(id="config-avisa-tambien-con-false", pruebas=[CAND + "test_llave_config_abre_solo_con_true"],
         viejo='        elif valor is not False and not abiertas:\n            _avisar_llave_config(valor)',
         nuevo='        elif True:\n            _avisar_llave_config(valor)'),
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

# --- Encargo 39 · commit 1: los lanzadores instalaban holidays si faltaba, sin frenar el arranque sin red
# (CICLO-maersk-cuatro-puntos.md). Desde el encargo 84 no instalan nada por su cuenta: lo hace preparar_entorno.py, con
# hash. Estas mutaciones, sobre el .bat nuevo: que vuelvan a instalar con pip, o que el preparador quede fuera. ---
PREPARA_BAT = "  python -I preparar_entorno.py\n"
LANZ_BAT = "test_consola.TestLanzadores.test_no_instalan_con_pip_y_llaman_al_preparador_antes_de_abrir"
PIP_BAT = ('  python -m pip install --user --disable-pip-version-check --timeout 5 --retries 0 holidays\n')

MUTACIONES += [
    dict(id="bat-vuelve-a-instalar-holidays", archivo="Iniciar AQUASHIELD.bat", pruebas=[LANZ_BAT],
         viejo=PREPARA_BAT, nuevo=PIP_BAT + PREPARA_BAT),
    dict(id="bat-emision-vuelve-a-instalar-holidays", archivo="Iniciar AQUASHIELD_EMISION.bat", pruebas=[LANZ_BAT],
         viejo=PREPARA_BAT, nuevo=PIP_BAT + PREPARA_BAT),
    dict(id="bat-sin-el-preparador", archivo="Iniciar AQUASHIELD.bat", pruebas=[LANZ_BAT], viejo=PREPARA_BAT, nuevo=""),
    dict(id="bat-emision-sin-el-preparador", archivo="Iniciar AQUASHIELD_EMISION.bat", pruebas=[LANZ_BAT],
         viejo=PREPARA_BAT, nuevo=""),
    dict(id="bat-el-preparador-despues-del-panel", archivo="Iniciar AQUASHIELD.bat", pruebas=[LANZ_BAT],
         cambios=[(PREPARA_BAT, ""), ('  start "" pythonw "AQUASHIELD.py"\n',
                                      '  start "" pythonw "AQUASHIELD.py"\n' + PREPARA_BAT)]),
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
         viejo="                              or CONTENEDOR_DE_LAS_FILAS,\n",
         nuevo="                              or \"20 DRY\",\n"),
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
         viejo="    return _leer_tras_envio(page, FORMA_BOOKING.get(naviera), espera, plazo_ms)\n",
         nuevo='    return _leer_tras_envio(page, FORMA_BOOKING.get(naviera, r"(SCLG\\d{8})"), espera, plazo_ms)\n'),
    dict(id="lectura-solo-la-pagina", pruebas=[TE + "test_lee_los_marcos", TE + "test_un_marco_que_falla_no_tapa_a_los_demas"],
         viejo="        for alcance in [page] + otros:\n", nuevo="        for alcance in [page]:\n"),
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
         viejo='hay_ifr = bool(_cma_leer(page, ', nuevo='hay_ifr = False and bool(_cma_leer(page, '),
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
    dict(id="web-config-ausente-otro-aviso", pruebas=[RU + "test_config_ausente_sin_plantilla_lo_dice"],
         viejo='"Falta config.json, y tampoco está config.example.json para crearlo. Vuelve a instalar "',
         nuevo='"Falta la configuración. Vuelve a instalar "'),
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
         viejo='_disposicion(f"{nom} - resultados {marca}.xlsx")', nuevo='_disposicion(f"{nom}-resultados {marca}.xlsx")'),
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
         viejo='sub_elegidas = [f for f in elegidas if _nav_de_la_fila(nav_obj, f) == nav]',
         nuevo='sub_elegidas = [f for f in elegidas if _nav_de_la_fila(nav_obj, f) in (nav, None)]'),
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
         viejo='esperar_cierre=lambda: _time.sleep(6), ', nuevo='esperar_cierre=lambda: _time.sleep(1), '),
    dict(id="login-acepta-navieras-desconocidas", pruebas=[CO + "test_modo_login"],
         viejo='navs = [n for n in (d.get("navieras") or []) if n in NAVIERAS]', nuevo='navs = list(d.get("navieras") or [])'),
    dict(id="previa-ociosa-no-se-apaga", pruebas=[AR + "test_instancia_previa_ociosa_se_apaga"],
         viejo='req = urllib.request.Request(f"http://127.0.0.1:{puerto}/api/apagar", data=b"{}", method="POST",',
         nuevo='req = urllib.request.Request(f"http://127.0.0.1:{puerto}/api/estado", data=b"{}", method="POST",'),
    dict(id="previa-ocupada-se-toca", pruebas=[AR + "test_instancia_previa_ocupada_no_se_toca"],
         viejo='    if estado.get("corriendo"):\n', nuevo='    if estado.get("corriendo") and False:\n'),
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
         viejo='    if on_pausa:\n        return _pausa_del_panel(reg, on_pausa, mensaje)\n',
         nuevo='    if on_pausa:\n        return\n'),
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
              "        try:\n"
              "            bkg = numero_tras_envio(page, naviera, plazo_ms=plazo_ms)\n")
EVIDENCIA = "    _guardar_evidencia(page, reg, evidencia, plazo_ms=plazo_ms)\n    if pulsado is False:\n"
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
         cambios=[('    rechazo = [str(c) for c in (campos or [])]\n    bkg = ref = contradice = ""\n',
                   '    rechazo = [str(c) for c in (campos or [])]\n    _guardar_evidencia(page, reg, evidencia)\n'
                   '    bkg = ref = contradice = ""\n'),
                  (EVIDENCIA, "    if pulsado is False:\n")]),
    dict(id="envio-emitida-sin-log", pruebas=[EN + "test_emitida_solo_con_la_forma_medida"],
         viejo='        reg.paso(f"🎉 {nombre}: Reserva EMITIDA con éxito. Booking: {bkg}")\n'
               '        return ("EMITIDA", f"{nombre} emitida con éxito (Booking: {bkg})")\n    if ambiguas:',
         nuevo='        return ("EMITIDA", f"{nombre} emitida con éxito (Booking: {bkg})")\n    if ambiguas:'),
    dict(id="envio-falla-al-pulsar-como-pulsado", pruebas=[EN + "test_falla_al_pulsar_pudo_salir"],
         viejo="    if pulsado is None:\n        que =", nuevo="    if False:\n        que ="),
    dict(id="envio-falla-tras-pulsar-callada", pruebas=[EN + "test_falla_del_programa_despues_de_pulsar"],
         viejo="    elif error is not None:\n        que =", nuevo="    elif False:\n        que ="),
    dict(id="envio-error-del-portal-callado", pruebas=[EN + "test_error_del_portal_es_enviada"],
         viejo="    elif error_portal:\n        que =", nuevo="    elif False:\n        que ="),
    dict(id="envio-sin-forma-como-medida", pruebas=[EN + "test_naviera_sin_forma_nunca_es_emitida"],
         viejo="    elif naviera in FORMA_BOOKING:\n        que =", nuevo="    elif True:\n        que ="),
    dict(id="envio-enviada-sin-log", pruebas=[EN + "test_pulsado_sin_confirmacion_es_enviada"],
         viejo='{_REVISA_PORTAL}"\n    reg.paso(f"⚠ {ENVIADA_REVISAR} · {detalle}")',
         nuevo='{_REVISA_PORTAL}"\n    pass'),
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
         viejo="marcos = [f for f in (getattr(page, \"frames\", None) or []) if f is not page and f is not principal]",
         nuevo="marcos = [f for f in (getattr(page, \"frames\", None) or []) if f is not page]"),
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
         viejo='color:var(--text-primary)">revisar en portal</span>`;', nuevo='color:var(--text-primary)">revisar</span>`;'),
    dict(id="panel-sin-usar-la-lectura", pruebas=[LP + "test_cada_lectura_nueva_pinta_su_fila"],
         viejo="        const lectura = lecturaEstado(est);", nuevo='        const lectura = "otro";'),
    # Solo una EMITIDA tiene número; los lectores y la consola no cambian con los estados nuevos
    dict(id="limpio-de-cualquier-estado",
         pruebas=[LI + "test_solo_una_emitida_tiene_numero", CO + "test_corrida_con_estados_tras_el_envio"],
         viejo='    if estado != "EMITIDA":\n        return ""\n', nuevo=""),
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
         viejo=DECIDE_CMA + "                                    error, plazo_ms=CMA_PLAZO_MS)",
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
             '                            campos=campos, error_portal=error_portal, campos_en_duda=en_duda)\n')
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
         pruebas=[CO_ + "test_errores_de_validacion_esperan_hasta_el_tope", CO_ + "test_espera_corta_con_aviso_del_portal"],
         viejo="        if campos or error_portal:\n            break\n", nuevo="        if False:\n            break\n"),
    dict(id="cosco-espera-no-anota-el-reminder",
         pruebas=[CO_ + "test_reminder_no_se_pulsa", CO_ + "test_reminder_tardio_tampoco_se_pulsa",
                  CO_ + "test_al_agotarse_lee_los_errores"],
         viejo="            vio_reminder = rem_abierta = True\n", nuevo="            rem_abierta = True\n"),
    dict(id="cosco-espera-otro-plazo",
         pruebas=[CO_ + "test_espera_se_agota", CO_ + "test_reminder_tardio_tampoco_se_pulsa",
                  CO_ + "test_al_agotarse_lee_los_errores"],
         viejo="COSCO_ESPERA_CONFIRMACION_SEG = 180\n", nuevo="COSCO_ESPERA_CONFIRMACION_SEG = 150\n"),
]

# --- Clics a ciegas antes de la guarda (CICLO-clics-a-ciegas.md) ---
SC = "test_clics.TestSinClicACiegas."
EVIDENCIA_CORTE = ("                _evidencia_antes_de_la_guarda(page, reg, f\"{prefijo}_f{(reserva or {}).get('fila')}"
                   "_sin_objetivo\",\n                                              \"en el paso sin objetivo\", "
                   "completa=False, plazo_ms=plazo_ms)\n")
# La condición del «Guardar» del panel Reefer (desde el encargo 55, contado y leído con plazo).
REEFER_GUARDAR = ("        if _cma_cuantos(page, btn_g) != 1 or not btn_g.evaluate(_JS_CMA_REEFER_GUARDAR, "
                  "timeout=CMA_PLAZO_MS):\n")
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
         viejo=SIN_CLIC["cma"], nuevo=""),
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
         viejo='    raise ObjetivoNoEncontrado("«I Agree» de CMA", CMA_CASILLA_I_AGREE)\n',
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
HTML_EG = ("        guardados, total, sin_shadow = _guardar_html_completo(page, reg, nombre, momento, "
           "plazo_ms=plazo_ms)\n")
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
         viejo="full_page=completa or bool(pagina_entera),", nuevo="full_page=completa,"),
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
         viejo='        _evidencia_antes_de_la_guarda(page, reg, f"cma_f{f}_guarda", plazo_ms=CMA_PLAZO_MS)\n',
         nuevo=""),
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
         viejo='    _anotar_candado(reg)\n    _podar_html_viejo(reg)\n', nuevo='    _anotar_candado(reg)\n'),
    dict(id="poda-no-corre-en-la-web", pruebas=[PO + "test_corre_al_empezar_cada_corrida_de_reservas"],
         viejo='        _anotar_candado(reg)\n        _podar_html_viejo(reg)\n',
         nuevo='        _anotar_candado(reg)\n'),
]

# --- CMA: la evidencia dentro del panel Reefer (CICLO-cma-reefer-y-fecha-maersk.md) ---
ER_ = "test_evidencia.TestEvidenciaReefer."
PANEL_R = ('        _evidencia_antes_de_la_guarda(page, reg, f"cma_f{f}_reefer_panel", "en el panel Reefer", '
           'completa=False,\n                                      plazo_ms=CMA_PLAZO_MS)\n')
GUARDADO_R = ('        _evidencia_antes_de_la_guarda(page, reg, f"cma_f{f}_reefer_guardado", "tras guardar el panel Reefer",\n'
              '                                      completa=False, plazo_ms=CMA_PLAZO_MS)\n')
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
         viejo='@_sin_clic_a_ciegas("mk")\n@_mk_con_el_contenedor_de_la_fila\ndef reservar_maersk(',
         nuevo="@_mk_con_el_contenedor_de_la_fila\ndef reservar_maersk("),
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
LLAMADA_RT = ("            corte = _mk_fecha_de_retiro(page, reg, det, f, plazo=eleccion.get(\"plazo\", \"\"))\n"
              "            if corte:\n                return corte\n")

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
         # Desde el encargo 69, la lectura de los días va en _mk_fechas_del_calendario, sin el día que toca: la fecha
         # que no existe cuenta como el 22-09, el que toca en la prueba.
         viejo="        except ValueError:\n            continue\n    return fechas\n",
         nuevo=("        except ValueError:\n            fechas[datetime.date(2026, 9, 22)] = True\n"
                "    return fechas\n")),
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
         viejo="    if elegido is None:\n        no_deja = _mk_plazo_no_deja(",
         nuevo="    if False:\n        no_deja = _mk_plazo_no_deja("),
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

# --- COSCO: la ventana «Reminder»: solo se espera; de su Submit no se pulsa nada (hasta el encargo 78 se pulsaba una vez,
# CICLO-revision-corrida-completa.md; desde el 78, CICLO-decisiones-tras-el-envio.md) ---
REMINDER_ESPERA = "            vio_reminder = rem_abierta = True\n            continue\n"
REMINDER_NO_PULSA = [CO_ + "test_reminder_no_se_pulsa", CO_ + "test_reminder_tardio_tampoco_se_pulsa"]

MUTACIONES += [
    # Vuelve a pulsar un Submit con la ventana a la vista: por JavaScript, o buscándolo con un localizador.
    dict(id="cosco-reminder-vuelve-a-pulsar", pruebas=REMINDER_NO_PULSA,
         viejo=REMINDER_ESPERA,
         nuevo=REMINDER_ESPERA.replace("            continue\n",
                                       "            _cosco_en_alguno(frame, page, _JS_COSCO_SUBMIT)\n            continue\n")),
    dict(id="cosco-reminder-busca-su-submit", pruebas=REMINDER_NO_PULSA,
         viejo=REMINDER_ESPERA,
         nuevo=REMINDER_ESPERA.replace("            continue\n",
                                       "            frame.locator(\"button:has-text('Submit')\")\n            continue\n")),
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
         viejo='            raise ObjetivoNoEncontrado("Tamaño y tipo de CMA", CMA_TAMANO_Y_TIPO + (f", porque {CMA_SIN_RESPUESTA}"\n                                                                                    if sin_respuesta else ""))\n',
         nuevo='            page.keyboard.press("ArrowDown"); esperar(page, 0.4); page.keyboard.press("Enter")\n'),
    dict(id='teclado-cma-mercancia', pruebas=[C1 + "test_tamano_y_mercancia_no_eligen_con_el_teclado", FG],
         viejo='            raise ObjetivoNoEncontrado("Mercancía de CMA", CMA_MERCANCIA)\n',
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
         viejo='        raise ObjetivoNoEncontrado("Comentarios de CMA", CMA_CAMPO_COMENTARIOS)\n',
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
         viejo='.strip() or _peso_reefer()\n',
         nuevo='.strip() or PESO_REEFER\n'),
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
         viejo=REEFER_GUARDAR,
         nuevo=('        if not btn_g.count():\n            btn_g = page.locator(".el-drawer .el-button--primary, '
                '[role=\'dialog\'] .el-button--primary")\n' + REEFER_GUARDAR)),
    dict(id='cma-reefer-guarda-sin-mirar-el-panel', pruebas=[C1 + "test_reefer_corta_en_cada_paso_sin_pulsar_a_ciegas", ER_ + "test_sin_el_guardar_del_panel_no_pulsa_ni_deja_lo_guardado"],
         viejo=' or not btn_g.evaluate(_JS_CMA_REEFER_GUARDAR, timeout=CMA_PLAZO_MS)',
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
JS_LISTA_COSCO = K1 + "test_js_lista_lee_la_salida_y_la_llegada_de_la_tarjeta"

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
    dict(id="cosco-js-fechas-del-boton", pruebas=[JS_LISTA_COSCO],
         viejo="const fechas=[...tarjeta(b).querySelectorAll('*')]", nuevo="const fechas=[...b.querySelectorAll('*')]"),
    dict(id="cosco-js-tarjeta-toda-la-lista", pruebas=[JS_LISTA_COSCO],
         viejo="btns.filter(x=>c.parentElement.contains(x)).length===1) c=c.parentElement;",
         nuevo="btns.filter(x=>c.parentElement.contains(x)).length>=1) c=c.parentElement;"),
    dict(id="cosco-js-corte-como-salida", pruebas=[JS_LISTA_COSCO],
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
         viejo='    hay_nave = bool(tarjetas)\n    desde = _desde(reserva)\n',
         nuevo='    hay_nave = bool(tarjetas)\n    desde = datetime.date.today()\n'),
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
         viejo=('        _evidencia_antes_de_la_guarda(page, reg, nombre, "en la lista de rutas", completa=False,\n'
                '                                      plazo_ms=CMA_PLAZO_MS)\n'),
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
         viejo="const matched = !!tramo && _traeLaNave(vessel.toUpperCase(), toks);",
         nuevo="const matched = !!tramo && _traeLaNave(vessel.toUpperCase(), toks.filter(tk => !['MSC', 'CMA', 'CGM', "
               "'HMM', 'ONE', 'COSCO', 'MV'].includes(tk)));"),
    dict(id="cma-nave-sin-guarda-vacia", pruebas=[C1 + "test_js_rutas_nave_con_todas_sus_palabras"],
         viejo="const matched = !!tramo && _traeLaNave(vessel.toUpperCase(), toks);",
         nuevo="const matched = !!tramo && toks.every(tk => _palabraEn(vessel.toUpperCase(), tk, 0) >= 0);"),
    # El calce de CMA como era hasta 9051f43, en sus tres lugares: las palabras sin los prefijos de naviera, que se
    # pasaban a la lectura como «sigToks» y le bastaban para calzar.
    dict(id="cma-vuelve-sin-prefijos", pruebas=[C1 + "test_itinerario_comodin_no_se_busca_como_nave"], cambios=[
        ("if nave_especificada else [])\n",
         'if nave_especificada else [])\n    sig_toks = [t for t in toks if t not in {"MSC", "CMA", "CGM", "HMM", "ONE", '
         '"COSCO", "MV"}] or toks\n'),
        ('res = _cma_js(page, _JS_CMA_RUTAS, {"toks": toks, "viaje": _palabras_del_viaje(viaje_pedido)})',
         'res = _cma_js(page, _JS_CMA_RUTAS, {"toks": toks, "viaje": _palabras_del_viaje(viaje_pedido), '
         '"sigToks": sig_toks})'),
        ("const matched = !!tramo && _traeLaNave(vessel.toUpperCase(), toks);",
         "const matched = !!tramo && (_traeLaNave(vessel.toUpperCase(), toks) || "
         "_traeLaNave(vessel.toUpperCase(), args.sigToks || []));")]),
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
EV_VR = ('        _evidencia_antes_de_la_guarda(page, reg, f"cma_f{f}_validar_{modo}", "tras «Validar ruta»", '
         'completa=False,\n                                      plazo_ms=CMA_PLAZO_MS)\n')
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
         viejo='@_con_la_nave_de_la_fila\n@_con_la_ruta_de_la_fila\n' + SIN_CLIC[pref],
         nuevo='@_con_la_ruta_de_la_fila\n' + SIN_CLIC[pref])
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
         viejo="const matched = !!tramo && _traeLaNave(vessel.toUpperCase(), toks);",
         nuevo="const matched = !!tramo && toks.length > 0 && toks.every(tk => vessel.toUpperCase().includes(tk));"),
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
         viejo="    _msc_buscar_itinerarios(page, reg, MSC_PUERTOS + (MSC_LISTAS_DEL_DESTINO if separado else ()))\n",
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
# Desde el encargo 50, «ante el error» son dos pruebas: el segundo intento tras el error después de la clave, y los
# otros errores (CICLO-msc-segundo-intento.md); desde el 51, que también reintentan, una sola vez
# (CICLO-modo-y-lanzadores.md): test_otros_errores_no_reintentan pasó a test_cualquier_error_un_solo_intento_mas.
MSC_DOS = "test_clics.TestMsc.test_tras_el_error_despues_de_la_clave_un_solo_intento_mas"
MSC_OTROS = "test_clics.TestMsc.test_cualquier_error_un_solo_intento_mas"
TEXTOS_ERR = 'MSC_TEXTOS_DE_ERROR = ("502", "no puede procesar", "unable to complete your request")\n'
SESION = '    return u.netloc.lower() == "www.mymsc.com" and u.path.lower().rstrip("/") in MSC_PAGINAS_CON_SESION\n'

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
    # Ante el error: sin mirar el error en la espera. Las demás de este grupo mutaban la ida a eBooking, que salió en el
    # encargo 50 (msc-error-sin-ir-a-ebooking, msc-error-dos-veces-a-ebooking, msc-error-reintenta-el-login,
    # msc-error-sin-mirar-la-sesion, msc-error-al-abrir-sin-mirar, msc-error-sin-su-captura y msc-error-sin-aviso): sus
    # equivalentes de hoy están en el bloque del encargo 50.
    dict(id="msc-espera-sin-el-error", pruebas=[MSC_DOS],
         viejo='        if _msc_error(page):\n            return "error"\n', nuevo=""),
    # Sin la sesión de MSC, la fila queda sin estado, como antes, en el panel o en la consola; o NO ENVIADA con
    # cualquier naviera.
    dict(id="msc-sin-sesion-panel-sin-estado", pruebas=[CO + "test_login_fallido_de_msc_queda_no_enviada"],
         viejo="                    for rsv in (sub_elegidas if _motivo_sin_sesion(reg, nav) else ()):\n",
         nuevo="                    for rsv in ():\n"),
    dict(id="msc-sin-sesion-consola-sin-estado", pruebas=[ER + "test_login_fallido_de_msc_queda_no_enviada"],
         viejo="            for i, rsv in (con_nave if _motivo_sin_sesion(reg, naviera_clave) else ()):\n",
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
         viejo='" ".join(str(texto or "").lower().split())\n',
         nuevo='str(texto or "").lower()\n'),
    dict(id="cma-mant-sin-leer", pruebas=[CMA_AVISO],
         viejo='" ".join(str(texto or "").lower().split())\n',
         nuevo=('(" ".join(str(texto or "").lower().split())\n'
                '        or "we are improving the ebusiness area")\n')),
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
         viejo=" || t.directa !== args.directa) return false;\n    const viaje = args.viaje || [];\n    if (viaje.length && "
               "!_traeLaNave(t.primera",
         nuevo=") return false;\n    const viaje = args.viaje || [];\n    if (viaje.length && !_traeLaNave(t.primera"),
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
         viejo='"directa": elegida.get("directa"),\n                                                          "viaje"',
         nuevo='"directa": None,\n                                                          "viaje"'),
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
         viejo=('    disponibles = [t for t in de_la_nave if _hmm_es_la_pedida(t, viaje) and t.get("disponible") and '
                't.get("book") == 1]\n'),
         nuevo="    disponibles = [t for t in de_la_nave if _hmm_es_la_pedida(t, viaje)]\n"),
    dict(id="hmm-elige-sin-la-interfaz-anterior", pruebas=[TH_ELIGE],
         viejo="    if not tarjetas:\n        return _hmm_indice_anterior(page, toks, reg, _palabras_del_viaje(viaje))\n",
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
         viejo="    while not any(_msc_es_la_pedida(x, toks, viaje) for x in naves):\n",
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
         viejo="    vistos = [e.nth(j) for j in range(_cma_cuantos(page, e)) if _cma_se_ve(page, e.nth(j))]\n",
         nuevo="    vistos = [e.nth(j) for j in range(_cma_cuantos(page, e))]\n"),
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
ON_RELEE = ("    if (!t || t.salida !== args.salida || t.directa !== args.directa) return false;\n"
            "    const viaje = args.viaje || [];\n    if (viaje.length && !_traeLaNave(t.nave, viaje)) return false;\n"
            "    const i = args.i;")
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
         viejo="    if not (r.get(\"titulo\") or r.get(\"titulo_nuevo\")):\n        return _mk_shipper_corte(",
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
         viejo="(s.titulo || s.tituloNuevo ? s.conEmpresa : [])", nuevo="s.conEmpresa"),
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
         viejo="for k in (\"resultados\", \"con_empresa\", \"titulo\", \"titulo_nuevo\"))",
         nuevo="for k in (\"resultados\", \"con_empresa\", \"titulo_nuevo\"))"),
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
         viejo="            if (!titulo && !tituloNuevo) return {el: null, por: 'titulo'};\n", nuevo=""),
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
         viejo='@_con_la_ruta_de_la_fila\n' + SIN_CLIC[pref], nuevo=SIN_CLIC[pref])
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
                 '            _evidencia_sin_sugerencia(page, reg, evidencia, etiqueta, plazo_ms=CMA_PLAZO_MS)\n'
                 '        val = _valor()\n')
SIN_LISTA_ENTREGA = ('    if pendiente:\n'
                     '        _evidencia_sin_sugerencia(page, reg, evidencia, "el lugar de entrega", '
                     'plazo_ms=CMA_PLAZO_MS)\n')
SIN_LISTA = ('    _evidencia_antes_de_la_guarda(page, reg, nombre, f"sin una sugerencia que elegir en {etiqueta}", '
             'completa=False,\n                                  plazo_ms=plazo_ms)\n')

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
         viejo='    celda = (reserva.get("pol") or "").strip()\n    puerto = _puerto_de_carga(celda)\n',
         nuevo='    celda = (reserva.get("pol") or "").strip()\n    puerto = _cosco_puerto_de_la_celda(celda)\n'),
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
         viejo='    celda = (reserva.get("pol") or "").strip()\n    puerto = _puerto_de_carga(celda)\n',
         nuevo=('    celda = (reserva.get("pol") or "").strip()\n'
                '    puerto = _cosco_puerto_de_la_celda(_ciudad_de(celda))\n')),
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
# Desde el encargo 74, lo de afuera de los paréntesis sale de _mk_partes (_mk_base salió); desde el 75, la regla está en
# _mk_ganadoras, que mira la lista entera (en el 74, _mk_calza, par por par).
EXACTAS_MK = "    return cy, textos, _mk_ganadoras(textos, escrita)\n"
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
         viejo='        sin = _re_mk.sub(r"\\(([^()]*)\\)", quitar, t)\n', nuevo="        sin = t\n"),
    dict(id="mk-base-sin-cortar-en-la-coma", pruebas=[FORMA_MK, SUG_EXACTA],
         viejo='    t = str(texto or "").split(",")[0]\n', nuevo='    t = str(texto or "")\n'),
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
MARCAS = "                sin_puerto=falta == FILA_SIN_PUERTO, sin_destino=falta == FILA_SIN_DESTINO,\n"

MUTACIONES += [
    # /api/filas: sin una de las dos marcas, o con las marcas también en la fila sin nave.
    dict(id="panel-sin-marca-de-puerto", pruebas=[RUTA_API], viejo=MARCAS,
         nuevo="                sin_puerto=False, sin_destino=falta == FILA_SIN_DESTINO,\n"),
    dict(id="panel-sin-marca-de-destino", pruebas=[RUTA_API], viejo=MARCAS,
         nuevo="                sin_puerto=falta == FILA_SIN_PUERTO, sin_destino=False,\n"),
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
         viejo=".sin-nave, .sin-ruta, .otro-contenedor { color: var(--text-muted); font-style: italic; }\n",
         nuevo=".sin-nave, .otro-contenedor { color: var(--text-muted); font-style: italic; }\n"),
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
         viejo=('    ctto = str(creds.get("contrato") or "").strip() or _contrato_por_defecto("hyundai")\n'
                '    if not ctto:\n'),
         nuevo='    ctto = str(creds.get("contrato") or "").strip() or "XX12345681"\n    if not ctto:\n'),
    dict(id="contrato-comentario-con-codigo", pruebas=[CD_NO_LOS_TRAE],
         viejo="    # Contrato inteligente: USA u Otros Mercados (_determinar_contrato_one).\n",
         nuevo="    # Contrato inteligente (USA = XX12345682, Otros Mercados = XX12345683)\n"),
    dict(id="hyundai-paso2-sin-guarda", pruebas=[CD_HMM],
         viejo=('    ctto = str(creds.get("contrato") or "").strip() or _contrato_por_defecto("hyundai")\n'
                '    if ctto:\n'),
         nuevo=('    ctto = str(creds.get("contrato") or "").strip() or _contrato_por_defecto("hyundai")\n'
                '    if True:\n')),
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
TRAS_EL_NEXT = "    if tras_el_error:\n        paso = _msc_recargar(page, reg, escucha, intento, creds)\n"
TRAS_LA_CLAVE = ('    paso = _msc_esperar(page, reg, "la sesión o el error tras el botón de entrar", '
                 'on_pausa=on_pausa, validar=True,\n                        sufijo=suf)\n')
ESPERA = ('    paso = _msc_esperar(page, reg, "la contraseña, la sesión o el error tras la recarga", '
          'campo="input[type=password]")\n')

MUTACIONES += [
    # Sin recargar, sin llamarla tras el «Next», dos veces, o también tras el error del botón de entrar.
    dict(id="msc-recarga-sin-recargar", pruebas=[MSC_REC],
         viejo=RECARGA, nuevo=RECARGA.replace('page.reload(wait_until="domcontentloaded")', "pass")),
    dict(id="msc-recarga-no-tras-el-next", pruebas=[MSC_REC], viejo=TRAS_EL_NEXT, nuevo=""),
    dict(id="msc-recarga-dos-veces", pruebas=[MSC_REC], viejo=TRAS_EL_NEXT, nuevo=TRAS_EL_NEXT + TRAS_EL_NEXT),
    dict(id="msc-recarga-tras-cualquier-error", pruebas=[MSC_DOS], viejo=TRAS_LA_CLAVE,
         nuevo=(TRAS_LA_CLAVE + '    if paso == "error":\n'
                '        paso = _msc_recargar(page, reg, escucha, intento, creds)\n')),
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
         viejo='    _msc_evidencia_del_error(page, reg, escucha, f"msc_error_next{suf}", creds)\n', nuevo=""),
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

# --- Encargo 48, lo que encontró la revisión del subagente: el mismo control con nombre en la cabecera, el año de fuera
# del calendario, los días ocultos, un día repetido, y los segundos de cada corte de COSCO ---
MUTACIONES += [
    dict(id="mk-cabecera-sin-un-solo-control", pruebas=[RT_JS_CABECERA],
         viejo="                const afuera = c.filter(x => !x.anc.some(a => de.has(a)));\n",
         nuevo="                const afuera = c;\n"),
    dict(id="mk-cabecera-boton-de-afuera", pruebas=[RT_JS_CABECERA],
         viejo="            const botones = todos.filter(x => enRaiz(x) && esBoton(x.el) && mkVisible(x.el));\n",
         nuevo="            const botones = todos.filter(x => esBoton(x.el) && mkVisible(x.el));\n"),
    dict(id="mk-cabecera-cuenta-los-ocultos", pruebas=[RT_JS_CABECERA],
         viejo="celdas.filter(c => enRaiz(c.x) && !fueraDe(c)).map(c => c.dia)",
         nuevo="celdas.filter(c => enRaiz(c.x) && !FUERA.test(marcas(c))).map(c => c.dia)"),
    dict(id="mk-cabecera-sin-mirar-cada-dia", pruebas=[RT_JS_CABECERA],
         viejo="            return numeros.length === ultimo && numeros.every((n, i) => n === i + 1)\n",
         nuevo="            return numeros.length === ultimo\n"),
    dict(id="cosco-sin-marco-sin-desde", pruebas=[COSCO_SIN_FORM], viejo=SIN_MARCO,
         nuevo=SIN_MARCO.replace("desde)", "time.monotonic())")),
    dict(id="cosco-sin-campos-sin-desde", pruebas=[COSCO_SIN_FORM], viejo=SIN_CAMPOS,
         nuevo=SIN_CAMPOS.replace("desde)", "time.monotonic())")),
]

MSC_CLAVE = "test_clics.TestMsc.test_la_clave_a_lo_mas_dos_veces"
URL_REG = "test_consola.TestUtilitarios.test_url_sin_consulta"

# --- Encargo 50: el login de MSC hace un solo intento más tras el error después de la clave, nunca un tercero, y sin la
# ida a eBooking; cada error deja en log.txt la respuesta que lo trajo, sin valores de sesión, y su captura y su HTML
# sin el usuario ni la clave; las filas de MSC llevan el motivo que dejó el login; y COSCO dice cuándo
# MAPA_PUERTOS_COSCO traduce el puerto de carga (decisiones de Marcelo, CICLO-msc-segundo-intento.md) ---
MSC_EVID = "test_clics.TestMsc.test_el_error_deja_su_respuesta_y_su_evidencia"
MSC_RESP = "test_clics.TestMsc.test_respuesta_del_error_sin_valores_de_sesion"
MSC_HTML = "test_clics.TestMsc.test_html_sin_el_usuario_ni_la_clave"
COSCO_TRAD = "test_clics.TestCosco.test_puerto_traducido_lo_dicen_el_log_y_el_motivo"
CO_MOTIVO = CO + "test_login_de_msc_deja_su_motivo"
ER_MOTIVO = ER + "test_login_de_msc_deja_su_motivo"
INTENTOS = "MSC_INTENTOS = 2\n"
CLAVE_FIN = ('    _msc_evidencia_del_error(page, reg, escucha, f"msc_error_clave{suf}", creds)\n'
             '    return MSC_ERROR_TRAS_LA_CLAVE\n')
FINAL = '    reg.url(page); reg.captura(page, "msc_final")\n    if desenlaces[-1] == "sesión":\n'
HTML_EVID = ('    guardados, total, _ = _guardar_html_completo(page, reg, nombre, "con el error del login de MSC",\n'
             '                                                 sin=_textos_de_la_cuenta(creds))\n')
VALORES = ("    valores = [f\"{k}: {' '.join(str(cab[k]).split())[:80]}\" for k in nombres if k in "
           "MSC_CABECERAS_CON_VALOR]\n")
SIN_CONSULTA = ("        limpia = (f\"{s.scheme}://{servidor}{f':{s.port}' if s.port else ''}{s.path}\" if "
                "s.netloc\n                  else f\"{s.scheme}:{s.path}\" if s.scheme else s.path)\n")
URL_LINEA = "    return limpia + (f\" (sin {' ni '.join(quitado)})\" if decirlo and quitado else \"\")\n"
CON_VALOR = 'MSC_CABECERAS_CON_VALOR = ("server", "via",'
DEL_MARCO = '            return peticion.resource_type == "document" and peticion.frame == page.main_frame\n'
GUARDA_HTML = "            if sin and any(str(t).casefold() in texto.casefold() for t in sin):\n"
TRADUCCION = ('    return otro if otro and not set(_cosco_puerto_de_la_celda(otro).split()) <= set(puerto.split()) '
              'else ""\n')
DECORADORES = ('@_con_el_puerto_de_cosco\n@_con_la_nave_de_la_fila\n@_con_la_ruta_de_la_fila\n'
               '@_sin_clic_a_ciegas("cosco")\n')
DECORADO = "test_clics.TestSinClicACiegas.test_cada_reservador_que_corta_esta_decorado"
MOTIVO = ('    return (_naviera_detenida(reg, nav) or (getattr(reg, "sin_sesion", None) or {}).get(nav)\n'
          '            or SIN_SESION.get(nav, ""))\n')

MUTACIONES += [
    # El segundo intento: con un tercero, sin él, también sin un error (desde el encargo 51, ante cualquier error), sin
    # reconocer el error tras la clave, volviendo a eBooking al final, dándola por iniciada sin mirar, o sin su aviso.
    dict(id="e50-msc-tercer-intento", pruebas=[MSC_DOS, MSC_CLAVE], viejo=INTENTOS, nuevo="MSC_INTENTOS = 3\n"),
    dict(id="e50-msc-sin-segundo-intento", pruebas=[MSC_DOS], viejo=INTENTOS, nuevo="MSC_INTENTOS = 1\n"),
    dict(id="e50-msc-reintenta-tras-cualquier-error", pruebas=[MSC_OTROS, MSC_CLAVE],
         viejo="        while desenlaces[-1] in MSC_ERRORES and intento < MSC_INTENTOS:\n",
         nuevo='        while desenlaces[-1] != "sesión" and intento < MSC_INTENTOS:\n'),
    dict(id="e50-msc-error-tras-la-clave-como-cualquiera", pruebas=[MSC_DOS], viejo=CLAVE_FIN,
         nuevo=CLAVE_FIN.replace("return MSC_ERROR_TRAS_LA_CLAVE", 'return "error"')),
    dict(id="e50-msc-vuelve-a-ebooking", pruebas=[MSC_DOS, MSC_OTROS], viejo=FINAL,
         nuevo=('    if desenlaces[-1] != "sesión":\n        page.goto(MSC_EBOOKING, wait_until="domcontentloaded")\n'
                + FINAL)),
    dict(id="e50-msc-sin-mirar-la-sesion", pruebas=[MSC_DOS],
         viejo='    if desenlaces[-1] == "sesión":\n        reg.paso("Sesión iniciada.")\n',
         nuevo='    if True:\n        reg.paso("Sesión iniciada.")\n'),
    dict(id="e50-msc-segundo-sin-aviso", pruebas=[MSC_DOS],
         viejo='            reg.paso(f"⚠ MSC dio un error {desenlaces[-1]}. Hago un solo intento más',
         nuevo='            reg.info(f"⚠ MSC dio un error {desenlaces[-1]}. Hago un solo intento más'),
    # Cómo termina: sin el motivo del segundo intento, con el motivo de un login anterior, o sin decir que el segundo
    # falló (el aviso del error antes de la clave, sin reintento, salió en el encargo 51).
    dict(id="e50-msc-segundo-sin-el-motivo", pruebas=[MSC_DOS],
         viejo='        reg.sin_sesion["msc"] = _msc_motivo_tras_dos(*desenlaces[:2])\n', nuevo="        pass\n"),
    dict(id="e50-msc-motivo-viejo-queda", pruebas=[MSC_DOS],
         viejo='    vars(reg).setdefault("sin_sesion", {}).pop("msc", None)\n',
         nuevo='    vars(reg).setdefault("sin_sesion", {})\n'),
    dict(id="e50-msc-segundo-fallido-sin-aviso", pruebas=[MSC_DOS],
         viejo='        reg.paso("⚠ El segundo intento de inicio de sesión de MSC tampoco dejó la sesión;',
         nuevo='        reg.info("⚠ El segundo intento de inicio de sesión de MSC tampoco dejó la sesión;'),
    # Las capturas del segundo intento con los nombres del primero, que las pisan.
    dict(id="e50-msc-sufijo-igual", pruebas=[MSC_DOS],
         viejo='    return "" if intento == 1 else f"_{intento}"\n', nuevo='    return ""\n'),
    # La portada con el error: sin mirarlo (escribe el usuario en la página de error) o sin su evidencia.
    dict(id="e50-msc-portada-sin-mirar-el-error", pruebas=[MSC_OTROS],
         viejo='    if _msc_error(page):\n        reg.paso("⚠ MSC mostró una página de error al abrir su portada;',
         nuevo='    if False:\n        reg.paso("⚠ MSC mostró una página de error al abrir su portada;'),
    dict(id="e50-msc-portada-sin-evidencia", pruebas=[MSC_OTROS],
         viejo=('        _msc_evidencia_del_error(page, reg, escucha, f"msc_error_portada{_msc_sufijo(intento)}", '
                'creds)\n'), nuevo=""),
    # La evidencia de cada error: sin la de después de la clave, sin la de después de la recarga; sin la línea de la
    # respuesta, sin la dirección, sin la captura, sin el HTML, o con el HTML que trae el usuario.
    dict(id="e50-msc-clave-sin-evidencia", pruebas=[MSC_DOS, MSC_EVID], viejo=CLAVE_FIN,
         nuevo="    return MSC_ERROR_TRAS_LA_CLAVE\n"),
    dict(id="e50-msc-recarga-sin-evidencia-tras-recargar", pruebas=[MSC_OTROS, MSC_REC],
         viejo='        _msc_evidencia_del_error(page, reg, escucha, f"msc_error_recarga{suf}", creds)\n', nuevo=""),
    dict(id="e50-msc-evidencia-sin-respuesta", pruebas=[MSC_EVID],
         viejo="    reg.info(_msc_respuesta_del_error(escucha))\n", nuevo=""),
    dict(id="e50-msc-evidencia-sin-url", pruebas=[MSC_EVID],
         viejo="    reg.info(_msc_respuesta_del_error(escucha))\n    reg.url(page)\n",
         nuevo="    reg.info(_msc_respuesta_del_error(escucha))\n"),
    dict(id="e50-msc-evidencia-sin-captura", pruebas=[MSC_EVID],
         viejo="    png = reg.captura(page, nombre)\n", nuevo="    png = False\n"),
    dict(id="e50-msc-evidencia-sin-html", pruebas=[MSC_EVID], viejo=HTML_EVID, nuevo="    guardados, total = 0, 1\n"),
    dict(id="e50-msc-evidencia-con-el-usuario", pruebas=[MSC_EVID], viejo=HTML_EVID,
         nuevo=HTML_EVID.replace("sin=_textos_de_la_cuenta(creds))", "sin=())")),
    # La escucha: sin dejar de escuchar al terminar, sin quitar a sus oyentes, con cualquier marco o tipo de petición,
    # sin las fallas de red, o guardando solo una.
    dict(id="e50-msc-escucha-sin-quitar", pruebas=[MSC_EVID], viejo='        escucha["quitar"]()\n',
         nuevo="        pass\n"),
    dict(id="e50-msc-quitar-no-quita", pruebas=[MSC_RESP, MSC_EVID],
         viejo="                page.remove_listener(evento, oyente)\n", nuevo="                pass\n"),
    dict(id="e50-msc-escucha-cualquier-marco", pruebas=[MSC_RESP], viejo=DEL_MARCO,
         nuevo='            return peticion.resource_type == "document"\n'),
    dict(id="e50-msc-escucha-cualquier-tipo", pruebas=[MSC_RESP], viejo=DEL_MARCO,
         nuevo="            return peticion.frame == page.main_frame\n"),
    dict(id="e50-msc-escucha-sin-fallas", pruebas=[MSC_RESP, MSC_EVID],
         viejo='    oyentes = (("response", al_responder), ("requestfailed", al_fallar))\n',
         nuevo='    oyentes = (("response", al_responder),)\n'),
    dict(id="e50-msc-escucha-de-a-una", pruebas=[MSC_RESP], viejo="MSC_ESCUCHA = 20\n", nuevo="MSC_ESCUCHA = 1\n"),
    # La línea de la respuesta: la primera que falló, sin su falla de red, repitiendo lo ya dicho, o tomando cualquier
    # respuesta como fallida.
    dict(id="e50-msc-respuesta-la-primera", pruebas=[MSC_RESP],
         viejo="        r = (fallidas or respuestas)[-1]\n", nuevo="        r = (fallidas or respuestas)[0]\n"),
    dict(id="e50-msc-respuesta-sin-la-falla", pruebas=[MSC_RESP, MSC_EVID],
         viejo='        red = [q["falla"] for q in fallas if q["url"] == r["url"]][-1:]\n', nuevo="        red = []\n"),
    dict(id="e50-msc-respuesta-repite", pruebas=[MSC_RESP], viejo='    escucha["nuevas"] = 0\n', nuevo=""),
    dict(id="e50-msc-respuesta-sin-escucha", pruebas=[MSC_RESP],
         viejo="    escucha = {} if escucha is None else escucha\n", nuevo=""),
    dict(id="e50-msc-respuesta-toda-fallida", pruebas=[MSC_RESP],
         viejo='    fallidas = [v for v in respuestas if (v.get("estado") or 0) >= 400]\n',
         nuevo="    fallidas = list(respuestas)\n"),
    # Las cabeceras: el valor de todas, sin recortarlo, sin las de cookies en los nombres, o con el valor de una cookie
    # o de un identificador.
    dict(id="e50-msc-cabeceras-todos-los-valores", pruebas=[MSC_RESP, MSC_EVID], viejo=VALORES,
         nuevo=VALORES.replace(" if k in MSC_CABECERAS_CON_VALOR]", "]")),
    dict(id="e50-msc-cabeceras-sin-recortar", pruebas=[MSC_RESP], viejo=VALORES,
         nuevo=VALORES.replace("[:80]", "[:800]")),
    dict(id="e50-msc-cabeceras-sin-set-cookie", pruebas=[MSC_RESP, MSC_EVID],
         viejo='        cab, aviso = dict(respuesta.all_headers()), ""\n',
         nuevo='        cab, aviso = dict(respuesta.headers), ""\n'),
    dict(id="e50-msc-cabeceras-con-cookie", pruebas=[MSC_RESP, MSC_EVID], viejo=CON_VALOR,
         nuevo=CON_VALOR.replace('("server",', '("set-cookie", "server",')),
    dict(id="e50-msc-cabeceras-con-id", pruebas=[MSC_RESP], viejo=CON_VALOR,
         nuevo=CON_VALOR.replace('("server",', '("x-request-id", "server",')),
    # Las direcciones: enteras, con el usuario y la clave de la dirección, o sin decir que se quitó la consulta.
    dict(id="e50-msc-sin-consulta-entera", pruebas=[MSC_RESP, MSC_EVID], viejo=SIN_CONSULTA,
         nuevo="        limpia = str(url)\n"),
    dict(id="e50-msc-sin-consulta-con-usuario", pruebas=[MSC_RESP, URL_REG], viejo=SIN_CONSULTA,
         nuevo=('        limpia = (f"{s.scheme}://{s.netloc}{s.path}" if s.netloc\n'
                '                  else f"{s.scheme}:{s.path}" if s.scheme else s.path)\n')),
    dict(id="e50-msc-url-sin-decirlo", pruebas=[MSC_RESP, URL_REG], viejo=URL_LINEA, nuevo="    return limpia\n"),
    # El HTML sin el usuario ni la clave: sin la guarda, distinguiendo mayúsculas, sin avisarlo; y los textos de la
    # cuenta sin su forma codificada, con los cortos, o sin la clave.
    dict(id="e50-html-sin-guarda", pruebas=[MSC_HTML, MSC_EVID], viejo=GUARDA_HTML, nuevo="            if False:\n"),
    dict(id="e50-html-guarda-con-mayusculas", pruebas=[MSC_HTML], viejo=GUARDA_HTML,
         nuevo="            if sin and any(str(t) in texto for t in sin):\n"),
    dict(id="e50-html-guarda-sin-aviso", pruebas=[MSC_HTML],
         viejo="                reg.paso(f\"⚠ No guardé el HTML {'de la página'",
         nuevo="                reg.info(f\"⚠ No guardé el HTML {'de la página'"),
    dict(id="e50-textos-sin-codificar", pruebas=[MSC_HTML, MSC_EVID],
         viejo='            textos |= {valor, quote(valor, safe=""), quote(valor)}\n',
         nuevo="            textos |= {valor}\n"),
    dict(id="e50-textos-cortos", pruebas=[MSC_HTML], viejo="        if len(valor) >= 3:\n",
         nuevo="        if valor:\n"),
    dict(id="e50-textos-sin-la-clave", pruebas=[MSC_HTML], viejo='    for clave in ("usuario", "clave"):\n',
         nuevo='    for clave in ("usuario",):\n'),
    # El motivo de las filas sin la sesión: siempre el de SIN_SESION, en _motivo_sin_sesion, en el panel o en la
    # consola.
    dict(id="e50-motivo-sin-sesion-fijo", pruebas=[CO_MOTIVO, ER_MOTIVO, MSC_DOS], viejo=MOTIVO,
         nuevo='    return SIN_SESION.get(nav, "")\n'),
    dict(id="e50-panel-motivo-fijo", pruebas=[CO_MOTIVO],
         viejo='"estado": NO_ENVIADA, "detalle": _motivo_sin_sesion(reg, nav), "booking": "",\n',
         nuevo='"estado": NO_ENVIADA, "detalle": SIN_SESION[nav], "booking": "",\n'),
    dict(id="e50-panel-linea-motivo-fijo", pruebas=[CO_MOTIVO],
         viejo="reg.paso(f\"✗ fila {rsv['fila']}: {NO_ENVIADA} · {_motivo_sin_sesion(reg, nav)}\")\n",
         nuevo="reg.paso(f\"✗ fila {rsv['fila']}: {NO_ENVIADA} · {SIN_SESION[nav]}\")\n"),
    dict(id="e50-consola-motivo-fijo", pruebas=[ER_MOTIVO],
         viejo="                anotar(i, rsv, NO_ENVIADA, _motivo_sin_sesion(reg, naviera_clave))\n",
         nuevo="                anotar(i, rsv, NO_ENVIADA, SIN_SESION[naviera_clave])\n"),
    # COSCO: la traducción siempre, nunca, o por el texto y no por las palabras; sin el aviso, sin la nota, sin sumarla
    # al motivo, sin borrar la de otra reserva, o con el decorador por dentro de los cortes o sin él.
    dict(id="e50-cosco-traduccion-siempre", pruebas=[COSCO_TRAD], viejo=TRADUCCION, nuevo="    return otro\n"),
    dict(id="e50-cosco-traduccion-nunca", pruebas=[COSCO_TRAD], viejo=TRADUCCION, nuevo='    return ""\n'),
    dict(id="e50-cosco-traduccion-por-el-texto", pruebas=[COSCO_TRAD], viejo=TRADUCCION,
         nuevo='    return otro if otro and _cosco_puerto_de_la_celda(otro) != puerto else ""\n'),
    dict(id="e50-cosco-sin-aviso", pruebas=[COSCO_TRAD],
         viejo='        reg.paso(f"⚠ COSCO: el puerto de carga de la fila,',
         nuevo='        reg.info(f"⚠ COSCO: el puerto de carga de la fila,'),
    dict(id="e50-cosco-sin-nota", pruebas=[COSCO_TRAD],
         viejo='        reg.cosco_puerto = (f"puerto de carga:', nuevo='        _nota = (f"puerto de carga:'),
    dict(id="e50-cosco-decorador-no-suma", pruebas=[COSCO_TRAD],
         viejo='        return (estado, " · ".join(x for x in (detalle, nota) if x)) if nota else (estado, detalle)\n',
         nuevo="        return (estado, detalle)\n"),
    dict(id="e50-cosco-decorador-no-borra-antes", pruebas=[COSCO_TRAD],
         viejo='        vars(reg).pop("cosco_puerto", None)\n        try:\n', nuevo="        try:\n"),
    dict(id="e50-cosco-decorador-por-dentro", pruebas=[COSCO_TRAD, DECORADO], viejo=DECORADORES,
         nuevo=('@_con_la_nave_de_la_fila\n@_con_la_ruta_de_la_fila\n@_sin_clic_a_ciegas("cosco")\n'
                '@_con_el_puerto_de_cosco\n')),
    dict(id="e50-cosco-sin-decorador", pruebas=[COSCO_TRAD, DECORADO], viejo=DECORADORES,
         nuevo='@_con_la_nave_de_la_fila\n@_con_la_ruta_de_la_fila\n@_sin_clic_a_ciegas("cosco")\n'),
]

# --- Encargo 51: cada corrida dice al empezar con qué candado corre y por cuál llave, y es_modo_emision sale de esas
# mismas llaves; un lanzador nunca se conecta a un panel abierto en otro modo: avisa y no corre; el login de MSC hace
# un solo intento más ante cualquier error que no se resuelva; y la línea «URL:» va sin su consulta en las seis
# navieras (decisiones de Marcelo, CICLO-modo-y-lanzadores.md) ---
MODO = "test_modo.TestModoDeCadaCorrida."
MODO_SALE = MODO + "test_el_candado_sale_de_las_llaves"
MODO_LLAVES = MODO + "test_cada_llave_dicha_y_el_mismo_candado"
MODO_PRIMERA = MODO + "test_sin_todas_se_detiene_en_la_primera"
MODO_LINEA = MODO + "test_la_linea_de_cada_modo"
WEB_CANDADO = "test_web.TestPanelCorridas.test_dice_su_candado_al_empezar"
CO_CANDADO = "test_consola.TestEjecutarReservas.test_dice_su_candado_al_empezar"
LO_CANDADO = "test_consola.TestEjecutarLogin.test_dice_su_candado_al_empezar"
ARR = "test_web.TestArranqueDelPanel."
OTRO_MODO = ARR + "test_panel_en_otro_modo_avisa_y_no_corre"
SIN_MODO = ARR + "test_panel_que_no_dice_su_modo_avisa_y_no_corre"
MISMO_MODO = ARR + "test_mismo_modo_de_emision_cede_como_antes"
VENTANA = ARR + "test_el_aviso_va_a_una_ventana"
PREVIAS = [ARR + "test_instancia_previa_ociosa_se_apaga", ARR + "test_instancia_previa_ocupada_no_se_toca"]
URL_TODAS = "test_consola.TestUtilitarios.test_toda_linea_url_va_sin_consulta"
SALE = "    return bool(_llaves_abiertas())\n"
CON_TODAS = "    llaves = _llaves_abiertas(todas=True)\n"
OTRO = "    if modo is not propio:\n"
AVISA = "        _avisar_al_lanzar(_otro_modo(puerto, estado, modo, propio))\n"
PROPIO = "    propio = es_modo_emision()          # el modo de este lanzador\n"
TRAS_NEXT = '        return MSC_ERROR_TRAS_EL_NEXT if tras_el_error and paso != "sesión" else paso\n'
ERRORES = "MSC_ERRORES = (MSC_ERROR_EN_LA_PORTADA, MSC_ERROR_TRAS_EL_NEXT, MSC_ERROR_TRAS_LA_CLAVE)\n"
SEGUNDO = ('        como = f"otro error {segundo}" if segundo in MSC_ERRORES else "no llegó ni la sesión ni otro '
           'error"\n')
MOTIVO_DOS = '        reg.sin_sesion["msc"] = _msc_motivo_tras_dos(*desenlaces[:2])\n'
QUITADO = '    quitado = [que for que, hay in (("su consulta", s.query), ("su fragmento", s.fragment)) if hay]\n'

MUTACIONES += [
    # El candado sale de las llaves: mirándolas todas (avisaría de config.json con otra llave abierta), o con una
    # llave por su cuenta, fuera de _llaves_abiertas.
    dict(id="e51-candado-con-todas", pruebas=[MODO_SALE, MODO_PRIMERA], viejo=SALE,
         nuevo="    return bool(_llaves_abiertas(todas=True))\n"),
    dict(id="e51-candado-con-otra-llave", pruebas=[MODO_SALE], viejo=SALE,
         nuevo='    return bool(_llaves_abiertas()) or os.environ.get("AQUASHIELD_PRODUCCION") == "1"\n'),
    # Las llaves con todas: deteniéndose en la primera; cada una dicha de otro modo.
    dict(id="e51-llaves-entorno-se-detiene", pruebas=[MODO_LLAVES],
         viejo='AQUASHIELD_EMISION.py)")\n        if not todas:\n',
         nuevo='AQUASHIELD_EMISION.py)")\n        if True:\n'),
    dict(id="e51-llaves-argumento-se-detiene", pruebas=[MODO_LLAVES],
         viejo='del programa")\n        if not todas:\n', nuevo='del programa")\n        if True:\n'),
    dict(id="e51-llave-entorno-sin-valor", pruebas=[MODO_LLAVES, MODO_PRIMERA],
         viejo='f"la variable AQUASHIELD_EMITIR={entorno.strip()} (la que pone',
         nuevo='f"la variable AQUASHIELD_EMITIR (la que pone'),
    dict(id="e51-llave-argumento-el-ultimo", pruebas=[MODO_LLAVES], viejo="«{argumentos[0]}»",
         nuevo="«{argumentos[-1]}»"),
    dict(id="e51-llave-config-sin-decir-cual", pruebas=[MODO_LLAVES],
         viejo='abiertas.append("config.json → opciones → emitir_reservas: true")',
         nuevo='abiertas.append("config.json")'),
    # La línea de cada corrida: sin mirar todas las llaves, siempre en prueba, con las llaves de otro modo, con otro
    # texto, o sin ella en la web, en la consola o en el login.
    dict(id="e51-anotar-sin-todas", pruebas=[MODO_LINEA, WEB_CANDADO, CO_CANDADO], viejo=CON_TODAS,
         nuevo="    llaves = _llaves_abiertas()\n"),
    dict(id="e51-anotar-siempre-prueba", pruebas=[MODO_LINEA, WEB_CANDADO, CO_CANDADO],
         viejo='    if llaves:\n        reg.paso(f"🔴 Candado', nuevo='    if False:\n        reg.paso(f"🔴 Candado'),
    dict(id="e51-anotar-llaves-con-coma", pruebas=[MODO_LINEA, WEB_CANDADO],
         viejo="por {' y '.join(llaves)}.", nuevo="por {', '.join(llaves)}."),
    dict(id="e51-anotar-prueba-otro-texto", pruebas=[MODO_LINEA, WEB_CANDADO, CO_CANDADO, LO_CANDADO],
         viejo='"🛡️ Candado de emisión cerrado: modo prueba, sin ninguna',
         nuevo='"🛡️ Candado de emisión cerrado: sin ninguna'),
    dict(id="e51-anotar-no-en-la-web", pruebas=[WEB_CANDADO],
         viejo='reserva(s)")\n        _anotar_candado(reg)\n', nuevo='reserva(s)")\n'),
    dict(id="e51-anotar-no-en-la-consola", pruebas=[CO_CANDADO],
         viejo='usuario={usuario}")\n    _anotar_candado(reg)\n', nuevo='usuario={usuario}")\n'),
    dict(id="e51-anotar-no-en-el-login", pruebas=[LO_CANDADO],
         viejo="navieras={','.join(navieras)}\")\n    _anotar_candado(reg)\n",
         nuevo="navieras={','.join(navieras)}\")\n"),
    # El lanzador: sin mirar el modo, siguiendo sin saberlo, con su modo fijo, rechazando el mismo modo de emisión,
    # avisando y siguiendo, o sin avisar.
    dict(id="e51-lanzador-no-mira-el-modo", pruebas=[OTRO_MODO, SIN_MODO], viejo=OTRO, nuevo="    if False:\n"),
    dict(id="e51-lanzador-sigue-sin-saber-el-modo", pruebas=[SIN_MODO], viejo=OTRO,
         nuevo="    if modo is not None and modo is not propio:\n"),
    dict(id="e51-lanzador-rechaza-el-mismo-de-emision", pruebas=[MISMO_MODO], viejo=OTRO,
         nuevo="    if modo or modo is not propio:\n"),
    dict(id="e51-lanzador-siempre-de-prueba", pruebas=[OTRO_MODO, MISMO_MODO],
         viejo=PROPIO, nuevo="    propio = False\n"),
    dict(id="e51-lanzador-siempre-de-emision", pruebas=[OTRO_MODO] + PREVIAS,
         viejo=PROPIO, nuevo="    propio = True\n"),
    dict(id="e51-lanzador-avisa-y-sigue", pruebas=[OTRO_MODO, SIN_MODO], viejo=AVISA + "        return True\n",
         nuevo=AVISA),
    dict(id="e51-lanzador-no-avisa", pruebas=[OTRO_MODO, SIN_MODO], viejo=AVISA, nuevo="        pass\n"),
    # El modo del panel abierto: sin preguntarlo, o aceptando lo que diga aunque no sea true ni false.
    dict(id="e51-panel-sin-preguntar-el-modo", pruebas=[OTRO_MODO, MISMO_MODO] + PREVIAS,
         viejo='            modo = _json.loads(resp.read().decode("utf-8")).get("modo_emision")\n',
         nuevo="            modo = None\n"),
    dict(id="e51-panel-acepta-cualquier-modo", pruebas=[SIN_MODO],
         viejo="    return estado, (modo if isinstance(modo, bool) else None)\n", nuevo="    return estado, modo\n"),
    # El aviso: sin decir que el panel está armando reservas, sin decir en qué modo está, sin la ventana o sin la
    # consola.
    dict(id="e51-aviso-sin-esperar-la-corrida", pruebas=[OTRO_MODO],
         viejo='            if estado.get("corriendo") else f"{cerrar[0].upper()}',
         nuevo='            if False else f"{cerrar[0].upper()}'),
    dict(id="e51-aviso-sin-el-modo", pruebas=[OTRO_MODO],
         viejo='    cual = f"en modo {nombre[modo]}" if modo is not None else "y no pude saber en qué modo está"\n',
         nuevo='    cual = "y no pude saber en qué modo está"\n'),
    dict(id="e51-aviso-sin-ventana", pruebas=[VENTANA], viejo='        mb.showwarning("AQUASHIELD", texto)\n',
         nuevo="        pass\n"),
    dict(id="e51-aviso-sin-consola", pruebas=[VENTANA],
         viejo="        print(texto, flush=True)\n    except Exception:\n        pass\n    try:\n"
               "        import tkinter.messagebox as mb\n",
         nuevo=("        pass\n    except Exception:\n        pass\n    try:\n"
                "        import tkinter.messagebox as mb\n")),
    # MSC, un solo camino: sin el error del «Next» que la recarga no arregla, o dándolo aunque llegue la sesión;
    # la portada sin reintento; MSC_ERRORES sin uno de los tres; la clave dos veces en un intento.
    dict(id="e51-msc-next-sin-reintento", pruebas=[MSC_OTROS, MSC_CLAVE, MSC_REC], viejo=TRAS_NEXT,
         nuevo="        return paso\n"),
    dict(id="e51-msc-next-aunque-llegue-la-sesion", pruebas=[MSC_REC, MSC_CLAVE], viejo=TRAS_NEXT,
         nuevo="        return MSC_ERROR_TRAS_EL_NEXT if tras_el_error else paso\n"),
    dict(id="e51-msc-portada-sin-reintento", pruebas=[MSC_OTROS, MSC_CLAVE],
         viejo="        return MSC_ERROR_EN_LA_PORTADA\n", nuevo='        return "error"\n'),
    dict(id="e51-msc-errores-sin-la-clave", pruebas=[MSC_DOS, MSC_CLAVE], viejo=ERRORES,
         nuevo="MSC_ERRORES = (MSC_ERROR_EN_LA_PORTADA, MSC_ERROR_TRAS_EL_NEXT)\n"),
    dict(id="e51-msc-errores-sin-el-next", pruebas=[MSC_OTROS, MSC_CLAVE, MSC_REC], viejo=ERRORES,
         nuevo="MSC_ERRORES = (MSC_ERROR_EN_LA_PORTADA, MSC_ERROR_TRAS_LA_CLAVE)\n"),
    dict(id="e51-msc-errores-sin-la-portada", pruebas=[MSC_OTROS, MSC_CLAVE], viejo=ERRORES,
         nuevo="MSC_ERRORES = (MSC_ERROR_TRAS_EL_NEXT, MSC_ERROR_TRAS_LA_CLAVE)\n"),
    dict(id="e51-msc-clave-dos-veces-en-un-intento", pruebas=[MSC_CLAVE],
         viejo='    rellenar(page, "input[type=password]", creds["clave"], 12000, reg)\n',
         nuevo=('    rellenar(page, "input[type=password]", creds["clave"], 12000, reg)\n'
                '    rellenar(page, "input[type=password]", creds["clave"], 12000, reg)\n')),
    # El aviso y el motivo: sin decir el error, con el segundo siempre sin error, con el primero fijo, al revés, o con
    # otro texto.
    dict(id="e51-msc-aviso-sin-el-error", pruebas=[MSC_DOS, MSC_OTROS],
         viejo='reg.paso(f"⚠ MSC dio un error {desenlaces[-1]}. Hago', nuevo='reg.paso(f"⚠ MSC dio un error. Hago'),
    dict(id="e51-msc-motivo-segundo-sin-error", pruebas=[MSC_DOS, MSC_OTROS, MSC_CLAVE], viejo=SEGUNDO,
         nuevo='        como = "no llegó ni la sesión ni otro error"\n'),
    dict(id="e51-msc-motivo-primero-fijo", pruebas=[MSC_OTROS, MSC_CLAVE],
         viejo="format(primero=primero, segundo=como)", nuevo="format(primero=MSC_ERROR_TRAS_LA_CLAVE, segundo=como)"),
    dict(id="e51-msc-motivo-al-reves", pruebas=[MSC_DOS, MSC_CLAVE], viejo=MOTIVO_DOS,
         nuevo='        reg.sin_sesion["msc"] = _msc_motivo_tras_dos(*desenlaces[1::-1])\n'),
    dict(id="e51-msc-motivo-otro-texto", pruebas=[MSC_DOS, MSC_OTROS],
         viejo='"no quedó iniciada la sesión de MSC: el portal dio un error {primero}, y el único intento "',
         nuevo='"no quedó iniciada la sesión de MSC: el portal dio un error ({primero}), y el único intento "'),
    # La dirección: entera en Registro.url o en el avance de MAERSK; con el fragmento, con «//» sin servidor, sin
    # decir que quitó el fragmento, o entera si no la puede leer.
    dict(id="e51-url-registro-entera", pruebas=[URL_REG, URL_TODAS, MSC_RESP],
         viejo='        try: self._emit("    URL: " + _sin_consulta(page.url, decirlo=True))\n',
         nuevo='        try: self._emit("    URL: " + page.url)\n'),
    dict(id="e51-url-maersk-entera", pruebas=[URL_TODAS, URL_REG],
         viejo='reg.info(f"avance detectado por URL: {_sin_consulta(u, decirlo=True)} (',
         nuevo='reg.info(f"avance detectado por URL: {u} ('),
    dict(id="e51-sin-consulta-con-fragmento", pruebas=[URL_REG], viejo=URL_LINEA,
         nuevo=('    return limpia + (f"#{s.fragment}" if s.fragment else "") + (f" (sin {\' ni \'.join(quitado)})" '
                'if decirlo and quitado else "")\n')),
    dict(id="e51-sin-consulta-barras-sin-servidor", pruebas=[URL_REG],
         viejo='                  else f"{s.scheme}:{s.path}" if s.scheme else s.path)\n',
         nuevo='                  else f"{s.scheme}://{s.path}" if s.scheme else s.path)\n'),
    dict(id="e51-sin-consulta-no-dice-el-fragmento", pruebas=[URL_REG, MSC_RESP], viejo=QUITADO,
         nuevo='    quitado = [que for que, hay in (("su consulta", s.query),) if hay]\n'),
    dict(id="e51-sin-consulta-entera-si-no-la-lee", pruebas=[URL_REG],
         viejo='        return "(no pude leer la dirección)"\n', nuevo="        return str(url)\n"),
]

# --- Encargo 51, lo que encontró la revisión del subagente (en un clon, sobre cb3f1c3): el lanzador vuelve a preguntar,
# con más paciencia, antes de cerrar a quien no deja libre el puerto; el aviso de config.json, solo sin otra llave
# abierta; ninguna dirección con su consulta a un mensaje (el paso de ONE); el motivo de MSC si el segundo intento se
# corta; y las direcciones IPv6 ---
LENTO = ARR + "test_panel_lento_del_otro_modo_no_se_cierra"
ONE_PASO = "test_consola.TestUtilitarios.test_one_paso_de_la_url"
SIN_CONSULTA_EN_MENSAJES = "test_consola.TestUtilitarios.test_ninguna_direccion_con_su_consulta_a_un_mensaje"
MSC_CORTADO = "test_clics.TestMsc.test_segundo_intento_cortado_deja_su_motivo"
PASO_ONE = '    return u.split("step=")[-1].split("&")[0][:30] if "step=" in u else _sin_consulta(u)\n'

MUTACIONES += [
    # La segunda pregunta del lanzador: sin ella, tan corta como la primera, o con la primera de plazo fijo.
    dict(id="e51-lanzador-sin-segunda-pregunta", pruebas=[LENTO],
         viejo="            visto = _panel_en(p, espera=PANEL_ESPERA_LARGA)\n",
         nuevo="            visto = None\n"),
    dict(id="e51-lanzador-segunda-pregunta-corta", pruebas=[LENTO], viejo="PANEL_ESPERA_LARGA = 5.0\n",
         nuevo="PANEL_ESPERA_LARGA = 1.0\n"),
    dict(id="e51-panel-espera-fija", pruebas=[LENTO],
         viejo='/api/estado", headers=marca),\n                                    timeout=espera) as resp:\n',
         nuevo='/api/estado", headers=marca),\n                                    timeout=1.0) as resp:\n'),
    dict(id="e51-aviso-corrida-en-curso-otro-texto", pruebas=[OTRO_MODO, LENTO],
         viejo='f"Ese panel tiene una corrida en curso: espera', nuevo='f"Ese panel está armando reservas: espera'),
    # Las llaves: avisar de config.json con otra llave abierta, o leerlo sin detenerse en la variable o el argumento.
    dict(id="e51-llaves-avisa-con-otra-llave", pruebas=[MODO_PRIMERA],
         viejo="        elif valor is not False and not abiertas:\n", nuevo="        elif valor is not False:\n"),
    dict(id="e51-llaves-entorno-no-se-detiene", pruebas=[MODO_PRIMERA],
         viejo='AQUASHIELD_EMISION.py)")\n        if not todas:\n',
         nuevo='AQUASHIELD_EMISION.py)")\n        if False:\n'),
    dict(id="e51-llaves-argumento-no-se-detiene", pruebas=[MODO_PRIMERA],
         viejo='del programa")\n        if not todas:\n', nuevo='del programa")\n        if False:\n'),
    # ONE: el paso con la dirección entera o con otro parámetro; y la dirección entera en reservar_one o en
    # _one_esperar_paso.
    dict(id="e51-one-paso-con-la-consulta", pruebas=[ONE_PASO], viejo=PASO_ONE,
         nuevo='    return u.split("step=")[-1].split("&")[0][:30] if "step=" in u else u\n'),
    dict(id="e51-one-paso-con-otro-parametro", pruebas=[ONE_PASO], viejo=PASO_ONE,
         nuevo='    return u.split("step=")[-1][:30] if "step=" in u else _sin_consulta(u)\n'),
    dict(id="e51-one-revisar-direccion-entera", pruebas=[SIN_CONSULTA_EN_MENSAJES],
         viejo='        actual = _one_paso_de_la_url(page.url)\n        reg.paso(f"NO se completó el flujo',
         nuevo='        actual = page.url\n        reg.paso(f"NO se completó el flujo'),
    dict(id="e51-one-esperar-direccion-entera", pruebas=[SIN_CONSULTA_EN_MENSAJES],
         viejo='        actual = _one_paso_de_la_url(page.url)\n    except Exception:\n',
         nuevo='        actual = page.url\n    except Exception:\n'),
    # IPv6 sin sus corchetes.
    dict(id="e51-sin-consulta-ipv6-sin-corchetes", pruebas=[URL_REG], viejo='            servidor = f"[{servidor}]"\n',
         nuevo="            pass\n"),
    # MSC: sin el motivo antes del segundo intento, o con el segundo cortado dicho como si no llegara nada.
    dict(id="e51-msc-cortado-sin-motivo", pruebas=[MSC_CORTADO],
         viejo='            reg.sin_sesion["msc"] = _msc_motivo_tras_dos(desenlaces[0], None)\n',
         nuevo="            pass\n"),
    dict(id="e51-msc-cortado-como-sin-nada", pruebas=[MSC_CORTADO],
         viejo='    if segundo is None:\n        como = "se cortó antes de terminar"\n',
         nuevo='    if False:\n        como = "se cortó antes de terminar"\n'),
]

# --- Encargo 52: el lanzador no cierra a quien tiene su puerto y no contesta como AQUASHIELD, y prueba el siguiente,
# con los paneles de AQUASHIELD tratados como hasta hoy en cada puerto; y antes de armar, el panel vuelve a leer su modo
# y no corre si no es el que muestra la página (decisiones de Marcelo, CICLO-puerto-libre-y-modo-al-armar.md). Salen
# puerto-mata-sin-forzar y puerto-no-busca-al-ocupante: el lanzador ya no llama a taskkill ---
NO_CIERRA = ARR + "test_no_cierra_al_que_ocupa_el_puerto"
CONTESTA = ARR + "test_otro_programa_que_contesta_no_se_cierra"
AUNQUE = ARR + "test_no_usa_el_puerto_de_quien_contesta_aunque_se_pueda_enlazar"
SE_SUELTA = ARR + "test_puerto_que_se_suelta_mientras_pregunta"
QUIEN = ARR + "test_panel_en_dice_quien_contesta"
SIGUIENTE = ARR + "test_panel_en_el_puerto_siguiente_como_hoy"
TARDA = ARR + "test_ocioso_que_tarda_en_soltar_el_puerto"
NO_SUELTA = ARR + "test_ocioso_que_no_suelta_el_puerto_no_se_cierra"
ARMA = "test_web.TestPanelCorridas.test_no_arma_si_la_pagina_muestra_otro_modo"
PAGINA = "test_envio.TestLecturaDelPanel.test_el_panel_vuelve_a_leer_su_modo_antes_de_armar"
BOTON = "test_envio.TestLecturaDelPanel.test_armar_pregunta_el_modo_y_lo_manda"
CIERRA = '__import__("subprocess").call("taskkill /F /PID 424242", shell=True)\n'
SALTA = ('        _avisar_en_pantalla_y_log(f"El puerto {p} lo tiene otro programa, que no contesta como '
         'AQUASHIELD: no lo "\n                                  f"cerré.")\n')
OCIOSO = ('            _avisar_en_pantalla_y_log(f"El panel de AQUASHIELD del puerto {p} no lo soltó en '
          '{PANEL_ESPERA_LARGA:g} s, "\n                                      f"después de pedirle que se apagara: '
          'no lo cerré.")\n')
GUARDA = ('                    if d.get("modo") is not modo:\n                        return self._json({"error": '
          '_modo_de_la_pagina(d.get("modo"), modo)}, 409)\n')
SIN_MODO_EN_EL_PEDIDO = '                    if d.get("modo") is not modo:\n'
OTRO_PROGRAMA = "    except (urllib.error.HTTPError, http.client.HTTPException):\n"
NO_ES_PANEL = '    if not isinstance(estado, dict) or "corriendo" not in estado:\n        return '
SIN_JSON = '        estado = _json.loads(cuerpo.decode("utf-8"))\n    except Exception:\n        return '
COMPARA = '  if (typeof modo === "boolean" && modo === MODO_PAGINA) return true;\n'

MUTACIONES += [
    # El lanzador: cierra a quien tiene el puerto, no lo dice, enlaza el puerto de quien contestó, prueba un solo
    # puerto, no vuelve a probar el que se soltó mientras preguntaba, salta al panel del puerto siguiente, o no espera
    # al ocioso que tarda en soltar el suyo, no dice que sigue o lo cierra.
    dict(id="e52-lanzador-cierra-al-ajeno", pruebas=[NO_CIERRA, CONTESTA], viejo=SALTA,
         nuevo=SALTA + "        " + CIERRA),
    dict(id="e52-lanzador-no-dice-que-salta", pruebas=[NO_CIERRA, CONTESTA], viejo=SALTA, nuevo="        pass\n"),
    dict(id="e52-lanzador-enlaza-si-contesta", pruebas=[AUNQUE],
         viejo="        elif visto is False:\n            ajenos.append(p)\n",
         nuevo="        elif visto is False:\n            libres.append(p)\n"),
    dict(id="e52-lanzador-un-solo-puerto", pruebas=[NO_CIERRA, CONTESTA, AUNQUE], viejo="PUERTOS_DEL_PANEL = 4\n",
         nuevo="PUERTOS_DEL_PANEL = 1\n"),
    dict(id="e52-lanzador-no-vuelve-a-probar", pruebas=[SE_SUELTA],
         viejo="            if visto is None and not _puerto_se_suelta(p):\n                visto = False\n",
         nuevo="            if visto is None:\n                visto = False\n"),
    dict(id="e52-lanzador-salta-al-panel-del-siguiente", pruebas=[SIGUIENTE],
         viejo="        if _ceder_al_previo(p, visto, propio, abrir):\n            return True, None\n",
         nuevo="        if False:\n            return True, None\n"),
    dict(id="e52-lanzador-no-espera-al-ocioso", pruebas=[TARDA],
         viejo="        srv = _enlazar(p, espera=PANEL_ESPERA_LARGA)", nuevo="        srv = _enlazar(p)"),
    dict(id="e52-lanzador-no-dice-que-el-ocioso-sigue", pruebas=[NO_SUELTA], viejo=OCIOSO,
         nuevo="            pass\n"),
    dict(id="e52-lanzador-cierra-al-ocioso", pruebas=[NO_SUELTA], viejo=OCIOSO,
         nuevo="            " + CIERRA + OCIOSO),
    # _panel_en: a quien contesta con otro código, cierra sin contestar, no manda JSON o no dice «corriendo», como a
    # nadie.
    dict(id="e52-panel-en-error-http-como-nadie", pruebas=[QUIEN, CONTESTA],
         viejo=OTRO_PROGRAMA + "        return False\n", nuevo=OTRO_PROGRAMA + "        return None\n"),
    dict(id="e52-panel-en-cierre-como-nadie", pruebas=[QUIEN], viejo=OTRO_PROGRAMA,
         nuevo="    except urllib.error.HTTPError:\n"),
    dict(id="e52-panel-en-sin-json-como-nadie", pruebas=[QUIEN], viejo=SIN_JSON + "False\n", nuevo=SIN_JSON + "None\n"),
    dict(id="e52-panel-en-sin-corriendo-como-nadie", pruebas=[QUIEN], viejo=NO_ES_PANEL + "False\n",
         nuevo=NO_ES_PANEL + "None\n"),
    # El servidor: arma sin mirar el modo, sin que la página lo diga, comparando a medias, con su modo fijo, o con el
    # aviso sin el modo que muestra la página.
    dict(id="e52-correr-sin-mirar-el-modo", pruebas=[ARMA], viejo=GUARDA, nuevo=""),
    dict(id="e52-correr-acepta-sin-modo", pruebas=[ARMA], viejo=SIN_MODO_EN_EL_PEDIDO,
         nuevo='                    if d.get("modo") is not None and d.get("modo") is not modo:\n'),
    dict(id="e52-correr-compara-a-medias", pruebas=[ARMA], viejo=SIN_MODO_EN_EL_PEDIDO,
         nuevo='                    if d.get("modo") != modo:\n'),
    dict(id="e52-correr-con-su-modo-fijo", pruebas=[ARMA],
         viejo="                    modo = bool(_llaves_abiertas())\n", nuevo="                    modo = False\n"),
    dict(id="e52-correr-aviso-sin-el-modo-de-la-pagina", pruebas=[ARMA],
         viejo='    muestra = (f"muestra el modo {NOMBRE_DEL_MODO[pagina]}" if isinstance(pagina, bool)\n',
         nuevo='    muestra = ("no dice qué modo muestra" if isinstance(pagina, bool)\n'),
    # La página: arma sin preguntar el modo, acepta cualquiera, compara a medias, no lo manda, no guarda el que pinta,
    # pinta con otro, cambia los nombres o no pide recargarla.
    dict(id="e52-armar-sin-preguntar-el-modo", pruebas=[BOTON], viejo="  if (!(await mismoModo())) return;\n",
         nuevo=""),
    dict(id="e52-pagina-acepta-cualquier-modo", pruebas=[PAGINA], viejo=COMPARA, nuevo="  return true;\n"),
    dict(id="e52-pagina-compara-a-medias", pruebas=[PAGINA], viejo=COMPARA,
         nuevo="  if (modo == MODO_PAGINA) return true;\n"),
    dict(id="e52-armar-sin-mandar-el-modo", pruebas=[BOTON], viejo="filas, modo: MODO_PAGINA })", nuevo="filas })"),
    dict(id="e52-pagina-sin-guardar-su-modo", pruebas=[BOTON], viejo="    MODO_PAGINA = Boolean(d.modo_emision);\n",
         nuevo=""),
    dict(id="e52-pagina-pinta-sin-su-modo", pruebas=[BOTON], viejo="      if (MODO_PAGINA) {",
         nuevo="      if (d.modo_emision) {"),
    dict(id="e52-pagina-aviso-con-los-modos-cambiados", pruebas=[PAGINA],
         viejo='  const nombre = { true: "EMISIÓN (reservas reales)", false: "prueba (sin emitir)" };\n',
         nuevo='  const nombre = { true: "prueba (sin emitir)", false: "EMISIÓN (reservas reales)" };\n'),
    dict(id="e52-pagina-sin-pedir-recargar", pruebas=[PAGINA], viejo='  estado("Recarga la página antes de armar");\n',
         nuevo=""),
    # Los nombres de los modos, otros en el programa que en la página.
    dict(id="e52-nombres-del-modo-otros", pruebas=[ARMA, OTRO_MODO, PAGINA],
         viejo='NOMBRE_DEL_MODO = {True: "EMISIÓN (reservas reales)", False: "prueba (sin emitir)"}\n',
         nuevo='NOMBRE_DEL_MODO = {True: "EMISIÓN", False: "prueba"}\n'),
]

# --- Encargo 53: el navegador se lanza con el sandbox de Chrome, desde un solo ayudante (_lanzar_navegador), que dice
# también en las reservas si cambia a Chromium; y el lanzador mira los cuatro puertos antes de tomar uno libre
# (decisiones de Marcelo, CICLO-bloqueo-cma-y-sandbox.md). Las del lanzador del 51 y el 52 que miraban su bucle quedan
# reescritas sobre el código nuevo, con sus mismas pruebas ---
NAV = "test_consola.TestUtilitarios."
UN_LANZADOR = NAV + "test_un_solo_lanzador_del_navegador"
SANDBOX = NAV + "test_navegador_con_el_sandbox_de_chrome"
WEB_CORRIDA = "test_web.TestPanelCorridas.test_corrida_de_una_hoja"
LOGIN_CONSOLA = "test_consola.TestEjecutarLogin.test_login_por_consola"
RESERVAS_CONSOLA = "test_consola.TestEjecutarReservas.test_reservas_por_consola"
CUATRO = ARR + "test_mira_los_cuatro_puertos_con_el_base_libre"
LENTO_OTRO = ARR + "test_panel_lento_en_otro_puerto_con_el_base_libre"
A_LA_VEZ = ARR + "test_pregunta_a_los_cuatro_a_la_vez"
DESPUES = ARR + "test_otro_programa_despues_del_puerto_usado_no_se_avisa"
DOS = ARR + "test_con_dos_paneles_decide_el_primero"
SE_TOMA = ARR + "test_puerto_que_se_toma_mientras_mira_los_demas"
TOMADOS = ARR + "test_con_los_cuatro_tomados_avisa_de_todos"
OPCIONES = '                    ignore_default_args=["--enable-automation"], chromium_sandbox=True)\n'
CAMBIO = "        reg.info(f\"no pude usar '{canal}' ({e}); uso chromium de playwright\")\n"
DIRECTO = ("p.chromium.launch_persistent_context(channel=canal, user_data_dir=str({}), headless=headless, "
           "no_viewport=True, args=_args_chrome(), ignore_default_args=[\"--enable-automation\"])")
AVISOS = "    for p in sorted(q for q in ajenos if srv is None or q < srv.server_address[1]):\n"
SIN_PUERTO = ('    if srv is None:\n        raise RuntimeError(f"no encontré un puerto libre para AQUASHIELD cerca de '
              '{puerto}")\n')

MUTACIONES += [
    # El navegador: sin el sandbox o con el sandbox apagado; cambiando a Chromium sin decirlo o con el mismo canal; o
    # lanzado en una de las tres vías sin el ayudante.
    dict(id="e53-navegador-sin-sandbox", pruebas=[SANDBOX, WEB_CORRIDA, LOGIN_CONSOLA, RESERVAS_CONSOLA],
         viejo=OPCIONES, nuevo='                    ignore_default_args=["--enable-automation"])\n'),
    dict(id="e53-navegador-sandbox-apagado", pruebas=[SANDBOX, WEB_CORRIDA, LOGIN_CONSOLA, RESERVAS_CONSOLA],
         viejo=OPCIONES, nuevo=OPCIONES.replace("chromium_sandbox=True", "chromium_sandbox=False")),
    dict(id="e53-navegador-cambia-sin-decirlo", pruebas=[SANDBOX], viejo=CAMBIO, nuevo=""),
    dict(id="e53-navegador-respaldo-con-el-canal", pruebas=[SANDBOX],
         viejo="        ctx = p.chromium.launch_persistent_context(**opciones)\n",
         nuevo="        ctx = p.chromium.launch_persistent_context(channel=canal, **opciones)\n"),
    dict(id="e53-navegador-login-sin-el-ayudante", pruebas=[UN_LANZADOR, LOGIN_CONSOLA],
         viejo="        ctx = _lanzar_navegador(p, perfil_dir, headless, canal, reg)\n        if al_abrir:\n",
         nuevo="        ctx = " + DIRECTO.format("perfil_dir") + "\n        if al_abrir:\n"),
    dict(id="e53-navegador-consola-sin-el-ayudante", pruebas=[UN_LANZADOR, RESERVAS_CONSOLA],
         viejo="        ctx = _lanzar_navegador(p, perfil_dir, headless, canal, reg)\n        # Traza",
         nuevo="        ctx = " + DIRECTO.format("perfil_dir") + "\n        # Traza"),
    dict(id="e53-navegador-web-sin-el-ayudante", pruebas=[UN_LANZADOR, WEB_CORRIDA],
         viejo="                ctx = _lanzar_navegador(p, perfil, headless, canal, reg)\n",
         nuevo="                ctx = " + DIRECTO.format("perfil") + "\n"),
    # El lanzador: toma el primer puerto libre sin mirar los demás, pregunta de a uno, le vuelve a preguntar solo al
    # base, da por libre un puerto tomado, toma otro después del relevo, avisa de todos los ajenos o de ninguno sin
    # puerto, sigue sin puerto, decide con el último panel, o no pregunta quién tomó el puerto que iba a usar.
    dict(id="e53-lanzador-toma-el-libre-sin-mirar", pruebas=[CUATRO, LENTO_OTRO, DOS],
         viejo="        if visto is None:\n            libres.append(p)\n",
         nuevo="        if visto is None:\n            libres.append(p)\n            break\n"),
    dict(id="e53-lanzador-pregunta-de-a-uno", pruebas=[A_LA_VEZ],
         viejo="        return dict(zip(puertos, pool.map(_panel_en, puertos)))\n",
         nuevo="        return {q: _panel_en(q) for q in puertos}\n"),
    dict(id="e53-lanzador-repregunta-solo-al-base", pruebas=[LENTO_OTRO],
         viejo="        if visto is None and not _puerto_libre(p):\n            visto = _panel_en(",
         nuevo="        if visto is None and p == puerto and not _puerto_libre(p):\n            visto = _panel_en("),
    dict(id="e53-lanzador-puerto-tomado-como-libre", pruebas=[NO_CIERRA, LENTO, LENTO_OTRO],
         viejo='            s.bind(("127.0.0.1", puerto))\n', nuevo='            s.bind(("127.0.0.1", 0))\n'),
    dict(id="e53-lanzador-toma-otro-despues-del-relevo", pruebas=[CUATRO],
         viejo="    for p in ([] if srv is not None else libres):\n", nuevo="    for p in libres:\n"),
    dict(id="e53-lanzador-avisa-de-todos-los-ajenos", pruebas=[DESPUES], viejo=AVISOS,
         nuevo="    for p in sorted(ajenos):\n"),
    dict(id="e53-lanzador-sin-puerto-no-avisa", pruebas=[TOMADOS], viejo=AVISOS,
         nuevo="    for p in sorted(q for q in ajenos if srv is not None and q < srv.server_address[1]):\n"),
    dict(id="e53-lanzador-sigue-sin-puerto", pruebas=[TOMADOS], viejo=SIN_PUERTO, nuevo=""),
    dict(id="e53-lanzador-decide-el-ultimo-panel", pruebas=[DOS],
         viejo="    for p in puertos:\n        visto = quien(p, vistos[p])\n",
         nuevo="    for p in reversed(puertos):\n        visto = quien(p, vistos[p])\n"),
    dict(id="e53-lanzador-no-pregunta-quien-lo-tomo", pruebas=[SE_TOMA],
         viejo="            visto = quien(p, None)\n", nuevo="            visto = False\n"),
]

# --- Encargo 54: CMA-CGM se detiene, sin reintentar ni recargar, si su portal restringe el acceso o su página no
# termina de cargar (decisión de Marcelo, CICLO-cma-acceso-restringido.md). ---
DD = "test_datadome.TestLoQueMuestraDataDome."
SD = "test_datadome.TestCmaSeDetiene."
LG = "test_datadome.TestLoginCma."
RS = "test_datadome.TestReservaCma."
RECONOCE = DD + "test_reconoce_cada_pagina_medida"
MEDIDO = DD + "test_lo_medido"
BLOQUEO_YA = SD + "test_bloqueo_se_detiene_enseguida"
SIN_FIN = SD + "test_verificacion_que_no_termina_se_detiene_al_plazo"
VACIA_PLAZO = SD + "test_pagina_vacia_se_detiene_al_plazo"
EVIDENCIA_CMA = SD + "test_evidencia_sin_las_credenciales_y_con_plazo"
PORTADA_MUDA = LG + "test_portada_que_no_responde_se_detiene"
PORTADA_BLOQUEADA = LG + "test_bloqueo_en_la_portada_no_intenta_entrar"
CLICK_BOOK = RS + "test_bloqueo_en_click_and_book_queda_no_enviada_y_no_sigue"
CO_CMA = CO + "test_cma_detenida_en_el_login_queda_no_enviada"
ER_CMA = ER + "test_cma_detenida_en_el_login_queda_no_enviada"
OTRAS_SIGUEN = CO + "test_cma_detenida_no_frena_a_las_otras"
SOLO_LOGIN_CMA = "test_consola.TestEjecutarLogin.test_login_que_se_detiene_en_cma_sigue"
CLASIFICA = ('    if de_datadome:\n        return "otra" if any(de_datadome) else "vacia"\n')
TRAE = '        if (partes.hostname or "").lower().endswith("captcha-delivery.com"):\n'
HTTP_ENTERO = '    return estado if isinstance(estado, int) and not isinstance(estado, bool) else None\n'
ROBOT_403 = '        if _cma_http(page) == 403:\n            return True\n'
HTML_CMA = ('    guardados, total, _ = _guardar_html_completo(page, reg, nombre, f"con CMA-CGM {como}",\n'
            '                                                 '
            'sin=_textos_de_la_cuenta(creds), plazo_ms=CMA_LECTURA_MS)\n')
CAPTURA_CON_PLAZO = ('            page.screenshot(path=str(ruta), full_page=completa or bool(pagina_entera),\n'
                     '                            **({"timeout": plazo_ms} if plazo_ms else {}))\n')
VUELTA = '        while que in ("verificacion", "vacia") and time.time() < fin:\n'
AL_PLAZO = '    if que in ("verificacion", "vacia"):\n        _cma_detener(page, reg, CMA_SIN_CARGAR.format(\n'
PRIMERO = ('    if _cma_sin_bloqueo_ni_espera(page, reg, creds) == "" and not _cma_es_robotcheck(page):\n'
           '        reg.paso("DataDome dejó pasar la página; sigo.")\n        return True\n')
ATAJA = ('        try:\n            return login(page, creds, reg, on_pausa=on_pausa)\n        except CmaDetenida:\n'
         '            return False\n')
PORTADA_GOTO = ('        page.goto("https://www.cma-cgm.com/", wait_until="domcontentloaded", '
                'timeout=CMA_ESPERA_PORTADA * 1000)\n')
SIN_CARGAR_PORTADA = ('    except PWTimeout:\n'
                      '        _cma_detener(page, reg, CMA_SIN_CARGAR.format(seg=CMA_ESPERA_PORTADA, '
                      'que="la portada no respondió"),\n')
DETENIDA_CMA = '    return (_naviera_detenida(reg, nav) or (getattr(reg, "sin_sesion", None) or {}).get(nav)\n'

MUTACIONES += [
    # Qué muestra DataDome: el bloqueo como deslizador, reconocido por «bloqueo» (que también trae el deslizador), sin
    # el deslizador, la verificación sin su marco o sin su texto, el marco sin texto como «otra» o con texto como vacío,
    # el 403 que no cuenta, otro servidor de DataDome, o el texto sin normalizar.
    dict(id="e54-datadome-bloqueo-como-deslizador", pruebas=[RECONOCE, BLOQUEO_YA],
         viejo='        return "bloqueo"\n', nuevo='        return "deslizador"\n'),
    dict(id="e54-datadome-por-bloqueo", pruebas=[RECONOCE, MEDIDO, SD + "test_deslizador_como_antes"],
         viejo='CMA_TEXTO_BLOQUEO = "restringido temporalmente"\n', nuevo='CMA_TEXTO_BLOQUEO = "bloqueo"\n'),
    dict(id="e54-datadome-sin-deslizador", pruebas=[RECONOCE],
         viejo='    if any(CMA_TEXTO_DESLIZADOR in t for t in textos):\n        return "deslizador"\n', nuevo=""),
    dict(id="e54-datadome-verificacion-sin-su-marco", pruebas=[RECONOCE],
         viejo='            verifica = verifica or partes.path.startswith("/interstitial")\n',
         nuevo="            pass\n"),
    dict(id="e54-datadome-verificacion-sin-su-texto", pruebas=[RECONOCE],
         viejo="    if verifica or any(CMA_TEXTO_VERIFICACION in t for t in textos):\n", nuevo="    if verifica:\n"),
    dict(id="e54-datadome-marco-sin-texto-como-otra", pruebas=[RECONOCE], viejo=CLASIFICA,
         nuevo='    if de_datadome:\n        return "otra"\n'),
    dict(id="e54-datadome-otra-como-vacia", pruebas=[RECONOCE, SD + "test_otra_pagina_de_datadome_va_al_operador"],
         viejo=CLASIFICA, nuevo='    if de_datadome:\n        return "vacia"\n'),
    dict(id="e54-datadome-403-no-cuenta", pruebas=[RECONOCE, VACIA_PLAZO],
         viejo='    return "vacia" if _cma_http(page) == 403 else ""\n', nuevo='    return ""\n'),
    dict(id="e54-datadome-otro-servidor", pruebas=[RECONOCE], viejo=TRAE,
         nuevo=TRAE.replace("captcha-delivery.com", "captcha-delivery.invalid")),
    dict(id="e54-datadome-sin-normalizar", pruebas=[RECONOCE],
         viejo='        texto = " ".join(str(_cma_leer(fr, _JS_CMA_TEXTO) or "").split()).lower()\n',
         nuevo='        texto = str(_cma_leer(fr, _JS_CMA_TEXTO) or "")\n'),
    # Las lecturas: sin plazo, con otro plazo, sin atajar el plazo vencido; el código HTTP que no es un entero.
    dict(id="e54-leer-sin-plazo", pruebas=[DD + "test_lee_solo_con_plazo", EVIDENCIA_CMA],
         viejo='    return alcance.locator(":root").evaluate(js, timeout=plazo_ms)\n',
         nuevo="    return alcance.evaluate(js)\n"),
    dict(id="e54-leer-otro-plazo", pruebas=[MEDIDO], viejo="CMA_LECTURA_MS = 1500\n", nuevo="CMA_LECTURA_MS = 15000\n"),
    dict(id="e54-leer-sin-atajar", pruebas=[RECONOCE, EVIDENCIA_CMA],
         viejo=("        return _evaluar_con_plazo(alcance, js, plazo_ms)\n    except Exception:\n"
                "        return None\n"),
         nuevo=("        return _evaluar_con_plazo(alcance, js, plazo_ms)\n    except ValueError:\n"
                "        return None\n")),
    dict(id="e54-http-cualquier-cosa", pruebas=[DD + "test_codigo_http_solo_entero"], viejo=HTTP_ENTERO,
         nuevo="    return estado\n"),
    dict(id="e54-http-verdadero", pruebas=[DD + "test_codigo_http_solo_entero"], viejo=HTTP_ENTERO,
         nuevo="    return estado if isinstance(estado, int) else None\n"),
    # El detector de antes: sin el 403, o también con el 200.
    dict(id="e54-robotcheck-sin-403", pruebas=[DD + "test_robotcheck_con_403_sin_leer_los_marcos"], viejo=ROBOT_403,
         nuevo=""),
    dict(id="e54-robotcheck-200-tambien",
         pruebas=[DD + "test_robotcheck_con_403_sin_leer_los_marcos", SD + "test_sin_datadome_sigue_sin_tocar_nada"],
         viejo=ROBOT_403, nuevo=ROBOT_403.replace("== 403", "in (200, 403)")),
    # La evidencia: el HTML sin plazo o con el de Playwright, que no lo tiene; la captura sin su plazo o con otro.
    dict(id="e54-html-sin-plazo", pruebas=[EVIDENCIA_CMA],
         viejo="                if plazo_ms:\n                    html = str((_evaluar_con_plazo(",
         nuevo="                if False:\n                    html = str((_evaluar_con_plazo("),
    dict(id="e54-html-con-content", pruebas=[EVIDENCIA_CMA],
         viejo=("                if plazo_ms:\n                    raise                  # sin el HTML de Playwright "
                "(content), que no tiene plazo\n"), nuevo=""),
    dict(id="e54-captura-sin-plazo", pruebas=[BLOQUEO_YA], viejo=CAPTURA_CON_PLAZO,
         nuevo="            page.screenshot(path=str(ruta), full_page=completa or bool(pagina_entera))\n"),
    dict(id="e54-captura-otro-plazo", pruebas=[MEDIDO], viejo="CMA_CAPTURA_MS = 5000\n",
         nuevo="CMA_CAPTURA_MS = 30000\n"),
    # La detención: sin el HTML, con las credenciales, sin la captura, sin el motivo en el Registro, sin detenerse,
    # o sin el aviso en pantalla.
    dict(id="e54-detener-sin-html", pruebas=[BLOQUEO_YA], viejo=HTML_CMA, nuevo="    guardados, total = 0, 1\n"),
    dict(id="e54-detener-con-las-credenciales", pruebas=[EVIDENCIA_CMA, PORTADA_BLOQUEADA, CLICK_BOOK], viejo=HTML_CMA,
         nuevo=HTML_CMA.replace("sin=_textos_de_la_cuenta(creds)", "sin=()")),
    dict(id="e54-detener-sin-captura", pruebas=[BLOQUEO_YA],
         viejo="    png = reg.captura(page, nombre, plazo_ms=CMA_CAPTURA_MS)\n", nuevo="    png = False\n"),
    dict(id="e54-detener-sin-motivo", pruebas=[BLOQUEO_YA, CLICK_BOOK, CO_CMA, ER_CMA],
         viejo='    vars(reg).setdefault("detenida", {})["cma"] = motivo\n',
         nuevo='    vars(reg).setdefault("detenida", {})\n'),
    dict(id="e54-detener-no-detiene", pruebas=[BLOQUEO_YA], viejo="    raise CmaDetenida(motivo)\n",
         nuevo="    return False\n"),
    dict(id="e54-detener-sin-aviso", pruebas=[BLOQUEO_YA, PORTADA_MUDA],
         viejo='    reg.paso(f"⛔ {causa[:1].upper()}{causa[1:]}. Me detengo sin reintentar ni recargar la página.")\n',
         nuevo='    reg.info(f"⛔ {causa[:1].upper()}{causa[1:]}. Me detengo sin reintentar ni recargar la página.")\n'),
    # La espera de la verificación o de la página vacía: sin esperar, el doble, sin detenerse al plazo, el bloqueo al
    # operador, otro plazo, sin su captura, o con los motivos cruzados.
    dict(id="e54-espera-sin-esperar",
         pruebas=[SD + "test_verificacion_que_termina_sigue",
                  SD + "test_verificacion_que_pasa_al_deslizador_lo_pide_al_operador", SIN_FIN],
         viejo=VUELTA, nuevo="        while False:\n"),
    dict(id="e54-espera-el-doble", pruebas=[SIN_FIN], viejo="        fin = time.time() + CMA_ESPERA_PORTADA\n",
         nuevo="        fin = time.time() + 2 * CMA_ESPERA_PORTADA\n"),
    dict(id="e54-espera-sin-detenerse-al-plazo", pruebas=[SIN_FIN, VACIA_PLAZO], viejo=AL_PLAZO,
         nuevo=AL_PLAZO.replace('if que in ("verificacion", "vacia"):', "if False:")),
    dict(id="e54-espera-bloqueo-al-operador", pruebas=[BLOQUEO_YA],
         viejo=('    if que == "bloqueo":\n        _cma_detener(page, reg, CMA_ACCESO_RESTRINGIDO, '
                '"cma_acceso_restringido", creds)\n    if que in'), nuevo="    if que in"),
    dict(id="e54-espera-otro-plazo", pruebas=[MEDIDO], viejo="CMA_ESPERA_PORTADA = 30\n",
         nuevo="CMA_ESPERA_PORTADA = 300\n"),
    dict(id="e54-espera-sin-captura", pruebas=[SIN_FIN],
         viejo='        reg.captura(page, "cma_verificacion", plazo_ms=CMA_CAPTURA_MS)\n', nuevo=""),
    dict(id="e54-espera-motivos-cruzados", pruebas=[SIN_FIN, VACIA_PLAZO],
         viejo='que="DataDome no terminó de verificar el navegador" if que == "verificacion"\n',
         nuevo='que="DataDome no terminó de verificar el navegador" if que == "vacia"\n'),
    # Antes de pedirle al operador que deslice: sin mirar qué muestra DataDome, sin volver a mirar con el detector de
    # antes, o sin el bloqueo mientras espera.
    dict(id="e54-desafio-sin-mirar-datadome", pruebas=[BLOQUEO_YA, SD + "test_verificacion_que_termina_sigue"],
         viejo=PRIMERO, nuevo=""),
    dict(id="e54-desafio-sin-volver-a-mirar", pruebas=[SD + "test_lo_que_solo_ve_el_detector_viejo_va_al_operador"],
         viejo=PRIMERO, nuevo=PRIMERO.replace(' and not _cma_es_robotcheck(page)', "")),
    # Reescrita en el encargo 56: el bloqueo en la espera del deslizador lo ve _cma_como_quedo, que mira también la
    # pausa del panel.
    dict(id="e54-desafio-sin-bloqueo-en-la-espera",
         pruebas=[SD + "test_bloqueo_mientras_espera_al_operador",
                  "test_datadome.TestPausaQueTerminaSola.test_termina_sola_cuando_datadome_bloquea",
                  "test_datadome.TestPausaQueTerminaSola.test_pagina_cerrada_no_dejo_pasar"],
         viejo='        return CMA_RESTRINGIO if _cma_datadome(page) == "bloqueo" else None\n',
         nuevo="        return None\n"),
    # El login: la portada sin plazo o sin detenerse, sin el decorador, el decorador que no ataja la detención o que
    # se traga todo, o sin las credenciales para la evidencia.
    dict(id="e54-login-sin-plazo-en-la-portada", pruebas=[PORTADA_MUDA], viejo=PORTADA_GOTO,
         nuevo=PORTADA_GOTO.replace(", timeout=CMA_ESPERA_PORTADA * 1000", "")),
    dict(id="e54-login-sin-detenerse-en-la-portada", pruebas=[PORTADA_MUDA], viejo=SIN_CARGAR_PORTADA,
         nuevo=SIN_CARGAR_PORTADA.replace("    except PWTimeout:\n", "    except PWTimeout:\n        raise\n")),
    dict(id="e54-login-sin-decorador", pruebas=[PORTADA_BLOQUEADA, PORTADA_MUDA],
         viejo="@_cma_login_se_detiene\ndef login_cma(", nuevo="def login_cma("),
    dict(id="e54-login-decorador-no-ataja", pruebas=[OTRAS_SIGUEN, SOLO_LOGIN_CMA, CO_CMA], viejo=ATAJA,
         nuevo="        return login(page, creds, reg, on_pausa=on_pausa)\n"),
    dict(id="e54-login-decorador-se-traga-todo", pruebas=[LG + "test_otra_falla_del_login_sigue_como_antes"],
         viejo=ATAJA, nuevo=ATAJA.replace("except CmaDetenida:", "except BaseException:")),
    dict(id="e54-login-sin-credenciales-para-la-evidencia", pruebas=[PORTADA_BLOQUEADA],
         viejo=("    # ¿Verificación de robot (deslizador)?\n    if _cma_es_robotcheck(page):\n"
                "        if not _cma_esperar_desafio(page, reg, on_pausa, creds=creds):\n"),
         nuevo=("    # ¿Verificación de robot (deslizador)?\n    if _cma_es_robotcheck(page):\n"
                "        if not _cma_esperar_desafio(page, reg, on_pausa):\n")),
    # La reserva: sin el decorador, de vuelta al portal en la fila siguiente, sin el motivo, sin las credenciales para
    # la evidencia, la detención después de la guarda, o una detención que un `except Exception` se traga.
    dict(id="e54-reserva-sin-decorador", pruebas=[CLICK_BOOK, DECORADO],
         viejo=SIN_CLIC["cma"] + '@_cma_si_se_detuvo\n', nuevo=SIN_CLIC["cma"]),
    dict(id="e54-reserva-vuelve-al-portal", pruebas=[CLICK_BOOK],
         viejo=('        motivo = _naviera_detenida(reg, "cma")\n        if motivo:\n'
                '            return _no_enviada(reg, motivo)\n'),
         nuevo=""),
    dict(id="e54-reserva-sin-motivo", pruebas=[CLICK_BOOK], viejo="            return _no_enviada(reg, e.motivo)\n",
         nuevo='            return (NO_ENVIADA, "")\n'),
    dict(id="e54-reserva-sin-credenciales-para-la-evidencia", pruebas=[CLICK_BOOK],
         viejo=('            if not _cma_esperar_desafio(page, reg, on_pausa, creds=creds):\n'
                '                _cma_interrumpir(page, reg, "al abrir el formulario",\n'),
         nuevo=('            if not _cma_esperar_desafio(page, reg, on_pausa):\n'
                '                _cma_interrumpir(page, reg, "al abrir el formulario",\n')),
    dict(id="e54-reserva-detenida-despues-de-la-guarda",
         pruebas=[RS + "test_lo_que_detiene_no_corre_despues_de_la_guarda"],
         viejo='            return _resultado_envio(page, reg, "cma", "CMA", f"cma_f{f}_6_confirmado"',
         nuevo=('            _cma_esperar_desafio(page, reg, on_pausa)\n'
                '            return _resultado_envio(page, reg, "cma", "CMA", f"cma_f{f}_6_confirmado"')),
    dict(id="e54-detenida-de-exception", pruebas=[CLICK_BOOK], viejo="class CmaDetenida(BaseException):\n",
         nuevo="class CmaDetenida(Exception):\n"),
    # El panel y la consola: las filas de CMA detenida en el login sin estado (como antes), el motivo sin la naviera
    # detenida, NO ENVIADA con cualquier naviera, o la naviera detenida que nunca se lee.
    dict(id="e54-panel-solo-sin-sesion", pruebas=[CO_CMA],
         viejo="                    for rsv in (sub_elegidas if _motivo_sin_sesion(reg, nav) else ()):\n",
         nuevo="                    for rsv in (sub_elegidas if nav in SIN_SESION else ()):\n"),
    dict(id="e54-consola-solo-sin-sesion", pruebas=[ER_CMA],
         viejo="            for i, rsv in (con_nave if _motivo_sin_sesion(reg, naviera_clave) else ()):\n",
         nuevo="            for i, rsv in (con_nave if naviera_clave in SIN_SESION else ()):\n"),
    dict(id="e54-motivo-sin-la-detenida", pruebas=[CO_CMA, ER_CMA], viejo=DETENIDA_CMA,
         nuevo='    return ((getattr(reg, "sin_sesion", None) or {}).get(nav)\n'),
    dict(id="e54-motivo-para-todas",
         pruebas=[CO + "test_login_fallido_no_reserva", ER + "test_login_fallido_no_toca_la_planilla"],
         viejo='            or SIN_SESION.get(nav, ""))\n',
         nuevo="            or SIN_SESION.get(nav, MSC_SIN_SESION))\n"),
    dict(id="e54-naviera-detenida-nunca", pruebas=[CLICK_BOOK, CO_CMA, BLOQUEO_YA],
         viejo='    return (getattr(reg, "detenida", None) or {}).get(nav, "")\n', nuevo='    return ""\n'),
]

# --- Encargo 55: la pausa del panel en log.txt, toda lectura de las páginas de CMA-CGM con plazo, y DataDome a mitad
# de una reserva de CMA-CGM (decisiones de Marcelo, CICLO-pausa-plazos-y-datadome.md). ---
LP = "test_datadome.TestLecturasConPlazo."
AM = "test_datadome.TestDataDomeAMitad."
RD = "test_datadome.TestReservaConDataDome."
PW = "test_web.TestPausaDelPanel."
PAUSA_LOG = UT + "test_pausa_del_panel_en_log"
DESLIZA = AM + "test_deslizador_lo_pasa_el_operador_y_la_fila_termina"
COMO_ANTES = SD + "test_deslizador_como_antes"
ENVUELTO = LP + "test_el_argumento_va_envuelto"
RESPONDE = LP + "test_cuenta_y_mira_solo_si_la_pagina_responde"
DETECTOR = LP + "test_el_detector_de_antes_lee_con_plazo"
FOTO_PLAZO = LP + "test_ninguna_lectura_de_cma_sin_plazo"
BOTON_FINAL = LP + "test_el_boton_final_solo_si_la_pagina_responde"
EVIDENCIA_ENVIO = LP + "test_la_evidencia_del_envio_con_plazo"
BOTON_LOGIN = LP + "test_el_login_mira_el_boton_con_plazo"
PASA = AM + "test_verificacion_que_deja_pasar_termina_la_fila"
BLOQUEO_A_MITAD = AM + "test_bloqueo_detiene_la_corrida"
CORTE_BLOQUEO = RD + "test_corte_con_el_bloqueo_detiene_la_corrida"
CORTE_SIN = RD + "test_corte_sin_datadome_sigue_como_antes"
REVISAR_DD = RD + "test_revisar_con_datadome_termina_la_fila_y_la_corrida_sigue"
ENTRE_PASOS = RD + "test_mira_entre_los_pasos_y_antes_de_la_guarda"
SIN_RESPUESTA = LP + "test_lo_que_vale_sin_respuesta"
PLAZOS = LP + "test_los_plazos_de_la_reserva_y_de_datadome"
NO_DECIDE = "test_datadome.TestSinRespuestaNoDecide."
ANADIR = NO_DECIDE + "test_no_pulsa_anadir_sin_saber_si_hace_falta"
RAMP = NO_DECIDE + "test_no_elige_otra_sugerencia_que_la_de_la_regla"
TAMANO = NO_DECIDE + "test_tamano_y_tipo_corta_sin_respuesta"
FINAL_PAUSA = ('    if como in (PAUSA_DETENIDA, PAUSA_VENCIDA):\n'
               '        reg.paso(f"⛔ La pausa se cortó a los {seg} s: {como}.")\n'
               '    else:\n'
               '        reg.paso(f"▶ La pausa terminó a los {seg} s" + (f": {como}." if como else "."))\n')
VUELTA_PANEL = ('        if _WEB["detener"] and _WEB["detener"].is_set():\n'
                '            como = PAUSA_DETENIDA\n'
                '            break\n'
                '        if ev.is_set():\n'
                '            _wlog("▸ Continuando (paso manual resuelto).")\n'
                '            como = PAUSA_RESUELTA\n'
                '            break\n')
ENVUELTA = '    return alcance.locator(":root").evaluate(f"(_raiz, arg) => ({js}\\n)(arg)", arg, timeout=plazo_ms)\n'
# Reescrita en el encargo 56: la pausa del deslizador devuelve cómo terminó, y le pasa al panel qué mirar (hasta).
DESLIZADOR_PAUSA = ('        como = _pausa_del_panel(reg, on_pausa, "CMA CGM: desliza la flecha hacia la derecha en el '
                    'navegador para "\n')
CORTE_DD = ('            except ObjetivoNoEncontrado:\n'
            '                _cma_datadome_a_mitad(page, reg, on_pausa, creds, '
            '"en un paso que no encontró su objetivo", fila)\n'
            '                raise\n')
SI_REVISAR = '            if resultado and resultado[0] == "REVISAR":\n'
EN_LA_GUARDA = '        _cma_datadome_a_mitad(page, reg, on_pausa, creds, "en «Envío de la reserva»", f)\n'
EVIDENCIA_GUARDA_CMA = '        _evidencia_antes_de_la_guarda(page, reg, f"cma_f{f}_guarda", plazo_ms=CMA_PLAZO_MS)\n'
AL_ABRIR = ('            if not _cma_esperar_desafio(page, reg, on_pausa, creds=creds):\n'
            '                _cma_interrumpir(page, reg, "al abrir el formulario",\n'
            '                                 CMA_SIN_DESLIZAR.format(seg=CMA_ESPERA_DESLIZADOR), f, creds)\n')
EMISION_CMA = '            reg.paso("EMISIÓN: Pulsando \'Enviar el booking\'...")\n'

MUTACIONES += [
    # La pausa del panel en log.txt: sin el porqué, sin cómo terminó, la cortada como terminada, sin los segundos, la
    # falla del panel sin anotar o tragada, pausa_manual o el deslizador sin anotarla, y el texto de «Detener».
    dict(id="e55-pausa-sin-por-que", pruebas=[PAUSA_LOG, DESLIZA, COMO_ANTES],
         viejo="    reg.paso(f\"⏸ PAUSA: espero al operador. Por qué: {' '.join(str(mensaje).split())}\")\n",
         nuevo='    reg.paso("⏸ PAUSA: espero al operador.")\n'),
    dict(id="e55-pausa-sin-final", pruebas=[PAUSA_LOG, DESLIZA], viejo=FINAL_PAUSA, nuevo="    pass\n"),
    dict(id="e55-pausa-detenida-como-terminada", pruebas=[PAUSA_LOG],
         viejo="    if como in (PAUSA_DETENIDA, PAUSA_VENCIDA):\n", nuevo="    if como in (PAUSA_VENCIDA,):\n"),
    dict(id="e55-pausa-vencida-como-terminada", pruebas=[PAUSA_LOG],
         viejo="    if como in (PAUSA_DETENIDA, PAUSA_VENCIDA):\n", nuevo="    if como in (PAUSA_DETENIDA,):\n"),
    dict(id="e55-pausa-sin-segundos", pruebas=[PAUSA_LOG], viejo="    seg = round(time.time() - t0)\n",
         nuevo="    seg = 0\n"),
    dict(id="e55-pausa-falla-sin-anotar", pruebas=[PAUSA_LOG],
         viejo=('        reg.paso(f"⛔ La pausa se cortó a los {round(time.time() - t0)} s: falló el panel '
                '({_texto_error(e)}).")\n'),
         nuevo="        pass\n"),
    dict(id="e55-pausa-falla-se-traga", pruebas=[PAUSA_LOG],
         viejo='falló el panel ({_texto_error(e)}).")\n        raise\n',
         nuevo='falló el panel ({_texto_error(e)}).")\n        return None\n'),
    dict(id="e55-pausa-manual-sin-anotar", pruebas=[PAUSA_LOG],
         viejo="        return _pausa_del_panel(reg, on_pausa, mensaje)\n", nuevo="        return on_pausa(mensaje)\n"),
    dict(id="e55-deslizador-pausa-sin-anotar", pruebas=[COMO_ANTES, DESLIZA], viejo=DESLIZADOR_PAUSA,
         nuevo=DESLIZADOR_PAUSA.replace("_pausa_del_panel(reg, on_pausa, ", "on_pausa(")),
    dict(id="e55-pausa-otro-texto-de-detener", pruebas=[PAUSA_LOG],
         viejo='PAUSA_DETENIDA = "el operador pulsó «Detener»"\n', nuevo='PAUSA_DETENIDA = "el operador la detuvo"\n'),
    # La pausa del panel web: «Ya lo resolví» antes que «Detener», sin decir cómo terminó, la vencida como resuelta, o
    # «Detener» sin decirlo.
    dict(id="e55-web-pausa-continuar-antes-que-detener", pruebas=[PW + "test_detener_la_corta", CO + "test_detener"],
         viejo=VUELTA_PANEL,
         nuevo=VUELTA_PANEL[VUELTA_PANEL.index("        if ev.is_set()"):]
         + VUELTA_PANEL[:VUELTA_PANEL.index("        if ev.is_set()")]),
    dict(id="e55-web-pausa-no-dice",
         pruebas=[PW + "test_termina_con_ya_lo_resolvi", PW + "test_vence_a_los_diez_minutos",
                  CO + "test_pausa_y_continuar"],
         viejo='        _WEB["pausa_msg"] = ""\n    return como\n',
         nuevo='        _WEB["pausa_msg"] = ""\n    return None\n'),
    dict(id="e55-web-pausa-vencida-como-resuelta", pruebas=[PW + "test_vence_a_los_diez_minutos"],
         viejo="    como = PAUSA_VENCIDA\n", nuevo="    como = PAUSA_RESUELTA\n"),
    dict(id="e55-web-pausa-detener-no-dice", pruebas=[PW + "test_detener_la_corta", CO + "test_detener"],
         viejo="            como = PAUSA_DETENIDA\n            break\n", nuevo="            break\n"),
    # Las lecturas con plazo: el argumento sin envolver o sin su salto de línea, None como sin argumento, la pregunta
    # siempre que sí o sin plazo, count, is_visible y el JavaScript sin preguntar o sin plazo.
    dict(id="e55-evaluar-sin-envoltura", pruebas=[ENVUELTO], viejo=ENVUELTA,
         nuevo='    return alcance.locator(":root").evaluate(js, arg, timeout=plazo_ms)\n'),
    dict(id="e55-evaluar-sin-salto", pruebas=[ENVUELTO], viejo="({js}\\n)(arg)", nuevo="({js})(arg)"),
    dict(id="e55-evaluar-none-sin-argumento", pruebas=[ENVUELTO],
         viejo="    if arg is _SIN_ARGUMENTO:\n        return alc",
         nuevo="    if arg is _SIN_ARGUMENTO or arg is None:\n        return alc"),
    dict(id="e55-responde-siempre", pruebas=[RESPONDE, BOTON_FINAL],
         viejo='        return _evaluar_con_plazo(alcance, "() => true", plazo_ms) is True\n',
         nuevo="        return True\n"),
    dict(id="e55-responde-sin-plazo", pruebas=[RESPONDE, FOTO_PLAZO],
         viejo='        return _evaluar_con_plazo(alcance, "() => true", plazo_ms) is True\n',
         nuevo='        return alcance.evaluate("() => true") is True\n'),
    dict(id="e55-cuantos-sin-preguntar", pruebas=[RESPONDE],
         viejo="    return loc.count() if _cma_responde(page) else si_no_responde\n", nuevo="    return loc.count()\n"),
    dict(id="e55-se-ve-sin-preguntar", pruebas=[RESPONDE],
         viejo="    return loc.is_visible() if _cma_responde(page) else si_no_responde\n",
         nuevo="    return loc.is_visible()\n"),
    dict(id="e55-js-sin-plazo", pruebas=[FOTO_PLAZO],
         viejo="    return _evaluar_con_plazo(alcance, js, CMA_PLAZO_MS, arg)\n",
         nuevo="    return alcance.evaluate(js) if arg is _SIN_ARGUMENTO else alcance.evaluate(js, arg)\n"),
    # El detector de antes, el login y la reserva leyendo otra vez sin plazo.
    dict(id="e55-robotcheck-marco-titulo-sin-plazo", pruebas=[DETECTOR, FOTO_PLAZO],
         viejo='                ftit = str(_cma_leer(fr, _JS_CMA_TITULO) or "").lower()\n',
         nuevo='                ftit = (fr.title() or "").lower()\n'),
    dict(id="e55-robotcheck-marco-texto-sin-plazo", pruebas=[DETECTOR, FOTO_PLAZO],
         viejo='                ftxt = str(_cma_leer(fr, _JS_CMA_TEXTO) or "").lower()\n',
         nuevo='                ftxt = (fr.evaluate(_JS_CMA_TEXTO) or "").lower()\n'),
    dict(id="e55-robotcheck-pagina-sin-plazo", pruebas=[DETECTOR, FOTO_PLAZO],
         viejo='        tit = str(_cma_leer(page, _JS_CMA_TITULO) or "").lower()\n',
         nuevo='        tit = (page.title() or "").lower()\n'),
    dict(id="e55-login-titulo-sin-plazo", pruebas=[FOTO_PLAZO],
         viejo='        titulo = str(_cma_leer(page, _JS_CMA_TITULO) or "").lower()       # con plazo (encargo 55)\n',
         nuevo='        titulo = (page.title() or "").lower()\n'),
    dict(id="e55-login-menu-sin-plazo", pruebas=[FOTO_PLAZO],
         viejo="            ab = _cma_js(page, _JS_CMA_MENU); reg.info",
         nuevo="            ab = page.evaluate(_JS_CMA_MENU); reg.info"),
    dict(id="e55-login-boton-sin-plazo", pruebas=[FOTO_PLAZO],
         viejo='        click_si_existe(page, "button[type=\'submit\']", 5000, reg, plazo_ms=CMA_PLAZO_MS)\n',
         nuevo='        click_si_existe(page, "button[type=\'submit\']", 5000, reg)\n'),
    dict(id="e55-aviso-sin-plazo", pruebas=[FOTO_PLAZO], viejo='        return str(_cma_js(page, r"""()=>{',
         nuevo='        return str(page.evaluate(r"""()=>{'),
    dict(id="e55-rutas-sin-plazo", pruebas=[FOTO_PLAZO],
         viejo='            res = _cma_js(page, _JS_CMA_RUTAS, {"toks": toks, "viaje": _palabras_del_viaje(viaje_pedido)',
         nuevo='            res = page.evaluate(_JS_CMA_RUTAS, {"toks": toks, "viaje": _palabras_del_viaje(viaje_pedido)'),
    dict(id="e55-temperatura-sin-plazo", pruebas=[FOTO_PLAZO],
         viejo="        donde = _cma_js(page, _JS_CMA_REEFER_TEMPERATURA, temp)\n",
         nuevo="        donde = page.evaluate(_JS_CMA_REEFER_TEMPERATURA, temp)\n"),
    dict(id="e55-reefer-guardar-sin-plazo", pruebas=[FOTO_PLAZO],
         viejo="btn_g.evaluate(_JS_CMA_REEFER_GUARDAR, timeout=CMA_PLAZO_MS)",
         nuevo="btn_g.evaluate(_JS_CMA_REEFER_GUARDAR)"),
    dict(id="e55-mantenimiento-sin-plazo", pruebas=[FOTO_PLAZO],
         viejo="    texto = _cma_leer(page, _JS_CMA_TEXTO, CMA_PLAZO_MS)\n",
         nuevo="    texto = texto_pagina(page)\n"),
    dict(id="e55-sugerencias-cuentan-sin-preguntar", pruebas=[FOTO_PLAZO],
         viejo="                if _cma_cuantos(page, li):\n", nuevo="                if li.count():\n"),
    # Los ayudantes comunes que CMA llama con plazo: llamados sin él, o sin usarlo.
    dict(id="e55-evidencia-del-puerto-sin-plazo", pruebas=[FOTO_PLAZO],
         viejo=('f"con las sugerencias de {etiqueta}",\n'
                '                                                      completa=False, plazo_ms=CMA_PLAZO_MS)\n'),
         nuevo=('f"con las sugerencias de {etiqueta}",\n'
                '                                                      completa=False)\n')),
    dict(id="e55-sin-sugerencia-sin-plazo", pruebas=[FOTO_PLAZO],
         viejo="_evidencia_sin_sugerencia(page, reg, evidencia, etiqueta, plazo_ms=CMA_PLAZO_MS)",
         nuevo="_evidencia_sin_sugerencia(page, reg, evidencia, etiqueta)"),
    dict(id="e55-sin-objetivo-sin-plazo",
         pruebas=[FOTO_PLAZO, "test_clics.TestSinClicACiegas.test_cada_reservador_que_corta_esta_decorado"],
         viejo=SIN_CLIC["cma"], nuevo='@_sin_clic_a_ciegas("cma")\n'),
    dict(id="e55-sin-objetivo-ignora-el-plazo", pruebas=[CORTE_SIN],
         viejo='"en el paso sin objetivo", completa=False, plazo_ms=plazo_ms)\n',
         nuevo='"en el paso sin objetivo", completa=False)\n'),
    dict(id="e55-evidencia-ignora-el-plazo", pruebas=[CORTE_SIN],
         viejo="_guardar_html_completo(page, reg, nombre, momento, plazo_ms=plazo_ms)\n",
         nuevo="_guardar_html_completo(page, reg, nombre, momento)\n"),
    dict(id="e55-guarda-cma-sin-plazo", pruebas=[LD + "test_cma", FOTO_PLAZO], viejo=EVIDENCIA_GUARDA_CMA,
         nuevo='        _evidencia_antes_de_la_guarda(page, reg, f"cma_f{f}_guarda")\n'),
    dict(id="e55-pulsar-sin-preguntar", pruebas=[BOTON_FINAL],
         viejo="    if plazo_ms and not _responde(alcance, plazo_ms):\n        return False\n", nuevo=""),
    dict(id="e55-envio-evidencia-ignora-el-plazo", pruebas=[EVIDENCIA_ENVIO],
         viejo='_guardar_html_completo(page, reg, nombre, "tras el envío", plazo_ms=plazo_ms)\n',
         nuevo='_guardar_html_completo(page, reg, nombre, "tras el envío")\n'),
    dict(id="e55-resultado-sin-plazo", pruebas=[EVIDENCIA_ENVIO], viejo=EVIDENCIA,
         nuevo=EVIDENCIA.replace(", plazo_ms=plazo_ms", "")),
    dict(id="e55-envio-cma-sin-plazo",
         pruebas=["test_envio.TestReservadores.test_cma_decide_con_lo_que_vio", FOTO_PLAZO],
         viejo="\"button:has-text('Submit booking')\", plazo_ms=CMA_PLAZO_MS)\n",
         nuevo="\"button:has-text('Submit booking')\")\n"),
    dict(id="e55-click-si-existe-ignora-el-plazo", pruebas=[BOTON_LOGIN],
         viejo=("                estado = int(_evaluar_con_plazo(page, _JS_ESTADO, plazo_ms, selector) if plazo_ms\n"
                "                             else page.evaluate(_JS_ESTADO, selector)); err = \"\"; break\n"),
         nuevo="                estado = int(page.evaluate(_JS_ESTADO, selector)); err = \"\"; break\n"),
    # DataDome a mitad de la reserva: no mirar, mirar y seguir, la otra página sin el operador, sin el nombre de la
    # fila, el deslizador sin pasar como pasado, sin la línea, la fila interrumpida que detiene la corrida o sin
    # evidencia, la interrumpida que no es una detenida, siempre interrumpir, no esperar ni detener, el bloqueo en la
    # espera, y lo medido.
    dict(id="e55-a-mitad-no-mira", pruebas=[BLOQUEO_A_MITAD, PASA, CORTE_BLOQUEO],
         viejo="    if not _cma_datadome(page):\n        return\n    reg.paso(f\"DataDome apareció",
         nuevo="    return\n    reg.paso(f\"DataDome apareció"),
    dict(id="e55-a-mitad-siempre-interrumpe", pruebas=[AM + "test_sin_datadome_no_hace_nada"],
         viejo="    if not _cma_datadome(page):\n        return\n    reg.paso(f\"DataDome apareció",
         nuevo="    if False:\n        return\n    reg.paso(f\"DataDome apareció"),
    dict(id="e55-a-mitad-sigue-tras-pasar", pruebas=[PASA, REVISAR_DD],
         viejo="    _cma_interrumpir(page, reg, donde, CMA_PASO_LA_VERIFICACION, fila, creds)\n", nuevo=""),
    dict(id="e55-a-mitad-otra-sin-operador", pruebas=[AM + "test_otra_pagina_suya_va_al_operador"],
         viejo='    if que in ("deslizador", "otra"):\n        deslizo',
         nuevo='    if que == "deslizador":\n        deslizo'),
    dict(id="e55-a-mitad-sin-nombre-de-fila", pruebas=[DESLIZA], viejo=', nombre=f"cma_f{fila}_robot_desafio")',
         nuevo=")"),
    dict(id="e55-a-mitad-sin-deslizar-como-deslizado", pruebas=[AM + "test_deslizador_que_nadie_desliza"],
         viejo=("CMA_DESLIZADO if deslizo\n"
                "                         else CMA_SIN_DESLIZAR.format(seg=CMA_ESPERA_DESLIZADOR), fila, creds)"),
         nuevo="CMA_DESLIZADO, fila, creds)"),
    dict(id="e55-a-mitad-sin-aviso", pruebas=[BLOQUEO_A_MITAD, CORTE_BLOQUEO],
         viejo='    reg.paso(f"DataDome apareció a mitad de la reserva de CMA-CGM, {donde}.")\n', nuevo=""),
    dict(id="e55-a-mitad-sin-esperar-ni-detener",
         pruebas=[AM + "test_verificacion_que_no_deja_pasar_detiene_al_plazo", BLOQUEO_A_MITAD],
         viejo="    que = _cma_sin_bloqueo_ni_espera(page, reg, creds)\n    if que in (\"deslizador\", \"otra\"):\n",
         nuevo="    que = _cma_datadome(page)\n    if que in (\"deslizador\", \"otra\"):\n"),
    # Reescrita en el encargo 56: con el bloqueo, la espera del deslizador ya no lo detiene ahí, y la da por superada.
    dict(id="e55-a-mitad-sin-bloqueo-en-la-espera",
         pruebas=[AM + "test_deslizador_que_pasa_al_bloqueo_detiene",
                  "test_datadome.TestPausaQueTerminaSola.test_termina_sola_cuando_datadome_bloquea"],
         viejo=('    if como == CMA_RESTRINGIO:\n'
                '        _cma_detener(page, reg, CMA_ACCESO_RESTRINGIDO, "cma_acceso_restringido", creds)\n'),
         nuevo=""),
    dict(id="e55-deslizador-captura-sin-plazo", pruebas=[COMO_ANTES, DESLIZA],
         viejo="    reg.captura(page, nombre, plazo_ms=CMA_CAPTURA_MS)\n", nuevo="    reg.captura(page, nombre)\n"),
    dict(id="e55-interrumpida-detiene", pruebas=[PASA, REVISAR_DD],
         viejo="    motivo = CMA_INTERRUMPIDA.format(donde=donde, que=que)\n",
         nuevo=('    motivo = CMA_INTERRUMPIDA.format(donde=donde, que=que)\n'
                '    vars(reg).setdefault("detenida", {})["cma"] = motivo\n')),
    dict(id="e55-interrumpida-sin-evidencia", pruebas=[PASA],
         viejo='    _cma_evidencia(page, reg, f"cma_f{fila}_datadome", "interrumpida", creds)\n', nuevo=""),
    dict(id="e55-interrumpida-de-baseexception", pruebas=[AM + "test_lo_medido", REVISAR_DD],
         viejo="class CmaInterrumpida(CmaDetenida):\n", nuevo="class CmaInterrumpida(BaseException):\n"),
    dict(id="e55-espera-deslizador-otra", pruebas=[AM + "test_lo_medido"], viejo="CMA_ESPERA_DESLIZADOR = 180\n",
         nuevo="CMA_ESPERA_DESLIZADOR = 120\n"),
    dict(id="e55-motivo-de-la-interrumpida-otro", pruebas=[AM + "test_lo_medido"],
         viejo='CMA_DESLIZADO = "el operador deslizó la flecha"\n',
         nuevo='CMA_DESLIZADO = "el operador lo resolvió"\n'),
    # El decorador: no mirar DataDome en el corte, tragárselo, no mirar REVISAR, mirarlo todo (también lo de después de
    # la guarda), o mirar también los errores.
    dict(id="e55-decorador-no-mira-el-corte", pruebas=[CORTE_BLOQUEO], viejo=CORTE_DD,
         nuevo="            except ObjetivoNoEncontrado:\n                raise\n"),
    dict(id="e55-decorador-se-traga-el-corte", pruebas=[RD + "test_el_decorador_no_se_traga_el_corte", CORTE_SIN],
         viejo=CORTE_DD,
         nuevo=CORTE_DD.replace("                raise\n", '                return _no_enviada(reg, "corte")\n')),
    dict(id="e55-decorador-no-mira-revisar", pruebas=[REVISAR_DD], viejo=SI_REVISAR, nuevo="            if False:\n"),
    dict(id="e55-decorador-mira-todo", pruebas=[RD + "test_despues_de_la_guarda_no_mira"], viejo=SI_REVISAR,
         nuevo="            if resultado:\n"),
    dict(id="e55-decorador-mira-los-errores", pruebas=[RD + "test_otra_falla_sale_sin_mirar"],
         viejo="            except ObjetivoNoEncontrado:\n                _cma_datadome_a_mitad(",
         nuevo="            except (ObjetivoNoEncontrado, Exception):\n                _cma_datadome_a_mitad("),
    # La reserva: sin mirar tras el origen o en la guarda, mirar después de la evidencia de la guarda o después de la
    # guarda, un REVISAR después de la guarda, y la que sigue sin el deslizador al abrir el formulario.
    dict(id="e55-reserva-no-mira-tras-el-origen", pruebas=[ENTRE_PASOS],
         viejo='        _cma_datadome_a_mitad(page, reg, on_pausa, creds, "tras el origen", f)\n', nuevo=""),
    dict(id="e55-reserva-no-mira-en-la-guarda", pruebas=[ENTRE_PASOS], viejo=EN_LA_GUARDA, nuevo=""),
    dict(id="e55-reserva-mira-despues-de-la-evidencia", pruebas=[ENTRE_PASOS],
         viejo=EN_LA_GUARDA + EVIDENCIA_GUARDA_CMA, nuevo=EVIDENCIA_GUARDA_CMA + EN_LA_GUARDA),
    dict(id="e55-reserva-mira-despues-de-la-guarda",
         pruebas=[ENTRE_PASOS, RS + "test_lo_que_detiene_no_corre_despues_de_la_guarda"], viejo=EMISION_CMA,
         nuevo=EMISION_CMA + '            _cma_datadome_a_mitad(page, reg, on_pausa, creds, "tras la guarda", f)\n'),
    dict(id="e55-revisar-despues-de-la-guarda", pruebas=[RD + "test_revisar_solo_antes_de_la_guarda"],
         viejo=EMISION_CMA,
         nuevo=EMISION_CMA + '            if not reserva:\n                return ("REVISAR", "x")\n'),
    dict(id="e55-formulario-sigue-sin-deslizar", pruebas=[RD + "test_deslizador_sin_pasar_al_abrir_el_formulario"],
         viejo=AL_ABRIR, nuevo="            _cma_esperar_desafio(page, reg, on_pausa, creds=creds)\n"),
    # Encargo 55, después de la revisión propia: las lecturas de la reserva y del login con CMA_PLAZO_MS, y las
    # elecciones que una lectura sin respuesta no decide. Sin respuesta, 0 o False aunque se pida otra cosa; el campo
    # que no se ve sin respuesta, la sugerencia de «ramp» o la opción de «Tamaño y tipo» elegidas igual, el JavaScript
    # de respaldo sin respuesta, el motivo sin decir por qué; y cada plazo con el del otro.
    dict(id="e55-cuantos-sin-respuesta-cero", pruebas=[SIN_RESPUESTA, RAMP, TAMANO],
         viejo="    return loc.count() if _cma_responde(page) else si_no_responde\n",
         nuevo="    return loc.count() if _cma_responde(page) else 0\n"),
    dict(id="e55-se-ve-sin-respuesta-falso", pruebas=[SIN_RESPUESTA, ANADIR],
         viejo="    return loc.is_visible() if _cma_responde(page) else si_no_responde\n",
         nuevo="    return loc.is_visible() if _cma_responde(page) else False\n"),
    dict(id="e55-anadir-sin-respuesta-pulsa", pruebas=[ANADIR],
         viejo="_cma_se_ve(page, page.locator(sel).first, si_no_responde=True)",
         nuevo="_cma_se_ve(page, page.locator(sel).first)"),
    dict(id="e55-ramp-sin-respuesta-elige", pruebas=[RAMP],
         viejo="        n = _cma_cuantos(page, ramp, si_no_responde=None)\n",
         nuevo="        n = _cma_cuantos(page, ramp)\n"),
    dict(id="e55-ramp-sin-respuesta-la-primera", pruebas=[RAMP],
         viejo="            raise TimeoutError(CMA_SIN_RESPUESTA)\n", nuevo="            return li.first\n"),
    dict(id="e55-tamano-sin-respuesta-cuenta-cero", pruebas=[TAMANO],
         viejo="                n = _cma_cuantos(page, op, si_no_responde=None)\n                if n == 0:\n",
         nuevo="                n = _cma_cuantos(page, op)\n                if n == 0:\n"),
    dict(id="e55-tamano-sin-respuesta-js", pruebas=[TAMANO],
         viejo="        if not sel_ok and not sin_respuesta:\n", nuevo="        if not sel_ok:\n"),
    dict(id="e55-tamano-sin-respuesta-sin-motivo", pruebas=[TAMANO], viejo='f", porque {CMA_SIN_RESPUESTA}"',
         nuevo='""'),
    dict(id="e55-plazo-de-la-reserva-corto", pruebas=[PLAZOS], viejo="CMA_PLAZO_MS = 30000\n",
         nuevo="CMA_PLAZO_MS = 1500\n"),
    dict(id="e55-sin-respuesta-sin-plazo", pruebas=[PLAZOS],
         viejo='CMA_SIN_RESPUESTA = f"la página no contestó en {CMA_PLAZO_MS // 1000} s"\n',
         nuevo='CMA_SIN_RESPUESTA = "la página no contestó"\n'),
    dict(id="e55-js-con-el-plazo-de-datadome", pruebas=[PLAZOS],
         viejo="    return _evaluar_con_plazo(alcance, js, CMA_PLAZO_MS, arg)\n",
         nuevo="    return _evaluar_con_plazo(alcance, js, CMA_LECTURA_MS, arg)\n"),
    dict(id="e55-responde-con-el-plazo-de-datadome", pruebas=[PLAZOS, RESPONDE],
         viejo="    return _responde(page, CMA_PLAZO_MS)\n", nuevo="    return _responde(page, CMA_LECTURA_MS)\n"),
    dict(id="e55-mantenimiento-con-el-plazo-de-datadome", pruebas=[PLAZOS],
         viejo="    texto = _cma_leer(page, _JS_CMA_TEXTO, CMA_PLAZO_MS)\n",
         nuevo="    texto = _cma_leer(page, _JS_CMA_TEXTO)\n"),
    dict(id="e55-leer-con-el-plazo-de-la-reserva", pruebas=[PLAZOS, DETECTOR],
         viejo="def _cma_leer(alcance, js, plazo_ms=CMA_LECTURA_MS):\n",
         nuevo="def _cma_leer(alcance, js, plazo_ms=CMA_PLAZO_MS):\n"),
]

# --- Encargo 56 (CICLO-pausa-sola-y-comentarios.md): los comentarios de CMA-CGM que fallan cortan la reserva, la pausa
# del deslizador termina sola cuando DataDome deja pasar la página o la bloquea, y «Detener» corta la espera. ---
PS = "test_datadome.TestPausaQueTerminaSola."
TK = "test_web.TestPausaDelPanelTkinter."
DEJA_PASAR = PS + "test_termina_sola_cuando_datadome_deja_pasar"
BLOQUEA = PS + "test_termina_sola_cuando_datadome_bloquea"
DETENER_PAUSA = PS + "test_detener_corta_la_espera_sin_volver_a_mirar_la_pagina"
RESUELTO_Y_DETENER = PS + "test_ya_lo_resolvi_y_despues_detener"
YA_CERRADO = PS + "test_detener_con_el_navegador_ya_cerrado"
SIN_CAMBIOS = PS + "test_sin_botones_ni_cambios_sigue_esperando"
A_MITAD_SOLA = PS + "test_a_mitad_de_la_reserva"
PAUSA_DICE_DETENER = PS + "test_la_pausa_que_dice_detener_corta"
DETENIDO_CMA = PS + "test_detener_deja_la_fila_detenido_y_el_login_sin_sesion"
CERRADA = PS + "test_pagina_cerrada_no_dejo_pasar"
MEDIDO_56 = PS + "test_lo_medido"
QUE_DETIENE = "test_datadome.TestReservaCma.test_lo_que_detiene_no_corre_despues_de_la_guarda"
COMENTARIOS_FALLAN = C1 + "test_comentarios_que_fallan_cortan"
NO_ESCRIBE = C1 + "test_comentarios_que_el_localizador_no_escribe_cortan"
ESCRITOS = C1 + "test_lo_que_falla_despues_de_escribirlos_sigue_como_antes"
FILA_COMENTARIOS = C1 + "test_comentarios_que_fallan_dejan_la_fila_no_enviada_con_su_evidencia"
SOLA = '        if sola:\n            como = sola\n            break\n'
MIRA = "        sola = hasta() if hasta and not ev.is_set() else None\n"
MIRA_TK = "                sola = hasta() if hasta else None\n"
CANCELA = '        raise CmaCancelada("Cancelado por el operador")\n'
CORTA_COMENTARIOS = ('        if not escritos:\n'
                     '            raise _cma_fallo("Comentarios de CMA", CMA_CAMPO_COMENTARIOS, "buscarlo o escribirlo"'
                     ', e)\n')

MUTACIONES += [
    # Los comentarios: lo que falla antes de escribirlos no corta, o corta también después; el localizador da por
    # escritos los que no escribió; el motivo sin la falla, el paso con otro nombre, o el campo con otro texto.
    dict(id="e56-comentarios-falla-sigue", pruebas=[COMENTARIOS_FALLAN, NO_ESCRIBE, FILA_COMENTARIOS],
         viejo=CORTA_COMENTARIOS, nuevo=CORTA_COMENTARIOS.replace("if not escritos:", "if False:")),
    dict(id="e56-comentarios-escritos-cortan", pruebas=[ESCRITOS],
         viejo="            escritos = True\n            reg.info(f\"comentario: '{COSCO_REMARK}'\")\n",
         nuevo="            reg.info(f\"comentario: '{COSCO_REMARK}'\")\n"),
    dict(id="e56-comentarios-localizador-escritos-antes", pruebas=[NO_ESCRIBE],
         viejo="            ta.fill(COSCO_REMARK)\n            escritos = True\n",
         nuevo="            escritos = True\n            ta.fill(COSCO_REMARK)\n"),
    dict(id="e56-comentarios-motivo-sin-la-falla", pruebas=[COMENTARIOS_FALLAN, NO_ESCRIBE, FILA_COMENTARIOS],
         viejo=CORTA_COMENTARIOS,
         nuevo=('        if not escritos:\n            raise ObjetivoNoEncontrado("Comentarios de CMA", '
                'CMA_CAMPO_COMENTARIOS + ", porque el programa falló al buscarlo o escribirlo")\n')),
    dict(id="e56-comentarios-otro-paso", pruebas=[COMENTARIOS_FALLAN, FILA_COMENTARIOS],
         viejo=CORTA_COMENTARIOS,
         nuevo=CORTA_COMENTARIOS.replace('("Comentarios de CMA",', '("Comentarios",')),
    dict(id="e56-comentarios-campo-otro", pruebas=[C1 + "test_comentarios_sin_su_campo_corta"],
         viejo='CMA_CAMPO_COMENTARIOS = ("el campo de comentarios (por su placeholder «facilítenos», «comentario», '
               '«comment» o "\n',
         nuevo='CMA_CAMPO_COMENTARIOS = ("el campo de comentarios (por su placeholder «comentario», «comment» o "\n'),
    # La pausa del deslizador: sin mirar la página, sin usar lo que dice, el panel sin pasarle qué mirar, la flecha
    # como si hubiera pasado, la página cerrada como si hubiera pasado, y la pausa vencida sin la espera de después.
    dict(id="e56-deslizador-sin-vigia", pruebas=[DEJA_PASAR, BLOQUEA, A_MITAD_SOLA],
         viejo='                                "continuar.", hasta=_cma_vigia(page))\n',
         nuevo='                                "continuar.")\n'),
    dict(id="e56-deslizador-sin-lo-que-dice-la-pausa", pruebas=[DEJA_PASAR, BLOQUEA],
         viejo="        como = _pausa_del_panel(reg, on_pausa, ", nuevo="        _pausa_del_panel(reg, on_pausa, "),
    dict(id="e56-pausa-del-panel-sin-hasta", pruebas=[DEJA_PASAR, BLOQUEA],
         viejo="        como = on_pausa(mensaje, hasta=hasta) if hasta else on_pausa(mensaje)\n",
         nuevo="        como = on_pausa(mensaje)\n"),
    dict(id="e56-vigia-deslizador-como-pasado", pruebas=[SIN_CAMBIOS, CERRADA],
         viejo='        return CMA_RESTRINGIO if _cma_datadome(page) == "bloqueo" else None\n',
         nuevo='        return CMA_RESTRINGIO if _cma_datadome(page) == "bloqueo" else CMA_DEJO_PASAR\n'),
    dict(id="e56-cerrada-deja-pasar", pruebas=[CERRADA],
         viejo="    return None if page.is_closed() else CMA_DEJO_PASAR\n", nuevo="    return CMA_DEJO_PASAR\n"),
    dict(id="e56-vencida-sin-la-espera-de-despues", pruebas=[SIN_CAMBIOS],
         viejo="    while como not in (CMA_DEJO_PASAR, CMA_RESTRINGIO):\n",
         nuevo="    while como not in (CMA_DEJO_PASAR, CMA_RESTRINGIO, PAUSA_VENCIDA):\n"),
    dict(id="e56-dejo-pasar-otro-texto", pruebas=[MEDIDO_56, DEJA_PASAR],
         viejo='CMA_DEJO_PASAR = "DataDome dejó pasar la página"\n', nuevo='CMA_DEJO_PASAR = "pasó"\n'),
    dict(id="e56-restringio-otro-texto", pruebas=[MEDIDO_56, BLOQUEA],
         viejo='CMA_RESTRINGIO = "DataDome restringió el acceso"\n', nuevo='CMA_RESTRINGIO = "bloqueó"\n'),
    # «Detener»: sin lo que dice la pausa, sin mirar después de leer ni cuando la espera falla, sin mirar el panel, sin
    # cortar, otra cosa en vez de CmaCancelada, sin decirlo, la fila NO ENVIADA, y CmaCancelada sin ser CmaDetenida.
    dict(id="e56-detener-sin-lo-que-dice-la-pausa", pruebas=[PAUSA_DICE_DETENER],
         viejo="        _cma_si_pulso_detener(reg, como)\n", nuevo="        _cma_si_pulso_detener(reg)\n"),
    dict(id="e56-detener-sin-mirar-tras-leer", pruebas=[RESUELTO_Y_DETENER],
         viejo="        _cma_si_pulso_detener(reg)              # y lo leído mientras lo cerraba no vale\n", nuevo=""),
    dict(id="e56-detener-sin-mirar-si-la-espera-falla", pruebas=[YA_CERRADO],
         viejo="            _cma_si_pulso_detener(reg)          # «Detener» cerró el navegador mientras esperaba\n",
         nuevo=""),
    dict(id="e56-detener-sin-mirar-el-panel", pruebas=[RESUELTO_Y_DETENER, YA_CERRADO],
         viejo='    if como == PAUSA_DETENIDA or (_WEB.get("detener") and _WEB["detener"].is_set()):\n',
         nuevo="    if como == PAUSA_DETENIDA:\n"),
    dict(id="e56-detener-no-corta", pruebas=[DETENER_PAUSA, PAUSA_DICE_DETENER], viejo=CANCELA,
         nuevo="        pass\n"),
    dict(id="e56-detener-levanta-otra-cosa", pruebas=[DETENER_PAUSA, QUE_DETIENE], viejo=CANCELA,
         nuevo='        raise RuntimeError("Cancelado por el operador")\n'),
    dict(id="e56-detener-otro-motivo", pruebas=[DETENER_PAUSA], viejo=CANCELA,
         nuevo='        raise CmaCancelada("Detenido")\n'),
    dict(id="e56-detener-sin-decirlo", pruebas=[DETENER_PAUSA],
         viejo=('        reg.paso("⛔ El operador pulsó «Detener»: corto la espera del deslizador sin volver a mirar la '
                'página.")\n'),
         nuevo=""),
    dict(id="e56-cancelada-como-no-enviada", pruebas=[DETENIDO_CMA],
         viejo='        except CmaCancelada as e:\n            return ("DETENIDO", e.motivo)\n', nuevo=""),
    dict(id="e56-cancelada-otro-estado", pruebas=[DETENIDO_CMA],
         viejo='            return ("DETENIDO", e.motivo)\n', nuevo='            return ("NO ENVIADA", e.motivo)\n'),
    dict(id="e56-cancelada-de-baseexception", pruebas=[DETENIDO_CMA, MEDIDO_56],
         viejo="class CmaCancelada(CmaDetenida):\n",
         nuevo='class CmaCancelada(BaseException):\n    motivo = "Cancelado por el operador"\n'),
    # La pausa del panel web: sin mirar, mirando con un botón ya pulsado, lo visto antes que «Detener», sin terminar
    # con lo visto, sin el tope de reloj o con otro.
    dict(id="e56-web-pausa-no-mira", pruebas=[PW + "test_termina_sola_con_lo_que_dice_hasta", DEJA_PASAR],
         viejo=MIRA, nuevo="        sola = None\n"),
    dict(id="e56-web-pausa-mira-con-un-boton", pruebas=[PW + "test_con_un_boton_pulsado_no_mira", DETENER_PAUSA],
         viejo=MIRA, nuevo="        sola = hasta() if hasta else None\n"),
    dict(id="e56-web-pausa-lo-visto-antes-que-detener", pruebas=[PW + "test_detener_antes_que_lo_que_vio"],
         viejo=VUELTA_PANEL + SOLA, nuevo=SOLA + VUELTA_PANEL),
    dict(id="e56-web-pausa-no-termina-con-lo-visto", pruebas=[PW + "test_termina_sola_con_lo_que_dice_hasta"],
         viejo=SOLA, nuevo=""),
    dict(id="e56-web-pausa-sin-tope-de-reloj", pruebas=[PW + "test_con_hasta_vence_a_los_diez_minutos_de_reloj"],
         viejo=("        if _time.time() >= fin:             # con 'hasta', cada vuelta tarda lo que tarde en leer "
                "(encargo 56)\n            break\n"),
         nuevo=""),
    dict(id="e56-web-pausa-otro-tope-de-reloj", pruebas=[PW + "test_con_hasta_vence_a_los_diez_minutos_de_reloj"],
         viejo="    fin = _time.time() + 600\n", nuevo="    fin = _time.time() + 1200\n"),
    # La pausa del panel Tkinter: sin mirar, terminando sin 'hasta', sin avisar ni apagar el botón, o mirando cada 20 s.
    dict(id="e56-tk-pausa-no-mira", pruebas=[TK + "test_termina_sola_con_lo_que_dice_hasta"],
         viejo=MIRA_TK, nuevo="                sola = None\n"),
    dict(id="e56-tk-pausa-termina-sin-hasta", pruebas=[TK + "test_ya_lo_resolvi_como_antes"],
         viejo=MIRA_TK, nuevo='                sola = hasta() if hasta else "sola"\n'),
    dict(id="e56-tk-pausa-no-avisa", pruebas=[TK + "test_termina_sola_con_lo_que_dice_hasta"],
         viejo='                    self.cola.put(("pausa_sola", sola))\n', nuevo=""),
    dict(id="e56-tk-boton-sigue-encendido", pruebas=[TK + "test_la_cola_apaga_el_boton"],
         viejo=('                    elif tipo == "pausa_sola":\n'
                '                        self.btn_manual.configure(state="disabled")\n'),
         nuevo='                    elif tipo == "pausa_sola":\n                        pass\n'),
    dict(id="e56-tk-pausa-mira-cada-20-s", pruebas=[TK + "test_termina_sola_con_lo_que_dice_hasta"],
         viejo="            while not self.ev_pausa.wait(timeout=2):\n",
         nuevo="            while not self.ev_pausa.wait(timeout=20):\n"),
]

# --- Encargo 57 (CICLO-cortes-de-cma-y-pausas.md): el tamaño y tipo, el peso, el panel Reefer y «I Agree» de CMA-CGM
# cortan si el programa falla antes de terminarlos; cada pausa del panel Tkinter espera su propia respuesta; la pausa
# del deslizador termina sola solo con dos lecturas seguidas sin DataDome; «Detener» detiene también «Solo iniciar
# sesión»; y la prueba de puertos del encargo 52 ya no depende del reloj del equipo. ---
TAMANO_FALLA = C1 + "test_tamano_y_tipo_que_falla_corta"
TAMANO_ELEGIDO = C1 + "test_lo_que_falla_despues_de_elegir_el_tamano_sigue_como_antes"
PESO_FALLA = C1 + "test_peso_que_falla_corta"
REEFER_FALLA = C1 + "test_reefer_que_falla_antes_de_guardar_corta"
REEFER_GUARDADO = C1 + "test_lo_que_falla_entre_el_guardar_y_la_comprobacion_corta"      # encargo 58
AGREE_FALLA = C1 + "test_i_agree_que_falla_corta"
AGREE_MARCADA = C1 + "test_i_agree_como_antes"
CUATRO = C1 + "test_los_cuatro_que_fallan_dejan_la_fila_no_enviada_con_su_evidencia"
BUSCAN = C1 + "test_lo_que_buscan"
PASOS_CMA = C1 + "test_reservar_cma_corre_los_pasos_que_cortan_antes_de_la_guarda"
UNA_NO_BASTA = PS + "test_una_lectura_sin_datadome_no_basta"
VIGIA = PS + "test_el_vigia_cuenta_las_lecturas_seguidas"
CADA_PAUSA = TK + "test_cada_pausa_espera_su_respuesta"
DETENER_LOGIN = "test_consola.TestEjecutarLogin.test_solo_login_con_detener_no_sigue"
DETENER_LOGIN_WEB = CO + "test_detener_en_solo_iniciar_sesion"
TAMANO_CORTA = ('        if not sel_ok:\n'
                '            raise _cma_fallo("Tamaño y tipo de CMA", CMA_TAMANO_Y_TIPO, "abrir el desplegable o '
                'elegirla", e)\n')
REEFER_CORTA = ('        raise _cma_fallo("Ajustes Reefer de CMA", CMA_REEFER_GUARDADO,\n'
                '                         "abrir el panel, escribir la temperatura, guardarla o comprobar que quedó '
                'guardada", e)\n')
AGREE_CORTA = ('        if not marcada:\n'
               '            raise _cma_fallo("«I Agree» de CMA", CMA_CASILLA_I_AGREE, "llegar a ella o marcarla", e)\n')
FALLO = '    return ObjetivoNoEncontrado(paso, f"{buscaba}, porque el programa falló al {que} ({_texto_error(e)})")\n'
VIGIA_PAUSA = '                                "continuar.", hasta=_cma_vigia(page))\n'
WEB_LOGIN = "se_detuvo=_web_se_detuvo, al_abrir=al_abrir)"

MUTACIONES += [
    # Los cuatro pasos de CMA-CGM: lo que falla antes no corta, corta también después, o el paso se da por terminado
    # antes de terminarlo; reservar_cma sin el paso de «I Agree»; el motivo sin la falla o con otro texto.
    dict(id="e57-tamano-falla-sigue", pruebas=[TAMANO_FALLA, CUATRO], viejo=TAMANO_CORTA,
         nuevo=TAMANO_CORTA.replace("if not sel_ok:", "if False:")),
    dict(id="e57-tamano-elegido-corta", pruebas=[TAMANO_ELEGIDO], viejo=TAMANO_CORTA,
         nuevo=TAMANO_CORTA.replace("if not sel_ok:", "if True:")),
    dict(id="e57-tamano-sin-elegido-de-entrada", pruebas=[TAMANO_FALLA],
         viejo="    sel_ok = False\n    try:\n        abierto = False\n", nuevo="    try:\n        abierto = False\n"),
    dict(id="e57-peso-falla-sigue", pruebas=[PESO_FALLA, CUATRO],
         viejo='        raise _cma_fallo("Peso por contenedor de CMA", CMA_CAMPO_PESO, "buscarlo o escribirlo", e)\n',
         nuevo='        reg.info(f"peso err: {str(e)[:50]}")\n'),
    dict(id="e57-reefer-falla-sigue", pruebas=[REEFER_FALLA, CUATRO, REEFER_GUARDADO], viejo=REEFER_CORTA,
         nuevo='        reg.info(f"ajustes reefer err: {str(e)[:50]}")\n        return False\n'),
    # (Encargo 58: las dos que anclaban en la bandera «guardado» se retiraron con ella: lo que falla después del
    # «Guardar» ya no sigue. Las reemplazan e58-reefer-clic-se-traga y e58-reefer-espera-tras-guardar-se-traga.)
    dict(id="e57-agree-falla-sigue", pruebas=[AGREE_FALLA, CUATRO], viejo=AGREE_CORTA,
         nuevo=AGREE_CORTA.replace("if not marcada:", "if False:")),
    dict(id="e57-agree-marcada-corta", pruebas=[AGREE_MARCADA],
         viejo="        marcada = _cma_marcar_i_agree(page, reg)\n", nuevo="        _cma_marcar_i_agree(page, reg)\n"),
    dict(id="e57-reservar-sin-agree", pruebas=[PASOS_CMA], viejo="        _cma_i_agree_en_el_envio(page, reg)\n",
         nuevo=""),
    dict(id="e57-fallo-sin-la-falla",
         pruebas=[TAMANO_FALLA, PESO_FALLA, REEFER_FALLA, AGREE_FALLA, CUATRO, COMENTARIOS_FALLAN, FILA_COMENTARIOS],
         viejo=FALLO, nuevo='    return ObjetivoNoEncontrado(paso, f"{buscaba}, porque el programa falló al {que}")\n'),
    dict(id="e57-fallo-otro-texto", pruebas=[CUATRO, FILA_COMENTARIOS], viejo=FALLO,
         nuevo=FALLO.replace("porque el programa falló al", "porque falló al")),
    dict(id="e57-tamano-otro-texto", pruebas=[BUSCAN],
         viejo='CMA_TAMANO_Y_TIPO = "la opción «40\' Reefer High Cube» en el desplegable (por su texto)"\n',
         nuevo='CMA_TAMANO_Y_TIPO = "la opción del tamaño"\n'),
    dict(id="e57-peso-otro-texto", pruebas=[BUSCAN],
         viejo='CMA_CAMPO_PESO = "el campo «Peso por contenedor» (por su etiqueta o su placeholder «Peso»)"\n',
         nuevo='CMA_CAMPO_PESO = "el campo del peso"\n'),
    dict(id="e57-reefer-otro-texto", pruebas=[BUSCAN],
         viejo='CMA_REEFER_GUARDADO = ("el panel Reefer con su temperatura guardada',
         nuevo='CMA_REEFER_GUARDADO = ("el panel Reefer'),
    dict(id="e57-agree-otro-texto", pruebas=[BUSCAN],
         viejo='CMA_CASILLA_I_AGREE = "la casilla «I Agree» (por su texto)"\n',
         nuevo='CMA_CASILLA_I_AGREE = "la casilla"\n'),
    # La pausa del deslizador: con una lectura, sin volver a contar desde cero, el bloqueo también con dos, y el panel
    # mirando como en el encargo 56.
    dict(id="e57-vigia-una-lectura", pruebas=[DEJA_PASAR, UNA_NO_BASTA, VIGIA, A_MITAD_SOLA],
         viejo="CMA_LECTURAS_PARA_SEGUIR = 2\n", nuevo="CMA_LECTURAS_PARA_SEGUIR = 1\n"),
    dict(id="e57-vigia-no-vuelve-a-cero", pruebas=[UNA_NO_BASTA, VIGIA],
         viejo="        seguidas = seguidas + 1 if como == CMA_DEJO_PASAR else 0\n",
         nuevo="        seguidas = seguidas + 1 if como == CMA_DEJO_PASAR else seguidas\n"),
    dict(id="e57-vigia-bloqueo-con-dos", pruebas=[BLOQUEA, VIGIA],
         viejo="        return None if como == CMA_DEJO_PASAR and seguidas < CMA_LECTURAS_PARA_SEGUIR else como\n",
         nuevo="        return None if seguidas < CMA_LECTURAS_PARA_SEGUIR else como\n"),
    dict(id="e57-deslizador-con-una-lectura", pruebas=[DEJA_PASAR, UNA_NO_BASTA, A_MITAD_SOLA], viejo=VIGIA_PAUSA,
         nuevo='                                "continuar.", hasta=lambda: _cma_como_quedo(page))\n'),
    # La pausa del panel Tkinter sin apagar lo que dejó el «Ya lo resolví» anterior.
    dict(id="e57-tk-pausa-sin-apagar", pruebas=[CADA_PAUSA],
         viejo='            self.ev_pausa.clear()\n            self.cola.put(("pausa", mensaje))\n',
         nuevo='            self.cola.put(("pausa", mensaje))\n'),
    # «Detener» en «Solo iniciar sesión»: sin mirarlo entre un inicio de sesión y otro, esperando para cerrar, sin
    # pasarle el navegador al panel, sin decirlo, con la lista de los que faltan mal, la falla por «Detener» como error,
    # y el panel web sin pasarle «Detener», sin guardar o soltar el navegador, sin decir «Detenido.» o sin verlo.
    dict(id="e57-login-sin-mirar-detener", pruebas=[DETENER_LOGIN, DETENER_LOGIN_WEB],
         viejo="        for clave in navieras:\n            if se_detuvo and se_detuvo():\n                break\n",
         nuevo="        for clave in navieras:\n"),
    dict(id="e57-login-espera-con-detener", pruebas=[DETENER_LOGIN],
         viejo="        if detenido:\n            pass                                # con «Detener», se cierra sin "
               "esperar\n",
         nuevo="        if False:\n            pass\n"),
    dict(id="e57-login-sin-al-abrir", pruebas=[DETENER_LOGIN, DETENER_LOGIN_WEB],
         viejo="        if al_abrir:\n            al_abrir(ctx)\n", nuevo=""),
    dict(id="e57-login-sin-decir-detenido", pruebas=[DETENER_LOGIN, DETENER_LOGIN_WEB],
         viejo='            reg.paso("⛔ Detenido por el operador: cierro el navegador"\n',
         nuevo='            reg.paso("Fin"\n'),
    dict(id="e57-login-faltan-todas", pruebas=[DETENER_LOGIN, DETENER_LOGIN_WEB],
         viejo="            faltan = [NAVIERAS[c][0] for c in navieras if c in NAVIERAS and c not in resultados]\n",
         nuevo="            faltan = [NAVIERAS[c][0] for c in navieras if c in NAVIERAS]\n"),
    dict(id="e57-login-detener-como-error", pruebas=[DETENER_LOGIN],
         viejo="                if se_detuvo and se_detuvo():       # «Detener» le cerró el navegador: no es un error "
               "del portal\n",
         nuevo="                if False:\n"),
    dict(id="e57-web-login-sin-detener", pruebas=[DETENER_LOGIN_WEB], viejo=WEB_LOGIN,
         nuevo="al_abrir=al_abrir)"),
    dict(id="e57-web-login-sin-navegador", pruebas=[DETENER_LOGIN_WEB], viejo=WEB_LOGIN,
         nuevo="se_detuvo=_web_se_detuvo)"),
    dict(id="e57-web-login-sin-detenido", pruebas=[DETENER_LOGIN_WEB],
         viejo='        if _web_se_detuvo():\n            _westado("Detenido.")\n',
         nuevo='        if False:\n            _westado("Detenido.")\n'),
    dict(id="e57-web-login-navegador-queda", pruebas=[DETENER_LOGIN_WEB],
         viejo='            _WEB["ctx"] = None\n        if _web_se_detuvo():\n',
         nuevo="        if _web_se_detuvo():\n"),
    dict(id="e57-web-se-detuvo-nunca", pruebas=[DETENER_LOGIN_WEB],
         viejo='    return bool(_WEB.get("detener") and _WEB["detener"].is_set())\n', nuevo="    return False\n"),
    # El lanzador que no le vuelve a preguntar a quien tiene su puerto (la prueba ya no depende del reloj).
    dict(id="e57-lanzador-no-vuelve-a-preguntar", pruebas=[SE_SUELTA],
         viejo="            visto = _panel_en(p, espera=PANEL_ESPERA_LARGA)\n", nuevo="            visto = None\n"),
]


# --- Encargo 58 (CICLO-temperatura-y-puerto.md): después del «Guardar» del panel Reefer, CMA-CGM comprueba en la página
# que el portal guardó la temperatura (si no, NO ENVIADA); la mercancía corta si el programa falla antes de elegirla; y
# el lanzador vuelve a probar el puerto unos instantes antes de saltarlo. ---
FALTA_T = C1 + "test_lo_que_falta_para_dar_la_temperatura_por_guardada"
JS_T = C1 + "test_js_temperatura_guardada_por_lo_medido"
SIN_T = C1 + "test_reefer_sin_la_temperatura_guardada_corta"
CON_T = C1 + "test_reefer_con_la_temperatura_guardada_sigue"
COMPRUEBA_FALLA = C1 + "test_la_comprobacion_que_falla_corta"
MERCANCIA_FALLA = C1 + "test_mercancia_que_falla_corta"
FILA_E58 = C1 + "test_la_temperatura_y_la_mercancia_dejan_la_fila_no_enviada_con_su_evidencia"
ORDEN_T = C1 + "test_la_comprobacion_va_tras_la_evidencia_y_antes_del_escape"
EV_REEFER = "test_evidencia.TestEvidenciaReefer.test_el_panel_abierto_y_tras_guardarlo"
WINDOWS = ARR + "test_puerto_que_windows_suelta_un_instante_despues"
UNOS_INSTANTES = ARR + "test_puerto_se_suelta_prueba_unos_instantes"
COMPRUEBA = "        _cma_temperatura_guardada(page, reg, temp)\n"
PASO_4 = "        # 4. Que el portal la guardó, con las señales medidas en esa evidencia (encargo 58)\n"
EVIDENCIA_G = ('        _evidencia_antes_de_la_guarda(page, reg, f"cma_f{f}_reefer_guardado", "tras guardar el panel '
               'Reefer",\n                                      completa=False, plazo_ms=CMA_PLAZO_MS)\n')
ENTRE_LECTURAS = "        if n < CMA_LECTURAS_TEMPERATURA:\n            esperar(page, 0.5)\n"
LO_DICE = ('            reg.info(f"temperatura guardada: la página muestra {temp} °C en «Operando en», sin el panel ni '
           '«to "\n')
NUMERO_T = '    m = _re_mk.fullmatch(r"(-?\\d+(?:[.,]\\d+)?)\\s*°\\s*C", temperaturas[0])\n'

MUTACIONES += [
    # La comprobación: sin ella, antes de la evidencia, tragándose su falla, o lo de entre el «Guardar» y ella que no
    # corta (el clic o la espera que fallan).
    dict(id="e58-reefer-sin-comprobar", pruebas=[SIN_T, CON_T, FILA_E58, EV_REEFER, ORDEN_T], viejo=COMPRUEBA,
         nuevo=""),
    dict(id="e58-comprobar-antes-de-la-evidencia", pruebas=[ORDEN_T, EV_REEFER], viejo=EVIDENCIA_G + PASO_4 + COMPRUEBA,
         nuevo=PASO_4 + COMPRUEBA + EVIDENCIA_G),
    dict(id="e58-escape-que-falla-corta", pruebas=[CON_T],
         viejo=(COMPRUEBA + "        # Asegurar que no quede ningún modal ni popup abierto\n        try:\n"
                '            page.keyboard.press("Escape")\n            esperar(page, 0.4)\n        except Exception:\n'
                "            pass\n"),
         nuevo=COMPRUEBA + '        page.keyboard.press("Escape")\n        esperar(page, 0.4)\n'),
    dict(id="e58-comprobacion-se-traga-la-falla", pruebas=[COMPRUEBA_FALLA], viejo=COMPRUEBA,
         nuevo="        try:\n    " + COMPRUEBA + "        except Exception:\n            pass\n"),
    dict(id="e58-reefer-clic-se-traga", pruebas=[REEFER_FALLA],
         viejo="        btn_g.click(timeout=4000)\n",
         nuevo="        try:\n            btn_g.click(timeout=4000)\n        except Exception:\n            pass\n"),
    dict(id="e58-reefer-espera-tras-guardar-se-traga", pruebas=[REEFER_GUARDADO],
         viejo='        reg.info("ajustes reefer guardados")\n        esperar(page, 1.5)\n',
         nuevo='        reg.info("ajustes reefer guardados")\n        try:\n            esperar(page, 1.5)\n'
               '        except Exception:\n            pass\n'),
    # Lo que falta: cada señal que no se mira, o se mira de otra forma.
    dict(id="e58-falta-sin-el-cajon", pruebas=[FALTA_T, SIN_T],
         viejo='    if leido.get("cajones"):\n        return "el panel Reefer sigue en la página"\n', nuevo=""),
    dict(id="e58-falta-sin-un-solo-boton", pruebas=[FALTA_T],
         viejo='    if leido.get("botones") != 1:\n', nuevo='    if not leido.get("botones"):\n'),
    dict(id="e58-falta-sin-la-fila", pruebas=[FALTA_T],
         viejo='    if leido.get("insignias") is None:\n', nuevo="    if False:\n"),
    dict(id="e58-falta-to-complete-no-cuenta", pruebas=[FALTA_T, SIN_T],
         viejo='    if any(_re_mk.search(r"to\\s*complete", i or "", _re_mk.I) for i in leido["insignias"]):\n',
         nuevo="    if False:\n"),
    dict(id="e58-falta-ninguna-temperatura-basta", pruebas=[FALTA_T],
         viejo="    if len(temperaturas) != 1:\n", nuevo="    if not temperaturas:\n"),
    dict(id="e58-falta-otra-temperatura-pasa", pruebas=[FALTA_T, SIN_T],
         viejo='    if float(m.group(1).replace(",", ".")) != float(q.group(1).replace(",", ".")):\n',
         nuevo="    if False:\n"),
    dict(id="e58-falta-sin-comparar-pasa", pruebas=[FALTA_T],
         viejo="    if not m or not q:\n", nuevo='    if not m or not q:\n        return ""\n'),
    dict(id="e58-falta-sin-la-coma", pruebas=[FALTA_T], viejo=NUMERO_T,
         nuevo=NUMERO_T.replace("[.,]", "[.]")),
    # El JavaScript: otro cajón, cualquier rótulo, sin mirar el <dd>, la fila del primer botón, otra insignia.
    dict(id="e58-js-otro-cajon", pruebas=[JS_T], viejo="document.querySelectorAll('.reefer-drawer').length",
         nuevo="document.querySelectorAll('.el-drawer').length"),
    dict(id="e58-js-cualquier-rotulo", pruebas=[JS_T], viejo=".filter(dt => txt(dt) === 'Operando en')",
         nuevo=".filter(dt => txt(dt).includes('Operando en'))"),
    dict(id="e58-js-sin-mirar-el-dd", pruebas=[JS_T],
         viejo="(dt.nextElementSibling && dt.nextElementSibling.tagName === 'DD')",
         nuevo="(dt.nextElementSibling)"),
    dict(id="e58-js-fila-del-primer-boton", pruebas=[JS_T],
         viejo="botones.length === 1 ? botones[0].closest(", nuevo="botones.length ? botones[0].closest("),
    dict(id="e58-js-otra-insignia", pruebas=[JS_T], viejo="botones[0].closest('.capsule-container')",
         nuevo="botones[0].closest('.row')"),
    # Las lecturas: una sola, cada 2 s, una espera de más tras la última, o sin decirlo en log.txt.
    dict(id="e58-una-lectura", pruebas=[SIN_T, CON_T], viejo="CMA_LECTURAS_TEMPERATURA = 20\n",
         nuevo="CMA_LECTURAS_TEMPERATURA = 1\n"),
    dict(id="e58-lecturas-cada-2-s", pruebas=[SIN_T, CON_T], viejo=ENTRE_LECTURAS,
         nuevo=ENTRE_LECTURAS.replace("0.5", "2.0")),
    dict(id="e58-espera-tras-la-ultima", pruebas=[SIN_T], viejo=ENTRE_LECTURAS,
         nuevo="        esperar(page, 0.5)\n"),
    dict(id="e58-sin-decir-guardada", pruebas=[CON_T], viejo=LO_DICE,
         nuevo=LO_DICE.replace("temperatura guardada:", "comprobada:")),
    # La mercancía que falla y sigue, y lo que buscan con otro texto.
    dict(id="e58-mercancia-falla-sigue", pruebas=[MERCANCIA_FALLA, FILA_E58],
         viejo='        raise _cma_fallo("Mercancía de CMA", CMA_MERCANCIA, "buscarla o elegirla", e)\n',
         nuevo='        reg.info(f"mercancía err: {str(e)[:50]}")\n'),
    dict(id="e58-mercancia-otro-texto", pruebas=[BUSCAN, C1 + "test_tamano_y_mercancia_no_eligen_con_el_teclado"],
         viejo='CMA_MERCANCIA = "la sugerencia que dice «030313» en la lista (por su texto)"\n',
         nuevo='CMA_MERCANCIA = "la mercancía"\n'),
    dict(id="e58-temperatura-otro-texto", pruebas=[BUSCAN],
         viejo='CMA_TEMPERATURA_GUARDADA = ("la temperatura guardada en la página',
         nuevo='CMA_TEMPERATURA_GUARDADA = ("la temperatura'),
    # El lanzador: una sola prueba del puerto, sin esperar, cada medio segundo, o sin ver que se soltó.
    dict(id="e58-lanzador-prueba-una-vez", pruebas=[WINDOWS],
         viejo="            if visto is None and not _puerto_se_suelta(p):\n",
         nuevo="            if visto is None and not _puerto_libre(p):\n"),
    dict(id="e58-se-suelta-sin-esperar", pruebas=[UNOS_INSTANTES, WINDOWS], viejo="PUERTO_SE_SUELTA = 1.0\n",
         nuevo="PUERTO_SE_SUELTA = 0.0\n"),
    dict(id="e58-se-suelta-cada-medio-segundo", pruebas=[UNOS_INSTANTES],
         viejo="            return False\n        time.sleep(0.05)\n",
         nuevo="            return False\n        time.sleep(0.5)\n"),
    dict(id="e58-se-suelta-no-lo-ve", pruebas=[UNOS_INSTANTES, WINDOWS],
         viejo="        if _puerto_libre(puerto):\n            return True\n",
         nuevo="        if False:\n            return True\n"),
]

# --- Encargo 59 (CICLO-tarde-08-10-y-cantidad.md): la cantidad de CMA no se escribe; el programa comprueba que el campo
# «Cantidad» dice 1, y si no, la fila queda NO ENVIADA (decisión de Marcelo).
FALTA_C = C1 + "test_lo_que_falta_para_decir_un_contenedor"
JS_C = C1 + "test_js_cantidad_por_lo_medido"
NO_UNO = C1 + "test_cantidad_que_no_dice_uno_corta"
UNO = C1 + "test_cantidad_que_dice_uno_sigue"
LEE_FALLA = C1 + "test_la_lectura_de_la_cantidad_que_falla_corta"
FILA_E59 = C1 + "test_la_cantidad_deja_la_fila_no_enviada_con_su_evidencia"
ORDEN_C = C1 + "test_la_cantidad_va_tras_el_tamano_y_antes_del_peso_sin_escribirla"
LLAMA_C = "    _cma_cantidad_es_uno(page, reg)\n"
PASO_3 = "    # 3. Peso por contenedor (el de config.json)\n"
PASO_4_M = "    # 4. Mercancía (HS Code: 030313 -> Frozen Atlantic Salmon...)\n"
ENTRE_C = "        if n < CMA_LECTURAS_CANTIDAD:\n            esperar(page, 0.5)\n"
CORTA_C = ('    raise ObjetivoNoEncontrado("Cantidad de CMA", f"{CMA_CANTIDAD}: {falta} (lo leí '
           '{CMA_LECTURAS_CANTIDAD} veces, "\n                                                  f"cada 0,5 s)")\n')
LO_DICE_C = ('            reg.info(f"cantidad: el campo «Cantidad» dice 1, un contenedor; no la escribo (lectura '
             '{n})")\n')
FILTRO_C = "return lab && txt(lab) === 'Cantidad'; })\n"

MUTACIONES += [
    # La comprobación: sin ella, antes del tamaño, después del peso, o con la cantidad escrita como antes.
    dict(id="e59-sin-comprobar-la-cantidad", pruebas=[NO_UNO, UNO, FILA_E59, ORDEN_C], viejo=LLAMA_C, nuevo=""),
    dict(id="e59-cantidad-antes-del-tamano", pruebas=[NO_UNO, ORDEN_C],
         cambios=[(LLAMA_C, ""), ('    reg.paso("CMA · Completando información extra de carga...")\n',
                                  '    reg.paso("CMA · Completando información extra de carga...")\n' + LLAMA_C)]),
    dict(id="e59-cantidad-despues-del-peso", pruebas=[NO_UNO, ORDEN_C],
         cambios=[(LLAMA_C, ""), (PASO_4_M, LLAMA_C + PASO_4_M)]),
    dict(id="e59-escribe-la-de-la-fila", pruebas=[UNO, ORDEN_C],
         viejo=LLAMA_C + "\n" + PASO_3,
         nuevo=(LLAMA_C + "    page.locator(\".el-form-item:has-text('Cantidad') input\").first.fill(\n"
                "        str(reserva.get(\"cant\") or 1))\n\n" + PASO_3)),
    # La lectura que falla y se traga, o con otro texto; el corte que no corta; el «dice 1» que no se mira.
    dict(id="e59-lectura-se-traga-la-falla", pruebas=[LEE_FALLA],
         viejo='            raise _cma_fallo("Cantidad de CMA", CMA_CANTIDAD, "leerla", e)\n',
         nuevo="            return\n"),
    dict(id="e59-lectura-falla-con-otro-texto", pruebas=[LEE_FALLA],
         viejo='            raise _cma_fallo("Cantidad de CMA", CMA_CANTIDAD, "leerla", e)\n',
         nuevo='            raise _cma_fallo("Cantidad de CMA", CMA_CANTIDAD, "escribirla", e)\n'),
    dict(id="e59-cantidad-no-corta", pruebas=[NO_UNO, FILA_E59], viejo=CORTA_C,
         nuevo='    reg.info(f"cantidad: {falta}")\n'),
    dict(id="e59-sin-mirar-lo-que-falta", pruebas=[NO_UNO, FILA_E59],
         viejo="        if not falta:\n            reg.info(f\"cantidad:",
         nuevo="        if True:\n            reg.info(f\"cantidad:"),
    # Lo que falta: varios campos o varias casillas que pasan, sin quitar los espacios, cualquier valor, un número que
    # se lee, lo que no es una lista, o None como texto.
    dict(id="e59-falta-varios-campos-pasan", pruebas=[FALTA_C, NO_UNO],
         viejo="    if len(items) != 1:\n", nuevo="    if not items:\n"),
    dict(id="e59-falta-varias-casillas-pasan", pruebas=[FALTA_C],
         viejo="    if len(valores) != 1:\n", nuevo="    if not valores:\n"),
    dict(id="e59-falta-sin-quitar-espacios", pruebas=[FALTA_C],
         viejo='    valor = str(valores[0] if valores[0] is not None else "").strip()\n',
         nuevo='    valor = str(valores[0] if valores[0] is not None else "")\n'),
    dict(id="e59-falta-cualquier-valor", pruebas=[FALTA_C, NO_UNO, FILA_E59],
         viejo='    if valor != "1":\n', nuevo="    if not valor:\n"),
    dict(id="e59-falta-por-su-numero", pruebas=[FALTA_C],
         viejo='    if valor != "1":\n', nuevo='    if valor.lstrip("0") != "1":\n'),
    dict(id="e59-falta-cualquier-coleccion", pruebas=[FALTA_C],
         viejo="    items = leido if isinstance(leido, list) else []\n", nuevo="    items = list(leido or [])\n"),
    dict(id="e59-falta-none-como-texto", pruebas=[FALTA_C],
         viejo='    valor = str(valores[0] if valores[0] is not None else "").strip()\n',
         nuevo="    valor = str(valores[0]).strip()\n"),
    # El JavaScript: la etiqueta por una parte, sin juntar los espacios, solo input, el primero, o null como texto.
    dict(id="e59-js-etiqueta-por-una-parte", pruebas=[JS_C], viejo=FILTRO_C,
         nuevo="return lab && txt(lab).startsWith('Cantidad'); })\n"),
    dict(id="e59-js-sin-juntar-espacios", pruebas=[JS_C],
         viejo="' ').trim();\n    return [...document.querySelectorAll('.el-form-item')]",
         nuevo="' ');\n    return [...document.querySelectorAll('.el-form-item')]"),
    dict(id="e59-js-solo-input", pruebas=[JS_C], viejo="it.querySelectorAll('input, select, textarea')",
         nuevo="it.querySelectorAll('input')"),
    dict(id="e59-js-solo-el-primero", pruebas=[JS_C], viejo=FILTRO_C,
         nuevo="return lab && txt(lab) === 'Cantidad'; }).slice(0, 1)\n"),
    dict(id="e59-js-null-como-texto", pruebas=[JS_C], viejo="c.value == null ? '' : String(c.value)",
         nuevo="String(c.value)"),
    # Las lecturas: una sola, cada 2 s, una espera de más tras la última, o sin decirlo en log.txt.
    dict(id="e59-una-lectura", pruebas=[NO_UNO, UNO], viejo="CMA_LECTURAS_CANTIDAD = 6\n",
         nuevo="CMA_LECTURAS_CANTIDAD = 1\n"),
    dict(id="e59-lecturas-cada-2-s", pruebas=[NO_UNO, UNO], viejo=ENTRE_C, nuevo=ENTRE_C.replace("0.5", "2.0")),
    dict(id="e59-espera-tras-la-ultima", pruebas=[NO_UNO], viejo=ENTRE_C, nuevo="        esperar(page, 0.5)\n"),
    dict(id="e59-sin-decir-la-cantidad", pruebas=[UNO], viejo=LO_DICE_C,
         nuevo=LO_DICE_C.replace("cantidad: el campo", "el campo")),
    # Lo que busca, con otro texto (la prueba de la fila arma su motivo con la constante: no la ve).
    dict(id="e59-cantidad-otro-texto", pruebas=[BUSCAN],
         viejo='CMA_CANTIDAD = "el campo «Cantidad» con 1 contenedor (cada fila de la planilla es una reserva de un '
               'contenedor)"\n',
         nuevo='CMA_CANTIDAD = "el campo «Cantidad»"\n'),
]

# --- Encargo 60 (CICLO-actualizar-desde-estable.md): al abrir, los equipos de los colegas traen la última versión de la
# rama «estable» (actualizar.py), sin pisar nada propio; el de desarrollo, en «main», no se actualiza (decisión de
# Marcelo).
TA = "test_actualizar.TestActualizar."
TRAE = TA + "test_trae_la_version_estable_sin_tocar_lo_propio_del_equipo"
AL_DIA = TA + "test_al_dia_no_cambia_nada"
EN_MAIN = TA + "test_el_equipo_de_desarrollo_en_main_no_se_actualiza_ni_busca"
SOLO_ESTABLE = TA + "test_solo_avanza_lo_que_marcelo_pone_en_estable"
SIN_RED = TA + "test_sin_red_abre_con_la_que_tiene"
CAMBIO_PROPIO = TA + "test_un_cambio_en_un_archivo_del_programa_no_se_pisa"
COMMIT_PROPIO = TA + "test_un_commit_propio_no_se_pierde"
IGNORADO = TA + "test_un_archivo_propio_ignorado_donde_la_version_pone_uno_no_se_pisa"
EN_EL_CAMINO = TA + "test_una_carpeta_o_un_archivo_propio_en_el_camino_no_se_pisan"
YA_VERSIONADO = TA + "test_lo_que_ya_versionaba_la_vieja_no_cuenta_como_propio"
OPERACION = TA + "test_una_operacion_de_git_a_medias_no_se_toca"
ABIERTO = TA + "test_un_archivo_abierto_vuelve_todo_a_la_version_que_tenia"
CLAVES = TA + "test_no_pide_ni_guarda_credenciales"
NO_CLON = TA + "test_una_carpeta_que_no_es_un_clon_no_se_actualiza"
SIN_ARGUMENTOS = TA + "test_sin_argumentos_actualiza_su_propia_carpeta"
TL = "test_actualizar.TestLosLanzadores."
BAT_BLOQUE = TL + "test_el_bat_actualiza_antes_de_abrir_y_todo_en_un_bloque"
BAT_CMD = TL + "test_en_cmd_abre_la_version_nueva_aunque_la_actualizacion_reescriba_el_bat"
GITIGNORE_ACT = TL + "test_gitignore_versiona_el_actualizador"
TP = "test_actualizar.TestAvisoEnElPanel."
AVISO_FRESCO = TP + "test_lo_dice_si_es_de_este_inicio"
AVISO_MAL = TP + "test_sin_archivo_o_malformado_no_dice_nada"
AVISO_AL_ABRIR = TP + "test_el_panel_lo_muestra_al_abrir"
ACT = "actualizar.py"
CORRE_ACT = "  python actualizar.py\n"

MUTACIONES += [
    # La rama: cualquiera se actualiza, se actualiza main, o se trae main.
    dict(id="e60-cualquier-rama", archivo=ACT, pruebas=[EN_MAIN], viejo="    if rama != RAMA:\n",
         nuevo="    if not rama:\n"),
    dict(id="e60-la-rama-main", archivo=ACT, pruebas=[TRAE, EN_MAIN], viejo='RAMA = "estable"\n',
         nuevo='RAMA = "main"\n'),
    dict(id="e60-trae-main", archivo=ACT, pruebas=[SOLO_ESTABLE],
         viejo='f"+refs/heads/{RAMA}:refs/remotes/{REMOTO}/{RAMA}"',
         nuevo='f"+refs/heads/main:refs/remotes/{REMOTO}/{RAMA}"'),
    # La búsqueda: sin buscar, sin ver que falló, o con el ayudante de credenciales del equipo.
    dict(id="e60-no-busca", archivo=ACT, pruebas=[TRAE],
         viejo='    codigo, _, error = g("fetch", "--no-tags", "--quiet", REMOTO,\n',
         nuevo='    codigo, error = 0, ""\n    (lambda *a, **k: None)(REMOTO,\n'),
    dict(id="e60-sin-red-sigue", archivo=ACT, pruebas=[SIN_RED],
         viejo='    if codigo:\n        return sin_actualizar(f"no pude buscar la versión nueva',
         nuevo='    if False:\n        return sin_actualizar(f"no pude buscar la versión nueva'),
    dict(id="e60-con-el-ayudante-de-claves", archivo=ACT, pruebas=[CLAVES],
         viejo='SIN_CLAVES = ("-c", "credential.helper=", "-c", "core.askPass=")\n',
         nuevo='SIN_CLAVES = ("-c", "core.askPass=")\n'),
    # Lo que impide actualizar: un clon que no es, una operación a medias, commits o cambios propios, lo ocupado.
    dict(id="e60-no-mira-si-es-un-clon", archivo=ACT, pruebas=[NO_CLON],
         viejo='    if not (carpeta / ".git").exists():\n', nuevo="    if False:\n"),
    dict(id="e60-sin-operaciones", archivo=ACT, pruebas=[OPERACION],
         viejo=('OPERACIONES = ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "BISECT_LOG", "rebase-merge", '
                '"rebase-apply",\n               "index.lock")\n'),
         nuevo="OPERACIONES = ()\n"),
    dict(id="e60-al-dia-sin-mirar", archivo=ACT, pruebas=[AL_DIA], viejo="    if nuevo == viejo:\n",
         nuevo="    if False:\n"),
    dict(id="e60-commits-propios-sigue", archivo=ACT, pruebas=[COMMIT_PROPIO],
         viejo='    if g("merge-base", "--is-ancestor", viejo, nuevo)[0] != 0:\n', nuevo="    if False:\n"),
    dict(id="e60-cambios-propios-sigue", archivo=ACT, pruebas=[CAMBIO_PROPIO], viejo="    if sucias:\n",
         nuevo="    if False:\n"),
    dict(id="e60-no-mira-lo-ocupado", archivo=ACT, pruebas=[IGNORADO, EN_EL_CAMINO],
         viejo="    tramo = ocupada(g, viejo, nuevo)\n", nuevo="    tramo = None\n"),
    dict(id="e60-ocupada-sin-las-carpetas-de-la-vieja", archivo=ACT, pruebas=[YA_VERSIONADO],
         viejo="            if tramo in viejas or (i < len(partes) and tramo in carpetas):\n",
         nuevo="            if tramo in viejas:\n"),
    dict(id="e60-ocupada-solo-la-ruta-entera", archivo=ACT, pruebas=[EN_EL_CAMINO],
         viejo="        for i in range(1, len(partes) + 1):\n",
         nuevo="        for i in range(len(partes), len(partes) + 1):\n"),
    # La escritura a medias: sin volver, o volviendo a la otra versión.
    dict(id="e60-no-vuelve", archivo=ACT, pruebas=[ABIERTO],
         viejo="            faltan = igualar(g, en, nuevo if en == viejo else viejo, rutas)\n",
         nuevo="            faltan = []\n"),
    dict(id="e60-vuelve-a-la-otra", archivo=ACT, pruebas=[ABIERTO],
         viejo="            faltan = igualar(g, en, nuevo if en == viejo else viejo, rutas)\n",
         nuevo="            faltan = igualar(g, nuevo, viejo, rutas)\n"),
    # Lo que dice, y de qué carpeta.
    dict(id="e60-otro-texto", archivo=ACT, pruebas=[TRAE],
         viejo='"actualizada", f"⟳ AQUASHIELD se actualizó a la versión estable {nuevo[:7]} "',
         nuevo='"actualizada", f"AQUASHIELD se actualizó {nuevo[:7]} "'),
    dict(id="e60-la-carpeta-de-donde-lo-llaman", archivo=ACT, pruebas=[SIN_ARGUMENTOS],
         viejo="    carpeta = Path(__file__).resolve().parent\n", nuevo="    carpeta = Path.cwd()\n"),
    # Los .bat: sin el actualizador, sin el bloque, o abriendo aunque quedó a medias.
    dict(id="e60-bat-sin-actualizar", archivo="Iniciar AQUASHIELD.bat", pruebas=[BAT_BLOQUE, BAT_CMD],
         viejo=CORRE_ACT, nuevo=""),
    dict(id="e60-bat-emision-sin-actualizar", archivo="Iniciar AQUASHIELD_EMISION.bat", pruebas=[BAT_BLOQUE, BAT_CMD],
         viejo=CORRE_ACT, nuevo=""),
    dict(id="e60-bat-sin-bloque", archivo="Iniciar AQUASHIELD.bat", pruebas=[BAT_BLOQUE, BAT_CMD],
         cambios=[('cd /d "%~dp0"\n(\n', 'cd /d "%~dp0"\n'), ('  exit /b 0\n)\n', '  exit /b 0\n')]),
    dict(id="e60-bat-abre-a-medias", archivo="Iniciar AQUASHIELD_EMISION.bat", pruebas=[BAT_BLOQUE],
         viejo="  if errorlevel 3 (\n    pause\n    exit /b 3\n  )\n", nuevo=""),
    dict(id="e60-sin-versionar-el-actualizador", archivo=".gitignore", pruebas=[GITIGNORE_ACT],
         viejo="!/actualizar.py\n", nuevo=""),
    # El aviso del panel: de cualquier inicio, sin mirar el texto, sin juntar sus espacios, o sin mostrarlo.
    dict(id="e60-aviso-de-cualquier-inicio", pruebas=[AVISO_FRESCO], viejo="AVISO_ACTUALIZACION_SEG = 600\n",
         nuevo="AVISO_ACTUALIZACION_SEG = 6000\n"),
    dict(id="e60-aviso-del-futuro", pruebas=[AVISO_FRESCO],
         viejo="    if not 0 <= (time.time() if ahora is None else ahora) - cuando <= AVISO_ACTUALIZACION_SEG:\n",
         nuevo="    if not (time.time() if ahora is None else ahora) - cuando <= AVISO_ACTUALIZACION_SEG:\n"),
    dict(id="e60-aviso-sin-mirar-el-texto", pruebas=[AVISO_MAL],
         viejo="    if not isinstance(texto, str) or not texto.strip():\n", nuevo="    if False:\n"),
    dict(id="e60-aviso-sin-juntar-espacios", pruebas=[AVISO_FRESCO], viejo='    return " ".join(texto.split())[:400]\n',
         nuevo="    return texto[:400]\n"),
    dict(id="e60-el-panel-no-lo-muestra", pruebas=[AVISO_AL_ABRIR],
         viejo="    aviso = _aviso_de_actualizacion()\n    if aviso:\n        _avisar_en_pantalla_y_log(aviso)\n",
         nuevo=""),
]

# --- Encargo 61 (CICLO-clon-nuevo-y-config.md): un clon recién hecho llega a «Modo Seguro Activo» y carga sus
# credenciales desde el panel; si algo falta, el panel dice qué y cómo resolverlo, y nunca queda mudo (decisión de
# Marcelo). Sin config.json, el panel lo crea desde config.example.json; si no puede leerlo, lo dice a la vista; y sin
# playwright u openpyxl, el .bat lo dice y espera.
SC = "test_web.TestPanelSinConfig."
CREA = SC + "test_lo_crea_desde_la_plantilla_y_lo_dice"
CRED_CREA = SC + "test_credenciales_sin_config_tambien_lo_crean"
NO_PISA = SC + "test_no_pisa_un_config_que_aparece_entretanto"
REINTENTA = SC + "test_reintenta_si_windows_niega_el_renombre"
NO_CREA = SC + "test_si_no_puede_crearlo_lo_dice"
PLANTILLA_ROTA = SC + "test_plantilla_que_no_se_lee"
ROTO = SC + "test_config_que_no_se_lee_lo_dice_sin_mostrarlo"
NO_ABRE = SC + "test_config_que_no_se_abre_lo_dice"
CANDADO_NO_CREA = SC + "test_el_candado_y_la_consola_no_lo_crean"
MODO_ARMAR = "test_envio.TestLecturaDelPanel.test_el_panel_vuelve_a_leer_su_modo_antes_de_armar"
VF = "test_envio.TestLoQueFaltaALaVista."
SE_VE = VF + "test_el_aviso_se_ve_y_va_al_registro"
AL_CARGAR = VF + "test_al_cargar_dice_lo_que_falta"
CUADRO = VF + "test_credenciales_sin_leer_abren_el_cuadro_con_el_motivo"
BOTONES = VF + "test_armar_y_entrar_avisan_a_la_vista"
BAT_LIB = TL + "test_sin_las_librerias_lo_dice_y_no_abre"
# Desde el encargo 84 el .bat no mira las librerías: lo hace el preparador, que sale con 11 si no se puede abrir. El .bat
# frena con ese código (FRENO_BAT). Las mutaciones e61 de los .bat, sobre ese freno.
FRENO_BAT = "  if errorlevel 11 (\n    echo.\n    pause\n    exit /b 1\n  )\n"

MUTACIONES += [
    # El servidor: no lo crea, no lo dice, no limpia el aviso, lo reescribe en vez de copiarlo, lo pisa o no reintenta.
    dict(id="e61-no-lo-crea", pruebas=[CREA, CRED_CREA],
         viejo="    if not ruta.exists():\n        _crear_config_desde_el_ejemplo(ruta)\n", nuevo=""),
    dict(id="e61-la-pagina-no-sabe-que-lo-creo", pruebas=[CREA], viejo='"aviso": _CONFIG["creada"] or "",',
         nuevo='"aviso": "",'),
    dict(id="e61-el-aviso-no-se-limpia", pruebas=[CREA],
         viejo='                    _CONFIG["creada"] = None        # ya tiene credenciales', nuevo="#"),
    dict(id="e61-crearlo-sin-decirlo", pruebas=[CREA], viejo="    _avisar_en_pantalla_y_log(CONFIG_CREADA)\n",
         nuevo=""),
    dict(id="e61-lo-reescribe", pruebas=[CREA], viejo="        tmp.write_bytes(datos)\n",
         nuevo="        tmp.write_bytes(json.dumps(plantilla).encode())\n"),
    dict(id="e61-credenciales-sin-crearlo", pruebas=[CRED_CREA],
         viejo='                if u.path == "/api/credenciales":\n                    cfg = _config_del_panel()\n',
         nuevo='                if u.path == "/api/credenciales":\n                    cfg = cargar_config()\n'),
    dict(id="e61-guardar-sin-crearlo", pruebas=[CRED_CREA],
         viejo='"falta el nombre del operador"}, 400)\n                    cfg = _config_del_panel()\n',
         nuevo='"falta el nombre del operador"}, 400)\n                    cfg = cargar_config()\n'),
    dict(id="e61-pisa-el-que-aparece", pruebas=[NO_PISA], viejo="                _os.rename(tmp, ruta)\n",
         nuevo="                _os.replace(tmp, ruta)\n"),
    dict(id="e61-no-reintenta", pruebas=[REINTENTA],
         viejo="def _crear_config_desde_el_ejemplo(ruta, intentos=20, pausa=0.05):",
         nuevo="def _crear_config_desde_el_ejemplo(ruta, intentos=1, pausa=0.05):"),
    dict(id="e61-deja-el-temporal", pruebas=[NO_CREA],
         viejo="        if tmp.exists():\n            try:\n                tmp.unlink()\n",
         nuevo="        if False:\n            try:\n                tmp.unlink()\n"),
    dict(id="e61-sin-crear-otro-aviso", pruebas=[NO_CREA],
         viejo='"Falta config.json y no pude crearlo en la carpeta del programa "',
         nuevo='"No pude crear config.json "'),
    dict(id="e61-plantilla-sin-forma", pruebas=[PLANTILLA_ROTA], viejo="    if not isinstance(plantilla, dict):\n",
         nuevo="    if plantilla is None:\n"),
    dict(id="e61-plantilla-rota-sin-motivo", pruebas=[PLANTILLA_ROTA], viejo="    except (OSError, ValueError):\n",
         nuevo="    except OSError:\n"),
    # Lo que no se lee: sin el motivo, mostrando el texto del archivo, o sin mirar la forma.
    dict(id="e61-muestra-el-archivo", pruebas=[ROTO], viejo='f"{e.colno}: {e.msg}). Corrígelo',
         nuevo='f"{e.colno}: {e.msg}; {e.doc[:120]}). Corrígelo'),
    dict(id="e61-sin-el-motivo-de-la-codificacion", pruebas=[ROTO],
         viejo="    except UnicodeDecodeError:\n        raise ConfigDelPanel(",
         nuevo="    except UnicodeError:\n        raise\n        raise ConfigDelPanel("),
    dict(id="e61-sin-mirar-las-opciones", pruebas=[ROTO],
         viejo='\n            and isinstance(cfg.get("opciones", {}), dict)):', nuevo="):"),
    dict(id="e61-sin-mirar-la-forma", pruebas=[ROTO], viejo='    if not (isinstance(cfg, dict) and isinstance(',
         nuevo='    if False and (isinstance(cfg, dict) and isinstance('),
    dict(id="e61-no-se-abre-sin-motivo", pruebas=[NO_ABRE],
         viejo='"No pude abrir config.json: {e.strerror or type(e).__name__}. Cierra el programa que "',
         nuevo='"No pude abrir config.json: {e}. Cierra el programa que "'),
    dict(id="e61-el-candado-lo-crea", pruebas=[CANDADO_NO_CREA],
         viejo='    ruta = BASE / "config.json"\n    if not ruta.exists():\n        raise FileNotFoundError(',
         nuevo=('    ruta = BASE / "config.json"\n    if not ruta.exists():\n'
                '        _crear_config_desde_el_ejemplo(ruta)\n'
                '    if not ruta.exists():\n        raise FileNotFoundError(')),
    # La página: el aviso no se ve, no dice lo que dijo el panel, no lo pinta al cargar, ni en Credenciales ni en los
    # botones.
    dict(id="e61-aviso-que-no-se-esconde", pruebas=[SE_VE], viejo="  a.hidden = !texto;\n",
         nuevo="  a.hidden = false;\n"),
    dict(id="e61-aviso-siempre-alerta", pruebas=[SE_VE],
         viejo='  feed(texto, cls || "f-alerta", etiqueta || "REVISAR");',
         nuevo='  feed(texto, "f-alerta", "REVISAR");'),
    dict(id="e61-sin-el-aviso-en-la-pagina", pruebas=[SE_VE],
         viejo='<p class="rs-aviso" id="aviso-panel" role="alert" hidden></p>', nuevo=""),
    dict(id="e61-armar-solo-al-registro", pruebas=[MODO_ARMAR],
         viejo='  avisoFijo(avisoDeModo(MODO_PAGINA, modo) + (motivo ?',
         nuevo='  feed(avisoDeModo(MODO_PAGINA, modo) + (motivo ?'),
    dict(id="e61-armar-sin-el-motivo", pruebas=[MODO_ARMAR], viejo="catch (e) { if (e.status) motivo = e.message; }",
         nuevo="catch (e) {}"),
    dict(id="e61-al-cargar-solo-el-estado", pruebas=[AL_CARGAR],
         viejo='    avisoFijo(texto);\n    estado("No pude leer la configuración");\n',
         nuevo='    estado("No pude leer la configuración");\n'),
    dict(id="e61-sin-el-motivo-en-la-lista", pruebas=[AL_CARGAR],
         viejo='    $("#navs").innerHTML = `<p class="nota">${esc(texto)}</p>`;\n', nuevo=""),
    dict(id="e61-sin-decir-que-lo-creo", pruebas=[AL_CARGAR],
         viejo='    notaVisible(d.aviso || (d.usuarios.length ? "" : SIN_OPERADOR));\n', nuevo=""),
    dict(id="e61-entrar-solo-al-registro", pruebas=[AL_CARGAR, BOTONES],
         viejo='avisoFijo("No pude entrar: " + e.message);',
         nuevo='feed("No pude entrar: " + e.message, "f-alerta", "REVISAR");'),
    dict(id="e61-credenciales-sin-el-cuadro", pruebas=[CUADRO],
         viejo='    $("#cred-estado").textContent = texto;\n    if (!yaAbierto) dlg.showModal();\n    return;\n',
         nuevo='    $("#cred-estado").textContent = texto;\n    return;\n'),
    dict(id="e61-credenciales-sin-operador-calla", pruebas=[CUADRO],
         viejo='$("#cred-estado").textContent = op.options.length ? "" : SIN_OPERADOR;',
         nuevo='$("#cred-estado").textContent = "";'),
    dict(id="e61-arrancar-solo-al-registro", pruebas=[BOTONES], viejo='avisoFijo("No pude arrancar: " + e.message);',
         nuevo='feed("No pude arrancar: " + e.message, "f-alerta", "REVISAR");'),
    dict(id="e61-api-sin-codigo", pruebas=[BOTONES], viejo=" e.status = r.status; throw e; }",
         nuevo=" throw e; }"),
    # El .bat: sin el freno del código 11, sin mirar lo que dio el preparador, o sin la pausa.
    dict(id="e61-bat-sin-chequeo", archivo="Iniciar AQUASHIELD.bat", pruebas=[BAT_BLOQUE, BAT_LIB],
         viejo=FRENO_BAT, nuevo=""),
    dict(id="e61-bat-emision-no-mira", archivo="Iniciar AQUASHIELD_EMISION.bat", pruebas=[BAT_BLOQUE, BAT_LIB],
         viejo=FRENO_BAT, nuevo=FRENO_BAT.replace("errorlevel 11", "errorlevel 12")),
    dict(id="e61-bat-sin-pausa", archivo="Iniciar AQUASHIELD_EMISION.bat", pruebas=[BAT_BLOQUE, BAT_LIB],
         viejo=FRENO_BAT, nuevo=FRENO_BAT.replace("    pause\n", "")),
]

# --- Encargo 62 (CICLO-maersk-contenedor.md): MAERSK elige la única opción «40 Reefer High», el contenedor de las
# filas, con la evidencia de la lista antes de elegir; si no hay exactamente una, NO ENVIADA sin pulsar nada (decisión
# de Marcelo). Hasta ahí pulsaba la primera opción con «40» y «Reefer».
TCM = "test_clics.TestContenedorMaersk."
CM_ES = TCM + "test_el_contenedor_es_el_de_las_filas"
CM_ELIGE = TCM + "test_elige_la_unica_con_el_texto_entero"
CM_QUIETA = TCM + "test_espera_la_lista_quieta"
CM_SIN_UNA = TCM + "test_sin_una_sola_no_pulsa_nada"
CM_CAMBIA = TCM + "test_si_la_lista_cambia_mientras_guarda_no_elige"
CM_FALLA = TCM + "test_el_campo_o_el_clic_que_fallan_cortan"
CM_REPINTA = TCM + "test_si_el_portal_repinta_antes_del_clic_no_pulsa_otra"
COLUMNA = "test_planilla.TestContenedorDeLaFila.test_los_dos_lectores_toman_la_misma_columna"
CM_DECORADOR = TCM + "test_la_reserva_queda_no_enviada_con_su_evidencia"
CM_LLAMADA = TCM + "test_reservar_maersk_elige_asi_antes_de_la_guarda"
EV_SOLO_AHI = LD + "test_solo_ahi"

MUTACIONES += [
    dict(id="e62-otro-contenedor", pruebas=[CM_ES, CM_ELIGE], viejo='MK_CONTENEDOR = "40 Reefer High"\n',
         nuevo='MK_CONTENEDOR = "40 Reefer Standard"\n'),
    # Desde el encargo 63, sobre el ayudante de las dos listas (_mk_elegir_unica), con las pruebas de los ajustes
    # reefer donde el caso es el mismo.
    dict(id="e62-basta-que-lo-traiga",
         pruebas=[CM_ELIGE, "test_clics.TestReeferMaersk.test_elige_la_unica_con_el_texto_entero"],
         viejo="    exactas = [i for i, t in enumerate(textos) if t == buscado]\n",
         nuevo="    exactas = [i for i, t in enumerate(textos) if buscado in t]\n"),
    dict(id="e62-la-primera-de-varias",
         pruebas=[CM_SIN_UNA, "test_clics.TestReeferMaersk.test_sin_una_sola_no_pulsa_nada"],
         viejo="    if len(exactas) != 1:\n",
         nuevo="    if not exactas:\n"),
    dict(id="e62-sin-juntar-los-espacios", pruebas=[CM_ELIGE],
         viejo='    return op, [" ".join((t or "").split()) for t in op.all_text_contents()]\n',
         nuevo='    return op, [(t or "").strip() for t in op.all_text_contents()]\n'),
    dict(id="e62-sin-esperar-la-lista-quieta", pruebas=[CM_QUIETA], viejo="        if textos and textos == anterior:\n",
         nuevo="        if textos:\n"),
    dict(id="e62-sin-evidencia", pruebas=[CM_ELIGE, CM_SIN_UNA, CM_DECORADOR, EV_SOLO_AHI],
         viejo='    _evidencia_antes_de_la_guarda(page, reg, evidencia, f"con la {lista}", completa=False)\n',
         nuevo=""),
    dict(id="e62-elige-de-otra-lista", pruebas=[CM_CAMBIA], viejo="    if despues != textos:\n",
         nuevo="    if False:\n"),
    dict(id="e62-el-campo-que-falla-sigue", pruebas=[CM_FALLA],
         viejo=('        raise ObjetivoNoEncontrado(MK_TIPO_CONTENEDOR, f"el campo «Select container type and size» '
                'para'),
         nuevo=('        return\n        raise ObjetivoNoEncontrado(MK_TIPO_CONTENEDOR, f"el campo «Select container '
                'type and size» para')),
    dict(id="e62-el-clic-que-falla-sin-motivo", pruebas=[CM_FALLA],
         viejo='"la opción «{buscado}», que no aceptó el clic ({_texto_error(e)})"',
         nuevo='"la opción «{buscado}» ({_texto_error(e)})"'),
    dict(id="e62-motivo-sin-las-opciones", pruebas=[CM_SIN_UNA, CM_DECORADOR],
         viejo='(f"hay {n} entre {len(textos)}: {vistas}" if textos else "la lista no apareció")',
         nuevo='(f"hay {n}" if textos else "la lista no apareció")'),
    dict(id="e62-como-antes", pruebas=[CM_ELIGE, CM_LLAMADA],
         viejo="    _mk_elegir_contenedor(page, reg, det, reserva.get(\"fila\", \"\"), MK_PALABRA_CONTENEDOR)\n",
         nuevo=("    cand = page.locator(\"mc-option:visible\")\n"
                "    page.get_by_placeholder(\"Select container type and size\").first.type(MK_PALABRA_CONTENEDOR)\n"
                "    cand.nth(0).click(timeout=3000)\n    det.append(\"cont=\" + MK_CONTENEDOR)\n")),
]

# --- Encargo 63 (CICLO-maersk-otro-contenedor-y-reefer.md): la fila de MAERSK que pide otro contenedor que «40 HC
# REEFER» queda NO ENVIADA sin entrar al portal, en el panel web, en la consola y con un decorador en reservar_maersk;
# y en los ajustes reefer, MAERSK elige la única opción «Standard (40´)», con la evidencia de la lista y el mismo
# ayudante que el tipo de contenedor (decisiones de Marcelo). Hasta ahí pulsaba la primera opción con «40».
TOC = "test_ayudantes.TestOtroContenedorMaersk."
OC_REGLA = TOC + "test_otro_contenedor"
OC_DECORADOR = TOC + "test_maersk_no_abre_el_portal_con_otro_contenedor"
OC_POR_DENTRO = TOC + "test_sin_nave_o_sin_ruta_dicen_eso"
OC_PASA = TOC + "test_con_el_contenedor_pasa_igual"
OC_WEB = "test_web.TestPanelCorridas.test_fila_de_maersk_con_otro_contenedor_no_abre_el_portal"
OC_CONSOLA = "test_consola.TestEjecutarReservas.test_fila_de_maersk_con_otro_contenedor_no_abre_el_portal"
DECORADO_MK = "test_clics.TestSinClicACiegas.test_cada_reservador_que_corta_esta_decorado"
TRF = "test_clics.TestReeferMaersk."
RF_ES = TRF + "test_el_reefer_es_el_medido"
RF_ELIGE = TRF + "test_elige_la_unica_con_el_texto_entero"
RF_SIN_UNA = TRF + "test_sin_una_sola_no_pulsa_nada"
RF_FALLA = TRF + "test_el_campo_o_el_clic_que_fallan_cortan"
RF_DECORADOR = TRF + "test_la_reserva_queda_no_enviada_con_su_evidencia"
RF_LLAMADA = TRF + "test_reservar_maersk_elige_asi_antes_de_la_guarda"
DECOS_MK = ('@_con_la_nave_de_la_fila\n@_con_la_ruta_de_la_fila\n@_sin_clic_a_ciegas("mk")\n'
            '@_mk_con_el_contenedor_de_la_fila\n')
REGLA_OC = "    if cont.upper() == CONTENEDOR_DE_LAS_FILAS:\n"
PASA_OC = ('            return _sin_el_contenedor(reg, (reserva or {}).get("fila"), motivo)\n'
           '        return reservar(page, reserva, creds, reg, on_pausa=on_pausa)\n')
AVISO_OC = ('    reg.paso(f"✗ fila {fila}: {NO_ENVIADA} · {motivo}. No entro al portal por ella: resérvala a mano '
            'en el portal, o "\n             f"corrige el contenedor en la planilla si la fila pide '
            '«{CONTENEDOR_DE_LAS_FILAS}».")\n')

MUTACIONES += [
    # La regla: también en las otras navieras, sin juntar los espacios, distinguiendo mayúsculas, con que traiga el
    # tamaño y «REEFER», con otro contenedor de las filas, con la celda vacía que pasa, o un motivo sin el valor.
    dict(id="e63-otra-naviera-tambien", pruebas=[OC_REGLA, OC_WEB],
         viejo='    if nav != "maersk":\n        return ""\n', nuevo=""),
    dict(id="e63-sin-juntar-los-espacios", pruebas=[OC_REGLA, OC_WEB],
         viejo='        return ""\n    cont = " ".join(str((reserva or {}).get("contenedor") or "").split())\n',
         nuevo='        return ""\n    cont = str((reserva or {}).get("contenedor") or "").strip()\n'),
    dict(id="e63-distingue-mayusculas", pruebas=[OC_REGLA, OC_PASA, OC_WEB], viejo=REGLA_OC,
         nuevo="    if cont == CONTENEDOR_DE_LAS_FILAS:\n"),
    dict(id="e63-basta-que-sea-reefer", pruebas=[OC_REGLA], viejo=REGLA_OC,
         nuevo='    if "REEFER" in cont.upper():\n'),
    dict(id="e63-otro-contenedor-de-las-filas",
         pruebas=[OC_REGLA, OC_PASA, OC_WEB, OC_CONSOLA,
                  "test_envio.TestLecturaDelPanel.test_marca_y_cuenta_aparte_las_filas_con_otro_contenedor",
                  "test_planilla.TestContenedorDeLaFila.test_los_dos_lectores_dan_el_mismo_contenedor"],
         viejo='CONTENEDOR_DE_LAS_FILAS = "40 HC REEFER"\n', nuevo='CONTENEDOR_DE_LAS_FILAS = "40 REEFER"\n'),
    dict(id="e63-la-celda-vacia-pasa", pruebas=[OC_REGLA, OC_DECORADOR],
         viejo='    if not cont:\n        return f"la fila no dice',
         nuevo='    if not cont:\n        return ""\n        return f"la fila no dice'),
    dict(id="e63-motivo-sin-el-valor", pruebas=[OC_REGLA, OC_DECORADOR, OC_WEB, OC_CONSOLA],
         viejo='"la fila pide el contenedor «{visto}», ', nuevo='"la fila pide el contenedor «otro», '),
    dict(id="e63-motivo-sin-recortar", pruebas=[OC_REGLA],
         viejo='"?" if unicodedata.category(c) in ("Cc", "Cf") else c for c in cont[:40])',
         nuevo='"?" if unicodedata.category(c) in ("Cc", "Cf") else c for c in cont)'),
    # El aviso y el estado.
    dict(id="e63-sin-aviso", pruebas=[OC_DECORADOR, OC_WEB, OC_CONSOLA], viejo=AVISO_OC, nuevo=""),
    dict(id="e63-omitida", pruebas=[OC_DECORADOR, OC_WEB, OC_CONSOLA],
         viejo="    return (NO_ENVIADA, motivo)\n", nuevo='    return ("OMITIDO", motivo)\n'),
    # El decorador: deja pasar la fila, mira otra naviera, pierde on_pausa, su nombre o su documentación, no está, o
    # va por fuera de los de la nave y la ruta.
    dict(id="e63-el-decorador-deja-pasar", pruebas=[OC_DECORADOR],
         viejo="        if motivo:\n            return _sin_el_contenedor(",
         nuevo="        if False:\n            return _sin_el_contenedor("),
    dict(id="e63-el-decorador-mira-otra-naviera", pruebas=[OC_DECORADOR],
         viejo='        motivo = _otro_contenedor("maersk", reserva)\n',
         nuevo='        motivo = _otro_contenedor("one", reserva)\n'),
    dict(id="e63-decorador-sin-on-pausa", pruebas=[OC_PASA], viejo=PASA_OC,
         nuevo=PASA_OC.replace(", on_pausa=on_pausa)", ")")),
    dict(id="e63-decorador-sin-nombre", pruebas=[OC_PASA],
         viejo="    reservar_con_el_contenedor.__name__ = reservar.__name__\n", nuevo=""),
    dict(id="e63-decorador-sin-documentacion", pruebas=[OC_PASA],
         viejo="    reservar_con_el_contenedor.__doc__ = reservar.__doc__\n", nuevo=""),
    dict(id="e63-maersk-sin-el-decorador", pruebas=[OC_DECORADOR, DECORADO_MK],
         viejo=DECOS_MK, nuevo=DECOS_MK.replace("@_mk_con_el_contenedor_de_la_fila\n", "")),
    dict(id="e63-el-decorador-por-fuera", pruebas=[OC_POR_DENTRO, DECORADO_MK],
         viejo=DECOS_MK,
         nuevo="@_mk_con_el_contenedor_de_la_fila\n" + DECOS_MK.replace("@_mk_con_el_contenedor_de_la_fila\n", "")),
    # El panel web: la fila va al portal, se abre el navegador sin filas, o no queda el resultado.
    dict(id="e63-web-va-al-portal", pruebas=[OC_WEB],
         viejo="            sub_elegidas = [f for f in sub_elegidas if not _otro_contenedor(nav, f)]\n", nuevo=""),
    dict(id="e63-web-abre-el-navegador", pruebas=[OC_WEB],
         viejo='            if not sub_elegidas:\n                reg.paso(f"De las filas de {nombre}',
         nuevo='            if False:\n                reg.paso(f"De las filas de {nombre}'),
    dict(id="e63-web-sin-resultado", pruebas=[OC_WEB],
         viejo=('_sin_el_contenedor(reg, rsv["fila"], _otro_contenedor(nav, rsv))\n                with _LOCK:\n'
                '                    _WEB["resultados"][str(rsv["fila"])] = {\n'),
         nuevo=('_sin_el_contenedor(reg, rsv["fila"], _otro_contenedor(nav, rsv))\n                with _LOCK:\n'
                '                    _ = {\n')),
    # La consola: no la anota, va al portal, se abre el navegador sin filas, o sin resumen.
    dict(id="e63-consola-no-anota", pruebas=[OC_CONSOLA],
         viejo=('            anotar(i, rsv, *_sin_el_contenedor(reg, rsv["fila"], _otro_contenedor(naviera_clave, '
                'rsv)))\n'),
         nuevo="            pass\n"),
    dict(id="e63-consola-va-al-portal", pruebas=[OC_CONSOLA],
         viejo="    con_nave = [(i, rsv) for i, rsv in con_nave if not _otro_contenedor(naviera_clave, rsv)]\n",
         nuevo=""),
    dict(id="e63-consola-abre-el-navegador", pruebas=[OC_CONSOLA],
         viejo='    if not con_nave:\n        reg.paso(f"De las filas de {nombre}',
         nuevo='    if False:\n        reg.paso(f"De las filas de {nombre}'),
    dict(id="e63-consola-sin-resumen", pruebas=[OC_CONSOLA],
         viejo='                 f"no abro el navegador ni entro al portal.")\n        resumen()\n',
         nuevo='                 f"no abro el navegador ni entro al portal.")\n'),
    # Los ajustes reefer: otra opción, otro paso, otra evidencia u otro nombre de la lista, el campo que falla y sigue,
    # sin anotarlo, o como antes (la primera opción, sin el ayudante).
    dict(id="e63-otro-reefer", pruebas=[RF_ES, RF_ELIGE], viejo='MK_REEFER = "Standard (40' + chr(0xB4) + ')"\n',
         nuevo="MK_REEFER = \"Standard (40')\"\n"),
    dict(id="e63-reefer-otro-paso", pruebas=[RF_ES, RF_SIN_UNA, RF_DECORADOR],
         viejo='MK_TIPO_REEFER = "Tipo de contenedor reefer de MAERSK"\n',
         nuevo='MK_TIPO_REEFER = "Tipo de contenedor de MAERSK"\n'),
    dict(id="e63-reefer-otra-evidencia", pruebas=[RF_ELIGE, RF_SIN_UNA, RF_DECORADOR, RF_LLAMADA],
         viejo='f"mk_f{fila}_reefer")\n', nuevo='f"mk_f{fila}_contenedor")\n'),
    dict(id="e63-reefer-otra-lista", pruebas=[RF_ELIGE, RF_SIN_UNA, RF_DECORADOR, RF_LLAMADA],
         viejo='"lista de tipos de contenedor reefer"', nuevo='"lista de tipos de contenedor"'),
    dict(id="e63-reefer-el-campo-que-falla-sigue", pruebas=[RF_FALLA],
         viejo='        raise ObjetivoNoEncontrado(MK_TIPO_REEFER, f"el campo «Select reefer',
         nuevo='        return\n        raise ObjetivoNoEncontrado(MK_TIPO_REEFER, f"el campo «Select reefer'),
    dict(id="e63-reefer-sin-anotar", pruebas=[RF_ELIGE], viejo='    det.append("reeferCont=" + MK_REEFER)\n', nuevo=""),
    dict(id="e63-reefer-como-antes", pruebas=[RF_LLAMADA],
         viejo="    _mk_elegir_reefer(page, reg, det, f)\n",
         nuevo=('    rc = page.get_by_placeholder("Select reefer container type and size").first\n'
                '    rc.click(timeout=4000)\n'
                '    page.locator("mc-option:visible").first.click(timeout=3000)\n')),
]

# --- Encargo 64 (CICLO-maersk-contenedor-consola-y-panel.md): con una columna de contenedor y la celda vacía, la
# consola le da el contenedor de las filas, como el panel; el panel marca antes de correr la fila de MAERSK que pide
# otro contenedor, como la sin ruta; y reservar_maersk queda sin las ramas para un contenedor que no es reefer, que ya
# no se alcanzaban (decisiones de Marcelo). Las que vuelven a poner una rama (e64-vuelve-*) no cambian lo que hace una
# fila que llega al reservador, que siempre es reefer: las ve solo la foto (SIN_RAMAS).
LECTORES = "test_planilla.TestContenedorDeLaFila.test_los_dos_lectores_dan_el_mismo_contenedor"
VACIA_CONSOLA = ER + "test_fila_de_maersk_con_la_celda_vacia_va_al_portal"
OTRO_API = CO + "test_filas_dicen_si_piden_otro_contenedor"
OTRO_PANEL = "test_envio.TestLecturaDelPanel.test_marca_y_cuenta_aparte_las_filas_con_otro_contenedor"
SOLO_REEFER = "test_clics.TestMaerskSoloReefer.test_la_fila_hace_siempre_lo_de_un_reefer"
SIN_RAMAS = "test_clics.TestMaerskSoloReefer.test_sin_ramas_por_el_contenedor"
CONSOLA_VACIA = ('                "contenedor": (_s(ws.cell(r, col_map["tipo"]).value) '
                 'if col_map.get("tipo") else "")\n'
                 '                              or CONTENEDOR_DE_LAS_FILAS,\n')
MARCA_OTRO = '    otro = "" if _fila_sin_nave(nave) or falta else _otro_contenedor(nav, fila)\n'
CONTROL_TEMP = ('    try:\n'
                '        page.get_by_text("requires temperature control", exact=False).first.click(timeout=3000)\n'
                '        reg.info("marcado: requiere control de temperatura"); det.append("reefer")\n'
                '        esperar(page, 1.5)\n'
                '    except Exception:\n'
                '        pass\n')
REEF = '    if "REEF" in (reserva.get("contenedor") or "").upper():\n'

MUTACIONES += [
    # Los lectores: la consola, con la celda vacía como antes; el panel, con la celda vacía vacía.
    dict(id="e64-consola-celda-vacia-como-antes", pruebas=[LECTORES, VACIA_CONSOLA], viejo=CONSOLA_VACIA,
         nuevo=('                "contenedor": _s(ws.cell(r, col_map["tipo"]).value) if col_map.get("tipo") '
                'else CONTENEDOR_DE_LAS_FILAS,\n')),
    dict(id="e64-panel-celda-vacia-vacia", pruebas=[LECTORES],
         viejo='            "contenedor": val("contenedor") or CONTENEDOR_DE_LAS_FILAS,\n',
         nuevo='            "contenedor": val("contenedor"),\n'),
    # /api/filas: sin la marca, también en la fila sin nave o sin ruta, mirando siempre MAERSK, o con la naviera de la
    # hoja en CONSOLIDADO; y la naviera de la fila, la de la hoja también en CONSOLIDADO (el panel no reparte).
    dict(id="e64-sin-marca-de-otro-contenedor", pruebas=[OTRO_API],
         viejo="otro_contenedor=bool(otro), ", nuevo="otro_contenedor=False, "),
    dict(id="e64-marca-tambien-sin-nave-o-sin-ruta", pruebas=[OTRO_API], viejo=MARCA_OTRO,
         nuevo="    otro = _otro_contenedor(nav, fila)\n"),
    dict(id="e64-marca-sin-mirar-la-naviera", pruebas=[OTRO_API], viejo=MARCA_OTRO,
         nuevo='    otro = "" if _fila_sin_nave(nave) or falta else _otro_contenedor("maersk", fila)\n'),
    dict(id="e64-marca-con-la-naviera-de-la-hoja", pruebas=[OTRO_API],
         viejo="_con_su_marca(f, _nav_de_la_fila(nav_hoja, f))", nuevo="_con_su_marca(f, nav_hoja)"),
    dict(id="e64-la-fila-con-la-naviera-de-la-hoja", pruebas=[OTRO_API, CO + "test_consolidado_reparte_por_naviera"],
         viejo='    return _match_nav_key(fila.get("naviera")) if nav_hoja == "todas" else nav_hoja\n',
         nuevo="    return nav_hoja\n"),
    # La página: sin la marca en la tabla, sin escapar el contenedor, sin el aviso, sin marcarla para correr, o sin su
    # estilo.
    dict(id="e64-panel-sin-marca-en-la-tabla", pruebas=[OTRO_PANEL],
         viejo=("\" <span class='otro-contenedor'>otro contenedor: \"\n"
                "                            + esc(f.contenedor_a_la_vista) + \"</span>\""),
         nuevo='""'),
    dict(id="e64-panel-sin-escapar", pruebas=[OTRO_PANEL],
         viejo="+ esc(f.contenedor_a_la_vista) + \"</span>\"",
         nuevo="+ f.contenedor_a_la_vista + \"</span>\""),
    dict(id="e64-panel-sin-aviso", pruebas=[OTRO_PANEL],
         viejo="  const otroCont = FILAS.filter(f => f.otro_contenedor).length;\n", nuevo="  const otroCont = 0;\n"),
    dict(id="e64-panel-sin-marcar-para-correr", pruebas=[OTRO_PANEL],
         viejo="function marcadaPorDefecto(f) {\n  return !f.manual;\n}\n",
         nuevo="function marcadaPorDefecto(f) {\n  return !f.manual && !f.otro_contenedor;\n}\n"),
    dict(id="e64-panel-sin-estilo", pruebas=[OTRO_PANEL],
         viejo=".sin-nave, .sin-ruta, .otro-contenedor { color", nuevo=".sin-nave, .sin-ruta { color"),
    # MAERSK: sin el salmón, sin el salmón exacto, sin el control de temperatura, otra palabra u otro peso.
    dict(id="e64-commodity-sin-salmon", pruebas=[SOLO_REEFER, SIN_RAMAS],
         viejo='    terminos = [base_com] if base_com else ["SALMON", "FISH", "SEAFOOD"]\n',
         nuevo='    terminos = [base_com] if base_com else ["FISH", "GOODS"]\n'),
    dict(id="e64-commodity-sin-el-salmon-exacto", pruebas=[SOLO_REEFER],
         viejo="                    if exact_salmon.count():\n                        target = exact_salmon.first\n",
         nuevo="                    if False:\n                        target = exact_salmon.first\n"),
    dict(id="e64-sin-control-de-temperatura", pruebas=[SOLO_REEFER, SIN_RAMAS], viejo=CONTROL_TEMP, nuevo=""),
    dict(id="e64-otra-palabra",
         pruebas=["test_clics.TestContenedorMaersk.test_el_contenedor_es_el_de_las_filas", SOLO_REEFER],
         viejo='MK_PALABRA_CONTENEDOR = "40 Reefer"\n', nuevo='MK_PALABRA_CONTENEDOR = "40"\n'),
    dict(id="e64-otro-peso",
         pruebas=[SOLO_REEFER, SIN_RAMAS, "test_clics.TestContenedorMaersk.test_elige_la_unica_con_el_texto_entero"],
         viejo=".strip() or _peso_reefer()\n", nuevo='.strip() or "20000"\n'),
    # Las ramas que vuelven: los ajustes reefer, el control de temperatura y el peso, otra vez según el contenedor.
    dict(id="e64-vuelve-la-rama-de-los-ajustes", pruebas=[SIN_RAMAS, RF_LLAMADA],
         viejo="    _mk_elegir_reefer(page, reg, det, f)\n",
         nuevo=REEF + "        _mk_elegir_reefer(page, reg, det, f)\n"),
    dict(id="e64-vuelve-la-rama-del-control", pruebas=[SIN_RAMAS], viejo=CONTROL_TEMP,
         nuevo=REEF + "".join("    " + l + "\n" for l in CONTROL_TEMP.splitlines())),
    dict(id="e64-vuelve-la-rama-del-peso", pruebas=[SIN_RAMAS], viejo=".strip() or _peso_reefer()\n",
         nuevo='.strip() or (_peso_reefer() if "REEF" in (reserva.get("contenedor") or "").upper() else "20000")\n'),
    # Encargo 65, las revisiones del diff de los encargos 62 a 64. El contenedor a la vista: con los caracteres de
    # control (que openpyxl no escribe) o los invisibles; el motivo, con la celda tal cual; /api/filas sin él; la
    # página, con la celda.
    dict(id="e65-a-la-vista-con-controles", pruebas=[OC_REGLA],
         viejo='    return "".join("?" if unicodedata.category(c) in ("Cc", "Cf") else c for c in cont[:40])\n',
         nuevo="    return cont[:40]\n"),
    dict(id="e65-a-la-vista-con-invisibles", pruebas=[OC_REGLA],
         viejo='unicodedata.category(c) in ("Cc", "Cf")', nuevo='unicodedata.category(c) in ("Cc",)'),
    dict(id="e65-a-la-vista-sin-juntar-los-espacios", pruebas=[OC_REGLA],
         viejo='    import unicodedata\n    cont = " ".join(str((reserva or {}).get("contenedor") or "").split())\n',
         nuevo='    import unicodedata\n    cont = str((reserva or {}).get("contenedor") or "").strip()\n'),
    dict(id="e65-motivo-con-la-celda", pruebas=[OC_REGLA], viejo="    visto = _contenedor_a_la_vista(reserva)\n",
         nuevo="    visto = cont[:40]\n"),
    dict(id="e65-api-sin-el-contenedor", pruebas=[OTRO_API],
         viejo='contenedor_a_la_vista=_contenedor_a_la_vista(fila) if otro else "",',
         nuevo='contenedor_a_la_vista="",'),
    dict(id="e65-panel-con-la-celda", pruebas=[OTRO_PANEL],
         viejo="esc(f.contenedor_a_la_vista)", nuevo="esc(f.contenedor)"),
    # La consola, con su propia columna del contenedor otra vez, o con la última que calza.
    dict(id="e65-consola-con-su-columna", pruebas=[COLUMNA],
         viejo=('    col_map.pop("tipo", None)\n    col_cont = _campos_de_la_fila(ws, h_row).get("contenedor")\n'
                '    if col_cont:\n        col_map["tipo"] = col_cont\n'), nuevo=""),
    dict(id="e65-la-ultima-que-calza", pruebas=[COLUMNA],
         viejo="            if campo in cabec:\n                continue\n            if any(k in h for k in claves):",
         nuevo="            if any(k in h for k in claves):"),
    # Y el clic de _mk_elegir_unica: otra vez al lugar de la opción (como hasta el encargo 64), sin comprobar su texto,
    # o sin cortar si no se puede tomar. El clic por su lugar no lo ve CM_REPINTA: la comprobación del texto corta antes
    # del clic (el censo del encargo 65 lo mostró); lo ven las dos que eligen, cuya página no admite ese clic.
    dict(id="e65-clic-por-posicion",
         pruebas=[CM_ELIGE, "test_clics.TestReeferMaersk.test_elige_la_unica_con_el_texto_entero"],
         viejo="        opcion.click(timeout=3000)\n", nuevo="        op.nth(exactas[0]).click(timeout=3000)\n"),
    dict(id="e65-sin-comprobar-la-opcion", pruebas=[CM_REPINTA], viejo="    if ahora != buscado:\n",
         nuevo="    if False:\n"),
    dict(id="e65-la-opcion-que-no-se-toma-sigue", pruebas=[CM_REPINTA],
         viejo='        raise ObjetivoNoEncontrado(paso, f"la opción «{buscado}», que no pude volver',
         nuevo='        return\n        raise ObjetivoNoEncontrado(paso, f"la opción «{buscado}», que no pude volver'),
]

# Encargo 66 (CICLO-viaje-y-origen.md). El viaje de la fila: como parte de una palabra, sin él no calza nada, sin
# mayúsculas o en una sola palabra.
VJ = "test_ayudantes.TestViajeDeLaFila."
ONE_V, MSC_V, HMM_V, CMA_V = ("test_clics.TestOne.", "test_clics.TestMsc.", "test_clics.TestHyundai.",
                              "test_clics.TestCma.")
PSP, ARR_V, MSE = "test_web.TestPanelSoloSuPagina.", "test_web.TestArranqueDelPanel.", "test_envio.TestMarcaDeLaSesion."
SIN_VIAJE_ONE = ONE_V + "test_sin_el_viaje_de_la_fila_no_elige_otra"
SIN_VIAJE_MSC = MSC_V + "test_sin_el_viaje_de_la_fila_no_elige_otra"
HMM_SOLO = HMM_V + "test_solo_la_salida_del_viaje_de_la_fila"
HMM_ANTES = HMM_V + "test_la_interfaz_anterior_tampoco_elige_otro_viaje"
CMA_JS, CMA_SIN = CMA_V + "test_js_rutas_con_el_viaje_de_la_fila", CMA_V + "test_itinerario_sin_el_viaje_de_la_fila"
MUTACIONES += [
    dict(id="e66-viaje-como-parte", pruebas=[VJ + "test_trae_el_viaje", VJ + "test_la_misma_regla_en_javascript"],
         viejo="    return not palabras or _trae_la_nave(texto, palabras)\n",
         nuevo='    return not palabras or all(p in str(texto or "").upper() for p in palabras)\n'),
    dict(id="e66-sin-viaje-no-calza",
         pruebas=[VJ + "test_trae_el_viaje", MSC_V + "test_la_salida_pedida_trae_el_viaje", HMM_V + "test_es_la_pedida"],
         viejo="    return not palabras or _trae_la_nave(texto, palabras)\n",
         nuevo="    return bool(palabras) and _trae_la_nave(texto, palabras)\n"),
    dict(id="e66-palabras-sin-mayusculas", pruebas=[VJ + "test_las_palabras_del_viaje", VJ + "test_trae_el_viaje"],
         viejo='    return [p for p in str(viaje or "").upper().split() if len(p) > 1]\n',
         nuevo='    return [p for p in str(viaje or "").split() if len(p) > 1]\n'),
    dict(id="e66-palabras-en-una", pruebas=[VJ + "test_las_palabras_del_viaje"],
         viejo='    return [p for p in str(viaje or "").upper().split() if len(p) > 1]\n',
         nuevo='    return [str(viaje or "").upper().strip()] if str(viaje or "").strip() else []\n'),
    # ONE: el clic sin volver a leer el viaje, sin filtrar, sin cortar, eligiendo entre todas, o sin pasarle el viaje.
    dict(id="e66-one-clic-sin-el-viaje", pruebas=[ONE_V + "test_js_clic_vuelve_a_leer_el_viaje"],
         viejo="    if (viaje.length && !_traeLaNave(t.nave, viaje)) return false;\n", nuevo=""),
    dict(id="e66-one-sin-filtrar", pruebas=[SIN_VIAJE_ONE],
         viejo='    con_el_viaje = [t for t in tarjetas if _trae_el_viaje(t.get("nave"), reserva.get("viaje"))]\n',
         nuevo="    con_el_viaje = list(tarjetas)\n"),
    dict(id="e66-one-sin-cortar", pruebas=[SIN_VIAJE_ONE],
         viejo=('    if tarjetas and not con_el_viaje:\n'
                '        return _one_sin_una_salida(page, reg, reserva, tarjetas, "sin-viaje", desde)\n'), nuevo=""),
    dict(id="e66-one-elige-entre-todas", pruebas=[SIN_VIAJE_ONE], viejo="    tarjetas = con_el_viaje\n", nuevo=""),
    dict(id="e66-one-clic-sin-pasar-el-viaje", pruebas=[ONE_V + "test_reservar_one_elige_la_proxima_salida"],
         viejo=', "viaje": _palabras_del_viaje(reserva.get("viaje"))}))', nuevo="}))"),
    # MSC: la salida pedida sin el viaje o sin su «Select»; baja solo por la nave; sin cortar; elige entre todas.
    dict(id="e66-msc-pedida-sin-viaje", pruebas=[MSC_V + "test_la_salida_pedida_trae_el_viaje"],
         viejo='    return bool(tarjeta.get("sel") and _trae_la_nave(texto, toks) and _trae_el_viaje(texto, viaje))\n',
         nuevo='    return bool(tarjeta.get("sel") and _trae_la_nave(texto, toks))\n'),
    dict(id="e66-msc-pedida-sin-select", pruebas=[MSC_V + "test_la_salida_pedida_trae_el_viaje"],
         viejo='    return bool(tarjeta.get("sel") and _trae_la_nave(texto, toks) and _trae_el_viaje(texto, viaje))\n',
         nuevo='    return bool(_trae_la_nave(texto, toks) and _trae_el_viaje(texto, viaje))\n'),
    dict(id="e66-msc-baja-por-la-nave-sola", pruebas=[MSC_V + "test_reservar_msc_baja_si_no_esta"],
         viejo="    while not any(_msc_es_la_pedida(x, toks, viaje) for x in naves):\n",
         nuevo="    while not any(x.get(\"sel\") and _trae_la_nave(_norm(x.get(\"nave\")), toks) for x in naves):\n"),
    dict(id="e66-msc-sin-cortar", pruebas=[SIN_VIAJE_MSC],
         viejo=("    if exacta and not any(_msc_es_la_pedida(n, toks, viaje) for n in exacta):\n"
                '        return _msc_salida_ambigua(page, reg, reserva, exacta, "sin-viaje", desde)\n'), nuevo=""),
    dict(id="e66-msc-elige-entre-todas",
         pruebas=[SIN_VIAJE_MSC, "test_ayudantes.TestNaveCompleta.test_msc_y_cosco_calzan_con_el_ayudante"],
         viejo="    exacta = [n for n in exacta if _msc_es_la_pedida(n, toks, viaje)]\n", nuevo=""),
    # HYUNDAI: la salida pedida sin el viaje; el clic sin volver a leerlo; sin ampliar por él; sin cortar; elige entre
    # las de la nave; el clic sin el viaje; la interfaz anterior sin él, sin mirar la cerrada, o su corte como REVISAR.
    dict(id="e66-hmm-pedida-sin-viaje", pruebas=[HMM_V + "test_es_la_pedida", HMM_SOLO],
         viejo='    return bool(tarjeta.get("calza") and _trae_el_viaje(tarjeta.get("primera"), viaje))\n',
         nuevo='    return bool(tarjeta.get("calza"))\n'),
    dict(id="e66-hmm-clic-sin-el-viaje", pruebas=[HMM_V + "test_js_clic_vuelve_a_leer_el_viaje"],
         viejo="    if (viaje.length && !_traeLaNave(t.primera, viaje)) return false;\n", nuevo=""),
    dict(id="e66-hmm-no-amplia-por-el-viaje", pruebas=[HMM_SOLO],
         viejo="    if not any(_hmm_es_la_pedida(t, viaje) for t in tarjetas):\n",
         nuevo='    if not any(t.get("calza") for t in tarjetas):\n'),
    dict(id="e66-hmm-sin-cortar", pruebas=[HMM_SOLO],
         viejo="    if not any(_hmm_es_la_pedida(t, viaje) for t in de_la_nave):\n", nuevo="    if False:\n"),
    dict(id="e66-hmm-disponibles-de-la-nave", pruebas=[HMM_SOLO],
         viejo=('    disponibles = [t for t in de_la_nave if _hmm_es_la_pedida(t, viaje) and t.get("disponible") and '
                't.get("book") == 1]\n'),
         nuevo='    disponibles = [t for t in de_la_nave if t.get("disponible") and t.get("book") == 1]\n'),
    dict(id="e66-hmm-clic-sin-pasar-el-viaje",
         pruebas=[HMM_SOLO, HMM_V + "test_elige_la_1st_vessel_y_la_proxima_salida"],
         viejo=('"directa": elegida.get("directa"),\n'
                '                                                          "viaje": _palabras_del_viaje(viaje)}))'),
         nuevo='"directa": elegida.get("directa")}))'),
    dict(id="e66-hmm-anterior-sin-el-viaje", pruebas=[HMM_ANTES],
         viejo="    res_nave = _hmm_leer_anterior(page, list(toks) + list(viaje), reg)\n",
         nuevo="    res_nave = _hmm_leer_anterior(page, toks, reg)\n"),
    dict(id="e66-hmm-anterior-sin-la-cerrada", pruebas=[HMM_ANTES],
         viejo='        if sin_el_viaje.get("idx", -1) >= 0 or sin_el_viaje.get("motivo") == "cerrada":\n',
         nuevo='        if sin_el_viaje.get("idx", -1) >= 0:\n'),
    dict(id="e66-hmm-anterior-como-revisar", pruebas=[HMM_ANTES],
         viejo='        if motivo_nave == "sin_viaje":\n', nuevo='        if motivo_nave == "sin-viaje":\n'),
    # CMA: sin mirar el viaje, como parte de una palabra, sin contar las de la nave, sin pasarle el viaje, su corte como
    # REVISAR, o reservar_cma que sigue.
    dict(id="e66-cma-sin-mirar-el-viaje", pruebas=[CMA_JS],
         viejo="    const matchIdx = cards.findIndex(c => c.matched && c.conViaje);\n",
         nuevo="    const matchIdx = cards.findIndex(c => c.matched);\n"),
    dict(id="e66-cma-viaje-como-parte", pruebas=[CMA_JS],
         viejo="        const conViaje = viaje.length === 0 || (!!tramo && _traeLaNave(voyage.toUpperCase(), viaje));\n",
         nuevo=("        const conViaje = viaje.length === 0 || (!!tramo && viaje.every(x => "
                "voyage.toUpperCase().includes(x)));\n")),
    dict(id="e66-cma-sin-contar-la-nave", pruebas=[CMA_JS],
         viejo="            deLaNave: cards.filter(c => c.matched).length, ilegibles:",
         nuevo="            deLaNave: 0, ilegibles:"),
    dict(id="e66-cma-sin-pasar-el-viaje", pruebas=[CMA_SIN],
         viejo='{"toks": toks, "viaje": _palabras_del_viaje(viaje_pedido)}', nuevo='{"toks": toks, "viaje": []}'),
    dict(id="e66-cma-sin-viaje-como-revisar", pruebas=[CMA_SIN],
         viejo='    de_la_nave = int(ultimo_resultado.get("deLaNave") or 0)\n    if de_la_nave:\n',
         nuevo='    de_la_nave = int(ultimo_resultado.get("deLaNave") or 0)\n    if False:\n'),
    dict(id="e66-cma-reservar-sigue", pruebas=[CMA_SIN],
         viejo=("        if ok_itin is None:     # la nave está, sin el viaje de la fila (encargo 66)\n"
                "            return _no_enviada(reg, detalle_itin)\n"), nuevo=""),
    # El panel: sin mirar el Host, de cualquier puerto o solo 127.0.0.1; sin mirar el origen, o rechazando el suyo; la
    # página dentro de otra; sus recursos para cualquiera; /api/ sin la marca, o con su comienzo; GET o POST sin
    # revisar; la página sin la marca, sin sus cabeceras; la misma marca siempre; otra cabecera, otra forma, otro meta.
    dict(id="e66-sin-mirar-el-host",
         pruebas=[PSP + "test_pedido_ajeno", PSP + "test_de_otro_origen_no_atiende_aunque_traiga_la_marca"],
         viejo=('    if host not in (f"127.0.0.1:{puerto}", f"localhost:{puerto}"):\n'
                '        return "su Host no es el del panel"\n'), nuevo=""),
    dict(id="e66-host-de-cualquier-puerto",
         pruebas=[PSP + "test_pedido_ajeno", PSP + "test_de_otro_origen_no_atiende_aunque_traiga_la_marca"],
         viejo='    if host not in (f"127.0.0.1:{puerto}", f"localhost:{puerto}"):\n',
         nuevo='    if host.split(":")[0] not in ("127.0.0.1", "localhost"):\n'),
    dict(id="e66-host-sin-localhost", pruebas=[PSP + "test_pedido_ajeno", PSP + "test_con_la_marca_desde_su_pagina_atiende"],
         viejo='    if host not in (f"127.0.0.1:{puerto}", f"localhost:{puerto}"):\n',
         nuevo='    if host not in (f"127.0.0.1:{puerto}",):\n'),
    dict(id="e66-sin-mirar-el-origen",
         pruebas=[PSP + "test_pedido_ajeno", PSP + "test_de_otro_origen_no_atiende_aunque_traiga_la_marca"],
         viejo='    if origen and origen != f"http://{host}":\n', nuevo="    if False:\n"),
    dict(id="e66-rechaza-su-origen", pruebas=[PSP + "test_pedido_ajeno", PSP + "test_con_la_marca_desde_su_pagina_atiende"],
         viejo='    if origen and origen != f"http://{host}":\n', nuevo="    if origen:\n"),
    dict(id="e66-la-pagina-dentro-de-otra",
         pruebas=[PSP + "test_pedido_ajeno", PSP + "test_la_pagina_trae_su_marca_y_no_va_dentro_de_otra"],
         viejo='        if sitio in ("cross-site", "same-site") and destino != "document":\n', nuevo="        if False:\n"),
    dict(id="e66-recursos-para-cualquiera",
         pruebas=[PSP + "test_pedido_ajeno", PSP + "test_sus_recursos_solo_para_su_pagina"],
         viejo='    if sitio not in ("", "same-origin"):\n        return "no lo pide la página del panel"\n', nuevo=""),
    dict(id="e66-api-sin-la-marca",
         pruebas=[PSP + "test_pedido_ajeno", PSP + "test_api_sin_la_marca_no_atiende", PSP + "test_cada_panel_su_marca"],
         viejo='    if ruta.startswith("/api/") and not hmac.compare_digest(',
         nuevo='    if False and not hmac.compare_digest('),
    dict(id="e66-marca-por-su-comienzo", pruebas=[PSP + "test_pedido_ajeno", PSP + "test_api_sin_la_marca_no_atiende"],
         viejo=('not hmac.compare_digest(cab(CABECERA_SESION).encode("utf-8"),\n'
                '                                                            str(sesion).encode("utf-8")):'),
         nuevo="not str(sesion).startswith(cab(CABECERA_SESION)):"),
    dict(id="e66-get-sin-revisar",
         pruebas=[PSP + "test_api_sin_la_marca_no_atiende", PSP + "test_de_otro_origen_no_atiende_aunque_traiga_la_marca"],
         viejo=("            u = urlparse(self.path)\n            if self._ajeno(u.path):\n                return\n"
                "            q = parse_qs(u.query)\n            try:\n"
                "                if u.path in (\"/\", \"/index.html\"):"),
         nuevo=("            u = urlparse(self.path)\n            q = parse_qs(u.query)\n            try:\n"
                "                if u.path in (\"/\", \"/index.html\"):")),
    dict(id="e66-post-sin-revisar", pruebas=[PSP + "test_api_sin_la_marca_no_atiende"],
         viejo=('            cuerpo = self.rfile.read(largo) if largo else b""\n'
                '            if por_que:\n'
                '                return self._env(403, "text/plain; charset=utf-8", PEDIDO_AJENO)\n'),
         nuevo='            cuerpo = self.rfile.read(largo) if largo else b""\n'),
    dict(id="e66-pagina-sin-la-marca", pruebas=[PSP + "test_la_pagina_trae_su_marca_y_no_va_dentro_de_otra"],
         viejo=("    pagina = HTML_INDEX.replace(META_SESION, META_SESION.replace('content=\"\"', "
                "f'content=\"{sesion}\"'), 1)\n"),
         nuevo="    pagina = HTML_INDEX\n"),
    dict(id="e66-pagina-sin-sus-cabeceras", pruebas=[PSP + "test_la_pagina_trae_su_marca_y_no_va_dentro_de_otra"],
         viejo="pagina, CABECERAS_DE_LA_PAGINA)", nuevo="pagina)"),
    dict(id="e66-misma-marca-siempre", pruebas=[PSP + "test_cada_panel_su_marca"],
         viejo="    sesion = secrets.token_urlsafe(32)\n",
         nuevo='    sesion = "marca-fija-de-prueba-0123456789-abcdefghijklm"\n'),
    dict(id="e66-otra-cabecera", pruebas=[PSP + "test_las_mismas_constantes"],
         viejo='CABECERA_SESION = "X-AquaShield-Sesion"\n', nuevo='CABECERA_SESION = "X-AquaShield-Marca"\n'),
    dict(id="e66-otra-forma-de-la-marca", pruebas=[PSP + "test_las_mismas_constantes"],
         viejo="RX_SESION = '<meta name=\"aquashield-sesion\" content=\"([A-Za-z0-9_-]+)\">'\n",
         nuevo="RX_SESION = '<meta name=\"aquashield-sesion\" content=\"([A-Za-z0-9]+)\">'\n"),
    dict(id="e66-otro-meta", pruebas=[PSP + "test_las_mismas_constantes"],
         viejo="META_SESION = '<meta name=\"aquashield-sesion\" content=\"\">'\n",
         nuevo="META_SESION = '<meta name=\"aquashield-marca\" content=\"\">'\n"),
    # El lanzador: sin la marca al preguntar o al pedir que se apague, sin leerla, el panel de antes como otro programa,
    # o sin pedirle que se apague si no pudo leer su página.
    dict(id="e66-lanzador-sin-la-marca",
         pruebas=[ARR_V + "test_el_lanzador_pregunta_con_la_marca", ARR_V + "test_instancia_previa_ociosa_se_apaga"],
         viejo="    marca = {CABECERA_SESION: sesion} if sesion else {}\n", nuevo="    marca = {}\n"),
    dict(id="e66-apagar-sin-la-marca", pruebas=[ARR_V + "test_el_lanzador_pregunta_con_la_marca"],
         viejo="                                     headers={CABECERA_SESION: sesion} if sesion else {})\n",
         nuevo="                                     headers={})\n"),
    dict(id="e66-sesion-nunca", pruebas=[ARR_V + "test_el_lanzador_pregunta_con_la_marca"],
         viejo='    m = _re.search(RX_SESION, pagina)\n    return m.group(1) if m else ""\n', nuevo='    return ""\n'),
    dict(id="e66-panel-de-antes-como-otro", pruebas=[ARR_V + "test_ocioso_que_tarda_en_soltar_el_puerto"],
         viejo="    except urllib.error.HTTPError:\n        sesion = \"\"\n    except http.client.HTTPException:\n",
         nuevo="    except urllib.error.HTTPError:\n        return False\n    except http.client.HTTPException:\n"),
    # La página que cierra sin contestar, como nadie (la pregunta a «/» va antes que la de /api/estado; el censo del
    # encargo 66 lo vio: e52-panel-en-cierre-como-nadie dejó de morder, y su prueba tiene ahora el caso de la página
    # que contesta y /api/estado que cierra).
    dict(id="e66-pagina-cierra-como-nadie", pruebas=[ARR_V + "test_panel_en_dice_quien_contesta"],
         viejo="        sesion = \"\"\n    except http.client.HTTPException:\n        return False\n",
         nuevo="        sesion = \"\"\n    except http.client.HTTPException:\n        return None\n"),
    dict(id="e66-sin-apagar-al-de-antes", pruebas=[ARR_V + "test_ocioso_que_tarda_en_soltar_el_puerto"],
         viejo=('    except Exception:\n        sesion = ""\n    try:\n'
                '        req = urllib.request.Request(f"http://127.0.0.1:{puerto}/api/apagar"'),
         nuevo=('    except Exception:\n        return False\n    try:\n'
                '        req = urllib.request.Request(f"http://127.0.0.1:{puerto}/api/apagar"')),
    # La página: sin la marca, sin sus otras cabeceras, sin renovarla, renovándola con la misma; la descarga sin el
    # nombre del panel, con un nombre fijo, o por una navegación.
    dict(id="e66-js-sin-la-marca",
         pruebas=[MSE + "test_cada_pedido_con_la_marca_y_una_renovacion", PSP + "test_las_mismas_constantes"],
         viejo='  o.headers = Object.assign({}, o.headers || {}, { "X-AquaShield-Sesion": SESION });\n',
         nuevo="  o.headers = Object.assign({}, o.headers || {});\n"),
    dict(id="e66-js-pisa-sus-cabeceras", pruebas=[MSE + "test_cada_pedido_con_la_marca_y_una_renovacion"],
         viejo='  o.headers = Object.assign({}, o.headers || {}, { "X-AquaShield-Sesion": SESION });\n',
         nuevo='  o.headers = Object.assign({}, { "X-AquaShield-Sesion": SESION });\n'),
    dict(id="e66-js-sin-renovar", pruebas=[MSE + "test_cada_pedido_con_la_marca_y_una_renovacion"],
         viejo="  if (r.status === 403 && await renovarSesion(usada)) r = await fetch(ruta, conSesion(opts));\n", nuevo=""),
    dict(id="e66-js-renueva-con-la-misma", pruebas=[MSE + "test_cada_pedido_con_la_marca_y_una_renovacion"],
         viejo="    if (!m || m[1] === usada) return false;\n", nuevo="    if (!m) return false;\n"),
    dict(id="e66-descarga-sin-su-nombre", pruebas=[MSE + "test_la_descarga_con_la_marca"],
         viejo='    a.download = nombreDeDescarga(r.headers.get("Content-Disposition"));\n',
         nuevo='    a.download = "planilla.xlsx";\n'),
    dict(id="e66-nombre-de-descarga-fijo", pruebas=[MSE + "test_la_descarga_con_la_marca"],
         viejo='  return m ? m[1] : "planilla - resultados.xlsx";\n', nuevo='  return "planilla - resultados.xlsx";\n'),
    dict(id="e66-descarga-por-navegacion", pruebas=[MSE + "test_la_descarga_con_la_marca"],
         viejo='    const r = await pedir("/api/descargar");\n',
         nuevo='    window.location = "/api/descargar"; return;\n    const r = await pedir("/api/descargar");\n'),
]

# Encargo 67 (CICLO-revisiones-msc-y-cma.md): MSC vuelve a leer la tarjeta antes del clic; CMA-CGM compara la nave y el
# viaje con el primer tramo; y lo técnico de la revisión de código del encargo 66 (el cuerpo de un POST, la descarga, la
# renovación de la marca, la espera del lanzador y las palabras del viaje).
MSC67, CMA67 = "test_clics.TestMsc.", "test_clics.TestCma."
MSC_RELEE, MSC_CORTA = MSC67 + "test_js_clic_vuelve_a_leer_la_tarjeta", MSC67 + "test_si_la_tarjeta_cambio_no_pulsa"
CMA_TRAMO = CMA67 + "test_js_rutas_solo_el_primer_tramo"
CMA_ILEGIBLES = CMA67 + "test_itinerario_dice_las_rutas_que_no_pudo_leer"
MUTACIONES += [
    # MSC: el clic sin volver a leer, sin mirar la ETA, sin mirar el «Select», con dos «Select»; reservar_msc que sigue
    # sin pulsar, que no le pasa lo que leyó, que da por pulsado lo que falló; el motivo de la falla; el motivo ya
    # escrito que no se usa.
    dict(id="e67-msc-clic-sin-releer", pruebas=[MSC_RELEE],
         viejo="    if(t.nave!==args.nave || t.etd!==args.etd || t.eta!==args.eta) return 'otra';\n", nuevo=""),
    dict(id="e67-msc-clic-sin-la-eta", pruebas=[MSC_RELEE],
         viejo="t.etd!==args.etd || t.eta!==args.eta) return 'otra';", nuevo="t.etd!==args.etd) return 'otra';"),
    dict(id="e67-msc-clic-sin-mirar-el-select", pruebas=[MSC_RELEE],
         viejo="    if(!t.sel) return 'sin-select';\n", nuevo=""),
    dict(id="e67-msc-clic-con-varios-select", pruebas=[MSC_RELEE],
         viejo="    if(bs.length!==1) return 'varios-select';\n", nuevo="    if(!bs.length) return 'varios-select';\n"),
    dict(id="e67-msc-sigue-sin-pulsar", pruebas=[MSC_CORTA],
         viejo=("        if pulso != MSC_PULSADO:\n            return _msc_salida_ambigua(page, reg, reserva, [elegida], "
                "\"\", desde, por_que=_msc_no_pulse(pulso))\n"), nuevo=""),
    dict(id="e67-msc-clic-sin-lo-leido", pruebas=[MS + "test_reservar_msc_no_toma_la_primera"],
         viejo='pulso = page.evaluate(_JS_MSC_CLIC_NAVE, {"i": elegida["i"], "nave": elegida.get("nave", ""),',
         nuevo='pulso = page.evaluate(_JS_MSC_CLIC_NAVE, {"i": elegida["i"], "nave": "",'),
    dict(id="e67-msc-falla-como-pulsado", pruebas=[MSC_CORTA],
         viejo='            pulso = f"error: {str(e)[:60]}"\n', nuevo="            pulso = MSC_PULSADO\n"),
    dict(id="e67-msc-motivo-de-la-falla", pruebas=[MSC_CORTA],
         viejo=('        return f"el JavaScript que vuelve a leer la tarjeta elegida y la pulsa falló '
                '({str(pulso)[7:]})"\n'), nuevo='        return "falló"\n'),
    dict(id="e67-msc-sin-el-motivo-escrito", pruebas=[MSC_CORTA],
         viejo=("    if por_que is None:\n"
                "        por_que = _por_que_sin_salida(motivo, _msc_salidas(exacta), desde, _msc_transito)\n"),
         nuevo="    por_que = _por_que_sin_salida(motivo, _msc_salidas(exacta), desde, _msc_transito)\n"),
    # CMA: la nave o el viaje del texto de la tarjeta, sin mirar el POL, el segundo tramo, con dos «Buque», sin contar
    # las ilegibles, el motivo sin ellas.
    dict(id="e67-cma-nave-del-texto", pruebas=[CMA_TRAMO],
         viejo="        const matched = !!tramo && _traeLaNave(vessel.toUpperCase(), toks);\n",
         nuevo="        const matched = _traeLaNave(txt.toUpperCase(), toks);\n"),
    dict(id="e67-cma-viaje-del-texto", pruebas=[CMA_TRAMO],
         viejo="        const conViaje = viaje.length === 0 || (!!tramo && _traeLaNave(voyage.toUpperCase(), viaje));\n",
         nuevo="        const conViaje = viaje.length === 0 || _traeLaNave(txt.toUpperCase(), viaje);\n"),
    dict(id="e67-cma-sin-el-pol", pruebas=[CMA_TRAMO],
         viejo="        if (pols.length !== 1) return null;\n        const tramo = lis[lis.indexOf(pols[0]) + 1];\n",
         nuevo="        const tramo = lis.find(li => li.matches('li.more-infos.vessel'));\n"),
    dict(id="e67-cma-segundo-tramo", pruebas=[CMA_TRAMO],
         viejo="        const tramo = lis[lis.indexOf(pols[0]) + 1];\n",
         nuevo="        const tramo = lis.filter(li => li.matches('li.more-infos.vessel')).pop();\n"),
    dict(id="e67-cma-con-dos-buques", pruebas=[CMA_TRAMO],
         viejo="        if (buque.length !== 1 || ref.length !== 1 || !buque[0] || !ref[0]) return null;\n",
         nuevo="        if (!buque[0] || !ref[0]) return null;\n"),
    dict(id="e67-cma-sin-contar-las-ilegibles", pruebas=[CMA_TRAMO],
         viejo="ilegibles: cards.filter(c => !c.legible).length,", nuevo="ilegibles: 0,"),
    dict(id="e67-cma-motivo-sin-las-ilegibles", pruebas=[CMA_ILEGIBLES],
         viejo=('    sin_leer = (f"; no pude leer el primer tramo (la nave que sale de Chile) de {ilegibles} de las "\n'
                "                f\"{int(ultimo_resultado.get('cardsCount') or ilegibles)} rutas\" "
                "if ilegibles else \"\")\n"),
         nuevo='    sin_leer = ""\n'),
    # El POST: el de otro origen se lee entero, o se atiende como uno sin la marca; sin el tope; un largo con cifras que
    # no son ASCII.
    dict(id="e67-post-ajeno-se-lee-entero", pruebas=[PSP + "test_un_post_de_otro_origen_no_se_lee"],
         viejo="                if largo is not None and largo <= DESCARTE_MAX:\n",
         nuevo="                if largo is not None:\n"),
    dict(id="e67-post-ajeno-como-sin-la-marca", pruebas=[PSP + "test_un_post_de_otro_origen_no_se_lee"],
         viejo="            if por_que and por_que != SIN_LA_MARCA:\n", nuevo="            if False:\n"),
    dict(id="e67-cuerpo-sin-tope", pruebas=[PSP + "test_un_cuerpo_fuera_de_medida_no_se_lee"],
         viejo="    return largo if largo <= CUERPO_MAX else None\n", nuevo="    return largo\n"),
    dict(id="e67-largo-con-otras-cifras", pruebas=[PSP + "test_un_cuerpo_fuera_de_medida_no_se_lee"],
         viejo="    if not (texto.isascii() and texto.isdigit()):\n", nuevo="    if not texto.isdigit():\n"),
    # La revisión de seguridad: sin plazo por pedido, con dos Host, la página que se guarda en la caché.
    dict(id="e67-sin-plazo-por-pedido", pruebas=[PSP + "test_un_pedido_mudo_no_retiene_el_panel"],
         viejo="        timeout = PANEL_PLAZO_PEDIDO                 # revisión de seguridad del encargo 67\n", nuevo=""),
    dict(id="e67-dos-host-pasan", pruebas=[PSP + "test_pedido_ajeno"],
         viejo=('    if hasattr(cabeceras, "get_all") and len(cabeceras.get_all("Host") or []) > 1:\n'
                '        return "su Host no es el del panel"\n'), nuevo=""),
    dict(id="e67-pagina-en-la-cache", pruebas=[PSP + "test_la_pagina_trae_su_marca_y_no_va_dentro_de_otra"],
         viejo='            self.send_header("Cache-Control", "no-store")\n', nuevo=""),
    # La descarga: el nombre con latin-1, sin filename* en ASCII; la página sin leer filename*, o sin su respaldo.
    dict(id="e67-descarga-en-latin1", pruebas=[PL + "test_descarga_con_un_nombre_fuera_de_latin1"],
         viejo="c if 32 <= ord(c) < 127 and c not in", nuevo="c if 32 <= ord(c) < 256 and c not in"),
    dict(id="e67-descarga-sin-codificar", pruebas=[PL + "test_descarga_con_un_nombre_fuera_de_latin1"],
         viejo="filename*=UTF-8''{quote(nombre, safe='')}", nuevo="filename*=UTF-8''{nombre}"),
    dict(id="e67-js-sin-filename-estrella", pruebas=[MSE + "test_el_nombre_de_la_descarga"],
         viejo="  if (u) { try { return decodeURIComponent(u[1]); } catch (e) { /* sigue con filename */ } }\n",
         nuevo=""),
    dict(id="e67-js-filename-estrella-sin-respaldo", pruebas=[MSE + "test_el_nombre_de_la_descarga"],
         viejo="  if (u) { try { return decodeURIComponent(u[1]); } catch (e) { /* sigue con filename */ } }\n",
         nuevo="  if (u) return decodeURIComponent(u[1]);\n"),
    # La renovación comparando con la marca de ahora (dos pedidos a la vez); la espera corta del lanzador; las palabras
    # del viaje con las de una letra.
    dict(id="e67-js-compara-con-la-de-ahora", pruebas=[MSE + "test_dos_pedidos_a_la_vez_con_la_marca_vieja"],
         viejo="    if (!m || m[1] === usada) return false;\n", nuevo="    if (!m || m[1] === SESION) return false;\n"),
    dict(id="e67-apagar-con-la-espera-corta", pruebas=[ARR_V + "test_el_apagar_lee_la_marca_con_la_espera_larga"],
         viejo="        sesion = _sesion_del_panel(puerto, PANEL_ESPERA_LARGA)\n",
         nuevo="        sesion = _sesion_del_panel(puerto)\n"),
    dict(id="e67-palabras-de-una-letra", pruebas=[VJ + "test_las_palabras_del_viaje"],
         viejo='    return [p for p in str(viaje or "").upper().split() if len(p) > 1]\n',
         nuevo='    return str(viaje or "").upper().split()\n'),
]

# Encargo 69 (CICLO-plazo-de-entrega-maersk.md): el plazo de entrega de la salida elegida de MAERSK, en el motivo de la
# fecha de retiro cuando el calendario no tiene un día que cumpla la regla.
PLAZO_JS = ("            if (!plazo && (l.textContent || '').trim().toLowerCase() === '\"\"\" + "
            "MK_PLAZO_DE_ENTREGA.lower() + \"\"\"') {\n"
            "                plazo = (v.textContent || '').replace(/\\\\s+/g, ' ').trim();\n            }\n")
PZ_JS = MK + "test_js_salidas_lee_el_plazo_de_entrega"
PZ_JS_A = MK + "test_js_salidas_lee_la_salida_y_si_se_puede_reservar"
PZ_ELEGIDA = MK + "test_la_elegida_guarda_su_plazo_de_entrega"
PZ_LLAMADA = MK + "test_sin_una_salida_no_llega_a_la_guarda"
PZ_NO_DEJA = RT + "test_el_plazo_de_entrega_que_no_deja_retirar"
PZ_MOTIVO = RT + "test_el_motivo_dice_el_plazo_de_entrega"
PZ_PASA = RT + "test_reservar_maersk_le_pasa_el_plazo_de_la_elegida"

MUTACIONES += [
    # La lectura: sin el plazo, sin juntar los espacios, el último y no el primero.
    dict(id="e69-js-sin-plazo", pruebas=[PZ_JS, PZ_JS_A], viejo=PLAZO_JS, nuevo=""),
    dict(id="e69-js-plazo-sin-espacios", pruebas=[PZ_JS],
         viejo="                plazo = (v.textContent || '').replace(/\\\\s+/g, ' ').trim();\n",
         nuevo="                plazo = (v.textContent || '').trim();\n"),
    dict(id="e69-js-el-ultimo-plazo", pruebas=[PZ_JS],
         viejo="            if (!plazo && (l.textContent || '')", nuevo="            if ((l.textContent || '')"),
    # La elección: no lo guarda, lo guarda sin juntar los espacios, no lo dice en log.txt.
    dict(id="e69-elegida-sin-plazo", pruebas=[PZ_ELEGIDA],
         viejo='                    eleccion["plazo"] = plazo\n', nuevo='                    eleccion["plazo"] = ""\n'),
    dict(id="e69-elegida-plazo-crudo", pruebas=[PZ_ELEGIDA],
         viejo='                plazo = " ".join(str(elegida.get("plazo") or "").split())\n',
         nuevo='                plazo = str(elegida.get("plazo") or "")\n'),
    dict(id="e69-log-sin-plazo", pruebas=[PZ_ELEGIDA],
         viejo=('                         + (f"; plazo de entrega («{MK_PLAZO_DE_ENTREGA}»): {plazo}" '
                'if plazo else ""))\n'),
         nuevo='                         + "")\n'),
    # reservar_maersk: no le pasa 'eleccion' a la elección, o el plazo a la fecha de retiro.
    dict(id="e69-no-le-pasa-eleccion", pruebas=[PZ_PASA, PZ_LLAMADA],
         viejo="    modo, sin_una, sin_nave, sin_book = _mk_elegir_nave(page, reserva, reg, eleccion)\n",
         nuevo="    modo, sin_una, sin_nave, sin_book = _mk_elegir_nave(page, reserva, reg)\n"),
    dict(id="e69-no-le-pasa-el-plazo", pruebas=[PZ_PASA, RT_ORDEN],
         viejo='            corte = _mk_fecha_de_retiro(page, reg, det, f, plazo=eleccion.get("plazo", ""))\n',
         nuevo="            corte = _mk_fecha_de_retiro(page, reg, det, f)\n"),
    # La fecha de retiro: el motivo de siempre aunque el plazo lo explique.
    dict(id="e69-motivo-de-siempre", pruebas=[PZ_MOTIVO],
         viejo="        if no_deja:\n            return _no_enviada(reg, f\"MAERSK: {no_deja}; {_MK_NADA_MAS}\")\n",
         nuevo="        if False:\n            return _no_enviada(reg, f\"MAERSK: {no_deja}; {_MK_NADA_MAS}\")\n"),
    # _mk_plazo_no_deja: el plazo del mismo día, o posterior, lo explicaría; sin el plazo, no infiere, o infiere sin
    # días habilitados, sin el día a la vista, o con el último habilitado el mismo día que toca.
    dict(id="e69-plazo-igual-no-deja", pruebas=[PZ_NO_DEJA],
         viejo="        if cuando >= objetivo:\n", nuevo="        if cuando > objetivo:\n"),
    dict(id="e69-plazo-posterior-no-deja", pruebas=[PZ_NO_DEJA, PZ_MOTIVO],
         viejo="        if cuando >= objetivo:\n            return \"\"\n",
         nuevo="        if cuando >= objetivo:\n            pass\n"),
    dict(id="e69-sin-plazo-no-infiere", pruebas=[PZ_NO_DEJA, PZ_MOTIVO],
         viejo="    elif not (fechas and min(fechas)", nuevo="    elif True or not (fechas and min(fechas)"),
    dict(id="e69-sin-plazo-sin-habilitados", pruebas=[PZ_NO_DEJA],
         viejo="and habilitados and habilitados[-1] < objetivo):",
         nuevo="and (not habilitados or habilitados[-1] < objetivo)):"),
    dict(id="e69-sin-plazo-fuera-de-vista", pruebas=[PZ_NO_DEJA],
         viejo="    elif not (fechas and min(fechas) <= objetivo <= max(fechas) and habilitados",
         nuevo="    elif not (fechas and habilitados"),
    dict(id="e69-sin-plazo-el-mismo-dia", pruebas=[PZ_NO_DEJA],
         viejo="habilitados and habilitados[-1] < objetivo):", nuevo="habilitados and habilitados[-1] <= objetivo):"),
    # El texto: sin el plazo, sin la salida posterior, con el primer habilitado, sin el recorte.
    dict(id="e69-texto-sin-el-plazo", pruebas=[PZ_NO_DEJA, PZ_MOTIVO],
         viejo="    visto = f\" («{MK_PLAZO_DE_ENTREGA}»: {plazo})\" if cuando is not None else \"\"\n",
         nuevo="    visto = \"\"\n"),
    dict(id="e69-texto-sin-salida-posterior", pruebas=[PZ_NO_DEJA, PZ_MOTIVO],
         viejo="ni después ({calendario}): hay que usar una salida posterior\")",
         nuevo="ni después ({calendario})\")"),
    dict(id="e69-texto-el-primer-habilitado", pruebas=[PZ_NO_DEJA],
         viejo="calendario de retiro es el {habilitados[-1]:%d-%m-%Y}\"",
         nuevo="calendario de retiro es el {habilitados[0]:%d-%m-%Y}\""),
    dict(id="e69-texto-sin-recorte", pruebas=[PZ_NO_DEJA],
         viejo="    plazo = \" \".join(str(plazo or \"\").split())[:40]\n",
         nuevo="    plazo = \" \".join(str(plazo or \"\").split())\n"),
]

# --- Encargo 71 (CICLO-hyundai-login-fijo.md): el login de HYUNDAI va siempre a su página de login, escrita en el
# programa, sin leer la `url` de las credenciales, como MAERSK (decisión de Marcelo). ---
HMM_LOGIN_VA = "test_clics.TestHyundai.test_el_login_va_siempre_a_su_pagina"
HMM_IR = '        page.goto(HMM_LOGIN, wait_until="domcontentloaded")\n'

MUTACIONES += [
    # Como hasta el encargo 70: la url de las credenciales, y solo sin ella la página del login.
    dict(id="e71-login-lee-la-url", pruebas=[HMM_LOGIN_VA],
         viejo=HMM_IR, nuevo='        page.goto(creds.get("url") or HMM_LOGIN, wait_until="domcontentloaded")\n'),
    # La url de las credenciales si trae la llave, aunque venga vacía.
    dict(id="e71-login-la-llave-primero", pruebas=[HMM_LOGIN_VA],
         viejo=HMM_IR, nuevo='        page.goto(creds.get("url", HMM_LOGIN), wait_until="domcontentloaded")\n'),
    # La url de las credenciales solo si es otra página de e-service (la encontró la revisión de código del encargo).
    dict(id="e71-login-la-llave-si-es-de-e-service", pruebas=[HMM_LOGIN_VA],
         viejo=HMM_IR, nuevo='        page.goto(creds.get("url") if str(creds.get("url") or "").startswith('
                             '"https://www.hmm21.com/e-service/") else HMM_LOGIN, wait_until="domcontentloaded")\n'),
    # Otra página: la portada que trae la plantilla.
    dict(id="e71-login-a-la-portada", pruebas=[HMM_LOGIN_VA],
         viejo='HMM_LOGIN = "https://www.hmm21.com/e-service/auth/login.do"\n',
         nuevo='HMM_LOGIN = "https://www.hmm21.com/"\n'),
]

# --- Encargo 72 (CICLO-guarda-de-datos.md): la guarda de datos reales. Lo que entra al repo, que es público, no trae
# razones sociales ni datos con la forma de un dato real; la suite lo revisa y el hook pre-commit lo frena. Los valores
# inventados van armados por partes: escritos enteros, la guarda los encontraría en este archivo. ---
GD = "test_guarda_datos."
GD_MUESTRAS = GD + "TestDetector.test_cada_muestra_da_lo_suyo"
GD_PERMITIDOS = GD + "TestDetector.test_la_lista_de_permitidos_esta_fija"
GD_VALOR = GD + "TestDetector.test_nunca_muestra_el_valor"
GD_REPO = GD + "TestLectura.test_control_del_repo_inventado"
GD_INDICE = GD + "TestLectura.test_control_del_indice"
GD_VERSIONADO = GD + "TestLoVersionado.test_lo_versionado_no_trae_datos_reales"
GD_FRENA = GD + "TestElHook.test_frena_un_commit_con_una_razon_social"
GD_LIMPIO = GD + "TestElHook.test_deja_pasar_un_commit_limpio"
GD_LEE_INDICE = GD + "TestElHook.test_lee_el_indice_que_se_commitea"
GD_MERGE = GD + "TestElHook.test_frena_el_commit_de_un_merge"
GD_LF = GD + "TestElHook.test_los_hooks_van_en_lf_y_ascii"
GUARDA = "tests/guarda_datos.py"
HOOK = ".githooks/pre-commit"
HOOK_MERGE = ".githooks/pre-merge-commit"

MUTACIONES += [
    # El detector: sin las razones sociales con la forma detrás; la propia empresa por «termina en», o apartada también
    # detrás de un espacio; cualquier número como inventado; sin las letras sueltas; la lista de formas sin su coma.
    dict(id="e72-sin-razones-detras", archivo=GUARDA, pruebas=[GD_MUESTRAS, GD_VALOR],
         viejo="    for m in RAZON_DETRAS.finditer(p):\n", nuevo='    for m in RAZON_DETRAS.finditer(""):\n'),
    dict(id="e72-permitido-por-sufijo", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo="        if clave(trozo) == clave(valor) and not pegado:\n",
         nuevo="        if clave(trozo).endswith(clave(valor)) and not pegado:\n"),
    dict(id="e72-propia-tras-un-espacio", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo="rx = re.compile(r\"(?<![\\w\\s.&'’-])\" + re.escape(valor)",
         nuevo="rx = re.compile(r\"(?<![\\w.&'’-])\" + re.escape(valor)"),
    dict(id="e72-todo-numero-inventado", archivo=GUARDA, pruebas=[GD_MUESTRAS, GD_VALOR],
         viejo="        if evidente(cifras):\n", nuevo="        if True:\n"),
    dict(id="e72-sin-letras-sueltas", archivo=GUARDA, pruebas=[GD_MUESTRAS, GD_VERSIONADO],
         viejo="        elif all(len(w) == 1 for w in clave(m.group(0)).split()) and re.match(",
         nuevo="        elif False and re.match("),
    dict(id="e72-lista-sin-coma", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo='        elif not delante and re.search(r"[,/]", p[m.end(1):m.start(2)]) and all(\n',
         nuevo="        elif not delante and all(\n"),
    # La tipografía como en NEPPEX (las cinco palabras que siguen): un comentario del CSS del panel sigue abajo. Y sin
    # apartar las formas de la guarda en su propio archivo.
    dict(id="e72-tipografia-como-neppex", archivo=GUARDA, pruebas=[GD_VERSIONADO],
         viejo="len(palabras) > 1 and palabras[1][:1].isupper()):",
         nuevo="any(w[:1].isupper() for w in palabras[1:])):"),
    dict(id="e72-sin-apartar-sus-formas", archivo=GUARDA, pruebas=[GD_VERSIONADO],
         viejo="    if archivo != PROPIO:\n        return t\n    lineas = t.split",
         nuevo="    return t\n    lineas = t.split"),
    # Una razón social inventada en el programa: la suite la ve en la copia del censo.
    dict(id="e72-razon-social-en-el-programa", pruebas=[GD_VERSIONADO],
         viejo="def _mk_paso_actual(page):\n",
         nuevo="def _mk_paso_actual(page):\n    # Pesquera Inventada " + chr(83) + ".A.\n"),
    # La lista fija: un permitido de más.
    dict(id="e72-un-permitido-de-mas", archivo=GUARDA, pruebas=[GD_PERMITIDOS],
         viejo="PERMITIDOS = (\n", nuevo='PERMITIDOS = (\n    ("correo", "alguien" + "@" + "otro.cl", "x"),\n'),
    # El nombre de un archivo, con sus cifras.
    dict(id="e72-muestra-las-cifras", archivo=GUARDA, pruebas=[GD_VALOR],
         viejo='    return re.sub(r"\\d{5,}", "<cifras>", ruta) + sufijo\n', nuevo="    return ruta + sufijo\n"),
    # La lectura: sin lo que el índice guarda distinto del árbol, sin los nombres, siguiendo una unión que sale del
    # repo.
    dict(id="e72-sin-el-indice-distinto", archivo=GUARDA, pruebas=[GD_REPO],
         viejo="    for rel, datos in _del_indice(raiz).items():\n", nuevo="    for rel, datos in {}.items():\n"),
    dict(id="e72-sin-los-nombres", archivo=GUARDA, pruebas=[GD_REPO],
         viejo='        revisar_texto(rel, rel + " (nombre)", cuenta)   # el nombre también entra al repo\n', nuevo=""),
    dict(id="e72-sigue-la-union", archivo=GUARDA, pruebas=[GD_REPO],
         viejo="            elif ruta == pathlib.Path(raiz) / rel and not ruta.resolve().is_relative_to(adentro):\n",
         nuevo="            elif False:\n"),
    # El índice: el de siempre y no el que se le pasa; un objeto que no se lee, por limpio.
    dict(id="e72-el-indice-de-siempre", archivo=GUARDA, pruebas=[GD_INDICE],
         viejo='    for e in _git(raiz, "ls-files", "-s", "-z", indice=indice).split(b"\\0"):\n',
         nuevo='    for e in _git(raiz, "ls-files", "-s", "-z").split(b"\\0"):\n'),
    dict(id="e72-ilegible-por-limpio", archivo=GUARDA, pruebas=[GD_INDICE],
         viejo="    if ilegibles:\n        return True, (", nuevo="    if False:\n        return True, ("),
    # El hook: no corre la guarda (deja pasar, o frena todo), no lee el índice que git le pasa, el merge sin guarda, y
    # un CR que /bin/sh no lee.
    dict(id="e72-hook-deja-pasar", archivo=HOOK, pruebas=[GD_FRENA, GD_LEE_INDICE, GD_MERGE],
         viejo='exec python -I "$guarda" --pre-commit\n', nuevo="exit 0\n"),
    dict(id="e72-hook-frena-todo", archivo=HOOK, pruebas=[GD_LIMPIO, GD_LEE_INDICE],
         viejo='exec python -I "$guarda" --pre-commit\n', nuevo="exit 1\n"),
    dict(id="e72-hook-sin-el-indice-de-git", archivo=GUARDA, pruebas=[GD_LEE_INDICE],
         viejo='    puesto = os.environ.get("GIT_INDEX_FILE")\n', nuevo="    puesto = None\n"),
    dict(id="e72-merge-sin-guarda", archivo=HOOK_MERGE, pruebas=[GD_MERGE],
         viejo='exec sh "$(dirname "$0")/pre-commit"\n', nuevo="exit 0\n"),
    dict(id="e72-hook-con-cr", archivo=HOOK, pruebas=[GD_LF], viejo="#!/bin/sh\n", nuevo="#!/bin/sh\r\n"),
]

# Lo de la revisión de seguridad del encargo 72: el nombre de un archivo con un dato, los binarios, el correo detrás de
# «:», el plazo de git, la expresión que retrocedía, los invisibles, Windows-1252, las iniciales y los permitidos
# exactos.
GD_PLAZO = GD + "TestLimites.test_el_plazo_de_git_se_cumple"
GD_TIRA = GD + "TestLimites.test_un_archivo_hecho_para_colgarla_no_la_cuelga"

MUTACIONES += [
    dict(id="e72-nombre-con-dato-a-la-vista", archivo=GUARDA, pruebas=[GD_VALOR],
         viejo="    if con_dato(ruta):\n", nuevo="    if False:\n"),
    dict(id="e72-binario-pasa", archivo=GUARDA, pruebas=[GD_INDICE],
         viejo="    if binarios:\n        return True, (", nuevo="    if False:\n        return True, ("),
    dict(id="e72-correo-tras-dos-puntos", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo='        if "://" in t[inicio:m.start()]:\n', nuevo='        if t[:m.start()].endswith(":"):\n'),
    dict(id="e72-git-sin-matar-el-arbol", archivo=GUARDA, pruebas=[GD_PLAZO],
         viejo='    if os.name == "nt":\n        taskkill = ', nuevo='    if False:\n        taskkill = '),
    dict(id="e72-git-espera-sin-plazo", archivo=GUARDA, pruebas=[GD_PLAZO],
         viejo="        p.communicate(timeout=10)\n", nuevo="        p.communicate()\n"),
    dict(id="e72-etiqueta-sin-tope", archivo=GUARDA, pruebas=[GD_TIRA],
         viejo=(r'r"(?i:booking(?:\s{1,20}(?:number|no\.?|n[°º])(?:\s{0,20}:)?|\s{0,3}:))"' + "\n"
                + r'                                  r"\s{0,20}(\d{9})(?!\d)"'),
         nuevo=(r'r"(?i:booking(?:\s+(?:number|no\.?|n[°º])\s*:?|\s*:))"' + "\n"
                + r'                                  r"\s*(\d{9})(?!\d)"')),
    dict(id="e72-sin-quitar-invisibles", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo='unicodedata.normalize("NFC", texto).translate(INVISIBLES)',
         nuevo='unicodedata.normalize("NFC", texto)'),
    dict(id="e72-latin-con-reemplazos", archivo=GUARDA, pruebas=[GD_REPO],
         viejo='            texto = datos.decode("cp1252", "replace")\n',
         nuevo='            texto = datos.decode("utf-8", "replace")\n'),
    dict(id="e72-iniciales-como-letras-sueltas", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo=' and re.match(r"\\s[^\\W\\d_](?![^\\W_])", p[m.end():]):\n', nuevo=":\n"),
    dict(id="e72-permitido-con-algo-pegado", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo="        if clave(trozo) == clave(valor) and not pegado:\n",
         nuevo="        if clave(trozo) == clave(valor):\n"),
    dict(id="e72-correo-sin-su-puntuacion", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo="            if texto.lower() == valor.lower():\n",
         nuevo="            if clave(texto) == clave(valor):\n"),
]

# Lo de la revisión de código del encargo 72: los dígitos verificadores contra un cálculo aparte, cada forma y cada
# separador, la huella del bloque de las formas, la falla cerrada del hook y de la guarda, y el .gitignore.
GD_DV = GD + "TestDetector.test_los_digitos_verificadores"
GD_FORMAS = GD + "TestDetector.test_cada_forma_y_cada_separador"
GD_HUELLA = GD + "TestDetector.test_las_formas_de_la_guarda_estan_fijas"
GD_SIN_GUARDA = GD + "TestElHook.test_sin_la_guarda_o_sin_python_frena"
GD_SIN_INDICE = GD + "TestElHook.test_sin_indice_o_con_el_detector_roto_frena"
GD_GITIGNORE = GD + "TestElHook.test_gitignore_versiona_los_hooks"

MUTACIONES += [
    dict(id="e72-rut-con-otros-pesos", archivo=GUARDA, pruebas=[GD_DV],
         viejo="        m = 2 if m == 7 else m + 1\n", nuevo="        m = 2 if m == 8 else m + 1\n"),
    dict(id="e72-iso-sin-saltar-los-once", archivo=GUARDA, pruebas=[GD_DV],
         viejo="        if n % 11 == 0:\n", nuevo="        if n % 10 == 0:\n"),
    dict(id="e72-abreviatura-solo-en-mayusculas", archivo=GUARDA, pruebas=[GD_FORMAS],
         viejo='    return "(?:" + r"\\.?\\s?".join(letras) + "|" + _libre(letras) + r")\\.?"\n',
         nuevo='    return "(?:" + r"\\.?\\s?".join(letras) + r")\\.?"\n'),
    dict(id="e72-sin-el-separador-de-porcentaje", archivo=GUARDA, pruebas=[GD_FORMAS],
         viejo='    (re.compile(r"%[0-9A-Fa-f]{2}"), " "),\n', nuevo=""),
    dict(id="e72-delante-solo-la-primera", archivo=GUARDA, pruebas=[GD_FORMAS],
         viejo='"|".join(FORMAS_DELANTE) + r")\\s{1,8}(" + NOMBRE + ")")',
         nuevo='"|".join(FORMAS_DELANTE[:1]) + r")\\s{1,8}(" + NOMBRE + ")")'),
    dict(id="e72-otra-cosa-en-las-formas", archivo=GUARDA, pruebas=[GD_HUELLA],
         viejo="RESTO = r\"[\\w&'’]{0,59}\\.?\"", nuevo="RESTO = r\"[\\w&'’]{0,58}\\.?\""),
    dict(id="e72-marcas-sin-falla-cerrada", archivo=GUARDA, pruebas=[GD_HUELLA],
         viejo="    if len(desde) != 1 or len(hasta) != 1 or desde[0] > hasta[0]:\n", nuevo="    if not desde:\n"),
    dict(id="e72-hook-sin-mirar-python", archivo=HOOK, pruebas=[GD_SIN_GUARDA],
         viejo="if ! command -v python >/dev/null 2>&1; then\n", nuevo="if false; then\n"),
    dict(id="e72-hook-sin-mirar-la-guarda", archivo=HOOK, pruebas=[GD_SIN_GUARDA],
         viejo='if [ ! -f "$guarda" ]; then\n', nuevo="if false; then\n"),
    dict(id="e72-indice-que-no-existe", archivo=GUARDA, pruebas=[GD_SIN_INDICE],
         viejo="    if not indice.is_file():\n", nuevo="    if False:\n"),
    dict(id="e72-detector-roto-pasa", archivo=GUARDA, pruebas=[GD_SIN_INDICE],
         viejo='    if rotas:\n        print(f"pre-commit: FRENADO.',
         nuevo='    if False:\n        print(f"pre-commit: FRENADO.'),
    dict(id="e72-gitignore-sin-los-hooks", archivo=".gitignore", pruebas=[GD_GITIGNORE],
         viejo="!/.githooks/\n", nuevo=""),
]

# --- Encargo 73 (CICLO-maersk-parentesis.md): MAERSK quita lo que va entre paréntesis también de lo escrito, como de la
# sugerencia, al elegir el origen y el destino (_mk_las_exactas). Hasta ahí, solo de la sugerencia: el 21-10, en el
# equipo de un colega, una fila con el destino «Ciudad (Estado), País» quedó NO ENVIADA. Lo escrito sin nada fuera de
# los paréntesis no calza con ninguna ---
PAREN_MK = SUG + "test_maersk_quita_los_parentesis_de_los_dos_lados"

MUTACIONES += [
    # Lo escrito con sus paréntesis, como hasta el encargo 73; o sin mirar si queda algo fuera de ellos. Desde el
    # encargo 74, lo escrito sale de _mk_partes.
    dict(id="mk-escrita-con-parentesis", pruebas=[PAREN_MK],
         viejo="    escrita = _mk_partes(ciudad)\n", nuevo="    escrita = (_mk_plano(ciudad), ())\n"),
    dict(id="mk-escrita-vacia-calza", pruebas=[PAREN_MK],
         viejo="    if not escrita[0]:\n        return cy, textos, []\n", nuevo=""),
]

# --- Encargo 74 (CICLO-maersk-mismo-parentesis.md): si la celda y la sugerencia de MAERSK traen paréntesis, lo que va
# entre ellos tiene que ser lo mismo, en _mk_plano; si solo uno lo trae, cuenta lo de afuera (en el 74, _mk_calza, par
# por par; desde el 75, _mk_ganadoras, por lista). Las dos partes salen de _mk_partes, que reemplazó a _mk_base. El
# motivo de la NO ENVIADA lo dice ---
MISMO_MK = SUG + "test_maersk_si_los_dos_traen_parentesis_tiene_que_ser_el_mismo"
# Desde el encargo 75, la tabla es la de las listas enteras (hasta ahí, test_el_parentesis_cuenta_si_lo_traen_los_dos).
CUENTA_MK = "test_ayudantes.TestMAERSK.test_la_regla_del_parentesis_por_lista"

MUTACIONES += [
    # Las tres de la regla par por par (mk-calza-sin-mirar-el-parentesis, mk-calza-exige-el-de-la-celda y
    # mk-calza-exige-el-de-la-sugerencia) salieron en el encargo 75 con _mk_calza: sus equivalentes en _mk_ganadoras
    # están en el bloque del 75.
    # Lo de adentro: sin _mk_plano, o sin guardarlo.
    dict(id="mk-partes-sin-normalizar-el-parentesis", pruebas=[MISMO_MK, CUENTA_MK],
         viejo="            quitados.append(_mk_plano(m.group(1)))\n",
         nuevo="            quitados.append(m.group(1))\n"),
    dict(id="mk-partes-sin-guardar-el-parentesis", pruebas=[MISMO_MK, CUENTA_MK],
         viejo="        grupos += quitados\n", nuevo=""),
    # El motivo, como hasta el encargo 74 (desde el 75 dice la regla de la lista).
    dict(id="mk-sin-una-exacta-sin-el-parentesis", pruebas=[SUG_EXACTA],
         viejo=('            f"entre paréntesis; si la celda lo trae, primero la del mismo, y si no hay, la que no lo '
                'trae, solo si "\n            f"ninguna otra con ese nombre trae otro): '),
         nuevo='            f"entre paréntesis): '),
]

# --- Encargo 75 (CICLO-maersk-parentesis-por-lista.md): la opción (a) del 74. Con la celda con paréntesis decide la
# lista entera (_mk_ganadoras, que reemplazó a _mk_calza): primero, las del mismo paréntesis; si no hay, las que no lo
# traen, solo si ninguna otra con lo mismo afuera trae otro; si no, ninguna. Con la celda sin paréntesis, como en el
# 43 ---
LISTA_MK = SUG + "test_maersk_con_parentesis_decide_la_lista_entera"
SIN_PAREN_MK = "        return [i for i, (a, p) in enumerate(partes) if a == afuera]\n"
OTRO_MK = "    otro = any(a == afuera and p for a, p in partes)\n"
GANA_SIN_MK = "    return [] if otro else sin\n"
# La que recorre todas las listas chicas (revisión de código del encargo 75): la tumban las que rompen lo que la
# regla promete, no las que solo cambian si se elige.
TODAS_MK = "test_ayudantes.TestMAERSK.test_la_regla_por_lista_en_todas_las_listas_chicas"

MUTACIONES += [
    # Sin mirar el paréntesis de la celda (como en a538b77), o sin preferir el mismo (como en el 74 con la del mismo y
    # la que no lo trae).
    dict(id="mk-ganadoras-sin-mirar-el-parentesis", pruebas=[LISTA_MK, MISMO_MK, CUENTA_MK, TODAS_MK],
         viejo="    if not parentesis:\n", nuevo="    if True:\n"),
    dict(id="mk-ganadoras-sin-preferir-el-mismo", pruebas=[LISTA_MK, MISMO_MK, CUENTA_MK, TODAS_MK],
         viejo="    if mismas:\n        return mismas\n", nuevo=""),
    # La que no lo trae: sin mirar las otras (el M1 de seguridad del 74), nunca (exige el mismo aunque solo la celda
    # lo traiga), o con cualquier otra con paréntesis, aunque sea otro nombre.
    dict(id="mk-ganadoras-sin-mirar-las-otras", pruebas=[LISTA_MK, CUENTA_MK, TODAS_MK], viejo=GANA_SIN_MK,
         nuevo="    return sin\n"),
    dict(id="mk-ganadoras-sin-la-que-no-lo-trae", pruebas=[PAREN_MK, LISTA_MK, CUENTA_MK], viejo=GANA_SIN_MK,
         nuevo="    return []\n"),
    dict(id="mk-ganadoras-otro-nombre-cuenta", pruebas=[LISTA_MK, CUENTA_MK], viejo=OTRO_MK,
         nuevo="    otro = any(p for a, p in partes)\n"),
    # El mismo paréntesis con otro nombre; y la celda sin paréntesis exigiendo que la sugerencia tampoco lo traiga.
    dict(id="mk-ganadoras-mismo-parentesis-otro-nombre", pruebas=[CUENTA_MK, TODAS_MK],
         viejo="    mismas = [i for i, (a, p) in enumerate(partes) if a == afuera and p == parentesis]\n",
         nuevo="    mismas = [i for i, (a, p) in enumerate(partes) if p == parentesis]\n"),
    dict(id="mk-ganadoras-celda-sin-parentesis-exige-que-no-lo-traiga",
         pruebas=[SUG_EXACTA, MISMO_MK, CUENTA_MK, TODAS_MK],
         viejo=SIN_PAREN_MK,
         nuevo="        return [i for i, (a, p) in enumerate(partes) if a == afuera and not p]\n"),
    # La que no lo trae, con otro nombre (revisión de código del encargo 75: sin esta, ninguna prueba caía).
    dict(id="mk-ganadoras-la-que-no-lo-trae-con-otro-nombre", pruebas=[LISTA_MK, CUENTA_MK, TODAS_MK],
         viejo="    sin = [i for i, (a, p) in enumerate(partes) if a == afuera and not p]\n",
         nuevo="    sin = [i for i, (a, p) in enumerate(partes) if not p]\n"),
    # Lo de afuera que solo empieza igual, en la del mismo paréntesis o en la que no lo trae (revisión de seguridad
    # del encargo 75: sin «Alfa Beta» en la red, ninguna prueba caía; es lo que arregló el encargo 43).
    dict(id="mk-ganadoras-la-del-mismo-por-prefijo", pruebas=[LISTA_MK, TODAS_MK],
         viejo="    mismas = [i for i, (a, p) in enumerate(partes) if a == afuera and p == parentesis]\n",
         nuevo="    mismas = [i for i, (a, p) in enumerate(partes) if a.startswith(afuera) and p == parentesis]\n"),
    dict(id="mk-ganadoras-la-que-no-lo-trae-por-prefijo", pruebas=[LISTA_MK, TODAS_MK],
         viejo="    sin = [i for i, (a, p) in enumerate(partes) if a == afuera and not p]\n",
         nuevo="    sin = [i for i, (a, p) in enumerate(partes) if a.startswith(afuera) and not p]\n"),
]

# --- Encargo 76 (CICLO-hyundai-paso-uno.md): el paso 01 de HYUNDAI, «Booking Reference». El formulario se espera hasta
# HMM_ESPERA_PASO1 s (hasta ahí, 6), y si después del NEXT la página sigue ahí con su formulario a la vista, se vuelve a
# pulsar ese NEXT, una sola vez, con la evidencia antes (_hmm_reintentar_paso2). El 22-10, en el equipo de un colega, el
# NEXT se pulsó antes de que cargara el formulario, y la fila quedó REVISAR ---
P1 = "test_clics.TestHyundai.test_el_paso1_"
P1_ESPERA, P1_VUELVE, P1_TERCERO = P1 + "espera_su_formulario", P1 + "vuelve_a_pulsar_su_next_una_vez", \
    P1 + "nunca_pulsa_un_tercer_next"
P1_SIN_FORM, P1_UN_NEXT, P1_AVANZA = P1 + "sin_su_formulario_no_vuelve_a_pulsar", P1 + "sin_un_solo_next_no_pulsa", \
    P1 + "que_avanza_no_vuelve_a_pulsar"
P1_LINEA = "    ok_paso2 = _hmm_esperar_paso2(page) or _hmm_reintentar_paso2(page, reg, f)\n"
P1_EVIDENCIA = ('    _evidencia_antes_de_la_guarda(page, reg, f"hmm_f{fila}_paso1", "en Booking Reference, antes de '
                'volver a pulsar "\n                                  "su NEXT", completa=False)\n')

MUTACIONES += [
    # La espera de antes; o el formulario buscado por otro campo, que no está.
    dict(id="e76-paso1-espera-de-antes", pruebas=[P1_ESPERA, P1_SIN_FORM],
         viejo="HMM_ESPERA_PASO1 = 30\n", nuevo="HMM_ESPERA_PASO1 = 6\n"),
    dict(id="e76-paso1-otra-señal", pruebas=[P1_ESPERA],
         viejo='HMM_PASO1 = "#previousBkgNo, #referenceNo0"\n', nuevo='HMM_PASO1 = "#referenceNo1"\n'),
    # Sin el segundo clic, como hasta el encargo 76; con un tercero; o dándolo por bueno sin mirar si llegó.
    dict(id="e76-paso1-sin-segundo-clic", pruebas=[P1_VUELVE],
         viejo=P1_LINEA, nuevo="    ok_paso2 = _hmm_esperar_paso2(page)\n"),
    dict(id="e76-paso1-un-tercer-clic", pruebas=[P1_TERCERO],
         viejo=P1_LINEA,
         nuevo="    ok_paso2 = (_hmm_esperar_paso2(page) or _hmm_reintentar_paso2(page, reg, f)\n"
               "                or _hmm_reintentar_paso2(page, reg, f))\n"),
    dict(id="e76-paso1-segundo-clic-sin-mirar-si-llego", pruebas=[P1_TERCERO],
         viejo='    reg.info("NEXT ok (role) -> Select Vessel, el clic del reintento")\n'
               '    return _hmm_esperar_paso2(page)\n',
         nuevo='    reg.info("NEXT ok (role) -> Select Vessel, el clic del reintento")\n    return True\n'),
    # El segundo clic sin el formulario a la vista; con 0 o con más de un NEXT; o sin buscarlo por su nombre.
    dict(id="e76-paso1-segundo-clic-sin-formulario", pruebas=[P1_SIN_FORM],
         viejo="        if not _hmm_cuantos_se_ven(page.locator(HMM_PASO1)):\n            return False\n",
         nuevo="        pass\n"),
    dict(id="e76-paso1-cualquier-cantidad-de-next", pruebas=[P1_UN_NEXT],
         viejo="    if len(vistos) != 1:\n        return _hmm_sin_reintento(",
         nuevo="    if not vistos:\n        return _hmm_sin_reintento("),
    dict(id="e76-paso1-next-sin-su-nombre", pruebas=[P1_VUELVE],
         viejo='        botones = page.get_by_role("button", name=HMM_NEXT_PASO1, exact=False)\n',
         nuevo='        botones = page.get_by_role("button")\n'),
    # Sin la evidencia antes del segundo clic.
    dict(id="e76-paso1-sin-evidencia", pruebas=[P1_VUELVE, "test_evidencia.TestCadaReservadorLaDeja.test_solo_ahi"],
         viejo=P1_EVIDENCIA, nuevo=""),
    # Sin mirar el paso 02: no llega nunca.
    dict(id="e76-paso2-sin-mirar", pruebas=[P1_ESPERA, P1_AVANZA],
         viejo="        if _hmm_se_ve_el_paso2(page):\n            return True\n", nuevo="        pass\n"),
    # De la revisión de código del encargo 76: sin mirar si el paso 02 llegó mientras guardaba la evidencia; y el
    # segundo clic en la posición, sin tomar el elemento que vio a la vista.
    dict(id="e76-paso1-sin-mirar-el-paso2-tras-la-evidencia", pruebas=[P1 + "no_vuelve_a_pulsar_si_el_paso2_llego"],
         viejo='    if _hmm_se_ve_el_paso2(page):\n        reg.info("el paso 02 llegó mientras guardaba la evidencia: '
               'no vuelvo a pulsar NEXT")\n        return True\n',
         nuevo=""),
    dict(id="e76-paso1-clic-por-su-posicion", pruebas=[P1_VUELVE],
         viejo=("        vistos = [e for e in (botones.nth(i).element_handle(timeout=4500) for i in "
                "range(botones.count()))\n"),
         nuevo="        vistos = [e for e in (botones.nth(i) for i in range(botones.count()))\n"),
    # De la revisión de seguridad del encargo 76: un clic del reintento que da error, sin esperar el paso 02; y sin
    # mirar si el paso 02 llegó cuando el reintento no pulsa.
    dict(id="e76-paso1-error-del-clic-sin-esperar", pruebas=[P1 + "si_el_clic_del_reintento_da_error_espera_el_paso2"],
         viejo='"miro si llega el paso 02, sin otro clic")\n        return _hmm_esperar_paso2(page)\n',
         nuevo='"miro si llega el paso 02, sin otro clic")\n        return False\n'),
    dict(id="e76-paso1-sin-reintento-sin-mirar-el-paso2",
         pruebas=[P1 + "no_vuelve_a_pulsar_si_llega_mientras_busca_el_next"],
         viejo="    if _hmm_se_ve_el_paso2(page):\n        reg.info(f\"no volví a pulsar «{HMM_NEXT_PASO1}» "
               "({motivo}), y el paso 02 ya llegó\")\n        return True\n",
         nuevo=""),
]

# --- Encargo 77 (CICLO-guarda-y-estado-tras-el-envio.md), ítem (b): la guarda de datos reconoce los números de MAERSK
# que empiezan con 28, y los de CMA-CGM y COSCO con la forma de su página tras el envío del 22-10. Y la prueba de
# _extraer_bkg_limpio fija que un «28» suelto no lo toma la regla de los «27…» y que el detalle «(Booking: …)» sí ---
GD_CMA = "    for m in RESERVA_CMA.finditer(t):\n"
GD_COSCO = "    for m in RESERVA_COSCO.finditer(t):\n"
GD_NUMERO = '        numero("número de reserva", m, m.group(1))\n'
GD_FORMA_CMA = r'RESERVA_CMA = re.compile(_ANTES + r"[A-Za-z]{3}[ -]?(\d{7})(?![A-Za-z0-9])")'
GD_FORMA_COSCO = r'RESERVA_COSCO = re.compile(_ANTES + r"[A-Za-z]{2}[ -]?(\d{10})(?![A-Za-z0-9])")'
GD_ANTES = r'_ANTES = r"(?:(?<![A-Za-z0-9])|(?<=\\[nrtf]))"'
GD_ETIQUETA = r'RESERVA_CON_ETIQUETA = re.compile(r"(?i:booking(?:\s{1,20}(?:number|no\.?|n[°º])(?:\s{0,20}:)?|\s{0,3}:))"'

MUTACIONES += [
    # Como hasta el encargo 77: solo los «27».
    dict(id="e77-maersk-solo-27", archivo=GUARDA, pruebas=[GD_MUESTRAS], viejo="2[78](", nuevo="27("),
    # El «28» con su etiqueta, contado dos veces (por RESERVA_MAERSK y por la etiqueta).
    dict(id="e77-etiqueta-cuenta-dos-veces", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo="        if not RESERVA_MAERSK.fullmatch(m.group(1)):", nuevo="        if True:"),
    # Sin CMA-CGM o sin COSCO; o sin dejar pasar sus inventados a la vista.
    dict(id="e77-sin-cma", archivo=GUARDA, pruebas=[GD_MUESTRAS], viejo=GD_CMA + GD_NUMERO, nuevo=""),
    dict(id="e77-sin-cosco", archivo=GUARDA, pruebas=[GD_MUESTRAS], viejo=GD_COSCO + GD_NUMERO, nuevo=""),
    dict(id="e77-cma-sin-inventados", archivo=GUARDA, pruebas=[GD_MUESTRAS], viejo=GD_CMA + GD_NUMERO,
         nuevo=GD_CMA + '        hallazgo("número de reserva", m)\n'),
    dict(id="e77-cosco-sin-inventados", archivo=GUARDA, pruebas=[GD_MUESTRAS], viejo=GD_COSCO + GD_NUMERO,
         nuevo=GD_COSCO + '        hallazgo("número de reserva", m)\n'),
    # _extraer_bkg_limpio con la regla de los «27» abierta a los «28» (lo que el comentario dice que no hace).
    dict(id="e77-limpio-toma-el-28-suelto", pruebas=[LI + "test_patrones_por_naviera"],
         viejo='    m = _re.search(r"\\b(27\\d{7})\\b", det)\n', nuevo='    m = _re.search(r"\\b(2[78]\\d{7})\\b", det)\n'),
    # Los bordes de CMA-CGM y de COSCO (revisión de código del encargo 77): sin ellos, o con otro largo, la forma calza
    # con un texto que no es la medida.
    dict(id="e77-cma-sin-borde-despues", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo=GD_FORMA_CMA, nuevo=GD_FORMA_CMA.replace(r"(\d{7})(?![A-Za-z0-9])", r"(\d{7})")),
    dict(id="e77-cma-borde-despues-solo-cifras", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo=GD_FORMA_CMA, nuevo=GD_FORMA_CMA.replace(r"(\d{7})(?![A-Za-z0-9])", r"(\d{7})(?!\d)")),
    dict(id="e77-borde-antes-solo-letras", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo=GD_ANTES, nuevo=GD_ANTES.replace(r"(?<![A-Za-z0-9])", r"(?<![A-Za-z])")),
    dict(id="e77-cma-de-6-a-8-cifras", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo=GD_FORMA_CMA, nuevo=GD_FORMA_CMA.replace(r"(\d{7})", r"(\d{6,8})")),
    dict(id="e77-cosco-sin-borde-antes", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo=GD_FORMA_COSCO, nuevo=GD_FORMA_COSCO.replace("_ANTES + ", "")),
    dict(id="e77-cosco-sin-borde-despues", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo=GD_FORMA_COSCO, nuevo=GD_FORMA_COSCO.replace(r"(?![A-Za-z0-9])", "")),
    dict(id="e77-cosco-de-9-a-11-cifras", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo=GD_FORMA_COSCO, nuevo=GD_FORMA_COSCO.replace(r"(\d{10})", r"(\d{9,11})")),
    # Lo de la revisión de seguridad del encargo 77: la forma ancha (otro prefijo de COSCO, minúsculas en CMA, un
    # espacio o un guion antes de las cifras), el número detrás del escape de un literal y la etiqueta «Booking:».
    dict(id="e77-cosco-solo-cd", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo=GD_FORMA_COSCO, nuevo=GD_FORMA_COSCO.replace("[A-Za-z]{2}[ -]?", "CD[ -]?")),
    dict(id="e77-cma-solo-mayusculas", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo=GD_FORMA_CMA, nuevo=GD_FORMA_CMA.replace("[A-Za-z]{3}", "[A-Z]{3}")),
    dict(id="e77-cma-sin-separador", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo=GD_FORMA_CMA, nuevo=GD_FORMA_CMA.replace("[A-Za-z]{3}[ -]?", "[A-Za-z]{3}")),
    dict(id="e77-cosco-sin-separador", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo=GD_FORMA_COSCO, nuevo=GD_FORMA_COSCO.replace("[A-Za-z]{2}[ -]?", "[A-Za-z]{2}")),
    dict(id="e77-sin-el-escape-delante", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo=GD_ANTES, nuevo=r'_ANTES = r"(?<![A-Za-z0-9])"'),
    dict(id="e77-sclg-sin-el-escape-delante", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo='RESERVA = re.compile(_ANTES + r"(?:SCLG',
         nuevo='RESERVA = re.compile(r"(?<![A-Za-z0-9])(?:SCLG'),
    dict(id="e77-sin-la-etiqueta-booking", archivo=GUARDA, pruebas=[GD_MUESTRAS],
         viejo=GD_ETIQUETA, nuevo=GD_ETIQUETA.replace(r"|\s{0,3}:))", "))")),
]

# --- Encargo 77 (CICLO-guarda-y-estado-tras-el-envio.md), ítem (a): COSCO queda EMITIDA – CONFIRMAR POR CORREO con la
# frase de su página tras el envío, sin errores y sin una falla del programa; el panel, log.txt y la planilla dicen el
# mismo estado; y la ventana «Reminder» es un paso normal (log.txt dice cuándo aparece y cuándo deja de verse) ---
FORMA_ENVIADA_CO = r'''    "cosco": (r"(?a)(?<![\w-])(?i:Booking)[ \t\xa0]+(CD[0-9]{10})[ \t\xa0]+"
              r"(?i:has[ \t\xa0]+been[ \t\xa0]+submitted[ \t\xa0]+successfully)\b"),
'''
LEE_CON_FALLA = "        except Exception as e:\n            # Con el clic ya dado o a medio dar"
LEE_REF = "        if not bkg and pulsado is True and error is None:\n"
RAMA_REF = "    if ref:\n        vistas = getattr(reg, \"referencias_enviadas\", {})"
NRES_CORREO = '    if str((r or {}).get("estado") or "") == EMITIDA_POR_CORREO:\n        return CONFIRMAR_POR_CORREO\n'
LEE_CORREO_JS = '  if (est === "EMITIDA – CONFIRMAR POR CORREO") return "emitida-correo";\n'
A_LA_VISTA = ("            if not vio_reminder:\n"
              "                reg.info(f\"Ventana 'Reminder' a la vista a los {esperado:.0f} s de esperar el resultado: es un paso \"\n"
              "                         f\"normal de COSCO, que recuerda enviar los documentos antes de su plazo. No pulso nada y sigo \"\n"
              "                         f\"esperando.\")\n")
CIERRE = "            reg.info(f\"La ventana 'Reminder' dejó de verse a los {esperado:.0f} s de esperar el resultado.\")\n"
LEE_AL_PLAZO = ("        campos, error_portal = _cosco_errores(frame, page)\n"
                "        if campos:\n"
                "            error_portal = \"; \".join(campos + ([error_portal] if error_portal else []))\n"
                "            campos = []\n"
                "    return campos, error_portal, vio_reminder\n")
COSCO_EN = EN + "test_cosco_enviada_con_su_frase_es_emitida_por_correo"
COSCO_FORMA = [EN + "test_cosco_solo_con_la_forma_medida", TE + "test_frase_de_cosco_que_dice_que_se_envio"]
LP_E77 = "test_envio.TestLecturaDelPanel."           # LP, más arriba, ya nombra otra clase
CORREO_LP = LP_E77 + "test_emitida_por_correo_se_pinta_como_emitida"

MUTACIONES += [
    # La forma de la frase: la referencia con cualquier cantidad de cifras, sin distinguir mayúsculas, o la frase sin su
    # «has been submitted successfully».
    dict(id="e77-cosco-referencia-de-cualquier-largo", pruebas=COSCO_FORMA,
         viejo=FORMA_ENVIADA_CO, nuevo=FORMA_ENVIADA_CO.replace(r"(CD[0-9]{10})", r"(CD[0-9]+)")),
    dict(id="e77-cosco-referencia-sin-caja", pruebas=COSCO_FORMA,
         viejo=FORMA_ENVIADA_CO, nuevo=FORMA_ENVIADA_CO.replace(r"(CD[0-9]{10})", r"((?i:CD)[0-9]{10})")),
    dict(id="e77-cosco-frase-a-medias", pruebas=COSCO_FORMA,
         viejo=FORMA_ENVIADA_CO,
         nuevo=FORMA_ENVIADA_CO.replace(r"(?i:has[ \t\xa0]+been[ \t\xa0]+submitted[ \t\xa0]+successfully)\b", "")),
    # De la revisión de seguridad: «Booking» detrás de otra palabra, un salto de línea entre las palabras, y el
    # plegado de Unicode (sin ASCII, la «ſ» cuenta como «s»).
    dict(id="e77-cosco-rebooking", pruebas=[EN + "test_cosco_solo_con_la_forma_medida"],
         viejo=FORMA_ENVIADA_CO, nuevo=FORMA_ENVIADA_CO.replace(r"(?<![\w-])", "")),
    dict(id="e77-cosco-salto-de-linea", pruebas=[EN + "test_cosco_solo_con_la_forma_medida"],
         viejo=FORMA_ENVIADA_CO, nuevo=FORMA_ENVIADA_CO.replace(r"(?i:Booking)[ \t\xa0]+(CD", r"(?i:Booking)\s+(CD")),
    dict(id="e77-cosco-salto-de-linea-despues", pruebas=[TE + "test_frase_de_cosco_que_dice_que_se_envio"],
         viejo=FORMA_ENVIADA_CO, nuevo=FORMA_ENVIADA_CO.replace(r'(CD[0-9]{10})[ \t\xa0]+"', r'(CD[0-9]{10})\s+"')),
    dict(id="e77-cosco-sin-ascii", pruebas=[EN + "test_cosco_solo_con_la_forma_medida"],
         viejo=FORMA_ENVIADA_CO, nuevo=FORMA_ENVIADA_CO.replace('(r"(?a)', '(r"')),
    # De la revisión de seguridad: una lectura que falla después de pulsar, otra vez fuera del reservador.
    dict(id="e77-lectura-que-falla-se-escapa", pruebas=[EN + "test_la_lectura_que_falla_tras_pulsar_es_enviada"],
         viejo=LEE_CON_FALLA, nuevo=LEE_CON_FALLA.replace("except Exception as e:", "except ZeroDivisionError as e:")),
    # Con duda, igual la lee: con el clic que pudo no salir, o con una falla del programa después de pulsar.
    dict(id="e77-cosco-lee-sin-pulsar", pruebas=[EN + "test_cosco_con_cualquier_duda_sigue_enviada"],
         viejo=LEE_REF, nuevo="        if not bkg and error is None:\n"),
    dict(id="e77-cosco-lee-tras-la-falla", pruebas=[EN + "test_cosco_con_cualquier_duda_sigue_enviada"],
         viejo=LEE_REF, nuevo="        if not bkg and pulsado is True:\n"),
    # La frase en cualquier naviera.
    dict(id="e77-la-frase-en-cualquier-naviera",
         pruebas=[EN + "test_la_frase_de_cosco_no_vale_en_otra_naviera", TE + "test_frase_de_cosco_que_dice_que_se_envio"],
         viejo="    return _leer_tras_envio(page, FORMA_ENVIADA.get(naviera), espera, plazo_ms, todas=",
         nuevo='    return _leer_tras_envio(page, FORMA_ENVIADA["cosco"], espera, plazo_ms, todas='),
    # Sin el estado nuevo, o con el de antes, o callado en log.txt.
    dict(id="e77-cosco-sin-estado-nuevo", pruebas=[COSCO_EN], viejo=RAMA_REF,
         nuevo=RAMA_REF.replace("    if ref:", "    if False:")),
    dict(id="e77-cosco-como-emitida", pruebas=[COSCO_EN, CORREO_LP],
         viejo='EMITIDA_POR_CORREO = "EMITIDA – CONFIRMAR POR CORREO"\n', nuevo='EMITIDA_POR_CORREO = "EMITIDA"\n'),
    dict(id="e77-cosco-estado-callado", pruebas=[COSCO_EN],
         viejo='        reg.paso(f"✅ {EMITIDA_POR_CORREO} · {detalle}")\n', nuevo=""),
    dict(id="e77-cosco-sin-su-frase-como-sin-forma", pruebas=[EN + "test_cosco_sin_su_frase_sigue_enviada"],
         viejo="    elif naviera in FORMA_ENVIADA:\n        que =", nuevo="    elif False:\n        que ="),
    # La columna del número, el panel y la planilla.
    dict(id="e77-numero-sin-confirmar-por-correo",
         pruebas=[CORREO_LP, ESC + "test_web_descarga_de_emitida_por_correo", PL_NRES],
         viejo=NRES_CORREO, nuevo=""),
    dict(id="e77-panel-no-lee-el-estado-nuevo", pruebas=[LP_E77 + "test_lectura_de_cada_estado", CORREO_LP],
         viejo=LEE_CORREO_JS, nuevo=""),
    dict(id="e77-panel-no-la-cuenta", pruebas=[CORREO_LP], viejo="          totalEmitidas++;\n", nuevo=""),
    dict(id="e77-panel-columna-sin-su-texto", pruebas=[CORREO_LP],
         viejo='${esc(nres)}</span>`;', nuevo='—</span>`;'),
    dict(id="e77-panel-otro-texto", pruebas=[CORREO_LP],
         viejo='          chip(f, "ok", "emitida – confirmar por correo");\n', nuevo='          chip(f, "ok", "emitida");\n'),
    # La ventana «Reminder»: callada al aparecer o al cerrarse, el cierre dicho cada vez, y el plazo que se cumple sin
    # leer los errores. (Hasta el encargo 78, también el cierre que siempre decía que pulsó: ya no pulsa nada.)
    dict(id="e77-reminder-callado-al-aparecer",
         pruebas=[CO_ + "test_reminder_no_se_pulsa", CO_ + "test_reminder_que_vuelve_dice_una_vez_que_se_cerro"],
         viejo=A_LA_VISTA, nuevo=""),
    dict(id="e77-reminder-callado-al-cerrarse",
         pruebas=[CO_ + "test_reminder_no_se_pulsa", CO_ + "test_reminder_que_vuelve_dice_una_vez_que_se_cerro"],
         viejo=CIERRE, nuevo=""),
    dict(id="e77-reminder-cierre-cada-vez", pruebas=[CO_ + "test_reminder_que_vuelve_dice_una_vez_que_se_cerro"],
         viejo="        if rem_abierta and not rem_cerrada:\n", nuevo="        if rem_abierta:\n"),
    dict(id="e77-plazo-sin-leer-errores", pruebas=[CO_ + "test_al_agotarse_lee_los_errores"],
         viejo=LEE_AL_PLAZO, nuevo="    return campos, error_portal, vio_reminder\n"),
    # Lo de la revisión de código del encargo 77: al cumplirse el plazo, los errores solo con la ventana (no con la
    # carga); y la frase con «Booking» pegado a la referencia o con una letra pegada al final.
    dict(id="e77-plazo-errores-solo-con-la-ventana", pruebas=[CO_ + "test_al_agotarse_con_la_carga_lee_los_errores"],
         viejo=LEE_AL_PLAZO,
         nuevo=LEE_AL_PLAZO.replace("        campos, error_portal = _cosco_errores(frame, page)\n",
                                    "        if vio_reminder:\n            campos, error_portal = _cosco_errores(frame, page)\n")),
    # De la revisión de seguridad: al plazo, los errores como errores de campo (NO ENVIADA invitaría a repetirla).
    dict(id="e77-plazo-errores-como-campos",
         pruebas=[CO_ + "test_al_agotarse_lee_los_errores", CO_ + "test_al_agotarse_con_la_carga_lee_los_errores"],
         viejo=LEE_AL_PLAZO, nuevo=LEE_AL_PLAZO.replace("        if campos:\n", "        if False:\n")),
    dict(id="e77-cosco-booking-pegado", pruebas=[EN + "test_cosco_solo_con_la_forma_medida"],
         viejo=FORMA_ENVIADA_CO,
         nuevo=FORMA_ENVIADA_CO.replace(r"(?i:Booking)[ \t\xa0]+(CD", r"(?i:Booking)[ \t\xa0]*(CD")),
    dict(id="e77-cosco-sin-borde-final", pruebas=[EN + "test_cosco_solo_con_la_forma_medida"],
         viejo=FORMA_ENVIADA_CO, nuevo=FORMA_ENVIADA_CO.replace(r"successfully)\b", "successfully)")),
]


# --- Encargo 78 (CICLO-decisiones-tras-el-envio.md), decisiones de Marcelo: (1) la referencia de la frase es el número
# de la reserva, y va a la columna «N° de reserva emitida»; (2) CMA-CGM con «Booking enviado» queda EMITIDA – CONFIRMAR
# POR CORREO, con su número; (3) del Submit del «Reminder» de COSCO no se pulsa nada; (4) errores de campo y, a la vez,
# la frase o el número en la pantalla: ENVIADA – REVISAR EN PORTAL. Cada una, en las dos direcciones ---
FORMA_ENVIADA_CMA = r'''    "cma": (r"(?a)(?ms)\A(?>.*?^[ \t\xa0]*(?:Booking[ \t\xa0]+)?Booking[ \t\xa0]+enviado[ \t\xa0]*$)"
            r".*?^[ \t\xa0]*Booking[ \t\xa0]+([A-Z]{3}[0-9]{7})[ \t\xa0]*$"),
'''
# La de antes de la revisión de código del encargo 78: las dos señales sin atar (en cualquier orden, y «Booking enviado»
# en cualquier lugar de su línea).
CMA_SIN_ATAR = r'''    "cma": (r"(?a)(?ms)\A(?=.*?(?<![\w-])Booking[ \t\xa0]+enviado\b).*?"
            r"^[ \t\xa0]*Booking[ \t\xa0]+([A-Z]{3}[0-9]{7})[ \t\xa0]*$"),
'''
NUMERO_CORREO = ('    if estado == EMITIDA_POR_CORREO:\n'
                 '        m = _re.search(r"\\(Booking: ([A-Z0-9]{6,18})\\)", str((r or {}).get("detalle") or ""))\n'
                 '        return m.group(1) if m else ""\n')
CONTRADICE = ("    elif rechazo and pulsado is not False:\n")
LEE_CONTRADICE = ("            contradice = (numero_tras_envio(page, naviera, espera=0, plazo_ms=plazo_ms)\n"
                  "                          or referencia_tras_envio(page, naviera, espera=0, plazo_ms=plazo_ms))\n")
FALLA_CONTRADICE = ("        except Exception as e:\n"
                    "            reg.info(f\"no pude leer la pantalla para ver si dice que la reserva se envió: {_texto_error(e)}\")\n")
RAMA_CONTRADICE = ("        if contradice:\n"
                   "            # NO ENVIADA invitaría a repetir una reserva que pudo crearse.\n")
# Desde el encargo 79, detrás de la contradicción va la duda del Submit de COSCO (campos_en_duda), con el mismo aviso.
AVISO_CONTRADICE = ("            reg.paso(f\"⚠ {ENVIADA_REVISAR} · {detalle}\")\n"
                    "            return (ENVIADA_REVISAR, detalle)\n"
                    "        if campos_en_duda:")
LEE_CON_PLAZO = ("                texto = ((_evaluar_con_plazo(alcance, _JS_TEXTO_VISIBLE, plazo_ms) if plazo_ms\n"
                 "                          else alcance.evaluate(_JS_TEXTO_VISIBLE)) or \"\")\n")
CMA_EN = EN + "test_cma_con_booking_enviado_es_emitida_por_correo"
CMA_TE = TE + "test_frase_de_cma_que_dice_que_se_envio"
CMA_PLAZO = "test_datadome.TestLecturasConPlazo.test_la_frase_de_envio_con_plazo"
CMA_MARCOS = "test_datadome.TestLecturasConPlazo.test_la_frase_en_un_marco_y_un_marco_colgado"
AMBIGUAS = EN + "test_dos_numeros_distintos_no_deciden"
MISMO_NUMERO = EN + "test_el_mismo_numero_dos_veces_en_la_corrida"
CAMPOS_FRASE = EN + "test_errores_de_campo_con_la_frase_son_enviada"
PANEL_NUMERO = ('            tdBkg.innerHTML = bkg ? `<span class="badge-bkg">${esc(nres)}</span>`\n'
                '              : `<span class="badge-bkg-vacio" style="color:var(--text-secondary)">${esc(nres)}</span>`;\n')

MUTACIONES += [
    # (1) La referencia no llega a la columna; o llega cualquier «Booking …» del detalle (como el del encargo 77); o la
    # toma también otro estado; y el panel sin la insignia del número.
    dict(id="e78-numero-correo-no-va-a-la-columna",
         pruebas=[COSCO_EN, CMA_EN, CORREO_LP, ESC + "test_web_descarga_de_emitida_por_correo", PL_NRES],
         viejo=NUMERO_CORREO, nuevo=NUMERO_CORREO.replace('        return m.group(1) if m else ""\n', '        return ""\n')),
    dict(id="e78-numero-correo-sin-sus-parentesis",
         pruebas=[CORREO_LP, ESC + "test_web_descarga_de_emitida_por_correo", PL_NRES],
         viejo=NUMERO_CORREO,
         nuevo=NUMERO_CORREO.replace(r'r"\(Booking: ([A-Z0-9]{6,18})\)"', r'r"Booking:? ([A-Z0-9]{6,18})"')),
    dict(id="e78-numero-de-otro-estado", pruebas=[CORREO_LP],
         viejo=NUMERO_CORREO,
         nuevo=NUMERO_CORREO.replace("    if estado == EMITIDA_POR_CORREO:\n",
                                     "    if estado in (EMITIDA_POR_CORREO, ENVIADA_REVISAR):\n")),
    dict(id="e78-panel-numero-sin-insignia", pruebas=[CORREO_LP],
         viejo=PANEL_NUMERO, nuevo=PANEL_NUMERO.replace("tdBkg.innerHTML = bkg ? ", "tdBkg.innerHTML = false ? ")),
    # (2) CMA sin su frase; con una sola de las dos señales; con la referencia acompañada en su línea o detrás de otra
    # palabra; «Booking enviado» partido en dos líneas o pegado a otra palabra; la referencia en minúsculas.
    dict(id="e78-cma-sin-frase", pruebas=[CMA_EN, CMA_TE, CMA_PLAZO, FOTO_PLAZO],
         viejo=FORMA_ENVIADA_CMA, nuevo=""),
    dict(id="e78-cma-sin-booking-enviado", pruebas=[CMA_EN, CMA_TE],
         viejo=FORMA_ENVIADA_CMA,
         nuevo=FORMA_ENVIADA_CMA.replace(r"\A(?>.*?^[ \t\xa0]*(?:Booking[ \t\xa0]+)?Booking[ \t\xa0]+enviado[ \t\xa0]*$)", r"\A")),
    dict(id="e78-cma-sin-la-linea-de-la-referencia", pruebas=[CMA_EN, CMA_TE],
         viejo=FORMA_ENVIADA_CMA,
         nuevo=FORMA_ENVIADA_CMA.replace(r"^[ \t\xa0]*Booking", r"(?<![\w-])Booking")
                                .replace(r"[0-9]{7})[ \t\xa0]*$", r"[0-9]{7})\b")),
    dict(id="e78-cma-enviado-en-otra-linea", pruebas=[CMA_TE],
         viejo=FORMA_ENVIADA_CMA, nuevo=FORMA_ENVIADA_CMA.replace(r"Booking[ \t\xa0]+enviado", r"Booking\s+enviado")),
    dict(id="e78-cma-booking-enviado-pegado", pruebas=[CMA_TE],
         viejo=FORMA_ENVIADA_CMA, nuevo=FORMA_ENVIADA_CMA.replace(r"(?>.*?^[ \t\xa0]*(?:Booking[ \t\xa0]+)?Booking", r"(?>.*?Booking")),
    dict(id="e78-cma-referencia-sin-caja", pruebas=[CMA_TE],
         viejo=FORMA_ENVIADA_CMA, nuevo=FORMA_ENVIADA_CMA.replace(r"([A-Z]{3}[0-9]{7})", r"([A-Za-z]{3}[0-9]{7})")),
    # CMA lee su frase sin plazo: la lectura, o _resultado_envio, que no le pasa el suyo.
    dict(id="e78-lectura-sin-plazo", pruebas=[CMA_PLAZO],
         viejo=LEE_CON_PLAZO, nuevo='                texto = alcance.evaluate(_JS_TEXTO_VISIBLE) or ""\n'),
    dict(id="e78-referencia-sin-el-plazo-del-envio", pruebas=[CMA_PLAZO],
         viejo="                ref = referencia_tras_envio(page, naviera, plazo_ms=plazo_ms)\n",
         nuevo="                ref = referencia_tras_envio(page, naviera)\n"),
    # (3) Los dos que vuelven a pulsar el Submit del Reminder están con la espera de COSCO, más arriba
    # (cosco-reminder-vuelve-a-pulsar y cosco-reminder-busca-su-submit); y su aviso, sin decir que no pulsa.
    dict(id="e78-reminder-no-dice-que-no-pulsa",
         pruebas=[CO_ + "test_reminder_no_se_pulsa", CO_ + "test_reminder_tardio_tampoco_se_pulsa"],
         viejo=A_LA_VISTA, nuevo=A_LA_VISTA.replace(" No pulso nada y sigo \"\n", "\"\n")
                                           .replace('                         f\"esperando.\")\n', '                         f\"\")\n')),
    # (4) Con errores de campo: sin mirar la frase; mirándola con espera; solo el número; también sin pulsar; como
    # antes, NO ENVIADA; callado; con la lectura que falla otra vez fuera, o callada; y sin plazo en CMA.
    dict(id="e78-campos-sin-mirar-la-frase", pruebas=[CAMPOS_FRASE, CMA_PLAZO],
         viejo=CONTRADICE, nuevo="    elif False:\n"),
    dict(id="e78-campos-numero-con-espera", pruebas=[EN + "test_validacion_es_no_enviada_con_los_campos"],
         viejo=LEE_CONTRADICE, nuevo=LEE_CONTRADICE.replace("numero_tras_envio(page, naviera, espera=0, ",
                                                            "numero_tras_envio(page, naviera, ")),
    dict(id="e78-campos-frase-con-espera", pruebas=[CAMPOS_FRASE],
         viejo=LEE_CONTRADICE, nuevo=LEE_CONTRADICE.replace("referencia_tras_envio(page, naviera, espera=0, ",
                                                            "referencia_tras_envio(page, naviera, ")),
    dict(id="e78-campos-solo-el-numero", pruebas=[CAMPOS_FRASE, CMA_PLAZO],
         viejo=LEE_CONTRADICE,
         nuevo="            contradice = numero_tras_envio(page, naviera, espera=0, plazo_ms=plazo_ms)\n"),
    dict(id="e78-campos-lee-sin-pulsar", pruebas=[CAMPOS_FRASE],
         viejo=CONTRADICE, nuevo="    elif rechazo:\n"),
    dict(id="e78-campos-con-la-frase-no-enviada", pruebas=[CAMPOS_FRASE, CMA_PLAZO],
         viejo=RAMA_CONTRADICE, nuevo=RAMA_CONTRADICE.replace("        if contradice:\n", "        if False:\n")),
    dict(id="e78-campos-con-la-frase-callado", pruebas=[CAMPOS_FRASE],
         viejo=AVISO_CONTRADICE, nuevo=AVISO_CONTRADICE.replace('            reg.paso(f"⚠ {ENVIADA_REVISAR} · {detalle}")\n', "")),
    dict(id="e78-campos-lectura-que-falla-se-escapa", pruebas=[CAMPOS_FRASE],
         viejo=FALLA_CONTRADICE, nuevo=FALLA_CONTRADICE.replace("except Exception as e:", "except ZeroDivisionError as e:")),
    dict(id="e78-campos-lectura-que-falla-callada", pruebas=[CAMPOS_FRASE],
         viejo=FALLA_CONTRADICE,
         nuevo="        except Exception as e:\n            pass\n"),
    dict(id="e78-campos-sin-plazo", pruebas=[CMA_PLAZO],
         viejo=LEE_CONTRADICE, nuevo=LEE_CONTRADICE.replace(", espera=0, plazo_ms=plazo_ms))", ", espera=0))")),
    # De la revisión de código del encargo 78. CMA-CGM: «Booking enviado» dentro de una frase, o las dos señales en
    # cualquier orden (la regla de antes de la revisión).
    dict(id="e78-cma-enviado-a-mitad-de-linea", pruebas=[CMA_TE],
         viejo=FORMA_ENVIADA_CMA, nuevo=FORMA_ENVIADA_CMA.replace(r"enviado[ \t\xa0]*$)", r"enviado)")),
    dict(id="e78-cma-en-cualquier-orden", pruebas=[CMA_EN, CMA_TE], viejo=FORMA_ENVIADA_CMA, nuevo=CMA_SIN_ATAR),
    # La lectura con plazo: solo la página (los marcos, sin plazo); un alcance que no contestó, leído en cada vuelta; y
    # el marco principal leído aparte de la página.
    dict(id="e78-marcos-sin-plazo", pruebas=[CMA_MARCOS],
         viejo=LEE_CON_PLAZO, nuevo=LEE_CON_PLAZO.replace("if plazo_ms\n", "if plazo_ms and alcance is page\n")),
    dict(id="e78-alcance-mudo-se-vuelve-a-leer", pruebas=[CMA_MARCOS],
         viejo="            if any(alcance is m for m in mudos):\n                continue\n", nuevo=""),
    dict(id="e78-marco-principal-dos-veces", pruebas=[CMA_MARCOS],
         viejo="        otros = [f for f in (getattr(page, \"frames\", None) or []) if f is not page and f is not principal]\n",
         nuevo="        otros = [f for f in (getattr(page, \"frames\", None) or []) if f is not page]\n"),
    # La contradicción con el clic a medio dar; y la planilla sin el verde de la reserva con su número.
    dict(id="e78-campos-sin-el-clic-a-medio-dar", pruebas=[CAMPOS_FRASE],
         viejo=CONTRADICE, nuevo="    elif rechazo and pulsado:\n"),
    dict(id="e78-planilla-correo-sin-verde", pruebas=[ESC + "test_web_descarga_de_emitida_por_correo"],
         viejo='                if bkg:\n                    c_n.fill = verde_fill\n',
         nuevo='                if bkg and st == "EMITIDA":\n                    c_n.fill = verde_fill\n'),
    # De la revisión de seguridad del encargo 78. CMA-CGM: el título en cualquier lugar de su línea (como antes de la
    # revisión, con el borde de la izquierda), o sin el «Booking» de delante que trae la página medida.
    dict(id="e78-cma-titulo-a-mitad-de-linea", pruebas=[CMA_TE],
         viejo=FORMA_ENVIADA_CMA,
         nuevo=FORMA_ENVIADA_CMA.replace(r"(?>.*?^[ \t\xa0]*(?:Booking[ \t\xa0]+)?Booking", r"(?>.*?(?<![\w-])Booking")),
    dict(id="e78-cma-sin-el-booking-de-delante", pruebas=[CMA_TE],
         viejo=FORMA_ENVIADA_CMA, nuevo=FORMA_ENVIADA_CMA.replace(r"(?:Booking[ \t\xa0]+)?", "")),
    # Dos referencias distintas: gana la primera; la lectura no las busca; la duda, tomada por una falla del programa; o,
    # con errores de campo, NO ENVIADA.
    dict(id="e78-ambigua-gana-la-primera", pruebas=[AMBIGUAS, CMA_TE],
         viejo="            if len(distintas) > 1:\n", nuevo="            if False:\n"),
    dict(id="e78-ambigua-sin-buscarlas", pruebas=[AMBIGUAS, CMA_TE],
         viejo=", todas=REFERENCIAS_ENVIADA.get(naviera))", nuevo=")"),
    dict(id="e78-ambigua-como-falla", pruebas=[AMBIGUAS],
         viejo="        except ReferenciaAmbigua as e:\n            ambiguas = e.referencias\n", nuevo=""),
    dict(id="e78-ambigua-con-campos-no-enviada", pruebas=[AMBIGUAS],
         viejo="        except ReferenciaAmbigua as e:\n            contradice = \", \".join(e.referencias)\n", nuevo=""),
    dict(id="e78-ambigua-callada", pruebas=[AMBIGUAS],
         viejo=("pero mostró {len(ambiguas)} \"\n                   f\"números distintos ({', '.join(ambiguas)}): no se "
                "sabe cuál es el de esta reserva. {_REVISA_PORTAL}\")\n        reg.paso(f\"⚠ {ENVIADA_REVISAR} · {detalle}\")\n"),
         nuevo=("pero mostró {len(ambiguas)} \"\n                   f\"números distintos ({', '.join(ambiguas)}): no se "
                "sabe cuál es el de esta reserva. {_REVISA_PORTAL}\")\n")),
    # La misma referencia en la corrida: sin mirar, sin recordarla, o sin decirlo en log.txt.
    dict(id="e78-mismo-numero-sin-mirar", pruebas=[MISMO_NUMERO],
         viejo="        if anterior:\n", nuevo="        if False:\n"),
    dict(id="e78-mismo-numero-sin-recordar", pruebas=[MISMO_NUMERO],
         viejo="        vistas[ref] = evidencia\n", nuevo=""),
    dict(id="e78-mismo-numero-callado", pruebas=[MISMO_NUMERO],
         viejo=("puede ser la pantalla de esa reserva. {_REVISA_PORTAL}\")\n"
                "            reg.paso(f\"⚠ {ENVIADA_REVISAR} · {detalle}\")\n"),
         nuevo="puede ser la pantalla de esa reserva. {_REVISA_PORTAL}\")\n"),
]

# --- Encargo 79 (CICLO-cosco-errores-y-submit.md), decisión de Marcelo: con errores de campo tras el Submit de COSCO,
# NO ENVIADA solo si el Submit sigue a la vista; si ya no está, o la lectura falla, ENVIADA – REVISAR EN PORTAL, con un
# motivo que dice que el envío pudo haber entrado. Los tres casos, en las dos direcciones; y de la revisión de código, la
# ventana Reminder a la vista y la respuesta que no es True ni False, también como duda ---
SUBMIT_DUDA = EN + "test_errores_de_campo_y_el_submit"
RS_E79 = "test_envio.TestReservadores."                     # RS, más arriba, ya nombra otra clase
JS_SUBMIT_E79 = CO_ + "test_js_submit_presente_solo_el_submit_a_la_vista"
EN_DUDA_COSCO = '    en_duda = _cosco_submit_en_duda(frame, page, reg) if campos else ""\n'
SIGUE_A_LA_VISTA = '    if sigue is True:\n        return ""\n'
RARA = ('    reg.info(f"la lectura del Submit de COSCO no dijo si sigue a la vista: dio un {type(sigue).__name__}")\n'
        '    return "no se pudo leer si «Submit» sigue a la vista"\n')
REMINDER_E79 = ('    if _cosco_en_alguno(frame, page, _JS_COSCO_HAY_REMINDER):\n'
                '        return "la ventana «Reminder» está a la vista"\n')
AVISO_DUDA = ("            reg.paso(f\"⚠ {ENVIADA_REVISAR} · {detalle}\")\n"
              "            return (ENVIADA_REVISAR, detalle)\n"
              "        return _no_enviada(")

MUTACIONES += [
    # reservar_cosco: sin mirar el Submit, mirándolo también sin errores de campo (una lectura de más: el estado no
    # cambia, porque la duda se lee solo con errores; la ve la foto de reservar_cosco), o sin pasar la duda.
    dict(id="e79-cosco-no-mira-el-submit", pruebas=[RS_E79 + "test_cosco_decide_con_lo_que_vio"],
         viejo=EN_DUDA_COSCO, nuevo='    en_duda = ""\n'),
    dict(id="e79-cosco-mira-sin-errores", pruebas=[RS_E79 + "test_cosco_decide_con_lo_que_vio"],
         viejo=EN_DUDA_COSCO, nuevo="    en_duda = _cosco_submit_en_duda(frame, page, reg)\n"),
    dict(id="e79-cosco-sin-pasar-la-duda", pruebas=[RS_E79 + "test_cosco_decide_con_lo_que_vio"],
         viejo=DECIDE_CO, nuevo=DECIDE_CO.replace(", campos_en_duda=en_duda", "")),
    # El ayudante: el Submit a la vista como duda; ya no está, la lectura que falla o la respuesta rara, como NO
    # ENVIADA; cualquier respuesta verdadera como «sigue»; la rara como «ya no está»; las fallas, calladas o sin atrapar.
    dict(id="e79-a-la-vista-es-duda", pruebas=[SUBMIT_DUDA],
         viejo=SIGUE_A_LA_VISTA, nuevo=SIGUE_A_LA_VISTA.replace(" is True:", " is None:")),
    dict(id="e79-ya-no-esta-es-no-enviada", pruebas=[SUBMIT_DUDA],
         viejo='        return "«Submit» ya no está a la vista"\n', nuevo='        return ""\n'),
    dict(id="e79-lectura-que-falla-es-no-enviada", pruebas=[SUBMIT_DUDA],
         viejo='        return "no se pudo leer si «Submit» sigue a la vista"\n', nuevo='        return ""\n'),
    dict(id="e79-respuesta-rara-es-no-enviada", pruebas=[SUBMIT_DUDA],
         viejo=RARA, nuevo=RARA.replace('    return "no se pudo leer si «Submit» sigue a la vista"\n',
                                        '    return ""\n')),
    dict(id="e79-cualquier-respuesta-es-que-sigue", pruebas=[SUBMIT_DUDA],
         viejo=SIGUE_A_LA_VISTA, nuevo=SIGUE_A_LA_VISTA.replace(" is True:", ":")),
    dict(id="e79-respuesta-rara-como-ausente", pruebas=[SUBMIT_DUDA],
         viejo="    if sigue is False:\n", nuevo="    if not sigue:\n"),
    dict(id="e79-respuesta-rara-callada", pruebas=[SUBMIT_DUDA],
         viejo=RARA, nuevo=RARA.replace(RARA.splitlines(True)[0], "")),
    dict(id="e79-lectura-que-falla-callada", pruebas=[SUBMIT_DUDA],
         viejo='        reg.info(f"no pude leer si el Submit de COSCO sigue a la vista: {_texto_error(e)}")\n', nuevo=""),
    dict(id="e79-lectura-que-falla-se-escapa", pruebas=[SUBMIT_DUDA],
         viejo=('        reg.info(f"no pude leer si el Submit de COSCO sigue a la vista: {_texto_error(e)}")\n'),
         nuevo=('        raise\n')),
    # La ventana Reminder: sin mirarla, o solo en el marco.
    dict(id="e79-reminder-no-se-mira", pruebas=[SUBMIT_DUDA],
         viejo=REMINDER_E79, nuevo=""),
    dict(id="e79-reminder-solo-en-el-marco", pruebas=[SUBMIT_DUDA],
         viejo=REMINDER_E79, nuevo=REMINDER_E79.replace("(frame, page, _JS", "(frame, None, _JS")),
    # El JavaScript: un Submit oculto, u otro texto que trae «submit».
    dict(id="e79-js-submit-oculto-cuenta", pruebas=[JS_SUBMIT_E79],
         viejo="find(e => e.offsetParent !== null && /^submit$/i", nuevo="find(e => /^submit$/i"),
    dict(id="e79-js-submit-parcial", pruebas=[JS_SUBMIT_E79],
         viejo="e.offsetParent !== null && /^submit$/i.test", nuevo="e.offsetParent !== null && /submit/i.test"),
    # _resultado_envio: la duda como NO ENVIADA, callada en log.txt, sin errores de campo (el FRENA SI: el camino de
    # EMITIDA – CONFIRMAR POR CORREO), o antes que la contradicción del encargo 78.
    dict(id="e79-duda-es-no-enviada", pruebas=[SUBMIT_DUDA],
         viejo="        if campos_en_duda:\n", nuevo="        if False:\n"),
    dict(id="e79-duda-callada", pruebas=[SUBMIT_DUDA],
         viejo=AVISO_DUDA, nuevo=AVISO_DUDA.replace("            reg.paso(f\"⚠ {ENVIADA_REVISAR} · {detalle}\")\n", "")),
    dict(id="e79-duda-sin-errores-de-campo", pruebas=[SUBMIT_DUDA],
         viejo="    if rechazo:\n        lista", nuevo="    if rechazo or campos_en_duda:\n        lista"),
    dict(id="e79-duda-antes-que-la-contradiccion", pruebas=[SUBMIT_DUDA],
         viejo=RAMA_CONTRADICE,
         nuevo="        if campos_en_duda:\n            return (ENVIADA_REVISAR, campos_en_duda)\n" + RAMA_CONTRADICE),
]

# --- Encargo 80 (CICLO-cosco-espera-tras-errores.md), decisión de Marcelo (la opción (b) del encargo 79): con errores de
# campo tras el Submit de COSCO, antes de dar NO ENVIADA la espera sigue mirando hasta 20 s desde el clic si aparece la
# ventana «Reminder» o la página que dice que la reserva se envió, y con cualquiera de las dos sigue su camino
# enseguida. Los tres casos de punta a punta (TestCoscoTrasLosErrores), la espera sola (TestCosco) y el FRENA SI: sin
# errores de campo, nada cambia ---
TE80 = "test_envio.TestCoscoTrasLosErrores."
TOPE_E80 = CO_ + "test_errores_de_validacion_esperan_hasta_el_tope"
RECHAZO_E80 = TE80 + "test_rechazo_que_dura_los_20_s"
REMINDER_E80 = TE80 + "test_reminder_que_llega_dentro_del_tramo"
ENVIO_E80 = TE80 + "test_pagina_de_envio_dentro_del_tramo"
FRASE_E80 = TE80 + "test_pagina_de_envio_es_la_frase"
TRAMO_E80 = ("        if campos and not vio_reminder and time.monotonic() - inicio < COSCO_ESPERA_TRAS_ERRORES_SEG:\n")
LLAMA_E80 = "            vio, esperado = _cosco_tras_los_errores(page, frame, reg, inicio, esperado)\n"
MARCA_E80 = "                rem_abierta = vio_reminder = True\n"
RELEE_E80 = ("            campos, error_portal = _cosco_errores(frame, page)     # lo que se ve con la página de envío, "
             "o al tope\n")
VE_REMINDER_E80 = ("        if _cosco_en_alguno(frame, page, _JS_COSCO_HAY_REMINDER):\n"
                   "            # Sin «error» en el texto: el registro del panel pintaría como alerta un paso normal "
                   "(clase, en JS_INDEX).\n")
DICE_REMINDER_E80 = ("            reg.info(f\"Ventana 'Reminder' a la vista a los {esperado:.0f} s de esperar el resultado, "
                     "con campos \"\n"
                     "                     f\"marcados antes: es un paso normal de COSCO, que sale después del envío. No "
                     "pulso nada y sigo \"\n"
                     "                     f\"esperando.\")\n")
VE_ENVIO_E80 = "        if _cosco_pagina_de_envio(page):\n"
DICE_ENVIO_E80 = ("            reg.info(f\"La página dijo que la reserva se envió a los {esperado:.0f} s de esperar el "
                  "resultado, después \"\n"
                  "                     f\"de los errores de campo.\")\n")
DICE_TOPE_E80 = ("    reg.info(f\"A los {COSCO_ESPERA_TRAS_ERRORES_SEG} s del Submit no apareció la ventana 'Reminder' ni "
                 "la página que \"\n"
                 "             f\"dice que la reserva se envió.\")\n")
DICE_TRAMO_E80 = ("    reg.info(f\"COSCO marcó errores de campo a los {esperado:.0f} s de esperar el resultado. Antes de "
                  "darlos por un \"\n"
                  "             f\"rechazo, espero hasta los {COSCO_ESPERA_TRAS_ERRORES_SEG} s desde el Submit, sin "
                  "pulsar nada, por si \"\n"
                  "             f\"aparece la ventana 'Reminder' o la página que dice que la reserva se envió.\")\n")
ATRAPA_E80 = ("    except ReferenciaAmbigua:\n        return True\n    except Exception:\n        return False\n")

MUTACIONES += [
    # La espera: sin el tramo; con él también con la ventana ya vista, con solo un aviso del portal o sin errores de campo
    # (el FRENA SI); el tope contado desde los errores, y no desde el clic; otro tope; un paso que se pasa del tope.
    dict(id="e80-sin-tramo", pruebas=[TOPE_E80, RECHAZO_E80],
         viejo=TRAMO_E80, nuevo="        if False:\n"),
    dict(id="e80-tramo-con-el-reminder-visto", pruebas=[REMINDER_E80],
         viejo=TRAMO_E80, nuevo=TRAMO_E80.replace("not vio_reminder and ", "")),
    dict(id="e80-tramo-con-aviso-del-portal", pruebas=[CO_ + "test_espera_corta_con_aviso_del_portal"],
         viejo=TRAMO_E80, nuevo=TRAMO_E80.replace("if campos and", "if (campos or error_portal) and")),
    dict(id="e80-tramo-sin-errores-de-campo", pruebas=[TE80 + "test_sin_errores_de_campo_no_hay_tramo"],
         viejo=TRAMO_E80, nuevo=TRAMO_E80.replace("if campos and ", "if ")),
    dict(id="e80-tope-desde-los-errores", pruebas=[TOPE_E80, RECHAZO_E80],
         viejo=LLAMA_E80, nuevo=LLAMA_E80.replace("reg, inicio, esperado", "reg, time.monotonic(), esperado")),
    dict(id="e80-otro-tope", pruebas=[TOPE_E80, RECHAZO_E80],
         viejo="COSCO_ESPERA_TRAS_ERRORES_SEG = 20\n", nuevo="COSCO_ESPERA_TRAS_ERRORES_SEG = 30\n"),
    dict(id="e80-se-pasa-del-tope", pruebas=[TOPE_E80, RECHAZO_E80],
         viejo="        paso = min(_COSCO_PASO_SEG, falta)\n", nuevo="        paso = _COSCO_PASO_SEG\n"),
    # La ventana en el tramo: sin mirarla, sin recordarla (una que se ve en una sola vuelta), o callada en log.txt.
    dict(id="e80-tramo-sin-reminder", pruebas=[REMINDER_E80],
         viejo=VE_REMINDER_E80, nuevo=VE_REMINDER_E80.replace(
             "        if _cosco_en_alguno(frame, page, _JS_COSCO_HAY_REMINDER):\n", "        if False:\n")),
    dict(id="e80-reminder-del-tramo-sin-marcar", pruebas=[REMINDER_E80],
         viejo=MARCA_E80, nuevo=""),
    dict(id="e80-reminder-del-tramo-callado", pruebas=[REMINDER_E80],
         viejo=DICE_REMINDER_E80, nuevo=""),
    # La página de envío en el tramo: sin mirarla, con _JS_COSCO_EXITO (que da la etiqueta del formulario), callada; y
    # sin volver a leer los errores después.
    dict(id="e80-envio-no-se-mira", pruebas=[ENVIO_E80],
         viejo=VE_ENVIO_E80, nuevo="        if False:\n"),
    dict(id="e80-envio-con-exito", pruebas=[TOPE_E80, RECHAZO_E80],
         viejo=VE_ENVIO_E80, nuevo="        if _cosco_en_alguno(frame, page, _JS_COSCO_EXITO):\n"),
    dict(id="e80-envio-callado", pruebas=[ENVIO_E80],
         viejo=DICE_ENVIO_E80, nuevo=""),
    dict(id="e80-sin-releer-los-errores", pruebas=[ENVIO_E80],
         viejo=RELEE_E80, nuevo=""),
    # Lo que dice log.txt al empezar el tramo y al tope.
    dict(id="e80-tramo-callado", pruebas=[TOPE_E80, RECHAZO_E80],
         viejo=DICE_TRAMO_E80, nuevo=""),
    dict(id="e80-tope-callado", pruebas=[TOPE_E80, RECHAZO_E80],
         viejo=DICE_TOPE_E80, nuevo=""),
    # La página de envío es la frase, en una sola lectura sin espera; con dos referencias también; si la lectura falla,
    # no.
    dict(id="e80-pagina-de-envio-con-espera", pruebas=[FRASE_E80],
         viejo='        return bool(referencia_tras_envio(page, "cosco", espera=0))\n',
         nuevo='        return bool(referencia_tras_envio(page, "cosco"))\n'),
    dict(id="e80-ambigua-no-es-envio", pruebas=[FRASE_E80],
         viejo=ATRAPA_E80, nuevo=ATRAPA_E80.replace("        return True\n", "        return False\n", 1)),
    dict(id="e80-lectura-que-falla-es-envio", pruebas=[FRASE_E80],
         viejo=ATRAPA_E80, nuevo=ATRAPA_E80[:ATRAPA_E80.rindex("        return False\n")] + "        return True\n"),
]

# De la revisión de código del encargo 80: las mutaciones del revisor que el censo no tenía.
MUTACIONES += [
    dict(id="e80-tramo-sin-mirar-el-reloj", pruebas=[RECHAZO_E80],
         viejo=TRAMO_E80, nuevo="        if campos and not vio_reminder:\n"),
    dict(id="e80-envio-cuenta-como-reminder", pruebas=[ENVIO_E80],
         viejo="            if vio == \"reminder\":\n", nuevo="            if vio:\n"),
    dict(id="e80-tope-estricto", pruebas=[TOPE_E80, RECHAZO_E80],
         viejo="        if falta <= 0:\n", nuevo="        if falta < 0:\n"),
    dict(id="e80-reminder-sin-seguir-su-camino", pruebas=[REMINDER_E80],
         viejo="                continue                  # su camino: mientras siga a la vista, solo se espera\n",
         nuevo="                pass\n"),
    dict(id="e80-tramo-sin-sumar-lo-esperado", pruebas=[REMINDER_E80, ENVIO_E80],
         viejo="        esperado += paso\n", nuevo=""),
    dict(id="e80-reminder-del-tramo-solo-en-la-pagina", pruebas=[REMINDER_E80],
         viejo=VE_REMINDER_E80, nuevo=VE_REMINDER_E80.replace("(frame, page,", "(None, page,")),
    dict(id="e80-reminder-del-tramo-solo-en-el-marco", pruebas=[REMINDER_E80],
         viejo=VE_REMINDER_E80, nuevo=VE_REMINDER_E80.replace("(frame, page,", "(frame, None,")),
]

# --- Encargo 81 (CICLO-cosco-carga-y-confirmacion.md), ítem 1, decisión de Marcelo: con errores de campo, si al decidir
# (a los 20 s) la máscara de carga sigue a la vista, en el marco o en la página, COSCO sigue procesando: ENVIADA –
# REVISAR EN PORTAL, nunca NO ENVIADA (_cosco_submit_en_duda). Sin mirarla, solo en un alcance, o sin decirlo ---
MASCARA_E81 = TE80 + "test_mascara_de_carga_al_tope"
CARGA_E81 = ('    if _cosco_en_alguno(frame, page, _JS_COSCO_EN_CARGA):\n'
             '        return "la máscara de carga sigue a la vista"\n')

MUTACIONES += [
    dict(id="e81-carga-no-se-mira", pruebas=[MASCARA_E81, SUBMIT_DUDA],
         viejo=CARGA_E81, nuevo=""),
    dict(id="e81-carga-solo-en-el-marco", pruebas=[MASCARA_E81],
         viejo=CARGA_E81, nuevo=CARGA_E81.replace("(frame, page,", "(frame, None,")),
    dict(id="e81-carga-solo-en-la-pagina", pruebas=[MASCARA_E81, SUBMIT_DUDA],
         viejo=CARGA_E81, nuevo=CARGA_E81.replace("(frame, page,", "(None, page,")),
    dict(id="e81-carga-sin-motivo", pruebas=[MASCARA_E81, SUBMIT_DUDA],
         viejo=CARGA_E81, nuevo=CARGA_E81.replace('return "la máscara de carga sigue a la vista"', 'return ""')),
]

# --- Encargo 81, ítem 2, decisión de Marcelo: sin errores de campo, EMITIDA – CONFIRMAR POR CORREO exige la frase de la
# página de envío, nunca la etiqueta del formulario (que da _JS_COSCO_EXITO); y el envío del 22-10 sigue dando EMITIDA –
# CONFIRMAR POR CORREO (FRENA SI). Una lectura que acepta la señal de la espera como la frase, y una espera que no espera
# con la máscara (el div «partial-shipment» del formulario) ---
ETIQUETA_E81 = TE80 + "test_la_etiqueta_sola_no_da_emitida"
DIA_22_E81 = TE80 + "test_el_22_10_sigue_emitido_con_su_evidencia"
REF_E81 = "                ref = referencia_tras_envio(page, naviera, plazo_ms=plazo_ms)\n"

MUTACIONES += [
    dict(id="e81-senal-de-la-espera-como-frase", pruebas=[ETIQUETA_E81],
         viejo=REF_E81,
         nuevo=REF_E81.replace(
             "plazo_ms=plazo_ms)\n",
             "plazo_ms=plazo_ms) or next((\"(sin número)\" for f in [page] + list(getattr(page, \"frames\", None) "
             "or []) if naviera == \"cosco\" and f.evaluate(_JS_COSCO_EXITO)), \"\")\n")),
    dict(id="e81-sin-esperar-la-carga", pruebas=[DIA_22_E81, ETIQUETA_E81],
         viejo="            vio_carga = True\n            continue\n", nuevo="            vio_carga = True\n"),
]

# --- Encargo 82 (CICLO-msc-lista-abierta-y-hs.md): antes de «Search Schedule», la lista de sugerencias de un puerto de
# MSC que quedó abierta se cierra con el método de su combobox, sin pulsar ni elegir nada, y se comprueba que se cerró y
# que su campo sigue igual; si no, corta (_msc_cerrar_listas_abiertas). Sin mirarla, sin cerrarla, sin comprobar, o
# pulsando ---
LISTA_E82 = M1 + "test_la_lista_de_un_puerto_abierta_se_cierra_antes_de_buscar"
CERRADAS_E82 = M1 + "test_con_las_listas_cerradas_el_camino_no_cambia"
CORTA_E82 = M1 + "test_si_la_lista_no_se_cierra_bien_corta_sin_buscar"
JS_LISTAS_E82 = M1 + "test_js_listas_de_puertos_y_su_cierre"
POR_QUE_E82 = ('        por_que = ("no pude volver a leerla" if despues is None else "sigue abierta" if despues[i][0]\n'
               '                   else "el campo ya no dice lo mismo" if despues[i][1] != antes[i][1] else "")\n')

MUTACIONES += [
    dict(id="e82-lista-no-se-mira", pruebas=[LISTA_E82],
         viejo="    _msc_cerrar_listas_abiertas(page, reg, listas)\n    if not click_si_existe(", nuevo="    if not click_si_existe("),
    dict(id="e82-lista-no-se-cierra", pruebas=[LISTA_E82, CORTA_E82],
         viejo="            r = page.evaluate(_JS_MSC_CERRAR_LISTA, i)\n", nuevo='            r = "no la cerré"\n'),
    dict(id="e82-lista-sin-comprobar", pruebas=[CORTA_E82],
         viejo=POR_QUE_E82, nuevo='        por_que = ""\n'),
    dict(id="e82-lista-sin-mirar-el-campo", pruebas=[CORTA_E82],
         viejo=POR_QUE_E82, nuevo=POR_QUE_E82.replace(' if despues[i][1] != antes[i][1] else ""', ' if False else ""')),
    dict(id="e82-lista-sin-releer-sigue", pruebas=[CORTA_E82],
         viejo=POR_QUE_E82, nuevo=POR_QUE_E82.replace('"no pude volver a leerla" if despues is None else ', '"" if despues is None else ')),
    # De la revisión de código: el cierre que falla sin atrapar (la fila daría ERROR), la comprobación solo de la
    # primera lista abierta, y sin el plazo de la animación del cierre.
    dict(id="e82-lista-cierre-sin-try", pruebas=[CORTA_E82],
         viejo=('        try:\n            r = page.evaluate(_JS_MSC_CERRAR_LISTA, i)\n        except Exception as e:\n'
                '            r = f"error: {str(e)[:60]}"\n'),
         nuevo="        r = page.evaluate(_JS_MSC_CERRAR_LISTA, i)\n"),
    dict(id="e82-lista-comprueba-solo-la-primera", pruebas=[CORTA_E82],
         viejo="    for i, etiqueta in abiertas:\n        por_que = (",
         nuevo="    for i, etiqueta in abiertas[:1]:\n        por_que = ("),
    dict(id="e82-lista-sin-plazo-del-cierre", pruebas=[LISTA_E82, CORTA_E82],
         viejo="    esperar(page, 0.6)\n    try:\n        despues = _msc_listas_de_puertos(page, listas)\n",
         nuevo="    esperar(page, 0)\n    try:\n        despues = _msc_listas_de_puertos(page, listas)\n"),
    dict(id="e82-lista-espera-siempre", pruebas=[CERRADAS_E82],
         viejo="    if not abiertas:\n        return\n", nuevo="    esperar(page, 0.6)\n    if not abiertas:\n        return\n"),
    dict(id="e82-lista-lectura-fallida-corta", pruebas=[CERRADAS_E82],
         viejo='        reg.info(f"listas de sugerencias de los puertos: no pude leerlas ({str(e)[:60]}); sigo")\n        return\n',
         nuevo='        raise ObjetivoNoEncontrado("Search Schedule de MSC", "las listas de los puertos")\n'),
    dict(id="e82-lista-solo-el-destino", pruebas=[LISTA_E82],
         viejo='MSC_PUERTOS = (("POLId", "Port of Load"), ("PODId", "Port of Discharge"))\n',
         nuevo='MSC_PUERTOS = (("PODId", "Port of Discharge"),)\n'),
    dict(id="e82-js-lista-sin-aria", pruebas=[JS_LISTAS_E82],
         viejo="    return [!!(campo && campo.getAttribute('aria-expanded') === 'true') || seVe, campo ? campo.value : null];\n",
         nuevo="    return [seVe, campo ? campo.value : null];\n"),
    dict(id="e82-js-lista-sin-verla", pruebas=[JS_LISTAS_E82],
         viejo="    const seVe = !!(lista && lista.getClientRects().length);\n", nuevo="    const seVe = false;\n"),
    dict(id="e82-js-cierre-elige", pruebas=[JS_LISTAS_E82],
         viejo="    w.close();\n    return 'cerrada';\n", nuevo="    w.select(0);\n    w.close();\n    return 'cerrada';\n"),
    dict(id="e82-js-cierre-otro-widget", pruebas=[JS_LISTAS_E82],
         viejo=".data('kendoComboBox') : null;\n", nuevo=".data('kendoDropDownList') : null;\n"),
]

# --- Encargo 82 (CICLO-msc-lista-abierta-y-hs.md): sin ninguna sugerencia del HS Code de MSC en MSC_SONDEOS_HS lecturas,
# lo vuelve a escribir una sola vez y lee otras tantas; con otras sugerencias sin el salmón, no. Sin volver a escribirlo,
# volviendo a escribirlo también con otras, leyendo una tercera tanda, con otra cuenta de lecturas, o escribiéndolo sin
# borrar lo que había ---
HS_E82 = M1 + "test_hs_sin_sugerencias_lo_escribe_otra_vez"
HS_FALLA_E82 = M1 + "test_hs_si_falla_al_volver_a_escribirlo_corta"
OTRA_VEZ_E82 = ('                reg.info(f"HS Code: el portal no ofreció ninguna sugerencia en {MSC_SONDEOS_HS * 0.5:.0f} s; lo "\n'
                '                         f"vuelvo a escribir, una sola vez")\n'
                '                reescrito = True\n'
                '                _msc_escribir_hs(page, inp, hscode)\n')

MUTACIONES += [
    dict(id="e82-hs-no-la-vuelve-a-escribir", pruebas=[HS_E82],
         viejo=OTRA_VEZ_E82, nuevo="                break\n"),
    dict(id="e82-hs-otra-vez-tambien-sin-salmon", pruebas=[HS_E82],
         viejo="                if elegido:   # el portal", nuevo="                if False:   # el portal"),
    dict(id="e82-hs-una-tercera-vez", pruebas=[HS_E82],
         viejo="        for seg in range(2 * MSC_SONDEOS_HS):", nuevo="        for seg in range(3 * MSC_SONDEOS_HS):"),
    dict(id="e82-hs-menos-lecturas", pruebas=[HS_E82],
         viejo="MSC_SONDEOS_HS = 14\n", nuevo="MSC_SONDEOS_HS = 10\n"),
    # De la revisión de código: una escritura de verdad por cada tanda (tres), decidir con cualquier lectura y no con la
    # última, y lo que falla desde la segunda escritura: que siga (con el campo borrado), o que corte también antes.
    dict(id="e82-hs-tercera-escritura", pruebas=[HS_E82],
         viejo=("        for seg in range(2 * MSC_SONDEOS_HS):   # hasta 7 s; sin ninguna sugerencia, otra escritura y 7 s más\n"
                "            if seg == MSC_SONDEOS_HS:\n"),
         nuevo=("        for seg in range(3 * MSC_SONDEOS_HS):   # hasta 7 s; sin ninguna sugerencia, otra escritura y 7 s más\n"
                "            if seg and seg % MSC_SONDEOS_HS == 0:\n")),
    dict(id="e82-hs-decide-con-cualquier-lectura", pruebas=[HS_E82],
         viejo="            elegido = str(page.evaluate(_JS_MSC_HS_ELEGIR))\n",
         nuevo="            elegido = str(page.evaluate(_JS_MSC_HS_ELEGIR)) or elegido\n"),
    dict(id="e82-hs-falla-al-volver-a-escribir-sigue", pruebas=[HS_FALLA_E82],
         viejo='        if reescrito and not (elegido and elegido != "sin-salmon"):\n',
         nuevo='        if False:\n'),
    dict(id="e82-hs-falla-antes-tambien-corta", pruebas=[HS_FALLA_E82],
         viejo='        if reescrito and not (elegido and elegido != "sin-salmon"):\n',
         nuevo='        if not (elegido and elegido != "sin-salmon"):\n'),
    dict(id="e82-hs-otra-vez-sin-borrar", pruebas=[HS_E82],
         viejo=OTRA_VEZ_E82, nuevo=OTRA_VEZ_E82.replace("_msc_escribir_hs(page, inp, hscode)", "inp.press_sequentially(str(hscode), delay=120)")),
]

# --- Encargo 83 (CICLO-maersk-buscador-nuevo.md), decisión de Marcelo: la pantalla nueva del buscador del Shipper de
# MAERSK, titulada «Search/Add party», se acepta con la misma regla (un solo resultado con la empresa, la lista quieta,
# y después la tarjeta «Shipper» lo muestra). Sin aceptarla, aceptando otro título (con otra cosa en su span, suelto en
# el encabezado o en otro elemento, oculto o fuera del buscador), sin elegir en ella, sin su casilla, sin el título en
# la lista quieta, sin anotarlo o anotándolo de más, o sin el resultado único ---
SH = "test_clics.TestShipperMaersk."
NUEVA_E83 = SH + "test_la_pantalla_nueva_elige_con_la_misma_regla"
UNICO_E83 = SH + "test_la_pantalla_nueva_sin_un_resultado_unico_corta"
QUIETA_E83 = SH + "test_la_lista_quieta_tambien_con_su_titulo"
JS_E83 = SH + "test_js_shipper"
CASILLA_E83 = SH + "test_js_casilla"
MEDIDOS_E83 = SH + "test_la_empresa_y_el_titulo_son_los_medidos"

MUTACIONES += [
    dict(id="e83-nueva-no-se-acepta", pruebas=[NUEVA_E83, UNICO_E83],
         viejo='    if not (r.get("titulo") or r.get("titulo_nuevo")):\n', nuevo='    if not r.get("titulo"):\n'),
    dict(id="e83-nueva-sin-resultado-unico", pruebas=[UNICO_E83],
         viejo='    if r.get("con_empresa") != 1:\n        cuantos = ',
         nuevo='    if r.get("con_empresa") != 1 and not r.get("titulo_nuevo"):\n        cuantos = '),
    dict(id="e83-nueva-sin-aviso", pruebas=[NUEVA_E83],
         viejo='    if not r.get("titulo"):\n        reg.info(f"Shipper: el buscador se abrió con la pantalla',
         nuevo='    if False:\n        reg.info(f"Shipper: el buscador se abrió con la pantalla'),
    dict(id="e83-aviso-tambien-en-el-de-siempre", pruebas=[NUEVA_E83],
         viejo='    if not r.get("titulo"):\n        reg.info(f"Shipper: el buscador se abrió con la pantalla',
         nuevo='    if True:\n        reg.info(f"Shipper: el buscador se abrió con la pantalla'),
    dict(id="e83-quieta-sin-titulo-nuevo", pruebas=[QUIETA_E83],
         viejo='for k in ("resultados", "con_empresa", "titulo", "titulo_nuevo"))',
         nuevo='for k in ("resultados", "con_empresa", "titulo"))'),
    dict(id="e83-otro-titulo-generico", pruebas=[MEDIDOS_E83, SH + "test_con_la_empresa_no_pulsa_nada"],
         viejo='MK_BUSCADOR_GENERICO = "Search/Add party"\n', nuevo='MK_BUSCADOR_GENERICO = "Search party"\n'),
    dict(id="e83-js-pulsar-sin-la-nueva", pruebas=[JS_E83],
         viejo="                : (s.titulo || s.tituloNuevo ? s.conEmpresa : []);\n",
         nuevo="                : (s.titulo ? s.conEmpresa : []);\n"),
    dict(id="e83-js-titulo-por-parte", pruebas=[JS_E83],
         viejo="            c => mkTag(c) === 'span' && mkTextoHondo(c) === String(a.generico).toUpperCase()));\n",
         nuevo=("            c => mkTag(c) === 'span'\n"
                "                 && mkTextoHondo(c).includes(String(a.generico).toUpperCase())));\n")),
    dict(id="e83-js-titulo-en-cualquier-hijo", pruebas=[JS_E83],
         viejo="            c => mkTag(c) === 'span' && mkTextoHondo(c) === String(a.generico).toUpperCase()));\n",
         nuevo="            c => mkTextoHondo(c) === String(a.generico).toUpperCase()));\n"),
    dict(id="e83-js-titulo-en-todo-el-encabezado", pruebas=[JS_E83],
         viejo=("        const tituloNuevo = encabezados.some(x => [...(x.el.children || [])].some(\n"
                "            c => mkTag(c) === 'span' && mkTextoHondo(c) === String(a.generico).toUpperCase()));\n"),
         nuevo=("        const tituloNuevo = encabezados.some(x => mkTextoHondo(x.el).startsWith(\n"
                "            String(a.generico).toUpperCase()));\n")),
    # De la revisión de código: el título genérico de un encabezado fuera del buscador, o de uno oculto; y el aviso de
    # la pantalla nueva también con los dos títulos a la vista.
    dict(id="e83-js-titulo-fuera-del-buscador", pruebas=[JS_E83],
         viejo="        const tituloNuevo = encabezados.some(x => ",
         nuevo=("        const tituloNuevo = todos.filter(x => mkAtr(x.el, 'slot') === 'heading' && mkVisible(x.el))"
                ".some(x => ")),
    dict(id="e83-js-titulo-oculto", pruebas=[JS_E83],
         viejo="        const tituloNuevo = encabezados.some(x => ",
         nuevo=("        const tituloNuevo = todos.filter(x => mkAtr(x.el, 'slot') === 'heading' && enBuscador(x))"
                ".some(x => ")),
    dict(id="e83-aviso-con-los-dos-titulos", pruebas=[NUEVA_E83],
         viejo='    if not r.get("titulo"):\n        reg.info(f"Shipper: el buscador se abrió con la pantalla',
         nuevo='    if r.get("titulo_nuevo"):\n        reg.info(f"Shipper: el buscador se abrió con la pantalla'),
    dict(id="e83-js-lectura-sin-titulo-nuevo", pruebas=[JS_E83],
         viejo="titulo: s.titulo, titulo_nuevo: s.tituloNuevo, abierto: s.abierto,",
         nuevo="titulo: s.titulo, abierto: s.abierto,"),
    dict(id="e83-js-casilla-sin-la-nueva", pruebas=[CASILLA_E83],
         viejo="            if (!titulo && !tituloNuevo) return {el: null, por: 'titulo'};\n",
         nuevo="            if (!titulo) return {el: null, por: 'titulo'};\n"),
]

# --- Encargo 84 (CICLO-entorno-propio.md): el programa arma su entorno propio (.venv) con preparar_entorno.py y las
# dependencias con hash de requirements.txt, sin terminal; si no puede, abre con el Python del equipo solo si ese ya
# tiene todo. Las mutaciones de preparar_entorno.py cambian solo la copia de la sandbox: sus pruebas corren el módulo
# sobre carpetas nuevas (ninguna instala en el Python del equipo: el -r equivocado hace fallar a pip, no lo desvía).
PE = "preparar_entorno.py"
TD = "test_entorno.TestDecisiones."
TAY = "test_entorno.TestAyudantes."
TEP = "test_entorno.TestEntornoPropio."
TEX = "test_entorno.TestExclusion."
TCR = "test_entorno.TestCaminoReal."
TBE = "test_entorno.TestElBatAbreConElEntornoPropio."
TRQ = "test_entorno.TestRequirements."
PENDIENTE = '        pendiente = bool(sin) or estado.get("requisitos") != huella\n'
RECIENTE = '        return intento["requisitos"] == huella and 0 <= time.time() - float(intento["cuando"]) < PAUSA_REINTENTO\n'
PATH_VENV = '    set "PATH=%~dp0.venv\\Scripts;%PATH:"=%"\n'
BAT_IMPREVISTO = "test_actualizar.TestLosLanzadores.test_si_el_preparador_falla_por_algo_imprevisto_abre_solo_con_un_python_completo"
BAT_IGUALES = "test_actualizar.TestLosLanzadores.test_los_dos_bat_son_el_mismo_salvo_el_modo"
BAT_SIN_GIT = "test_actualizar.TestLosLanzadores.test_sin_git_pregunta_una_sola_vez"
ABRE_CON_VENV = TBE + "test_el_programa_abre_con_el_python_del_venv_con_sus_librerias"

MUTACIONES += [
    # Cuándo instala: siempre, sin mirar los requisitos, o sin mirar lo que falta.
    dict(id="e84-instala-siempre", archivo=PE, pruebas=[TD + "test_al_dia_no_instala_ni_dice_nada",
                                                        TCR + "test_la_segunda_vez_solo_comprueba_y_no_dice_nada"],
         viejo=PENDIENTE, nuevo="        pendiente = True\n"),
    dict(id="e84-ignora-los-requisitos", archivo=PE,
         pruebas=[TD + "test_si_cambiaron_los_requisitos_instala_y_lo_anota", TD + "test_sin_estado_instala",
                  TCR + "test_si_cambian_los_requisitos_vuelve_a_instalar"],
         viejo=PENDIENTE, nuevo="        pendiente = bool(sin)\n"),
    dict(id="e84-ignora-lo-que-falta", archivo=PE,
         pruebas=[TD + "test_si_falta_una_libreria_instala_aunque_los_requisitos_no_cambien"],
         viejo=PENDIENTE, nuevo='        pendiente = estado.get("requisitos") != huella\n'),
    dict(id="e84-un-venv-ajeno-se-llena", archivo=PE,
         pruebas=[TD + "test_un_venv_que_no_armo_el_programa_no_se_llena", TD + "test_un_venv_ajeno_con_todo_se_usa_sin_instalar"],
         viejo="    propio = python is not None and (RAIZ / VENV / MARCA).is_file()\n",
         nuevo="    propio = python is not None\n"),
    # La falla reciente: ni se mira, ni se compara con los requisitos, ni vence.
    dict(id="e84-no-mira-la-falla-reciente", archivo=PE,
         pruebas=[TD + "test_tras_una_falla_reciente_no_vuelve_a_esperar_a_pip_si_todo_se_importa",
                  TCR + "test_sin_red_el_segundo_inicio_no_vuelve_a_esperar_a_pip_si_todo_se_importa"],
         viejo='        if pendiente and reciente(estado.get("intento"), huella):\n',
         nuevo="        if False:\n"),
    dict(id="e84-falla-reciente-sin-mirar-el-equipo", archivo=PE,
         pruebas=[TD + "test_tras_una_falla_reciente_con_el_venv_vacio_y_el_equipo_completo_no_vuelve_a_esperar_a_pip",
                  TCR + "test_sin_red_y_con_el_python_del_equipo_completo_el_segundo_inicio_no_espera_a_pip"],
         viejo='            if not obligatorias_que_faltan(sin) or not obligatorias_que_faltan(faltan(sys.executable, "-E")):\n',
         nuevo="            if not obligatorias_que_faltan(sin):\n"),
    dict(id="e84-falla-reciente-sin-equipo-no-prueba", archivo=PE,
         pruebas=[TD + "test_tras_una_falla_reciente_si_el_equipo_no_tiene_nada_vuelve_a_probar_con_pip"],
         viejo='            if not obligatorias_que_faltan(sin) or not obligatorias_que_faltan(faltan(sys.executable, "-E")):\n',
         nuevo="            if True:\n"),
    dict(id="e84-mensaje-en-singular", archivo=PE, pruebas=[TD + "test_si_faltan_las_dos_el_mensaje_concuerda_en_plural"],
         viejo="{'falta' if len(faltan_ellas) == 1 else 'faltan'}", nuevo="{'falta'}"),
    # correr(): al vencer el plazo cierra el árbol, y si no vence devuelve el código y la salida.
    dict(id="e84-correr-no-cierra-el-arbol", archivo=PE, pruebas=[TAY + "test_correr_cierra_los_hijos_del_proceso_cuando_vence_el_plazo"],
         viejo="        cerrar_arbol(p.pid)\n", nuevo="        p.kill()\n"),
    dict(id="e84-cerrar-arbol-sin-los-hijos", archivo=PE, pruebas=[TAY + "test_correr_cierra_los_hijos_del_proceso_cuando_vence_el_plazo"],
         viejo='[taskkill, "/T", "/F", "/PID", str(pid)]', nuevo='[taskkill, "/F", "/PID", str(pid)]'),
    dict(id="e84-correr-pierde-el-codigo", archivo=PE, pruebas=[TAY + "test_un_proceso_que_termina_a_tiempo_devuelve_su_codigo_y_su_salida"],
         viejo='    return p.returncode, salida.decode("utf-8", "replace")\n', nuevo='    return 0, salida.decode("utf-8", "replace")\n'),
    dict(id="e84-falla-de-otros-requisitos", archivo=PE,
         pruebas=[TD + "test_el_intento_fallido_de_otros_requisitos_no_cuenta", TAY + "test_reciente_pide_los_mismos_requisitos_y_un_plazo"],
         viejo=RECIENTE, nuevo='        return 0 <= time.time() - float(intento["cuando"]) < PAUSA_REINTENTO\n'),
    dict(id="e84-la-falla-no-vence", archivo=PE,
         pruebas=[TD + "test_tras_una_falla_reciente_no_vuelve_a_esperar_a_pip_si_todo_se_importa",
                  TAY + "test_reciente_pide_los_mismos_requisitos_y_un_plazo"],
         viejo=RECIENTE, nuevo='        return intento["requisitos"] == huella and 0 <= time.time() - float(intento["cuando"])\n'),
    dict(id="e84-la-falla-del-futuro", archivo=PE, pruebas=[TAY + "test_reciente_pide_los_mismos_requisitos_y_un_plazo"],
         viejo=RECIENTE, nuevo='        return intento["requisitos"] == huella and time.time() - float(intento["cuando"]) < PAUSA_REINTENTO\n'),
    dict(id="e84-no-anota-la-falla", archivo=PE, pruebas=[TD + "test_una_falla_de_pip_con_todo_importable_anota_el_intento"],
         viejo='                estado["intento"] = {"requisitos": huella, "cuando": time.time()}\n',
         nuevo="                pass\n"),
    dict(id="e84-da-por-hecho-lo-que-no-esta", archivo=PE,
         pruebas=[TD + "test_si_pip_dijo_listo_pero_algo_sigue_faltando_no_da_por_hecho_nada"],
         viejo='            if resultado == "listo" and not sin:\n', nuevo='            if resultado == "listo":\n'),
    dict(id="e84-no-guarda-que-quedo-listo", archivo=PE, pruebas=[TCR + "test_la_segunda_vez_solo_comprueba_y_no_dice_nada"],
         viejo='                estado["requisitos"] = huella\n', nuevo="                pass\n"),
    # Con qué abre: el Python del equipo sin mirarlo, o dicho como entorno propio; y un hash distinto no abre nunca.
    dict(id="e84-equipo-sin-mirar", archivo=PE,
         pruebas=[TD + "test_sin_red_y_sin_nada_en_el_equipo_no_abre_y_dice_que_falta",
                  TD + "test_sin_entorno_propio_y_sin_nada_en_el_equipo_no_abre"],
         viejo="    if not obligatorias_que_faltan(sin_equipo):\n", nuevo="    if True:\n"),
    dict(id="e84-equipo-siempre-completo", archivo=PE,
         pruebas=[TD + "test_sin_red_y_sin_nada_en_el_equipo_no_abre_y_dice_que_falta",
                  TD + "test_sin_entorno_propio_y_sin_nada_en_el_equipo_no_abre"],
         viejo='    sin_equipo = faltan(sys.executable, "-E")\n', nuevo="    sin_equipo = []\n"),
    dict(id="e84-equipo-dice-propio", archivo=PE,
         pruebas=[TD + "test_sin_red_y_con_todo_en_el_equipo_abre_con_el_del_equipo",
                  TD + "test_sin_entorno_propio_abre_con_el_del_equipo_si_lo_tiene_todo",
                  TCR + "test_sin_red_y_con_el_python_del_equipo_completo_abre_con_ese"],
         viejo='        anotar("abro con el Python del equipo")\n        return SALIDA_EQUIPO\n',
         nuevo='        anotar("abro con el Python del equipo")\n        return SALIDA_PROPIO\n'),
    dict(id="e84-hash-no-frena", archivo=PE,
         pruebas=[TD + "test_un_hash_que_no_coincide_no_abre_ni_con_el_python_del_equipo",
                  TCR + "test_un_hash_que_no_coincide_no_abre_aunque_el_equipo_tenga_todo"],
         viejo='            if resultado == "hash":\n', nuevo="            if False:\n"),
    dict(id="e84-holidays-obligatoria", archivo=PE,
         pruebas=[TD + "test_si_solo_falta_holidays_abre_con_el_entorno_propio", TD + "test_las_obligatorias_son_las_que_el_programa_necesita_para_abrir"],
         viejo='OBLIGATORIAS = ("playwright.sync_api", "openpyxl")\n',
         nuevo='OBLIGATORIAS = ("playwright.sync_api", "openpyxl", "holidays")\n'),
    dict(id="e84-obligatorias-con-las-opcionales", archivo=PE,
         pruebas=[TD + "test_las_obligatorias_son_las_que_el_programa_necesita_para_abrir", TD + "test_si_solo_falta_holidays_abre_con_el_entorno_propio"],
         viejo='    return [n.split(".")[0] for n in lista if n in OBLIGATORIAS]\n',
         nuevo='    return [n.split(".")[0] for n in lista if n in OBLIGATORIAS + OPCIONALES]\n'),
    # main: una falla imprevista, y lo que dice cuando no se puede abrir.
    dict(id="e84-imprevisto-no-abre-con-el-equipo", archivo=PE,
         pruebas=[TD + "test_main_con_una_falla_imprevista_abre_con_el_del_equipo_si_lo_tiene_todo"],
         viejo='lo que usa.")\n            return SALIDA_EQUIPO\n', nuevo='lo que usa.")\n            return SALIDA_NO_PUEDE\n'),
    dict(id="e84-imprevisto-abre-sin-mirar", archivo=PE,
         pruebas=[TD + "test_main_con_una_falla_imprevista_y_sin_librerias_no_abre"],
         viejo='        if not obligatorias_que_faltan(faltan(sys.executable, "-E")):\n', nuevo="        if True:\n"),
    dict(id="e84-no-dice-por-que-no-abre", archivo=PE, pruebas=[TD + "test_main_cuando_no_se_puede_dice_las_lineas_y_sale_con_11"],
         viejo="        for linea in e.lineas:\n            decir(linea)\n", nuevo="        for linea in []:\n            decir(linea)\n"),
    # faltan(): lo que lee del hijo.
    dict(id="e84-faltan-no-lee-nada", archivo=PE, pruebas=[TAY + "test_faltan_lee_los_nombres_que_imprime_el_hijo"],
         viejo="    sin = set(x.strip() for x in salida.splitlines())\n", nuevo="    sin = set()\n"),
    dict(id="e84-faltan-si-no-corre-cree-que-esta", archivo=PE, pruebas=[TAY + "test_si_el_python_no_corre_faltan_todas"],
         viejo="    if codigo != 0:\n        return nombres\n", nuevo="    if False:\n        return nombres\n"),
    dict(id="e84-faltan-al-reves", archivo=PE,
         pruebas=[TAY + "test_faltan_lee_los_nombres_que_imprime_el_hijo", TAY + "test_con_todas_a_mano_no_falta_ninguna"],
         viejo="    return [n for n in nombres if n in sin]\n", nuevo="    return [n for n in nombres if n not in sin]\n"),
    # instalar(): con hash, solo ruedas, el pip aislado y, si no está, el otro; el hash distinto no se repite.
    dict(id="e84-instalar-sin-hash", archivo=PE, pruebas=[TAY + "test_instalar_usa_hash_solo_ruedas_y_el_pip_del_equipo_aislado"],
         viejo='"install", "--require-hashes",\n', nuevo='"install", "--no-deps",\n'),
    dict(id="e84-instalar-con-codigo-de-instalacion", archivo=PE,
         pruebas=[TAY + "test_instalar_usa_hash_solo_ruedas_y_el_pip_del_equipo_aislado"],
         viejo='"--only-binary=:all:", ', nuevo='"--prefer-binary", '),
    dict(id="e84-instalar-sin-aislar-primero", archivo=PE,
         pruebas=[TAY + "test_instalar_usa_hash_solo_ruedas_y_el_pip_del_equipo_aislado", TAY + "test_si_el_pip_del_equipo_no_esta_donde_siempre_repite_sin_aislar"],
         viejo='    for banderas in (("-I",), ("-E", "-P")):\n', nuevo='    for banderas in (("-E", "-P"), ("-I",)):\n'),
    dict(id="e84-pip-de-respaldo-con-la-carpeta-actual", archivo=PE,
         pruebas=[TAY + "test_si_el_pip_del_equipo_no_esta_donde_siempre_repite_sin_aislar"],
         viejo='    for banderas in (("-I",), ("-E", "-P")):\n', nuevo='    for banderas in (("-I",), ("-E",)):\n'),
    # Qué Python cubre requirements.txt: 32 bits, ARM, y versiones fuera de 3.11 a 3.14 no se intentan.
    dict(id="e84-cobertura-32-bits", archivo=PE, pruebas=[TAY + "test_que_python_cubre_requirements"],
         viejo='    if plataforma == "win32":\n        return "es de 32 bits"\n', nuevo='    if False:\n        return "es de 32 bits"\n'),
    dict(id="e84-cobertura-lee-otro-python", archivo=PE,
         pruebas=[TAY + "test_el_python_de_las_pruebas_esta_dentro_de_la_cobertura_que_se_declara"],
         viejo="    plataforma = plataforma or sysconfig.get_platform()\n", nuevo='    plataforma = plataforma or "win32"\n'),
    dict(id="e84-cobertura-arm", archivo=PE, pruebas=[TAY + "test_que_python_cubre_requirements"],
         viejo='    if plataforma != "win-amd64":\n', nuevo="    if False:\n"),
    dict(id="e84-cobertura-sin-gil", archivo=PE, pruebas=[TAY + "test_que_python_cubre_requirements"],
         viejo='    if sin_gil:\n        return "es la versión sin GIL"\n', nuevo='    if False:\n        return "es la versión sin GIL"\n'),
    dict(id="e84-cobertura-no-lee-el-gil", archivo=PE,
         pruebas=[TAY + "test_el_python_de_las_pruebas_esta_dentro_de_la_cobertura_que_se_declara"],
         viejo='    sin_gil = bool(sysconfig.get_config_var("Py_GIL_DISABLED")) if sin_gil is None else sin_gil\n',
         nuevo="    sin_gil = True if sin_gil is None else sin_gil\n"),
    dict(id="e84-cobertura-version", archivo=PE, pruebas=[TAY + "test_que_python_cubre_requirements"],
         viejo="    if not PYTHON_MINIMO <= tuple(version[:2]) <= PYTHON_MAXIMO:\n", nuevo="    if False:\n"),
    dict(id="e84-cobertura-hasta-la-3-15", archivo=PE,
         pruebas=[TAY + "test_que_python_cubre_requirements"], viejo="PYTHON_MAXIMO = (3, 14)\n", nuevo="PYTHON_MAXIMO = (3, 15)\n"),
    dict(id="e84-cobertura-desde-la-3-10", archivo=PE,
         pruebas=[TAY + "test_que_python_cubre_requirements", TAY + "test_los_bat_piden_el_mismo_minimo_que_el_preparador"],
         viejo="PYTHON_MINIMO = (3, 11)\n", nuevo="PYTHON_MINIMO = (3, 10)\n"),
    dict(id="e84-instala-aunque-no-hay-ruedas", archivo=PE,
         pruebas=[TD + "test_un_python_fuera_de_cobertura_no_instala_y_lo_dice_al_no_abrir",
                  TD + "test_un_python_fuera_de_cobertura_abre_con_el_del_equipo_si_lo_tiene_todo",
                  TD + "test_un_python_fuera_de_cobertura_usa_el_venv_que_ya_esta_completo"],
         viejo="        if fuera and pendiente:\n", nuevo="        if False:\n"),
    dict(id="e84-fuera-de-cobertura-sin-decirlo", archivo=PE,
         pruebas=[TD + "test_un_python_fuera_de_cobertura_no_instala_y_lo_dice_al_no_abrir",
                  TD + "test_dentro_de_la_cobertura_el_mensaje_si_habla_de_la_conexion"],
         viejo="    if fuera:\n        lineas.append(", nuevo="    if not fuera:\n        lineas.append("),
    dict(id="e84-bat-pide-otro-minimo", archivo="Iniciar AQUASHIELD.bat", pruebas=[TAY + "test_los_bat_piden_el_mismo_minimo_que_el_preparador"],
         viejo="sys.version_info >= (3, 11)", nuevo="sys.version_info >= (3, 10)"),
    dict(id="e84-instalar-nunca-repite", archivo=PE, pruebas=[TAY + "test_si_el_pip_del_equipo_no_esta_donde_siempre_repite_sin_aislar"],
         viejo="        if SIN_PIP not in salida:\n            break\n", nuevo="        if True:\n            break\n"),
    dict(id="e84-instalar-siempre-repite", archivo=PE, pruebas=[TAY + "test_otra_falla_de_pip_no_se_repite"],
         viejo="        if SIN_PIP not in salida:\n            break\n", nuevo="        if False:\n            break\n"),
    dict(id="e84-instalar-no-ve-el-hash", archivo=PE,
         pruebas=[TAY + "test_un_hash_distinto_se_dice_y_no_se_repite", TCR + "test_un_hash_que_no_coincide_no_abre_aunque_el_equipo_tenga_todo"],
         viejo='        if HASH_NO_COINCIDE in salida:\n            return "hash", salida\n',
         nuevo='        if False:\n            return "hash", salida\n'),
    dict(id="e84-instalar-otro-archivo", archivo=PE,
         pruebas=[TCR + "test_la_primera_vez_arma_el_venv_e_instala_con_hash", TCR + "test_si_cambian_los_requisitos_vuelve_a_instalar"],
         viejo='"-r", str(RAIZ / REQUISITOS)]', nuevo='"-r", str(RAIZ / "otro.txt")]'),
    # El log y lo que se le muestra a la persona: sin claves, recortado.
    dict(id="e84-log-con-claves", archivo=PE, pruebas=[TAY + "test_el_log_no_guarda_la_clave_de_una_direccion"],
         viejo="{sin_usuario(sin_claves(texto))}\\n\")\n", nuevo="{sin_usuario(texto)}\\n\")\n"),
    dict(id="e84-pantalla-con-claves", archivo=PE, pruebas=[TAY + "test_lo_que_se_le_muestra_a_la_persona_no_trae_claves"],
         viejo="    lineas = [x.strip() for x in sin_usuario(sin_claves(salida)).splitlines() if x.strip()]\n",
         nuevo="    lineas = [x.strip() for x in sin_usuario(salida).splitlines() if x.strip()]\n"),
    dict(id="e84-log-sin-recortar", archivo=PE, pruebas=[TAY + "test_el_log_se_recorta"],
         viejo="        if ruta.exists() and ruta.stat().st_size > LARGO_MAXIMO_LOG:\n", nuevo="        if False:\n"),
    # La huella, el estado y los nombres.
    dict(id="e84-huella-con-fin-de-linea", archivo=PE, pruebas=[TAY + "test_la_huella_no_depende_del_fin_de_linea"],
         viejo='.replace(b"\\r\\n", b"\\n")', nuevo=""),
    dict(id="e84-huella-sin-archivo", archivo=PE, pruebas=[TAY + "test_sin_requirements_la_huella_es_otra_cosa_y_no_falla"],
         viejo='        return "(falta)"\n', nuevo='        return ""\n'),
    dict(id="e84-estado-de-otra-forma", archivo=PE, pruebas=[TAY + "test_un_estado_roto_o_de_otra_forma_se_lee_como_vacio"],
         viejo="    return datos if isinstance(datos, dict) else {}\n", nuevo="    return datos\n"),
    dict(id="e84-estado-deja-el-temporal", archivo=PE, pruebas=[TAY + "test_el_estado_se_guarda_y_se_lee"],
         viejo="                os.replace(temporal, ruta)\n                return\n",
         nuevo="                shutil.copyfile(temporal, ruta)\n                return\n"),
    dict(id="e84-nombrar-sin-y", archivo=PE, pruebas=[TAY + "test_el_nombre_de_las_librerias"],
         viejo='    return nombres[0] if len(nombres) == 1 else ", ".join(nombres[:-1]) + " y " + nombres[-1]\n',
         nuevo='    return nombres[0] if len(nombres) == 1 else ", ".join(nombres)\n'),
    # El .venv: lo crea, lo usa, lo rehace sin borrar antes, no toca el ajeno ni lo que no se pudo correr, y no sigue una unión.
    dict(id="e84-venv-no-lo-crea", archivo=PE, pruebas=[TEP + "test_sin_venv_lo_crea"],
         viejo="    if not os.path.lexists(ruta):\n        return crear_entorno(ruta, python)\n",
         nuevo="    if False:\n        return crear_entorno(ruta, python)\n"),
    dict(id="e84-venv-que-arranca-no-se-usa", archivo=PE, pruebas=[TEP + "test_un_venv_que_arranca_se_usa_tal_cual"],
         viejo="    if codigo == 0:\n        return python\n", nuevo="    if codigo == 0:\n        return None\n"),
    dict(id="e84-venv-ajeno-se-rehace", archivo=PE,
         pruebas=[TEP + "test_uno_ajeno_cuyo_python_no_arranca_no_se_toca",
                  TCR + "test_un_venv_ajeno_que_no_arranca_no_se_toca_y_se_abre_con_el_del_equipo"],
         viejo="    if not (ruta / MARCA).is_file():\n        decir(", nuevo="    if False:\n        decir("),
    dict(id="e84-venv-retenido-se-rehace", archivo=PE, pruebas=[TEP + "test_uno_propio_que_no_se_pudo_correr_no_se_rehace"],
         viejo="    if codigo is None and python.is_file():\n", nuevo="    if False:\n"),
    dict(id="e84-venv-a-medias-no-se-rehace", archivo=PE, pruebas=[TEP + "test_uno_propio_a_medias_sin_python_se_rehace"],
         viejo="    if codigo is None and python.is_file():\n", nuevo="    if codigo is None:\n"),
    dict(id="e84-venv-se-borra-antes", archivo=PE, pruebas=[TEP + "test_uno_propio_cuyo_python_sale_con_error_se_rehace_sin_borrarlo_antes"],
         viejo="        apartar(ruta, viejo)\n", nuevo="        shutil.rmtree(ruta)\n"),
    dict(id="e84-venv-apartado-queda", archivo=PE,
         pruebas=[TEP + "test_uno_propio_cuyo_python_sale_con_error_se_rehace_sin_borrarlo_antes",
                  TCR + "test_un_venv_cuyo_python_ya_no_existe_se_rehace"],
         viejo="    nuevo = crear_entorno(ruta, python)\n    borrar_apartados()\n", nuevo="    nuevo = crear_entorno(ruta, python)\n"),
    dict(id="e84-apartados-solo-lectura", archivo=PE, pruebas=[TEP + "test_los_apartados_viejos_se_borran_aunque_tengan_archivos_de_solo_lectura"],
         viejo="                shutil.rmtree(carpeta / nombre, **opcion)\n", nuevo="                shutil.rmtree(carpeta / nombre)\n"),
    dict(id="e84-union-no-se-ve", archivo=PE,
         pruebas=[TEP + "test_una_union_con_ese_nombre_se_quita_sin_tocar_lo_de_adentro",
                  TCR + "test_una_union_con_el_nombre_del_venv_no_deja_instalar_en_lo_de_afuera"],
         viejo="    return os.path.islink(ruta) or os.path.normcase(os.path.realpath(ruta)) != os.path.normcase(en_su_lugar)\n",
         nuevo="    return os.path.islink(ruta)\n"),
    dict(id="e84-union-no-se-mira", archivo=PE,
         pruebas=[TEP + "test_una_union_con_ese_nombre_se_quita_sin_tocar_lo_de_adentro",
                  TCR + "test_una_union_con_el_nombre_del_venv_no_deja_instalar_en_lo_de_afuera"],
         viejo="    if es_enlace(ruta):\n", nuevo="    if False:\n"),
    dict(id="e84-lo-que-no-existe-es-enlace", archivo=PE, pruebas=[TEP + "test_una_carpeta_comun_no_es_un_enlace"],
         viejo="    if not os.path.lexists(ruta):\n        return False\n", nuevo="    if not os.path.lexists(ruta):\n        return True\n"),
    # Una sola ventana a la vez.
    dict(id="e84-exclusion-no-mira", archivo=PE,
         pruebas=[TEX + "test_la_segunda_ventana_espera_a_la_primera", TCR + "test_dos_ventanas_a_la_vez_dejan_un_solo_entorno"],
         viejo="        if k32.WaitForSingleObject(mutex, 0) not in (0, 0x80):          # ya la tiene otra ventana\n",
         nuevo="        if False:          # ya la tiene otra ventana\n"),
    dict(id="e84-exclusion-no-espera", archivo=PE, pruebas=[TEX + "test_la_segunda_ventana_espera_a_la_primera"],
         viejo="            k32.WaitForSingleObject(mutex, int(ESPERA_OTRA_VENTANA * 1000))\n", nuevo="            pass\n"),
    dict(id="e84-exclusion-de-todas-las-carpetas", archivo=PE, pruebas=[TEX + "test_dos_carpetas_no_se_esperan"],
         viejo='hashlib.sha256(os.path.normcase(str(RAIZ)).encode("utf-8"))', nuevo='hashlib.sha256(b"")'),
    dict(id="e84-exclusion-con-mayusculas", archivo=PE, pruebas=[TEX + "test_dos_carpetas_no_se_esperan"],
         viejo='os.path.normcase(str(RAIZ)).encode("utf-8")', nuevo='str(RAIZ).encode("utf-8")'),
    # Los .bat: el Python, el orden, el PATH del .venv, el código 10 y la red de seguridad.
    dict(id="e84-bat-sin-mirar-el-python", archivo="Iniciar AQUASHIELD.bat", pruebas=[BAT_BLOQUE],
         viejo='  python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul\n', nuevo=""),
    dict(id="e84-bat-emision-sin-mirar-el-python", archivo="Iniciar AQUASHIELD_EMISION.bat", pruebas=[BAT_BLOQUE],
         viejo='  python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul\n', nuevo=""),
    dict(id="e84-bat-prepara-antes-de-actualizar", archivo="Iniciar AQUASHIELD.bat", pruebas=[BAT_BLOQUE],
         cambios=[("  python actualizar.py\n", "  python -I preparar_entorno.py\n  python actualizar.py\n"), (PREPARA_BAT, "")]),
    dict(id="e84-bat-sin-el-path-del-venv", archivo="Iniciar AQUASHIELD.bat", pruebas=[BAT_BLOQUE, ABRE_CON_VENV],
         viejo=PATH_VENV, nuevo="    echo.\n"),
    dict(id="e84-bat-emision-sin-el-path-del-venv", archivo="Iniciar AQUASHIELD_EMISION.bat", pruebas=[BAT_BLOQUE, ABRE_CON_VENV],
         viejo=PATH_VENV, nuevo="    echo.\n"),
    dict(id="e84-bat-crash-no-llega", archivo="Iniciar AQUASHIELD.bat", pruebas=[BAT_IMPREVISTO],
         viejo="  ) else if errorlevel 1 (\n    REM preparar_entorno.py fallo", nuevo="  ) else if errorlevel 99 (\n    REM preparar_entorno.py fallo"),
    dict(id="e84-bat-sin-la-red-de-seguridad", archivo="Iniciar AQUASHIELD.bat", pruebas=[BAT_IMPREVISTO],
         viejo='    python -c "import playwright.sync_api, openpyxl" 2>nul\n    if errorlevel 1 (\n', nuevo="    if 1==0 (\n"),
    dict(id="e84-bat-path-con-comillas", archivo="Iniciar AQUASHIELD.bat", pruebas=[BAT_BLOQUE, ABRE_CON_VENV],
         viejo='%PATH:"=%"', nuevo='%PATH%"'),
    dict(id="e84-bat-emision-path-con-comillas", archivo="Iniciar AQUASHIELD_EMISION.bat", pruebas=[BAT_BLOQUE, ABRE_CON_VENV],
         viejo='%PATH:"=%"', nuevo='%PATH%"'),
    dict(id="e84-bat-codigo-12-o-mas", archivo="Iniciar AQUASHIELD.bat", pruebas=[BAT_BLOQUE, BAT_IMPREVISTO],
         viejo="  if errorlevel 12 cmd /c exit 1\n", nuevo=""),
    dict(id="e84-bat-emision-codigo-12-o-mas", archivo="Iniciar AQUASHIELD_EMISION.bat", pruebas=[BAT_BLOQUE],
         viejo="  if errorlevel 12 cmd /c exit 1\n", nuevo=""),
    dict(id="e84-bat-git-siempre-pregunta", archivo="Iniciar AQUASHIELD.bat", pruebas=[BAT_SIN_GIT],
         viejo='  if errorlevel 1 if not exist "logs\\.git-preguntado" (\n', nuevo="  if errorlevel 1 (\n"),
    dict(id="e84-bat-git-sin-marca", archivo="Iniciar AQUASHIELD.bat", pruebas=[BAT_SIN_GIT],
         viejo='    type nul > "logs\\.git-preguntado"\n', nuevo=""),
    dict(id="e84-bat-python-para-arm", archivo="Iniciar AQUASHIELD.bat", pruebas=[BAT_BLOQUE],
         viejo=" --architecture x64", nuevo=""),
    dict(id="e84-bat-emision-python-para-arm", archivo="Iniciar AQUASHIELD_EMISION.bat", pruebas=[BAT_BLOQUE],
         viejo=" --architecture x64", nuevo=""),
    dict(id="e84-bat-emision-distinto-del-seguro", archivo="Iniciar AQUASHIELD_EMISION.bat", pruebas=[BAT_IGUALES],
         viejo='/t 60 /d N /m "  Falta Python.', nuevo='/t 30 /d N /m "  Falta Python.'),
    # requirements.txt.
    dict(id="e84-requisitos-no-ascii", archivo="requirements.txt", pruebas=[TRQ + "test_es_ascii_con_fin_de_linea_lf"],
         viejo="# Solo ASCII: pip lee este archivo con la pagina de codigos del equipo.",
         nuevo="# Solo ASCII: pip lee este archivo con la página de codigos del equipo."),
    dict(id="e84-requisitos-sin-version-fija", archivo="requirements.txt",
         pruebas=[TRQ + "test_cada_linea_es_un_comentario_una_version_fija_o_un_hash", TRQ + "test_cada_paquete_tiene_hash_y_ninguno_viene_de_una_direccion"],
         viejo="greenlet==3.3.1 \\\n", nuevo="greenlet>=3.3.1 \\\n"),
    dict(id="e84-requisitos-sin-hash", archivo="requirements.txt", pruebas=[TRQ + "test_cada_paquete_tiene_hash_y_ninguno_viene_de_una_direccion"],
         viejo="et-xmlfile==2.0.0 \\\n    --hash=sha256:", nuevo="et-xmlfile==2.0.0 \\\n    # --hash=sha256:"),
    dict(id="e84-requisitos-desde-una-direccion", archivo="requirements.txt",
         pruebas=[TRQ + "test_cada_linea_es_un_comentario_una_version_fija_o_un_hash", TRQ + "test_cada_paquete_tiene_hash_y_ninguno_viene_de_una_direccion"],
         viejo="et-xmlfile==2.0.0 \\\n", nuevo="https://ejemplo.invalid/x.whl\n\net-xmlfile==2.0.0 \\\n"),
    dict(id="e84-requisitos-sin-pyee", archivo="requirements.txt", pruebas=[TRQ + "test_trae_lo_que_el_preparador_exige_para_abrir"],
         viejo="pyee==13.0.0 \\\n", nuevo="pyee-otro==13.0.0 \\\n"),
    dict(id="e84-libreria-sin-requisito", archivo="AQUASHIELD.py",
         pruebas=[TRQ + "test_todo_lo_que_el_programa_importa_de_afuera_esta_en_el_archivo"],
         viejo='VERSION = "2026.09.10"', nuevo='VERSION = "2026.09.10"; import yaml'),
    dict(id="e84-gitignore-sin-el-preparador", archivo=".gitignore", pruebas=[TRQ + "test_el_gitignore_versiona_los_dos_archivos"],
         viejo="!/preparar_entorno.py\n", nuevo=""),
    dict(id="e84-gitignore-sin-requirements", archivo=".gitignore", pruebas=[TRQ + "test_el_gitignore_versiona_los_dos_archivos"],
         viejo="!/requirements.txt\n", nuevo=""),
    # Revisión de seguridad: el preparador corre aislado (-I), y ni las claves ni el usuario de Windows llegan al log
    # ni a la pantalla.
    dict(id="e84-bat-prepara-sin-aislar", archivo="Iniciar AQUASHIELD.bat",
         pruebas=[BAT_BLOQUE, "test_consola.TestLanzadores.test_no_instalan_con_pip_y_llaman_al_preparador_antes_de_abrir"],
         viejo="  python -I preparar_entorno.py\n", nuevo="  python preparar_entorno.py\n"),
    dict(id="e84-bat-emision-prepara-sin-aislar", archivo="Iniciar AQUASHIELD_EMISION.bat",
         pruebas=["test_consola.TestLanzadores.test_no_instalan_con_pip_y_llaman_al_preparador_antes_de_abrir"],
         viejo="  python -I preparar_entorno.py\n", nuevo="  python preparar_entorno.py\n"),
    dict(id="e84-claves-con-arroba", archivo=PE, pruebas=[TAY + "test_la_clave_con_arroba_y_los_parametros_secretos_tampoco_quedan"],
         viejo=r'(https?://)[^/\s]*@', nuevo=r'(https?://)[^/@\s]+@'),
    dict(id="e84-parametros-secretos-pasan", archivo=PE,
         pruebas=[TAY + "test_la_clave_con_arroba_y_los_parametros_secretos_tampoco_quedan"],
         viejo=r'    return re.sub(r"(?i)([?&](?:access_token|api_key|apikey|key|password|passwd|pwd|secret|token)=)[^&\s]+", r"\1****", texto)' + "\n",
         nuevo="    return texto\n"),
    dict(id="e84-log-con-el-usuario", archivo=PE, pruebas=[TAY + "test_el_log_y_lo_que_se_muestra_no_traen_la_carpeta_del_usuario"],
         viejo="{sin_usuario(sin_claves(texto))}", nuevo="{sin_claves(texto)}"),
    dict(id="e84-pantalla-con-el-usuario", archivo=PE,
         pruebas=[TAY + "test_el_log_y_lo_que_se_muestra_no_traen_la_carpeta_del_usuario"],
         viejo="sin_usuario(sin_claves(salida)).splitlines()", nuevo="sin_claves(salida).splitlines()"),
    dict(id="e84-usuario-solo-con-barra-invertida", archivo=PE,
         pruebas=[TAY + "test_el_log_y_lo_que_se_muestra_no_traen_la_carpeta_del_usuario"],
         viejo=r'for variante in (forma, forma.replace("\\", "/")):', nuevo="for variante in (forma,):"),
    dict(id="e84-usuario-solo-en-minuscula", archivo=PE,
         pruebas=[TAY + "test_el_log_y_lo_que_se_muestra_no_traen_la_carpeta_del_usuario"],
         viejo='lambda _: "%USERPROFILE%", texto, flags=re.IGNORECASE)', nuevo='lambda _: "%USERPROFILE%", texto)'),
]

# --- Encargo 84, aquachile-brand: el panel lleva el bloque estándar de marca v48 (header, pie, tema, nombre de usuario),
# con Credenciales y Cerrar AQUASHIELD en una barra de contexto. test_marca vigila el bloque en el panel, la receta del
# tema viejo, la declaración de estados y el extractor (tests/marca/).
TMB = "test_marca.TestBloqueEnElPanel."
TME = "test_marca.TestEstadosDeclarados."
TMX = "test_marca.TestExtractor."
ESTADOS_JSON = "tests/marca/aquashield-estados.json"
EXTRACTOR = "tests/marca/extraer_panel.py"

MUTACIONES += [
    dict(id="e84-marca-bloque-de-otra-version", pruebas=[TMB + "test_el_html_trae_el_bloque_una_sola_vez"],
         viejo='<meta name="aquashield-bloque" content="v48">', nuevo='<meta name="aquashield-bloque" content="v47">'),
    dict(id="e84-marca-js-con-otro-prefijo", pruebas=[TMB + "test_el_js_del_bloque_va_despues_del_pie_y_antes_de_app_js"],
         viejo='const ASH_PREFIX = "mars_reservas_";', nuevo='const ASH_PREFIX = "mars_otro_";'),
    dict(id="e84-marca-app-js-vuelve-al-tema-viejo", pruebas=[TMB + "test_app_js_ya_no_maneja_el_tema_ni_el_nombre_de_usuario"],
         viejo="// ---------- tabla de filas ----------", nuevo='// ---------- tabla de filas ----------\nconst K_TEMA_VIEJO = "aq-tema";'),
    dict(id="e84-marca-header-propio-de_vuelta", pruebas=[TMB + "test_el_css_trae_el_bloque_una_vez_y_no_redefine_el_header"],
         viejo=".context-bar .context-spacer { flex: 1 1 auto; }",
         nuevo=".context-bar .context-spacer { flex: 1 1 auto; }\n.workspace-header { display: flex; }"),
    dict(id="e84-marca-credenciales-sin-su-id", pruebas=[TMB + "test_credenciales_y_cerrar_siguen_con_sus_id_en_la_barra_de_contexto"],
         viejo='id="btn-cred" type="button"', nuevo='id="btn-credenciales" type="button"'),
    dict(id="e84-marca-receta-cambia-el-tema", pruebas=[TMB + "test_la_receta_pasa_el_tema_viejo_a_la_clave_del_bloque"],
         viejo='v === "oscuro" ? "dark-theme" : "light-theme"', nuevo='v === "oscuro" ? "light-theme" : "dark-theme"'),
    dict(id="e84-marca-receta-no-borra-la-clave-vieja", pruebas=[TMB + "test_la_receta_pasa_el_tema_viejo_a_la_clave_del_bloque"],
         viejo="localStorage.removeItem(viejo);", nuevo="void 0;"),
    dict(id="e84-marca-sin-la-regla-del-logo", pruebas=[TMB + "test_el_css_trae_el_bloque_una_vez_y_no_redefine_el_header"],
         viejo=".brand-logo svg {", nuevo=".brand-logo svgX {"),
    dict(id="e84-marca-sin-barra-de-contexto", pruebas=[TMB + "test_el_panel_conserva_las_reglas_que_le_dan_lugar_a_la_nota_y_a_los_estados"],
         viejo="\n.context-bar {\n    flex: 0 0 auto;", nuevo="\n.context-barX {\n    flex: 0 0 auto;"),
    dict(id="e84-marca-fila-emitida-clara-en-oscuro", pruebas=[TMB + "test_el_panel_conserva_las_reglas_que_le_dan_lugar_a_la_nota_y_a_los_estados"],
         viejo="body:not(.light-theme) tbody tr.fila-emitida td {", nuevo="body.nada tbody tr.fila-emitida td {"),
    dict(id="e84-marca-la-nota-del-modo-se-desplaza", pruebas=[TMB + "test_el_panel_conserva_las_reglas_que_le_dan_lugar_a_la_nota_y_a_los_estados"],
         viejo=".rs-panel > .rs-widgets {", nuevo=".rs-panel > .rs-widgetsX {"),
    dict(id="e84-marca-insignia-segura-en-blanco-sobre-verde", pruebas=[TMB + "test_las_insignias_del_modo_van_en_clases_con_los_colores_de_la_paleta"],
         viejo='<span class="modo-insignia seguro">MODO SEGURO</span>',
         nuevo='<span style="background:#10b981;color:#fff;padding:2px 6px">MODO SEGURO</span>'),
    dict(id="e84-marca-insignia-de-emision-sin-regla", pruebas=[TMB + "test_las_insignias_del_modo_van_en_clases_con_los_colores_de_la_paleta"],
         viejo=".modo-insignia.emision {", nuevo=".modo-insignia.emisionX {"),
    dict(id="e84-marca-estado-de-emision-sin-emision", archivo=ESTADOS_JSON,
         pruebas=[TME + "test_el_estado_de_emision_dice_que_la_emision_esta_abierta"],
         viejo="modo_emision: true", nuevo="modo_emision: false"),
    dict(id="e84-marca-abierto-de-emision-que-no-existe", archivo=ESTADOS_JSON,
         pruebas=[TME + "test_los_selectores_de_abierto_existen_en_el_panel"],
         viejo='"abierto": [".modo-insignia.emision"]', nuevo='"abierto": [".modo-insignia.pastilla-que-no-existe"]'),
    dict(id="e84-marca-extractor-hereda-git-dir", archivo=EXTRACTOR, pruebas=[TMX + "test_con_git_dir_puesto_no_toca_ese_repo"],
         viejo='    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}\n',
         nuevo='    env = dict(os.environ)\n'),
    dict(id="e84-marca-api-falsa-sin-config", archivo=ESTADOS_JSON,
         pruebas=[TME + "test_la_api_falsa_responde_lo_que_app_js_lee"],
         viejo="modo_emision: false, usuarios: ['usuario1'], navieras: [], aviso: ''", nuevo="usuarios: ['usuario1']"),
    dict(id="e84-marca-tema-sin-onclick", pruebas=[TMB + "test_el_html_trae_el_bloque_una_sola_vez"],
         viejo='onclick="aquashieldToggleTheme()"', nuevo=""),
    dict(id="e84-marca-procesando-en-naranja", pruebas=["test_envio.TestLecturaDelPanel.test_cada_lectura_nueva_pinta_su_fila"],
         viejo='style="color:var(--text-primary);">procesando…</span>', nuevo='style="color:var(--accent);">procesando…</span>'),
    dict(id="e84-marca-revisar-en-ocre", pruebas=["test_envio.TestLecturaDelPanel.test_cada_lectura_nueva_pinta_su_fila"],
         viejo='style="color:var(--text-primary)">revisar</span>', nuevo='style="color:var(--danger)">revisar</span>'),
    dict(id="e84-marca-estado-sin-por-que", archivo=ESTADOS_JSON, pruebas=[TME + "test_cada_estado_trae_lo_que_el_verificador_pide"],
         viejo='"por_que": "la tabla con las filas', nuevo='"porque": "la tabla con las filas'),
    dict(id="e84-marca-api-falsa-sin-destino", archivo=ESTADOS_JSON, pruebas=[TME + "test_la_api_falsa_responde_lo_que_app_js_lee"],
         viejo="destino_final: 'DESTINO UNO', ", nuevo=""),
    dict(id="e84-marca-api-falsa-repite-las-filas", archivo=ESTADOS_JSON,
         pruebas=[TME + "test_la_api_falsa_responde_lo_que_app_js_lee"], viejo="dado = true; ", nuevo=""),
    dict(id="e84-marca-abierto-que-no-existe", archivo=ESTADOS_JSON,
         pruebas=[TME + "test_los_selectores_de_abierto_existen_en_el_panel"],
         viejo='"#progreso-pill"', nuevo='"#pastilla-que-no-existe"'),
    dict(id="e84-marca-extractor-sin-los-estados", archivo=EXTRACTOR, pruebas=[TMX + "test_arma_el_panel_como_archivos"],
         viejo="    shutil.copyfile(os.path.join(AQUI, ESTADOS), os.path.join(destino, ESTADOS))\n", nuevo="    pass\n"),
    dict(id="e84-marca-extractor-con-rutas-absolutas", archivo=EXTRACTOR, pruebas=[TMX + "test_arma_el_panel_como_archivos"],
         viejo=".replace('href=\"/estilo.css\"', 'href=\"estilo.css\"').replace('src=\"/app.js\"', 'src=\"app.js\"'))",
         nuevo=".replace('href=\"/estilo.css\"', 'href=\"estilo.css\"'))"),
    dict(id="e84-marca-extractor-sin-control", archivo=EXTRACTOR, pruebas=[TMX + "test_aborta_si_el_programa_no_trae_el_header_del_bloque"],
         viejo=' or "aquashield-header" not in consts["HTML_INDEX"]', nuevo=""),
]

# Encargo 85: la insignia de EMISIÓN va llena en los dos temas; la de MODO SEGURO, con borde (test_marca).
TEL = TMB + "test_en_modo_emision_la_insignia_va_llena_en_los_dos_temas"
MUTACIONES += [
    dict(id="e85-emision-vuelve-al-borde", pruebas=[TEL],
         viejo=".modo-insignia.emision { background: #A8441E; border-color: #A8441E; border-width: 2px; color: #FFFFFF; }",
         nuevo=".modo-insignia.emision { border-color: #A8441E; border-width: 2px; background: rgba(168, 68, 30, 0.12); }"),
    dict(id="e85-emision-neutra-en-oscuro", pruebas=[TEL],
         viejo="body:not(.light-theme) .modo-insignia.seguro {", nuevo="body:not(.light-theme) .modo-insignia {"),
    dict(id="e85-emision-con-el-texto-del-tema", pruebas=[TEL],
         viejo="border-width: 2px; color: #FFFFFF; }", nuevo="border-width: 2px; }"),
    dict(id="e85-emision-en-el-ocre-de-la-paleta", pruebas=[TEL],
         viejo="background: #A8441E; border-color: #A8441E;", nuevo="background: #C76728; border-color: #C76728;"),
    dict(id="e85-emision-llena-solo-en-claro", pruebas=[TEL],
         viejo="body:not(.light-theme) .modo-insignia.seguro { background: rgba(30, 45, 59, 0.5); }",
         nuevo="body:not(.light-theme) .modo-insignia.seguro { background: rgba(30, 45, 59, 0.5); }\n"
               "body:not(.light-theme) .modo-insignia.emision { background: rgba(30, 45, 59, 0.5); }"),
    dict(id="e85-seguro-lleno", pruebas=[TEL],
         viejo=".modo-insignia.seguro { border-color: var(--success); background: rgba(108, 139, 139, 0.15); }",
         nuevo=".modo-insignia.seguro { border-color: var(--success); background: #6C8B8B; }"),
]
# Los huecos que encontró la revisión de código del encargo 85 en la prueba de la cascada: la forma larga de una
# propiedad, el atajo «border», una regla genérica sobre la nota y el neutro de MODO SEGURO en oscuro.
MUTACIONES += [
    dict(id="e85-oscuro-con-background-color", pruebas=[TEL],
         viejo="body:not(.light-theme) .modo-insignia.seguro { background: rgba(30, 45, 59, 0.5); }",
         nuevo="body:not(.light-theme) .modo-insignia.seguro { background: rgba(30, 45, 59, 0.5); }\n"
               "body:not(.light-theme) .modo-insignia { background-color: rgba(30, 45, 59, 0.5); }"),
    dict(id="e85-borde-de-seguro-por-atajo", pruebas=[TEL],
         viejo="body:not(.light-theme) .modo-insignia.seguro { background: rgba(30, 45, 59, 0.5); }",
         nuevo="body:not(.light-theme) .modo-insignia.seguro { background: rgba(30, 45, 59, 0.5); }\n"
               "body:not(.light-theme) .modo-insignia.seguro { border: 1px solid var(--border-main); }"),
    dict(id="e85-regla-generica-sobre-la-nota", pruebas=[TEL],
         viejo="body:not(.light-theme) .modo-insignia.seguro { background: rgba(30, 45, 59, 0.5); }",
         nuevo="body:not(.light-theme) .modo-insignia.seguro { background: rgba(30, 45, 59, 0.5); }\n"
               "body:not(.light-theme) #nota-modo span { background: rgba(30, 45, 59, 0.5); }"),
    dict(id="e85-seguro-sin-neutro-en-oscuro", pruebas=[TEL],
         viejo="body:not(.light-theme) .modo-insignia.seguro { background: rgba(30, 45, 59, 0.5); }\n",
         nuevo=""),
]
# Los dos bajos de la revisión de seguridad del encargo 85: el borde de 2 px (lo único que distingue a las dos
# insignias en el alto contraste de Windows) y las reglas que las alcanzan sin nombrar «modo-insignia».
MUTACIONES += [
    dict(id="e85-emision-con-borde-de-1px", pruebas=[TEL],
         viejo="border-color: #A8441E; border-width: 2px;", nuevo="border-color: #A8441E;"),
    dict(id="e85-oscuro-por-la-segunda-clase", pruebas=[TEL],
         viejo="body:not(.light-theme) .modo-insignia.seguro { background: rgba(30, 45, 59, 0.5); }",
         nuevo="body:not(.light-theme) .modo-insignia.seguro { background: rgba(30, 45, 59, 0.5); }\n"
               "body:not(.light-theme) .emision { background: rgba(30, 45, 59, 0.5); }"),
    dict(id="e85-texto-oscuro-desde-la-nota", pruebas=[TEL],
         viejo="body:not(.light-theme) .modo-insignia.seguro { background: rgba(30, 45, 59, 0.5); }",
         nuevo="body:not(.light-theme) .modo-insignia.seguro { background: rgba(30, 45, 59, 0.5); }\n"
               "#nota-modo span { color: #1E2D3B; }"),
]

# --- Encargo 86 (CICLO-msc-destino-final.md): MSC con un puerto de descarga y otro destino final (decisión de Marcelo).
# La lectura de CMA-CGM para separarlos; el puerto en «Port of Discharge» y el destino final después («Door», «TRUCK» y
# «Destination», con la única sugerencia que trae la ciudad como palabra entera); con un solo puerto, el camino de
# siempre; y las listas del modo y del destino, también antes de «Search Schedule». Sin separar, sin distinguir
# mayúsculas, con un nombre dentro del otro, con el destino final en el puerto o el puerto sin cortar en su coma, sin el
# destino final, sin sus listas antes de buscar, sin pulsar «Door», sin comprobarla o con una sola de sus dos señales,
# sin anotarlas, con otro texto o con varias, con «TRUCK» dentro de otra opción, con la primera de varias, con la ciudad
# en cualquier lugar, sin su borde o con el borde de las letras del castellano, sin lecturas iguales, sin volver a leer
# la lista o la opción, sin comprobar el campo, con la celda entera o sus espacios (también los del puerto), sin
# escribir o sin evidencia.
DFM = "test_clics.TestDestinoFinalMsc."
DFM_LECTURA = DFM + "test_la_misma_lectura_que_cma"
DFM_CAMINOS = DFM + "test_los_dos_caminos"
DFM_PAGINA = DFM + "test_el_destino_final_en_la_pagina"
DFM_CORTA = DFM + "test_cada_paso_corta_sin_seguir"
DFM_LISTAS = DFM + "test_las_listas_del_destino_antes_de_buscar"
DFM_LECTORES = "test_planilla.TestDestinoSeparadoMsc.test_los_dos_lectores_separan_las_mismas_filas"
SEPARA_E86 = ("    if not puerto or not final or puerto.upper() in final.upper() or final.upper() in puerto.upper():\n")
PLANO_E86 = "    if a[:len(b)] == b[:len(a)]:\n"
PARTES_E87 = '    a = [_mk_plano(p) for p in puerto.split(",")]\n'
DOOR_E86 = ("    if not _msc_hasta(page, lambda: (activa() or radio.is_checked(timeout=1000)) and "
            "campo_modo.is_visible()):\n")
CIUDAD_E86 = ('    ciudad = " ".join(_ciudad_de(final).split())\n    if not ciudad:\n'
              "        raise ObjetivoNoEncontrado(MSC_PASO_DESTINO")
PUERTO_E86 = '        dest = " ".join(separado[0].split(",")[0].split())\n'
CALZA_E86 = "    return bool(c) and s.startswith(c) and not s[len(c):len(c) + 1].isalnum()\n"
MUTACIONES += [
    dict(id="e86-nunca-separa", pruebas=[DFM_LECTURA, DFM_CAMINOS, DFM_LECTORES],
         viejo=SEPARA_E86, nuevo="    if True:\n"),
    dict(id="e86-separa-sin-mayusculas", pruebas=[DFM_LECTURA],
         viejo=SEPARA_E86, nuevo="    if not puerto or not final or puerto in final or final in puerto:\n"),
    dict(id="e86-separa-con-el-final-dentro", pruebas=[DFM_LECTURA],
         viejo=SEPARA_E86, nuevo="    if not puerto or not final or puerto.upper() in final.upper():\n"),
    dict(id="e86-puerto-con-el-final", pruebas=[DFM_CAMINOS],
         viejo=PUERTO_E86, nuevo="        dest = \" \".join(separado[1].split(\",\")[0].split())\n"),
    dict(id="e86-puerto-sin-cortar-en-la-coma", pruebas=[DFM_CAMINOS],
         viejo=PUERTO_E86, nuevo="        dest = \" \".join(separado[0].split())\n"),
    dict(id="e86-puerto-con-sus-saltos-de-linea", pruebas=[DFM_CAMINOS],
         viejo=PUERTO_E86, nuevo="        dest = separado[0].split(\",\")[0].strip()\n"),
    dict(id="e86-sin-destino-final", pruebas=[DFM_CAMINOS],
         viejo="        _msc_destino_final(page, reg, f, separado[1])\n", nuevo="        pass\n"),
    dict(id="e86-buscar-sin-sus-listas", pruebas=[DFM_CAMINOS, MSC_BUSCA],
         viejo="    _msc_buscar_itinerarios(page, reg, MSC_PUERTOS + (MSC_LISTAS_DEL_DESTINO if separado else ()))\n",
         nuevo="    _msc_buscar_itinerarios(page, reg, MSC_PUERTOS)\n"),
    dict(id="e86-linea-sin-el-puerto", pruebas=[DFM_CAMINOS],
         viejo="    destino = f\"{separado[0]} / {separado[1]}\" if separado else reserva['destino_final']\n",
         nuevo="    destino = reserva['destino_final']\n"),
    dict(id="e86-listas-solo-los-puertos", pruebas=[DFM_LISTAS],
         viejo="    abiertas = [(i, etiqueta) for i, etiqueta in listas if antes[i][0]]\n",
         nuevo="    abiertas = [(i, etiqueta) for i, etiqueta in MSC_PUERTOS if antes[i][0]]\n"),
    dict(id="e86-sin-pulsar-door", pruebas=[DFM_PAGINA],
         viejo="        puerta.click(timeout=4000)\n", nuevo="        pass\n"),
    dict(id="e86-door-sin-comprobar", pruebas=[DFM_CORTA],
         viejo=DOOR_E86, nuevo="    if False:\n"),
    dict(id="e86-door-solo-el-radio", pruebas=[DFM_PAGINA],
         viejo=DOOR_E86, nuevo="    if not _msc_hasta(page, lambda: radio.is_checked(timeout=1000) and campo_modo.is_visible()):\n"),
    dict(id="e86-door-solo-la-clase", pruebas=[DFM_PAGINA],
         viejo=DOOR_E86, nuevo="    if not _msc_hasta(page, lambda: activa() and campo_modo.is_visible()):\n"),
    dict(id="e86-door-sin-sus-senales", pruebas=[DFM_PAGINA],
         viejo="    reg.info(f\"Port of Discharge: Door ✓ ({senales})\")\n",
         nuevo="    reg.info(\"Port of Discharge: Door ✓\")\n"),
    dict(id="e86-door-con-otro-texto", pruebas=[DFM_CORTA],
         viejo="    if dice != \"Door\":\n", nuevo="    if not dice:\n"),
    dict(id="e86-door-uno-de-varios", pruebas=[DFM_CORTA],
         viejo="        if n == 1 and loc.is_visible():\n", nuevo="        if n >= 1 and loc.is_visible():\n"),
    dict(id="e86-modo-dentro-de-otro", pruebas=[DFM_PAGINA],
         viejo="lambda t: t == MSC_EN_CAMION, MSC_EN_CAMION,", nuevo="lambda t: MSC_EN_CAMION in t, MSC_EN_CAMION,"),
    dict(id="e86-modo-sin-comprobar", pruebas=[DFM_CORTA],
         viejo=("    if not _msc_hasta(page, lambda: (campo_modo.input_value(timeout=1000).strip() == MSC_EN_CAMION\n"
                "                                     and campo.is_visible())):\n"),
         nuevo="    if not _msc_hasta(page, lambda: True):\n"),
    dict(id="e86-la-primera-de-varias", pruebas=[DFM_CORTA],
         viejo="    if len(calzan) != 1:\n", nuevo="    if not calzan:\n"),
    dict(id="e86-destino-en-cualquier-lugar", pruebas=[DFM_CORTA],
         viejo=CALZA_E86, nuevo="    return bool(c) and c in s and not s[len(c):len(c) + 1].isalnum()\n"),
    dict(id="e86-destino-sin-borde", pruebas=[DFM_CORTA],
         viejo=CALZA_E86, nuevo="    return bool(c) and s.startswith(c)\n"),
    dict(id="e86-destino-borde-solo-latino", pruebas=[DFM_CORTA],
         viejo=CALZA_E86,
         nuevo="    return bool(c) and s.startswith(c) and s[len(c):len(c) + 1] not in _LETRAS_DE_NAVE\n"),
    dict(id="e86-destino-sin-su-regla", pruebas=[DFM_CORTA],
         viejo="lambda t: _msc_calza_el_destino(t, ciudad), ciudad,", nuevo="lambda t: True, ciudad,"),
    dict(id="e86-lista-sin-lecturas-iguales", pruebas=[DFM_PAGINA],
         viejo=("            op, textos = _msc_opciones(page, lista)\n        except Exception:\n"
                "            op, textos = None, []\n        if textos and textos == anterior:\n"),
         nuevo=("            op, textos = _msc_opciones(page, lista)\n        except Exception:\n"
                "            op, textos = None, []\n        if textos:\n")),
    dict(id="e86-lista-sin-volver-a-leer", pruebas=[DFM_CORTA],
         viejo="    if despues != textos:\n        raise ObjetivoNoEncontrado(paso, f\"la opción que calza",
         nuevo="    if False:\n        raise ObjetivoNoEncontrado(paso, f\"la opción que calza"),
    dict(id="e86-opcion-sin-volver-a-leer", pruebas=[DFM_CORTA],
         viejo="    if ahora != texto:\n        raise ObjetivoNoEncontrado(paso, f\"la opción «{texto[:45]}»: la que",
         nuevo="    if False:\n        raise ObjetivoNoEncontrado(paso, f\"la opción «{texto[:45]}»: la que"),
    dict(id="e86-destino-sin-comprobar", pruebas=[DFM_CORTA],
         viejo="    if not _msc_hasta(page, lambda: \" \".join(campo.input_value(timeout=1000).split()) == elegida):\n",
         nuevo="    if not _msc_hasta(page, lambda: True):\n"),
    dict(id="e86-destino-con-la-celda-entera", pruebas=[DFM_PAGINA],
         viejo=CIUDAD_E86,
         nuevo="    ciudad = final\n    if not ciudad:\n        raise ObjetivoNoEncontrado(MSC_PASO_DESTINO"),
    dict(id="e86-destino-con-sus-espacios", pruebas=[DFM_PAGINA],
         viejo=CIUDAD_E86,
         nuevo="    ciudad = _ciudad_de(final)\n    if not ciudad:\n        raise ObjetivoNoEncontrado(MSC_PASO_DESTINO"),
    dict(id="e86-destino-sin-palabra", pruebas=[DFM_CORTA],
         viejo=CIUDAD_E86,
         nuevo="    ciudad = final\n    if False:\n        raise ObjetivoNoEncontrado(MSC_PASO_DESTINO"),
    dict(id="e86-lista-sin-evidencia", pruebas=[DFM_PAGINA, "test_evidencia.TestCadaReservadorLaDeja.test_solo_ahi"],
         viejo="    _evidencia_antes_de_la_guarda(page, reg, evidencia, f\"con la lista de «{nombre}»\", completa=False)\n",
         nuevo=""),
    dict(id="e86-destino-sin-escribir", pruebas=[DFM_PAGINA],
         viejo="        campo.type(ciudad, delay=90)\n", nuevo="        pass\n"),
]

# --- Encargo 87 (CICLO-destino-final-normalizado.md): una sola regla para MSC y CMA-CGM (_destino_separado), que
# reconoce el mismo lugar escrito distinto (las partes separadas por comas, normalizadas con _mk_plano, coinciden
# hasta la más corta; la contención sigue sin distinguir mayúsculas, como antes) y lee «-» como la celda vacía; y la
# marca del panel (destino_aparte de /api/filas, saneada para mostrarla, y la celda del destino de la página) en sus
# filas. Sin normalizar, sin cortar el puerto en sus partes, solo por el nombre, por contención o con la celda
# entera, con «-» o lo normalizado como vacío, devolviendo lo normalizado, CMA-CGM o MSC con su propia regla,
# CMA-CGM escribiendo lo normalizado; la marca sin el destino o sin sanear, en toda naviera, sin mirar la nave o la
# ruta, solo en MSC; la página sin la marca, sin escapar, sin el puerto o sin su estilo; y el destino de un solo
# puerto de MSC con sus saltos de línea.
E87_API = "test_web.TestPanelCorridas.test_filas_dicen_si_van_con_destino_final"
E87_QUIEN = "test_web.TestPanelCorridas.test_la_marca_del_destino_final_es_de_quien_lo_separa"
E87_PAGINA = "test_envio.TestLecturaDelPanel.test_dice_si_va_con_destino_final"
APARTE_E87 = "    aparte = (None if _fila_sin_nave(nave) or falta or nav not in NAVIERAS_CON_DESTINO_APARTE\n"
MUTACIONES += [
    dict(id="e87-sin-normalizar", pruebas=[DFM_LECTURA, DFM_CAMINOS, E87_API],
         viejo=PARTES_E87, nuevo='    a = [p.strip().upper() for p in puerto.split(",")]\n'),
    dict(id="e87-puerto-sin-sus-partes", pruebas=[DFM_LECTURA],
         viejo=PARTES_E87, nuevo="    a = [_mk_plano(puerto)]\n"),
    dict(id="e87-mismo-lugar-solo-por-el-nombre", pruebas=[DFM_LECTURA],
         viejo=PLANO_E86, nuevo="    if a[0] == b[0]:\n"),
    dict(id="e87-sin-el-mismo-lugar", pruebas=[DFM_LECTURA, DFM_CAMINOS, E87_API],
         viejo=PLANO_E86, nuevo="    if False:\n"),
    dict(id="e87-mismo-lugar-por-contencion", pruebas=[DFM_LECTURA],
         viejo=PLANO_E86,
         nuevo="    if _mk_plano(puerto) in _mk_plano(final) or _mk_plano(final) in _mk_plano(puerto):\n"),
    dict(id="e87-mismo-lugar-con-la-celda-entera", pruebas=[DFM_LECTURA],
         viejo=PLANO_E86, nuevo="    if a == b:\n"),
    dict(id="e87-vacio-normalizado", pruebas=[DFM_LECTURA],
         viejo=SEPARA_E86,
         nuevo=("    if not _mk_plano(puerto) or not final or puerto.upper() in final.upper() "
                "or final.upper() in puerto.upper():\n")),
    dict(id="e87-guion-es-un-puerto", pruebas=[DFM_LECTURA, DFM_CAMINOS, E87_API],
         viejo='    puerto = str(_destino_final_de((reserva or {}).get("destino_orig")) or "").strip()\n',
         nuevo='    puerto = str((reserva or {}).get("destino_orig") or "").strip()\n'),
    dict(id="e87-guion-es-un-destino", pruebas=[DFM_LECTURA],
         viejo='    final = str(_destino_final_de((reserva or {}).get("destino_final")) or "").strip()\n',
         nuevo='    final = str((reserva or {}).get("destino_final") or "").strip()\n'),
    dict(id="e87-devuelve-lo-normalizado", pruebas=[DFM_LECTURA, DFM_CAMINOS, E87_API],
         viejo="    return puerto, final\n", nuevo="    return _mk_plano(puerto), _mk_plano(final)\n"),
    dict(id="e87-cma-con-su-propia-regla", pruebas=[DFM_LECTURA],
         viejo="    tiene_ramp_separado = _destino_separado(reserva) is not None\n",
         nuevo=("    tiene_ramp_separado = bool(dest_orig and dest_fin and dest_orig.upper() not in dest_fin.upper() "
                "and dest_fin.upper() not in dest_orig.upper())\n")),
    dict(id="e87-cma-escribe-lo-normalizado", pruebas=[DFM_LECTURA],
         viejo='    dest_orig = (reserva.get("destino_orig") or "").strip()\n',
         nuevo='    dest_orig = _mk_plano(reserva.get("destino_orig"))\n'),
    dict(id="e87-msc-sin-la-regla", pruebas=[DFM_LECTURA, DFM_CAMINOS, E87_QUIEN],
         viejo="    separado = _destino_separado(reserva)\n", nuevo="    separado = None\n"),
    dict(id="e87-marca-sin-el-destino", pruebas=[E87_API],
         viejo="destino_aparte=[_destino_a_la_vista(t) for t in aparte] if aparte else None)",
         nuevo="destino_aparte=None)"),
    dict(id="e87-marca-sin-sanear", pruebas=[E87_API],
         viejo="destino_aparte=[_destino_a_la_vista(t) for t in aparte] if aparte else None)",
         nuevo="destino_aparte=list(aparte) if aparte else None)"),
    dict(id="e87-sanea-sin-los-privados", pruebas=[E87_API],
         viejo='"?" if unicodedata.category(c).startswith("C") else c',
         nuevo='"?" if unicodedata.category(c) in ("Cc", "Cf") else c'),
    dict(id="e87-sanea-solo-los-controles", pruebas=[E87_API],
         viejo='"?" if unicodedata.category(c).startswith("C") else c',
         nuevo='"?" if unicodedata.category(c) == "Cc" else c'),
    dict(id="e87-marca-en-toda-naviera", pruebas=[E87_API],
         viejo=APARTE_E87, nuevo="    aparte = (None if _fila_sin_nave(nave) or falta\n"),
    dict(id="e87-marca-sin-mirar-la-nave", pruebas=[E87_API],
         viejo=APARTE_E87, nuevo="    aparte = (None if falta or nav not in NAVIERAS_CON_DESTINO_APARTE\n"),
    dict(id="e87-marca-sin-mirar-la-ruta", pruebas=[E87_API],
         viejo=APARTE_E87, nuevo="    aparte = (None if _fila_sin_nave(nave) or nav not in NAVIERAS_CON_DESTINO_APARTE\n"),
    dict(id="e87-marca-solo-msc", pruebas=[E87_API, E87_QUIEN],
         viejo='NAVIERAS_CON_DESTINO_APARTE = ("msc", "cma")\n', nuevo='NAVIERAS_CON_DESTINO_APARTE = ("msc",)\n'),
    dict(id="e87-pagina-sin-la-marca", pruebas=[E87_PAGINA],
         viejo="          : f.destino_aparte ? esc(f.destino_aparte[0])",
         nuevo="          : false ? esc(f.destino_aparte[0])"),
    dict(id="e87-pagina-sin-escapar", pruebas=[E87_PAGINA],
         viejo='+ esc(f.destino_aparte[1]) + "</span>"', nuevo='+ f.destino_aparte[1] + "</span>"'),
    dict(id="e87-pagina-sin-el-puerto", pruebas=[E87_PAGINA],
         viejo='? esc(f.destino_aparte[0]) + " <span', nuevo='? esc(f.destino_final) + " <span'),
    dict(id="e87-pagina-sin-estilo", pruebas=[E87_PAGINA],
         viejo=".destino-aparte { color: var(--text-muted); font-style: italic; }\n", nuevo=""),
    dict(id="e87-un-puerto-con-sus-saltos-de-linea", pruebas=[DFM_CAMINOS],
         viejo=('        dest = " ".join((reserva["destino_final"] or reserva["destino_orig"] or "")'
                '.split(",")[0].split())\n'),
         nuevo='        dest = (reserva["destino_final"] or reserva["destino_orig"] or "").split(",")[0].strip()\n'),
]

# --- Encargo 89 (CICLO-hyundai-contrato-por-posicion.md): «Contract No» de HYUNDAI elige solo la única opción cuyo
# código es el contrato configurado entero (_hmm_contratos_que_calzan, _hmm_codigo_del_contrato; la decisión (a)), y
# después lee que quedó esa; si la lista no trae contratos, si no está, si dos tienen ese código, si la lista no acepta
# la elección o queda con otra, NO ENVIADA sin elegir nada; los motivos dicen dónde se escribe
# (HMM_DONDE_VA_EL_CONTRATO) y muestran el contrato saneado (_hmm_contrato_a_la_vista); y el paso 2 le quita los
# espacios al contrato. Eligiendo la primera real o la primera de dos, culpando al contrato sin lista, siguiendo si no
# la acepta o si queda otra, sin leer qué quedó, con el texto configurado o con «contiene», con la primera lectura que
# trae una real, leyendo una sola vez o sin esperar, distinguiendo mayúsculas o espacios, con un contrato de solo
# espacios, con «Direct Input» como contrato, con config.json en el motivo, con el contrato sin sanear o sin su tope,
# sin quitarle los espacios al de las credenciales (paso 2 o 3), o sin elegir en el paso 3.
CH = "test_ayudantes.TestContratoDeHyundai."
CH_ELIGE = CH + "test_elige_la_unica_que_trae_el_contrato"
CH_ENTERO = CH + "test_el_contrato_se_compara_entero"
CH_NO_ESTA = CH + "test_si_no_esta_no_envia_y_no_elige_por_posicion"
CH_SIN_LISTA = CH + "test_si_la_lista_no_trae_contratos_no_culpa_al_configurado"
CH_DOS = CH + "test_si_dos_tienen_el_mismo_codigo_no_elige_la_primera"
CH_NO_ACEPTA = CH + "test_si_la_lista_no_acepta_la_eleccion_corta"
CH_QUEDA = CH + "test_si_la_lista_queda_con_otra_opcion_corta"
CH_SANEADO = CH + "test_el_motivo_muestra_el_contrato_saneado"
CH_NO_SON = CH + "test_las_opciones_que_no_son_un_contrato_no_cuentan"
CH_MOTIVOS = CH + "test_los_motivos_dicen_donde_se_escribe"
CALZAN_E89 = "    calzan = _hmm_contratos_que_calzan(opciones, ctto)\n"
SELECT_E89 = '    if not _hmm_select_por_texto(page, "#selContractNo", [calzan[0]], reg, "Contract No"):\n'
CALZA_E89 = ("            if c and o and o.strip().lower() not in HMM_NO_SON_CONTRATO and _hmm_codigo_del_contrato(o) == c]"
             "\n")
CODIGO_E89 = '    return str(opcion or "").split(" - ")[0].strip().upper()\n'
PASO3_E89 = '    ctto = str(creds.get("contrato") or "").strip() or _contrato_por_defecto("hyundai")\n    if not ctto:\n'
PASO2_E89 = '    ctto = str(creds.get("contrato") or "").strip() or _contrato_por_defecto("hyundai")\n    if ctto:\n'
MUTACIONES += [
    dict(id="e89-elige-la-primera-real", pruebas=[CH_NO_ESTA],
         viejo=CALZAN_E89,
         nuevo=("    calzan = (_hmm_contratos_que_calzan(opciones, ctto)\n"
                "              or [o for o in opciones if o and o.lower() not in HMM_NO_SON_CONTRATO][:1])\n")),
    dict(id="e89-elige-la-primera-de-dos", pruebas=[CH_DOS],
         viejo="    if len(calzan) > 1:\n", nuevo="    if False:\n"),
    dict(id="e89-culpa-al-contrato-sin-lista", pruebas=[CH_SIN_LISTA],
         viejo="    if not reales:\n", nuevo="    if False:\n"),
    dict(id="e89-sigue-si-no-la-acepta", pruebas=[CH_NO_ACEPTA],
         viejo=SELECT_E89,
         nuevo='    if _hmm_select_por_texto(page, "#selContractNo", [calzan[0]], reg, "Contract No") and False:\n'),
    dict(id="e89-elige-con-el-texto-configurado", pruebas=[CH_ENTERO],
         viejo=SELECT_E89, nuevo='    if not _hmm_select_por_texto(page, "#selContractNo", [ctto], reg, "Contract No"):\n'),
    dict(id="e89-calza-si-lo-contiene", pruebas=[CH_ENTERO],
         viejo=CALZA_E89,
         nuevo="            if c and o and o.strip().lower() not in HMM_NO_SON_CONTRATO and c in o.upper()]\n"),
    dict(id="e89-sigue-si-queda-otra", pruebas=[CH_QUEDA],
         viejo="    if elegida != calzan[0].strip():\n", nuevo="    if False:\n"),
    dict(id="e89-da-por-elegida-sin-leerla", pruebas=[CH_QUEDA],
         viejo="        elegida = None\n", nuevo="        elegida = calzan[0]\n"),
    dict(id="e89-se-queda-con-la-primera-lectura-real", pruebas=[CH_ELIGE],
         viejo="        if _hmm_contratos_que_calzan(opciones, ctto):\n            break\n",
         nuevo=("        if [o for o in opciones if o and o.lower() not in HMM_NO_SON_CONTRATO]:\n"
                "            break\n")),
    dict(id="e89-lee-una-sola-vez", pruebas=[CH_NO_ESTA],
         viejo="HMM_LECTURAS_CONTRATO = 15\n", nuevo="HMM_LECTURAS_CONTRATO = 1\n"),
    dict(id="e89-lee-sin-esperar", pruebas=[CH_NO_ESTA],
         viejo="    for _ in range(HMM_LECTURAS_CONTRATO):\n        esperar(page, 0.4)\n",
         nuevo="    for _ in range(HMM_LECTURAS_CONTRATO):\n        pass\n"),
    dict(id="e89-distingue-mayusculas", pruebas=[CH_ELIGE],
         viejo='    c = str(ctto or "").strip().upper()\n', nuevo='    c = str(ctto or "").strip()\n'),
    dict(id="e89-opcion-sin-mayusculas", pruebas=[CH_ELIGE],
         viejo=CODIGO_E89, nuevo='    return str(opcion or "").split(" - ")[0].strip()\n'),
    dict(id="e89-con-sus-espacios", pruebas=[CH_ELIGE],
         viejo='    c = str(ctto or "").strip().upper()\n', nuevo='    c = str(ctto or "").upper()\n'),
    dict(id="e89-calza-con-solo-espacios", pruebas=[CH_NO_SON],
         viejo=CALZA_E89,
         nuevo="            if o and o.strip().lower() not in HMM_NO_SON_CONTRATO and _hmm_codigo_del_contrato(o) == c]\n"),
    dict(id="e89-direct-input-es-un-contrato", pruebas=[CH_NO_SON],
         viejo='HMM_NO_SON_CONTRATO = ("select", "dummy", "direct input")\n', nuevo='HMM_NO_SON_CONTRATO = ("select",)\n'),
    dict(id="e89-motivo-con-config", pruebas=[CH_NO_ESTA, CH_MOTIVOS],
         viejo='HMM_DONDE_VA_EL_CONTRATO = "panel → Credenciales → HYUNDAI → columna Contrato"\n',
         nuevo='HMM_DONDE_VA_EL_CONTRATO = "config.json → opciones → contratos_por_defecto → hyundai"\n'),
    dict(id="e89-motivo-sin-sanear", pruebas=[CH_SANEADO],
         viejo="    visto = _hmm_contrato_a_la_vista(ctto)\n", nuevo='    visto = str(ctto or "").strip()\n'),
    dict(id="e89-saneado-sin-tope", pruebas=[CH_SANEADO],
         viejo="    return _destino_a_la_vista(ctto)[:40]\n", nuevo="    return _destino_a_la_vista(ctto)\n"),
    dict(id="e89-sin-contrato-con-el-motivo-de-antes", pruebas=[CH_MOTIVOS],
         viejo='                                   f"un contrato (se escribe en el {HMM_DONDE_VA_EL_CONTRATO})")\n',
         nuevo='                                   "un contrato en las credenciales o en config.json")\n'),
    dict(id="e89-contrato-con-sus-espacios", pruebas=[CH_MOTIVOS],
         viejo=PASO3_E89,
         nuevo='    ctto = creds.get("contrato", "") or _contrato_por_defecto("hyundai")\n    if not ctto:\n'),
    dict(id="e89-paso2-con-sus-espacios", pruebas=[CH_MOTIVOS],
         viejo=PASO2_E89,
         nuevo='    ctto = creds.get("contrato", "") or _contrato_por_defecto("hyundai")\n    if ctto:\n'),
    dict(id="e89-paso3-sin-elegir", pruebas=[CD_HMM],
         viejo="    _hmm_elegir_contrato(page, ctto, reg)\n", nuevo="    pass\n"),
    # Tras la segunda revisión de código: los dos JavaScript que leen la lista, corridos en Node; la línea de log.txt
    # que dice qué opción quedó; y el motivo que dice qué es el código.
    dict(id="e89-js-elegida-lee-el-valor", pruebas=[CH + "test_js_lee_la_lista_y_la_opcion_elegida"],
         viejo="    return o ? (o.textContent||'').trim() : null;}\"\"\"\n",
         nuevo="    return o ? o.value : null;}\"\"\"\n"),
    dict(id="e89-js-elegida-la-primera", pruebas=[CH + "test_js_lee_la_lista_y_la_opcion_elegida"],
         viejo="    const o = s && s.selectedIndex >= 0 ? s.options[s.selectedIndex] : null;\n",
         nuevo="    const o = s && s.selectedIndex >= 0 ? s.options[0] : null;\n"),
    dict(id="e89-js-opciones-sin-recortar", pruebas=[CH + "test_js_lee_la_lista_y_la_opcion_elegida"],
         viejo="    return s ? [...s.options].map(o=>(o.textContent||'').trim()) : [];}\"\"\"\n",
         nuevo="    return s ? [...s.options].map(o=>o.textContent||'') : [];}\"\"\"\n"),
    dict(id="e89-no-dice-cual-quedo", pruebas=[CH_QUEDA],
         viejo='            reg.info(f"Contract No: la lista quedó con «{_hmm_contrato_a_la_vista(elegida)}»")\n',
         nuevo="            pass\n"),
    dict(id="e89-motivo-sin-el-codigo", pruebas=[CH_NO_ESTA],
         viejo='                                   f"entero con el código de cada opción, su texto antes de « - »; se corrige en el "\n',
         nuevo='                                   f"entero con el código de cada opción; se corrige en el "\n'),
]
