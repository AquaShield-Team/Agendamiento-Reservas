# CICLO · MAERSK elige el origen y el destino exactos y no cuenta como empate las tarjetas idénticas; y los tres ajustes de la fila sin ruta

**Módulo:** Agendamiento Reservas · **Encargo 43** · **Fecha:** 2026-10-01 · **Método:** skill `metodo-ciclo` v14 ·
**Commits** (locales; el repo no tiene remoto, así que no hay push que entregar):
- `41e5bf0`: MAERSK elige el origen y el destino con tu regla, comprueba el campo y, si no, corta;
- `a876c05`: las tarjetas de salida de MAERSK con el HTML idéntico cuentan como una sola;
- `dde926e`: el panel marca la fila sin puerto de carga o sin destino antes de correr;
- `82a22f4`: «CL» solo en el puerto de carga cuenta como el país;
- `b055c94`: «-» en el destino final es la celda vacía;
- `6055965`: lo que encontró la revisión de código (la lista quieta, el campo comparado como la regla y el prefijo);
- `c233b63`: los comentarios que el commit 6 dejó viejos (revisión del informe);
- y el de este informe, con `CLAUDE.md` al día.

**Base: `C:\dev\Agendamiento Reservas` @ `27b5fe3` · árbol limpio** (pieza 9). Lo medido sale de los `log.txt` y el HTML
guardados en `logs/` (las 4 listas de sugerencias del 30-09, las 8 listas de salidas de MAERSK y los 97 bloques de
reserva) y del código de los commits. En `logs/` no hay corridas después de las del encargo 42: son 26 carpetas, y la
última corrida es la del 30-09 a las 15:31.

> Datos reales solo en lectura. Las sondas leen los `log.txt` y el HTML en su lugar, sin copiarlos, e imprimen formas,
> cuentas, fechas y booleanos: en este informe no van nombres de naves, viajes, puertos, países de una fila, partes,
> códigos ni números de reserva. El único país que nombro es Chile, que ya está en el código. No se miró ninguna
> captura.

**Resumen.**
- **MAERSK elige el origen y el destino con tu regla:** entre las sugerencias Container Yard, la única cuya parte antes
  de la primera coma, sin lo que va entre paréntesis, es lo escrito. Después comprueba que el campo quedó con el texto
  entero de esa sugerencia. Si no hay una sola, o el campo no calza, vuelve a escribir una vez, como antes, y si
  tampoco, la fila queda NO ENVIADA con el motivo, la captura y el HTML.
- **Tu FRENA SI 1 no se cumple:** con el código de los commits 1 y 6, en las 4 listas del 30-09 la regla elige la
  sugerencia que el informe del encargo 42 da por correcta, también el destino de las 15:21 (el del 27-09, que encontró
  la nave).
- **Las tarjetas de salida con el HTML idéntico cuentan como una sola,** y se pulsa el «Book» de la primera. El HTML
  entero, con sus raíces shadow, se arma igual que en la evidencia. En las 8 listas guardadas da los mismos 12 grupos
  que midió el encargo 42, y la elección cambia solo a las 15:31: del empate, a esa salida.
- **El panel marca antes de correr la fila sin puerto de carga o sin destino,** en la celda que le falta, y la cuenta
  aparte, como la fila sin nave. **«CL» solo en el puerto de carga cuenta como el país,** igual que «CHILE». **«-» en el
  destino final es la celda vacía:** el destino pasa a ser el original.
- **Tu FRENA SI 2 no se cumple, con lo que se puede medir:** de las 66 reservas de `logs/` que llegaron a la guarda,
  ninguna cambia por «CL», por «-» ni por las tarjetas idénticas. Las 6 de MAERSK pulsaron un origen y un destino con la
  forma de tu regla, y en la lista del origen del 30-09, que trae lo mismo escrito, la regla elige el que pulsaron. Lo
  que no se puede medir, porque sus listas no se guardaron y su `log.txt` no lo anota: si ese día cada una era la única
  Container Yard con esa forma, en el origen y en el destino, y si el campo quedó con ella (residual).
- **Sin clics nuevos** (182 antes y después), y `test_candado` no cambia. La red queda en 547 pruebas y 1628 mutaciones
  en 1959 pares (eran 537, 1586 y 1911), y en el censo completo sobre `c233b63` muerden todos.
- **Nada de esto se probó en el portal.**

## Veredicto del PASO 0, por parte del encargo

| Parte | Veredicto | Qué quedó |
|---|---|---|
| MAERSK: el origen y el destino con tu regla, el campo comprobado y, si no, NO ENVIADA | **CICLO** | `41e5bf0` |
| MAERSK: las tarjetas con el HTML idéntico, una sola salida | **CICLO** | `a876c05` |
| El panel marca la fila sin ruta antes de correr | **CICLO** | `dde926e` |
| «CL» solo en el puerto de carga, como el país | **CICLO** | `82a22f4` |
| «-» en el destino final, como la celda vacía | **CICLO** | `b055c94` |
| Lo que encontró la revisión de código (la lista quieta, el campo, el prefijo y las pruebas que faltaban) | **CICLO** | `6055965`; el resto, residual y preguntas |
| Lo que encontró en el código la revisión del informe (dos comentarios viejos) | **CICLO** | `c233b63`; lo demás, en este informe |
| Tu FRENA SI 1 | **NOTA:** no se cumple (la regla elige la correcta en las 4 listas) | — |
| Tu FRENA SI 2 | **NOTA:** no se cumple con lo medido (0 de 66); de 6 reservas de MAERSK no se pueden medir sus listas ni su campo | Residual |
| Sin clics nuevos; `test_candado` no cambia | **NOTA:** se cumple (182 antes y después) | Sin cambios |

## Parte 1 · MAERSK elige el origen y el destino exactos

### Cómo quedó

- **`_mk_ciudad` pulsa, entre las sugerencias Container Yard, la única cuya parte antes de la primera coma, sin lo que
  va entre paréntesis, es lo escrito** (`_mk_las_exactas`, `_mk_base`, `_mk_plano`). Las sugerencias que mira son las de
  antes: las que traen los 5 primeros caracteres ASCII de lo escrito (`_mk_sugerencias`), ahora tomados con los espacios
  de a uno (commit 6). El tipo de lugar, «Container Yard» o «Store Door», está en la raíz shadow de cada opción: lo ve
  el filtro de Playwright y no `text_content`, así que la Store Door con el mismo texto no cuenta.
- **Decide con la lista quieta:** con dos lecturas iguales seguidas de sus Container Yard, porque la lista puede llegar
  de a poco; si no se queda quieta, con la última (revisión de código, commit 6).
- **Después comprueba que el campo quedó con el texto entero de esa sugerencia,** comparado como la regla (sin
  mayúsculas, tildes ni espacios de más) y leído hasta 5 veces en 2 segundos, por si se asienta tarde (commit 6). Hasta
  ahora bastaba que trajera los 4 primeros caracteres de lo escrito, y lo tecleado también los trae.
