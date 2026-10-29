# CICLO-hyundai-valor-compartido-y-paso2 · Encargo 91: «Contract No» de HYUNDAI, el valor compartido, el paso 2 exacto y el log saneado

> **metodo-ciclo v39** (la misma del disco). Base: `main` en `5fea309`, árbol limpio; GitHub tiene `5fea309`
> (medido con `git ls-remote` al cerrar). **Dos commits:** el cambio (`6419527`) y este informe. **No se subió
> nada:** el bloque de push está al final. Sin datos de clientes ni de la cuenta: los log.txt, el HTML guardado y
> `config.json` se leyeron en su lugar, en solo lectura y en memoria, y de ahí salieron solo cuentas; las pruebas usan
> contratos inventados.

## Qué se pidió y qué salió

Tu decisión sobre la pregunta del encargo 90, y un loop en el mismo frente:
- **Decisión:** si dos opciones de «Contract No» comparten el valor, NO ENVIADA, se haya escrito el texto completo de la
  primera o el de la segunda.
- **(1)** El paso 2 pasa de «contiene» a comparación exacta. Antes, medir en el HTML de `logs/` que ninguna fila cambie
  de resultado, y frenar si alguna cambia.
- **(2)** Sanear la línea «Contract No opciones» de log.txt.
- «Named Customer», «HMM Sales Person» y las mutaciones de MAERSK siguen para su ciclo.

**No cayó en el FRENA:** en el paso 2 ninguna fila cambia de resultado (abajo). El cambio queda en «Contract No» de
HYUNDAI: no toca otra naviera.

## Paso 0 (medido)

- **El paso 2** (`.trabajo/e91/medir_paso2.py`):
  - la lista de contrato del paso 2 es la que encuentra el programa: el primer `select` del documento cuyo id o name trae
    «contract», fuera de las raíces shadow;
  - en el HTML que 17 corridas guardaron justo antes del paso 2 (`hmm_f<fila>_destino`), hay una sola, y viene sin
    opciones; tampoco trae opciones en ningún HTML de HYUNDAI de después (77 listas en total);
  - de las 17 filas, las 10 con contrato dijeron «sin opción para» y las 7 sin contrato (las del colega) no la miraron;
  - ni «contiene» ni la regla exacta eligen nada: **ninguna fila cambia**;
  - el control positivo, que aborta: lo que predice «contiene» sobre el HTML es lo que log.txt dice que hizo el paso 2, en
    las 10. La primera corrida de la sonda abortó en las 7 sin contrato, que dicen otra cosa porque no llaman a la lista;
    se separaron (ese camino no cambia).
  - La regla nueva no se copió: la sonda toma del programa `_hmm_contratos_que_calzan` y la ejecuta.
- **El paso 3** (`.trabajo/e91/medir_paso3.py`): **apareció el HTML del paso 3**, en los 7 cortes de «Contract No» de las
  corridas del colega (`hmm_f<fila>_sin_objetivo.html`, en «1. pruebas»; en `logs/` de este equipo, ninguno).
  - Cada lista trae 4 opciones y 1 real.
  - El valor de la real es su código, lo que el encargo 89 había inferido de log.txt.
  - Ningún valor se repite: «Select» trae el valor vacío, y «Dummy» y «Direct Input», valores distintos del de la real.
  - El corte por el valor compartido no habría cortado ninguna de esas listas.

### Premisas que se corrigieron

- **«El HTML del paso 3 no se guardó nunca»** (CLAUDE.md desde el encargo 89): se guardó en los 7 cortes del colega, en
  «1. pruebas». El 89 buscó solo en `logs/`.
- **«La elección va por el valor»** (encargo 90): `select_option(value=…)` de Playwright para Python elige por el valor o
  por la etiqueta (lo midió la revisión de código, en el Chromium de Playwright 1.58).
- **Los 42 HTML del encargo:** eran las listas `cboContractNoForAlternativeRoute` de todo el HTML de HYUNDAI de `logs/`,
  de antes y de después del paso 2 (el origen, el destino, la lista de naves y el modal de otra nave). Con «1. pruebas»
  son 77, y las que deciden el paso 2 son las de justo antes, 17.

## El cambio · `6419527`

- **Paso 3, el valor compartido** (`_hmm_valor_compartido`): si otra opción responde al valor de la que calza, la fila
  queda NO ENVIADA, sin elegir nada: «no encontré una sola opción con el contrato «…»: el portal da el mismo valor a N
  opciones, y al elegir no se distinguen». Cuenta tanto otra opción con ese valor (un contrato del mismo código, o
  «Select», «Dummy» o «Direct Input») como otra con esa etiqueta. Hasta ahí, con el texto de la primera de dos opciones
  con el mismo valor, la reserva seguía.
