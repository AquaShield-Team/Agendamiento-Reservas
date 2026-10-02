# -*- coding: utf-8 -*-
"""Evidencia antes de la guarda del candado (CICLO-evidencia-en-la-guarda.md).

- Cada reservador deja, justo antes de su guarda y se abra o no el candado, la captura de la página completa y
  el HTML completo de la página y de cada marco (con sus raíces shadow): «<nav>_f<fila>_guarda.png» y «.html».
- Solo lee: ni clics, ni navegación, ni esperas. Si algo falla, lo avisa en pantalla y en log.txt, y la reserva
  sigue igual: la evidencia nunca corta el flujo.
- El paso que no encontró su objetivo deja también el HTML junto a su captura «_sin_objetivo».
- CMA deja la captura de la ventana y el HTML con el panel Reefer abierto y tras guardarlo, sin clics, teclas ni
  esperas nuevas (CICLO-cma-reefer-y-fecha-maersk.md).
- HYUNDAI deja la captura de la ventana y el HTML justo antes de escribir el Remark, sin clics, teclas, esperas ni
  navegación nuevas; si falla, lo avisa y el Remark se escribe igual (CICLO-evidencia-remark-hyundai.md).
- HYUNDAI y CMA la dejan al leer su lista de salidas (CICLO-cola-siete-items.md), y CMA al terminar la espera de
  «Validar ruta», después de leer su aviso (CICLO-cola-tres-items.md).
- La poda borra solo los .html de las carpetas de corrida con más de 30 días; log.txt, las capturas y las 4
  corridas de referencia de los generadores no se tocan.

Páginas falsas y carpetas sintéticas en la sandbox; ningún portal, captura ni HTML real.
"""
import _winapi
import ast
import datetime
import itertools
import os
import re
import stat
import types
from pathlib import Path
from unittest import mock

import soporte
from test_envio import Marco, Pantalla, correr_node

N = itertools.count()
PREFIJOS = {"reservar_one": "one", "reservar_msc": "msc", "reservar_cma": "cma", "reservar_cosco": "cosco",
            "reservar_hyundai": "hmm", "reservar_maersk": "mk"}
SIGUE = "La reserva sigue igual; si necesitas medir esta pantalla, vuelve a correr la fila con el candado cerrado."


def funciones(mod):
    tree = ast.parse(Path(mod.__file__).read_text(encoding="utf-8"))
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


def justo_antes_de_la_guarda(f):
    """La sentencia que va justo antes de la guarda, en el mismo bloque (None si la guarda abre su bloque)."""
    for padre in ast.walk(f):
        for campo in ("body", "orelse", "finalbody"):
            cuerpo = getattr(padre, campo, None)
            if isinstance(cuerpo, list):
                for previa, s in zip(cuerpo, cuerpo[1:]):
                    if isinstance(s, ast.If) and ast.unparse(s.test) == "not es_modo_emision()":
                        return previa
    return None


class SoloLee:
    """Página (o marco) que solo sabe lo que la evidencia puede pedir: capturar, evaluar un JavaScript y dar su
    HTML. Cualquier otra cosa (un clic, una tecla, una espera, navegar, un localizador) queda anotada."""

    def __init__(self, frames=(), url="https://portal.invalid/guarda"):
        self.frames, self.url, self.main_frame = list(frames), url, None
        self.capturas, self.js, self.prohibidos = [], [], []

    def screenshot(self, path=None, full_page=False):
        self.capturas.append((Path(path).name, full_page))
        Path(path).write_bytes(b"")

    def evaluate(self, js, *a):
        self.js.append(js)
        return {"html": "<body>sintetico</body>", "sombras": 0}

    def content(self):
        return "<body>sintetico</body>"

    def __getattr__(self, nombre):
        self.prohibidos.append(nombre)
        raise AttributeError(nombre)


class Rota(Pantalla):
    """Página cerrada: ni captura ni marcos."""

    @property
    def frames(self):
        raise RuntimeError("página cerrada")

    @frames.setter
    def frames(self, valor):
        pass

    def screenshot(self, path=None, full_page=False):
        raise RuntimeError("página cerrada")


class ConRegistro(soporte.CasoAQ):
    def corrida(self):
        carpeta, vistas = self.sb / f"corrida_{next(N)}", []
        reg = self.mod.Registro(carpeta / "log.txt", on_log=vistas.append)
        self.addCleanup(reg.cerrar)
        return carpeta, reg, vistas

    def leer(self, carpeta, vistas):
        """(log.txt, pantalla): lo que quedó escrito y lo que vio el operador."""
        return (carpeta / "log.txt").read_text(encoding="utf-8"), "\n".join(vistas)


class TestEvidenciaEnLaGuarda(ConRegistro):
    def setUp(self):
        super().setUp()
        for env in ("AQUASHIELD_CAPTURA_FULL", "AQUASHIELD_DESCUBRIR"):     # sin variable: igual página completa
            os.environ.pop(env, None)

    def test_captura_de_la_pagina_completa_y_html_de_la_pagina_y_los_marcos(self):
        pagina = Pantalla(html="<body>principal</body>", url="https://portal.invalid/review",
                          frames=[Marco(html="<body>uno</body>", url="https://portal.invalid/m1"),
                                  Marco(html="<body>dos</body>", url="https://portal.invalid/m2")])
        carpeta, reg, vistas = self.corrida()
        self.assertIsNone(self.mod._evidencia_antes_de_la_guarda(pagina, reg, "mk_f5_guarda"))
        self.assertEqual(sorted(p.name for p in carpeta.iterdir()),
                         ["log.txt", "mk_f5_guarda.html", "mk_f5_guarda.png", "mk_f5_guarda_marco1.html",
                          "mk_f5_guarda_marco2.html"])
        self.assertEqual(pagina.capturas, [("mk_f5_guarda.png", True)])          # la página completa
        self.assertEqual((carpeta / "mk_f5_guarda.html").read_text(encoding="utf-8"),
                         "<!-- página · https://portal.invalid/review -->\n<body>principal</body>")
        self.assertEqual((carpeta / "mk_f5_guarda_marco2.html").read_text(encoding="utf-8"),
                         "<!-- marco 2 · https://portal.invalid/m2 -->\n<body>dos</body>")
        for donde in self.leer(carpeta, vistas):
            self.assertIn("evidencia en la guarda: mk_f5_guarda.png (página completa) y 3 de 3 HTML (la página y "
                          "2 marco(s); 0 sin raíces shadow)", donde)
            self.assertNotIn("⚠", donde)

    def test_solo_lee_sin_clics_ni_navegacion_ni_esperas(self):
        marco = SoloLee(url="https://portal.invalid/marco")
        pagina = SoloLee(frames=[marco])
        carpeta, reg, _ = self.corrida()
        self.mod._evidencia_antes_de_la_guarda(pagina, reg, "one_f5_guarda")
        self.assertEqual((pagina.prohibidos, marco.prohibidos), ([], []))
        self.assertEqual((pagina.js, marco.js), ([self.mod._JS_HTML_COMPLETO], [self.mod._JS_HTML_COMPLETO]))
        self.assertEqual((pagina.capturas, marco.capturas), ([("one_f5_guarda.png", True)], []))
        self.assertTrue((carpeta / "one_f5_guarda_marco1.html").exists())

    def test_si_la_captura_falla_avisa_y_la_reserva_sigue(self):
        class SinCaptura(Pantalla):
            def screenshot(self, path=None, full_page=False):
                raise RuntimeError("pantalla bloqueada")
        carpeta, reg, vistas = self.corrida()
        self.assertIsNone(self.mod._evidencia_antes_de_la_guarda(SinCaptura(html="<body>x</body>"), reg,
                                                                 "cma_f7_guarda"))
        self.assertTrue((carpeta / "cma_f7_guarda.html").exists())                # el HTML igual queda
        for donde in self.leer(carpeta, vistas):
            self.assertIn("(no pude capturar cma_f7_guarda: pantalla bloqueada)", donde)
            self.assertIn("· ⚠ La evidencia en la guarda quedó incompleta: sin la captura y 1 de 1 HTML (la página "
                          f"y 0 marco(s); 0 sin raíces shadow). {SIGUE}", donde)

    def test_si_un_html_falla_avisa_y_la_reserva_sigue(self):
        roto = Marco(html=RuntimeError("marco cerrado"), contenido=RuntimeError("marco cerrado"))
        carpeta, reg, vistas = self.corrida()
        self.mod._evidencia_antes_de_la_guarda(Pantalla(frames=[roto]), reg, "cosco_f3_guarda")
        self.assertFalse((carpeta / "cosco_f3_guarda_marco1.html").exists())
        for donde in self.leer(carpeta, vistas):
            self.assertIn("· ⚠ No pude guardar el HTML del marco 1 en la guarda: RuntimeError: marco cerrado", donde)
            self.assertIn("· ⚠ La evidencia en la guarda quedó incompleta: cosco_f3_guarda.png (página completa) y "
                          f"1 de 2 HTML (la página y 1 marco(s); 0 sin raíces shadow). {SIGUE}", donde)

    def test_si_todo_falla_no_corta_el_flujo(self):
        carpeta, reg, vistas = self.corrida()
        self.assertIsNone(self.mod._evidencia_antes_de_la_guarda(Rota(), reg, "hmm_f9_guarda"))
        for donde in self.leer(carpeta, vistas):
            self.assertIn("· ⚠ No pude guardar la evidencia en la guarda (hmm_f9_guarda): RuntimeError: página "
                          f"cerrada. {SIGUE}", donde)


class TestCadaReservadorLaDeja(soporte.CasoAQ):
    """Justo antes de la guarda, como sentencia suelta (su resultado no decide nada), con el prefijo de las
    capturas de su naviera y la fila."""

    def _deja(self, nombre):
        previa = justo_antes_de_la_guarda(funciones(self.mod)[nombre])
        self.assertIsInstance(previa, ast.Expr, f"{nombre}: la evidencia no va justo antes de la guarda")
        self.assertEqual(ast.unparse(previa),
                         f"_evidencia_antes_de_la_guarda(page, reg, f'{PREFIJOS[nombre]}_f{{f}}_guarda')")

    def test_one(self):
        self._deja("reservar_one")

    def test_msc(self):
        self._deja("reservar_msc")

    def test_cma(self):
        self._deja("reservar_cma")

    def test_cosco(self):
        self._deja("reservar_cosco")

    def test_hyundai(self):
        self._deja("reservar_hyundai")

    def test_maersk(self):
        self._deja("reservar_maersk")

    def test_solo_ahi(self):
        # Los seis reservadores (su llamada exacta la miran las pruebas de arriba), el paso sin objetivo, las dos
        # del panel Reefer de CMA (TestEvidenciaReefer), MAERSK sin nave (test_clics.TestMaersk), COSCO con más de
        # un itinerario para la nave (test_clics.TestCosco), ONE donde se detuvo (test_clics.TestOne), HYUNDAI antes
        # de escribir el Remark (TestEvidenciaRemarkHyundai): reservar_hyundai aparece dos veces; y MSC sin una sola
        # salida para la nave (test_clics.TestMsc; desde el encargo 25, CICLO-proxima-salida.md). MAERSK la deja en
        # _mk_detenida, sin nave, sin una sola salida y, desde el encargo 40, sin salidas (SIN-CUPO); hasta 16d3583
        # estaba escrita en _mk_sin_nave. Desde el encargo
        # 26, también HYUNDAI y CMA en su lista de salidas (TestEvidenciaListaHyundai, TestEvidenciaRutasCma): hasta
        # 86d6e63, reservar_hyundai aparecía dos veces y _cma_seleccionar_itinerario ninguna.
        llamadas = sorted(nombre for nombre, f in funciones(self.mod).items() for n in ast.walk(f)
                          if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "_evidencia_antes_de_la_guarda")
        self.assertEqual(llamadas, sorted(list(PREFIJOS) + ["_sin_clic_a_ciegas"] + ["_cma_ajustes_reefer"] * 2
                                          + ["_mk_detenida", "_cosco_itinerario_ambiguo", "_one_detenida"]
                                          + ["reservar_hyundai", "_msc_salida_ambigua"]
                                          + ["reservar_hyundai", "_cma_seleccionar_itinerario"]
                                          # Desde el encargo 27, CMA tras «Validar ruta» (TestEvidenciaValidarRutaCma):
                                          # hasta 4b0182b, reservar_cma aparecía una sola vez, la de su guarda.
                                          + ["reservar_cma"]
                                          # Desde el encargo 28, HYUNDAI con el modal «Alternate Vessel Option»
                                          # (TestOtraNaveHyundai): hasta a198645 pulsaba su OK sin dejar evidencia.
                                          # Desde el encargo 32 marca que no quiere otra nave y pulsa OK, y si el modal
                                          # sigue, deja otra (TestModalHyundai, CICLO-ampliar-la-busqueda.md).
                                          + ["_hmm_mantener_nave"] * 2
                                          # Desde el encargo 32, HYUNDAI con la lista ampliada (test_clics.TestHyundai,
                                          # CICLO-ampliar-la-busqueda.md).
                                          + ["_hmm_elegir_nave"]
                                          # Desde el encargo 36, MAERSK con el calendario de la fecha de retiro, y
                                          # después de elegirla si la tarjeta no muestra esa fecha
                                          # (test_clics.TestRetiroMaersk, CICLO-maersk-retiro-y-terminos.md); y con la
                                          # casilla de los términos, antes de marcarla (test_clics.TestTerminosMaersk).
                                          + ["_mk_fecha_de_retiro", "_mk_comprobar_retiro", "_mk_marcar_terminos"]
                                          # Desde el encargo 37, MAERSK en «Booking Information» sin avanzar
                                          # (test_clics.TestMaersk, CICLO-maersk-ultimos-puntos.md).
                                          + ["_mk_booking_sin_avanzar"]
                                          # Desde el encargo 38, MAERSK con el buscador de partes del Shipper abierto,
                                          # y si el Shipper no queda elegido (test_clics.TestShipperMaersk,
                                          # CICLO-maersk-shipper-y-cortes.md).
                                          + ["_mk_elegir_shipper", "_mk_shipper_corte"]
                                          # Desde la revisión del encargo 38, «Review booking» a la vista que no acepta
                                          # el clic, y «Booking Information» incompleta (test_clics.TestMaersk).
                                          + ["_mk_pulsar_revision", "_mk_formulario_incompleto"]
                                          # Desde el encargo 39, «Continue» de «Recommended services» a la vista que
                                          # no acepta el clic (test_clics.TestContinuarMaersk,
                                          # CICLO-maersk-cuatro-puntos.md).
                                          + ["_mk_continuar_servicios"]
                                          # Y con el buscador del Shipper abierto y AQUACHILE en la tarjeta, antes de
                                          # su «Close» (test_clics.TestShipperMaersk).
                                          + ["_mk_cerrar_buscador"]
                                          # Desde el encargo 40, antes de la casilla del resultado con AQUACHILE, si el
                                          # clic en el resultado no lo eligió (test_clics.TestShipperMaersk,
                                          # CICLO-maersk-busqueda-vacia.md).
                                          + ["_mk_marcar_casilla"]
                                          # Desde el encargo 41, antes de elegir una sugerencia de origen o de destino
                                          # (TestListaDeSugerencias, CICLO-origen-y-destino.md).
                                          + ["_fill_autocomplete", "_msc_puerto", "_cosco_autocomplete",
                                             "_hmm_autocomplete", "_mk_ciudad", "_cma_puerto", "_cma_entrega"]
                                          # Desde el encargo 42, la misma evidencia cuando no ven ninguna que elegir:
                                          # la dejan los siete por _evidencia_sin_sugerencia
                                          # (test_sin_sugerencias_deja_la_evidencia_igual).
                                          + ["_evidencia_sin_sugerencia"]
                                          # Desde el encargo 48, New Booking de COSCO sin su formulario
                                          # (test_clics.TestCosco, CICLO-calendario-cosco-y-cma.md).
                                          + ["_cosco_sin_formulario"]))


