# CICLO · Los frenos del 26-09 con tus decisiones: MSC, ONE, CMA y el viaje; HYUNDAI vuelve a frenar

**Módulo:** Agendamiento Reservas · **Encargo 31** · **Fecha:** 2026-09-26 · **Método:** skill `metodo-ciclo` v14 ·
**Commits** (locales; el repo no tiene remoto, así que no hay push que entregar): uno por ítem, `351e637` (MSC), `2e5afbb`
(ONE), `6905580` (CMA) y `285e296` (el viaje en MAERSK y COSCO), y el de este informe.

**Base: `C:\dev\Agendamiento Reservas` @ `4948e16` · árbol limpio** (pieza 9). Las mediciones de `logs/` y de las
planillas se hicieron sobre esa base, antes del primer commit del encargo, salvo `viaje_efecto.py`, que corrió después,
con el programa de `285e296`, sobre los mismos `logs/` y planillas.

> Sin datos reales. `logs/`, las planillas y `config.json` se midieron en solo lectura, con sondas que tapan naves,
> viajes, fechas, contratos y el nombre del operador, e imprimen conteos, booleanos, etiquetas de la interfaz y formas
> enmascaradas. Las capturas se leyeron con OCR sin mirarlas. Los HTML guardados se leyeron en un Chromium sin red y sin
> el JavaScript de la página.

**Resumen:**
- **Cuatro decisiones quedaron hechas,** una por commit:
  - MSC repite el login tras un 502, hasta 2 veces y avisando, y su botón de entrar va solo por su texto;
  - ONE espera, tras el login, la dirección donde su portal aterriza hoy;
  - CMA reconoce el aviso de mantenimiento y sus filas quedan NO ENVIADA con «el portal de CMA está en mantenimiento»;
  - MAERSK y COSCO cortan con motivo si la fila trae viaje y ninguna salida de la nave lo trae.
- **HYUNDAI frenó, y no se tocó:** en la evidencia de hoy, la nave de la fila, con su viaje, aparece en los dos campos:
  como MAIN VESSEL en una tarjeta, como 1ST VESSEL en otra, y en los dos en una tercera. Es tu condición de freno. Tampoco
  se implementó la opción del modal: sin el campo, HYUNDAI llegaría a la guarda con la tarjeta que hoy elige el texto de
  toda la tarjeta.
- `test_candado` no cambió, y ningún clic nuevo quedó antes de la guarda.

## Veredicto del PASO 0, por parte del encargo

| Parte | Veredicto | Qué quedó |
|---|---|---|
| HYUNDAI: el campo de la nave | **PREGUNTA** (freno del encargo): la nave está en los dos campos | Medido abajo. Nada cambió en HYUNDAI |
| HYUNDAI: la opción del modal | **PREGUNTA:** va con el campo. Su propio freno (si deja avanzar sin otro clic) no se puede medir sin el portal | Medido el HTML del modal. No se implementó |
| MSC: el reintento tras un 502 y el botón por su texto | **CICLO** | `351e637` |
| ONE: la dirección tras el login | **CICLO** | `2e5afbb` |
| CMA: el aviso de mantenimiento | **CICLO** | `6905580` |
| MAERSK y COSCO: el viaje que ninguna salida trae | **CICLO** | `285e296` |

## HYUNDAI (FRENO)

**El campo de la nave.** Decidiste compararla con el campo, MAIN VESSEL o 1ST VESSEL, donde aparece en la evidencia de
hoy. Medido en las dos listas guardadas (`hmm_f9_naves.html`, 14:18 y 14:25), iguales entre sí: 6 tarjetas con «Book
Now», cada una con MAIN VESSEL, ROUTE, OPERATOR, 1ST VESSEL y tres fechas con hora (dos cortes y el DOC CUT).

| Tarjeta (orden por su primera fecha) | La nave de la fila, en MAIN VESSEL | En 1ST VESSEL | Su viaje, en ese campo |
|---|---|---|---|
| 1.ª a 3.ª | No | No | — |
| 4.ª | **Sí** (la 1ST VESSEL, la que sale de Chile, es otra nave) | No | Sí |
| 5.ª | No (la MAIN VESSEL es otra nave) | **Sí** | Sí |
| 6.ª | **Sí** | **Sí** | Sí, en los dos |

