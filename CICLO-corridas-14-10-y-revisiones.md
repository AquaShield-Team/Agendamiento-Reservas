# Encargo 65 · Las corridas del 14-10, naviera por naviera, y las revisiones del diff de los encargos 62 a 64

**Base:** `C:\dev\Agendamiento Reservas` @ `9402321` · árbol limpio al empezar.

Con `metodo-ciclo` v24: el encabezado del archivo decía v24 y la sesión tenía cargada la v23, así que volví a invocar
la skill antes de medir. Las corridas, medidas sin abrir ningún portal: `logs/` y el HTML que guardó el programa,
cargado en un Chromium sin red. Las dos revisiones trabajaron en un clon dentro de la carpeta del encargo.

## En resumen

- **Las seis navieras llegaron a la guarda** (OK-EJEMPLO, sin emitir), con el candado cerrado y el programa de
  `9402321`.
- **Cinco pantallas finales calzan con su fila:** ONE, MSC, COSCO, HYUNDAI y MAERSK, en nave, viaje, puertos,
  contenedor, peso, temperatura y contrato. Donde la pantalla final no trae un campo, lo comprobé en una captura
  anterior o en `log.txt`, como en el encargo 49.
- **CMA-CGM armó la reserva con la nave de la fila, pero en otro viaje.** El viaje de su fila ya no está en la lista del
  portal: la fila es la misma del 02-10, cuando sí estaba y CMA lo eligió. Hoy CMA eligió la primera tarjeta con la
  nave, con cut-off el 27-10, porque nunca mira el viaje. El panel lo mostró como «lista para emitir».
- **MAERSK eligió «40 Reefer High» y «Standard (40´)», cada una la única de su lista:** la de tipos traía 2 opciones a
  la vista («40 Reefer High» y «40 Reefer Standard Shipper owned container only», la del embarcador) y la de los ajustes
  reefer, 3 («Standard (40´)», «Magnum (40´)» y «StarFreeze (40´)»). Es la primera vez que se miden las dos listas en
  el portal, y la pantalla final las muestra.
- **Las dos revisiones no encontraron nada crítico ni alto.** Entre las dos dieron 7 hallazgos distintos (3 los vieron
  las dos): 3 medios y 4 bajos. Arreglé 6, cada uno con su prueba y su mutación, salvo el de HYUNDAI, que era de la
  documentación. El séptimo, que el panel no valida de dónde le llegan los pedidos, es de antes de estos encargos: va al
  residual como propuesta.
- **`estable` ya está en `9402321`** (la miré en GitHub con `ls-remote`), con el diff que revisaron. **Sí queda listo
  para avanzarla** a estos dos commits, que arreglan lo que ellas encontraron. Dos condiciones: que subas `main` antes,
  y que nadie emita reservas de CMA-CGM hasta que decidas qué hacer con el viaje (ver «Lo decides tú»).

## El veredicto, naviera por naviera

| Naviera | Pantalla final | ¿Calza con su fila? | ¿Lista para la emisión real? |
|---|---|---|---|
| ONE · fila 5 | «Review Booking» | Sí, en todo | **Sí.** Declara «FISH FILLET,MEAT FRE/CHI/FRO, SALMONIDAE», como siempre (tu decisión del encargo 50) |
| MSC · fila 6 | «Summary» | Sí, en todo, en la misma pantalla | **Sí.** Hoy entró al primer intento; si el inicio de sesión falla, la fila queda NO ENVIADA |
| CMA-CGM · fila 7 | «Envío de la reserva» | **No en el viaje:** el de la fila no está en la lista del portal | **No, con esta fila.** Emitida, quedaría reservada otra salida. Además, CMA no llega nunca a EMITIDA: queda ENVIADA – REVISAR EN PORTAL |
| COSCO · fila 8 | «Booking Details» | Sí, en todo | **Sí, revisando el portal después:** COSCO tampoco llega a EMITIDA, y su formulario avisa «Your current allocation needs further confirmation…» |
| HYUNDAI · fila 9 | «Review & Book» | Sí, en todo | **Sí.** El peso y la temperatura solo están en `log.txt`; el contrato es el de `config.json`, como el 02-10 |
| MAERSK · fila 10 | «Review booking» | Sí, en todo | **Sí.** La nave y el viaje no están en la pantalla final, pero sí en la lista donde los eligió |

