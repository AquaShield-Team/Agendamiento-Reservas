# CICLO · El estado de cada reserva después del envío

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-23 y 24 · **Método:** skill `metodo-ciclo` v12 ·
**Base:** `f03bb75` · **Commits** (locales, sin push):
- `66859dd`: el cambio transversal.
- `af59551` ONE, `872ddbd` MSC, `023554b` HYUNDAI, `4362fcb` MAERSK, `7d769bc` CMA y `2c2ed4f` COSCO.
- El de este informe con `CLAUDE.md`.

> Sin datos reales. Las capturas y los logs de `logs/` se miraron en su lugar y en solo lectura. Este
> informe describe **la forma** de los números y de los mensajes, nunca un número, una ruta ni una nave.
> Los casos de prueba son sintéticos.

## Veredicto

- **El estado ya dice lo que pasó, en las seis navieras.** Después de la guarda del candado, cada
  reservador pulsa el mismo botón de antes, anota si lo pulsó y decide con lo que vio:

| Estado | Cuándo | Qué dice el detalle (pantalla, `log.txt` y planilla) |
|---|---|---|
| `EMITIDA` | Se vio la confirmación con un número que calza con la forma medida de la naviera | «<naviera> emitida con éxito (Booking: <número>)» |
| `ENVIADA – REVISAR EN PORTAL` | Se pulsó y no hubo confirmación reconocible; el portal mostró un error; o el programa falló al pulsar o después | Qué se vio y «Revisa en el portal si la reserva quedó creada y, si está, anota su número en la planilla.» |
| `NO ENVIADA` | El botón no estaba en la pantalla, o el portal marcó errores de validación | «no se pulsó «<botón>» porque no estaba en la pantalla» o «el portal no aceptó el envío y marcó: «<campo>»; …», y «La reserva no se envió» |

- **Cada envío deja evidencia**, en las seis navieras: la captura de la ventana y el HTML completo de la
  página y de cada marco, con sus raíces shadow, en la carpeta de la corrida (`logs/`, fuera del repo). Se
  guarda **después** de leer el número, así muestra la pantalla sobre la que se decidió. Solo lee.
- **HYUNDAI y MAERSK tienen forma medida** (5 de 5 capturas cada una). **CMA y COSCO no**: nunca llegan a
  EMITIDA hasta que se mida su confirmación. Desde ahora, la evidencia que dejan permite medirla.
- **El N° de reserva va solo con EMITIDA**, en el panel y en la planilla.
- **«SIN EMITIR» de OK-EJEMPLO y el candado no cambiaron.** Lo de antes de la guarda tampoco: `test_candado`
  lo fotografía y sigue igual.
- **Los tres FRENA SI no se cumplieron** (abajo, cada uno con lo medido).
- **PASO 0: CICLO.**

## Los FRENA SI, medidos

**1. Distinguir los tres casos no exige ningún clic ni navegación nueva.**
- **«No pulsado» y «pulsado»** los sabe el propio programa: el clic de Playwright termina o no, y el
  JavaScript que busca el botón por su texto ahora devuelve si lo pulsó (`_pulsar_boton`).
- **«Pulsado sin confirmación»** es no ver la forma medida en la pantalla que ya está abierta.
- **«Rechazado por validación»** se lee en esa misma pantalla.

**Límite:** la validación solo está medida en COSCO. En las otras cinco, unos errores de validación
después de pulsar se verían como ENVIADA – REVISAR EN PORTAL, el lado seguro. Va al residual.

**2. Guardar la evidencia no cambia nada antes de la guarda.**
- `_guardar_evidencia` solo se llama desde `_resultado_envio`, y `_resultado_envio`, `_pulsar_boton` y
  `_cosco_esperar_resultado` solo después de la guarda de cada reservador. Lo fija
  `test_envio.TestReservadores.test_la_evidencia_y_el_estado_solo_despues_de_la_guarda`, con su defecto
  inyectado: una evidencia antes de la guarda de MSC.
