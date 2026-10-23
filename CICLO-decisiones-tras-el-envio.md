# Encargo 78 · Las cuatro decisiones de Marcelo sobre lo que pasa después del envío

**Fecha:** 2026-10-22 y 23 · **Método:** `metodo-ciclo` v38, en Modo autónomo (por omisión).

Base: `Agendamiento Reservas` @ `e1c218b` · árbol limpio (los tres commits del encargo 77, sin subir; `origin/main` en
`abadb88`).

**Commits,** en `main` y sin push (el repo es público: el bloque lo lleva Marcelo):
- `b71e804`, las cuatro decisiones y lo que pidieron sus dos revisiones;
- el de este informe.

## Las decisiones de Marcelo, en sus palabras

Después del encargo 77, Marcelo contestó sus cuatro preguntas (aclaradas en esta sesión, con sus palabras):

1. **La referencia «CD» y 10 cifras de COSCO es el número de la reserva:** lo vio en su correo de confirmación. Va a la
   columna «N° de reserva emitida», en el panel y en la planilla. El estado sigue siendo EMITIDA – CONFIRMAR POR CORREO.
2. **CMA-CGM con «aún no confirmada» queda EMITIDA – CONFIRMAR POR CORREO, como COSCO,** con su número: el que vio en
   el portal calza con el que mostró su página (tres letras y 7 cifras).
3. **El Submit del «Reminder» de COSCO no se pulsa.** Solo eso: el estado lo sigue decidiendo la frase de envío.
4. **Un error de campo junto con la frase de éxito pasa a ENVIADA – REVISAR EN PORTAL,** no a NO ENVIADA.

«Hazlo como ciclo aparte, con su prueba en las dos direcciones.»

## PASO 0

- **El registro:** `CLAUDE.md` y el informe del encargo 77 decían que CMA-CGM seguía en REVISAR (FRENO), que la
  referencia de COSCO no iba a la columna del número, que el programa seguía intentando pulsar el Submit del «Reminder»
  una vez, y que errores de campo daban NO ENVIADA aunque la frase estuviera.
- **Re-medí contra HEAD (`e1c218b`):** la página de CMA-CGM tras el envío, con el JavaScript del programa (abajo).
- **Veredicto:** las cuatro, **CICLO**. Son decisiones de Marcelo, y lo técnico que queda (cómo reconocer la página de
  CMA-CGM) se midió.

## (2) CMA-CGM: lo medido

`sonda_cma_frase.py`: el `_JS_TEXTO_VISIBLE` del programa, leído de `AQUASHIELD.py` con `ast`, en un Chromium sin red y
sin el JavaScript de la página, sobre los HTML de CMA-CGM de la evidencia del colega y de `logs/` de este equipo. Imprime
cuentas y formas, nunca valores.
- **Control positivo:** el HTML del envío del colega trae «Booking enviado»; si no, aborta. Pasó.
- **Universo:** 45 HTML de la fila de CMA-CGM del colega y 409 de CMA-CGM en `logs/`; **0 sin leer**.
- **Cómo se ve la página tras el envío:** una línea «Booking Booking enviado»; el aviso de que la reserva «aún no está
  confirmada»; y una línea que trae solo «Booking» y la referencia (tres letras y 7 cifras). La referencia **no** va en
  la misma línea que «Submitted»: los dos patrones que la buscaban así (el que pensé desde el encargo 77) no calzan.
- **La regla** (`FORMA_ENVIADA["cma"]`, leída del programa por la sonda): las dos señales, atadas después de las dos
  revisiones (abajo). Calza en 1 de los 45 del colega (el del envío) y en 0 de los 409 de `logs/`, igual que sus dos
  versiones anteriores. La página del envío muestra 1 referencia distinta.
- La referencia suelta («Booking» y tres letras y 7 cifras, en cualquier lugar) también calza solo ahí, pero una sola
  señal es más fácil de encontrar en otra pantalla: la regla pide las dos.
