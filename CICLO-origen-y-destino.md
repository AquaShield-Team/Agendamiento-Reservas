# CICLO · El origen y el destino: las seis navieras guardan la lista de sugerencias antes de elegir, y el motivo de SIN-CUPO dice con qué buscó MAERSK; la regla nueva de MAERSK, en FRENO

**Módulo:** Agendamiento Reservas · **Encargo 41** · **Fecha:** 2026-09-30 · **Método:** skill `metodo-ciclo` v14 ·
**Commits** (locales; el repo no tiene remoto, así que no hay push que entregar):
- `5a21f31`: las seis navieras guardan la lista de sugerencias antes de elegir el origen o el destino;
- `e0924e6`: el motivo de SIN-CUPO dice el origen y el destino elegidos;
- `9644bac`: el control del censo corre por tandas, bajo el límite de Windows;
- `448e3e4`: lo que encontró la revisión de código;
- `e3e0a76`: el aviso de ONE compara solo el texto de la sugerencia, de la revisión de este informe;
- `c8a0467`: vuelve una mutación de ONE que el commit 4 quitó sin reemplazo, y la prueba nueva pide que la página falsa
  no vea nada inesperado, de su segunda revisión;
- y el de este informe, con `CLAUDE.md` al día.

**Base: `C:\dev\Agendamiento Reservas` @ `d6a0662` · árbol limpio** (pieza 9). Lo medido sale de los `log.txt` de las 14
reservas de MAERSK de `logs/`, de los 93 HTML de MAERSK guardados y del código en `d6a0662`.

> Datos reales solo en lectura. Las sondas leen los `log.txt` y el HTML en su lugar, sin copiarlos, e imprimen formas,
> cuentas, fechas y booleanos: en este informe no van nombres de naves, viajes, puertos, países de una fila, partes,
> códigos ni números de reserva. Los únicos nombres de países que aparecen son los que ya están en el código. No se miró
> ninguna captura.

**Resumen.**
- **La regla de MAERSK: FRENO, se cumple tu FRENA SI con lo medido (la segunda condición).** La sugerencia elegida tiene
  la forma de tu regla en 27 de las 28 elecciones de las 14 reservas guardadas, en 13 reservas enteras; no la tiene el
  destino del 29-09, el que ya nombras. Tu regla pide además que sea la única de su lista con esa forma, y eso no se
  puede medir, porque ninguna corrida guardó una lista: tu primera condición no se puede descartar todavía. Y con lo
  medido, el texto de cada sugerencia, el programa no puede reconocer el país del final sin una lista que no está en el
  código: en él, como datos que el programa usa, solo están Chile (en COSCO, la oficina de reservas de MSC y los
  feriados) y Estados Unidos (el contrato de ONE). Si MAERSK trae el país aparte en su HTML, no está medido. Lo único
  que comparten las 27 es que lo de más va después de la última coma, y eso es una posición, no un país. No escribí la
  regla (pregunta 1).
- **La lista de sugerencias, en las seis navieras:** antes de pulsar una sugerencia de origen o de destino, cada una
  deja la captura de la ventana y el HTML de la página y de sus marcos, con la lista: `<nav>_f<fila>_origen` y
  `_destino` (CMA, con su modo; MAERSK y COSCO, `_reintento` si vuelven a escribir la ciudad). Después del clic avisa si
  pulsó sin dejarla o si la lista cambió mientras la guardaba, comparando el texto de cada sugerencia (en ONE, desde el
  commit 5). La regla con que elige cada una no cambia, y no hay clics nuevos: 182 llamadas a clic o tecla antes y
  después. Con esas listas se puede medir la pregunta 1.
- **SIN-CUPO:** el motivo dice ahora con qué origen y destino buscó: la sugerencia que pulsó en cada campo y, si el
  campo no quedó con ella, lo que quedó. Va a la columna Estado de la planilla. Si la fila del 29-09 hubiera quedado
  SIN-CUPO (lo más probable con el detector del encargo 40, sin medir), ahí se habría visto el destino equivocado.
- **La revisión de código** encontró 0 críticos, 0 altos, 4 medios y 9 bajos. El commit 4 corrige dos medios y siete
  bajos, y mitiga los otros dos medios: avisa si la lista cambió, y el motivo dice lo que quedó en el campo. Dos bajos
  son tuyos (preguntas 3 y 4), y también lo que queda de esos dos medios: si la evidencia puede retrasar el clic
  (pregunta 4) y comprobar que el campo quedó con la sugerencia, que es parte de la regla en FRENO (pregunta 1).
  Encontró además un defecto que ya existía, y grave: con la celda del puerto o del destino vacía, cuatro navieras
  pulsan a ciegas antes de la guarda (pregunta 5).
- **Las revisiones de este informe:** la primera encontró 1 alto, 5 medios y 11 bajos, y la segunda, 0 altos, 3 medios y
  8 bajos. El alto de la primera cambió cómo presento el FRENO (arriba). Dos hallazgos eran de la red: un aviso de ONE
  que podía salir con la misma sugerencia, que corrige el commit 5, y dos mutaciones que el commit 4 quitó sin
  reemplazo, que vuelven en los commits 5 y 6. Lo demás es del informe, de `CLAUDE.md` y de mis sondas: una de ellas, la
  de los países del código, leía `logs/` sin declararlo.
- **El censo completo** se cayó a los 2 minutos sobre `e0924e6`: su control pasaba las 520 pruebas en una línea de
  comando de 33.374 caracteres, y Windows no acepta más de 32.767. Lo arregla el commit 3: el censo sobre `448e3e4` pasó
  su control en 2 tandas, y lo detuve después, porque el commit 5 lo dejaba sin uso. El censo completo sobre `e3e0a76`
  pasó su control (525 pruebas en 2 tandas) y dio 1478 mutaciones en 1764 pares, y todas muerden: 0 pruebas sin
  mutación, 0 tiempos agotados y 3397 originales sin cambios, en 82 min y sin suspensión. El commit 6 solo agrega una
  mutación y una aserción: lo cubren su gate y ese censo (la red, abajo).
- **Nada de esto se probó en el portal.** `test_candado` no cambia.

## Veredicto del PASO 0, por parte del encargo

| Parte | Veredicto | Qué quedó |
|---|---|---|
| MAERSK elige el origen y el destino con la regla nueva | **PREGUNTA (FRENO):** con lo medido, el país del final no se reconoce sin una lista que no está en el código | Sin cambios en la regla (pregunta 1) |
| Las 14 reservas guardadas, con la regla nueva | **NOTA:** la elegida tiene la forma de la regla en 27 de 28 elecciones, y no el destino del 29-09; si era la única de su lista, sin medir (0 listas guardadas) | — |
| Las seis navieras guardan la lista antes de elegir | **CICLO** | `5a21f31`, `448e3e4` y `e3e0a76` |
| El motivo de SIN-CUPO con el origen y el destino | **CICLO** | `e0924e6` y `448e3e4` |
| Sin clics nuevos; `test_candado` no cambia | **NOTA:** se cumple (182 antes y después) | Sin cambios |

## Lo medido

