# -*- coding: utf-8 -*-
"""El panel web lleva el bloque estándar de marca de aquachile-brand (v48), y solo en lo que ve el operador (decisión de
Marcelo, encargo 84, CICLO-entorno-propio.md).

El panel se arma en memoria (HTML_INDEX, JS_INDEX, CSS_INDEX y CSS_FUENTES), así que el verificador de la skill no lo lee
tal cual: tests/marca/extraer_panel.py lo saca a archivos y la skill los mide. Esta red vigila lo que la medición de
la skill no ve y lo que se rompería sin avisar:
- el HTML trae el header, el pie y el JS del bloque una sola vez y en su orden (el JS, después del pie y antes de app.js,
  que lee sus claves al cargar), y app.js ya no maneja el tema ni el nombre de usuario;
- las dos funciones que el bloque no trae (Credenciales y Cerrar AQUASHIELD) siguen con sus id, en la barra de contexto;
- la receta que pasa el tema viejo («aq-tema», con «claro» u «oscuro») a la clave del bloque, corrida en Node;
- la declaración de estados (tests/marca/aquashield-estados.json) es usable y calza con lo que app.js lee de la API;
- el extractor arma el panel como archivos.
Se corre en Node lo que el navegador correría; sin Node, esas pruebas fallan."""
import json
import os
import re
import shutil
import sys
import unittest
from pathlib import Path

import soporte

MARCA = soporte.FUENTES / "tests" / "marca"
VERSION_DEL_BLOQUE = "v48"
N = iter(range(1, 10_000))


def correr_node(caso, guion):
    """Corre 'guion' en Node (fuera del navegador) y devuelve lo que imprimió, leído como JSON."""
    node = shutil.which("node")
    caso.assertTrue(node, "esta prueba corre JavaScript en Node y Node no está instalado")
    ruta = caso.sb / f"guion_marca_{next(N)}.js"
    ruta.write_text(guion, encoding="utf-8")
    rc, out, err = soporte.hijo([node, str(ruta)], cwd=caso.sb)
    caso.assertEqual(rc, 0, err[-600:])
    return json.loads(out)


