# CICLO · Publicar el repo en GitHub sin datos de AquaChile, de las personas ni de las cuentas de las navieras

**Módulo:** Agendamiento Reservas · **Encargo 44** · **Fecha:** 2026-10-01 · **Método:** skill `metodo-ciclo` v15, que
entró a mitad del ciclo (ver la pieza 7).

**Commits del encargo,** en `main` hasta que `orfana.sh` la reemplace, y desde ahí en `historial-local`, que no se sube:
- `7d9e52c`: los contratos por defecto salen del programa a `config.json`;
- `a119d14`: los generadores de material y el logo quedan fuera del repo;
- `ecd89e9`: sin la ruta corta del usuario de Windows en el repo;
- `f823586`: lo que encontró la revisión de código;
- `b94d8fb`: este informe, con `CLAUDE.md` y `LEEME.md` al día;
- y el que suma tus dos decisiones del «publica» (abajo), en este informe y en `CLAUDE.md`: el último de
  `historial-local`.

Después, `orfana.sh` arma en este equipo una `main` nueva de un solo commit, con el árbol del commit de este informe.
**Nada de eso sale del equipo antes de tu «publica».**

**Respondiste «publica»** y decidiste dos cosas: los datos de la empresa que el programa usa se publican tal como están,
y el correo noreply queda como `user.email` de este repo antes de cualquier commit nuevo. Las dos están en `CLAUDE.md`,
y el commit que las suma ya lleva ese correo.

**Base: `C:\dev\Agendamiento Reservas` @ `503718b` · árbol limpio** (pieza 9).

> **Datos reales.** Las sondas leen `config.json`, las dos planillas, los `log.txt` de `logs/` y, para dos números de
> COSCO, los HTML de `logs/`, sin copiarlos, e imprimen categorías, archivos, líneas y cuentas, nunca un valor. **Se
> escribió dos veces en tu `config.json`:** los cuatro contratos y el código de Shipper de HYUNDAI, con la escritura del
> programa. En este informe no van credenciales, contratos, correos, teléfonos, naves, viajes, números de reserva ni el
> nombre del operador; el único correo es el noreply de tu cuenta de GitHub, que es público a propósito. No se miró
> ninguna captura.

**Resumen.**
- **No hay credenciales ni en el árbol ni en el historial:** ni los usuarios ni las claves de `config.json`, ni tokens,
  llaves privadas o RUT, en ningún archivo del árbol ni en ninguno de los 1183 objetos de git. **Tu FRENA SI de
  credenciales no se cumple, y tampoco el de `gh`:** tu cuenta administra AquaShield-Team y su token tiene el permiso
  `repo`. Lo consulté con `gh`, solo en lectura: la cuenta, su rol y si el repo existe. Fueron las únicas consultas a
  GitHub del encargo.
- **Tu FRENA SI de los datos que el programa usa sí se cumple.** Quedan en el código, reportados y sin tocar:
  - el nombre de la empresa: AQUACHILE, que MAERSK busca en el Shipper y HYUNDAI en su modal; y «AQUACHILE S.A.», el
    Shipper de COSCO y el cliente de MAERSK;
  - la dirección, la ciudad y el país de la planta, para COSCO;
  - la descripción de la carga y su código HS.

  Son de la misma clase que AQUACHILE, el ejemplo de tu FRENA SI. Los datos de la cuenta (los contratos y el código de
  Shipper de HYUNDAI) sí salieron, como pide el encargo. **Al responder «publica», decidiste que se publiquen tal como
  están.**
- **Lo que había en el árbol, y qué se hizo:**
  - **los contratos por defecto** de ONE (Estados Unidos y otros mercados), MSC y HYUNDAI estaban escritos en el
    programa: pasan a `config.json` → opciones → `contratos_por_defecto` (`7d9e52c`). **El código con que HYUNDAI
    identifica a la empresa como Shipper** pasa a `codigo_shipper_hyundai` (`f823586`). Tu `config.json` ya trae esos
    cinco valores, así que en este equipo el programa hace lo mismo; en `config.example.json` van vacíos;
  - **un comentario de COSCO** traía el número de la cuenta y otro contrato: queda sin ellos (`7d9e52c`). No pasaron a
    `config.json`, porque el programa no los usa;
  - **los cuatro generadores de material** traían naves, viajes, números de reserva y contratos reales, tu correo de la
    empresa, tu celular y la etiqueta «Uso Interno Confidencial». Quedan fuera del repo, con **el logo de la empresa**,
    y siguen en el equipo (`a119d14`, decisión tuya);
  - **la forma corta de la carpeta de tu usuario de Windows**, en un comentario de una prueba y en un informe, pasa a un
    marcador (`ecd89e9`).
- **Lo que queda por decisión tuya:** tu nombre, en «decisión de Marcelo» y, completo, en el pie del panel.
- **HYUNDAI sin contrato ya no elige el primero de la lista.** Con `7d9e52c`, en un equipo sin contratos habría elegido
  en Booking Details la primera opción, antes de la guarda. Desde `f823586` corta antes: NO ENVIADA. Lo encontró la
  revisión de código.
- **El historial queda en `historial-local`, que nunca se sube.** Trae el nombre del operador (en los 72 commits hasta
  `9710ae2`), el correo de la empresa en cada commit y las versiones viejas de lo que salió del árbol. La `main` nueva
  es un commit huérfano con el árbol limpio, con tu correo noreply de GitHub como autor y committer.
- **La red:** 559 pruebas y 1653 mutaciones; cada commit pasó su gate, y el censo completo de `f823586` dio los 1987
  pares mordiendo. `test_candado` no cambió, y la suite pasa antes (547 pruebas en verde en `503718b`, en 607 s) y
  después (559 pruebas en verde con `CLAUDE.md` y `LEEME.md` al día, en 354 s).
