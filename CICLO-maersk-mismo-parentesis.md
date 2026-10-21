# Encargo 74 · MAERSK: si la celda y la sugerencia traen paréntesis, tienen que decir lo mismo

**Fecha:** 2026-10-21 · **Método:** `metodo-ciclo` v36, en Modo autónomo (por omisión).

Base: `Agendamiento Reservas` @ `189225c` · árbol limpio. Los dos commits del encargo 73 (`a538b77` y `189225c`) todavía
no estaban en GitHub: el bloque de push de abajo los lleva junto con los de este.

**Commits,** en `main` y sin push (el repo es público: el bloque lo lleva Marcelo): `411535c`, el cambio, su red y
`CLAUDE.md`; y el de este informe.

## La decisión, y lo que hice con ella

Tu decisión, sobre el RESIDUAL del encargo 73: «cuando los dos lados traen paréntesis, tienen que decir lo mismo
(normalizado). Si solo la fila trae paréntesis, calza por lo de afuera, como en a538b77», en un ciclo aparte, con su
prueba en las dos direcciones y «Alfa (Norte)» contra «Alfa (Sur)» como NO ENVIADA.

- **`_mk_partes`** parte lo que va antes de la primera coma en dos: lo de afuera de los paréntesis y lo de adentro, cada
  paréntesis por separado, los dos en `_mk_plano` (sin tildes, en mayúsculas y con los espacios de a uno). Lo de afuera
  es exactamente lo que daba `_mk_base`, que salió: se quedó sin quien la llame.
- **`_mk_calza`** decide: lo de afuera igual y, si los dos traen paréntesis, lo de adentro también igual, todos y en el
  mismo orden. Si solo uno los trae, cuenta lo de afuera.
- **`_mk_las_exactas`** elige con `_mk_calza`. Nada más de `_mk_ciudad` cambió: lo que escribe, la lista quieta, la
  evidencia, el reintento, la comprobación del campo.
- **El motivo de la NO ENVIADA** dice la regla: «(sin lo que va entre paréntesis, salvo que lo traigan las dos:
  entonces, el mismo)». Hasta ahora decía solo «(sin lo que va entre paréntesis)».

**Cómo leí «normalizado»:** lo de adentro de cada paréntesis pasa por `_mk_plano`, como lo de afuera desde el encargo
43. Así «( región  uno )» y «(REGION UNO)» son lo mismo. **«Decir lo mismo»** lo leí como todos los paréntesis, y en el
mismo orden: «Alfa (Norte)» no calza con «Alfa (Norte) (Puerto)». Si alguna lectura no te sirve, dímelo.

**Lo que quedó igual, y que tu decisión no nombra:** la celda sin paréntesis contra una sugerencia con paréntesis sigue
calzando por lo de afuera, como desde el encargo 43 («Alfa» elige «Alfa (Norte), País» si es la única). Tu decisión
habla de la fila con paréntesis; este lado lo dejé como estaba.

| Celda | Sugerencia | Encargo 43 | Encargo 73 (`a538b77`) | Encargo 74 |
|---|---|---|---|---|
| «Alfa (Norte)» | «Alfa (Norte), País» | no calza | calza | calza |
| «Alfa (Norte)» | «ALFA ( nórte ), País» | no calza | calza | calza (normalizado) |
| «Alfa (Norte)» | «Alfa (Sur), País» | no calza | calza | **no calza** |
| «Alfa (Norte)» | «Alfa, País» | no calza | calza | calza |
| «Alfa» | «Alfa (Norte), País» | calza | calza | calza |
| «Alfa (Norte)» | «Alfa (Norte) (Puerto), País» | no calza | calza | no calza |

La tabla está medida, no escrita a mano: `_mk_las_exactas` de cada versión, cargada de su commit (`afef717`, `189225c`
y `411535c`), sobre una lista con esa sola Container Yard (`tabla_versiones.py`; control: «Alfa» contra «Alfa, País»
calza en las tres).

## PASO 0

- **El registro:** el encargo 73 (`CICLO-maersk-parentesis.md`) dejó en su RESIDUAL esta decisión, y las dos revisiones
  de ese ciclo la marcaron MEDIUM, declarada. `CLAUDE.md` decía la regla del 73.