class TestHtmlSinObjetivo(ConRegistro):
    """El paso que no encontró su objetivo deja, junto a su captura «_sin_objetivo» (la de la ventana, como antes),
    el HTML completo de la página y de cada marco."""
    DETALLE = ("Paso de prueba: no encontré el botón «Prueba» (texto), así que no pulsé nada. La reserva no se "
               "envió; revisa ese paso en el portal.")

    def cortar(self, pagina):
        def reservar(page, reserva, creds, reg, on_pausa=None):
            reg.paso("Paso 1 · algo que sí salió")
            raise self.mod.ObjetivoNoEncontrado("Paso de prueba", "el botón «Prueba» (texto)")
        carpeta, reg, vistas = self.corrida()
        r = self.mod._sin_clic_a_ciegas("cma")(reservar)(pagina, {"fila": 7}, {}, reg)
        return r, carpeta, self.leer(carpeta, vistas)

    def test_el_html_queda_junto_a_la_captura(self):
        pagina = Pantalla(html="<body>paso</body>", frames=[Marco(html="<body>marco</body>")])
        r, carpeta, lugares = self.cortar(pagina)
        self.assertEqual(r, ("NO ENVIADA", self.DETALLE))
        self.assertEqual(sorted(p.name for p in carpeta.iterdir()),
                         ["cma_f7_sin_objetivo.html", "cma_f7_sin_objetivo.png", "cma_f7_sin_objetivo_marco1.html",
                          "log.txt"])
        self.assertEqual(pagina.capturas, [("cma_f7_sin_objetivo.png", False)])      # la ventana, como antes
        self.assertIn("<body>paso</body>", (carpeta / "cma_f7_sin_objetivo.html").read_text(encoding="utf-8"))
        for donde in lugares:
            self.assertIn("evidencia en el paso sin objetivo: cma_f7_sin_objetivo.png y 2 de 2 HTML (la página y "
                          "1 marco(s); 0 sin raíces shadow)", donde)
            self.assertIn(f"· ✗ NO ENVIADA · {self.DETALLE}", donde)

    def test_si_la_evidencia_falla_igual_queda_no_enviada(self):
        r, _, lugares = self.cortar(Rota())
        self.assertEqual(r, ("NO ENVIADA", self.DETALLE))
        for donde in lugares:
            self.assertIn("· ⚠ No pude guardar la evidencia en el paso sin objetivo (cma_f7_sin_objetivo): "
                          f"RuntimeError: página cerrada. {SIGUE}", donde)
            self.assertIn(f"· ✗ NO ENVIADA · {self.DETALLE}", donde)


# --- La poda del HTML viejo de logs/ ---
AHORA = datetime.datetime(2026, 12, 1, 12, 0, 0)
DIA = datetime.timedelta(days=1)
HORA = datetime.timedelta(hours=1)
GENERADORES = ("crear_simulador_html.py", "crear_video_demostracion.py", "crear_video_tutorial.py",
               "generar_manuales.py")


def corrida(prefijo, antes, sufijo=""):
    """Nombre de una carpeta de corrida de hace 'antes' (respecto de AHORA), como lo arma carpeta_corrida."""
    return f"{prefijo}_{(AHORA - antes).strftime('%Y%m%d_%H%M%S')}{sufijo}"


def foto(base):
    """Cada archivo bajo 'base' con su contenido."""
    return {p.relative_to(base).as_posix(): p.read_bytes() for p in base.rglob("*") if p.is_file()}


def escribir(carpeta, *nombres):
    for n in nombres:
        (carpeta / n).parent.mkdir(parents=True, exist_ok=True)
        (carpeta / n).write_text(f"sintetico {n}", encoding="utf-8")


def quitar_enlaces(logs):
    for e in os.scandir(logs):
        if e.is_junction() or e.is_symlink():
            os.rmdir(e.path)


class TestPodaHtml(ConRegistro):
    """Solo los .html de las carpetas de corrida con más de 30 días (por la fecha de su nombre); nada más."""

    def test_borra_solo_los_html_de_las_corridas_de_mas_de_30_dias(self):
        base = self.sb / f"poda_{next(N)}"
        logs = base / "logs"
        vieja, sufijo = corrida("web_msc_op", 45 * DIA), corrida("reservas_cma_op", 31 * DIA, "_2")
        borde_viejo, borde_nuevo = corrida("web_one_op", 30 * DIA + HORA), corrida("web_one_op", 30 * DIA - HORA)
        escribir(logs / vieja, "log.txt", "msc_f5_4_parties.png", "msc_f5_guarda.png", "msc_f5_guarda.html",
                 "msc_f5_guarda_marco1.html", "msc_f5_6_confirmado.html", "notas.HTML", "x.htm", "y.html.png",
                 "sub/z.html")
        escribir(logs / sufijo, "log.txt", "a.html")
        escribir(logs / borde_viejo, "b.html")                                    # 30 días y 1 hora: se poda
        escribir(logs / borde_nuevo, "c.html")                                    # 29 días y 23 horas: queda
        escribir(logs / corrida("web_cosco_op", DIA), "d.html")
        escribir(logs / "cma_dev", "e.html")                                      # sin fecha: no es corrida
        escribir(logs / "notas_20250101", "f.html")
        escribir(logs / corrida("web_one_op", 45 * DIA, "_copia"), "g.html")      # no calza exacto
        escribir(logs / "web_one_op_20251399_250000", "h.html")                   # fecha que no existe
        escribir(logs, "suelto.html")
        escribir(base / "afuera", "u.html")                                       # fuera de logs/
        self.addCleanup(quitar_enlaces, logs)
        _winapi.CreateJunction(str(base / "afuera"), str(logs / corrida("web_hmm_op", 45 * DIA)))
        os.symlink(str(base / "afuera"), str(logs / corrida("web_mk_op", 45 * DIA)), target_is_directory=True)
        antes = foto(base)
        borrados, errores = self.mod.podar_html(logs, ahora=AHORA)
        esperados = [f"{vieja}/msc_f5_6_confirmado.html", f"{vieja}/msc_f5_guarda.html",
                     f"{vieja}/msc_f5_guarda_marco1.html", f"{sufijo}/a.html", f"{borde_viejo}/b.html"]
        self.assertEqual((sorted(borrados), errores), (sorted(esperados), []))
        self.assertEqual(foto(base), {k: v for k, v in antes.items() if k not in {f"logs/{b}" for b in esperados}})

    def test_lo_que_no_se_puede_borrar_queda_y_se_cuenta(self):
        logs = self.sb / f"poda_{next(N)}" / "logs"
        vieja = corrida("web_one_op", 40 * DIA)
        escribir(logs / vieja, "a.html", "b.html", "c.html")
        os.chmod(logs / vieja / "b.html", stat.S_IREAD)
        self.addCleanup(os.chmod, logs / vieja / "b.html", stat.S_IWRITE)
        borrados, errores = self.mod.podar_html(logs, ahora=AHORA)
        self.assertEqual(borrados, [f"{vieja}/a.html", f"{vieja}/c.html"])
        self.assertEqual(len(errores), 1)
        self.assertTrue(errores[0].startswith(f"«{vieja}/b.html» (PermissionError: "), errores[0])
        self.assertTrue((logs / vieja / "b.html").exists())

    def test_sin_logs_no_hace_nada(self):
        self.assertEqual(self.mod.podar_html(self.sb / "no_existe", ahora=AHORA), ([], []))

    def test_al_empezar_la_corrida_avisa_y_nunca_la_detiene(self):
        # Con el reloj detenido en MOMENTO_FIJO (2026-01-02), una corrida de octubre de 2025 tiene más de 30 días.
        vieja = self.mod.LOGS / "web_one_op_20251001_120000"
        escribir(vieja, "log.txt", "one_f5_guarda.png", "one_f5_guarda.html")
        carpeta, reg, vistas = self.corrida()
        with soporte.reloj_detenido(self.mod):
            self.mod._podar_html_viejo(reg)
        self.assertEqual(sorted(p.name for p in vieja.iterdir()), ["log.txt", "one_f5_guarda.png"])
        casos = [(RuntimeError("disco lleno"), "· ⚠ No pude revisar el HTML antiguo de logs/ (RuntimeError: disco "
                                               "lleno); la corrida sigue."),
                 (([], ["«x_20250101_000000/y.html» (PermissionError: sin permiso)"]),
                  "· ⚠ No pude borrar el HTML antiguo «x_20250101_000000/y.html» (PermissionError: sin permiso); "
                  "bórralo a mano si sobra.")]
        for respuesta, aviso in casos:
            with mock.patch.object(self.mod, "podar_html", side_effect=[respuesta] if not isinstance(
                    respuesta, Exception) else respuesta):
                self.assertIsNone(self.mod._podar_html_viejo(reg))
            for donde in self.leer(carpeta, vistas):
                self.assertIn(aviso, donde)
        for donde in self.leer(carpeta, vistas):
            self.assertIn("Borré 1 HTML de evidencia con más de 30 días en logs/ (log.txt y las capturas se "
                          "conservan).", donde)

    def test_corre_al_empezar_cada_corrida_de_reservas(self):
        llamadas = sorted(nombre for nombre, f in funciones(self.mod).items() for n in ast.walk(f)
                          if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "_podar_html_viejo")
        self.assertEqual(llamadas, ["_web_worker", "ejecutar_reservas"])


class TestCorridasDeReferencia(soporte.CasoAQ):
    """Las 4 corridas de referencia que nombran los generadores: la poda no las toca jamás. Se leen de los
    generadores (solo lectura), que son la fuente. Desde el encargo 44 están en el equipo y no en el repo: en un
    equipo sin ninguno, estas pruebas se saltan (CICLO-publicar-el-repo.md)."""

    def nombradas(self):
        nombres, leidos = set(), 0
        for g in GENERADORES:
            # De la copia de las fuentes si la trae; si no, de la carpeta del programa.
            ruta = soporte.FUENTES / g if (soporte.FUENTES / g).exists() else soporte.RAIZ / g
            if not ruta.exists():
                continue
            leidos += 1
            nombres |= set(re.findall(r"logs/([A-Za-z0-9_*]+)/", ruta.read_text(encoding="utf-8")))
        if not leidos:
            self.skipTest("los generadores de material no están en este equipo (quedan fuera del repo)")
        return nombres

    def corridas(self):
        return sorted(n for n in self.nombradas() if re.fullmatch(self.mod.PATRON_CORRIDA, n))

    def test_son_las_que_nombran_los_generadores(self):
        corridas = self.corridas()
        self.assertTrue(corridas, "el instrumento no ve las carpetas que nombran los generadores")
        self.assertEqual(corridas, sorted(self.mod.CORRIDAS_DE_REFERENCIA))
        # Ninguna carpeta sin forma de corrida: hasta 42247d4 el simulador nombraba «logs/cma_dev», que no existe
        # (CICLO-cola-nueve-items.md).
        self.assertEqual(sorted(self.nombradas() - set(corridas)), [])

    def test_la_poda_no_las_toca(self):
        logs = self.sb / f"referencia_{next(N)}" / "logs"
        # Las del programa, no las de los generadores: así no se salta en un equipo sin ellos (revisión del encargo 44).
        corridas = sorted(self.mod.CORRIDAS_DE_REFERENCIA)
        # Con «*» en lugar del operador: la de cualquier operador en esa fecha y hora queda.
        for n in corridas:
            for op in ("op_prueba", "otro_op"):
                escribir(logs / n.replace("*", op), "log.txt", "one_f5_1_form.png", "one_f5_guarda.html")
        control = "web_one_op_20250101_000000"                    # más vieja que todas: esa sí se poda
        escribir(logs / control, "log.txt", "one_f5_guarda.html")
        antes = foto(logs)
        borrados, errores = self.mod.podar_html(logs, ahora=datetime.datetime(2030, 1, 1))
        self.assertEqual((borrados, errores), ([f"{control}/one_f5_guarda.html"], []))
        self.assertEqual(foto(logs), {k: v for k, v in antes.items() if k != f"{control}/one_f5_guarda.html"})

    def test_calzan_con_cualquier_operador_y_solo_en_su_fecha(self):
        # Hasta 9710ae2 nombraban al operador de la corrida (CICLO-cola-cuatro-items.md).
        es = self.mod._es_de_referencia
        for n in sorted(self.mod.CORRIDAS_DE_REFERENCIA):
            self.assertEqual(n.count("*"), 1, n)
            for op in ("op_prueba", "otro_op"):
                self.assertTrue(es(n.replace("*", op)), (n, op))
            nombre = n.replace("*", "op_prueba")
            otra_hora = nombre[:-1] + ("1" if nombre.endswith("0") else "0")
            otra_naviera = re.sub(r"^web_[a-z]+_", "web_one_", nombre)
            for ajeno in (otra_hora, otra_naviera, nombre + "_2"):
                self.assertFalse(es(ajeno), ajeno)


# --- La evidencia dentro del panel Reefer de CMA (CICLO-cma-reefer-y-fecha-maersk.md) ---
ABRE_REEFER = "button:has-text('Modifique el reefer')"
GUARDAR_REEFER = ".el-drawer button, [class*='drawer'] button"


class LocPanel:
    """Localizador falso del panel Reefer: existe si su selector está entre los visibles; anota los clics y la
    pregunta de si el botón es del panel visible (_JS_CMA_REEFER_GUARDAR)."""
    first = property(lambda s: s)

    def __init__(self, pagina, sel):
        self.pagina, self.sel = pagina, sel

    def filter(self, has_text=None, visible=None):
        return self

    def evaluate(self, js, *a):
        if js == self.pagina.mod._JS_CMA_REEFER_GUARDAR:
            self.pagina.eventos.append(("js", "del panel"))
            return self.pagina.del_panel
        self.pagina.eventos.append(("js", "desconocido"))
        raise AssertionError("JavaScript desconocido")

    def count(self):
        return 1 if self.sel in self.pagina.visibles else 0

    def is_visible(self, **k):
        return bool(self.count())

    def scroll_into_view_if_needed(self, **k):
        pass

    def click(self, **k):
        self.pagina.eventos.append(("clic", self.sel))

    def fill(self, valor, **k):
        self.pagina.eventos.append(("escribe", valor))


class PanelReefer(Pantalla):
    """Página falsa de CMA con el panel Reefer. Anota en orden cada clic, tecla, espera, captura y lectura del
    HTML; un JavaScript que no conoce hace fallar la prueba. 'del_panel': el botón «Guardar» a la vista es del panel
    visible. Con 'rota', la captura, el HTML y los marcos fallan."""

    def __init__(self, mod, visibles=(ABRE_REEFER, GUARDAR_REEFER), del_panel=True, rota=False):
        super().__init__(html="<body>panel sintetico</body>")
        self.mod, self.visibles, self.del_panel, self.rota, self.eventos = mod, set(visibles), del_panel, rota, []
        self.keyboard = types.SimpleNamespace(press=lambda k: self.eventos.append(("tecla", k)),
                                              type=lambda t, delay=None: self.eventos.append(("escribe", t)))

    @property
    def frames(self):
        if self.rota:
            raise RuntimeError("página cerrada")
        return []

    @frames.setter
    def frames(self, valor):
        pass

    def locator(self, sel):
        return LocPanel(self, sel)

    def wait_for_timeout(self, ms):
        self.eventos.append(("espera", ms))

    def screenshot(self, path=None, full_page=False):
        if self.rota:
            raise RuntimeError("página cerrada")
        self.eventos.append(("captura", Path(path).name, full_page))
        Path(path).write_bytes(b"")

    def evaluate(self, js, *a):
        if js == self.mod._JS_HTML_COMPLETO:
            self.eventos.append(("html",))
            return {"html": "<body>panel sintetico</body>", "sombras": 0}
        if js == self.mod._JS_CMA_REEFER_TEMPERATURA:
            self.eventos.append(("js", "temperatura"))
            return "ok"
        self.eventos.append(("js", "desconocido"))
        raise AssertionError("JavaScript desconocido")


