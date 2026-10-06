# -*- coding: utf-8 -*-
"""CMA-CGM se detiene, sin reintentar ni recargar, cuando su portal restringe el acceso o su página no termina de cargar
(decisión de Marcelo, encargo 54, CICLO-cma-acceso-restringido.md).

Lo que se fotografía: qué muestra DataDome (_cma_datadome), leído solo con plazo; la espera de su verificación o de su
página vacía, hasta CMA_ESPERA_PORTADA s, con un reloj falso; la detención (_cma_detener: la línea, la captura y el
HTML con plazo, sin las credenciales, el motivo en el Registro y CmaDetenida); y lo que hacen con ella el login y el
reservador de CMA. Las páginas son falsas, con las frases que el OCR leyó en las capturas de DataDome de logs/ (sin IP
ni ID) y relleno inventado; ninguna prueba abre un navegador ni toca un portal.
"""
import ast
import types
import unittest
from pathlib import Path
from unittest import mock

import soporte

CAPTCHA = "https://geo.captcha-delivery.com/captcha/?t=fe&cid=inventado"
VERIFICA = "https://geo.captcha-delivery.com/interstitial/?cid=inventado"
PORTADA = "https://www.cma-cgm.com/"
# Las frases que el OCR leyó en las capturas (lo medido, arriba de CMA_TEXTO_BLOQUEO), con relleno inventado. El
# deslizador trae también «El bloqueo actual puede ser…», como el acceso restringido.
BLOQUEO = "CMA CGM\nEl acceso está restringido temporalmente\nEl bloqueo actual puede ser el resultado de otra cosa."
DESLIZADOR = ("CMA CGM\nNos aseguramos de que nos dirigimos a usted, y no a un robot.\nDesliza hacia la derecha para "
              "asegurar tu acceso\nEl bloqueo actual puede ser el resultado de otra cosa.")
VERIFICACION = "CMA CGM\nVerificación del dispositivo ...\nEl contenido solicitado estará disponible después."
CREDS = {"usuario": "usuario.inventado@ejemplo.invalid", "clave": "ClaveInventada-123"}


class Raiz:
    """locator(':root') falso de la página o de un marco: su evaluate y su inner_html, con plazo."""

    def __init__(self, alcance):
        self.alcance = alcance

    def evaluate(self, js, arg=None, timeout=None):
        return self.alcance.con_plazo(js, timeout)

    def inner_html(self, timeout=None):
        return self.alcance.con_plazo("innerHTML", timeout)


class Alcance:
    """La página o un marco, falsos. Lo que se lee con plazo (Raiz) responde según una marca del JavaScript: el código
    HTTP (responseStatus), el HTML (getHTML) o el texto (innerText); si 'responde' es False, levanta el TimeoutError de
    Playwright, como el marco ocupado medido en Chrome (medir_instrumento.py del encargo 54). Lo que se lee sin plazo
    (evaluate, title, content) responde igual, pero lo anota en 'sin_plazo' de la página."""

    def __init__(self, pagina, url, texto="", http=None, responde=True):
        self.pagina, self.url, self.texto, self.http, self.responde = pagina, url, texto, http, responde

    def locator(self, sel):
        self.pagina.selectores.append(sel)
        return Raiz(self)

    def _responder(self, js):
        if "responseStatus" in js:
            return self.http
        if "getHTML" in js:
            return {"html": f"<!DOCTYPE html>\n<html><body>{self.texto}</body></html>", "sombras": 0}
        if "innerHTML" in js:
            return f"<body>{self.texto}</body>"
        if "querySelector('iframe" in js:
            return False
        if "innerText" in js:
            return self.texto
        return None

    def con_plazo(self, js, timeout):
        self.pagina.plazos.append(timeout)
        if not self.responde:
            raise self.pagina.mod.PWTimeout(f"Locator.evaluate: Timeout {timeout}ms exceeded.")
        return self._responder(js)

    def evaluate(self, js, *a):
        self.pagina.sin_plazo.append(("evaluate", self.url, js[:30]))
        return self._responder(js)

    def title(self):
        self.pagina.sin_plazo.append(("title", self.url))
        return ""

    def content(self):
        self.pagina.sin_plazo.append(("content", self.url))
        return f"<html><body>{self.texto}</body></html>"


