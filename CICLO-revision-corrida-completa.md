# CICLO · Revisión de la corrida completa con el candado cerrado

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-24 · **Método:** skill `metodo-ciclo` v12 ·
**Base:** `fbc0588` (último de código: `0f1507e`) · **Corrida revisada:** la «todas» de las 18:45, con una fila por
naviera · **Commits** (locales, sin push; el repo no tiene remoto):
- `d938cd1` CMA;
- `e910bf1` COSCO;
- el de este informe.

> Sin datos reales. La evidencia (log, capturas y HTML) se midió en su lugar y en solo lectura:
> - el log, con un lector que imprime solo las plantillas de mensaje del programa y enmascara cada valor;
> - el HTML, con instrumentos que sacan estructura de interfaz: etiquetas, placeholders, textos de botón y avisos
>   con cifras y mayúsculas tapadas;
> - de una captura del 23 de septiembre, solo un recorte de la ventana Reminder, borrado después.
>
> Aquí no van naves, rutas, contratos ni nombres.

## Las seis navieras

**El candado aguantó:**
- ninguna fila terminó en EMITIDA ni en ENVIADA;
- el log no tiene ninguna línea de la rama de emisión («MODO EMISIÓN REAL», «EMISIÓN: Pulsando…», «evidencia del
  envío»);
- no hay archivos `_confirmado`;
- las cuatro que llegaron a su guarda dijeron «Me DETENGO…».

| Naviera (fila) | Estado final | Dónde terminó | Avisos del log y de la pantalla |
|---|---|---|---|
| ONE (5) | REVISAR | Buscando la nave en los itinerarios: «NO encontré la nave por el nombre exacto» | Login: «no confirmé redirect en 25 s», pero la sesión quedó iniciada. Antes de la nave, el contrato quedó escrito con ✓. No dejó HTML: su evidencia de guarda va dentro de «si llegó a Review Booking». |
| MSC (10) | OK-EJEMPLO | Summary, su guarda | Login: «HTTP ERROR 502»; al recargar, el campo de usuario dio error y «Next» no apareció, pero siguió con la contraseña y la sesión quedó iniciada. En Summary, «The Quote is expired», «Instant Booking…» y «Required» están en la página pero ocultos (`display:none`). |
| CMA (15) | NO ENVIADA | Panel Reefer: «Temperatura Reefer de CMA» | El panel no se abrió: el abridor pulsó la insignia «to complete». Visible en la pantalla: «Faltan algunos ajustes para carga(s) especial(es), por favor complete». Tras «Validar ruta»: «sin respuesta del portal tras 12 s» y, enseguida, «Ruta validada con éxito» (hallazgo 2). DataDome se resolvió solo. |
| COSCO (20) | OK-EJEMPLO | Booking Details, su guarda | Su CONTROL marcó «✗ Size Type: VACÍO», que es una falsa alarma (pendiente de COSCO). «OJO: 2 itinerarios calzan con la nave; tomo el primero». El puzzle se resolvió solo. |
| HYUNDAI (25) | OK-EJEMPLO | Review & Book, su guarda | «Contract No (Paso 2): sin opción…»; el contrato se puso después, en el paso 3. Sin avisos visibles en la revisión. |
| MAERSK (30) | REVISAR | Select sailing: «la nave no se encontró en itinerarios disponibles» | Aun así dijo «Me DETENGO en Review booking», y el detalle dice «armada hasta Review» (hallazgo 1). «fecha: mañana»: la fila no traía un día de carga que el programa entendiera, y usó «Select tomorrow». |

## Los pendientes

**ONE · el campo del contrato: resuelto, sin cambios.**
- El log dice «contrato ONE: resultado selección 'otros'» y «contrato ONE: escrito … en Otros Contratos ✓».
- El programa escribe solo en `input[name="contractNo"]` y corta si no lo encuentra. El campo tiene
  `name=contractNo`, y el código ya lo usa.

