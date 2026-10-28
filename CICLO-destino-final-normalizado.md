# CICLO-destino-final-normalizado · Encargo 87: el mismo lugar escrito distinto, en MSC y CMA-CGM, y el destino final en el panel

> **metodo-ciclo v39** (la misma del disco al empezar). Base: `main` en `4812f88`, árbol limpio. **Dos commits:** el cambio
> (`22644e2`) y este informe. **No se subió nada:** el bloque de push está al final. Sin datos de clientes: las
> planillas y los log.txt del equipo se leyeron en su lugar, en solo lectura, y de ahí salieron solo cuentas; las pruebas
> usan nombres inventados.

## Qué se pidió y qué salió

El encargo, la opción (b) del encargo 86: que MSC y CMA-CGM comparen el puerto de descarga y el destino final normalizados
(sin tildes, en mayúsculas, con los espacios de a uno), y que el mismo lugar vaya por el camino de un solo puerto; lo que se
escribe en el portal, el texto de la planilla; «-» en «Puerto Descarga» como celda vacía; las dos navieras con la misma
lectura, y la prueba que las compara en pie; el panel, antes de correr, dice si la fila va con destino final y cuál; volver a
medir las 15 filas del ejemplo; prueba, mutación, revisión de código, commit sin push. FRENA SI una fila que hoy va a
CMA-CGM con puerto y rampa distintos de verdad cambia de camino, o el cambio toca otra naviera.

**No cayó en ningún FRENA**, y la regla final lo cumple por construcción, no solo en lo medido: una fila cambia de camino
solo si sus dos celdas, normalizadas, coinciden parte por parte (separadas por comas) hasta la más corta, o si el puerto es
«-». Las dos primeras versiones de la regla no lo cumplían; lo encontraron las revisiones (abajo, «Lo que salió mal»).
Ninguna otra naviera cambia: la marca del panel es solo de MSC y CMA-CGM, y los lectores de la planilla no se tocaron.

## Paso 0 (medido)

- **Las filas del equipo** (`.trabajo/e87/medir.py`, con el lector del panel, `leer_filas`, de una copia del programa, y la
  naviera de cada fila por su hoja o su columna): 4 planillas (2 en la raíz, 2 en «1. pruebas»), 6 hojas, 90 filas, 0
  hojas sin leer. 12 de CMA-CGM, separadas las 12; 27 de MSC, 7 separadas. Entre ellas, las 15 del ejemplo del dueño: 5 con
  el par del ejemplo y 2 con el otro par, separadas, y 8 con el mismo valor en las dos columnas, de un solo puerto.
  **Ninguna de las 90 cambia de camino**: ninguna trae el mismo lugar escrito distinto, ni «-» en el puerto.
- **Lo que CMA-CGM separó de verdad:** en los 50 log.txt de `logs/` y de «1. pruebas», 36 líneas «[CMA fila N] … -> PUERTO
  / RAMPA», todas con los dos, de un solo par. **Ninguna cambia.**
- **Repetido con el código** (`medir2.py`: la regla de la base, `_msc_destino_separado` de `4812f88`, sacada con git y
  ejecutada tal cual, contra `_destino_separado` del programa de hoy): lo mismo, 0 filas y 0 pares que cambien de camino o
  de textos. Su control positivo aborta si la regla de la base no separa y la de hoy no junta los casos inventados que
  motivan el cambio, o si alguna de las dos junta dos lugares distintos («Ciudad Éta» y «CIUDAD ETANA»).
- **La regla, sobre pares al azar** (`sonda_pares.py`, 210.005 pares con tildes, Ñ, mayúsculas, espacios dobles, espacio
  duro, comas y «-»): 0 pares que la base daba por un solo puerto pasan a ir aparte; los que pasan a un solo puerto son por
  «-» (5.335) o por las mismas partes normalizadas (6.813), y ningún otro motivo; separados, la regla devuelve el texto de
  las celdas en todos.

### Premisas que se corrigieron

- **«-» en el destino final como celda vacía es del encargo 43, no del 44** (`_destino_final_de`).
- **No lo leen así los dos lectores en MSC:** la rama de MSC de la consola (`leer_reservas`), sin destino final, repone la
  columna 4 tal como viene, así que con «-» la fila queda NO ENVIADA en la consola y se arma en el panel (medido por la
  revisión de código; no se cambió: es de antes y de otro lector). CLAUDE.md lo decía de los dos; ya no.
