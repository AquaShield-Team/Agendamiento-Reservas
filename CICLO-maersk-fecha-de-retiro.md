# CICLO · MAERSK no llega a su guarda: el portal pide la fecha de retiro (FRENO)

**Módulo:** Agendamiento Reservas · **Encargo 35** · **Fecha:** 2026-09-27 · **Método:** skill `metodo-ciclo` v14 ·
**Commits** (locales; el repo no tiene remoto, así que no hay push que entregar): solo el de este informe, con
`CLAUDE.md` al día. **Sin cambios de código:** el encargo frenó.

**Base: `C:\dev\Agendamiento Reservas` @ `10b5769` · árbol limpio** (pieza 9). Lo medido sale de la corrida de hoy con
el lanzador de prueba (`web_todas_<operador>_20260927_211531`, la más reciente de `logs/`), de los HTML de MAERSK
guardados desde el 24-09 y de la corrida del 21-09, la única que llegó a la revisión de MAERSK.

> Datos reales solo en lectura. Se leyeron los `log.txt`, los HTML de MAERSK y la planilla que subiste (sus
> encabezados, y de la fila 10 solo conteos). Los HTML se abrieron en un Chromium sin red y sin el JavaScript de la
> página. Las capturas se leyeron con OCR, sin mirarlas. En este informe no van nombres de naves, viajes, puertos ni
> depósitos, ni números de reserva.

**Resumen.**
- **MAERSK eligió la nave y pulsó «Review booking»; el portal no avanzó.** Amplió la búsqueda una vez, pulsó el «Book»
  de la salida pedida y pasó «Recommended services». En «Additional details» completó la referencia y pulsó «Review
  booking». Entonces el portal marcó «Please correct the following errors» y «Pick up date cannot be left blank», y se
  quedó en esa pantalla. Esa fecha es la de retiro del contenedor, y el programa no la elige desde `0f1507e`, por tu
  decisión («la define la naviera»). A los 15,5 s, `_mk_esperar_revision` cortó: NO ENVIADA con «Revisión de MAERSK».
- **No faltó bajar.** El programa lleva el botón a la vista antes de pulsarlo, y el error apareció después del clic:
  antes no estaba.
- **Se cumplen las dos condiciones del FRENA SI.** El portal pide un dato que la fila no trae: la planilla no tiene
  ninguna columna de fecha. Y elegirlo exige clics nuevos: «Choose another date» o «Click to choose date», un día del
  calendario y su «Done». **No cambié el código:** decides tú (abajo, «Qué decides tú»).
- **Con la fecha, el portal sí avanza: ya se vio el 21-09.** Esa corrida, con el código de entonces (el primer día
  habilitado) y el candado abierto, eligió la fecha en sus 5 filas de MAERSK, llegó a la revisión en las 5 y las 5
  terminaron EMITIDA.
- **La casilla de términos no está en ningún HTML guardado.** La pantalla de hoy es «Additional details», sin ninguna
  casilla, y ninguno de los 83 HTML de MAERSK es la revisión. Queda como hoy, con «el último checkbox» y su FRENO. Las
  capturas de la revisión del 21-09 sí la muestran: «I have read and accept all the terms and conditions of this
  booking», justo antes de «Submit booking».
- **ONE llegó a su guarda** (OK-EJEMPLO) con «prefiero la directa; descarto 3 con transbordo»: el cambio del encargo 34
  funcionó en el portal.

## Veredicto del PASO 0, por parte del encargo

| Parte | Veredicto | Qué quedó |
|---|---|---|
| MAERSK queda NO ENVIADA antes de su guarda | **PREGUNTA:** se cumple el FRENA SI | Nada en el código; decides tú |
| FRENA SI: el portal pide un dato que la fila no trae | **Se cumple:** la fecha de retiro | |
| FRENA SI: llegar a la guarda exige un clic nuevo distinto de la casilla de términos | **Se cumple:** elegir la fecha en su calendario | |
| «Le faltó bajar en la pantalla para llegar a la opción de enviar» | **DESCARTE** (medido abajo) | Nada |
| La casilla de términos, por su texto, con el HTML de esa pantalla | **NOTA:** la casilla no está en el HTML | «El último checkbox» queda como hoy |

## Lo que dicen `log.txt`, el HTML y las capturas de hoy