- **Re-medí contra HEAD (`189225c`):** `_mk_las_exactas` comparaba `_mk_base` de los dos lados, y `_mk_base` solo la
  usaba ella en el programa (las pruebas, en `test_ayudantes`).
- **Veredicto: CICLO.** La decisión es tuya y está tomada; lo demás se mide.

## Lo medido

**1. No cambia ninguna elección guardada.** La sonda del 73, puesta al día (`medir_listas.py`), sobre las 18 listas de
MAERSK de `logs/`, con lo que su `log.txt` dice que se escribió, cargadas en un Chromium sin red y leídas con las
funciones del programa: 30 elecciones, 0 listas saltadas, 0 distintas entre HEAD (la regla del 73) y el árbol (la del
74). Ninguna ciudad escrita trae un paréntesis; de las 19 Container Yard, 8 traen uno, y ninguna lista trae dos con lo
mismo afuera y otra cosa adentro. Control que aborta, sobre la regla nueva: en una lista sintética, el mismo paréntesis,
también escrito de otra forma, da 1; otro, 0; sin paréntesis, 1.

**2. La sonda queda lista para la evidencia del colega.** La probé en su modo `--carpeta` con una carpeta inventada con
la forma de la suya (`mk_f10_destino.html`, `_reintento` y un `_marco`, que salta), contra `bccaf67`, la versión de su
corrida: con «Ciudad Alfa (Estado)» escrito y dos Container Yard, «(Estado)» y «(Otro)», la de `bccaf67` no calza con
ninguna (el «0 de las …» de su `log.txt`), y la regla nueva elige la del mismo paréntesis. Imprime, de cada Container
Yard, lo de afuera y lo de adentro de sus paréntesis: con eso se ve también si la suya es otro nombre (tu FRENA SI del
encargo 73).

## La red

- **En las dos direcciones, por el camino real** (`test_evidencia.TestListaDeSugerencias`, `_mk_ciudad` sobre la página
  falsa que anota cada acción), la prueba nueva `test_maersk_si_los_dos_traen_parentesis_tiene_que_ser_el_mismo`:
  - elige el mismo paréntesis escrito de otra forma, y entre «(Norte)» y «(Sur)», la que dice lo mismo que la celda;
  - **«Alfa (Norte)» contra la única «Alfa (Sur)» queda NO ENVIADA**, sin pulsar nada, con su motivo, y `log.txt` lo
    anota en las dos vueltas (la gemela Store Door con «(Norte)» no cuenta);
  - la celda sin paréntesis contra dos que solo distingue el paréntesis: ninguna, como desde el encargo 43.
- **La tabla de la regla** (`test_ayudantes.TestMAERSK.test_el_parentesis_cuenta_si_lo_traen_los_dos`): `_mk_partes`
  con anidados, varios, sin cerrar, tildes y espacios, y `_mk_calza` con los siete casos, en las dos direcciones.
- **Las fotos que cayeron a propósito:** la prueba del encargo 73 elegía «Alfa (Sur)» para «Alfa (Norte)» y no elegía
  ninguna entre «(Norte)» y «(Sur)»; esos dos casos pasaron a la prueba nueva, con lo que se espera ahora. Y las dos
  aserciones con el texto del motivo.
- **Mutaciones nuevas** (bloque del encargo 74): `mk-calza-sin-mirar-el-parentesis` (la regla de `a538b77`),
  `mk-calza-exige-el-de-la-celda` y `mk-calza-exige-el-de-la-sugerencia` (exigir el mismo aunque solo uno lo traiga),
  `mk-partes-sin-normalizar-el-parentesis`, `mk-partes-sin-guardar-el-parentesis` y
  `mk-sin-una-exacta-sin-el-parentesis` (el motivo de antes). **Actualizadas** (su texto viejo apuntaba a líneas que
  cambiaron): `mk-exacta-la-primera-container-yard`, `mk-base-con-parentesis`, `mk-base-sin-cortar-en-la-coma`,
  `mk-escrita-con-parentesis` y `mk-escrita-vacia-calza`. Cada texto viejo aparece una sola vez en el programa
  (`viejos_una_vez.py`).