- **«-» en «Puerto Descarga» se lee como vacío solo en la regla que separa** (`_destino_separado`), no en los lectores: en
  los lectores cambiaría el destino de las otras navieras, que lo usan cuando el destino final viene vacío.

## El cambio · `22644e2`

- **`_destino_separado`, una sola regla para MSC y CMA-CGM** (reemplaza a `_msc_destino_separado`; la llaman `reservar_msc`
  y el `tiene_ramp_separado` de `reservar_cma`). Van aparte si los dos traen texto («-» en cualquiera de las dos celdas es la
  vacía; «--» o un acento suelto, un texto), ninguno contiene al otro sin distinguir mayúsculas, como siempre, y no son el
  mismo lugar escrito distinto: sus partes separadas por comas, normalizadas con `_mk_plano`, no coinciden hasta la más
  corta. «Puérto  Beta» y «PUERTO BETA, PAÍS» van por un solo puerto; «Ciudad Éta» y «CIUDAD ETANA», o «Delta, Estado A»
  y «Delta, Estado B», siguen aparte, como antes. Separados, devuelve el texto de las celdas sin los espacios de los
  extremos: lo que se escribe en el portal no cambia.
- **El panel lo dice antes de correr:** `/api/filas` trae `destino_aparte` (el puerto y el destino final) en las filas de MSC
  y CMA-CGM con nave y ruta que van aparte (`NAVIERAS_CON_DESTINO_APARTE`), y la página pinta en la celda del destino «PUERTO
  con destino final: CIUDAD», escapado como el resto de la tabla, con su estilo `.destino-aparte`. Los dos textos van
  saneados para mostrarlos (`_destino_a_la_vista`): con los espacios de a uno y cada carácter de control, de formato, privado
  o sin asignar como «?», como la marca del contenedor del encargo 65.
- **MSC escribe el destino de un solo puerto con los espacios de a uno**, como ya escribía el puerto separado: con la regla
  normalizada, el mismo lugar escrito con un salto de línea pasa a ese camino, y escrito tal cual sería la tecla Enter en la
  lista (hallazgo de la revisión de código).
- **Pruebas:**
  - `test_clics.TestDestinoFinalMsc.test_la_misma_lectura_que_cma` ahora corre lo que hace cada reservador, leído de su
    código (de `reservar_cma`, sus asignaciones de `dest_orig`, `dest_fin` y `tiene_ramp_separado`; de `reservar_msc`, la
    de `separado`), sobre 27 casos (17 nuevos), y exige lo mismo de las dos: la decisión, y separados, el texto de las celdas.
  - `test_los_dos_caminos`, con el mismo lugar escrito distinto, «-» en el puerto, dos lugares distintos con tildes y un
    salto de línea en la celda.
  - `test_web`: `test_filas_dicen_si_van_con_destino_final` (las marcas por hoja, en CONSOLIDADO, sin nave, sin ruta, con
    tildes, con «-» y con caracteres de control, invisibles y privados) y `test_la_marca_del_destino_final_es_de_quien_lo_separa`
    (las navieras marcadas son las de los reservadores que llaman a `_destino_separado`).
  - `test_envio.test_dice_si_va_con_destino_final` (la celda, corrida en Node, con HTML en las celdas).
  - Fotos que cambian a propósito: la celda del destino en `test_marca_y_cuenta_aparte_las_filas_sin_ruta` (ahora la
    constante `CELDA_DESTINO`), el nombre de la regla en `test_planilla`, y en
    `test_clics.TestSinSugerenciaNoSigue.test_sin_una_palabra_corta_el_ayudante` el POD de CMA-CGM sin una palabra pasa
    de «-» a «--»: con «-», que ahora es la celda vacía, CMA-CGM ya no separa, y la prueba dejaba de probar el corte del
    POD.
- **Mutaciones:** 26 del encargo 87; las anclas de tres del 86 (la regla) y dos del 43 (la línea de las marcas, que ahora
  sigue con `destino_aparte`).
- **CLAUDE.md:** el punto de MSC con su destino final (la regla, lo medido, el panel, los residuales), el de los lectores de
  la planilla y el número de pruebas.

## Compuertas

