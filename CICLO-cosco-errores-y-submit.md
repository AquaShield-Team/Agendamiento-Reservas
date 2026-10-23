# Encargo 79 · COSCO con errores de campo: NO ENVIADA solo si el Submit sigue a la vista

**Fecha:** 2026-10-23 · **Método:** `metodo-ciclo` v38, en Modo autónomo (por omisión).

Base: `Agendamiento Reservas` @ `6ade779` · árbol limpio. `origin/main` también estaba en `6ade779`: los commits de los
encargos 77 y 78 se subieron el 2026-10-23 a las 05:52, antes de este encargo (el reflog de `origin/main`).

**Commits,** en `main` y sin push (lo pidió el encargo, y el repo es público):
- `018c3b3`, el cambio;
- `ceb74e8`, este informe;
- el que corrige esta línea de la base, que decía que los commits de los encargos 77 y 78 no estaban subidos.

## La decisión

Es la pregunta 1 del encargo 78. Marcelo eligió la tercera opción. Su razón: NO ENVIADA invita a reenviar la fila, y si
COSCO aceptó el envío después, la reserva queda duplicada.
- **Errores de campo y el Submit a la vista:** el portal rechazó → NO ENVIADA, como hasta ahora.
- **Errores de campo y el Submit ya no a la vista:** no se sabe → ENVIADA – REVISAR EN PORTAL, con un motivo que dice que
  se vieron errores pero el envío pudo haber entrado.
- **Si la lectura del Submit falla:** también ENVIADA – REVISAR EN PORTAL. Ante la duda, nunca NO ENVIADA.
- **FRENA SI:** el cambio toca el estado de otra naviera, o el camino de COSCO sin errores de campo. No pasó (abajo).

## PASO 0

- **El registro:** `CLAUDE.md` y el informe del encargo 78 decían lo que pasa con errores de campo:
  - NO ENVIADA, salvo con la ventana Reminder ya vista (van como aviso del portal);
  - o salvo con la frase de envío o el número a la vista (las dos señales se contradicen).
  - `_cosco_esperar_resultado` sale apenas ve errores de campo, a unos 3 s del Submit.
- **Lo medido** (`sonda_submit_cosco.py`): el `_JS_COSCO_SUBMIT_PRESENTE` y el `_JS_COSCO_ERRORES` del programa,
  leídos de su fuente con `ast`, en un Chromium sin red, sobre los 20 HTML de COSCO del envío del 22-10, el único
  guardado. Quedaron 0 sin leer.
  - **Control positivo:** en la guarda, antes del clic, el marco del formulario trae el Submit (2 elementos), y el
    JavaScript lo da a la vista. Pasó.
  - **Después del envío que entró,** ninguno de los 5 documentos (la página y sus 4 marcos) trae un «Submit», y ninguno
    trae errores de campo.
  - **LÍMITE:** el HTML guardado no trae las hojas de estilo del portal. Lo que el JavaScript ve «a la vista» en esa copia
    no es lo que vio el navegador; la cuenta sin estilo dice si el botón seguía en el documento.
  - **No está medido** que COSCO deje su Submit a la vista cuando marca errores de campo: ninguna corrida guardada los
    trae.
- **Veredicto:** **CICLO**.

## El cambio

En `AQUASHIELD.py`, `CLAUDE.md`, `tests/test_envio.py` y `tests/mutaciones.py`.
- **`_cosco_submit_en_duda(frame, page, reg)`** solo lee, sin clics ni esperas:
  - con la ventana Reminder a la vista, en el marco o en la página, «la ventana «Reminder» está a la vista», sin mirar
    el Submit (de la revisión de código);
  - devuelve '' si `frame.evaluate(_JS_COSCO_SUBMIT_PRESENTE)` es `True`;
  - con `False`, ««Submit» ya no está a la vista»;
  - si la lectura falla, o da otra cosa, «no se pudo leer si «Submit» sigue a la vista», y lo anota en log.txt.