class PaginaDataDome:
    """Página falsa de CMA-CGM: una secuencia de estados (el código HTTP del documento, su texto y sus marcos, cada uno
    (dirección, texto, responde)); cada espera (wait_for_timeout) adelanta el reloj falso y pasa al estado siguiente, y
    el último se queda. Anota las esperas, las capturas con su plazo, los plazos de cada lectura, lo leído sin plazo y
    las navegaciones; no tiene recarga, clics ni teclado: si el programa los usara, la prueba caería. Más de TOPE
    esperas también la hacen caer: el programa seguía esperando (la espera del deslizador cuenta con el reloj de
    verdad, hasta 180 s)."""
    TOPE = 100

    def __init__(self, mod, estados, reloj=None, goto=None):
        self.mod, self.estados, self.reloj, self.i = mod, list(estados), reloj, 0
        self.esperas, self.capturas, self.plazos, self.sin_plazo, self.visitas, self.selectores = [], [], [], [], [], []
        self.al_navegar = goto
        self._alcances = {}

    def _de_este_estado(self):
        k = min(self.i, len(self.estados) - 1)
        if k not in self._alcances:
            e = self.estados[k]
            principal = Alcance(self, e.get("url", PORTADA), e.get("texto", ""), e.get("http"))
            marcos = [Alcance(self, u, t, responde=r) for u, t, r in e.get("marcos", ())]
            self._alcances[k] = (principal, marcos)
        return self._alcances[k]

    @property
    def main_frame(self):
        return self._de_este_estado()[0]

    @property
    def frames(self):
        principal, marcos = self._de_este_estado()
        return [principal] + marcos

    @property
    def url(self):
        return self.main_frame.url

    def locator(self, sel):
        return self.main_frame.locator(sel)

    def evaluate(self, js, *a):
        return self.main_frame.evaluate(js, *a)

    def title(self):
        return self.main_frame.title()

    def content(self):
        return self.main_frame.content()

    def goto(self, url, **k):
        self.visitas.append((url, k))
        if self.al_navegar:
            self.al_navegar(url, k)

    def wait_for_timeout(self, ms):
        self.esperas.append(ms)
        if len(self.esperas) > self.TOPE:
            raise AssertionError(f"la página siguió esperando: {len(self.esperas)} esperas")
        if self.reloj:
            self.reloj.t += ms / 1000
        self.i += 1

    def bring_to_front(self):
        pass

    def screenshot(self, path=None, full_page=False, timeout=None):
        self.capturas.append((Path(path).name, timeout))
        Path(path).write_bytes(b"")


def estado(http=403, texto="", marcos=(), url=PORTADA):
    return {"http": http, "texto": texto, "marcos": list(marcos), "url": url}


BLOQUEADA = estado(marcos=[(CAPTCHA, BLOQUEO, True)])
CON_DESLIZADOR = estado(marcos=[(CAPTCHA, DESLIZADOR, True)])
VERIFICANDO = estado(marcos=[(VERIFICA, VERIFICACION, True)])
VACIA = estado()
NORMAL = estado(http=200, texto="My CMA CGM\nportada inventada")


class Reloj:
    """El time del programa, con el reloj detenido: solo avanza con las esperas de la página falsa."""

    def __init__(self):
        self.t = 1000.0

    def time(self):
        return self.t


class ConCorrida(soporte.CasoAQ):
    def corrida(self, nombre):
        vistas = []
        reg = self.mod.Registro(self.sb / nombre / "log.txt", on_log=vistas.append)
        self.addCleanup(reg.cerrar)
        return reg, vistas, self.sb / nombre

    def motivo(self, causa):
        return self.mod.CMA_DETENIDA.format(causa=causa)

    def sin_cargar(self, que):
        return self.motivo(self.mod.CMA_SIN_CARGAR.format(seg=self.mod.CMA_ESPERA_PORTADA, que=que))


