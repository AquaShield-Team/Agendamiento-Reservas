# -*- coding: utf-8 -*-
"""Panel web (lanzar_web) en un puerto propio, dentro de la sandbox.

Las navieras se reemplazan por login y reservador FALSOS y Playwright por uno
que solo registra: ninguna prueba abre un navegador ni toca un portal. Lo que
se fotografía es la orquestación: rutas, credenciales, planilla subida,
corridas por hoja y por consolidado, pausa, detener, modo login, y el arranque
(cierre a la fuerza del que ocupe el puerto; relevo de una instancia previa).
"""
import ast
import contextlib
import http.server
import io
import json
import re
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from io import BytesIO
from pathlib import Path
from unittest import mock
from urllib.parse import quote

import openpyxl

import sinteticos
import soporte

TESTS = Path(__file__).resolve().parent
RUTAS_JS = ["/api/apagar", "/api/config", "/api/continuar", "/api/correr", "/api/credenciales", "/api/descargar",
            "/api/detener", "/api/estado", "/api/filas", "/api/login", "/api/planilla"]


def planilla_bytes(sb):
    ruta = sinteticos.crear_planilla(sb / "_planilla_para_subir.xlsx")
    datos = ruta.read_bytes()
    ruta.unlink()
    return datos


Navieras = soporte.Navieras


class PanelBase(soporte.CasoAQ):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.srv = soporte.Servidor(cls.mod).iniciar()
        cls.xlsx = planilla_bytes(cls.sb)

    @classmethod
    def tearDownClass(cls):
        cls.srv.apagar()

    def subir(self, nombre="Prueba.xlsx"):
        return self.srv.json(f"/api/planilla?nombre={quote(nombre)}", self.xlsx)

    def correr(self, hoja, filas, usuario="op_prueba"):
        st, r = self.srv.json("/api/correr", {"hoja": hoja, "usuario": usuario, "filas": filas})
        self.assertEqual((st, r), (200, {"ok": True}))
        return self.srv.esperar_fin()


class TestPanelRutas(PanelBase):
    def test_recursos_del_panel(self):
        for ruta, tipo, marca in (("/", "text/html", b"<html"), ("/app.js", "application/javascript", b"fetch"),
                                  ("/estilo.css", "text/css", b"{"), ("/fuentes.css", "text/css", b"@font-face")):
            st, cab, cuerpo = self.srv.completo(ruta)
            with self.subTest(ruta=ruta):
                self.assertEqual(st, 200)
                self.assertTrue(cab["Content-Type"].startswith(tipo))
                self.assertIn(marca, cuerpo)
        self.assertEqual(self.srv.get("/api/no-existe"), (404, b"no existe"))
        self.assertEqual(self.srv.post("/api/no-existe"), (404, b"no existe"))

    def test_config_del_panel(self):
        st, cfg = self.srv.json("/api/config")
        self.assertEqual(st, 200)
        self.assertIs(cfg["modo_emision"], False)
        self.assertEqual(cfg["version"], self.mod.VERSION)
        self.assertEqual(cfg["usuarios"], ["op_prueba", "op_vacio"])
        self.assertEqual([(n["clave"], n["reserva"]) for n in cfg["navieras"]],
                         [(k, True) for k in sinteticos.NAVIERAS])

    def test_config_ausente_da_500(self):
        ruta = self.sb / "config.json"
        original = ruta.read_bytes()
        ruta.unlink()
        try:
            st, cuerpo = self.srv.get("/api/config")
        finally:
            ruta.write_bytes(original)
        self.assertEqual(st, 500)
        self.assertIn(b"No existe config.json (copia config.example.json", cuerpo)

    def test_llave_invalida_se_avisa_en_pantalla(self):
        ruta = self.sb / "config.json"
        original = ruta.read_bytes()
        cfg = json.loads(original)
        cfg["opciones"]["emitir_reservas"] = "true"            # «true» entre comillas: texto, no booleano
        soporte.escribir_json(ruta, cfg)
        try:
            _, antes = self.srv.json("/api/estado")
            st, config = self.srv.json("/api/config")
            _, despues = self.srv.json(f"/api/estado?desde={antes['cursor']}")
        finally:
            ruta.write_bytes(original)
        self.assertEqual((st, config["modo_emision"]), (200, False))
        self.assertEqual(len(despues["lineas"]), 1)
        self.assertIn('«emitir_reservas» vale "true" y solo se abre con true (sin comillas)', despues["lineas"][0])

    def test_rutas_del_js_existen_en_el_servidor(self):
        fuente = Path(self.mod.__file__).read_text(encoding="utf-8")
        js = set(re.findall(r"""['"`](/api/[a-z]+)""", self.mod.JS_INDEX))
        tree = ast.parse(fuente)
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "lanzar_web")
        atendidas = set()
        for n in ast.walk(f):
            if isinstance(n, ast.Compare) and ast.unparse(n.left) == "u.path":
                for c in ast.walk(n.comparators[0]):
                    if isinstance(c, ast.Constant) and isinstance(c.value, str):
                        atendidas.add(c.value)
        self.assertEqual(sorted(js), RUTAS_JS)
        self.assertEqual(sorted(atendidas - {"/", "/index.html", "/app.js", "/estilo.css", "/fuentes.css"}),
                         sorted(RUTAS_JS + ["/api/salir", "/api/shutdown"]))


