# Encargo 69 · MAERSK dice cuándo el plazo de entrega de la salida no deja retirar el contenedor

**Base:** `C:\dev\Agendamiento Reservas` @ `b6ad211` · árbol limpio al empezar.

Con `metodo-ciclo` v24 al empezar, y v26 al cerrar: a mitad del ciclo, la skill pasó a la v26 (lo vi por su guardia
nueva del `cd`), la volví a invocar, y el cierre sigue la v26 (abajo, «Reglas de método aplicadas»). Todo se midió sin
abrir ningún portal: `logs/` y el HTML que guardó el programa, cargado en un Chromium sin red.

**Al abrir el ciclo (v25):** lo publicado coincide con su registro. En GitHub, `estable`, la rama que traen los equipos
de los colegas, está en `582924d`, como dice el informe del encargo 68, y `main` en `b6ad211`, que solo suma
documentación (medido con `ls-remote` al empezar y al cerrar). Ninguna librería de terceros viaja en el HTML del panel:
su único `<script src>` es su propio `/app.js`, así que no hay avisos de seguridad que consultar.

## En resumen

- **Qué cambia:** el motivo de MAERSK cuando el calendario de retiro no tiene ningún día que cumpla la regla y el
  plazo de entrega de la salida elegida lo explica. Ahora dice ese plazo, tal como lo muestra la página, y que hay que
  usar una salida posterior. Con la corrida del 15-10 habría dicho:

  > MAERSK: el plazo de entrega de la salida elegida («Gate-in deadline»: 15 Oct 2026, 21:00) no deja retirar el
  > contenedor el 16-10-2026, el primer día hábil después de hoy, ni después (el último día habilitado en el calendario
  > de retiro es el 15-10-2026): hay que usar una salida posterior; no pulsé nada más y la reserva no se envió

- **La regla no cambia:** nunca se retira el mismo día. Con un día que la cumple, MAERSK lo elige como antes, aunque el
  plazo sea anterior.
- **Sin clics nuevos:** el plazo se lee de la lista de «Select sailing», que el programa ya leía para elegir la salida.
  `test_candado` no cambió.
- **La condición de freno no se cumplió:** el plazo está en lo guardado. Las 80 tarjetas de las 8 listas guardadas traen
  su «Gate-in deadline», y las 68 que se pueden reservar, con una fecha legible.
- **Verificación:** la suite pasa entera (833 pruebas OK), y en el censo del área muerden los 627 pares de sus 455
  mutaciones.

## Dónde está el plazo (la condición de freno)

La pantalla del calendario («Additional details») no muestra el plazo: lo busqué en su HTML del 15-10 y no está. Está en
la lista de salidas («Select sailing»), dos pantallas antes, en el encabezado de cada tarjeta.

- **La forma:** el mismo par etiqueta/valor que el programa ya lee para «Departure», «Vessel/voyage» y «Transit time»
  (`.new-sailings-group-header__label` y `__value`). La etiqueta es «Gate-in deadline», y el valor, una fecha como
  «15 Oct 2026, 21:00». En las capturas del 14 y del 15-10, el OCR lee la misma columna, en mayúsculas: «GATE-IN
  DEADLINE».
- **Medido en las 8 listas guardadas con tarjetas** (`mk_f<fila>_detenida.html`, del 25-09 al 01-10; otras 2 listas
  guardadas, del 29 y el 30-09, vinieron vacías):
  - las 80 tarjetas traen la etiqueta una vez;
  - las 68 con «Book» traen su valor, con una fecha legible;
  - de las 12 sin «Book», 8 traen el valor y 4 no traen el elemento del valor;
  - ningún plazo cae después de la salida de su tarjeta.
- **La salida que el programa elige siempre trae «Book»,** así que en lo guardado siempre trae su plazo.

## El cambio

- **La lectura de salidas** (`_JS_MK_SALIDAS`) devuelve también el plazo de cada tarjeta: el valor de su «Gate-in
  deadline», con los espacios de a uno, o vacío si la tarjeta no lo trae. La etiqueta está en una constante,
  `MK_PLAZO_DE_ENTREGA`.
- **La elección de la salida** (`_mk_elegir_nave`), cuando pulsa el «Book» de la elegida, guarda su plazo en un
  diccionario (`eleccion`) que le pasa `reservar_maersk`, y lo anota en `log.txt`: «nave seleccionada: …, sale …; plazo
  de entrega («Gate-in deadline»): …».
