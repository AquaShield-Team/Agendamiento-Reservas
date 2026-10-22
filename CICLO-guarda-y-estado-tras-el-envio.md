# Encargo 77 · La guarda ve los números nuevos, y COSCO queda con el estado que de verdad tuvo

**Fecha:** 2026-10-22 · **Método:** `metodo-ciclo` v37, en Modo autónomo (por omisión).

Base: `Agendamiento Reservas` @ `abadb88` · árbol limpio. `origin/main` y `origin/estable` estaban en el mismo commit.

**Commits,** en `main` y sin push (el repo es público: el bloque lo lleva Marcelo):
- `90d2281`, el ítem (b), la guarda;
- `719280c`, el ítem (a), el estado de COSCO;
- el de este informe.

Cada commit lleva su red, `CLAUDE.md` y lo que pidieron sus dos revisiones.

## Qué pasó

El 22-10, en el equipo de un colega, una corrida con el candado abierto emitió una reserva de CMA-CGM y una de COSCO.
La evidencia está en Descargas: el log y los HTML de cada paso, 65 en total. Las dos reservas quedaron ENVIADA –
REVISAR EN PORTAL. Según Marcelo, la de COSCO sí quedó creada, y COSCO manda el número por correo. En la emisión del
mismo día, MAERSK devolvió un número de 9 cifras que empieza con 28.

## PASO 0

- **El registro:**
  - `CLAUDE.md` decía que CMA y COSCO no tienen forma medida y nunca llegan a EMITIDA.
  - También decía que la guarda de datos ve los números de MAERSK que empiezan con 27. El comentario de
    `_extraer_bkg_limpio` decía lo mismo.
- **Re-medí contra HEAD (`abadb88`):** la guarda de antes, contra los números reales de este equipo y de la evidencia
  (abajo), y el código de COSCO que corre después de la guarda.
- **Veredicto:**
  - (b): **CICLO**.
  - (a) COSCO: **CICLO**.
  - (a) CMA-CGM: **FRENO**. Con una sola muestra, y sin el número que vio el portal (el encargo lo traía «sin dato»),
    no se fija su forma, y sigue en ENVIADA – REVISAR EN PORTAL.

## (b) La guarda de datos

### Lo medido

**El universo de números reales** (`barrido_reservas.py`). Lo saqué de los datos, no de la guarda:
- en los `log.txt` de `logs/` y en los del colega: «Reserva N: EMITIDA (…)», el «Booking: …» de las líneas «🎉», y el
  «Bkg=…» y el «Bkg: …» de las corridas del 21-09;
- en cada HTML de confirmación: la forma medida de cada naviera (`FORMA_BOOKING`, leída con `ast`), la tarjeta de
  CMA-CGM (`.booking-submitted .booking-ref a`) y la frase de COSCO.

Salieron **15 números distintos**: ONE 1, MSC 1, HYUNDAI 5, MAERSK con 27 5, MAERSK con 28 1, CMA-CGM 1 y COSCO 1.
Control: tiene que haber números de las navieras con forma medida en `logs/` de este equipo, y la guarda de control
tiene que ver alguno de ONE. Si no, la sonda aborta.

Cada número se probó en tres textos: suelto, detrás de «Booking number:» y como lo escribe el log
(«… (Booking: N)»). Son 45 pruebas:

| Guarda | Pruebas sin ver |
|---|---|
| La de `abadb88` | **8 de 45**: el 28 suelto y en el log; el de CMA-CGM y el de COSCO en los tres textos |
| La nueva | **0 de 45** |

### El cambio

- `RESERVA_MAERSK`: `2[78]` y 7 cifras, sin dejar de ver los 27.
- `RESERVA_CMA` y `RESERVA_COSCO`, nuevas. Pasan por el mismo `numero()`, que deja pasar el inventado con las cifras a
  la vista. La forma de cada una salió de su página tras el envío del 22-10, con una muestra de cada una:
  - CMA-CGM: tres letras y 7 cifras, en la tarjeta «Booking enviado»;
  - COSCO: «CD» y 10 cifras, en «Booking … has been submitted successfully!».
- `RESERVA_CON_ETIQUETA` no cuenta otra vez un número que ya vio `RESERVA_MAERSK`: con el 28, la muestra con etiqueta
  salía con dos hallazgos.
