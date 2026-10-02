# CICLO · Panel Reefer de CMA y fecha de retiro de MAERSK

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-24 · **Método:** skill `metodo-ciclo` v12 ·
**Base:** `87b6b88` · **Commits** (locales, sin push; el repo no tiene remoto):
- `2b69304` CMA;
- el de este informe.

> Sin datos reales: todo sale de leer el código y de páginas falsas. No se abrió nada de `logs/`.

## Veredicto

- **CMA: hecho.** Con el panel Reefer abierto y tras guardarlo, deja la captura de la ventana y el HTML
  (`cma_f<fila>_reefer_panel.*` y `cma_f<fila>_reefer_guardado.*`). No agrega clics, teclas, esperas ni
  navegación.
- **MAERSK: FRENO, sin cambios.** Quitar la fecha obliga a cambiar otro paso de MAERSK: el paso siguiente no
  corta como tu decisión supone. Detalle abajo.
- **Censo completo final sobre `2b69304`:** **pasó.** Corrió de 16:39 a 17:21, con el árbol limpio antes y
  después. La copia sin mutar pasa las 239 pruebas. Las 448 mutaciones, en 539 pares, muerden todas, y no
  queda ninguna prueba sin mutación. 0 cambios en los originales.

**PASO 0: CICLO** en CMA; **PREGUNTA** en MAERSK.

## MAERSK: el freno

**Lo que quitar la fecha no rompe:**
- El bloque de la fecha son 117 líneas: abrir el selector, elegir el día y pulsar «Done». Nada de lo que viene
  después usa lo que eligió.
- Sin él, la foto de `test_clics` pierde solo `primero-sin-filtro` de MAERSK (de 1 a 0), como previste.
- `test_candado` no cambia: ningún texto del bloque calza con los de envío.

**Lo que tu decisión supone y hoy no pasa:** «si el portal no avanza sin fecha, el paso siguiente corta como
cualquier objetivo no encontrado». MAERSK no tiene ese mecanismo: `reservar_maersk` no está decorado con
`_sin_clic_a_ciegas` y ninguno de sus pasos levanta `ObjetivoNoEncontrado`, porque sus genéricos quedaron en
freno en `CICLO-clics-a-ciegas.md`. Si el portal no avanza desde «Additional details», el código de hoy hace
esto:
1. encuentra «Review booking» y lo pulsa;
2. espera la pantalla de revisión hasta unos 15 s y sigue sin decir nada;
3. corre la cascada de los términos sobre «Additional details» y marca el último checkbox de **esa** página;
4. con el candado cerrado, la guarda devuelve OK-EJEMPLO «armada hasta Review», que sería falso, aunque la
   evidencia de la guarda mostraría dónde quedó;
5. con el candado abierto, si en esa pantalla no hay «Submit booking» ni «Book now», termina NO ENVIADA «no se
   pulsó…», con captura y HTML.

**Para que corte como decidiste** hay que tocar otro paso: el de revisión tiene que levantar
`ObjetivoNoEncontrado` cuando la pantalla de revisión no aparece, y `reservar_maersk` tiene que llevar el
decorador. Es justo el FRENA SI.

**Lo que decides:**
- **a) Autorizar ese corte (recomendado).** El paso de revisión corta si la revisión no aparece, MAERSK lleva
  el decorador, y recién ahí se quita la fecha.
  - Así MAERSK deja de decir «armada hasta Review» cuando se queda en otra pantalla, por la fecha o por lo que
    sea, y la cascada de los términos ya no corre sobre la página equivocada.
  - Según cómo se escriba, `test_clics` suma a MAERSK entre los reservadores que cortan. Esa expectativa se
    listaría.
- **b) Quitar solo la fecha.** Aceptas los puntos 3 y 4 de arriba.

**Aparte, fuera de tu regla:** la fecha de zarpe («earliest departure») sale del día de carga de la planilla; si
falta, el programa pulsa «Select tomorrow». Es una fecha de búsqueda, no de retiro. Lo anoto por si también la
quieres fuera.

## CMA: qué cambió (`2b69304`)

- **Con el panel abierto:** `_evidencia_antes_de_la_guarda(page, reg, f"cma_f{f}_reefer_panel", …)`, justo
  después de la captura `4b_reefer_drawer` que ya había, y antes de la temperatura.
- **Tras guardarlo:** `cma_f{f}_reefer_guardado`, después de la espera de 1,5 s que ya había y antes del
  Escape. Muestra si el guardado dejó el panel en paz o con errores.
- **Si falta el botón de guardar,** el paso corta como antes («Guardar los ajustes Reefer de CMA») y queda
  `cma_f<fila>_sin_objetivo.*` de esa misma pantalla: no se repite como `reefer_guardado`.
- **La captura es de la ventana, no de la página completa.** La de página completa dispara un `resize` en la
  página (medido en `7b3e3e2`), y aquí el flujo sigue después.
  - Con la de la ventana no hay interacción nueva: es la misma clase de captura que la de `4b_reefer_drawer`, y
    el HTML solo lee.
  - Por eso no se cumple el FRENA SI del panel.