**Una condición vale para cuatro de las seis:** solo MAERSK y COSCO comparan el viaje de la fila. ONE, MSC, HYUNDAI y
CMA-CGM eligen por la nave. Hoy, en ONE, MSC y HYUNDAI, el viaje elegido era el de la fila, pero el programa no lo
comprueba: si el viaje de una fila deja de estar, esas tres harían lo mismo que CMA-CGM hoy (leído en el código).

## Las dos corridas de hoy

| Corrida | Carpeta | Qué pasó |
|---|---|---|
| Solo MAERSK | `web_todas_…_20261014_083422`, de 08:34:22 a 08:35:42 | Llegó a la guarda |
| Las otras cinco | `web_todas_…_20261014_083552`, de 08:35:52 a 08:41:36 | ONE, MSC, CMA-CGM, COSCO y HYUNDAI llegaron a la guarda |

- **El programa que corrió es el de `9402321`.** El panel se abrió a las 08:34:03 (`logs/actualizacion.json`), y
  `AQUASHIELD.py` era el de HEAD: el mismo blob, sin cambios desde las 00:06.
- **Las dos corridas, con el candado cerrado:** la segunda línea de cada `log.txt` dice «modo prueba, sin ninguna de sus
  tres llaves abierta».
- **La planilla** es la copia que guardó el panel a las 08:34, igual byte a byte a `Reservas AQUASHIELD.xlsx` (del
  08-10). Es la hoja CONSOLIDADO, filas 5 a 10, una por naviera. Las seis traen nave, viaje y contrato, y ninguna trae
  contenedor, temperatura, peso ni día de carga, así que el programa usa «40 HC REEFER» y 1 contenedor, y la temperatura
  y el peso de `config.json` (−20 °C y 22 500 kg).
- **Las filas de ONE, CMA-CGM y MAERSK son las mismas del 02-10;** las de MSC y COSCO, otras. Lo comparé por la cabecera
  de cada reserva en `log.txt`; HYUNDAI no la escribe.
- **El inicio de sesión:** MSC entró al primer intento, sin el 502. COSCO resolvió solo su rompecabezas. CMA-CGM mostró
  el deslizador de DataDome y lo pasaste en 8 s. MAERSK ya tenía la sesión abierta.

## Las seis pantallas finales

**Cómo se comparó, igual que en el encargo 49.** La pantalla final es la de la guarda: `<nav>_f<fila>_guarda.html` (la
página y sus marcos). Cada HTML se cargó en un Chromium sin red y sin el JavaScript de la página, y cada campo se leyó
por su etiqueta. La comparación con la fila usa las funciones del programa:
- la nave, con todas sus palabras, cada una como palabra entera (`_trae_la_nave`);
- el viaje, como palabra entera (`_palabra_en`);
- el puerto y el destino, por la ciudad (`_norm_ctrl`).

Si la pantalla final no trae un campo, la fuente es una captura anterior (por OCR, sin mirarla) o `log.txt`. El
comparador aborta si un campo no aparece en su fuente, y al final no faltó ninguno. Este informe no imprime la nave, el
viaje, el puerto ni el destino: dice si calzan.