- El comentario de `_extraer_bkg_limpio`. Su regla 3 sigue en 27: un 28 lo toma la regla 5, por su «(Booking: …)», que
  es como `_resultado_envio` escribe el detalle de una EMITIDA. Lo fijan dos aserciones de
  `test_booking.test_patrones_por_naviera`.
- `test_booking.py:66`: un contrato inventado de una prueba de HYUNDAI, de tres letras y 7 cifras que no estaban a la
  vista, pasó a 7 ceros, porque la forma de CMA lo tomaba por un número de reserva.

### Revisión de código

`code-reviewer`, en un clon sin remoto dentro de la carpeta del encargo. Su worktree de arranque quedó vacío.
- Comparó la guarda vieja con la nueva sobre 60.000 textos al azar: 0 escapes.
- Corrió las regex nuevas sobre los 105 archivos de texto del clon y sobre 1.117 de la biblioteca de Python: 17
  coincidencias, todas evidentes.
- **Veredicto: APROBAR**, con cuatro LOW:

| Hallazgo | Qué hice |
|---|---|
| L1. Los bordes de las dos formas nuevas no tenían muestra ni mutación: ocho mutaciones que las ensanchan sobrevivían | **Arreglado:** 6 muestras de borde y sus mutaciones (`e77-cma-sin-borde-despues` y las demás) |
| L2. La documentación del inventado nombraba a MAERSK y a CMA, no a COSCO | **Arreglado**, en el docstring y en `CLAUDE.md` |
| L3. `CLAUDE.md` cita este informe, que todavía no existía | Va en el mismo push, en su propio commit |
| L4. La regla 3 de `_extraer_bkg_limpio` sigue en 27, y una mutación lo fija | Queda: hoy solo `_resultado_envio` produce una EMITIDA, con «(Booking: …)»; al RESIDUAL |
| INFO: un monto pegado al código de su moneda (tres letras y 7 cifras) frena como un número de CMA | Declarado en el docstring y en `CLAUDE.md` |

Pidió también comparar las muestras con los números reales (`muestras_contra_reales.py`): **0 de 69** traen uno, ni
sus 7 cifras finales. Control: un texto armado con un número real cuenta 1.

### Revisión de seguridad

`security-reviewer`, en el mismo clon, con el commit que ya traía lo de la revisión de código. Su worktree de arranque
quedó vacío.
- Probó unas 75 formas de escribir los números y el hook de verdad, en un repo inventado.
- Midió tiempos con textos hostiles: las regex nuevas son lineales, de 0,02 a 0,2 s con 2 MB.
- Midió el atajo de `evidente()`: 30 combinaciones por largo; la probabilidad de que un número real pase por casualidad
  es de 3e-6 con 7 cifras y de 3e-9 con 10.
- **Veredicto: APROBAR CON CAMBIOS**, sin CRITICAL ni HIGH:

| Hallazgo | Qué hice |
|---|---|
| **F1 (MEDIUM).** Un número pegado al escape de un literal (`"…\nCD…"`, `"\tQXZ…"`) no frena: la `n` cuenta como letra. Pasaba también con SCLG, EBKG y SCLA, de antes | **Arreglado:** delante de las tres formas con letras, `_ANTES` acepta la letra de un escape (`\n`, `\r`, `\t`, `\f`). Con sus muestras y sus mutaciones |
| **F2 (MEDIUM).** «(Booking: 29…)», como escribe el programa una EMITIDA, pasaba: solo «Booking number» era etiqueta. De punta a punta, el hook lo dejó pasar | **Arreglado:** «Booking:» también es etiqueta. Muestra con 29, mutación, y la vieja `e72-etiqueta-sin-tope` reescrita sobre la línea nueva |
| **F3 (LOW).** Las formas de CMA y COSCO, fijadas con una muestra, y una prueba exigía que otro prefijo pasara | **Arreglado:** COSCO, dos letras cualesquiera; la muestra con «XD» ahora frena |
| **F4 (LOW).** En minúscula, o con un espacio o un guion antes de las cifras, CMA y COSCO pasaban (SCLG admite el espacio) | **Arreglado:** letras en cualquier caja y `[ -]?` antes de las cifras. En lo versionado, 0 hallazgos nuevos |
| F5 (LOW, de antes). Un invisible parte el número (`INVISIBLES` lo cambia por un espacio); las cifras de ancho completo pasan | Declarado en «LO QUE NO VE»; al RESIDUAL |
| F6 (INFO). Los límites ya declarados (partido, pegado a cifras, armado en el código, mensajes de commit) siguen igual | Nada |
| F7 (LOW). La última celda de Excel (tres letras y 7 cifras) o un monto con su moneda frenan | Declarado: se reescriben con las cifras a la vista o con sus puntos de miles |