- **Si no hay una sola, o el campo no calza, vuelve a escribir la ciudad una vez, como antes, y si tampoco, corta él
  mismo:** la reserva queda NO ENVIADA, con la captura `mk_f<fila>_sin_objetivo` y su HTML (lo hace el decorador de
  siempre). El motivo dice qué buscaba:
  - sin una sola: «Origen de MAERSK: no encontré una sola sugerencia Container Yard que diga «…» antes de su primera
    coma (sin lo que va entre paréntesis): hay 2» (o «no hay ninguna»);
  - el campo no calza: «… no encontré la sugerencia «…» en el campo, que quedó con «…»» (o «que quedó vacío»);
  - sin lista: «… no encontré una sugerencia para «…»»; y si el campo no responde, «… el campo donde escribir «…»»;
  - con dos vueltas, el de la última en que apareció la lista: si en la primera había 2 y en la segunda la lista no
    apareció, dice «hay 2», y la evidencia `_reintento` no trae lista.
- **Elige de la lista que dejó en la evidencia** (`mk_f<fila>_origen` y `_destino`): si al dejarla no había una sola, en
  esa vuelta no pulsa, aunque mientras la guardaba apareciera; vuelve a escribir y elige de la segunda, que queda con
  `_reintento`. Si pulsa, la lista que dejó tenía una sola con la forma de la regla; si la lista cambió mientras la
  guardaba, `_avisar_lista_distinta` lo avisa después del clic, como en las otras navieras.
- `log.txt` anota, cuando no hay una sola, cuántas Container Yard dicen lo escrito y de cuántas.
- `reservar_maersk` ya no corta con lo que devuelve `_mk_ciudad` (el corte del encargo 42): el corte viene de adentro,
  con su motivo. Sin clics nuevos: el clic en la sugerencia es el mismo, sobre otra elegida.

**Cómo leí «igual a lo escrito».** Sin distinguir mayúsculas (el programa escribe en mayúsculas y el portal muestra la
sugerencia en minúsculas y mayúsculas), sin distinguir tildes y con los espacios de a uno. Los signos sí cuentan:
«PUERTO-ALFA» no es «PUERTO ALFA». Lo que va entre paréntesis se quita solo de la sugerencia, como dijiste: si lo
escrito trae un paréntesis cerrado («ALFA (NORTE)»), en la práctica no calza con ninguna, y la fila queda NO ENVIADA. Lo
de las tildes es mío (pregunta 1).

**Otras tres lecturas mías, que tu decisión no dice:** antes de cortar vuelve a escribir la ciudad una vez, como ya
hacía; el campo se compara como la regla, sin mayúsculas, tildes ni espacios de más (con el texto exacto, un portal que
dejara el campo con otras mayúsculas cortaría todas las reservas de MAERSK); y decide con la lista quieta. Si alguna no
te sirve, dímelo.

### Lo medido: tu FRENA SI 1 no se cumple

Corrí las funciones del programa, con el código del commit 1 y con el del 6 (el 7 solo cambia comentarios), sobre las 4
listas del 30-09, cargadas en un Chromium sin red y con el JavaScript de la página apagado (el HTML guardado trae sus
raíces shadow como plantillas, 370 en la lista del origen de las 15:21, y el navegador las vuelve raíces de verdad). La
correcta es la que da el informe del encargo 42: en los dos orígenes y en el destino de las 15:31, la que se pulsó (con
la que la búsqueda encontró la nave); en el destino de las 15:21, la que se pulsó el 27-09 con la misma celda y lo mismo
escrito, con la que la nave apareció.

| Lista | Container Yard con el prefijo | Con la forma de la regla | Elige | ¿La correcta? |
|---|---|---|---|---|
| Origen, 15:21 | 1 | 1 | la 1.ª de 34 (su Store Door gemela es la 28.ª) | sí |
| Destino, 15:21 | 2 | 1 | la 6.ª de 8, «ciudad, país» (la del 27-09) | sí |
| Origen, 15:31 | 1 | 1 | la 1.ª de 34 | sí |
| Destino, 15:31 | 1 | 1 | la 1.ª de 3, «palabra (palabra), país» | sí |

A las 15:21, la que pulsó el programa, «ciudad + 1 palabra, país», es la otra Container Yard: su parte antes de la coma
trae una palabra más, y la regla no la toma. Control que aborta, antes de las listas: una página sintética con dos
Container Yard que calzan da ninguna, y sin una de ellas, la otra.

**El campo.** En la única corrida que anota con qué quedó el campo (las 15:21, en su motivo de SIN-CUPO), quedó con el
texto exacto de la sugerencia pulsada, en el origen y en el destino. La línea «la sugerencia no quedó en el campo» no
aparece en ningún `log.txt` de `logs/`. Si en las demás corridas el campo quedó con el texto entero no está anotado.

### Las reservas guardadas (tu FRENA SI 2, la parte de MAERSK)

En `logs/` hay 16 reservas de MAERSK, con 32 elecciones (el origen y el destino de cada una). La sugerencia que pulsó
cada una (los 45 caracteres que anota `log.txt`, que en las 32 alcanzan a la primera coma) tiene la forma de la regla en
30. Las 2 que no son los dos destinos equivocados, el del 29-09 y el del 30-09 a las 15:21. Ninguna escribió letras
fuera de ASCII ni paréntesis, y ninguna sugerencia pulsada trae letras fuera de ASCII antes de su primera coma.

Llegaron a la guarda 6: las 5 del 21-09, que quedaron EMITIDA, y una del 24-09, REVISAR, que dejó la evidencia de la
guarda (`mk_f30_guarda`).
- **El origen:** escribieron lo mismo que en las listas del 30-09, y en esa lista la regla elige la que pulsaron. Su
  propia lista no se guardó, y la lista cambia entre corridas (con la misma celda, el destino del 27-09 y el del 29-09
  se eligieron distintos): si ese día era la única con esa forma tampoco se puede medir.
- **El destino** tiene la forma de la regla en las 6, pero su lista no se guardó (las listas se guardan desde el encargo
  41): si era la única Container Yard con esa forma no se puede medir. Si había otra, hoy quedarían NO ENVIADA en el
  destino. No veo cómo medirlo sin el portal; la primera corrida con ese destino guarda su lista.
- **El campo:** en esas corridas no está anotado con qué quedó (residual).

Con lo medido, ninguna cambiaría de estado; lo que no se puede medir queda en el residual.

**Lo que cambia, fuera de la guarda.** Con la regla, la corrida de las 15:21 habría elegido el destino del 27-09. Si con
él la búsqueda habría traído la nave no está probado: así fue el 27-09.

## Parte 2 · MAERSK no cuenta como empate las tarjetas idénticas

### Cómo quedó

- **`_JS_MK_SALIDAS`, cuando se le pide, dice de cada tarjeta de «Select sailing» cuál es la primera con su mismo HTML
  entero:** su etiqueta con sus atributos y su contenido con todas sus raíces shadow abiertas. La lectura de las raíces
  y la etiqueta de apertura son las de la evidencia: las dos usan ahora `_JS_HTML_ENTERO`, así que «HTML idéntico» es lo
  mismo en el programa y en la evidencia que se guarda. Lo que guarda la evidencia no cambia.
- **`_mk_elegir_nave` descarta las copias (`_mk_sin_repetidas`) antes de elegir la próxima salida,** y si la elegida
  venía repetida, pulsa el «Book» de la primera. `log.txt` lo anota: «4 tarjetas de la nave; 2 son copias de otra, con
  el HTML entero idéntico: cuentan como una sola salida (quedan 2)».
