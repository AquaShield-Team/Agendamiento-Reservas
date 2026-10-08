# -*- coding: utf-8 -*-
"""CMA-CGM se detiene, sin reintentar ni recargar, cuando su portal restringe el acceso o su página no termina de cargar
(decisión de Marcelo, encargo 54, CICLO-cma-acceso-restringido.md); y desde el encargo 55
(CICLO-pausa-plazos-y-datadome.md), también a mitad de una reserva, con todas sus lecturas con plazo. Desde el encargo
56 (CICLO-pausa-sola-y-comentarios.md), la pausa del deslizador termina sola cuando DataDome deja pasar la página o la
bloquea, y «Detener» corta la espera.

Lo que se fotografía: qué muestra DataDome (_cma_datadome), leído solo con plazo; la espera de su verificación o de su
página vacía, hasta CMA_ESPERA_PORTADA s, con un reloj falso; la detención (_cma_detener: la línea, la captura y el
HTML con plazo, sin las credenciales, el motivo en el Registro y CmaDetenida); y lo que hacen con ella el login y el
reservador de CMA. Las páginas son falsas, con las frases que el OCR leyó en las capturas de DataDome de logs/ (sin IP
ni ID) y relleno inventado; ninguna prueba abre un navegador ni toca un portal.
"""
import ast
import threading
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