Con eso, en el clon de revisión:
- la guarda da 69 muestras en verde y **0 hallazgos** en los 109 archivos versionados;
- los 15 números reales, **0 de 45 sin ver**;
- las muestras traen 0 números reales;
- el censo de la guarda: **64 mutaciones y 70 pares, los 70 muerden**, y el de `_extraer_bkg_limpio`, 6 de 6.

## (a) El estado de COSCO tras el envío

### Lo medido

**1. Qué muestra la página de COSCO tras el envío** (`sonda_exito_cosco.py`). La sonda carga cada HTML en un Chromium
sin red y sin el JavaScript de la página, y corre el `_JS_TEXTO_VISIBLE` y el `_JS_COSCO_ERRORES` del programa, leídos
de `AQUASHIELD.py` con `ast`. Control: el marco del formulario del envío del colega tiene que calzar; si no, aborta.
- En el marco del formulario dice «Booking CD<10 cifras> has been submitted successfully! Please check booking status
  in the "To do list".».
- **La frase calza en 1 de los 65 HTML de la evidencia, y en 0 de los 1.347 de `logs/` de este equipo.** Ninguno quedó
  sin leer. La primera corrida dejó 897 sin leer, porque una página rota tapaba a las siguientes. La rehice con una
  página por archivo.
- `_JS_COSCO_ERRORES` da 0 campos y ningún aviso en los 10 HTML de COSCO de esa evidencia.
- La página de arriba trae «fail», «reject» y «error» en textos fijos del sitio: el aviso de cookies y los términos de
  uso. Son los mismos 13 contextos antes del envío (en la guarda) y después (`textos_evidencia.py`).
- **No hay nada que pueda ser un error o un rechazo:** el FRENA SI no se cumple.

**2. El «Reminder».** Esto dice el log del colega:

| Segundo | Lo que pasó |
|---|---|
| 0 | «MODO EMISIÓN REAL: Pulsando 'Submit' en COSCO» |
| 1 | «Esperando el resultado de COSCO…» |
| 13 | la ventana está a la vista; «no identifiqué su Submit sin ambigüedad (sin-ventana, sin-ventana); no pulsé nada» |
| 34 | la evidencia del envío y ENVIADA – REVISAR EN PORTAL |

- Marcelo dice que se cerró sola a los 33 s. La espera terminó con la frase de éxito, porque el programa se detiene al
  verla.
- Es el aviso medido en `CICLO-cosco-campos-y-reminder.md`: «To complete your booking request, please submit below
  document(s) before deadline». **Solo recuerda enviar los documentos** (la Shipping Instruction y el VGM) antes de su
  plazo.
- **Ningún botón hizo falta:** el programa no pulsó nada, la ventana se cerró y la reserva quedó creada. El otro FRENA
  SI tampoco se cumple.
- Por qué `_JS_COSCO_SUBMIT_DEL_REMINDER` no encontró la ventana no se pudo medir: de esa ventana no hay HTML. Va al
  RESIDUAL.

### El cambio

- **El estado nuevo, solo para COSCO:** `EMITIDA – CONFIRMAR POR CORREO` (`EMITIDA_POR_CORREO`). `_resultado_envio` lo
  da con estas condiciones:
  - se pulsó Submit: `pulsado` es True, no None, porque con None el clic pudo no salir;
  - el programa no falló después;
  - el portal no mostró errores, ni de validación ni un aviso;
  - la página o uno de sus marcos dice la frase de `FORMA_ENVIADA`: «Booking», «CD» y 10 cifras, y «has been submitted
    successfully». La lee `referencia_tras_envio` como el número, con sus reintentos de 15 s (`_leer_tras_envio`). La
    frase va en ASCII (cifras 0-9, sin el plegado de mayúsculas de Unicode), con «Booking» sin nada pegado delante y
    sus palabras en una misma línea. Con ese patrón, el del programa, la sonda vuelve a dar 1 de 65 y 0 de 1.347.

  Con cualquier duda queda ENVIADA – REVISAR EN PORTAL. Sin la frase, el motivo dice «la pantalla no mostró que la
  reserva se enviara». Antes decía «el programa todavía no sabe reconocer la confirmación».
