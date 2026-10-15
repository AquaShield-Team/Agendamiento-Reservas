# Encargo 67 · Las revisiones del encargo 66, MSC que vuelve a leer la tarjeta y CMA-CGM por el tramo que sale de Chile

**Base:** `C:\dev\Agendamiento Reservas` @ `14b8444` · árbol limpio al empezar.

En **Modo autónomo**, con `metodo-ciclo` v24 (el encabezado del archivo dice v24, la misma que la sesión tenía cargada).
Lo guardado en `logs/` se midió sin abrir ningún portal: el HTML de las listas, cargado en un Chromium sin red y sin sus
`<script>`, con el JavaScript del programa. Ningún valor de la planilla ni de una corrida va en este informe: de un
viaje, su forma (cada letra, A; cada cifra, 9).

## En resumen

- **Las dos revisiones, sin nada CRITICAL ni HIGH:** no se activó el primer FRENA. Las dos encontraron el mismo
  MEDIUM: el panel leía entero el cuerpo de un POST antes de mirar de dónde venía. Lo arreglé, con lo demás técnico que
  encontraron (abajo). Lo que queda son endurecimientos BAJA, documentados en el residual.
- **MSC vuelve a leer la tarjeta elegida justo antes del clic,** como ONE, HYUNDAI y CMA-CGM: el mismo «Vessel /
  Voyage», la misma ETD y la misma ETA, y un solo «Select» a la vista. Si cambió, NO ENVIADA sin pulsar, con el motivo
  y la lista en su evidencia. En las 302 tarjetas de las 11 listas guardadas, el clic nuevo pulsa la elegida, y con
  la ETD cambiada no pulsa nada.
- **CMA-CGM compara la nave y el viaje solo con el primer tramo de la ruta,** el que sale del POL: la nave que sale de
  Chile. No se activó el segundo FRENA: el campo se identifica en las 38 tarjetas de las 10 listas guardadas.
- **No se activó el tercer FRENA:** con la regla por campo, las 9 corridas con su lista guardada eligen la misma ruta
  que con la de HEAD, con el viaje de la fila y con la nave sola.
- **Sin clics nuevos;** el de MSC ahora puede no salir. **`test_candado` no cambió.**
  La suite pasa (828 OK) y, en el censo del área, de 710 pares muerden todos tras un repaso.

## Las revisiones

Cada una en su clon de `14b8444` dentro de la carpeta del encargo (`e67\clon_seg`, `e67\clon_cod`), solo con `main`,
sobre `git diff 2f68e0c..14b8444 -- AQUASHIELD.py tests/`. Las dos verificaron corriendo pruebas y sondas propias, y
dejaron su clon limpio y sin procesos vivos.

| Hallazgo | De | Severidad | Qué hice |
|---|---|---|---|
| `do_POST` lee entero el cuerpo antes de mirar si el pedido es ajeno; un `Content-Length` no numérico o negativo deja el hilo muerto o colgado; sin plazo, una conexión muda retiene su hilo | las dos | MEDIUM | arreglado: el origen antes del cuerpo, tope de 20 MB, 413 si no se entiende, plazo de 30 s por pedido |
| La renovación de la marca pierde la carrera entre dos pedidos a la vez | código | LOW | arreglado: compara con la marca que usó el pedido |
| `_palabras_del_viaje` dice tomarlas como COSCO y no deja fuera las de una letra: «070E / 071E» pedía un «/» | código | LOW | arreglado: como COSCO |
| `_ceder_al_previo` lee la marca con 1 s: con el equipo cargado, el apagar sale sin marca y no se atiende | código | LOW (plausible) | arreglado: con `PANEL_ESPERA_LARGA` |
| La descarga falla con un nombre de planilla fuera de latin-1 (un 200 y después un 500) | código | LOW | arreglado: `filename` en ASCII y `filename*` entero |
| `TestMarcaDeLaSesion` va después del `__main__` de `test_envio.py` | código | LOW | arreglado: el `__main__` al final |
| La marca la lee cualquier programa de este equipo, no solo la página | seguridad | LOW | documentado en `CLAUDE.md` |
| La página no trae una CSP de scripts, COOP ni `nosniff` | seguridad | LOW | residual |
| Ninguna prueba vigila `Cache-Control: no-store`, ni que la marca se compare con `hmac.compare_digest` | seguridad | LOW | la primera, arreglada (prueba y mutación); la segunda, residual |
| Dos cabeceras `Host`: `http.server` toma la primera, y «buena, ajena» pasaba | seguridad | LOW | arreglado |
| La cabecera `Server` dice la versión de Python; `urlopen` del lanzador sigue redirecciones | seguridad | INFO | residual |