class NavegadorCerrado(Exception):
    """Lo que levanta Playwright con la página o el navegador cerrados: así terminaron en logs/ dos esperas del
    deslizador del 06-10 («Page.wait_for_timeout: Target page, context or browser has been closed»)."""


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

    def __init__(self, pagina, url, texto="", http=None, responde=True, titulo=""):
        self.pagina, self.url, self.texto, self.http, self.responde = pagina, url, texto, http, responde
        self.titulo = titulo

    def locator(self, sel):
        self.pagina.selectores.append(sel)
        return Raiz(self)

    def _responder(self, js):
        if js == "() => true":                 # la pregunta de si la página responde (_responde, encargo 55)
            return True
        if "responseStatus" in js:
            return self.http
        if js == "() => document.title":
            return self.titulo
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
        if self.pagina.cerrada:
            raise NavegadorCerrado("Locator.evaluate: Target page, context or browser has been closed")
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
    verdad, hasta 180 s). Desde el encargo 56, puede estar cerrada (sus lecturas fallan, como las de Playwright), y
    'al_esperar(pagina)' corre en cada espera, antes de pasar de estado (ahí el operador pulsa «Detener»)."""
    TOPE = 100

    def __init__(self, mod, estados, reloj=None, goto=None):
        self.mod, self.estados, self.reloj, self.i = mod, list(estados), reloj, 0
        self.esperas, self.capturas, self.plazos, self.sin_plazo, self.visitas, self.selectores = [], [], [], [], [], []
        self.al_navegar = goto
        self.cerrada, self.al_esperar = False, None
        self._alcances = {}

    def _de_este_estado(self):
        k = min(self.i, len(self.estados) - 1)
        if k not in self._alcances:
            e = self.estados[k]
            principal = Alcance(self, e.get("url", PORTADA), e.get("texto", ""), e.get("http"), e.get("responde", True),
                                e.get("titulo", ""))
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
        if self.al_esperar:
            self.al_esperar(self)
        self.i += 1

    def is_closed(self):
        return self.cerrada

    def bring_to_front(self):
        pass

    def screenshot(self, path=None, full_page=False, timeout=None):
        self.capturas.append((Path(path).name, timeout))
        Path(path).write_bytes(b"")


def estado(http=403, texto="", marcos=(), url=PORTADA, responde=True, titulo=""):
    return {"http": http, "texto": texto, "marcos": list(marcos), "url": url, "responde": responde, "titulo": titulo}


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

        def on_pausa(m, hasta=None):              # una pausa falsa que no dice cómo terminó (como la del Tkinter)
            pausas.append(m)

        with mock.patch.object(self.mod, "time", reloj), mock.patch("winsound.MessageBeep"):
            reg, vistas, carpeta = self.corrida(nombre)
            try:
                r = self.mod._cma_esperar_desafio(pagina, reg, on_pausa, creds=CREDS)
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
        # Desde el encargo 55, su captura con plazo, y la pausa en log.txt: cuándo empezó, por qué y cómo terminó
        # (aquí, una pausa falsa que no dice cómo).
        self.assertEqual((len(pausas), pagina.capturas), (1, [("cma_robot_desafio.png", self.mod.CMA_CAPTURA_MS)]))
        texto = "\n".join(vistas)
        self.assertIn("· CMA CGM muestra verificación de seguridad (DataDome: 'Desliza hacia la derecha').", texto)
        self.assertIn("· ⏸ PAUSA: espero al operador. Por qué: CMA CGM: desliza la flecha hacia la derecha en el "
                      "navegador para continuar.", texto)
        self.assertIn("· ▶ La pausa terminó a los 0 s.", texto)

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
        # Se detuvo al abrir el formulario, una sola vez, sin seguir a ningún paso (encargo 55: el decorador mira
        # DataDome cuando un paso se corta, y así taparía una detención que la reserva se tragara antes).
        self.assertEqual("\n".join(vistas).count("· ⛔ CMA-CGM restringió el acceso"), 1)
        self.assertNotIn("DataDome apareció a mitad de la reserva", "\n".join(vistas))
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
        detienen = {n for n, f in funcs.items() for s in ast.walk(f) if isinstance(s, ast.Raise)
                    and any(x in ast.unparse(s) for x in ("CmaDetenida", "CmaInterrumpida", "CmaCancelada"))}
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
        # Desde el encargo 55, también DataDome a mitad de la reserva y la fila interrumpida; desde el 56, «Detener» en
        # la espera del deslizador (CmaCancelada), que corre dentro de las dos primeras.
        self.assertTrue({"_cma_si_pulso_detener", "_cma_pedir_deslizador"} <= detienen)
        self.assertEqual((antes, despues), (["_cma_datadome_a_mitad", "_cma_esperar_desafio", "_cma_interrumpir"], []))


# --- Encargo 55: DataDome a mitad de una reserva, y toda lectura de las páginas de CMA-CGM con plazo ---
FORMULARIO_URL = "https://www.cma-cgm.com/ebusiness/shipment/request"


def en_el_formulario(*marcos):
    """Click & Book (200) con el desafío de DataDome encima, en su marco: así lo muestra su etiqueta cuando bloquea un
    pedido de la página (ajaxListenerPath, en las 60 páginas de CMA de logs/ que la traen)."""
    return estado(http=200, texto="Formulario inventado", marcos=marcos, url=FORMULARIO_URL)


FORMULARIO = en_el_formulario()
BLOQUEO_ENCIMA = en_el_formulario((CAPTCHA, BLOQUEO, True))
DESLIZADOR_ENCIMA = en_el_formulario((CAPTCHA, DESLIZADOR, True))
VERIFICANDO_ENCIMA = en_el_formulario((VERIFICA, VERIFICACION, True))
# Las lecturas de Playwright sin plazo (medido en Chrome, encargo 55: con la página ocupada, o con una navegación que no
# termina, no volvieron en más de 25 s), y los ayudantes comunes que CMA llama con plazo_ms.
SIN_PLAZO = {"evaluate", "title", "content", "count", "is_visible", "is_hidden", "evaluate_all", "evaluate_handle",
             "query_selector", "query_selector_all", "all_inner_texts", "all_text_contents", "element_handles",
             "bounding_box"}
CON_PLAZO_DE_CMA = {"_guardar_html_completo", "_evidencia_antes_de_la_guarda", "_evidencia_sin_sugerencia",
                    "click_si_existe", "_pulsar_boton", "_resultado_envio", "_guardar_evidencia", "_sin_clic_a_ciegas"}
ANTES_DE_REVISAR = "antes de quedar para revisar"


def arbol_y_funciones(mod):
    tree = ast.parse(Path(mod.__file__).read_text(encoding="utf-8"))
    return tree, {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


def lo_que_corre_en_cma(funcs):
    """Las funciones del módulo que corren desde login_cma y reservar_cma: las que llaman, transitivamente, y sus
    decoradores."""
    vistas, pendientes = set(), {"login_cma", "reservar_cma"}
    while pendientes:
        x = pendientes.pop()
        if x in vistas or x not in funcs:
            continue
        vistas.add(x)
        for c in ast.walk(funcs[x]):               # lo que llama, y lo que le pasa a otra para que lo llame
            if isinstance(c, ast.Call):
                pendientes |= {n.id for n in [c.func] + list(c.args) if isinstance(n, ast.Name) and n.id in funcs}
        pendientes |= {n.id for d in funcs[x].decorator_list for n in ast.walk(d) if isinstance(n, ast.Name)}
    return vistas


def linea_de_la_guarda(f):
    return min(n.lineno for n in ast.walk(f) if isinstance(n, ast.If) and "es_modo_emision" in ast.unparse(n.test))


class TestLecturasConPlazo(ConCorrida):
    """Toda lectura de las páginas de CMA-CGM tiene plazo, como las del encargo 54 (decisión de Marcelo, encargo 55)."""

    def test_el_argumento_va_envuelto(self):
        # El localizador le da primero su elemento al JavaScript: el argumento va en un envoltorio, con un salto de
        # línea antes del cierre (medido en Chrome: así vuelve con su valor, aunque el JavaScript termine en un
        # comentario).
        vistos = []

        class RaizQueAnota:
            def evaluate(self, js, *a, timeout=None):
                vistos.append((js, a, timeout))
                return 42

        class AlcanceQueAnota:
            def locator(self, sel):
                vistos.append(sel)
                return RaizQueAnota()

        f = self.mod._evaluar_con_plazo
        self.assertEqual([f(AlcanceQueAnota(), "(x) => x.n + 1", 1500, {"n": 41}),
                          f(AlcanceQueAnota(), "(x) => x", 1500, None),          # None también es un argumento
                          f(AlcanceQueAnota(), "() => 1", 1500)], [42] * 3)
        self.assertEqual(vistos, [":root", ("(_raiz, arg) => ((x) => x.n + 1\n)(arg)", ({"n": 41},), 1500),
                                  ":root", ("(_raiz, arg) => ((x) => x\n)(arg)", (None,), 1500),
                                  ":root", ("() => 1", (), 1500)])

    def test_cuenta_y_mira_solo_si_la_pagina_responde(self):
        # count() e is_visible() no tienen plazo: antes de cada una, la pregunta con plazo. Si la página no responde,
        # no las llama: 0 y False.
        class Localizador:
            def __init__(self):
                self.llamadas = []

            def count(self):
                self.llamadas.append("count")
                return 3

            def is_visible(self):
                self.llamadas.append("is_visible")
                return True

        for responde, esperado in ((True, (3, True, ["count", "is_visible"])), (False, (0, False, []))):
            with self.subTest(responde=responde):
                pagina = PaginaDataDome(self.mod, [estado(http=200, responde=responde)])
                loc = Localizador()
                self.assertEqual((self.mod._cma_cuantos(pagina, loc), self.mod._cma_se_ve(pagina, loc), loc.llamadas),
                                 esperado)
                self.assertEqual((pagina.plazos, pagina.sin_plazo), ([self.mod.CMA_PLAZO_MS] * 2, []))

    def test_el_detector_de_antes_lee_con_plazo(self):
        # _cma_es_robotcheck con un documento que no es 403: el título y el texto de cada marco y de la página, y el
        # marco de un desafío, todo con plazo. Hasta el encargo 55: frame.title, frame.evaluate, page.title y
        # page.evaluate, sin plazo; con un marco que no responde, no volvía.
        otro = "https://otro.ejemplo.invalid/x"
        casos = ((estado(http=200, texto="Bienvenido", marcos=[(otro, "relleno", True)]), False),
                 (estado(http=200, marcos=[(otro, "Please prove you are not a robot", True)]), True),
                 (estado(http=200, titulo="Verificación de seguridad"), True),
                 (estado(http=200, texto="Desliza la flecha"), True),
                 (estado(http=200, marcos=[(otro, "Please prove you are not a robot", False)]), False))
        for k, (e, esperado) in enumerate(casos):
            with self.subTest(caso=k):
                pagina = PaginaDataDome(self.mod, [e])
                self.assertIs(self.mod._cma_es_robotcheck(pagina), esperado)
                self.assertEqual((pagina.sin_plazo, set(pagina.plazos)), ([], {self.mod.CMA_LECTURA_MS}))

    def test_ninguna_lectura_de_cma_sin_plazo(self):
        # La foto de las lecturas sin plazo de Playwright en lo que corre desde login_cma y reservar_cma: quedan solo
        # detrás de la pregunta con plazo (_cma_cuantos, _cma_se_ve y _pulsar_boton con plazo_ms) y en la rama sin plazo
        # de los ayudantes comunes, que CMA llama con plazo_ms; y numero_tras_envio, que con CMA no lee (no tiene forma
        # medida). Un evaluate con timeout tiene plazo.
        _, funcs = arbol_y_funciones(self.mod)
        vistas = lo_que_corre_en_cma(funcs)
        sin = sorted({(n, c.func.attr) for n in vistas for c in ast.walk(funcs[n])
                      if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr in SIN_PLAZO
                      and not any(k.arg == "timeout" for k in c.keywords)
                      and not isinstance(c.func.value, ast.Constant)})
        self.assertEqual(sin, [("_cma_cuantos", "count"), ("_cma_se_ve", "is_visible"),
                               ("_guardar_html_completo", "content"), ("_guardar_html_completo", "evaluate"),
                               ("_pulsar_boton", "count"), ("_pulsar_boton", "evaluate"),
                               ("_pulsar_boton", "is_visible"), ("click_si_existe", "evaluate"),
                               ("numero_tras_envio", "evaluate")])
        self.assertNotIn("cma", self.mod.FORMA_BOOKING)
        self.assertNotIn("texto_pagina", vistas)
        # Cada llamada de CMA a esos ayudantes comunes, con plazo_ms.
        cma = {n for n in vistas if n in ("login_cma", "reservar_cma") or n.startswith("_cma_")}
        sin_plazo_ms = sorted((n, c.func.id) for n in cma for c in ast.walk(funcs[n])
                              if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                              and c.func.id in CON_PLAZO_DE_CMA and not any(k.arg == "plazo_ms" for k in c.keywords))
        self.assertEqual(sin_plazo_ms, [])
        self.assertTrue({"_cma_puerto", "_cma_entrega", "_cma_evidencia", "_cma_ajustes_reefer"} <= cma)

    def test_el_boton_final_solo_si_la_pagina_responde(self):
        # Después de la guarda, CMA mira su botón final con plazo (_pulsar_boton con plazo_ms): si la página no
        # responde, no lo mira ni lo pulsa (False: no se envió).
        class Boton:
            first = property(lambda s: s)

            def __init__(self):
                self.hechos = []

            def count(self):
                self.hechos.append("count")
                return 1

            def is_visible(self):
                self.hechos.append("is_visible")
                return True

            def click(self, **k):
                self.hechos.append("click")

        for responde, esperado in ((True, (True, ["count", "is_visible", "click"])), (False, (False, []))):
            with self.subTest(responde=responde):
                pagina = PaginaDataDome(self.mod, [estado(http=200, responde=responde)])
                boton = Boton()
                pagina.locator = lambda sel, p=pagina, b=boton: p.main_frame.locator(sel) if sel == ":root" else b
                pulsado = self.mod._pulsar_boton(pagina, "button:has-text('Enviar el booking')",
                                                 plazo_ms=self.mod.CMA_PLAZO_MS)
                self.assertEqual((pulsado, boton.hechos), esperado)
                self.assertEqual(pagina.plazos, [self.mod.CMA_PLAZO_MS])

    def test_la_evidencia_del_envio_con_plazo(self):
        # Y la evidencia del envío, con plazo (_resultado_envio y _guardar_evidencia con plazo_ms).
        reg, _, carpeta = self.corrida("envio")
        pagina = PaginaDataDome(self.mod, [FORMULARIO])
        r = self.mod._resultado_envio(pagina, reg, "cma", "CMA", "cma_f9_6_confirmado", "Enviar el booking", False,
                                      plazo_ms=self.mod.CMA_PLAZO_MS)
        self.assertEqual(r[0], "NO ENVIADA")
        self.assertEqual((pagina.sin_plazo, set(pagina.plazos)), ([], {self.mod.CMA_PLAZO_MS}))
        self.assertTrue((carpeta / "cma_f9_6_confirmado.html").exists())

    def test_el_login_mira_el_boton_con_plazo(self):
        # click_si_existe con plazo_ms (el botón de entrar de CMA): su consulta, con plazo. Si la página no la
        # contesta, no pulsa, como antes con la página ocupada.
        reg, vistas, _ = self.corrida("login_boton")
        pagina = PaginaDataDome(self.mod, [estado(http=200, responde=False)])
        self.assertIs(self.mod.click_si_existe(pagina, "button[type='submit']", 5000, reg,
                                               plazo_ms=self.mod.CMA_PLAZO_MS), False)
        self.assertEqual((pagina.sin_plazo, pagina.plazos), ([], [self.mod.CMA_PLAZO_MS] * 2))
        self.assertIn("clic NO (pagina ocupada)", "\n".join(vistas))

    def test_lo_que_vale_sin_respuesta(self):
        # Sin respuesta, _cma_cuantos y _cma_se_ve dan lo que les pide quien las llama: 0 y False, si no le pide otra
        # cosa; None o True, donde contar 0 o no ver cambiaría lo que hace el programa (TestSinRespuestaNoDecide). Y no
        # llaman a count() ni a is_visible(), que no tienen plazo.
        class Localizador:
            def count(self):
                raise AssertionError("count() sin respuesta")

            def is_visible(self):
                raise AssertionError("is_visible() sin respuesta")

        m, loc = self.mod, Localizador()
        pagina = PaginaDataDome(m, [estado(http=200, responde=False)])
        self.assertEqual((m._cma_cuantos(pagina, loc), m._cma_cuantos(pagina, loc, si_no_responde=None),
                          m._cma_se_ve(pagina, loc), m._cma_se_ve(pagina, loc, si_no_responde=True)),
                         (0, None, False, True))

    def test_los_plazos_de_la_reserva_y_de_datadome(self):
        # Las lecturas de la reserva y del login van con CMA_PLAZO_MS, el plazo por omisión de Playwright, el mismo que
        # ya tenían text_content, input_value e is_disabled: con CMA_LECTURA_MS, una página ocupada un momento cambiaba
        # lo que el programa hacía (el JavaScript de los comentarios que no volvía dejaba la reserva sin ellos; desde el
        # encargo 56, corta), y antes la esperaba. Las que miran qué muestra DataDome siguen con CMA_LECTURA_MS
        # (encargo 54). El aviso de mantenimiento, con CMA_PLAZO_MS: con el otro, el de una página que todavía carga no
        # se vería.
        m = self.mod
        self.assertEqual((m.CMA_PLAZO_MS, m.CMA_SIN_RESPUESTA), (30000, "la página no contestó en 30 s"))
        texto = "Inicio\nWe are improving the eBusiness area"
        pagina = PaginaDataDome(m, [estado(http=200, texto=texto)])
        self.assertEqual((m._cma_js(pagina, m._JS_CMA_TEXTO), m._cma_responde(pagina), m._cma_en_mantenimiento(pagina),
                          m._cma_leer(pagina, m._JS_CMA_TEXTO)), (texto, True, True, texto))
        self.assertEqual(pagina.plazos, [m.CMA_PLAZO_MS] * 3 + [m.CMA_LECTURA_MS])


CAMPO_ENTREGA = "input[placeholder*='entrega' i], input[placeholder*='delivery' i]"
SUGERENCIAS = ".el-autocomplete-suggestion:visible li:visible"
SELECCIONAR = "input[placeholder*='Seleccionar' i]"
OPCIONES = ".el-select-dropdown:visible li:visible"


class Lista:
    """Un localizador falso: los textos de lo que calza con su selector, en orden. Filtra por un texto o una expresión
    (has_text), y su first es el primero; sin ninguno, sus acciones fallan, como las de Playwright al vencer su
    plazo."""

    def __init__(self, pagina, textos):
        self.pagina, self.textos = pagina, list(textos)

    def filter(self, has_text=None):
        calza = has_text.search if hasattr(has_text, "search") else (lambda t: has_text in t)
        return Lista(self.pagina, [t for t in self.textos if calza(t)])

    @property
    def first(self):
        return Lista(self.pagina, self.textos[:1])

    def count(self):
        return len(self.textos)

    def is_visible(self):
        return bool(self.textos)

    def text_content(self, **k):
        return self.textos[0]

    def _que_este(self):
        if not self.textos:
            raise TimeoutError("no está")

    def scroll_into_view_if_needed(self, **k):
        self._que_este()

    def click(self, **k):
        self._que_este()
        self.pagina.clics.append(self.textos[0])

    def fill(self, *a, **k):
        self._que_este()

    def type(self, *a, **k):
        self._que_este()


class RaizQueContesta:
    """El localizador ':root' de PaginaQueContesta: la pregunta con plazo contesta o no, según su lista."""

    def __init__(self, pagina):
        self.pagina = pagina

    def evaluate(self, js, *a, timeout=None):
        if js == "() => true":
            if self.pagina.contesta and not self.pagina.contesta.pop(0):
                raise TimeoutError(f"Locator.evaluate: Timeout {timeout}ms exceeded.")
            return True
        self.pagina.js.append(js)
        return next((r for marca, r in self.pagina.respuestas.items() if marca in js), None)


class PaginaQueContesta:
    """Página falsa de CMA para las elecciones que una lectura sin respuesta no decide (encargo 55). 'contesta' dice,
    pregunta por pregunta, si la página contesta la pregunta con plazo («() => true»), y cuando se acaba, contesta;
    'listas', los textos de cada selector; 'visibles', los que se ven en la página (get_by_text); y 'js' responde a cada
    JavaScript según una marca de su texto. Anota los clics (el texto de lo pulsado) y cada JavaScript que no es la
    pregunta."""

    def __init__(self, contesta=(), listas=None, visibles=(), js=None):
        self.contesta, self.listas, self.visibles = list(contesta), dict(listas or {}), set(visibles)
        self.respuestas, self.clics, self.js = dict(js or {}), [], []
        self.keyboard = types.SimpleNamespace(press=lambda *a, **k: None)

    def wait_for_timeout(self, ms):
        pass

    def locator(self, sel):
        return RaizQueContesta(self) if sel == ":root" else Lista(self, self.listas.get(sel, []))

    def get_by_text(self, texto, exact=False):
        return Lista(self, [texto] if texto in self.visibles else [])


class TestSinRespuestaNoDecide(ConCorrida):
    """Donde contar 0 o no ver cambiaría qué elige el programa o le haría pulsar algo, una lectura sin respuesta no
    decide (encargo 55): la sugerencia con «ramp» del lugar de entrega, «Añadir dirección de entrega» y la opción de
    «Tamaño y tipo». Las páginas son falsas, con nombres inventados."""

    def test_no_pulsa_anadir_sin_saber_si_hace_falta(self):
        # Sin respuesta, el campo del lugar de entrega cuenta como visto: no se pulsa «Añadir dirección de entrega».
        # Aquí el campo no está: el paso no lo encuentra, y el ayudante devuelve que no eligió (reservar_cma corta ahí).
        # Control: si la página contesta y el campo no se ve, lo pulsa, como siempre.
        for contesta, clics in (([False], []), ([], ["Añadir dirección de entrega"])):
            with self.subTest(contesta=contesta):
                reg, _, _ = self.corrida(f"anadir_{len(contesta)}")
                pagina = PaginaQueContesta(contesta=contesta, visibles={"Añadir dirección de entrega"})
                self.assertEqual(self.mod._cma_entrega(pagina, "CIUDAD PRUEBA, PAIS", reg), "")
                self.assertEqual(pagina.clics, clics)

    def test_no_elige_otra_sugerencia_que_la_de_la_regla(self):
        # La regla del lugar de entrega: la primera sugerencia con «ramp». Si la página no contesta al buscarla, en esa
        # vuelta no se elige, y la vuelta se repite: se pulsa la de la regla, y no la primera de la lista. Las
        # preguntas: la del campo y la de las sugerencias contestan, la de las de «ramp» no; después, todas.
        reg, _, _ = self.corrida("ramp")
        listas = {CAMPO_ENTREGA: ["campo"], SUGERENCIAS: ["CIUDAD PRUEBA, PAIS", "CIUDAD PRUEBA RAMP, PAIS"]}
        pagina = PaginaQueContesta(contesta=[True, True, False], listas=listas)
        self.assertEqual(self.mod._cma_entrega(pagina, "CIUDAD PRUEBA, PAIS", reg), "CIUDAD PRUEBA RAMP, PAIS")
        self.assertEqual(pagina.clics, ["campo", "CIUDAD PRUEBA RAMP, PAIS"])

    def test_tamano_y_tipo_corta_sin_respuesta(self):
        # La opción de «Tamaño y tipo»: si la página no contesta al buscarla, no se elige con esa lectura, ni con la
        # segunda forma de buscarla, ni con el JavaScript de respaldo; el paso corta, y el motivo dice por qué.
        listas = {SELECCIONAR: ["Seleccionar"], OPCIONES: ["40' Dry", "40' Reefer High Cube"]}
        reg, _, _ = self.corrida("tamano")
        pagina = PaginaQueContesta(contesta=[True, False], listas=listas, js={"40.*high.*cube": "40' Reefer High Cube"})
        with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
            self.mod._cma_completar_info_extra(pagina, {"fila": 5}, reg)
        self.assertEqual((e.exception.paso, e.exception.buscaba, pagina.clics, pagina.js),
                         ("Tamaño y tipo de CMA", "la opción «40' Reefer High Cube» en el desplegable (por su texto), "
                                                  "porque la página no contestó en 30 s", ["Seleccionar"], []))
        # Control: si la página contesta, elige la opción por su texto, y el paso sigue (después corta en otro que esta
        # página falsa no tiene, o no corta).
        reg, _, _ = self.corrida("tamano_control")
        pagina = PaginaQueContesta(listas=listas, js={"40.*high.*cube": "40' Reefer High Cube"})
        try:
            self.mod._cma_completar_info_extra(pagina, {"fila": 5}, reg)
        except self.mod.ObjetivoNoEncontrado as otro:
            self.assertNotEqual(otro.paso, "Tamaño y tipo de CMA")
        self.assertEqual(pagina.clics[:2], ["Seleccionar", "40' Reefer High Cube"])


class TestDataDomeAMitad(ConCorrida):
    """DataDome a mitad de una reserva de CMA-CGM (decisión de Marcelo, encargo 55): con el bloqueo, o con una
    verificación que no deja pasar en 30 s, se detiene igual que en la portada; el deslizador lo sigue pasando el
    operador; y si DataDome deja pasar la página, la fila igual termina, NO ENVIADA, y la corrida sigue."""

    def a_mitad(self, nombre, estados, tope=None):
        reloj = Reloj()
        pagina = PaginaDataDome(self.mod, estados, reloj)
        pagina.TOPE = tope or pagina.TOPE
        pausas = []

        def on_pausa(m, hasta=None):
            pausas.append(m)
            return self.mod.PAUSA_RESUELTA

        # La espera del deslizador cuenta con el time de la biblioteca: aquí, con el mismo reloj falso.
        with mock.patch.object(self.mod, "time", reloj), mock.patch("time.time", reloj.time), \
                mock.patch("winsound.MessageBeep"):
            reg, vistas, carpeta = self.corrida(nombre)
            try:
                r = self.mod._cma_datadome_a_mitad(pagina, reg, on_pausa, CREDS, "tras el origen", 9)
            except self.mod.CmaDetenida as e:
                r = e
        return r, pagina, pausas, vistas, carpeta, reg

    def interrumpida(self, que):
        return self.mod.CMA_INTERRUMPIDA.format(donde="tras el origen", que=que)

    def test_sin_datadome_no_hace_nada(self):
        r, pagina, pausas, vistas, _, _ = self.a_mitad("sin_datadome", [FORMULARIO])
        self.assertEqual((r, pagina.esperas, pagina.capturas, pausas, vistas), (None, [], [], [], []))
        self.assertEqual(pagina.sin_plazo, [])

    def test_bloqueo_detiene_la_corrida(self):
        r, pagina, pausas, vistas, _, reg = self.a_mitad("bloqueo", [BLOQUEO_ENCIMA])
        motivo = self.motivo(self.mod.CMA_ACCESO_RESTRINGIDO)
        self.assertIs(type(r), self.mod.CmaDetenida)
        self.assertEqual((r.motivo, self.mod._naviera_detenida(reg, "cma")), (motivo, motivo))
        self.assertEqual((pausas, pagina.esperas, pagina.visitas), ([], [], []))
        self.assertEqual(pagina.capturas, [("cma_acceso_restringido.png", self.mod.CMA_CAPTURA_MS)])
        self.assertIn("· DataDome apareció a mitad de la reserva de CMA-CGM, tras el origen.", "\n".join(vistas))

    def test_verificacion_que_no_deja_pasar_detiene_al_plazo(self):
        r, pagina, pausas, _, _, reg = self.a_mitad("verificacion_sin_fin", [VERIFICANDO_ENCIMA])
        self.assertIs(type(r), self.mod.CmaDetenida)
        self.assertEqual(r.motivo, self.sin_cargar("DataDome no terminó de verificar el navegador"))
        self.assertEqual((pagina.esperas, pausas), ([1000] * self.mod.CMA_ESPERA_PORTADA, []))

    def test_verificacion_que_deja_pasar_termina_la_fila(self):
        r, pagina, pausas, vistas, carpeta, reg = self.a_mitad("verificacion_pasa",
                                                               [VERIFICANDO_ENCIMA, VERIFICANDO_ENCIMA, FORMULARIO])
        motivo = self.interrumpida(self.mod.CMA_PASO_LA_VERIFICACION)
        self.assertIs(type(r), self.mod.CmaInterrumpida)
        # La corrida sigue: el motivo no queda en el Registro.
        self.assertEqual((r.motivo, self.mod._naviera_detenida(reg, "cma")), (motivo, ""))
        self.assertEqual((pagina.esperas, pausas, pagina.visitas), ([1000, 1000], [], []))
        self.assertEqual(pagina.capturas, [("cma_verificacion.png", self.mod.CMA_CAPTURA_MS),
                                           ("cma_f9_datadome.png", self.mod.CMA_CAPTURA_MS)])
        self.assertEqual(sorted(a.name for a in carpeta.iterdir() if a.suffix == ".html"), ["cma_f9_datadome.html"])
        texto = "\n".join(vistas)
        self.assertIn(f"· ⛔ {motivo}.", texto)
        self.assertIn("evidencia de CMA-CGM interrumpida: cma_f9_datadome.png y 1 de 1 HTML (la página y 0 marco(s))",
                      texto)

    def test_deslizador_lo_pasa_el_operador_y_la_fila_termina(self):
        r, pagina, pausas, vistas, _, reg = self.a_mitad("deslizador", [DESLIZADOR_ENCIMA, FORMULARIO])
        self.assertIs(type(r), self.mod.CmaInterrumpida)
        self.assertEqual((r.motivo, self.mod._naviera_detenida(reg, "cma")),
                         (self.interrumpida(self.mod.CMA_DESLIZADO), ""))
        self.assertEqual(pausas, ["CMA CGM: desliza la flecha hacia la derecha en el navegador para continuar."])
        self.assertEqual(pagina.capturas, [("cma_f9_robot_desafio.png", self.mod.CMA_CAPTURA_MS),
                                           ("cma_f9_datadome.png", self.mod.CMA_CAPTURA_MS)])
        # La pausa, en log.txt: cuándo empezó y por qué, y cómo terminó.
        texto = "\n".join(vistas)
        self.assertIn("· ⏸ PAUSA: espero al operador. Por qué: CMA CGM: desliza la flecha hacia la derecha en el "
                      "navegador para continuar.", texto)
        self.assertIn("· ▶ La pausa terminó a los 0 s: el operador pulsó «Ya lo resolví».", texto)

    def test_otra_pagina_suya_va_al_operador(self):
        r, _, pausas, _, _, _ = self.a_mitad("otra", [en_el_formulario((CAPTCHA, "Texto inventado", True)), FORMULARIO])
        self.assertEqual((type(r), len(pausas)), (self.mod.CmaInterrumpida, 1))

    def test_deslizador_que_nadie_desliza(self):
        r, pagina, pausas, vistas, _, reg = self.a_mitad("sin_deslizar", [DESLIZADOR_ENCIMA], tope=400)
        que = self.mod.CMA_SIN_DESLIZAR.format(seg=self.mod.CMA_ESPERA_DESLIZADOR)
        self.assertEqual((type(r), r.motivo, self.mod._naviera_detenida(reg, "cma")),
                         (self.mod.CmaInterrumpida, self.interrumpida(que), ""))
        self.assertEqual((len(pagina.esperas), len(pausas)), (self.mod.CMA_ESPERA_DESLIZADOR, 1))
        self.assertIn("· Tiempo de espera agotado para la verificación de CMA CGM.", "\n".join(vistas))

    def test_deslizador_que_pasa_al_bloqueo_detiene(self):
        r, _, pausas, _, _, reg = self.a_mitad("al_bloqueo", [DESLIZADOR_ENCIMA, BLOQUEO_ENCIMA])
        self.assertEqual((type(r), r.motivo, len(pausas)),
                         (self.mod.CmaDetenida, self.motivo(self.mod.CMA_ACCESO_RESTRINGIDO), 1))

    def test_lo_medido(self):
        # La espera del deslizador, la de siempre (180 s), y los textos del motivo.
        m = self.mod
        self.assertEqual(m.CMA_ESPERA_DESLIZADOR, 180)
        self.assertEqual(m.CMA_INTERRUMPIDA.format(donde="tras el origen", que=m.CMA_DESLIZADO),
                         "DataDome interrumpió la reserva tras el origen (el operador deslizó la flecha). La reserva "
                         "no se envió y no se volvió a intentar (la captura y el HTML, en la carpeta de la corrida)")
        self.assertTrue(issubclass(m.CmaInterrumpida, m.CmaDetenida))


class TestReservaConDataDome(ConCorrida):
    """Lo que hace la reserva de CMA-CGM con DataDome a mitad de camino (encargo 55): el decorador lo mira cuando la
    reserva se corta o queda REVISAR, y nunca después de la guarda; la reserva lo mira entre un paso y otro."""
    RESERVA = dict(TestReservaCma.RESERVA)

    def decorada(self, cruda):
        return self.mod._sin_clic_a_ciegas("cma", plazo_ms=self.mod.CMA_PLAZO_MS)(self.mod._cma_si_se_detuvo(cruda))

    def correr(self, nombre, cruda, filas):
        """Corre la reserva decorada, fila por fila, cada una con su página falsa (sus estados), con el mismo Registro.
        Devuelve (resultados, páginas, lo que se vio, la carpeta, el Registro)."""
        reloj = Reloj()
        paginas = [PaginaDataDome(self.mod, estados, reloj) for estados in filas]
        with mock.patch.object(self.mod, "time", reloj), mock.patch("time.time", reloj.time), \
                mock.patch("winsound.MessageBeep"):
            reg, vistas, carpeta = self.corrida(nombre)
            r = [self.decorada(cruda)(p, dict(self.RESERVA, fila=9 + k), dict(CREDS), reg,
                                      on_pausa=lambda m, hasta=None: self.mod.PAUSA_RESUELTA)
                 for k, p in enumerate(paginas)]
        return r, paginas, vistas, carpeta, reg

    def corta(self):
        def cruda(page, reserva, creds, reg, on_pausa=None):
            cruda.filas.append(reserva["fila"])
            raise self.mod.ObjetivoNoEncontrado("Origen de CMA", "la sugerencia inventada")
        cruda.filas = []
        return cruda

    def devuelve(self, resultado):
        def cruda(page, reserva, creds, reg, on_pausa=None):
            cruda.filas.append(reserva["fila"])
            return resultado
        cruda.filas = []
        return cruda

    def test_corte_con_el_bloqueo_detiene_la_corrida(self):
        cruda = self.corta()
        r, paginas, vistas, carpeta, reg = self.correr("corte_bloqueo", cruda, [[BLOQUEO_ENCIMA], [FORMULARIO]])
        motivo = self.motivo(self.mod.CMA_ACCESO_RESTRINGIDO)
        # Las dos filas NO ENVIADA con el motivo, y la segunda sin volver al portal.
        self.assertEqual((r, cruda.filas), ([("NO ENVIADA", motivo)] * 2, [9]))
        self.assertEqual(self.mod._naviera_detenida(reg, "cma"), motivo)
        # La evidencia de la detención, y no la del paso sin objetivo.
        self.assertEqual((paginas[0].capturas, paginas[1].capturas),
                         ([("cma_acceso_restringido.png", self.mod.CMA_CAPTURA_MS)], []))
        self.assertIn("· DataDome apareció a mitad de la reserva de CMA-CGM, en un paso que no encontró su objetivo.",
                      "\n".join(vistas))

    def test_corte_sin_datadome_sigue_como_antes(self):
        cruda = self.corta()
        r, paginas, _, carpeta, reg = self.correr("corte", cruda, [[FORMULARIO], [FORMULARIO]])
        motivo = ("Origen de CMA: no encontré la sugerencia inventada, así que no pulsé nada. La reserva no se envió; "
                  "revisa ese paso en el portal.")
        self.assertEqual((r, cruda.filas, self.mod._naviera_detenida(reg, "cma")), ([("NO ENVIADA", motivo)] * 2,
                                                                                      [9, 10], ""))
        self.assertEqual(paginas[0].capturas, [("cma_f9_sin_objetivo.png", None)])
        # Con plazo: lo que mira si DataDome está, con CMA_LECTURA_MS, y su HTML, con CMA_PLAZO_MS.
        self.assertEqual((paginas[0].sin_plazo, set(paginas[0].plazos)),
                         ([], {self.mod.CMA_LECTURA_MS, self.mod.CMA_PLAZO_MS}))

    def test_revisar_con_datadome_termina_la_fila_y_la_corrida_sigue(self):
        cruda = self.devuelve(("REVISAR", "x"))
        r, _, _, _, reg = self.correr("revisar", cruda, [[VERIFICANDO_ENCIMA, FORMULARIO], [FORMULARIO]])
        motivo = self.mod.CMA_INTERRUMPIDA.format(donde=ANTES_DE_REVISAR, que=self.mod.CMA_PASO_LA_VERIFICACION)
        self.assertEqual((r, cruda.filas, self.mod._naviera_detenida(reg, "cma")),
                         ([("NO ENVIADA", motivo), ("REVISAR", "x")], [9, 10], ""))

    def test_despues_de_la_guarda_no_mira(self):
        # La guarda (OK-EJEMPLO) y lo que devuelve el envío: el decorador no lee nada, aunque DataDome esté.
        for resultado in (("OK-EJEMPLO", "x"), ("NO ENVIADA", "y"), ("ENVIADA – REVISAR EN PORTAL", "z"),
                          ("EMITIDA", "w")):
            with self.subTest(resultado=resultado[0]):
                r, paginas, vistas, _, _ = self.correr("guarda", self.devuelve(resultado), [[BLOQUEO_ENCIMA]])
                self.assertEqual((r, paginas[0].plazos, paginas[0].capturas), ([resultado], [], []))

    def test_otra_falla_sale_sin_mirar(self):
        # Un error que no es un corte sale como antes, sin que el decorador lea la página: después de la guarda no se
        # mira nada, y de un error no se sabe si fue antes.
        def cruda(page, reserva, creds, reg, on_pausa=None):
            raise LoginFalla("falla inventada")
        pagina = PaginaDataDome(self.mod, [BLOQUEO_ENCIMA])
        reg, _, _ = self.corrida("otra_falla")
        with self.assertRaises(LoginFalla):
            self.decorada(cruda)(pagina, dict(self.RESERVA), dict(CREDS), reg)
        self.assertEqual((pagina.plazos, pagina.capturas), ([], []))

    def test_el_decorador_no_se_traga_el_corte(self):
        # Lo atrapa solo para mirar DataDome, y lo vuelve a levantar.
        _, funcs = arbol_y_funciones(self.mod)
        manejadores = [h for h in ast.walk(funcs["_cma_si_se_detuvo"]) if isinstance(h, ast.ExceptHandler)
                       and h.type is not None and "ObjetivoNoEncontrado" in ast.unparse(h.type)]
        self.assertEqual([ast.unparse(h.body[-1]) for h in manejadores], ["raise"])

    def test_mira_entre_los_pasos_y_antes_de_la_guarda(self):
        _, funcs = arbol_y_funciones(self.mod)
        f = funcs["reservar_cma"]
        guarda = linea_de_la_guarda(f)
        donde = sorted((c.lineno, c.args[4].value) for c in ast.walk(f) if isinstance(c, ast.Call)
                       and getattr(c.func, "id", "") == "_cma_datadome_a_mitad")
        self.assertEqual([d for _, d in donde], ["tras el origen", "tras el destino", "tras «Validar ruta»",
                                                 "tras la información de la carga", "tras elegir la ruta",
                                                 "tras el panel Reefer", "en «Envío de la reserva»"])
        self.assertTrue(all(linea < guarda for linea, _ in donde))
        # La última, justo antes de la evidencia de la guarda: entre las dos no hay otra sentencia.
        sentencias = [s for s in ast.walk(f) if isinstance(s, ast.Expr)]
        siguiente = min((s for s in sentencias if s.lineno > donde[-1][0]), key=lambda s: s.lineno)
        self.assertIn('_evidencia_antes_de_la_guarda(page, reg, f"cma_f{f}_guarda"', ast.unparse(siguiente).replace(
            "'", '"'))

    def test_revisar_solo_antes_de_la_guarda(self):
        # El decorador mira DataDome cuando la reserva queda REVISAR: eso nunca sale después de la guarda. La guarda
        # termina la reserva por sus dos ramas (return), y ningún REVISAR está en ellas: el que va después del bucle de
        # los modos sale solo si ninguno llegó a la guarda.
        _, funcs = arbol_y_funciones(self.mod)
        f = funcs["reservar_cma"]
        guarda = next(n for n in ast.walk(f) if isinstance(n, ast.If) and "es_modo_emision" in ast.unparse(n.test))
        self.assertEqual((type(guarda.body[-1]), type(guarda.orelse[-1])), (ast.Return, ast.Return))
        en_la_guarda = {id(n) for n in ast.walk(guarda)}
        revisar = [n for n in ast.walk(f) if isinstance(n, ast.Tuple) and n.elts
                   and isinstance(n.elts[0], ast.Constant) and n.elts[0].value == "REVISAR"]
        self.assertTrue(revisar)
        self.assertEqual([n.lineno for n in revisar if id(n) in en_la_guarda], [])

    def test_deslizador_sin_pasar_al_abrir_el_formulario(self):
        # reservar_cma de verdad: Click & Book muestra el deslizador y nadie lo desliza. La fila queda NO ENVIADA con
        # el motivo, sin seguir al origen ni probar el otro modo, y la corrida sigue (hasta el encargo 55, la reserva
        # seguía y se cortaba en el origen).
        reloj = Reloj()
        pagina = PaginaDataDome(self.mod, [DESLIZADOR_ENCIMA], reloj)
        pagina.TOPE = 400
        with mock.patch.object(self.mod, "time", reloj), mock.patch("time.time", reloj.time), \
                mock.patch("winsound.MessageBeep"):
            reg, vistas, _ = self.corrida("sin_deslizar_al_abrir")
            r = self.mod.reservar_cma(pagina, dict(self.RESERVA), dict(CREDS), reg,
                                      on_pausa=lambda m, hasta=None: self.mod.PAUSA_RESUELTA)
        que = self.mod.CMA_SIN_DESLIZAR.format(seg=self.mod.CMA_ESPERA_DESLIZADOR)
        motivo = self.mod.CMA_INTERRUMPIDA.format(donde="al abrir el formulario", que=que)
        self.assertEqual((r, len(pagina.visitas), self.mod._naviera_detenida(reg, "cma")),
                         (("NO ENVIADA", motivo), 1, ""))
        self.assertEqual(pagina.capturas[-1], ("cma_f9_datadome.png", self.mod.CMA_CAPTURA_MS))


# --- Encargo 56: la pausa del deslizador termina sola, y «Detener» corta la espera ---
class TestPausaQueTerminaSola(ConCorrida):
    """La pausa del deslizador termina sola cuando DataDome deja pasar la página (la corrida sigue) o la bloquea
    (CMA-CGM se detiene, como antes), y «Detener» corta la espera sin volver a mirar la página (decisión de Marcelo,
    encargo 56, CICLO-pausa-sola-y-comentarios.md). Con la pausa de verdad del panel web (_web_pausa): cada espera suya
    de 2 s pasa la página falsa al estado siguiente, como el tiempo que corre mientras el operador desliza la flecha."""

    def setUp(self):
        super().setUp()
        m = self.mod
        with m._LOCK:
            m._WEB.update(detener=threading.Event(), log=[], base=0, pausa=None, pausa_msg="")
        self.addCleanup(lambda: m._WEB.update(detener=None, log=[], base=0, pausa=None, pausa_msg=""))

    def detener(self, pagina):
        """«Detener», como lo pulsa el panel (/api/detener): marca la detención, suelta la pausa y cierra el
        navegador."""
        self.mod._WEB["detener"].set()
        if self.mod._WEB["pausa"]:
            self.mod._WEB["pausa"].set()
        pagina.cerrada = True

    def ya_lo_resolvi(self, k, pagina):
        if k == 0:
            self.mod._WEB["pausa"].set()

    def con_el_panel(self, nombre, estados, en_la_pausa=None, al_esperar=None, a_mitad=False, tope=None):
        """La espera del deslizador (en la portada, o a mitad de la reserva) con la pausa del panel web. 'en_la_pausa(k,
        pagina)' corre en la espera k de la pausa (0, 1…), y 'al_esperar(pagina)' en cada espera de la página: ahí el
        operador pulsa un botón. Devuelve (el resultado o la CmaDetenida, la página, lo que se vio, cómo quedó el panel,
        las esperas de la pausa, el Registro)."""
        m = self.mod
        reloj = Reloj()
        pagina = PaginaDataDome(m, estados, reloj)
        pagina.al_esperar, pagina.TOPE = al_esperar, tope or pagina.TOPE
        dormidas = []

        def dormir(s):
            dormidas.append(s)
            reloj.t += s
            if en_la_pausa:
                en_la_pausa(len(dormidas) - 1, pagina)
            pagina.i += 1

        with mock.patch.object(m, "time", reloj), mock.patch("time.time", reloj.time), \
                mock.patch.object(m, "_time", types.SimpleNamespace(sleep=dormir, time=reloj.time)), \
                mock.patch("winsound.MessageBeep"):
            reg, vistas, _ = self.corrida(nombre)
            try:
                if a_mitad:
                    r = m._cma_datadome_a_mitad(pagina, reg, m._web_pausa, CREDS, "tras el origen", 9)
                else:
                    r = m._cma_esperar_desafio(pagina, reg, m._web_pausa, creds=CREDS)
            except m.CmaDetenida as e:
                r = e
        return r, pagina, vistas, (m._WEB["pausa"], m._WEB["pausa_msg"]), dormidas, reg

    def test_termina_sola_cuando_datadome_deja_pasar(self):
        r, pagina, vistas, panel, dormidas, _ = self.con_el_panel(
            "deja_pasar", [CON_DESLIZADOR, CON_DESLIZADOR, CON_DESLIZADOR, NORMAL])
        self.assertIs(r, True)
        # Sin «Ya lo resolví»: cuatro esperas de 2 s de la pausa (desde el encargo 57, la tercera ve la página sin
        # DataDome y la cuarta lo confirma; hasta ahí, bastaba la tercera), y la espera de después no corrió (la página
        # esperó solo el segundo y medio de siempre tras darla por superada). El panel ya no muestra la pausa.
        self.assertEqual((dormidas, pagina.esperas, panel), ([2, 2, 2, 2], [1500], (None, "")))
        texto = "\n".join(vistas)
        self.assertIn("· ▶ La pausa terminó a los 8 s: DataDome dejó pasar la página.", texto)
        self.assertIn("· Verificación de CMA CGM superada ✓; continúo automáticamente.", texto)
        self.assertNotIn("esperando que deslices", texto)
        # Solo lee, con el plazo de lo que mira DataDome: sin navegar ni leer sin plazo.
        self.assertEqual((pagina.visitas, pagina.sin_plazo, set(pagina.plazos)), ([], [], {self.mod.CMA_LECTURA_MS}))

    def test_una_lectura_sin_datadome_no_basta(self):
        # Decisión de Marcelo, encargo 57 (CICLO-cortes-de-cma-y-pausas.md): la pausa termina sola solo con dos lecturas
        # seguidas sin DataDome. Aquí la segunda espera ve la página sin DataDome y la tercera, otra vez con la flecha:
        # la cuenta vuelve a cero, y la pausa termina en la quinta, la segunda seguida sin DataDome.
        r, pagina, vistas, _, dormidas, _ = self.con_el_panel(
            "una_no_basta", [CON_DESLIZADOR, CON_DESLIZADOR, NORMAL, CON_DESLIZADOR, NORMAL])
        self.assertIs(r, True)
        self.assertEqual((dormidas, pagina.esperas), ([2] * 5, [1500]))
        self.assertIn("· ▶ La pausa terminó a los 10 s: DataDome dejó pasar la página.", "\n".join(vistas))
        self.assertEqual(self.mod.CMA_LECTURAS_PARA_SEGUIR, 2)

    def test_el_vigia_cuenta_las_lecturas_seguidas(self):
        # Lo que dice el vigía en cada lectura: el bloqueo, con una; que DataDome dejó pasar, en la segunda seguida; y
        # una con la página cerrada también vuelve a contar desde cero.
        m = self.mod
        lecturas = [None, m.CMA_DEJO_PASAR, None, m.CMA_DEJO_PASAR, m.CMA_DEJO_PASAR, m.CMA_DEJO_PASAR,
                    m.CMA_RESTRINGIO]
        with mock.patch.object(m, "_cma_como_quedo", lambda page: lecturas.pop(0)):
            mirar = m._cma_vigia(object())
            dice = [mirar() for _ in range(7)]
        self.assertEqual(dice, [None, None, None, None, m.CMA_DEJO_PASAR, m.CMA_DEJO_PASAR, m.CMA_RESTRINGIO])
        with mock.patch.object(m, "_cma_como_quedo", lambda page: m.CMA_RESTRINGIO):
            self.assertEqual(m._cma_vigia(object())(), m.CMA_RESTRINGIO)

    def test_termina_sola_cuando_datadome_bloquea(self):
        r, pagina, vistas, panel, dormidas, reg = self.con_el_panel("bloquea",
                                                                   [CON_DESLIZADOR, CON_DESLIZADOR, BLOQUEADA])
        motivo = self.motivo(self.mod.CMA_ACCESO_RESTRINGIDO)
        self.assertIs(type(r), self.mod.CmaDetenida)
        self.assertEqual((r.motivo, self.mod._naviera_detenida(reg, "cma")), (motivo, motivo))
        self.assertEqual((dormidas, pagina.esperas, panel), ([2, 2], [], (None, "")))
        self.assertEqual(pagina.capturas[-1], ("cma_acceso_restringido.png", self.mod.CMA_CAPTURA_MS))
        self.assertIn("· ▶ La pausa terminó a los 4 s: DataDome restringió el acceso.", "\n".join(vistas))

    def test_detener_corta_la_espera_sin_volver_a_mirar_la_pagina(self):
        lecturas = []

        def pulsa_detener(k, pagina):
            if k == 1:
                self.detener(pagina)
                lecturas.append(len(pagina.plazos))
        r, pagina, vistas, panel, dormidas, reg = self.con_el_panel("detener", [CON_DESLIZADOR] * 5,
                                                                   en_la_pausa=pulsa_detener)
        self.assertIs(type(r), self.mod.CmaCancelada)
        self.assertEqual((r.motivo, self.mod._naviera_detenida(reg, "cma")), ("Cancelado por el operador", ""))
        # Desde «Detener», ni una lectura más ni una espera de la página; la pausa, suelta.
        self.assertEqual((len(pagina.plazos), pagina.esperas, dormidas, panel), (lecturas[0], [], [2, 2], (None, "")))
        texto = "\n".join(vistas)
        self.assertIn("· ⛔ La pausa se cortó a los 4 s: el operador pulsó «Detener».", texto)
        self.assertIn("· ⛔ El operador pulsó «Detener»: corto la espera del deslizador sin volver a mirar la página.",
                      texto)
        self.assertNotIn("superada", texto)

    def test_ya_lo_resolvi_y_despues_detener(self):
        # «Ya lo resolví» con la flecha todavía a la vista: la espera de después sigue, como antes. Si ahí el operador
        # pulsa «Detener», la corta, aunque la página que se leyó en ese momento ya no muestre a DataDome: el panel la
        # estaba cerrando, y lo leído no vale.
        r, pagina, vistas, _, dormidas, _ = self.con_el_panel(
            "resuelto_y_detener", [CON_DESLIZADOR, CON_DESLIZADOR, NORMAL], en_la_pausa=self.ya_lo_resolvi,
            al_esperar=lambda p: self.mod._WEB["detener"].set())
        self.assertIs(type(r), self.mod.CmaCancelada)
        self.assertEqual((dormidas, pagina.esperas), ([2], [1000]))
        texto = "\n".join(vistas)
        self.assertIn("· ▶ La pausa terminó a los 2 s: el operador pulsó «Ya lo resolví».", texto)
        self.assertNotIn("superada", texto)

    def test_detener_con_el_navegador_ya_cerrado(self):
        # Si «Detener» cierra el navegador mientras la espera de después espera, esa espera falla (como en logs/ el
        # 06-10): corta igual, por «Detener», y no con la falla de la página.
        def cierra(p):
            self.detener(p)
            raise NavegadorCerrado("Page.wait_for_timeout: Target page, context or browser has been closed")
        r, pagina, vistas, _, _, _ = self.con_el_panel("cerrado", [CON_DESLIZADOR] * 3,
                                                       en_la_pausa=self.ya_lo_resolvi, al_esperar=cierra)
        self.assertIs(type(r), self.mod.CmaCancelada)
        self.assertEqual(pagina.esperas, [1000])

    def test_sin_botones_ni_cambios_sigue_esperando(self):
        # Mientras DataDome muestra la flecha y nadie pulsa nada, la pausa no termina: aquí vence a los 10 minutos, y
        # la espera de después sigue como antes, hasta sus 180 s.
        r, pagina, vistas, _, dormidas, _ = self.con_el_panel("sin_cambios", [CON_DESLIZADOR], tope=400)
        self.assertEqual((r, len(dormidas)), (False, 300))
        texto = "\n".join(vistas)
        self.assertIn("· ⛔ La pausa se cortó a los 600 s: pasaron 10 minutos sin que el operador la resolviera.", texto)
        self.assertIn("· Tiempo de espera agotado para la verificación de CMA CGM.", texto)

    def test_a_mitad_de_la_reserva(self):
        # A mitad de una reserva, igual: si DataDome deja pasar la página durante la pausa, la fila termina NO ENVIADA
        # (encargo 55) y la corrida sigue; con «Detener», CmaCancelada.
        r, pagina, vistas, _, dormidas, reg = self.con_el_panel(
            "a_mitad", [DESLIZADOR_ENCIMA, DESLIZADOR_ENCIMA, FORMULARIO], a_mitad=True)
        self.assertIs(type(r), self.mod.CmaInterrumpida)
        self.assertEqual((r.motivo, self.mod._naviera_detenida(reg, "cma")),
                         (self.mod.CMA_INTERRUMPIDA.format(donde="tras el origen", que=self.mod.CMA_DESLIZADO), ""))
        self.assertIn("· ▶ La pausa terminó a los 6 s: DataDome dejó pasar la página.", "\n".join(vistas))
        r, *_ = self.con_el_panel("a_mitad_detener", [DESLIZADOR_ENCIMA] * 3, a_mitad=True,
                                  en_la_pausa=lambda k, p: self.detener(p))
        self.assertIs(type(r), self.mod.CmaCancelada)

    def test_la_pausa_que_dice_detener_corta(self):
        # Lo que dice la pausa basta (aquí, una pausa falsa, sin el «Detener» del panel web): si terminó con «Detener»,
        # la espera se corta sin leer la página ni esperarla.
        m = self.mod
        reloj = Reloj()
        pagina = PaginaDataDome(m, [CON_DESLIZADOR], reloj)
        with mock.patch.object(m, "time", reloj), mock.patch("time.time", reloj.time), \
                mock.patch("winsound.MessageBeep"):
            reg, _, _ = self.corrida("la_pausa_dice_detener")
            with self.assertRaises(m.CmaCancelada):
                m._cma_pedir_deslizador(pagina, reg, lambda msg, hasta=None: m.PAUSA_DETENIDA, creds=CREDS)
        self.assertEqual((pagina.esperas, pagina.plazos), ([], []))

    def test_detener_deja_la_fila_detenido_y_el_login_sin_sesion(self):
        # Como las otras navieras con «Detener»: la fila, DETENIDO, «Cancelado por el operador»; el login, sin sesión.
        # No deja el motivo en el Registro: lo que detiene la corrida es «Detener», por el panel.
        m = self.mod

        def cancelada(*a, **k):
            raise m.CmaCancelada("Cancelado por el operador")
        reg, _, _ = self.corrida("decoradores")
        pagina = PaginaDataDome(m, [FORMULARIO])
        self.assertEqual(m._cma_si_se_detuvo(cancelada)(pagina, dict(TestReservaCma.RESERVA), dict(CREDS), reg),
                         ("DETENIDO", "Cancelado por el operador"))
        self.assertIs(m._cma_login_se_detiene(cancelada)(pagina, CREDS, reg), False)
        self.assertEqual((m._naviera_detenida(reg, "cma"), pagina.plazos, pagina.capturas), ("", [], []))

    def test_pagina_cerrada_no_dejo_pasar(self):
        # Con la página cerrada nada se lee, y _cma_es_robotcheck no ve a DataDome: eso no es que haya dejado pasar.
        m = self.mod
        casos = ((estado(http=200), True, None), (estado(http=200), False, m.CMA_DEJO_PASAR),
                 (BLOQUEADA, False, m.CMA_RESTRINGIO), (CON_DESLIZADOR, False, None), (VERIFICANDO, False, None))
        for k, (e, cerrada, esperado) in enumerate(casos):
            with self.subTest(caso=k):
                pagina = PaginaDataDome(m, [e])
                pagina.cerrada = cerrada
                self.assertEqual(m._cma_como_quedo(pagina), esperado)

    def test_lo_medido(self):
        m = self.mod
        self.assertEqual((m.CMA_DEJO_PASAR, m.CMA_RESTRINGIO),
                         ("DataDome dejó pasar la página", "DataDome restringió el acceso"))
        self.assertTrue(issubclass(m.CmaCancelada, m.CmaDetenida))


if __name__ == "__main__":
    unittest.main()
