# CICLO · Las corridas del 26-09: el inicio de «todas», las emisiones y la cola decidida

**Módulo:** Agendamiento Reservas · **Encargo 30** · **Fecha:** 2026-09-26 · **Método:** skill `metodo-ciclo` v14 (el
ciclo empezó con la v13; la v14 entró a las 15:38 de hoy y suma la pieza 9) · **Commits** (locales; el repo no tiene
remoto, así que no hay push que entregar): uno por ítem, `479ebf6` (ítem 1), `9036d2c` (ítem 2), `3968cfa` (ítem 3),
`796d95a` (ítem 4) y `49de5d4` (ítem 5), y el de este informe.

**Base: `C:\dev\Agendamiento Reservas` @ `c4df3ab` · árbol limpio** (pieza 9). Las mediciones de `logs/` y de las
planillas se hicieron sobre esa base, antes del primer commit del encargo.

> Sin datos reales. `logs/`, las planillas y `config.json` se midieron en solo lectura, con sondas que tapan naves,
> viajes, puertos de la fila, contratos, números de reserva y el nombre del operador, e imprimen conteos, etiquetas de
> la interfaz y formas enmascaradas. Las capturas se leyeron con OCR sin mirarlas. Los HTML guardados se leyeron en un
> Chromium sin red y sin el JavaScript de la página. Los únicos nombres de puerto que aparecen son los que ya están en el
> código (el mapa de COSCO). Lo que trae datos reales quedó fuera del repo, en `revision_local/emisiones_2026-09-26.md`.

**Resumen:**
- **Ningún reservador pulsó hoy su botón final:** no hay números que anular. El único clic del programa que no se pudo
  descartar como origen de una reserva es el «Book Now» de HYUNDAI (14:18 y 14:25). No se cree que la cree, pero no está
  verificado.
- **Se activaron dos frenos**, y lo que les toca no se implementó:
  - **el inicio de «todas» falló por otras causas,** no por un primer login más lento que lo que el programa espera:
    MSC respondió HTTP 502 y CMA estaba en mantenimiento. En ONE, el asistente se reinició después de un login nuevo,
    por una causa que no se midió;
  - **el modal de HYUNDAI apareció con la nave pedida en la lista.**
- **Los cinco ítems decididos quedaron hechos,** uno por commit.

## Veredicto del PASO 0, por parte del encargo

| Parte | Veredicto | Qué quedó |
|---|---|---|
| Las emisiones de hoy y sus números | **DESCARTE:** la premisa era falsa | Ningún botón final pulsado. La nota local lo dice y no trae números |
| Por qué falla el inicio de «todas» | **PREGUNTA** (freno del encargo): MSC y CMA, otra causa medida; ONE, sin causa medida | Diagnóstico abajo. No se implementó el login previo de todas las navieras |
| El modal de HYUNDAI | **PREGUNTA** (freno del encargo): apareció con la nave pedida en la lista | Medido abajo. Nada cambió en HYUNDAI |
| La forma del número de CMA y COSCO | **NOTA:** sin confirmaciones, no se mide | `FORMA_BOOKING` no cambió: CMA y COSCO siguen sin llegar a EMITIDA |
| Los pendientes de `CICLO-cola-seis-items.md` | **CICLO** donde la evidencia alcanza | Lo decidido, más dos mediciones: el «Next» de ONE y la lista de HYUNDAI |
| Los cinco ítems decididos | **CICLO** | Cinco commits |

## Las corridas de hoy

