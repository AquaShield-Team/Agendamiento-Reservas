# Encargo 75 · MAERSK: con la celda con paréntesis decide la lista entera

**Fecha:** 2026-10-21 · **Método:** `metodo-ciclo` v36, en Modo autónomo (por omisión).

Base: `Agendamiento Reservas` @ `5ae3e3c` · árbol limpio. `origin/main` estaba en el mismo commit: los encargos 73 y 74
ya habían subido.

**Commits,** en `main` y sin push (el repo es público: el bloque lo lleva Marcelo): `7048940`, el cambio, su red y
`CLAUDE.md`; `ed4f463`, la red con lo que encontró la revisión de código; `1dd19da`, la red con lo que encontró la de
seguridad; y el de este informe.

## La decisión, y lo que hice con ella

Tu decisión, la opción (a) del encargo 74: «Primero gana la sugerencia con el mismo paréntesis que la celda. Si no hay
ninguna, gana la que no trae paréntesis, solo si ninguna otra de la lista trae un paréntesis distinto. Si no se cumple
ninguna de las dos: NO ENVIADA, sin pulsar nada.»

- **`_mk_ganadoras`** reemplaza a `_mk_calza`, que decidía par por par. Recibe las Container Yard de la lista y devuelve
  las que ganan; `_mk_ciudad` elige solo si gana una, como siempre.
- **Con la celda con paréntesis:** primero, las del mismo paréntesis (lo de adentro en `_mk_plano`, como en el 74). Si
  no hay ninguna, las que no lo traen, solo si ninguna otra con lo mismo afuera trae otro paréntesis. Si no, ninguna.
- **Con la celda sin paréntesis:** como desde el encargo 43, ganan todas las que dicen lo mismo afuera, traigan
  paréntesis o no.
- **El motivo de la NO ENVIADA** dice la regla nueva: «(sin lo que va entre paréntesis; si la celda lo trae, primero la
  del mismo, y si no hay, la que no lo trae, solo si ninguna otra con ese nombre trae otro)».
- Nada más de `_mk_ciudad` cambió: lo que escribe, la lista quieta, la evidencia, el reintento, la comprobación del
  campo.

**Dos lecturas mías, que tu decisión no dice:**
1. **(a) vale con la celda con paréntesis.** Así la planteó el informe del 74 («qué hacer cuando la celda trae
   paréntesis»). Aplicada también a la celda sin paréntesis, «Alfa» dejaría de elegir «Alfa (Norte), País» cuando es
   la única: es la forma con que MAERSK nombra muchos de sus lugares (8 de las 19 Container Yard de `logs/`), y el
   informe del encargo 43 registra un destino sin paréntesis que eligió «palabra (palabra), país», con el que la
   búsqueda encontró la nave.
2. **«Ninguna otra de la lista» es ninguna otra Container Yard con lo mismo afuera.** La lista que mira el programa son
   las sugerencias que traen los 5 primeros caracteres de lo escrito: puede traer otro lugar con paréntesis («Puerto
   Beta (Sur)» para «Puerto Alfa (Norte)»), que no dice que «Puerto Alfa» se repita. La razón de la opción (a) era
   esa: no elegir un lugar sin estado cuando la lista muestra que el nombre se repite.

Si alguna no te sirve, dímelo: cada una tiene su mutación, que la otra lectura hace caer.

**Lo que la decisión deja igual:** con dos del mismo paréntesis («Alfa (Norte), País» y «Alfa (Norte), Otro País»), o
dos sin paréntesis, ganan las dos y no se elige ninguna, como siempre.

## PASO 0

- **El registro:** el informe del 74 dejó el M1 de su revisión de seguridad como tu decisión, con tres opciones; la (a)
  era la recomendada. `CLAUDE.md` decía la regla del 74.
- **Re-medí contra HEAD (`5ae3e3c`):** `_mk_las_exactas` elegía con `_mk_calza`, par por par, y nadie más la llamaba.
- **Veredicto: CICLO.**

## Lo medido

**1. Los casos del encargo, por lista,** con `_mk_las_exactas` de cuatro versiones cargadas de su commit
(`listas_versiones.py`; control: «Alfa» contra «Alfa, País» la eligen las cuatro):