**`log.txt`**, en orden:
1. «Select sailing» con sus «Book» a la vista en 2,1 s.
2. 25,7 s después, «pulsando 'Search more sailing options'…». La salida pedida no estaba en la primera lista, y el
   programa amplía hasta encontrarla. Ese tiempo casi seguro se fue en `_mk_ampliar`, esperando que el botón se
   habilitara (hasta 40 s). Es inferido del código, no medido: la espera de las tarjetas de `_mk_elegir_nave` (hasta
   20 s) corta con los mismos «Book» que ya estaban a la vista.
3. «nave seleccionada», 1,3 s después: el «Book» se pulsó.
4. «Recommended services»: sin servicios, «Continue».
5. «Additional details»: la referencia de retiro («haulage reference») completada, la captura `mk_f10_5c_details` y,
   0,1 s después, «pulsado 'Review booking'».
6. 15,5 s después, sin la revisión, el corte: la evidencia `mk_f10_sin_objetivo` (captura y 10 HTML) y la NO ENVIADA.

**El HTML de donde cortó** (`mk_f10_sin_objetivo.html`, con el portal ya respondiendo al clic):
- El título del paso es «Additional details». La barra de pasos dice «Booking Information · Select sailing ·
  Recommended services · Additional details · Review booking»: quedó en el 4.º de 5.
- **Los errores del portal:**
  - arriba, un aviso de error «Please correct the following errors», con el enlace «Pickup date»;
  - en «Container stuffing details», bajo «Pick-up date and reference», «No date selected · Click to choose date»
    (`data-test` `haulage-invalid-date`);
  - al pie de esa sección, «Pick up date cannot be left blank» (`haulage-invalid-date-footer`).
- **Los botones del paso:** «Choose another date» (`haulageSettingsPickupDateButton-allContainer`, habilitado),
  «Select a different depot» (deshabilitado; el depósito de retiro ya venía puesto), «Optional parties» y «Review
  booking» (`details-submit`, habilitado). Ningún «Submit booking», «Book now» ni «Done».
- **Un campo de fecha oculto:** un `input type="date"` dentro de un `span.hidden-date-picker` con `aria-hidden`. No es
  para escribir en él: la fecha se elige en el calendario.
- **Un aviso del portal junto a la fecha:** «Additional charges can incur if the container is picked up from a
  different location than the origin or the date selected exceeds the agreed free time or other standard details.»
- **Casillas:** 0, ni `input` checkbox ni `mc-checkbox`, tampoco dentro de las raíces shadow ni en los 9 marcos.

**Las dos capturas de «Additional details», por OCR** (frases de la interfaz que aparecen):

| Frase | `mk_f10_5c_details` (antes del clic) | `mk_f10_sin_objetivo` (donde cortó) |
|---|---|---|
| «Additional details» (control: tiene que estar) | sí | sí |
| «Pick-up date» | sí | sí |
| «No date selected» · «Click to choose date» | sí · sí | sí · sí |
| «Review booking» | sí | sí |
| «Choose another date» | no | no |
| «Please correct the following errors» | **no** | **sí** |
| «Pick up date cannot be left blank» | **no** | **sí** |

- La fecha ya faltaba antes del clic, y los dos errores aparecieron después. El clic de «Review booking» llegó al
  botón, y el portal validó el formulario y lo rechazó por la fecha.
- «Choose another date» está en el HTML, pero el OCR no lo lee. Lo probable es que sea por ser el texto de un botón:
  el OCR no lee texto claro sobre un botón de color (medido en el encargo 29). «Click to choose date» sí se lee.

**La planilla de la corrida** (la que subiste a las 21:14, en `%TEMP%`, y también `Reservas AQUASHIELD.xlsx`):
- la hoja CONSOLIDADO tiene 9 columnas (Naviera, Pto. Embarque, Puerto Descarga, Destino Final, NAVE, Viaje, Contrato /
  Cotización, Estado y N° de reserva emitida), ninguna de fecha;
- la fila 10 trae 7 celdas con valor: ninguna es una fecha de Excel, un número ni un texto con forma de fecha.

`log.txt` lo confirma: MAERSK buscó las salidas «desde mañana», el aviso que sale cuando la fila no trae día de carga.

