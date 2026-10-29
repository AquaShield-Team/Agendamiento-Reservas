# CICLO-hyundai-contrato-texto-completo · Encargo 90: «Contract No» de HYUNDAI acepta también el texto completo de la opción

> **metodo-ciclo v39** (la misma del disco). Base: `main` en `8cb4af5`, árbol limpio. **Dos commits:** el cambio
> (`25e646f`) y este informe. **No se subió nada:** el bloque de push está al final. Sin datos de clientes ni de la
> cuenta: los log.txt y `config.json` se leyeron en su lugar, en solo lectura y en memoria, y de ahí salieron solo
> cuentas; las pruebas usan contratos inventados.

## Qué se pidió y qué salió

Tus decisiones sobre lo que dejó el encargo 89:
1. Aceptar también el contrato escrito como el texto entero de la opción: comparación exacta contra el código o contra
   el texto completo, nunca «contiene»; medir que las 20 filas sigan igual.
2. El contrato en el motivo se queda, saneado y con su tope.

Además, la pregunta de si el paso 2 le quita los espacios al contrato (si no, sumarlo), y las 4 mutaciones de MAERSK
con el texto repetido, para su ciclo.

**Las 20 filas siguen igual** (abajo), y el cambio queda en `_hmm_contratos_que_calzan` y en los textos que la
describen: no toca otra naviera ni otro paso.

**El paso 2 ya le quitaba los espacios al contrato:** entró en el encargo 89 (`60bbd25`). Las dos líneas del contrato de
`reservar_hyundai`, la del paso 2 y la del 3, son `str(creds.get("contrato") or "").strip() or …`, y
`test_ayudantes.TestContratoDeHyundai.test_los_motivos_dicen_donde_se_escribe` lee las dos del código y exige esa forma.
No hubo que sumar nada.

## Paso 0 (medido)

`.trabajo/e90/medir_texto.py` importa la lectura de las filas de `.trabajo/e89/medir_exacto.py` (no la copia), sobre los
50 log.txt de `logs/` y de «1. pruebas», con 0 descartados, y `config.json`, leído en memoria. En las 20 filas de HYUNDAI
que llegaron a la guarda:
- con el contrato configurado hoy, la regla del 89 (el código) y la del 90 (el código o el texto completo) eligen una
  sola opción, y la misma: 20 de 20;
- con el texto completo de la opción elegida como contrato, la regla del 90 elige esa misma y la del 89 ninguna: 20 de
  20 (es el control de que la regla nueva hace lo que se pidió);
- con el contrato sin su último carácter, ninguna de las dos elige: 20 de 20 (sigue sin «contiene»).

**Ninguna fila cambia.** Control positivo que aborta: el total de 20 filas a la guarda, las 3 de la corrida del 28-10 de
este equipo, y el texto completo, que la regla nueva tiene que elegir en las 20. **LÍMITE:** el contrato configurado en las
corridas viejas pudo ser otro; se midió el de hoy, como en el 89.

## El cambio · `25e646f`

- **`_hmm_contratos_que_calzan`:** una opción calza si su código (`_hmm_codigo_del_contrato`, el texto antes del primer
  « - ») o su texto completo es el contrato entero, los dos sin los espacios de los extremos y sin distinguir mayúsculas;
  nunca «el texto lo contiene». Así calzan «CT-1» y «CT-1 - (GA)», escritos como contrato, y no un pedazo ni un alargue.
  Dos opciones que calzan siempre comparten el código: si el contrato no trae « - », el texto completo que lo iguala es
  también su código; si lo trae, no puede igualar un código.
- **El motivo de «no está»** dice que se compara con el código o con el texto completo. El contrato sigue saneado y con
  su tope, y CLAUDE.md anota que lo confirmaste.
- **Pruebas** (`test_ayudantes.TestContratoDeHyundai`):
  - una nueva, `test_acepta_el_texto_completo_de_la_opcion`: el texto completo elige su opción, en mayúsculas o
    minúsculas, con espacios en los extremos del contrato y de la opción;
  - `test_el_contrato_se_compara_entero` suma un pedazo, un alargue y un sufijo del texto completo, que no calzan;
  - `test_si_dos_tienen_el_mismo_codigo_no_elige_la_primera` fotografía el contrato escrito con el texto completo de una
    de dos opciones que comparten el código (abajo, la revisión de código).
- **Mutaciones:** 3 del encargo 90 (sin el texto completo, distinguiendo mayúsculas en la opción, con los espacios de la
  opción); tres del 89 que anclaban en las líneas cambiadas, a sus líneas nuevas; y la que quita la comprobación de la
  opción elegida suma la prueba de las dos opciones.
- **CLAUDE.md:** la regla, el motivo, lo medido, el contrato en el motivo como decisión tuya, sin el residual que se
  cerró, la lista de motivos de NO ENVIADA y el número de pruebas (1021).

## Compuertas