**Las 14 reservas de MAERSK guardadas, con la regla nueva** (`formas.py`; los `log.txt` de `logs/`, en su lugar). Son 28
elecciones: el origen y el destino de cada reserva, de 3 textos de celda (1 de origen y 2 de destino) en 6 filas; la
sonda cuenta los textos distintos sin imprimirlos. Universo: las 23 carpetas de primer nivel de `logs/`, 0 sin
`log.txt`, 14 bloques de MAERSK, 0 sin cabecera, 0 sin la línea «Origen '…': …» o «Destino '…': …» y 0 «sin sugerencia».
La sonda imprime la forma de cada texto (cada palabra de la celda, «C»; cada una de más, «x»; los signos, tal cual),
nunca sus palabras:

| Campo | La celda | La sugerencia elegida | Reservas | ¿Tiene la forma de la regla? |
|---|---|---|---|---|
| Origen (1 texto) | «C C» | «C C, x»: la palabra de más, después de la última coma | 14 | sí |
| Destino de las filas 30 a 34 (1 texto) | «C C» | «C C, x», igual | 8 | sí |
| Destino de la fila 10 (1 texto) | «C, C» (la ciudad y el país) | «C, C»: la celda entera | 5 (26 y 27-09) | sí |
| Destino de la fila 10, el 29-09 | «C, C» | «C x, C»: una palabra de más en medio | 1 | **no** |

- La regla, como la escribiste: la única sugerencia que trae las palabras de la celda en el mismo orden, como palabras
  enteras, y de más solo un país al final (la sonda lo lee así: las de la celda al principio, sin otra en medio). La
  sonda mide solo la forma de la sugerencia elegida, con dos maneras de reconocer el país:
  - **A**, una lista de nombres de países de la sonda del encargo 40 (`palabra_pais.py`), que **no está en el
    programa**;
  - **B**, lo que va después de la última coma, que es una posición, no un país.

  Las dos dan lo mismo: 27 elecciones tienen la forma, en 13 reservas enteras, y 1 no, el destino del 29-09.

  Si la elegida era la única de su lista con esa forma, no se puede medir, porque ninguna corrida guardó una lista
  (abajo). Una ciudad que existiera en dos países, por ejemplo, daría dos, y la regla terminaría en NO ENVIADA.
- Ninguna sugerencia elegida llega a 45 caracteres, donde `_mk_ciudad` corta lo que anota: la más larga tiene 26.
  Ninguna trae letras fuera de ASCII, y ninguna celda tampoco.
- Ninguna se partió en dos líneas del `log.txt` (`lineas_siguientes.py`): en las 28, la línea siguiente empieza con la
  marca de tiempo del registro. Así que la sonda vio cada sugerencia entera.

**El país en el código** (`paises_en_el_codigo.py`). Busqué 210 nombres en las 14.107 líneas de `AQUASHIELD.py` en
`d6a0662`, sin las 6 de fuentes en base64, como palabra entera, sin distinguir mayúsculas ni tildes: los de una palabra
de la lista de la sonda del encargo 40 y 13 de dos palabras. Calzan 6:
- CHILE, en 15 lugares: los datos de COSCO (su país, `COSCO_COUNTRY`, su dirección y su puerto de carga), la oficina de
  reservas de MSC, los feriados, y comentarios y docstrings;
- UNITED STATES y USA: la lista con que ONE elige su contrato (`_determinar_contrato_one`, que también nombra así sus
  variables) y un comentario de `reservar_one`. En mayúsculas, «USA» está en 3 líneas: la de esa lista, el docstring
  de esa función y el comentario. En los otros 11 lugares, «usa» es el verbo: en comentarios, docstrings, la interfaz y
  un mensaje de la consola;
- CHINA y PARAGUAY, cada uno en un comentario;
- GEORGIA, una tipografía.

No hay una lista con que reconocer el país del final de una sugerencia.

**La lista de sugerencias guardada** (`opciones_mk.py`). En los 93 HTML de MAERSK de `logs/`, contando los de sus marcos
(70 de «detenida», 13 de la guarda y 10 sin objetivo), en 9 carpetas, hay 0 etiquetas `mc-option`: ninguna corrida
guardó la lista. No está medido si MAERSK muestra el país de cada sugerencia en un elemento o un atributo propio, o solo
en su texto.

**Dónde elige cada naviera** (el código en `d6a0662`). Son 7 ayudantes y 16 llamadas de origen y de destino:

| Naviera | Ayudante | Llamadas | Cómo elige hoy |
|---|---|---|---|
| ONE | `_fill_port` → `_fill_autocomplete` (`_JS_PICK_SUGGESTION`) | 2 | la que trae la ciudad y está más arriba en la pantalla |
| MSC | `_msc_puerto` | 2 | la más corta a la vista que trae la ciudad |
| COSCO | `_cosco_autocomplete` (`_JS_COSCO_AUTO_PICK`) | 2 | origen: la que dice Chile; destino: la que empieza con la ciudad y una coma, o la primera |
| HYUNDAI | `_hmm_autocomplete` | 2 | la primera que trae la ciudad |
| MAERSK | `_mk_ciudad` | 2 | la primera con «container yard» o la primera, entre las que traen los 5 primeros caracteres ASCII |
| CMA | `_cma_puerto` y `_cma_entrega` | 1 de origen, 3 de destino y 2 del lugar de entrega (uno por modo) | la primera con los 5 primeros caracteres ASCII; el lugar de entrega, la primera con «ramp» o la primera |

ONE, MSC, HYUNDAI y COSCO eligen y pulsan en un mismo JavaScript; MAERSK y CMA, con localizadores de Playwright. Los
mismos ayudantes escriben otros dos campos, el commodity de ONE y el contrato de COSCO, que no son origen ni destino.

**Sin clics nuevos** (`clics_por_funcion.py`). Hay 182 llamadas a `.click(` o `.press(` en las funciones y constantes de
nivel superior, en Python y en el JavaScript de sus textos: 182 en `d6a0662` y 182 con los cinco commits. Ninguna
función cambia su cuenta, y las 5 nuevas no tienen ninguna: `_sugerencia_sin_pulsar`, `_avisar_lista_distinta`,
`_texto_de_la_sugerencia`, `_mk_ruta_buscada` y `_mk_motivo_sin_cupo`.

## Cómo quedó cada punto

**1. La regla de MAERSK para el origen y el destino: FRENO, sin cambios.** `_mk_ciudad` elige como antes: entre las
sugerencias que traen los 5 primeros caracteres ASCII de la ciudad, la primera con «container yard» o, si no hay, la
primera; si no aparece ninguna, o si el campo no queda con sus 4 primeros, vuelve a escribir la ciudad una vez, y la
reserva sigue aunque tampoco quede. Su docstring lo dice ahora así, y que está en FRENO (hasta aquí decía que escribía
en «el primer campo visible y vacío» y que elegía la de «Container Yard»). Lo que falta para escribir la regla es cómo
reconocer el país (pregunta 1).

**2. La lista de sugerencias, antes de elegir, en las seis navieras** (commits 1, 4 y 5):
- Los 7 ayudantes reciben `evidencia=`, el nombre, y los 6 reservadores se la pasan solo para el origen y el destino:
  `<nav>_f<fila>_origen` y `_destino`. CMA agrega su modo (`cma_f<fila>_origen_<modo>`, `_destino_<modo>` y
  `_entrega_<modo>`, el lugar de entrega), porque vuelve a elegir en cada intento; MAERSK y COSCO, si vuelven a
  escribir la ciudad, dejan la de esa otra lista con `_reintento`. El commodity de ONE y el contrato de COSCO usan los
  mismos ayudantes y no la dejan.
