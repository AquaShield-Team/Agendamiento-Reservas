# -*- coding: utf-8 -*-
"""La guarda de datos reales (tests/guarda_datos.py; encargo 72, CICLO-guarda-de-datos.md): lo que entra al repo, que
es público, no trae razones sociales ni datos con la forma de un dato real, y el hook pre-commit lo frena.

La guarda se carga de soporte.FUENTES si el censo dejó ahí su copia mutada; si no, del repo. git corre de verdad: sobre
repos inventados en el temporal de antes de las pruebas, y sobre este repo solo para leer (ls-files, diff, cat-file).
Los valores inventados van armados por partes: escritos enteros, la guarda los encontraría en este archivo."""
import hashlib
import importlib.util
import itertools
import os
import re
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

import soporte

IDENTIDAD = ["-c", "user.name=Prueba Inventada", "-c", "user.email=prueba@ejemplo.invalid", "-c",
             "core.autocrlf=false", "-c", "init.defaultBranch=main"]
# La huella del bloque de las formas de tests/guarda_datos.py (entre sus dos marcas): los 16 primeros del sha256.
HUELLA_DE_LAS_FORMAS = "81c49b9ab3bf5df9"


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


def carpeta_de_git():
    """La carpeta de Git for Windows (la que trae usr/bin/sh.exe), desde el git del PATH: desde PowerShell es
    Git/cmd/git.exe, y desde Git Bash, Git/mingw64/bin/git.exe."""
    git = Path(shutil.which("git")).resolve()
    for carpeta in git.parents:
        if (carpeta / "usr" / "bin" / "sh.exe").is_file():
            return carpeta
    raise AssertionError("no encuentro la carpeta de Git for Windows")


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
        self.assertGreaterEqual(len(self.g.muestras()), 45)

    def test_la_lista_de_permitidos_esta_fija(self):
        # La propia empresa como el programa la escribe en el formulario de COSCO, el dueño como lo trae el pie del
        # panel y como autor de los commits, y su correo noreply: nada más. Un nombre de cliente no entra a la lista.
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
        # trae el nombre de un archivo. Un nombre con un dato queda como «‹un nombre con un dato›», con su carpeta; y de
        # un nombre sin un dato, sus tiras de 5 cifras o más. Hasta la revisión de seguridad del encargo 72, un nombre
        # con una razón social o un correo salía entero.
        c = self.g.Cuenta()
        nombre = "notas " + reserva_inventada() + ".md"
        self.g.revisar_texto(nombre, nombre + " (nombre)", c)
        texto_con_dato = "Lo pidió " + razon_inventada() + " y su reserva " + reserva_inventada()
        self.g.revisar_texto(texto_con_dato, "a.md", c)
        self.g.revisar_texto(texto_con_dato, "docs/" + razon_inventada() + ".md", c)
        self.g.revisar_texto(texto_con_dato, "informe " + "2026" + "101612.md", c)
        texto = self.g.veredicto(c)[1] + self.g.informe(c.hallazgos)
        self.assertEqual(self.g.por_tipo(c), {"número de reserva": 4, "razón social": 3})
        self.assertNotIn("Pesquera", texto)
        self.assertNotIn(reserva_inventada()[4:], texto)
        self.assertNotIn("101612", texto)
        self.assertIn("a.md:1 razón social (S.A.)", texto)
        self.assertIn("‹un nombre con un dato› (nombre):1 número de reserva", texto)
        self.assertIn("docs/‹un nombre con un dato›:1 razón social (S.A.)", texto)
        self.assertIn("informe <cifras>.md:1 razón social (S.A.)", texto)


    def test_los_digitos_verificadores(self):
        # Contra un cálculo aparte, no contra el de la guarda: la muestra del RUT armaba su dígito con la misma dv_rut,
        # y un dv_rut roto no lo veía nadie (revisión de código del encargo 72). Lo mismo con ISO 6346.
        def dv(cuerpo):
            r = 11 - sum(int(c) * p for c, p in zip(reversed(cuerpo), itertools.cycle(range(2, 8)))) % 11
            return {11: "0", 10: "K"}.get(r, str(r))
        conocidos = (("12345678", "5"), ("11111111", "1"), ("6", "K"), ("1", "9"), ("10000000", "8"))
        self.assertEqual([(self.g.dv_rut(c), dv(c)) for c, _ in conocidos], [(d, d) for _, d in conocidos])
        cuerpos = [str(c) for c in range(1, 30000, 7)]
        self.assertEqual([c for c in cuerpos if self.g.dv_rut(c) != dv(c)], [])
        self.assertEqual({dv(c) for c in cuerpos} >= {"0", "K"}, True)
        valor = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", (10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27,
                                                        28, 29, 30, 31, 32, 34, 35, 36, 37, 38)))

        def iso(c):
            suma = sum((valor[x] if x.isalpha() else int(x)) * 2 ** i for i, x in enumerate(c[:10]))
            return suma % 11 % 10 == int(c[10])
        codigos = [d + f"{n:06d}" + str(k) for d in ("CSQU", "TGHU", "XYZU") for n in range(0, 999999, 99991)
                   for k in range(10)]
        self.assertEqual([c for c in codigos if self.g.contenedor_valido(c) != iso(c)], [])
        self.assertTrue(self.g.contenedor_valido("CSQU" + "305438" + "3"))     # el ejemplo de la norma

    def test_cada_forma_y_cada_separador(self):
        # Cada forma de las listas, detrás de un nombre inventado (o delante, las que van delante), y cada separador que
        # la guarda pasa a espacio, frenan. Hasta la revisión de código del encargo 72, la mayoría se podía quitar sin
        # que cayera ninguna prueba.
        def ve(texto):
            c = self.g.Cuenta()
            self.g.revisar_texto(texto, "x.md", c)
            return self.g.por_tipo(c).get("razón social", 0) > 0
        g, nombre = self.g, "Pesquera Inventada "
        formas = (list(g.TRES_O_MAS) + [t.capitalize() for t in g.TRES_O_MAS] + list(g.DOS)
                  + [a + "." + b + "." for a, b in g.DOS] + list(g.PALABRAS) + list(g.EJEMPLOS_DE_OTRAS))
        self.assertEqual([f for f in formas if not ve(nombre + f)], [])
        self.assertEqual([f for f in g.FORMAS_DELANTE if not ve(f + " " + nombre)], [])
        sa, barra = "S" + chr(46) + "A" + chr(46), chr(92)
        separadores = {
            "escape": "Pesquera" + barra + "u0020Inventada" + barra + "u0020" + sa,
            "barra antes de un signo": "Pesquera Inventada S" + barra + ".A" + barra + ".",
            "entidad": "Pesquera&nbsp;Inventada&#32;" + sa,
            "%HH": "Pesquera%20Inventada%20" + sa,
            "etiqueta": "Pesquera Inventada <b>" + sa + "</b>",
            "unión de cadenas": '"Pesquera Inv" + "entada ' + sa + '"',
            "comillas y signos": "«Pesquera»_Inventada=" + sa,
        }
        self.assertEqual([k for k, v in separadores.items() if not ve(v)], [])

    def test_las_formas_de_la_guarda_estan_fijas(self):
        # Lo que va entre las dos marcas de tests/guarda_datos.py no cuenta para la razón social, y una razón social
        # escrita ahí no se vería: la suite fija ese bloque por su huella (revisión de código del encargo 72). Cambiarlo
        # pide cambiar la huella en el mismo commit, a la vista de quien lo revisa. Y sin una de sus marcas, se revisa
        # entero.
        texto = desde_fuentes("tests/guarda_datos.py").read_bytes().decode("utf-8")
        lineas = texto.split("\n")
        bloque = "\n".join(lineas[lineas.index(self.g.MARCA_DESDE):lineas.index(self.g.MARCA_HASTA) + 1])
        self.assertEqual(hashlib.sha256(bloque.encode("utf-8")).hexdigest()[:16], HUELLA_DE_LAS_FORMAS)
        c = self.g.Cuenta()
        self.g.revisar_texto(texto.replace(self.g.MARCA_HASTA + "\n", "", 1), self.g.PROPIO, c)
        self.assertGreater(self.g.por_tipo(c).get("razón social", 0), 0)


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
        self.assertEqual(self.g.control(self.tmp), "repo inventado: 14 archivos")

    def test_control_del_indice(self):
        self.assertEqual(self.g.control_indice(self.tmp), "índice: el propio, uno aparte y el veredicto")


