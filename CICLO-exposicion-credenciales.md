# CICLO · Exposición de las credenciales de `config.example.json`

**Módulo:** Agendamiento Reservas (`C:\dev\Agendamiento Reservas`) · **Fecha:** 2026-09-23 ·
**Método:** skill `metodo-ciclo` v12 · **Tipo:** solo medición. No se modificó ningún archivo del módulo,
no se hizo commit ni push y no se contactó ningún portal.

> Este informe no trae ninguna clave ni usuario. Cada secreto se nombra como `op1/<naviera>` + tipo; las
> sondas los leen desde el propio JSON y nunca los imprimen. La sonda 1, corrida sobre este mismo informe,
> da 0 claves y 0 usuarios.

## Veredicto

**No se cumple ninguna condición de FRENA SI.**
- Ninguna clave aparece en ningún commit: la carpeta no es un repo git, y en el historial completo de los
  17 repos locales hay 0 claves y 0 usuarios.
- El código no usa la plantilla como respaldo: solo lee `config.json`.

**PASO 0: CICLO, con una PREGUNTA abierta.** Hay algo que arreglar y se puede medir: la plantilla es una copia
exacta de las credenciales en uso, y vaciarla no cambia el arranque. Cambiar las claves en los portales es
decisión tuya: depende de si la carpeta salió del equipo, y eso no se mide desde acá.

## Lo que pediste medir

