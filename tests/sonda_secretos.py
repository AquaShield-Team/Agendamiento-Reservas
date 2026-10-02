# -*- coding: utf-8 -*-
"""Sonda de credenciales sobre lo que va a entrar al repo. Nunca imprime valores.

Secretos: 'usuario' y 'clave' no vacíos de config.json (la plantilla está vacía).
Nombre del operador: las palabras de 4 letras o más de su clave en «usuarios», de su
'descripcion' y del 'nombre_en_pantalla' de COSCO, sin distinguir mayúsculas ni tildes.
Los operadores de la plantilla no cuentan (clave usuario<n>, descripción «por rellenar»).
Modos (uno por llamada):
  (sin modo)         índice: cada blob en staging, leído con git cat-file
  --dry-run          lista de `git add -A --dry-run` (no escribe objetos) y su contenido
  --almacen          TODOS los objetos de .git (alcanzables o no); ahí el nombre solo informa
  --negativo-clave   staging + un blob falso con el contenido de config.json -> tiene que dar 1
  --negativo-ruta    staging + rutas falsas prohibidas                    -> tiene que dar 1
  --negativo-nombre  staging + un blob falso por cada término del nombre   -> tiene que dar 1
Salida: 0 limpio · 1 encontró algo · 2 aborta (control positivo fallido).
Correr ANTES de cada commit:  python tests/sonda_secretos.py --dry-run  y, tras el
git add,  python tests/sonda_secretos.py
"""
import fnmatch
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
GIT = str(Path.home() / "AppData/Local/Programs/Git/cmd/git.exe")
LARGO_MINIMO = 4
PROHIBIDAS = ["config.json", "*.json.tmp", "perfiles/*", "logs/*", "*.xlsx", "*.xlsm", "*.xls",
              "*.csv", "~$*", "*.mp4", "*.docx", "*_dump.html", "maersk_sailing.html",
              "SIMULADOR_AQUASHIELD.html", "*.zip", "__pycache__/*", "*.pyc", "_para_borrar/*",
              "*.tmp", "crear_*.py", "generar_manuales.py"]     # los generadores, fuera desde el encargo 44
IMAGENES_PERMITIDAS = set()          # desde el encargo 44 no entra ninguna: el logo quedó fuera del repo
PALABRA = re.compile(r"[^\W\d_]+")
CLAVE_DE_PLANTILLA = re.compile(r"usuario\d*")
MODOS_STAGING = ("--staging", "--negativo-clave", "--negativo-ruta", "--negativo-nombre")


def secretos(cfg):
    out, descartados = [], 0
    for n, (_, datos) in enumerate(cfg.get("usuarios", {}).items(), start=1):
        for nav, c in datos.items():
            if not isinstance(c, dict):
                continue
            for tipo in ("usuario", "clave"):
                v = str(c.get(tipo) or "")
                if not v:
                    continue
                if len(v) < LARGO_MINIMO:
                    descartados += 1
                    continue
                out.append((f"op{n}/{nav}", tipo, v))
    return out, descartados


def datos_de_cuenta(cfg):
    """Los contratos de cada naviera de cada operador (contrato, contrato_usa, contrato_otros), los contratos por
    defecto y el código de Shipper de HYUNDAI de «opciones»: datos de la cuenta que no van al repo (encargo 44). Bloquean
    como el nombre del operador: salvo en --almacen, donde el historial anterior los trae y solo informan."""
    out, descartados = [], 0

    def agregar(etq, tipo, v):
        nonlocal descartados
        v = str(v or "")
        if not v:
            return
        if len(v) < LARGO_MINIMO:
            descartados += 1
            return
        out.append((etq, tipo, v))

    for n, (_, datos) in enumerate(cfg.get("usuarios", {}).items(), start=1):
        for nav, c in (datos.items() if isinstance(datos, dict) else ()):
            if isinstance(c, dict):
                for tipo, v in c.items():
                    if tipo.startswith("contrato"):
                        agregar(f"op{n}/{nav}", tipo, v)
    opciones = cfg.get("opciones") if isinstance(cfg.get("opciones"), dict) else {}
    defecto = opciones.get("contratos_por_defecto")
    for clave, v in (defecto.items() if isinstance(defecto, dict) else ()):
        agregar("opciones/contratos_por_defecto", clave, v)
    agregar("opciones", "codigo_shipper_hyundai", opciones.get("codigo_shipper_hyundai"))
    return out, descartados