- **Tiempo** (`tiempo_regla_cma.py`, con la regla y `REFERENCIAS_ENVIADA` leídas del programa): con 3 a 6 millones de
  caracteres armados para el retroceso (el título repetido sin referencia, casi-títulos, casi-referencias, una línea
  larga, solo saltos de línea), de 0,09 a 0,43 s, y todas las referencias de 0,06 a 0,14 s. Crece lineal.

## El cambio

En `AQUASHIELD.py`, `CLAUDE.md`, `tests/` (test_envio, test_booking, test_planilla, test_web, test_datadome) y
`tests/mutaciones.py`.

**(1) El número a la columna.**
- El detalle de EMITIDA – CONFIRMAR POR CORREO lleva la referencia como «(Booking: …)»:
  «COSCO: se pulsó «Submit» y la página dijo que la reserva se envió (Booking: …). Falta su confirmación: revisa que
  llegue por correo, con ese número.»
- `_extraer_bkg_limpio`, con ese estado, toma solo el número de ese «(Booking: …)», sin las reglas sueltas de la
  EMITIDA. Así llega a la columna «N° de reserva emitida» del panel (`n_reserva`) y de la planilla.
- Un detalle sin él, como los del encargo 77, sigue con «confirmar por correo».
- Con su número, la planilla pinta el número y el estado en verde, como una EMITIDA y como el panel.

**(2) CMA-CGM.**
- `FORMA_ENVIADA["cma"]` pide las dos señales en el texto visible y en ese orden:
  - la línea del título, que trae solo «Booking enviado» o, como la medida, «Booking Booking enviado» (la primera, con
    un grupo atómico);
  - después, una línea que trae solo «Booking» y la referencia (`[A-Z]{3}[0-9]{7}`), en ASCII.
- `reservar_cma` ya pasaba `plazo_ms` a `_resultado_envio`. Ahora `numero_tras_envio`, `referencia_tras_envio` y
  `_leer_tras_envio` lo reciben y leen con plazo.
- `_leer_tras_envio`:
  - no vuelve a leer un alcance que no contestó a su plazo;
  - no lee el marco principal aparte de la página.
- Con la página de CMA-CGM colgada, la lectura habría tardado unos 16 minutos por fila. Con 3 vueltas, ahora son 5
  lecturas en vez de 12.

**(3) El Reminder.** Salieron `_JS_COSCO_SUBMIT_DEL_REMINDER` y `_cosco_pulsar_reminder`. `_cosco_esperar_resultado`
solo espera, y log.txt dice «No pulso nada y sigo esperando» y cuándo deja de verse la ventana.

**(4) La contradicción.** Con errores de campo y el clic dado o a medio dar, `_resultado_envio` lee una vez, sin espera,
el número o la frase.
- Si está, queda ENVIADA – REVISAR EN PORTAL, con las dos señales en el motivo.
- Si no está, o si la lectura falla, queda NO ENVIADA, como antes.

**De la revisión de seguridad.** Dos casos más quedan ENVIADA – REVISAR EN PORTAL, con su motivo:
- la pantalla muestra más de una referencia distinta (`REFERENCIAS_ENVIADA`, `ReferenciaAmbigua`);
- la referencia ya dio una EMITIDA – CONFIRMAR POR CORREO en la misma corrida (`Registro.referencias_enviadas`).

`test_candado` no cambió.

## Las pruebas, en las dos direcciones

| Decisión | Cuando sí | Cuando no |
|---|---|---|
| 1, el número a la columna | La referencia de COSCO y la de CMA-CGM van a `_texto_n_reserva` y a la planilla, en verde (`test_cosco_enviada_…`, `test_cma_con_booking_enviado_…`, `test_emitida_por_correo_se_pinta_como_emitida`, `test_web_descarga_de_emitida_por_correo`, `test_numero_de_reserva_igual_…`) | El detalle del encargo 77 sigue con «confirmar por correo»; otro estado con el mismo detalle, sin número; dos referencias distintas, sin número (`test_dos_numeros_distintos_no_deciden`) |
| 2, CMA-CGM | Las dos señales, en la página o en un marco, con plazo (`test_frase_de_cma_…`, `test_la_frase_de_envio_con_plazo`, `test_la_frase_en_un_marco_y_un_marco_colgado`) | Una sola señal, la referencia con más texto o antes del título, el título en una frase, «enviados», otra forma, minúsculas: 16 casos en `test_booking` y 6 en `test_envio`, ninguno calza |
| 3, el Reminder | La espera sigue y termina con la frase (`test_reminder_no_se_pulsa`, `test_reminder_tardio_tampoco_se_pulsa`, `test_reminder_que_vuelve_…`) | Un JavaScript que pulse, o un localizador, hace caer la prueba (la página falsa los anota); `cosco-reminder-vuelve-a-pulsar` y `cosco-reminder-busca-su-submit` lo comprueban |
| 4, la contradicción | Errores y la frase, o el número, o dos referencias, también con el clic a medio dar: REVISAR (`test_errores_de_campo_con_la_frase_son_enviada`) | Errores sin la frase, sin espera; la lectura que falla; el botón que no estaba: NO ENVIADA |

