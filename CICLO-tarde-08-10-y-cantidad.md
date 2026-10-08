# Encargo 59 · La tarde del 08-10: qué navieras están listas para emitir, y la cantidad de CMA-CGM como comprobación

**Base:** `C:\dev\Agendamiento Reservas` @ `ab847ce` · árbol limpio al empezar.

Medido con `metodo-ciclo` v16 sobre lo guardado en `logs/`, sin abrir ningún portal. El cambio del programa es uno solo:
la cantidad de CMA-CGM ya no se escribe, y si su campo no dice 1, la fila queda NO ENVIADA.

## En resumen

- **La tarde dejó cinco corridas, no dos.** Las cinco, sobre `ab847ce` y en modo prueba:

  | Corrida | Navieras | Desenlace |
  |---|---|---|
  | «Solo iniciar sesión», 16:29:41 | las seis | cinco OK; MSC, REVISAR (los dos intentos dieron 502) |
  | «Solo iniciar sesión», 16:34:14 | MSC | OK, a la primera |
  | «Solo iniciar sesión», 16:35:47 | MSC | OK, a la primera |
  | Las reservas, 16:36:34 | las seis | ONE, MSC, CMA-CGM, COSCO y HYUNDAI llegaron a la guarda; MAERSK, NO ENVIADA |
  | Las reservas, 16:50:32 | MAERSK | NO ENVIADA otra vez, en el mismo paso |

- **Las cinco pantallas finales calzan con su fila** en la nave, el viaje, los puertos, el contenedor, la temperatura,
  el peso y el commodity, como el 02-10 (encargo 49).
- **MAERSK no llegó a la guarda porque eligió otro contenedor.** En las 15 corridas anteriores de `logs/` eligió «40
  Reefer High»; hoy, «40 Reefer Standard Shipper own», el contenedor del embarcador. Con él, «Additional details» no
  trae el retiro del contenedor vacío, y el programa cortó al no encontrar «Choose another date». El corte es correcto,
  pero MAERSK **no está lista**: elige el tipo con la primera opción que trae «40» y «Reefer».
- **Actuaron por primera vez en el portal:** la pausa del deslizador de CMA-CGM que termina sola (encargos 56 y 57), la
  comprobación de la temperatura guardada (encargo 58) y, en MSC, la recarga tras el 502 del «Next», que esta vez trajo
  el campo de la clave.
- **La cantidad de CMA-CGM:** el programa ya no la escribe; lee el campo «Cantidad» y, si no dice 1, la fila queda NO
  ENVIADA con el motivo, la captura y el HTML. Las 10 reservas de CMA-CGM que llegaron a la guarda con su HTML dicen 1
  en todos sus pasos guardados: el FRENA SI no salta. Las 5 del 21-09 no tienen HTML y no se pueden medir.

## 1. Las corridas, naviera por naviera

### El inicio de sesión

Cuánto tardó, desde que abre el portal hasta la sesión iniciada (en «Solo iniciar sesión», el «tardó» de `log.txt`; en
las reservas, de «Login …» a «Sesión iniciada» o «Ya había una sesión activa»):

| Naviera | Solo login, 16:29 | Reservas, 16:36 | Reservas, 16:50 | Qué pasó |
|---|---:|---:|---:|---|
| ONE | 16,2 s | 4,5 s | — | En las reservas ya había sesión |
| MSC | 61,5 s, REVISAR | 22,1 s | — | Ver abajo; a las 16:34 y 16:35, solo MSC, 24,2 s y 22,3 s |
| CMA-CGM | 18,1 s | 438,1 s | — | En las reservas, el deslizador: 419 s de pausa; sin ella, 19 s |
| COSCO | 31,6 s | 27,3 s | — | El puzzle, resuelto solo al primer intento, las dos veces |
| HYUNDAI | 4,9 s | 4,3 s | — | |
| MAERSK | 8,2 s | 7,8 s | 2,8 s | Ya había sesión las tres veces |

