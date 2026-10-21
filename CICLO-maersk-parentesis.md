# Encargo 73 · MAERSK no eligió el destino de una fila con paréntesis

**Fecha:** 2026-10-21 · **Método:** `metodo-ciclo` v36, en Modo autónomo (por omisión).

Base: `Agendamiento Reservas` @ `afef717` · árbol limpio. La corrida del colega fue con `bccaf67`, y entre los dos
commits `_mk_ciudad` y sus ayudantes no cambiaron (solo la guarda de datos, el encargo 72).

**Commits,** en `main` y sin push (el repo es público: el bloque lo lleva Marcelo): `a538b77`, el arreglo, su red y
`CLAUDE.md`; y el de este informe.

## La respuesta

**MAERSK quitaba lo que va entre paréntesis solo de la sugerencia, no de lo escrito.** Una celda con la forma
«Ciudad (Estado), País», que es la forma con que MAERSK nombra sus lugares, nunca calzaba con ninguna sugerencia, ni con
la que la escribe igual. Por eso la fila del colega quedó NO ENVIADA: «0 de las 1 sugerencias Container Yard dicen «…
(…)» antes de su primera coma», dos veces, y después el corte.

**El arreglo aplica la misma regla a los dos lados** (`_mk_las_exactas`): lo escrito pasa por `_mk_base`, como la
sugerencia. Es lo que autorizaste: «si el arreglo solo aplica la misma regla a los dos lados, hazlo». No cambia qué
cuenta como igual.

**Lo que no pude medir: el texto de la única sugerencia del colega.** La carpeta de evidencias no está en la ruta del
encargo, ni en ninguna otra parte de tu perfil que busqué (abajo). Sin ese HTML no sé si la sugerencia decía la misma
ciudad (y entonces el arreglo la elige) o otro nombre (tu FRENA SI). El arreglo no depende de eso: si dice otro nombre,
la fila sigue NO ENVIADA, igual que hoy. La sonda para medirlo está lista, y se corre con un comando (en «Re-medir»).

## PASO 0

- **El registro:** la regla es la del encargo 43 (`CICLO-maersk-elige-exacto.md`), la opción recomendada a la pregunta 1
  del encargo 42 sobre la regla del encargo 41. Ese informe ya lo decía: «Lo que va entre paréntesis se quita solo de la
  sugerencia, como dijiste: si lo escrito trae un paréntesis cerrado («ALFA (NORTE)»), en la práctica no calza con
  ninguna, y la fila queda NO ENVIADA». Y una prueba lo fijaba como foto
  (`test_maersk_escribe_y_compara_con_los_espacios_de_a_uno`). No fue un descuido: fue la lectura literal, declarada.
- **El código de la corrida:** en `bccaf67`, `_mk_las_exactas` compara `_mk_base(sugerencia)` con `_mk_plano(ciudad)`.
  `_mk_plano` no quita los paréntesis. Con lo escrito «Ciudad (Estado)», lo escrito queda «CIUDAD (ESTADO)», y toda
  sugerencia queda sin su paréntesis: nunca son iguales.
- **Veredicto: CICLO.** El arreglo está autorizado y se puede medir en el camino real.

## Lo medido

**1. Dónde está la evidencia del colega.** La ruta del encargo no existe. Busqué carpetas con «colega» o «evidencia» en
el nombre, y archivos `mk_f10_destino*` o `.zip` desde el 20-10:
- en las dos carpetas de OneDrive (la personal y la de la empresa), `Desktop`, `Downloads` y `Documents`: 79.599
  archivos vistos, 0 sin leer, 0 hallazgos;
- control positivo: la misma búsqueda sobre `logs/` de este equipo encuentra 95 archivos `mk_f10_destino*`.

**2. Este equipo no tiene ninguna corrida con ese destino.** En `logs/`, 0 de 46 `log.txt` y 0 de 86 HTML de destino de
MAERSK nombran la ciudad del colega (control: «Container Yard» aparece en 9 de esos HTML).

**3. Las planillas de este equipo no traen paréntesis.** Con `leer_filas` del programa, sobre los 2 libros distintos de la
carpeta del programa que git no sigue (4 hojas, 72 filas, 12 de cada naviera): 0 filas con un paréntesis en el puerto
de carga, el destino final o el destino original. 0 hojas sin leer.

