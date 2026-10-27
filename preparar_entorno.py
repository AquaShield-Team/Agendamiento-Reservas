# -*- coding: utf-8 -*-
"""AQUASHIELD · preparar_entorno.py: deja listas las librerías del programa antes de abrir el panel, sin que la persona
abra una terminal (decisión de Marcelo, encargo 84, CICLO-entorno-propio.md).

Lo corren los dos .bat después de actualizar.py, con el Python del equipo. Arma un entorno propio del programa, `.venv`
en esta carpeta, y le instala ahí lo que dice requirements.txt: cada paquete en una versión fija y con el sha256 de
cada rueda, así que pip no instala un archivo que no sea byte a byte el que PyPI publicó. Una instalación aparte del
Python del equipo no se toca: cambiarlo (TI, una actualización de Python) ya no deja el programa sin librerías.

Qué hace en cada inicio, y cuánto tarda:
- con el `.venv` listo y requirements.txt igual que la última vez que salió bien, solo comprueba que cada librería se
  importe (menos de 2 s);
- si falta el `.venv`, o su Python ya no arranca (TI cambió el del equipo), lo crea sin pip y le instala lo que falta
  con el pip del equipo (`pip --python`): la primera vez, de uno a dos minutos, con conexión a internet;
- si no puede (sin red, o pip falla) pero el Python del equipo ya tiene todo lo que el programa necesita, abre con ese:
  es lo que hacía el .bat hasta el encargo 83. Si no lo tiene, lo dice y no abre.

Lo que no hace: no pide permisos de administrador (todo queda en esta carpeta), no usa los .exe que pip crea en
Scripts (Defender los bloquea), no toca un `.venv` que no armó este programa (lleva una marca adentro), no sigue una
unión o un enlace con ese nombre, no cierra ningún programa, y si un archivo bajado no coincide con su hash no sigue.

Sale con 0 si el entorno propio está listo, con 10 si abre con el Python del equipo, y con 11 si no se puede abrir. Lo
que pasó queda en logs/entorno.log (sin direcciones con clave); el estado, en logs/.entorno-estado.json.

Uso: python -I preparar_entorno.py   (aislado: no importa de esta carpeta ningún archivo con nombre de módulo estándar)"""
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import sysconfig
import time
import traceback
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
VENV = ".venv"
MARCA = ".aquashield-entorno"            # dentro del .venv: lo armó este programa, y solo ese se rehace
APARTADO = ".venv-apartado-"             # en logs/: un .venv que se rehízo, hasta que se pueda borrar
REQUISITOS = "requirements.txt"
ESTADO = Path("logs") / ".entorno-estado.json"
LOG = Path("logs") / "entorno.log"
# Sin estas el panel no abre. playwright.sync_api es lo que importa el programa (y trae greenlet y pyee).
OBLIGATORIAS = ("playwright.sync_api", "openpyxl")
# Sin esta el programa sigue, de lunes a viernes, y lo avisa (los feriados de Chile de la fecha de retiro de MAERSK).
OPCIONALES = ("holidays",)
# Los Python que cubre requirements.txt: de 3.11 a 3.14 en Windows de 64 bits (greenlet 3.3.1 no publica ruedas para
# 3.15, Windows de 32 bits ni ARM). El .bat pide el mismo mínimo. Fuera de ahí pip no tiene ruedas con hash: no se intenta.
PYTHON_MINIMO = (3, 11)
PYTHON_MAXIMO = (3, 14)
SALIDA_PROPIO = 0                        # el .bat pone .venv\Scripts primero en el PATH
SALIDA_EQUIPO = 10                       # el .bat abre con el Python del equipo
SALIDA_NO_PUEDE = 11                     # el .bat lo dice y no abre
PLAZO_ENTORNO = 120.0                    # s para crear el .venv sin pip (unos 3 s, medido en LabelInspect)
PLAZO_IMPORTA = 60.0                     # s para que un Python importe las librerías
PLAZO_PIP = 900.0                        # s para instalar (el wheel de playwright pesa unos 35 MB)
PLAZO_CIERRE = 10.0                      # s que se espera la salida de un proceso al que se le cerró el árbol
ESPERA_OTRA_VENTANA = 1200.0             # s que espera a otra ventana que está preparando lo mismo
PAUSA_REINTENTO = 1800.0                 # s sin volver a instalar tras una falla, si todo lo necesario ya se importa
REINTENTOS_ARCHIVO = 20                  # intentos de reemplazar o apartar algo que el antivirus abre a veces
PAUSA_ARCHIVO = 0.1                      # s entre intentos: unos 2 s en total
LARGO_MAXIMO_LOG = 512 * 1024            # bytes de logs/entorno.log antes de recortarlo
LINEAS_DE_ERROR = 6                      # líneas de lo que dijo pip que se muestran si falla
HASH_NO_COINCIDE = "DO NOT MATCH THE HASHES"
SIN_PIP = "No module named pip"
SIN_VENTANA = 0x08000000                 # CREATE_NO_WINDOW
# Lo que cada librería importa, sin la carpeta actual en sys.path: un archivo del programa con su nombre no la reemplaza.
CODIGO_IMPORTA = ("import sys\n"
                  "sys.path[:] = [p for p in sys.path if p not in ('', '.')]\n"
                  "import importlib\n"
                  "for n in %r:\n"
                  "    try:\n"
                  "        importlib.import_module(n)\n"
                  "    except BaseException:\n"
                  "        print(n)\n")


