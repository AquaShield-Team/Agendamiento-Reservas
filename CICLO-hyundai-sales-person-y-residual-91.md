# CICLO-hyundai-sales-person-y-residual-91 · Encargo 92: «HMM Sales Person», el freno de «Named Customer», el censo completo, el residual del 91 y las 5 caídas del 23-10

> **metodo-ciclo v39** (la misma del disco). Base: `main` en `64f9760`, árbol limpio; GitHub, medido con `ls-remote` el 2026-11-02: `main` en `64f9760` y `estable` en `b39c95c`. `estable` sigue en
> `b39c95c`: no se tocó. **Tres commits:** el frente 1 (`31dd439`), el frente 2 (`0d640d0`) y este informe. **No se
> subió nada:** el bloque de push, en PowerShell, está al final. Sin datos de clientes ni de la cuenta: los log.txt, el
> HTML guardado y `config.json` se leyeron en su lugar, en solo lectura y en memoria, y de ahí salieron solo cuentas y
> verdadero o falso; las pruebas usan datos inventados.

## Qué se pidió y qué salió

Un loop autónomo sobre la cola, en este orden y con un commit por frente:

| Frente | Qué salió |
|---|---|
| **1.** «Named Customer», «HMM Sales Person» y las 4 mutaciones de MAERSK que rompían el censo completo | **«HMM Sales Person», hecho:** elige solo su única opción real. **«Named Customer»: FRENO** (regla de negocio, abajo): sigue eligiendo como antes, y log.txt dice sus opciones. **Las 4 anclas de MAERSK, arregladas:** cada una vuelve a aparecer una vez en su archivo, y el censo completo da verde: 2.913 mutaciones y 3.676 pares, todos muerden, con la foto de los originales sin cambios (8 pares, repetidos con el equipo despierto: abajo, en «Compuertas») |
| **2.** El residual del encargo 91 | Los 4 puntos, hechos, y lo que encontraron sus revisiones |
| **3.** Las 5 reservas que fallaron el 23-10 | **Diagnóstico, sin arreglo nuevo:** las 5 ya las cubren los encargos 82 y 83, cuyos arreglos están en `estable` y no se probaron en el portal |

**El FRENA SI saltó una vez:** elegir «Named Customer» bien cambia una regla de negocio. Se frenó solo eso, y los
demás frentes siguieron. **Ningún diagnóstico apuntó a algo que pida emitir una reserva real.**

## La decisión que te toca: «Named Customer»

**Qué se midió** (`.trabajo/e92/medir_nc_sp.py` y `medir_nc_codigo.py`):
- En las 20 filas de este equipo que llegaron a la guarda, la regla de siempre (la primera opción con un valor que no es
  «select») eligió **«Direct Input»** en las 20. Es un texto fijo del portal, no un cliente: no es el código de Shipper
  de `config.json` ni el contrato.
- Su lista se llena después de elegir el contrato: en los 7 HTML del paso 3 del colega, cortados antes del contrato,
  trae solo «Select».
- Cuántas opciones trae con el contrato elegido no está guardado en ningún lado. Desde este encargo lo dice log.txt
  (`Named Customer opciones: …`): la primera corrida de prueba lo muestra.

**Por qué es tuya:** qué cliente nombrado va en la reserva (o si va «Direct Input») cambia lo que se reserva. Opciones:

- **(a) «Direct Input» por su texto,** lo que pasó en las 20 filas, y si no está, NO ENVIADA. Deja escrita la regla que
  ya se aplica.
- **(b) La única opción que no es relleno** (un cliente nombrado), y si no hay ninguna, «Direct Input» o NO ENVIADA.
- **(c) No elegir nada** y dejar «Select».

**Mi recomendación:** mira primero la línea `Named Customer opciones` de la prueba conjunta. Si trae solo «Select»,
«Dummy» y «Direct Input», (a) es lo de siempre y no cambia ninguna fila. Mientras tanto, el programa elige como antes.

## Paso 0 (medido)

