# CICLO · HYUNDAI deja la pantalla del Remark antes de escribirlo

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-24 · **Método:** skill `metodo-ciclo` v13 ·
**Base:** `f527908` (último de código: `cad1ae0`) · **Commits** (locales, sin push; el repo no tiene remoto):
`eb94499` con el cambio y el de este informe.

> Sin datos reales. Lo de `logs/` se midió en su lugar y en solo lectura, con sondas que imprimen conteos y nombres
> de etiquetas y de atributos; ningún valor ni texto del portal.

## Qué cambió

En `reservar_hyundai`, justo antes de escribir el Remark (después de marcar Non-waste), una sola sentencia suelta con
el mecanismo de evidencia existente:

```python
_evidencia_antes_de_la_guarda(page, reg, f"hmm_f{f}_remark", "antes de escribir el Remark", completa=False)
```

- Deja en la carpeta de la corrida `hmm_f<fila>_remark.png` (la ventana), `hmm_f<fila>_remark.html` y un
  `hmm_f<fila>_remark_marco<n>.html` por marco, y lo anota: «evidencia antes de escribir el Remark: …».
- Si algo falla, lo avisa en pantalla y en `log.txt`, y la reserva sigue: «⚠ No pude guardar la evidencia antes de
  escribir el Remark (hmm_f<fila>_remark): … La reserva sigue igual; si necesitas medir esta pantalla, vuelve a correr
  la fila con el candado cerrado.» El Remark se escribe igual.
- **La escritura del Remark no cambia:** su FRENO sigue. En `AQUASHIELD.py` hay 9 líneas agregadas y 0 borradas:
  - la llamada;
  - su comentario de 2 líneas;
  - una línea en blanco;
  - 5 líneas del docstring de `_evidencia_antes_de_la_guarda`.

## El freno, medido

El FRENA SI dice: «guardar la evidencia exige esperar o interactuar con la página». No se cumple:
- **No hace falta esperar:** la llamada va después de las esperas que ya había para esa pantalla (el `esperar_hasta`
  de «Non-waste» o de un textarea visible, el reintento y `_hmm_no_residuo`).
- **No interactúa:** `_evidencia_antes_de_la_guarda` toma una captura y lee el HTML con `_JS_HTML_COMPLETO`, sin clics,
  teclas, esperas ni navegación. `test_solo_lee_sin_clics_ni_navegacion_ni_esperas` lo vigila.
- **Lo que Playwright hace por dentro en cada captura** (leído en la fuente instalada, Playwright 1.58.0,
  `screenshotter.js`): oculta el cursor de texto de los campos y lo repone, y espera `document.fonts.ready`.
  - Pasa en todas las capturas del programa, también en `hmm_f<fila>_4_additional`, que ya se toma de esta misma
    pantalla justo después del Remark.
  - En Chrome 153, la captura de la ventana dio 0 `resize` y solo esas 2 mutaciones del cursor
    (`CICLO-evidencia-en-la-guarda.md`). No lo volví a medir con un navegador.

## Expectativas que cambiaron (antes → ahora)

| Prueba | Antes | Ahora |
|---|---|---|
| `test_evidencia.test_solo_ahi` | 12 llamadas a `_evidencia_antes_de_la_guarda`; `reservar_hyundai`, una vez (su guarda) | 13; `reservar_hyundai`, dos veces (su guarda y el Remark) |

- `test_candado` no cambia: los textos nuevos no calzan con su expresión de «enviar» (medido).
- `test_clics` no cambia: su foto da lo mismo, con las 2 formas del Remark (FRENO).
- Red: de 261 a 264 pruebas, de 539 a 543 mutaciones y de 648 a 657 pares.
  - `TestEvidenciaRemarkHyundai` toma de `reservar_hyundai` la llamada y el `try` que escribe el Remark, tal como están.
    Los corre sobre una página falsa: primero la ventana y el HTML, después el Remark.
  - Si la página falla, avisa y el Remark se escribe igual.
