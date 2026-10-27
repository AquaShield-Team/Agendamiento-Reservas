# CICLO-entorno-propio · Encargo 84: aplicar a Agendamiento Reservas las skills del equipo que le corresponden

> **metodo-ciclo v39.** Base: `main` en `71413ea`, con el trabajo de este encargo en el árbol sin commitear. **Tres commits:** uno por
> skill que se aplicó (`d0266f5` y `9c48de3`) y este informe. **No se subió nada:** el bloque de push está al final.
> Sin datos de clientes en este informe: todo lo medido sale de datos inventados o de cuentas.

## Qué se pidió y qué salió

El encargo: dejar el programa robusto en cualquier equipo aplicando las skills del equipo que le correspondan y todavía no
cumpla, un commit por skill. El detonante, medido el 2026-10-26: el `python` del PATH de este equipo pasó a ser el 3.13.15 de
python.org, que no trae `playwright` ni `openpyxl` (los trae el de la Tienda de Microsoft), así que el panel no abría.

**Veredicto del PASO 0: CICLO.** Había algo que arreglar y se podía medir. De las skills del equipo, **dos se aplican y dejaron commit**
(`lanzador-modulo`, en su parte del entorno propio, y `aquachile-brand`); una ya se cumplía; el resto se frenó o no corresponde, y
queda como propuesta con lo que cambiaría.

## Inventario de skills, medido contra el código

| Skill | ¿Aplica? | Ya cumplía | Faltaba | Qué se hizo |
|---|---|---|---|---|
| `lanzador-modulo` | Sí | El `.bat` de doble clic en un solo bloque, la actualización desde `estable` al abrir, el puerto siguiente libre sin cerrar un programa ajeno, un candado de emisión que los `.bat` no tocan | Un entorno propio con requisitos con hash y cada librería comprobada, sin terminal; ofrecer Python y Git con winget | **Commit 1.** `preparar_entorno.py` + `requirements.txt` + los dos `.bat`. Adoptar el lanzador común de la skill (su `lanzador.py`, la tabla de puertos, los modos, el acceso directo): **propuesta**, toca la actualización y el arranque (FRENA) |
| `aquachile-brand` | Sí: el panel y la salida de los lanzadores | La paleta, el tema claro y oscuro y la tipografía en casi todo el panel | El bloque estándar v48 (header, pie, tema, nombre de usuario) y varios hallazgos del verificador (contraste, peso de la letra, color de estado) | **Commit 2.** El panel migrado al bloque; el verificador de la skill, en OK salvo `tinte-estado` en SIN DECIDIR (4 discos sin texto que medir). La salida en texto de los `.bat` no lleva marca: es del lanzador común (FRENA) |
| `panel-escritorio-tkinter` | Sí, el panel de respaldo (`python AQUASHIELD.py panel`) | Su identidad (`MARCA`) y su estructura | Nada que el código no hiciera | Sin commit |
| `empaquetar-exe-windows` | No | — | Pasar a `.exe` cambia cómo se distribuye el programa | **FRENA.** Propuesta abajo |
| `automatizacion-portales` | Sí, para revisar | Las reglas duras de la skill, en su mayor parte; la parada antes de emitir | Un choque con su «Límite que no se cruza» (abajo) | Sin cambios en cómo se llenan los portales (FRENA). Propuestas abajo |
| `manual-modulo` | Sí | No hay manual de uso del módulo en el repo | Una página con la marca y su PDF, de una sola fuente | **Propuesta.** Es un encargo aparte |
| `metodo-ciclo` | Sí | — | — | Aplicado (v39): clones para los revisores, barrido de datos reales, la suite sobre el árbol de cada commit |
| `auditoria-blindaje`, `playwright-py-skill` | No | — | — | No corresponden: el módulo ya tiene su red de verificación y no es un sitio que probar |

## Commit 1 · `d0266f5` · el entorno propio (`lanzador-modulo`)

**Qué hace.** Los dos `.bat` corren `preparar_entorno.py` después de `actualizar.py` y antes de abrir el panel. Crea `.venv` en la
carpeta del programa y le instala `requirements.txt` con el pip del equipo: 9 paquetes, cada uno con versión fija y con el sha256
de cada rueda (`--require-hashes --only-binary=:all:`, sin ejecutar código de instalación de nadie). Sin permisos de
administrador y sin terminal. Con el `.venv` listo solo comprueba que cada librería se importe. Si no puede (sin red, o pip falla)
pero el Python del equipo ya tiene todo, abre con ese; si no, lo dice y no abre. Los `.bat` ofrecen instalar Python y Git con
winget, solo para el usuario y con una pregunta antes. El detalle y sus límites están en `CLAUDE.md`, «Ejecutar y verificar».