class TestEvidenciaReefer(ConRegistro):
    """Con el panel Reefer abierto y tras guardarlo, la captura de la ventana y el HTML; sin clics, teclas ni
    esperas nuevas, y si la evidencia falla, el panel se configura igual."""
    ABRIR = [("clic", ABRE_REEFER), ("espera", 2000), ("captura", "cma_f5_4b_reefer_drawer.png", False)]
    PANEL = [("captura", "cma_f5_reefer_panel.png", False), ("html",)]
    TEMPERATURA = [("js", "temperatura"), ("tecla", "Control+A"), ("tecla", "Backspace"), ("escribe", "-20"),
                   ("espera", 800)]
    # El «Guardar» a la vista, solo si es del panel visible (CICLO-pendientes-con-evidencia.md).
    GUARDAR = [("js", "del panel"), ("clic", GUARDAR_REEFER), ("espera", 1500)]
    GUARDADO = [("captura", "cma_f5_reefer_guardado.png", False), ("html",)]
    CIERRE = [("tecla", "Escape"), ("espera", 400)]

    def setUp(self):
        super().setUp()
        for env in ("AQUASHIELD_CAPTURA_FULL", "AQUASHIELD_DESCUBRIR"):
            os.environ.pop(env, None)

    def configurar(self, pagina):
        carpeta, reg, vistas = self.corrida()
        r = self.mod._cma_ajustes_reefer(pagina, {"fila": 5}, reg)
        return r, carpeta, self.leer(carpeta, vistas)

    def test_el_panel_abierto_y_tras_guardarlo(self):
        pagina = PanelReefer(self.mod)
        r, carpeta, lugares = self.configurar(pagina)
        self.assertIs(r, True)
        # Lo de siempre, en el mismo orden, con la evidencia intercalada: ni un clic, una tecla ni una espera más.
        self.assertEqual(pagina.eventos, self.ABRIR + self.PANEL + self.TEMPERATURA + self.GUARDAR + self.GUARDADO
                         + self.CIERRE)
        self.assertEqual(sorted(p.name for p in carpeta.iterdir() if "reefer_" in p.name and "4b" not in p.name),
                         ["cma_f5_reefer_guardado.html", "cma_f5_reefer_guardado.png", "cma_f5_reefer_panel.html",
                          "cma_f5_reefer_panel.png"])
        for donde in lugares:
            self.assertIn("evidencia en el panel Reefer: cma_f5_reefer_panel.png y 1 de 1 HTML (la página y 0 "
                          "marco(s); 0 sin raíces shadow)", donde)
            self.assertIn("evidencia tras guardar el panel Reefer: cma_f5_reefer_guardado.png y 1 de 1 HTML", donde)

    def test_sin_el_guardar_del_panel_no_pulsa_ni_deja_lo_guardado(self):
        # Hasta 1e8d510, si el «Guardar» no estaba a la vista, el JavaScript pulsaba el de cualquier cajón, también el
        # de uno oculto, y la evidencia decía «tras guardar». Ahora corta: ni clic ni esa evidencia.
        for visibles, del_panel, pregunta in (((ABRE_REEFER,), True, []),
                                              ((ABRE_REEFER, GUARDAR_REEFER), False, [("js", "del panel")])):
            with self.subTest(visibles=visibles, del_panel=del_panel):
                pagina = PanelReefer(self.mod, visibles=visibles, del_panel=del_panel)
                carpeta, reg, _ = self.corrida()
                with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
                    self.mod._cma_ajustes_reefer(pagina, {"fila": 5}, reg)
                self.assertEqual((e.exception.paso, e.exception.buscaba),
                                 ("Guardar los ajustes Reefer de CMA", "el botón «Guardar» del panel Reefer visible"))
                self.assertEqual(pagina.eventos, self.ABRIR + self.PANEL + self.TEMPERATURA + pregunta)
                self.assertEqual(sorted(p.name for p in carpeta.glob("cma_f5_reefer_guardado.*")), [])
                self.assertTrue((carpeta / "cma_f5_reefer_panel.html").exists())

    def test_si_la_evidencia_falla_el_panel_se_configura_igual(self):
        pagina = PanelReefer(self.mod, rota=True)
        r, _, lugares = self.configurar(pagina)
        self.assertIs(r, True)
        self.assertEqual(pagina.eventos, [("clic", ABRE_REEFER), ("espera", 2000)] + self.TEMPERATURA + self.GUARDAR
                         + self.CIERRE)
        for donde in lugares:
            for momento, nombre in (("en el panel Reefer", "cma_f5_reefer_panel"),
                                    ("tras guardar el panel Reefer", "cma_f5_reefer_guardado")):
                self.assertIn(f"· ⚠ No pude guardar la evidencia {momento} ({nombre}): RuntimeError: página cerrada. "
                              f"{SIGUE}", donde)


# --- La pantalla donde HYUNDAI escribe el Remark (CICLO-evidencia-remark-hyundai.md) ---
class PaginaRemark(Pantalla):
    """Página falsa de HYUNDAI con el Remark por escribir. Anota en orden cada captura, lectura del HTML, JavaScript y
    espera; no sabe hacer clics, teclas ni navegar, y un JavaScript que no conoce hace fallar la prueba. Con 'rota', la
    captura, el HTML y los marcos fallan."""

    def __init__(self, mod, rota=False):
        super().__init__(html="<body>additional information sintetico</body>")
        self.mod, self.rota, self.eventos = mod, rota, []

    @property
    def frames(self):
        if self.rota:
            raise RuntimeError("página cerrada")
        return []

    @frames.setter
    def frames(self, valor):
        pass

    def wait_for_timeout(self, ms):
        self.eventos.append(("espera", ms))

    def screenshot(self, path=None, full_page=False):
        if self.rota:
            raise RuntimeError("página cerrada")
        self.eventos.append(("captura", Path(path).name, full_page))
        Path(path).write_bytes(b"")

    def evaluate(self, js, *a):
        if js == self.mod._JS_HTML_COMPLETO:
            self.eventos.append(("html",))
            return {"html": "<body>additional information sintetico</body>", "sombras": 0}
        if js == self.mod._JS_HMM_REMARK and a == (self.mod.COSCO_REMARK,):
            self.eventos.append(("js", "remark"))
            return "ok"
        self.eventos.append(("js", "desconocido"))
        raise AssertionError("JavaScript desconocido")


class TestEvidenciaRemarkHyundai(ConRegistro):
    """Justo antes de escribir el Remark, HYUNDAI deja la captura de la ventana y el HTML de esa pantalla, sin clics,
    teclas, esperas ni navegación nuevas, y si la evidencia falla, lo avisa y el Remark se escribe igual. Esa evidencia
    cerró el FRENO: desde e423a38 el Remark va al campo de su recuadro (_hmm_remark, test_clics.TestHyundai)."""
    LLAMADA = ("_evidencia_antes_de_la_guarda(page, reg, f'hmm_f{f}_remark', 'antes de escribir el Remark', "
               "completa=False)")
    REMARK = [("js", "remark"), ("espera", 200)]

    def tramo(self):
        """Las dos sentencias que preceden, en reservar_hyundai, a la que escribe el Remark (_hmm_remark), y esa."""
        hallados = []
        for padre in ast.walk(funciones(self.mod)["reservar_hyundai"]):
            for campo in ("body", "orelse", "finalbody"):
                cuerpo = getattr(padre, campo, None)
                if isinstance(cuerpo, list):
                    hallados += [cuerpo[i - 2:i + 1] for i, s in enumerate(cuerpo)
                                 if isinstance(s, ast.Expr) and ast.unparse(s) == "_hmm_remark(page, reg)"]
        self.assertEqual(len(hallados), 1, "el instrumento no ve la sentencia que escribe el Remark")
        return hallados[0]

    def correr(self, pagina):
        """Corre sobre la página falsa las dos sentencias de reservar_hyundai tal como están: la evidencia y la que
        escribe el Remark."""
        _, evidencia, remark = self.tramo()
        carpeta, reg, vistas = self.corrida()
        exec(compile(ast.Module(body=[evidencia, remark], type_ignores=[]), "reservar_hyundai", "exec"),
             {**vars(self.mod), "page": pagina, "reg": reg, "f": 5})
        return carpeta, self.leer(carpeta, vistas)

    def test_va_justo_antes_del_remark_como_sentencia_suelta(self):
        previa, evidencia, _ = self.tramo()
        self.assertEqual(ast.unparse(previa), "_hmm_no_residuo(page, reg)")          # entre medio, nada más
        self.assertIsInstance(evidencia, ast.Expr)                                   # su resultado no decide nada
        self.assertEqual(ast.unparse(evidencia), self.LLAMADA)

    def test_la_ventana_y_el_html_y_despues_el_remark(self):
        pagina = PaginaRemark(self.mod)
        carpeta, lugares = self.correr(pagina)
        # Lo de siempre, con la evidencia delante: ni un clic, una tecla, una espera ni una navegación más.
        self.assertEqual(pagina.eventos, [("captura", "hmm_f5_remark.png", False), ("html",)] + self.REMARK)
        self.assertEqual(sorted(p.name for p in carpeta.iterdir()),
                         ["hmm_f5_remark.html", "hmm_f5_remark.png", "log.txt"])
        for donde in lugares:
            self.assertIn("evidencia antes de escribir el Remark: hmm_f5_remark.png y 1 de 1 HTML (la página y 0 "
                          "marco(s); 0 sin raíces shadow)", donde)
            self.assertNotIn("⚠", donde)

    def test_si_la_evidencia_falla_el_remark_se_escribe_igual(self):
        pagina = PaginaRemark(self.mod, rota=True)
        _, lugares = self.correr(pagina)
        self.assertEqual(pagina.eventos, self.REMARK)
        for donde in lugares:
            self.assertIn("· ⚠ No pude guardar la evidencia antes de escribir el Remark (hmm_f5_remark): RuntimeError: "
                          f"página cerrada. {SIGUE}", donde)


class TestEvidenciaListaHyundai(ConRegistro):
    """Cuando la lista de naves ya cargó y antes de leerla, HYUNDAI deja la captura de la ventana y el HTML de esa
    pantalla, sin clics, teclas, esperas ni navegación nuevas. Hace falta para medir la fecha, el tránsito y los
    transbordos de cada salida (decisión de Marcelo, CICLO-cola-siete-items.md)."""
    LLAMADA = "_evidencia_antes_de_la_guarda(page, reg, f'hmm_f{f}_naves', 'en la lista de naves', completa=False)"

    def tramo(self):
        """La sentencia que precede a la evidencia, la evidencia y la que la sigue, en reservar_hyundai."""
        hallados = []
        for padre in ast.walk(funciones(self.mod)["reservar_hyundai"]):
            cuerpo = getattr(padre, "body", None)
            if isinstance(cuerpo, list):
                hallados += [cuerpo[i - 1:i + 2] for i, s in enumerate(cuerpo)
                             if isinstance(s, ast.Expr) and "hmm_f{f}_naves" in ast.unparse(s)]
        self.assertEqual(len(hallados), 1, "el instrumento no ve la evidencia de la lista de naves")
        return hallados[0]

    def test_va_despues_de_esperar_la_lista_y_antes_de_leerla(self):
        previa, evidencia, siguiente = self.tramo()
        self.assertIsInstance(previa, ast.For)                                       # la espera de «Book Now»
        self.assertIn("Book Now", ast.unparse(previa))
        self.assertIsInstance(evidencia, ast.Expr)                                   # su resultado no decide nada
        self.assertEqual(ast.unparse(evidencia), self.LLAMADA)
        self.assertTrue(ast.unparse(siguiente).startswith("toks = "))               # y enseguida se lee la lista
        f = funciones(self.mod)["reservar_hyundai"]
        lee = min(n.lineno for n in ast.walk(f) if isinstance(n, ast.Call) and "_hmm_elegir_nave" in ast.unparse(n))
        self.assertLess(evidencia.lineno, lee)

    def correr(self, pagina):
        _, evidencia, _ = self.tramo()
        carpeta, reg, vistas = self.corrida()
        exec(compile(ast.Module(body=[evidencia], type_ignores=[]), "reservar_hyundai", "exec"),
             {**vars(self.mod), "page": pagina, "reg": reg, "f": 25})
        return carpeta, self.leer(carpeta, vistas)

    def test_la_ventana_y_el_html_sin_clics(self):
        pagina = PaginaRemark(self.mod)
        carpeta, lugares = self.correr(pagina)
        self.assertEqual(pagina.eventos, [("captura", "hmm_f25_naves.png", False), ("html",)])
        self.assertEqual(sorted(p.name for p in carpeta.iterdir()), ["hmm_f25_naves.html", "hmm_f25_naves.png", "log.txt"])
        for donde in lugares:
            self.assertIn("evidencia en la lista de naves: hmm_f25_naves.png y 1 de 1 HTML (la página y 0 marco(s); 0 sin "
                          "raíces shadow)", donde)

    def test_si_la_evidencia_falla_sigue_igual(self):
        pagina = PaginaRemark(self.mod, rota=True)
        _, lugares = self.correr(pagina)
        self.assertEqual(pagina.eventos, [])
        for donde in lugares:
            self.assertIn("· ⚠ No pude guardar la evidencia en la lista de naves (hmm_f25_naves): RuntimeError: página "
                          f"cerrada. {SIGUE}", donde)


class TestEvidenciaValidarRutaCma(ConRegistro):
    """«Validar ruta» sigue sin respuesta del portal. Al terminar la espera que ya existe tras pulsarlo, y después de leer
    su aviso, CMA deja la captura de la ventana y el HTML de esa pantalla, sin clics, teclas, esperas ni navegación
    nuevas; si guardarla falla, lo avisa y la reserva sigue (decisión de Marcelo, CICLO-cola-tres-items.md)."""
    LLAMADA = ("_evidencia_antes_de_la_guarda(page, reg, f'cma_f{f}_validar_{modo}', 'tras «Validar ruta»', "
               "completa=False)")

    def tramo(self):
        """En reservar_cma, las cuatro sentencias que preceden a la evidencia, la evidencia y la que la sigue."""
        hallados = []
        for padre in ast.walk(funciones(self.mod)["reservar_cma"]):
            cuerpo = getattr(padre, "body", None)
            if isinstance(cuerpo, list):
                hallados += [cuerpo[i - 4:i + 2] for i, s in enumerate(cuerpo)
                             if isinstance(s, ast.Expr) and "cma_f{f}_validar_" in ast.unparse(s)]
        self.assertEqual(len(hallados), 1, "el instrumento no ve la evidencia de «Validar ruta»")
        return hallados[0]

    def test_va_al_terminar_la_espera_y_tras_leer_el_aviso(self):
        validar, deshabilitado, captura, aviso, evidencia, siguiente = self.tramo()
        # «Validar ruta» y su espera (_validar, que termina en _cma_esperar_resultado), el corte si quedó deshabilitado,
        # la captura de siempre y la lectura del aviso, que decide el camino en el mismo instante que antes.
        self.assertEqual(ast.unparse(validar), "estado = _validar()")
        self.assertIsInstance(deshabilitado, ast.If)
        self.assertEqual(ast.unparse(deshabilitado.test), "estado == 'deshabilitado'")
        self.assertTrue(ast.unparse(captura).startswith("reg.captura(page, f'cma_f{f}_3_itinerarios_{modo}'"))
        self.assertEqual(ast.unparse(aviso), "ultimo_aviso = _cma_aviso(page)")
        self.assertIsInstance(evidencia, ast.Expr)                                   # su resultado no decide nada
        self.assertEqual(ast.unparse(evidencia), self.LLAMADA)
        self.assertIsInstance(siguiente, ast.If)
        self.assertIn("no matching", ast.unparse(siguiente.test))                    # y enseguida, el camino de siempre

    def correr(self, pagina):
        evidencia = self.tramo()[4]
        carpeta, reg, vistas = self.corrida()
        exec(compile(ast.Module(body=[evidencia], type_ignores=[]), "reservar_cma", "exec"),
             {**vars(self.mod), "page": pagina, "reg": reg, "f": 15, "modo": "puerto"})
        return carpeta, self.leer(carpeta, vistas)

    def test_la_ventana_y_el_html_sin_clics(self):
        pagina = PaginaRemark(self.mod)
        carpeta, lugares = self.correr(pagina)
        self.assertEqual(pagina.eventos, [("captura", "cma_f15_validar_puerto.png", False), ("html",)])
        self.assertEqual(sorted(p.name for p in carpeta.iterdir()),
                         ["cma_f15_validar_puerto.html", "cma_f15_validar_puerto.png", "log.txt"])
        for donde in lugares:
            self.assertIn("evidencia tras «Validar ruta»: cma_f15_validar_puerto.png y 1 de 1 HTML (la página y 0 "
                          "marco(s); 0 sin raíces shadow)", donde)

    def test_si_la_evidencia_falla_sigue_igual(self):
        pagina = PaginaRemark(self.mod, rota=True)
        _, lugares = self.correr(pagina)
        self.assertEqual(pagina.eventos, [])
        for donde in lugares:
            self.assertIn("· ⚠ No pude guardar la evidencia tras «Validar ruta» (cma_f15_validar_puerto): RuntimeError: "
                          f"página cerrada. {SIGUE}", donde)