## Lo que ya se vio el 21-09

La corrida `web_todas_<operador>_20260921_145827` es la única de `logs/` que llegó a la revisión de MAERSK. Es de
antes de que se guardara el HTML, así que deja `log.txt` y capturas.
- **`log.txt`, en el tramo de MAERSK:** 5 «fecha de retiro seleccionada», 5 «pulsado 'Done'», 5 «pulsado 'Review
  booking'» y 5 «términos y condiciones aceptados (mc click)». Las 5 filas terminaron EMITIDA, cada una con su número de
  reserva.
- **Las capturas de «Additional details»** (`mk_f30` a `mk_f34`, `_5c_details`, por OCR): «Pick-up date» sí; «No date
  selected» y «Click to choose date», no. La fecha ya estaba puesta.
- **Las capturas de la revisión** (`mk_f30` a `mk_f34`, `_6_review`, por OCR):
  - son de la ventana, abajo de todo;
  - traen la sección «Terms & Conditions», la casilla «I have read and accept all the terms and conditions of this
    booking» y el botón «Submit booking»;
  - no traen la barra de pasos.
- **La casilla la marcó la 3.ª vía de la cascada** («mc click»: `page.locator("mc-checkbox").last`). Las dos primeras,
  la del `input` y la de `get_by_role`, no la dieron por marcada; por qué, el log no lo dice.

Lo que esto mide: **con una fecha de retiro, el portal pasa a la revisión.** Lo que no mide: el HTML del calendario y el
de la revisión (no se guardaban), si el portal acepta cualquier fecha, y cuánto costaron esas fechas.

## «Le faltó bajar en la pantalla»: no

- Antes de pulsar «Review booking», el programa lleva el botón a la vista (`scroll_into_view_if_needed`), y el clic de
  Playwright también lo hace. `log.txt` dice «pulsado 'Review booking'», y la respuesta del portal (los dos errores que
  no estaban antes del clic) muestra que el clic salió.
- El localizador del programa (`mc-button, button, [role='button'], a` con el texto «Review booking»), sobre el HTML
  guardado, da solo el `mc-button` `details-submit` y el botón de adentro. El paso «Review booking» de la barra es un
  `div` y no calza. La revisión adversarial lo emuló así.
- Bajar no llena la fecha: el portal no deja pasar a la revisión sin ella.
- En la revisión, cuando se llegue, el programa ya baja al final antes de los términos
  (`window.scrollTo(0, document.body.scrollHeight)`). Bajar ya está en los dos lugares. Las capturas del 21-09 muestran
  que abajo de todo están la casilla y «Submit booking».

## La casilla de términos: no está en ningún HTML guardado

`todas_mk.py` abrió los **83 HTML de MAERSK** de `logs/` (del 24 al 27-09, la página y sus marcos): los 83 se
abrieron, 0 fallaron.
- **Ninguno es la revisión:** ningún título «Review booking» y ningún botón «Submit booking» ni «Book now».
  - `mk_f30_guarda.html`, del 24-09, se llama «guarda», pero es de «Select sailing». Es de antes de que MAERSK cortara
    sin la nave.
- **Casillas:** solo en uno, el de «Select sailing» del 25-09 a las 13:47. Son 5 interruptores de la ventana de cookies
  (Essential, Functional, Statistical, Marketing y Unclassified), no los términos.
- **«Terms»:** aparece en las 8 páginas (sin contar los marcos). En 7, solo en el enlace «Terms & conditions» del pie de
  página. En la del 25-09, además, en 26 enlaces de la ventana de cookies. En ninguna es una casilla.

Por eso la casilla queda como hoy, como dice el encargo. Lo que se sabe de ella sale de las capturas y del `log.txt` del
21-09: su texto, y que la marcó el clic en el último `mc-checkbox` (la cascada da por marcada la casilla después de
ese clic, sin comprobarlo; las 5 reservas se emitieron).

Una observación del HTML del 25-09: si una pantalla trajera la ventana de cookies abierta, «el último checkbox» sería
su interruptor «Unclassified». En la revisión no se sabe, porque no está guardada.

## Qué decides tú

