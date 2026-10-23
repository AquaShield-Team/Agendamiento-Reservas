# Encargo 81 · COSCO tras el Submit: la máscara de carga al decidir, y EMITIDA solo con la frase

**Fecha:** 2026-10-23 · **Método:** `metodo-ciclo` v38, en Modo autónomo (por omisión).

Base: `Agendamiento Reservas` @ `a623bab` · árbol limpio · `origin/main` también en `a623bab` (los commits del encargo
80, subidos por Marcelo).

**Commits,** en `main` y sin push (lo pidió el encargo, y el repo es público), uno por ítem:
- `236cc29`, ítem 1: la máscara de carga a la vista al decidir cuenta como duda;
- `91da525`, ítem 2: las pruebas que fijan que EMITIDA – CONFIRMAR POR CORREO exige la frase, y el caso del 22-10;
- el de este informe.

## Las decisiones

Son las dos preguntas del encargo 80; Marcelo eligió (b) en las dos.
- **(1)** Con errores de campo, si a los 20 s la máscara de carga sigue a la vista → ENVIADA – REVISAR EN PORTAL, nunca
  NO ENVIADA.
- **(2)** Medir si hoy el camino sin errores de campo puede cortar la espera a los 3 s y dar EMITIDA – CONFIRMAR POR
  CORREO sin la página de envío. Si puede, que EMITIDA – CONFIRMAR POR CORREO exija la frase de la página de envío; sin
  ella, al tope, ENVIADA – REVISAR EN PORTAL.
- **Regla para los dos:** ante la duda, REVISAR; ni NO ENVIADA ni EMITIDA sin prueba en la página.
- **El caso del 22-10** (reserva creada) tiene que seguir dando EMITIDA – CONFIRMAR POR CORREO con su evidencia.
- **FRENA SI:** el cambio toca el estado de otra naviera, o el caso del 22-10 deja de dar EMITIDA – CONFIRMAR POR CORREO.
  No pasó (abajo).

## PASO 0: lo medido

Sin red, con el JavaScript del programa leído de su fuente con `ast`, en un Chromium sin el JavaScript de la página,
sobre los mismos 140 HTML de COSCO del encargo 80: los 20 del envío del 22-10 y los 120 de `logs/` (0 sin leer).
- **`_JS_COSCO_EN_CARGA` también calza con el formulario** (`sonda_carga.py`). Control positivo: una
  `.el-loading-mask` inventada a la vista da true, y oculta, false. Pasó.

  | | Formularios del 22-10 | Formularios de `logs/` |
  |---|---|---|
  | `_JS_COSCO_EN_CARGA` | 1 de 20 | 10 de 120 |
  | La máscara misma (`.el-loading-mask` y las de su clase) | 0 | 0 |
  | El «barco» (`[class*=boat]`, `ship`, `water`) | 1, un `div` por «ship» | 10, un `div` por «ship» |

  Son los mismos documentos donde la etiqueta del formulario da `_JS_COSCO_EXITO` (encargo 80): el marco del formulario
  de la guarda. El elemento (`sonda_ship.py`) es un `div` vacío de clase `partial-shipment` (sin descendientes, sin
  campos, sin marca de oculto en el HTML), dentro del formulario.
- **LÍMITE:** sin las hojas de estilo del portal, no se sabe si ese `div` se ve. Si se ve:
  - mientras el formulario esté a la vista, la espera lo toma por la carga y sigue esperando, sin leer los errores ni
    `_JS_COSCO_EXITO`;
  - eso explica el 22-10: con la misma espera, no se cortó a los 3 s por la etiqueta del formulario y vio la ventana a
    los 12,3 s;
  - y un rechazo con el formulario a la vista esperaría el plazo de 180 s y quedaría ENVIADA – REVISAR EN PORTAL: el
    tramo del encargo 80 y la regla del Submit del 79 no se alcanzarían. Del lado seguro, pero lento.
- **El camino sin errores de campo no puede dar EMITIDA – CONFIRMAR POR CORREO sin la frase** (leído en el código y
  medido de punta a punta, abajo): esa salida de `_resultado_envio` exige la referencia de la frase de
  `FORMA_ENVIADA` (`referencia_tras_envio`), y COSCO no tiene forma de número en `FORMA_BOOKING`. La etiqueta del
  formulario solo puede cortar la espera; y si la corta, `_resultado_envio` lee la frase hasta 15 s y, sin ella,
  ENVIADA – REVISAR EN PORTAL.