- Una vez por lista, justo antes de pulsar la sugerencia que pulsaría sin ella: la captura de la ventana y el HTML de la
  página y de cada marco (con sus raíces shadow), con `_evidencia_antes_de_la_guarda`. La captura es la de la ventana
  porque la de página completa dispara un «resize», que podría cerrar la lista. La lista de COSCO está en el marco del
  formulario: queda en `cosco_f<fila>_origen_marco<n>.html`.
- Cómo sabe que la lista está: MAERSK y CMA, con el mismo localizador con que pulsan. ONE, MSC, HYUNDAI y COSCO eligen y
  pulsan en un mismo JavaScript, que ahora, con sus argumentos en una lista, pulsa solo con la marca true (el de ONE y
  el de COSCO aceptan todavía el texto solo, y pulsan, pero el programa ya no los llama así); con la marca false
  devuelve la que pulsaría sin pulsarla. En cada vuelta, mientras no la dejó, `_sugerencia_sin_pulsar` lo corre así (y
  pone la marca, para que nadie la olvide); después, igual que antes, con el clic. La regla con que elige no cambia, y
  no hay clics nuevos (182 antes y después).
- Después del clic, `_avisar_lista_distinta` avisa en pantalla y en `log.txt` si pulsó sin dejarla (la lista apareció
  entre la lectura y el clic, o la lectura falló) o si la lista cambió mientras la guardaba y el clic eligió de otra: la
  evidencia toma su tiempo, y el clic sale después (revisión de código, M1 y M3). ONE anota ahora cuál pulsó. El aviso
  compara el texto de cada sugerencia; en ONE, desde el commit 5, sin su etiqueta, su clase ni su posición, que su
  JavaScript agrega a la descripción y que cambian sin que cambie la sugerencia: la clase la lee después del clic
  (revisión de este informe, M4).
- La evidencia no corta por sí misma: si la lectura falla, no la deja y elige como siempre; si guardarla falla, lo
  avisa, como toda evidencia. Pero si la lista se cierra mientras se guarda (no medido), el clic de después ya no la
  encuentra, y cada ayudante sigue su camino de siempre sin sugerencia (según el código; la segunda revisión de este
  informe):
  - MSC y el puerto de CMA quedan NO ENVIADA, porque el paso no encuentra su objetivo; CMA, después de esperar hasta 30
    segundos, el plazo de Playwright, porque vuelve a leer el texto de la sugerencia.
  - El origen de COSCO vuelve a escribir la ciudad y, si tampoco la ve, queda NO ENVIADA; su destino vuelve a escribirla
    y sigue aunque no la vea.
  - MAERSK espera hasta 30 s y vuelve a escribir la ciudad.
  - HYUNDAI sigue sin ese campo y solo anota «sin sugerencia» en `log.txt`; el lugar de entrega de CMA, después de
    esperar hasta 30 s, también sigue sin él.
  - ONE, no se sabe: su JavaScript elige entre todos los elementos de la página que traen el texto, no solo los de la
    lista, así que podría pulsar otro; si no hay ninguno, queda NO ENVIADA.
- Cuesta, por lista, una lectura más en cada vuelta hasta que aparece y la evidencia (una captura y el HTML): dos por
  reserva, y en CMA, hasta tres por modo. No está medido en el portal cuánto tarda.

**3. El motivo de SIN-CUPO** (commits 2 y 4): «MAERSK dice: "…"; busqué con origen «…» y destino «…» (formulario
completo: …; SIN emitir)», armado por `_mk_motivo_sin_cupo`. De cada campo, la sugerencia que pulsó `_mk_ciudad`, entera
y en una línea, y si el campo no quedó con ella, «(el campo quedó con «…»)»; si no quedó ninguna, «(ninguna sugerencia
quedó en el campo)». «Quedó» es lo que el programa comprueba hoy, que el campo traiga los 4 primeros caracteres de la
ciudad, y lo tecleado también los trae; comprobar de verdad que quedó es parte de la regla en FRENO. El motivo no dice
«elegida», porque el registro del panel pinta de verde la línea que la trae. El `log.txt` anota la sugerencia con sus
primeros 45 caracteres, como antes, pero ahora en una línea.

**4. El control del censo, por tandas** (commit 3). El censo completo sobre `e0924e6` se cayó a los 2 minutos, sin
resultado: `tests/correr.py` corría su control (la copia sin mutar, con todas las pruebas que nombran las mutaciones) en
una sola línea de comando, y Windows no crea un proceso con una de más de 32.767 caracteres. Medía 32.554 con las 510
pruebas de `d6a0662`, 213 bajo el límite, y 33.374 con las 520 de `e0924e6`. Ahora `por_tandas` las reparte en tandas de
hasta 30.000 caracteres: con las 525 de `e3e0a76`, dos, de 29.947 y 4.013 (`tandas_control.py`), que juntas son las
mismas pruebas y en su orden. Los gates no lo veían, porque filtran.

## La red y el gate de cada commit

La red la cuenta `red_por_commit.py` en cada commit: las pruebas, las mutaciones y los pares mutación-prueba. El gate
corrió antes de cada commit, sobre el árbol con el cambio: la suite completa, la foto de los originales (3397 entradas,
0 cambios en los seis) y el censo filtrado de las mutaciones nuevas o tocadas y de las que nombran las pruebas que
cambiaron. Antes, un precenso en una copia, salvo en el commit 3, que cambió solo el corredor. Los filtros se solapan:
sus pares no se suman.

| Commit | Pruebas | Mutaciones | Pares | Gate: suite | Gate: censo filtrado (mutaciones en pares; todos muerden) |
|---|---|---|---|---|---|
| `d6a0662` (base) | 510 | 1407 | 1679 | — | — |
| `5a21f31` | 518 | 1445 | 1727 | 518, en verde (475 s) | `sug-` 38 en 48 · `cosco-origen` 17 en 17 · `test_solo_ahi` 35 en 77 |
| `e0924e6` | 520 | 1455 | 1737 | 520, en verde (608 s) | `mk-ruta` 7 en 7 · `mk-sincupo` 3 en 3 · `mk-zarpes` 2 en 3 · `sug-mk` 5 en 7 · `mk-origen-sin-guardar` 1 en 1 · `una-vez-mk` 1 en 1 |
| `9644bac` | 520 | 1455 | 1737 | 520, en verde (410 s) | `mk-ruta` 7 en 7 (el control, en una tanda) |
| `448e3e4` | 524 | 1474 | 1758 | 524, en verde (678 s) | `sug-` 53 en 64 · `mk-ruta` 10 en 11 · `mk-sincupo` 4 en 4 · `mk-zarpes` 2 en 3 · `mk-origen-sin-guardar` 1 en 1 · `cosco-origen` 17 en 17 · `test_solo_ahi` 35 en 77 |
| `e3e0a76` | 525 | 1478 | 1764 | 525, en verde (301 s) | `sug-` 57 en 70 · `mk-ruta` 10 en 11 |
| `c8a0467` | 525 | 1479 | 1765 | 525, en verde (329 s) | `sug-js-one` 5 en 5 · `sug-one-` 7 en 10 |

