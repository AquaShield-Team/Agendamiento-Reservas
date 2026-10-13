# Encargo 60 · Los equipos de los colegas se actualizan solos desde la rama `estable`

**Base:** `C:\dev\Agendamiento Reservas` @ `414bc04` · árbol limpio al empezar.

Con `metodo-ciclo` v20 (la sesión tenía cargada la v16: la volví a invocar antes de medir) y `lanzador-modulo` v2 como
referencia. Sin abrir ningún portal y sin red, salvo una lectura del repositorio público en GitHub (abajo).

## En resumen

- **Al abrir, los dos lanzadores corren `actualizar.py`,** que trae la última versión de `estable` y la aplica en ese
  mismo inicio. Después abren el panel, que dice qué pasó: que se actualizó, que ya estaba al día, o por qué no lo hizo.
  Sin red, o si algo lo impide, el panel abre con la versión que tiene el equipo.
- **Solo se actualiza un clon que está en la rama `estable`.** Tu equipo, en `main`, nunca: ni busca la versión nueva.
- **No pisa nada del equipo:** ni `config.json`, ni los perfiles, ni los registros, ni las planillas. Lo medido que lo
  exigió: git pisa sin avisar un archivo ignorado si la versión nueva empieza a versionarlo.
- **No usa credenciales:** el repositorio es público y se lee sin clave, y el actualizador apaga el ayudante de
  credenciales del equipo y las preguntas de la consola.
- **Cada `.bat` va en un solo bloque,** para que la actualización pueda reescribirlo mientras corre. Medido en cmd.
- Lo elegiste tú al empezar: un actualizador propio, y no migrar al lanzador estándar (abajo, «Paso 0»).

## Paso 0

- **Los lanzadores de hoy no se actualizan:** `Iniciar AQUASHIELD.bat` y `Iniciar AQUASHIELD_EMISION.bat` instalan lo
  que falta y abren el panel; no llaman a git. Así que el cambio no tiene la transición del lanzador estándar (un `.bat`
  viejo que hace `git pull` mientras corre). Pero tampoco le llega solo a nadie: cada colega pasa su clon a `estable`
  una vez, a mano (LEEME.md).
- **El lanzador estándar** (`lanzador-modulo` v2, ya en Correos) tiene a Agendamiento «pendiente» en su tabla, con el
  puerto 8770 propuesto. Busca la versión nueva en segundo plano y la aplica en el **inicio siguiente**, lo dice en su
  ventana de consola, no tiene excepción para un equipo de desarrollo, y migrar a él cambia también el puerto, la
  ventana y el manejo de los dos modos. Te lo pregunté, y elegiste el actualizador propio: aplica en el mismo inicio,
  lo dice en el panel y no cambia nada más del arranque. Lo que copia del estándar son sus reglas (solo avanzar, no
  pisar lo propio, el bloque del `.bat`), no su código.

## Lo medido antes de cambiar nada

**El repositorio se lee sin credenciales** (`git ls-remote`, con `credential.helper` vacío y `GIT_TERMINAL_PROMPT=0`;
este equipo tiene el Git Credential Manager puesto en la configuración del sistema y en la global):
- el repositorio público: contestó en 1,4 s, con `main` en `414bc04`;
- uno que no existe, donde GitHub pide usuario y clave: falló en 1,4 s con «terminal prompts disabled», sin preguntar
  nada.

**Lo que hace `git merge --ff-only` en un clon** (repositorios inventados, origen local, sin red; `sonda_merge.py`):

| Caso | Qué hizo git |
|---|---|
| Control: nada que lo impida | Avanzó la rama y escribió los dos archivos |
| La versión nueva empieza a versionar `config.json`, que el clon tiene **ignorado** | **Lo pisó sin avisar:** quedó el de la versión nueva |
| Lo mismo con un archivo **sin rastrear, no ignorado** | Se negó: «would be overwritten by merge»; nada cambió |
| Un archivo que cambia, **abierto por otro programa** | La rama quedó en la vieja, el archivo anterior ya escrito con la nueva y el abierto con la vieja: una mezcla |