class TestBloqueEnElPanel(soporte.CasoAQ):
    def test_el_html_trae_el_bloque_una_sola_vez(self):
        html = self.mod.HTML_INDEX
        self.assertEqual(html.count(f'<meta name="aquashield-bloque" content="{VERSION_DEL_BLOQUE}">'), 1)
        self.assertEqual(html.count('<header class="aquashield-header">'), 1)
        self.assertEqual(html.count('<footer class="aquashield-credit">'), 1)
        # El botón de tema llama a la función del bloque, que existe (una vez cada una).
        self.assertEqual(html.count('onclick="aquashieldToggleTheme()"'), 1)
        self.assertEqual(html.count("window.aquashieldToggleTheme = function"), 1)
        # El header propio de antes ya no está, ni su botón de tema, que ahora trae el bloque.
        self.assertNotIn("workspace-header", html)
        self.assertNotIn('id="tema"', html)

    def test_el_js_del_bloque_va_despues_del_pie_y_antes_de_app_js(self):
        html = self.mod.HTML_INDEX
        pie = html.index('<footer class="aquashield-credit">')
        bloque = html.index('const ASH_PREFIX = "mars_reservas_";')
        app = html.index('<script src="/app.js"></script>')
        self.assertLess(pie, bloque)
        self.assertLess(bloque, app)
        self.assertEqual(html.count("const ASH_PREFIX"), 1)

    def test_app_js_ya_no_maneja_el_tema_ni_el_nombre_de_usuario(self):
        js = self.mod.JS_INDEX
        for rastro in ("aq-tema", "K_USUARIO", "limpiarUsuario", "USUARIO_DEFECTO", "MARS_RESERVAS", "#tema", "#user-name"):
            with self.subTest(rastro=rastro):
                self.assertNotIn(rastro, js)

    def test_el_css_trae_el_bloque_una_vez_y_no_redefine_el_header(self):
        css = self.mod.CSS_INDEX
        self.assertEqual(css.count("BLOQUE ESTÁNDAR AQUASHIELD · aquachile-brand " + VERSION_DEL_BLOQUE), 1)
        # Cada regla del bloque está, una vez (con 0 el panel quedaría sin su header y esta prueba lo daría por bueno: el
        # comentario que enmarca el bloque seguiría ahí; revisión de código del encargo 84).
        for selector in (".brand-logo svg {", ".platform-name h1 {", ".module-label {", ".module-name {", ".avatar {",
                         ".user-profile {", ".theme-toggle-minimal {"):
            with self.subTest(selector=selector):
                self.assertEqual(css.count(selector), 1)
        self.assertNotIn(".workspace-header", css)

    def test_el_panel_conserva_las_reglas_que_le_dan_lugar_a_la_nota_y_a_los_estados(self):
        css = self.mod.CSS_INDEX
        for regla in ("\n.context-bar {\n",                                     # la barra de Credenciales y Cerrar
                      ".rs-panel > .rs-widgets {",                              # se desplazan los widgets, no la nota del modo
                      "body:not(.light-theme) tbody tr.fila-activa td {",       # en oscuro, el fondo de un estado es el neutro
                      "body:not(.light-theme) tbody tr.fila-emitida td {",
                      "body:not(.light-theme) .chip.rev",
                      "body:not(.light-theme) .progreso-pill {"):
            with self.subTest(regla=regla):
                self.assertEqual(css.count(regla), 1)

    def test_las_insignias_del_modo_van_en_clases_con_los_colores_de_la_paleta(self):
        # Antes iban en blanco sobre #10b981 y #ef4444, que no son de la paleta: 2,54 y 3,76 de contraste (medido por el
        # verificador de la skill). Ahora son clases del CSS, con el color de la paleta en el borde.
        js, css = self.mod.JS_INDEX, self.mod.CSS_INDEX
        self.assertEqual(js.count('<span class="modo-insignia seguro">MODO SEGURO</span>'), 1)
        self.assertEqual(js.count('<span class="modo-insignia emision">EMISIÓN REAL</span>'), 1)
        for color in ("#ef4444", "#10b981"):
            with self.subTest(color=color):
                self.assertNotIn(color, js)
        for regla in (".modo-insignia.seguro {", ".modo-insignia.emision {"):
            with self.subTest(regla=regla):
                self.assertEqual(css.count(regla), 1)

    def test_credenciales_y_cerrar_siguen_con_sus_id_en_la_barra_de_contexto(self):
        html = self.mod.HTML_INDEX
        barra = html[html.index('<div class="context-bar" id="context-bar">'):]
        barra = barra[:barra.index("</div>")]
        for ident in ('id="btn-cred"', 'id="btn-salir"'):
            with self.subTest(ident=ident):
                self.assertEqual(barra.count(ident), 1)
                self.assertEqual(html.count(ident), 1)
        # app.js los cablea por esos id: abrirCred y /api/apagar.
        self.assertIn("#btn-cred", self.mod.JS_INDEX)
        self.assertIn("#btn-salir", self.mod.JS_INDEX)
        self.assertIn("/api/apagar", self.mod.JS_INDEX)

    def test_la_receta_pasa_el_tema_viejo_a_la_clave_del_bloque(self):
        # El tema se guardaba en «aq-tema», con «claro» u «oscuro»; el bloque lee mars_reservas_theme, con «light-theme» o
        # «dark-theme». Corre en cada carga hasta que la marca existe, y no pisa un valor nuevo.
        m = re.search(r'\[\["aq-tema", "theme"\]\]\.forEach\(function \(par\) \{.*?\n    \}\);\n', self.mod.HTML_INDEX, re.S)
        self.assertIsNotNone(m, "no encontré la receta de migración del tema en HTML_INDEX")
        casos = [("oscuro", {"aq-tema": "oscuro"}), ("claro", {"aq-tema": "claro"}), ("sin viejo", {}),
                 ("ya migrado", {"aq-tema": "claro", "mars_reservas_migrado_theme": "1", "mars_reservas_theme": "dark-theme"}),
                 ("valor nuevo previo", {"aq-tema": "claro", "mars_reservas_theme": "dark-theme"})]
        guion = ('const ASH_PREFIX = "mars_reservas_";\n'
                 "function fake(inicial) { const d = Object.assign({}, inicial); return {\n"
                 "  getItem: k => (k in d ? d[k] : null), setItem: (k, v) => { d[k] = String(v); },\n"
                 "  removeItem: k => { delete d[k]; }, datos: d }; }\n"
                 f"const casos = {json.dumps([c[1] for c in casos])};\n"
                 "const salida = casos.map(c => { global.localStorage = fake(c);\n" + m.group(0) +
                 "\n  return global.localStorage.datos; });\n"
                 "console.log(JSON.stringify(salida));\n")
        salida = dict(zip([c[0] for c in casos], correr_node(self, guion)))
        self.assertEqual(salida["oscuro"], {"mars_reservas_theme": "dark-theme", "mars_reservas_migrado_theme": "1"})
        self.assertEqual(salida["claro"], {"mars_reservas_theme": "light-theme", "mars_reservas_migrado_theme": "1"})
        self.assertEqual(salida["sin viejo"], {})                       # nada que migrar: la marca no se quema
        self.assertEqual(salida["ya migrado"], {"mars_reservas_migrado_theme": "1", "aq-tema": "claro",
                                                "mars_reservas_theme": "dark-theme"})
        self.assertEqual(salida["valor nuevo previo"], {"mars_reservas_theme": "dark-theme",
                                                        "mars_reservas_migrado_theme": "1"})


