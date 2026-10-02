# Encargo 48 · El calendario de MAERSK por su cabecera, COSCO sin formulario y el prefijo de CMA

**Base:** `C:\dev\Agendamiento Reservas` @ `36b362b` · árbol limpio.

Medido con `metodo-ciclo` v15 sobre lo guardado en `logs/`: 30 carpetas de corrida, 0 que no calzan con el patrón del
programa, y ninguna nueva desde el encargo 47 (la última es la del 02-10 a las 11:55). Nada de este encargo abrió un
portal.

## En resumen

- **MAERSK** toma el mes y el año del calendario de la fecha de retiro de los dos botones de su cabecera, si el
  calendario no trae una leyenda. **Con el calendario guardado del 02-10 elige el 13-10**, y pulsaría el botón de ese
  día y el «Done». La regla de la fecha no cambia; si no puede leer el mes y el año, NO ENVIADA, como hasta ahora.
- **COSCO**, cuando New Booking no muestra su formulario, queda NO ENVIADA, con lo que faltó y los segundos que
  esperó, y deja la captura de la ventana y el HTML de la página y de sus marcos. En `reservar_cosco`, REVISAR queda
  solo para la nave no encontrada.
- **CMA** arma el prefijo con que reconoce su lista de sugerencias con la misma función que MAERSK: la letra con tilde
  como la letra sin ella, y la ñ como n.
- **FRENA SI no se cumplió:** el lector nuevo elige el 13-10, y ninguna de las 74 reservas guardadas que llegaron a la
  guarda cambia de estado.
- **La revisión del subagente**, en un clon dentro de la carpeta del encargo, aprobó el cambio sin defectos de
  comportamiento. De sus hallazgos, de cobertura de pruebas y detalles, corregí seis en un segundo commit, el informe y
  `CLAUDE.md` van en el último, y los otros quedan anotados.
- Sin clics nuevos, y `test_candado` no cambia. La suite pasa con 573 pruebas, y el censo completo muerde con sus 1707
  mutaciones; las 6 de la revisión, en su censo filtrado.

## MAERSK: el mes y el año, de la cabecera

### El cambio

`mkCalendario` (`_JS_MK_DIAS`) le pone fecha a cada día por un atributo que la trae entera o por la leyenda de su mes
(«September 2026»). Desde hoy, **si el calendario no trae ninguna leyenda**, por los de su cabecera:

- un solo botón a la vista cuyo nombre (su `label`, su `aria-label` o su texto) es un mes en inglés, y uno solo cuyo
  nombre es un año de 4 cifras;
- y solo si los días del calendario, sin los marcados de otro mes, van del 1 al último de ese mes, una vez cada uno.
  Así no le pone ese mes a un día de otro que venga sin marca.

Si algo de eso falla, ningún día tiene fecha, y la reserva queda NO ENVIADA con el motivo de siempre («no pude
identificar por su fecha ningún día del calendario»). `log.txt` dice de dónde salió cada fecha: «cabecera: 31». Con una
leyenda, manda la leyenda, como antes.

### El calendario del 02-10

Medido sin red, con el JavaScript del programa, sobre `mk_f10_calendario.html` (la página y sus 9 marcos, cargados en
un Chromium con el JavaScript de la página apagado):

| | `36b362b` | con el cambio |
|---|---|---|
| Días | 31, 0 con su fecha (lo mismo que dijo `log.txt`) | 31, los 31 con su fecha, del 2026-10-01 al 2026-10-31, por la cabecera |
| Habilitados | | 5: del lunes 12 al viernes 16 |
| La regla | | el primer día hábil después del 02-10 es el 05-10, que no está habilitado; el 12 es feriado («Día del Encuentro de dos Mundos», en la librería holidays 0.105 instalada): **elige el 13-10** |
| Lo que pulsaría | | para el 13, el `button` de adentro de su `mc-button` (`aria-label` «13», habilitado); para el 05, nada; y el botón de adentro del «Done» |

En ningún marco hay un calendario. Lo que dice `log.txt` en ese caso: «el 05-10-2026 no está habilitado en el
calendario: elijo el siguiente día hábil habilitado, el 13-10-2026 (martes)».

