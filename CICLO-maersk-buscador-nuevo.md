# Encargo 83 · MAERSK acepta la pantalla nueva del buscador del Shipper («Search/Add party»)

**Fecha:** 2026-10-26 · **Método:** `metodo-ciclo` v38, en Modo autónomo (por omisión).

Base: `Agendamiento Reservas` @ `613039d` · árbol limpio. `origin/main` no lo medí al empezar; al cerrar,
`origin/main` y `origin/estable` estaban en `613039d` (los commits del encargo 82, que subió Marcelo; medido con
`git fetch`).

**Commits,** en `main` y sin push (lo pidió el encargo, y el repo es público):
- `32740e9`: MAERSK acepta la pantalla nueva del buscador del Shipper, con la misma regla;
- el de este informe.

## Lo que pidió el encargo

La opción (a) del encargo 82, decisión de Marcelo: que MAERSK acepte la pantalla «Search/Add party» con la misma regla
del encargo 38.
- **La regla no cambia:** se elige AQUACHILE solo si el resultado es único e inequívoco, y la tarjeta «Shipper» tiene
  que mostrarlo después. Si no, NO ENVIADA, como hoy.
- **El buscador de siempre sigue igual.** La pantalla nueva es un segundo camino, y se reconoce por lo que muestra, no
  por intentos a ciegas.
- **FRENA SI:** la pantalla nueva exige crear o editar una parte en vez de elegir una existente, o el resultado de
  AQUACHILE no se puede identificar sin ambigüedad en los 2 HTML. **No pasó** (abajo).

**Los datos:** los 2 HTML de la pantalla nueva y los 23 de siempre, del 23-10, en `1. pruebas/`, la carpeta ignorada
(comprobado en el encargo 82). Son datos reales: no entran al repo, a los commits ni a este informe. Las sondas
imprimen solo la estructura, los textos fijos del portal y cuentas; los nombres, las direcciones y los códigos de las
partes salen tapados.

## PASO 0: lo medido

**1. La estructura, entera** (`sonda_estructura.py`): el árbol de cada `mc-c-party-finder`, con sus raíces shadow,
de uno de siempre y de los 2 nuevos, con los textos de las partes tapados. Control positivo: el de siempre tiene que
traer el encabezado «Shipper», y los nuevos «Search/Add party». Pasó.
- **Los tres árboles tienen las mismas 208 líneas, y solo difieren en dos textos:** el título (un span hijo del
  encabezado: «Shipper» o «Search/Add party») y el de la primera pestaña («Previously used» o «Favourite», con el mismo
  `data-cy=favourite-tab`).
- Lo demás es igual: el mismo componente; el encabezado con el título y la barra de pestañas («Search» la segunda); el
  texto «Click a card to add party.»; los resultados, sueltos en un `div.party-search-results`, casilla de opción y
  `label` alternados, cada `label` con su `mc-c-party-card`; el «Close» de la cabecera (`data-cy=close`) y el «Cancel»
  del pie.
- **Ningún botón para crear ni editar una parte:** dentro de los resultados no hay ningún botón. La pantalla nueva
  elige entre partes que ya existen. El primer FRENO no se cumple.
- Las 2 filas nuevas traen la misma lista, en el mismo orden.

**2. El camino real** (`sonda_camino.py`): el JavaScript del programa, ya cambiado y leído de su fuente con `ast`, sobre
los 25 HTML del buscador del 23-10, en un Chromium sin red y sin el JavaScript de la página. Control positivo: tienen
que salir 25 filas, 23 con «Shipper» y 2 con el título nuevo. Pasó.

| Pantalla | Filas | `titulo` | `titulo_nuevo` | Resultados | Con AQUACHILE | Pulsaría uno con AQUACHILE | Su casilla |
|---|---|---|---|---|---|---|---|
| De siempre | 23 | sí | no | 3 | 1 | sí | coinciden |
| Nueva | 2 | no | sí | 3 | 1 | sí | coinciden |