def buscar(buf, lista):
    low = buf.lower()
    hits = set()
    for etq, tipo, v in lista:
        cands = [v.encode("utf-8"), v.encode("utf-16-le")]
        base = buf
        if tipo == "usuario":
            cands, base = [c.lower() for c in cands], low
        if any(c in base for c in cands):
            hits.add((etq, tipo))
    return hits


def _plano(texto):
    """Sin tildes y sin mayúsculas: «Núñez», «NUNEZ» y «nunez» quedan iguales."""
    t = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in t if not unicodedata.combining(c)).casefold()


def nombres_del_operador(cfg):
    """El nombre y el apellido de cada operador, tal como los sabe config.json: las palabras de su clave en «usuarios»,
    de su descripción y del nombre con que lo muestra COSCO. Devuelve (términos, palabras cortas que no se buscan)."""
    terminos, cortas = set(), 0
    for clave, datos in (cfg.get("usuarios") or {}).items():
        datos = datos if isinstance(datos, dict) else {}
        desc = str(datos.get("descripcion") or "")
        cosco = datos.get("cosco") if isinstance(datos.get("cosco"), dict) else {}
        fuentes = [str(cosco.get("nombre_en_pantalla") or "")]
        if not CLAVE_DE_PLANTILLA.fullmatch(clave):
            fuentes.append(clave)
        if "rellenar" not in _plano(desc):
            fuentes.append(desc)
        for palabra in (p for f in fuentes for p in PALABRA.findall(_plano(f))):
            if len(palabra) >= LARGO_MINIMO:
                terminos.add(palabra)
            else:
                cortas += 1
    return sorted(terminos), cortas


def con_nombre(entradas, terminos):
    """Las entradas cuya ruta o cuyo contenido (UTF-8 o UTF-16) trae alguno de los términos."""
    out = []
    for ruta, b in entradas:
        texto = "\n".join(_plano(t) for t in (ruta, b.decode("utf-8", "ignore"), b.decode("utf-16-le", "ignore")))
        if any(t in texto for t in terminos):
            out.append(ruta)
    return out


def mostrar(ruta, terminos):
    """La ruta tal cual, salvo que traiga el nombre: entonces no se imprime."""
    return "(ruta con el nombre del operador)" if con_nombre([(ruta, b"")], terminos) else ruta


def codigo_de_salida(modo, hallazgos, rutas_malas, nombres, cuenta=()):
    """1 si algo no puede entrar al repo. El nombre y los datos de la cuenta bloquean salvo en --almacen: el historial
    hasta 9710ae2 trae el nombre, el anterior al encargo 44 trae los contratos, y no se reescribieron (CLAUDE.md, «Git y
    GitHub»), así que ahí solo informan."""
    return 1 if hallazgos or rutas_malas or ((nombres or cuenta) and modo != "--almacen") else 0


def prohibida(ruta):
    r = ruta.replace("\\", "/")
    nombre = r.rsplit("/", 1)[-1]
    if any(fnmatch.fnmatch(r, p) or fnmatch.fnmatch(nombre, p) for p in PROHIBIDAS):
        return True
    return nombre.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webm")) and r not in IMAGENES_PERMITIDAS