class TestEstadosDeclarados(soporte.CasoAQ):
    """tests/marca/aquashield-estados.json: la fila en curso, la emitida, el chip de revisar y la pastilla de progreso solo
    existen con datos que llegan de la API; la declaración los abre con una API falsa que el navegador monta."""

    def setUp(self):
        super().setUp()
        self.datos = json.loads((MARCA / "aquashield-estados.json").read_text(encoding="utf-8"))

    def test_cada_estado_trae_lo_que_el_verificador_pide(self):
        estados = self.datos["estados"]
        self.assertTrue(estados)
        nombres = [e["nombre"] for e in estados]
        self.assertEqual(len(nombres), len(set(nombres)))
        for e in estados:
            with self.subTest(estado=e["nombre"]):
                for campo in ("nombre", "pagina", "por_que", "pasos", "abierto"):
                    self.assertTrue(e.get(campo), campo)
                self.assertEqual(e["pagina"], "index.html")

    def test_la_api_falsa_responde_lo_que_app_js_lee(self):
        # La declaración monta fetch con 'antes'. Se corre en Node con un window falso y se pregunta lo que app.js pregunta.
        estado = self.datos["estados"][0]
        # El sondeo de /api/estado entrega las filas una sola vez y solo cuando la tabla ya las pintó (#tr-2): así el
        # navegador no rehace los chips cada 0,8 s mientras el verificador los mide.
        guion = ("const window = {}; let hay = false;\n"
                 "const document = { querySelector: () => (hay ? {} : null) };\n" + estado["antes"] + ";\n"
                 "(async () => {\n"
                 "  const leer = async u => (await window.fetch(u)).json();\n"
                 "  const config = await leer('/api/config');\n"
                 "  const planilla = await leer('/api/planilla?nombre=x.xlsx');\n"
                 "  const filas = await leer('/api/filas?hoja=MAERSK');\n"
                 "  const antes = await leer('/api/estado?desde=0');\n"
                 "  hay = true;\n"
                 "  const sondeo = await leer('/api/estado?desde=0');\n"
                 "  const despues = await leer('/api/estado?desde=0');\n"
                 "  console.log(JSON.stringify({config, planilla, filas, antes, sondeo, despues}));\n"
                 "})();\n")
        r = correr_node(self, guion)
        # La nota del modo: app.js lee estas cuatro cosas de /api/config; el primer estado es el de prueba, sin emitir.
        self.assertIs(r["config"]["modo_emision"], False)
        self.assertEqual((type(r["config"]["usuarios"]), type(r["config"]["navieras"]), r["config"]["aviso"]),
                         (list, list, ""))
        self.assertTrue(r["config"]["version"])
        self.assertEqual(r["antes"]["resultados"], {})                  # sin la tabla pintada, nada
        self.assertEqual(r["despues"]["resultados"], {})                # y no se repite
        h = r["planilla"]["hojas"][0]
        self.assertEqual((h["hoja"], h["filas"], h["reservador"]), ("MAERSK", 3, True))
        filas = r["filas"]["filas"]
        self.assertEqual(len(filas), 3)
        for f in filas:
            self.assertIsInstance(f["fila"], int)
            for campo in ("pol", "destino_final", "nave", "viaje", "cotizacion"):
                self.assertIn(campo, f)
        # Los estados de cada fila, tal como los lee lecturaEstado: en curso, emitida y enviada para revisar.
        resultados = r["sondeo"]["resultados"]
        self.assertEqual(sorted(resultados, key=int), [str(f["fila"]) for f in filas])
        self.assertEqual([resultados[str(f["fila"])]["estado"] for f in filas],
                         ["EN CURSO", "EMITIDA", "ENVIADA – REVISAR EN PORTAL"])
        self.assertIs(r["sondeo"]["corriendo"], True)

    def test_el_estado_de_emision_dice_que_la_emision_esta_abierta(self):
        # Mide la nota del panel en modo EMISIÓN (su título y su insignia), que solo se pinta si /api/config lo dice. Lo demás
        # lo deja pasar al fetch de verdad.
        estado = next(e for e in self.datos["estados"] if e["nombre"] == "modo-emision")
        guion = ("const window = { fetch: (u) => Promise.resolve({ json: async () => ({ paso: String(u) }) }) };\n"
                 + estado["antes"] + ";\n"
                 "(async () => {\n"
                 "  const config = await (await window.fetch('/api/config')).json();\n"
                 "  const otra = await (await window.fetch('/api/estado?desde=0')).json();\n"
                 "  console.log(JSON.stringify({config, otra}));\n"
                 "})();\n")
        r = correr_node(self, guion)
        self.assertIs(r["config"]["modo_emision"], True)
        self.assertEqual(r["otra"], {"paso": "/api/estado?desde=0"})

    def test_los_selectores_de_abierto_existen_en_el_panel(self):
        # Lo que declara 'abierto' tiene que poder existir: sus clases e id salen del HTML o de app.js.
        fuente = self.mod.HTML_INDEX + self.mod.JS_INDEX
        for e in self.datos["estados"]:
            abierto = e["abierto"] if isinstance(e["abierto"], list) else [e["abierto"]]
            for selector in abierto:
                for nombre in re.findall(r"[.#]([A-Za-z][\w-]*)", selector):
                    with self.subTest(estado=e["nombre"], selector=selector, nombre=nombre):
                        self.assertIn(nombre, fuente)


