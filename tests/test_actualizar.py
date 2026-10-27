# -*- coding: utf-8 -*-
"""El actualizador de los equipos de los colegas (actualizar.py; decisión de Marcelo, encargo 60,
CICLO-actualizar-desde-estable.md): al abrir, trae la última versión de la rama «estable» sin pisar nada propio del
equipo, y si no puede, el programa abre con la versión que tiene y el panel lo dice.

Con git de verdad, sobre repositorios inventados en la sandbox: un origen local (sin red), el trabajo de quien publica
y el clon del colega. El actualizador corre como lo corre el .bat, en un proceso aparte, desde soporte.FUENTES (el
censo deja ahí su copia mutada), con --carpeta apuntando al clon."""
import json
import re
import os
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import soporte

ACTUALIZAR = soporte.FUENTES / "actualizar.py"
PREPARADOR = soporte.FUENTES / "preparar_entorno.py"
REQUISITOS = soporte.FUENTES / "requirements.txt"
IDENTIDAD = ["-c", "user.name=Prueba Inventada", "-c", "user.email=prueba@ejemplo.invalid", "-c",
             "core.autocrlf=false", "-c", "init.defaultBranch=main"]
GITIGNORE = ("/*\nconfig.json\nperfiles/\nlogs/\n*.xlsx\n!/.gitignore\n!/.gitattributes\n!/AQUASHIELD.py\n"
             "!/actualizar.py\n!/preparar_entorno.py\n!/requirements.txt\n!/LEEME.md\n")


def carpeta_corta(prefijo):
    """Una carpeta nueva en el temporal de antes de las pruebas, no en la sandbox de otra clase (soporte.cargar mueve
    tempfile.tempdir): en el censo, las rutas de los objetos de git pasaban los 260 caracteres y git no los escribía."""
    return Path(tempfile.mkdtemp(prefix=prefijo, dir=soporte.TMP_ORIGINAL))


def borrar(carpeta):
    """git deja sus .pack de solo lectura, y Windows no borra un archivo de solo lectura."""
    def de_nuevo(funcion, ruta, *_):
        os.chmod(ruta, 0o666)
        funcion(ruta)
    shutil.rmtree(carpeta, onexc=de_nuevo)


class Repos(object):
    """El trabajo de quien publica, el origen y el clon del colega, en la rama «estable»."""

    def __init__(self, raiz, rama="estable"):
        self.raiz = raiz
        # Nombres cortos: git de Windows no escribe un objeto en una ruta de más de 260 caracteres.
        self.trabajo, self.origen, self.clon = raiz / "w", raiz / "o.git", raiz / "c"
        self.trabajo.mkdir(parents=True)
        self.git(self.trabajo, "init", "-q")
        self.escribir({".gitignore": GITIGNORE, ".gitattributes": "* text=auto eol=lf\n",
                       "AQUASHIELD.py": "version = 1\n", "LEEME.md": "uno\n"})
        self.publicar("v1")
        self.git(raiz, "clone", "-q", "--bare", str(self.trabajo), str(self.origen))
        self.git(self.trabajo, "remote", "add", "origin", str(self.origen))
        self.git(self.trabajo, "push", "-q", "origin", "main", "main:estable")
        self.git(raiz, "clone", "-q", "-b", rama, str(self.origen), str(self.clon))

    def git(self, carpeta, *argumentos):
        codigo, salida, error = soporte.hijo(["git", *IDENTIDAD, *argumentos], carpeta,
                                             env_extra={"GIT_CEILING_DIRECTORIES": str(self.raiz)})
        if codigo:
            raise AssertionError(f"git {argumentos} salió con {codigo}: {error}")
        return salida.strip()

    def escribir(self, archivos, carpeta=None):
        for ruta, texto in archivos.items():
            p = (carpeta or self.trabajo) / ruta
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(texto.encode("utf-8"))

    def publicar(self, mensaje, archivos=None, quitar=(), a_estable=True):
        """Un commit nuevo en el trabajo; si hay origen, lo sube a main y, si se pide, también a estable."""
        for ruta in quitar:
            (self.trabajo / ruta).unlink()
        self.escribir(archivos or {})
        self.git(self.trabajo, "add", "-A", "-f")
        self.git(self.trabajo, "commit", "-q", "-m", mensaje)
        if self.origen.exists():
            self.git(self.trabajo, "push", "-q", "origin", "main", *(["main:estable"] if a_estable else []))
        return self.git(self.trabajo, "rev-parse", "HEAD")

    def head(self):
        return self.git(self.clon, "rev-parse", "HEAD")

    def leer(self, ruta):
        return (self.clon / ruta).read_bytes().decode("utf-8")

    def actualizar(self, timeout=120):
        codigo, salida, error = soporte.hijo(["python", str(ACTUALIZAR), "--carpeta", str(self.clon)], self.raiz,
                                             timeout=timeout,
                                             env_extra={"GIT_CEILING_DIRECTORIES": str(self.raiz)})
        datos = json.loads((self.clon / "logs" / "actualizacion.json").read_bytes().decode("utf-8"))
        return codigo, datos, salida + error


