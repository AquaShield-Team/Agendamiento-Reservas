# CICLO · La cola de tres ítems decididos

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-25 · **Método:** skill `metodo-ciclo` v13 ·
**Base:** `9051f43` (último de código: `6339e38`) · **Commits** (locales, sin push; el repo no tiene remoto): uno por
ítem, `2825153` (ítem 1), `4b0182b` (ítem 2) y `be6a86f` (ítem 3), y el de este informe.

> Sin datos reales. `logs/`, la planilla y `config.json` se midieron en solo lectura, con sondas que imprimen conteos,
> etiquetas de interfaz, formas enmascaradas (letras → A, dígitos → 9) y diferencias en días. Nunca salen naves,
> puertos, fechas de salida, contratos ni el nombre del operador.

## Los tres ítems

| # | Ítem | Resultado | Commit | Freno |
|---|---|---|---|---|
| 1 | La tarjeta calza con la nave solo si trae todas sus palabras, en las seis | Hecho | `2825153` | No se cumple en lo medido: ONE, MSC, COSCO y MAERSK, en el HTML de sus listas; HYUNDAI y CMA, en sus elecciones de `logs/` (no hay HTML de su lista) |
| 2 | Entre salidas del mismo día, la de menor tiempo de tránsito | Hecho | `4b0182b` | No se cumple: el tránsito se lee sin ambigüedad en las cuatro |
| 3 | CMA guarda la pantalla al terminar la espera de «Validar ruta» | Hecho | `be6a86f` | — |

Los tres pasaron por una revisión adversarial antes de su commit. Los ítems 1 y 2 tuvieron tres enfoques (la regla y sus
bordes, el candado y la guarda, y la red de pruebas) y el 3, dos (el flujo y la red). Lo que encontraron las revisiones
está en cada ítem y en los defectos de instrumento (pieza 4).

## Ítem 1 · La nave con todas sus palabras

**El freno, medido.** Una naviera frena si muestra la nave recortada o abreviada, de modo que la nave completa no
pueda calzar nunca. En lo medido no pasa en ninguna:
- **Las listas guardadas** en la corrida del 25: ninguna tarjeta trae «…» ni «...».
  - ONE (32 tarjetas): el enlace de la nave trae la nave entera con su viaje, con la misma forma de viaje que la planilla.
  - MSC (27): «Vessel / Voyage» trae la nave entera y su viaje.
  - COSCO (4): cada tramo trae su nave con su viaje.
  - MAERSK (4 con salida): «Vessel/voyage» trae la nave y su viaje.
- **Las elecciones de `logs/`** (9 carpetas, 0 descartadas):
  - COSCO: en las 15 elecciones, la nave de la fila estaba entera en una sola de las naves de su itinerario.
  - CMA: la nave de la planilla tiene una palabra, sin prefijo de naviera, y calzó entera en la tarjeta.
  - HYUNDAI: hay 8 elecciones, las 5 de la corrida del 21 y una en cada una de las otras tres corridas (la del 24 y las
    dos del 25). En todas, a la tarjeta le falta la segunda palabra de la nave, y ninguna palabra de la tarjeta empieza
    siquiera con la misma letra que esa segunda palabra. Es otra nave, no un recorte, como dijo Marcelo.
  - ONE: su log no guarda el texto de la tarjeta; se midió en el HTML.

**Cómo calza ahora cada naviera:**

| Naviera | Con qué compara | Regla | Antes (hasta `9051f43`) |
|---|---|---|---|
| MSC | El campo «Vessel / Voyage» de la tarjeta | Todas las palabras (`_trae_la_nave`) | Igual, pero sin palabras de nave calzaba con todas |
| ONE | El enlace de la nave de la tarjeta | Todas las palabras | La nave entera, la nave sin su última palabra o esa última palabra sola, en cualquier parte de la tarjeta |
| COSCO | Una sola de las naves de «Vessel / Voyage» (`_cosco_calzan`) | Todas las palabras de la nave y del viaje; si ninguna nave del itinerario las trae, basta con las de la nave | Las mismas, en el texto de toda la fila: podían salir de dos naves distintas |
| MAERSK | El valor de «Vessel/voyage» | Todas, en orden | Todas, en orden, en toda la tarjeta: un destino con el nombre de la nave calzaba |
| HYUNDAI | El texto de la tarjeta | Todas las palabras | Todas, **o solo la primera**, que en la planilla es el prefijo de la naviera |
| CMA | El texto de la tarjeta | Todas las palabras; una nave comodín («LIBRE», «AUTO», «-») no aporta palabras, así que no calza con ninguna | Todas, o todas menos los prefijos de naviera |