| Pregunta | Resultado | Evidencia |
|---|---|---|
| ¿La carpeta es un repo git? | **No.** | No hay `.git` en la carpeta, en `C:\dev` ni en `C:\`. `git rev-parse --show-toplevel` sale con 128 («not a git repository (or any of the parent directories)»). 0 `.git` en subcarpetas. `GIT_DIR` y `GIT_WORK_TREE` vacías. Control positivo: la misma orden sobre el repo de `metodo-ciclo` sale con 0. |
| ¿Tiene remoto? | No aplica: no hay repo. | — |
| ¿El remoto es público o privado? | No aplica. | — |
| ¿`config.json` está en `.gitignore`? | **No existe ningún `.gitignore`** (0 en toda la carpeta, `perfiles/` incluida). | Ver «Decisiones», punto 3. |
| ¿`config.example.json` o `config.json` aparecen en algún commit? | **En esta carpeta no hay historial.** Extendido a los 17 repos locales: **0**. | 43 658 objetos de todo el almacén de cada repo, alcanzables o no: 31 491 blobs y 12 167 commits, árboles y tags; 0 faltantes. 0 blobs idénticos a cualquiera de los dos archivos. 0 rutas del historial llamadas `config.example.json`, `AQUASHIELD.py` o `AQUASHIELD_EMISION.py`. 0 objetos, incluidos los mensajes de commit, con alguna clave o usuario. Controles positivos 17/17. |
| ¿Esos commits están en el remoto? | No aplica: no hay commits con credenciales. | — |
| ¿`AQUASHIELD.py` lee `config.example.json` como respaldo? | **No.** | Un solo lector de JSON en disco: `cargar_config()` ([AQUASHIELD.py:7460](AQUASHIELD.py:7460)), que lee `BASE / "config.json"` y, si falta, lanza `FileNotFoundError`. La plantilla solo se nombra en ese mensaje de error (línea 7463). Los otros cuatro `json.loads` leen cuerpos HTTP (8773, 8812, 8831, 8884). Los `.bat` no copian la plantilla. Control: el mismo Grep encontró esa única mención conocida. |

## Lo que apareció además

1. **La plantilla es una copia exacta de las credenciales en uso.** Los 8 valores de la plantilla (4 claves y 4
   usuarios del operador 1: CMA, COSCO, ONE y MSC) son **idénticos** en `config.json`: 8 de 8. El operador 2,
   HYUNDAI y MAERSK están vacíos en los dos archivos.
2. **3 de las 4 claves funcionaban hace menos de tres días**, según los logs locales (sin tocar ningún portal). El
   programa teclea la clave de `config.json` y el log registra «Sesión iniciada»:
   - CMA-CGM: 2026-09-21 16:55, en `logs\web_cma_<operador>_20260921_165455\log.txt`;
   - MSC: 2026-09-21 16:32, en `logs\web_msc_<operador>_20260921_163058\log.txt`;
   - COSCO: 2026-09-23 08:44, en `logs\web_cosco_<operador>_20260923_084347\log.txt`.

   En ONE el log dice «Ya había una sesión activa», así que su clave no deja evidencia. «Sesión iniciada» es
   el juicio del propio programa, no una verificación independiente.
3. **Los usuarios aparecen en 4 de los 6 `log.txt`, pero es un solo valor:** el correo que comparten CMA,
   COSCO y MSC. Sale dentro de la URL de login de COSCO y en el campo «booking confirmation sent» del
   formulario de COSCO. **0 claves en los logs.** Archivos: `web_cosco_<operador>_20260922_134605`,
   `web_cosco_<operador>_20260923_084347`, `web_cosco_<operador>_20260923_092515` y `web_todas_<operador>_20260921_145827`.
4. **Lo que se reparte está limpio:** los dos manuales `.docx`, `SIMULADOR_AQUASHIELD.html`, `LEEME.md`,
   `CLAUDE.md` y los scripts generadores tienen 0 claves y 0 usuarios. Las imágenes que llevan adentro no se
   revisaron (ver Residual).
5. **El Manual del Administrador presenta la plantilla como respaldo manual:** «Plantilla modelo para restaurar
   la configuración ante cualquier corrupción» ([generar_manuales.py:639](generar_manuales.py:639) y el
   `.docx` generado). El código no depende de eso; el procedimiento humano, sí. Con la plantilla vacía,
   restaurar desde ella deja todas las credenciales en blanco.
6. **Tampoco hay copias en el resto de `C:\dev`:** fuera de esta carpeta, 0 archivos con esos nombres y 0 `.json`
   con alguna de las claves (566 `.json` revisados, 0 descartados).

## Decisiones para Marcelo

1. **Vaciar la plantilla.** Es seguro para el arranque, porque el código no la lee. Lo que cambia es el
   procedimiento de restauración del manual (punto 5): o se ajusta `generar_manuales.py:639` y se regeneran los
   manuales, o se acepta que restaurar desde la plantilla obliga a volver a escribir las claves (el panel lo
   permite en *Credenciales*).
2. **Cambiar las claves en los portales.** No hay evidencia de exposición en git ni en `C:\dev`. Lo que decide
   es si esta carpeta, o un `.zip` o `.exe` hecho con ella, salió del equipo. `LEEME.md` describe una versión
   anterior que se distribuía con `config.json` junto al `.exe` y pedía mandar la carpeta `logs\`. Eso no se
   mide desde acá.
3. **Si algún día el módulo se versiona:** crear un `.gitignore` con `config.json`, `perfiles/` y `logs/`
   **antes** del primer `git add`. Hoy, un `git init` seguido de `git add .` subiría las dos copias de las
   claves, las sesiones abiertas de `perfiles/` y los logs.

## Universo y cobertura (pieza 3)

| Sonda | Universo | Cubierto | Fuera, con su motivo | Control positivo |
|---|---|---|---|---|
| Secretos buscados | Campos `usuario` y `clave` no vacíos de la plantilla | 8: 4 claves distintas, y 4 entradas de usuario con 2 valores distintos | 0 descartados por cortos (< 4 caracteres). Los `contrato` quedan fuera por definición: son números de contrato comercial y ya están en el código | — |
| 1 · Carpeta | 619 archivos al momento de medir | 25 con texto buscable (`.docx` y `.xlsx` descomprimidos, con y sin etiquetas XML) | 317 `.png` y 2 `.mp4` (sin texto buscable); 275 en `perfiles/` (almacén del navegador); 0 errores | C1: la plantilla da sus 8 secretos · C2: el `.docx` da una frase conocida |
| 2 · Historial git | 17 repos: 15 en `C:\dev`, más `aquachile-brand` y `metodo-ciclo` | 43 658 objetos, todos los tipos | 0 faltantes | Por repo: un trozo de un blob de HEAD y el asunto del último commit, cada uno en su tipo de objeto: 17/17 |
| 3 · Copias en `C:\dev` | 23 692 archivos en 2 621 carpetas | Todos por nombre; 566 `.json` por contenido | 19 carpetas `.git`, `node_modules` o `perfiles` (las `.git` las cubre la sonda 2); 0 `.json` saltados; 0 errores | Los dos `.json` del proyecto, con 4 claves cada uno |
| 4 · Logs | 6 `log.txt` | 6 | 0 | La misma búsqueda que valida C1 |

## Re-medir (pieza 1)

Las sondas van en el Anexo. Guárdalas juntas en una carpeta y córrelas desde PowerShell:

```powershell
$env:PYTHONIOENCODING = "utf-8"
python sonda_carpeta.py   # sonda 1: carpeta, plantilla contra config.json, C1 y C2
python sonda_repos.py     # sonda 2: historial de los 17 repos (unos minutos)
python sonda_copias.py    # sonda 3: copias en C:\dev
python sonda_logs.py      # sonda 4: usuarios distintos y líneas de log enmascaradas
git -C "C:\dev\Agendamiento Reservas" rev-parse --show-toplevel   # 128 = no es repo
```

**Después de vaciar la plantilla**, las sondas ya no pueden leer los secretos desde ella: cambia
`cargar("config.example.json")` por `cargar("config.json")` en cada una, y C1 pasa a exigir 8 secretos en
`config.json`. El resultado esperado es `config.example.json` con 0 claves y `config.json` con 4.

## NO retroceder (pieza 2)

No se modificó nada, así que no hay nada que revertir: lo único nuevo es este informe. Si se vacía la plantilla,
**no vuelvas a generarla copiando `config.json`**. Que coincidan 8 de 8 sugiere que así se llenó; es una
hipótesis, no una medición.

## Defectos de instrumento cazados (pieza 4)

1. **Contaba entradas en vez de valores.** La sonda 1 reportó «3 usuarios» en cada log: eran 3 entradas (CMA,
   COSCO y MSC) de **un solo valor**, el correo compartido. La unidad es el valor distinto; la sonda 4
   recuenta así.
2. **Un salto silencioso en la sonda 3.** La primera versión saltaba sin contarlos los `.json` de más de 1 MB,
   así que su «0 copias» no valía. Con el contador aparecieron 34 saltados; se corrió de nuevo sin tope: 566
   revisados, 0 descartados, el mismo 0.
3. **La sonda 2 solo miraba blobs.** La primera corrida (31 480 blobs, 0 claves) se saltaba los commits, y una
   clave pegada en un mensaje de commit también es exposición. Se corrió de nuevo sobre todos los tipos de
   objeto, con un segundo control positivo (el asunto del último commit de cada repo): el mismo 0. Entre una
   corrida y otra, `Modulo-Invoice-Converter` pasó de 547 a 566 objetos porque otra sesión hizo commits; las
   cifras de este informe son las de la segunda corrida.
4. **Una precaución que no resultó defecto:** en un `.docx`, una palabra puede quedar partida entre varias
   etiquetas `<w:t>`. Por eso la sonda 1 busca en el XML con y sin etiquetas, y C2 lo valida.

## Premisas refutadas y registros contrastados (pieza 5)

- **«Parecen reales (observado por CC, no verificado)»:** no se refutó, se reforzó. Son idénticas a
  `config.json` (8 de 8), y tres de ellas figuran en los logs con inicio de sesión exitoso entre el 21 y el
  23-09. Sigue en pie que no se verificaron contra los portales.
- **Premisa implícita de que la exposición sería por git:** esta carpeta no tiene git, así que las preguntas de
  remoto, visibilidad y commits no aplican. El riesgo está fuera de git («Decisiones», punto 2) y en la falta
  de `.gitignore` para el futuro.
- **Mi `CLAUDE.md` del `/init` de hoy** dice que la plantilla «también trae datos que parecen reales». Ahora está
  medido: son las mismas de `config.json`. No lo corregí, porque el encargo era no modificar nada (ver Residual).
- **El registro de la skill `metodo-ciclo`** («15 repos (los 12 modulos, `Second Brain`, `aquachile-brand` y esta
  skill), un solo remoto cada uno») no coincide con lo medido hoy. Son 17 repos: 15 en `C:\dev` (14 módulos más
  `Second Brain`), más `aquachile-brand` y `metodo-ciclo`. Y `ExportDesk` tiene **dos** remotos, `origin` y
  `respaldo`. No afecta este diagnóstico: ninguno tiene credenciales.

## Residual (pieza 6)

| Qué no se miró | Por qué | Se reabre si… |
|---|---|---|
| Texto dentro de imágenes: 317 capturas de `logs/`, 2 videos `.mp4` y las capturas incrustadas en los manuales | No es texto buscable; haría falta OCR. Los campos de clave de los portales salen enmascarados (hipótesis); un usuario sí podría leerse | …los manuales, los videos o el simulador se van a compartir fuera de AquaChile |
| `perfiles/` (275 archivos) | Es el almacén de Chrome, con las sesiones y cookies de los portales; no se revisa como texto | …la carpeta se copió o se va a copiar a otro equipo: las sesiones abiertas viajan con ella |
| Copias fuera de `C:\dev` y del equipo (correo, OneDrive, pendrive, `.exe` repartidos) | No se mide desde acá | …confirmas que la carpeta o un `.exe` salió del equipo: entonces hay que cambiar las claves |
| Validez actual de las claves en los portales | El encargo pide no verificarlas | …se decide cambiarlas: la clave nueva se prueba iniciando sesión desde el panel |
| La línea de `CLAUDE.md` que dice «parecen reales» | El encargo era no modificar nada | …se vacía la plantilla: esa línea se actualiza en el mismo cambio |
| Visto de paso, fuera de alcance: el panel Tkinter guarda `config.json` con `open(…, "w")` directo ([AQUASHIELD.py:8123](AQUASHIELD.py:8123)), no de forma atómica como la API web | Es otro tema | …un corte a mitad de guardado deja `config.json` truncado, y con la plantilla vacía ya no hay de dónde restaurarlo |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v12**:
- control positivo que aborta: C1, C2, los dos controles por repo, el de la sonda 3 y el de `git rev-parse`;
- todo salto silencioso lleva contador: lo destapó el defecto 2;
- la unidad de la medición la fija el sujeto de la afirmación: el defecto 1;
- todo registro es una hipótesis hasta que se contrasta: el propio `CLAUDE.md` y el registro de la skill;
- declarar las premisas refutadas;
- el residual se declara;
- FRENAR cuando la decisión es de negocio: cambiar las claves y el procedimiento del manual quedan para ti.

El módulo **no tiene reglas de método propias**: no hay un registro previo, y `CLAUDE.md` nació hoy sin sección
de método. **Choques: ninguno.**

## Entregable (pieza 8)

Este `.md`, sin renderizar. Pasó la sonda 1 (0 claves y 0 usuarios) antes de entregarse.

## Anexo · sondas

Copiadas tal cual desde los archivos que produjeron los números de arriba. Leen los secretos del JSON y solo
imprimen `op<n>/<naviera>` y el tipo.

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

<details><summary><code>sonda_carpeta.py</code></summary>

```python
"""Sonda 1: donde aparecen las credenciales de config.example.json dentro de la
carpeta del proyecto. Imprime archivo + (operador/naviera, tipo), nunca el valor.

Universo: todos los archivos bajo la carpeta, salvo perfiles/ (almacen del
navegador; se cuenta y se declara). Controles positivos que ABORTAN:
  C1: config.example.json tiene que contener TODOS los secretos.
  C2: la extraccion de .docx sin etiquetas tiene que encontrar una frase que
      generar_manuales.py escribe en el manual de administrador.
"""
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from secretos import PROYECTO, cargar, secretos, buscar  # noqa: E402