- **«HMM Sales Person»:** en los 7 HTML del paso 3 del colega, `#hmmSalesmanCd` trae «Select» sin valor y una sola
  opción real. En las 20 filas de este equipo se eligió siempre el mismo valor, el de esa misma opción (comparado en
  memoria). **Con el contrato ya elegido no está medido:** los 7 HTML son de cortes antes del contrato. Que las 20
  eligieran siempre el mismo valor también se explica con dos opciones y la primera elegida. Es lo primero que muestra
  la prueba conjunta.
- **Las 4 anclas de MAERSK:** `.trabajo/e92/anclas.py` aplica la regla del corredor a las 2.871 mutaciones: 4 aparecían
  2 veces en `AQUASHIELD.py` (`e62-sin-juntar-los-espacios`, `e62-sin-esperar-la-lista-quieta`,
  `e62-elige-de-otra-lista` y `e65-clic-por-posicion`). La copia de MSC del encargo 86 (`_msc_opciones` y su elección)
  repite esas líneas de MAERSK. Con las líneas de alrededor, cada una es única. Ninguna más.
- **El residual del 91** (`.trabajo/e92/medir_listas.py`, los 99 HTML de HYUNDAI sin sus marcos):
  - ninguna raíz shadow (0 `<template>`);
  - la página del paso 2 trae una sola lista de contrato, en sus 70 HTML. La del paso 3 trae dos que calzan con
    `HMM_LISTA_PASO2`, pero el paso 2 no corre ahí;
  - `#selContractNo`, `#actualShipperCode` y `#hmmSalesmanCd`, una vez cada una;
  - las 63 opciones de las listas de contrato, las 40 líneas de log.txt con opciones o valores de «Contract No» y el
    contrato configurado, todos en ASCII, donde la mayúscula solo de a-z y `str.upper()` dan lo mismo.

  Ninguna fila cambia.
- **El frente 3:** abajo, en su sección.

## Frente 3 · Las 5 reservas que fallaron el 23-10 (diagnóstico, sin arreglo)

**Veredicto del paso 0: NOTA.** Las 5 ya las diagnosticó el encargo 82 (`CICLO-msc-lista-abierta-y-hs.md`) y las
arreglaron los encargos 82 y 83. Los tres arreglos están en `estable` desde antes de este encargo: `cc0e2ac`, `c1ee372`
y `32740e9` son antepasados de `b39c95c`, medido con `git merge-base --is-ancestor`. No hizo falta ningún arreglo nuevo,
y nada de lo que se ve apunta a algo que pida emitir una reserva real para reproducirlo.

**La corrida:** la del colega del viernes 23-10 (`1. pruebas`, la carpeta de las 09:59), 102 reservas en modo EMISIÓN,
por la variable del lanzador de emisión. Su log.txt da un estado final para cada una de las 102: 0 sin estado, 0
descartadas. La sonda es `.trabajo/e92/estados_23_10.py`, y su control positivo aborta si los estados no suman las 102
del INICIO.

| Naviera | EMITIDA | ENVIADA – REVISAR EN PORTAL | NO ENVIADA |
|---|---|---|---|
| ONE | 19 | | |
| MSC | 33 | | 3 |
| CMA-CGM | | 11 | |
| COSCO | | 11 | |
| MAERSK | 23 | | 2 |
| **Total (102)** | **75** | **22** | **5** |

Las 5 que fallaron son las 5 NO ENVIADA:

| # | Naviera | Paso donde cayó | Causa | La cubre |
|---|---|---|---|---|
| 1 | MSC | Paso 3, «Harmonized Code» | El portal no ofreció ninguna sugerencia del HS Code en 7 s. El campo decía «030313» y no había ninguna lista a la vista. Del portal | Encargo 82 (`cc0e2ac`): lo vuelve a escribir una vez. No la cubren el 91 ni este |
| 2 | MSC | El mismo | La misma, en otro momento de la corrida (a los 16 y a los 32 minutos, con filas que sí la recibieron antes y después) | La misma |
| 3 | MSC | Paso 2, «Search Schedule» | La lista del destino volvió a abrirse encima del botón, y el clic esperó 30 s sin darse. El motivo decía «no encontré el botón», pero el botón estaba | Encargo 82 (`c1ee372`): cierra la lista antes de buscar |
| 4 | MAERSK | «Additional details», el Shipper | El «Add» abrió el buscador con una pantalla nueva, titulada «Search/Add party», y la regla del encargo 38 exigía el título «Shipper». Del portal | Encargo 83 (`32740e9`): acepta esa pantalla con la misma regla |
| 5 | MAERSK | El mismo | La misma (la 1.ª y la 10.ª fila de MAERSK, no seguidas) | La misma |

