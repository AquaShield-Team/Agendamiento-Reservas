# -*- coding: utf-8 -*-
"""Arnés de la red de verificación offline de AQUASHIELD.

Lo que hace cumplir, en cada prueba:
- El programa se carga desde una COPIA en una carpeta aislada (sandbox) del
  directorio temporal: BASE, perfiles/, logs/, config.json y la planilla quedan
  dentro de ella. El AQUASHIELD.py original nunca se importa desde su carpeta.
- Trampas: abrir el navegador, lanzar un proceso, conectarse fuera de 127.0.0.1
  o usar Playwright de verdad levanta EfectoReal y queda en DISPAROS. Cada
  prueba termina exigiendo DISPAROS vacío.
- Las tres llaves del candado de emisión (AQUASHIELD_EMITIR, el argumento
  emitir/--emitir/produccion/--produccion y opciones.emitir_reservas) se apagan
  al empezar y se exige que sigan apagadas al terminar cada prueba.
- Las fuentes del programa se leen de AQUASHIELD_FUENTES (carpeta con copias,
  la usa el corredor de mutaciones) o, si no está, de la raíz del proyecto.
"""
import contextlib
import importlib.util
import itertools
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import types
import unittest
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

import sinteticos

RAIZ = Path(__file__).resolve().parent.parent
FUENTES = Path(os.environ["AQUASHIELD_FUENTES"]) if os.environ.get("AQUASHIELD_FUENTES") else RAIZ
LLAVE_ENTORNO = "AQUASHIELD_EMITIR"
ARGUMENTOS_EMISION = ("emitir", "--emitir", "produccion", "--produccion")
TMP_ORIGINAL = tempfile.gettempdir()
_POPEN = subprocess.Popen          # el original, solo para procesos hijos que la prueba controla


class EfectoReal(AssertionError):
    """Intento de efecto real: navegador, proceso, red externa o Playwright."""


DISPAROS = []


def _trampa(nombre):
    def disparar(*a, **k):
        DISPAROS.append((nombre, repr(a)[:160]))
        raise EfectoReal(f"efecto real bloqueado: {nombre}")
    return disparar


# --- Trampas del proceso de pruebas (se instalan al importar este módulo) ---
_conectar = socket.socket.connect
_conectar_ex = socket.socket.connect_ex


def _es_local(direccion):
    host = direccion[0] if isinstance(direccion, tuple) else str(direccion)
    return host in ("127.0.0.1", "localhost", "::1")


def _connect(self, direccion):
    if not _es_local(direccion):
        DISPAROS.append(("red", str(direccion)[:80]))
        raise EfectoReal(f"efecto real bloqueado: conexion a {direccion}")
    return _conectar(self, direccion)


def _connect_ex(self, direccion):
    if not _es_local(direccion):
        DISPAROS.append(("red", str(direccion)[:80]))
        raise EfectoReal(f"efecto real bloqueado: conexion a {direccion}")
    return _conectar_ex(self, direccion)


class _PopenTrampa(subprocess.Popen):
    """Sigue siendo una clase (asyncio hereda de subprocess.Popen), pero no lanza nada."""

    def __init__(self, *a, **k):
        self._child_created = False          # para que Popen.__del__ no se queje
        DISPAROS.append(("subprocess.Popen", repr(a)[:160]))
        raise EfectoReal("efecto real bloqueado: subprocess.Popen")


# Playwright y asyncio se importan ANTES de las trampas: el programa los importa
# al cargarse y asyncio necesita la clase Popen verdadera para definir la suya.
import asyncio  # noqa: E402,F401
import playwright.sync_api  # noqa: E402,F401

socket.socket.connect = _connect
socket.socket.connect_ex = _connect_ex
webbrowser.open = webbrowser.open_new = webbrowser.open_new_tab = _trampa("webbrowser")
for _n in ("run", "call", "check_call", "check_output"):
    setattr(subprocess, _n, _trampa(f"subprocess.{_n}"))
subprocess.Popen = _PopenTrampa
os.system = _trampa("os.system")
if hasattr(os, "startfile"):
    os.startfile = _trampa("os.startfile")


# --- Medición opcional: qué funciones del programa se ejecutan (apagada por defecto) ---
# AQUASHIELD_COBERTURA=<prefijo> escribe <prefijo>.<pid> al salir, con un nombre por línea.
if os.environ.get("AQUASHIELD_COBERTURA"):
    import atexit

    _EJECUTADAS = set()

    def _perfil(frame, evento, arg):
        if evento == "call" and frame.f_code.co_filename.endswith("AQUASHIELD.py"):
            _EJECUTADAS.add(frame.f_code.co_name)

    sys.setprofile(_perfil)
    threading.setprofile(_perfil)
    atexit.register(lambda: Path(f"{os.environ['AQUASHIELD_COBERTURA']}.{os.getpid()}").write_text(
        "\n".join(sorted(_EJECUTADAS)), encoding="utf-8"))


# --- Llaves del candado ---
def apagar_llaves():
    os.environ.pop(LLAVE_ENTORNO, None)
    sys.argv[:] = sys.argv[:1]