**1. La fecha de retiro de MAERSK.** Decidiste que la define la naviera, y el 24-09 el programa dejó de elegirla
(`0f1507e`, con la opción a de `CICLO-cma-reefer-y-fecha-maersk.md`). Hasta ahí abría el selector, marcaba el primer día
habilitado y pulsaba «Done». El residual de `CICLO-maersk-corta-en-la-revision.md` lo anticipaba: «si MAERSK no avanza
sin fecha, todas sus filas quedan NO ENVIADA en la revisión». Hoy se midió que no avanza. Las opciones:
- **a) Mantener la regla.** Cada fila de MAERSK que llega a «Additional details» queda NO ENVIADA ahí.
  - El panel cierra el navegador de cada naviera al terminar sus filas (`ctx.close()` en `_web_worker`): la reserva a
    medio armar se pierde, y el operador la arma entera en el portal.
  - No cambia el código.
- **b) Que la fecha venga en la planilla** (la que recomiendo). Agregas una columna «Fecha de retiro»: los dos
  lectores ya ubican un encabezado con «retiro» (`dia_retiro`), y hoy la planilla no la tiene.
  - Para las filas que la traen, el programa abre «Choose another date» o «Click to choose date» por su texto, elige
    ese día en el calendario por su fecha y pulsa «Done». No escribe en el campo de fecha oculto.
  - Una fila sin ella queda NO ENVIADA con un motivo que lo dice, sin abrir el selector.
  - Son clics nuevos antes de la guarda, cada uno por su texto.
  - El HTML del calendario no está guardado: el 21-09 no se guardaba, y desde el 24-09 no se abre. La primera corrida
    tendría que dejar su evidencia antes de elegir, como el modal de HYUNDAI.
  - **Ojo con MSC:** `_msc_desde` ya usa esa columna. Busca desde el día de carga y, si la fila no lo trae, desde el de
    retiro (`CICLO-proxima-salida.md`). Con la columna en CONSOLIDADO, las filas de MSC que la traigan sin día de carga
    buscarían desde esa fecha. Decides si está bien así o si la columna es solo de MAERSK.
- **c) Que el programa la calcule.** Por ejemplo, el primer día que el portal habilita, como antes de `0f1507e`, o N
  días antes de la salida elegida.
  - El primer día habilitado es el camino con que el 21-09 llegó a la revisión y se emitieron las 5.
  - El portal avisa que una fecha que excede el tiempo libre acordado puede tener cargos: es una regla con costo.
  - «El primer día habilitado» es un clic por posición, que la regla de los clics a ciegas no permite. Habría que
    elegirlo por su fecha.

Recomiendo la b porque respeta que el programa no invente un dato que la fila no trae, y cada clic es por su texto.
Pero la regla del retiro es tuya.

**2. El motivo de la NO ENVIADA.** Hoy dice «no encontré la pantalla de revisión («Review booking»), que no apareció en
15 s, así que no pulsé nada», y no dice que el portal pidió la fecha. Puedo hacer que, cuando la revisión no aparece,
lea los errores de «Additional details» y los ponga en el motivo: «el portal pide: Pickup date». Solo lee: sin clics ni
esperas nuevas. Con la a, es lo que le dice al operador qué completar. ¿Lo hago?

**3. Los términos y condiciones.** Siguen con «el último checkbox» hasta que una corrida llegue a la revisión y deje
`mk_f<fila>_guarda.html`. Con ese HTML se identifica por su texto, que según las capturas del 21-09 es «I have read and
accept all the terms and conditions of this booking».

## Re-medir (pieza 1)

Las sondas son de solo lectura y no se versionan, porque leen datos reales. Quedaron en el scratchpad de esta sesión
(`$env:TEMP\claude\<proyecto>\<sesión>\scratchpad\e35`), que puede limpiarse; sin ellas, estos números no se re-miden.
Todas abortan si no pasa su control positivo, salvo `ultimas.py`, que solo lista.
- **`ultimas.py`:** las carpetas más recientes de `logs/`, con el operador tapado, y los archivos de MAERSK de la
  última. Sin control.
- **`sonda.py <archivo.js> <html>…`:** corre un JavaScript sobre un HTML guardado, sin red y sin los `<script>` de la
  página. Su control: un `mc-checkbox` sintético con el `input` dentro de una raíz shadow declarativa.
  - `detalles.js`: los campos, errores y botones de «Additional details».
  - `casillas.js`: el título, las casillas, «terms» y el botón de envío de una página.
  - `terms_hoja.js`: dónde aparece «terms».
  - **No correr `retiro.js` ni `esqueleto.js` sin tapar su salida:** imprimen textos de la página, y `retiro.js`
    imprimió el nombre del depósito (pieza 4).