- **Lo verificado por la de seguridad, que no encontró forma de entrar:** con el Chromium de Playwright y la página
  hostil abierta desde otro sitio, otro puerto y `localhost`, `fetch` (con o sin `no-cors`), formularios,
  `sendBeacon`, `<img>`, `<script>`, `prefetch`, un `<iframe>`, un `<iframe sandbox>`, `window.open`, `postMessage`
  y `window.name`, y un DNS rebinding aproximado (`--host-resolver-rules`): todo 403, o bloqueado por el navegador.
  26 formas de la ruta y de la línea del pedido: 403 o 404, nunca datos. Ninguna respuesta trae `Access-Control-*`.
  La marca no va a ningún log. Tras más de 100 pedidos rechazados, el panel seguía sin planilla, sin corrida y con
  `config.json` igual por hash.
- **Lo medido del MEDIUM:** un POST ajeno con 300 MB reales subió la memoria del panel en 269 MB antes de su 403; uno
  que anuncia 1.000 MB y manda 1 KB la subió 1.000 MB hasta que el cliente cerró. Una página web solo puede mandar
  bytes de verdad, y que la protección de red local de Chrome la frene no se midió.
- **Lo que la de código dejó como nota, sin severidad:** las pruebas de «sin el viaje» de ONE y de MSC prueban el
  ayudante y fijan su llamada, pero no corren `reservar_one` ni `reservar_msc` enteros con una página falsa (residual).

## MSC: la tarjeta, otra vez antes del clic

Hasta ahora `_JS_MSC_CLIC_NAVE` recibía la posición de la elegida y pulsaba el primer «Select» de esa tarjeta, sin
volver a leerla. Si MSC repintaba la lista entre la lectura y el clic, podía pulsar otra salida. Y si el clic fallaba,
`reservar_msc` seguía como si la nave no estuviera: REVISAR «nave … no está en MSC», que no era cierto.

- **El clic nuevo** recibe lo que `_JS_MSC_NAVES` leyó de la elegida (`i`, `nave`, `etd`, `eta`). En el mismo
  JavaScript vuelve a leer la lista con `_JS_MSC_NAVES`, y pulsa solo si en la posición `i` está la misma tarjeta: el
  mismo «Vessel / Voyage» (la nave y su viaje), la misma ETD y la misma ETA, con su «Select» a la vista y uno solo.
  Si no, devuelve por qué (`sin-tarjeta`, `otra`, `sin-select`, `varios-select`) y no pulsa nada.
- **Si no pulsó, NO ENVIADA** con `_msc_salida_ambigua` y el motivo de `_msc_no_pulse` («al volver a leer la lista
  justo antes de pulsar, …; no pulsé nada»), y la lista en `msc_f<fila>_itinerarios`. Si el JavaScript falla, lo
  mismo, con la falla. La evidencia la deja la misma función de siempre: `test_evidencia.test_solo_ahi` no cambió.
- **Medido en las 11 listas guardadas** (los HTML de la guarda de MSC, del 24-09 al 14-10, 302 tarjetas): cada
  tarjeta trae un solo «Select», y todas traen su «Vessel / Voyage» y su ETD (`select_msc.py`). Por eso el clic exige
  uno solo.
- **Por el camino real** (`verificar_msc_clic.py`, el JavaScript de la copia del encargo en un Chromium sin red, sobre
  las 11 listas): con lo que leyó de cada tarjeta, pulsa su «Select» una vez en las 302; con la ETD cambiada devuelve
  `otra` sin pulsar en las 302; con una posición que no existe, `sin-tarjeta` en las 11. El control: el clic de HEAD
  pulsa en las 11 sin volver a leer.

## CMA-CGM: el tramo que sale de Chile

### Qué campo es (el segundo FRENA)

Las 10 listas de «Route choices» guardadas (`cma_f7_rutas*.html`, del 27-09 al 14-10) traen 38 rutas a la vista. Cada
tarjeta, armada como la arma el programa (el `_JS_CMA_RUTAS` de la copia, que sube desde cada «Seleccionar» a la
vista), trae:

- **un resumen:** un `li.more-infos.vessel` con «Port Cut-off», «Buque principal», «Primer servicio» y «Ref. de
  viaje», cada uno en un `<dt>` con su `<dd>`;
- **los detalles** («Mostrar detalles», plegados, pero en la página): un `.route-wrapper` con un solo `ul.route`, que
  trae el `li` de la cápsula «POL», el primer tramo (`li.more-infos.vessel main-leg`, con su «Buque», su «servicio» y
  su «Ref. de viaje»), el transbordo y el segundo tramo, con otra nave y otro viaje.

Medido en las 38 (`campos_cma.py`, que compara en el navegador e imprime solo sí o no):

| | tarjetas |
|---|---|
| dos tramos | 38 |
| el primer tramo sale del POL | 38 |
| el POL está en Chile («…, CL»), en los detalles y en el resumen | 38 |
| el `main-leg` es el primer tramo | 38 |
| un solo «Buque principal» y un solo «Ref. de viaje» en el resumen | 38 |
| el primer tramo con un solo «Buque» y un solo «Ref. de viaje» | 38 |
| el «Buque principal» del resumen es el «Buque» del primer tramo | 38 |
| el «Ref. de viaje» del resumen es el del primer tramo | 38 |

- **El campo de la nave que sale de Chile:** el «Buque» del tramo que sigue al POL, y su viaje, el «Ref. de viaje» de
  ese tramo. En las 38 dicen lo mismo que el resumen, y el segundo tramo trae otra nave y otro viaje (de otra forma:
  AA99A9A99 en el primero, 9AA99A9AA en el segundo).
- **El texto de toda la tarjeta**, que miraba el programa hasta ahora, trae también la nave y el viaje del segundo
  tramo. Una ruta con la nave de la fila solo después del transbordo calzaba.
- **El control** (aborta): una tarjeta sintética de dos tramos, con la nave principal en el segundo, da «resumen =
  tramo 1: no» y «resumen = principal: sí».

### El cambio

`primerTramo` (en `_JS_CMA_RUTAS`) toma el único `ul.route` de `.route-wrapper`, su único `li` con la cápsula «POL» y
el `li` siguiente, que tiene que ser `li.more-infos.vessel`, con un solo «Buque» y un solo «Ref. de viaje», no vacíos.
La nave de la fila se compara con su «Buque» y el viaje con su «Ref. de viaje», con la regla de siempre
(`_traeLaNave`). Una ruta sin ese tramo legible no calza y se cuenta (`ilegibles`). Si ninguna calza y alguna fue
ilegible, el motivo de la nave que no está lo dice («no pude leer el primer tramo … de N de las M rutas»): sin eso,
«no disponible» podría no ser cierto. Lo que muestra el log de lo ofrecido (nave y viaje de cada ruta) sale del mismo
tramo.

### Las reservas guardadas (el tercer FRENA)

`medir_cma_campo.py`: el `_JS_CMA_RUTAS` de HEAD y el de la copia del encargo, por el camino real, sobre cada lista
guardada en el orden en que se guardó, como `_cma_seleccionar_itinerario` (la primera lista donde calza), con la nave
de la cabecera de la reserva en `log.txt` y el viaje de la fila de la planilla del equipo cuando la nave de esa fila es
la de la cabecera. Qué ruta pulsó cada uno lo dice un escuchador de clics puesto antes.

| Corrida | Llegó a la guarda | Con el viaje de la fila | Con la nave sola |
|---|---|---|---|
| 27-09 | sí | ninguna en las dos (el viaje de la fila de hoy no está; la de ese día ya no está) | la misma (1.ª) |
| 29-09 | sí | ninguna en las dos (ídem) | la misma (1.ª) |
| 30-09 | sí | la misma (3.ª) | la misma (3.ª) |
| 01-10 | sí | la misma (3.ª de la lista ampliada) | la misma |
| 02-10, 11:55 | sí | la misma (3.ª) | la misma |
| 02-10, 16:50 | sí | la misma (2.ª) | la misma |
| 02-10, 18:52 | sí | la misma (3.ª) | la misma |
| 08-10 | sí | la misma (3.ª) | la misma |
| 14-10 | sí | ninguna en las dos (el viaje que ya no se ofrecía) | la misma (3.ª) |