Seis corridas en `logs/`, de 14:13 a 14:26: una de «todas» (6 filas de CONSOLIDADO) y cinco de una fila cada una. No
hubo ninguna corrida real fuera de `logs/`: se buscó en `C:\dev`, en todo el perfil, en las carpetas de `C:\` que no son
del sistema y en las otras unidades. Fuera de `logs/` solo están las carpetas de la red de pruebas en el temporal, que
no abren ningún portal.

| Hora | Naviera | Login | Cómo terminó |
|---|---|---|---|
| 14:13 | ONE | Nuevo, 33 s | NO ENVIADA: a mitad de Container & Cargo, el asistente volvió a Search Schedule |
| 14:14 | MSC | **Falló** | Sin procesar: HTTP 502 dos veces |
| 14:15 | CMA | Nuevo, 24 s | NO ENVIADA: eBusiness en mantenimiento, el Origen no apareció |
| 14:17 | COSCO | Nuevo, 29 s | OK-EJEMPLO, detenida en la guarda |
| 14:18 | HYUNDAI | Nuevo, 5 s | NO ENVIADA: el modal «Alternate Vessel Option» |
| 14:18 | MAERSK | Ya había sesión | REVISAR: la nave está en la lista, sin «Book» |
| 14:20 | MSC | Nuevo, 22 s | OK-EJEMPLO, detenida en la guarda |
| 14:21 | ONE | Ya había sesión | OK-EJEMPLO, detenida en la guarda, tras los tres «Next» |
| 14:24 | CMA | Nuevo, 15 s | NO ENVIADA: el mismo corte; la página se cerró a las 14:25:13 |
| 14:25 | HYUNDAI | Nuevo, 6 s | NO ENVIADA: el mismo modal |
| 14:25 | MAERSK | Ya había sesión | REVISAR: lo mismo |

## Las emisiones (premisa refutada)

El encargo decía que, después de «todas», Marcelo emitió una a una con el candado abierto y que varias salieron
confirmadas. En la evidencia no hay ninguna emisión:
- **Ningún reservador pulsó su botón final.** Cada uno anota una línea justo antes de pulsarlo: «MODO EMISIÓN REAL» en
  ONE, MSC y COSCO, y «EMISIÓN: Pulsando …» en HYUNDAI, MAERSK y CMA. Hoy las dos formas dan 0.
- **Tampoco hay ninguna fila EMITIDA ni ENVIADA – REVISAR EN PORTAL,** ni capturas de confirmación. Los estados de hoy:
  NO ENVIADA 5, OK-EJEMPLO 3, REVISAR 2, y MSC sin procesar.
- **Tres reservas llegaron a la guarda, y las tres la encontraron cerrada:** COSCO, MSC y ONE dicen «Me DETENGO …». Las
  otras se detuvieron antes, así que en ellas el candado no se consultó.
- **Control:** la misma cuenta encuentra las emisiones del 21 al 23-09.

Por eso no hay números que dejar en `revision_local/`. La nota local (`emisiones_2026-09-26.md`) lo dice y lista qué
revisar en los portales. Si Marcelo vio reservas confirmadas de hoy, los logs no pueden descartar tres orígenes:
1. un botón final pulsado a mano en una ventana que quedó abierta en la guarda (COSCO a las 14:18, MSC a las 14:21, ONE
   a las 14:22);
2. otro equipo;
3. el «Book Now» que el programa pulsó en HYUNDAI (14:18 y 14:25), antes del modal. No se cree que cree la reserva, porque
   en HYUNDAI la crea «Create NOW», pero no está verificado.

Una vez la página se cerró a mitad de un paso (CMA, 14:25:13). A las 14:14:40, en ONE, solo se soltó un marco, cuando el
asistente se reinició. No se sabe quién ni qué cerró la de CMA.

**El freno de las emisiones no se activó:** no hay ninguna EMITIDA sin confirmación ni ninguna fila enviada dos veces,
porque ningún botón final se pulsó.

## El inicio de «todas»: qué falló y por qué (FRENO)

**La hipótesis era que el primer login tarda más de lo que el programa espera. No se confirma.** En la corrida de
«todas» falló un solo login de seis, el de MSC, y por un error del portal. Los otros cortes fueron después de entrar.

En las cinco corridas de «todas» de `logs/` (del 21 al 26-09) hay 30 logins:
- 22 entraron;
- en 6 ya había una sesión;
- 2 fallaron, los dos de MSC y los dos en una página de error 502.

**MSC (HTTP 502):**
- **El portal respondió HTTP 502 en 4 de sus 7 logins.** En el del 21-09 el log no lo dice: está en su captura.
- **Hoy salió dos veces.** La primera fue al pulsar «Next» tras el usuario; el programa recargó y siguió. La segunda,
  al pulsar el botón de entrar: la captura final muestra la página de error de Chrome, que el OCR lee «HTTP ERROR S02».
- **El programa recarga solo si el 502 sale en el primer paso.** Con el segundo no recargó, y la sesión no quedó.
- **No fue una espera corta:** la página final era un error ya cargado. Lo que falta es un reintento después del botón
  de entrar.
- **Una correlación que no se sabe si es causa:** en los 4 logins con 502, el clic en «Next» respondió en 0,8-0,9 s, y en
  los 3 sin 502, en 3,9-4,3 s. Puede ser un síntoma (el portal falla rápido); no está medido.

**CMA (mantenimiento):**
- El login entró las dos veces. Después, la página de reservas mostraba «We are improving the eBusiness area».
- La ventana anunciada iba de 14:00 a 21:00, hora local, y las dos corridas cayeron dentro.
- El formulario de Click & Book no estaba en el HTML (0 campos de origen), y el programa cortó en el Origen, sin pulsar
  nada.
- El motivo que escribió, «no encontré la sugerencia del puerto», no dice lo que pasó: faltaba el campo mismo.
- El 25-09 el mismo paso funcionó.
- En la segunda corrida la página se cerró a las 14:25:13 y no dejó evidencia. Que allí también estaba el aviso se
  infiere de su captura del inicio de eBusiness, que lo muestra, y de la ventana anunciada.

**ONE (el asistente se reinició):**
- **Entró, armó la búsqueda, eligió la nave y pasó Booking Parties.** A mitad de Container & Cargo, unos 60 s después de
  pulsar «Sign In», la página volvió a Search Schedule con el formulario en sus valores por defecto: 0 resultados, «Next
  2 weeks» y carga seca.
- **El programa cortó bien:** no encontró la pantalla de Container & Cargo y no pulsó nada.
- **El «login lento» es un artefacto del programa.** `login_one` espera la URL `**ecomm.one-line.com/one-ecom**`, pero
  ONE aterriza en www.one-line.com. Esa espera venció en los 4 logins nuevos medidos: los 4 anotan «no confirmé redirect
  en 25s» y tardan 32-33 s. Cuánto tardó de verdad el portal no se sabe.
- **La diferencia medida es sesión nueva contra sesión ya iniciada:**
  - con sesión iniciada, 6 recorridos del asistente pasaron sin reiniciarse (5 del 21-09 y el de las 14:21 de hoy);
  - con sesión nueva, 1 llegó al asistente, y se reinició;
  - los otros 3 logins nuevos cortaron antes, con la nave no encontrada.

  Con un solo caso, que la sesión nueva sea la causa es compatible pero no está confirmado. Tampoco se descartan una
  respuesta del portal al abrir el desplegable «Container Type/ Size» (el reinicio coincide con ese clic) ni una
  inestabilidad del portal a esa hora.

**HYUNDAI y MAERSK** entraron sin problemas y cortaron por otras razones: el modal y la nave sin «Book».

**Por qué frena:** de los cinco cortes de «todas», cuatro tienen otra causa medida: MSC y CMA en el inicio, HYUNDAI y
MAERSK después de entrar. El login previo de todas las navieras no los habría evitado. El de ONE no se midió. No se
implementó nada del inicio. Lo que sí ayudaría, para que decidas:
- en MSC, reintentar después de un 502 al entrar;
- en ONE, esperar la URL con que el portal aterriza hoy;
- en CMA, reconocer el aviso de mantenimiento y decirlo como motivo;
- en ONE, una corrida con `AQUASHIELD_TRAZA=1` y login nuevo que llegue al asistente, para ver qué lo reinicia.

## El modal de HYUNDAI (FRENO)

- **La nave de la fila estaba en la lista,** en las dos corridas: 3 de las 6 tarjetas la traen. Una la trae como «MAIN
  VESSEL» con otra nave como «1ST VESSEL», otra solo como «1ST VESSEL», y otra en los dos campos.
- **El programa eligió la primera que calza,** la de «MAIN VESSEL» con otra «1ST VESSEL». HYUNDAI calza todavía con el
  texto de toda la tarjeta y no aplica la regla de la próxima salida.
- **Después de «Book Now», el modal no ofrece otra nave.** Pregunta qué hacer si la pedida no estuviera disponible, con
  tres opciones:
  1. «Book on next available vessel (Any)»;
  2. «Book on next available vessel (if within N weeks)»;
  3. «I do not want to choose an alternate vessel»: si no está disponible, la reserva se rechaza.
- **Según la captura, viene marcada la opción 1.** El HTML guardado no dice qué opción está marcada (el atributo
  `checked` no refleja el estado): la marca se midió en la captura, contra la vista activa de la misma página, que tiene
  el mismo estilo.
- **Pulsar OK sin tocar nada**, que era lo que hacía el programa hasta `a198645`, autorizaba a HYUNDAI a pasar la reserva
  a la próxima nave disponible.
- **El programa hoy corta ahí,** NO ENVIADA, con el motivo «HYUNDAI ofreció otra nave en lugar de la pedida», que no
  describe el modal.
- **La lista de HYUNDAI ya tiene HTML guardado:** cada tarjeta trae «MAIN VESSEL», «ROUTE», «OPERATOR», «1ST VESSEL» y
  tres fechas con hora.

Lo que decides tú, y nada de eso se tocó:
1. **Qué opción elegir en el modal.** Lo coherente con tu regla sería la 3; elegirla es un clic nuevo antes de la guarda.
2. **Si la nave de la fila es la «MAIN VESSEL» o la que sale de Chile («1ST VESSEL»),** para calzar con ese campo y no con
   toda la tarjeta.
3. **El texto del motivo.**

## Los cinco ítems decididos

| # | Ítem | Commit | Qué cambia hoy en las planillas |
|---|---|---|---|
| 1 | CSCL y COSCO SHIPPING son prefijos de naviera | `479ebf6` | Nada: 0 de 72 filas los traen solos |
| 2 | MANUAL calza por palabra entera | `9036d2c` | Nada: 0 filas con MANUAL |
| 3 | El viaje calza por palabra entera (MAERSK, el único que lo comparaba como parte del texto) | `3968cfa` | Nada: en las 5 listas guardadas de MAERSK (43 salidas), el viaje calza en las mismas 2 |
| 4 | MSC pierde su clic genérico antes de la guarda | `796d95a` | Nada medido: en los 7 logins y las 9 búsquedas, el selector encontró su botón, salvo una vez, en que el clic genérico tampoco sirvió |
| 5 | COSCO normaliza el puerto de carga antes de su mapa | `49de5d4` | Nada: las 72 filas traen CORONEL, LIRQUEN o SAN VICENTE, sin coma ni tilde, y el mapa ya las traducía |

Las planillas medidas son la de la carpeta y la subida al panel, con el lector del panel (72 filas).

**Ítem 1 · CSCL y COSCO SHIPPING.**
- **Qué se sumó:** CSCL y SHIPPING a `NAVES_PREFIJO`. COSCO SHIPPING entra como sus dos palabras, igual que CMA CGM, así
  que tampoco piden una nave «SHIPPING» sola ni «SHIPPING COSCO».
- **La versión descartada:** una primera, con la frase exacta, se descartó en la revisión por eso (pieza 4).
- **Antes:** hasta `c4df3ab`, «CSCL» o «COSCO SHIPPING» pedían una nave, y cada naviera calzaba con toda tarjeta que la
  trajera. En las listas guardadas de COSCO, 2 de 16 textos de nave empiezan con CSCL (medido en el encargo 29,
  `CICLO-cola-seis-items.md`).

**Ítem 2 · MANUAL.**
- **La regla:** `_fila_manual` usa `_palabra_en`, la misma frontera de palabra del calce de la nave.
- **Ya no son MANUAL, y piden esa nave:** «MANUALMENTE», «SEMIMANUAL», «MANUAL2» o «MANUALÉ».
- **Siguen siendo MANUAL:** «(MANUAL)», «NAVE-MANUAL» y «NAVE_MANUAL».
- **Nada más cambia:** el panel sigue dejando sin marcar las MANUAL.

**Ítem 3 · El viaje.** Se revisó cada naviera:
- COSCO ya calzaba el viaje entero, desde el encargo 29.
- MSC, ONE, HYUNDAI y CMA no comparan la columna de viaje. CMA la lee y no la usa.
- MAERSK lo comparaba como parte del valor de «Vessel/voyage». Ahora va con `_palabraEn`, sin distinguir mayúsculas:
  «541W» no es el viaje de «1541W» ni de «541WA».

MAERSK (`_mk_elegir_nave`) y COSCO (`_cosco_calzan`) siguen usando el viaje como filtro suave: si ninguna salida de la
nave lo trae, eligen entre todas las de la nave y no lo avisan. Eso no cambió (residual).

**Ítem 4 · MSC.**
- **El login:** pulsa el «Next» con su selector de texto. El de entrar lo pulsa con un selector que junta los textos
  «Login», «Sign In», «Next» e «Iniciar» con `button[type=submit]`, y toma el primero que aparezca en la página. Si no
  encuentra uno, lo anota y no pulsa nada; la verificación de la sesión, que no cambió, dice si entró.
- **«Search Schedule»:** va con un ayudante nuevo, `_msc_buscar_itinerarios`, que corta como objetivo no encontrado si no
  encuentra el botón.
- **El clic genérico** (`_JS_CLICK_BTN`) queda solo en el envío de ONE y de MSC, después de la guarda, que no se tocó.
- **La foto de `test_clics` ahora lo ve** con la forma «primero-que-calce-el-texto». La foto recorre los reservadores y
  sus ayudantes. El login de MSC no está en ese universo, así que lo vigila su propia prueba.

**Ítem 5 · El puerto de COSCO.** `_cosco_puerto_de_la_celda` normaliza la celda antes del mapa:
- toma la parte antes de la primera coma, la pasa por `_norm_ctrl` (mayúsculas, sin tildes) y usa como separador todo lo
  que no es letra ni número;
- quita el «CHILE» del final, las veces que venga;
- «CORONEL, CHILE», «Coronel (Chile)», «CORONEL–CHILE», «CORONEL · CHILE», «Lirquén» y «Concepción» dan «Lirquen»;
- una celda con solo el país («CHILE», «(Chile)», «CHILE CHILE») corta como celda sin puerto: buscar «CHILE» calzaría con
  cualquier sugerencia de Chile;
- un puerto que no está en el mapa se busca normalizado, en mayúsculas: las sugerencias de COSCO no llevan tildes, y su
  búsqueda no distingue mayúsculas.

**Convención:** «hasta `c4df3ab`» quiere decir «antes del encargo 30», en este informe y en los comentarios del código,
como «hasta `f68ce6c`» en el encargo 29.

Cada ítem pasó por una revisión adversarial antes de su commit:
- en el ítem 1, tres revisores, uno por enfoque, en dos rondas;
- en los otros, dos por ítem;
- después, una verificación de los arreglos de los ítems 2 a 5.

Encontraron huecos reales en los cinco: están en la pieza 4.

## Expectativas que cambiaron (antes → ahora)

| Prueba | Antes | Ahora |
|---|---|---|
| `test_ayudantes.TestFilaSinNave.test_fila_sin_nave` | «CSCL», «COSCO SHIPPING», «SHIPPING» y «SHIPPING COSCO» pedían una nave; la foto de `NAVES_PREFIJO` tenía 9 | No la piden; la foto suma CSCL y SHIPPING. «MANUALMENTE» y «NAVE SEMIMANUAL» piden su nave (antes eran MANUAL) |
| `test_ayudantes.TestFilaSinNave.test_fila_manual` | «MANUALMENTE» era MANUAL | No lo es; y 14 casos nuevos de la frontera de palabra (cifras, Ñ, tildes, Ü, «_», signos, MANUAL dos veces) |
| `test_clics.TestMaersk.test_js_salidas_lee_la_salida_y_si_se_puede_reservar` | El viaje «541W» calzaba en «1541W», «541W», «541WA» y «NAVE/541W»: [True, True, True, True] (caso nuevo) | [False, True, False, True], también con el viaje en minúsculas |
| `test_clics` (`GENERICOS`) | Ninguna forma veía `_JS_CLICK_BTN` | La forma «primero-que-calce-el-texto» lo ve. `PERMITIDOS` no cambia: ya no queda ningún uso antes de una guarda |
| `test_clics.TestCosco.test_puerto_de_carga_sin_sugerencia_corta` | «CORONEL, CHILE» buscaba «CORONEL», «Lirquén» buscaba «Lirquén», y «CHILE» buscaba «CHILE» | Buscan «Lirquen», «Lirquen» y cortan; 24 casos nuevos. Los de antes esperan lo mismo |

**Pruebas nuevas (2):** `test_clics.TestMsc.test_login_sin_clic_generico` y `test_search_schedule_sin_boton_corta`.

**`test_candado` no cambió:** su archivo es igual en los cinco commits (`git diff c4df3ab 49de5d4 -- tests/test_candado.py`
da 0 líneas), y pasó en cada gate. `PERMITIDOS`, la foto de los clics permitidos antes de la guarda, tampoco cambió.

**Mutaciones:**
- Entran 29: 3 en el ítem 1, 6 en el 2, 4 en el 3, 8 en el 4 y 8 en el 5.
- Sale 1: `manual-por-palabra`, que ahora sería igual al código.
- `cosco-origen-mapa-con-mayusculas` se reescribió con el mismo id, porque su texto ya no existe.
- `prefijos-sin-hmm` y `prefijos-sin-los-de-hoja-alias` se reanclaron: la constante `PREFIJOS` cambió.

## Veredicto por naviera: ¿lista para una emisión real de prueba?

| Naviera | Veredicto | Qué le falta | Lo nuevo de este encargo |
|---|---|---|---|
| **MSC** | **Casi lista** | Tu decisión sobre el reintento tras un 502 al entrar. Con candado cerrado, la corrida de las 14:20 llegó a Summary | Sin el clic genérico antes de la guarda; el 502 al entrar, medido (4 de 7 logins) |
| **ONE** | **Casi lista** | Una corrida con login nuevo que llegue a Review Booking: con sesión ya iniciada llegó hoy, pasando los tres «Next» | El «Next» único, medido en una corrida real; el reinicio del asistente tras un login nuevo, sin explicar |
| **COSCO** | **No para emitir** | El programa no reconoce el número de su confirmación. Con candado cerrado llegó hoy a la guarda | El puerto de carga, normalizado |
| **HYUNDAI** | No | Tus tres decisiones del modal y de la tarjeta; aplicar la próxima salida | El modal, medido: sale con la nave pedida y trae «Any» marcada |
| **CMA** | No | Que salga del mantenimiento; «Validar ruta», el HTML de su lista, la próxima salida y su número | Hoy no pasó del Origen: eBusiness en mantenimiento |
| **MAERSK** | No | Una fila cuya nave tenga una salida con «Book», para llegar a la revisión y medir la casilla de términos | El viaje, por palabra entera |

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\correr.py --mutaciones --filtro prefij
python tests\correr.py --mutaciones --filtro sin-nave-
python tests\correr.py --mutaciones --filtro manual-
python tests\correr.py --mutaciones --filtro comodines-
python tests\correr.py --mutaciones --filtro filas-
python tests\correr.py --mutaciones --filtro mk-
python tests\correr.py --mutaciones --filtro msc-
python tests\correr.py --mutaciones --filtro cma-
python tests\correr.py --mutaciones --filtro hmm-remark
python tests\correr.py --mutaciones --filtro maersk-vuelve
python tests\correr.py --mutaciones --filtro one-campo-contrato
python tests\correr.py --mutaciones --filtro one-cierre-a-ciegas
python tests\correr.py --mutaciones --filtro one-contrato-el-primero
python tests\correr.py --mutaciones --filtro one-nave-viaje-solo
python tests\correr.py --mutaciones --filtro teclado-
python tests\correr.py --mutaciones --filtro textarea-
python tests\correr.py --mutaciones --filtro cosco-origen
python tests\correr.py --todo
```