«Solo iniciar sesión» de las seis tardó 152,7 s en total, 12,1 s de ellos en abrir Chrome. La corrida de las reservas,
813,9 s, y CMA-CGM se llevó 8 min 31 s de ellos.

**MSC en «Solo iniciar sesión» (16:29), paso a paso:**
1. El «Next» dio 502 (TriggerOidcLogin). El programa esperó 20 s y recargó una vez (encargo 47): **la recarga trajo el
   campo de la clave.** Es la primera vez que la recarga del encargo 47 actúa y sirve en el portal.
2. Escribió la clave; la vuelta a myMSC dio 502 (un POST a `/mymsc/`).
3. Hizo su único intento más, desde el principio (encargos 50 y 51). Al pulsar «Next», el portal no pidió la clave: la
   respuesta de error es otra vez el POST de la vuelta, con 502. O sea, b2clogin todavía tenía la sesión y devolvió al
   programa directo a myMSC, que volvió a fallar.
4. La recarga de ese error volvió a enviar ese POST y dio 500. Sin un tercer intento: REVISAR, que es lo que da el modo
   de solo login.

La clave se escribió una sola vez. En las tres veces siguientes (16:34, 16:35 y la de las reservas) MSC entró a la
primera, en unos 22 a 24 s. El 06-10 a las 09:54 el segundo intento ya había actuado, y también falló.

**CMA-CGM en las reservas:** al abrir el portal, DataDome mostró el deslizador (en «Solo iniciar sesión», 7 min antes,
no lo mostró). La pausa empezó a las 16:38:44 y **terminó sola a los 419 s**: «DataDome dejó pasar la página». Nadie
pulsó «Ya lo resolví». Qué se llevó esos 7 minutos no lo dice `log.txt`: el programa no ve cuándo se desliza la flecha;
solo mira la página cada 2 s y sigue con dos lecturas seguidas sin DataDome.

### Las reservas (16:36:34)

| Fila | Naviera | Estado | ¿Llegó a la guarda? |
|---:|---|---|---|
| 5 | ONE | OK-EJEMPLO, «armada hasta Review; SIN emitir» | Sí, 16:37:32 |
| 6 | MSC | OK-EJEMPLO, «armada hasta Summary» | Sí, 16:38:38 |
| 7 | CMA-CGM | OK-EJEMPLO, «armada hasta Envío de la reserva» | Sí, 16:47:10 |
| 8 | COSCO | OK-EJEMPLO, «armada hasta Booking Details» | Sí, 16:48:15 |
| 9 | HYUNDAI | OK-EJEMPLO, «armada hasta Review & Book» | Sí, 16:49:03 |
| 10 | MAERSK | NO ENVIADA: «no encontré un solo botón «Choose another date» a la vista…» | No; tampoco a las 16:50:32 |

### Las pantallas finales, contra su fila

Como en el encargo 49: el HTML de la guarda en un Chromium sin red y sin el JavaScript de la página, cada campo leído
por su etiqueta y comparado con la fila con las funciones del programa (`_trae_la_nave`, `_palabra_en`, `_norm_ctrl`).
Lo que la pantalla final no trae sale de una captura anterior (OCR, sin mirarla) o de `log.txt`. 0 campos sin
encontrar en su fuente. El informe no imprime naves, viajes, puertos ni contratos: dice si calzan.