- **Las 6 medibles del encargo 66** (del 30-09 al 08-10) eligen con la regla por campo la misma ruta que con la de
  HEAD: ninguna queda NO ENVIADA. Ninguna ruta fue ilegible.
- **Las 5 EMITIDA del 21-09** no tienen HTML. El OCR del encargo 66 encontró el viaje de la fila junto a la nave en la
  captura de la lista, que muestra el resumen («Buque principal» y «Ref. de viaje»). Que el resumen sea el primer
  tramo está medido en las 38 tarjetas de después, no en las del 21-09: no se puede medir sin su HTML.
- **Las 2 del 25-09** no tienen la lista guardada, como en el encargo 66.
- **Los controles** (abortan): en una página sintética de dos rutas con la nave de la fila, la primera solo en su
  segundo tramo, HEAD pulsa la primera y la regla nueva la segunda; y con el viaje de la fila solo en el segundo tramo
  de la única ruta con la nave, HEAD la pulsa y la nueva no (`deLaNave` 1).

## Lo que cambió

- **`AQUASHIELD.py`:**
  - CMA-CGM: `primerTramo` en `_JS_CMA_RUTAS`, `ilegibles`, y el motivo que lo dice.
  - MSC: `_JS_MSC_CLIC_NAVE` con la relectura, `MSC_PULSADO`, `MSC_NO_PULSE`, `_msc_no_pulse`, `_msc_salida_ambigua`
    con `por_que`, y el corte en `reservar_msc`.
  - El panel: `SIN_LA_MARCA`, `CUERPO_MAX`, `CUERPO_FUERA_DE_MEDIDA`, `DESCARTE_MAX`, `PANEL_PLAZO_PEDIDO`,
    `_largo_del_cuerpo`, `_disposicion`; `do_POST` mira el origen antes del cuerpo; el plazo del manejador; dos `Host`
    en `_pedido_ajeno`; `_ceder_al_previo` con la espera larga; `renovarSesion(usada)` y `nombreDeDescarga` con
    `filename*`.
  - `_palabras_del_viaje` sin las de una letra.
- **Pruebas** (`test_clics`, `test_web`, `test_envio`, `test_ayudantes`): 11 pruebas nuevas, las de CMA
  con un DOM falso con la forma medida (resumen y tramos) y un selector de clases y descendientes; 30 mutaciones nuevas
  y 12 re-ancladas en `tests/mutaciones.py`; y el clic de MSC en `PERMITIDOS` de la foto de clics genéricos.
- **`CLAUDE.md`** y **`LEEME.md`**, al día.

## Decisiones que tomé solo

| Decisión | Por qué |
|---|---|
| CMA-CGM compara con el primer tramo de los detalles, no con el «Buque principal» del resumen | Es la nave que sale del POL, lo que pide el encargo. En las 38 medidas dicen lo mismo; si una ruta trajera primero un alimentador, el resumen diría el principal y no el que sale de Chile (no medido) |
| Una ruta sin el primer tramo legible no calza, y el motivo lo dice | Equivocarse hacia no reservar. Sin la cuenta, «no disponible» podría ser falso |
| Solo los rótulos en español («Buque», «Ref. de viaje») | Son los medidos en las 38. Con el portal en otro idioma, ninguna calzaría, y el motivo diría que no pudo leerlas |
| MSC exige el mismo «Vessel / Voyage», ETD y ETA, y un solo «Select» | Es lo que el programa leyó para elegir; un solo «Select» en las 302 medidas |
| Si el JavaScript del clic de MSC falla, NO ENVIADA | No se sabe si pulsó. Antes daba REVISAR «nave no está», que era falso |
| El POST de otro origen recibe el 403 sin que se lea su cuerpo; si es corto se descarta | Así una página ajena no ocupa memoria; descartar el corto evita que el cierre corte la respuesta |
| El de su origen sin la marca se lee antes del 403 | La pestaña de antes de un reinicio necesita ver el 403 para renovarse (la revisión de seguridad lo pidió así) |
| `CUERPO_MAX` 20 MB y 413 para un largo que no se entiende | La planilla del equipo pesa 13 KB; un solo código para «no dice cuánto» y «demasiado» |
| `PANEL_PLAZO_PEDIDO` 30 s | La página pide y recibe en milisegundos; es una hipótesis, sin medir con el equipo cargado |
| Las palabras del viaje como COSCO | Es lo que decía el docstring y lo que pidió el encargo 66 («la regla de MAERSK y COSCO») |
| La CSP de scripts, COOP y `nosniff`, al residual | Son BAJA, y la CSP no se probó con una corrida ni con la descarga: podría cambiar lo que ve el operador |
| La renovación lee siempre la página (sin atajo si otro pedido ya la renovó) | El atajo daba el mismo resultado: su mutación no habría mordido. Más simple |
| El clic de MSC, en `PERMITIDOS` de la foto de clics genéricos («primero-sin-filtro», `bs[0]`) | Pulsa el único «Select» de la tarjeta elegida, comprobado en el mismo JavaScript, como el de ONE, que ya está ahí. Escribirlo de otra forma para que la foto no lo vea sería esquivar al guardián |