**Lo que no cambia** (los FRENA del encargo, comprobados): `Iniciar AQUASHIELD.bat` sigue sin emitir nunca (solo el de emisión abre
`AQUASHIELD_EMISION.py`); `test_candado` y `AQUASHIELD.py` no se tocaron en este commit; `actualizar.py` ni su llamada cambiaron; no se
cierra un programa ajeno y se toma el puerto siguiente libre; los datos reales siguen fuera del repo. Instalar las librerías no pide
administrador (una prueba lo fija).

**Medido** (2026-10-26 y 27, con datos inventados):
- **En un clon limpio desde una rama `estable` local** (un script del encargo, en su carpeta de trabajo y sin versionar: un origen local con `estable` en `d0266f5`, `git
  clone -b estable`, el `.bat` con el `python` de python.org del PATH, el que no tiene las librerías): el primer arranque salió con 0 en
  24,3 s (con la caché de pip tibia; sin caché, 43 s medidos antes), el panel contestó en el 8765, en modo prueba, y lo corría el
  `pythonw` del `.venv` del clon. El segundo arranque, 2,8 s.
- **La suite completa sobre el árbol del commit:** 984 pruebas, OK (1 omitida), en 1.173 s. El censo de sus mutaciones: 137 pares
  mutación-prueba, todos muerden (4 fallaron al primer pase, 2 por un texto viejo que mi arreglo había cambiado y 2 que no mordían, y se
  corrigieron).

## Commit 2 · `9c48de3` · la marca del panel (`aquachile-brand`)

El panel web lleva el bloque estándar v48 de la skill, pegado tal cual; Credenciales y Cerrar AQUASHIELD pasaron a una barra de
contexto con los mismos `id`; el tema viejo (`aq-tema`) se migra solo; los estados, las insignias del modo y los pesos de la letra se
ajustaron a lo que mide el verificador. El detalle está en `CLAUDE.md`, «Interfaz y marca».

**Medido:**
- **El verificador de la skill** sobre el panel extraído (`tests/marca/extraer_panel.py`, con dos estados declarados): todos los
  chequeos en OK, salvo `tinte-estado` en SIN DECIDIR (los discos detrás de los íconos no llevan texto en su instancia viva o están
  ocultos). `version` acepta v48. Los 7 tintes de estado declarados dan «gana sólo en CLARO, que es lo que v4 prescribe».
- **A ojo, en el navegador:** claro, oscuro y 375 px; la nota del modo queda a la vista a 1366 × 520 y 660 y a 375 × 812, y la página
  no desborda.
- **La suite completa sobre el árbol del commit:** 999 pruebas, OK (1 omitida), en 981 s. Las 59 mutaciones de la lectura del panel y
  las 128 de marca (151 pares): todas muerden.

## Revisiones (Opus, en clones dentro de la carpeta del encargo)