| Campo | ONE | MSC | CMA-CGM | COSCO | HYUNDAI |
|---|---|---|---|---|---|
| Nave | Sí | Sí | Sí («Buque principal») | Sí (1.er tramo) | Sí («1st Vessel») |
| Viaje | Sí | Sí | Sí | Sí | Sí, pegado al código de servicio, como el 02-10 |
| Puerto de carga | Sí | Sí | Sí, en el campo y en el resumen | Sí (hoy el mapa no lo cambia) | Sí |
| Destino | Sí | Sí | Sí: descarga y rampa, los dos de la fila | Sí | Sí |
| Contenedor | 40' HC reefer x 1 | 40' HC reefer x 1 | 1 x 40' Reefer HC | 40RQ, 1 | RF/4H x 1 |
| Temperatura | −20 °C (captura y `log.txt`) | −20 °C | −20 °C («Operando en») | −20 (captura y CONTROL) | −20 C (`log.txt`) |
| Peso | 22 500 (captura y `log.txt`) | 22 500 | 22 500 | 22 500 | 22 500 (captura) |
| Commodity | Filete de salmónido (la regla) | HS 030313 | HS 030313 | HS 030313 (CONTROL) | SALMON |
| Contrato | El de la celda | El de la celda | El de la celda | El de la celda | El de `config.json`, dentro del texto de la celda |

- **ONE** eligió la directa entre 4 salidas de la nave del mismo día. Su evidencia del origen quedó con 4 de 5 HTML: un
  marco se cerró mientras se guardaba (no cambia nada).
- **MSC** eligió la nave y su contrato, con 28 itinerarios cargados.
- **CMA-CGM:** «Validar ruta» no respondió en 12 s y el programa siguió «sin darla por validada». Pasa en las 10
  corridas de CMA-CGM desde el 25-09. La temperatura quedó comprobada en la primera lectura (encargo 58), la mercancía
  elegida y los comentarios escritos.
- **COSCO:** de 2 itinerarios de la nave, el de menor tránsito (35 días frente a 47). El formulario vuelve a decir «Your
  current allocation needs further confirmation…»: la reserva quedaría sujeta a la confirmación del portal.
- **HYUNDAI:** el modal «Alternate Vessel Option» salió, y el programa marcó que no quiere otra nave; directa preferida.

### MAERSK: el contenedor del embarcador

- `_mk_contenedor` escribe «40 Reefer» en el tipo de contenedor y pulsa **la primera** opción a la vista que trae «40» y
  «Reefer». `log.txt` anota su texto cortado a 30 caracteres:
  - del 21-09 al 02-10, las 15 corridas con MAERSK: «40 Reefer High»;
  - el 08-10, las dos: «40 Reefer Standard Shipper own». Shipper's own container: el contenedor lo pone el embarcador.
- **El efecto, medido en el HTML del corte** (`mk_f10_sin_objetivo`, igual en las dos corridas): «Additional details» no
  trae el bloque «Container stuffing details» (depósito, fecha de retiro y referencia), que el 02-10 sí traía. Sin ese
  bloque no hay «Choose another date», y el programa cortó sin pulsar nada (encargo 37).
- Antes del corte todo calzó: el origen y el destino exactos, la nave con su viaje (`mk_f10_5_nave`, por OCR), la salida
  del 18-10.
- **Por qué el portal ofreció primero esa opción no está medido:** la lista de opciones no queda en ningún HTML ni
  captura. Confirmarlo exige el portal; no lo abrí.

## 2. Lo que actuó de los encargos 50 a 58