def llaves_encendidas(mod):
    """Lista de llaves encendidas; vacía si las tres están apagadas."""
    encendidas = []
    if os.environ.get(LLAVE_ENTORNO) is not None:
        encendidas.append("entorno")
    if any(str(a).lower() in ARGUMENTOS_EMISION for a in sys.argv):
        encendidas.append("argumento")
    cfg = Path(mod.BASE) / "config.json"
    if cfg.exists():
        try:
            if json.loads(cfg.read_text(encoding="utf-8")).get("opciones", {}).get("emitir_reservas"):
                encendidas.append("config")
        except Exception:
            pass
    return encendidas


# --- Sandbox y carga del programa ---
_N = itertools.count()
SANDBOXES = []


def nueva_sandbox():
    # resolve(): %TEMP% puede venir en forma corta 8.3 (USUARI~1.XXX) y el programa
    # resuelve su propia ruta en forma larga; así las dos coinciden.
    sb = Path(tempfile.mkdtemp(prefix="aquashield_red_", dir=TMP_ORIGINAL)).resolve()
    SANDBOXES.append(sb)
    return sb


def _limpiar_sandboxes():
    """Al salir del proceso, borra sus sandboxes (sin esto, un censo dejaba cientos en %TEMP%)."""
    tempfile.tempdir = None
    for sb in SANDBOXES:
        shutil.rmtree(sb, ignore_errors=True)


import atexit  # noqa: E402
atexit.register(_limpiar_sandboxes)


def escribir_json(ruta, datos):
    Path(ruta).write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