- **Respondiste «publica», y el push lo haces tú** (regla permanente y `metodo-ciclo`): creo con `gh` el repo vacío y
  agrego el remoto; tú subes `main` con los comandos que te dejo; después compruebo en GitHub un solo commit y que
  `historial-local` no esté.

## Veredicto del PASO 0, por parte del encargo

| Parte | Veredicto | Qué quedó |
|---|---|---|
| Revisar el árbol: credenciales, correos, RUT, contratos, nombres, rutas, reservas | **CICLO** | Hallazgos abajo; `7d9e52c`, `a119d14`, `ecd89e9`, `f823586` |
| Revisar el historial | **NOTA:** sin credenciales; lo demás queda en `historial-local` | Sin cambios: no se publica |
| Los contratos y lo que el programa necesita, a `config.json` | **CICLO** | `7d9e52c` (contratos) y `f823586` (código de Shipper de HYUNDAI) |
| Los generadores y el logo | **FRENA** (cambiar sus datos cambiaba el material); decidiste: fuera del repo | `a119d14` |
| Tu nombre | **FRENA**; decidiste: queda | Sin cambios |
| Los datos de la empresa que el programa usa | **FRENA SI:** reportados, sin tocar; decidiste: se publican tal como están | Sin cambios |
| El autor del commit publicado | Decidiste: el correo noreply de GitHub | El commit de la `main` nueva |
| La rama huérfana y `historial-local` | **CICLO**, local, después del commit de este informe | `orfana.sh` |
| Sin licencia | **NOTA:** el repo no trae `LICENSE` | Sin cambios |
| Tu FRENA SI de credenciales | **NOTA:** no se cumple | — |
| Tu FRENA SI de `gh` | **NOTA:** no se cumple (rol `admin` en la organización; el token tiene `repo`) | — |
| La publicación | Respondiste «publica»; el push lo haces tú | Los comandos, en el mensaje final |
| El correo de los commits nuevos | Decidiste: el noreply, como `user.email` de este repo | `.git/config` del repo |

## La revisión, sin valores

### Cómo se midió

`revision_datos.py` mide el árbol de un commit (los archivos de `git ls-tree`) y el historial (cada versión distinta de
cada archivo, alcanzable desde todas las ramas, y los mensajes y autores de los commits). Busca dos cosas:
- **Los valores reales de este equipo**, sin imprimirlos:
  - de `config.json`, los usuarios, las claves y los contratos de cada naviera, los contratos por defecto y el código de
    Shipper de HYUNDAI, y el nombre del operador como lo arma la sonda de secretos;
  - de la planilla y de la que subió el panel, las naves, los viajes, las reservas, los números de reserva y las
    cotizaciones;
  - de los `log.txt`, las naves y los números de reserva con la forma de ONE, MSC, HYUNDAI y MAERSK;
  - y los contratos que el programa del commit medido trae escritos.
- **Formas genéricas:** correos, RUT con su dígito verificador, rutas de Windows con el usuario y su forma corta 8.3,
  prefijos de tokens, llaves privadas, asignaciones de una clave con su valor, teléfonos, etiquetas de confidencialidad,
  posibles nombres de personas, cifras de 7 o más y códigos con forma de cuenta (letras y cifras) en una línea que habla
  de contratos, clientes o cuentas.

Su control positivo aborta si un caso sintético de cada diccionario y de cada forma no da positivo. Cuenta las
**coincidencias**, no las líneas: una línea con dos cuenta dos. Cuenta también lo que salta: los valores de menos de 4
caracteres, las carpetas de `logs/` sin `log.txt` y las versiones binarias.

Aparte:
- `quitados.py` busca en un árbol, sin imprimirlos, los siete valores que el encargo sacó (los cuatro contratos, los dos
  del comentario de COSCO y el código de Shipper de HYUNDAI) y la carpeta de tu usuario de Windows, en su forma corta y
  en la larga; su control exige que cada uno esté en el commit de donde salió.
- `historial_commits.py` cuenta los commits cuyo árbol trae el nombre del operador, y compara las rutas de todos los
  commits con las rutas prohibidas de la sonda de secretos.
- La sonda de secretos del repo (`--almacen`) mira los 1183 objetos de git, con sus tres negativos.

### Lo que encontró en el árbol de `503718b` (73 archivos)

