# CICLO · MAERSK elige la fecha de retiro, dice lo que el portal pide y busca los términos por su texto

**Módulo:** Agendamiento Reservas · **Encargo 36** · **Fecha:** 2026-09-28 · **Método:** skill `metodo-ciclo` v14 ·
**Commits** (locales; el repo no tiene remoto, así que no hay push que entregar): `3841c9f` (el motivo dice lo que el
portal pide), `5aed8ba` (la fecha de retiro), `44faaa9` (los términos por su texto) y `1ef2536` (lo que encontró la
revisión de código); y el de este informe, con `CLAUDE.md` al día.

**Base: `C:\dev\Agendamiento Reservas` @ `b59b40e` · árbol limpio** (pieza 9). Lo medido sale del HTML de «Additional
details» del 27-09 (`mk_f10_sin_objetivo.html`), del `log.txt` y las capturas de la corrida del 21-09 (la única que
llegó a la revisión) y de la documentación pública del Maersk Design System.

> Datos reales solo en lectura. Los HTML se abrieron en un Chromium sin red y sin el JavaScript de la página; las
> capturas se leyeron con OCR, sin mirarlas. En este informe no van nombres de naves, viajes, puertos, depósitos ni
> números de reserva.

**Resumen.**
- **La fecha de retiro.** MAERSK la elige con tu regla: el primer día hábil después del día en que se corre el
  programa, y si ese día no está habilitado, el siguiente habilitado. Usa los tres clics que permitiste: «Choose another
  date» (en el HTML guardado del 27-09, el único botón con ese nombre), el día del calendario por su fecha y el «Done»
  del calendario. Los avisos de cargos quedan en `log.txt` y la reserva sigue.
- **Tu FRENA SI no se cumplió al escribirlo, pero el calendario no está medido:** ninguna corrida guardó su HTML. El
  programa lo lee sin suponer su forma: un día cuenta solo si se sabe su fecha, por un atributo que la trae entera o por
  la leyenda de su mes. Si no puede identificar el día, o si hace falta cambiar de mes (otro clic), **no pulsa nada
  más**: NO ENVIADA, con el HTML del calendario guardado (`mk_f<fila>_calendario`) para medirlo. Tu FRENA SI queda a
  cargo del programa en la corrida.
- **Lo que el portal pide.** Cuando la revisión no aparece, el motivo empieza así: «Revisión de MAERSK: el portal pide:
  Pickup date («Pick up date cannot be left blank»). No encontré…». El lector de antes (`_mk_errores`) daba solo el
  encabezado del aviso, «Please correct the following errors».
- **Los términos, por su texto.** La casilla es la que dice «I have read and accept all the terms and conditions of
  this booking» (leído con OCR en las capturas del 21-09), ya no «el último checkbox»: cierra ese FRENO. Antes de
  marcarla guarda el HTML de la revisión (`mk_f<fila>_terminos`), que nunca se guardó. La marca con un clic de
  JavaScript en su `input`, que no está probado en el portal: el 21-09 la marcó un clic del mouse en su centro. Si no
  hay una sola casilla con ese texto, o si no queda marcada, corta sin pulsar nada más.
- **Una revisión de código** de los tres primeros commits (sin críticos ni altos) encontró cinco problemas medios, entre
  ellos que el clic en la casilla podía caer en el enlace de «terms and conditions» y que un «Done» ajeno al calendario
  se podía pulsar. Están corregidos en `1ef2536`.
- **Para decidir** (abajo, «Qué decides tú»): si un sábado o un domingo sirven como «el siguiente habilitado» (el 21-09
  habría sido el domingo 27), si permites el clic de cambiar de mes, y otras tres cosas.
- **Nada de esto se probó en el portal:** esa prueba la corres tú (abajo, «Cómo probarlo»).

## Veredicto del PASO 0, por parte del encargo

| Parte | Veredicto | Qué quedó |
|---|---|---|
| La fecha de retiro con tu regla, y tres clics | **CICLO** | `5aed8ba`, corregido en `1ef2536` |
| FRENA SI: el calendario no permite identificar el día por su fecha | **Sin medir:** ninguna corrida guardó el calendario. El programa frena solo si no puede | El corte y la evidencia `mk_f<fila>_calendario` |
| FRENA SI: elegir la fecha exige un clic distinto de esos tres | **No, al escribirlo.** Si en la corrida hiciera falta cambiar de mes, el programa frena | El corte, con el motivo |
| El motivo de la NO ENVIADA dice lo que el portal pide | **CICLO** | `3841c9f`, corregido en `1ef2536` |
| La casilla de términos por su texto | **CICLO** | `44faaa9`, corregido en `1ef2536` |
| `test_candado` no cambia | **Se cumple** | Sin cambios |

## Lo medido antes de escribir

**El HTML de «Additional details» del 27-09** (`mk_f10_sin_objetivo.html`, la pantalla donde cortó esa corrida):
- **«Choose another date»:** un `mc-button` con `label="Choose another date"` (`data-test`
  `haulageSettingsPickupDateButton-allContainer`), y en su raíz shadow un `button` con ese mismo `aria-label`. Por su
  rol y su nombre exacto: 1 botón, 1 a la vista en el HTML guardado, abierto sin el JavaScript de la página. «Click to
  choose date» no es un botón (0 por su rol): es un texto de la tarjeta.
- **La tarjeta de la fecha:** `section#containerPickupDatePicker` (`haulageSelectCard`), con «No date selected»
  (`haulage-invalid-date`). Al lado, un `input type="date"` vacío dentro de un `span.hidden-date-picker` con
  `aria-hidden`.
- **Los avisos de error:**
  - el resumen es un `mc-notification` `appearance="error"` con `heading="Please correct the following errors"`, y
    nombra el campo en un enlace de su pie (`slot="actions"`), fuera de su raíz shadow: «Pickup date», con
    `href="#containerPickupDatePicker"`;
  - el del campo es otro `mc-notification` de error, con `body="Pick up date cannot be left blank"`;
  - el lector de antes, `_mk_errores`, daba solo «Please correct the following errors».
- **El aviso de cargos:** un `mc-notification` `appearance="warning"` (`haulage-disclaimer`), «Additional charges can
  incur if the container is picked up from a different location than the origin or the date selected exceeds the
  agreed free time…». Ya está antes de elegir la fecha.
