# CICLO · Repo git local con los secretos y datos reales fuera desde el primer commit

**Módulo:** Agendamiento Reservas (`C:\dev\Agendamiento Reservas`) · **Fecha:** 2026-09-23 ·
**Método:** skill `metodo-ciclo` v12 · **Commits:** `14aa9ef` (repo inicial) y el de este informe · **Remoto:**
ninguno; no hubo push.

> Este informe no trae datos reales: ni claves, ni usuarios, ni nombres. El operador aparece como `<op1>`.
> La sonda de staging se corre sobre este mismo informe antes de su commit, y tiene que dar 0.

## Veredicto

**No se cumplió ninguna condición de FRENA SI.**
- **La sonda sobre el staging dio 0.** Revisó 15 entradas buscando los 12 secretos de `config.json`: 0 claves o
  usuarios y 0 rutas prohibidas. Sus dos negativos, corridos de a uno, salieron con 1.
- **Regenerar el manual cambió solo ese texto.** Se comparó parte por parte:
  - en el manual de administrador cambia 1 de 26 partes (`word/document.xml`), y el XML base, con el texto viejo
    reemplazado una sola vez por el nuevo, es idéntico byte a byte al regenerado;
  - el manual de usuario no cambia.

  Los dos negativos del control salieron con 1.
- **El programa arranca sin lo que quedó fuera.** Se probó sobre el árbol que sale del índice
  (`git checkout-index`), sin nada de lo ignorado:
  - sin `config.json`, el panel web levanta, sirve la página, `app.js`, los estilos y las fuentes, y
    `/api/config` responde 500 con el aviso de copiar la plantilla (ese comportamiento ya existía);
  - con la plantilla copiada como `config.json`, `/api/config` responde 200, con el modo emisión en `false`,
    2 operadores y 0 credenciales.

**PASO 0: CICLO, cerrado.**

## Qué quedó hecho

| Pieza | Estado |
|---|---|
| Repo | `git init` local, rama `master` (por defecto en la configuración de sistema), identidad de la configuración global, **sin remoto**. 1 commit de código (`14aa9ef`) y 1 de este informe. |
| `.gitignore` | **Lista blanca:** `/*` deja fuera todo lo de la raíz, y `!/…` nombra lo que entra. Debajo, una **capa explícita** con los mínimos pedidos, que funciona aunque alguien quite `/*` (ver Universo). |
| `.gitattributes` | `* text=auto eol=lf` y `*.png binary`. Los 15 archivos ya usaban LF, y el `core.autocrlf=true` del sistema los habría devuelto con CRLF al clonar. |
| `config.example.json` | Mismas 62 claves JSON, en el mismo orden. Usuario, clave y contrato quedan vacíos en las 6 navieras de los 2 operadores. `descripcion` pasa a «Operador 1 (rellenar)». `_comentario` dice que viene sin credenciales y que al restaurar hay que volver a escribir las claves. Se mantienen `opciones`, las URL y el EOL (LF, 79 líneas, sin salto final). |
| `generar_manuales.py:639` | La fila de la plantilla agrega: «Viene sin usuarios, claves ni contratos: al restaurar hay que volver a escribir las claves de cada naviera.» |
| Manual de administrador | Regenerado en una carpeta aislada e instalado de forma atómica (938 830 bytes). El de usuario no se reemplazó: su contenido regenerado es idéntico. |
| `CLAUDE.md` | Sección «Git (local, sin remoto)». La nota de credenciales ahora dice que la plantilla viene vacía y por qué. |

### Lo que entró en `14aa9ef` (15 archivos)

`.gitattributes`, `.gitignore`, `AQUASHIELD.py`, `AQUASHIELD_EMISION.py`, `Iniciar AQUASHIELD.bat`,
`Iniciar AQUASHIELD_EMISION.bat`, `config.example.json`, `CLAUDE.md`, `LEEME.md`,
`CICLO-exposicion-credenciales.md`, `generar_manuales.py`, `crear_simulador_html.py`,
`crear_video_demostracion.py`, `crear_video_tutorial.py` y `logo_aquachile_dark.png` (79 863 bytes). El logo es
la única imagen versionada: no muestra datos y lo usa `generar_manuales.py`.

### Lo que quedó fuera: ubicación, cantidad y peso

Son 607 archivos y 132,78 MB en total (`git status --ignored`). Los 15 versionados más los 607 ignorados dan 622,
y no queda ningún archivo sin rastrear.