- **`_JS_HMM_CONTRATOS`** recibe el selector por argumento, y de cada opción da el texto, el valor y la etiqueta
  (`_hmm_pares`).
- **Paso 2** (`_hmm_contrato_paso2`, `HMM_LISTA_PASO2`): elige solo la única opción cuyo código o texto completo es el
  contrato, como el paso 3, y solo si ninguna otra responde a su valor. La elige por ese valor. Si no, no elige nada y no
  corta: queda el del portal, como antes. Si la lectura o la elección fallan, tampoco corta. Hasta ahí,
  `_hmm_select_por_texto` elegía la primera opción que contenía el contrato.
- **log.txt** (`_destino_a_la_vista`): la línea «Contract No opciones», las líneas del paso 2 (también sus errores) y el
  error al leer la opción elegida del paso 3 van saneados. Un salto de línea ya no parte la línea.
- **Pruebas:**
  - `test_ayudantes.TestContratoPaso2DeHyundai`, nueva, con 4 pruebas del paso 2: elige solo la que calza exacto, por su
    valor; sin una que calce, no elige (la lista vacía, un contrato a medias, dos del mismo código, el valor compartido,
    una cuya etiqueta es el valor); si falla, no corta; y lo del portal va saneado;
  - en `TestContratoDeHyundai`:
    - el valor compartido, las dos veces, también con «Select»;
    - la etiqueta;
    - con el mismo código y valores distintos, el texto completo elige la suya;
    - la línea de opciones saneada;
    - el error saneado;
    - el JavaScript en Node, con la etiqueta y con el selector que recibe;
  - `test_hyundai_sin_contrato_no_elige_a_ciegas` exige `_hmm_contrato_paso2` dentro de «if ctto», y ninguna llamada a
    `_hmm_select_por_texto` con el contrato.
- **Mutaciones:**
  - 17 del encargo 91;
  - las anclas de cuatro que miraban las líneas cambiadas (`e89-js-opciones-sin-recortar`, `e91-js-sin-valores`,
    `e91-valor-compartido-cuenta-uno`, `e91-paso2-contiene`) y la de `e86-la-primera-de-varias` (abajo, la revisión de
    código);
  - `e89-sigue-si-queda-otra` ya no nombra la prueba de las dos opciones, que ahora corta antes de la comprobación.
- **CLAUDE.md:** la regla, el paso 2, el log, lo medido, el HTML del paso 3, el residual, la lista de motivos de NO
  ENVIADA y el número de pruebas (1025).

## Compuertas

| compuerta | resultado |
|---|---|
| Censo de las mutaciones de contrato (`--filtro TestContrato`), el final | 68 mutaciones, 73 pares, los 73 muerden; control (la copia sin mutar, 24 pruebas) pasa; 1.025 pruebas, 0 sin mutación; foto de los originales sin cambios; `RESULTADO: OK`, exit 0 |
| El mismo censo, antes de los arreglos de la revisión | 64 mutaciones, 69 pares: 68 muerden, y `e89-sigue-si-queda-otra` no muerde la prueba de las dos opciones (un par viejo; abajo, «Lo que salió mal») |
| Censo de `e89-sigue-si-queda-otra`, sin ese par | 1 y 1: muerde su prueba; `RESULTADO: OK`, exit 0 |
| Censo de `e86-la-primera-de-varias`, con su ancla nueva | 1 y 1: muerde su prueba de MSC; `RESULTADO: OK`, exit 0 |
| Las anclas de las 2.871 mutaciones | Una sola vez cada una, salvo las 4 de MAERSK ya conocidas (residual, para su ciclo) |
| Suite completa, sobre el árbol del commit | `Ran 1025 tests in 1302.930s · OK`, foto de los originales sin cambios, `RESULTADO: OK`, exit 0 (con el tope de la corrida subido a 3.600 s) |
| Sonda de secretos | 0 con `--dry-run` y 0 después del `git add`, en los dos commits |
| Guarda de datos (hook pre-commit) | 0 hallazgos en los 129 archivos del cambio |
| Guarda de datos sobre los mensajes de los commits y el informe | 1 en cada mensaje: la línea `Co-Authored-By`, la dirección pública de atribución, como en los commits de antes (no es un dato); 0 en el informe |
| Las pruebas que leen lo versionado, con este informe preparado | `test_guarda_datos` y `test_sonda`: `Ran 32 tests · OK`. La suite completa no se repitió para el commit del informe: no toca código ni pruebas |