| Encargo | Pieza | ¿Actuó hoy? | Cómo le fue |
|---|---|---|---|
| 47 (de antes) | La recarga de MSC tras el 502 del «Next» | Sí, dos veces | La primera trajo el campo de la clave: **primera vez que sirve en el portal**. La segunda recargó la vuelta (un POST) y dio 500 |
| 50, 51 | El único intento más de MSC | Sí (también el 06-10) | Falló: el 502 llegó en la vuelta, también en el segundo intento |
| 50 | La evidencia del error de MSC | Sí | La respuesta y sus cabeceras en `log.txt`, las capturas, y el HTML solo donde no traía la cuenta |
| 51 | La línea del candado | Sí, en las cinco | «modo prueba» |
| 52 | El modo al armar | Sí, sin verse | Armó: el modo de la página era el del panel |
| 53 | Chrome con el sandbox, y no el respaldo | Sí | «navegador=chrome»; ninguna línea del respaldo |
| 53, 58 | El lanzador (cuatro puertos, y volver a probar el suyo) | No se sabe | El lanzador no escribe en `logs/`: no quedó rastro de cómo abrió el panel |
| 54 | El detector de DataDome de CMA-CGM | Sí | Vio el deslizador en las reservas; en el solo login, nada que detectar |
| 55 | La pausa en `log.txt` y las lecturas con plazo | Sí | La pausa, con su porqué y su final; ninguna lectura venció su plazo |
| 56, 57 | La pausa del deslizador que termina sola, con dos lecturas | **Sí, por primera vez** | Terminó a los 419 s sin «Ya lo resolví» |
| 56, 57 | Los cortes de CMA-CGM (comentarios, tamaño, peso, Reefer, «I Agree») | No hizo falta | Los cinco pasos terminaron |
| 58 | La temperatura comprobada | **Sí, por primera vez** | Dada por guardada en la primera lectura |
| 58 | El corte de la mercancía | No hizo falta | La eligió |
| 48 | El calendario de MAERSK | No se alcanzó | Sin retiro, no hubo calendario |

## 3. Veredicto por naviera

| Naviera | Veredicto | Por qué |
|---|---|---|
| ONE | **Lista** | Llegó a la guarda con todo calzado; tiene forma medida, así que con el candado abierto puede llegar a EMITIDA. Su commodity es otro que el de las demás, y lo diste por bueno (encargo 50) |
| HYUNDAI | **Lista** | Igual: todo calzado y forma medida. El contrato es el de `config.json`, que está dentro del texto de la celda |
| MSC | **Lista con reparos** | La reserva calza, pero el inicio de sesión sigue dando 502 a ratos (1 de 4 hoy, con los dos intentos). Si falla, la fila queda NO ENVIADA y no se envía nada a medias |
| CMA-CGM | **Lista con reparos** | Calza, y las comprobaciones nuevas actuaron. Pero: el deslizador lo pasa una persona; «Validar ruta» nunca responde; y sin forma medida (`FORMA_BOOKING`), lo mejor que puede dar es «ENVIADA – REVISAR EN PORTAL», nunca EMITIDA. Su primera emisión real nunca ocurrió |
| COSCO | **Lista con reparos** | Calza. Sin forma medida, como CMA-CGM. El portal avisa que la asignación necesita confirmación |
| MAERSK | **No lista** | Eligió el contenedor del embarcador y no llegó a la guarda. Mientras elija el tipo con la primera opción que trae «40» y «Reefer», puede armar otro contenedor |

«Lista» quiere decir que el programa armó la reserva correcta y se detuvo antes del botón final. Lo que pasa después del
botón final no se probó hoy en ninguna: el candado estaba cerrado.

## 4. La cantidad de CMA-CGM

Lo que decidiste: se quita el paso que intentaba escribirla, y el programa solo comprueba que el campo «Cantidad» dice
1; si dice otra cosa, NO ENVIADA con el motivo, la captura y el HTML.

**Lo medido antes de cambiar nada:**
- En los 67 HTML guardados de CMA-CGM que traen el campo, del 25-09 al 08-10, en cada paso guardado:
  - es un solo `.el-form-item` cuya etiqueta es «Cantidad»;
  - tiene un solo `input` (con `name`, `style` y `value`);
  - y dice 1.
- **Las 10 reservas que llegaron a la guarda con su HTML** (9 de antes y la de hoy) dicen 1 en todos sus pasos
  guardados. Antes del cambio, el JavaScript nuevo se corrió en un Chromium sin red sobre sus 65 HTML: los 65 dicen 1.
  Y la guarda de cada una con el valor cambiado a 2, sin el campo o con el campo repetido corta (control).
- **Las 5 reservas del 21-09 que llegaron a la guarda no tienen HTML.** El OCR de sus capturas encuentra la etiqueta
  «Cantidad» pero no lee su valor (el control con las capturas de hoy y del 02-10, que dicen 1 en el HTML, tampoco lo
  lee). Con ellas no se puede medir. Ninguna escribió la cantidad: el paso viejo nunca encontró el campo.