- `test_candado` (lo que se pulsa antes de la guarda) no cambió en ningún commit.

**3. Ningún estado nuevo rompe la lectura de la columna de estado.**
- **Los lectores de la planilla:** `leer_filas` (panel) y `leer_reservas` (consola) ubican la columna, pero
  **no leen su valor**. Lo comprobé escribiendo los tres estados en todas las filas de las siete hojas,
  como los escriben la consola y la descarga: los dos lectores leen exactamente lo mismo
  (`test_planilla.TestEstadosNuevos`, con un defecto inyectado por lector: saltarse las filas «ENVIADA»).
- **El panel sí lee el estado de cada resultado** para pintar la fila. Medí que «NO ENVIADA» caía en la
  rama genérica y dejaba la fila marcada «en curso», con «procesando…» en la columna del número. No es la
  columna de la planilla, así que no lo tomé como freno: lo arreglé en el mismo commit con `lecturaEstado`
  y dos ramas nuevas, y la lectura se prueba corriéndola en Node.

## Lo medido

**Fuentes, en solo lectura:**
- Las 6 corridas de `logs/`.
- Las capturas posteriores al envío: 39 (5 de ONE, 5 de MSC, 5 de CMA, 14 de COSCO, 5 de HYUNDAI y 5 de
  MAERSK).
- Las líneas del log desde el clic de envío hasta el resultado.
- **HTML guardado: 0.** Por eso la evidencia es nueva.

**La confirmación de HYUNDAI y MAERSK.** Agrupé sus 10 capturas por huella (10 distintas) y miré las 10.

| Naviera | Qué muestra la pantalla | Forma medida |
|---|---|---|
| HYUNDAI | Una ventana sobre la página de revisión: «A Tentative Booking has been created.», «- Created tentative booking number:» y el número; aclara que el personal de HMM la revisa antes de aprobarla. En la página hay otros códigos (contrato, nave y viaje, indicativo) y ninguno tiene esa forma | «Created tentative booking number:» + `SCLA` + 8 dígitos (5 de 5) |
| MAERSK | La página «Booking confirmed», con «Booking number:» y el número; más abajo, fechas, viaje y tiempos, ninguno de 9 dígitos | «Booking number:» + 9 dígitos (5 de 5). Los 5 empiezan igual, pero ese prefijo es un rango de numeración y no se exige: la etiqueta ya separa el número |

**El ERROR de COSCO después de Submit.** El único medido (c3, 1 reserva) no lo mostró el portal. Fue una
**excepción del propio programa** (`NameError`, de una versión anterior del código) lanzada después de
pulsar Submit, y la ventana «Reminder» seguía abierta.
- **Ahora, cualquier falla del programa después de pulsar da ENVIADA – REVISAR EN PORTAL**, en las seis
  navieras.
- **Los dos ERROR que COSCO devolvía tras Submit se reparten así:**
  - «COSCO rechazó el envío» se separa en dos. Los errores bajo los campos pasan a NO ENVIADA, con los
    campos. El aviso de error del portal pasa a ENVIADA – REVISAR EN PORTAL.
  - «Tiempo de espera agotado» pasa a ENVIADA – REVISAR EN PORTAL.
- **Si la ventana Reminder llegó a verse,** los errores de campo no bastan para NO ENVIADA: no está medido
  si frenaron el envío, así que van como aviso del portal.

## Los cambios