La nave, con su viaje, aparece en los dos campos: frena, con cualquier lectura. Entre tarjetas, está en la 4.ª y en la
5.ª; dentro de una, en la 6.ª. Y aun leyendo «el campo de la tarjeta que el programa elige hoy» (MAIN VESSEL), quedan dos
(la 4.ª y la 6.ª), y HYUNDAI todavía no aplica la próxima salida. Qué tarjeta sería la de la fila depende de qué quieras
decir con «la nave»:
- la que lleva la carga en el tramo principal: la 4.ª o la 6.ª;
- la que sale de Chile: la 5.ª o la 6.ª;
- las dos a la vez: solo la 6.ª, la que trae la misma nave en los dos campos.

El programa elige hoy la 4.ª: la primera en la página cuyo texto trae la nave. El orden de la página es el de las fechas.

La distribución de la nave en las tarjetas ya estaba en `CICLO-inicio-de-todas.md`; lo nuevo es que el viaje de la fila
está en el mismo campo que la nave en las tres.

**La opción del modal.** Decidiste marcar «I do not want to choose an alternate vessel», por su texto, y pulsar OK. No se
implementó. Su propio freno no se pudo medir sin el portal.
- **Va con el campo:** hoy HYUNDAI siempre corta en el modal. Con la opción sola, lo pasaría y seguiría hacia la guarda
  con la 4.ª tarjeta, cuya nave de salida desde Chile es otra:
  - eso elegiría por defecto la lectura MAIN VESSEL, que es tu decisión;
  - con la lectura 1ST VESSEL, rompería «el programa nunca reserva una nave que la fila no pidió»;
  - el «porque restringe» vale para el portal, que rechaza la reserva si la nave no está; para el programa, la opción
    hace que llegue más lejos.

  El costo: su freno queda sin medir hasta que haya una corrida con la opción implementada.
- **Lo que se midió del modal** (`hmm_f9_otra_nave.html`, las dos corridas, iguales): `div#alternate_vessel_opt`; tres
  opciones, cada una un `label.radio-area` con su `input[type=radio][name=vessel-option]` y su texto; la tercera dice
  exactamente «I do not want to choose an alternate vessel», con la explicación «If requested vessel is not available,
  booking will be rejected.»; y el OK es `#vesselOptionSubmit`, sin `disabled`. La opción se puede identificar por su
  texto.
- **Si marcarla deja avanzar sin otro clic no se puede medir sin el portal:** lo que hace el OK está en el JavaScript del
  portal, que no viene en el HTML guardado (0 de los 41 scripts en línea de la página nombran el modal).

## MSC · el reintento tras un 502 y el botón por su texto (`351e637`)

**Medido** en los 7 logins de MSC de `logs/` (del 21 al 26-09): el 502 salió en 4.
- 3 veces tras el «Next»: el programa recargó (21-09 16:31, 24-09 18:47, 26-09 14:15). En las dos primeras entró; en la
  de hoy, el 502 volvió al pulsar el botón de entrar, la página quedó en el error de Chrome
  (`chrome-error://chromewebdata/`) y el login falló.
- 1 vez, el 21-09 a las 15:03, también tras el «Next», el programa no lo reconoció: anotó «no vi el campo de contraseña»,
  aunque la captura (OCR) muestra la página de error. No se sabe por qué su lectura no vio el texto.

**Cambio.** `login_msc` se partió en sus pasos (`_msc_abrir`, `_msc_entrar`, `_msc_verificar`) sin cambiar lo que hace
cada uno, y ahora:
- si el login termina sin sesión y en la página de error (`_msc_error_502`: el texto a la vista trae «502» o «no puede
  procesar», la misma lectura que ya usaba el primer paso), vuelve a abrir myMSC y lo repite desde el principio, hasta
  `MSC_REINTENTOS_502` = 2 veces. Cada vez avisa en pantalla y en `log.txt`: «⚠ MSC respondió HTTP 502 al entrar.
  Reintento el login (1 de 2).» Si el tercero también termina en el error: «… 3 veces; no reintento más.»;
