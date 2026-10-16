# Encargo 71 · El login de HYUNDAI va siempre a su página de login

**Base:** `C:\dev\Agendamiento Reservas` @ `21d92bf` · árbol limpio al empezar.

Cambio de código con `metodo-ciclo` v28. Es la opción 2 del encargo 70 (`CICLO-hyundai-en-clon-nuevo.md`), la que
elegiste. Todo se midió sin abrir ningún portal ni tocar `config.json`.

**Al abrir el ciclo:**
- `main` local y `origin/main` están en `21d92bf` (ya subiste el informe 70), y `origin/estable` en `a2998b0`.
- Entre los dos solo cambian el informe 70 y `CLAUDE.md`: el código que reciben los colegas es el mismo de `main`.
- Ninguna librería de terceros viaja en el HTML del panel. Carga solo lo propio (`/app.js`, `/estilo.css` y
  `/fuentes.css`), así que no hay avisos de seguridad que consultar.

## En resumen

- **`login_hyundai` va siempre a `HMM_LOGIN`,** `https://www.hmm21.com/e-service/auth/login.do`, escrita en el
  programa, y ya no lee la `url` de las credenciales. Así hace también `login_maersk`, que va siempre a su página de
  reservas, y sin sesión MAERSK lo lleva al login.
  - Hasta ahí iba a esa llave, y solo sin ella al login. La plantilla trae ahí la portada, `https://www.hmm21.com/`, en
    `usuario1` y `usuario2`: en un clon nuevo, esos dos operadores iban a la portada (encargo 70).
  - Es la misma dirección que el programa ya usaba de respaldo. Ningún otro código cambia.
- **Por el camino real y sin red, los tres casos del encargo van al login** (tabla abajo):
  - un `config.json` creado desde la plantilla, con `usuario1`;
  - un operador con la forma del de las corridas de este equipo;
  - y un operador creado desde Credenciales.
- **La llave `url` queda en la plantilla, sin uso.** Lo decidí yo, como pediste; el porqué, abajo.
- **Prueba nueva, con 4 mutaciones,** que caen las cuatro. La cuarta salió de la revisión de código.
- **Las dos revisiones del diff:**
  - la de código lo aprobó, con un LOW que arreglé;
  - la de seguridad no encontró nada CRITICAL ni HIGH. Su LOW es previo al cambio, y va al residual.
- **No se activó ningún FRENA:** no cambia otra naviera, ni la regla del «Contract No», ni `test_candado`.

## El cambio

En `AQUASHIELD.py`, una constante y una línea:

```python
HMM_LOGIN = "https://www.hmm21.com/e-service/auth/login.do"
...
        page.goto(HMM_LOGIN, wait_until="domcontentloaded")     # antes: page.goto(url, …), con
                                                                # url = creds.get("url") or "…/auth/login.do"
```

El resto de `login_hyundai` no cambia: el mismo formulario, el mismo clic y la misma forma de reconocer la sesión.

**Los 22 inicios de sesión de HYUNDAI guardados en `logs/` son del operador cuya `url` es esa misma página.**
- Son los 22 del operador de las corridas (el operador 1 de `config.json`).
- Los 22 encontraron su campo de usuario (`campo OK '#userId'`) y pulsaron «Login».
- 21 terminaron en el panel de e-service y 1 en la página de cambio de clave.

`logs/` no guarda la primera dirección del login, solo la última. Pero ese operador ya iba a la página del login, así
que en este equipo el cambio no mueve nada.

## Por el camino real, sin red

`sonda_login_e71.py` corre el programa de cada copia: la de `21d92bf` (el antes) y la cambiada (el después).
- Cada copia corre en una sandbox sin `config.json`, como un clon nuevo.
- Su panel lo crea desde la plantilla y guarda credenciales inventadas.
- «Solo iniciar sesión» corre con un Playwright falso, que anota cada dirección a la que va.

Los cuatro operadores de la sonda:

| Operador | Su `url` de HYUNDAI en `config.json` | HYUNDAI va a, antes | HYUNDAI va a, después |
|---|---|---|---|
| `usuario1`, el de la plantilla | `https://www.hmm21.com/` | la portada | el login |
| con la forma del de las corridas de este equipo | `…/e-service/auth/login.do` | el login | el login |
| creado desde Credenciales | sin la llave | el login | el login |
| control, con otra dirección | `https://portal.invalid/hmm` | `portal.invalid` | el login |

- **«Con la forma del de este equipo»:** leí el `config.json` de este equipo sin escribirlo.
  - Del operador 1 copié a la sandbox solo sus navieras, los nombres de sus llaves y la `url` de cada naviera, sin su
    consulta.
  - Usuarios, claves y contratos van inventados, y el operador va con otro nombre.