- **Una fila sin palabras de nave no calza con ninguna tarjeta, en las seis.** MSC, COSCO y ONE calzaban con todas (ONE,
  con una nave de una sola letra o un guion); HYUNDAI, MAERSK y CMA ya exigían al menos una palabra.
- Si ninguna calza, cada naviera sigue su camino de nave no encontrada, que no cambió.
- **HYUNDAI y CMA siguen comparando con toda la tarjeta:** no hay HTML de su lista para ubicar el campo de la nave. Desde
  `50e3f04` la guardan (`hmm_f<fila>_naves` y `cma_f<fila>_rutas`).
- El hallazgo 2 de `CICLO-proxima-salida.md` (ONE toma la última palabra por el viaje) queda cerrado.

## Ítem 2 · El desempate por el menor tiempo de tránsito

**El freno, medido** en las listas del 25: cada tarjeta trae un solo tiempo de tránsito.

| Naviera | Tarjetas | Qué muestra | Contra la llegada menos la salida | Cómo lo lee el programa |
|---|---|---|---|---|
| ONE | 32 | «N day(s)» | Igual en las 32 | Llegada menos salida (sus dos fechas textStyle-h5) |
| MSC | 27 | «Est T.T» | Igual en las 27 | ETA menos ETD |
| COSCO | 4 | El número y «Days» | Igual en las 4 | Llegada menos salida de su tarjeta |
| MAERSK | 4 con salida | «Transit time», con días y horas | En las 4, el mostrado da 4 horas menos que la llegada menos la salida: cada fecha va en la hora local de su puerto | Su «Transit time» |

- **La regla** vive en el ayudante compartido: `_proxima_salida(salidas, desde, transito)` y `_menor_transito`. Entre las
  del mismo día, la de menor tránsito si todas lo traen legible (leído y mayor que cero) y el menor no se repite; si no,
  NO ENVIADA con la lista, como antes. Los transbordos no cuentan.
- **El motivo de la NO ENVIADA** dice ahora por qué el tránsito no desempató: «y no pude leer el tiempo de tránsito de N
  de ellas» o «y N de ellas tienen el menor tiempo de tránsito, T».
- **Cuando el tránsito desempata, `log.txt` lo dice:** cuántas salían ese día, el tiempo de la elegida y el de las otras.
- **Cada lectura exige que la tarjeta no deje dudas,** o el tránsito no se lee: en ONE y COSCO, exactamente dos fechas
  (salida y llegada); en MSC, una sola ETA. Medido: las 32, las 4 y las 27 cumplen.
- **Cuánto resuelve**, medido en `CICLO-cola-siete-items.md` sobre las mismas listas: los 2 empates de COSCO y 6 de los 8
  de ONE. Los otros 2 de ONE siguen NO ENVIADA: tardan lo mismo.

## Ítem 3 · CMA y «Validar ruta»

- Al terminar la espera que ya existía tras «Validar ruta» (hasta 12 s), y después de leer su aviso, CMA deja
  `cma_f<fila>_validar_<modo>`: la captura de la ventana y el HTML, respondiera o no el portal.
- Va después de leer el aviso para que esa lectura, que decide si la reserva sigue, prueba el otro destino o queda en
  REVISAR, ocurra en el mismo instante que antes.