| Celda | Lista | 43 | 73 | 74 | 75 |
|---|---|---|---|---|---|
| «Alfa (Norte)» | «Alfa (Sur)», «Alfa» | ninguna (0) | ninguna (2) | «Alfa» | **ninguna (0)** |
| «Alfa (Norte)» | «Alfa», «Alfa (Norte)» | ninguna (0) | ninguna (2) | ninguna (2) | **«Alfa (Norte)»** |
| «Alfa (Norte)» | «Alfa (Sur)», «Alfa», «Alfa (Norte)» | ninguna (0) | ninguna (3) | ninguna (2) | «Alfa (Norte)» |
| «Alfa (Norte)» | «Alfa (Sur)», «Alfa (Norte)» | ninguna (0) | ninguna (2) | «Alfa (Norte)» | «Alfa (Norte)» |
| «Alfa (Norte)» | «Alfa» | ninguna (0) | «Alfa» | «Alfa» | «Alfa» |
| «Alfa (Norte)» | «Alfa», «Beta (Sur)» | ninguna (0) | «Alfa» | «Alfa» | «Alfa» |
| «Alfa» | «Alfa (Sur)», «Alfa (Norte)» | ninguna (2) | ninguna (2) | ninguna (2) | ninguna (2) |
| «Alfa» | «Alfa (Norte)» | «Alfa (Norte)» | «Alfa (Norte)» | «Alfa (Norte)» | «Alfa (Norte)» |

(Cada sugerencia, con «, País».) Con la celda sin paréntesis, las cuatro versiones eligen lo mismo.

**2. Tu FRENA SI, las 30 elecciones guardadas: no se cumple.** La sonda de los encargos 73 y 74 (`medir_listas.py`),
sobre las 18 listas de MAERSK de `logs/` con lo que su `log.txt` dice que se escribió, cargadas en un Chromium sin red
y leídas con las funciones del programa: 30 elecciones, 0 listas saltadas, 0 distintas entre HEAD (la regla del 74) y el
árbol; y 0 distintas también contra `afef717` (la del 43). Control que aborta, sobre la regla del árbol: pasa. **Este
cero sale por construcción:** ninguna ciudad escrita en `logs/` trae un paréntesis, y con la celda sin paréntesis la
regla no cambió. Prueba que no se tocó lo que ya funcionaba; lo que el cambio hace lo prueban las pruebas por listas.

**3. Tu FRENA SI, otra naviera: no se cumple.** Comparé las funciones de HEAD y del árbol por su AST, sin los docstrings
(`quien_llama.py`): cambiaron `_mk_las_exactas` y `_mk_sin_una_exacta`; salió `_mk_calza` y entró `_mk_ganadoras`.
Quien las nombra, directa o indirectamente, en todo el archivo: `la_exacta`, `_mk_ciudad` y `reservar_maersk`, y de los
reservadores y logins, solo `reservar_maersk`. El prefijo que comparte CMA (`_prefijo_de_la_lista`) y `_mk_plano` no
cambiaron. Control que aborta: `_mk_ciudad` llama a `_mk_las_exactas` y `reservar_maersk` a `_mk_ciudad`.

## La red

- **Por listas enteras, por el camino real** (`test_evidencia.TestListaDeSugerencias`, `_mk_ciudad` sobre la página
  falsa que anota cada acción), la prueba nueva `test_maersk_con_parentesis_decide_la_lista_entera`:
  - elige la del mismo paréntesis con la que no lo trae, y con esa y otra de otro paréntesis;
  - elige la que no lo trae si la otra con paréntesis tiene otro nombre, o es Store Door, o si otra sin paréntesis
    tiene otro nombre;
  - **NO ENVIADA, sin pulsar nada,** con la que no lo trae y otra del mismo nombre con otro paréntesis (en el 74 la
    elegía), con dos del mismo paréntesis, con dos que no lo traen, con una sin paréntesis de otro nombre sola, y con
    un nombre que solo empieza como el de la celda («Puerto Alfa Beta», con su paréntesis y sin él), cada una con su
    motivo y `log.txt` en las dos vueltas. Los dos últimos, de los commits segundo y tercero.
- **La tabla, por listas** (`test_ayudantes.TestMAERSK.test_la_regla_del_parentesis_por_lista`, hasta el 75
  `test_el_parentesis_cuenta_si_lo_traen_los_dos`): `_mk_partes` y 17 listas sobre `_mk_ganadoras`, con la celda con y
  sin paréntesis (dos de ellas, del segundo commit).