## COSCO sin formulario

- Si después de abrir New Booking no aparece el marco de su formulario (bkg2), o el marco no muestra su campo «Origin
  City» en 20 vueltas de 1,5 s, `_cosco_sin_formulario` deja la captura de la ventana y el HTML de la página y de sus
  marcos (`cosco_f<fila>_sin_formulario`) y la reserva queda NO ENVIADA. El motivo, por ejemplo:

  > COSCO: abrí New Booking y su formulario (el marco bkg2) no mostró sus campos («Origin City») en 36 s; no pulsé
  > nada y la reserva no se envió

  Los segundos se cuentan desde que abre New Booking. El 02-10 habrían sido unos 36: abrió a las 11:57:40, y a las
  11:58:15 dejó de esperar.
- **Los dos casos, no solo el de los campos:** hasta hoy, sin el marco quedaba REVISAR («no cargó el formulario de
  booking»), y sin los campos, también. Tu decisión dice que REVISAR queda solo para la nave no encontrada, así que los
  dos quedan NO ENVIADA, con la misma evidencia. En `logs/`, de las 25 esperas del formulario, 24 lo encontraron, 1 se
  quedó sin los campos (la del 02-10) y ninguna sin el marco.
- La captura que COSCO ya sacaba en ese punto (`cosco_f<fila>_1_choose`, o `cosco_f<fila>_err` sin el marco) sigue.

## CMA: el prefijo de su lista

`_prefijo_de_la_lista` es ahora la única fórmula, para MAERSK (`_mk_sugerencias`) y para CMA (`_cma_puerto` y
`_cma_entrega`): los primeros 5 caracteres ASCII de la ciudad, sin tildes, la Ñ como N, en mayúsculas y con los espacios
de a uno. Para MAERSK es la misma de antes; CMA dejaba caer la letra con tilde y la ñ («PEÑA ALFA» esperaba «PEA A»), y
ahora espera «PENA ». Lo que escribe en el campo sigue con sus tildes.

- Como la fórmula es la de MAERSK, CMA también toma los espacios de a uno: un espacio doble entre las 5 primeras letras
  ya no deja el prefijo fuera de toda sugerencia.
- La sugerencia se mira como viene: en las 24 sugerencias de las listas de CMA que guardó la evidencia (45 archivos, de
  3 corridas), ninguna trae una letra fuera de ASCII.

## FRENA SI

**Con el calendario guardado del 02-10, el lector nuevo elige el 13-10** (arriba), y la sonda que lo mide aborta si no.

**Ninguna reserva guardada que llegó a la guarda cambia de estado.** De las 108 reservas de `logs/` (0 sin estado
final), 74 llegaron a la guarda: CMA-CGM 12, COSCO 19, MSC 13, ONE 11, HYUNDAI 13 y MAERSK 6.
- **El calendario:** solo lo leyó 1 reserva, la de MAERSK del 02-10, que no llegó a la guarda (NO ENVIADA ahí). El
  lector es del encargo 36, y ninguna otra corrida llegó a la fecha de retiro con él.
- **COSCO sin formulario:** 1 reserva, la del 02-10, que no llegó a la guarda (REVISAR; con el cambio, NO ENVIADA).
- **El prefijo de CMA:** de las 60 ciudades de las 20 reservas de CMA con cabecera (el origen, el destino y el lugar
  de entrega), ninguna trae una letra fuera de ASCII, y el prefijo de ninguna cambia.

## La revisión del cambio

Un subagente revisor trabajó sobre `99b3c6f`, en un clon de `main` (sin otras ramas ni etiquetas) dentro de la carpeta
del encargo, y sin tocar el repo vivo. **Su veredicto: aprobado, sin defectos de comportamiento.** Lo que verificó
corriendo:
- las pruebas tocadas y las que vigilan los clics (`test_candado`, la foto de `test_clics`): OK;
- las 16 mutaciones nuevas, una por una: todas muerden; y las 1707 anclan una sola vez;
- 600 calendarios al azar en Node, con el lector viejo y el nuevo (bisiestos, febrero de 2100, días de otro mes con y
  sin marca, leyendas, fechas por atributo, dos meses, cabeceras sin año): con leyenda, con fecha por atributo, sin
  botones, con dos meses o sin año, el resultado es el mismo que antes, y ninguna fecha equivocada;