## Las revisiones

### Revisión de código (`code-reviewer`, en un clon sin remoto, sobre `a8c61b9` del clon)

Veredicto: **APROBAR CON CAMBIOS**, sin CRITICAL ni HIGH. Corrió los cuatro módulos que podía (181 pruebas, OK) y las 35
mutaciones tocadas por el cambio: 58 de 58 pares muerden. Lo que encontró y qué hice:

| # | Severidad | Hallazgo | Qué hice |
|---|---|---|---|
| 1 | MEDIUM | Un párrafo de `CLAUDE.md` («Planilla Excel») seguía diciendo que solo una EMITIDA lleva número; dos comentarios de `test_booking` igual | Reescritos |
| 2 | LOW | La contradicción (decisión 4) solo se ve si la frase ya está cuando se leen los errores: COSCO sale de su espera apenas los ve, a unos 3 s | Queda como pregunta: cubrirlo es esperar más en cada fila rechazada |
| 3 | LOW | Las dos señales de CMA-CGM no estaban atadas: «Su Booking enviado ayer» y la referencia antes del título también calzaban | La regla pide «Booking enviado» al final de su línea y la referencia después. Medido: 1 de 45 y 0 de 409, como antes; lineal (0,11 s con 3,2 millones de caracteres armados) |
| 4 | LOW | Con la página de CMA-CGM colgada, la lectura de la frase podía tardar unos 16 minutos por fila (cada vuelta, cada alcance, su plazo entero; y el marco principal leído dos veces) | Un alcance que no contestó a su plazo no se vuelve a leer, y el marco principal no se lee aparte. Con 3 vueltas, 5 lecturas en vez de 12 |
| 5 | LOW | Tres mutantes suyos vivían: la contradicción sin el clic a medio dar, «enviados», y los marcos leídos sin plazo | Pruebas nuevas y sus mutaciones (`e78-campos-sin-el-clic-a-medio-dar`, `e78-cma-enviado-a-mitad-de-linea`, `e78-marcos-sin-plazo`); el docstring de la página falsa de COSCO dice cómo reconoce cada JavaScript |
| 6 | LOW | La planilla pinta ahora en verde la EMITIDA – CONFIRMAR POR CORREO con número, sin que nada lo diga ni lo pruebe | Se queda en verde, como la pinta el panel; probado (`e78-planilla-correo-sin-verde`) y escrito en `CLAUDE.md` |
| 7 | LOW | El detalle decía «CMA la confirma por correo»: no está medido | Dice «Falta su confirmación: revisa que llegue por correo, con ese número», el nombre del estado que decidió Marcelo |

### Revisión de seguridad (`security-reviewer`, en el mismo clon, sobre `9ee43fd` del clon, con los arreglos de arriba)

Veredicto: **APROBAR CON CAMBIOS**, sin CRITICAL ni HIGH. Corrió los cuatro módulos (182 pruebas, OK), sondas propias
sobre las reglas y sobre un Chromium sin red (qué cuenta como texto visible, `page.main_frame is page.frames[0]` en
Playwright 1.58, la página ocupada en un bucle). Pidió M1 y M2 antes de subir:

| # | Severidad | Hallazgo | Qué hice |
|---|---|---|---|
| M1 | MEDIUM | Con varias referencias distintas en la pantalla, ganaba la primera, y esa iba a la columna del número | Si la página o sus marcos muestran más de una referencia distinta con la forma de la naviera (`REFERENCIAS_ENVIADA`), ENVIADA – REVISAR EN PORTAL con todas (`ReferenciaAmbigua`). La misma dos veces no es ambigua. Medido: la página del envío del 22-10 muestra 1 |
| M2 | MEDIUM | Nada distinguía lo que la página dijo por este envío de lo que ya decía: la misma pantalla daría el mismo número a dos filas | Una referencia que ya dio una EMITIDA – CONFIRMAR POR CORREO en esta corrida (`reg.referencias_enviadas`, una por `Registro`) queda ENVIADA – REVISAR EN PORTAL, con la evidencia de la anterior. Leer la pantalla antes del clic, no: queda en el RESIDUAL |
| M3 | MEDIUM | El punto ciego de COSCO con errores de campo (el 2 de la revisión de código) | Pregunta para Marcelo |
| L1 | LOW | Con errores de campo, una lectura que falla da NO ENVIADA; en la rama normal, REVISAR | Queda así: el portal sí mostró sus errores, y la regla de Marcelo de `CICLO-estado-tras-envio.md` es NO ENVIADA. RESIDUAL |
| L2 | LOW | Cuenta un marco de cualquier origen | RESIDUAL: filtrar por el host de la naviera |
| L3 | LOW | El título de CMA-CGM no estaba atado al principio de su línea («Error: Booking enviado», «éBooking enviado») | La línea del título trae solo «Booking enviado» o «Booking Booking enviado», como la medida. Medido otra vez: 1 de 45 y 0 de 409; lineal, de 0,1 a 0,5 s con 3 a 6 millones de caracteres armados. El comentario de COSCO dice ahora que la letra pegada que mira es ASCII |
| L4 | LOW | `_extraer_bkg_limpio` toma el primer «(Booking: …)» del detalle | Hoy el programa lo pone primero; RESIDUAL |

## Las suites

Sobre el árbol de `b71e804`, en el repo, una corrida después de la otra (dos a la vez se cruzan en los puertos de
`test_web`). El equipo estuvo despierto (pedido a la app). No es una medición de tiempo.

| Corrida | Resultado |
|---|---|
| Suite completa (`suite_sin_tope.py`: `tests/correr.py` con el tope de unittest en 3.600 s) | **884 pruebas, OK**, en 2.190 s; los originales, sin cambios (5.584 entradas) |
| Censo, filtro `test_envio` | 219 mutaciones, 277 pares: muerden todos menos uno (abajo) |
| Censo, filtro `test_booking` | 60 mutaciones, 76 pares: muerden todos menos el mismo |
| Censo, filtro `test_datadome.TestLecturasConPlazo` | 47 mutaciones, 66 pares: todos muerden |
| Censo, filtro `test_planilla` | 73 mutaciones, 121 pares: todos muerden |
| Censo, filtro `test_web.TestPanelPlanilla` | 18 mutaciones, 35 pares: todos muerden |

- **Un par no mordía:** `e78-cma-enviado-a-mitad-de-linea` contra `test_cma_con_booking_enviado_es_emitida_por_correo`.
  Después de atar el título al principio de su línea (L3), quitar el ancla del final ya no deja pasar «Su Booking
  enviado ayer», el caso de esa prueba. La mutación sigue mordiendo con el caso «enviados» de `test_booking`. Le quité
  esa prueba, y su censo dio 1 de 1. Ninguna prueba lee `tests/mutaciones.py`: la suite no cambia con eso.
- Censo estático de la revisión de código: 0 pruebas sin mutación, 0 nombradas que no existen, 0 ids repetidos.
- **Las compuertas del commit, todas en 0:**
  - la sonda de secretos, con `--dry-run` y sobre el índice;
  - el barrido de valores reales, sobre las 764 líneas agregadas y sobre el mensaje;
  - la guarda del hook pre-commit, con 0 hallazgos.
- Este informe va en su propio commit, con la guarda del hook y las mismas compuertas.

## Decisiones que tomé solo

