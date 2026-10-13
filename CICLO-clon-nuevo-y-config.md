# Encargo 61 · Un clon recién hecho funciona, y el panel nunca queda mudo

**Base:** `C:\dev\Agendamiento Reservas` @ `b348d48` · árbol limpio al empezar.

Con `metodo-ciclo` v20 (la versión del archivo; la sesión la tenía cargada). Sin abrir ningún portal. Leí dos veces el
repositorio público en GitHub (un `git clone` y un `ls-remote`), y pip bajó de PyPI las librerías del clon de prueba;
nada se subió.

## En resumen

- **Por qué el panel del colega quedaba mudo: le faltaba `config.json`.** Sin él, `/api/config` y `/api/credenciales`
  contestaban 500, y la página lo anotaba solo en el registro plegado, que antes de cargar una planilla ni siquiera se
  muestra. Así, Operador quedaba vacío, «Solo iniciar sesión» abría una lista vacía, Credenciales no abría su cuadro y
  «Armar» no cambiaba nada a la vista. Medido en un clon nuevo del repositorio público, con un Python sin las librerías
  de este equipo. Las dependencias no eran: el `.bat` las instaló solo, y con `config.json` copiado el mismo clon
  funcionó entero.
- **Ahora el panel crea `config.json` desde `config.example.json`, sin credenciales,** la primera vez que se abre, y lo
  dice en un aviso a la vista. Es el paso que LEEME.md pedía hacer a mano. El clon llega a «Modo Seguro Activo» y
  carga sus credenciales desde el panel (medido con el programa de verdad, en el clon de prueba).
- **Si algo falta, el panel lo dice a la vista y dice cómo resolverlo:** un `config.json` que no se lee (con la línea
  del error, sin mostrar su contenido), una plantilla que falta, un archivo que no se puede escribir, un operador que
  no hay. Los botones que fallan (Credenciales, «Entrar a los portales», «Armar») lo dicen en el mismo aviso.
- **Sin red en el primer arranque, el `.bat` ahora lo dice y espera una tecla.** Antes pip fallaba, `pythonw` moría al
  importar playwright y la ventana se cerraba sin decir nada: ni panel, ni mensaje (medido).
- **La primera `estable`: el último commit de este encargo,** el de documentos (su hash va en el mensaje de cierre). Con
  `b348d48`, la que te sugerí en el encargo 60, un clon nuevo seguiría mudo.

## Paso 0

- **El clon del colega no está en este equipo.** Lo reproduje como lo haría él, en `scratchpad\e61\t`: un clon nuevo,
  sin `config.json` ni perfiles, y un Python limpio. El Python es el mismo de este equipo (3.13.14), con su carpeta de
  paquetes del usuario vacía y propia (`PYTHONUSERBASE`): aquí playwright, openpyxl y holidays están todas ahí, así
  que ese Python no ve ninguna (0 de 3, medido antes de correr el `.bat`). El entorno, el de un doble clic: sin
  `PYTHONDONTWRITEBYTECODE` ni `NoDefaultCurrentDirectoryInExePath`, que traen las sesiones de Claude Code. El
  navegador del panel, el de la sesión: `BROWSER` anotaba la dirección en vez de abrir el tuyo.
- **`git clone -b estable` falla hoy:** «fatal: Remote branch estable not found in upstream origin». En GitHub está solo
  `main` (`b348d48`, `ls-remote`). Así que el colega tiene que haber clonado `main`, que el actualizador no toca: su
  clon no recibe arreglos solo.
- **Veredicto:** CICLO. Hay algo que arreglar y se puede medir sin portales.

## Lo medido antes de cambiar nada

| Qué | Resultado |
|---|---|
| El `.bat` en el clon nuevo, con red | Instaló playwright 1.63.0, openpyxl 3.1.5 y holidays 0.106 (en este equipo: 1.58.0, 3.1.5 y 0.105) y abrió el panel en 71 s, en el 8766 (el 8765 lo tiene otro programa, que no cerró) |
| `/api/config` y `/api/credenciales` sin `config.json` | 500: «No existe config.json (copia config.example.json y pon tus credenciales).» |
| La página, con la planilla inventada cargada | Operador: 0 opciones. «Solo iniciar sesión»: lista vacía. Credenciales: no abre el cuadro. «Armar»: nada a la vista. Los tres mensajes, en el registro plegado; el estado lo pisa el sondeo («Listo.») en menos de un segundo |
| El control: el mismo clon, con `config.example.json` copiado como `config.json` | «Modo Seguro Activo», 2 operadores, 6 navieras en la lista y el cuadro de Credenciales con sus 6 filas |
| El `.bat` sin red en el primer arranque (pip contra un puerto local donde nadie escucha) | pip falla 3 veces, `pythonw` muere al importar playwright y el `.bat` termina: ningún panel, ninguna palabra |