**Ninguno de los tres arreglos se probó todavía en el portal.** Después del 23-10, las únicas corridas fueron de
HYUNDAI: la del colega del 26-10 y la del 28-10, y la de este equipo del 28-10. Ninguna pasó por MSC ni por MAERSK. Van
a la lista de la prueba conjunta.

**Las 22 ENVIADA – REVISAR EN PORTAL de CMA-CGM y COSCO no son fallas:** el viernes corrió una versión anterior a
`719280c` (encargo 77), que no reconocía la confirmación de ninguna de las dos. El encargo 82 lo midió por los textos
del log. Este encargo midió lo que esa evidencia permite: con el código de hoy, ¿habrían salido EMITIDA – CONFIRMAR POR
CORREO?
- El 23-10 guardó el HTML de después de cada envío: 11 de CMA-CGM y 11 de COSCO, 110 documentos con sus marcos.
  `CLAUDE.md` decía que la del 22-10 era la única emisión que lo había guardado, y no es así.
- `.trabajo/e92/medir_frase_23_10.py` carga cada documento en el Chromium de Playwright, sin red y sin su JavaScript, le
  corre la lectura del texto visible del programa (`_JS_TEXTO_VISIBLE`) y le aplica sus expresiones (`FORMA_ENVIADA`,
  `REFERENCIAS_ENVIADA`), tomadas del módulo y no copiadas. Control positivo que aborta: la frase de COSCO en una página
  armada con su forma.
- **En los 22 envíos, la frase de su naviera está en un documento** (para COSCO, el marco del formulario), con una sola
  referencia en la pantalla, y la referencia es distinta en cada fila: 11 de 11 en cada naviera. Con el código de hoy,
  las 22 habrían salido EMITIDA – CONFIRMAR POR CORREO, con su número.
- La frase de cada naviera se había medido en una sola emisión, la del 22-10; ahora son 12 de cada una.
- Límite: sin las hojas de estilo del portal, el texto «visible» es el del HTML con sus estilos en línea.

## El cambio · frente 1 · `31dd439`

- **«HMM Sales Person»** (`_hmm_sales_person`):
  - **Qué elige:** la única opción con un valor que no es «Select», «Dummy» ni «Direct Input» (`_hmm_reales`), por su
    valor, si ninguna otra responde a él (`_hmm_responden`).
  - **Cómo lee:** con el mismo localizador con que elige, el de la única lista que calza (`_hmm_una_lista`).
  - **Después:** en una sola lectura comprueba que quedó la misma opción que leyó, todavía la única real y la única con
    su valor. Si no, log.txt dice cuál quedó.
  - **Cuándo corta (NO ENVIADA):** con dos listas (también si aparece otra al leer), con dos opciones reales, si la
    lista no acepta o si no queda.
  - **Cuándo sigue como antes:** sin la lista, sin opción real o sin poder leerla.
  - **Hasta ahí:** elegía la primera con valor, por su posición, y si algo fallaba seguía.
- **«Named Customer»** (`_hmm_named_customer_opciones`): solo anota sus opciones, saneadas y con su tope. La elección no
  cambió (el freno).
- **`_hmm_una_lista`** y **`_JS_HMM_LISTA`:** cuentan con el localizador y leen el texto, el valor, la etiqueta y la
  elegida del mismo elemento, en una sola lectura.
- **`tests/mutaciones.py`:** las 4 anclas de MAERSK y una del encargo 89, que repetía la línea nueva; 26 mutaciones
  nuevas. **Pruebas:** `PaginaLista` y `TestSalesPersonDeHyundai` (10).