Los dos casos marcados son los que el actualizador tiene que impedir o deshacer.

## Lo que cambió

- **`actualizar.py`, nuevo** (y en `.gitignore`). Al abrir, en este orden:
  - la carpeta tiene que ser la raíz de un clon, en la rama `estable`; si no, «no se actualiza solo», y no busca nada;
  - sin una operación de git a medio terminar (`MERGE_HEAD`, `index.lock`, un rebase…);
  - trae `origin/estable` (60 s de plazo; sin red, «no pude buscar la versión nueva (…)»);
  - si el clon ya está ahí, «al día»; si tiene commits que `estable` no trae, no actualiza;
  - sin cambios en los archivos del programa, y sin nada propio en una ruta que la versión nueva empieza a versionar
    (`ocupada`: un archivo o una carpeta, ignorados o no; lo que la vieja ya versiona lo mueve git);
  - `git merge --ff-only` y, después, cada archivo que cambió tiene que tener la versión de donde quedó la rama.
    Si quedó a medias, vuelve cada uno a esa versión (`igualar`), con hasta 5 intentos, cada 2 s; un archivo que no es
    de ninguna de las dos no lo toca. Si no puede, sale con 3 y no se abre el panel.
  - git corre sin ayudante de credenciales (`-c credential.helper=`, que vacía también los del sistema), sin preguntas
    (`GIT_TERMINAL_PROMPT=0`, `GCM_INTERACTIVE=never`, ssh en modo sin preguntas), con el `git.exe` de una carpeta
    absoluta del PATH (nunca de la del programa) y sin `GIT_DIR` ni `GIT_WORK_TREE` heredados. Un git que no termina
    se cierra con su árbol (`taskkill /T`).
  - Lo que pasó queda en `logs/actualizacion.json`, de forma atómica.
- **Los dos `.bat`:** corren `python actualizar.py` antes de instalar lo que falte y de abrir el panel; si sale con 3,
  se quedan en la ventana (`pause`) y no abren. Toda su lógica va en un bloque `( … )` que termina en `exit /b`, en
  ASCII y sin paréntesis en los comentarios de adentro.
- **El panel** (`AQUASHIELD.py`): `_aviso_de_actualizacion` lee ese archivo y, si es de los últimos 10 minutos
  (`AVISO_ACTUALIZACION_SEG`, hipótesis: el `.bat` instala lo que falte entre los dos), `lanzar_web` lo dice en el
  registro del panel al abrir, por el aviso de siempre. El texto lo arma `actualizar.py`, la fuente única.
- **LEEME.md**, «Instalar y mantenerlo al día»: cómo clonar con `estable`, cómo pasar a `estable` un clon que ya está
  en `main`, qué pasa al abrir y cómo avanzas tú la rama.
- **CLAUDE.md**, en «Git y GitHub»: la rama `estable` y el actualizador.
- **`tests/correr.py`:** el censo copia también `actualizar.py` y `.gitignore`, que sus pruebas leen de
  `soporte.FUENTES`.

`test_candado` no cambió y pasa. No hay clics nuevos: el portal no se toca.

## El camino real, en cmd

`sonda_bat.py`: el `.bat` de verdad, en cmd, sobre un clon inventado. La versión nueva le agrega 40 líneas de
comentario a la cabecera del propio `.bat` (corre todos sus bytes) y cambia el programa, que aquí es un sustituto que
anota su versión.

| `.bat` | cmd | ¿Actualizó? | El programa abrió | Errores de cmd |
|---|---|---|---|---|
| El del encargo, en un bloque | salió con 0 | Sí | Una vez, la versión nueva | Ninguno |
| El control: el mismo, línea por línea | salió con 0 | Sí | Una vez | «"va" no se reconoce…»: cmd retomó en el archivo nuevo y corrió un pedazo de comentario |

Con otro largo de cabecera, el pedazo que corre cmd puede ser cualquier cosa. Esto quedó como prueba
(`TestLosLanzadores`), con los dos `.bat` y con el control.

## Pruebas, mutaciones, censo y suite