class TestExtractor(soporte.CasoAQ):
    def test_arma_el_panel_como_archivos(self):
        destino = self.sb / "panel_extraido"
        rc, out, err = soporte.hijo([sys.executable, str(MARCA / "extraer_panel.py"), str(destino), str(soporte.FUENTES)],
                                    self.sb, timeout=120)
        self.assertEqual(rc, 0, err[-600:] + out[-600:])
        for nombre in ("index.html", "estilo.css", "app.js", "fuentes.css", "aquashield-estados.json", "muestra.xlsx"):
            with self.subTest(archivo=nombre):
                self.assertTrue((destino / nombre).is_file())
        self.assertEqual((destino / "app.js").read_bytes(), self.mod.JS_INDEX.encode("utf-8"))
        self.assertEqual((destino / "estilo.css").read_bytes(), self.mod.CSS_INDEX.encode("utf-8"))
        # Las rutas de la raíz del servidor pasan a relativas, y las letras salen a archivos.
        html = (destino / "index.html").read_text(encoding="utf-8")
        for ruta in ('href="fuentes.css"', 'href="estilo.css"', 'src="app.js"'):
            self.assertIn(ruta, html)
        self.assertGreaterEqual(len(list((destino / "fuentes").glob("*.woff2"))), 5)
        self.assertNotIn("base64", (destino / "fuentes.css").read_text(encoding="utf-8"))
        self.assertEqual((destino / "aquashield-estados.json").read_bytes(), (MARCA / "aquashield-estados.json").read_bytes())
        self.assertTrue((destino / ".git").is_dir())

    def test_con_git_dir_puesto_no_toca_ese_repo(self):
        # Revisión de seguridad del encargo 84: con GIT_DIR en el entorno (git lo exporta a todo hook), `git init` reinicializaba
        # el repo de GIT_DIR (lo dejaba bare y le ponía la identidad de la copia) en vez de armar el destino.
        juguete = self.sb / "juguete"
        git = ["git", "-c", "core.hooksPath=NUL"]
        for args in (["init", "-q", str(juguete)], ["-C", str(juguete), "config", "user.email", "juguete@example.invalid"],
                     ["-C", str(juguete), "config", "user.name", "juguete"]):
            rc, out, err = soporte.hijo(git + args, self.sb)
            self.assertEqual(rc, 0, err)
        destino = self.sb / "panel_con_git_dir"
        rc, out, err = soporte.hijo([sys.executable, str(MARCA / "extraer_panel.py"), str(destino), str(soporte.FUENTES)], self.sb,
                                    timeout=120, env_extra={"GIT_DIR": str(juguete / ".git"),
                                                            "GIT_INDEX_FILE": str(juguete / ".git" / "index")})
        self.assertEqual(rc, 0, err[-600:] + out[-600:])
        self.assertTrue((destino / ".git").is_dir())
        for clave, esperado in (("core.bare", "false"), ("user.email", "juguete@example.invalid"), ("user.name", "juguete")):
            with self.subTest(clave=clave):
                rc, out, err = soporte.hijo(git + ["-C", str(juguete), "config", "--get", clave], self.sb)
                self.assertEqual((rc, out.strip()), (0, esperado), err)

    def test_aborta_si_el_programa_no_trae_el_header_del_bloque(self):
        # Control positivo: un AQUASHIELD.py sin el header del bloque no se extrae como si estuviera bien.
        falso = self.sb / "falso"
        falso.mkdir()
        (falso / "AQUASHIELD.py").write_text('HTML_INDEX = "x"\nJS_INDEX = "x"\nCSS_INDEX = "x"\nCSS_FUENTES = "x"\n',
                                             encoding="utf-8")
        rc, out, err = soporte.hijo([sys.executable, str(MARCA / "extraer_panel.py"), str(self.sb / "no_sale"), str(falso)],
                                    self.sb, timeout=60)
        self.assertNotEqual(rc, 0)
        self.assertIn("ABORTA", err + out)
        self.assertFalse((self.sb / "no_sale").exists())


if __name__ == "__main__":
    unittest.main()