ZIPS = {".docx", ".xlsx", ".pptx"}
SIN_TEXTO = {".png", ".jpg", ".jpeg", ".mp4", ".webm", ".gif"}
TAG = re.compile(rb"<[^>]+>")

ej = cargar("config.example.json")
lista, desc_cortos = secretos(ej)
print(f"secretos en la plantilla: {len(lista)} "
      f"({sum(t == 'clave' for _, t, _ in lista)} claves, "
      f"{sum(t == 'usuario' for _, t, _ in lista)} usuarios) · descartados por cortos: {desc_cortos}")

# --- Comparacion plantilla vs config.json (solo booleanos) ---
try:
    real = cargar("config.json")
    real_idx = {}
    for n, (_, datos) in enumerate(real.get("usuarios", {}).items(), start=1):
        for nav, c in datos.items():
            if isinstance(c, dict):
                for tipo in ("usuario", "clave"):
                    real_idx[(f"op{n}/{nav}", tipo)] = str(c.get(tipo) or "")
    iguales = sum(real_idx.get((e, t)) == v for e, t, v in lista)
    print(f"plantilla vs config.json: {iguales} de {len(lista)} valores IDENTICOS")
    for e, t, v in lista:
        print(f"   {e:14} {t:8} igual_en_config={real_idx.get((e, t)) == v}")
