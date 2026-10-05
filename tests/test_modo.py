# -*- coding: utf-8 -*-
"""El modo de cada corrida (decisión de Marcelo, encargo 51, CICLO-modo-y-lanzadores.md).

es_modo_emision sale de _llaves_abiertas: la misma regla con que cada corrida dice al empezar, en su log.txt y en su
pantalla, con qué candado corre y por cuál llave (_anotar_candado). test_candado fotografía el candado y no cambia;
esta red vigila que la línea de cada corrida diga lo mismo que el candado. Las llaves se encienden solo dentro de cada
caso y se apagan al salir, como en test_candado; CasoAQ exige que empiecen y terminen apagadas."""
import ast
import contextlib
import io
import json
import os
import re
import sys
import unittest
from pathlib import Path
from unittest import mock

import soporte

ENTORNO = (None, "1", " Yes ", "0")
ARGUMENTOS = ((), ("--emitir",), ("PRODUCCION", "emitir"), ("reservas",))
CONFIG = (False, True, "true", "sin_clave")


class TestModoDeCadaCorrida(soporte.CasoAQ):
    @contextlib.contextmanager
    def llaves(self, entorno=None, args=(), config=False):
        """Enciende las llaves pedidas solo dentro del bloque y las apaga al salir, pase lo que pase."""
        ruta = self.sb / "config.json"
        original = ruta.read_bytes()
        try:
            if entorno is not None:
                os.environ[soporte.LLAVE_ENTORNO] = entorno
            sys.argv[:] = sys.argv[:1] + list(args)
            cfg = json.loads(original)
            if config == "sin_clave":
                cfg["opciones"].pop("emitir_reservas", None)
            else:
                cfg["opciones"]["emitir_reservas"] = config
            soporte.escribir_json(ruta, cfg)
            yield
        finally:
            soporte.apagar_llaves()
            ruta.write_bytes(original)

    @staticmethod
    def esperadas(entorno, args, config):
        """Las llaves que tienen que salir dichas, en el orden en que las mira el candado."""
        dichas = []
        if entorno is not None and entorno.strip().lower() in ("1", "true", "si", "yes"):
            dichas.append(f"la variable AQUASHIELD_EMITIR={entorno.strip()} (la que pone el lanzador de emisión, "
                          f"AQUASHIELD_EMISION.py)")
        abre = [a for a in args if a.lower() in soporte.ARGUMENTOS_EMISION]
        if abre:
            dichas.append(f"el argumento «{abre[0]}» del programa")
        if config is True:
            dichas.append("config.json → opciones → emitir_reservas: true")
        return dichas

    def test_el_candado_sale_de_las_llaves(self):
        # Una sola regla: es_modo_emision no mira las llaves por su cuenta, solo dice si _llaves_abiertas encontró una
        # (fuente única, encargo 51). Si alguien le agrega una llave sin pasar por _llaves_abiertas, cae.
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "es_modo_emision")
        cuerpo = [ast.unparse(s) for s in f.body
                  if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
        self.assertEqual(cuerpo, ["return bool(_llaves_abiertas())"])

    def test_cada_llave_dicha_y_el_mismo_candado(self):
        # Con todas (lo que anota cada corrida), las llaves abiertas, cada una dicha, en el orden en que las mira el
        # candado; y el candado, abierto si y solo si hay una. 4 × 4 × 4 combinaciones de las tres llaves.
        casos = 0
        for entorno in ENTORNO:
            for args in ARGUMENTOS:
                for config in CONFIG:
                    with self.subTest(entorno=entorno, args=args, config=config):
                        with self.llaves(entorno, args, config), contextlib.redirect_stdout(io.StringIO()):
                            dichas = self.mod._llaves_abiertas(todas=True)
                            emite = self.mod.es_modo_emision()
                        esperadas = self.esperadas(entorno, args, config)
                        self.assertEqual(dichas, esperadas)
                        self.assertIs(emite, bool(esperadas))
                    casos += 1
        self.assertEqual(casos, len(ENTORNO) * len(ARGUMENTOS) * len(CONFIG))

    def test_sin_todas_se_detiene_en_la_primera(self):
        # El candado se detiene en la primera llave abierta, como siempre: con la variable o con un argumento abiertos,
        # no lee config.json ni avisa de su valor inválido. Con todas (al empezar cada corrida), lee config.json, pero
        # de su valor inválido avisa solo si ninguna otra llave abrió el candado, como el candado: su aviso dice que
        # el candado quedó cerrado (revisión del encargo 51: el log decía «no se emite ninguna reserva» y, debajo,
        # «modo EMISIÓN»).
        real, lecturas = self.mod.cargar_config, []

        def contar():
            lecturas.append(1)
            return real()
        for entorno, args in (("1", ()), (None, ("--emitir",))):
            with self.subTest(entorno=entorno, args=args):
                antes, salida = len(self.mod._WEB["log"]), io.StringIO()
                with self.llaves(entorno, args, "true"), contextlib.redirect_stdout(salida), \
                        mock.patch.object(self.mod, "cargar_config", contar):
                    lecturas.clear()
                    self.assertIs(self.mod.es_modo_emision(), True)
                    self.assertEqual(self.mod._llaves_abiertas(), self.esperadas(entorno, args, False))
                    sin_todas = len(lecturas)
                    todas = self.mod._llaves_abiertas(todas=True)
                    con_todas = len(lecturas) - sin_todas
                self.assertEqual((sin_todas, con_todas), (0, 1))
                self.assertEqual(todas, self.esperadas(entorno, args, False))
                self.assertEqual((self.mod._WEB["log"][antes:], salida.getvalue()), ([], ""))
        # Sin otra llave abierta, el valor inválido avisa con o sin todas: una vez por llamada.
        antes = len(self.mod._WEB["log"])
        with self.llaves(None, (), "true"), contextlib.redirect_stdout(io.StringIO()):
            self.assertIs(self.mod.es_modo_emision(), False)
            self.assertEqual(self.mod._llaves_abiertas(todas=True), [])
        nuevas = self.mod._WEB["log"][antes:]
        self.assertEqual(len(nuevas), 2)
        self.assertTrue(all('«emitir_reservas» vale "true" y solo se abre con true' in ln for ln in nuevas), nuevas)

    def test_la_linea_de_cada_modo(self):
        # Lo que dice cada corrida al empezar (_anotar_candado): modo prueba, sin llaves; o modo EMISIÓN, y por
        # cuáles, en el orden en que las mira el candado. Las llaves las da _llaves_abiertas, mirándolas todas.
        reg = self.mod.Registro(self.sb / "modo" / "log.txt")
        try:
            for llaves in ([], ["la primera"], ["la primera", "la segunda"]):
                abiertas = (lambda todas=False, dadas=llaves: list(dadas) if todas else [])
                with mock.patch.object(self.mod, "_llaves_abiertas", abiertas):
                    self.mod._anotar_candado(reg)
        finally:
            reg.cerrar()
        lineas = [re.sub(r"^\[[^\]]*\] ", "", ln)
                  for ln in (self.sb / "modo" / "log.txt").read_text(encoding="utf-8").splitlines()]
        fin = "Cada reserva que llegue al botón final se envía a la naviera."
        self.assertEqual(lineas, [
            "· 🛡️ Candado de emisión cerrado: modo prueba, sin ninguna de sus tres llaves abierta (la variable "
            "AQUASHIELD_EMITIR, un argumento emitir o produccion, y emitir_reservas en config.json). Cada reserva se "
            "detiene antes del botón final, sin emitir.",
            f"· 🔴 Candado de emisión abierto: modo EMISIÓN, por la primera. {fin}",
            f"· 🔴 Candado de emisión abierto: modo EMISIÓN, por la primera y la segunda. {fin}"])


if __name__ == "__main__":
    unittest.main()
