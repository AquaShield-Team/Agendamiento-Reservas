# -*- coding: utf-8 -*-
"""Corredor de la red de verificación offline.

  python tests/correr.py                la suite sobre el programa tal cual: tiene que pasar
  python tests/correr.py --mutaciones   cada defecto inyectado tiene que hacer fallar SU prueba
  python tests/correr.py --todo         las dos cosas
  --filtro TEXTO                        solo las mutaciones cuyo id o prueba contiene TEXTO

Siempre toma una foto de los originales antes y después (la raíz del proyecto,
logs/, perfiles/ y la planilla temporal del panel real); si algo cambió, falla.
No importa ni el programa ni el arnés: las pruebas corren en procesos hijos, y
las mutaciones se aplican a COPIAS de las fuentes (el original no se toca).
"""
import ast
import concurrent.futures
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

TESTS = Path(__file__).resolve().parent
RAIZ = TESTS.parent
FUENTES_PROGRAMA = ["AQUASHIELD.py", "AQUASHIELD_EMISION.py", "Iniciar AQUASHIELD.bat",
                    "Iniciar AQUASHIELD_EMISION.bat", "config.example.json"]
PLANILLA_TEMPORAL_REAL = Path(tempfile.gettempdir()) / "aquashield_planilla.xlsx"
TRABAJO = Path(tempfile.mkdtemp(prefix="aquashield_mut_"))


def _huella(p):
    try:
        st = p.stat()
        h = hashlib.sha256(p.read_bytes()).hexdigest() if st.st_size < 50_000_000 else None
        return (st.st_size, st.st_mtime_ns, h)
    except OSError:
        return "ilegible"


def foto_originales():
    foto = {}
    for p in RAIZ.iterdir():
        if p.is_file():
            foto[p.name] = _huella(p)
        elif p.is_dir() and p.name in ("logs", "perfiles"):
            for q in p.rglob("*"):
                if q.is_file():
                    foto[str(q.relative_to(RAIZ))] = _huella(q)
        elif p.is_dir() and p.name not in (".git", "tests", "__pycache__"):
            foto[p.name + "/"] = "carpeta"
    foto["<planilla temporal del panel real>"] = (_huella(PLANILLA_TEMPORAL_REAL)
                                                   if PLANILLA_TEMPORAL_REAL.exists() else None)
    return foto


def diferencias(a, b):
    out = []
    for k in sorted(set(a) | set(b)):
        if a.get(k) != b.get(k):
            out.append(f"{k}: {'nuevo' if k not in a else ('borrado' if k not in b else 'cambió')}")
    return out