- **Ningún «Done» ni calendario:** el calendario no se abrió. Tampoco hay etiquetas de calendario o de fecha del Maersk
  Design System (`mc-calendar`, `mc-input-date`). Las `mc-*` del HTML son botones, íconos, avisos, pestañas, un
  `mc-modal`, la barra de pasos, dos `mc-textarea` (con su etiqueta, su error y su ayuda), el asistente «Ask Maersk» y
  los componentes de las partes y de sus direcciones.

**La corrida del 21-09** (la que se analizó en el encargo 35; su código elegía la fecha, hasta `0f1507e`):
- **`log.txt`:** en las 5 filas de MAERSK, «fecha de retiro seleccionada en modal (locator): día 27» y «pulsado 'Done'
  en modal de fecha de retiro». Ningún otro día.
- **Qué es ese 27:** el código de entonces pulsaba el primer elemento de la página, en su orden, que fuera un botón, una
  celda `gridcell`, algo con `role` button o un `mc-calendar-day`, con un número de 1 o 2 cifras como texto, y que se
  viera habilitado: a la vista, habilitado para Playwright, sin «disab» ni «inact» en su clase y sin `aria-disabled`.
  El 21-09 fue lunes, y el 27, domingo: del 22 al 26 no se veían habilitados. Es inferido del código de entonces, porque
  el calendario no se guardó.
- **Las capturas `_5c_details`, por OCR y sin mirarlas:** la tarjeta muestra el mes con su año («September 2026»), y ya
  no «No date selected». El número del día no se lee junto al mes: en 3 de las 5 no aparece ningún número de día.
- **La revisión** (encargo 35): las capturas `_6_review` muestran la casilla «I have read and accept all the terms and
  conditions of this booking», justo antes de «Submit booking». El `log.txt` trae 5 «términos y condiciones aceptados
  (mc click)»: un clic forzado del mouse en el centro del último `mc-checkbox`, sin comprobarlo después. Las 5 filas
  terminaron EMITIDA.

**El Maersk Design System, lo público:**
- El paquete de sus componentes no está publicado con el nombre que busqué: 404 en npm y en jsDelivr. La búsqueda de
  npm «maersk mds» trae 20 paquetes, ninguno de Maersk.
- Su sitio (`designsystem.maersk.com`) lista Calendar, Input Date, Date Range y Modal, pero con guías de diseño: sin el
  nombre de la etiqueta, sus atributos ni cómo arma los días. La página de desarrollo del calendario da 404.
- Lo único que usé: el calendario puede mostrar números de semana, así que el programa no los cuenta como días.

**Conclusión:** el calendario no está medido. El 21-09 no se guardaba el HTML, y del 24-09 al encargo 36 el calendario
no se abría. Por eso el programa lo lee sin suponer su forma, y deja su HTML en la primera corrida.

## Cómo elige la fecha de retiro

En «Additional details», antes de la referencia de retiro, `_mk_fecha_de_retiro` hace esto:
1. **El día que toca** (`_mk_dia_de_retiro`): el primer día hábil después de hoy. De lunes a jueves, el día siguiente;
   el viernes, el sábado o el domingo, el lunes. Los feriados no se saltan: tu regla es de lunes a viernes. Lo anota.
2. **Clic 1, «Choose another date»:** espera hasta 10 s un solo botón a la vista con ese nombre exacto
   (`_mk_boton_unico`). Si antes de abrir ya hay un «Done» a la vista, no abre: no sabría cuál es el del calendario.
3. **El calendario:** espera hasta 10 s el único «Done» a la vista que tenga alrededor al menos 28 días. Anota cuántos
   días leyó, cuántos con su fecha y cuántos habilitados, entre qué fechas y cómo los identificó. Deja la evidencia
   `mk_f<fila>_calendario`: la captura de la ventana y el HTML con sus raíces shadow, sin clics.
4. **Qué día** (`_mk_elegir_dia_de_retiro`): el que toca, si está habilitado; si no, el siguiente habilitado, y lo
   anota con su día de la semana. El que toca tiene que estar a la vista, y cada día desde él hasta el elegido,
   identificado por su fecha. Si no, no elige: cambiar de mes sería otro clic.
5. **Clic 2, el día:** vuelve a leer el calendario y pulsa el botón de esa fecha solo si está en una sola celda
   habilitada.
6. **Clic 3, «Done»:** vuelve a leer el calendario y pulsa su propio «Done». Si el calendario se cerró solo al elegir
   el día, no pulsa nada y lo anota.
7. **Los avisos de cargos:** después del día y después del «Done», anota cada aviso a la vista que hable de cargos
   (charge, fee, cost, free time, demurrage, detention), una sola vez, y dice si ya estaba antes de elegir la fecha. La
   reserva sigue.
8. **La tarjeta** (`_mk_comprobar_retiro`): la lee hasta 5 s mientras siga sin fecha. Si muestra la elegida, lo anota.

**Cómo sabe la fecha de un día**, sin el calendario medido (`_JS_MK_DIAS`):
- Un día es algo que se puede pulsar (un botón, una celda, un enlace, algo con `role` gridcell…) cuyo texto entero es
  un número del 1 al 31. Los números de semana no cuentan.
- Su fecha sale de un atributo que la traiga entera (`aria-label` «Tuesday, 29 September 2026», `title`, `data-date`…)
  con ese mismo número, o de la única leyenda del mes de su bloque («September 2026»).
- Los días marcados como de otro mes no toman la leyenda, y una fecha que queda en dos celdas vale solo en la de su
  propio mes.
- Un día está deshabilitado si trae `disabled`, `aria-disabled="true"`, o una clase o un `part` con disab, inact,
  unavailable, out-of-range, not-allowed o blocked.
- Lo que no se identifica así no se pulsa.

**Los cortes.** Todos son NO ENVIADA, sin otro clic, y el motivo va a la pantalla, a `log.txt` y a la planilla:

| Dónde | Motivo (resumido) | Evidencia |
|---|---|---|
| No hay un solo «Choose another date» a la vista en 10 s, o ya hay un «Done» | «Fecha de retiro de MAERSK: no encontré un solo botón «Choose another date» a la vista y ningún «Done» antes de abrir el calendario (había N y M), así que no pulsé nada…» | `mk_f<fila>_sin_objetivo` |
| Falla el clic en «Choose another date» | «MAERSK: falló el clic en «Choose another date» (…)» | **ninguna** (residual) |
| El calendario no aparece | «…pulsé «Choose another date», pero no apareció el calendario en 10 s (ningún «Done» a la vista)»; o «había N «Done» a la vista, y no sé cuál es el del calendario»; o «junto al «Done» a la vista no hay un calendario de al menos 28 días» | `mk_f<fila>_calendario` |
| El día no se puede elegir por su fecha | «…abrí el calendario de la fecha de retiro, pero» «no pude identificar por su fecha ningún día del calendario»; o «el día que toca, el DD-MM-AAAA, no está a la vista: el calendario muestra del … al …, y cambiar de mes es un clic que no está permitido»; o «no pude identificar por su fecha el …»; o «no hay un día habilitado del … al …» | `mk_f<fila>_calendario` |
| Al volver a leerlo, el día ya no es uno solo habilitado | «…al volver a leer el calendario, el … ya no estaba habilitado o no era uno solo» | `mk_f<fila>_calendario` |
| Falla el clic en el día o en «Done» | «…falló el clic en el … del calendario (…)»; o «…elegí el …, pero falló el clic en «Done» (…)» | `mk_f<fila>_calendario` |
| Después del día hay un «Done» que no es del calendario | «…elegí el …, pero había N «Done» a la vista y ninguno es el del calendario» | `mk_f<fila>_calendario` |
| La tarjeta sigue sin fecha | «…elegí el … en el calendario, pero la tarjeta sigue sin fecha de retiro y el portal pide: …» | `mk_f<fila>_retiro` |
| La tarjeta, o el campo oculto, muestran otra fecha | «…elegí el … en el calendario, pero el portal quedó con el …» | `mk_f<fila>_retiro` |

Uno no corta: si la tarjeta no se puede leer, el programa avisa «⚠ MAERSK: no pude leer qué fecha de retiro muestra la
tarjeta; sigo, y la guarda deja su evidencia» (pregunta 5).

## Lo que el portal pide