**4. El arreglo no cambia ninguna elección guardada.** Sobre las 18 listas de origen y destino de MAERSK de `logs/`,
cargadas en un Chromium sin red y leídas con las funciones del programa (antes, HEAD; después, el árbol con el arreglo),
cada una con lo que su `log.txt` dice que se escribió:
- 30 elecciones, 0 listas saltadas, 0 elecciones distintas entre antes y después;
- 0 ciudades escritas con un paréntesis;
- de las 19 Container Yard distintas de esas listas, 8 traen un paréntesis antes de su primera coma: la forma es común
  en MAERSK;
- 0 listas con dos Container Yard que solo distinga lo que va entre paréntesis.
- Control que aborta: en una lista sintética, lo escrito con paréntesis da 0 antes y 1 después, y sin ellos, 1 y 1.

**5. El origen de MAERSK tiene el mismo defecto, y el mismo arreglo.** El origen y el destino los elige la misma función,
`_mk_ciudad` (`test_cada_reservador_la_pide_para_su_origen_y_su_destino` fija las dos llamadas).

**6. El prefijo de CMA-CGM no tiene este defecto.** `_prefijo_de_la_lista`, que comparten CMA y MAERSK para reconocer su
lista, toma los primeros 5 caracteres de lo escrito y los busca en la sugerencia, los dos con sus paréntesis: no quita
nada de ningún lado. CMA no compara la sugerencia entera: pulsa la primera con esos 5 caracteres. Para la celda del
colega, el prefijo son las 4 letras de la ciudad y el espacio: el paréntesis no llega a él. Medido con el programa,
sobre celdas inventadas: «Puerto Alfa (Norte)» da «PUERT», «Alfa (Norte)» da «ALFA », y el paréntesis entra solo si
empieza antes del sexto carácter («Mo (Sur)» da «MO (S»). Si el portal de CMA trae sugerencias con lo escrito entre
paréntesis no está medido: no hay ninguna corrida de CMA con una celda así.

## El cambio

- `AQUASHIELD.py`, `_mk_las_exactas`: lo escrito pasa por `_mk_base`, como cada sugerencia. Si lo escrito no deja nada
  fuera de los paréntesis («(Estado)»), no calza con ninguna: sin eso, calzaría con una sugerencia que tampoco deja
  nada. Los docstrings de `_mk_base` y `_mk_ciudad`, y el comentario de `MK_CONTAINER_YARD`, lo dicen.
- Lo que se escribe en el campo no cambia: la ciudad con su paréntesis, como antes. En la corrida del colega, con eso el
  portal mostró su lista.
- El motivo de la NO ENVIADA y la línea de `log.txt` no cambian.
- `CLAUDE.md`: la regla, con el porqué y lo medido.

**La consecuencia, a la vista:** el paréntesis ya no distingue, de ningún lado. Con una sola Container Yard que dice lo
mismo fuera de él, se elige esa, aunque su paréntesis sea otro («Alfa (Norte)» escrito elige «Alfa (Sur), País» si es la
única). Con dos que solo se distinguen por el paréntesis, ninguna, y la fila queda NO ENVIADA. Es lo que dice la regla
aplicada a los dos lados; en las 18 listas guardadas no hay ningún caso así. La prueba lo fija, para que se vea.

## La red

- **Prueba nueva:** `test_evidencia.TestListaDeSugerencias.test_maersk_quita_los_parentesis_de_los_dos_lados`, por el
  camino real (`_mk_ciudad` sobre la página falsa de sugerencias, que anota cada acción):
  - elige la sugerencia que escribe igual la celda con paréntesis (la forma del 21-10);
  - elige con el paréntesis solo en la celda;
  - elige la única, aunque su paréntesis sea otro, y la Store Door gemela de la celda no cuenta;
  - no elige ninguna con dos que solo distingue el paréntesis, ni con lo escrito sin nada fuera de ellos; corta con su
    motivo, sin pulsar nada, y `log.txt` anota las dos vueltas.
- **La foto que cayó a propósito:** `test_maersk_escribe_y_compara_con_los_espacios_de_a_uno` fijaba que lo escrito con
  paréntesis no calzaba. Esa parte salió; la de los espacios queda igual.
- **Mutaciones** (`tests/mutaciones.py`, bloque del encargo 73), cada una corrida sola, con su control (la copia sin
  mutar pasa) y 0 cambios en los 5.578 originales:
  - `mk-escrita-con-parentesis` (lo escrito con `_mk_plano`, como hasta hoy): muerde (la celda con paréntesis corta en
    vez de elegir);
  - `mk-escrita-vacia-calza` (sin mirar si queda algo fuera de los paréntesis): muerde (lo escrito «(Norte)» elige la
    sugerencia «(Norte), País»).
- **La suite, antes del commit, sobre el árbol del commit:** 854 pruebas, OK, en 1.340 s; 0 cambios en los 5.579
  originales. La primera corrida no dio resultado: `correr.py` corta la de `unittest` a los 1.200 s, y la cortó (abajo,
  «Defectos de instrumento»). La segunda corrió con el mismo `correr.py`, importado tal cual, con ese tope en 3.600 s
  (`suite_sin_tope.py`): la misma corrida y la misma foto.
- **Commit `a538b77`:** la sonda de secretos dio 0 en seco y después de `git add`; el barrido por valor del encargo 72
  (76 valores vigilados de la planilla, los `log.txt` y `config.json`, con su control) dio 0 en las 87 líneas
  agregadas y en las 17 del mensaje; el nombre del lugar del colega, 0; y la guarda del hook, 0 hallazgos.
- **Censo del área, sobre `a538b77`** (`correr.py --mutaciones --filtro TestListaDeSugerencias`: las mutaciones cuyas
  pruebas están en esa clase, la de los ayudantes de origen y destino de las seis navieras): 127 mutaciones, 154 pares,
  y muerden los 154. Control (la copia sin mutar, 27 pruebas): pasa. Sin mutación: 0 de 854. Originales: 0 cambios en
  5.578. Entre ellas, `mk-prefijo-con-los-espacios`, que mordía con la parte de la prueba de los espacios que se quedó,
  sigue mordiendo.
- **El commit de este informe** no corre la suite otra vez: la única prueba que lee un `CICLO-*.md` es la de lo que git
  versiona (`test_guarda_datos.TestLoVersionado`, que recorre `git ls-files`; busqué en `tests/test_*.py` quién lee
  `.md`: además, `LEEME.md` y `CLAUDE.md`, que no cambian). Esa misma guarda corre a mano sobre el índice y en el hook.

## Revisión de código

Un `code-reviewer` sobre un clon de verdad, sin remoto (`.git/config` sin `[remote]`, en la rama `e73`), con el diff en
un archivo. Arrancó en su worktree y no corrió `git` sobre el clon ni sobre el repo vivo; su `git status` final, vacío.
Corrió 134 pruebas de `test_evidencia` y `test_ayudantes`, y 21 de las que leen el texto fuente (OK), las dos mutaciones
en copias, y una sonda propia por `_mk_ciudad`. **Veredicto: APROBAR CON CAMBIOS**, sin CRITICAL ni HIGH: «el código
hace lo que dice y nada más», y no hay regresión (todo lo que calzaba antes calza ahora: si una sugerencia calzaba con
lo escrito sin quitarle nada, lo escrito no tenía paréntesis cerrados, y `_mk_base` lo deja igual).

| Hallazgo | Qué hice |
|---|---|
| H1 · MEDIUM: una celda «Alfa (Norte)» elige «Alfa (Sur), País» si es la única Container Yard; antes quedaba NO ENVIADA. Es la regla autorizada, no un defecto | Ya estaba declarado («La consecuencia, a la vista») y la prueba lo fija. Va al RESIDUAL como decisión tuya |
| H2 · LOW: con un nombre de 4 letras o menos, el prefijo de 5 caracteres toma el espacio o el paréntesis («Alfa (Norte)» da «ALFA »), y una sugerencia sin él («Alfa, País») no se reconoce como lista: NO ENVIADA | Al RESIDUAL, con el caso. Arreglarlo es tocar el prefijo, que comparte CMA |
| H3 · LOW: `CLAUDE.md` seguía diciendo que el paréntesis se quita solo de la sugerencia | Ya corregido en el árbol cuando armé el clon; va en el mismo commit |
| H4 · LOW: una línea del docstring de `_mk_ciudad` de 182 caracteres | Ya corregido (0 líneas agregadas de más de 120) |
| Notas sin severidad: la línea de `log.txt` no dice que el paréntesis no cuenta; el parámetro de `_mk_base` se llama `sugerencia` | No las toqué: el motivo de la NO ENVIADA sí lo dice, y renombrar movería otras fotos |

## Revisión de seguridad

Un `security-reviewer` sobre el mismo clon sin remoto, con el commit `a538b77` (rama `e73-commit`), con las mismas
reglas: no corrió `git` sobre el clon ni sobre el repo vivo, no abrió ningún `.env`, `logs/`, `perfiles/`,
`config.json` ni planillas, y su `git status` final, vacío. Corrió 30 pruebas del clon (OK) y sacó las funciones de la
regla del archivo con `ast`, sin importarlo. **Veredicto: APROBAR**, sin CRITICAL ni HIGH.
- **Regla vieja contra la nueva, en 400.000 pares al azar** (con paréntesis, comas, letras de ancho completo, espacios
  invisibles y saltos de línea): 0 casos que calzaban y ya no calzan; 17 nuevos que calzan, todos con un par de
  paréntesis ASCII cerrado en la celda; 0 de un texto vacío con una sugerencia vacía. Y en 100.000 textos, `_mk_base`
  siempre termina.
- **Los paréntesis raros fallan cerrado:** los de ancho completo, corchetes, llaves, comas que no son ASCII y un espacio
  invisible dentro del nombre no calzan, o calzan solo con una sugerencia que dice exactamente lo mismo.
- **No se registra ni muestra nada nuevo,** y no hay datos reales en las pruebas, el mensaje del commit, `CLAUDE.md` ni
  el borrador de este informe.

| Hallazgo | Qué hice |
|---|---|
| 1 · MEDIUM, declarado: el paréntesis ya no distingue (el H1 de la revisión de código). Propone, si lo quieres cerrar, exigir el mismo paréntesis cuando los dos lados traen uno, o al menos una línea en `log.txt` cuando difieren | Al RESIDUAL, como decisión tuya: exigirlo es cambiar qué cuenta como igual, y la línea de aviso depende de lo que decidas |
| 2 · LOW: `_mk_base` es cuadrática con paréntesis anidados (sin retroceso catastrófico: siempre termina). Medido: 1,89 s con 16.000 caracteres anidados, 6,9 s con 32.766, el tope de una celda; sin anidar, 0,3 s con un millón. No se alcanza por la celda: el programa la teclea con 90 ms por letra dentro del plazo de 30 s de Playwright, y a los 330 caracteres cuesta menos de 12 ms (lo leyó en el código de Playwright, sin correrlo). El lado de la sugerencia ya pasaba por `_mk_base` | Documentado. Si se quiere, un tope de largo |
| 3 · LOW: el guardia de lo escrito vacío no cubre una base de una letra o sin letras: «X (Norte)» da «X», y calza con «X, País»; «-- (Norte)», con «--, País» | Documentado y no lo cambié: exige un lugar que se llame «X», el prefijo de 5 caracteres (con el paréntesis) deja afuera casi todo, y antes del commit esa celda tampoco calzaba con otra cosa. Cerrarlo es una línea (`if not _ciudad_de(escrita)`), al RESIDUAL |
| 4 · LOW, de antes: un salto de línea dentro de la celda (Alt+Enter) se teclea como Enter (leído en Playwright, sin correrlo). La comprobación del campo limita el daño | Al RESIDUAL: no es de este cambio |

## Decisiones que tomé solo

| Decisión | Por qué |
|---|---|
| Seguir sin la evidencia del colega, con el arreglo y su red | El arreglo no depende del texto de la sugerencia: si es la misma ciudad, la elige; si es otro nombre, la fila sigue NO ENVIADA, como hoy. Tu FRENA SI queda para cuando se mida |
| Lo escrito sin nada fuera de los paréntesis no calza | Con la regla aplicada tal cual, «(Estado)» daría vacío, y calzaría con una sugerencia que tampoco deja nada fuera. Cortar es la dirección segura: queda NO ENVIADA, como hoy |
| No tocar el prefijo (`_prefijo_de_la_lista`) | No tiene este defecto (compara los dos lados con sus paréntesis), y lo comparte CMA, fuera del arreglo |
| No cambiar lo que se escribe en el campo | No es la regla, y en la corrida del colega el portal mostró su lista con lo escrito con paréntesis |
| No cambiar el motivo ni la línea de `log.txt` | Siguen diciendo lo que pasó, y cambiarlos movería otras fotos sin necesidad |
| No nombrar la ciudad del colega en el repo | Es un dato de su corrida: el encargo pide que no entre. En las pruebas y en este informe va «Ciudad (Estado), País» |
| La prueba fija la consecuencia (el paréntesis no distingue) | Para que se vea y no se lea como un descuido; si la quieres distinta, es una decisión tuya (RESIDUAL) |
| Repetir la suite con el tope de `unittest` en 3.600 s, sin tocar `correr.py` | Con la carga de otras sesiones tardó 1.340 s; la corrida y la foto son las mismas. Cambiar el tope en el repo no es de este encargo |
| Armar el clon de revisión con los tres archivos del cambio antes del commit, y sin `CLAUDE.md` | Para que la revisión corriera mientras terminaba la segunda mutación; `CLAUDE.md` no es código, y el revisor lo vio desactualizado (H3), ya corregido |
| Sumar la revisión de seguridad, que el encargo no pedía | El Modo autónomo la pide para todo cambio de código que llega al equipo. La lancé después del censo, para que su worktree no cruzara la foto de los originales |
| No arreglar los tres LOW de seguridad | El método: con solo hallazgos BAJA, se documentan y se cierra. Ninguno es de lo que pide el encargo, y cada uno costaría otra vuelta de suite y censo |

## Defectos de instrumento que me cacé

1. **El control de la sonda de `logs/` era un supuesto:** usé «San Antonio» como control, sin medir que lo trajera algún
   archivo. Abortó, como tiene que hacer, y lo cambié por «Container Yard» en los HTML de destino, que sí está.
2. **Escribí código con barras invertidas por Bash**, contra la fila de «Entorno»: el bloque de mutaciones quedó con
   saltos de línea reales dentro de sus cadenas. Lo vi al mirar el final del archivo, antes de correr nada, y lo corregí
   con un script escrito con Write, que reemplazó el tramo una sola vez y comprobó que el archivo compilara.
3. **Usé `sort` de Git Bash** en una tubería: la guardia de Defender lo frenó antes de correr. Rehice el comando sin él.
4. **Lancé la suite mientras el revisor corría pruebas,** con otras dos sesiones cargando el equipo (un censo de
   `lanzador-modulo` con tres `pytest`, y una suite de Control-Congelado). Tardó más de los 1.200 s que le da
   `correr.py`, y se cortó sin resultado. No quedó ningún proceso suyo vivo. La repetí con el tope en 3.600 s.

## Premisas del encargo que se refutaron

- **La ruta de la evidencia no existe** (arriba, «Lo medido», 1).
- **«La regla del encargo 41 (variante A)»:** la regla es la del encargo 43, la opción A de la pregunta del encargo 42
  sobre la regla del 41. Y que lo escrito con paréntesis no calzaba no estaba sin medir: el informe del 43 lo declaró,
  y una prueba lo fijaba. Lo que la hipótesis decía de la causa sí se confirmó, en el código.

## RESIDUAL

| Qué | Condición de reapertura |
|---|---|
| **El texto de la única sugerencia del colega, y qué elige la regla corregida.** Sin su HTML no se mide | Cuando la carpeta aparezca: el comando de «Re-medir», 2. Si la sugerencia dice otro nombre, es tu FRENA SI |
| **El paréntesis ya no distingue** («Alfa (Norte)» elige «Alfa (Sur)» si es la única; las dos revisiones lo marcaron como MEDIUM, declarado) | Si quieres que, cuando los dos lados traen paréntesis, tengan que decir lo mismo (sigue pasando el caso del 21-10 y el del paréntesis solo en la celda), o solo un aviso en `log.txt` cuando difieren: es cambiar qué cuenta como igual, y lo decides tú |
| **Una base de una letra o sin letras** («X (Norte)» da «X») calza con una sugerencia que diga lo mismo fuera del paréntesis (LOW 3 de seguridad) | Si lo quieres cerrado: `if not _ciudad_de(escrita)` en `_mk_las_exactas`, con su prueba y su mutación |
| **`_mk_base` es cuadrática con paréntesis anidados** (LOW 2 de seguridad), sin alcance por la celda | Si el programa empieza a leer lo escrito de otro lado que no sea el tipeo |
| **Un salto de línea dentro de la celda se teclea como Enter** (LOW 4 de seguridad, de antes de este cambio) | Si aparece una celda así: `" ".join(ciudad.split())` antes de escribir |
| **Con un nombre de 4 letras o menos, el prefijo toma el espacio o el paréntesis** («Alfa (Norte)» da «ALFA », «Mo (Sur)», «MO (S», y «(Norte) Alfa», «(NORT»), y una lista cuya sugerencia no los trae ahí no se reconoce: la fila queda NO ENVIADA (H2 de la revisión, medido con la página falsa) | Si aparece una fila así. Arreglarlo es tocar `_prefijo_de_la_lista`, que comparte CMA |
| **Lo que se escribe en el campo lleva el paréntesis de la celda.** Si el buscador de MAERSK no trae nada con un paréntesis que no es el suyo no está medido: el único caso medido es el del 21-10, y ahí trajo su lista | Si una fila así queda NO ENVIADA con «una sugerencia para …» |
| **CMA con una celda con paréntesis:** si su portal trae sugerencias con lo escrito así no está medido | Con una corrida de CMA con una celda así |

## Re-medir

1. `python <e73>/medir_listas.py` (antes y después sobre las listas de `logs/`; imprime solo cuentas).
2. Con la evidencia del colega: `python <e73>/medir_listas.py --carpeta "<carpeta de la evidencia>" --ciudad "<la ciudad
   de la celda, con su paréntesis>"`. Imprime cada Container Yard de la lista, su parte antes de la coma sin el
   paréntesis, y qué elige la regla antes y después.
3. `python <e73>/filas_con_parentesis.py` (las planillas de este equipo), `python -I <e73>/lugar_del_colega_local.py`
   (`logs/`), `python <e73>/buscar_evidencia.py <raíces>` y `python <e73>/prefijos.py`.
4. La prueba: `python -m unittest test_evidencia.TestListaDeSugerencias.test_maersk_quita_los_parentesis_de_los_dos_lados`
   (desde `tests/`), y las dos mutaciones: `python tests/correr.py --mutaciones --filtro mk-escrita-`.

`<e73>` es la carpeta del encargo en el scratchpad de la sesión: no se versiona, porque sus sondas leen `logs/` y las
planillas (datos reales).

## NO retroceder

- **Lo escrito pasa por `_mk_base`, como la sugerencia.** Volver a `_mk_plano` deja NO ENVIADA toda fila con la forma con
  que MAERSK nombra sus lugares.
- **Lo escrito sin nada fuera de los paréntesis no calza.** Sin esa línea, «(Estado)» calzaría con cualquier sugerencia
  que tampoco deje nada fuera.

## Reglas de método aplicadas

`metodo-ciclo` v36: control positivo que aborta (la búsqueda de la evidencia, la sonda de `logs/` y la de listas), todo
salto con su contador, se mide sobre el camino real (las funciones del programa sobre las listas en Chromium, y la
prueba por `_mk_ciudad`), el negativo tiene que morder (cada mutación sola), el cambio y su guardián en la misma
operación, re-medir contra HEAD, las premisas refutadas, el RESIDUAL, la base, todas las suites antes del commit, los
revisores en un clon sin remoto, el push (repo público: se entrega el bloque), y el cierre sin esperas vivas. Las del
módulo: las de `CLAUDE.md` (las pruebas son fotos, toda prueba con su mutación, casos sintéticos, la sonda de secretos
antes del commit, la guarda de datos reales en el hook). No chocaron.