class TestActualizar(unittest.TestCase):
    def setUp(self):
        soporte.DISPAROS.clear()
        self.raiz = carpeta_corta("aq_act_")
        self.addCleanup(borrar, self.raiz)

    def tearDown(self):
        self.assertEqual(soporte.DISPAROS, [])

    def repos(self, **k):
        return Repos(self.raiz / "r", **k)

    def test_trae_la_version_estable_sin_tocar_lo_propio_del_equipo(self):
        r = self.repos()
        lo_propio = {"config.json": "claves del colega\n", "perfiles/chrome/Cookies": "sesion\n",
                     "logs/web_x/log.txt": "corrida\n", "Reservas AQUASHIELD.xlsx": "planilla\n"}
        r.escribir(lo_propio, r.clon)
        viejo = r.head()
        nuevo = r.publicar("v2", {"AQUASHIELD.py": "version = 2\n", "nuevo.py": "x = 1\n"}, quitar=["LEEME.md"])
        codigo, datos, salida = r.actualizar()
        self.assertEqual((codigo, datos["estado"], r.head(), datos["desde"], datos["version"]),
                         (0, "actualizada", nuevo, viejo, nuevo))
        self.assertEqual(datos["texto"], f"⟳ AQUASHIELD se actualizó a la versión estable {nuevo[:7]} (tenía la "
                                         f"{viejo[:7]}).")
        self.assertEqual((r.leer("AQUASHIELD.py"), r.leer("nuevo.py"), (r.clon / "LEEME.md").exists()),
                         ("version = 2\n", "x = 1\n", False))
        for ruta, texto in lo_propio.items():
            with self.subTest(ruta=ruta):
                self.assertEqual(r.leer(ruta), texto)
        self.assertIn(datos["texto"], salida)

    def test_al_dia_no_cambia_nada(self):
        r = self.repos()
        codigo, datos, _ = r.actualizar()
        self.assertEqual((codigo, datos["estado"], datos["texto"]),
                         (0, "al-dia", f"✓ AQUASHIELD está al día con la versión estable ({r.head()[:7]})."))

    def test_el_equipo_de_desarrollo_en_main_no_se_actualiza_ni_busca(self):
        r = self.repos(rama="main")
        viejo = r.head()
        r.publicar("v2", {"AQUASHIELD.py": "version = 2\n"})
        codigo, datos, _ = r.actualizar()
        self.assertEqual((codigo, datos["estado"], r.head(), r.leer("AQUASHIELD.py")),
                         (0, "no-aplica", viejo, "version = 1\n"))
        self.assertEqual(datos["texto"], "Este equipo no se actualiza solo: está en la rama «main», y solo se "
                                         "actualiza la rama «estable».")
        # Ni siquiera la buscó: su copia de origin/estable sigue en la de antes.
        self.assertEqual(r.git(r.clon, "rev-parse", "origin/estable"), viejo)

    def test_solo_avanza_lo_que_marcelo_pone_en_estable(self):
        r = self.repos()
        viejo = r.head()
        r.publicar("v2 sin probar", {"AQUASHIELD.py": "version = 2\n"}, a_estable=False)
        codigo, datos, _ = r.actualizar()
        self.assertEqual((datos["estado"], r.head(), r.leer("AQUASHIELD.py")), ("al-dia", viejo, "version = 1\n"))

    def test_sin_red_abre_con_la_que_tiene(self):
        r = self.repos()
        viejo = r.head()
        r.publicar("v2", {"AQUASHIELD.py": "version = 2\n"})
        shutil.move(str(r.origen), str(r.raiz / "origen_movido.git"))
        codigo, datos, _ = r.actualizar()
        self.assertEqual((codigo, datos["estado"], r.head(), r.leer("AQUASHIELD.py")),
                         (0, "sin-actualizar", viejo, "version = 1\n"))
        self.assertTrue(datos["texto"].startswith("⚠ No actualicé AQUASHIELD: no pude buscar la versión nueva ("),
                        datos["texto"])
        self.assertTrue(datos["texto"].endswith(f"Abro con la versión que tiene este equipo ({viejo[:7]})."))

    def test_un_cambio_en_un_archivo_del_programa_no_se_pisa(self):
        r = self.repos()
        viejo = r.head()
        r.escribir({"AQUASHIELD.py": "version = 1  # tocado por el colega\n"}, r.clon)
        r.publicar("v2", {"AQUASHIELD.py": "version = 2\n"})
        codigo, datos, _ = r.actualizar()
        self.assertEqual((codigo, datos["estado"], r.head(), r.leer("AQUASHIELD.py")),
                         (0, "sin-actualizar", viejo, "version = 1  # tocado por el colega\n"))
        self.assertEqual(datos["motivo"], "hay cambios en archivos del programa: «AQUASHIELD.py»")

    def test_un_commit_propio_no_se_pierde(self):
        r = self.repos()
        r.escribir({"AQUASHIELD.py": "version = 1.5\n"}, r.clon)
        r.git(r.clon, "commit", "-q", "-am", "propio")
        propio = r.head()
        r.publicar("v2", {"LEEME.md": "dos\n"})
        codigo, datos, _ = r.actualizar()
        self.assertEqual((datos["estado"], r.head(), r.leer("AQUASHIELD.py"), datos["motivo"]),
                         ("sin-actualizar", propio, "version = 1.5\n", "este equipo tiene commits que la versión "
                                                                       "estable no trae (propios, o de una estable "
                                                                       "anterior)"))

    def test_un_archivo_propio_ignorado_donde_la_version_pone_uno_no_se_pisa(self):
        # git lo pisaría sin avisar (medido en el encargo 60): si la versión estable empezara a versionar config.json.
        r = self.repos()
        viejo = r.head()
        r.escribir({"config.json": "claves del colega\n"}, r.clon)
        r.publicar("v2", {"config.json": "{}\n", "AQUASHIELD.py": "version = 2\n"})
        codigo, datos, _ = r.actualizar()
        self.assertEqual((codigo, datos["estado"], r.head(), r.leer("config.json"), r.leer("AQUASHIELD.py")),
                         (0, "sin-actualizar", viejo, "claves del colega\n", "version = 1\n"))
        self.assertEqual(datos["motivo"], "la versión nueva trae «config.json», y en esta carpeta ya hay algo con ese "
                                          "nombre que no es del programa: no lo piso")

    def test_una_carpeta_o_un_archivo_propio_en_el_camino_no_se_pisan(self):
        casos = (({"perfiles/x": "sesion\n"}, {"perfiles/leeme.txt": "nuevo\n"}, "perfiles"),
                 ({"datos": "un archivo del colega\n"}, {"datos/uno.txt": "nuevo\n"}, "datos"),
                 ({"notas/mias.txt": "del colega\n"}, {"notas": "ahora un archivo\n"}, "notas"))
        for k, (propio, trae, tramo) in enumerate(casos):
            with self.subTest(tramo=tramo):
                r = Repos(self.raiz / f"r{k}")
                viejo = r.head()
                r.escribir(propio, r.clon)
                r.publicar("v2", trae)
                codigo, datos, _ = r.actualizar()
                self.assertEqual((datos["estado"], r.head()), ("sin-actualizar", viejo))
                self.assertIn(f"la versión nueva trae «{tramo}»", datos["motivo"])
                for ruta, texto in propio.items():
                    self.assertEqual(r.leer(ruta), texto)

    def test_lo_que_ya_versionaba_la_vieja_no_cuenta_como_propio(self):
        # Una carpeta del programa que gana un archivo, y un archivo del programa que pasa a carpeta: los mueve git.
        r = self.repos()
        r.publicar("v2", {"tests/uno.py": "1\n", "doc": "archivo\n"})
        r.actualizar()
        nuevo = r.publicar("v3", {"tests/dos.py": "2\n", "doc/x.txt": "x\n"}, quitar=["doc"])
        codigo, datos, _ = r.actualizar()
        self.assertEqual((datos["estado"], r.head(), r.leer("tests/dos.py"), r.leer("doc/x.txt")),
                         ("actualizada", nuevo, "2\n", "x\n"))

    def test_una_operacion_de_git_a_medias_no_se_toca(self):
        for op in ("MERGE_HEAD", "index.lock", "rebase-merge"):
            with self.subTest(op=op):
                r = Repos(self.raiz / op)
                viejo = r.head()
                p = r.clon / ".git" / op
                if op == "rebase-merge":
                    p.mkdir()
                else:
                    p.write_bytes(viejo.encode() + b"\n")
                r.publicar("v2", {"AQUASHIELD.py": "version = 2\n"})
                codigo, datos, _ = r.actualizar()
                self.assertEqual((datos["estado"], r.head(), r.leer("AQUASHIELD.py")),
                                 ("sin-actualizar", viejo, "version = 1\n"))
                self.assertIn(op, datos["motivo"])

    def test_un_archivo_abierto_vuelve_todo_a_la_version_que_tenia(self):
        # Medido en el encargo 60: git no puede quitar un archivo abierto por otro programa, deja la rama en la versión
        # vieja y ya escribió los anteriores. El actualizador los vuelve a la vieja, y el programa abre con ella.
        r = self.repos()
        viejo = r.head()
        r.publicar("v2", {"AQUASHIELD.py": "version = 2\n", "LEEME.md": "dos\n", "agregado.txt": "agregado\n"})
        abierto = open(r.clon / "LEEME.md", "rb")
        try:
            codigo, datos, _ = r.actualizar()
        finally:
            abierto.close()
        self.assertEqual((codigo, datos["estado"], r.head()), (0, "sin-actualizar", viejo))
        self.assertEqual((r.leer("AQUASHIELD.py"), r.leer("LEEME.md"), (r.clon / "agregado.txt").exists()),
                         ("version = 1\n", "uno\n", False))
        self.assertIn("y dejé los archivos como estaban", datos["motivo"])
        self.assertEqual(r.git(r.clon, "status", "--porcelain", "--untracked-files=no"), "")
        # Cerrado el archivo, la vez siguiente actualiza.
        codigo, datos, _ = r.actualizar()
        self.assertEqual((datos["estado"], r.leer("LEEME.md")), ("actualizada", "dos\n"))

    def test_no_pide_ni_guarda_credenciales(self):
        # Un origen que pide usuario y clave (un servidor local que contesta 401): con el ayudante de credenciales del
        # equipo y la consola apagados, git falla enseguida, sin preguntar ni guardar nada.
        class PideClave(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(401)
                self.send_header("WWW-Authenticate", 'Basic realm="inventado"')
                self.send_header("Content-Length", "0")
                self.end_headers()

            def log_message(self, *a):
                pass
        srv = ThreadingHTTPServer(("127.0.0.1", 0), PideClave)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.shutdown)
        r = self.repos()
        viejo = r.head()
        r.git(r.clon, "remote", "set-url", "origin", f"http://127.0.0.1:{srv.server_address[1]}/repo.git")
        # Un ayudante de credenciales inventado en el clon, como el del equipo: si git lo llamara, dejaría su marca.
        marca = r.raiz / "ayudante_llamado.txt"
        ayudante = r.raiz / "ayudante.py"
        ayudante.write_bytes(f"open({str(marca)!r}, 'a').write('llamado')\n".encode())
        r.git(r.clon, "config", "--local", "credential.helper", f"!python '{ayudante.as_posix()}'")
        inicio = time.time()
        codigo, datos, _ = r.actualizar(timeout=90)
        self.assertLess(time.time() - inicio, 60)
        self.assertEqual((codigo, datos["estado"], r.head()), (0, "sin-actualizar", viejo))
        self.assertIn("no pude buscar la versión nueva", datos["motivo"])
        self.assertFalse(marca.exists(), "git le pidió la clave al ayudante de credenciales")
        # El control: el mismo git, sin lo que hace el actualizador, sí lo llama.
        soporte.hijo(["git", "fetch", "origin"], r.clon, timeout=60,
                     env_extra={"GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never",
                                "GIT_CEILING_DIRECTORIES": str(r.raiz)})
        self.assertTrue(marca.exists(), "el control no llamó al ayudante: la prueba no lo vería")

    def test_una_carpeta_que_no_es_un_clon_no_se_actualiza(self):
        carpeta = self.raiz / "suelta"
        carpeta.mkdir()
        codigo, salida, _ = soporte.hijo(["python", str(ACTUALIZAR), "--carpeta", str(carpeta)], self.raiz,
                                         env_extra={"GIT_CEILING_DIRECTORIES": str(self.raiz)})
        datos = json.loads((carpeta / "logs" / "actualizacion.json").read_bytes().decode("utf-8"))
        self.assertEqual((codigo, datos["estado"]), (0, "no-aplica"))

    def test_sin_argumentos_actualiza_su_propia_carpeta(self):
        # Como lo corre el .bat: «python actualizar.py», sin argumentos. Desde otra carpeta, para que se vea que usa la
        # suya y no aquella desde donde lo llaman.
        r = self.repos()
        shutil.copyfile(ACTUALIZAR, r.trabajo / "actualizar.py")
        r.publicar("con el actualizador")
        r.actualizar()
        nuevo = r.publicar("v3", {"AQUASHIELD.py": "version = 3\n"})
        codigo, salida, _ = soporte.hijo(["python", str(r.clon / "actualizar.py")], r.raiz,
                                         env_extra={"GIT_CEILING_DIRECTORIES": str(r.raiz)})
        self.assertEqual((codigo, r.head(), r.leer("AQUASHIELD.py")), (0, nuevo, "version = 3\n"))