- Sin clics, teclas, esperas ni navegación. Si guardarla falla, lo avisa y la reserva sigue.
- `<modo>` es `puerto`, `ramp` o `ramp_separado`: hay hasta dos intentos por reserva, y cada uno deja la suya.
- Lo que viene después del aviso se atrasa lo que tarda la evidencia (la captura y el HTML de la página y de cada
  marco), como con el panel Reefer y el Remark de HYUNDAI.
- Si el clic o la espera fallaron (estado «error»), la evidencia también queda. Con el botón deshabilitado, ese intento
  no deja evidencia, porque no hubo pulsación ni espera: en `puerto` pasa al intento siguiente, y en `ramp` o
  `ramp_separado` la reserva queda en REVISAR.

## Expectativas que cambiaron (antes → ahora)

| Commit | Prueba | Antes | Ahora |
|---|---|---|---|
| Ítem 1 | `test_clics.TestOne.test_js_tarjetas_de_la_nave_con_su_salida` | «ONE NAVE UNO SC001E» calzaba con las tarjetas 0, 2, 3 y 4 (la 3 y la 4 son la misma nave con otro viaje) | Solo con la 0 y la 2. Casos nuevos: sin viaje, otra nave con las mismas primeras palabras, una letra, el viaje solo, la barra, un puerto, y las minúsculas en la fila y en el enlace |
| Ítem 1 | `test_clics.TestFotoDeClicsGenericos.test_ningun_clic_generico_nuevo_antes_de_la_guarda` | («reservar_one», «_JS_ONE_TARJETAS_NAVE», «ultimo-por-posicion»): 2 | Sin esa entrada: ONE ya no toma la última palabra aparte |
| Ítem 1 | `test_clics.TestMaersk.test_js_salidas_lee_la_salida_y_si_se_puede_reservar` | — | Caso nuevo: una salida de otra nave que va a un puerto con el nombre de la pedida ya no calza |
| Ítem 1 | `test_evidencia.PaginaRutasCma` (soporte) | Reconocía la lectura de CMA por «sigToks» | Por «getCard(»; sus expectativas no cambian |
| Ítem 2 | `test_clics.TestOne.test_js_tarjetas_de_la_nave_con_su_salida` | {i, calza, salida, nave, botones} | Más «llegada»; con una o con tres fechas, vacía |
| Ítem 2 | `test_clics.TestMaersk.test_js_salidas_lee_la_salida_y_si_se_puede_reservar` | {i, calza, viaje, salida, book} | Más «transito» |
| Ítem 2 | `test_clics.TestCosco.test_js_lista_lee_la_salida_y_la_llegada_de_la_tarjeta` | — | Caso nuevo: con tres fechas, sin llegada (antes, la segunda) |
| Ítem 2 | `test_clics.TestOne.test_reservar_one_elige_la_proxima_salida` | `_proxima_salida(_one_salidas(tarjetas), desde)` | `…, desde, _one_transito)` |
| Ítem 2 | Las cuatro NO ENVIADA por empate (TestOne, TestMsc, TestCosco, TestMaersk) | El motivo terminaba en «…la próxima salida desde el …» | Sigue con «, y no pude leer el tiempo de tránsito de 2 de ellas»: sus tarjetas sintéticas no lo traen |
| Ítem 3 | `test_evidencia.TestCadaReservadorLaDeja.test_solo_ahi` | `reservar_cma` la dejaba una vez (su guarda) | Dos |

- **`test_candado` no cambió** en ningún commit, ni la guarda (de `_evidencia_antes_de_la_guarda` solo cambió el
  docstring), ni el lector de la planilla.
- No hay clics, teclas, esperas ni navegación nuevos. La foto de clics genéricos solo perdió la entrada de ONE.
- Las demás elecciones de la regla no cambian: sin tránsito, el empate queda empate.

**La red, por commit:**

| Commit | Pruebas | Mutaciones | Pares |
|---|---|---|---|
| `9051f43` (base) | 317 | 667 | 811 |
| `2825153` (ítem 1) | 323 | 691 | 836 |
| `4b0182b` (ítem 2) | 336 | 737 | 888 |
| `be6a86f` (ítem 3) | 339 | 744 | 897 |

- Frente a la base no se borró ninguna mutación.
- 9 se pusieron al día en el ítem 2 porque su texto viejo cambió: las llamadas al ayudante de las cuatro navieras.
- En el borrador del ítem 1, 2 mutaciones de COSCO miraban el texto de toda la fila; antes del commit las reemplazaron las
  de `_cosco_calzan`.
- Una mutación nueva del ítem 2, `motivo-transito-de-todas-las-salidas`, se ancló con la línea anterior antes del commit,
  porque `_anotar_desempate` repite su línea (defecto 7).

## Veredicto por naviera: ¿lista para una emisión real de prueba?

| Naviera | Veredicto | Qué le falta |
|---|---|---|
| **MSC** | **Casi lista** | Una corrida con candado cerrado que busque desde hoy (`8927e1f`), para ver en vivo la próxima salida y el calce por su campo. Tiene forma medida de confirmación: puede llegar a EMITIDA |
| **ONE** | **Casi lista** | Una fila cuya nave esté en la búsqueda, escrita como en el enlace de su tarjeta, que llegue a Review Booking. El desempate resuelve 6 de sus 8 empates medidos. Tiene forma medida |
| **COSCO** | Casi lista para la prueba con candado cerrado; no para emitir | El desempate resuelve sus 2 empates medidos, así que puede llegar a su guarda. Sin forma medida de confirmación, tras el envío queda en ENVIADA – REVISAR EN PORTAL |
| **HYUNDAI** | No | Ya no calza por la primera palabra. Falta su lista (`hmm_f<fila>_naves`) para calzar por el campo de la nave y aplicar la próxima salida, y medir el modal «Alternate Vessel Option» que acepta antes de la guarda |
| **CMA** | No | «Validar ruta» sin respuesta: ahora deja `cma_f<fila>_validar_<modo>` para ver por qué. Falta su lista (`cma_f<fila>_rutas`) para calzar por el campo de la nave y aplicar la próxima salida. Sin forma medida, nunca llega a EMITIDA |
| **MAERSK** | No | Una fila con una salida con «Book», para llegar a la revisión y medir la casilla de términos (FRENO). Busca desde mañana y lo avisa en pantalla y en `log.txt` (`fc7de54`) |

## Qué fila elegir en cada naviera para la próxima prueba con candado cerrado

- Una fila por naviera en CONSOLIDADO, con el lanzador normal, nunca el de emisión.
- Las columnas de la planilla no cambian. Sin día de carga, ONE, MSC y COSCO cuentan desde hoy y MAERSK desde mañana;
  HYUNDAI y CMA toman la primera tarjeta que calza.
- Elige cada nave en el portal el mismo día de la corrida, en la ruta de la fila, y escríbela en la fila **con todas las
  palabras con que el portal la muestra**:
  - una palabra que el portal no muestra deja la fila en REVISAR por nave no encontrada («no encontrada» o «no está»,
    según la naviera);
  - con una de menos, puede calzar también con otros viajes de esa nave.

| Naviera | Qué fila elegir | Qué evidencia va a dejar |
|---|---|---|
| MSC | Cualquier nave de su lista para esa ruta, con su prefijo («MSC …») | `msc_f<fila>_guarda` (Summary): la elección en vivo, desde hoy |
| ONE | La nave como la trae el enlace de su tarjeta: nombre y viaje. Si su día trae varias tarjetas, el tránsito elige; si tardan lo mismo, NO ENVIADA | `one_f<fila>_guarda` (Review Booking), o `one_f<fila>_detenida` con la lista; en `log.txt`, «N salidas de la nave salen el …: elijo la de menor tiempo de tránsito» |
| COSCO | Una nave con su itinerario; si hay dos el mismo día, el tránsito elige | `cosco_f<fila>_guarda`, o `cosco_f<fila>_itinerarios` si empatan; la línea del desempate en `log.txt` |
| MAERSK | Una nave con una salida que traiga «Book» (el plazo «Gate-in deadline» vigente). En la corrida del 25, solo la salida que zarpaba 9 días después lo traía | `mk_f<fila>_guarda`: la revisión, con la casilla de términos por identificar |
| HYUNDAI | Cualquier nave de su lista, con el prefijo y el nombre («HMM …»), como la muestra el portal | `hmm_f<fila>_naves` (la lista, para el campo de la nave y la próxima salida), `hmm_f<fila>_remark` y `hmm_f<fila>_guarda` |
| CMA | Cualquier nave con ruta ese día | `cma_f<fila>_rutas` (la lista), `cma_f<fila>_validar_<modo>` (lo que deja «Validar ruta»), los del panel Reefer y `cma_f<fila>_guarda` |

**Después de la corrida, lo primero:** revisa que ninguna fila haya quedado en EMITIDA ni en ENVIADA – REVISAR EN
PORTAL, y que no haya capturas `*_confirmado`, las que quedan tras pulsar el botón final. Después, los HTML nuevos:
`hmm_f*_naves`, `cma_f*_rutas`, `cma_f*_validar_*` y la revisión de MAERSK, si llegó.

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\correr.py --mutaciones --filtro nave
python tests\correr.py --mutaciones --filtro calce
python tests\correr.py --mutaciones --filtro transito
python tests\correr.py --mutaciones --filtro proxima
python tests\correr.py --mutaciones --filtro anota
python tests\correr.py --mutaciones --filtro cma-validar
python tests\correr.py --mutaciones --filtro test_solo_ahi
python tests\correr.py --todo
```

Las sondas son de solo lectura y viven fuera del repo. Cada una aborta si su control sintético no da lo esperado:
- **La nave recortada:** en cada elección y cada lista «ofrecidos» de `logs/`, si el texto trae todas las palabras de
  la nave de la fila, le faltan solo prefijos, trae una recortada (una es prefijo de la otra, 3 letras o más) o tiene
  puntos suspensivos. En los HTML de las listas, los «…» y la forma enmascarada del campo de la nave.
- **El detalle de las que no calzan:** su forma enmascarada, y para cada palabra que falta, la distancia de edición y el
  prefijo común con las del texto.
- **El campo de la nave:**
  - en COSCO, emulando `campo(fila, 'Vessel / Voyage')`, cuántas naves lee cada fila y si la de la fila queda dentro de
    una;
  - en MAERSK, la forma del valor de «Vessel/voyage»;
  - en los logs de COSCO, si la nave de la fila estaba dentro de una sola de las naves elegidas.
- **El tránsito:** cuántos valores trae cada tarjeta, y la diferencia entre el tránsito mostrado y la llegada menos la
  salida, en días (MAERSK, en horas). Las etiquetas de MSC se imprimen solo si son de interfaz.
- **Los conteos de las lecturas:** fechas por tarjeta de COSCO y «ETA» por tarjeta de MSC.
- **La red por commit y las piezas cambiadas:** leídas de git, con `ast`.

## NO retroceder (pieza 2)

- **No vuelvas a aceptar una tarjeta por una parte de la nave:** ni la primera palabra (en la planilla de HYUNDAI es el
  prefijo de la naviera), ni la nave sin su última palabra, ni esa palabra sola, ni la nave sin sus prefijos.
- **No vuelvas a comparar con toda la tarjeta donde el campo de la nave está medido** (ONE, MSC, COSCO y MAERSK): la
  tarjeta trae puertos, servicios y la otra nave del transbordo.
- **No dejes que una fila sin palabras de nave calce:** `all([])` es verdadero, y se elegía cualquier salida.
- **No saques el tránsito del ayudante compartido,** ni dejes que decida uno que no se lee, uno de cero o menos, o uno
  que venga de una tarjeta con dos ETA o con tres fechas.
- **No pongas la evidencia de «Validar ruta» antes de leer el aviso:** atrasaría la lectura que decide el camino.

## Universo y cobertura (pieza 3)

- **`logs/`:** 9 carpetas de corrida, las 9 con `log.txt`; 0 descartadas. Elecciones leídas: COSCO 15, MSC 8, MAERSK 8,
  CMA 8, HYUNDAI 8 y ONE 5. Listas de naves ofrecidas cuando no se encontró la nave: 1 (COSCO).
- **Las listas del 25:** ONE 32 tarjetas, MSC 27, COSCO 4 y MAERSK 5. En el tránsito, 1 descartada: la tarjeta de
  MAERSK que estaba cargando, sin salida ni «Book».
- **La planilla del panel:** 7 hojas, 0 sin leer; la forma de la nave de cada naviera, por conteo.
- **Git:** 31 piezas de nivel superior de `AQUASHIELD.py` entre `9051f43` y `be6a86f` (20 cambiadas y 11 nuevas),
  medidas con `ast`.
  - Ninguna es del lector de la planilla.
  - De la evidencia de la guarda, solo el docstring de `_evidencia_antes_de_la_guarda`; su cuerpo y su firma son
    idénticos.
- **No medido:**
  - el campo de la nave en las listas de HYUNDAI y CMA: no hay HTML;
  - si un nombre de la planilla con puntuación («A.», paréntesis) calzaría en las cinco que no la quitan;
  - el modal «Alternate Vessel Option» de HYUNDAI;
  - «Validar ruta» en una corrida nueva.

## Defectos de instrumento cazados (pieza 4)

1. **La prueba del JavaScript de CMA pasaba igual con el código viejo.**
   - El defecto vivía en Python: se pasaba `sigToks` a la lectura, y la prueba llamaba al JavaScript sin él. Lo cazó la
     revisión.
   - Ahora la prueba del comodín fija el diccionario entero que recibe la lectura, y una mutación restaura el código viejo
     en sus tres lugares.
2. **En ONE, nada fijaba las mayúsculas, y un reemplazo de la barra sobre el enlace no hacía nada.** Hay casos y
   mutaciones nuevos, y el reemplazo se quitó.
3. **La mutación «llegada sin exigir dos fechas» mordía por otra razón:** con una sola fecha, la llave desaparecía del
   JSON. Se sumó una tarjeta con tres fechas.
4. **Cuatro defectos cruzados, que probó la revisión, sobrevivían a la red:** una naviera podía pasar al motivo el
   tránsito de otra. Se sumó una prueba por naviera, el empate con el tránsito legible
   (`…_con_el_mismo_tiempo_de_transito`), y una mutación que cruza la función en cada una.
5. **La tarjeta sintética de COSCO no rellenaba el día con cero:** el resultado dependía de la fecha de la corrida.
6. **Dos mutaciones de CMA no probaban lo que decían, y faltaba una.**
   - La de «antes del aviso» duplicaba la evidencia en vez de moverla, así que caía porque la prueba veía dos llamadas.
   - La que quitaba el modo del nombre del archivo también le quitaba el «_validar_» con que la prueba ubica la llamada:
     caía porque no la encontraba, no por el nombre.
   - Las dos caen ahora por la aserción de posición y por los nombres de archivo.
   - Faltaba la mutación del mecanismo que corta; ya está.
7. **Una mutación quedó con su texto viejo repetido,** porque `_anotar_desempate` repite la línea de los tiempos. La
   cazó el prechequeo, y se ancló con la línea anterior.
8. **La «elección» del log de ONE es un texto del programa, no la tarjeta.** La sonda lo mostró, y ONE se midió en su
   HTML.
9. **Se quitó un `\b` de la ETA de MSC:** ninguna prueba podía fijarlo, y la ETD no lo lleva.

## Premisas del encargo contrastadas (pieza 5)

- **«La base: 317 pruebas, 667 mutaciones y 811 pares en `9051f43`»:** confirmada.
- **«Las 5 reservas de HYUNDAI del 21 son la evidencia del defecto (la misma tarjeta, con otra segunda palabra, en las
  cuatro corridas)»:** confirmada.
  - En las 8 elecciones, a la tarjeta le falta la segunda palabra de la nave, y ninguna de sus palabras empieza siquiera
    con la misma letra que esa segunda palabra: es otra nave, no un recorte.
  - En la planilla, la primera palabra es el prefijo de la naviera, así que calzar por ella aceptaba cualquier nave de
    HYUNDAI.
- **«Como ya hace MSC»:** MSC compara con el campo de la nave, no con toda la tarjeta. Se aplicó así donde el campo está
  medido (ONE, COSCO y MAERSK); en HYUNDAI y CMA, todavía no.
- **«El camino de nave no encontrada que ya tiene cada naviera»:** confirmada; ninguno cambió.
- **«El hallazgo 2 sobre ONE»:** confirmada y cerrada.
- **«El tiempo de tránsito» de las cuatro:** se lee sin ambigüedad. En ONE, MSC y COSCO es la llegada menos la salida; en
  MAERSK, 4 horas menos, por la hora local de cada puerto.
- **«"Validar ruta" sigue sin respuesta»:** no hay corrida nueva desde la del 25; no se volvió a medir.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| HYUNDAI y CMA comparan con toda la tarjeta (un nombre de puerto de la ruta podría calzar) | No hay HTML de su lista | …una corrida deja `hmm_f*_naves` y `cma_f*_rutas` |
| HYUNDAI no exige las palabras de su lista `ignore` (AUTO, PRIMERA, DISPONIBLE, CUALQUIERA, NW2, VIAJE, V., VOY) | Es anterior; «NW2» parece un código, no un rótulo | …decides si se exigen, o si la lista vale para las seis |
| Los comodines: CMA reconoce los suyos (AUTO, CUALQUIERA, LIBRE, N/A, NINGUNA, -, NONE) y HYUNDAI ignora AUTO, PRIMERA, DISPONIBLE y CUALQUIERA; ONE, MSC, COSCO y MAERSK buscan «LIBRE» como nave, y las seis buscan «NA» | No era parte del encargo | …decides una sola lista de comodines para las seis |
| CMA quita toda la puntuación de la nave; las otras cinco, solo la barra | Una nave con puntuación distinta a la del portal queda en REVISAR (el lado seguro) | …decides un solo tokenizador |
| MAERSK, con `AQUASHIELD_PRIMERA_NAVE`, toma la primera salida reservable sin calzar la nave | Es un modo de prueba explícito, anterior | …decides apagarlo, al menos con el candado abierto |
| HYUNDAI acepta el modal «Alternate Vessel Option» antes de la guarda | No está medido si cambia la nave | …una corrida lo deja en su evidencia |
| HYUNDAI y CMA toman la primera tarjeta que calza, sin la regla de la próxima salida | Falta el HTML de su lista | …se mide ese HTML |
| COSCO acepta la nave de la fila en cualquier tramo del itinerario | Todas las palabras están en una sola nave: cumple la regla | …decides que sea el primer tramo |
| MSC lee su campo de la nave hasta 40 caracteres | Una nave larga con su viaje daría «no está» (el lado seguro) | …una nave real lo supera |
| 2 de los 8 empates medidos de ONE siguen NO ENVIADA | Tardan lo mismo | …decides otro criterio |
| CMA: «Validar ruta» sigue sin respuesta; su evidencia queda también si el clic o la espera fallan | Se mide en la próxima corrida | …se lee `cma_f*_validar_*` |
| MAERSK: la casilla de términos (FRENO) y la búsqueda desde mañana | Ninguna corrida llegó a la revisión | …una corrida la alcanza |
| CMA y COSCO sin forma medida de confirmación | Nunca llegan a EMITIDA | …una emisión real deja su confirmación |
| Los residuales de `CICLO-cola-siete-items.md` y anteriores | No son parte de este encargo | …según cada fila de esos informes |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v13**:
- **PASO 0 con veredicto:** CICLO para los tres ítems. Los frenos de los ítems 1 y 2 se midieron antes de tocar código, y
  no se cumplieron.
- **Re-medir contra HEAD antes de diseñar:** la base del encargo (317, 667 y 811), con la sonda de la red.
- **Control positivo que aborta:** en cada sonda.
- **Todo salto silencioso lleva contador:** los descartes de carpetas, tarjetas, hojas y entradas de git se publican. Hay
  1: la tarjeta de MAERSK que estaba cargando.
- **La unidad la fija el sujeto:** el calce decide por tarjeta y por campo, así que se midió por tarjeta y por campo, no
  por página; el desempate, por grupo del mismo día.
- **Todo registro es una hipótesis:**
  - «como MSC» se contrastó con el código: MSC compara el campo, no la tarjeta;
  - la «elección» del log de ONE resultó ser un texto del programa.
- **El negativo tiene que morder:**
  - un censo filtrado en cada commit, dos veces en cada uno de los tres (antes y después de su revisión), y el censo
    completo al final;
  - tres mutaciones que mordían por otra razón se corrigieron.
- **Un gate en cero prueba contención, no correctitud:** por eso cada ítem pasó por una revisión adversarial antes de su
  commit.
- **Fuente única:**
  - el desempate, en `_proxima_salida` con `_menor_transito`, `_transito_legible`, `_texto_transito`, `_y_el_transito` y
    `_anotar_desempate`;
  - el calce, en `_trae_la_nave` para MSC y COSCO, y repetido en el JavaScript de las otras cuatro.
- **El cambio y su guardián en la misma operación; cada reemplazo afirma su viejo una vez; el EOL se preserva:**
  - los aplicadores afirmaron cada texto;
  - el prechequeo cazó el texto repetido;
  - todos los archivos de los commits tienen 0 CR.
- **FRENAR cuando la decisión es de negocio:** lo del residual queda reportado, no hecho.
- **Choque, sin freno:** la revisión del ítem 1 pidió comparar con el campo de la nave en COSCO y MAERSK. Entró en el
  mismo commit: es la regla «como MSC», y el campo estaba medido.

Reglas del módulo:
- casos sintéticos que imitan la estructura medida;
- la sonda de secretos antes de cada commit, que bloquea el nombre del operador;
- nada de `logs/` en el repo;
- los textos nuevos en español con tuteo.

## Entregable (pieza 8)

Este `.md`, sin renderizar, y `CLAUDE.md` al día.

**Gates.** En cada uno, la suite completa pasó con 0 cambios en los originales, y la sonda de secretos dio 0 sobre el
staging. Entre paréntesis van las mutaciones y los pares de cada censo filtrado, y todas muerden. Cada ítem corrió su gate
dos veces, antes y después de su revisión; va el segundo.

| Commit | Suite completa | Censos filtrados |
|---|---|---|
| Ítem 1, `2825153` | 323 en verde | `nave` (41 y 49), `calce` (2 y 2), `cosco-calza` (3 y 3), `cma-vuelve` (2 y 2), `cma-comodin` (1 y 1), `mk-salidas` (6 y 6), `FotoDeClics` (28 y 53), `TestEvidenciaRutasCma` (2 y 4) |
| Ítem 2, `4b0182b` | 336 en verde | `transito` (34 y 40), `proxima` (23 y 31), `motivo` (15 y 17), `llegada` (8 y 8), `msc-eta` (2 y 2), `sin_una` (12 y 15), `ambigu` (17 y 25), `js_tarjetas` (14 y 15), `js_salidas` (7 y 7), `js_naves` (2 y 2, las mismas de `msc-eta`), `anota` (16 y 19), `FotoDeClics` (28 y 53) |
| Ítem 3, `be6a86f` | 339 en verde | `cma-validar` (8 y 10), `test_solo_ahi` (19 y 42), `ValidarRuta` (7 y 9) |

- **Censo completo final sobre `be6a86f`:** pasó, en 61 minutos.
  - 339 pruebas en verde, y el control (la copia sin mutar) pasa;
  - 744 mutaciones y 897 pares, y muerden todos;
  - 0 pruebas sin mutación y 0 cambios en los originales.
- **El commit de este informe** solo agrega este `.md` y cambia `CLAUDE.md`, que ninguna prueba lee. La suite
  completa corrió con los dos ya cambiados: 339 en verde y 0 cambios en los originales.