- **`reservar_cosco`**, después de que los errores con el Reminder visto pasan a aviso del portal:
  `en_duda = _cosco_submit_en_duda(frame, page, reg) if campos else ""`, y se lo pasa a `_resultado_envio`.
- **`_resultado_envio`** tiene un parámetro nuevo, `campos_en_duda=""`, que solo pasa COSCO:
  - con errores de campo y el motivo, ENVIADA – REVISAR EN PORTAL: «el portal marcó: …, pero «Submit» ya no está a la
    vista: el envío pudo haber entrado», y qué hacer si la reserva no quedó creada;
  - va después de la contradicción del encargo 78, que dice más, y antes de NO ENVIADA.
- **El FRENA SI no se tocó:**
  - las otras navieras no pasan errores de campo ni el parámetro, que por omisión no cambia nada;
  - sin errores de campo, COSCO no mira el Submit, y el parámetro solo se lee dentro de `if rechazo:`.
  - La prueba lo comprueba: la frase de envío con el motivo puesto y sin errores sigue EMITIDA – CONFIRMAR POR CORREO.

## Las pruebas, en las dos direcciones

`test_envio.TestResultadoEnvio.test_errores_de_campo_y_el_submit` pasa por el ayudante y por `_resultado_envio`, en el
orden de `reservar_cosco`. Los tres casos:

| Caso | Resultado |
|---|---|
| El Submit a la vista | NO ENVIADA, con el motivo de siempre |
| El Submit ya no está | ENVIADA – REVISAR EN PORTAL, «… pero «Submit» ya no está a la vista: el envío pudo haber entrado» |
| La lectura falla | ENVIADA – REVISAR EN PORTAL, «… pero no se pudo leer si «Submit» sigue a la vista…», y la línea en log.txt |

La prueba comprueba además estas cosas:
- una respuesta que no es `True` ni `False` (`None`, «true», `1`) no basta para NO ENVIADA, y log.txt dice qué dio;
- con la ventana Reminder a la vista, en el marco o en la página, el Submit no se mira, y queda REVISAR;
- con la frase de envío a la vista, gana el motivo de la contradicción;
- sin errores de campo, nada cambia.

`test_envio.TestReservadores.test_cosco_decide_con_lo_que_vio` fija la forma de `reservar_cosco`: mira el Submit solo
con errores de campo, y pasa el motivo.

Las preguntas tienen ahora tres orígenes posibles:
- la ventana Reminder, en el marco o en la página;
- el Submit, solo en el marco;
- cualquier otro JavaScript, que hace caer la prueba.

`test_envio.TestCosco.test_js_submit_presente_solo_el_submit_a_la_vista` corre el `_JS_COSCO_SUBMIT_PRESENTE` en Node,
con un `document` falso:
- da `True` con «Submit» a la vista, también con otras mayúsculas y espacios a los lados;
- da `False` con el Submit oculto, con «Submit booking» y sin elementos.

## La revisión de código

`code-reviewer`, en un clon sin remoto, sobre el commit `5007f40` del clon. Veredicto: **APROBAR CON CAMBIOS**, sin
CRITICAL ni HIGH.
- Corrió `test_envio`, `test_datadome` y `test_candado` (148 pruebas, OK) y otros nueve módulos (578, OK, 1 omitida).
- Las 10 mutaciones e79 de entonces murieron, y 6 viejas que tocan el código siguieron cayendo.
- Comprobó que las 2.540 mutaciones se aplican una vez cada una.
- La guarda de datos sobre lo agregado dio 0, y su control positivo, 1.

