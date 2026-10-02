# CICLO · Ampliar la búsqueda de la nave y cerrar HYUNDAI

**Módulo:** Agendamiento Reservas · **Encargo 32** · **Fecha:** 2026-09-26 y 27 · **Método:** skill `metodo-ciclo` v14 ·
**Commits** (locales; el repo no tiene remoto, así que no hay push que entregar): uno por ítem, `bf75525` (MAERSK),
`4c34f83` (COSCO), `05cfdb7` (ONE), `c95e5c0` (HYUNDAI: la nave y «Duration»), `d8cff13` (HYUNDAI: el modal) y `e8b027b`
(COSCO: el campo por su lista de opciones); tres que salieron de la revisión del informe, `2819828` (HYUNDAI: el freno
del modal también si aparece tarde), `f164fd7` (HYUNDAI: el «Book Now» vuelve a leer su tarjeta) y `a18f771` (MAERSK:
anota por qué dejó de ampliar); y el de este informe.

**Base: `C:\dev\Agendamiento Reservas` @ `4cae528` · árbol limpio** (pieza 9). Las mediciones de `logs/` y de las
planillas se hicieron sobre esa base, antes del primer commit del encargo.

> Sin datos reales. `logs/`, las planillas y `config.json` se midieron en solo lectura, con sondas que tapan naves,
> viajes, fechas, contratos y el nombre del operador, e imprimen conteos, booleanos, etiquetas de la interfaz, días
> relativos y formas enmascaradas. Las capturas se leyeron con OCR sin mirarlas. Los HTML guardados se leyeron en un
> Chromium sin red y sin el JavaScript de la página.

**Resumen:** todo está implementado y probado sin abrir los portales. **Ninguna de las seis se probó en el portal
con este código:** esa prueba la corres tú (abajo, «Cómo probarlo»).
- **Cuatro navieras amplían la búsqueda** cuando la nave de la fila no está en lo que el portal muestra de entrada, con
  la opción medida en sus pantallas guardadas, y si no la encuentran quedan REVISAR diciendo hasta qué fecha buscaron:
  - MAERSK, con «Search more sailing options», tanda por tanda;
  - COSCO, con la opción más larga de «Sailing Within N Weeks» (de 2 a 8);
  - ONE, con la opción más larga de su selector «N weeks», si hay una más larga que 8;
  - HYUNDAI, con la opción más larga de «Duration» (de 1 a 8 semanas).
- **HYUNDAI quedó cerrado como lo decidiste:** la nave de la fila es la «1st Vessel»; entre las que la traen, la próxima
  salida; y en el modal «Alternate Vessel Option» marca «I do not want to choose an alternate vessel» y pulsa OK.
- **MAERSK:** la salida pedida sin «Book» queda NO ENVIADA con «la salida pedida ya no se puede reservar».
- **FRENO en MSC y CMA:** la opción de ampliar no aparece en sus pantallas guardadas. No se tocaron.
- **La prueba con el lanzador de prueba la corres tú:** no la corrí porque entra a los portales con las credenciales
  guardadas y resuelve sus validadores, y eso no lo hago yo.
- `test_candado` no cambió. Los únicos clics nuevos antes de la guarda son los de ampliar y los dos del modal, cada uno
  por su texto (el desplegable «Duration» de HYUNDAI, por su id). El «Book Now» de HYUNDAI, que ya se pulsaba, ahora
  vuelve a leer su tarjeta antes de pulsarse.

## Veredicto del PASO 0, por parte del encargo

| Parte | Veredicto | Qué quedó |
|---|---|---|
| MAERSK: ampliar con «Search more sailing options» | **CICLO** | `bf75525`, y `a18f771` para anotar por qué dejó de ampliar |
| MAERSK: la salida pedida sin «Book» | **CICLO** | `bf75525` |
| COSCO: ampliar | **CICLO:** la opción, medida («Sailing Within N Weeks») | `4c34f83`, y `e8b027b` para reconocer el campo |
| ONE: ampliar con el selector de semanas | **CICLO:** el selector aparece en lo guardado, así que el freno no se cumple; sus opciones no están medidas | `05cfdb7` |
| HYUNDAI: la nave es la 1st Vessel; ampliar | **CICLO:** «Duration», medido | `c95e5c0`, y `f164fd7` para volver a leer la tarjeta al pulsar |
| HYUNDAI: el modal | **CICLO**, con su freno en el código: si no avanza tras el OK, corta sin otro clic | `d8cff13`, y `2819828` si el modal aparece tarde |
| MSC: ampliar | **PREGUNTA** (freno del encargo): la opción no aparece en las pantallas guardadas | Nada cambió en MSC |
| CMA: ampliar | **PREGUNTA** (freno del encargo): la opción no aparece en las pantallas guardadas | Nada cambió en CMA |
| La prueba con el lanzador de prueba | **PREGUNTA:** la corres tú (choque 4, pieza 7) | Sin correr: 0 de las 6 probadas en el portal con este código |

## Las seis: hasta dónde llegan y qué les falta

«Llegó» es lo que muestran los `log.txt` de las corridas con el candado cerrado del 24 al 26-09 (9 carpetas: 4 de
«todas» y 5 de una fila), antes de este encargo. Llegar a la guarda es armar la reserva completa y detenerse antes del
botón final.

| Naviera | Hasta dónde llegó (24 al 26-09) | Qué cambia con este encargo | Qué le falta para llegar a la guarda |
|---|---|---|---|
| **MSC** | A la guarda en 4 de 5. La otra (26-09, «todas») no entró: el login dio HTTP 502 | Nada: FRENO | Nada, con la nave en lo que muestra de entrada. Para ampliar, la opción (abajo) |
| **COSCO** | A la guarda en 2 de 4. Las otras 2 (25-09) quedaron NO ENVIADA por un empate que el tránsito ya resuelve | Amplía a 8 semanas si la nave, o su viaje, no está en las 2 de entrada | Una corrida con la nave más allá de 2 semanas, para ver la ampliación |
| **ONE** | A la guarda en 1 de 5. En 3, la fila pedía una nave de MSC («no encontrada», con 8 semanas; en las 2 listas guardadas, 32 tarjetas en cada una); 1 se cortó con el asistente reiniciado | Si la nave no está, prueba una opción de semanas más larga; si no hay, REVISAR con la fecha | Saber si hay más de 8 semanas; una fila con una nave de ONE |
| **HYUNDAI** | A la guarda en 3 de 5 (24 y 25-09), pero con otra nave: el calce viejo aceptaba el prefijo de la naviera, y el OK del modal salía con «Any» marcada. Con la nave pedida, 0. Las 2 del 26-09 quedaron NO ENVIADA en el modal | 1st Vessel, la próxima salida, «Duration» y el modal marcado | Una corrida que muestre si el OK del modal deja avanzar sin otro clic (el freno) |
| **CMA** | A la guarda en 2 de 5 (25-09). 24-09: la temperatura (ya corregida); 26-09: el mantenimiento o el Origen | Nada: FRENO | Que salga del mantenimiento; el HTML de su lista para medir la opción de ampliar |
| **MAERSK** | 1 de 5 llegó a la revisión (24-09), sin haber elegido la nave: un defecto viejo, ya corregido. Las otras 4 se detuvieron en «Select sailing». 25-09: la nave no estaba en las 5 salidas cargadas y el botón seguía cargando; 26-09: el viaje de la fila estaba solo en una salida sin «Book» | Amplía hasta que el portal no deja más; la salida sin «Book» queda NO ENVIADA con su motivo | Una fila cuya salida pedida tenga «Book» |

