# Encargo 80 · COSCO con errores de campo: hasta 20 s desde el clic antes de dar NO ENVIADA

**Fecha:** 2026-10-23 · **Método:** `metodo-ciclo` v38, en Modo autónomo (por omisión).

Base: `Agendamiento Reservas` @ `e83cf63` · árbol limpio · `origin/main` también en `e83cf63` (los commits del encargo
79, subidos por Marcelo).

**Commits,** en `main` y sin push (lo pidió el encargo, y el repo es público):
- `acda2ca`, el cambio;
- el de este informe.

## La decisión

Es la opción (b) de la pregunta del encargo 79: con errores de campo, antes de dar NO ENVIADA, esperar hasta 20 s desde
el clic del Submit. Único dato medido: el 22-10, la ventana «Reminder» llegó a los 12 s.
- **NO ENVIADA solo si a los 20 s el Submit sigue a la vista** y no apareció la ventana «Reminder» ni la página de envío.
- **Si aparece cualquiera de las dos antes,** se sigue su camino de inmediato, sin esperar el resto.
- **El camino de COSCO sin errores de campo** no cambia ni espera más.
- **FRENA SI:** el cambio toca el estado de otra naviera, o el camino de COSCO sin errores de campo. No pasó (abajo).

## PASO 0

- **El registro:** hasta este encargo, `_cosco_esperar_resultado` salía con la primera lectura que traía errores de
  campo, a unos 3 s del Submit (`CLAUDE.md`, encargo 79). Sus señales de «COSCO recibió el envío», para dejar de esperar
  sin errores, son `_JS_COSCO_EXITO` y un número (`_cosco_hay_numero`); la del estado es la frase de `FORMA_ENVIADA`.
- **Lo medido** (`sonda_senales.py`): el JavaScript del programa, leído de su fuente con `ast`, en un Chromium sin red,
  sobre los 20 HTML de COSCO del envío del 22-10 y los 120 de `logs/` de este equipo (0 sin leer; 1 carpeta de `logs/`
  saltada por no ser una carpeta común). Control positivo: el documento de después del envío da la frase y
  `_JS_COSCO_EXITO`. Pasó.

  | Señal | Formularios, antes del clic | Después del envío que entró |
  |---|---|---|
  | `_JS_COSCO_EXITO` | **la da** el marco del formulario de la guarda del 22-10 (1 de 20) y 10 de los 120 de `logs/` (dos nombres: el marco del formulario de la guarda) | 1 (el marco del formulario) |
  | Un número (`_JS_COSCO_NUMERO`) | 0 | 0 |
  | La ventana «Reminder» | 0 | 0 (de la ventana no hay HTML) |
  | La frase de `FORMA_ENVIADA` | 0 | 1 (el marco del formulario) |

  - **Por qué `_JS_COSCO_EXITO` la da en el formulario** (`sonda_exito.py`): su texto «booking confirmation sent to» es
    la etiqueta (`label`) de un campo del formulario, sin marca de oculto en el HTML. Después del envío, el que calza es
    «submitted successfully», en un `p`.
  - **LÍMITE:** el HTML guardado no trae las hojas de estilo del portal: lo que `innerText` ve es una cota de más.
- **Los tiempos del 22-10** (`sonda_tiempos2.py`, sobre el log del colega, con las cifras tapadas): el Submit a los
  282,4 s de la corrida, la espera desde los 283,3 s, la ventana «Reminder» a los 295,6 s (12,3 s de reloj después) y la
  evidencia del envío a los 315,7 s (33 s). Esa corrida usaba una versión vieja del programa: su línea de la ventana
  dice otra cosa que la de hoy.
- **Veredicto:** **CICLO**. Dos cosas que decidió la medición:
  - la página de envío, en el tramo, es la frase de `FORMA_ENVIADA`, no `_JS_COSCO_EXITO`: con esa señal el tramo no
    esperaría nunca;
  - el tope se cuenta con el reloj, como el dato de los 12 s, y no con la suma de las esperas.

## El cambio

Solo en la espera de COSCO (`AQUASHIELD.py`), con `CLAUDE.md`, `tests/test_envio.py` y `tests/mutaciones.py`.
`reservar_cosco` y `_resultado_envio` no cambiaron.
- **`COSCO_ESPERA_TRAS_ERRORES_SEG = 20`** (hipótesis), contado con `time.monotonic` desde que la espera empieza, justo
  después del clic.