- **La suite, antes del commit, sobre el árbol del commit:** 856 pruebas, OK, en 1.677 s; 0 cambios en los 5.579
  originales. Con el mismo `correr.py`, importado, con el tope de `unittest` en 3.600 s (la de 1.200 s se pasó en el 73).
- **Commit `411535c`:** la sonda de secretos dio 0 en seco y después de `git add`; el barrido por valor del encargo 72
  (76 valores vigilados) dio 0 en las 185 líneas agregadas y en el mensaje; el nombre del lugar del colega, 0; y la
  guarda del hook pasó.
- **Censo del área, sobre `411535c`** (`correr.py --mutaciones --filtro TestListaDeSugerencias`, después de las dos
  revisiones): 133 mutaciones, 165 pares, y muerden los 165, entre ellos los 18 de las once mutaciones nuevas y
  actualizadas (11 de las seis nuevas y 7 de las cinco actualizadas). Control (la copia sin mutar, 29 pruebas): pasa. Sin mutación: 0 de 856. Originales: 0 cambios en 5.579.
- **El commit de este informe** no corre la suite otra vez: la única prueba que lee un `CICLO-*.md` es la de lo que git
  versiona (`test_guarda_datos.TestLoVersionado`), y esa guarda corre a mano sobre el índice y en el hook.

## Revisión de código

Un `code-reviewer` sobre un clon de verdad, sin remoto (`.git/config` sin `[remote]`, rama `e74-commit` con `411535c`),
con el diff en un archivo. Arrancó en su worktree y no corrió `git` sobre el clon ni sobre el repo vivo; su `git status`
final, vacío. **Veredicto: APROBAR**, sin CRITICAL, HIGH ni MEDIUM.
- Corrió 27 pruebas del área sobre el clon (OK) y el censo de las mutaciones de la regla en el clon: 19 pares, todos
  muerden; control sin mutar, pasa; 0 de 856 pruebas sin mutación.
- **Lo de afuera de `_mk_partes` es idéntico a lo que daba `_mk_base`:** 0 diferencias en 200.000 textos al azar (con
  paréntesis, comas, espacios, tildes y NFD).
- **La regla nueva contra la de `a538b77`, en 300.000 pares al azar:** 1.564 dejan de calzar, 0 empiezan a calzar, y
  los 1.564 son «los dos traen paréntesis y difieren». Lo que calza ahora está contenido en lo que calzaba.
- Tres mutaciones propias: sin mirar lo de afuera en `_mk_calza` caen 4 aserciones; sin el orden (`sorted`), cae la
  tabla; sin contar los `()` vacíos, no cae ninguna (su LOW 1).

| Hallazgo | Qué hice |
|---|---|
| LOW 1: «()» vacío cuenta como paréntesis («Alfa (), País» no calza con «Alfa (Norte)», y sí con «Alfa»), y ninguna prueba lo fija | Documentado, al RESIDUAL: es la lectura literal de la decisión, y no hay un caso real |
| LOW 2: un paréntesis con una coma adentro sale de la regla, porque la parte se corta en la primera coma («Alfa (Norte, Este)» calza con «Alfa (Norte, Sur)»; igual en `a538b77`) | Al RESIDUAL: los nombres de MAERSK que conocemos no traen coma entre paréntesis |
| LOW 3: los anidados pierden su forma («Alfa (Viejo) (Norte)» y «Alfa (Norte (Viejo))» dan lo mismo), y el docstring dice «en cada nivel» cuando es «en cada pasada, los que no tienen otro adentro» | Al RESIDUAL, con la frase del docstring: no es un caso realista, y corregir el docstring pide otra vuelta de suite |
| Sin severidad: «Alfa (Norte)» con «Alfa, País» y «Alfa (Sur), País» elige «Alfa, País» (solo la celda trae paréntesis frente a esa, y calza por lo de afuera); y si el paréntesis de la celda del colega no es textualmente el del portal (una abreviatura, un punto), su fila vuelve a quedar NO ENVIADA | Al RESIDUAL: el primero es la decisión aplicada; el segundo se mide con la evidencia |

## Revisión de seguridad