- **El resultado de AQUACHILE se identifica sin ambigüedad en los 2:** uno solo trae AQUACHILE como palabra entera en
  su nombre, es el que daría `_JS_MK_SHIPPER_PULSAR`, y la posición y las cifras del código de su casilla apuntan a la
  misma. El segundo FRENO tampoco se cumple.
- **Las 2 páginas del buscador de `logs/` de este equipo** (20 HTML con sus marcos) dan lo mismo que antes: «Shipper»,
  sin el título nuevo (`sonda_camino_logs.py`).

**Veredicto: CICLO.** La pantalla nueva es el mismo buscador con otro título.

## El cambio

`AQUASHIELD.py`:
- `MK_BUSCADOR_GENERICO = "Search/Add party"`, en `_MK_ARGS_SHIPPER` como «generico».
- `mkShipper` (`_JS_MK_SHIPPER_LEER`): `tituloNuevo`, verdadero si un span hijo de un encabezado del buscador, a la
  vista, dice entero el título genérico. Solo el span: el texto del encabezado entero trae también las pestañas
  («Shipper Previously used Search»). El resultado se pulsa con `titulo || tituloNuevo`, y la casilla también.
  `_JS_MK_SHIPPER` devuelve `titulo_nuevo`.
- `_mk_elegir_shipper`: corta si no está ninguno de los dos títulos (el motivo nombra los dos). Con el nuevo, lo anota
  en log.txt («el buscador se abrió con la pantalla «Search/Add party», sin el título «Shipper»; elijo con la misma
  regla, y después compruebo la tarjeta «Shipper»») y sigue con la misma regla. Con los dos títulos a la vez, manda el
  de siempre.
- `_mk_resultados_quietos`: la lista quieta incluye `titulo_nuevo`.
- **El camino de siempre no cambia:** las mismas lecturas, clics y esperas. Le cambian solo dos motivos, el del
  buscador sin ninguno de los dos títulos y el de la casilla en ese caso, que ahora nombran los dos.
- **Ese título no nombra la parte.** Que el buscador sea el del Shipper lo dicen el «Add» que se acaba de pulsar, el de
  la única tarjeta «Shipper», y la comprobación final, que esa tarjeta muestre a AQUACHILE (revisión de código, L1).
- **Que el clic elija a AQUACHILE en la pantalla nueva no está probado en el portal.** Si no lo elige, la fila queda NO
  ENVIADA, como hoy.

`tests/test_clics.py`, `TestShipperMaersk`:
- dos pruebas nuevas, de punta a punta sobre `_mk_shipper`: la pantalla nueva elige con la misma regla (con su «Close»
  y con su casilla, como el de siempre); el de siempre no la anota, y con los dos títulos manda el de siempre; y la
  pantalla nueva sin un solo resultado con AQUACHILE, o con la tarjeta sin mostrarlo, corta;
- en Node: `test_js_shipper` (la pantalla nueva como se midió; el título genérico con otra cosa en su span, suelto en el
  encabezado, en otro elemento, oculto o fuera del buscador, no cuenta) y `test_js_casilla` (la misma casilla, y
  ninguna con dos resultados con AQUACHILE);
- la lista quieta también espera el título nuevo.

`tests/mutaciones.py`: 15 mutaciones «e83-…», y 4 de antes puestas al día con la misma intención (el texto que apuntaban
cambió). `CLAUDE.md`: la viñeta de la pantalla nueva, en el Shipper de MAERSK.

## Las suites

Con `TEMP`, `TMP` y `TMPDIR` en la carpeta del encargo:

| Corrida | Resultado |
|---|---|
| `TestShipperMaersk`, `TestMaersk` y la foto de clics genéricos | 73 pruebas, OK |
| El censo de las mutaciones del Shipper (`--filtro TestShipperMaersk`), primera vez | 103 mutaciones, 110 pares: todos muerden. Pero «Originales: 2 cambios» (abajo, errores propios), así que no vale |
| El mismo censo, con los arreglos de la revisión y la raíz quieta | 106 mutaciones, 113 pares: todos muerden. Originales: 0 cambios (1.144 s) |
| La suite completa, sobre el árbol de `32740e9` (un clon), con el equipo despierto | 902 pruebas, OK (1 omitida), 1.462 s. Originales: 0 cambios |

Las compuertas del commit: la sonda de secretos (antes y después de agregar al índice), 0; el barrido de las palabras
de los datos del colega del encargo 82 (`barrido_colega.py`), 0; la guarda de datos del hook, 0. **El barrido del
encargo 72 marca 8 líneas agregadas y 1 del mensaje, y las 9 son falsos positivos:** lo que calza es una palabra de 5
letras del nombre de una nave que está dentro de «AQUACHILE», el nombre de la empresa, que se publica a propósito. Sin
«AQUACHILE», 0 (`barrido_aquachile.py`, sin imprimir el valor; el mismo caso del encargo 82). En el commit de este
informe, el mismo barrido marca 13 líneas del informe y 1 del mensaje, todas por la misma causa (una, por el nombre
de ese script, en minúsculas).

## La revisión de código

Con `code-reviewer`, en un clon sin remoto. **La primera se detuvo** («no progress for 600s»): el equipo entró en
espera en ese rato (abajo). La segunda, con un agente nuevo: **APROBAR**, sin CRITICAL, HIGH ni MEDIUM.
- Corrió `TestShipperMaersk` y la foto (24, OK), la evidencia y el candado (86, OK, 1 omitida); las 16 mutaciones
  (12 nuevas y 4 puestas al día) muerden; la guarda de datos sobre los 4 archivos, 0.
- Armó la estructura medida en un DOM real de Chrome, con raíces shadow declarativas, y corrió el JavaScript del
  programa en 10 casos: el de siempre y el nuevo, con los resultados esperados; el genérico oculto, anidado, con otra
  cosa, suelto o fuera del buscador, no cuenta; con los dos títulos, manda el de siempre.

| # | Hallazgo | Qué hice |
|---|---|---|
| L1 | El título genérico no nombra la parte, y no estaba dicho qué garantiza que sea el Shipper | Dicho en el comentario y en `CLAUDE.md`: el «Add» de la única tarjeta «Shipper» y la comprobación final |
| L2 | Tres mutaciones suyas sobrevivían: el título genérico fuera del buscador, oculto, y el aviso con los dos títulos | Los tres casos en las pruebas y sus tres mutaciones (`e83-js-titulo-fuera-del-buscador`, `-oculto`, `e83-aviso-con-los-dos-titulos`) |
| L3 | El comentario y el docstring no decían «no probado en el portal»; `CLAUDE.md` resumía la regla sin la excepción, atribuía la regla al encargo 82 y daba las cifras de `logs/` distinto que el informe 82; líneas de 121 y 122 caracteres | Corregido |

## Decisiones que tomé solo

| Decisión | Por qué |
|---|---|
| Reconocer la pantalla nueva por el título entero en su span, no por las pestañas ni por la falta de «Shipper» | Es lo único que difiere, además de una pestaña; un título que contenga el genérico, o el genérico fuera del span, no cuenta |
| No exigir la pestaña «Favourite» | Su `data-cy` es el mismo en las dos pantallas: no distingue nada que el título no distinga, y la haría más frágil |
| Con los dos títulos a la vez, el camino de siempre | No cambiar lo que hace el buscador de siempre |
| Anotar en log.txt cuando sale la pantalla nueva | Para medirla en el portal: hoy solo está en 2 de 25 filas |
| El título nuevo, también en la lista quieta | Como el de siempre: decidir con un título que todavía no llegó cambiaría lo que se elige |

## Errores propios, y cómo se vieron