class NoPuede(Exception):
    """No se puede abrir, y no se intenta con el Python del equipo: lleva lo que se le dice a la persona."""

    def __init__(self, lineas):
        Exception.__init__(self, " ".join(lineas))
        self.lineas = lineas


def decir(texto=""):
    print(texto, flush=True)


def sin_claves(texto):
    """Sin la clave de una dirección con usuario y clave (un índice de paquetes de la empresa), aunque la clave traiga
    una arroba, y sin el valor de un parámetro que suele llevar una (`?token=...`): pip enmascara sus direcciones, pero
    no se confía en eso para un archivo que la persona puede mandar."""
    texto = re.sub(r"(https?://)[^/\s]*@", r"\1", str(texto))
    return re.sub(r"(?i)([?&](?:access_token|api_key|apikey|key|password|passwd|pwd|secret|token)=)[^&\s]+", r"\1****", texto)


def formas_del_perfil():
    """Cómo puede aparecer en lo que cuenta pip la carpeta del usuario de Windows: la larga y su forma corta 8.3, de la más
    larga a la más corta."""
    bases = {os.environ.get("USERPROFILE", ""), os.path.expanduser("~")}
    bases |= {os.path.realpath(b) for b in bases if b}
    formas = set()
    for base in bases:
        if len(base) < 4:                       # vacía o una raíz ("C:\"): no es la carpeta de nadie
            continue
        formas.add(base)
        try:
            import ctypes
            corta = ctypes.create_unicode_buffer(1024)
            if ctypes.windll.kernel32.GetShortPathNameW(base, corta, 1024):
                formas.add(corta.value)
        except (AttributeError, OSError):
            pass
    return sorted(formas, key=len, reverse=True)


def sin_usuario(texto):
    """Sin el nombre del usuario de Windows en las rutas: logs/entorno.log y lo que se muestra viajan a quien le dio el
    programa a la persona (LEEME). Cambia la carpeta del usuario, con barras de cualquier lado, por %USERPROFILE%."""
    texto = str(texto)
    for forma in formas_del_perfil():
        for variante in (forma, forma.replace("\\", "/")):
            texto = re.sub(re.escape(variante), lambda _: "%USERPROFILE%", texto, flags=re.IGNORECASE)
    return texto