**Con el código de este encargo, 0 de las 6 se probaron en el portal.** La columna del medio está probada en la red
offline y sobre el HTML guardado (abajo, «Lo nuevo sobre el HTML guardado»), no en vivo.

## Cómo probarlo (con el lanzador de prueba, candado cerrado)

1. Cierra el panel si está abierto, para que tome el programa nuevo, y ábrelo con `Iniciar AQUASHIELD.bat` (nunca con
   el de emisión).
2. Corre, con el candado cerrado, una fila por naviera, de preferencia con una nave que salga más allá de lo que el
   portal muestra de entrada (más de 2 semanas en COSCO; más de lo que carga MAERSK de entrada).
3. La ampliación corre solo si la nave no está en lo de entrada: si está, no vas a ver ninguna de estas líneas. Lo que
   puede aparecer en `log.txt`:
   - al ampliar, «La nave no estaba en lo que mostró ONE: amplié las semanas y busco de nuevo.» (lo mismo con COSCO y
     «Sailing Within», y con HYUNDAI y «Duration»), o «pulsando 'Search more sailing options'...» en MAERSK, una vez por
     tanda;
   - si dejó de ampliar, por qué: en COSCO, «no amplié la búsqueda: …» (a veces repite «no pude ampliar la
     búsqueda»); en MAERSK, con la nave pero sin la salida pedida, «dejé de ampliar la búsqueda: …»; si no, en el motivo
     del REVISAR;
   - si la nave no aparece: REVISAR con «busqué hasta el DD-MM-AAAA, la última salida que mostró el portal, y …»;
   - HYUNDAI, en el modal: «HYUNDAI mostró el modal «Alternate Vessel Option»: marco que no quiero otra nave y pulso
     OK.», la evidencia `hmm_f<fila>_otra_nave` y, si pulsó, «modal 'Alternate Vessel Option': marqué «I do not want to
     choose an alternate vessel» y pulsé OK»;
   - HYUNDAI deja también `hmm_f<fila>_naves_mas` si amplió.
4. **El freno del modal de HYUNDAI**, si después del OK Booking Details no aparece (salga el modal al elegir la nave o
   más tarde):
   - si el modal sigue a la vista, NO ENVIADA con «HYUNDAI siguió mostrando el modal «Alternate Vessel Option» después
     de marcar … y pulsar OK; no pulsé nada más y la reserva no se envió», y `hmm_f<fila>_otra_nave_sigue`. Es tu freno:
     dímelo;
   - si el modal se cerró, REVISAR con «HYUNDAI: no avanzó al paso Booking Details», como antes, con la captura
     `hmm_f<fila>_3x_sinpaso3`.
5. Con eso mido lo que falta: las opciones de semanas de ONE, cuánto tarda MAERSK en cargar cada tanda, y el freno del
   modal de HYUNDAI.

## MAERSK · ampliar y la salida que ya no se puede reservar (`bf75525` y `a18f771`)

**Medido** en las 4 listas «Select sailing» guardadas (`mk_f*_detenida.html`) y en sus `log.txt`:
- el botón es `mc-button data-test="load-more-sailings-btn" label="Search more sailing options"`, con un botón adentro
  cuyo `aria-label` es el mismo texto; está en 3 de las 4;
- 25-09 (2 corridas): 5 tarjetas, de +1 a +9 días; el `mc-button` con `loading="true"`, y los dos, el `mc-button` y el
  botón de adentro, con `disabled`. El programa lo pulsó 2 veces, esperó 7 s cada una, y la tercera venció a los 4 s: se
  rindió con el botón todavía cargando;
- 26-09 (2 corridas): 14 tarjetas (+8 a +36 días; el botón habilitado) y 16 (+8 a +50; sin el botón). En las dos, el
  viaje de la fila está en una sola salida, y sin «Book»;
- **la tanda de entrada no se guardó:** las 4 listas son de después de los pedidos del programa.

**Cambio.** `_mk_elegir_nave` lee las salidas y, si la salida pedida no está (la nave, y su viaje si la fila lo trae),
pide más con `_mk_ampliar`:
- busca el único botón con el nombre accesible «Search more sailing options», exacto (`get_by_role`);
- espera hasta `MK_ESPERA_MAS` (40 s, hipótesis) a que se habilite, lo pulsa, y espera otro tanto a que haya más
  salidas;
- se detiene si no hay botón o no llegó ninguna salida nueva (`NO_AMPLIA_MAS`, «el portal no deja ampliar más la
  búsqueda»), si no pudo (con el porqué), o en el tope `AMPLIAR_MAX`, 12 tandas (hipótesis);
- si la nave está, pero no la salida pedida, al dejar de ampliar anota por qué en `log.txt` («dejé de ampliar la
  búsqueda: …», `a18f771`): el motivo de la NO ENVIADA no lo dice.

Después, según lo que encontró:

| Encontró | Estado |
|---|---|
| La salida pedida, con «Book» | La próxima entre ellas, como antes |
| El viaje de la fila, solo en salidas sin «Book» | NO ENVIADA, «MAERSK: la salida pedida ya no se puede reservar ('nave')», sin ampliar |
| La nave, sin el viaje de la fila, tras ampliar | NO ENVIADA, «ninguna de las N opciones de la nave trae el viaje de la fila» (encargo 31) |
| La nave, sin viaje en la fila, solo sin «Book», tras ampliar | NO ENVIADA, «la salida pedida ya no se puede reservar» |
| Nada de la nave, tras ampliar | REVISAR, «…no está en los itinerarios: busqué hasta el DD-MM-AAAA, la última salida que mostró el portal, y …» |

Con esto, las 2 corridas del 26-09 habrían quedado NO ENVIADA con «la salida pedida ya no se puede reservar», y en las 2
del 25-09 el programa habría esperado hasta 40 s a que el botón se habilitara, en vez de rendirse. Si el portal lo
habilita en ese tiempo, no está medido.

## COSCO · «Sailing Within N Weeks» (`4c34f83` y `e8b027b`)

**Medido** en las 2 listas guardadas (`cosco_f*_itinerarios_marco2.html`, 25-09): la búsqueda tiene tres pestañas
(«Sailing Schedule», la activa; «Intended Vessel Voyage»; y «Origin Earliest Depart. Date or Destination Latest Arrival
Date»). En «Sailing Schedule» hay un desplegable con las opciones «Sailing Within 2 Weeks» a «Sailing Within 8 Weeks»,
con la de 2 elegida, y el botón «Search Service». Las 2 listas traen 4 itinerarios, de +3 a +10 días.