## El cambio · frente 2 · `0d640d0`

El residual de la revisión de seguridad del 91, y lo que encontraron las revisiones de este frente:
- **Mismo localizador:** las listas de contrato de los pasos 2 y 3 se leen y se eligen con `_hmm_una_lista`.
  `document.querySelector`, con el que se leía, no entra a las raíces shadow, y Playwright, con el que se elige, sí. Con
  dos listas, el paso 2 no elige y el paso 3 corta.
- **El paso 3 elige por el valor ya comprobado:** ya no con `_hmm_select_por_texto`, que elegía la primera opción cuyo
  texto contenía el de la del contrato. Se cierra también el residual «XCT-1 antes de CT-1»: ahora elige CT-1.
- **La comprobación** (`_hmm_comprobar_contrato`), en una sola lectura:
  - vuelve a contar si es la única que calza y se distingue (`_hmm_sin_una_opcion`);
  - compara el texto tal como se leyó, sin recortarlo otra vez;
  - **se repite antes de «NEXT - Additional Information»**, sin tocar nada. Entre las dos corren Named Customer, Sales
    Person y la carga, y el `change` de una lista puede cambiar otra (revisión de seguridad).
- **Si la última lectura falla:** log.txt lo dice y vuelve a contar las listas (revisión de código).
- **Mayúsculas solo de a-z** (`_mayusculas_ascii`): `str.upper()` igualaba «ß» con «SS», «ı» con «I» y «ﬁ» con «FI».
- **`_hmm_select_por_texto` y «Size opciones»:** escriben saneado. Todo lo del portal va a log.txt con un tope de 60
  caracteres por texto.
- **Lo que se quitó:** `_JS_HMM_CONTRATOS`, `_JS_HMM_CONTRATO_ELEGIDO` y `_hmm_pares`.
- **Mutaciones:** las de los encargos 89 a 91 ancladas en el código quitado pasan al nuevo, con la misma falla; 2
  quedaron sin equivalente y salen. Hay 18 nuevas.
- **Pruebas:**
  - `PaginaContrato` y `PaginaPaso2` leen y eligen con un localizador;
  - 6 pruebas nuevas del contrato y 1 del paso 2;
  - `TestSelectPorTextoDeHyundai` (2);
  - sale la prueba en Node del JavaScript quitado.

## Las revisiones

| Revisión | Hallazgos | Qué se hizo |
|---|---|---|
| Código, frente 1 | 0 críticos, altos o medios; 2 BAJAS: si la comprobación corta, el log no decía qué quedó; ninguna prueba corría la lectura de Named Customer | Arreglados: la línea de qué quedó, con motivos separados, y el ayudante con su prueba. **Aprobado** |
| Seguridad, frente 1 | 1 MEDIA: la comprobación miraba el valor, no que la elegida fuera la opción leída (el portal cambia la lista entre la lectura y la elección, y queda una de relleno con ese valor); 3 BAJAS: la lectura que falla por una segunda lista seguía, el log sin tope, la comprobación de un solo instante | La MEDIA y las 2 primeras BAJAS, arregladas, con una prueba que modela la carrera. La tercera, al residual |
| Código, frente 2 | 0 críticos, altos o medios; 3 BAJAS: la mitad del texto de la comprobación sin prueba, la lectura que falla en el paso 3 sin log ni recuento, documentación atrasada | Las 3, arregladas. **Aprobado** |
| Seguridad, frente 2 | 1 MEDIA, de antes: nada volvía a mirar el contrato antes de la guarda; 3 BAJAS: `IndexError` si el portal reescribe la opción (el `strip()` de Python y el `trim()` de JavaScript no quitan lo mismo), el log sin tope, «Size opciones» sin sanear (de antes) | Las 4, arregladas: la comprobación antes de seguir, el texto sin recortar, el motivo sin ninguna que calce, el tope y «Size opciones» |

Los revisores trabajaron en clones (`.trabajo/e92/clon` y `clon-r2`), sin tocar el repo vivo.