| Qué | Dónde | Qué se hizo |
|---|---|---|
| Credenciales, tokens, llaves, RUT | Ninguno. Una asignación de clave, sintética, en `tests/test_sonda.py` | Nada |
| Contratos por defecto | `AQUASHIELD.py`: 2 de ONE (más el docstring y un comentario que los repetían), 1 de MSC y 1 de HYUNDAI, en dos lugares | A `config.json` (`7d9e52c`) |
| Un número de la cuenta y un contrato | Un comentario de COSCO en `AQUASHIELD.py` | El comentario, sin ellos (`7d9e52c`) |
| Los contratos de ONE, por hash | 3 aserciones de `tests/test_ayudantes.py` (el hash corto de un código corto se revierte probando) | Contratos sintéticos (`7d9e52c`) |
| El código de Shipper de HYUNDAI | `AQUASHIELD.py`: un comentario, el localizador del modal y un respaldo en JavaScript | A `config.json` (`f823586`) |
| Naves, viajes, números de reserva y contratos reales | Los cuatro generadores de material | Fuera del repo (`a119d14`) |
| Tu correo de la empresa, tu celular, tu nombre completo | Los generadores (5 coincidencias de correo y 7 de teléfono, en los 4) | Fuera del repo (`a119d14`) |
| «Uso Interno Confidencial», con la razón social y el área | `generar_manuales.py` y `crear_video_demostracion.py` | Fuera del repo (`a119d14`) |
| El logo de la empresa | `logo_aquachile_dark.png` (sin bloques de texto) | Fuera del repo (`a119d14`) |
| La carpeta de tu usuario de Windows | La forma corta en `tests/soporte.py` y `CICLO-red-verificacion.md`; en los generadores, la larga | Un marcador (`ecd89e9`); los generadores, fuera |
| Tu nombre completo | El pie del panel web (`AQUASHIELD.py`) | Queda (decisión tuya) |
| «Marcelo» | 310 coincidencias en 26 archivos (en el árbol que se publica, 303 en 22), casi todas «decisión de Marcelo» | Queda (decisión tuya) |
| Datos de la empresa que el programa usa | `AQUASHIELD.py` (ver el resumen) | Quedan (tu FRENA SI y tu decisión) |
| Cifras de 7 o más | 110 coincidencias en 19 archivos: 26 en los generadores, el número de la cuenta de COSCO, 50 hashes de commits, 30 datos sintéticos de las pruebas, los 2 registros públicos del sitio de COSCO (ICP y «公网安备») y 1 color | Nada (el número de la cuenta, arriba) |
| Posibles nombres de personas | 56 coincidencias: 55 son «marco» (el marco de una página, no un nombre) y 1 es el pie del panel, con tu nombre completo | Nada |
| Correos | Los de los generadores (arriba) y 6 sintéticos (`.invalid`) en `tests/test_web.py` | Nada más |

Los `CICLO-*.md` hablan de corridas reales solo por fecha, fila y estado, sin valores.

### El árbol que se publica (`f823586`, 68 archivos)

Es el árbol del último commit de código; el commit de este informe le suma solo `CLAUDE.md`, `LEEME.md` y este archivo,
revisados con el mismo escáner antes del commit.
- **De los valores reales de este equipo, ninguno:** 0 coincidencias de los 10 diccionarios con valores: ni usuarios,
  claves o contratos de `config.json`, ni naves, viajes, reservas o cotizaciones de las planillas, ni naves o números de
  reserva de los `log.txt`. Tampoco hay teléfonos, etiquetas de confidencialidad, correos de la empresa, tokens, llaves,
  RUT ni rutas con tu usuario.
- **`quitados.py`:** los cuatro contratos, los dos valores del comentario de COSCO, el código de Shipper y la carpeta de
  tu usuario de Windows, en su forma corta y en la larga, aparecen en 0 de los 68 archivos (en `503718b`, en 5, 1, 1 y
  6).
- **Lo que queda, y qué es:**
  - «Marcelo»: 303 coincidencias en 22 archivos, casi todas «decisión de Marcelo», y tu nombre completo en el pie del
    panel;
  - 53 posibles nombres de personas: 52 son «marco» y 1 es el pie del panel;
  - 83 cifras de 7 o más, por la forma de su línea: 50 hashes de commits, 30 datos sintéticos de las pruebas, los 2
    registros del sitio de COSCO y 1 color (el corporativo, en el ícono del panel);
  - 20 códigos con forma de cuenta junto a contratos, clientes o cuentas: todos inventados, en las pruebas y las
    mutaciones (ninguno es un valor de `config.json`);
  - 6 correos sintéticos (`.invalid`) y 1 asignación de clave sintética, en las pruebas;
  - 2 marcadores neutros de la ruta corta;
  - y los datos de la empresa que el programa usa (tu FRENA SI).

### Lo que encontró en el historial (190 commits, 652 versiones de archivos, 1183 objetos)

- **Credenciales:** ninguna. `git fsck --unreachable` da 0, con los reflogs o sin ellos: todos los objetos los alcanza
  alguna rama.
- **El nombre del operador:** en 94 objetos de 9 archivos; por commits, en los 72 hasta `9710ae2` y en ninguno después
  (`historial_commits.py`, que mira el árbol de cada commit).
- **Lo mismo que el árbol, en sus versiones viejas:** los contratos de `config.json` en 5 archivos, el código de Shipper
  de HYUNDAI, los datos de los generadores (naves, viajes, números de reserva, cotizaciones, tu correo de la empresa, tu
  celular y la etiqueta de confidencialidad) y la ruta corta de tu usuario. La sonda cuenta 151 objetos con contratos o
  datos de la cuenta.
- **Las rutas:** 73 rutas distintas. 5 ya no están en el árbol (los cuatro generadores y el logo), y son las 5 que hoy
  prohíbe la sonda; ninguna es `config.json`, de `perfiles/` o de `logs/`, una planilla o un volcado
  (`historial_commits.py`).
- **Los autores:** los 190 commits llevan tu nombre y tu correo de la empresa, de autor y de committer.
- **Los mensajes:** tu nombre en 97 (por «decisión de Marcelo»), cifras de 7 o más en 4 (hashes de commits) y un posible
  nombre en 1 (otra vez «marco», en `448e3e4`); el correo de Anthropic va en los 190, en la línea `Co-Authored-By`.

Nada de esto se publica: queda en `historial-local`.

## Parte 1 · Los contratos por defecto salen a config.json (`7d9e52c`)

- **`_contrato_por_defecto(clave)`** lee `config.json` → opciones → `contratos_por_defecto` → `one_usa`, `one_otros`,
  `msc` o `hyundai`. Sin la llave, o si no es un texto, devuelve vacío y lo avisa una vez por corrida; el vacío escrito
  no se avisa: es una decisión del operador.
- **Cada naviera lo pide donde antes tenía el código:** ONE en `_determinar_contrato_one` (las dos), MSC en
  `reservar_msc` y HYUNDAI en sus dos pasos. El orden no cambió: en ONE y MSC, la fila, después las credenciales y al
  final este; HYUNDAI no mira la fila.
