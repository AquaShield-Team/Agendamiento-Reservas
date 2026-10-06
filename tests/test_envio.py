# -*- coding: utf-8 -*-
"""Después de la guarda del candado: el estado dice lo que el programa vio y cada envío deja
evidencia (CICLO-estado-tras-envio.md).

- EMITIDA solo con la confirmación y un número con la forma medida de la naviera.
- ENVIADA – REVISAR EN PORTAL: se pulsó (o el clic pudo salir) y no hubo confirmación.
- NO ENVIADA: el botón no se pulsó, o el portal marcó errores de validación (con los campos).
- La evidencia: la captura y el HTML de la página y de cada marco, en la carpeta de la corrida.
- El panel lee cada estado con lecturaEstado (JavaScript, se corre en Node).

Páginas falsas y números inventados con la forma medida: ningún portal, captura ni HTML real.
"""
import ast
import itertools
import json
import re
import shutil
import unittest
from pathlib import Path

import soporte

P = soporte.PaginaFalsa
N = itertools.count()
CONFIRMA_ONE = "Your booking has been successfully submitted!\nBooking Reference No.\nSCLG10000002\n"
REVISA = "Revisa en el portal si la reserva quedó creada y, si está, anota su número en la planilla."


class Pantalla(P):
    """Página falsa que distingue el JavaScript que se le pide: el HTML completo (evidencia) o el
    texto visible (número). Cuenta las lecturas del texto; no sabe hacer clics ni navegar."""

    def __init__(self, texto="", html="<body>pantalla</body>", frames=None, contenido="<body>de playwright</body>",
                 url="https://portal.invalid/confirmacion"):
        super().__init__(texto, url=url, frames=frames)
        self.html, self.contenido, self.lecturas = html, contenido, 0

    def evaluate(self, js, *a):
        if "getHTML" in js:
            if isinstance(self.html, Exception):
                raise self.html
            return {"html": self.html(self) if callable(self.html) else self.html, "sombras": 0}
        self.lecturas += 1
        return self.texto(js, *a) if callable(self.texto) else self.texto

    def content(self):
        if isinstance(self.contenido, Exception):
            raise self.contenido
        return self.contenido


class ConRegistro(soporte.CasoAQ):
    def corrida(self):
        carpeta = self.sb / f"corrida_{next(N)}"
        return carpeta, self.mod.Registro(carpeta / "log.txt")


class TestResultadoEnvio(ConRegistro):
    def envio(self, pagina, naviera="one", nombre="ONE", pulsado=True, boton="Submit", **kw):
        carpeta, reg = self.corrida()
        try:
            r = self.mod._resultado_envio(pagina, reg, naviera, nombre, "nav_f5_9_confirmado", boton, pulsado, **kw)
        finally:
            reg.cerrar()
        return r, carpeta, (carpeta / "log.txt").read_text(encoding="utf-8")

    def evidencia(self, carpeta):
        return sorted(p.name for p in carpeta.iterdir() if p.name != "log.txt")

    def test_emitida_solo_con_la_forma_medida(self):
        r, carpeta, log = self.envio(Pantalla(CONFIRMA_ONE))
        self.assertEqual(r, ("EMITIDA", "ONE emitida con éxito (Booking: SCLG10000002)"))
        self.assertIn("· 🎉 ONE: Reserva EMITIDA con éxito. Booking: SCLG10000002", log)
        self.assertEqual(self.evidencia(carpeta), ["nav_f5_9_confirmado.html", "nav_f5_9_confirmado.png"])

    def test_pulsado_sin_confirmacion_es_enviada(self):
        pagina = Pantalla("Booking Parties · Review Booking")
        r, carpeta, log = self.envio(pagina)
        detalle = ("ONE: se pulsó «Submit», pero la pantalla no mostró la confirmación con el número de reserva. "
                   + REVISA)
        self.assertEqual(r, ("ENVIADA – REVISAR EN PORTAL", detalle))
        self.assertIn(f"· ⚠ ENVIADA – REVISAR EN PORTAL · {detalle}", log)
        self.assertEqual(pagina.esperas, self.mod.BKG_ESPERA_SEG)          # esperó la confirmación
        self.assertEqual(self.evidencia(carpeta), ["nav_f5_9_confirmado.html", "nav_f5_9_confirmado.png"])

    def test_naviera_sin_forma_nunca_es_emitida(self):
        # CMA y COSCO no tienen forma medida: ni un número con forma de otra naviera las vuelve EMITIDA.
        pagina = Pantalla(CONFIRMA_ONE + "Booking reference: CMAFALSO01")
        r, _, _ = self.envio(pagina, naviera="cma", nombre="CMA", boton="Enviar el booking")
        self.assertEqual(r, ("ENVIADA – REVISAR EN PORTAL",
                             "CMA: se pulsó «Enviar el booking», pero el programa todavía no sabe reconocer la "
                             "confirmación de CMA. " + REVISA))
        self.assertEqual((pagina.lecturas, pagina.esperas), (0, 0))

    def test_no_pulsado_es_no_enviada(self):
        pagina = Pantalla(CONFIRMA_ONE)            # aunque la pantalla mostrara un número, no se lee
        r, carpeta, log = self.envio(pagina, pulsado=False)
        detalle = "ONE: no se pulsó «Submit» porque no estaba en la pantalla. La reserva no se envió."
        self.assertEqual(r, ("NO ENVIADA", detalle))
        self.assertIn(f"· ✗ NO ENVIADA · {detalle}", log)
        self.assertEqual((pagina.lecturas, pagina.esperas), (0, 0))
        self.assertEqual(self.evidencia(carpeta), ["nav_f5_9_confirmado.html", "nav_f5_9_confirmado.png"])

    def test_validacion_es_no_enviada_con_los_campos(self):
        pagina = Pantalla(CONFIRMA_ONE)
        r, _, log = self.envio(pagina, naviera="cosco", nombre="COSCO",
                               campos=["Gross Weight is required", "Temperature is required"])
        detalle = ("COSCO: el portal no aceptó el envío y marcó: «Gross Weight is required»; «Temperature is "
                   "required». La reserva no se envió; corrige esos datos y vuelve a correrla.")
        self.assertEqual(r, ("NO ENVIADA", detalle))
        self.assertIn(f"· ✗ NO ENVIADA · {detalle}", log)
        # Con una naviera medida y un número en pantalla, igual no se lee: el portal rechazó el envío.
        pagina = Pantalla(CONFIRMA_ONE)
        r, _, _ = self.envio(pagina, campos=["Gross Weight is required"])
        self.assertEqual((r[0], pagina.lecturas), ("NO ENVIADA", 0))
        muchos = [f"Campo {i} is required" for i in range(1, 13)]
        r, _, _ = self.envio(Pantalla(), naviera="cosco", nombre="COSCO", campos=muchos)
        self.assertIn("«Campo 10 is required» y 2 más. La reserva no se envió", r[1])
        self.assertNotIn("Campo 11", r[1])

    def test_error_del_portal_es_enviada(self):
        r, _, _ = self.envio(Pantalla(), naviera="cosco", nombre="COSCO", error_portal="Sistema ocupado")
        self.assertEqual(r, ("ENVIADA – REVISAR EN PORTAL",
                             "COSCO: se pulsó «Submit» y el portal mostró un error: «Sistema ocupado». " + REVISA))
        # Con una naviera medida y un número en pantalla, tampoco se lee: el portal mostró un error.
        pagina = Pantalla(CONFIRMA_ONE)
        r, _, _ = self.envio(pagina, error_portal="Sistema ocupado")
        self.assertEqual((r[0], pagina.lecturas), ("ENVIADA – REVISAR EN PORTAL", 0))

    def test_falla_del_programa_despues_de_pulsar(self):
        r, _, log = self.envio(Pantalla("cargando"), error=RuntimeError("se cerró\n la página"))
        self.assertEqual(r, ("ENVIADA – REVISAR EN PORTAL",
                             "ONE: se pulsó «Submit», pero después el programa falló (RuntimeError: se cerró la "
                             "página). " + REVISA))
        self.assertIn("falla del programa durante el envío: RuntimeError: se cerró la página", log)

    def test_falla_al_pulsar_pudo_salir(self):
        r, _, _ = self.envio(Pantalla("cargando"), pulsado=None, error=TimeoutError("30000 ms"))
        self.assertEqual(r, ("ENVIADA – REVISAR EN PORTAL",
                             "ONE: el programa falló al pulsar «Submit» (TimeoutError: 30000 ms) y el clic pudo "
                             "haber salido. " + REVISA))

    def test_falla_pero_la_confirmacion_esta(self):
        for pulsado in (True, None):
            with self.subTest(pulsado=pulsado):
                r, _, _ = self.envio(Pantalla(CONFIRMA_ONE), pulsado=pulsado, error=RuntimeError("x"))
                self.assertEqual(r, ("EMITIDA", "ONE emitida con éxito (Booking: SCLG10000002)"))

    def test_evidencia_despues_de_leer(self):
        # La evidencia muestra la pantalla sobre la que se decidió: la de después de esperar el número.
        pagina = Pantalla(lambda js, *a: CONFIRMA_ONE if pagina.lecturas >= 4 else "cargando",
                          html=lambda p: f"<p>lecturas={p.lecturas}</p>")
        r, carpeta, _ = self.envio(pagina)
        self.assertEqual(r[0], "EMITIDA")
        self.assertIn("<p>lecturas=4</p>", (carpeta / "nav_f5_9_confirmado.html").read_text(encoding="utf-8"))


