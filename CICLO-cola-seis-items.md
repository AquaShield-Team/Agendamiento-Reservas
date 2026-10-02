# CICLO · Cola de seis ítems: solo la nave que la fila pide

**Módulo:** Agendamiento Reservas · **Encargo 29** · **Fecha:** 2026-09-26 · **Método:** skill `metodo-ciclo` v13 ·
**Base:** `f68ce6c` (último de código: `714cbaa`) · **Commits** (locales; el repo no tiene remoto): uno por ítem,
`100f3b5` (ítem 1), `ed00cb5` (ítem 2), `4994f6e` (ítem 3), `c284fb0` (ítem 4), `1aecb06` (ítem 5) y `e6a0786`
(ítem 6), y el de este informe.

> Sin datos reales. `logs/`, las planillas y `config.json` se midieron en solo lectura. Las sondas imprimen conteos,
> etiquetas de interfaz, nombres de naviera, formas enmascaradas y nombres de archivo del programa. Las capturas se
> leyeron con OCR sin mirarlas, y la sonda imprime solo las etiquetas de botón que lee. Los HTML guardados se leyeron
> en un Chromium sin red y sin el JavaScript de la página. Nunca salen naves, puertos, contratos ni el nombre del
> operador, salvo los valores que ya están en el código: el puerto fijo y el mapa de puertos de COSCO.

La regla de los seis ítems, decidida por Marcelo: **el programa nunca reserva una nave que la fila no pidió.**

## Los seis ítems

| # | Ítem | Resultado | Commit | Freno |
|---|---|---|---|---|
| 1 | Una fila con solo el prefijo de la naviera es un comodín: queda NO ENVIADA como fila sin nave | Hecho | `100f3b5` | El ítem no traía freno propio |
| 2 | La nave calza por palabra entera, en el ayudante compartido | Hecho, en las seis navieras | `ed00cb5` | **No se activó:** en la evidencia guardada, ninguna tarjeta de la nave correcta deja de calzar |
| 3 | MANUAL es un comodín con su propio motivo | Hecho | `4994f6e` | El ítem no traía freno propio |
| 4 | La consola deja de tomar la nave de la columna F en ONE y MSC | Hecho | `c284fb0` | El ítem no traía freno propio |
| 5 | COSCO, sin el puerto de carga, corta en vez de usar el puerto fijo | Hecho | `1aecb06` | **No se activó:** el puerto se identifica sin el valor fijo en 18 de 18 reservas |
| 6 | El clic genérico de ONE antes de la guarda se reemplaza por objetivos identificados | Hecho: los 3 usos | `e6a0786` | **No se activó:** los 3 se identifican por su texto con la evidencia. En Additional Information, en 2 de 5 capturas |

Cada ítem pasó por una revisión adversarial antes de su commit: tres revisores con enfoques distintos en los ítems 1 y
2, dos en los ítems 3 a 6, y una verificación de los arreglos de los ítems 5 y 6. Encontraron huecos reales en todos:
están en la pieza 4.

**Convención de este informe y de los comentarios del código:** «hasta `f68ce6c`» quiere decir «antes del encargo 29»,
como «hasta `a198645`» en el encargo 28. Ningún ítem tocó código que hubiera cambiado un ítem anterior, así que «hasta
`f68ce6c`» vale igual para todos.

## Ítem 1 · Solo el prefijo de la naviera

**Los prefijos medidos en el código:** la lista de prefijos que CMA quitaba de la nave antes de calzar, hasta `9051f43`
(MSC, CMA, CGM, HMM, ONE, COSCO y MV), y los nombres de hoja de `HOJA_ALIAS` que no estaban en ella (HYUNDAI y MAERSK).
No hay otra lista de prefijos en el código de hoy ni en el historial (`git log -S`). MV es «motor vessel», no el prefijo
de una naviera: va porque es de esa lista medida.

**Las planillas reales:** 0 filas tienen solo prefijos: 120 del panel (60 por libro; la raíz y la copia del panel son
casi la misma planilla, así que cada fila cuenta dos veces) y 30 de la consola (`sonda_formas.py`). 60 de las 120 del
panel traen un prefijo junto a otras palabras, y esas siguen pidiendo su nave.

**Lo hecho:**
- `NAVES_PREFIJO`, aparte de `NAVES_COMODIN`, porque son también los nombres de las navieras, que otras funciones
  escriben como texto. `test_una_sola_regla` sigue vigilando que ninguna función traiga un comodín como texto, y ahora
  también que ningún JavaScript traiga un prefijo entre comillas.
- `_fila_sin_nave`: una celda con solo prefijos, o con prefijos y comodines («HMM PRIMERA»), no pide una nave. Con otra
  palabra («MSC NAVE»), la pide, con el prefijo incluido.
- Lo usan igual el panel web, la consola, `/api/filas`, el decorador de los seis reservadores y CMA: una fila «CMA CGM»
  ya no busca [CMA, CGM].

## Ítem 2 · La nave por palabra entera

**Lo hecho:**
- **Un solo ayudante,** con la misma cuenta en los dos lenguajes:
  - en Python, `_trae_la_nave` con `_palabra_en`, que usan MSC y COSCO (COSCO también para el viaje);
  - en JavaScript, `_JS_TRAE_LA_NAVE`, que ONE, HYUNDAI, MAERSK y CMA llevan al principio de su función. MAERSK usa
    `_palabraEn` para exigir el orden.