# Las tres opciones del modal «Alternate Vessel Option», medidas en hmm_f<fila>_otra_nave.html (2026-09-26).
OPCIONES_MEDIDAS = ("Book on next Available Vessel. (Any)", "Book on Next Available Vessel. (if within 2 weeks)",
                    "I do not want to choose an alternate vessel")


class PaginaModalHmm(PaginaRemark):
    """Página falsa de HYUNDAI después de elegir la nave, con el modal «Alternate Vessel Option» a la vista o no. Sus
    opciones son 'opciones' (el texto de cada label.radio-area) y pulsar una la marca (con 'marca' en False, no); su OK
    dice 'ok' (None: no está). Anota cada mirada, clic, captura y HTML; con 'ciega', mirar falla."""

    def __init__(self, mod, modal, opciones=OPCIONES_MEDIDAS, marca=True, ok="OK", rota=False, ciega=False):
        super().__init__(mod, rota=rota)
        self.modal, self.opciones, self.marca, self.ok, self.ciega = modal, list(opciones), marca, ok, ciega
        self.marcada = None

    def locator(self, sel):
        return LocModal(self, sel)


class LocModal:
    """Localizador falso del modal: su OK visto desde afuera, sus opciones y su OK de adentro, filtrados por texto."""

    def __init__(self, pagina, sel, texto=None):
        self.pagina, self.sel, self.texto = pagina, sel, texto

    def elementos(self):
        p = self.pagina
        if self.sel == "#vesselOptionSubmit":
            base = ["OK"] if p.modal else []
        elif self.sel == "#alternate_vessel_opt label.radio-area":
            base = p.opciones if p.modal else []
        elif self.sel == "#alternate_vessel_opt #vesselOptionSubmit":
            base = [p.ok] if p.modal and p.ok is not None else []
        else:
            raise AssertionError(f"selector inesperado: {self.sel}")
        return [e for e in base if self.texto is None or self.texto.search(e)]

    def filter(self, has_text=None):
        return LocModal(self.pagina, self.sel, has_text)

    @property
    def first(self):
        return self

    def count(self):
        return len(self.elementos())

    def is_visible(self, timeout=None):
        self.pagina.eventos.append(("mira", self.sel))
        if self.pagina.ciega:
            raise RuntimeError("marco cerrado")
        return bool(self.elementos())

    def click(self, *a, **k):
        e = self.elementos()[0]
        self.pagina.eventos.append(("clic", e))
        if self.sel.endswith("label.radio-area") and self.pagina.marca:
            self.pagina.marcada = e

    def locator(self, sel):
        pagina, e = self.pagina, (self.elementos() or [None])[0]
        return types.SimpleNamespace(is_checked=lambda: pagina.marcada is not None and pagina.marcada == e)


class TestModalHyundai(ConRegistro):
    """Después de elegir la nave, HYUNDAI muestra el modal «Alternate Vessel Option». Decisión de Marcelo
    (CICLO-ampliar-la-busqueda.md): marcar «I do not want to choose an alternate vessel», por su texto, y pulsar OK; si esa
    opción no está, NO ENVIADA con «HYUNDAI no ofreció la opción de mantener la nave pedida; la reserva no se envió». Antes
    de marcar deja la captura de la ventana y el HTML. Si el modal sigue después del OK, no pulsa nada más (su FRENO).
    Hasta a198645 pulsaba el OK con lo que viniera marcado; hasta 4cae528 no pulsaba nada y cortaba."""
    MIRA = ("mira", "#vesselOptionSubmit")
    MANTENER = "I do not want to choose an alternate vessel"
    SIN_OPCION = "HYUNDAI no ofreció la opción de mantener la nave pedida; la reserva no se envió"
    EVIDENCIA = [("captura", "hmm_f25_otra_nave.png", False), ("html",)]

    def test_marca_mantener_la_nave_y_pulsa_ok(self):
        pagina = PaginaModalHmm(self.mod, modal=True)
        carpeta, reg, vistas = self.corrida()
        self.assertEqual(self.mod._hmm_mantener_nave(pagina, reg, 25), "marcada")
        # Lo mira, deja la evidencia, marca la opción por su texto y pulsa OK: nada más.
        self.assertEqual(pagina.eventos, [self.MIRA] + self.EVIDENCIA + [("clic", self.MANTENER), ("clic", "OK")])
        self.assertEqual(pagina.marcada, self.MANTENER)
        log, pantalla = self.leer(carpeta, vistas)
        for donde in (log, pantalla):
            self.assertIn("· HYUNDAI mostró el modal «Alternate Vessel Option»: marco que no quiero otra nave y pulso OK.",
                          donde)
        self.assertIn("modal 'Alternate Vessel Option': marqué «I do not want to choose an alternate vessel» y pulsé OK", log)
        self.assertEqual(self.mod.HMM_OPCION_MANTENER, self.MANTENER)

    def test_sin_la_opcion_no_pulsa_y_no_envia(self):
        # Sin ella, o con otro texto (solo la exacta, sin distinguir los espacios de los extremos), no pulsa nada.
        for opciones in (OPCIONES_MEDIDAS[:2], OPCIONES_MEDIDAS[:2] + (self.MANTENER + " (beta)",),
                         OPCIONES_MEDIDAS[:2] + ("Any: " + self.MANTENER,)):
            with self.subTest(opciones=opciones):
                pagina = PaginaModalHmm(self.mod, modal=True, opciones=opciones)
                carpeta, reg, vistas = self.corrida()
                self.assertEqual(self.mod._hmm_mantener_nave(pagina, reg, 25), ("NO ENVIADA", self.SIN_OPCION))
                self.assertEqual(pagina.eventos, [self.MIRA] + self.EVIDENCIA)
                for donde in self.leer(carpeta, vistas):
                    self.assertIn(f"· ✗ NO ENVIADA · {self.SIN_OPCION}", donde)
        self.assertEqual(self.mod.HMM_SIN_OPCION, self.SIN_OPCION)
        pagina = PaginaModalHmm(self.mod, modal=True, opciones=OPCIONES_MEDIDAS[:2] + ("  " + self.MANTENER + " ",))
        carpeta, reg, vistas = self.corrida()
        self.assertEqual(self.mod._hmm_mantener_nave(pagina, reg, 25), "marcada")

    def test_si_el_clic_no_la_marca_o_no_hay_ok(self):
        casos = (({"marca": False}, "HYUNDAI: el clic en «I do not want to choose an alternate vessel» no la dejó marcada; "
                                    "no pulsé OK y la reserva no se envió"),
                 ({"ok": None}, "HYUNDAI: marqué «I do not want to choose an alternate vessel», pero no encontré un solo "
                                "botón «OK» en el modal; no pulsé nada más y la reserva no se envió"),
                 ({"ok": "Aceptar"}, "HYUNDAI: marqué «I do not want to choose an alternate vessel», pero no encontré un "
                                     "solo botón «OK» en el modal; no pulsé nada más y la reserva no se envió"))
        for estado, detalle in casos:
            with self.subTest(estado=estado):
                pagina = PaginaModalHmm(self.mod, modal=True, **estado)
                carpeta, reg, vistas = self.corrida()
                self.assertEqual(self.mod._hmm_mantener_nave(pagina, reg, 25), ("NO ENVIADA", detalle))
                self.assertEqual(pagina.eventos, [self.MIRA] + self.EVIDENCIA + [("clic", self.MANTENER)])

    def test_sin_el_modal_sigue_sin_evidencia(self):
        for ciega, ya, linea in ((False, False, "modal 'Alternate Vessel Option': no apareció"),
                                 (True, False, "modal 'Alternate Vessel Option': no pude mirarlo (marco cerrado)"),
                                 (False, True, "modal 'Alternate Vessel Option': no apareció")):
            with self.subTest(ciega=ciega, ya=ya):
                pagina = PaginaModalHmm(self.mod, modal=False, ciega=ciega)
                carpeta, reg, vistas = self.corrida()
                self.assertIsNone(self.mod._hmm_mantener_nave(pagina, reg, 25, ya=ya))
                self.assertEqual(pagina.eventos, [self.MIRA])
                self.assertEqual(sorted(p.name for p in carpeta.iterdir()), ["log.txt"])
                self.assertIn(linea, self.leer(carpeta, vistas)[0])

    def test_si_el_modal_sigue_despues_del_ok_no_pulsa_mas(self):
        # El FRENO de Marcelo: si marcar la opción no deja avanzar sin otro clic nuevo, se frena: NO ENVIADA, con la
        # evidencia, y ningún clic.
        pagina = PaginaModalHmm(self.mod, modal=True)
        carpeta, reg, vistas = self.corrida()
        r = self.mod._hmm_mantener_nave(pagina, reg, 25, ya=True)
        self.assertEqual(r, ("NO ENVIADA", self.mod.HMM_NO_AVANZO))
        self.assertEqual(pagina.eventos, [self.MIRA, ("captura", "hmm_f25_otra_nave_sigue.png", False), ("html",)])
        self.assertEqual(self.mod.HMM_NO_AVANZO, "HYUNDAI siguió mostrando el modal «Alternate Vessel Option» después de "
                                                 "marcar «I do not want to choose an alternate vessel» y pulsar OK; no pulsé "
                                                 "nada más y la reserva no se envió")

    def test_si_la_evidencia_falla_igual_marca(self):
        pagina = PaginaModalHmm(self.mod, modal=True, rota=True)
        carpeta, reg, vistas = self.corrida()
        self.assertEqual(self.mod._hmm_mantener_nave(pagina, reg, 25), "marcada")
        self.assertEqual(pagina.eventos, [self.MIRA, ("clic", self.MANTENER), ("clic", "OK")])
        for donde in self.leer(carpeta, vistas):
            self.assertIn("· ⚠ No pude guardar la evidencia con el modal «Alternate Vessel Option» (hmm_f25_otra_nave): "
                          f"RuntimeError: página cerrada. {SIGUE}", donde)

    def test_los_lugares_en_el_reservador(self):
        # En el mismo momento que antes: 1,5 s después de elegir la nave, antes de esperar Booking Details; y, si no
        # aparece en 12 s, lo primero, antes de esperarlo 5 s más. La segunda vez sabe si ya marcó la opción. Si la
        # marcó recién esa segunda vez (el modal apareció tarde) y Booking Details sigue sin aparecer, una tercera, que
        # ya la marcó: si el modal sigue, es el FRENO. Hasta e8b027b quedaba REVISAR sin mirarlo (revisión del encargo 32).
        f = funciones(self.mod)["reservar_hyundai"]
        lugares = []
        for padre in ast.walk(f):
            cuerpo = getattr(padre, "body", None)
            if isinstance(cuerpo, list):
                lugares += [(padre, cuerpo, i) for i, s in enumerate(cuerpo)
                            if isinstance(s, ast.Assign) and "_hmm_mantener_nave" in ast.unparse(s)]
        self.assertEqual(len(lugares), 3, "el instrumento no ve los tres lugares")
        (padre1, cuerpo1, i1), (padre2, cuerpo2, i2), (padre3, cuerpo3, i3) = sorted(
            lugares, key=lambda x: x[1][x[2]].lineno)
        self.assertEqual(ast.unparse(cuerpo1[i1]), "modal = _hmm_mantener_nave(page, reg, f)")
        self.assertEqual(ast.unparse(cuerpo2[i2]), "modal = _hmm_mantener_nave(page, reg, f, ya=modal == 'marcada')")
        self.assertEqual(ast.unparse(cuerpo3[i3]), "modal = _hmm_mantener_nave(page, reg, f, ya=True)")
        guarda = min(n.lineno for n in ast.walk(f) if isinstance(n, ast.If) and "es_modo_emision" in ast.unparse(n.test))
        for cuerpo, i in ((cuerpo1, i1), (cuerpo2, i2), (cuerpo3, i3)):
            self.assertEqual(ast.unparse(cuerpo[i + 1]), "if isinstance(modal, tuple):\n    return modal")
            self.assertLess(cuerpo[i].lineno, guarda)
        self.assertEqual(ast.unparse(cuerpo1[i1 - 2].test), "tipo_sel == 'book_now'")
        self.assertEqual(ast.unparse(cuerpo1[i1 - 1]), "esperar(page, 1.5)")
        self.assertEqual(ast.unparse(cuerpo1[i1 + 2]), "ok_step3 = False")
        self.assertEqual((ast.unparse(padre2.test), i2), ("not ok_step3", 0))
        self.assertTrue(ast.unparse(cuerpo2[i2 + 2]).startswith("for _ in range(5):"))
        # La tercera, justo después de esa espera, solo si la segunda la marcó, y nada más en su if.
        self.assertIs(cuerpo2[i2 + 3], padre3)
        self.assertEqual((ast.unparse(padre3.test), i3, len(cuerpo3)), ("not ok_step3 and modal == 'marcada'", 0, 2))
        # Nada más en el módulo nombra su botón: ni otra función ni una constante de JavaScript.
        arbol = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        nombran = {n.name if isinstance(n, ast.FunctionDef) else ast.unparse(n.targets[0])
                   for n in arbol.body if isinstance(n, (ast.FunctionDef, ast.Assign))
                   for c in ast.walk(n) if isinstance(c, ast.Constant) and "vesselOption" in str(c.value)}
        self.assertEqual(nombran, {"_hmm_mantener_nave"})