- **`crudo.py <texto> <html>…`:** en qué etiqueta y con qué atributos aparece un texto de la interfaz en el HTML crudo.
- **`todas_mk.py`:** `casillas.js` sobre los 83 HTML de MAERSK, con los que no pudo abrir contados. Su control: una
  revisión sintética con casilla, «terms» y «Submit booking».
- **`ocr.py`:** las frases de la tabla de hoy en las dos capturas, sin mirarlas. Controles: una imagen sintética, y
  «Additional details» en cada captura.
- **`ocr21.py`:** las capturas del 21-09 (revisión y «Additional details»), y la línea de la casilla. Controles: una
  imagen sintética, y que el OCR lea al menos 100 palabras de cada captura.
- **`log21.py`:** por corrida, cuántas veces aparecen en el tramo de MAERSK de `log.txt` la fecha de retiro, «Done»,
  «Review booking» y cada vía de los términos. Su control: un log sintético.
- **`planilla.py`:** los encabezados de la planilla y los conteos de la fila 10, sin valores. Sus controles: un libro
  sintético con «Fecha de retiro», y una fila sintética con cada clase de fecha.

En PowerShell, desde `C:\dev\Agendamiento Reservas`: `$env:PYTHONIOENCODING='utf-8'` y después
`python "<scratchpad>\e35\<sonda>.py" …`.

## NO retroceder (pieza 2)

- **No trates el corte «Revisión de MAERSK» de hoy como un problema de desplazamiento:** el portal validó el
  formulario y pidió la fecha de retiro. Bajar no la llena.
- **No vuelvas a elegir la fecha de retiro sin tu decisión:** pide clics nuevos y un dato que la fila no trae, y el
  portal avisa cargos si excede el tiempo libre.
- **No leas la NO ENVIADA «Revisión de MAERSK» como que el clic de «Review booking» no salió:** el error del portal
  aparece después del clic.
- **No identifiques los términos sin el HTML de la revisión:** las capturas del 21-09 dan su texto, no su objetivo en la
  página.

## Universo y cobertura (pieza 3)

- **`logs/`:** 21 carpetas; la más reciente, la de hoy a las 21:15, con 35 archivos. De MAERSK trae 10 HTML (la página
  y 9 marcos, todos de `mk_f10_sin_objetivo`) y 8 capturas.
- **HTML de MAERSK:** 83 en `logs/`, del 24 al 27-09 (8 páginas y 75 marcos): 83 abiertos, 0 fallidos.
  - Con casillas: 1, las de cookies.
  - Revisión: 0.
- **`log.txt` con un tramo de reservas de MAERSK:** 9 corridas, del 21 al 27-09. Solo la del 21-09 trae la fecha de
  retiro y la revisión.
- **Capturas, todas por OCR y ninguna mirada:**
  - hoy, 2 (`mk_f10_5c_details` y `mk_f10_sin_objetivo`);
  - del 21-09, 10 (`_5c_details` y `_6_review` de sus 5 filas).
- **Planilla:** 2 archivos, la hoja CONSOLIDADO de cada uno; la fila 10.
- **No medido:**
  - el HTML del calendario y el de la revisión (nunca se guardaron);
  - si el portal acepta cualquier fecha, y qué cargos tuvieron las del 21-09;
  - en cuál de las dos esperas de «Select sailing» se fueron los 25,7 s (inferido del código, arriba).

## Defectos de instrumento cazados (pieza 4)

1. **Tomé los HTML como todo el registro de MAERSK.** Escribí que el calendario y la revisión no se veían desde el
   24-09, sin mirar lo anterior. La corrida del 21-09 no tiene HTML, pero su `log.txt` y sus capturas muestran la fecha
   elegida, la revisión y las 5 EMITIDA. Lo cazó la revisión adversarial. Es el defecto que el método ya registra:
   tomar un tipo de archivo como si fuera todo el registro.