- si al volver a abrir ya hay sesión, no entra de nuevo;
- un login que falla sin el error (una clave rechazada, un validador) no se repite: decide la verificación, como antes;
- el botón de entrar va solo por sus textos: Login, Sign In, Next o Iniciar. Se quitó `button[type='submit']`.

«Pocas veces» quedó en 2: es una hipótesis, no medida. El reintento cubre también el 502 tras el «Next» que la recarga no
arregla, porque el login termina igual en la página de error.

## ONE · la dirección tras el login (`2e5afbb`)

**Medido:** los 4 logins nuevos de `logs/` (24-09 18:45, 25-09 00:29 y 13:47, 26-09 14:13) terminaron en
`https://www.one-line.com/one-ecom/booking/quick-booking`, y en los 4 la espera de `**ecomm.one-line.com/one-ecom**`
venció a los 25 s. Los 2 que ya tenían sesión también cayeron en `www.one-line.com/one-ecom/…`.

**Cambio:** `login_one` espera `ONE_TRAS_LOGIN = "**://www.one-line.com/one-ecom/**"`, con los mismos 25 s. Calza con esa
dirección y no con el login (`auth.one-line.com`) ni con la de antes. Si vence, lo anota como antes y la sesión la decide
la dirección, como antes. Cada login nuevo debería tardar hasta unos 25 s menos, según cuánto tarde ONE en volver; no
está medido en una corrida.

## CMA · el aviso de mantenimiento (`6905580`)

**Medido:**
- en los 44 HTML de CMA de `logs/` (24 al 26-09), el aviso «We are improving the eBusiness area» está en 1, la pantalla
  donde cortó la fila de hoy, a la vista (sin ancestros ocultos);
- los otros 43 no lo traen;
- con OCR, también en `cma_final` de las dos corridas de hoy.

**Cambio.** Apenas abre Click & Book, `reservar_cma` mira el aviso (`_cma_en_mantenimiento`: el texto a la vista, sin
distinguir mayúsculas ni saltos de línea). Si está:
- deja la captura de la ventana (`cma_f<fila>_mantenimiento`);
- la fila queda NO ENVIADA con `CMA_MANTENIMIENTO`, «el portal de CMA está en mantenimiento», sin buscar el Origen.

Solo lee: ni clics ni esperas nuevas. Sin el aviso, sigue igual. Con «todas», cada fila de CMA hace lo mismo.

## MAERSK y COSCO · el viaje que ninguna salida trae (`285e296`)

**Cambio.** Si la fila trae viaje y ninguna salida de la nave lo trae, no eligen ninguna. La reserva queda NO ENVIADA,
con la evidencia de la lista de cada una:
- MAERSK: `_mk_elegir_nave` devuelve el motivo «sin-viaje»; evidencia `mk_f<fila>_detenida`;
- COSCO: `_cosco_sin_el_viaje`; evidencia `cosco_f<fila>_itinerarios`.

El motivo de MAERSK: «MAERSK: no elegí salida para esa nave ('…'): ninguna de las N opciones de la nave trae el viaje de
la fila. Revisa la fila y elige la salida en el portal.» COSCO dice «itinerario» en los dos lugares. Con una sola opción:
«la única opción de la nave no trae el viaje de la fila». Hasta `4948e16` elegían entre todas las de la nave, sin
avisarlo.

Sin cambios:
- con al menos una salida (o itinerario) que traiga el viaje, se elige entre esas, como antes;
- sin la nave en la lista, cada una sigue su camino de nave no encontrada;
- una fila sin viaje sigue igual.

**MAERSK corta con lo que ya cargó, antes de mirar el «Book»:**
- la N cuenta todas las salidas de la nave en ese lote, se puedan reservar o no;
- «Search more sailing options» lo pide solo si no queda ninguna salida reservable de la nave (con el viaje, si la fila
  lo trae);
- con la nave solo en salidas sin «Book» y ninguna con el viaje, ahora corta; hasta `4948e16` pedía más salidas.

**Medido sobre la evidencia guardada** (`viaje_efecto.py`, con el programa de `285e296`): el corte no se habría activado
en ninguna.
- MAERSK: 5 listas medibles, las 5 con viaje en la fila y 2 con la nave en la lista. De los otros 48 HTML, ninguno trae
  la lista.