- **La fecha de retiro** (`_mk_fecha_de_retiro`) recibe ese plazo. Si el calendario no tiene un día que cumpla la regla,
  `_mk_plazo_no_deja` decide si el plazo lo explica:
  - **con el plazo de la tarjeta:** si su fecha es anterior al primer día hábil después de hoy;
  - **sin él** (la tarjeta no lo trae, o su fecha no se lee): si el calendario muestra ese día, habilita alguno, y el
    último habilitado es anterior.

  Si lo explica, el motivo nuevo; si no, el de siempre.
- **Los días del calendario con su fecha** se leen en un solo lugar, `_mk_fechas_del_calendario`, que usan la regla y el
  motivo.

## Lo que decidí yo

| Qué | Por qué |
|---|---|
| **El motivo nuevo sale solo cuando el plazo explica el calendario vacío,** no siempre que el calendario no tiene un día que sirva | Si no, el motivo podría ser falso. Con el plazo después del día que toca, no es el plazo. Sin el plazo y sin ningún día habilitado, puede ser que el retiro abra más adelante: el 02-10, el calendario habilitaba del 12 al 16-10, 10 días después de la corrida. Si quieres la versión literal, es cambiar una condición |
| **El plazo viaja en un diccionario** que `reservar_maersk` le pasa a la elección | Así lo que devuelve la elección no cambia de forma. Cambiarla habría tocado unas 20 comprobaciones de pruebas que no tienen que ver con esto. Es el mismo estilo de `det`, la lista que ya recorre esos pasos |
| **El plazo va tal como lo muestra la página,** en inglés, hasta 40 caracteres | Es lo que el operador ve en el portal; el recorte evita que un texto raro llene la planilla |
| **Se compara la fecha del plazo, no su hora** | El calendario elige días, no horas: un plazo el mismo día que toca, a cualquier hora, todavía deja retirar ese día |
| **La lectura de los días del calendario quedó en una sola función,** y su mutación vieja se re-ancló | La usaban dos lugares. La mutación ponía la fecha inválida como «el día que toca», que la función nueva no conoce: ahora la pone como el 22-09, el día que toca en esa prueba, y muerde igual |

## Verificación

- **En una copia, antes de tocar el repo** (`scratchpad\e69\src`: el árbol de `b6ad211` con los parches):
  - las clases de MAERSK y de la fecha de retiro, y `test_candado`: 94 pruebas OK;
  - el chequeo de todas las mutaciones (`mut_viejos.py`): 2.370 mutaciones y 833 pruebas, cada texto viejo una sola
    vez, las 22 nuevas o re-ancladas compilan y ninguna prueba queda sin su mutación: 0 problemas.

  El repo quedó igual byte a byte a esa copia, y en LF.
- **Por el camino real** (`medir_e69.py`, con el JavaScript y las funciones de la copia, sobre lo guardado):
  - en las listas, las 68 tarjetas con «Book» dan su plazo legible; de las 12 sin «Book», 8 lo dan y 4 vienen vacías;
  - con los 4 calendarios guardados, los dos del 02-10 eligen el 13-10 y el del 14-10 elige el 15-10, como antes, con
    plazo y sin él;
  - el del 15-10 no elige ninguno y da el motivo nuevo: con el plazo del OCR (el de arriba, en «En resumen») y sin él
    («el plazo de entrega de la salida elegida no deja retirar el contenedor el 16-10-2026, … (el último día habilitado
    en el calendario de retiro es el 15-10-2026): hay que usar una salida posterior»).
- **La suite, sobre el repo** (`correr_sin_tope.py`, lanzada aparte): **833 pruebas OK en 1.559 s**, de las 10:09 a
  las 10:36, y la foto de los 5.574 originales da 0 cambios.
- **El censo del área** (`alcance_e69.py` y `censo_e69.py`, lanzado aparte, de las 10:46 a las 12:48):
  - **qué entró:** las 19 mutaciones del encargo y las 4 re-ancladas; las que caen a 15 líneas o menos de una de las 74
    líneas cambiadas de `AQUASHIELD.py` (98); y las que nombran una prueba cuyo camino cambió: la lectura y la
    elección de las salidas de MAERSK y su reservador, la fecha de retiro, las fotos que leen el texto del programa, la
    evidencia de cada reservador y `test_candado` (451);
  - **455 mutaciones, 627 pares y 202 pruebas:** el control pasa, y **muerden los 627**. El par más largo tardó
    174 s, y ningún motivo fue por plazo;
  - la foto de los 5.574 originales da 0 cambios.
