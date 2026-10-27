# -*- coding: utf-8 -*-
"""El entorno propio del programa (preparar_entorno.py y requirements.txt; decisión de Marcelo, encargo 84,
CICLO-entorno-propio.md): al abrir, el programa deja listas sus librerías en su carpeta .venv, sin terminal, y si no
puede abre con el Python del equipo solo si ese ya las tiene.

Tres capas:
- las decisiones (qué se instala, cuándo se abre con el Python del equipo, cuándo no se abre), con el módulo cargado en
  la prueba y sus ayudantes de procesos reemplazados;
- el camino real, en un proceso aparte y sin red: un índice local con ruedas inventadas (los mismos nombres de módulo
  que las librerías de verdad, con una marca) y pip de verdad, con `--require-hashes`;
- el requirements.txt: su forma, y que cubra todo lo que el programa importa.
Todo en carpetas nuevas del temporal; nada toca la carpeta del programa."""
import ast
import ctypes
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import unittest
import zipfile
from pathlib import Path
from unittest import mock

import soporte
import test_actualizar                  # el módulo: importar la clase la haría correr también desde este archivo
from test_actualizar import borrar, carpeta_corta
from test_actualizar import correr as correr_cmd

PREPARADOR = soporte.FUENTES / "preparar_entorno.py"
REQUISITOS = soporte.FUENTES / "requirements.txt"
LOS_TRES = ["playwright.sync_api", "openpyxl", "holidays"]


def cerrar(proceso):
    """Un proceso hijo de la prueba: lo cierra si sigue vivo y suelta sus tuberías."""
    if proceso.poll() is None:
        proceso.kill()
    proceso.wait(30)
    for tuberia in (proceso.stdout, proceso.stderr):
        if tuberia:
            tuberia.close()