2. **`esqueleto.js` cortaba la lista de botones en 60,** y los enlaces del encabezado la llenaron: «Review booking»
   (`details-submit`) no aparecía, como si el botón no existiera. Lo cazó `crudo.py`, que lo encontró en el HTML crudo
   como `mc-button label="Review booking"`. `detalles.js` lee solo el contenido del paso.
3. **`planilla.py` dio «Puerto Descarga» como columna de fecha:** buscaba «carga» como parte de la palabra. Leído, es
   el puerto. Es el mismo defecto que la regla de la palabra entera corrige en el programa.
4. **`planilla.py` contaba solo las celdas de tipo fecha.** Al agregarle los números y los textos con forma de fecha,
   la herramienta Bash convirtió `\\b` en `\b`, y en el archivo quedaron dos caracteres de retroceso: esa cuenta no
   podía dar otra cosa que 0. Lo vi antes de usar el número. Se rehízo con un archivo escrito aparte, con un control de
   la fila que aborta. En la misma edición, `write_text` de Python dejó el archivo con CRLF, y la aserción del ancla lo
   frenó.
5. **El control de `ocr21.py` pedía «Review booking» y después la barra de pasos,** y abortó: las capturas de la
   revisión del 21-09 son de la ventana, abajo de todo, sin la barra. El control pasó a ser que el OCR lea al menos 100
   palabras. Además, el OCR lee la «I» de «I have read» como «|»: la sonda lo tolera.
6. **El comentario de `retiro.js` decía que tapaba las palabras con mayúscula,** y solo tapaba las cifras: imprimió en
   mi consola el nombre del depósito de retiro. No está en ningún archivo del repo ni en este informe.
7. **Dos comandos míos imprimieron en mi consola la ruta de la carpeta de la corrida,** que lleva el nombre del
   operador. Los siguientes la toman sin imprimirla. Tampoco está en ningún archivo del repo ni en este informe.
8. **Usé `sort` de Git Bash, que Defender bloquea** (`CLAUDE.md` global). Falló a la vista; lo rehíce con Python. Sin
   efecto en los resultados.

## Premisas del encargo contrastadas (pieza 5)

- **«MAERSK avanzó hasta el último paso»:** hasta el penúltimo. Llegó a «Additional details», el 4.º de 5; «Review
  booking», el 5.º, no se mostró.
- **«Le faltó bajar en la pantalla para llegar a la opción de enviar»:** no. Pulsó «Review booking», y el portal
  respondió con el error de la fecha.
- **«Con el HTML de esa pantalla, identificar la casilla de términos»:** esa pantalla no es la revisión, y no trae
  ninguna casilla.
- **De `CICLO-maersk-corta-en-la-revision.md`, «si el portal no avanza sin ella, corta en la revisión»:** confirmado,
  tal cual.
- **Del residual de `CICLO-one-y-maersk-eligen-la-nave.md`, «`_mk_pulsar_book` no cambió: que pulse el «Book» de esa
  tarjeta está inferido (…), no probado»:** ahora se vio en el portal. Pulsó el «Book» y el portal pasó a «Recommended
  services»: esa fila del residual se cierra. ONE también llegó: OK-EJEMPLO, con la directa.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| Cada fila de MAERSK que llega a «Additional details» queda NO ENVIADA ahí | Tu regla (la fecha la define la naviera) y el portal, que no avanza sin ella | …eliges a, b o c |
| El motivo dice «no encontré la pantalla de revisión», no que el portal pide la fecha | Fuera del encargo; te lo propongo | …me dices que sí |
| Los términos siguen con «el último checkbox» (FRENO); su texto se conoce por las capturas del 21-09 | Ningún HTML de la revisión guardado | …una corrida llega a la revisión y deja `mk_f<fila>_guarda.html` |
| El HTML del calendario de la fecha de retiro no está guardado | El 21-09 no se guardaba, y desde el 24-09 no se abre | …eliges b o c |
| MAERSK amplió una vez antes de encontrar la salida (25,7 s entre la lista y el clic) | Hace lo que se decidió; la espera, inferida del código | …la espera molesta |
| La fecha de zarpe con «Select tomorrow» si la fila no trae día de carga | Fuera del encargo | …lo decides |
| La prueba del puerto del panel falló una vez en la suite completa y pasó en las demás | Intermitente; fuera del encargo | …la tarea aparte mide la causa |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v14**.
- **PASO 0 con sus cuatro valores:** PREGUNTA (la fecha de retiro), DESCARTE (bajar) y NOTA (la casilla no está en el
  HTML); CICLO no salió.