- **Todas las listas chicas** (`test_ayudantes.TestMAERSK.test_la_regla_por_lista_en_todas_las_listas_chicas`, del
  segundo commit, ampliada en el tercero): las celdas «Alfa», «Alfa (Norte)» y «Alfa (Sur)» contra todas las listas de
  0 a 3 sugerencias de «Alfa» y «Beta» (sin paréntesis, con «Norte» y con «Sur») y de «Alfa Beta» (sin paréntesis y con
  «Norte»): 1.755 casos. No repite cómo calcula la regla: exige lo que promete. La elegida dice lo mismo afuera; con la
  celda con paréntesis no trae otro, y si no trae ninguno, ninguna otra con ese nombre trae otro; si hay una sola con el
  mismo paréntesis, gana esa; y con la celda sin paréntesis, se elige si y solo si hay una sola con lo mismo afuera.
  Control: recorre los 1.755 casos, y hay más de 100 elegidas y más de 100 sin elegir. La tumban ocho de las diez
  mutaciones nuevas; las otras dos solo cambian si se elige, y eso no lo promete ninguna invariante. «Alfa Beta» la
  sumó la revisión de seguridad: con solo «Alfa» y «Beta», «lo mismo afuera» y «empieza igual» daban lo mismo.
- **Las fotos que cayeron a propósito:** la tabla par por par de `_mk_calza` y el texto del motivo.
- **Mutaciones nuevas** (bloque del encargo 75): sin mirar el paréntesis de la celda; sin preferir el mismo; sin mirar
  las otras (el M1 del 74); sin la que no lo trae; con otro nombre contando como «otra» (la otra lectura de «la
  lista»); el mismo paréntesis con otro nombre; y la celda sin paréntesis exigiendo que la sugerencia tampoco lo traiga
  (la otra lectura del alcance). Del segundo commit, la que no lo trae con otro nombre
  (`mk-ganadoras-la-que-no-lo-trae-con-otro-nombre`); y del tercero, lo de afuera que solo empieza igual, en la del
  mismo paréntesis y en la que no lo trae (`mk-ganadoras-la-del-mismo-por-prefijo` y
  `mk-ganadoras-la-que-no-lo-trae-por-prefijo`): diez en total. **Salieron** con `_mk_calza` las tres `mk-calza-*` del
  74 (sus equivalentes son las nuevas), y **apuntan a sus líneas nuevas** `mk-exacta-la-primera-container-yard` y
  `mk-sin-una-exacta-sin-el-parentesis`. Cada texto viejo aparece una sola vez en el programa (`viejos_una_vez.py`).
- **La suite, antes del commit, sobre el árbol del commit:** 857 pruebas, OK, en 1.520 s; 0 cambios en los 5.580
  originales. Con el mismo `correr.py`, importado, con el tope de `unittest` en 3.600 s (como en el 73 y el 74).
- **Commit `7048940`:** la sonda de secretos dio 0 en seco y después de `git add`; el barrido por valor del encargo 72
  (76 valores vigilados) dio 0 en las 166 líneas agregadas y en el mensaje; el nombre del lugar del colega, 0; y la
  guarda del hook, 0 hallazgos.
- **El segundo commit, `ed4f463`:** la suite antes, sobre su árbol: 858 pruebas, OK, en 1.285 s; 0 cambios en los
  5.580 originales. La sonda de secretos, 0 y 0; el barrido por valor, 0 en las 71 líneas agregadas y en el mensaje; el
  lugar del colega, 0; la guarda del hook, 0 hallazgos.
- **El tercer commit, `1dd19da`:** la suite antes, sobre su árbol: 858 pruebas, OK, en 2.159 s; 0 cambios en los
  5.580 originales. La sonda de secretos, 0 y 0; el barrido por valor, 0 en las 24 líneas agregadas y en el mensaje; el
  lugar del colega, 0; la guarda del hook, 0 hallazgos.
- **Censo del área, sobre `1dd19da`, en dos pasadas:** `--filtro TestListaDeSugerencias`, 139 mutaciones y 186 pares,
  y muerden los 186; y `--filtro mk-ganadoras`, para la que solo tumban las pruebas de `test_ayudantes`, 10 mutaciones
  y 29 pares, y muerden los 29. En las dos, el control (la copia sin mutar) pasa, 0 de 858 pruebas sin mutación y 0
  cambios en los 5.580 originales.
- **Las 30 elecciones, con el código final** (`1dd19da` contra `5ae3e3c`): 0 distintas, con el control en verde.