class Marco(Pantalla):
    """Un marco de la página: se guarda igual que la página."""


class TestEvidencia(ConRegistro):
    def guardar(self, pagina):
        carpeta, reg = self.corrida()
        try:
            self.mod._guardar_evidencia(pagina, reg, "cosco_f5_6_confirmado")
        finally:
            reg.cerrar()
        return carpeta, (carpeta / "log.txt").read_text(encoding="utf-8")

    def leer(self, carpeta, nombre):
        return (carpeta / nombre).read_text(encoding="utf-8")

    def test_captura_y_html_de_la_pagina_y_los_marcos(self):
        pagina = Pantalla(html="<body>principal</body>",
                          frames=[Marco(html="<body>uno</body>", url="https://portal.invalid/m1"),
                                  Marco(html="<body>dos</body>", url="https://portal.invalid/m2")])
        carpeta, log = self.guardar(pagina)
        self.assertEqual(sorted(p.name for p in carpeta.iterdir()),
                         ["cosco_f5_6_confirmado.html", "cosco_f5_6_confirmado.png", "cosco_f5_6_confirmado_marco1.html",
                          "cosco_f5_6_confirmado_marco2.html", "log.txt"])
        self.assertEqual(self.leer(carpeta, "cosco_f5_6_confirmado.html"),
                         "<!-- página · https://portal.invalid/confirmacion -->\n<body>principal</body>")
        self.assertEqual(self.leer(carpeta, "cosco_f5_6_confirmado_marco2.html"),
                         "<!-- marco 2 · https://portal.invalid/m2 -->\n<body>dos</body>")
        self.assertEqual(pagina.capturas, [("cosco_f5_6_confirmado.png", False)])   # la ventana, no la página entera
        self.assertIn("evidencia del envío: cosco_f5_6_confirmado.png y 3 de 3 HTML (la página y 2 marco(s); "
                      "0 sin raíces shadow)", log)

    def test_sin_javascript_usa_el_html_de_playwright(self):
        carpeta, log = self.guardar(Pantalla(frames=[Marco(html=RuntimeError("marco sin permiso"))]))
        self.assertEqual(self.leer(carpeta, "cosco_f5_6_confirmado_marco1.html"),
                         "<!-- marco 1 · https://portal.invalid/confirmacion -->\n<body>de playwright</body>")
        self.assertIn("2 de 2 HTML (la página y 1 marco(s); 1 sin raíces shadow)", log)

    def test_un_html_que_falla_se_avisa_y_no_tapa_a_los_demas(self):
        roto = Marco(html=RuntimeError("marco cerrado"), contenido=RuntimeError("marco cerrado"))
        carpeta, log = self.guardar(Pantalla(frames=[roto, Marco(html="<body>dos</body>")]))
        self.assertIn("· ⚠ No pude guardar el HTML del marco 1 tras el envío: RuntimeError: marco cerrado", log)
        self.assertFalse((carpeta / "cosco_f5_6_confirmado_marco1.html").exists())
        self.assertIn("<body>dos</body>", self.leer(carpeta, "cosco_f5_6_confirmado_marco2.html"))
        self.assertIn("2 de 3 HTML", log)

    def test_no_repite_el_marco_principal(self):
        # En Playwright, page.frames empieza con el marco principal, que es la misma página.
        pagina = Pantalla(html="<body>principal</body>", frames=[Marco(html="<body>principal</body>"),
                                                                 Marco(html="<body>hijo</body>")])
        pagina.main_frame = pagina.frames[0]
        carpeta, log = self.guardar(pagina)
        self.assertIn("<body>hijo</body>", self.leer(carpeta, "cosco_f5_6_confirmado_marco1.html"))
        self.assertFalse((carpeta / "cosco_f5_6_confirmado_marco2.html").exists())
        self.assertIn("2 de 2 HTML (la página y 1 marco(s)", log)

    def test_el_javascript_trae_las_raices_shadow(self):
        # El JavaScript no corre offline: se fija su forma. Solo lee (ni clics ni navegación).
        js = self.mod._JS_HTML_COMPLETO
        self.assertIn("if (e.shadowRoot) { raices.push(e.shadowRoot); visitar(e.shadowRoot); }", js)
        self.assertIn("html.getHTML({shadowRoots: raices})", js)
        for accion in ("click(", "location", "submit(", "dispatchEvent"):
            self.assertNotIn(accion, js)