- **`config.example.json`** trae las cuatro llaves vacías, y su comentario lo explica. **Tu `config.json`** recibió los
  cuatro valores que el programa traía (`config_contratos.py`, con la escritura del programa: atómica, indentación 2,
  sin BOM), y lo demás quedó idéntico (comprobado, sin imprimir nada).
- **Los comentarios** de ONE y de COSCO quedan sin códigos ni números de la cuenta.
- **En un equipo sin los contratos:** ONE elige «Otros contratos» sin escribir uno y MSC deja el campo vacío, como hoy
  cuando la fila y las credenciales no traen uno. HYUNDAI, desde `f823586`, corta (Parte 4).

## Parte 2 · Los generadores y el logo, fuera del repo (`a119d14`)

- `crear_simulador_html.py`, `crear_video_demostracion.py`, `crear_video_tutorial.py`, `generar_manuales.py` y
  `logo_aquachile_dark.png` salen del índice (`git rm --cached`) y de la lista blanca del `.gitignore`. **Siguen en el
  disco y funcionan igual**; ya no se versionan.
- **La sonda de secretos ya no deja entrar ninguna imagen de las que reconoce** (`.png`, `.jpg`, `.jpeg`, `.gif` y
  `.webm`): el logo era la única permitida (`TestSondaImagenes`).
- **`TestCorridasDeReferencia`** lee los generadores que haya en el equipo. Sin ninguno, desde `f823586` se salta solo
  la prueba que los lee (`test_son_las_que_nombran_los_generadores`); aquí corre como antes.
- Se va la mutación que mutaba un generador; las corridas de referencia siguen vigiladas por otras mutaciones, en
  `AQUASHIELD.py`.

## Parte 3 · La ruta corta del usuario de Windows (`ecd89e9`)

Un comentario de `tests/soporte.py` y una línea de `CICLO-red-verificacion.md` traían la forma corta 8.3 de la carpeta
de tu usuario de Windows. Ahora traen un marcador neutro con la misma forma, que el escáner reconoce aparte. El script
la buscó por su forma, sin escribirla, y exigió una sola en cada archivo.

## Parte 4 · Lo que encontró la revisión de código (`f823586`)

- **HYUNDAI sin contrato corta antes de Booking Details.** Sin contrato en las credenciales ni en `config.json`,
  `reservar_hyundai` levanta `ObjetivoNoEncontrado` (NO ENVIADA, con su evidencia): elegir uno sería por su posición. En
  el paso 2 sigue sin elegir (queda el del portal). La primera opción real queda solo para un contrato que no está en la
  lista, como antes del encargo.
- **El código de Shipper de HYUNDAI sale a `config.json`** → opciones → `codigo_shipper_hyundai`
  (`_codigo_shipper_hyundai`, que avisa como el de los contratos). El modal busca la fila por «AQUACHILE S.A.», por el
  código si viene y por «AQUACHILE»; el respaldo en JavaScript escribe el código solo si viene. Sin él, un texto vacío
  no entra al localizador: `has-text('')` calzaría con cualquier fila. Tu `config.json` ya lo trae (`config_shipper.py`,
  que comprobó también que los cuatro contratos son los de `503718b`).
- **COSCO:** el ejemplo de un comentario pasa a ser inventado, y un comentario explica los dos números de
  `_COSCO_NO_ES_NUMERO`: son los registros públicos del sitio de COSCO, no de la cuenta.
- **La sonda de secretos** bloquea también los contratos y los datos de la cuenta de `config.json` (`datos_de_cuenta`:
  los `contrato*` de cada naviera, los contratos por defecto y el código de Shipper), con su control C3, y los
  generadores (`crear_*.py`, `generar_manuales.py`). En `--almacen` los datos de la cuenta solo informan, como el nombre
  del operador: el historial anterior los trae.
- **`test_la_poda_no_las_toca`** usa las corridas de referencia del programa: ya no se salta en un equipo sin los
  generadores.
- **Las pruebas:** 6 nuevas, `TestSondaCuenta` (3), `test_bloquea_un_contrato_sin_mostrarlo` y el código de Shipper en
  `TestContratosPorDefecto` (2). `test_hyundai_sin_contrato_no_elige_a_ciegas` exige ahora el corte, y
  `test_el_programa_ya_no_los_trae` mira también las líneas que hablan de Shipper, clientes o cuentas, y cualquier
  código de 4 letras y 4 cifras. Mutaciones: 11 nuevas, 1 quitada y 6 reancladas.

## Parte 5 · La rama limpia (después del commit de este informe)

`orfana.sh`, en este equipo:
1. Aborta si el árbol tiene cambios, si no está en `main`, si `historial-local` ya existe o si ya hay un remoto.
2. Arma una rama huérfana con el mismo índice y pasa la sonda de secretos sobre él. Si no da 0, vuelve a `main` y no
   queda nada creado.
3. Crea `historial-local` en el último commit de `main`, que es el de este informe.
4. Hace un solo commit con autor y committer `Marcelo Ramirez <269565694+1992MARS@users.noreply.github.com>`, y esa rama
   pasa a ser `main`.
5. Comprueba que `main` tenga un solo commit, que su árbol sea idéntico al de `historial-local`, el autor, y que no haya
   etiquetas ni remotos.

**Lo probé antes en dos clones de prueba de `f823586`**, con la sonda reemplazada, porque un clon no trae `config.json`.
Con la sonda en 0, dejó `main` con un solo commit, el mismo árbol, el correo noreply de autor y de committer, y
`historial-local` en `f823586` (190 commits), sin etiquetas ni remotos. Con la sonda fallando, volvió a `main` sin crear
nada. Los dos clones los borré.

**Después de tu «publica»,** el commit con tus decisiones va a `historial-local`, y `main` se rehace igual desde ahí: un
solo commit, con el árbol nuevo. La `main` de antes no había salido del equipo.