| Campo | ONE | MSC | CMA-CGM | COSCO | HYUNDAI | MAERSK |
|---|---|---|---|---|---|---|
| Nave | Sí | Sí | Sí («Buque principal») | Sí (1.er tramo) | Sí («1st Vessel») | Sí, en la lista al elegir (OCR) y en `log.txt` |
| Viaje | Sí | Sí | **No** | Sí | Sí, pegado al código de servicio, como el 02-10 | Sí, en la lista al elegir (OCR) |
| Puerto de carga | Sí | Sí | Sí | Sí | Sí | Sí |
| Destino | Sí | Sí | Sí (descarga y rampa) | Sí | Sí | Sí, el destino final, como dice su regla |
| Contenedor | «REEFER 40FT High Cube x 1» | «40' high cube reefer», x 1 | «1 x 40' Reefer High Cube» | «40RQ - 40' Hi-Cube Refrigerated Container» | «RF/4H X 1» | «40 Reefer High», 1, «Shipper's own container: No» |
| Temperatura | −20, en la captura de la carga y en `log.txt` | −20 °C | −20 °C («Operando en») | −20, en el CONTROL de `log.txt` | −20, solo en `log.txt` | −20 ºC |
| Peso | 22 500, en la captura y en `log.txt` | 22 500 kgs | 22 500 KGM | 22 500, en la captura y en el CONTROL | 22 500, solo en `log.txt` | 22 500 kg |
| Commodity | La primera sugerencia de «SALMON» | El HS 030313 | La sugerencia del HS 030313 | «Frozen / Freeze Fish» y el HS, en el CONTROL | «SALMON» | «Salmon, frozen, fish» |
| Contrato | El de la celda | El de la celda | El de la celda | El de la celda | El de `config.json`, dentro del texto de la celda | El que pone el portal |
| Salida | 25-10, la directa de 4 | ETD 03-11 | Cut-off 27-10 | ETD 20-10, con transbordo, 33 días; CY Cutoff el domingo 18-10 a las 15:00 | ETD 28-10, la directa de 2; cut-off 24-10 | 18-10 a las 08:30 |

**MAERSK, además:**
- La fecha de retiro es el jueves 15-10, el primer día hábil después de hoy. El calendario traía 2 días habilitados, y
  la tarjeta quedó con esa fecha.
- La casilla de los términos quedó marcada, la única de la página.
- El Shipper quedó con AQUACHILE con el clic en el resultado.
- La fecha de zarpe se buscó «desde mañana»: sigue el freno del encargo 37.
- De las 3 tarjetas de la nave, 1 era copia de otra, y de las 2 que quedaron, 1 no traía «Book».

**Los ajustes reefer de MAERSK en la pantalla final:** «Container Type: Standard (40´)», «Temperature: -20 ºC», «GenSet
Export: No» y «GenSet Import: No».

### CMA-CGM: la nave sí, el viaje no

Corrí sin red el JavaScript del programa (`_JS_CMA_RUTAS`, de HEAD) sobre la lista de rutas que guardó antes de elegir
(`cma_f7_rutas.html`):

| Tarjeta | ¿Trae la nave de la fila? | ¿Su «Ref. de viaje» es el de la fila? | Cut-off |
|---|---|---|---|
| 1 | No | No | 20-10 |
| 2 | No | No | 20-10 |
| 3 | **Sí** (su «Buque principal») | No | 27-10 |
| 4 | Sí | No | 27-10 |

- El programa elige la 3.ª, la primera con la nave: es la que quedó elegida en la guarda.
- El viaje de la fila no está en ninguna tarjeta, ni en el HTML entero de la lista, y no hay enlace «Cargar … siguientes
  resultados».
- Los cuatro viajes de la lista tienen la misma forma que el de la fila y difieren de él en un solo carácter, el 5.º.
  Ese carácter crece con la fecha (el de las tarjetas del 20-10 es menor que el de las del 27-10), y el de la fila es
  menor que los dos. Lo más probable es que la fila pida una salida anterior que el portal ya no ofrece (inferido, no
  medido).
- **Es la misma fila del 02-10,** y ese día CMA eligió la ruta cuyo viaje es el de la fila (salía el 19-10).
- `reservar_cma` lee el viaje de la fila (`viaje_pedido`) y no lo usa en ninguna parte.

## Las revisiones del diff de los encargos 62 a 64 (`455c0fd..9402321`)

Las dos revisiones corrieron en paralelo, cada una en el clon `scratchpad\e65\clon` (HEAD `9402321`) con su temporal
dentro de la carpeta del encargo. Ninguna tocó el clon ni el repo vivo. La de código corrió 308 pruebas y 62 mutaciones
de los tres encargos (90 pares, todos muerden); la de seguridad, 166 pruebas y sus sondas. Ninguna corrió `test_web` ni
el censo, por los puertos.