class Boton:
    def __init__(self, hay, visible):
        self.hay, self.visible, self.clics = hay, visible, 0

    def count(self):
        return self.hay

    def is_visible(self):
        return self.visible

    def click(self):
        self.clics += 1


class Alcance:
    def __init__(self, boton, js_pulsa=False):
        self.boton, self.js_pulsa, self.selectores, self.js = boton, js_pulsa, [], []

    def locator(self, selector):
        self.selectores.append(selector)
        return type("Loc", (), {"first": self.boton})()

    def evaluate(self, js, *a):
        self.js.append((js,) + a)
        return self.js_pulsa


class TestPulsarBoton(soporte.CasoAQ):
    def test_pulsa_el_boton_visible(self):
        a = Alcance(Boton(1, True), js_pulsa=True)
        self.assertIs(self.mod._pulsar_boton(a, "button:has-text('Submit')", "JS", "^submit$"), True)
        self.assertEqual((a.boton.clics, a.selectores, a.js), (1, ["button:has-text('Submit')"], []))

    def test_sin_boton_visible_usa_el_javascript(self):
        for hay, visible in ((0, False), (1, False)):
            for pulsa in (True, False):
                with self.subTest(hay=hay, pulsa=pulsa):
                    a = Alcance(Boton(hay, visible), js_pulsa=pulsa)
                    self.assertIs(self.mod._pulsar_boton(a, "sel", "JS", "^submit$"), pulsa)
                    self.assertEqual((a.boton.clics, a.js), (0, [("JS", "^submit$")]))
        a = Alcance(Boton(0, False), js_pulsa=1)
        self.assertIs(self.mod._pulsar_boton(a, "sel", "JS"), True)
        self.assertEqual(a.js, [("JS",)])

    def test_sin_boton_ni_javascript_no_pulsa(self):
        a = Alcance(Boton(1, False), js_pulsa=True)
        self.assertIs(self.mod._pulsar_boton(a, "sel"), False)
        self.assertEqual((a.boton.clics, a.js), (0, []))


def tras_la_guarda(mod, nombre, tree=None):
    """Sentencias que corren después de la guarda del candado en el reservador 'nombre': la rama
    else de la guarda o, si no tiene, lo que la sigue en su bloque."""
    tree = tree or ast.parse(Path(mod.__file__).read_text(encoding="utf-8"))
    f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == nombre)
    for padre in ast.walk(f):
        for campo in ("body", "orelse"):
            cuerpo = getattr(padre, campo, None)
            for i, s in enumerate(cuerpo if isinstance(cuerpo, list) else []):
                if isinstance(s, ast.If) and ast.unparse(s.test) == "not es_modo_emision()":
                    return s.orelse or cuerpo[i + 1:]
    raise AssertionError(f"{nombre}: no encontré la guarda del candado")


def normal(fuente):
    return ast.unparse(ast.parse(fuente))