Lo que dio en el repo está en el mensaje final del encargo: este informe va dentro del commit y no puede citarlo.

## Parte 6 · La publicación (después de tu «publica»)

El encargo pedía que yo subiera `main`. **Una regla permanente posterior dice que el push lo haces tú** («CC no hace
push: lo hace Marcelo»), y `metodo-ciclo` dice que un encargo que pide push se reescribe para entregarlo. Queda así:
1. **Yo, con tu «publica»:** creo con `gh` el repo público `AquaShield-Team/Agendamiento-Reservas`, vacío y sin
   licencia, y agrego el remoto `origin`. Eso escribe el remoto en `.git/config`.
2. **Tú:** subes solo `main`, con los comandos del mensaje final (`git push origin main` y `ls-remote` con el hash
   esperado). Sin `-u`, el push no cambia la configuración.
3. **Yo, después:** compruebo en GitHub un solo commit y que sea el de `main`, solo la rama `main`, ninguna etiqueta,
   que `historial-local` no esté, que sea público y que no tenga licencia.

## Las revisiones

Dos revisores leyeron el trabajo, en el repo vivo y sin escribir en él (ver la pieza 7). Ninguno corrió pruebas ni leyó
`config.json`, `logs/`, las planillas ni los generadores.
- **La de código (11 hallazgos)**, sobre `7d9e52c`, `a119d14` y `ecd89e9`:
  - **el historial publicaría todo lo que se sacó** (crítico): lo resuelve la rama huérfana, que el encargo ya decidía;
  - **HYUNDAI sin contrato elegía la primera opción**, y **quedaba el código de Shipper**: `f823586`;
  - **nada impedía que un contrato volviera:** la sonda bloquea desde `f823586` los contratos y los datos de la cuenta,
    y la prueba mira más líneas. El número de la cuenta de COSCO, que no está en `config.json`, sigue sin guardián
    (residual);
  - **la prueba de la poda se saltaba de más:** `f823586`;
  - **la sonda reconoce las imágenes solo por cinco extensiones:** los generadores entraron a la lista en `f823586`; las
    extensiones, al residual;
  - **la documentación desalineada:** el commit de este informe;
  - **nada comprobaba que tu `config.json` trajera los mismos contratos:** `config_shipper.py` lo comprobó (iguales);
  - **un equipo sin contratos corre sin aviso** en ONE y MSC, y **el aviso de `_contrato_por_defecto` dice «no trae»
    también cuando `config.json` no se puede leer:** al residual, lo decides tú;
  - **los datos de la empresa y de las personas que quedan:** tu FRENA SI y tu decisión sobre tu nombre.
- **La del informe (18 hallazgos)**, sobre el borrador de las 17:58. Todos van en este informe:
  - el FRENA SI de los datos que el programa usa sí se cumple;
  - la rama limpia y la publicación van en futuro;
  - la lista blanca se mide por las rutas de cada commit, no con `--almacen`;
  - la sección del árbol que se publica;
  - el control positivo cubre ahora llaves privadas y rutas cortas;
  - la pieza 2 dice qué vigila cada cosa;
  - el comentario de COSCO no pasó a `config.json`;
  - las escrituras en tu `config.json`;
  - la versión del método;
  - los contadores que faltaban;
  - las coincidencias en lugar de las líneas;
  - lo que el remoto escribe en `.git/config`;
  - el residual, con cuándo se reabre cada cosa;
  - los gates tal como corrieron;
  - las fuentes de `gh` y del conteo de commits;
  - que no hay objetos inalcanzables;
  - que HYUNDAI no mira la fila;
  - y los detalles.

## La red y el gate de cada commit

| Commit | Pruebas | Mutaciones (pares) | Gate: suite | Gate: censo de sus filtros |
|---|---|---|---|---|
| `503718b` (base) | 547 | 1628 (1959) | 547 en verde (607 s), el «antes» | — |
| `7d9e52c` (los contratos) | 552 | 1643 (1976) | 552 en verde (513 s) | `TestContratosPorDefecto` 15 en 17 pares · `test_contrato_one` 4 en 6 |
| `a119d14` (generadores y logo) | 553 | 1643 (1976) | 553 en verde (479 s) | `TestSondaImagenes` 1 en 1 · `TestCorridasDeReferencia` 5 en 9 |
| `ecd89e9` (la ruta corta) | 553 | 1643 (1976) | 553 en verde (377 s) | Sin censo: no cambia pruebas ni mutaciones |
| `f823586` (la revisión de código) | 559 | 1653 (1987) | 559 en verde (414 s) | `TestContratosPorDefecto` 20 en 22 pares · `TestSondaCuenta` 5 en 7 · `test_bloquea_un_contrato_sin_mostrarlo` 2 en 4 · `sonda-nombre` 12 en 20 · `TestCorridasDeReferencia` 5 en 8 |
| El de este informe | 559 | 1653 | 559 pruebas en verde con `CLAUDE.md` y `LEEME.md` al día, en 354 s, el «después» | Sin censo: solo texto |

En los gates con filtros mordieron todos los pares, con 0 tiempos agotados, 0 pruebas sin mutación y los originales sin
cambios. Antes de cada gate de código corrió un precenso en una copia:
- el de `7d9e52c`, con los dos filtros de su gate;
- el de `a119d14`, solo con `TestSondaImagenes`: en una copia sin los generadores, las corridas de referencia no
  muerden;
- el de `ecd89e9`, solo la suite;
- el de `f823586`, la suite y cuatro filtros: 559 pruebas con 1 saltada, y en los cuatro primeros filtros del gate, los
  mismos pares, todos mordiendo.

