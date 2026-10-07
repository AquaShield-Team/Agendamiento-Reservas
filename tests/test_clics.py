# -*- coding: utf-8 -*-
"""Clics a ciegas antes de la guarda del candado (CICLO-clics-a-ciegas.md).

- Un paso que no encuentra su objetivo por su identificación propia (su texto, su etiqueta o un selector
  propio) no pulsa nada: la reserva queda NO ENVIADA, con el paso y lo que buscaba en pantalla, en log.txt y
  en una captura (ObjetivoNoEncontrado y el decorador _sin_clic_a_ciegas).
- Ninguna forma de clic genérico («el primero» o «el último» visible, sin nada propio que lo nombre)
  reaparece antes de la guarda: el detector recorre lo que corre antes de la guarda de cada reservador,
  incluido el JavaScript inyectado, y compara con la foto de lo permitido.

Páginas y documentos falsos; el JavaScript se corre en Node. Ningún portal ni dato real.
"""
import ast
import datetime
import hashlib
import json
import os
import re
import types
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock
from urllib.parse import quote

import soporte
from test_envio import correr_node

RESERVADORES = {"reservar_one": "one", "reservar_msc": "msc", "reservar_cma": "cma", "reservar_cosco": "cosco",
                "reservar_hyundai": "hmm", "reservar_maersk": "mk"}

# Formas de clic genérico: eligen por posición entre candidatos que no se filtraron por nada propio del objetivo.
GENERICOS = {
    "casilla-por-tipo": r"input\[type=['\"]?checkbox",
    "rol-sin-nombre": r"get_by_role\(\s*['\"]checkbox['\"]\s*\)",
    # «.last» también sin paréntesis delante («loc.last»): hasta el encargo 37 la foto veía solo «).last», y así no
    # veía el Shipper de MAERSK, «loc_aqua.last» (decisión de Marcelo, CICLO-maersk-ultimos-puntos.md). También
    # «.nth(-1)» (revisión del encargo 37).
    "ultimo-por-posicion": r"\.last\b|\[\s*\w+\.length\s*-\s*1\s*\]|\.nth\(\s*-\s*1\s*\)",
    "ancestro-con-texto": r"div:has-text\([^)]*\)\s*(?:>>\s*)?(?:button|svg|input)\b",
    "clase-de-componente": r"\.el-select input|\.el-drawer input|\.el-button--primary|mc-textarea textarea|"
                           r"input\.mag-input__input",
    "primero-sin-filtro": r"\|\|\s*\w+\[0\]|\b\w+\[0\]\.(?:click|focus)\(\)",
    "primer-control-del-bloque": r"querySelector\(\s*['\"]button\s*,|querySelectorAll\(\s*['\"]button\s*,\s*\[aria",
    "textarea-cualquiera": r"locator\(\s*\"(?:[^\"]*,\s*)?textarea\s*\"|locator\(\s*'(?:[^']*,\s*)?textarea\s*'",
    # Las formas de teclado y de textarea de CICLO-cola-nueve-items.md: la flecha abajo elige la opción que quede
    # primera; un textarea buscado solo por su etiqueta HTML, o el primer control de un bloque, es el que haya.
    "teclado-flecha": r"press\(\s*['\"]ArrowDown",
    "textarea-en-js": r"querySelectorAll\(\s*['\"]textarea['\"]\s*\)",
    "textarea-o-control": r"querySelector\(\s*['\"]textarea\s*,",
    # El primer elemento cuyo textContent calza, elegido con .find (revisión del encargo 38): así era el respaldo de
    # «Review booking» que pulsaba <html>, y la foto no lo veía.
    "primero-por-textContent": r"\.find\(\s*\w+\s*=>\s*\{\s*const\s+\w+\s*=\s*\(\s*\w+\.textContent",
    # _JS_CLICK_BTN (CICLO-inicio-de-todas.md): pulsa el primer botón, enlace o input submit de la página, fuera del
    # encabezado y de la navegación, cuyo texto calce, visible o no. Filtra por el texto, pero no mira si se ve ni de
    # qué pantalla es. Hasta c4df3ab ninguna forma de esta foto lo veía, y MSC lo usaba antes de su guarda en «Search
    # Schedule».
    "primero-que-calce-el-texto": r"\.find\(\s*b\s*=>\s*re\.test\(",
}

# La foto: cada forma que el detector encuentra antes de la guarda, con su motivo. Lo que no está aquí es un
# clic genérico nuevo, y la prueba cae. Las «ESPECÍFICO» toman el primero entre candidatos ya filtrados por su
# texto o por el dato de la reserva; las «NO ES CLIC» calzan con la forma sin pulsar nada.
PERMITIDOS = {
    ("reservar_one", "_JS_CLICK_OPTION_EXACT", "primero-sin-filtro"): 1,     # ESPECÍFICO: texto exacto
    ("reservar_one", "_JS_PICK_SUGGESTION", "primero-sin-filtro"): 1,        # ESPECÍFICO: la ciudad
    ("reservar_one", "_one_click_search", "primero-sin-filtro"): 1,          # ESPECÍFICO: «Search» exacto
    ("reservar_one", "_set_weeks_one", "primero-sin-filtro"): 1,             # ESPECÍFICO: «8 semanas»
    # ONE lee sus tarjetas y pulsa la de la próxima salida (CICLO-proxima-salida.md); hasta 8927e1f lo hacía todo
    # _JS_ONE_SELECT_NAVE, que pulsaba el botón del elemento más chico con la nave. Hasta 9051f43,
    # _JS_ONE_TARJETAS_NAVE tomaba la última palabra de la nave por el viaje («ultimo-por-posicion»: 2); desde
    # CICLO-cola-tres-items.md exige todas las palabras y ya no la toma aparte.
    ("reservar_one", "_JS_ONE_CLIC_TARJETA", "primero-sin-filtro"): 1,       # ESPECÍFICO: el único botón de la elegida
    # El «Next» del asistente de ONE, desde CICLO-cola-seis-items.md: hasta f68ce6c era _JS_CLICK_BTN, que ninguna forma
    # de esta foto veía (pulsaba el primero cuyo texto calzara, visible o no).
    ("reservar_one", "_JS_ONE_SIGUIENTE", "primero-sin-filtro"): 1,          # ESPECÍFICO: el único «Next» a la vista
    # Entre 05cfdb7 y el encargo 33, _JS_ONE_SEMANAS («primero-sin-filtro»: 2) ampliaba las semanas de ONE: el único
    # selector «N weeks» y su opción más larga. ONE ya no pasa de 8 semanas (CICLO-ampliar-msc-y-cma.md).
    ("reservar_msc", "_msc_puerto", "primero-sin-filtro"): 1,                # ESPECÍFICO: la ciudad
    ("reservar_cma", "_cma_completar_info_extra", "primero-sin-filtro"): 1,  # ESPECÍFICO: «40…High Cube»
    ("reservar_cma", "_cma_aviso", "ultimo-por-posicion"): 1,                # NO ES CLIC: lee el último aviso
    ("reservar_cma", "_cma_comentarios", "textarea-en-js"): 1,               # ESPECÍFICO: placeholder o etiqueta
    ("reservar_cosco", "_JS_COSCO_AUTO_PICK", "primero-sin-filtro"): 1,      # ESPECÍFICO: la ciudad
    # ESPECÍFICO: entre las sugerencias de la ciudad, la de Chile o la que empieza por ella (encargo 38).
    ("reservar_cosco", "_JS_COSCO_AUTO_PICK", "primero-por-textContent"): 2,
    # MAERSK ya no tiene ninguna: hasta el encargo 39 tenía el respaldo de «Continue» en «Recommended services», el
    # primero a la vista cuyo texto entero es «Continue» («primero-por-textContent»: 1; CICLO-maersk-cuatro-puntos.md).
    ("reservar_cosco", "_JS_COSCO_COPIAR_PERFIL", "casilla-por-tipo"): 1,       # ESPECÍFICO: dentro de «Copy from my profile»
    ("reservar_cosco", "_JS_COSCO_LEER_DESPLEGABLE", "clase-de-componente"): 1,  # NO ES CLIC: lee por su placeholder
    ("reservar_hyundai", "_hmm_autocomplete", "primero-sin-filtro"): 1,      # ESPECÍFICO: la ciudad
    # HYUNDAI: el único textarea del formulario titulado «Remark (n / m)», medido en hmm_f<fila>_remark.html
    # (CICLO-pendientes-con-evidencia.md). Hasta e423a38 era el FRENO del primer textarea visible.
    ("reservar_hyundai", "_JS_HMM_REMARK", "textarea-en-js"): 1,             # ESPECÍFICO: el de su recuadro
    # MAERSK: ninguna. Hasta el encargo 36, los términos y condiciones, «el último checkbox» por cuatro vías (FRENO):
    # «casilla-por-tipo» 1, «rol-sin-nombre» 1 y «ultimo-por-posicion» 5; desde entonces, la casilla se busca por su
    # texto, y la fecha de retiro, por su fecha (TestTerminosMaersk, TestRetiroMaersk;
    # CICLO-maersk-retiro-y-terminos.md). Hasta el encargo 37, la referencia de retiro, el primer textarea:
    # «clase-de-componente» 1 y «textarea-cualquiera» 1; desde entonces, por su name (TestReferenciaMaersk;
    # CICLO-maersk-ultimos-puntos.md).
}


def linea_guarda(f):
    return min(n.lineno for n in ast.walk(f) if isinstance(n, ast.If) and "es_modo_emision" in ast.unparse(n.test))


def antes_de_la_guarda(f, g):
    """Lo que corre antes de la guarda: las sentencias que terminan antes, enteras; de las que la contienen
    (un bucle, un try, un if), su cabecera y, recursivamente, sus sentencias anteriores."""
    out = []

    def recortar(stmts):
        for s in stmts:
            if s.end_lineno < g:
                out.append(s)
            elif s.lineno < g:
                for campo in ("test", "iter", "items"):
                    v = getattr(s, campo, None)
                    if isinstance(v, ast.AST):
                        out.append(v)
                    elif isinstance(v, list):
                        out.extend(i.context_expr if isinstance(i, ast.withitem) else i for i in v)
                for campo in ("body", "orelse", "finalbody"):
                    recortar(getattr(s, campo, []) or [])
                for h in getattr(s, "handlers", []) or []:
                    recortar(h.body)

    recortar(f.body)
    return out


def universo(tree):
    """Por reservador: los nodos antes de su guarda, las funciones del módulo que esos nodos llaman
    (transitivamente, enteras) y las constantes de texto que todo eso nombra (el JavaScript inyectado), con las que
    esas constantes nombran al armarse (como _JS_CMA_PANELES_VISIBLES, CICLO-pendientes-con-evidencia.md)."""
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    consts = {t.id: n for n in tree.body if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
    out = {}
    for r in RESERVADORES:
        tramo = antes_de_la_guarda(funcs[r], linea_guarda(funcs[r]))
        vistas, pendientes = set(), {c.func.id for n in tramo for c in ast.walk(n)
                                     if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id in funcs}
        while pendientes:
            x = pendientes.pop()
            if x in vistas or x in RESERVADORES:
                continue
            vistas.add(x)
            pendientes |= {c.func.id for c in ast.walk(funcs[x])
                           if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id in funcs}
        nodos = tramo + [funcs[x] for x in vistas]
        nombres = {n.id for nodo in nodos for n in ast.walk(nodo) if isinstance(n, ast.Name) and n.id in consts}
        pendientes = set(nombres)
        while pendientes:
            nuevos = {n.id for n in ast.walk(consts[pendientes.pop()])
                      if isinstance(n, ast.Name) and n.id in consts} - nombres
            nombres |= nuevos
            pendientes |= nuevos
        out[r] = (tramo, sorted(vistas), sorted(nombres))
    return out


def clics_genericos(mod):
    """(reservador, lugar, forma) de cada forma genérica que aparece antes de la guarda."""
    src = Path(mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    consts = {t.id: n for n in tree.body if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
    hallados = []
    for r, (tramo, vistas, nombres) in universo(tree).items():
        textos = [(r, ast.get_source_segment(src, n) or "") for n in tramo]
        textos += [(x, ast.get_source_segment(src, funcs[x])) for x in vistas]
        textos += [(c, ast.get_source_segment(src, consts[c])) for c in nombres]
        for lugar, texto in textos:
            for forma, patron in GENERICOS.items():
                hallados += [(r, lugar, forma)] * len(re.findall(patron, texto))
    return Counter(hallados)


def que_cortan(tree):
    """Funciones del módulo que levantan ObjetivoNoEncontrado, directamente o por lo que llaman."""
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    cortan = {n for n, f in funcs.items() for s in ast.walk(f)
              if isinstance(s, ast.Raise) and "ObjetivoNoEncontrado" in ast.unparse(s)}
    cambio = True
    while cambio:
        cambio = False
        for n, f in funcs.items():
            if n not in cortan and n not in RESERVADORES and any(
                    isinstance(c, ast.Call) and getattr(c.func, "id", "") in cortan for c in ast.walk(f)):
                cortan.add(n)
                cambio = True
    return cortan


class ConRegistro(soporte.CasoAQ):
    def corrida(self, nombre="corrida"):
        vistas = []
        reg = self.mod.Registro(self.sb / nombre / "log.txt", on_log=vistas.append)
        self.addCleanup(reg.cerrar)
        return reg, vistas, self.sb / nombre / "log.txt"


class TestSinClicACiegas(ConRegistro):
    def envuelto(self, reservar, prefijo="one"):
        return self.mod._sin_clic_a_ciegas(prefijo)(reservar)

    def test_sin_objetivo_queda_no_enviada_con_el_paso_y_lo_que_buscaba(self):
        def reservar(page, reserva, creds, reg, on_pausa=None):
            reg.paso("Paso 1 · algo que sí salió")
            raise self.mod.ObjetivoNoEncontrado("Paso de prueba", "el botón «Prueba» (texto)")
        reg, vistas, log = self.corrida()
        pagina = soporte.PaginaFalsa()
        r = self.envuelto(reservar, "cma")(pagina, {"fila": 7}, {}, reg)
        detalle = ("Paso de prueba: no encontré el botón «Prueba» (texto), así que no pulsé nada. La reserva no se "
                   "envió; revisa ese paso en el portal.")
        self.assertEqual(r, ("NO ENVIADA", detalle))
        self.assertEqual(pagina.capturas, [("cma_f7_sin_objetivo.png", False)])
        for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):        # log.txt y pantalla
            self.assertIn(f"· ✗ NO ENVIADA · {detalle}", donde)

    def test_el_motivo_dice_primero_lo_que_pide_el_portal(self):
        # Si el paso leyó lo que el portal pide en esa pantalla, el motivo lo dice antes (decisión de Marcelo,
        # CICLO-maersk-retiro-y-terminos.md); sin eso, el motivo de siempre (la prueba de arriba).
        def reservar(page, reserva, creds, reg, on_pausa=None):
            raise self.mod.ObjetivoNoEncontrado("Paso de prueba", "el botón «Prueba» (texto)", pide="Campo X («falta»)")
        reg, vistas, log = self.corrida()
        r = self.envuelto(reservar, "mk")(soporte.PaginaFalsa(), {"fila": 7}, {}, reg)
        detalle = ("Paso de prueba: el portal pide: Campo X («falta»). No encontré el botón «Prueba» (texto), así que no "
                   "pulsé nada. La reserva no se envió; revisa ese paso en el portal.")
        self.assertEqual(r, ("NO ENVIADA", detalle))
        for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):
            self.assertIn(f"· ✗ NO ENVIADA · {detalle}", donde)

    def test_lo_demas_pasa_igual(self):
        def bien(page, reserva, creds, reg, on_pausa=None):
            """doc"""
            return ("OK-EJEMPLO", f"fila {reserva['fila']} {on_pausa}")

        def falla(page, reserva, creds, reg, on_pausa=None):
            raise RuntimeError("otra falla")
        reg, _, _ = self.corrida()
        pagina = soporte.PaginaFalsa()
        envuelto = self.envuelto(bien)
        self.assertEqual(envuelto(pagina, {"fila": 5}, {}, reg, on_pausa="p"), ("OK-EJEMPLO", "fila 5 p"))
        self.assertEqual((envuelto.__name__, envuelto.__doc__), ("bien", "doc"))
        with self.assertRaises(RuntimeError):
            self.envuelto(falla)(pagina, {"fila": 5}, {}, reg)
        self.assertEqual(pagina.capturas, [])

    def test_ningun_except_exception_se_lo_traga(self):
        # El camino tiene muchos «except Exception: pass»; si ObjetivoNoEncontrado heredara de Exception, la
        # reserva seguiría como si nada.
        def ayudante():
            try:
                raise self.mod.ObjetivoNoEncontrado("Paso", "algo")
            except Exception:
                return "tragado"

        def reservar(page, reserva, creds, reg, on_pausa=None):
            return ("OK-EJEMPLO", ayudante())
        reg, _, _ = self.corrida()
        self.assertEqual(self.envuelto(reservar)(soporte.PaginaFalsa(), {"fila": 5}, {}, reg)[0], "NO ENVIADA")

    def test_cada_reservador_que_corta_esta_decorado(self):
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        cortan, uni = que_cortan(tree), universo(tree)
        decorados = {}
        for r, prefijo in RESERVADORES.items():
            decos = [ast.unparse(d) for d in funcs[r].decorator_list]
            if any(x in cortan for x in uni[r][1]):
                decorados[r] = decos
                # Desde el encargo 28, antes va el de la fila sin nave (CICLO-solo-la-nave-pedida.md); desde el 42,
                # entre los dos, el de la fila sin puerto de carga o sin destino (CICLO-maersk-y-fila-sin-ruta.md);
                # desde el 50, en COSCO, por fuera de todos, el del puerto traducido (CICLO-msc-segundo-intento.md);
                # desde el 54, en CMA, por dentro de todos, el de CMA detenida (CICLO-cma-acceso-restringido.md); y
                # desde el 55, el de CMA guarda con plazo el HTML del paso sin objetivo
                # (CICLO-pausa-plazos-y-datadome.md).
                plazo = ", plazo_ms=CMA_PLAZO_MS" if r == "reservar_cma" else ""
                self.assertEqual(decos, (["_con_el_puerto_de_cosco"] if r == "reservar_cosco" else [])
                                 + ["_con_la_nave_de_la_fila", "_con_la_ruta_de_la_fila",
                                    f"_sin_clic_a_ciegas({prefijo!r}{plazo})"]
                                 + (["_cma_si_se_detuvo"] if r == "reservar_cma" else []), r)
        self.assertEqual(sorted(decorados), sorted(self.CORTAN))

    CORTAN = ["reservar_cma", "reservar_cosco", "reservar_hyundai", "reservar_maersk", "reservar_msc", "reservar_one"]

    def test_nada_se_traga_el_corte(self):
        # Nada de lo que corre antes de la guarda atrapa ObjetivoNoEncontrado, BaseException o todo (except desnudo):
        # se tragaría el corte, y la reserva seguiría con lo que se pulse después (revisión del encargo 37).
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        malos = []
        for r, (tramo, vistas, _) in universo(tree).items():
            for nodo in tramo + [funcs[x] for x in vistas]:
                for h in ast.walk(nodo):
                    if isinstance(h, ast.ExceptHandler):
                        tipo = ast.unparse(h.type) if h.type is not None else ""
                        if not tipo or re.search(r"\b(ObjetivoNoEncontrado|BaseException)\b", tipo):
                            malos.append((r, h.lineno, tipo or "except:"))
        self.assertEqual(malos, [])

    def test_lo_que_corta_no_se_llama_despues_de_la_guarda(self):
        # Después de la guarda el envío pudo haber salido: ahí nada puede terminar en NO ENVIADA.
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        cortan = que_cortan(tree)
        vistas = []
        for r in RESERVADORES:
            g = linea_guarda(funcs[r])
            for c in ast.walk(funcs[r]):
                if isinstance(c, ast.Call) and getattr(c.func, "id", "") in cortan and c.lineno > g:
                    kw = {k.arg: ast.unparse(k.value) for k in c.keywords}
                    vistas.append((r, c.func.id, kw.get("antes_de_la_guarda")))
        self.assertEqual(vistas, [("reservar_one", "_cerrar_modal_one", "False")])



class LocalizadorALaVista:
    """Localizador falso a la vista y habilitado: acepta cualquier otra cosa sin hacer nada, y la anota en 'eventos'
    con su selector (TestSinSugerenciaNoSigue). Hasta la revisión de código del encargo 42 no la anotaba: un reservador
    que siguiera escribiendo en la página después del ayudante que no eligió pasaba sin que se viera."""
    first = property(lambda s: s)

    def __init__(self, eventos, sel):
        self.eventos, self.sel = eventos, sel

    def count(self):
        return 1

    def is_visible(self, **k):
        return True

    def is_disabled(self, **k):
        return False

    def __getattr__(self, nombre):
        def accion(*a, **k):
            self.eventos.append(("accion", self.sel, nombre))
        return accion


class PaginaHastaLaRuta(soporte.PaginaFalsa):
    """Una página falsa que deja llegar a cada reservador hasta su origen y su destino, con los pasos de antes
    reemplazados (TestSinSugerenciaNoSigue): cada localizador está a la vista, y 'eventos' anota en orden lo que se hace
    con ellos (también con los de get_by_text, get_by_role, get_by_placeholder y get_by_label), cada acción de la
    página (ACCIONES), del teclado y del mouse, cada dirección que se abre y cada JavaScript que se corre, con el que el
    programa también pulsa. Solo no anota el que guarda el HTML de la evidencia (el que trae «getHTML»), que solo lee
    (revisiones del encargo 42), ni las dos lecturas con que CMA mira si DataDome está (el código HTTP del documento y
    el texto, LECTURAS_DE_DATADOME; encargo 55), que tampoco tocan nada. Sin un __getattr__ general: lo que la página no
    tiene (main_frame, content) sigue fallando."""
    LECTURAS_DE_DATADOME = ("performance.getEntriesByType('navigation')",
                            "() => document.body ? document.body.innerText")
    ACCIONES = ("fill", "click", "dblclick", "type", "press", "select_option", "check", "uncheck", "hover",
                "dispatch_event", "set_input_files", "tap", "focus")

    def __init__(self):
        super().__init__(texto="")
        self.eventos = []
        self.goto = lambda url, **k: self.eventos.append(("abre", url))
        self.keyboard = types.SimpleNamespace(**{n: self.anota("teclado", n)
                                                 for n in ("press", "type", "insert_text", "down", "up")})
        self.mouse = types.SimpleNamespace(**{n: self.anota("mouse", n)
                                              for n in ("click", "dblclick", "move", "down", "up", "wheel")})
        for nombre in self.ACCIONES:
            setattr(self, nombre, self.anota("pagina", nombre))

    def anota(self, donde, nombre):
        return lambda *a, **k: self.eventos.append((donde, nombre))

    def locator(self, sel):
        if sel == ":root":                       # lo que el programa lee con plazo (encargo 55)
            return soporte.RaizFalsa(self)
        return LocalizadorALaVista(self.eventos, sel)

    def get_by_text(self, texto, **k):
        return LocalizadorALaVista(self.eventos, f"texto={texto}")

    def get_by_role(self, rol, **k):
        return LocalizadorALaVista(self.eventos, f"rol={rol}")

    def get_by_placeholder(self, texto, **k):
        return LocalizadorALaVista(self.eventos, f"placeholder={texto}")

    def get_by_label(self, texto, **k):
        return LocalizadorALaVista(self.eventos, f"etiqueta={texto}")

    def evaluate(self, js, *a):
        if "getHTML" not in js and not any(m in js for m in self.LECTURAS_DE_DATADOME):
            self.eventos.append(("javascript", js[:40]))
        return super().evaluate(js, *a)


class MarcoConCampo:
    """El marco del formulario de COSCO, con su campo «Origin City» a la vista (TestSinSugerenciaNoSigue): anota cada
    JavaScript que se le corre en 'guiones' y, si se le dan, en los 'eventos' de la página (revisión final del encargo
    42: sin eso, COSCO podía seguir en su marco después del ayudante que no eligió sin que se viera)."""
    url = "https://portal.invalid/bkg2"

    def __init__(self, eventos=None):
        self.guiones, self.eventos = [], eventos

    def evaluate(self, js, *a):
        self.guiones.append(js)
        if self.eventos is not None:
            self.eventos.append(("marco", js[:40]))
        return 1


class MarcoSinCampos:
    """El marco del formulario de COSCO (bkg2) sin su campo «Origin City» (encargo 48): el JavaScript que lo cuenta da
    0, y anota cuántas veces se lo corrió; da su HTML a la evidencia. Otro JavaScript queda en 'prohibidos' (revisión
    del encargo 48: el programa se traga sus errores)."""
    url = "https://portal.invalid/bkg2"

    def __init__(self, mod):
        self.mod, self.cuentas, self.prohibidos = mod, 0, []

    def evaluate(self, js, *a):
        if js == self.mod._JS_HTML_COMPLETO:
            return {"html": "<body>marco sintetico</body>", "sombras": 0}
        if "origin ci" in js:
            self.cuentas += 1
            return 0
        self.prohibidos.append(js[:40])
        return None


class PaginaNewBooking(soporte.PaginaFalsa):
    """New Booking falsa de COSCO (encargo 48): anota cada dirección que se abre y da su HTML a la evidencia; 'marco'
    es el marco del formulario, en sus frames. Otro JavaScript queda en 'prohibidos', y cada espera, en 'esperas'
    (revisión del encargo 48)."""

    def __init__(self, mod, marco=None):
        super().__init__(frames=[marco] if marco else [])
        self.mod, self.main_frame, self.abiertas, self.prohibidos = mod, None, [], []
        self.goto = lambda url, **k: self.abiertas.append(url)

    def evaluate(self, js, *a):
        if js == self.mod._JS_HTML_COMPLETO:
            return {"html": "<body>new booking sintetica</body>", "sombras": 0}
        self.prohibidos.append(js[:40])
        return None


def _nada(*a, **k):
    return None


def _si(*a, **k):
    return True


class TestSinSugerenciaNoSigue(ConRegistro):
    """Si el ayudante de origen, de destino o del lugar de entrega no elige ninguna sugerencia, la fila queda NO ENVIADA
    con el motivo, y la naviera no sigue: ni siquiera al campo siguiente (decisión de Marcelo, encargo 42,
    CICLO-maersk-y-fila-sin-ruta.md). Hasta ahí, MAERSK, HYUNDAI, el destino de COSCO y el lugar de entrega de CMA
    seguían sin el campo; y un False de _cma_puerto habría dado REVISAR en el origen, pero no lo devuelve: corta él
    mismo. Desde el encargo 43, _mk_ciudad también corta él mismo (test_evidencia): aquí se mira que reservar_maersk
    no lo ataje. Cada reservador corre de verdad hasta su ruta, con los pasos de antes reemplazados, y sus ayudantes
    responden lo que dice cada caso."""
    RESERVA = {"fila": 9, "pol": "PUERTO ALFA, CHILE", "destino_orig": "PUERTO BETA", "destino_final": "CIUDAD GAMMA",
               "nave": "NAVE PRUEBA UNO", "viaje": "", "dia_carga": "", "cotizacion": ""}
    # CMA sin un lugar de entrega aparte: prueba primero el puerto y, si el portal no cubre la ruta, el ramp.
    RESERVA_CMA_RAMP = dict(RESERVA, destino_orig="CIUDAD GAMMA")
    ANTES = {
        "reservar_one": dict(esperar_hasta=_si, _cerrar_modal_one=lambda *a, **k: False, esperar=_nada),
        "reservar_msc": dict(_msc_esperar_paso=_si, _msc_cookies=_nada, _msc_kendo_dropdown=_si, _msc_next=_nada,
                             _msc_fecha=_si, rellenar=_nada, esperar=_nada),
        "reservar_cosco": dict(_cosco_esperar_contenido=_nada, _cosco_frame=lambda *a, **k: MarcoConCampo(),
                               _cosco_puerto_de_carga=lambda *a, **k: "PUERTO ALFA", esperar=_nada),
        "reservar_hyundai": dict(esperar_hasta=_si, _hmm_realclick=_nada, esperar=_nada),
        "reservar_maersk": dict(_mk_listo_para_reservar=_si, _maersk_cookies=_nada, _mk_got_it=_nada, esperar_hasta=_si,
                                esperar=_nada),
        "reservar_cma": dict(_cma_esperar_desafio=_si, esperar_hasta=_si, esperar=_nada,
                             _cma_esperar_resultado=lambda *a, **k: "aviso",
                             _cma_aviso=lambda *a, **k: "No matching quotation for this route"),
    }

    def correr(self, caso, reservar, ayudante, respuestas, reserva, fijos=None):
        """Corre 'reservar' con los pasos de antes reemplazados, 'ayudante' respondiendo en orden 'respuestas' y los de
        'fijos' ({nombre: respuesta}) siempre lo mismo; una respuesta que es una excepción, la levanta. Devuelve
        (resultado, evidencia de cada llamada a un ayudante, lo que se hizo en la página después de la última). Si el
        reservador sigue después de la última respuesta, la llamada falla: no debía seguir."""
        llamadas, cola, pagina = [], list(respuestas), PaginaHastaLaRuta()

        def responde(fija=None):
            def falso(*a, **k):
                llamadas.append(k.get("evidencia", ""))
                pagina.eventos.append(("ayudante", k.get("evidencia", "")))
                if fija is not None:
                    return fija
                if not cola:
                    raise AssertionError(f"el reservador siguió hasta {k.get('evidencia')}")
                respuesta = cola.pop(0)
                if isinstance(respuesta, BaseException):
                    raise respuesta
                return respuesta
            return falso
        cambios = dict(self.ANTES[reservar], **{ayudante: responde()})
        cambios.update({n: responde(v) for n, v in (fijos or {}).items()})
        if reservar == "reservar_cosco":            # su marco anota en la misma lista
            cambios["_cosco_frame"] = lambda *a, **k: MarcoConCampo(pagina.eventos)
        reg, _, _ = self.corrida(f"sin_sugerencia_{caso}")
        with mock.patch.multiple(self.mod, **cambios):
            r = getattr(self.mod, reservar)(pagina, dict(reserva), {"contrato": "CT-PRUEBA"}, reg)
        ultima = max(i for i, e in enumerate(pagina.eventos) if e[0] == "ayudante")
        return r, llamadas, pagina.eventos[ultima + 1:]

    def test_sin_sugerencia_ninguna_naviera_sigue(self):
        R, RAMP = self.RESERVA, self.RESERVA_CMA_RAMP
        que = "una sugerencia que elegir para «{}»"
        exacta = self.mod._mk_sin_una_exacta

        def corte_mk(campo, ciudad):
            return self.mod.ObjetivoNoEncontrado(f"{campo} de MAERSK", exacta(ciudad, 0))
        casos = [
            ("reservar_one", "_fill_port", [False], R, None, "Origen de ONE", que.format("PUERTO ALFA"),
             ["one_f9_origen"]),
            ("reservar_one", "_fill_port", [True, False], R, None, "Destino de ONE", que.format("CIUDAD GAMMA"),
             ["one_f9_origen", "one_f9_destino"]),
            ("reservar_msc", "_msc_puerto", [False], R, None, "Port of Load de MSC", que.format("PUERTO ALFA"),
             ["msc_f9_origen"]),
            ("reservar_msc", "_msc_puerto", [True, False], R, None, "Port of Discharge de MSC",
             que.format("CIUDAD GAMMA"), ["msc_f9_origen", "msc_f9_destino"]),
            ("reservar_cosco", "_cosco_autocomplete", [False], R, None, "Destination de COSCO",
             que.format("CIUDAD GAMMA"), ["cosco_f9_destino"]),
            ("reservar_hyundai", "_hmm_autocomplete", [False], R, None, "Origen de HYUNDAI", que.format("PUERTO ALFA"),
             ["hmm_f9_origen"]),
            ("reservar_hyundai", "_hmm_autocomplete", [True, False], R, None, "Destino de HYUNDAI",
             que.format("CIUDAD GAMMA"), ["hmm_f9_origen", "hmm_f9_destino"]),
            # MAERSK: desde el encargo 43 el corte viene de adentro de _mk_ciudad, y el reservador no lo ataja.
            ("reservar_maersk", "_mk_ciudad", [corte_mk("Origen", "PUERTO ALFA")], R, None, "Origen de MAERSK",
             exacta("PUERTO ALFA", 0), ["mk_f9_origen"]),
            ("reservar_maersk", "_mk_ciudad", [("SUG", "SUG"), corte_mk("Destino", "CIUDAD GAMMA")], R, None,
             "Destino de MAERSK", exacta("CIUDAD GAMMA", 0), ["mk_f9_origen", "mk_f9_destino"]),
            ("reservar_cma", "_cma_puerto", [False], R, None, "Origen de CMA", que.format("PUERTO ALFA"),
             ["cma_f9_origen_ramp_separado"]),
            ("reservar_cma", "_cma_puerto", [True, False], R, None, "POD de CMA", que.format("PUERTO BETA"),
             ["cma_f9_origen_ramp_separado", "cma_f9_destino_ramp_separado"]),
            ("reservar_cma", "_cma_entrega", [""], R, {"_cma_puerto": True}, "Lugar de entrega de CMA",
             que.format("CIUDAD GAMMA"),
             ["cma_f9_origen_ramp_separado", "cma_f9_destino_ramp_separado", "cma_f9_entrega_ramp_separado"]),
            ("reservar_cma", "_cma_puerto", [True, False], RAMP, None, "POD de CMA", que.format("CIUDAD GAMMA"),
             ["cma_f9_origen_puerto", "cma_f9_destino_puerto"]),
            # El portal no cubre el puerto («no matching»): prueba el ramp, y ahí no elige.
            ("reservar_cma", "_cma_puerto", [True, True, True, False], RAMP, None, "POD de CMA",
             que.format("CIUDAD GAMMA"),
             ["cma_f9_origen_puerto", "cma_f9_destino_puerto", "cma_f9_origen_ramp", "cma_f9_destino_ramp"]),
            # Ahí, el motivo dice también el aviso con que CMA rechazó el puerto (revisión de código del encargo 42).
            ("reservar_cma", "_cma_entrega", [""], RAMP, {"_cma_puerto": True}, "Lugar de entrega de CMA",
             que.format("CIUDAD GAMMA") + " (con el puerto, CMA avisó: «No matching quotation for this route»)",
             ["cma_f9_origen_puerto", "cma_f9_destino_puerto", "cma_f9_origen_ramp", "cma_f9_destino_ramp",
              "cma_f9_entrega_ramp"]),
        ]
        for caso, (reservar, ayudante, respuestas, reserva, fijos, paso, buscaba, llamadas) in enumerate(casos):
            with self.subTest(reservar=reservar, paso=paso, llamadas=len(llamadas)):
                r, vistas, despues = self.correr(caso, reservar, ayudante, respuestas, reserva, fijos)
                motivo = (f"{paso}: no encontré {buscaba}, así que no pulsé nada. La reserva no se envió; revisa ese "
                          "paso en el portal.")
                self.assertEqual(r, ("NO ENVIADA", motivo))
                self.assertEqual(vistas, llamadas)
                # Después del ayudante que no eligió, nada en la página: ni un clic, una tecla ni lo que se escribe.
                self.assertEqual(despues, [])

    def test_sin_una_palabra_corta_el_ayudante(self):
        # «-» o «X» no son un puerto ni un destino (_ciudad_de; revisión de código del encargo 42). La regla de la fila
        # (_falta_en_la_fila) no mira el destino original de CMA cuando el lugar de entrega va aparte: ahí corta el
        # ayudante del POD, sin escribir ni pulsar. El de COSCO sirve también al contrato y corta solo con el texto
        # vacío: su origen y su destino los toma con _ciudad_de quien lo llama, y cortan aunque la fila pasara la regla.
        # El origen, también con «X CHILE» y «CHILE X»: la palabra se pide al puerto sin «CHILE» en ninguna posición
        # (_puerto_de_carga; revisiones del informe).
        m = self.mod
        real = m._cma_puerto
        sin_puerto = "el puerto de carga en la fila (la celda no trae su nombre; escríbelo en la planilla)"

        def cma_puerto(page, sel, *a, **k):
            if sel != "#pol":
                return real(page, sel, *a, **k)
            page.eventos.append(("ayudante", sel))
            return True
        casos = [
            ("reservar_cma", dict(self.RESERVA, destino_orig="-"), {"_cma_puerto": cma_puerto}, "POD de CMA",
             m._TEXTO_DE_LA_FILA),
            ("reservar_cosco", dict(self.RESERVA, pol="X"), {"_cosco_puerto_de_carga": m._cosco_puerto_de_carga},
             "Origin City de COSCO", sin_puerto),
            ("reservar_cosco", dict(self.RESERVA, pol="X CHILE"), {"_cosco_puerto_de_carga": m._cosco_puerto_de_carga},
             "Origin City de COSCO", sin_puerto),
            ("reservar_cosco", dict(self.RESERVA, pol="CHILE X"), {"_cosco_puerto_de_carga": m._cosco_puerto_de_carga},
             "Origin City de COSCO", sin_puerto),
            ("reservar_cosco", dict(self.RESERVA, destino_final="-"), {}, "Destination de COSCO", m._TEXTO_DE_LA_FILA),
        ]
        for caso, (reservar, reserva, cambios, paso, buscaba) in enumerate(casos):
            with self.subTest(reservar=reservar, paso=paso):
                reg, _, _ = self.corrida(f"sin_palabra_{caso}")
                pagina, marco = PaginaHastaLaRuta(), MarcoConCampo()
                if reservar == "reservar_cosco":        # como si la fila hubiera pasado la regla
                    cambios = dict(cambios, _falta_en_la_fila=lambda *a, **k: "", _cosco_frame=lambda *a, **k: marco)
                with mock.patch.multiple(m, **dict(self.ANTES[reservar], **cambios)):
                    r = getattr(m, reservar)(pagina, dict(reserva), {"contrato": "CT-PRUEBA"}, reg)
                self.assertEqual(r, ("NO ENVIADA", f"{paso}: no encontré {buscaba}, así que no pulsé nada. La reserva "
                                                   "no se envió; revisa ese paso en el portal."))
                # Sin escribir en el campo: en CMA, nada en la página después del puerto de carga; en COSCO, ningún
                # JavaScript que escriba en el marco.
                marca = [i for i, e in enumerate(pagina.eventos) if e[0] == "ayudante"]
                self.assertEqual(pagina.eventos[marca[-1] + 1:] if marca else [], [])
                self.assertNotIn(m._JS_COSCO_AUTO_SET, marco.guiones)


class TestFotoDeClicsGenericos(soporte.CasoAQ):
    def test_ningun_clic_generico_nuevo_antes_de_la_guarda(self):
        hallados = dict(clics_genericos(self.mod))
        nuevos = {k: v for k, v in hallados.items() if v > PERMITIDOS.get(k, 0)}
        self.assertEqual(nuevos, {}, "reapareció un clic genérico antes de la guarda: clasifícalo "
                                     "(CICLO-clics-a-ciegas.md) y quítalo, o fotografíalo con su motivo")
        self.assertEqual(hallados, PERMITIDOS)


class TestOne(ConRegistro):
    def test_js_siguiente_solo_el_de_la_pantalla(self):
        # El «Next» del asistente: el único botón a la vista, fuera del encabezado y de la navegación, cuyo texto es
        # exactamente Next o Siguiente (sin los espacios de los extremos y sin distinguir mayúsculas). Medido con OCR en
        # las capturas de Booking Parties, Container & Cargo y Additional Information del 2026-09-21 (en esta última, en 2
        # de 5, las que muestran el pie): al lado va «Previous» (CICLO-cola-seis-items.md).
        guion = "const f = " + self.mod._JS_ONE_SIGUIENTE + r""";
const boton = (texto, {visible = true, tamano = true, en = '', tag = 'BUTTON', valor = ''} = {}) => ({
  tagName: tag, textContent: texto, value: valor, clics: 0, offsetParent: visible ? {} : null,
  getBoundingClientRect: () => (tamano ? {width: 80, height: 30} : {width: 0, height: 0}),
  closest: (sel) => (en && sel.includes(en) ? {} : null), scrollIntoView() {}, click() { this.clics++; }});
const correr = (botones) => {
  global.document = {querySelectorAll: (s) => (s === 'button,a,input[type=submit]' ? botones : [])};
  const r = f();
  return [r, botones.map(b => b.clics)];
};
console.log(JSON.stringify([
  correr([boton('Previous'), boton('Next')]),
  correr([boton('Next', {visible: false}), boton('Next', {tamano: false}), boton('Next')]),
  correr([boton('Next'), boton('Next')]),
  correr([boton('Next', {en: 'header'}), boton(' next ')]),
  correr([boton('Next step'), boton('Continue'), boton('Review'), boton('Revisar')]),
  correr([boton('', {tag: 'INPUT', valor: 'Siguiente'})]),
  correr([boton('Cancel', {en: 'dialog'}), boton('Next', {en: 'dialog'})]),
  correr([boton('Next', {en: 'dialog'}), boton('Next')]),
  correr([]),
]));
"""
        self.assertEqual(correr_node(self, guion), [
            [1, [0, 1]],            # el «Next», no el «Previous»
            # Uno oculto (sin lugar en la página, o sin tamaño) no cuenta: hasta f68ce6c _JS_CLICK_BTN pulsaba el primero.
            [1, [0, 0, 1]],
            [2, [0, 0]],            # dos a la vista: ninguno; hasta f68ce6c, el primero
            [1, [0, 1]],            # el del encabezado no cuenta
            [0, [0, 0, 0, 0]],      # otros textos no son «Next»: hasta f68ce6c, Continue o Review también
            [1, [1]],               # un input con su valor
            # Un «Next» en una ventana emergente (como «Vessel Information», que lleva a elegir otra nave): ninguno, ni
            # el del pie. Hasta f68ce6c, el primero.
            [-1, [0, 0]],
            [-1, [0, 0]],
            [0, []],
        ])

    def test_siguiente_sin_uno_solo_corta(self):
        reg, vistas, _ = self.corrida()
        p = PaginaSiguiente(self.mod, [0, 1])            # todavía no estaba: reintenta
        self.assertIsNone(self.mod._one_siguiente(p, reg, "Booking Parties", "booking-parties"))
        self.assertEqual((p.busquedas, vistas[-1].endswith("Booking Parties: Next")), (2, True))
        # Sin ninguno tras 3 intentos, con dos, con uno en una ventana emergente, o si la búsqueda falla, corta sin pulsar
        # (y sin reintentar tras la falla: el clic pudo haber salido). Hasta f68ce6c, sin ninguno lo anotaba y seguía; con
        # dos, pulsaba el primero; con el de la ventana, también; y la falla dejaba la reserva en ERROR.
        casos = (([0, 0, 0], 3, "un solo botón «Next» a la vista (había 0)"),
                 ([2, 1], 1, "un solo botón «Next» a la vista (había 2)"),
                 ([-1, 1], 1, "un «Next» fuera de una ventana emergente: la que está abierta trae el suyo"),
                 ([RuntimeError("navegando"), 1], 1, "un solo botón «Next» a la vista (no pude buscarlo: navegando)"))
        for respuestas, busquedas, buscaba in casos:
            with self.subTest(respuestas=respuestas):
                p = PaginaSiguiente(self.mod, respuestas, "additional-information")
                with self.assertRaises(self.mod.ObjetivoNoEncontrado) as c:
                    self.mod._one_siguiente(p, reg, "Additional Info", "additional-information")
                self.assertEqual((c.exception.paso, c.exception.buscaba, p.busquedas),
                                 ("«Next» de Additional Info en ONE", buscaba, busquedas))
        # Si el asistente no está en esa pantalla, corta sin buscar: hasta f68ce6c pulsaba el «Next» de la que hubiera.
        p = PaginaSiguiente(self.mod, [1], "booking-parties")
        with self.assertRaises(self.mod.ObjetivoNoEncontrado) as c:
            self.mod._one_siguiente(p, reg, "Container & Cargo", "container-cargo-details")
        self.assertEqual((c.exception.buscaba, p.busquedas),
                         ("la pantalla «Container & Cargo»: el asistente no está en ella", 0))

    def test_reservar_one_avanza_con_el_siguiente_identificado(self):
        # Antes de la guarda, el asistente avanza solo con _one_siguiente, en sus tres pantallas; _JS_CLICK_BTN queda
        # solo para el envío, después de la guarda, que no se toca (CICLO-cola-seis-items.md). Hasta f68ce6c los tres
        # «Next» eran _JS_CLICK_BTN.
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_one")
        g = linea_guarda(f)
        antes = [c for n in antes_de_la_guarda(f, g) for c in ast.walk(n) if isinstance(c, ast.Call)]
        self.assertEqual([[ast.unparse(a) for a in c.args[2:]] for c in antes if ast.unparse(c.func) == "_one_siguiente"],
                         [["'Booking Parties'", "'booking-parties'"], ["'Container & Cargo'", "'container-cargo-details'"],
                          ["'Additional Info'", "'additional-information'"]])
        nombres = lambda nodos: [x.id for n in nodos for x in ast.walk(n) if isinstance(x, ast.Name)]
        self.assertNotIn("_JS_CLICK_BTN", nombres(antes_de_la_guarda(f, g)))
        self.assertEqual(nombres(f.body).count("_JS_CLICK_BTN"), 1)

    def cerrar(self, botones, cierres=(), hay_dialogo=True, texto=""):
        """Corre _JS_ONE_CERRAR_MODAL sobre un diálogo falso: 'botones' y 'cierres' (íconos con aria-label o
        clase «close») son (texto, visible), y 'texto' es lo que dice el diálogo. El diálogo responde a cada parte del
        selector que se le pide."""
        guion = (
            "const el = ([t, v]) => ({textContent: t, offsetParent: v ? {} : null, clics: 0, click() { this.clics++; }});\n"
            f"const botones = {json.dumps(botones)}.map(el), cierres = {json.dumps(cierres)}.map(el);\n"
            f"const dlg = {{textContent: {json.dumps(texto)}, querySelectorAll: (s) => {{ const p = s.split(',').map(x => x.trim());\n"
            "  return [...(p.includes('button') ? botones : []),\n"
            "          ...(p.some(x => /close/.test(x)) ? cierres : [])]; }};\n"
            f"global.document = {{querySelector: () => {'dlg' if hay_dialogo else 'null'}}};\n"
            "const f = " + self.mod._JS_ONE_CERRAR_MODAL + ";\n"
            "const r = f();\n"
            "console.log(JSON.stringify([r, botones.map(b => b.clics), cierres.map(b => b.clics)]));\n")
        return correr_node(self, guion)

    def test_js_cerrar_modal_no_pulsa_a_ciegas(self):
        self.assertEqual(self.cerrar([("Guardar", True), ("Ver", True)]), ["sin-cierre", [0, 0], []])
        self.assertEqual(self.cerrar([("Guardar", True), (" Close ", True)]), ["button-close", [0, 1], []])
        self.assertEqual(self.cerrar([("Guardar", True)], [("", False), ("", True)]), ["icon-close", [0], [0, 1]])
        self.assertEqual(self.cerrar([("Guardar", False)]), [False, [0], []])            # nada visible que pulsar
        self.assertEqual(self.cerrar([], hay_dialogo=False), [False, [], []])

    def test_js_vessel_information_nunca_next(self):
        # «Vessel Information» avisa que la nave pasó su cut-off y ofrece «Next» para elegir otra: el programa no pulsa
        # nada en él (ni «Next» ni «Cancel») y la reserva corta (test_vessel_information_corta_antes_de_la_guarda).
        # Hasta a198645 lo cerraba con su primer botón y seguía: «Next» si iba antes que «Cancel», [1, 0], o si era el
        # único, [1] (CICLO-solo-la-nave-pedida.md). Ningún log.txt guardado lo trae.
        aviso = "This vessel has passed the cut-off date. Click Next to select a new vessel."
        self.assertEqual(self.cerrar([("Next", True), ("Cancel", True)], texto=aviso), ["vessel-info", [0, 0], []])
        self.assertEqual(self.cerrar([("Siguiente", True), ("Cerrar", True)], texto=aviso), ["vessel-info", [0, 0], []])
        self.assertEqual(self.cerrar([("Next", True)], texto=aviso), ["vessel-info", [0], []])

    def test_vessel_information_corta_antes_de_la_guarda(self):
        reg, _, log = self.corrida()
        pagina = soporte.PaginaFalsa(texto="vessel-info")
        with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
            self.mod._cerrar_modal_one(pagina, reg)
        self.assertEqual((e.exception.paso, e.exception.buscaba),
                         ("«Vessel Information» de ONE", "una salida de la nave con su cut-off vigente: ONE avisa que "
                                                         "la elegida lo pasó y ofrece elegir otra nave"))
        self.assertIs(self.mod._cerrar_modal_one(pagina, reg, antes_de_la_guarda=False), False)
        self.assertIn("ONE muestra «Vessel Information»: la nave pasó su cut-off y ofrece elegir otra; no pulsé nada",
                      log.read_text(encoding="utf-8"))

    def test_cerrar_modal_corta_antes_de_la_guarda_y_no_despues(self):
        reg, _, log = self.corrida()
        pagina = soporte.PaginaFalsa(texto="sin-cierre")
        with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
            self.mod._cerrar_modal_one(pagina, reg)
        self.assertEqual(e.exception.paso, "Cerrar la ventana emergente de ONE")
        self.assertIs(self.mod._cerrar_modal_one(pagina, reg, antes_de_la_guarda=False), False)
        self.assertIn("hay una ventana emergente y no encontré el botón que cierra la ventana emergente («Cancel», "
                      "«Close», «OK» o «Aceptar») ni su ícono de cierre; no pulsé nada", log.read_text(encoding="utf-8"))
        self.assertIs(self.mod._cerrar_modal_one(soporte.PaginaFalsa(texto="icon-close"), reg), True)
        self.assertIn("cerré un modal emergente (icon-close)", log.read_text(encoding="utf-8"))

    def contrato(self, textos, c="C-999"):
        guion = (
            "const el = (t) => ({textContent: t, offsetParent: {}, clics: 0, closest: () => null, "
            "click() { this.clics++; }});\n"
            f"const opts = {textos}.map(el);\n"
            "global.document = {querySelector: () => null, querySelectorAll: () => opts};\n"
            "const f = " + self.mod._JS_ONE_ELEGIR_CONTRATO + ";\n"
            f"console.log(JSON.stringify([f('{c}'), opts.map(o => o.clics)]));\n")
        return correr_node(self, guion)

    def test_js_contrato_no_elige_el_primero(self):
        self.assertEqual(self.contrato(["CONTRATO UNO", "CONTRATO DOS"]), ["sin-contrato", [0, 0]])
        self.assertEqual(self.contrato(["CONTRATO UNO", "Otros contratos"]), ["otros", [0, 1]])
        self.assertEqual(self.contrato(["c-999 · prueba", "Otros contratos"]), ["match", [1, 0]])

    def pagina_contrato(self, eleccion, campos):
        """Página falsa del contrato: abre el desplegable, elige 'eleccion' y tiene 'campos' contractNo."""
        pagina = soporte.PaginaFalsa(texto=lambda js, *a: eleccion if "sin-contrato" in js else True)
        escritos = []

        class Campo:
            first = property(lambda s: s)

            def count(s):
                return campos

            def click(s, timeout=None):
                escritos.append("clic")

            def fill(s, v, timeout=None):
                escritos.append(v)
        pagina.locator = lambda sel: Campo() if sel == 'input[name="contractNo"]' else self.fail(sel)
        pagina.keyboard = types.SimpleNamespace(press=lambda k: escritos.append(k))
        return pagina, escritos

    def test_contrato_sin_objetivo_corta(self):
        reg, _, log = self.corrida()
        for eleccion, campos, buscaba in (
                ("sin-contrato", 1, "el contrato «C-999» ni «Otros contratos» en la lista"),
                ("otros", 0, "el campo del contrato (name «contractNo») junto a «Otros contratos»")):
            with self.subTest(eleccion=eleccion):
                pagina, escritos = self.pagina_contrato(eleccion, campos)
                with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
                    self.mod._set_contract(pagina, "C-999", reg)
                self.assertEqual((e.exception.paso, e.exception.buscaba, escritos), ("Contrato de ONE", buscaba, []))
        pagina, escritos = self.pagina_contrato("otros", 1)
        self.mod._set_contract(pagina, "C-999", reg)
        self.assertEqual(escritos, ["clic", "C-999", "Tab"])
        self.assertIn("contrato ONE: escrito 'C-999' en Otros Contratos ✓", log.read_text(encoding="utf-8"))

    def test_autocompletar_sin_sugerencia_no_elige_con_el_teclado(self):
        # Hasta fb63271 elegía con el teclado (flecha abajo y Enter) la sugerencia que quedara primera. 0 veces en los
        # logs medidos (CICLO-cola-nueve-items.md).
        reg, _, log = self.corrida()
        hechos = []
        pagina = soporte.PaginaFalsa(texto=lambda js, *a: False if js == self.mod._JS_ONE_CERRAR_MODAL
                                     else "CLICK[] CANDS[]")
        pagina.locator = lambda sel: CampoFalso(hechos)
        pagina.keyboard = types.SimpleNamespace(press=hechos.append)
        with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
            self.mod._fill_port(pagina, "input[placeholder*='Origin' i]", "LIRQUEN, CHILE", reg, "Origen")
        self.assertEqual((e.exception.paso, e.exception.buscaba),
                         ("Origen de ONE", "la sugerencia «LIRQUEN» en la lista del autocompletado"))
        self.assertEqual(hechos, ["clic", "LIRQUEN"])
        self.assertIn("Origen ('LIRQUEN'): sin sugerencia | CLICK[] CANDS[]", log.read_text(encoding="utf-8"))

    def test_detenida_deja_captura_y_html_sin_esperar(self):
        reg, vistas, log = self.corrida()
        pagina = soporte.PaginaFalsa(texto=lambda js, *a: {"html": "<body>itinerarios sinteticos</body>", "sombras": 0}
                                     if js == self.mod._JS_HTML_COMPLETO else self.fail("JavaScript inesperado"))
        self.assertIsNone(self.mod._one_detenida(pagina, reg, 5))
        self.assertEqual((pagina.capturas, pagina.esperas), ([("one_f5_detenida.png", False)], 0))
        self.assertTrue((log.parent / "one_f5_detenida.html").exists())
        for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):
            self.assertIn("evidencia donde se detuvo: one_f5_detenida.png y 1 de 1 HTML (la página y 0 marco(s); 0 sin "
                          "raíces shadow)", donde)

    def test_cada_revisar_deja_la_evidencia_donde_se_detuvo(self):
        # Medido en la corrida del 2026-09-24: la fila 5 terminó en REVISAR sin HTML, porque la evidencia de la guarda
        # va dentro de «si llegó a Review Booking».
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_one")
        primeras = [ast.unparse(cuerpo[0]) for n in ast.walk(f) for cuerpo in (getattr(n, "body", None),
                                                                              getattr(n, "orelse", None))
                    if isinstance(cuerpo, list) and any(isinstance(s, ast.Return) and s.value is not None and
                                                        ast.unparse(s.value).startswith("('REVISAR'") for s in cuerpo)]
        self.assertEqual(primeras, ["_one_detenida(page, reg, f)"] * 2)

    # --- La espera de los itinerarios (CICLO-cola-cuatro-items.md) ---
    VIEJO = "mag-card, [class*=schedule], [class*=result], [data-booking-step]"

    def resultados(self, elementos, nombre):
        reg, vistas, log = self.corrida(nombre)
        pagina = PaginaOneResultados(elementos)
        r = self.mod._one_esperar_resultados(pagina, reg)
        return r, pagina, log.read_text(encoding="utf-8"), "\n".join(vistas)

    def test_la_espera_mira_las_tarjetas_y_no_la_lista_del_autocompletado(self):
        pagina = PaginaOneResultados(ONE_MEDIDO)
        # Con el selector de hasta e16beb6, el primero que calza es la lista vacía del autocompletado: vencía siempre.
        self.assertEqual(pagina.todos(self.VIEJO)[0][:2], ("ul", "SearchMenu_search-menu-result__zTdgw"))
        with self.assertRaises(TimeoutError):
            pagina.wait_for_selector(self.VIEJO)
        # Con las tarjetas, llega.
        r, pagina, log, pantalla = self.resultados(ONE_MEDIDO, "corrida_one_medido")
        self.assertIs(r, True)
        self.assertEqual(pagina.selectores, ["[class*='ResultCard_card']"])
        for donde in (log, pantalla):
            self.assertIn("itinerarios: 32 tarjeta(s) a la vista", donde)
            self.assertNotIn("⚠", donde)

    def test_si_la_espera_vence_dice_lo_que_paso(self):
        sin = [e for e in ONE_MEDIDO if "ResultCard" not in e[1]]
        ocultas = sin + [("div", "ResultCard_card__VrwST", (), False)] * 3
        casos = ((sin, "no apareció ninguna tarjeta de itinerario. Busco la nave igual."),
                 (ocultas, "llegaron 3 tarjeta(s) de itinerario, pero la primera no se ve. Busco la nave igual."))
        for elementos, aviso in casos:
            with self.subTest(aviso=aviso):
                r, _, log, pantalla = self.resultados(elementos, f"corrida_one_{len(elementos)}")
                self.assertIs(r, False)
                for donde in (log, pantalla):
                    self.assertRegex(donde, r"· ⚠ ONE: en \d+ s " + re.escape(aviso))
                    self.assertNotIn("sin señal", donde)

    def test_reservar_one_espera_las_tarjetas(self):
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_one")
        llamadas = [ast.unparse(c) for c in ast.walk(f)
                    if isinstance(c, ast.Call) and getattr(c.func, "id", "") == "_one_esperar_resultados"]
        self.assertEqual(llamadas, ["_one_esperar_resultados(page, reg)"])
        self.assertNotIn("[class*=result]", ast.unparse(f))
        self.assertEqual(self.mod._ONE_TARJETAS, "[class*='ResultCard_card']")

    def test_login_espera_la_direccion_de_hoy(self):
        # Después del login, ONE vuelve a www.one-line.com/one-ecom/…: así terminaron los 4 logins nuevos de logs/, del
        # 2026-09-24 al 26 (CICLO-cierre-de-frenos.md). Hasta 4948e16 esperaba ecomm.one-line.com/one-ecom, que ya no
        # aparece: la espera vencía siempre a los 25 s.
        glob = self.mod.ONE_TRAS_LOGIN
        self.assertFalse(set(glob) & set("?[]{}"), "el patrón usa solo * y **")
        rx = re.compile("^" + "".join(".*" if p == "**" else "[^/]*" if p == "*" else re.escape(p)
                                      for p in re.split(r"(\*\*|\*)", glob)) + "$")
        for url, calza in (("https://www.one-line.com/one-ecom/booking/quick-booking?step=search-schedule", True),
                           ("https://www.one-line.com/one-ecom/home", True),
                           ("https://auth.one-line.com/login?client_id=x", False),                # el login
                           ("https://ecomm.one-line.com/one-ecom/booking/quick-booking", False),  # la de hasta 4948e16
                           ("https://www.one-line.com/en", False)):
            with self.subTest(url=url):
                self.assertIs(bool(rx.match(url)), calza)
        # login_one la espera 25 s, como antes, y si vence lo anota y decide por la dirección.
        for vence in (False, True):
            with self.subTest(vence=vence):
                reg, _, log = self.corrida(f"one_login_{vence}")
                pagina = PaginaLoginOne(vence)
                with mock.patch.multiple(self.mod, rellenar=lambda *a, **k: True, click_si_existe=lambda *a, **k: True,
                                         esperar=lambda *a, **k: None):
                    self.assertIs(self.mod.login_one(pagina, {"usuario": "u", "clave": "c"}, reg), True)
                self.assertEqual(pagina.esperas_url, [(glob, 25000)])
                self.assertIs("no confirmé redirect en 25s" in log.read_text(encoding="utf-8"), vence)

    # --- La próxima salida (CICLO-proxima-salida.md): la tarjeta medida en one_f5_detenida.html del 2026-09-25 ---
    DOM_ONE = r"""
const nodo = (tag, cls, texto, hijos = []) => {
  const n = {tagName: tag.toUpperCase(), className: cls, texto, hijos, parentElement: null, clics: 0};
  Object.defineProperty(n, 'children', {get() { return this.hijos; }});
  Object.defineProperty(n, 'textContent', {get() { return [this.texto, ...this.hijos.map(h => h.textContent)].join(''); }});
  const calza = (e, sel) => sel.split(',').map(s => s.trim()).some(s => {
    const m = s.match(/^\[class\*=['"]?([^'"\]]+)['"]?\]$/);
    return m ? (e.className || '').includes(m[1]) : s === e.tagName.toLowerCase();
  });
  n.querySelectorAll = function (sel) {
    const out = []; const walk = (x) => { for (const h of x.hijos) { if (calza(h, sel)) out.push(h); walk(h); } };
    walk(this); return out; };
  n.querySelector = function (sel) { return this.querySelectorAll(sel)[0] || null; };
  n.click = function () { this.clics++; };
  n.scrollIntoView = function () {};
  hijos.forEach(h => { h.parentElement = n; });
  return n;
};
const p = (cls, t) => nodo('p', cls, t);
// Si es directa, como en las 128 tarjetas medidas (25 y 27-09): un div TransshipmentInfo_transshipment-container con un p
// que dice «Direct» o «Transshipment». 'tipo' es ese texto, una lista de textos (un div por cada uno) o nada (sin el div).
const tipos = (tipo) => (tipo === undefined ? [] : [].concat(tipo)).map(x =>
  nodo('div', 'TransshipmentInfo_transshipment-container__3isep', '', [p('mag-text__base mag-textStyle-body2', x)]));
const tarjeta = (salida, llegada, nave, botones = ['BOOK NOW'], tipo) => nodo('div', 'ResultCard_card__VrwST', '', [
  nodo('div', 'ResultCard_schedule__a1', '', [p('mag-text mag-textStyle-body', 'Coronel'),
    p('mag-text mag-textStyle-h5 t', salida), nodo('span', '', '40 day(s)'), ...tipos(tipo),
    p('mag-text mag-textStyle-body', 'Shanghai'), p('mag-text mag-textStyle-h5 t', llegada)]),
  nodo('div', 'VesselServiceInfo_info__b2', '', [
    nodo('div', 'VesselServiceInfo_info-item-label__c3', 'Vessel Voyage / Service Name'),
    nodo('div', '', '', [nodo('a', 'mag-text', nave), p('', '/'), nodo('a', 'mag-text', 'AS1')]),
    p('', 'Port Cut-off'), p('mag-text mag-textStyle-body', salida + ' 12:00')]),
  nodo('div', 'ResultCard_action-buttons-wrapper__d4', '',
       botones.map(b => nodo('button', '', '', [nodo('div', 'mag-button', b)])))]);
const pagina = (tarjetas, dialogo) => {
  const body = nodo('body', '', '', [nodo('ul', 'SearchMenu_search-menu-result__zTdgw', ''),
                                     nodo('div', 'SearchSchedule_list', '', tarjetas)].concat(dialogo ? [dialogo] : []));
  global.document = {querySelectorAll: (s) => body.querySelectorAll(s), querySelector: (s) => body.querySelector(s)};
  return body;
};
"""

    def test_js_tarjetas_de_la_nave_con_su_salida(self):
        guion = self.DOM_ONE + "const f = " + self.mod._JS_ONE_TARJETAS_NAVE + r""";
pagina([tarjeta('2026-10-03', '2026-11-12', 'ONE NAVE UNO SC001E'), tarjeta('2026-10-05', '2026-11-14', 'ONE NAVE DOS SC002E'),
        tarjeta('2026-10-03', '2026-11-20', 'ONE NAVE UNO SC001E'), tarjeta('2026-10-24', '2026-12-01', 'ONE NAVE UNO SC009E'),
        tarjeta('2026-10-10', '2026-11-30', 'ONE NAVE UNO SC005E', [])]);
const r = [f('ONE NAVE UNO SC001E'), f('ONE NAVE TRES SC007E'), f('SC002E'), f('ONE NAVE UNO'), f('ONE NAVE CUATRO'),
  f('XX SC001E'), f('A'), f('ONE NAVE UNO/SC001E'), f('ONE CORONEL'), f('one nave uno sc001e')];
pagina([tarjeta('2026-10-03', '2026-11-12', 'One Nave Uno SC001E')]);
r.push(f('ONE NAVE UNO SC001E'));
pagina([tarjeta('2026-10-03', '', 'ONE NAVE UNO SC001E')]);
r.push(f('ONE NAVE UNO SC001E'));
const tres_fechas = tarjeta('2026-10-03', '2026-11-12', 'ONE NAVE UNO SC001E');
tres_fechas.hijos[0].hijos.push(p('mag-text mag-textStyle-h5 t', '2026-10-20'));
pagina([tres_fechas]);
r.push(f('ONE NAVE UNO SC001E'));
pagina([tarjeta('2026-10-03', '2026-11-12', 'ONE NAVE SAVANNAH SC001E')]);
console.log(JSON.stringify(r.concat([f('ONE NAVE ANNA'), f('ONE NAVE SAVANNAH SC001'), f('ONE NAVE SAVANNAH SC001E')])));
"""
        (uno, tres, dos, sin_viaje, cuatro, viaje_solo, corta, con_barra, puerto, minusculas,
         enlace_mixto, sin_llegada, con_tres_fechas, parte_de_otra, viaje_corto, entera) = correr_node(self, guion)
        # Cada tarjeta, con su llegada (la segunda fecha textStyle-h5) para el tiempo de tránsito: hasta 2825153 no la traía
        # (CICLO-cola-tres-items.md).
        llegada = {0: "2026-11-12", 1: "2026-11-14", 2: "2026-11-20", 3: "2026-12-01", 4: "2026-11-30"}
        t = lambda i, salida, nave, botones=1: {"i": i, "calza": True, "salida": salida, "nave": nave,
                                                "llegada": llegada[i], "botones": botones, "directa": None}
        # Calza solo la tarjeta cuyo enlace de la nave trae todas las palabras de la de la fila (CICLO-cola-tres-items.md).
        # Hasta 9051f43 también calzaba sin la última palabra o con esa palabra sola, que se tomaba por el viaje: el mismo
        # barco con otro viaje (3 y 4) calzaba con «ONE NAVE UNO SC001E».
        self.assertEqual(uno, [t(0, "2026-10-03", "ONE NAVE UNO SC001E"), t(2, "2026-10-03", "ONE NAVE UNO SC001E")])
        self.assertEqual(tres, [])
        self.assertEqual(dos, [t(1, "2026-10-05", "ONE NAVE DOS SC002E")])
        # La fila sin viaje calza con cada viaje de ese barco, también el sin botón (la 4), que reservar_one descarta.
        self.assertEqual(sin_viaje, [t(0, "2026-10-03", "ONE NAVE UNO SC001E"), t(2, "2026-10-03", "ONE NAVE UNO SC001E"),
                                     t(3, "2026-10-24", "ONE NAVE UNO SC009E"), t(4, "2026-10-10", "ONE NAVE UNO SC005E", 0)])
        # Hasta 9051f43 calzaban: «ONE NAVE CUATRO» y «A» con las cinco, por la primera parte de la nave o por una letra, y
        # «XX SC001E» con la 0 y la 2, por el viaje solo.
        self.assertEqual((cuatro, viaje_solo, corta), ([], [], []))
        # La barra separa palabras, como en MSC: hasta 9051f43 esa nave no calzaba con ninguna.
        self.assertEqual(con_barra, [t(0, "2026-10-03", "ONE NAVE UNO SC001E"), t(2, "2026-10-03", "ONE NAVE UNO SC001E")])
        # Un puerto de la tarjeta no es su nave: se compara con el enlace de la nave, no con toda la tarjeta.
        self.assertEqual(puerto, [])
        # Sin distinguir mayúsculas, ni en la planilla ni en el enlace.
        self.assertEqual(minusculas, uno)
        self.assertEqual(enlace_mixto, [t(0, "2026-10-03", "One Nave Uno SC001E")])
        # Sin exactamente dos fechas, sin llegada: con una sola, o con tres (¿cuál sería la llegada?).
        self.assertEqual(sin_llegada, [dict(t(0, "2026-10-03", "ONE NAVE UNO SC001E"), llegada="")])
        self.assertEqual(con_tres_fechas, [dict(t(0, "2026-10-03", "ONE NAVE UNO SC001E"), llegada="")])
        # Cada palabra, entera (CICLO-cola-seis-items.md): «ANNA» no calza dentro de «SAVANNAH», ni «SC001» dentro de
        # «SC001E». Hasta f68ce6c las dos calzaban con esa tarjeta.
        self.assertEqual((parte_de_otra, viaje_corto), ([], []))
        self.assertEqual(entera, [t(0, "2026-10-03", "ONE NAVE SAVANNAH SC001E")])

    def test_js_clic_solo_el_boton_de_la_tarjeta_elegida(self):
        guion = self.DOM_ONE + "const f = " + self.mod._JS_ONE_CLIC_TARJETA + r""";
const NAVE = 'ONE NAVE UNO SC001E';
const correr = (tarjetas, i, dialogo, eleg = {}) => {
  const body = pagina(tarjetas, dialogo);
  const r = f(Object.assign({i, nave: NAVE, salida: '2026-10-03', directa: null}, eleg));
  return [r, body.querySelectorAll('button').map(b => b.clics)];
};
const a = () => tarjeta('2026-10-03', '2026-11-12', NAVE);
const d = (tipo) => tarjeta('2026-10-03', '2026-11-12', NAVE, ['BOOK NOW'], tipo);
console.log(JSON.stringify([
  correr([a(), a()], 1),
  correr([a()], 3),
  correr([tarjeta('2026-10-03', '2026-11-12', NAVE, ['BOOK NOW', 'SELECT'])], 0),
  correr([tarjeta('2026-10-03', '2026-11-12', NAVE, [])], 0),
  correr([a()], 0, nodo('div', 'x dialog__overlay', '', [nodo('button', '', 'Cancel')])),
  correr([a()], 0, nodo('div', 'x dialog__overlay', '', [nodo('button', '', 'Next')])),
  correr([a()], 0, nodo('div', 'x dialog__overlay', '', [nodo('button', '', 'Siguiente')])),
  // Vuelve a leer la tarjeta i: la directa elegida, sí; si es con transbordo, si sale otro día o si es de otra nave, no.
  correr([d('Transshipment'), d('Direct')], 1, null, {directa: true}),
  correr([d('Transshipment'), d('Direct')], 0, null, {directa: true}),
  correr([a()], 0, null, {salida: '2026-10-04'}),
  correr([a()], 0, null, {nave: 'ONE NAVE DOS SC002E'}),
]));
"""
        nada = lambda n: [False, [0] * n]
        self.assertEqual(correr_node(self, guion), [
            [True, [0, 1]],             # la tarjeta elegida, no la primera
            [False, [0]],               # no existe: nada
            [False, [0, 0]],            # dos botones de reserva: no pulsa ninguno
            [False, []],                # sin botón: nada
            [True, [1, 1]],             # cierra el diálogo que tapa la lista, como antes, y pulsa
            # Nunca «Next», que en «Vessel Information» lleva a elegir otra nave: pulsa solo el de la tarjeta (el primero de
            # la lista). Hasta a198645 pulsaba los dos, [True, [1, 1]] (CICLO-solo-la-nave-pedida.md).
            [True, [1, 0]],
            [True, [1, 0]],
            # Hasta el encargo 34 pulsaba la i-ésima sin volver a leerla: [True, [1, 0]] y [True, [1]] en las tres de abajo
            # (CICLO-one-y-maersk-eligen-la-nave.md).
            [True, [0, 1]], nada(2), nada(1), nada(1)])

    def test_js_directa_o_con_transbordo(self):
        # Si la salida es directa: el único TransshipmentInfo_transshipment-container de la tarjeta, «Direct» o
        # «Transshipment», medido en las 128 tarjetas de las 4 listas guardadas (25 y 27-09). Sin uno solo, o con otro
        # texto, no se sabe (null), como en HYUNDAI (CICLO-one-y-maersk-eligen-la-nave.md).
        guion = self.DOM_ONE + "const f = " + self.mod._JS_ONE_TARJETAS_NAVE + r""";
pagina(['Direct', 'Transshipment', ' direct ', undefined, ['Direct', 'Transshipment'], 'Indirect'].map(
  (tipo, k) => tarjeta('2026-10-0' + (k + 1), '2026-11-12', 'ONE NAVE UNO SC001E', ['BOOK NOW'], tipo)));
console.log(JSON.stringify(f('ONE NAVE UNO SC001E').map(x => x.directa)));
"""
        self.assertEqual(correr_node(self, guion), [True, False, True, None, None, None])

    def test_prefiere_la_directa(self):
        # Entre las salidas del mismo día, la directa; solo si ninguna lo es (o todas), el tránsito: la regla de HYUNDAI,
        # decisión de Marcelo para ONE (CICLO-one-y-maersk-eligen-la-nave.md). Medido en las 4 listas guardadas: cada nave
        # trae 4 salidas del mismo día y una sola directa. En 8 de las 32, la directa y una con transbordo empataban en el
        # menor tránsito, y la reserva quedaba NO ENVIADA; en 6, una con transbordo llegaba 1 día antes y se elegía esa.
        hoy = datetime.date.today()
        dia = lambda n: (hoy + datetime.timedelta(days=n)).isoformat()
        t = lambda i, transito, directa, n=22: {"i": i, "nave": "ONE NAVE PRUEBA SC001E", "salida": dia(n),
                                                "llegada": dia(n + transito), "botones": 1, "directa": directa}
        mod = self.mod

        def elige(tarjetas):
            reg, _, log = self.corrida(f"one_directa_{len(self._logs)}")
            self._logs.append(log)
            quedan = mod._directas_primero(tarjetas, hoy, reg, mod._one_salidas)
            elegida, _ = mod._proxima_salida(mod._one_salidas(quedan), hoy, mod._one_transito)
            return (elegida or {}).get("i"), log.read_text(encoding="utf-8")

        self._logs = []
        # El empate medido: 38 días la directa y una con transbordo, y dos más largas. Hasta el encargo 34, NO ENVIADA.
        i, log = elige([t(0, 38, False), t(1, 38, True), t(2, 51, False), t(3, 56, False)])
        self.assertEqual(i, 1)
        self.assertIn(f"4 salidas de la nave salen el {hoy + datetime.timedelta(days=22):%d-%m-%Y}: prefiero la directa; "
                      "descarto 3 con transbordo", log)
        # La con transbordo llega 1 día antes: igual la directa. Hasta el encargo 34, la con transbordo.
        self.assertEqual(elige([t(0, 39, False), t(1, 40, True)])[0], 1)
        # Todas con transbordo: el tránsito, como antes, sin descartar nada.
        i, log = elige([t(0, 40, False), t(1, 38, False)])
        self.assertEqual(i, 1)
        self.assertNotIn("prefiero", log)
        # La que no dice si es directa cuenta como con transbordo.
        self.assertEqual(elige([t(0, 38, None), t(1, 40, True)])[0], 1)
        # La directa solo desempata el mismo día: la con transbordo que sale antes gana.
        self.assertEqual(elige([t(0, 38, False, n=10), t(1, 38, True)])[0], 0)

    def test_salidas_de_las_tarjetas(self):
        r = self.mod._one_salidas([{"salida": "2026-10-03"}, {"salida": ""}, {"salida": "2026-13-45"}, {}])
        self.assertEqual([d for d, _ in r], [datetime.date(2026, 10, 3), None, None, None])

    def test_transito_y_desempate(self):
        # El tiempo de tránsito de la tarjeta es su llegada menos su salida: en las 32 tarjetas medidas, el «N day(s)» que
        # muestra (CICLO-cola-tres-items.md).
        f = self.mod._one_transito
        self.assertEqual(f({"salida": "2026-10-03", "llegada": "2026-11-12"}), datetime.timedelta(days=40))
        for x in ({"salida": "2026-10-03", "llegada": ""}, {"salida": "2026-10-03"}, {"llegada": "2026-11-12"},
                  {"salida": "2026-10-03", "llegada": "2026-10-03"}, {"salida": "2026-10-03", "llegada": "2026-09-30"}):
            with self.subTest(tarjeta=x):
                self.assertIsNone(f(x))
        # Dos tarjetas de la nave que salen el mismo día, con 48 y 40 días: la de 40. Hasta 2825153, empate.
        hoy = datetime.date.today()
        dia = lambda n: (hoy + datetime.timedelta(days=n)).isoformat()
        a, b = {"i": 0, "salida": dia(8), "llegada": dia(56)}, {"i": 2, "salida": dia(8), "llegada": dia(48)}
        self.assertIs(self.mod._proxima_salida(self.mod._one_salidas([a, b]), hoy, f)[0], b)

    def test_sin_una_salida_queda_no_enviada_con_evidencia(self):
        hoy = datetime.date.today()
        ocho = hoy + datetime.timedelta(days=8)
        tarjetas = [{"i": 0, "nave": "ONE NAVE PRUEBA SC001E", "salida": ocho.isoformat(), "botones": 1},
                    {"i": 2, "nave": "ONE NAVE PRUEBA SC001E", "salida": ocho.isoformat(), "botones": 1}]
        reg, vistas, log = self.corrida("one_sin_una")
        pagina = soporte.PaginaFalsa(texto=lambda js, *a: {"html": "<body>tarjetas sinteticas</body>", "sombras": 0}
                                     if js == self.mod._JS_HTML_COMPLETO else self.fail("JavaScript inesperado"))
        reserva = {"fila": 5, "nave": "ONE NAVE PRUEBA SC001E"}
        # Hasta 2825153 el motivo terminaba en «…la próxima salida desde el …»; ahora dice también por qué el tiempo de
        # tránsito no desempató: estas tarjetas sintéticas no lo traen (CICLO-cola-tres-items.md).
        detalle = (f"ONE: no elegí salida para esa nave ('ONE NAVE PRUEBA SC001E'): 2 de las 2 opciones salen el "
                   f"{ocho:%d-%m-%Y}, la próxima salida desde el {hoy:%d-%m-%Y}, y no pude leer el tiempo de tránsito de "
                   "2 de ellas. Revisa la fila y elige la salida en el portal.")
        self.assertEqual(self.mod._one_sin_una_salida(pagina, reg, reserva, tarjetas, "empate", hoy),
                         ("NO ENVIADA", detalle))
        self.assertEqual((pagina.capturas, pagina.esperas), ([("one_f5_detenida.png", False)], 0))
        self.assertTrue((log.parent / "one_f5_detenida.html").exists())
        for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):
            self.assertIn(f"· ✗ NO ENVIADA · {detalle}", donde)
            self.assertIn(f"tarjetas que calzan: ONE NAVE PRUEBA SC001E sale {ocho.isoformat()} | ONE NAVE PRUEBA SC001E "
                          f"sale {ocho.isoformat()}", donde)

    def test_sin_una_salida_con_el_mismo_tiempo_de_transito(self):
        hoy = datetime.date.today()
        ocho, llega = hoy + datetime.timedelta(days=8), hoy + datetime.timedelta(days=48)
        tarjetas = [{"i": i, "nave": "ONE NAVE PRUEBA SC001E", "salida": ocho.isoformat(), "llegada": llega.isoformat(),
                     "botones": 1} for i in (0, 2)]
        reg, _, _ = self.corrida("one_mismo_transito")
        pagina = soporte.PaginaFalsa(texto=lambda js, *a: {"html": "<body>tarjetas sinteticas</body>", "sombras": 0})
        r = self.mod._one_sin_una_salida(pagina, reg, {"fila": 5, "nave": "ONE NAVE PRUEBA SC001E"}, tarjetas, "empate",
                                         hoy)
        self.assertEqual(r, ("NO ENVIADA", f"ONE: no elegí salida para esa nave ('ONE NAVE PRUEBA SC001E'): 2 de las 2 "
                                           f"opciones salen el {ocho:%d-%m-%Y}, la próxima salida desde el {hoy:%d-%m-%Y}, y "
                                           "2 de ellas tienen el menor tiempo de tránsito, 40 días. Revisa la fila y elige la "
                                           "salida en el portal."))

    def test_reservar_one_no_amplia(self):
        # ONE busca solo las 8 semanas que pide la nota de la planilla, y no amplía (decisión de Marcelo,
        # CICLO-ampliar-msc-y-cma.md): si la nave no está, el REVISAR dice hasta qué fecha buscó. Entre 05cfdb7 y el
        # encargo 33 abría el selector «N weeks» y probaba una opción más larga (CICLO-ampliar-la-busqueda.md).
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_one")
        self.assertEqual([ast.unparse(n.test) for n in ast.walk(f) if isinstance(n, ast.If)
                          and ast.unparse(n.test) == "not tarjetas"], [])
        for nombre in ("_one_ampliar", "_one_semanas", "_JS_ONE_SEMANAS", "_one_esperar_mas"):
            self.assertFalse(hasattr(self.mod, nombre), nombre)
        asignas = {}
        for n in ast.walk(f):
            if isinstance(n, ast.Assign):
                asignas.setdefault(ast.unparse(n), []).append(n.lineno)
        self.assertEqual(len(asignas["tarjetas = _one_tarjetas(page, reg, reserva['nave'])"]), 1)
        self.assertLess(asignas["hay_nave = bool(tarjetas)"][0],
                        asignas["tarjetas = [t for t in tarjetas if t.get('botones') == 1]"][0])
        self.assertIn("donde = '' if hay_nave else f': {_hasta_donde_busque(_one_fechas(page), ONE_SOLO_8)}'", asignas)
        self.assertEqual(self.mod.ONE_SOLO_8, "no amplío más allá de las 8 semanas que pide la nota de la planilla")
        self.assertEqual(self.mod._hasta_donde_busque([datetime.date(2026, 11, 20)], self.mod.ONE_SOLO_8),
                         "busqué hasta el 20-11-2026, la última salida que mostró el portal, y no amplío más allá de las "
                         "8 semanas que pide la nota de la planilla")

    def test_fechas_de_todas_las_tarjetas(self):
        # Hasta qué fecha buscó: la salida de cada tarjeta, calce o no con la nave (CICLO-ampliar-la-busqueda.md).
        guion = self.DOM_ONE + "const f = " + self.mod._JS_ONE_FECHAS + r""";
pagina([tarjeta('2026-10-03', '2026-11-12', 'ONE NAVE UNO SC001E'), tarjeta('2026-10-24', '2026-12-01', 'ONE OTRA SC002E'),
        tarjeta('', '', 'ONE NAVE TRES SC003E')]);
console.log(JSON.stringify(f()));
"""
        self.assertEqual(correr_node(self, guion), ["2026-10-03", "2026-10-24", ""])
        pagina = soporte.PaginaFalsa(texto=lambda js, *a: ["2026-10-03", "", "2026-10-24", "3 Oct"]
                                     if js == self.mod._JS_ONE_FECHAS else None)
        d = datetime.date
        self.assertEqual(self.mod._one_fechas(pagina), [d(2026, 10, 3), None, d(2026, 10, 24), None])

    def test_reservar_one_elige_la_proxima_salida(self):
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_one")
        asignas = [ast.unparse(n) for n in ast.walk(f) if isinstance(n, ast.Assign)]
        for forma in ("tarjetas = _one_tarjetas(page, reg, reserva['nave'])",
                      "tarjetas = [t for t in tarjetas if t.get('botones') == 1]",
                      # Hasta fc7de54, «desde = datetime.date.today()»: ONE no usaba el día de carga de la fila.
                      "desde = _desde(reserva)",
                      # Hasta 2825153, sin _one_transito: el empate del mismo día no se desempataba.
                      "elegida, motivo = _proxima_salida(_one_salidas(tarjetas), desde, _one_transito) if tarjetas else "
                      "(None, '')",
                      # Hasta el encargo 34, sin la directa primero, y el clic sin volver a leer la tarjeta elegida
                      # (CICLO-one-y-maersk-eligen-la-nave.md).
                      "tarjetas = _directas_primero(tarjetas, desde, reg, _one_salidas)",
                      "seleccionada = bool(page.evaluate(_JS_ONE_CLIC_TARJETA, {'i': elegida['i'], 'nave': reserva['nave'], "
                      "'salida': elegida.get('salida', ''), 'directa': elegida.get('directa')}))"):
            self.assertIn(forma, asignas)
        lineas = {ast.unparse(n): n.lineno for n in ast.walk(f) if isinstance(n, ast.Assign)}
        orden = [lineas[x] for x in ("desde = _desde(reserva)",
                                             "tarjetas = _directas_primero(tarjetas, desde, reg, _one_salidas)",
                                             "elegida, motivo = _proxima_salida(_one_salidas(tarjetas), desde, "
                                             "_one_transito) if tarjetas else (None, '')")]
        self.assertEqual(orden, sorted(orden))
        sin_una = [n for n in ast.walk(f) if isinstance(n, ast.If) and ast.unparse(n.test) == "tarjetas and elegida is None"]
        self.assertEqual([ast.unparse(r) for n in sin_una for r in ast.walk(n) if isinstance(r, ast.Return)],
                         ["return _one_sin_una_salida(page, reg, reserva, tarjetas, motivo, desde)"])
        clic = next(n for n in ast.walk(f) if isinstance(n, ast.Call) and "_JS_ONE_CLIC_TARJETA" in ast.unparse(n))
        self.assertLess(sin_una[0].lineno, clic.lineno)
        self.assertLess(clic.lineno, linea_guarda(f))
        self.assertNotIn("_JS_ONE_SELECT_NAVE", ast.unparse(f))


# El orden medido en one_f5_detenida.html (corrida del 2026-09-25): primero la lista vacía del autocompletado de puertos,
# después el contenedor de la búsqueda, los botones del asistente y, al final, las 32 tarjetas de itinerario.
ONE_MEDIDO = ([("ul", "SearchMenu_search-menu-result__zTdgw", (), False),
               ("div", "SearchSchedule_schedule-wrapper__x62cJ", (), True),
               ("button", "mag-segmented-item__base", ("data-booking-step",), True)]
              + [("div", "ResultCard_card__VrwST", (), True)] * 32)


class PaginaSiguiente:
    """Página falsa del asistente de ONE, en el paso de su URL: a cada búsqueda de _JS_ONE_SIGUIENTE responde lo que sigue
    en 'respuestas' (cuántos «Next» había; con uno, lo pulsó; -1, uno en una ventana emergente), o levanta la excepción
    que esté ahí. A cualquier otro JavaScript (el texto de la página que mira _one_esta_en_paso) responde vacío."""

    def __init__(self, mod, respuestas, paso="booking-parties"):
        self.mod, self.respuestas, self.busquedas = mod, list(respuestas), 0
        self.url = f"https://ecommerce.one-line.invalid/booking?step={paso}"

    def evaluate(self, js, *a):
        if js != self.mod._JS_ONE_SIGUIENTE:
            return ""
        self.busquedas += 1
        r = self.respuestas.pop(0)
        if isinstance(r, Exception):
            raise r
        return r

    def wait_for_timeout(self, ms):
        pass


class PaginaOneResultados(soporte.PaginaFalsa):
    """Página falsa de ONE con sus elementos en orden de documento: (etiqueta, clases, atributos, a la vista). Como
    Playwright 1.58.0 (frames.js), wait_for_selector mira solo el PRIMER elemento que calza. Los selectores son los de
    la espera: etiquetas, [class*=x] (distingue mayúsculas, como CSS) y [atributo], separados por comas."""

    def __init__(self, elementos):
        super().__init__()
        self.elementos, self.selectores = list(elementos), []

    @staticmethod
    def calza(sel, e):
        tag, clases, atributos, _ = e
        for parte in (p.strip() for p in sel.split(",")):
            m = re.fullmatch(r"\[class\*=['\"]?([^'\"\]]+)['\"]?\]", parte)
            if m and m.group(1) in clases:
                return True
            m = re.fullmatch(r"\[([\w-]+)\]", parte)
            if m and m.group(1) in atributos:
                return True
            if re.fullmatch(r"[a-z][\w-]*", parte) and parte == tag:
                return True
        return False

    def todos(self, sel):
        return [e for e in self.elementos if self.calza(sel, e)]

    def wait_for_selector(self, sel, timeout=None, state="visible"):
        self.selectores.append(sel)
        primero = next(iter(self.todos(sel)), None)
        if primero is None or not primero[3]:
            raise TimeoutError(f"{sel}: el primero que calza no se ve")

    def locator(self, sel):
        todos = self.todos(sel)
        return types.SimpleNamespace(count=lambda: len(todos),
                                     first=types.SimpleNamespace(is_visible=lambda: bool(todos) and todos[0][3]))


class CampoFalso:
    """Campo de texto de Playwright que anota lo que se le hace."""
    first = property(lambda s: s)

    def __init__(self, hechos):
        self.hechos = hechos

    def wait_for(self, **k):
        pass

    def click(self, **k):
        self.hechos.append("clic")

    def press(self, tecla):
        self.hechos.append(tecla)

    def press_sequentially(self, v, delay=None):
        self.hechos.append(v)

    def fill(self, v, **k):
        pass

    def type(self, v, delay=None):
        self.hechos.append(v)


def pagina_con_respuestas(respuestas):
    """Página falsa cuyo evaluate devuelve cada respuesta en orden y repite la última."""
    pendientes = list(respuestas)
    pagina = soporte.PaginaFalsa(texto=lambda js, *a: pendientes.pop(0) if len(pendientes) > 1 else pendientes[0])
    hechos = []
    pagina.locator = lambda sel: CampoFalso(hechos)
    return pagina, hechos


class RespuestaFalsa:
    """Una respuesta de Playwright a un documento: su petición (método, tipo y marco), su dirección, su código y sus
    cabeceras. all_headers las trae todas; headers, sin las de cookies, como Playwright (medido sin red, encargo 50)."""

    def __init__(self, marco, metodo, url, estado, cabeceras, tipo="document"):
        self.request = types.SimpleNamespace(method=metodo, url=url, resource_type=tipo, frame=marco, failure=None)
        self.url, self.status, self.frame, self._cab = url, estado, marco, dict(cabeceras)

    def all_headers(self):
        return {k.lower(): v for k, v in self._cab.items()}

    @property
    def headers(self):
        return {k.lower(): v for k, v in self._cab.items() if k.lower() != "set-cookie"}


def falla_de_red(marco, metodo, url, tipo="document"):
    """La petición que Playwright da en «requestfailed»: tras un 502 sin cuerpo, Chrome la da por fallida con
    net::ERR_HTTP_RESPONSE_CODE_FAILURE (medido sin red, encargo 50)."""
    return types.SimpleNamespace(method=metodo, url=url, resource_type=tipo, frame=marco,
                                 failure="net::ERR_HTTP_RESPONSE_CODE_FAILURE")


class PaginaLoginMsc(soporte.PaginaFalsa):
    """El login de MSC en una página falsa: su estado decide la dirección, el texto a la vista y el campo que se ve. Cada
    acción del login (el «Next», el botón de entrar, el goto, la recarga, la pausa) puede traer un estado nuevo, que
    llega después de tantas esperas (llega). Anota cada goto. No tiene reload propio: login_falso le pone uno que anota
    cada recarga, como cada acción (encargo 47), porque _msc_recargar atrapa la falla de la recarga y una que no se
    espera no reventaría.
    Desde el encargo 50 escucha como Playwright (on y remove_listener; 'oyentes' dice quién escucha). Cuando una acción
    trae la página de error de Chrome, emite lo medido sin red: la respuesta 502 sin cuerpo, con cabeceras inventadas
    (CABECERAS), y después su falla de red. Tras el botón de entrar, la vuelta a myMSC (POST a OidcLoginCallBack, sin
    consulta); tras el «Next» o la recarga, TriggerOidcLogin (GET, con el usuario en usernameLoginHint). Su HTML (el de
    _JS_HTML_COMPLETO) es el de esa página de error: tras el GET repite la dirección entera, con el usuario; tras el
    POST, no."""
    URLS = {"portada": "https://www.mymsc.com/myMSC/",
            "clave": "https://mscciam.b2clogin.com/mscciam.onmicrosoft.com/oauth2/v2.0/authorize",
            "sesión": "https://www.mymsc.com/myMSC/welcome", "ebooking": "https://www.mymsc.com/myMSC/booking/main",
            "error_chrome": "chrome-error://chromewebdata/", "error_msc": "https://www.mymsc.com/mymsc/",
            "validador": "https://mscciam.b2clogin.com/mscciam.onmicrosoft.com/api/validar",
            "nada": "https://identityserver.msc.com/connect/authorize/callback"}
    TEXTOS = {"error_chrome": "Esta página no funciona\nwww.mymsc.com no puede procesar esta solicitud ahora.",
              "error_msc": "We are unable to complete your request at this time.",
              "validador": "Please solve the captcha to continue"}
    VUELTA = "https://www.mymsc.com/myMSC/Account/OidcLoginCallBack"
    TRIGGER = "https://www.mymsc.com/myMSC/Account/TriggerOidcLogin"
    CABECERAS = {"content-length": "0", "content-type": "text/html", "server": "PasarelaDePrueba/1.0",
                 "via": "1.1 proxy-de-prueba", "set-cookie": "sesion=VALORDECOOKIEDEPRUEBA; HttpOnly",
                 "x-azure-ref": "REFERENCIADEPRUEBA"}

    def __init__(self, estado, js_html=None, usuario=""):
        super().__init__(texto=self._leer)
        self.estado, self.pendiente, self.gotos = estado, None, []
        self.js_html, self.usuario, self.causa, self.fallida = js_html, usuario, "", ""
        self.oyentes, self.main_frame = {}, object()

    def _leer(self, js, *a):
        if js == self.js_html:
            return {"html": f"<html><body>{self.TEXTOS.get(self.estado, '')}<script>{self.fallida}</script></body>"
                            f"</html>", "sombras": 0}
        return self.TEXTOS.get(self.estado, "")

    @property
    def url(self):
        return self.URLS[self.estado]

    @url.setter
    def url(self, valor):
        pass

    def on(self, evento, oyente):
        self.oyentes.setdefault(evento, []).append(oyente)

    def remove_listener(self, evento, oyente):
        self.oyentes[evento].remove(oyente)

    def emitir(self, evento, objeto):
        for oyente in list(self.oyentes.get(evento, ())):
            oyente(objeto)

    def llega(self, estado, tras, causa=""):
        """'estado' llega después de 'tras' esperas (con 0, ya), traído por la acción 'causa'."""
        self.causa = causa
        if tras:
            self.pendiente = [tras, estado]
        else:
            self._llegar(estado)

    def avanza(self):
        if self.pendiente:
            self.pendiente[0] -= 1
            if not self.pendiente[0]:
                self._llegar(self.pendiente[1])

    def _llegar(self, estado):
        self.estado, self.pendiente = estado, None
        if estado != "error_chrome":
            return
        if self.causa == "entrar":
            metodo, url, self.fallida = "POST", self.VUELTA, ""
        else:
            metodo = "GET"
            url = self.fallida = (f"{self.TRIGGER}?option=x&returnUrl=%2FmyMSC%2Fwelcome&usernameLoginHint="
                                  f"{quote(self.usuario, safe='')}")
        self.emitir("response", RespuestaFalsa(self.main_frame, metodo, url, 502, self.CABECERAS))
        self.emitir("requestfailed", falla_de_red(self.main_frame, metodo, url))

    def locator(self, selector):
        visible = ((self.estado == "portada" and "#UserName" in selector)
                   or (self.estado == "clave" and "password" in selector))
        return types.SimpleNamespace(first=types.SimpleNamespace(is_visible=lambda *a, **k: visible))


class TestMsc(ConRegistro):
    def lista(self, js, textos, *args):
        """Corre un JavaScript de MSC sobre una lista Kendo falsa con 'textos'; devuelve lo que respondió y los
        clics de cada sugerencia."""
        guion = (
            "const el = (t) => ({textContent: t, offsetParent: {}, clics: 0, scrollIntoView() {}, "
            "click() { this.clics++; }});\n"
            f"const items = {json.dumps(textos)}.map(el);\n"
            "const lb = {querySelectorAll: () => items};\n"
            "global.document = {querySelector: (s) => /_listbox$/.test(s) ? lb : null, querySelectorAll: () => []};\n"
            "const f = " + js + ";\n"
            f"console.log(JSON.stringify([f(...{json.dumps(list(args))}), items.map(i => i.clics)]));\n")
        return correr_node(self, guion)

    def test_js_hs_elige_el_salmon_o_nada(self):
        js = self.mod._JS_MSC_HS_ELEGIR
        salmon = "030313 - FROZEN ATLANTIC SALMON (SALMO SALAR)"
        self.assertEqual(self.lista(js, ["030313 - OTRO PESCADO", salmon]), [salmon, [0, 1]])
        self.assertEqual(self.lista(js, ["030319 - OTRO", "030399 - OTRO"]), ["sin-salmon", [0, 0]])
        self.assertEqual(self.lista(js, []), ["", []])

    def test_js_kendo_elige_por_texto_o_nada(self):
        js = self.mod._JS_MSC_KENDO_ELEGIR
        self.assertEqual(self.lista(js, ["FISH", "ATLANTIC SALMON, FROZEN"], ["Commodity", "Atlantic salmon"]),
                         ["ATLANTIC SALMON, FROZEN", [0, 1]])
        self.assertEqual(self.lista(js, ["FISH", "BEEF"], ["Commodity", "Atlantic salmon"]),
                         ["sin-coincidencia", [0, 0]])
        self.assertEqual(self.lista(js, [], ["Commodity", "Atlantic salmon"]), ["", []])

    def test_hs_sin_salmon_corta(self):
        reg, _, log = self.corrida()
        pagina, _ = pagina_con_respuestas(["sin-salmon"])
        with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
            self.mod._msc_set_hscode(pagina, "030313", reg)
        self.assertEqual(e.exception.paso, "HS Code de MSC")
        # El salmón puede llegar en un sondeo posterior: no se corta antes de tiempo.
        pagina, hechos = pagina_con_respuestas(["sin-salmon", "sin-salmon", "030313 SALMON"])
        self.assertIs(self.mod._msc_set_hscode(pagina, "030313", reg), True)
        self.assertIn("HS Code '030313' seleccionado (salmón): '030313 SALMON' ✓", log.read_text(encoding="utf-8"))
        # Sin ninguna sugerencia en pantalla tampoco elige: hasta fb63271 la confirmaba con el teclado.
        pagina, hechos = pagina_con_respuestas([""])
        with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
            self.mod._msc_set_hscode(pagina, "030313", reg)
        self.assertEqual((e.exception.paso, e.exception.buscaba),
                         ("HS Code de MSC", "la sugerencia del salmón para '030313': el portal no ofreció ninguna"))
        self.assertNotIn("ArrowDown", hechos)
        self.assertNotIn("Enter", hechos)

    def test_kendo_sin_coincidencia_corta(self):
        reg, _, log = self.corrida()
        pagina, _ = pagina_con_respuestas(["sin-coincidencia"])
        with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
            self.mod._msc_kendo_autocomplete(pagina, "Commodity", "Atlantic salmon", reg, "Commodity")
        self.assertEqual((e.exception.paso, e.exception.buscaba),
                         ("Commodity de MSC", "la sugerencia que dice «Atlantic salmon» entre las que ofrece el portal"))
        pagina, _ = pagina_con_respuestas(["sin-coincidencia", "ATLANTIC SALMON, FROZEN"])
        self.assertIs(self.mod._msc_kendo_autocomplete(pagina, "Commodity", "Atlantic salmon", reg, "Commodity"), True)
        self.assertIn("Commodity 'Atlantic salmon': ATLANTIC SALMON, FROZEN", log.read_text(encoding="utf-8"))

    def test_sin_sugerencias_no_elige_con_el_teclado(self):
        # Hasta fb63271, sin sugerencias, el puerto y el Kendo elegían con el teclado (flecha abajo y Enter) la que
        # quedara primera. 0 veces en los logs medidos (CICLO-cola-nueve-items.md).
        reg, _, _ = self.corrida()
        casos = (
            (lambda p: self.mod._msc_puerto(p, "POLId_input", "SAN ANTONIO", reg, "Port of Load"),
             ("Port of Load de MSC", "la sugerencia que dice «SAN ANTONIO» entre las que ofrece el portal")),
            (lambda p: self.mod._msc_kendo_autocomplete(p, "Commodity", "Atlantic salmon", reg, "Commodity"),
             ("Commodity de MSC", "la sugerencia que dice «Atlantic salmon»: el portal no ofreció ninguna")),
        )
        for llamar, esperado in casos:
            with self.subTest(paso=esperado[0]):
                pagina, hechos = pagina_con_respuestas([""])
                with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
                    llamar(pagina)
                self.assertEqual((e.exception.paso, e.exception.buscaba), esperado)
                self.assertNotIn("ArrowDown", hechos)
                self.assertNotIn("Enter", hechos)

    MESES = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")

    @classmethod
    def etd(cls, n):
        """La ETD a n días de hoy, como la lee _JS_MSC_NAVES: «27 SEP 2026» (los meses a mano: %b depende del locale)."""
        d = datetime.date.today() + datetime.timedelta(days=n)
        return f"{d.day:02d} {cls.MESES[d.month - 1]} {d.year}"

    def test_salida_la_proxima_nunca_la_primera(self):
        # Decisión de Marcelo (CICLO-proxima-salida.md): de las tarjetas con la nave de la fila, la próxima salida desde
        # hoy. Hasta 384d3ce tomaba la primera que calzaba, y buscaba desde hoy + 18 días.
        hoy = datetime.date.today()
        a, b, c = ({"i": 3, "nave": "NAVE UNO 001E", "etd": self.etd(20)}, {"i": 7, "nave": "NAVE UNO 002E", "etd": self.etd(6)},
                   {"i": 9, "nave": "NAVE UNO 002E", "etd": self.etd(6)})
        pasada, sin = {"i": 1, "nave": "NAVE UNO 000E", "etd": self.etd(-4)}, {"i": 2, "nave": "NAVE UNO", "etd": ""}
        casos = (([a], hoy, (a, "")), ([sin], hoy, (sin, "")), ([a, b], hoy, (b, "")), ([pasada, a], hoy, (a, "")),
                 ([pasada], hoy, (None, "ninguna")), ([b, c], hoy, (None, "empate")), ([a, sin], hoy, (None, "sin-fecha")),
                 ([a, b], hoy + datetime.timedelta(days=10), (a, "")))
        for exacta, desde, (elegida, motivo) in casos:
            with self.subTest(tarjetas=[x["i"] for x in exacta], desde=desde):
                r = self.mod._msc_elegir_salida(exacta, desde)
                self.assertEqual(r[1], motivo)
                self.assertIs(r[0], elegida)

    def test_js_naves_lee_la_etd_y_la_eta(self):
        # La tarjeta como la lee _JS_MSC_NAVES: su texto, con «Vessel / Voyage», «ETD», «ETA» y «Est T.T» como en las 27
        # tarjetas medidas el 2026-09-25, y su botón «Select». Hasta 2825153 no leía la ETA (CICLO-cola-tres-items.md).
        guion = "const f = " + self.mod._JS_MSC_NAVES + r""";
const tarjeta = (texto, visible) => ({textContent: texto,
  querySelectorAll: () => [{textContent: ' Select ', offsetParent: visible ? {} : null}]});
const tarjetas = [
  tarjeta('Vessel / Voyage MSC NAVE UNO / FA001E ETD 03 Oct 2026 12:00 ETA 12 Nov 2026 06:00 Service ANDES Est T.T 40', true),
  tarjeta('Vessel / Voyage MSC NAVE DOS / FA002E ETD 05 Oct 2026 12:00 Service ANDES', false),
  tarjeta('Vessel / Voyage MSC NAVE TRES / FA003E ETD 07 Oct 2026 12:00 ETA 15 Oct 2026 06:00 Transhipment via ETA 20 Nov '
          + '2026 06:00', true),
  tarjeta('MSC NAVE CUATRO / FA004E Service ANDES ETD 09 Oct 2026 12:00', true)];
global.document = {querySelectorAll: () => tarjetas};
console.log(JSON.stringify(f()));
"""
        self.assertEqual(correr_node(self, guion), [
            {"i": 0, "nave": "MSC NAVE UNO FA001E", "etd": "03 OCT 2026", "eta": "12 NOV 2026", "sel": True},
            {"i": 1, "nave": "MSC NAVE DOS FA002E", "etd": "05 OCT 2026", "eta": "", "sel": False},
            # Con dos «ETA», ¿cuál es la llegada? Ninguna: el tránsito no se lee (medido: las 27 traen una sola).
            {"i": 2, "nave": "MSC NAVE TRES FA003E", "etd": "07 OCT 2026", "eta": "", "sel": True},
            # Sin «Vessel / Voyage» no hay nave que comparar. Hasta a198645 tomaba los primeros 40 caracteres de la
            # tarjeta, «MSC NAVE CUATRO FA004E SERVICE ANDES ETD», que no son su nave (CICLO-solo-la-nave-pedida.md).
            {"i": 3, "nave": "", "etd": "09 OCT 2026", "eta": "", "sel": True}])

    def test_transito_y_desempate(self):
        # El tiempo de tránsito es la ETA menos la ETD: en las 27 tarjetas medidas, el «Est T.T» que muestran.
        f = self.mod._msc_transito
        self.assertEqual(f({"etd": "03 OCT 2026", "eta": "12 NOV 2026"}), datetime.timedelta(days=40))
        for x in ({"etd": "03 OCT 2026", "eta": ""}, {"etd": "03 OCT 2026"}, {"eta": "12 NOV 2026"},
                  {"etd": "03 OCT 2026", "eta": "03 OCT 2026"}, {"etd": "03 OCT 2026", "eta": "01 OCT 2026"}):
            with self.subTest(tarjeta=x):
                self.assertIsNone(f(x))
        # Las dos salen el mismo día: la que llega antes. Hasta 2825153, empate.
        hoy = datetime.date.today()
        b = {"i": 7, "nave": "NAVE UNO 002E", "etd": self.etd(6), "eta": self.etd(52)}
        c = {"i": 9, "nave": "NAVE UNO 002E", "etd": self.etd(6), "eta": self.etd(46)}
        self.assertIs(self.mod._msc_elegir_salida([b, c], hoy)[0], c)
        self.assertEqual(self.mod._msc_elegir_salida([b, dict(c, eta=self.etd(52))], hoy), (None, "empate"))

    def test_salida_ambigua_queda_no_enviada_con_evidencia(self):
        hoy = datetime.date.today()
        exacta = [{"i": 7, "nave": "NAVE PRUEBA 002E", "etd": self.etd(6)},
                  {"i": 9, "nave": "NAVE PRUEBA 002E", "etd": self.etd(6)}]
        reg, vistas, log = self.corrida("msc_itinerarios")
        pagina = soporte.PaginaFalsa(texto=lambda js, *a: {"html": "<body>lista sintetica</body>", "sombras": 0}
                                     if js == self.mod._JS_HTML_COMPLETO else None)
        reserva = {"fila": 10, "nave": "NAVE PRUEBA"}
        seis = hoy + datetime.timedelta(days=6)
        # Hasta 2825153 el motivo terminaba en «…la próxima salida desde el …»; ahora dice también por qué el tiempo de
        # tránsito no desempató: estas tarjetas sintéticas no lo traen (CICLO-cola-tres-items.md).
        detalle = (f"MSC: no elegí salida para esa nave ('NAVE PRUEBA'): 2 de las 2 opciones salen el {seis:%d-%m-%Y}, la "
                   f"próxima salida desde el {hoy:%d-%m-%Y}, y no pude leer el tiempo de tránsito de 2 de ellas. Revisa "
                   "la fila y elige la salida en el portal.")
        self.assertEqual(self.mod._msc_salida_ambigua(pagina, reg, reserva, exacta, "empate", hoy), ("NO ENVIADA", detalle))
        self.assertEqual(pagina.capturas, [("msc_f10_itinerarios.png", False)])
        self.assertTrue((log.parent / "msc_f10_itinerarios.html").exists())
        for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):
            self.assertIn(f"· ✗ NO ENVIADA · {detalle}", donde)
            self.assertIn(f"itinerarios que calzan: NAVE PRUEBA 002E ETD {self.etd(6)} | NAVE PRUEBA 002E ETD "
                          f"{self.etd(6)}", donde)

    def test_salida_ambigua_con_el_mismo_tiempo_de_transito(self):
        hoy = datetime.date.today()
        exacta = [{"i": i, "nave": "NAVE PRUEBA 002E", "etd": self.etd(6), "eta": self.etd(52)} for i in (7, 9)]
        reg, _, _ = self.corrida("msc_mismo_transito")
        pagina = soporte.PaginaFalsa(texto=lambda js, *a: {"html": "<body>lista sintetica</body>", "sombras": 0})
        seis = hoy + datetime.timedelta(days=6)
        self.assertEqual(self.mod._msc_salida_ambigua(pagina, reg, {"fila": 10, "nave": "NAVE PRUEBA"}, exacta, "empate", hoy),
                         ("NO ENVIADA", f"MSC: no elegí salida para esa nave ('NAVE PRUEBA'): 2 de las 2 opciones salen el "
                                        f"{seis:%d-%m-%Y}, la próxima salida desde el {hoy:%d-%m-%Y}, y 2 de ellas tienen el "
                                        "menor tiempo de tránsito, 46 días. Revisa la fila y elige la salida en el portal."))

    def test_login_sin_clic_generico(self):
        # El login pulsa el «Next» y el de entrar solo por su texto (click_si_existe); si no encuentra uno, lo anota y no
        # pulsa nada, y la verificación de la sesión dice si entró (CICLO-inicio-de-todas.md, CICLO-cierre-de-frenos.md).
        # Hasta c4df3ab caía a _JS_CLICK_BTN; hasta 4948e16 el de entrar también podía ser el primer button[type=submit]
        # de la página. El login no está en el universo de la foto; sus pasos están en _msc_entrar.
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        for nombre in ("login_msc", "_msc_abrir", "_msc_intento", "_msc_entrar", "_msc_esperar", "_msc_recargar",
                       "_msc_escuchar", "_msc_evidencia_del_error"):
            self.assertNotIn("_JS_CLICK_BTN", [x.id for x in ast.walk(funcs[nombre]) if isinstance(x, ast.Name)], nombre)
        # Desde el encargo 50, login_msc entra solo por _msc_intento, que llama una vez a _msc_entrar; y la ida a
        # eBooking, que tenía _msc_tras_el_error, ya no está.
        def llamadas(f, a):
            return [ast.unparse(c) for c in ast.walk(funcs[f]) if isinstance(c, ast.Call) and ast.unparse(c.func) == a]
        self.assertEqual(llamadas("login_msc", "_msc_entrar"), [])
        self.assertEqual(llamadas("login_msc", "_msc_intento"),
                         ["_msc_intento(page, creds, reg, on_pausa, escucha, intento)"] * 2)
        self.assertEqual(llamadas("_msc_intento", "_msc_entrar"),
                         ["_msc_entrar(page, creds, reg, on_pausa, escucha, intento)"])
        self.assertNotIn("_msc_tras_el_error", funcs)
        # La escucha y la evidencia del error solo leen (decisión de Marcelo, encargo 50: sin clics nuevos): ni un clic,
        # ni una tecla, ni una navegación, ni un campo.
        for nombre in ("_msc_escuchar", "_msc_evidencia_del_error", "_msc_respuesta_del_error", "_msc_cabeceras"):
            hechos = [ast.unparse(c.func) for c in ast.walk(funcs[nombre]) if isinstance(c, ast.Call)
                      and isinstance(c.func, ast.Attribute) and c.func.attr in (
                          "click", "dblclick", "press", "type", "fill", "check", "goto", "reload", "go_back",
                          "go_forward", "dispatch_event", "tap", "set_input_files", "select_option")]
            self.assertEqual(hechos, [], nombre)
        f = funcs["_msc_entrar"]
        sin_boton = [n for n in ast.walk(f) if isinstance(n, ast.If) and ast.unparse(n.test).startswith("not click_si_existe(")]
        self.assertEqual([[ast.unparse(s) for s in n.body] for n in sin_boton],
                         [["reg.info('no encontré el botón «Next» ni «Siguiente» del login de MSC; no pulsé nada')"],
                          ["reg.info('no encontré el botón para entrar a MSC (Login, Sign In, Next o Iniciar); no pulsé "
                           "nada')"]])
        # Y con qué pulsa: sus textos, no «el primer botón» ni el primero de envío.
        self.assertEqual([n.test.operand.args[1].value for n in sin_boton],
                         ["button:has-text('Next'), button:has-text('Siguiente')",
                          "button:has-text('Login'), button:has-text('Sign In'), button:has-text('Next'), "
                          "button:has-text('Iniciar')"])

    def test_error_del_portal(self):
        # El error del portal en el login de MSC (_msc_error): la página de error de Chrome cuando MSC responde 502,
        # medida con OCR en msc_final (CICLO-inicio-de-todas.md) y msc_paso_email (CICLO-cierre-de-frenos.md), por su
        # texto o por su dirección (chrome-error://, la del final de los 2 logins de logs/ sin sesión), y la página de
        # error del propio MSC, medida con OCR en las 2 capturas del 2026-10-01 (encargo 45, CICLO-login-msc-y-maersk.md).
        f = self.mod._msc_error
        casos = (("https://www.mymsc.com/myMSC/Account/OidcLoginCallBack",
                  "Esta página no funciona\nwww.mymsc.com no puede procesar esta solicitud ahora.\nHTTP ERROR 502", True),
                 ("https://www.mymsc.com/myMSC/",
                  "This page isn't working\nwww.mymsc.com is currently unable to handle this request.\nHTTP ERROR 502", True),
                 ("https://www.mymsc.com/myMSC/", "Esta página no funciona\nwww.mymsc.com no puede procesar esta solicitud "
                                                  "ahora.", True),                       # sin el código
                 ("https://www.mymsc.com/mymsc/", "We are unable to complete your request at this time.", True),
                 ("chrome-error://chromewebdata/", "", True),
                 ("https://www.mymsc.com/myMSC/welcome", "Welcome to myMSC\nMy bookings", False),
                 ("https://www.mymsc.com/myMSC/", "", False))
        for url, texto, es in casos:
            with self.subTest(url=url, texto=texto[:40]):
                self.assertIs(f(soporte.PaginaFalsa(texto=texto, url=url)), es)

        def falla(js, *a):
            raise RuntimeError("marco cerrado")
        self.assertIs(f(soporte.PaginaFalsa(texto=falla, url="https://www.mymsc.com/myMSC/")), False)  # no la pudo leer

    def test_sesion_solo_en_su_pagina(self):
        # La sesión de myMSC se reconoce por su página (_msc_sesion): /myMSC/welcome, donde terminan las 53 vueltas a
        # myMSC del historial del perfil, y la de eBooking (MSC_EBOOKING). Hasta el encargo 45 bastaba que no se viera el
        # formulario y que la dirección fuera de mymsc.com: el 2026-10-01 dio por iniciada la sesión en la página de error
        # del propio MSC, en www.mymsc.com/mymsc/ (CICLO-login-msc-y-maersk.md).
        f = self.mod._msc_sesion
        si = ("https://www.mymsc.com/myMSC/welcome", "https://www.mymsc.com/mymsc/welcome/",
              "https://www.mymsc.com/myMSC/booking/main", self.mod.MSC_EBOOKING)
        no = ("https://www.mymsc.com/mymsc/", "https://www.mymsc.com/myMSC/", "https://www.mymsc.com/",
              "https://www.mymsc.com/myMSC/Account/TriggerOidcLogin",
              "https://www.mymsc.com/myMSC/Account/OidcLoginCallBack",
              "https://identityserver.msc.com/connect/authorize/callback",
              "https://mscciam.b2clogin.com/mscciam.onmicrosoft.com/oauth2/v2.0/authorize",
              "chrome-error://chromewebdata/", "https://otro.ejemplo/myMSC/welcome", "about:blank")
        for url in si + no:
            with self.subTest(url=url):
                self.assertIs(f(soporte.PaginaFalsa(url=url)), url in si)

        class SinDireccion:
            @property
            def url(self):
                raise RuntimeError("página cerrada")
        self.assertIs(f(SinDireccion()), False)

    # Las credenciales del login falso: inventadas, y largas para que _textos_de_la_cuenta las cuente (encargo 50).
    CREDS_MSC = {"usuario": "usuario.de.prueba@ejemplo.test", "clave": "ClaveDePrueba-123"}

    def login_falso(self, guion, al_abrir="portada", reg=None):
        """Corre login_msc sobre PaginaLoginMsc. 'guion' dice qué estado trae cada acción y tras cuántas esperas:
        {"Next" | "entrar" | "goto" | "recarga" | "pausa": (estado, esperas)}, o una lista de esos pares, uno por cada
        vez que pasa la acción (la última se repite; encargo 50: un intento puede salir distinto del otro). Cada
        apertura de myMSC (_msc_abrir) deja la página en 'al_abrir', como el goto a www.mymsc.com, o, con una lista, en
        el de esa apertura (la última se repite; encargo 51: la portada con el error en un intento y sin él en el otro).
        Cada recarga queda en lo que hizo, también la que el guion no trae (encargo 47). Con 'reg', corre en ese
        Registro. Deja la página en
        self.pagina_login y el Registro en self.reg_login. Devuelve (resultado, lo que hizo, las esperas, los goto,
        log.txt y las capturas)."""
        TestMsc.n_login = getattr(TestMsc, "n_login", 0) + 1         # de la clase: cada login, su carpeta
        if reg is None:
            reg, _, log = self.corrida(f"msc_login_{TestMsc.n_login}")
        else:
            log = reg.ruta
        aperturas = al_abrir if isinstance(al_abrir, list) else [al_abrir]
        pagina = PaginaLoginMsc(aperturas[0], js_html=self.mod._JS_HTML_COMPLETO, usuario=self.CREDS_MSC["usuario"])
        self.pagina_login, self.reg_login = pagina, reg
        hechos, esperas, veces = [], [], Counter()

        def accion(nombre):
            hechos.append(nombre)
            veces[nombre] += 1
            if nombre in guion:
                paso = guion[nombre]
                if isinstance(paso, list):
                    paso = paso[min(veces[nombre], len(paso)) - 1]
                if paso == "revienta":                       # la acción se corta, como con «Detener» (encargo 51)
                    raise RuntimeError("se cerró el navegador de prueba")
                pagina.llega(*paso, causa=nombre)

        def abrir(page, reg):
            hechos.append("abrir")
            pagina.estado = aperturas[min(hechos.count("abrir"), len(aperturas)) - 1]
            pagina.pendiente = None

        def rellenar(page, selector, valor, timeout_ms=15000, reg=None):
            hechos.append("escribe la clave" if "password" in selector else "escribe el usuario")
            return True

        def pulsar(page, selector, timeout_ms=2500, reg=None):
            accion("entrar" if "Login" in selector else "Next")
            return True

        def esperar(page, seg, *a, **k):
            esperas.append(seg)
            pagina.avanza()

        def ir(url, **k):
            # El goto termina en la página que carga (identityserver, en la cadena del login); lo que trae el guion
            # llega después.
            pagina.gotos.append(url)
            pagina.estado = "nada"
            accion("goto")
        pagina.goto = ir

        def recargar(**k):
            # La recarga vuelve a pedir la misma dirección (en la cadena del login, identityserver); lo que trae el
            # guion llega después.
            pagina.estado = "nada"
            accion("recarga")
        pagina.reload = recargar
        with mock.patch.multiple(self.mod, _msc_abrir=abrir, rellenar=rellenar,
                                 click_si_existe=pulsar, _msc_cookies=lambda page, reg: False, esperar=esperar,
                                 pausa_manual=lambda reg, on_pausa, mensaje: accion("pausa")):
            r = self.mod.login_msc(pagina, dict(self.CREDS_MSC), reg)
        return r, hechos, esperas, pagina.gotos, log.read_text(encoding="utf-8"), [c for c, _ in pagina.capturas]

    def test_login_termina_con_lo_primero_que_llega(self):
        # Cada espera del login de MSC termina con lo primero que llegue: el campo de la contraseña, la sesión o el error
        # del portal (decisión de Marcelo, encargo 45, CICLO-login-msc-y-maersk.md). Hasta el encargo 45, tras el «Next»
        # esperaba 3 s fijos y hasta 15 s la contraseña, y tras el botón de entrar hasta 5 s y tres vueltas de 3 s, sin
        # mirar si la sesión ya estaba: el 2026-10-01 llegó a las 16:09:06, y el programa siguió esperando hasta las 16:09:46.
        sondeo, tope = self.mod.MSC_SONDEO, self.mod.MSC_SONDEOS
        self.assertEqual(sondeo * tope, 30)
        # La sesión de identityserver seguía abierta: tras el «Next» llega la sesión, sin pedir la clave.
        r, hechos, esperas, gotos, log, caps = self.login_falso({"Next": ("sesión", 3)})
        self.assertEqual((r, hechos, esperas, gotos), (True, ["abrir", "escribe el usuario", "Next"], [sondeo] * 3, []))
        self.assertIn("· Sesión iniciada.", log)
        self.assertEqual(caps, ["msc_final.png"])
        # La contraseña y después la sesión, cada una apenas llega.
        r, hechos, esperas, gotos, _, _ = self.login_falso({"Next": ("clave", 2), "entrar": ("sesión", 5)})
        self.assertEqual((r, hechos, esperas, gotos),
                         (True, ["abrir", "escribe el usuario", "Next", "escribe la clave", "entrar"], [sondeo] * 7, []))
        # Nada llega tras el «Next»: espera el tope, una sola vez, y no da la sesión por iniciada.
        r, hechos, esperas, gotos, log, caps = self.login_falso({})
        self.assertEqual((r, hechos, esperas, gotos), (False, ["abrir", "escribe el usuario", "Next"], [sondeo] * tope, []))
        self.assertIn("· No confirmé la sesión.", log)
        self.assertEqual(caps, ["msc_paso_email.png", "msc_final.png"])
        # Ya había sesión al abrir: no escribe nada.
        r, hechos, esperas, _, log, _ = self.login_falso({}, al_abrir="sesión")
        self.assertEqual((r, hechos, esperas), (True, ["abrir"], []))
        self.assertIn("· Ya había una sesión activa.", log)
        # MSC pide una validación: pausa una vez para el operador y sigue esperando.
        r, hechos, _, _, _, caps = self.login_falso({"Next": ("clave", 0), "entrar": ("validador", 1),
                                                      "pausa": ("sesión", 0)})
        self.assertEqual((r, hechos.count("pausa")), (True, 1))
        self.assertIn("msc_validador.png", caps)

    def test_tras_el_error_despues_de_la_clave_un_solo_intento_mas(self):
        # Decisión de Marcelo, encargo 50 (CICLO-msc-segundo-intento.md): el 502 llega después de que b2clogin e
        # identityserver aceptaron el usuario y la clave, al volver a myMSC; la ida a eBooking del encargo 45 no rescató
        # la sesión en ninguno de los 4 casos medidos, y lo único medido que la recupera es otro inicio de sesión. Ante
        # ese error, un solo intento más, completo y desde el principio, y nunca un tercero: la clave se escribe a lo
        # más dos veces. Ninguna ida a eBooking. Desde el encargo 51, el mismo camino para cualquier error
        # (test_cualquier_error_un_solo_intento_mas), y el motivo dice cómo terminó cada intento.
        self.assertEqual(self.mod.MSC_INTENTOS, 2)
        entrar = ["abrir", "escribe el usuario", "Next", "escribe la clave", "entrar"]
        aviso = ("· ⚠ MSC dio un error después de la clave, al pulsar el botón de entrar. Hago un solo intento más de "
                 "inicio de sesión, desde el principio; si también falla, no hay un tercero.")
        # El error después de la clave, y el segundo intento entra.
        r, hechos, _, gotos, log, caps = self.login_falso(
            {"Next": ("clave", 0), "entrar": [("error_chrome", 1), ("sesión", 1)]})
        self.assertEqual((r, hechos, gotos), (True, entrar * 2, []))
        self.assertIn(aviso, log)
        self.assertIn("· ⚠ MSC mostró una página de error después de la clave, al pulsar el botón de entrar.", log)
        self.assertIn("· Abriendo myMSC otra vez, desde el principio...", log)
        self.assertIn("· Ingresando credenciales (segundo intento)...", log)
        self.assertIn("· Sesión iniciada.", log)
        self.assertEqual(caps, ["msc_error_clave.png", "msc_final.png"])
        # En el segundo, identityserver todavía tiene la sesión (así entró la pasada siguiente del código de antes del
        # encargo 45): tras el «Next» llega la sesión, sin pedir la clave.
        r, hechos, _, gotos, _, _ = self.login_falso({"Next": [("clave", 0), ("sesión", 1)],
                                                      "entrar": ("error_chrome", 1)})
        self.assertEqual((r, hechos, gotos), (True, entrar + ["abrir", "escribe el usuario", "Next"], []))
        # Falla también el segundo: no hay un tercero, la clave se escribió dos veces, y el motivo de las filas lo dice.
        r, hechos, _, gotos, log, caps = self.login_falso({"Next": ("clave", 0), "entrar": ("error_chrome", 1)})
        self.assertEqual((r, hechos, gotos), (False, entrar * 2, []))
        self.assertEqual((hechos.count("abrir"), hechos.count("escribe la clave")), (2, 2))
        self.assertEqual(caps, ["msc_error_clave.png", "msc_error_clave_2.png", "msc_final.png"])
        self.assertIn("· ⚠ El segundo intento de inicio de sesión de MSC tampoco dejó la sesión; no hay un "
                      "tercero.", log)
        self.assertNotIn("· Sesión iniciada.", log)
        reg = self.reg_login
        self.assertEqual(self.mod._motivo_sin_sesion(reg, "msc"),
                         "no quedó iniciada la sesión de MSC: el portal dio un error después de la clave, al pulsar el "
                         "botón de entrar, y el único intento más, desde el principio, tampoco dejó la sesión (otro "
                         "error después de la clave, al pulsar el botón de entrar). La reserva no se envió (el "
                         "detalle, en log.txt)")
        # Si el login siguiente, en el mismo Registro, entra, el motivo del anterior no queda.
        r, _, _, _, _, _ = self.login_falso({"Next": ("sesión", 1)}, reg=reg)
        self.assertEqual((r, self.mod._motivo_sin_sesion(reg, "msc")), (True, self.mod.MSC_SIN_SESION))
        # El segundo termina con el error tras el «Next», aun después de su recarga: tampoco hay un tercero.
        r, hechos, _, gotos, _, caps = self.login_falso(
            {"Next": [("clave", 0), ("error_chrome", 1)], "entrar": ("error_msc", 1), "recarga": ("error_chrome", 1)})
        self.assertEqual((r, hechos, gotos), (False, entrar + ["abrir", "escribe el usuario", "Next", "recarga"], []))
        self.assertEqual(caps, ["msc_error_clave.png", "msc_error_next_2.png", "msc_error_recarga_2.png",
                                "msc_final.png"])
        self.assertEqual(self.mod._motivo_sin_sesion(self.reg_login, "msc"),
                         "no quedó iniciada la sesión de MSC: el portal dio un error después de la clave, al pulsar el "
                         "botón de entrar, y el único intento más, desde el principio, tampoco dejó la sesión (otro "
                         "error al pulsar «Next», y su recarga no lo arregló). La reserva no se envió (el detalle, en "
                         "log.txt)")

    def test_cualquier_error_un_solo_intento_mas(self):
        # Un solo camino de rescate para cualquier error del inicio de sesión que no se resuelva (decisión de Marcelo,
        # encargo 51, CICLO-modo-y-lanzadores.md): también el de la portada y el que sigue tras el «Next» aunque lo
        # haya recargado (el 502 de TriggerOidcLogin, o el de la vuelta a myMSC que llega justo tras el «Next», sin
        # pedir la clave), y también si la recarga trae de vuelta el campo del usuario. Un solo intento más, desde el
        # principio, y nunca un tercero. Hasta el encargo 51 no reintentaba: el segundo intento era solo tras el error
        # después de la clave (encargo 50). Sin un error (no llega ni la sesión ni el error), no reintenta: puede ser
        # la clave equivocada.
        antes = ["abrir", "escribe el usuario", "Next", "recarga"]
        aviso_next = ("· ⚠ MSC dio un error al pulsar «Next», y su recarga no lo arregló. Hago un solo intento más de "
                      "inicio de sesión, desde el principio; si también falla, no hay un tercero.")
        # El error tras el «Next», otra vez tras la recarga, y el segundo intento entra.
        r, hechos, _, gotos, log, caps = self.login_falso({"Next": [("error_chrome", 1), ("sesión", 1)],
                                                            "recarga": ("error_chrome", 1)})
        self.assertEqual((r, hechos, gotos), (True, antes + ["abrir", "escribe el usuario", "Next"], []))
        self.assertIn("· ⚠ Después de la recarga, MSC sigue mostrando la página de error.", log)
        self.assertIn(aviso_next, log)
        self.assertIn("· Abriendo myMSC otra vez, desde el principio...", log)
        self.assertEqual(caps, ["msc_error_next.png", "msc_error_recarga.png", "msc_final.png"])
        # La recarga trae de vuelta el campo del usuario: no lo escribe, y el segundo intento, desde el principio, sí.
        r, hechos, _, gotos, log, caps = self.login_falso({"Next": [("error_chrome", 1), ("clave", 0)],
                                                            "recarga": ("portada", 1), "entrar": ("sesión", 1)})
        self.assertEqual((r, hechos, gotos),
                         (True, antes + ["abrir", "escribe el usuario", "Next", "escribe la clave", "entrar"], []))
        self.assertEqual(caps, ["msc_error_next.png", "msc_paso_email.png", "msc_final.png"])
        self.assertIn(aviso_next, log)
        # El error ya al abrir la portada: no escribe nada, deja su evidencia, y el segundo intento entra.
        r, hechos, _, gotos, log, caps = self.login_falso({"Next": ("sesión", 1)}, al_abrir=["error_msc", "portada"])
        self.assertEqual((r, hechos, gotos, caps),
                         (True, ["abrir", "abrir", "escribe el usuario", "Next"], [],
                          ["msc_error_portada.png", "msc_final.png"]))
        self.assertIn("· ⚠ MSC mostró una página de error al abrir su portada; no escribo el usuario ni la clave.", log)
        self.assertIn("· ⚠ MSC dio un error al abrir su portada. Hago un solo intento más de inicio de sesión, desde "
                      "el principio; si también falla, no hay un tercero.", log)
        # Fallan los dos, el primero en la portada y el segundo tras el «Next»: no hay un tercero, y el motivo lo dice.
        r, hechos, _, gotos, log, caps = self.login_falso({"Next": ("error_chrome", 1), "recarga": ("error_chrome", 1)},
                                                           al_abrir=["error_msc", "portada"])
        self.assertEqual((r, hechos, gotos), (False, ["abrir"] + antes, []))
        self.assertEqual(caps, ["msc_error_portada.png", "msc_error_next_2.png", "msc_error_recarga_2.png",
                                "msc_final.png"])
        self.assertEqual(self.mod._motivo_sin_sesion(self.reg_login, "msc"),
                         "no quedó iniciada la sesión de MSC: el portal dio un error al abrir su portada, y el único "
                         "intento más, desde el principio, tampoco dejó la sesión (otro error al pulsar «Next», y su "
                         "recarga no lo arregló). La reserva no se envió (el detalle, en log.txt)")
        # El segundo termina sin que llegue nada: el motivo también lo dice.
        r, hechos, _, _, _, _ = self.login_falso({"Next": [("error_chrome", 1), ("nada", 0)],
                                                  "recarga": ("error_chrome", 1)})
        self.assertEqual((r, hechos), (False, antes + ["abrir", "escribe el usuario", "Next"]))
        self.assertEqual(self.mod._motivo_sin_sesion(self.reg_login, "msc"),
                         "no quedó iniciada la sesión de MSC: el portal dio un error al pulsar «Next», y su recarga no "
                         "lo arregló, y el único intento más, desde el principio, tampoco dejó la sesión (no llegó ni "
                         "la sesión ni otro error). La reserva no se envió (el detalle, en log.txt)")
        # Sin un error no reintenta: nada llega tras el botón de entrar (la clave equivocada, por ejemplo)...
        r, hechos, esperas, gotos, log, _ = self.login_falso({"Next": ("clave", 0)})
        self.assertEqual((r, hechos, gotos, len(esperas)),
                         (False, ["abrir", "escribe el usuario", "Next", "escribe la clave", "entrar"], [],
                          self.mod.MSC_SONDEOS))
        self.assertIn("· No confirmé la sesión.", log)
        self.assertNotIn("Hago un solo intento más", log)
        self.assertEqual(self.mod._motivo_sin_sesion(self.reg_login, "msc"), self.mod.MSC_SIN_SESION)
        # ...ni tras el «Next».
        r, hechos, _, _, log, _ = self.login_falso({})
        self.assertEqual((r, hechos), (False, ["abrir", "escribe el usuario", "Next"]))
        self.assertNotIn("Hago un solo intento más", log)

    def test_segundo_intento_cortado_deja_su_motivo(self):
        # Si el segundo intento se corta (con «Detener», que cierra el navegador, por ejemplo), el motivo de las filas
        # dice que lo hubo y que se cortó, y no «no se reintentó» (revisión del encargo 51). La escucha se quita igual.
        with self.assertRaises(RuntimeError):
            self.login_falso({"Next": [("clave", 0), "revienta"], "entrar": ("error_chrome", 1)})
        self.assertEqual(self.mod._motivo_sin_sesion(self.reg_login, "msc"),
                         "no quedó iniciada la sesión de MSC: el portal dio un error después de la clave, al pulsar el "
                         "botón de entrar, y el único intento más, desde el principio, tampoco dejó la sesión (se "
                         "cortó antes de terminar). La reserva no se envió (el detalle, en log.txt)")
        self.assertEqual({k: v for k, v in self.pagina_login.oyentes.items() if v}, {})

    # Cómo puede terminar cada intento del login de MSC: dónde deja la página la apertura, lo que trae cada acción (en
    # el orden en que pasan), cómo termina («sesión», «error» o «nada»), cuántas veces escribe la clave y, si termina
    # con un error, cómo lo dice el motivo.
    NEXT_ERROR = [("Next", ("error_chrome", 1))]
    PLANES = {
        "portada con error": ("error_msc", [], "error", 0, "al abrir su portada"),
        "sesión tras el Next": ("portada", [("Next", ("sesión", 1))], "sesión", 0, ""),
        "nada tras el Next": ("portada", [("Next", ("nada", 0))], "nada", 0, ""),
        "clave y sesión": ("portada", [("Next", ("clave", 0)), ("entrar", ("sesión", 1))], "sesión", 1, ""),
        "clave y error": ("portada", [("Next", ("clave", 0)), ("entrar", ("error_chrome", 1))], "error", 1,
                          "después de la clave, al pulsar el botón de entrar"),
        "clave y nada": ("portada", [("Next", ("clave", 0)), ("entrar", ("nada", 0))], "nada", 1, ""),
        "recarga y sesión": ("portada", NEXT_ERROR + [("recarga", ("sesión", 1))], "sesión", 0, ""),
        "recarga y error": ("portada", NEXT_ERROR + [("recarga", ("error_chrome", 1))], "error", 0,
                            "al pulsar «Next», y su recarga no lo arregló"),
        "recarga y usuario": ("portada", NEXT_ERROR + [("recarga", ("portada", 1))], "error", 0,
                              "al pulsar «Next», y su recarga no lo arregló"),
        "recarga y nada": ("portada", NEXT_ERROR + [("recarga", ("nada", 1))], "error", 0,
                           "al pulsar «Next», y su recarga no lo arregló"),
        "recarga, clave y sesión": ("portada", NEXT_ERROR + [("recarga", ("clave", 1)), ("entrar", ("sesión", 1))],
                                    "sesión", 1, ""),
        "recarga, clave y error": ("portada", NEXT_ERROR + [("recarga", ("clave", 1)),
                                                            ("entrar", ("error_chrome", 1))], "error", 1,
                                   "después de la clave, al pulsar el botón de entrar"),
        "recarga, clave y nada": ("portada", NEXT_ERROR + [("recarga", ("clave", 1)), ("entrar", ("nada", 0))],
                                  "nada", 1, ""),
    }

    def test_la_clave_a_lo_mas_dos_veces(self):
        # FRENA SI del encargo 51: el rescate de MSC nunca escribe la clave más de dos veces en total. Cada intento
        # termina de uno de 13 modos (PLANES); el segundo, solo si el primero terminó con un error del portal, y nunca
        # un tercero. Las 85 combinaciones: las 7 que terminan sin error en el primero y las 6 × 13 que reintentan.
        # En todas: cuántas veces abre myMSC y escribe la clave, si deja la sesión, y el motivo si no.
        combinaciones = [(a,) for a, p in self.PLANES.items() if p[2] != "error"]
        combinaciones += [(a, b) for a, p in self.PLANES.items() if p[2] == "error" for b in self.PLANES]
        self.assertEqual(len(combinaciones), 85)
        for combo in combinaciones:
            with self.subTest(combo=combo):
                planes = [self.PLANES[n] for n in combo]
                guion = {}
                for _, acciones, _, _, _ in planes:
                    for accion, paso in acciones:
                        guion.setdefault(accion, []).append(paso)
                r, hechos, _, gotos, log, _ = self.login_falso(guion, al_abrir=[p[0] for p in planes])
                claves = sum(p[3] for p in planes)
                self.assertLessEqual(hechos.count("escribe la clave"), 2)
                self.assertEqual((hechos.count("abrir"), hechos.count("escribe la clave"), gotos),
                                 (len(planes), claves, []))
                self.assertIs(r, planes[-1][2] == "sesión")
                if r or len(planes) == 1:
                    continue
                segundo = (f"otro error {planes[1][4]}" if planes[1][2] == "error"
                           else "no llegó ni la sesión ni otro error")
                self.assertEqual(self.mod._motivo_sin_sesion(self.reg_login, "msc"),
                                 f"no quedó iniciada la sesión de MSC: el portal dio un error {planes[0][4]}, y el "
                                 f"único intento más, desde el principio, tampoco dejó la sesión ({segundo}). La "
                                 f"reserva no se envió (el detalle, en log.txt)")

    def test_el_error_deja_su_respuesta_y_su_evidencia(self):
        # Cuando aparece el error, log.txt anota la respuesta que lo trajo: su dirección sin parámetros, su código HTTP,
        # los nombres de sus cabeceras y el valor solo de las que nombran al servidor o a una protección contra robots;
        # nunca cookies, tokens ni valores de sesión. Y se guardan la captura y el HTML de la página de error, salvo el
        # que traiga el usuario o la clave (decisión de Marcelo, encargo 50). Solo escucha: la página falsa emite lo
        # medido sin red en Chrome, con datos inventados.
        cab = "cabeceras (6): content-length, content-type, server, set-cookie, via, x-azure-ref"
        valores = "server: PasarelaDePrueba/1.0 · via: 1.1 proxy-de-prueba"
        # Tras la clave: la vuelta a myMSC, un POST sin consulta; su HTML no trae el usuario, y se guarda.
        r, _, _, _, log, _ = self.login_falso({"Next": ("clave", 0), "entrar": [("error_chrome", 1), ("sesión", 1)]})
        self.assertIs(r, True)
        self.assertIn("    respuesta que trajo la página de error: POST https://www.mymsc.com/myMSC/Account/"
                      f"OidcLoginCallBack · HTTP 502 · falla de red: net::ERR_HTTP_RESPONSE_CODE_FAILURE · {cab} · "
                      f"{valores}\n", log)
        self.assertIn("    URL: chrome-error://chromewebdata/\n", log)
        self.assertIn("    evidencia del error de MSC: msc_error_clave.png y 1 de 1 HTML (la página y 0 marco(s))", log)
        html = (self.reg_login.ruta.parent / "msc_error_clave.html").read_text(encoding="utf-8")
        self.assertIn("no puede procesar esta solicitud", html)
        # Tras el «Next»: TriggerOidcLogin, un GET con el usuario en la consulta. log.txt no trae la consulta, y el HTML
        # de la página de error de Chrome, que la repite, no se guarda.
        r, _, _, _, log, caps = self.login_falso({"Next": [("error_chrome", 1), ("clave", 0)],
                                                  "recarga": ("clave", 1), "entrar": ("sesión", 1)})
        self.assertIs(r, True)
        self.assertIn("    respuesta que trajo la página de error: GET https://www.mymsc.com/myMSC/Account/"
                      f"TriggerOidcLogin · HTTP 502 · falla de red: net::ERR_HTTP_RESPONSE_CODE_FAILURE · {cab} · "
                      f"{valores}\n", log)
        self.assertIn("· ⚠ No guardé el HTML de la página con el error del login de MSC: trae el usuario o la clave de "
                      "la cuenta.", log)
        self.assertIn("    evidencia del error de MSC: msc_error_next.png y 0 de 1 HTML (la página y 0 marco(s))", log)
        self.assertEqual(caps, ["msc_error_next.png", "msc_final.png"])
        self.assertFalse((self.reg_login.ruta.parent / "msc_error_next.html").exists())
        # Ni en log.txt ni en ningún archivo de la corrida: el usuario, la clave, la cookie, la referencia ni la
        # consulta.
        for archivo in self.reg_login.ruta.parent.iterdir():
            texto = archivo.read_text(encoding="utf-8", errors="replace").casefold()
            for secreto in (self.CREDS_MSC["usuario"], quote(self.CREDS_MSC["usuario"], safe=""),
                            self.CREDS_MSC["clave"], "VALORDECOOKIEDEPRUEBA", "REFERENCIADEPRUEBA",
                            "usernameLoginHint"):
                with self.subTest(archivo=archivo.name, secreto=secreto[:12]):
                    self.assertNotIn(secreto.casefold(), texto)
        # Al terminar, deja de escuchar.
        self.assertEqual({k: v for k, v in self.pagina_login.oyentes.items() if v}, {})

    def test_respuesta_del_error_sin_valores_de_sesion(self):
        # _msc_respuesta_del_error, de lo que _msc_escuchar vio desde la línea anterior: la última respuesta con un
        # código de 400 o más (con su falla de red, si es de su misma dirección); si no, la última falla; si no, la
        # última respuesta. Solo los documentos del marco principal. Las cabeceras: el nombre de todas, y el valor solo
        # de las de MSC_CABECERAS_CON_VALOR (decisión de Marcelo, encargo 50).
        marco = object()
        pagina = types.SimpleNamespace(main_frame=marco, oyentes={})
        pagina.on = lambda ev, f: pagina.oyentes.setdefault(ev, []).append(f)
        pagina.remove_listener = lambda ev, f: pagina.oyentes[ev].remove(f)
        escucha = self.mod._msc_escuchar(pagina)
        self.assertIs(escucha["activa"], True)

        def emitir(ev, obj):
            for f in list(pagina.oyentes.get(ev, ())):
                f(obj)
        cab = {"Server": "PasarelaDePrueba/1.0", "Set-Cookie": "sesion=VALORDECOOKIEDEPRUEBA", "X-Azure-Ref": "REF-1",
               "cf-ray": "RAYODEPRUEBA-SCL", "Via": "1.1   proxy " + "x" * 100, "X-Request-Id": "IDDEPRUEBA"}
        url = "https://usuario:clave@www.mymsc.com:8443/myMSC/Account/TriggerOidcLogin?usernameLoginHint=u%40e.test#f"
        emitir("response", RespuestaFalsa(marco, "GET", "https://www.mymsc.com/myMSC/", 200, {"server": "otro"}))
        emitir("response", RespuestaFalsa(marco, "GET", url, 503, cab))
        emitir("response", RespuestaFalsa(marco, "GET", url, 502, cab))
        emitir("requestfailed", falla_de_red(marco, "GET", url))
        # De otro marco o que no es un documento: no cuentan.
        emitir("response", RespuestaFalsa(object(), "GET", "https://otro.ejemplo/marco", 500, {}))
        emitir("response", RespuestaFalsa(marco, "GET", "https://www.mymsc.com/imagen.png", 404, {}, tipo="image"))
        emitir("requestfailed", falla_de_red(marco, "GET", "https://www.mymsc.com/api", tipo="xhr"))
        linea = self.mod._msc_respuesta_del_error(escucha)
        self.assertEqual(linea, "respuesta que trajo la página de error: GET https://www.mymsc.com:8443/myMSC/Account/"
                                "TriggerOidcLogin · HTTP 502 · falla de red: net::ERR_HTTP_RESPONSE_CODE_FAILURE · "
                                "cabeceras (6): cf-ray, server, set-cookie, via, x-azure-ref, x-request-id · server: "
                                f"PasarelaDePrueba/1.0 · via: 1.1 proxy {'x' * 70}")
        for secreto in ("VALORDECOOKIE", "REF-1", "RAYODEPRUEBA", "IDDEPRUEBA", "usuario", "clave", "u%40e", "#f"):
            self.assertNotIn(secreto, linea)
        # Lo ya informado no se repite.
        self.assertEqual(self.mod._msc_respuesta_del_error(escucha),
                         "no vi ninguna respuesta nueva de la página: no sé cuál trajo la página de error")
        # Una falla de red sin respuesta; y, si ninguna falló, la última respuesta.
        emitir("requestfailed", types.SimpleNamespace(method="POST", url=url, resource_type="document", frame=marco,
                                                      failure="net::ERR_CONNECTION_RESET"))
        self.assertEqual(self.mod._msc_respuesta_del_error(escucha),
                         "petición que falló, sin respuesta HTTP: POST https://www.mymsc.com:8443/myMSC/Account/"
                         "TriggerOidcLogin · falla de red: net::ERR_CONNECTION_RESET")
        emitir("response", RespuestaFalsa(marco, "GET", "https://www.mymsc.com/mymsc/?errorMessage=x", 200,
                                          {"server": "PasarelaDePrueba/1.0"}))
        self.assertEqual(self.mod._msc_respuesta_del_error(escucha),
                         "ninguna respuesta falló; la última: GET https://www.mymsc.com/mymsc/ · HTTP 200 · "
                         "cabeceras (1): server · server: PasarelaDePrueba/1.0")
        # Sin all_headers, headers, que no trae las de cookies, y lo dice.
        r = RespuestaFalsa(marco, "GET", url, 502, cab)
        r.all_headers = None
        self.assertEqual(self.mod._msc_cabeceras(r),
                         "cabeceras (5, sin las de cookies: no pude leerlas todas): cf-ray, server, via, x-azure-ref, "
                         f"x-request-id · server: PasarelaDePrueba/1.0 · via: 1.1 proxy {'x' * 70}")
        # Ninguna cabecera de la lista con valor es de cookies, de autorización ni de sesión, ni un identificador.
        self.assertEqual([h for h in self.mod.MSC_CABECERAS_CON_VALOR
                          if re.search(r"cookie|auth|token|sesi|session|key|-id|ref|ray|cid", h)], [])
        # Deja de escuchar; y una página que no deja escuchar lo dice.
        escucha["quitar"]()
        self.assertEqual({k: v for k, v in pagina.oyentes.items() if v}, {})
        self.assertEqual(self.mod._msc_respuesta_del_error(self.mod._msc_escuchar(object())),
                         "no pude escuchar la red de la página: no sé qué respuesta trajo la página de error")
        self.assertEqual(self.mod._msc_respuesta_del_error(None),
                         "no pude escuchar la red de la página: no sé qué respuesta trajo la página de error")
        # La dirección en log.txt, sin su consulta ni su fragmento, y lo dice: Registro.url, en las seis navieras desde
        # el encargo 51 (hasta ahí, _msc_url, solo en el login de MSC).
        reg, _, log = self.corrida("msc_url")
        reg.url(soporte.PaginaFalsa(url=url))
        reg.url(soporte.PaginaFalsa(url="https://www.mymsc.com/myMSC/"))
        self.assertEqual(re.findall(r"URL: .*", log.read_text(encoding="utf-8")),
                         ["URL: https://www.mymsc.com:8443/myMSC/Account/TriggerOidcLogin (sin su consulta ni su "
                          "fragmento)", "URL: https://www.mymsc.com/myMSC/"])

    def test_html_sin_el_usuario_ni_la_clave(self):
        # _guardar_html_completo con 'sin' no escribe el HTML que traiga uno de esos textos, sin distinguir mayúsculas,
        # y lo avisa sin decir cuál; los demás, sí. _textos_de_la_cuenta da el usuario y la clave tal cual y codificados
        # para una dirección; los de menos de 3 caracteres no cuentan (encargo 50: la evidencia del login de MSC).
        textos = self.mod._textos_de_la_cuenta({"usuario": " usuario.de.prueba@ejemplo.test ",
                                                "clave": "Clave/De Prueba"})
        self.assertEqual(textos, tuple(sorted({"usuario.de.prueba@ejemplo.test", "usuario.de.prueba%40ejemplo.test",
                                               "Clave/De Prueba", "Clave%2FDe%20Prueba", "Clave/De%20Prueba"})))
        self.assertEqual(self.mod._textos_de_la_cuenta({"usuario": "ab", "clave": ""}), ())
        self.assertEqual(self.mod._textos_de_la_cuenta(None), ())
        reg, _, log = self.corrida("html_sin")
        marco = soporte.PaginaFalsa(texto=lambda js, *a: {"html": "<p>marco sin datos</p>"}, url="https://marco.test/")
        for html, guardado in (("<p>hola USUARIO.DE.PRUEBA%40EJEMPLO.TEST</p>", False),
                               ("<p>Clave/De Prueba</p>", False), ("<p>nada de la cuenta</p>", True)):
            with self.subTest(html=html):
                pagina = soporte.PaginaFalsa(texto=lambda js, *a, h=html: {"html": h},
                                             url="chrome-error://chromewebdata/", frames=[marco])
                n = f"html_{len(html)}"
                self.assertEqual(self.mod._guardar_html_completo(pagina, reg, n, "con el error del login de MSC",
                                                                 sin=textos), (2 if guardado else 1, 2, 0))
                self.assertIs((reg.dir_capturas / f"{n}.html").exists(), guardado)
                self.assertTrue((reg.dir_capturas / f"{n}_marco1.html").exists())
        aviso = ("· ⚠ No guardé el HTML de la página con el error del login de MSC: trae el usuario o la clave de la "
                 "cuenta.")
        self.assertEqual(log.read_text(encoding="utf-8").count(aviso), 2)
        # Sin 'sin', como siempre.
        pagina = soporte.PaginaFalsa(texto=lambda js, *a: {"html": "<p>Clave/De Prueba</p>"}, url="https://x.test/")
        self.assertEqual(self.mod._guardar_html_completo(pagina, reg, "html_sin_lista", "en la guarda"), (1, 1, 0))

    def test_tras_el_error_del_next_recarga_una_vez(self):
        # El 502 tras el «Next» (TriggerOidcLogin): espera MSC_PAUSA_RECARGA s, recarga esa página una sola vez y espera
        # lo primero que llegue (decisión de Marcelo, encargo 47, CICLO-msc-recarga-y-corrida-02-10.md). Así rescataba
        # la sesión el código de antes del encargo 45: en el historial del perfil, la recarga siguió sola hasta la
        # página de la clave. No vuelve a escribir el usuario, no reenvía la clave ni hace otro intento de inicio de
        # sesión. El 2026-10-02, sin la recarga, la ida a eBooking llevó a la portada de myMSC, sin la sesión.
        sondeo, pausa = self.mod.MSC_SONDEO, self.mod.MSC_PAUSA_RECARGA
        self.assertEqual(pausa, 20)
        aviso = "· ⚠ MSC mostró una página de error al pulsar «Next». Espero 20 s y recargo esa página una sola vez"
        antes = ["abrir", "escribe el usuario", "Next", "recarga"]
        tope = self.mod.MSC_SONDEOS
        # La recarga lleva a la página de la clave: la escribe por primera vez, y llega la sesión.
        r, hechos, esperas, gotos, log, caps = self.login_falso(
            {"Next": ("error_chrome", 1), "recarga": ("clave", 2), "entrar": ("sesión", 1)})
        self.assertEqual((r, hechos, esperas, gotos),
                         (True, antes + ["escribe la clave", "entrar"], [sondeo, pausa, sondeo, sondeo, sondeo], []))
        self.assertIn(aviso, log)
        self.assertIn("· Sesión iniciada.", log)
        self.assertEqual(caps, ["msc_error_next.png", "msc_final.png"])
        # La recarga deja la sesión: no escribe la clave.
        r, hechos, _, gotos, _, _ = self.login_falso({"Next": ("error_chrome", 1), "recarga": ("sesión", 1)})
        self.assertEqual((r, hechos, gotos), (True, antes, []))
        # Vuelve el campo del usuario: la recarga no lo escribe ni pulsa «Next» otra vez; espera la clave hasta el
        # tope, una sola vez por intento. Desde el encargo 51, el login hace su único intento más, desde el principio
        # (aquí, con el mismo error): una recarga por intento, y no da la sesión por iniciada.
        r, hechos, esperas, gotos, log, caps = self.login_falso({"Next": ("error_chrome", 1),
                                                                  "recarga": ("portada", 1)})
        self.assertEqual((r, hechos, esperas, gotos), (False, antes * 2, ([sondeo, pausa] + [sondeo] * tope) * 2, []))
        self.assertIn("no vi el campo de contraseña", log)
        self.assertEqual(caps, ["msc_error_next.png", "msc_paso_email.png", "msc_error_next_2.png",
                                "msc_paso_email_2.png", "msc_final.png"])
        # Sigue el error: una sola recarga por intento, con su evidencia. Hasta el encargo 50, después iba una sola vez
        # a eBooking (encargo 45); en el 50, no reintentaba; desde el 51, el único intento más, desde el principio.
        r, hechos, _, gotos, log, caps = self.login_falso(
            {"Next": ("error_chrome", 1), "recarga": ("error_chrome", 1)})
        self.assertEqual((r, hechos, gotos), (False, antes * 2, []))
        self.assertEqual(caps, ["msc_error_next.png", "msc_error_recarga.png", "msc_error_next_2.png",
                                "msc_error_recarga_2.png", "msc_final.png"])

    def test_search_schedule_sin_boton_corta(self):
        # «Search Schedule» con _msc_buscar_itinerarios: el botón por su texto (click_si_existe); si no está, corta como
        # objetivo no encontrado, sin pulsar nada (CICLO-inicio-de-todas.md). Hasta c4df3ab caía a _JS_CLICK_BTN, que
        # pulsaba también enlaces e input submit, visibles o no.
        reg, _, _ = self.corrida("msc_busca")
        pedidos = []

        def sin_boton(page, selector, timeout_ms=2500, reg=None):
            pedidos.append(selector)
            return False
        with mock.patch.object(self.mod, "click_si_existe", sin_boton):
            with self.assertRaises(self.mod.ObjetivoNoEncontrado) as c:
                self.mod._msc_buscar_itinerarios(object(), reg)
        self.assertEqual((c.exception.paso, c.exception.buscaba, pedidos),
                         ("Search Schedule de MSC", "el botón «Search Schedule» o «Buscar» (por su texto)",
                          ["button:has-text('Search Schedule'), button:has-text('Buscar')"]))
        with mock.patch.object(self.mod, "click_si_existe", lambda *a, **k: True):
            self.assertIsNone(self.mod._msc_buscar_itinerarios(object(), reg))
        # reservar_msc la llama antes de la guarda; _JS_CLICK_BTN queda solo en el envío, después, que no se toca.
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_msc")
        g = linea_guarda(f)
        antes = [c for n in antes_de_la_guarda(f, g) for c in ast.walk(n) if isinstance(c, ast.Call)]
        self.assertEqual([ast.unparse(c) for c in antes if ast.unparse(c.func) == "_msc_buscar_itinerarios"],
                         ["_msc_buscar_itinerarios(page, reg)"])
        nombres = lambda nodos: [x.id for n in nodos for x in ast.walk(n) if isinstance(x, ast.Name)]
        self.assertNotIn("_JS_CLICK_BTN", nombres(antes_de_la_guarda(f, g)))
        self.assertEqual(nombres(f.body).count("_JS_CLICK_BTN"), 1)

    def test_reservar_msc_no_toma_la_primera(self):
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_msc")
        asignas = {ast.unparse(n.targets[0]): (ast.unparse(n), n.lineno) for n in ast.walk(f) if isinstance(n, ast.Assign)}
        self.assertEqual(asignas["desde"][0], "desde = _msc_desde(reserva)")
        self.assertEqual(asignas["(elegida, motivo)"][0],
                         "elegida, motivo = _msc_elegir_salida(exacta, desde) if exacta else (None, '')")
        fecha = [n for n in ast.walk(f) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "_msc_fecha"]
        self.assertEqual([ast.unparse(n) for n in fecha], ["_msc_fecha(page, desde.isoformat(), reg)"])
        self.assertLess(asignas["desde"][1], fecha[0].lineno)                  # busca desde la misma fecha con que elige
        sin_una = [n for n in ast.walk(f) if isinstance(n, ast.If) and ast.unparse(n.test) == "exacta and elegida is None"]
        self.assertEqual([ast.unparse(r) for n in sin_una for r in ast.walk(n) if isinstance(r, ast.Return)],
                         ["return _msc_salida_ambigua(page, reg, reserva, exacta, motivo, desde)"])
        clics = [n for n in ast.walk(f) if isinstance(n, ast.Call) and "_JS_MSC_CLIC_NAVE" in [ast.unparse(a) for a in n.args]]
        self.assertEqual([ast.unparse(n) for n in clics], ["page.evaluate(_JS_MSC_CLIC_NAVE, elegida['i'])"])
        self.assertLess(sin_una[0].lineno, clics[0].lineno)
        self.assertLess(clics[0].lineno, linea_guarda(f))

    def test_reservar_msc_baja_si_no_esta(self):
        # Si la nave no está en lo que muestra la lista, baja por ella (no es un clic) para que MSC cargue más, hasta
        # encontrarla o hasta que no lleguen tarjetas nuevas, con un tope; si no aparece, el REVISAR dice hasta qué fecha
        # buscó (decisión de Marcelo, CICLO-ampliar-msc-y-cma.md). Hasta el encargo 33 cortaba con lo cargado de entrada.
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_msc")
        bucle = [n for n in ast.walk(f) if isinstance(n, ast.While)]
        self.assertEqual(len(bucle), 1)
        prueba = ast.unparse(bucle[0].test)
        self.assertTrue(prueba.startswith("not any("), prueba)
        self.assertIn("x.get('sel') and _trae_la_nave(_norm(x.get('nave')), toks) for x in naves", prueba)
        cuerpo = [ast.unparse(s) for s in bucle[0].body]
        self.assertEqual(cuerpo[0], "if bajadas >= AMPLIAR_MAX:\n    por_que = f'bajé por la lista {AMPLIAR_MAX} veces, "
                                    "el tope'\n    break")
        self.assertTrue(cuerpo[1].startswith("por_que = _msc_bajar(page, reg, sum("), cuerpo[1])
        self.assertIn("1 for x in naves if x.get('sel')", cuerpo[1])
        self.assertEqual(cuerpo[2:4], ["if por_que:\n    break", "bajadas += 1"])
        self.assertIn("naves = page.evaluate(_JS_MSC_NAVES) or naves", cuerpo[4])
        asignas = {ast.unparse(n): n.lineno for n in ast.walk(f) if isinstance(n, ast.Assign)}
        exacta = next(v for k, v in asignas.items() if k.startswith("exacta = "))
        self.assertLess(bucle[0].lineno, exacta)
        self.assertIn("donde = '' if exacta else f\": {_hasta_donde_busque([_msc_fecha_etd(n.get('etd')) for n in naves], "
                      "por_que)}\"", asignas)
        self.assertLess(bucle[0].lineno, linea_guarda(f))

    def test_baja_por_la_lista(self):
        # Baja (_JS_MSC_BAJAR) y espera hasta MSC_ESPERA_MAS s a que haya más tarjetas con su «Select» a la vista.
        def pagina(bajar, cuentas):
            eventos, cuentas = [], list(cuentas)

            def responder(js, *a):
                if js == self.mod._JS_MSC_BAJAR:
                    eventos.append("bajar")
                    if isinstance(bajar, Exception):
                        raise bajar
                    return bajar
                if js == self.mod._JS_MSC_COUNT_SCHED:
                    eventos.append("contar")
                    return cuentas.pop(0) if cuentas else 26
                raise AssertionError("JavaScript inesperado")
            return soporte.PaginaFalsa(texto=responder), eventos
        espera = self.mod.MSC_ESPERA_MAS
        casos = ((27, [26, 26, 30], "", ["bajar"] + ["contar"] * 3),
                 (27, [], self.mod.NO_AMPLIA_MAS, ["bajar"] + ["contar"] * espera),
                 (0, [], "no pude ampliar la búsqueda: no encontré la lista de itinerarios para bajar por ella", ["bajar"]),
                 (RuntimeError("marco cerrado"), [], "no pude ampliar la búsqueda: no pude bajar por la lista (marco "
                                                     "cerrado)", ["bajar"]))
        for k, (bajar, cuentas, esperado, orden) in enumerate(casos):
            with self.subTest(k=k):
                reg, _, log = self.corrida(f"msc_bajar_{k}")
                p, eventos = pagina(bajar, cuentas)
                self.assertEqual(self.mod._msc_bajar(p, reg, 26), esperado)
                self.assertEqual(eventos, orden)
                if not esperado:
                    self.assertIn("búsqueda ampliada: 26 -> 30 itinerarios", log.read_text(encoding="utf-8"))
        self.assertEqual(espera, 15)

    def test_js_bajar(self):
        # Lleva al final cada ancestro de las tarjetas que tenga desplazamiento, y la ventana; sin tarjetas, nada.
        guion = "const f = " + self.mod._JS_MSC_BAJAR + r""";
const caja = (alto, visible) => ({scrollHeight: alto, clientHeight: visible, scrollTop: 0, parentElement: null});
const correr = (n) => {
  const cuerpo = caja(5000, 800), lista = caja(3000, 600), fija = caja(400, 400);
  fija.parentElement = lista; lista.parentElement = cuerpo;
  const tarjetas = Array.from({length: n}, () => ({parentElement: fija}));
  let ventana = null;
  global.window = {scrollTo: (x, y) => { ventana = y; }};
  global.document = {documentElement: {scrollHeight: 5000},
                     querySelectorAll: (s) => (s === 'div.shipment-grid-list' ? tarjetas : [])};
  return [f(), lista.scrollTop, cuerpo.scrollTop, fija.scrollTop, ventana];
};
console.log(JSON.stringify([correr(27), correr(0)]));
"""
        self.assertEqual(correr_node(self, guion), [[27, 3000, 5000, 0, 5000], [0, 0, 0, 0, None]])


class LocFalso:
    """Localizador de Playwright falso: existe si su selector está entre los visibles de la página."""
    first = property(lambda s: s)

    def __init__(self, pagina, sel):
        self.pagina, self.sel = pagina, sel

    def filter(self, has_text=None, visible=None):
        self.pagina.filtros.append((self.sel, getattr(has_text, "pattern", has_text), visible))
        return self

    def evaluate(self, js, *a, **k):                  # k: el plazo con que lo lee el programa (encargo 55)
        return self.pagina.evaluate(js, *a)

    def count(self):
        return 1 if self.sel in self.pagina.visibles else 0

    def is_visible(self, **k):
        return bool(self.count())

    def is_disabled(self):
        return False

    def scroll_into_view_if_needed(self, **k):
        pass

    def click(self, **k):
        self.pagina.clics.append(self.sel)

    def fill(self, v, **k):
        self.pagina.clics.append(("escribe", self.sel, v))

    def type(self, v, **k):
        pass

    def input_value(self, **k):
        return ""

    def text_content(self):
        return "40' Reefer High Cube"


class PaginaCma(soporte.PaginaFalsa):
    """Página falsa de CMA: 'visibles' son los selectores que existen; 'js' responde a cada JavaScript según
    una marca de su texto (uno sin marca devuelve None). Anota los clics y las teclas."""

    def __init__(self, visibles=(), js=None):
        super().__init__()
        self.visibles, self.js, self.clics, self.teclas, self.filtros = set(visibles), dict(js or {}), [], [], []
        self.keyboard = types.SimpleNamespace(press=self.teclas.append,
                                              type=lambda t, delay=None: self.teclas.append(t))

    def locator(self, sel):
        if sel == ":root":                       # lo que el programa lee con plazo (encargo 55)
            return soporte.RaizFalsa(self)
        return LocFalso(self, sel)

    def get_by_placeholder(self, texto):
        return LocFalso(self, f"placeholder={texto}")

    def evaluate(self, js, *a):
        return next((r for marca, r in self.js.items() if marca in js), None)


class TestCma(ConRegistro):
    SELECCIONAR = "input[placeholder*='Seleccionar' i]"
    OPCION = ".el-select-dropdown:visible li:visible"

    def test_aviso_de_mantenimiento(self):
        # El aviso medido el 2026-09-26 en la pantalla donde la reserva cortó (CICLO-cierre-de-frenos.md): su título, y
        # debajo la ventana anunciada.
        f = self.mod._cma_en_mantenimiento
        casos = (("Inicio\nWe are improving the eBusiness area\nStart: September 26 from 7 PM CEST", True),
                 ("WE ARE IMPROVING THE\n  eBusiness AREA", True),         # sin distinguir mayúsculas ni saltos
                 ("Click & Book\nPort of loading", False),
                 ("We are improving our website", False),
                 ("", False))
        for texto, esta in casos:
            with self.subTest(texto=texto[:30]):
                self.assertIs(f(soporte.PaginaFalsa(texto=texto)), esta)

        def falla(js, *a):
            raise RuntimeError("marco cerrado")
        self.assertIs(f(soporte.PaginaFalsa(texto=falla)), False)

    def test_en_mantenimiento_la_fila_queda_no_enviada(self):
        # Con el aviso, reservar_cma no busca el Origen: la fila queda NO ENVIADA con el motivo que decidió Marcelo, con la
        # captura de la ventana (CICLO-cierre-de-frenos.md). Hasta 4948e16 cortaba en el Origen, hablando de la sugerencia.
        reserva = {"fila": 7, "pol": "LIRQUEN, CHILE", "destino_orig": "SHANGHAI", "destino_final": "SHANGHAI",
                   "nave": "CMA CGM NAVE PRUEBA", "dia_carga": ""}
        motivo = "el portal de CMA está en mantenimiento"
        buscados = []
        cambios = dict(_cma_esperar_desafio=lambda *a, **k: True, esperar_hasta=lambda *a, **k: True,
                       _cma_puerto=lambda page, sel, *a, **k: buscados.append(sel) or False)
        reg, vistas, log = self.corrida("cma_mantenimiento")
        pagina = PaginaCmaPortal("Inicio\nWe are improving the eBusiness area\nStart: September 26 from 7 PM CEST")
        with mock.patch.multiple(self.mod, **cambios):
            self.assertEqual(self.mod.reservar_cma(pagina, reserva, {"contrato": ""}, reg), ("NO ENVIADA", motivo))
        self.assertEqual(self.mod.CMA_MANTENIMIENTO, motivo)
        self.assertEqual((pagina.visitas, buscados), (["https://www.cma-cgm.com/ebusiness/shipment/request"], []))
        self.assertEqual(pagina.capturas, [("cma_f7_mantenimiento.png", False)])
        for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):
            self.assertIn(f"· ✗ NO ENVIADA · {motivo}", donde)
        # Sin el aviso, busca el Origen como antes. Si no lo eligiera (aquí, un _cma_puerto falso que devuelve False: el
        # de verdad corta él mismo), NO ENVIADA con la captura del paso (desde el encargo 42,
        # CICLO-maersk-y-fila-sin-ruta.md; hasta ahí, ese False daba REVISAR).
        reg, _, _ = self.corrida("cma_sin_mantenimiento")
        pagina = PaginaCmaPortal("Click & Book\nPort of loading")
        with mock.patch.multiple(self.mod, **cambios):
            self.assertEqual(self.mod.reservar_cma(pagina, reserva, {"contrato": ""}, reg),
                             ("NO ENVIADA", "Origen de CMA: no encontré una sugerencia que elegir para «LIRQUEN», "
                                            "así que no pulsé nada. La reserva no se envió; revisa ese paso en el "
                                            "portal."))
        self.assertEqual((buscados, pagina.capturas), (["#pol"], [("cma_f7_sin_objetivo.png", False)]))

    def corta(self, funcion, pagina, *args):
        reg, _, log = self.corrida()
        with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
            funcion(pagina, *args, reg)
        return e.exception, log.read_text(encoding="utf-8")

    def test_tamano_y_tipo_no_abre_el_primer_desplegable(self):
        pagina = PaginaCma(visibles={".el-select input", "div:has-text('Tamaño y tipo') input"},
                           js={"querySelector(\".el-form-item input": True})
        e, _ = self.corta(self.mod._cma_completar_info_extra, pagina, {"fila": 5})
        # Lo que buscaba separa este corte del de la opción, que tiene el mismo paso (CICLO-cola-nueve-items.md).
        self.assertEqual((e.paso, e.buscaba, pagina.clics),
                         ("Tamaño y tipo de CMA", "el desplegable «Tamaño y tipo» (por su etiqueta o su placeholder "
                                                  "«Seleccionar»)", []))

    def test_peso_solo_por_su_etiqueta(self):
        pagina = PaginaCma(visibles={self.SELECCIONAR, self.OPCION, "div:has-text('Peso por contenedor') >> input"},
                           js={"peso por contenedor": False})
        e, _ = self.corta(self.mod._cma_completar_info_extra, pagina, {"fila": 5})
        self.assertEqual((e.paso, pagina.clics), ("Peso por contenedor de CMA", [self.SELECCIONAR, self.OPCION]))

    def test_itinerario_sin_nave_no_elige_el_primero(self):
        botones = ("button:has-text('Seleccionar'), button:has-text('Select'), button:has-text('Deseleccionar'), "
                   "button:has-text('Deselect')")
        pagina = PaginaCma(visibles={botones}, js={"getCard": {"ok": False, "ofrecidas": ["NAVE PRUEBA UNO"]},
                                                  "primer itinerario seleccionado": {"ok": True, "msg": "el primero"}})
        reg, _, _ = self.corrida()
        with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
            self.mod._cma_seleccionar_itinerario(pagina, {"nave": "", "viaje": ""}, reg)
        self.assertEqual((e.exception.paso, e.exception.buscaba),
                         ("Itinerario de CMA", "la nave de la reserva: la fila no trae nave, y no elijo un itinerario "
                                               "a ciegas"))

    # --- La nave con todas sus palabras en «Route choices» (CICLO-cola-tres-items.md) ---
    def js_rutas(self):
        """El JavaScript con que _cma_seleccionar_itinerario lee y elige la ruta. Hasta f68ce6c iba escrito dentro de la
        función; desde CICLO-cola-seis-items.md es _JS_CMA_RUTAS, que lleva al principio _JS_TRAE_LA_NAVE."""
        return self.mod._JS_CMA_RUTAS

    def test_js_rutas_nave_con_todas_sus_palabras(self):
        guion = "const f = " + self.js_rutas() + r""";
const nodo = (tag, texto, hijos = []) => {
  const n = {tagName: tag.toUpperCase(), texto, hijos, parentElement: null, offsetParent: {}, id: '', clics: 0,
             getBoundingClientRect: () => ({width: 10, height: 10}), scrollIntoView() {}, click() { this.clics++; }};
  Object.defineProperty(n, 'textContent', {get() { return [this.texto, ...this.hijos.map(h => h.textContent)].join(' '); }});
  const todos = (x) => x.hijos.flatMap(h => [h, ...todos(h)]);
  n.contains = (x) => x === n || todos(n).includes(x);
  n.querySelectorAll = (sel) => todos(n).filter(e => sel.split(',').some(s => e.tagName === s.trim().toUpperCase()));
  hijos.forEach(h => { h.parentElement = n; });
  return n;
};
// Cada ruta: su buque principal, su corte y su botón «Seleccionar», como las opciones de «Route choices».
const ruta = (nave) => nodo('div', '', [nodo('p', 'Buque principal: ' + nave), nodo('p', 'Port Cut-off: 01/10/2026'),
                                        nodo('button', 'Seleccionar')]);
const correr = (naves, toks) => {
  const body = nodo('body', '', [nodo('div', '', naves.map(ruta))]);
  global.document = {querySelectorAll: (s) => body.querySelectorAll(s)};
  const r = f({toks});
  return [!!r.ok, body.querySelectorAll('button').map(b => b.clics)];
};
console.log(JSON.stringify([
  correr(['NAVE PRUEBA', 'NAVE OTRA'], ['CMA', 'CGM', 'NAVE', 'PRUEBA']),
  correr(['CMA CGM NAVE PRUEBA', 'NAVE OTRA'], ['CMA', 'CGM', 'NAVE', 'PRUEBA']),
  correr(['NAVE OTRA', 'NAVE PRUEBA'], ['NAVE', 'PRUEBA']),
  correr(['NAVE PRUEBA', 'NAVE OTRA'], []),
  correr(['CMA CGM SAVANNAH', 'CMA CGM ANNA'], ['CMA', 'CGM', 'ANNA']),
]));
"""
        self.assertEqual(correr_node(self, guion), [
            [False, [0, 0]],        # sin «CMA CGM» no es la nave: hasta 9051f43 bastaban las palabras sin prefijo
            [True, [1, 0]],         # con todas sus palabras, esa
            [True, [0, 1]],         # la que la trae, no la primera
            [False, [0, 0]],        # sin palabras, ninguna
            # Cada palabra, entera: hasta f68ce6c «ANNA» calzaba dentro de «SAVANNAH», y pulsaba la primera, [True, [1, 0]]
            # (CICLO-cola-seis-items.md).
            [True, [0, 1]],
        ])

    def test_itinerario_comodin_no_se_busca_como_nave(self):
        botones = ("button:has-text('Seleccionar'), button:has-text('Select'), button:has-text('Deseleccionar'), "
                   "button:has-text('Deselect')")

        class Pagina(PaginaCma):
            def evaluate(self, js, *a):
                if "getCard(" in js:
                    self.buscadas.append(a[0])
                return super().evaluate(js, *a)
        reg, _, _ = self.corrida()
        # Lo que la lectura recibe, entero: hasta 9051f43 también «sigToks», las palabras sin los prefijos de naviera, que
        # bastaban para calzar. La Ñ y las tildes son letras: hasta f68ce6c, «PIÑA» daba «PI» (CICLO-cola-seis-items.md).
        for nave, toks in (("LIBRE", []), ("AUTO", []), ("-", []), ("NAVE PRUEBA", ["NAVE", "PRUEBA"]),
                           ("CMA CGM NAVE PRUEBA", ["CMA", "CGM", "NAVE", "PRUEBA"]), ("CMA CGM", []),
                           ("CMA CGM PIÑA", ["CMA", "CGM", "PIÑA"])):
            buscadas = [{"toks": toks}]     # una lectura: sin el enlace «Cargar … siguientes resultados», no hay más
            with self.subTest(nave=nave):
                pagina = Pagina(visibles={botones}, js={"getCard": {"ok": False, "ofrecidas": ["NAVE OTRA"]}})
                pagina.buscadas = []
                if toks:
                    r = self.mod._cma_seleccionar_itinerario(pagina, {"fila": 15, "nave": nave, "viaje": ""}, reg)
                    self.assertIs(r[0], False)
                else:
                    # Un comodín no trae palabras de nave: la lectura no calza con ninguna ruta, y corta sin elegir.
                    # Hasta 9051f43 se buscaba «LIBRE» como nave, antes de ese corte; y hasta f68ce6c, «CMA CGM»
                    # buscaba ["CMA", "CGM"], que calzaba con toda ruta de CMA CGM (CICLO-cola-seis-items.md).
                    with self.assertRaises(self.mod.ObjetivoNoEncontrado):
                        self.mod._cma_seleccionar_itinerario(pagina, {"fila": 15, "nave": nave, "viaje": ""}, reg)
                self.assertEqual(pagina.buscadas, buscadas)

    def test_itinerario_carga_mas_hasta_encontrarla(self):
        # Si la nave no está, «Cargar N siguientes resultados» (_cma_ampliar), las veces que haga falta, con un tope; sin
        # palabras de nave, ninguna; si no aparece, el aviso dice hasta qué fecha buscó (decisión de Marcelo,
        # CICLO-ampliar-msc-y-cma.md). Hasta el encargo 33, una sola vez el primero con «mostrar más» (Nota H23).
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_cma_seleccionar_itinerario")
        bucle = [n for n in ast.walk(f) if isinstance(n, (ast.While, ast.For))]
        self.assertEqual([ast.unparse(n.test) for n in bucle if isinstance(n, ast.While)], ["True"])
        cuerpo = [ast.unparse(s) for s in next(n for n in bucle if isinstance(n, ast.While)).body]
        self.assertEqual(cuerpo[-5:], [
            "if not toks:\n    por_que = 'la fila no trae palabras de nave que buscar'\n    break",
            "if cargas >= AMPLIAR_MAX:\n    por_que = f'cargué más rutas {AMPLIAR_MAX} veces, el tope'\n    break",
            "por_que = _cma_ampliar(page, reg, _cma_contar_rutas(page))", "if por_que:\n    break", "cargas += 1"])
        self.assertNotIn("mostrar m", ast.unparse(f).lower())
        asignas = [ast.unparse(n) for n in ast.walk(f) if isinstance(n, ast.Assign)]
        self.assertIn("donde = _hasta_donde_busque(_cma_fechas(page), por_que)", asignas)
        self.assertEqual(self.mod.AMPLIAR_MAX, 12)

    def test_cargar_mas_por_su_texto(self):
        # «Cargar N siguientes resultados» (N cambia): el único enlace o botón a la vista con ese texto entero; lo pulsa y
        # espera más rutas; sin el enlace, o sin rutas nuevas, el portal no deja más (CICLO-ampliar-msc-y-cma.md).
        mod = self.mod

        class Pagina(soporte.PaginaFalsa):
            def __init__(self, enlaces, rutas, falla=False):
                super().__init__(texto=self.responder)
                self.enlaces, self.rutas, self.falla, self.clics, self.cuentas = list(enlaces), list(rutas), falla, [], 0

            def responder(self, js, *a):
                if js != mod._JS_CMA_CONTAR:
                    raise AssertionError("JavaScript inesperado")
                self.cuentas += 1
                return self.rutas.pop(0) if len(self.rutas) > 1 else self.rutas[0]

            def locator(self, sel):
                if sel == ":root":                   # la pregunta de si la página responde (encargo 55)
                    return soporte.RaizFalsa(self)
                pagina = self
                assert sel == "a, button, [role=link], [role=button]", sel

                class Enlace:
                    def __init__(self, texto, visible):
                        self.texto, self.visible = texto, visible

                    def is_visible(self):
                        return self.visible

                    def scroll_into_view_if_needed(self, **k):
                        pass

                    def click(self, **k):
                        if pagina.falla:
                            raise RuntimeError("tapado por otra capa")
                        pagina.clics.append(self.texto)

                class Filtro:
                    def filter(self, has_text=None):
                        self.hallados = [Enlace(t, v) for t, v in pagina.enlaces if has_text.search(t)]
                        return self

                    def count(self):
                        return len(self.hallados)

                    def nth(self, j):
                        return self.hallados[j]
                return Filtro()

        cargar = "Cargar 10 siguientes resultados"
        senuelos = [("Mostrar más viajes", True), ("Cargar más", True), ("Cargar siguientes resultados", True),
                    ("Cargar 5 siguientes resultados", False), ("Cargar 10 siguientes resultados y más", True)]
        espera = mod.CMA_ESPERA_MAS
        casos = (
            ([(cargar, True)] + senuelos, [10, 10, 20], "", [cargar], 3),
            (senuelos, [10], mod.CMA_SIN_ENLACE, [], 0),
            ([(cargar, True), ("  cargar 20 SIGUIENTES resultados ", True)], [10],
             "no pude ampliar la búsqueda: había 2 enlaces «Cargar … siguientes resultados» a la vista", [], 0),
            ([(cargar, True)], [10], f"pulsé «Cargar … siguientes resultados» y no llegaron rutas nuevas en {espera} s",
             [cargar], espera),
        )
        for k, (enlaces, rutas, esperado, clics, cuentas) in enumerate(casos):
            with self.subTest(k=k):
                reg, _, log = self.corrida(f"cma_cargar_{k}")
                p = Pagina(enlaces, rutas)
                self.assertEqual(mod._cma_ampliar(p, reg, 10), esperado)
                self.assertEqual((p.clics, p.cuentas), (clics, cuentas))
                if not esperado:
                    self.assertIn("búsqueda ampliada: 10 -> 20 rutas", log.read_text(encoding="utf-8"))
        reg, _, _ = self.corrida("cma_cargar_falla")
        self.assertEqual(mod._cma_ampliar(Pagina([(cargar, True)], [10], falla=True), reg, 10),
                         "no pude ampliar la búsqueda: el clic en «Cargar … siguientes resultados» falló (tapado por otra "
                         "capa)")
        self.assertEqual(espera, 20)
        # Dos motivos distintos: hasta 2044222, los dos cortes decían «el portal no deja ampliar más la búsqueda».
        self.assertEqual(mod.CMA_SIN_ENLACE, "ya no vi el enlace «Cargar … siguientes resultados»")

    def test_fechas_de_las_rutas(self):
        # La salida de cada tarjeta: la primera fecha de su .wrap-card, «Lunes, 05-oct-2026» (la forma medida en las
        # corridas del 24
        # y el 25-09), para decir hasta qué fecha buscó.
        d = datetime.date
        casos = (("Lunes, 06-oct-2026", d(2026, 10, 6)), ("Miércoles, 12-nov-2026", d(2026, 11, 12)),
                 ("viernes, 3-sept-2027", d(2027, 9, 3)), ("Lunes, 06-OCT-2026", d(2026, 10, 6)),
                 ("06-dic.-2026", d(2026, 12, 6)), ("Lunes, 31-feb-2026", None), ("Lunes, 06-oct.", None),
                 ("Monday, 06-oct-2026", d(2026, 10, 6)), ("Lunes, 06-xyz-2026", None), ("", None), (None, None))
        for texto, fecha in casos:
            with self.subTest(texto=texto):
                self.assertEqual(self.mod._cma_fecha_tarjeta(texto), fecha)
        guion = "const f = " + self.mod._JS_CMA_FECHAS + r""";
const tarjeta = (...fechas) => ({querySelector: (s) => (s === '.date' && fechas.length ? {textContent: ' ' + fechas[0] + ' '} : null)});
global.document = {querySelectorAll: (s) => (s === '.wrap-card'
  ? [tarjeta('Lunes, 06-oct-2026', 'Martes, 04-nov-2026'), tarjeta(), tarjeta('Viernes, 10-oct-2026')] : [])};
console.log(JSON.stringify(f()));
"""
        self.assertEqual(correr_node(self, guion), ["Lunes, 06-oct-2026", "", "Viernes, 10-oct-2026"])
        pagina = soporte.PaginaFalsa(texto=lambda js, *a: ["Lunes, 06-oct-2026", ""] if js == self.mod._JS_CMA_FECHAS else None)
        self.assertEqual(self.mod._cma_fechas(pagina), [d(2026, 10, 6), None])

    def test_js_contar_rutas(self):
        # Las rutas: sus botones «Seleccionar» o «Deseleccionar» a la vista, con el texto entero.
        guion = "const f = " + self.mod._JS_CMA_CONTAR + r""";
const b = (t, vis = true) => ({textContent: t, offsetParent: vis ? {} : null,
                               getBoundingClientRect: () => ({width: vis ? 9 : 0, height: vis ? 9 : 0})});
global.document = {querySelectorAll: () => [b('Seleccionar'), b(' Deseleccionar '), b('Select'), b('Seleccionar ruta'),
                                              b('Seleccionar', false), b('Cargar 10 siguientes resultados')]};
console.log(JSON.stringify(f()));
"""
        self.assertEqual(correr_node(self, guion), 3)

    # Los paneles falsos imitan la forma medida en la corrida del 2026-09-25 (CICLO-pendientes-con-evidencia.md): cada
    # campo es un bloque .el-form-item con su etiqueta (un div .el-form-item__label) y su input.
    PANELES_FALSOS = (
        "const bloque = (vis) => ([t, ph]) => { const hay = vis !== 'display:none';\n"
        "  const inp = {offsetParent: hay ? {} : null, placeholder: ph, clics: 0,\n"
        "               getBoundingClientRect: () => (hay ? {width: 9, height: 9} : {width: 0, height: 0}),\n"
        "               focus() {}, click() { this.clics++; }};\n"
        "  return {inp, querySelector: (s) => (s === '.el-form-item__label' && t !== null ? {textContent: t} : null),\n"
        "          querySelectorAll: (s) => (s === 'input' ? [inp] : [])}; };\n"
        "const armar = (ps) => ps.map(([vis, d, bs]) => ({vis, d, bloques: bs.map(bloque(vis))}));\n"
        "const dentro = (ps, p, q) => { for (let x = q; x; x = x.d === null ? null : ps[x.d]) {\n"
        "  if (x === p) return true; } return false; };\n"
        "const conectar = (ps, pagina) => {\n"
        "  for (const p of ps) Object.assign(p, {contains: (q) => dentro(ps, p, q),\n"
        "    getBoundingClientRect: () => (p.vis === 'display:none' ? {width: 0, height: 0} : {width: 300, height: 400}),\n"
        "    querySelectorAll: (s) => { const bs = ps.filter(q => dentro(ps, p, q)).flatMap(q => q.bloques);\n"
        "      return s === '.el-form-item' ? bs : s === 'input' ? bs.map(b => b.inp) : []; }});\n"
        "  global.getComputedStyle = (e) => ({visibility: e.vis === 'visibility:hidden' ? 'hidden' : 'visible'});\n"
        "  const todos = [...pagina, ...ps.flatMap(p => p.bloques)];\n"
        "  global.document = {querySelector: () => ps[0] || null,\n"
        "    querySelectorAll: (s) => (s === 'input' ? todos.map(b => b.inp) : s === '.el-form-item' ? todos : ps)}; };\n")

    def temperatura(self, paneles, pagina=()):
        """Corre _JS_CMA_REEFER_TEMPERATURA sobre paneles falsos. Cada panel es (visibilidad, dentro_de, bloques):
        la visibilidad es «visible», «display:none» o «visibility:hidden»; 'dentro_de', el índice del panel que lo
        contiene, o None; y cada bloque, (etiqueta, placeholder de su input), con None si no tiene etiqueta. 'pagina'
        son bloques visibles fuera de todo panel. Devuelve lo que responde, los clics de los input de cada panel y los
        de la página."""
        guion = (
            self.PANELES_FALSOS
            + f"const paneles = armar({json.dumps(paneles)});\n"
            + f"const pagina = {json.dumps(pagina)}.map(bloque('visible'));\n"
            + "conectar(paneles, pagina);\n"
            + "const f = " + self.mod._JS_CMA_REEFER_TEMPERATURA + ";\n"
            + "console.log(JSON.stringify([f('-20'), paneles.map(p => p.bloques.map(b => b.inp.clics)), "
            + "pagina.map(b => b.inp.clics)]));\n")
        return correr_node(self, guion)

    def test_js_temperatura_solo_por_su_etiqueta(self):
        v = "visible"
        # Medido en la corrida del 2026-09-25: entre los campos del panel, solo la etiqueta «Temperature» es la suya.
        medido = [("Modo Reefer", ""), ("Temperature", ""), ("Unidad", "Select"), ("Ventilación", ""),
                  ("Genset requerido", ""), (None, "")]
        self.assertEqual(self.temperatura([(v, None, medido)]), ["ok", [[0, 1, 0, 0, 0, 0]], []])
        self.assertEqual(self.temperatura([(v, None, [("Humedad", ""), ("Ventilación", "")])]),
                         ["sin-campo", [[0, 0]], []])
        # Ni su placeholder, ni un «°C» en otra etiqueta, ni la palabra dentro de otra etiqueta: hasta 1e8d510,
        # cualquiera de esos bastaba.
        self.assertEqual(self.temperatura([(v, None, [("Unidad", "Temperature"), ("Unidad (°C)", ""),
                                                      ("Pre-cooling temperature", "")])]),
                         ["sin-campo", [[0, 0, 0]], []])
        # Con dos campos «Temperature», no elige.
        self.assertEqual(self.temperatura([(v, None, [("Temperature", ""), (" Temperature ", "")])]),
                         ["varios-campos", [[0, 0]], []])

    def test_js_temperatura_solo_en_el_panel_visible(self):
        v, d, h = "visible", "display:none", "visibility:hidden"
        t = [("Temperature", "")]
        # Medido en la corrida del 2026-09-24: el primer contenedor de la página era un diálogo oculto.
        self.assertEqual(self.temperatura([(d, None, t), (v, None, [("Humedad", "")] + t)]),
                         ["ok", [[0], [0, 1]], []])
        # Sin un panel visible no busca en ningún otro lado: ni en los ocultos ni en la página.
        self.assertEqual(self.temperatura([(d, None, t), (h, None, t)], pagina=t), ["sin-panel", [[0], [0]], [0]])
        # Con más de uno visible, no elige.
        self.assertEqual(self.temperatura([(v, None, t), (v, None, t)]), ["varios-paneles", [[0], [0]], []])
        # Uno dentro de otro es un solo panel: el de afuera.
        self.assertEqual(self.temperatura([(v, None, []), (v, 0, t)]), ["ok", [[], [1]], []])

    def guardar(self, paneles, en):
        """Corre _JS_CMA_REEFER_GUARDAR con un botón falso dentro del panel 'en' (su índice, o None si está fuera de
        todo panel). Cada panel es (visibilidad, dentro_de), como en temperatura(). Devuelve lo que responde y los
        clics del botón."""
        guion = (
            self.PANELES_FALSOS
            + f"const paneles = armar({json.dumps([(vis, d, []) for vis, d in paneles])});\n"
            + "conectar(paneles, []);\n"
            + f"const boton = {{d: {json.dumps(en)}, clics: 0, click() {{ this.clics++; }}}};\n"
            + "const f = " + self.mod._JS_CMA_REEFER_GUARDAR + ";\n"
            + "console.log(JSON.stringify([f(boton), boton.clics]));\n")
        return correr_node(self, guion)

    def test_js_guardar_solo_si_es_del_panel_visible(self):
        v, d = "visible", "display:none"
        # El «Guardar» del único panel visible sí. El JavaScript no pulsa: solo dice si el botón es de ese panel.
        self.assertEqual(self.guardar([(v, None)], 0), [True, 0])
        # El de un cajón oculto no: hasta 1e8d510, el JavaScript pulsaba el primero de cualquier cajón.
        self.assertEqual(self.guardar([(d, None), (v, None)], 0), [False, 0])
        # Ni con dos paneles visibles, ni sin ninguno, ni fuera de todo panel.
        self.assertEqual(self.guardar([(v, None), (v, None)], 1), [False, 0])
        self.assertEqual(self.guardar([(d, None)], 0), [False, 0])
        self.assertEqual(self.guardar([(v, None)], None), [False, 0])
        # En un panel anidado dentro del visible, es del visible.
        self.assertEqual(self.guardar([(v, None), (v, 0)], 1), [True, 0])

    def test_reefer_corta_en_cada_paso_sin_pulsar_a_ciegas(self):
        f = self.mod._cma_ajustes_reefer
        abre, temp, del_panel = "button:has-text('Modifique el reefer')", "/^temperature$/i", "paneles[0].contains(boton)"
        principal = ".el-drawer .el-button--primary, [role='dialog'] .el-button--primary"
        guardar = ".el-drawer button, [class*='drawer'] button"
        # Medido en la corrida del 2026-09-24: la insignia «to complete», el encabezado «Detalles de la carga … Reefer»
        # y la fila «Reefer to complete» existen, pero ninguno abre el panel: sin el botón, no se pulsa nada.
        no_abren = {"div:has-text('Reefer') button", "text=/TO COMPLETE/i", "button:has-text('Reefer')",
                    "span:has-text('Reefer TO COMPLETE')"}
        pagina = PaginaCma(visibles=no_abren, js={"rOnly": True})
        e, _ = self.corta(f, pagina, {"fila": 5})
        self.assertEqual((e.paso, pagina.clics), ("Sección Reefer de CMA", []))
        # La temperatura, solo dentro del panel visible: los campos de la página con esa etiqueta o ese placeholder no
        # se tocan (hasta 1ed40f4 se buscaban ahí). Solo «ok» sigue.
        en_la_pagina = {"input[placeholder*='Temperature' i]", "input[placeholder*='temp' i]",
                        ".el-form-item:has-text('Temperature') input", ".el-drawer input"}
        campo = "el campo «Temperature» dentro del panel Reefer visible (por su etiqueta)"
        for falta, buscaba in (("sin-panel", "el panel Reefer: no hay ningún panel visible en la página"),
                               ("varios-paneles", "un solo panel Reefer: hay más de un panel visible y no elijo uno "
                                                  "a ciegas"),
                               ("sin-campo", campo), (True, campo),
                               ("varios-campos", "un solo campo «Temperature» en el panel Reefer: hay más de uno y no "
                                                 "elijo uno a ciegas")):
            with self.subTest(falta=falta):
                pagina = PaginaCma(visibles={abre} | en_la_pagina, js={temp: falta})
                e, log = self.corta(f, pagina, {"fila": 5})
                self.assertEqual((e.paso, e.buscaba, pagina.clics, pagina.teclas),
                                 ("Temperatura Reefer de CMA", buscaba, [abre], []))
                self.assertNotIn("temperatura reefer:", log)
        # Guardar: el «Guardar» a la vista, y solo si es del panel visible. Sin él, o si es de otro lado, no pulsa nada
        # (ni el botón principal de otra ventana). Hasta 1e8d510, el JavaScript pulsaba el de cualquier cajón.
        for visibles, es_del_panel in (({abre, principal}, True), ({abre, principal, guardar}, False)):
            with self.subTest(guardar_a_la_vista=guardar in visibles):
                pagina = PaginaCma(visibles=visibles, js={temp: "ok", del_panel: es_del_panel})
                e, log = self.corta(f, pagina, {"fila": 5})
                self.assertEqual((e.paso, e.buscaba, pagina.clics),
                                 ("Guardar los ajustes Reefer de CMA", "el botón «Guardar» del panel Reefer visible",
                                  [abre]))
                self.assertEqual(pagina.filtros, [(guardar, r"^\s*Guardar\s*$", True)])
                self.assertNotIn("guardados", log)
                self.assertIn("temperatura reefer: -20 °C (focus)", log)

    def test_ruta_sin_respuesta_no_se_da_por_validada(self):
        exito = "· Ruta validada con éxito. Continuando con datos de carga e itinerario..."
        sigue = "Sigo con los datos de carga e itinerario, sin darla por validada."
        casos = (("itinerarios", exito), ("aviso", exito),
                 ("indefinido", f"· ⚠ No pude confirmar la ruta: el portal no respondió a «Validar ruta». {sigue}"),
                 ("error", f"· ⚠ No pude confirmar la ruta: no pude pulsar «Validar ruta». {sigue}"))
        for resultado, esperado in casos:
            with self.subTest(resultado=resultado):
                reg, vistas, log = self.corrida(f"ruta_{resultado}")
                self.mod._cma_anunciar_ruta(reg, resultado)
                for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):
                    self.assertIn(esperado, donde)
                    if resultado in ("indefinido", "error"):
                        self.assertNotIn("validada con éxito", donde)

    def test_validar_devuelve_lo_que_vio_el_portal(self):
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_cma")
        validar = next(n for n in ast.walk(f) if isinstance(n, ast.FunctionDef) and n.name == "_validar")
        retornos = [ast.unparse(n.value) for n in ast.walk(validar) if isinstance(n, ast.Return) and n.value is not None]
        self.assertIn("_cma_esperar_resultado(page, 12, reg)", retornos)
        self.assertNotIn("'ok'", retornos)
        anuncios = [n for n in ast.walk(f) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "_cma_anunciar_ruta"]
        self.assertEqual([ast.unparse(n) for n in anuncios], ["_cma_anunciar_ruta(reg, estado)"])
        self.assertLess(anuncios[0].lineno, linea_guarda(f))

    def test_puerto_sin_codigo_no_elige_con_el_teclado(self):
        # Hasta fb63271, si el clic no dejaba el código del puerto, volvía a escribir y elegía con el teclado la
        # sugerencia que quedara primera (CICLO-cola-nueve-items.md).
        reg, _, log = self.corrida()
        pagina = PaginaCma()
        with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
            self.mod._cma_puerto(pagina, "#pol", "LIRQUEN, CHILE", reg, "Origen")
        self.assertEqual((e.exception.paso, e.exception.buscaba),
                         ("Origen de CMA", "la sugerencia del puerto «LIRQUEN» (por su texto) que deja el código del "
                                           "puerto en el campo"))
        self.assertEqual(pagina.teclas, ["Tab"])
        self.assertIn("Origen 'LIRQUEN': SIN codigo de puerto ('')", log.read_text(encoding="utf-8"))

        class ConCodigo(PaginaCma):
            def locator(s, sel):
                loc = LocFalso(s, sel)
                loc.input_value = lambda **k: "LIRQUEN ; CL ; CLLQN"
                return loc
        pagina = ConCodigo()
        self.assertIs(self.mod._cma_puerto(pagina, "#pol", "LIRQUEN, CHILE", reg, "Origen"), True)
        self.assertEqual(pagina.teclas, ["Tab"])
        self.assertIn("Origen 'LIRQUEN': LIRQUEN ; CL ; CLLQN", log.read_text(encoding="utf-8"))

    def test_tamano_y_mercancia_no_eligen_con_el_teclado(self):
        # Hasta fb63271, sin su opción por el texto, elegían con el teclado la que quedara ahí.
        pagina = PaginaCma(visibles={self.SELECCIONAR}, js={"high.*cube": ""})
        e, _ = self.corta(self.mod._cma_completar_info_extra, pagina, {"fila": 5})
        self.assertEqual((e.paso, e.buscaba, pagina.clics, pagina.teclas),
                         ("Tamaño y tipo de CMA", "la opción «40' Reefer High Cube» en el desplegable (por su texto)",
                          [self.SELECCIONAR], []))
        hs = "input[placeholder*='código HS' i]"
        pagina = PaginaCma(visibles={self.SELECCIONAR, self.OPCION, hs}, js={"peso por contenedor": True})
        e, _ = self.corta(self.mod._cma_completar_info_extra, pagina, {"fila": 5})
        self.assertEqual((e.paso, e.buscaba, pagina.clics[:2]),
                         ("Mercancía de CMA", "la sugerencia que dice «030313» en la lista (por su texto)",
                          [self.SELECCIONAR, self.OPCION]))
        self.assertFalse({"ArrowDown", "Enter"} & set(pagina.teclas))

    def js_comentarios(self):
        """El JavaScript de _cma_comentarios que busca el campo y escribe (va dentro de la función)."""
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_cma_comentarios")
        return next(a.value for c in ast.walk(f) if isinstance(c, ast.Call) for a in c.args
                    if isinstance(a, ast.Constant) and "allTa" in str(a.value))

    def test_js_comentarios_solo_en_su_campo(self):
        def correr(campos):
            guion = (
                "class TA { constructor([ph, etq]) { this.placeholder = ph; this.etq = etq; this._v = '';\n"
                "  this.offsetParent = {}; } closest() { return {textContent: this.etq}; }\n"
                "  scrollIntoView() {} focus() {} dispatchEvent() {} }\n"
                "Object.defineProperty(TA.prototype, 'value', {get() { return this._v; }, set(v) { this._v = v; }});\n"
                "global.window = {HTMLTextAreaElement: TA, getSelection: () => ({removeAllRanges() {}})};\n"
                f"const tas = {json.dumps(campos)}.map(c => new TA(c));\n"
                "global.document = {querySelectorAll: () => tas};\n"
                "const f = " + self.js_comentarios() + ";\n"
                "console.log(JSON.stringify([f('COMENTARIO'), tas.map(t => t.value)]));\n")
            return correr_node(self, guion)
        self.assertEqual(correr([["Buscar", "Filtro"], ["Por favor, facilítenos más datos", ""]]),
                         [True, ["", "COMENTARIO"]])
        self.assertEqual(correr([["", "Comentarios"]]), [True, ["COMENTARIO"]])
        # Sin un campo con ese placeholder o esa etiqueta, no escribe en ninguno: hasta fb63271, en el primero.
        self.assertEqual(correr([["Buscar", "Filtro"], ["", "Otro"]]), [False, ["", ""]])

    def test_comentarios_sin_su_campo_corta(self):
        pagina = PaginaCma(visibles={"textarea", ".el-textarea__inner"}, js={"allTa": False})
        e, _ = self.corta(self.mod._cma_comentarios, pagina)
        self.assertEqual((e.paso, pagina.clics), ("Comentarios de CMA", []))

    def test_i_agree_solo_por_su_texto(self):
        pagina = PaginaCma(visibles={"input[type='checkbox']"})
        e, _ = self.corta(self.mod._cma_marcar_i_agree, pagina)
        self.assertEqual((e.paso, pagina.clics), ("«I Agree» de CMA", []))
        reg, _, log = self.corrida()
        pagina = PaginaCma(visibles={"label:has-text('I Agree')", "input[type='checkbox']"})
        self.assertIs(self.mod._cma_marcar_i_agree(pagina, reg), True)
        self.assertEqual(pagina.clics, ["label:has-text('I Agree')"])
        self.assertIn("marcado 'I Agree'", log.read_text(encoding="utf-8"))


class MarcoCosco:
    """Marco falso del formulario de COSCO: responde a cada JavaScript del programa por su identidad; los
    clics de Playwright fallan si 'clics_fallan'."""

    def __init__(self, mod, respuestas, clics_fallan=False):
        self.mod, self.respuestas, self.clics_fallan, self.clics = mod, respuestas, clics_fallan, []

    def evaluate(self, js, *a):
        for nombre, r in self.respuestas.items():
            if js == getattr(self.mod, nombre):
                return r
        return None

    def click(self, sel, timeout=None):
        if self.clics_fallan:
            raise RuntimeError("el clic no salió")
        self.clics.append(sel)


class MarcoSemanas:
    """Marco falso de «Sailing Within N Weeks» de COSCO: responde _JS_COSCO_SEMANAS con el estado ('campos' a la vista,
    las semanas 'actual' y la opción más larga, 'tope'), y los clics reales abren el desplegable y eligen la opción
    marcada. Con 'oculta', las opciones no están hasta abrirlo; con 'sin_marca', no se ve una sola; con 'no_cambia', el
    clic en la opción no cambia el valor; con 'falla', el primer clic falla."""

    def __init__(self, mod, campos=1, actual=2, tope=8, oculta=False, sin_marca=False, no_cambia=False, falla=False):
        self.mod, self.campos, self.actual, self.tope = mod, campos, actual, tope
        self.oculta, self.sin_marca, self.no_cambia, self.falla = oculta, sin_marca, no_cambia, falla
        self.abierto, self.marca, self.clics = False, "", []

    def evaluate(self, js, marcar=""):
        if js != self.mod._JS_COSCO_SEMANAS:
            raise AssertionError("JavaScript inesperado en «Sailing Within»")
        if self.campos != 1:
            return {"campos": self.campos}
        mayor = None if self.oculta and not self.abierto else self.tope
        r = {"campos": 1, "actual": self.actual, "mayor": mayor, "marcada": False}
        self.marca = ""
        if marcar == "campo" or (marcar == "opcion" and self.abierto and not self.sin_marca and mayor is not None):
            self.marca, r["marcada"] = marcar, True
        return r

    def click(self, sel, timeout=None):
        if self.falla:
            raise RuntimeError("el clic no salió")
        self.clics.append(sel)
        if self.marca == "campo":
            self.abierto = True
        elif self.marca == "opcion" and not self.no_cambia:
            self.actual = self.tope


class MarcoLista:
    """Marco falso de la lista de itinerarios de COSCO: cada lectura de _JS_COSCO_LISTA_NAVES da la siguiente de
    'lecturas' (la última, siempre); nunca dice que no hay itinerarios."""

    def __init__(self, mod, lecturas):
        self.mod, self.lecturas = mod, list(lecturas)

    def evaluate(self, js, *a):
        if js == self.mod._JS_COSCO_LISTA_NAVES:
            return self.lecturas.pop(0) if len(self.lecturas) > 1 else self.lecturas[0]
        return False


class MarcoOrigen:
    """Marco falso de «Origin City» de COSCO, con la forma del autocompletado que usa el programa: _JS_COSCO_AUTO_SET
    escribe el texto en el campo de su placeholder, y _JS_COSCO_AUTO_PICK devuelve la sugerencia elegida para el texto
    que busca, o nada. Ofrece la de 'sugerencias' solo si se escribe en «origin ci» y se pide una de Chile, y anota cada
    texto que se escribió."""

    def __init__(self, mod, sugerencias):
        self.mod, self.sugerencias, self.escritos = mod, sugerencias, []

    def wait_for_timeout(self, ms):
        pass

    def evaluate(self, js, arg=None):
        if js == self.mod._JS_COSCO_AUTO_SET:
            self.escritos.append(arg[1])
            return "set" if arg[0] == "origin ci" else "no-input"
        if js == self.mod._JS_COSCO_AUTO_PICK:
            return self.sugerencias.get(arg[0], "") if arg[1] is True else ""
        raise AssertionError("JavaScript inesperado en Origin City")


class TestCosco(ConRegistro):
    def test_puerto_de_carga_sin_sugerencia_corta(self):
        # El puerto de carga es el de la fila (su celda normalizada por _cosco_puerto_de_la_celda y traducida por
        # MAPA_PUERTOS_COSCO o, si no está ahí, tal como quedó al normalizarla), con una sugerencia de Chile en «Origin
        # City». Si COSCO no la ofrece, o la celda no trae el puerto, corta sin elegir nada (decisiones de Marcelo,
        # CICLO-cola-seis-items.md y CICLO-inicio-de-todas.md).
        reg, _, _ = self.corrida()
        f = self.mod._cosco_puerto_de_carga
        m = MarcoOrigen(self.mod, {"San Antonio": "SAN ANTONIO, CHILE", "Lirquen": "LIRQUEN, CHILE"})
        self.assertEqual((f(m, {"pol": "SAN ANTONIO"}, reg), m.escritos), ("San Antonio", ["San Antonio"]))
        self.assertEqual(f(m, {"pol": "Coronel"}, reg), "Lirquen")
        m = MarcoOrigen(self.mod, {"PUERTO ALFA": "PUERTO ALFA, CHILE"})
        self.assertEqual((f(m, {"pol": "PUERTO ALFA, CHILE"}, reg), m.escritos), ("PUERTO ALFA", ["PUERTO ALFA"]))
        # Sin sugerencia para el de la fila, corta aunque el puerto fijo sí la tenga: hasta f68ce6c escribía «Lirquen»
        # y seguía con él.
        m = MarcoOrigen(self.mod, {"Lirquen": "LIRQUEN, CHILE"})
        with self.assertRaises(self.mod.ObjetivoNoEncontrado) as c:
            f(m, {"pol": "PUERTO ALFA"}, reg)
        self.assertEqual((c.exception.paso, c.exception.buscaba),
                         ("Origin City de COSCO", "una sugerencia de Chile para el puerto de carga «PUERTO ALFA»"))
        self.assertEqual(set(m.escritos), {"PUERTO ALFA"})
        # Si el mapa la tradujo, el motivo trae también la celda de la fila; si es el mismo puerto, no.
        m = MarcoOrigen(self.mod, {})
        with self.assertRaises(self.mod.ObjetivoNoEncontrado) as c:
            f(m, {"pol": "SAN ANTONIO"}, reg)
        self.assertEqual(c.exception.buscaba, "una sugerencia de Chile para el puerto de carga «San Antonio»")
        with self.assertRaises(self.mod.ObjetivoNoEncontrado) as c:
            f(m, {"pol": "CORONEL"}, reg)
        self.assertEqual(c.exception.buscaba,
                         "una sugerencia de Chile para el puerto de carga «Lirquen» (en la fila, «CORONEL»)")
        # La celda se normaliza antes del mapa: la parte antes de la primera coma, en mayúsculas, sin tildes, con todo
        # signo como separador, y sin el país al final, «CHILE» o «CL» (_cosco_puerto_de_la_celda,
        # CICLO-inicio-de-todas.md; «CL», decisión de Marcelo, encargo 46: hasta ahí COSCO buscaba «CORONEL CL»).
        # Hasta c4df3ab, «CORONEL, CHILE» y «Lirquén» no se traducían: se buscaban «CORONEL» y «Lirquén», y la de tilde
        # no calza con las sugerencias de COSCO, que no la llevan.
        m = MarcoOrigen(self.mod, {"Lirquen": "LIRQUEN, CHILE", "PUERTO ALFA": "PUERTO ALFA, CHILE",
                                   "San Vicente": "SAN VICENTE, CHILE"})
        for celda, buscado in (("CORONEL, CHILE", "Lirquen"), ("Coronel (Chile)", "Lirquen"), ("CORONEL - CHILE", "Lirquen"),
                               ("CORONEL CHILE", "Lirquen"), ("CORONEL – CHILE", "Lirquen"), ("CORONEL–CHILE", "Lirquen"),
                               ("CORONEL — CHILE", "Lirquen"), ("CORONEL · CHILE", "Lirquen"), ("Lirquén", "Lirquen"),
                               ("LIRQUÉN, CHILE", "Lirquen"), ("Concepción", "Lirquen"), ("CORONEL, BIOBIO, CHILE", "Lirquen"),
                               ("San  Vicente,  Chile", "San Vicente"), ("San Vicente, Talcahuano", "San Vicente"),
                               ("Puerto Álfa, Chile", "PUERTO ALFA"), ("puerto alfa", "PUERTO ALFA"),
                               ("CORONEL CHILE CHILE", "Lirquen"), ("CORONEL CL", "Lirquen"),
                               ("Coronel - CL", "Lirquen"), ("CORONEL CHILE CL", "Lirquen"),
                               ("CORONEL CL CHILE", "Lirquen"), ("Puerto Álfa (CL)", "PUERTO ALFA")):
            with self.subTest(celda=celda):
                self.assertEqual(f(m, {"pol": celda}, reg), buscado)
        # «CHILE» sale solo al final: en medio del nombre es parte del puerto. Y la celda con solo el país da vacío:
        # desde la revisión final del encargo 42, _puerto_de_carga la corta igual (no mira «CHILE» en ninguna
        # posición), así que el contrato de la normalización se prueba aquí, directo.
        self.assertEqual(self.mod._cosco_puerto_de_la_celda("PUERTO CHILE ALFA"), "PUERTO CHILE ALFA")
        self.assertEqual(self.mod._cosco_puerto_de_la_celda("PUERTO CL ALFA"), "PUERTO CL ALFA")
        for celda in ("CHILE", "Chile (Chile)", "CHILE CHILE", "CL", "CL CL", "Chile - CL"):
            with self.subTest(normalizada=celda):
                self.assertEqual(self.mod._cosco_puerto_de_la_celda(celda), "")
        # Con el puerto normalizado distinto de la celda, el motivo trae también la celda.
        m = MarcoOrigen(self.mod, {})
        with self.assertRaises(self.mod.ObjetivoNoEncontrado) as c:
            f(m, {"pol": "Puerto Álfa"}, reg)
        self.assertEqual(c.exception.buscaba,
                         "una sugerencia de Chile para el puerto de carga «PUERTO ALFA» (en la fila, «Puerto Álfa»)")
        # Sin el puerto en la celda, corta sin escribir nada: hasta f68ce6c buscaba el texto vacío, que calza con
        # cualquier sugerencia de Chile. Con solo el país, lo mismo: hasta c4df3ab buscaba «CHILE», que calza igual.
        for celda in ("  ", ", CHILE", "CHILE", "(Chile)", " - ", "CHILE CHILE", "Chile (Chile)", "–"):
            with self.subTest(celda=celda):
                m = MarcoOrigen(self.mod, {"": "OTRO PUERTO, CHILE", "Lirquen": "LIRQUEN, CHILE"})
                with self.assertRaises(self.mod.ObjetivoNoEncontrado) as c:
                    f(m, {"pol": celda}, reg)
                self.assertEqual((c.exception.buscaba, m.escritos),
                                 ("el puerto de carga en la fila (la celda no trae su nombre; escríbelo en la planilla)", []))

    def test_reservar_cosco_elige_el_puerto_de_carga_con_el_ayudante(self):
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_cosco")
        self.assertEqual([ast.unparse(n) for n in ast.walk(f) if isinstance(n, ast.Assign)
                          and ast.unparse(n.targets[0]) == "pol_ciudad"],
                         ["pol_ciudad = _cosco_puerto_de_carga(frame, reserva, reg)"])
        # Ningún «Lirquen» escrito en reservar_cosco: el único que queda está en MAPA_PUERTOS_COSCO, que traduce el
        # puerto de la celda ya normalizado. Hasta f68ce6c era el respaldo.
        self.assertNotIn("Lirquen", ast.unparse(f))

    def test_puerto_traducido_lo_dicen_el_log_y_el_motivo(self):
        # MAPA_PUERTOS_COSCO se mantiene, pero cuando traduce el puerto de carga de la fila a otro puerto, log.txt y el
        # motivo de la reserva dicen desde qué puerto se armó (decisión de Marcelo, encargo 50,
        # CICLO-msc-segundo-intento.md). La tarde del 02-10, COSCO armó su reserva desde otro puerto que el de su
        # fila, y solo lo decía el campo del formulario (CICLO-corridas-de-la-tarde-02-10.md). Si el mapa solo cambia
        # cómo se escribe el mismo puerto, no dice nada.
        f = self.mod._cosco_traduccion
        for celda, otro in (("CORONEL", "Lirquen"), ("Coronel, Chile", "Lirquen"), ("PUERTO CORONEL", "Lirquen"),
                            ("Concepción", "Lirquen"), ("CORONEL CL", "Lirquen"), ("LIRQUEN", ""),
                            ("Lirquén, Chile", ""), ("PUERTO LIRQUEN", ""), ("San Antonio", ""),
                            ("SAN VICENTE, TALCAHUANO", ""), ("Valparaíso", ""), ("PUERTO ALFA", ""), ("", ""),
                            ("CHILE", "")):
            with self.subTest(celda=celda):
                self.assertEqual(f(celda), otro)
        reg, vistas, log = self.corrida("cosco_traducido")
        m = MarcoOrigen(self.mod, {"Lirquen": "LIRQUEN, CHILE"})
        self.assertEqual(self.mod._cosco_puerto_de_carga(m, {"pol": "Coronel, Chile", "fila": 8}, reg), "Lirquen")
        aviso = ("· ⚠ COSCO: el puerto de carga de la fila, «Coronel, Chile», lo traduce MAPA_PUERTOS_COSCO a "
                 "«Lirquen»: la reserva se arma desde «Lirquen».")
        nota = "puerto de carga: COSCO la arma desde «Lirquen»; la fila dice «Coronel, Chile» (MAPA_PUERTOS_COSCO)"
        for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):
            self.assertIn(aviso, donde)
        self.assertEqual(vars(reg).pop("cosco_puerto"), nota)
        # El mismo puerto con otra forma: ni aviso ni nota.
        self.assertEqual(self.mod._cosco_puerto_de_carga(m, {"pol": "LIRQUEN", "fila": 8}, reg), "Lirquen")
        self.assertNotIn("cosco_puerto", vars(reg))
        self.assertEqual(log.read_text(encoding="utf-8").count("lo traduce MAPA_PUERTOS_COSCO"), 1)
        # Sin una sugerencia para el puerto traducido, corta como antes, sin la nota: su motivo ya trae la celda.
        with self.assertRaises(self.mod.ObjetivoNoEncontrado):
            self.mod._cosco_puerto_de_carga(MarcoOrigen(self.mod, {}), {"pol": "CORONEL", "fila": 8}, reg)
        self.assertNotIn("cosco_puerto", vars(reg))

        # El decorador suma la nota al motivo de la reserva, sea cual sea su estado, también al de un paso sin su
        # objetivo; borra la que quedó de otra reserva; y sin nota deja el motivo como está.
        def con_nota(estado, detalle, corta=False):
            def reservar(page, reserva, creds, reg, on_pausa=None):
                reg.cosco_puerto = nota
                if corta:
                    raise self.mod.ObjetivoNoEncontrado("Destination de COSCO", "una sugerencia que elegir para «X»")
                return estado, detalle
            return self.mod._con_el_puerto_de_cosco(self.mod._sin_clic_a_ciegas("cosco")(reservar))
        pagina = soporte.PaginaFalsa(texto=lambda js, *a: {"html": "<body>sintetica</body>", "sombras": 0})
        armada = "COSCO armada hasta Booking Details (ETD X); SIN emitir"
        self.assertEqual(con_nota("OK-EJEMPLO", armada)(pagina, {"fila": 8}, {}, reg),
                         ("OK-EJEMPLO", f"{armada} · {nota}"))
        estado, detalle = con_nota("", "", corta=True)(pagina, {"fila": 8}, {}, reg)
        self.assertEqual((estado, detalle.endswith(f"revisa ese paso en el portal. · {nota}")), ("NO ENVIADA", True))
        sin_nota = self.mod._con_el_puerto_de_cosco(lambda page, reserva, creds, reg, on_pausa=None: ("REVISAR", "x"))
        reg.cosco_puerto = nota                         # la nota que quedó de otra reserva
        self.assertEqual(sin_nota(pagina, {"fila": 8}, {}, reg), ("REVISAR", "x"))
        self.assertNotIn("cosco_puerto", vars(reg))
        # reservar_cosco lo lleva por fuera de todos, y así por fuera de los cortes.
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        g = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_cosco")
        self.assertEqual([ast.unparse(d) for d in g.decorator_list],
                         ["_con_el_puerto_de_cosco", "_con_la_nave_de_la_fila", "_con_la_ruta_de_la_fila",
                          "_sin_clic_a_ciegas('cosco')"])

    def test_sin_formulario_queda_no_enviada_con_evidencia(self):
        # New Booking sin su formulario: sin su marco bkg2, o con el marco y sin el campo «Origin City» en 20 vueltas.
        # La reserva queda NO ENVIADA, con lo que faltó y los segundos desde que abrió New Booking, y deja la captura de
        # la ventana y el HTML de la página y de sus marcos (decisión de Marcelo, encargo 48,
        # CICLO-calendario-cosco-y-cma.md). Hasta ahí quedaba REVISAR, y el HTML no se guardaba (sin los campos, solo
        # con AQUASHIELD_DESCUBRIR): así quedó el 2026-10-02, sin poder medir qué mostraba.
        reserva = {"fila": 9, "pol": "PUERTO ALFA, CHILE", "destino_orig": "PUERTO BETA",
                   "destino_final": "CIUDAD GAMMA", "nave": "NAVE PRUEBA UNO", "viaje": "", "dia_carga": "",
                   "cotizacion": ""}
        fin = "; no pulsé nada y la reserva no se envió"
        sin_marco = "no apareció el marco de su formulario (bkg2)"
        sin_campos = "su formulario (el marco bkg2) no mostró sus campos («Origin City»)"
        # Un reloj que avanzan las esperas (revisión del encargo 48): la carga de New Booking, 3,7 s; sin el marco,
        # su búsqueda, 18 s (12 de 1,5); y cada vuelta sin los campos, 1,5 s.
        for que, segundos in ((sin_marco, 22), (sin_campos, 34)):
            with self.subTest(que=que):
                marco = MarcoSinCampos(self.mod) if que == sin_campos else None
                pagina, esperas, reloj = PaginaNewBooking(self.mod, marco), [], [1000.0]

                def avanza(seg, devuelve=None):
                    reloj[0] += seg
                    return devuelve

                def esperar(page, seg, *a, **k):
                    esperas.append(seg)
                    avanza(seg)
                reg, vistas, log = self.corrida("sin_formulario_" + ("campos" if marco else "marco"))
                with mock.patch.multiple(self.mod, _cosco_esperar_contenido=lambda *a, **k: avanza(3.7),
                                         _cosco_frame=lambda *a, **k: marco or avanza(18), esperar=esperar), \
                        mock.patch.object(self.mod.time, "monotonic", lambda: reloj[0]):
                    r = self.mod.reservar_cosco(pagina, dict(reserva), {"contrato": "CT-PRUEBA"}, reg)
                self.assertEqual(r, ("NO ENVIADA", f"COSCO: abrí New Booking y {que} en {segundos} s{fin}"))
                self.assertEqual((pagina.prohibidos, pagina.esperas, marco.prohibidos if marco else []), ([], 0, []))
                # La captura de siempre (de la ventana, salvo con AQUASHIELD_CAPTURA_FULL) y la de la evidencia.
                antes = [("cosco_f9_1_choose.png", False)] if marco else [("cosco_f9_err.png", False)]
                self.assertEqual(pagina.capturas, antes + [("cosco_f9_sin_formulario.png", False)])
                self.assertEqual(sorted(p.name for p in log.parent.iterdir() if p.suffix == ".html"),
                                 ["cosco_f9_sin_formulario.html"]
                                 + (["cosco_f9_sin_formulario_marco1.html"] if marco else []))
                self.assertEqual((pagina.abiertas, esperas, marco.cuentas if marco else 0),
                                 (["https://elines.coscoshipping.com/ebusiness/bookingrequest/"],
                                  [1.5] * 20 if marco else [], 20 if marco else 0))
                total = 2 if marco else 1
                for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):
                    self.assertIn(f"· ✗ NO ENVIADA · {r[1]}", donde)
                    self.assertIn(f"evidencia sin el formulario de New Booking: cosco_f9_sin_formulario.png y "
                                  f"{total} de {total} HTML", donde)
        # Los segundos, desde 'desde' (time.monotonic), con el reloj fijo.
        reg, _, _ = self.corrida("sin_formulario_segundos")
        with mock.patch.object(self.mod.time, "monotonic", lambda: 135.4):
            r = self.mod._cosco_sin_formulario(PaginaNewBooking(self.mod), reg, 8, sin_marco, 100.0)
        self.assertEqual(r, ("NO ENVIADA", f"COSCO: abrí New Booking y {sin_marco} en 35 s{fin}"))

    def test_revisar_solo_si_la_nave_no_esta(self):
        # En reservar_cosco, REVISAR queda solo para la nave no encontrada (decisión de Marcelo, encargo 48): sin el
        # formulario de New Booking, NO ENVIADA (test_sin_formulario_queda_no_enviada_con_evidencia).
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_cosco")
        revisar = [ast.unparse(n) for n in ast.walk(f) if isinstance(n, ast.Return) and "'REVISAR'" in ast.unparse(n)]
        self.assertEqual(len(revisar), 1)
        self.assertIn("no está en COSCO", revisar[0])

    def test_js_perfil_dice_si_pulso(self):
        def correr(hay, falla):
            guion = (
                f"const cb = {{clics: 0, scrollIntoView() {{}}, click() {{ if ({json.dumps(falla)}) throw new Error('x'); "
                "this.clics++; }};\n"
                "const lab = {offsetParent: {}, textContent: 'Copy from my profile', tagName: 'LABEL', "
                "querySelector: () => cb};\n"
                f"global.document = {{querySelectorAll: () => {json.dumps(hay)} ? [lab] : []}};\n"
                "const f = " + self.mod._JS_COSCO_COPIAR_PERFIL + ";\n"
                "console.log(JSON.stringify([f(), cb.clics]));\n")
            return correr_node(self, guion)
        self.assertEqual(correr(True, False), ["ok", 1])
        self.assertEqual(correr(True, True), ["fallo", 0])
        self.assertEqual(correr(False, False), ["no", 0])

    def test_js_pulsar_opcion_dice_si_pulso(self):
        def correr(hay):
            guion = ("const op = {clics: 0, click() { this.clics++; }};\n"
                     f"global.document = {{querySelector: () => {json.dumps(hay)} ? op : null}};\n"
                     "const f = " + self.mod._JS_COSCO_PULSAR_OPCION + ";\n"
                     "console.log(JSON.stringify([f(), op.clics]));\n")
            return correr_node(self, guion)
        self.assertEqual(correr(True), [True, 1])
        self.assertEqual(correr(False), [False, 0])

    def test_opcion_solo_se_anuncia_si_se_pulso(self):
        reg, _, log = self.corrida()
        base = {"_JS_COSCO_ETQ_LEER": "", "_JS_COSCO_MARCAR": "ok", "_JS_COSCO_MARCAR_OPCION": "CY"}
        marco = MarcoCosco(self.mod, dict(base, _JS_COSCO_PULSAR_OPCION=False), clics_fallan=True)
        self.assertIs(self.mod._cosco_select_etq(soporte.PaginaFalsa(), marco, "Door Pickup", "CY", reg), False)
        texto = log.read_text(encoding="utf-8")
        self.assertIn("Door Pickup: no pude pulsar la opción 'CY'", texto)
        self.assertNotIn("Door Pickup = ", texto)
        marco = MarcoCosco(self.mod, dict(base, _JS_COSCO_PULSAR_OPCION=True), clics_fallan=True)
        self.assertIs(self.mod._cosco_select_etq(soporte.PaginaFalsa(), marco, "Door Pickup", "CY", reg), True)
        self.assertIn("Door Pickup = 'CY'", log.read_text(encoding="utf-8"))

    def test_autocompletar_no_elige_con_el_teclado(self):
        # Hasta fb63271, si el clic y los eventos de puntero no dejaban elegida la sugerencia, elegía con el teclado
        # (flecha abajo y Enter) la opción que quedara ahí. 0 veces en los logs medidos: las 25 sugerencias quedaron
        # con el primer clic (CICLO-cola-nueve-items.md).
        reg, _, _ = self.corrida()
        teclas = []
        pagina = soporte.PaginaFalsa()
        pagina.keyboard = types.SimpleNamespace(type=lambda t, delay=None: teclas.append(t), press=teclas.append)
        marco = MarcoCosco(self.mod, {"_JS_COSCO_ETQ_FOCO": "ok", "_JS_COSCO_ETQ_LEER": "",
                                      "_JS_COSCO_MARCAR_AUTO_OPCION": {"texto": "FROZEN SALMON"}})
        with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
            self.mod._cosco_auto_etq(pagina, marco, "Cargo Descriptions", "FROZ", "FROZEN ATLANTIC SALMON", reg)
        self.assertEqual((e.exception.paso, e.exception.buscaba),
                         ("Cargo Descriptions de COSCO", "la sugerencia «FROZEN SALMON» elegida en el campo (el clic y "
                                                         "los eventos de puntero no la dejaron; con el teclado sería a "
                                                         "ciegas)"))
        self.assertEqual((teclas, marco.clics), (["FROZ"], ["[data-aq-op]"]))

    def test_itinerario_la_proxima_salida_nunca_el_primero(self):
        # Decisión de Marcelo (CICLO-proxima-salida.md): la próxima salida desde hoy, o desde el día de carga si la fila
        # lo trae y es posterior. Hasta 135e765: la única con «ETD» igual al día de carga, y esa ETD era el CY Cutoff.
        hoy = datetime.date.today()
        dia = lambda n: (hoy + datetime.timedelta(days=n)).isoformat()
        a, b, c = {"i": 0, "etd": dia(10)}, {"i": 1, "etd": dia(3)}, {"i": 2, "etd": dia(3)}
        pasada, sin = {"i": 3, "etd": dia(-2)}, {"i": 4, "etd": ""}
        # Un día de carga posterior cuyo día del mes pasa de 12: leído con el mes primero, no sería una fecha.
        carga = next(hoy + datetime.timedelta(days=k) for k in range(4, 40) if (hoy + datetime.timedelta(days=k)).day > 12)
        tras_carga = {"i": 5, "etd": (carga + datetime.timedelta(days=5)).isoformat()}
        casos = (([tras_carga, b], carga.strftime("%d-%m-%Y"), (tras_carga, "")),         # DD-MM-AAAA, el día primero
                 ([tras_carga, b], carga.isoformat() + " 00:00:00", (tras_carga, "")),   # con hora (camino de consola)
                 ([a], "", (a, "")),                    # uno solo: ese
                 ([sin], "", (sin, "")),                # uno solo, aunque su tarjeta no traiga la salida
                 ([a, b], "", (b, "")),                 # la próxima, aunque no sea la primera de la lista
                 ([pasada, a], "", (a, "")),            # los que ya salieron no cuentan
                 ([pasada], "", (None, "ninguna")),
                 ([b, c], "", (None, "empate")),        # la misma salida con otro transbordo: no se elige
                 ([b, c, a], "", (None, "empate")),
                 ([a, sin], "", (None, "sin-fecha")),   # no se pueden ordenar
                 ([a, b], dia(5), (a, "")),             # desde el día de carga, si la fila lo trae y es posterior
                 ([a, b], "2020-01-01", (b, "")),       # uno pasado no cuenta: desde hoy
                 ([a, b], "por confirmar", (b, "")))    # ilegible: desde hoy
        for cand, dia_carga, (elegido, motivo) in casos:
            with self.subTest(itinerarios=len(cand), dia=dia_carga):
                r = self.mod._cosco_elegir_itinerario(cand, {"dia_carga": dia_carga})
                self.assertEqual(r[1], motivo)
                self.assertIs(r[0], elegido)

    def test_transito_y_desempate(self):
        # El tiempo de tránsito es la llegada menos la salida de la tarjeta («Nov15 (Sun)»): en las 4 tarjetas medidas,
        # el «N Days» que muestran (CICLO-cola-tres-items.md).
        hoy = datetime.date.today()
        d = lambda n: hoy + datetime.timedelta(days=n)
        meses = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
        dias = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
        tarjeta = lambda x: f"{meses[x.month - 1]}{x.day:02d} ({dias[x.weekday()]})"
        uno = {"i": 0, "etd": d(3).isoformat(), "llegada": tarjeta(d(51))}
        dos = {"i": 1, "etd": d(3).isoformat(), "llegada": tarjeta(d(45))}
        self.assertEqual(self.mod._cosco_transito(uno), datetime.timedelta(days=48))
        for x in (dict(uno, llegada=""), dict(uno, etd=""), dict(uno, llegada=tarjeta(d(3))),
                  dict(uno, llegada=tarjeta(d(1))), {}):
            with self.subTest(itinerario=x):
                self.assertIsNone(self.mod._cosco_transito(x))
        # La misma salida con otro transbordo: la que llega antes, aunque tenga más transbordos (no cuentan). Hasta
        # 2825153, empate.
        dos = dict(dos, naves=["CSCL ALFA 001E", "NAVE PRUEBA 002W"])
        self.assertIs(self.mod._cosco_elegir_itinerario([dict(uno, naves=["NAVE PRUEBA 001E"]), dos], {})[0], dos)
        self.assertEqual(self.mod._cosco_elegir_itinerario([uno, dict(dos, llegada=tarjeta(d(51)))], {}),
                         (None, "empate"))

    def test_itinerario_ambiguo_queda_no_enviada_con_evidencia(self):
        hoy = datetime.date.today()
        d = lambda n: hoy + datetime.timedelta(days=n)
        uno = {"i": 0, "etd": d(3).isoformat(), "servicios": ["SRV1"], "naves": ["NAVE PRUEBA 001E"]}
        dos = {"i": 1, "etd": d(3).isoformat(), "servicios": ["SRV2"], "naves": ["NAVE PRUEBA 001E"]}
        meses = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
        dias = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
        tarjeta_cosco = lambda x: f"{meses[x.month - 1]}{x.day:02d} ({dias[x.weekday()]})"
        vistos = (f"itinerarios que calzan: servicio SRV1 · nave NAVE PRUEBA 001E · ETD {d(3).isoformat()} | servicio "
                  f"SRV2 · nave NAVE PRUEBA 001E · ETD {d(3).isoformat()}")
        # Hasta 2825153 el motivo terminaba en «…la próxima salida desde el …»; ahora dice también por qué el tiempo de
        # tránsito no desempató: estas tarjetas sintéticas no lo traen (CICLO-cola-tres-items.md).
        casos = (([uno, dos], "empate", f"2 de las 2 opciones salen el {d(3):%d-%m-%Y}, la próxima salida desde el "
                                        f"{hoy:%d-%m-%Y}, y no pude leer el tiempo de tránsito de 2 de ellas"),
                 # El mismo tránsito, legible: lo dice (CICLO-cola-tres-items.md).
                 ([dict(uno, llegada=tarjeta_cosco(d(51))), dict(dos, llegada=tarjeta_cosco(d(51)))], "empate",
                  f"2 de las 2 opciones salen el {d(3):%d-%m-%Y}, la próxima salida desde el {hoy:%d-%m-%Y}, y 2 de ellas "
                  "tienen el menor tiempo de tránsito, 48 días"),
                 ([uno, dict(dos, etd="")], "sin-fecha", "no pude leer la fecha de salida de 1 de las 2 opciones"),
                 ([dict(uno, etd=d(-1).isoformat()), dict(dos, etd=d(-5).isoformat())], "ninguna",
                  f"las 2 opciones salen antes del {hoy:%d-%m-%Y}"),
                 ([dict(uno, etd=d(-1).isoformat())], "ninguna", f"la única opción sale antes del {hoy:%d-%m-%Y}"))
        # Con día de carga posterior (DD-MM-AAAA, día del mes mayor que 12), el motivo se cuenta desde ese día.
        carga = next(d(k) for k in range(4, 40) if d(k).day > 12)
        antes = [dict(uno, etd=(carga - datetime.timedelta(days=1)).isoformat()),
                 dict(dos, etd=(carga - datetime.timedelta(days=2)).isoformat())]
        casos += ((antes, "ninguna", f"las 2 opciones salen antes del {carga:%d-%m-%Y}", carga.strftime("%d-%m-%Y")),)
        casos = tuple(c if len(c) == 4 else c + ("",) for c in casos)
        for n, (cand, motivo, por_que, dia_carga) in enumerate(casos):
            with self.subTest(motivo=motivo, itinerarios=len(cand), dia=dia_carga):
                reg, vistas, log = self.corrida(f"itinerarios_{n}")
                pagina = soporte.PaginaFalsa(texto=lambda js, *a: {"html": "<body>lista sintetica</body>", "sombras": 0}
                                             if js == self.mod._JS_HTML_COMPLETO else None)
                reserva = {"fila": 20, "nave": "NAVE PRUEBA", "dia_carga": dia_carga}
                detalle = (f"COSCO: no elegí itinerario para esa nave ('NAVE PRUEBA'): {por_que}. Revisa la fila y elige "
                           "el itinerario en el portal.")
                self.assertEqual(self.mod._cosco_itinerario_ambiguo(pagina, reg, reserva, cand, motivo),
                                 ("NO ENVIADA", detalle))
                self.assertEqual(pagina.capturas, [("cosco_f20_itinerarios.png", False)])
                self.assertTrue((log.parent / "cosco_f20_itinerarios.html").exists())
                for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):
                    self.assertIn(f"· ✗ NO ENVIADA · {detalle}", donde)
                    self.assertIn("itinerarios que calzan: servicio SRV1 · nave NAVE PRUEBA 001E", donde)
                    if n == 0:
                        self.assertIn(vistos, donde)

    def test_sin_el_viaje_de_la_fila_corta(self):
        # Si la fila trae viaje y ninguno de los itinerarios de la nave lo trae, no elige: la reserva queda NO ENVIADA con
        # la lista (decisión de Marcelo, CICLO-cierre-de-frenos.md). Hasta 4948e16 elegía entre los de la nave con otro
        # viaje.
        a = {"i": 0, "naves": ["COSCO SHIPPING BETA 002W"]}
        d = {"i": 3, "naves": ["COSCO SHIPPING BETA 009W"]}
        nave = ["COSCO", "SHIPPING", "BETA"]
        corta = lambda viaje: self.mod._cosco_sin_el_viaje(self.mod._cosco_calzan([a, d], nave, nave + viaje), nave + viaje)
        self.assertIs(corta(["999W"]), True)            # la nave, con otros viajes
        self.assertIs(corta(["002W"]), False)           # uno lo trae: se elige entre esos
        self.assertIs(corta([]), False)                 # la fila sin viaje
        self.assertIs(corta(["002"]), True)             # el viaje, entero: «002» no es «002W»
        self.assertIs(self.mod._cosco_sin_el_viaje([], nave + ["999W"]), False)   # sin la nave: su propio camino
        # reservar_cosco corta así, con la lista, después de ver los itinerarios de la nave y antes de elegir.
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_cosco")
        corte = [n for n in ast.walk(f) if isinstance(n, ast.If) and ast.unparse(n.test) == "_cosco_sin_el_viaje(cand, toks_todos)"]
        self.assertEqual([[ast.unparse(s) for s in n.body] for n in corte],
                         [["return _cosco_itinerario_ambiguo(page, reg, reserva, cand, 'sin-viaje')"]])
        linea = lambda destino: next(n.lineno for n in ast.walk(f) if isinstance(n, ast.Assign)
                                     and ast.unparse(n.targets[0]) == destino)
        self.assertLess(linea("cand"), corte[0].lineno)
        self.assertLess(corte[0].lineno, linea("(elegido, motivo)"))
        # El motivo.
        hoy = datetime.date.today()
        cand = [dict(a, etd=(hoy + datetime.timedelta(days=3)).isoformat(), servicios=["SRV1"]),
                dict(d, etd=(hoy + datetime.timedelta(days=10)).isoformat(), servicios=["SRV2"])]
        reg, vistas, log = self.corrida("cosco_sin_viaje")
        pagina = soporte.PaginaFalsa(texto=lambda js, *a: {"html": "<body>lista sintetica</body>", "sombras": 0}
                                     if js == self.mod._JS_HTML_COMPLETO else None)
        detalle = ("COSCO: no elegí itinerario para esa nave ('COSCO SHIPPING BETA'): ninguna de las 2 opciones de la nave "
                   "trae el viaje de la fila. Revisa la fila y elige el itinerario en el portal.")
        self.assertEqual(self.mod._cosco_itinerario_ambiguo(pagina, reg, {"fila": 20, "nave": "COSCO SHIPPING BETA",
                                                                          "viaje": "999W"}, cand, "sin-viaje"),
                         ("NO ENVIADA", detalle))
        self.assertEqual(pagina.capturas, [("cosco_f20_itinerarios.png", False)])
        for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):
            self.assertIn(f"· ✗ NO ENVIADA · {detalle}", donde)

    def test_reservar_cosco_no_toma_el_primero(self):
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_cosco")
        clics = [ast.unparse(n) for n in ast.walk(f) if isinstance(n, ast.Call)
                 and "_JS_COSCO_CLIC_NAVE" in [ast.unparse(a) for a in n.args]]
        self.assertEqual(clics, ["frame.evaluate(_JS_COSCO_CLIC_NAVE, elegido['i'])"])
        elige = [ast.unparse(n) for n in ast.walk(f) if isinstance(n, ast.Assign)
                 and [ast.unparse(t) for t in n.targets] == ["(elegido, motivo)"]]
        self.assertEqual(elige, ["elegido, motivo = _cosco_elegir_itinerario(cand, reserva) if cand else (None, '')"])
        sin_una = [n for n in ast.walk(f) if isinstance(n, ast.If) and ast.unparse(n.test) == "cand and elegido is None"]
        self.assertEqual([ast.unparse(r) for n in sin_una for r in ast.walk(n) if isinstance(r, ast.Return)],
                         ["return _cosco_itinerario_ambiguo(page, reg, reserva, cand, motivo)"])
        self.assertLess(sin_una[0].lineno, linea_guarda(f))
        # Cada itinerario lleva su salida antes de elegir: la de su tarjeta, no el CY Cutoff de la fila.
        con_salida = [n for n in ast.walk(f) if isinstance(n, ast.Assign) and ast.unparse(n) == "filas = "
                      "_cosco_con_salida(filas)"]
        self.assertEqual(len(con_salida), 1)
        self.assertLess(con_salida[0].lineno, sin_una[0].lineno)

    def test_reservar_cosco_amplia_antes_de_cortar(self):
        # Si la nave, o su viaje, no está en lo que COSCO muestra de entrada, amplía «Sailing Within» a lo más largo y
        # vuelve a buscar, una vez, antes de cortar por el viaje y antes de la guarda; si tampoco aparece, el REVISAR dice
        # hasta qué fecha buscó (decisión de Marcelo, CICLO-ampliar-la-busqueda.md). Hasta 4cae528 cortaba con lo primero.
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_cosco")
        bucle = [n for n in ast.walk(f) if isinstance(n, ast.While) and "_cosco_ampliar" in ast.unparse(n)]
        self.assertEqual(len(bucle), 1)
        self.assertEqual([ast.unparse(s).splitlines()[0] for s in bucle[0].body], [
            "antes = len(filas) if ampliada else 0",
            "filas = _cosco_leer_itinerarios(page, frame, reg, antes=antes)",
            "if filas is None:",
            "filas = _cosco_con_salida(filas)",
            "cand = _cosco_calzan(filas, toks_nave, toks_todos)",
            "if ampliada or (cand and (not _cosco_sin_el_viaje(cand, toks_todos))):",
            "por_que = _cosco_ampliar(page, frame, reg)",
            "if por_que:",
            "reg.paso('La nave no estaba en lo que mostró COSCO: amplié «Sailing Within» y busco de nuevo.')",
            "_cosco_click_btn(frame, 'search service', reg)",
            "esperar(page, 2.0)",
            "ampliada, por_que = (True, NO_AMPLIA_MAS)"])
        self.assertEqual(ast.unparse(bucle[0].body[5].body[0]), "break")
        # Si no amplía, lo anota: en el camino del viaje, el motivo NO ENVIADA no lo dice.
        self.assertEqual(ast.unparse(bucle[0].body[7]), "if por_que:\n    reg.info(f'no amplié la búsqueda: {por_que}')\n"
                                                         "    break")
        corte = [n for n in ast.walk(f) if isinstance(n, ast.If) and ast.unparse(n.test) == "_cosco_sin_el_viaje(cand, toks_todos)"]
        self.assertLess(bucle[0].lineno, corte[0].lineno)
        self.assertLess(corte[0].lineno, linea_guarda(f))
        donde = [ast.unparse(n) for n in ast.walk(f) if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == "donde"]
        self.assertEqual(donde, ["donde = '' if cand else f': "
                                 "{_hasta_donde_busque([d for d, _ in _cosco_salidas(filas)], por_que)}'"])

    def test_amplia_sailing_within(self):
        # «Sailing Within N Weeks»: el único campo a la vista con ese texto y la opción con más semanas, con clic real
        # (CICLO-ampliar-la-busqueda.md). Medido: de 2 a 8 semanas, con la de 2 elegida.
        casos = (
            ({}, "", ["[data-aq-semanas]", "[data-aq-semanas]"]),
            ({"actual": 8}, self.mod.NO_AMPLIA_MAS, []),                     # ya está en la más larga: no pulsa nada
            ({"oculta": True}, "", ["[data-aq-semanas]", "[data-aq-semanas]"]),   # sin opciones hasta abrirlo
            ({"oculta": True, "tope": 2}, self.mod.NO_AMPLIA_MAS, ["[data-aq-semanas]"]),
            ({"campos": 0}, "no pude ampliar la búsqueda: había 0 campos «Sailing Within» a la vista", []),
            ({"campos": 2}, "no pude ampliar la búsqueda: había 2 campos «Sailing Within» a la vista", []),
            ({"actual": None}, "no pude ampliar la búsqueda: no pude leer qué opción de «Sailing Within» está elegida", []),
            ({"sin_marca": True}, "no pude ampliar la búsqueda: no vi una sola opción «Sailing Within 8 Weeks»",
             ["[data-aq-semanas]"]),
            ({"no_cambia": True}, "no pude ampliar la búsqueda: «Sailing Within» quedó en 2 semanas, no en 8",
             ["[data-aq-semanas]", "[data-aq-semanas]"]),
            ({"falla": True}, "no pude ampliar la búsqueda: el clic en «Sailing Within» falló (el clic no salió)", []),
        )
        for k, (estado, esperado, clics) in enumerate(casos):
            with self.subTest(estado=estado):
                reg, vistas, log = self.corrida(f"cosco_semanas_{k}")
                marco = MarcoSemanas(self.mod, **estado)
                self.assertEqual(self.mod._cosco_ampliar(soporte.PaginaFalsa(), marco, reg), esperado)
                self.assertEqual(marco.clics, clics)
                if not esperado:
                    self.assertIn("búsqueda ampliada: «Sailing Within 2 Weeks» -> «Sailing Within 8 Weeks»",
                                  log.read_text(encoding="utf-8"))

    def test_leer_itinerarios_espera_los_nuevos(self):
        # Después de ampliar, espera a que haya más itinerarios que antes; si no llegan, se queda con lo que hay.
        reg, _, _ = self.corrida("cosco_leer")
        uno, dos = [{"i": 0}], [{"i": 0}, {"i": 1}]
        pagina = soporte.PaginaFalsa()
        marco = MarcoLista(self.mod, [uno, uno, uno, dos])
        self.assertEqual(self.mod._cosco_leer_itinerarios(pagina, marco, reg, antes=1), dos)
        self.assertEqual(pagina.esperas, 3)
        pagina = soporte.PaginaFalsa()
        self.assertEqual(self.mod._cosco_leer_itinerarios(pagina, MarcoLista(self.mod, [uno] * 20), reg, antes=1), uno)
        self.assertEqual(pagina.esperas, 15)
        # Sin 'antes', como hasta ahora: el primero que traiga alguno.
        pagina = soporte.PaginaFalsa()
        self.assertEqual(self.mod._cosco_leer_itinerarios(pagina, MarcoLista(self.mod, [[], uno, dos]), reg), uno)
        self.assertEqual(pagina.esperas, 1)

    def test_js_semanas_lee_el_campo_y_las_opciones(self):
        # La forma medida en cosco_f<fila>_itinerarios_marco2.html (2026-09-25): el campo nombra su lista en aria-controls;
        # la lista, oculta mientras está cerrada, trae solo las opciones «Sailing Within N Weeks», con la elegida marcada.
        # El valor del campo no queda en el HTML guardado: hasta el commit anterior se leía de ahí, y sobre las dos listas
        # guardadas no veía ningún campo.
        guion = r"""
const el = (tag, props, hijos = []) => {
  const a = Object.assign({}, props.attrs || {});
  const clases = props.clases || [];
  return {tagName: tag.toUpperCase(), id: props.id || '', offsetParent: props.oculto ? null : {}, textContent: props.texto || '',
    value: '', classList: {contains: (c) => clases.includes(c)},
    setAttribute(k, v) { a[k] = v; }, removeAttribute(k) { delete a[k]; }, getAttribute(k) { return k in a ? a[k] : null; },
    querySelectorAll: (s) => hijos.filter(h => h.tagName.toLowerCase() === s)};
};
const correr = (campos, listas, marcar) => {
  const todos = campos.concat(listas).concat(listas.flatMap(u => u.querySelectorAll('li')));
  global.document = {querySelectorAll: (sel) => sel === '[data-aq-semanas]'
      ? todos.filter(e => e.getAttribute('data-aq-semanas') !== null)
      : todos.filter(e => e.tagName.toLowerCase() === sel)};
  const f = """ + self.mod._JS_COSCO_SEMANAS + r""";
  const r = f(marcar);
  r.marcados = todos.filter(e => e.getAttribute('data-aq-semanas') !== null).map(e => e.textContent || e.id || 'campo');
  return r;
};
const campo = (lista, oculto = false) => el('input', {oculto, attrs: lista ? {'aria-controls': lista} : {}});
const lista = (id, textos, elegida, oculta = true, marca = 'clase') => el('ul', {id}, textos.map(t => el('li', {texto: t,
  oculto: oculta, clases: t === elegida && marca === 'clase' ? ['selected'] : [],
  attrs: t === elegida && marca === 'aria' ? {'aria-selected': 'true'} : {}})));
const SW = [2, 3, 4, 5, 6, 7, 8].map(n => 'Sailing Within ' + n + ' Weeks');
const medida = (oculta = true) => lista('u1', SW, 'Sailing Within 2 Weeks', oculta);
// Otras listas de la página: «Search By» (una opción de semanas mezclada) y una de semanas sin «Sailing Within».
const otras = () => [lista('u2', ['Earliest Departure', 'Sailing Within 3 Weeks', 'Earliest Arrival'], 'Earliest Departure', true),
                     lista('u3', ['12 Weeks', 'Next 9 Weeks'], '12 Weeks', true)];
const suyos = () => [campo('u2'), campo('u3'), campo(null)];
console.log(JSON.stringify([
  correr([campo('u1'), ...suyos()], [medida(), ...otras()], ''),
  correr([campo('u1'), ...suyos()], [medida(), ...otras()], 'campo'),
  correr([campo('u1'), ...suyos()], [medida(), ...otras()], 'opcion'),
  correr([campo('u1'), ...suyos()], [medida(false), ...otras()], 'opcion'),
  correr([campo('u1')], [lista('u1', [' sailing within 1 week ', 'Sailing Within 3 Weeks'], 'Sailing Within 3 Weeks', false, 'aria')], ''),
  correr([campo('u1')], [lista('u1', SW, null)], ''),
  correr([campo('u1'), campo('u4')], [medida(), lista('u4', SW, 'Sailing Within 4 Weeks')], 'campo'),
  correr([campo('u1', true)], [medida()], 'campo'),
  correr([campo(null)], [medida()], ''),
]));
"""
        self.assertEqual(correr_node(self, guion), [
            {"campos": 1, "actual": 2, "mayor": 8, "marcada": False, "marcados": []},
            {"campos": 1, "actual": 2, "mayor": 8, "marcada": True, "marcados": ["campo"]},
            {"campos": 1, "actual": 2, "mayor": 8, "marcada": False, "marcados": []},        # la opción no se ve
            {"campos": 1, "actual": 2, "mayor": 8, "marcada": True, "marcados": ["Sailing Within 8 Weeks"]},
            {"campos": 1, "actual": 3, "mayor": 3, "marcada": False, "marcados": []},        # marcada por aria-selected
            {"campos": 1, "actual": None, "mayor": 8, "marcada": False, "marcados": []},     # ninguna marcada
            {"campos": 2, "marcados": []},                                                   # dos campos: ninguno
            {"campos": 0, "marcados": []},                                                   # el campo no se ve
            {"campos": 0, "marcados": []},                                                   # sin aria-controls
        ])

    def test_js_lista_lee_la_salida_y_la_llegada_de_la_tarjeta(self):
        # La forma medida en la lista de la corrida del 2026-09-25 (CICLO-proxima-salida.md): la salida y la llegada van
        # arriba en la tarjeta, como «Sep27 (Sun)»; la fila de «Service» y «Vessel / Voyage» trae solo el CY Cutoff.
        guion = r"""
const nodo = (tag, cls, texto, hijos = []) => {
  const n = {tagName: tag.toUpperCase(), className: cls, texto, hijos, parentElement: null, offsetParent: {}};
  Object.defineProperty(n, 'children', {get() { return this.hijos; }});
  Object.defineProperty(n, 'textContent', {get() { return [this.texto, ...this.hijos.map(h => h.textContent)].join(''); }});
  Object.defineProperty(n, 'nextElementSibling', {get() {
    const p = this.parentElement; return p ? (p.hijos[p.hijos.indexOf(this) + 1] || null) : null; }});
  n.contains = function (x) { for (let y = x; y; y = y.parentElement) if (y === this) return true; return false; };
  const calza = (e, sel) => sel.split(',').map(s => s.trim()).some(s => s === '*' || s === e.tagName.toLowerCase()
      || (s.startsWith('[class*=') && e.className.includes(s.slice(8, -1))));
  n.querySelectorAll = function (sel) {
    const out = []; const walk = (x) => { for (const h of x.hijos) { if (calza(h, sel)) out.push(h); walk(h); } };
    walk(this); return out; };
  hijos.forEach(h => { h.parentElement = n; });
  return n;
};
const s = (t) => nodo('span', '', t);
const tarjeta = (salida, llegada, corte, naves) => nodo('div', 'card', '', [
  nodo('div', 'recorrido', '', [nodo('p', '', 'Lirquen'), s(salida), s('48'), s('Days'), s('Haulage :'), s('CY'),
                                s('CY'), s(llegada), nodo('p', '', 'Shanghai')]),
  nodo('div', 'fila', '', [s('CY Cutoff :'), s(corte), s('Service :'), nodo('div', '', '', [s('SV1'), s('SV2')]),
                           s('Vessel / Voyage :'), nodo('div', '', '', naves.map(s)),
                           nodo('button', 'px-2', '', [s('Book Now')])])]);
const correr = (tarjetas) => {
  const body = nodo('body', '', '', [nodo('div', 'lista', '', tarjetas)]);
  global.document = {querySelectorAll: (sel) => body.querySelectorAll(sel)};
  const f = """ + self.mod._JS_COSCO_LISTA_NAVES + r""";
  return f().map(x => [x.i, x.salida, x.llegada, x.corte, x.naves]);
};
console.log(JSON.stringify([
  correr([tarjeta('Sep28 (Mon)', 'Nov15 (Sun)', '2026-09-27 (Sun) 12:00', ['NAVE UNO 001E', 'OTRA 002W']),
          tarjeta('Oct05 (Mon)', 'Nov04 (Wed)', '2026-10-04 (Sun) 12:00', ['NAVE DOS 003E'])]),
  correr([tarjeta('Sep28 (Mon)', 'Nov15 (Sun)', '2026-09-27 (Sun) 12:00', ['NAVE UNO 001E'])]),
  correr([nodo('div', 'card', '', [nodo('div', 'fila', '', [s('Service :'), nodo('div', '', '', [s('SV1')]),
                                   s('Vessel / Voyage :'), nodo('div', '', '', [s('NAVE TRES')]),
                                   nodo('button', '', '', [s('Book Now')])])])]),
  correr([nodo('div', 'card', '', [nodo('div', 'recorrido', '', [s('Sep28 (Mon)'), s('Oct10 (Sat)'), s('Nov15 (Sun)')]),
          nodo('div', 'fila', '', [s('CY Cutoff :'), s('2026-09-27 (Sun) 12:00'), s('Service :'),
                                   nodo('div', '', '', [s('SV1')]), s('Vessel / Voyage :'),
                                   nodo('div', '', '', [s('NAVE CUATRO')]), nodo('button', '', '', [s('Book Now')])])])]),
  correr([tarjeta('Oct05 (Mon)', 'Nov04 (Wed)', '2026-10-04 (Sun) 12:00', ['NAVE DOS 003E']),
          [1, 2, 3, 4, 5, 6, 7].reduce((x) => nodo('div', '', '', [x]), nodo('button', 'px-2', '', [s('Book Now')]))])
    .map(x => [x[0], x[4]]),
  correr([tarjeta('Oct05 (Mon)', 'Nov04 (Wed)', '2026-10-04 (Sun) 12:00', ['NAVE DOS 003E']),
          nodo('div', 'card', '', [nodo('div', 'recorrido', '', [s('Sep28 (Mon)'), s('Nov15 (Sun)')]),
                                   nodo('div', '', '', [nodo('div', '', '', [nodo('button', 'px-2', '', [s('Book Now')])])])])])
    .map(x => [x[0], x[4]]),
]));
"""
        self.assertEqual(correr_node(self, guion), [
            [[0, "Sep28 (Mon)", "Nov15 (Sun)", "2026-09-27", ["NAVE UNO 001E", "OTRA 002W"]],
             [1, "Oct05 (Mon)", "Nov04 (Wed)", "2026-10-04", ["NAVE DOS 003E"]]],     # cada una con las suyas
            [[0, "Sep28 (Mon)", "Nov15 (Sun)", "2026-09-27", ["NAVE UNO 001E"]]],       # una sola en la lista
            [[0, "", "", "", ["NAVE TRES"]]],                                           # sin el recorrido: sin salida
            # Con tres fechas, ¿cuál es la llegada? Ninguna: el tránsito no se lee (medido: las 4 traen dos). Hasta
            # 2825153, la segunda.
            [[0, "Sep28 (Mon)", "", "2026-09-27", ["NAVE CUATRO"]]],
            # Un «Book now» sin su fila a 8 niveles no tiene nave. Hasta a198645 leía el octavo ancestro, la lista, y se
            # quedaba con la nave del otro itinerario, [1, ["NAVE DOS 003E"]] (CICLO-solo-la-nave-pedida.md).
            [[0, ["NAVE DOS 003E"]], [1, []]],
            # Tampoco si la primera con «Service» y «Vessel» es la lista, que trae otro «Book now»: hasta a198645,
            # [1, ["NAVE DOS 003E"]].
            [[0, ["NAVE DOS 003E"]], [1, []]]])


class MarcoControl:
    """Marco falso para el CONTROL de COSCO: cada JavaScript de lectura responde según la etiqueta que se le pide;
    si 'roto', toda lectura falla."""

    def __init__(self, mod, desplegable=None, leer=None, roto=False):
        self.mod, self.desplegable, self.leer, self.roto = mod, dict(desplegable or {}), dict(leer or {}), roto

    def evaluate(self, js, etiqueta):
        if self.roto:
            raise RuntimeError("marco cerrado")
        if js == self.mod._JS_COSCO_LEER_DESPLEGABLE:
            return self.desplegable.get(etiqueta)
        if js == self.mod._JS_COSCO_ETQ_LEER:
            return self.leer.get(etiqueta)
        raise AssertionError("JavaScript desconocido")


class TestControlCosco(ConRegistro):
    TIPO = "40RQ - 40' Hi-Cube Refrigerated Container"

    def desplegable(self, campos, etq="Size Type"):
        """Corre _JS_COSCO_LEER_DESPLEGABLE sobre campos falsos de desplegables: (placeholder, valor, visible)."""
        guion = (
            "const campo = ([ph, v, vis]) => ({placeholder: ph, value: v, offsetParent: vis ? {} : null});\n"
            f"const campos = {json.dumps(campos)}.map(campo);\n"
            "global.document = {querySelectorAll: () => campos};\n"
            "const f = " + self.mod._JS_COSCO_LEER_DESPLEGABLE + ";\n"
            f"console.log(JSON.stringify(f({json.dumps(etq)})));\n")
        return correr_node(self, guion)

    def test_js_desplegable_por_su_placeholder(self):
        pais, tipo = ("Please select Country", "CHILE", True), ("Please select Size Type", self.TIPO, True)
        # Medido en la corrida del 2026-09-24: el placeholder del desplegable no empieza por la etiqueta.
        self.assertEqual(self.desplegable([pais, tipo]), self.TIPO)
        self.assertIsNone(self.desplegable([pais]))                                         # no está
        self.assertIsNone(self.desplegable([("Please select Size Type", " ", True)]))         # no muestra texto
        self.assertIsNone(self.desplegable([("Please select Size Type", "20RF", True), tipo]))  # más de uno: no elige
        self.assertEqual(self.desplegable([("Please select Size Type", "20RF", False), tipo]), self.TIPO)  # oculto

    def test_size_type_dice_no_pude_leer_nunca_vacio(self):
        no_pude = "   ?  Size Type: no pude leer (esperaba '40RQ')"
        aviso = "OJO: no pude leer Size Type en 'Booking Details'; revísalo en la captura."
        casos = (
            (MarcoControl(self.mod, desplegable={"Size Type": self.TIPO}), f"   ✓  Size Type: {self.TIPO}"),
            # En «Choose Service» lo lee _JS_COSCO_ETQ_LEER (16 de 16 ✓ en las corridas medidas).
            (MarcoControl(self.mod, leer={"Size Type": "40RQ"}), "   ✓  Size Type: 40RQ"),
            (MarcoControl(self.mod), no_pude),
            (MarcoControl(self.mod, leer={"Size Type": ""}), no_pude),
            (MarcoControl(self.mod, roto=True), no_pude),
        )
        for n, (marco, esperado) in enumerate(casos):
            with self.subTest(caso=n):
                reg, vistas, log = self.corrida(f"control_{n}")
                self.mod._cosco_control(marco, reg, "Booking Details", [("Size Type", "40RQ"), ("Gross Weight", "22500")])
                for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):
                    self.assertIn(esperado, donde)
                    self.assertNotIn("Size Type: VACÍO", donde)
                    self.assertEqual(aviso in donde, esperado == no_pude)
                    # Los demás campos siguen como antes: si no se leen, «VACÍO».
                    self.assertIn("   ✗  Gross Weight: VACÍO (esperaba '22500')", donde)


class TestHyundai(ConRegistro):
    def test_js_dicen_lo_que_hicieron(self):
        guion = (
            "const res = [];\n"
            "const casilla = (checked) => ({checked, clics: 0, dispatchEvent() {}, click() { this.clics++; this.checked = true; }});\n"
            "const conDoc = (doc, f, ...a) => { global.document = doc; return f(...a); };\n"
            "const marcar = " + self.mod._JS_HMM_MARCAR_POR_ID + ";\n"
            "const correo = " + self.mod._JS_HMM_AVISO_CORREO + ";\n"
            "const residuo = " + self.mod._JS_HMM_NO_RESIDUO + ";\n"
            "let c = casilla(false);\n"
            "res.push([conDoc({querySelector: () => c}, marcar, '#dangerousN'), c.checked]);\n"
            "res.push([conDoc({querySelector: () => null}, marcar, '#dangerousN')]);\n"
            "c = casilla(false); res.push([conDoc({querySelector: () => c}, correo), c.clics]);\n"
            "c = casilla(true); res.push([conDoc({querySelector: () => c}, correo), c.clics]);\n"
            "res.push([conDoc({querySelector: () => null}, correo)]);\n"
            "c = casilla(false);\n"
            "const lab = {textContent: ' Non-waste ', querySelector: () => c};\n"
            "res.push([conDoc({querySelectorAll: () => [{textContent: 'Waste', querySelector: () => null}, lab]}, residuo), c.clics]);\n"
            "res.push([conDoc({querySelectorAll: () => [{textContent: 'Waste', querySelector: () => null}]}, residuo)]);\n"
            "console.log(JSON.stringify(res));\n")
        self.assertEqual(correr_node(self, guion),
                         [[True, True], [False], ["marcado", 1], ["ya", 0], [""], [True, 1], [False]])

    def test_los_mensajes_dicen_lo_que_paso(self):
        reg, _, log = self.corrida()
        casos = (
            (lambda p: self.mod._hmm_marcar_no(p, reg, "Dangerous Cargo", "#dangerousN", "#dangerousN"),
             {"querySelector(sel)": True}, "Dangerous Cargo: No (js)"),
            (lambda p: self.mod._hmm_marcar_no(p, reg, "Dangerous Cargo", "#dangerousN", "#dangerousN"),
             {"querySelector(sel)": False}, "Dangerous Cargo: no encontré #dangerousN; no marqué nada"),
            (lambda p: self.mod._hmm_aviso_correo(p, reg), {"emailChk": "marcado"}, "E-mail Notice Setting: activado"),
            (lambda p: self.mod._hmm_aviso_correo(p, reg), {"emailChk": "ya"}, "E-mail Notice Setting: ya estaba activado"),
            (lambda p: self.mod._hmm_aviso_correo(p, reg), {"emailChk": ""},
             "E-mail Notice Setting: no encontré #emailChk; no marqué nada"),
            (lambda p: self.mod._hmm_no_residuo(p, reg), {"non-waste": True}, "Scrap/Waste: Non-waste (js)"),
            (lambda p: self.mod._hmm_no_residuo(p, reg), {"non-waste": False},
             "Scrap/Waste: no encontré «Non-waste»; no marqué nada"),
        )
        for i, (llamar, js, mensaje) in enumerate(casos):
            with self.subTest(mensaje=mensaje):
                antes = log.read_text(encoding="utf-8")
                llamar(PaginaCma(js=js))                      # ningún localizador existe: va al JavaScript
                nuevo = log.read_text(encoding="utf-8")[len(antes):]
                self.assertEqual(nuevo.split("    ", 1)[1].strip(), mensaje)

    # --- La nave con todas sus palabras (CICLO-cola-tres-items.md). Las filas imitan la tarjeta que guardó el log de las
    # corridas del 21 al 25: «MAIN VESSEL», la nave con el prefijo de la naviera y su viaje, y su «Book Now». Su
    # textContent une los trozos con un espacio, como el de las 8 tarjetas de esos log.txt (CICLO-cola-seis-items.md). ---
    NAVES_HMM = r"""
const nodo = (tag, cls, texto, hijos = []) => {
  const n = {tagName: tag.toUpperCase(), className: cls, texto, hijos, parentElement: null, offsetParent: {}, clics: 0,
             getBoundingClientRect: () => ({width: 10, height: 10}), scrollIntoView() {}, click() { this.clics++; }};
  Object.defineProperty(n, 'textContent', {get() { return [this.texto, ...this.hijos.map(h => h.textContent)].join(' '); }});
  const todos = (x) => x.hijos.flatMap(h => [h, ...todos(h)]);
  n.querySelectorAll = (sel) => todos(n).filter(e => sel.split(',').some(s => {
    const [tag, cl] = s.trim().split('.');
    return (!tag || e.tagName === tag.toUpperCase()) && (!cl || (' ' + e.className + ' ').includes(' ' + cl + ' '));
  }));
  n.querySelector = (sel) => n.querySelectorAll(sel)[0] || null;
  hijos.forEach(h => { h.parentElement = n; });
  return n;
};
global.window = {getComputedStyle: () => ({color: 'rgb(0, 0, 0)'})};
const fila = (nave, cls = '') => nodo('div', cls, '', [nodo('p', '', 'MAIN VESSEL'), nodo('p', 'vessel', nave),
                                                      nodo('button', '', 'Book Now')]);
const previa = (nave) => nodo('a', 'preview-area', '', [nodo('span', 'vessel', nave)]);
const correr = (hijos, toks) => {
  const body = nodo('body', '', '', [nodo('div', 'lista', '', hijos)]);
  global.document = {body, querySelectorAll: (s) => body.querySelectorAll(s)};
  const r = f(toks);
  return [r.idx, r.motivo, r.tipo || null, body.querySelectorAll('button').map(b => b.clics)];
};
"""

    def test_js_nave_con_todas_sus_palabras(self):
        # Desde el encargo 32, _JS_HMM_INDICE_NAVE es solo la interfaz anterior (a.preview-area): las tarjetas con «Book
        # Now» las lee _JS_HMM_TARJETAS, por su «1st Vessel» (CICLO-ampliar-la-busqueda.md). Hasta 4cae528 también las
        # calzaba, con el texto de toda la tarjeta, y pulsaba la primera: aquí, [1, "ok", "book_now", [0, 1]].
        guion = ("const f = " + self.mod._JS_HMM_INDICE_NAVE + ";\n" + self.NAVES_HMM + r"""
const filas = () => [fila('HMM ALFA (0001E)'), fila('HMM BETA (0002E)')];
console.log(JSON.stringify([
  correr(filas(), ['HMM', 'BETA']),
  correr([previa('HMM ALFA'), previa('HMM BETA')], ['HMM', 'BETA']),
  correr([previa('HMM ALFA'), previa('HMM BETA')], ['HMM', 'GAMA']),
  correr([previa('HMM ALFA'), previa('HMM BETA')], ['PRIMERA', 'DISPONIBLE']),
  correr([previa('HMM ALFA'), previa('HMM BETA')], ['HMM', 'NW2']),
  correr([previa('HMM ALFA'), previa('HMM BETA')], ['HMM', 'VOY']),
  correr([previa('HMM ALFA'), previa('HMM BETA')], ['HMM', 'VIAJE']),
  correr([previa('HMM ALFA'), previa('HMM BETA')], ['HMM', 'V.']),
  correr([previa('HMM ALFA'), previa('HMM BETA')], []),
  correr([previa('HMM SAVANNAH'), previa('HMM ANNA')], ['HMM', 'ANNA']),
]));
""")
        self.assertEqual(correr_node(self, guion), [
            [-1, "no_encontrada", None, [0, 0]],                     # las de «Book Now» ya no son suyas: ni un clic
            # La interfaz anterior, con todas las palabras: hasta 9051f43, [0, "ok", "preview_area", []] en las dos.
            [1, "ok", "preview_area", []],
            [-1, "no_encontrada", None, []],
            # Sus comodines y sus palabras de ruido (NW2, VOY, VIAJE y V.) se exigen como las demás: hasta a198645 las
            # quitaba y calzaba la primera nave HMM (CICLO-solo-la-nave-pedida.md).
            [-1, "no_encontrada", None, []],
            [-1, "no_encontrada", None, []],
            [-1, "no_encontrada", None, []],
            [-1, "no_encontrada", None, []],
            [-1, "no_encontrada", None, []],
            # Sin palabras de nave, ninguna.
            [-1, "sin_nave", None, []],
            # Cada palabra, entera: hasta f68ce6c «ANNA» calzaba dentro de «SAVANNAH» (CICLO-cola-seis-items.md).
            [1, "ok", "preview_area", []],
        ])

    # --- La «1st Vessel» (decisión de Marcelo, CICLO-ampliar-la-busqueda.md): la tarjeta medida en hmm_f9_naves.html
    # del 2026-09-26, un li con el origen y el destino (.place-content, con su fecha), los campos .schedule-info-text
    # (etiqueta y valor) y su «Book Now». ---
    TARJETAS_HMM = r"""
const nodo = (tag, cls, texto, hijos = [], vis = true) => {
  const n = {tagName: tag.toUpperCase(), className: cls, texto, hijos, parentElement: null, clics: 0, vis};
  Object.defineProperty(n, 'children', {get() { return this.hijos; }});
  Object.defineProperty(n, 'textContent', {get() { return [this.texto, ...this.hijos.map(h => h.textContent)].join(' '); }});
  Object.defineProperty(n, 'offsetParent', {get() { return this.vis ? {} : null; }});
  n.getBoundingClientRect = () => ({width: n.vis ? 10 : 0, height: n.vis ? 10 : 0});
  n.click = function () { this.clics++; };
  n.scrollIntoView = () => {};
  const todos = (x) => x.hijos.flatMap(h => [h, ...todos(h)]);
  n.querySelectorAll = (sel) => todos(n).filter(e => sel.split(',').some(s => {
    s = s.trim();
    return s.startsWith('.') ? (' ' + e.className + ' ').includes(' ' + s.slice(1) + ' ') : e.tagName === s.toUpperCase();
  }));
  n.querySelector = (sel) => n.querySelectorAll(sel)[0] || null;
  hijos.forEach(h => { h.parentElement = n; });
  return n;
};
global.window = {getComputedStyle: () => ({color: 'rgb(0, 0, 0)'})};
const caja = (cls, etq, valor) => nodo('div', 'schedule-info-text ' + cls, '', [nodo('div', '', etq), nodo('div', '', valor)]);
const lugar = (nombre, fecha) => nodo('div', 'place-content', '', [nodo('div', '', nombre), nodo('div', '', fecha)]);
const tarjeta = (salida, llegada, main, primera, cls = '', book = true, tipo = null) => nodo('li', cls, '', [
  nodo('div', 'place-week', '', [nodo('div', '', 'WK'), nodo('div', '', '41')]),
  lugar('ORIGEN', salida), nodo('span', 'transshipment-line-day', '28'), lugar('DESTINO', llegada),
  ...(tipo === null ? [] : [nodo('div', 'place-transshipment', '',
                                 [].concat(tipo).map(x => nodo('div', 'mid-state', '', [nodo('span', '', x)])))]),
  nodo('div', 'result-info-container', '', [caja('available', 'Main Vessel', main), caja('', 'Route', 'NW2'),
    caja('', 'Operator', 'HMM')].concat(primera === null ? [] : [caja('first-vessel', '1st Vessel', primera)])
    .concat([caja('cut-off', 'Port Cut-off', '2026-10-03 04:00')])),
  nodo('div', 'now', '', book === true ? [nodo('a', '', 'Book Now')] : book === 'oculto' ? [nodo('a', '', 'Book Now', [], false)] : []),
  nodo('p', 'down btnToggleDetail', 'Show Details')]);
const pagina = (tarjetas) => {
  const body = nodo('body', '', '', [nodo('ul', 'lista', '', tarjetas)]);
  global.document = {body, querySelectorAll: (s) => body.querySelectorAll(s), querySelector: (s) => body.querySelector(s)};
  return body;
};
"""

    def test_js_tarjetas_con_su_1st_vessel(self):
        guion = self.TARJETAS_HMM + "const f = " + self.mod._JS_HMM_TARJETAS + r""";
const lista = () => [tarjeta('2026-10-07', '2026-11-04', 'OTRA NAVE (001E)', 'OTRA NAVE (001E)'),
  tarjeta('2026-10-09', '2026-11-27', 'HMM NAVE (002W)', 'FEEDER (003E)'),
  tarjeta('2026-10-23', '2026-11-25', 'OTRA NAVE (004E)', 'HMM NAVE (002W)'),
  tarjeta('2026-10-23', '2026-11-27', 'HMM NAVE (002W)', 'HMM NAVE (002W)')];
const r = [];
pagina(lista()); r.push(f(['HMM', 'NAVE']));
pagina(lista()); r.push(f([]));
pagina([tarjeta('2026-10-07', '2026-11-04', 'X', 'HMM SAVANNAH (1E)'), tarjeta('2026-10-08', '2026-11-05', 'X', 'hmm anna (2E)')]);
r.push(f(['HMM', 'ANNA']));
pagina([tarjeta('2026-10-07', '2026-11-04', 'X', 'HMM NAVE (1E)', 'closed'), tarjeta('2026-10-08', '', 'X', null),
        tarjeta('2026-10-09', '2026-11-06', 'X', 'HMM NAVE (1E)', '', 'oculto'), tarjeta('2026-10-10', '2026-11-07', 'X', 'HMM NAVE (1E)')]);
r.push(f(['HMM', 'NAVE']));
// Una sola tarjeta, dentro de un bloque que trae otro .place-content: la tarjeta no pasa de su li.
const una = nodo('body', '', '', [nodo('div', 'resultado', '', [lugar('RESUMEN', '2026-09-01'),
  nodo('ul', 'lista', '', [tarjeta('2026-10-23', '2026-11-25', 'X', 'HMM NAVE (1E)')])])]);
global.document = {body: una, querySelectorAll: (s) => una.querySelectorAll(s)};
r.push(f(['HMM', 'NAVE']));
console.log(JSON.stringify(r));
"""
        medida, sin_palabras, entera, varias, sola = correr_node(self, guion)
        self.assertEqual(sola, [{"i": 0, "primera": "HMM NAVE (1E)", "calza": True, "salida": "2026-10-23",
                                 "llegada": "2026-11-25", "disponible": True, "book": 1, "directa": None}])
        t = lambda i, primera, calza, salida, llegada, disponible=True: {
            "i": i, "primera": primera, "calza": calza, "salida": salida, "llegada": llegada, "disponible": disponible,
            "book": 1, "directa": None}
        # La nave de la fila solo en «1st Vessel»: la de la 2.ª la trae como «Main Vessel» y no calza. Hasta 4cae528, con el
        # texto de toda la tarjeta, calzaban la 2.ª, la 3.ª y la 4.ª, y se pulsaba la 2.ª.
        self.assertEqual(medida, [t(0, "OTRA NAVE (001E)", False, "2026-10-07", "2026-11-04"),
                                  t(1, "FEEDER (003E)", False, "2026-10-09", "2026-11-27"),
                                  t(2, "HMM NAVE (002W)", True, "2026-10-23", "2026-11-25"),
                                  t(3, "HMM NAVE (002W)", True, "2026-10-23", "2026-11-27")])
        self.assertEqual([x["calza"] for x in sin_palabras], [False] * 4)      # sin palabras de nave, ninguna
        self.assertEqual([x["calza"] for x in entera], [False, True])          # entera, sin distinguir mayúsculas
        # La cerrada no está disponible; sin «1st Vessel», no calza; sin llegada, no la inventa; el «Book Now» oculto no
        # cuenta: la última es la i = 2.
        self.assertEqual(varias, [t(0, "HMM NAVE (1E)", True, "2026-10-07", "2026-11-04", False),
                                  t(1, "", False, "2026-10-08", ""),
                                  t(2, "HMM NAVE (1E)", True, "2026-10-10", "2026-11-07")])

    def test_js_directa_o_con_transbordo(self):
        # Si la salida es directa: el único .mid-state de la tarjeta, «Direct» o «Transshipment», medido en las 12
        # tarjetas del 26-09 (CICLO-ampliar-msc-y-cma.md). Sin uno solo, o con otro texto, no se sabe (null).
        guion = self.TARJETAS_HMM + "const f = " + self.mod._JS_HMM_TARJETAS + r""";
pagina(['Direct', 'Transshipment', ' direct ', null, ['Direct', 'Transshipment'], 'Indirect'].map(
  (tipo, k) => tarjeta('2026-10-0' + (k + 1), '2026-11-04', 'X', 'HMM NAVE (1E)', '', true, tipo)));
console.log(JSON.stringify(f(['HMM', 'NAVE']).map(x => x.directa)));
"""
        self.assertEqual(correr_node(self, guion), [True, False, True, None, None, None])

    def test_js_clic_en_la_tarjeta_elegida(self):
        guion = self.TARJETAS_HMM + "const f = " + self.mod._JS_HMM_CLIC_TARJETA + r""";
const cuatro = () => [tarjeta('2026-10-07', '2026-11-04', 'X', 'HMM NAVE (1E)', '', true, 'Direct'),
                      tarjeta('2026-10-08', '2026-11-05', 'X', 'HMM NAVE (1E)', '', 'oculto'),
                      tarjeta('2026-10-09', '2026-11-06', 'X', 'OTRA (2E)', '', true, 'Transshipment'),
                      tarjeta('2026-10-10', '2026-11-07', 'X', 'HMM NAVE (1E)', 'closed')];
const T = ['HMM', 'NAVE'];
const casos = [[0, T, '2026-10-07', true], [1, ['OTRA'], '2026-10-09', false], [2, T, '2026-10-10', null],
               [3, T, '2026-10-10', null], [0, T, '2026-10-08', true], [0, ['OTRA'], '2026-10-07', true],
               [1, T, '2026-10-09', false], [0, T, '2026-10-07', false]];
const r = [];
for (const [i, toks, salida, directa] of casos) {
  const body = pagina(cuatro());
  r.push([f({i, toks, salida, directa}), body.querySelectorAll('a').map(a => a.clics)]);
}
console.log(JSON.stringify(r));
"""
        # El «Book Now» i-ésimo a la vista, como los cuenta _JS_HMM_TARJETAS (el oculto no cuenta), y solo si la tarjeta i
        # sigue siendo la elegida: la 1.ª y la 3.ª, sí; la 4.ª está cerrada; no hay 4.ª a la vista; y ni con otra salida,
        # ni con otra nave, ni si la elegida era con transbordo y esta es directa, pulsa nada. Hasta e8b027b pulsaba el
        # i-ésimo sin volver a leer la tarjeta; hasta 2044222 no miraba si era directa.
        nada = [False, [0, 0, 0, 0]]
        self.assertEqual(correr_node(self, guion), [[True, [1, 0, 0, 0]], [True, [0, 0, 1, 0]], nada, nada, nada, nada,
                                                    nada, nada])

    def test_js_duration(self):
        guion = "const f = " + self.mod._JS_HMM_SEMANAS + r""";
const op = (t) => ({textContent: t});
const s = (i, vis = true) => ({options: [op('1 weeks'), op('2 weeks'), op(' 8 Weeks '), op('ALL')], selectedIndex: i,
                               offsetParent: vis ? {} : null});
const r = [];
for (const sel of [s(1), s(2), s(1, false), s(3), null]) {
  global.document = {querySelector: (q) => (q === '#srchSelWeeks' ? sel : null)};
  r.push(f());
}
console.log(JSON.stringify(r));
"""
        ops = [{"texto": "1 weeks", "n": 1}, {"texto": "2 weeks", "n": 2}, {"texto": "8 Weeks", "n": 8}]
        self.assertEqual(correr_node(self, guion), [
            {"visible": True, "actual": 2, "opciones": ops}, {"visible": True, "actual": 8, "opciones": ops},
            {"visible": False, "actual": 2, "opciones": ops}, {"visible": True, "actual": None, "opciones": ops}, None])

    # La lista medida el 2026-09-26: la nave de la fila es la «1st Vessel» de la 5.ª y la 6.ª, que salen el mismo día; la
    # 5.ª llega antes (33 días; la 6.ª, 35). La 4.ª la trae como «Main Vessel» y sale antes, con otra nave desde Chile.
    @staticmethod
    def hmm(i, calza, n, transito, disponible=True, directa=None):
        hoy = datetime.date.today()
        return {"i": i, "primera": "HMM NAVE (002W)" if calza else "OTRA (001E)", "calza": calza,
                "salida": (hoy + datetime.timedelta(days=n)).isoformat(),
                "llegada": (hoy + datetime.timedelta(days=n + transito)).isoformat(), "disponible": disponible, "book": 1,
                "directa": directa}

    def elegir_hmm(self, lotes, semanas=2, legado=None):
        self.n_hmm = getattr(self, "n_hmm", 0) + 1
        reg, vistas, log = self.corrida(f"hmm_{self._testMethodName}_{self.n_hmm}")
        pagina = PaginaListaHmm(self.mod, lotes, semanas, legado)
        r = self.mod._hmm_elegir_nave(pagina, reg, {"fila": 9, "nave": "HMM NAVE"}, ["HMM", "NAVE"])
        return r, pagina, log.read_text(encoding="utf-8")

    def test_elige_la_1st_vessel_y_la_proxima_salida(self):
        h = self.hmm
        medida = [h(0, False, 11, 28), h(1, False, 11, 36), h(2, False, 13, 34), h(3, False, 13, 49), h(4, True, 27, 33),
                  h(5, True, 27, 35)]
        r, pagina, log = self.elegir_hmm([medida])
        # Sin leer si son directas (directa None), decide el tránsito: la 5.ª. Con lo medido, la 6.ª
        # (test_prefiere_la_directa).
        self.assertEqual((r["idx"], r["motivo"], r["tipo"], pagina.clics, pagina.elegidas), (4, "ok", "book_now", [4], []))
        # Al pulsar, el JavaScript vuelve a leer la tarjeta con la nave de la fila y su salida.
        self.assertEqual(pagina.args_clic, [{"i": 4, "toks": ["HMM", "NAVE"], "salida": medida[4]["salida"],
                                             "directa": None}])
        veintisiete = datetime.date.today() + datetime.timedelta(days=27)
        self.assertIn("2 tarjetas traen la nave como 1st Vessel; elijo la próxima salida desde el", log)
        self.assertIn(f"2 salidas de la nave salen el {veintisiete:%d-%m-%Y}: elijo la de menor tiempo de tránsito, 33 días "
                      "(las otras: 35 días)", log)
        # La próxima, no la primera en la página.
        r, pagina, _ = self.elegir_hmm([[h(0, True, 30, 30), h(1, True, 20, 30)]])
        self.assertEqual(pagina.clics, [1])
        # El mismo día y el mismo tránsito: ninguna, NO ENVIADA con el motivo.
        r, pagina, _ = self.elegir_hmm([[h(0, True, 27, 33), h(1, True, 27, 33)]])
        hoy = datetime.date.today()
        self.assertEqual((r, pagina.clics), ({"corte": ("NO ENVIADA", f"HYUNDAI: no elegí salida para esa nave ('HMM NAVE'): "
                                                        f"2 de las 2 opciones salen el {veintisiete:%d-%m-%Y}, la próxima salida "
                                                        f"desde el {hoy:%d-%m-%Y}, y 2 de ellas tienen el menor tiempo de "
                                                        "tránsito, 33 días. Revisa la fila y elige la salida en el portal.")},
                                             []))
        # Solo en tarjetas cerradas: «cerrada», sin pulsar.
        r, pagina, _ = self.elegir_hmm([[h(0, True, 27, 33, disponible=False), h(1, False, 11, 28)]])
        self.assertEqual((r, pagina.clics), ({"idx": -1, "motivo": "cerrada"}, []))
        # Sin tarjetas con «Book Now»: la interfaz anterior, como hasta ahora.
        r, pagina, _ = self.elegir_hmm([[]], legado={"idx": 2, "motivo": "ok", "tipo": "preview_area"})
        self.assertEqual((r, pagina.clics), ({"idx": 2, "motivo": "ok", "tipo": "preview_area"}, []))

    def test_prefiere_la_directa(self):
        # Entre dos salidas del mismo día con la nave de la fila, la directa; solo si las dos tienen transbordo, la de
        # menor tránsito (decisión de Marcelo, CICLO-ampliar-msc-y-cma.md). Medido en las dos listas del 26-09: la 5.ª
        # (con transbordo, 33 días) y la 6.ª (directa, 35) salen el mismo día. Hasta el encargo 33 se elegía la 5.ª.
        h = self.hmm
        veintisiete = datetime.date.today() + datetime.timedelta(days=27)
        medida = [h(0, False, 11, 28, directa=True), h(1, False, 11, 36, directa=False), h(2, False, 13, 34, directa=True),
                  h(3, False, 13, 49, directa=False), h(4, True, 27, 33, directa=False), h(5, True, 27, 35, directa=True)]
        r, pagina, log = self.elegir_hmm([medida])
        self.assertEqual((r["idx"], pagina.clics), (5, [5]))
        self.assertEqual(pagina.args_clic[0]["directa"], True)          # el clic comprueba que sea la directa
        self.assertIn(f"2 salidas de la nave salen el {veintisiete:%d-%m-%Y}: prefiero la directa; descarto 1 con "
                      "transbordo", log)
        self.assertNotIn("elijo la de menor tiempo de tránsito", log)
        # Las dos con transbordo: la de menor tránsito, como antes.
        r, pagina, log = self.elegir_hmm([[h(0, True, 27, 33, directa=False), h(1, True, 27, 35, directa=False)]])
        self.assertEqual(pagina.clics, [0])
        self.assertIn("elijo la de menor tiempo de tránsito, 33 días", log)
        # Las dos directas: también la de menor tránsito, sin descartar nada.
        r, pagina, log = self.elegir_hmm([[h(0, True, 27, 35, directa=True), h(1, True, 27, 33, directa=True)]])
        self.assertEqual(pagina.clics, [1])
        self.assertNotIn("prefiero", log)
        # La que no dice si es directa cuenta como con transbordo: gana la directa.
        r, pagina, _ = self.elegir_hmm([[h(0, True, 27, 33, directa=None), h(1, True, 27, 35, directa=True)]])
        self.assertEqual(pagina.clics, [1])
        # La directa solo desempata el mismo día: la con transbordo que sale antes gana.
        r, pagina, _ = self.elegir_hmm([[h(0, True, 27, 30, directa=True), h(1, True, 20, 40, directa=False)]])
        self.assertEqual(pagina.clics, [1])
        # Dos directas con el mismo tránsito, y una con transbordo que llega antes: empate entre las directas, NO ENVIADA.
        r, pagina, log = self.elegir_hmm([[h(0, True, 27, 33, directa=True), h(1, True, 27, 33, directa=True),
                                           h(2, True, 27, 30, directa=False)]])
        self.assertEqual((sorted(r), pagina.clics), (["corte"], []))
        self.assertIn("prefiero las 2 directas; descarto 1 con transbordo", log)

    def test_amplia_duration_si_no_esta(self):
        # Si ninguna tarjeta trae la nave como «1st Vessel», elige en «Duration» la opción más larga, busca de nuevo con
        # «Retrieve» y deja la evidencia de la lista ampliada (decisión de Marcelo, CICLO-ampliar-la-busqueda.md).
        h = self.hmm
        r, pagina, log = self.elegir_hmm([[h(0, False, 11, 28)], [h(0, False, 11, 28), h(1, True, 40, 33)]])
        self.assertEqual((r["idx"], pagina.clics, pagina.elegidas, pagina.busquedas), (1, [1], ["8 weeks"], 1))
        self.assertIn(("hmm_f9_naves_mas.png", False), pagina.capturas)
        self.assertIn("búsqueda ampliada: «Duration» de 2 a 8 semanas", log)
        # Si tampoco aparece: dice hasta qué fecha buscó.
        r, pagina, log = self.elegir_hmm([[h(0, False, 11, 28)], [h(0, False, 11, 28), h(1, False, 40, 33)]])
        cuarenta = datetime.date.today() + datetime.timedelta(days=40)
        self.assertEqual((r["idx"], r["motivo"], r["busqueda"][1], max(r["busqueda"][0]), pagina.clics),
                         (-1, "no_encontrada", self.mod.NO_AMPLIA_MAS, cuarenta, []))
        self.assertIn(f"busqué hasta el {cuarenta:%d-%m-%Y}, la última salida que mostró el portal", log)
        # Ya en la más larga: no la cambia ni busca de nuevo.
        r, pagina, _ = self.elegir_hmm([[h(0, False, 11, 28)], [h(0, True, 40, 33)]], semanas=8)
        self.assertEqual((r["motivo"], r["busqueda"][1], pagina.elegidas, pagina.busquedas),
                         ("no_encontrada", self.mod.NO_AMPLIA_MAS, [], 0))

    def test_duration_elige_la_mas_larga(self):
        casos = (({}, "", ["8 weeks"]), ({"semanas": 8}, self.mod.NO_AMPLIA_MAS, []),
                 ({"visible": False}, "no pude ampliar la búsqueda: no vi «Duration» a la vista", []),
                 ({"semanas": None}, "no pude ampliar la búsqueda: no pude leer las semanas de «Duration»", []),
                 ({"no_cambia": True}, "no pude ampliar la búsqueda: «Duration» quedó en 2 semanas, no en 8", ["8 weeks"]),
                 ({"falla": True}, "no pude ampliar la búsqueda: no pude elegir «8 weeks» en «Duration» (no hay tal opción)",
                  []))
        for k, (estado, esperado, elegidas) in enumerate(casos):
            with self.subTest(estado=estado):
                reg, _, _ = self.corrida(f"hmm_duration_{k}")
                pagina = PaginaListaHmm(self.mod, [[]], **estado)
                self.assertEqual(self.mod._hmm_ampliar(pagina, reg), esperado)
                self.assertEqual(pagina.elegidas, elegidas)

    def test_transito_y_salidas(self):
        d = datetime.date
        self.assertEqual(self.mod._hmm_salidas([{"salida": "2026-10-23"}, {"salida": ""}]),
                         [(d(2026, 10, 23), {"salida": "2026-10-23"}), (None, {"salida": ""})])
        for t, esperado in (({"salida": "2026-10-23", "llegada": "2026-11-25"}, datetime.timedelta(days=33)),
                            ({"salida": "2026-10-23", "llegada": ""}, None), ({"salida": "2026-10-23", "llegada": "2026-10-23"}, None),
                            ({}, None)):
            with self.subTest(t=t):
                self.assertEqual(self.mod._hmm_transito(t), esperado)

    def test_reservar_hyundai_elige_con_su_1st_vessel(self):
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_hyundai")
        asignas = {ast.unparse(n): n.lineno for n in ast.walk(f) if isinstance(n, ast.Assign)}
        self.assertIn("res_nave = _hmm_elegir_nave(page, reg, reserva, toks)", asignas)
        corte = [n for n in ast.walk(f) if isinstance(n, ast.If) and ast.unparse(n.test) == "res_nave.get('corte')"]
        self.assertEqual([ast.unparse(s) for s in corte[0].body], ["return res_nave['corte']"])
        self.assertIn("donde = f\": {_hasta_donde_busque(*res_nave['busqueda'])}\" if res_nave.get('busqueda') else ''",
                      asignas)
        self.assertLess(corte[0].lineno, linea_guarda(f))
        self.assertNotIn("_JS_HMM_INDICE_NAVE", ast.unparse(f))       # la elección vive en _hmm_elegir_nave

    def remark(self, titulos):
        """Corre _JS_HMM_REMARK sobre una pantalla falsa con la forma medida en hmm_f<fila>_remark.html (corrida del
        2026-09-25, CICLO-pendientes-con-evidencia.md): el título .box-title «Remark (n / m)» va dentro de un formulario
        con un solo textarea, sin id, name ni clase. Cada título es (texto, formulario): el formulario es (nombre, sus
        textarea con True si está a la vista), o None si el título no está en uno. Siempre hay además un textarea a la
        vista fuera de todo formulario, como el que hasta e423a38 recibía el Remark. Devuelve lo que responde, (valor,
        eventos) de cada textarea de cada formulario y el valor del de afuera."""
        guion = (
            "global.Event = class { constructor(t) { this.type = t; } };\n"
            "const ta = (vis) => ({offsetParent: vis ? {} : null, value: '', eventos: [],\n"
            "  scrollIntoView() {}, focus() {}, dispatchEvent(e) { this.eventos.push(e.type); }});\n"
            "const forms = new Map();\n"
            f"const titulos = {json.dumps(titulos)}.map(([t, f]) => {{\n"
            "  if (f !== null && !forms.has(f[0])) forms.set(f[0], {tas: f[1].map(ta)});\n"
            "  const form = f === null ? null : forms.get(f[0]);\n"
            "  return {textContent: t, closest: (s) => (s === 'form' ? form : null)}; });\n"
            "for (const f of forms.values()) f.querySelectorAll = (s) => (s === 'textarea' ? f.tas : []);\n"
            "const fuera = ta(true);\n"
            "global.document = {querySelectorAll: (s) => (s === '.box-title' ? titulos\n"
            "  : s === 'textarea' ? [fuera, ...[...forms.values()].flatMap(f => f.tas)] : [])};\n"
            "const f = " + self.mod._JS_HMM_REMARK + ";\n"
            "const r = f('REMARK SINTETICO');\n"
            "console.log(JSON.stringify([r, [...forms.values()].map(f => f.tas.map(t => [t.value, t.eventos])),\n"
            "  fuera.value]));\n")
        return correr_node(self, guion)

    def test_js_remark_en_el_campo_de_su_recuadro(self):
        # Medido: un solo título «Remark (0 / 4000)» y su formulario con un solo textarea a la vista.
        self.assertEqual(self.remark([("Remark (0 / 4000)", ("f", [True]))]),
                         ["ok", [[["REMARK SINTETICO", ["input", "change"]]]], ""])
        # El contador cambia al escribir y los espacios pueden variar: sigue siendo su recuadro.
        self.assertEqual(self.remark([(" Remark  (35 / 4000) ", ("f", [True]))])[0], "ok")

    def test_js_remark_no_escribe_en_otro_campo(self):
        # Sin su recuadro no escribe en ningún campo, tampoco en el textarea a la vista de afuera: hasta e423a38, el
        # primer textarea visible recibía el Remark.
        casos = (
            ([], "sin-titulo"),
            ([("Stowage Remark", ("f", [True]))], "sin-titulo"),
            ([("Remark", ("f", [True]))], "sin-titulo"),
            ([("Remark (0 / 4000)", ("f", [True])), ("Remark (0 / 500)", ("g", [True]))], "varios-titulos"),
            ([("Remark (0 / 4000)", None)], "sin-campo"),
            ([("Remark (0 / 4000)", ("f", []))], "sin-campo"),
            ([("Remark (0 / 4000)", ("f", [True, True]))], "varios-campos"),
            ([("Remark (0 / 4000)", ("f", [False]))], "oculto"),
        )
        for titulos, falta in casos:
            with self.subTest(falta=falta, titulos=titulos):
                r, formularios, fuera = self.remark(titulos)
                self.assertEqual(r, falta)
                self.assertEqual([c for f in formularios for c in f if c != ["", []]], [])
                self.assertEqual(fuera, "")

    def test_remark_sin_su_campo_corta_sin_escribir(self):
        reg, _, log = self.corrida("corrida_remark")
        motivos = {"sin-titulo": "el recuadro «Remark (n / m)» de Additional Information",
                   "varios-titulos": "un solo recuadro «Remark (n / m)»: hay más de uno y no elijo uno a ciegas",
                   "sin-campo": "el campo del recuadro «Remark (n / m)»",
                   "varios-campos": "un solo campo en el recuadro «Remark (n / m)»: hay más de uno y no elijo uno a "
                                    "ciegas",
                   "oculto": "el campo del recuadro «Remark (n / m)» a la vista: está oculto",
                   None: "el campo del recuadro «Remark (n / m)»"}
        for falta, buscaba in motivos.items():
            with self.subTest(falta=falta):
                with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
                    self.mod._hmm_remark(PaginaCma(js={"box-title": falta}), reg)
                self.assertEqual((e.exception.paso, e.exception.buscaba), ("Remark de HYUNDAI", buscaba))
        self.assertNotIn("Remark corporativo", log.read_text(encoding="utf-8"))
        # Con «ok» sigue, y lo anota.
        self.assertIsNone(self.mod._hmm_remark(PaginaCma(js={"box-title": "ok"}), reg))
        self.assertIn("    Remark corporativo: '", log.read_text(encoding="utf-8"))


class PaginaListaHmm(soporte.PaginaFalsa):
    """La lista de naves de HYUNDAI falsa: cada lote es lo que responde _JS_HMM_TARJETAS; «Retrieve» (por su rol, como
    lo pulsa _hmm_realclick) pasa al lote siguiente. «Duration» (_JS_HMM_SEMANAS) tiene 'semanas' elegidas de 1 a 8, y
    select_option la cambia (con 'no_cambia', no; con 'falla', levanta). _JS_HMM_INDICE_NAVE responde 'legado'. Anota
    los «Book Now» pulsados, las opciones elegidas y las búsquedas."""

    def __init__(self, mod, lotes, semanas=2, legado=None, visible=True, no_cambia=False, falla=False):
        super().__init__(texto=self.responder)
        self.mod, self.lotes, self.semanas, self.legado = mod, list(lotes), semanas, legado
        self.visible, self.no_cambia, self.falla = visible, no_cambia, falla
        self.clics, self.elegidas, self.busquedas, self.args_clic = [], [], 0, []

    def responder(self, js, *a):
        if js == self.mod._JS_HMM_TARJETAS:
            return self.lotes[0]
        if js == self.mod._JS_HMM_CLIC_TARJETA:
            self.clics.append(a[0]["i"])
            self.args_clic.append(a[0])
            return True
        if js == self.mod._JS_HMM_SEMANAS:
            return {"visible": self.visible, "actual": self.semanas,
                    "opciones": [{"texto": f"{n} weeks", "n": n} for n in range(1, 9)]}
        if js == self.mod._JS_HMM_INDICE_NAVE:
            return self.legado
        return None                                    # el HTML de la evidencia, y nada más

    def select_option(self, sel, label=None, timeout=None):
        if self.falla:
            raise RuntimeError("no hay tal opción")
        self.elegidas.append(label)
        if not self.no_cambia:
            self.semanas = int(label.split()[0])

    def get_by_role(self, rol, name=None, exact=False):
        pagina = self

        class Boton:
            first = property(lambda s: s)

            def scroll_into_view_if_needed(self, **k):
                pass

            def click(self, **k):
                pagina.busquedas += 1
                if len(pagina.lotes) > 1:
                    pagina.lotes.pop(0)
        return Boton()


class PaginaMaersk(soporte.PaginaFalsa):
    """Página falsa de MAERSK: se queda en «Additional details» y pasa a la revisión después de 'llega' esperas
    (con None, nunca). Da su HTML sin JavaScript. Con 'mod', a _JS_MK_LO_QUE_PIDE le responde 'pide'."""

    def __init__(self, llega=None, mod=None, pide=None):
        super().__init__(url="https://portal.invalid/book/additional-details")
        self.llega, self.mod, self.pide = llega, mod, pide

    def evaluate(self, js, *a):
        if self.mod is not None and js == self.mod._JS_MK_LO_QUE_PIDE:
            return self.pide
        return super().evaluate(js, *a)

    def wait_for_timeout(self, ms):
        super().wait_for_timeout(ms)
        if self.llega is not None and self.esperas >= self.llega:
            self.url = "https://portal.invalid/book/review"

    def content(self):
        return "<body>additional details sintetico</body>"


# Un DOM falso para correr en Node el JavaScript de MAERSK que recorre la página con sus raíces shadow (_JS_MK_RECORRER):
# el(etiqueta, atributos, hijos, opciones), con hijos que son elementos o textos. Con opciones.shadow, la raíz shadow (una
# lista de elementos); con opciones.oculto, sin cajas propias (getClientRects vacío, como display:none o, si lo de adentro
# se ve, display:contents); con opciones.invisible, con cajas pero checkVisibility falso (visibility:hidden); checked,
# type, value y labels se copian al elemento. click() anota el data-prueba del elemento en global.clics. Con
# childNodes y nodeType, cada texto es su propio nodo (encargo 38: el Shipper lee el texto nodo por nodo), y cada hijo
# sabe su parentElement (encargo 40: la casilla del Shipper se ubica entre sus hermanos).
DOM_AQ = r"""
global.clics = [];
const el = (tag, atributos = {}, hijos = [], opciones = {}) => {
  const e = {tagName: tag.toUpperCase(), nodeType: 1};
  e.children = hijos.filter(h => typeof h !== 'string');
  e.children.forEach(h => { h.parentElement = e; });
  e.childNodes = hijos.map(h => (typeof h === 'string' ? {nodeType: 3, nodeValue: h} : h));
  Object.defineProperty(e, 'textContent', {get() { return hijos.map(h => typeof h === 'string' ? h : h.textContent).join(''); }});
  e.getAttribute = a => (a in atributos ? String(atributos[a]) : null);
  e.hasAttribute = a => a in atributos;
  e.getClientRects = () => (opciones.oculto ? [] : [{}]);
  e.checkVisibility = () => !opciones.invisible;
  e.click = () => global.clics.push(atributos['data-prueba'] || tag);
  if (opciones.shadow) e.shadowRoot = {children: opciones.shadow, childNodes: opciones.shadow};
  for (const k of ['checked', 'type', 'value', 'labels']) if (k in opciones) e[k] = opciones[k];
  return e;
};
const pagina = (...hijos) => { global.document = {children: [el('html', {}, [el('body', {}, hijos)])]}; };
"""


class BotonRevision:
    """Un mc-button «Review booking» de PaginaRevision: se ve desde la espera 'desde' (None: nunca), mientras la página
    no haya pasado a la revisión. Si su página tiene 'falla', sus primeros clics fallan; con 'avanza', el que falla
    igual la lleva a la revisión (un clic que falló pudo haber salido)."""
    def __init__(self, pagina, desde):
        self.pagina, self.desde = pagina, desde

    def is_visible(self):
        p = self.pagina
        return self.desde is not None and p.esperas >= self.desde and "/review" not in p.url

    def scroll_into_view_if_needed(self, **k):
        pass

    def click(self, **k):
        p = self.pagina
        if p.falla:
            p.falla -= 1
            if p.avanza:
                p.url = "https://portal.invalid/book/review"
            raise RuntimeError("otro elemento recibiría el clic")
        p.clics.append("Review booking")


class PaginaRevision(soporte.PaginaFalsa):
    """«Additional details» falsa de MAERSK para «Review booking»: page.locator(selector).filter(has_text=…) anota su
    selector y su filtro (su patrón y si ignora mayúsculas) y da un BotonRevision por cada espera de 'botones'; con
    'rota', el localizador falla. _JS_MK_LO_QUE_PIDE responde 'pide'. Todo lo demás que se le pida (otro JavaScript, el
    teclado, el mouse…) queda en 'prohibidos' aunque el programa se trague el error: cada prueba exige esa lista vacía
    (revisión del encargo 38: con un try, el respaldo que pulsaba <html> volvía sin que la red lo viera)."""
    def __init__(self, mod, botones=(0,), falla=0, avanza=False, rota=False, pide=None):
        super().__init__(url="https://portal.invalid/book/additional-details")
        self.mod, self.falla, self.avanza, self.rota, self.pide = mod, falla, avanza, rota, pide
        self.main_frame, self.clics, self.buscado, self.prohibidos = None, [], [], []
        self.botones = [BotonRevision(self, d) for d in botones]

    def locator(self, selector):
        if self.rota:
            raise RuntimeError("la página se cerró")
        pagina = self

        def filtrar(has_text):
            pagina.buscado.append((selector, has_text.pattern, bool(has_text.flags & re.I)))
            b = pagina.botones
            return types.SimpleNamespace(count=lambda: len(b), nth=lambda i: b[i])
        return types.SimpleNamespace(filter=filtrar)

    def evaluate(self, js, *a):
        if js == self.mod._JS_MK_LO_QUE_PIDE:
            return self.pide
        if js == self.mod._JS_HTML_COMPLETO:
            return {}
        self.prohibidos.append("evaluate")
        raise AssertionError("JavaScript inesperado")

    def content(self):
        return "<body>review sintetico</body>"

    def __getattr__(self, nombre):
        if nombre.startswith("__"):
            raise AttributeError(nombre)
        self.__dict__.setdefault("prohibidos", []).append(nombre)
        raise AttributeError(nombre)


class PaginaSalidas(soporte.PaginaFalsa):
    """«Select sailing» falsa de MAERSK para _mk_desenlace_sailing, con su reloj: cada espera lo adelanta, y la prueba
    le da a time.time ese reloj. _JS_MK_SALIDAS responde, por espera, las tarjetas que da 'tarjetas' (el «Book» de cada
    una; si levanta una excepción, la levanta) y anota con qué lo leyó; «no sailings for your search» se ve desde la
    espera 'sin_salidas' (None: nunca). Lo demás que se le pida queda en 'prohibidos'; así, el «Book» del encabezado o
    el pie, que el detector contaba hasta el encargo 40 (a la vista, más abajo de 100 px)."""

    def __init__(self, mod, tarjetas=lambda n: [], sin_salidas=None):
        super().__init__(url="https://portal.invalid/book/sailings")
        self.mod, self.tarjetas, self.sin_salidas = mod, tarjetas, sin_salidas
        self.reloj, self.leidas, self.prohibidos = 1000.0, [], []

    def wait_for_timeout(self, ms):
        super().wait_for_timeout(ms)
        self.reloj += ms / 1000

    def evaluate(self, js, *a):
        if js != self.mod._JS_MK_SALIDAS:
            self.prohibidos.append("evaluate")
            raise AssertionError("JavaScript inesperado")
        self.leidas.append(a)
        return [{"i": i, "book": b} for i, b in enumerate(self.tarjetas(self.esperas))]

    def get_by_text(self, texto, exact=False):
        if (texto, exact) != ("no sailings for your search", False):
            self.prohibidos.append(("get_by_text", texto))
        visto = self.sin_salidas is not None and self.esperas >= self.sin_salidas
        aviso = types.SimpleNamespace(is_visible=lambda: visto,
                                      text_content=lambda: "There are no sailings for your search.")
        return types.SimpleNamespace(count=lambda: int(visto), first=aviso)

    def locator(self, selector):
        if selector == "text=/USD\\s*[\\d,.]+/i":
            return types.SimpleNamespace(count=lambda: 0)
        self.prohibidos.append(("locator", selector))
        enlace = types.SimpleNamespace(is_visible=lambda: True, bounding_box=lambda: {"y": 900, "height": 20})
        return types.SimpleNamespace(filter=lambda **k: types.SimpleNamespace(count=lambda: 1, nth=lambda i: enlace))

    def __getattr__(self, nombre):
        if nombre.startswith("__"):
            raise AttributeError(nombre)
        self.__dict__.setdefault("prohibidos", []).append(nombre)
        raise AttributeError(nombre)


class TestMaersk(ConRegistro):
    """MAERSK corta si la revisión no aparece, antes de los términos (CICLO-maersk-corta-en-la-revision.md), y el motivo
    dice lo que el portal pide (CICLO-maersk-retiro-y-terminos.md). La fecha de retiro, en TestRetiroMaersk."""
    BUSCABA = "la pantalla de revisión («Review booking»), que no apareció en 15 s"

    def test_revision_que_no_aparece_corta(self):
        pagina = PaginaMaersk()
        with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
            self.mod._mk_esperar_revision(pagina)
        self.assertEqual((e.exception.paso, e.exception.buscaba, e.exception.pide),
                         ("Revisión de MAERSK", self.BUSCABA, ""))             # sin avisos, el portal no pide nada
        self.assertEqual(pagina.esperas, 30)                                   # unos 15 s, como antes

    def test_el_corte_dice_lo_que_pide_el_portal(self):
        # Cuando el portal rechaza un paso, el motivo de la NO ENVIADA dice lo que pide, leído de la pantalla (decisión de
        # Marcelo, CICLO-maersk-retiro-y-terminos.md). Así cortó el 27-09, en «Additional details» sin la fecha de retiro:
        # hasta el encargo 36 el motivo decía solo que la revisión no apareció.
        def reservar(page, reserva, creds, reg, on_pausa=None):
            self.mod._mk_esperar_revision(page)
            return ("OK-EJEMPLO", "MAERSK: armada hasta Review; SIN emitir")
        reg, vistas, log = self.corrida("corrida_mk_pide")
        pagina = PaginaMaersk(mod=self.mod, pide={"campos": ["Pickup date"],
                                                  "mensajes": ["Pick up date cannot be left blank"]})
        r = self.mod._sin_clic_a_ciegas("mk")(reservar)(pagina, {"fila": 30}, {}, reg)
        detalle = ("Revisión de MAERSK: el portal pide: Pickup date («Pick up date cannot be left blank»). No encontré "
                   f"{self.BUSCABA}, así que no pulsé nada. La reserva no se envió; revisa ese paso en el portal.")
        self.assertEqual(r, ("NO ENVIADA", detalle))
        self.assertEqual(pagina.capturas, [("mk_f30_sin_objetivo.png", False)])
        for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):      # log.txt y pantalla
            self.assertIn(f"· ✗ NO ENVIADA · {detalle}", donde)

    def test_lo_que_pide_en_una_linea(self):
        casos = (({"campos": ["Pickup date"], "mensajes": ["Pick up date cannot be left blank"]},
                  "Pickup date («Pick up date cannot be left blank»)"),
                 ({"campos": ["Pickup date", "GenSet Import"], "mensajes": []}, "Pickup date, GenSet Import"),
                 ({"campos": [], "mensajes": ["Uno", "Dos"]}, "«Uno»; «Dos»"),
                 ({"campos": ["  Pickup\n date "]}, "Pickup date"),
                 ({}, ""), ("", ""), (None, ""))
        for respuesta, esperado in casos:
            with self.subTest(respuesta=respuesta):
                self.assertEqual(self.mod._mk_lo_que_pide(PaginaMaersk(mod=self.mod, pide=respuesta)), esperado)

        def rota(js, *a):
            raise RuntimeError("la página se cerró")
        self.assertEqual(self.mod._mk_lo_que_pide(soporte.PaginaFalsa(texto=rota)), "")

    def test_js_lo_que_pide(self):
        # La forma medida en mk_f10_sin_objetivo.html (27-09): el resumen, con su heading, nombra el campo en un enlace de
        # su pie (slot "actions"), fuera de la raíz shadow del aviso; el aviso del campo trae su mensaje en el atributo
        # body. Los avisos ocultos y los que no son de error no cuentan; un aviso dentro de la raíz shadow de otro
        # componente, sí. Los campos con el atributo invalid, por su label, como los leía _mk_errores (sin medir).
        guion = DOM_AQ + "const f = " + self.mod._JS_MK_LO_QUE_PIDE + r""";
const resumen = el('mc-notification', {heading: 'Please correct the following errors', appearance: 'error',
                                       'data-test': 'notificationError'},
  [el('footer', {slot: 'actions'}, [el('a', {href: '#containerPickupDatePicker'}, ['Pickup date'])])],
  {shadow: [el('div', {class: 'mc-notification error'}, [el('div', {class: 'heading', role: 'heading'},
            ['Please correct the following errors']), el('div', {class: 'body'}, [el('slot')])])]});
const campo = el('mc-notification', {appearance: 'error', body: 'Pick up date cannot be left blank',
                                     'data-test': 'haulage-invalid-date-footer'}, [],
                 {shadow: [el('div', {class: 'body'}, [el('slot')])]});
const oculto = el('mc-notification', {appearance: 'error', body: 'Otro aviso'}, [], {oculto: true});
const invisible = el('mc-notification', {appearance: 'error', body: 'Con visibility hidden'}, [], {invisible: true});
// Sin cajas propias, pero con lo de adentro a la vista (display:contents): sí cuenta.
const contenido = el('mc-notification', {appearance: 'error', body: 'Por su contenido'}, [],
                     {oculto: true, shadow: [el('div', {class: 'body'}, ['Por su contenido'])]});
const aviso = el('mc-notification', {appearance: 'warning'}, ['Additional charges can incur']);
const enSombra = el('mc-c-panel', {}, [], {shadow: [el('mc-notification', {appearance: 'error', body: 'En la sombra'})]});
// Un enlace a otra página no es un campo: queda como mensaje; el body se lee aunque haya campos.
const otraPagina = el('mc-notification', {appearance: 'error'}, [el('a', {href: '/reintentar'}, ['Try again'])]);
const conBody = el('mc-notification', {appearance: 'error', body: 'Revisa los campos'}, [el('a', {href: '#x'}, ['Campo X'])]);
const invalido = el('mc-select', {invalid: '', label: 'GenSet Import', errormessage: 'Required'});
const valido = el('mc-select', {invalid: 'false', label: 'Otro', errormessage: 'Nada'});
pagina(resumen, el('section', {}, [campo, oculto, invisible, contenido]), aviso, enSombra, otraPagina, conBody, invalido,
       valido);
const r = [f()];
pagina(aviso, valido);
r.push(f());
console.log(JSON.stringify(r));
"""
        con, sin = correr_node(self, guion)
        self.assertEqual(con, {"campos": ["Pickup date", "Campo X", "GenSet Import"],
                               "mensajes": ["Pick up date cannot be left blank", "Por su contenido", "En la sombra",
                                            "Try again", "Revisa los campos", "Required"]})
        self.assertEqual(sin, {"campos": [], "mensajes": []})

    def test_booking_information_dice_lo_que_pide(self):
        # «Booking Information» que no avanza queda NO ENVIADA (decisión de Marcelo, CICLO-maersk-ultimos-puntos.md;
        # hasta el encargo 37, REVISAR), y su motivo dice lo que pide el portal, con el mismo lector que la revisión
        # (_mk_lo_que_pide). Deja la evidencia de esa pantalla, cuyos avisos no están medidos. No pulsa nada.
        nada = "no pulsé nada más y la reserva no se envió"
        casos = (({"campos": ["Commodity"], "mensajes": ["Commodity is required"]},
                  f"el portal no dejó avanzar y pide: Commodity («Commodity is required»); {nada} (ruta=A-B)"),
                 (None, f"el portal no dejó avanzar, y no pude leer qué pide; {nada} (ruta=A-B)"))
        for i, (pide, que) in enumerate(casos):
            with self.subTest(pide=pide):
                reg, vistas, log = self.corrida(f"corrida_mk_booking_{i}")
                pagina = PaginaMaersk(mod=self.mod, pide=pide)
                r = self.mod._mk_booking_sin_avanzar(pagina, reg, ["ruta=A-B"], 30)
                detalle = f"MAERSK: en «Booking Information», {que}"
                self.assertEqual(r, ("NO ENVIADA", detalle))
                self.assertEqual(pagina.capturas, [("mk_f30_booking.png", False)])
                for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):      # log.txt y pantalla
                    self.assertIn(f"· ✗ NO ENVIADA · {detalle}", donde)

    def test_formulario_incompleto_dice_lo_que_pide(self):
        # Sin un botón para seguir que acepte el clic, NO ENVIADA con lo que pide el portal (decisión de Marcelo,
        # CICLO-maersk-shipper-y-cortes.md; hasta el encargo 38, REVISAR). No pulsa nada, y deja la evidencia de esa
        # pantalla (revisión del encargo 38).
        nada = "no pulsé nada más y la reserva no se envió"
        casos = (({"campos": ["Commodity"], "mensajes": ["Commodity is required"]},
                  f"formulario incompleto, y el portal pide: Commodity («Commodity is required»); {nada} (ruta=A-B)"),
                 (None, f"formulario incompleto, y no vi qué pide el portal; {nada} (ruta=A-B)"))
        for i, (pide, que) in enumerate(casos):
            with self.subTest(pide=pide):
                reg, vistas, log = self.corrida(f"corrida_mk_incompleto_{i}")
                pagina = PaginaMaersk(mod=self.mod, pide=pide)
                r = self.mod._mk_formulario_incompleto(pagina, reg, ["ruta=A-B"], 30)
                self.assertEqual(r, ("NO ENVIADA", f"MAERSK: {que}"))
                self.assertEqual(pagina.capturas, [("mk_f30_booking.png", False)])     # su evidencia
                for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):      # log.txt y pantalla
                    self.assertIn(f"· ✗ NO ENVIADA · MAERSK: {que}", donde)

    def test_los_cortes_antes_de_la_nave_son_no_enviada(self):
        # El formulario que no abre y el que queda incompleto (decisión de Marcelo, CICLO-maersk-shipper-y-cortes.md;
        # hasta el encargo 38, REVISAR), con su motivo. Desde el encargo 40, el incompleto lo dice
        # _mk_continuar_a_la_nave, cuando su botón está a la vista y no acepta el clic. La búsqueda de salidas que no
        # termina no corta (test_la_busqueda_de_salidas_no_corta).
        fuente = Path(self.mod.__file__).read_text(encoding="utf-8")
        funcs = {n.name: n for n in ast.parse(fuente).body if isinstance(n, ast.FunctionDef)}
        ramas = {ast.unparse(n.test): ast.unparse(n.body[-1])
                 for nombre in ("reservar_maersk", "_mk_continuar_a_la_nave")
                 for n in ast.walk(funcs[nombre]) if isinstance(n, ast.If)}
        esperado = {
            "not _mk_listo_para_reservar(page, _mk_cliente(reserva, creds), reg)":
                "return _no_enviada(reg, 'MAERSK: no se abrió el formulario /book/' + f'; {_MK_NADA_MAS}')",
            "res == 'clic'": "return _mk_formulario_incompleto(page, reg, det, f)",
        }
        self.assertEqual({k: ramas.get(k) for k in esperado}, esperado)

    def test_la_busqueda_de_salidas_no_corta(self):
        # A los 45 s sin desenlace, la búsqueda de salidas sigue a elegir la nave, y si no aparece, REVISAR por
        # _mk_sin_nave (decisión de Marcelo, CICLO-maersk-cuatro-puntos.md). Hasta el encargo 39, reservar_maersk tenía
        # una rama a NO ENVIADA para «indefinido», que _mk_desenlace_sailing nunca devuelve.
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        comparaciones = sorted(ast.unparse(c) for c in ast.walk(funcs["reservar_maersk"])
                               if isinstance(c, ast.Compare) and "desenlace" in ast.unparse(c.left))
        self.assertEqual(comparaciones, ["desenlace == 'sin-zarpes'"])
        devuelve = sorted({ast.unparse(r.value.elts[0]) for r in ast.walk(funcs["_mk_desenlace_sailing"])
                           if isinstance(r, ast.Return)})
        self.assertEqual(devuelve, ["'con-zarpes'", "'sin-zarpes'"])

    def test_a_los_45_s_sigue_a_buscar_la_nave(self):
        # Sin desenlace en el tiempo que espera, dice «con-zarpes» y lo anota: reservar_maersk sigue a elegir la nave.
        reg, _, log = self.corrida("corrida_mk_sin_desenlace")
        pagina = soporte.PaginaFalsa(url="https://portal.invalid/book/sailings")
        self.assertEqual(self.mod._mk_desenlace_sailing(pagina, reg, seg=0, minimo=0), ("con-zarpes", ""))
        self.assertIn("la búsqueda de zarpes tardó más de 0s; procedo a buscar naves", log.read_text(encoding="utf-8"))

    def salidas(self, **k):
        """Una corrida de _mk_desenlace_sailing sobre PaginaSalidas, con time.time en su reloj. Al terminar la
        prueba, la página no tiene que haber recibido nada prohibido."""
        pagina = PaginaSalidas(self.mod, **k)
        self.addCleanup(lambda: self.assertEqual(pagina.prohibidos, []))
        self.n = getattr(self, "n", 0) + 1
        reg, _, log = self.corrida(f"corrida_mk_salidas_{self.n}")
        with mock.patch("time.time", lambda: pagina.reloj):
            r = self.mod._mk_desenlace_sailing(pagina, reg)
        return r, pagina, log.read_text(encoding="utf-8")

    def test_el_book_del_encabezado_no_termina_la_busqueda(self):
        # El 29-09 la página guardada dice «no sailings for your search», y el detector había terminado a los 2 s, lo
        # más probable es que con un enlace «Book» del encabezado o el pie: la fila quedó REVISAR y no SIN-CUPO. Cuenta
        # solo el «Book» de una
        # tarjeta de salida, como la lista (decisión de Marcelo, CICLO-maersk-busqueda-vacia.md): sigue esperando, y
        # termina con el aviso del portal.
        r, pagina, log = self.salidas(sin_salidas=5)
        self.assertEqual(r, ("sin-zarpes", "There are no sailings for your search."))
        self.assertEqual(pagina.esperas, 5)
        self.assertIn("el portal responde: no hay zarpes (6.0s)", log)

    def test_una_tarjeta_con_su_book_termina_la_busqueda(self):
        # La lista la lee _JS_MK_SALIDAS, con lo mismo que _mk_elegir_nave para contar el «Book» de cada tarjeta.
        r, pagina, log = self.salidas(tarjetas=lambda n: [0, 1] if n >= 3 else [])
        self.assertEqual(r, ("con-zarpes", ""))
        self.assertEqual(pagina.esperas, 3)
        self.assertIn("salidas con su «Book» en la página (4.0s)", log)      # no mira si se ven: «en la página»
        self.assertEqual({json.dumps(a) for a in pagina.leidas}, {json.dumps([{"toks": [], "viaje": ""}])})

    def test_tarjetas_sin_book_no_terminan_la_busqueda(self):
        # Tarjetas sin «Book» (el portal no deja reservarlas) no son un desenlace: a los 45 s sigue a buscar la nave,
        # como sin desenlace.
        r, pagina, log = self.salidas(tarjetas=lambda n: [0, 0])
        self.assertEqual(r, ("con-zarpes", ""))
        self.assertEqual(pagina.esperas, 44)
        self.assertIn("la búsqueda de zarpes tardó más de 45s; procedo a buscar naves", log)

    def test_si_no_puede_leer_las_tarjetas_sigue_esperando(self):
        def tarjetas(n):
            if n < 3:
                raise RuntimeError("la página todavía carga")
            return [1]
        r, pagina, _ = self.salidas(tarjetas=tarjetas)
        self.assertEqual((r, pagina.esperas), (("con-zarpes", ""), 3))

    def test_sin_cupo_deja_la_evidencia_de_select_sailing(self):
        # Con «no sailings for your search», SIN-CUPO, y deja además de su captura la evidencia de «Select sailing»
        # (_mk_detenida), como cuando la nave no está: con la del 29-09 se midió qué destino buscó
        # (CICLO-maersk-busqueda-vacia.md).
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_maersk")
        [rama] = [n for n in ast.walk(f)
                  if isinstance(n, ast.If) and ast.unparse(n.test) == "desenlace == 'sin-zarpes'"]
        cuerpo = [ast.unparse(s) for s in rama.body]
        self.assertIn("_mk_detenida(page, reg, f)", cuerpo)
        self.assertTrue(cuerpo[-1].startswith("return ('SIN-CUPO', "), cuerpo[-1])

    def test_sin_cupo_dice_el_origen_y_el_destino_con_que_busco(self):
        # El motivo de SIN-CUPO dice con qué origen y destino buscó: de cada campo, lo que devolvió _mk_ciudad, la
        # sugerencia que pulsó y, si el campo no quedó con ella, lo que quedó (decisión de Marcelo,
        # CICLO-origen-y-destino.md; revisión del encargo 41). El 29-09, la búsqueda volvió vacía con otro destino que
        # el de la fila, y el motivo no lo decía (CICLO-maersk-busqueda-vacia.md).
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_maersk")
        asignadas = sorted((ast.unparse(n.targets[0]), ast.unparse(n.value)) for n in ast.walk(f)
                           if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) in ("origen", "destino"))
        self.assertEqual(asignadas, [
            ("destino", "_mk_ciudad(page, dest, reg, 'Destino', campo='destination', evidencia=f'mk_f{f}_destino')"),
            ("origen", "_mk_ciudad(page, reserva['pol'], reg, 'Origen', campo='origin', evidencia=f'mk_f{f}_origen')")])
        [rama] = [n for n in ast.walk(f)
                  if isinstance(n, ast.If) and ast.unparse(n.test) == "desenlace == 'sin-zarpes'"]
        self.assertEqual(ast.unparse(rama.body[-1]),
                         "return ('SIN-CUPO', _mk_motivo_sin_cupo(aviso, det, origen, destino))")
        alfa, beta = ("PUERTO ALFA, PAIS", "PUERTO ALFA, PAIS"), ("PUERTO BETA, OTRO PAIS", "PUERTO BETA, OTRO PAIS")
        self.assertEqual(self.mod._mk_motivo_sin_cupo("There are no sailings for your search.",
                                                      ["commodity=X", "reefer"], alfa, beta),
                         'MAERSK dice: "There are no sailings for your search."; busqué con origen «PUERTO ALFA, PAIS» '
                         'y destino «PUERTO BETA, OTRO PAIS» (formulario completo: commodity=X, reefer; SIN emitir)')
        r = self.mod._mk_ruta_buscada
        self.assertEqual(r(alfa, ("PUERTO BETA, OTRO PAIS", "PUERTO BETA")),
                         "origen «PUERTO ALFA, PAIS» y destino «PUERTO BETA, OTRO PAIS» (el campo quedó con "
                         "«PUERTO BETA»)")
        self.assertEqual(r(("", ""), beta),
                         "origen (ninguna sugerencia quedó en el campo) y destino «PUERTO BETA, OTRO PAIS»")
        self.assertEqual(r(alfa, ("", "")),
                         "origen «PUERTO ALFA, PAIS» y destino (ninguna sugerencia quedó en el campo)")

    def test_el_motivo_de_sin_cupo_no_se_pinta_de_verde(self):
        # Revisión del encargo 41: el registro del panel pinta cada línea con clase (JS_INDEX), y una línea con una
        # palabra como «elegida» sale verde, como un OK. La de una reserva SIN-CUPO no puede salir así, diga lo que diga
        # su motivo.
        m = re.search(r"^function clase\(l\) \{\n.*?\n\}\n", self.mod.JS_INDEX, re.S | re.M)
        self.assertIsNotNone(m, "no encontré clase en JS_INDEX")
        vacio, alfa = ("", ""), ("PUERTO ALFA, PAIS", "PUERTO ALFA, PAIS")
        aviso = "There are no sailings for your search."
        lineas = [f"· Reserva 1: SIN-CUPO ({self.mod._mk_motivo_sin_cupo(aviso, ['reefer'], o, d)})"
                  for o, d in ((alfa, alfa), (vacio, vacio), (alfa, ("PUERTO ALFA, PAIS", "PUERTO")))]
        clases = correr_node(self, m.group(0) + f"console.log(JSON.stringify({json.dumps(lineas)}"
                                                ".map(l => clase(l)[0])));\n")
        self.assertEqual(len(clases), 3)
        self.assertNotIn("f-ok", clases)

    def test_revisar_solo_si_la_nave_no_esta(self):
        # Antes del botón final, MAERSK devuelve REVISAR solo desde _mk_sin_nave (la nave de la fila no está en sus
        # itinerarios): en lo que corre antes de su guarda y en lo que eso llama, el estado «REVISAR» no aparece en otro
        # lugar (decisión de Marcelo, CICLO-maersk-shipper-y-cortes.md).
        fuente = Path(self.mod.__file__).read_text(encoding="utf-8")
        tree = ast.parse(fuente)
        tramo, vistas, _ = universo(tree)["reservar_maersk"]
        funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        lugares = [("reservar_maersk", n) for n in tramo] + [(x, funcs[x]) for x in vistas]
        con_revisar = sorted({lugar for lugar, nodo in lugares for c in ast.walk(nodo)
                              if isinstance(c, ast.Constant) and c.value == "REVISAR"})
        self.assertEqual(con_revisar, ["_mk_sin_nave"])

    def test_booking_information_no_avanza_corta(self):
        # En reservar_maersk, «Booking Information» que no avanzó corta con _mk_booking_sin_avanzar, sin más.
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_maersk")
        rama = [n for n in ast.walk(f) if isinstance(n, ast.If) and ast.unparse(n.test) == "not avanzo"]
        self.assertEqual(len(rama), 1)
        self.assertEqual([ast.unparse(s) for s in rama[0].body], ["return _mk_booking_sin_avanzar(page, reg, det, f)"])

    def revisar(self, pagina):
        """Una corrida para _mk_pulsar_revision; al terminar la prueba, la página no tiene que haber recibido nada
        prohibido."""
        self.n = getattr(self, "n", 0) + 1
        self.addCleanup(lambda: self.assertEqual(pagina.prohibidos, []))
        return self.corrida(f"corrida_mk_revision_{self.n}")

    def test_review_booking_por_su_texto(self):
        # «Review booking»: el único mc-button a la vista con ese texto, buscado hasta 15 veces, sin ningún JavaScript
        # (decisión de Marcelo, CICLO-maersk-shipper-y-cortes.md). Hasta el encargo 38 pulsaba por JavaScript el primer
        # elemento a la vista cuyo texto lo traía, que era <html>; hasta su revisión, el primero entre botones y
        # enlaces, visible o no.
        buscado = ("mc-button", "Review booking", True)
        casos = ((dict(), 0), (dict(botones=(3,)), 3), (dict(falla=1), 1),
                 (dict(botones=(None, 0)), 0))                # uno oculto antes del que se ve: pulsa el que se ve
        for opciones, esperas in casos:
            with self.subTest(**opciones):
                pagina = PaginaRevision(self.mod, **opciones)
                reg, _, log = self.revisar(pagina)
                self.assertIsNone(self.mod._mk_pulsar_revision(pagina, reg, 30))
                self.assertEqual((pagina.clics, pagina.esperas), (["Review booking"], esperas))
                self.assertEqual(pagina.buscado, [buscado] * (esperas + 1))
                self.assertIn("pulsado 'Review booking'", log.read_text(encoding="utf-8"))

    def test_la_revision_ya_aparecio(self):
        # Un clic que falló pudo haber salido: si la revisión ya apareció, no se busca otra vez ni se corta.
        pagina = PaginaRevision(self.mod, falla=1, avanza=True)
        reg, _, log = self.revisar(pagina)
        self.assertIsNone(self.mod._mk_pulsar_revision(pagina, reg, 30))
        self.assertEqual((pagina.clics, pagina.esperas), ([], 1))
        self.assertIn("la revisión ya apareció; no hace falta pulsar 'Review booking'", log.read_text(encoding="utf-8"))

    def test_sin_review_booking_corta(self):
        casos = ((dict(botones=(None,)), "había 0"), (dict(botones=(0, 0)), "había 2"),
                 (dict(rota=True), "no pude leer la página: RuntimeError: la página se cerró"))
        for opciones, cuantos in casos:
            with self.subTest(**opciones):
                pagina = PaginaRevision(self.mod, pide={"campos": ["Pickup date"], "mensajes": []}, **opciones)
                reg, _, _ = self.revisar(pagina)
                with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
                    self.mod._mk_pulsar_revision(pagina, reg, 30)
                self.assertEqual((e.exception.paso, e.exception.buscaba, e.exception.pide),
                                 ("Review booking de MAERSK", f"un solo botón «Review booking» a la vista, por su "
                                                              f"texto, en 15 intentos ({cuantos})", "Pickup date"))
                self.assertEqual((pagina.clics, pagina.esperas), ([], 14))

    def test_review_booking_que_no_acepta_el_clic(self):
        # A la vista, pero sin aceptar el clic: el motivo lo dice, con su evidencia (revisión del encargo 38: decía «no
        # encontré» y «no pulsé nada», y tardaba unos 76 s).
        pagina = PaginaRevision(self.mod, falla=15)
        reg, vistas, log = self.revisar(pagina)
        r = self.mod._mk_pulsar_revision(pagina, reg, 30)
        detalle = ("MAERSK: el botón «Review booking» estaba a la vista, pero no aceptó el clic (RuntimeError: otro "
                   "elemento recibiría el clic); no pulsé nada más y la reserva no se envió")
        self.assertEqual((r, pagina.clics, pagina.esperas), (("NO ENVIADA", detalle), [], 14))
        self.assertEqual(pagina.capturas, [("mk_f30_revision.png", False)])
        for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):      # log.txt y pantalla
            self.assertIn(f"· ✗ NO ENVIADA · {detalle}", donde)

    def test_reservar_maersk_pulsa_la_revision_sin_respaldo(self):
        # Una sola llamada, que corta si hace falta, después del Shipper y antes de esperar la revisión; y ningún
        # JavaScript que busque «Review booking» en la página.
        fuente = Path(self.mod.__file__).read_text(encoding="utf-8")
        f = next(n for n in ast.parse(fuente).body if isinstance(n, ast.FunctionDef) and n.name == "reservar_maersk")
        cuerpos = [n.body for n in ast.walk(f) if isinstance(getattr(n, "body", None), list)]
        cuerpo, i = next((c, i) for c in cuerpos for i, s in enumerate(c)
                         if ast.unparse(s) == "corte = _mk_pulsar_revision(page, reg, f)")
        self.assertEqual(ast.unparse(cuerpo[i + 1]), "if corte:\n    return corte")
        llamadas = {n: [c for c in ast.walk(f) if isinstance(c, ast.Call) and getattr(c.func, "id", "") == n]
                    for n in ("_mk_shipper", "_mk_pulsar_revision", "_mk_esperar_revision")}
        self.assertEqual(len(llamadas["_mk_pulsar_revision"]), 1)
        orden = [llamadas[n][0].lineno for n in ("_mk_shipper", "_mk_pulsar_revision", "_mk_esperar_revision")]
        self.assertEqual(orden, sorted(orden))
        respaldos = [ast.unparse(c) for c in ast.walk(f) if isinstance(c, ast.Call)
                     and ast.unparse(c.func).endswith(".evaluate") and "Review booking" in ast.unparse(c)]
        self.assertEqual(respaldos, [])

    def test_revision_que_aparece_sigue(self):
        pagina = PaginaMaersk(llega=3)
        self.assertIsNone(self.mod._mk_esperar_revision(pagina))
        self.assertEqual(pagina.esperas, 3)

    def test_el_corte_queda_no_enviada_con_captura_y_html(self):
        def reservar(page, reserva, creds, reg, on_pausa=None):
            self.mod._mk_esperar_revision(page)
            return ("OK-EJEMPLO", "MAERSK: armada hasta Review; SIN emitir")
        reg, vistas, log = self.corrida("corrida_mk")
        pagina = PaginaMaersk()
        r = self.mod._sin_clic_a_ciegas("mk")(reservar)(pagina, {"fila": 30}, {}, reg)
        detalle = (f"Revisión de MAERSK: no encontré {self.BUSCABA}, así que no pulsé nada. La reserva no se envió; "
                   "revisa ese paso en el portal.")
        self.assertEqual(r, ("NO ENVIADA", detalle))
        self.assertEqual(pagina.capturas, [("mk_f30_sin_objetivo.png", False)])
        self.assertIn("additional details sintetico",
                      (self.sb / "corrida_mk" / "mk_f30_sin_objetivo.html").read_text(encoding="utf-8"))
        for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):      # log.txt y pantalla
            self.assertIn(f"· ✗ NO ENVIADA · {detalle}", donde)

    def test_espera_la_revision_antes_de_los_terminos(self):
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_maersk")
        llamadas = [c.lineno for c in ast.walk(f)
                    if isinstance(c, ast.Call) and getattr(c.func, "id", "") == "_mk_esperar_revision"]
        cuerpos = [n.body for n in ast.walk(f) if isinstance(getattr(n, "body", None), list)]
        cuerpo, i = next((c, i) for c in cuerpos for i, s in enumerate(c)
                         if ast.unparse(s) == "corte = _mk_marcar_terminos(page, reg, f)")
        self.assertEqual(ast.unparse(cuerpo[i + 1]), "if corte:\n    return corte")
        self.assertEqual(len(llamadas), 1, "la revisión se espera una vez, con la ayuda que corta")
        self.assertLess(llamadas[0], cuerpo[i].lineno, "tiene que cortar antes de marcar los términos")
        self.assertLess(cuerpo[i].lineno, linea_guarda(f))
        # Ningún checkbox por su tipo en el reservador: hasta el encargo 36, «el último checkbox» estaba escrito ahí.
        self.assertEqual([n.lineno for n in ast.walk(f)
                          if isinstance(n, ast.Constant) and isinstance(n.value, str) and "checkbox" in n.value], [])

    def test_sin_nave_se_detiene_en_select_sailing(self):
        reg, vistas, log = self.corrida("corrida_mk_sin_nave")
        pagina = PaginaMaersk()
        r = self.mod._mk_sin_nave(pagina, reg, {"fila": 30, "nave": "NAVE SINTETICA"}, ["origen=X"])
        self.assertEqual(r, ("REVISAR", "MAERSK: me detuve en «Select sailing»: la nave 'NAVE SINTETICA' no está en "
                                        "los itinerarios (origen=X); SIN emitir"))
        self.assertEqual(pagina.capturas, [("mk_f30_detenida.png", False)])
        self.assertTrue((self.sb / "corrida_mk_sin_nave" / "mk_f30_detenida.html").exists())
        for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):
            self.assertIn("· Me detuve en «Select sailing»: la nave de la fila no está en los itinerarios de MAERSK.",
                          donde)
            self.assertNotIn("Review", donde)

    def test_sin_nave_dice_hasta_donde_busco(self):
        # Con lo que buscó (_mk_elegir_nave), el REVISAR dice hasta qué fecha: la última salida que mostró el portal, y
        # por qué dejó de ampliar (decisión de Marcelo, CICLO-ampliar-la-busqueda.md). Hasta 4cae528 no lo decía.
        hoy = datetime.date.today()
        treinta = hoy + datetime.timedelta(days=30)
        reg, vistas, log = self.corrida("corrida_mk_hasta")
        pagina = PaginaMaersk()
        fechas = [hoy + datetime.timedelta(days=2), None, treinta]
        r = self.mod._mk_sin_nave(pagina, reg, {"fila": 30, "nave": "NAVE SINTETICA"}, ["origen=X"],
                                  (fechas, self.mod.NO_AMPLIA_MAS))
        self.assertEqual(r, ("REVISAR", f"MAERSK: me detuve en «Select sailing»: la nave 'NAVE SINTETICA' no está en "
                                        f"los itinerarios: busqué hasta el {treinta:%d-%m-%Y}, la última salida que "
                                        "mostró el portal, y el portal no deja ampliar más la búsqueda (origen=X); SIN "
                                        "emitir"))
        self.assertEqual(pagina.capturas, [("mk_f30_detenida.png", False)])

    def test_sin_nave_no_llega_a_la_guarda(self):
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_maersk")
        corte = [n for n in ast.walk(f) if isinstance(n, ast.If) and ast.unparse(n.test) == "not modo"]
        eleccion = [n for n in ast.walk(f) if isinstance(n, ast.Assign) and "_mk_elegir_nave" in ast.unparse(n.value)]
        self.assertEqual(len(corte), 1, "sin nave, MAERSK tiene que detenerse antes de la guarda")
        self.assertEqual(ast.unparse(corte[0].body[0]), "return _mk_sin_nave(page, reg, reserva, det, sin_nave)")
        self.assertLess(eleccion[0].lineno, corte[0].lineno)
        self.assertLess(corte[0].lineno, linea_guarda(f))

    # --- La próxima salida en «Select sailing» (CICLO-proxima-salida.md): la forma medida en mk_f30_detenida.html ---
    MESES = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

    @classmethod
    def salida(cls, n):
        """La salida a n días de hoy, como la muestra MAERSK: «4 Oct 2026, 18:00» (los meses a mano, sin locale)."""
        d = datetime.date.today() + datetime.timedelta(days=n)
        return f"{d.day} {cls.MESES[d.month - 1]} {d.year}, 18:00"

    DOM_MK = r"""
const nodo = (tag, cls, texto, hijos = [], role, atributos = {}) => {
  const n = {tagName: tag.toUpperCase(), className: cls, texto, hijos, role, parentElement: null};
  Object.defineProperty(n, 'textContent', {get() { return [this.texto, ...this.hijos.map(h => h.textContent)].join(''); }});
  n.getAttribute = (a) => (a in atributos ? atributos[a] : null);
  // Para el HTML entero (encargo 43): su etiqueta, sus atributos (la clase primero), su raíz shadow y getHTML.
  n.localName = tag;
  n.attributes = Object.entries(Object.assign(cls ? {class: cls} : {}, atributos))
    .map(([name, value]) => ({name, value}));
  n.shadowRoot = null;
  n.getHTML = function ({shadowRoots = []} = {}) { return htmlDe(this, shadowRoots); };
  const calza = (e, sel) => sel.split(',').map(s => s.trim()).some(s => {
    if (s === '*') return true;
    const r = s.match(/^\[role=['"]?(\w+)['"]?\]$/);
    if (r) return e.role === r[1];
    const m = s.match(/^([a-z-]*)((?:\.[\w-]+)*)$/);
    if (!m) return false;
    const clases = (e.className || '').split(/\s+/);
    return (!m[1] || m[1] === e.tagName.toLowerCase()) && m[2].split('.').filter(Boolean).every(c => clases.includes(c));
  });
  n.querySelectorAll = function (sel) {
    const out = []; const walk = (x) => { for (const h of x.hijos) { if (calza(h, sel)) out.push(h); walk(h); } };
    walk(this); return out; };
  n.querySelector = function (sel) { return this.querySelectorAll(sel)[0] || null; };
  hijos.forEach(h => { h.parentElement = n; });
  return n;
};
// El contenido de un nodo falso como lo da getHTML: su raíz shadow, si está entre las pedidas, como plantilla
// declarativa; su texto, y cada hijo con su etiqueta y sus atributos.
const htmlDe = (x, raices) => (x.shadowRoot && raices.includes(x.shadowRoot)
  ? '<template shadowrootmode="open">' + htmlDe(x.shadowRoot, raices) + '</template>' : '') + x.texto
  + x.hijos.map(h => '<' + h.localName + h.attributes.map(a => ` ${a.name}="${a.value}"`).join('') + '>'
                + htmlDe(h, raices) + '</' + h.localName + '>').join('');
// La raíz shadow de un nodo falso, con estos hijos.
const sombra = (n, hijos) => {
  n.shadowRoot = {texto: '', hijos, shadowRoot: null, querySelectorAll: n.querySelectorAll};
  return n;
};
const bloque = (etq, valor) => nodo('div', 'new-sailings-group-header__content', '', [
  nodo('span', 'new-sailings-group-header__label', etq), nodo('span', 'new-sailings-group-header__value', valor)]);
// El «Book» medido en los 6 mk_f*_detenida.html (25 al 27-09): un mc-button con label="Book" y el texto dentro de su raíz
// shadow, que querySelectorAll no alcanza: su textContent viene vacío. Con reservable = 'texto', el «Book» como texto del
// mc-button, que ninguna lista guardada trae (el programa también lo cuenta). Las que no se pueden reservar traen sus otros
// mc-button, con su texto, y ningún «Book».
const book = (forma) => forma === 'texto' ? nodo('mc-button', '', 'Book')
  : nodo('mc-button', '', '', [], undefined, {label: 'Book', 'data-test': 'sailings-book-btn'});
const salida = (dep, nave, reservable = true, destino = 'Shanghai', transito = '44 days 6 hours') => nodo('mc-card',
  'new-sailings-card mds', '', [
  nodo('header', 'new-sailings-group-header', '', [bloque('Departure', dep), bloque('Transit time', transito),
    bloque('Arrival', '9 Nov 2026, 06:00'), bloque('Vessel/voyage', nave), bloque('Gate-in deadline', '24 Sep 2026, 12:00')]),
  nodo('div', 'new-sailings-route', 'San Antonio -> ' + destino),
  nodo('mc-button', '', 'Route & other details'),
  nodo('div', 'product-offer-card-action-btn', '', reservable ? [book(reservable)] : []),
  nodo('mc-button', '', 'Price breakdown & details')]);
const pagina = (salidas) => {
  const body = nodo('body', '', '', [nodo('mc-card', 'otra-cosa', '', [nodo('mc-button', '', 'Book')]),
                                     nodo('section', 'booking sailings', '', salidas)]);
  global.document = {querySelectorAll: (s) => body.querySelectorAll(s)};
};
"""

    def test_js_book_por_su_label(self):
        # El «Book» de MAERSK lleva su texto dentro de la raíz shadow del mc-button, y su textContent viene vacío: se
        # cuenta por su atributo label (medido en los 6 mk_f*_detenida.html del 25 al 27-09: 42 de 52 tarjetas lo traen,
        # ninguna como texto). Hasta el encargo 34 se contaba solo por el texto: daba 0 en todas, y la salida pedida, con
        # su «Book», quedaba «ya no se puede reservar» (CICLO-one-y-maersk-eligen-la-nave.md). El texto también cuenta.
        guion = self.DOM_MK + "const f = " + self.mod._JS_MK_SALIDAS + r""";
pagina([salida('4 Oct 2026, 18:00', 'MAERSK OTRA / 539W'), salida('11 Oct 2026, 18:00', 'MAERSK NAVE / 540W'),
        salida('18 Oct 2026, 18:00', 'MAERSK NAVE / 541W', 'texto'), salida('25 Oct 2026, 18:00', 'MAERSK NAVE / 542W', false)]);
console.log(JSON.stringify(f({toks: ['MAERSK', 'NAVE'], viaje: '540W'}).map(x => [x.calza, x.viaje, x.book])));
"""
        self.assertEqual(correr_node(self, guion), [[False, False, 1], [True, True, 1], [True, False, 1], [True, False, 0]])

    def test_js_salidas_lee_la_salida_y_si_se_puede_reservar(self):
        guion = self.DOM_MK + "const f = " + self.mod._JS_MK_SALIDAS + r""";
pagina([salida('26 Sep 2026, 18:00', 'MAERSK NAVE / 539W', false),
        salida('4 Oct 2026, 18:00', 'MAERSK OTRA / 540W', true, 'Shanghai', '40 days'),
        salida('11 Oct 2026, 18:00', 'MAERSK NAVE / 541W')]);
const r = [f({toks: ['MAERSK', 'NAVE'], viaje: ''}), f({toks: ['NAVE', 'MAERSK'], viaje: ''}),
           f({toks: ['MAERSK', 'NAVE'], viaje: '541W'}), f({toks: [], viaje: ''})];
// Una nave con nombre de puerto y la tarjeta de otra que va a ese puerto.
pagina([salida('4 Oct 2026, 18:00', 'MAERSK OTRA / 540W', true, 'Kolkata'),
        salida('11 Oct 2026, 18:00', 'MAERSK KOLKATA / 541W', true, 'Shanghai')]);
r.push(f({toks: ['MAERSK', 'KOLKATA'], viaje: ''}));
pagina([salida('4 Oct 2026, 18:00', 'MAERSK SAVANNAH / 540W', true), salida('11 Oct 2026, 18:00', 'MAERSK ANNA / 541W', true)]);
r.push(f({toks: ['MAERSK', 'ANNA'], viaje: ''}));
// El viaje de la fila dentro de otro viaje: antes y después de él.
pagina([salida('4 Oct 2026, 18:00', 'MAERSK NAVE / 1541W'), salida('11 Oct 2026, 18:00', 'MAERSK NAVE / 541W'),
        salida('18 Oct 2026, 18:00', 'MAERSK NAVE / 541WA'), salida('25 Oct 2026, 18:00', 'MAERSK NAVE/541W')]);
console.log(JSON.stringify(r.concat([f({toks: ['MAERSK', 'NAVE'], viaje: '541W'}),
                                      f({toks: ['MAERSK', 'NAVE'], viaje: '541w'})])));
"""
        normal, al_reves, con_viaje, sin_nave, puerto, entera, viaje_entero, en_minusculas = correr_node(self, guion)
        # Cada salida, con su «Transit time»: hasta 2825153 no lo traía (CICLO-cola-tres-items.md).
        s = lambda i, calza, salida, book, transito="44 days 6 hours": {"i": i, "calza": calza, "viaje": False,
                                                                        "salida": salida, "transito": transito, "book": book}
        self.assertEqual(normal, [s(0, True, "26 Sep 2026, 18:00", 0), s(1, False, "4 Oct 2026, 18:00", 1, "40 days"),
                                  s(2, True, "11 Oct 2026, 18:00", 1)])      # la que no trae «Book» se ve igual
        self.assertEqual([x["calza"] for x in al_reves], [False, False, False])     # las palabras, en orden
        self.assertEqual([x["viaje"] for x in con_viaje], [False, False, True])
        self.assertEqual([x["calza"] for x in sin_nave], [False, False, False])
        # Se compara con el valor de «Vessel/voyage», no con toda la tarjeta: hasta 9051f43 la primera también calzaba,
        # por su destino (CICLO-cola-tres-items.md).
        self.assertEqual([x["calza"] for x in puerto], [False, True])
        # Cada palabra, entera, en su orden: hasta f68ce6c «ANNA» calzaba dentro de «SAVANNAH», [True, True]
        # (CICLO-cola-seis-items.md).
        self.assertEqual([x["calza"] for x in entera], [False, True])
        # El viaje, también entero: hasta c4df3ab «541W» calzaba dentro de «1541W» y de «541WA», [True, True, True, True]
        # (CICLO-inicio-de-todas.md). Pegado a la barra sí es entero: la barra no es letra ni número.
        self.assertEqual([x["viaje"] for x in viaje_entero], [False, True, False, True])
        # Sin distinguir mayúsculas: el viaje llega de la planilla tal como está escrito.
        self.assertEqual([x["viaje"] for x in en_minusculas], [False, True, False, True])

    def test_js_salidas_dice_la_primera_con_su_mismo_html(self):
        # Con 'iguales', cada tarjeta dice la primera con su mismo HTML entero: su etiqueta con sus atributos y su
        # contenido con sus raíces shadow, armado como la evidencia (_JS_HTML_ENTERO; decisión de Marcelo, encargo 43).
        # Una que difiere solo dentro de su raíz shadow, o en un atributo, es otra; una sin getHTML cuenta aparte,
        # aunque haya otra igual. Sin 'iguales', la lectura es la de siempre: no trae «igual».
        guion = self.DOM_MK + "const f = " + self.mod._JS_MK_SALIDAS + r""";
const a = (precio = '1 USD') => sombra(salida('18 Oct 2026, 08:30', 'MAERSK NAVE / 541W'),
                                       [nodo('span', 'precio', precio)]);
const otra = sombra(salida('25 Oct 2026, 08:30', 'MAERSK NAVE / 542W'), [nodo('span', 'precio', '1 USD')]);
pagina([a(), a(), a('2 USD'), otra]);
const toks = ['MAERSK', 'NAVE'];
const r = [f({toks, viaje: '', iguales: true}).map(x => x.igual), f({toks, viaje: ''}).map(x => 'igual' in x)];
const b = [a(), a(), a(), a()];
b[1].attributes.push({name: 'data-x', value: '1'});
b[2].getHTML = undefined;
b[3].getHTML = undefined;
pagina(b);
r.push(f({toks, viaje: '', iguales: true}).map(x => x.igual));
console.log(JSON.stringify(r));
"""
        self.assertEqual(correr_node(self, guion), [[0, 0, 2, 3], [False] * 4, [0, 1, 2, 3]])

    def test_sin_una_salida_con_el_mismo_tiempo_de_transito(self):
        hoy = datetime.date.today()
        nueve = hoy + datetime.timedelta(days=9)
        salidas = [{"i": i, "salida": self.salida(9), "transito": "40 days"} for i in (0, 1)]
        reg, _, _ = self.corrida("mk_mismo_transito")
        r = self.mod._mk_sin_una_salida(PaginaMaersk(), reg, {"fila": 30, "nave": "MAERSK NAVE"}, salidas, "empate", hoy)
        self.assertEqual(r, ("NO ENVIADA", f"MAERSK: no elegí salida para esa nave ('MAERSK NAVE'): 2 de las 2 opciones "
                                           f"salen el {nueve:%d-%m-%Y}, la próxima salida desde el {hoy:%d-%m-%Y}, y 2 de "
                                           "ellas tienen el menor tiempo de tránsito, 40 días. Revisa la fila y elige la "
                                           "salida en el portal."))

    def test_transito_de_la_salida(self):
        f = self.mod._mk_transito
        d = datetime.timedelta
        casos = (("44 days 6 hours", d(days=44, hours=6)), ("1 day 1 hour", d(days=1, hours=1)), ("40 days", d(days=40)),
                 (" 44 Days 6 Hours ", d(days=44, hours=6)), ("Loading", None), ("", None), ("6 hours", None),
                 ("44 days 6 hours 30 minutes", None))
        for texto, esperado in casos:
            with self.subTest(texto=texto):
                self.assertEqual(f({"transito": texto}), esperado)
        self.assertIsNone(f({}))

    def test_desempata_por_el_menor_tiempo_de_transito(self):
        s = lambda i, n, transito: {"i": i, "calza": True, "viaje": False, "salida": self.salida(n), "book": 1,
                                    "transito": transito}
        # Las dos primeras salen el mismo día: la que tarda menos. La tercera tarda menos, pero sale después.
        r, clics, log = self.elegir([[s(0, 9, "44 days 6 hours"), s(1, 9, "40 days 2 hours"), s(2, 16, "30 days")]])
        self.assertEqual((r, clics), (("nave: MAERSK NAVE", None, None, None), [("book", 1)]))
        nueve = datetime.date.today() + datetime.timedelta(days=9)
        self.assertIn(f"2 salidas de la nave salen el {nueve:%d-%m-%Y}: elijo la de menor tiempo de tránsito, 40 días y 2 "
                      "horas (las otras: 44 días y 6 horas)", log)
        # El mismo tránsito, o uno que no se entiende: ninguna, como hasta 2825153 con cualquier empate.
        for otro in ("40 days", "Loading"):
            with self.subTest(otro=otro):
                r, clics, _ = self.elegir([[s(0, 9, "40 days"), s(1, 9, otro)]])
                self.assertEqual((r[0], r[1][1], clics), ("", "empate", []))

    def test_las_tarjetas_identicas_cuentan_como_una_sola(self):
        # Decisión de Marcelo (encargo 43): las tarjetas de «Select sailing» con el HTML entero idéntico (su «igual», de
        # _JS_MK_SALIDAS: la primera con ese HTML) cuentan como una sola salida, y se pulsa el «Book» de la primera. Si
        # difieren en cualquier cosa, el empate sigue. El 30-09 a las 15:31, la salida de la nave venía 3 veces, con el
        # mismo HTML, y la reserva quedó NO ENVIADA por el empate (CICLO-maersk-y-fila-sin-ruta.md).
        def s(i, n, igual, transito="54 days 3 hours"):
            return {"i": i, "calza": True, "viaje": False, "book": 1, "salida": self.salida(n), "transito": transito,
                    "igual": igual}
        otra = dict(s(0, 2, 0), calza=False)
        r, clics, log = self.elegir([[otra, s(1, 9, 1), s(2, 9, 1), s(3, 9, 1), s(4, 16, 4)]])
        self.assertEqual((r, clics), (("nave: MAERSK NAVE", None, None, None), [("book", 1)]))
        self.assertIn("4 tarjetas de la nave; 2 son copias de otra, con el HTML entero idéntico: cuentan como una sola "
                      "salida (quedan 2)", log)
        # Una del mismo día que difiere en algo: el empate sigue, entre las que quedan, como antes.
        r, clics, log = self.elegir([[s(0, 9, 0), s(1, 9, 0), s(2, 9, 2)]])
        self.assertEqual((r[0], [x["i"] for x in r[1][0]], r[1][1], clics), ("", [0, 2], "empate", []))
        self.assertIn("3 tarjetas de la nave; 1 es copia de otra, con el HTML entero idéntico", log)
        # Sin «igual» (la lectura no lo trajo), cada una cuenta, y nada lo anota.
        sin = {k: v for k, v in s(1, 9, 0).items() if k != "igual"}
        r, clics, log = self.elegir([[s(0, 9, 0), sin]])
        self.assertEqual((r[0], [x["i"] for x in r[1][0]], r[1][1], clics), ("", [0, 1], "empate", []))
        self.assertNotIn("copia", log)

    def elegir(self, lotes, reserva=None, prueba=False, cargando=0, botones=1, altura=400):
        self.n_sailing = getattr(self, "n_sailing", 0) + 1
        reg, vistas, log = self.corrida(f"sailing_{self.n_sailing}")
        pagina = PaginaSailing(self.mod, lotes, cargando, botones, altura)
        self.pagina_sailing = pagina
        entorno = {k: v for k, v in os.environ.items() if k != "AQUASHIELD_PRIMERA_NAVE"}
        if prueba:
            entorno["AQUASHIELD_PRIMERA_NAVE"] = "1"
        with mock.patch.dict(os.environ, entorno, clear=True):
            r = self.mod._mk_elegir_nave(pagina, reserva or {"fila": 30, "nave": "MAERSK NAVE"}, reg)
        return r, pagina.clics, log.read_text(encoding="utf-8")

    def test_elige_la_proxima_salida_que_se_puede_reservar(self):
        # Hasta 16d3583 recorría los candidatos del último al primero: con la nave en dos salidas, pulsaba la de más abajo.
        hoy = datetime.date.today()
        s = lambda i, calza, n, book=1, viaje=False: {"i": i, "calza": calza, "viaje": viaje, "salida": self.salida(n),
                                                      "book": book}
        # La próxima que se puede reservar: las de mañana no traen «Book» (como en la corrida medida) y no cuentan.
        r, clics, log = self.elegir([[s(0, True, 1, 0), s(1, True, 1, 0), s(2, False, 3), s(3, True, 16), s(4, True, 9)]])
        self.assertEqual((r, clics), (("nave: MAERSK NAVE", None, None, None), [("book", 4)]))
        self.assertIn("2 salida(s) de la nave sin un solo «Book»: el portal no deja reservarlas", log)
        # Empate: no pulsa nada y devuelve las salidas, el motivo y la fecha desde la que eligió.
        r, clics, _ = self.elegir([[s(0, True, 9), s(1, True, 9), s(2, True, 16)]])
        self.assertEqual((r[0], [x["i"] for x in r[1][0]], r[1][1:], r[2], clics), ("", [0, 1, 2], ("empate", hoy), None, []))
        # No está: pide más salidas y la encuentra en el lote siguiente.
        r, clics, _ = self.elegir([[s(0, False, 2)], [s(0, False, 2), s(1, True, 12)]])
        self.assertEqual((r, clics), (("nave: MAERSK NAVE", None, None, None), [("mas",), ("book", 1)]))
        # No está en ningún lote: dice hasta qué fecha buscó (CICLO-ampliar-la-busqueda.md).
        r, clics, log = self.elegir([[s(0, False, 2), s(1, False, 9)]])
        dos, nueve = (hoy + datetime.timedelta(days=n) for n in (2, 9))
        self.assertEqual((r, clics), (("", None, ([dos, nueve], self.mod.NO_AMPLIA_MAS), None), []))
        self.assertIn(f"nave 'MAERSK NAVE': no se encontró en itinerarios disponibles; busqué hasta el {nueve:%d-%m-%Y}, "
                      "la última salida que mostró el portal, y el portal no deja ampliar más la búsqueda", log)
        # Con viaje en la fila: solo las de ese viaje, si hay alguna.
        r, clics, _ = self.elegir([[s(0, True, 3), s(1, True, 10, viaje=True)]],
                                  {"fila": 30, "nave": "MAERSK NAVE", "viaje": "541W"})
        self.assertEqual(clics, [("book", 1)])
        # Con AQUASHIELD_PRIMERA_NAVE, sin nave que calce, tampoco elige: hasta a198645 pulsaba la primera que se podía
        # reservar, fuera la nave que fuera, [("book", 1)] (CICLO-solo-la-nave-pedida.md).
        r, clics, log = self.elegir([[s(0, False, 2, 0), s(1, False, 5), s(2, False, 3)]], prueba=True)
        self.assertEqual((r[:2], clics), (("", None), []))
        self.assertIn("nave 'MAERSK NAVE': no se encontró en itinerarios disponibles", log)

    def test_sin_el_viaje_de_la_fila_no_elige(self):
        # Si la fila trae viaje y ninguna salida de la nave lo trae, no elige ninguna: la reserva queda NO ENVIADA, con la
        # evidencia de «Select sailing» (decisión de Marcelo, CICLO-cierre-de-frenos.md). Hasta 4948e16 elegía entre todas
        # las de la nave, sin avisarlo: aquí, la 0.
        hoy = datetime.date.today()
        s = lambda i, n, viaje=False, calza=True: {"i": i, "calza": calza, "viaje": viaje, "salida": self.salida(n),
                                                   "book": 1}
        reserva = {"fila": 30, "nave": "MAERSK NAVE", "viaje": "541W"}
        r, clics, _ = self.elegir([[s(0, 3), s(1, 10), s(2, 5, viaje=True, calza=False)]], reserva)
        self.assertEqual((r[0], [x["i"] for x in r[1][0]], r[1][1:], r[2], clics), ("", [0, 1], ("sin-viaje", hoy), None, []))
        # Antes de cortar amplía la búsqueda, y si el viaje aparece, lo elige (decisión de Marcelo,
        # CICLO-ampliar-la-busqueda.md). Hasta 4cae528 cortaba con el primer lote: aquí, sin pedir más.
        r, clics, _ = self.elegir([[s(0, 3), s(1, 10)], [s(0, 3), s(1, 10), s(2, 17, viaje=True)]], reserva)
        self.assertEqual((r, clics), (("nave: MAERSK NAVE", None, None, None), [("mas",), ("book", 2)]))
        # Con una que lo trae, esa, aunque salga después.
        r, clics, _ = self.elegir([[s(0, 3), s(1, 10, viaje=True)]], reserva)
        self.assertEqual((r, clics), (("nave: MAERSK NAVE", None, None, None), [("book", 1)]))
        # Sin la nave, su camino de siempre: pide más salidas y no la encuentra.
        r, clics, log = self.elegir([[s(0, 3, calza=False)]], reserva)
        self.assertEqual((r[:2], r[2][1], clics), (("", None), self.mod.NO_AMPLIA_MAS, []))
        self.assertIn("nave 'MAERSK NAVE': no se encontró en itinerarios disponibles", log)
        # El motivo, con la evidencia.
        salidas = [{"i": 0, "salida": self.salida(3)}, {"i": 1, "salida": self.salida(10)}]
        reg, vistas, log = self.corrida("mk_sin_viaje")
        pagina = PaginaMaersk()
        detalle = ("MAERSK: no elegí salida para esa nave ('MAERSK NAVE'): ninguna de las 2 opciones de la nave trae el "
                   "viaje de la fila. Revisa la fila y elige la salida en el portal.")
        self.assertEqual(self.mod._mk_sin_una_salida(pagina, reg, reserva, salidas, "sin-viaje", hoy), ("NO ENVIADA", detalle))
        self.assertEqual(pagina.capturas, [("mk_f30_detenida.png", False)])
        for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):
            self.assertIn(f"· ✗ NO ENVIADA · {detalle}", donde)

    def test_la_salida_pedida_ya_no_se_puede_reservar(self):
        # El viaje de la fila está, pero solo en salidas sin «Book»: NO ENVIADA con «la salida pedida ya no se puede
        # reservar», sin pedir más salidas (decisión de Marcelo, CICLO-ampliar-la-busqueda.md). Hasta 4cae528 pedía más
        # y quedaba REVISAR, como una nave que no está: así terminaron las dos corridas de MAERSK del 2026-09-26.
        hoy = datetime.date.today()
        s = lambda i, n, book=1, viaje=False, calza=True: {"i": i, "calza": calza, "viaje": viaje,
                                                           "salida": self.salida(n), "book": book}
        reserva = {"fila": 30, "nave": "MAERSK NAVE", "viaje": "541W"}
        r, clics, _ = self.elegir([[s(0, 3, book=0, viaje=True), s(1, 10)], [s(0, 3), s(1, 10), s(2, 17)]], reserva)
        self.assertEqual((r[0], [x["i"] for x in r[1][0]], r[1][1:], r[2], clics),
                         ("", [0], ("no-reservable", hoy), None, []))
        # Con otra salida del mismo viaje que sí se puede reservar, esa.
        r, clics, _ = self.elegir([[s(0, 3, book=0, viaje=True), s(1, 10, viaje=True)]], reserva)
        self.assertEqual(clics, [("book", 1)])
        # Sin viaje en la fila, la nave solo en salidas sin «Book»: amplía, y si no aparece otra, lo mismo.
        r, clics, _ = self.elegir([[s(0, 3, book=0)], [s(0, 3, book=0), s(1, 10, calza=False)]])
        self.assertEqual((r[0], [x["i"] for x in r[1][0]], r[1][1:], r[2], clics),
                         ("", [0], ("no-reservable", hoy), None, [("mas",)]))
        # El motivo, con la evidencia de «Select sailing».
        reg, vistas, log = self.corrida("mk_no_reservable")
        pagina = PaginaMaersk()
        detalle = "MAERSK: la salida pedida ya no se puede reservar ('MAERSK NAVE')"
        r = self.mod._mk_sin_una_salida(pagina, reg, reserva, [{"i": 0, "salida": self.salida(3)}], "no-reservable", hoy)
        self.assertEqual(r, ("NO ENVIADA", detalle))
        self.assertEqual(pagina.capturas, [("mk_f30_detenida.png", False)])
        for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):
            self.assertIn(f"· ✗ NO ENVIADA · {detalle}", donde)

    def test_amplia_hasta_que_el_portal_no_deja_mas(self):
        # «Search more sailing options»: espera a que se habilite (mientras carga, el portal lo deja deshabilitado) y a
        # que lleguen salidas nuevas; se detiene cuando no hay botón, cuando no llega ninguna nueva o en el tope
        # (CICLO-ampliar-la-busqueda.md). Hasta 4cae528 lo pulsaba 3 veces como mucho, esperando 7 s: el 2026-09-25 se
        # rindió con el botón todavía cargando.
        s = lambda i, calza, n: {"i": i, "calza": calza, "viaje": False, "salida": self.salida(n), "book": 1}
        espera = self.mod.MK_ESPERA_MAS
        # Mientras carga, espera; después lo pulsa y encuentra la nave.
        r, clics, _ = self.elegir([[s(0, False, 2)], [s(0, False, 2), s(1, True, 12)]], cargando=3)
        self.assertEqual((r, clics), (("nave: MAERSK NAVE", None, None, None), [("mas",), ("book", 1)]))
        self.assertEqual(self.pagina_sailing.consultas, 4)
        # Si no se habilita, no lo pulsa, y dice por qué.
        r, clics, _ = self.elegir([[s(0, False, 2)], [s(0, False, 2), s(1, True, 12)]], cargando=10 ** 6)
        self.assertEqual((r[:2], r[2][1], clics), (("", None), "no pude ampliar la búsqueda: «Search more sailing options» "
                                                                f"siguió deshabilitado {espera} s", []))
        self.assertEqual(self.pagina_sailing.consultas, espera)
        # Con dos botones a la vista, ninguno.
        r, clics, _ = self.elegir([[s(0, False, 2)], [s(0, False, 2), s(1, True, 12)]], botones=2)
        self.assertEqual((r[2][1], clics), ("no pude ampliar la búsqueda: había 2 botones «Search more sailing options» "
                                            "a la vista", []))
        # Si después de pulsarlo no llega ninguna salida nueva, el portal no deja ampliar más: no lo pulsa otra vez.
        r, clics, _ = self.elegir([[s(0, False, 2)], [s(0, False, 2)], [s(0, False, 2), s(1, True, 12)]])
        self.assertEqual((r[2][1], clics), (self.mod.NO_AMPLIA_MAS, [("mas",)]))
        # El tope de seguridad: AMPLIAR_MAX tandas, y dice hasta qué fecha llegó.
        tope = self.mod.AMPLIAR_MAX
        lotes = [[s(k, False, 2 + k) for k in range(n)] for n in range(1, tope + 3)]
        r, clics, _ = self.elegir(lotes)
        self.assertEqual((r[2][1], clics), (f"ya amplié la búsqueda {tope} veces, el tope", [("mas",)] * tope))
        self.assertEqual(max(r[2][0]), datetime.date.today() + datetime.timedelta(days=2 + tope))

    def test_anota_por_que_dejo_de_ampliar(self):
        # La nave está, pero no la salida pedida: sin viaje en la fila, solo sin «Book»; con viaje, sin ese viaje. Amplía,
        # y cuando deja de ampliar lo anota, porque el motivo de la NO ENVIADA no lo dice (revisión del encargo 32).
        s = lambda book: {"i": 0, "calza": True, "viaje": False, "salida": self.salida(2), "book": book}
        for reserva, lote, motivo in (({"fila": 30, "nave": "MAERSK NAVE"}, [s(0)], "no-reservable"),
                                      ({"fila": 30, "nave": "MAERSK NAVE", "viaje": "123E"}, [s(1)], "sin-viaje")):
            with self.subTest(motivo=motivo):
                r, clics, log = self.elegir([lote, lote], reserva=reserva)
                self.assertEqual((r[0], r[1][1], r[2], clics), ("", motivo, None, [("mas",)]))
                self.assertIn(f"dejé de ampliar la búsqueda: {self.mod.NO_AMPLIA_MAS}", log)

    def test_sin_una_salida_queda_no_enviada_con_evidencia(self):
        hoy = datetime.date.today()
        nueve = hoy + datetime.timedelta(days=9)
        salidas = [{"i": 0, "salida": self.salida(9)}, {"i": 1, "salida": self.salida(9)}]
        reg, vistas, log = self.corrida("mk_sin_una")
        pagina = PaginaMaersk()
        # Hasta 2825153 el motivo terminaba en «…la próxima salida desde el …»; ahora dice también por qué el tiempo de
        # tránsito no desempató: estas tarjetas sintéticas no lo traen (CICLO-cola-tres-items.md).
        detalle = (f"MAERSK: no elegí salida para esa nave ('MAERSK NAVE'): 2 de las 2 opciones salen el "
                   f"{nueve:%d-%m-%Y}, la próxima salida desde el {hoy:%d-%m-%Y}, y no pude leer el tiempo de tránsito de "
                   "2 de ellas. Revisa la fila y elige la salida en el portal.")
        r = self.mod._mk_sin_una_salida(pagina, reg, {"fila": 30, "nave": "MAERSK NAVE"}, salidas, "empate", hoy)
        self.assertEqual(r, ("NO ENVIADA", detalle))
        self.assertEqual(pagina.capturas, [("mk_f30_detenida.png", False)])
        self.assertTrue((self.sb / "mk_sin_una" / "mk_f30_detenida.html").exists())
        for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):
            self.assertIn(f"· ✗ NO ENVIADA · {detalle}", donde)
            self.assertIn(f"salidas que calzan: sale {self.salida(9)} | sale {self.salida(9)}", donde)

    def test_sin_una_salida_no_llega_a_la_guarda(self):
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_maersk")
        eleccion = [n for n in ast.walk(f) if isinstance(n, ast.Assign) and "_mk_elegir_nave" in ast.unparse(n.value)]
        self.assertEqual([ast.unparse(n) for n in eleccion],
                         ["modo, sin_una, sin_nave, sin_book = _mk_elegir_nave(page, reserva, reg)"])
        sin_una = [n for n in ast.walk(f) if isinstance(n, ast.If) and ast.unparse(n.test) == "sin_una"]
        self.assertEqual([ast.unparse(s) for s in sin_una[0].body],
                         ["return _mk_sin_una_salida(page, reg, reserva, *sin_una)"])
        corte = [n for n in ast.walk(f) if isinstance(n, ast.If) and ast.unparse(n.test) == "not modo"]
        self.assertLess(eleccion[0].lineno, sin_una[0].lineno)
        self.assertLess(sin_una[0].lineno, corte[0].lineno)
        self.assertLess(corte[0].lineno, linea_guarda(f))

    # --- El «Book» de la salida elegida (decisión de Marcelo, encargo 46, CICLO-maersk-pulsa-el-book.md) ---
    def test_trae_la_tarjeta_a_la_vista_antes_de_mirar_el_book(self):
        # Antes de mirar a qué altura está el «Book» de la salida elegida, trae su tarjeta a la vista
        # (scroll_into_view_if_needed, sin clics ni teclas), y la regla de los 100 px se aplica después. Hasta el
        # encargo 46 la miraba antes: el 2026-10-01 la tarjeta elegida había quedado arriba de la ventana, y no la
        # pulsó (encargo 45, CICLO-login-msc-y-maersk.md). Un solo clic (el mc-button y su botón interno son el mismo
        # control), y si no lo pulsa, dice por qué.
        f = self.mod._mk_pulsar_book
        pagina = PaginaBook()
        self.assertEqual(f(pagina, 7), "")
        self.assertEqual(pagina.eventos, [("trae", 7), ("altura", 7), ("trae el book", 7), ("clic", 7)])
        regla = ("con su tarjeta a la vista, el «Book» quedó a {} px del borde de arriba de la ventana, y lo pulso "
                 "solo si está a más de 100 px")
        for despues in (80, 100):                 # la regla se mantiene: a 100 px o menos, no lo pulsa
            with self.subTest(despues=despues):
                pagina = PaginaBook(despues=despues)
                self.assertEqual(f(pagina, 7), regla.format(despues))
                self.assertEqual(pagina.eventos, [("trae", 7), ("altura", 7), ("altura", 7)])
        pagina = PaginaBook(falla_clic=True)
        self.assertEqual(f(pagina, 7), "el clic en el «Book» falló (RuntimeError: otro elemento recibiría el clic)")
        self.assertEqual(pagina.eventos, [("trae", 7), ("altura", 7), ("trae el book", 7), ("clic", 7)])
        pagina = PaginaBook(falla_traer=True)
        self.assertEqual(f(pagina, 7), "no pude traer su tarjeta a la vista (RuntimeError: la tarjeta se movió)")
        self.assertEqual(pagina.eventos, [("trae", 7)])
        pagina = PaginaBook(sin_book=True)
        self.assertEqual(f(pagina, 7), "su tarjeta no trae un «Book» a la vista")
        self.assertEqual(pagina.eventos, [("trae", 7)])

    def test_el_book_que_no_pudo_pulsar_vuelve_con_la_salida_y_el_porque(self):
        # Si la nave está y no pudo pulsar el «Book» de la salida elegida, _mk_elegir_nave lo devuelve aparte, con la
        # salida y por qué (decisión de Marcelo, encargo 46). Hasta ahí devolvía lo mismo que la nave que no está, y
        # reservar_maersk seguía por _mk_sin_nave: «no está en los itinerarios».
        s = {"i": 0, "calza": True, "viaje": False, "salida": self.salida(9), "book": 1}
        r, clics, log = self.elegir([[s]], altura=50)
        por_que = ("con su tarjeta a la vista, el «Book» quedó a 50 px del borde de arriba de la ventana, y lo "
                   "pulso solo si está a más de 100 px")
        self.assertEqual((r, clics), (("", None, None, (s, por_que)), []))
        # Lo último que anota (la carpeta de la corrida es la de las otras pruebas de elegir, y su log.txt se suma).
        self.assertTrue(log.rstrip("\n").endswith(f"    no pude pulsar el «Book» de la salida elegida: {por_que}"))

    def test_el_book_sin_pulsar_queda_no_enviada_con_evidencia(self):
        # La nave estaba y no se pudo pulsar su «Book»: NO ENVIADA, con la evidencia de «Select sailing»
        # (mk_f<fila>_detenida: la captura de la ventana y su HTML) y un motivo que dice que la nave estaba (decisión de
        # Marcelo, encargo 46). Hasta ahí, REVISAR con «la nave … no está en los itinerarios».
        reg, vistas, log = self.corrida("mk_book_sin_pulsar")
        pagina = PaginaMaersk()
        salida = {"i": 7, "salida": "18 Oct 2026, 08:30"}
        por_que = "el clic en el «Book» falló (RuntimeError: otro elemento recibiría el clic)"
        r = self.mod._mk_book_sin_pulsar(pagina, reg, {"fila": 30, "nave": "MAERSK NAVE"}, salida, por_que)
        detalle = ("MAERSK: la nave 'MAERSK NAVE' estaba en «Select sailing» y elegí su salida (sale 18 Oct 2026, "
                   f"08:30), pero no pude pulsar su «Book»: {por_que}. No pulsé nada más, y la reserva no se envió")
        self.assertEqual(r, ("NO ENVIADA", detalle))
        self.assertEqual(pagina.capturas, [("mk_f30_detenida.png", False)])
        self.assertTrue((self.sb / "mk_book_sin_pulsar" / "mk_f30_detenida.html").exists())
        for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):
            self.assertIn(f"· ✗ NO ENVIADA · {detalle}", donde)
            self.assertNotIn("no está en los itinerarios", donde)

    def test_el_book_sin_pulsar_no_sigue_por_la_nave_que_no_esta(self):
        # En reservar_maersk, el «Book» que no se pudo pulsar tiene su rama (_mk_book_sin_pulsar), antes de la de la
        # nave que no está y antes de la guarda (decisión de Marcelo, encargo 46).
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_maersk")
        [rama] = [n for n in ast.walk(f) if isinstance(n, ast.If) and ast.unparse(n.test) == "sin_book"]
        self.assertEqual([ast.unparse(s) for s in rama.body],
                         ["return _mk_book_sin_pulsar(page, reg, reserva, *sin_book)"])
        [corte] = [n for n in ast.walk(f) if isinstance(n, ast.If) and ast.unparse(n.test) == "not modo"]
        self.assertLess(rama.lineno, corte.lineno)
        self.assertLess(rama.lineno, linea_guarda(f))


class BotonRetiro:
    """Un botón de PaginaRetiro por su nombre accesible: cuántos hay a la vista, y el clic, que se anota."""
    def __init__(self, pagina, nombre):
        self.pagina, self.nombre = pagina, nombre

    def count(self):
        return self.pagina.botones(self.nombre)

    def nth(self, j):
        return self

    def is_visible(self):
        return True

    def scroll_into_view_if_needed(self, **k):
        pass

    def click(self, **k):
        self.pagina.clics.append(("boton", self.nombre))
        if self.nombre == self.pagina.mod.MK_OTRA_FECHA:
            self.pagina.etapa, self.pagina.esperas = "abierto", 0
        elif self.nombre == self.pagina.mod.MK_LISTO:
            self.pagina.etapa = "listo"


class PaginaRetiro(soporte.PaginaFalsa):
    """«Additional details» falsa de MAERSK para la fecha de retiro. Hay 'otra' botones «Choose another date» a la vista
    desde la espera 'otra_tarda', y 'listos_antes' «Done» antes de abrir el calendario. Abierto, _JS_MK_CALENDARIO
    responde 'calendario' desde la espera 'tarda' (antes, sin calendario); _JS_MK_DIA_DE_RETIRO da el día pedido si
    'dia'; después de pulsarlo, _JS_MK_LISTO da el «Done» del calendario si 'listo', y si no, hay 'listos_despues' «Done»
    a la vista. _JS_MK_AVISOS_CARGOS responde 'avisos' antes de elegir el día y 'avisos_despues' después;
    _JS_MK_RETIRO_PUESTO, 'puesto' (con una lista, una respuesta por lectura, y la última se repite); _JS_MK_LO_QUE_PIDE,
    'pide'. Cada clic queda en 'clics'. Otro JavaScript hace caer la prueba."""
    SIN_CALENDARIO = {"listos": 0, "raiz": False, "meses": [], "dias": []}

    def __init__(self, mod, calendario, otra=1, otra_tarda=0, listos_antes=0, tarda=0, dia=True, listo=True,
                 listos_despues=0, avisos=(), avisos_despues=None, puesto=None, pide=None):
        super().__init__(url="https://portal.invalid/book/additional-details")
        self.mod, self.calendario, self.otra, self.otra_tarda = mod, calendario, otra, otra_tarda
        self.listos_antes, self.tarda, self.dia, self.listo = listos_antes, tarda, dia, listo
        self.listos_despues, self.avisos = listos_despues, list(avisos)
        self.avisos_despues = list(self.avisos if avisos_despues is None else avisos_despues)
        puesto = puesto if puesto is not None else {"tarjeta": True, "vacia": False, "fechas": [], "valor": ""}
        self.puestos = list(puesto) if isinstance(puesto, list) else [puesto]
        self.pide, self.clics, self.etapa = pide, [], "cerrado"

    def get_by_role(self, rol, name=None, exact=False):
        if rol != "button" or not exact:
            raise AssertionError(f"botón buscado sin su nombre exacto: {rol}, {name}, {exact}")
        return BotonRetiro(self, name)

    def botones(self, nombre):
        if nombre == self.mod.MK_OTRA_FECHA:
            return self.otra if self.esperas >= self.otra_tarda else 0
        if nombre == self.mod.MK_LISTO:
            return {"cerrado": self.listos_antes, "elegido": self.listos_despues}.get(self.etapa, 0)
        return 0

    def evaluate(self, js, *a):
        m = self.mod
        if js == m._JS_MK_CALENDARIO:
            return self.calendario if self.etapa != "cerrado" and self.esperas >= self.tarda else self.SIN_CALENDARIO
        if js == m._JS_MK_AVISOS_CARGOS:
            return self.avisos_despues if self.etapa in ("elegido", "listo") else self.avisos
        if js == m._JS_MK_RETIRO_PUESTO:
            puesto = self.puestos.pop(0) if len(self.puestos) > 1 else self.puestos[0]
            if isinstance(puesto, Exception):
                raise puesto
            return puesto
        if js == m._JS_MK_LO_QUE_PIDE:
            return self.pide
        if js == m._JS_HTML_COMPLETO:
            return {}
        raise AssertionError("JavaScript inesperado")

    def evaluate_handle(self, js, arg=None):
        pagina = self

        def pulsar_dia(**k):
            pagina.clics.append(("dia", arg["fecha"]))
            pagina.etapa = "elegido"

        def pulsar_listo(**k):
            pagina.clics.append(("boton", pagina.mod.MK_LISTO))
            pagina.etapa = "listo"

        if js == self.mod._JS_MK_DIA_DE_RETIRO:
            el = types.SimpleNamespace(click=pulsar_dia) if self.dia else None
        elif js == self.mod._JS_MK_LISTO:
            el = types.SimpleNamespace(click=pulsar_listo) if self.listo and self.etapa == "elegido" else None
        else:
            raise AssertionError("JavaScript inesperado")
        return types.SimpleNamespace(as_element=lambda: el)

    def content(self):
        return "<body>calendario sintetico</body>"


class TestRetiroMaersk(ConRegistro):
    """La fecha de retiro de MAERSK, con la regla de Marcelo (CICLO-maersk-retiro-y-terminos.md): el primer día hábil
    después de hoy, o el siguiente día hábil habilitado (nunca sábado ni domingo, CICLO-maersk-ultimos-puntos.md), con
    tres clics: «Choose another date», el día por su fecha y «Done». Del 24-09 al encargo 36 no se elegía, y el portal
    no pasaba a la revisión sin ella (CICLO-maersk-fecha-de-retiro.md)."""
    SIN_FECHA = {"tarjeta": True, "vacia": False, "fechas": [], "valor": ""}

    def setUp(self):
        super().setUp()
        # Una librería holidays falsa y sin feriados (encargo 38): así ninguna prueba depende de que la máquina la
        # tenga. Las de los feriados ponen la suya.
        libreria = types.SimpleNamespace(country_holidays=lambda pais, years=None: {})
        parche = mock.patch.dict("sys.modules", {"holidays": libreria})
        parche.start()
        self.addCleanup(parche.stop)

    @staticmethod
    def septiembre(desde=1):
        """Lo que responde _JS_MK_CALENDARIO: septiembre de 2026 por su leyenda, habilitado desde el día 'desde' (el
        21-09, el primer día habilitado fue el 27)."""
        return {"listos": 1, "raiz": True, "meses": ["2026-09"],
                "dias": [{"dia": n, "fecha": f"2026-09-{n:02d}", "como": "mes", "habilitado": n >= desde}
                         for n in range(1, 31)]}

    def puesto(self, *fechas, valor=""):
        return dict(self.SIN_FECHA, fechas=list(fechas), valor=valor)

    def retirar(self, pagina, hoy=datetime.date(2026, 9, 28)):
        self.n = getattr(self, "n", 0) + 1
        reg, vistas, log = self.corrida(f"retiro_{self.n}")
        det = []
        r = self.mod._mk_fecha_de_retiro(pagina, reg, det, 30, hoy)
        return r, det, log.read_text(encoding="utf-8")

    def test_el_primer_dia_habil_despues_de_hoy(self):
        d = datetime.date
        casos = ((d(2026, 9, 28), d(2026, 9, 29)),     # lunes: el martes
                 (d(2026, 9, 29), d(2026, 9, 30)),     # martes: el miércoles
                 (d(2026, 9, 30), d(2026, 10, 1)),     # miércoles: el jueves, del mes siguiente
                 (d(2026, 10, 1), d(2026, 10, 2)),     # jueves: el viernes
                 (d(2026, 10, 2), d(2026, 10, 5)),     # viernes: el lunes siguiente
                 (d(2026, 10, 3), d(2026, 10, 5)),     # sábado: el lunes
                 (d(2026, 10, 4), d(2026, 10, 5)),     # domingo: el lunes
                 (d(2026, 12, 31), d(2027, 1, 1)))     # los feriados no cuentan: la regla es de lunes a viernes
        for hoy, esperado in casos:
            with self.subTest(hoy=hoy):
                self.assertEqual(self.mod._mk_dia_de_retiro(hoy), esperado)

    # Con un feriado en sábado (el 19-09), que ya no es día hábil: el log no lo nombra.
    FERIADOS = {datetime.date(2026, 9, 18): "Independencia Nacional",
                datetime.date(2026, 9, 19): "Glorias del Ejército",
                datetime.date(2026, 10, 12): "Encuentro", datetime.date(2027, 1, 1): "Año Nuevo"}

    def test_los_feriados_no_son_dias_habiles(self):
        # Los feriados de Chile no cuentan como días hábiles (decisión de Marcelo, CICLO-maersk-shipper-y-cortes.md;
        # hasta el encargo 38, sí).
        d, fer = datetime.date, self.FERIADOS
        casos = ((d(2026, 10, 9), d(2026, 10, 13)),    # viernes: el lunes 12 es feriado, el martes
                 (d(2026, 9, 17), d(2026, 9, 21)),     # jueves: el viernes 18 es feriado, el lunes
                 (d(2026, 12, 31), d(2027, 1, 4)),     # jueves: el viernes 1 es feriado, el lunes
                 (d(2026, 9, 28), d(2026, 9, 29)))     # sin feriado en medio, como antes
        for hoy, esperado in casos:
            with self.subTest(hoy=hoy):
                self.assertEqual(self.mod._mk_dia_de_retiro(hoy, fer), esperado)
        self.assertEqual(self.mod._mk_feriados_saltados(d(2026, 10, 9), d(2026, 10, 13), fer),
                         "; el 12-10-2026 (Encuentro) es feriado en Chile")
        self.assertEqual(self.mod._mk_feriados_saltados(d(2026, 9, 17), d(2026, 9, 21), fer),
                         "; el 18-09-2026 (Independencia Nacional) es feriado en Chile")
        dos = {d(2026, 9, 17): "Uno", d(2026, 9, 18): "Dos"}
        self.assertEqual(self.mod._mk_dia_de_retiro(d(2026, 9, 16), dos), d(2026, 9, 21))
        self.assertEqual(self.mod._mk_feriados_saltados(d(2026, 9, 16), d(2026, 9, 21), dos),
                         "; el 17-09-2026 (Uno) y el 18-09-2026 (Dos) son feriados en Chile")
        self.assertEqual(self.mod._mk_feriados_saltados(d(2026, 9, 28), d(2026, 9, 29), fer), "")

    def test_el_calendario_salta_los_feriados(self):
        # El que toca no está habilitado y el siguiente día de lunes a viernes es feriado: el día hábil después.
        f, d = self.mod._mk_elegir_dia_de_retiro, datetime.date
        sep = self.septiembre(desde=18)["dias"]
        self.assertEqual(f(sep, d(2026, 9, 17), self.FERIADOS),
                         (d(2026, 9, 21), "el 17-09-2026 no está habilitado en el calendario: elijo el siguiente día "
                                          "hábil habilitado, el 21-09-2026 (lunes)"))
        self.assertEqual(f(sep, d(2026, 9, 17))[0], d(2026, 9, 18))       # sin feriados, el viernes 18
        solo_feriado = [dict(x, habilitado=x["fecha"] == "2026-09-18") for x in sep]
        self.assertEqual(f(solo_feriado, d(2026, 9, 17), self.FERIADOS)[0], None)

    def feriados_falsos(self, respuesta):
        """sys.modules con una librería holidays falsa: su country_holidays anota el país y los años, y devuelve
        'respuesta'."""
        paises = []

        def country_holidays(pais, years=None):
            paises.append((pais, tuple(years or ())))
            return respuesta
        libreria = types.SimpleNamespace(country_holidays=country_holidays)
        return mock.patch.dict("sys.modules", {"holidays": libreria}), paises

    def test_los_feriados_son_los_de_chile_de_la_libreria(self):
        parche, paises = self.feriados_falsos(self.FERIADOS)
        reg, vistas, _ = self.corrida("feriados_libreria")
        with parche:
            self.assertEqual(self.mod._feriados_de_chile(datetime.date(2026, 9, 29)), self.FERIADOS)
        self.assertEqual((paises, vistas), ([("CL", (2026, 2027))], []))

    def test_la_libreria_que_falla_al_calcular_avisa(self):
        # La librería calcula cada año recién al consultarlo: los feriados se copian dentro del try, y un fallo ahí
        # también avisa y sigue de lunes a viernes (revisión del encargo 38: escapaba como ERROR).
        class Perezosa:
            def keys(self):
                raise RuntimeError("no pude calcular el año")
        parche, _ = self.feriados_falsos(Perezosa())
        reg, vistas, log = self.corrida("feriados_perezosos")
        with parche:
            self.assertEqual(self.mod._feriados_de_chile(datetime.date(2026, 12, 31)), {})
        self.assertIn("⚠ No pude usar los feriados de Chile de la librería holidays (RuntimeError: no pude calcular el "
                      "año)", log.read_text(encoding="utf-8"))

    def test_sin_la_libreria_avisa_una_vez_y_sigue_de_lunes_a_viernes(self):
        reg, vistas, log = self.corrida("feriados_sin_libreria")
        with mock.patch.dict("sys.modules", {"holidays": None}):
            self.assertEqual([self.mod._feriados_de_chile(datetime.date(2026, 9, 29)) for _ in range(2)], [{}, {}])
        aviso = ("⚠ No pude usar los feriados de Chile de la librería holidays (ModuleNotFoundError: import of "
                 "holidays halted; None in sys.modules): la fecha de retiro de MAERSK sigue de lunes a viernes, sin "
                 "feriados. Se instala con «python -m pip install --user holidays».")
        for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):
            self.assertEqual(donde.count(aviso), 1)

    def test_la_fecha_de_retiro_usa_los_feriados(self):
        # _mk_fecha_de_retiro busca desde el primer día hábil sin feriados y lo dice en log.txt; en el calendario, salta
        # también los feriados.
        parche, _ = self.feriados_falsos(self.FERIADOS)
        with parche:
            r, det, log = self.retirar(PaginaRetiro(self.mod, self.septiembre(desde=22),
                                                    puesto=self.puesto("2026-09-22")), hoy=datetime.date(2026, 9, 17))
        self.assertEqual((r, det), (None, ["retiro=22-09-2026"]))
        self.assertIn("Fecha de retiro: el primer día hábil después de hoy es el 21-09-2026 (lunes); el 18-09-2026 "
                      "(Independencia Nacional) es feriado en Chile.", log)
        with parche:
            r, det, _ = self.retirar(PaginaRetiro(self.mod, self.septiembre(desde=18),
                                                  puesto=self.puesto("2026-09-21")), hoy=datetime.date(2026, 9, 16))
        self.assertEqual((r, det), (None, ["retiro=21-09-2026"]))

    def test_elige_el_dia_con_la_regla(self):
        f, d = self.mod._mk_elegir_dia_de_retiro, datetime.date
        sep = self.septiembre(desde=27)["dias"]
        self.assertEqual(f(sep, d(2026, 9, 28)), (d(2026, 9, 28), ""))
        # El que toca no está habilitado: el siguiente día hábil habilitado, nunca sábado ni domingo (decisión de
        # Marcelo, CICLO-maersk-ultimos-puntos.md; hasta el encargo 37, el domingo 27).
        self.assertEqual(f(sep, d(2026, 9, 22)), (d(2026, 9, 28), "el 22-09-2026 no está habilitado en el calendario: "
                                                                  "elijo el siguiente día hábil habilitado, el "
                                                                  "28-09-2026 (lunes)"))
        # Con el sábado habilitado, tampoco: el lunes.
        self.assertEqual(f(self.septiembre(desde=26)["dias"], d(2026, 9, 25)),
                         (d(2026, 9, 28), "el 25-09-2026 no está habilitado en el calendario: elijo el siguiente día "
                                          "hábil habilitado, el 28-09-2026 (lunes)"))
        # Un sábado sin su fecha no importa: nunca se elige.
        sin_sabado = [x for x in self.septiembre(desde=28)["dias"] if x["fecha"] != "2026-09-26"]
        self.assertEqual(f(sin_sabado, d(2026, 9, 22))[0], d(2026, 9, 28))
        # Si del que toca al último a la vista solo están habilitados el sábado y el domingo, no hay día que elegir.
        finde = [dict(x, habilitado=x["fecha"] in ("2026-09-26", "2026-09-27")) for x in sep]
        self.assertEqual(f(finde, d(2026, 9, 22)),
                         (None, "no hay un día hábil habilitado del 22-09-2026 al 30-09-2026, el último que muestra "
                                "el calendario, y cambiar de mes es un clic que no está permitido"))
        # No está a la vista: cambiar de mes es un clic que no está permitido.
        oct_ = [{"fecha": f"2026-10-{n:02d}", "habilitado": True} for n in range(1, 32)]
        for dias, objetivo, primero, ultimo in ((sep, d(2026, 10, 1), "01-09-2026", "30-09-2026"),
                                                (oct_, d(2026, 9, 30), "01-10-2026", "31-10-2026")):
            with self.subTest(objetivo=objetivo):
                self.assertEqual(f(dias, objetivo), (None, f"el día que toca, el {objetivo:%d-%m-%Y}, no está a la vista: "
                                                           f"el calendario muestra del {primero} al {ultimo}, y cambiar "
                                                           "de mes es un clic que no está permitido"))
        self.assertEqual(f(self.septiembre(desde=31)["dias"], d(2026, 9, 22)),
                         (None, "no hay un día hábil habilitado del 22-09-2026 al 30-09-2026, el último que muestra "
                                "el calendario, y cambiar de mes es un clic que no está permitido"))
        # Un día sin su fecha entre el que toca y el habilitado: no se sabe si está habilitado.
        hueco = [x for x in sep if x["fecha"] != "2026-09-25"]
        self.assertEqual(f(hueco, d(2026, 9, 22)), (None, "no pude identificar por su fecha el 25-09-2026 en el calendario"))
        for dias in ([], None, [{"fecha": "", "habilitado": True}], [{"fecha": "2026-02-30", "habilitado": True}]):
            with self.subTest(dias=dias):
                self.assertEqual(f(dias, d(2026, 9, 22)), (None, "no pude identificar por su fecha ningún día del "
                                                                 "calendario"))

    def test_elige_con_tres_clics(self):
        pagina = PaginaRetiro(self.mod, self.septiembre(), puesto=self.puesto("2026-09-29"))
        r, det, log = self.retirar(pagina)                    # lunes 28-09: el martes 29
        self.assertIsNone(r)
        self.assertEqual(pagina.clics, [("boton", "Choose another date"), ("dia", "2026-09-29"), ("boton", "Done")])
        self.assertEqual(det, ["retiro=29-09-2026"])
        self.assertEqual(pagina.capturas, [("mk_f30_calendario.png", False)])      # el calendario, antes de elegir
        for texto in ("· Fecha de retiro: el primer día hábil después de hoy es el 29-09-2026 (martes).",
                      "evidencia con el calendario de la fecha de retiro: mk_f30_calendario.png",
                      "calendario de la fecha de retiro: 30 días, 30 con su fecha y 30 de ellos habilitados, del "
                      "2026-09-01 al 2026-09-30 (mes: 30)",
                      "elegido en el calendario: 29-09-2026 (martes)", "pulsado 'Done'",
                      "la tarjeta muestra la fecha de retiro elegida, el 29-09-2026"):
            self.assertIn(texto, log)
        # El botón y el calendario tardan: los espera, hasta MK_ESPERA_CALENDARIO s cada uno (revisión del encargo 36:
        # hasta ahí, el botón se buscaba una sola vez).
        pagina = PaginaRetiro(self.mod, self.septiembre(), otra_tarda=4, tarda=6, puesto=self.puesto(valor="2026-09-29"))
        r, _, _ = self.retirar(pagina)
        self.assertEqual((r, pagina.clics[-1]), (None, ("boton", "Done")))

    def test_si_no_esta_habilitado_el_siguiente(self):
        # Como el 21-09, un lunes: el martes 22 no está habilitado, y el primero habilitado es el domingo 27. Nunca
        # sábado ni domingo (decisión de Marcelo, CICLO-maersk-ultimos-puntos.md): el lunes 28.
        pagina = PaginaRetiro(self.mod, self.septiembre(desde=27), puesto=self.puesto("2026-09-28"))
        r, det, log = self.retirar(pagina, hoy=datetime.date(2026, 9, 21))
        self.assertIsNone(r)
        self.assertEqual((pagina.clics[1], det), (("dia", "2026-09-28"), ["retiro=28-09-2026"]))
        self.assertIn("· Fecha de retiro: el 22-09-2026 no está habilitado en el calendario: elijo el siguiente día "
                      "hábil habilitado, el 28-09-2026 (lunes).", log)

    def test_sin_un_solo_boton_no_pulsa_nada(self):
        # Sin un solo «Choose another date» (lo espera hasta 10 s), o con un «Done» ya en la página antes de abrir el
        # calendario, que se confundiría con el del calendario (revisión del encargo 36).
        for otra, antes, esperas in ((0, 0, 20), (2, 0, 0), (1, 1, 0)):
            with self.subTest(otra=otra, antes=antes):
                pagina = PaginaRetiro(self.mod, self.septiembre(), otra=otra, listos_antes=antes)
                reg, _, _ = self.corrida(f"sin_boton_{otra}_{antes}")
                with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
                    self.mod._mk_fecha_de_retiro(pagina, reg, [], 30, datetime.date(2026, 9, 28))
                self.assertEqual((e.exception.paso, e.exception.buscaba, pagina.clics, pagina.esperas),
                                 ("Fecha de retiro de MAERSK", "un solo botón «Choose another date» a la vista y ningún "
                                  f"«Done» antes de abrir el calendario (había {otra} y {antes})", [], esperas))

    def test_calendario_que_no_aparece(self):
        # El calendario es el del único «Done» a la vista con al menos 28 días alrededor (_JS_MK_CALENDARIO): hasta la
        # revisión del encargo 36 bastaba un «Done» cualquiera.
        sin = PaginaRetiro.SIN_CALENDARIO
        casos = ((sin, 20, "no apareció el calendario en 10 s (ningún «Done» a la vista)"),
                 ("no es un diccionario", 20, "no apareció el calendario en 10 s (ningún «Done» a la vista)"),
                 (dict(sin, listos=2), 1, "había 2 «Done» a la vista, y no sé cuál es el del calendario"),
                 (dict(sin, listos=1), 20, "junto al «Done» a la vista no hay un calendario de al menos 28 días"))
        for calendario, esperas, por_que in casos:
            with self.subTest(por_que=por_que, calendario=calendario):
                pagina = PaginaRetiro(self.mod, calendario)
                r, det, log = self.retirar(pagina)
                self.assertEqual(r, ("NO ENVIADA", f"MAERSK: pulsé «Choose another date», pero {por_que}; no pulsé nada "
                                                   "más y la reserva no se envió"))
                self.assertEqual((pagina.clics, pagina.esperas, det), ([("boton", "Choose another date")], esperas, []))
                self.assertEqual(pagina.capturas, [("mk_f30_calendario.png", False)])
                self.assertIn(f"calendario de la fecha de retiro: no lo encontré: {por_que}", log)

    def test_sin_el_dia_por_su_fecha_no_pulsa_el_dia(self):
        casos = ((self.septiembre(desde=31), datetime.date(2026, 9, 28),
                  "no hay un día hábil habilitado del 29-09-2026 al 30-09-2026, el último que muestra el calendario, y "
                  "cambiar de mes es un clic que no está permitido"),
                 (self.septiembre(), datetime.date(2026, 9, 30),
                  "el día que toca, el 01-10-2026, no está a la vista: el calendario muestra del 01-09-2026 al "
                  "30-09-2026, y cambiar de mes es un clic que no está permitido"),
                 ({"listos": 1, "raiz": True, "dias": [{"dia": 5, "fecha": "", "como": "repetida"}]},
                  datetime.date(2026, 9, 28), "no pude identificar por su fecha ningún día del calendario"))
        for calendario, hoy, por_que in casos:
            with self.subTest(por_que=por_que):
                pagina = PaginaRetiro(self.mod, calendario)
                r, det, _ = self.retirar(pagina, hoy)
                self.assertEqual(r, ("NO ENVIADA", f"MAERSK: abrí el calendario de la fecha de retiro, pero {por_que}; "
                                                   "no pulsé nada más y la reserva no se envió"))
                self.assertEqual((pagina.clics, det), ([("boton", "Choose another date")], []))

    def test_el_dia_ya_no_esta_al_volver_a_leerlo(self):
        pagina = PaginaRetiro(self.mod, self.septiembre(), dia=False)
        r, det, _ = self.retirar(pagina)
        self.assertEqual(r, ("NO ENVIADA", "MAERSK: al volver a leer el calendario, el 29-09-2026 ya no estaba "
                                           "habilitado o no era uno solo; no pulsé nada más y la reserva no se envió"))
        self.assertEqual((pagina.clics, det), ([("boton", "Choose another date")], []))

    def test_done_despues_del_dia(self):
        # Solo se pulsa el «Done» del calendario (_JS_MK_LISTO). Uno que no es del calendario no se pulsa (revisión del
        # encargo 36: hasta ahí se pulsaba el único «Done» a la vista, fuera de donde fuera).
        for otros in (1, 2):
            with self.subTest(otros=otros):
                pagina = PaginaRetiro(self.mod, self.septiembre(), listo=False, listos_despues=otros)
                r, _, _ = self.retirar(pagina)
                self.assertEqual(r, ("NO ENVIADA", f"MAERSK: elegí el 29-09-2026, pero había {otros} «Done» a la vista y "
                                                   "ninguno es el del calendario; no pulsé nada más y la reserva no se "
                                                   "envió"))
                self.assertEqual(pagina.clics, [("boton", "Choose another date"), ("dia", "2026-09-29")])
        # Si el calendario se cerró al elegir el día, no hace falta «Done».
        pagina = PaginaRetiro(self.mod, self.septiembre(), listo=False, puesto=self.puesto("2026-09-29"))
        r, _, log = self.retirar(pagina)
        self.assertIsNone(r)
        self.assertEqual(pagina.clics, [("boton", "Choose another date"), ("dia", "2026-09-29")])
        self.assertIn("el calendario se cerró al elegir el día, sin «Done»", log)

    def test_comprueba_la_fecha_que_quedo(self):
        nada = "no pulsé nada más y la reserva no se envió"
        vacia = dict(self.SIN_FECHA, vacia=True)
        casos = ((self.puesto("2026-09-30"), None, f"el portal quedó con el 30-09-2026; {nada}"),
                 (self.puesto(valor="2026-10-01"), None, f"el portal quedó con el 01-10-2026; {nada}"),
                 (self.puesto("2026-09-29", valor="2026-09-30"), None, f"el portal quedó con el 30-09-2026; {nada}"),
                 (vacia, {"campos": ["Pickup date"], "mensajes": []},
                  f"la tarjeta sigue sin fecha de retiro y el portal pide: Pickup date; {nada}"),
                 (vacia, None, f"la tarjeta sigue sin fecha de retiro; {nada}"))
        for puesto, pide, que in casos:
            with self.subTest(que=que):
                pagina = PaginaRetiro(self.mod, self.septiembre(), puesto=puesto, pide=pide)
                r, _, _ = self.retirar(pagina)
                self.assertEqual(r, ("NO ENVIADA", f"MAERSK: elegí el 29-09-2026 en el calendario, pero {que}"))
                self.assertEqual(pagina.capturas, [("mk_f30_calendario.png", False), ("mk_f30_retiro.png", False)])
        # Sin fecha, la mira hasta 5 s: diez lecturas, con medio segundo entre una y otra (revisión del encargo 36).
        self.assertEqual(pagina.esperas, 1 + 1 + 1 + 9)
        # Sigue con la elegida: sola, entre otras fechas de la tarjeta, en el campo oculto, o después de esperarla.
        # También si al principio no se podía leer (revisión del encargo 37: hasta ahí cortaba a la primera).
        for puesto in (self.puesto("2026-09-29", valor="2026-09-29"), self.puesto("2026-10-20", "2026-09-29"),
                       self.puesto(valor="2026-09-29"), [vacia, vacia, self.puesto("2026-09-29")],
                       [self.SIN_FECHA, {"tarjeta": False}, RuntimeError("se está dibujando"),
                        self.puesto("2026-09-29")]):
            with self.subTest(puesto=puesto):
                pagina = PaginaRetiro(self.mod, self.septiembre(), puesto=puesto)
                r, _, log = self.retirar(pagina)
                self.assertIsNone(r)
                self.assertEqual(pagina.capturas, [("mk_f30_calendario.png", False)])
                self.assertIn("la tarjeta muestra la fecha de retiro elegida, el 29-09-2026", log)
        # Si no se puede leer qué fecha muestra, corta (decisión de Marcelo, CICLO-maersk-ultimos-puntos.md; hasta el
        # encargo 37 seguía y lo avisaba).
        for puesto, cual in ((self.SIN_FECHA, ""), ({"tarjeta": False}, " (no la encontré)"),
                             ("no es un diccionario", " (no la encontré)"),
                             (RuntimeError("la página se cerró"),
                              " (no pude leer la página: RuntimeError: la página se cerró)")):
            with self.subTest(puesto=puesto):
                pagina = PaginaRetiro(self.mod, self.septiembre(), puesto=puesto)
                r, _, log = self.retirar(pagina)
                self.assertEqual(r, ("NO ENVIADA", "MAERSK: elegí el 29-09-2026 en el calendario, pero no pude leer "
                                                   f"qué fecha muestra la tarjeta{cual}; {nada}"))
                self.assertEqual(pagina.capturas, [("mk_f30_calendario.png", False), ("mk_f30_retiro.png", False)])
                self.assertNotIn("⚠", log)
                self.assertEqual(pagina.esperas, 1 + 1 + 1 + 9)          # la esperó hasta 5 s

    def test_anota_los_avisos_de_cargos_y_sigue(self):
        pagina = PaginaRetiro(self.mod, self.septiembre(), avisos=["Additional charges can incur"],
                              avisos_despues=["Additional charges can incur", "Charges apply for this date"],
                              puesto=self.puesto("2026-09-29"))
        r, _, log = self.retirar(pagina)
        self.assertIsNone(r)
        self.assertEqual(log.count("aviso de MAERSK sobre la fecha de retiro"), 2)       # cada uno, una vez
        self.assertIn("aviso de MAERSK sobre la fecha de retiro (ya estaba antes de elegirla): «Additional charges can "
                      "incur»", log)
        self.assertIn("aviso de MAERSK sobre la fecha de retiro: «Charges apply for this date»", log)

    def test_reservar_maersk_la_elige_antes_de_la_referencia(self):
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_maersk")
        cuerpos = [n.body for n in ast.walk(f) if isinstance(getattr(n, "body", None), list)]
        cuerpo, i = next((c, i) for c in cuerpos for i, s in enumerate(c)
                         if ast.unparse(s) == "corte = _mk_fecha_de_retiro(page, reg, det, f)")
        self.assertEqual(ast.unparse(cuerpo[i + 1]), "if corte:\n    return corte")
        referencia = next(n.lineno for n in ast.walk(f) if isinstance(n, ast.Assign)
                          and ast.unparse(n.targets[0]) == "ref_txt")
        revision = next(c.lineno for c in ast.walk(f) if isinstance(c, ast.Call)
                        and getattr(c.func, "id", "") == "_mk_esperar_revision")
        self.assertLess(cuerpo[i].lineno, referencia)
        self.assertLess(referencia, revision)
        self.assertLess(revision, linea_guarda(f))

    # --- El JavaScript, en Node, sobre calendarios falsos (el del portal no está medido) ---
    CALENDARIO = r"""
const listo = () => el('mc-button', {label: 'Done', 'data-prueba': 'listo'}, [],
                       {shadow: [el('button', {'aria-label': 'Done', 'data-prueba': 'listo-interno'}, ['Done'])]});
const dia = (n, td = {}, boton = {}, opciones = {}) => el('td', Object.assign({role: 'gridcell'}, td),
  [el('button', Object.assign({'data-prueba': 'd' + n}, boton), [String(n)], opciones)], opciones);
const mes = (leyenda, dias) => el('section', {}, [el('header', {}, [el('span', {}, [leyenda])]),
  el('table', {}, [el('tbody', {}, [el('tr', {}, dias)])])]);
const rango = (a, b, f) => Array.from({length: b - a + 1}, (_, i) => f(a + i));
const corto = r => r.dias.map(d => [d.dia, d.fecha, d.como, d.habilitado]);
"""

    def js(self, cuerpo):
        guion = (DOM_AQ + self.CALENDARIO + "const leer = " + self.mod._JS_MK_CALENDARIO + ";\nconst pulsar = "
                 + self.mod._JS_MK_DIA_DE_RETIRO + ";\nconst leerListo = " + self.mod._JS_MK_LISTO
                 + ";\nconst prueba = e => e && e.getAttribute('data-prueba');\nconst r = {};\n" + cuerpo
                 + "\nconsole.log(JSON.stringify(r));\n")
        return correr_node(self, guion)

    def test_js_calendario_por_su_leyenda(self):
        r = self.js(r"""
pagina(el('td', {}, ['1']), el('div', {role: 'dialog'}, [
  mes('September 2026', rango(1, 31, n => dia(n, n < 27 ? {class: 'is-disabled'} : {}))), listo()]));
const a = leer();
r.a = [a.listos, a.raiz, a.meses, corto(a)];                 // septiembre no tiene 31: esa celda queda sin fecha
r.pulsa = [pulsar({fecha: '2026-09-29'}), pulsar({fecha: '2026-09-20'}), pulsar({fecha: '2026-10-01'})].map(prueba);
r.listo = prueba(leerListo());                              // el botón de adentro del «Done» del calendario
pagina(el('div', {role: 'dialog'}, [mes('September 2026', rango(1, 30, n => dia(n))),
                                    mes('Oct 2026', rango(1, 31, n => dia(n))), listo()]));
const b = leer();
r.dos = [b.meses, b.dias.length, b.dias.filter(d => d.fecha).length, b.dias[29].fecha, b.dias[30].fecha];
// Un mes dibujado, pero invisible (visibility:hidden): sus días no cuentan.
pagina(el('div', {role: 'dialog'}, [mes('September 2026', rango(1, 30, n => dia(n))),
                                    mes('October 2026', rango(1, 31, n => dia(n, {}, {}, {invisible: true}))), listo()]));
const c = leer();
r.invisible = [c.dias.length, c.dias.every(d => d.fecha.startsWith('2026-09'))];
pagina(el('div', {role: 'dialog'}, [mes('September 2026', rango(1, 27, n => dia(n))), listo()]));
r.sinListo = leerListo();                                   // sin calendario, ningún «Done»
""")
        dias = [[n, f"2026-09-{n:02d}", "mes", n >= 27] for n in range(1, 31)] + [[31, "", "", True]]
        self.assertEqual(r["a"], [1, True, ["2026-09"], dias])     # el «1» de fuera del calendario no cuenta
        self.assertEqual(r["pulsa"], ["d29", None, None])          # el botón del día, solo si está habilitado
        self.assertEqual((r["listo"], r["sinListo"]), ("listo-interno", None))
        self.assertEqual(r["dos"], [["2026-09", "2026-10"], 61, 61, "2026-09-30", "2026-10-01"])
        self.assertEqual(r["invisible"], [30, True])

    def test_js_calendario_por_su_atributo(self):
        r = self.js(r"""
pagina(el('div', {role: 'dialog'}, [el('table', {}, [el('tr', {}, rango(1, 30, n => dia(n, {}, {'aria-label':
  n === 15 ? 'Wednesday, 16 September 2026' : n === 16 ? 'September 16, 2026' : `Tuesday, ${n} September 2026`})))]),
  listo()]));
r.a = corto(leer()).filter(d => [14, 15, 16].includes(d[0]));
pagina(el('div', {role: 'dialog'}, [el('table', {}, [el('tr', {}, rango(1, 30, n => dia(n, {'data-date':
  `2026-09-${String(n).padStart(2, '0')}`})))]), listo()]));
r.b = corto(leer()).filter(d => d[0] === 29);
// Dos meses a la vista, con la fecha en cada celda: el 1 al 3 de octubre, también al final de la grilla de septiembre.
const etiqueta = (n, m) => `${n} ${m} 2026`;
pagina(el('div', {role: 'dialog'}, [
  mes('September 2026', rango(1, 30, n => dia(n, {}, {'aria-label': etiqueta(n, 'September'), 'data-prueba': 's' + n}))
    .concat(rango(1, 3, n => dia(n, {}, {'aria-label': etiqueta(n, 'October'), 'data-prueba': 'so' + n})))),
  mes('October 2026', rango(1, 31, n => dia(n, {}, {'aria-label': etiqueta(n, 'October'), 'data-prueba': 'o' + n}))),
  listo()]));
const c = leer();
r.dosMeses = [c.dias.filter(d => d.fecha === '2026-10-01').length, c.dias.filter(d => d.como === 'repetida').length,
              prueba(pulsar({fecha: '2026-10-01'}))];
""")
        # Un atributo con la fecha de otro día no cuenta: la del 15 queda sin fecha.
        self.assertEqual(r["a"], [[14, "2026-09-14", "atributo", True], [15, "", "", True],
                                  [16, "2026-09-16", "atributo", True]])
        self.assertEqual(r["b"], [[29, "2026-09-29", "atributo", True]])
        # La fecha repetida queda en la celda de su propio mes (revisión del encargo 36: hasta ahí, en ninguna).
        self.assertEqual(r["dosMeses"], [1, 3, "o1"])

    def test_js_calendario_otros_meses_y_deshabilitados(self):
        r = self.js(r"""
pagina(el('div', {role: 'dialog'}, [mes('September 2026', [dia(30, {class: 'outside-month'}),
  dia(31, {'aria-hidden': 'true'})].concat(rango(1, 30, n => dia(n))).concat([dia(1), dia(2)])), listo()]));
r.otros = corto(leer()).filter((d, i) => i < 4 || i > 31);
pagina(el('div', {role: 'dialog'}, [mes('September 2026', rango(1, 30, n => dia(n, {}, n === 26 ? {disabled: ''}
  : n === 27 ? {'aria-disabled': 'true'} : n === 28 ? {class: 'day inactive'} : n === 29 ? {part: 'day disabled'} : {}))),
  listo()]));
r.apagados = corto(leer()).filter(d => !d[3]).map(d => d[0]);
// Los fines de semana marcados con «weekend» son días, no números de semana (revisión del encargo 36): aquí, celdas con el
// número adentro, sin botón.
pagina(el('div', {role: 'dialog'}, [mes('September 2026', rango(1, 30, n => [5, 6, 12, 13, 19, 20, 26, 27].includes(n)
  ? el('td', {role: 'gridcell', class: 'day weekend'}, [String(n)]) : dia(n))), listo()]));
const finde = leer();
r.finde = [finde.raiz, finde.dias.filter(d => d.fecha).length];
""")
        # Los marcados de otro mes no toman la leyenda; los sin marca chocan con el 1 y el 2: ninguno de los dos queda.
        self.assertEqual(r["otros"], [[30, "", "otro-mes", True], [31, "", "otro-mes", True], [1, "", "repetida", True],
                                      [2, "", "repetida", True], [1, "", "repetida", True], [2, "", "repetida", True]])
        self.assertEqual(r["apagados"], [26, 27, 28, 29])
        self.assertEqual(r["finde"], [True, 30])

    def test_js_calendario_solo_con_un_done_y_28_dias(self):
        r = self.js(r"""
pagina(el('div', {role: 'dialog'}, [mes('September 2026', rango(1, 30, n => dia(n)))]));
r.sin = leer();
pagina(el('div', {role: 'dialog'}, [mes('September 2026', rango(1, 30, n => dia(n))), listo(), listo()]));
r.dos = leer().listos;
pagina(el('div', {role: 'dialog'}, [mes('September 2026', rango(1, 27, n => dia(n))), listo()]));
r.pocos = leer();
pagina(el('mc-c-fecha', {}, [], {shadow: [el('div', {role: 'dialog'}, [el('table', {}, [el('tr', {},
  [el('td', {class: 'week-number'}, ['5'])].concat(rango(1, 30, n => dia(n))))]), el('p', {}, ['September 2026']),
  listo()])]}));
const s = leer();
r.sombra = [s.raiz, s.dias.length, s.dias.filter(d => d.fecha).length];
""")
        self.assertEqual(r["sin"], {"listos": 0, "raiz": False, "meses": [], "dias": []})
        self.assertEqual(r["dos"], 2)
        self.assertEqual(r["pocos"], {"listos": 1, "raiz": False, "meses": [], "dias": []})
        self.assertEqual(r["sombra"], [True, 30, 30])       # dentro de una raíz shadow; el número de semana no cuenta

    def test_js_calendario_por_su_cabecera(self):
        # Sin una leyenda, el mes y el año salen de la cabecera: un solo botón a la vista cuyo nombre es un mes y uno
        # solo cuyo nombre es un año, si los días, sin los de otro mes, van del 1 al último de ese mes (decisión de
        # Marcelo, encargo 48, CICLO-calendario-cosco-y-cma.md). La forma es la medida el 2026-10-02: en un mc-modal, el
        # mes y el año en dos mc-button de la cabecera, con su label; cada día, un mc-button con su número por label y,
        # adentro, un button con el número por aria-label y disabled si no se puede elegir. Hasta ahí, ningún día tenía
        # fecha, y la fila quedó NO ENVIADA.
        r = self.js(r"""
const boton = (label, opciones = {}) => el('mc-button', {label}, [],
  Object.assign({shadow: [el('button', {part: 'button'}, [])]}, opciones));
const diaMc = (n, atrs = {}) => el('mc-button', {label: String(n)}, [], {shadow: [el('button',
  Object.assign({part: 'button', 'aria-label': String(n), 'data-prueba': 'd' + n}, atrs),
  [el('div', {class: 'mc-text-and-icon small'}, [String(n)])])]});
const octubre = n => diaMc(n, n >= 12 && n <= 16 ? {} : {disabled: ''});
const semana = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(d => el('div', {class: 'weekday'}, [d]));
const modal = (cabecera, dias, extra = []) => el('mc-modal', {open: ''}, [
  el('p', {class: 'mds-headline--x-small'}, ['Container pick-up details']), el('div', {}, cabecera),
  el('div', {}, semana), el('div', {class: 'body-days'}, dias)].concat(extra, [listo()]));
const cab = (mes, anio, opciones = {}) => [boton('Previous month'), boton(mes, opciones), boton(anio),
  boton('Next month')];
const fechados = () => leer().dias.filter(d => d.fecha).length;
// En el HTML medido, el button de adentro del mes y del año va sin nombre; si lo trajera, es el mismo control.
const nombrado = label => el('mc-button', {label}, [], {shadow: [el('button', {part: 'button', 'aria-label': label},
  [el('div', {class: 'mc-text-and-icon small'}, [label])])]});
pagina(modal(cab('October', '2026'), rango(1, 31, octubre)));
const a = leer();
r.medido = [a.raiz, a.meses, corto(a)];
r.pulsa = [pulsar({fecha: '2026-10-13'}), pulsar({fecha: '2026-10-05'})].map(prueba);
r.listo = prueba(leerListo());
pagina(modal([boton('Previous month'), nombrado('October'), nombrado('2026'), boton('Next month')],
             rango(1, 31, octubre)));
r.nombrados = fechados();
// Dos meses, sin el año, con el año fuera del calendario o con el mes que no se ve: ningún día.
pagina(modal([boton('October'), boton('November'), boton('2026')], rango(1, 31, octubre)));
r.dosMeses = fechados();
pagina(modal([boton('October')], rango(1, 31, octubre)));
r.sinAnio = fechados();
pagina(el('div', {}, [boton('2026')]), modal([boton('October')], rango(1, 31, octubre)));
r.anioAfuera = fechados();
pagina(modal(cab('October', '2026', {invisible: true}), rango(1, 31, octubre)));
r.oculto = fechados();
// Con una leyenda, manda la leyenda.
pagina(modal(cab('October', '2026'), rango(1, 31, octubre), [el('span', {}, ['October 2026'])]));
r.leyenda = [...new Set(leer().dias.map(d => d.como))];
// Tres días sin marca antes del 1: ninguno; los mismos, marcados de otro mes, no cuentan; septiembre no tiene 31.
pagina(modal(cab('October', '2026'), rango(28, 30, octubre).concat(rango(1, 31, octubre))));
r.sinMarca = fechados();
pagina(modal(cab('October', '2026'), rango(28, 30, n => diaMc(n, {class: 'outside-month'}))
  .concat(rango(1, 31, octubre))));
const g = leer();
r.marcados = [g.dias.filter(d => d.como === 'cabecera').length, g.dias.filter(d => d.como === 'otro-mes').length];
pagina(modal(cab('October', '2026'), rango(28, 30, n => diaMc(n, {'aria-hidden': 'true'}))
  .concat(rango(1, 31, octubre))));
const h = leer();
r.ocultos = [h.dias.filter(d => d.como === 'cabecera').length, h.dias.filter(d => d.como === 'otro-mes').length];
// 31 celdas, pero con el 15 dos veces y sin el 31: ninguno.
pagina(modal(cab('October', '2026'), rango(1, 30, octubre).concat([octubre(15)])));
r.repetido = fechados();
pagina(modal(cab('September', '2026'), rango(1, 31, octubre)));
r.septiembre = fechados();
""")
        octubre = [[n, f"2026-10-{n:02d}", "cabecera", 12 <= n <= 16] for n in range(1, 32)]
        self.assertEqual(r["medido"], [True, [], octubre])
        self.assertEqual((r["pulsa"], r["listo"], r["nombrados"]), (["d13", None], "listo-interno", 31))
        self.assertEqual((r["dosMeses"], r["sinAnio"], r["anioAfuera"], r["oculto"]), (0, 0, 0, 0))
        self.assertEqual(r["leyenda"], ["mes"])
        self.assertEqual((r["sinMarca"], r["marcados"], r["ocultos"], r["septiembre"], r["repetido"]),
                         (0, [31, 3], [31, 3], 0, 0))

    def test_js_tarjeta_y_avisos_de_cargos(self):
        guion = DOM_AQ + "const puesto = " + self.mod._JS_MK_RETIRO_PUESTO + ";\nconst avisos = " + \
            self.mod._JS_MK_AVISOS_CARGOS + r""";
// La sección medida el 27-09: el input date oculto y la tarjeta; sin fecha, «No date selected».
const seccion = (tarjeta, valor) => el('span', {'data-test': 'sameContainersPickupDateDetails'}, [
  el('span', {class: 'hidden-date-picker', 'aria-hidden': 'true'}, [el('input', {type: 'date'}, [], {type: 'date', value: valor})]),
  el('section', {id: 'containerPickupDatePicker', 'data-test': 'haulageSelectCard'}, tarjeta)]);
const r = [];
pagina(seccion([el('section', {'data-test': 'haulage-invalid-date'}, [el('span', {}, ['No date selected'])])], ''));
r.push(puesto());
pagina(seccion([el('p', {}, ['Tuesday, 29 September 2026'])], ''));
r.push(puesto());
pagina(seccion([el('p', {}, ['Tue']), el('p', {}, ['29']), el('p', {}, ['September 2026'])], ''));
r.push(puesto());
pagina(seccion([el('p', {}, ['29']), el('p', {}, ['1']), el('p', {}, ['September 2026'])], '2026-09-29'));
r.push(puesto());
pagina(el('div', {}, ['sin tarjeta']));
r.push(puesto());
pagina(el('mc-notification', {appearance: 'warning', 'data-test': 'haulage-disclaimer'},
          ['Additional charges can incur if the date selected exceeds the agreed free time']),
       el('div', {role: 'alert'}, ['Extra fees apply for this date']),
       el('mc-notification', {appearance: 'info', heading: 'Nota', body: 'Nada de plata'}),
       el('mc-notification', {appearance: 'info', body: 'Port of discharge updated'}),
       el('mc-notification', {appearance: 'warning', body: 'Demurrage may apply'}, [], {oculto: true}),
       el('mc-c-x', {}, [], {shadow: [el('mc-notification', {appearance: 'warning', heading: 'Cost', body: 'Storage'})]}),
       el('p', {}, ['COSTOS PREPAID B/L EMISION EN ORIGEN']));
r.push(avisos());
console.log(JSON.stringify(r));
"""
        vacia, entera, aparte, dos_sueltos, sin_tarjeta, cargos = correr_node(self, guion)
        base = {"tarjeta": True, "vacia": False, "fechas": [], "valor": ""}
        self.assertEqual(vacia, dict(base, vacia=True))
        self.assertEqual(entera, dict(base, fechas=["2026-09-29"]))
        self.assertEqual(aparte, dict(base, fechas=["2026-09-29"]))              # el día aparte del mes y su año
        self.assertEqual(dos_sueltos, dict(base, valor="2026-09-29"))            # dos números sueltos: ninguno
        self.assertEqual(sin_tarjeta, {"tarjeta": False, "vacia": False, "fechas": [], "valor": ""})
        self.assertEqual(cargos, ["Additional charges can incur if the date selected exceeds the agreed free time",
                                  "Extra fees apply for this date", "Cost · Storage"])


class PaginaTerminos(soporte.PaginaFalsa):
    """La revisión falsa de MAERSK para los términos: _JS_MK_TERMINOS responde, en orden, lo de 'lecturas' (la última se
    repite); _JS_MK_TERMINOS_PULSAR pulsa la casilla si 'pulsa', y con 'navega' la página se va a otra dirección. Anota
    cuántas veces baja y cada clic. Otro JavaScript, o la casilla buscada con otro texto, hacen caer la prueba."""

    def __init__(self, mod, lecturas, pulsa=True, navega=False):
        super().__init__(url="https://portal.invalid/book/review")
        self.mod, self.lecturas, self.pulsa, self.navega = mod, list(lecturas), pulsa, navega
        self.clics, self.bajadas = [], 0

    def evaluate(self, js, *a):
        if js == "window.scrollTo(0, document.body.scrollHeight)":
            self.bajadas += 1
            return None
        if js == self.mod._JS_MK_TERMINOS and a == (self.mod.MK_TERMINOS,):
            return self.lecturas.pop(0) if len(self.lecturas) > 1 else self.lecturas[0]
        if js == self.mod._JS_MK_TERMINOS_PULSAR and a == (self.mod.MK_TERMINOS,):
            if self.pulsa:
                self.clics.append("casilla")
                if self.navega:
                    self.url = "https://portal.invalid/terms"
            return self.pulsa
        if js == self.mod._JS_HTML_COMPLETO:
            return {}
        raise AssertionError("JavaScript inesperado")

    def content(self):
        return "<body>revision sintetica</body>"


class TestTerminosMaersk(ConRegistro):
    """La casilla de los términos de la revisión de MAERSK, por su texto (decisión de Marcelo,
    CICLO-maersk-retiro-y-terminos.md): «I have read and accept all the terms and conditions of this booking», leída con
    OCR en las capturas de la revisión del 21-09. Hasta el encargo 36, «el último checkbox» de la pantalla (FRENO)."""
    TEXTO = "I have read and accept all the terms and conditions of this booking"
    UNA = {"n": 1, "marcada": False}
    MARCADA = {"n": 1, "marcada": True}
    NADA = "no pulsé nada más y la reserva no se envió"

    def marcar(self, pagina):
        self.n = getattr(self, "n", 0) + 1
        reg, _, log = self.corrida(f"terminos_{self.n}")
        r = self.mod._mk_marcar_terminos(pagina, reg, 30)
        return r, log.read_text(encoding="utf-8")

    def test_el_texto_es_el_de_la_captura(self):
        self.assertEqual(self.mod.MK_TERMINOS, self.TEXTO)

    def test_marca_la_casilla_por_su_texto(self):
        pagina = PaginaTerminos(self.mod, [self.UNA, self.MARCADA])
        r, log = self.marcar(pagina)
        self.assertIsNone(r)
        self.assertEqual((pagina.clics, pagina.bajadas), (["casilla"], 1))       # baja al final antes de buscarla
        self.assertIn("marcado: términos y condiciones aceptados, la casilla por su texto\n", log)
        # La revisión queda guardada antes del clic: su HTML no está medido (revisión del encargo 36).
        self.assertEqual(pagina.capturas, [("mk_f30_terminos.png", False)])
        self.assertIn("evidencia con la casilla de los términos: mk_f30_terminos.png", log)
        # Tarda en aparecer: la espera, hasta MK_ESPERA_TERMINOS s.
        pagina = PaginaTerminos(self.mod, [{"n": 0}] * 5 + [self.UNA, self.MARCADA])
        r, _ = self.marcar(pagina)
        self.assertEqual((r, pagina.clics, pagina.esperas), (None, ["casilla"], 6 + 1))

    def test_ya_marcada_no_la_pulsa(self):
        pagina = PaginaTerminos(self.mod, [self.MARCADA])
        r, log = self.marcar(pagina)
        self.assertEqual((r, pagina.clics, pagina.capturas), (None, [], [("mk_f30_terminos.png", False)]))
        self.assertIn("la casilla de los términos ya estaba marcada: no la pulsé", log)

    def test_sin_saber_si_estaba_marcada_no_la_pulsa(self):
        # Pulsar una casilla que quizás estaba marcada la desmarcaría (revisión del encargo 36).
        pagina = PaginaTerminos(self.mod, [{"n": 1, "marcada": None}])
        r, _ = self.marcar(pagina)
        self.assertEqual(r, ("NO ENVIADA", f"MAERSK: no pude leer si la casilla «{self.TEXTO}» estaba marcada, así que no "
                                           "la pulsé; la reserva no se envió"))
        self.assertEqual((pagina.clics, pagina.capturas), ([], [("mk_f30_terminos.png", False)]))

    def test_sin_una_sola_corta_sin_pulsar(self):
        for lecturas, n, esperas in (([{"n": 0}], 0, 20), ([{"n": 2, "marcada": None}], 2, 1), ([{}], 0, 20)):
            with self.subTest(n=n, lecturas=lecturas):
                pagina = PaginaTerminos(self.mod, lecturas)
                with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
                    self.marcar(pagina)
                self.assertEqual((e.exception.paso, e.exception.buscaba),
                                 ("Términos de MAERSK", f"una sola casilla «{self.TEXTO}» (había {n})"))
                self.assertEqual((pagina.clics, pagina.esperas), ([], esperas))

    def test_comprueba_despues_del_clic(self):
        # Después del clic: una sola casilla, marcada, y la página en la misma dirección. Hasta la revisión del encargo
        # 36, un estado que no se podía leer contaba como marcada.
        pulse = f"MAERSK: pulsé la casilla «{self.TEXTO}», pero"
        casos = (([self.UNA, {"n": 1, "marcada": False}], {}, f"{pulse} no quedó marcada; {self.NADA}", ["casilla"]),
                 ([self.UNA, {"n": 1, "marcada": None}], {}, f"{pulse} no pude comprobar que quedó marcada; {self.NADA}",
                  ["casilla"]),
                 ([self.UNA, {"n": 2, "marcada": None}], {}, f"{pulse} no pude comprobar que quedó marcada; {self.NADA}",
                  ["casilla"]),
                 ([self.UNA, self.MARCADA], {"navega": True},
                  f"MAERSK: después del clic en la casilla «{self.TEXTO}», la página cambió; {self.NADA}", ["casilla"]),
                 ([self.UNA], {"pulsa": False},
                  f"MAERSK: al volver a buscar la casilla «{self.TEXTO}», ya no era una sola sin marcar; {self.NADA}", []))
        for lecturas, opciones, motivo, clics in casos:
            with self.subTest(motivo=motivo):
                pagina = PaginaTerminos(self.mod, lecturas, **opciones)
                r, _ = self.marcar(pagina)
                self.assertEqual((r, pagina.clics), (("NO ENVIADA", motivo), clics))

    def test_js_casilla_por_su_texto(self):
        guion = DOM_AQ + "const leer = " + self.mod._JS_MK_TERMINOS + ";\nconst pulsar = " + \
            self.mod._JS_MK_TERMINOS_PULSAR + r""";
const TEXTO = 'I have read and accept all the terms and conditions of this booking';
// Lo que devuelve la lectura, si la marca pulsó y qué pulsó (el data-prueba de lo pulsado).
const ver = () => { global.clics = []; const l = leer(TEXTO); const p = pulsar(TEXTO); return [l, p, global.clics]; };
const mc = (prueba, atributos, hijos, marcada, delInput = marcada) => el('mc-checkbox',
  Object.assign({'data-prueba': prueba}, atributos), hijos, {checked: marcada, shadow: [el('label', {}, [
    el('input', {type: 'checkbox', 'data-prueba': prueba + '-input'}, [], {type: 'checkbox', checked: delInput}),
    el('slot', {name: 'label'})])]});
// Los interruptores de cookies medidos en un «Select sailing» del 25-09: con ellos, «el último checkbox» sería «Unclassified».
const galletas = ['Essential', 'Functional', 'Statistical', 'Marketing', 'Unclassified'].map(n =>
  el('input', {type: 'checkbox', 'aria-label': n, 'data-prueba': n}, [], {type: 'checkbox', checked: false}));
const r = {};
pagina(mc('terminos', {label: TEXTO}, [], false), el('div', {class: 'cookies'}, galletas));
r.label = ver();
pagina(mc('slot', {}, [el('span', {slot: 'label'}, ['I have read and accept all the ', el('a', {}, ['terms and conditions']),
                                                    ' of this booking.'])], true), ...galletas);
r.slot = ver();
pagina(el('label', {}, [el('input', {type: 'checkbox', 'data-prueba': 'input'}, [], {type: 'checkbox', checked: false}),
                        ' ' + TEXTO]));
r.input = ver();
pagina(el('mc-checkbox', {label: TEXTO, 'data-prueba': 'uno'}, [], {checked: false, shadow: [
  el('input', {type: 'checkbox', 'aria-label': TEXTO, 'data-prueba': 'uno-input'}, [], {type: 'checkbox', checked: false})]}));
r.mismo = ver();
pagina(el('mc-checkbox', {label: TEXTO, 'data-prueba': 'anfitrion'}, [], {checked: true}));
r.anfitrion = ver();
pagina(mc('distintos', {label: TEXTO}, [], true, false));
r.distintos = ver();
pagina(el('div', {role: 'checkbox', 'aria-checked': 'false', 'data-prueba': 'rol'}, [TEXTO]));
r.rol = ver();
pagina(mc('a', {label: TEXTO}, [], false), mc('b', {label: TEXTO}, [], false));
r.dos = ver();
pagina(mc('otra', {label: 'I have read and accept all the terms and conditions'}, [], false));
r.otra = ver();
pagina(el('mc-checkbox', {label: TEXTO}, [], {oculto: true, checked: false}));
r.oculta = ver();
console.log(JSON.stringify(r));
"""
        r = correr_node(self, guion)
        leida = lambda n, marcada: {"n": n, "marcada": marcada}
        # Se pulsa el input de la casilla, nunca el centro del mc-checkbox (revisión del encargo 36: ahí puede estar el
        # enlace de «terms and conditions»); una casilla ya marcada, o con estados que no coinciden, no se pulsa.
        self.assertEqual(r, {"label": [leida(1, False), True, ["terminos-input"]],
                             "slot": [leida(1, True), False, []],
                             "input": [leida(1, False), True, ["input"]],
                             "mismo": [leida(1, False), True, ["uno-input"]],
                             "anfitrion": [leida(1, True), False, []],
                             "distintos": [leida(1, None), False, []],
                             "rol": [leida(1, False), True, ["rol"]],
                             "dos": [leida(2, None), False, []],
                             "otra": [leida(0, None), False, []],
                             "oculta": [leida(0, None), False, []]})


class CampoReferencia:
    """Un textarea de PaginaReferencia: si se ve, y lo que se hace en él, en las acciones de su página."""
    def __init__(self, pagina, visible):
        self.pagina, self.visible = pagina, visible

    def is_visible(self):
        return self.visible

    def scroll_into_view_if_needed(self, **k):
        pass

    def click(self, **k):
        self.pagina.acciones.append(("clic", self.visible))

    def fill(self, texto, **k):
        if self.pagina.falla:
            raise RuntimeError(self.pagina.falla)
        self.pagina.acciones.append(("escribe", self.visible, texto))


class PaginaReferencia(soporte.PaginaFalsa):
    """«Additional details» falsa de MAERSK para la referencia de retiro: page.locator(MK_REFERENCIA) da los campos de
    'campos' (True si se ve); otro selector hace caer la prueba. Con 'falla', escribir falla con ese mensaje; con
    'rota', el localizador falla."""
    def __init__(self, mod, campos, falla=None, rota=False):
        super().__init__(url="https://portal.invalid/book/additional-details")
        self.mod, self.acciones, self.falla, self.rota = mod, [], falla, rota
        self.campos = [CampoReferencia(self, v) for v in campos]

    def locator(self, selector):
        if self.rota:
            raise RuntimeError("la página se cerró")
        if selector != self.mod.MK_REFERENCIA:
            raise AssertionError(f"selector inesperado: {selector}")
        campos = self.campos
        return types.SimpleNamespace(count=lambda: len(campos), nth=lambda i: campos[i])


class TestReferenciaMaersk(ConRegistro):
    """La referencia de retiro de MAERSK en su campo, por su name (decisión de Marcelo, CICLO-maersk-ultimos-puntos.md):
    el único textarea a la vista con name="haulageReference", medido en mk_f10_sin_objetivo.html del 27-09. Hasta el
    encargo 37 iba en «el primer textarea», que ese día era el campo oculto del asistente «Ask Maersk»."""

    def escribir(self, pagina):
        self.n = getattr(self, "n", 0) + 1
        reg, vistas, log = self.corrida(f"referencia_{self.n}")
        det = []
        r = self.mod._mk_referencia_de_retiro(pagina, reg, det, "REFERENCIA DE PRUEBA")
        return r, det, log.read_text(encoding="utf-8")

    def test_el_campo_es_el_medido(self):
        self.assertEqual(self.mod.MK_REFERENCIA, "textarea[name='haulageReference']")

    def test_escribe_en_el_unico_a_la_vista(self):
        # Un campo oculto con el mismo name no cuenta.
        pagina = PaginaReferencia(self.mod, [False, True])
        r, det, log = self.escribir(pagina)
        self.assertIsNone(r)
        self.assertEqual(pagina.acciones, [("clic", True), ("escribe", True, "REFERENCIA DE PRUEBA")])
        self.assertEqual(det, ["haulageRef=REFERENCIA DE PRUEBA"])
        self.assertIn("haulage reference completada: 'REFERENCIA DE PRUEBA'", log)

    def test_sin_un_solo_campo_no_escribe(self):
        casos = (([], False, "había 0"), ([False], False, "había 0"), ([True, True], False, "había 2"),
                 ([True], True, "no pude leer la página: RuntimeError: la página se cerró"))
        for campos, rota, cuantos in casos:
            with self.subTest(campos=campos, rota=rota):
                pagina = PaginaReferencia(self.mod, campos, rota=rota)
                reg, _, _ = self.corrida(f"sin_campo_{len(campos)}_{rota}")
                with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
                    self.mod._mk_referencia_de_retiro(pagina, reg, [], "X")
                self.assertEqual((e.exception.paso, e.exception.buscaba, pagina.acciones),
                                 ("Referencia de retiro de MAERSK",
                                  f"un solo campo «haulageReference» a la vista ({cuantos})", []))

    def test_si_no_se_puede_escribir_corta(self):
        pagina = PaginaReferencia(self.mod, [True], falla="el campo está deshabilitado")
        r, det, _ = self.escribir(pagina)
        self.assertEqual(r, ("NO ENVIADA", "MAERSK: falló la escritura de la referencia de retiro (RuntimeError: el "
                                           "campo está deshabilitado); no pulsé nada más y la reserva no se envió"))
        self.assertEqual(det, [])

    def test_reservar_maersk_la_escribe_y_corta(self):
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "reservar_maersk")
        cuerpos = [n.body for n in ast.walk(f) if isinstance(getattr(n, "body", None), list)]
        cuerpo, i = next((c, i) for c in cuerpos for i, s in enumerate(c)
                         if ast.unparse(s) == "corte = _mk_referencia_de_retiro(page, reg, det, ref_txt)")
        self.assertEqual(ast.unparse(cuerpo[i + 1]), "if corte:\n    return corte")
        self.assertEqual(ast.unparse(cuerpo[i - 1]),
                         "ref_txt = str(reserva.get('comentario') or '').strip() or COSCO_REMARK")


class PaginaServicios(soporte.PaginaFalsa):
    """«Recommended services» falsa de MAERSK para «Continue»: _JS_MK_CONTINUAR responde, por lectura, lo que dice
    'vistos' (una lista; la última se repite; una excepción, la levanta). _JS_MK_CONTINUAR_PULSAR da el botón si
    'pulsable'; su clic queda en 'clics', o falla las primeras 'falla' veces (con 'avanza', el que falla igual lleva a
    'siguiente', «Additional details» si no se dice otra: un clic que falló pudo haber salido). _JS_MK_LO_QUE_PIDE
    responde 'pide'. Todo lo demás que se le pida queda en 'prohibidos' aunque el programa se trague el error: cada
    prueba exige esa lista vacía. Desde el encargo 40 sirve también para «Booking Information»."""
    def __init__(self, mod, vistos=(1,), pulsable=True, falla=0, avanza=False, pide=None,
                 url="https://portal.invalid/book/additional-services",
                 siguiente="https://portal.invalid/book/additional-details"):
        super().__init__(url=url)
        self.mod, self.vistos, self.pulsable, self.falla, self.avanza, self.pide = (mod, list(vistos), pulsable, falla,
                                                                                    avanza, pide)
        self.siguiente, self.main_frame, self.clics, self.args, self.prohibidos = siguiente, None, [], [], []

    def evaluate(self, js, *a):
        if js == self.mod._JS_MK_LO_QUE_PIDE:
            return self.pide
        if js == self.mod._JS_HTML_COMPLETO:
            return {}
        if js != self.mod._JS_MK_CONTINUAR:
            self.prohibidos.append("evaluate")
            raise AssertionError("JavaScript inesperado")
        self.args.append(a)
        r = self.vistos.pop(0) if len(self.vistos) > 1 else self.vistos[0]
        if isinstance(r, Exception):
            raise r
        return r

    def evaluate_handle(self, js, arg=None):
        if js != self.mod._JS_MK_CONTINUAR_PULSAR:
            self.prohibidos.append("evaluate_handle")
            raise AssertionError("JavaScript inesperado")
        pagina = self

        def pulsar(**k):
            if pagina.falla:
                pagina.falla -= 1
                if pagina.avanza:
                    pagina.url = pagina.siguiente
                raise RuntimeError("otro elemento recibiría el clic")
            pagina.clics.append("Continue")
        el = (types.SimpleNamespace(click=pulsar, scroll_into_view_if_needed=lambda **k: None)
              if self.pulsable else None)
        return types.SimpleNamespace(as_element=lambda: el)

    def content(self):
        return "<body>servicios sintetico</body>"

    def __getattr__(self, nombre):
        if nombre.startswith("__"):
            raise AttributeError(nombre)
        self.__dict__.setdefault("prohibidos", []).append(nombre)
        raise AttributeError(nombre)


class TestContinuarMaersk(ConRegistro):
    """«Continue» de «Recommended services» de MAERSK (decisión de Marcelo, CICLO-maersk-cuatro-puntos.md): se pulsa
    solo si hay exactamente uno a la vista; con cero o más de uno, NO ENVIADA con lo que el portal pide. Hasta el
    encargo 39 pulsaba el primero con ese texto o, por JavaScript, el primer elemento a la vista con ese texto, y si no
    encontraba ninguno seguía sin cortar."""
    NADA = "no pulsé nada más y la reserva no se envió"

    def pagina(self, **opciones):
        """Una PaginaServicios que, al terminar la prueba, no tiene que haber recibido nada prohibido."""
        pagina = PaginaServicios(self.mod, **opciones)
        self.addCleanup(lambda: self.assertEqual(pagina.prohibidos, []))
        return pagina

    def continuar(self, pagina):
        self.n = getattr(self, "n", 0) + 1
        reg, vistas, log = self.corrida(f"continuar_{self.n}")
        return self.mod._mk_continuar_servicios(pagina, reg, 30), log, vistas

    def test_continuar_es_el_medido(self):
        self.assertEqual((self.mod.MK_CONTINUAR, self.mod.MK_INTENTOS_CONTINUAR), ("Continue", 15))

    def test_continue_uno_a_la_vista(self):
        pagina = self.pagina()
        r, log, _ = self.continuar(pagina)
        self.assertEqual((r, pagina.clics, pagina.esperas, pagina.args),
                         (None, ["Continue"], 0, [({"textos": ["Continue"]},)]))
        self.assertIn("pulsado 'Continue' en Recommended services", log.read_text(encoding="utf-8"))

    def test_espera_que_aparezca(self):
        pagina = self.pagina(vistos=[0, 0, 1])
        r, _, _ = self.continuar(pagina)
        self.assertEqual((r, pagina.clics, pagina.esperas), (None, ["Continue"], 2))

    def test_sin_uno_solo_corta(self):
        # Con cero o con más de uno a la vista, en los 15 intentos, corta sin pulsar nada.
        casos = ((0, "había 0"), (2, "había 2"),
                 (RuntimeError("la página se cerró"), "no pude leer la página: RuntimeError: la página se cerró"))
        for vistos, cuantos in casos:
            with self.subTest(vistos=vistos):
                pagina = self.pagina(vistos=[vistos])
                with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
                    self.continuar(pagina)
                self.assertEqual((e.exception.paso, e.exception.buscaba, e.exception.pide),
                                 ("Recommended services de MAERSK",
                                  f"un solo botón «Continue» a la vista, por su texto, en 15 intentos ({cuantos})", ""))
                self.assertEqual((pagina.clics, pagina.esperas), ([], 14))
        # El corte lleva lo que el portal pide en esa pantalla.
        pagina = self.pagina(vistos=[2], pide={"campos": ["Cargo value"], "mensajes": []})
        with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
            self.continuar(pagina)
        self.assertEqual(e.exception.pide, "Cargo value")

    def test_ya_en_additional_details(self):
        pagina = self.pagina(url="https://portal.invalid/book/additional-details")
        r, log, _ = self.continuar(pagina)
        self.assertEqual((r, pagina.clics, pagina.esperas, pagina.args), (None, [], 0, []))
        self.assertIn("«Additional details» ya apareció; no hace falta pulsar 'Continue'",
                      log.read_text(encoding="utf-8"))

    def test_no_acepta_el_clic(self):
        pagina = self.pagina(falla=99)
        r, log, vistas = self.continuar(pagina)
        detalle = ("MAERSK: el botón «Continue» de «Recommended services» estaba a la vista, pero no aceptó el clic "
                   f"(RuntimeError: otro elemento recibiría el clic); {self.NADA}")
        self.assertEqual((r, pagina.clics, pagina.esperas), (("NO ENVIADA", detalle), [], 14))
        self.assertEqual(pagina.capturas, [("mk_f30_servicios.png", False)])
        for donde in (log.read_text(encoding="utf-8"), "\n".join(vistas)):          # log.txt y pantalla
            self.assertIn(f"· ✗ NO ENVIADA · {detalle}", donde)

    def test_clic_que_fallo_pero_avanzo(self):
        # Un clic que falló pudo haber salido: si «Additional details» apareció, sigue sin otro clic.
        pagina = self.pagina(falla=1, avanza=True)
        r, log, _ = self.continuar(pagina)
        self.assertEqual((r, pagina.clics, pagina.esperas), (None, [], 1))
        self.assertIn("«Additional details» ya apareció", log.read_text(encoding="utf-8"))

    def test_releido_ya_no_es_uno(self):
        # Justo antes del clic se vuelve a leer: si ya no es uno solo, no pulsa, y el motivo lo dice.
        pagina = self.pagina(pulsable=False)
        with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
            self.continuar(pagina)
        self.assertEqual(e.exception.buscaba, "un solo botón «Continue» a la vista, por su texto, en 15 intentos "
                                              "(había 1, pero al volver a leer ya no era uno solo)")
        self.assertEqual((pagina.clics, pagina.esperas), ([], 14))

    def test_reservar_maersk_continua_sin_respaldo(self):
        # En «Recommended services», reservar_maersk pulsa «Continue» solo con _mk_continuar_servicios y corta si
        # devuelve el corte; el primero con ese texto y el respaldo en JavaScript ya no están.
        fuente = Path(self.mod.__file__).read_text(encoding="utf-8")
        f = next(n for n in ast.parse(fuente).body if isinstance(n, ast.FunctionDef) and n.name == "reservar_maersk")
        cuerpos = [n.body for n in ast.walk(f) if isinstance(getattr(n, "body", None), list)]
        cuerpo, i = next((c, i) for c in cuerpos for i, s in enumerate(c)
                         if ast.unparse(s) == "corte = _mk_continuar_servicios(page, reg, f)")
        self.assertEqual(ast.unparse(cuerpo[i + 1]), "if corte:\n    return corte")
        segmento = ast.get_source_segment(fuente, f)
        for forma in ("getAllDeep", "click_cont", "b_cont"):
            self.assertNotIn(forma, segmento)

    def test_js_continuar(self):
        # Un «Continue» es un mc-button (por su label o su texto), un button, un enlace o lo que tenga role button, con
        # ese texto entero, sin distinguir mayúsculas y a la vista; lo que está dentro de otro es el mismo control. Un
        # mc-button oculto oculta también su botón interno.
        guion = (DOM_AQ + "const f = " + self.mod._JS_MK_CONTINUAR + ";\nconst p = " + self.mod._JS_MK_CONTINUAR_PULSAR
                 + r""";
const a = {textos: ['Continue']};
const mc = (dp, label, opciones = {}) => el('mc-button', {label, 'data-prueba': dp}, [],
  Object.assign({}, opciones, {shadow: [el('button', {'data-prueba': dp + '-interno'}, [label], opciones)]}));
const r = [];
const leer = () => { const e = p(a); r.push([f(a), e ? e.getAttribute('data-prueba') : null]); };
// 0. Un mc-button con su label y su botón interno: un solo control; 1. dos.
pagina(mc('c', 'Continue'));
leer();
pagina(mc('c1', 'Continue'), mc('c2', 'Continue'));
leer();
// 2. Uno invisible y otro a la vista; 3. uno sin cajas (display:none).
pagina(mc('oculto', 'Continue', {invisible: true}), mc('c', 'Continue'));
leer();
pagina(mc('sin-cajas', 'Continue', {oculto: true}));
leer();
// 4. «Continue to book» no es «Continue»; un span con ese texto tampoco es un control.
pagina(mc('libro', 'Continue to book'), el('span', {'data-prueba': 's'}, ['Continue']));
leer();
// 5. Un button suelto; 6. un enlace y un mc-button: dos; 7. role button, en mayúsculas.
pagina(el('button', {'data-prueba': 'b'}, ['Continue']));
leer();
pagina(el('a', {'data-prueba': 'l'}, [' Continue ']), mc('c', 'Continue'));
leer();
pagina(el('div', {role: 'button', 'data-prueba': 'd'}, ['CONTINUE']));
leer();
// 8. Un mc-button sin label, con su texto adentro.
pagina(el('mc-button', {'data-prueba': 't'}, ['Continue']));
leer();
console.log(JSON.stringify(r));
""")
        self.assertEqual(correr_node(self, guion), [
            [1, "c"], [2, None], [1, "c"], [0, None], [0, None], [1, "b"], [2, None], [1, "d"], [1, "t"]])


class TestContinuarALaNaveMaersk(ConRegistro):
    """«Continue to book» o «Continue» de «Booking Information» de MAERSK (decisión de Marcelo,
    CICLO-maersk-busqueda-vacia.md): se pulsa solo si hay exactamente uno a la vista entre los dos; con cero o más de
    uno, NO ENVIADA con lo que el portal pide; si está y no acepta el clic, formulario incompleto. Hasta el encargo 40,
    el primero habilitado cuyo nombre accesible los traía, sin mirar si se veía."""
    NADA = "no pulsé nada más y la reserva no se envió"
    TEXTOS = ("Continue to book", "Continue")
    AMBOS = "«Continue to book» o «Continue»"

    def pagina(self, **opciones):
        """Una PaginaServicios en «Booking Information», que al terminar la prueba no tiene que haber recibido nada
        prohibido."""
        opciones.setdefault("url", "https://portal.invalid/book/")
        opciones.setdefault("siguiente", "https://portal.invalid/book/sailings")
        pagina = PaginaServicios(self.mod, **opciones)
        self.addCleanup(lambda: self.assertEqual(pagina.prohibidos, []))
        return pagina

    def continuar(self, pagina):
        self.n = getattr(self, "n", 0) + 1
        reg, vistas, log = self.corrida(f"continuar_nave_{self.n}")
        return self.mod._mk_continuar_a_la_nave(pagina, reg, ["ruta=A-B"], 30, self.TEXTOS), log, vistas

    def test_uno_a_la_vista(self):
        pagina = self.pagina()
        r, log, _ = self.continuar(pagina)
        self.assertEqual((r, pagina.clics, pagina.esperas, pagina.args),
                         (None, ["Continue"], 0, [({"textos": list(self.TEXTOS)},)]))
        self.assertIn(f"pulsado el único {self.AMBOS} a la vista", log.read_text(encoding="utf-8"))

    def test_sin_uno_solo_corta(self):
        # Con cero o con más de uno a la vista, en los 15 intentos, corta sin pulsar nada, con lo que pide el portal.
        casos = ((0, "había 0"), (2, "había 2"),
                 (RuntimeError("la página se cerró"), "no pude leer la página: RuntimeError: la página se cerró"))
        for vistos, cuantos in casos:
            with self.subTest(vistos=vistos):
                pagina = self.pagina(vistos=[vistos], pide={"campos": ["Commodity"], "mensajes": []})
                with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
                    self.continuar(pagina)
                self.assertEqual((e.exception.paso, e.exception.buscaba, e.exception.pide),
                                 ("Booking Information de MAERSK",
                                  f"un solo botón {self.AMBOS} a la vista, por su texto, en 15 intentos ({cuantos})",
                                  "Commodity"))
                self.assertEqual((pagina.clics, pagina.esperas), ([], 14))

    def test_no_acepta_el_clic_es_formulario_incompleto(self):
        pagina = self.pagina(falla=99, pide={"campos": ["Commodity"], "mensajes": ["Commodity is required"]})
        r, log, vistas = self.continuar(pagina)
        detalle = ("MAERSK: formulario incompleto, y el portal pide: Commodity («Commodity is required»); "
                   f"{self.NADA} (ruta=A-B)")
        self.assertEqual((r, pagina.clics, pagina.esperas), (("NO ENVIADA", detalle), [], 14))
        self.assertEqual(pagina.capturas, [("mk_f30_4_sailing.png", False), ("mk_f30_booking.png", False)])
        texto = log.read_text(encoding="utf-8")
        self.assertIn(f"No pude continuar a la selección de nave: {self.AMBOS} no aceptó el clic (RuntimeError: otro "
                      "elemento recibiría el clic).", texto)
        for donde in (texto, "\n".join(vistas)):                                    # log.txt y pantalla
            self.assertIn(f"· ✗ NO ENVIADA · {detalle}", donde)

    def test_ya_en_la_seleccion_de_nave(self):
        pagina = self.pagina(url="https://portal.invalid/book/sailings")
        r, log, _ = self.continuar(pagina)
        self.assertEqual((r, pagina.clics, pagina.esperas, pagina.args), (None, [], 0, []))
        self.assertIn(f"«Select sailing» ya apareció; no hace falta pulsar {self.AMBOS}",
                      log.read_text(encoding="utf-8"))

    def test_clic_que_fallo_pero_avanzo(self):
        # Un clic que falló pudo haber salido: si la selección de nave apareció, sigue sin otro clic.
        pagina = self.pagina(falla=1, avanza=True)
        r, _, _ = self.continuar(pagina)
        self.assertEqual((r, pagina.clics, pagina.esperas), (None, [], 1))

    def test_reservar_maersk_sigue_solo_con_el_ayudante(self):
        # reservar_maersk pasa a la selección de nave solo con _mk_continuar_a_la_nave, con los dos textos, y corta si
        # devuelve el corte; el primero habilitado por su nombre accesible ya no está. «Continue to book» queda escrito
        # en reservar_maersk: test_candado fotografía ese texto.
        fuente = Path(self.mod.__file__).read_text(encoding="utf-8")
        f = next(n for n in ast.parse(fuente).body if isinstance(n, ast.FunctionDef) and n.name == "reservar_maersk")
        cuerpos = [n.body for n in ast.walk(f) if isinstance(getattr(n, "body", None), list)]
        llamada = "corte = _mk_continuar_a_la_nave(page, reg, det, f, ('Continue to book', MK_CONTINUAR))"
        hallado = next(((c, i) for c in cuerpos for i, s in enumerate(c) if ast.unparse(s) == llamada), None)
        self.assertIsNotNone(hallado, f"reservar_maersk no trae: {llamada}")
        cuerpo, i = hallado
        self.assertEqual([ast.unparse(s) for s in cuerpo[i - 1:i + 2]],
                         ["paso_antes = _mk_paso_actual(page)", llamada, "if corte:\n    return corte"])
        segmento = ast.get_source_segment(fuente, f)
        for forma in ("get_by_role(\"button\", name=nm", "cont_ok", "is_enabled()"):
            self.assertNotIn(forma, segmento)

    def test_js_con_los_dos_textos(self):
        # Con los dos textos cuenta un «Continue to book» (el medido: un mc-button por su label, con su botón interno)
        # y un «Continue», cada uno con su texto entero y sin distinguir mayúsculas; los dos a la vista son dos.
        guion = (DOM_AQ + "const f = " + self.mod._JS_MK_CONTINUAR + ";\nconst p = " + self.mod._JS_MK_CONTINUAR_PULSAR
                 + r""";
const a = {textos: ['Continue to book', 'Continue']};
const mc = (dp, label, opciones = {}) => el('mc-button', {label, 'data-prueba': dp}, [],
  Object.assign({}, opciones, {shadow: [el('button', {'data-prueba': dp + '-interno'}, [label], opciones)]}));
const r = [];
const leer = () => { const e = p(a); r.push([f(a), e ? e.getAttribute('data-prueba') : null]); };
// 0. El medido; 1. un «Continue» solo.
pagina(mc('libro', 'Continue to book'));
leer();
pagina(mc('c', 'Continue'));
leer();
// 2. Los dos a la vista: dos; 3. el «Continue to book» sin cajas (display:none) y un «Continue»: uno.
pagina(mc('libro', 'Continue to book'), mc('c', 'Continue'));
leer();
pagina(mc('libro', 'Continue to book', {oculto: true}), mc('c', 'Continue'));
leer();
// 4. «Continue to booking» no es ninguno de los dos; 5. un button en mayúsculas sí.
pagina(mc('otro', 'Continue to booking'));
leer();
pagina(el('button', {'data-prueba': 'b'}, ['CONTINUE TO BOOK']));
leer();
console.log(JSON.stringify(r));
""")
        self.assertEqual(correr_node(self, guion),
                         [[1, "libro"], [1, "c"], [2, None], [1, "c"], [0, None], [1, "b"]])


class PaginaShipper(soporte.PaginaFalsa):
    """«Additional details» falsa de MAERSK para el Shipper, por etapas: «antes» de pulsar nada, «abierto» después del
    «Add», «elegido» después del resultado, «marcado» después de su casilla (encargo 40) y «cerrado» después del
    «Close» (encargo 39). En cada etapa, _JS_MK_SHIPPER responde lo suyo (con una lista, una respuesta por lectura, y
    la última se repite; una excepción, la levanta). _JS_MK_SHIPPER_PULSAR da el elemento de
    'que' si está en 'pulsables'; su clic queda en 'clics' y pasa a la etapa siguiente, o falla si 'que' está en
    'fallan'. _JS_MK_SHIPPER_CASILLA responde 'casilla' (por omisión, que la posición y las cifras no coinciden), y
    _JS_MK_SHIPPER_MARCAR pulsa la casilla si «casilla» está en 'pulsables', da false si no, o falla si está en
    'fallan'; los dos quedan en 'marcar'. Anota los argumentos de cada JavaScript. Todo lo demás que se le pida (otro
    JavaScript, el teclado, el mouse, un localizador…) queda en 'prohibidos' aunque el programa se trague el error: cada
    prueba exige esa lista vacía (revisión del encargo 38: con un try, una tecla Escape o un clic en «Close» volvían
    sin que la red lo viera)."""
    def __init__(self, mod, antes, abierto=None, elegido=None, cerrado=None, marcado=None, casilla=None,
                 pulsables=("agregar", "resultado", "cerrar", "casilla"), fallan=()):
        super().__init__(url="https://portal.invalid/book/additional-details")
        self.mod, self.args, self.pulsar, self.clics, self.etapa = mod, [], [], [], "antes"
        self.main_frame, self.prohibidos, self.marcar = None, [], []
        lista = lambda r: list(r) if isinstance(r, list) else [r]
        self.respuestas = {"antes": lista(antes), "abierto": lista(abierto), "elegido": lista(elegido),
                           "cerrado": lista(cerrado), "marcado": lista(marcado)}
        self.casilla = {"casilla": "distintas", "marcada": None} if casilla is None else casilla
        self.pulsables, self.fallan = pulsables, fallan

    def evaluate(self, js, *a):
        if js == self.mod._JS_HTML_COMPLETO:
            return {}
        if js == self.mod._JS_MK_SHIPPER_CASILLA:
            self.marcar.append(("leer", a))
            if isinstance(self.casilla, Exception):
                raise self.casilla
            return self.casilla
        if js == self.mod._JS_MK_SHIPPER_MARCAR:
            self.marcar.append(("marcar", a))
            if "casilla" in self.fallan:
                raise RuntimeError("la página se cerró")
            if "casilla" not in self.pulsables:
                return False
            self.clics.append("casilla")
            self.etapa = "marcado"
            return True
        if js != self.mod._JS_MK_SHIPPER:
            self.prohibidos.append("evaluate")
            raise AssertionError("JavaScript inesperado")
        self.args.append(a)
        lista = self.respuestas[self.etapa]
        r = lista.pop(0) if len(lista) > 1 else lista[0]
        if isinstance(r, Exception):
            raise r
        return r

    def evaluate_handle(self, js, arg=None):
        if js != self.mod._JS_MK_SHIPPER_PULSAR:
            self.prohibidos.append("evaluate_handle")
            raise AssertionError("JavaScript inesperado")
        self.pulsar.append(arg)
        que, pagina = arg["que"], self

        def pulsar(**k):
            if que in pagina.fallan:
                raise RuntimeError("otro elemento recibiría el clic")
            pagina.clics.append(que)
            pagina.etapa = {"agregar": "abierto", "resultado": "elegido", "cerrar": "cerrado"}[que]
        el = (types.SimpleNamespace(click=pulsar, scroll_into_view_if_needed=lambda **k: None)
              if que in self.pulsables else None)
        return types.SimpleNamespace(as_element=lambda: el)

    def content(self):
        return "<body>shipper sintetico</body>"

    def __getattr__(self, nombre):
        if nombre.startswith("__"):
            raise AttributeError(nombre)
        self.__dict__.setdefault("prohibidos", []).append(nombre)
        raise AttributeError(nombre)


class TestShipperMaersk(ConRegistro):
    """El Shipper de MAERSK por su tarjeta (decisiones de Marcelo, CICLO-maersk-ultimos-puntos.md y
    CICLO-maersk-shipper-y-cortes.md): la única tarjeta de parte a la vista con title="Shipper", que tiene que traer a
    la empresa (MK_EMPRESA, comparada por hash) en el nombre de la parte, en su raíz shadow, como se midió en
    mk_f10_sin_objetivo.html del 27-09. Si no la trae, la elige con dos clics: el «Add» de la tarjeta y, en el buscador
    de partes titulado «Shipper», el único resultado con la empresa, con la lista quieta. Después comprueba que la
    tarjeta la muestre y que el buscador se haya cerrado, y si la muestra y sigue abierto, pulsa su «Close» (encargo
    39); si no, NO ENVIADA con su evidencia, sin otro clic. Hasta el
    encargo 37 la buscaba en el textContent del primer div con «Parties», que no ve las raíces shadow, y pulsaba el
    primer «+ Add» y el último elemento con la empresa; en el encargo 37 cortaba sin pulsar nada."""
    CERRADO = {"n": 1, "empresa": False, "agregar": 1, "resultados": 0, "con_empresa": 0, "titulo": False,
               "abierto": False}
    ABIERTO = {"n": 1, "empresa": False, "agregar": 1, "resultados": 3, "con_empresa": 1, "titulo": True,
               "abierto": True}
    ELEGIDO = {"n": 1, "empresa": True, "agregar": 0, "resultados": 0, "con_empresa": 0, "titulo": False,
               "abierto": False}
    NADA = "no pulsé nada más y la reserva no se envió"

    def shipper(self, pagina):
        """Corre _mk_shipper en una corrida nueva; al terminar la prueba, la página no tiene que haber recibido nada
        prohibido."""
        self.n = getattr(self, "n", 0) + 1
        self.addCleanup(lambda: self.assertEqual(pagina.prohibidos, []))
        reg, vistas, log = self.corrida(f"shipper_{self.n}")
        det = []
        r = self.mod._mk_shipper(pagina, reg, det, 30)
        return r, det, log.read_text(encoding="utf-8"), vistas

    def test_la_empresa_y_el_titulo_son_los_medidos(self):
        self.assertEqual((self.mod.MK_SHIPPER, self.mod.MK_AGREGAR, self.mod.MK_CERRAR), ("Shipper", "Add", "Close"))
        self.assertEqual(hashlib.sha256(self.mod.MK_EMPRESA.encode("utf-8")).hexdigest()[:16], "811b369c26aead3f")
        self.assertEqual((self.mod.MK_ESPERA_SHIPPER, self.mod.MK_ESPERA_BUSCADOR), (5, 10))

    def test_con_la_empresa_no_pulsa_nada(self):
        pagina = PaginaShipper(self.mod, self.ELEGIDO)
        r, det, log, _ = self.shipper(pagina)
        self.assertEqual((r, det, pagina.esperas, pagina.clics, pagina.pulsar),
                         (None, ["shipper=" + self.mod.MK_EMPRESA], 0, [], []))
        self.assertEqual(pagina.args, [({"titulo": "Shipper", "empresa": self.mod.MK_EMPRESA, "agregar": "Add",
                                         "cerrar": "Close"},)])
        self.assertIn(f"Shipper: {self.mod.MK_EMPRESA} ya viene en la tarjeta «Shipper»; no pulsé nada", log)

    def test_espera_la_tarjeta_con_la_empresa(self):
        # Hasta MK_ESPERA_SHIPPER s, por si el portal la llena después (revisión del encargo 37: la leía una sola vez).
        pagina = PaginaShipper(self.mod, [self.CERRADO, RuntimeError("se está dibujando"), self.ELEGIDO])
        r, det, _, _ = self.shipper(pagina)
        self.assertEqual((r, det, pagina.esperas, pagina.clics), (None, ["shipper=" + self.mod.MK_EMPRESA], 2, []))

    def test_sin_una_sola_tarjeta_corta(self):
        casos = (({"n": 0, "empresa": None}, "había 0"), ({"n": 2, "empresa": None}, "había 2"), ({}, "había 0"),
                 ("no es un diccionario", "había 0"),
                 (RuntimeError("la página se cerró"), "no pude leer la página: RuntimeError: la página se cerró"))
        for respuesta, cuantas in casos:
            with self.subTest(respuesta=respuesta):
                pagina = PaginaShipper(self.mod, respuesta)
                with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
                    self.shipper(pagina)
                self.assertEqual((e.exception.paso, e.exception.buscaba, pagina.esperas, pagina.clics),
                                 ("Shipper de MAERSK", f"una sola tarjeta «Shipper» a la vista ({cuantas})", 9, []))

    def test_sin_un_solo_add_corta_sin_pulsar(self):
        # La tarjeta sin la empresa y sin un solo «Add» a la vista (llena con otra, por ejemplo: cambiarla sería otro
        # clic): corta antes de pulsar nada, después de esperarla hasta 5 s.
        for agregar in (0, 2):
            with self.subTest(agregar=agregar):
                pagina = PaginaShipper(self.mod, dict(self.CERRADO, agregar=agregar))
                with self.assertRaises(self.mod.ObjetivoNoEncontrado) as e:
                    self.shipper(pagina)
                self.assertEqual((e.exception.paso, e.exception.buscaba),
                                 ("Shipper de MAERSK", f"a {self.mod.MK_EMPRESA} en la tarjeta «Shipper», ni un solo "
                                                       f"«Add» a la vista en ella para elegirlo (había {agregar})"))
                self.assertEqual((pagina.esperas, pagina.clics, pagina.pulsar), (9, [], []))

    def test_elige_a_la_empresa_con_dos_clics(self):
        pagina = PaginaShipper(self.mod, self.CERRADO, abierto=[self.CERRADO, self.ABIERTO], elegido=self.ELEGIDO)
        r, det, log, _ = self.shipper(pagina)
        self.assertEqual((r, det, pagina.clics), (None, ["shipper=" + self.mod.MK_EMPRESA], ["agregar", "resultado"]))
        # 9 esperas por la tarjeta (5 s), 2 por el buscador (la lista, quieta en dos lecturas) y ninguna al comprobar.
        self.assertEqual(pagina.esperas, 11)
        args = {"titulo": "Shipper", "empresa": self.mod.MK_EMPRESA, "agregar": "Add", "cerrar": "Close"}
        self.assertEqual(pagina.pulsar, [dict(args, que="agregar"), dict(args, que="resultado")])
        self.assertEqual(pagina.capturas, [("mk_f30_buscador.png", False)])
        for linea in ("Shipper: pulsé el «Add» de la tarjeta «Shipper»",
                      f"Shipper: pulsé el resultado con {self.mod.MK_EMPRESA} del buscador",
                      f"Shipper: elegí a {self.mod.MK_EMPRESA} en el buscador, y la tarjeta «Shipper» lo muestra"):
            self.assertIn(linea, log)

    def test_espera_el_resultado_con_la_empresa(self):
        # Los resultados del buscador pueden llegar de a poco: espera hasta 10 s el que trae a la empresa.
        a_medias = dict(self.ABIERTO, resultados=2, con_empresa=0)
        pagina = PaginaShipper(self.mod, self.CERRADO, abierto=[self.CERRADO, a_medias, self.ABIERTO],
                               elegido=self.ELEGIDO)
        r, det, _, _ = self.shipper(pagina)
        self.assertEqual((r, det, pagina.clics, pagina.esperas),
                         (None, ["shipper=" + self.mod.MK_EMPRESA], ["agregar", "resultado"], 12))

    def test_espera_que_la_lista_se_quede_quieta(self):
        # Con la lista a medias, «un solo resultado» puede no serlo: se decide con la lista quieta en dos lecturas
        # (revisión del encargo 38: elegía con el primero que traía a la empresa).
        uno_de_dos = dict(self.ABIERTO, resultados=2, con_empresa=1)
        dos_de_tres = dict(self.ABIERTO, resultados=3, con_empresa=2)
        pagina = PaginaShipper(self.mod, self.CERRADO, abierto=[uno_de_dos, dos_de_tres])
        r, det, _, _ = self.shipper(pagina)
        detalle = (f"MAERSK: pulsé el «Add» de la tarjeta «Shipper», pero en el buscador no hay un solo resultado con "
                   f"{self.mod.MK_EMPRESA} (había 2 de 3); {self.NADA}")
        self.assertEqual((r, det, pagina.clics, pagina.esperas), (("NO ENVIADA", detalle), [], ["agregar"], 11))

    def test_la_lista_quieta_tambien_con_su_titulo(self):
        # El título del buscador también tiene que quedarse quieto: si llega después que los resultados, espera otra
        # lectura antes de decidir.
        sin_titulo = dict(self.ABIERTO, titulo=False)
        pagina = PaginaShipper(self.mod, self.CERRADO, abierto=[sin_titulo, self.ABIERTO], elegido=self.ELEGIDO)
        r, det, _, _ = self.shipper(pagina)
        self.assertEqual((r, det, pagina.clics, pagina.esperas),
                         (None, ["shipper=" + self.mod.MK_EMPRESA], ["agregar", "resultado"], 11))

    def test_si_no_queda_elegido_corta_sin_otro_clic(self):
        e = self.mod.MK_EMPRESA
        add = "pulsé el «Add» de la tarjeta «Shipper», pero"
        res = f"pulsé el resultado con {e} del buscador, pero"
        leer = RuntimeError("la página se cerró")
        # Abierto y sin un solo «Close» a la vista en él: no hay qué pulsar (encargo 39).
        abierto = (f"la tarjeta «Shipper» ya muestra a {e}, pero el buscador siguió abierto y no hay un solo «Close» a "
                   f"la vista en él (había 0)")
        sin_casilla = ("la tarjeta «Shipper» no lo muestra, y no pulsé la casilla del resultado: la casilla que va "
                       "antes del resultado no es la que dan las cifras de su código")
        casos = (
            (dict(abierto=self.CERRADO), f"{add} el buscador de partes no mostró resultados en 10 s", ["agregar"], 28),
            (dict(abierto=leer), f"{add} el buscador de partes no mostró resultados en 10 s (no pude leer la página: "
                                 f"RuntimeError: la página se cerró)", ["agregar"], 28),
            (dict(abierto=dict(self.ABIERTO, titulo=False)), f"{add} el buscador que se abrió no está titulado "
                                                             f"«Shipper»", ["agregar"], 10),
            # Sin un resultado con la empresa, lo espera los 10 s: los resultados pueden llegar de a poco.
            (dict(abierto=dict(self.ABIERTO, con_empresa=0)), f"{add} en el buscador no hay un solo resultado con {e} "
                                                              f"(había 0 de 3)", ["agregar"], 28),
            (dict(abierto=dict(self.ABIERTO, con_empresa=2)), f"{add} en el buscador no hay un solo resultado con {e} "
                                                              f"(había 2 de 3)", ["agregar"], 10),
            # Sin la empresa en la tarjeta, la casilla del resultado, solo si su posición y las cifras de su código
            # apuntan a la misma (encargo 40): por omisión, la página falsa dice que no.
            (dict(abierto=self.ABIERTO, elegido=dict(self.ELEGIDO, empresa=False)), f"{res} {sin_casilla}",
             ["agregar", "resultado"], 19),
            # Sin la empresa en la tarjeta, no pulsa el «Close», aunque el buscador siga abierto con uno a la vista.
            (dict(abierto=self.ABIERTO,
                  elegido=dict(self.ELEGIDO, empresa=False, resultados=3, abierto=True, cerrar=1)),
             f"{res} {sin_casilla}", ["agregar", "resultado"], 19),
            # Sin una sola tarjeta «Shipper», ni la casilla ni el «Close», aunque el buscador siga abierto con uno a la
            # vista (encargo 40: el caso de arriba ya no llega ahí, porque la casilla va antes).
            (dict(abierto=self.ABIERTO,
                  elegido=dict(self.ELEGIDO, n=2, empresa=None, resultados=3, abierto=True, cerrar=1)),
             f"{res} la tarjeta «Shipper» no lo muestra", ["agregar", "resultado"], 19),
            (dict(abierto=self.ABIERTO, elegido=leer),
             f"{res} no pude leer la tarjeta «Shipper» (RuntimeError: la página se cerró)",
             ["agregar", "resultado"], 19),
            (dict(abierto=self.ABIERTO, elegido=dict(self.ELEGIDO, resultados=3, abierto=True)), abierto,
             ["agregar", "resultado"], 19),
            # Abierto en otra vista, sin resultados: su encabezado sigue a la vista (revisión del encargo 38).
            (dict(abierto=self.ABIERTO, elegido=dict(self.ELEGIDO, abierto=True)), abierto,
             ["agregar", "resultado"], 19),
            (dict(pulsables=()), "al volver a leer la página, el «Add» de la tarjeta «Shipper» ya no era uno solo a la "
                                 "vista", [], 9),
            (dict(abierto=self.ABIERTO, pulsables=("agregar",)),
             f"al volver a leer la página, el resultado con {e} del buscador ya no era uno solo a la vista",
             ["agregar"], 10),
            (dict(fallan=("agregar",)),
             "falló el clic en el «Add» de la tarjeta «Shipper» (RuntimeError: otro elemento recibiría el clic)",
             [], 9),
            (dict(abierto=self.ABIERTO, fallan=("resultado",)),
             f"falló el clic en el resultado con {e} del buscador (RuntimeError: otro elemento recibiría el clic)",
             ["agregar"], 10),
        )
        for opciones, que, clics, esperas in casos:
            with self.subTest(que=que, opciones=sorted(opciones)):
                pagina = PaginaShipper(self.mod, self.CERRADO, **opciones)
                r, det, log, vistas = self.shipper(pagina)
                detalle = f"MAERSK: {que}; {self.NADA}"
                self.assertEqual((r, det, pagina.clics, pagina.esperas), (("NO ENVIADA", detalle), [], clics, esperas))
                self.assertEqual(pagina.capturas[-1], ("mk_f30_shipper.png", False))
                for donde in (log, "\n".join(vistas)):                              # log.txt y pantalla
                    self.assertIn(f"· ✗ NO ENVIADA · {detalle}", donde)

    def test_cierra_el_buscador_si_la_tarjeta_ya_lo_muestra(self):
        # Si después del resultado la tarjeta ya muestra a la empresa y el buscador sigue abierto, pulsa su «Close», el
        # único a la vista en él (decisión de Marcelo, CICLO-maersk-cuatro-puntos.md), y comprueba que se cerró y que la
        # tarjeta la sigue mostrando.
        sigue_abierto = dict(self.ELEGIDO, resultados=3, abierto=True, cerrar=1)
        pagina = PaginaShipper(self.mod, self.CERRADO, abierto=self.ABIERTO, elegido=sigue_abierto,
                               cerrado=self.ELEGIDO)
        r, det, log, _ = self.shipper(pagina)
        self.assertEqual((r, det, pagina.clics),
                         (None, ["shipper=" + self.mod.MK_EMPRESA], ["agregar", "resultado", "cerrar"]))
        # 9 esperas por la tarjeta, 1 por el buscador, 9 con él abierto después del resultado y ninguna al cerrarlo.
        self.assertEqual(pagina.esperas, 19)
        args = {"titulo": "Shipper", "empresa": self.mod.MK_EMPRESA, "agregar": "Add", "cerrar": "Close"}
        self.assertEqual(pagina.pulsar[-1], dict(args, que="cerrar"))
        # Antes del «Close», la evidencia de ese estado, que ninguna corrida guardó (revisión del encargo 39).
        self.assertEqual(pagina.capturas, [("mk_f30_buscador.png", False), ("mk_f30_cerrar.png", False)])
        for linea in ("Shipper: pulsé el «Close» del buscador",
                      f"Shipper: elegí a {self.mod.MK_EMPRESA} en el buscador, y la tarjeta «Shipper» lo muestra"):
            self.assertIn(linea, log)

    def test_si_el_close_no_lo_deja_elegido_corta(self):
        # Sin un solo «Close» a la vista, no lo pulsa; después del «Close», si el buscador sigue abierto, si la
        # tarjeta ya no muestra a la empresa o si no se puede leer, corta sin otro clic.
        e = self.mod.MK_EMPRESA
        sigue = dict(self.ELEGIDO, resultados=3, abierto=True, cerrar=1)
        abierto = f"la tarjeta «Shipper» ya muestra a {e}, pero el buscador siguió abierto"
        cerrar = "pulsé el «Close» del buscador, pero"
        tres = ["agregar", "resultado", "cerrar"]
        casos = (
            (dict(elegido=dict(sigue, cerrar=0)), f"{abierto} y no hay un solo «Close» a la vista en él (había 0)",
             ["agregar", "resultado"], 19),
            (dict(elegido=dict(sigue, cerrar=2)), f"{abierto} y no hay un solo «Close» a la vista en él (había 2)",
             ["agregar", "resultado"], 19),
            (dict(elegido=sigue, cerrado=sigue), f"{cerrar} siguió abierto", tres, 28),
            (dict(elegido=sigue, cerrado=dict(self.ELEGIDO, empresa=False)),
             f"{cerrar} la tarjeta «Shipper» ya no muestra a {e}", tres, 28),
            (dict(elegido=sigue, cerrado=RuntimeError("la página se cerró")),
             f"{cerrar} no pude leer la página (RuntimeError: la página se cerró)", tres, 28),
            # Al volver a leer, ya no da el «Close»: el motivo dice las dos razones posibles (revisión del encargo 39).
            (dict(elegido=sigue, pulsables=("agregar", "resultado")),
             f"al volver a leer la página, ya no había un solo «Close» a la vista en el buscador, o la tarjeta "
             f"«Shipper» ya no mostraba a {e}", ["agregar", "resultado"], 19),
            (dict(elegido=sigue, fallan=("cerrar",)),
             "falló el clic en el «Close» del buscador (RuntimeError: otro elemento recibiría el clic)",
             ["agregar", "resultado"], 19),
        )
        for opciones, que, clics, esperas in casos:
            with self.subTest(que=que):
                pagina = PaginaShipper(self.mod, self.CERRADO, abierto=self.ABIERTO, **opciones)
                r, det, log, vistas = self.shipper(pagina)
                detalle = f"MAERSK: {que}; {self.NADA}"
                self.assertEqual((r, det, pagina.clics, pagina.esperas), (("NO ENVIADA", detalle), [], clics, esperas))
                self.assertEqual(pagina.capturas[-1], ("mk_f30_shipper.png", False))
                for donde in (log, "\n".join(vistas)):                              # log.txt y pantalla
                    self.assertIn(f"· ✗ NO ENVIADA · {detalle}", donde)

    SIN_ELEGIR = {"n": 1, "empresa": False, "agregar": 0, "resultados": 3, "con_empresa": 1, "titulo": True,
                  "abierto": True}
    COINCIDEN = {"casilla": "coinciden", "marcada": False}

    def test_si_el_resultado_no_lo_elige_pulsa_su_casilla(self):
        # Si después del resultado la tarjeta no muestra a la empresa, pulsa la casilla de ese resultado, solo si su
        # posición y las cifras de su código apuntan a la misma (decisión de Marcelo, CICLO-maersk-busqueda-vacia.md), y
        # lo vuelve a comprobar; si queda con el buscador abierto, lo cierra con su «Close», como después del resultado.
        e = self.mod.MK_EMPRESA
        sigue = dict(self.ELEGIDO, resultados=3, abierto=True, cerrar=1)
        args = ({"titulo": "Shipper", "empresa": e, "agregar": "Add", "cerrar": "Close"},)
        casos = ((dict(marcado=self.ELEGIDO), ["agregar", "resultado", "casilla"], 19,
                  ["mk_f30_buscador.png", "mk_f30_casilla.png"]),
                 (dict(marcado=sigue, cerrado=self.ELEGIDO), ["agregar", "resultado", "casilla", "cerrar"], 28,
                  ["mk_f30_buscador.png", "mk_f30_casilla.png", "mk_f30_cerrar.png"]))
        for opciones, clics, esperas, capturas in casos:
            with self.subTest(clics=clics):
                pagina = PaginaShipper(self.mod, self.CERRADO, abierto=self.ABIERTO, elegido=self.SIN_ELEGIR,
                                       casilla=self.COINCIDEN, **opciones)
                r, det, log, _ = self.shipper(pagina)
                self.assertEqual((r, det, pagina.clics, pagina.esperas), (None, ["shipper=" + e], clics, esperas))
                self.assertEqual(pagina.capturas, [(c, False) for c in capturas])
                self.assertEqual(pagina.marcar, [("leer", args), ("marcar", args)])
                for linea in (f"Shipper: pulsé la casilla del resultado con {e}; antes del clic, marcada: no",
                              f"Shipper: elegí a {e} en el buscador, y la tarjeta «Shipper» lo muestra"):
                    self.assertIn(linea, log)

    def test_si_al_volver_a_leer_ya_lo_muestra_no_pulsa_la_casilla(self):
        # Si la casilla ya no se da al volver a leer justo antes del clic porque la tarjeta ya muestra a la empresa (el
        # clic en el resultado tardó en verse), sigue sin pulsarla (revisión del encargo 40: cortaba).
        e = self.mod.MK_EMPRESA
        pagina = PaginaShipper(self.mod, self.CERRADO, abierto=self.ABIERTO,
                               elegido=[self.SIN_ELEGIR] * 10 + [self.ELEGIDO], casilla=self.COINCIDEN,
                               pulsables=("agregar", "resultado"))
        r, det, log, _ = self.shipper(pagina)
        self.assertEqual((r, det, pagina.clics, pagina.esperas),
                         (None, ["shipper=" + e], ["agregar", "resultado"], 19))
        self.assertEqual([que for que, _ in pagina.marcar], ["leer", "marcar"])
        for linea in (f"Shipper: la tarjeta «Shipper» ya muestra a {e}; no pulsé la casilla del resultado",
                      f"Shipper: elegí a {e} en el buscador, y la tarjeta «Shipper» lo muestra"):
            self.assertIn(linea, log)

    def test_anota_si_la_casilla_estaba_marcada(self):
        # Antes del clic, si estaba marcada: el HTML guardado no lo dice (el atributo checked no refleja el estado).
        e = self.mod.MK_EMPRESA
        for marcada, dice in ((True, "sí"), (False, "no"), (None, "no pude leerlo")):
            with self.subTest(marcada=marcada):
                pagina = PaginaShipper(self.mod, self.CERRADO, abierto=self.ABIERTO, elegido=self.SIN_ELEGIR,
                                       marcado=self.ELEGIDO, casilla={"casilla": "coinciden", "marcada": marcada})
                r, _, log, _ = self.shipper(pagina)
                self.assertIsNone(r)
                self.assertIn(f"Shipper: pulsé la casilla del resultado con {e}; antes del clic, marcada: {dice}", log)

    def test_si_la_casilla_no_coincide_corta_como_hoy(self):
        # Sin una casilla a la que apunten su posición y las cifras de su código, no la pulsa: corta como hasta el
        # encargo 40, y el motivo dice por qué.
        e = self.mod.MK_EMPRESA
        no_la = (f"pulsé el resultado con {e} del buscador, pero la tarjeta «Shipper» no lo muestra, y no pulsé la "
                 f"casilla del resultado")
        casos = (({"casilla": "titulo"}, "el buscador ya no está titulado «Shipper»"),
                 ({"casilla": "resultado"}, f"no hay un solo resultado con {e} a la vista"),
                 ({"casilla": "posicion"}, "en su contenedor, las casillas y los resultados no van alternados"),
                 ({"casilla": "codigo"}, "la tarjeta del resultado no muestra un solo código con cifras"),
                 ({"casilla": "cifras"}, "no hay una sola casilla cuyo id termine con las cifras de su código"),
                 ({"casilla": "distintas"}, "la casilla que va antes del resultado no es la que dan las cifras de su "
                                            "código"),
                 ({"casilla": "otra cosa"}, "no pude identificarla"), ("no es un diccionario", "no pude identificarla"),
                 (RuntimeError("la página se cerró"), "no pude leer la página (RuntimeError: la página se cerró)"))
        for casilla, razon in casos:
            with self.subTest(casilla=casilla):
                pagina = PaginaShipper(self.mod, self.CERRADO, abierto=self.ABIERTO, elegido=self.SIN_ELEGIR,
                                       casilla=casilla)
                r, det, log, vistas = self.shipper(pagina)
                detalle = f"MAERSK: {no_la}: {razon}; {self.NADA}"
                self.assertEqual((r, det, pagina.clics, pagina.esperas),
                                 (("NO ENVIADA", detalle), [], ["agregar", "resultado"], 19))
                self.assertEqual([que for que, _ in pagina.marcar], ["leer"])
                self.assertEqual(pagina.capturas, [("mk_f30_buscador.png", False), ("mk_f30_shipper.png", False)])
                for donde in (log, "\n".join(vistas)):                              # log.txt y pantalla
                    self.assertIn(f"· ✗ NO ENVIADA · {detalle}", donde)

    def test_si_la_casilla_no_lo_deja_elegido_corta(self):
        # Después de la casilla, si la tarjeta sigue sin la empresa o no se puede leer, corta sin otro clic; y si al
        # volver a leer ya no hay casilla, o su clic falla, no la pulsa.
        e = self.mod.MK_EMPRESA
        y_casilla = f"pulsé el resultado con {e} del buscador y su casilla, pero"
        tres = ["agregar", "resultado", "casilla"]
        casos = ((dict(marcado=self.SIN_ELEGIR), f"{y_casilla} la tarjeta «Shipper» no lo muestra", tres, 28),
                 (dict(marcado=RuntimeError("la página se cerró")),
                  f"{y_casilla} no pude leer la tarjeta «Shipper» (RuntimeError: la página se cerró)", tres, 28),
                 (dict(pulsables=("agregar", "resultado")),
                  f"pulsé el resultado con {e} del buscador, pero la tarjeta «Shipper» no lo muestra, y no pulsé la "
                  f"casilla del resultado: al volver a leer la página, su posición y las cifras de su código ya no "
                  f"apuntaban a la misma, o ya no había una sola tarjeta «Shipper» sin {e}", ["agregar", "resultado"],
                  20),
                 (dict(fallan=("casilla",)),
                  f"falló el clic en la casilla del resultado con {e} (RuntimeError: la página se cerró)",
                  ["agregar", "resultado"], 19))
        for opciones, que, clics, esperas in casos:
            with self.subTest(que=que):
                pagina = PaginaShipper(self.mod, self.CERRADO, abierto=self.ABIERTO, elegido=self.SIN_ELEGIR,
                                       casilla=self.COINCIDEN, **opciones)
                r, det, log, vistas = self.shipper(pagina)
                detalle = f"MAERSK: {que}; {self.NADA}"
                self.assertEqual((r, det, pagina.clics, pagina.esperas), (("NO ENVIADA", detalle), [], clics, esperas))
                self.assertEqual(pagina.capturas[-2:], [("mk_f30_casilla.png", False), ("mk_f30_shipper.png", False)])
                for donde in (log, "\n".join(vistas)):                              # log.txt y pantalla
                    self.assertIn(f"· ✗ NO ENVIADA · {detalle}", donde)

    def test_js_casilla(self):
        # La casilla del resultado con la empresa, como se midió el 27-09: los resultados van sueltos en un mismo
        # contenedor, casilla (input radio, con id) y label alternados, y el id de cada casilla termina con las cifras
        # que muestra el código (party__code) de la tarjeta de su resultado. Se pulsa solo si la que va antes del label
        # y la única cuyo id termina con esas cifras son la misma, y la tarjeta «Shipper» sigue sin la empresa.
        guion = (DOM_AQ + "const leerC = " + self.mod._JS_MK_SHIPPER_CASILLA + ";\nconst marcar = "
                 + self.mod._JS_MK_SHIPPER_MARCAR + ";\nconst EMPRESA = " + json.dumps(self.mod.MK_EMPRESA)
                 + ";\nconst NOMBRE = " + json.dumps(self.mod.MK_EMPRESA.title() + " S.A.") + r""";
const tarjeta = nombre => el('mc-c-party-card', {title: 'Shipper'}, [], {shadow: [el('article', {}, [
  el('header', {}, ['Shipper']), el('p', {class: 'party__info'}, [nombre])])]});
const casilla = (id, dp, opciones = {}, tipo = 'radio') => el('input', {type: tipo, id, name: id, 'data-prueba': dp},
                                                              [], opciones);
const resultado = (nombre, codigo) => el('label', {class: 'party-card__label'}, [el('mc-c-party-card', {}, [],
  {shadow: [el('p', {class: 'party__info'}, [nombre, ' ', el('span', {class: 'party__code'}, [codigo])])]})]);
const buscador = (hijos, titulo = 'Shipper') => el('mc-c-party-finder', {}, [], {shadow: [el('mc-modal', {}, [
  el('span', {slot: 'heading'}, [titulo]), el('div', {class: 'party-search-results'}, hijos)])]});
const a = {titulo: 'Shipper', empresa: EMPRESA, agregar: 'Add', cerrar: 'Close'};
const r = [];
const leer = () => { global.clics = []; const c = leerC(a); r.push([c.casilla, c.marcada, marcar(a), global.clics]); };
const tres = (c2 = {}) => [casilla('px-0123-777', 'c1'), resultado('OTRA S.A.', '****777'),
                           casilla('px-000-0123', 'c2', c2), resultado(NOMBRE, '***-0123'),
                           casilla('px-000-0555', 'c3'), resultado('TERCERA S.A.', '****555')];
// 0. El medido: tres resultados; el de la empresa, el segundo. El id de la primera casilla trae sus cifras, pero no al
// final. 1. La tarjeta ya muestra a la empresa: se lee, pero no se pulsa. 2. Marcada.
pagina(tarjeta(''), buscador(tres()));
leer();
pagina(tarjeta(NOMBRE), buscador(tres()));
leer();
pagina(tarjeta(''), buscador(tres({checked: true})));
leer();
// 3. Algo entre los resultados: ya no van alternados; 4. un código sin cifras.
pagina(tarjeta(''), buscador([casilla('px-000-0777', 'c1'), resultado('OTRA S.A.', '****777'), el('div', {}, []),
                              casilla('px-000-0123', 'c2'), resultado(NOMBRE, '***-0123')]));
leer();
pagina(tarjeta(''), buscador([casilla('px-000-0777', 'c1'), resultado('OTRA S.A.', '****777'),
                              casilla('px-000-0123', 'c2'), resultado(NOMBRE, '*******')]));
leer();
// 5. Dos casillas cuyo id termina con sus cifras; 6. la que las trae no es la que va antes del resultado.
pagina(tarjeta(''), buscador([casilla('py-111-0123', 'c1'), resultado('OTRA S.A.', '****777'),
                              casilla('px-000-0123', 'c2'), resultado(NOMBRE, '***-0123')]));
leer();
pagina(tarjeta(''), buscador([casilla('px-000-0123', 'c1'), resultado('OTRA S.A.', '****777'),
                              casilla('px-000-0999', 'c2'), resultado(NOMBRE, '***-0123')]));
leer();
// 7. El buscador de otra parte; 8. dos resultados con la empresa; 9. una casilla de verificación en lugar de la opción.
pagina(tarjeta(''), buscador(tres(), 'Consignee'));
leer();
pagina(tarjeta(''), buscador([casilla('px-000-0123', 'c1'), resultado(NOMBRE, '***-0123'),
                              casilla('px-000-0555', 'c2'), resultado('SALMONES ' + EMPRESA, '****555')]));
leer();
pagina(tarjeta(''), buscador([casilla('px-000-0777', 'c1'), resultado('OTRA S.A.', '****777'),
                              casilla('px-000-0123', 'c2', {}, 'checkbox'), resultado(NOMBRE, '***-0123')]));
leer();
// 10. Una casilla suelta al final: no van en pares (revisión del encargo 40); 11. dos tarjetas «Shipper»: se lee, pero
// no se pulsa.
pagina(tarjeta(''), buscador([casilla('px-000-0123', 'c1'), resultado(NOMBRE, '***-0123'),
                              casilla('px-000-0555', 'c3')]));
leer();
pagina(tarjeta(''), tarjeta(''), buscador(tres()));
leer();
console.log(JSON.stringify(r));
""")
        self.assertEqual(correr_node(self, guion), [
            ["coinciden", False, True, ["c2"]], ["coinciden", False, False, []], ["coinciden", True, True, ["c2"]],
            ["posicion", None, False, []], ["codigo", None, False, []], ["cifras", None, False, []],
            ["distintas", None, False, []], ["titulo", None, False, []], ["resultado", None, False, []],
            ["posicion", None, False, []], ["posicion", None, False, []], ["coinciden", False, False, []]])

    def test_js_shipper(self):
        # La forma medida el 27-09: cada parte es un mc-c-party-card con su title y el nombre del cliente en su
        # p.party__info, en su raíz shadow; una vacía trae su mc-button «Add» ahí. El buscador (mc-c-party-finder) tiene
        # su título en el slot «heading» y cada resultado es un label con su tarjeta; cerrado, no se ven. Una tarjeta
        # invisible no cuenta, la empresa en otra parte («Booked By») tampoco, ni en la dirección; va como palabra
        # entera.
        guion = (DOM_AQ + "const f = " + self.mod._JS_MK_SHIPPER + ";\nconst p = " + self.mod._JS_MK_SHIPPER_PULSAR
                 + ";\nconst EMPRESA = " + json.dumps(self.mod.MK_EMPRESA) + ";\nconst NOMBRE = "
                 + json.dumps(self.mod.MK_EMPRESA.title() + " S.A.") + r""";
const agregar = (dp, opciones = {}) => el('mc-button', {'data-cy': 'addButton', 'data-prueba': dp}, ['Add'], opciones);
const cuerpo = (nombre, dir) => [el('p', {class: 'party__info'}, [nombre]), el('address', {}, [dir || 'Calle 1'])];
const tarjeta = (titulo, nombre, opciones = {}, boton = null, dir = '') => el('mc-c-party-card', {title: titulo}, [],
  Object.assign({shadow: [el('article', {}, [el('header', {}, boton ? [titulo, boton] : [titulo]),
                                              ...cuerpo(nombre, dir)])]}, opciones));
const resultado = (nombre, dp, visto, dir = '') => el('label', {'data-prueba': dp}, [el('mc-c-party-card', {}, [],
  {shadow: cuerpo(nombre, dir)})], visto ? {} : {invisible: true});
const buscadorCon = (titulo, hijos, visto) => el('mc-c-party-finder', {}, [], {shadow: [el('mc-modal', {}, [
  el('span', {slot: 'heading'}, [el('span', {}, [titulo])], visto ? {} : {invisible: true}), el('div', {}, hijos)])]});
const buscador = (titulo, nombres, visto, extra = []) =>
  buscadorCon(titulo, nombres.map((n, i) => resultado(n, 'r' + i, visto)).concat(extra), visto);
const a = {titulo: 'Shipper', empresa: EMPRESA, agregar: 'Add', cerrar: 'Close'};
const pulsa = que => { const e = p(Object.assign({que}, a)); return e ? e.getAttribute('data-prueba') : null; };
const r = [];
const leer = () => r.push([f(a), pulsa('agregar'), pulsa('resultado'), pulsa('cerrar')]);
// 0. Llena, con el buscador cerrado.
pagina(tarjeta('Booked By', NOMBRE), tarjeta('Shipper', NOMBRE), tarjeta('Shipper', NOMBRE, {invisible: true}),
       buscador('Shipper', [NOMBRE, 'OTRA S.A.'], false));
leer();
// 1. Vacía, con su «Add», y el buscador cerrado; 2. después, abierto.
pagina(tarjeta('Booked By', NOMBRE), tarjeta('Shipper', '', {}, agregar('add')),
       buscador('Shipper', [NOMBRE, 'OTRA S.A.', 'TERCERA S.A.'], false));
leer();
pagina(tarjeta('Booked By', NOMBRE), tarjeta('Shipper', '', {}, agregar('add')),
       buscador('Shipper', ['OTRA S.A.', NOMBRE, 'TERCERA S.A.'], true, [el('label', {}, ['Search by name'])]));
leer();
// 3. Abierto para otra parte; 4. sin la empresa como palabra entera; 5. con dos.
pagina(tarjeta('Shipper', '', {}, agregar('add')), buscador('Consignee', [NOMBRE], true));
leer();
pagina(tarjeta('Shipper', '', {}, agregar('add')),
       buscador('Shipper', [EMPRESA + 'S S.A.', 'SALMONES ' + EMPRESA + 'X', 'EX' + EMPRESA], true));
leer();
pagina(tarjeta('Shipper', '', {}, agregar('add')), buscador('Shipper', [NOMBRE, 'SALMONES ' + EMPRESA], true));
leer();
// 6-8. Sin un solo «Add» a la vista: invisible, dos, u otro texto; 9. sin tarjeta «Shipper».
pagina(tarjeta('Shipper', '', {}, agregar('add', {invisible: true})));
leer();
pagina(tarjeta('Shipper', '', {}, el('div', {}, [agregar('a1'), agregar('a2')])));
leer();
pagina(tarjeta('Shipper', '', {}, el('mc-button', {'data-prueba': 'otro'}, ['Add more'])));
leer();
pagina(tarjeta('Booked By', NOMBRE), buscador('Shipper', [NOMBRE], true));
leer();
// 10. El «Add» de otra parte y un label con tarjeta fuera del buscador no cuentan.
pagina(tarjeta('Consignee', '', {}, agregar('otra')), tarjeta('Shipper', NOMBRE),
       el('label', {}, [el('mc-c-party-card', {}, [], {shadow: cuerpo(NOMBRE)})]));
leer();
// 11. Abierto en otra vista, sin resultados: su encabezado se ve.
pagina(tarjeta('Shipper', '', {}, agregar('add')), buscadorCon('Shipper', [], true));
leer();
// 12. La empresa solo en la dirección, de un resultado y de la tarjeta: no cuenta.
pagina(tarjeta('Shipper', 'OTRA S.A.', {}, null, 'Planta ' + EMPRESA),
       buscadorCon('Shipper', [resultado('OTRA S.A.', 'r0', true, 'Planta ' + EMPRESA)], true));
leer();
// 13. El encabezado es un componente con su título en su propia raíz shadow; el nombre, dentro de otro componente en el
// party__info, o repartido en dos nodos: el texto se lee nodo por nodo y entra en las raíces shadow.
const resultadoCon = (hijos, dp) => el('label', {'data-prueba': dp}, [el('mc-c-party-card', {}, [],
  {shadow: [el('p', {class: 'party__info'}, hijos)]})]);
pagina(tarjeta('Shipper', '', {}, agregar('add')), el('mc-c-party-finder', {}, [], {shadow: [el('mc-modal', {}, [
  el('mc-heading', {slot: 'heading'}, [], {shadow: [el('span', {}, ['Shipper'])]}),
  el('div', {}, [resultadoCon([el('mc-text', {}, [], {shadow: [el('span', {}, [NOMBRE])]})], 'r0'),
                 resultadoCon([el('span', {}, ['SALMONES']), el('span', {}, [EMPRESA])], 'r1')])])]}));
leer();
// 14. La tarjeta ya muestra a la empresa y el buscador sigue abierto, con su «Close» en la cabecera, un botón con otro
// label y «Cancel», que no cuentan; 15. la tarjeta todavía no la muestra: el «Close» se cuenta, pero no se pulsa.
const cerrarBtn = (dp, opciones = {}) => el('mc-button', {class: 'close', label: 'Close', 'data-cy': 'close',
  'data-prueba': dp}, [], opciones);
const buscadorConCerrar = (cerrar, extra = []) => el('mc-c-party-finder', {}, [], {shadow: [el('mc-modal', {}, [
  el('header', {}, [el('span', {slot: 'heading'}, ['Shipper']), ...cerrar]),
  el('div', {}, [resultado(NOMBRE, 'r0', true)]), ...extra])]});
const otros = [el('mc-button', {label: 'Search', 'data-prueba': 'buscar'}, []),
               el('mc-button', {'data-cy': 'cancelButton', slot: 'secondaryAction'}, ['Cancel'])];
pagina(tarjeta('Shipper', NOMBRE), buscadorConCerrar([cerrarBtn('x')], otros));
leer();
pagina(tarjeta('Shipper', '', {}, agregar('add')), buscadorConCerrar([cerrarBtn('x')]));
leer();
// 16. Un «Close» fuera del buscador no cuenta; 17. dos en el buscador; 18. uno invisible.
pagina(tarjeta('Shipper', NOMBRE), el('mc-modal', {}, [cerrarBtn('fuera')]), buscadorConCerrar([]));
leer();
pagina(tarjeta('Shipper', NOMBRE), buscadorConCerrar([cerrarBtn('x1'), cerrarBtn('x2')]));
leer();
pagina(tarjeta('Shipper', NOMBRE), buscadorConCerrar([cerrarBtn('x', {invisible: true})]));
leer();
// 19. Dos tarjetas «Shipper» a la vista, con la empresa, y el buscador abierto con su «Close»: no se pulsa; 20. ninguna
// tarjeta «Shipper» a la vista: tampoco (revisión del encargo 39).
pagina(tarjeta('Shipper', NOMBRE), tarjeta('Shipper', NOMBRE), buscadorConCerrar([cerrarBtn('x')]));
leer();
pagina(tarjeta('Booked By', NOMBRE), buscadorConCerrar([cerrarBtn('x')]));
leer();
console.log(JSON.stringify(r));
""")

        def lectura(n=1, empresa=False, agregar=0, resultados=0, con_empresa=0, titulo=False, abierto=False, cerrar=0):
            return {"n": n, "empresa": empresa, "agregar": agregar, "resultados": resultados,
                    "con_empresa": con_empresa, "titulo": titulo, "abierto": abierto, "cerrar": cerrar}
        self.assertEqual(correr_node(self, guion), [
            [lectura(empresa=True), None, None, None],
            [lectura(agregar=1), "add", None, None],
            [lectura(agregar=1, resultados=3, con_empresa=1, titulo=True, abierto=True), "add", "r1", None],
            [lectura(agregar=1, resultados=1, con_empresa=1, abierto=True), "add", None, None],
            [lectura(agregar=1, resultados=3, titulo=True, abierto=True), "add", None, None],
            [lectura(agregar=1, resultados=2, con_empresa=2, titulo=True, abierto=True), "add", None, None],
            [lectura(), None, None, None],
            [lectura(agregar=2), None, None, None],
            [lectura(), None, None, None],
            [lectura(n=0, empresa=None, resultados=1, con_empresa=1, titulo=True, abierto=True), None, "r0", None],
            [lectura(empresa=True), None, None, None],
            [lectura(agregar=1, titulo=True, abierto=True), "add", None, None],
            [lectura(resultados=1, titulo=True, abierto=True), None, None, None],
            [lectura(agregar=1, resultados=2, con_empresa=2, titulo=True, abierto=True), "add", None, None],
            # 14-18: el «Close» del buscador (encargo 39).
            [lectura(empresa=True, resultados=1, con_empresa=1, titulo=True, abierto=True, cerrar=1), None, "r0", "x"],
            [lectura(agregar=1, resultados=1, con_empresa=1, titulo=True, abierto=True, cerrar=1), "add", "r0", None],
            [lectura(empresa=True, resultados=1, con_empresa=1, titulo=True, abierto=True), None, "r0", None],
            [lectura(empresa=True, resultados=1, con_empresa=1, titulo=True, abierto=True, cerrar=2), None, "r0", None],
            [lectura(empresa=True, resultados=1, con_empresa=1, titulo=True, abierto=True), None, "r0", None],
            [lectura(n=2, empresa=None, resultados=1, con_empresa=1, titulo=True, abierto=True, cerrar=1), None, "r0",
             None],
            [lectura(n=0, empresa=None, resultados=1, con_empresa=1, titulo=True, abierto=True, cerrar=1), None, "r0",
             None],
        ])

    def test_despues_del_shipper_no_pulsa_escape(self):
        # Hasta el encargo 38, después del Shipper pulsaba la tecla Escape para cerrar «cualquier modal residual» (no
        # está medido si con ella se cerraba el buscador de partes). Se quitó (decisión de Marcelo,
        # CICLO-maersk-shipper-y-cortes.md): el cuerpo de reservar_maersk ya no pulsa teclas con page.keyboard, que es
        # lo que mira esta prueba. Sigue escribiendo con type() (el commodity, y en lo que llama, el puerto, el
        # contenedor y la fecha de zarpe), y _mk_fecha cierra su selector con Escape; el Shipper lo vigilan sus pruebas
        # (su página falsa anota el teclado).
        fuente = Path(self.mod.__file__).read_text(encoding="utf-8")
        f = next(n for n in ast.parse(fuente).body if isinstance(n, ast.FunctionDef) and n.name == "reservar_maersk")
        teclas = [ast.unparse(c) for c in ast.walk(f) if isinstance(c, ast.Call) and "keyboard" in ast.unparse(c.func)]
        self.assertEqual(teclas, [])

    def test_reservar_maersk_elige_el_shipper_y_corta(self):
        fuente = Path(self.mod.__file__).read_text(encoding="utf-8")
        f = next(n for n in ast.parse(fuente).body if isinstance(n, ast.FunctionDef) and n.name == "reservar_maersk")
        cuerpos = [n.body for n in ast.walk(f) if isinstance(getattr(n, "body", None), list)]
        cuerpo, i = next((c, i) for c in cuerpos for i, s in enumerate(c)
                         if ast.unparse(s) == "corte = _mk_shipper(page, reg, det, f)")
        self.assertEqual(ast.unparse(cuerpo[i + 1]), "if corte:\n    return corte")
        linea = {n: next(c.lineno for c in ast.walk(f) if isinstance(c, ast.Call) and getattr(c.func, "id", "") == n)
                 for n in ("_mk_referencia_de_retiro", "_mk_shipper", "_mk_pulsar_revision")}
        self.assertLess(linea["_mk_referencia_de_retiro"], linea["_mk_shipper"])
        self.assertLess(linea["_mk_shipper"], linea["_mk_pulsar_revision"])
        # Lo de antes ya no está: el primer div con «Parties», el primer «+ Add» y el último elemento con la empresa.
        for forma in ("parties_sec", "b_add", "loc_aqua"):
            self.assertNotIn(forma, ast.get_source_segment(fuente, f))


class LocBook:
    """Localizador falso de PaginaBook: la lista de tarjetas, la tarjeta i, o el «Book» de esa tarjeta (el mc-button y
    su botón interno: dos elementos, el mismo control). Cada acción queda anotada en la página."""

    def __init__(self, pagina, que, i=None):
        self.pagina, self.que, self.i = pagina, que, i

    def nth(self, j):
        return LocBook(self.pagina, "tarjeta", j) if self.que == "tarjetas" else self

    def scroll_into_view_if_needed(self, **k):
        if self.que != "tarjeta":
            self.pagina.eventos.append(("trae el book", self.i))
            return
        self.pagina.eventos.append(("trae", self.i))
        if self.pagina.falla_traer:
            raise RuntimeError("la tarjeta se movió")
        self.pagina.a_la_vista = True

    def locator(self, sel):
        if self.que != "tarjeta" or sel != "mc-button, button, [role='button']":
            raise AssertionError(f"localizador inesperado: {sel}")
        return LocBook(self.pagina, "book", self.i)

    def filter(self, has_text=None):
        if not (has_text and has_text.search(" Book ") and not has_text.search("Booking")):
            raise AssertionError("filtro inesperado")
        return self

    def count(self):
        return 0 if self.pagina.sin_book else 2

    def is_visible(self):
        return True

    def bounding_box(self):
        self.pagina.eventos.append(("altura", self.i))
        return {"y": self.pagina.despues if self.pagina.a_la_vista else self.pagina.antes}

    def click(self, **k):
        self.pagina.eventos.append(("clic", self.i))
        if self.pagina.falla_clic:
            raise RuntimeError("otro elemento recibiría el clic")


class PaginaBook(soporte.PaginaFalsa):
    """«Select sailing» falsa para _mk_pulsar_book (encargo 46): el «Book» de cada tarjeta está a 'antes' px del
    borde de arriba de la ventana hasta que su tarjeta se trae a la vista, y a 'despues' desde ahí. Con 'falla_traer',
    traer la tarjeta falla; con 'falla_clic', el clic; con 'sin_book', la tarjeta no trae «Book». 'eventos' anota cada
    acción, en orden."""

    def __init__(self, antes=-300, despues=600, falla_traer=False, falla_clic=False, sin_book=False):
        super().__init__()
        self.antes, self.despues, self.falla_traer, self.falla_clic = antes, despues, falla_traer, falla_clic
        self.sin_book, self.a_la_vista, self.eventos = sin_book, False, []

    def locator(self, sel):
        if sel != "mc-card.new-sailings-card":
            raise AssertionError(f"localizador inesperado: {sel}")
        return LocBook(self, "tarjetas")


class LocSailing:
    """Localizador falso de «Select sailing» de MAERSK: la lista de tarjetas, el «Book» de una tarjeta (el mc-button y su
    botón interno: dos elementos, el mismo control), «Search more sailing options» o la espera de los precios."""
    first = property(lambda s: s)

    def __init__(self, pagina, que, i=None):
        self.pagina, self.que, self.i = pagina, que, i

    def filter(self, has_text=None):
        return self

    def nth(self, j):
        return LocSailing(self.pagina, "tarjeta", j) if self.que == "mc-card.new-sailings-card" else self

    def locator(self, sel):
        return LocSailing(self.pagina, "book", self.i)

    def count(self):
        if self.que.startswith("text=/USD"):
            return 1
        if self.que == "book":
            return 2
        if self.que == "mas":           # «Search more sailing options»
            return self.pagina.botones if len(self.pagina.lotes) > 1 else 0
        if self.que == "otro-boton":
            return 0
        return 0

    def is_visible(self):
        return True

    def is_enabled(self):
        return self.pagina.habilitado()

    def bounding_box(self):
        return {"y": self.pagina.altura}

    def scroll_into_view_if_needed(self, **k):
        pass

    def click(self, **k):
        if self.que == "mas":
            self.pagina.lotes.pop(0)
            self.pagina.clics.append(("mas",))
        else:
            self.pagina.clics.append((self.que, self.i))


class PaginaSailing(soporte.PaginaFalsa):
    """«Select sailing» falsa: cada lote es lo que responde _JS_MK_SALIDAS (con «igual», solo si la lectura lo pide,
    como el JavaScript; encargo 43); «Search more sailing options» está a la vista mientras quede otro lote ('botones'
    dice cuántos), sigue deshabilitado las primeras 'cargando' consultas y pasa al lote siguiente. Otro JavaScript
    hace caer la prueba. El «Book» de cada tarjeta está a 'altura' px del borde de arriba de la ventana (encargo 46)."""

    def __init__(self, mod, lotes, cargando=0, botones=1, altura=400):
        super().__init__(texto=self.responder)
        self.mod, self.lotes, self.clics = mod, list(lotes), []
        self.cargando, self.botones, self.consultas, self.altura = cargando, botones, 0, altura

    def habilitado(self):
        self.consultas += 1
        return self.consultas > self.cargando

    def responder(self, js, *a):
        if js != self.mod._JS_MK_SALIDAS:
            raise AssertionError("JavaScript inesperado")
        if a and a[0].get("iguales"):
            return self.lotes[0]
        return [{k: v for k, v in s.items() if k != "igual"} for s in self.lotes[0]]

    def locator(self, sel):
        return LocSailing(self, sel)

    def get_by_role(self, rol, name=None, exact=False):
        """El botón por su nombre accesible: solo «Search more sailing options», exacto."""
        es = rol == "button" and name == "Search more sailing options" and exact
        return LocSailing(self, "mas" if es else "otro-boton")

class PaginaLoginOne(soporte.PaginaFalsa):
    """El login de ONE falso: abrirlo lleva al login (auth.one-line.com), y wait_for_url anota el patrón y lleva a la
    dirección de hoy; con 'vence', la página llega igual, pero la espera vence."""

    def __init__(self, vence):
        super().__init__(url="about:blank")
        self.vence, self.esperas_url = vence, []
        self.goto = self._abrir

    def _abrir(self, url, **k):
        self.url = "https://auth.one-line.com/login?client_id=x"

    def wait_for_url(self, patron, timeout=None):
        self.esperas_url.append((patron, timeout))
        self.url = "https://www.one-line.com/one-ecom/booking/quick-booking?step=search-schedule"
        if self.vence:
            raise TimeoutError("vencida")

class PaginaCmaPortal(soporte.PaginaFalsa):
    """Click & Book de CMA falso: abrirlo anota la dirección, y la página trae ese texto a la vista."""

    def __init__(self, texto):
        super().__init__(texto=texto)
        self.visitas = []
        self.goto = lambda url, **k: self.visitas.append(url)
