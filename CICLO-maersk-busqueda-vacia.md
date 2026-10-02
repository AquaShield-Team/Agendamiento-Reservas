# CICLO · MAERSK: por qué la búsqueda de salidas volvió vacía (el destino que eligió el programa, en FRENO) y los tres puntos decididos: el detector de salidas, «Continue to book» y la casilla del Shipper

**Módulo:** Agendamiento Reservas · **Encargo 40** · **Fecha:** 2026-09-29 · **Método:** skill `metodo-ciclo` v14 ·
**Commits** (locales; el repo no tiene remoto, así que no hay push que entregar):
- `32f3860`: el detector de salidas cuenta solo el «Book» de una tarjeta;
- `2f4659e`: «Continue to book» o «Continue», solo si hay uno a la vista;
- `24b474e`: la casilla del Shipper, si su posición y su código coinciden;
- `6c0dba2`: lo que encontró la revisión de código;
- `57ebf67`: el panel pinta SIN-CUPO, de la revisión de este informe;
- y el de este informe, con `CLAUDE.md` al día.

**Base: `C:\dev\Agendamiento Reservas` @ `acd952c` · árbol limpio** (pieza 9). Lo medido sale de los `log.txt` y el HTML
de «Select sailing» de las 6 corridas de la fila 10 (26, 27 y 29-09; ese HTML, de 5 de ellas), de las 14 reservas de
MAERSK de `logs/`, de las 14 capturas de «Booking Information», del HTML de «Additional details» del 27-09 y del código
en `acd952c`.

> Datos reales solo en lectura. Las sondas leen el HTML y los `log.txt` en su lugar, sin copiarlos, y las capturas con
> OCR, sin mirarlas; una corre el JavaScript del programa sobre el HTML del 27-09 en un Chromium local sin red. Imprimen
> etiquetas de interfaz, cuentas, fechas y hashes: en este informe no van nombres de naves, viajes, puertos, depósitos,
> partes, códigos ni números de reserva; de las partes, solo AQUACHILE. Una sonda imprimió en la consola de la sesión
> el comienzo del nombre de una nave (pieza 4, 1): no llegó al repo ni a este informe, pero queda en la transcripción
> local de la sesión. No se miró ninguna captura.

**Resumen.**
- **La búsqueda vacía: FRENO, se cumple tu FRENA SI.** Es una regla nuestra: en la fila 10, el 29-09 el programa
  escribió en el destino lo mismo que los días anteriores, pero pulsó otra sugerencia. `_mk_ciudad` pulsa la primera que
  trae los primeros 5 caracteres de la ciudad escrita; el 26 y el 27-09 fue el texto de la celda, entero, y el 29-09 una
  con una palabra más en medio, que no es un país. La página de ese día trae esa otra sugerencia en la lista de destino
  de su formulario, no el destino de la fila, y dice «There are no sailings for your search». Lo demás fue igual en las
  6 corridas: la fila, el origen, el commodity, el contenedor, el reefer y la regla de la fecha («mañana», el día
  siguiente a cada corrida: el 30-09 para la del 29-09; la salida de la nave era el 11-10). No lo corregí (pregunta 1).
- **El detector de salidas:** cuenta solo el «Book» de una tarjeta de salida, como la lista. Con el aviso del portal,
  la fila queda SIN-CUPO y deja la evidencia de «Select sailing»; el panel la pinta «sin cupo» (hasta el commit 5, el
  estado decía «SIN-CUPO», pero el N° seguía en «procesando…» y la fila, marcada en curso). **Ojo:** lo más probable
  es que tu corrida del 29-09, con este detector, hubiera quedado SIN-CUPO por el destino equivocado (pregunta 2).
- **«Continue to book»:** se pulsa solo si hay un solo «Continue to book» o «Continue» a la vista; si no, NO ENVIADA con
  lo que el portal pide. En las 11 capturas legibles de esa pantalla hay uno solo.
- **La casilla del Shipper:** si el clic en el resultado con AQUACHILE no lo elige, se pulsa su casilla, solo si su
  posición y las cifras del código de su `id` apuntan a la misma; si no, corta como antes y dice por qué. Sobre el árbol
  real del 27-09 las dos coinciden.
- **La revisión de código** aprobó los tres cambios: 0 críticos, 0 altos, 1 medio (ese SIN-CUPO por el destino, la
  pregunta 2) y 5 bajos. El commit 4 (`6c0dba2`) corrige una carrera en la casilla, suma casos y mutaciones para
  guardas que ninguna prueba mordía y ajusta comentarios que afirmaban más de lo medido; lo demás queda en el residual.
- **La revisión de este informe** encontró 2 hallazgos altos, 5 medios y 12 bajos. Los altos: el panel dejaba una fila
  SIN-CUPO en «procesando…» (lo corrige el commit 5, `57ebf67`), y mi sonda contaba 9 reservas de MAERSK en vez de
  14, cuando lo que decide es el texto de la celda: 1 de origen y 2 de destino, en 6 filas (pregunta 1). Lo demás
  quedó corregido aquí, salvo un docstring, un comentario de prueba y el texto de un log, que corrige el commit 5.
- **Una segunda revisión,** del `CLAUDE.md` nuevo y de este informe ya corregido, encontró 0 altos, 2 medios y 10
  bajos, todos de texto: los corregí aquí y en `CLAUDE.md`, salvo unos comentarios del código sobre el «Continue to
  book» de antes y el panel antes del commit 5, que quedan en el residual.
- **Nada de esto se probó en el portal.** `test_candado` no cambia.

## Veredicto del PASO 0, por parte del encargo

| Parte | Veredicto | Qué quedó |
|---|---|---|
| Por qué la búsqueda de salidas volvió vacía | **PREGUNTA (FRENO):** se cumple tu FRENA SI; es una regla nuestra, la sugerencia de destino que elige `_mk_ciudad` | Sin cambios en esa regla (pregunta 1) |
| El detector cuenta solo el «Book» de una tarjeta; sin salidas, SIN-CUPO | **CICLO** | `32f3860` |
| «Continue to book» / «Continue», solo si hay uno a la vista | **CICLO:** medido con OCR, uno solo en 11 capturas | `2f4659e` |
| La casilla del Shipper, si su posición y su código coinciden | **CICLO:** medido en el árbol real, coinciden | `24b474e` |
| `test_candado` no cambia | **NOTA:** se cumple | Sin cambios |

## Lo medido

**Las 6 corridas de la fila 10 de MAERSK** (`corridas_mk.py`, `pasos_mk.py`; los `log.txt` de `logs/`, en su lugar):
del 26-09 a las 14:13 y 14:25, del 27-09 a las 18:32, 18:40 y 21:15, y la tuya del 29-09 a las 15:03. En las 6, el
encabezado de la reserva trae el mismo puerto de carga, el mismo destino y la misma nave (comparados por hash, sin
imprimirlos): es la misma fila. Cada paso de «Booking Information», línea por línea del `log.txt`; las líneas que la
sonda no clasifica son capturas, esperas, cookies, evidencias y pasos de después de la búsqueda, y ninguna de «Booking
Information» nombra un campo (`sin_clasificar.py`):