| compuerta | resultado |
|---|---|
| Censo de las mutaciones de «Contract No» (`--filtro TestContratoDeHyundai`), el final | 30 mutaciones, 32 pares, los 32 muerden; control (la copia sin mutar, 12 pruebas) pasa; 1.021 pruebas, 0 sin mutación; foto de los originales sin cambios; `RESULTADO: OK`, exit 0 |
| El mismo censo, antes de los arreglos de la revisión de código | 30 mutaciones, 31 pares, los 31 muerden; `RESULTADO: OK`, exit 0 |
| Las mutaciones que miran el contrato en `reservar_hyundai` (`test_hyundai_sin_contrato_no_elige_a_ciegas`, `contrato-hyundai-fijo`) | No se repitieron: este encargo no cambia sus anclas ni sus pruebas (en `reservar_hyundai` cambió solo un comentario); el 89 las dejó en verde |
| Suite completa, sobre el árbol del commit | `Ran 1021 tests in 2793.923s · OK`, foto de los originales sin cambios, `RESULTADO: OK`, exit 0 (con el tope de la corrida subido a 3.600 s) |
| Sonda de secretos | 0 con `--dry-run` y 0 después del `git add`, en los dos commits |
| Guarda de datos (hook pre-commit) | 0 hallazgos en los 128 archivos del cambio |
| Guarda de datos sobre los mensajes de los commits y el informe | 1 en cada mensaje: la línea `Co-Authored-By`, la dirección pública de atribución, como en los commits de antes (no es un dato); 0 en el informe |
| Las pruebas que leen lo versionado, con este informe preparado | `test_guarda_datos` y `test_sonda`: `Ran 32 tests · OK`. La suite completa no se repitió para el commit del informe: no toca código ni pruebas |

El censo y la suite los corrió un ayudante, uno detrás de otro, con el envoltorio de la salida literal; las salidas las
leí yo, en `.trabajo/e90/` (`censo_contrato.out`, `censo_contrato_2.out`, `suite.out`). Los tiempos son de reloj, no una
medición de tiempo.

## Las revisiones

Una a la vez, cada una sobre un clon en `.trabajo/e90/clon`, sin remoto.

| Revisión | Hallazgo | Qué se hizo |
|---|---|---|
| Código | Aprobado: nada calza por «contiene», y el texto completo no deja elegida una opción equivocada (la comprobación lo frena siempre). Sus 31 mutaciones del 89 y del 90 caen, en copias propias | — |
| Código | BAJA: con dos opciones del mismo código, el contrato escrito con el texto completo de una la separa en la regla, pero la elección va por el valor, que comparten, y queda la primera: si no es la del contrato, NO ENVIADA «quedó otra opción». CLAUDE.md decía que escribirlo de otra forma no las distingue, y ninguna prueba fijaba el caso | Corregido CLAUDE.md, y la prueba de las dos opciones lo fotografía, con su mutación de guardia |
| Código | BAJA: CLAUDE.md («si ninguna opción tiene el código») y el docstring de la clase de pruebas hablaban solo del código | Al día |
| Código | BAJA: el paso 2 recibe ahora también el contrato con el texto completo y elige por «contiene»; nunca da otro contrato (con un texto más largo, da la misma opción que con el código, o ninguna), pero si su lista no lo trae, queda el del portal sin avisar | Residual (abajo); el contrato final lo elige y lo comprueba el paso 3 |
| Código | Observación: los espacios de adentro no se juntan; «CT-1  -  (GA)», con espacios dobles, queda NO ENVIADA, y el motivo lo muestra con los espacios de a uno, igual que la opción | Residual (abajo): es el lado seguro |
| Seguridad | Sin hallazgos críticos ni altos: ningún camino deja seguir la reserva con otra opción de la lista; el código de una opción nunca trae « - » (medido sobre todo Unicode), así que el texto completo y el código no se cruzan; el motivo sigue saneado; el candado no cambia | — |
| Seguridad | BAJA, hipotética: dos opciones con el mismo valor («… - (GA)» y «… - (FMC)», con el valor del código), y el contrato escrito con el texto completo de la primera: la reserva sigue, con la lista en esa opción y el mismo valor que la otra; con el orden al revés, NO ENVIADA. Con el 89 se cortaba siempre | Residual, y lo decides tú (abajo). La página queda como si una persona eligiera esa opción a mano; la asimetría por el orden es la de elegir por el valor, el residual del 89. No se vio: la lista trajo siempre una sola opción real |
| Seguridad | Info (del 89): Python y JavaScript no recortan los mismos caracteres de los extremos (U+0085, U+001C–U+001F, U+FEFF), y la comprobación compara contra `calzan[0].strip()` | Residual: da NO ENVIADA de más (el lado seguro); comparar contra `calzan[0]` tal cual lo cerraría |
| Seguridad | Info: las mayúsculas de Unicode juntan letras distintas («ı», «ſ», «ß», «ﬁ»), ahora también en el texto completo; el filtro de lo que no es contrato compara en minúsculas | Residual: los códigos del portal son ASCII; Python y Node dan la misma mayúscula para esas letras |
| Seguridad | BAJA (de antes del 89): la línea «Contract No opciones» y el valor elegido van a log.txt sin sanear; una opción con un salto de línea agrega una línea | Residual; el motivo y la línea «quedó con «…»» sí van saneados |
| Seguridad | Info: se compara con el `textContent`, no con lo que se ve; espacios duros o dobles en la opción no calzan con el texto copiado de la pantalla | Residual: NO ENVIADA, el lado seguro |