- **`_cosco_esperar_resultado`**, con errores de campo antes del tope y sin la ventana ya vista, llama a
  `_cosco_tras_los_errores`:
  - con la ventana, la anota y vuelve a la espera, que la sigue como a cualquier ventana: espera mientras siga a la
    vista, y los errores van como aviso del portal (ENVIADA – REVISAR EN PORTAL, como desde el encargo 77);
  - con la página de envío, o al tope, vuelve a leer los errores y sigue con lo que ve: con errores, decide
    `reservar_cosco`, como en el encargo 79 (NO ENVIADA solo con el Submit a la vista); sin ellos, el camino de siempre.
- **`_cosco_tras_los_errores`** mira cada 1,5 s, sin pulsar nada, la ventana y la página de envío; la última vuelta,
  hasta el tope justo. log.txt dice cuándo empieza el tramo y cómo terminó.
- **`_cosco_pagina_de_envio`**: la frase de `FORMA_ENVIADA` (`referencia_tras_envio`, una lectura sin espera); con dos
  referencias, también; si la lectura falla, no.
- **El FRENA SI no se tocó:** el tramo corre solo con errores de campo; con solo un aviso del portal, o sin errores, la
  espera hace lo mismo que antes. Ninguna otra naviera llama a la espera de COSCO.

## Las pruebas

`test_envio.TestCoscoTrasLosErrores` corre de punta a punta **el código real de `reservar_cosco` después de su guarda**
(sacado de su AST, como la foto, y compilado aparte: `despues_de_la_guarda`), del clic al estado, sobre un portal falso
en el tiempo (`PortalCOSCO`): un reloj en milisegundos que avanza solo con las esperas, y lo que muestra cada alcance según
los segundos desde el clic. El marco del formulario da siempre `_JS_COSCO_EXITO`, como lo medido.

| Caso | Resultado | A los |
|---|---|---|
| Errores de campo, el Submit a la vista, ni la ventana ni la página de envío | NO ENVIADA | 20,0 s (hasta el encargo 79, 3 s) |
| Lo mismo, con el Submit ya no a la vista a los 20 s | ENVIADA – REVISAR EN PORTAL, «… ya no está a la vista» | 20,0 s |
| Errores después del tope (la máscara de carga hasta los 21 s) | NO ENVIADA, sin tramo | 22,5 s |
| La ventana de los 9 a los 12 s, en la página o en el marco | ENVIADA – REVISAR EN PORTAL, con los errores como aviso del portal | 13,5 s |
| La ventana en una sola vuelta del tramo | ENVIADA – REVISAR EN PORTAL | 10,5 s |
| La página de envío desde los 10 s, sin errores | EMITIDA – CONFIRMAR POR CORREO, con su número | 10,5 s |
| La página de envío desde los 10 s, con los errores todavía | ENVIADA – REVISAR EN PORTAL, la contradicción del encargo 78 | 10,5 s |
| Sin errores de campo (el FRENA SI) | EMITIDA – CONFIRMAR POR CORREO, sin tramo | 10,0 s, como antes |

Además:
- `TestCosco.test_errores_de_validacion_esperan_hasta_el_tope` (antes `test_espera_corta_con_errores_de_validacion`):
  la espera sola vuelve con los errores a los 20 s justos, en 14 esperas, sin preguntar `_JS_COSCO_EXITO`.
- `test_pagina_de_envio_es_la_frase`: la etiqueta del formulario no es la página de envío; la frase sí, en una lectura
  sin espera; dos referencias, también; una lectura que falla, no.
- `TestCosco.test_espera_corta_con_aviso_del_portal` sigue en 2 esperas: con solo un aviso del portal no hay tramo.

## Las suites

Corridas sobre el árbol del commit `acda2ca`, antes de commitearlo, con `TEMP`, `TMP` y `TMPDIR` en la carpeta del
encargo:

| Corrida | Resultado |
|---|---|
| `test_envio`, `test_datadome` y `test_candado`, antes de la revisión | 154 pruebas, OK (308 s) |
| El censo de las mutaciones e80, antes de la revisión | 19 mutaciones, 26 pares: todos muerden |
| Las pruebas de COSCO, después de los arreglos de la revisión | 17 pruebas, OK |
| El censo de `test_envio` (`correr.py --mutaciones --filtro test_envio`) | 264 mutaciones, 330 pares: los 330 muerden, y los 35 de las 26 e80 entre ellos. Originales: 0 cambios |
| La suite completa (`correr.py`, con el tope de 3.600 s del encargo 76) | 891 pruebas, OK (1.074 s). Originales: 5.585 entradas, 0 cambios |