class TestPanelCredenciales(PanelBase):
    def tearDown(self):
        soporte.escribir_json(self.sb / "config.json", sinteticos.config())
        super().tearDown()

    def test_credenciales_nunca_devuelven_la_clave(self):
        st, cuerpo = self.srv.get("/api/credenciales?usuario=op_prueba")
        self.assertEqual(st, 200)
        self.assertNotIn(b"clave-falsa", cuerpo)
        r = json.loads(cuerpo)
        for n in r["navieras"]:
            self.assertEqual(set(n), {"clave", "nombre", "usuario", "contrato", "tiene_clave"})
            self.assertTrue(n["tiene_clave"])
            self.assertEqual(n["usuario"], f"usuario.{n['clave']}@ejemplo.invalid")
        _, vacio = self.srv.json("/api/credenciales?usuario=op_vacio")
        self.assertEqual({n["tiene_clave"] for n in vacio["navieras"]}, {False})

    def test_guardar_credenciales(self):
        leer = lambda: json.loads((self.sb / "config.json").read_text(encoding="utf-8"))["usuarios"]["op_nuevo"]
        st, r = self.srv.json("/api/credenciales", {"usuario": "op_nuevo", "descripcion": "Nuevo",
                                                    "navieras": {"one": {"usuario": "u1", "clave": "c1", "contrato": "k1"}}})
        self.assertEqual((st, r["ok"], r["operadores"]), (200, True, ["op_prueba", "op_vacio", "op_nuevo"]))
        op = leer()
        self.assertEqual(sorted(op), sorted(["descripcion"] + list(sinteticos.NAVIERAS)))   # nace con las seis
        self.assertEqual(op["one"], {"usuario": "u1", "clave": "c1", "contrato": "k1"})
        self.assertEqual(op["msc"], {"usuario": "", "clave": "", "contrato": ""})
        # clave ausente: se conserva la que había
        self.srv.json("/api/credenciales", {"usuario": "op_nuevo", "navieras": {"one": {"usuario": "u2", "contrato": "k1"}}})
        self.assertEqual(leer()["one"], {"usuario": "u2", "clave": "c1", "contrato": "k1"})
        # clave "" : se borra
        self.srv.json("/api/credenciales", {"usuario": "op_nuevo", "navieras": {"one": {"usuario": "u2", "clave": ""}}})
        self.assertEqual(leer()["one"]["clave"], "")
        self.assertFalse((self.sb / "config.json.tmp").exists())
        self.assertEqual(self.srv.json("/api/credenciales", {"navieras": {}}),
                         (400, {"error": "falta el nombre del operador"}))

    # --- El reemplazo de config.json que Windows niega un instante (CICLO-cola-cuatro-items.md) ---
    def negar_reemplazo(self, veces):
        """os.replace niega el reemplazo las primeras 'veces' veces, como Windows cuando otro proceso (el antivirus) tiene
        abierto el archivo un instante; después reemplaza de verdad. Devuelve el parche y la lista de intentos."""
        real, intentos = self.mod._os.replace, []

        def replace(origen, destino):
            intentos.append(Path(destino).name)
            if len(intentos) <= veces:
                raise PermissionError(13, "Acceso denegado (sintético)")
            return real(origen, destino)
        return mock.patch.object(self.mod._os, "replace", replace), intentos

    def test_guardar_reintenta_si_windows_niega_el_reemplazo(self):
        # Medido: 47 de 900 guardados seguidos respondían 500 «[WinError 5] Acceso denegado» al reemplazar config.json,
        # y hasta 45f2171 test_guardar_credenciales caía así en 1 de 12 suites completas.
        parche, intentos = self.negar_reemplazo(3)
        with parche:
            st, r = self.srv.json("/api/credenciales", {"usuario": "op_nuevo",
                                                        "navieras": {"one": {"usuario": "u9", "clave": "c9"}}})
        self.assertEqual((st, r["ok"]), (200, True))
        self.assertEqual(intentos, ["config.json"] * 4)
        cfg = json.loads((self.sb / "config.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["usuarios"]["op_nuevo"]["one"], {"usuario": "u9", "clave": "c9", "contrato": ""})
        self.assertFalse((self.sb / "config.json.tmp").exists())

    def test_guardar_se_rinde_si_el_reemplazo_sigue_negado(self):
        antes = (self.sb / "config.json").read_bytes()
        self.addCleanup(lambda: (self.sb / "config.json.tmp").unlink(missing_ok=True))
        parche, intentos = self.negar_reemplazo(10 ** 6)
        with parche:
            st, cuerpo = self.srv.pedir("/api/credenciales", {"usuario": "op_nuevo", "navieras": {}})
        self.assertEqual(st, 500)
        self.assertIn("Acceso denegado", cuerpo.decode("utf-8"))            # el panel muestra el error
        self.assertEqual(len(intentos), 20)
        self.assertEqual((self.sb / "config.json").read_bytes(), antes)     # config.json queda como estaba

    def test_reemplazar_solo_reintenta_el_acceso_denegado(self):
        llamadas = []

        def replace(origen, destino):
            llamadas.append(destino)
            raise FileNotFoundError(2, "no está (sintético)")
        with mock.patch.object(self.mod._os, "replace", replace):
            with self.assertRaises(FileNotFoundError):
                self.mod._reemplazar("a.tmp", "a", pausa=0)
        self.assertEqual(llamadas, ["a"])                                   # otro error sube de inmediato

    # --- Los dos paneles escriben config.json con el mismo ayudante atómico (CICLO-cola-siete-items.md) ---
    def test_escribir_config_es_atomica_y_reintenta(self):
        ruta = self.sb / "config.json"
        cfg = {"usuarios": {"op_ñandú": {"descripcion": "Operación de prueba"}}}
        parche, intentos = self.negar_reemplazo(2)
        with parche:
            self.assertEqual(self.mod._escribir_config(cfg, ruta), 2)                   # reintentó dos veces
        self.assertEqual(intentos, ["config.json"] * 3)
        # El mismo formato que escribían los dos paneles: UTF-8 sin escapar, con sangría de 2.
        self.assertEqual(ruta.read_text(encoding="utf-8"), json.dumps(cfg, ensure_ascii=False, indent=2))
        self.assertFalse((self.sb / "config.json.tmp").exists())

    def test_escribir_config_no_toca_el_archivo_si_el_reemplazo_sigue_negado(self):
        ruta = self.sb / "config.json"
        antes = ruta.read_bytes()
        self.addCleanup(lambda: (self.sb / "config.json.tmp").unlink(missing_ok=True))
        parche, intentos = self.negar_reemplazo(10 ** 6)
        with parche, self.assertRaises(PermissionError):
            self.mod._escribir_config({"usuarios": {}}, ruta)
        self.assertEqual(len(intentos), 20)
        self.assertEqual(ruta.read_bytes(), antes)                                     # ni truncado ni a medias

    def test_los_dos_paneles_escriben_config_con_el_mismo_ayudante(self):
        # Hasta 0af2d5b, el panel de escritorio abría config.json con open(w), que lo trunca al abrir: un fallo a mitad
        # lo dejaba vacío, y con él las credenciales de los portales.
        src = Path(self.mod.__file__).read_text(encoding="utf-8")
        arbol = ast.parse(src)
        padres = {}
        for n in ast.walk(arbol):
            for h in ast.iter_child_nodes(n):
                padres[h] = n

        def funcion(n):
            while n in padres and not isinstance(n, ast.FunctionDef):
                n = padres[n]
            return n.name
        llamadas = [c for c in ast.walk(arbol) if isinstance(c, ast.Call) and getattr(c.func, "id", "") == "_escribir_config"]
        self.assertEqual(sorted((funcion(c), ast.unparse(c)) for c in llamadas),
                         [("do_POST", "_escribir_config(cfg, BASE / 'config.json')"),
                          ("guardar", "_escribir_config(self.cfg, BASE / 'config.json')")])
        # Nadie más abre config.json para escribir, ni escribe el temporal por su cuenta.
        escrituras = [ast.unparse(c) for c in ast.walk(arbol) if isinstance(c, ast.Call)
                      and getattr(c.func, "id", "") == "open" and len(c.args) > 1
                      and isinstance(c.args[1], ast.Constant) and "w" in str(c.args[1].value)]
        self.assertEqual([e for e in escrituras if "config" in e or e.startswith("open(tmp")],
                         ["open(tmp, 'w', encoding='utf-8')"])
        self.assertEqual(src.count('".json.tmp"'), 1)


class TestPanelPlanilla(PanelBase):
    def test_planilla_subida_va_al_temporal_con_nombre_fijo(self):
        st, r = self.subir()
        self.assertEqual(st, 200)
        self.assertEqual(r["nombre"], "Prueba.xlsx")
        self.assertEqual([(h["hoja"], h["filas"], h["reservador"]) for h in r["hojas"]],
                         [("CONSOLIDADO", 7, True), ("ONE", 5, True), ("MSC", 3, True), ("CMA-CGM", 3, True),
                          ("COSCO", 2, True), ("HYUNDAI", 2, True), ("MAERSK", 2, True)])
        destino = Path(tempfile.gettempdir()) / "aquashield_planilla.xlsx"
        self.assertTrue(self.sb.resolve() in destino.resolve().parents, "el temporal no está en la sandbox")
        self.assertEqual(destino.read_bytes(), self.xlsx)

    def test_filas_de_una_hoja(self):
        self.subir()
        _, r = self.srv.json("/api/filas?hoja=ONE")
        self.assertEqual([f["fila"] for f in r["filas"]], [5, 6, 7, 9, 10])
        _, r = self.srv.json("/api/filas?hoja=NO-EXISTE")
        self.assertEqual(r, {"filas": []})

    def test_descarga_de_resultados(self):
        self.subir("Mi Planilla.xlsx")
        temporal = Path(tempfile.gettempdir()) / "aquashield_planilla.xlsx"
        antes = temporal.read_bytes()
        with self.mod._LOCK:
            self.mod._WEB.update({"hoja": "ONE", "resultados": {"5": {"estado": "EMITIDA", "booking": "BKGFALSO03"}}})
        st, cab, cuerpo = self.srv.completo("/api/descargar")
        self.assertEqual(st, 200)
        self.assertRegex(cab["Content-Disposition"],
                         r'^attachment; filename="Mi Planilla - resultados \d\d-\d\d_\d{4}\.xlsx"$')
        ws = openpyxl.load_workbook(BytesIO(cuerpo))["ONE"]
        self.assertEqual((ws["H5"].value, ws["I5"].value), ("EMITIDA", "BKGFALSO03"))
        self.assertEqual(temporal.read_bytes(), antes, "la descarga tocó la planilla subida")

    def test_numero_de_reserva_igual_en_el_panel_y_en_la_planilla(self):
        # La columna «N° de reserva emitida» dice lo mismo en el panel (n_reserva de /api/estado) y en la planilla: el
        # número de la EMITIDA; «lista para emitir» en la OK-EJEMPLO, que no se emitió; nada en las demás. Hasta el
        # encargo 34, el panel decía «✓ Confirmada» en la OK-EJEMPLO y la planilla dejaba la celda vacía
        # (CICLO-one-y-maersk-eligen-la-nave.md).
        self.subir()
        resultados = {"5": {"estado": "EMITIDA", "detalle": "ONE emitida con éxito (Booking: BKGFALSO11)", "booking": ""},
                      "6": {"estado": "OK-EJEMPLO", "detalle": "armada hasta Review; SIN emitir", "booking": ""},
                      "7": {"estado": "NO ENVIADA", "detalle": "ONE: no elegí salida", "booking": ""}}
        with self.mod._LOCK:
            self.mod._WEB.update({"hoja": "ONE", "resultados": resultados})
        try:
            _, _, cuerpo = self.srv.completo("/api/descargar")
            _, estado = self.srv.json("/api/estado")
        finally:
            with self.mod._LOCK:
                self.mod._WEB.update({"resultados": {}})
        ws = openpyxl.load_workbook(BytesIO(cuerpo))["ONE"]
        planilla = {f: ws[f"I{f}"].value or "" for f in resultados}
        panel = {f: estado["resultados"][f]["n_reserva"] for f in resultados}
        self.assertEqual(planilla, {"5": "BKGFALSO11", "6": "lista para emitir", "7": ""})
        self.assertEqual(panel, planilla)
        self.assertEqual(self.mod.LISTA_PARA_EMITIR, "lista para emitir")


    def test_descarga_avisa_en_pantalla_y_en_el_log(self):
        # De punta a punta: lo que la descarga no pudo escribir (la fila 1 es un título combinado)
        # sale en el registro que muestra el panel y en el log.txt de la corrida.
        self.subir()
        carpeta = self.sb / "logs" / "web_one_prueba_descarga"
        _, antes = self.srv.json("/api/estado")
        with self.mod._LOCK:
            self.mod._WEB.update({"hoja": "ONE", "carpeta": str(carpeta),
                                  "resultados": {"1": {"estado": "EMITIDA", "detalle": "x", "booking": "BKGFALSO07"}}})
        try:
            st, _, _ = self.srv.completo("/api/descargar")
            _, despues = self.srv.json(f"/api/estado?desde={antes['cursor']}")
        finally:
            with self.mod._LOCK:
                self.mod._WEB.update({"carpeta": "", "resultados": {}})
        self.assertEqual(st, 200)
        log = (carpeta / "log.txt").read_text(encoding="utf-8")
        for texto in ("· ⚠ No pude escribir en la planilla descargada el resultado de la fila 1: error inesperado "
                      "(AttributeError: ", "Anótalo a mano: EMITIDA · BKGFALSO07 · x",
                      "· ⚠ 1 resultado(s) no quedaron en la planilla descargada (filas 1); cada uno está arriba en este log."):
            with self.subTest(texto=texto[:40]):
                self.assertIn(texto, log)
                self.assertTrue(any(texto in l for l in despues["lineas"]), despues["lineas"])


class TestPanelSinPlanilla(PanelBase):
    def test_descarga_sin_planilla(self):
        self.assertEqual(self.srv.get("/api/descargar"), (400, "No hay planilla cargada.".encode("utf-8")))
        self.assertEqual(self.srv.json("/api/filas?hoja=ONE"), (200, {"filas": []}))


class TestPanelCorridas(PanelBase):
    def setUp(self):
        super().setUp()
        self.subir()

    def test_correr_rechazos(self):
        self.assertEqual(self.srv.json("/api/correr", {"hoja": "OTRA", "filas": [5]}),
                         (400, {"error": "'OTRA' no tiene automatización"}))
        with self.mod._LOCK:
            self.mod._WEB["corriendo"] = True
        try:
            self.assertEqual(self.srv.json("/api/correr", {"hoja": "ONE", "filas": [5]}),
                             (409, {"error": "ya hay una corrida en curso"}))
        finally:
            with self.mod._LOCK:
                self.mod._WEB["corriendo"] = False

    def test_corrida_de_una_hoja(self):
        # Con las filas 5 y 6: hasta a198645 eran la 5 y la 7, que no trae nave y ahora no va al portal
        # (test_fila_sin_nave_no_abre_el_portal, CICLO-solo-la-nave-pedida.md).
        def respuesta(nav, rsv, on_pausa):
            if rsv["fila"] == 6:
                return ("EMITIDA", "ONE emitida con éxito (Booking: FALSO12345)")
            return ("OK-EJEMPLO", "armada falsa")
        antes = {p.name for p in (self.sb / "logs").glob("*")}
        with Navieras(self.mod, respuesta=respuesta) as n:
            e = self.correr("ONE", [5, 6])
        self.assertEqual(n.logins, [("one", "usuario.one@ejemplo.invalid")])
        self.assertEqual(n.reservas, [("one", 5, "usuario.one@ejemplo.invalid"), ("one", 6, "usuario.one@ejemplo.invalid")])
        self.assertEqual(e["estado"], "Terminado.")
        self.assertEqual({k: (v["estado"], v["booking"], v["nave"]) for k, v in e["resultados"].items()},
                         {"5": ("OK-EJEMPLO", "", "NAVE PRUEBA UNO"), "6": ("EMITIDA", "FALSO12345", "NAVE PRUEBA DOS")})
        lanz = n.pw.lanzamientos
        self.assertEqual(len(lanz), 1)
        self.assertEqual(Path(lanz[0]["user_data_dir"]), self.sb / "perfiles" / "op_prueba")
        self.assertEqual((lanz[0]["channel"], lanz[0]["headless"], lanz[0]["no_viewport"], lanz[0]["ignore_default_args"]),
                         ("chrome", False, True, ["--enable-automation"]))
        self.assertEqual(lanz[0]["args"], self.mod._args_chrome())
        self.assertTrue(n.pw.contextos[0].cerrado)
        self.assertEqual(n.pw.contextos[0].scripts, [self.mod.STEALTH_JS])
        self.assertIn("INICIO · ONE · operador op_prueba · 2 reserva(s)", e["lineas"][0])
        carpeta = Path(self.mod._WEB["carpeta"])
        self.assertEqual(carpeta.parent, self.sb / "logs")
        # Con «_2», «_3»… si otra corrida ya tomó ese segundo; la carpeta tiene que ser nueva (hasta 393f504
        # compartía la de la prueba anterior 4 de cada 5 veces, y esta prueba no lo veía).
        self.assertRegex(carpeta.name, r"^web_one_op_prueba_\d{8}_\d{6}(_\d+)?$")
        self.assertNotIn(carpeta.name, antes)
        self.assertTrue((carpeta / "log.txt").exists())

    def test_dice_su_candado_al_empezar(self):
        # Cada corrida del panel dice al empezar, en su registro y en log.txt, con qué candado corre y por cuál llave
        # (_anotar_candado; decisión de Marcelo, encargo 51). Con las tres apagadas, modo prueba; con llaves, cuáles
        # (aquí, dichas por _llaves_abiertas solo para la línea: el candado de la guarda sigue cerrado).
        with Navieras(self.mod):
            e = self.correr("ONE", [5])
        self.assertIn("· INICIO · ONE · operador op_prueba · 1 reserva(s)", e["lineas"][0])
        self.assertIn("· 🛡️ Candado de emisión cerrado: modo prueba, sin ninguna de sus tres llaves abierta",
                      e["lineas"][1])
        log = (Path(self.mod._WEB["carpeta"]) / "log.txt").read_text(encoding="utf-8").splitlines()
        self.assertEqual(log[:2], e["lineas"][:2])
        llaves = (lambda todas=False: ["la primera", "la segunda"] if todas else [])
        with Navieras(self.mod), mock.patch.object(self.mod, "_llaves_abiertas", llaves):
            e = self.correr("ONE", [5])
        self.assertIn("· 🔴 Candado de emisión abierto: modo EMISIÓN, por la primera y la segunda. Cada reserva que "
                      "llegue al botón final se envía a la naviera.", e["lineas"][1])

    def test_dos_corridas_en_el_mismo_segundo(self):
        # Con el reloj detenido, dos corridas seguidas caen en el mismo segundo: cada una con su carpeta
        # y su log (CICLO-carpetas-unicas.md).
        carpetas = []
        with soporte.reloj_detenido(self.mod), Navieras(self.mod):
            for _ in range(2):
                self.correr("ONE", [5])
                carpetas.append(Path(self.mod._WEB["carpeta"]))
        self.assertEqual([c.name for c in carpetas],
                         ["web_one_op_prueba_20260102_030405", "web_one_op_prueba_20260102_030405_2"])
        self.assertEqual([len(re.findall(r"· INICIO", (c / "log.txt").read_text(encoding="utf-8")))
                          for c in carpetas], [1, 1])

    def test_corrida_con_estados_tras_el_envio(self):
        # De punta a punta: lo que devuelve el reservador llega al panel y a la planilla descargada.
        # El número va solo con EMITIDA, aunque el error del portal cite un código. La 7 no trae nave: su NO ENVIADA
        # lo pone el panel sin ir al portal. Hasta a198645, la 5 volvía NO ENVIADA del reservador y la 7, EMITIDA
        # (CICLO-solo-la-nave-pedida.md).
        respuestas = {
            5: ("EMITIDA", "ONE emitida con éxito (Booking: SCLG10000003)"),
            6: ("ENVIADA – REVISAR EN PORTAL", "ONE: se pulsó «Submit» y el portal mostró un error: «Booking: "
                                               "COSFALSO9876 ya existe». Revisa en el portal.")}
        with Navieras(self.mod, respuesta=lambda nav, rsv, on_pausa: respuestas[rsv["fila"]]):
            e = self.correr("ONE", [5, 6, 7])
        self.assertEqual({k: (v["estado"], v["booking"]) for k, v in e["resultados"].items()},
                         {"5": ("EMITIDA", "SCLG10000003"), "6": ("ENVIADA – REVISAR EN PORTAL", ""), "7": ("NO ENVIADA", "")})
        st, _, cuerpo = self.srv.completo("/api/descargar")
        self.assertEqual(st, 200)
        ws = openpyxl.load_workbook(BytesIO(cuerpo))["ONE"]
        self.assertEqual([(ws[f"H{f}"].value, ws[f"I{f}"].value) for f in (5, 6, 7)],
                         [("EMITIDA", "SCLG10000003"),
                          (f"ENVIADA – REVISAR EN PORTAL · {respuestas[6][1]}", None),
                          ("NO ENVIADA · la fila no trae una nave para reservar", None)])

    def test_corrida_sin_filas_no_abre_el_navegador(self):
        # Hasta 42247d4, con una sola naviera, abría el navegador y entraba al portal igual
        # (CICLO-cola-nueve-items.md).
        aviso = ("⚠ No hay filas elegidas: no abro el navegador ni entro a ningún portal. Elige al menos una fila y "
                 "vuelve a armar las reservas.")
        for hoja in ("ONE", "CONSOLIDADO"):
            with self.subTest(hoja=hoja), Navieras(self.mod) as n:
                e = self.correr(hoja, [])
                self.assertEqual((len(n.pw.lanzamientos), len(n.logins), n.reservas), (0, 0, []))
                self.assertEqual((e["estado"], e["resultados"]), ("Terminado.", {}))
                self.assertEqual(sum(aviso in l for l in e["lineas"]), 1)
                # Ni el aviso de las filas sin nave, que es para una naviera con filas (desde el encargo 28).
                self.assertFalse(any("Ninguna fila de" in l for l in e["lineas"]))

    def test_fila_sin_nave_no_abre_el_portal(self):
        # Una fila sin nave (vacía o con un comodín) queda NO ENVIADA con el motivo, en pantalla, en log.txt y en la
        # planilla, y no se abre el portal por ella (decisión de Marcelo, CICLO-solo-la-nave-pedida.md). Hasta a198645
        # iba al reservador: ONE y COSCO devolvían OMITIDO solo con la celda vacía, y con un comodín entraban al portal.
        motivo = "la fila no trae una nave para reservar"
        self.subir_con({("ONE", 6): "Primera disponible"})     # un comodín; la 7 viene vacía y la 10, «POR COMPLETAR»
        with Navieras(self.mod) as n:
            e = self.correr("ONE", [5, 6, 7, 10])
        self.assertEqual((len(n.pw.lanzamientos), n.reservas), (1, [("one", 5, "usuario.one@ejemplo.invalid")]))
        self.assertEqual({k: (v["estado"], v["detalle"], v["booking"]) for k, v in e["resultados"].items() if k != "5"},
                         {f: ("NO ENVIADA", motivo, "") for f in ("6", "7", "10")})
        log = (Path(self.mod._WEB["carpeta"]) / "log.txt").read_text(encoding="utf-8")
        for f in (6, 7, 10):
            linea = (f"✗ fila {f}: NO ENVIADA · {motivo}. No entro al portal por ella: escribe la nave en la planilla y "
                     "vuelve a armar la reserva.")
            with self.subTest(fila=f):
                self.assertIn(linea, log)
                self.assertEqual(sum(linea in l for l in e["lineas"]), 1)
        st, _, cuerpo = self.srv.completo("/api/descargar")
        self.assertEqual(st, 200)
        ws = openpyxl.load_workbook(BytesIO(cuerpo))["ONE"]
        self.assertEqual([(ws[f"H{f}"].value, ws[f"I{f}"].value) for f in (6, 7, 10)],
                         [(f"NO ENVIADA · {motivo}", None)] * 3)
        # Si ninguna fila de la naviera trae nave, no se abre el navegador ni se entra al portal.
        aviso = "Ninguna fila de ONE trae una nave para reservar: no abro el navegador ni entro al portal."
        with Navieras(self.mod) as n:
            e = self.correr("ONE", [6, 7])
        self.assertEqual((len(n.pw.lanzamientos), n.logins, n.reservas), (0, [], []))
        self.assertEqual(sorted(e["resultados"], key=int), ["6", "7"])
        self.assertEqual(sum(aviso in l for l in e["lineas"]), 1)

    def test_fila_con_solo_el_prefijo_no_abre_el_portal(self):
        # Una fila con solo el prefijo de la naviera tampoco pide una nave: /api/filas lo dice, y la corrida la deja NO
        # ENVIADA sin abrir el navegador (decisión de Marcelo, CICLO-cola-seis-items.md). Hasta f68ce6c iba al portal, y
        # el reservador buscaba «ONE» en las tarjetas.
        motivo = "la fila no trae una nave para reservar"
        self.subir_con({("ONE", 5): "ONE"})
        st, d = self.srv.json("/api/filas?hoja=ONE")
        self.assertEqual((st, {f["fila"]: f["sin_nave"] for f in d["filas"]}[5]), (200, True))
        with Navieras(self.mod) as n:
            e = self.correr("ONE", [5])
        self.assertEqual((len(n.pw.lanzamientos), n.logins, n.reservas), (0, [], []))
        self.assertEqual((e["resultados"]["5"]["estado"], e["resultados"]["5"]["detalle"]), ("NO ENVIADA", motivo))

    def test_fila_manual_corrida_igual_queda_no_enviada(self):
        # /api/filas marca la fila MANUAL (el panel la deja sin marcar) y no la cuenta como sin nave. Si se corre igual,
        # queda NO ENVIADA con su motivo, en pantalla, en log.txt y en la planilla, sin entrar al portal por ella
        # (decisión de Marcelo, CICLO-cola-seis-items.md). Hasta f68ce6c iba al portal y buscaba «MANUAL» como nave.
        motivo = "la fila está marcada para hacerse a mano"
        self.subir_con({("ONE", 6): "Reserva MANUAL"})
        st, d = self.srv.json("/api/filas?hoja=ONE")
        self.assertEqual(st, 200)
        self.assertEqual({f["fila"]: (f["sin_nave"], f["manual"]) for f in d["filas"]},
                         {5: (False, False), 6: (False, True), 7: (True, False), 9: (True, False), 10: (True, False)})
        with Navieras(self.mod) as n:
            e = self.correr("ONE", [5, 6])
        self.assertEqual((len(n.pw.lanzamientos), n.reservas), (1, [("one", 5, "usuario.one@ejemplo.invalid")]))
        self.assertEqual((e["resultados"]["6"]["estado"], e["resultados"]["6"]["detalle"]), ("NO ENVIADA", motivo))
        linea = (f"✗ fila 6: NO ENVIADA · {motivo}. No entro al portal por ella: hazla a mano en el portal, o escribe "
                 "en la celda solo la nave, sin MANUAL, si quieres que la arme yo.")
        self.assertIn(linea, (Path(self.mod._WEB["carpeta"]) / "log.txt").read_text(encoding="utf-8"))
        self.assertEqual(sum(linea in l for l in e["lineas"]), 1)
        st, _, cuerpo = self.srv.completo("/api/descargar")
        ws = openpyxl.load_workbook(BytesIO(cuerpo))["ONE"]
        self.assertEqual((st, ws["H6"].value, ws["I6"].value), (200, f"NO ENVIADA · {motivo}", None))
        # Sola, no abre el navegador.
        with Navieras(self.mod) as n:
            self.correr("ONE", [6])
        self.assertEqual((len(n.pw.lanzamientos), n.logins, n.reservas), (0, [], []))

    def subir_con(self, naves):
        """Sube la planilla sintética con estas naves: {(hoja, fila): nave}."""
        wb = openpyxl.load_workbook(BytesIO(self.xlsx))
        for (hoja, fila), nave in naves.items():
            wb[hoja][f"E{fila}"] = nave
        cuerpo = BytesIO()
        wb.save(cuerpo)
        self.assertEqual(self.srv.json("/api/planilla?nombre=Naves.xlsx", cuerpo.getvalue())[0], 200)

    def test_fila_sin_nave_en_consolidado(self):
        # En CONSOLIDADO, cada fila sin nave queda NO ENVIADA una sola vez, con su naviera, y una naviera sin filas con
        # nave no abre su navegador (CICLO-solo-la-nave-pedida.md).
        self.subir_con({("CONSOLIDADO", 6): None, ("CONSOLIDADO", 7): "Cualquiera"})     # la de MSC y la de CMA
        with Navieras(self.mod) as n:
            e = self.correr("CONSOLIDADO", [5, 6, 7, 8])
        self.assertEqual([r[:2] for r in n.reservas], [("one", 5), ("cosco", 8)])
        self.assertEqual([l[0] for l in n.logins], ["one", "cosco"])
        self.assertEqual({k: v["estado"] for k, v in e["resultados"].items()},
                         {"5": "OK-EJEMPLO", "6": "NO ENVIADA", "7": "NO ENVIADA", "8": "OK-EJEMPLO"})
        for texto in ("✗ fila 6: NO ENVIADA", "✗ fila 7: NO ENVIADA",
                      "Ninguna fila de MSC trae una nave para reservar", "Ninguna fila de CMA-CGM trae una nave para reservar"):
            with self.subTest(texto=texto):
                self.assertEqual(sum(texto in l for l in e["lineas"]), 1)

    def subir_celdas(self, celdas):
        """Sube la planilla sintética con estas celdas: {(hoja, celda): valor}."""
        wb = openpyxl.load_workbook(BytesIO(self.xlsx))
        for (hoja, celda), valor in celdas.items():
            wb[hoja][celda] = valor
        cuerpo = BytesIO()
        wb.save(cuerpo)
        self.assertEqual(self.srv.json("/api/planilla?nombre=Ruta.xlsx", cuerpo.getvalue())[0], 200)

    def test_fila_sin_puerto_o_sin_destino_no_abre_el_portal(self):
        # Una fila con nave y sin puerto de carga o sin destino queda NO ENVIADA con el motivo, en pantalla, en log.txt
        # y en la planilla, sin abrir el portal por ella, como la fila sin nave (decisión de Marcelo, encargo 42,
        # CICLO-maersk-y-fila-sin-ruta.md). La 6, con solo el país en el puerto de carga; la 7, con nave y sin destino.
        puerto, destino = "a la fila le falta el puerto de carga", "a la fila le falta el destino"
        self.subir_celdas({("ONE", "B6"): ", CHILE", ("ONE", "E7"): "NAVE PRUEBA QUINCE", ("ONE", "C7"): None,
                           ("ONE", "D7"): None})
        with Navieras(self.mod) as n:
            e = self.correr("ONE", [5, 6, 7])
        self.assertEqual((len(n.pw.lanzamientos), n.reservas), (1, [("one", 5, "usuario.one@ejemplo.invalid")]))
        self.assertEqual({k: (v["estado"], v["detalle"], v["booking"]) for k, v in e["resultados"].items() if k != "5"},
                         {"6": ("NO ENVIADA", puerto, ""), "7": ("NO ENVIADA", destino, "")})
        log = (Path(self.mod._WEB["carpeta"]) / "log.txt").read_text(encoding="utf-8")
        for f, falta, que in ((6, puerto, "el puerto de carga"), (7, destino, "el destino")):
            linea = (f"✗ fila {f}: NO ENVIADA · {falta}. No entro al portal por ella: escribe {que} en la planilla y "
                     "vuelve a armar la reserva.")
            with self.subTest(fila=f):
                self.assertIn(linea, log)
                self.assertEqual(sum(linea in l for l in e["lineas"]), 1)
        st, _, cuerpo = self.srv.completo("/api/descargar")
        ws = openpyxl.load_workbook(BytesIO(cuerpo))["ONE"]
        self.assertEqual((st, [(ws[f"H{f}"].value, ws[f"I{f}"].value) for f in (6, 7)]),
                         (200, [(f"NO ENVIADA · {puerto}", None), (f"NO ENVIADA · {destino}", None)]))
        # Si ninguna fila con nave trae la ruta, no se abre el navegador ni se entra al portal.
        aviso = ("Ninguna fila de ONE con nave trae el puerto de carga y el destino: no abro el navegador ni entro al "
                 "portal.")
        with Navieras(self.mod) as n:
            e = self.correr("ONE", [6, 7])
        self.assertEqual((len(n.pw.lanzamientos), n.logins, n.reservas), (0, [], []))
        self.assertEqual(sorted(e["resultados"], key=int), ["6", "7"])
        self.assertEqual(sum(aviso in l for l in e["lineas"]), 1)
        # Sin nave y sin destino, el motivo es el de la nave (la 7 viene sin nave).
        self.subir_celdas({("ONE", "C7"): None, ("ONE", "D7"): None})
        with Navieras(self.mod) as n:
            e = self.correr("ONE", [7])
        self.assertEqual((e["resultados"]["7"]["detalle"], n.reservas), ("la fila no trae una nave para reservar", []))

    def test_fila_sin_puerto_en_consolidado(self):
        # En CONSOLIDADO, cada fila con su naviera: la de MSC sin puerto de carga queda NO ENVIADA una sola vez, y MSC
        # no abre su navegador (encargo 42).
        self.subir_celdas({("CONSOLIDADO", "B6"): None})
        with Navieras(self.mod) as n:
            e = self.correr("CONSOLIDADO", [5, 6, 7])
        self.assertEqual([r[:2] for r in n.reservas], [("one", 5), ("cma", 7)])
        self.assertEqual([l[0] for l in n.logins], ["one", "cma"])
        self.assertEqual({k: v["estado"] for k, v in e["resultados"].items()},
                         {"5": "OK-EJEMPLO", "6": "NO ENVIADA", "7": "OK-EJEMPLO"})
        for texto in ("✗ fila 6: NO ENVIADA · a la fila le falta el puerto de carga",
                      "Ninguna fila de MSC con nave trae el puerto de carga y el destino"):
            with self.subTest(texto=texto):
                self.assertEqual(sum(texto in l for l in e["lineas"]), 1)

    def test_filas_dicen_si_traen_nave(self):
        # /api/filas dice, con la regla del programa, qué fila no trae una nave para reservar: el panel la muestra y la
        # marca con eso (test_envio.TestLecturaDelPanel). Hasta a198645 el panel solo miraba la celda vacía.
        self.subir_con({("ONE", 6): "Primera disponible"})
        st, d = self.srv.json("/api/filas?hoja=ONE")
        self.assertEqual(st, 200)
        self.assertEqual({f["fila"]: f["sin_nave"] for f in d["filas"]}, {5: False, 6: True, 7: True, 9: True, 10: True})

    def test_filas_dicen_si_traen_la_ruta(self):
        # /api/filas dice, con la regla del programa (_falta_en_la_fila), qué fila con nave no trae su puerto de carga o
        # su destino: el panel la marca y la cuenta aparte antes de correr, como la fila sin nave (decisión de Marcelo,
        # encargo 43, CICLO-maersk-elige-exacto.md; test_envio.TestLecturaDelPanel). La fila sin nave, o MANUAL, no
        # lleva esas marcas: su motivo es el de la nave. La 6, con solo el país en el puerto de carga; la 7, con nave y
        # sin destino; la 9, sin nave y sin destino; la 10, MANUAL y sin puerto de carga.
        self.subir_celdas({("ONE", "B6"): ", CHILE", ("ONE", "E7"): "NAVE PRUEBA QUINCE", ("ONE", "C7"): None,
                           ("ONE", "D7"): None, ("ONE", "E10"): "Reserva MANUAL", ("ONE", "B10"): None})
        st, d = self.srv.json("/api/filas?hoja=ONE")
        self.assertEqual(st, 200)
        marcas = {f["fila"]: (f["sin_puerto"], f["sin_destino"], f["sin_nave"], f["manual"]) for f in d["filas"]}
        self.assertEqual(marcas, {5: (False, False, False, False), 6: (True, False, False, False),
                                  7: (False, True, False, False), 9: (False, False, True, False),
                                  10: (False, False, False, True)})

    def test_consolidado_reparte_por_naviera(self):
        with Navieras(self.mod) as n:
            e = self.correr("CONSOLIDADO", [5, 6, 7, 8, 9, 10, 11])
        self.assertEqual([r[:2] for r in n.reservas],
                         [("one", 5), ("msc", 6), ("cma", 7), ("cosco", 8), ("hyundai", 9), ("maersk", 10)])
        self.assertEqual([l[0] for l in n.logins], ["one", "msc", "cma", "cosco", "hyundai", "maersk"])
        self.assertEqual(len(n.pw.lanzamientos), 6)                  # un navegador por naviera
        self.assertNotIn("11", e["resultados"])                      # «OTRA LINEA» no se procesa
        self.assertEqual(sorted(e["resultados"], key=int), ["5", "6", "7", "8", "9", "10"])

    def test_login_fallido_no_reserva(self):
        with Navieras(self.mod, login_ok=False) as n:
            e = self.correr("ONE", [5, 7])
        # La 7 no trae nave: queda NO ENVIADA antes del login, y no depende de él. Hasta a198645 no tenía resultado
        # (CICLO-solo-la-nave-pedida.md). La 5 queda sin estado: así sigue el login fallido de las navieras que no son
        # MSC (encargo 45; hasta ahí esta prueba usaba MSC).
        self.assertEqual((n.reservas, {k: (v["estado"], v["detalle"]) for k, v in e["resultados"].items()}),
                         ([], {"7": ("NO ENVIADA", "la fila no trae una nave para reservar")}))
        self.assertTrue(any("No se pudo iniciar sesión en ONE" in l for l in e["lineas"]))

    def test_login_fallido_de_msc_queda_no_enviada(self):
        # Sin la sesión de MSC, cada fila de MSC queda NO ENVIADA con su motivo, sin otro intento de inicio de sesión
        # (decisión de Marcelo, encargo 45, CICLO-login-msc-y-maersk.md); hasta ahí quedaba sin estado.
        with Navieras(self.mod, login_ok=False) as n:
            e = self.correr("MSC", [5, 6])
        self.assertEqual((n.reservas, [l[0] for l in n.logins],
                          {k: (v["estado"], v["detalle"]) for k, v in e["resultados"].items()}),
                         ([], ["msc"], {"5": ("NO ENVIADA", self.mod.MSC_SIN_SESION),
                                        "6": ("NO ENVIADA", "la fila no trae una nave para reservar")}))
        self.assertTrue(any(f"✗ fila 5: NO ENVIADA · {self.mod.MSC_SIN_SESION}" in l for l in e["lineas"]))

    def test_login_de_msc_deja_su_motivo(self):
        # Si el login de MSC dejó su motivo en el Registro (tras el segundo intento: MSC_SIN_SESION_TRAS_DOS,
        # decisión de Marcelo, encargo 50), es el de cada fila de MSC, en el panel y en log.txt (_motivo_sin_sesion).
        def login(page, creds, reg, on_pausa=None):
            reg.sin_sesion = {"msc": self.mod.MSC_SIN_SESION_TRAS_DOS}
            return False
        with Navieras(self.mod, login_ok=False) as n:
            self.mod.NAVIERAS["msc"] = ("MSC", login)
            e = self.correr("MSC", [5])
        self.assertEqual((n.reservas, (e["resultados"]["5"]["estado"], e["resultados"]["5"]["detalle"])),
                         ([], ("NO ENVIADA", self.mod.MSC_SIN_SESION_TRAS_DOS)))
        self.assertTrue(any(f"✗ fila 5: NO ENVIADA · {self.mod.MSC_SIN_SESION_TRAS_DOS}" in l for l in e["lineas"]))

    def test_reservador_que_revienta(self):
        def respuesta(nav, rsv, on_pausa):
            raise RuntimeError("falla falsa del portal")
        with Navieras(self.mod, respuesta=respuesta) as n:
            e = self.correr("COSCO", [5])
        self.assertEqual((e["resultados"]["5"]["estado"], e["resultados"]["5"]["detalle"]),
                         ("ERROR", "falla falsa del portal"))
        self.assertEqual(n.pw.contextos[0].pages[0].capturas, [("error_cosco_rsv_1.png", False)])

    def test_pausa_y_continuar(self):
        def respuesta(nav, rsv, on_pausa):
            on_pausa("resuelve el paso de prueba")
            return ("OK-EJEMPLO", "siguió tras la pausa")
        with Navieras(self.mod, respuesta=respuesta):
            self.srv.json("/api/correr", {"hoja": "HYUNDAI", "usuario": "op_prueba", "filas": [5]})
            fin = time.time() + 10
            while time.time() < fin:
                _, e = self.srv.json("/api/estado")
                if e["pausa"]:
                    break
                time.sleep(0.1)
            self.assertEqual((e["pausa"], e["pausa_msg"], e["estado"]),
                             (True, "resuelve el paso de prueba", "Te toca a ti: resuelve el paso en el navegador"))
            self.assertEqual(self.srv.json("/api/continuar", {}), (200, {"ok": True}))
            e = self.srv.esperar_fin()
        self.assertEqual(e["resultados"]["5"]["detalle"], "siguió tras la pausa")
        self.assertFalse(e["pausa"])

    def test_detener(self):
        def respuesta(nav, rsv, on_pausa):
            on_pausa("esperando para detener")
            return ("OK-EJEMPLO", "fila tras detener")
        with Navieras(self.mod, respuesta=respuesta) as n:
            self.srv.json("/api/correr", {"hoja": "MAERSK", "usuario": "op_prueba", "filas": [5, 6]})
            fin = time.time() + 10
            while time.time() < fin and not self.srv.json("/api/estado")[1]["pausa"]:
                time.sleep(0.1)
            self.assertEqual(self.srv.json("/api/detener", {}), (200, {"ok": True}))
            e = self.srv.esperar_fin()
            time.sleep(0.3)
        self.assertEqual(e["estado"], "Detenido.")
        self.assertEqual([r[1] for r in n.reservas], [5])            # la fila 6 ya no se procesa
        self.assertTrue(n.pw.contextos[0].cerrado)
        self.assertTrue(any("Detenido por el operador" in l for l in e["lineas"]))

    def test_modo_login(self):
        self.assertEqual(self.srv.json("/api/login", {"usuario": "op_prueba", "navieras": ["xx"]}),
                         (400, {"error": "elige al menos una naviera"}))
        with Navieras(self.mod) as n:
            t0 = time.time()
            st, r = self.srv.json("/api/login", {"usuario": "op_prueba", "navieras": ["one", "xx", "msc"]})
            e = self.srv.esperar_fin(maximo=20)
            demora = time.time() - t0
        self.assertEqual((st, r), (200, {"ok": True}))
        self.assertEqual([l[0] for l in n.logins], ["one", "msc"])
        self.assertEqual(e["estado"], "Sesiones abiertas.")
        self.assertGreaterEqual(demora, 6)          # deja el navegador abierto 6 s antes de cerrarlo
        self.assertEqual(Path(n.pw.lanzamientos[0]["user_data_dir"]), self.sb / "perfiles" / "op_prueba")


class TestArranqueDelPanel(unittest.TestCase):
    """Cómo arranca lanzar_web cuando el puerto está ocupado."""

    def setUp(self):
        soporte.DISPAROS.clear()
        self.orig = (subprocess.check_output, subprocess.call)
        self.llamadas = []

    def tearDown(self):
        subprocess.check_output, subprocess.call = self.orig
        disparos = list(soporte.DISPAROS)
        soporte.DISPAROS.clear()
        soporte.apagar_llaves()
        self.assertEqual(disparos, [])

    def _falsos(self, salida_netstat):
        def check_output(cmd, shell=False):
            self.llamadas.append(("netstat", cmd))
            return salida_netstat.encode()

        def call(cmd, shell=False):
            self.llamadas.append(("call", cmd))
            return 0
        subprocess.check_output, subprocess.call = check_output, call

    def test_cierra_a_la_fuerza_al_que_ocupa_el_puerto(self):
        mod, _ = soporte.cargar()
        ocupante = socket.socket()
        ocupante.bind(("127.0.0.1", 0))
        ocupante.listen(1)
        p = ocupante.getsockname()[1]
        self._falsos(f"  TCP    127.0.0.1:{p}     0.0.0.0:0      LISTENING       424242\n")
        srv = soporte.Servidor(mod, p + 1)
        hilo = threading.Thread(target=mod.lanzar_web, kwargs={"puerto": p, "abrir": False}, daemon=True)
        try:
            hilo.start()
            fin = time.time() + 15
            while time.time() < fin:
                try:
                    srv.get("/api/estado")
                    break
                except Exception:
                    time.sleep(0.1)
            self.assertEqual(self.llamadas, [
                ("netstat", f'netstat -ano -p tcp | findstr /R /C:":{p} .*LISTENING"'),
                ("call", "taskkill /F /PID 424242")])
            self.assertEqual(srv.get("/api/estado")[0], 200)     # como el ocupante sigue, usa el puerto siguiente
        finally:
            srv.hilo = hilo
            srv.apagar()
            ocupante.close()

    def _hijo_servidor(self, puerto, corriendo=False, emision=False):
        # Con 'emision', el panel previo está en modo emisión sin abrir ninguna llave: su es_modo_emision dice True
        # (encargo 51).
        sb = soporte.nueva_sandbox()
        codigo = (f"import sys; sys.path.insert(0, {str(TESTS)!r}); import soporte; "
                  f"mod, sb = soporte.cargar(); mod._WEB['corriendo'] = {corriendo}; "
                  f"mod.es_modo_emision = lambda: {emision}; "
                  f"mod.lanzar_web(puerto={puerto}, abrir=False)")
        return soporte._POPEN([sys.executable, "-c", codigo], cwd=str(sb), stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL, env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})

    def _esperar(self, srv, segundos=20):
        fin = time.time() + segundos
        while time.time() < fin:
            try:
                return srv.get("/api/estado")
            except Exception:
                time.sleep(0.2)
        raise AssertionError("no respondió")

    def test_instancia_previa_ociosa_se_apaga(self):
        self._falsos("")
        p = soporte.puerto_libre()
        hijo = self._hijo_servidor(p)
        try:
            self._esperar(soporte.Servidor(None, p))
            cfg = sinteticos.config()
            cfg["usuarios"] = {"op_relevo": cfg["usuarios"]["op_prueba"]}
            mod, _ = soporte.cargar(config=cfg)
            hilo = threading.Thread(target=mod.lanzar_web, kwargs={"puerto": p, "abrir": False}, daemon=True)
            hilo.start()
            self.assertEqual(hijo.wait(timeout=15), 0)               # la instancia previa se apagó sola
            # El relevo espera 0,6 s y toma el puerto; si la previa tardó más en soltarlo,
            # usa el siguiente. Las dos salidas son del programa tal como es.
            for q in (p, p + 1):
                srv = soporte.Servidor(mod, q)
                try:
                    self._esperar(srv, 5)
                    break
                except AssertionError:
                    continue
            self.assertEqual(srv.json("/api/config")[1]["usuarios"], ["op_relevo"])
            srv.hilo = hilo
            srv.apagar()
        finally:
            if hijo.poll() is None:
                hijo.kill()

    def test_instancia_previa_ocupada_no_se_toca(self):
        self._falsos("")
        p = soporte.puerto_libre()
        hijo = self._hijo_servidor(p, corriendo=True)
        try:
            previa = soporte.Servidor(None, p)
            self._esperar(previa)
            mod, _ = soporte.cargar()
            hilo = threading.Thread(target=mod.lanzar_web, kwargs={"puerto": p, "abrir": False}, daemon=True)
            hilo.start()
            hilo.join(timeout=5)                                     # vuelve enseguida, sin levantar nada
            vivo = hilo.is_alive()
            if vivo and mod._SRV_ACTUAL:
                mod._SRV_ACTUAL.shutdown()
            self.assertFalse(vivo, "lanzar_web levantó un servidor en vez de ceder a la instancia ocupada")
            self.assertIsNone(hijo.poll())
            self.assertIs(previa.json("/api/estado")[1]["corriendo"], True)
            self.assertIsNone(mod._SRV_ACTUAL)
            self.assertEqual(self.llamadas, [])
        finally:
            if hijo.poll() is None:
                hijo.kill()

    MODO = {True: "EMISIÓN (reservas reales)", False: "prueba (sin emitir)"}

    def texto_otro_modo(self, puerto, modo, propio, ocupado):
        """El aviso del lanzador ante un panel en el otro modo (o que no dice el suyo, con 'modo' None)."""
        cual = f"en modo {self.MODO[modo]}" if modo is not None else "y no pude saber en qué modo está"
        cerrar = "con su botón rojo de apagar, arriba a la derecha, o cerrando su pestaña y esperando unos dos minutos"
        como = (f"Ese panel está armando reservas: espera a que termine, después ciérralo {cerrar}, y vuelve a abrir "
                f"este lanzador." if ocupado else f"Ciérralo {cerrar}, y vuelve a abrir este lanzador.")
        return (f"Ya hay un panel de AQUASHIELD abierto {cual}, en http://127.0.0.1:{puerto}/, y este lanzador lo "
                f"abriría en modo {self.MODO[propio]}. Para no mezclar los modos, no me conecto a ese panel, no lo "
                f"cierro y no abro otro. {como}")

    def lanzar(self, puerto, propio, abrir=True):
        """Corre lanzar_web de una copia nueva, en modo 'propio' (su es_modo_emision, sin abrir ninguna llave), con su
        aviso anotado. Devuelve (si quedó sirviendo, los avisos, la copia)."""
        mod, _ = soporte.cargar()
        mod.es_modo_emision = (lambda: propio)
        avisos = []
        mod._avisar_al_lanzar = avisos.append
        hilo = threading.Thread(target=mod.lanzar_web, kwargs={"puerto": puerto, "abrir": abrir}, daemon=True)
        hilo.start()
        hilo.join(timeout=10)
        vivo = hilo.is_alive()
        if vivo and mod._SRV_ACTUAL:
            mod._SRV_ACTUAL.shutdown()
            hilo.join(timeout=6)
        return vivo, avisos, mod

    def test_panel_en_otro_modo_avisa_y_no_corre(self):
        # Decisión de Marcelo, encargo 51 (CICLO-modo-y-lanzadores.md): un lanzador nunca se conecta a un panel abierto
        # en otro modo; avisa y no corre. Medido antes del cambio, en estos mismos cuatro casos: con el panel ocupado,
        # el lanzador lo abría en el navegador en el modo que tuviera (también el de prueba a uno de emisión); con el
        # panel ocioso, le pedía que se apagara y tomaba su puerto, y una pestaña suya que quedara abierta hablaba con
        # el panel nuevo, del otro modo. Ahora: un solo aviso; sin abrir el navegador (abrir=True: la trampa lo
        # anotaría), sin apagar ni tocar ese panel, sin netstat ni taskkill, y sin levantar otro.
        self._falsos("")
        for emision in (False, True):
            for ocupado in (False, True):
                with self.subTest(panel="emisión" if emision else "prueba", ocupado=ocupado):
                    p = soporte.puerto_libre()
                    hijo = self._hijo_servidor(p, corriendo=ocupado, emision=emision)
                    try:
                        previa = soporte.Servidor(None, p)
                        self._esperar(previa)
                        vivo, avisos, mod = self.lanzar(p, not emision)
                        self.assertFalse(vivo, "el lanzador levantó un servidor")
                        self.assertIsNone(mod._SRV_ACTUAL)
                        self.assertEqual(avisos, [self.texto_otro_modo(p, emision, not emision, ocupado)])
                        self.assertIsNone(hijo.poll())
                        self.assertEqual((previa.json("/api/estado")[1]["corriendo"],
                                          previa.json("/api/config")[1]["modo_emision"]), (ocupado, emision))
                        self.assertEqual(self.llamadas, [])
                    finally:
                        if hijo.poll() is None:
                            hijo.kill()

    def test_panel_que_no_dice_su_modo_avisa_y_no_corre(self):
        # Si el panel abierto responde como AQUASHIELD pero no dice su modo (su /api/config falla, o no trae
        # «modo_emision» como true o false), el lanzador tampoco se conecta: avisa que no supo en qué modo está, y no
        # le pide que se apague.
        self._falsos("")
        for config in (None, {"version": "otra"}, {"modo_emision": "false"}):
            with self.subTest(config=config):
                pedidos = []

                class Falso(http.server.BaseHTTPRequestHandler):
                    def log_message(self, *a):
                        pass

                    def responder(self, codigo, cuerpo):
                        self.send_response(codigo)
                        self.send_header("Content-Length", str(len(cuerpo)))
                        self.end_headers()
                        self.wfile.write(cuerpo)

                    def do_GET(self, cfg=config):
                        pedidos.append(("GET", self.path))
                        if self.path.startswith("/api/estado"):
                            return self.responder(200, json.dumps({"corriendo": False}).encode())
                        if self.path == "/api/config" and cfg is not None:
                            return self.responder(200, json.dumps(cfg).encode())
                        self.responder(500, b"falla de prueba")

                    def do_POST(self):
                        pedidos.append(("POST", self.path))
                        self.responder(200, b"{}")
                srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Falso)
                hilo = threading.Thread(target=srv.serve_forever, daemon=True)
                hilo.start()
                try:
                    p = srv.server_address[1]
                    vivo, avisos, mod = self.lanzar(p, False)
                    self.assertEqual((vivo, mod._SRV_ACTUAL), (False, None))
                    self.assertEqual(avisos, [self.texto_otro_modo(p, None, False, False)])
                    self.assertEqual([m for m, _ in pedidos], ["GET", "GET"])
                    self.assertEqual(self.llamadas, [])
                finally:
                    srv.shutdown()
                    srv.server_close()

    def test_mismo_modo_de_emision_cede_como_antes(self):
        # En el mismo modo, como antes: al panel de emisión ocupado, el lanzador de emisión lo deja como está y no
        # levanta otro, sin aviso (aquí no abre el navegador: abrir=False).
        self._falsos("")
        p = soporte.puerto_libre()
        hijo = self._hijo_servidor(p, corriendo=True, emision=True)
        try:
            self._esperar(soporte.Servidor(None, p))
            vivo, avisos, mod = self.lanzar(p, True, abrir=False)
            self.assertEqual((vivo, avisos, mod._SRV_ACTUAL, hijo.poll(), self.llamadas), (False, [], None, None, []))
        finally:
            if hijo.poll() is None:
                hijo.kill()

    def test_el_aviso_va_a_una_ventana(self):
        # Los .bat lanzan con pythonw, sin consola: el aviso del lanzador va por la consola y a una ventana, como el de
        # main() cuando el panel web no abre (encargo 51). Aquí la ventana es una trampa del arnés, que la anota.
        mod, _ = soporte.cargar()
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            mod._avisar_al_lanzar("aviso de prueba")
        disparos = list(soporte.DISPAROS)
        soporte.DISPAROS.clear()
        self.assertEqual(salida.getvalue(), "aviso de prueba\n")
        self.assertEqual(disparos, [("tkinter.messagebox.showwarning", repr(("AQUASHIELD", "aviso de prueba")))])


if __name__ == "__main__":
    unittest.main()
