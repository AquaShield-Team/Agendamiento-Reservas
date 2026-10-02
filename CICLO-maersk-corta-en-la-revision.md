# CICLO · MAERSK corta si no llega a la revisión, y no elige la fecha de retiro

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-24 · **Método:** skill `metodo-ciclo` v12 ·
**Base:** `1957e28` · **Commits** (locales, sin push; el repo no tiene remoto):
- `0f1507e` MAERSK;
- el de este informe.

> Sin datos reales: todo sale de leer el código y de páginas falsas. No se abrió nada de `logs/`.

## Veredicto

- **Hecho, sin freno.** Para cortar en la revisión no hubo que tocar ningún otro paso de MAERSK. Cambiaron solo
  la revisión, el decorador y la fecha, más el aviso del paso que anunciaba la fecha (abajo).
- **Censo completo final sobre `0f1507e`:** **pasó.** Corrió de 17:38 a 17:58, con el árbol limpio antes y
  después. La copia sin mutar pasa las 244 pruebas. Las 458 mutaciones, en 553 pares, muerden todas, y no
  queda ninguna prueba sin mutación. 0 cambios en los originales.

**PASO 0: CICLO.**

## Qué cambió (`0f1507e`)

- **La revisión corta.** `_mk_esperar_revision(page)` espera la pantalla de revisión como antes (30 veces 0,5 s,
  unos 15 s). Si no aparece, corta con «Revisión de MAERSK»: no encontré la pantalla de revisión («Review
  booking»), que no apareció en 15 s.
  - Reemplaza al bucle que esperaba sin avisar y va antes de la cascada de los términos.
- **El decorador:** `reservar_maersk` lleva `@_sin_clic_a_ciegas("mk")`, como ONE, MSC y CMA. El corte queda
  NO ENVIADA, en pantalla y en `log.txt`, con este motivo: «Revisión de MAERSK: no encontré la pantalla de
  revisión («Review booking»), que no apareció en 15 s, así que no pulsé nada. La reserva no se envió; revisa
  ese paso en el portal.» Quedan además la captura `mk_f<fila>_sin_objetivo.png` y su HTML.
- **Sin la fecha de retiro:** sale entero el bloque del selector «Pick-up date», 117 líneas, sin reemplazo.
  Abría el selector, marcaba el primer día habilitado y pulsaba «Done».
  - El aviso del paso decía «completando fecha de retiro, referencia y Shipper». Ahora dice «completando
    referencia y Shipper (la fecha de retiro la define la naviera)». Lo cambié porque, sin el bloque, el aviso
    sería falso; es parte de quitar la fecha, no otro paso.
- **No cambian:** la fecha de zarpe («earliest departure»), la referencia, el Shipper, «Review booking», los
  términos y la guarda.

**Lo que cambia de comportamiento:**

| Si el portal… | Antes | Ahora |
|---|---|---|
| llega a la revisión | sigue a los términos | igual |
| se queda en «Additional details» (u otra pantalla) | espera unos 15 s sin avisar, marca «el último checkbox» de esa pantalla y termina en OK-EJEMPLO «armada hasta Review» | NO ENVIADA con motivo, captura y HTML; no marca nada |
| pide la fecha de retiro | el programa marcaba el primer día | el programa no la toca: si el portal no avanza sin ella, corta en la revisión |

Si MAERSK no deja avanzar sin fecha, **cada fila de MAERSK va a quedar NO ENVIADA en la revisión**. Tu prueba con
el candado cerrado lo va a mostrar.

## Expectativas

- **`test_candado`:** no cambia. Ningún texto que se quitó o se agregó calza con los de envío.
- **`test_clics`**, dos cambios:
  - `CORTAN` (`test_cada_reservador_que_corta_esta_decorado`):
    - antes: `["reservar_cma", "reservar_msc", "reservar_one"]`;
    - ahora: `["reservar_cma", "reservar_maersk", "reservar_msc", "reservar_one"]`.
  - La foto `PERMITIDOS` pierde `("reservar_maersk", "reservar_maersk", "primero-sin-filtro")`: de 1 a 0. Era el
    primer día del calendario. Las demás formas de MAERSK siguen igual.
- **Ninguna mutación existente cambió.**

## Defectos inyectados

`TestMaersk` (5 pruebas, en `test_clics`) y 10 mutaciones nuevas:
- **El corte:** sin el decorador; la revisión que no corta, con otro motivo, más corta o sin espera; la espera
  vieja en lugar del corte; y el corte después de los términos.