**Las pruebas nuevas (21)**, en `tests/test_actualizar.py`. Corren git de verdad sobre repositorios inventados (un
origen local, sin red) y el actualizador en un proceso aparte, como lo corre el `.bat`:

| Prueba | Qué vigila |
|---|---|
| `test_trae_la_version_estable_sin_tocar_lo_propio_del_equipo` | Actualiza (cambia, agrega y quita archivos), y `config.json`, los perfiles, los registros y la planilla quedan igual |
| `test_al_dia_no_cambia_nada` | «al día» |
| `test_el_equipo_de_desarrollo_en_main_no_se_actualiza_ni_busca` | En `main` no actualiza ni trae nada |
| `test_solo_avanza_lo_que_marcelo_pone_en_estable` | Un commit en `main` que no está en `estable` no llega |
| `test_sin_red_abre_con_la_que_tiene` | Sin el origen, abre con la que tiene y lo dice |
| `test_un_cambio_en_un_archivo_del_programa_no_se_pisa` | Un archivo del programa cambiado en el equipo |
| `test_un_commit_propio_no_se_pierde` | Un commit del equipo |
| `test_un_archivo_propio_ignorado_donde_la_version_pone_uno_no_se_pisa` | El caso que git pisaba: `config.json` |
| `test_una_carpeta_o_un_archivo_propio_en_el_camino_no_se_pisan` | Una carpeta propia, un archivo propio donde la versión pone una carpeta, y al revés |
| `test_lo_que_ya_versionaba_la_vieja_no_cuenta_como_propio` | Una carpeta del programa que gana un archivo, y un archivo que pasa a carpeta: actualiza |
| `test_una_operacion_de_git_a_medias_no_se_toca` | `MERGE_HEAD`, `index.lock`, un rebase |
| `test_un_archivo_abierto_vuelve_todo_a_la_version_que_tenia` | El caso de la mezcla: vuelve todo a la vieja, abre; cerrado el archivo, la vez siguiente actualiza |
| `test_no_pide_ni_guarda_credenciales` | Un origen que pide clave (un servidor local que contesta 401) y un ayudante de credenciales inventado en el clon: el actualizador falla rápido y no lo llama; el mismo git sin lo que hace el actualizador sí lo llama (control) |
| `test_una_carpeta_que_no_es_un_clon_no_se_actualiza` | Una carpeta sin `.git` |
| `test_sin_argumentos_actualiza_su_propia_carpeta` | Como lo corre el `.bat`, desde otra carpeta: usa la suya |
| `TestLosLanzadores` (3) | Los dos `.bat` en un bloque, el actualizador antes de abrir, sin abrir si quedó a medias; los dos en cmd con el control; `.gitignore` lo versiona |
| `TestAvisoEnElPanel` (3) | El aviso de este inicio sí, el viejo, el del futuro o el malformado no; `lanzar_web` lo dice al abrir |

**Fotos que cambiaron a propósito:** `test_consola.TestLanzadores` lee las líneas sin su sangría (ahora van en un
bloque), y `TestLeeme` suma `actualizar.py` a lo que LEEME.md nombra. La mutación
`bat-holidays-despues-del-panel` se reancló sobre el bloque.

**Las mutaciones:** 28 nuevas (`e60-*`): la rama que no se mira o es otra, la búsqueda que no se hace o no se mira, el
ayudante de credenciales que vuelve, cada cosa que impide actualizar quitada o mirada de otra forma, la escritura a
medias sin volver o volviendo a la otra versión, la carpeta de donde lo llaman, los `.bat` sin el actualizador, sin el
bloque o abriendo a medias, `.gitignore` sin el actualizador, y el aviso del panel. 2.154 mutaciones, 751 pruebas, 0
problemas de anclas (`mut_viejos.py`).