**FRENA SI:** no salta en lo que se puede medir: ninguna de las 10 habría quedado NO ENVIADA. Las 5 del 21-09 quedan sin
medir, como en el encargo 58.

**Lo que cambió** (`AQUASHIELD.py`):
- `_cma_completar_info_extra`: en el lugar del paso viejo (después del tamaño y tipo, antes del peso) llama a
  `_cma_cantidad_es_uno`, que no escribe nada. La cantidad de la fila (`cant`) ya no la usa CMA-CGM.
- `_JS_CMA_CANTIDAD` devuelve, de cada `.el-form-item` cuya etiqueta es «Cantidad», el valor de cada campo que trae.
  Solo lee lo que trae el HTML guardado: no mira si algo se ve.
- `_cma_lo_que_falta_de_la_cantidad` decide: un solo campo, una sola casilla, y que diga 1, sin los espacios de los
  bordes. Si no, dice qué faltó: ningún campo, varios, varias casillas, vacío, u otro valor.
- `_cma_cantidad_es_uno` lee hasta `CMA_LECTURAS_CANTIDAD` veces (6), cada 0,5 s (hipótesis: en lo medido ya decía 1
  antes de elegir el tamaño), y escribe en `log.txt` «cantidad: el campo «Cantidad» dice 1, un contenedor; no la escribo
  (lectura n)».
  - Si no dice 1: `ObjetivoNoEncontrado("Cantidad de CMA", …)` con `CMA_CANTIDAD` y lo que faltó. El motivo de la fila:
    «Cantidad de CMA: no encontré el campo «Cantidad» con 1 contenedor (cada fila de la planilla es una reserva de un
    contenedor): el campo «Cantidad» dice «2» (lo leí 6 veces, cada 0,5 s), así que no pulsé nada…».
  - Si la lectura falla o vence su plazo: `_cma_fallo`, como los otros pasos.
- Sin clics nuevos ni teclas; `test_candado` no cambió.

## 5. Pruebas, mutaciones, censo y suite

**Las pruebas nuevas (7)**, en `test_clics.TestCma`:

| Prueba | Qué vigila |
|---|---|
| `test_lo_que_falta_para_decir_un_contenedor` | La decisión: 1 y « 1 » pasan; 2, 01, 1,5, vacío, None, ninguno, dos campos, cero o dos casillas, no |
| `test_js_cantidad_por_lo_medido` | El JavaScript, en Node: solo la etiqueta «Cantidad» entera, con sus espacios juntados; todos los campos que la traen, y todas sus casillas |
| `test_cantidad_que_no_dice_uno_corta` | 6 lecturas cada 0,5 s y el corte con lo que faltó, sin escribirla ni seguir al peso |
| `test_cantidad_que_dice_uno_sigue` | Con 1 (en la lectura 1, 3 o 6) sigue al peso sin escribirla, también si la fila trae otra cantidad, y lo dice en `log.txt` |
| `test_la_lectura_de_la_cantidad_que_falla_corta` | La lectura que falla o no vuelve corta con `_cma_fallo` |
| `test_la_cantidad_deja_la_fila_no_enviada_con_su_evidencia` | Con los decoradores de `reservar_cma`: NO ENVIADA, el motivo literal, la captura y el HTML |
| `test_la_cantidad_va_tras_el_tamano_y_antes_del_peso_sin_escribirla` | El orden, y que no quede nada del paso viejo |

`test_lo_que_buscan` suma `CMA_CANTIDAD`. La página falsa de CMA (`PaginaCma`) responde que el campo dice 1, como lo
medido, salvo que la prueba diga otra cosa; nueva, `PaginaCmaConCantidad`, que cuenta las lecturas y las esperas.