## Verificación

- **La suite, sobre lo que se commitea:**
  828 pruebas OK en 732 s (`tests/correr.py`, lanzada aparte a la 01:23); la foto de los 5.254 originales, 0 cambios.
  Antes había pasado entera una vez (828 OK en 1.289 s), sin el caso de 10 MB de la prueba del POST ajeno (abajo).
- **Antes de tocar el repo,** en una copia limpia de `14b8444` con los mismos parches: las clases que cambié (395 OK)
  y el chequeo de las mutaciones (`mut_viejos.py`): 2.351 mutaciones y 828 pruebas, cada texto viejo una sola vez, las
  30 nuevas compilan, ninguna prueba sin su mutación, ningún id repetido: 0 problemas. El repo quedó igual byte a byte
  a esa copia (y en LF).
- **El censo del área** (`alcance_e67.py`, `censo_e67.py`, lanzado aparte), sobre el repo:
  - **Qué entró:** las 30 mutaciones del encargo y las 12 re-ancladas; las que caen a 15 líneas o menos de una línea
    cambiada de `AQUASHIELD.py` (178 líneas cambiadas); y las que nombran una prueba cuyo camino cambió (la elección de
    MSC y CMA-CGM, el panel, la página, la regla del viaje y de la nave, `test_candado` y las de `test_datadome` que
    corren `reservar_cma`).
  - **515 mutaciones, 710 pares y 217 pruebas: el control pasa, y muerden 709.** Ningún par se acercó al plazo del
    censo (el más largo, 67 s) y el equipo no entró en reposo (0 eventos 506 y 507). Los 4 motivos `TimeoutExpired`
    son el plazo de la propia prueba (`hijo.wait` de `test_instancia_previa_ociosa_se_apaga`).
  - **La que no mordía,** `e67-post-ajeno-se-lee-entero`: un caso incompleto mío. La prueba anunciaba 50 MB, más que
    `CUERPO_MAX`, y el tope ya impedía leerlos. Le sumé un POST ajeno de 10 MB anunciados, que solo el origen evita
    leer. **El repaso** (`correr.py --mutaciones --filtro test_un_post_de_otro_origen_no_se_lee`): el control pasa y
    muerden sus 2 mutaciones.
  - En el censo y en el repaso, la foto de los 5.254 originales: 0 cambios.
- **El panel en un navegador de verdad** (el de la app, con un panel de prueba de la copia en el puerto 40411, con una
  configuración sintética): con una planilla sintética llamada «Reservas – octubre 🐟.xlsx», la descarga dio 200, el
  nombre entero (leído de `filename*`) y 10.718 bytes de xlsx; después de apagar y levantar otro panel en el mismo
  puerto, la pestaña con la marca de antes mandó tres pedidos a la vez, y los tres se renovaron y pasaron. Los 403 de la
  consola fueron 12, los del reinicio y los de la prueba, y no crecieron.
- **El barrido de datos reales** (`barrido_diff.py`) y la sonda de secretos, antes de cada commit: abajo, en «El repo».

## Residual

- **La CSP de scripts** (`script-src 'self'` y lo demás que propuso la revisión de seguridad),
  `Cross-Origin-Opener-Policy` y `X-Content-Type-Options: nosniff` en la página. La revisión la probó cargando la
  página, el sondeo, el tema, las credenciales y una planilla, sin violaciones; no con una corrida ni con la descarga.
  Se reabre si lo encargas, con la prueba de esas dos en el navegador.