- **MAERSK fue a `https://www.maersk.com/book/` con los cuatro,** antes y después.
- **Los controles abortan:**
  - en el antes, `usuario1` tiene que ir a la portada, y el control a `portal.invalid`: el instrumento ve la llave
    cuando el programa la lee;
  - en las dos copias, cada operador va a una dirección por naviera y MAERSK a la suya, sin ningún efecto real (0).

## La llave `url`: queda en la plantilla, sin uso

Lo decidí yo, como pediste. Queda en `config.example.json` y en los `config.json` ya creados, y nadie la lee.
- **Sacarla de la plantilla no arregla nada que el cambio no arregle ya.** El panel crea `config.json` solo si falta,
  así que un `config.json` ya creado la conserva igual, el del colega incluido.
- **La de MAERSK tampoco se usa,** y sacarla tocaría otra naviera, que es una condición de freno. Sacar solo la de
  HYUNDAI dejaría las dos llaves sin uso tratadas distinto.
- **No cambia qué trae la plantilla ni lo que ve el colega al abrir el lanzador.**
- **El costo:** una llave que no hace nada, y alguien podría cambiarla esperando un efecto. Lo dicen `CLAUDE.md` y el
  comentario de `HMM_LOGIN`; el `_comentario` de la plantilla no (lo notó la revisión de código).

Si quieres la plantilla limpia, se sacan las dos en un cambio aparte, y ese toca MAERSK.

## La prueba y su censo

`test_clics.TestHyundai.test_el_login_va_siempre_a_su_pagina` llama a `login_hyundai` con una página falsa que anota
adónde va. Corre 9 casos:
- los dos operadores de la plantilla, leídos de `config.example.json` tal como vienen;
- en la llave, la portada, la del login, otra página de e-service, otra dirección, una vacía y `None`;
- y sin la llave.

En cada caso exige una sola ida, a `HMM_LOGIN`, y la línea «URL:» de `log.txt` con ella. Exige también que `HMM_LOGIN`
sea la página del login, y que algún caso traiga otra dirección en la llave: si no, la prueba no distinguiría leerla de
no leerla.

Sus 4 mutaciones caen las cuatro, cada una en su corrida:
- `e71-login-lee-la-url`: como hasta ahora, la llave y solo sin ella el login;
- `e71-login-la-llave-primero`: la llave si viene, aunque esté vacía;
- `e71-login-la-llave-si-es-de-e-service`: la llave solo si es otra página de e-service (la de la revisión);
- `e71-login-a-la-portada`: `HMM_LOGIN` con la portada.

**El censo del área** corrió sobre la copia del primer arreglo: 177 mutaciones y 244 pares, con las pruebas que
nombran. Entran:
- las 3 primeras mutaciones nuevas;
- las que caen a 15 líneas o menos del cambio (3);
- y las que nombran una prueba de `TestHyundai`, de las fotos que leen el texto del programa (`TestSinClicACiegas`,
  `TestFotoDeClicsGenericos`) o de `test_candado`.

Muerden los 244 pares, y la foto de los originales de la copia (80 entradas) no cambió: RESULTADO OK, en 12 minutos.
- **Después del segundo arreglo,** que cambia solo la prueba nueva y un comentario, corrí otra vez las mutaciones
  propias: 4 de 4 muerden, RESULTADO OK.
- **El chequeo de las 2.374 mutaciones del archivo da 0 problemas:** cada texto viejo aparece una vez, ningún id se
  repite, y cada una de las 834 pruebas tiene su mutación.

## Las revisiones

Una de código y una de seguridad, sobre `git diff 21d92bf..39c7078`. Cada una corrió en su propio worktree, nunca en
el repo vivo, y sin la suite completa.
- Los dos worktrees se crearon en `21d92bf`, no en `39c7078` (abajo, en mis errores). Les avisé, y las dos corrieron
  sus pruebas sobre una copia de `39c7078` sacada con `git archive` a su carpeta temporal, dentro de `e71`.
- Al terminar, los worktrees y sus ramas se borraron solos. Quité la carpeta vacía que quedó (`.claude\worktrees`).