| compuerta | resultado |
|---|---|
| Censo de mutaciones (`--filtro e87-`) | 26 mutaciones, 37 pares, los 37 muerden; control (la copia sin mutar, 5 pruebas) pasa; 1.009 pruebas, 0 sin mutación; foto de los originales sin cambios; `RESULTADO: OK`, exit 0 |
| Censo de las mutaciones del encargo 86 (`--filtro e86-`) | 33 mutaciones, 37 pares, todos muerden; `RESULTADO: OK`, exit 0 |
| Censo de las que cambiaron de ancla o de prueba (`--filtro panel-sin-marca-de`, `--filtro test_marca_y_cuenta_aparte_las_filas_sin_ruta` y `--filtro test_sin_una_palabra_corta_el_ayudante`) | 4 mutaciones y 4 pares, 5 y 5, y 6 y 11: todos muerden; foto sin cambios; `RESULTADO: OK`, exit 0 en los tres |
| Suite completa, la final | `Ran 1009 tests in 1862.325s · OK`, foto sin cambios, `RESULTADO: OK`, exit 0 (con el tope de la corrida subido a 3.600 s, como en los encargos 85 y 86) |
| Sonda de secretos | 0 con `--dry-run` y 0 después del `git add` |
| Guarda de datos (hook pre-commit) | 0 hallazgos en los 125 archivos que se commitean |
| Guarda de datos sobre los mensajes de los commits y el informe | 1 en cada mensaje: la línea `Co-Authored-By`, la dirección pública de atribución, como en los commits de antes (no es un dato); 0 en el informe |

La primera suite completa cayó en 1 de 1.009 (abajo, «Lo que salió mal»); la de la tabla es la que se repitió después del
arreglo, sobre el árbol del commit (el número de pruebas de CLAUDE.md se puso al día después, y solo una prueba lee ese
archivo, para buscar el nombre del dueño). Los censos y las suites los corrió un ayudante, uno detrás de otro, con el
envoltorio de la salida literal; las salidas las leí yo, en `.trabajo/e87/salidas/`.

## Las revisiones

Tres, una a la vez, cada una sobre un clon en `.trabajo/e87/clon`, sin remoto: una de código, una de seguridad y una
segunda pasada de código sobre lo que cambió después de las dos. Ninguna encontró nada crítico ni alto.

| Revisión | Hallazgo | Qué se hizo |
|---|---|---|
| Código | LOW: un salto de línea en la celda llegaba crudo a «Port of Discharge» de MSC por el camino de un solo puerto (la tecla Enter en la lista) | Arreglado: ese destino va con los espacios de a uno |
| Código | LOW: la consola de MSC no lee «-» en el destino final como vacía, y CLAUDE.md decía que sí | CLAUDE.md corregido; el lector no se tocó (residual) |
| Código | LOW: un puerto sin palabra distinto de «-» («--», «N/A», «, PAIS») sigue separándose, y el panel lo marca; la fila queda NO ENVIADA en el puerto, como antes | Residual, en CLAUDE.md |
| Código | LOW: el número de pruebas de CLAUDE.md | Al día |
| Seguridad | MEDIUM: con «uno dentro del otro» sobre lo normalizado, dos lugares distintos que solo difieren en una tilde pasaban a un solo puerto (el FRENA) | Arreglado: lo normalizado decide solo el mismo lugar, y la contención queda como era |
| Seguridad | LOW: un control de dirección del texto (U+202E) daba vuelta la marca en pantalla | Arreglado: la marca se sanea para mostrarla |
| Seguridad | LOW: los caracteres invisibles (U+200B, U+00AD) no se normalizan | Residual: una fila así sigue aparte, como antes, y el «?» de la marca lo deja a la vista |
| Seguridad | LOW: un puerto hecho solo de un acento se leía como vacío | Resuelto con el arreglo de la regla (se mira el texto, no lo normalizado) |
| Seguridad | Info: la iota suscrita griega daba el único caso inverso (de un puerto a dos) | Resuelto: la regla final solo junta lo que la base ya juntaba, más lo normalizado |
| Seguridad | Info: la regla depende de `_mk_plano`, el ayudante de MAERSK | Declarado en CLAUDE.md; lo frenan los casos de la prueba |
| Segunda pasada | MEDIUM: con el nombre antes de la coma solo, dos homónimos de distinto estado o país pasaban a un solo puerto (el FRENA) | Arreglado: las partes separadas por comas, hasta la más corta |
| Segunda pasada | LOW: dos lugares de CLAUDE.md y el comentario de las mutaciones decían la regla de antes; faltaban un caso de prueba (el país solo en el puerto) y uno de los privados | Todo al día |