- Una palabra es entera si no tiene pegada antes ni después una letra o un número de `_LETRAS_DE_NAVE`, la misma clase
  con que `_fila_sin_nave` separa las palabras. «ANNA» ya no calza con «SAVANNAH», ni «FA001» con «FA001E».
- `test_trae_la_nave` corre en Python 16 casos de la regla (y el caso vacío). `test_la_misma_regla_en_javascript` corre
  los mismos 16 en Node, compara en los dos lenguajes 5 posiciones de `_palabra_en`, y compara la clase de letras con la
  de `_fila_sin_nave`.
- El JavaScript de CMA pasó a la constante `_JS_CMA_RUTAS`, idéntico salvo la línea del calce. Aparte, en Python, las
  palabras que CMA saca de la nave de la fila ya no se parten en la Ñ ni en las tildes: «PIÑA» daba «PI», que como
  palabra entera ya no calzaría.
- El aviso de MSC «ese barco con otro viaje» usa la misma regla.

**El freno, medido en la evidencia guardada** (`calce_evidencia.py`, `calce_log.py`, `pegado_y_formas.py`):

| Fuente | Universo | Calzaban (parte del texto) | Calzan (palabra entera) | Pierden |
|---|---|---|---|---|
| HTML con lista, con la nave de su fila (el calce de `f68ce6c` y el nuevo, con el JavaScript del programa, en Chromium) | 10 listas, 164 tarjetas de ONE, MSC, COSCO y MAERSK | 7 | 7 | **0** (y 0 ganan) |
| COSCO, con nave y viaje (el viaje sale de la planilla, con control: la nave de la planilla es la del log) | 2 listas | nave 2, viaje 2 | nave 2, viaje 2 | **0** |
| Elecciones escritas en `log.txt`, frente a la nave de su fila | 30 de MSC, COSCO y CMA | 29 | 29 | **0**; la otra no calzaba ni como parte del texto |

- **Textos pegados:** en los campos de nave de las listas, ningún texto de un elemento termina en letra o número justo
  donde empieza otro que también empieza así (lo que haría que dos palabras se lean como una). Son 64 campos de ONE, 79
  de MSC y 10 de MAERSK (las 13 tarjetas de MAERSK traen 10 con su campo). Los 16 textos de nave de COSCO traen la nave
  y su viaje separados por espacio.
- **HYUNDAI:** compara con el texto de toda la tarjeta. En sus 8 textos de tarjeta que dejó el log, la etiqueta «MAIN
  VESSEL», la nave y su viaje van separados por espacios.
- **Sin medir:** HYUNDAI y CMA no tienen HTML de su lista guardado, y ONE hasta `16d3583` no escribía el texto de la
  tarjeta elegida. ONE y MAERSK no tenían ninguna tarjeta que calzara en sus listas guardadas (sus `log.txt` dicen «no
  encontré la nave»), así que ahí la palabra entera no se puso a prueba.

## Ítem 3 · MANUAL

**Las planillas reales:** 0 filas traen MANUAL (las mismas 120 del panel y 30 de la consola).

**Lo hecho:**
- `_fila_manual`: la misma regla con que el panel dejaba la fila sin marcar, MANUAL en cualquier parte de la celda y sin
  distinguir mayúsculas. Hasta `f68ce6c` vivía solo en el JavaScript del panel; ahora el panel la recibe de `/api/filas`
  (`_con_su_marca`) y `marcadaPorDefecto` usa `f.manual`.
- `_fila_sin_nave` la cuenta como fila sin nave, y `_sin_nave` le da su propio motivo, «la fila está marcada para
  hacerse a mano». El aviso dice: «No entro al portal por ella: hazla a mano en el portal, o escribe en la celda solo la
  nave, sin MANUAL, si quieres que la arme yo».
- El panel deja sin marcar las mismas filas que antes, y no las cuenta como sin nave. Si se corren igual, o en la
  consola, que no tiene casillas, quedan NO ENVIADA sin entrar al portal por ellas.

## Ítem 4 · La columna F de la consola

**Lo medido:** en la planilla estándar, la F es «Viaje». Con la celda de la nave vacía, ONE y MSC tomaban el viaje como
nave si traía una de las palabras fijas que el lector buscaba en ella. En la planilla real de la consola, 0 de 30 filas
lo hacían (`sonda_formas.py`, que compara el lector de `f68ce6c` con una copia sin la F).

**Lo hecho:** `leer_reservas` marca `nave_de_la_f` y devuelve la nave vacía. Lo demás del lector no cambia: la F sigue
decidiendo si la fila es una nota, si entra a la lista y, en ONE, el destino final. La regla corre también si la hoja no
tiene columna de nave, porque es el mismo camino del código. Lo muestra la «trampa de título» de las pruebas: una
planilla sintética cuyo título dice «origen», y la consola toma esa fila como encabezado.

## Ítem 5 · El puerto de carga de COSCO

**El freno, medido en los 9 `log.txt`** (`cosco_origen.py`): de las 19 reservas de COSCO, 18 llegaron a elegir el puerto
de carga, y en las 18 la primera búsqueda eligió su sugerencia, con el puerto de la fila o el del mapa del código
(las 18 celdas estaban en el mapa). **Ninguna cayó al puerto fijo.** El puerto se identifica sin él: el freno no se
activó.

**Lo hecho:**
- `_cosco_puerto_de_carga` busca en «Origin City» la celda de la fila traducida por `MAPA_PUERTOS_COSCO` (que pasó al
  nivel del módulo sin cambiar su contenido), o su primera parte antes de la coma, con una sugerencia de Chile.