- COSCO: 2 listas medibles, las 2 con la nave. De los otros 18 HTML, ninguno trae la lista.
- En las planillas, las 72 filas con nave traen un viaje con letras y cifras. Ninguna trae un marcador («-», «TBA»), que
  ahora cortaría.

**Convención:** «hasta `4948e16`» quiere decir «antes del encargo 31», en este informe y en los comentarios del código.

## Expectativas que cambiaron (antes → ahora)

- `test_clics.TestMsc.test_login_sin_clic_generico`: mira los pasos en `_msc_entrar`, y el selector de entrar ya no trae
  `button[type='submit']`.
- La mutación `cosco-calza-sin-el-viaje` apunta a `_cosco_trae`, el ayudante que sacó el calce de `_cosco_calzan` sin
  cambiarlo.
- **Pruebas nuevas (7),** todas en `test_clics`:
  - `TestMsc.test_error_502` y `test_login_reintenta_tras_un_502`;
  - `TestOne.test_login_espera_la_direccion_de_hoy`;
  - `TestCma.test_aviso_de_mantenimiento` y `test_en_mantenimiento_la_fila_queda_no_enviada`;
  - `TestMaersk.test_sin_el_viaje_de_la_fila_no_elige` y `TestCosco.test_sin_el_viaje_de_la_fila_corta`.

  Además, `test_ayudantes.TestProximaSalida.test_el_motivo_en_palabras` suma el motivo «sin-viaje».
- **Mutaciones nuevas (39):**
  - 13 de MSC (`msc-502-*`, `msc-error-502-*` y `msc-entrar-con-submit`);
  - 5 de ONE (`one-login-*`);
  - 9 de CMA (`cma-mant-*`);
  - 12 del viaje (`mk-viaje-*`, `motivo-sin-viaje-*`, `cosco-viaje-*` y `cosco-sin-viaje-*`).

  Se actualizaron 4 viejas: las dos que usan el mensaje del botón de entrar de MSC (`SIN_ENTRAR`), `mk-viaje-no-filtra` y
  `cosco-calza-sin-el-viaje`.
- **`test_candado` no cambió:** `git diff 4948e16 285e296 -- tests/test_candado.py` sale vacío. `PERMITIDOS` de `test_clics`
  tampoco.

## Veredicto por naviera: ¿lista para una emisión real de prueba?