- que `_prefijo_de_la_lista` deja a MAERSK exactamente igual.

Sus hallazgos, y lo que hice con cada uno:

| Hallazgo | Gravedad | Qué hice |
|---|---|---|
| Ninguna prueba vigila que el mes y el año se cuenten una vez cuando el `button` de adentro de su `mc-button` también trae el nombre | MEDIO | La prueba suma ese caso y su mutación. Su premisa («en el portal ese `button` tiene que mostrar el mes») no es lo medido: en el HTML del 02-10 va sin nombre. Quedan cubiertos los dos |
| Los segundos del motivo de COSCO no se comprueban en `reservar_cosco` | BAJO | La prueba corre con un reloj que avanzan las esperas, y exige 22 s sin el marco y 34 sin los campos; una mutación por cada corte |
| La página falsa de COSCO no anota lo inesperado | BAJO | La página y el marco anotan cualquier otro JavaScript, y la prueba exige esas listas vacías y ninguna espera de la página |
| Tres piezas de la cabecera sin vigilar: el año fuera del calendario, los días ocultos con `aria-hidden` y un día repetido | BAJO | Un escenario y una mutación por cada una |
| CMA: si su lista trajera la tilde («ÉXITO»), el prefijo nuevo no la reconocería, y el viejo sí cuando la tilde iba en la primera letra | BAJO | Nada: en las 24 sugerencias de CMA guardadas, ninguna trae una letra fuera de ASCII, y tu decisión es la letra sin tilde. Queda en el residual |
| El reloj de la prueba de los segundos tenía un margen de 0,3 s | BAJO | Ahora el reloj es fijo |
| El docstring de `_cosco_sin_formulario` decía que el HTML se guardaba con `AQUASHIELD_DESCUBRIR`; sin el marco, nunca se guardaba | BAJO | Corregido |
| Sin el marco salen dos capturas seguidas (`_err` y la de la evidencia) | BAJO | Nada: la de siempre sigue, y la otra es la evidencia |
| «Oct.», con punto, no se toma por un mes | BAJO | Nada: falla del lado seguro (NO ENVIADA), y lo medido es «October». Queda en el residual |
| El motivo no dice cuál de las condiciones de la cabecera falló | BAJO | Nada: lo mide el HTML de la evidencia. Queda en el residual |
| Faltaban este informe y `CLAUDE.md` al día | BAJO | El último commit |

Lo corregido va en un segundo commit, `78fd0e5`: solo pruebas, mutaciones y el docstring.

## Lo que vigila el cambio

- `test_clics.TestRetiroMaersk.test_js_calendario_por_su_cabecera`, en Node, sobre un calendario sintético con la forma
  medida: los 31 días de octubre por la cabecera y el botón del 13, también si el `button` de adentro del mes y del año
  trae el nombre; y ninguno con dos meses, sin el año, con el año fuera del calendario, con el mes que no se ve, con
  tres días sin marca antes del 1, con un día repetido o con septiembre (que no tiene 31); con una leyenda, manda la
  leyenda; y los marcados de otro mes, por su clase o por `aria-hidden`, no cuentan.
- `test_clics.TestCosco.test_sin_formulario_queda_no_enviada_con_evidencia` (los dos casos, sobre `reservar_cosco`
  entero, con un reloj que avanzan las esperas: 22 s sin el marco y 34 sin los campos; y su página y su marco falsos
  anotan cualquier otro JavaScript) y `test_revisar_solo_si_la_nave_no_esta`.
- `test_evidencia.TestListaDeSugerencias.test_cma_reconoce_la_lista_con_una_tilde_en_las_primeras_letras`, para el
  puerto y para el lugar de entrega; y `test_solo_ahi`, con la evidencia nueva de COSCO.
- 22 mutaciones nuevas: 16 en el primer commit (8 del calendario, 6 de COSCO y 2 de CMA) y 6 en el de la revisión (4
  del calendario y 2 de COSCO). La del prefijo de MAERSK sin tildes vigila también la prueba de CMA.
