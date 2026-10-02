# CICLO · CMA: la sección Reefer y el botón «Enviar el booking»

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-24 · **Método:** skill `metodo-ciclo` v12 ·
**Base:** `f2a3dda` · **Commits:** solo el de este informe (local, sin push). **No se tocó el código.**

> Sin datos reales. El log y las capturas se leyeron en su lugar y en solo lectura. Este informe describe la
> página del portal y el código, nunca una reserva (con dos excepciones en mi sesión, en los defectos de
> instrumento; ninguna llegó a un archivo).

## Veredicto: FRENO

Se cumplen **dos** de los tres FRENA SI, y el tercero no se puede medir. Paré sin cambiar nada.

1. **Completar la sección Reefer exige clics antes de la guarda.** En la página, la sección no tiene campos
   propios. Solo tiene un botón con un lápiz, que abre un panel. Para completarla hay que pulsar ese lápiz y,
   después, el botón que guarda el panel. **Los dos clics ya están en el código**, antes de la guarda, desde el
   primer commit. Corrieron en las 5 reservas medidas y la sección quedó igual. Arreglarlos es cambiar a qué
   pulsan, y **si esos clics son seguros lo decides tú** (abajo, qué hace cada uno según la evidencia).
2. **La causa de «TO COMPLETE» no se puede determinar con la evidencia guardada.** Se sabe que el paso corrió
   en las 5 reservas y que la sección siguió pendiente. No se sabe si el panel se abrió, en qué campo quedó la
   temperatura ni qué pide el panel. Tampoco si el programa llegó a guardarlo. De esa corrida no hay captura
   del panel ni HTML.
3. **Un dato fuera de la planilla y de las constantes: no se puede medir.** Depende de qué campos pida el
   panel, y el panel no aparece en ninguna captura. La temperatura tiene fuente; la ventilación, la humedad o
   cualquier otro campo, no.

**PASO 0: FRENO (PREGUNTA).**

## Qué hace el programa en la sección Reefer

Lo hace `_cma_ajustes_reefer`, llamada por `reservar_cma` **antes de la guarda**, después de elegir el
itinerario. Corre igual con el candado cerrado.

| Paso | Qué hace | Selector | Dato | En el log (5 reservas) |
|---|---|---|---|---|
| 1. Abrir | Clic (JavaScript) en el primer `button`, `[role=button]`, `svg`, `i`, `[class*=edit]` o `[class*=pencil]` del `div` más cercano al primer elemento cuyo texto dice «reefer» y «complete» (menos de 120 caracteres). Si no lo encuentra, cinco selectores de respaldo, el primero `div:has-text('Reefer') button` | — | — | **Nada:** el programa no anota si abrió, ni por qué camino |
| 2. Captura | `cma_f<fila>_4b_reefer_drawer` | — | — | **0 de 5:** la versión que corrió ese día no la tenía (no hay «captura:» ni «no pude capturar») |
| 3. Temperatura | Enfoca un campo y teclea. Busca dentro del primer `.el-drawer`, `[class*="drawer"]` o `[role="dialog"]` del documento, o en todo el documento si no hay ninguno. Toma el primer campo visible cuyo contenedor dice «temperature», «temperatura» o «°c». Si hay «drawer» y ninguno calza, toma el primer campo visible de ese drawer | `_temp_reserva`: la columna de temperatura si la hoja la tiene; si no, `TEMP_REEFER`. La planilla no la tiene (`CICLO-cosco-campos-y-reminder.md`) | **5 de 5 «(focus)»:** enfocó *algún* campo; no se sabe cuál |
| 4. Guardar | Clic en el botón que dice exactamente «guardar», «save», «confirm» o «confirmar», dentro de `.el-drawer` o `[class*='drawer']`. Si no, el primer `.el-button--primary` de `.el-drawer` o de `[role='dialog']`. Si ninguno está visible, JavaScript que pulsa el primero con ese texto exacto, si existe | — | — | **5 de 5 «ajustes reefer guardados (vía JS)»:** ningún botón visible calzó. El JavaScript escribe ese mensaje **haya pulsado o no** |
| 5. Cerrar | Escape | — | — | — |

**Solo llena la temperatura.** Ventilación, humedad o cualquier otro ajuste del panel: no los intenta.

## Por qué queda «TO COMPLETE»

**Lo que muestran las capturas, en las 5 reservas** (las de cada paso son iguales o casi, por huella y por
diferencia de píxeles):