def git(*args):
    return subprocess.run([GIT, "-C", str(RAIZ), *args], capture_output=True)


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "--staging"
    crudo = (RAIZ / "config.json").read_bytes()
    real = json.loads(crudo.decode("utf-8"))
    lista, desc = secretos(real)
    n_sec = len(lista)
    if n_sec == 0 or len(buscar(crudo, lista)) != n_sec:
        print(f"ABORTA C1: config.json da {n_sec} secretos o la búsqueda no los encuentra todos")
        sys.exit(2)
    terminos, cortas = nombres_del_operador(real)
    if not terminos or any(not con_nombre([("config.json", crudo)], [t]) for t in terminos):
        print(f"ABORTA C2: config.json da {len(terminos)} términos del nombre del operador o la búsqueda no los "
              "encuentra todos")
        sys.exit(2)
    print(f"C1 ok: {n_sec} secretos desde config.json · descartados por cortos: {desc}")
    print(f"C2 ok: {len(terminos)} términos del nombre del operador desde config.json · palabras de menos de "
          f"{LARGO_MINIMO} letras que no se buscan: {cortas}")
    print(f"plantilla en el árbol: {len(buscar((RAIZ / 'config.example.json').read_bytes(), lista))} secretos")
    cuenta, desc_c = datos_de_cuenta(real)
    if len(buscar(crudo, cuenta)) != len(cuenta):
        print(f"ABORTA C3: config.json da {len(cuenta)} datos de la cuenta y la búsqueda no los encuentra todos")
        sys.exit(2)
    print(f"C3 ok: {len(cuenta)} contratos o datos de la cuenta desde config.json · descartados por cortos: {desc_c}")

    entradas = []
    if modo in MODOS_STAGING:
        for e in git("ls-files", "-s", "-z").stdout.split(b"\0"):
            if e:
                meta, ruta = e.split(b"\t", 1)
                entradas.append((ruta.decode("utf-8"), git("cat-file", "blob", meta.split()[1].decode()).stdout))
        etiqueta = "staging (índice)"
    elif modo == "--dry-run":
        for linea in git("add", "-A", "--dry-run").stdout.decode("utf-8", "replace").splitlines():
            if linea.startswith("add '") and linea.endswith("'"):
                ruta = linea[5:-1]
                entradas.append((ruta, (RAIZ / ruta).read_bytes()))
        etiqueta = "git add -A --dry-run (árbol de trabajo)"
    elif modo == "--almacen":
        p = subprocess.Popen([GIT, "-C", str(RAIZ), "cat-file", "--batch-all-objects", "--batch"],
                             stdout=subprocess.PIPE)
        while True:
            cab = p.stdout.readline()
            if not cab:
                break
            partes = cab.split()
            tam = int(partes[2])
            entradas.append((f"{partes[1].decode()}:{partes[0].decode()[:12]}", p.stdout.read(tam)))
            p.stdout.read(1)
        p.wait()
        etiqueta = "almacén .git (todos los objetos)"
    else:
        print("modo desconocido")
        sys.exit(2)

    if modo == "--negativo-clave":
        entradas.append(("NEGATIVO/falso.txt", crudo))
    if modo == "--negativo-ruta":
        for r in ("config.json", "logs/web_x/log.txt", "perfiles/x/Cookies", "Reservas AQUASHIELD.xlsx",
                  "Manual_Administrador_Agendamiento_Reservas.docx", "logs/web_x/captura.png", "msc_dump.html"):
            entradas.append((r, b""))
    if modo == "--negativo-nombre":
        for i, t in enumerate(terminos, 1):
            entradas.append((f"NEGATIVO/nombre_{i}.txt", f"Lo pidió {t.upper()}.".encode("utf-8")))

    if modo != "--dry-run" and not any(b"def cargar_config" in b for _, b in entradas):
        print(f"ABORTA: ninguna entrada de '{etiqueta}' contiene el texto conocido de AQUASHIELD.py")
        sys.exit(2)

    hallazgos, rutas_malas, en_cuenta = [], [], []
    for ruta, b in entradas:
        h = buscar(b, lista)
        if h:
            hallazgos.append((ruta, sorted(f"{e}:{t}" for e, t in h)))
        hc = buscar(b, cuenta)
        if hc:
            en_cuenta.append((ruta, sorted(f"{e}:{t}" for e, t in hc)))
        if modo != "--almacen" and prohibida(ruta):
            rutas_malas.append(ruta)
    nombres = con_nombre(entradas, terminos)

    print(f"universo: {etiqueta} · entradas: {len(entradas)}")
    print(f"entradas con claves/usuarios: {len(hallazgos)}")
    for r, h in hallazgos:
        print(f"    {mostrar(r, terminos)}: {h}")
    print(f"rutas prohibidas: {len(rutas_malas)} {[mostrar(r, terminos) for r in rutas_malas]}")
    print(f"{'(informativo) ' if modo == '--almacen' else ''}entradas con contratos o datos de la cuenta: "
          f"{len(en_cuenta)} {[mostrar(r, terminos) for r, _ in en_cuenta][:20]}")
    print(f"{'(informativo) ' if modo == '--almacen' else ''}entradas con el nombre o el apellido del operador: "
          f"{len(nombres)} {[mostrar(r, terminos) for r in nombres]}")
    sys.exit(codigo_de_salida(modo, hallazgos, rutas_malas, nombres, en_cuenta))


if __name__ == "__main__":
    main()