| Ubicación | Cantidad | Peso | Por qué queda fuera |
|---|---|---|---|
| `logs\web_cma_<op1>_20260921_165455\` | 27 capturas + `log.txt` | 3,36 MB en capturas | Los logs registran corridas en **modo emisión real**: `EMITIDA` aparece en 5 de los 6 `log.txt` y «MODO EMISIÓN REAL» en 5. Las capturas muestran reservas reales. |
| `logs\web_cosco_<op1>_20260922_134605\` | 19 + `log.txt` | 4,18 MB | ídem |
| `logs\web_cosco_<op1>_20260923_084347\` | 12 + `log.txt` | 3,06 MB | ídem |
| `logs\web_cosco_<op1>_20260923_092515\` | 31 + `log.txt` | 7,86 MB | ídem |
| `logs\web_msc_<op1>_20260921_163058\` | 41 + `log.txt` | 3,44 MB | ídem |
| `logs\web_todas_<op1>_20260921_145827\` | 186 + `log.txt` | 28,99 MB | ídem |
| **Subtotal `logs/`** | **316 capturas + 6 `log.txt`** | **51,06 MB** | |
| `Demostracion_AQUASHIELD_Reservas.mp4` | 1 video | 26,66 MB | Hecho con capturas de corridas reales |
| `Tutorial_Paso_a_Paso_AQUASHIELD.mp4` | 1 video | 34,74 MB | ídem |
| `Manual_Administrador_Agendamiento_Reservas.docx` | 1 manual con 7 imágenes incrustadas | 0,90 MB | Las imágenes son capturas de `logs/` |
| `Manual_Usuario_Agendamiento_Reservas.docx` | 1 manual con 7 imágenes incrustadas | 0,89 MB | ídem |
| `SIMULADOR_AQUASHIELD.html` | 1 página con 36 referencias a capturas de `logs/` | 0,05 MB | Es una salida generada que muestra esas capturas |
| `Reservas AQUASHIELD.xlsx` | 1 planilla | 0,01 MB | Planilla de reservas |
| `config.json` | 1 | < 0,01 MB | Credenciales |
| `perfiles/` | 275 archivos | 17,56 MB | Sesiones y cookies de Chrome en los portales (no se revisó por dentro) |
| `__pycache__/` | 3 | 0,90 MB | Compilados de Python |

## Decisiones tomadas dentro del encargo, y por qué

1. **Valores vacíos en la plantilla, no marcadores.** El encargo permitía cualquiera de los dos. Lo que hace el
   código con cada uno:
   - el modo login salta la naviera cuando el usuario está vacío ([AQUASHIELD.py:7520](AQUASHIELD.py:7520));
   - el panel informa `tiene_clave = bool(clave)`, así que un «TU_CLAVE» aparecería como clave guardada;
   - los `login_*` teclean `creds["usuario"]` tal cual (líneas 422, 504 y 821), así que un marcador llegaría al
     portal real.
2. **Se conservan las claves JSON de los operadores**, como pide el encargo («mismas claves y estructura»).
   El nombre real que había en `descripcion` es un valor, y pasa al marcador que ya usaba el operador 2.
3. **Los generadores entran como código; el simulador HTML no, porque es su salida.** Los números de booking de
   los generadores son secuencias (…900, …901, …902). En los logs aparecen 0 de los 6 que se probaron: lucen
   inventados. Además traen nombres de naves, rutas y números de contrato, que también están en `AQUASHIELD.py`.
4. **Solo se reemplazó el manual de administrador.** El de usuario no incluye la tabla de archivos, y su
   regeneración salió idéntica en contenido.

## Universo y cobertura (pieza 3)

| Sonda | Universo | Resultado | Control positivo | Negativo que muerde |
|---|---|---|---|---|
| Secretos | Todos los `usuario`/`clave` no vacíos de `config.json` | 12: 6 claves y 6 usuarios; 4 valores de usuario distintos; 0 descartados por cortos | La búsqueda encuentra los 12 en `config.json`: gate **relativo**, aborta si da otro número | — |
| Plantilla nueva | `config.example.json` | 0 secretos | (el mismo) | — |
| `--dry-run` | Lista de `git add -A --dry-run`, antes de escribir objetos | 15 entradas, 0 claves o usuarios, 0 rutas prohibidas, **0 objetos en `.git`** | Texto conocido de `AQUASHIELD.py` | — |
| Staging | Los 15 blobs del índice (`git ls-files -s` + `cat-file`) | **0** y 0 rutas prohibidas; corrida también justo antes del commit | Texto conocido en el blob de `AQUASHIELD.py` | `--negativo-clave`: 1 hallazgo, sale con 1 · `--negativo-ruta`: 7 rutas prohibidas, sale con 1 |
| Almacén `.git` | Todos los objetos tras `14aa9ef`: 15 blobs, 1 árbol y 1 commit | 0 | Texto conocido | — |
| `.gitignore` | 12 rutas mínimas con `check-ignore -v`, más la capa explícita sola (sin `/*`) en un repo de prueba con 19 archivos | Las 12 caen en una regla explícita. Sin `/*`, entran solo los 3 versionables que había y un `nuevo_script.py` cualquiera (lo que `/*` agrega); los 16 prohibidos quedan fuera | El logo, `AQUASHIELD.py` y la plantilla salen como versionados | — |
| EOL | Los 15 archivos | Árbol del índice 15/15 idéntico byte a byte; clon 15/15 idéntico | — | — |
| Manual | 26 partes de cada `.docx` | Línea base = originales (0 partes distintas). Nuevo contra línea base: solo `document.xml` del de administrador, solo ese texto | La línea base reproduce los originales | Sin cambio: sale con 1 · con un cambio extra en el mismo XML: sale con 1 |
| Arranque | Árbol del índice, puerto 18765, `abrir=False` | Sin config: arranca, `/api/config` responde 500 con el aviso · con plantilla: 200, emisión `false`, 0 credenciales | Carpeta real: OK | Caso «plantilla» sin `config.json`: sale con 1 |
| Otros repos | 17 repos, todos sus objetos, con los **12** secretos | 0 (controles 17/17) | Blob de HEAD y asunto del último commit | — |
| Carpeta | Archivos con texto, con los 12 secretos | Claves solo en `config.json`; en `logs/`, solo el correo compartido (4 `log.txt`) | `config.json` da sus 12 | — |

## Re-medir (pieza 1)

Las sondas van en el Anexo. Guárdalas juntas y córrelas desde PowerShell:

```powershell
$env:PYTHONIOENCODING = "utf-8"
python sonda_staging.py                   # staging: tiene que dar 0 (exit 0)
python sonda_staging.py --dry-run         # antes de un git add: lo que entraría, sin escribir objetos
python sonda_staging.py --almacen         # todo .git
python sonda_staging.py --negativo-clave  # tiene que salir con 1
python sonda_staging.py --negativo-ruta   # tiene que salir con 1
python test_arranque.py "<árbol limpio>" 18765 plantilla   # con config.json copiado de la plantilla
python inventario_fuera.py                # lo que queda fuera: ubicación, cantidad, peso
git -C "C:\dev\Agendamiento Reservas" checkout-index -a --prefix="<carpeta vacía>\"   # árbol limpio del índice
```

Para el manual: `python manual_regen.py generar <dir>` corre el generador aislado (copia script, logo y `logs/`), y
`python manual_gate.py <dir con regen_base y regen_nuevo>` decide si cambió solo ese texto.

## NO retroceder (pieza 2)

- **No vuelvas a llenar la plantilla copiando `config.json`.** Así se había filtrado.
- **No quites `/*` del `.gitignore`**, no agregues un `!` para planillas, capturas o manuales, y no uses
  `git add -f` sobre algo ignorado.
- **Nunca hagas `git add` de `config.json`, ni por un instante.** Aunque después lo saques del índice, el blob con
  las claves queda en `.git/objects` hasta un `git gc --prune=now`. Por eso este ciclo corrió `--dry-run` antes de
  escribir cualquier objeto.
- **No borres `.gitattributes`:** con el `core.autocrlf=true` del sistema, los clones volverían con CRLF.
- **El manual de administrador anterior no se guardó**, y no hace falta: la línea base demostró que el generador
  lo reproduce idéntico en contenido si se revierte la línea 639.

## Defectos de instrumento cazados (pieza 4)

1. **Un número fijo en el control C1.** La sonda de staging exigía 8 secretos, la cuenta de la plantilla vieja.
   Abortó al leer `config.json`, que tiene 12. Ahora el gate es relativo: todos los que haya.
2. **`check-ignore -v` también imprime las reglas de negación.** La primera lectura clasificó como IGNORADOS el
   logo y `AQUASHIELD.py`, que salían por `!/…`. Ahora un patrón con `!` se lee como versionado.
3. **El ciclo anterior buscó solo 8 de 12 secretos.** Sus sondas sacaban los secretos de la plantilla, que no
   tenía HYUNDAI ni MAERSK. Se corrieron de nuevo la carpeta y los 17 repos con los 12: mismo resultado.
4. **Una precaución, no un defecto:** el `--dry-run` se corrió antes del `git add` para que ningún blob con
   secretos llegara a existir. El almacén final lo confirma: 17 objetos, 0 secretos.

## Premisas refutadas y registros contrastados (pieza 5)

- **«config.example.json es copia exacta de config.json (4 usuarios y 4 claves)».** Era una copia **parcial**:
  coincidía en CMA, COSCO, ONE y MSC, pero `config.json` trae además usuario y clave de HYUNDAI y MAERSK, así que
  son 12 secretos (defecto 3).
- **«Las 317 capturas».** Hay 316 en `logs/`. La 317 del conteo anterior era `logo_aquachile_dark.png`, que no es
  una captura y sí entra al repo.
- **«4 logs traen el correo compartido».** Confirmado con los 12 secretos: los mismos 4 `log.txt` y el mismo
  valor.
- **La regla `git-workflow.md`** dice que la atribución está «disabled globally via settings.json». Ni
  `settings.json` tiene esa clave, ni los commits recientes de `Modulo-Invoice-Converter` y `Proformas` le hacen
  caso: llevan `Co-Authored-By`. Seguí esa convención.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| El nombre de pila del operador está en 8 archivos versionados: como clave JSON de la plantilla (por decisión), en rutas de `logs\` dentro de los generadores y del informe anterior, en 2 ejemplos de `CLAUDE.md` y en 2 líneas de `AQUASHIELD.py` (un comentario y el texto de ayuda de un diálogo). Su apellido aparece en 1: la heurística de sesión de COSCO ([AQUASHIELD.py:958](AQUASHIELD.py:958)) | No es un secreto ni una reserva, y cambiarlo tocaba código fuera del encargo | …el repo va a tener un remoto o se va a compartir fuera del equipo |
| En un clon limpio, los generadores no reproducen el material. `generar_manuales.py` sale con exit 0, pero sin `logs/` omite las capturas **sin avisar** (~120 KB en vez de ~935 KB por manual). El simulador apunta a 36 capturas que no existen. Los videos no se probaron | Dependen de `logs/`, que por decisión queda fuera | …los manuales o el simulador tienen que poder regenerarse solo desde el repo |
| El panel Tkinter, los `.bat` y `main()` en el puerto 8765 no se probaron | Abren ventanas o tocarían una instancia en uso; se probó `lanzar_web`, que es el camino por defecto de `main()` | …se cambia el arranque o los lanzadores |
| Sin `config.json`, el panel web levanta pero `/api/config` responde 500. No se vio cómo lo muestra la página | Comportamiento previo; el aviso de copiar la plantilla viene del servidor | …alguien nuevo va a usar un clon |
| El código trae datos de empresa: números de contrato, dirección y los nombres de las carpetas de logs dentro de los generadores | No son credenciales ni reservas | …se decide limpiar el código para compartirlo |
| Siguen del ciclo anterior: el texto dentro de las imágenes (ahora fuera del repo), `perfiles/` sin revisar, el `open(…, "w")` no atómico del panel Tkinter ([AQUASHIELD.py:8123](AQUASHIELD.py:8123)) y la decisión de cambiar las claves en los portales | Fuera de este encargo | Sus condiciones, en `CICLO-exposicion-credenciales.md` |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v12**:
- **Re-medir contra HEAD antes de diseñar:** el PASO 0 volvió a medir la plantilla, el EOL, la configuración de
  git y los datos de los generadores.
- **Control positivo que aborta:** C1 relativo, lectura del staging, carpeta real en el arranque, línea base del
  manual.
- **El negativo tiene que morder, de a uno por llamada:** 2 en el staging, 2 en el manual y 1 en el arranque.
- **Un número fijo deja de morder:** defecto 1.
- **Un chequeo de sintaxis no prueba el contrato:** el arranque se probó por HTTP, no con `py_compile`.
- **Cada reemplazo afirma que su viejo aparece exactamente una vez, y la escritura es atómica:** el Edit es
  único; la plantilla se escribió con `.tmp`, `fsync` y `os.replace`; el manual, con `.tmp` y `os.replace`; el
  gate del manual exige que el texto viejo aparezca 1 vez.
- **El EOL se preserva y se verifica:** 15/15 en el árbol del índice y en el clon.
- **El cambio y su guardián, en la misma operación:** el `CLAUDE.md` va en el mismo commit que el cambio; el
  `.gitignore` trae su capa explícita.
- **Todo registro es una hipótesis:** premisas de 12 secretos y 316 capturas, y la nota de atribución.
- **Se declaran el residual y las premisas refutadas.**
- **FRENAR:** las tres condiciones del encargo se midieron antes del commit, salvo el clon, que exige un commit.
- **El push se entrega, no se hace:** no hay remoto, así que no hay nada que entregar.

El módulo no tiene reglas de método propias: su `CLAUDE.md` trae la sección Git, pero no reglas de método.
**Choques: ninguno.**

## Entregable (pieza 8)

Este `.md`, sin renderizar. Antes de su commit pasa la sonda de staging.

## Anexo · sondas

Copiadas tal cual desde los archivos que produjeron los números. Leen los secretos y los nombres desde
`config.json` y solo imprimen etiquetas (`op<n>/<naviera>`) o marcadores.

<details><summary><code>secretos.py</code></summary>

```python
"""Carga las credenciales de config.example.json SIN imprimirlas.

Cada secreto se identifica por (operador n, naviera, tipo); el valor nunca sale
de este proceso. Los contratos no cuentan: son numeros de contrato comercial y
ya estan escritos en el codigo (no son credenciales).
"""
import json
from pathlib import Path

PROYECTO = Path("C:/dev/Agendamiento Reservas")
LARGO_MINIMO = 4


def cargar(nombre="config.example.json"):
    return json.loads((PROYECTO / nombre).read_text(encoding="utf-8"))


def secretos(cfg):
    """Lista de (etiqueta, tipo, valor). etiqueta = 'op<n>/<naviera>'."""
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


def buscar(buf: bytes, lista):
    """Devuelve las (etiqueta, tipo) que aparecen en buf. Clave: exacta.
    Usuario: sin distinguir mayusculas. Prueba UTF-8/ASCII y UTF-16LE."""
    low = buf.lower()
    hits = set()
    for etq, tipo, v in lista:
        cands = [v.encode("utf-8"), v.encode("utf-16-le")]
        base = buf
        if tipo == "usuario":
            cands = [c.lower() for c in cands]
            base = low
        if any(c in base for c in cands):
            hits.add((etq, tipo))
    return hits
```

</details>

<details><summary><code>sonda_staging.py</code></summary>

```python
"""Sonda de credenciales sobre lo que va a entrar al repo. Nunca imprime valores.

Secretos: usuario y clave no vacios de config.json (la plantilla ya esta vacia).
Modos (uno por llamada):
  --dry-run         lista de `git add -A --dry-run` (no escribe objetos) y contenido del arbol
  (sin modo)        indice: cada blob en staging, leido con git cat-file
  --almacen         TODOS los objetos de .git (alcanzables o no)
  --negativo-clave  staging + un blob falso con el contenido de config.json -> tiene que dar 1
  --negativo-ruta   staging + rutas falsas prohibidas                    -> tiene que dar 1
Salida: 0 limpio · 1 encontro algo · 2 aborta (control positivo fallido).
"""
import fnmatch
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from secretos import PROYECTO, cargar, secretos, buscar  # noqa: E402

GIT = str(Path.home() / "AppData/Local/Programs/Git/cmd/git.exe")
modo = sys.argv[1] if len(sys.argv) > 1 else "--staging"

PROHIBIDAS = ["config.json", "*.json.tmp", "perfiles/*", "logs/*", "*.xlsx", "*.xlsm", "*.xls",
              "*.csv", "~$*", "*.mp4", "*.docx", "*_dump.html", "maersk_sailing.html",
              "SIMULADOR_AQUASHIELD.html", "*.zip", "__pycache__/*", "*.pyc", "_para_borrar/*",
              "*.tmp"]
IMAGENES_PERMITIDAS = {"logo_aquachile_dark.png"}


def prohibida(ruta):
    r = ruta.replace("\\", "/")
    nombre = r.rsplit("/", 1)[-1]
    if any(fnmatch.fnmatch(r, p) or fnmatch.fnmatch(nombre, p) for p in PROHIBIDAS):
        return True
    if nombre.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webm")) and r not in IMAGENES_PERMITIDAS:
        return True
    return False


def git(*args, entrada=None):
    return subprocess.run([GIT, "-C", str(PROYECTO), *args], capture_output=True, input=entrada)


# --- Secretos y control C1 ---
real = cargar("config.json")
lista, desc = secretos(real)
# Gate RELATIVO al universo: todos los secretos que tenga config.json, sean cuantos sean.
n_sec = len(lista)
if n_sec == 0 or len(buscar((PROYECTO / "config.json").read_bytes(), lista)) != n_sec:
    print(f"ABORTA C1: config.json da {n_sec} secretos o la busqueda no los encuentra todos")
    sys.exit(2)
nombres = [d.get("descripcion", "") for d in real.get("usuarios", {}).values()
           if len(d.get("descripcion", "")) >= 4 and "rellenar" not in d.get("descripcion", "")]
print(f"C1 ok: {n_sec} secretos desde config.json "
      f"({sum(t == 'clave' for _, t, _ in lista)} claves, {sum(t == 'usuario' for _, t, _ in lista)} usuarios)"
      f" · descartados por cortos: {desc} · nombres reales buscados aparte: {len(nombres)}")
en_plantilla = buscar((PROYECTO / "config.example.json").read_bytes(), lista)
print(f"plantilla en el arbol: {len(en_plantilla)} secretos")

# --- Universo segun el modo ---
entradas = []          # (ruta, bytes)
if modo in ("--staging", "--negativo-clave", "--negativo-ruta"):
    ls = git("ls-files", "-s", "-z").stdout.split(b"\0")
    for e in ls:
        if not e:
            continue
        meta, ruta = e.split(b"\t", 1)
        sha = meta.split()[1].decode()
        entradas.append((ruta.decode("utf-8"), git("cat-file", "blob", sha).stdout))
    etiqueta = "staging (indice)"
elif modo == "--dry-run":
    out = git("add", "-A", "--dry-run").stdout.decode("utf-8", "replace")
    for linea in out.splitlines():
        if linea.startswith("add '") and linea.endswith("'"):
            ruta = linea[5:-1]
            entradas.append((ruta, (PROYECTO / ruta).read_bytes()))
    etiqueta = "git add -A --dry-run (arbol de trabajo)"
elif modo == "--almacen":
    p = subprocess.Popen([GIT, "-C", str(PROYECTO), "cat-file", "--batch-all-objects", "--batch"],
                         stdout=subprocess.PIPE)
    while True:
        cab = p.stdout.readline()
        if not cab:
            break
        partes = cab.split()
        sha, tipo, tam = partes[0].decode(), partes[1].decode(), int(partes[2])
        cuerpo = p.stdout.read(tam)
        p.stdout.read(1)
        entradas.append((f"{tipo}:{sha[:12]}", cuerpo))
    p.wait()
    etiqueta = "almacen .git (todos los objetos)"
else:
    print("modo desconocido"); sys.exit(2)

if modo == "--negativo-clave":
    entradas.append(("NEGATIVO/falso.txt", (PROYECTO / "config.json").read_bytes()))
if modo == "--negativo-ruta":
    for r in ("config.json", "logs/web_x/log.txt", "perfiles/x/Cookies", "Reservas AQUASHIELD.xlsx",
              "Manual_Administrador_Agendamiento_Reservas.docx", "logs/web_x/captura.png", "msc_dump.html"):
        entradas.append((r, b""))

# --- Control positivo de lectura del universo ---
aguja = b"def cargar_config"
if not any(aguja in b for _, b in entradas):
    print(f"ABORTA: ninguna entrada de '{etiqueta}' contiene el texto conocido de AQUASHIELD.py")
    sys.exit(2)

hallazgos, rutas_malas, con_nombre = [], [], []
for ruta, b in entradas:
    h = buscar(b, lista)
    if h:
        hallazgos.append((ruta, sorted(f"{e}:{t}" for e, t in h)))
    if modo != "--almacen" and prohibida(ruta):
        rutas_malas.append(ruta)
    if any(n.lower().encode("utf-8") in b.lower() for n in nombres):
        con_nombre.append(ruta)

print(f"universo: {etiqueta} · entradas: {len(entradas)} · control de lectura ok")
if modo != "--almacen":
    for ruta, _ in entradas:
        print(f"    {ruta}")
print(f"entradas con claves/usuarios: {len(hallazgos)}")
for r, h in hallazgos:
    print(f"    {r}: {h}")
print(f"rutas prohibidas: {len(rutas_malas)} {rutas_malas}")
print(f"(informativo) entradas con el nombre real del operador: {len(con_nombre)} {con_nombre}")
sys.exit(1 if hallazgos or rutas_malas else 0)
```

</details>

<details><summary><code>test_arranque.py</code></summary>

```python
"""Arranca el panel web de AQUASHIELD desde <dir> y lo recorre por HTTP.

Uso: python test_arranque.py <dir> <puerto> <caso>
  sin_config   -> sin config.json: el servidor arranca; /api/config da 500 con el aviso
  plantilla    -> config.json copiado de la plantilla: /api/config 200, modo_emision False,
                  operadores de la plantilla y NINGUNA clave guardada
  real         -> carpeta real (control positivo): /api/config 200, modo_emision False
Sale con 0 si el caso se cumple, 1 si no. Nunca abre el navegador (abrir=False) y usa un
puerto propio para no tocar un AQUASHIELD que este corriendo en el 8765.
"""
import importlib.util
import json
import os
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

d, puerto, caso = Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
os.environ.pop("AQUASHIELD_EMITIR", None)
fallos = []

with socket.socket() as s:                      # el puerto tiene que estar libre ANTES
    try:
        s.bind(("127.0.0.1", puerto))
    except OSError:
        print(f"ABORTA: el puerto {puerto} esta ocupado"); sys.exit(2)

sys.path.insert(0, str(d))
spec = importlib.util.spec_from_file_location("AQUASHIELD", d / "AQUASHIELD.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print(f"importado desde {d} · BASE={mod.BASE} · VERSION={mod.VERSION}")
if Path(mod.BASE).resolve() != d.resolve():
    fallos.append("BASE no apunta a la carpeta probada")

hilo = threading.Thread(target=mod.lanzar_web, kwargs={"puerto": puerto, "abrir": False}, daemon=True)
hilo.start()
base = f"http://127.0.0.1:{puerto}"


def get(ruta):
    try:
        with urllib.request.urlopen(base + ruta, timeout=5) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


for _ in range(50):
    try:
        get("/api/estado"); break
    except Exception:
        time.sleep(0.2)
else:
    print("ERROR: el servidor no respondio en 10 s"); sys.exit(1)

for ruta, marca in (("/", b"<html"), ("/app.js", b"fetch"), ("/estilo.css", b"{"),
                    ("/fuentes.css", b"@font-face"), ("/api/estado", b"corriendo")):
    st, cuerpo = get(ruta)
    ok = st == 200 and marca in cuerpo
    print(f"GET {ruta:14} {st} · {len(cuerpo):>7} bytes · contiene {marca!r}: {marca in cuerpo}")
    if not ok:
        fallos.append(f"{ruta} -> {st}")

st, cuerpo = get("/api/config")
print(f"GET /api/config    {st} · {cuerpo[:160].decode('utf-8', 'replace')}")
if caso == "sin_config":
    if st != 500 or b"No existe config.json" not in cuerpo:
        fallos.append("sin config.json se esperaba 500 con el aviso de copiar la plantilla")
else:
    if st != 200:
        fallos.append(f"/api/config -> {st}")
    else:
        cfg = json.loads(cuerpo)
        if cfg.get("modo_emision") is not False:
            fallos.append("modo_emision no es False")
        if not cfg.get("usuarios"):
            fallos.append("sin operadores")
        if caso == "plantilla":
            for op in cfg["usuarios"]:
                st2, c2 = get(f"/api/credenciales?usuario={op}")
                cr = json.loads(c2)
                con_clave = [n["clave"] for n in cr["navieras"] if n["tiene_clave"]]
                con_usuario = [n["clave"] for n in cr["navieras"] if n["usuario"]]
                print(f"GET /api/credenciales {op}: {st2} · navieras={len(cr['navieras'])} "
                      f"con clave={con_clave} con usuario={con_usuario}")
                if con_clave or con_usuario:
                    fallos.append(f"la plantilla trae credenciales para {op}")

req = urllib.request.Request(base + "/api/apagar", data=b"{}", method="POST")
urllib.request.urlopen(req, timeout=5).read()
hilo.join(timeout=6)
print(f"apagado limpio: {not hilo.is_alive()}")
if hilo.is_alive():
    fallos.append("el servidor no se apago")

print("RESULTADO:", "OK" if not fallos else f"FALLA {fallos}")
sys.exit(1 if fallos else 0)
```

</details>

<details><summary><code>manual_regen.py</code></summary>

```python
"""Regenera los manuales en una carpeta AISLADA y los compara parte por parte.

Uso:
  python manual_regen.py preparar          respalda los .docx originales
  python manual_regen.py generar <dir>     copia script+logo+logs a <dir> y corre el generador ahi
  python manual_regen.py comparar <a.docx> <b.docx>
Nunca escribe en la carpeta del proyecto.
"""
import difflib
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

PROY = Path("C:/dev/Agendamiento Reservas")
AQUI = Path(__file__).parent
RESP = AQUI / "respaldo_manuales"
MANUALES = ["Manual_Usuario_Agendamiento_Reservas.docx", "Manual_Administrador_Agendamiento_Reservas.docx"]


def preparar():
    RESP.mkdir(exist_ok=True)
    for m in MANUALES:
        dst = RESP / m
        if dst.exists():
            print(f"ya respaldado: {m} ({dst.stat().st_size} bytes)")
            continue
        shutil.copy2(PROY / m, dst)
        assert dst.read_bytes() == (PROY / m).read_bytes()
        print(f"respaldado: {m} ({dst.stat().st_size} bytes)")


def generar(destino):
    d = Path(destino)
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    shutil.copy2(PROY / "generar_manuales.py", d)
    shutil.copy2(PROY / "logo_aquachile_dark.png", d)
    shutil.copytree(PROY / "logs", d / "logs")
    r = subprocess.run([sys.executable, "generar_manuales.py"], cwd=d, capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    print(r.stdout[-600:])
    if r.returncode:
        print("ERROR:", r.stderr[-1500:])
        sys.exit(1)
    for m in MANUALES:
        print(f"generado: {d / m} ({(d / m).stat().st_size} bytes)")


def texto_parrafos(xml: bytes):
    """Texto de cada parrafo (<w:p>) del documento, en orden."""
    s = xml.decode("utf-8")
    out = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", s, flags=re.S):
        out.append("".join(re.findall(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", p)))
    return out


def comparar(a, b):
    za, zb = zipfile.ZipFile(a), zipfile.ZipFile(b)
    na, nb = set(za.namelist()), set(zb.namelist())
    print(f"partes: {len(na)} vs {len(nb)} · solo en A: {sorted(na - nb)} · solo en B: {sorted(nb - na)}")
    distintas = []
    for n in sorted(na & nb):
        if za.read(n) != zb.read(n):
            distintas.append(n)
    print(f"partes con CONTENIDO distinto: {len(distintas)} de {len(na & nb)} -> {distintas}")
    meta = sum(1 for n in sorted(na & nb) if za.getinfo(n).date_time != zb.getinfo(n).date_time)
    print(f"partes con fecha de zip distinta (metadato del contenedor, no contenido): {meta}")
    for n in distintas:
        if n == "word/document.xml":
            ta, tb = texto_parrafos(za.read(n)), texto_parrafos(zb.read(n))
            print(f"  document.xml: {len(ta)} vs {len(tb)} parrafos")
            dif = [l for l in difflib.unified_diff(ta, tb, lineterm="", n=0) if not l.startswith(("---", "+++"))]
            for l in dif:
                print("   ", l[:300])
            # ¿El XML difiere en algo mas que ese texto? Se reemplaza el texto viejo por el nuevo
            # en A y se compara el XML entero.
            return distintas, ta, tb, za.read(n), zb.read(n)
    return distintas, None, None, None, None


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "preparar":
        preparar()
    elif cmd == "generar":
        generar(sys.argv[2])
    elif cmd == "comparar":
        comparar(sys.argv[2], sys.argv[3])
```

</details>

<details><summary><code>manual_gate.py</code></summary>

```python
"""Gate del manual: el regenerado tiene que diferir de la linea base SOLO en el
texto de la fila de config.example.json. Sale con 1 si cambia algo mas.

Prueba: (1) el manual de usuario, identico en contenido; (2) en el de
administrador, una sola parte distinta (word/document.xml); (3) reemplazando
en el XML base el texto viejo por el nuevo -una sola vez- el XML queda
IDENTICO byte a byte al regenerado.
"""
import sys
import zipfile
from xml.sax.saxutils import escape

AQUI = sys.argv[1]
VIEJO = "Plantilla modelo para restaurar la configuración ante cualquier corrupción."
NUEVO = ("Plantilla modelo para restaurar la configuración ante cualquier corrupción. Viene sin "
         "usuarios, claves ni contratos: al restaurar hay que volver a escribir las claves de cada naviera.")
fallos = []


def partes(ruta):
    z = zipfile.ZipFile(ruta)
    return {n: z.read(n) for n in z.namelist()}


u_base = partes(f"{AQUI}/regen_base/Manual_Usuario_Agendamiento_Reservas.docx")
u_nuevo = partes(f"{AQUI}/regen_nuevo/Manual_Usuario_Agendamiento_Reservas.docx")
dif_u = [n for n in u_base if u_base[n] != u_nuevo.get(n)] + [n for n in u_nuevo if n not in u_base]
print(f"usuario: partes distintas = {len(dif_u)} {dif_u}")
if dif_u:
    fallos.append("el manual de usuario cambio")

a_base = partes(f"{AQUI}/regen_base/Manual_Administrador_Agendamiento_Reservas.docx")
a_nuevo = partes(f"{AQUI}/regen_nuevo/Manual_Administrador_Agendamiento_Reservas.docx")
dif_a = [n for n in a_base if a_base[n] != a_nuevo.get(n)] + [n for n in a_nuevo if n not in a_base]
print(f"administrador: partes distintas = {len(dif_a)} {dif_a}")
if dif_a != ["word/document.xml"]:
    fallos.append(f"el manual de administrador cambia en {dif_a}, no solo en word/document.xml")

xml_base = a_base["word/document.xml"].decode("utf-8")
xml_nuevo = a_nuevo["word/document.xml"].decode("utf-8")
v, n = escape(VIEJO), escape(NUEVO)
cuenta = xml_base.count(v)
print(f"texto viejo en el XML base: {cuenta} vez/veces · texto nuevo en el XML nuevo: {xml_nuevo.count(n)}")
if cuenta != 1:
    fallos.append(f"el texto viejo aparece {cuenta} veces en el XML base (se esperaba 1)")
else:
    igual = xml_base.replace(v, n) == xml_nuevo
    print(f"XML base con el texto reemplazado == XML regenerado: {igual}")
    if not igual:
        fallos.append("el XML difiere en algo mas que ese texto")

if fallos:
    print("FRENA:", fallos)
    sys.exit(1)
print("GATE OK: solo cambia el texto de la fila de config.example.json")
```

</details>

<details><summary><code>vaciar_plantilla.py</code></summary>

```python
"""Vacia config.example.json conservando claves JSON y estructura.

- usuario / clave / contrato de cada naviera -> "" (vacio: el programa lo trata
  como "sin credenciales" y salta la naviera; un marcador se mandaria al portal).
- descripcion con nombre real -> marcador "Operador N (rellenar)".
- _comentario -> dice que viene vacia y que al restaurar hay que reescribir claves.
- opciones y url publicas: sin cambio.
Valida ANTES de escribir, escribe a .tmp y reemplaza. Nunca imprime valores viejos.
"""
import copy
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from secretos import secretos  # noqa: E402

RUTA = Path("C:/dev/Agendamiento Reservas/config.example.json")
crudo = RUTA.read_bytes()
assert b"\r" not in crudo and not crudo.endswith(b"\n"), "EOL inesperado: se esperaba LF sin EOL final"
viejo = json.loads(crudo.decode("utf-8"))

nuevo = copy.deepcopy(viejo)
nuevo["_comentario"] = (
    "Copia este archivo como config.json y completa usuario, clave y contrato de cada naviera "
    "(o hazlo desde el panel, en Credenciales). Viene sin credenciales: si restauras la "
    "configuración desde aquí, hay que volver a escribir las claves. Las credenciales NUNCA "
    "salen de tu equipo.")
cambios = ["_comentario"]
for n, (op, datos) in enumerate(nuevo["usuarios"].items(), start=1):
    if datos.get("descripcion") != f"Operador {n} (rellenar)":
        datos["descripcion"] = f"Operador {n} (rellenar)"
        cambios.append(f"usuarios.{op}.descripcion")
    for nav, c in datos.items():
        if not isinstance(c, dict):
            continue
        for campo in ("usuario", "clave", "contrato"):
            if c.get(campo):
                c[campo] = ""
                cambios.append(f"usuarios.{op}.{nav}.{campo}")


def rutas(o, pre=""):
    if isinstance(o, dict):
        out = []
        for k, v in o.items():
            out.append(f"{pre}{k}")
            out += rutas(v, f"{pre}{k}.")
        return out
    return []


# Validaciones antes de tocar el archivo
assert rutas(viejo) == rutas(nuevo), "cambio la estructura o el orden de las claves JSON"
restantes, _ = secretos(nuevo)
assert not [s for s in restantes if s[1] in ("usuario", "clave")], "quedan credenciales en la plantilla"
for op, datos in nuevo["usuarios"].items():
    for nav, c in datos.items():
        if isinstance(c, dict):
            assert c.get("url", "") == viejo["usuarios"][op][nav].get("url", ""), "cambio una url"
assert nuevo["opciones"] == viejo["opciones"], "cambiaron las opciones"

texto = json.dumps(nuevo, ensure_ascii=False, indent=2)
json.loads(texto)  # parsea
tmp = RUTA.with_name(RUTA.name + ".tmp")
with open(tmp, "w", encoding="utf-8", newline="\n") as f:
    f.write(texto)
    f.flush()
    os.fsync(f.fileno())
os.replace(tmp, RUTA)

final = RUTA.read_bytes()
print(f"campos cambiados: {len(cambios)}")
for c in cambios:
    print("   ", c)
print(f"estructura identica: True · claves JSON: {len(rutas(nuevo))}")
print(f"EOL: CRLF={final.count(b'\r\n')} LF={final.count(b'\n')} · EOL final: {final.endswith(b'\n')} · bytes={len(final)}")
print(f"tmp residual: {tmp.exists()}")
```

</details>

<details><summary><code>inventario_fuera.py</code></summary>

```python
"""Inventario de lo que quedo fuera del commit: ubicacion, cantidad y peso.
Los nombres de operador (claves de config.json) se enmascaran en las rutas
como <opN>; se leen del archivo, no se escriben aca."""
import json
import re
import subprocess
import zipfile
from collections import defaultdict
from pathlib import Path

P = Path("C:/dev/Agendamiento Reservas")
GIT = str(Path.home() / "AppData/Local/Programs/Git/cmd/git.exe")
OPS = list(json.loads((P / "config.json").read_text(encoding="utf-8"))["usuarios"])


def mb(n):
    return f"{n / 1_048_576:.2f} MB"


def mask(s):
    for n, op in enumerate(OPS, start=1):
        s = re.sub(rf"_{re.escape(op)}_", f"_<op{n}>_", s, flags=re.I)
    return s


# 1. Capturas en logs/, por carpeta
print("=== logs/ (capturas y log.txt)")
tot_png = tot_png_b = 0
for d in sorted((P / "logs").iterdir()):
    pngs = list(d.glob("*.png"))
    otros = [f for f in d.iterdir() if f.is_file() and f.suffix.lower() != ".png"]
    b = sum(f.stat().st_size for f in pngs)
    tot_png += len(pngs); tot_png_b += b
    print(f"  logs\\{mask(d.name)}\\ : {len(pngs)} png, {mb(b)} · otros: {[f.name for f in otros]}")
print(f"  TOTAL png en logs/: {tot_png}, {mb(tot_png_b)}")

# 2. Videos
print("=== videos")
for f in sorted(P.glob("*.mp4")):
    print(f"  {f.name}: {mb(f.stat().st_size)}")

# 3. Imagenes dentro de los manuales
print("=== manuales (.docx) e imagenes incrustadas")
for f in sorted(P.glob("*.docx")):
    z = zipfile.ZipFile(f)
    media = [i for i in z.infolist() if i.filename.startswith("word/media/")]
    print(f"  {f.name}: {mb(f.stat().st_size)} · {len(media)} imagenes incrustadas, "
          f"{mb(sum(i.file_size for i in media))} sin comprimir")

# 4. Simulador
sim = P / "SIMULADOR_AQUASHIELD.html"
t = sim.read_text(encoding="utf-8", errors="replace")
refs = re.findall(r"logs/[^\"')\s]+\.png", t)
print(f"=== {sim.name}: {mb(sim.stat().st_size)} · {len(refs)} referencias a capturas de logs/ "
      f"({len(set(refs))} distintas)")

# 5. Resto de lo ignorado, agrupado
print("=== todo lo ignorado por git, agrupado")
out = subprocess.run([GIT, "-C", str(P), "status", "--ignored", "--porcelain", "-uall"],
                     capture_output=True, text=True, encoding="utf-8").stdout
grupos = defaultdict(lambda: [0, 0])
for linea in out.splitlines():
    if not linea.startswith("!! "):
        continue
    r = linea[3:].strip('"')
    f = P / r
    top = r.split("/")[0] + ("/" if "/" in r else "")
    grupos[top][0] += 1
    grupos[top][1] += f.stat().st_size if f.exists() else 0
tot = [0, 0]
for k, (n, b) in sorted(grupos.items()):
    print(f"  {mask(k):52} {n:>4} archivo(s)  {mb(b)}")
    tot[0] += n; tot[1] += b
print(f"  TOTAL ignorado: {tot[0]} archivos, {mb(tot[1])}")
```

</details>