## Compuertas

Todas corrieron sobre el árbol que se commiteó, con el temporal en la ruta corta de la carpeta del encargo.

| Compuerta | Sobre | Resultado |
|---|---|---|
| Suite (`tests/correr.py`, con `con_mas_plazo.py`: 7.200 s) | frente 1, antes de sus revisiones | 1.034 pruebas, OK; la foto de los originales, sin cambios |
| Suite | frente 1, final (`31dd439`) | 1.035 pruebas, OK, sin cambios |
| Censo de las mutaciones nuevas y las arregladas (`censo_ids.py`) | frente 1, final | 33 mutaciones y 39 pares, todos muerden; el control, con 17 pruebas, pasa; sin cambios |
| Suite | frente 2 (`0d640d0`) | 1.043 pruebas, OK, sin cambios |
| **Censo completo** | `0d640d0` | **2.913 mutaciones y 3.676 pares, todos muerden; 0 pruebas sin mutación; el control, con las 1.043 pruebas, pasa; la foto (5.362 entradas), sin cambios** |
| Los 8 pares que vencieron dormidos, repetidos | `0d640d0` | 8 de 8 muerden por su aserción, en 18 o 19 s; el control, con 6 pruebas, pasa |
| Anclas (`anclas.py`) | frentes 1 y 2 | 0 anclas que no aparecen una vez |
| Sonda de secretos (`--dry-run`, `git add` y la sonda) | cada commit | 0 y 0 |
| Guarda de datos reales (el hook pre-commit) | cada commit | 0 |
| Guarda sobre los mensajes de los commits y este informe | cada commit | 0 |
| Commit de este informe: `test_guarda_datos` y `test_sonda` | el árbol del informe | 19 y 13 pruebas, OK |

**El censo completo cruzó un fin de semana con el equipo dormido.** Empezó el viernes 30-10 a las 12:27 y terminó el
lunes 02-11 a las 09:43. Según el registro de Windows, a las 17:18 del viernes el equipo cambió de fuente de energía y
pasó a espera (Kernel-Power 105 y 506), a las 23:57 pasó a sueño (42), y volvió el lunes a las 08:36 (507). No hubo
reinicio (ningún 109), y el censo siguió vivo hasta el final. 8 pares de MAERSK estaban abiertos en ese tramo y salieron
«tiempo agotado» a las 6,6 y a las 56,7 horas de reloj. El plazo de 240 s de cada par cuenta también con el equipo
dormido, así que ese «muerde» no decía nada: pudo tapar uno que no muerde. Se repitieron con el equipo despierto
(`.trabajo/e92/censo_8_despierto.out`), y los 8 muerden por su aserción, en 18 o 19 s.

Esa repetición da `RESULTADO: FALLA` solo por la foto de los originales: 187 cambios en `logs/`, en `perfiles/` y en la
planilla. Son de la corrida en modo prueba que se abrió desde tu panel a las 14:30, mientras el censo corría; ninguno es
del censo (las pruebas corren en copias del temporal).

## Decisiones que tomé solo

| Decisión | Por qué |
|---|---|
| «HMM Sales Person»: con más de una opción real, NO ENVIADA | Aplica la regla de Marcelo de «no hay clics a ciegas»; lo medido trae una sola. Si la prueba muestra más, decides tú y `estable` no se mueve |
| «Named Customer»: frenar la elección, pero anotar sus opciones | Elegir bien es regla de negocio; anotar no cambia nada que vea el colega y da el dato para decidir |
| Volver a mirar el contrato antes de «NEXT - Additional Information» | Lo pidió la revisión de seguridad (y la del 89 lo había propuesto); es antes de la guarda y corta solo si el contrato cambió |
| El paso 3 elige por valor, no con `_hmm_select_por_texto` | Cierra a la vez el residual de la raíz shadow y el de «XCT-1 antes de CT-1», y es lo que mide la comprobación |
| «Size opciones», saneado | Lo marcó la revisión; es la misma familia de listas y el mismo arreglo del 91 |
| El frente 3 sin arreglo nuevo | Las 5 ya están arregladas en `estable` (encargos 82 y 83) |
| Medir la frase de envío en los 22 envíos del 23-10 | Fuera de las 5 caídas, pero solo lectura, y valida la regla de los encargos 77 y 78 con 11 muestras más por naviera |

