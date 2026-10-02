# -*- coding: utf-8 -*-
"""Candado de emisión: fotografía de es_modo_emision(), de sus llamadas y de la
guarda de cada reservador.

Lo que se fotografió (2026-09-23): el candado se abre con CUALQUIERA de las tres
llaves; no hace falta que estén las tres. Con las tres apagadas no se abre en
ninguna de las combinaciones probadas.

Cambio decidido por Marcelo (2026-09-23): la llave de config abre SOLO con el
booleano JSON true. Antes, el texto "false" o el número 1 también abrían; ahora
cualquier valor que no sea true ni false deja el candado cerrado y avisa en
pantalla y en el log.
"""
import io
import ast
import contextlib
import json
import os
import re
import shutil
import sys
import unittest
from pathlib import Path

import sinteticos
import soporte

TESTS = Path(__file__).resolve().parent

# Textos de botón que envían: la misma expresión con que se midió el programa.
ENVIAR = re.compile(r"submit|enviar|send\b|send booking|confirm|place booking|book now|\bbook\b", re.I)
RESERVADORES = ("reservar_one", "reservar_msc", "reservar_cma", "reservar_cosco",
                "reservar_hyundai", "reservar_maersk")


def arbol(mod):
    return ast.parse(Path(mod.__file__).read_text(encoding="utf-8"))


def analizar_guarda(tree, nombre):
    """Guardas del candado dentro del reservador y literales de 'enviar'
    antes y después de la primera guarda."""
    f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == nombre)
    guardas = [n for n in ast.walk(f) if isinstance(n, ast.If) and "es_modo_emision" in ast.unparse(n.test)]
    literales = sorted({(n.lineno, n.value) for n in ast.walk(f)
                        if isinstance(n, ast.Constant) and isinstance(n.value, str) and ENVIAR.search(n.value)})
    g0 = min(g.lineno for g in guardas) if guardas else 10 ** 9
    antes = sorted({" ".join(v.split())[:50] for l, v in literales if l < g0})
    despues = [v for l, v in literales if l > g0]
    return guardas, antes, despues