| # | Hallazgo | Severidad | Qué hice |
|---|---|---|---|
| 1 | **El clic de `_mk_elegir_unica` iba al lugar de la opción, no a la opción** (las dos): `op.nth(i)` se vuelve a resolver al pulsar, y si el portal repinta la lista en ese instante, pulsaría otra, por ejemplo la del embarcador. La de código lo reprodujo con una página falsa; en `logs/` no se vio | Media (código), baja (seguridad) | **Arreglado.** Toma la opción (`element_handle`), comprueba que su texto sigue siendo el buscado y pulsa esa; si no puede tomarla, o ya dice otra cosa, NO ENVIADA sin pulsar nada |
| 2 | La de código sugiere, además, leer el campo después del clic y cortar si no muestra la opción | Media | **Residual:** qué muestra el campo después de elegir no está medido, y un corte por una lectura no medida podría dejar NO ENVIADA una reserva correcta |
| 3 | **«Las otras navieras no miran el contenedor» es falso para HYUNDAI** (código): `_hmm_llenar_detalles` lo lee para elegir REEFER o DRY. Con la consola, una columna de contenedor y la celda vacía, hasta el encargo 64 elegía DRY, y desde entonces REEFER, que es lo correcto (por el panel siempre fue REEFER) | Media | **Arreglado en la documentación:** `CLAUDE.md` y el docstring de `_otro_contenedor`. Sin prueba propia de HYUNDAI por la consola: residual |
| 4 | **Los dos lectores no tomaban la misma columna de contenedor** (las dos): con dos encabezados con «contenedor», la consola tomaba el último y el panel el primero; con «Tipo cont.», «Retiro contenedor» o «Depósito contenedor», la consola leía la columna y el panel no | Baja | **Arreglado.** La consola toma la columna con la regla del panel (`_campos_de_la_fila`, que ahora usa también `_mapear`) |
| 5 | **Un carácter de control en la celda** (un NUL, un ESC) llegaba al motivo, y openpyxl no lo escribe: la fila quedaba sin su resultado en la planilla descargada (seguridad, verificado) | Baja | **Arreglado** con el 6 |
| 6 | **Un carácter invisible** (un espacio de ancho cero, una marca de orden de bytes) hacía que el motivo dijera que la fila pedía «40 HC REEFER», el mismo que acepta; y **la marca del panel pintaba la celda entera**, sin el recorte a 40 del motivo (las dos) | Baja | **Arreglado.** Una sola fuente, `_contenedor_a_la_vista`, para el motivo y para la marca (`contenedor_a_la_vista` de `/api/filas`): hasta 40 caracteres, y cada carácter de control o invisible como «?». La regla de corte no cambia: esas filas siguen NO ENVIADA |
| 7 | La docstring de `_evidencia_antes_de_la_guarda` no nombraba `mk_f<fila>_contenedor` ni `mk_f<fila>_reefer` (código) | Baja | **Arreglado** |
| 8 | **El panel no valida `Host` ni `Origin`** (seguridad): una página de otro sitio abierta en el mismo navegador podría mandar un POST a `127.0.0.1` y armar una corrida, y en un panel de EMISIÓN, emitir con la planilla cargada. Es de antes de estos encargos | Media | **Residual, como propuesta:** está fuera del diff. Si el Chrome de este equipo ya frena esos pedidos (su protección de la red local, Local Network Access), no lo medí |

**Lo que las dos dieron por bien hecho:**
- el escape de la marca del panel;
- el candado intacto: `test_candado` no cambió, y ningún clic nuevo antes de la guarda;
- nada atrapa `ObjetivoNoEncontrado`;
- el orden en que se aparta la fila (sin nave, sin ruta, otro contenedor), el mismo en los tres lugares;
- la evidencia nueva no guarda credenciales;
- en los documentos nuevos no hay datos reales;
- en el diff no hay caracteres invisibles ni CR.

La de seguridad notó, además, que `_match_nav_key` mira «one» antes que «maersk», así que una celda «Maersk (phone)» se
repartiría a ONE. Es de antes y no lo toqué (residual).

## Lo decides tú