- **La marca protege del navegador, no de otro programa de este equipo,** que puede leer `/` como el lanzador. Se
  reabre si el equipo pasa a tener más de un usuario de Windows.
- **Ninguna prueba vigila que la marca se compare en tiempo constante** (`hmac.compare_digest`): no se puede medir de
  forma funcional, y quien podría medir tiempos ya puede leer `/`. Se reabre con una foto del texto fuente, si lo pides.
- **La cabecera `Server`** dice la versión de Python, y el `urlopen` del lanzador sigue redirecciones: un programa
  hostil en los puertos 8765 a 8768 podría hacerle pedir otra dirección, sin datos que robar. Ya era así.
- **El descarte del cuerpo corto de un POST ajeno no tiene mutación:** que el cierre sin leer corte la respuesta
  depende de Windows y del momento, y una prueba no lo ve siempre.
- **Las pruebas de «sin el viaje» de ONE y de MSC** no corren el reservador entero. Se reabre si lo encargas.
- **Firefox y Safari no se probaron;** tampoco la protección de red local de Chrome.
- **Las 5 de CMA-CGM del 21-09** se midieron por OCR del resumen; que el resumen sea el primer tramo, en las 38 de
  después.
- **`PANEL_PLAZO_PEDIDO`** (30 s) es una hipótesis: se reabre si un pedido legítimo se corta con el equipo cargado.

## FRENA SI

- **La revisión de seguridad, CRITICAL o HIGH:** no; un MEDIUM (arreglado) y BAJA.
- **No identificar en los HTML el campo de la nave que sale de Chile:** sí se identifica, en las 38 tarjetas.
- **Una reserva guardada con el viaje de su fila que quedaría NO ENVIADA con la comparación por campo:** ninguna de las
  medibles; las no medibles, arriba.

## Premisas

- «MSC no vuelve a leer la tarjeta, ONE, HYUNDAI y CMA-CGM sí»: **confirmada.** CMA-CGM lee y pulsa en el mismo
  JavaScript.
- «Una página de otro sitio no puede leer la marca» (encargo 66): **confirmada para páginas web, y matizada:** cualquier
  programa de este equipo la lee (revisión de seguridad). Va en `CLAUDE.md`.
- El docstring de `_palabras_del_viaje` («como las toma COSCO, que deja fuera las de una letra») **no era cierto**: no
  las dejaba fuera. Ahora sí.

## Defectos de instrumento (míos)

- **El volcado del JavaScript se escribió encima de su propio script** (`volcar_js.py`): tomaba la ruta de salida de
  `sys.argv` después de cargar el programa, y `soporte.cargar()` deja `sys.argv` sin argumentos. Ahora la toma antes y
  exige que esté en `e67\t`.
- **La primera lectura de las tarjetas de CMA-CGM dio 0:** tomé el `.wrap-card` por la tarjeta, y cada ruta trae dos
  (el resumen y los detalles), y dos botones (el «Seleccionar» a la vista y el «Deseleccionar» oculto). La rehice con el
  `_JS_CMA_RUTAS` del programa, que sube desde cada botón a la vista. Su control, con una sola tarjeta, tampoco servía:
  el programa sube hasta el `body` y toma el botón por la tarjeta. Lo rehice con dos dentro de un `<main>`.
- **Un `sed` no cambió la raíz de `mut_viejos.py`** (la herramienta Bash junta los pares de barras invertidas), y su
  primera corrida chequeó el repo, solo leyéndolo, en lugar de la copia. Lo cambié con Edit.
- **Un arreglo por heredoc tampoco llegó** (la misma causa): corrí `aplicar_pruebas_panel67.py` con el reemplazo viejo
  sobre una copia, que quedó con una línea en blanco de más. Arreglé el script con Edit, y el repo recibió la cadena
  entera rehecha sobre copias limpias (`src3` a `src5`), igual byte a byte a la última probada.
- **Un nombre de clase equivocado** en un comando de `unittest` (`TestTraeLaNave`; es `TestNaveCompleta`): un error de
  carga entre 152 pruebas, sin otro efecto.
- **El lanzador del censo comparaba la carpeta en su forma corta (8.3) con la larga** y abortó antes de empezar. Ahora
  compara con `resolve()`.