**Cambio.** Si la nave, o su viaje, no está en lo que COSCO muestra de entrada, `_cosco_ampliar` abre con clic real el
único campo «Sailing Within» a la vista, elige con clic real la opción con más semanas y comprueba que quedó;
`reservar_cosco` vuelve a buscar con «Search Service» y espera más itinerarios que antes (`_cosco_leer_itinerarios`).
Amplía una vez: la opción más larga es la última. Si ya estaba en la más larga, no pulsa nada. Si tampoco aparece, el
REVISAR dice hasta qué fecha buscó; si aparece sin el viaje, corta con «sin-viaje» como antes, pero después de ampliar.

**De `4c34f83` a `e8b027b`.** La primera versión reconocía el campo por su valor, «Sailing Within N Weeks». Sobre el
HTML guardado no encontró ninguno (0 campos en las 2 listas): el valor de un campo no queda en el HTML, y sin el portal
no se podía saber si lo encontraría en vivo. `e8b027b` lo reconoce por lo que sí está en el HTML: la lista (`ul`) cuyas
opciones son todas «Sailing Within N Weeks», y el único campo a la vista que la nombra en `aria-controls`; las semanas
elegidas, por la marca de su opción (`selected` o `aria-selected`). Sobre las 2 listas da 1 campo, 2 semanas elegidas y
8 la mayor. Si no puede leer cuál está elegida, no amplía, y lo anota.

## ONE · el selector de semanas (`05cfdb7`)

**Medido** en las 2 listas guardadas (`one_f*_detenida.html`, 25-09): el selector es un `combobox` con la etiqueta
«Next» (`data-cy="booking-next-duration-days"`) que muestra «8 weeks», con 32 tarjetas en cada una. El programa ya elige
8 semanas antes de buscar, por la nota del Excel de agendamientos, «DEBE SELECCIONAR SIEMPRE 8 SEMANAS», y lo anotó en
10 reservas de 6 corridas. **Sus opciones no están medidas:** la lista cerrada no queda en el HTML. En esas 2 corridas
la fila de ONE pedía una nave de MSC.

**Cambio.** Si la nave no está, `_one_ampliar` abre el único selector «N weeks» y lee las opciones a la vista: si hay
una más larga que la elegida, la pulsa, comprueba que quedó, y `reservar_one` vuelve a buscar con su «Search» y espera
más tarjetas; si no hay, pulsa la misma que estaba, para cerrar la lista sin cambiar nada, y queda REVISAR con la fecha.
El selector y su opción van con `.click()` de JavaScript, como los pulsaba ya `_set_weeks_one`; los dos quedaron en la
foto de `test_clics` como «ESPECÍFICO». Con la nave en las 8 semanas, nada cambia: la nota se sigue cumpliendo (choque
7, pieza 7).

## HYUNDAI · la 1st Vessel, la próxima salida y «Duration» (`c95e5c0` y `f164fd7`)

**Medido** en las 2 listas guardadas (`hmm_f*_naves.html`, 26-09), con `_JS_HMM_TARJETAS` y `_proxima_salida` del
programa de HEAD (`validar_head.py`):
- cada tarjeta es un `li` con su origen y su destino (`.place-content`, cada uno con su fecha), sus campos
  `.schedule-info-text` de etiqueta y valor («Main Vessel», «Route», «Operator», «1st Vessel» y los cortes) y su «Book
  Now»;
- la nave de la fila es la «1st Vessel» de la 5.ª y la 6.ª tarjeta: salen el mismo día (+27), con 33 y 35 días de
  tránsito. La llegada menos la salida es el «N Days» de la tarjeta en las 12;
- con la regla de la próxima salida, **elige la 5.ª** (la de menor tránsito). Hasta `4cae528` pulsaba la 4.ª, que trae
  la nave como «Main Vessel» y sale de Chile en otra;
- «Duration» es `select#srchSelWeeks`, de «1 weeks» a «8 weeks», en el formulario de Select Vessel, con «Retrieve». Cuál
  estaba elegida en esas corridas no se sabe: el HTML guardado no lo trae.

**Cambio.** `_hmm_elegir_nave` lee las tarjetas con `_JS_HMM_TARJETAS` y calza la nave con el valor de «1st Vessel» (la
misma regla de palabras enteras). Si ninguna la trae, elige en «Duration» la opción más larga (`_hmm_ampliar`,
`select_option` por su texto), vuelve a buscar con «Retrieve» y deja la evidencia de la lista ampliada,
`hmm_f<fila>_naves_mas`. Entre las que traen la nave y se pueden reservar, la próxima salida; si no queda una sola, NO
ENVIADA con el motivo. Pulsa el «Book Now» de la elegida (`_JS_HMM_CLIC_TARJETA`) solo si, al volver a leer la lista en
el mismo JavaScript, esa tarjeta sigue siendo la elegida: su «1st Vessel» calza, se puede reservar y sale el mismo día
(`f164fd7`; hasta `e8b027b` pulsaba el i-ésimo «Book Now» a la vista sin volver a leerla, y entre leer y pulsar corre la
evidencia de la lista ampliada). Si la nave no aparece, REVISAR con la fecha; si está solo en tarjetas cerradas, REVISAR
«CERRADA», como antes, y sin ampliar. `_JS_HMM_INDICE_NAVE` queda solo para la interfaz anterior (`a.preview-area`).

## HYUNDAI · el modal (`d8cff13` y `2819828`)

**Medido** (encargo 31, en los 2 modales guardados): `#alternate_vessel_opt`, tres `label.radio-area` con su radio
`vessel-option` y su texto, la tercera «I do not want to choose an alternate vessel», y el OK, `#vesselOptionSubmit`,
sin `disabled`.

**Cambio.** `_hmm_mantener_nave`, en los dos momentos en que antes se miraba el modal (al elegir la nave y, si Booking
Details no aparece, otra vez):
1. deja la evidencia `hmm_f<fila>_otra_nave`;
2. busca la opción cuyo texto es exactamente «I do not want to choose an alternate vessel»; si no hay exactamente una,
   NO ENVIADA con «HYUNDAI no ofreció la opción de mantener la nave pedida; la reserva no se envió»;
3. la marca con un clic real y comprueba que su radio quedó marcado; si no, NO ENVIADA sin pulsar OK;
4. busca el único «OK» del modal; si no hay uno solo, NO ENVIADA sin pulsar nada más; si lo hay, lo pulsa.

Si uno de los dos clics falla, ERROR, como cualquier falla del programa antes de la guarda.

**Tu freno, en el código:** si después del OK Booking Details no aparece y el modal sigue a la vista, no pulsa nada más:
deja `hmm_f<fila>_otra_nave_sigue` y la reserva queda NO ENVIADA con «HYUNDAI siguió mostrando el modal … y pulsar OK;
no pulsé nada más y la reserva no se envió». Si el modal apareció recién en la segunda mirada, lo mira una tercera vez
para esto (`2819828`; hasta `e8b027b` ese camino quedaba REVISAR sin volver a mirarlo: lo cazó la revisión del informe).
Si el modal se cerró y Booking Details no aparece, REVISAR «HYUNDAI: no avanzó al paso Booking Details», como antes.