def anotar(texto):
    """Una línea en logs/entorno.log, con la hora. Si no se puede escribir, se sigue: el log nunca frena el inicio."""
    try:
        ruta = RAIZ / LOG
        ruta.parent.mkdir(exist_ok=True)
        if ruta.exists() and ruta.stat().st_size > LARGO_MAXIMO_LOG:
            ruta.write_bytes(ruta.read_bytes()[-LARGO_MAXIMO_LOG // 4:])
        with open(ruta, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {sin_usuario(sin_claves(texto))}\n")
    except OSError:
        pass


def entorno_de_los_hijos():
    env = dict(os.environ)
    env["NoDefaultCurrentDirectoryInExePath"] = "1"          # cmd no corre un .bat de la carpeta por su nombre solo
    return env


def cerrar_arbol(pid):
    """`pip --python` vuelve a correr pip con el Python del .venv, como un proceso hijo que hereda la salida: al vencer el
    plazo, matar solo al de afuera deja al de adentro con la tubería abierta, y quien lee no vuelve (medido por la
    revisión de código del encargo 84: 3,0 s sin nieto y 20,2 s con uno). Se cierra el árbol con el taskkill del sistema,
    como actualizar.py con el de git."""
    taskkill = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "taskkill.exe")
    try:
        subprocess.run([taskkill, "/T", "/F", "/PID", str(pid)], capture_output=True, timeout=15,
                       creationflags=SIN_VENTANA)
    except Exception:
        pass


def correr(argumentos, plazo):
    """(código, salida): código None si no se pudo lanzar o venció el plazo (y entonces cierra el proceso y sus hijos).
    La salida junta lo que escribió en la salida normal y en la de error."""
    try:
        p = subprocess.Popen(argumentos, cwd=str(RAIZ), env=entorno_de_los_hijos(), stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=SIN_VENTANA)
    except OSError as e:
        return None, str(e)
    try:
        salida, _ = p.communicate(timeout=plazo)
    except subprocess.TimeoutExpired:
        cerrar_arbol(p.pid)
        try:
            p.communicate(timeout=PLAZO_CIERRE)
        except subprocess.TimeoutExpired:
            pass
        return None, ""
    return p.returncode, salida.decode("utf-8", "replace")


def nombre_del_mutex():
    """Uno por carpeta del programa: dos copias de AQUASHIELD en el mismo equipo no se esperan entre sí."""
    return "Local\\AquaShieldEntorno" + hashlib.sha256(os.path.normcase(str(RAIZ)).encode("utf-8")).hexdigest()[:24]


def esperar_a_las_otras_ventanas():
    """Una sola ventana a la vez prepara el entorno: el doble clic de quien ve que tarda dejaría dos pip escribiendo en
    el mismo .venv. Un mutex con nombre (por esta carpeta): la segunda espera a que la primera termine, y entonces el
    entorno ya está listo. Se suelta solo al terminar el proceso. Si Windows no lo deja tomar, sigue sin él."""
    try:
        import ctypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.CreateMutexW.restype = ctypes.c_void_p
        k32.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_wchar_p]
        k32.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        k32.WaitForSingleObject.restype = ctypes.c_uint32
        mutex = k32.CreateMutexW(None, 0, nombre_del_mutex())
        if not mutex:
            return
        if k32.WaitForSingleObject(mutex, 0) not in (0, 0x80):          # ya la tiene otra ventana
            decir("Otra ventana de AQUASHIELD está preparando el programa: espero a que termine…")
            anotar("espero a otra ventana que prepara el entorno")
            k32.WaitForSingleObject(mutex, int(ESPERA_OTRA_VENTANA * 1000))
    except Exception as e:
        anotar(f"sin exclusión entre ventanas: {e}")


def huella_de_requisitos():
    """El sha256 de requirements.txt, con los fines de línea de git: un clon con CRLF no cambia la huella."""
    try:
        datos = (RAIZ / REQUISITOS).read_bytes().replace(b"\r\n", b"\n")
    except OSError:
        return "(falta)"
    return hashlib.sha256(datos).hexdigest()


def leer_estado():
    try:
        datos = json.loads((RAIZ / ESTADO).read_bytes().decode("utf-8"))
    except (OSError, ValueError):
        return {}
    return datos if isinstance(datos, dict) else {}


def guardar_estado(estado):
    """Reemplaza el archivo de a un paso, con reintentos: el antivirus lo abre a veces (os.replace da WinError 5)."""
    ruta = RAIZ / ESTADO
    try:
        ruta.parent.mkdir(exist_ok=True)
        temporal = ruta.with_name(ruta.name + ".tmp")
        temporal.write_bytes(json.dumps(estado).encode("utf-8"))
        for intento in range(REINTENTOS_ARCHIVO):
            try:
                os.replace(temporal, ruta)
                return
            except OSError:
                if intento == REINTENTOS_ARCHIVO - 1:
                    raise
                time.sleep(PAUSA_ARCHIVO)
    except OSError as e:
        anotar(f"no pude guardar el estado: {e}")


def python_del_venv():
    return RAIZ / VENV / "Scripts" / "python.exe"


def es_enlace(ruta):
    """True si la ruta no es una carpeta de verdad en su lugar: una unión (junction) o un enlace. Llenarla o rehacerla
    tocaría lo que hay del otro lado (`venv --clear` lo vaciaba: medido en LabelInspect, el 18-10)."""
    if not os.path.lexists(ruta):
        return False
    en_su_lugar = os.path.join(os.path.realpath(os.path.dirname(ruta)), os.path.basename(ruta))
    return os.path.islink(ruta) or os.path.normcase(os.path.realpath(ruta)) != os.path.normcase(en_su_lugar)


def codigo_al_arrancar(python):
    """Con qué código sale ese Python (-I: sin las variables PYTHON* ni la carpeta actual): 0 si arranca. None si no
    está, si no se pudo correr o si venció el plazo: un antivirus que lo retiene, o un equipo cargado, no es un entorno
    roto (la revisión de seguridad del 20-10, en LabelInspect, midió un .venv sano rehecho por un plazo vencido)."""
    if not Path(python).is_file():
        return None
    return correr([str(python), "-I", "-c", "pass"], PLAZO_IMPORTA)[0]


def faltan(python, bandera):
    """Las librerías, obligatorias y opcionales, que ese Python no puede importar. Si no corre, faltan todas. Con el
    Python del equipo, -E y no -I: el de la tienda instala en el sitio del usuario, que -I no mira. En el .venv, el
    sitio del usuario no cuenta, y va -I."""
    nombres = list(OBLIGATORIAS + OPCIONALES)
    codigo, salida = correr([str(python), bandera, "-c", CODIGO_IMPORTA % (nombres,)], PLAZO_IMPORTA)
    if codigo != 0:
        return nombres
    sin = set(x.strip() for x in salida.splitlines())
    return [n for n in nombres if n in sin]


def fuera_de_cobertura(plataforma=None, version=None, sin_gil=None):
    """Por qué requirements.txt no cubre a este Python, dicho para la persona, o None si lo cubre. Sin parámetros, mira
    el Python que corre el preparador (el del equipo, el mismo con que crearía el .venv). La plataforma es la de
    `sysconfig` (win-amd64, win32, win-arm64) y no la de la máquina: un Python x64 emulado en un equipo ARM64 sirve. Un
    Python sin GIL (3.14t) baja ruedas cp314t que no están en los hashes: pip lo diría como un hash alterado, y no lo es
    (medido por la revisión de código del encargo 84)."""
    plataforma = plataforma or sysconfig.get_platform()
    version = version or sys.version_info[:2]
    sin_gil = bool(sysconfig.get_config_var("Py_GIL_DISABLED")) if sin_gil is None else sin_gil
    if plataforma == "win32":
        return "es de 32 bits"
    if plataforma != "win-amd64":
        return f"es para {plataforma}"
    if not PYTHON_MINIMO <= tuple(version[:2]) <= PYTHON_MAXIMO:
        return f"es la {version[0]}.{version[1]}"
    if sin_gil:
        return "es la versión sin GIL"
    return None


def reciente(intento, huella):
    """True si la última instalación que falló fue de estos mismos requisitos y hace menos de PAUSA_REINTENTO s: sin
    red, no se vuelve a esperar a pip en cada inicio por un cambio de versión que el programa no necesita para abrir."""
    try:
        return intento["requisitos"] == huella and 0 <= time.time() - float(intento["cuando"]) < PAUSA_REINTENTO
    except (KeyError, TypeError, ValueError):
        return False


def obligatorias_que_faltan(lista):
    return [n.split(".")[0] for n in lista if n in OBLIGATORIAS]


def nombrar(nombres):
    nombres = [f"«{n}»" for n in nombres]
    return nombres[0] if len(nombres) == 1 else ", ".join(nombres[:-1]) + " y " + nombres[-1]


def apartar(ruta, destino):
    """os.replace con reintentos: el antivirus abre a veces lo recién usado, y el renombre de una carpeta da WinError 5
    una vez en unas 40 (medido en el HUB el 2026-09-28). Uno retenido de verdad sigue fallando, y se rinde."""
    for intento in range(REINTENTOS_ARCHIVO):
        try:
            os.replace(ruta, destino)
            return
        except OSError:
            if intento == REINTENTOS_ARCHIVO - 1:
                raise
            time.sleep(PAUSA_ARCHIVO)


def quitar_solo_lectura(funcion, ruta, *_):
    """git deja sus archivos de solo lectura, y Windows no borra uno así (WinError 5, medido); un .venv no, pero un
    archivo que la persona marcó sí. Se le quita y se vuelve a intentar."""
    os.chmod(ruta, stat.S_IWRITE)
    funcion(ruta)


def borrar_apartados():
    """Los .venv apartados al rehacer, en logs/: se borran si se puede, y uno retenido queda para la vez siguiente.
    rmtree no entra en una unión: la quita como enlace."""
    carpeta = RAIZ / "logs"
    try:
        nombres = os.listdir(carpeta)
    except OSError:
        return
    opcion = {"onexc": quitar_solo_lectura} if sys.version_info >= (3, 12) else {"onerror": quitar_solo_lectura}
    for nombre in nombres:
        if nombre.startswith(APARTADO):
            try:
                shutil.rmtree(carpeta / nombre, **opcion)
            except OSError as e:
                anotar(f"no pude borrar {nombre}: {e}")


def crear_entorno(ruta, python):
    """Crea el .venv con su marca adentro, ANTES de venv: si la creación se corta, el inicio siguiente sabe que es suyo
    y lo rehace. Sin pip (unos 3 s, contra 28 a 60 s con pip, medido en LabelInspect): lo llena el pip del equipo con
    --python. venv con -I: un venv.py en la carpeta del programa no corre en su lugar."""
    try:
        ruta.mkdir()
        (ruta / MARCA).write_text("Lo armó preparar_entorno.py: si su Python no arranca, lo rehace.\n", encoding="utf-8")
    except OSError as e:
        anotar(f"no pude crear {VENV}: {e}")
        try:
            ruta.rmdir()                                  # sin la marca, el inicio siguiente lo tomaría por ajeno
        except OSError:
            pass
        return None
    codigo, salida = correr([sys.executable, "-I", "-m", "venv", "--without-pip", str(ruta)], PLAZO_ENTORNO)
    if codigo != 0 or codigo_al_arrancar(python) != 0:
        anotar(f"no pude crear el entorno propio (código {codigo}): {salida.strip()[-300:]}")
        return None
    estado = leer_estado()
    estado.pop("requisitos", None)                      # un entorno nuevo está vacío: lo que se dio por instalado ya no
    guardar_estado(estado)
    return python


def entorno_propio():
    """El python.exe del .venv, creado o rehecho; None si no se pudo. Un .venv cuyo Python arranca se usa, sea de quien
    sea. Se rehace solo el que armó este programa (lleva MARCA), y solo si su Python falta o sale con error; y sin
    borrar antes: el viejo se aparta entero a logs/ (un solo os.replace, que con un archivo retenido adentro falla sin
    mover nada), se crea el nuevo, y recién después se borra el viejo."""
    ruta, python = RAIZ / VENV, python_del_venv()
    if es_enlace(ruta):
        anotar(f"{VENV} es una unión o un enlace: lo quito como enlace, sin tocar lo de adentro")
        try:
            os.rmdir(ruta)
        except OSError:
            try:
                os.unlink(ruta)
            except OSError as e:
                anotar(f"no pude quitar el enlace {VENV}: {e}")
                return None
    if not os.path.lexists(ruta):
        return crear_entorno(ruta, python)
    codigo = codigo_al_arrancar(python)
    if codigo == 0:
        return python
    if not (ruta / MARCA).is_file():
        decir(f"Hay una carpeta {VENV} que no armó este programa, y su Python no arranca: no la toco.")
        anotar(f"{VENV} ajeno cuyo Python no arranca")
        return None
    if codigo is None and python.is_file():
        anotar(f"el Python de {VENV} no se pudo correr (retenido, o venció el plazo): no lo rehago")
        return None
    viejo = RAIZ / "logs" / f"{APARTADO}{int(time.time() * 1000)}"
    try:
        viejo.parent.mkdir(exist_ok=True)
        apartar(ruta, viejo)
    except OSError as e:
        anotar(f"no pude apartar {VENV} para rehacerlo: {e}")
        decir("No pude rehacer el entorno propio del programa: un archivo suyo está en uso. Lo intento la próxima vez.")
        return None
    nuevo = crear_entorno(ruta, python)
    borrar_apartados()
    return nuevo


def instalar(python):
    """Instala requirements.txt en el .venv con el pip del equipo (`pip --python`): con hash de cada rueda y solo ruedas
    ya hechas, así que no corre ningún código de instalación de un paquete. -I: un pip.py de la carpeta del programa
    no corre en lugar del de verdad; si el pip del equipo no está en su carpeta de siempre (el de la tienda lo trae en
    el sitio del usuario), se repite con -E. Devuelve ("listo" | "hash" | "fallo", lo que dijo pip)."""
    salida = ""
    # El segundo intento va con -E y -P (sin la carpeta actual en sys.path): -E solo no la quita en `-m`.
    for banderas in (("-I",), ("-E", "-P")):
        comando = [sys.executable, *banderas, "-m", "pip", "--python", str(python), "install", "--require-hashes",
                   "--only-binary=:all:", "--disable-pip-version-check", "--no-input", "--progress-bar", "off",
                   "--retries", "2", "--timeout", "15", "-r", str(RAIZ / REQUISITOS)]
        codigo, salida = correr(comando, PLAZO_PIP)
        anotar(f"pip {' '.join(banderas)} salió con {codigo}\n{sin_claves(salida).rstrip()}")
        if codigo == 0:
            return "listo", salida
        if HASH_NO_COINCIDE in salida:
            return "hash", salida
        if SIN_PIP not in salida:
            break
    return "fallo", salida


def cola_de(salida):
    lineas = [x.strip() for x in sin_usuario(sin_claves(salida)).splitlines() if x.strip()]
    return lineas[-LINEAS_DE_ERROR:]


def preparar():
    """El código de salida: SALIDA_PROPIO, SALIDA_EQUIPO, o NoPuede si no se puede abrir."""
    inicio = time.monotonic()
    python = entorno_propio()
    huella = huella_de_requisitos()
    propio = python is not None and (RAIZ / VENV / MARCA).is_file()
    fuera = fuera_de_cobertura()
    if python is not None:
        sin = faltan(python, "-I")
        estado = leer_estado()
        pendiente = bool(sin) or estado.get("requisitos") != huella
        if pendiente and reciente(estado.get("intento"), huella):
            # Ya falló hace poco con estos requisitos: no se espera otra vez a pip (unos 65 s sin red, medido por la
            # revisión de código del encargo 84) si el programa puede abrir sin él, con lo necesario ya en el .venv o en
            # el Python del equipo. Pasada PAUSA_REINTENTO, vuelve a probar.
            if not obligatorias_que_faltan(sin) or not obligatorias_que_faltan(faltan(sys.executable, "-E")):
                pendiente = False
        if fuera and pendiente:
            anotar(f"no instalo: este Python {fuera} y requirements.txt no tiene ruedas para él")
            pendiente = False
        if pendiente and propio:
            decir("AQUASHIELD · preparo las librerías del programa (solo la primera vez, o si cambiaron; puede tardar "
                  "un par de minutos)…")
            resultado, salida = instalar(python)
            if resultado == "hash":
                raise NoPuede(["No abrí AQUASHIELD: un archivo que bajé no coincide con su hash.",
                               "No sigas: avisa a quien te dio el programa y mándale logs\\entorno.log."])
            sin = faltan(python, "-I")
            estado = leer_estado()
            if resultado == "listo" and not sin:
                estado["requisitos"] = huella
                estado.pop("intento", None)
                decir(f"Listo en {time.monotonic() - inicio:.0f} s.")
            elif resultado == "fallo":
                estado["intento"] = {"requisitos": huella, "cuando": time.time()}
                decir("No pude instalar las librerías (sin conexión, o falló pip):")
                for linea in cola_de(salida):
                    decir("  " + linea)
            guardar_estado(estado)
        if not obligatorias_que_faltan(sin):
            if sin:
                anotar(f"faltan solo librerías opcionales: {sin}")
            return SALIDA_PROPIO
    elif (RAIZ / VENV).exists():
        anotar(f"{VENV} no se pudo usar")
    sin_equipo = faltan(sys.executable, "-E")
    if not obligatorias_que_faltan(sin_equipo):
        decir("No pude dejar listo el entorno propio del programa: abro con el Python del equipo, que tiene todo lo que "
              "usa.")
        anotar("abro con el Python del equipo")
        return SALIDA_EQUIPO
    faltan_ellas = obligatorias_que_faltan(sin_equipo)
    lineas = [f"No abrí AQUASHIELD: {'falta' if len(faltan_ellas) == 1 else 'faltan'} {nombrar(faltan_ellas)} y no se "
              "pudo instalar."]
    if fuera:
        lineas.append(f"Este Python {fuera}, y las librerías del programa están hechas para Python de 3.11 a 3.14 "
                      "de 64 bits: instala Python 3.13 de 64 bits (python.org) y vuelve a abrirlo.")
    else:
        lineas.append("Revisa la conexión a internet y vuelve a abrirlo. Si sigue igual, avisa a quien te dio el "
                      "programa y mándale logs\\entorno.log.")
    raise NoPuede(lineas)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")      # con -I, PYTHONIOENCODING no cuenta
    except (AttributeError, OSError, ValueError):
        pass
    esperar_a_las_otras_ventanas()
    try:
        return preparar()
    except NoPuede as e:
        anotar("no se puede abrir: " + e.args[0])
        for linea in e.lineas:
            decir(linea)
        return SALIDA_NO_PUEDE
    except Exception:
        # Una falla que nadie previó no deja al programa sin abrir si el Python del equipo ya tiene todo.
        anotar("falla no prevista:\n" + traceback.format_exc())
        if not obligatorias_que_faltan(faltan(sys.executable, "-E")):
            decir("El entorno propio del programa falló: abro con el Python del equipo, que tiene todo lo que usa.")
            return SALIDA_EQUIPO
        decir("No abrí AQUASHIELD: falló la preparación de las librerías. Avisa a quien te dio el programa y mándale "
              "logs\\entorno.log.")
        return SALIDA_NO_PUEDE


if __name__ == "__main__":
    sys.exit(main())