| Captura | Cuándo | Qué se ve |
|---|---|---|
| `4_itinerario` | **Antes** del paso Reefer | Sección Carga: «40' REEFER HIGH CUBE» con un «!» rojo; al lado, «Reefer TO COMPLETE» con su lápiz y «Configuración de liberación de vacío NOT FILLED» con el suyo, más una nota: completarla «mejorará el tiempo de procesamiento» |
| `5_review` | **Después** del paso, antes del envío | El pie de la misma página: «Faltan algunos ajustes para carga(s) especial(es), por favor complete» y, debajo, «Envío de la reserva» con «Enviar el booking» |
| `6_confirmado` | Después de pulsar el envío (21-09, con emisión) | La página vuelta a la sección Carga, con «Reefer TO COMPLETE». Ninguna confirmación |

**La cadena no cierra.** Las capturas y el log admiten cinco explicaciones, y no hay con qué separarlas:
- **(a)** El clic del lápiz no abrió el panel.
- **(b)** El panel se abrió, pero el «-20» quedó en otro campo. El paso 3 toma el primer elemento del
  documento cuya clase contiene «drawer», y en una página puede haber más de uno.
- **(c)** El panel pide más que la temperatura (ventilación, humedad u otro). Si es así, se cumple también el
  FRENA del dato que no está.
- **(d)** Su botón de guardar tiene otro nombre, el JavaScript no pulsó nada, y el Escape cerró el panel sin
  guardar.
- **(e)** El panel se guardó y el portal pide otra cosa.

Lo que las separa es una imagen o el HTML del panel abierto. El código de hoy saca esa imagen
(`4b_reefer_drawer`), pero **no ha corrido en CMA:** la última corrida de CMA es del 21-09, y el repo es del
23-09.

## Si el botón de envío depende de la sección

- **El botón no se deshabilita.** En las 5 capturas `5_review`, «Enviar el booking» está visible y con el
  color de un botón activo, con la sección pendiente y el aviso encima.
- **El envío sí depende de la sección.** En las 5 capturas `6_confirmado`, tomadas después del clic, la
  página volvió a la sección Carga, sin confirmación. Calza con un portal que rechaza el envío y lleva a lo
  que falta. Que el clic haya salido lo dice el log de esa versión; el HTML lo habría confirmado.
- **Con el código de hoy, ese caso sale «ENVIADA – REVISAR EN PORTAL», no «NO ENVIADA».** `_pulsar_boton` pulsa
  el botón porque está visible. CMA no tiene forma medida, y el programa no lee su validación: la marca
  «TO COMPLETE» y el aviso «Faltan algunos ajustes…». Es lo que se decidió para un envío pulsado sin
  confirmación. Va al residual.

## Los tres FRENA SI, uno por uno

1. **Un dato que no está en la planilla ni en las constantes:** sin medir. La temperatura sale de
   `TEMP_REEFER` (la planilla no tiene columna). Para la ventilación o la humedad no hay constante: ONE
   escribe un «0» fijo en su propio código y HYUNDAI un «0% CLOSED». Si el panel las pide, **frena aquí**, y la
   fuente la decides tú, como en COSCO.
2. **Un clic antes de la guarda (abrir, confirmar o guardar la sección):** se cumple. Los dos clics, con lo
   que hacen según la evidencia:
   - **El lápiz de «Reefer TO COMPLETE»** es el único control de la sección en las 5 capturas `4_itinerario`.
     Qué abre no está en ninguna captura (el comentario del código dice «drawer»; es una hipótesis). **Si el
     JavaScript no lo encuentra, el primer respaldo, `div:has-text('Reefer') button`, pulsa el primer botón
     visible de cualquier `div` que contenga la palabra.** El contenedor de la página entera la contiene. Ese
     botón puede ser cualquiera, por ejemplo «Deseleccionar» del itinerario, que está más arriba. El log no dice
     qué camino tomó.
   - **El guardar del panel:** su nombre y lo que hace no están en ninguna evidencia. El respaldo pulsa el
     primer botón principal de **cualquier** ventana `[role='dialog']` abierta, sea o no la del panel.
   - Nada de esto lo vigila la red: `test_candado` mira solo los textos dentro de `reservar_cma`, y estos
     clics viven en `_cma_ajustes_reefer`.
3. **La causa no se puede determinar:** se cumple (la sección anterior).

## Qué mirar en tu prueba con el candado cerrado