- **Una lectura que falla después de pulsar** (el navegador que cierra «Detener» en medio de la espera del número o de
  la frase) queda como una falla del programa después del envío: ENVIADA – REVISAR EN PORTAL, y log.txt lo dice. Hasta
  ahí, la excepción salía del reservador y la fila quedaba DETENIDO o ERROR con el envío ya hecho. Pasaba también en
  ONE, MSC, HYUNDAI y MAERSK; en COSCO, desde este encargo, en sus 15 s de espera de la frase.
- **El detalle,** que llega a log.txt y a la planilla:

  > COSCO: se pulsó «Submit» y la página dijo «Booking … has been submitted successfully». COSCO manda el número de la
  > reserva por correo, en un aviso y en la confirmación: confírmalo ahí y anótalo en la planilla.

  Lleva la referencia que mostró la página. No va en la columna del número: no se sabe si es el número de la reserva
  (abajo, la pregunta). El detalle no trae «error» ni «revisar», porque el registro del panel pintaría la línea como una
  alerta (`clase`). Una prueba lo corre en Node.
- **El mismo estado en los tres lugares:**

  | Dónde | Qué dice |
  |---|---|
  | log.txt | «✅ EMITIDA – CONFIRMAR POR CORREO · …» y «Reserva N: EMITIDA – CONFIRMAR POR CORREO (…)» |
  | Planilla, columna de estado | «EMITIDA – CONFIRMAR POR CORREO · …» |
  | Planilla, columna del número | «confirmar por correo» (`CONFIRMAR_POR_CORREO`, de `_texto_n_reserva`) |
  | Panel | `lecturaEstado` la lee por el mismo texto, que el JavaScript repite y su prueba compara. Pinta «emitida – confirmar por correo», con «confirmar por correo» en la columna, y la cuenta como emitida |

  La consola escribe «SOLICITUD N · EMITIDA – CONFIRMAR POR CORREO · …», como cualquier estado.
- **El «Reminder», un paso normal:**
  - log.txt dice a los cuántos segundos de esperar el resultado aparece («es un paso normal de COSCO, que recuerda
    enviar los documentos antes de su plazo») y deja de verse, y si el programa pulsó su Submit. Dice «deja de verse» y
    no «se cierra»: si las dos lecturas fallan, tampoco se ve.
  - El aviso de que no identificó su Submit termina en «y sigo esperando».
  - El programa sigue intentando pulsar ese Submit una vez, como decidió Marcelo en
    `CICLO-revision-corrida-completa.md`. Si eso debe seguir, va como pregunta, abajo.
- **Al cumplirse el plazo de 180 s, la espera vuelve a leer los errores una vez.** Con la ventana o la carga abiertas
  hasta el final, no se habían leído en las últimas vueltas, y el estado nuevo no puede decidir sin ellos. Van como
  aviso del portal, nunca como errores de campo: al plazo no se sabe si COSCO creó la reserva, y NO ENVIADA invitaría a
  repetirla. Queda ENVIADA – REVISAR EN PORTAL, como antes de este encargo.

### CMA-CGM: FRENO

Lo que muestra su página tras el envío (`numero_cma.py`, con formas y no valores; control: la página trae «Booking
enviado»):
- un solo texto con forma de número, tres letras y 7 cifras, en el enlace de `.booking-ref` de la tarjeta
  `card-route booking-submitted`;
- al lado, «EN PROCESO» y «aún no está confirmada».

De los 82 HTML de CMA de este equipo, 0 traen «Booking enviado»: ninguna corrida de aquí emitió en CMA. Con una sola
muestra, sin el número que vio el portal, y con la propia página diciendo que no está confirmada, **CMA-CGM sigue en
ENVIADA – REVISAR EN PORTAL** (lo pide el encargo).

### Revisión de código

`code-reviewer`, en el clon de trabajo, con el ítem (a) sobre una versión anterior de la guarda. Su worktree de arranque
quedó vacío. Corrió 147 pruebas, el censo del bloque e77 (28 mutaciones, 38 pares) y 10 mutantes propios. **Veredicto:
APROBAR**, con siete LOW:

| Hallazgo | Qué hice |
|---|---|
| 1. La frase se lee en la página y en todos sus marcos; un marco viejo con la frase valdría para la fila nueva (no construyó el caso: cada fila hace `page.goto`) | Al RESIDUAL, con el 5 de seguridad |
| 2. Ninguna prueba cubría el plazo vencido con la máscara de carga (su mutante «solo con la ventana» sobrevivía) | **Arreglado:** `test_al_agotarse_con_la_carga_lee_los_errores` y su mutación |
| 3. Dos mutantes triviales sobrevivían: «Booking» pegado a la referencia y una letra pegada al final | **Arreglado:** dos casos más en `test_cosco_solo_con_la_forma_medida` y sus mutaciones |
| 4. `CLAUDE.md` decía «la primera emisión real de CMA-CGM no ocurrió» y debajo «la primera ocurrió… con COSCO» | **Arreglado:** «no ocurrió en este equipo» y «ocurrió el 2026-10-22, en el equipo de un colega, en una corrida que también emitió una de COSCO» |
| 5. «a los N s» es el contador de la espera, y «se cerró» sale también si las dos lecturas fallan | **Arreglado:** «a los N s de esperar el resultado» y «dejó de verse» |
| 6. Se sigue intentando pulsar el Submit del «Reminder» | Pregunta 3 |
| 7. La cabecera de `test_envio` no nombraba el estado nuevo, y un comentario decía «nunca EMITIDA» | **Arreglado** |

### Revisión de seguridad

`security-reviewer`, en un clon nuevo con el ítem (a) ya sobre el commit del ítem (b) y con lo de la revisión de código.
Su worktree de arranque quedó vacío. Corrió 142 pruebas y siete sondas con páginas falsas. **Veredicto: APROBAR CON
CAMBIOS**: «no encontré un camino concreto para que el estado nuevo salga sin que se haya pulsado Submit».

| Hallazgo | Qué hice |
|---|---|
| **1 (MEDIUM).** Al plazo de 180 s, con la máscara de carga y sin la ventana, un error de campo dejaba la fila NO ENVIADA («vuelve a correrla»). Antes de este encargo, ese caso daba REVISAR | **Arreglado:** al plazo, los errores van como aviso del portal (REVISAR). Las dos pruebas del plazo, al día, y su mutación |
| **2 (MEDIUM).** Un error de campo junto con la frase de éxito da NO ENVIADA, por la regla de antes (validación → NO ENVIADA) | Pregunta 4: es una regla de Marcelo (`CICLO-estado-tras-envio.md`) |
| **3 (MEDIUM).** «Detener» en la espera nueva de 15 s dejaba DETENIDO con el Submit ya pulsado; en ONE pasaba desde antes | **Arreglado:** una lectura que falla después de pulsar es una falla del programa: ENVIADA – REVISAR. Su prueba (COSCO y ONE) y su mutación |
| **4 (LOW).** La frase era más laxa que lo medido: «Rebooking», «Pre-Booking», partida en líneas, cifras de Unicode, la «ſ» o la «K» de los kelvin | **Arreglado:** ASCII, «Booking» sin nada pegado delante y espacios en la misma línea. Sus casos y sus mutaciones; la sonda, con el patrón del programa, sigue en 1 de 65 y 0 de 1.347 |
| 5 (LOW). La frase no se ata a este Submit: la misma pantalla para dos filas daría el estado nuevo dos veces (no construyó el caso en el flujo real) | Al RESIDUAL: leerla antes de pulsar y descartarla si ya estaba |
| 6 (INFO). El panel la pinta y la cuenta como una emitida | Es la decisión de Marcelo («EMITIDA – …») |
| 7 (INFO). El Submit del «Reminder» | Pregunta 3 |
| Verificado sin hallazgo: la referencia no puede inyectar nada en la planilla (celdas de texto) ni en el panel (`esc`, `textContent`); nada corre antes de la guarda y `test_candado` no cambió; CMA no tiene lectura nueva sin plazo; 0 datos reales, 0 invisibles, sin BOM ni CR | Nada |

## Las suites

Con `suite_sin_tope.py`, que corre `tests/correr.py` tal cual con el tope de unittest en 3.600 s. El equipo estuvo
despierto (pedido a la app). No es una medición de tiempo: corrían censos a la par.