- Si no la hay, o si la celda no trae el puerto, levanta `ObjetivoNoEncontrado`: NO ENVIADA, con
  `cosco_f<fila>_sin_objetivo` (captura y HTML).
- El motivo nombra el puerto buscado y, si difiere de la celda (porque el mapa la tradujo o porque se cortó lo que va
  tras la coma), también la celda. Con la celda vacía dice «escríbelo en la planilla».
- La página falsa de la prueba exige el campo «origin ci» y la sugerencia de Chile.

**Cambia (antes → ahora):**
- sin sugerencia, escribía «Lirquen» y seguía aunque tampoco eligiera nada → NO ENVIADA;
- si el puerto de la fila ya era «Lirquen», seguía sin elegir → NO ENVIADA;
- con la celda vacía, buscaba el texto vacío (que calza con cualquier sugerencia de Chile) o caía a «Lirquen» → NO
  ENVIADA sin escribir nada.

## Ítem 6 · El clic genérico de ONE

**Dónde se usaba `_JS_CLICK_BTN` en ONE:** 3 veces antes de la guarda, los «Next» de Booking Parties, Container &
Cargo y Additional Information; y 1 después, el envío (`_pulsar_boton`), que no se tocó. En MSC quedan 4 usos: el login
(2), «Search Schedule» y el envío.

**El freno, medido** (`one_siguiente.py`, `one_botones.py`): no hay HTML de esas tres pantallas, así que se leyeron las
capturas de las 5 reservas del 2026-09-21 que recorrieron el asistente, con OCR y sin mirarlas.

| Pantalla | El único botón de color con etiqueta | El paso siguiente, en `log.txt` |
|---|---|---|
| Booking Parties (`_6_parties`) | «Next», 5 de 5 | 5 de 5 |
| Container & Cargo (`_8_carga`) | «Next», 5 de 5 | 5 de 5 |
| Additional Information (`_9_adicional`) | «Next», 2 de 5; en las otras 3 la captura no llega al pie | 5 de 5 |

Los tres usos se identifican por su texto: el freno no se activó. En Additional Information la evidencia es más corta (2
de 5), y en ninguna pantalla hay HTML: que el «Next» sea el único en toda la página lo confirma la próxima prueba.

**Lo hecho:**
- `_JS_ONE_SIGUIENTE`: el único botón a la vista, fuera del encabezado y de la navegación, cuyo texto es exactamente
  «Next» o «Siguiente». Si un «Next» está en una ventana emergente (el selector de `_JS_ONE_CERRAR_MODAL`), como
  «Vessel Information», no pulsa nada.
- `_one_siguiente` comprueba primero que el asistente esté en su paso (`_one_esta_en_paso`). Si no está, si el «Next»
  está en una ventana o si no hay uno solo, corta; si la búsqueda falla, corta sin reintentar, porque el clic pudo haber
  salido.
- Esto cierra la parte del residual del encargo 28 sobre el «Next» de un «Vessel Information» que saliera entre dos
  pantallas del asistente. El cierre de otros diálogos con OK o «Accept» (`_cerrar_modal_one`) sigue igual.

**Cambia (antes → ahora):**
- sin «Next» en Booking Parties o Container & Cargo, lo anotaba y seguía → NO ENVIADA;
- sin «Next» en Additional Information, REVISAR «no llegó a review-booking» → NO ENVIADA con evidencia;
- con dos «Next» a la vista, o uno en una ventana emergente, pulsaba el primero → NO ENVIADA;
- si la búsqueda falla, la excepción dejaba la reserva en ERROR → NO ENVIADA;
- Continue, Continuar, Review y Revisar ya no avanzan el asistente.

## Expectativas que cambiaron (antes → ahora)