El encargo suma 15 pruebas, 72 mutaciones y 86 pares. Son netos: el commit 4 quitó 8 mutaciones de los commits 1 y 2 y
cambió 4 pruebas por otras (`red_diff.py`). Seis mutaciones tenían su ancla en código que cambió, y las reemplazan
otras: las cuatro `sug-*-lee-pulsando`, por `sug-sin-pulsar-pulsa`, porque la marca de solo leer la pone ahora
`_sugerencia_sin_pulsar`; `sug-js-cosco-pulsar-al-reves`, por las `sug-js-cosco-*` del JavaScript nuevo; y
`mk-ruta-buscada-vacia-entre-comillas`, por `mk-ruta-buscada-elegida`. Dos se quitaron sin reemplazo, y lo que vigilaban
seguía en el código: `sug-hmm-origen-sin-evidencia`, que vuelve en el commit 5 (lo vio la revisión de este informe), y
`sug-js-one-texto-solo-no-pulsa`, que vuelve en el commit 6 (lo vio la segunda revisión). Las 4 pruebas cambiaron de
nombre o se partieron al corregir lo que vio la revisión de código. Solo el primer precenso falló: `sug-` mordió 46 de
47 pares (pieza 4, 2). **El censo completo sobre `e3e0a76`:** el control, las 525 pruebas en 2 tandas, pasa; 1478
mutaciones en 1764 pares, y todas muerden; 0 pruebas sin mutación, 0 tiempos agotados y 3397 originales sin cambios.
Tardó 82 min, de 12:49 a 14:11: 11 de control, 44 de preparación y 27 de pares. No hubo suspensión: 0 eventos de
Kernel-Power en ese rato, y la misma consulta encuentra el apagado del 29-09 a las 11:37. El commit 6 no lo repite:
agrega una mutación, que muerde en su gate, y una aserción al final de una prueba, que solo puede hacerla caer más; el
programa y las demás pruebas son los mismos.

## Cómo probarlo