Las sondas son de solo lectura y no se versionan, porque leen datos reales. Quedaron en la carpeta temporal de la
sesión (`scratchpad\e30`), que puede limpiarse; sin ellas, estos números no se re-miden. Cada una aborta si su control
no da lo esperado:
- **`leer_log.py <sufijo>`:** el `log.txt` de una corrida, tapado.
- **`logins.py`:** cada login de cada corrida, cómo terminó, cuánto tardó y sus señales (502, redirect sin confirmar,
  DataDome).
- **`otras_copias.py`:** copias del programa y carpetas de corrida de hoy fuera de `logs/`.
- **`pantallas_hoy.py` y `texto_tapado.py <sufijo> <html>`:** en qué pantalla quedaron ONE y CMA.
- **`hmm_hoy.py`, `hmm_modal_texto.py` y `hmm_etiquetas.py`:** la lista y el modal de HYUNDAI contra la nave de la fila.
  La marca del modal la midieron los verificadores con `hmm_radio_cajas.py`.
- **`planillas.py`:** lo que traen las planillas en las celdas que tocan los ítems.
- **`mk_viaje.py`:** el viaje de MAERSK como parte del texto (el programa de `c4df3ab`, que carga con `git show`) y como
  palabra entera, en las listas guardadas.
- **`v_*.py` y `verif_*.py`:** las sondas de los verificadores. Miden el 502 por OCR, las capturas de ONE y el aviso de
  CMA; la ventana del aviso sale de `verif_cma_ventana.py`.