- **Antes de tocar el repo corrí solo las clases que cambié (395 pruebas),** y no la foto de las formas de clic
  genérico (`test_clics.TestFotoDeClicsGenericos`), que lee todo el programa. La encontró el control del primer censo,
  a los 26 minutos: el clic nuevo de MSC pulsa `bs[0]`, la forma «primero-sin-filtro». La agregué a `PERMITIDOS` (ver
  «Decisiones que tomé solo») y, antes del censo, corrí la suite entera.
- **Un caso incompleto en la prueba del POST ajeno:** anunciaba 50 MB, más que `CUERPO_MAX`, y con eso la mutación que
  lee entero el cuerpo ajeno no se veía (el tope ya impedía leerlo). El censo la marcó como la única que no mordía; le
  sumé un caso de 10 MB, y en el repaso muerde.
- **El primer monitor del censo buscaba el PID en la columna equivocada de `ps -W`** (la de Cygwin, no la de Windows):
  anunció el fin a los 14 s, con el censo vivo. Lo comprobé por PID en PowerShell y lo rearmé con la columna de
  Windows y un control al empezar.

## Re-medir

Todo desde `…\scratchpad\e67`, con `source entorno_e67.sh` (TEMP, TMP y TMPDIR en `e67\t`):

- `estructura_cma.py` (el árbol de cada tarjeta, enmascarado) y `campos_cma.py` (la tabla de los 38).
- `medir_cma_campo.py` (las 9 corridas, HEAD contra la copia).
- `select_msc.py` (un «Select» por tarjeta) y `verificar_msc_clic.py` (el clic nuevo en las 302).
- `mut_viejos.py <raíz> e67` (cada texto viejo una vez, las nuevas compilan, cada prueba con su mutación).
- `alcance_e67.py <raíz>` y `lanzar_censo_e67.py <salida> <raíz>` (el censo del área).
- `largas.py`, `barrido_diff.py`.

## NO retroceder

- **CMA-CGM no vuelve a comparar con el texto de toda la tarjeta:** trae la nave y el viaje del segundo tramo.
- **MSC no vuelve a pulsar la i-ésima sin leerla,** ni a seguir como «nave no está» si el clic no salió.
- **El panel no vuelve a leer el cuerpo de un POST antes de mirar su origen,** ni a esperar un pedido sin plazo.

## Reglas aplicadas

`metodo-ciclo` v24, en Modo autónomo:

- **Las reglas:**
  - el control positivo que aborta, en cada sonda;
  - el camino real: el JavaScript del programa, no una paráfrasis;
  - todo salto lleva su contador (`ilegibles`, las no medibles);
  - el negativo que muerde, por el censo;
  - cada reemplazo, una sola vez, y en LF;
  - el cambio y su guardián juntos;
  - el residual declarado;
  - las premisas refutadas.
- **El Modo autónomo:** las dos revisiones las lancé yo, cada una en su clon, y los arreglos van en la misma corrida.
- **Choque:** la regla de ECC de lanzar revisiones sola cede ante las reglas permanentes, salvo en Modo autónomo, que es
  este caso. Sin otro choque.

## El repo

- `b1d5fe2` fix: MSC vuelve a leer la tarjeta, CMA-CGM por el tramo que sale de Chile, y lo de las revisiones
  (`AQUASHIELD.py` y `tests/`).
- El de este informe, `CLAUDE.md` y `LEEME.md` (docs), el siguiente.

Los dos llevan de autor y de committer el correo noreply del repo, y la sonda de secretos dio 0 antes de cada uno.

El barrido de datos reales (`barrido_diff.py`, con la máscara de la planilla, los `log.txt` y `config.json`, y su
control) sobre las líneas agregadas de cada commit: en los dos, solo líneas con la palabra del país, «Chile», que la
máscara vigila porque va en el nombre de una nave de un `log.txt` (en el arreglo, 6; el programa publicado ya la
nombra en 95 líneas), y ningún otro valor.

No subí nada: el repo es público, así que el push lo hace Marcelo (el bloque, en el mensaje de cierre). En GitHub,
`main` y `estable` están en `14b8444`, la base de este encargo (medido con `ls-remote` al cerrar): los equipos de los
colegas corren hoy el código del encargo 66, con el POST que se lee antes de mirar de dónde viene.