| # | Severidad | Hallazgo | Qué hice |
|---|---|---|---|
| M1 | MEDIUM | Lo medido no cubre el intervalo entre el clic y el Reminder. El Submit se lee a los ~3 s; si COSCO acepta un envío con errores de campo y deja su Submit hasta su respuesta, la fila queda NO ENVIADA con la reserva creada | Escrito en `CLAUDE.md` y en el RESIDUAL. Cerrarlo es esperar más antes de dar NO ENVIADA: va como pregunta |
| M2 | MEDIUM | `_JS_COSCO_SUBMIT_PRESENTE` decide ahora, y ninguna prueba lo ejecutaba: dos mutaciones suyas sobrevivían | Prueba en Node y sus dos mutaciones (`e79-js-submit-oculto-cuenta`, `e79-js-submit-parcial`) |
| L1 | LOW | Faltaban tres mutaciones; `e79-cosco-mira-sin-errores` solo la ve la foto | Agregadas (`e79-duda-sin-errores-de-campo`, `e79-duda-antes-que-la-contradiccion`, `e79-cosco-sin-pasar-la-duda`); el comentario dice que esa la ve la foto |
| L2 | LOW | El motivo no decía qué hacer si la reserva no quedó creada | Termina en «Si no está, corrige esos datos y vuelve a correrla» |
| L3 | LOW | Con la ventana Reminder abierta, su Submit se leería como el del formulario | El ayudante mira antes la ventana, en el marco y en la página; si está, es duda (`e79-reminder-no-se-mira`, `e79-reminder-solo-en-el-marco`) |
| L4 | LOW | Textos atrasados: el docstring de `test_envio`, una frase de `CLAUDE.md`, y la respuesta rara se informaba como «ya no está» | Corregidos. La respuesta que no es `True` ni `False` es «no se pudo leer», y log.txt dice qué dio (`e79-respuesta-rara-…`) |

No hubo revisión de seguridad: el encargo pidió la de código. Los arreglos de la revisión no tuvieron otra vuelta; van
con sus pruebas y sus mutaciones en el censo.

## Preguntas para Marcelo

1. **El intervalo entre el clic y el Reminder** (M1): con errores de campo y el Submit a la vista a los ~3 s, ¿lo dejo
   NO ENVIADA, como decidiste, o espero un tramo más antes de darlo (el 22-10 el Reminder llegó a los ~12 s y la frase,
   después)? Esperar retrasa cada fila rechazada; no esperar deja el caso de un envío aceptado tarde.

## Las suites

Corridas sobre el árbol del commit `018c3b3`, antes de commitearlo, con `TEMP`, `TMP` y `TMPDIR` en la carpeta del
encargo:

| Corrida | Resultado |
|---|---|
| `test_envio`, `test_datadome` y `test_candado`, después de los arreglos de la revisión | 149 pruebas, OK (302 s) |
| El censo de `test_envio` (`correr.py --mutaciones --filtro test_envio`) | 238 mutaciones, 295 pares: los 295 muerden, y las 20 e79 entre ellos. Originales: 5.584 entradas, 0 cambios |
| La suite completa (`correr.py`, con el tope de 3.600 s del encargo 76) | 886 pruebas, OK (2.907 s). Originales: 5.584 entradas, 0 cambios |

Las compuertas del commit, en 0: la sonda de secretos (antes y después de `git add`), el barrido de datos reales sobre
lo agregado (241 líneas) y sobre el mensaje, y la guarda de datos del hook (0 hallazgos).
`tests/mutaciones.py` trae 2.550 mutaciones, y cada una se aplica una sola vez.

## Decisiones que tomé solo

| Decisión | Por qué |
|---|---|
| NO ENVIADA solo con la respuesta `True`, no con cualquier valor «verdadero» | Ante la duda, nunca NO ENVIADA: el JavaScript devuelve un booleano, y lo demás es duda |
| Con la ventana Reminder a la vista, duda, sin mirar el Submit | El Submit de la ventana se leería como el del formulario, y la ventana sale después del envío |
| El motivo dice también qué hacer si la reserva no quedó creada | Varios rechazos reales pueden caer en REVISAR mientras no se mida el Submit de COSCO tras un rechazo |
| El motivo en `_resultado_envio`, con un parámetro que solo pasa COSCO, y no como un aviso del portal | Así dice lo que decidió Marcelo («se vieron errores, pero pudo haber entrado»), y las otras navieras no cambian |
| Una sola lectura, sin esperar | La decisión es de lo que se ve cuando la espera ve los errores; esperar retrasaría cada fila rechazada |
| La contradicción del encargo 78 va antes | Si la página dice que la reserva se envió, ese motivo dice más |