- **Veredicto:**
  - ítem 1, **CICLO**: la máscara, con la definición única del programa (`_JS_COSCO_EN_CARGA`), al decidir;
  - ítem 2, **NOTA con sus pruebas**: no puede, así que no se cambia el código; se fijan con pruebas de punta a punta la
    garantía y el caso del 22-10, con mutaciones.
  - **La espera no se cambia:** si lo que sostuvo la espera del 22-10 fue el `div` (una de las dos lecturas que
    explican su log), sacar el «ship» de `_JS_COSCO_EN_CARGA` dejaría que la etiqueta la cortara a los 3 s, y ese caso
    quedaría ENVIADA – REVISAR EN PORTAL (FRENA SI). Es la pregunta 1.

## Ítem 1: la máscara al decidir

En `AQUASHIELD.py`, `CLAUDE.md`, `tests/test_envio.py` y `tests/mutaciones.py`.
- `_cosco_submit_en_duda`, después de la ventana y antes del Submit: si `_cosco_en_alguno(frame, page,
  _JS_COSCO_EN_CARGA)` da verdadero, el motivo «la máscara de carga sigue a la vista». Con errores de campo, la
  decisión se toma a los 20 s (encargo 80): ahí se mira.
- Pruebas: `test_errores_de_campo_y_el_submit` al día (el orden de las preguntas, y la máscara antes que el Submit), y
  `TestCoscoTrasLosErrores.test_mascara_de_carga_al_tope`, de punta a punta sobre el código real de después de la
  guarda:

  | Caso | Resultado | A los |
  |---|---|---|
  | La máscara de los 5 a los 30 s, en el marco o en la página | ENVIADA – REVISAR EN PORTAL, «… pero la máscara de carga sigue a la vista» | 20,0 s |
  | La máscara de los 5 a los 15 s | NO ENVIADA | 20,0 s |
  | La máscara para siempre, como el `div` si el portal lo muestra | ENVIADA – REVISAR EN PORTAL, los errores como aviso del portal, sin tramo | 180,0 s |

- 4 mutaciones (`e81-carga-no-se-mira`, `-solo-en-el-marco`, `-solo-en-la-pagina`, `-sin-motivo`).

## Ítem 2: EMITIDA – CONFIRMAR POR CORREO solo con la frase

Sin cambio de código: medido, no puede darla sin la frase. En `CLAUDE.md`, `tests/test_envio.py` y
`tests/mutaciones.py`, las pruebas que lo fijan de punta a punta sobre el código real de después de la guarda.
- El portal falso de las pruebas (`PortalCOSCO`) suma `formulario_hasta`: el formulario a la vista hasta ese segundo,
  con su etiqueta (`_JS_COSCO_EXITO`) y su `div` (`_JS_COSCO_EN_CARGA`), como están en el HTML guardado. Que el portal
  muestre el `div` es una hipótesis. Sin `formulario_hasta`, todo queda como antes.

| Caso | Resultado | A los |
|---|---|---|
| La etiqueta sola, sin la frase (la espera se corta a los 3 s) | ENVIADA – REVISAR EN PORTAL, «… no mostró que la reserva se enviara» | 18,0 s (3 + los 15 de la lectura) |
| El formulario a la vista para siempre, sin la frase | ENVIADA – REVISAR EN PORTAL | 195,0 s (el plazo de 180 + 15) |
| El 22-10 en el tiempo, con el `div` del formulario hasta los 33 s, la ventana de los 12 a los 33 y la página de envío | EMITIDA – CONFIRMAR POR CORREO, con su número y su evidencia (la captura y los HTML de la página y del marco) | 34,5 s |
| El 22-10 con una máscara de verdad hasta la ventana, en lugar del `div` | lo mismo | 34,5 s |
| La etiqueta y la frase dentro de los 15 s de la lectura (del encargo 80) | EMITIDA – CONFIRMAR POR CORREO | 10,0 s |

- **Lo medido del 22-10** es su log: la espera, con las mismas vueltas, no se cortó antes de ver la ventana a los
  12,3 s. Las dos lecturas que lo explican están en la prueba. Una que cortara la espera antes de la ventana contradice
  el log; con ella, la reserva creada quedaría ENVIADA – REVISAR EN PORTAL, el lado seguro.
- 2 mutaciones: `e81-senal-de-la-espera-como-frase` (una lectura que acepta la señal de la espera como la frase) y
  `e81-sin-esperar-la-carga` (una espera que no espera con la máscara: el 22-10 quedaría ENVIADA – REVISAR EN PORTAL).

## Las suites

Sobre el árbol de cada commit, antes de commitearlo, con `TEMP`, `TMP` y `TMPDIR` en la carpeta del encargo:

| Corrida | Resultado |
|---|---|
| Ítem 1: `test_envio`, `test_datadome` y `test_candado` | 155 pruebas, OK (230 s) |
| Ítem 1: el censo de las mutaciones e81 | 4 mutaciones, 7 pares: todos muerden |
| Ítem 1: la suite completa (con el tope de 3.600 s del encargo 76) | 892 pruebas, OK (1.551 s). Originales: 0 cambios |
| Ítem 2: el censo de las mutaciones e81 | 6 mutaciones, 9 pares: todos muerden |
| Ítem 2: el censo de `test_envio` (cubre los dos ítems) | 270 mutaciones, 340 pares: los 340 muerden, 10 de las e81. Originales: 0 cambios |
| Ítem 2: la suite completa | 894 pruebas, OK (1.770 s). Originales: 5.586 entradas, 0 cambios |

`tests/mutaciones.py` trae 2.582 mutaciones, y cada una se aplica una sola vez. Las compuertas de cada commit, en 0: la
sonda de secretos (antes y después de `git add`), el barrido de datos reales sobre lo agregado (99 y 83 líneas) y sobre
el mensaje, y la guarda de datos del hook.

## Las revisiones de código

Una por diff, cada una con `code-reviewer` en un clon sin remoto.

**Ítem 1** (commit `0102c4b` del clon): **APROBAR**, sin CRITICAL ni HIGH.
- Corrió `test_envio`, `test_datadome` y `test_candado` (155, OK) y `test_clics`, `test_evidencia` y `test_consola`
  (441, OK, 1 omitida); las 4 mutaciones e81 y 5 propias muerden; la guarda de datos sobre lo agregado, 0.
- Con 16 escenarios, antes y después del cambio: solo cambian los de la máscara a la vista al decidir (de NO ENVIADA a
  REVISAR); los cinco al estilo 22-10 dan lo mismo.
- Confirmó con el código que, si el `div` se ve, el rechazo espera 180 s y queda REVISAR (la pregunta 1), y que el
  cambio no lo empeora.

| # | Hallazgo | Qué hice |
|---|---|---|
| L1 | Una máscara que se vio en el tramo y ya no está a los 20 s da NO ENVIADA, aunque la ventana llegue después | Al RESIDUAL: es la letra de la decisión («a los 20 s») |
| L2 | El comentario de `reservar_cosco` y el docstring de `_resultado_envio` no nombraban la ventana ni la máscara | Completados, también en `CLAUDE.md` |
| L3 | Faltaba la prueba de la máscara para siempre, el caso que la medición hace probable | Agregada: ENVIADA – REVISAR EN PORTAL a los 180 s, sin tramo |

**Ítem 2** (commit `03d34d1` del clon): **APROBAR CON CAMBIOS**, sin CRITICAL ni HIGH.
- Confirmó la conclusión leyendo cada camino (`numero_tras_envio` sin forma de COSCO, `if ref:` como única salida de
  EMITIDA – CONFIRMAR POR CORREO, los errores de campo y el aviso del portal antes, la falla del programa, la
  referencia ambigua o repetida, el plazo), y con 3 mutaciones propias que caen.
- Corrió el 22-10 con seis lecturas de lo medido: las que no cortan la espera antes de la ventana dan EMITIDA; una con
  un hueco entre la máscara y la ventana da ENVIADA – REVISAR EN PORTAL.

| # | Hallazgo | Qué hice |
|---|---|---|
| M1 | La prueba del 22-10 presentaba como medido el modelo del `div`, que es una hipótesis | La prueba corre las dos lecturas que explican el log, y la prueba, el portal falso y `CLAUDE.md` dicen que son hipótesis, y qué pasa con una que cortara antes |
| L1 | El docstring de `PortalCOSCO` decía que el marco da `_JS_COSCO_EXITO` «siempre» | Dice cuándo, con y sin `formulario_hasta` |
| L2 | `e81-sin-esperar-la-carga` también tumba la prueba de la etiqueta, y no la nombraba | Agregada a sus pruebas |

No hubo revisión de seguridad: el encargo pidió la de código. Los arreglos no tuvieron otra vuelta; van con sus pruebas
y sus mutaciones en el censo.

## Decisiones que tomé solo

