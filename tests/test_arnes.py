# -*- coding: utf-8 -*-
"""El arnés mismo: importar el programa no tiene efectos y todo lo que el
programa escribe cae dentro de la sandbox. Si estas pruebas fallan, el resto de
la red no vale."""
import threading
import unittest
from pathlib import Path

import soporte
from soporte import DISPAROS


class TestArnes(unittest.TestCase):
    def setUp(self):
        DISPAROS.clear()

    def tearDown(self):
        DISPAROS.clear()
        soporte.apagar_llaves()

    def test_importar_no_dispara_efectos(self):
        antes = set(threading.enumerate())
        try:
            mod, sb = soporte.cargar()
        except soporte.EfectoReal as e:
            self.fail(f"importar el programa disparó un efecto real: {e}")
        nuevos = [t.name for t in threading.enumerate() if t not in antes and t.is_alive()]
        self.assertEqual(DISPAROS, [])
        self.assertEqual(nuevos, [], "importar el programa lanzó hilos")
        creados = sorted(p.name for p in sb.iterdir() if p.name != "__pycache__")
        self.assertEqual(creados, ["AQUASHIELD.py", "config.json"], "importar el programa escribió archivos")

    def test_rutas_de_trabajo_dentro_de_la_sandbox(self):
        mod, sb = soporte.cargar()
        raiz = sb.resolve()
        for nombre in ("BASE", "PERFILES", "LOGS"):
            ruta = Path(getattr(mod, nombre)).resolve()
            self.assertTrue(ruta == raiz or raiz in ruta.parents, f"{nombre} fuera de la sandbox: {ruta}")
        self.assertEqual(mod.encontrar_archivo_reservas().resolve().parent, raiz)

    def test_candado_cerrado_al_cargar(self):
        mod, _ = soporte.cargar()
        self.assertEqual(soporte.llaves_encendidas(mod), [])
        self.assertIs(mod.es_modo_emision(), False)

    def test_candado_cerrado_sin_config(self):
        mod, sb = soporte.cargar(config=None)
        self.assertFalse((sb / "config.json").exists())
        self.assertIs(mod.es_modo_emision(), False)


if __name__ == "__main__":
    unittest.main()