**CMA · el panel Reefer: arreglado el abridor (`d938cd1`); el resto, FRENO.**
- **Lo medido** en `cma_f15_reefer_panel.html`, con el panel supuestamente abierto:
  - en toda la página no aparecen «temperat» ni «°C»;
  - ningún cajón o diálogo contiene «Reefer»;
  - los tres selectores del abridor calzan con otra cosa:

    | Selector | Calza con | ¿Abre el panel? |
    |---|---|---|
    | `text=/TO COMPLETE/i` | `<span class="capsule error-light">to complete</span>`, una insignia de estado | No |
    | `button:has-text('Reefer')` | primero, el encabezado «Detalles de la carga…» | No |
    | `span:has-text('Reefer TO COMPLETE')` | la fila entera | No |

  - El botón propio de la fila es `<button class="style-link">Modifique el reefer</button>`.
- **El arreglo:** el abridor busca solo ese botón, por su texto. Es el mismo clic de antes, con su objetivo
  medido; no hay clics nuevos.
- **FRENO en lo demás** (la evidencia no alcanza):
  - **Los campos del panel y su botón de guardar:** el panel no se abrió.
  - **«I Agree»:** la reserva no llegó a la revisión.
  - **«Faltan algunos ajustes…» en la revisión:** no se llegó. En la pantalla de carga ese aviso sí está visible.
  - Para medirlos hace falta otra corrida de CMA con este arreglo: `cma_f<fila>_reefer_panel.*` va a mostrar el
    panel abierto.
- **Un riesgo medido, sin arreglar:** el JavaScript de la temperatura busca en el primer contenedor
  `.el-drawer, [class*="drawer"], [role="dialog"]` de la página. Aquí ese primero es un diálogo oculto
  (`u-hidden`), así que con el panel abierto podría seguir sin encontrar el campo. Se decide con el HTML del panel
  abierto.

**COSCO · Booking Details: completo en lo que la evidencia alcanza, sin cambios.**
- **Lo que confirma el CONTROL del programa**, que lee la pantalla en vivo: Quantity (1), Gross Weight (22500),
  Temperature (-20) y Shipper.
- **Size Type:** el CONTROL dice «VACÍO» en **15 de 15** controles de Booking Details de todas las corridas de
  COSCO. Eso incluye los 5 del 23 de septiembre, que pasaron la validación, mostraron el Reminder y crearon las
  reservas. Es una falsa alarma: el CONTROL no sabe leer ese select (hallazgo 4).
- **El HTML no alcanza para verificar valores.** Trae los atributos de cada campo, no lo que se escribió (Vue lo
  guarda en la propiedad): de 58 campos, solo 1 trae su valor en el HTML.
- **«… is required»:** 0 mensajes. Con el candado cerrado no hay Submit y el portal no valida, así que el cero
  solo dice que no hubo errores antes de enviar.

**MAERSK · FRENO: la evidencia no alcanza.**
- La nave de la fila no estaba en los itinerarios, así que MAERSK no llegó a «Additional details» ni a la
  revisión. No se puede saber si avanza sin la fecha de retiro, ni medir la casilla de términos.
- No se cumplió el FRENA SI de la fecha: MAERSK no quedó NO ENVIADA en la revisión.
- **Falta** una corrida de MAERSK con una fila cuya nave sí esté en los itinerarios.

**COSCO · el Reminder: hecho (`e910bf1`).**
- **Medido en la captura** (un recorte temporal de la ventana, borrado después):
  - título «Reminder», con su cierre «×»;
  - el texto «To complete your booking request, please submit below document(s) before deadline:»;
  - los dos documentos;
  - un solo «Submit» y un «Back»;
  - todo bajo la máscara de carga.
- **Cómo pulsa ahora** (`_JS_COSCO_SUBMIT_DEL_REMINDER`):
  - La ventana es el elemento visible más interno que tiene el título y el texto. Dentro de ella tiene que haber
    un solo «Submit», y ese se pulsa.
  - Con dos o con ninguno, no pulsa nada. Nunca «el último Submit» de la página.