class PaginaRutasCma(PaginaRemark):
    """«Route choices» falsa de CMA: los botones de selección ya están; cada lectura de la lista responde lo que sigue en
    'lecturas'. El enlace «Cargar 10 siguientes resultados» está mientras queden lecturas, y pulsarlo suma 10 rutas.
    Anota en orden capturas, HTML, JavaScript, clics y esperas."""

    def __init__(self, mod, lecturas):
        super().__init__(mod)
        self.lecturas, self.rutas = list(lecturas), 10

    def locator(self, sel):
        if sel != "a, button, [role=link], [role=button]":
            return types.SimpleNamespace(count=lambda: 1)
        pagina = self
        enlace = types.SimpleNamespace(is_visible=lambda: True, scroll_into_view_if_needed=lambda **k: None,
                                       click=lambda **k: (pagina.eventos.append(("clic", "cargar más")),
                                                          setattr(pagina, "rutas", pagina.rutas + 10)))
        hay = lambda rx: pagina.lecturas and rx.search("Cargar 10 siguientes resultados")
        return types.SimpleNamespace(filter=lambda has_text=None: types.SimpleNamespace(
            count=lambda: 1 if hay(has_text) else 0, nth=lambda j: enlace))

    def evaluate(self, js, *a):
        if js == self.mod._JS_HTML_COMPLETO:
            self.eventos.append(("html",))
            return {"html": "<body>rutas sinteticas</body>", "sombras": 0}
        if "getCard(" in js:                     # hasta 9051f43 se reconocía por «sigToks», que ya no está
            self.eventos.append(("js", "leer"))
            return self.lecturas.pop(0)
        if js == self.mod._JS_CMA_CONTAR:
            self.eventos.append(("js", "contar"))
            return self.rutas
        if js == self.mod._JS_CMA_FECHAS:
            self.eventos.append(("js", "fechas"))
            return ["Lunes, 06-oct-2026", "Viernes, 10-oct-2026"]
        self.eventos.append(("js", "desconocido"))
        raise AssertionError("JavaScript desconocido")


class TestEvidenciaRutasCma(ConRegistro):
    """Antes de leer «Route choices», CMA deja la captura de la ventana y el HTML de la lista; si no encontró la nave y
    cargó más rutas, deja también la de cada carga (decisiones de Marcelo, CICLO-cola-siete-items.md y
    CICLO-ampliar-msc-y-cma.md)."""
    NO = {"ok": False, "match": False, "cardsCount": 2, "ofrecidas": ["NAVE OTRA"], "msg": "nave no encontrada"}
    SI = {"ok": True, "match": True, "vessel": "NAVE PRUEBA", "msg": "nave seleccionada: NAVE PRUEBA"}

    def elegir(self, lecturas):
        carpeta, reg, vistas = self.corrida()
        pagina = PaginaRutasCma(self.mod, lecturas)
        r = self.mod._cma_seleccionar_itinerario(pagina, {"fila": 15, "nave": "NAVE PRUEBA"}, reg)
        return r, pagina.eventos, carpeta, self.leer(carpeta, vistas)

    def test_la_lista_antes_de_leerla(self):
        r, eventos, carpeta, lugares = self.elegir([self.SI])
        self.assertEqual(r, (True, "nave seleccionada: NAVE PRUEBA"))
        self.assertEqual(eventos, [("captura", "cma_f15_rutas.png", False), ("html",), ("js", "leer"), ("espera", 2500)])
        self.assertEqual(sorted(p.name for p in carpeta.iterdir()), ["cma_f15_rutas.html", "cma_f15_rutas.png", "log.txt"])
        for donde in lugares:
            self.assertIn("evidencia en la lista de rutas: cma_f15_rutas.png y 1 de 1 HTML", donde)

    def test_y_otra_tras_cada_carga(self):
        # «Cargar N siguientes resultados» hasta encontrarla, y la evidencia de cada lista (CICLO-ampliar-msc-y-cma.md).
        # Hasta el encargo 33, «Mostrar más viajes» una sola vez (Nota H23), y la segunda lista era la última.
        r, eventos, carpeta, lugares = self.elegir([self.NO, self.NO, self.SI])
        self.assertEqual(r, (True, "nave seleccionada: NAVE PRUEBA"))
        cargar = [("js", "contar"), ("clic", "cargar más"), ("espera", 1000), ("js", "contar")]
        self.assertEqual(eventos, [("captura", "cma_f15_rutas.png", False), ("html",), ("js", "leer")] + cargar
                         + [("captura", "cma_f15_rutas_mas.png", False), ("html",), ("js", "leer")] + cargar
                         + [("captura", "cma_f15_rutas_mas2.png", False), ("html",), ("js", "leer"), ("espera", 2500)])
        self.assertEqual(sorted(p.name for p in carpeta.iterdir()),
                         ["cma_f15_rutas.html", "cma_f15_rutas.png", "cma_f15_rutas_mas.html", "cma_f15_rutas_mas.png",
                          "cma_f15_rutas_mas2.html", "cma_f15_rutas_mas2.png", "log.txt"])
        self.assertIn("búsqueda ampliada: 20 -> 30 rutas", lugares[0])

    def test_hasta_que_el_enlace_desaparece(self):
        # Sin el enlace, no hay más: el aviso dice hasta qué fecha buscó, la última salida que mostró la lista.
        r, eventos, _, _ = self.elegir([self.NO])
        self.assertEqual(r, (False, "CMA: nave 'NAVE PRUEBA' no disponible en el portal: busqué hasta el 10-10-2026, la "
                                    "última salida que mostró el portal, y ya no vi el enlace «Cargar … siguientes "
                                    "resultados» (rutas ofrecidas: NAVE OTRA). No se seleccionó nave errónea."))
        self.assertEqual(eventos[-3:], [("js", "leer"), ("js", "contar"), ("js", "fechas")])


# --- La lista de sugerencias de origen y de destino, antes de elegir (CICLO-origen-y-destino.md) ---
# Sintética: trae «PUERT», el código del puerto que pide CMA y, antes de su primera coma, lo escrito, como pide MAERSK
# desde el encargo 43 (su tipo de lugar, Container Yard, lo lleva la página falsa: PaginaSugerencias). Hasta ahí,
# «PUERTO ALFA ; XX ; XXPAL» y «PUERTO ALFA NORTE ; XX ; XXPAN».
SUGERIDA = "PUERTO ALFA, PAIS ; XX ; XXPAL"
OTRA = "PUERTO ALFA (NORTE), PAIS ; XX ; XXPAN"   # la que queda si la lista cambia mientras se guarda la evidencia
# Los campos donde escribe cada ayudante: un clic ahí es el del campo; en otro lado, un clic que queda anotado.
CAMPOS = ("input[placeholder*='Origin' i]", "input[name='POLId_input']", "#schOriginText", "#mc-input-origin", "#pol",
          "input[placeholder*='entrega' i], input[placeholder*='delivery' i]")


class Oculto:
    """Localizador de Playwright que no se ve (el «Got it» de MAERSK)."""
    first = property(lambda s: s)

    def is_visible(self, **k):
        return False


class LocSugerencias:
    """Localizador falso de PaginaSugerencias: el campo donde se escribe (uno de CAMPOS), la lista de sugerencias (uno
    de OPCIONES), con los filtros de texto que se le pidan, u otro elemento, cuyo clic queda anotado. Como el has_text
    de Playwright, cada filtro mira el texto de la sugerencia y su raíz shadow (su tipo de lugar en MAERSK);
    text_content y all_text_contents, solo el texto (encargo 43). Con 'campo_falla' de la página, cada acción sobre lo
    que no es la lista falla; con 'campo_oculto', además, no se ve."""
    OPCIONES = ("mc-option:visible", ".el-autocomplete-suggestion:visible li:visible")
    first = property(lambda s: s)

    def __init__(self, pagina, sel, filtros=(), indice=0):
        self.pagina, self.sel, self.filtros, self.indice = pagina, sel, tuple(filtros), indice

    def pares(self):
        return [(t, s) for t, s in self.pagina.lista() if all(re.search(f, f"{t} {s}") for f in self.filtros)]

    def opciones(self):
        return [t for t, _ in self.pares()]

    def responde(self):
        if self.pagina.campo_falla and self.sel not in self.OPCIONES:
            raise RuntimeError("el campo no responde")

    def filter(self, has_text=None, **k):
        return LocSugerencias(self.pagina, self.sel, self.filtros + (has_text,))

    def nth(self, i):
        return LocSugerencias(self.pagina, self.sel, self.filtros, i)

    def count(self):
        return len(self.opciones()) if self.sel in self.OPCIONES else 1

    def is_visible(self, **k):
        return not (self.pagina.campo_oculto and self.sel not in self.OPCIONES)

    def text_content(self):
        return self.opciones()[self.indice]

    def all_text_contents(self):
        return self.opciones()

    def click(self, **k):
        if self.sel in self.OPCIONES:
            texto, tipo = self.pares()[self.indice]
            self.pagina.tipo_pulsado = tipo
            self.pagina.pulsar(texto)
        else:
            self.responde()
            self.pagina.eventos.append(("campo",) if self.sel in CAMPOS else ("clic", self.sel))

    def type(self, texto, **k):
        self.responde()
        self.pagina.escribir(texto)

    def fill(self, texto, **k):
        self.responde()
        self.pagina.valor = texto

    def input_value(self, **k):
        return self.pagina.leer_campo()

    def wait_for(self, **k):
        self.responde()

    def scroll_into_view_if_needed(self, **k):
        self.responde()


class MarcoSugerencias:
    """El marco del formulario de COSCO: la lista de sugerencias está en él, no en su página, y él no sabe capturar."""

    def __init__(self, pagina):
        self.page, self.url = pagina, "https://portal.invalid/bkg2"

    def evaluate(self, js, *a):
        return self.page.responder(js, a[0] if a else None, marco=True)

    def wait_for_timeout(self, ms):
        self.page.wait_for_timeout(ms)


class PaginaSugerencias(Pantalla):
    """Página falsa con el campo de origen o de destino y su lista de sugerencias, que aparece tras 'aparece' esperas y
    'escritos' escrituras, o recién al pulsar, con 'al_pulsar'. Responde a los localizadores de MAERSK y CMA y al
    JavaScript que elige de ONE, MSC, HYUNDAI y COSCO, que pulsa solo con la marca true, y si no, dice cuál pulsaría (o
    falla, con 'lectura_falla'). Anota en orden todo lo que se le hace: el clic en el campo, lo escrito, cada espera,
    cada tecla, cada captura (y si la lista estaba a la vista), cada HTML (el del marco aparte), cada sugerencia pulsada
    y cualquier otro clic. Con 'cambia', la lista cambia mientras se guarda el HTML de la evidencia. Los primeros
    'fallos' clics en la sugerencia fallan; los primeros 'borra' borran el campo, y los primeros 'no_la_toma' lo dejan
    con lo escrito. Con 'marco', la lista está en un marco aparte (COSCO); si no, la página hace también de marco. Con
    'se_mueve', ONE describe la que pulsa con otra clase y otra posición: la clase la lee después del clic. Con
    'campo_falla', el campo no responde: cada acción sobre él falla, y el JavaScript con que COSCO escribe dice que no
    lo encontró (o falla, con «lanza»); con 'campo_oculto', además, no se ve. Un JavaScript que no conoce queda en
    'inesperados'. La sugerencia lleva en su raíz shadow 'tipo' (en MAERSK, su tipo de lugar: el filtro has_text de
    Playwright lo ve, text_content no), y 'extra' son otras sugerencias a la vista con ella, cada una (texto, tipo);
    'tipo_pulsado' dice el de la que se pulsó (encargo 43). Con 'tarde' (esperas, [(texto, tipo)]), esas aparecen
    después de esas esperas; con 'tarda', las primeras lecturas del campo después del clic todavía traen lo escrito;
    y con 'campo_como', el campo queda con la sugerencia pasada por esa función (revisión de código del encargo 43)."""

    def __init__(self, mod, aparece=2, escritos=0, al_pulsar=False, cambia=False, fallos=0, borra=0, no_la_toma=0,
                 lectura_falla=False, marco=False, se_mueve=False, campo_falla=False, campo_oculto=False,
                 tipo="Container Yard", extra=(), tarde=None, tarda=0, campo_como=None):
        super().__init__(html="<body>lista de sugerencias sintetica</body>", url="https://portal.invalid/ruta")
        self.mod, self.aparece, self.minimo_escritos, self.al_pulsar = mod, aparece, escritos, al_pulsar
        self.cambia, self.fallos, self.borra, self.no_la_toma = cambia, fallos, borra, no_la_toma
        self.lectura_falla, self.eventos, self.inesperados, self.se_mueve = lectura_falla, [], [], se_mueve
        self.campo_falla, self.campo_oculto = campo_falla, campo_oculto
        self.tipo, self.extra, self.tipo_pulsado = tipo, list(extra), None
        self.tarde, self.tarda, self.campo_como, self.por_leer, self.valor_tarde = tarde, tarda, campo_como, 0, None
        self.valor, self.opcion, self.escritos, self.a_la_vista = "", SUGERIDA, 0, False
        self.keyboard = types.SimpleNamespace(press=lambda tecla: self.eventos.append(("tecla", tecla)))
        self.marco = MarcoSugerencias(self) if marco else None
        self.frames = [self.marco] if marco else []
        self.page = self

    def lista(self):
        """Las sugerencias a la vista, cada una (su texto, el de su raíz shadow: su tipo de lugar en MAERSK)."""
        vista = self.a_la_vista or (self.esperas >= self.aparece and self.escritos >= self.minimo_escritos)
        tarde = list(self.tarde[1]) if self.tarde and self.esperas >= self.tarde[0] else []
        return [(self.opcion, self.tipo)] + self.extra + tarde if vista else []

    def leer_campo(self):
        """Lo que trae el campo: con 'tarda', lo escrito en las primeras lecturas después del clic."""
        if self.por_leer:
            self.por_leer -= 1
        elif self.valor_tarde is not None:
            self.valor, self.valor_tarde = self.valor_tarde, None
        return self.valor

    def wait_for_timeout(self, ms):
        self.esperas += 1
        self.eventos.append(("espera",))

    def screenshot(self, path=None, full_page=False):
        self.eventos.append(("captura", Path(path).name, full_page, bool(self.lista())))
        Path(path).write_bytes(b"")

    def locator(self, sel):
        return LocSugerencias(self, sel)

    def get_by_role(self, *a, **k):
        return Oculto()

    def get_by_text(self, texto, **k):
        return LocSugerencias(self, f"text={texto}")

    def escribir(self, texto):
        self.escritos += 1
        self.eventos.append(("escribe", texto))
        self.valor = texto

    def pulsar(self, texto):
        if self.fallos:
            self.fallos -= 1
            raise RuntimeError("el clic no salió")
        self.eventos.append(("pulsa", texto))
        if self.borra:
            self.borra -= 1
            self.valor = ""
        elif self.no_la_toma:
            self.no_la_toma -= 1                     # el campo sigue con lo escrito
        elif self.tarda:
            self.valor_tarde = self.campo_como(texto) if self.campo_como else texto
            self.por_leer, self.tarda = self.tarda, 0
        else:
            self.valor = self.campo_como(texto) if self.campo_como else texto

    def evaluate(self, js, *a):
        return self.responder(js, a[0] if a else None, marco=False)

    def responder(self, js, args, marco):
        m = self.mod
        if "getHTML" in js:
            self.eventos.append(("html", "marco") if marco else ("html",))
            if self.cambia and not marco:
                self.opcion = OTRA
            return {"html": "<body>lista de sugerencias sintetica</body>", "sombras": 0}
        if js == m._JS_ONE_CERRAR_MODAL:
            return False
        if js == m._JS_COSCO_AUTO_SET:
            if self.campo_falla == "lanza":
                raise RuntimeError("el marco no responde")
            if self.campo_falla:
                return "no-input"
            self.escribir(args[1])
            return "set"
        if "pulsar" not in js:
            self.inesperados.append(js[:40])
            return None
        de_one = js == m._JS_PICK_SUGGESTION
        if js == m._JS_COSCO_AUTO_PICK:
            pulsa = len(args) > 2 and args[2] is True
        else:
            pulsa = len(args) > 1 and args[1] is True
        if not pulsa and self.lectura_falla:
            raise RuntimeError("la página cambió")
        if pulsa and self.al_pulsar:
            self.a_la_vista = True
        if (self.marco is not None and not marco) or not self.lista():     # la de COSCO, solo en su marco
            return "CLICK[] CANDS[]" if de_one and pulsa else ""
        cual = f"LI.opcion#120 «{self.opcion}»" if de_one else self.opcion
        if not pulsa:
            return cual
        self.pulsar(self.opcion)
        if de_one and self.se_mueve:
            cual = f"LI.opcion activa#118 «{self.opcion}»"
        return f"CLICK[{cual}] CANDS[{cual}]" if de_one else self.opcion