class TestCandado(soporte.CasoAQ):
    ENTORNO_SI = ("1", "true", "si", "yes", "TRUE", " Yes ", "Si", "1 ")
    ENTORNO_NO = ("0", "false", "no", "", "sí", "on", "2", "emitir", "verdadero")
    ARG_SI = ("emitir", "--emitir", "produccion", "--produccion", "EMITIR", "--Emitir", "PRODUCCION")
    ARG_NO = ("reservas", "auto", "--emitir=1", "emision", "-emitir", "emitir_reservas", "producción", "todas")
    CONFIG_NO = ("false", "sin_clave", "sin_archivo", "invalido", "cero", "vacio")

    @contextlib.contextmanager
    def llaves(self, entorno=None, args=(), config="false"):
        """Enciende llaves solo dentro del bloque y las apaga al salir, pase lo que pase."""
        ruta = self.sb / "config.json"
        original = ruta.read_bytes()
        try:
            if entorno is not None:
                os.environ[soporte.LLAVE_ENTORNO] = entorno
            sys.argv[:] = sys.argv[:1] + list(args)
            cfg = json.loads(original)
            valores = {"true": True, "uno": 1, "texto_false": "false", "false": False, "cero": 0, "vacio": "",
                       "texto_true": "true", "texto_si": "si", "null": None, "lista": [], "objeto": {}}
            if config in valores:
                cfg["opciones"]["emitir_reservas"] = valores[config]
                soporte.escribir_json(ruta, cfg)
            elif config == "sin_clave":
                cfg["opciones"].pop("emitir_reservas", None)
                soporte.escribir_json(ruta, cfg)
            elif config == "sin_archivo":
                ruta.unlink()
            elif config == "invalido":
                ruta.write_text("{esto no es json", encoding="utf-8")
            yield
        finally:
            soporte.apagar_llaves()
            ruta.write_bytes(original)

    def emite(self, **kw):
        with self.llaves(**kw):
            return self.mod.es_modo_emision()

    def test_tres_apagadas_nunca_emite(self):
        combinaciones = 0
        for entorno in (None,) + self.ENTORNO_NO:
            for args in ((),) + tuple((a,) for a in self.ARG_NO):
                for config in self.CONFIG_NO:
                    with self.subTest(entorno=entorno, args=args, config=config):
                        self.assertIs(self.avisos(entorno=entorno, args=args, config=config)[0], False)
                    combinaciones += 1
        self.assertEqual(combinaciones, 10 * 9 * 6)

    def test_llave_entorno_sola_abre(self):
        for v in self.ENTORNO_SI:
            with self.subTest(valor=v):
                self.assertIs(self.emite(entorno=v), True)

    def test_llave_argumento_sola_abre(self):
        for a in self.ARG_SI:
            with self.subTest(argumento=a):
                self.assertIs(self.emite(args=(a,)), True)

    def avisos(self, **kw):
        """(emite, líneas nuevas en el registro del panel, lo que salió por consola)."""
        antes = len(self.mod._WEB["log"])
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            resultado = self.emite(**kw)
        return resultado, self.mod._WEB["log"][antes:], salida.getvalue()

    def test_llave_config_abre_solo_con_true(self):
        emite, panel, consola = self.avisos(config="true")
        self.assertEqual((emite, panel, consola), (True, [], ""))
        for config in ("false", "sin_clave"):              # false o ausente: cerrado y sin aviso
            with self.subTest(config=config):
                self.assertEqual(self.avisos(config=config), (False, [], ""))

    def test_llave_config_con_otro_valor_no_abre_y_avisa(self):
        casos = {"texto_false": '"false"', "texto_true": '"true"', "uno": "1", "cero": "0", "vacio": '""',
                 "texto_si": '"si"', "null": "null", "lista": "[]", "objeto": "{}"}
        for config, como_json in casos.items():
            with self.subTest(config=config):
                emite, panel, consola = self.avisos(config=config)
                self.assertIs(emite, False)
                aviso = (f"⚠ Candado de emisión: en config.json, «emitir_reservas» vale {como_json} y solo se abre "
                         f"con true (sin comillas). Lo dejé cerrado: no se emite ninguna reserva. Si quieres "
                         f"emitir, escribe true; si no, false.")
                self.assertEqual(panel, [aviso])               # en pantalla: el registro del panel web
                self.assertEqual(consola.strip(), aviso)       # y en la consola

    def test_aviso_va_al_log_de_la_corrida(self):
        vistas = []
        reg = self.mod.Registro(self.sb / "corrida" / "log.txt", on_log=vistas.append)
        try:
            emite, panel, _ = self.avisos(config="texto_false")
        finally:
            reg.cerrar()
        self.assertIs(emite, False)
        self.assertEqual(panel, [])                            # va por el Registro de la corrida...
        self.assertEqual(len(vistas), 1)                       # ...a su pantalla (on_log)...
        self.assertIn("· ⚠ Candado de emisión", vistas[0])
        log = (self.sb / "corrida" / "log.txt").read_text(encoding="utf-8")
        self.assertIn('«emitir_reservas» vale "false"', log)   # ...y a su log.txt
        # Con la corrida cerrada, el aviso vuelve al registro del panel.
        self.assertEqual(len(self.avisos(config="texto_false")[1]), 1)

    def test_basta_una_llave_de_tres(self):
        # Tabla de verdad completa: emite si hay AL MENOS una llave (O lógico), no las tres.
        for e in (False, True):
            for a in (False, True):
                for c in (False, True):
                    with self.subTest(entorno=e, argumento=a, config=c):
                        got = self.emite(entorno="1" if e else None, args=("--emitir",) if a else (),
                                         config="true" if c else "false")
                        self.assertIs(got, e or a or c)

    def test_llamadas_al_candado(self):
        tree = arbol(self.mod)
        llamadores = set()
        for nodo in ast.walk(tree):
            if isinstance(nodo, ast.FunctionDef):
                for sub in ast.walk(nodo):
                    if (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name)
                            and sub.func.id == "es_modo_emision"):
                        llamadores.add(nodo.name)
        # Los reservadores y do_GET (dentro de lanzar_web, que lo contiene) consultan el candado.
        self.assertEqual(llamadores, set(RESERVADORES) | {"do_GET", "lanzar_web"})

    # --- Guarda de cada reservador ---
    # Literales tipo 'enviar' que cada reservador tiene ANTES de su guarda (normalizados,
    # 50 caracteres). Si aparece uno nuevo antes de la guarda, la prueba cae.
    ANTES_ESPERADO = {
        "reservar_one": [],
        "reservar_msc": [],
        "reservar_cma": ["CMA-CGM (Click & Book): ruta + cotización, carga r", "cargar Click & Book"],
        "reservar_cosco": ["antes de Submit...", "book\\s+now|no\\s+record|no\\s+service",
                           "booking confirmation sent"],
        # HYUNDAI: pasos intermedios (elegir nave con «Book Now», aceptar el aviso
        # reefer con «Confirm», avanzar a «Review & Book»). Offline no se puede
        # comprobar que ninguno envíe: queda fotografiado, no verificado.
        "reservar_hyundai": ["()=>{ const btns = [...document.querySelectorAll('", "-> Review & Book",
                             "Modal 'Warning (Reefer Undertaking)': Confirmado (", "NEXT - Review & Book",
                             "Paso 5 · Avanzando a Review & Book...", "botón Book Now",
                             "button:has-text('Book Now'), a:has-text('Book Now'",
                             "button:has-text('Confirm'), .btn:has-text('Confirm",
                             "nave elegida y botón Book Now presionado:", "pantalla Review & Book"],
        "reservar_maersk": ["Continue to book", "MAERSK: no se abrió el formulario /book/"],
    }

    def _guarda(self, nombre, retorno):
        tree = arbol(self.mod)
        guardas, antes, despues = analizar_guarda(tree, nombre)
        self.assertEqual(len(guardas), 1, f"{nombre}: se esperaba una sola guarda")
        g = guardas[0]
        self.assertEqual(ast.unparse(g.test), "not es_modo_emision()")
        self.assertIsInstance(g.body[-1], ast.Return, f"{nombre}: la guarda no termina en return")
        self.assertEqual(ast.unparse(g.body[-1].value).split(",")[0], retorno)
        self.assertEqual(antes, sorted(self.ANTES_ESPERADO[nombre]),
                         f"{nombre}: cambió lo que se pulsa antes de la guarda")
        self.assertGreater(len(despues), 0, f"{nombre}: no hay rama de emisión después de la guarda")

    def test_guarda_one(self):
        self._guarda("reservar_one", "('OK-EJEMPLO'")

    def test_guarda_msc(self):
        self._guarda("reservar_msc", "('OK-EJEMPLO'")

    def test_guarda_cma(self):
        self._guarda("reservar_cma", "('OK-EJEMPLO'")

    def test_guarda_cosco(self):
        self._guarda("reservar_cosco", "('OK-EJEMPLO'")

    def test_guarda_hyundai(self):
        self._guarda("reservar_hyundai", "('OK-EJEMPLO'")

    def test_guarda_maersk(self):
        # La guarda de MAERSK devuelve la variable 'estado' ('OK-EJEMPLO' si encontró nave, si no 'REVISAR').
        self._guarda("reservar_maersk", "(estado")
        tree = arbol(self.mod)
        g = analizar_guarda(tree, "reservar_maersk")[0][0]
        asignaciones = [ast.unparse(s) for s in g.body if isinstance(s, ast.Assign)]
        self.assertIn("estado = 'OK-EJEMPLO' if modo else 'REVISAR'", asignaciones)