**Del lanzador.** *De código:* el PATH con una entrada entre comillas y un paréntesis (como `Program Files (x86)`) cerraba el bloque del
`.bat` antes de correr nada (ahora `%PATH:"=%`); pip sin red esperaba su plazo en cada inicio (ahora una falla reciente no se espera
30 minutos si el programa ya puede abrir); el nieto de pip no se cerraba al vencer el plazo (ahora se cierra el árbol de procesos); el
Python sin GIL o x64 emulado en ARM no se detectaba (ahora por `sysconfig`); los códigos de salida de 12 en adelante; la pregunta por
Git en cada inicio (ahora una vez, con una marca); winget en ARM64 (`--architecture x64`); un mutante repetido y una prueba sin
mutante. *De seguridad:* **1 por la regla del encargo**: la forma corta 8.3 del nombre de usuario de Windows en un comentario de
`tests/test_entorno.py` (el repo es público; la guarda de datos no ve esa forma), corregida; y 4 bajos corregidos: el preparador cargaba
módulos de la carpeta del programa (ahora `python -I`), `sin_claves` dejaba parte de una clave con arroba y un `?token=`, el log y la
pantalla traían la ruta con el usuario (ahora `%USERPROFILE%`), y la frase de Git que decía «si pide permisos, no instala» (con
permisos, sí instala; ahora «si Windows pide permisos y no los tienes, no se instala»). Quedan documentados: un `.venv` ajeno que
arranca se usa sin la garantía del hash, la segunda ventana espera hasta 20 minutos y una unión apartada se queda en `logs\`.

**Del panel.** *De código:* 1 medio y 5 bajos. El medio: la barra de contexto (57 px) dejaba la nota del modo (seguro o EMISIÓN) fuera de
la vista en ventanas de 754 a 809 px de alto, medido contra el commit anterior (ahora 35 px y el panel desplaza sus widgets, no la
nota). Los bajos: la prueba no fijaba el color de «revisar» ni de «procesando…», `test_marca` vigilaba textos y no reglas, dos frases
de `CLAUDE.md` que el código no cumplía, la insignia del modo en negrita sintetizada y una regla huérfana (`.mono`). *De seguridad:* sin
críticos; **1 medio**, el extractor heredaba `GIT_DIR` y podía reinicializar otro repo (corregido, con prueba y mutación), y 1 bajo, el
aviso de EMISIÓN, que cambió de aspecto (te lo dejo para que decidas). Dos propuestas que no son defectos de este commit: endurecer la
CSP con hashes (hoy es solo `frame-ancestors`; el commit agregó un script en línea y un `onclick`), y que el campo del nombre acepte HTML
arrastrado (viene del bloque de la skill, igual que antes).

## Decisiones tomadas (Modo autónomo)

| Decisión | Por qué | Cómo se revierte |
|---|---|---|
| Python de 3.11 a 3.14, de 64 bits, con GIL | `greenlet 3.3.1` no publica ruedas con hash para 3.15, 32 bits, ARM nativo ni 3.14t; fuera de ahí no se intenta instalar y se abre con el Python del equipo si ya lo tiene todo | Cambiar `PYTHON_MAXIMO` y regenerar `requirements.txt` |
| Un `.venv` por carpeta; solo uno con su marca se rehace | No tocar el entorno de otra persona | — |
| **No sumé `opencv`/`numpy`** | Su único uso es resolver la verificación de COSCO sola, y `automatizacion-portales` («Límite que no se cruza») dice que eso no se automatiza. Sin ellos el programa ya hace lo que esa skill pide: detecta la verificación y le pide el paso manual al operador | Agregar las dos librerías a `requirements.txt` con sus hashes (pregunta abajo) |
| La marca va solo en lo que ve el operador | Lo pediste | — |
| JetBrains Mono, de 700 y 800 a 400 | La letra vendorizada trae solo 400: el navegador sintetizaba la negrita | Vendorizar la cara 700 (propuesta) |
| El fondo de un estado, neutro en oscuro | `aquashield.md`, v4 | — |
| Las insignias del modo, a clases con la paleta | Daban 2,54 y 3,76 de contraste. **Cambia cómo se ve el aviso de EMISIÓN** (borde naranja de 2 px en vez de rojo lleno) | Volver a las dos reglas `.modo-insignia` |
| La barra de contexto de 35 px, y el panel izquierdo desplazando solo sus widgets | La revisión midió la nota del modo fuera de la vista | — |
| La declaración de estados y el extractor, en `tests/marca/` | El panel se arma en memoria: el verificador de la skill necesita archivos | — |

## Propuestas que quedaron sin aplicar (FRENA)

1. **Adoptar el lanzador común de `lanzador-modulo`** (su `lanzador.py`, la tabla única de puertos, el modo básico, el acceso directo con
   el isotipo, la salida con la marca). Cambiaría cómo se actualiza y se abre el programa: hoy es el `.bat` con `actualizar.py`; pasaría
   a ser el `lanzador.py` de la skill con su `modulo.json`. Es la «actualización desde estable» del FRENA.
2. **`empaquetar-exe-windows`:** un `.exe` con PyInstaller. Cambia la forma de distribuir; los colegas ya reciben el programa por git.
3. **`automatizacion-portales`:** su «Límite que no se cruza» choca con tres cosas que el módulo ya tenía: `resolver_cosco_puzzle` (resuelve
   la verificación de COSCO con `opencv`), `resolver_cma_slider` (no se llama desde el encargo 53) y el disfraz del navegador (`STEALTH_JS` y
   `--disable-blink-features=AutomationControlled`, que `CLAUDE.md` ya marca como decisión tuya). Propongo que el login de COSCO pida siempre
   el paso manual y que se quite el disfraz; lo decides tú, porque cambia cómo se llenan los portales.
4. **`manual-modulo`:** un manual de uso con la marca y su PDF, de una sola fuente. Encargo aparte.
5. **Vendorizar JetBrains Mono 700,** si quieres la negrita real en el registro y los widgets.
6. **CSP con hashes** para los scripts en línea del panel, calculados al arrancar desde `HTML_INDEX` (propuesta de la revisión de seguridad).

## Para decidir tú

1. ¿`opencv` para el puzzle de COSCO? Mi recomendación: no (arriba). Si lo quieres igual, es tuyo: se agrega a `requirements.txt` con sus
   hashes y el login vuelve a resolver solo.
2. ¿El aviso de EMISIÓN con borde naranja, o con el rojo lleno de antes (el texto blanco sobre ese rojo da 3,76)?
3. ¿Adoptamos el lanzador común de la skill? Es el cambio que más se parece a lo que pedía el encargo, y el que más toca.

## Lo que salió mal, y lo medido de la máquina

- **Mi primera prueba de punta a punta midió mal.** Capturé la salida del `.bat` por una tubería, y el `pythonw` que abre con `start`
  heredó la tubería: `subprocess.run` esperó a que el panel muriera (su vigilante lo apaga a los 90 s sin sondeos). Dio 132,9 s y 94,5 s
  y «el panel no contesta». Con la salida a un archivo: 24,3 s y 2,8 s. **Medido de la máquina** (candidato a fila de «Entorno Windows»):
  un `.bat` que abre un programa con `start` le deja heredada la salida redirigida a quien lo corrió.
- **Una prueba existente que mis pruebas parciales no vieron.** `test_envio` cuenta que `.rs-aviso {` salga una sola vez en el CSS, y mi
  regla nueva lo repetía: la vio la suite completa sobre el árbol del commit. Por eso esa suite es una compuerta y no un trámite.
- **Mutantes que fallaron al primer pase,** 5: 2 del lanzador con un texto viejo que mi arreglo había cambiado, 2 del lanzador que no
  mordían (una cadena de prueba mal escrita y una prueba sin la forma con barras inclinadas) y 1 del panel (un selector con la palabra
  «nada», que el panel sí trae). Los corregí antes de commitear.
- **La herramienta Bash junta los pares de barras invertidas** (`\\` pasa a `\`): varias veces las perdí al escribir con un heredoc y volví
  a Edit. Es la fila ya conocida del entorno.
- **`OSError 22` al escribir `AQUASHIELD.py`** con el parche, una vez: Windows con el archivo abierto un instante (otra fila conocida). El
  parche ahora reintenta unos segundos.
- **Un Python distinto en cada lugar:** `python` (el del PATH) no tiene las librerías; el de la Tienda, sí. Las pruebas y el verificador
  de la skill corren con el de la Tienda; el arranque real, con el `.venv`.
- **No se probó en 3.11 ni 3.12:** en este equipo solo hay 3.13. El rango lo dicen `requirements.txt` y `fuera_de_cobertura`.

## Residual

- `tinte-estado`, SIN DECIDIR: los 4 discos detrás de íconos (no es un hallazgo ni una aprobación).
- La tabla con filas se midió con una API falsa, no con una corrida real ni con un portal; el aviso de EMISIÓN nuevo no se vio con la
  emisión abierta de verdad (el candado sigue cerrado: no lo abrí).
- `ESPERA_OTRA_VENTANA` (20 minutos), la unión apartada que se queda en `logs\` y el `.venv` ajeno sin hash: documentados en `CLAUDE.md`.
- El campo del nombre del bloque acepta HTML arrastrado (de la skill, no de este módulo).

## El push (no se subió nada)

Los tres commits, de `main`, con el correo noreply de autor y de committer. Antes de subir, en una consola:

```bash
git -C "C:\dev\Agendamiento Reservas" log origin/main..main --format="%h %ae %ce %s"
```

Tiene que mostrar solo el correo noreply en las tres columnas. Después, el push de `main` y la comprobación de que subió lo mismo:

```bash
git -C "C:\dev\Agendamiento Reservas" push origin main
git -C "C:\dev\Agendamiento Reservas" rev-parse main
git -C "C:\dev\Agendamiento Reservas" ls-remote origin refs/heads/main
```

Los dos hashes tienen que ser iguales. **`estable` no se movió:** la avanzas tú, después de probar, y solo hacia adelante
(`push origin <commit>:refs/heads/estable`, sin forzar). Un detalle de cuando la avances: la primera vez que un colega abra después de
actualizar, el `.bat` que ya estaba corriendo es el de antes (cmd lo había leído entero); termina con su flujo de siempre y abre el
panel nuevo. El entorno propio rige desde la segunda apertura (lo cubre `TestLosLanzadores`, con un clon inventado).

## Declaración de método

**metodo-ciclo v39.** Se aplicó: encargo con su FRENA SI comprobado commit por commit; revisores de código y de seguridad (Opus) en clones
dentro de la carpeta del encargo, lanzados de a uno; todas las suites sobre el árbol de cada commit, en un clon; censo de mutaciones de lo
nuevo; sonda de secretos, guarda de datos y barridos de datos reales sobre lo que se commitea y sobre cada mensaje de commit; el candado
y `actualizar.py` sin cambios; ningún push; lo que cayó en un FRENA, como propuesta. No se escribió en la memoria de Claude Code. **La lista de tareas no se llevó:**
esta sesión no tiene la herramienta (`mcp__ccd_turn__update_plan`; no está entre las diferidas).