## Revisión de código

Un `code-reviewer` sobre un clon de verdad, sin remoto (`.git/config` sin `[remote]`, rama `e75-commit` con `7048940`),
con el diff en un archivo. Arrancó en su worktree y no corrió `git` sobre el clon ni sobre el repo vivo; su `git status`
final, vacío. **Veredicto: APROBAR CON CAMBIOS.**
- Las siete mutaciones nuevas muerden sus 17 pares; las 25 mutaciones que el cambio toca dan 40 pares y muerden todos;
  las tres `mk-calza-*` tienen su equivalente.
- **Enumeró 777 combinaciones** (celdas «Alfa», «Alfa (Norte)» y «Alfa (Sur)» contra todas las listas de 0 a 3
  sugerencias de «Alfa» y «Beta», sin paréntesis, con «Norte» y con «Sur»), con las funciones sacadas del archivo: la
  elegida tiene siempre lo mismo afuera que la celda; con la celda con paréntesis, nunca trae otro; la sin paréntesis
  nunca convive con otra del mismo nombre con paréntesis; con la celda sin paréntesis, 0 diferencias con el 74; y con
  la celda con paréntesis, los únicos cambios son los dos del encargo. Lo que gana en el 75 está contenido en lo que
  ganaba en el 74.
- **Mis dos lecturas:** «no contradicen la decisión ni dejan un caso sin decidir». La estricta de «la lista» difiere de
  la mía en 34 de las 777 combinaciones, siempre en que la mía elige y la estricta no; es un cambio de una línea, y
  `mk-ganadoras-otro-nombre-cuenta` la describe.
- Lanzó por error un censo más ancho de lo necesario y lo cortó él mismo por PID; no dio resultado. Busqué sus
  procesos por la línea de comandos (`correr.py`, `unittest discover`): no quedó ninguno.

| Hallazgo | Qué hice |
|---|---|
| **M1 · MEDIUM: ninguna prueba fijaba que una sugerencia sin paréntesis con otro nombre no gana.** Sin «lo mismo afuera» en la línea de las que no lo traen, las 28 pruebas pasaban, y con la celda «Alfa (Norte)» y la lista «Beta, País» se elegiría «Beta». El código estaba bien | **Arreglado** en el segundo commit: dos filas en la tabla, un caso que elige y otro NO ENVIADA por `_mk_ciudad` («Puerto Beta, País» sola), y la mutación `mk-ganadoras-la-que-no-lo-trae-con-otro-nombre`. Y, como era el segundo hueco seguido de una red hecha de casos, una prueba que recorre las 777 combinaciones del revisor (arriba, «La red») |
| L1 · LOW: las dos lecturas | Declaradas arriba, con su mutación |
| L2 · LOW: en `CLAUDE.md` los ejemplos no decían cuál era la celda | Arreglado: «Con la celda «Alfa (Norte)»: …» |
| L3 · LOW: el encabezado del bloque de mutaciones del 74 hablaba de `_mk_calza` en presente, y el docstring de `_mk_ciudad` tenía una línea corta suelta | Arreglados |
| Sin severidad: con la celda «Alfa (Norte)» y «Alfa (Sur)» + «Alfa», `log.txt` dice «0 de las 2 sugerencias … dicen …» sin decir que el paréntesis fue la razón (el motivo sí) | No lo toqué: el motivo lo explica, y la evidencia guarda la lista |

## Revisión de seguridad

Un `security-reviewer` sobre el mismo clon sin remoto, con los dos commits (`7048940` y `ed4f463`, rama `e75-final`),
con las mismas reglas: no corrió `git` sobre el clon ni sobre el repo vivo, no abrió `logs/`, `perfiles/`,
`config.json`, planillas ni `.env`, el clon quedó igual (una foto de sus 178 archivos antes y después) y su `git status`
final, vacío. **Veredicto: APROBAR**, sin CRITICAL, HIGH ni MEDIUM.
- **Contra la regla del 74,** con las funciones sacadas del archivo: 667.251 casos exhaustivos (todas las listas de 0
  a 4 sugerencias de 14 textos, y de 5 con 8, contra 9 celdas, con paréntesis vacíos, anidados, dobles, sin cerrar, tildes y
  otro país) y 900.000 al azar (con ancho completo, invisibles, saltos de línea), 0 violaciones: lo que gana en el 75
  está siempre contenido en lo que ganaba en el 74; con la celda sin paréntesis, las dos son idénticas; la elegida dice
  lo mismo afuera, y su paréntesis es el mismo o ninguno; y una elegida nunca cambia por otra. Solo cambian los dos
  casos del encargo.