Los censos y la suite los corrió un ayudante, uno detrás de otro, con el envoltorio de la salida literal; las salidas las
leí yo, en `.trabajo/e91/` (`censo_*.out`, `suite.out`). Los tiempos son de reloj, no una medición de tiempo.

## Las revisiones

Una a la vez, cada una sobre un clon en `.trabajo/e91/clon`, sin remoto.

| Revisión | Hallazgo | Qué se hizo |
|---|---|---|
| Código | ALTA: la línea nueva `if len(calzan) != 1:` del paso 2 repetía el ancla de `e86-la-primera-de-varias` (MSC): el censo completo la daría por error, y el defecto que vigila quedaba sin mutante | Arreglado: su ancla suma la línea que le sigue en MSC; y la sesión comprueba ahora las anclas de todas las mutaciones, no solo las del frente |
| Código | MEDIA: `select_option(value=…)` de Playwright para Python elige por el valor o por la etiqueta: una opción cuyo texto es el valor de la que calza quedaba elegida en su lugar (en el paso 2 sin aviso; en el 3 lo frenaba la comprobación) | Arreglado: el JavaScript lee la etiqueta, y una opción que responde al valor como etiqueta cuenta como que lo comparte, en los dos pasos; con su prueba y su mutación |
| Código | BAJA: ninguna prueba veía que el JavaScript dejara de usar el selector que recibe | Arreglado: la prueba en Node le pide también la lista del paso 2, con su mutación |
| Código | BAJA: el paso 3 seguía escribiendo errores sin sanear, y CLAUDE.md daba a entender lo contrario | Arreglado el de «err al leer la opción elegida»; los de `_hmm_select_por_texto` (el ayudante común), residuales, y CLAUDE.md lo dice |
| Código | Observación: con una lista dentro de una raíz shadow, `querySelector` y Playwright toman listas distintas | Residual (ya pasaba antes; en lo medido hay una sola lista, en la página) |
| Seguridad | Sin hallazgos críticos ni altos: la regla nueva hace lo que promete en un Chromium de verdad (la etiqueta compartida corta; sin ella, sigue), el paso 2 no corta nada ni se traga un corte, y lo saneado sale saneado | — |
| Seguridad | BAJA (de los encargos 89 y 90; ahora la usa también el paso 2): `upper()` convierte letras que no son ASCII en ASCII («ſ» en «S», «ı» en «I», «ß» en «SS»): una opción «ſT-1 - (GA)» calza con el contrato «ST-1», y la comprobación pasa | Residual: tendría que ofrecerla el propio portal. El arreglo: mayúsculas solo de ASCII, o exigir que el contrato y el código lo sean |
| Seguridad | BAJA (el residual de la raíz shadow, ahora medido): en el paso 2, con una lista que calza dentro de una raíz shadow antes de la de la página, se lee una y se elige en la otra, y log.txt dice que eligió bien | Residual: el contrato lo vuelve a elegir y lo comprueba el paso 3, donde no se repite. El arreglo: elegir sobre el mismo elemento que se leyó y volver a leer qué quedó |
| Seguridad | BAJA (sin medir): la comprobación final del paso 3 mira el texto de la elegida, no vuelve a contar el valor compartido; si el portal sumara otra opción con ese valor en los milisegundos entre la lectura y la elección, no lo vería | Residual. El arreglo: leer en una sola llamada la elegida y todas las opciones, y volver a contar |
| Seguridad | Confirmó los residuales conocidos: `_hmm_select_por_texto` escribe sin sanear su valor y sus errores (solo en log.txt) | Residual |

## Decisiones que tomé (Modo autónomo)

| Decisión | Por qué | Cómo se deshace |
|---|---|---|
| El valor compartido cuenta cualquier opción, también «Select», «Dummy» y «Direct Input» | Tu regla dice «dos opciones»; si cualquiera responde al mismo valor, al elegir no se distinguen. En el HTML medido ninguna lo comparte | `_hmm_valor_compartido` |
| La etiqueta cuenta como el valor | Lo midió la revisión: Playwright elige por las dos | La misma función |
| El paso 2 elige por el valor (`select_option`), no con `_hmm_select_por_texto` | Con el valor único, elegir por él es exacto; `_hmm_select_por_texto` busca por «contiene» | Una línea en `_hmm_contrato_paso2` |
| El paso 2 no corta nunca | Así era; el contrato de la reserva lo elige y lo comprueba el paso 3 | — |
| Los errores de `_hmm_select_por_texto` siguen sin sanear | Es el ayudante común de las listas de HYUNDAI; el encargo pidió la línea de opciones | Residual |

## Lo que salió mal

- **Mi línea nueva repitió el ancla de una mutación de otro encargo,** y no lo vi: comprobé solo las anclas de las
  mutaciones de este frente. Lo encontró la revisión de código. Desde ahí, la comprobación mira las 2.871.