Las copias no traen los generadores, como un clon: su suite pasó con 2 pruebas saltadas hasta `ecd89e9`, y con 1 desde
`f823586`.

**El censo completo de `f823586`** (`censo.sh`, con `TEMP` en la carpeta del encargo): 1653 mutaciones en 1987 pares, y
mordieron los 1987, con 0 tiempos agotados, 0 pruebas sin mutación y los originales sin cambios (4120 entradas). Duró 97
min, de las 19:43 a las 21:20, más que los 52 a 82 de los censos del 28-09 al 01-10: preparar sus copias tomó 55 min,
probablemente porque mientras tanto corrí el escáner del historial y la sonda (sin medir). No hubo eventos de
Kernel-Power en esa ventana. El primer censo del encargo, sobre `ecd89e9`, lo mató una suspensión, y el segundo lo
detuve para el commit de la revisión de código (pieza 4).

## Re-medir (pieza 1)

Las sondas son de solo lectura y no se versionan. Quedaron en la carpeta del encargo, en el scratchpad de esta sesión
(`$env:TEMP\claude\<proyecto>\<sesión>\scratchpad\e44`), que puede limpiarse: sin ellas, estos números no se re-miden.
- **`revision_datos.py`** (lee `config.json`, las planillas y los `log.txt`; `REV=<commit>` elige el árbol, y
  `SOLO_ARBOL=1` salta el historial): `salida_arbol_503718b.txt`, `salida_arbol_c4.txt` y `salida_historial_c4.txt`.
- **`quitados.py <commit>`** y `--indice`: `salida_quitados.txt`.
- **`historial_commits.py`:** `salida_historial_commits.txt`.
- **`nombres_y_cifras.py <commit>`:** de qué son los posibles nombres y las cifras largas de un árbol, por la forma de
  su línea.
- **`restos_temp.py` y `restos_borrar.py`:** las sandboxes de las pruebas en el temporal de Windows; el segundo borró
  las 7 de mis corridas desde las 17:09, por su nombre.
- **`salida_sonda_almacen_c4.txt`:** la sonda en `--almacen` y sus tres negativos, y `git fsck`, en `f823586`.
- **`orfana.sh`, `crear_repo.sh` y `verificar_publicacion.sh`:** la rama limpia; el repo y el remoto, con tu «publica»;
  y la comprobación, después de tu push. Ninguno hace push.
- **`revisar_docs.py <archivo>...`:** el mismo escáner sobre archivos sueltos, para los tres `.md` de este commit.
- **`contexto.py <archivo>:<línea>`:** una línea del árbol con los valores de los diccionarios, los correos, las rutas
  de usuario, los códigos y las cifras largas tapados (no tapa teléfonos ni nombres de personas).
- **`buscar.py` y `ver.py`:** buscan y muestran tramos del código con los códigos tapados.
- **`python tests/sonda_secretos.py --almacen`** y sus tres `--negativo-*`.
- **`gh` y `git fsck`:** `salida_gh.txt` y `salida_gh_y_fsck.txt`.
- **`config_contratos.py` y `config_shipper.py`:** escribieron en `config.json`, sin imprimir nada, y comprobaron que lo
  demás quedara igual. Una segunda corrida se niega: la llave ya está.
- **Las herramientas del gate:** `copia.py`, `aplicar_c1.py` a `aplicar_c4.py` (con sus `_pruebas`; los códigos se
  reemplazan por su forma, sin escribirlos), `anclas.py`, `precenso.sh`, `suite_y_precenso.sh`, `gate.sh`, `censo.sh`,
  `commit.sh`, `commit_c2.sh` y `entorno_e44.sh` (TEMP, TMP y TMPDIR dentro de la carpeta del encargo).

## NO retroceder (pieza 2)

- **Ningún contrato ni dato de la cuenta vuelve al programa:** van en `config.json`. Lo vigilan:
  - `TestContratosPorDefecto.test_el_programa_ya_no_los_trae`: ninguna línea que hable de contratos, Shipper, clientes o
    cuentas trae un código con letras y cifras, y no hay ningún código de 4 letras y 4 cifras;
  - la sonda de secretos, que bloquea los valores de `config.json` antes de cada commit.

  **No vigila nada el número de la cuenta de COSCO**, que son solo cifras y no está en `config.json` (residual).
- **Los generadores y el logo no vuelven al repo:** la sonda bloquea sus nombres y las imágenes.
- **HYUNDAI sin contrato no elige:** corta antes de Booking Details (`test_hyundai_sin_contrato_no_elige_a_ciegas`, con
  su mutación).
- **`historial-local` nunca se sube, ni ninguna etiqueta:** trae el nombre del operador y el correo de la empresa. Esto
  no lo vigila ninguna prueba: lo dice `CLAUDE.md`.
- **Cada commit que se publique lleva el correo noreply:** uno con el correo de la empresa lo publicaría. Tampoco lo
  vigila una prueba: `CLAUDE.md` pide revisarlo antes de cada push.

## Universo y cobertura (pieza 3)

| Medición | Universo | Cobertura | Descartados o saltados |
|---|---|---|---|
| El árbol de antes | Los 73 archivos de `503718b` | 72 de texto, línea por línea; el PNG, sus bloques de texto | 0 |
| El árbol que se publica | Los 68 archivos de `f823586`, más los tres `.md` del commit del informe | Todos de texto | 0 |
| El historial | Los 190 commits de todas las ramas en `f823586`: 652 versiones distintas de 73 archivos, sus mensajes y sus autores | 651 de texto, línea por línea; 1 versión binaria (el logo), contada y sin texto que leer | 0 |
| Los objetos de git | Los 1183 del almacén (`--almacen`); ninguno inalcanzable | 1183 | 0 |
| Los diccionarios | `config.json`, 2 planillas, los `log.txt` de `logs/` y los contratos del programa del commit medido | 94 valores reales en 10 diccionarios (más los 4 contratos del programa, al medir `503718b`), y 2 palabras del nombre del operador | 0 valores de menos de 4 caracteres; las URL, que son las públicas de los portales |
| `logs/` | Las 28 carpetas de `logs/`, todas con `log.txt`: 22 de corridas del panel y 6 de inicio de sesión (`salida_corridas_recientes.txt`) | Los 28 `log.txt`: las naves de las cabeceras de reserva y los números de reserva con la forma de 4 navieras | 0 carpetas sin `log.txt`; las 6 de inicio de sesión no traen cabeceras de reserva |