- **Si difieren en cualquier cosa, o el HTML de una no se pudo leer, cuentan aparte, y el empate sigue como hoy.**
- Las otras lecturas de la lista (la espera del desenlace y la cuenta al ampliar) no lo piden y no cambian.

### Lo medido

Con la lectura del programa, en un Chromium sin red, sobre las 8 listas de salidas guardadas en `logs/`:
- **Los grupos de tarjetas idénticas son los 12 del encargo 42,** en las mismas 7 listas: por «igual», por el texto
  entero y por el HTML entero armado aparte dan los mismos grupos. Cada tarjeta trae de 6 a 12 raíces shadow, y el HTML
  entero las incluye (control: dos tarjetas sintéticas que difieren solo dentro de su raíz shadow quedan aparte, y el
  `outerHTML` no las distingue).
- **Con la nave de cada reserva** (de la cabecera de su `log.txt`, sin el viaje, que la cabecera no trae), la elección
  cambia solo en la lista de las 15:31: antes, empate entre las 3 tarjetas de la nave; ahora, la primera de las 3 (la
  8.ª de 14). En las otras 7, la nave no estaba o sus tarjetas no tenían copias, y la elección es la misma.

**Tu FRENA SI 2, esta parte:** descartar copias idénticas solo puede deshacer un empate. Nunca crea uno, y si una salida
ya era la única elegible, lo sigue siendo: una copia suya tendría su misma fecha y su mismo tránsito, y habría empatado
con ella; y las copias de otras salidas no cambian ni la fecha más próxima ni el menor tránsito. Así que ninguna reserva
deja de llegar a la guarda por esto. De las 6 de MAERSK que llegaron, solo la del 24-09 guardó su lista (en la evidencia
de la guarda): 3 tarjetas, ninguna repetida.

**Lo que cambia, fuera de la guarda.** Con la regla, la corrida de las 15:31 habría pulsado el «Book» de esa salida y
seguido. Si el portal arma la misma reserva con cualquiera de las 3 tarjetas no está medido (residual).

## Parte 3 · Los tres ajustes de la fila sin ruta

### El panel marca la fila sin puerto de carga o sin destino antes de correr

- `/api/filas` trae, para cada fila con nave, `sin_puerto` o `sin_destino`, según `_falta_en_la_fila` (`_con_su_marca`).
  La fila sin nave, o MANUAL, no las lleva: su motivo es el de la nave, como al correr.
- El panel la marca en la celda que le falta («sin puerto de carga» o «sin destino», con el estilo de «sin nave») y la
  cuenta aparte, con su aviso: «N reserva(s) con nave no traen su puerto de carga o su destino: quedan NO ENVIADA, sin
  entrar al portal. Escríbelos en la planilla si quieres reservarlas.»
- Va marcada para correr, como la fila sin nave: así queda NO ENVIADA con su motivo en la planilla.

### «CL» solo en el puerto de carga cuenta como el país

La palabra del puerto de carga se pide sin «CHILE» ni «CL» en ninguna posición (`PAIS_DEL_PUERTO`): «CL», «CL CHILE»,
«CHILE CL», «Chile (CL)», «X CL» o «CL-CHILE» no traen el puerto. «PUERTO CL», «CLARO» o «PUERTO ALFA, CL» sí. Lo
apliqué en cualquier posición, como «CHILE», porque así es «igual que CHILE» en la regla del encargo 42; con «X CL», la
palabra sería «X», que tampoco es un puerto.

### «-» en el destino final es la celda vacía

Los dos lectores de la planilla, `leer_filas` (el panel) y `leer_reservas` (la consola), leen «-» en el destino final,
sin otra cosa y con o sin espacios, como la celda vacía (`_destino_final_de`), y el destino pasa a ser el original, como
ya hacían con la celda vacía. Así lo ven igual el panel, la regla de la fila y las seis navieras. Sin destino original,
la fila no trae destino. Otro texto, como «--» o «N/A», queda como viene (y no trae una palabra: sin destino).
`_falta_en_la_fila` no cambió: una fila armada de otra forma, con «-» en el final, sigue sin destino.

### Lo medido: tu FRENA SI 2, esta parte

En los 97 bloques de reserva de `logs/`, con las funciones de la copia con los cinco commits frente a las de la base
(`27b5fe3`): ninguno trae «CL» como palabra en el puerto de carga ni «-» en el destino final, y a ninguno le cambia lo
que le falta, ni a los 66 que llegaron a la guarda. El panel solo marca: no cambia el estado de nada.

## La red y el gate de cada commit

Cada commit pasó primero por una copia del repo (la suite entera y el censo de sus filtros: el precenso) y después por
la raíz (el gate: la suite entera y los mismos filtros). Los filtros toman las mutaciones nuevas o reancladas y las que
nombran una prueba que cambió. La sonda de secretos dio 0 en el ensayo y en lo que se commiteaba, en cada commit.

| Commit | Pruebas | Mutaciones (pares) | Gate: filtros del censo | Mutaciones en esos filtros (pares) |
|---|---|---|---|---|
| `27b5fe3` (base) | 537 | 1586 (1911) | — | — |
| `41e5bf0` (MAERSK: el origen y el destino) | 539 | 1598 (1929) | `TestListaDeSugerencias`, `TestSinSugerenciaNoSigue` y `test_la_forma_de_la_regla` | 146 (176) |
| `a876c05` (MAERSK: las tarjetas idénticas) | 541 | 1609 (1940) | `TestMaersk` y `test_el_javascript_trae_las_raices_shadow` | 137 (167) |
| `dde926e` (el panel y la fila sin ruta) | 543 | 1617 (1948) | `panel-` y `filas-` | 45 (46) |
| `82a22f4` («CL» en el puerto de carga) | 543 | 1618 (1949) | `test_falta_en_la_fila` | 17 (39) |
| `b055c94` («-» en el destino final) | 544 | 1623 (1954) | `guion-` | 8 (9) |
| `6055965` (lo de la revisión de código) | 547 | 1628 (1959) | `TestListaDeSugerencias` | 122 (148) |
| `c233b63` (los comentarios viejos) | 547 | 1628 (1959) | `mk-ruta` | 10 (11) |

En los siete gates, la suite entera pasó, con 0 cambios en los originales, y en el censo de sus filtros mordieron todos
los pares, con 0 tiempos agotados y 0 pruebas sin mutación; el del commit 2, la segunda vez (pieza 4, 8). Los filtros de
un mismo gate se pisan: la tabla da las mutaciones y los pares distintos (`gates_distintos.py`), y sumando cada filtro,
el commit 1 da 151 en 188 pares. Antes de cada gate, el precenso en la copia dio las mismas cifras; en el commit 6, sin
la mutación que volvió, que corrió aparte, en otra copia, y mordió. El commit 7 no tiene mutaciones nuevas ni pruebas
que cambien: su filtro, `mk-ruta`, toma las 10 `mk-ruta-*`, que anclan junto a lo que cambia (5 en `_mk_ciudad`, 2 en
`_mk_las_exactas` y 3 en `_mk_ruta_buscada`) y ninguna en las 6 líneas que cambia (`anclas_c7.py`); las 1628 anclan una
vez.