Un `security-reviewer` sobre el mismo clon sin remoto, con las mismas reglas: no corrió `git` sobre el clon ni sobre el
repo vivo, no abrió ningún `.env`, `logs/`, `perfiles/`, `config.json` ni planillas, y su `git status` final, vacío.
Corrió 27 pruebas del área y 76 de las que leen el texto fuente (OK), y una sonda propia por `_mk_ciudad`.
**Veredicto: APROBAR CON CAMBIOS**, sin CRITICAL ni HIGH: el cambio «hace lo que dice y es estrictamente más
restrictivo que a538b77 en cada par». En 600.000 pares al azar, 2.589 dejan de calzar, 0 empiezan a calzar, y en los
2.589 los dos textos traen un paréntesis ASCII cerrado; en listas, ninguna elección única de la regla del 73 pasó a ser
otra. No hay datos reales en las 185 líneas agregadas ni en el mensaje.

| Hallazgo | Qué hice |
|---|---|
| **M1 · MEDIUM, no declarado: la sugerencia sin paréntesis gana por descarte.** Con la celda «Alfa (Norte)» y la lista «Alfa (Sur), País» y «Alfa, País», elige «Alfa, País»; en `a538b77` calzaban las dos y quedaba NO ENVIADA. Y con «Alfa, País» y «Alfa (Norte), País», ninguna: la que dice lo mismo que la celda no gana. Una «Alfa (Sur)» en la lista es la señal de que «Alfa» sin paréntesis puede ser otro lugar | **Lo decides tú** (abajo). Es tu decisión aplicada a la letra, par por par; el efecto es de la lista. No cambié la regla. Lo medí con las tres versiones (`listas_versiones.py`): el 43 y el 73 no eligen ninguna en esa lista, el 74 elige «Alfa, País» |
| L1 · LOW: los anidados y el orden se confunden («Alfa (Norte (Alto))» calza con «Alfa (Alto) (Norte)») | Al RESIDUAL, con el LOW 3 de la revisión de código |
| L2 · LOW: un paréntesis con una coma adentro queda sin comparar | Al RESIDUAL, con el LOW 2 de la revisión de código |
| L3 · LOW: `_mk_partes` es cuadrática con anidados, como `_mk_base`, y de 2 a 3 veces más lenta por la función interna: 4,6 s con 32.766 caracteres anidados (el tope de una celda), sin alcance práctico (la celda se teclea a 90 ms por letra, y una sugerencia de 3.000 niveles tardó 1,3 s por `_mk_ciudad`) | Documentado, como el LOW 2 de seguridad del encargo 73 |
| Sin severidad: «()» vacío cuenta como paréntesis; un espacio invisible dentro del paréntesis de la sugerencia ahora impide el calce (falla cerrado); la línea de `log.txt` no dice que el paréntesis fue la razón (el motivo sí) | Al RESIDUAL los dos primeros; el tercero, como en el 73 |

## Lo que decides tú

**Qué hacer cuando la celda trae paréntesis y la lista trae una sugerencia sin ellos** (el M1 de seguridad). Hoy, por la
decisión tal como la diste, la sin paréntesis calza siempre: si es la única que calza, se elige, aunque haya otra con
otro paréntesis; y si también está la del mismo paréntesis, calzan las dos y no se elige ninguna. Las opciones que
propone la revisión, sobre las listas de arriba. La columna «Hoy» está medida; las otras tres son reglas que no existen
en el programa, aplicadas a mano:

| Lista, con la celda «Alfa (Norte)» | Hoy (74) | (a) | (b) | (c) |
|---|---|---|---|---|
| «Alfa (Sur)», «Alfa» | «Alfa» | ninguna | «Alfa» | ninguna |
| «Alfa», «Alfa (Norte)» | ninguna | «Alfa (Norte)» | ninguna | ninguna |
| «Alfa» sola | «Alfa» | «Alfa» | «Alfa» | «Alfa» |

- **(a) Recomendada:** primero, las del mismo paréntesis que la celda; si hay una sola, esa. Si no hay ninguna, la sin
  paréntesis, pero solo si ninguna otra de la lista trae otro paréntesis. Elige lo que la celda dice, y no elige un
  lugar sin estado cuando la lista muestra que el nombre se repite.
