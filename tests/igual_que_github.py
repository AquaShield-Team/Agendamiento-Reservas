# -*- coding: utf-8 -*-
"""¿Corre este equipo lo mismo que GitHub? (pedido de Marcelo, encargo 93, CICLO-named-customer-rutas-cma-y-version.md)

Clona la rama desde su remoto (origin, el repo público, sin clave: sin ayudante de credenciales y sin preguntas) DENTRO
de la carpeta del programa, en .trabajo/igual-que-github/<rama>-<fecha>/ (nada fuera), y compara:
  - el commit de la rama en GitHub con el de la rama local, y sus árboles;
  - los archivos versionados, byte a byte, entre el clon y la carpeta del programa (lo que corre de verdad);
  - los cambios sin commitear de la carpeta del programa (en archivos versionados).
Después corre la suite (tests/correr.py) en el clon, con el temporal en una carpeta propia junto al clon, por su nombre
corto (sin espacios: con uno, las pruebas del .venv caen; CLAUDE.md, «Red de verificación») y con el techo de git ahí
(GIT_CEILING_DIRECTORIES: sin él, git sube al repo del programa desde las carpetas de las pruebas). El plazo de la suite
entera pasa de 1.200 a 7.200 s, como en .trabajo/e92/con_mas_plazo.py. Si todo es igual y la suite pasa, borra el clon
y su temporal (salvo con --dejar); si no, los deja y dice dónde.

Sale con 0 si es igual y la suite pasa (o se pidió --sin-suite), 1 si algo difiere o la suite falla, y 2 si no pudo
comparar (sin el remoto, sin la rama, el clon falló). Imprime hashes cortos, cuentas y rutas del repo: nada de datos.
Corre con el Python que corre la suite (en este equipo, el de la Tienda de Microsoft: CLAUDE.md, «Interfaz y marca»).

Uso: python tests/igual_que_github.py [--rama RAMA] [--sin-suite] [--dejar]"""
import argparse
import ctypes
import importlib.util
import os
import re
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path

POPEN = subprocess.Popen          # las pruebas ponen aquí el Popen verdadero (el arnés pone una trampa en el de subprocess)
RAIZ = Path(__file__).resolve().parent.parent
PLAZO_GIT = 600                   # s: clonar el repo público tardó 1,4 s el 2026-10-13 (encargo 61)
PLAZO_SUITE = 3 * 3600            # s: la suite tardó de 40 a 60 minutos con el equipo cargado (encargos 92 y 93)
RAMA = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]*")
TASKKILL = str(Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "taskkill.exe")