**No hay arreglo que confirmar.** Esta prueba es para separar las cinco explicaciones y saber qué pide el
panel. Ten presente que **con el candado cerrado el programa igual pulsa el lápiz y el guardar del panel**,
porque están antes de la guarda (ha sido así en toda prueba de CMA). Se detiene antes de «Enviar el booking».

En la carpeta de la corrida:

1. **`cma_f<fila>_4b_reefer_drawer.png`** (la imagen nueva, tomada después del lápiz y antes de teclear):
   - **¿Se abrió un panel con los ajustes reefer?** Si la imagen es la página de siempre, sin panel, el lápiz
     no abrió nada: es la explicación (a).
   - **¿Qué campos tiene y cuáles son obligatorios** (asterisco o texto rojo)? Temperatura, ventilación,
     humedad, otros. Cualquier obligatorio distinto de la temperatura no tiene fuente: esa es la decisión.
   - **¿Cómo se llama su botón de guardar** («Guardar», «Validar», «Aplicar»…)?
   - Es solo la ventana visible: si el panel tiene más campos abajo, no salen.
2. **`cma_f<fila>_5_review.png`:** si encima de «Envío de la reserva» sigue «Faltan algunos ajustes para
   carga(s) especial(es), por favor complete», la sección siguió pendiente.
3. **En `log.txt`**, después de «CMA · Configurando Ajustes Reefer»:
   - «captura: cma_f<fila>_4b_reefer_drawer.png».
   - «temperatura reefer: -20 °C (focus)» o «(locator)».
   - «ajustes reefer guardados» a secas o «(vía JS)». **El «(vía JS)» no prueba que haya guardado.**

## Premisas del encargo contrastadas (pieza 5)

- **«Las 5 capturas posteriores al envío muestran la página de revisión con «Reefer: TO COMPLETE» y sin
  confirmación»:** confirmada, 5 de 5. Con una precisión: no es una página de revisión aparte. Es la misma
  página del formulario, que después del clic vuelve a la sección Carga. La «revisión» (`5_review`) es su pie.
- **«El programa pulsa «Enviar el booking» solo si el botón está visible»:** confirmada en el código.
  Además, en las 5 reservas el botón **estaba** visible: el problema no es llegar al botón sino que el portal
  no envía con la sección pendiente. **La TAREA, «que llegue a pulsar», parte de una premisa que no se
  cumple:** ya llegaba y pulsaba.
- **«El peso y la temperatura salen de PESO_REEFER y TEMP_REEFER»:** confirmada para CMA. El peso va en la
  información extra de la carga: 5 de 5 «peso contenedor: … KGM (focus)». La temperatura va en el panel
  Reefer, por `_temp_reserva`.
- **Implícita: que el programa no intenta completar la sección.** Refutada: la abre, teclea la temperatura y
  la guarda. Lo que no se sabe es dónde falla.

## Hallazgos fuera de la sección Reefer (no tocados)

- **«marcado 'I Agree'» en las 5 reservas, sin ningún «I Agree» en pantalla.** El tercer selector,
  `input[type='checkbox']`, marca **la primera casilla visible de la página**, sea la que sea, antes de la
  guarda. Cuál fue no queda en ningún registro.
- **Una prueba de la red falla según el reloj.** `test_consola.test_todas_deja_una_sola_copia` falló en **4 de
  5** corridas de la red completa sobre HEAD, con `(5, 0, 5)` en vez de `(6, 1, 5)`. El código es el de
  `2c2ed4f`, cuyo censo pasó: la prueba ya dependía del reloj. La causa está medida:
  - Las carpetas de log se llaman `reservas_<naviera>_<usuario>_<AAAAmmdd_HHMMSS>`.
  - Una prueba anterior de la misma clase corre ONE. Si «todas» corre ONE en ese mismo segundo, las dos
    carpetas tienen el mismo nombre. La carpeta ya existía antes de la prueba, así que la resta de conjuntos
    la descarta. Es justo la de ONE, la que anota la copia.
  - Con un envoltorio de diagnóstico (en memoria, sin tocar `tests/`), en las 2 corridas que fallaron «todas»
    no dejó ninguna carpeta nueva de ONE: su nombre ya estaba. En la que pasó, la anterior era de 1 segundo
    antes.
  - Con la prueba de ONE justo antes, falló 4 de 6 veces. Con la de HYUNDAI en su lugar (control), 0 de 6.

  **Es de la prueba, no del programa.** No la arreglé porque está fuera del encargo: queda propuesta como
  tarea aparte. **Mientras tanto, la red completa no sirve de puerta:** una falla con `(5, 0, 5)` en esa
  prueba no dice nada del cambio.