## Defectos de instrumento cazados (pieza 4)

1. **El tapado de `contexto.py` no cubrió todo:** tapaba solo los valores de los diccionarios, y los generadores traían
   valores que ya no están en la planilla (dos naves, dos contratos con otra forma, un teléfono). Salieron en la salida
   de la herramienta, que solo veo yo, no en el chat ni en el informe. Desde ahí no imprimí el contexto de los
   generadores, y el escáner sumó los teléfonos, las etiquetas de confidencialidad y los posibles nombres de personas.
2. **La primera pasada del escáner no buscaba teléfonos ni etiquetas de confidencialidad:** la segunda encontró 7
   coincidencias de teléfono y 3 de la etiqueta, todas en los generadores.
3. **El escáner tenía un punto ciego que la revisión del informe encontró:** no leía las opciones de `config.json`, así
   que medido sobre un árbol sin contratos en el programa su diccionario de contratos quedaba vacío, y su control
   saltaba los diccionarios vacíos. Ahora lee `contratos_por_defecto` y `codigo_shipper_hyundai`, y `quitados.py` busca
   los siete valores que se sacaron, con un control que no puede quedar vacío.
4. **El control positivo no traía una llave privada ni una ruta corta 8.3**, ni contaba lo que saltaba (los valores
   cortos, las carpetas de `logs/` sin `log.txt`, las versiones binarias). Las tres cosas están ahora.
5. **`historial_commits.py` contó contratos como si fueran el nombre del operador.** Tomaba todos los objetos que la
   sonda imprime en `--almacen`; desde `f823586` la sonda imprime también los que traen datos de la cuenta, y el conteo
   saltó de 94 a 114 objetos y de 0 a 11 commits con el nombre después de `9710ae2`. Un instrumento roto que alarma: lo
   vi porque el número cambió sin que cambiara el historial. Ahora lee solo la línea del nombre, y aborta si no la
   encuentra: 94 y 0, como antes.