def entorno_hijo(fuentes=None):
    env = {k: v for k, v in os.environ.items() if k not in ("AQUASHIELD_EMITIR", "AQUASHIELD_FUENTES")}
    env.update(PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    if fuentes:
        env["AQUASHIELD_FUENTES"] = str(fuentes)
    return env


# Windows no crea un proceso con una línea de comando de más de 32.767 caracteres (WinError 206). El control del censo
# completo nombraba todas las pruebas en una sola: 32.554 caracteres con 510, y 33.374 con 520, que ya no corrió
# (encargo 41, CICLO-origen-y-destino.md). Por eso va por tandas.
LARGO_MAXIMO = 30000


def por_tandas(ids, largo=LARGO_MAXIMO):
    """Los ids, en su orden, en tandas cuya línea de comando para unittest no pasa de 'largo' caracteres."""
    tandas, actual = [], []
    for i in ids:
        if actual and len(subprocess.list2cmdline([sys.executable, "-m", "unittest"] + actual + [i])) > largo:
            tandas.append(actual)
            actual = []
        actual.append(i)
    return tandas + [actual] if actual else tandas


def correr_unittest(ids=None, fuentes=None, timeout=1200):
    args = [sys.executable, "-m", "unittest"] + (list(ids) if ids else ["discover", "-s", ".", "-p", "test_*.py"])
    p = subprocess.run(args, cwd=TESTS, env=entorno_hijo(fuentes), capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=timeout)
    return p.returncode, p.stdout + p.stderr


def listar_pruebas():
    ids = []
    for f in sorted(TESTS.glob("test_*.py")):
        for c in ast.parse(f.read_text(encoding="utf-8")).body:
            if isinstance(c, ast.ClassDef):
                ids += [f"{f.stem}.{c.name}.{m.name}" for m in c.body
                        if isinstance(m, ast.FunctionDef) and m.name.startswith("test")]
    return ids


def preparar_fuentes(destino, mutacion=None):
    destino.mkdir(parents=True)
    for n in FUENTES_PROGRAMA:
        shutil.copyfile(RAIZ / n, destino / n)
    if mutacion:
        archivo = mutacion.get("archivo", "AQUASHIELD.py")
        texto = (RAIZ / archivo).read_bytes().decode("utf-8")
        # Una mutación puede traer varios cambios ('cambios'): sirve cuando dos piezas se
        # tapan entre sí y hay que apagar las dos para que el caso caiga.
        cambios = mutacion.get("cambios") or [(mutacion["viejo"], mutacion["nuevo"])]
        mutado = texto
        for viejo, nuevo in cambios:
            n = texto.count(viejo)
            if n != 1:
                raise ValueError(f"{mutacion['id']}: el texto viejo aparece {n} veces en {archivo}")
            mutado = mutado.replace(viejo, nuevo)
        if archivo.endswith(".py"):
            try:                      # un defecto que no compila tumbaría la prueba sin probar nada
                compile(mutado, archivo, "exec")
            except SyntaxError as e:
                raise ValueError(f"{mutacion['id']}: la mutación deja {archivo} sin compilar ({e})")
        # Un archivo en una subcarpeta (tests/sonda_secretos.py) va en la misma subcarpeta de la copia.
        (destino / archivo).parent.mkdir(parents=True, exist_ok=True)
        (destino / archivo).write_bytes(mutado.encode("utf-8"))
    return destino


def motivo(salida):
    """Primera línea de error de unittest, para auditar POR QUÉ cayó la prueba."""
    for linea in salida.splitlines():
        s = linea.strip()
        if s.startswith(("AssertionError", "soporte.EfectoReal", "EfectoReal", "ValueError", "KeyError",
                         "TypeError", "AttributeError", "FileNotFoundError", "Exception", "RuntimeError",
                         "subprocess.TimeoutExpired", "TimeoutError")):
            return s[:110]
    # Excepciones del propio programa: llegan con el nombre del módulo de la sandbox delante
    # («aquashield_prueba_3.ErrorEscritura: ...», «...ObjetivoNoEncontrado: ...»); sin esto, el motivo
    # quedaba vacío.
    for linea in salida.splitlines():
        s = linea.strip()
        if re.match(r"^[A-Za-z_][\w.]*(Error|Exception|Escritura|Encontrado)(:|$)", s):
            return s[:110]
    return ""


def huella_fuentes():
    return {n: hashlib.sha256((RAIZ / n).read_bytes()).hexdigest() for n in FUENTES_PROGRAMA}


def suite():
    t = time.time()
    rc, salida = correr_unittest()
    ultima = [l for l in salida.strip().splitlines() if l.startswith(("Ran ", "OK", "FAILED"))]
    print(f"SUITE: exit={rc} · {' · '.join(ultima)} · {time.time() - t:.0f} s")
    if rc:
        print(salida[-6000:])
    return rc == 0


def mutaciones(filtro=None):
    sys.path.insert(0, str(TESTS))
    from mutaciones import MUTACIONES
    pruebas = listar_pruebas()
    errores = []
    # Censo: toda prueba tiene al menos una mutación que debería tumbarla.
    cubiertas = {p for m in MUTACIONES for p in m["pruebas"]}
    sin_mutacion = [p for p in pruebas if p not in cubiertas]
    inexistentes = sorted(cubiertas - set(pruebas))
    ids = [m["id"] for m in MUTACIONES]
    repetidos = sorted({i for i in ids if ids.count(i) > 1})
    for texto, lista in (("pruebas sin mutación", sin_mutacion), ("pruebas nombradas que no existen", inexistentes),
                         ("ids de mutación repetidos", repetidos)):
        if lista:
            errores.append(f"{texto}: {lista}")
    elegidas = [m for m in MUTACIONES if not filtro or filtro in m["id"] or any(filtro in p for p in m["pruebas"])]
    # Control: la copia SIN mutar tiene que pasar las pruebas elegidas.
    base = preparar_fuentes(TRABAJO / "base")
    objetivo = sorted({p for m in elegidas for p in m["pruebas"]})
    tandas = por_tandas(objetivo)
    if [p for t in tandas for p in t] != objetivo:
        errores.append("las tandas del control no son las pruebas elegidas")
        return errores
    rc, salida = 0, ""
    for tanda in tandas:
        r, s = correr_unittest(tanda, fuentes=base)
        rc, salida = rc or r, salida + s
    print(f"CONTROL (copia sin mutar, {len(objetivo)} pruebas en {len(tandas)} tanda(s)): "
          f"{'pasa' if rc == 0 else 'FALLA'}")
    if rc:
        print(salida[-4000:])
        errores.append("la copia sin mutar no pasa: el mecanismo de mutación no es confiable")
        return errores
    trabajos = []
    for i, m in enumerate(elegidas):
        try:
            d = preparar_fuentes(TRABAJO / f"m{i:03d}", m)
        except ValueError as e:
            errores.append(str(e))
            continue
        trabajos += [(m["id"], p, d) for p in m["pruebas"]]

    def uno(t):
        mid, prueba, d = t
        t0 = time.time()
        try:
            rc, salida = correr_unittest([prueba], fuentes=d, timeout=240)
        except subprocess.TimeoutExpired:
            rc, salida = 124, "Exception: tiempo agotado (la prueba quedó colgada con el defecto)"
        return mid, prueba, rc, time.time() - t0, salida

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for mid, prueba, rc, seg, salida in ex.map(uno, trabajos):
            estado = "MUERDE" if rc != 0 else "NO MUERDE"
            print(f"  {estado:9} {mid:40} -> {prueba} ({seg:.0f} s)")
            if rc != 0:
                print(f"            motivo: {motivo(salida)}")
            if rc == 0:
                errores.append(f"{mid} no hace fallar {prueba}")
    print(f"MUTACIONES: {len(elegidas)} · pares mutación-prueba: {len(trabajos)} · pruebas en la suite: "
          f"{len(pruebas)} · sin mutación: {len(sin_mutacion)}")
    return errores


def main():
    args = sys.argv[1:]
    filtro = args[args.index("--filtro") + 1] if "--filtro" in args else None
    antes, fuentes_antes = foto_originales(), huella_fuentes()
    ok = True
    try:
        if "--mutaciones" not in args or "--todo" in args:
            ok = suite() and ok
        if "--mutaciones" in args or "--todo" in args:
            errores = mutaciones(filtro)
            for e in errores:
                print("ERROR:", e)
            ok = not errores and ok
    finally:
        shutil.rmtree(TRABAJO, ignore_errors=True)
    cambios = diferencias(antes, foto_originales())
    if huella_fuentes() != fuentes_antes:
        cambios.append("las fuentes del programa cambiaron durante la corrida")
    print(f"ORIGINALES: {len(antes)} entradas fotografiadas · cambios: {len(cambios)}")
    for c in cambios:
        print("   ", c)
    ok = ok and not cambios
    print("RESULTADO:", "OK" if ok else "FALLA")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