## Decisiones que tomé (Modo autónomo)

| Decisión | Por qué | Cómo se deshace |
|---|---|---|
| El texto completo se compara como el código: sin los espacios de los extremos y sin distinguir mayúsculas, en los dos lados, sin juntar los de adentro | Es lo que pediste («comparación exacta»), con la misma tolerancia que ya tenía el código | Una línea en `_hmm_contratos_que_calzan` |
| La elección de dos opciones del mismo código no cambia: se fotografía, y la frena la comprobación | La revisión lo dio por BAJA y del lado seguro; elegir por índice es el residual del 89 | — |
| El paso 2, al residual | Ya era un residual del 89; el contrato final lo decide el paso 3 | — |

## Lo que salió mal

- **Dos textos quedaron hablando solo del código** (un punto de CLAUDE.md y el docstring de la clase de pruebas), y uno
  decía que escribir el contrato de otra forma no distingue dos opciones del mismo código, que dejó de ser cierto con el
  texto completo. Lo encontró la revisión de código.
- **Al poner al día CLAUDE.md, un reemplazo juntó dos líneas en una de 161 caracteres:** lo vio mi propia medida del largo
  de las líneas nuevas, antes de las revisiones.

## Residual

- **El paso 2** recibe el contrato tal como se escribió, también el texto completo, y lo elige por «contiene», tragando
  sus errores (de antes del 89). Nunca da otro contrato, pero si su lista (`cboContractNoForAlternativeRoute`) no trae
  ese texto, deja el del portal sin avisar. Se puede medir sin abrir el portal: hay 42 HTML guardados con esa lista en
  `logs/`. **Reapertura:** que lo encargues.
- **Dos opciones con el mismo código y el mismo valor** (no se vio nunca): escrito el texto completo de la primera, la
  reserva sigue, con la lista en esa opción, como si una persona la eligiera a mano, y el formulario con el valor que
  también tiene la otra; escrito el de la segunda, queda la primera, y la fila queda NO ENVIADA, «quedó otra opción», sin
  decir por qué (log.txt dice cuál quedó). **Lo decides tú:** cortar también el primer caso (cuando el valor de la opción
  elegida lo comparte otra opción real), o dejarlo así. **Reapertura de la asimetría:** elegir por el índice de la
  opción (el residual del 89).
- **De la revisión de seguridad, del lado seguro o de antes:** Python y JavaScript no recortan los mismos caracteres de
  los extremos; las mayúsculas de Unicode juntan letras distintas; la línea «Contract No opciones» va a log.txt sin
  sanear; y la opción con espacios duros o dobles no calza con el texto copiado de la pantalla.
- **Los espacios de adentro no se juntan:** «CT-1  -  (GA)» queda NO ENVIADA, y el motivo lo muestra como la opción.
  **Reapertura:** si un equipo lo escribe así.
- **Las 4 mutaciones de MAERSK con el ancla doble** (las del 86), para su ciclo, por tu decisión.
- **«Named Customer» y «HMM Sales Person»** siguen eligiendo por posición (el residual del 89, para un ciclo propio).
- **No está probado en el portal:** la regla no pulsa nada nuevo.

## Re-medir

- Las filas guardadas: `python .trabajo/e90/medir_texto.py` (con el Python de la Tienda; lee `logs/`, «1. pruebas» y
  `config.json` en solo lectura, e imprime cuentas).
- Las pruebas: `python -m unittest test_ayudantes.TestContratoDeHyundai test_ayudantes.TestContratosPorDefecto`, desde
  `tests/`.
- El censo: `python tests/correr.py --mutaciones --filtro TestContratoDeHyundai`.

## NO retroceder

- No volver a «el texto de la opción contiene el contrato», tampoco para el texto completo.
- No sacar el texto completo de la regla: un contrato copiado de la lista tal cual quedaría NO ENVIADA.

## Reglas aplicadas

metodo-ciclo v39: medir antes de cambiar, con control positivo que aborta y la lectura de las filas importada, no
copiada (fuente única); el cambio y su guardián en la misma operación; el negativo que muerde (el censo); todas las
suites antes de cada commit; las dos revisiones en un clon, una a la vez; el modo autónomo, con su tabla; el ayudante
mecánico con la salida literal, leída por la sesión; la limpieza dentro de la carpeta que borra. No chocaron con las
reglas del módulo.

## Push

Dos commits de `main` sin subir: `25e646f` (el cambio) y este informe. GitHub tiene `8cb4af5` (medido con
`git ls-remote` al cerrar: el encargo 89 ya está subido). Los dos, con el correo noreply de autor y de committer. Antes de
subir, en una consola:

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