**El censo del área** (`alcance_censo.py`, `lanzar_censo_e60.py`): las 28 nuevas, las que caen cerca de lo que cambió
en `lanzar_web`, y todas las que nombran una prueba del actualizador, de los lanzadores (`test_consola`,
`test_candado`) o de LEEME.md. En total, 43 mutaciones, 50 pares y 31 pruebas.
- **El primer intento abortó en su control** (la copia sin mutar no pasó, 4 fallas): en el censo, las carpetas de las
  pruebas quedaban dentro de la sandbox de otra clase (`soporte.cargar` mueve `tempfile.tempdir`), y la ruta de un
  objeto de git pasaba los 260 caracteres: git no lo escribía (defecto 6). Con carpetas cortas en el temporal de antes
  de las pruebas, pasan también con una clase de sandbox antes, como en el censo.
- **El segundo**, de las 11:21 a las 11:43: el control pasa, y **50 de 50 pares muerden**, con 0 cambios en las 4.878
  entradas fotografiadas de los originales.

**La suite:** `tests/correr.py` (con `correr_sin_tope.py`: el plazo de la corrida entera en 7.200 s), sobre el árbol
que se commitea: **751 pruebas, OK, en 2.047 s**, de las 11:44 a las 12:28, con 0 cambios en las 4.878
entradas fotografiadas de los originales. El equipo estaba al 83 % de CPU, con 18 procesos de Python y
Node de otras sesiones. Las pruebas nuevas suman unos 6 minutos (corren git y cmd de verdad): con el
equipo cargado, la suite pasa los 1.200 s que `correr.py` le da por omisión (residual 8).

**El camino real con el árbol de verdad:**
`e2e_arbol.py`, sin red y sin tocar el repo: un origen local con el árbol del commit del arreglo
(`11976eb`) en `estable`; el clon de un colega con `-b estable` y lo propio inventado (`config.json`, un
perfil, un registro y una planilla), que `git status` no ve; después `estable` avanza a un commit hecho
ahí (LEEME.md cambiado y un archivo nuevo en `tests/`), y el colega corre `python actualizar.py`, como su
`.bat`. Salió con 0, «⟳ AQUASHIELD se actualizó a la versión estable …», el clon quedó en la versión
nueva y en `estable`, lo propio igual y los archivos del programa sin cambios. Un clon en `main` del mismo
árbol: «Este equipo no se actualiza solo…», y siguió en su commit.

## FRENA SI

- **Pisar o borrar un archivo propio del equipo:** no salta. Lo que git pisaría (un archivo ignorado donde la versión
  nueva pone uno, o una carpeta o un archivo en su camino) no deja actualizar; lo que borra o cambia son archivos del
  programa sin cambios del equipo; y una escritura a medias se vuelve atrás sin tocar lo que no es de ninguna de las dos
  versiones. Lo que sigue abierto, en el residual: un nombre que solo cambia de mayúsculas, y un corte de luz a mitad
  de la escritura.
- **Guardar credenciales de GitHub en el equipo:** no salta. El repositorio público se lee sin clave (medido), y el
  actualizador no deja que git pida ni guarde ninguna (probado con un ayudante inventado, y su control).

## Lo decides tú

1. **Qué commit es la primera `estable`.** Tiene que ser el de este encargo o uno posterior: con uno anterior, los
   `.bat` de los colegas no traen el actualizador. Lo pruebas en tu equipo y lo publicas con el bloque de abajo.
2. **Los clones que ya tienen los colegas:** si están en `main`, cada uno pasa a `estable` una vez, con los dos comandos
   de LEEME.md; si lo bajaron como ZIP, sin `.git`, el programa no se actualiza solo y lo dice en el panel. Si conviene
   que el panel lo diga más fuerte, lo decides.

## El push

**No lo subo:** el repositorio es público (subir publica), y desde este encargo los lanzadores traen código de GitHub a
los equipos de los colegas, que también cuenta como publicar. Sube `main` con dos commits; `estable` no existe todavía,
y la creas tú cuando la versión esté probada.
El bloque va abajo, al final del mensaje de cierre, con el hash esperado de `main`; y, cuando
la pruebes, la primera `estable` con los comandos de LEEME.md.

## Re-medir

Todo corre desde `scratchpad\e60`, en Git Bash, después de `source entorno_e60.sh` (`TMPDIR`, `TEMP` y `TMP` dentro de
la carpeta), con Python 3.13.