| Commit | Qué cambia |
|---|---|
| `66859dd` transversal | `_resultado_envio`, `_guardar_evidencia`, `_pulsar_boton`; el N° de reserva solo con EMITIDA; `lecturaEstado` y las dos ramas nuevas del panel |
| ONE | Tras la guarda, `_pulsar_boton` (mismo selector y mismo JavaScript de respaldo) y `_resultado_envio` |
| MSC | Lo mismo; sale `_emitida`, que ya no tenía quién la llamara |
| HYUNDAI | Su forma medida; sale su rama del extractor viejo (una «scla» en el texto metía a otra naviera en ella); la ventana de confirmación de HMM se acepta igual que antes y **solo si se pulsó** «Create NOW» |
| MAERSK | Su forma medida; sale su rama del extractor viejo, a la que entraba cualquier naviera con un «27» en el texto |
| CMA | `_pulsar_boton` y `_resultado_envio`; sin forma medida: nunca EMITIDA |
| COSCO | El Submit por texto dice si pulsó (`_JS_COSCO_SUBMIT`). La espera pasa a `_cosco_esperar_resultado` con los mismos clics (la ventana Reminder incluida) y **solo si se pulsó**. Los errores de validación se separan del aviso del portal (`_JS_COSCO_ERRORES`), y el posible número ya no se toma: solo sirve para dejar de esperar |

**En el detalle de EMITIDA ya no van** los datos de la ruta que agregaban HYUNDAI y MAERSK, ni la nave que
agregaba CMA: siguen en el log de la corrida.

## Pruebas que cambiaron su expectativa

| Prueba | Antes | Después |
|---|---|---|
| `test_booking.TestNumeroLimpio` (4 pruebas, transversal) | Entradas sin estado | Las mismas entradas con estado EMITIDA; mismas expectativas. La nueva `test_solo_una_emitida_tiene_numero` fija que cualquier otro estado da vacío |
| `test_booking.TestNumeroTrasEnvio.test_reservadores_usan_la_forma_medida` | ONE y MSC devolvían `_emitida` | ONE: solo MSC (ONE pasa a `test_envio.TestReservadores`). MSC: se retira con `_emitida` |
| `test_emitida_con_numero` y `test_emitida_sin_numero_avisa_sin_relleno` (MSC) | Sin número: `EMITIDA` y «se pulsó el envío, pero la pantalla de confirmación no mostró el número. Búscalo en el portal…» | Se retiran con `_emitida`. Sin número ahora es `ENVIADA – REVISAR EN PORTAL`, en `test_envio.TestResultadoEnvio.test_pulsado_sin_confirmacion_es_enviada`; con número, igual que antes |
| `test_booking.TestExtraerNumero.test_hyundai` | «Booking No: SCLA…» y «Bkg No …» daban el código | Las dos dan vacío; se suma la forma medida, que da el número |
| `test_booking.TestExtraerNumero.test_una_sclg_ya_no_mete_a_otra_naviera_en_one` | Entrada «hyundai» | Entrada «cma»: «hyundai» ya va por su forma medida y la prueba no habría pasado por la cadena que su defecto toca. Misma intención |
| `test_booking.TestExtraerNumero.test_maersk` | «Your booking …» y un «27…» suelto daban el número | Los dos dan vacío; se suman la forma medida y un código con letras tras la etiqueta, que también da vacío |
| `test_un_27_mete_a_cualquiera_en_la_rama_maersk` (MAERSK) | CMA con «27 contenedores» devolvía un número ajeno | Renombrada `test_un_27_ya_no_mete_a_otra_naviera_en_maersk`: devuelve la referencia de CMA |

**Una prueba cambió solo su comentario:** `test_consola…test_sin_emitir_solo_si_volvio_sin_emitir`.

**Pruebas: 43 nuevas, 1 renombrada y 3 retiradas** (las de `_emitida`), de 145 a 185.
- `test_envio.py`, archivo nuevo, 35:
  - `TestResultadoEnvio` (10), con cada rama del estado;
  - `TestEvidencia` (5);
  - `TestPulsarBoton` (3);
  - `TestReservadores` (7): la forma después de la guarda en cada uno de los seis reservadores, y el
    FRENA de la evidencia;
  - `TestCosco` (8);
  - `TestLecturaDelPanel` (2).
  - Parte de `TestCosco` y las dos de `TestLecturaDelPanel` corren en Node.
- `TestNumeroLimpio` (1).
- `TestEstadosNuevos` (2).
- La corrida del panel (1) y la de la consola (1) con los estados nuevos.
- Las formas medidas de HYUNDAI (1) y de MAERSK (1).
- La «scla» que ya no mete a otra naviera en HYUNDAI (1). La del «27» es la renombrada.