- **La compuerta, en dos pasos.** En una copia de `36b362b` con el cambio: la suite, 573 pruebas, OK, en 276 s (1
  saltada: la que necesita los generadores, que no están en el repo), y el censo filtrado de los JavaScript del
  calendario (31 mutaciones), `TestCosco` (98), `TestListaDeSugerencias` (125) y `test_solo_ahi` (35): los 381 pares
  muerden. En la raíz, lo mismo: 573 pruebas, OK, en 270 s, el mismo censo, y 0 cambios en los 4285 originales
  fotografiados.
- **El censo completo, sobre `99b3c6f`:** 1707 mutaciones y 2046 pares mutación-prueba, y los 2046 muerden; 0 pruebas
  sin mutación y 0 cambios en los originales, en 66 minutos.
- **El commit de la revisión, `78fd0e5`,** no cambia lo que hace el programa: solo pruebas, mutaciones y un docstring.
  Su compuerta: la suite, 573 pruebas, OK, en 270 s, y el censo de las dos pruebas que toca, con sus 6 mutaciones
  nuevas: 12 de 12 pares en la del calendario y 10 de 10 en la de COSCO, en la copia y en la raíz. Las demás pruebas
  y mutaciones son las del censo completo de `99b3c6f`, y sus anclas calzan una sola vez en `78fd0e5`.

## Re-medir

Todo corre desde `scratchpad\e48`, en Git Bash, después de `source entorno_e48.sh` (`TMPDIR`, `TEMP` y `TMP` dentro
de la carpeta), con `python3.13`. Ningún script imprime valores de la planilla ni de la cuenta.

| Número | Script |
|---|---|
| Carpetas de `logs/` | `python3.13 corridas.py 20261002` |
| El calendario del 02-10 con el lector de antes y con el nuevo, la regla y lo que pulsaría (el freno 1) | `python3.13 calendario_e48.py <copia con el cambio>` |
| Las reservas que llegaron a la guarda, y cuáles tocan los cambios (el freno 2) | `python3.13 freno_e48.py` |
| Las sugerencias de CMA guardadas con letras fuera de ASCII | `python3.13 listas_cma.py` |
| Cada log, con la máscara | `python3.13 ver_log.py <AAAAmmdd_HHMMSS> [desde] [hasta] [regex]`; su control, `python3.13 control_mascara.py` |
| La suite y el censo | `bash precenso.sh <etiqueta> <filtros…>`, `bash gate.sh <etiqueta> <filtros…>`, `bash censo.sh` |

## NO retroceder

- **La cabecera solo sin leyenda, y solo con un mes, un año y los días del 1 al último:** con menos, le pondría un mes a
  días que pueden ser de otro.
- **El calendario sin el mes y el año sigue en NO ENVIADA, sin otro clic:** cambiar de mes es un clic que no está
  permitido.
- **COSCO sin formulario queda NO ENVIADA, con la evidencia:** REVISAR es para la nave no encontrada (tu decisión).
- **Una sola fórmula para el prefijo de MAERSK y de CMA** (`_prefijo_de_la_lista`): dos copias se separan sin aviso.

## Defectos de instrumento que me cacé

- **Mi prueba de COSCO esperaba de página completa las capturas que COSCO ya sacaba:** con `full=True`, el programa
  saca la ventana salvo con `AQUASHIELD_CAPTURA_FULL`. Corregí lo esperado; el programa no tenía nada mal.
- **Las pruebas que la revisión reforzó eran mías:** la del calendario no tenía el `button` de adentro con nombre, ni el
  año fuera del calendario, ni los días con `aria-hidden`, ni un día repetido; la de COSCO aceptaba cualquier número de
  segundos y su página falsa no anotaba lo inesperado. El programa de hoy no tenía esos defectos, pero esas pruebas no
  los habrían visto en un cambio futuro.

## Premisas del encargo que se matizaron

- **«COSCO, cuando el formulario no carga sus campos»:** el cambio cubre también el caso sin el marco del formulario,
  que hasta hoy era el otro REVISAR de COSCO antes de buscar la nave; si no, REVISAR no quedaba solo para la nave no
  encontrada. En `logs/` no pasó nunca.