- **FRENAR cuando la decisión es de negocio:** la fecha de retiro, con cargos si excede el tiempo libre. Se entrega lo
  medido y las opciones; no elegí por ti.
- **Control positivo que aborta:** en cada sonda salvo `ultimas.py` (pieza 1). En `ocr.py`, la sensibilidad queda a la
  vista: las frases de error que no están antes del clic sí se leen en la captura de después.
- **Todo salto silencioso lleva contador:** 83 HTML, 83 abiertos, 0 fallidos.
- **El barrido va sobre todos los registros:** los HTML no eran todo; el 21-09 estaba en `log.txt` y en las capturas
  (pieza 4, 1).
- **Todo registro es una hipótesis:** la premisa de bajar, y el motivo de la NO ENVIADA, que se leía como que el clic
  no salió.
- **Re-medir contra HEAD:** el código se leyó en `10b5769`.
- **Declarar las premisas refutadas y el residual:** piezas 5 y 6.
- **Verificación adversarial:** una revisión de este informe contra la evidencia (pieza 8).
- **Choques entre reglas:**
  1. **«Corregirlo» contra el FRENA SI:** el FRENA SI manda. No cambié nada del flujo.
  2. **«Identificar la casilla con el HTML de esa pantalla» contra lo medido:** la pantalla no es la revisión. Queda
     como hoy, como dice el encargo, aunque las capturas del 21-09 den su texto.
  3. **«Leer el motivo en la captura» contra la regla de no mirar capturas reales:** se leyeron con OCR, sin mirarlas.
     Se cumplen las dos.

Reglas del módulo: nada de `logs/` en el repo; ningún nombre de nave, viaje, puerto, depósito ni operador, ni número de
reserva, en este informe; `test_candado` sin cambios (no cambió nada del código); la sonda de secretos antes del commit;
los textos en español con tuteo.

## Entregable (pieza 8)

- **Este `.md`:** no se convirtió en página; se leyó como texto.
- **`CLAUDE.md` al día,** en el mismo commit: MAERSK no avanza sin la fecha de retiro, ya avanzó con ella el 21-09, y
  ningún HTML guardado es la revisión.
- **La red, sin cambios:** 415 pruebas, 1107 mutaciones y 1337 pares, los de `4ae4fd6`.
- **La suite sobre la base (`10b5769`), dos veces:**
  - La primera dio 414 en verde y 1 error:
    `test_web.TestArranqueDelPanel.test_cierra_a_la_fuerza_al_que_ocupa_el_puerto`, con la conexión rechazada al
    pedir `/api/estado` en el puerto siguiente.
  - Sola, esa prueba pasó 6 de 6 (3 con la salida guardada en `puerto_solo.txt`). La segunda corrida completa dio las
    415 en verde (242 s), con 0 cambios en los originales.
  - Es intermitente y no la toca este encargo, que no cambia código. La hipótesis, sin medir: la prueba espera que el
    puerto siguiente a uno al azar esté libre. Quedó propuesta como una tarea aparte.
- **El commit:** la sonda de secretos dio 0 sobre el árbol y 0 sobre lo agregado con `git add`; 0 CRLF en los dos
  archivos.
- **Revisión adversarial del informe** (un agente, solo lectura, con sus propias sondas y sin mirar capturas): el núcleo
  se sostiene (el corte por la fecha, el descarte de bajar y las dos condiciones del FRENA SI), y ningún dato real en el
  informe. Trajo 1 hallazgo alto, 5 medios y 9 bajos, todos corregidos en esta versión:
  - el alto: la corrida del 21-09 (pieza 4, 1);
  - los medios: los términos vistos en las capturas, el efecto de la opción b sobre MSC, el costo de la opción a, las
    sondas que imprimen textos y el cierre escrito antes de tiempo;
  - los bajos: filas de la tabla del OCR, tiempos, la espera inferida, el alcance leído, la sonda de la fila 10, la
    redacción del control, una cita no textual, el campo de fecha oculto y el `mk_f30_guarda.html` del 24-09.