**Mutaciones: 119 nuevas y 8 retiradas**, de 234 a 345.
- **Nuevas, una por rasgo de cada cambio:**
  - Cada rama del estado y el texto de cada mensaje.
  - La evidencia: la captura, los marcos, el respaldo sin JavaScript, el aviso de la falla y el contador.
  - El botón, que dice si pulsó.
  - Las dos ramas nuevas del panel.
  - Cada rasgo de las formas de HYUNDAI y MAERSK.
  - En cada reservador: el mismo botón, el error guardado y la decisión.
  - Los JavaScript y la espera de COSCO.
  - Un defecto por lector.
  - La evidencia antes de la guarda.
- **Retiradas: 8,** porque su texto ya no existe:
  - `reservar-one-vuelve-al-extractor-viejo`;
  - `emitida-con-relleno`, `emitida-sin-aviso-en-log` y `emitida-numero-sin-log`;
  - `reservar-msc-vuelve-al-extractor-viejo`;
  - `booking-hyundai-sin-bkg`;
  - `booking-maersk-sin-27` y `booking-27-ya-no-activa-maersk`.
- **Ajustadas: 2:** `lectura-sin-shadow` y `emitida-numero-sin-log`, porque su texto viejo pasó a
  aparecer dos veces.

## Universo y cobertura (pieza 3)

**Lo medido:**
- **Corridas:** 6 de 6. **Capturas tras el envío:** 39, y las 10 de HYUNDAI y MAERSK, miradas enteras.
- **Reservas EMITIDA en los logs:** 38. De ellas, 10 son de HYUNDAI y MAERSK, y traen número.

**La red, por commit** (cada commit pasó la suite completa, el censo completo y la sonda de secretos en 0
sobre el staging; los originales no cambiaron en ninguna corrida):

| Commit | Pruebas | Mutaciones | Pares mutación-prueba | Sin mutación | Motivos vacíos | Pares que no muerden |
|---|---|---|---|---|---|---|
| base `f03bb75` | 145 | 234 | 273 | 0 | 0 | 0 |
| `66859dd` transversal | 170 | 282 | 330 | 0 | 0 | 0 |
| `af59551` ONE | 171 | 288 | 336 | 0 | 0 | 0 |
| `872ddbd` MSC | 169 | 290 | 338 | 0 | 0 | 0 |
| `023554b` HYUNDAI | 172 | 304 | 353 | 0 | 0 | 0 |
| `4362fcb` MAERSK | 174 | 316 | 367 | 0 | 0 | 0 |
| `7d769bc` CMA | 175 | 323 | 374 | 0 | 0 | 0 |
| `2c2ed4f` COSCO | 185 | 345 | 397 | 0 | 0 | 0 |

Cada fila sale del censo corrido sobre la copia fija de ese commit, leído entero:
- **Cada par impreso**, con su motivo.
- **Las cuentas del corredor:** pruebas, mutaciones y pares.
- **La foto de los originales:** 0 cambios en todos.

## Re-medir (pieza 1)

```powershell
python tests\correr.py --todo
python tests\sonda_secretos.py --dry-run
cd tests; python -m unittest test_envio
```

- **Las formas:** agrupar por huella SHA-256 las `hmm_f*_6_confirmado.png` y `mk_f*_7_confirmado.png` de
  `logs/` y mirar cada una.
- **El ERROR de COSCO:** en el log de la corrida c3, las líneas desde «MODO EMISIÓN REAL» hasta
  «Reserva 1:».
- **Los censos de cada commit se corrieron sobre una copia fija de su estado**, mientras el árbol seguía
  con el commit siguiente. Cada commit se armó desde esa copia con `git hash-object` y una sola llamada a
  `git update-index --index-info`. Se verificó byte a byte contra `git show :<ruta>` antes de la sonda, y
  contra `git show HEAD:<ruta>` después del commit.

## NO retroceder (pieza 2)