| Paso | 26-09 (2) y 27-09 (3) | 29-09, 15:03 |
|---|---|---|
| Origen: lo escrito y la sugerencia elegida | la misma en las 5 | la misma |
| Destino: lo escrito | la ciudad de la celda (lo mismo en las 6) | lo mismo |
| **Destino: la sugerencia elegida** | **el texto de la celda, entero** (2 palabras) | **otra: 3 palabras** |
| Commodity, contenedor, reefer, temperatura, GenSet, price owner | «Salmon, frozen, fish», 40 Reefer High, Standard (40´), -20 °C, importación No, «yo» | lo mismo |
| Fecha de zarpe | «mañana» (el 27-09 y el 28-09) | «mañana» (el 30-09) |
| El botón | «Continue to book» | lo mismo |
| El desenlace de la búsqueda | «Book» a la vista, a los 2,1 s | lo mismo |
| Lo que siguió | la lista, con salidas desde el 4-10; el 27-09 a las 21:15 eligió la salida de la nave del 11-10 | ninguna salida con fecha; REVISAR |

La sugerencia del 29-09 trae las 2 palabras de la celda, en orden, y una más **en medio** (`destino_forma.py`): no
empieza con el texto de la celda ni lo contiene.

**El HTML de «Select sailing»** (`html_mk.py`, `destino_donde.py`, `lista_forma.py`; `mk_f10_detenida.html` de cada
corrida, sin sus marcos):
- En las 4 del 26 y el 27-09, el encabezado de la página (un `h2`) trae el origen elegido y el destino de la fila; la
  sugerencia del 29-09 no aparece. Traen 14, 16, 6 y 6 tarjetas de salida, con 13, 15, 6 y 6 `mc-button` «Book».
- En la del 29-09, el destino de la fila no aparece; la sugerencia elegida ese día está en el valor de la lista de
  destino del formulario (un `mc-list`; que se vea en pantalla no está medido), y la fecha, «30 Sep 2026», en su campo
  de fecha (`mc-input-date`). La página dice «There are no sailings for your search», sin tarjetas, sin `mc-button`
  «Book» y sin «Search more sailing options»: sus únicos «Book» son los 3 enlaces a `/booking/new` que trae cada
  página de MAERSK guardada (en el menú del encabezado, en el encabezado y en el pie; `enlace_book.py`).

**La regla que eligió ese destino** es de `_mk_ciudad`: escribe la ciudad (la parte de la celda antes de la primera
coma), toma sus primeros 5 caracteres ASCII (con los espacios; una letra con tilde o una ñ se cae, no queda sin tilde)
y, entre las sugerencias que los traen en cualquier parte de su texto, pulsa la primera con «container yard» si hay
alguna, y si no, la primera. Después mira si el campo trae los 4 primeros de esos caracteres (el 29-09 los traía): si
no, lo intenta una vez más y, si tampoco, anota «sin sugerencia», pero la reserva sigue igual, porque
`reservar_maersk` no mira lo que devuelve. En las 14 reservas de MAERSK de `logs/` (`regla_ciudad.py`,
`palabra_de_mas.py`; que la palabra de más es un país lo mide `palabra_pais.py`, de la revisión del informe), que
vienen de **1 texto de origen y 2 de destino**, en las celdas de 6 filas (la unidad en que la regla decide es el texto
de la celda con su lista de sugerencias, no la reserva ni la fila), ninguna sugerencia elegida trajo «container
yard», y:

| Sugerencia elegida | Origen (1 texto, 14 reservas) | Destino de la fila 10 (6) | Destino de las filas 30 a 34 (8) |
|---|---|---|---|
| El texto de la celda, entero | 0 | 5 (26 y 27-09) | 0 |
| Las palabras de la celda y un país **al final** | 14 | 0 | 8 (21, 24 y 25-09) |
| Las palabras de la celda y una palabra **en medio**, que no es un país | 0 | 1 (29-09) | 0 |

El texto del destino de la fila 10 ya trae el país al final; el del origen y el del destino de las filas 30 a 34, no.
Ninguna página guardada trae la lista de sugerencias (0 `mc-option`; `opciones_lista.py`, de la revisión del informe).

**«Continue to book»** (`continuar_reservar.py`, `continuar_contexto.py`, `continuar_forma.py`):
- Con OCR, sin mirarlas, en las 14 capturas `mk_f<fila>_3_detalle.png` (el formulario lleno, justo antes del clic): en
  11 hay un solo botón que se lea «continue», al pie, y dice «Continue to book»; las otras 3 (las 2 del 26-09 y la del
  29-09) el OCR no las reconoce como el formulario y no cuentan. Las otras apariciones de «continue» son frases de
  ayuda, no controles.
- En HTML, solo la página de «Select sailing» del 29-09 lo trae (el formulario sigue en ella): un `mc-button` con
  `label="Continue to book"`, `appearance="primary"` y, en su raíz shadow, su botón interno con el mismo
  `aria-label`. Ninguna corrida guardó «Booking Information».

**El detector** (`usd_tarjetas.py`, que mira solo las 7 `detenida`, y `usd_todas.py`, de la revisión del informe): en
las 8 páginas de «Select sailing» guardadas (del 24 al 29-09; una es la de la guarda del 24-09), los 52 importes «USD»
van dentro de una tarjeta de salida, y ninguno fuera; la del 29-09 no trae ninguno.

**La casilla del Shipper, sobre el árbol real** (`casilla_real.py`): el JavaScript nuevo, sobre el HTML del 27-09 en
un Chromium local sin red y sin los `<script>` de la página, con la ventana del buscador abierta (en ese HTML está
cerrada): `_JS_MK_SHIPPER` ve una sola tarjeta «Shipper», 3 resultados, 1 con AQUACHILE y el buscador titulado
«Shipper»; `_JS_MK_SHIPPER_CASILLA` da «coinciden». Con la ventana cerrada, da «titulo» (el buscador no se ve).

## Cómo quedó cada punto

**1. El detector de salidas** (`32f3860`): el único «Book» con que `_mk_desenlace_sailing` da la búsqueda por
terminada, «con-zarpes», es el de una tarjeta de salida, leída con `_JS_MK_SALIDAS`: lo mismo con que
`_mk_elegir_nave` cuenta el «Book» de cada tarjeta, el `mc-button` con `label="Book"` dentro de un
`mc-card.new-sailings-card`. Un «Book» fuera de las tarjetas, como los enlaces del encabezado o el pie, ya no cuenta,
ni una tarjeta sin «Book». Como la lista, no mira si la tarjeta se ve, y lo anota «en la página» (commit 5; hasta ahí
decía «en pantalla»). Un importe «USD» a la vista, que mira antes, y los 45 s también la terminan, como antes.
- Con «no sailings for your search» a la vista, SIN-CUPO con el aviso del portal, como antes; y ahora deja también la
  evidencia de «Select sailing» (`mk_f<fila>_detenida`), la misma que dejaba el REVISAR de esa fila. El panel la pinta
  «sin cupo» (`57ebf67`): hasta ahí caía en «otro», y el estado decía «SIN-CUPO», pero el N° seguía en «procesando…»
  y la fila, marcada en curso, como NO ENVIADA hasta `f03bb75`.