def _correr(args, cwd=None, env=None, plazo=PLAZO_GIT):
    """Corre un proceso y devuelve (código, salida, error) en texto. Al vencer el plazo cierra su árbol (taskkill /T: un
    git lanzado desde aquí puede ser un lanzador con un hijo; CLAUDE.md de la máquina) y devuelve el código 124."""
    p = POPEN(args, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        out, err = p.communicate(timeout=plazo)
    except subprocess.TimeoutExpired:
        POPEN([TASKKILL, "/T", "/F", "/PID", str(p.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).wait()
        out, err = p.communicate()
        return 124, out.decode("utf-8", "replace"), err.decode("utf-8", "replace") + f" (venció el plazo de {plazo} s)"
    return p.returncode, out.decode("utf-8", "replace"), err.decode("utf-8", "replace")


def _entorno_git():
    """Sin clave y sin preguntas: el remoto es público, y uno que pida clave falla enseguida (como actualizar.py)."""
    return dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")


def git(carpeta, *args):
    """git en 'carpeta', sin ayudante de credenciales. Devuelve (código, salida sin espacios en los extremos)."""
    rc, out, _ = _correr(["git", "-C", str(carpeta), "-c", "credential.helper=", *args], env=_entorno_git())
    return rc, out.strip()


def corto(ruta):
    """El nombre corto (8.3) de 'ruta', sin espacios, para TEMP; si Windows no lo da, la ruta como está."""
    try:
        buf = ctypes.create_unicode_buffer(32768)
        n = ctypes.windll.kernel32.GetShortPathNameW(str(ruta), buf, len(buf))
        return buf.value if 0 < n < len(buf) else str(ruta)
    except (AttributeError, OSError):
        return str(ruta)


def distintos_en_bytes(clon, local, archivos):
    """De los archivos versionados del clon ('archivos', rutas con «/»), los que en la carpeta local no están o no son
    byte a byte iguales. Devuelve (faltan, distintos), listas de rutas."""
    faltan, distintos = [], []
    for rel in archivos:
        a, b = Path(clon) / rel, Path(local) / rel
        if not b.is_file():
            faltan.append(rel)
        elif a.read_bytes() != b.read_bytes():
            distintos.append(rel)
    return faltan, distintos


def _borrar(ruta):
    """Borra una carpeta de este programa (el clon o su temporal), quitando el solo lectura de los archivos de git
    (CLAUDE.md de la máquina: shutil.rmtree de un clon da WinError 5). No sigue enlaces: los quita."""
    def solo_escritura(func, p, _):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    if Path(ruta).exists():
        shutil.rmtree(ruta, onexc=solo_escritura)


def comparar(raiz, rama, sin_suite=False, dejar=False, salida=print):
    """Lo que hace la herramienta (main la llama con los argumentos). Devuelve el código de salida."""
    raiz = Path(raiz).resolve()
    rc, url = git(raiz, "remote", "get-url", "origin")
    if rc or not url:
        salida("No pude leer el remoto origin de la carpeta del programa: no comparo.")
        return 2
    if not rama:
        rc, rama = git(raiz, "rev-parse", "--abbrev-ref", "HEAD")
        if rc or rama == "HEAD":
            salida("La carpeta del programa no está en una rama: dime cuál con --rama.")
            return 2
    # Solo un nombre de rama: letras ASCII, cifras y «._/-», sin empezar con «-» (git la tomaría por una opción) y sin
    # «..». Así la carpeta del clon, con «/» como «_», queda siempre dentro de .trabajo/igual-que-github/.
    if not RAMA.fullmatch(rama) or ".." in rama:
        salida(f"«{rama[:60]}» no tiene la forma de una rama (letras, cifras y «._/-»): no comparo.")
        return 2
    trabajo = raiz / ".trabajo" / "igual-que-github"
    sello = time.strftime("%Y%m%d-%H%M%S")
    clon, tmp = trabajo / f"{rama.replace('/', '_')}-{sello}", trabajo / f"tmp-{sello}"
    trabajo.mkdir(parents=True, exist_ok=True)
    salida(f"Clono «{rama}» desde {url} en {clon.relative_to(raiz)} …")
    rc, _, err = _correr(["git", "-c", "credential.helper=", "clone", "--quiet", "--no-hardlinks", "--single-branch",
                          "--branch", rama, "--", url, str(clon)], env=_entorno_git())
    if rc:
        salida(f"El clon falló ({rc}): {err.strip()[:200]}")
        return 2
    _, gh = git(clon, "rev-parse", "HEAD")
    _, gh_arbol = git(clon, "rev-parse", "HEAD^{tree}")
    rc_local, local = git(raiz, "rev-parse", "--verify", "--quiet", rama)
    _, local_arbol = git(raiz, "rev-parse", "--verify", "--quiet", rama + "^{tree}")
    _, cabeza = git(raiz, "rev-parse", "HEAD")
    _, cambios = git(raiz, "status", "--porcelain", "--untracked-files=no")
    _, listado = git(clon, "ls-files", "-z")
    archivos = [a for a in listado.split("\0") if a]
    faltan, distintos = distintos_en_bytes(clon, raiz, archivos)
    cambios = [c for c in cambios.splitlines() if c.strip()]
    igual_commit = bool(gh) and gh == local
    igual_arbol = bool(gh_arbol) and gh_arbol == local_arbol
    salida(f"GitHub «{rama}»: {gh[:7]} · local «{rama}»: {local[:7] if not rc_local else 'no existe'}"
           f"{'' if cabeza == local else f' (la carpeta está en {cabeza[:7]})'}")
    salida(f"commit: {'igual' if igual_commit else 'DISTINTO'} · árbol: {'igual' if igual_arbol else 'DISTINTO'}")
    salida(f"archivos versionados: {len(archivos)} · faltan en la carpeta: {len(faltan)} · distintos en bytes: "
           f"{len(distintos)} · cambios sin commitear: {len(cambios)}")
    for rel in (faltan + distintos)[:20]:
        salida(f"   {'falta' if rel in faltan else 'distinto'}: {rel}")
    for c in cambios[:20]:
        salida(f"   sin commitear: {c}")
    # El árbol se muestra, pero no decide: con el mismo commit es el mismo.
    igual = igual_commit and cabeza == local and not (faltan or distintos or cambios)
    suite_ok = True
    if not sin_suite:
        tmp.mkdir(parents=True, exist_ok=True)
        t = corto(tmp)
        env = dict(os.environ, TEMP=t, TMP=t, TMPDIR=t, GIT_CEILING_DIRECTORIES=t, PYTHONIOENCODING="utf-8")
        salida(f"Corro la suite en el clon (de 40 a 60 minutos; el temporal, en {tmp.relative_to(raiz)}) …")
        rc, out, err = _correr([sys.executable, str(Path(__file__).resolve()), "--correr-suite", str(clon / "tests")],
                               cwd=str(clon), env=env, plazo=PLAZO_SUITE)
        (trabajo / f"suite-{sello}.txt").write_text(out + err, encoding="utf-8")
        resultado = next((l for l in reversed(out.splitlines()) if l.startswith("RESULTADO:")), "sin línea RESULTADO")
        suite_ok = rc == 0 and resultado == "RESULTADO: OK"
        salida(f"suite en el clon: {resultado} (código {rc}); la salida entera, en "
               f"{(trabajo / f'suite-{sello}.txt').relative_to(raiz)}")
    salida("IGUAL: este equipo corre lo mismo que GitHub" + ("" if sin_suite else ", y la suite pasa en el clon")
           if igual and suite_ok else "DISTINTO: mira las líneas de arriba")
    if igual and suite_ok and not dejar:
        _borrar(clon)
        _borrar(tmp)
    else:
        salida(f"El clon queda en {clon.relative_to(raiz)}")
    return 0 if igual and suite_ok else 1


def _correr_suite(tests):
    """El modo hijo: corre <tests>/correr.py tal cual (su main(): la foto de los originales, la suite y el resultado),
    con un solo cambio, el de .trabajo/e92/con_mas_plazo.py: la corrida de unittest con el plazo por omisión (1.200 s)
    recibe 7.200. Lo carga por su ruta y con otro nombre: así no se confunde con un «correr» ya importado."""
    tests = Path(tests).resolve()
    sys.path.insert(0, str(tests))
    spec = importlib.util.spec_from_file_location("correr_del_clon", tests / "correr.py")
    correr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(correr)
    original = correr.correr_unittest

    def con_mas_plazo(ids=None, fuentes=None, timeout=1200):
        return original(ids, fuentes, 7200 if timeout == 1200 else timeout)
    correr.correr_unittest = con_mas_plazo
    sys.argv = [str(tests / "correr.py")]
    return correr.main()


def main(argv=None):
    a = argparse.ArgumentParser(description="¿Corre este equipo lo mismo que GitHub?")
    a.add_argument("--rama", default="", help="la rama a comparar (por omisión, la de la carpeta del programa)")
    a.add_argument("--sin-suite", action="store_true", help="solo compara, sin correr la suite en el clon")
    a.add_argument("--dejar", action="store_true", help="no borra el clon aunque todo sea igual")
    a.add_argument("--correr-suite", default="", help=argparse.SUPPRESS)
    args = a.parse_args(argv)
    if args.correr_suite:
        return _correr_suite(args.correr_suite)
    return comparar(RAIZ, args.rama, sin_suite=args.sin_suite, dejar=args.dejar)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
