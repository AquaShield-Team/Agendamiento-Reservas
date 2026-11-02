# -*- coding: utf-8 -*-
"""tests/igual_que_github.py (pedido de Marcelo, encargo 93): clona la rama desde su remoto dentro de la carpeta del
programa, compara commit, árbol, bytes y cambios sin commitear, y corre la suite en el clon. Aquí, sin red: el remoto
es un repo inventado en el temporal (una ruta), y la suite del clon se reemplaza por una respuesta falsa. git corre de
verdad, con el Popen verdadero que guarda el arnés (soporte._POPEN). Valores inventados."""
import importlib.util
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

import soporte

IDENTIDAD = ["-c", "user.name=Prueba Inventada", "-c", "user.email=prueba@ejemplo.invalid", "-c",
             "core.autocrlf=false", "-c", "init.defaultBranch=main"]


def desde_fuentes(rel):
    """El archivo de la copia del censo, si la trae; si no, el del repo."""
    ruta = soporte.FUENTES / rel
    return ruta if ruta.exists() else soporte.RAIZ / rel


def cargar():
    spec = importlib.util.spec_from_file_location("igual_prueba", desde_fuentes("tests/igual_que_github.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.POPEN = soporte._POPEN            # el arnés pone una trampa en subprocess.Popen
    return mod


def git(carpeta, *args):
    p = soporte._POPEN(["git", "-C", str(carpeta), *IDENTIDAD, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       stdin=subprocess.DEVNULL, env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))
    out, err = p.communicate(timeout=120)
    if p.returncode:
        raise RuntimeError(f"git {args}: {err.decode('utf-8', 'replace')[:200]}")
    return out.decode("utf-8", "replace").strip()


class TestIgualQueGithub(unittest.TestCase):
    """Un remoto inventado (un repo vacío en el temporal) y una «carpeta del programa» clonada de él, con un espacio en el
    nombre, como la de verdad. Cada prueba deja la carpeta como la encontró."""

    @classmethod
    def setUpClass(cls):
        cls.mod = cargar()
        cls.tmp = Path(tempfile.mkdtemp(prefix="igual_github_"))
        remoto, armado = cls.tmp / "remoto.git", cls.tmp / "armado"
        git(cls.tmp, "init", "--bare", "-q", str(remoto))
        git(cls.tmp, "init", "-q", str(armado))
        (armado / "tests").mkdir()
        # Como el repo de verdad: sin esto, el core.autocrlf=true del sistema saca el clon de la herramienta en CRLF.
        (armado / ".gitattributes").write_bytes(b"* text=auto eol=lf\n")
        (armado / "programa.py").write_bytes(b"print('hola')\n")
        (armado / "tests" / "prueba.txt").write_bytes(b"uno\n")
        git(armado, "add", "-A")
        git(armado, "commit", "-q", "-m", "primero")
        git(armado, "push", "-q", str(remoto), "main")
        cls.local = cls.tmp / "carpeta del programa"
        git(cls.tmp, "clone", "-q", str(remoto), str(cls.local))

    @classmethod
    def tearDownClass(cls):
        cls.mod._borrar(cls.tmp)

    def comparar(self, *, rama="main", sin_suite=True, dejar=False, raiz=None):
        lineas = []
        rc = self.mod.comparar(raiz or self.local, rama, sin_suite=sin_suite, dejar=dejar, salida=lineas.append)
        return rc, "\n".join(lineas)

    def clones(self):
        trabajo = self.local / ".trabajo" / "igual-que-github"
        return sorted(p.name for p in trabajo.iterdir() if p.is_dir()) if trabajo.exists() else []

    def tearDown(self):
        self.mod._borrar(self.local / ".trabajo")

    def test_igual(self):
        rc, texto = self.comparar()
        self.assertEqual(rc, 0, texto)
        self.assertIn("commit: igual · árbol: igual", texto)
        self.assertIn("archivos versionados: 3 · faltan en la carpeta: 0 · distintos en bytes: 0 · cambios sin "
                      "commitear: 0", texto)
        self.assertIn("IGUAL: este equipo corre lo mismo que GitHub", texto)
        self.assertEqual(self.clones(), [])           # todo igual: borra el clon

    def test_el_clon_queda_dentro_de_la_carpeta(self):
        rc, texto = self.comparar(dejar=True)
        self.assertEqual(rc, 0, texto)
        [clon] = self.clones()
        self.assertTrue(clon.startswith("main-"))
        self.assertEqual(git(self.local / ".trabajo" / "igual-que-github" / clon, "rev-parse", "HEAD"),
                         git(self.local, "rev-parse", "HEAD"))

    def test_un_cambio_sin_commitear(self):
        archivo = self.local / "programa.py"
        original = archivo.read_bytes()
        archivo.write_bytes(b"print('chao')\n")
        try:
            rc, texto = self.comparar()
        finally:
            archivo.write_bytes(original)
        self.assertEqual(rc, 1)
        self.assertIn("distintos en bytes: 1 · cambios sin commitear: 1", texto)
        self.assertIn("   distinto: programa.py", texto)
        self.assertIn("DISTINTO: mira las líneas de arriba", texto)
        self.assertEqual(len(self.clones()), 1)       # algo difiere: deja el clon

    def test_un_cambio_solo_en_el_indice(self):
        # Los archivos son los de GitHub, pero el índice trae un cambio preparado: también es distinto.
        archivo = self.local / "programa.py"
        original = archivo.read_bytes()
        archivo.write_bytes(b"print('preparado')\n")
        git(self.local, "add", "programa.py")
        archivo.write_bytes(original)
        try:
            rc, texto = self.comparar()
        finally:
            git(self.local, "reset", "-q")
        self.assertEqual(rc, 1)
        self.assertIn("distintos en bytes: 0 · cambios sin commitear: 1", texto)
        self.assertIn("DISTINTO: mira las líneas de arriba", texto)

    def test_un_proceso_que_no_termina_se_corta(self):
        # Al vencer su plazo se cierra el árbol del proceso, y vuelve con 124 en segundos, no cuando el proceso termine.
        t0 = time.monotonic()
        rc, _, err = self.mod._correr([sys.executable, "-c", "import time; time.sleep(60)"], plazo=1)
        self.assertEqual(rc, 124)
        self.assertIn("venció el plazo de 1 s", err)
        self.assertLess(time.monotonic() - t0, 30)

    def test_main_lee_sus_argumentos(self):
        original = self.mod.RAIZ
        self.mod.RAIZ = self.local
        try:
            self.assertEqual(self.mod.main(["--rama", "main", "--sin-suite", "--dejar"]), 0)
            self.assertEqual(len(self.clones()), 1)
            self.mod._borrar(self.local / ".trabajo")
            self.assertEqual(self.mod.main(["--rama", "no-existe", "--sin-suite"]), 2)
            self.assertEqual(self.mod.main(["--sin-suite"]), 0)          # sin --rama, la de la carpeta
            self.assertEqual(self.clones(), [])
        finally:
            self.mod.RAIZ = original

    def test_un_commit_que_github_no_tiene(self):
        # Un commit vacío: el árbol y los bytes son los mismos, y solo el commit difiere. Con un cambio, también el árbol.
        for vacio, esperado in ((True, "commit: DISTINTO · árbol: igual"), (False, "commit: DISTINTO · árbol: DISTINTO")):
            if vacio:
                git(self.local, "commit", "-q", "--allow-empty", "-m", "local")
            else:
                (self.local / "programa.py").write_bytes(b"print('otro')\n")
                git(self.local, "commit", "-q", "-am", "local")
            try:
                rc, texto = self.comparar()
            finally:
                git(self.local, "reset", "-q", "--hard", "origin/main")
                self.mod._borrar(self.local / ".trabajo")
            with self.subTest(vacio=vacio):
                self.assertEqual(rc, 1)
                self.assertIn(esperado, texto)

    def test_la_carpeta_en_otro_commit(self):
        # La rama es la de GitHub, pero la carpeta corre otro commit (suelto), con los mismos archivos.
        git(self.local, "commit", "-q", "--allow-empty", "-m", "suelto")
        git(self.local, "checkout", "-q", "--detach")
        git(self.local, "branch", "-f", "main", "origin/main")
        try:
            rc, texto = self.comparar()
        finally:
            git(self.local, "checkout", "-q", "main")
        self.assertEqual(rc, 1)
        self.assertIn("commit: igual · árbol: igual", texto)
        self.assertIn("(la carpeta está en ", texto)
        self.assertIn("DISTINTO: mira las líneas de arriba", texto)

    def test_una_rama_sin_forma_no_clona(self):
        # Ni subir de carpeta, ni una opción de git, ni otra cosa: no crea nada, ni adentro ni afuera.
        antes = sorted(p.name for p in self.tmp.iterdir())
        for rama in ("..\\..\\..\\fuera", "-x", "a..b", "C:\\fuera", "rama con espacio", "ñandú"):
            with self.subTest(rama=rama):
                rc, texto = self.comparar(rama=rama)
                self.assertEqual(rc, 2, texto)
                self.assertIn("no tiene la forma de una rama", texto)
                self.assertFalse((self.local / ".trabajo").exists())
        self.assertEqual(sorted(p.name for p in self.tmp.iterdir()), antes)

    def test_la_suite_del_clon_va_con_mas_plazo(self):
        # El modo hijo corre el correr.py del clon tal cual, con 7.200 s en vez de los 1.200 por omisión; los demás
        # plazos (los 240 de cada par del censo) no cambian. Aquí, un correr.py inventado que anota lo que recibe.
        falsa = self.tmp / "tests falsos"
        falsa.mkdir(exist_ok=True)
        (falsa / "correr.py").write_text(
            "import pathlib, sys\nvistos = []\n\n"
            "def correr_unittest(ids=None, fuentes=None, timeout=1200):\n    vistos.append(timeout)\n    return 0, ''\n\n"
            "def main():\n    correr_unittest()\n    correr_unittest(['x'], None, 240)\n"
            "    (pathlib.Path(__file__).parent / 'vistos.txt').write_text(repr((vistos, sys.argv[1:])))\n"
            "    sys.exit(7)\n", encoding="utf-8")
        argv, path = list(sys.argv), list(sys.path)
        try:
            with self.assertRaises(SystemExit) as fin:
                self.mod._correr_suite(falsa)
        finally:
            sys.argv[:], sys.path[:] = argv, path
        self.assertEqual(fin.exception.code, 7)
        self.assertEqual((falsa / "vistos.txt").read_text(), repr(([7200, 240], [])))

    def test_sin_remoto_o_sin_la_rama_no_compara(self):
        sin = self.tmp / "sin remoto"
        git(self.tmp, "init", "-q", str(sin))
        rc, texto = self.comparar(raiz=sin)
        self.assertEqual(rc, 2)
        self.assertIn("No pude leer el remoto origin", texto)
        rc, texto = self.comparar(rama="no-existe")
        self.assertEqual(rc, 2)
        self.assertIn("El clon falló", texto)

    def test_distintos_en_bytes(self):
        a, b = self.tmp / "bytes_a", self.tmp / "bytes_b"
        for d, uno, dos in ((a, b"x\n", b"y\n"), (b, b"x\n", b"y\r\n")):
            d.mkdir(exist_ok=True)
            (d / "uno.txt").write_bytes(uno)
            (d / "dos.txt").write_bytes(dos)
        (a / "tres.txt").write_bytes(b"z\n")
        self.assertEqual(self.mod.distintos_en_bytes(a, b, ["uno.txt", "dos.txt", "tres.txt"]),
                         (["tres.txt"], ["dos.txt"]))

    def test_git_sin_clave_ni_preguntas(self):
        # Cada git va sin ayudante de credenciales y sin preguntas (el remoto es público).
        llamadas, original = [], self.mod._correr

        def espia(args, cwd=None, env=None, plazo=None):
            llamadas.append((args, env))
            return original(args, cwd=cwd, env=env, plazo=plazo or self.mod.PLAZO_GIT)
        self.mod._correr = espia
        try:
            rc, texto = self.comparar()
        finally:
            self.mod._correr = original
        self.assertEqual(rc, 0, texto)
        de_git = [(a, e) for a, e in llamadas if a[0] == "git"]
        self.assertTrue(de_git)
        for args, env in de_git:
            self.assertIn("credential.helper=", args)
            self.assertEqual((env["GIT_TERMINAL_PROMPT"], env["GCM_INTERACTIVE"]), ("0", "never"))

    def test_la_suite_corre_en_el_clon(self):
        # La suite del clon se reemplaza: lo que se mira es con qué la lanza (el clon, su temporal sin espacios y dentro
        # de la carpeta, el techo de git ahí) y cómo lee su resultado.
        original = self.mod._correr
        for k, (rc_suite, ultima, rc_esperado, queda) in enumerate(((0, "RESULTADO: OK", 0, 0),
                                                                    (1, "RESULTADO: FALLA", 1, 1),
                                                                    (0, "RESULTADO: FALLA", 1, 1),
                                                                    (1, "RESULTADO: OK", 1, 1))):
            vistas = []

            def falsa(args, cwd=None, env=None, plazo=None):
                if "--correr-suite" in args:
                    vistas.append((args, cwd, env, plazo))
                    return rc_suite, "algo\n" + ultima + "\n", ""
                return original(args, cwd=cwd, env=env, plazo=plazo or self.mod.PLAZO_GIT)
            self.mod._correr = falsa
            try:
                rc, texto = self.comparar(sin_suite=False)
            finally:
                self.mod._correr = original
            with self.subTest(k=k):
                self.assertEqual(rc, rc_esperado, texto)
                self.assertIn(f"suite en el clon: {ultima} (código {rc_suite})", texto)
                [(args, cwd, env, plazo)] = vistas
                self.assertEqual(Path(args[-1]).parent, Path(cwd))
                self.assertEqual(Path(args[-1]).name, "tests")
                self.assertNotIn(" ", env["TEMP"])
                self.assertEqual((env["TMP"], env["TMPDIR"], env["GIT_CEILING_DIRECTORIES"]), (env["TEMP"],) * 3)
                self.assertEqual(Path(env["TEMP"]).resolve().parent, (self.local / ".trabajo" / "igual-que-github").resolve())
                self.assertEqual(plazo, self.mod.PLAZO_SUITE)
                self.assertEqual(len([c for c in self.clones() if c.startswith("main-")]), queda)
            self.mod._borrar(self.local / ".trabajo")


if __name__ == "__main__":
    unittest.main()