class TestReservadores(soporte.CasoAQ):
    """Después de la guarda, cada reservador pulsa el MISMO botón de antes (sin clics nuevos),
    guarda el error si algo falla y decide con _resultado_envio. El flujo en el portal no corre
    offline: se fija su forma. Lo de antes de la guarda lo vigila test_candado."""
    PROHIBIDOS = ("extraer_numero_booking", "_emitida(", "'EMITIDA'", "Consultar portal", "en proceso", "Ver captura",
                  "Pendiente", "reg.captura(")

    def envio(self, nombre, pulsar, resultado):
        post = tras_la_guarda(self.mod, nombre)
        fuente = "\n".join(ast.unparse(s) for s in post)
        self.assertIn("pulsado, error = (None, None)", fuente)
        intentos = [s for s in post if isinstance(s, ast.Try)]
        self.assertEqual(len(intentos), 1, f"{nombre}: se esperaba un solo try después de la guarda")
        asignaciones = [ast.unparse(n) for n in ast.walk(intentos[0]) if isinstance(n, ast.Assign)]
        self.assertIn(normal(f"pulsado = {pulsar}"), asignaciones)
        self.assertEqual([(ast.unparse(h.type), h.name, [ast.unparse(b) for b in h.body]) for h in intentos[0].handlers],
                         [("Exception", "e", ["error = e"])])
        self.assertEqual(ast.unparse(post[-1]), normal(f"return {resultado}"))
        for prohibido in self.PROHIBIDOS:
            self.assertNotIn(prohibido, fuente)
        return post

    def test_one_decide_con_lo_que_vio(self):
        self.envio("reservar_one",
                   """_pulsar_boton(page, "button:has-text('Submit'), button:has-text('Enviar'), button[type='submit']",
                                    _JS_CLICK_BTN, "^(submit|enviar|submit booking)$")""",
                   """_resultado_envio(page, reg, "one", "ONE", f"one_f{f}_11_confirmado", "Submit", pulsado, error)""")

    def test_msc_decide_con_lo_que_vio(self):
        self.envio("reservar_msc",
                   """_pulsar_boton(page, "button:has-text('Submit'), button[type='submit']", _JS_CLICK_BTN, "^(submit|enviar)$")""",
                   """_resultado_envio(page, reg, "msc", "MSC", f"msc_f{f}_6_confirmado", "Submit", pulsado, error)""")

    def test_hyundai_decide_con_lo_que_vio(self):
        post = self.envio("reservar_hyundai",
                          """_pulsar_boton(page, "button:has-text('Create NOW'), .btn:has-text('Create NOW')")""",
                          """_resultado_envio(page, reg, "hyundai", "HYUNDAI", f"hmm_f{f}_6_confirmado", "Create NOW",
                                              pulsado, error)""")
        # La ventana de confirmación de HMM se acepta igual que antes y solo si se pulsó «Create NOW».
        modal = "#confirmBtn, button:has-text('Confirm'), button:has-text('Yes'), button:has-text('Aceptar')"
        si_pulso = [n for s in post for n in ast.walk(s) if isinstance(n, ast.If) and ast.unparse(n.test) == "pulsado"]
        self.assertEqual(len(si_pulso), 1)
        self.assertIn(modal, ast.unparse(si_pulso[0]))
        self.assertEqual(sum(ast.unparse(s).count(modal) for s in post), 1)

    def test_maersk_decide_con_lo_que_vio(self):
        self.envio("reservar_maersk",
                   """_pulsar_boton(page, "button:has-text('Submit booking'), button:has-text('Book now')")""",
                   """_resultado_envio(page, reg, "maersk", "MAERSK", f"mk_f{f}_7_confirmado", "Submit booking",
                                       pulsado, error)""")

    def test_cma_decide_con_lo_que_vio(self):
        self.envio("reservar_cma",
                   """_pulsar_boton(page, "button:has-text('Enviar el booking'), button:has-text('Send booking'), "
                                          "button:has-text('Submit booking')")""",
                   """_resultado_envio(page, reg, "cma", "CMA", f"cma_f{f}_6_confirmado", "Enviar el booking", pulsado,
                                       error)""")
        self.assertNotIn("cma", self.mod.FORMA_BOOKING)       # sin forma medida: nunca EMITIDA

    def test_cosco_decide_con_lo_que_vio(self):
        post = self.envio("reservar_cosco",
                          """_pulsar_boton(frame, "button:has-text('Submit'), .btn:has-text('Submit')", _JS_COSCO_SUBMIT)""",
                          """_resultado_envio(page, reg, "cosco", "COSCO", f"cosco_f{f}_6_confirmado", "Submit", pulsado,
                                              error, campos=campos, error_portal=error_portal)""")
        condicionales = [ast.unparse(n) for s in post for n in ast.walk(s) if isinstance(n, ast.If)]
        # Solo espera el resultado si pulsó; con la ventana Reminder ya vista, los errores de campo
        # no bastan para NO ENVIADA: van como error del portal (ENVIADA – REVISAR EN PORTAL).
        self.assertIn(normal("if pulsado:\n    campos, error_portal, vio_reminder = "
                             "_cosco_esperar_resultado(page, frame, reg)"), condicionales)
        self.assertIn(normal("if campos and vio_reminder:\n"
                             "    error_portal = '; '.join(campos + ([error_portal] if error_portal else []))\n"
                             "    campos = []"), condicionales)
        self.assertNotIn("cosco", self.mod.FORMA_BOOKING)     # sin forma medida: nunca EMITIDA

    def test_la_evidencia_y_el_estado_solo_despues_de_la_guarda(self):
        # FRENA del encargo: guardar la evidencia no puede cambiar el flujo antes de la guarda.
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        despues = {nombre: {id(n) for s in tras_la_guarda(self.mod, nombre, tree) for n in ast.walk(s)}
                   for nombre in ("reservar_one", "reservar_msc", "reservar_cma", "reservar_cosco",
                                  "reservar_hyundai", "reservar_maersk")}
        llamadas = {}
        for f in (n for n in tree.body if isinstance(n, ast.FunctionDef)):
            for n in ast.walk(f):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in (
                        "_resultado_envio", "_guardar_evidencia", "_cosco_esperar_resultado", "_pulsar_boton"):
                    tras = f.name in despues and id(n) in despues[f.name]
                    llamadas.setdefault(n.func.id, []).append((f.name, tras))
        seis = sorted((n, True) for n in despues)
        self.assertEqual(sorted(llamadas["_resultado_envio"]), seis)
        self.assertEqual(sorted(llamadas["_pulsar_boton"]), seis)
        self.assertEqual(llamadas["_guardar_evidencia"], [("_resultado_envio", False)])
        self.assertEqual(llamadas["_cosco_esperar_resultado"], [("reservar_cosco", True)])


def correr_node(caso, guion):
    """Corre 'guion' en Node (fuera del navegador) y devuelve lo que imprimió, leído como JSON."""
    node = shutil.which("node")
    caso.assertTrue(node, "esta prueba corre JavaScript en Node y Node no está instalado")
    ruta = caso.sb / f"guion_{next(N)}.js"
    ruta.write_text(guion, encoding="utf-8")
    rc, out, err = soporte.hijo([node, str(ruta)], cwd=caso.sb)
    caso.assertEqual(rc, 0, err[-600:])
    return json.loads(out)


class Nada:
    """Localizador de Playwright que no encuentra nada."""
    last = property(lambda self: self)

    def count(self):
        return 0

    def is_visible(self):
        return False

    def all(self):
        return []


class AlcanceCOSCO:
    """El formulario (marco) o la página de COSCO después de Submit: cada JavaScript de la espera
    recibe la respuesta de su tipo; uno desconocido queda anotado y la prueba cae. Cuenta las esperas."""
    TIPOS = (("'ambiguo'", "submit_ventana"), ("submit below document", "reminder"), ("[class*=boat]", "carga"),
             ("el-form-item__error", "errores"), ("(?:Request", "numero"), ("submitted successfully", "exito"),
             ("return !!b;", "submit_presente"))

    def __init__(self, estado, **resp):
        self.estado, self.resp, self.esperas = estado, resp, 0

    def evaluate(self, js, *a):
        tipo = next((t for clave, t in self.TIPOS if clave in js), "desconocido")
        self.estado["vistos"].append(tipo)
        r = self.resp.get(tipo)
        return r(self.estado) if callable(r) else r

    def locator(self, selector):
        return Nada()

    def wait_for_timeout(self, ms):
        self.esperas += 1