class TestLoQueMuestraDataDome(ConCorrida):
    def test_reconoce_cada_pagina_medida(self):
        casos = {
            "bloqueo": [BLOQUEADA,
                        estado(marcos=[(CAPTCHA, "EL ACCESO ESTÁ RESTRINGIDO\n   TEMPORALMENTE", True)])],
            # El deslizador trae «El bloqueo actual…»: no es el acceso restringido.
            "deslizador": [CON_DESLIZADOR],
            # La verificación del dispositivo, por su marco /interstitial/ (aunque no se lea) o por su texto.
            "verificacion": [VERIFICANDO, estado(marcos=[(VERIFICA, "", True)]),
                             estado(marcos=[("https://otro.ejemplo.invalid/x", VERIFICACION, True)])],
            # Un 403 sin el marco de DataDome (así quedó a las 14:26:44 del 06-10), o su marco sin texto o sin
            # responder.
            "vacia": [VACIA, estado(texto="Please enable JS"), estado(marcos=[(CAPTCHA, "", True)]),
                      estado(marcos=[(CAPTCHA, BLOQUEO, False)])],
            "otra": [estado(marcos=[(CAPTCHA, "Texto inventado de otra página", True)])],
            "": [NORMAL, estado(http=200, marcos=[("https://otro.ejemplo.invalid/x", "relleno", True)]),
                 estado(http=None), estado(http=200, marcos=[("https://otro.ejemplo.invalid/x", "", False)])],
        }
        for esperado, estados in casos.items():
            for k, e in enumerate(estados):
                with self.subTest(esperado=esperado, caso=k):
                    self.assertEqual(self.mod._cma_datadome(PaginaDataDome(self.mod, [e])), esperado)

    def test_lee_solo_con_plazo(self):
        # Cada lectura, con un localizador de su documento y el plazo de CMA_LECTURA_MS: frame.evaluate no tiene plazo,
        # y en un marco que no responde no vuelve (medido en Chrome: más de 40 s; con plazo, 1,5 s).
        for e in (BLOQUEADA, VERIFICANDO, VACIA, NORMAL):
            with self.subTest(e=e["marcos"][:1] or e["http"]):
                pagina = PaginaDataDome(self.mod, [e])
                self.mod._cma_datadome(pagina)
                self.assertEqual((pagina.sin_plazo, set(pagina.selectores)), ([], {":root"}))
                self.assertEqual(set(pagina.plazos), {self.mod.CMA_LECTURA_MS})

    def test_codigo_http_solo_entero(self):
        for http, esperado in ((403, 403), (200, 200), ("403", None), (True, None), (None, None)):
            with self.subTest(http=http):
                self.assertEqual(self.mod._cma_http(PaginaDataDome(self.mod, [estado(http=http)])), esperado)
        self.assertIsNone(self.mod._cma_http(soporte.PaginaFalsa()))        # sin locator: no se puede leer

    def test_robotcheck_con_403_sin_leer_los_marcos(self):
        # Un documento 403, aunque esté vacío, es de DataDome, y basta con eso: los marcos no se leen sin plazo.
        pagina = PaginaDataDome(self.mod, [VACIA])
        self.assertIs(self.mod._cma_es_robotcheck(pagina), True)
        self.assertEqual(pagina.sin_plazo, [])
        self.assertIs(self.mod._cma_es_robotcheck(PaginaDataDome(self.mod, [NORMAL])), False)

    def test_lo_medido(self):
        # Las frases que el OCR leyó en las 11 capturas de DataDome de logs/, y los plazos: CMA_ESPERA_PORTADA, unas 8
        # veces lo más largo que tardó la portada en los 23 inicios de sesión de logs/ (3,7 s); cada lectura, de 0,01
        # a 0,15 s en Chrome; la captura, de 0,1 a 0,2 s.
        m = self.mod
        self.assertEqual((m.CMA_TEXTO_BLOQUEO, m.CMA_TEXTO_DESLIZADOR, m.CMA_TEXTO_VERIFICACION),
                         ("restringido temporalmente", "desliza hacia la derecha", "verificación del dispositivo"))
        self.assertEqual((m.CMA_ESPERA_PORTADA, m.CMA_LECTURA_MS, m.CMA_CAPTURA_MS), (30, 1500, 5000))