`tests/mutaciones.py` trae 2.576 mutaciones, y cada una se aplica una sola vez. Las compuertas del commit, en 0: la
sonda de secretos (antes y después de `git add`), el barrido de datos reales sobre lo agregado (462 líneas) y sobre el
mensaje, y la guarda de datos del hook (0 hallazgos).

## La revisión de código

`code-reviewer`, en un clon sin remoto, sobre el commit `9fc08c8` del clon. Veredicto: **APROBAR**, sin CRITICAL, HIGH
ni MEDIUM.
- Corrió `test_envio`, `test_datadome` y `test_candado` (154, OK) y `test_clics`, `test_evidencia` y `test_consola`
  (441, OK, 1 omitida).
- Las 19 mutaciones e80 y la vieja que cambió de prueba: 28 de 28 pares muerden. Las 22 viejas de `TestCosco`, 32 de 32.
- La guarda de datos sobre lo agregado dio 0; sin caracteres invisibles, CRLF ni BOM.
- Con 10 escenarios sobre el portal falso, ninguna fila con errores de campo quedó NO ENVIADA antes de los 20 s ni con la
  ventana o la página de envío vistas, y la espera no puede quedar colgada: el tramo termina con el reloj y la espera
  entera, con sus 180 s.
- Comprobó que la prueba de punta a punta corre el código mutado de `reservar_cosco` en el censo.

| # | Hallazgo | Qué hice |
|---|---|---|
| L1 | La máscara de carga no cuenta en el tramo: con errores de campo, la máscara y el Submit a la vista a los 20 s, NO ENVIADA mientras COSCO sigue procesando. No es una regresión (antes, a los 3 s) | Al RESIDUAL y a `CLAUDE.md`: no está medido que COSCO muestre las dos cosas a la vez, y sumarla como duda cambia la regla de Marcelo |
| L2 | La ventana en el marco del formulario, dentro del tramo, no estaba probada: su mutación (`x7`) sobrevivía. Otras cinco morían por una sola prueba | La prueba de la ventana corre también con la ventana en el marco; 7 mutaciones del revisor al censo (`e80-tramo-sin-mirar-el-reloj`, `-envio-cuenta-como-reminder`, `-tope-estricto`, `-reminder-sin-seguir-su-camino`, `-tramo-sin-sumar-lo-esperado` y la ventana solo en la página o solo en el marco) |
| L3 | Las cifras de la medición no calzaban entre el docstring y `CLAUDE.md`, y `CLAUDE.md` le atribuía el caso del aviso del portal a otra prueba | Alineadas: la frase, en ningún formulario (1 de los 20 HTML del 22-10, el de después del envío; 0 de los 120 de `logs/`); el aviso, `test_espera_corta_con_aviso_del_portal` |
| L4 | La línea de la ventana en el tramo traía «errores», y el registro del panel la pintaba como alerta | Dice «con campos marcados antes», y la prueba exige que el panel la pinte como información |

Notas sin gravedad: el informe que citan el código y `CLAUDE.md` entra en su propio commit; una ventana que dure menos
de 1,5 s entre dos lecturas del tramo no se ve (la del 22-10 duró unos 21 s). No hubo revisión de seguridad: el encargo
pidió la de código. Los arreglos no tuvieron otra vuelta; van con sus pruebas y sus mutaciones en el censo.

## Decisiones que tomé solo

| Decisión | Por qué |
|---|---|
| La página de envío es la frase de `FORMA_ENVIADA`, no `_JS_COSCO_EXITO` | Medido: `_JS_COSCO_EXITO` la da la etiqueta de un campo del formulario, antes del clic. Con ella, el tramo terminaría enseguida y no esperaría nada |
| El tope, con el reloj desde que la espera empieza | El único dato, los 12 s, salió del reloj del log; la suma de las esperas no cuenta lo que tardan las lecturas |
| Con la ventana en el tramo, su camino es el de siempre: esperar mientras siga a la vista | Es lo que la espera hace con la ventana desde el encargo 78; los errores, después, van como aviso del portal |
| Al tope, o con la página de envío, se vuelven a leer los errores | El estado decide con lo que se ve a los 20 s; si los errores ya no están, no es un rechazo |
| `reservar_cosco` y `_resultado_envio`, sin cambios | La decisión del encargo 79 (el Submit a la vista) queda igual; solo cambia cuándo se toma |
| Los errores que llegan después del tope no esperan más | El tope cuenta desde el clic, como pide el encargo |

## Errores propios, y cómo se vieron