| Error | Cómo se vio | Qué hice |
|---|---|---|
| Edité el `CLAUDE.md` del repo vivo mientras corría el censo, y la revisión creó su worktree en la raíz en ese rato | El censo: «Originales: 2 cambios» (`CLAUDE.md` y `.claude/`) | Repetí el censo con la raíz quieta |
| La primera suite completa corrió a la par del censo y de la revisión, y el equipo entró en espera de 17:55 a 18:39 (Kernel-Power 506/507, después de un 105, cambio de fuente de energía): su corrida de unittest pasó el tope de 3.600 s | La suite salió con 1, sin resultado; el registro System | La repetí, con el pedido de mantener el equipo despierto (no evita el cambio de fuente de energía) |
| Una prueba nueva miraba el log.txt de la clase, que comparten sus pruebas, y encontró la línea de otra | Al correrla | Mira lo que vio la pantalla de su propia corrida |
| Cuatro mutaciones de antes apuntaban al texto que cambié | Al revisar los textos de las 2.618 | Puestas al día, con la misma intención |

## RESIDUAL

| Qué | Condición de reapertura |
|---|---|
| **Que el clic elija a AQUACHILE en la pantalla nueva** no está probado en el portal: los 2 HTML son de antes del clic | La primera fila que lo use: su log.txt dice «el buscador se abrió con la pantalla «Search/Add party»» y si la tarjeta lo mostró |
| **Si el portal cambia también la estructura** de la pantalla nueva (otro componente, otra lista), no la reconoce o no elige: NO ENVIADA, el lado seguro | Una fila NO ENVIADA en el Shipper con el título nuevo |
| **Si un buscador titulado «Search/Add party» se abriera para otra parte**, AQUACHILE iría a esa parte y la fila quedaría NO ENVIADA por la comprobación final (hipotético) | Una fila NO ENVIADA con «la tarjeta «Shipper» no lo muestra» después de la pantalla nueva |

## Re-medir

1. `python -B -P <e83>/sonda_estructura.py`: el árbol del buscador, de siempre y nuevo, tapado; `diff` entre sus
   salidas.
2. `python -B -P <e83>/sonda_camino.py` y `sonda_camino_logs.py`: el JavaScript del programa sobre los 25 HTML del
   23-10 y sobre los de `logs/`.
3. Desde `tests/`: `python -m unittest test_clics.TestShipperMaersk`; y
   `python tests/correr.py --mutaciones --filtro TestShipperMaersk`.

`<e83>` es la carpeta del encargo en el scratchpad de la sesión. No se versiona: las sondas leen la evidencia del
colega y `logs/`, que son datos reales, e imprimen solo estructura, textos fijos y cuentas. Corren con el Python de la
Store (el `python` del PATH de este equipo no trae playwright; encargo 82).

## NO retroceder

- **AQUACHILE se elige solo con un solo resultado que lo traiga, la lista quieta, y la tarjeta «Shipper» que lo muestre
  después,** en el buscador de siempre y en la pantalla nueva.
- **La pantalla nueva se reconoce por su título entero en su span,** nunca por la falta de «Shipper».
- **Un buscador sin ninguno de los dos títulos no se usa:** NO ENVIADA sin elegir nada.

## Reglas de método aplicadas

`metodo-ciclo` v38 (la misma del disco al empezar):
- medir antes de cambiar: el árbol entero de las dos pantallas, comparado, y el JavaScript del programa sobre los 25
  HTML, con control positivo que aborta y salidas tapadas;
- los FRENA SI, medidos antes de escribir código;
- el camino real: las pruebas corren `_mk_shipper` de punta a punta, y la sonda, el JavaScript de la fuente;
- cada camino con su prueba y su mutación; una revisión de código sobre el diff, en un clon sin remoto;
- todas las suites antes del commit, sobre el árbol del commit, con el equipo despierto;
- la base, sin push y el cierre sin esperas vivas.

Las del módulo: `test_candado` sin cambios, ningún dato real en lo versionado, y la sonda de secretos y la guarda antes
de cada commit.