- Los 4 defectos inyectados (`hmm-remark-*`):
  - quitar la evidencia;
  - pedir la página completa;
  - guardar sin la protección del mecanismo, que corta la reserva antes del Remark;
  - agregarle una espera delante.

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\correr.py --mutaciones --filtro hmm-remark
python tests\correr.py --mutaciones
cd tests; python -m unittest test_evidencia.TestEvidenciaRemarkHyundai
```

Las tres sondas de `logs/` son de solo lectura y viven fuera del repo:
- **Conteo:** cada `.html` de las carpetas de corrida. De los de HYUNDAI (`hmm_`), cuántas veces traen `<textarea`,
  «remark» y «non-waste». Control positivo: un texto sintético con un textarea y «Remark» da 1 y 1.
- **Estructura:** en los mismos archivos, los nombres de los atributos de cada textarea, si alguno nombra «remark» y
  en qué etiqueta aparece la palabra. Control positivo: un HTML sintético con `textarea id="remark"`.
- **Cuadre:** las apariciones de «remark» por tipo de nodo (texto, comentario o atributo), que tienen que sumar lo
  mismo que el conteo crudo. Control positivo: un HTML sintético con una de cada tipo.

## NO retroceder (pieza 2)

- **No muevas la evidencia después del Remark ni le agregues una espera delante:** cae
  `test_va_justo_antes_del_remark_como_sentencia_suelta`.
- **No la cambies por llamadas directas a la captura y al HTML:** sin la protección del mecanismo, una falla
  corta la reserva antes del Remark. La mutación `hmm-remark-evidencia-sin-proteger` lo muestra.
- **No cambies el Remark a partir de este HTML sin tu decisión:** su FRENO sigue.

## Premisas del encargo contrastadas (pieza 5)

- **«Ningún HTML guardado muestra esa pantalla»:** confirmada. En `logs/` hay 36 HTML y 2 son de HYUNDAI: la guarda
  de la fila 25 (Review & Book) y su marco.
  - Ninguno trae «Non-waste», la etiqueta con que el programa reconoce Additional Information.
  - En la guarda, los 8 textarea llevan un índice de fila (`data-rowidx`) y ninguno nombra «remark» en sus
    atributos.
  - «remark» aparece 5 veces en esa guarda: 4 dentro de un script y 1 como texto de un `div`, ninguna en un
    atributo. Ahí el Remark se muestra como texto, no como campo.
  - El marco trae 4 textarea y ningún «remark».
  - Ninguna evidencia guardada dice cuál era el primer textarea visible en Additional Information.
- **«El prefijo que ya usa HYUNDAI»:** confirmado, `hmm_f<fila>_…`.
- **«Sus 5 reservas confirmadas del 21 de septiembre»:** viene de `CICLO-cola-nueve-items.md`; no la volví a medir.

## Universo y cobertura (pieza 3)

- **`logs/`:** 36 HTML en las carpetas de corrida, 2 de HYUNDAI y 0 descartados. Además hay 6 capturas
  `hmm_f*_4_additional.png`, sin HTML.
- **Código:** 1 sentencia nueva en `reservar_hyundai`. Las 12 llamadas que ya había a la evidencia no cambian.

## Defectos de instrumento cazados (pieza 4)

1. **El docstring de `_evidencia_antes_de_la_guarda` no nombraba a los tres llamadores del encargo 21:** MAERSK sin
   nave, ONE detenida y COSCO con varios itinerarios. Era un registro mío, desactualizado desde `2cabddf`. Ahora los
   nombra a los tres, además del nuevo.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| El Remark de HYUNDAI se escribe en el primer textarea visible | FRENO: todavía no hay HTML de esa pantalla | …una corrida con el candado cerrado deja `hmm_f<fila>_remark.html` |
| Un `style` vacío en los campos del HTML | Hipótesis sin medir: al reponer el cursor, la captura podría dejar un `style` vacío en campos que no lo tenían | …alguien quiere identificar un campo por su `style` |
| Lo demás de `CICLO-cola-nueve-items.md` | No es parte de este encargo | …según cada fila de ese informe |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v13**. La v13 solo pasó a tuteo un ejemplo que estaba en voseo; las reglas son las de la v12.
- **PASO 0 con veredicto:** CICLO. El freno se midió antes de tocar el código y no se cumplió.
- **Re-medir contra HEAD antes de diseñar:** la suite sobre `f527908` (261, verde) y la premisa en `logs/`.
- **Control positivo que aborta:** en las tres sondas.
- **La unidad la fija el sujeto:** el Remark se escribe en un campo, así que se contó por campo y por nodo, no por
  archivo. Las 5 apariciones crudas de «remark» resultaron ser texto, no campos.
- **El negativo tiene que morder:** 4 mutaciones, con el censo filtrado en la puerta y el censo completo al cerrar.
- **Un gate en cero no prueba el efecto:** lo prueba `TestEvidenciaRemarkHyundai`, que corre las sentencias reales, con
  sus negativos.
- **Fuente única:** se usó el mecanismo existente, sin copiarlo.
- **Cada reemplazo afirma su viejo una vez, y el EOL se preserva:** CR en 0 en los archivos tocados.
- **El cambio y su guardián en la misma operación, y se declaran el residual y las premisas.**
- **Choque:** ninguno. El FRENO del Remark y este cambio no chocan: la evidencia va antes y la escritura no se toca.

Reglas del módulo: casos sintéticos, la sonda de secretos antes de cada commit, nada de `logs/` en el repo y los
textos nuevos en español con tuteo.

## Entregable (pieza 8)

Este `.md`, sin renderizar, y `CLAUDE.md` al día.

**Gate y cierre:**
- **Gate del commit de código (`eb94499`):**
  - la suite completa: 264 pruebas en verde y 0 cambios en los originales;
  - el censo filtrado a `hmm-remark`: 4 mutaciones y 9 pares, y muerden todos, cada uno por su motivo;
  - el censo de las mutaciones de `test_solo_ahi`, cuya expectativa cambió: 14 y 30 pares, y muerden todos;
  - la sonda de secretos en 0 sobre el staging.
- **Censo completo final sobre `eb94499`:** pasó, en 19 minutos.
  - 264 pruebas en verde, y el control (la copia sin mutar) pasa;
  - 543 mutaciones y 657 pares, y muerden todos;
  - 0 pruebas sin mutación y 0 cambios en los originales.
- **El commit de este informe** solo agrega este `.md` y cambia `CLAUDE.md`. Ninguna prueba los lee: el único `.md`
  que lee la red es `LEEME.md`. Por eso el censo sobre `eb94499` vale también para él.

**Para tu próxima prueba con el candado cerrado:**
- Sirve la misma que propone `CICLO-cola-nueve-items.md`: una corrida «todas» con una fila por naviera. Ahí HYUNDAI
  (fila 25) deja además la evidencia del Remark, así que no hace falta otra corrida.
- En su carpeta quedarán `hmm_f25_remark.png` y `hmm_f25_remark.html`, con la pantalla antes de escribir el Remark.
- Con ese HTML se identifica el campo por su etiqueta o por un atributo propio. La captura `hmm_f25_4_additional.png`,
  tomada después, muestra en qué campo quedó escrito.
- Con eso se puede cerrar el FRENO, si lo decides.