except Exception as ex:
    print(f"no pude comparar con config.json: {type(ex).__name__}")


def contenido_zip(ruta):
    """Bytes crudos de cada miembro + version sin etiquetas XML (une runs)."""
    partes = []
    with zipfile.ZipFile(ruta) as z:
        for m in z.namelist():
            b = z.read(m)
            partes.append(b)
            if m.endswith(".xml"):
                partes.append(TAG.sub(b"", b))
    return b"\n".join(partes)


# --- C2: control positivo de la extraccion .docx ---
manual = PROYECTO / "Manual_Administrador_Agendamiento_Reservas.docx"
frase = "Plantilla modelo para restaurar".encode("utf-8")
if frase not in contenido_zip(manual):
    print("ABORTA: C2 no encontro la frase conocida en el manual (.docx). La sonda no audita.")
    sys.exit(2)
print("C2 ok: la extraccion .docx encuentra la frase conocida")

por_archivo = {}
cont = Counter()
excluidos_perfiles = 0
errores = []
for p in sorted(PROYECTO.rglob("*")):
    if not p.is_file():
        continue
    rel = p.relative_to(PROYECTO)
    if rel.parts[0] == "perfiles":
        excluidos_perfiles += 1
        continue
    ext = p.suffix.lower()
    if ext in SIN_TEXTO:
        cont["sin_texto:" + ext] += 1
        continue
    try:
        buf = contenido_zip(p) if ext in ZIPS else p.read_bytes()
    except Exception as ex:
        errores.append((str(rel), type(ex).__name__))
        continue
    cont["escaneado"] += 1
    h = buscar(buf, lista)
    if h:
        por_archivo[str(rel)] = h