## Lo que cambió

- **`AQUASHIELD.py`, el servidor del panel:** `_config_del_panel` lee `config.json` para `/api/config` y
  `/api/credenciales` (las dos). Si falta, `_crear_config_desde_el_ejemplo` copia `config.example.json` byte a byte: a
  un temporal y lo renombra, que en Windows no pisa un `config.json` que aparezca entretanto, con los reintentos de
  siempre si Windows niega el renombre un instante. Lo dice en el registro del panel, y `/api/config` trae el aviso
  (`aviso`) hasta que se guardan credenciales. Si no puede crear o leer el archivo, levanta `ConfigDelPanel` con qué
  falta y cómo resolverlo, y el servidor lo contesta como texto:
  - sin la plantilla, o con una plantilla que no se lee: reinstalar como dice LEEME.md;
  - sin poder escribir: copiar la plantilla a mano;
  - un `config.json` que no es JSON: la línea, la columna y el motivo, sin el texto del archivo (trae las claves), y
    cómo corregirlo o apartarlo para que el panel cree uno nuevo;
  - uno que no está en UTF-8, o que no tiene la forma de la plantilla, o que no se puede abrir: lo mismo, con su motivo.
- **Solo el panel web lo crea.** El candado (`_llaves_abiertas`) y la consola siguen leyendo con `cargar_config`, que
  no crea nada: sin `config.json` el candado sigue cerrado, como antes. `test_candado` no cambió.
- **La página:** un aviso a la vista, bajo la nota del modo (`#aviso-panel`, `notaVisible` y `avisoFijo`), que también
  va al registro. Lo usan:
  - el arranque: el aviso de que creó `config.json`, el de que no hay ningún operador, o, si no pudo leer la
    configuración, el motivo (y la nota del modo pasa a «Modo sin leer», y la lista de «Solo iniciar sesión» muestra el
    motivo);
  - Credenciales: si no puede leerlas, abre el cuadro igual, con el motivo; y sin operadores, dice cómo crear uno;
  - «Entrar a los portales» y «Armar»: lo que antes iba solo al registro («Marca al menos una naviera», «No pude
    entrar», «No pude arrancar», el aviso de modo del encargo 52), y si el panel no pudo leer su configuración, su
    motivo. Cada botón limpia el aviso al empezar.
- **Los dos `.bat`:** después de instalar playwright y openpyxl, y antes de holidays (que sin red no frena el
  arranque), comprueban que se importen; si no, dicen qué falta y cómo instalarlo a mano, y esperan una tecla, sin
  abrir el panel. En ASCII, dentro del bloque, sin paréntesis en sus textos.
- **LEEME.md:** el clon con `-b estable` (y qué hacer si git dice que la rama no existe), el primer arranque, y que el
  panel crea `config.json` y avisa lo que falta. Ya no pide copiar la plantilla a mano.

Sin clics nuevos en los portales: el cambio es del arranque del panel y de su página.

## El camino real, en el clon de prueba

Con el programa de este encargo copiado al clon nuevo, el mismo Python limpio, el `.bat` de verdad en cmd y la página en
el navegador de la sesión:

- **Sin `config.json`:** «Modo Seguro Activo», Operador con `usuario1` y `usuario2`, la lista de navieras, y el aviso
  «No había config.json en la carpeta del programa: lo creé desde config.example.json, sin credenciales…». El
  `config.json` creado es la plantilla, byte a byte, y no quedó ningún temporal.
- **Credenciales:** el cuadro abre; guardé un usuario inventado de ONE, sin clave. `config.json` lo trae, con las
  «opciones» de la plantilla intactas; el aviso se fue; `git status --ignored` muestra `config.json` como ignorado.
- **Un `config.json` roto, con una clave inventada adentro:** al cargar, el aviso y la lista de «Solo iniciar sesión»
  dicen «config.json no se puede leer: no es un JSON válido (línea 2, columna 16: …)» y cómo resolverlo; la nota del
  modo, «Modo sin leer»; Credenciales abre el cuadro con el motivo; «Armar» no arma y lo dice, con el motivo. La clave
  inventada no aparece en la página, y el archivo quedó igual.