class TestLanzadores(unittest.TestCase):
    def _hijo(self, codigo, extra=("AQUASHIELD_EMISION.py",)):
        sb = soporte.nueva_sandbox()
        for n in ("AQUASHIELD.py",) + tuple(extra):
            shutil.copyfile(soporte.FUENTES / n, sb / n)
        soporte.escribir_json(sb / "config.json", sinteticos.config())
        pre = (f"import sys; sys.path.insert(0, {str(TESTS)!r}); import soporte; "
               f"sys.path.insert(0, {str(sb)!r}); sys.argv[:] = ['hijo']; import os; ")
        rc, out, err = soporte.hijo([sys.executable, "-c", pre + codigo], cwd=sb)
        self.assertEqual(rc, 0, err[-800:])
        return out.split()

    def test_lanzador_de_emision_abre_el_candado(self):
        out = self._hijo("import AQUASHIELD_EMISION, AQUASHIELD; "
                         "print(AQUASHIELD.es_modo_emision(), os.environ.get('AQUASHIELD_EMITIR'))")
        self.assertEqual(out, ["True", "1"])

    def test_programa_solo_no_abre_el_candado(self):
        out = self._hijo("import AQUASHIELD; "
                         "print(AQUASHIELD.es_modo_emision(), os.environ.get('AQUASHIELD_EMITIR'))", extra=())
        self.assertEqual(out, ["False", "None"])

    def test_bat_seguro_lanza_el_programa(self):
        texto = (soporte.FUENTES / "Iniciar AQUASHIELD.bat").read_text(encoding="utf-8")
        self.assertIn('pythonw "AQUASHIELD.py"', texto)
        self.assertNotIn("AQUASHIELD_EMISION", texto)

    def test_bat_emision_lanza_el_lanzador_de_emision(self):
        texto = (soporte.FUENTES / "Iniciar AQUASHIELD_EMISION.bat").read_text(encoding="utf-8")
        self.assertIn('pythonw "AQUASHIELD_EMISION.py"', texto)


if __name__ == "__main__":
    unittest.main()