**Las mutaciones:** 25 nuevas (`e59-*`): la comprobación quitada, antes del tamaño, después del peso, o con la cantidad
escrita como antes; la lectura que se traga su falla o la cuenta con otro texto; el corte que no corta; cada parte de la
decisión y del JavaScript mirada de otra forma; una lectura, cada 2 s, una espera de más, sin decirlo; y lo que busca
con otro texto. Ninguna vieja perdió su ancla: 2.126 mutaciones, 730 pruebas, 0 problemas (`mut_viejos.py`).

**El censo del área del cambio** (`alcance_censo.py`, `lanzar_censo_e59.py`), de las 17:46 a las 19:18: las 25 nuevas,
las que caen cerca de lo que cambió en `_cma_completar_info_extra`, y todas las que nombran una prueba de
`test_clics.TestCma` (su página falsa cambió), de la foto de los clics genéricos o de `TestSinClicACiegas`. En total,
207 mutaciones, 306 pares y 89 pruebas. El control pasa, y **305 de 306 pares muerden**, con 0 cambios en las 4.876
entradas fotografiadas de los originales.
- El que no, `e59-cantidad-otro-texto` contra `test_la_cantidad_deja_la_fila_no_enviada_con_su_evidencia`, era un par
  mal puesto: esa prueba arma el motivo esperado con la misma constante, así que cambiarle el texto no la puede tumbar
  (defecto 7). Lo vigila `test_lo_que_buscan`, que sí mordió. Quité el par; las anclas siguen en 0 problemas.

**La suite:**
`tests/correr.py` (con `correr_sin_tope.py`: el plazo de la corrida entera en 7.200 s), sobre el árbol que se
commitea, después de quitar el par: **730 pruebas, OK, en 536 s**, de las 19:19 a las 19:32, con 0 cambios en las
4.876 entradas fotografiadas de los originales.

## FRENA SI

- **La cantidad:** no salta. Las 10 reservas de CMA-CGM que llegaron a la guarda con su HTML dicen 1; las 5 del 21-09
  quedan sin medir (no tienen HTML, y el OCR no lee el valor).
- **Abrir un portal:** nada lo exigió. Lo que no se puede confirmar sin él queda dicho como no confirmado: por qué
  MAERSK ofreció primero el contenedor del embarcador, por qué MSC da el 502 y qué tardó 7 minutos en el deslizador.

## Lo decides tú

1. **Cómo elige MAERSK el tipo de contenedor.** Te propongo: la única opción cuyo texto entero es «40 Reefer High» (la
   de las 15 corridas anteriores), y si no hay una sola, NO ENVIADA sin pulsar nada, como los otros pasos. La otra
   lectura, quitar las que dicen «Shipper own», deja abierta cualquier opción nueva que el portal ponga primero.
2. **La primera emisión real de CMA-CGM y de COSCO** termina, como mucho, en «ENVIADA – REVISAR EN PORTAL»: sin su forma
   medida, el programa no reconoce su número. Si emites, revisa esas dos en el portal, y guarda la pantalla de la
   confirmación para medir su forma.

## Re-medir

Todo corre desde `scratchpad\e59`, en Git Bash, después de `source entorno_e59.sh` (`TMPDIR`, `TEMP` y `TMP` dentro de
la carpeta), con Python 3.13. Los scripts que leen `logs/` imprimen con la máscara del encargo 49 (`mascara.py`, con su
control `control_mascara.py`), con el programa de `ab847ce` (`srcHEAD`, de `sacar_head.py`).