# --- C1: control positivo de la busqueda ---
en_plantilla = por_archivo.get("config.example.json", set())
if len(en_plantilla) != len(lista):
    print(f"ABORTA: C1 encontro {len(en_plantilla)} de {len(lista)} secretos en la plantilla.")
    sys.exit(2)
print(f"C1 ok: la plantilla contiene los {len(lista)} secretos")

print("\n=== archivos con coincidencias (sin valores) ===")
for f, h in por_archivo.items():
    claves = sorted(e for e, t in h if t == "clave")
    usuarios = sorted(e for e, t in h if t == "usuario")
    print(f"{f}\n    claves:   {len(claves)} {claves}\n    usuarios: {len(usuarios)} {usuarios}")

print("\n=== universo ===")
print(f"escaneados: {cont['escaneado']}")
for k, v in sorted(cont.items()):
    if k.startswith("sin_texto"):
        print(f"NO cubiertos (imagen/video, sin texto buscable) {k[10:]}: {v}")
print(f"excluidos perfiles/ (almacen del navegador): {excluidos_perfiles}")
print(f"errores de lectura (descartados): {len(errores)} {errores}")
```

</details>

<details><summary><code>sonda_repos.py</code></summary>

```python
"""Sonda 2: ¿las credenciales de config.example.json estan en el historial de
algun repo git de C:/dev? Imprime repo + objeto + commits, nunca el valor.

Universo: TODOS los objetos del almacen de cada repo (git cat-file
--batch-all-objects), alcanzables o no. Ademas: identidad exacta de blob de
config.example.json y config.json, y rutas del historial con esos nombres.
Control positivo por repo que ABORTA: un trozo de un blob de HEAD tiene que
aparecer en el mismo flujo que se escanea.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from secretos import PROYECTO, cargar, secretos, buscar  # noqa: E402

GIT = str(Path.home() / "AppData/Local/Programs/Git/cmd/git.exe")
REPOS = [p for p in sorted(Path("C:/dev").iterdir()) if (p / ".git").exists()]
REPOS += [p for p in sorted((Path.home() / ".claude/skills").iterdir())
          if (p / ".git").exists()]

lista, _ = secretos(cargar("config.example.json"))


def git(repo, *args, entrada=None):
    return subprocess.run([GIT, "-C", str(repo), *args], capture_output=True,
                          input=entrada)


def hash_obj(ruta):
    return subprocess.run([GIT, "hash-object", str(ruta)], capture_output=True,
                          text=True).stdout.strip()


H_EJ = hash_obj(PROYECTO / "config.example.json")
H_CF = hash_obj(PROYECTO / "config.json")


def control(repo):
    """Toma un blob de HEAD de al menos 64 bytes y devuelve 24 bytes de el."""
    ls = git(repo, "ls-tree", "-r", "-l", "HEAD").stdout.decode("utf-8", "replace")
    for linea in ls.splitlines():
        meta, _, _ = linea.partition("\t")
        partes = meta.split()
        if len(partes) == 4 and partes[1] == "blob" and partes[3].isdigit() and int(partes[3]) >= 64:
            b = git(repo, "cat-file", "blob", partes[2]).stdout
            return b[16:40]
    return None


def control_commit(repo):
    """El asunto del ultimo commit: tiene que aparecer en un objeto commit."""
    s = git(repo, "log", "-1", "--format=%s").stdout.strip()
    return s if len(s) >= 8 else None


def escanear(repo, aguja_control, aguja_commit):
    proc = subprocess.Popen([GIT, "-C", str(repo), "cat-file", "--batch-all-objects", "--batch"],
                            stdout=subprocess.PIPE)
    f = proc.stdout
    blobs = otros = faltantes = 0
    hits = {}
    visto_control = False
    visto_commit = aguja_commit is None
    while True:
        cab = f.readline()
        if not cab:
            break
        partes = cab.split()
        if len(partes) == 2 and partes[1] == b"missing":
            faltantes += 1
            continue
        sha, tipo, tam = partes[0].decode(), partes[1], int(partes[2])
        cuerpo = f.read(tam)
        f.read(1)
        # Se buscan TODOS los tipos: un commit o un tag anotado lleva mensaje,
        # y una clave pegada en un mensaje de commit tambien es exposicion.
        if tipo == b"blob":
            blobs += 1
            if aguja_control and aguja_control in cuerpo:
                visto_control = True
        else:
            otros += 1
            if tipo == b"commit" and aguja_commit and aguja_commit in cuerpo:
                visto_commit = True
        h = buscar(cuerpo, lista)
        if h:
            hits[sha] = (tipo.decode(), h)
    proc.wait()
    return blobs, otros, faltantes, hits, visto_control and visto_commit


total_claves = 0
for repo in REPOS:
    ag = control(repo)
    blobs, otros, falt, hits, ok = escanear(repo, ag, control_commit(repo))
    ident = [n for n, h in (("config.example.json", H_EJ), ("config.json", H_CF))
             if git(repo, "cat-file", "-e", h).returncode == 0]
    rutas = git(repo, "log", "--all", "--format=", "--name-only").stdout.decode("utf-8", "replace")
    rutas_hit = sorted({r for r in rutas.splitlines()
                        if r.rsplit("/", 1)[-1].lower() in ("config.example.json", "aquashield.py", "aquashield_emision.py")})
    estado_ctl = "ok" if ok else ("SIN CONTROL" if ag is None else "FALLO")
    print(f"{repo.name:28} blobs={blobs:>6} otros={otros:>6} faltantes={falt} control={estado_ctl} "
          f"blob_identico={ident or '-'} rutas_con_ese_nombre={len(rutas_hit)}")
    if not ok:
        print(f"   ABORTA este repo: el control positivo no aparecio; su cero no vale.")
        continue
    for r in rutas_hit:
        print(f"   ruta en historial: {r}")
    for sha, (tipo_obj, h) in hits.items():
        claves = sorted(e for e, t in h if t == "clave")
        usuarios = sorted(e for e, t in h if t == "usuario")
        total_claves += len(claves)
        if tipo_obj == "commit":
            commits = git(repo, "log", "-1", "--format=%H %ad", "--date=iso",
                          sha).stdout.decode("utf-8", "replace").strip()
            rutas_obj = ["(mensaje de commit)"]
        else:
            commits = git(repo, "log", "--all", "--format=%H %ad", "--date=iso",
                          f"--find-object={sha}").stdout.decode("utf-8", "replace").strip()
            rutas_obj = git(repo, "log", "--all", "--format=", "--name-only",
                            f"--find-object={sha}").stdout.decode("utf-8", "replace").split()
        print(f"   OBJETO {tipo_obj} {sha[:12]} claves={claves} usuarios={usuarios}")
        print(f"      rutas: {sorted(set(rutas_obj))}")
        for c in commits.splitlines():
            remotas = git(repo, "branch", "-r", "--contains", c.split()[0]).stdout.decode().split()
            print(f"      commit {c}  en_ramas_remotas={remotas or '-'}")

print(f"\nrepos: {len(REPOS)} · claves encontradas en historial (suma por objeto): {total_claves}")
```

</details>

<details><summary><code>sonda_copias.py</code></summary>

```python
"""Sonda 3: copias SIN versionar dentro de C:/dev (fuera de esta carpeta) de la
plantilla, de config.json o de AQUASHIELD.py, por nombre y por contenido.
Por contenido: todo .json de menos de 1 MB se revisa con buscar() (claves).
Control positivo que ABORTA: la propia carpeta del proyecto se recorre tambien
y tiene que dar sus dos .json con las 4 claves."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from secretos import PROYECTO, cargar, secretos, buscar  # noqa: E402

