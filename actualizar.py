# -*- coding: utf-8 -*-
"""AQUASHIELD · actualizar.py: al abrir el programa, trae la última versión de la rama «estable» del repositorio
(decisión de Marcelo, encargo 60, CICLO-actualizar-desde-estable.md).

Lo corren los dos .bat antes de abrir el panel. La rama «estable» la avanza solo Marcelo, después de probar; «main»
recibe los cambios de cada ciclo. Solo se actualiza un clon que está en la rama «estable»: el equipo de desarrollo,
en «main», nunca se actualiza solo.

Actualiza solo si no pisa nada propio del equipo, y si no puede, el programa abre con la versión que tiene:
- avanza con `git merge --ff-only`, y solo si el clon no tiene commits propios, ni cambios en los archivos del
  programa, ni una operación de git a medio terminar;
- ni algo propio en una ruta que la versión nueva empieza a versionar: git pisa sin avisar un archivo ignorado
  (config.json, perfiles/, logs/, una planilla) si la versión nueva lo versiona (medido en el encargo 60);
- lee el repositorio sin credenciales (es público) y nunca las pide ni las guarda: sin el ayudante de credenciales
  de git y sin preguntas en la consola;
- si la escritura queda a medias (un archivo abierto por otro programa: git deja la versión vieja con archivos de la
  nueva ya escritos, medido en el encargo 60), vuelve cada archivo a la versión en que quedó la rama. Nunca `reset`,
  `clean`, `stash` ni `checkout` de todo.

Lo que pasó queda en logs/actualizacion.json (RESULTADO), que el panel muestra al abrir (_aviso_de_actualizacion, en
AQUASHIELD.py). Sale con 0 si el programa puede abrir, y con 3 si una actualización quedó a medias y no pudo volver a
una sola versión: abrir correría una mezcla de las dos.

Uso: python actualizar.py [--carpeta RUTA]. Sin --carpeta, la carpeta de este archivo."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

RAMA = "estable"
REMOTO = "origin"
RESULTADO = Path("logs") / "actualizacion.json"
PLAZO_GIT = 30.0                 # s para un comando de git local (hipótesis)
PLAZO_FETCH = 60.0               # s para buscar la versión nueva (medido: 1,4 s leer el repositorio en GitHub)
PLAZO_MERGE = 120.0              # s para escribir la versión nueva
REINTENTOS_VOLVER = 5            # intentos de dejar los archivos en una sola versión tras una escritura a medias
PAUSA_VOLVER = 2.0               # s entre intentos: unos 10 s en total
MUESTRA = 3                      # rutas que nombra un motivo
A_MEDIAS = 3                     # código de salida: no se abre
# Lo que dice que una operación de git quedó a medio terminar (en la carpeta .git).
OPERACIONES = ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "BISECT_LOG", "rebase-merge", "rebase-apply",
               "index.lock")
# git sin pedir ni guardar claves: sin ayudante de credenciales ni programa que las pida.
SIN_CLAVES = ("-c", "credential.helper=", "-c", "core.askPass=")
SIN_VENTANA = 0x08000000         # CREATE_NO_WINDOW


ESCRIBIENDO = []                 # la versión que se empezó a escribir en esta corrida, si se empezó


class Falla(Exception):
    """Un comando de git que no terminó o no se pudo correr."""


def git_del_equipo():
    """git.exe de una carpeta absoluta del PATH, nunca de la carpeta del programa (Windows mira primero ahí)."""
    for d in os.environ.get("PATH", "").split(os.pathsep):
        d = d.strip().strip('"')
        if d and os.path.isabs(d) and os.path.isfile(os.path.join(d, "git.exe")):
            return os.path.join(d, "git.exe")
    return None


def entorno():
    """El de este proceso, sin lo que haría a git trabajar sobre otro repositorio ni preguntar nada."""
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_ASKPASS", "SSH_ASKPASS")}
    env.update({"GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never", "GIT_SSH_COMMAND": "ssh -o BatchMode=yes"})
    return env


def cerrar_arbol(pid):
    """El git que encuentra un programa en Windows es un lanzador que corre el git real como hijo: kill() mata solo
    al lanzador (medido en el HUB). Se cierra el árbol con el taskkill del sistema."""
    taskkill = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "taskkill.exe")
    try:
        subprocess.run([taskkill, "/T", "/F", "/PID", str(pid)], capture_output=True, timeout=15,
                       creationflags=SIN_VENTANA)
    except Exception:
        pass


class Git(object):
    def __init__(self, exe, carpeta):
        self.exe, self.carpeta = exe, carpeta

    def __call__(self, *argumentos, plazo=PLAZO_GIT):
        try:
            p = subprocess.Popen([self.exe, *SIN_CLAVES, *argumentos], cwd=str(self.carpeta), env=entorno(),
                                 stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 creationflags=SIN_VENTANA)
        except OSError as e:
            raise Falla(f"no pude correr git ({e})")
        try:
            salida, error = p.communicate(timeout=plazo)
        except subprocess.TimeoutExpired:
            cerrar_arbol(p.pid)
            p.communicate()
            raise Falla(f"git {argumentos[0]} no terminó en {plazo:.0f} s")
        return p.returncode, salida.decode("utf-8", "replace"), error.decode("utf-8", "replace")

    def texto(self, *argumentos, plazo=PLAZO_GIT):
        codigo, salida, error = self(*argumentos, plazo=plazo)
        if codigo:
            raise Falla(f"git {argumentos[0]} salió con {codigo}: {primera_linea(error)}")
        return salida

    def rutas(self, *argumentos):
        return [r for r in self.texto(*argumentos).split("\0") if r]

    def blob(self, commit, ruta):
        """El blob de 'ruta' en 'commit', o None si no está (o no es un archivo)."""
        linea = self.texto("ls-tree", "-z", commit, "--", ruta).split("\0")[0]
        partes = linea.split(None, 3)
        return partes[2] if len(partes) == 4 and partes[1] == "blob" and partes[3] == ruta else None

    def en_disco(self, ruta):
        """El blob que daría el archivo de 'ruta' como está en el disco, o None si no hay un archivo ahí."""
        if not (self.carpeta / ruta).is_file():
            return None
        return self.texto("hash-object", f"--path={ruta}", "--", ruta).strip()


def primera_linea(texto):
    """La primera línea con algo de un error de git, sin direcciones con una clave adentro."""
    import re
    linea = next((x.strip() for x in str(texto).splitlines() if x.strip()), "sin detalle")
    return re.sub(r"(https?://)[^/@\s]+@", r"\1", linea)[:200]


def muestra(rutas):
    nombres = ", ".join(f"«{r}»" for r in rutas[:MUESTRA])
    return nombres + (f" y {len(rutas) - MUESTRA} más" if len(rutas) > MUESTRA else "")


def resultado(estado, texto, **datos):
    return dict(datos, estado=estado, texto=texto, cuando=time.time())


def sin_actualizar(motivo, version):
    return resultado("sin-actualizar", f"⚠ No actualicé AQUASHIELD: {motivo}. Abro con la versión que tiene este "
                                       f"equipo ({version[:7]}).", motivo=motivo, version=version)


def ocupada(g, viejo, nuevo):
    """La primera ruta que la versión nueva empieza a versionar y donde la carpeta ya tiene algo que no es de la
    versión vieja (un archivo o una carpeta, ignorados o no), o None. Lo que la versión vieja ya versiona lo maneja
    git; una carpeta que la vieja ya tiene, también, salvo que la nueva ponga un archivo en su lugar."""
    viejas = set(g.rutas("ls-tree", "-r", "-z", "--name-only", viejo))
    carpetas = {"/".join(r.split("/")[:i]) for r in viejas for i in range(1, r.count("/") + 1)}
    for ruta in sorted(set(g.rutas("ls-tree", "-r", "-z", "--name-only", nuevo)) - viejas):
        partes = ruta.split("/")
        for i in range(1, len(partes) + 1):
            tramo = "/".join(partes[:i])
            if tramo in viejas or (i < len(partes) and tramo in carpetas):
                continue
            if os.path.lexists(g.carpeta / tramo):
                return tramo
    return None


def igualar(g, objetivo, otra, rutas):
    """Deja cada archivo de 'rutas' como está en 'objetivo' si en el disco tiene la versión de 'otra' (lo que una
    escritura a medias dejó). Un archivo que no es ninguna de las dos no se toca. Devuelve las rutas que no quedaron
    como en 'objetivo'."""
    faltan = []
    for ruta in rutas:
        try:
            disco, quiero, dejo = g.en_disco(ruta), g.blob(objetivo, ruta), g.blob(otra, ruta)
            if disco == quiero:
                continue
            if disco != dejo:
                faltan.append(ruta)
                continue
            if quiero is None:
                os.remove(g.carpeta / ruta)
            else:
                g.texto("checkout", objetivo, "--", ruta)
            if g.en_disco(ruta) != quiero:
                faltan.append(ruta)
        except (OSError, Falla):
            faltan.append(ruta)
    return faltan


def actualizar(carpeta):
    """Devuelve (resultado, código de salida)."""
    exe = git_del_equipo()
    if exe is None:
        return resultado("sin-actualizar", "⚠ No actualicé AQUASHIELD: no encontré git en este equipo. Abro con la "
                                           "versión que tiene.", motivo="sin git"), 0
    if not (carpeta / ".git").exists():
        return resultado("no-aplica", "Esta carpeta no es un clon del repositorio: AQUASHIELD no se actualiza "
                                      "solo.", motivo="sin .git"), 0
    g = Git(exe, carpeta)
    arriba = g.texto("rev-parse", "--show-toplevel").strip()
    if not os.path.samefile(arriba, carpeta):
        return resultado("no-aplica", "Esta carpeta no es la raíz de un clon del repositorio: AQUASHIELD no se "
                                      "actualiza solo.", motivo="otra raíz"), 0
    codigo, rama, _ = g("symbolic-ref", "--short", "-q", "HEAD")
    rama = rama.strip() if codigo == 0 else ""
    if rama != RAMA:
        return resultado("no-aplica", f"Este equipo no se actualiza solo: está en la rama «{rama or 'ninguna'}», y "
                                      f"solo se actualiza la rama «{RAMA}».", rama=rama), 0
    viejo = g.texto("rev-parse", "HEAD").strip()
    carpeta_git = Path(g.texto("rev-parse", "--absolute-git-dir").strip())
    abiertas = [op for op in OPERACIONES if (carpeta_git / op).exists()]
    if abiertas:
        return sin_actualizar(f"hay una operación de git a medio terminar en la carpeta ({', '.join(abiertas)})",
                              viejo), 0
    codigo, _, error = g("fetch", "--no-tags", "--quiet", REMOTO,
                         f"+refs/heads/{RAMA}:refs/remotes/{REMOTO}/{RAMA}", plazo=PLAZO_FETCH)
    if codigo:
        return sin_actualizar(f"no pude buscar la versión nueva ({primera_linea(error)})", viejo), 0
    nuevo = g.texto("rev-parse", "--verify", f"refs/remotes/{REMOTO}/{RAMA}^{{commit}}").strip()
    if nuevo == viejo:
        return resultado("al-dia", f"✓ AQUASHIELD está al día con la versión estable ({viejo[:7]}).",
                         version=viejo), 0
    if g("merge-base", "--is-ancestor", viejo, nuevo)[0] != 0:
        return sin_actualizar("este equipo tiene commits que la versión estable no trae (propios, o de una estable "
                              "anterior)", viejo), 0
    sucias = [r[3:] for r in g.texto("status", "--porcelain=v1", "-z", "--untracked-files=no").split("\0")
              if len(r) > 3]
    if sucias:
        return sin_actualizar(f"hay cambios en archivos del programa: {muestra(sucias)}", viejo), 0
    tramo = ocupada(g, viejo, nuevo)
    if tramo:
        return sin_actualizar(f"la versión nueva trae «{tramo}», y en esta carpeta ya hay algo con ese nombre que no "
                              f"es del programa: no lo piso", viejo), 0
    rutas = g.rutas("diff", "--name-only", "--no-renames", "-z", viejo, nuevo)
    ESCRIBIENDO.append(nuevo)              # desde aquí, una falla que nadie previó no deja abrir (main)
    try:
        codigo, _, error = g("merge", "--ff-only", "--no-edit", "--quiet", nuevo, plazo=PLAZO_MERGE)
        error = "" if codigo == 0 else primera_linea(error)
    except Falla as e:                     # git no terminó: lo que haya escrito se revisa igual
        error = str(e)
    return revisar(g, viejo, nuevo, rutas, error)


def revisar(g, viejo, nuevo, rutas, error):
    """Después de escribir: si la rama quedó en la versión nueva y los archivos con ella, está actualizado. Si no,
    deja cada archivo en la versión donde quedó la rama (la vieja, si git no la movió), reintentando unos segundos
    por si un archivo sigue abierto."""
    faltan = []
    for intento in range(REINTENTOS_VOLVER):
        try:
            en = g.texto("rev-parse", "HEAD").strip()
        except Falla:
            en = ""
        if en in (viejo, nuevo):
            faltan = igualar(g, en, nuevo if en == viejo else viejo, rutas)
            if not faltan and en == nuevo and not error:
                return resultado("actualizada", f"⟳ AQUASHIELD se actualizó a la versión estable {nuevo[:7]} "
                                                f"(tenía la {viejo[:7]}).", desde=viejo, version=nuevo), 0
            if not faltan and en == nuevo:
                return resultado("actualizada", f"⟳ AQUASHIELD se actualizó a la versión estable {nuevo[:7]} (tenía "
                                                f"la {viejo[:7]}), después de completar archivos que no se habían "
                                                f"escrito.", desde=viejo, version=nuevo), 0
            if not faltan:
                return sin_actualizar(f"la versión nueva ({nuevo[:7]}) no se pudo escribir ({error or 'sin detalle'})"
                                      f", y dejé los archivos como estaban", viejo), 0
        if intento + 1 < REINTENTOS_VOLVER:
            time.sleep(PAUSA_VOLVER)
    texto = (f"⛔ La actualización de AQUASHIELD quedó a medias y no pude dejar los archivos en una sola versión "
             f"({muestra(faltan) or 'la rama no quedó en ninguna de las dos'}): no abro el programa, para no correr "
             f"una mezcla de las dos. Cierra lo que tenga abierto un archivo de esta carpeta y vuelve a abrirlo.")
    return resultado("a-medias", texto, desde=viejo, version=nuevo, faltan=faltan), A_MEDIAS


def guardar(carpeta, datos):
    """logs/actualizacion.json, de forma atómica (un temporal al lado y os.replace, con reintentos)."""
    destino = carpeta / RESULTADO
    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        tmp = destino.with_name(destino.name + ".tmp")
        tmp.write_bytes(json.dumps(datos, ensure_ascii=False, indent=1).encode("utf-8"))
        for i in range(20):
            try:
                os.replace(tmp, destino)
                return
            except PermissionError:
                if i == 19:
                    raise
                time.sleep(0.1)
    except OSError:
        pass                                   # sin el archivo, el panel no muestra nada: el programa abre igual


def main(argumentos=None):
    argumentos = list(sys.argv[1:] if argumentos is None else argumentos)
    carpeta = Path(__file__).resolve().parent
    if argumentos[:1] == ["--carpeta"] and len(argumentos) == 2:
        carpeta = Path(argumentos[1]).resolve()
    print(f"Buscando la versión nueva de AQUASHIELD (rama «{RAMA}»)...", flush=True)
    try:
        datos, codigo = actualizar(carpeta)
    except Exception as e:
        falla = f"{type(e).__name__}: {primera_linea(e)}"
        if ESCRIBIENDO:                    # ya había empezado a escribir: los archivos pueden ser de las dos versiones
            datos, codigo = resultado("a-medias", f"⛔ La actualización de AQUASHIELD falló mientras escribía la "
                                                  f"versión nueva ({falla}): no abro el programa, para no correr una "
                                                  f"mezcla de dos versiones. Vuelve a abrirlo."), A_MEDIAS
        else:                              # nada de lo de antes de escribir debe impedir abrir el programa
            datos, codigo = resultado("sin-actualizar", f"⚠ No actualicé AQUASHIELD: el actualizador falló "
                                                        f"({falla}). Abro con la versión que tiene."), 0
    guardar(carpeta, datos)
    print(datos["texto"], flush=True)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