- **Sin suspensiones:** 0 eventos de Kernel-Power desde las 10:05. La misma consulta ve 87 desde el 12-10, el último
  a las 08:15 de hoy.
- **El barrido de datos reales y la sonda de secretos:** abajo, en «El repo».

## Lo decides tú

1. **Si el motivo nuevo debe salir siempre** que el calendario no tenga un día que sirva, aunque el plazo no lo explique
   (arriba, «Lo que decidí yo»).
2. **Las revisiones de código y de seguridad del diff:** las reglas del módulo las proponen después de escribir código,
   y no las lancé, porque el encargo no es en Modo autónomo. Las corro si me lo pides.

## Residual

| Qué | Por qué no se hizo | Se reabre si |
|---|---|---|
| Que MAERSK corte antes, al elegir una salida cuyo plazo vence antes del día de retiro | El encargo pidió solo el motivo | Lo encargas |
| Que MAERSK guarde el HTML de su lista de salidas cuando elige | Es código fuera del encargo | Lo encargas |
| La etiqueta «Gate-in deadline» del portal de hoy no está medida en HTML: lo guardado llega al 01-10 | El OCR del 14 y del 15-10 la lee en la misma columna | Una corrida guarde la lista. Si la etiqueta cambiara, el plazo saldría vacío, y el motivo se decidiría por el calendario |
| No se probó en el portal | Con el candado cerrado, la fila tiene que traer una salida que cierre ese día | La próxima corrida con una salida así |

## FRENA SI

«Leer el plazo exige algo que no está en lo guardado»: no se cumplió. El plazo está en las 8 listas guardadas, en el
mismo encabezado que el programa ya lee, y no hace falta abrir el portal ni pulsar nada.

## Premisas que se cayeron

- **«Con la fecha del plazo si la página la muestra»:** la página del calendario no lo muestra; la de la lista de
  salidas, sí. Por eso el plazo se lee al elegir la salida y viaja hasta el calendario.

## Defectos de instrumento y errores míos

- **Mi espera del censo lo dio por terminado con el proceso vivo.** Buscaba su PID en la tabla de `ps -W` de Git Bash,
  y en una vuelta no lo encontró. Lo vi porque la salida no traía la foto de los originales ni el resultado; lo busqué
  por su línea de comandos y lo esperé por su PID desde PowerShell, que lo vio terminar a las 12:48. En el encargo 67
  me pasó algo parecido, con la columna del PID.
- **Mi primera copia del programa no traía los `.bat` ni el lanzador de emisión,** porque saqué solo `AQUASHIELD.py` y
  `tests/`. Por eso cayeron 3 pruebas de `test_candado`, no por el cambio. Rehíce la copia con el árbol entero de HEAD,
  y pasaron.
- **El parche de las pruebas, en su primera versión, escribía un archivo antes de validar el otro.** Frenó por una
  línea larga en el segundo, con el primero ya escrito en la copia. Lo cambié para validar los dos antes de escribir,
  rehíce la copia, y en el repo se aplicó entero. Frenó otras dos veces por líneas de más de 120 caracteres, antes de
  escribir nada.
- **Una mutación vieja quedó sin su texto** (`mk-retiro-sigue-sin-dia`): se anclaba en el bloque que ahora mira primero
  el plazo. La encontró `mut_viejos.py` antes del censo, y la re-anclé con la misma intención.
- **La sonda de los plazos vacíos falló una vez:** esas 4 tarjetas no traen el elemento del valor, no un valor vacío.
  La corregí, y así se supo cómo vienen.
- **Usé `sort` en Git Bash,** que Defender bloquea («Permission denied»), en un comando que contaba los errores de una
  corrida de pruebas. No cambió ningún resultado. Es la segunda vez en tres encargos.
- **Un `cd` en primer plano movió la sesión a `logs/`** durante un comando, como en el encargo 68. Y otro comando, que
  seguía a un `cd`, lo frenó la guardia nueva del `cd` (v26). Desde ahí, solo rutas absolutas, `git -C` y `env -C`.