def cargar(config="sintetica", extra=()):
    """Copia AQUASHIELD.py (y 'extra') a una sandbox nueva y lo importa desde ahí.
    config: "sintetica" (llaves apagadas), None (sin config.json) o un dict."""
    sb = nueva_sandbox()
    for nombre in ("AQUASHIELD.py",) + tuple(extra):
        shutil.copyfile(FUENTES / nombre, sb / nombre)
    if config == "sintetica":
        escribir_json(sb / "config.json", sinteticos.config())
    elif isinstance(config, dict):
        escribir_json(sb / "config.json", config)
    apagar_llaves()
    tempfile.tempdir = str(sb)      # el panel guarda la planilla subida en gettempdir()
    nombre = f"aquashield_prueba_{next(_N)}"
    spec = importlib.util.spec_from_file_location(nombre, sb / "AQUASHIELD.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    spec.loader.exec_module(mod)
    mod.sync_playwright = _trampa("sync_playwright")
    return mod, sb


def hijo(args, cwd, timeout=60, env_extra=None):
    """Proceso hijo controlado por la prueba (sin la llave de entorno)."""
    env = {k: v for k, v in os.environ.items() if k != LLAVE_ENTORNO}
    env["PYTHONIOENCODING"] = "utf-8"
    env.update(env_extra or {})
    p = _POPEN(args, cwd=str(cwd), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate(timeout=timeout)
    return p.returncode, out.decode("utf-8", "replace"), err.decode("utf-8", "replace")


class CasoAQ(unittest.TestCase):
    """Caso base: programa cargado en sandbox, trampas y llaves vigiladas."""
    config_inicial = "sintetica"

    @classmethod
    def setUpClass(cls):
        cls.mod, cls.sb = cargar(cls.config_inicial)

    def setUp(self):
        DISPAROS.clear()
        apagar_llaves()
        self.assertEqual(llaves_encendidas(self.mod), [], "una llave del candado empezó encendida")
        self.assertIs(self.mod.es_modo_emision(), False, "el candado empezó abierto")

    def tearDown(self):
        disparos = list(DISPAROS)
        DISPAROS.clear()
        self.assertEqual(disparos, [], f"la prueba intentó un efecto real: {disparos}")
        self.assertEqual(llaves_encendidas(self.mod), [], "una llave del candado quedó encendida")


# --- Playwright y página falsos ---
class PaginaFalsa:
    def __init__(self, texto="", url="about:blank", titulo="", frames=None):
        self.texto, self.url, self._titulo = texto, url, titulo
        self.frames = frames or []
        self.capturas, self.esperas = [], 0
        self.goto = _trampa("page.goto")

    def evaluate(self, js, *a):
        return self.texto(js, *a) if callable(self.texto) else self.texto

    def title(self):
        return self._titulo

    def wait_for_timeout(self, ms):
        self.esperas += 1

    def screenshot(self, path=None, full_page=False):
        self.capturas.append((Path(path).name, full_page))
        Path(path).write_bytes(b"")


class ContextoFalso:
    def __init__(self):
        self.pages = [PaginaFalsa()]
        self.cerrado = False
        self.scripts = []

    def add_init_script(self, s):
        self.scripts.append(s)

    def new_page(self):
        p = PaginaFalsa()
        self.pages.append(p)
        return p

    def close(self):
        self.cerrado = True


class PlaywrightFalso:
    """Reemplaza sync_playwright: registra cada lanzamiento y no abre nada."""

    def __init__(self):
        self.lanzamientos, self.contextos = [], []

    def __call__(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    @property
    def chromium(self):
        return self

    def launch_persistent_context(self, **kw):
        self.lanzamientos.append(kw)
        c = ContextoFalso()
        self.contextos.append(c)
        return c


class Navieras:
    """Reemplaza el login y el reservador de las seis navieras por FALSOS que
    registran lo que reciben, y Playwright por PlaywrightFalso. Al salir deja
    todo como estaba (y Playwright otra vez como trampa)."""

    def __init__(self, mod, login_ok=True, respuesta=None):
        self.mod, self.login_ok = mod, login_ok
        self.respuesta = respuesta or (lambda nav, rsv, on_pausa: ("OK-EJEMPLO", f"armada falsa {nav} fila {rsv['fila']}"))
        self.logins, self.reservas = [], []
        self.orig_nav, self.orig_res = dict(mod.NAVIERAS), dict(mod.RESERVADORES)
        self.pw = PlaywrightFalso()

    def __enter__(self):
        for k, (nombre, _) in self.orig_nav.items():
            self.mod.NAVIERAS[k] = (nombre, self._login(k))
            self.mod.RESERVADORES[k] = self._reservador(k)
        self.mod.sync_playwright = self.pw
        return self

    def __exit__(self, *a):
        self.mod.NAVIERAS.clear()
        self.mod.NAVIERAS.update(self.orig_nav)
        self.mod.RESERVADORES.clear()
        self.mod.RESERVADORES.update(self.orig_res)
        self.mod.sync_playwright = _trampa("sync_playwright")
        return False

    def _login(self, nav):
        def login(page, creds, reg, on_pausa=None):
            self.logins.append((nav, creds.get("usuario")))
            return self.login_ok(nav) if callable(self.login_ok) else self.login_ok
        return login

    def _reservador(self, nav):
        def reservar(page, rsv, creds, reg, on_pausa=None):
            self.reservas.append((nav, rsv["fila"], creds.get("usuario")))
            return self.respuesta(nav, rsv, on_pausa)
        return reservar


# --- Reloj detenido: dos corridas seguidas caen en el mismo segundo ---
MOMENTO_FIJO = (2026, 1, 2, 3, 4, 5)       # sale en los nombres como 20260102_030405


@contextlib.contextmanager
def reloj_detenido(mod):
    """El nombre «datetime» del programa en la sandbox pasa a un espejo del módulo cuyo datetime.now()
    devuelve siempre MOMENTO_FIJO. El módulo datetime de Python no se toca, y al salir vuelve el real."""
    real = mod.datetime

    class Detenido(real.datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(*MOMENTO_FIJO)

    espejo = types.ModuleType("datetime_detenido")
    espejo.__dict__.update({k: v for k, v in vars(real).items() if not k.startswith("__")})
    espejo.datetime = Detenido
    mod.datetime = espejo
    try:
        yield
    finally:
        mod.datetime = real


# --- Servidor web del programa, en un puerto propio ---
def puerto_libre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Servidor:
    def __init__(self, mod, puerto=None):
        self.mod = mod
        self.puerto = puerto or puerto_libre()
        self.hilo = None

    @property
    def base(self):
        return f"http://127.0.0.1:{self.puerto}"

    def iniciar(self, espera=10):
        self.hilo = threading.Thread(target=self.mod.lanzar_web,
                                     kwargs={"puerto": self.puerto, "abrir": False}, daemon=True)
        self.hilo.start()
        fin = time.time() + espera
        while time.time() < fin:
            try:
                self.get("/api/estado")
                return self
            except Exception:
                time.sleep(0.1)
        raise AssertionError("el servidor no respondió")

    def completo(self, ruta, datos=None, timeout=10):
        """(estado, cabeceras, cuerpo)."""
        if isinstance(datos, (dict, list)):
            datos = json.dumps(datos).encode("utf-8")
        req = urllib.request.Request(self.base + ruta, data=datos, method="POST" if datos is not None else "GET")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, dict(r.headers), r.read()
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers), e.read()

    def pedir(self, ruta, datos=None, timeout=10):
        st, _, cuerpo = self.completo(ruta, datos, timeout)
        return st, cuerpo

    def get(self, ruta):
        return self.pedir(ruta)

    def post(self, ruta, datos=b"{}"):
        return self.pedir(ruta, datos)

    def json(self, ruta, datos=None):
        st, cuerpo = self.pedir(ruta, datos)
        return st, json.loads(cuerpo.decode("utf-8"))

    def esperar_fin(self, maximo=20):
        fin = time.time() + maximo
        while time.time() < fin:
            _, e = self.json("/api/estado")
            if not e["corriendo"]:
                return e
            time.sleep(0.1)
        raise AssertionError("la corrida no terminó")

    def apagar(self):
        with contextlib.suppress(Exception):
            self.post("/api/apagar")
        if self.hilo:
            self.hilo.join(timeout=6)
        return not (self.hilo and self.hilo.is_alive())