| Commit | Suite, sobre su árbol | Censos |
|---|---|---|
| `90d2281` (b) | **867 pruebas, OK** en 1.538 s; la foto de los originales, sin cambios (5.583 entradas) | En el clon de revisión, idéntico byte a byte: la guarda, 64 mutaciones y 70 pares; `_extraer_bkg_limpio`, 6 y 7. Todas muerden |
| `719280c` (a) | **880 pruebas, OK** en 843 s; los originales, sin cambios | En el repo: test_envio, 198 mutaciones y 237 pares; la foto de `test_datadome`, 38 y 51; `numero_tras_envio` y la frase, 37 y 43; el bloque e77, 50 y 62. Muerden todos menos un par (abajo); después de arreglarlo, las 21 de la frase, 25 pares, todos muerden |

- **Una mutación mía no mordía en el primer censo final:** `e77-cosco-salto-de-linea` cambia el espacio entre
  «Booking» y la referencia, y la prueba de `test_booking` que le asigné prueba el salto de línea después de la
  referencia. Ahora cada una va con su prueba (`e77-cosco-salto-de-linea-despues`), y el censo de las 21 de la frase dio
  25 pares, todos muerden. Ninguna prueba de la suite lee `tests/mutaciones.py`, así que la suite no cambió con eso.
- **Las compuertas de cada commit:**
  - la sonda de secretos, con `--dry-run` y sobre el índice;
  - el barrido de valores reales, sobre lo agregado y sobre el mensaje del commit;
  - la guarda del hook pre-commit.

  Las cuatro, en 0, salvo la línea «AquaChile» del ítem (b): ver los defectos.
- **Este informe va en un commit aparte.** Solo lo lee la guarda de datos reales, y la corre el hook sobre el índice de
  ese commit.

## Decisiones que tomé solo

| Decisión | Por qué |
|---|---|
| El estado nuevo exige la frase de éxito, no solo «sin error» | «Ante cualquier duda, REVISAR»: una página que no muestra nada (una carga que no termina, un plazo vencido) no es una reserva creada |
| La frase con su forma medida: «CD» y 10 cifras | Con una muestra, la forma estrecha deja en REVISAR lo que no calce, que es el lado seguro. La guarda, al revés, la toma ancha, que también es el lado seguro: frenar de más |
| La referencia en el detalle, no en la columna del número | No se sabe si es el número de la reserva o el de la solicitud (pregunta) |
| `pulsado` tiene que ser True, y sin una falla del programa después | Con None el clic pudo no salir, y con una falla no se sabe qué vio la página |
| Volver a leer los errores al cumplirse el plazo, y que vayan como aviso del portal | Sin eso, el estado nuevo podía decidir sin haberlos leído en las últimas vueltas; como errores de campo darían NO ENVIADA, que invita a repetir una reserva que pudo crearse (1 de seguridad) |
| Una lectura que falla después de pulsar, ENVIADA – REVISAR en las seis navieras, no solo en COSCO | Es la misma falla para todas, y lo seguro con el clic ya dado es REVISAR (3 de seguridad); en ONE, MSC, HYUNDAI y MAERSK cambia lo que pasaba si «Detener» llegaba en su espera del número |
| Endurecer la frase (ASCII, sin «Rebooking», en una línea) | Lo que no calce queda en REVISAR, el lado seguro, y la frase medida sigue calzando (4 de seguridad) |
| No dejar de pulsar el Submit del «Reminder» | Lo decidió Marcelo; la evidencia nueva dice que no hizo falta, pero no que pulsarlo dañe. Va como pregunta |
| Ensanchar las formas de CMA y COSCO en la guarda (F3 y F4) y aceptar el escape de un literal (F1) | Una guarda de lo publicado frena de más antes que de menos. Medido: 0 hallazgos nuevos en lo versionado |
| «Booking:» como etiqueta (F2), y no un prefijo más ancho para MAERSK | La etiqueta cubre la forma con que el programa escribe una EMITIDA. `2\d` y 7 cifras chocaba con el número público de la cuenta noreply del dueño (medido por la revisión) |

## Defectos de instrumento que me cacé

1. **La sonda de la frase dejó 897 HTML sin leer** en su primera corrida: usaba una sola página del navegador, y una
   rota tapaba a todas las siguientes. Su «0 calces» de `logs/` no valía. Con una página por archivo: 0 sin leer.