1. **El viaje de la fila en ONE, MSC, HYUNDAI y CMA-CGM.** Hoy solo MAERSK y COSCO cortan con NO ENVIADA si la fila
   trae un viaje que ninguna salida de la nave trae (tu decisión, `CICLO-cierre-de-frenos.md`). Las otras cuatro eligen
   por la nave, y CMA-CGM, la primera tarjeta con ella. Hoy CMA-CGM armó otro viaje. Las opciones:
   - que las cuatro corten como MAERSK y COSCO (lo que recomiendo: una reserva emitida no se deshace);
   - que solo CMA-CGM corte, porque es la única que hoy eligió otro;
   - dejarlas como están y corregir la fila de CMA-CGM en la planilla.
2. **La fila de CMA-CGM de la planilla de prueba** pide una salida que el portal ya no ofrece. Para la próxima prueba,
   conviene una fila con un viaje vigente.

## Residual

| Qué | Por qué no se hizo | Se reabre si |
|---|---|---|
| Que ONE, MSC, HYUNDAI y CMA-CGM corten si la fila trae un viaje que el portal no ofrece | Es una regla de negocio | Lo decides (arriba) |
| Que el panel valide `Host` y `Origin` (y un token por arranque) | Es de antes de estos encargos y está fuera del diff revisado | Lo encargas |
| Leer el campo del tipo de contenedor después del clic | Qué muestra el campo no está medido: el HTML guardado no trae lo escrito en un campo | Un HTML o una captura de «Booking Information» con el tipo ya elegido, leída |
| Una prueba de HYUNDAI por la consola con la celda de contenedor vacía | El lector ya tiene su prueba (`test_los_dos_lectores_dan_el_mismo_contenedor`); falta la de lo que hace HYUNDAI con eso | Lo encargas |
| «Cant. contenedores» cuenta como columna de contenedor para los dos lectores (la regla del panel, de antes) | Ninguna planilla del equipo la trae; el efecto es un corte de más, nunca una reserva equivocada | El equipo use esa columna |
| `_match_nav_key` reparte «Maersk (phone)» a ONE | De antes, fuera del diff | Una naviera se escriba así en la planilla |
| La fecha de zarpe de MAERSK, «desde mañana» | El freno del encargo 37: sin el portal no se sabe si acepta la de hoy | Lo pruebas en el portal |
| CMA-CGM y COSCO no llegan a EMITIDA | Falta medir su confirmación (`FORMA_BOOKING`) | Haya una confirmación real guardada |

## FRENA SI

El encargo no traía condiciones de freno. Lo único que pide una regla de negocio (que CMA-CGM, ONE, MSC y HYUNDAI
corten si la fila trae un viaje que el portal no ofrece) no lo construí: va en «Lo decides tú».

## Premisas que se cayeron

- **«El panel marcó todo OK»** no quiere decir que todo calce: el OK-EJEMPLO dice que la reserva llegó a la guarda, no
  que la pantalla final sea la de la fila. CMA-CGM llegó con otro viaje.
- **«Las otras navieras no miran el contenedor»** (`CLAUDE.md` e informes de los encargos 63 y 64) es falso para
  HYUNDAI: lo lee para elegir REEFER o DRY. Lo que es cierto es que no cortan por él.
- **«Los dos lectores dan el mismo contenedor»** (encargo 64) valía con una sola columna cuyo encabezado los dos
  reconocen. Con dos columnas, o con «Tipo cont.», leían otra. Desde este encargo, la misma.
- **«Si la lista traía una sola opción no está medido»** (encargos 62 y 63): ya está medido. Hoy, en el portal, cada
  lista traía una sola de la buscada.

## Defectos de instrumento que me encontré

- **El comparador leyó mal los ajustes reefer de MAERSK:** buscaba la etiqueta «Container Type» sin distinguir
  mayúsculas y encontraba antes «Container type», la del contenedor, así que decía que no calzaba. Ahora la busca desde
  «Reefer Settings», y calza.
- **El peso de HYUNDAI salía de la línea de COSCO:** las dos van en el mismo `log.txt`, y la expresión calzaba primero
  con el CONTROL de COSCO. Daban la misma cifra, pero la fuente era otra. Ahora busca «Gross Weight: … KGS», la de
  HYUNDAI.