- **Después:** `_cosco_esperar_resultado` pulsa ese Submit **una sola vez**, en el marco o en la página. Después
  solo espera, sin volver a pulsar, hasta ver errores o una señal de envío, o hasta
  `COSCO_ESPERA_CONFIRMACION_SEG` = 180 s, que es una **hipótesis no medida**. Si vence, `_resultado_envio` da
  ENVIADA – REVISAR EN PORTAL.
- **Sale** todo lo que elegía el último: el `.last` del localizador, el `subs[-1]` y los dos `allSub` del
  JavaScript, incluido el que volvía a pulsar en cada vuelta de la segunda fase.

## Hallazgos nuevos (reportados, sin implementar)

1. **MAERSK sin nave dice que llegó a la revisión.** Con la nave no encontrada, la revisión no corre (está dentro
   de «si hay nave»). Aun así, el programa:
   - toma la captura `mk_f<fila>_6_review` de la pantalla de itinerarios;
   - escribe «Me DETENGO en Review booking»;
   - devuelve REVISAR con «armada hasta Review».
2. **CMA dice «Ruta validada con éxito» sin haberla visto.** `_cma_esperar_resultado` devolvió «indefinido» (12 s
   sin respuesta), y el código solo revisa «deshabilitado» y el aviso «no matching». En esta fila el portal sí la
   había aceptado, porque después apareció el itinerario, pero el mensaje afirma algo que el programa no vio.
3. **CMA: el JavaScript de la temperatura busca en el primer contenedor de la página,** que aquí es un diálogo
   oculto (ver el pendiente de CMA).
4. **COSCO: el CONTROL de Booking Details no sabe leer el Size Type.** Da «✗ VACÍO» siempre, aunque la validación
   pasó.
5. **COSCO elige el primero de dos itinerarios que calzan con la nave.** Es una elección por posición entre
   candidatos que su filtro no separa.
6. **ONE no deja HTML cuando no llega a Review Booking.** La evidencia de la guarda está dentro de esa rama, y el
   REVISAR de esta fila quedó solo con capturas.
7. **MSC:** el login pasó por un «HTTP ERROR 502» y un campo que falló al recargar, y se recuperó solo. En Summary
   hay tres avisos del portal, pero ocultos.
8. **HYUNDAI:** el contrato no aparece entre las opciones del paso 2; se pone en el paso 3.

## Expectativas que cambiaron

- **`test_candado`:** no cambia.
- **`test_clics.TestCma.test_reefer_corta_en_cada_paso_sin_pulsar_a_ciegas`:**
  - antes: el abridor era `text=/TO COMPLETE/i`, y el primer caso solo tenía un `div … button` visible;
  - ahora: el abridor es `button:has-text('Modifique el reefer')`, y el primer caso suma la insignia, el
    encabezado y la fila medidos, que no se pulsan.
- **`test_evidencia.TestEvidenciaReefer`:** `ABRE_REEFER` cambia igual.
- **`test_envio.TestCosco`:**

  | Prueba | Antes | Ahora |
  |---|---|---|
  | errores de validación / aviso del portal | 17 esperas | 2 |
  | la espera agotada | 105 esperas | 120 (180 s en vueltas de 1,5 s), con el aviso del plazo |
  | `test_espera_acepta_la_ventana_reminder` | 1 clic y la ventana se cierra | `test_reminder_pulsa_su_submit_una_sola_vez`: la ventana sigue abierta 5 vueltas, 1 clic |
  | `test_espera_ve_la_ventana_reminder_despues` | volvía a pulsar en la segunda fase | `test_reminder_tardio_tambien_una_sola_vez`: 1 clic en 120 esperas |
  | `AlcanceCOSCO` | un JavaScript desconocido reventaba sin decir cuál | se anota y la prueba cae |