- **Si la evidencia falla,** lo avisa en pantalla y en `log.txt`, y el panel se configura igual.
- **Tiempo:** dos capturas de la ventana y dos HTML más por fila de CMA.

## Expectativas

- **`test_candado` y `test_clics`:** no cambian. La forma de la fecha de MAERSK sigue en la foto de `test_clics`
  porque MAERSK quedó en freno. El antes y el después que pediste serían
  `("reservar_maersk", "reservar_maersk", "primero-sin-filtro")`: de 1 a 0.
- **`test_evidencia.TestCadaReservadorLaDeja.test_solo_ahi`:**
  - antes: los seis reservadores y `_sin_clic_a_ciegas`;
  - ahora: además, las dos llamadas de `_cma_ajustes_reefer`.
- **Ninguna mutación existente cambió.**

## Defectos inyectados

10 nuevas, con `TestEvidenciaReefer` (3 pruebas), que fija la secuencia exacta de clics, teclas, esperas,
capturas y lecturas del HTML. Cada mutación ataca una de estas propiedades:
- sin la evidencia del panel o sin la de lo guardado;
- con la página completa en una u otra;
- con una espera o una tecla antes;
- lo guardado antes de guardar, o solo si guardó Playwright;
- cualquiera de las dos sin protección.

La red pasa de 236 pruebas, 438 mutaciones y 526 pares a **239 pruebas, 448 mutaciones y 539 pares**.

**Gate de `2b69304`:**
- suite verde (239 pruebas);
- censo filtrado «reefer-»: 20 mutaciones y 27 pares; «test_solo_ahi»: 10 y 20; todas mordiendo por su razón;
- sonda de secretos en 0 sobre el árbol y el staging.

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\correr.py --mutaciones
python -m unittest test_evidencia.TestEvidenciaReefer      # desde tests\
```

- **La foto sin la fecha:** una copia temporal de `AQUASHIELD.py` sin el bloque «# 1) Pick-up date» hasta
  «# 2) Haulage reference», con `test_clics.clics_genericos` sobre las dos. El control positivo: la foto del
  original es igual a `PERMITIDOS`.
- **El paso siguiente de MAERSK:** leer `reservar_maersk` desde «Additional details» hasta la guarda.

## NO retroceder (pieza 2)

- **No hagas de página completa la evidencia del panel Reefer:** después de ella el flujo sigue.
- **No le pongas una espera propia:** usa las que ya hay.
- **No quites la fecha de MAERSK sin decidir el corte de la revisión:** dejarías un OK-EJEMPLO falso.

## Premisas del encargo contrastadas (pieza 5)

- **«Solo MAERSK elige una fecha de retiro»:** confirmada.
- **«Si el portal no avanza sin fecha, el paso siguiente corta como cualquier objetivo no encontrado»:**
  refutada para MAERSK. Hoy no corta ningún paso de MAERSK.
- **«El panel Reefer solo queda medido si corta ahí o si sigue abierto en la guarda»:** confirmada. Ahora queda
  en dos momentos.

## Universo y cobertura (pieza 3)

- **CMA:** los 3 caminos del panel: guardar por Playwright, por JavaScript, y la evidencia que falla. El corte
  por falta del botón lo sigue cubriendo `test_clics`.
- **MAERSK:** desde «Additional details» hasta la guarda, leído entero.
- **No se midió sobre los portales:** es la corrida con el candado cerrado.

## Defectos de instrumento cazados (pieza 4)

1. **Un `sed` con barras invertidas en Bash.** No reemplazó la ruta del script del censo (la herramienta
   convierte `\\` en `\`). Lo vi en la salida y reescribí el script con Write.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| La fecha de retiro de MAERSK | FRENO: pide cambiar el paso de revisión | …eliges a) o b) |
| La fecha de zarpe de MAERSK con «Select tomorrow» si falta el día de carga | Fuera de la regla del retiro | …la quieres fuera |
| La captura `4b_reefer_drawer` repite el momento de `reefer_panel` | No se pidió quitarla | …sobra |
| Guardar el panel sin botón deja `_sin_objetivo` y no `reefer_guardado` | Es la misma pantalla: no se duplica | …prefieres los dos nombres |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v12**:
- **FRENAR cuando la decisión es de negocio:** el corte en la revisión de MAERSK.
- **Control positivo que aborta:** la foto del original igual a `PERMITIDOS` antes de leer la de sin fecha.
- **El negativo tiene que morder, de a uno por proceso:** censo filtrado, con cada motivo revisado.
- **El cambio y su guardián en la misma operación.**
- **El EOL se verifica en binario.**
- **Todo registro es una hipótesis:** la frase «el paso siguiente corta» se midió contra el código.

Reglas del módulo: casos sintéticos, toda prueba nueva con su mutación, la sonda antes del commit.

## Entregable (pieza 8)

Este `.md`, sin renderizar, y `CLAUDE.md` al día: la evidencia del panel Reefer, el freno de la fecha de MAERSK y
la red en 239 pruebas.

**Para la prueba con el candado cerrado:** CMA deja además `cma_f<fila>_reefer_panel.*` y
`cma_f<fila>_reefer_guardado.*` en la carpeta de la corrida. MAERSK sigue eligiendo la fecha hasta que decidas.