| Número | Comando |
|---|---|
| Leer el repositorio sin credenciales, y el que pide clave | `GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never git -c credential.helper= ls-remote <url>` |
| Lo que hace `git merge --ff-only` en un clon | `python sonda_merge.py` |
| El `.bat` de verdad en cmd, con el control | `python sonda_bat.py` |
| Las pruebas del actualizador | `cd tests; python -m unittest test_actualizar` (en una subcapa, para no mover la sesión) |
| Las anclas de las mutaciones | `python mut_viejos.py e60- bat-` |
| El censo del área | `python alcance_censo.py`; `python lanzar_censo_e60.py` (aparte; escribe `censo_e60.txt`) |
| El camino real con el árbol de verdad | `python e2e_arbol.py` |

## NO retroceder

- **Un clon fuera de `estable` no se actualiza ni busca.** Así tu equipo de desarrollo no se mueve solo.
- **Nada propio se pisa:** lo que git pisaría sin avisar se mira antes, y no se actualiza; nunca `reset`, `clean`,
  `stash` ni `checkout` de todo.
- **git sin ayudante de credenciales ni preguntas:** el repositorio es público, y un equipo de uso no tiene por qué
  guardar una clave.
- **Cada `.bat`, en un bloque que termina en `exit /b`,** y sin paréntesis en sus comentarios de adentro.
- **`estable` solo avanza, y nunca se fuerza:** un equipo con una `estable` que no se continúa deja de actualizarse.

## Defectos de instrumento que me cacé

1. **La primera sonda del `.bat` daba «no abrió» en los dos casos,** y no era el `.bat`: las sesiones de Claude Code
   traen `NoDefaultCurrentDirectoryInExePath=1`, y con eso cmd no corre un `.bat` de su carpeta por su nombre solo. Con
   la ruta completa, corre. Sumé la fila a «Entorno Windows de esta máquina».
2. **Esa misma sonda comparaba la rama del clon con su `origin/estable`,** que el clon todavía no había traído: daba
   «actualizó» sin que nada hubiera corrido. La rehice contra el commit que se publicó.
3. **Los primeros repositorios de prueba no traían el `.gitattributes` del repo de verdad,** y git escribía los
   archivos con CRLF: 4 pruebas cayeron por eso y no por el actualizador. Ahora lo traen.
4. **La primera prueba de las credenciales no veía el ayudante:** comprobaba que el clon no guardara nada, y eso pasa
   igual sin `-c credential.helper=`. La rehice con un ayudante inventado que deja una marca, y su control.
5. **La herramienta Bash volvió a juntar las barras invertidas** en dos scripts escritos por heredoc: fallaron sus
   anclas antes de escribir nada, y los rehice con Edit.
6. **Las pruebas del actualizador dependían del largo de la ruta del temporal:** pasaban solas y caían en el censo,
   donde sus carpetas quedaban dentro de la sandbox de otra clase. Las cazó el control del censo. Ahora crean sus
   carpetas, con nombres cortos, en el temporal de antes de las pruebas (`carpeta_corta`).
7. **Corrí las pruebas mientras el primer censo, ya abortado, terminaba de fotografiar los originales:** su foto dio 0
   cambios, y no usé ese intento para nada.
8. **El monitor del censo buscaba «MUERDE» al principio de la línea, y la línea empieza con espacios:** avisaba cada par
   que mordía, y su latido decía «muerden 0». Los números de arriba salen de contar en el archivo, no del monitor.

## Premisas del encargo que se refutaron

- **«El launcher de los colegas»:** hoy no tiene cómo actualizarse; el primer paso a `estable` es a mano, una vez por
  equipo (LEEME.md). No es una premisa falsa del encargo, pero el encargo no lo decía.

## Residual