- **No devuelvas EMITIDA sin la forma medida en pantalla**, ni pongas en `FORMA_BOOKING` una forma que no
  salga de capturas o HTML de una confirmación real.
- **No vuelvas a devolver un estado a mano después de la guarda:** todo pasa por `_resultado_envio`.
- **No llames a `_guardar_evidencia` antes de la guarda ni le agregues clics:** es solo lectura.
- **No saques número de un estado que no sea EMITIDA** (`_extraer_bkg_limpio`).
- **No devuelvas las ramas «scla» y «27» al extractor:** metían a una naviera en la rama de otra.
- **No dejes un estado nuevo sin su rama en `lecturaEstado`:** la fila quedaría «en curso».

## Defectos de instrumento cazados (pieza 4)

1. **Dos negativos vacíos por un caso incompleto (lectura b).** «Leer el número aunque no se haya pulsado»
   no mordía las pruebas de validación y de aviso del portal: las dos usaban COSCO, que no tiene forma
   medida y nunca lee. Les agregué el caso con una naviera medida y un número en pantalla.
2. **Otro negativo que habría quedado vacío, cazado antes del censo.** Sin la forma de MAERSK, la cadena
   genérica también acepta «Booking number» y 9 dígitos. Agregué a `test_maersk` un código con letras, que
   la forma medida rechaza y la cadena acepta.
3. **Un negativo que se habría vuelto vacío por el cambio.** `test_una_sclg…` usaba «hyundai», que ya no
   pasa por la cadena que su defecto toca. Lo cambié a «cma».
4. **Creí muerto un censo que seguía vivo.** Busqué el proceso como `python.exe`, pero el Python de esta
   máquina corre como `python3.13.exe`. Relancé el censo del commit transversal y los dos escribieron en el
   mismo archivo:
   - El primero terminó en `RESULTADO: OK`, que el corredor calcula él mismo.
   - Como registro guardé el segundo, completo: 330 pares, 0 motivos vacíos.
   - Desde ahí lanzo los censos desacoplados, cada uno con su archivo y sin búfer.
5. **Textos viejos repetidos o incompletos**, cazados por un prechequeo que armé para no gastar un censo
   entero:
   - Tres mutaciones cuyo texto viejo aparecía dos veces: `lectura-sin-shadow` y dos de COSCO.
   - Una a la que le faltaba el comentario de su línea.
6. **Dos fallas de mi propia prueba de estructura, no del programa.** Comparaba texto con otra indentación,
   y los ids de nodos de dos árboles distintos.