class TestCosco(soporte.CasoAQ):
    """Lo nuevo de COSCO tras Submit: el JavaScript que dice si pulsó, el que separa los errores de
    validación del aviso del portal, y la espera, que devuelve lo que vio sin decidir el estado."""
    CAMPOS = "'.el-form-item__error'"
    AVISOS = "'.el-message--error, .el-alert--error, .el-notification--error'"

    def test_js_submit_dice_si_pulso(self):
        guion = ("const el = (t) => ({textContent: t, clics: 0, click() { this.clics++; }});\n"
                 "const correr = (els) => { global.document = {querySelectorAll: () => els};\n"
                 "  const f = " + self.mod._JS_COSCO_SUBMIT + ";\n  return [f(), els.map(e => e.clics)]; };\n"
                 "console.log(JSON.stringify([correr([el('Save'), el(' Submit '), el('Submit booking')]), "
                 "correr([el('Save')])]));\n")
        self.assertEqual(correr_node(self, guion), [[True, [0, 1, 0]], [False, [0]]])

    def test_js_errores_separa_campos_y_aviso(self):
        guion = ("const el = (t, v) => ({textContent: t, offsetParent: v ? {} : null});\n"
                 "const correr = (tabla) => { global.document = {querySelectorAll: (s) => tabla[s] || []};\n"
                 "  const f = " + self.mod._JS_COSCO_ERRORES + ";\n  return f(); };\n"
                 "console.log(JSON.stringify([\n"
                 "  correr({[" + self.CAMPOS + "]: [el('Gross Weight is required', true), "
                 "el('  Gross\\n  Weight is required ', true), el('Temperature is required', true), "
                 "el('Oculto is required', false), el('', true)],\n"
                 "          [" + self.AVISOS + "]: [el('Allocation needs further confirmation', true), "
                 "el('Sistema ocupado', true)]}),\n"
                 "  correr({})]));\n")
        self.assertEqual(correr_node(self, guion), [
            {"campos": ["Gross Weight is required", "Temperature is required"], "portal": "Sistema ocupado"},
            {"campos": [], "portal": ""}])

    def test_errores_de_los_dos_alcances(self):
        class A:
            def __init__(self, r):
                self.r = r

            def evaluate(self, js):
                if isinstance(self.r, Exception):
                    raise self.r
                return self.r
        marco = A({"campos": ["Gross Weight is required"], "portal": ""})
        pagina = A({"campos": ["Gross Weight is required", "Shipper is required"], "portal": "Sistema ocupado"})
        juntos = (["Gross Weight is required", "Shipper is required"], "Sistema ocupado")
        self.assertEqual(self.mod._cosco_errores(marco, pagina), juntos)
        self.assertEqual(self.mod._cosco_errores(A(RuntimeError("marco cerrado")), pagina), juntos)
        self.assertEqual(self.mod._cosco_errores(None, A({})), ([], ""))

    def esperar(self, **resp):
        estado = {"vistos": [], "clics": 0}
        marco, pagina = AlcanceCOSCO(estado, **resp), AlcanceCOSCO(estado)
        carpeta = self.sb / f"cosco_{next(N)}"
        reg = self.mod.Registro(carpeta / "log.txt")
        try:
            r = self.mod._cosco_esperar_resultado(pagina, marco, reg)
        finally:
            reg.cerrar()
        self.assertNotIn("desconocido", estado["vistos"], "la espera corrió un JavaScript que la prueba no conoce")
        return r, pagina.esperas, estado, (carpeta / "log.txt").read_text(encoding="utf-8")

    @staticmethod
    def pulsa(e):
        e["clics"] += 1
        return "pulsado"

    def test_espera_corta_con_errores_de_validacion(self):
        r, esperas, _, _ = self.esperar(errores={"campos": ["Gross Weight is required"], "portal": ""},
                                        submit_presente=True)
        self.assertEqual((r, esperas), ((["Gross Weight is required"], "", False), 2))

    def test_espera_corta_con_aviso_del_portal(self):
        r, esperas, _, _ = self.esperar(errores={"campos": [], "portal": "Sistema ocupado"}, submit_presente=True)
        self.assertEqual((r, esperas), (([], "Sistema ocupado", False), 2))

    def test_reminder_pulsa_su_submit_una_sola_vez(self):
        # Como en c4, la ventana sigue abierta después del clic (cinco vueltas); después, la señal de envío.
        r, esperas, estado, log = self.esperar(reminder=lambda e: e["vistos"].count("reminder") <= 5,
                                               submit_ventana=self.pulsa, exito=True)
        self.assertEqual((r, esperas, estado["clics"]), (([], "", True), 7, 1))
        self.assertIn("Ventana 'Reminder': pulsé una vez su Submit, el de la ventana (por su título y su texto).", log)

    def test_reminder_tardio_tambien_una_sola_vez(self):
        # La ventana aparece en la sexta vuelta y no se cierra: un clic, y después solo se espera hasta el plazo.
        r, esperas, estado, _ = self.esperar(reminder=lambda e: e["vistos"].count("reminder") > 10,
                                             submit_ventana=self.pulsa, submit_presente=True)
        self.assertEqual((r, esperas, estado["clics"]), (([], "", True), 120, 1))

    def test_reminder_ambiguo_no_pulsa(self):
        r, esperas, estado, log = self.esperar(reminder=True, submit_ventana="ambiguo")
        self.assertEqual((r, esperas, estado["clics"]), (([], "", True), 120, 0))
        aviso = "Ventana 'Reminder': no identifiqué su Submit sin ambigüedad (ambiguo, sin respuesta); no pulsé nada."
        self.assertEqual(log.count(aviso), 1)

    def test_espera_se_agota(self):
        # Sin nada en pantalla y con el Submit todavía visible: vueltas de 2 × 1,5 s hasta el plazo de 180 s.
        r, esperas, _, log = self.esperar(submit_presente=True)
        self.assertEqual((r, esperas), (([], "", False), 120))
        self.assertIn("Se cumplió el plazo de 180 s sin confirmación de COSCO.", log)

    def test_js_submit_del_reminder_solo_el_de_la_ventana(self):
        # La ventana medida en las capturas: título «Reminder», el texto y los botones «Submit» y «Back». El
        # formulario también tiene su «Submit», y va al final: el «último Submit» de la página es el suyo.
        guion = r"""
const nodo = (tag, texto, hijos = []) => {
  const n = {tag, texto, hijos, visible: true, clics: 0, parentElement: null};
  Object.defineProperty(n, 'children', {get() { return this.hijos; }});
  Object.defineProperty(n, 'textContent', {get() { return [this.texto, ...this.hijos.map(h => h.textContent)].join(' '); }});
  n.getClientRects = function () { return this.visible ? [{}] : []; };
  n.click = function () { this.clics++; };
  n.querySelectorAll = function (sel) {
    const tags = sel === '*' ? null : sel.split(',').map(s => s.trim());
    const out = [];
    const walk = (x) => { for (const h of x.hijos) { if (!tags || tags.includes(h.tag)) out.push(h); walk(h); } };
    walk(this);
    return out;
  };
  hijos.forEach(h => { h.parentElement = n; });
  return n;
};
const ocultar = (n) => { n.visible = false; n.hijos.forEach(ocultar); };
const TEXTO = 'To complete your booking request, please submit below document(s) before deadline:';
const ventana = (botones) => nodo('div', '', [nodo('div', 'Reminder'), nodo('div', TEXTO), nodo('div', '', botones)]);
const correr = (armar) => {
  const b = {};
  const body = armar(b);
  global.document = {body, querySelectorAll: (s) => body.querySelectorAll(s === 'body *' ? '*' : s)};
  const f = """ + self.mod._JS_COSCO_SUBMIT_DEL_REMINDER + r""";
  return [f(), Object.keys(b).sort().map(k => k + ':' + b[k].clics)];
};
console.log(JSON.stringify([
  correr(b => nodo('body', '', [ventana([b.submit = nodo('button', 'Submit'), b.back = nodo('button', 'Back')]),
                                nodo('form', '', [b.formulario = nodo('button', 'Submit')])])),
  correr(b => nodo('body', '', [ventana([nodo('button', '', [b.span = nodo('span', 'Submit')]), nodo('button', 'Back')]),
                                nodo('form', '', [b.formulario = nodo('button', 'Submit')])])),
  correr(b => nodo('body', '', [ventana([b.uno = nodo('button', 'Submit'), b.dos = nodo('button', 'Submit')]),
                                nodo('form', '', [b.formulario = nodo('button', 'Submit')])])),
  correr(b => { const v = ventana([b.submit = nodo('button', 'Submit')]); ocultar(v);
                return nodo('body', '', [v, nodo('form', '', [b.formulario = nodo('button', 'Submit')])]); }),
  correr(b => nodo('body', '', [nodo('div', '', [nodo('p', TEXTO), b.formulario = nodo('button', 'Submit')])])),
  correr(b => nodo('body', '', [ventana([b.back = nodo('button', 'Back')]),
                                nodo('form', '', [b.formulario = nodo('button', 'Submit')])])),
]));
"""
        self.assertEqual(correr_node(self, guion), [
            ["pulsado", ["back:0", "formulario:0", "submit:1"]],          # el de la ventana, no el último
            ["pulsado", ["formulario:0", "span:1"]],                      # el más interno que dice «Submit»
            ["ambiguo", ["dos:0", "formulario:0", "uno:0"]],              # dos en la ventana: nada
            ["sin-ventana", ["formulario:0", "submit:0"]],                # la ventana cerrada: nada
            ["sin-ventana", ["formulario:0"]],                            # el texto sin el título: nada
            ["sin-boton", ["back:0", "formulario:0"]]])                   # sin «Submit» en la ventana: nada