- **(b)** Dejarlo como está, y fijarlo con una prueba por lista y en `CLAUDE.md`.
- **(c)** Si alguna de la lista trae otro paréntesis, ninguna; si no, como hoy.

(a) y (c) se separan en la segunda lista: (a) elige la que dice lo mismo que la celda, y (c) la deja como hoy, sin
ninguna. Este cambio solo llega a los colegas cuando avances `estable`: si lo decides antes, va en un encargo aparte
antes de eso.

## Decisiones que tomé solo

| Decisión | Por qué |
|---|---|
| «Normalizado» es `_mk_plano` de lo de adentro de cada paréntesis | Es la normalización que la regla ya usa para lo de afuera desde el encargo 43 |
| «Decir lo mismo» es todos los paréntesis, en el mismo orden | Es la lectura estricta: un paréntesis de más es algo que la celda no dice. En las 18 listas no hay ningún caso de varios |
| La celda sin paréntesis sigue calzando con la sugerencia que los trae | Tu decisión habla de la fila con paréntesis; este lado es la regla del 43, y cambiarlo dejaría NO ENVIADA cada celda sin el estado, con 8 de 19 Container Yard con paréntesis |
| `_mk_base` salió, y `_mk_partes` da las dos partes | Se quedó sin quien la llame; dos funciones con el mismo bucle serían dos copias de la regla |
| El motivo de la NO ENVIADA dice la regla nueva | Con el motivo de antes, «(sin lo que va entre paréntesis)», la fila del caso «(Norte)» contra «(Sur)» diría que el paréntesis no cuenta, y es lo que la dejó NO ENVIADA |
| Ciclo aparte, con su suite, sus dos revisiones y su censo | Lo pediste así, y el Modo autónomo pide las dos revisiones para código que llega al equipo |
| No cambiar la regla por el M1 de seguridad, y no fijarlo todavía con una prueba por lista | Es una regla de negocio y tiene tres salidas razonables: la decides tú. Fijarlo ahora (la opción b) sería elegir por ti, y pediría otra vuelta de suite y censo que tu decisión puede deshacer |
| No corregir la frase «en cada nivel» del docstring de `_mk_partes` | Con solo hallazgos LOW se documenta y se cierra; la frase va con el próximo cambio de esa función, que el M1 probablemente pide |

## Defectos de instrumento que me cacé

1. **El nombre `CALZA_MK` ya existía** en el bloque de mutaciones del encargo 43, para otra cosa. Lo vi al buscarlo
   antes de correr nada, y renombré el mío (`CUENTA_MK`) solo en el bloque nuevo. Es el mismo defecto del encargo 72
   (`JSC`).
2. **Un caso de la prueba nueva esperaba el espacio doble del lado de la sugerencia,** que la página falsa devuelve en
   una línea, como el programa. Cayó la prueba, y lo pasé a la celda, que es donde la normalización tiene que actuar.
3. **La tabla de las opciones del M1 la escribí mal la primera vez:** le puse a (c) «Alfa (Norte)» en una lista que (c)
   deja como hoy, sin ninguna. Lo vi al releerla contra la definición de (c). Y la escribí como «medida» cuando solo la
   columna de hoy lo está: las otras son reglas que no existen en el programa. Las dos cosas, corregidas.
4. **No vi el M1 cuando diseñé las pruebas:** probé la regla par por par (la tabla de `_mk_calza`) y por `_mk_ciudad` con
   listas de una o dos sugerencias, pero no la lista con una sin paréntesis y otra con otro paréntesis. Lo encontró la
   revisión de seguridad, que probó listas al azar.

## Premisas que se refutaron

Ninguna: la decisión es sobre lo medido en el encargo 73.

## RESIDUAL

