# -*- coding: utf-8 -*-
"""La sonda de secretos (tests/sonda_secretos.py) bloquea el commit si lo que va al staging trae el nombre o el apellido
del operador; hasta 0e15b8a solo lo informaba (decisión de Marcelo, CICLO-cola-siete-items.md). Con configuraciones y
blobs sintéticos, y un git falso: la prueba no lee config.json ni el repo."""
import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import soporte

# El operador sintético de estas pruebas: la clave es el nombre, la descripción trae nombre y apellido, y COSCO lo
# muestra con la inicial y otro apellido, como en la forma medida de config.json.
OPERADOR = {"descripcion": "Filomena Núñez de la Torre", "cosco": {"nombre_en_pantalla": "F. ARRIAGADA"},
            "one": {"usuario": "filo.prueba", "clave": "Clave-Sintetica-1"}}
PLANTILLA = {"descripcion": "Operador 2 (rellenar)", "cosco": {"nombre_en_pantalla": ""},
             "one": {"usuario": "", "clave": ""}}
PROGRAMA = b"def cargar_config():\n    pass\n"


def cargar_sonda():
    # De la copia de las fuentes si la trae (el censo deja ahí la sonda mutada); si no, del repo.
    ruta = soporte.FUENTES / "tests" / "sonda_secretos.py"
    ruta = ruta if ruta.exists() else soporte.RAIZ / "tests" / "sonda_secretos.py"
    spec = importlib.util.spec_from_file_location("sonda_prueba", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestSondaNombre(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sonda = cargar_sonda()

    def test_los_terminos_salen_de_la_clave_la_descripcion_y_cosco(self):
        f = self.sonda.nombres_del_operador
        self.assertEqual(f({"usuarios": {"Filomena": OPERADOR, "usuario2": PLANTILLA}}),
                         (["arriagada", "filomena", "nunez", "torre"], 3))          # «de», «la» y «F»
        # La plantilla no cuenta: ni la clave usuario<n> ni la descripción «por rellenar».
        self.assertEqual(f({"usuarios": {"usuario1": {"descripcion": "Operador 1 (rellenar)"}}}), ([], 0))
        self.assertEqual(f({"usuarios": {"usuario1": {"descripcion": "Ramona Quispe"}}}), (["quispe", "ramona"], 0))
        self.assertEqual(f({"usuarios": {"Ramona": {"descripcion": "Operador 1 (rellenar)"}}}), (["ramona"], 0))
        self.assertEqual(f({}), ([], 0))

    def test_encuentra_el_nombre_sin_mayusculas_ni_tildes(self):
        entradas = [("NOTAS.md", "Lo pidió FILOMENA.".encode("utf-8")),
                    ("a.md", "Sra. Núñez".encode("utf-8")),
                    ("b.txt", "sra. NUNEZ".encode("utf-16-le")),
                    ("logs/web_todas_filomena_20260925/log.txt", b""),
                    ("limpio.md", "Lo decidió operaciones.".encode("utf-8"))]
        self.assertEqual(self.sonda.con_nombre(entradas, ["filomena", "nunez"]),
                         ["NOTAS.md", "a.md", "b.txt", "logs/web_todas_filomena_20260925/log.txt"])
        self.assertEqual(self.sonda.con_nombre(entradas, []), [])

    def test_el_nombre_bloquea_salvo_en_el_almacen(self):
        f = self.sonda.codigo_de_salida
        for modo in ("--staging", "--dry-run", "--negativo-nombre"):
            self.assertEqual(f(modo, [], [], ["NOTAS.md"]), 1, modo)
        # El historial hasta 9710ae2 trae el nombre y no se reescribió: en el almacén solo informa.
        self.assertEqual(f("--almacen", [], [], ["NOTAS.md"]), 0)
        self.assertEqual(f("--almacen", [("x", ["op1/one:clave"])], [], []), 1)
        self.assertEqual(f("--staging", [], ["config.json"], []), 1)
        self.assertEqual(f("--staging", [], [], []), 0)


class TestSondaDeUnaPunta(unittest.TestCase):
    """main() entera, con config.json sintético en una carpeta temporal y el índice de git falso."""

    def setUp(self):
        self.sonda = cargar_sonda()
        self.dir = tempfile.TemporaryDirectory()
        self.raiz = Path(self.dir.name)
        (self.raiz / "config.example.json").write_text(json.dumps({"usuarios": {"usuario2": PLANTILLA}}),
                                                       encoding="utf-8")
        self.config({"Filomena": OPERADOR, "usuario2": PLANTILLA})

    def tearDown(self):
        self.dir.cleanup()

    def config(self, usuarios):
        (self.raiz / "config.json").write_text(json.dumps({"usuarios": usuarios}, ensure_ascii=False),
                                               encoding="utf-8")

    def correr(self, blobs, modo=None):
        indice = b"".join(f"100644 {i:040x} 0\t{ruta}\0".encode("utf-8") for i, ruta in enumerate(blobs))
        contenido = {f"{i:040x}": b for i, b in enumerate(blobs.values())}

        def git(*args):
            if args[:2] == ("ls-files", "-s"):
                return SimpleNamespace(stdout=indice)
            if args[:2] == ("cat-file", "blob"):
                return SimpleNamespace(stdout=contenido[args[2]])
            raise AssertionError(f"git inesperado: {args}")
        salida = io.StringIO()
        with mock.patch.object(self.sonda, "RAIZ", self.raiz), mock.patch.object(self.sonda, "git", git), \
                mock.patch.object(sys, "argv", ["sonda_secretos.py"] + ([modo] if modo else [])), \
                contextlib.redirect_stdout(salida), self.assertRaises(SystemExit) as fin:
            self.sonda.main()
        texto = salida.getvalue()
        for termino in ("filomena", "núñez", "nunez", "arriagada"):          # la salida nunca trae el nombre
            self.assertNotIn(termino, texto.casefold())
        return fin.exception.code, texto

    def test_bloquea_el_nombre_en_el_contenido(self):
        codigo, texto = self.correr({"AQUASHIELD.py": PROGRAMA, "NOTAS.md": "Lo pidió la Sra. NÚÑEZ.".encode("utf-8")})
        self.assertEqual(codigo, 1)
        self.assertIn("entradas con el nombre o el apellido del operador: 1 ['NOTAS.md']", texto)
        self.assertIn("C2 ok: 4 términos del nombre del operador desde config.json", texto)

    def test_bloquea_el_nombre_en_la_ruta_sin_mostrarla(self):
        codigo, texto = self.correr({"AQUASHIELD.py": PROGRAMA, "notas_de_filomena.md": b"nada"})
        self.assertEqual(codigo, 1)
        self.assertIn("entradas con el nombre o el apellido del operador: 1 ['(ruta con el nombre del operador)']",
                      texto)

    def test_deja_pasar_el_staging_limpio(self):
        codigo, texto = self.correr({"AQUASHIELD.py": PROGRAMA, "NOTAS.md": "Lo decidió operaciones.".encode("utf-8")})
        self.assertEqual(codigo, 0)
        self.assertIn("entradas con el nombre o el apellido del operador: 0 []", texto)

    def test_el_negativo_del_nombre_da_uno(self):
        codigo, texto = self.correr({"AQUASHIELD.py": PROGRAMA}, "--negativo-nombre")
        self.assertEqual(codigo, 1)
        self.assertIn("entradas con el nombre o el apellido del operador: 4 ['NEGATIVO/nombre_1.txt', "
                      "'NEGATIVO/nombre_2.txt', 'NEGATIVO/nombre_3.txt', 'NEGATIVO/nombre_4.txt']", texto)

    def test_bloquea_un_contrato_sin_mostrarlo(self):
        operador = dict(OPERADOR, one=dict(OPERADOR["one"], contrato="CT-SINTETICO-9"))
        self.config({"Filomena": operador, "usuario2": PLANTILLA})
        codigo, texto = self.correr({"AQUASHIELD.py": PROGRAMA, "NOTAS.md": b"usa el CT-SINTETICO-9"})
        self.assertEqual(codigo, 1)
        self.assertIn("entradas con contratos o datos de la cuenta: 1 ['NOTAS.md']", texto)
        self.assertNotIn("CT-SINTETICO-9", texto)

    def test_aborta_si_config_no_sabe_el_nombre(self):
        # Control positivo (C2): sin un nombre que buscar, la sonda no audita; aborta con 2.
        self.config({"usuario1": {"descripcion": "Operador 1 (rellenar)", "one": OPERADOR["one"]}})
        codigo, texto = self.correr({"AQUASHIELD.py": PROGRAMA})
        self.assertEqual(codigo, 2)
        self.assertIn("ABORTA C2: config.json da 0 términos del nombre del operador", texto)


class TestSondaCuenta(unittest.TestCase):
    """Desde la revisión del encargo 44, la sonda bloquea también los contratos y el código de Shipper de HYUNDAI de
    config.json, y los generadores de material. En el almacén, los datos de la cuenta solo informan: el historial
    anterior los trae (CICLO-publicar-el-repo.md)."""

    def setUp(self):
        self.sonda = cargar_sonda()

    def test_los_datos_de_la_cuenta_salen_de_config(self):
        cfg = {"usuarios": {"Filomena": {"descripcion": "x",
                                         "one": {"usuario": "u", "contrato": "CT-PRUEBA-1", "contrato_usa": "CT-USA-1",
                                                 "contrato_otros": "x"}}},
               "opciones": {"contratos_por_defecto": {"msc": "CT-DEF-MSC", "hyundai": ""},
                            "codigo_shipper_hyundai": "SHIP0001"}}
        self.assertEqual(self.sonda.datos_de_cuenta(cfg),
                         ([("op1/one", "contrato", "CT-PRUEBA-1"), ("op1/one", "contrato_usa", "CT-USA-1"),
                           ("opciones/contratos_por_defecto", "msc", "CT-DEF-MSC"),
                           ("opciones", "codigo_shipper_hyundai", "SHIP0001")], 1))
        self.assertEqual(self.sonda.datos_de_cuenta({}), ([], 0))

    def test_la_cuenta_bloquea_salvo_en_el_almacen(self):
        f = self.sonda.codigo_de_salida
        cuenta = [("NOTAS.md", ["op1/one:contrato"])]
        for modo in ("--staging", "--dry-run"):
            self.assertEqual(f(modo, [], [], [], cuenta), 1, modo)
        self.assertEqual(f("--almacen", [], [], [], cuenta), 0)

    def test_los_generadores_no_entran(self):
        for ruta in ("crear_simulador_html.py", "crear_video_tutorial.py", "generar_manuales.py"):
            self.assertTrue(self.sonda.prohibida(ruta), ruta)
        self.assertFalse(self.sonda.prohibida("tests/test_web.py"))


class TestSondaImagenes(unittest.TestCase):
    """Desde el encargo 44 no entra ninguna imagen: el logo de la empresa, la única permitida hasta entonces, quedó
    fuera del repo (CICLO-publicar-el-repo.md)."""

    def test_ninguna_imagen_entra(self):
        sonda = cargar_sonda()
        self.assertEqual(sonda.IMAGENES_PERMITIDAS, set())
        for ruta in ("logo_aquachile_dark.png", "material/otra.JPG"):
            self.assertTrue(sonda.prohibida(ruta), ruta)
        self.assertFalse(sonda.prohibida("AQUASHIELD.py"))


if __name__ == "__main__":
    unittest.main()