## NO retroceder (pieza 2)

- **No vuelvas a tratar COSCO SHIPPING como frase exacta:** «SHIPPING» sola y «SHIPPING COSCO» pedirían una nave y
  calzarían con toda nave COSCO SHIPPING.
- **No vuelvas a MANUAL como parte del texto,** ni al viaje de MAERSK como parte del texto.
- **No vuelvas a usar `_JS_CLICK_BTN` antes de una guarda:**
  - la foto de `test_clics` lo ve en los reservadores y sus ayudantes;
  - en el login de MSC lo vigila `test_login_sin_clic_generico`;
  - los otros logins no están vigilados.
- **No traduzcas el puerto de COSCO sin normalizarlo,** ni busques el país solo.
- **No leas el estado de un radio en el HTML guardado:** el atributo `checked` no lo refleja; se ve en la captura.
- **No des por lento el login de ONE por «no confirmé redirect en 25s»:** esa espera venció en los 4 logins nuevos
  medidos, porque espera una URL con que ONE ya no aterriza.

## Universo y cobertura (pieza 3)

- **`logs/`:** 15 carpetas, las 15 con `log.txt`; 0 descartadas. Las de hoy son 6, con 51 HTML (con sus marcos) y
  66 capturas.
- **Fuera de `logs/`:** 0 corridas reales. Hay copias de la red de pruebas en el temporal (sintéticas). El recorrido
  descartó 8 carpetas por permiso, más las que desaparecieron mientras se recorrían (sandboxes de la red de pruebas en
  curso: 8 en la medición del informe). Los verificadores descartaron otras 63 en su recorrido amplio.