## Errores propios, y cómo se vieron

| Error | Cómo se vio | Qué hice |
|---|---|---|
| El bloque nuevo de `_resultado_envio` terminaba igual que el de la contradicción, y la mutación `e78-campos-con-la-frase-callado` habría calzado con los dos | El revisor de mutaciones (cada `viejo`, una sola vez) | El texto de esa mutación termina ahora en `if campos_en_duda:`, que solo trae el primero |
| Tres mutaciones de COSCO del encargo 77 quedaron sin calzar al cambiar la llamada a `_resultado_envio` | El mismo revisor | `DECIDE_CO`, con `campos_en_duda=en_duda` |
| `RS`, el prefijo de `TestReservadores`, ya nombraba otra clase más abajo en el archivo | Leyendo `mutaciones.py` antes de usarlo | `RS_E79` |
| El `return` de «no se pudo leer» aparece dos veces, con distinta sangría, y uno contiene al otro | El revisor de mutaciones | La mutación de la respuesta rara lleva también la línea de log.txt de antes (`RARA`) |

## RESIDUAL

| Qué | Condición de reapertura |
|---|---|
| **Que COSCO deje su Submit a la vista cuando marca errores de campo no está medido.** Si no lo deja, cada fila rechazada queda en REVISAR (el lado seguro) | La primera fila rechazada en una corrida con el candado abierto deja su HTML: medir el Submit con `sonda_submit_cosco.py` |
| **El intervalo entre el clic y el Reminder** (M1 de la revisión): la espera sale a los ~3 s, y si COSCO acepta un envío con errores de campo y deja su Submit hasta su respuesta, la fila queda NO ENVIADA con la reserva creada | La pregunta 1; o un caso medido |
| **Un `position: fixed` también da `offsetParent` nulo** (nota de la revisión, sin comprobar): un Submit fijo se leería como «ya no está», REVISAR (el lado seguro) | Si se mide que el Submit de COSCO es fijo |

## Re-medir

1. `python -P <e79>/sonda_submit_cosco.py`: el Submit y los errores en los HTML de COSCO del envío del 22-10.
2. Desde `tests/`: `python -m unittest test_envio`; y `python tests/correr.py --mutaciones --filtro e79`.

`<e79>` es la carpeta del encargo en el scratchpad de la sesión. No se versiona: la sonda lee la evidencia del colega,
que son datos reales, y solo imprime nombres de archivo y cuentas.

## NO retroceder

- **Con errores de campo, NO ENVIADA solo con el Submit de COSCO a la vista, leído como `True`, y sin la ventana
  Reminder;** lo demás, ENVIADA – REVISAR EN PORTAL. NO ENVIADA invita a reenviar una reserva que pudo crearse.
- **Sin errores de campo, COSCO no mira el Submit.**

## Reglas de método aplicadas

`metodo-ciclo` v38 (la misma del disco al empezar):
- re-medir contra HEAD, con el JavaScript del programa leído de su fuente, y control positivo que aborta (0 sin leer);
- cada caso con su prueba en las dos direcciones, y cada prueba con su mutación;
- el revisor, en un clon sin remoto; todas las suites antes del commit;
- el RESIDUAL, la base, sin push (lo pidió el encargo) y el cierre sin esperas vivas.

Las del módulo: `test_candado` sin cambios, ningún dato real en lo versionado, y la sonda de secretos y la guarda antes
de cada commit.