class TestCmaSeDetiene(ConCorrida):
    def esperar_desafio(self, nombre, estados, reloj=None):
        """Corre _cma_esperar_desafio de verdad sobre la página falsa. Devuelve (resultado o la CmaDetenida, la página,
        las pausas pedidas, lo que se vio, la carpeta de la corrida)."""
        reloj = reloj or Reloj()
        pagina = PaginaDataDome(self.mod, estados, reloj)
        pausas = []
        with mock.patch.object(self.mod, "time", reloj), mock.patch("winsound.MessageBeep"):
            reg, vistas, carpeta = self.corrida(nombre)
            try:
                r = self.mod._cma_esperar_desafio(pagina, reg, pausas.append, creds=CREDS)
            except self.mod.CmaDetenida as e:
                r = e
        return r, pagina, pausas, vistas, carpeta, reg

    def test_bloqueo_se_detiene_enseguida(self):
        r, pagina, pausas, vistas, carpeta, reg = self.esperar_desafio("bloqueo", [BLOQUEADA])
        motivo = self.motivo(self.mod.CMA_ACCESO_RESTRINGIDO)
        self.assertIsInstance(r, self.mod.CmaDetenida)
        self.assertEqual((r.motivo, self.mod._naviera_detenida(reg, "cma")), (motivo, motivo))
        # Sin pedirle nada al operador, sin esperar, sin navegar ni recargar.
        self.assertEqual((pausas, pagina.esperas, pagina.visitas), ([], [], []))
        self.assertEqual(pagina.capturas, [("cma_acceso_restringido.png", self.mod.CMA_CAPTURA_MS)])
        self.assertEqual(sorted(a.name for a in carpeta.iterdir() if a.suffix == ".html"),
                         ["cma_acceso_restringido.html", "cma_acceso_restringido_marco1.html"])
        texto = "\n".join(vistas)
        self.assertIn("· ⛔ CMA-CGM restringió el acceso: su página dice «El acceso está restringido temporalmente». "
                      "Me detengo sin reintentar ni recargar la página.", texto)
        self.assertIn("evidencia de CMA-CGM detenida: cma_acceso_restringido.png y 2 de 2 HTML (la página y 1 "
                      "marco(s))", texto)
        self.assertNotIn("Desliza hacia la derecha", texto)

    def test_verificacion_que_no_termina_se_detiene_al_plazo(self):
        r, pagina, pausas, vistas, _, _ = self.esperar_desafio("verificacion_sin_fin", [VERIFICANDO])
        self.assertEqual(r.motivo, self.sin_cargar("DataDome no terminó de verificar el navegador"))
        # Una espera de 1 s por vuelta, hasta el plazo, contado desde que la vio; y ningún pedido al operador.
        self.assertEqual((pagina.esperas, pausas), ([1000] * self.mod.CMA_ESPERA_PORTADA, []))
        self.assertEqual(pagina.capturas, [("cma_verificacion.png", self.mod.CMA_CAPTURA_MS),
                                           ("cma_sin_cargar.png", self.mod.CMA_CAPTURA_MS)])
        self.assertIn(f"· CMA CGM muestra la verificación del navegador de DataDome, o una página vacía: espero hasta "
                      f"{self.mod.CMA_ESPERA_PORTADA} s a que termine de cargar, sin tocar nada.", "\n".join(vistas))

    def test_pagina_vacia_se_detiene_al_plazo(self):
        # Como a las 14:26 del 06-10: la verificación, a los 5 s la página recargada, 403 y sin su marco, y así sigue.
        r, pagina, pausas, _, _, _ = self.esperar_desafio("vacia", [VERIFICANDO] * 5 + [VACIA])
        self.assertEqual(r.motivo, self.sin_cargar("la página de DataDome quedó vacía"))
        self.assertEqual((len(pagina.esperas), pausas, pagina.visitas), (self.mod.CMA_ESPERA_PORTADA, [], []))

    def test_verificacion_que_termina_sigue(self):
        r, pagina, pausas, vistas, carpeta, reg = self.esperar_desafio("verificacion_pasa",
                                                                        [VERIFICANDO, VERIFICANDO, NORMAL])
        self.assertIs(r, True)
        self.assertEqual((pagina.esperas, pausas, self.mod._naviera_detenida(reg, "cma")), ([1000, 1000], [], ""))
        self.assertIn("· DataDome dejó pasar la página; sigo.", "\n".join(vistas))
        self.assertEqual(pagina.capturas, [("cma_verificacion.png", self.mod.CMA_CAPTURA_MS)])

    def test_verificacion_que_pasa_al_deslizador_lo_pide_al_operador(self):
        # El deslizador lo sigue pasando el operador, como antes (decisión de Marcelo): la pausa, y la espera hasta que
        # DataDome deja pasar.
        r, pagina, pausas, vistas, _, _ = self.esperar_desafio("al_deslizador", [VERIFICANDO, CON_DESLIZADOR, NORMAL])
        self.assertIs(r, True)
        self.assertEqual(pausas, ["CMA CGM: desliza la flecha hacia la derecha en el navegador para continuar."])
        self.assertIn("· Verificación de CMA CGM superada ✓; continúo automáticamente.", "\n".join(vistas))

    def test_deslizador_como_antes(self):
        r, pagina, pausas, vistas, _, _ = self.esperar_desafio("deslizador", [CON_DESLIZADOR, NORMAL])
        self.assertIs(r, True)
        self.assertEqual((len(pausas), pagina.capturas), (1, [("cma_robot_desafio.png", None)]))
        self.assertIn("· CMA CGM muestra verificación de seguridad (DataDome: 'Desliza hacia la derecha').",
                      "\n".join(vistas))

    def test_otra_pagina_de_datadome_va_al_operador(self):
        r, _, pausas, _, _, _ = self.esperar_desafio("otra", [estado(marcos=[(CAPTCHA, "Texto inventado", True)]),
                                                              NORMAL])
        self.assertEqual((r, len(pausas)), (True, 1))

    def test_lo_que_solo_ve_el_detector_viejo_va_al_operador(self):
        # Sin DataDome para el detector nuevo, pero con una señal del de antes (_cma_es_robotcheck: aquí, «not a robot»
        # en un marco), la espera sigue como antes: se la pide al operador, y no sigue sola.
        otra = estado(http=200, marcos=[("https://otro.ejemplo.invalid/x", "Please prove you are not a robot", True)])
        r, _, pausas, vistas, _, _ = self.esperar_desafio("detector_viejo", [otra, NORMAL])
        self.assertEqual((r, len(pausas)), (True, 1))
        self.assertNotIn("DataDome dejó pasar la página", "\n".join(vistas))

    def test_bloqueo_mientras_espera_al_operador(self):
        r, pagina, pausas, _, _, reg = self.esperar_desafio("bloqueo_en_la_espera", [CON_DESLIZADOR, BLOQUEADA])
        self.assertEqual((r.motivo, len(pausas)), (self.motivo(self.mod.CMA_ACCESO_RESTRINGIDO), 1))
        self.assertEqual(pagina.capturas[-1], ("cma_acceso_restringido.png", self.mod.CMA_CAPTURA_MS))

    def test_sin_datadome_sigue_sin_tocar_nada(self):
        r, pagina, pausas, vistas, _, _ = self.esperar_desafio("sin_datadome", [NORMAL])
        self.assertEqual((r, pagina.esperas, pagina.capturas, pausas, vistas), (True, [], [], [], []))

    def test_evidencia_sin_las_credenciales_y_con_plazo(self):
        # El HTML que trae el usuario o la clave no se escribe (como la evidencia del login de MSC), y el de un marco
        # que no responde se avisa como no guardado, sin el HTML de Playwright, que no tiene plazo.
        e = estado(texto=f"<p>{CREDS['usuario']}</p>", marcos=[(CAPTCHA, BLOQUEO, True),
                                                                ("https://otro.ejemplo.invalid/x", "", False)])
        r, pagina, _, vistas, carpeta, _ = self.esperar_desafio("evidencia", [e])
        self.assertIsInstance(r, self.mod.CmaDetenida)
        self.assertEqual(sorted(a.name for a in carpeta.iterdir() if a.suffix == ".html"),
                         ["cma_acceso_restringido_marco1.html"])
        self.assertEqual(pagina.sin_plazo, [])
        texto = "\n".join(vistas)
        self.assertIn("· ⚠ No guardé el HTML de la página con CMA-CGM detenida: trae el usuario o la clave de la "
                      "cuenta.", texto)
        self.assertIn("· ⚠ No pude guardar el HTML del marco 2 con CMA-CGM detenida: TimeoutError", texto)
        self.assertIn("1 de 3 HTML (la página y 2 marco(s))", texto)