- **Mutaciones existentes:**
  - `cma-reefer-abre-a-ciegas`, `cosco-espera-no-anota-el-reminder` y `cosco-espera-otro-plazo` ponen al día su
    «viejo»;
  - `cosco-espera-no-anota-el-reminder-tardio` se borra, porque su código ya no existe.

## Defectos inyectados

- **CMA, 2 mutaciones:** vuelve la insignia; vuelve el botón genérico.
- **COSCO, 2 pruebas nuevas** (lo ambiguo no se pulsa; el JavaScript en Node con 6 casos, en que el «Submit» del
  formulario va al final) **y 9 mutaciones:**
  - el último Submit, pulsar lo ambiguo, sin título, ventanas cerradas;
  - volver a pulsar;
  - callar el clic, callar que no pulsó, avisar en cada vuelta, callar el plazo.

La red pasa de 244 pruebas, 458 mutaciones y 553 pares a **246 pruebas, 468 mutaciones y 568 pares**.

| Commit | Suite | Censo filtrado (mutaciones y pares, todas mordiendo por su razón) |
|---|---|---|
| `d938cd1` | 244 pruebas | «cma-reefer»: 10 y 14 · `test_reefer_corta`: 8 y 11 · `TestEvidenciaReefer`: 10 y 13 |
| `e910bf1` | 246 pruebas | «cosco-»: 38 y 45 · `test_envio.TestCosco`: 20 y 26 |

**Censo completo final sobre `e910bf1`:** **pasó.** Corrió de 19:32 a 20:00, con el árbol limpio antes y después.
La copia sin mutar pasa las 246 pruebas. Las 468 mutaciones, en 568 pares, muerden todas, y no queda ninguna
prueba sin mutación. 0 cambios en los originales.