## Lo que salió mal

- **Lancé el censo del frente 1 antes de aplicar las revisiones:** se detuvo enseguida (5 procesos cerrados por PID, sin
  pares corridos) y se volvió a correr sobre el código final.
- **Un rebase en el clon del frente 2 con la base equivocada** (`HEAD~0`): se abortó y se rehízo con la base correcta.
  El árbol del frente 2 que llegó al repo vivo es idéntico al del clon (`write-tree`, el mismo hash).
- **Dos sondas que no servían como estaban:**
  - la de «Named Customer» buscaba las líneas con «·», y empiezan con espacios. El control abortó y se corrigió;
  - la de las anclas compilaba el programa una vez por mutación (unos 20 min): la compilación pasó a ser una opción.
- **Un `grep -r` sobre toda la carpeta** (con `perfiles/`) no terminaba: se detuvo y se cerró su proceso.
- **Un `cd /c` suelto** en un comando: lo frenó la guardia del `cd` antes de correr.
- **El censo completo cruzó el fin de semana con el equipo dormido,** y 8 de sus pares salieron «muerde» por un plazo
  que venció dormido. Se repitieron despiertos (abajo, en «Compuertas»). Para un censo de horas: el equipo enchufado y
  con la tapa abierta, y después buscar los eventos 506 y 507 en su ventana y los pares de más de 240 s.

## Residual

- **«Named Customer»:** el freno, arriba.
- **«HMM Sales Person» con el contrato elegido:** no está medido que traiga una sola opción.
- **Una sola lectura en cada comprobación:** la de «HMM Sales Person» y las del contrato miran un solo instante. Una
  opción que el portal sume después no se ve (revisión de seguridad del frente 1; hipotético).
- **Las otras listas de HYUNDAI siguen leyendo con `document.querySelector`** y eligiendo con `page.select_option`:
  `_hmm_select_por_texto` (Contract Holder, el tipo, el tamaño, la unidad y la ventilación) y la elección de «Named
  Customer». En lo medido no hay raíces shadow (revisión de código del frente 2).
- **Que el portal no cambie el contrato** entre la elección y «NEXT - Additional Information» no está medido. Ahora, si
  lo cambia, la fila queda NO ENVIADA, y la prueba conjunta lo mostraría.
- **Un `grep` de otra sesión** corre desde el 29-10 a las 17:44 sobre la carpeta de la skill `lanzador-modulo` y usa CPU
  todo el tiempo. Hizo más lentas la suite y el censo. No lo cerré: no es de esta sesión.

## La prueba conjunta en el portal

Siempre con el lanzador de prueba, `Iniciar AQUASHIELD.bat`, nunca con el de emisión: cada fila tiene que terminar en
OK-EJEMPLO, «lista para emitir». Lo que hay que ver está en log.txt de la corrida (`logs\web_…\log.txt`). Ninguna de
estas comprobaciones necesita emitir una reserva.

**1. HYUNDAI, 1 o 2 filas con su contrato configurado** (los frentes 1 y 2 de este encargo):
- `Contract No opciones: …` y después `Contract No: '<código>'` y `Contract No: la lista quedó con la opción del
  contrato`. Así se ve que el paso 3 lee y elige con el mismo localizador, por el valor.
- En el paso 2, una de estas: `Contract No (Paso 2): no hay una sola lista de contrato (hay N)…`,
  `… sin opción que calce exacto…` o `Contract No (Paso 2): '<código>'`. Ninguna con «err». Lo medido es una lista
  vacía, así que lo esperable es la segunda.
- `HMM Sales Person opciones: Select | <una persona>`, después `HMM Sales Person: '<valor>'` y `HMM Sales Person: la
  lista quedó con su única opción`. Si el portal ofrece más de una persona, la fila queda NO ENVIADA con «el portal
  ofrece N»: eso lo decides tú, y `estable` no se mueve hasta entonces.