| Qué | Condición de reapertura |
|---|---|
| **El texto de la única sugerencia del colega.** La sonda está lista y probada en su modo | Cuando la carpeta aparezca: «Re-medir», 2. Si la sugerencia dice otro nombre afuera del paréntesis, es tu FRENA SI del encargo 73 |
| **La celda sin paréntesis calza con la sugerencia que los trae** («Alfa» elige «Alfa (Norte)» si es la única) | Si quieres que eso también quede NO ENVIADA: lo decides tú, y cambiaría muchas filas (8 de 19 Container Yard traen paréntesis) |
| **«Decir lo mismo» es todos, en orden** | Si una fila real choca con eso (varios paréntesis, u otro orden) |
| **Si el paréntesis de la celda no es textualmente el del portal** (una abreviatura, un punto), la fila queda NO ENVIADA, con el «0 de las …» | Con la evidencia del colega, o con la primera fila así: la sonda imprime lo de adentro de cada lado |
| **La sugerencia sin paréntesis gana por descarte** («Alfa (Norte)» elige «Alfa, País» frente a «Alfa (Sur), País»), y la del mismo paréntesis no gana a la sin paréntesis (el M1 de seguridad) | Tu decisión entre (a), (b) y (c), en «Lo que decides tú»; antes de avanzar `estable` |
| **«()» vacío cuenta como paréntesis; una coma dentro del paréntesis lo saca de la regla; los anidados pierden su forma,** y el docstring de `_mk_partes` dice «en cada nivel» donde es «en cada pasada» (los tres LOW de la revisión de código) | Si aparece un nombre así en una lista; la frase del docstring, en el próximo cambio de esa función |
| Lo que el encargo 73 dejó abierto y este no tocó: el prefijo con nombres de 4 letras o menos, una base de una letra, lo que se teclea con el paréntesis de la celda, un salto de línea en la celda y el costo con paréntesis anidados | Las condiciones del RESIDUAL de `CICLO-maersk-parentesis.md` |

## Re-medir

1. `python <e74>/medir_listas.py` (HEAD contra el árbol, sobre `logs/`; solo cuentas). Con `--antes <commit>` compara
   contra otro.
2. Con la evidencia del colega: `python <e74>/medir_listas.py --antes bccaf67 --carpeta "<carpeta de la evidencia>"
   --ciudad "<la ciudad de la celda, con su paréntesis>"`.
3. La sonda en modo `--carpeta`, sobre la carpeta inventada: `python <e74>/armar_prueba_colega.py` y el comando de 2 con
   `--carpeta <e74>/prueba_colega --ciudad "Ciudad Alfa (Estado)"`.
4. Las pruebas, desde `tests/`: `python -m unittest
   test_evidencia.TestListaDeSugerencias.test_maersk_si_los_dos_traen_parentesis_tiene_que_ser_el_mismo
   test_ayudantes.TestMAERSK.test_el_parentesis_cuenta_si_lo_traen_los_dos`; y las mutaciones:
   `python tests/correr.py --mutaciones --filtro TestListaDeSugerencias`.

5. Las tablas de las tres versiones: `python <e74>/tabla_versiones.py` (por pares) y `python <e74>/listas_versiones.py`
   (por listas, el M1).

`<e74>` es la carpeta del encargo en el scratchpad de la sesión: no se versiona, porque la sonda lee `logs/` (datos
reales).

## NO retroceder

- **Si la celda y la sugerencia traen paréntesis, lo de adentro tiene que ser lo mismo** (`_mk_calza`): sin eso,
  «Alfa (Norte)» vuelve a elegir «Alfa (Sur)», y con el candado abierto la reserva sale con otro lugar.
- **Si solo la celda trae paréntesis, calza por lo de afuera:** sin eso, la fila del 21-10 vuelve a quedar NO ENVIADA.
- **Las dos partes salen de `_mk_partes`:** una segunda copia del bucle de los paréntesis es una segunda regla.

## Reglas de método aplicadas

`metodo-ciclo` v36: re-medir contra HEAD, control positivo que aborta (la sonda de listas, con su control sobre la regla
nueva), se mide sobre el camino real (las funciones del programa sobre las listas en Chromium, y la prueba por
`_mk_ciudad`), el negativo tiene que morder, el cambio y su guardián en la misma operación, fuente única (`_mk_partes`),
todas las suites antes del commit, los revisores en un clon sin remoto, el RESIDUAL, la base, el push (repo público: se
entrega el bloque) y el cierre sin esperas vivas. Las del módulo: las de `CLAUDE.md` (las pruebas son fotos y caen a
propósito en el mismo cambio, toda prueba con su mutación, casos sintéticos, la sonda de secretos antes del commit, la
guarda de datos reales en el hook). No chocaron.