- **Commit 1:** 15 mutaciones nuevas, 7 reancladas al código nuevo de `_mk_ciudad` y `_mk_las_exactas`, y 3 quitadas:
  las dos de los cortes de `reservar_maersk`, que se fueron con ellos, y `mk-ruta-sin-el-campo`, que quedó equivalente
  (con el chequeo exacto, el campo siempre devolvía la sugerencia; volvió en el commit 6). Las páginas falsas de las
  sugerencias separan ahora el texto de la sugerencia de su tipo de lugar, como Playwright; y la sugerencia sintética
  trae la forma de la regla, para los siete ayudantes.
- **Commit 2:** 11 nuevas y 3 reancladas (la lista de tarjetas, el ayudante de la nave y la de la evidencia que hace
  clic, que ahora arma su HTML con `_JS_HTML_ENTERO`). El DOM falso de MAERSK en Node sabe su HTML entero, con su raíz
  shadow, y la página falsa de «Select sailing» trae «igual» solo si la lectura lo pide, como el JavaScript.
- **Commit 3:** 8 nuevas y 4 reancladas (las de las marcas de `/api/filas`, cuya línea del `return` ahora sigue en
  otra).
- **Commit 4:** 1 nueva y 1 reanclada (la de «CHILE» en cualquier posición).
- **Commit 5:** 5 nuevas.
- **Commit 6:** 5 nuevas y 1 reanclada (la que pedía que bastara lo tecleado, sobre la comparación nueva del campo). Una
  de las nuevas es `mk-ruta-sin-el-campo`: con el campo comparado como la regla, lo que quedó puede diferir de la
  sugerencia, y vuelve a morder. MAERSK espera una lectura más antes de decidir, así que sus secuencias en las pruebas
  de las sugerencias tienen una espera más; la página falsa sabe además de una lista que crece tarde y de un campo que
  se asienta tarde o con otra forma.
- **Commit 7:** solo comentarios: ninguna mutación nueva ni reanclada, y las 1628 anclan una vez.

**El censo completo.** Sobre `c233b63`, el último commit de código: 1628 mutaciones en 1959 pares, y todos muerden. Duró
77 minutos (de 14:13 a 15:30: unos 5 de control, 37 de preparación y 35 de pares), con 0 pruebas sin mutación, 0 tiempos
agotados del corredor, los originales sin cambios y ninguna suspensión: 0 eventos de Kernel-Power entre su inicio y su
fin, y la misma consulta encuentra los 18 de la tarde del 30-09, con sus 506 y 507. Una mordida trae «TimeoutExpired» en
su motivo: es la espera de la propia prueba (`previa-ociosa-no-se-apaga`), como en los censos de los encargos 41 y 42.
Antes lancé uno sobre `6055965` y lo detuve en su preparación, cuando la revisión del informe encontró los comentarios
que corrige el commit 7 (en «Las revisiones»): cerré sus 4 procesos (los dos del lanzador, el del corredor y el del
monitor) por su número, después de comprobar su línea de comando, y borré su carpeta de trabajo, de 793 entradas.

## Cómo probarlo

1. Abre `Iniciar AQUASHIELD.bat` con las tres llaves de emisión cerradas. Si el panel estaba abierto, ciérralo y vuelve
   a abrirlo: el programa se carga al arrancar.