class LoginFalla(Exception):
    pass


class TestLoginCma(ConCorrida):
    def login(self, nombre, estados, goto=None):
        pagina = PaginaDataDome(self.mod, estados, Reloj(), goto=goto)
        with mock.patch.object(self.mod, "time", pagina.reloj), mock.patch("winsound.MessageBeep"):
            reg, vistas, _ = self.corrida(nombre)
            r = self.mod.login_cma(pagina, CREDS, reg, on_pausa=lambda m: self.fail(f"pidió la pausa: {m}"))
        return r, pagina, vistas, reg

    def test_portada_que_no_responde_se_detiene(self):
        # La portada tiene CMA_ESPERA_PORTADA s; hasta el encargo 54, al vencer el plazo de Playwright, el login
        # terminaba con un error inesperado.
        def vence(url, k):
            raise self.mod.PWTimeout(f"Page.goto: Timeout {k.get('timeout')}ms exceeded.")
        r, pagina, vistas, reg = self.login("portada_muda", [estado(http=None, url="about:blank")], goto=vence)
        self.assertIs(r, False)
        self.assertEqual(pagina.visitas, [(PORTADA, {"wait_until": "domcontentloaded",
                                                     "timeout": self.mod.CMA_ESPERA_PORTADA * 1000})])
        self.assertEqual(self.mod._naviera_detenida(reg, "cma"), self.sin_cargar("la portada no respondió"))
        self.assertEqual((pagina.esperas, pagina.capturas), ([], [("cma_sin_cargar.png", self.mod.CMA_CAPTURA_MS)]))
        self.assertIn(f"· ⛔ La página de CMA-CGM no terminó de cargar en {self.mod.CMA_ESPERA_PORTADA} s (la portada "
                      f"no respondió). Me detengo sin reintentar ni recargar la página.", "\n".join(vistas))

    def test_bloqueo_en_la_portada_no_intenta_entrar(self):
        con_la_cuenta = dict(BLOQUEADA, texto=f"<p>{CREDS['usuario']}</p>")
        r, pagina, vistas, reg = self.login("portada_bloqueada", [con_la_cuenta])
        self.assertIs(r, False)
        self.assertEqual(self.mod._naviera_detenida(reg, "cma"), self.motivo(self.mod.CMA_ACCESO_RESTRINGIDO))
        # Una sola navegación, la de la portada; y ni el menú ni el botón de entrar.
        self.assertEqual([u for u, _ in pagina.visitas], [PORTADA])
        self.assertEqual([x for x in pagina.sin_plazo if x[0] == "evaluate"], [])
        self.assertNotIn("Abriendo menú de acceso", "\n".join(vistas))
        # Sin el HTML de la página, que trae el usuario: el login le pasa sus credenciales a la evidencia.
        self.assertIn("· ⚠ No guardé el HTML de la página con CMA-CGM detenida", "\n".join(vistas))

    def test_otra_falla_del_login_sigue_como_antes(self):
        # El decorador ataja solo la detención: otra falla sale del login, como antes, y quien lo llama la anota.
        def falla(url, k):
            raise LoginFalla("falla inventada")
        with self.assertRaises(LoginFalla):
            self.login("otra_falla", [NORMAL], goto=falla)