class TestLoVersionado(unittest.TestCase):
    def test_lo_versionado_no_trae_datos_reales(self):
        # Lo que git versionaría hoy, con lo que el índice guarda distinto del árbol. El censo deja su archivo mutado en
        # soporte.FUENTES, y se lee de ahí.
        g = cargar_guarda()
        fuentes = soporte.FUENTES if soporte.FUENTES.resolve() != soporte.RAIZ.resolve() else None
        c = g.escanear(soporte.RAIZ, fuentes=fuentes)
        if c.hallazgos:                      # el informe, nunca la lista: la lista trae los nombres de los archivos
            self.fail(g.informe(c.hallazgos))
        # Ningún binario: la guarda no lo puede leer, y el hook lo frena.
        self.assertEqual([g.mostrar(n) for n, m in c.descartados if m == "binario"], [])
        # El control, en el repo de verdad: la guarda tiene que ver a la propia empresa en el programa, que la escribe
        # en los formularios. Si no la ve, dejó de leer, y su cero no vale.
        self.assertGreater(c.permitidos["razón social"], 0)
        # Y leyó cada archivo que git versionaría: ninguno ausente, fuera del repo ni ilegible.
        self.assertEqual((c.archivos, c.ausentes), (len(g.versionables(soporte.RAIZ)), []))
        self.assertIn("AQUASHIELD.py", g.versionables(soporte.RAIZ))