- **Siguiendo el consejo del aviso** (renombrarlo y recargar): el panel creó uno nuevo y volvió a «Modo Seguro Activo».
- **Sin red, con el `.bat` nuevo:** «AQUASHIELD no puede abrir: faltan las librerias playwright u openpyxl de Python…»,
  el comando para instalarlas a mano y «Presione una tecla para continuar». Ningún panel.

**Con el árbol commiteado** (`e2e_final.py 88463d2`, sin red hacia GitHub para el código): un origen local con
`main` y `estable` en `88463d2`, el clon de un colega con `-b estable`, como dice LEEME.md (sin `config.json` ni
perfiles), otro Python limpio y el `.bat` de verdad. El `.bat` dijo «✓ AQUASHIELD está al día con la versión
estable (88463d2)», instaló las tres librerías y abrió el panel a los 35 s. `/api/config`: 200, modo prueba,
`usuario1` y `usuario2`, y el aviso de que creó `config.json`, que es la plantilla byte a byte. `/api/credenciales`:
200, 6 navieras, ninguna clave. git ve `config.json` y `logs/` como ignorados. En la página: «Modo Seguro Activo»,
Operador `usuario1`, y Credenciales abre su cuadro con las 6 filas.

## Pruebas, mutaciones, censo y suite

**Las pruebas nuevas (14):**
- `test_web.TestPanelSinConfig` (9), con el servidor de verdad en una sandbox sin `config.json` y con la plantilla:
  lo crea y lo dice una sola vez, y el aviso sigue hasta guardar credenciales; Credenciales también lo crea; no pisa
  uno que aparece entretanto; reintenta si Windows niega el renombre; si no puede crearlo, lo dice y no deja
  temporales; una plantilla que no se lee; un `config.json` que no se lee, en los tres pedidos (sin mostrar su
  contenido, y sin tocarlo); uno que no se abre; y el candado, sin `config.json`, sigue cerrado y no crea nada.
- `test_envio.TestLoQueFaltaALaVista` (4), en Node con un DOM falso: el aviso se ve, se esconde y va al registro; el
  arranque (sin configuración, con el aviso de que la creó, sin operadores, y «Entrar» sin naviera o con el login que
  falla); Credenciales que no se leen abren el cuadro con el motivo; y los botones ya no avisan solo al registro.
- `test_actualizar.TestLosLanzadores.test_sin_las_librerias_lo_dice_y_no_abre`: los dos `.bat` en cmd, con un Python
  sin playwright ni openpyxl y pip contra un puerto local: lo dicen y no abren. Control: el mismo `.bat` sin el
  chequeo abre el programa (un sustituto que deja una marca).

**Fotos que cambiaron a propósito:** `test_config_ausente_da_500` pasó a `test_config_ausente_sin_plantilla_lo_dice`
(sin la plantilla, el panel lo dice y no crea nada); la del encargo 52, `mismoModo`, ahora exige que su aviso se vea y
que traiga el motivo del panel si contestó con un error; y la estática de los `.bat`, que el chequeo esté en su lugar.

**Las mutaciones:** 35 nuevas (`e61-*`) y una reescrita (`web-config-ausente-otro-aviso`, sobre el texto nuevo).
El chequeo de anclas de toda la lista (`mut_viejos.py`):
2.189 mutaciones, 765 pruebas, 0 problemas (cada texto viejo una vez, las 36 del encargo compilan).

**El censo del área** (`alcance_censo.py`, `lanzar_censo_e61.py`): las 36 del encargo, las que caen a 15 líneas
o menos de lo que cambió en `AQUASHIELD.py` y en los `.bat` (también las del JavaScript de la página), y las que
nombran una prueba cuyo camino cambió (el panel que lee la configuración, la página en Node, los lanzadores,
LEEME y el candado sin `config.json`). **122 mutaciones, 147 pares, 61 pruebas: los 147 muerden.** El control
(la copia sin mutar) pasa, y la foto de los 4.879 originales, 0 cambios. De las 14:52 a las 15:16.

**La suite:** `tests/correr.py` (con `correr_sin_tope.py`: el plazo de la corrida entera en 7.200 s), sobre el
árbol que se commitea: **765 pruebas, OK, en 1.354 s**, de las 15:16 a las 15:39, con 0 cambios en las 4.879
entradas fotografiadas de los originales. El equipo estaba al 76 % de CPU al empezar, con otros programas: otra vez
más de los 1.200 s que `correr.py` le da por omisión (residual 10).