| Prueba | Antes | Ahora |
|---|---|---|
| `test_ayudantes.TestFilaSinNave.test_fila_sin_nave` | «MSC» y «MANUAL» pedían una nave | No la piden: prefijo y MANUAL |
| `test_ayudantes.TestFilaSinNave.test_ningun_reservador_abre_el_portal_sin_nave` | Una fila «HMM» entraba al portal en las seis navieras | Queda NO ENVIADA, sin tocar la página (caso nuevo) |
| `test_consola.TestEjecutarReservas.test_fila_sin_nave_no_abre_el_portal` | La fila 6 de COSCO con «COSCO» iba al portal | NO ENVIADA sin abrir el navegador (caso nuevo) |
| `test_ayudantes.TestNaveCompleta.test_trae_la_nave` | («SAVANNAH», [ANNA]) calzaba | No calza; y 10 casos nuevos de la regla |
| `test_ayudantes.TestNaveCompleta.test_cosco_calza_en_una_de_sus_naves` | Viaje «002» con «… 002W»: [0] | La nave con cualquier viaje: [0, 3] |
| `test_ayudantes.TestNaveCompleta.test_msc_y_cosco_calzan_con_el_ayudante` | El aviso de MSC: sus dos primeras palabras juntas y en orden, como parte del texto («MSC NAVE» no avisaba con «NAVE MSC 001E» y sí con «MSC NAVES 001E») | Cada una entera, en cualquier lugar |
| `test_ayudantes.TestFilaSinNave.test_una_sola_regla` | Comodines en el JavaScript | También prefijos y MANUAL; MANUAL, solo en `_fila_manual` |
| `test_clics.TestOne.test_js_tarjetas_de_la_nave_con_su_salida` | «ONE NAVE ANNA» y «… SC001» calzaban con «ONE NAVE SAVANNAH SC001E» | No calzan |
| `test_clics.TestHyundai.test_js_nave_con_todas_sus_palabras` | En sus dos formas de lista (la de «Book Now» y la anterior, `a.preview-area`), pulsaba la primera, la de «SAVANNAH» | Pulsa la de «ANNA» |
| `test_clics.TestMaersk.test_js_salidas_lee_la_salida_y_si_se_puede_reservar` | Con «SAVANNAH» y «ANNA»: [True, True] | [False, True] |
| `test_clics.TestCma.test_js_rutas_nave_con_todas_sus_palabras` | Extraía el JavaScript de la función; con «SAVANNAH» y «ANNA», [True, [1, 0]] | Usa `_JS_CMA_RUTAS`; [True, [0, 1]] |
| `test_clics.TestCma.test_itinerario_comodin_no_se_busca_como_nave` | «CMA CGM» buscaba [CMA, CGM]; «PIÑA» daba «PI» | [] y [CMA, CGM, PIÑA] |
| `test_clics.TestFotoDeClicsGenericos` (`PERMITIDOS`) | Sin esa entrada: `_JS_CLICK_BTN` no lo veía ninguna forma | Suma `("reservar_one", "_JS_ONE_SIGUIENTE", "primero-sin-filtro"): 1`, ESPECÍFICO |
| `test_envio.TestLecturaDelPanel.test_marca_por_defecto_tambien_las_filas_sin_nave` | El panel dejaba sin marcar la fila por el texto MANUAL de su celda | Decide con `f.manual` de `/api/filas`; si viene falso, la fila va marcada aunque diga MANUAL |
| `test_planilla` (la foto de la consola, la trampa de título y las diferencias entre lectores) | La fila 7 de ONE y la 6 de MSC de la planilla sintética, con el viaje como nave | Nave «»; lo demás igual |
| `test_consola`: `test_sin_emitir_solo_si_volvio_sin_emitir`, `test_estados_tras_el_envio_en_la_planilla`, `test_sin_escrituras_no_deja_respaldo` y `test_login_fallido_no_toca_la_planilla` | Esas filas llegaban al reservador | Lo que esperan no cambia; cambia el dato: ponen una nave en esas filas |

**Pruebas nuevas (14):** en `test_ayudantes`, `test_fila_manual`, `test_ningun_reservador_abre_el_portal_con_manual`,
`test_la_misma_regla_en_javascript` y `test_las_navieras_de_javascript_con_el_ayudante`; en `test_web`,
`test_fila_con_solo_el_prefijo_no_abre_el_portal` y `test_fila_manual_corrida_igual_queda_no_enviada`; en
`test_consola`, `test_fila_manual_queda_no_enviada` y `test_la_nave_no_sale_de_la_columna_f`; en `test_planilla`,
`test_la_f_sigue_decidiendo_las_filas`; en `test_clics`, `test_puerto_de_carga_sin_sugerencia_corta`,
`test_reservar_cosco_elige_el_puerto_de_carga_con_el_ayudante`, `test_js_siguiente_solo_el_de_la_pantalla`,
`test_siguiente_sin_uno_solo_corta` y `test_reservar_one_avanza_con_el_siguiente_identificado`.

**`test_candado` no cambió:** su archivo es igual en los seis commits, y pasó en cada gate.

**Mutaciones:**
- Entran 72 (4, 25, 11, 7, 9 y 16 por ítem).
- Sale 1, `one-nave-distingue-mayusculas-del-enlace`, que quedó equivalente: el ayudante de JavaScript pasa el texto a
  mayúsculas. La cubre `js-trae-la-nave-con-mayusculas`.
- Se reanclaron 29 veces 26 mutaciones distintas: 3 en el ítem 1, 13 en el 2 y 13 en el 3. Tres de ellas se reanclaron
  en los ítems 1 y 3. El mensaje de `4994f6e` dice «14 reancladas»: son 13.
- `consola-sin-regla-one` cambió su lista de pruebas en el ítem 4.

## Veredicto por naviera: ¿lista para una emisión real de prueba?

Ningún veredicto cambió desde `CICLO-solo-la-nave-pedida.md`. Lo nuevo va en la última columna.