| Hallazgo | De | Severidad | Qué hice |
|---|---|---|---|
| La prueba seguía en verde si se volvía a leer la llave solo cuando trae otra página de e-service: la mutación del revisor sobrevivía | código | LOW | arreglado: un caso más y su mutación. Medido: sobrevive con la prueba de `39c7078` y cae con la nueva |
| «Como `login_maersk` a la suya» era impreciso: MAERSK va a su página de reservas, que lleva al login | código | INFO | arreglado, en el comentario y en `CLAUDE.md` |
| La llave queda en la plantilla sin que su `_comentario` lo diga | código | INFO | residual: la plantilla no cambia en este ciclo |
| El comentario y `CLAUDE.md` citan este informe, que el commit del arreglo no trae | código y seguridad | INFO | va en el commit siguiente |
| «Son del operador cuyo `config.json` trae esta página» no lo pudo comprobar, porque no abre `logs/` | código | INFO | está medido (`operador_de_los_logins.py`: 22 de 22) |
| Si el `goto` a HMM falla, o la página redirige a otro sitio, `login_hyundai` escribe el usuario y la clave en la página que haya, sin mirar que sea la de HMM | seguridad | LOW, previo al cambio | residual, con la propuesta |
| El nombre del operador entra sin validar en la ruta de su perfil y de sus carpetas de `logs/` | seguridad | INFO, fuera del alcance | residual |

**Lo que verificó la de seguridad, sin encontrar un camino:**
- Los 17 `page.goto` del programa van a textos escritos en el programa, salvo el de `_login_portal`, que nadie llama.
- Ningún JavaScript del programa navega (`window.open`, `location`).
- El panel no escribe la llave `url`: `/api/credenciales` solo escribe `usuario`, `clave`, `contrato` y la
  descripción.
- La línea «URL:» de `log.txt` va sin la consulta ni los datos de la cuenta de la dirección.
- El diff no trae secretos, datos reales ni rutas del usuario.

Su LOW lo probó con una sonda con datos inventados: con el `goto` fallido, `rellenar` recibe la clave en otra página.
Si un campo real la aceptaría depende de la página, y no lo midió sin red.

**Lo que corrió la de código:** sus propias mutaciones. Caen todas menos la del LOW y una equivalente: leer la llave
sin usarla. Corrió también 89 pruebas de las clases vecinas, `test_candado` y las fotos, todas OK.

## Lo que el cambio no toca

- **Ninguna otra naviera:** el diff de `AQUASHIELD.py` es la constante, su comentario y dos líneas de
  `login_hyundai`. `login_maersk` aparece solo en el comentario.
- **La regla del «Contract No»:** sin cambios.
  - Sin un contrato de HYUNDAI en las credenciales ni en `contratos_por_defecto`, la reserva sigue quedando NO ENVIADA
    ahí (encargo 44).
  - Es lo siguiente que va a encontrar el colega, después del login.
- **`test_candado`:** no está en el diff, y pasa.
- **La página de reservas de HYUNDAI** sigue escrita en el programa (`BookingStepByStep1.do`).

## Antes de cada commit

- **El arreglo (`39c7078`):**
  - la suite completa, sobre el árbol de ese commit: 834 OK en 767 s, sin cambios en los 5.576 originales;
  - el censo del área (arriba): 244 de 244 pares;
  - la sonda de secretos dio 0 en seco y después del `git add`;
  - el barrido de datos reales dio 0 en las 82 líneas agregadas y en el mensaje.
- **Lo de la revisión (`732f4ad`):**
  - la suite completa, sobre el árbol de ese commit: 834 OK en 768 s, sin cambios en los 5.576 originales;
  - las 4 mutaciones propias, 4 de 4;
  - la sonda de secretos dio 0 en seco y después del `git add`;
  - el barrido dio 0 en las 17 líneas agregadas y en el mensaje.
- **Este informe:** la suite no lee los informes (de los `.md`, solo lee `LEEME.md`, que no cambia), así que vale la
  del commit anterior. La sonda de secretos y el barrido, sobre él y su mensaje, dieron 0.

## Premisas del encargo

- **«La dirección del login ya está en el programa como respaldo»:** confirmada. Es la misma que ahora usa siempre.
- **«MAERSK ya ignora su `url` de credenciales»:** confirmada. `login_maersk` va a `https://www.maersk.com/book/`, y
  ninguna línea lee su llave.
- **«Este equipo va al login porque su `config.json` trae esa dirección»:** confirmada. Los 22 inicios de sesión de
  HYUNDAI de `logs/` son del operador 1, y su `url` es la del login. El operador 2 trae la portada, como la plantilla.
- **«Los tres casos de la sonda deben ir al login»:** confirmada con el cambio. Sin él, `usuario1` iba a la portada.

## Residual

- **El equipo del colega, sin medir.** Le llega cuando avances `estable`. Se confirma con su `log.txt`:
  - el campo de usuario tiene que decir `campo OK '#userId…'`;
  - la última línea «URL:» del login tiene que ser una página de `www.hmm21.com/e-service/`.