- **«31 s»:** fue lo que esperó los campos; desde que abrió New Booking, unos 36, que es lo que dice el motivo nuevo.

## Residual

| Qué | Por qué no se hizo | Se reabre si |
|---|---|---|
| Que el lector nuevo elija y pulse en el portal | Este encargo no abre portales | Corres la fila de MAERSK: `log.txt` dice «cabecera: 31» y el día elegido |
| Lo que sigue al calendario en MAERSK: la referencia, el Shipper, «Review booking» y los términos | Con el código de hoy, ninguna corrida llegó ahí | Lo mismo |
| Un calendario con dos meses a la vista y sin leyenda | Con dos botones de mes, ningún día tiene fecha y queda NO ENVIADA; no está medido que el portal lo muestre así | Una corrida queda NO ENVIADA ahí: su `mk_f<fila>_calendario.html` lo mide |
| El aviso de la regla no dice que saltó el 12 por feriado | La regla no cambia, y `log.txt` ya dice que el 05 no estaba habilitado y que elige el 13 | Lo decides |
| Qué mostraba COSCO el 02-10 sin su formulario | Esa corrida no guardó el HTML | La próxima vez, `cosco_f<fila>_sin_formulario.html` lo mide |
| Una lista de CMA con tildes no la reconocería el prefijo nuevo (revisión) | En las 24 sugerencias de CMA guardadas no hay ninguna; tu decisión es la letra sin tilde | Una fila de CMA con tilde queda NO ENVIADA en ese campo: su evidencia muestra la lista; reconocer las dos grafías lo decides tú |
| «Oct.», con punto, no se toma por un mes (revisión) | Falla del lado seguro, y lo medido es «October» | Un calendario así queda NO ENVIADA |
| El motivo del calendario sin fechas no dice por qué la cabecera no sirvió (revisión) | Lo mide el HTML de la evidencia | Lo decides |

## Reglas de método aplicadas

`metodo-ciclo` v15, con las reglas permanentes de `~/.claude/CLAUDE.md`:
- **Todo salto silencioso lleva contador:** 30 carpetas y 0 que no calzan; 108 reservas y 0 sin estado final; 31 días;
  25 esperas del formulario de COSCO; 60 ciudades de CMA; 45 archivos de listas de CMA y 24 sugerencias.
- **Control positivo que aborta:** la sonda del calendario aborta si el lector de `36b362b` no da lo que dijo `log.txt`
  (31 días, 0 con fecha); la del freno, si su prefijo nuevo no es el de `_mk_sugerencias` en las 36 ciudades de MAERSK
  o si la ciudad de la cabecera de CMA no es la que `_cma_puerto` anotó; la de las listas, con su HTML sintético.
- **El negativo tiene que morder:** las 16 mutaciones nuevas, en el censo filtrado y en el completo.
- **Re-medir contra HEAD; fuente única** (`_prefijo_de_la_lista`); **el cambio y su guardián, en la misma operación.**
- **Frenar si la decisión es de negocio; lo que está fuera del encargo se propone:** el aviso del feriado.
- **Todo entregable declara su base:** la primera línea.

**Choques:** las reglas de Python de ECC piden pytest, anotaciones de tipos y black; el repo usa `unittest` y su propio
estilo, y seguí el del repo (mandan las reglas permanentes y `metodo-ciclo`). La revisión por un subagente la pediste
tú, en un clon dentro de la carpeta del encargo: no choca con la regla de proponer los agentes de ECC. Entre las reglas
del método, ninguno.

## Lo que dio en el repo

- `99b3c6f` fix: el calendario de MAERSK por su cabecera, COSCO sin formulario NO ENVIADA y el prefijo de CMA sin
  tildes;
- `78fd0e5` test: lo que encontró la revisión del encargo 48 en las pruebas del calendario y de COSCO;
- y el de este informe, con `CLAUDE.md` al día.

El push lo haces tú. Los comandos, con el hash esperado, van en el mensaje final del encargo: este informe va dentro
del commit y no puede citar su propio hash.