- **El OCR a escala 2** no leía la temperatura de ONE ni el contenedor de COSCO; a escala 3, sí. El comparador abortaba
  por eso (su control), y no concluyó nada hasta leerlos.
- **Mi lector de las listas de MAERSK imprimió todas las `mc-option` de la página,** también las ya elegidas en otros
  campos, como el origen y el destino. Quedó solo en la salida del script, en la carpeta del encargo: este informe no
  las trae.
- **La máscara dejó pasar una palabra de la nave del transbordo de COSCO**, que no está en la planilla, en mi copia
  enmascarada de `log.txt`. Quedó solo en la carpeta del encargo.
- **Bash me juntó dos veces las barras invertidas** de un parche escrito en un heredoc. Los dos fallaron al compilarse,
  antes de escribir nada; los rehice con Write.
- **Mis parches frenaron dos veces por una línea de más de 120 caracteres,** antes de escribir; las partí.
- **Mi ensayo en seco del informe escribió el borrador en la raíz del repo, con el censo corriendo** (09:39): la marca
  `--seco` se perdía, porque el programa cargado con `soporte` deja `sys.argv` sin argumentos. Era un archivo mío, sin
  versionar; lo borré a los pocos minutos, antes de que el censo terminara, y su foto de los originales, que compara
  la raíz por nombre, lo dice (abajo). Ahora la marca se lee antes de cargar el programa.

## Verificación

**El censo del área** (`alcance_censo.py`, `lanzar_censo_e65.py`), corrido aparte y con el equipo despierto, de las
09:33 a las 11:15:
- **Qué entró:**
  - las mutaciones del encargo, las de los encargos 62, 63 y 64, y las 6 viejas re-ancladas;
  - las que caen a 15 líneas o menos de lo que cambió en `AQUASHIELD.py`;
  - las que nombran una prueba cuyo camino cambió: los dos lectores, la consola que reserva, las marcas y el reparto
    del panel, el reservador de MAERSK y sus listas, `test_candado`, la evidencia y la regla del contenedor.
- **585 mutaciones, 854 pares y 250 pruebas: muerden 853.** El que no mordía es mío:
  - `e65-clic-por-posicion` vuelve a pulsar por posición, y yo la había puesto también contra la prueba de la carrera.
  - Esa prueba no la puede ver: la comprobación del texto corta antes del clic.
  - Quité ese par. La misma mutación la tumban las otras dos pruebas que la nombran, las que eligen la opción.
- **Con ese par quitado, el censo de las 11 mutaciones del encargo** (`--filtro e65-`, de 11:16 a 11:23): 12 pares, y
  muerden todos.
- **En las dos corridas, el control pasa, y la foto de los 5.252 originales da 0 cambios.** El borrador que mi ensayo
  escribió en la raíz lo borré antes del final.
- **Sin suspensiones:** 0 eventos de Kernel-Power desde las 09:30. A las 07:54 y a las 08:04 el equipo sí se había
  suspendido.
- **El chequeo de las 2.262 mutaciones** (`mut_viejos.py`):
  - el texto viejo de cada una aparece una sola vez;
  - las nuevas y las re-ancladas compilan;
  - cada una de las 793 pruebas tiene al menos una mutación.

**La suite:** `tests/correr.py` (con `correr_sin_tope.py`), sobre el árbol que se commitea, con `CLAUDE.md` ya al día:
**793 pruebas, OK, en 1.779 s**, de las 11:23 a las 11:59 del 14-10, con 0 cambios en las 5.252 entradas fotografiadas
de los originales. Tardó 2,5 veces lo del encargo 64 (696 s), con otras cinco sesiones trabajando en el equipo y la CPU
al 59 %: con el plazo de siempre de `correr.py` (1.200 s), el corredor la habría cortado. Sin suspensiones: 0 eventos de
Kernel-Power desde las 09:30.

## Re-medir

Todo corre desde `scratchpad\e65`, en Git Bash, después de `source entorno_e65.sh`, que pone `TMPDIR`, `TEMP` y `TMP`
dentro de la carpeta. Ningún script imprime valores de la planilla ni de la cuenta: pasan por `mascara.py`, la del
encargo 49, con el programa de HEAD.