## Universo y cobertura (pieza 3)

- **Carpetas en `logs/`:** 6. CMA aparece en 2:
  - `web_cma` del 21-09: 5 reservas con emisión. Las 5 llegaron al paso Reefer.
  - `web_todas` del 21-09: 5 reservas de CMA, **0 llegaron al paso Reefer**. Las 5 quedaron REVISAR al elegir
    el itinerario.
- **HTML en `logs/`:** 0 archivos. `_cma_*` tampoco tiene volcado con `AQUASHIELD_DESCUBRIR`, a diferencia de
  MSC, COSCO, HYUNDAI y MAERSK.
- **Capturas miradas enteras:**
  - `4_itinerario` de las filas 5 y 6, `5_review` de las filas 5 y 8, y `6_confirmado` de la fila 5.
  - Las demás, comparadas por huella y por diferencia de píxeles:
    - `6_confirmado`: las 5 iguales salvo 3 píxeles de la barra de desplazamiento.
    - `5_review`: dos grupos, los dos mirados.
    - `4_itinerario`: la misma página, desplazada unos píxeles.
  - Dos recortes temporales para ampliar, borrados después.
- **Log:** las 190 líneas de `web_cma` contadas por mensaje del programa. En pantalla, solo mensajes propios
  del programa, por lista blanca (ver los defectos 1 y 2).
- **Código:** `reservar_cma`, `_cma_completar_info_extra`, `_cma_ajustes_reefer`, `_cma_comentarios`, el
  bloque de «I Agree» y `Registro.captura`. Historia de `_cma_ajustes_reefer` en git: sin cambios desde el
  primer commit (`14aa9ef`).