2. **MAERSK:** corre la fila 10 de nuevo. En su carpeta de `logs\`, `mk_f10_origen` y `mk_f10_destino` son las listas de
   las que eligió (o `_reintento`, si volvió a escribir). Si no hay una sola sugerencia con la forma de tu regla, la
   fila queda NO ENVIADA en ese campo, con el motivo («… no encontré una sola sugerencia Container Yard que diga «…» …:
   hay 2», o «no hay ninguna») y `mk_f10_sin_objetivo`; y si encuentra la nave en tarjetas repetidas, `log.txt` dice «…
   es copia de otra…» o «… son copias de otra, con el HTML entero idéntico: cuentan como una sola salida».
3. **El panel:** en una copia de la planilla, deja una fila con nave y sin puerto de carga (vacío, «CHILE» o «CL») y
   otra con nave y sin destino. Al cargar la hoja, tienen que verse marcadas («sin puerto de carga», «sin destino») y
   con su aviso aparte, y al correrlas, quedar NO ENVIADA sin abrir el navegador si no hay otra fila de esa naviera.
4. **«-» en el destino final:** una fila con «-» en el destino final y el destino original lleno tiene que mostrar en el
   panel el destino original como su destino, y correr con él.

Avísame si una fila que trae su ruta queda NO ENVIADA en el origen o el destino de MAERSK: el motivo dice qué buscaba, y
`mk_f<fila>_origen` o `_destino`, qué mostraba el portal.

## Qué decides tú

1. **«Igual a lo escrito», sin distinguir tildes.** Comparo sin mayúsculas (el programa escribe en mayúsculas y el
   portal no), con los espacios de a uno y sin tildes: «PUERTO ÁLFA» escrito calza con «Puerto Alfa, …». Si quieres que
   las tildes cuenten, dímelo. En `logs/`, ni las 32 ciudades que escribió MAERSK ni las 32 sugerencias que pulsó traen
   letras fuera de ASCII antes de su primera coma, así que lo guardado no cambia con una u otra: en las 4 listas del
   30-09, la que elige la regla es una de esas pulsadas.
2. **El prefijo con que MAERSK espera su lista quita las letras con tilde y la ñ** (ya era así): con una de ellas entre
   la segunda y la quinta letra de la ciudad, la lista no se reconoce y la fila queda NO ENVIADA en ese campo («… una
   sugerencia para «…»»). ¿Lo cambio para que las pliegue («Ñ» como «N») en vez de quitarlas? En `logs/` no pasó nunca
   (ver la 1).
3. **COSCO y «CL» al final.** Una celda como «PUERTO CL» trae el puerto, y COSCO lo busca tal cual, con «CL»: al final
   solo quita «CHILE». ¿Quito también «CL» al final, como «CHILE»? En `logs/`, ninguna celda de puerto de carga trae
   «CL».
4. **Las 5 capturas del encargo 42 que el OCR no confirma** (`msc_f6_origen`, `msc_f6_destino`, `cosco_f8_origen`,
   `hmm_f9_origen` y `hmm_f9_destino`, de las 15:21 del 30-09): esa pregunta sigue abierta.

## Re-medir (pieza 1)

Las sondas son de solo lectura y no se versionan. Quedaron en el scratchpad de esta sesión
(`$env:TEMP\claude\<proyecto>\<sesión>\scratchpad\e43`), que puede limpiarse; sin ellas, estos números no se re-miden.
Cada una declara su universo y su control positivo, que aborta si no pasa, y su salida quedó en `salida_<sonda>.txt`
(solo formas, cuentas, fechas y booleanos). Las que leen `logs/` lo dicen. Cargan el programa con `programa.py`, que
copia su `AQUASHIELD.py` (de un commit o de una copia del repo) a una carpeta nueva del scratchpad y lo importa desde
ahí, sin `config.json` ni `perfiles/`.
- **`corridas_recientes.py`** (lee `logs/`): las carpetas por su fecha y hora, sin el resto del nombre; ninguna después
  de las 15:31 del 30-09. Control: la última corrida del encargo 42 está.
- **`campo_quedo.py`** (lee `logs/`): en cada `log.txt`, las líneas con la ruta de SIN-CUPO y cuántas dicen que el campo
  quedó con otra cosa, y las de «la sugerencia no quedó en el campo». Control: la corrida de las 15:21 tiene la suya.
  Cuenta las carpetas que lee y las que salta.
- **`dsd_prueba.py`** (lee una lista de `logs/`, en un Chromium sin red): que `set_content` convierte las raíces shadow
  declarativas del HTML guardado. Control: una página sintética.
- **`freno_mk.py`** (lee `logs/`, en un Chromium sin red), con `MODO=prototipo` o `MODO=programa COPIA=<copia>`: la
  regla de MAERSK sobre las 4 listas del 30-09 (tu FRENA SI 1) y la forma de las 32 elecciones de MAERSK de `logs/`.
  Controles: una lista sintética, y que las 4 listas estén.
- **`iguales_mk.py` e `iguales_programa.py`** (leen `logs/`, en un Chromium sin red): los grupos de tarjetas idénticas
  de las 8 listas de salidas por el texto, por el `outerHTML` y por el HTML entero, y la lectura y la elección del
  programa del commit 2 en cada una. Controles: tarjetas sintéticas que difieren solo dentro de su raíz shadow, y el
  grupo de 3 de las 15:31. Cuentan los HTML que leen y los que no traen tarjetas.
- **`freno_ruta.py`** (lee `logs/`), con `MODO=prototipo` o `MODO=programa COPIA=<copia>`: «CL» y «-» en los 97 bloques,
  y si a alguno le cambia lo que le falta frente a la regla de `27b5fe3`. Control: casos sintéticos. Cuenta las carpetas
  y los bloques que salta.
- **`espacios_mk.py`** (lee `logs/`): en lo que escribieron MAERSK y HYUNDAI, los espacios de más, las letras fuera de
  ASCII, los paréntesis y el prefijo. Control: una línea sintética con espacio doble. Cuenta las carpetas que lee y las
  que salta.
- **`anclas_c7.py`:** dónde anclan las mutaciones del filtro del gate del commit 7, y si alguna ancla en lo que cambió.
- **`tildes_pulsadas.py`** (lee `logs/`): en las 32 elecciones de MAERSK, las letras fuera de ASCII de lo escrito y de
  la sugerencia pulsada, antes de su primera coma. Control: la corrida de las 15:21, con sus 2 elecciones.
- **`largo_mk_ciudad.py <commit>…`:** las líneas de `_mk_ciudad` en cada commit, con `ast` sobre `git show`.
- `freno_mk.py`, `freno_ruta.py`, `iguales_programa.py` y `tildes_pulsadas.py` leen `logs/` con los lectores del encargo
  42 (`../e42/freno_guarda.py` y, en la primera y la última, `../e42/listas_mk.py`): sin esa carpeta no se re-miden.
- **`clics_por_funcion.py <árbol> <base>`:** las llamadas a clic y a tecla por función y constante (del encargo 41).
- **`ver.py <archivo> <desde> <hasta>`:** un tramo del código con los códigos tapados (del encargo 42).
- **Las herramientas del gate:** `copia.py`; `aplicar_c1.py` a `aplicar_c7.py`, con sus `_pruebas.py` y `_mutaciones.py`
  donde los hay, y `aplicar_docs43.py`, el de `CLAUDE.md` (cada viejo, exactamente una vez; escritura atómica, en
  binario y LF); `anclas.py` (las anclas de las mutaciones y las líneas nuevas de más de 120); y `precenso.sh`,
  `suite_y_precenso.sh`, `gate.sh`, `censo.sh` y `commit.sh`, los del encargo 42 con la ruta de este.
- **Las cuentas de la red:** `red_por_commit.py <commit>…` (pruebas, mutaciones y pares de cada commit, leídos con
  `git show`) y `gates_distintos.py` (las mutaciones y los pares distintos de cada gate, porque sus filtros se pisan;
  control: cada filtro da lo que imprimió su gate).
- **El informe:** `armar_e43.py` lo arma con sus partes y `valores_e43.json`, y lo reacomoda a 120 con `reacomodar.py`;
  `corregir_informe.py` le aplicó lo de su revisión, y `revisar_informe.py` (del encargo 41) mide su forma.

La red versionada, desde `C:\dev\Agendamiento Reservas`:
- `python tests/correr.py`: la suite;
- `python tests/correr.py --mutaciones --filtro <texto>`: el censo de un filtro (`TestListaDeSugerencias`, `TestMaersk`,
  `TestDestinoFinalConGuion`…);
- `python tests/correr.py --mutaciones`: el censo completo.

## NO retroceder (pieza 2)

- **MAERSK no vuelve a «la primera Container Yard o, si no hay, la primera».** Así eligió el 29-09 y el 30-09 un destino
  que no era el de la fila. Elige la única con la forma de tu regla, y si no hay una sola, corta.
- **El campo se comprueba con el texto entero de la sugerencia,** no con sus primeros caracteres: lo tecleado también
  los trae, y no prueba que la sugerencia haya quedado.
- **`_mk_ciudad` corta él mismo, con su motivo;** que vuelva a devolver `('', '')` deja al reservador sin saber por qué.
- **Pulsa solo si la lista que dejó en la evidencia tenía una sola con la forma de la regla:** si no, la evidencia
  podría no mostrar la lista con que decidió.
- **Las copias se reconocen por el HTML entero, con sus raíces shadow,** armado como la evidencia (`_JS_HTML_ENTERO`):
  no por el texto, que no ve los atributos ni lo que va dentro de las raíces, ni por el `outerHTML`, que no trae las
  raíces (el control sintético lo muestra). Y una tarjeta cuyo HTML no se pudo leer cuenta aparte.
- **Las marcas del panel salen de la regla del programa (`/api/filas`),** como la de la fila sin nave desde `f68ce6c`:
  el panel no decide por su cuenta.
- **«-» se lee en los dos lectores, con una sola función (`_destino_final_de`),** donde ya se completaba el destino
  vacío: no en cada naviera.

## Universo y cobertura (pieza 3)

| Medición | Universo | Cobertura | Descartados |
|---|---|---|---|
| La regla de MAERSK (FRENA SI 1) | Las 4 listas de sugerencias del 30-09 (2 orígenes y 2 destinos, 3 textos distintos) | 4 de 4 | 0 |
| La forma de lo elegido en MAERSK | Las 16 reservas de MAERSK de `logs/`, con 32 elecciones | 32 de 32 (las 32 traen la primera coma en los 45 caracteres que anota `log.txt`) | las 5 carpetas de inicio de sesión, que no son corridas de reservas (las cuenta `tildes_pulsadas.py`, que lee igual) |
| Las tarjetas idénticas | Los 15 `mk_f*.html` de `logs/` sin los `_marco`, 8 de ellos con tarjetas de salida | 8 de 8 | 7, sin tarjetas de salida |
| «CL» y «-» (FRENA SI 2) | Las 26 carpetas de `logs/`: 97 bloques de reserva con estado final, 66 en la guarda | 97 de 97 | las 5 carpetas de inicio de sesión, que no son corridas de reservas; 0 bloques sin estado final |
| El campo de MAERSK | Las líneas con la ruta de SIN-CUPO en los `log.txt` de las 26 carpetas de `logs/` | 1 corrida (las 15:21 del 30-09), con sus 2 campos | 0 |
| Las letras fuera de ASCII | Las 32 elecciones de MAERSK de `logs/`: lo escrito y la sugerencia pulsada, antes de su primera coma | 32 de 32 | las 5 carpetas de inicio de sesión, que no son corridas de reservas |
| Sin clics nuevos | Las funciones y constantes de nivel superior de `AQUASHIELD.py`, en la base y en el commit 6 (y en el 7) | 501 y 512 | 0 |

## Defectos de instrumento cazados (pieza 4)

1. **`freno_ruta.py`, con el código real, comparaba la regla nueva consigo misma:** «antes» salía del mismo programa que
   «ahora». Daba 0 cambios, pero ese 0 no medía nada. Ahora «antes» es la regla de `27b5fe3`; sigue en 0, y en los 97
   bloques no hay «CL» en el puerto ni «-» en el destino final, que es lo que hace imposible el cambio.
2. **`iguales_mk.py` miró al principio solo los `mk_f*_detenida.html`:** 7 listas. La octava del encargo 42 es la de la
   guarda del 24-09. La amplié a todos los `mk_f*.html`; y `iguales_programa.py` saltaba los HTML sin tarjetas sin
   contarlos (ahora: 15 leídos, 8 con tarjetas, 7 descartados).
3. **El primer chequeo de anclas compilaba el programa mutado de cada una de las 1586 mutaciones,** y en 20 minutos no
   había terminado. Lo detuve (comprobé su línea de comando antes de cerrarlo); ahora solo cuenta las anclas, y la
   compilación la hacen el precenso y el gate, que preparan cada mutación.
4. **Una navegación a un archivo local con la red cortada falla** (`net::ERR_FAILED`): la ruta que aborta las peticiones
   también la ataja. `set_content` convierte igual las raíces shadow declarativas (la sintética da 1 raíz; la lista del
   origen, 370), así que las sondas cargan el HTML así.
5. **Dos archivos del scratchpad escritos con un heredoc de Bash salieron mal:** uno no terminó («unexpected EOF») y el
   otro perdió las barras invertidas, porque la herramienta de Bash convierte `\\` en `\`. Los rehice con las
   herramientas de escritura. Ninguno era del repo.
6. **Un ancla de prueba estaba dos veces** (`test_sin_una_salida_con_el_mismo_tiempo_de_transito` está en dos clases de
   `test_clics`): la edición, que exige una sola, se negó, y la anclé con la línea anterior, que es de MAERSK.
7. **El primer borrador de la tabla de la Parte 1 contaba las posiciones desde la lista entera de la página,** con la
   opción de la otra lista: el informe del encargo 42 las cuenta dentro de la lista de cada campo. Las puse como allá.
8. **El primer gate del commit 2 cayó en una prueba del arranque del panel**
   (`test_web.TestArranqueDelPanel.test_cierra_a_la_fuerza_al_que_ocupa_el_puerto`, conexión rechazada), mientras
   corrían a la vez las pruebas del agente revisor y un `pytest` de otra sesión. La clase sola pasó (3 de 3), y el gate
   repetido pasó entero; la salida del primero quedó en `gate_c2_suite_interferencia.txt`. Que la causa fueran las otras
   pruebas, que usan puertos locales, es lo más probable, sin medir. Desde ahí, mis precensos y mis gates no se pisaron
   en el tiempo (sus horas están en sus resúmenes); las pruebas de otras sesiones no las controlo.
9. **Di por equivalente `mk-ruta-sin-el-campo` y la quité en el commit 1,** con razón: el campo tenía que ser idéntico a
   la sugerencia. Al preparar el commit 6, que compara el campo como la regla, la seguí dando por equivalente sin volver
   a mirarla, y ya no lo era: lo que quedó en el campo puede diferir de la sugerencia. Volvió antes del gate (pieza 7).
10. **El primer borrador de este informe tenía 28 líneas de prosa de más de 120.** El armador las reacomoda ahora con
    `reacomodar.py`, que no parte un código entre backticks ni toca tablas, títulos ni bloques de código, y aborta si el
    texto cambia en algo más que los saltos de línea.
11. **Dos comentarios que el commit 6 dejó viejos decían lo contrario de lo que hace el programa** (revisión del
    informe): el de `_mk_ciudad`, que devuelve la sugerencia y lo que quedó en el campo «iguales», y el de
    `_mk_ruta_buscada`, que la rama «el campo quedó con» ya no se alcanza. Desde el commit 6 el campo se compara como la
    regla, y las dos pueden diferir en mayúsculas, tildes o espacios. Los corrige el commit 7, que además deja sintético
    el ejemplo del prefijo, como en las pruebas.
12. **Tres sondas no cumplían lo que el informe decía de ellas** (revisión del informe): `freno_ruta.py` saltaba sin
    contar los bloques sin estado final (el 0 venía de la salida del encargo 42), `iguales_mk.py` saltaba sin contar los
    HTML sin tarjetas, y `corridas_recientes.py` no tenía control. Ahora cuentan (las 5 carpetas de inicio de sesión y 0
    bloques sin estado final; 15 HTML leídos y 7 sin tarjetas), y la tercera aborta si no encuentra la última corrida
    del encargo 42. En la segunda pasada de la revisión aparecieron dos más, `campo_quedo.py` y `espacios_mk.py`, que
    saltaban sin contar las carpetas sin `log.txt`: ahora las cuentan, y no salta ninguna (leen las 26).
13. **El borrador daba por medido el origen de las 6 reservas de MAERSK que llegaron a la guarda** (revisión del
    informe): `freno_mk.py` lo mide con la lista del 30-09 que trae lo mismo escrito, no con la suya, que no se guardó,
    y la lista cambia entre corridas. El resumen, el veredicto y el residual lo dicen ahora así.

## Premisas del encargo contrastadas (pieza 5)

- **«La variante A acertó en las 4 listas del 30-09»:** confirmado con el código del commit 1 y con el del 6, no solo
  con la sonda del encargo 42.
- **«En 7 de 8 listas de salidas hay tarjetas repetidas con HTML idéntico byte a byte»:** confirmado, y más fuerte. El
  encargo 42 comparó el `outerHTML` en el navegador, que no trae lo que va dentro de las raíces shadow; con ellas (de 6
  a 12 por tarjeta), los grupos son los mismos 12.
- **«_mk_ciudad toma la primera sugerencia Container Yard»:** cierto hasta este encargo; con la regla, ya no.
- **«El país no viene aparte»** y **«cada Container Yard se repite como Store Door»:** no los volví a medir; la regla no
  mira el país, y el filtro del tipo descarta la Store Door gemela.
- Ninguna premisa resultó falsa.

## Residual (pieza 6)

- **Las listas y el campo de las 6 reservas de MAERSK que llegaron a la guarda** (21-09 y 24-09): lo que pulsaron tiene
  la forma de tu regla, y en la lista del origen del 30-09 la regla elige lo mismo, pero sus propias listas no se
  guardaron y su `log.txt` no anota el campo. Si ese día cada una era la única Container Yard con esa forma, en el
  origen y en el destino, y si el campo quedó con ella, no se puede medir. **Se reabre** con la primera corrida con ese
  origen y ese destino: `mk_f<fila>_origen` y `_destino` miden su lista, y si el campo no calza, el motivo lo dice.
- **El campo con el texto entero:** medido en una sola corrida (los 2 campos de las 15:21 del 30-09). Si en otra el
  portal deja el campo con otro texto, la fila queda NO ENVIADA con lo que quedó en el motivo. **Se reabre** con ese
  motivo.
- **La tarjeta que se pulsa entre las copias es la primera.** Si el portal arma la misma reserva con cualquiera de ellas
  no está medido. **Se reabre** con la primera reserva emitida desde una tarjeta repetida.
- **Las raíces shadow cerradas no se leen,** ni en la evidencia ni en la lectura: dos tarjetas que difirieran solo
  dentro de una contarían como idénticas. En el HTML guardado no se puede saber si hay alguna. **Se reabre** si una
  reserva que eligió entre copias («… copia de otra…» en `log.txt`) no queda como la salida que se ve en la tarjeta.
- **Lo escrito con una letra con tilde o una ñ entre la segunda y la quinta** no encuentra su lista en MAERSK (pregunta
  2), y COSCO busca «CL» al final de un puerto que lo trae (pregunta 3). En `logs/` no pasó ninguna de las dos. **Se
  reabre** con tu respuesta.
- **`_falta_en_la_fila` sigue leyendo «-» en el destino final como sin destino** en una fila que no salió de los
  lectores: así, cualquier camino que se salte los lectores no entra al portal con «-». **Se reabre** si aparece un
  camino que arme las filas sin los lectores.
- **`_mk_ruta_buscada` conserva su rama de «ninguna sugerencia quedó en el campo»,** que desde `reservar_maersk` ya no
  se alcanza (sus pruebas la llaman directo; la de «el campo quedó con» vuelve a alcanzarse desde el commit 6). Y
  `_mk_ciudad` es larga: 157 líneas desde el commit 6 (122 en la base y 138 en el commit 1; revisión de código, B5).
  **Se reabre** con el próximo cambio de `_mk_ciudad`: partirla, y quitar esa rama si sigue sin alcanzarse.
- **El motivo dice «así que no pulsé nada» también cuando el campo no calza,** aunque la sugerencia se pulsó: ese final
  lo pone el corte de todas las navieras, y CMA lo tiene igual en su puerto (revisión de código, B1). **Se reabre** si
  quieres que el motivo lo distinga: cambia el texto de todos los cortes.
- **Con dos vueltas, el motivo es el de la última en que apareció la lista** (revisión del informe): si en la primera
  había 2 y en la segunda la lista no apareció, dice «hay 2». **Se reabre** si quieres que diga las dos.
- **`MK_LECTURAS_CAMPO` (5 lecturas, 2 s) es una hipótesis:** en la única corrida que lo anota, el campo ya estaba en la
  primera lectura. **Se reabre** con un motivo de MAERSK que diga que el campo quedó con otra cosa.
- **El panel marca lo primero que falta,** como el motivo: una fila sin puerto de carga y sin destino dice «sin puerto
  de carga». **Se reabre** si quieres que marque las dos.
- **Nada de esto se probó en el portal.** **Se reabre** con la primera corrida de MAERSK: su `log.txt`, sus
  `mk_f<fila>_origen` y `_destino`, y el motivo de cada fila.

## Reglas de método aplicadas (pieza 7)

Contra `metodo-ciclo` **v14**:
- **PASO 0 de solo lectura**, con veredicto por parte (todas CICLO; los dos FRENA SI, NOTA).
- **Control positivo que aborta** en cada sonda (listas, páginas y tarjetas sintéticas; las 4 listas; el grupo de 3;
  corridas conocidas de `logs/`); `corridas_recientes.py` lo recibió en la revisión del informe (pieza 4, 12).
- **Todo salto silencioso lleva contador:** las carpetas de inicio de sesión, las carpetas sin `log.txt`, los bloques
  sin estado final y los HTML sin tarjetas (pieza 4, 2 y 12).
- **Todo registro es una hipótesis, incluidos los comentarios del código:** dos, que el commit 6 dejó viejos, decían lo
  contrario de lo que hace el programa, y los corrige el commit 7 (pieza 4, 11).
- **La unidad la fija el sujeto:** la regla decide por sugerencia y por campo; las copias, por tarjeta; «CL» y «-», por
  bloque de reserva.
- **El negativo tiene que morder:** cada prueba nueva con su mutación, y el censo completo sobre el último commit de
  código. Una mutación quedó equivalente por otro cambio del mismo ciclo, la lectura (c) de las cinco:
  `mk-ruta-sin-el-campo`, con el chequeo exacto del campo del commit 1, y la quité; con la comparación del commit 6 el
  campo puede quedar con otra forma, volvió a poder morder, y volvió.
- **Un número fijo deja de morder:** el gate de cada commit es relativo a lo que cambió (sus filtros), y el censo
  completo a toda la red.
- **Cada reemplazo afirma que su viejo aparece una vez,** con escritura atómica en binario y LF.
- **El cambio y su guardián, en la misma operación:** cada commit que cambia lo que hace el programa trae sus pruebas y
  sus mutaciones; el 7 solo cambia comentarios.
- **Fuente única:** el HTML entero de las tarjetas y el de la evidencia se arman con la misma lectura de raíces
  (`_JS_HTML_ENTERO`); «-» se lee en una sola función para los dos lectores.
- **Frenar cuando la decisión es de negocio:** las tildes, el prefijo y «CL» al final de COSCO, en preguntas.
- Reglas del módulo: sin clics nuevos (medido), `test_candado` sin cambios, nada importado desde la raíz en las pruebas,
  ni el puerto 8765; los datos de `logs/` solo en lectura y sin imprimirlos.
- **No chocaron entre sí.** Lo más cerca: «frenar cuando la decisión es de negocio» frente a aplicar tu regla como la
  dijiste. Lo que tu regla no decide (las tildes, el campo comparado como la regla, la lista quieta y la vuelta de más)
  lo tomé yo, porque se puede cambiar sin deshacer nada, y va en «Cómo leí» y en las preguntas, en vez de frenar el
  encargo.

## Entregable (pieza 8)

- Este informe, `CICLO-maersk-elige-exacto.md`, y `CLAUDE.md` al día, en el commit de documentación.
- La forma de los dos, medida con `revisar_informe.py` (del encargo 41): los bytes (sin CR, NUL, BOM ni caracteres
  invisibles), las líneas de prosa de más de 120, los códigos partidos entre dos líneas, el voseo y las marcas sin
  llenar. Los dos pasan: sin CR, NUL ni BOM, sin caracteres invisibles, sin códigos partidos, sin voseo y sin marcas sin
  llenar. Las únicas líneas de prosa de más de 120 son 2 de `CLAUDE.md` que ya estaban antes de este encargo; el título
  del informe también pasa de 120, y los títulos no se reacomodan.
- El código lo revisó un agente contra las decisiones y el informe otro, contra sus fuentes (abajo). No miré el informe
  renderizado: la pieza es opcional mientras R22 sea candidata.

## Las revisiones

### La revisión de código

Un agente revisó los cinco cambios, de solo lectura, sobre una copia con los cinco aplicados. Leyó el diff entero,
corrió 218 pruebas sueltas de la copia y ejecutó el programa en un Chromium real sobre páginas sintéticas con raíces
shadow. No encontró nada crítico ni alto. Encontró 2 hallazgos medios y 6 bajos. Corregí estos en el commit `6055965`:
- **M1, la lista a medias:** `_mk_ciudad` decidía con la primera lectura de la lista. Si una segunda sugerencia exacta
  llegaba después, pulsaba la primera, y la regla pide una sola. Ahora decide con dos lecturas iguales seguidas de sus
  Container Yard, y si la lista no se queda quieta, con la última, como ya hacía el buscador del Shipper
  (`_mk_resultados_quietos`). Cuesta una espera de medio segundo por campo.
- **M2, el campo:** se leía una vez, a los 0,4 s, y se comparaba exacto. Si el portal deja el campo con otra
  capitalización, o se asienta tarde, todas las reservas de MAERSK habrían cortado. Ahora se compara como la regla
  (`_mk_plano`) y se lee hasta `MK_LECTURAS_CAMPO` veces (5, cada 0,4 s; hipótesis). Si el campo queda con otra forma,
  el motivo de SIN-CUPO lo muestra.
- **B3, el prefijo:** con un espacio doble en las 5 primeras letras de la ciudad, el prefijo con que se espera la lista
  no estaba en ninguna sugerencia. Ahora se toma con los espacios de a uno, como compara la regla. En `logs/`, ninguna
  de las 76 ciudades que escribieron MAERSK y HYUNDAI trae espacios dobles, letras fuera de ASCII ni paréntesis.
- **B6, las pruebas que faltaban:** la lista que crece tarde, el campo con otra forma y el que se asienta tarde, el
  espacio doble, y lo escrito con un paréntesis cerrado, que no calza (la regla, tal como la dijiste).

Lo que no cambié, con su razón:
- **B1:** el motivo termina «así que no pulsé nada» también cuando el campo no calza, aunque la sugerencia sí se pulsó.
  Ese final lo pone el corte de todas las navieras, y CMA ya lo tenía igual en su puerto. Cambiarlo toca todos los
  motivos (residual).
- **B2:** «CL» al final, en lo que busca COSCO (pregunta 3). El revisor encontró que COSCO mismo escribe Chile como
  «(CL)» en algunas sugerencias.
- **B4:** dos lecturas literales de la regla. «Alfa (Norte, Sur), País» se corta en la primera coma, que va dentro del
  paréntesis, y no calza con «ALFA»; y lo escrito con un paréntesis cerrado, en la práctica, no calza con ninguna. Las
  dos terminan en NO ENVIADA, no en otra sugerencia, así que se quedan como dijiste. La segunda, con su prueba.
- **B5:** `_mk_ciudad` es larga (138 líneas cuando la revisó; 157 desde el commit 6), y dos ramas de `_mk_ruta_buscada`
  no se alcanzaban desde `reservar_maersk`. Con M2, la de «el campo quedó con» vuelve a alcanzarse; la otra queda
  (residual).

El revisor confirmó además, cada cosa medida:
- **Sin clics nuevos.**
- **El corte no lo traga ningún `except`.**
- **La evidencia** guarda lo mismo que antes: el mismo HTML y la misma cuenta de raíces en un Chromium real.
- **La lectura de salidas** sin `iguales` devuelve lo mismo que antes.
- **El panel** marca bien sin nave, MANUAL y sin ruta.
- **Los lectores** leen bien «-».
- **Las mutaciones:** las 1623 de entonces anclan una vez y compilan, y ninguna de las nuevas es equivalente.

### La revisión del informe

Otro agente revisó el borrador contra sus fuentes, de solo lectura y sin correr pruebas, porque el censo estaba
corriendo: las salidas de las sondas, los gates, el código de cada commit con `git show`, `tests/mutaciones.py` entre
commits y el informe del encargo 42. No leyó `logs/`. Confirmó las cifras de la red, de los gates y de las sondas, y que
el código hace lo que dicen las Partes 1 a 3. Encontró 1 hallazgo alto, 8 medios y 10 bajos, y los corregí todos:
- **Alto, el origen de las 6 reservas de MAERSK que llegaron a la guarda:** el borrador lo daba por medido, y se midió
  con la lista del 30-09, no con la suya. Ahora el resumen, el veredicto y el residual dicen que no se puede medir,
  igual que el destino y el campo (pieza 4, 13).
- **Dos comentarios del código, viejos desde el commit 6:** los corrige el commit `c233b63`, solo de comentarios. Para
  que el censo completo corriera sobre el último commit de código, detuve el del commit 6 hacia las 13:50, cuando
  todavía preparaba sus copias (su último aviso, a las 13:49, iba en 696 de 1628), y lo lancé sobre el 7; la copia del
  commit 7 se armó a las 13:53, después.
- **Las sondas:** dos saltos sin contar y un control que faltaba (pieza 4, 12; un tercer contador lo agregué de paso), y
  lo pulsado, que la pregunta 1 daba por medido sin medirlo (ahora `tildes_pulsadas.py`: 0 de 32).
- **El contrato:** la pieza 1 sin tres sondas (`espacios_mk.py`, la de las tildes y la del largo de `_mk_ciudad`) y sin
  decir que varias leen con los lectores del encargo 42; siete ítems del residual sin su condición de reapertura; y la
  pieza 7 sin decir si las reglas chocaron.
- **Afirmaciones de más:**
  - «la evidencia siempre es la lista de la que eligió»: si la lista cambia mientras se guarda, el clic sale de la
    nueva, y `_avisar_lista_distinta` lo avisa;
  - «lo escrito con paréntesis nunca calza»: un paréntesis que la coma deja abierto sí calza;
  - el prefijo con una letra con tilde «en las 5 primeras»: si es la primera, la lista se reconoce igual;
  - «HTML idéntico» igual a lo que midió el encargo 42, que comparó el `outerHTML`, sin las raíces shadow.
- **Lo demás, de redacción:** con qué commits se midió cada cosa, de qué lista son las 370 raíces, las 76 ciudades (de
  MAERSK y HYUNDAI), las mutaciones reancladas en `_mk_las_exactas`, los siete ayudantes (no navieras), el motivo con
  dos vueltas, mis otras tres lecturas de tu regla («Cómo leí») y lo que dice «Cómo probarlo» de `_reintento` y de una
  sola copia.

**La segunda pasada,** del mismo agente sobre el informe corregido: los 19 quedaron bien, y encontró 6 errores nuevos,
bajos, que también corregí: dos sondas más que saltaban sin contar (`campo_quedo.py` y `espacios_mk.py`; ahora cuentan,
y leen las 26 carpetas), qué toma el filtro del gate del commit 7, que las 5 carpetas que saltan las sondas son las de
inicio de sesión, la hora en que detuve el censo del commit 6, que los comentarios viejos los escribió el commit 1 y el
6 los dejó viejos, y el resumen de esta sección.