| Decisión | Por qué |
|---|---|
| La máscara se mira con la definición única del programa, `_JS_COSCO_EN_CARGA` | El instrumento lee la definición que vigila; una propia diría otra cosa que la espera |
| No cambiar `_JS_COSCO_EN_CARGA` aunque calce con el formulario | El caso del 22-10 depende de esa espera (FRENA SI); cambiarla lo decide Marcelo (pregunta 1) |
| La máscara, al decidir y no en el tramo | La decisión dice «a los 20 s»: es lo que se ve al tope |
| Ítem 2 sin cambio de código | Medido: EMITIDA – CONFIRMAR POR CORREO ya exige la frase; el encargo pedía cambiarlo «si puede» |

## Errores propios, y cómo se vieron

| Error | Cómo se vio | Qué hice |
|---|---|---|
| La prueba del 22-10 presentaba como medido el modelo del `div`, que es una hipótesis | La revisión del ítem 2 (M1) | Las dos lecturas que explican el log, dichas como hipótesis |
| El comentario de `reservar_cosco` y el docstring de `_resultado_envio` quedaron sin la máscara (y sin la ventana, desde el encargo 79) | La revisión del ítem 1 (L2) | Completados |
| Al rehacer el docstring de `PortalCOSCO` quedó una línea de 162 caracteres, y después decía «siempre» | Las dos revisiones | Reescrito |

## Preguntas para Marcelo

1. **¿Mido o cambio la «máscara» de la espera?** `_JS_COSCO_EN_CARGA` calza con el `div` `partial-shipment` del
   formulario. Si el portal lo muestra, todo rechazo de COSCO espera 180 s y queda REVISAR, sin llegar a la regla del
   Submit ni al tramo de 20 s.
   - (a) Dejarlo así: es del lado seguro, y sostiene la espera del 22-10.
   - (b) Medirlo en el portal, con las hojas de estilo: si el `div` se ve con el formulario.
   - (c) Cambiarlo: la máscara sin el «ship», y la etiqueta del formulario fuera de `_JS_COSCO_EXITO`, para que la
     espera no se corte a los 3 s. Toca el camino del 22-10, y necesita su propio encargo.

## RESIDUAL

| Qué | Condición de reapertura |
|---|---|
| **Si el `div` `partial-shipment` se ve con el formulario**, un rechazo de COSCO espera 180 s y queda REVISAR (la pregunta 1) | La pregunta 1, o una corrida con el candado abierto y una fila rechazada |
| **Una máscara que se vio en el tramo y ya no está a los 20 s** no cuenta: con el Submit a la vista, NO ENVIADA, aunque la ventana llegara después (revisión del ítem 1, L1). Es la letra de la decisión («a los 20 s») | Si Marcelo quiere contar la máscara vista en cualquier momento del tramo |
| **Los 20 s siguen siendo una hipótesis,** y que COSCO deje su Submit a la vista cuando rechaza sigue sin medirse (encargos 79 y 80) | Un envío con errores de campo que deje su HTML y su log |

## Re-medir

1. `python -B -P <e81>/sonda_carga.py` y `sonda_ship.py`: `_JS_COSCO_EN_CARGA` y sus dos mitades en los 140 HTML, y el
   `div` que calza.
2. Desde `tests/`: `python -m unittest test_envio.TestCoscoTrasLosErrores`; y
   `python tests/correr.py --mutaciones --filtro e81`.

`<e81>` es la carpeta del encargo en el scratchpad de la sesión. No se versiona: las sondas leen la evidencia del colega
y `logs/`, que son datos reales, e imprimen solo nombres de archivo, clases del portal y cuentas.

## NO retroceder

- **Con errores de campo y la máscara de carga a la vista al decidir, nunca NO ENVIADA.**
- **EMITIDA – CONFIRMAR POR CORREO solo con la frase de la página de envío,** nunca por la etiqueta del formulario ni
  por las señales con que la espera deja de esperar.
- **El caso del 22-10 da EMITIDA – CONFIRMAR POR CORREO con su número.**

## Reglas de método aplicadas

`metodo-ciclo` v38 (la misma del disco al empezar):
- medir antes de cambiar, con el JavaScript del programa leído de su fuente y control positivo que aborta;
- el instrumento lee la definición única de la guarda que vigila (`_JS_COSCO_EN_CARGA`);
- el camino real: las pruebas corren el código de después de la guarda, no una paráfrasis;
- cada caso con su prueba y su mutación; una revisión de código por diff, en un clon sin remoto;
- todas las suites antes de cada commit;
- lo que está fuera del encargo se propone (la pregunta 1); el RESIDUAL, la base, sin push y el cierre sin esperas
  vivas.

Las del módulo: `test_candado` sin cambios, ningún dato real en lo versionado, y la sonda de secretos y la guarda antes
de cada commit.