| Error | Cómo se vio | Qué hice |
|---|---|---|
| La primera idea de «página de envío» era la señal con que la espera ya deja de esperar (`_JS_COSCO_EXITO`) | La sonda del PASO 0, antes de escribir código: la da el formulario mismo | La frase de `FORMA_ENVIADA` |
| La sonda de los tiempos del 22-10 buscaba la línea de la ventana de la versión de hoy, y abortó | Su control positivo | La segunda sonda lee el tramo del log tal como lo escribió la versión de ese día |
| La página falsa «cerrada» de la prueba tenía una propiedad sin setter, y `PaginaFalsa` la asigna al crearse | Leyendo el código antes de correrla | Un setter que no hace nada |
| La línea de la ventana en el tramo decía «errores», y el panel la pintaba como alerta | La revisión de código (L4) | Otro texto, y una prueba que lo exige |
| No había prueba con la ventana en el marco dentro del tramo | La revisión de código (L2) | La prueba y sus mutaciones |

## RESIDUAL

| Qué | Condición de reapertura |
|---|---|
| **Los 20 s son una hipótesis:** el único dato es la ventana a los 12,3 s del 22-10. Una ventana que llegue después de los 20 s, con errores de campo y el Submit a la vista, deja la fila NO ENVIADA | Un envío con errores de campo que deje su HTML y su log |
| **Que COSCO deje su Submit a la vista cuando rechaza sigue sin medirse** (encargo 79). Si no lo deja, cada rechazo queda REVISAR | La primera fila rechazada con el candado abierto |
| **La máscara de carga no cuenta en el tramo** (L1 de la revisión): con errores de campo, la máscara y el Submit a la vista a los 20 s, la fila queda NO ENVIADA mientras COSCO sigue procesando. No está medido que COSCO muestre las dos cosas a la vez | Un envío así, o una decisión de Marcelo de contarla como duda |
| **Una ventana que dure menos de 1,5 s entre dos lecturas del tramo no se ve** (nota de la revisión). La del 22-10 duró unos 21 s | Una ventana más corta, medida |
| **Sin errores de campo, la etiqueta del formulario da `_JS_COSCO_EXITO`,** y la espera puede dejar de esperar a los 3 s. Después `_resultado_envio` lee la frase hasta 15 s. El 22-10 la frase llegó a los 33 s: si la espera se cortara a los 3 s, la fila quedaría ENVIADA – REVISAR EN PORTAL y no EMITIDA – CONFIRMAR POR CORREO. Ese día, con la versión del colega (de antes del encargo 78: la línea de la ventana de su log la escribía esa versión), la ventana se vio a los 12,3 s, así que esa espera no se cortó a los 3 s. En `719280c^` la espera mira la ventana, la máscara de carga y después `_JS_COSCO_EXITO`, como hoy; si la del colega era igual, la máscara estaba a la vista o la etiqueta no se veía (no se midió). Está fuera del encargo: el FRENA SI prohíbe tocar ese camino | Decisión de Marcelo: mirar ese camino en un encargo propio |

## Re-medir

1. `python -B -P <e80>/sonda_senales.py`: las cuatro señales en los HTML de COSCO del colega y de `logs/`.
2. `python -B -P <e80>/sonda_exito.py` y `sonda_tiempos2.py`: qué texto da `_JS_COSCO_EXITO`, y los tiempos del 22-10.
3. Desde `tests/`: `python -m unittest test_envio.TestCoscoTrasLosErrores test_envio.TestCosco`; y
   `python tests/correr.py --mutaciones --filtro e80`.

`<e80>` es la carpeta del encargo en el scratchpad de la sesión. No se versiona: las sondas leen la evidencia del colega
y `logs/`, que son datos reales, e imprimen solo nombres de archivo y cuentas.

## NO retroceder

- **Con errores de campo, NO ENVIADA solo a los 20 s del clic,** con el Submit a la vista y sin que haya aparecido la
  ventana «Reminder» ni la página de envío.
- **La página de envío del tramo es la frase de `FORMA_ENVIADA`,** no `_JS_COSCO_EXITO`.
- **Sin errores de campo, la espera de COSCO no tiene tramo.**

## Reglas de método aplicadas

`metodo-ciclo` v38 (la misma del disco al empezar):
- medir antes de cambiar, con el JavaScript del programa leído de su fuente y control positivo que aborta;
- el camino real: las pruebas corren el código de después de la guarda, no una paráfrasis;
- cada caso con su prueba y su mutación;
- el revisor, en un clon sin remoto;
- todas las suites antes del commit;
- el RESIDUAL, la base, sin push (lo pidió el encargo) y el cierre sin esperas vivas.

Las del módulo: `test_candado` sin cambios, ningún dato real en lo versionado, y la sonda de secretos y la guarda antes
de cada commit.