- `Named Customer opciones: …`: **es el dato que falta para el freno.** Dice cuántas opciones trae la lista después de
  elegir el contrato y cuáles son, y si «Direct Input» es la única además de «Select». Hoy sigue eligiendo como antes
  (`Named Customer: 'Direct Input'`).

**2. MSC, 2 o 3 filas** (los arreglos del encargo 82, que cubren 3 de las 5 caídas del 23-10):
- `HS Code '030313' seleccionado (salmón)`. Si el portal no ofrece ninguna sugerencia en 7 s, primero `HS Code: el
  portal no ofreció ninguna sugerencia en 7 s; lo vuelvo a escribir, una sola vez` y después la elección. Esto depende
  del portal: puede no pasar en la prueba.
- «Search Schedule» pulsado. Si una lista quedó abierta encima del botón: `… su lista de sugerencias quedó abierta; la
  cierro sin elegir nada (…)`, y la búsqueda sigue.

**3. MAERSK, varias filas** (el arreglo del encargo 83, que cubre las otras 2 caídas; la pantalla nueva salió en 2 de
25):
- En el Shipper, si el buscador se abre con la pantalla nueva: `Shipper: el buscador se abrió con la pantalla
  «Search/Add party», sin el título «Shipper»; elijo con la misma regla…`, y la fila sigue hasta OK-EJEMPLO, con
  AQUACHILE en la tarjeta «Shipper». Con la pantalla de siempre, como antes.

**4. CMA-CGM y COSCO: nada en modo prueba.** Su frase de envío solo aparece al emitir. La cubre la medición de los 22
envíos del 23-10 (frente 3), y reproducirla en el portal exigiría emitir una reserva real.

## Re-medir

- **«HMM Sales Person» con el contrato elegido:** la línea `HMM Sales Person opciones` de la primera corrida.
- **«Named Customer»:** su línea de opciones, para la decisión.
- **Las frases de envío de CMA-CGM y COSCO:** con la próxima emisión de cada una, `.trabajo/e92/medir_frase_23_10.py`
  adaptado a su carpeta.

## NO retroceder

- **Leer y elegir una lista de HYUNDAI con el mismo localizador** (`_hmm_una_lista`): leer con `document.querySelector`
  y elegir con Playwright puede tomar listas distintas.
- **No comparar con `str.upper()`:** iguala letras que no son ASCII. Las mayúsculas, solo de a-z.
- **Cada ancla de `tests/mutaciones.py` aparece una vez en su archivo:** una copia de código que repite líneas rompe el
  censo completo. `.trabajo/e92/anclas.py` lo cuenta en segundos.

## Reglas aplicadas

PASO 0 con veredicto por frente: CICLO (1 y 2), NOTA (3) y una PREGUNTA (el freno). Control positivo que aborta en cada
sonda (dos abortaron y se corrigieron). Censo relativo a las mutaciones elegidas. Revisores en clones. Datos solo como
cuentas. Guarda de datos sobre los mensajes y el informe. Ningún comando detrás de un `cd`. Lista de tareas: esta sesión
no tiene la herramienta.

## El bloque de push

El repo es público: lo subes tú. El hash que tiene que quedar en `main` es el del commit de este informe, que no
puede ir dentro de su propio commit: está en el mensaje con que cerré el ciclo. `estable` no se mueve hasta la prueba
conjunta.

```powershell
git -C "C:\dev\Agendamiento Reservas" log origin/main..main --format="%h %ae %ce %s"
git -C "C:\dev\Agendamiento Reservas" push origin main
git -C "C:\dev\Agendamiento Reservas" rev-parse main
git -C "C:\dev\Agendamiento Reservas" ls-remote origin refs/heads/main
```

- El primer comando tiene que mostrar 3 commits (`31dd439`, `0d640d0` y el del informe), cada uno solo con el correo
  noreply, como autor y como committer.
- Después de subir, `rev-parse` y `ls-remote` tienen que dar el mismo hash.