lista, _ = secretos(cargar("config.example.json"))
claves = [x for x in lista if x[1] == "clave"]
NOMBRES = {"config.example.json", "aquashield.py", "aquashield_emision.py"}

por_nombre, por_contenido, control = [], [], []
dirs = archivos = json_revisados = errores = json_grandes = dirs_excluidas = 0
for raiz, subdirs, files in os.walk("C:/dev"):
    antes = len(subdirs)
    subdirs[:] = [d for d in subdirs if d not in (".git", "node_modules", "perfiles")]
    dirs_excluidas += antes - len(subdirs)
    dirs += 1
    for f in files:
        archivos += 1
        p = Path(raiz) / f
        propio = PROYECTO in p.parents
        if f.lower() in NOMBRES and not propio:
            por_nombre.append(str(p))
        if f.lower().endswith(".json"):
            try:
                if p.stat().st_size > 2_000_000_000:
                    json_grandes += 1
                    continue
                h = buscar(p.read_bytes(), claves)
            except Exception:
                errores += 1
                continue
            json_revisados += 1
            if h:
                (control if propio else por_contenido).append((str(p), len(h)))

print(f"control (carpeta propia): {control}")
if sorted(n for _, n in control) != [4, 4]:
    print("ABORTA: el control no encontro los dos .json del proyecto con 4 claves.")
    sys.exit(2)