def sin_bloque(bat):
    """El mismo .bat línea por línea: sin el «(» del bloque, su «)» final ni su sangría (el control)."""
    lineas = bat.split("\n")
    i, j = lineas.index("("), len(lineas) - 1 - lineas[::-1].index(")")
    return "\n".join(lineas[:i] + [x[2:] if x.startswith("  ") else x for x in lineas[i + 1:j]] + lineas[j + 1:])


def sin_chequeo(bat):
    """El mismo .bat sin el freno del código 11 de preparar_entorno.py, el de «no se puede abrir» (el control)."""
    sin = bat.replace("  if errorlevel 11 (\n    echo.\n    pause\n    exit /b 1\n  )\n", "", 1)
    assert sin != bat, "no encontré el freno del código 11 en el .bat"
    return sin


def sin_red_de_seguridad(bat):
    """El mismo .bat sin la mirada al Python del equipo cuando preparar_entorno.py falla por algo imprevisto (el control)."""
    sin = bat.replace('    python -c "import playwright.sync_api, openpyxl" 2>nul\n    if errorlevel 1 (\n',
                      "    if 1==0 (\n", 1)
    assert sin != bat, "no encontré la mirada al Python del equipo en el .bat"
    return sin


def correr(args, cwd, env_extra, timeout=60):
    """Como soporte.hijo, con la entrada vacía: «pause» no espera una tecla."""
    env = {k: v for k, v in os.environ.items() if k != soporte.LLAVE_ENTORNO}
    env.update(env_extra, PYTHONIOENCODING="utf-8")
    p = soporte._POPEN(args, cwd=str(cwd), env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    out, err = p.communicate(timeout=timeout)
    return p.returncode, out.decode("utf-8", "replace"), err.decode("utf-8", "replace")


class TestLosLanzadores(unittest.TestCase):
    """Los dos .bat corren el actualizador y el preparador del entorno antes de abrir el panel, en un solo bloque que
    cmd lee entero."""
    BATS = (("Iniciar AQUASHIELD.bat", "AQUASHIELD.py"), ("Iniciar AQUASHIELD_EMISION.bat", "AQUASHIELD_EMISION.py"))
    PYTHON_3_11 = 'python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul'
    PATH_DEL_VENV = r'set "PATH=%~dp0.venv\Scripts;%PATH:"=%"'

    def test_el_bat_actualiza_antes_de_abrir_y_todo_en_un_bloque(self):
        for nombre, programa in self.BATS:
            with self.subTest(bat=nombre):
                b = (soporte.FUENTES / nombre).read_bytes()
                self.assertTrue(all(c < 128 for c in b), "el .bat va en ASCII")
                lineas = [x.strip() for x in b.decode("ascii").splitlines()]
                abre, cierra = lineas.index("("), len(lineas) - 1 - lineas[::-1].index(")")
                bloque = lineas[abre + 1:cierra]
                self.assertEqual([x for x in lineas[:abre] if not x.upper().startswith("REM")],
                                 ["@echo off", 'cd /d "%~dp0"'])
                self.assertEqual(lineas[cierra + 1:], [])
                inicio = f'start "" pythonw "{programa}"'
                self.assertEqual(bloque[-2:], [inicio, "exit /b 0"])
                i = bloque.index("python actualizar.py")
                self.assertEqual(bloque[i + 1:i + 5], ["if errorlevel 3 (", "pause", "exit /b 3", ")"])
                # Un paréntesis en un comentario del bloque lo cerraría antes de tiempo, y uno en un echo, también.
                self.assertEqual([x for x in bloque if x.upper().startswith(("REM", "ECHO"))
                                  and ("(" in x or ")" in x)], [])
                # Sin Python 3.11 o más nuevo no hay actualizador ni preparador: se mira antes, y se ofrece instalarlo.
                self.assertLess(bloque.index(self.PYTHON_3_11), i)
                # El preparador va después del actualizador (la versión nueva puede traer otros requisitos) y antes de
                # abrir. Con el código 11 no se abre; con el 10 se abre con el Python del equipo; con 0, con el .venv.
                k = bloque.index("python -I preparar_entorno.py")
                self.assertLess(i, k)
                # Un código negativo o de 12 en adelante pasa a 1, la falla imprevista; el 11, no abrir; el 10, el del equipo.
                self.assertEqual(bloque[k + 1:k + 9], ["if not errorlevel 0 cmd /c exit 1", "if errorlevel 12 cmd /c exit 1",
                                                       "if errorlevel 11 (", "echo.", "pause", "exit /b 1", ")",
                                                       "if errorlevel 10 ("])
                self.assertLess(bloque.index(self.PATH_DEL_VENV, k), bloque.index(inicio))
                # Python se ofrece de 64 bits: en un equipo ARM64 winget traería el ARM64, que requirements.txt no cubre.
                self.assertEqual([("--architecture x64" in x) for x in bloque if x.startswith("winget install --id Python")],
                                 [True])
                # El .bat ya no instala nada por su cuenta: lo hace el preparador, con hash.
                self.assertEqual([x for x in bloque if "pip" in x.lower() and not x.upper().startswith(("REM", "ECHO"))],
                                 [])

    def test_los_dos_bat_son_el_mismo_salvo_el_modo(self):
        # Un arreglo en uno que no llega al otro deja a quien emite con un lanzador distinto del que se probó.
        seguro, emision = [(soporte.FUENTES / n).read_bytes().decode("ascii").split("\n") for n, _ in self.BATS]
        self.assertEqual(len(seguro), len(emision))
        self.assertEqual([(a.strip(), b.strip()) for a, b in zip(seguro, emision) if a != b], [
            ("REM  AQUASHIELD - Lanzador Principal (Modo Seguro)", "REM  AQUASHIELD - Lanzador Principal (Modo Emision Real)"),
            ("REM  Doble clic para abrir el panel de control web.",
             "REM  Doble clic para abrir el panel en modo emision sin consola."),
            ("REM  Las reservas se completan al 100% y se detienen antes de emitir.",
             "REM  Las reservas seleccionadas se enviaran y confirmaran formalmente."),
            ("title AquaShield - Modulo Reservas", "title AquaShield - Modulo Reservas - EMISION"),
            ("REM Abre el panel, sin ventana negra de consola", "REM Abre el panel en modo emision, sin ventana negra de consola"),
            ('start "" pythonw "AQUASHIELD.py"', 'start "" pythonw "AQUASHIELD_EMISION.py"')])

    def test_en_cmd_abre_la_version_nueva_aunque_la_actualizacion_reescriba_el_bat(self):
        # El camino real: cmd corre el .bat en un clon inventado, y la actualización que corre adentro le agrega 40
        # líneas a la cabecera del propio .bat. cmd vuelve a abrir el archivo después de cada comando y sigue desde el
        # byte donde quedó; con todo en un bloque, ya lo leyó entero. El programa es un sustituto que anota su versión.
        # Control (medido en el encargo 60): el mismo .bat sin el bloque retoma en el nuevo y corre un pedazo de
        # comentario.
        raiz = carpeta_corta("aq_bat_")
        self.addCleanup(borrar, raiz)
        for k, (nombre, programa) in enumerate((("Iniciar AQUASHIELD.bat", "AQUASHIELD.py"),
                                                ("Iniciar AQUASHIELD_EMISION.bat", "AQUASHIELD_EMISION.py"))):
            bat = (soporte.FUENTES / nombre).read_bytes().decode("ascii")
            for bloque in (True, False):
                with self.subTest(bat=nombre, bloque=bloque):
                    codigo, marca, errores = self.correr_bat(raiz / f"{k}{bloque}", nombre, programa,
                                                             bat if bloque else sin_bloque(bat))
                    if bloque:
                        self.assertEqual((codigo, marca, errores), (0, ["2"], []))
                    else:
                        self.assertNotEqual((codigo, marca, errores), (0, ["2"], []))

    def correr_bat(self, raiz, nombre, programa, bat):
        r = Repos(raiz)
        shutil.copyfile(ACTUALIZAR, r.trabajo / "actualizar.py")
        sustituto = ('import pathlib\nVERSION = "{}"\nwith open(pathlib.Path(__file__).resolve().parent / '
                     '"marca.txt", "a", encoding="utf-8") as f:\n    f.write(VERSION + "\\n")\n')
        # El preparador, aquí, dice que abra con el Python del equipo (10): esta prueba es de cómo cmd lee el .bat. Lo
        # que hace el preparador de verdad, en test_entorno.
        preparador = "import sys\nsys.exit(10)\n"
        (r.trabajo / ".gitignore").write_bytes((GITIGNORE + f"!/{nombre}\n!/{programa}\n!/preparar_entorno.py\n").encode())
        r.publicar("con el .bat", {nombre: bat, programa: sustituto.format(1), "preparar_entorno.py": preparador})
        r.git(r.trabajo, "push", "-q", "origin", "main:estable")
        r.git(r.clon, "pull", "-q", "--ff-only")
        lineas = bat.split("\n")
        nuevo = "\n".join(lineas[:2] + [f"REM linea de comentario agregada en la version nueva {n}" for n in range(40)]
                          + lineas[2:])
        r.publicar("v2", {nombre: nuevo, programa: sustituto.format(2)})
        codigo, _, error = soporte.hijo(["cmd", "/d", "/c", str(r.clon / nombre)], r.clon, timeout=180,
                                        env_extra={"GIT_CEILING_DIRECTORIES": str(raiz)})
        marca = r.clon / "marca.txt"
        for _ in range(60):                    # pythonw corre aparte: se espera su marca
            if marca.exists():
                break
            time.sleep(0.5)
        time.sleep(2)                          # por si cmd lo abriera otra vez
        errores = [x for x in error.splitlines() if "no se reconoce" in x or "inesperado" in x]
        return codigo, (marca.read_text(encoding="utf-8").split() if marca.exists() else None), errores

    def python_del_path(self):
        """El `python` que encuentra cmd en el PATH, el que corre el .bat. No el de "python" en un Popen: Windows busca
        primero en la carpeta del programa que lo lanza, y aquí es la del Python de las pruebas, que trae las librerías."""
        python = shutil.which("python")
        if python is None:
            self.skipTest("no hay un python en el PATH")
        return python

    def entorno_sin_red(self, raiz):
        """Pip sin red de verdad: le pregunta a un puerto local donde nadie escucha. Sin la configuración ni la caché de
        quien corre la prueba."""
        # PYTHONUSERBASE vacío: el Python de la Store, que corre estas pruebas, deja puesto el suyo en el entorno de sus
        # hijos, y -E no lo ignora (medido el 2026-10-26: el Python de python.org importaba el playwright de la Store).
        (raiz / "u").mkdir(exist_ok=True)
        return {"PYTHONUSERBASE": str(raiz / "u"), "PIP_INDEX_URL": "http://127.0.0.1:9/simple", "PIP_RETRIES": "0",
                "PIP_TIMEOUT": "3", "PIP_DISABLE_PIP_VERSION_CHECK": "1", "PIP_NO_INPUT": "1",
                "PIP_CONFIG_FILE": os.devnull, "PIP_CACHE_DIR": str(raiz / "cache"),
                "GIT_CEILING_DIRECTORIES": str(raiz)}

    def carpeta_del_programa(self, raiz, nombre, programa, bat, preparador=None):
        """Una carpeta con el .bat, el actualizador, el preparador (el de verdad, o el que se diga) y un programa
        sustituto que anota que abrió."""
        carpeta = raiz / f"p{len(list(raiz.glob('p*')))}"
        carpeta.mkdir()
        shutil.copyfile(ACTUALIZAR, carpeta / "actualizar.py")
        if preparador is None:
            shutil.copyfile(PREPARADOR, carpeta / "preparar_entorno.py")
            shutil.copyfile(REQUISITOS, carpeta / "requirements.txt")
        else:
            (carpeta / "preparar_entorno.py").write_bytes(preparador.encode())
        sustituto = 'import pathlib\n(pathlib.Path(__file__).resolve().parent / "marca.txt").write_text("abrio")\n'
        (carpeta / programa).write_bytes(sustituto.encode())
        (carpeta / nombre).write_bytes(bat.encode("ascii"))
        return carpeta

    def abrio(self, carpeta, espera):
        """True si el programa sustituto anotó que abrió (pythonw corre aparte: se espera su marca)."""
        for _ in range(int(espera * 2)):
            if (carpeta / "marca.txt").exists():
                return True
            time.sleep(0.5)
        return False

    def test_sin_las_librerias_lo_dice_y_no_abre(self):
        # Medido en el encargo 61, en un clon nuevo con un Python sin las librerías de este equipo y sin red: pip no las
        # instala, pythonw muere al importar playwright, y el .bat salía sin decir nada: no se abría ningún panel. Desde
        # el encargo 84 lo dice el preparador (preparar_entorno.py) y el .bat no abre y espera una tecla. Control: el
        # mismo .bat sin ese freno abre el programa igual (aquí, un sustituto que anota que abrió).
        raiz = carpeta_corta("aq_lib_")
        self.addCleanup(borrar, raiz)
        env = self.entorno_sin_red(raiz)
        if correr([self.python_del_path(), "-E", "-c", "import playwright.sync_api, openpyxl"], raiz, env)[0] == 0:
            self.skipTest("el python del PATH trae playwright y openpyxl: el preparador abriría con él")
        for nombre, programa in self.BATS:
            bat = (soporte.FUENTES / nombre).read_bytes().decode("ascii")
            for freno in (True, False):
                with self.subTest(bat=nombre, freno=freno):
                    carpeta = self.carpeta_del_programa(raiz, nombre, programa, bat if freno else sin_chequeo(bat))
                    _, salida, _ = correr(["cmd", "/d", "/c", str(carpeta / nombre)], carpeta, env, timeout=180)
                    dice = "No abrí AQUASHIELD: faltan «playwright» y «openpyxl» y no se pudo instalar." in salida
                    self.assertEqual((dice, self.abrio(carpeta, 3 if freno else 30)), (True, not freno), salida)

    def test_si_el_preparador_falla_por_algo_imprevisto_abre_solo_con_un_python_completo(self):
        # Un error del propio preparador (un archivo roto en una actualización, por ejemplo) no deja sin abrir a quien ya
        # tenía todo en el Python del equipo, y no abre un panel que moriría al importar playwright. Las librerías del
        # equipo, aquí, son módulos inventados en PYTHONPATH.
        raiz = carpeta_corta("aq_imp_")
        self.addCleanup(borrar, raiz)
        env = self.entorno_sin_red(raiz)
        falsas = raiz / "falsas"
        for ruta in ("playwright/__init__.py", "playwright/sync_api.py", "openpyxl/__init__.py"):
            (falsas / ruta).parent.mkdir(parents=True, exist_ok=True)
            (falsas / ruta).write_bytes(b"")
        con, sin = dict(env, PYTHONPATH=str(falsas)), dict(env, PYTHONPATH=str(raiz / "nada"))
        if correr([self.python_del_path(), "-c", "import playwright.sync_api, openpyxl"], raiz, sin)[0] == 0:
            self.skipTest("el python del PATH trae playwright y openpyxl")
        nombre, programa = self.BATS[0]
        bat = (soporte.FUENTES / nombre).read_bytes().decode("ascii")
        roto, sale_255 = "import sys\nsys.exit(1)\n", "import sys\nsys.exit(255)\n"
        # El 255 (y todo código de 12 en adelante) es también una falla imprevista, no el 11 de «no se puede abrir».
        for caso, entorno, bat_probado, abre, preparador in (
                ("python completo", con, bat, True, roto),
                ("python sin las librerias", sin, bat, False, roto),
                ("control: sin la mirada", sin, sin_red_de_seguridad(bat), True, roto),
                ("codigo 255 con python completo", con, bat, True, sale_255),
                ("codigo 255 con python sin las librerias", sin, bat, False, sale_255)):
            with self.subTest(caso=caso):
                carpeta = self.carpeta_del_programa(raiz, nombre, programa, bat_probado, preparador=preparador)
                _, salida, _ = correr(["cmd", "/d", "/c", str(carpeta / nombre)], carpeta, entorno, timeout=180)
                dice = "fallo la preparacion de las librerias" in salida
                self.assertEqual((self.abrio(carpeta, 30 if abre else 3), dice), (abre, not abre), salida)

    def test_sin_git_pregunta_una_sola_vez(self):
        # Sin Git (y con un winget que no instala nada), cada inicio esperaba la respuesta de `choice` hasta 60 s en una
        # consola de verdad (revisión de código del encargo 84; con la entrada de las pruebas, vacía, contesta enseguida y
        # no se ve). Ahora pregunta una vez y deja una marca en logs\. El PATH de la prueba trae solo el Python, el sistema
        # y el winget falso.
        raiz = carpeta_corta("aq_git_")
        self.addCleanup(borrar, raiz)
        python = self.python_del_path()
        raiz_windows = os.environ["SystemRoot"]
        falso = raiz / "winget_falso"
        falso.mkdir()
        (falso / "winget.cmd").write_bytes(b"@echo WINGET_FALSO %*\r\n@exit /b 1\r\n")
        env = dict(self.entorno_sin_red(raiz), PATH=os.pathsep.join([os.path.dirname(python), str(falso),
                                                                      os.path.join(raiz_windows, "System32"), raiz_windows]))
        nombre, programa = self.BATS[0]
        bat = (soporte.FUENTES / nombre).read_bytes().decode("ascii")
        carpeta = self.carpeta_del_programa(raiz, nombre, programa, bat, preparador="import sys\nsys.exit(10)\n")
        dicen = []
        for vez in (1, 2):
            (carpeta / "marca.txt").unlink(missing_ok=True)
            _, salida, _ = correr(["cmd", "/d", "/c", str(carpeta / nombre)], carpeta, env, timeout=180)
            self.assertTrue(self.abrio(carpeta, 30), salida)
            dicen.append("Este equipo no tiene Git" in salida)
        self.assertEqual(dicen, [True, False])
        self.assertTrue((carpeta / "logs" / ".git-preguntado").is_file())

    def test_gitignore_versiona_el_actualizador(self):
        lineas = (soporte.FUENTES / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("!/actualizar.py", lineas)


class TestAvisoEnElPanel(soporte.CasoAQ):
    """El panel muestra lo que dijo actualizar.py, solo si es de este inicio."""

    def escribir(self, datos):
        p = self.sb / "logs" / "actualizacion.json"
        p.parent.mkdir(exist_ok=True)
        p.write_bytes(json.dumps(datos).encode("utf-8") if isinstance(datos, dict) else datos)
        self.addCleanup(lambda: p.unlink() if p.exists() else None)

    def test_lo_dice_si_es_de_este_inicio(self):
        m = self.mod
        self.escribir({"texto": "⚠ No actualicé AQUASHIELD:\n  sin red.", "cuando": 1000.0})
        self.assertEqual(m._aviso_de_actualizacion(ahora=1000.0 + 599), "⚠ No actualicé AQUASHIELD: sin red.")
        for ahora in (1000.0 + 601, 999.0):
            with self.subTest(ahora=ahora):
                self.assertIsNone(m._aviso_de_actualizacion(ahora=ahora))

    def test_sin_archivo_o_malformado_no_dice_nada(self):
        m = self.mod
        self.assertIsNone(m._aviso_de_actualizacion(ahora=1000.0))
        for datos in (b"no es json", {"texto": "", "cuando": 1000.0}, {"texto": 3, "cuando": 1000.0},
                      {"cuando": 1000.0}, {"texto": "x", "cuando": "mañana"}):
            with self.subTest(datos=datos):
                self.escribir(datos)
                self.assertIsNone(m._aviso_de_actualizacion(ahora=1000.0))

    def test_el_panel_lo_muestra_al_abrir(self):
        # Lo llama lanzar_web después de tomar su puerto y antes de servir, por el aviso de siempre.
        fuente = (soporte.FUENTES / "AQUASHIELD.py").read_text(encoding="utf-8")
        cuerpo = fuente[fuente.index("def lanzar_web("):fuente.index("srv.serve_forever()")]
        llamada = "    aviso = _aviso_de_actualizacion()\n    if aviso:\n        _avisar_en_pantalla_y_log(aviso)\n"
        self.assertIn(llamada, cuerpo)
        self.assertLess(cuerpo.index("_SRV_ACTUAL = srv"), cuerpo.index("aviso = _aviso_de_actualizacion()"))


if __name__ == "__main__":
    unittest.main()