class TestLecturaDelPanel(soporte.CasoAQ):
    """El panel pinta cada fila según lecturaEstado. Se corre en Node, fuera del navegador."""

    def lecturas(self, estados):
        m = re.search(r"^function lecturaEstado\(est\) \{\n.*?\n\}\n", self.mod.JS_INDEX, re.S | re.M)
        self.assertIsNotNone(m, "no encontré lecturaEstado en JS_INDEX")
        guion = m.group(0) + f"console.log(JSON.stringify({json.dumps(estados)}.map(lecturaEstado)));\n"
        return dict(zip(estados, correr_node(self, guion)))

    def test_marca_por_defecto_tambien_las_filas_sin_nave(self):
        # Una fila sin nave va marcada, como las demás: queda NO ENVIADA con el motivo sin entrar al portal, y así llega a
        # log.txt y a la planilla. Solo las MANUAL quedan sin marcar. Hasta a198645, la fila con la nave vacía quedaba sin
        # marcar, con el aviso «esas se omiten», y no llegaba a la planilla (CICLO-solo-la-nave-pedida.md). Cuál es MANUAL
        # lo dice el programa (f.manual, de /api/filas): hasta f68ce6c el panel lo decidía por su cuenta con el texto de
        # la nave, y la última, sin f.manual, quedaba sin marcar (CICLO-cola-seis-items.md).
        js = self.mod.JS_INDEX
        m = re.search(r"^function marcadaPorDefecto\(f\) \{\n.*?\n\}\n", js, re.S | re.M)
        self.assertIsNotNone(m, "no encontré marcadaPorDefecto en JS_INDEX")
        filas = [{"nave": ""}, {"nave": "AUTO", "sin_nave": True}, {"nave": "NAVE UNO"},
                 {"nave": "reserva manual", "manual": True}, {}, {"nave": "MANUAL"}]
        guion = m.group(0) + f"console.log(JSON.stringify({json.dumps(filas)}.map(marcadaPorDefecto)));\n"
        self.assertEqual(correr_node(self, guion), [True, True, True, False, True, True])
        # La tabla y «Todas» marcan con ella, y la etiqueta y el aviso usan la regla del programa (f.sin_nave).
        for trozo in ('const chk = marcadaPorDefecto(f) ? "checked" : "";',
                      "c.checked = marcadaPorDefecto(FILAS[i]);",
                      "${f.sin_nave ? \"<span class='sin-nave'>sin nave</span> \" + esc(f.nave) : esc(f.nave)}",
                      "const sin = FILAS.filter(f => f.sin_nave).length;",
                      '" reserva(s) no traen una nave para reservar: quedan NO ENVIADA, sin entrar al portal. "'):
            with self.subTest(trozo=trozo):
                self.assertEqual(js.count(trozo), 1)
        self.assertNotIn("esas se omiten", js)

    def test_marca_y_cuenta_aparte_las_filas_sin_ruta(self):
        # La fila con nave y sin puerto de carga o sin destino se ve marcada antes de correr, en la celda que le falta,
        # y se cuenta aparte, como la fila sin nave (decisión de Marcelo, encargo 43, CICLO-maersk-elige-exacto.md; las
        # marcas, de /api/filas: test_web). Va marcada para correr, como las demás: queda NO ENVIADA con su motivo, sin
        # entrar al portal. Hasta ahí, el panel no la distinguía.
        js = self.mod.JS_INDEX
        m = re.search(r"^function marcadaPorDefecto\(f\) \{\n.*?\n\}\n", js, re.S | re.M)
        filas = [{"nave": "NAVE UNO", "sin_puerto": True}, {"nave": "NAVE UNO", "sin_destino": True}]
        guion = m.group(0) + f"console.log(JSON.stringify({json.dumps(filas)}.map(marcadaPorDefecto)));\n"
        self.assertEqual(correr_node(self, guion), [True, True])
        for trozo in ("${f.sin_puerto ? \"<span class='sin-ruta'>sin puerto de carga</span> \" + esc(f.pol) : "
                      "esc(f.pol)}",
                      "${f.sin_destino ? \"<span class='sin-ruta'>sin destino</span> \" + esc(f.destino_final)\n"
                      "                          : esc(f.destino_final)}",
                      "const sinRuta = FILAS.filter(f => f.sin_puerto || f.sin_destino).length;",
                      '" reserva(s) con nave no traen su puerto de carga o su destino: quedan NO ENVIADA, "'):
            with self.subTest(trozo=trozo):
                self.assertEqual(js.count(trozo), 1)
        self.assertIn(".sin-nave, .sin-ruta { color: var(--text-muted); font-style: italic; }", self.mod.CSS_INDEX)

    def test_lectura_de_cada_estado(self):
        # «OK-EJEMPLO» es «lista»: no se emitió. Hasta el encargo 34 era «emitida» (CICLO-one-y-maersk-eligen-la-nave.md).
        esperado = {"EN CURSO": "curso", "EMITIDA": "emitida", "OK-EJEMPLO": "lista", "DETENIDO": "detenido",
                    "NO ENVIADA": "no-enviada", "ENVIADA – REVISAR EN PORTAL": "revisar-portal",
                    "REVISAR": "revisar", "ERROR": "revisar", "SIN-CUPO": "sin-cupo", "": "otro",
                    "OTRO ESTADO": "otro"}
        self.assertEqual(self.lecturas(list(esperado)), esperado)

    def test_cada_lectura_nueva_pinta_su_fila(self):
        js = self.mod.JS_INDEX
        self.assertIn("const lectura = lecturaEstado(est);", js)
        # SIN-CUPO, desde el encargo 40: hasta ahí quedaba en «procesando…» (CICLO-maersk-busqueda-vacia.md).
        for lectura, texto in (("no-enviada", "no enviada"), ("revisar-portal", "revisar en portal"),
                               ("sin-cupo", "sin cupo")):
            with self.subTest(lectura=lectura):
                m = re.search(r'\} else if \(lectura === "%s"\) \{\n(.*?)\n        \} else if' % lectura, js, re.S)
                self.assertIsNotNone(m, f"el panel no tiene rama para {lectura}")
                bloque = m.group(1)
                self.assertIn(f'chip(f, "rev", "{texto}");', bloque)
                self.assertIn('if (tr) tr.classList.remove("fila-activa", "fila-emitida");', bloque)   # deja «en curso»
                self.assertIn(f'color:var(--danger)">{texto}</span>', bloque)                         # y «procesando…»

    def test_lista_para_emitir_no_es_emitida(self):
        # Con el candado cerrado, la OK-EJEMPLO no se emitió: su columna dice lo que dice la planilla (n_reserva, de
        # _texto_n_reserva), nunca «Confirmada», y la píldora y el estado final la cuentan aparte de las emitidas. Hasta el
        # encargo 34, «✓ Confirmada» y «N de M emitidas» (CICLO-one-y-maersk-eligen-la-nave.md).
        js = self.mod.JS_INDEX
        codigo = "\n".join(l for l in js.splitlines() if not l.strip().startswith("//"))    # el comentario lo nombra
        self.assertNotIn("Confirmada", codigo)
        m = re.search(r'\} else if \(lectura === "emitida" \|\| lectura === "lista"\) \{\n(.*?)\n        \} else if', js, re.S)
        self.assertIsNotNone(m, "el panel no pinta juntas la emitida y la lista")
        for trozo in ('chip(f, "ok", lista ? "ok (previa)" : "emitida");', "if (lista) totalListas++; else totalEmitidas++;",
                      '${esc(nres || "—")}</span>'):
            with self.subTest(trozo=trozo):
                self.assertIn(trozo, m.group(1))
        self.assertEqual(js.count('const nres = (typeof r === "object" && r) ? (r.n_reserva || "") : "";'), 1)
        for trozo in ("const cuenta = cuentaCorrida(totalEmitidas, totalListas, selCount);",
                      "estado(`Terminó: ${cuentaCorrida(totalEmitidas, totalListas, selCount)}`);"):
            with self.subTest(trozo=trozo):
                self.assertEqual(js.count(trozo), 1)
        f = re.search(r"^function cuentaCorrida\(emitidas, listas, total\) \{\n.*?\n\}\n", js, re.S | re.M)
        self.assertIsNotNone(f, "no encontré cuentaCorrida en JS_INDEX")
        casos = [[0, 3, 5], [2, 0, 5], [0, 0, 5], [1, 2, 5]]
        guion = f.group(0) + f"console.log(JSON.stringify({json.dumps(casos)}.map(c => cuentaCorrida(...c))));\n"
        self.assertEqual(correr_node(self, guion), ["3 de 5 listas para emitir", "2 de 5 emitidas", "0 de 5 emitidas",
                                                    "1 de 5 emitidas · 2 de 5 listas para emitir"])
        # El texto de la columna, de una sola fuente, el mismo de la planilla.
        t = self.mod._texto_n_reserva
        self.assertEqual([t({"estado": "EMITIDA", "detalle": "MSC emitida con éxito (Booking: EBKG20000001)"}),
                          t({"estado": "EMITIDA", "booking": "BKGFALSO12"}), t({"estado": "OK-EJEMPLO"}),
                          t({"estado": "EMITIDA"}), t({"estado": "NO ENVIADA"}), t({"estado": "OK-EJEMPLO", "booking": "X9"}),
                          t(None)],
                         ["EBKG20000001", "BKGFALSO12", "lista para emitir", "", "", "lista para emitir", ""])

    def aviso_de_modo(self, pagina, panel):
        """El aviso de la página que no arma las reservas: 'pagina', el modo que muestra (o None si no lo pudo leer);
        'panel', el que dijo el panel (o None si no dijo uno). Con los nombres de NOMBRE_DEL_MODO, los del programa."""
        n = self.mod.NOMBRE_DEL_MODO
        muestra = f"muestra el modo {n[pagina]}" if isinstance(pagina, bool) else "no muestra el modo del panel"
        esta = f"está en modo {n[panel]}" if isinstance(panel, bool) else "no dijo en qué modo está"
        return (f"No armé las reservas: esta página {muestra}, y el panel {esta}. Recarga la página (F5) para ver el "
                f"modo del panel, y vuelve a armarlas.")

    def test_el_panel_vuelve_a_leer_su_modo_antes_de_armar(self):
        # Decisión de Marcelo, encargo 52 (CICLO-puerto-libre-y-modo-al-armar.md): la página pinta su aviso de modo al
        # cargar (MODO_PAGINA); antes de armar, vuelve a leer el modo del panel (/api/config), y si no es el que
        # muestra, no corre y avisa que hay que recargarla. Tampoco corre si el panel no dice un modo (no contesta, o no
        # dice true ni false) o si la página no pudo leer el suyo. Se corre en Node, con api, feed y estado falsos.
        js = self.mod.JS_INDEX
        f = re.search(r"^async function mismoModo\(\) \{\n.*?\n\}\n", js, re.S | re.M)
        a = re.search(r"^function avisoDeModo\(pagina, panel\) \{\n.*?\n\}\n", js, re.S | re.M)
        self.assertIsNotNone(f, "no encontré mismoModo en JS_INDEX")
        self.assertIsNotNone(a, "no encontré avisoDeModo en JS_INDEX")
        casos = [[False, False], [True, True], [False, True], [True, False], [False, "error"], [None, False],
                 [None, "error"], [False, "false"], [True, None]]
        guion = ("let MODO_PAGINA = null, RESPUESTA = null, AVISOS = [], ESTADOS = [], RUTAS = [];\n"
                 "async function api(ruta) {\n"
                 "  RUTAS.push(ruta);\n"
                 "  if (RESPUESTA === 'error') throw new Error('sin respuesta');\n"
                 "  return { modo_emision: RESPUESTA };\n"
                 "}\n"
                 "function feed(t, c, e) { AVISOS.push([t, c, e]); }\n"
                 "function estado(t) { ESTADOS.push(t); }\n"
                 + f.group(0) + a.group(0) +
                 "(async () => {\n"
                 "  const salida = [];\n"
                 f"  for (const [pagina, panel] of {json.dumps(casos)}) {{\n"
                 "    MODO_PAGINA = pagina; RESPUESTA = panel; AVISOS = []; ESTADOS = []; RUTAS = [];\n"
                 "    salida.push([await mismoModo(), AVISOS, ESTADOS, RUTAS]);\n"
                 "  }\n"
                 "  console.log(JSON.stringify(salida));\n"
                 "})();\n")
        esperado = []
        for pagina, panel in casos:
            dijo = panel if isinstance(panel, bool) else None
            if isinstance(pagina, bool) and pagina is dijo:
                esperado.append([True, [], [], ["/api/config"]])
            else:
                esperado.append([False, [[self.aviso_de_modo(pagina, dijo), "f-alerta", "REVISAR"]],
                                 ["Recarga la página antes de armar"], ["/api/config"]])
        self.assertEqual(correr_node(self, guion), esperado)

    def test_armar_pregunta_el_modo_y_lo_manda(self):
        # El botón de armar pregunta el modo (mismoModo) antes de tocar la pantalla o el panel, y manda a /api/correr el
        # modo que muestra la página, que el panel vuelve a comparar con el suyo (test_web). MODO_PAGINA es el modo con
        # que la página pintó su aviso al cargar, y el aviso se pinta con él (encargo 52).
        js = self.mod.JS_INDEX
        for trozo in ("let MODO_PAGINA = null;", "MODO_PAGINA = Boolean(d.modo_emision);", "if (MODO_PAGINA) {",
                      "if (!(await mismoModo())) return;"):
            with self.subTest(trozo=trozo):
                self.assertEqual(js.count(trozo), 1)
        self.assertEqual(js.count("d.modo_emision"), 1)
        m = re.search(r'^\$\("#wg-armar"\)\.onclick = async \(\) => \{\n(.*?)\n\};\n', js, re.S | re.M)
        self.assertIsNotNone(m, "no encontré el botón de armar")
        boton = m.group(1)
        pregunta = boton.find("if (!(await mismoModo())) return;")
        self.assertGreater(pregunta, -1)
        for despues in ('$("#log").innerHTML = ""; CURSOR = 0;', 'chip(f, "curso", "en curso");',
                        'await api("/api/correr"'):
            with self.subTest(despues=despues):
                self.assertGreater(boton.find(despues), pregunta)
        self.assertIn('body: JSON.stringify({ hoja: HOJA_ACT, usuario: $("#usuario").value, filas, '
                      'modo: MODO_PAGINA })', boton)


if __name__ == "__main__":
    unittest.main()