6. **Un parche escrito con un heredoc de Bash perdió las barras invertidas:** la herramienta de Bash convierte `\\` en
   `\`. Lo rehice con las herramientas de escritura, en un texto crudo.
7. **`git log -S` sobre el historial tardó más de dos minutos** (lo pasé a segundo plano); con él supe que los dos
   números de `_COSCO_NO_ES_NUMERO` entraron en el primer commit y están en 12 HTML de `logs/`, junto al registro del
   sitio.
8. **Una suspensión del equipo mató el primer censo completo y dejó colgados a los dos revisores:** pedí que el equipo
   no se suspenda, relancé el censo y retomé a los revisores. Ese censo lo detuve después, para el commit de la revisión
   de código.
9. **Mis guiones de prueba usaban el temporal de Windows,** y desde las 17:09 la regla permanente pide TEMP y TMP dentro
   de la carpeta del encargo. En Git Bash hace falta además TMPDIR, que Git Bash trae puesto y que Python mira antes que
   TEMP (medido). Las 7 sandboxes que dejaron mis corridas desde esa hora (una por suite completa, cada una con el
   programa y una configuración sintética) las borré por su nombre; desde el gate de `f823586`, todo va en la carpeta
   del encargo.
10. **Las pruebas de las corridas de referencia no pueden morder en una copia sin generadores:** el precenso de esas
   copias corrió sin ellas; el de las corridas de referencia, en el gate de la raíz.

## Premisas del encargo contrastadas (pieza 5)

- **«Los 74 commits hasta 9710ae2 traen el nombre del operador»:** son 72 (`git rev-list --count 9710ae2`), y los 72 lo
  traen en su árbol; ninguno después (`historial_commits.py`, por commit).
- **«Un comentario de reservar_one trae los dos códigos de contrato de ONE»:** más que eso. Los dos estaban también en
  el docstring de `_determinar_contrato_one` y, sobre todo, como valores por defecto que el programa usa; y había otros
  dos, de MSC y de HYUNDAI, un número de la cuenta y un contrato en un comentario de COSCO, y el código de Shipper de
  HYUNDAI.
- **«config.json, perfiles/, logs/ y las planillas quedan fuera por la lista blanca»:** confirmado por las rutas de los
  190 commits: ninguna de esas rutas está en ninguno (`historial_commits.py`). `--almacen` no lo puede confirmar: no
  mira rutas.

## Residual (pieza 6)

- **`historial-local` trae lo que no se publica.** **Se reabre** si alguna vez hay que publicar el historial: habría que
  reescribirlo.
- **El correo de los commits nuevos:** desde tu «publica», el noreply es el `user.email` de este repo, y tu
  configuración global sigue con el de la empresa. `.git/config` no viaja: **se reabre** en otro clon, antes de su
  primer commit.
- **Los hashes de commit que citan `CLAUDE.md`, los `CICLO-*.md` y los comentarios son de `historial-local`:** en GitHub
  no existen. **Se reabre** si molesta leerlos así.
- **Los datos de la empresa que el programa usa quedan en el código público,** por tu decisión al responder «publica».
  **Se reabre** si decides pasarlos a `config.json`.
- **En un equipo sin `contratos_por_defecto`,** ONE elige «Otros contratos» sin escribir uno y MSC deja el campo vacío,
  sin avisar (la revisión de código propone que queden NO ENVIADA, como HYUNDAI). **Se reabre** si un equipo sin esos
  contratos tiene que reservar, o si lo decides.
- **HYUNDAI elige la primera opción real cuando el contrato no está en la lista,** y «Named Customer» también elige la
  primera: los dos vienen de antes del encargo. **Se reabre** si lo decides.
- **El aviso de `_contrato_por_defecto` dice «no trae» también cuando `config.json` no se puede leer,** y lo lee en cada
  reserva. **Se reabre** si una reserva sale sin contrato teniéndolo.
- **El número de la cuenta de COSCO no tiene guardián:** no está en `config.json` y son solo cifras. **Se reabre** si
  quieres que la sonda lo bloquee (habría que guardarlo en `config.json` sin que el programa lo use).
- **La sonda reconoce las imágenes por cinco extensiones** (`.png`, `.jpg`, `.jpeg`, `.gif`, `.webm`): un `.svg`, un
  `.webp` o un `.pdf` pasan. **Se reabre** si quieres sumar extensiones.
- **En un clon sin los generadores, `test_son_las_que_nombran_los_generadores` se salta,** y sus dos pares
  mutación-prueba (`referencia-falta-una` y `referencia-sin-comodin`) contarían como que no muerden (sin medir en un
  clon). **Se reabre** si el censo tiene que correr en un clon.
- **Los generadores y el logo ya no tienen versiones:** un cambio en ellos no queda en git. **Se reabre** si quieres
  versionarlos en otro lugar.
- **El temporal de Windows tiene 1676 sandboxes `aquashield_red_*` de corridas anteriores a la regla** (del 24-09 a las
  17:09 de hoy, incluidas las de este encargo hasta esa hora). **Se reabre** si quieres que se borren: es otro encargo.
- **Nada de esto se probó en el portal.**

## Reglas de método aplicadas (pieza 7)

**Versión:** el encargo empezó con `metodo-ciclo` v14 y la v15 entró a las 17:01, a mitad del ciclo. Este informe se
declara contra la **v15**; su regla nueva («lo que está fuera del encargo se propone, no se construye») se aplicó desde
ahí: el residual propone y no construye. El commit de la revisión de código (`f823586`) cabe en el encargo: el código de
Shipper es un dato que el programa necesita (DATOS del encargo), el corte de HYUNDAI arregla lo que cambió `7d9e52c`, y
la sonda y la prueba de la poda son los guardianes de los propios cambios.

Las reglas aplicadas:
- **PASO 0 de solo lectura**, con la revisión completa antes de tocar nada, y tus decisiones antes de la rama limpia.
- **Control positivo que aborta** en el escáner (un caso de cada diccionario y de cada forma), en `quitados.py` (cada
  valor en su fuente) y en la sonda (sus tres negativos).
- **Todo salto silencioso lleva contador:** los binarios, los valores cortos y las carpetas de `logs/`, contados.
- **La unidad la fija el sujeto:** el valor por coincidencia, la versión por archivo y el commit por su árbol.
- **El negativo tiene que morder:** cada prueba nueva con su mutación, y el censo completo sobre el último commit de
  código.
- **Fuente única:** los contratos por defecto y el código de Shipper viven solo en `config.json`.
- **Cada reemplazo afirma que su viejo aparece una vez,** también los que se buscan por su forma (los códigos).
- **Frenar cuando la decisión es de negocio:** los generadores, tu nombre, el logo y el autor, en cuatro preguntas; los
  datos de la empresa que el programa usa, reportados y sin tocar.
- **El push se entrega, no se hace.**
- **El entorno vive en un solo lugar:** las dos fallas de la máquina que medí (`TMPDIR` en Git Bash, y el solo lectura
  de git al borrar un clon) quedaron en `~/.claude/CLAUDE.md`, «Entorno Windows de esta máquina», con su plan B.

**Choques, y cómo se resolvieron:**
- **El encargo pedía que yo hiciera el push, y la regla permanente de las 17:09 dice que lo haces tú.** Mandan la regla
  y `metodo-ciclo`: te entrego los comandos (Parte 6).
- **Reglas permanentes que entraron a las 17:09 y no cumplí antes de verlas:**
  - **TEMP y TMP dentro de la carpeta del encargo:** ver el defecto 9;
  - **los revisores no trabajan en el repo vivo:** los dos revisores leyeron el repo vivo, sin escribir en él, y el de
    código dejó sus scripts y sus salidas en el scratchpad de la sesión, fuera de la carpeta del encargo. Los moví a
    `e44/revisor_codigo/`; sus salidas no traen ningún valor de los diccionarios (`revisar_docs.py`);
  - **las revisiones que ECC pide se proponen, no se lanzan:** las dos revisiones las lancé yo, después de esa hora.
- **«Fuente única» frente a dejar en el código los datos de la empresa que el programa usa:** los dejó tu FRENA SI, y al
  responder «publica» decidiste publicarlos tal como están.

## Entregable (pieza 8)

- Este informe, `CICLO-publicar-el-repo.md`, con `CLAUDE.md` y `LEEME.md` al día, en el último commit de
  `historial-local` y en el de la `main` nueva.
- La forma, medida antes del commit: `revisar_informe.py` sobre este informe, `CLAUDE.md` y `LEEME.md` (sin CR ni BOM,
  sin caracteres invisibles, sin voseo ni marcadores; ninguna línea de prosa nueva de más de 120: las 2 de `CLAUDE.md`
  ya estaban), y `revisar_docs.py` y `quitados.py` sobre los tres: ningún valor de los diccionarios ni de los que se
  sacaron.