- **Un heredoc me juntó las barras de una expresión** al armar el alcance del censo. Quedó bien por casualidad: Python
  dejó la barra sola tal cual, con un aviso. Lo comprobé en el archivo.

## Re-medir

Todo corre desde `scratchpad\e69`, en Git Bash, después de `source entorno_e69.sh`. Ningún script imprime naves,
viajes ni puertos.

| Número | Script |
|---|---|
| El plazo en las listas guardadas | `python plazo_guardado.py`; las que no lo traen, `python plazo_vacio.py` |
| El cambio por el camino real (las listas y los calendarios guardados) | `python medir_e69.py` |
| El chequeo de todas las mutaciones | `python mut_viejos.py <raíz> e69-` |
| El alcance del censo | `python alcance_e69.py <raíz>` |
| El censo, aparte | `python lanzar_censo_e69.py <salida> <raíz>` |
| La suite, aparte | `python lanzar_suite_e69.py` |
| Los parches | `aplicar_programa69.py`, `aplicar_pruebas69.py` y `aplicar_docs69.py` |

## NO retroceder

- **El motivo del plazo no se le atribuye a un calendario vacío que el plazo no explica.** Lo vigila
  `test_clics.TestRetiroMaersk.test_el_plazo_de_entrega_que_no_deja_retirar`.
- **La regla de la fecha de retiro sigue igual:** con un día que la cumple, lo elige, aunque el plazo sea anterior
  (`test_el_motivo_dice_el_plazo_de_entrega`).
- **El plazo viaja explícito,** por `eleccion` y `plazo=`, no por un estado compartido
  (`test_reservar_maersk_le_pasa_el_plazo_de_la_elegida`).

## Reglas de método aplicadas

`metodo-ciclo` v26 (v24 al empezar; arriba), y las reglas del módulo (`CLAUDE.md`). Sin choques entre ellas.

- **Lo de la v25 y la v26 que alcanzó a este ciclo:** lo publicado comparado con su registro y las librerías del HTML,
  al abrir (arriba); el barrido también sobre los mensajes de commit; rutas absolutas y ningún comando detrás de un
  `cd` que no aborte; y la limpieza del cierre dentro de la carpeta que borra, probada antes con un testigo (en el
  mensaje de cierre).

- **Control positivo que aborta:** las sondas del plazo (una tarjeta sintética), la medición por el camino real (que la
  copia traiga la lectura nueva, y que el calendario del 15-10 dé solo el 15-10), `mut_viejos.py` (una mutación
  sintética) y el alcance del censo (líneas cambiadas, y las re-ancladas presentes).
- **Se mide sobre el camino real:** el JavaScript del programa sobre las listas y los calendarios guardados, y sus
  funciones sobre lo que leyó.
- **El negativo muerde:** el censo.
- **Cada reemplazo, una sola vez, y la escritura validada antes:** los tres parches. El de las pruebas, en su primera
  versión, dejó escrito uno de sus dos archivos en la copia antes de frenar en el otro («Defectos», arriba).
- **El EOL:** 0 CR en los archivos tocados.
- **El cambio y su guardián juntos:** cada parte, con su prueba y sus mutaciones.
- **Residual y premisas:** declarados arriba.
- **Del módulo:** ningún portal; `test_candado` sin cambios; ningún clic nuevo; las pruebas en `soporte`, nunca el
  8765; la suite y el censo aparte; la sonda de secretos y el barrido antes de cada commit; el correo noreply.

## El repo

Dos commits en `main`, sin push (el repo es público; el push lo haces tú):

- `a0f4d06` fix: el motivo del plazo de entrega (`AQUASHIELD.py`, `tests/test_clics.py` y `tests/mutaciones.py`);
- el de este informe, `CLAUDE.md` y `LEEME.md` (docs), el siguiente.

Los dos llevan de autor y de committer el correo noreply del repo. Antes de cada uno, la sonda de secretos dio 0, y el
barrido de datos reales (`barrido_e69.py`) dio 0 en las líneas agregadas y en el mensaje del commit.

- **Qué vigila el barrido:** la máscara de la planilla, de la copia del encargo 68, de los `log.txt` y de
  `config.json`, más 4 palabras del portal que la máscara no traía.
- **Su control:** un valor de la planilla y uno de esas palabras, puestos a mano en una línea de prueba, aparecen.