| Número | Script |
|---|---|
| Las carpetas de la tarde | `python corridas.py 20261007` |
| Cada `log.txt`, enmascarado | `python ver_log.py <AAAAmmdd_HHMMSS> [desde] [hasta] [regex]` |
| Las pantallas finales contra su fila | `python armar_calce.py` y `python calce_e59.py` |
| Qué pantalla de MAERSK guardó cada HTML | `python mk_pantalla.py`; el cuerpo de «Additional details», `python mk_pantalla2.py` |
| Los avisos de cada guarda | `python avisos_guarda.py` |
| El campo «Cantidad» en los HTML de CMA | `python cantidad_html_e59.py` |
| La comprobación nueva sobre los HTML reales | `python calce_cantidad.py` |
| El OCR de la cantidad (su control falla) | `python ocr_cantidad.py <sello/captura.png>…`, `python ocr_cantidad2.py …` |
| Las anclas de las mutaciones | `python mut_viejos.py e59-` |
| El censo del área | `python alcance_censo.py`; `python lanzar_censo_e59.py` (aparte; escribe `censo_e59.txt`) |
| El tipo de contenedor de MAERSK en cada corrida | `grep "contenedor tipo:" logs/*/log.txt` (sin la carpeta en la salida) |

## NO retroceder

- **CMA-CGM no escribe la cantidad:** cada fila es una reserva de un contenedor. Si el campo no dice 1, la fila no se
  arma.
- **La comprobación solo lee lo que trae el HTML guardado** (el ítem, su etiqueta, su casilla y su valor): así se puede
  medir sobre lo guardado.
- **«40 Reefer» no identifica el contenedor en MAERSK:** el portal ofrece más de una opción con esas palabras, y la
  primera cambió.

## Defectos de instrumento que me cacé

1. **El OCR de la cantidad no pasó su control con capturas reales.** El control sintético pasa, pero en las capturas de
   hoy y del 02-10 (que en el HTML dicen 1) lee la etiqueta y no el valor. No usé sus números: las 5 del 21-09 quedan
   sin medir.
2. **Una salida de herramienta mostró el nombre de una carpeta de `logs/`,** que trae el nombre del operador (un `ls -d`
   para comprobar un sello). Quedó solo en la salida de esta sesión, no en un archivo ni en este informe. Después usé
   solo los sellos.
3. **La máscara dejó pasar, en salidas de herramienta, una dirección de un depósito de MAERSK y un código de vendedor
   de HYUNDAI.** Tampoco salieron de esta sesión.
4. **La herramienta Bash volvió a juntar los pares de barras invertidas** en un generador escrito por heredoc: falló su
   ancla antes de escribir nada. Lo rehice con Write.
5. **Un `cd` dentro de `logs/` movió la sesión dos veces,** y Git Bash no deja usar `sort` (bloqueado): reemplazado con
   Python, sin efecto en los números.
6. **Mi primera versión del comentario del paso nuevo nombraba los selectores viejos,** y la prueba que pide que no
   quede nada del paso viejo la cazó: el comentario los describe sin nombrarlos.
7. **Le asigné a una mutación una prueba que no la puede ver:** `e59-cantidad-otro-texto` cambia `CMA_CANTIDAD`, y la
   prueba de la fila arma su motivo esperado con esa misma constante. El censo lo cazó (el único par que no mordió);
   quité el par.
8. **El primer monitor del censo avisaba cada par que mordía** (mi filtro buscaba «MUERDE» al principio de la línea, y
   no calzaba): lo rehice para que avise solo lo que no muerde y el final.

## Premisas del encargo que se refutaron

- **«Son las dos corridas más recientes»:** son cinco. Después de «Solo iniciar sesión» de las seis hubo dos de solo
  MSC, y después de las reservas, una de solo MAERSK. Las cinco están arriba.

## Residual