## Decisiones que tomé (Modo autónomo)

| Decisión | Por qué | Cómo se deshace |
|---|---|---|
| La normalización decide si es el mismo lugar (las partes, hasta la más corta), no si uno contiene al otro | La contención normalizada, y el nombre solo, juntaban lugares distintos: el FRENA. Así, una fila solo cambia de camino si la regla de antes ya la juntaba escrita igual, o por «-» | Si prefieres la lectura literal («uno dentro del otro» sobre lo normalizado), es una línea en `_destino_separado`; las pruebas dicen qué casos cambian |
| «-» en el puerto, como vacío solo en la regla | En los lectores cambiaría el destino de las otras navieras | — |
| El destino de un solo puerto de MSC, con los espacios de a uno | Con la regla nueva, un salto de línea en la celda llegaba a la lista como la tecla Enter | Una línea en `reservar_msc` |
| La marca, saneada para mostrar | Un U+202E la daba vuelta; es lo mismo que la marca del contenedor | `_destino_a_la_vista` |
| La marca va en la celda del destino: el puerto y «con destino final: …» | El encargo pide que el detalle diga si va con destino final y cuál | La celda, en `verFilas` |

## Lo que salió mal

- **Las dos primeras versiones de la regla rozaban el FRENA, y lo medido no lo mostraba.** La primera hacía «uno dentro del
  otro» sobre lo normalizado: juntaba dos lugares distintos que solo difieren en una tilde. La segunda miraba solo el nombre
  antes de la coma: juntaba dos homónimos de distinto estado. En las 90 filas y los 36 pares del equipo, ninguna de las dos
  cambiaba nada, así que la medición del paso 0 no las distinguía de la buena. Las encontraron la revisión de seguridad y la
  segunda pasada, con pares armados a mano y al azar. **Lección:** un FRENA sobre «una fila que cambia de camino» se
  comprueba sobre la regla, con pares armados para romperla, no solo sobre las filas que hay; `sonda_pares.py` es esa prueba.
- **La primera suite completa cayó en 1 de 1009:** `test_sin_una_palabra_corta_el_ayudante` usaba «-» en «Puerto
  Descarga» para hacer cortar el POD de CMA-CGM, y con el cambio esa fila va por un solo puerto. Es una foto que el encargo
  cambia a propósito, y antes de la suite yo había corrido solo las pruebas que tocaba. Pasó a «--», con su censo (6
  mutaciones, 11 pares, todos muerden), y la suite se repitió entera.
- **Windows negó una escritura de `tests/mutaciones.py`** (`OSError 22`, el de la fila de la máquina): el archivo quedó
  entero, y el segundo intento escribió.
- **La sonda que saca con git la regla de la base falló una vez:** `soporte` bloquea `subprocess` (su trampa); la lectura de
  git va antes de cargarlo.
- **Un heredoc de Bash juntó un par de barras invertidas** en un script que editaba `test_envio.py`, y su `assert` lo
  frenó antes de escribir: el script fue a un archivo.

## Residual

- La consola de MSC no lee «-» en el destino final como vacía (de antes del encargo; otro lector).
- Un puerto sin una palabra distinto de «-» se separa, el panel lo marca, y la fila queda NO ENVIADA en el puerto, como antes.
- Los caracteres invisibles no se normalizan en la regla: una fila así sigue aparte, como antes, y la marca los muestra
  como «?».
- CMA-CGM escribe su POD y su rampa con un salto de línea de la celda tal cual, como antes del encargo, en los dos caminos.
- `_destino_separado` depende de `_mk_plano`, de MAERSK.
- **No está probado en el portal:** la regla no clica nada nuevo; la marca del panel, sí se ve en la página (medida en Node).

## Push

Un commit de `main` sin subir antes de este informe (`22644e2`), y este. Los dos, con el correo noreply de autor y de
committer. Antes de subir, en una consola:

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
tú, después de probar MSC y CMA-CGM en modo prueba.