- **Logins:** 30 en las cinco corridas de «todas» y 10 en las otras; MSC, 7.
- **Listas:** HYUNDAI, 2 listas de 6 tarjetas; MAERSK, 5 listas con 43 salidas.
- **Planillas:** 72 filas, las dos planillas con el lector del panel.
- **No medido:**
  - qué muestra la página de reservas de CMA en la segunda corrida, que se cerró;
  - qué reinicia el asistente de ONE;
  - si el modal de HYUNDAI sale también con una tarjeta directa, sin transbordo;
  - si el «Book Now» de HYUNDAI deja algo en el portal;
  - la lista de CMA y la revisión de MAERSK: no se llegó a ellas;
  - la forma del número de CMA y COSCO: no hay confirmaciones.

## Defectos de instrumento cazados (pieza 4)

1. **El marcador de emisión:** la primera cuenta usó solo «MODO EMISIÓN REAL», que escriben ONE, MSC y COSCO; HYUNDAI,
   MAERSK y CMA escriben «EMISIÓN: Pulsando». Un verificador lo cazó. Las dos formas dan 0 hoy.
2. **«Las 6 corridas con el candado cerrado» decía más de lo medido:** solo 3 consultaron la guarda. Se corrigió a «ninguna
   llegó al botón final».
3. **«Ningún radio marcado» en el modal de HYUNDAI era falso:** el HTML serializado no trae el estado. Se midió en la
   captura, calibrando con la vista activa de la misma página.