- **La red sobre HEAD:** 185 pruebas, 5 corridas (tabla en Re-medir). Las 4 fallas son siempre la misma
  prueba. El censo de mutaciones no se volvió a correr: el código es el de `2c2ed4f`, cuyo censo pasó (345
  mutaciones, 397 pares).

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\sonda_secretos.py --dry-run
```

- **El paso Reefer:** en `logs/web_cma_*/log.txt`, contar «CMA · Configurando Ajustes Reefer», «temperatura
  reefer: -20 °C (focus)», «ajustes reefer guardados (vía JS)» y «captura: cma_f…_4b_reefer_drawer». Hoy dan
  5, 5, 5 y 0. El log tiene fin de línea CRLF: cuenta por línea, sin «\n» en el patrón (defecto 3).
- **Las capturas:** comparar `cma_f<fila>_<paso>.png` entre filas con una huella y con la diferencia de
  píxeles, y mirar una por grupo.
- **La prueba que depende del reloj:**

  ```powershell
  cd tests
  python -m unittest test_consola.TestEjecutarReservas.test_sin_emitir_solo_si_volvio_sin_emitir test_consola.TestEjecutarReservas.test_todas_deja_una_sola_copia
  ```

  Repetida 6 veces: 4 fallas. El control cambia la primera por `test_solo_primera_fila`: 0 fallas.

| Corrida de la red sobre HEAD | Cómo | Resultado | Carpetas de ONE nuevas en «todas» |
|---|---|---|---|
| 1 | `tests\correr.py` | 184 de 185; falla `test_todas_deja_una_sola_copia`, `(5, 0, 5)` | — |
| 2 | `tests\correr.py` | Igual | — |
| 3 | Envoltorio de diagnóstico | 185 de 185 | 1 (la anterior, 1 s antes) |
| 4 | Envoltorio de diagnóstico | 184 de 185, la misma | 0 (el nombre ya existía) |
| 5 | Envoltorio de diagnóstico | 184 de 185, la misma | 0 (el nombre ya existía) |

El envoltorio corre la red con `discover`, igual que el corredor, y envuelve en memoria esa prueba para anotar
las carpetas `reservas_one_*` de antes y de después. No compara la foto de los originales: eso lo hace el
corredor, y en las corridas 1 y 2 dio 0 cambios.

## NO retroceder (pieza 2)

- **No des por completada la sección por lo que diga el log.** «(focus)» no dice en qué campo quedó la
  temperatura, y «guardados (vía JS)» se escribe aunque no se haya pulsado nada.
- **No quites la captura `4b_reefer_drawer`:** es la única evidencia que habrá del panel.
- **No agregues un valor por defecto** para la ventilación ni para otro ajuste del panel: si es obligatorio,
  la fuente la decides tú.
- **No cambies a qué pulsan el lápiz ni el guardar del panel** sin tu decisión: son clics antes de la guarda.

## Defectos de instrumento cazados (pieza 4)

1. **Una ruta real en mi sesión.** Mi primer filtro del log enmascaraba por lista negra y dejó pasar la línea
   «intento con …», con los puertos de la reserva. No quedó en ningún archivo. Lo corregí con lista blanca.
2. **Números de reserva reales en mi sesión.** La lista blanca con «EMISI» y «err», aplicada al log entero
   de `web_todas`, trajo líneas de otras navieras, con sus números de booking. No quedó en ningún archivo. Lo
   corregí limitando a un rango de líneas de CMA y a mensajes propios del programa.
3. **Un cero con patrón frágil.** Conté «guardados» sin «(vía JS)» con `\n` en el patrón, sobre un log CRLF.
   El 0 era correcto por casualidad; lo volví a contar por línea (0 y 5).
4. **Un texto ilegible que casi entra como evidencia.** Arriba de `5_review` asoma una línea del resumen,
   cortada por el encabezado fijo del portal. Ampliada, sigue ilegible: no la uso.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| Reefer «TO COMPLETE» | FRENO: clics antes de la guarda y causa sin evidencia | …decides sobre los dos clics y tu prueba deja `4b_reefer_drawer` |
| Los campos del panel además de la temperatura | Nadie los ha visto | …la imagen del panel los muestra; si hay obligatorios sin fuente, decides la fuente |
| «ajustes reefer guardados (vía JS)» se escribe sin saber si pulsó | Cambiarlo es parte del arreglo del paso 4 | …se toca el guardar del panel |
| Un envío de CMA con la sección pendiente sale «ENVIADA – REVISAR EN PORTAL» | El programa no lee la validación de CMA; su forma está en las 5 capturas (`TO COMPLETE`, «Faltan algunos ajustes…») | …decides que CMA la lea y dé NO ENVIADA |
| «I Agree» marca la primera casilla visible de la página | Clic antes de la guarda, fuera de la sección Reefer | …decides qué casilla es la correcta |
| `test_candado` no ve los clics de los ayudantes de CMA | Mira solo los textos de `reservar_cma` | …se toca un ayudante de CMA |
| `test_todas_deja_una_sola_copia` falla según el reloj (4 de 5 hoy) | Colisión de nombres de carpeta en el mismo segundo; fuera del encargo | …se arregla la prueba (queda propuesta como tarea aparte). Hasta entonces, la red completa no sirve de puerta para un commit de código |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v12**:
- **PASO 0 con veredicto de cuatro valores:** FRENO (PREGUNTA).
- **Todo registro es una hipótesis:**
  - El log del programa dice «guardados» sin haberlo comprobado.
  - El comentario del código dice que el lápiz abre un «drawer», y nadie lo ha visto.
- **Todo salto silencioso lleva contador:** el paso 1 no anota si abrió, ni por qué camino; queda al residual
  como parte del arreglo.
- **Control positivo:** cada conteo del log con su control (5 encabezados de reserva, 5 capturas `5_review`).
  La prueba que depende del reloj, con su control (0 de 6).
- **La unidad la fija el sujeto:** la reserva (5), no la captura (15 de los tres pasos).
- **Re-medir contra HEAD:** correr la red sobre HEAD destapó la prueba que depende del reloj. El número
  heredado («la red pasa», de `2c2ed4f`) ya no era cierto. El código que corrió el 21-09 tampoco es el de hoy:
  le faltaba la captura del panel.
- **Un número fijo deja de morder:** el nombre de carpeta al segundo es un número fijo. Alcanzó mientras las
  pruebas tardaban más de un segundo entre sí.
- **FRENAR cuando la decisión es de negocio:** los clics antes de la guarda y la fuente de los datos.
- **Se declaran el residual y las premisas.**
- **El push se entrega, no se hace:** no hay remoto.

Reglas propias del módulo (`CLAUDE.md`): casos sintéticos, la sonda antes del commit y los logs en solo
lectura.

**Choques:** ninguno. El freno cae antes de cualquier cambio.

## Entregable (pieza 8)

Este `.md`, sin renderizar, y `CLAUDE.md` con dos notas: los clics de CMA antes de la guarda y la prueba que
depende del reloj. Pasan la sonda de staging antes de su commit.