- **Si HMM mueve su página de login,** ahora hace falta un cambio de código: la llave ya no la puede corregir. Se
  reabre si un `log.txt` dice `campo ERROR '#userId…'`.
- **Propuesta: que el login de HYUNDAI no escriba la clave fuera de HMM** (el LOW de la revisión de seguridad).
  - Si el `goto` falla, su error se calla, y el usuario y la clave van a la página que haya. Si la página redirige a
    otro sitio, también.
  - El navegador es el mismo para todas las navieras, y HYUNDAI va después de COSCO.
  - Un arreglo sería no escribir si la dirección no es de `hmm21.com`. Cambia lo que hace el login en un caso sin
    medir: si el login de HMM pasara por otro dominio, cortaría. Por eso no lo hice aquí.
  - Vale igual para las otras navieras. Se reabre si lo encargas.
- **El nombre del operador, sin validar como nombre de carpeta** (INFO de la revisión de seguridad). Entra en la ruta
  de su perfil de Chrome y de sus carpetas de `logs/`. Desde el encargo 66 solo lo escribe la página del propio panel.
  Se reabre si lo encargas.
- **La plantilla no dice que la llave `url` no se usa.** Se reabre si decides limpiar la plantilla.
- **Lo que dejó el encargo 70 sigue igual:**
  - el clic del login de HYUNDAI pulsa el primero de un selector genérico; en la página del login es su botón;
  - si el contrato configurado no está entre las opciones, se elige la primera real, por su posición. En `logs/` no
    pasó nunca;
  - sin uso: la llave `url` de HYUNDAI y la de MAERSK, `_login_portal` y `opciones/espera_seg`.

  Cada uno se reabre si lo encargas.

## Defectos de instrumento y errores míos

- **Imprimí en la consola de esta sesión cuatro palabras del portal que el barrido vigila.**
  - Leí con `cat` un script del encargo 70 que arma la lista de palabras extra del barrido, y las trae escritas.
  - No están en ningún archivo del repo, y este informe no las repite.
  - Desde ahí, la lista la saqué de ese script con `ast`, sin imprimirla.
- **Toqué la copia del censo mientras corría,** al pasarle a su `CLAUDE.md` el cambio del párrafo. Los 244 pares
  mordían, pero la foto de los originales vio el cambio, y el resultado fue FALLA. Lo volví a correr sin tocar nada,
  y dio OK.
- **Mi prueba dejaba pasar una forma de volver a leer la llave.** La encontró la revisión de código, y la arreglé
  (arriba).
- **El primer borrador del comentario de `HMM_LOGIN` decía que los 22 inicios de sesión «fueron a esta» página.**
  `logs/` no guarda la primera dirección, solo la última. Lo medí por operador y lo reescribí antes de aplicarlo.
- **Los worktrees de los dos revisores se crearon en `21d92bf`, no en mi commit `39c7078`.**
  - Lo medí con `git worktree list`. `21d92bf` es `origin/main`, y también era el HEAD antes del commit.
  - Lo vi después de lanzarlos, y les avisé que sacaran `39c7078` a su carpeta temporal para correr pruebas.
  - Lo sumé como fila en «Entorno» de `~/.claude/CLAUDE.md`.
- **Usé `sort` de Git Bash,** que Defender bloquea (fila de «Entorno»). No corrió nada; conté con Python.
- **Escribí por heredoc un reemplazo con barras invertidas,** contra la fila de «Entorno».
  - La herramienta juntó los pares, y Python avisó (`SyntaxWarning`).
  - El resultado salió bien: lo comprobé en el archivo y por los conteos del alcance.

## Re-medir

Todo corre desde `scratchpad\e71`, en Git Bash, después de `source entorno_e71.sh`. Ningún script imprime usuarios,
claves, contratos ni nombres de operador.

| Número | Script |
|---|---|
| Adónde va el login, antes y después, por el panel y «Solo iniciar sesión» | `python sonda_login_e71.py <src_head o src>` |
| Las copias de un commit, byte a byte | `python extraer.py <commit> <carpeta>`; los cambios, `aplicar71.py`, `aplicar_claude71.py` y `aplicar71b.py` |
| Los 22 inicios de sesión de HYUNDAI y su operador | `python operador_de_los_logins.py`, y `logs_hyundai.py` del 70 |
| Las `url` de `config.json` y de la plantilla | `forma_config.py` del encargo 70 |
| El alcance y el censo del área | `python alcance_e71.py <raíz>` y `python lanzar_censo_e71.py <salida> <raíz> [propias]` |
| El chequeo de todas las mutaciones | `python mut_viejos.py <raíz> e71-` |
| La suite, aparte | `python lanzar_suite_e71.py` |
| El barrido | `python barrido\barrido_e71.py --cached`, `<rango>`, `--mensajes <rango>` o `--texto <archivo>` |

