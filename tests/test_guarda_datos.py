# -*- coding: utf-8 -*-
"""La guarda de datos reales (tests/guarda_datos.py; encargo 72, CICLO-guarda-de-datos.md): lo que entra al repo, que
es público, no trae razones sociales ni datos con la forma de un dato real, y el hook pre-commit lo frena.

La guarda se carga de soporte.FUENTES si el censo dejó ahí su copia mutada; si no, del repo. git corre de verdad: sobre
repos inventados en el temporal de antes de las pruebas, y sobre este repo solo para leer (ls-files, diff, cat-file).
Los valores inventados van armados por partes: escritos enteros, la guarda los encontraría en este archivo."""
import importlib.util
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

import soporte

IDENTIDAD = ["-c", "user.name=Prueba Inventada", "-c", "user.email=prueba@ejemplo.invalid", "-c",
             "core.autocrlf=false", "-c", "init.defaultBranch=main"]


def desde_fuentes(rel):
    """El archivo de la copia del censo, si la trae; si no, el del repo."""
    ruta = soporte.FUENTES / rel
    return ruta if ruta.exists() else soporte.RAIZ / rel


def cargar_guarda():
    spec = importlib.util.spec_from_file_location("guarda_prueba", desde_fuentes("tests/guarda_datos.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.POPEN = soporte._POPEN            # el arnés pone una trampa en subprocess.Popen
    return mod


def carpeta_corta(prefijo):
    """Una carpeta nueva en el temporal de antes de las pruebas: git de Windows no escribe un objeto en una ruta de más
    de 260 caracteres (test_actualizar, encargo 60)."""
    return Path(tempfile.mkdtemp(prefix=prefijo, dir=soporte.TMP_ORIGINAL))


def borrar(carpeta):
    """git deja sus .pack de solo lectura, y Windows no borra un archivo de solo lectura."""
    def de_nuevo(funcion, ruta, *_):
        os.chmod(ruta, 0o666)
        funcion(ruta)
    shutil.rmtree(carpeta, onexc=de_nuevo)


def razon_inventada():
    return "Pesquera Inventada " + "S" + chr(46) + "A" + chr(46)


def reserva_inventada():
    return "SCLG" + "2794" + "6031"


class TestDetector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = cargar_guarda()

    def test_cada_muestra_da_lo_suyo(self):
        # Una muestra de cada tipo, de cada excepción declarada y de lo que no es nada: el control positivo, que el hook
        # y la suite corren antes de mirar. Falla cerrada: un nombre ajeno delante del propio, o el propio en una frase
        # que empieza con mayúscula, frenan.
        self.assertEqual(self.g.control_detector(), [])
        self.assertGreaterEqual(len(self.g.muestras()), 40)

    def test_la_lista_de_permitidos_esta_fija(self):
        # La propia empresa como el programa la escribe en el formulario de COSCO, el dueño como lo trae el pie del panel
        # y como autor de los commits, y su correo noreply: nada más. Un nombre de cliente no entra a la lista.
        p = self.g.PERMITIDOS
        self.assertEqual([t for t, _, _ in p], ["razón social", "nombre y apellido", "nombre y apellido", "correo"])
        programa = desde_fuentes("AQUASHIELD.py").read_bytes().decode("utf-8")
        shipper = re.findall(r'^COSCO_SHIPPER = "([^"]+)"$', programa, re.M)
        self.assertEqual(shipper, [p[0][1]])
        pie = re.findall(r"AquaShield · ([^<]+)</span>", programa)
        self.assertEqual([x.strip() for x in pie], [p[2][1]])
        autor = f"`{p[1][1]} <{p[3][1]}>`"
        self.assertIn(autor, desde_fuentes("CLAUDE.md").read_bytes().decode("utf-8"))

    def test_nunca_muestra_el_valor(self):
        # El informe dice el tipo, el archivo y la línea (de una razón social, su forma): nunca el valor, tampoco el que
        # trae el nombre de un archivo.
        c = self.g.Cuenta()
        nombre = "notas " + reserva_inventada() + ".md"
        self.g.revisar_texto(nombre, nombre + " (nombre)", c)
        self.g.revisar_texto("Lo pidió " + razon_inventada() + " y su reserva " + reserva_inventada(), "a.md", c)
        texto = self.g.veredicto(c)[1] + self.g.informe(c.hallazgos)
        self.assertEqual(self.g.por_tipo(c), {"número de reserva": 2, "razón social": 1})
        self.assertNotIn("Pesquera", texto)
        self.assertNotIn(reserva_inventada()[4:], texto)
        self.assertIn("a.md:1 razón social (S.A.)", texto)
        self.assertIn("notas SCLG<cifras>.md (nombre):1 número de reserva", texto)


class TestLectura(unittest.TestCase):
    """La lectura de lo que versiona git: lo seguido, lo nuevo, lo que el índice guarda distinto del árbol, los nombres;
    nunca lo ignorado ni lo que una unión lleva afuera. Y la del índice que le pasa git al hook."""

    @classmethod
    def setUpClass(cls):
        cls.g = cargar_guarda()

    def setUp(self):
        self.tmp = carpeta_corta("guarda_")
        self.addCleanup(borrar, self.tmp)

    def test_control_del_repo_inventado(self):
        self.assertEqual(self.g.control(self.tmp), "repo inventado: 13 archivos")

    def test_control_del_indice(self):
        self.assertEqual(self.g.control_indice(self.tmp), "índice: el propio, uno aparte y el veredicto")


class TestLoVersionado(unittest.TestCase):
    def test_lo_versionado_no_trae_datos_reales(self):
        # Lo que git versionaría hoy, con lo que el índice guarda distinto del árbol. El censo deja su archivo mutado en
        # soporte.FUENTES, y se lee de ahí.
        g = cargar_guarda()
        fuentes = soporte.FUENTES if soporte.FUENTES.resolve() != soporte.RAIZ.resolve() else None
        c = g.escanear(soporte.RAIZ, fuentes=fuentes)
        self.assertEqual(c.hallazgos, [], g.informe(c.hallazgos))
        # El control, en el repo de verdad: la guarda tiene que ver a la propia empresa en el programa, que la escribe
        # en los formularios. Si no la ve, dejó de leer, y su cero no vale.
        self.assertGreater(c.permitidos["razón social"], 0)
        # Y leyó cada archivo que git versionaría: ninguno ausente, fuera del repo ni ilegible.
        self.assertEqual((c.archivos, c.ausentes), (len(g.versionables(soporte.RAIZ)), []))
        self.assertIn("AQUASHIELD.py", g.versionables(soporte.RAIZ))


class TestElHook(unittest.TestCase):
    """El hook pre-commit (.githooks/pre-commit) con un commit de verdad, en un repo inventado que trae la guarda en
    tests/: frena lo que trae un dato, deja pasar lo limpio, y lee el índice que se commitea, no el árbol."""

    def setUp(self):
        self.tmp = carpeta_corta("hook_")
        self.addCleanup(borrar, self.tmp)
        self.repo = self.tmp / "r"
        self.repo.mkdir()
        self.git("init", "-q")
        for nombre in ("pre-commit", "pre-merge-commit"):
            destino = self.repo / ".githooks" / nombre
            destino.parent.mkdir(exist_ok=True)
            destino.write_bytes(desde_fuentes(f".githooks/{nombre}").read_bytes())
        (self.repo / "tests").mkdir()
        (self.repo / "tests" / "guarda_datos.py").write_bytes(desde_fuentes("tests/guarda_datos.py").read_bytes())
        self.git("config", "core.hooksPath", ".githooks")
        self.escribir("LEEME.md", "Un repo inventado.\n")
        self.git("add", "-A")
        self.git("commit", "-q", "--no-verify", "-m", "base")
        self.base = self.git("rev-parse", "HEAD")

    def git(self, *argumentos, fallar=True):
        codigo, salida, error = soporte.hijo(["git", *IDENTIDAD, *argumentos], self.repo, timeout=240,
                                             env_extra={"GIT_CEILING_DIRECTORIES": str(self.tmp)})
        if fallar and codigo:
            raise AssertionError(f"git {argumentos[0]} salió con {codigo}: {error}")
        return salida.strip() if fallar else (codigo, salida + error)

    def escribir(self, ruta, texto):
        (self.repo / ruta).write_bytes(texto.encode("utf-8"))

    def commit(self, *extra):
        return self.git("commit", "-q", "-m", "prueba", *extra, fallar=False)

    def test_frena_un_commit_con_una_razon_social(self):
        self.escribir("notas.md", "Lo pidió " + razon_inventada() + ".\n")
        self.git("add", "notas.md")
        codigo, salida = self.commit()
        self.assertNotEqual(codigo, 0, salida)
        self.assertIn("pre-commit: FRENADO.", salida)
        self.assertIn("notas.md:1 razón social (S.A.)", salida)
        self.assertNotIn("Pesquera", salida)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.base)

    def test_deja_pasar_un_commit_limpio(self):
        self.escribir("notas.md", "Nada que ver aquí.\n")
        self.git("add", "notas.md")
        codigo, salida = self.commit()
        self.assertEqual(codigo, 0, salida)
        self.assertIn("pre-commit: guarda de datos reales, controles en verde", salida)
        self.assertNotEqual(self.git("rev-parse", "HEAD"), self.base)

    def test_lee_el_indice_que_se_commitea(self):
        # Agregado con la reserva y limpiado después sin volver a agregar: el commit lleva la reserva, y frena. Con -a,
        # git agrega antes lo limpio en un índice aparte, que es el que el hook recibe, y pasa.
        self.escribir("notas.md", "reserva " + reserva_inventada() + "\n")
        self.git("add", "notas.md")
        self.escribir("notas.md", "sin reserva\n")
        codigo, salida = self.commit()
        self.assertNotEqual(codigo, 0, salida)
        self.assertIn("notas.md:1 número de reserva", salida)
        codigo, salida = self.commit("-a")
        self.assertEqual(codigo, 0, salida)

    def test_frena_el_commit_de_un_merge(self):
        # git merge no corre el pre-commit: el pre-merge-commit lo corre. El dato entró en otra rama con --no-verify.
        self.git("checkout", "-q", "-b", "otra")
        self.escribir("notas.md", "Lo pidió " + razon_inventada() + ".\n")
        self.git("add", "notas.md")
        self.git("commit", "-q", "--no-verify", "-m", "con el dato")
        self.git("checkout", "-q", "main")
        self.escribir("LEEME.md", "Un repo inventado, con otro cambio.\n")
        self.git("commit", "-q", "--no-verify", "-a", "-m", "otro")
        antes = self.git("rev-parse", "HEAD")
        codigo, salida = self.git("merge", "--no-ff", "-m", "merge", "otra", fallar=False)
        self.assertNotEqual(codigo, 0, salida)
        self.assertIn("notas.md:1 razón social", salida)
        self.assertEqual(self.git("rev-parse", "HEAD"), antes)

    def test_los_hooks_van_en_lf_y_ascii(self):
        # Los lee /bin/sh de Git Bash: un CR al final de una línea la rompe, y .gitattributes los deja en LF.
        for nombre in ("pre-commit", "pre-merge-commit"):
            datos = desde_fuentes(f".githooks/{nombre}").read_bytes()
            self.assertTrue(datos.startswith(b"#!/bin/sh\n"), nombre)
            self.assertNotIn(b"\r", datos, nombre)
            self.assertTrue(datos.isascii(), nombre)


if __name__ == "__main__":
    unittest.main()