- **Una prueba mía comparaba el resultado entero con el estado:** lo vi al correrla.
- **Los arreglos de largo de línea juntaron líneas** (reemplazos que terminaban a mitad de línea), varias veces: terminé
  recortando cada párrafo con un script que verifica que el texto no cambie.
- **El censo de contrato encontró un par de mutación y prueba que ya no mordía:** `e89-sigue-si-queda-otra` contra la
  prueba de las dos opciones, que ahora corta antes de la comprobación. Se quitó ese par; la mutación muerde su propia
  prueba, 1 de 1.
- **La primera corrida de la sonda del paso 2 abortó** en las 7 filas sin contrato, que no llaman a la lista: el control
  hizo su trabajo, y se separaron.

## Residual

- **`_hmm_select_por_texto`** (el ayudante común de las listas de HYUNDAI) escribe tal cual en log.txt el valor que
  elige y sus errores. **Reapertura:** que lo encargues.
- **Una lista dentro de una raíz shadow** antes de la de la página: en el paso 2, `querySelector` y Playwright toman
  listas distintas, y log.txt dice que eligió bien (medido por la revisión de seguridad). Ya pasaba antes; en lo medido
  hay una sola lista, en la página, y el paso 3 vuelve a elegir y comprueba. **Reapertura:** si aparece; el arreglo es
  elegir sobre el mismo elemento que se leyó.
- **`upper()` y las letras que no son ASCII** (de los encargos 89 y 90): una opción con «ſ» o «ı» calza con el contrato
  escrito con «S» o «I». Tendría que ofrecerla el portal. **Reapertura:** que lo encargues.
- **La comprobación final del paso 3 no vuelve a contar el valor compartido:** una opción con ese valor que el portal
  sumara en los milisegundos entre la lectura y la elección no se vería. Sin medir.
- **«Named Customer» y «HMM Sales Person»**, para su ciclo. Los 7 cortes del colega en «1. pruebas» traen el HTML del
  paso 3 que ese ciclo necesita.
- **Las 4 mutaciones de MAERSK** con el ancla doble, para su ciclo. Con ellas el censo completo sigue dando error,
  como desde el encargo 86.
- **La regla del paso 2 no está probada en el portal:** su lista nunca trajo opciones en lo guardado.

## Re-medir

- Las filas: `python .trabajo/e91/medir_paso2.py` y `python .trabajo/e91/medir_paso3.py` (con el Python de la Tienda;
  leen `logs/`, «1. pruebas» y `config.json` en solo lectura, e imprimen cuentas).
- Las pruebas: `python -m unittest test_ayudantes.TestContratoDeHyundai test_ayudantes.TestContratoPaso2DeHyundai
  test_ayudantes.TestContratosPorDefecto`, desde `tests/`.
- El censo: `python tests/correr.py --mutaciones --filtro TestContrato` y `--filtro e86-la-primera-de-varias`.

## NO retroceder

- No volver a elegir en el paso 2 por «contiene».
- No volver a dejar seguir una reserva cuyo contrato comparte el valor con otra opción, como valor o como etiqueta.
- No escribir en log.txt sin sanear lo que se lee del portal en «Contract No».

## Reglas aplicadas

metodo-ciclo v39: medir antes de cambiar, con control positivo que aborta (abortó una vez, y se corrigió la sonda, no el
control); la regla del programa ejecutada, no copiada (fuente única); el cambio y su guardián en la misma operación; el
negativo que muerde (el censo, que encontró un par viejo); todas las suites antes de cada commit; las dos revisiones en
un clon, una a la vez; el modo autónomo, con su tabla; el ayudante mecánico con la salida literal, leída por la sesión;
la limpieza dentro de la carpeta que borra. No chocaron con las reglas del módulo.

## Push

Dos commits de `main` sin subir: `6419527` (el cambio) y este informe. GitHub tiene `5fea309`. Los dos, con el correo
noreply de autor y de committer. Antes de subir, en una consola:

```bash
git -C "C:\dev\Agendamiento Reservas" log origin/main..main --format="%h %ae %ce %s"
```

Tiene que mostrar solo el correo noreply en las dos columnas. Después:

```bash
git -C "C:\dev\Agendamiento Reservas" push origin main
git -C "C:\dev\Agendamiento Reservas" rev-parse main
git -C "C:\dev\Agendamiento Reservas" ls-remote origin refs/heads/main
```

Los dos hashes tienen que ser iguales. **`estable` no se movió:** el cambio les llega a los colegas solo cuando la avances
tú, después de probar HYUNDAI en modo prueba.