## Lo nuevo sobre el HTML guardado (`validar_head.py`)

La red offline prueba cada paso con páginas falsas. Esto prueba los selectores y el JavaScript nuevos sobre el HTML real
que dejaron las corridas: `validar_head.py` saca `AQUASHIELD.py` del commit con `git show`, abre cada HTML guardado sin
sus `<script>` en un Chromium sin red y sin JavaScript de la página (por `file://`, para que se armen las raíces shadow
declarativas), y corre sobre él lo del programa. Su control positivo (un botón sintético con raíz shadow y una tarjeta
sintética de HYUNDAI) aborta si no da lo esperado. Con `e8b027b`:

- **MAERSK:** `_mk_boton_mas` encuentra un solo botón en 3 de las 4 listas: deshabilitado en las 2 del 25-09 y
  habilitado en una del 26-09; en la otra del 26-09 no está, como en la medición.
- **COSCO:** `_JS_COSCO_SEMANAS` da 1 campo, 2 semanas elegidas y 8 la mayor, en las 2 listas. La de `4c34f83` daba 0
  campos.
- **ONE:** `_JS_ONE_SEMANAS` da 1 selector, en 8 semanas; `_JS_ONE_FECHAS`, 32 tarjetas con fecha en cada lista, de +8
  a +56 días.
- **HYUNDAI:** `_JS_HMM_TARJETAS` da 6 tarjetas en cada lista, todas disponibles y con un solo «Book Now»; la «1st
  Vessel» calza en la 5.ª y la 6.ª, y `_proxima_salida` elige la 5.ª. «Duration» está a la vista, con las opciones de 1
  a 8; el HTML da 1 como elegida, pero eso da un `select` sin la marca `selected`: cuál estaba elegida en vivo no se
  sabe.
- **El modal:** en los 2 guardados, el OK a la vista, una sola opción con el texto exacto (con su radio) y un solo «OK»
  por su texto.

**Lo que no prueba:** que el portal responda a los clics (que cargue más salidas, que la opción quede elegida, que el OK
deje avanzar), ni cómo se dibuja la página con el CSS del portal, que no se cargó (así, qué tarjetas de MSC tienen su
«Select» a la vista). Eso es la corrida en vivo. Los tres commits posteriores a `e8b027b` no tocan estos selectores.

## MSC y CMA (FRENO)

**MSC.** La lista de itinerarios queda en el HTML de la guarda (la pestaña de Route Details sigue en el DOM):
- 26 o 27 tarjetas en las 4 corridas, todas hermanas en un mismo contenedor, de +2 a +84 días (unas 12 semanas);
- después de la última, solo un texto legal; ningún botón de «más», ninguna paginación, ninguna clase de «load more»;
- el formulario trae «Sailing Date», ETD o ETA, y «Search Schedule»; ningún campo de semanas;
- las 9 capturas `msc_f*_2b_schedules.png` no muestran la lista (el OCR no lee «Select» ni «ETD» en ninguna).

El lector de MSC lee todas las tarjetas del HTML, pero cuenta solo las que tienen su «Select» dibujado (`offsetParent`).
Cuántas se dibujan no está medido: el HTML guardado se abrió sin el CSS del portal. La «opción debajo de las primeras 4
o 5 naves» no aparece en lo guardado. Si destapa tarjetas que ya están en el HTML pero ocultas, hoy el programa no las
cuenta; si solo desplaza la vista, ya las cuenta. **Qué necesito:** una captura o el HTML de la lista de MSC con esa
opción a la vista, o su texto exacto.

**CMA.** No hay HTML de su lista de rutas: `cma_f*_rutas` se guarda desde `50e3f04` (2026-09-25, 17:42), las 2 corridas
del 25-09 que llegaron a la lista son anteriores, y las del 26-09 cortaron antes, en el mantenimiento o en el Origen. En
los 44 HTML de CMA no aparece «Mostrar más», «más viajes» ni «show more»; en las 26 capturas de itinerario, el OCR lee
«Mostrar soluciones disponibles», «Ver producto» y «Mostrar detalles», no «Mostrar más viajes». El programa ya pulsa
«Mostrar más viajes» una vez si no ve la nave (Nota H23), pero en `logs/` nunca pasó: en las corridas que llegaron a su
lista, la nave estaba de entrada. No se tocó. **Qué necesito:** una corrida que llegue a la lista de rutas (deja
`cma_f<fila>_rutas`), o su texto exacto.

## Expectativas que cambiaron (antes → ahora)