- **Textos raros por el camino real** (ancho completo, espacios invisibles, otro nombre afuera, saltos de línea): fallan
  cerrado o se normalizan; los anidados y en fila se confunden, como en el 74.
- **El costo,** igual al del 74 dentro del ruido. **Nada nuevo** en `log.txt`, la pantalla o el motivo, salvo el texto
  fijo de la regla. **Sin datos reales** en las 224 líneas agregadas: la guarda del repo dio 0, con su control 2 de 2.
- Corrió el censo con `--filtro mk-ganadoras` en el clon: 8 mutaciones, 25 pares, muerden los 25.

| Hallazgo | Qué hice |
|---|---|
| **Un hueco más de la red:** con «empieza igual» en lugar de «lo mismo afuera», en la del mismo paréntesis o en la que no lo trae, ninguna prueba caía, y «Puerto Alfa (Norte)» habría elegido «Puerto Alfa Beta (Norte)» (lo que arregló el encargo 43). La enumeración usaba «Alfa» y «Beta», que no empiezan una como la otra | **Arreglado** en el tercer commit: la enumeración suma «Alfa Beta» (1.755 casos), dos casos NO ENVIADA por `_mk_ciudad`, y las mutaciones `mk-ganadoras-la-del-mismo-por-prefijo` y `mk-ganadoras-la-que-no-lo-trae-por-prefijo` |
| L1 · LOW: la señal «otra con otro paréntesis» se esconde si esa otra trae una coma dentro del paréntesis, un espacio invisible en el nombre o paréntesis de ancho completo: su parte de afuera deja de coincidir. Igual en el 73 y el 74; un portal hostil lograría lo mismo omitiéndola | Al RESIDUAL: la frase «la lista muestra que el nombre se repite» vale para paréntesis ASCII sin coma |
| L2 · LOW: anidados y en fila se confunden (el L1 del 74) | Ya en el RESIDUAL del 74 |
| L3 · LOW: `log.txt` dice «0 de las 2 sugerencias … dicen …» aunque una diga el nombre: el número ya es de las que ganan | Al RESIDUAL; el motivo dice la regla |
| Otros mutantes que sobreviven: los paréntesis comparados sin orden, y «()» tratado como celda sin paréntesis | Al RESIDUAL: son las dos lecturas que el 74 ya declaró («todos, en orden», y «()» cuenta como paréntesis) |
| Sin severidad: el prefijo con nombres de 4 letras o menos hace inalcanzable la rama «la que no lo trae» para esos nombres (falla cerrado; ya en el RESIDUAL del 73); la lista tiene que traer a la hermana cuando se decide (lo acota la lista quieta); la Store Door no cuenta como «otra» (diseño) | Ya declarados |

## Decisiones que tomé solo

| Decisión | Por qué |
|---|---|
| (a) solo con la celda con paréntesis | Así la planteó el informe del 74; con la celda sin paréntesis cambiaría elegir «Alfa (Norte)» para «Alfa», la forma con que MAERSK nombra muchos lugares |
| «Ninguna otra de la lista» es ninguna otra Container Yard con lo mismo afuera | La lista trae los 5 primeros caracteres de lo escrito, y otro lugar con paréntesis no dice que el nombre se repita; esa era la razón de (a) |
| `_mk_calza` salió, y `_mk_ganadoras` decide sobre la lista | Par por par no se puede decidir (a): necesita ver las otras |
| Las tres mutaciones de `_mk_calza` salieron, con sus equivalentes en el bloque del 75 | Su texto viejo ya no existe; dejarlas haría caer el censo, y lo que vigilaban lo vigilan las nuevas |
| La Store Door con otro paréntesis no cuenta como «otra» | La regla mira solo Container Yard desde el encargo 43, y cada Store Door viene con su Container Yard gemela |

## Defectos de instrumento que me cacé

1. **Otra vez probé por casos que se me ocurrieron, y quedó un hueco:** el encargo pedía «listas enteras, no solo
   pares», y las mías lo eran, pero ninguna traía una sugerencia sin paréntesis con otro nombre. Lo encontró la
   revisión de código enumerando todas las listas chicas. Es el mismo defecto del 74, un nivel más abajo: por eso la
   red de esta regla ahora también recorre la enumeración, no solo una lista de casos.