| Naviera | Veredicto | Qué le falta | Lo nuevo de este encargo |
|---|---|---|---|
| **MSC** | **Casi lista** | Una corrida con candado cerrado. El programa reconoce el número de reserva en su confirmación, así que puede llegar a EMITIDA | La nave calza por palabra entera, y eligió lo mismo que antes en sus 3 listas guardadas |
| **ONE** | **Casi lista** | Una corrida con candado cerrado que pase por sus tres pantallas (Booking Parties, Container & Cargo y Additional Information). El programa reconoce su número de reserva | Ahora exige un solo botón «Next» en cada una de esas pantallas. No hay HTML guardado de ellas, así que eso se confirma en la corrida: si hay otro «Next», se detiene (NO ENVIADA) con captura y HTML |
| **COSCO** | **No para emitir** | El programa no reconoce el número de su confirmación: tras el envío la dejaría en ENVIADA – REVISAR EN PORTAL. Para la prueba con candado cerrado está casi lista | Si no encuentra el puerto de carga de la fila, se detiene (NO ENVIADA) en vez de usar un puerto fijo |
| **HYUNDAI** | No | Si la ventana «Alternate Vessel Option» (donde el portal ofrece otra nave) sale siempre, todas sus reservas quedan NO ENVIADA. Falta una prueba con la nave pedida en su lista, el HTML de su lista para calzar con el campo de la nave, y aplicar la regla de la próxima salida | La nave calza por palabra entera |
| **CMA** | No | El portal sigue sin responder a «Validar ruta», falta el HTML de su lista de salidas, no aplica la próxima salida, y el programa no reconoce su número: nunca llega a EMITIDA | La nave calza por palabra entera, y la Ñ y las tildes cuentan como letras |
| **MAERSK** | No | Necesita una fila cuya nave tenga una salida con el botón «Book», para llegar a la revisión. La casilla de términos se sigue marcando con «el último checkbox» hasta medirla | La nave calza por palabra entera, en orden |

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\correr.py --mutaciones --filtro prefij
python tests\correr.py --mutaciones --filtro sin-nave-
python tests\correr.py --mutaciones --filtro trae-la-nave
python tests\correr.py --mutaciones --filtro palabra-en
python tests\correr.py --mutaciones --filtro letras-
python tests\correr.py --mutaciones --filtro js-
python tests\correr.py --mutaciones --filtro parte-del-texto
python tests\correr.py --mutaciones --filtro sin-el-ayudante
python tests\correr.py --mutaciones --filtro one-nave
python tests\correr.py --mutaciones --filtro hmm-nave
python tests\correr.py --mutaciones --filtro mk-salidas
python tests\correr.py --mutaciones --filtro cma-
python tests\correr.py --mutaciones --filtro manual
python tests\correr.py --mutaciones --filtro filas-
python tests\correr.py --mutaciones --filtro panel-
python tests\correr.py --mutaciones --filtro consola-
python tests\correr.py --mutaciones --filtro cosco-origen
python tests\correr.py --mutaciones --filtro one-siguiente
python tests\correr.py --mutaciones --filtro generico
python tests\correr.py --todo
```

Las sondas son de solo lectura y no se versionan, porque leen datos reales. Quedaron en la carpeta temporal de la
sesión (`scratchpad\e29`), que puede limpiarse; sin ellas, estos números no se re-miden. Se corren con
`python <sonda>.py`, y cada una aborta si su control no da lo esperado.
- **`sonda_formas.py`, las planillas:** con los dos lectores, las filas con solo prefijos, con MANUAL y con un prefijo
  junto a otras palabras; y con la consola, las filas que toman la nave de la F (compara el lector de `f68ce6c` con una
  copia sin la F).
- **`calce_evidencia.py <AQUASHIELD.py> [commit]`, el freno del ítem 2:** el calce del commit (por defecto `f68ce6c`) y
  el del `AQUASHIELD.py` que se pase, con el JavaScript del programa, sobre cada HTML con lista, con la nave de su fila.
- **`calce_log.py`:** las elecciones escritas en `log.txt`, frente a la nave de su fila.
- **`pegado_y_formas.py`:** los textos pegados en los campos de nave, y las palabras con Ñ, tildes o signos en las
  planillas.
- **`cosco_origen.py`, el freno del ítem 5:** cada línea «Origin City» de COSCO y si cayó al puerto fijo.
- **`one_siguiente.py` y `one_botones.py`, el freno del ítem 6:** las líneas de cada «Next» en `log.txt`, y con OCR las
  etiquetas de los botones de color en cada captura del asistente.
- **`scratchpad\e26\red_por_commit.py`, del encargo 26:** pruebas, mutaciones y pares de cada commit, leídos de git.
  Se corre con `python e26\red_por_commit.py f68ce6c 100f3b5 ed00cb5 4994f6e c284fb0 1aecb06 e6a0786`.

## NO retroceder (pieza 2)

- **No vuelvas a calzar como parte del texto,** en ninguna naviera ni en el viaje de COSCO: `_trae_la_nave` y
  `_JS_TRAE_LA_NAVE` son el único calce, y `test_la_misma_regla_en_javascript` vigila que den lo mismo.
- **No copies el ayudante de JavaScript en cada naviera:** se arma con la constante.
- **No vuelvas a dejar que una fila con solo el prefijo, o con MANUAL, entre al portal.**
- **No vuelvas a poner la regla de MANUAL en el JavaScript del panel:** el panel la recibe de `/api/filas`.
- **No vuelvas a tomar la nave de la columna F** en la consola.
- **No vuelvas a buscar el origen de COSCO desde un puerto fijo.**
- **No vuelvas a usar `_JS_CLICK_BTN` antes de la guarda de ONE,** ni a reintentar un «Next» después de una falla de
  la búsqueda.

## Universo y cobertura (pieza 3)

- **`logs/`:** 9 carpetas, las 9 con `log.txt`; 0 descartadas.
  - HTML con lista de salidas, de las filas con su nave en `log.txt` (marcos incluidos): 10 archivos con lista y 164
    tarjetas. ONE, 2 listas (64); MSC, 3 (79); COSCO, 2 (8 filas); MAERSK, 3 (13). En todos los HTML de COSCO hay 16
    textos de nave.
  - HYUNDAI y CMA: 0 HTML de su lista.
  - Reservas de COSCO: 19; que llegaron a elegir el puerto: 18.
  - Recorridos del asistente de ONE: 5, de una corrida (15 capturas de sus tres pantallas).
- **Las planillas:** el lector del panel leyó los 2 libros (la raíz y la copia del panel), 60 filas cada uno; el de la
  consola, 30 filas de las seis hojas de naviera de la raíz.
- **El código:** el mapeo del código recorrió los seis ítems con 5 agentes y un revisor crítico.
- **No medido:**
  - la palabra entera en las listas de HYUNDAI y CMA (sin HTML), y en listas de ONE y MAERSK donde calzara la nave;
  - que el «Next» de ONE sea el único de su página (sin HTML de esas pantallas);
  - que un «Vessel Information» salga entre dos pantallas del asistente.

## Defectos de instrumento cazados (pieza 4)

1. **La herramienta Bash cambia `\\` por `\` también en el heredoc:** tres scripts de mutaciones y de ajustes no
   encontraron su texto y abortaron sin escribir. Se reescribieron con Write o con Edit.
2. **Un script escribió una prueba con CRLF** (`write_text` de Python en Windows). Se cazó en el `git diff`, antes del
   gate, y se volvió a LF; los demás escriben en binario.
3. **`sort` de Git Bash está bloqueado por Defender:** un conteo con `sort | uniq` salió vacío sin error. Se rehízo con
   Python.
4. **El OCR no leía el texto blanco sobre un botón de color.** La sonda abortó porque su control sintético no leyó el
   botón; así se descubrió. Se cambió el instrumento: ubicar los rectángulos de color con OpenCV y leer cada uno por
   dentro. Con eso, el control pasa y «Next» aparece en las capturas donde antes no se leía.
5. **La comparación de `BASE` en la sonda de las planillas** daba falso por la ruta corta del temporal: se compararon las
   rutas resueltas, y la sonda aborta si no coinciden.
6. **Dos sondas medían contra HEAD,** y dejaron de reproducir sus números cuando HEAD ya traía el cambio: `sonda_formas.py`
   abortaba y `calce_evidencia.py` comparaba el calce nuevo consigo mismo. Lo cazó la revisión del informe; ahora las
   dos miden contra `f68ce6c`, y dan lo mismo.
7. **La revisión del ítem 1 cazó:**
   - un caso de prueba que fijaba «COSCO SHIPPING» como una nave sin que nadie lo hubiera decidido;
   - una mutación reanclada que dejó de aislar su defecto.
8. **La revisión del ítem 2 cazó:**
   - una mutación que quedó equivalente (`one-nave-distingue-mayusculas-del-enlace`);
   - CMA partía las palabras en la Ñ;
   - el JavaScript de la palabra vacía no terminaba;
   - el viaje de COSCO cambió sin listarse;
   - el mensaje de MSC cambió más de lo que decía su prueba.
9. **Las revisiones de los ítems 3 a 6 cazaron:**
   - un aviso de MANUAL incompleto;
   - que nada vigilaba lo que la F seguía decidiendo en la consola;
   - una página falsa de COSCO que no miraba el campo ni el país;
   - un «Next» de ventana emergente que contaba como el del asistente;
   - un clic que la foto no veía;
   - un reintento tras una falla que podía pulsar el «Next» de la pantalla siguiente.
10. **La verificación de los ítems 5 y 6 cazó una mutación que mordía por otra razón** (`cosco-origen-sigue-sin-sugerencia`
    no llegaba a buscar). Se reescribió para que corte la búsqueda en el lugar del defecto.

## Premisas del encargo contrastadas (pieza 5)

- **«La base: 356 pruebas, 814 mutaciones y 986 pares en `f68ce6c`»:** confirmada con `red_por_commit.py`.
- **««MSC», «HMM» y los que se midan en el código»:** confirmada. Son 9, con MV, que no es de una naviera.
- **«Va en el ayudante compartido que ya usan las navieras»:** parcial. Solo MSC y COSCO usaban `_trae_la_nave`; ONE,
  HYUNDAI, MAERSK y CMA calzaban en su propio JavaScript. Se hizo un solo ayudante para los dos lenguajes.
- **«El campo de la nave de la tarjeta»:** HYUNDAI y CMA siguen comparando con toda la tarjeta, porque falta el HTML de
  su lista para ubicar el campo (residual).
- **«La consola toma la nave de la columna F cuando la celda viene vacía»:** confirmada, y también cuando la hoja no
  tiene columna de nave; es el mismo camino.
- **«COSCO busca desde el puerto fijo cuando no encuentra el puerto de carga»:** confirmada en el código; en la evidencia,
  ninguna reserva cayó a él.
- **«El clic genérico de ONE antes y después de la guarda»:** confirmada: 3 antes y 1 después.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| «CSCL» y «COSCO SHIPPING» no son prefijos: una fila con solo eso calzaría con las naves de COSCO que empiezan así. En las listas guardadas de COSCO, 2 de 16 textos de nave empiezan con «CSCL» y 0 con «COSCO SHIPPING» | El ítem pedía los prefijos medidos en el código, y no están en él | …decides sumarlos a `NAVES_PREFIJO` |
| MANUAL cuenta en cualquier parte de la celda («MANUALMENTE», «NAVE UNO MANUAL»), no como palabra | Es la misma regla con que el panel ya la dejaba sin marcar; 0 filas reales con MANUAL | …decides que cuente solo como palabra |
| Si todas las filas de una naviera son MANUAL, el aviso dice «Ninguna fila de … trae una nave para reservar» | La línea de cada fila sí trae su motivo | …decides otro texto |
| HYUNDAI y CMA calzan con el texto de toda la tarjeta, no con el campo de la nave | Falta el HTML de sus listas | …se miden `hmm_f*_naves` y `cma_f*_rutas` |
| El viaje de MAERSK sigue comparándose como parte del texto (solo elige entre salidas de la misma nave) | El ítem 2 era sobre la nave | …decides exigirlo entero |
| COSCO: el mapa traduce la celda entera; «CORONEL, CHILE» o «Lirquén» con tilde no se traducen, y sin sugerencia quedan NO ENVIADA. Con la celda vacía, el motivo termina en «revisa ese paso en el portal» | 18 de 18 reservas reales eligieron su puerto; ese cierre es el de todos los cortes | …una corrida corta por eso, o decides otro texto |
| ONE: `_one_esta_en_paso` acepta el paso también por el texto de la página, y el resultado de `_one_esperar_paso` se sigue ignorando. Si un «Next» no avanza, la pantalla siguiente corta, pero el motivo nombra la pantalla siguiente, no la que falló | Es anterior al encargo; los 5 recorridos confirmaron cada paso | …una corrida corta en una pantalla que no correspondía |
| ONE: con un «Next» en una ventana emergente, el motivo es genérico (no dice si era «Vessel Information») | La captura y el HTML de la ventana quedan en la evidencia | …decides nombrar la ventana |
| ONE: `_cerrar_modal_one` cierra los diálogos que no son «Vessel Information» con OK, «Accept» o «Aceptar» | No es el clic genérico del ítem 6; 0 cierres en los 9 `log.txt` | …una corrida muestra un diálogo que ofrezca otra nave con esos botones |
| MSC usa `_JS_CLICK_BTN` antes de su guarda en «Search Schedule» (y en su login). La foto de `test_clics` no ve `_JS_CLICK_BTN`: un uso nuevo antes de una guarda no tumba la red, salvo en ONE, que vigila `test_reservar_one_avanza_con_el_siguiente_identificado` | El ítem 6 era sobre ONE | …decides extenderlo a MSC |
| La planilla descargada deja vacío «N° de reserva emitida» en toda fila que no quedó EMITIDA, también en las MANUAL | Es anterior al encargo | …decides conservar lo escrito a mano |
| Los residuales de `CICLO-solo-la-nave-pedida.md`, salvo los que cierra este encargo: los prefijos, el calce por parte del texto, MANUAL, la columna F, el origen de COSCO y el «Next» de un diálogo en el asistente de ONE | No son parte de este encargo | …según cada fila de ese informe |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v13**:
- **PASO 0 con veredicto:** CICLO para los seis. Los tres frenos (ítems 2, 5 y 6) se midieron antes de tocar su código.
- **Re-medir contra HEAD:** la base del encargo, con `red_por_commit.py`.
- **Control positivo que aborta:** en cada sonda (planillas, logs, HTML en Chromium, OCR). El OCR tuvo que cambiar de
  instrumento para que su control pasara (pieza 4).
- **Todo salto silencioso lleva contador:** 0 carpetas descartadas; los HTML sin lista se cuentan aparte.
- **La unidad la fija el sujeto:** el calce decide por tarjeta y se midió por tarjeta; el puerto, por reserva; el «Next»,
  por pantalla.
- **Todo registro es una hipótesis:** «el ayudante compartido que ya usan las navieras» resultó ser dos de seis.
- **El negativo tiene que morder:** en cada commit, un censo filtrado a las mutaciones nuevas y las reancladas, todas
  cubiertas. Las que apuntan a pruebas cambiadas se censaron en los ítems 4 a 6. En el ítem 1 quedaron fuera 23, y 1 en
  los ítems 2 y 3; las cubre el censo completo final. Una mutación quedó equivalente y se quitó (lectura (c): redundante
  por otro cambio del mismo ciclo).
- **Un gate en cero prueba contención:** por eso cada ítem pasó por una revisión adversarial, y los ítems 5 y 6 por una
  verificación de sus arreglos.
- **Fuente única:** un solo ayudante de calce para los dos lenguajes, armado con su constante; una sola regla de MANUAL.
- **El cambio y su guardián en la misma operación; cada reemplazo afirma su viejo una vez; el EOL se preserva:** los
  aplicadores afirmaron cada texto y abortaron cuando no calzó; todos los archivos de los commits tienen 0 CR.
- **FRENAR cuando la decisión es de negocio:** «CSCL», MANUAL por palabra y el viaje de MAERSK quedan en el residual.
- **Choques entre reglas:**
  - El ítem 4 era la única excepción autorizada a no tocar el lector, y exigía no cambiar otra columna ni fila. Se
    resolvió sin frenar: la F sigue decidiendo todo lo demás, y una prueba lo vigila.
  - La regla de no clics a ciegas y el envío después de la guarda, que no se toca, comparten `_JS_CLICK_BTN`. Se
    resolvió reemplazándolo solo antes de la guarda de ONE.

Reglas del módulo:
- casos sintéticos que imitan la estructura medida;
- la sonda de secretos antes de cada commit;
- nada de `logs/` en el repo;
- los textos nuevos en español con tuteo.

## Entregable (pieza 8)

Este `.md` (no se convirtió en página; se leyó como texto, no renderizado) y `CLAUDE.md` al día.

**La red por commit** (`red_por_commit.py`):

| Commit | Pruebas | Mutaciones | Pares |
|---|---|---|---|
| `f68ce6c` (base) | 356 | 814 | 986 |
| `100f3b5` (ítem 1) | 357 | 818 | 994 |
| `ed00cb5` (ítem 2) | 359 | 842 | 1034 |
| `4994f6e` (ítem 3) | 363 | 853 | 1056 |
| `c284fb0` (ítem 4) | 365 | 860 | 1070 |
| `1aecb06` (ítem 5) | 367 | 869 | 1079 |
| `e6a0786` (ítem 6) | 370 | 885 | 1095 |

**Gates.** En cada uno, la suite completa pasó con 0 cambios en los originales, y la sonda de secretos dio 0 sobre el
árbol y sobre lo agregado con `git add`. Los filtros de un mismo gate se solapan: la tabla da las mutaciones y los pares
distintos.

| Commit | Suite completa | Censos filtrados |
|---|---|---|
| Ítem 1, `100f3b5` | 357 en verde | 5 filtros, 13 mutaciones y 20 pares; todas muerden |
| Ítem 2, `ed00cb5` | 359 en verde | 18 filtros, 156 mutaciones y 194 pares; todas muerden |
| Ítem 3, `4994f6e` | 363 en verde | 7 filtros, 82 mutaciones y 114 pares; todas muerden |
| Ítem 4, `c284fb0` | 365 en verde | 3 filtros, 61 mutaciones y 79 pares; todas muerden |
| Ítem 5, `1aecb06` | 367 en verde | 4 filtros, 21 mutaciones y 25 pares; todas muerden |
| Ítem 6, `e6a0786` | 370 en verde | 5 filtros, 128 mutaciones y 161 pares; todas muerden |

- **Censo completo final sobre `e6a0786`:** pasó, en 58 minutos.
  - 370 pruebas, y la copia de control, sin mutar, pasa;
  - 885 mutaciones y 1095 pares: los 1095 muerden;
  - 0 pruebas sin mutación y 0 cambios en los 2313 archivos originales fotografiados.

## Qué fila elegir en cada naviera para la próxima prueba con candado cerrado

- Una fila por naviera en CONSOLIDADO, con «Iniciar AQUASHIELD.bat», nunca con «Iniciar AQUASHIELD_EMISION.bat».
- Elige cada nave en el portal el mismo día de la corrida, en la ruta de la fila, y escríbela **con todas sus palabras
  completas, como el portal la muestra**:
  - salvo en las dos filas de control de abajo, nunca la dejes vacía, con «completar», con un comodín, con MANUAL ni con
    solo el prefijo de la naviera: quedaría NO ENVIADA sin entrar al portal;
  - una palabra cortada ya no calza: «FA001» no calza con «FA001E». El viaje va en su columna, también completo.
- **Suma dos filas de control:**
  - **una sin nave,** con la celda de la nave vacía, en cualquier naviera. En el panel aparece marcada por defecto. Al
    correr, queda NO ENVIADA con «la fila no trae una nave para reservar», sin que el programa entre al portal por ella;
    el portal se abre igual por la otra fila de esa naviera;
  - **una con MANUAL,** en otra naviera. En el panel aparece sin marcar; márcala a mano: queda NO ENVIADA con «la fila
    está marcada para hacerse a mano», sin entrar al portal por ella.

| Naviera | Qué fila elegir | Qué evidencia va a dejar |
|---|---|---|
| **HYUNDAI (la más importante)** | Una nave que **sí esté** en su lista para esa ruta y ese día, con el prefijo y el nombre como la muestra el portal | `hmm_f<fila>_naves` (la lista). Si sale la ventana «Alternate Vessel Option», `hmm_f<fila>_otra_nave`, y la fila queda NO ENVIADA: así se sabrá si sale también con la nave pedida. Si no sale, `hmm_f<fila>_remark` y `hmm_f<fila>_guarda` |
| **ONE** | La nave como la trae el enlace de su tarjeta, con una salida que no sea de hoy ni de mañana, para que el cierre de recepción (cut-off) esté vigente | `one_f<fila>_guarda` si llega a Review Booking; `one_f<fila>_detenida` con la lista si no queda una sola salida; `one_f<fila>_sin_objetivo` si ONE muestra «Vessel Information» o si un «Next» del asistente no es único, con el HTML de esa pantalla, que falta para medir |
| MSC | Cualquier nave de su lista para esa ruta, con su prefijo («MSC …») | `msc_f<fila>_guarda` (Summary) |
| COSCO | Una nave con un itinerario para esa ruta. Escribe el puerto de carga como lo sugiere COSCO, sin tilde y sin el país | `cosco_f<fila>_guarda`; `cosco_f<fila>_itinerarios` si hay más de un itinerario y el programa no puede elegir; `cosco_f<fila>_sin_objetivo` si no encuentra el puerto |
| MAERSK | Una nave con una salida que traiga el botón «Book» (con el plazo «Gate-in deadline» vigente) | `mk_f<fila>_guarda`: la revisión, con la casilla de términos por identificar |
| CMA | Cualquier nave con ruta ese día | `cma_f<fila>_rutas`, `cma_f<fila>_validar_<modo>`, los del panel Reefer y `cma_f<fila>_guarda` |

**Después de la corrida, lo primero:** revisa que ninguna fila haya quedado en EMITIDA ni en ENVIADA – REVISAR EN
PORTAL, y que no haya capturas `*_confirmado`. Después revisa las dos filas de control, `hmm_f*_otra_nave`,
`hmm_f*_naves`, `cma_f*_rutas`, `cma_f*_validar_*`, los `*_sin_objetivo` de ONE y COSCO, y la revisión de MAERSK si
llegó a ella.