| Decisión | Por qué |
|---|---|
| CMA-CGM con dos señales atadas, en mayúsculas como el portal | Una sola muestra: la forma estrecha deja en REVISAR lo que no calce, el lado seguro |
| La columna toma el número solo del «(Booking: …)» que escribe `_resultado_envio`, y solo con este estado | Las reglas sueltas de `_extraer_bkg_limpio` (cualquier «Booking …») tomarían la referencia del detalle del encargo 77, que no la dice como número; y otro estado con el mismo detalle no tiene número |
| Un detalle del encargo 77, sin «(Booking: …)», sigue con «confirmar por correo» | Ningún resultado viejo cambia: el panel guarda los resultados en memoria, y una planilla descargada no se vuelve a escribir |
| Con errores de campo, una sola lectura, sin espera | Los errores ya dicen algo; esperar 15 s la frase que casi nunca estará retrasa cada fila rechazada (la otra opción es la pregunta 1) |
| Si esa lectura falla, NO ENVIADA, como antes | No hay señal de que se envió, y el portal sí mostró sus errores; la regla de Marcelo de `CICLO-estado-tras-envio.md` sigue para ese caso (L1) |
| CMA-CGM lee su frase con plazo, y un alcance colgado se lee una sola vez | Todo lo de CMA-CGM se lee con plazo (encargo 55); sin eso, una fila con la página colgada tardaba unos 16 minutos |
| La espera de COSCO ya no sabe pulsar: el JavaScript que pulsaba el Submit del «Reminder» y su ayudante salieron | Sin código muerto que alguien vuelva a llamar |
| Dos referencias distintas, o la misma de otra fila de la corrida: ENVIADA – REVISAR EN PORTAL | La columna del número la usa la agencia de aduana: un número equivocado es peor que ninguno (M1 y M2) |
| Esas dos guardas, solo para EMITIDA – CONFIRMAR POR CORREO | Son nuevas con este encargo; para la EMITIDA de las navieras con forma medida, sería cambiar lo que ya andaba (RESIDUAL) |
| La planilla, en verde con el número | Como el panel, que la cuenta como emitida; el estado dice que falta la confirmación |
| Sin una segunda vuelta de las revisiones sobre los arreglos de M1, M2 y L3 | Son los arreglos que pidieron, con sus pruebas y sus mutaciones en el censo; queda dicho aquí |

## Defectos de instrumento que me cacé

1. **La sonda de CMA-CGM medía copias de la regla:** sus candidatos estaban escritos en la sonda. Desde la segunda vuelta
   lee la regla y `REFERENCIAS_ENVIADA` de `AQUASHIELD.py` con `ast` («la-del-programa»), como ya leía el JavaScript.
   Las cuentas de la regla final salen de ahí.
2. **Un script de mutaciones con comillas escapadas dentro de cadenas crudas** (`\'` en `r'''…'''`), que habría dejado
   las barras en el texto. Lo vi antes de correrlo y lo reescribí con otro delimitador. Sus reemplazos exigen calzar una
   sola vez, así que tampoco habría escrito nada.
3. **Una línea nueva igual a otra que ya existía** (la exclusión del marco principal, igual a la de la evidencia): dos
   mutaciones calzaban dos veces. Lo vio la revisión de las mutaciones (`revisar_mutaciones.py`) antes del censo; la
   variable nueva se llama `otros`.
4. **Dos censos detenidos a propósito:** las revisiones cambiaron el código después de lanzarlos. Cerré sus procesos por
   su línea de comandos (`cerrar_censo.py`: 3 en cada uno, 0 vivos después). El que cuenta es el último («Las suites»).

## RESIDUAL