2. **Y la enumeración que escribí tenía su propio punto ciego:** solo «Alfa» y «Beta», que no empiezan una como la
   otra, así que no distinguía «lo mismo afuera» de «empieza igual», justo lo que arregló el encargo 43. Lo encontró la
   revisión de seguridad con mutantes propios. Una enumeración prueba lo que trae su alfabeto: el de esta ahora trae un
   nombre que empieza como otro.
3. **Volví a escribir barras invertidas por Bash** al sumar la prueba nueva a las mutaciones, contra la fila de
   «Entorno»: la herramienta juntó los pares, y la aserción del propio script (cada reemplazo, una vez) lo frenó antes
   de escribir nada. Lo rehíce con un script escrito con Write. Es la tercera vez en estos tres encargos.

## Premisas que se refutaron

Ninguna. Los dos casos medidos en el encargo 74 son los de la tabla, y salen como dice el encargo.

## RESIDUAL

| Qué | Condición de reapertura |
|---|---|
| **El texto de la única sugerencia del colega del 21-10.** La sonda sigue lista | Cuando la carpeta aparezca: «Re-medir», 2 |
| **Las dos lecturas** (solo con la celda con paréntesis; «la lista» como las de lo mismo afuera) | Si quieres la otra en alguna: su mutación ya la describe |
| **La señal «otra con otro paréntesis» se esconde** si esa otra trae una coma dentro del paréntesis, un espacio invisible en el nombre o paréntesis de ancho completo (L1 de seguridad; igual en el 73 y el 74) | Si aparece una lista así; un portal que quisiera esconderla podría también omitirla |
| **`log.txt` cuenta las que ganan** y dice «dicen» (L3 de seguridad): «0 de las 2 … dicen «Alfa (Norte)»» aunque una diga «Alfa» | Si confunde a quien lee el log; el motivo de la NO ENVIADA dice la regla |
| Lo que dejaron abiertos los encargos 73 y 74 (el prefijo con nombres de 4 letras o menos, lo que se teclea con el paréntesis de la celda, «()» vacío, una coma dentro del paréntesis, los anidados, el costo con anidados) | Las condiciones de sus RESIDUAL |

## Re-medir

1. `python <e75>/medir_listas.py` (HEAD contra el árbol, sobre `logs/`; con `--antes afef717`, contra la regla del 43).
2. Con la evidencia del colega: `python <e75>/medir_listas.py --antes bccaf67 --carpeta "<carpeta>" --ciudad "<la celda,
   con su paréntesis>"`.
3. `python <e75>/listas_versiones.py` (la tabla de cuatro versiones) y `python <e75>/quien_llama.py` (otra naviera).
4. Las pruebas, desde `tests/`: `python -m unittest
   test_evidencia.TestListaDeSugerencias.test_maersk_con_parentesis_decide_la_lista_entera
   test_ayudantes.TestMAERSK.test_la_regla_del_parentesis_por_lista
   test_ayudantes.TestMAERSK.test_la_regla_por_lista_en_todas_las_listas_chicas`; y `python tests/correr.py
   --mutaciones --filtro TestListaDeSugerencias` y `--filtro mk-ganadoras`.

`<e75>` es la carpeta del encargo en el scratchpad de la sesión: no se versiona, porque la sonda lee `logs/`.

## NO retroceder

- **Con la celda con paréntesis decide la lista entera:** par por par, la sugerencia sin paréntesis gana por descarte
  cuando hay otra del mismo nombre con otro paréntesis.
- **Con la celda sin paréntesis, la regla del 43:** «Alfa» elige «Alfa (Norte), País» si es la única.

## Reglas de método aplicadas

`metodo-ciclo` v36: re-medir contra HEAD, control positivo que aborta (la sonda de listas, la tabla de versiones y la de
llamadores), se mide sobre el camino real (las funciones de cada versión cargadas de su commit, y la prueba por
`_mk_ciudad`), un gate en cero prueba contención y no correctitud (las 30 elecciones, declarado), el negativo tiene que
morder, el cambio y su guardián en la misma operación, todas las suites antes del commit, los revisores en un clon sin
remoto, el RESIDUAL, la base, el push (repo público: se entrega el bloque) y el cierre sin esperas vivas. Las del
módulo: las de `CLAUDE.md`. No chocaron.