4. **`logins.py` no vio las reservas de la corrida del 21-09,** que escribe «fila N:» y no «Reserva N:». Además contó el
   502 de MSC 3 veces en vez de 4: el del 21-09 no está en el log, solo en su captura.
5. **La primera lectura del login de ONE lo tomó por lento:** el patrón de URL que espera el programa no calzó en ningún
   login nuevo.
6. **La primera versión de este informe decía que la página se cerró dos veces:** en ONE solo falló el HTML de un marco;
   la página se guardó.
7. **`leer_log.py` dejó ver en la consola una nave de transbordo** del detalle de COSCO y parte del texto de la tarjeta de
   HYUNDAI, que no vienen tras «NAVE:». Solo en la salida de la sesión, en ningún archivo; hay que taparlos antes de
   volver a usarla.
8. **`pantallas_hoy.py` marcó «origin» en CMA** por «B/Ls Originales» del menú, no por un campo Origen.
9. **`verif_cma_mant.py` no lee la ventana del aviso** (su regex no admite la coma que sigue al año) y dice «None»; la
   ventana se midió con `verif_cma_ventana.py`.
10. **`mk_viaje.py` fallaba sobre el repo al día**, porque buscaba el código de antes del ítem 3; ahora carga `c4df3ab`.
11. **La revisión del código cazó, por ítem:**
    - **Ítem 1:** la frase exacta (se rehízo), un comentario que atribuía CSCL al código, y una mutación que era la misma
      que otra.
    - **Ítem 2:** la frontera con tildes, Ü y «_» sin prueba, y una celda con MANUAL dos veces.
    - **Ítem 3:** dos mutaciones que no aislaban un límite de la palabra, y las mayúsculas del viaje sin prueba.
    - **Ítem 4:**
      - un `raise` directo en el reservador, que la prueba de «nada corta después de la guarda» no veía (pasó a un
        ayudante);
      - comentarios que decían «por su texto» del `button[type=submit]`;
      - la prueba del login no fijaba sus selectores.
    - **Ítem 5:**
      - la coma sin prueba;
      - «CHILE CHILE», que buscaba «CHILE»;
      - los signos pegados al país (la raya), que lo dejaban;
      - dos comentarios de mutación al revés.