| # | Lo que queda | Condición de reapertura |
|---|---|---|
| 1 | Un nombre que solo cambia de mayúsculas (`Manual.txt` a `manual.txt`) cuenta como algo propio en el camino, y ese equipo no se actualiza más hasta arreglarlo a mano | Si una versión tiene que hacerlo: se hace en dos versiones, como pide la regla de `lanzador-modulo` |
| 2 | Un corte de luz a mitad de la escritura deja un archivo truncado, que no es de ninguna de las dos versiones: el actualizador no lo toca y no abre (código 3) | Si pasa |
| 3 | La vuelta atrás de una escritura a medias con un archivo que no es de ninguna de las dos versiones no tiene prueba con git de verdad (no se arma sin un corte) | Si se encuentra cómo armarlo |
| 4 | Si al abrir ya hay un panel de AQUASHIELD ocupado, el lanzador lo abre en el navegador: ese panel no muestra el aviso, y sigue con el código de antes en memoria hasta que se cierre | Si molesta |
| 5 | El aviso dura 10 minutos (hipótesis): si el `.bat` tarda más instalando lo que falte, el panel no lo muestra | Si pasa |
| 6 | Un remoto por ssh (no https) necesita una clave del equipo: el actualizador no pregunta y no actualiza | Si un colega clonó por ssh |
| 7 | Las revisiones que pide ECC (de código y de seguridad) no se lanzaron | Si las pides |
| 8 | Con el equipo cargado, la suite pasa los 1.200 s que `correr.py` le da por omisión (hoy, 2.047 s): el corredor la corta sin dar el resultado | Si hay que correrla así: `correr_sin_tope.py`, o subir ese plazo |

## Reglas de método (v20)

- **Aplicadas:** las 21 universales. En especial:
  - el control positivo que aborta: `sonda_merge.py` (su control avanza), `sonda_bat.py` (el control sin bloque se
    tiene que notar distinto, y se notó), la prueba de las credenciales (el control llama al ayudante), `mut_viejos.py`;
  - se mide sobre el camino real: el actualizador corre en un proceso aparte con git de verdad, y el `.bat` en cmd; y el
    control del bloque sobrevive al cambio (el mismo `.bat` sin el bloque);
  - el negativo que muerde: cada prueba nueva con su mutación, y el censo del área;
  - un gate en cero prueba contención: la suite no basta; las pruebas funcionales con git y cmd prueban el efecto;
  - fuente única: el texto del aviso lo arma solo `actualizar.py`;
  - cada reemplazo, una sola vez; escritura atómica del resultado; EOL: LF (0 CR), y los `.bat`, en ASCII;
  - frenar en lo que es tuyo: el actualizador propio o el estándar (lo preguntaste y lo elegiste), y la primera
    `estable`.
- **Las del módulo** (`CLAUDE.md`): `test_candado` no cambia; ningún clic nuevo; casos sintéticos (repositorios
  inventados, sin red); nunca el puerto 8765 en una prueba; la sonda de secretos antes de cada commit; el correo
  noreply de autor y de committer.
- **El push** («CC sube solo cuando subir no publica nada»): el repositorio es público, y este cambio trae código de
  GitHub a los equipos: no subo, entrego el bloque.
- **Choques:** ECC pide lanzar revisores solos; las reglas permanentes dicen que se proponen: no lancé ninguno
  (residual 7).
- **Pieza 8:** opcional; este informe es Markdown y no lo rendericé.

## Lo que dio en el repo

Dos commits en `main`, sin push (el push lo haces tú):

- `11976eb` feat: el actualizador, los dos `.bat`, el aviso del panel, `.gitignore` y las pruebas
  (`actualizar.py`, `AQUASHIELD.py`, y en `tests/`: `test_actualizar.py`, `test_consola.py`,
  `mutaciones.py` y `correr.py`);
- el commit siguiente, docs: `CLAUDE.md`, `LEEME.md` y este informe.

Los dos llevan de autor y de committer el correo noreply del repo, y la sonda de secretos dio 0 antes de
cada uno. Fuera del repo, en «Entorno Windows de esta máquina» (`~/.claude/CLAUDE.md`), una fila medida:
las sesiones de Claude Code traen `NoDefaultCurrentDirectoryInExePath=1`, y con eso cmd no corre un
`.bat` de su carpeta por su nombre solo.