class TestLimites(unittest.TestCase):
    """Lo que no puede colgar a la guarda: un git que no termina, y un archivo hecho para que las expresiones retrocedan
    (las dos, de la revisión de seguridad del encargo 72)."""

    def test_el_plazo_de_git_se_cumple(self):
        # Al vencer el plazo, la guarda mata el árbol de git con el taskkill de System32, y la última lectura también
        # tiene plazo: un hijo de git con las tuberías abiertas la dejaba esperando (300 s con un plazo de 4). Con un
        # proceso falso: no corre nada.
        g = cargar_guarda()
        llamadas = []

        class Proceso:
            pid = 4242

            def __init__(self, args, **_):
                self.args = list(args)
                llamadas.append(("lanza", Path(self.args[0]).name.lower(), self.args[1:]))

            def communicate(self, entrada=None, timeout=None):
                llamadas.append(("lee", timeout))
                if timeout is None:
                    raise AssertionError("una lectura sin plazo esperaría para siempre")
                raise subprocess.TimeoutExpired(self.args, timeout)

            def wait(self, timeout=None):
                llamadas.append(("espera", timeout))
                return 0

            def kill(self):
                llamadas.append(("mata",))

        g.POPEN, g.PLAZO_GIT = Proceso, 3
        with self.assertRaisesRegex(RuntimeError, "no terminó en 3 s"):
            g._git(Path(tempfile.gettempdir()), "status")
        self.assertIn(("lanza", "taskkill.exe", ["/T", "/F", "/PID", "4242"]), llamadas)
        self.assertEqual(llamadas[-2:], [("mata",), ("lee", 10)])
        self.assertNotIn(("lee", None), llamadas)

    def test_un_archivo_hecho_para_colgarla_no_la_cuelga(self):
        # Una etiqueta de reserva y una tira larga de espacios (con `\s*:?\s*`, 64.000 espacios tardaban 46 s), y miles
        # de hallazgos en un archivo (contar las líneas desde el principio en cada uno la hacía cuadrática).
        g = cargar_guarda()
        texto = "Booking number" + " " * 64000 + "x\n" + ("reserva " + reserva_inventada() + "\n") * 20000
        c = g.Cuenta()
        t0 = time.monotonic()
        g.revisar_texto(texto, "largo.txt", c)
        segundos = time.monotonic() - t0
        self.assertEqual(g.por_tipo(c), {"número de reserva": 20000})
        self.assertEqual(c.hallazgos[-1][2], 20001)
        self.assertLess(segundos, 15)


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

    def test_sin_la_guarda_o_sin_python_frena(self):
        # Falla cerrada (revisión de código del encargo 72): sin la guarda en el árbol abierto, o sin python en el PATH,
        # el hook frena el commit con su motivo, en lugar de dejarlo pasar sin revisar.
        self.escribir("notas.md", "Nada que ver aquí.\n")
        self.git("add", "notas.md")
        git = carpeta_de_git()
        sin_python = os.pathsep.join(str(git / d) for d in ("usr/bin", "mingw64/bin"))   # sin el PATH de Windows
        codigo, salida, error = soporte.hijo([str(git / "usr/bin/sh.exe"), ".githooks/pre-commit"], self.repo,
                                             env_extra={"PATH": sin_python, "GIT_CEILING_DIRECTORIES": str(self.tmp)})
        self.assertEqual(codigo, 1, salida + error)
        self.assertIn("no hay 'python' en el PATH", error)
        (self.repo / "tests" / "guarda_datos.py").unlink()
        codigo, salida = self.commit()
        self.assertNotEqual(codigo, 0, salida)
        self.assertIn("no encuentro tests/guarda_datos.py", salida)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.base)

    def test_sin_indice_o_con_el_detector_roto_frena(self):
        # Falla cerrada, en la guarda: un índice que no existe se leería como uno vacío y daría un verde con cero
        # archivos; y un detector que no da sus muestras no audita. Las dos frenan (revisión de código del encargo 72).
        guarda = self.repo / "tests" / "guarda_datos.py"

        def correr(**entorno):
            entorno["GIT_CEILING_DIRECTORIES"] = str(self.tmp)
            return soporte.hijo(["python", "-I", str(guarda), "--pre-commit"], self.repo, env_extra=entorno)
        codigo, salida, error = correr(GIT_INDEX_FILE=str(self.repo / ".git" / "no-existe"))
        self.assertEqual(codigo, 1, salida + error)
        self.assertIn("No encuentro el índice que se va a commitear", error)
        # Un detector roto: otra control_detector, antes del bloque que corre el hook (después ya no se usaría).
        texto = guarda.read_bytes().decode("utf-8")
        principal = '\nif __name__ == "__main__":'
        self.assertEqual(texto.count(principal), 1)
        roto = '\ndef control_detector():\n    return ["roto"]\n\n' + principal
        guarda.write_bytes(texto.replace(principal, roto).encode("utf-8"))
        codigo, salida, error = correr()
        self.assertEqual(codigo, 1, salida + error)
        self.assertIn("El detector está roto", error)

    def test_gitignore_versiona_los_hooks(self):
        # .gitignore es una lista blanca: sin su línea, los hooks quedan fuera del repo.
        lineas = desde_fuentes(".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("!/.githooks/", lineas)

    def test_los_hooks_van_en_lf_y_ascii(self):
        # Los lee /bin/sh de Git Bash: un CR al final de una línea la rompe, y .gitattributes los deja en LF.
        for nombre in ("pre-commit", "pre-merge-commit"):
            datos = desde_fuentes(f".githooks/{nombre}").read_bytes()
            self.assertTrue(datos.startswith(b"#!/bin/sh\n"), nombre)
            self.assertNotIn(b"\r", datos, nombre)
            self.assertTrue(datos.isascii(), nombre)


if __name__ == "__main__":
    unittest.main()