print(f"recorrido: {dirs} carpetas, {archivos} archivos, {json_revisados} .json revisados, "
      f"errores (descartados) {errores}; .json > 2 GB sin revisar (descartados) {json_grandes}; "
      f"carpetas excluidas .git/node_modules/perfiles: {dirs_excluidas}")
print(f"copias por nombre fuera del proyecto: {len(por_nombre)}")
for x in por_nombre:
    print("   ", x)
print(f".json con alguna de las claves fuera del proyecto: {len(por_contenido)}")
for x in por_contenido:
    print("   ", x)
```

</details>

<details><summary><code>sonda_logs.py</code></summary>

```python
"""Cuantos valores DISTINTOS de usuario hay, y en que lineas de log.txt aparecen
(con el valor enmascarado). Nunca imprime el valor."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from secretos import PROYECTO, cargar, secretos  # noqa: E402

lista, _ = secretos(cargar("config.example.json"))
usuarios = {}
for e, t, v in lista:
    if t == "usuario":
        usuarios.setdefault(v.lower(), []).append(e)
print(f"usuarios en la plantilla: {sum(len(x) for x in usuarios.values())} entradas, "
      f"{len(usuarios)} valores distintos")
for i, (v, etqs) in enumerate(usuarios.items(), start=1):
    print(f"   valor U{i}: usado por {etqs}")

claves = [v for e, t, v in lista if t == "clave"]
print(f"claves: {len(claves)} entradas, {len(set(claves))} valores distintos")

logs = sorted((PROYECTO / "logs").rglob("log.txt"))
print(f"\nlog.txt en logs/: {len(logs)}")
for p in logs:
    texto = p.read_text(encoding="utf-8", errors="replace")
    lineas = texto.splitlines()
    hits = []
    for n, l in enumerate(lineas, start=1):
        enm = l
        toco = False
        for i, v in enumerate(usuarios, start=1):
            if v in enm.lower():
                enm = re.sub(re.escape(v), f"<U{i}>", enm, flags=re.I)
                toco = True
        if toco:
            hits.append((n, enm.strip()[:150]))
    print(f"{p.relative_to(PROYECTO)}: {len(hits)} linea(s) de {len(lineas)}")
    for n, l in hits[:6]:
        print(f"   L{n}: {l}")
```

</details>