- A los 45 s sin desenlace, sigue igual: busca la nave y, si no está, REVISAR. La señal de tarifas (un importe «USD» a
  la vista) no cambia.
- Lo más probable es que tu corrida de las 15:03, con este detector, hubiera seguido esperando hasta el aviso del
  portal y quedado SIN-CUPO (sin medir: no hay HTML de los 2,1 s, y el aviso está en el guardado unos 22 s después).
  **Ese SIN-CUPO vendría del destino que eligió el programa, no de la nave** (preguntas 1 y 2).

**2. «Continue to book»** (`2f4659e`): para pasar de «Booking Information» a la selección de nave, pulsa el único
botón a la vista cuyo texto entero es «Continue to book» o «Continue» (`_mk_continuar_a_la_nave`), sobre lo que su
JavaScript vuelve a leer justo antes.
- Lo busca hasta 15 veces, una por segundo; si la selección de nave ya apareció, no hace falta.
- Con cero o más de uno: NO ENVIADA, con lo que el portal pide (`ObjetivoNoEncontrado`, `mk_f<fila>_sin_objetivo`).
- Si está y no acepta el clic, lo vuelve a intentar en la vuelta siguiente; si no lo acepta en ninguna: formulario
  incompleto, NO ENVIADA con lo que el portal pide y `mk_f<fila>_booking`, como antes.
- Comparte el ayudante (`_mk_pulsar_unico`) con el «Continue» de «Recommended services»: la lectura de
  `_JS_MK_CONTINUAR` recibe ahora una lista de textos. El texto «Continue to book» sigue escrito en `reservar_maersk`,
  donde `test_candado` lo fotografía.

**3. La casilla del Shipper** (`24b474e`): si el clic en el resultado con AQUACHILE no lo elige (la única tarjeta
«Shipper» sigue sin él), `_mk_marcar_casilla` pulsa la casilla de ese resultado, solo si su posición y las cifras del
código de su `id` apuntan a la misma (`_JS_MK_SHIPPER_CASILLA`):
- su posición: la casilla que va justo antes del `label` del resultado, en un contenedor donde casillas (`input` radio)
  y `label` van alternados;
- sus cifras: la única casilla del contenedor cuyo `id` termina con las cifras que muestra el código (`party__code`) de
  la tarjeta del resultado.

Si no son la misma, o no hay una de las dos, corta como antes (NO ENVIADA con `mk_f<fila>_shipper`), y el motivo dice
por qué: «…y no pulsé la casilla del resultado: <por qué>». Si coinciden, deja `mk_f<fila>_casilla`, la pulsa con un
clic de JavaScript en el `input` (`_JS_MK_SHIPPER_MARCAR`, que vuelve a leer justo antes y la pulsa solo si siguen
coincidiendo y la única tarjeta «Shipper» sigue sin AQUACHILE), anota si estaba marcada y vuelve a comprobar la tarjeta.
Si la tarjeta lo muestra y el buscador sigue abierto, lo cierra con su «Close», como después del resultado; si no lo
muestra, NO ENVIADA. Si al volver a leer justo antes del clic la tarjeta ya lo muestra (el clic en el resultado tardó en
verse), sigue sin pulsar la casilla (`6c0dba2`, de la revisión de código). Las 3 casillas del HTML del 27-09 no
traen `disabled` (sus atributos son `class`, `id`, `name`, `style` y `type`).

## Cómo probarlo

Con **`Iniciar AQUASHIELD.bat`**; nunca con `Iniciar AQUASHIELD_EMISION.bat`. Antes, revisa que `config.json` no traiga
`"emitir_reservas": true` en «opciones», que no esté definida la variable `AQUASHIELD_EMITIR` (la abren 1, true, si o
yes) y que el programa no se lance con el argumento `emitir`, `--emitir`, `produccion` o `--produccion`: con cualquiera
de las tres llaves, se emite. Si tienes un panel abierto de antes, ciérralo y vuelve a abrirlo, así carga el código
nuevo.

- **La fila 10 de MAERSK, mientras decides la pregunta 1:** si el portal vuelve a ofrecer primero esa otra sugerencia
  y responde que no hay salidas, ahora la fila queda **SIN-CUPO**, y no por la nave. En su `log.txt`, la línea
  «Destino '…': …» dice qué sugerencia eligió; compárala con la celda de la planilla. Queda `mk_f10_detenida.html` con
  la página.
- **En el `log.txt` de una fila de MAERSK:** «pulsado el único «Continue to book» o «Continue» a la vista»; «salidas
  con su «Book» en la página (N s)» o «tarifas cargadas en pantalla (N s)» cuando la búsqueda da salidas, «el portal
  responde: no hay zarpes (N s)» cuando no, y «la búsqueda de zarpes tardó más de 45s; procedo a buscar naves» sin
  desenlace. En el panel, una fila SIN-CUPO dice «sin cupo».
- **En el Shipper, si el clic en el resultado no lo elige:** «Shipper: pulsé la casilla del resultado con AQUACHILE;
  antes del clic, marcada: …», y `mk_f<fila>_casilla`. Si no la pulsa, el motivo de la NO ENVIADA dice «…y no pulsé la
  casilla del resultado: <por qué>; no pulsé nada más y la reserva no se envió».
- **Si corta en «Booking Information»:** «Booking Information de MAERSK: … no encontré un solo botón «Continue to book»
  o «Continue» a la vista … (había N)», con `mk_f<fila>_sin_objetivo`, el primer HTML de esa pantalla.

## Qué decides tú

1. **El destino que elige el programa (FRENO).** Hoy `_mk_ciudad` escribe la ciudad de la celda y, entre las
   sugerencias que traen sus primeros 5 caracteres, pulsa la primera con «container yard» (que en `logs/` nunca
   apareció) o, si no hay, la primera. Mira si el campo trae los 4 primeros, pero eso no frena nada: sin ellos, lo
   intenta otra vez y la reserva sigue. El 29-09 esa primera sugerencia fue otra que la de los días anteriores, y la
   búsqueda volvió vacía. Lo medido es poco: 1 texto de origen y 2 de destino, en 6 filas. ¿Cómo sigo?
   - **Medir primero:** que el programa deje el HTML de la lista de sugerencias antes de elegir, como el buscador del
     Shipper, sin cambiar la regla. Ninguna corrida la guardó, así que no se sabe qué otras ofrece el portal.
   - **La que trae las palabras de la celda, en orden, y de más solo un país al final:** la cumplen todas las
     sugerencias elegidas en las 14 reservas, de origen y de destino, salvo el destino del 29-09. Si no hay una sola
     así, NO ENVIADA con lo que ofreció el portal; y comparando el valor que queda en el campo con lo elegido, no solo
     4 caracteres.
   - **La que es, entera, el texto de la celda:** sirve para el destino de la fila 10, pero no para el origen ni para
     el destino de las filas 30 a 34, cuyas celdas no traen el país.
   - **Que siga como hoy.**
   Y si la regla nueva alcanza también a las demás navieras: CMA (`_cma_puerto`, `_cma_entrega`) usa el mismo prefijo
   de 5 caracteres, ONE (`_JS_PICK_SUGGESTION`) y HYUNDAI (`_hmm_autocomplete`) también pulsan la primera sugerencia
   que trae la ciudad, y MSC (`_msc_puerto`), la más corta a la vista que la trae.