7. **Dos ediciones por script frenadas por sus aserciones, sin escribir nada:**
   - Una por la conversión de `\\` en `\` de la herramienta Bash.
   - Otra porque mi comprobación de que ya no quedaba la variable «bkg» también encontraba el selector
     `.bkg-loading`.
8. **El índice armado desde la copia, dos veces mal.** Las dos veces lo cazó la verificación byte a byte
   del índice contra la copia, antes de la sonda y del commit:
   - Primero, 19 llamadas a `update-index`, una por archivo, chocaron con el candado del índice, que otro
     proceso tomaba a ratos. El índice quedó a medias.
   - Después, una sola llamada con `--index-info` no actualizó nada: en Windows, el texto que le pasé
     llevaba `\r\n` en vez de `\n`. Un archivo seguía distinto.
   - Ahora va una sola llamada en bytes, que reintenta si el candado está tomado y nunca lo borra. Cada
     commit se verifica también después, contra `HEAD`.
9. **Una línea real en mi sesión.** Al medir los logs de HYUNDAI y MAERSK imprimí, con los dígitos
   ocultos, una línea que traía una ruta y una nave reales. No quedó en ningún archivo.

## Premisas del encargo contrastadas (pieza 5)

- **«HYUNDAI y MAERSK traen número válido»:** confirmada, en 5 de 5 capturas cada una. Matiz: el de HYUNDAI
  es una reserva **tentativa**, que el personal de HMM revisa antes de aprobarla.
- **«En CMA el programa devuelve EMITIDA aunque el botón no se haya pulsado»:** confirmada en el código.
  En las 5 reservas reales no se puede saber si el botón estaba visible: el log escribe «Pulsando…» antes
  de mirarlo. Ahora queda escrito.
- **«En COSCO, 8 de 14 con errores de validación visibles»:** sigue siendo lo que muestran las capturas.
  Sin HTML no se puede saber si esos mensajes son del campo (`.el-form-item__error`, NO ENVIADA) o un
  aviso del portal (ENVIADA – REVISAR). El código los separa, y la evidencia nueva lo va a mostrar.
- **«El ERROR de COSCO después de Submit»:** el medido fue una falla del programa, no un mensaje del
  portal (arriba). La decisión se aplicó a los dos casos.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| CMA y COSCO nunca llegan a EMITIDA | Sin forma medida: ninguna captura muestra su confirmación | …una corrida real deja HTML con su confirmación: se mide y entra en `FORMA_BOOKING` |
| «Rechazado por validación» solo se reconoce en COSCO | Es la única con errores de validación medidos | …la evidencia muestra una pantalla de validación en otra naviera |
| Qué mensajes de COSCO son de campo y cuáles avisos | Sin HTML no se ve la clase | …se lee el HTML guardado de una corrida de COSCO |
| EMITIDA en HYUNDAI y MSC es «creada y pendiente de revisión de la línea» | Es lo que confirma el portal | …decides si esas dos necesitan otro estado |
| `extraer_numero_booking` ya no tiene llamadores en el programa | Conserva el camino viejo de CMA, COSCO y los patrones genéricos, con sus pruebas | …CMA o COSCO tienen forma medida, o decides borrarlo |
| `_extraer_bkg_limpio` sigue aceptando «Templates» con EMITIDA | Ya no llega: el detalle de EMITIDA lo escribe `_resultado_envio` con el número medido | …otro camino vuelve a escribir EMITIDA |
| El JavaScript de la evidencia y los de COSCO no corren en un navegador en la red | Se prueban en Node con un `document` falso o por su forma | …se prueba contra un navegador |
| La evidencia no se poda | Un HTML por envío y marco en `logs/` | …`logs/` crece de más |
| Las filas marcadas EMITIDA por corridas anteriores | Este ciclo no revisa el pasado | …se decide revisarlas en el portal (`CICLO-numero-booking.md`) |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v12**:
- **PASO 0 y re-medir** contra `f03bb75`; cada captura distinta, por huella.
- **Todo registro es una hipótesis:**
  - El ERROR de COSCO tras Submit era una falla del programa.
  - La clase de los mensajes de COSCO no está verificada.
- **La unidad la fija el sujeto:** la pantalla tras el envío.
- **Control positivo:** cada prueba de los lectores verifica que el estado quedó escrito antes de comparar
  la lectura.
- **El negativo tiene que morder, de a uno por llamada; un negativo vacío delata un caso incompleto:**
  defectos 1 a 3.
- **Lo inocuo y lo peligroso conviven:** un NO ENVIADA falso llevaría a emitir dos veces; ante la duda, el
  estado es ENVIADA – REVISAR EN PORTAL.
- **El cambio y su guardián, en el mismo commit.**
- **Cada reemplazo afirma su viejo una vez y la escritura es atómica:** el script de COSCO.
- **Se declaran el residual y las premisas.**
- **El push se entrega, no se hace:** no hay remoto.

Reglas propias del módulo (`CLAUDE.md`): sandbox, las fotos se actualizan en el mismo cambio, casos
sintéticos y la sonda antes de cada commit.

**Choque:** «un commit por naviera», con la red y el censo completos antes de cada uno, contra el tiempo
del censo, que son varios minutos por commit. Lo resolví con censos sobre copias fijas, varios a la vez, y
cada commit armado desde su copia verificada.

## Entregable (pieza 8)

Este `.md`, sin renderizar, y `CLAUDE.md` al día. Pasan la sonda de staging antes de su commit.
