# -*- coding: utf-8 -*-
"""AQUASHIELD · extraer_panel.py (encargo 84, aquachile-brand): saca de AQUASHIELD.py, como archivos, lo que el panel web
sirve, para que el verificador de marca de la skill lo pueda medir. El verificador lee archivos html, css y js, y el
panel los arma en memoria (HTML_INDEX, JS_INDEX, CSS_INDEX y CSS_FUENTES), así que sin este paso no hay nada que medir.

Escribe en <destino>, que no puede existir: index.html, estilo.css, app.js y fuentes.css (con las rutas de la raíz del
servidor pasadas a relativas: con file:// no cargan), las letras de fuentes.css como archivos woff2 en fuentes/ (el
verificador tarda mucho en leerlas en base64), aquashield-estados.json (los estados que el panel muestra con datos,
copiados de esta carpeta, que es donde se versionan), una muestra.xlsx inventada que cargan los pasos de esa
declaración, y un repo de git con un único commit (el verificador recorre lo versionado). No importa el programa: lee las
cuatro constantes con ast. Solo lee el repo del programa.

Control positivo: las cuatro constantes tienen que salir, el HTML traer el header del bloque («aquashield-header») y
fuentes.css traer letras: si no, aborta.

Uso:
    python tests/marca/extraer_panel.py <destino> [<carpeta con AQUASHIELD.py>]
    python "~/.claude/skills/aquachile-brand/snippet/verificar-modulo.py" <destino>
El verificador necesita el Python que tenga playwright (en este equipo, el de la Tienda de Microsoft)."""
import ast
import base64
import os
import re
import shutil
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
CONSTANTES = ("HTML_INDEX", "JS_INDEX", "CSS_INDEX", "CSS_FUENTES")
PATRON_LETRAS = r"url\(data:font/woff2;base64,([A-Za-z0-9+/=]+)\)"
ESTADOS = "aquashield-estados.json"
MUESTRA = "muestra.xlsx"                  # el contenido no importa: el panel de la declaración solo lee su nombre


def leer_constantes(programa):
    """{nombre: texto} de las cuatro constantes del panel, leídas con ast sin importar el programa."""
    with open(programa, encoding="utf-8") as f:
        arbol = ast.parse(f.read())
    consts = {}
    for n in arbol.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            if n.targets[0].id in CONSTANTES:
                consts[n.targets[0].id] = ast.literal_eval(n.value)
    faltan = set(CONSTANTES) - set(consts)
    if faltan or "aquashield-header" not in consts["HTML_INDEX"]:
        sys.exit(f"ABORTA: faltan {sorted(faltan)} o el HTML no trae el header del bloque (control positivo)")
    return consts


def extraer(programa, destino):
    consts = leer_constantes(programa)
    if os.path.exists(destino):
        sys.exit(f"ABORTA: ya existe {destino}")
    os.makedirs(os.path.join(destino, "fuentes"))
    html = (consts["HTML_INDEX"].replace('href="/fuentes.css"', 'href="fuentes.css"')
            .replace('href="/estilo.css"', 'href="estilo.css"').replace('src="/app.js"', 'src="app.js"'))
    cuenta = [0]

    def a_archivo(m):
        cuenta[0] += 1
        nombre = f"fuentes/f{cuenta[0]}.woff2"
        with open(os.path.join(destino, nombre), "wb") as g:
            g.write(base64.b64decode(m.group(1)))
        return f"url({nombre})"

    fuentes_css = re.sub(PATRON_LETRAS, a_archivo, consts["CSS_FUENTES"])
    if not cuenta[0]:
        sys.exit("ABORTA: no encontré letras en base64 en CSS_FUENTES (control positivo)")
    for nombre, texto in (("index.html", html), ("estilo.css", consts["CSS_INDEX"]), ("app.js", consts["JS_INDEX"]),
                          ("fuentes.css", fuentes_css)):
        with open(os.path.join(destino, nombre), "wb") as f:
            f.write(texto.encode("utf-8"))
    shutil.copyfile(os.path.join(AQUI, ESTADOS), os.path.join(destino, ESTADOS))
    with open(os.path.join(destino, MUESTRA), "wb") as f:
        f.write(b"muestra inventada\n")
    # Sin las GIT_* que el entorno traiga (GIT_DIR, GIT_INDEX_FILE, GIT_WORK_TREE: git las exporta a todo hook): con una puesta,
    # `git init` reinicializaría ESE repo, no el destino, y le dejaría core.bare y la identidad de esta copia (revisión de
    # seguridad del encargo 84). Como guarda_datos.py y actualizar.py.
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
    env["GIT_CEILING_DIRECTORIES"] = os.path.dirname(os.path.abspath(destino))
    for cmd in (["init", "-q"], ["config", "user.email", "x@example.invalid"], ["config", "user.name", "x"],
                ["config", "core.autocrlf", "false"], ["add", "-A"], ["commit", "-q", "-m", "panel servido"]):
        r = subprocess.run(["git", "-C", destino, *cmd], capture_output=True, env=env)
        if r.returncode:
            sys.exit(f"ABORTA: git {cmd[0]} salió con {r.returncode}: {r.stderr.decode('utf-8', 'replace')[-300:]}")
    return {"letras": cuenta[0]}


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    repo = os.path.abspath(sys.argv[2]) if len(sys.argv) == 3 else os.path.dirname(os.path.dirname(AQUI))
    datos = extraer(os.path.join(repo, "AQUASHIELD.py"), os.path.abspath(sys.argv[1]))
    print(f"listo en {os.path.abspath(sys.argv[1])}: {datos['letras']} letras. Siguiente: verificar-modulo.py sobre esa carpeta.")