Con `Iniciar AQUASHIELD.bat` y las tres llaves de emisión cerradas; si el panel estaba abierto, ciérralo y vuelve a
abrirlo para que cargue el código nuevo. Corre una fila de cada naviera que puedas:
- En `logs\web_<nav>_<operador>_<fecha>\`, además de lo de siempre: `<nav>_f<fila>_origen.png` y `.html`, y
  `_destino` (en CMA, con el modo; en MAERSK y COSCO, `_reintento` si volvió a escribir la ciudad). En `log.txt`,
  «evidencia con las sugerencias de Origen: …».
- Si `log.txt` dice «pulsé una sugerencia sin dejar la evidencia de la lista», esa lista no quedó guardada; si dice
  «la lista cambió mientras guardaba su evidencia», la que quedó no es la lista de la que eligió; y si una captura sale
  sin la lista, la lista se cerró antes: eso no está medido. Y si después de una «evidencia con las sugerencias de …»
  el `log.txt` dice que no hubo sugerencia, o la fila queda NO ENVIADA en ese paso, la lista se cerró mientras se
  guardaba. Avísame en cualquiera de esos casos.
- Una fila de MAERSK que quede SIN-CUPO dice en su motivo el origen y el destino con que buscó.
- Para la pregunta 1: los `mk_f<fila>_origen.html` y `_destino.html` de una fila de MAERSK.

## Qué decides tú

1. **El país del final, y si la elegida es la única (FRENO).** La elegida tiene la forma de tu regla en 27 de las 28
   elecciones guardadas, y el destino del 29-09 no. Pero con lo medido, el texto de cada sugerencia, el programa no
   puede reconocer un país sin una lista que no está en el código, y si cada elegida era la única de su lista con esa
   forma no está medido. ¿Cómo sigo?
   - **Medir primero (te la recomiendo):** corre una fila de MAERSK con el candado cerrado. Desde este ciclo deja
     `mk_f<fila>_origen.html` y `_destino.html`, la lista tal como la muestra MAERSK. Con ella mido si cada sugerencia
     trae el país en un elemento o un atributo propio (así la regla lo reconocería sin una lista) y cuántas de la lista
     tienen la forma de la regla (con más de una, la regla daría NO ENVIADA), y te traigo la regla.
   - **Lo de más, solo después de la última coma:** calza con las 27 y rechaza el destino del 29-09, pero reconoce una
     posición, no un país: aceptaría «Ciudad, Región» si MAERSK ofreciera algo así.
   - **El país en la celda de la planilla:** si la celda trae la ciudad y el país, como ya la trae la fila 10, la regla
     pide las palabras de la celda y nada más, sin reconocer países. Las celdas que hoy traen solo la ciudad (el origen
     de las 6 filas y el destino de las filas 30 a 34) tendrían que traer también el país.
   - **Una lista de países:** en el código, cuál (los nombres como los escribe MAERSK, en inglés; algunos de dos
     palabras, como «United States») y quién la mantiene; o una librería de terceros, como pycountry, con los nombres de
     la norma ISO 3166. Sería una dependencia nueva, y si sus nombres son los que escribe MAERSK no está medido.
2. **Las otras cinco.** Cuando la regla de MAERSK esté decidida, ¿la llevamos también a ONE, MSC, COSCO, HYUNDAI y CMA?
   Desde este ciclo sus listas quedan guardadas, así que se puede medir antes.
3. **La lista cuando no hay ninguna que elegir.** Si la regla no encuentra una sugerencia, ONE, MSC, el origen de COSCO
   y el puerto de CMA cortan, y el corte deja su captura y su HTML; HYUNDAI, MAERSK, el destino de COSCO y el lugar de
   entrega de CMA siguen sin dejar nada. Tu decisión dice «antes de elegir»: ¿la dejamos también cuando no elige?
4. **Cuándo se lee lo que quedó, y si la evidencia puede retrasar el clic.** El motivo de SIN-CUPO toma el origen y el
   destino al elegirlos, no al buscar; entre medio el programa llena el commodity, el contenedor, el reefer y la fecha
   (sin tocar el origen ni el destino). Y la evidencia retrasa el clic lo que tarda en guardarse: si la lista cambia en
   ese rato, el clic elige de la nueva, y lo avisa. ¿Te sirve así?
5. **Fuera del encargo, y grave: la celda del puerto o del destino vacía.** `leer_filas` deja pasar una fila con nave y
   sin puerto de carga (o sin destino), y con el texto vacío ONE, MSC, HYUNDAI y el destino de COSCO calzan con
   cualquier elemento de la página y pulsan a ciegas antes de la guarda (lo reprodujo la revisión, en Node); MAERSK y
   CMA, probablemente también. Propongo un encargo aparte para que un origen o un destino vacío corte antes de escribir,
   como la fila sin nave.
6. **Las sandboxes que quedan en `%TEMP%`.** Hay 1408 carpetas `aquashield_red_*`, del 24 al 30-09 (3453 archivos, 1,15
   GB; `sandboxes_red.py`, a las 12:32). La causa que di antes, pruebas que el censo cortó por tiempo, explica pocas:
   en las 699 salidas de censo del scratchpad (encargos 21 a 41), solo una trae tiempos agotados, 4, en un censo
   filtrado del encargo 36 (28-09). Lo medido:
   - 470 están completas; 851 tienen solo el programa y 72 solo un `log.txt`, a medio borrar; 9 están vacías y 6 traen
     otra cosa. El borrado de `soporte` calla si no puede borrar (`ignore_errors=True`), y por qué no pudo no está
     medido.
   - Las 7 de hoy están completas, y cada una es de una corrida completa de la suite o del control del censo. Por el
     código, lo más probable es `test_web.TestArranqueDelPanel.test_instancia_previa_ocupada_no_se_toca`, que termina
     con `hijo.kill()` a un proceso hijo que creó su propia sandbox; un proceso matado no borra la suya.

   Borrarlas no detiene la fuga. ¿Las borro, sin ninguna corrida viva? Y propongo un encargo aparte para `soporte` y esa
   prueba.

## Re-medir (pieza 1)

Las sondas son de solo lectura y no se versionan: tres leen datos reales de `logs/` (`formas.py`, `lineas_siguientes.py`
y `opciones_mk.py`), y las demás son herramientas de este ciclo, con rutas de esta máquina. Quedaron en el scratchpad de
esta sesión (`$env:TEMP\claude\<proyecto>\<sesión>\scratchpad\e41`), que puede limpiarse; sin ellas, estos números no se
re-miden. Cada una declara su universo y su control positivo, que aborta si no pasa, y sus salidas quedaron en
`salida_<sonda>.txt`, en la misma carpeta (solo formas, cuentas y nombres del código):
- **`formas.py`:** las 28 elecciones de las 14 reservas de MAERSK de `logs/`, con la forma de la celda y de la
  sugerencia, su largo, los textos de celda distintos (sin imprimirlos) y la regla nueva con las dos maneras de
  reconocer el país (A, la lista de la sonda `e40/revision_informe/palabra_pais.py`; B, lo que va después de la última
  coma). Control: el destino del 29-09 a las 15:03 no calza con A ni con B, y el del 27-09 a las 21:15 calza con las
  dos.
- **`lineas_siguientes.py`:** la línea que sigue a cada una de esas 28 en su `log.txt`, por su forma. Control: las
  cabeceras «[MAERSK fila N]» tienen la forma de una línea del registro, y un texto con un salto no.
- **`paises_en_el_codigo.py [revisión]`:** los nombres de países en `AQUASHIELD.py` de esa revisión (por defecto la
  base, `d6a0662`), y en qué función o constante. Control: CHILE en `COSCO_COUNTRY`. Lee la lista de la sonda del
  encargo 40 con `ast`, sin ejecutarla; hasta la revisión de este informe la importaba, y al importarse recorría los
  `log.txt` de `logs/` (pieza 4). `formas.py` también la lee así.
- **`opciones_mk.py`:** las etiquetas `mc-option` en los HTML de MAERSK de `logs/`. Control: un texto sintético con dos,
  y que haya al menos un HTML.
- **`clics_por_funcion.py <árbol> [base]`:** las llamadas a `.click(` y `.press(` por función y constante, en la base
  (por defecto `d6a0662`) y en el `AQUASHIELD.py` de una carpeta, la raíz o una copia. Control: `_cma_puerto` 3 y
  `_JS_COSCO_AUTO_PICK` 3 en la base.
- **`largo_control.py <rev>…`:** el largo de la línea de comando del control del censo completo en cada revisión.
  Control: en `d6a0662`, donde el censo corrió, queda bajo el límite; corre siempre, aunque no se pida esa revisión.
- **`tandas_control.py <raíz>`:** `por_tandas`, sacada de `tests/correr.py` con `ast` (importarlo crea su carpeta de
  trabajo), sobre las pruebas que nombran las mutaciones: cuántas tandas, sus largos y que juntas sean las mismas.
  Control: 50 ids sintéticos con un largo de 1000 dan más de una tanda, ninguna más larga.
- **`sandboxes_red.py [día]`:** las sandboxes `aquashield_red_*` de `%TEMP%`: cuántas, de qué días, cuántos archivos y
  cuánto pesan, qué traen (completas, solo el programa, solo un `log.txt`, vacías u otra cosa) y la hora de las de un
  día. Control: las categorías suman el total.
- **`red_diff.py <antes> <después>`:** las mutaciones nuevas, quitadas y tocadas, y las pruebas nuevas y quitadas, entre
  dos revisiones. Control: de `d6a0662` a `5a21f31`, `sug-one-sin-evidencia` es nueva.
- **Las herramientas del gate:** `copia.py` (una copia de HEAD con `git archive`), `aplicar_c1.py` a `aplicar_c6.py` y
  `aplicar_docs41.py` (cada viejo, exactamente una vez; escritura en binario, LF, y atómica desde el commit 5),
  `anclas.py` (las anclas de las mutaciones que no calzan una vez), `largas_c1.py`, `largas_c2.py` y `largas_c4.py` (las
  líneas nuevas de más de 120; en los commits 5 y 6 las contó `anclas.py`, que también lo hace), `precenso.sh`,
  `suite_y_precenso.sh`, `gate.sh`, `censo.sh`, `commit.sh` y `red_por_commit.py`, los del encargo 40 con la ruta de
  este; y `revisar_informe.py`, la forma de un `.md`.

La red versionada, desde `C:\dev\Agendamiento Reservas`: `python tests/correr.py` (la suite, de 5 a 11 min en esta
sesión), `python tests/correr.py --mutaciones --filtro <texto>` (`sug-`, `mk-ruta`, `mk-sincupo`…) y
`python tests/correr.py --mutaciones` (el censo completo).

## NO retroceder (pieza 2)

- **La evidencia va antes del clic**, no después: después la lista ya se cerró, y lo que hay que medir es entre qué
  sugerencias eligió. Y el aviso de después del clic tampoco se quita: dice cuándo la evidencia no es esa lista.
- **Con la captura de la ventana**, no la de página completa: la de página completa dispara un «resize», que podría
  cerrar la lista.
- **Leer con el mismo JavaScript que elige, que con sus argumentos en una lista pulsa solo con la marca true** (ONE,
  MSC, HYUNDAI y COSCO): una lectura
  escrita aparte podría ver otra lista que la del clic, y una marca que pulse si falta convierte una lectura olvidadiza
  en un clic.
- **El aviso compara el texto de cada sugerencia; en ONE, sin su etiqueta, su clase ni su posición:** la clase se lee
  después del clic y la posición puede moverse, y con la descripción entera el aviso saldría con la misma sugerencia.
- **CMA, con su modo en el nombre:** cada intento vuelve a elegir, y sin el modo el segundo taparía al primero.
- **`_mk_ciudad` devuelve la sugerencia y lo que quedó en el campo:** el motivo de SIN-CUPO lo dice; con el `bool` de
  antes no había qué decir, y con la sugerencia sola afirmaba que quedó.
- **El control del censo, por tandas:** una sola línea con todas las pruebas ya no cabe en Windows.
- **La regla de MAERSK no se escribe sin reconocer el país** como decidas (pregunta 1): una posición no es un país.

## Universo y cobertura (pieza 3)

- **Las elecciones medidas:** 28, el origen y el destino de las 14 reservas de MAERSK de `logs/` (23 carpetas, 14
  bloques de MAERSK, 0 descartados), de 3 textos de celda. La unidad en que la regla decide es el texto de la celda con
  su lista de sugerencias: 3 textos no es una muestra de las celdas que puede traer la planilla.
- **Las listas de sugerencias:** 0 guardadas en 93 HTML de MAERSK; de las otras cinco, no las busqué. Por eso, si cada
  elegida era la única de su lista con la forma de la regla no se puede medir.
- **El código:** 7 ayudantes y 16 llamadas de origen y de destino, más 2 de otros campos; 182 llamadas a clic o tecla.
- **Las pruebas** corren con páginas falsas y JavaScript en Node, no en el portal: que la lista siga abierta durante la
  captura, cuánto tarda la evidencia y cómo la muestra cada portal no están medidos.

## Defectos de instrumento cazados (pieza 4)

1. **El censo completo se cayó a los 2 minutos**, sin resultado: su control no cabía en una línea de comando de Windows
   (arriba, el punto 4). Los gates, filtrados, no podían verlo. Lo arregla el commit 3, y `largo_control.py` lo mide.
2. **Una mutación no mordía:** en el primer precenso, `sug-one-lee-pulsando` no tumbó su prueba (46 de 47 pares). En
   ONE, el JavaScript que pulsa devuelve «CLICK[] CANDS[]» aunque no haya lista, un texto que no está vacío; con la
   mutación, la evidencia se tomaba antes de que la lista apareciera, y la página falsa no anotaba si la lista estaba a
   la vista. Desde entonces, cada captura lo anota.
3. **El control de `clics_por_funcion.py` abortó:** esperaba 2 en `_cma_puerto` y hay 3, porque la sonda cuenta también
   `.press(` y ahí está la tecla Tab. Corregí el valor esperado, no la sonda.
4. **`paises_en_el_codigo.py` medía HEAD, que se mueve con cada commit:** después del commit 1 daba 16 lugares con
   CHILE en vez de 15, porque un comentario nuevo de `_JS_COSCO_AUTO_PICK` dice «preferir Chile». Ahora mide la
   revisión que se le da, por defecto la base, y da 15. Lo mismo hace ahora `clics_por_funcion.py`.
5. **`paises_en_el_codigo.py` cuenta de más:** busca sin distinguir mayúsculas, y así «USA» calza con el verbo «usa» (11
   de sus 13 lugares, en comentarios, docstrings y textos), y «GEORGIA» es una tipografía. La conclusión no cambia; el
   informe dice cuáles son.
6. **Pasé código con barras invertidas por la herramienta Bash** (un «heredoc» que agregaba a `aplicar_c4.py` la
   mutación reanclada), y la herramienta volvió `\\n` en `\n`: el ancla ya no habría calzado. Lo vi al leer el archivo
   antes de aplicarlo, y lo reescribí con Edit y cadenas crudas. El catálogo del entorno lo advierte.
7. **En un aviso de la sesión dije «siete ayudantes y catorce llamadas»:** son 16 llamadas, porque CMA tiene 6 (el
   origen, 3 destinos y 2 lugares de entrega, uno por modo).
8. **Usé `sort` en Git Bash**, que Defender bloquea (también lo dice el catálogo): esa línea no dio nada, y la repetí
   sin él.
9. **`paises_en_el_codigo.py` leía `logs/` sin declararlo** (lo vio la revisión de este informe): importaba la sonda
   del encargo 40, que al importarse recorre los `log.txt` con la salida tapada, y si su control no pasaba, abortaba en
   silencio. La presenté como una sonda del código. Ahora lee la lista con `ast`, sin ejecutarla, y da la misma salida.
10. **«27 de 28 calzan» no medía la regla entera** (la revisión de este informe, A1): la sonda mira la forma de la
    elegida, y la regla pide además que sea la única de su lista. Lo presenté como si la midiera.
11. **Di una causa sin medirla:** atribuí las sandboxes que quedan en `%TEMP%` a pruebas que el censo cortó por tiempo,
    y explica pocas: en las 699 salidas de censo del scratchpad, solo un censo filtrado del encargo 36 trae tiempos
    agotados, 4 (la revisión de este informe, M2; pregunta 6).
12. **Una sonda de esta revisión imprimió en mi terminal un código de contrato:** para ver dónde está «USA» en el
    código, imprimí el contexto de cada coincidencia, y una trae el código de un contrato de ONE que está en el
    programa. No va a ningún archivo ni a este informe.
13. **Detener el censo desde la sesión no cerró sus procesos:** el Python del corredor y dos bash de `censo.sh`
    siguieron vivos. Los cerré por su número de proceso, después de comprobar su línea de comando, y borré su carpeta de
    trabajo.
14. **Corregí de más, dos veces** (la segunda revisión): al corregir esa causa escribí que en los censos no hubo ningún
    tiempo agotado, y en ese del encargo 36 hubo 4; y di por reemplazadas siete de las ocho mutaciones que quitó el
    commit 4, y eran seis. Las dos sin reemplazo vuelven en los commits 5 y 6.

## Premisas del encargo contrastadas (pieza 5)

- **Se cumplen:** que `_mk_ciudad` pulsa la primera sugerencia que trae los 5 primeros caracteres de la ciudad (con un
  matiz: la primera con «container yard», si hay, y ninguna lo trajo); que el 29-09 eligió un destino con una palabra de
  más en medio; y que las sugerencias elegidas tienen la forma de la regla salvo ese destino (27 de 28 elecciones, con A
  y con B). Que cada una fuera la única de su lista con esa forma no se puede medir: 0 listas guardadas.
- **Matiz de «el origen y el destino que quedaron elegidos»:** el programa sabe que una sugerencia quedó por lo que ya
  comprobaba, los 4 primeros caracteres en el campo, y lo tecleado también los trae (lo vio la revisión). Por eso el
  motivo dice también lo que quedó en el campo, cuando difiere. Que el campo calce con la sugerencia entera es parte de
  la regla que quedó en FRENO.
- **Matiz de «con el mecanismo de evidencia existente»:** en ONE, MSC, HYUNDAI y COSCO, guardar la lista antes de elegir
  pedía saber que la lista está sin pulsar, y su JavaScript pulsaba al elegir: ahora, con sus argumentos en una lista,
  pulsa solo con la marca true. La
  evidencia es la de siempre, y retrasa el clic lo que tarda en guardarse.
- **Ninguna premisa quedó refutada.** La segunda condición de tu FRENA SI se cumple con lo medido (el texto de las
  sugerencias; si MAERSK trae el país aparte en su HTML, no está medido). La primera no se puede descartar ni afirmar
  sin las listas: la única elección cuya forma no calza es la que ya nombras.

## Residual (pieza 6)

| Qué | Por qué queda | Se reabre si |
|---|---|---|
| La regla de MAERSK para el origen y el destino | FRENO: con lo medido, el país del final no se reconoce sin una lista que no está en el código | decides cómo reconocerlo (pregunta 1) |
| Si la elegida era la única de su lista con la forma de la regla | 0 listas guardadas | una corrida de MAERSK deja `mk_f<fila>_origen.html` y `_destino.html` (pregunta 1) |
| El control del campo de `_mk_ciudad`: los 4 primeros caracteres, y sin ellos la reserva sigue | es parte de esa regla | ídem |
| La regla de elección de ONE, MSC, COSCO, HYUNDAI y CMA | el encargo no la cambia | decides si la regla de MAERSK las alcanza (pregunta 2) |
| Sin sugerencia, HYUNDAI, MAERSK, el destino de COSCO y el lugar de entrega de CMA no dejan nada | tu decisión dice «antes de elegir» | pregunta 3 |
| El motivo de SIN-CUPO toma lo que quedó al elegir, no al buscar; y la evidencia retrasa el clic | lo avisa, pero la decisión es tuya | pregunta 4 |
| Con la celda del puerto o del destino vacía, cuatro navieras pulsan a ciegas antes de la guarda | ya existía y es otro encargo | pregunta 5 |
| 1408 sandboxes `aquashield_red_*` en `%TEMP%` (1,15 GB), y la fuga que las deja | no son de este encargo, y su causa está medida a medias | pregunta 6 |
| Si la lista sigue abierta durante la captura (si se cierra, cada ayudante sigue su camino sin sugerencia: punto 2), y cuánto tarda la evidencia | sin medir en el portal | una captura sale sin la lista, una fila queda NO ENVIADA ahí, o la reserva se vuelve lenta |
| El aviso de ONE compara los primeros 45 caracteres del texto, y su JavaScript acepta sugerencias de hasta 55: dos iguales en sus primeros 45 ya no avisan (antes las separaba la posición). Y el texto se lee después del clic, también en MSC, HYUNDAI y COSCO: si el portal lo cambia al elegirla, el aviso sale con la misma sugerencia | es el texto que da cada JavaScript | un aviso sale con la misma sugerencia, o dos sugerencias comparten sus primeros 45 caracteres |
| `por_tandas`, del control del censo, no tiene prueba ni mutación propia | si falla, el censo se cae con WinError 206, y se ve; su verificación interna pide que las tandas sean las pruebas elegidas | se toca el corredor |
| La prueba del puerto de carga de COSCO (`test_puerto_de_carga_sin_sugerencia_corta`) pasa ahora por la evidencia con un marco falso que no captura: anota «evidencia incompleta» y no la vigila | la vigila `TestListaDeSugerencias` | se toca ese marco falso |
| La línea del selector de MSC, de 157 caracteres | ya pasaba de 120; ahora va en la variable `js` | se toca ese JavaScript |

El residual del encargo 40 sigue igual, salvo su fila del destino y el origen de MAERSK, que sigue aquí.

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v14**, y las reglas propias del módulo, las de su `CLAUDE.md`. No chocaron entre sí.
- **Frenar cuando la decisión es de negocio:** cómo reconocer un país es tuyo; no elegí entre la lista, la última coma
  o medir primero (pregunta 1), y lo demás del encargo, que no depende de eso, siguió. Lo mismo con lo que la revisión
  dejó fuera de tu decisión literal (preguntas 3 a 5).
- **Control positivo que aborta:** cada sonda trae el suyo. El de `clics_por_funcion.py` abortó una vez, y el defecto
  era el valor esperado (pieza 4, 3).
- **Todo salto silencioso lleva contador:** `formas.py` cuenta carpetas sin `log.txt`, bloques sin cabecera, líneas que
  faltan y «sin sugerencia» (todos en 0); `paises_en_el_codigo.py`, las líneas en base64 que salta (6).
- **Re-medir contra HEAD antes de diseñar:** lo que traía el informe del encargo 40 (las 14 reservas, 0 listas
  guardadas) lo volví a medir con sondas nuevas, sobre `logs/` de hoy.
- **La unidad de la medición la fija el sujeto:** la regla decide por el texto de la celda con su lista de sugerencias:
  28 elecciones de 3 textos, no 14 reservas ni 6 filas.
- **El negativo tiene que morder, y un negativo vacuo delata un caso incompleto:** cada prueba nueva trae sus
  mutaciones (72 del encargo, en 86 pares). El precenso en una copia, antes de cada gate salvo el del commit 3, cazó
  una que no mordía (pieza 4, 2), y la revisión de código vio que tres defectos inyectados pasaban las pruebas (M4): en
  los dos casos faltaba algo en la página falsa, no en el assert. Las dos revisiones de este informe vieron que el
  commit 4 quitó dos mutaciones sin reemplazo: vuelven en los commits 5 y 6.
- **El censo de guardianes:** completo, sobre el último commit que cambia el programa, `e3e0a76`, con su control
  arreglado (pieza 4, 1): 1764 pares, y todos muerden. El commit 6 no lo repite: solo agrega una mutación, verificada en
  su gate, y una aserción al final de una prueba (la red y el gate, arriba).
- **Un gate en cero prueba contención, no correctitud:** el efecto lo prueban las pruebas funcionales con la página
  falsa (la evidencia antes del clic, con la lista a la vista, una vez, y nada entre medio) y el JavaScript corrido en
  Node.
- **Fuente única:** la lectura sin pulsar es el mismo JavaScript que elige, con una marca; no una copia de su filtro.
- **Cada reemplazo afirma su viejo una vez, la escritura es atómica y el EOL se preserva:** los `aplicar_*.py` asertan
  cada ancla y escriben en binario, LF; cada commit sale sin CR, y `anclas.py` verifica las anclas de todas las
  mutaciones. La escritura es atómica desde el commit 5 (un temporal y `os.replace`); hasta el commit 4, `write_bytes`,
  que trunca al abrir, después de validar todas las anclas en memoria (lo vio la revisión de este informe).
- **El cambio y su guardián, en la misma operación:** cada commit trae su código, sus pruebas y sus mutaciones; el del
  censo (commit 3) trae su verificación adentro, que las tandas sean las pruebas elegidas, pero ninguna prueba ni
  mutación para su límite (residual).
- **El residual se declara, y las premisas se contrastan:** piezas 5 y 6.
- **Todo registro es una hipótesis hasta que se contrasta:** también lo que escribí yo. La causa que di de las
  sandboxes, sin medirla, explica pocas; una sonda que presenté como del código leía `logs/`; y dos correcciones
  corrigieron de más (pieza 4, 9, 11 y 14).
- **Del módulo:** el candado no se toca y `test_candado` no cambia; antes de la guarda, ni clics a ciegas nuevos ni
  clics nuevos (182 antes y después; los de la celda vacía, pregunta 5, ya existían); la evidencia solo lee y nunca
  corta; las pruebas cargan la copia de `soporte.cargar()`, nunca el programa de la raíz, y nunca usan el puerto 8765;
  la sonda de secretos antes de cada commit; los datos de `logs/`, solo en lectura y sin imprimirlos; ninguna captura
  mirada.

## Entregable (pieza 8)

- Este informe, `CICLO-origen-y-destino.md`, y `CLAUDE.md` al día, en el commit de documentación.
- La forma de los dos, medida con `revisar_informe.py`: los bytes (sin CR, NUL, BOM ni caracteres invisibles), las
  líneas de prosa de más de 120, los códigos partidos entre dos líneas, el voseo y las marcas sin llenar: en los dos, 0
  de cada cosa.
- Lo revisaron dos agentes contra sus fuentes (abajo). No lo miré renderizado: la pieza es opcional mientras R22 sea
  candidata.

## Las revisiones

**La revisión de código** (un agente, de solo lectura, sobre los commits 1 y 2, leídos con `git archive` en una carpeta
aparte): 0 críticos, 0 altos, 4 medios y 9 bajos. Corrió la suite completa sobre `e0924e6` (520, en verde) y el censo
filtrado de 64 mutaciones en 74 pares, en tres filtros (43, 16 y 5 mutaciones), y todas muerden (sus salidas, en
`rev41/censo_*.txt` del scratchpad). El commit 4 corrige M3, M4 y siete bajos, y mitiga M1 y M2:
- **M1, la evidencia retrasa el clic:** mientras guarda la captura y el HTML, la lista puede cambiar, y el clic de
  después elige de la nueva; lo reprodujo con la página falsa. La regla no cambia, pero la evidencia puede no ser la
  lista de la que eligió. Ahora `_avisar_lista_distinta` lo avisa: compara la que pulsaría al dejar la evidencia con
  la que pulsó. Si prefieres que la evidencia no retrase el clic, es tuyo (pregunta 4).
- **M2, «quedó» no prueba que la sugerencia se eligió:** si el clic no la toma, el campo sigue con lo tecleado, que
  también trae los 4 primeros caracteres, y el motivo decía la sugerencia como si hubiera quedado. Ahora `_mk_ciudad`
  devuelve también lo que quedó en el campo, y el motivo lo dice cuando difiere. Comprobar de verdad que quedó es
  parte de la regla en FRENO.
- **M3, la lista que aparece entre la lectura y el clic:** ONE, MSC, HYUNDAI y COSCO pulsaban sin evidencia y sin
  aviso. Ahora lo avisa `_avisar_lista_distinta`.
- **M4, las pruebas no veían esperas, teclas ni clics de más:** con una espera antes de la evidencia de MSC, un Escape
  antes de la de CMA o un clic en otro elemento antes de la de HYUNDAI, las 291 pruebas de `test_clics`, `test_candado`
  y `test_evidencia` seguían pasando. Ahora la página falsa anota el clic en el campo, cada espera, cada tecla y
  cualquier otro clic, y las pruebas piden la secuencia entera; esas tres, y otras, son mutaciones.
- **B1:** la página falsa de COSCO era su propio marco; ahora la lista va en un marco aparte, que no sabe capturar.
  **B2:** la prueba de los nombres no veía un origen y un destino cruzados; ahora compara con la etiqueta de cada
  llamada. **B3:** COSCO no dejaba la lista de su segundo intento; ahora la deja, con `_reintento`. **B4:** la marca de
  solo leer dependía de quien llamaba; ahora la pone `_sugerencia_sin_pulsar`, y el JavaScript, con sus argumentos en
  una lista, pulsa solo con la marca true. **B6:** «sin una sugerencia elegida» pintaba de verde la línea de SIN-CUPO en
  el registro del panel; ahora no dice «elegida», y una prueba corre la función `clase` del panel. **B7:** el motivo se
  probaba solo como texto del código; ahora lo arma `_mk_motivo_sin_cupo`, que se prueba entero. **B8:** docstrings que
  afirmaban de más; ONE no anotaba cuál pulsó.
- **Dos bajos quedan para ti, B5 y B9:** si la regla no encuentra ninguna sugerencia, HYUNDAI, MAERSK y el lugar de
  entrega de CMA no dejan la lista, y el destino de COSCO tampoco, que la revisión no nombró: `reservar_cosco` no mira
  lo que devuelve su ayudante (pregunta 3). Y el motivo toma el origen y el destino al elegirlos, no al buscar
  (pregunta 4).
- **Fuera del encargo, y grave** (pregunta 5): con la celda del puerto de carga o del destino vacía, ONE, MSC, HYUNDAI y
  el destino de COSCO pulsan a ciegas antes de la guarda: el texto vacío calza con todo, y el revisor lo reprodujo en
  Node con un enlace «Inicio» arriba. `leer_filas` deja pasar una fila con nave y sin puerto de carga, y MAERSK y CMA
  probablemente hagan lo mismo (el prefijo vacío calza con todo). No lo toqué.

**La revisión de este informe** (un agente, de solo lectura, sin nada pesado mientras corría el censo): 1 alto, 5
medios y 11 bajos. Verifiqué cada uno antes de corregirlo, y todos se sostienen:
- **A1, «27 de 28 calzan» no medía la regla entera:** la regla pide la única sugerencia con esa forma, y la sonda mira
  solo la elegida. Con 0 listas guardadas, que fuera la única no se puede medir, así que tu primera condición del FRENA
  SI no se puede descartar. Lo corregí en el resumen, lo medido, las premisas, la pregunta 1, el residual y `CLAUDE.md`.
- **M1:** la segunda condición se cumple con lo medido, no en absoluto: si MAERSK trae el país aparte en su HTML, no
  está medido. La pregunta 1 suma dos caminos, el país en la celda y una librería de países.
- **M2:** la causa que di de las sandboxes no estaba medida: ahora la pregunta 6 dice lo medido.
- **M3:** `paises_en_el_codigo.py` leía `logs/` sin declararlo (pieza 4, 9). La revisión la corrió creyéndola de solo
  código, como yo la presenté; no imprimió ningún dato.
- **M4:** en ONE, el aviso de la lista que cambió podía salir con la misma sugerencia. Lo corrige el commit 5.
- **M5:** `CLAUDE.md` decía «antes de la guarda no hay clics a ciegas» sin la excepción que este ciclo encontró, la de
  la celda vacía (pregunta 5): ahora la dice.
- **Los bajos:**
  - B1: faltaba decir que el commit 3 no tuvo precenso.
  - B2: qué eran las 64 mutaciones del censo de la revisión de código.
  - B3: dónde está «USA» en el código.
  - B4: cuándo pulsa el JavaScript, también en su docstring (commit 5).
  - B5: las mutaciones y las pruebas que el commit 4 quitó o cambió; una volvió en el commit 5.
  - B6: la escritura atómica, y el límite de `por_tandas`, que queda en el residual.
  - B7: números sin su comando; dos sondas nuevas y dos arregladas.
  - B8: qué pasa si la lista se cierra durante la evidencia.
  - B9: qué corrigió y qué mitigó el commit 4.
  - B10: tres frases ambiguas.
  - B11: `CLAUDE.md` vuelve a decir cómo eligen las otras cinco.

**La segunda revisión** (otro agente, de solo lectura, sobre el informe corregido, el commit 5 y el `CLAUDE.md` nuevo,
mientras corría el censo): 0 altos, 3 medios y 8 bajos. El commit 5 hace lo que dice, y sus mutaciones muerden. Lo
demás lo verifiqué y lo corregí:
- **M1:** qué pasa si la lista se cierra durante la evidencia estaba mal: no quedan NO ENVIADA ONE, MSC y CMA, sino que
  cada ayudante sigue su camino sin sugerencia, y MAERSK y CMA esperan antes hasta 30 s (punto 2).
- **M2:** corregí de más la causa de las sandboxes: un censo filtrado del encargo 36 sí tuvo 4 tiempos agotados.
- **M3:** el commit 4 había quitado sin reemplazo también `sug-js-one-texto-solo-no-pulsa`: vuelve en el commit 6.
- **Los bajos:** la suite tardó de 5 a 11 min, no de 7 a 11; la cuenta de «USA» y dónde está Chile en el código; el
  censo de la revisión de código, sin la cuenta que no cerraba; las salidas de las sondas, guardadas otra vez; dos
  limitaciones del commit 5 (residual); cinco frases ambiguas, dos en `CLAUDE.md`; la hora de la medición de las
  sandboxes; y la prueba nueva pide ahora que la página falsa no vea nada inesperado (commit 6).