2. **El motivo de SIN-CUPO.** Con el detector nuevo, una búsqueda con el destino equivocado queda SIN-CUPO si el
   portal responde que no hay salidas («There are no sailings for your search»; si la ruta equivocada sí las tiene, la
   nave no aparece y queda REVISAR), y se puede leer como una nave sin cupo. ¿Le agrego al motivo el origen y el
   destino que eligió el programa (hoy están en `log.txt`, no en la planilla)?

## Re-medir (pieza 1)

Las sondas son de solo lectura y no se versionan, porque leen datos reales. Quedaron en el scratchpad de esta sesión
(`$env:TEMP\claude\<proyecto>\<sesión>\scratchpad\e40`), que puede limpiarse; sin ellas, estos números no se re-miden.
Las que leen `logs/` abortan si no pasa su control positivo (las que importan otra, con el de esa), y leen en su lugar,
sin copiar el HTML ni los `log.txt`. Las herramientas del gate (`anclas.py`, `retarget.py`, `red_por_commit.py`) no
tienen un control escrito: el de `retarget.py` fue una corrida a mano.
- **`corridas_mk.py`:** las carpetas de `logs/` con reservas de MAERSK (solo la fecha y hora de su nombre; su
  separador de reservas acepta, desde la revisión del informe, el «(fila N)» del log del 21-09), y de cada
  reserva la fila, un hash corto de su puerto de carga, su destino y su nave, y su estado final. Su control: la fila 10
  de la corrida del 29-09 a las 15:03:11.
- **`pasos_mk.py`:** cada línea del bloque de la fila 10 que calza con un texto del programa, con lo escrito y lo
  elegido como hash o como forma (largo, «container yard» sí o no) y las URL sin su dominio ni sus parámetros. Su
  control: la corrida del 29-09 trae «fecha:» y «Origen».
- **`sin_clasificar.py`:** de las líneas que `pasos_mk.py` no clasifica, la primera palabra si es del programa y si
  alguna nombra un campo (ver la pieza 4, 1).
- **`html_mk.py`:** en cada `mk_f10_*.html` de esas corridas, cuántas veces aparecen el destino de la fila, lo escrito
  y lo elegido (sin imprimirlos), y las tarjetas, los `mc-button` «Book», «no sailings for your search», «Search more
  sailing options», los importes «USD» y las fechas. No ve los enlaces «Book» que llevan un ícono adentro (pieza 4,
  13): los 3 enlaces los cuenta `enlace_book.py`. Su control: la corrida del 29-09 tiene su `mk_f10_detenida.html` y
  su log dice una sugerencia de destino.
- **`destino_forma.py`:** cuántas palabras tienen la celda, lo escrito y lo elegido el 29-09, y cuáles comparten, sin
  imprimirlas; y el texto alrededor de «no sailings for your search», con cada palabra que no es de interfaz tapada. Su
  control: la sugerencia del 27-09 tiene que ser el texto de la celda.
- **`destino_donde.py` y `lista_forma.py`:** en qué etiqueta y atributo de cada `mk_f10_detenida.html` están lo elegido
  y lo escrito, y la forma del valor del `mc-list` y dónde está «30 Sep 2026» en la del 29-09.
- **`regla_ciudad.py` y `palabra_de_mas.py`:** en las 14 reservas de MAERSK de `logs/` (toman las reservas de
  `corridas_mk.py`, con su separador corregido; las volví a correr), si la sugerencia elegida en Origen y en Destino
  es el texto de la celda, si trae sus palabras y dónde va la de más. Su control: el destino del 29-09 distinto de la
  celda, y el del 27-09 a las 21:15, igual.
- **`continuar_reservar.py`, `continuar_contexto.py` y `continuar_forma.py`:** los «Continue» y «Continue to book» del
  HTML guardado y, con OCR, de las 14 capturas de «Booking Information» (por botón de color, el método de
  `e29/one_botones.py`, y en la imagen entera, con la línea en que aparece «continue»); y la forma del `mc-button` en el
  HTML del 29-09 (con `e39/casilla_forma.py`). Sus controles: una imagen sintética con «Continue to book» blanco sobre
  azul; por captura, que se lea «commodity»; y que haya exactamente un `mc-button` así.
- **`usd_tarjetas.py`:** en los 7 `mk_*_detenida.html`, las tarjetas de salida y los importes «USD» dentro y fuera de
  ellas. Su control: una página sintética con uno dentro y otro fuera.
- **`casilla_real.py`:** el JavaScript de la casilla, de la copia con el commit 3, sobre el HTML del 27-09 en un
  Chromium local sin red y sin los `<script>` de la página, con la ventana del buscador cerrada y abierta. Sus
  controles: una sola tarjeta «Shipper», 3 resultados y el título a la vista, y que con la ventana cerrada no dé
  «coinciden».
- **`e39/casilla_codigo.py` y `e39/casilla_relacion.py`**, vueltos a correr: la posición y las cifras de cada casilla en
  el HTML del 27-09.
- **`copia.py`, `anclas.py`, `largas_copia.py`, `precenso.sh`, `gate.sh`, `censo.sh`, `commit.sh`, `red_por_commit.py`
  y `comun.py`:** los del encargo 39, con la ruta de este. **`retarget.py <copia>`**, nuevo: las mutaciones cuya ancla
  cambió de función o de constante respecto de HEAD (anclas.py solo cuenta cuántas veces calza). Su control: renombrar
  en una copia la función donde calzan dos anclas las muestra movidas; no ve las que cambian de ancla y de función a
  la vez (pieza 4, 9).