| Número | Script |
|---|---|
| Las carpetas de hoy | `python listar_hoy.py` |
| Cada `log.txt`, con la máscara | `python ver_log.py <AAAAmmdd_HHMMSS>` |
| Las filas de la planilla | `python filas_e65.py` |
| La fila de cada naviera, hoy y el 02-10 | `python filas_iguales.py` |
| Los campos de las seis pantallas finales | `python calce_e65.py` (se arma con `armar_calce.py` y `ajustar_calce.py`) |
| Las opciones de las dos listas de MAERSK | `python opciones_mk.py` |
| Las rutas de CMA-CGM y el viaje | `python rutas_cma.py`; frente al 02-10, `python cma_antes.py` |
| El OCR de una captura, enmascarado | `python ocr_buscar.py <AAAAmmdd_HHMMSS> <regex> <captura.png>[@escala]` |
| El alcance del censo | `python alcance_censo.py`; el chequeo de todas las mutaciones, `python mut_viejos.py` |

## NO retroceder

- **El clic de `_mk_elegir_unica` va a la opción que se leyó** (`element_handle` y su texto), no a `op.nth(i)`. Lo
  vigila `test_clics.TestContenedorMaersk.test_si_el_portal_repinta_antes_del_clic_no_pulsa_otra`.
- **El contenedor a la vista sale de una sola función** (`_contenedor_a_la_vista`), para el motivo y para la marca del
  panel. La página no recorta ni limpia por su cuenta.
- **Los dos lectores toman la columna del contenedor con la misma regla** (`_campos_de_la_fila`). Lo vigila
  `test_planilla.TestContenedorDeLaFila.test_los_dos_lectores_toman_la_misma_columna`.

## Reglas de método aplicadas

`metodo-ciclo` v24, y las reglas del módulo (`CLAUDE.md`). Sin choques entre ellas.

- **Control positivo que aborta:**
  - la máscara aborta si le queda un valor;
  - el comparador aborta si un campo no aparece en su fuente (abortó dos veces);
  - el lector de las listas de MAERSK y el de las rutas de CMA-CGM, con un HTML sintético;
  - el alcance del censo exige líneas cambiadas;
  - `mut_viejos.py`, con una mutación sintética.
- **Se mide sobre el camino real:** el JavaScript del programa (`_JS_CMA_RUTAS`) sobre el HTML guardado, y los lectores
  del programa sobre la planilla.
- **La unidad la fija el sujeto:** el veredicto es por reserva, y cada campo, por su fuente.
- **Fuente única:** `_contenedor_a_la_vista` y `_campos_de_la_fila`.
- **Cada reemplazo, una sola vez, y la escritura atómica:** todos los parches; dos frenaron antes de escribir.
- **El EOL:** 0 CR en los archivos tocados.
- **El cambio y su guardián juntos:** cada arreglo, con su prueba y su mutación.
- **El negativo muerde:** el censo.
- **Residual y premisas:** declarados arriba.
- **FRENAR en lo de negocio:** el viaje de CMA-CGM.
- **El alcance:** lo de fuera del diff se propone.
- **El cierre sin espera viva:** al final.
- **Del módulo:** ningún portal ni la emisión; `test_candado` sin cambios; las pruebas en `soporte`, nunca el 8765; el
  censo aparte, con el equipo despierto; la sonda de secretos antes de cada commit; el correo noreply.

## El repo

Dos commits en `main`, sin push (el push lo haces tú):

- `0e96b72` fix: lo que encontraron las revisiones (`AQUASHIELD.py`, y en `tests/`: `test_ayudantes.py`,
  `test_clics.py`, `test_envio.py`, `test_planilla.py`, `test_web.py` y `mutaciones.py`);
- el commit siguiente, docs: `CLAUDE.md` y este informe.

Los dos llevan de autor y de committer el correo noreply del repo, y la sonda de secretos dio 0 antes de cada uno.
En GitHub, `main` y `estable` están en `9402321` (medido con `ls-remote` al empezar): `estable` la avanzas tú,
después de subir `main`.