| # | Lo que queda | Condición de reapertura |
|---|---|---|
| 1 | MAERSK elige el tipo de contenedor con la primera opción que trae «40» y «Reefer» | Tu decisión («Lo decides tú», 1) |
| 2 | MSC: el 502 sigue a ratos; en el segundo intento, b2clogin no pide la clave y la vuelta vuelve a fallar; la recarga de esa vuelta reenvía un POST y da 500 | Si quieres que el segundo intento o la recarga cambien |
| 3 | CMA-CGM: «Validar ruta» no responde en 12 s en las 10 corridas desde el 25-09; el programa sigue sin darla por validada | Si un HTML de esa pantalla muestra qué espera el portal |
| 4 | CMA-CGM y COSCO no tienen forma medida: sin ella, nunca EMITIDA | La primera confirmación real guardada |
| 5 | COSCO: «Your current allocation needs further confirmation» | Si hay que tratarlo antes de emitir |
| 6 | Las 5 reservas de CMA-CGM del 21-09, sin medir para la cantidad (y para la temperatura, encargo 58) | Ninguna: no hay más qué medir en ellas |
| 7 | El lanzador no deja rastro en `logs/`: si volvió a probar el puerto no se sabe | Si el lanzador escribe su arranque en un archivo |
| 8 | Los 419 s del deslizador: qué los tomó no se ve | Ninguna sin el portal |
| 9 | La cantidad de la fila: CMA-CGM ya no la usa; MAERSK la escribe si no es 1; la planilla no trae esa columna | Si la planilla trae una cantidad |
| 10 | Las revisiones que pide ECC (de código y de seguridad) no se lanzaron | Si las pides |

## Reglas de método (v16)

- **Aplicadas:** las 20 universales. En especial:
  - el contador al lado de cada cero: 5 corridas leídas de 5; 0 campos sin encontrar en su fuente; 67 HTML con el campo,
    0 sin él entre los de las reservas que llegaron a la guarda; 0 problemas de anclas en 2.126 mutaciones;
  - el control positivo que aborta: la máscara, el calce (cada campo en su fuente), `calce_cantidad.py` en las dos
    direcciones (lo guardado no corta; el valor 2, sin el campo y repetido sí), `mut_viejos.py`; el del OCR no pasó y
    no usé sus números (defecto 1);
  - la unidad la fija el sujeto: la comprobación decide por reserva, y se midió por reserva (cada HTML de sus pasos);
  - el negativo que muerde: cada prueba nueva con su mutación y el censo del área; el par que no mordió, leído (no era
    una prueba inútil: el par estaba mal puesto);
  - re-medir contra HEAD: la máscara y el calce con el programa de `ab847ce`;
  - un gate en cero prueba contención: además de la suite, la comprobación corrida sobre los HTML reales;
  - fuente única: `_cma_fallo` para la lectura que falla, y `CMA_CANTIDAD` en los dos cortes;
  - el cambio y su guardián en la misma operación; cada reemplazo, una sola vez; LF (0 CR);
  - frenar en lo que es tuyo: el tipo de contenedor de MAERSK.
- **Las del módulo** (`CLAUDE.md`): `test_candado` no cambia; ningún clic nuevo; nada se traga el corte; casos
  sintéticos; nunca el puerto 8765 en una prueba; la sonda de secretos antes de cada commit; el correo noreply de autor
  y de committer; las capturas reales no se miran (el OCR imprime solo lo que la regla deja).
- **Choques:** ECC pide lanzar revisores solos; las reglas permanentes dicen que se proponen: no lancé ninguno (residual
  10).
- **Pieza 8 (el entregable renderizado y mirado):** opcional; este informe es Markdown y no lo rendericé.

## Lo que dio en el repo

Dos commits en `main`, sin push (el push lo haces tú):

- `58f3153` fix: el programa y las pruebas (`AQUASHIELD.py` y, en `tests/`, `mutaciones.py` y `test_clics.py`);
- el commit siguiente, docs: `CLAUDE.md`, `LEEME.md` y este informe.

Los dos llevan de autor y de committer el correo noreply del repo, y la sonda de secretos dio 0 antes de cada uno.
`CLAUDE.md` suma la cantidad de CMA-CGM (que ya no se escribe), el estado nuevo de NO ENVIADA, las 730 pruebas y el
tipo de contenedor de MAERSK del 08-10. Nada fuera de la carpeta del encargo: esta vez no medí nada del entorno de la
máquina que no estuviera ya registrado.