## FRENA SI

- **El clon limpio necesita algo que el lanzador no puede instalar solo:** no salta. Lo que le faltaba era
  `config.json`, que ahora crea el panel; las librerías de Python las instala el `.bat` (con internet). Lo que el colega
  instala a mano es lo que LEEME.md ya pedía: Python 3.13, Git for Windows y Chrome.
- **El arreglo obliga a guardar credenciales en el repo:** no salta. `config.json` se crea en la carpeta del colega, y
  git lo ignora (medido); `config.example.json` sigue sin credenciales.

## Lo decides tú

1. **La primera `estable`: el commit de documentos de este encargo, o uno posterior.** Trae el arreglo (`88463d2`) y
   LEEME.md al día. Con `b348d48`, un clon nuevo quedaría mudo como el del colega. El bloque va al final del mensaje de
   cierre.
2. **El clon que ya tiene el colega** está en `main` (la única rama publicada), y no se actualiza solo. Para que
   funcione hoy, con su versión: copiar `config.example.json` como `config.json` en su carpeta y recargar el panel. Y
   cuando crees `estable`: los dos comandos de LEEME.md (`fetch` y `switch estable`), una vez.
3. **Con qué operadores nace `config.json`:** con los de la plantilla, `usuario1` y `usuario2`, como la copia a mano
   que pedía LEEME.md. Si prefieres que nazca sin ninguno, y que el colega cree el suyo, es un cambio de pocas líneas.

## El push

**No lo subo:** el repositorio es público (subir publica), y los lanzadores traen código de GitHub a los equipos de los
colegas. Sube `main` con dos commits; la primera `estable`, cuando la pruebes. El bloque va al final del mensaje de
cierre, con el hash esperado de `main`.

## Re-medir

Todo corre desde `scratchpad\e61`, en Git Bash, después de `source entorno_e61.sh`, con Python 3.13.

| Número | Comando |
|---|---|
| El clon del colega y su Python limpio | `python colega.py clonar <url> <carpeta>`; `python colega.py lanzar <carpeta> "Iniciar AQUASHIELD.bat"` (la dirección del panel queda en `urls.txt`) |
| El mismo, sin red | `E61_USERBASE=userbase_sinred E61_SIN_RED=1 python colega.py lanzar …` |
| Las pruebas nuevas | `cd tests; python -m unittest test_web.TestPanelSinConfig test_envio.TestLoQueFaltaALaVista test_actualizar.TestLosLanzadores` |
| Las anclas de las mutaciones | `python mut_viejos.py e61-` |
| El censo del área | `python alcance_censo.py`; `python lanzar_censo_e61.py` (aparte; escribe `censo_e61.txt`) |
| Las líneas de más de 120 caracteres | `python largas.py` |

## NO retroceder

- **El panel web crea `config.json` desde la plantilla, y solo él:** el candado y la consola no crean nada.
- **Lo que falta se dice a la vista,** no solo en el registro plegado ni en el estado, que el sondeo pisa.
- **Un `config.json` que no se lee no se muestra:** el motivo dice la línea y la columna, nunca su texto.
- **Crear no pisa:** a un temporal y renombrar, que en Windows no reemplaza un archivo que ya está.
- **Sin playwright ni openpyxl, el `.bat` lo dice y espera;** el de holidays sigue sin frenar el arranque.

## Defectos de instrumento que me cacé

1. **El primer `.bat` del clon «no encontró la ruta»:** `colega.py` le pasaba una ruta relativa y lo corría desde otra
   carpeta. Con la ruta absoluta, corrió.
2. **La herramienta Bash volvió a juntar las barras invertidas** en un parche de `test_envio.py` escrito por heredoc:
   su ancla falló antes de escribir nada, y lo hice con Edit.
3. **Mi primera prueba de la página leía el registro de la página por referencia:** los clics que venían después le
   sumaban líneas, y daba de más. Ahora copia cada lectura.
4. **Mi primera mutación del `.bat` «sin chequeo» lo dejaba siempre fallando,** y así la prueba en cmd no la habría
   visto: el control quita el chequeo y no lo notaría. La rehice como un bloque que nunca corre.
5. **El chequeo nuevo del `.bat` iba primero después de holidays,** y `test_instalan_holidays_sin_frenar_el_arranque`
   lo cazó: entre holidays y el panel no puede haber nada que frene. Lo puse antes de holidays.