| Naviera | Veredicto | Qué le falta | Lo nuevo de este encargo |
|---|---|---|---|
| **MSC** | **Casi lista** | Una corrida con candado cerrado que pase el login con el reintento, si el 502 vuelve | Repite el login tras un 502; el botón de entrar, por su texto |
| **ONE** | **Casi lista** | Una corrida con login nuevo que llegue a Review Booking | La espera del login, en la dirección de hoy |
| **COSCO** | **No para emitir** | El programa no reconoce el número de su confirmación | Corta si ninguna salida trae el viaje |
| **HYUNDAI** | No | Tus decisiones sobre el campo (con esta medición) y, con eso, la opción del modal; aplicar la próxima salida | El campo, medido: la nave está en los dos |
| **CMA** | No | Que salga del mantenimiento; la lista, la próxima salida y su número | Reconoce el mantenimiento |
| **MAERSK** | No | Una fila cuya nave tenga una salida con «Book», para llegar a la revisión | Corta si ninguna salida trae el viaje |

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\correr.py --mutaciones --filtro msc-
python tests\correr.py --mutaciones --filtro one-login-
python tests\correr.py --mutaciones --filtro cma-mant-
python tests\correr.py --mutaciones --filtro mk-
python tests\correr.py --mutaciones --filtro motivo-
python tests\correr.py --mutaciones --filtro cosco-
python tests\correr.py --todo
```

Las sondas son de solo lectura y no se versionan, porque leen datos reales. Quedaron en la carpeta temporal de la sesión
(`scratchpad\e31`, y las del encargo 30 en `scratchpad\e30`), que puede limpiarse; sin ellas, estos números no se
re-miden. Cada una aborta si su control no da lo esperado:
- **`e31\hmm_campos_viaje.py`:** en qué campo de cada tarjeta de HYUNDAI está la nave de la fila, y su viaje.
- **`e31\hmm_modal_esqueleto.py`:** el esqueleto del modal, con el texto tapado.
- **`e30\hmm_hoy.py`, `hmm_modal_estructura.py`, `hmm_modal_texto.py` y `hmm_js_popup.py`:** la lista y el modal de
  HYUNDAI, re-corridas sobre la base.
- **`e30\v_msc_logins.py` y `v_msc_ocr.py`:** los logins de MSC y sus capturas.
- **`e31\v_one_logins.py`:** los logins de ONE, con la consulta de cada dirección tapada.
- **`e31\cma_mant_universo.py` y `e30\verif_cma_mant.py`:** el aviso de CMA en todos sus HTML y en las capturas de hoy.
- **`e31\viaje_efecto.py`:** en qué listas guardadas de MAERSK y COSCO cortaría el viaje, y la forma de las celdas de viaje
  de las planillas.
- **`e26\red_por_commit.py`:** pruebas, mutaciones y pares de la red en cada commit, leídos de git.
- **`e31\datos_en_informe2.py`:** si este informe o `CLAUDE.md` traen palabras de las celdas de la planilla.

Cada una se corre con `python "%TEMP%\claude\C--dev-Agendamiento-Reservas\<sesión>\scratchpad\<carpeta>\<sonda>.py"`
y la variable `PYTHONIOENCODING=utf-8`. Las 15 carpetas de `logs/` se contaron con una línea de Python en la consola, sin
imprimir sus nombres.

## NO retroceder (pieza 2)

- **No vuelvas a tomar el botón de entrar de MSC por `button[type=submit]`:** es el primero de la página, no el suyo.
- **No reintentes el login de MSC tras cualquier falla,** ni sin volver a abrir la página, ni en silencio.
- **No vuelvas a esperar `ecomm.one-line.com/one-ecom` tras el login de ONE:** ya no aparece.
- **No busques el Origen de CMA con el aviso de mantenimiento a la vista.**
- **No vuelvas a elegir entre todas las salidas de la nave cuando la fila trae un viaje que ninguna trae** (MAERSK y
  COSCO).
- **No implementes la opción del modal de HYUNDAI sin el campo de la nave:** pasaría el modal con la tarjeta que elige el
  texto de toda la tarjeta.

## Universo y cobertura (pieza 3)

- **`logs/`:** 15 carpetas, todas con `log.txt`; 0 descartadas.
- **HYUNDAI:** 2 listas de 6 tarjetas y 2 modales (las dos corridas de hoy); 0 descartados.
- **Logins:** MSC, 7; ONE, 6 (4 nuevos y 2 con sesión).
- **CMA:** 44 HTML (con sus marcos), del 24 al 26-09; 0 descartados. Las carpetas sin fecha en el nombre: 0.
- **MAERSK y COSCO, el viaje:** 53 HTML de MAERSK y 20 de COSCO (con sus marcos). Traen la lista 5 y 2; los otros no la
  traen, y ninguno se descartó por no conocer la fila. Planillas: 72 filas con nave.
- **No medido:**
  - si marcar «I do not want…» y OK deja avanzar sin otro clic: hace falta el portal;
  - si el login de MSC entra con el reintento: el 502 no se puede provocar;
  - cuánto tarda ahora el login de ONE;
  - por qué el 502 del 21-09 tras el «Next» no se reconoció;
  - si el viaje de alguna fila está en salidas de MAERSK que no cargaron en el primer lote.

## Defectos de instrumento cazados (pieza 4)

1. **El control de `hmm_modal_esqueleto.py` abortó la primera vez:** esperaba 4 elementos en un modal sintético que tiene
   5. Se corrigió el control, no la sonda.
2. **El parche del viaje dejó una mutación vieja apuntando a una línea que ya no existía** (`mk-viaje-no-filtra`). El censo
   en la copia de simulación lo cazó («el texto viejo aparece 0 veces») antes de tocar el repo.
3. **La revisión de MSC:**
   - la docstring de `_msc_error_502` citaba `CICLO-inicio-de-todas.md` por el OCR de `msc_paso_email`, que ese informe
     no trae. Se corrigió después del gate; `TestMsc` y el censo `msc-error-502` se volvieron a correr;
   - señaló que la lectura del 502 («502» en el texto a la vista), que antes decidía solo la recarga tras el «Next», ahora
     decide también el reintento de todo el login. Queda en el residual.
4. **La revisión de ONE, CMA y el viaje:**
   - MAERSK corta con el primer lote de salidas, sin pedir más. Queda como pregunta (choque 3 de la pieza 7). La revisión
     del informe agregó que el corte va antes de mirar el «Book»: con la nave solo en salidas sin «Book», ahora corta,
     y antes pedía más salidas. Se declaró arriba y en el residual;
   - dos líneas de 121 caracteres, que se reacomodaron antes de cada gate;
   - pidió confirmar el OCR de `cma_final` que cita el comentario de CMA: se midió con `verif_cma_mant.py`, en las dos
     corridas.
5. **`v_one_logins.py` es una copia de la sonda de MSC** con el bloque cambiado: su descripción todavía habla de MSC y
   cuenta «502» (0 en ONE). No cambia lo medido.
6. **`viaje_efecto.py` no veía la fila de COSCO:** buscaba un formato de línea que COSCO no escribe, y descartó los 20
   HTML sin tratarlo como falla. Se corrigió el patrón («[COSCO fila N] … | NAVE:») y se le agregó un control que aborta
   si los descarta todos.
7. **La revisión del informe** corrigió:
   - dos contradicciones (cuántos 502 hubo tras el «Next»; si el freno de la opción «no se activó» o no se pudo medir);
   - el texto exacto del motivo del viaje;
   - el filtro `motivo-` en la pieza 1;
   - que el FRENA SI trae dos condiciones, no una.
8. **La sonda de datos reales del encargo 30 (`datos_en_informe.py`) miraba una sola columna:** toma como encabezado la
   primera fila de cada hoja, que en la planilla es un título, y juntó solo 9 palabras. Su control pasaba igual, porque
   usa una de esas 9. La nueva, `e31\datos_en_informe2.py`, lee las 72 filas con el lector del programa (47 palabras de
   nave, viaje, cotización, destinos y puerto de carga) y exige al menos 50 filas. Sobre este informe y `CLAUDE.md`, las
   palabras de la planilla que aparecen están todas también en el código. El único número largo del informe es el hash
   `6905580`. El chequeo del encargo 30 se hizo con la sonda vieja y no se repitió sobre sus textos.

## Premisas del encargo contrastadas (pieza 5)

- **«La nave de la fila se compara con el campo donde aparece en la evidencia de hoy»:** supone que aparece en uno. Aparece
  en los dos (refutada; es el freno).
- **«Si esa opción no está, la reserva corta como hoy»:** la opción está, con ese texto exacto, en los dos modales
  guardados.
- **«MSC reintenta tras un 502 al entrar»:** el 502 al pulsar el botón de entrar salió 1 vez en 7 logins, hoy. El del
  primer paso, tras el «Next», salió en 4 logins: en 3, el programa lo reconoció y recargó; en 1 (21-09, 15:03), no.
- **«ONE espera la dirección que su portal usa hoy»:** medida, `www.one-line.com/one-ecom/…`, en los 4 logins nuevos.
- **«CMA reconoce el aviso de mantenimiento»:** el aviso está en el HTML, a la vista, en 1 de 44, y en ningún otro.
- **«MAERSK y COSCO eligen entre todas»:** confirmado en el código de `4948e16`.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| HYUNDAI: el campo de la nave, la opción del modal, el texto del motivo y la próxima salida | FRENO: la nave está en los dos campos | …decides el campo |
| Si el «Book Now» de HYUNDAI deja algo en el portal | No está medido | …revisas el portal |
| El 502 del 21-09 tras el «Next» no se reconoció | No se sabe por qué su lectura no vio el texto | …se repite con traza |
| «Pocas veces» son 2 | Hipótesis | …un 502 dura más que tres intentos |
| `_msc_error_502` lee «502» o «no puede procesar» en todo el texto a la vista, y ahora decide el reintento de todo el login | Es la lectura que ya usaba el primer paso; un falso positivo costaría hasta 2 logins más, avisados | …un login falla por otra causa con «502» en la página |
| MAERSK no pide más salidas para buscar el viaje antes de cortar | Lo decidido era cortar en vez de elegir; no se agregaron clics | …el viaje de la fila está en salidas que no cargaron |
| MAERSK con la nave solo en salidas sin «Book» y sin el viaje: ahora corta NO ENVIADA; antes pedía más salidas | El corte mira todas las salidas de la nave, se puedan reservar o no | …decides que el viaje se busque solo entre las reservables |
| Un marcador en la celda del viaje («-», «TBA») cortaría: en MAERSK, cualquiera; en COSCO, uno de dos letras o más | Hoy ninguna fila lo trae (72 de 72 con letras y cifras) | …una planilla trae marcadores en esa celda |
| CMA en mantenimiento deja la captura, sin HTML | El aviso se lee del texto a la vista; la captura basta para verlo | …el aviso cambia de texto |
| ONE: si no ve «Sign In», `login_one` todavía pulsa `button[type='submit']`, el mismo patrón que se le quitó a MSC; y el `**` inicial de `ONE_TRAS_LOGIN` calzaría con una dirección de login que trajera la de regreso sin codificar | No era parte de lo decidido; lo segundo no se vio (las consultas se midieron tapadas) | …decides el botón de ONE, o un login de ONE falla tras la espera |
| El asistente de ONE que se reinició tras un login nuevo (26-09) | Un solo caso, sin causa medida | …se repite con traza |
| La página de CMA que se cerró a las 14:25:13 | No se sabe quién ni qué la cerró | …se repite |
| CMA y COSCO sin forma de número; la casilla de términos de MAERSK; los demás residuales de `CICLO-inicio-de-todas.md` | Sin evidencia nueva | …según ese informe |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v14**.
- **PASO 0 con sus cuatro valores:** CICLO (cuatro ítems) y PREGUNTA (HYUNDAI).
- **FRENAR cuando la decisión es de negocio:** el freno de HYUNDAI se reporta con lo medido y sin implementar.
- **Re-medir contra HEAD antes de diseñar:** las sondas del encargo 30 se volvieron a correr sobre `4948e16` antes de
  tocar el código.
- **Control positivo que aborta:** en cada sonda.
- **Todo salto silencioso lleva contador:** 0 carpetas y 0 HTML descartados.
- **Todo registro es una hipótesis:** «no vi el campo de contraseña» del 21-09 era un 502 que la lectura no vio.
- **El negativo tiene que morder:** en cada commit, el censo filtrado; al cerrar, el censo completo.
- **El cambio y su guardián en la misma operación:** cada ítem trae sus pruebas y mutaciones en su commit.
- **Fuente única:** el 502 del primer paso y el del final se leen con el mismo ayudante, y el calce de COSCO con
  `_cosco_trae`, en `_cosco_calzan` y en el corte.
- **Cada reemplazo afirma su viejo una vez; el EOL se preserva:** los parches abortan si el texto no calza. Cada archivo
  del árbol es idéntico byte a byte a su blob, y `git ls-files --eol` da `i/lf w/lf` en los 4 archivos tocados.
- **Verificación adversarial:** la revisión de cada ítem y la de este informe.
- **Choques entre reglas:**
  1. **El freno del campo contra la opción decidida.** El FRENA SI trae dos condiciones: la del campo, que se cumplió, y
     la de la opción, que no se puede medir sin el portal. Se frenó la decisión entera. Sola, la opción haría pasar el
     modal a HYUNDAI con la 4.ª tarjeta, cuya nave de salida desde Chile es otra: elegiría por defecto la lectura MAIN
     VESSEL, que es tu decisión, y con la lectura 1ST VESSEL rompería «solo la nave que la fila pide». El costo: su
     propio freno no se mide hasta que haya una corrida con la opción implementada. Si la quieres sola, se implementa
     aparte (pregunta 4).
  2. **«Tras un 502 al entrar» contra lo que se puede ver.** El programa no distingue en qué paso salió el 502 que dejó el
     login en la página de error. Se implementó «si el login termina sin sesión en la página de error», que incluye el
     del botón de entrar y el del «Next» que la recarga no arregló.
  3. **«Ninguna salida de la nave lo trae» contra «el único clic nuevo permitido antes de la guarda».** MAERSK carga sus
     salidas por lotes («Search more sailing options»), y pide más solo si no queda ninguna salida reservable de la
     nave. Buscar el viaje en lotes
     siguientes sería pulsar ese botón en un caso en que antes no se pulsaba, y el encargo permite un solo clic nuevo, el
     de HYUNDAI. Se cortó con lo cargado, y queda como pregunta. La revisión lo marcó como el hallazgo más serio: una
     salida con el viaje en el lote siguiente quedaría NO ENVIADA.

Reglas del módulo: casos sintéticos; la sonda de secretos antes de cada commit; nada de `logs/` en el repo; ningún clic
nuevo antes de la guarda (el reintento de MSC repite los mismos pasos del login, identificados por su texto o su selector
propio); `test_candado` sin cambios; los textos en español con tuteo.

## Entregable (pieza 8)

- **Este `.md`:** no se convirtió en página; se leyó como texto.
- **`CLAUDE.md` al día,** en el mismo commit.

**La red por commit:**

| Commit | Pruebas | Mutaciones | Pares |
|---|---|---|---|
| `4948e16` (base) | 372 | 913 | 1125 |
| `351e637` (MSC) | 374 | 926 | 1138 |
| `2e5afbb` (ONE) | 375 | 931 | 1143 |
| `6905580` (CMA) | 377 | 940 | 1152 |
| `285e296` (el viaje) | 379 | 952 | 1164 |

Contada de git con `scratchpad\e26\red_por_commit.py`, del encargo 26.

**Gates.** En cada uno, la suite completa pasó con 0 cambios en los originales, y la sonda de secretos dio 0 sobre el
árbol y sobre lo agregado con `git add`.

| Commit | Suite completa | Censos filtrados |
|---|---|---|
| MSC, `351e637` | 374 en verde | `msc-`: 71 mutaciones y 81 pares, todas muerden. Tras corregir la docstring: `TestMsc` (15 pruebas) y el censo `msc-error-502` (3 mutaciones y 3 pares), en verde; su salida no se guardó |
| ONE, `2e5afbb` | 375 en verde | `one-login-`: 5 mutaciones y 5 pares, todas muerden |
| CMA, `6905580` | 377 en verde | `cma-mant-`: 9 mutaciones y 9 pares, todas muerden |
| El viaje, `285e296` | 379 en verde | `mk-`, `cosco-` y `motivo-`: 153 mutaciones y 169 pares distintos, todas muerden |

- **ONE, CMA y el viaje se probaron antes en una copia de simulación,** con sus pruebas y el censo de sus mutaciones
  nuevas, mientras corría el gate anterior.
- **Los filtros incluyen las mutaciones que nombran una prueba cambiada:** `msc-` las de `test_login_sin_clic_generico`,
  y `motivo-` las de `test_el_motivo_en_palabras`.

**Censo completo final sobre `285e296`:** pasó, en 44 minutos.
- 379 pruebas, y la copia de control, sin mutar, pasa;
- 952 mutaciones y 1164 pares: los 1164 muerden;
- 0 pruebas sin mutación y 0 cambios en los 2556 archivos originales fotografiados.

## Qué decides tú

1. **HYUNDAI, el campo:** con qué tarjeta se queda la fila cuando la nave está en los dos campos: MAIN VESSEL (4.ª y
   6.ª), 1ST VESSEL (5.ª y 6.ª), o los dos a la vez (solo la 6.ª). Con eso se implementa también la opción del modal, como
   la decidiste, y la próxima salida entre las que queden.
2. **HYUNDAI, el motivo** de la reserva que corta si la opción no está.
3. **MAERSK:** si, antes de cortar por el viaje, debe pedir más salidas («Search more sailing options», un clic que ya
   existe), y si el viaje se busca solo entre las salidas que se pueden reservar.
4. **HYUNDAI, la opción sola:** si la quieres ya, con el candado cerrado, para medir en una corrida si deja avanzar sin
   otro clic, aceptando que llegue a la guarda con la tarjeta que elige hoy (la 4.ª).
