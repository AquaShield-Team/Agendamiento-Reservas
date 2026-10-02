# -*- coding: utf-8 -*-
"""Registro de navieras: que cada una esté en todos los lugares donde el
programa la busca (NAVIERAS, RESERVADORES, HOJA_ALIAS, la secuencia del
worker web) y cómo se traduce una hoja o un texto a su clave.
Rareza fotografiada: _match_nav_key busca «one» ANTES que las demás, así que
cualquier texto que lo contenga (ej. «MSC ONE») se asigna a ONE."""
import ast
import unittest
from pathlib import Path

import soporte

CLAVES = ["one", "msc", "cma", "cosco", "hyundai", "maersk"]


class TestRegistro(soporte.CasoAQ):
    def test_navieras_y_reservadores(self):
        self.assertEqual(list(self.mod.NAVIERAS), CLAVES)
        self.assertEqual(list(self.mod.RESERVADORES), CLAVES)
        self.assertEqual([v[0] for v in self.mod.NAVIERAS.values()],
                         ["ONE", "MSC", "CMA-CGM", "COSCO", "HYUNDAI", "MAERSK"])
        for k in CLAVES:
            self.assertEqual(self.mod.RESERVADORES[k].__name__, f"reservar_{k}")
            self.assertEqual(self.mod.NAVIERAS[k][1].__name__, f"login_{k}")

    def test_secuencia_del_worker_web(self):
        tree = ast.parse(Path(self.mod.__file__).read_text(encoding="utf-8"))
        f = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_web_worker")
        asign = [n for n in ast.walk(f) if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == "navs_secuencia" for t in n.targets)]
        literales = [ast.literal_eval(a.value) for a in asign if isinstance(a.value, ast.List)
                     and all(isinstance(e, ast.Constant) for e in a.value.elts)]
        self.assertEqual(literales, [CLAVES])      # la otra asignación es [nav_obj], una sola naviera

    def test_hoja_a_naviera(self):
        f = self.mod._nav_de_hoja
        casos = {"ONE": "one", " one ": "one", "MSC": "msc", "CMA-CGM": "cma", "CMA CGM": "cma", "cma": "cma",
                 "COSCO": "cosco", "HYUNDAI": "hyundai", "HMM": "hyundai", "MAERSK": "maersk",
                 "CONSOLIDADO": "todas", "Todas": "todas", "general": "todas", "OTRA": None, "": None}
        for hoja, esperado in casos.items():
            with self.subTest(hoja=hoja):
                self.assertEqual(f(hoja), esperado)
        self.assertEqual(self.mod.HOJA, {"one": "ONE", "msc": "MSC", "cma": "CMA-CGM", "cosco": "COSCO",
                                         "hyundai": "HYUNDAI", "hmm": "HYUNDAI", "maersk": "MAERSK"})

    def test_texto_a_naviera(self):
        f = self.mod._match_nav_key
        casos = {"ONE": "one", "MSC": "msc", "CMA CGM": "cma", "COSCO": "cosco", "HMM": "hyundai",
                 "Hyundai Merchant": "hyundai", "Maersk Line": "maersk", "OTRA LINEA": None, "": None, None: None,
                 "MSC ONE": "one"}
        for texto, esperado in casos.items():
            with self.subTest(texto=texto):
                self.assertEqual(f(texto), esperado)


if __name__ == "__main__":
    unittest.main()