- **La fecha:** vuelve a elegirla; vuelve el primer día del calendario, que lo caza la foto de `test_clics`; o el
  aviso vuelve a anunciarla.

La red pasa de 239 pruebas, 448 mutaciones y 539 pares a **244 pruebas, 458 mutaciones y 553 pares**.

**Gate de `0f1507e`:**
- suite verde (244 pruebas);
- censo filtrado «maersk-»: 28 mutaciones y 35 pares; `test_cada_reservador_que_corta_esta_decorado`: 5 y 6; la
  foto de clics genéricos: 14 y 27; todas mordiendo por su razón;
- sonda de secretos en 0 sobre el árbol y el staging.

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\correr.py --mutaciones
python -m unittest test_clics.TestMaersk      # desde tests\
```

**Control positivo del detector de la fecha:** el mismo recorrido de `test_no_elige_la_fecha_de_retiro`, sobre
`1957e28`, encuentra sus 4 marcas («Choose another date», «Click to choose date», `mc-calendar-day` y
`pickupDate`). Sobre `0f1507e` encuentra 0.

## NO retroceder (pieza 2)

- **No vuelvas a elegir la fecha de retiro:** la define la naviera. `test_no_elige_la_fecha_de_retiro` cae.
- **No saques el corte de la revisión ni lo pases después de los términos:** marcaría una casilla de otra
  pantalla y diría «armada hasta Review» sin serlo.
- **No le quites el decorador a `reservar_maersk`:** `ObjetivoNoEncontrado` deriva de `BaseException` y sin el
  decorador subiría hasta cortar la corrida entera.

## Premisas del encargo contrastadas (pieza 5)

- **«Quitar la fecha no rompe nada posterior»:** confirmada otra vez: compila, y nada después del bloque usa lo
  que elegía.
- **«En test_clics solo baja la forma genérica de la fecha de 1 a 0»:** confirmada. Además cambia `CORTAN`, que
  el encargo preveía.
- **«Cortar en la revisión no obliga a cambiar otro paso»:** confirmada. Los otros cambios son la revisión, el
  decorador, la fecha y su aviso.

## Universo y cobertura (pieza 3)

- **MAERSK:** de «Additional details» a la guarda, y su universo antes de la guarda para la fecha.
- **Si no encuentra nave:** la revisión no corre, como antes, y MAERSK sigue en REVISAR «nave=no-encontrada».
- **No medido en el portal:** si MAERSK avanza sin fecha lo va a decir tu prueba con el candado cerrado.

## Defectos de instrumento cazados (pieza 4)

Ninguno nuevo.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| Si MAERSK no avanza sin fecha, todas sus filas quedan NO ENVIADA en la revisión | Tu regla: la fecha la define la naviera | …la prueba lo muestra. Ahí decides: los lectores ya ubican una columna «retiro» si la hoja la trae |
| Los términos y condiciones de MAERSK siguen marcando «el último checkbox» | FRENO de `CICLO-clics-a-ciegas.md`; falta su HTML | …la prueba deja `mk_f<fila>_guarda.html` |
| La fecha de zarpe con «Select tomorrow» si falta el día de carga | Decidiste que no cambia | …lo decides |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v12**:
- **El cambio y su guardián en la misma operación:** el corte con su prueba y el decorador con la que ya
  existía, `test_cada_reservador_que_corta_esta_decorado`.
- **Control positivo que aborta:** el detector de la fecha, probado sobre el código de antes.
- **El negativo tiene que morder, de a uno por proceso:** censo filtrado, con cada motivo revisado.
- **Cada reemplazo afirma su viejo una vez, y la escritura es atómica:** el script del cambio.
- **El EOL se verifica en binario.**
- **Se declaran el residual y las premisas.**

Reglas del módulo: casos sintéticos, toda prueba nueva con su mutación, la sonda antes del commit.

## Entregable (pieza 8)

Este `.md`, sin renderizar, y `CLAUDE.md` al día: MAERSK entre los que cortan, sin fecha de retiro, y la red en
244 pruebas.

**Para la prueba con el candado cerrado:** MAERSK ya no elige la fecha de retiro. Si llega a la revisión, deja
`mk_f<fila>_guarda.*`, donde se miden las casillas de los términos. Si no llega, queda NO ENVIADA con
`mk_f<fila>_sin_objetivo.*`, que muestra la pantalla donde se detuvo.