## NO retroceder

- **`login_hyundai` no vuelve a leer la `url` de las credenciales.**
  - Con ella, la dirección del login dependía del `config.json` de cada equipo, y un clon nuevo iba a la portada.
  - Con ella, además, una llave editable decidía en qué página se escribía la clave de HYUNDAI.
  - Lo vigila la prueba nueva, con la plantilla tal como viene.
- **No se saca de la plantilla solo la llave de HYUNDAI:** quedarían las dos llaves sin uso tratadas distinto. Si se
  limpia la plantilla, van las dos, y eso toca MAERSK.

## Reglas de método aplicadas

`metodo-ciclo` v28 (la versión del archivo y la cargada coinciden) y las reglas del módulo (`CLAUDE.md`).

- **Paso 0:** barrí el registro por el tema: el informe 70 y el párrafo de `CLAUDE.md`, el único que nombra la llave.
  Veredicto: **CICLO**. La causa estaba medida, y la decisión ya era tuya.
- **Al abrir:** comparé lo publicado con su registro, y miré las librerías del HTML (arriba).
- **Re-medir contra HEAD antes de diseñar:** los 22 inicios de sesión de `logs/` y las `url` de `config.json` los
  medí de nuevo hoy; no los heredé del informe 70.
- **Control positivo que aborta,** en las tres sondas:
  - en la del camino real, el antes tiene que ver la llave;
  - en la de los operadores, el total tiene que dar 22;
  - en el barrido, un valor vigilado puesto a mano tiene que aparecer.
- **Todo salto silencioso con su contador:** 0 `log.txt` sin poder leer, y 0 inicios de sesión sin un operador
  reconocible.
- **Sobre el camino real:** el programa entero en una copia, con su panel creando `config.json` y «Solo iniciar
  sesión» leyéndolo, antes y después. La prueba llama a `login_hyundai` suelta; la sonda lo confirma por el camino
  entero.
- **El negativo muerde, de a uno:** cada mutación en su corrida del censo. El censo del área, con su alcance
  declarado.
- **Un negativo vacuo delata un caso incompleto:** la mutación de la revisión sobrevivía porque faltaba un caso, y no
  porque sobrara la prueba.
- **El cambio y su guardián en la misma operación:** la prueba y sus mutaciones van en los commits del arreglo.
- **Fuente única:** la dirección vive en `HMM_LOGIN`, y la prueba la lee de ahí y de la plantilla.
- **Cada reemplazo, una vez, y el EOL preservado:** cada texto viejo se contó antes de escribir; LF, y 0 CR después.
  - La escritura no fue atómica: fue en el mismo archivo, con el contenido ya validado y leído de vuelta.
  - Es el plan B de «Entorno»: la app de Claude retiene `AQUASHIELD.py`, y `os.replace` falla.
- **Antes de cada commit, todas las suites:** el resultado de cada commit está arriba.
- **Rutas absolutas y ningún comando detrás de un `cd`.** El temporal de todo lo que corrió, en `e71\t`. La limpieza
  del cierre vive dentro de la carpeta que borra, y la probé antes con un testigo.
- **Los revisores, cada uno en su worktree,** nunca en el repo vivo, y sin la suite completa mientras corría la mía.
- **Del módulo:**
  - ningún portal;
  - `config.json` solo leído (sus nombres de llaves y sus direcciones);
  - ninguna prueba importa `AQUASHIELD.py` desde la raíz, y nunca el puerto 8765;
  - la sonda de secretos y el barrido antes de cada commit, y el correo noreply.
- **Choques:** ninguno entre `metodo-ciclo` y el módulo. Las reglas de ECC piden pytest y anotaciones de tipo; el
  módulo usa `unittest` y su propio estilo, y mandan las del módulo.

## El repo

Tres commits en `main`, sin push: el repo es público, y lo pediste así.

- **`39c7078`:** el arreglo, su prueba, sus mutaciones y `CLAUDE.md`.
- **`732f4ad`:** lo de la revisión de código: un caso más en la prueba, su mutación y la comparación con MAERSK.
- **El de este informe.**

Los tres llevan de autor y de committer el correo noreply del repo. `estable` no se movió: llega a los colegas cuando
la avances.