class TestReservaCma(ConCorrida):
    RESERVA = {"fila": 9, "pol": "PUERTO ALFA, CHILE", "destino_orig": "PUERTO BETA", "destino_final": "PUERTO BETA",
               "nave": "NAVE PRUEBA UNO", "viaje": "", "dia_carga": "", "cotizacion": ""}

    def test_bloqueo_en_click_and_book_queda_no_enviada_y_no_sigue(self):
        reg, vistas, _ = self.corrida("reserva_bloqueada")
        motivo = self.motivo(self.mod.CMA_ACCESO_RESTRINGIDO)
        pagina = PaginaDataDome(self.mod, [dict(BLOQUEADA, texto=f"<p>{CREDS['clave']}</p>")])
        r = self.mod.reservar_cma(pagina, dict(self.RESERVA), dict(CREDS), reg)
        # NO ENVIADA con el motivo, después de una sola navegación: no prueba el otro modo.
        self.assertEqual((r, len(pagina.visitas)), (("NO ENVIADA", motivo), 1))
        # La fila siguiente queda igual, sin tocar la página.
        otra = PaginaDataDome(self.mod, [NORMAL])
        self.assertEqual(self.mod.reservar_cma(otra, dict(self.RESERVA, fila=10), dict(CREDS), reg),
                         ("NO ENVIADA", motivo))
        self.assertEqual((otra.visitas, otra.plazos, otra.sin_plazo, otra.capturas), ([], [], [], []))
        self.assertEqual("\n".join(vistas).count(f"· ✗ NO ENVIADA · {motivo}"), 2)
        # Sin el HTML de la página, que trae la clave: la reserva le pasa sus credenciales a la evidencia.
        self.assertIn("· ⚠ No guardé el HTML de la página con CMA-CGM detenida", "\n".join(vistas))

    def test_lo_que_detiene_no_corre_despues_de_la_guarda(self):
        # Después de la guarda el envío pudo haber salido: ahí nada puede terminar en NO ENVIADA.
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        detienen = {n for n, f in funcs.items() for s in ast.walk(f)
                    if isinstance(s, ast.Raise) and "CmaDetenida" in ast.unparse(s)}
        cambio = True
        while cambio:
            nuevos = {n for n, f in funcs.items() if n not in detienen and any(
                isinstance(c, ast.Call) and getattr(c.func, "id", "") in detienen for c in ast.walk(f))}
            detienen |= nuevos
            cambio = bool(nuevos)
        f = funcs["reservar_cma"]
        guarda = min(n.lineno for n in ast.walk(f)
                     if isinstance(n, ast.If) and "es_modo_emision" in ast.unparse(n.test))
        antes = sorted({c.func.id for c in ast.walk(f) if isinstance(c, ast.Call)
                        and getattr(c.func, "id", "") in detienen and c.lineno < guarda})
        despues = [c.func.id for c in ast.walk(f) if isinstance(c, ast.Call)
                   and getattr(c.func, "id", "") in detienen and c.lineno > guarda]
        self.assertEqual((antes, despues), (["_cma_esperar_desafio"], []))


if __name__ == "__main__":
    unittest.main()