12. **El primer gate del ítem 1 se detuvo a mitad** para corregir lo de la revisión. Sus dos procesos se cerraron a mano,
    sin tocar el panel web que estaba abierto ni los procesos de otra sesión.

## Premisas del encargo contrastadas (pieza 5)

- **«Varias reservas fallaron al inicio, en el login»:** refutada. Falló un login de seis (MSC, 502 del portal); los otros
  cortes fueron después de entrar.
- **«Después emitió una a una con el candado abierto, y varias salieron confirmadas»:** refutada en la evidencia. En las
  corridas una a una ningún reservador pulsó su botón final; las que llegaron a la guarda la encontraron cerrada.
- **«El primer login tarda más de lo que el programa espera»:** no confirmada. En ONE es un artefacto de la espera; en MSC,
  un 502; en CMA, un mantenimiento.
- **«Con las confirmaciones de hoy, mide la forma del número de CMA y COSCO»:** no hay confirmaciones.
- **«El modal de HYUNDAI ofrece otra nave»,** la lectura del encargo 28: refutada. Es una pregunta, con «Any» marcada.
- **«MSC usa su clic genérico antes de la guarda»:** confirmada, en 3 lugares.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| El modal de HYUNDAI: qué opción elegir, con qué campo calzar la nave, el texto del motivo y la próxima salida | FRENO: lo decides tú | …decides |
| Si el «Book Now» de HYUNDAI deja algo en el portal | No está medido | …revisas el portal de HYUNDAI |
| MSC no reintenta tras un 502 al entrar | El inicio frenó: no se implementó | …decides el reintento |
| ONE espera una URL con que ya no aterriza (25 s en cada login nuevo), y su asistente se reinició una vez tras un login nuevo | Frenado; un solo caso | …decides corregir la espera, o una corrida con traza lo explica |
| CMA en mantenimiento corta con un motivo que habla del puerto | No decidido | …decides reconocer el aviso |
| La página de CMA se cerró a las 14:25:13 | No se sabe quién ni qué la cerró | …se repite |
| MAERSK y COSCO: si ninguna salida trae el viaje, eligen entre todas las de la nave sin avisarlo | La regla es de la nave, no del viaje | …decides avisar o cortar |
| El botón de entrar de MSC se toma entre sus textos y `button[type=submit]`, el primero de la página | No decidido: el ítem era quitar `_JS_CLICK_BTN` | …decides exigir el botón por su texto |
| `_one_esta_en_paso('booking-parties')` da verdadero en Search Schedule (la barra de pasos lo nombra) | Allí no hay ningún «Next», así que el paso corta igual | …una pantalla sin formulario trae un «Next» |
| CMA y COSCO sin forma de número | Sin confirmaciones | …haya una confirmación guardada |
| La casilla de términos de MAERSK y la fecha desde mañana | No se llegó a la revisión | …una fila llega a la revisión |
| Los demás residuales de `CICLO-cola-seis-items.md`, sin cambios; entre ellos, CMA calza todavía con el texto de toda la tarjeta, el motivo de COSCO con la celda vacía, y `_one_esperar_paso` con su resultado ignorado | Sin evidencia nueva | …según ese informe |
| `leer_log.py` deja ver naves que no vienen tras «NAVE:» | Instrumento del scratchpad | …se vuelva a usar |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v14**. El ciclo empezó con la v13; la v14 entró a las 15:38, antes de los ítems 2 a 5 y de este
informe, y su único cambio que toca este informe es la pieza 9, que se agregó.
- **PASO 0 con sus cuatro valores:**
  - DESCARTE (las emisiones);
  - PREGUNTA, por los frenos del encargo (el inicio y HYUNDAI);
  - NOTA (la forma del número);
  - CICLO (los cinco ítems y dos mediciones).
- **FRENAR cuando la decisión es de negocio:** los dos frenos del encargo se reportan sin implementar; lo decidido
  siguió, porque ningún freno lo toca.
- **Control positivo que aborta:** en cada sonda; la de emisiones, contra las corridas del 21 al 23-09.
- **Todo salto silencioso lleva contador:**
  - 0 carpetas de `logs/` descartadas;
  - fuera de `logs/`, 8 por permiso y las sandboxes que desaparecían;
  - 63 del recorrido amplio de los verificadores.
- **Todo registro es una hipótesis:** los textos del programa no dicen lo que pasó.
  - El log dice «no confirmé redirect», y no era lentitud.
  - El motivo de HYUNDAI dice «ofreció otra nave», y no la ofrecía.
  - El de CMA habla del puerto, y faltaba la página.