## Premisas del encargo que se refutaron

- **«Un clon recién hecho del repo»:** con `-b estable`, como dice LEEME.md, hoy no se puede clonar: la rama no existe
  en GitHub. El colega tiene que haber clonado `main`.

## Residual

| # | Lo que queda | Condición de reapertura |
|---|---|---|
| 1 | El clon que tiene el colega sigue mudo hasta que copie la plantilla o pase a `estable` | Cuando crees `estable` |
| 2 | Un clon nuevo instala playwright 1.63.0, más nuevo que el 1.58.0 con que se midió todo en este equipo: con los portales no está probado | Si un colega ve algo distinto en un portal |
| 3 | El `.bat` no instala el Chromium de Playwright (`playwright install`): si Chrome no abre, el respaldo no está | Si un colega no tiene Chrome |
| 4 | Sin Python en el equipo, el `.bat` muestra el error de cmd y después dice que faltan las librerías (sin medir) | Si un colega no tiene Python |
| 5 | Con una ventana chica, el aviso queda al pie del panel izquierdo y hay que bajar para verlo (visto a 800×450) | Si molesta |
| 6 | El motivo de un JSON roto trae el texto de Python en inglés («Expecting property name…») | Si molesta |
| 7 | El `.bat` que sale por el chequeo (`exit /b 1`, después de `pause`) devuelve 0 por `cmd /c` (medido, con `||` y con `if errorlevel`): nadie lo lee en un doble clic | Si algo empieza a leerlo |
| 8 | `test_sin_las_librerias_lo_dice_y_no_abre` se salta en un equipo cuyo Python traiga playwright fuera de la carpeta del usuario | Si se salta en otro equipo |
| 9 | Las revisiones que pide ECC (de código y de seguridad) no se lanzaron | Si las pides |
| 10 | Con el equipo cargado, la suite pasa los 1.200 s que `correr.py` le da por omisión (hoy, 1.354 s; en el encargo 60, 2.047 s): el corredor la corta sin dar el resultado | Si hay que correrla así: `correr_sin_tope.py`, o subir ese plazo |

## Reglas de método (v20)

- **Aplicadas:** las 21 universales. En especial:
  - se mide sobre el camino real: el clon nuevo del repositorio público, el `.bat` de verdad en cmd, el panel de
    verdad y su página en un navegador; y el control (el mismo clon con `config.json`) separó la causa de las
    dependencias;
  - el control positivo que aborta: `mut_viejos.py`; y la prueba del `.bat` en cmd tiene su control sin el chequeo;
  - el negativo que muerde: cada prueba nueva con su mutación, y el censo del área;
  - un gate en cero prueba contención: la suite no basta; el camino real en el clon y las pruebas funcionales prueban
    el efecto;
  - cada reemplazo, una sola vez; escritura atómica (temporal y renombre); EOL: LF, y los `.bat`, en ASCII;
  - frenar en lo que es tuyo: la primera `estable` y con qué operadores nace `config.json`.
- **Las del módulo** (`CLAUDE.md`): `test_candado` no cambia; ningún clic nuevo; casos sintéticos (una planilla y
  credenciales inventadas); nunca el puerto 8765 en una prueba (el panel del clon tomó el 8766, como tomaría el del
  colega con el 8765 ocupado); la sonda de secretos antes de cada commit; el correo noreply de autor y de committer.
- **El push:** el repositorio es público y los lanzadores traen código de GitHub a los equipos: no subo, entrego el
  bloque.
- **Choques:** ECC pide lanzar revisores solos; las reglas permanentes dicen que se proponen: no lancé ninguno
  (residual 9).
- **Pieza 8:** opcional; este informe es Markdown y no lo rendericé.

## Lo que dio en el repo

Dos commits en `main`, sin push (el push lo haces tú):

- `88463d2` fix: el panel crea `config.json` desde la plantilla y dice a la vista lo que falta, y los `.bat`
  dicen si faltan las librerías (`AQUASHIELD.py`, los dos `.bat`, y en `tests/`: `test_web.py`,
  `test_envio.py`, `test_actualizar.py` y `mutaciones.py`);
- el commit siguiente, docs: `CLAUDE.md`, `LEEME.md` y este informe.

Los dos llevan de autor y de committer el correo noreply del repo, y la sonda de secretos dio 0 antes de cada uno.
Los clones de prueba y sus Python limpios, en `scratchpad\e61\t`, se borraron al terminar.