def cargar_preparador():
    """El módulo, nuevo en cada prueba. No hace nada al importarse."""
    spec = importlib.util.spec_from_file_location("preparar_entorno_prueba", PREPARADOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestDecisiones(unittest.TestCase):
    """preparar() decide con lo que dicen faltan(), entorno_propio() e instalar(); aquí los tres son falsos."""

    def setUp(self):
        soporte.DISPAROS.clear()
        self.m = cargar_preparador()
        self.raiz = carpeta_corta("aq_env_")
        self.addCleanup(borrar, self.raiz)
        self.m.RAIZ = self.raiz
        (self.raiz / "requirements.txt").write_bytes(b"uno==1 \\\n    --hash=sha256:" + b"0" * 64 + b"\n")
        self.dicho = []
        self.m.decir = self.dicho.append

    def tearDown(self):
        self.assertEqual(soporte.DISPAROS, [])

    def preparar(self, venv=True, propio=True, faltan_venv=((),), instalar=("listo", ""), faltan_equipo=(),
                 estado=None, fuera=None):
        """(lo que devolvió preparar() o ("NoPuede", sus líneas), cuántas veces instaló y miró al Python del equipo)."""
        m = self.m
        python = self.raiz / ".venv" / "Scripts" / "python.exe"
        if venv:
            (self.raiz / ".venv").mkdir()
            if propio:
                (self.raiz / ".venv" / m.MARCA).write_text("marca", encoding="utf-8")
        cuenta = {"instalar": 0, "equipo": 0}
        secuencia = [list(x) for x in faltan_venv]

        def falso_faltan(py, bandera):
            if bandera == "-E":
                cuenta["equipo"] += 1
                return list(faltan_equipo)
            return secuencia.pop(0) if len(secuencia) > 1 else list(secuencia[0])

        def falso_instalar(py):
            cuenta["instalar"] += 1
            return instalar

        m.entorno_propio = lambda: python if venv else None
        m.fuera_de_cobertura = lambda *a, **k: fuera          # el Python de las pruebas no decide el resultado
        m.faltan = falso_faltan
        m.instalar = falso_instalar
        if estado is not None:
            m.guardar_estado(estado(m) if callable(estado) else estado)
        try:
            salida = m.preparar()
        except m.NoPuede as e:
            salida = ("NoPuede", e.lineas)
        return salida, cuenta

    def test_al_dia_no_instala_ni_dice_nada(self):
        m = self.m
        salida, cuenta = self.preparar(estado=lambda mod: {"requisitos": mod.huella_de_requisitos()})
        self.assertEqual((salida, cuenta, self.dicho), (m.SALIDA_PROPIO, {"instalar": 0, "equipo": 0}, []))

    def test_un_python_fuera_de_cobertura_no_instala_y_lo_dice_al_no_abrir(self):
        # Sin ruedas con hash para este Python (32 bits, ARM, 3.15) pip falla: no se intenta, y el mensaje no culpa a la red.
        falta = [list(LOS_TRES)]
        salida, cuenta = self.preparar(faltan_venv=falta, instalar=("fallo", "x"), faltan_equipo=list(LOS_TRES),
                                       fuera="es de 32 bits")
        self.assertEqual((salida[0], cuenta["instalar"]), ("NoPuede", 0))
        self.assertIn("«playwright» y «openpyxl»", salida[1][0])
        self.assertIn("es de 32 bits", salida[1][1])
        self.assertIn("3.11 a 3.14", salida[1][1])
        self.assertNotIn("conexión", salida[1][1])

    def test_dentro_de_la_cobertura_el_mensaje_si_habla_de_la_conexion(self):
        falta = [list(LOS_TRES), list(LOS_TRES)]
        salida, _ = self.preparar(faltan_venv=falta, instalar=("fallo", "x"), faltan_equipo=list(LOS_TRES))
        self.assertIn("conexión", salida[1][1])
        self.assertNotIn("3.11 a 3.14", salida[1][1])

    def test_un_python_fuera_de_cobertura_abre_con_el_del_equipo_si_lo_tiene_todo(self):
        salida, cuenta = self.preparar(faltan_venv=(list(LOS_TRES),), faltan_equipo=[], fuera="es la 3.15")
        self.assertEqual((salida, cuenta), (self.m.SALIDA_EQUIPO, {"instalar": 0, "equipo": 1}))

    def test_un_python_fuera_de_cobertura_usa_el_venv_que_ya_esta_completo(self):
        salida, cuenta = self.preparar(faltan_venv=((),), estado={"requisitos": "otros"}, fuera="es la 3.15")
        self.assertEqual((salida, cuenta["instalar"]), (self.m.SALIDA_PROPIO, 0))

    def test_si_cambiaron_los_requisitos_instala_y_lo_anota(self):
        m = self.m
        salida, cuenta = self.preparar(faltan_venv=([], []), estado={"requisitos": "otros"})
        self.assertEqual((salida, cuenta["instalar"]), (m.SALIDA_PROPIO, 1))
        self.assertEqual(m.leer_estado()["requisitos"], m.huella_de_requisitos())

    def test_sin_estado_instala(self):
        salida, cuenta = self.preparar(faltan_venv=([], []))
        self.assertEqual((salida, cuenta["instalar"]), (self.m.SALIDA_PROPIO, 1))

    def test_si_falta_una_libreria_instala_aunque_los_requisitos_no_cambien(self):
        m = self.m
        salida, cuenta = self.preparar(faltan_venv=(["openpyxl"], []),
                                       estado=lambda mod: {"requisitos": mod.huella_de_requisitos()})
        self.assertEqual((salida, cuenta["instalar"]), (m.SALIDA_PROPIO, 1))

    def test_sin_red_y_con_todo_en_el_equipo_abre_con_el_del_equipo(self):
        m = self.m
        falta = [list(LOS_TRES), list(LOS_TRES)]
        salida, cuenta = self.preparar(faltan_venv=falta, instalar=("fallo", "sin conexion"), faltan_equipo=[])
        self.assertEqual((salida, cuenta), (m.SALIDA_EQUIPO, {"instalar": 1, "equipo": 1}))
        self.assertTrue(any("abro con el Python del equipo" in x for x in self.dicho), self.dicho)

    def test_sin_red_y_sin_nada_en_el_equipo_no_abre_y_dice_que_falta(self):
        falta = [list(LOS_TRES), list(LOS_TRES)]
        salida, cuenta = self.preparar(faltan_venv=falta, instalar=("fallo", "x"), faltan_equipo=["playwright.sync_api"])
        self.assertEqual(salida[0], "NoPuede")
        self.assertIn("falta «playwright» y no se pudo instalar", salida[1][0])
        self.assertNotIn("openpyxl", salida[1][0])

    def test_si_faltan_las_dos_el_mensaje_concuerda_en_plural(self):
        falta = [list(LOS_TRES), list(LOS_TRES)]
        salida, _ = self.preparar(faltan_venv=falta, instalar=("fallo", "x"), faltan_equipo=list(LOS_TRES))
        self.assertIn("faltan «playwright» y «openpyxl» y no se pudo instalar", salida[1][0])

    def test_tras_una_falla_reciente_con_el_venv_vacio_y_el_equipo_completo_no_vuelve_a_esperar_a_pip(self):
        # Sin red, con el .venv vacío y el Python del equipo completo, cada inicio esperaba a pip unos 65 s (medido por la
        # revisión de código del encargo 84). Tras una falla de estos mismos requisitos, abre con el del equipo sin pip.
        m = self.m
        estado = lambda mod: {"requisitos": "otros", "intento": {"requisitos": mod.huella_de_requisitos(),
                                                                 "cuando": time.time() - 60}}
        salida, cuenta = self.preparar(faltan_venv=(list(LOS_TRES),), faltan_equipo=[], estado=estado)
        self.assertEqual((salida, cuenta["instalar"]), (m.SALIDA_EQUIPO, 0))

    def test_tras_una_falla_reciente_si_el_equipo_no_tiene_nada_vuelve_a_probar_con_pip(self):
        # Si no hay con qué abrir, esperar a pip sigue siendo lo único que se puede hacer.
        m = self.m
        estado = lambda mod: {"requisitos": "otros", "intento": {"requisitos": mod.huella_de_requisitos(),
                                                                 "cuando": time.time() - 60}}
        salida, cuenta = self.preparar(faltan_venv=(list(LOS_TRES), []), faltan_equipo=list(LOS_TRES), estado=estado)
        self.assertEqual((salida, cuenta["instalar"]), (m.SALIDA_PROPIO, 1))

    def test_un_hash_que_no_coincide_no_abre_ni_con_el_python_del_equipo(self):
        # El Python del equipo no se mira: no se abre con lo que haya, y se avisa.
        salida, cuenta = self.preparar(faltan_venv=(list(LOS_TRES),), instalar=("hash", ""), faltan_equipo=[])
        self.assertEqual((salida[0], cuenta["equipo"]), ("NoPuede", 0))
        self.assertIn("hash", salida[1][0])

    def test_si_solo_falta_holidays_abre_con_el_entorno_propio(self):
        # Sin holidays el programa sigue de lunes a viernes y lo avisa (CICLO-maersk-cuatro-puntos.md).
        salida, cuenta = self.preparar(faltan_venv=(["holidays"], ["holidays"]), instalar=("fallo", "x"))
        self.assertEqual((salida, cuenta["equipo"]), (self.m.SALIDA_PROPIO, 0))

    def test_sin_entorno_propio_abre_con_el_del_equipo_si_lo_tiene_todo(self):
        salida, cuenta = self.preparar(venv=False, faltan_equipo=[])
        self.assertEqual((salida, cuenta), (self.m.SALIDA_EQUIPO, {"instalar": 0, "equipo": 1}))

    def test_sin_entorno_propio_y_sin_nada_en_el_equipo_no_abre(self):
        salida, _ = self.preparar(venv=False, faltan_equipo=["openpyxl", "holidays"])
        self.assertEqual(salida[0], "NoPuede")
        self.assertIn("«openpyxl»", salida[1][0])
        self.assertNotIn("holidays", salida[1][0])

    def test_un_venv_que_no_armo_el_programa_no_se_llena(self):
        # Un .venv de la persona que arranca pero le faltan librerías: no se le instala nada.
        salida, cuenta = self.preparar(propio=False, faltan_venv=(["playwright.sync_api"],), faltan_equipo=[])
        self.assertEqual((salida, cuenta["instalar"]), (self.m.SALIDA_EQUIPO, 0))

    def test_un_venv_ajeno_con_todo_se_usa_sin_instalar(self):
        salida, cuenta = self.preparar(propio=False, faltan_venv=((),))
        self.assertEqual((salida, cuenta["instalar"]), (self.m.SALIDA_PROPIO, 0))

    def test_tras_una_falla_reciente_no_vuelve_a_esperar_a_pip_si_todo_se_importa(self):
        # Sin red y con una versión nueva en requirements.txt: cada inicio esperaría a pip por algo que el programa no
        # necesita para abrir. Pasados PAUSA_REINTENTO s, vuelve a probar.
        m = self.m
        for hace, instala in ((60, 0), (m.PAUSA_REINTENTO + 60, 1)):
            with self.subTest(hace=hace):
                for p in list(self.raiz.glob(".venv")):
                    borrar(p)
                estado = lambda mod, h=hace: {"requisitos": "otros", "intento": {
                    "requisitos": mod.huella_de_requisitos(), "cuando": time.time() - h}}
                salida, cuenta = self.preparar(faltan_venv=([], []), estado=estado)
                self.assertEqual((salida, cuenta["instalar"]), (m.SALIDA_PROPIO, instala))

    def test_el_intento_fallido_de_otros_requisitos_no_cuenta(self):
        m = self.m
        estado = {"requisitos": "otros", "intento": {"requisitos": "los de antes", "cuando": time.time()}}
        salida, cuenta = self.preparar(faltan_venv=([], []), estado=estado)
        self.assertEqual((salida, cuenta["instalar"]), (m.SALIDA_PROPIO, 1))

    def test_una_falla_de_pip_con_todo_importable_anota_el_intento(self):
        self.preparar(faltan_venv=([], []), instalar=("fallo", "sin conexion"), estado={"requisitos": "otros"})
        estado = self.m.leer_estado()
        self.assertEqual(estado["intento"]["requisitos"], self.m.huella_de_requisitos())
        self.assertEqual(estado["requisitos"], "otros")          # no se da por instalado lo que no se instaló

    def test_si_pip_dijo_listo_pero_algo_sigue_faltando_no_da_por_hecho_nada(self):
        m = self.m
        salida, cuenta = self.preparar(faltan_venv=(["openpyxl"], ["openpyxl"]), instalar=("listo", ""),
                                       faltan_equipo=[])
        self.assertEqual((salida, "requisitos" in m.leer_estado()), (m.SALIDA_EQUIPO, False))

    def test_main_con_una_falla_imprevista_abre_con_el_del_equipo_si_lo_tiene_todo(self):
        m = self.m
        m.esperar_a_las_otras_ventanas = lambda: None
        m.preparar = mock.Mock(side_effect=RuntimeError("imprevisto"))
        m.faltan = lambda py, bandera: []
        self.assertEqual(m.main(), m.SALIDA_EQUIPO)
        self.assertIn("RuntimeError", (self.raiz / "logs" / "entorno.log").read_text(encoding="utf-8"))

    def test_main_con_una_falla_imprevista_y_sin_librerias_no_abre(self):
        m = self.m
        m.esperar_a_las_otras_ventanas = lambda: None
        m.preparar = mock.Mock(side_effect=RuntimeError("imprevisto"))
        m.faltan = lambda py, bandera: ["playwright.sync_api"]
        self.assertEqual(m.main(), m.SALIDA_NO_PUEDE)

    def test_main_cuando_no_se_puede_dice_las_lineas_y_sale_con_11(self):
        m = self.m
        m.esperar_a_las_otras_ventanas = lambda: None
        m.preparar = mock.Mock(side_effect=m.NoPuede(["uno", "dos"]))
        self.assertEqual((m.main(), self.dicho), (m.SALIDA_NO_PUEDE, ["uno", "dos"]))

    def test_las_obligatorias_son_las_que_el_programa_necesita_para_abrir(self):
        m = self.m
        self.assertEqual(m.obligatorias_que_faltan(["holidays", "openpyxl", "playwright.sync_api"]),
                         ["openpyxl", "playwright"])
        self.assertEqual(m.obligatorias_que_faltan(["holidays"]), [])


class TestAyudantes(unittest.TestCase):
    def setUp(self):
        soporte.DISPAROS.clear()
        self.m = cargar_preparador()
        self.raiz = carpeta_corta("aq_env_")
        self.addCleanup(borrar, self.raiz)
        self.m.RAIZ = self.raiz

    def tearDown(self):
        self.assertEqual(soporte.DISPAROS, [])

    def test_faltan_lee_los_nombres_que_imprime_el_hijo(self):
        m = self.m
        with mock.patch.object(m, "correr", return_value=(0, "openpyxl\r\nholidays\r\n")) as c:
            self.assertEqual(m.faltan("py", "-I"), ["openpyxl", "holidays"])
        comando = c.call_args[0][0]
        self.assertEqual(comando[:3], ["py", "-I", "-c"])
        for nombre in LOS_TRES:
            self.assertIn(nombre, comando[3])

    def test_si_el_python_no_corre_faltan_todas(self):
        m = self.m
        for resultado in ((1, ""), (None, ""), (3, "openpyxl")):
            with self.subTest(resultado=resultado), mock.patch.object(m, "correr", return_value=resultado):
                self.assertEqual(m.faltan("py", "-I"), LOS_TRES)

    def test_con_todas_a_mano_no_falta_ninguna(self):
        with mock.patch.object(self.m, "correr", return_value=(0, "")):
            self.assertEqual(self.m.faltan("py", "-E"), [])

    def test_instalar_usa_hash_solo_ruedas_y_el_pip_del_equipo_aislado(self):
        m = self.m
        with mock.patch.object(m, "correr", return_value=(0, "ok")) as c:
            self.assertEqual(m.instalar(Path("venv/Scripts/python.exe")), ("listo", "ok"))
        comando = c.call_args[0][0]
        self.assertEqual(comando[:6], [sys.executable, "-I", "-m", "pip", "--python", str(Path("venv/Scripts/python.exe"))])
        for opcion in ("install", "--require-hashes", "--only-binary=:all:", "--no-input"):
            self.assertIn(opcion, comando)
        self.assertEqual(comando[comando.index("-r") + 1], str(self.raiz / "requirements.txt"))
        self.assertEqual(c.call_args[0][1], m.PLAZO_PIP)

    def test_si_el_pip_del_equipo_no_esta_donde_siempre_repite_sin_aislar(self):
        m = self.m
        respuestas = [(1, "No module named pip"), (0, "bien")]
        with mock.patch.object(m, "correr", side_effect=respuestas) as c:
            self.assertEqual(m.instalar("py")[0], "listo")
        # El segundo, sin la carpeta actual en sys.path: -E solo no la quita con `-m`.
        self.assertEqual([x[0][0][1:4] for x in c.call_args_list], [["-I", "-m", "pip"], ["-E", "-P", "-m"]])

    def test_otra_falla_de_pip_no_se_repite(self):
        m = self.m
        with mock.patch.object(m, "correr", side_effect=[(1, "sin conexion")]) as c:
            self.assertEqual(m.instalar("py")[0], "fallo")
        self.assertEqual(c.call_count, 1)

    def test_un_hash_distinto_se_dice_y_no_se_repite(self):
        m = self.m
        salida = "ERROR: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE."
        with mock.patch.object(m, "correr", side_effect=[(1, salida)]) as c:
            self.assertEqual(m.instalar("py")[0], "hash")
        self.assertEqual(c.call_count, 1)

    def test_el_log_no_guarda_la_clave_de_una_direccion(self):
        m = self.m
        m.anotar("Looking in indexes: https://usuario:clave-secreta@indice.example.invalid/simple")
        texto = (self.raiz / "logs" / "entorno.log").read_text(encoding="utf-8")
        self.assertNotIn("clave-secreta", texto)
        self.assertIn("indice.example.invalid", texto)

    def test_lo_que_se_le_muestra_a_la_persona_no_trae_claves(self):
        m = self.m
        salida = "uno\nERROR: no pude bajar https://u:clave-secreta@indice.example.invalid/x\n"
        self.assertNotIn("clave-secreta", " ".join(m.cola_de(salida)))

    def test_la_clave_con_arroba_y_los_parametros_secretos_tampoco_quedan(self):
        # Revisión de seguridad del encargo 84: `usuario:cl@ve@host` dejaba `ve@host`, y un `?token=` pasaba entero.
        m = self.m
        casos = ("https://usuario:cl@ve-secreto@indice.example.invalid/simple",
                 "https://indice.example.invalid/simple?token=valor-secreto&x=1",
                 "https://indice.example.invalid/simple?x=1&api_key=valor-secreto")
        for texto in casos:
            with self.subTest(texto=texto):
                limpio = m.sin_claves(texto)
                self.assertNotIn("secreto", limpio)
                self.assertNotIn("ve@", limpio)
                self.assertIn("indice.example.invalid", limpio)
        # Lo que no es una clave se deja: una arroba después de la barra, y un parámetro cualquiera.
        sin_clave = "https://indice.example.invalid/a@b?x=1&nombre=valor"
        self.assertEqual(m.sin_claves(sin_clave), sin_clave)

    def test_el_log_y_lo_que_se_muestra_no_traen_la_carpeta_del_usuario(self):
        # Revisión de seguridad del encargo 84: logs/entorno.log viaja a quien le dio el programa a la persona.
        m = self.m
        perfil = "C:\\Users\\Persona.Inventada"
        with mock.patch.dict(os.environ, {"USERPROFILE": perfil}), \
                mock.patch.object(os.path, "expanduser", return_value=perfil):
            m.anotar(f"Looking in links: {perfil}\\ruedas y {perfil.upper()}/otra y {perfil.replace(chr(92), '/')}/mas")
            texto = (self.raiz / "logs" / "entorno.log").read_text(encoding="utf-8")
            self.assertNotIn("inventada", texto.lower())
            self.assertIn("%USERPROFILE%\\ruedas", texto)
            self.assertIn("%USERPROFILE%/otra", texto)
            self.assertIn("%USERPROFILE%/mas", texto)
            self.assertNotIn("inventada", " ".join(m.cola_de(f"error en {perfil}\\x")).lower())
        self.assertEqual(m.sin_usuario("nada de usuarios aquí"), "nada de usuarios aquí")

    def test_el_log_se_recorta(self):
        m = self.m
        ruta = self.raiz / "logs" / "entorno.log"
        ruta.parent.mkdir()
        ruta.write_bytes(b"x" * (m.LARGO_MAXIMO_LOG + 10))
        m.anotar("nueva")
        self.assertLess(ruta.stat().st_size, m.LARGO_MAXIMO_LOG)
        self.assertTrue(ruta.read_text(encoding="utf-8").rstrip().endswith("nueva"))

    def test_la_huella_no_depende_del_fin_de_linea(self):
        m = self.m
        (self.raiz / "requirements.txt").write_bytes(b"a==1\nb==2\n")
        lf = m.huella_de_requisitos()
        (self.raiz / "requirements.txt").write_bytes(b"a==1\r\nb==2\r\n")
        self.assertEqual(m.huella_de_requisitos(), lf)
        (self.raiz / "requirements.txt").write_bytes(b"a==1\nb==3\n")
        self.assertNotEqual(m.huella_de_requisitos(), lf)

    def test_sin_requirements_la_huella_es_otra_cosa_y_no_falla(self):
        self.assertEqual(self.m.huella_de_requisitos(), "(falta)")

    def test_un_estado_roto_o_de_otra_forma_se_lee_como_vacio(self):
        m = self.m
        ruta = self.raiz / "logs" / ".entorno-estado.json"
        ruta.parent.mkdir()
        for contenido in (b"{", b"[1, 2]", b"\xff\xfe", b""):
            with self.subTest(contenido=contenido):
                ruta.write_bytes(contenido)
                self.assertEqual(m.leer_estado(), {})

    def test_el_estado_se_guarda_y_se_lee(self):
        m = self.m
        m.guardar_estado({"requisitos": "abc"})
        self.assertEqual(m.leer_estado(), {"requisitos": "abc"})
        self.assertEqual([p.name for p in (self.raiz / "logs").iterdir()], [".entorno-estado.json"])

    def test_reciente_pide_los_mismos_requisitos_y_un_plazo(self):
        m = self.m
        ahora = time.time()
        self.assertTrue(m.reciente({"requisitos": "h", "cuando": ahora - 10}, "h"))
        self.assertFalse(m.reciente({"requisitos": "h", "cuando": ahora - m.PAUSA_REINTENTO - 1}, "h"))
        self.assertFalse(m.reciente({"requisitos": "otro", "cuando": ahora - 10}, "h"))
        self.assertFalse(m.reciente({"requisitos": "h", "cuando": ahora + 3600}, "h"))
        for raro in (None, {}, {"requisitos": "h"}, {"requisitos": "h", "cuando": "ayer"}, "texto"):
            with self.subTest(raro=raro):
                self.assertFalse(m.reciente(raro, "h"))

    def test_que_python_cubre_requirements(self):
        m = self.m
        # (plataforma de sysconfig, versión, sin GIL) y lo que dice. Un Python x64 emulado en ARM64 da win-amd64.
        for argumentos, esperado in ((("win-amd64", (3, 13), False), None), (("win-amd64", (3, 11), False), None),
                                     (("win-amd64", (3, 14), False), None),
                                     (("win32", (3, 13), False), "es de 32 bits"),
                                     (("win-arm64", (3, 13), False), "es para win-arm64"),
                                     (("win-amd64", (3, 15), False), "es la 3.15"),
                                     (("win-amd64", (3, 10), False), "es la 3.10"),
                                     (("win-amd64", (4, 0), False), "es la 4.0"),
                                     (("win-amd64", (3, 14), True), "es la versión sin GIL"),
                                     (("win-amd64", (3, 13), True), "es la versión sin GIL")):
            with self.subTest(argumentos=argumentos):
                self.assertEqual(m.fuera_de_cobertura(*argumentos), esperado)

    def test_el_python_de_las_pruebas_esta_dentro_de_la_cobertura_que_se_declara(self):
        # Sin parámetros mira el Python que corre; este es de 64 bits, con GIL y no más nuevo que lo que dice
        # requirements.txt.
        m = self.m
        self.assertEqual(m.fuera_de_cobertura(), None if m.PYTHON_MINIMO <= sys.version_info[:2] <= m.PYTHON_MAXIMO
                         else f"es la {sys.version_info[0]}.{sys.version_info[1]}")

    def test_correr_cierra_los_hijos_del_proceso_cuando_vence_el_plazo(self):
        # `pip --python` corre pip otra vez con el Python del .venv, como hijo que hereda la salida. Si al vencer el plazo
        # solo se mata al de afuera, quien lee no vuelve hasta que el nieto termine (3,0 s sin nieto y 20,2 s con uno,
        # medido por la revisión de código). Se corre en un proceso aparte: aquí subprocess está trabado.
        codigo = ("import importlib.util, sys, time\n"
                  f"s = importlib.util.spec_from_file_location('p', {str(PREPARADOR)!r})\n"
                  "m = importlib.util.module_from_spec(s); s.loader.exec_module(m)\n"
                  "nieto = \"import subprocess, sys, time; subprocess.Popen([sys.executable, '-c', "
                  "'import time; time.sleep(25)']); time.sleep(25)\"\n"
                  "t = time.monotonic()\n"
                  "r = m.correr([sys.executable, '-c', nieto], 3)\n"
                  "print(r[0], round(time.monotonic() - t))\n")
        env = {k: v for k, v in os.environ.items() if k != soporte.LLAVE_ENTORNO}
        p = soporte._POPEN([sys.executable, "-I", "-c", codigo], cwd=str(PREPARADOR.parent), env=env,
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(cerrar, p)
        salida, error = p.communicate(timeout=120)
        resultado, segundos = salida.decode("utf-8", "replace").split()
        self.assertEqual((resultado, p.returncode), ("None", 0), error.decode("utf-8", "replace"))
        self.assertLess(int(segundos), 12)

    def test_un_proceso_que_termina_a_tiempo_devuelve_su_codigo_y_su_salida(self):
        codigo = ("import importlib.util, sys\n"
                  f"s = importlib.util.spec_from_file_location('p', {str(PREPARADOR)!r})\n"
                  "m = importlib.util.module_from_spec(s); s.loader.exec_module(m)\n"
                  "r = m.correr([sys.executable, '-c', 'import sys; print(\"hola\"); '\n"
                  "              'print(\"error\", file=sys.stderr); sys.exit(7)'], 30)\n"
                  "print(r[0], sorted(r[1].split()))\n")
        env = {k: v for k, v in os.environ.items() if k != soporte.LLAVE_ENTORNO}
        p = soporte._POPEN([sys.executable, "-I", "-c", codigo], cwd=str(PREPARADOR.parent), env=env,
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(cerrar, p)
        salida, error = p.communicate(timeout=60)
        self.assertEqual(salida.decode("utf-8", "replace").strip(), "7 ['error', 'hola']", error)

    def test_los_bat_piden_el_mismo_minimo_que_el_preparador(self):
        m = self.m
        for nombre, _ in test_actualizar.TestLosLanzadores.BATS:
            with self.subTest(bat=nombre):
                texto = (soporte.FUENTES / nombre).read_bytes().decode("ascii")
                self.assertIn(f"sys.version_info >= {m.PYTHON_MINIMO}", texto)
                self.assertIn(f"Python {m.PYTHON_MINIMO[0]}.{m.PYTHON_MINIMO[1]} o mas nuevo", texto)

    def test_el_nombre_de_las_librerias(self):
        m = self.m
        self.assertEqual(m.nombrar(["playwright"]), "«playwright»")
        self.assertEqual(m.nombrar(["playwright", "openpyxl"]), "«playwright» y «openpyxl»")
        self.assertEqual(m.nombrar(["a", "b", "c"]), "«a», «b» y «c»")


class TestEntornoPropio(unittest.TestCase):
    """entorno_propio() sobre carpetas de verdad, con crear_entorno() y el arranque del Python falsos."""

    def setUp(self):
        soporte.DISPAROS.clear()
        self.m = cargar_preparador()
        self.raiz = carpeta_corta("aq_env_")
        self.addCleanup(borrar, self.raiz)
        self.m.RAIZ = self.raiz
        self.venv = self.raiz / ".venv"
        self.creados = []
        self.dicho = []
        self.m.decir = self.dicho.append

        def crear(ruta, python):
            self.creados.append(ruta)
            ruta.mkdir()
            (ruta / self.m.MARCA).write_text("nuevo", encoding="utf-8")
            return python

        self.m.crear_entorno = crear

    def tearDown(self):
        self.assertEqual(soporte.DISPAROS, [])

    def python_falso(self, marca=True):
        self.venv.mkdir()
        (self.venv / "Scripts").mkdir()
        (self.venv / "Scripts" / "python.exe").write_bytes(b"MZ")
        (self.venv / "testigo.txt").write_text("de la persona", encoding="utf-8")
        if marca:
            (self.venv / self.m.MARCA).write_text("viejo", encoding="utf-8")

    def test_sin_venv_lo_crea(self):
        self.assertEqual(self.m.entorno_propio(), self.venv / "Scripts" / "python.exe")
        self.assertEqual(self.creados, [self.venv])

    def test_un_venv_que_arranca_se_usa_tal_cual(self):
        self.python_falso(marca=False)
        self.m.codigo_al_arrancar = lambda py: 0
        self.assertEqual(self.m.entorno_propio(), self.venv / "Scripts" / "python.exe")
        self.assertEqual((self.creados, (self.venv / "testigo.txt").exists()), ([], True))

    def test_uno_propio_cuyo_python_sale_con_error_se_rehace_sin_borrarlo_antes(self):
        self.python_falso()
        self.m.codigo_al_arrancar = lambda py: 106 if not self.creados else 0
        vistos = []
        borrar_apartados = self.m.borrar_apartados

        def espiar():
            vistos.append(sorted(p.name for p in (self.raiz / "logs").iterdir()))
            borrar_apartados()

        self.m.borrar_apartados = espiar
        self.assertEqual(self.m.entorno_propio(), self.venv / "Scripts" / "python.exe")
        # El viejo estaba apartado entero en logs/ cuando se creó el nuevo, y recién después se borró.
        self.assertEqual(len(vistos[0]), 1)
        self.assertTrue(vistos[0][0].startswith(self.m.APARTADO))
        self.assertEqual((self.creados, sorted(p.name for p in (self.raiz / "logs").iterdir()),
                          (self.venv / "testigo.txt").exists()), ([self.venv], [], False))

    def test_uno_ajeno_cuyo_python_no_arranca_no_se_toca(self):
        self.python_falso(marca=False)
        self.m.codigo_al_arrancar = lambda py: 106
        self.assertIsNone(self.m.entorno_propio())
        self.assertEqual((self.creados, (self.venv / "testigo.txt").exists(), (self.venv / "Scripts").is_dir()),
                         ([], True, True))
        self.assertEqual([p.name for p in (self.raiz / "logs").iterdir() if p.name.startswith(self.m.APARTADO)], [])
        self.assertTrue(any("no armó este programa" in x for x in self.dicho), self.dicho)

    def test_uno_propio_que_no_se_pudo_correr_no_se_rehace(self):
        # Retenido por un antivirus, o un equipo cargado que venció el plazo: no es un entorno roto.
        self.python_falso()
        self.m.codigo_al_arrancar = lambda py: None
        self.assertIsNone(self.m.entorno_propio())
        self.assertEqual((self.creados, (self.venv / "testigo.txt").exists()), ([], True))

    def test_uno_propio_a_medias_sin_python_se_rehace(self):
        # La creación se cortó después de la marca: no hay python.exe. El inicio siguiente lo rehace.
        self.venv.mkdir()
        (self.venv / self.m.MARCA).write_text("viejo", encoding="utf-8")
        self.assertEqual(self.m.entorno_propio(), self.venv / "Scripts" / "python.exe")
        self.assertEqual(self.creados, [self.venv])

    def test_una_union_con_ese_nombre_se_quita_sin_tocar_lo_de_adentro(self):
        # Rehacer o llenar una unión tocaría lo que hay del otro lado (venv --clear lo vaciaba, en LabelInspect).
        afuera = self.raiz / "afuera"
        afuera.mkdir()
        (afuera / "testigo.txt").write_text("no se toca", encoding="utf-8")
        codigo, _, error = soporte.hijo(["cmd", "/c", "mklink", "/J", str(self.venv), str(afuera)], self.raiz)
        self.assertEqual(codigo, 0, error)
        self.assertTrue(self.m.es_enlace(self.venv))
        self.assertEqual(self.m.entorno_propio(), self.venv / "Scripts" / "python.exe")
        self.assertEqual(((afuera / "testigo.txt").read_text(encoding="utf-8"), self.creados),
                         ("no se toca", [self.venv]))
        self.assertFalse(self.m.es_enlace(self.venv))

    def test_una_carpeta_comun_no_es_un_enlace(self):
        self.python_falso()
        self.assertFalse(self.m.es_enlace(self.venv))
        self.assertFalse(self.m.es_enlace(self.raiz / "no_existe"))

    def test_los_apartados_viejos_se_borran_aunque_tengan_archivos_de_solo_lectura(self):
        m = self.m
        viejo = self.raiz / "logs" / (m.APARTADO + "1")
        (viejo / "a").mkdir(parents=True)
        archivo = viejo / "a" / "solo_lectura.pack"
        archivo.write_bytes(b"x")
        os.chmod(archivo, 0o444)
        otro = self.raiz / "logs" / "entorno.log"
        otro.write_text("no se borra", encoding="utf-8")
        m.borrar_apartados()
        self.assertEqual(sorted(p.name for p in (self.raiz / "logs").iterdir()), ["entorno.log"])


class TestExclusion(unittest.TestCase):
    """Una sola ventana prepara el entorno a la vez: el doble clic de quien ve que tarda."""

    def test_la_segunda_ventana_espera_a_la_primera(self):
        m = cargar_preparador()
        raiz = carpeta_corta("aq_env_")
        self.addCleanup(borrar, raiz)
        m.RAIZ = raiz
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.CreateMutexW.restype = ctypes.c_void_p
        k32.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_wchar_p]
        k32.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        k32.WaitForSingleObject.restype = ctypes.c_uint32
        k32.ReleaseMutex.argtypes = [ctypes.c_void_p]
        k32.CloseHandle.argtypes = [ctypes.c_void_p]
        primera = k32.CreateMutexW(None, 0, m.nombre_del_mutex())
        self.assertEqual(k32.WaitForSingleObject(primera, 0), 0)                       # la primera ventana lo tiene
        self.addCleanup(k32.CloseHandle, primera)
        codigo = (f"import importlib.util, pathlib, sys\n"
                  f"sys.stdout.reconfigure(encoding='utf-8')\n"            # -I ignora PYTHONIOENCODING
                  f"s = importlib.util.spec_from_file_location('p', {str(PREPARADOR)!r})\n"
                  f"m = importlib.util.module_from_spec(s); s.loader.exec_module(m)\n"
                  f"m.RAIZ = pathlib.Path({str(raiz)!r})\n"
                  f"m.esperar_a_las_otras_ventanas()\n"
                  f"print('siguio', flush=True)\n")
        env = {k: v for k, v in os.environ.items() if k != soporte.LLAVE_ENTORNO}
        env["PYTHONIOENCODING"] = "utf-8"
        hijo = soporte._POPEN([sys.executable, "-I", "-c", codigo], cwd=str(raiz), env=env, stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(cerrar, hijo)
        lineas = []
        lector = threading.Thread(target=lambda: [lineas.append(x.decode("utf-8", "replace").strip())
                                                  for x in iter(hijo.stdout.readline, b"")], daemon=True)
        lector.start()
        for _ in range(100):                           # espera a que diga que espera
            if lineas:
                break
            time.sleep(0.1)
        time.sleep(1.0)
        self.assertEqual(len(lineas), 1, lineas)
        self.assertIn("Otra ventana de AQUASHIELD está preparando", lineas[0])      # y no siguió
        k32.ReleaseMutex(primera)
        lector.join(30)
        self.assertEqual(lineas[1:], ["siguio"])
        self.assertEqual(hijo.wait(30), 0)

    def test_dos_carpetas_no_se_esperan(self):
        a, b = cargar_preparador(), cargar_preparador()
        a.RAIZ, b.RAIZ = Path(r"C:\una\carpeta"), Path(r"C:\otra\carpeta")
        self.assertNotEqual(a.nombre_del_mutex(), b.nombre_del_mutex())
        b.RAIZ = Path(r"C:\UNA\Carpeta")
        self.assertEqual(a.nombre_del_mutex(), b.nombre_del_mutex())            # Windows no distingue mayúsculas


# --- El camino real: un proceso aparte, pip de verdad y un índice local con ruedas inventadas ---

def construir_rueda(carpeta, nombre, version, version_marcada):
    """Una rueda pura de Python con el módulo `nombre` (y `playwright.sync_api` para playwright), que dice en ES_FALSA
    de dónde vino. Devuelve (archivo, sha256)."""
    base = f"{nombre}-{version}"
    dist = f"{base}.dist-info"
    archivos = {f"{nombre}/__init__.py": f'ES_FALSA = "{version_marcada}"\n',
                f"{dist}/METADATA": f"Metadata-Version: 2.1\nName: {nombre}\nVersion: {version}\n",
                f"{dist}/WHEEL": "Wheel-Version: 1.0\nGenerator: prueba\nRoot-Is-Purelib: true\nTag: py3-none-any\n"}
    if nombre == "playwright":
        archivos["playwright/sync_api.py"] = f'ES_FALSA = "{version_marcada}"\n'
    archivos[f"{dist}/RECORD"] = "".join(f"{ruta},,\n" for ruta in archivos) + f"{dist}/RECORD,,\n"
    ruta = Path(carpeta) / f"{base}-py3-none-any.whl"
    with zipfile.ZipFile(ruta, "w", zipfile.ZIP_DEFLATED) as z:
        for relativa, texto in archivos.items():
            z.writestr(relativa, texto)
    return ruta, hashlib.sha256(ruta.read_bytes()).hexdigest()


def texto_de_requisitos(ruedas):
    """Un requirements.txt con la forma del de verdad: versión fija y un hash por rueda."""
    lineas = []
    for (nombre, version), (_, sha) in sorted(ruedas.items()):
        lineas += [f"{nombre}=={version} \\", f"    --hash=sha256:{sha}"]
    return "\n".join(lineas) + "\n"


class CajaConIndiceLocal(unittest.TestCase):
    """Una carpeta del programa inventada (preparar_entorno.py y su requirements.txt) y un índice local."""

    @classmethod
    def setUpClass(cls):
        cls.base = carpeta_corta("aq_env_")
        cls.ruedas_dir = cls.base / "ruedas"
        cls.ruedas_dir.mkdir()
        cls.ruedas = {}
        for nombre in ("playwright", "openpyxl", "holidays"):
            cls.ruedas[(nombre, "0.0.1")] = construir_rueda(cls.ruedas_dir, nombre, "0.0.1", "0.0.1")
        cls.ruedas[("holidays", "0.0.2")] = construir_rueda(cls.ruedas_dir, "holidays", "0.0.2", "0.0.2")

    @classmethod
    def tearDownClass(cls):
        borrar(cls.base)

    def setUp(self):
        soporte.DISPAROS.clear()
        self.n = getattr(CajaConIndiceLocal, "_n", 0)
        CajaConIndiceLocal._n = self.n + 1
        self.caja = self.base / f"caja{self.n}"
        self.caja.mkdir()
        (self.caja / "preparar_entorno.py").write_bytes(PREPARADOR.read_bytes())
        self.requisitos(("playwright", "0.0.1"), ("openpyxl", "0.0.1"), ("holidays", "0.0.1"))

    def tearDown(self):
        self.assertEqual(soporte.DISPAROS, [])

    def requisitos(self, *claves, texto=None):
        elegidas = {k: self.ruedas[k] for k in claves}
        (self.caja / "requirements.txt").write_bytes((texto or texto_de_requisitos(elegidas)).encode("ascii"))

    def env(self, indice=None):
        """Pip sin red: solo la carpeta de ruedas (o la que se diga), sin configuración ni caché del equipo."""
        return {"PIP_NO_INDEX": "1", "PIP_FIND_LINKS": str(indice or self.ruedas_dir), "PIP_CACHE_DIR":
                str(self.base / "cache"), "PIP_CONFIG_FILE": os.devnull, "PIP_DISABLE_PIP_VERSION_CHECK": "1"}

    def correr(self, indice=None, caja=None):
        caja = caja or self.caja
        codigo, salida, error = soporte.hijo([sys.executable, "-I", str(caja / "preparar_entorno.py")], caja, timeout=300,
                                             env_extra=self.env(indice))
        return codigo, salida, error

    def marca_del_venv(self, modulo="holidays", caja=None):
        """Lo que dice ES_FALSA del módulo, importado por el python del .venv (aislado), o None si no se importa."""
        py = (caja or self.caja) / ".venv" / "Scripts" / "python.exe"
        codigo, salida, _ = soporte.hijo([str(py), "-I", "-c", f"import {modulo}; print({modulo}.ES_FALSA)"],
                                         caja or self.caja)
        return salida.strip() if codigo == 0 else None

    def pasadas_de_pip(self):
        return (self.caja / "logs" / "entorno.log").read_text(encoding="utf-8").count("pip -I salió con")


class TestCaminoReal(CajaConIndiceLocal):
    def test_la_primera_vez_arma_el_venv_e_instala_con_hash(self):
        codigo, salida, error = self.correr()
        self.assertEqual((codigo, error), (0, ""), salida)
        self.assertIn("preparo las librerías", salida)
        self.assertEqual([self.marca_del_venv(m) for m in ("playwright.sync_api", "openpyxl", "holidays")],
                         ["0.0.1"] * 3)
        self.assertTrue((self.caja / ".venv" / ".aquashield-entorno").is_file())
        self.assertEqual(self.pasadas_de_pip(), 1)

    def test_la_segunda_vez_solo_comprueba_y_no_dice_nada(self):
        self.correr()
        codigo, salida, error = self.correr()
        self.assertEqual((codigo, salida, error), (0, "", ""))
        self.assertEqual(self.pasadas_de_pip(), 1)

    def test_si_cambian_los_requisitos_vuelve_a_instalar(self):
        self.correr()
        self.requisitos(("playwright", "0.0.1"), ("openpyxl", "0.0.1"), ("holidays", "0.0.2"))
        codigo, salida, _ = self.correr()
        self.assertEqual(codigo, 0, salida)
        self.assertEqual((self.marca_del_venv(), self.pasadas_de_pip()), ("0.0.2", 2))

    def test_un_hash_que_no_coincide_no_abre_aunque_el_equipo_tenga_todo(self):
        # sys.executable (el Python de las pruebas) trae las librerías de verdad: aun así no se abre con él.
        mala = texto_de_requisitos({k: self.ruedas[k] for k in (("playwright", "0.0.1"), ("openpyxl", "0.0.1"),
                                                                    ("holidays", "0.0.1"))})
        sha = self.ruedas[("holidays", "0.0.1")][1]
        self.requisitos(texto=mala.replace(sha, "0" * 64))
        codigo, salida, _ = self.correr()
        self.assertEqual(codigo, 11, salida)
        self.assertIn("no coincide con su hash", salida)
        self.assertIsNone(self.marca_del_venv("openpyxl"))

    def test_sin_red_y_con_el_python_del_equipo_completo_abre_con_ese(self):
        vacio = self.base / "vacio"
        vacio.mkdir(exist_ok=True)
        codigo, salida, _ = self.correr(indice=vacio)
        self.assertEqual(codigo, 10, salida)
        self.assertIn("No pude instalar las librerías", salida)
        self.assertIn("abro con el Python del equipo", salida)
        log = (self.caja / "logs" / "entorno.log").read_text(encoding="utf-8")
        self.assertIn("abro con el Python del equipo", log)

    def test_sin_red_el_segundo_inicio_no_vuelve_a_esperar_a_pip_si_todo_se_importa(self):
        # Primero el entorno completo; después una versión nueva en requirements.txt que no se puede bajar.
        self.correr()
        self.requisitos(("playwright", "0.0.1"), ("openpyxl", "0.0.1"), ("holidays", "0.0.2"))
        vacio = self.base / "vacio"
        vacio.mkdir(exist_ok=True)
        for esperado in (1, 1):
            codigo, _, _ = self.correr(indice=vacio)
            self.assertEqual(codigo, 0)
            self.assertEqual(self.pasadas_de_pip(), 1 + esperado)

    def test_sin_red_y_con_el_python_del_equipo_completo_el_segundo_inicio_no_espera_a_pip(self):
        # Sin red, el primer inicio prueba pip y abre con el Python del equipo (10); el segundo, con los mismos
        # requisitos, ya no espera a pip otra vez (medido por la revisión de código: unos 65 s en cada inicio).
        vacio = self.base / "vacio"
        vacio.mkdir(exist_ok=True)
        codigos = [self.correr(indice=vacio)[0] for _ in range(2)]
        self.assertEqual((codigos, self.pasadas_de_pip()), ([10, 10], 1))

    def test_un_venv_cuyo_python_ya_no_existe_se_rehace(self):
        # TI cambió el Python del equipo: el python.exe del .venv arranca y no encuentra su intérprete.
        self.correr()
        cfg = self.caja / ".venv" / "pyvenv.cfg"
        cfg.write_text(re.sub(r"(?m)^home = .*$", r"home = C:\\no\\existe", cfg.read_text(encoding="utf-8")),
                       encoding="utf-8")
        (self.caja / ".venv" / "testigo.txt").write_text("del venv viejo", encoding="utf-8")
        codigo, salida, error = self.correr()
        self.assertEqual((codigo, error), (0, ""), salida)
        self.assertEqual((self.marca_del_venv(), (self.caja / ".venv" / "testigo.txt").exists()), ("0.0.1", False))
        self.assertEqual([p.name for p in (self.caja / "logs").iterdir() if p.name.startswith(".venv-apartado")], [])

    def test_un_venv_ajeno_que_no_arranca_no_se_toca_y_se_abre_con_el_del_equipo(self):
        (self.caja / ".venv").mkdir()
        (self.caja / ".venv" / "testigo.txt").write_text("de la persona", encoding="utf-8")
        codigo, salida, _ = self.correr()
        self.assertEqual(codigo, 10, salida)
        self.assertEqual((self.caja / ".venv" / "testigo.txt").read_text(encoding="utf-8"), "de la persona")
        self.assertFalse((self.caja / ".venv" / "Scripts").exists())

    def test_una_union_con_el_nombre_del_venv_no_deja_instalar_en_lo_de_afuera(self):
        afuera = self.base / f"afuera{self.n}"
        afuera.mkdir()
        (afuera / "testigo.txt").write_text("no se toca", encoding="utf-8")
        codigo, _, error = soporte.hijo(["cmd", "/c", "mklink", "/J", str(self.caja / ".venv"), str(afuera)],
                                        self.caja)
        self.assertEqual(codigo, 0, error)
        codigo, salida, _ = self.correr()
        self.assertEqual(codigo, 0, salida)
        self.assertEqual((sorted(p.name for p in afuera.iterdir()), self.marca_del_venv()), (["testigo.txt"], "0.0.1"))

    def test_dos_ventanas_a_la_vez_dejan_un_solo_entorno(self):
        # El doble clic de quien ve que tarda: la segunda espera a la primera y encuentra todo hecho.
        env = {k: v for k, v in os.environ.items() if k != soporte.LLAVE_ENTORNO}
        env.update(self.env(), PYTHONIOENCODING="utf-8")
        procesos = [soporte._POPEN([sys.executable, "-I", str(self.caja / "preparar_entorno.py")], cwd=str(self.caja),
                                   env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE) for _ in range(2)]
        for p in procesos:
            self.addCleanup(cerrar, p)
        resultados = []
        for p in procesos:
            salida, _ = p.communicate(timeout=300)
            resultados.append((p.returncode, salida.decode("utf-8", "replace")))
        self.assertEqual([r[0] for r in resultados], [0, 0], resultados)
        self.assertEqual((self.pasadas_de_pip(), self.marca_del_venv()), (1, "0.0.1"))


# --- Los .bat, de punta a punta con el entorno propio ---

def sin_el_path_del_venv(bat):
    """El mismo .bat sin poner la carpeta Scripts del .venv primero en el PATH (el control)."""
    linea = r'    set "PATH=%~dp0.venv\Scripts;%PATH:"=%"' + "\n"
    sin = bat.replace(linea, "    echo.\n", 1)
    assert sin != bat, "no encontré la línea del PATH en el .bat"
    return sin


class TestElBatAbreConElEntornoPropio(CajaConIndiceLocal):
    SUSTITUTO = ("import pathlib, sys\n"
                 "try:\n"
                 "    import playwright.sync_api as p\n"
                 "    fake = p.ES_FALSA\n"
                 "except Exception:\n"
                 "    fake = 'no-importa'\n"
                 "(pathlib.Path(__file__).resolve().parent / 'marca.txt').write_text(sys.executable + '\\n' + fake, encoding='utf-8')\n")

    def test_el_programa_abre_con_el_python_del_venv_con_sus_librerias(self):
        # El camino real: cmd corre el .bat en una carpeta nueva, con el Python del PATH, que no trae las librerías;
        # el preparador arma el .venv e instala (aquí, de un índice local); y pythonw sale del .venv. Control: el mismo
        # .bat sin poner el .venv en el PATH abre con el Python del equipo, sin las librerías.
        python = shutil.which("python")
        if python is None or correr_cmd([python, "-c", "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"],
                                        self.base, {})[0] != 0:
            self.skipTest("no hay un python 3.11 o más nuevo en el PATH")
        env = dict(self.env(), GIT_CEILING_DIRECTORIES=str(self.base))
        # Una entrada del PATH entre comillas y con un paréntesis en el nombre, como las que dejan algunos instaladores:
        # cmd expande %PATH% antes de correr el bloque, y sin quitarle las comillas el «)» cerraba el bloque entero y el
        # .bat salía sin abrir (medido por la revisión de código del encargo 84; el .bat anterior abría con ese PATH).
        entrada = '"C:\\Program Files (x86)\\NadaAQ";'
        con_comillas = dict(env, PATH=entrada + os.environ["PATH"])
        # (.bat, con el PATH del .venv, nombre de la carpeta, entorno). La carpeta con espacios, paréntesis y una «ñ», como
        # el escritorio de una persona o «Program Files (x86)»: dentro del bloque, un «)» sin comillas lo cerraría antes.
        casos = ((0, True, None, env), (1, True, None, env), (0, False, None, env),
                 (0, True, "AQ (prueba) ñandú", env), (0, True, None, con_comillas), (1, True, None, con_comillas))
        for k, con_path, nombre_carpeta, entorno in casos:
            nombre, programa = test_actualizar.TestLosLanzadores.BATS[k]
            bat = (soporte.FUENTES / nombre).read_bytes().decode("ascii")
            with self.subTest(bat=nombre, con_path_del_venv=con_path, carpeta=nombre_carpeta,
                              path_con_comillas=entorno is con_comillas):
                carpeta = self.base / (nombre_carpeta or f"b{len(list(self.base.glob('b*')))}")
                carpeta.mkdir()
                for archivo in ("actualizar.py", "preparar_entorno.py"):
                    shutil.copyfile(soporte.FUENTES / archivo, carpeta / archivo)
                shutil.copyfile(self.caja / "requirements.txt", carpeta / "requirements.txt")
                (carpeta / programa).write_bytes(self.SUSTITUTO.encode())
                (carpeta / nombre).write_bytes((bat if con_path else sin_el_path_del_venv(bat)).encode("ascii"))
                correr_cmd(["cmd", "/d", "/c", str(carpeta / nombre)], carpeta, entorno, timeout=300)
                marca = carpeta / "marca.txt"
                for _ in range(120):                          # pythonw corre aparte: se espera su marca
                    if marca.exists():
                        break
                    time.sleep(0.5)
                ejecutable, fake = marca.read_text(encoding="utf-8").split("\n")
                # El temporal viene en forma 8.3 (la carpeta del usuario recortada) y otras herramientas imprimen la larga: se comparan
                # las dos resueltas (Entorno de ~/.claude/CLAUDE.md).
                esperado = os.path.realpath(carpeta / ".venv" / "Scripts" / "pythonw.exe")
                if con_path:
                    self.assertEqual((os.path.normcase(os.path.realpath(ejecutable)), fake),
                                     (os.path.normcase(esperado), "0.0.1"))
                else:
                    self.assertNotIn(".venv", ejecutable.lower())
                    self.assertEqual(fake, "no-importa")


# --- requirements.txt ---

class TestRequirements(unittest.TestCase):
    def lineas(self):
        return REQUISITOS.read_bytes().decode("ascii").split("\n")

    def paquetes(self):
        """{nombre: [hashes]} de lo que dice el archivo."""
        texto = "\n".join(x for x in self.lineas() if not x.lstrip().startswith("#"))
        unidos = re.sub(r"\\\n", " ", texto)
        salida = {}
        for linea in unidos.split("\n"):
            if linea.strip():
                nombre = re.match(r"([A-Za-z0-9._-]+)==", linea.strip())
                salida[nombre.group(1).lower()] = re.findall(r"--hash=sha256:([0-9a-f]{64})", linea)
        return salida

    def test_es_ascii_con_fin_de_linea_lf(self):
        datos = REQUISITOS.read_bytes()
        self.assertTrue(all(c < 128 for c in datos), "pip lo lee con la página de códigos del equipo")
        self.assertNotIn(b"\r", datos)

    def test_cada_linea_es_un_comentario_una_version_fija_o_un_hash(self):
        malas = [x for x in self.lineas()
                 if x.strip() and not re.fullmatch(r"#.*|[A-Za-z0-9._-]+==[A-Za-z0-9._!+]+ \\|"
                                                   r"    --hash=sha256:[0-9a-f]{64}( \\)?|    #.*", x)]
        self.assertEqual(malas, [])

    def test_cada_paquete_tiene_hash_y_ninguno_viene_de_una_direccion(self):
        paquetes = self.paquetes()
        self.assertGreaterEqual(len(paquetes), 3)
        for nombre, hashes in paquetes.items():
            with self.subTest(paquete=nombre):
                self.assertGreaterEqual(len(hashes), 1)
                self.assertEqual(len(hashes), len(set(hashes)))
        texto = REQUISITOS.read_bytes().decode("ascii")
        self.assertNotRegex(texto, r"(?m)^\s*(-e|git\+|https?://|\.|/)")

    def test_trae_lo_que_el_preparador_exige_para_abrir(self):
        m = cargar_preparador()
        paquetes = self.paquetes()
        for modulo in m.OBLIGATORIAS + m.OPCIONALES:
            with self.subTest(modulo=modulo):
                self.assertIn(modulo.split(".")[0], paquetes)
        # playwright pide estas dos: pip, en modo con hash, exige todas las dependencias en el archivo.
        for dependencia in ("greenlet", "pyee", "typing-extensions", "et-xmlfile", "python-dateutil", "six"):
            with self.subTest(dependencia=dependencia):
                self.assertIn(dependencia, paquetes)

    def test_todo_lo_que_el_programa_importa_de_afuera_esta_en_el_archivo(self):
        # Una librería nueva en AQUASHIELD.py sin su línea en requirements.txt se vería recién en el equipo de un
        # colega. Las dos que no están son del solucionador del puzzle de COSCO (import perezoso, dentro de una
        # función): si faltan, el programa cae a la pausa para que la persona lo resuelva (CICLO-entorno-propio.md).
        arbol = ast.parse((soporte.FUENTES / "AQUASHIELD.py").read_text(encoding="utf-8"))
        importados = set()
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Import):
                importados |= {a.name.split(".")[0] for a in nodo.names}
            elif isinstance(nodo, ast.ImportFrom) and nodo.level == 0 and nodo.module:
                importados.add(nodo.module.split(".")[0])
        locales = {"AQUASHIELD", "actualizar", "preparar_entorno"}
        de_afuera = {n for n in importados if n not in sys.stdlib_module_names and n not in locales}
        self.assertEqual(sorted(de_afuera - set(self.paquetes())), ["cv2", "numpy"])
        self.assertEqual(sorted(de_afuera & set(self.paquetes())), ["holidays", "openpyxl", "playwright"])

    def test_el_gitignore_versiona_los_dos_archivos(self):
        lineas = (soporte.FUENTES / ".gitignore").read_text(encoding="utf-8").splitlines()
        for nombre in ("!/preparar_entorno.py", "!/requirements.txt"):
            with self.subTest(nombre=nombre):
                self.assertIn(nombre, lineas)


if __name__ == "__main__":
    unittest.main()