La sonda de secretos dio 0 sobre el árbol y el staging en cada commit.

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\correr.py --mutaciones
```

- **El candado:** en el `log.txt` de la corrida, el estado de cada «Reserva i: <estado>», las líneas de la rama de
  emisión y los archivos `_confirmado`. Tiene control positivo con líneas sintéticas.
- **El log sin datos:** cada línea contra las plantillas `reg.paso`/`reg.info` del programa, mostrando un valor
  solo si ya está en el código. Reconoció 336 de 343 líneas: 5 son «Sesión iniciada.», que sale de una expresión
  condicional, y 2 son continuaciones.
- **El HTML:** un árbol con `html.parser` sobre `cma_f15_reefer_panel.html` y el marco `bkg2` de
  `cosco_f20_guarda`. Cada instrumento tiene su control positivo: el botón «Mostrar soluciones», el campo «Gross
  Weight» por su placeholder, y el aviso «Faltan algunos ajustes».
- **Size Type en todas las corridas:** contar «✓/✗ Size Type» por etapa en los logs; COSCO aparece en 5 de las 7
  carpetas.

## NO retroceder (pieza 2)

- **No vuelvas a abrir el panel Reefer por «to complete» ni por `button:has-text('Reefer')`:** la insignia no abre
  nada y el botón genérico calza con el encabezado.
- **No vuelvas a pulsar «el último Submit» en COSCO, ni a pulsar el Reminder más de una vez:** las reservas se
  creaban igual y los clics de más no ayudaban.
- **No leas los valores de un formulario en el HTML guardado:** trae los atributos, no lo escrito.

## Premisas del encargo contrastadas (pieza 5)

- **«La evidencia está en las carpetas más recientes»:** confirmada, en una sola carpeta «todas».
- **«ONE: si el campo tiene name=contractNo»:** confirmada por el log.
- **«CMA: qué campos y qué botón tiene el panel»:** no se pudo: el panel no se abrió. La causa es el abridor.
- **«COSCO: Booking Details completo»:** sí, en lo que alcanza la evidencia. El «VACÍO» del Size Type es del
  CONTROL, no del campo.
- **«MAERSK: si llegó a la revisión sin fecha»:** no llegó, por la nave.
- **«Reminder: el programa pulsó el último Submit durante unos 70 s»:** confirmada en el código que salió.

## Universo y cobertura (pieza 3)

- **La corrida:** 1 carpeta, 6 navieras con 1 fila cada una, 343 líneas de log, 36 HTML y 46 capturas.
- **Leído en HTML:** el panel Reefer de CMA (página y 4 marcos), el `bkg2` de COSCO, y los avisos de todas las
  pantallas de guarda y de `sin_objetivo`.
- **Capturas:** solo el recorte de la ventana Reminder.
- **No medido:** el Reminder en su HTML (hace falta una corrida con el candado abierto), el panel Reefer abierto y
  la revisión de CMA y de MAERSK.

## Defectos de instrumento cazados (pieza 4)

1. **El lector del log abortó en su propio control:** la plantilla reconstruida no traía la viñeta «· ».
2. **El lector no desarma las expresiones condicionales:** 5 líneas quedaron sin plantilla, y eran «Sesión
   iniciada.».
3. **El filtro de valores «ya está en el código» deja pasar valores versionados** (puertos de ejemplo, contratos):
   ninguno entró a este informe.
4. **El instrumento de COSCO abortó dos veces en su control positivo:** buscaba etiquetas, y la grilla de
   Container Info usa placeholders. La tercera versión, por placeholder, pasó.
5. **El HTML guardado no trae lo escrito en los campos:** se midió cuántos traen el atributo `value` (1 de 58) en
   lugar de leer valores falsos.
6. **El escaneo de avisos incluía elementos ocultos:** se agregó la revisión de `display:none` y del atributo
   `hidden`. Los tres avisos de MSC estaban ocultos.
7. **Una suma mal hecha en la sesión:** conté 16 controles de Size Type y eran 15 (5 + 3 + 1 + 5 + 1). Lo
   recontó un script antes de escribirlo aquí.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| CMA: campos y botón del panel, «I Agree», el aviso en la revisión | El panel no se abrió | …una corrida de CMA con `d938cd1` deja el panel abierto en `reefer_panel` |
| CMA: el contenedor que elige el JavaScript de la temperatura | Se decide con el panel abierto | …esa misma corrida |
| MAERSK: la fecha y la casilla de términos | La nave de la fila no estaba en los itinerarios | …una fila de MAERSK con una nave que sí esté |
| El Reminder en la realidad: la estructura del DOM y los 180 s | Solo se ve con el candado abierto | …una emisión real de COSCO deja su HTML y su log |
| Hallazgos 1 a 8 | Se reportan en esta corrida | …decides cuáles se arreglan |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v12**:
- **Control positivo que aborta,** en cada instrumento. Abortaron tres veces y se corrigieron antes de leer sus
  ceros.
- **Todo registro es una hipótesis:** el CONTROL de COSCO se contrastó con las corridas que sí validaron.
- **FRENAR:** CMA (lo del panel) y MAERSK, por evidencia insuficiente.
- **La unidad la fija el sujeto:** el control de Booking Details, contado por control y por corrida.
- **El negativo tiene que morder, de a uno por proceso,** con el motivo de cada mutación revisado.
- **El cambio y su guardián en la misma operación,** y el EOL verificado en binario.
- **Se declaran el residual y las premisas.**

Reglas del módulo: casos sintéticos que imitan la estructura medida, la sonda antes de cada commit, y nada de
`logs/` en el repo.

## Entregable (pieza 8)

Este `.md`, sin renderizar, y `CLAUDE.md` al día: el Reminder de COSCO y la red en 246 pruebas.

**Para la próxima corrida con el candado cerrado:**
- **CMA:** su panel Reefer debería abrirse ahora; `cma_f<fila>_reefer_panel.*` va a mostrar sus campos y su botón
  de guardar.
- **MAERSK:** elige una fila cuya nave esté en los itinerarios de MAERSK.

El Reminder solo se puede ver con el candado abierto: cuándo, lo decides tú.