- **De la revisión del informe** (`revision_informe\`): `enlace_book.py` (los «Book» fuera de las tarjetas),
  `usd_todas.py` (los importes de las 9 páginas), `palabra_pais.py` (si la palabra de más es un país, sin
  imprimirla), `opciones_lista.py` (las listas de sugerencias guardadas) y `sugerencias_todas.py`; todas con su
  control positivo, y las corrí para confirmar lo que cito.
- **De la segunda revisión** (`revision_docs\`): `anclas_por_funcion.py` (en qué función calza cada ancla de las
  mutaciones) y `bytes_commiteados.py` (CR, BOM y caracteres invisibles), cada una con su control positivo.
- **Los cambios:** `aplicar_c1.py` a `aplicar_c5.py` y `aplicar_docs40.py`, con `comun.py`: cada viejo, exactamente una
  vez, y escritura en binario, LF; este informe, con `corrige40_informe.py` y `reflujo40.py`, y después de la segunda
  revisión, con `corrige40b.py` (y `arregla_sin_clasificar.py`, la sonda).

La red versionada, desde `C:\dev\Agendamiento Reservas`: `python tests/correr.py` (la suite, unos 5 min),
`python tests/correr.py --mutaciones --filtro <texto>` (`mk-detector`, `mk-nave`, `mk-casilla`…) y
`python tests/correr.py --mutaciones` (el censo completo).

## NO retroceder (pieza 2)

- **El detector no vuelve a contar cualquier «Book» a la vista.** Cada una de las 9 páginas de MAERSK guardadas trae 3
  enlaces «Book» fuera de las tarjetas, y lo más probable es que uno de ellos terminara la espera a los 2 s. Lo vigila
  `test_el_book_del_encabezado_no_termina_la_busqueda` (su página falsa anota el localizador genérico).
- **El panel pinta SIN-CUPO.** Sin su rama, el N° queda en «procesando…» y la fila, marcada en curso; lo vigila
  `test_envio.TestLecturaDelPanel`.
- **SIN-CUPO deja la evidencia de «Select sailing».** Con ese HTML se midió el destino que buscó el programa el 29-09;
  sin él, un SIN-CUPO solo dejaría una captura. Lo vigila
  `test_clics.TestMaersk.test_sin_cupo_deja_la_evidencia_de_select_sailing`.
- **«Continue to book» sigue escrito en `reservar_maersk`.** Es el texto que `test_candado` fotografía antes de la
  guarda: si se mueve a una constante, esa foto cambia.
- **La casilla del Shipper se pulsa solo con las dos pruebas de identidad a la vez** (posición y cifras del código), y
  con el clic de JavaScript que vuelve a leer justo antes. Una sola de las dos es lo que el encargo 39 dejó en FRENO.
- **El destino de MAERSK no se corrige sin tu decisión** (pregunta 1): cualquier regla nueva cambia qué ruta se busca.

## Universo y cobertura (pieza 3)

- `logs/`: 23 carpetas, todas con `log.txt`; 10 con MAERSK; 14 reservas de MAERSK (5 del 21-09, que la sonda no veía:
  pieza 4, 12), de 6 filas (la 10 y de la 30 a la 34), con 1 texto de origen y 2 de destino; 6 de la fila 10 (26, 27 y
  29-09), y 5 de ellas dejaron el HTML de «Select sailing».
- HTML de MAERSK: 9 páginas sin sus marcos: 8 de «Select sailing» (7 `mk_*_detenida.html` del 25 al 29-09 y la de la
  guarda del 24-09) y 1 de «Additional details» (27-09); ninguna de «Booking Information».
- Capturas de «Booking Information» (`mk_f<fila>_3_detalle.png`): 14; 11 legibles por OCR, 3 que no cuentan.
- Sugerencias elegidas: 28 (14 de origen y 14 de destino), de 3 textos de celda; la lista de sugerencias que ofreció
  el portal no está en ninguna corrida.
- La casilla, en el HTML del 27-09: 3 resultados.

## Defectos de instrumento cazados (pieza 4)

1. **Una sonda imprimió en la consola de la sesión el comienzo del nombre de una nave.** `sin_clasificar.py` mostraba
   las dos primeras palabras de cada línea sin clasificar, y en las dos corridas del 26-09 la segunda palabra de una de
   ellas era el comienzo del nombre de la nave. Salió solo por esa consola, no a un archivo ni a este informe. Ahora
   imprime solo la primera palabra, y solo si es del programa.
2. **Mi primer borrador afirmaba «0 líneas sin clasificar» en el paso a paso,** y `pasos_mk.py` dejaba de 10 a 19 por
   corrida sin clasificar. Lo medí con `sin_clasificar.py`: son capturas, esperas, cookies, evidencias y el resultado, y
   ninguna de «Booking Information» nombra un campo.
3. **`retarget.py` se caía con los archivos que no son Python** (los `.bat` y `LEEME.md`, que también llevan
   mutaciones): los lee ahora solo si terminan en `.py`.
4. **El ancla de una mutación del encargo 39 quedó dos veces** con la lista de textos de `_JS_MK_CONTINUAR`
   («distingue mayúsculas»: `mkTexto(e)).trim().toLowerCase();` también está en otro JavaScript de MAERSK). `anclas.py`
   lo vio antes del gate; ahora se ancla con lo que va delante.
5. **Una mutación del encargo 39 dejó de morder con el commit 3** (`mk-shipper-cerrar-sin-la-tarjeta`, en el primer
   precenso): su caso, una tarjeta sin AQUACHILE con el buscador abierto, ahora pasa primero por la casilla y no llega a
   lo que la mutación cambia. No era una prueba inútil: el caso quedó incompleto para el flujo nuevo. Sumé a esa prueba
   el caso que sí llega (dos tarjetas «Shipper» con el buscador abierto), y muerde.
6. **La prueba de la casilla esperaba una captura de página completa,** y en la red `reg.captura(…, full=True)` no la
   hace (solo con `AQUASHIELD_CAPTURA_FULL`). Lo corregí antes de correrla.
7. **Mi borrador de la pregunta 1 contaba mal las sugerencias** («17 antes del 29-09»: el origen del 29-09 también
   cuenta). Con la sonda de entonces eran 9 de origen y 9 de destino; con la corregida, 14 y 14 (defecto 12).
8. **Un heredoc de Bash no sirve para reemplazar texto con barras invertidas** (el entorno lo registra): el script de
   corrección del commit 3 abortó sin escribir. Corregí el script con Edit, y el script escribió los archivos del repo
   en binario, como los demás.
9. **`retarget.py` no ve una mutación que cambia de ancla y de función a la vez:** la cuenta como nueva, porque su ancla
   nueva no está en HEAD. Así dijo 4 movidas en el commit 2, y el mensaje de `2f4659e` dice «3 pasaron al ayudante»:
   son 5 en `_mk_pulsar_unico` (3 con su ancla de antes y 2 con ancla nueva) y 1 en `_mk_continuar_a_la_nave`. Lo
   encontró la revisión de código, con su propia sonda.
10. **Dos mensajes de commit afirman de más,** y los corrige este informe: el de `32f3860` da como hecho que el enlace
    «Book» del encabezado o el pie terminó la búsqueda del 29-09 (es lo más probable: pieza 5, 1); el de `2f4659e` dice
    «11 de las 14 capturas, del 21 al 27-09», y las 14 llegan al 29-09 (las 11 legibles son del 21 al 27-09). El
    commit 4 corrige los comentarios del código que decían lo mismo.
11. **Dos pruebas nuevas no mordían lo que dicen:** la de que `reservar_maersk` sigue con `_mk_continuar_a_la_nave` caía
    por `StopIteration`, no por su aserción; y cinco guardas nuevas no tenían un caso que las mordiera (los pares de
    casilla y `label`, no pulsar con dos tarjetas «Shipper», las tres formas de anotar si estaba marcada y
    `_mk_shipper_listo`). Las encontró la revisión, con mutantes propios; el commit 4 les da su caso y su mutación.
12. **Mi sonda contaba 9 reservas de MAERSK, no 14,** y en la unidad equivocada. Su expresión del separador no admitía
    el «(fila N)» del log del 21-09, y escribí en el informe que ese log «no trae el separador»; lo trae. Y la regla
    decide por el texto de la celda y su lista de sugerencias: 9 corridas del mismo texto no son 9 casos. Son 14
    reservas de 6 filas, con 1 texto de origen y 2 de destino. Lo encontró la revisión del informe; corregí la sonda y
    volví a medir. Al corregirlo escribí «1 celda» por «1 texto» y «la fila 30» por las filas 30 a 34: las 8 reservas
    de ese destino son las 5 filas del 21-09 y la 30 del 24 y el 25-09 (`sugerencias_todas.py` lo muestra por fila).
    Lo encontró la segunda revisión.
13. **«El único «Book»» era falso:** cada página trae 3 enlaces «Book» a `/booking/new`, y la expresión de
    `html_mk.py` no veía los 2 que llevan un ícono adentro. El commit 4 lo había escrito en un docstring; lo corrige el
    commit 5. También contaba 7 páginas de «Select sailing» (`usd_tarjetas.py` solo miraba las `detenida`): son 8, con
    la de la guarda del 24-09, y 52 importes. El mensaje de `32f3860` repite el 7/50.
14. **Dije de más en tres lugares:** que el enlace terminaba la espera «antes del aviso del portal», que la corrida
    del 29-09 «habría quedado SIN-CUPO» con el detector nuevo, y que el commit 4 corregía los comentarios que lo daban
    por hecho (quedaba uno en `test_clics`). Son lo más probable, sin medir; el comentario lo corrige el commit 5.
15. **`sin_clasificar.py` decía en un comentario que la nave salió el 29-09** (fue en las corridas del 26-09), y en su
    docstring, que imprimía las dos primeras palabras. La primera revisión encontró lo primero, y lo di por corregido
    sin corregirlo; la segunda encontró los dos, y ahí los corregí.
16. **Describí de más el «Continue to book» de antes,** en los comentarios de `AQUASHIELD.py`
    (`_mk_continuar_a_la_nave` y `reservar_maersk`), en el de `test_reservar_maersk_sigue_solo_con_el_ayudante`, en el
    mensaje de `2f4659e` y en el borrador de `CLAUDE.md`: «el primer botón habilitado cuyo nombre accesible los traía,
    sin mirar si se veía». El código de `acd952c` tomaba el primero cuyo nombre accesible traía «Continue to book» y lo
    pulsaba solo si estaba habilitado; si no, o si el clic fallaba, lo mismo con «Continue». `get_by_role` deja fuera
    lo que está oculto para ARIA, y el clic esperaba a que el botón se viera: lo que no hacía era elegir entre los que
    se veían. Lo encontró la segunda revisión; `CLAUDE.md` y este informe lo dicen así, y los comentarios quedan en el
    residual.
17. **Dos afirmaciones de más sobre `_mk_ciudad`:** «sin tildes» (descarta todo carácter que no es ASCII: una letra
    con tilde o una ñ se cae) y «la da por buena si el campo trae los 4 primeros», como si eso frenara algo
    (`reservar_maersk` no mira lo que devuelve: sin ellos, la reserva sigue). Y el orden se podía leer al revés:
    prefiere la primera con «container yard». Lo encontró la segunda revisión.
18. **Lo que SIN-CUPO hacía en el panel antes del commit 5 lo dije a medias:** el estado mostraba «SIN-CUPO»; lo que
    seguía en «procesando…» era el N°, y la fila quedaba marcada en curso. Lo dicen igual de corto el mensaje de
    `57ebf67` y su comentario en `lecturaEstado`. Y el borrador de `CLAUDE.md` daba como hecho que, con el detector
    nuevo, la fila del 29-09 queda SIN-CUPO: es lo más probable, sin medir, y solo si el portal responde que no hay
    salidas. Lo encontró la segunda revisión.

## Premisas del encargo contrastadas (pieza 5)

1. **«El detector dio la búsqueda por terminada al ver un «Book» del encabezado o del pie»: lo más probable, sin
   medir.** En el HTML de esa página, guardado unos 22 s después, los únicos «Book» son 3 enlaces a `/booking/new`,
   los mismos que trae cada página de MAERSK guardada, en el encabezado y en el pie. A los 2,1 s no hay HTML.
2. **«El 27-09, la misma fila sí encontró su nave»: se confirma.** Las 6 corridas traen el mismo puerto de carga, el
   mismo destino y la misma nave; la del 27-09 a las 21:15 eligió su salida del 11-10, y las dos del 26-09 y las de
   las 18:32 y 18:40 del 27-09 vieron una salida de la nave, pero con el «Book» contado por el texto (antes de
   `a07d465`) la leyeron sin «Book».
3. **La búsqueda vacía no fue la del destino de la fila, sino la de otro.** El informe anterior leyó la página del 29-09
   como si el portal no tuviera salidas para esa ruta (su pregunta 3 hablaba de SIN-CUPO); buscó otro destino.
4. **«Si el portal dice que no hay salidas, la fila queda sin cupo»:** así quedó, pero con el destino equivocado, si
   el portal responde que no hay salidas, esa fila también queda SIN-CUPO, y la causa no es la nave (pregunta 2).

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| El destino (y el origen) de MAERSK con la primera sugerencia que trae los primeros 5 caracteres de la ciudad | FRENO: lo decides tú (pregunta 1) | decides la regla |
| Un SIN-CUPO de MAERSK no dice qué ruta se buscó | Lo decides tú (pregunta 2) | decides |
| La espera de `_mk_elegir_nave` (hasta 20 s) todavía termina con cualquier botón «Book» o un importe «USD» | Es solo una espera antes de leer la lista, no decide nada; el encargo nombró el detector | una lista se lee antes de cargar |
| La señal de tarifas del detector (un importe «USD» a la vista) sigue | En las 8 páginas de «Select sailing» guardadas, los 52 importes van dentro de una tarjeta | aparece un importe fuera de una tarjeta |
| «Booking Information» no tiene HTML guardado de su propia pantalla | Ninguna corrida lo guardó; lo medido es OCR de 11 capturas y el formulario que sigue en la página de «Select sailing» del 29-09 | el primer corte deja `mk_f<fila>_sin_objetivo` |
| El clic en «Continue to book» espera 4 s por vuelta, no 5, y un clic que falla se reintenta hasta 15 veces: si nunca sale, queda «formulario incompleto» después de más de un minuto (antes, uno o dos clics de 5 s) | Comparte el ayudante del «Continue» de «Recommended services» | un clic que tarda más, o un corte así |
| La casilla del Shipper, con un clic de JavaScript, no está probada en el portal | Ninguna corrida pasó por ahí; no se sabe si se ve | la primera corrida que la pulse (deja `mk_f<fila>_casilla`) |
| Si algo más se mete entre los resultados del buscador, la casilla no se pulsa | La regla pide casillas y resultados alternados | una corrida corta por «posicion» |
| Con un «Continue to book» a la vista pero deshabilitado, no está medido qué pasa: si Playwright no lo ve deshabilitado, recibe un clic sin efecto y la reserva queda NO ENVIADA al no avanzar (hasta 35 s); si lo ve, cada clic espera y falla, y queda «formulario incompleto» después de más de un minuto. Antes, «formulario incompleto» al instante | La regla decidida mira cuántos hay a la vista, no si están habilitados; en lo guardado no trae `disabled`, y depende de cómo el `mc-button` diga que está deshabilitado | un corte así en una corrida |
| Si el clic en «Continue to book» falla por otra cosa (algo encima que recibe el clic), la planilla dice «formulario incompleto»; el error real queda en `log.txt` | Es lo que hacía antes | un corte así |
| Si la página ya estuviera en `/sailings` antes del clic, no pulsaría nada y seguiría | Lo mismo hace «Recommended services» con «Additional details»; el paso anterior deja la página en `/book/` | pasa |
| Otras pruebas de `reservar_maersk` (del encargo 39) también caen por `StopIteration` y no por su aserción | Muerden igual; el motivo del censo sale vacío | se tocan |
| ONE, HYUNDAI y CMA también pulsan la primera sugerencia que trae la ciudad (CMA, con el mismo prefijo de 5 caracteres), y MSC, la más corta a la vista que la trae | El encargo es de MAERSK; lo pregunto (pregunta 1) | una corrida de esas elige otro puerto |
| El detector, como la lista, no mira si la tarjeta de salida se ve | «Como la lista» es lo decidido | una tarjeta oculta con «Book» termina la espera |
| Los comentarios de `AQUASHIELD.py` (`_mk_continuar_a_la_nave` y `reservar_maersk`) y de `test_clics` describen el «Continue to book» de antes como «el primer botón habilitado… sin mirar si se veía», y el de `lecturaEstado` dice que SIN-CUPO dejaba la fila en «procesando…» (pieza 4, 16 y 18) | Son notas de historia; corregirlas pedía otro commit de código y otro censo completo | se toca ese código |
| Del encargo 39: la línea de 126 columnas de los `.bat` | Sigue igual | se toca el `.bat` |
| Del encargo 39: una carrera si el buscador del Shipper se cierra solo justo antes del «Close» | Corta, sin otro clic | una corrida corta por «siguió abierto» o «ya no había un solo «Close»» |
| Del encargo 39: después de «Continue» de «Recommended services» no se comprueba que el portal avanzó | La espera de «Additional details» lo cubre a medias | una corrida se queda en esa pantalla después del clic |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v14**. Del instrumento: el control positivo que aborta (cada sonda que lee `logs/`; el de
`retarget.py` fue una corrida a mano), todo salto silencioso con su contador (líneas sin clasificar, capturas que el
OCR no reconoce, páginas sin marcos), la unidad de la medición (la búsqueda de cada corrida; y en la regla del
destino, el texto de la celda y no la reserva, que al principio conté mal: pieza 4, 12). Del guardián: el
negativo que muerde (cada prueba nueva con su mutación, precenso en una copia y gate), el negativo vacuo que delata un
caso incompleto (pieza 4, 5) y el censo de guardianes (el completo, sobre el último commit de código). Del registro:
todo registro es una hipótesis (la pregunta 3 del informe anterior, pieza 5, 3), re-medir contra HEAD, el residual
declarado, las premisas contrastadas. Del cambio: fuente única (`_mk_pulsar_unico` para los dos «Continue»; el detector
lee con `_JS_MK_SALIDAS`, lo mismo que la lista), cada reemplazo con su viejo exactamente una vez y escritura en
binario, el EOL (LF, 0 CR en lo commiteado) y el cambio con su guardián en el mismo commit. Del límite: **FRENAR**
cuando la decisión es de negocio: el destino (pregunta 1). Del encargo: TAREA / DATOS / FRENA SI.

Del módulo (`CLAUDE.md`): el candado (nada cambió después de la guarda; `test_candado` igual), antes de la guarda no hay
clics a ciegas (cada clic nuevo, por lo que es, y sin tragarse `ObjetivoNoEncontrado`; la foto de `test_clics` igual),
la evidencia donde la reserva se detiene (`mk_f<fila>_detenida` en SIN-CUPO y `mk_f<fila>_casilla`), las pruebas son
fotos (las cambiadas, en el mismo commit), toda prueba nueva con su mutación, la sonda de secretos antes de cada
commit, y los datos reales solo en lectura.

**Choques:** ninguno entre reglas. Una consecuencia, declarada: la decisión 3 (SIN-CUPO si el portal no tiene salidas)
convierte en SIN-CUPO una búsqueda con el destino equivocado cuando el portal responde que no hay salidas, y eso es
justo lo que el FRENA SI pide no corregir; seguí las dos y lo pregunto (pregunta 2).

## Entregable (pieza 8)

- **Este `.md`:** no se convirtió en página; se leyó como texto.
- **`CLAUDE.md` al día,** en el commit de este informe: el detector y SIN-CUPO, «Continue to book», la casilla del
  Shipper (de FRENO a decisión), el FRENO del destino y el origen, la evidencia `mk_f<fila>_casilla` y la de SIN-CUPO,
  los estados y el número de pruebas.
- **La red, commit por commit:**

| Commit | Pruebas | Mutaciones | Pares |
|---|---|---|---|
| `acd952c` (base) | 492 | 1365 | 1627 |
| `32f3860` | 497 | 1370 | 1632 |
| `2f4659e` | 504 | 1379 | 1648 |
| `24b474e` | 508 | 1399 | 1670 |
| `6c0dba2` | 510 | 1405 | 1677 |
| `57ebf67` | 510 | 1407 | 1679 |

- **El gate de cada commit:** la suite completa en verde, sin cambios en los originales, y los censos filtrados (pares
  que muerden / pares), todos en OK:

| Commit | Suite | Censos filtrados |
|---|---|---|
| `32f3860` | 497 | mk-detector 4/4 · mk-sincupo 1/1 · mk-zarpes 3/3 |
| `2f4659e` | 504 | mk-continuar 30/30 · mk-nave 11/11 · mk-incompleto 6/6 · test_los_cortes_antes_de_la_nave_son_no_enviada 4/4 · TestContinuarMaersk 28/28 |
| `24b474e` | 508 | mk-casilla 31/31 · mk-shipper 66/66 · test_solo_ahi 62/62 · TestShipperMaersk 89/89 · test_js 279/279 |
| `6c0dba2` | 510 | mk-casilla 37/37 · mk-shipper 67/67 · TestShipperMaersk 96/96 · TestContinuarALaNaveMaersk 22/22 · test_solo_ahi 62/62 |
| `57ebf67` | 510 | panel- 28/28 · TestLecturaDelPanel 27/27 · mk-detector 4/4 |

- **Antes de cada gate,** las mutaciones se censaron en una copia (`precenso.sh`), con los filtros de su gate (el del
  commit 4, sin `test_solo_ahi`, cuya prueba solo cambió en un comentario). En el commit
  3, el primer precenso dio 1 que no muerde (pieza 4, 5); corregido, 66/66 y 89/89. `test_js` va en el commit 3 porque
  cambió la página falsa de Node (`DOM_AQ`), que usan todas las pruebas de JavaScript.
- **El censo completo, sobre `57ebf67`, el último commit de código:** 1407 mutaciones y 1679 pares, todos muerden (0
  que no muerden y 0 errores fuera de los motivos); 510 pruebas, ninguna sin mutación; el control, la copia sin mutar,
  pasa; 3396 originales fotografiados, 0 cambios. De 22:42:21 a 23:43:12, 60 min 51 s, y sin suspensión ni reinicio:
  en el registro System hay 2 eventos de Kernel-Power en ese lapso, los dos 105, «Cambio de fuente de energía»; como
  control, la misma consulta encuentra el apagado de las 11:37 (109, con 125, 521 y 577). Uno anterior, sobre
  `6c0dba2`, lo paré a mitad cuando la revisión del informe trajo el commit 5, y borré su carpeta de trabajo por su
  nombre.
- **Cada commit:** la sonda de secretos dio 0 sobre el árbol y 0 sobre lo agregado, y 0 CR en los archivos commiteados.
- **La revisión de código:** un agente, en solo lectura, con sus propias copias, mutantes y sondas (sin `logs/`), sobre
  los commits 1 y 2 y el 3 antes de su commit.
  - Resultado: aprobado; 0 críticos, 0 altos, 1 medio y 5 bajos.
  - Confirmó: que solo cambian dos tramos de `reservar_maersk` antes de la guarda y `test_candado` es idéntico; que el
    único clic nuevo es el de la casilla, sobre un elemento identificado; que `TestContinuarMaersk` del encargo 39
    pasa con el ayudante nuevo, salvo por la forma del argumento; que `parentElement` en `DOM_AQ` no cambia las otras
    pruebas de JavaScript (la suite, 508 en verde); que las 34 mutaciones nuevas calzan una vez y en su función; y 0
    caracteres invisibles, CR ni BOM.
  - **El medio:** un SIN-CUPO por el destino equivocado se lee como falta de cupo (pregunta 2).
  - **Los bajos:** la carrera de la casilla; las guardas sin caso y la prueba que caía por `StopIteration` (pieza 4,
    11); el botón deshabilitado y el motivo de un clic fallido en «Continue to book» (residual); los comentarios y
    mensajes que afirmaban de más (pieza 4, 10); y las listas de evidencia del código.
  - Quedó en `6c0dba2`: la carrera, los casos y sus 6 mutaciones, la prueba con su aserción, los comentarios y las
    listas de evidencia. Pidió medir si las casillas traen `disabled`: no lo traen (punto 3). Lo demás, en el residual.
- **La revisión de este informe:** un agente, en solo lectura, sobre el borrador y los commits 1 a 4, con sus propias
  sondas sobre `logs/` (cada una con su control positivo que aborta; imprimen cuentas, hashes, booleanos y textos de
  interfaz) y el JavaScript del panel corrido en Node.
  - Resultado: 2 altos, 5 medios y 12 bajos; ninguno cambia el FRENO.
  - Confirmó: los commits y la base; las 6 corridas de la fila 10 (la misma fila por hash, el «Book» a los 2,1 s, el
    HTML unos 22 s después); el HTML de «Select sailing»; en el código, el orden del detector, el ayudante de los
    «Continue», el flujo de la casilla y que `_mk_ciudad` no cambió; que `test_candado` y la foto de clics genéricos no
    cambiaron; los números de la red y de cada gate; 0 CR, BOM ni caracteres invisibles; y que el informe no trae voseo,
    datos reales ni el nombre del operador. No corrió las sondas de OCR ni la del Chromium.
  - **Los altos:** el panel dejaba una fila SIN-CUPO en «procesando…» (el commit 5, con sus 2 casos y 2 mutaciones); y
    el universo y la unidad de la pregunta 1 (pieza 4, 12).
  - **Los medios:** «el único «Book»» (pieza 4, 13; el docstring, en el commit 5); tres afirmaciones sin medir (pieza 4,
    14; el comentario de `test_clics`, en el commit 5); el control positivo, declarado y no escrito en `retarget.py`,
    `red_por_commit.py` y `anclas.py` (queda dicho en «Re-medir»); una fila del residual sin condición de
    reapertura (ahora la tiene); y la misma regla en CMA, ONE y HYUNDAI, con la comprobación de 4 caracteres que dejó
    pasar la sugerencia del 29-09 (en la pregunta 1 y el residual).
  - **Los bajos:** en «Cómo probarlo», los argumentos que también abren el candado, la línea de las tarifas, la de los
    45 s y el final del motivo del Shipper; el precenso del commit 4 sin `test_solo_ahi`; las 8 páginas y 52 importes;
    las 5 corridas con HTML de «Select sailing»; la transcripción local de la sesión (pieza 4, 1); los «primeros 5
    caracteres»; el Edit del commit 3 (pieza 4, 8); el detector que no mira si la tarjeta se ve (residual, y el log
    dice «en la página» desde el commit 5); las corridas del 26-09 en la premisa 2; el `mc-list` del destino; la sonda
    que mide el país; y la opción de guardar primero la lista de sugerencias (pregunta 1). Quedaron corregidos aquí o
    en el commit 5.
- **La segunda revisión:** otro agente, en solo lectura, sobre el `CLAUDE.md` nuevo, antes de commitearlo, y este
  informe ya corregido, contra el código en `57ebf67` y git; sin correr la red (corría el censo completo) ni leer
  `logs/`.
  - Resultado: 0 altos, 2 medios y 10 bajos, todos de texto.
  - Confirmó: la tabla de la red (con `red_por_commit.py`) y cada cifra del gate contra sus archivos; que `test_candado`
    y la foto de clics no cambian; el código detrás de cada afirmación del diff de `CLAUDE.md`; lo que dice «Cómo
    probarlo» del lanzador y de los textos del log; las fechas de los commits citados; y 0 CR, BOM ni caracteres
    invisibles, sin voseo.
  - **Los medios:** «la fila 30» eran las filas 30 a 34, y la unidad es el texto de la celda (pieza 4, 12); y el
    borrador de `CLAUDE.md` daba como hecho el SIN-CUPO del 29-09 (pieza 4, 18).
  - **Los bajos:** el «Continue to book» de antes (pieza 4, 16); lo que el panel hacía con SIN-CUPO (pieza 4, 18); la
    prueba que vigila la evidencia de SIN-CUPO; el importe «USD» y los 45 s en el detector; los reintentos del clic de
    «Continue to book» (residual); `_mk_ciudad` (pieza 4, 17); MSC en la pregunta 1; «Re-medir» (`regla_ciudad.py` y
    `palabra_de_mas.py` ya veían 14, y `html_mk.py` no ve 2 de los 3 enlaces); `sin_clasificar.py` (pieza 4, 15); y
    tres detalles: de quién es `usd_tarjetas.py`, el HTML de «Booking Information» y la ventana del buscador abierta a
    mano. Quedaron corregidos aquí y en `CLAUDE.md`, salvo los comentarios del código, que van al residual.