2. **La misma sonda traía su propia copia del patrón** de la frase. Al endurecerlo, la copia ya no medía lo que corre:
   ahora lo lee de `AQUASHIELD.py` con `ast`, como el JavaScript.
3. **`python -I` no ve los paquetes del usuario:** la sonda no encontró Playwright. La corrí con `-P`, que no pone la
   carpeta del script en la ruta.
4. **Volví a escribir barras invertidas por Bash** (un bloque de mutaciones por heredoc), contra la fila de «Entorno»:
   `\\b` quedó como un retroceso. Lo vi antes de correr nada y lo reescribí con Edit. Es la quinta vez en estos
   encargos.
5. **Una constante con el nombre de otra:** `LP`, en `tests/mutaciones.py`, nombra más abajo otra clase de pruebas. Mis
   mutaciones apuntaban a pruebas que no existen, y el censo lo dijo. Va con su propio nombre, `LP_E77`.
6. **No corrí `test_datadome` antes del primer censo:** su foto de las lecturas sin plazo que alcanza CMA nombraba
   `numero_tras_envio`, y la lectura pasó a `_leer_tras_envio`. El control del censo lo encontró. La foto está al día y
   exige que CMA no tenga frase.
7. **La sonda que dice qué línea marcó el barrido** importaba la máscara, que trae el arnés de las pruebas, antes de
   correr git, y el arnés bloquea `subprocess`. Corre git primero.
8. **Un `cd` de más** en un comando de prueba: la guardia del `cd` lo frenó antes de correr.
9. **Este informe citaba tres ejemplos inventados** (el contrato de la prueba de HYUNDAI y dos montos con su moneda)
   que la guarda nueva frena, y el hook lo paró. Van descritos, sin el valor: la guarda hace lo que se le pidió.
10. **Dos corridas de la suite y una de los censos se detuvieron a propósito:** las revisiones cambiaron el árbol
   después de lanzarlas. Las que cuentan son las de los árboles commiteados (abajo, «Las suites»).

El barrido de valores reales marcó una línea de `CLAUDE.md` del ítem (b). Era solo la palabra «chile», dentro de
«AquaChile», el nombre de la empresa, que se publica a propósito (`barrido_cual.py`, sin imprimir el valor). Es el mismo
falso positivo que trató el encargo 72.

## Premisas que se refutaron

1. **«COSCO no muestra el número en la página».** Muestra «Booking CD… has been submitted successfully!», con una
   referencia de «CD» y 10 cifras. No se sabe si es el número de la reserva que llega por correo: va como pregunta. El
   estado nuevo no lo trata como número, así que no cambia la decisión.
2. **«El Reminder se cerró solo a los 33 s sin que el programa pulsara nada».** Que no pulsó, lo confirma el log. Que se
   cerró sola, solo lo dice Marcelo: el log no registra el cierre, y sí que la espera terminó a los 34 s con la frase de
   éxito. Desde este encargo, log.txt dice cuándo se cierra.

## RESIDUAL

| Qué | Condición de reapertura |
|---|---|
| **CMA-CGM sigue en ENVIADA – REVISAR EN PORTAL** (FRENO) | Con el número que vio Marcelo en el portal, y su respuesta sobre si «aún no está confirmada» cuenta como emitida |
| **Por qué el programa no encontró la ventana «Reminder»** («sin-ventana» en el marco y en la página) | Sin su HTML no se mide. Si se decide dejar de pulsarla, desaparece |
| **La frase de COSCO está medida en una sola página** | Si COSCO cambia su texto, la reserva queda en REVISAR (el lado seguro). La próxima emisión deja su HTML |
| **La frase no se ata a este Submit y se busca en cualquier marco** (L1 de código, 5 de seguridad): una pantalla vieja con la frase valdría para la fila nueva. Ninguno de los dos revisores construyó el caso, porque cada fila hace `page.goto` y necesita el formulario | Si aparece: leer la frase justo antes de pulsar y descartarla si ya estaba, o leerla solo en el marco del formulario |
| **La regla 3 de `_extraer_bkg_limpio` sigue en 27** (L4 de código) | Si algún día la EMITIDA de MAERSK se escribe sin «Booking:» |
| **Un número partido por un invisible, o con cifras de ancho completo, pasa la guarda** (F5 de seguridad, de antes) | Si aparece un caso; el arreglo es borrar los invisibles en vez de cambiarlos por un espacio |
| **Un número de MAERSK con otro prefijo y sin etiqueta pasa la guarda** | Si MAERSK cambia otra vez de prefijo: se agrega el prefijo medido |