| Qué | Antes (`4cae528`) | Ahora |
|---|---|---|
| MAERSK sin la salida pedida | Hasta 3 tandas de 7 s; REVISAR sin fecha | Hasta que el portal no deja más; REVISAR con la fecha |
| MAERSK, el viaje solo en salidas sin «Book» | REVISAR, como si la nave no estuviera | NO ENVIADA, «la salida pedida ya no se puede reservar» |
| MAERSK y COSCO, la nave sin el viaje de la fila | NO ENVIADA con lo primero que vio | NO ENVIADA después de ampliar |
| COSCO sin la nave | REVISAR con 2 semanas | Amplía a 8; REVISAR con la fecha |
| ONE sin la nave | REVISAR sin fecha | Prueba más semanas; REVISAR con la fecha |
| HYUNDAI, qué calza | El texto de toda la tarjeta, la primera en la página | La «1st Vessel», la próxima salida |
| HYUNDAI sin la nave | REVISAR | Amplía «Duration»; REVISAR con la fecha |
| HYUNDAI, el modal | NO ENVIADA, «HYUNDAI ofreció otra nave en lugar de la pedida» | Marca «I do not want…» y OK; si el modal sigue, NO ENVIADA |
| Clics antes de la guarda | — | Los de ampliar (por su texto) y los dos del modal; el «Book Now» de HYUNDAI vuelve a leer su tarjeta |

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\correr.py --mutaciones --filtro TestMaersk
python tests\correr.py --mutaciones --filtro TestProximaSalida
python tests\correr.py --mutaciones --filtro TestCosco
python tests\correr.py --mutaciones --filtro TestOne
python tests\correr.py --mutaciones --filtro TestHyundai
python tests\correr.py --mutaciones --filtro TestModalHyundai
python tests\correr.py --mutaciones --filtro TestFotoDeClicsGenericos
python tests\correr.py --mutaciones --filtro TestNaveCompleta
python tests\correr.py --mutaciones --filtro TestEvidenciaListaHyundai
python tests\correr.py --mutaciones --filtro TestCadaReservadorLaDeja
python tests\correr.py --mutaciones --filtro test_cada_naviera_anota_el_desempate
python tests\correr.py --todo
```

Las sondas son de solo lectura y no se versionan, porque leen datos reales. Quedaron en `scratchpad\e32`, que puede
limpiarse; sin ellas, estos números no se re-miden. Las que tienen control positivo abortan si no da lo esperado;
`inventario.py`, `inventario_png.py`, `ocr_vocab.py` y `anclas.py` no lo tienen (los conteos de `logs/` de la pieza 3
salen de las dos primeras):
- **`validar_head.py <commit>`:** lo nuevo del programa de ese commit sobre el HTML guardado (arriba).
- **`cosco_v2.py`:** el reconocimiento de «Sailing Within» por su lista, sobre las 2 listas de COSCO.
- **`inventario.py` e `inventario_png.py`:** los HTML y las capturas de `logs/` por naviera y paso (`inventario.py`
  cuenta también la raíz de `logs/` como carpeta: pieza 4, 12).
- **`ampliar_html.py`:** los controles de ampliar de cada lista guardada, con el texto tapado.
- **`mk_lista.py`:** las listas de MAERSK: tarjetas, rango de días, la nave, el viaje, el «Book» y el botón.
- **`control_semanas.py` y `cosco_semanas.py`:** «Sailing Within» de COSCO y «Duration» de HYUNDAI.
- **`hmm_tarjetas.py`:** las tarjetas de HYUNDAI con el lector nuevo y lo que elige la próxima salida.
- **`msc_lista.py`, `msc_estructura.py`, `etiquetas.py` y `rangos.py`:** la lista de MSC en el HTML de la guarda, y el
  rango de MSC y COSCO.
- **`cma_lista.py`, `ocr_lista.py` y `ocr_vocab.py`:** CMA en sus HTML y la lista de MSC y CMA en sus capturas, con OCR.
- **`grep_log.py`:** líneas de los `log.txt`, tapadas.
- **`anclas.py`:** cada `viejo` de `tests/mutaciones.py`, una vez en su archivo, y cada prueba nombrada, existente.
- **`tapado.py`:** el tapado común (palabras de las planillas y de los `log.txt`, el operador, las credenciales).

En PowerShell, cada una se corre con `$env:PYTHONIOENCODING='utf-8'` y después
`python "$env:TEMP\claude\C--dev-Agendamiento-Reservas\<sesión>\scratchpad\e32\<sonda>.py"`.

## NO retroceder (pieza 2)

- **No vuelvas a rendirte con «Search more sailing options» cargando:** se espera a que se habilite.
- **No busques ese botón por «el primero» de `button, a`:** va por su nombre accesible, exacto, y uno solo.
- **No trates la salida pedida sin «Book» como una nave que no está.**
- **No vuelvas a reconocer «Sailing Within» de COSCO por el valor del campo:** no queda en el HTML y no se puede
  verificar; va por su lista de opciones.
- **No vuelvas a calzar HYUNDAI con el texto de toda la tarjeta:** la nave de la fila es la «1st Vessel».
- **No pulses el OK del modal de HYUNDAI sin marcar antes «I do not want…»,** ni vuelvas a pulsarlo si el modal sigue;
  y míralo después del OK aunque haya aparecido tarde.
- **No vuelvas a pulsar el «Book Now» de HYUNDAI por su posición sin volver a leer su tarjeta.**
- **No amplíes MSC ni CMA con una opción que no esté medida.**

## Universo y cobertura (pieza 3)

- **`logs/`:** 15 carpetas, todas con `log.txt`; 0 HTML ni capturas descartados por nombre. De ellas, 9 son las corridas
  del 24 al 26-09 de la tabla de las seis.
- **MAERSK:** 4 listas (y 36 marcos); las 2 del 25-09 sin la fila en las planillas de hoy: se midieron sin la nave.
- **COSCO:** 2 listas con sus 8 marcos. **HYUNDAI:** 2 listas de 6 tarjetas y 2 modales. **ONE:** 2 listas (y 6
  marcos).
- **MSC:** 4 HTML de la guarda y 9 capturas de la lista. **CMA:** 44 HTML y 26 capturas de itinerario.
- **No medido:** las opciones de semanas de ONE; cuánto tarda MAERSK en cada tanda; si el OK del modal deja avanzar;
  cuál «Duration» estaba elegida en HYUNDAI; cómo se ve la opción de MSC, y qué tarjetas de MSC se dibujan; la lista
  de rutas de CMA.

## Defectos de instrumento cazados (pieza 4)

1. **Una sonda imprimió en la sesión el nombre de una nave de otra tarjeta de HYUNDAI** (no la de la fila, que sí se
   tapaba: el tapado conocía solo las naves de las planillas y de los `log.txt`). No quedó en ningún archivo del repo
   ni del scratchpad, pero sí en la transcripción de esta sesión. Desde ahí, las sondas que describen tarjetas imprimen
   las etiquetas y tapan todos los valores.
2. **El primer tapado (`ampliar_html.py`) tapaba toda palabra de 4 letras que no estuviera en una lista:** las etiquetas
   salían ilegibles. Se reemplazó por `tapado.py`, que tapa lo que es dato (las palabras de las planillas y de los
   `log.txt`, el operador, las credenciales, los códigos de letras y cifras).
3. **El control de `tapado.py` abortó:** pedía 50 palabras de las planillas y hay 48. Se bajó a 30; y dejaba pasar
   «POL<puerto>» (una palabra de la planilla pegada a una etiqueta): ahora tapa también el token que la trae pegada.
4. **`ocr_lista.py`:** su control abortó (leía 2 «Select» de 3 dibujados dentro de rectángulos; se dibujaron sin ellos),
   y su primer patrón no calzaba con el nombre real de las capturas (`2b_schedules`), así que dio «0 capturas».
5. **Las 9 capturas `msc_f*_2b_schedules.png` no muestran la lista** (0 palabras de interfaz con OCR, ni ampliadas): la
   lista de MSC se midió en el HTML de la guarda.
6. **`mk_lista.py` descartó 2 de las 4 listas** (sus filas del 25-09 ya no están en las planillas); se midieron sin la
   nave: tarjetas, rango y botón.
7. **Cinco mutaciones nuevas nombraban pruebas que no existen:** las 4 de COSCO con el prefijo de `test_envio.TestCosco`
   (las pruebas están en `test_clics.TestCosco`) y una de HYUNDAI con `TestEvidencia.test_solo_ahi`. El censo las habría
   rechazado todas. Se cazaron antes del censo de COSCO (se detuvo su gate y se volvió a correr); `anclas.py` ahora
   comprueba también que cada prueba nombrada exista. Dos revisiones lo marcaron como HIGH, ya corregido.
8. **El parche de HYUNDAI no se aplicó en la copia y las pruebas pasaron igual:** su ancla no traía un espacio al final
   de una línea del JavaScript viejo, y el bucle que aplicaba los parches siguió con los demás. Desde ahí, el bucle se
   detiene y dice cuál falló.
9. **El código de HYUNDAI repetía textos de ONE** y dejó 10 anclas de mutaciones de ONE con dos apariciones; y un nombre
   (`MARCA`) chocaba con uno que ya existía. `anclas.py` los cazó en la copia; se reescribieron.
10. **En la copia, la suite completa dio 1 falla** (`test_cada_naviera_anota_el_desempate`, que ahora incluye a HYUNDAI)
    y el censo de HYUNDAI, 2 mutaciones que no mordían (`hmm-vuelve-la-lista-ignore-sin-nw2`, porque la prueba ya no
    traía VOY, VIAJE ni V.; y `hmm-tarjeta-llegada-la-salida`). Se corrigieron antes del gate. Después,
    `hmm-tarjeta-hasta-la-lista` dejó de morder porque el tope del `li` la tapa: pasó a ser de dos cambios.
11. **COSCO pasó sus pruebas y su censo sin reconocer el campo real:** las pruebas usaban un campo falso con su valor, y
    el HTML guardado no lo trae (0 campos). Lo cazó `validar_head.py`, que corre lo nuevo sobre el HTML guardado; de ahí
    salió `e8b027b`. El censo completo sobre `d8cff13` se detuvo para correrlo sobre el último commit de código, y el de
    `e8b027b`, por los commits de la segunda revisión del informe.
12. **`inventario.py` contó 16 carpetas en `logs/`:** sumaba la raíz, que `os.walk` da primero. Son 15, todas con
    `log.txt`, como en el informe anterior. Lo cazó la segunda revisión del informe; se recontó con `iterdir()`.
13. **La herramienta Bash convierte `\\` en `\`:** un reemplazo con barras escrito en un heredoc no calzó; se pasó a
    archivos escritos con Write.
14. **Las revisiones del código:**
    - MAERSK: el tiempo del peor caso (40 s + 40 s por tanda, 12 tandas) queda en el residual; el botón pasó a buscarse
      por su nombre accesible, exacto (`get_by_role`), en vez del texto crudo, y la compuerta se volvió a correr;
    - COSCO y ONE: COSCO anota por qué no amplió; ONE avisa si no pudo cerrar la lista y cierra sus ventanas tras la
      nueva búsqueda, como tras la primera. Las líneas largas de las pruebas y las mutaciones quedaron como estaban;
    - HYUNDAI: la tarjeta no pasa de su `li`, con una lista de una sola tarjeta en la prueba;
    - COSCO, el campo (`e8b027b`): aprobado, con una observación especulativa que va al residual.

## Premisas del encargo contrastadas (pieza 5)

- **«Hoy el programa mira solo la primera tanda (en MAERSK, 5) y, si no ve la nave, corta»:** MAERSK ya pedía más, hasta
  3 veces, pero se rendía con el botón cargando; las 5 del 25-09 y las 14 y 16 del 26-09 son de después de esos pedidos,
  y la tanda de entrada no se guardó. ONE ya buscaba 8 semanas. En MSC, el HTML trae unas 12 semanas.
- **«MSC: la opción que aparece debajo de las primeras 4 o 5 naves»:** no aparece en lo guardado (el freno).
- **«La nave de la fila siempre existe»:** en 3 de las 5 corridas de ONE, la fila pedía una nave de MSC; en MAERSK, el
  26-09, la salida pedida estaba, pero sin «Book».
- **«La nave de la fila es la 1ST VESSEL, la que sale de Chile»:** en las 2 listas, la 1st Vessel de cada tarjeta es la
  que sale del puerto de origen.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| MSC no amplía | FRENO: la opción no aparece en lo guardado | …me mandas una captura o el HTML de la lista con la opción, o su texto |
| CMA no amplía; su «Mostrar más viajes» (Nota H23) sigue como estaba, una vez | FRENO: no hay HTML de su lista y el OCR no la ve | …una corrida deja `cma_f<fila>_rutas`, o me das su texto |
| ONE: no se sabe si su selector trae más de 8 semanas; si no, no amplía | La lista cerrada no queda en el HTML | …la corrida en vivo lo muestra en `log.txt` |
| MAERSK: `MK_ESPERA_MAS` (40 s) y `AMPLIAR_MAX` (12) son hipótesis. En el peor caso, unos 16 minutos por fila, y «Detener» no corta esa búsqueda (MAERSK no lo mira ahí) | No hay medición de cuánto tarda cada tanda | …la corrida en vivo mide las tandas |
| La fecha del REVISAR es la última salida que mostró el portal, no el fin del rango pedido | Es lo que se ve; el rango de cada portal no está medido | …prefieres el fin del rango |
| ONE, COSCO y HYUNDAI amplían una vez, a la opción más larga, no paso a paso | La más larga trae también lo de las cortas | …una opción más larga no trae lo de las cortas |
| HYUNDAI no exige el viaje de la fila (el valor de «1st Vessel» lo trae entre paréntesis) | No está decidido | …decides que lo exija |
| HYUNDAI elige la 5.ª (con transbordo, 33 días) sobre la 6.ª (directa, 35) | Es tu regla: los transbordos no cuentan | …prefieres las directas |
| COSCO comprueba la opción elegida por su marca en la lista, 0,6 s después del clic; si el portal tarda más en moverla, dice «no pude ampliar» aunque sí amplió (queda REVISAR, sin otro clic) | No está medido cuánto tarda | …la corrida en vivo muestra «quedó en None semanas» |
| ONE y HYUNDAI amplían solo si ninguna tarjeta trae la nave: si la traen, pero no se pueden reservar (en HYUNDAI, cerradas: REVISAR «CERRADA», sin fecha), no amplían; MAERSK sí | El encargo pide ampliar cuando la nave no está | …decides que amplíen también ahí |
| Más allá de la opción más larga, cada portal tiene un campo de fecha que buscaría más lejos: la tercera pestaña de COSCO, la fecha de zarpe de HYUNDAI, «Sailing Date» de MSC y la fecha de salida de ONE | No es la opción de ampliar decidida; sería otro clic antes de la guarda | …decides usarlo (preguntas 4 y 7) |
| MSC cuenta solo las tarjetas con su «Select» dibujado; cuáles se dibujan no está medido | El HTML guardado no trae el CSS del portal | …tu captura o la corrida en vivo |
| En COSCO, la línea «no amplié la búsqueda: …» a veces repite «no pude ampliar la búsqueda» | Es solo el texto de `log.txt` | …molesta al leerlo |
| Si el «Book Now» de HYUNDAI no se pulsa (el clic falla, o al volver a leer la tarjeta ya no es la elegida), la reserva queda REVISAR «nave … no encontrada en HMM»: el motivo no lo describe bien; `log.txt` sí | Era así cuando el clic fallaba | …prefieres otro motivo |
| Los controles de `tapado.py` (30 palabras) y de `datos_en_informe.py` (50 filas) son pisos fijos | Choque 9 | …las planillas cambian mucho |
| HYUNDAI: la regla de «disponible» (`isAvail`) está copiada en `_JS_HMM_TARJETAS` y en `_JS_HMM_INDICE_NAVE` | La interfaz anterior la usa tal cual | …se retira la interfaz anterior, o cambia la regla |
| Si el «Book Now» de HYUNDAI deja algo en el portal (un borrador) al cortar después | No está medido; el clic ya existía antes de este encargo | …el portal muestra reservas a medias |
| El freno del modal de HYUNDAI no se midió | Hace falta el portal | …la corrida en vivo |
| Tras volver a buscar en HYUNDAI, si el filtro «Available Vessels Only» sigue marcado | No está medido | …la corrida en vivo |
| La interfaz anterior de HYUNDAI (`a.preview-area`) sigue con el texto de toda la tarjeta | No hay evidencia reciente de esa interfaz | …vuelve a aparecer |
| COSCO tiene una pestaña «Intended Vessel Voyage», que buscaría por nave y viaje | No es la opción de ampliar decidida | …decides usarla |
| ONE cierra sus ventanas tras la nueva búsqueda, como tras la primera (`_cerrar_modal_one`) | Es el mismo paso de búsqueda, no un clic nuevo | …decides que no |
| La prueba con el lanzador de prueba | La corres tú (arriba) | …me dices que corrió |
| Líneas de más de 120 en pruebas y mutaciones nuevas | Como las que ya había | — |
| Los residuales de `CICLO-cierre-de-frenos.md` que este encargo no tocó (MSC y su 502, el `button[type=submit]` de ONE, CMA y COSCO sin forma de número, la casilla de términos de MAERSK) | Sin evidencia nueva | …según ese informe |

**Lo que este encargo cierra del informe anterior:** HYUNDAI (el campo de la nave, que había frenado, y el modal, que
esperaba esa decisión); en MAERSK, pedir más salidas antes de cortar (su pregunta 3) y la salida sin «Book».

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v14**.
- **PASO 0 con sus cuatro valores** (CICLO, NOTA, DESCARTE y PREGUNTA): salieron CICLO (seis partes) y PREGUNTA (MSC,
  CMA y la prueba en el portal).
- **FRENAR cuando la decisión es de negocio y no de medición:** las preguntas de «Qué decides tú». MSC y CMA frenan por
  el FRENA SI del encargo, y se reportan con lo medido y sin tocar.
- **Re-medir contra HEAD antes de diseñar:** las listas guardadas se volvieron a leer con el programa de `4cae528`; y lo
  nuevo, con el de cada commit (`validar_head.py`).
- **Un chequeo de sintaxis no prueba el contrato:** que las pruebas pasen con páginas falsas no dice que el selector
  calce con la página real; `validar_head.py` lo corrió sobre el HTML guardado y cazó el de COSCO (pieza 4, 11).
- **Control positivo que aborta:** en las sondas que miden, y varios abortaron (pieza 4); no en `inventario.py`,
  `inventario_png.py`, `ocr_vocab.py` ni `anclas.py`, que cuentan o comprueban (pieza 1).
- **Todo salto silencioso lleva contador:** 0 HTML y 0 capturas descartados por nombre; las 2 listas de MAERSK sin su
  fila se midieron sin la nave, y se dice.
- **Todo registro es una hipótesis:** «hoy el programa mira solo la primera tanda» no era así en MAERSK ni en ONE
  (pieza 5).
- **El negativo tiene que morder:** en cada commit, el censo filtrado; al cerrar, el censo completo. Dos censos en la
  copia cazaron 3 mutaciones que no mordían.
- **El cambio y su guardián en la misma operación:** cada commit trae sus pruebas y mutaciones.
- **Fuente única:** `_hasta_donde_busque` y `NO_AMPLIA_MAS` para las cuatro; `_proxima_salida` y `_JS_TRAE_LA_NAVE`
  también para HYUNDAI.
- **Cada reemplazo afirma su viejo una vez; el EOL se preserva:** los parches abortan si el texto no calza; cada archivo
  commiteado es idéntico a su blob y sin CR.
- **Verificación adversarial:** cuatro revisiones del código (MAERSK; COSCO y ONE; HYUNDAI; COSCO, el campo) y dos de
  este informe con `CLAUDE.md`. La segunda cazó dos defectos del código, corregidos con su prueba y sus mutaciones
  (`2819828`, el freno del modal si aparece tarde; `f164fd7`, el «Book Now» de HYUNDAI sin volver a leer su tarjeta), un
  registro que faltaba (`a18f771`, MAERSK sin decir por qué dejó de ampliar), un conteo mal hecho (pieza 4, 12) y
  afirmaciones que el código no sostenía (el lector de MSC, el freno del modal).
- **Choques entre reglas:**
  1. **«La nave no está» contra el viaje.** La salida pedida es la nave con su viaje: MAERSK y COSCO amplían también si
     la nave está sin el viaje de la fila, y el corte del encargo 31 («sin-viaje») queda para después de ampliar. Es una
     lectura del encargo; responde la pregunta 3 del informe anterior («pedir más salidas antes de cortar»).
  2. **«Hasta que el portal no deje ampliar más» contra los clics.** En ONE, COSCO y HYUNDAI la opción es un rango de
     semanas: se elige de una vez el más largo, que trae también lo de los cortos, en vez de subir de a uno.
  3. **«Los únicos clics nuevos son los de ampliar» contra «vuelve a buscar».** Volver a buscar usa el botón de búsqueda
     que cada naviera ya pulsaba, y ONE cierra sus ventanas tras la nueva búsqueda como tras la primera: no son clics
     nuevos, son el mismo paso. Para cerrar su lista sin cambiar nada, ONE pulsa la opción que ya estaba elegida.
  4. **«Todo se prueba con el lanzador de prueba» contra lo que hago yo.** La corrida entra a los portales con las
     credenciales guardadas y resuelve sus validadores (el puzle de COSCO, el deslizador de CMA): eso no lo hago yo. La
     corres tú, con el candado cerrado, y yo mido lo que deje en `logs/`.
  5. **«MAERSK: si el viaje aparece solo en una salida que ya no se puede reservar».** Con viaje en la fila, así. Sin
     viaje (0 de las 72 filas, según `CICLO-cierre-de-frenos.md`), lo mismo si la nave está solo sin «Book» después de
     ampliar. El motivo lleva delante «MAERSK:» y la nave, como los demás de MAERSK; el texto decidido va entero.
  6. **La próxima salida en HYUNDAI.** El encargo decidió el campo; la próxima salida entre las que lo traen es tu regla
     de `CICLO-proxima-salida.md`, que HYUNDAI no aplicaba por falta del HTML de su lista, y el informe anterior la
     anunció junto con el campo.
  7. **La nota de ONE contra ampliar.** La nota del Excel dice «DEBE SELECCIONAR SIEMPRE 8 SEMANAS»; el encargo, ampliar
     con el selector de semanas. ONE sigue eligiendo 8 antes de buscar, y solo si la nave no está elige una más larga,
     si la hay. Es una lectura: la pregunta 4 lo deja en tus manos.
  8. **El FRENA SI del modal contra lo que se puede medir.** «Frena si marcar la opción no deja avanzar sin otro clic
     nuevo» solo se ve en el portal. No frené el encargo: el freno quedó como guarda en el código (si el modal sigue
     después del OK, aparezca al elegir la nave o más tarde, NO ENVIADA sin otro clic) y se mide en tu corrida.
  9. **«Un número fijo deja de morder» contra los controles de las sondas.** El de `tapado.py` pide al menos 30 palabras
     de las planillas (se bajó de 50, porque hay 48), y el de `datos_en_informe.py`, 50 filas (hay 72): son pisos fijos,
     no relativos. Sirven para que la sonda no corra sobre planillas vacías; si las planillas cambian mucho, hay que
     revisarlos.

Reglas del módulo: casos sintéticos; la sonda de secretos antes de cada commit; nada de `logs/` en el repo; los clics
nuevos antes de la guarda, solo los de ampliar y los del modal, cada uno por su texto; `test_candado` sin cambios; los
textos en español con tuteo.

## Entregable (pieza 8)

- **Este `.md`:** no se convirtió en página; se leyó como texto.
- **`CLAUDE.md` al día,** en el mismo commit.

**La red por commit:**

| Commit | Pruebas | Mutaciones | Pares |
|---|---|---|---|
| `4cae528` (base) | 379 | 952 | 1164 |
| `bf75525` (MAERSK) | 383 | 971 | 1190 |
| `4c34f83` (COSCO) | 387 | 987 | 1206 |
| `05cfdb7` (ONE) | 391 | 1005 | 1224 |
| `c95e5c0` (HYUNDAI: la nave y «Duration») | 399 | 1032 | 1254 |
| `d8cff13` (HYUNDAI: el modal) | 401 | 1038 | 1260 |
| `e8b027b` (COSCO: el campo por su lista) | 401 | 1043 | 1265 |
| `2819828` (HYUNDAI: el freno del modal, también tarde) | 401 | 1046 | 1268 |
| `f164fd7` (HYUNDAI: el «Book Now», con su tarjeta) | 401 | 1052 | 1274 |
| `a18f771` (MAERSK: por qué dejó de ampliar) | 402 | 1053 | 1275 |

Contada de git con `scratchpad\e26\red_por_commit.py`, del encargo 26.

**Gates.** En cada uno, la suite completa pasó con 0 cambios en los originales, y la sonda de secretos dio 0 sobre el
árbol y sobre lo agregado con `git add`. Todas las mutaciones de cada censo muerden.

| Commit | Suite completa | Censos filtrados (mutaciones y pares) |
|---|---|---|
| MAERSK, `bf75525` | 383 en verde, dos veces (antes y después de la revisión) | `TestMaersk`: 64 y 84 (antes de la revisión, 63 y 82); `TestProximaSalida`: 37 y 48, solo antes de la revisión |
| COSCO, `4c34f83` | 387 en verde | `TestCosco`: 85 y 101 |
| ONE, `05cfdb7` | 391 en verde | `TestOne`: 95 y 112; `TestFotoDeClicsGenericos`: 29 y 55 |
| HYUNDAI, la nave, `c95e5c0` | 399 en verde | `TestHyundai`: 52 y 60; `TestNaveCompleta`: 31 y 47; `TestEvidenciaListaHyundai`: 3 y 5; `TestCadaReservadorLaDeja`: 24 y 49; `test_cada_naviera_anota_el_desempate`: 5 y 7 |
| HYUNDAI, el modal, `d8cff13` | 401 en verde | `TestModalHyundai`: 20 y 21; `TestCadaReservadorLaDeja`: 24 y 49 |
| COSCO, el campo, `e8b027b` | 401 en verde | `TestCosco`: 90 y 106 |
| HYUNDAI, el modal tarde, `2819828` | 401 en verde | `TestModalHyundai`: 23 y 24 |
| HYUNDAI, el «Book Now», `f164fd7` | 401 en verde | `TestHyundai`: 58 y 66; `TestNaveCompleta`: 31 y 47; `TestFotoDeClicsGenericos`: 29 y 55 |
| MAERSK, por qué dejó de ampliar, `a18f771` | 402 en verde | `TestMaersk`: 65 y 85 |

- **COSCO, ONE y HYUNDAI se probaron antes en copias de simulación,** con la suite completa (401 pruebas, 1 falla que se
  corrigió) y el censo de sus mutaciones, mientras corría el gate anterior. Los tres commits de la revisión, también: en
  una copia, las 89 pruebas de sus clases y las anclas de sus mutaciones (una de MAERSK, `mk-viaje-corta-sin-la-nave`,
  perdió su ancla con el cambio y se ajustó antes del gate).
- **El gate de COSCO se detuvo dos veces:** por las mutaciones con nombres de prueba equivocados, y para incluir lo que
  pidió su revisión. Se volvió a correr entero. El de MAERSK se volvió a correr después de su revisión; su censo de
  `TestProximaSalida` no, porque la revisión no tocó lo que esas pruebas miran.
- **Los filtros incluyen las mutaciones que nombran una prueba cambiada:** `TestProximaSalida` las de
  `test_el_motivo_en_palabras`; `TestNaveCompleta` las de `test_las_navieras_de_javascript_con_el_ayudante`;
  `TestCadaReservadorLaDeja` las de `test_solo_ahi`.

**Censo completo** sobre `a18f771`, el último commit de código: 1053 mutaciones y 1275 pares mutación-prueba, sobre 402
pruebas. Los 1275 pares muerden, no hay pruebas sin mutación, el control (la copia sin mutar) pasa y hay 0 cambios en
los originales. Corrió el 27-09, de 01:14 a 01:44. Los censos completos sobre `d8cff13` y `e8b027b` se detuvieron
sin terminar, porque después vino otro commit de código.

## Qué decides tú

1. **Corre la prueba** con el lanzador de prueba (arriba) y avísame: con lo que deje en `logs/` mido las opciones de
   ONE, las tandas de MAERSK y el freno del modal de HYUNDAI.
2. **MSC:** mándame una captura o el HTML de la lista con la opción de ampliar a la vista, o su texto exacto. Hoy el
   HTML trae unas 12 semanas de entrada, pero el programa cuenta solo las tarjetas que se dibujan: si la opción destapa
   tarjetas ocultas, hace falta pulsarla.
3. **CMA:** lo mismo; o dime el texto exacto del botón que pulsa la Nota H23 («Mostrar más viajes») y si es esa opción,
   y entonces la repito hasta que no haya más.
4. **ONE:** la nota del Excel dice «siempre 8 semanas». ¿Amplío a más de 8 cuando la nave no está, como quedó, o me
   quedo en 8? Y si el selector no trae más de 8, ¿se queda ahí o se amplía moviendo la fecha de salida (otro clic)?
5. **HYUNDAI:** entre la 5.ª (con transbordo, llega a los 33 días) y la 6.ª (directa, 35), tu regla elige la 5.ª. ¿Está
   bien, o prefieres la directa?
6. **HYUNDAI:** ¿exige también el viaje de la fila en la «1st Vessel»?
7. **Fechas:** si la nave no aparece ni con la opción más larga, ¿se busca más lejos moviendo la fecha de salida en
   COSCO (su tercera pestaña), HYUNDAI y MSC? Sería otro clic antes de la guarda, y hoy no se hace.