class TestListaDeSugerencias(ConRegistro):
    """Antes de elegir una sugerencia de origen o de destino, las seis navieras dejan la captura de la ventana y el HTML
    de la página y de sus marcos, con la lista (decisión de Marcelo, CICLO-origen-y-destino.md): solo con 'evidencia',
    una vez por lista, justo antes de pulsar la misma sugerencia que pulsarían sin ella, y sin otro clic, tecla ni
    espera. La regla con que eligen no cambia. ONE, MSC, HYUNDAI y COSCO eligen y pulsan en un mismo JavaScript: lo
    corren antes sin pulsar, para saber si hay una. Después del clic avisan si pulsaron sin dejarla, o si la lista
    cambió mientras la guardaban (revisión del encargo 41)."""
    AYUDANTES = ("_fill_autocomplete", "_msc_puerto", "_cosco_autocomplete", "_hmm_autocomplete", "_mk_ciudad",
                 "_cma_puerto", "_cma_entrega")
    CON_JAVASCRIPT = ("_fill_autocomplete", "_msc_puerto", "_cosco_autocomplete", "_hmm_autocomplete")
    ETIQUETA = {"_msc_puerto": "Port of Load", "_cosco_autocomplete": "Destination", "_cma_entrega": "Lugar de entrega"}
    # Lo que hace cada ayudante después del clic, con la lista a la vista desde la segunda espera.
    DESPUES = {"_fill_autocomplete": [("espera",)], "_msc_puerto": [("espera",)], "_cosco_autocomplete": [],
               "_hmm_autocomplete": [], "_mk_ciudad": [("espera",), ("espera",)],
               "_cma_puerto": [("espera",), ("tecla", "Tab"), ("espera",)],
               "_cma_entrega": [("espera",), ("tecla", "Escape")]}

    def pagina(self, ayudante, **k):
        return PaginaSugerencias(self.mod, marco=ayudante == "_cosco_autocomplete", **k)

    def llamar(self, ayudante, pagina, reg, **k):
        """Corre el ayudante sobre la página falsa (el de COSCO, sobre su marco). Si levanta ObjetivoNoEncontrado (su
        forma de terminar sin sugerencia), lo devuelve."""
        m = self.mod
        llamadas = {
            "_fill_autocomplete": lambda: m._fill_port(pagina, "input[placeholder*='Origin' i]", "PUERTO ALFA, PAIS",
                                                       reg, "Origen", **k),
            "_msc_puerto": lambda: m._msc_puerto(pagina, "POLId_input", "PUERTO ALFA", reg, "Port of Load", **k),
            "_cosco_autocomplete": lambda: m._cosco_autocomplete(pagina.marco, "destinati", "PUERTO ALFA",
                                                                 "PUERTO ALFA", reg, "Destination", **k),
            "_hmm_autocomplete": lambda: m._hmm_autocomplete(pagina, "#schOriginText", "PUERTO ALFA, PAIS", reg,
                                                             "Origen", **k),
            "_mk_ciudad": lambda: m._mk_ciudad(pagina, "PUERTO ALFA, PAIS", reg, "Origen", campo="origin", **k),
            "_cma_puerto": lambda: m._cma_puerto(pagina, "#pol", "PUERTO ALFA, PAIS", reg, "Origen", **k),
            "_cma_entrega": lambda: m._cma_entrega(pagina, "PUERTO ALFA, PAIS", reg, **k),
        }
        try:
            return llamadas[ayudante]()
        except m.ObjetivoNoEncontrado as e:
            return e

    def llamar_con(self, ayudante, pagina, reg, texto, **k):
        """Como llamar, con 'texto' en lugar de la celda de prueba. Devuelve el ObjetivoNoEncontrado si lo levanta."""
        m = self.mod
        llamadas = {
            "_fill_autocomplete": lambda: m._fill_port(pagina, "input[placeholder*='Origin' i]", texto, reg, "Origen",
                                                       **k),
            "_msc_puerto": lambda: m._msc_puerto(pagina, "POLId_input", texto, reg, "Port of Load", **k),
            "_cosco_autocomplete": lambda: m._cosco_autocomplete(pagina.marco, "destinati", texto, texto, reg,
                                                                 "Destination", **k),
            "_hmm_autocomplete": lambda: m._hmm_autocomplete(pagina, "#schOriginText", texto, reg, "Origen", **k),
            "_mk_ciudad": lambda: m._mk_ciudad(pagina, texto, reg, "Origen", campo="origin", **k),
            "_cma_puerto": lambda: m._cma_puerto(pagina, "#pol", texto, reg, "Origen", **k),
            "_cma_entrega": lambda: m._cma_entrega(pagina, texto, reg, **k),
        }
        try:
            return llamadas[ayudante]()
        except m.ObjetivoNoEncontrado as e:
            return e

    def test_con_el_texto_vacio_no_escribe_ni_pulsa(self):
        # Sin una palabra antes de la primera coma (_ciudad_de), ninguno escribe ni pulsa nada, aunque la lista esté a
        # la vista, y corta: el texto vacío calzaba con cualquier sugerencia, y la pulsaba (medido en el encargo 42, en
        # un Chromium local; CICLO-maersk-y-fila-sin-ruta.md), y «-» o «X», con cualquiera que los trajera (revisión de
        # código). El de COSCO corta solo con el vacío: busca el texto entero y sirve también al contrato, que va tal
        # como viene; el origen y el destino se los pasa ya con _ciudad_de quien lo llama (test_clics,
        # TestSinSugerenciaNoSigue.test_sin_una_palabra_corta_el_ayudante).
        naviera = {"_fill_autocomplete": "ONE", "_msc_puerto": "MSC", "_cosco_autocomplete": "COSCO",
                   "_hmm_autocomplete": "HYUNDAI", "_mk_ciudad": "MAERSK", "_cma_puerto": "CMA", "_cma_entrega": "CMA"}
        for ayudante in self.AYUDANTES:
            textos = ("", "  ") + (() if ayudante == "_cosco_autocomplete" else
                                   (", PAIS", " , PAIS", "-", "X", "?, PAIS", " x , PAIS"))
            for texto in textos:
                with self.subTest(ayudante=ayudante, texto=texto):
                    carpeta, reg, _ = self.corrida()
                    pagina = self.pagina(ayudante, aparece=0)
                    e = self.llamar_con(ayudante, pagina, reg, texto, evidencia="xx_f5_origen")
                    self.assertIsInstance(e, self.mod.ObjetivoNoEncontrado)
                    paso = f"{self.ETIQUETA.get(ayudante, 'Origen')} de {naviera[ayudante]}"
                    self.assertEqual((e.paso, e.buscaba), (paso, self.mod._TEXTO_DE_LA_FILA))
                    self.assertEqual((pagina.eventos, pagina.inesperados), ([], []))
                    self.assertEqual(sorted(p.name for p in carpeta.iterdir()), ["log.txt"])
        self.assertEqual(self.mod._TEXTO_DE_LA_FILA,
                         "en la celda de la planilla, antes de su primera coma, el texto para buscar en la lista")

    @staticmethod
    def escribe(ayudante):
        """El clic en el campo (COSCO escribe con JavaScript) y lo que escribe (HYUNDAI, la celda entera; los demás, la
        parte antes de la coma)."""
        escribe = ("escribe", "PUERTO ALFA, PAIS" if ayudante == "_hmm_autocomplete" else "PUERTO ALFA")
        campo = [] if ayudante == "_cosco_autocomplete" else [("campo",)]
        return campo + [escribe]

    @classmethod
    def antes(cls, ayudante):
        """Lo que hace cada ayudante antes de ver la lista: escribir (escribe) y las dos esperas; MAERSK, una más,
        porque decide con dos lecturas iguales de la lista (revisión de código del encargo 43)."""
        return cls.escribe(ayudante) + [("espera",)] * (3 if ayudante == "_mk_ciudad" else 2)

    @staticmethod
    def evidencia(ayudante, nombre):
        """La captura de la ventana con la lista a la vista y el HTML (y el de su marco, en COSCO)."""
        marco = [("html", "marco")] if ayudante == "_cosco_autocomplete" else []
        return [("captura", f"{nombre}.png", False, True), ("html",)] + marco

    def test_deja_la_lista_justo_antes_de_pulsar(self):
        # La captura de la ventana (la de página completa dispara un «resize», que podría cerrar la lista), con la
        # lista a la vista, el HTML y después el clic de siempre: ni un clic, una tecla ni una espera más.
        for ayudante in self.AYUDANTES:
            with self.subTest(ayudante=ayudante):
                carpeta, reg, vistas = self.corrida()
                pagina = self.pagina(ayudante)
                self.llamar(ayudante, pagina, reg, evidencia="xx_f5_origen")
                self.assertEqual(pagina.eventos, self.antes(ayudante) + self.evidencia(ayudante, "xx_f5_origen")
                                 + [("pulsa", SUGERIDA)] + self.DESPUES[ayudante])
                self.assertEqual(pagina.inesperados, [])
                marco = ayudante == "_cosco_autocomplete"
                self.assertEqual(sorted(p.name for p in carpeta.iterdir()),
                                 ["log.txt", "xx_f5_origen.html", "xx_f5_origen.png"]
                                 + (["xx_f5_origen_marco1.html"] if marco else []))
                momento = f"con las sugerencias de {self.ETIQUETA.get(ayudante, 'Origen')}".replace(
                    "de Lugar de entrega", "del lugar de entrega")
                html = "2 de 2 HTML (la página y 1 marco(s)" if marco else "1 de 1 HTML (la página y 0 marco(s)"
                for donde in self.leer(carpeta, vistas):
                    self.assertIn(f"evidencia {momento}: xx_f5_origen.png y {html}; 0 sin raíces shadow)", donde)
                    self.assertNotIn("⚠", donde)
                if ayudante == "_fill_autocomplete":        # ONE anota cuál pulsó
                    self.assertIn(f"Origen ('PUERTO ALFA'): sugerencia seleccionada: LI.opcion#120 «{SUGERIDA}»",
                                  self.leer(carpeta, vistas)[0])

    def test_sin_evidencia_elige_igual_y_no_deja_nada(self):
        # El commodity de ONE y el contrato de COSCO usan los mismos ayudantes, sin 'evidencia'.
        for ayudante in self.AYUDANTES:
            with self.subTest(ayudante=ayudante):
                carpeta, reg, vistas = self.corrida()
                pagina = self.pagina(ayudante)
                self.llamar(ayudante, pagina, reg)
                self.assertEqual(pagina.eventos, self.antes(ayudante) + [("pulsa", SUGERIDA)] + self.DESPUES[ayudante])
                self.assertEqual(sorted(p.name for p in carpeta.iterdir()), ["log.txt"])
                self.assertNotIn("⚠", self.leer(carpeta, vistas)[0])

    # Cuántas veces espera cada ayudante su lista antes de darse por vencido: lo que ya esperaba.
    ESPERAS = {"_fill_autocomplete": 9, "_msc_puerto": 8, "_cosco_autocomplete": 12, "_hmm_autocomplete": 10,
               "_mk_ciudad": 14, "_cma_puerto": 14, "_cma_entrega": 14}

    @staticmethod
    def sin_lista(ayudante, nombre):
        """La evidencia sin la lista a la vista: la captura de la ventana y el HTML (y el de su marco, en COSCO)."""
        marco = [("html", "marco")] if ayudante == "_cosco_autocomplete" else []
        return [("captura", f"{nombre}.png", False, False), ("html",)] + marco

    # Lo que devuelve el ayudante que no eligió ninguna sugerencia, para que corte quien lo llama
    # (TestSinSugerenciaNoSigue, en test_clics); ONE, MSC, el puerto de CMA y, desde el encargo 43, MAERSK cortan
    # ellos mismos, con su paso (hasta ahí, _mk_ciudad devolvía ('', '')).
    NO_ELIGIO = {"_cosco_autocomplete": False, "_hmm_autocomplete": False, "_cma_entrega": ""}
    CORTA = {"_fill_autocomplete": "Origen de ONE", "_msc_puerto": "Port of Load de MSC",
             "_cma_puerto": "Origen de CMA", "_mk_ciudad": "Origen de MAERSK"}

    def no_eligio(self, ayudante, r, esperado=None):
        """Que 'r' diga que el ayudante no eligió: su corte, o lo que devuelve ('esperado', o el de NO_ELIGIO)."""
        if esperado is None and ayudante in self.CORTA:
            self.assertIsInstance(r, self.mod.ObjetivoNoEncontrado)
            self.assertEqual(r.paso, self.CORTA[ayudante])
            return
        esperado = self.NO_ELIGIO[ayudante] if esperado is None else esperado
        self.assertEqual((type(r), r), (type(esperado), esperado))

    def test_sin_sugerencias_deja_la_evidencia_igual(self):
        # Sin una sugerencia que elegir, la evidencia queda igual, con el mismo nombre, al terminar la espera que el
        # ayudante ya tenía y sin un clic (decisión de Marcelo, encargo 42, CICLO-maersk-y-fila-sin-ruta.md; hasta ahí
        # no quedaba nada). MAERSK y COSCO vuelven a escribir la ciudad y dejan también la de esa segunda espera,
        # «_reintento». El puerto de CMA la deja antes del Tab con que lee lo que quedó. Después, cada uno dice que no
        # eligió, o corta (revisión de código del encargo 42: nada lo miraba).
        for ayudante in self.AYUDANTES:
            with self.subTest(ayudante=ayudante):
                carpeta, reg, vistas = self.corrida()
                pagina = self.pagina(ayudante, aparece=10 ** 6)
                self.no_eligio(ayudante, self.llamar(ayudante, pagina, reg, evidencia="xx_f5_origen"))
                esperas = [("espera",)] * self.ESPERAS[ayudante]
                primera = self.escribe(ayudante) + esperas + self.sin_lista(ayudante, "xx_f5_origen")
                reintento = self.sin_lista(ayudante, "xx_f5_origen_reintento")
                esperado = {"_mk_ciudad": primera + [("campo",), ("espera",), ("escribe", "PUERTO ALFA")] + esperas
                            + reintento,
                            "_cosco_autocomplete": primera + [("escribe", "PUERTO ALFA")] + esperas + reintento,
                            "_cma_puerto": primera + [("tecla", "Tab"), ("espera",)]}.get(ayudante, primera)
                self.assertEqual(pagina.eventos, esperado)
                self.assertEqual(pagina.inesperados, [])
                nombres = [e[1][:-4] for e in esperado if e[0] == "captura"]
                marco = ["_marco1.html"] if ayudante == "_cosco_autocomplete" else []
                self.assertEqual(sorted(p.name for p in carpeta.iterdir()),
                                 sorted(["log.txt"] + [n + x for n in nombres for x in [".html", ".png"] + marco]))
                momento = ("sin una sugerencia que elegir en el lugar de entrega" if ayudante == "_cma_entrega"
                           else f"sin una sugerencia que elegir en {self.ETIQUETA.get(ayudante, 'Origen')}")
                for donde in self.leer(carpeta, vistas):
                    for n in nombres:
                        self.assertIn(f"evidencia {momento}: {n}.png y ", donde)

    def test_si_el_campo_falla_no_elige(self):
        # Si el campo no responde, ninguno pulsa, escribe ni deja evidencia, y cada uno dice que no eligió: quien lo
        # llama corta (revisión de código del encargo 42: nada lo miraba). El puerto de CMA corta él mismo, porque el
        # campo no queda con el código del puerto, y desde el encargo 43 MAERSK también. COSCO, también si su
        # JavaScript falla; y el lugar de entrega de CMA, también si no puede abrir el campo.
        falla = {"_fill_autocomplete": False, "_msc_puerto": False, "_cosco_autocomplete": False,
                 "_hmm_autocomplete": False, "_mk_ciudad": None, "_cma_puerto": None, "_cma_entrega": ""}
        casos = [(a, {}) for a in self.AYUDANTES] + [("_cosco_autocomplete", {"campo_falla": "lanza"}),
                                                    ("_cma_entrega", {"campo_oculto": True})]
        for ayudante, k in casos:
            with self.subTest(ayudante=ayudante, **k):
                carpeta, reg, _ = self.corrida()
                pagina = self.pagina(ayudante, **dict({"campo_falla": True}, **k))
                self.no_eligio(ayudante, self.llamar(ayudante, pagina, reg, evidencia="xx_f5_origen"), falla[ayudante])
                self.assertEqual([e for e in pagina.eventos if e[0] in ("pulsa", "escribe", "captura", "html")], [])
                self.assertEqual(pagina.inesperados, [])
                self.assertEqual(sorted(p.name for p in carpeta.iterdir()), ["log.txt"])

    def test_una_sola_vez_aunque_el_primer_clic_falle(self):
        # El clic que falla se reintenta en la vuelta siguiente, como antes, sin volver a dejar la lista.
        for ayudante in self.AYUDANTES:
            with self.subTest(ayudante=ayudante):
                _, reg, _ = self.corrida()
                pagina = self.pagina(ayudante, fallos=1)
                self.llamar(ayudante, pagina, reg, evidencia="xx_f5_origen")
                self.assertEqual(pagina.eventos, self.antes(ayudante) + self.evidencia(ayudante, "xx_f5_origen")
                                 + [("espera",), ("pulsa", SUGERIDA)] + self.DESPUES[ayudante])

    def test_si_no_puede_leer_la_lista_elige_igual_y_lo_avisa(self):
        # Si el JavaScript que solo lee falla, no deja la evidencia y elige como siempre (la evidencia nunca corta), y
        # lo avisa: pulsó sin dejar la lista.
        for ayudante in self.CON_JAVASCRIPT:
            with self.subTest(ayudante=ayudante):
                carpeta, reg, vistas = self.corrida()
                pagina = self.pagina(ayudante, lectura_falla=True)
                self.llamar(ayudante, pagina, reg, evidencia="xx_f5_origen")
                self.assertEqual(pagina.eventos, self.antes(ayudante) + [("pulsa", SUGERIDA)] + self.DESPUES[ayudante])
                self.assertEqual(sorted(p.name for p in carpeta.iterdir()), ["log.txt"])
                for donde in self.leer(carpeta, vistas):
                    self.assertIn(f"· ⚠ {self.ETIQUETA.get(ayudante, 'Origen')}: pulsé una sugerencia sin dejar la "
                                  "evidencia de la lista (xx_f5_origen): al leerla, justo antes, no la vi", donde)

    def test_si_la_lista_aparece_al_pulsar_lo_avisa(self):
        # Revisión del encargo 41: la lista puede aparecer entre la lectura y el clic. El clic sale igual, sin la
        # evidencia, y lo avisa.
        for ayudante in self.CON_JAVASCRIPT:
            with self.subTest(ayudante=ayudante):
                carpeta, reg, vistas = self.corrida()
                pagina = self.pagina(ayudante, aparece=10 ** 6, al_pulsar=True)
                self.llamar(ayudante, pagina, reg, evidencia="xx_f5_origen")
                self.assertEqual(pagina.eventos, self.antes(ayudante)[:-1] + [("pulsa", SUGERIDA)]
                                 + self.DESPUES[ayudante])
                for donde in self.leer(carpeta, vistas):
                    self.assertIn(f"· ⚠ {self.ETIQUETA.get(ayudante, 'Origen')}: pulsé una sugerencia sin dejar la "
                                  "evidencia de la lista (xx_f5_origen)", donde)

    def test_si_la_lista_cambia_mientras_la_guarda_lo_avisa(self):
        # Revisión del encargo 41: mientras se guarda la evidencia la lista puede cambiar, y el clic de después elige de
        # la nueva. La regla no cambia; el aviso dice que la evidencia no es la lista de la que eligió, con el texto de
        # cada una (en ONE, sin su etiqueta, su clase ni su posición, desde la revisión del informe).
        for ayudante in self.AYUDANTES:
            with self.subTest(ayudante=ayudante):
                carpeta, reg, vistas = self.corrida()
                pagina = self.pagina(ayudante, cambia=True)
                self.llamar(ayudante, pagina, reg, evidencia="xx_f5_origen")
                self.assertEqual(pagina.eventos, self.antes(ayudante) + self.evidencia(ayudante, "xx_f5_origen")
                                 + [("pulsa", OTRA)] + self.DESPUES[ayudante])
                for donde in self.leer(carpeta, vistas):
                    self.assertIn(f"· ⚠ {self.ETIQUETA.get(ayudante, 'Origen')}: la lista cambió mientras guardaba su "
                                  f"evidencia (xx_f5_origen): ahí habría pulsado «{SUGERIDA}», y pulsé «{OTRA}»", donde)

    def test_one_compara_solo_el_texto_de_la_sugerencia(self):
        # Revisión del informe del encargo 41: ONE describe la sugerencia con su etiqueta, su clase, su posición y su
        # texto, y la clase la lee después del clic. Si solo cambian la clase o la posición, es la misma sugerencia: no
        # avisa, y anota la que pulsó como la describe el JavaScript.
        carpeta, reg, vistas = self.corrida()
        pagina = self.pagina("_fill_autocomplete", se_mueve=True)
        self.llamar("_fill_autocomplete", pagina, reg, evidencia="xx_f5_origen")
        self.assertEqual(pagina.eventos, self.antes("_fill_autocomplete")
                         + self.evidencia("_fill_autocomplete", "xx_f5_origen") + [("pulsa", SUGERIDA)]
                         + self.DESPUES["_fill_autocomplete"])
        self.assertIn(f"Origen ('PUERTO ALFA'): sugerencia seleccionada: LI.opcion activa#118 «{SUGERIDA}»",
                      self.leer(carpeta, vistas)[0])
        for donde in self.leer(carpeta, vistas):
            self.assertNotIn("⚠", donde)
        self.assertEqual(pagina.inesperados, [])

    def test_maersk_si_vuelve_a_escribir_deja_la_del_reintento(self):
        # Si la sugerencia no queda en el campo (aquí el clic lo borra), _mk_ciudad vuelve a escribir la ciudad y elige
        # otra vez: esa otra lista queda con «_reintento».
        _, reg, _ = self.corrida()
        pagina = self.pagina("_mk_ciudad", borra=1)
        self.llamar("_mk_ciudad", pagina, reg, evidencia="mk_f5_origen")
        self.assertEqual(pagina.eventos, self.antes("_mk_ciudad") + self.evidencia("_mk_ciudad", "mk_f5_origen")
                         + [("pulsa", SUGERIDA)] + [("espera",)] * self.mod.MK_LECTURAS_CAMPO
                         + [("campo",), ("espera",), ("escribe", "PUERTO ALFA"), ("espera",), ("espera",)]
                         + self.evidencia("_mk_ciudad", "mk_f5_origen_reintento")
                         + [("pulsa", SUGERIDA), ("espera",), ("espera",)])

    def test_cosco_si_vuelve_a_escribir_deja_la_del_reintento(self):
        # Revisión del encargo 41: si la primera vez no apareció ninguna, COSCO vuelve a escribir, y la lista de esa
        # segunda vez queda con «_reintento» (hasta aquí, la de la segunda vez no quedaba si la primera ya había dejado
        # una). Desde el encargo 42 queda también la de la primera, sin la lista, al terminar su espera.
        _, reg, _ = self.corrida()
        pagina = self.pagina("_cosco_autocomplete", escritos=2)
        self.llamar("_cosco_autocomplete", pagina, reg, evidencia="cosco_f5_destino")
        self.assertEqual(pagina.eventos, [("escribe", "PUERTO ALFA")] + [("espera",)] * 12
                         + self.sin_lista("_cosco_autocomplete", "cosco_f5_destino")
                         + [("escribe", "PUERTO ALFA"), ("espera",)]
                         + self.evidencia("_cosco_autocomplete", "cosco_f5_destino_reintento") + [("pulsa", SUGERIDA)])

    def test_maersk_devuelve_la_sugerencia_y_lo_que_quedo_en_el_campo(self):
        # Para el motivo de SIN-CUPO (_mk_ruta_buscada, CICLO-origen-y-destino.md): la sugerencia que pulsó y lo que
        # quedó en el campo, cada una entera y en una línea. Desde el encargo 43, el campo tiene que quedar con el texto
        # entero de la sugerencia: si el clic no la toma (el campo sigue con lo escrito, que también trae sus primeros
        # caracteres: hasta ahí, eso pasaba) o lo borra, vuelve a escribir, y si tampoco, corta con lo que quedó; sin
        # lista, corta con lo que buscaba. El log.txt la anota con sus primeros 45 caracteres, en una línea.
        carpeta, reg, _ = self.corrida()
        f = lambda **k: self.llamar("_mk_ciudad", PaginaSugerencias(self.mod, **k), reg)     # noqa: E731
        self.assertEqual(f(), (SUGERIDA, SUGERIDA))
        self.assertEqual(f(no_la_toma=1), (SUGERIDA, SUGERIDA))
        self.assertIn("Origen: la sugerencia no quedó en el campo ('PUERTO ALFA')",
                      (carpeta / "log.txt").read_text(encoding="utf-8"))
        cortes = [(f(no_la_toma=2), f"la sugerencia «{SUGERIDA}» en el campo, que quedó con «PUERTO ALFA»"),
                  (f(borra=2), f"la sugerencia «{SUGERIDA}» en el campo, que quedó vacío"),
                  (f(aparece=10 ** 6), "una sugerencia para «PUERTO ALFA»"),
                  (f(campo_falla=True), "el campo donde escribir «PUERTO ALFA»")]
        for e, buscaba in cortes:
            with self.subTest(buscaba=buscaba):
                self.assertIsInstance(e, self.mod.ObjetivoNoEncontrado)
                self.assertEqual((e.paso, e.buscaba), ("Origen de MAERSK", buscaba))
        larga = PaginaSugerencias(self.mod)
        larga.opcion = "PUERTO ALFA\n      (UNA REGION DE PRUEBA BASTANTE LARGA),  PAIS DE PRUEBA"
        entera = "PUERTO ALFA (UNA REGION DE PRUEBA BASTANTE LARGA), PAIS DE PRUEBA"
        self.assertEqual(self.llamar("_mk_ciudad", larga, reg), (entera, entera))
        self.assertIn(f"Origen 'PUERTO ALFA': {entera[:45]}\n", (carpeta / "log.txt").read_text(encoding="utf-8"))

    def test_maersk_elige_la_unica_container_yard_que_dice_lo_escrito(self):
        # La regla de Marcelo (encargo 43): entre las sugerencias Container Yard (su tipo de lugar va en la raíz
        # shadow: lo ve el filtro de Playwright, no text_content), la única cuya parte antes de la primera coma, sin lo
        # que va entre paréntesis, es lo escrito, sin distinguir mayúsculas ni tildes. En las 4 listas del 30-09, cada
        # Container Yard venía repetida, con el mismo texto, como Store Door, y a las 15:21 la Container Yard «ciudad +
        # 1 palabra, país» iba antes que «ciudad, país», y se pulsó (CICLO-maersk-y-fila-sin-ruta.md). Si no hay una
        # sola, no pulsa nada, vuelve a escribir y, si tampoco, corta con cuántas había. Hasta el encargo 43 pulsaba la
        # primera Container Yard o, si no había, la primera.
        CY, SD = "Container Yard", "Store Door"
        elige = [("PUERTO ALFA NORTE, PAIS", [("PUERTO ALFA, PAIS", SD), ("PUERTO ALFA, PAIS", CY)],
                  "PUERTO ALFA, PAIS", "PUERTO ALFA, PAIS"),
                 ("Puerto Alfa (Region Uno), Pais", [], "PUERTO ALFA", "Puerto Alfa (Region Uno), Pais"),
                 ("Puerto Alfa, País", [], "PUERTO ÁLFA, PAIS", "Puerto Alfa, País")]
        for opcion, extra, celda, pulsa in elige:
            with self.subTest(opcion=opcion, celda=celda):
                carpeta, reg, _ = self.corrida()
                pagina = PaginaSugerencias(self.mod, extra=extra)
                pagina.opcion = opcion
                self.assertEqual(self.llamar_con("_mk_ciudad", pagina, reg, celda, evidencia="mk_f5_origen"),
                                 (pulsa, pulsa))
                escrita = celda.split(",")[0].upper()
                self.assertEqual(pagina.eventos, [("campo",), ("escribe", escrita)] + [("espera",)] * 3
                                 + self.evidencia("_mk_ciudad", "mk_f5_origen") + [("pulsa", pulsa)]
                                 + self.DESPUES["_mk_ciudad"])
                self.assertEqual(pagina.tipo_pulsado, CY)
        no_elige = [("PUERTO ALFA, PAIS", CY, [("PUERTO ALFA, OTRO PAIS", CY)], 2),
                    ("PUERTO ALFA, PAIS", SD, [], 0),
                    ("PUERTO ALFA NORTE, PAIS", CY, [("PUERTO ALFA, PAIS", SD)], 0)]
        for opcion, tipo, extra, n in no_elige:
            with self.subTest(opcion=opcion, tipo=tipo, extra=extra):
                carpeta, reg, _ = self.corrida()
                pagina = PaginaSugerencias(self.mod, tipo=tipo, extra=extra)
                pagina.opcion = opcion
                e = self.llamar("_mk_ciudad", pagina, reg, evidencia="mk_f5_origen")
                self.assertIsInstance(e, self.mod.ObjetivoNoEncontrado)
                buscaba = self.mod._mk_sin_una_exacta("PUERTO ALFA", n)
                self.assertEqual((e.paso, e.buscaba), ("Origen de MAERSK", buscaba))
                self.assertEqual(pagina.eventos, self.antes("_mk_ciudad") + self.evidencia("_mk_ciudad", "mk_f5_origen")
                                 + [("campo",), ("espera",), ("escribe", "PUERTO ALFA"), ("espera",), ("espera",)]
                                 + self.evidencia("_mk_ciudad", "mk_f5_origen_reintento"))
                cy = sum(t == CY for t in [tipo] + [x for _, x in extra])
                log = (carpeta / "log.txt").read_text(encoding="utf-8")
                self.assertEqual(log.count(f"Origen: {n} de las {cy} sugerencias Container Yard dicen «PUERTO ALFA» "
                                           "antes de su primera coma"), 2)
        # Elige de la lista que dejó: si al dejarla no había una sola, no pulsa en esa vuelta, aunque mientras la
        # guardaba apareciera; vuelve a escribir y elige de la segunda, que deja con «_reintento».
        carpeta, reg, vistas = self.corrida()
        pagina = PaginaSugerencias(self.mod, cambia=True)
        pagina.opcion = "PUERTO ALFA NORTE, PAIS"
        self.assertEqual(self.llamar("_mk_ciudad", pagina, reg, evidencia="mk_f5_origen"), (OTRA, OTRA))
        self.assertEqual(pagina.eventos, self.antes("_mk_ciudad") + self.evidencia("_mk_ciudad", "mk_f5_origen")
                         + [("campo",), ("espera",), ("escribe", "PUERTO ALFA"), ("espera",), ("espera",)]
                         + self.evidencia("_mk_ciudad", "mk_f5_origen_reintento") + [("pulsa", OTRA)]
                         + self.DESPUES["_mk_ciudad"])
        for donde in self.leer(carpeta, vistas):
            self.assertNotIn("⚠", donde)
        self.assertEqual(self.mod._mk_sin_una_exacta("PUERTO ALFA", 2),
                         "una sola sugerencia Container Yard que diga «PUERTO ALFA» antes de su primera coma (sin lo "
                         "que va entre paréntesis): hay 2")
        self.assertEqual(self.mod._mk_sin_una_exacta("PUERTO ALFA", 0),
                         "una sola sugerencia Container Yard que diga «PUERTO ALFA» antes de su primera coma (sin lo "
                         "que va entre paréntesis): no hay ninguna")

    def test_maersk_decide_con_la_lista_quieta(self):
        # Revisión de código del encargo 43: la lista puede llegar de a poco. _mk_ciudad decide con dos lecturas iguales
        # seguidas de sus Container Yard: si una segunda exacta llega después de la primera lectura, no pulsa la
        # primera, vuelve a escribir y, si sigue habiendo dos, corta. Hasta ahí decidía con la primera lectura.
        _, reg, _ = self.corrida()
        pagina = PaginaSugerencias(self.mod, tarde=(3, [("PUERTO ALFA, OTRO PAIS", "Container Yard")]))
        e = self.llamar("_mk_ciudad", pagina, reg, evidencia="mk_f5_origen")
        self.assertIsInstance(e, self.mod.ObjetivoNoEncontrado)
        self.assertEqual(e.buscaba, self.mod._mk_sin_una_exacta("PUERTO ALFA", 2))
        self.assertNotIn("pulsa", [x[0] for x in pagina.eventos])
        # Con la lista quieta desde que aparece, la segunda lectura la confirma y pulsa.
        pagina = PaginaSugerencias(self.mod)
        self.assertEqual(self.llamar("_mk_ciudad", pagina, reg, evidencia="mk_f5_origen"), (SUGERIDA, SUGERIDA))
        self.assertEqual(pagina.eventos[:5], [("campo",), ("escribe", "PUERTO ALFA")] + [("espera",)] * 3)

    def test_maersk_lee_el_campo_como_la_regla(self):
        # Revisión de código del encargo 43: el campo se compara como la regla (_mk_plano: sin mayúsculas, tildes ni
        # espacios de más) y se lee hasta MK_LECTURAS_CAMPO veces, cada 0,4 s, por si se asienta tarde. Lo tecleado
        # sigue sin bastar (test_maersk_devuelve_la_sugerencia_y_lo_que_quedo_en_el_campo).
        _, reg, _ = self.corrida()
        pagina = PaginaSugerencias(self.mod, campo_como=str.lower)
        self.assertEqual(self.llamar("_mk_ciudad", pagina, reg), (SUGERIDA, SUGERIDA.lower()))
        pagina = PaginaSugerencias(self.mod, tarda=2)
        self.assertEqual(self.llamar("_mk_ciudad", pagina, reg), (SUGERIDA, SUGERIDA))
        # Tres lecturas (la de siempre, a los 0,4 s, y dos más) y la espera de 0,8 s del final.
        despues = pagina.eventos[pagina.eventos.index(("pulsa", SUGERIDA)):]
        self.assertEqual(despues, [("pulsa", SUGERIDA)] + [("espera",)] * 4)
        self.assertEqual(self.mod.MK_LECTURAS_CAMPO, 5)

    def test_maersk_reconoce_la_lista_con_una_tilde_en_las_primeras_letras(self):
        # Decisión de Marcelo (encargo 46, pendiente del 43): el prefijo con que _mk_ciudad espera su lista toma la
        # letra con tilde como la letra sin ella, y la ñ como n (_mk_plano). Hasta ahí se caían: «PEÑA ALFA» esperaba
        # «PEA A» y «PUÉRTO ALFA», «PURTO», que ninguna sugerencia trae, y la fila quedaba NO ENVIADA en ese campo. Con
        # la letra con tilde en la primera, la lista se reconocía igual (revisión del encargo 43). «Igual a lo escrito»
        # sigue sin distinguir tildes, y lo escrito en el campo, con ellas.
        for celda, opcion in (("PEÑA ALFA, PAIS", "Pena Alfa, Pais"), ("PUÉRTO ALFA", "Puerto Alfa, Pais"),
                              ("ÁLFA SUR, PAIS", "Alfa Sur, Pais")):
            with self.subTest(celda=celda):
                _, reg, _ = self.corrida()
                pagina = PaginaSugerencias(self.mod)
                pagina.opcion = opcion
                self.assertEqual(self.llamar_con("_mk_ciudad", pagina, reg, celda, evidencia="mk_f5_origen"),
                                 (opcion, opcion))
                self.assertEqual(pagina.eventos, [("campo",), ("escribe", celda.split(",")[0].upper())]
                                 + [("espera",)] * 3 + self.evidencia("_mk_ciudad", "mk_f5_origen")
                                 + [("pulsa", opcion)] + self.DESPUES["_mk_ciudad"])

    def test_cma_reconoce_la_lista_con_una_tilde_en_las_primeras_letras(self):
        # Decisión de Marcelo (encargo 48): CMA arma el prefijo con que reconoce su lista como MAERSK desde el encargo
        # 46 (_prefijo_de_la_lista): la letra con tilde como la letra sin ella, y la ñ como n. Hasta ahí se caían:
        # «PEÑA ALFA» esperaba «PEA A» y «PUÉRTO ALFA», «PURTO», que ninguna sugerencia trae, y la fila quedaba NO
        # ENVIADA en ese campo. Lo escrito en el campo sigue con sus tildes.
        for ayudante in ("_cma_puerto", "_cma_entrega"):
            for celda, opcion in (("PEÑA ALFA, PAIS", "PENA ALFA, PAIS ; XX ; XXPNA"),
                                  ("PUÉRTO ALFA", "PUERTO ALFA, PAIS ; XX ; XXPAL")):
                with self.subTest(ayudante=ayudante, celda=celda):
                    _, reg, _ = self.corrida()
                    pagina = PaginaSugerencias(self.mod)
                    pagina.opcion = opcion
                    r = self.llamar_con(ayudante, pagina, reg, celda, evidencia="cma_f7_origen_puerto")
                    self.assertEqual(r, True if ayudante == "_cma_puerto" else opcion)
                    self.assertEqual(pagina.eventos, [("campo",), ("escribe", celda.split(",")[0].upper())]
                                     + [("espera",)] * 2 + self.evidencia(ayudante, "cma_f7_origen_puerto")
                                     + [("pulsa", opcion)] + self.DESPUES[ayudante])

    def test_maersk_escribe_y_compara_con_los_espacios_de_a_uno(self):
        # Revisión de código del encargo 43: el prefijo con que espera la lista se toma con los espacios de a uno, como
        # compara la regla («SAN  ALFA» escrito encuentra «San Alfa, …»; hasta ahí, su prefijo «SAN  » no estaba en
        # ninguna sugerencia). Lo que va entre paréntesis se quita solo de la sugerencia: lo escrito con paréntesis no
        # calza con ninguna, como dice la regla.
        _, reg, _ = self.corrida()
        pagina = PaginaSugerencias(self.mod)
        pagina.opcion = "San Alfa, Pais"
        self.assertEqual(self.llamar_con("_mk_ciudad", pagina, reg, "SAN  ALFA, PAIS"),
                         ("San Alfa, Pais", "San Alfa, Pais"))
        pagina = PaginaSugerencias(self.mod)
        pagina.opcion = "PUERTO ALFA (NORTE), PAIS"
        e = self.llamar_con("_mk_ciudad", pagina, reg, "PUERTO ALFA (NORTE), PAIS")
        self.assertIsInstance(e, self.mod.ObjetivoNoEncontrado)
        self.assertEqual(e.buscaba, self.mod._mk_sin_una_exacta("PUERTO ALFA (NORTE)", 0))

    def test_cada_reservador_la_pide_para_su_origen_y_su_destino(self):
        # Solo el origen y el destino: ni el commodity de ONE ni el contrato de COSCO, que usan los mismos ayudantes.
        # CMA, con su modo, porque vuelve a elegir en cada intento (ramp_separado, puerto o ramp). Con el último
        # argumento de cada llamada (su etiqueta), para que un nombre no pueda ir con el otro campo.
        ayudantes = {"_fill_port", "_fill_autocomplete", "_msc_puerto", "_cosco_autocomplete", "_hmm_autocomplete",
                     "_mk_ciudad", "_cma_puerto", "_cma_entrega"}
        llamadas = sorted((nombre, c.func.id, ast.unparse(c.args[-1]),
                           next((ast.unparse(k.value) for k in c.keywords if k.arg == "evidencia"), "-"))
                          for nombre, f in funciones(self.mod).items() for c in ast.walk(f)
                          if isinstance(c, ast.Call) and getattr(c.func, "id", "") in ayudantes)
        self.assertEqual(llamadas, sorted([
            ("_cosco_puerto_de_carga", "_cosco_autocomplete", "'Origin City'",
             "f\"cosco_f{reserva.get('fila')}_origen\""),
            ("_fill_port", "_fill_autocomplete", "etiqueta", "evidencia"),
            ("reservar_cma", "_cma_entrega", "reg", "f'cma_f{f}_entrega_{modo}'"),
            ("reservar_cma", "_cma_entrega", "reg", "f'cma_f{f}_entrega_{modo}'"),
            ("reservar_cma", "_cma_puerto", "'POD'", "f'cma_f{f}_destino_{modo}'"),
            ("reservar_cma", "_cma_puerto", "'POD'", "f'cma_f{f}_destino_{modo}'"),
            ("reservar_cma", "_cma_puerto", "'POD'", "f'cma_f{f}_destino_{modo}'"),
            ("reservar_cma", "_cma_puerto", "'Origen'", "f'cma_f{f}_origen_{modo}'"),
            ("reservar_cosco", "_cosco_autocomplete", "'Contract Number'", "-"),
            ("reservar_cosco", "_cosco_autocomplete", "'Destination'", "f'cosco_f{f}_destino'"),
            ("reservar_hyundai", "_hmm_autocomplete", "'Destino'", "f'hmm_f{f}_destino'"),
            ("reservar_hyundai", "_hmm_autocomplete", "'Origen'", "f'hmm_f{f}_origen'"),
            ("reservar_maersk", "_mk_ciudad", "'Destino'", "f'mk_f{f}_destino'"),
            ("reservar_maersk", "_mk_ciudad", "'Origen'", "f'mk_f{f}_origen'"),
            ("reservar_msc", "_msc_puerto", "'Port of Discharge'", "f'msc_f{f}_destino'"),
            ("reservar_msc", "_msc_puerto", "'Port of Load'", "f'msc_f{f}_origen'"),
            ("reservar_one", "_fill_autocomplete", "'Commodity'", "-"),
            ("reservar_one", "_fill_port", "'Destino'", "f'one_f{f}_destino'"),
            ("reservar_one", "_fill_port", "'Origen'", "f'one_f{f}_origen'"),
        ]))

    def js_local(self, funcion):
        """El JavaScript que 'funcion' guarda en su variable js (MSC y HYUNDAI lo llevan adentro)."""
        [js] = [n.value.value for n in ast.walk(funciones(self.mod)[funcion])
                if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == "js"]
        return js

    def test_js_pulsa_solo_con_la_marca_true(self):
        # Con la marca false, el mismo JavaScript devuelve la que pulsaría ('' si ninguna) y no pulsa nada; con true,
        # pulsa esa misma; sin la marca, tampoco pulsa (revisión del encargo 41: así, una lectura que la olvide no
        # pulsa). ONE y COSCO aceptan todavía el texto solo, y pulsan, como antes. ONE describe la elegida con su
        # etiqueta, su clase, su posición y su texto.
        guion = (
            "const el = (t, i) => ({tagName: 'LI', className: 'opcion', textContent: t, offsetParent: {}, clics: 0,\n"
            "  children: {length: 0}, getBoundingClientRect: () => ({top: 300 - 100 * i, height: 20}),\n"
            "  closest: () => null, click() { this.clics++; }});\n"
            "const correr = (f, textos, arg) => {\n"
            "  const els = textos.map(el);\n"
            "  global.document = {querySelectorAll: () => els};\n"
            "  return [f(arg), els.map(e => e.clics)];\n"
            "};\n"
            f"const one = {self.mod._JS_PICK_SUGGESTION};\n"
            f"const msc = {self.js_local('_msc_puerto')};\n"
            f"const hmm = {self.js_local('_hmm_autocomplete')};\n"
            f"const cosco = {self.mod._JS_COSCO_AUTO_PICK};\n"
            "const dos = ['PUERTO ALFA, PAIS', 'PUERTO ALFA'], otra = ['OTRA'];\n"
            "const chile = ['PUERTO ALFA, PARAGUAY', 'PUERTO ALFA, CHILE'];\n"
            "const exacta = ['PUERTO ALFA NORTE', 'PUERTO ALFA, PAIS'];\n"
            "const sin = ['PUERTO ALFA NORTE', 'PUERTO ALFA SUR'];\n"
            "const lee = ['PUERTO ALFA', false], pulsa = ['PUERTO ALFA', true], sola = ['PUERTO ALFA'];\n"
            "const leeC = (c) => ['PUERTO ALFA', c, false], pulsaC = (c) => ['PUERTO ALFA', c, true];\n"
            "console.log(JSON.stringify({\n"
            "  one: [correr(one, dos, lee), correr(one, dos, pulsa), correr(one, dos, 'PUERTO ALFA'),\n"
            "        correr(one, otra, lee), correr(one, dos, sola)],\n"
            "  msc: [correr(msc, dos, lee), correr(msc, dos, pulsa), correr(msc, otra, lee), correr(msc, dos, sola)],\n"
            "  hmm: [correr(hmm, dos, lee), correr(hmm, dos, pulsa), correr(hmm, otra, lee), correr(hmm, dos, sola)],\n"
            "  cosco: [correr(cosco, chile, leeC(true)), correr(cosco, chile, pulsaC(true)),\n"
            "          correr(cosco, exacta, leeC(false)), correr(cosco, exacta, pulsaC(false)),\n"
            "          correr(cosco, exacta, 'PUERTO ALFA'), correr(cosco, sin, leeC(false)),\n"
            "          correr(cosco, sin, pulsaC(false)), correr(cosco, otra, leeC(false)),\n"
            "          correr(cosco, sin, ['PUERTO ALFA', false])],\n"
            "}));\n")
        r = correr_node(self, guion)
        elegida = "LI.opcion#200 «PUERTO ALFA»"
        pulsada = f"CLICK[{elegida}] CANDS[LI.opcion#300  LI.opcion#200]"
        self.assertEqual(r["one"], [[elegida, [0, 0]], [pulsada, [0, 1]], [pulsada, [0, 1]], ["", [0]],
                                    [elegida, [0, 0]]])
        self.assertEqual(r["msc"], [["PUERTO ALFA", [0, 0]], ["PUERTO ALFA", [0, 1]], ["", [0]],
                                    ["PUERTO ALFA", [0, 0]]])
        self.assertEqual(r["hmm"], [["PUERTO ALFA, PAIS", [0, 0]], ["PUERTO ALFA, PAIS", [1, 0]], ["", [0]],
                                    ["PUERTO ALFA, PAIS", [0, 0]]])
        self.assertEqual(r["cosco"], [["PUERTO ALFA, CHILE", [0, 0]], ["PUERTO ALFA, CHILE", [0, 1]],
                                      ["PUERTO ALFA, PAIS", [0, 0]], ["PUERTO ALFA, PAIS", [0, 1]],
                                      ["PUERTO ALFA, PAIS", [0, 1]], ["PUERTO ALFA NORTE", [0, 0]],
                                      ["PUERTO ALFA NORTE", [1, 0]], ["", [0]], ["PUERTO ALFA NORTE", [0, 0]]])