`_mk_lo_que_pide` lee los avisos de error a la vista, también dentro de las raíces shadow:
- los campos: los enlaces a una parte de la página («#…») y los ítems de lista que hay dentro del aviso;
- sus mensajes: su atributo `body`; su texto, solo si no trae campos;
- y los campos marcados con el atributo `invalid`: su `legend`, su `label` o su `name`, y su `errormessage`.
  `_mk_errores` leía el `legend` o el `name` de los `[invalid="true"]`; el `label` y el `errormessage` son nuevos. Esta
  forma no está medida.

Se usa en tres lugares:
1. **Si la revisión no aparece** (`_mk_esperar_revision`), el motivo empieza por eso. Con la pantalla del 27-09:
   «Revisión de MAERSK: el portal pide: Pickup date («Pick up date cannot be left blank»). No encontré la pantalla de
   revisión («Review booking»), que no apareció en 15 s, así que no pulsé nada. La reserva no se envió; revisa ese paso
   en el portal.»
2. **Si la tarjeta sigue sin fecha** después de elegirla (en la tabla de arriba).
3. **Si «Booking Information» no avanza:** sigue en REVISAR, como antes, con «MAERSK: el portal no dejó avanzar y
   pide: …», o «…el portal no dejó avanzar, y no pude leer qué pide» (pregunta 4).

Sobre lo guardado (`programa_real.py`, con el JavaScript del programa como quedó en `1ef2536`): en «Additional details»
del 27-09 da exactamente «Pickup date» y «Pick up date cannot be left blank». En las otras 7 páginas de MAERSK, que son
de «Select sailing», no da nada.

Es solo de MAERSK: en las demás navieras los motivos no cambian (residual).

## Los términos, por su texto

`_mk_marcar_terminos`, en la revisión:
1. Baja al final de la página, que no es un clic. Espera hasta 10 s una sola casilla a la vista cuyo texto entero sea
   «I have read and accept all the terms and conditions of this booking».
   - Una casilla es un `mc-checkbox`, un `input` checkbox o algo con `role` checkbox.
   - Su texto es su `label`, su `aria-label`, lo que dice adentro o la etiqueta que la contiene. No distingue
     mayúsculas, espacios de más ni un punto final.
2. Deja la evidencia `mk_f<fila>_terminos`: el HTML de la revisión, que nunca se guardó.
3. Si ya está marcada, no la pulsa. Si no se puede leer si está marcada, tampoco, y corta.
4. Si está sin marcar, vuelve a buscarla y pulsa su `input` con un clic de JavaScript (`input.click()` dentro de la
   página), no con el mouse en el centro del `mc-checkbox`, donde puede estar el enlace de «terms and conditions». El
   21-09 la marcó justamente un clic forzado del mouse en ese centro, y funcionó en las 5. El de ahora no está probado
   en el portal: si no la marca, la comprobación lo detecta y corta.
5. Comprueba tres cosas: la misma dirección, una sola casilla y que quedó marcada.

Así se cierra el FRENO de «el último checkbox» (`CICLO-clics-a-ciegas.md`): la foto de `test_clics` pierde las formas
genéricas de MAERSK de los términos (`casilla-por-tipo`, `rol-sin-nombre` y las 5 de `ultimo-por-posicion`). A MAERSK
le quedan dos, y son una misma línea: la referencia de retiro, que va en «el primer textarea». En el HTML del 27-09 ese
primero es el campo oculto del asistente «Ask Maersk», y la referencia llega a su campo por el respaldo, su etiqueta
(`textarea_real.py`; residual).

| Dónde | Motivo (resumido) | Evidencia |
|---|---|---|
| No hay una sola casilla con ese texto en 10 s | «Términos de MAERSK: no encontré una sola casilla «I have read…» (había N), así que no pulsé nada…» | `mk_f<fila>_sin_objetivo` |
| No se puede leer si está marcada | «…no pude leer si la casilla «…» estaba marcada, así que no la pulsé» | `mk_f<fila>_terminos` |
| Falla el clic | «…falló el clic en la casilla «…» (…)» | `mk_f<fila>_terminos` |
| Al volver a buscarla, ya no es una sola sin marcar | «…ya no era una sola sin marcar» | `mk_f<fila>_terminos` |
| Después del clic, la página cambió | «…después del clic en la casilla «…», la página cambió» | `mk_f<fila>_terminos` |
| No quedó marcada, o no se pudo comprobar | «…pulsé la casilla «…», pero no quedó marcada»; o «no pude comprobar que quedó marcada» | `mk_f<fila>_terminos` |

Todos son NO ENVIADA, antes de la guarda. El texto de la casilla sale del OCR de las capturas del 21-09: su HTML sigue
sin medir, y ni el clic en su `input` ni la comprobación se probaron en el portal.

## La revisión de código

Un agente revisó los tres primeros commits, en solo lectura y con páginas sintéticas (Node y un Chromium sin red). Dio
**0 críticos, 0 altos, 5 medios y 8 bajos**. Reprodujo M1, M2, M4, M5, L1, L2 y L3 con páginas sintéticas; los demás
salen de leer el código, y L6, de un caso supuesto. Confirmó que no hay clics nuevos después de la guarda, que
`test_candado` no cambió, que la regla da el lunes desde el viernes, el sábado y el domingo, y que el día se pulsa solo
si se sabe su fecha.

Los medios, corregidos en `1ef2536`:
- **M1.** El clic en la casilla iba al centro del `mc-checkbox`. Con el enlace «terms and conditions» en su texto, la
  página lo seguía y la casilla quedaba sin marcar. Ahora se pulsa su `input`, con un clic de JavaScript.
- **M2.** Después del clic, un estado ilegible contaba como marcada, aunque la página hubiera cambiado. Ahora pide una
  sola casilla, marcada y en la misma dirección. Y si antes del clic no se sabe si está marcada, no la pulsa.
- **M3.** Si los términos fallaban, no quedaba evidencia de la revisión. Ahora deja `mk_f<fila>_terminos` antes del
  clic.
- **M4.** Se podía pulsar un «Done» ajeno al calendario. Ahora el calendario se reconoce por su «Done» con 28 días y se
  pulsa ese; con un «Done» ya en la página, no se abre el calendario.
- **M5.** El filtro de números de semana (`/week/`) también sacaba los días con «weekend» en su clase. Un mes quedaba
  con menos de 28 y no se reconocía ningún calendario. Ahora es `/week(?!end)/`.

Los bajos: 3 corregidos y 5 en parte.
- **Corregidos:**
  - L1: el botón se espera hasta 10 s;
  - L3: con dos meses a la vista, la fecha repetida queda en la celda de su mes;
  - L5: el motivo dice por qué no encontró el calendario.
- **En parte:**
  - L2: «a la vista» excluye `visibility:hidden` y cuenta un anfitrión sin cajas propias, pero un mes recortado fuera de
    la ventana sigue contando;
  - L4: la tarjeta se espera hasta 5 s, y la fecha elegida puede venir junto a otras; si no se puede leer, sigue;
  - L6: un enlace a otra página ya no cuenta como campo, y el `body` del aviso se lee aunque haya campos; pero los ítems
    de lista siguen contando como campos, y si hay campos, un mensaje que no está en el `body` se pierde;
  - L7: «discharge» ya no cuenta como cargo, pero un aviso que llega más de 1 s después del «Done» no se anota;
  - L8: la espera del calendario y la búsqueda del «Done» después del día ya están protegidas; la búsqueda de «Choose
    another date» y la cuenta de «Done» antes de abrir, no: una falla ahí termina en ERROR y no en NO ENVIADA. Y
    `_mk_boton_unico` vuelve a buscar el botón al pulsarlo. Todo eso pasa antes de la guarda: nada se envía.

También señaló pruebas que no cazarían una regresión. Las de M2, M4 y M5 ya las cazan, y el DOM falso de las pruebas
ya sabe de elementos ocultos. Dos siguen mirando la forma del código sin correrlo (residual).

## Cómo probarlo

Con **`Iniciar AQUASHIELD.bat`**; nunca con `Iniciar AQUASHIELD_EMISION.bat`. Antes, revisa que el candado esté
cerrado por sus otras dos llaves: que `config.json` no traiga `"emitir_reservas": true` en «opciones» y que no esté
definida la variable `AQUASHIELD_EMITIR=1`. Con cualquiera de las tres, se emite. Después corre una o más filas de
MAERSK con su nave: la reserva se detiene antes de «Submit booking».

En `log.txt`, en «Additional details», tiene que aparecer esto, en orden:
1. «Fecha de retiro: el primer día hábil después de hoy es el DD-MM-AAAA (día).»
2. «pulsado 'Choose another date'»
3. «calendario de la fecha de retiro: N días, M con su fecha y K de ellos habilitados, del … al … (…)»
4. «evidencia con el calendario de la fecha de retiro: mk_f<fila>_calendario.png y … HTML …»
5. Solo si el día que toca no está habilitado: «Fecha de retiro: el … no está habilitado en el calendario: elijo el
   siguiente habilitado, el … (día).»
6. «elegido en el calendario: DD-MM-AAAA (día)»
7. «aviso de MAERSK sobre la fecha de retiro (ya estaba antes de elegirla): «Additional charges can incur…»»
8. «pulsado 'Done'»
9. «la tarjeta muestra la fecha de retiro elegida, el DD-MM-AAAA»

Y en la revisión:
1. «evidencia con la casilla de los términos: mk_f<fila>_terminos.png y … HTML …»
2. «marcado: términos y condiciones aceptados, la casilla por su texto», o «la casilla de los términos ya estaba
   marcada: no la pulsé».
3. La evidencia `mk_f<fila>_guarda` y «Me DETENGO en Review booking antes de emitir (NO se pulsa Submit booking).» La
   fila queda «lista para emitir», con `retiro=DD-MM-AAAA` en el detalle.

Si corta, el motivo dice dónde y por qué. Si corta con «pulsé la casilla …, pero no quedó marcada», es el clic de
JavaScript, que el portal no tomó. En cualquier caso, dime qué corrida fue: leo su `log.txt` y los HTML de
`mk_f<fila>_calendario`, `_retiro`, `_terminos` y `_guarda` en `logs/`, sin sacarlos de ahí. Con el del calendario se
mide lo que hoy el programa lee sin conocer.

## Qué decides tú

1. **La prueba** (arriba). Es lo único que dice si el calendario se deja leer.
2. **¿Un sábado o un domingo sirven como «el siguiente habilitado»?** Lo dejé como lo escribiste. El 21-09 (lunes), con
   tu regla tocaba el martes 22; según el `log.txt` y el código de entonces, el primer día habilitado era el domingo 27,
   y el programa habría elegido ese domingo (inferido). Si el depósito no atiende los fines de semana, el siguiente
   habilitado también puede ser de lunes a viernes: ese día habría sido el 28 o uno posterior, porque no se sabe si el
   28 estaba habilitado. Tampoco se saltan los feriados.
3. **¿Permites el clic de cambiar de mes?** Hoy, si el día que toca, o el siguiente habilitado, está en un mes que el
   calendario no muestra, corta (NO ENVIADA). Puede pasar a fin de mes. Recomiendo decidirlo con el HTML del calendario
   de la prueba: hoy no se sabe cómo es ese botón.
4. **«Booking Information» que no avanza: ¿REVISAR o NO ENVIADA?** Quedó en REVISAR, como antes, y ahora con lo que el
   portal pide. Los cortes nuevos de este encargo (la fecha de retiro, la revisión y los términos) son NO ENVIADA, pero
   MAERSK tiene otros REVISAR antes de la guarda: el formulario que no abre o queda incompleto, la búsqueda de salidas
   que no termina y la nave que no está.
5. **La tarjeta que no se puede leer: ¿sigue o corta?** Hoy sigue, con el aviso ⚠. Su forma con una fecha no está
   medida, y cortar podría frenar todas las filas si el lector falla con la tarjeta real. Con el candado abierto, la
   reserva se enviaría sin haber comprobado la fecha en la tarjeta; la revisión la muestra, y la guarda deja su
   evidencia.
6. **¿Borro las 28 carpetas de censos cortados que quedaron en `%TEMP%`?** Son 2,78 GB de copias del programa y de las
   pruebas, sin datos reales (pieza 4).

## Re-medir (pieza 1)

Las sondas son de solo lectura y no se versionan, porque leen datos reales. Quedaron en el scratchpad de esta sesión
(`$env:TEMP\claude\<proyecto>\<sesión>\scratchpad\e36`), que puede limpiarse; sin ellas, estos números no se re-miden.
Todas abortan si no pasa su control positivo, salvo las que solo cuentan o extraen: `mds_lista.py`,
`red_por_commit.py`, `salidas.py`, `ritmo.py`, `js_del_programa.py` y `temp_mut.py`.
- **`sonda.py <archivo.js> <html>…`** (la del encargo 35): corre un JavaScript sobre un HTML guardado, sin red y sin los
  `<script>` de la página. Su control: un `mc-checkbox` sintético con su `input` en una raíz shadow declarativa.
  - `arbol_retiro.js`: el árbol de la sección de la fecha de retiro, con sus raíces shadow; de los textos, solo los de
    la interfaz.
  - `tarjeta_deposito.js`: las tarjetas `haulageSelectCard`, con los textos tapados.
- **`errores.py`:** los avisos de error, lo que daba `_mk_errores` y cuántos botones hay con cada nombre. Su control: un
  aviso sintético con su enlace. Saca `_mk_errores` de `AQUASHIELD.py`, y desde `3841c9f` ya no está ahí: para
  re-medirlo, apúntalo a la versión de `b59b40e` (`git show b59b40e:AQUASHIELD.py`).
- **`ocr_tarjeta21.py` y `ocr_fecha21.py`:** la tarjeta de la fecha en las capturas `_5c_details` del 21-09, tapada
  (cifras → 9; de las palabras, solo meses, días de la semana y textos de la interfaz). Sus controles: una imagen
  sintética con una fecha, y que cada captura traiga «Pick-up date» (en `ocr_tarjeta21.py`, que el OCR lea al menos 100
  palabras).
- **`programa_real.py`:** el JavaScript de MAERSK del programa, sacado de `AQUASHIELD.py` sin importarlo, sobre las 8
  páginas de MAERSK de `logs/`. Su control: una página sintética con la forma medida.
- **`textarea_real.py`:** qué textarea toma el localizador de la referencia de retiro en el HTML del 27-09, y qué da su
  respaldo por la etiqueta. Su control: una página sintética con un textarea oculto antes del de la referencia.
- **`npm_consulta.py`:** el paquete del Maersk Design System en npm y la búsqueda «maersk mds». Su control: un paquete
  público conocido. `mds_lista.py` hace lo mismo en jsDelivr, sin control. En el sitio del Maersk Design System se
  leyeron a mano 4 páginas.
- **`js_del_programa.py`:** saca los `_JS_MK_*` del programa, para los arneses de Node de `js/`.
- **`red_por_commit.py <rev>…`:** pruebas, mutaciones y pares de cada commit, con `git show`.
- **`salidas.py`:** saca del registro de la sesión lo que imprimieron las sondas. Solo sirve en esta sesión.
- **`ritmo.py`:** cuántas copias preparó el censo en un minuto, y cuánto tarda copiar y compilar el programa una vez.
- **`temp_mut.py [carpeta a dejar fuera]`:** las carpetas `aquashield_mut_*` de `%TEMP%`, con sus archivos y bytes.
- **Las esperas de la máquina:** en PowerShell, `Get-WinEvent -FilterHashtable @{LogName='System'; Id=506,507;
  StartTime=(Get-Date '2026-09-28 16:00')}` (506, entra en espera moderna; 507, sale).
- **Los gates:** `gate.sh <etiqueta> <clase>…` (la suite y los censos filtrados), `censo.sh` (el completo) y `commit.sh`
  (la sonda de secretos, el `git add`, la sonda sobre lo agregado y el commit).

En PowerShell, desde `C:\dev\Agendamiento Reservas`: `$env:PYTHONIOENCODING='utf-8'` y después
`python "<scratchpad>\e36\<sonda>.py" …`. La red versionada:
- `python tests/correr.py`: la suite, de 4 a 6 min (la de 13 min incluyó 7 min de la máquina en espera);
- `python tests/correr.py --mutaciones --filtro TestRetiroMaersk`: el censo de una clase (también `TestTerminosMaersk`,
  `TestMaersk`, `TestSinClicACiegas`, `TestCadaReservadorLaDeja` y `TestFotoDeClicsGenericos`);
- `python tests/correr.py --mutaciones`: el censo completo.

## NO retroceder (pieza 2)

- **No vuelvas a «el primer día habilitado» sin mirar su fecha:** es un clic por posición, y tu regla es otra.
- **No agregues clics en el calendario sin tu decisión:** ni cambiar de mes, ni «Today», ni escribir en el campo de
  fecha oculto. Solo «Choose another date», el día por su fecha y su «Done»: es el FRENA SI.
- **No pulses un «Done» que no sea el del calendario,** ni abras el calendario con otro «Done» a la vista (M4).
- **No quites las evidencias `mk_f<fila>_calendario` ni `mk_f<fila>_terminos`:** son la única forma de medir el
  calendario y la revisión (M3).
- **No vuelvas al clic en el centro del `mc-checkbox` sin el HTML de la revisión:** el 21-09 funcionó, pero si el
  enlace de «terms and conditions» queda en ese centro, el clic lo sigue (M1).
- **No des la casilla por marcada sin leerla después del clic** (M2).
- **No leas lo que pide el portal en el texto alrededor del resumen:** el enlace del campo está fuera de su raíz shadow,
  y así se leía solo el encabezado.
- **No uses `/week/` para los números de semana:** también saca los días de fin de semana (M5).

## Universo y cobertura (pieza 3)

- **HTML de MAERSK en `logs/`:** 8 páginas (83 archivos con sus marcos), del 24 al 27-09: 8 abiertas, 0 fallidas.
  - 1 es «Additional details» (27-09) y 7 son de «Select sailing».
  - Ninguna es el calendario ni la revisión.
  - Los marcos no se abrieron: el programa corre ese JavaScript en la página.
- **La corrida del 21-09:** el tramo de MAERSK de su `log.txt` (5 filas), y sus 5 capturas `_5c_details` por OCR,
  ninguna mirada. Las 5 `_6_review` se leyeron en el encargo 35.
- **El Maersk Design System:** npm, jsDelivr y la búsqueda de npm; en su sitio, la lista de componentes, Calendar, su
  página de desarrollo (404) e Input Date.
- **La revisión de código:** `3841c9f`, `5aed8ba` y `44faaa9`.
- **No medido:**
  - el HTML del calendario, el de la tarjeta con una fecha (del 21-09 hay solo OCR) y el de la revisión;
  - que «Choose another date» se vea en la página real: el «1 a la vista» sale del HTML guardado, abierto sin el
    JavaScript de la página, y el OCR de las capturas del 27-09 no lo leyó (el encargo 35 lo atribuyó, sin medirlo, a
    que es un texto sobre un botón de color);
  - qué días habilita el portal y si deja un sábado o un domingo: lo del 21-09 es inferido del código de entonces;
  - si el portal toma el clic de JavaScript en el `input` de la casilla;
  - cuánto tardan en aparecer el calendario y la casilla (`MK_ESPERA_CALENDARIO` y `MK_ESPERA_TERMINOS`, 10 s cada una,
    hipótesis);
  - los cargos de la fecha elegida.

## Defectos de instrumento cazados (pieza 4)

1. **`mds_lista.py` buscaba el paquete del Maersk Design System con un nombre que no está publicado:** dio 404, y la
   búsqueda de npm no trajo otro. Su sitio público no trae la API. Por eso el lector del calendario no se apoya en
   documentación.
2. **`js_del_programa.py` daba NameError:** los `_JS_MK_*` se arman con otros `_JS_`. Pasó a sacarlos todos, en orden.
3. **El control de `ocr_fecha21.py` abortó:** el recorte cortaba el día de la semana de la línea sintética. Se agrandó,
   y el control pasó.
4. **En el gate del segundo commit, dos mutaciones nombraban pruebas que no podían tumbar.** El censo dio NO MUERDE:
   - `maersk-espera-sin-cortar` → `test_cada_reservador_que_corta_esta_decorado`;
   - `mk-boton-unico-el-primero` → `test_done_despues_del_dia` y `test_amplia_hasta_que_el_portal_no_deja_mas`.

   Se corrigió su lista de pruebas y los dos censos se volvieron a correr: OK.
5. **En el gate del cuarto commit, `mk-dias-semana-con-finde` no mordió.** El día de fin de semana de la prueba tenía su
   número en un botón de adentro, que igual contaba como celda. La prueba pasó a celdas con el número directo, y mordió.
6. **La foto de clics cazó dos formas mías,** `|| unicos[0]` y `|| cs[0]`. Eran únicas por construcción, pero es la
   forma que la foto prohíbe, y se reescribieron.
7. **Dos errores de mis pruebas, al escribirlas:** un filtro corrido en uno (`i > 30` en un mes de 31) y una aserción
   que dependía de las comillas de `ast.unparse`. Fallaron en la primera corrida y se corrigieron antes del gate.
8. **Edité `tests/test_clics.py` mientras corría un censo del gate del cuarto commit.** Paré el gate. `TaskStop` dejó
   vivos procesos hijos, que cerré por su PID, y volví a correr el gate entero.
9. **El censo completo sobre `44faaa9` empezó antes de que llegara la revisión de código,** y lo paré cuando la revisión
   trajo cambios: habría medido un commit que iba a cambiar.
10. **La sesión se cerró mientras corría el último censo del gate del cuarto commit.** Comprobé que no quedaba ningún
    proceso y que los 4 archivos eran anteriores al inicio del gate, y volví a correr ese censo solo: OK. El corte
    coincide con una espera de la máquina (17:27 a 17:31); la causa no la medí.
11. **`salidas.py`, en su primera búsqueda, sin filtrar por encargo, volvió a imprimir en mi consola salidas de encargos
    anteriores:** el nombre de un depósito y rutas de carpetas con el nombre del operador, que ya se habían impreso
    entonces. No están en ningún archivo del repo ni en este informe. Las búsquedas siguientes filtran por el encargo
    36.
12. **La máquina entró en espera moderna mientras corrían los gates** (el registro System, eventos 506 y 507):
    - de 16:54 a 17:01, en la suite del gate del cuarto commit, que por eso tardó 761 s y no unos 250;
    - de 17:55 a 19:37, en dos tramos, mientras el censo completo preparaba sus copias: estuvo detenido 1 h 42 min, y la
      primera revisión adversarial de este informe se trabó y se volvió a lanzar. Al volver, el censo preparó 68 copias
      en el minuto que lo medí.
13. **Las corridas cortadas de `correr.py` dejan su carpeta de trabajo en `%TEMP%`:** la crea al empezar y la borra en
    un `finally`, que no corre si el proceso se mata. Hay 28 carpetas `aquashield_mut_*` de corridas anteriores (17
    vacías), con 15 744 archivos y 2,78 GB: copias del programa y de las pruebas, sin datos reales. No las borré
    (pregunta 6).
14. **El mensaje de `1ef2536` dice que la revisión trajo hallazgos «reproducidos en páginas sintéticas»:** de los 13,
    lo fueron 7. No reescribí el commit; lo corrige este informe.
15. **La primera versión de este informe afirmaba de más en 6 puntos** (pieza 8): «cada uno reproducido», L6 y L8, la
    evidencia de un clic fallido, «los demás cortes son NO ENVIADA» y el lunes 28 del 21-09. Los cazó la revisión
    adversarial.

## Premisas del encargo contrastadas (pieza 5)

- **«El portal exige «Pick up date» y rechaza «Review booking» sin ella; por defecto no trae fecha elegida»:**
  confirmado en el HTML del 27-09. El JavaScript nuevo lo lee así.
- **«El 21-09, el programa elegía el primer día habilitado y las 5 filas llegaron a la revisión»:** confirmado.
  `log.txt` trae «día 27» y «Done» en las 5 filas, y la revisión consta en sus 5 capturas `_6_review` y en 5 «términos y
  condiciones aceptados (mc click)»; las 5 terminaron EMITIDA. Hay algo más: ese primer día habilitado fue un domingo, y
  del 22 al 26 no se veían habilitados (inferido).
- **«Los clics permitidos son «Choose another date», el día por su fecha y «Done»»:** «Choose another date» es un solo
  botón en el HTML guardado. «Click to choose date», que el encargo 35 nombraba como otra forma de abrir el calendario,
  no es un botón: es un texto de la tarjeta, y no se pulsa.
- **FRENA SI «el calendario no permite identificar el día por su fecha»:** no se pudo contrastar, porque el calendario
  no está guardado. Queda a cargo del programa en la corrida.
- **FRENA SI «elegir la fecha exige un clic distinto de esos tres»:** con lo que se sabe, no. Cambiar de mes sería uno,
  y ahí el programa frena.
- **De mi propio diseño, refutado por la revisión:**
  - que el centro del `mc-checkbox` fuera la casilla (M1);
  - que un estado ilegible después del clic pudiera contar como marcada (M2);
  - que el único «Done» a la vista fuera el del calendario (M4);
  - que «week» en una clase marcara un número de semana (M5).
- **«test_candado no cambia»:** se cumple.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| El calendario se lee sin medirlo | Ninguna corrida guardó su HTML | …la prueba deja `mk_f<fila>_calendario.html` |
| Cambiar de mes no está permitido: si el día no está a la vista, NO ENVIADA | Sería un clic fuera de los tres | …lo permites (pregunta 3) |
| «El siguiente habilitado» puede ser sábado o domingo, y un feriado cuenta como hábil | Así está escrita la regla | …decides otra cosa (pregunta 2) |
| La revisión no está medida: el texto de la casilla sale del OCR del 21-09 | Desde el 24-09 ninguna corrida llega a la revisión | …la prueba deja `mk_f<fila>_terminos.html` |
| La casilla se marca con un clic de JavaScript en su `input`, sin probar en el portal; el 21-09 funcionó el clic del mouse en su centro | Lo pidió la revisión (M1); si no la marca, corta | …la prueba corta con «no quedó marcada» |
| «Choose another date» a la vista en la página real, sin medir | El OCR del 27-09 no lo leyó; el HTML guardado sí lo trae | …la prueba lo pulsa, o corta ahí |
| Si falla el clic en «Choose another date», no queda evidencia | La del calendario se deja después de ese clic | …pasa en una corrida |
| La tarjeta que no se puede leer sigue, con ⚠ (L4) | Su forma con una fecha no está medida | …decides que corte (pregunta 5), o se mide |
| «Booking Information» que no avanza queda REVISAR | El encargo pedía el motivo, no el estado | …lo decides (pregunta 4) |
| Lo que el portal pide: solo en MAERSK; los ítems de lista cuentan como campos, y sin `body` el mensaje se pierde si hay campos (L6) | El encargo es de MAERSK, y esas formas no están medidas | …otra naviera lo necesita, o una pantalla lo muestra |
| Un mes recortado fuera de la ventana cuenta como a la vista (L2) | `checkVisibility` no mira el recorte | …el HTML del calendario lo muestra |
| Un aviso de cargos que llega más de 1 s después del «Done» no se anota (L7) | Se lee 0,5 s después del día y 1 s después del «Done» | …la prueba lo muestra |
| La búsqueda de «Choose another date» y la cuenta de «Done» antes de abrir no están protegidas: una falla termina en ERROR (L8) | Es el camino general de los errores, antes de la guarda | …se decide tratarlo |
| Dos pruebas miran la forma del código sin correrlo: la rama de «Booking Information» y el lugar de la fecha | Correr esa rama pide una página falsa de todo el asistente | …esa rama cambia |
| La referencia de retiro toma «el primer textarea»: en el HTML del 27-09 es el campo oculto del asistente «Ask Maersk», y la referencia llega por su etiqueta. Con el asistente abierto, iría al asistente | Es de antes y está fuera del encargo | …la tarea aparte lo mide (te la propongo) |
| El Shipper, si AQUACHILE no viene asignado, pulsa el último elemento con ese texto (`loc_aqua.last`), y la foto no lo ve: su expresión busca `).last` | Es de antes y está fuera del encargo | …la misma tarea aparte |
| `MK_ESPERA_CALENDARIO` y `MK_ESPERA_TERMINOS` (10 s) son hipótesis | Sin medir | …la prueba muestra otra cosa |
| La prueba del puerto del panel es intermitente | Tarea aparte del encargo 35 | …esa tarea mide la causa |
| 28 carpetas de corridas cortadas en `%TEMP%` (2,78 GB) | `correr.py` las borra en un `finally` que no corre si se mata el proceso | …me dices que las borre (pregunta 6) |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v14**.
- **PASO 0 con sus cuatro valores:** CICLO en las tres partes. El FRENA SI no se podía medir antes: queda a cargo del
  programa, que frena en la corrida.
- **FRENAR cuando la decisión es de negocio:** los fines de semana, los feriados, cambiar de mes y dos estados quedan
  como preguntas. No elegí por ti.
- **Control positivo que aborta:** en cada sonda que mide, salvo las seis que solo cuentan o extraen (pieza 1).
- **Todo salto silencioso lleva contador:** 8 páginas, 8 abiertas, 0 fallidas.
- **El negativo tiene que morder:** cada prueba nueva con su mutación, el censo filtrado en cada commit y el completo en
  el último. Tres mutaciones no mordían: se corrigió la lista de pruebas de dos y la prueba de la otra (pieza 4).
- **Un gate en cero prueba contención, no correctitud:** la red dice que el programa hace lo que se escribió. Si el
  portal lo acepta, lo dice la prueba.
- **Todo registro es una hipótesis:** «el primer día habilitado» del 21-09 se leyó en su `log.txt` y en el código de
  entonces, y resultó un domingo. Y el mensaje de mi propio commit decía de más (pieza 4, 14).
- **Re-medir contra HEAD:** el código se leyó en `b59b40e` antes de cambiarlo, y `errores.py` corrió con esa versión; el
  JavaScript nuevo se corrió sobre lo guardado con la de `1ef2536`.
- **Fuente única:**
  - un solo recorrido de la página (`_JS_MK_RECORRER`) y un solo lector de fechas (`_JS_MK_FECHAS`);
  - un solo lector del calendario (`mkCalendario`), que usan la lectura, el día y el «Done»;
  - un solo buscador de botones (`_mk_boton_unico`).
- **Cada reemplazo, exactamente una vez, y el EOL preservado:** ediciones con anclas únicas; 0 CR en cada commit.
- **El cambio y su guardián, juntos:** cada commit con sus pruebas y sus mutaciones.
- **Declarar las premisas refutadas y el residual:** piezas 5 y 6.
- **Choques entre reglas:**
  1. **«El día identificado por su fecha» contra un calendario sin medir:** el programa lo identifica sin suponer su
     forma, y si no puede, frena. El FRENA SI pasa a la corrida.
  2. **«Si no está habilitado, el siguiente habilitado» contra «ningún clic fuera de esos tres»:** si el siguiente está
     en otro mes, frena.
  3. **«`test_candado` no cambia» contra la foto de `test_clics`, que cambió:** son dos pruebas distintas.
     `test_candado` no cambió; la foto perdió las formas genéricas de los términos, que es lo que el encargo pedía.
  4. **«La casilla por su texto» contra su HTML sin medir:** el texto sale del OCR del 21-09; si en el portal no calza,
     corta sin pulsar.
  5. **El clic que funcionó el 21-09 contra el hallazgo M1:** el clic del mouse en el centro del `mc-checkbox` marcó la
     casilla en las 5, pero en una página sintética caía en el enlace. Elegí el clic de JavaScript en su `input`, que
     falla cerrado: si no la marca, corta. La prueba dirá si el portal lo toma.

Reglas del módulo: nada de `logs/` en el repo; ningún nombre de nave, viaje, puerto, depósito ni operador, ni número de
reserva, en este informe; `test_candado` sin cambios; la sonda de secretos antes de cada commit; los textos en español
con tuteo.

## Entregable (pieza 8)

- **Este `.md`:** no se convirtió en página; se leyó como texto.
- **`CLAUDE.md` al día,** en el commit de este informe: la fecha de retiro, lo que pide el portal, los términos por su
  texto, las tres evidencias nuevas y el número de pruebas.
- **En el mismo commit, dos cambios de `AQUASHIELD.py` que no tocan el código:** la lista del docstring de
  `_evidencia_antes_de_la_guarda`, que no nombraba las tres evidencias nuevas, y el comentario de
  `_JS_MK_RETIRO_PUESTO`, que decía que en las capturas del 21-09 se lee «el día aparte». Son posteriores al censo
  completo; ninguna mutación tiene su ancla en esas líneas, y su gate fue la suite completa: 443 pruebas en verde (314
  s) y 0 cambios en los originales.
- **La red, commit por commit:**

| Commit | Pruebas | Mutaciones | Pares |
|---|---|---|---|
| `b59b40e` (base) | 415 | 1107 | 1337 |
| `3841c9f` | 420 | 1121 | 1353 |
| `5aed8ba` | 436 | 1173 | 1414 |
| `44faaa9` | 442 | 1194 | 1437 |
| `1ef2536` | 443 | 1216 | 1464 |

- **El gate de cada commit:** la suite completa en verde, con 0 cambios en los originales, y los censos filtrados
  (mutaciones / pares), todos en OK:

| Commit | Suite | Censos filtrados |
|---|---|---|
| `3841c9f` | 420 | TestMaersk 81/104 · TestSinClicACiegas 21/31 |
| `5aed8ba` | 436 | TestRetiroMaersk 54/64 · TestMaersk 79/101 (los dos, tras corregir 2 mutaciones) · TestFotoDeClicsGenericos 29/55 · TestCadaReservadorLaDeja 25/52 |
| `44faaa9` | 442 | TestTerminosMaersk 19/20 · TestMaersk 81/104 · TestFotoDeClicsGenericos 30/57 |
| `1ef2536` | 443 | TestRetiroMaersk 68/81 (tras corregir una prueba) · TestTerminosMaersk 25/28 · TestMaersk 84/108 · TestCadaReservadorLaDeja 26/55 · TestFotoDeClicsGenericos 30/57 |

- **El censo completo sobre `1ef2536`:** el control pasó con las 443 pruebas; 1216 mutaciones y 1464 pares, y los 1464
  muerden: ninguno quedó sin morder ni cayó por tiempo agotado. 0 pruebas sin mutación y 0 cambios en los 2893
  originales. Tardó 2 h 35 min, de los que 1 h 42 min fueron de la máquina en espera.
- **Cada commit:** la sonda de secretos dio 0 sobre el árbol y 0 sobre lo agregado, y 0 CR en los archivos commiteados.
- **La revisión de código** está arriba.
- **La revisión adversarial de este informe:** un agente, en solo lectura y con sus propias sondas (sin mirar capturas),
  la segunda vez: la primera se trabó con la máquina en espera. Confirmó las dos tablas de la red, lo medido en el HTML
  del 27-09, el `log.txt` del 21-09 y cada motivo de los cortes, sin voseo ni datos reales. Trajo 6 hallazgos altos, 5
  medios y 14 bajos, verificados y corregidos en esta versión:
  - los altos: pieza 4, 15;
  - los medios: el clic de JavaScript en la casilla, «el primer textarea» de la referencia, la pieza 1 incompleta, las
    otras llaves del candado en «Cómo probarlo» y que «Choose another date» a la vista no está medido en la página real;
  - los bajos: las esperas de la máquina medidas, las carpetas vacías, la lista de `mc-*`, qué corrida era de qué
    encargo, lo que pulsaba el código de entonces, las pruebas de la revisión del 21-09, el día en la tarjeta, una fila
    de los términos, una de NO retroceder, dos premisas refutadas, la casilla ya marcada, lo que leía `_mk_errores`, la
    frase de re-medir y el gate del docstring.

  El revisor corrió una vez `sort` de Git Bash; Defender lo bloqueó, sin efecto.