- **Verificación adversarial:**
  - cinco verificadores escépticos sobre el diagnóstico, solo con sondas que tapan, que corrigieron cuatro afirmaciones
    (pieza 4);
  - la revisión de cada ítem y la de este informe, con tres enfoques.
- **El negativo tiene que morder:** en cada commit, el censo filtrado a las mutaciones nuevas y a las que nombran una
  prueba cambiada; al cerrar, el censo completo.
- **El cambio y su guardián en la misma operación:** la foto de `test_clics` ve `_JS_CLICK_BTN` en el mismo commit que se
  lo quita a MSC.
- **Cada reemplazo afirma su viejo una vez; el EOL se preserva:** los parches abortan si el texto no calza, y cada archivo
  commiteado tiene 0 CR.
- **Choques entre reglas:**
  1. **Los frenos del encargo contra lo decidido.** El encargo no dice si un freno para todo. Se resolvió leyendo el freno
     del inicio, que trae «reporta cuál, sin implementar», como un freno de su parte, y se siguió con lo decidido, que
     ningún freno toca. Lo urgente, las emisiones, se te mandó apenas se midió.
  2. **La regla del módulo «nunca por el primero de un selector genérico» contra el botón de entrar de MSC.** Ese botón
     todavía se toma entre sus textos y `button[type=submit]`, el primero de la página. El ítem era quitar
     `_JS_CLICK_BTN`, no cambiar ese selector, que ya estaba. Queda en el residual.
  3. **El cambio de versión a mitad del ciclo:** se aplica la vigente (v14), como dice la skill.

Reglas del módulo: casos sintéticos; la sonda de secretos antes de cada commit; nada de `logs/` en el repo; ningún clic
nuevo antes de la guarda; `test_candado` sin cambios; los textos en español con tuteo.

## Entregable (pieza 8)

- **Este `.md`:** no se convirtió en página; se leyó como texto.
- **`CLAUDE.md` al día,** en el mismo commit.
- **La nota local `revision_local/emisiones_2026-09-26.md`,** fuera de git.

**La red por commit** (`scratchpad\e26\red_por_commit.py`, del encargo 26):

| Commit | Pruebas | Mutaciones | Pares |
|---|---|---|---|
| `c4df3ab` (base) | 370 | 885 | 1095 |
| `479ebf6` (ítem 1) | 370 | 888 | 1098 |
| `9036d2c` (ítem 2) | 370 | 893 | 1104 |
| `3968cfa` (ítem 3) | 370 | 897 | 1108 |
| `796d95a` (ítem 4) | 372 | 905 | 1117 |
| `49de5d4` (ítem 5) | 372 | 913 | 1125 |

**Gates.** En cada uno, la suite completa pasó con 0 cambios en los originales, y la sonda de secretos dio 0 sobre el
árbol y sobre lo agregado con `git add`. Los filtros de un mismo gate se solapan: la tabla da las mutaciones y los pares
distintos.

| Commit | Suite completa | Censos filtrados |
|---|---|---|
| Ítem 1, `479ebf6` | 370 en verde | 4 filtros: 61 mutaciones y 92 pares, todas muerden |
| Ítem 2, `9036d2c` | 370 en verde, dos veces | 5 filtros: 73 mutaciones y 105 pares; y tras sumar casos, `manual-`: 14 y 25. Todas muerden |
| Ítem 3, `3968cfa` | 370 en verde | `mk-`: 33 mutaciones y 38 pares, todas muerden |
| Ítem 4, `796d95a` | 372 en verde | 10 filtros: 158 mutaciones y 202 pares, todas muerden. El mensaje del commit dice 167: es la suma con las repetidas |
| Ítem 5, `49de5d4` | 372 en verde | `cosco-origen`: 17 mutaciones y 17 pares, todas muerden |

- **El primer gate del ítem 1 se detuvo a mitad** para corregir lo que encontró la revisión, y se repitió completo.
- **Los ítems 2 a 5 se probaron antes en copias de simulación con git,** una por ítem, con sus pruebas y el censo de sus
  mutaciones nuevas.
- **Censo completo final sobre `49de5d4`:** pasó, en 51 minutos.
  - 372 pruebas, y la copia de control, sin mutar, pasa;
  - 913 mutaciones y 1125 pares: los 1125 muerden;
  - 0 pruebas sin mutación y 0 cambios en los 2555 archivos originales fotografiados.

## Qué decides tú

1. **HYUNDAI:** la opción del modal, el campo de la nave (MAIN VESSEL o 1ST VESSEL) y el motivo.
2. **El inicio:** el reintento de MSC tras un 502 al entrar, la espera de ONE y el aviso de mantenimiento de CMA.
3. **El viaje en MAERSK y COSCO:** si el viaje que no está en ninguna salida de la nave debe avisar o cortar.
4. **El botón de entrar de MSC:** si debe ser solo por su texto.

Y revisa en los portales si hay reservas de hoy, sobre todo en HYUNDAI: ningún reservador pulsó su botón final, pero el
«Book Now» de HYUNDAI no está verificado.