| Qué | Condición de reapertura |
|---|---|
| **La frase de CMA-CGM está medida en una sola página, guardada** (el DOM, sin su JavaScript). Si la página viva parte o junta las líneas de otra forma, la reserva queda en REVISAR (el lado seguro) | La próxima emisión de CMA-CGM deja su HTML: medirlo con `sonda_cma_frase.py` |
| **La frase no se ata a este envío** (del encargo 77, ahora también para CMA-CGM). La memoria de la corrida (M2) cubre la misma pantalla en dos filas; no, la primera fila de una corrida con una pantalla vieja | Si aparece: leerla justo antes de pulsar y descartarla si ya estaba |
| **La frase se busca en cualquier marco, de cualquier origen** (L2) | Si aparece un caso: filtrar por el host de la naviera |
| **El punto ciego de COSCO con errores de campo** (2 de código, M3 de seguridad): la frase que llega después de los ~3 s en que la espera ve los errores no se ve, y la fila queda NO ENVIADA | Pregunta 1 |
| **Con errores de campo, una lectura que falla da NO ENVIADA** (L1) | Si Marcelo prefiere tratarlo como duda |
| **`_extraer_bkg_limpio` toma el primer «(Booking: …)» del detalle** (L4): hoy el programa lo pone primero | Si algo empieza a anteponer texto al detalle |
| **La EMITIDA de ONE, MSC, HYUNDAI y MAERSK no mira dos números ni el número repetido** | Si se decide extender las guardas de M1 y M2 |
| **Que el portal muestre a la vez errores de campo y la frase no está medido** | Si pasa, la fila queda ENVIADA – REVISAR, con los dos en el motivo |
| **El grupo atómico pide Python 3.11 o más** (el programa pide 3.13). Con uno anterior, la regla da un error que `_resultado_envio` deja en ENVIADA – REVISAR | Si algún equipo corre un Python viejo |

## Preguntas para Marcelo

1. **COSCO con errores de campo** (decisión 4): su espera sale apenas ve errores de campo, a unos 3 s del Submit, y lee
   la frase una sola vez. Si COSCO muestra un error y acepta el envío después (el 22-10 la frase llegó a los 33 s), la
   fila queda NO ENVIADA con la reserva creada. ¿Lo dejo así, o, con errores de campo, espero un tramo más la frase
   (unos segundos de más en cada fila rechazada), o lo trato como aviso del portal si el Submit ya no está a la vista?
   No hay medición de que el portal muestre las dos cosas.

## Re-medir

1. `python -P <e78>/sonda_cma_frase.py`: la página de CMA-CGM tras el envío (la evidencia del colega y `logs/`), con la
   regla y `REFERENCIAS_ENVIADA` leídas del programa.
2. `python <e78>/tiempo_regla_cma.py`: la regla con textos armados para el retroceso.
3. Desde `tests/`: `python -m unittest test_envio test_booking test_planilla test_datadome test_web.TestPanelPlanilla`;
   y `python tests/correr.py --mutaciones --filtro e78`.

`<e78>` es la carpeta del encargo en el scratchpad de la sesión. No se versiona: la sonda lee `logs/` y la evidencia del
colega, que son datos reales, y solo imprime cuentas y formas.

## NO retroceder

- **EMITIDA – CONFIRMAR POR CORREO solo con la frase de su naviera, sin errores y sin dudas del clic;** en CMA-CGM, con
  las dos señales.
- **El número de la columna sale solo del «(Booking: …)» de ese estado, y nunca de una pantalla con dos referencias
  distintas ni de una que ya dio el suyo en la corrida.**
- **Lo de CMA-CGM se lee con plazo, y un alcance que no contestó no se vuelve a leer.**
- **Del Submit del «Reminder» no se pulsa nada.**
- **Errores de campo con la frase o el número a la vista: ENVIADA – REVISAR EN PORTAL.** NO ENVIADA invita a repetir una
  reserva que pudo crearse.

## Reglas de método aplicadas

`metodo-ciclo` v38 (la misma del disco al empezar):
- re-medir contra HEAD; la sonda ejecuta el JavaScript del programa, leído de su fuente, sobre el camino real;
- control positivo que aborta, y su cero junto a «0 sin leer»;
- cada decisión, con su prueba en las dos direcciones, y cada prueba, con su mutación (el negativo tiene que morder);
- los revisores, en un clon sin remoto y de a uno; todas las suites antes de cada commit;
- el RESIDUAL, la base, el push (repo público: se entrega el bloque) y el cierre sin esperas vivas.

Las del módulo: `test_candado` sin cambios, ningún dato real en lo versionado, y la sonda de secretos y la guarda antes
de cada commit.