## Preguntas para Marcelo

1. **¿La referencia «CD» y 10 cifras que muestra COSCO es el número de la reserva?** Si lo es, puede ir en la columna
   del número y el estado ser EMITIDA. Si es la de la solicitud, queda como está.
2. **CMA-CGM:** ¿qué número viste en el portal para la reserva del 22-10? ¿Calza con lo que mostró su página, tres
   letras y 7 cifras? ¿Una reserva que el portal dice «aún no está confirmada» cuenta como EMITIDA?
3. **El «Reminder» de COSCO:** el 22-10 se cerró sin que el programa pulsara nada, y la reserva quedó creada. ¿Sigo
   intentando pulsar su Submit una vez, como decidiste en `CICLO-revision-corrida-completa.md`, o dejo solo de esperar?
4. **Un error de campo junto con la frase de éxito** (revisión de seguridad, hallazgo 2). Hoy da NO ENVIADA, por tu
   regla de `CICLO-estado-tras-envio.md`: con errores de validación, el envío no salió. Si la frase es real, la reserva
   existe, y NO ENVIADA invita a repetirla. ¿Lo cambio a ENVIADA – REVISAR EN PORTAL solo cuando las dos señales se
   contradicen? No hay medición de que el portal muestre las dos a la vez.

## Re-medir

1. `python <e77>/barrido_reservas.py <guarda_datos.py> [--antes <otra guarda>]`: los números reales de `logs/` y de la
   evidencia, contra una guarda.
2. `python <e77>/muestras_contra_reales.py <guarda_datos.py>`: las muestras del detector, contra los números reales.
3. `python <e77>/sonda_exito_cosco.py`: la frase de COSCO (`FORMA_ENVIADA` del programa) y los errores en los HTML de
   la evidencia y de `logs/`; y `python <e77>/probar_frase.py`: la frase contra textos inventados.
4. `python <e77>/textos_evidencia.py` y `python <e77>/numero_cma.py`: los textos de COSCO y de CMA tras el envío.
5. Desde `tests/`: `python -m unittest test_guarda_datos test_booking test_envio test_planilla
   test_web.TestPanelPlanilla`; y `python tests/correr.py --mutaciones --filtro e77`.

`<e77>` es la carpeta del encargo en el scratchpad de la sesión. No se versiona, porque las sondas leen `logs/` y la
evidencia del colega, que son datos reales. Ninguna imprime un valor: solo cuentas y formas.

## NO retroceder

- **COSCO llega a EMITIDA – CONFIRMAR POR CORREO solo con la frase de éxito, sin errores y sin dudas del clic.**
  Quitar una condición deja pasar una reserva que no se sabe si se creó.
- **El estado nuevo nunca es EMITIDA a secas, y su referencia no va a la columna del número,** mientras Marcelo no diga
  que es el número.
- **La guarda ve los números con letras detrás del escape de un literal, y «Booking:» es etiqueta:** las pruebas
  guardan textos de página en literales, y el programa escribe así una EMITIDA.
- **Después de pulsar, nada que dude termina en NO ENVIADA ni en DETENIDO:** los errores que se leen al cumplirse el
  plazo van como aviso del portal, y una lectura que falla es una falla del programa después del envío (ENVIADA –
  REVISAR EN PORTAL). NO ENVIADA invita a repetir una reserva que pudo crearse.

## Reglas de método aplicadas

`metodo-ciclo` v37:
- re-medir contra HEAD; el universo sacado de los datos, no de la guarda;
- control positivo que aborta (las seis sondas), con su cero junto a «0 descartados» (0 HTML sin leer);
- se mide sobre el camino real: el JavaScript del programa, en Chromium, sobre el HTML guardado;
- el negativo tiene que morder (los censos); una guarda de lo publicado se cruza con los datos reales del equipo, solo
  con cuentas;
- los revisores, en un clon sin remoto y de a uno; todas las suites antes de cada commit;
- las premisas refutadas, el RESIDUAL, la base, el push (repo público: se entrega el bloque) y el cierre sin esperas
  vivas.

Las del módulo: `test_candado` sin cambios, ningún dato real en lo versionado, y la sonda de secretos y la guarda antes
de cada commit. No chocaron.
