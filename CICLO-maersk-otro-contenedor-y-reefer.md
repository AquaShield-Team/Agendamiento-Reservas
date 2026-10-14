# Encargo 63 · MAERSK corta la fila que pide otro contenedor, y elige el tipo reefer por su texto entero

**Base:** `C:\dev\Agendamiento Reservas` @ `fea432f` · árbol limpio al empezar.

Con `metodo-ciclo` v20 (la versión del archivo; la sesión la tenía cargada). Sin abrir ningún portal y sin red.

## En resumen

- **Una fila de MAERSK que pide otro contenedor que «40 HC REEFER» queda NO ENVIADA sin entrar al portal,** con el
  motivo en pantalla, en `log.txt` y en la planilla. El panel web y la consola la apartan antes de abrir el
  navegador, como la fila sin nave o sin ruta, y `reservar_maersk` lleva además un decorador que la corta sin tocar la
  página. Las otras navieras no miran el contenedor.
- **En los ajustes reefer, MAERSK pulsa la única opción cuyo texto entero es «Standard (40´)»,** con el acento agudo
  (U+00B4) que trae el portal, y antes deja la evidencia de la lista (`mk_f<fila>_reefer`: la captura de la ventana y
  el HTML). Si no hay exactamente una, NO ENVIADA con el motivo, la captura y el HTML, sin pulsar nada. Lo hace con el
  mismo ayudante del tipo de contenedor del encargo 62 (`_mk_elegir_unica`): una sola regla para las dos listas.
- **La condición de freno no salta con lo medido:** las 7 reservas de MAERSK que llegaron a la guarda eligieron
  «Standard (40´)», con ese mismo carácter, y nada de lo guardado dice que pidieran otro contenedor que «40 HC
  REEFER». Lo que no se pudo medir: si su lista traía una sola «Standard (40´)», y qué contenedor decía su fila (ni
  `log.txt` ni la evidencia lo guardan; ver «FRENA SI»).
- **Medido con Playwright de verdad, sin red:** el código de este encargo elige «Standard (40´)» aunque la lista ponga
  antes «Standard (40')»; el de antes, sobre la misma página, eligió esa, y sin una opción de 40 pies, «Standard
  (20´)».

## Paso 0

- **Lo que hacía MAERSK en los ajustes reefer** (dentro de `reservar_maersk`): pulsa «Select reefer container type
  and size» (el campo abre su lista al recibir el foco), espera 1,5 s y, en hasta 10 lecturas, pulsa la primera
  opción a la vista que trae «40» o, si ninguna lo trae, la primera de todas (`op.first`). Si algo fallaba, lo anotaba
  («reefer cont err») y seguía sin el tipo.
- **Lo que hacía con el contenedor de la fila:** nada, salvo armar la palabra que escribe en la lista de tipos («40»,
  «45» o «20», y «Reefer» si el texto trae «REEF», «RF» o «RH»). Con otro contenedor, escribía otra palabra; sin esas
  letras, se saltaba los ajustes reefer y la temperatura.
- **Cómo llega el contenedor:** los dos lectores lo leen de una columna «Tipo contenedor» o «Contenedor». Sin la
  columna, los dos dan «40 HC REEFER»; con ella, el panel le da ese valor también a la celda vacía, y la consola la
  deja vacía.
- **Veredicto:** CICLO.

## Lo medido antes de cambiar nada

**Lo que eligió MAERSK en los ajustes reefer** (`medir_reefer.py`): cada bloque «[MAERSK fila N]» de cada `log.txt`,
con su «reefer cont:», sus caracteres que no son ASCII y si llegó a la guarda (como en el encargo 62). 0 carpetas sin
`log.txt`; 0 bloques de MAERSK sin esa línea; 0 «reefer cont err». Control positivo que aborta: las 21 filas del
encargo 62.

| Qué | Resultado |
|---|---|
| Filas de MAERSK que llegaron a los ajustes reefer | 21, del 21-09 al 08-10 |
| La opción que pulsó | «Standard (40´)» en las 21, con U+00B4 (ACUTE ACCENT) en las 21 |
| Las que llegaron a la guarda | 7 (las 5 del 21-09, la del 24-09 y la del 02-10): «Standard (40´)» en las 7 |
| Su lista de opciones | No se guardó nunca: 0 `mc-option` en los 322 HTML de MAERSK de `logs/` |
| Lo que sí guardó el HTML | El valor elegido, «Standard (40´)», en el campo `reeferContainer` (29-09 y 30-09) y en la revisión (02-10) |

**El contenedor de las filas** (`medir_planillas.py`, del encargo 62, con los respaldos y las planillas de `logs/` en
el universo): 2 planillas (la de la carpeta del programa y la última subida al panel), 0 respaldos y 0 planillas en
`logs/`. Ninguna tiene columna de contenedor: sus 36 filas llegan con «40 HC REEFER».

**La regla nueva sobre esas planillas** (`medir_regla.py`, con los dos lectores de una copia del programa): por el
panel, 36 filas, 6 de MAERSK, **0 NO ENVIADA** por la regla. La consola no puede correr MAERSK con ellas: no tienen
una hoja de MAERSK (`ValueError` de `leer_reservas`), así que su medición está vacía. Control positivo que aborta: una
planilla sintética con una fila de MAERSK que pide «20 DRY» da 1 con los dos lectores.

## Lo que cambió

- **La fila que pide otro contenedor** (`_otro_contenedor`, `CONTENEDOR_DE_LAS_FILAS`, `_sin_el_contenedor`):
  - si la fila es de MAERSK y su contenedor, sin distinguir mayúsculas y con los espacios de a uno, no es «40 HC
    REEFER», da el motivo: «la fila pide el contenedor «20 DRY», y en MAERSK el programa reserva solo «40 HC REEFER»»;
    con la celda vacía (la consola, con la columna), «la fila no dice qué contenedor pide, y…»;
  - el panel web y la consola apartan esa fila antes de abrir el navegador, después de la fila sin nave y de la sin
    ruta, y si no queda ninguna, no lo abren: «De las filas de MAERSK con nave y ruta, ninguna pide el contenedor «40
    HC REEFER»: no abro el navegador ni entro al portal.»;
  - `reservar_maersk` lleva `_mk_con_el_contenedor_de_la_fila`, por dentro de todos sus decoradores: la fila sin nave
    o sin ruta dice eso.
- **Los ajustes reefer** (`_mk_elegir_reefer`, `MK_REEFER`): el mismo clic de antes en el campo; la lista leída hasta
  que dos lecturas seguidas den lo mismo; la evidencia; la única opción «Standard (40´)»; si la lista cambió mientras
  guardaba la evidencia, si no hay una sola, o si el campo o el clic fallan, NO ENVIADA sin pulsar nada («Tipo de
  contenedor reefer de MAERSK»).
- **Un solo ayudante para las dos listas** (`_mk_elegir_unica`): lo que el encargo 62 escribió para el tipo de
  contenedor, con el texto buscado, el paso, el nombre de la lista y el de la evidencia como parámetros. `log.txt`
  dice «lista de tipos de contenedor: 1 de las N opciones dicen «40 Reefer High»» (hasta aquí, «contenedor: …») y
  «lista de tipos de contenedor reefer: 1 de las N opciones dicen «Standard (40´)»».
- **Lo que no cambió:** lo que se escribe en la lista de tipos, la temperatura, el GenSet y todo lo demás de MAERSK;
  las otras navieras; los lectores. Nada para disfrazar el navegador. `test_candado` no cambió y pasa.

## El camino real, en un Chromium sin red

`sonda_reefer.py`: el `_mk_elegir_reefer` de este árbol y, de control, el de `fea432f`: el bloque «if es_reefer:» de su
`reservar_maersk`, tal cual está en ese commit, hasta el `try` que elige el tipo, corrido con `exec` en una copia de ese
programa (el código del motor, no una paráfrasis). Playwright de verdad, sobre una página local: el campo, al recibir
el foco, muestra a los 0,6 s una lista de `mc-option` con su raíz shadow, y a los 1,2 s agrega una opción más.

| Lista | Este encargo | El de antes |
|---|---|---|
| «Standard (20´)», «Standard (40')» y, tarde, «Standard (40´)» | «Standard (40´)»; la evidencia trae las 3 y sus raíces shadow | «Standard (40')», sin esperar la que llegó tarde |
| «Standard (20´)» y «High cube (45´)» | No pulsa: «hay 0 entre 2: …» | «Standard (20´)» |
| Dos «Standard (40´)» | No pulsa: «hay 2 entre 2: …» | La primera |

El control (el de antes elige «Standard (40')») aborta la sonda si no se da. `sonda_contenedor.py`, la del encargo 62,
sobre el ayudante que ahora comparten las dos listas, da lo mismo que en el 62.

## Pruebas, mutaciones, censo y suite

**Las pruebas nuevas (12):**
- `test_ayudantes.TestOtroContenedorMaersk` (4): la regla (mayúsculas, espacios, otros textos, uno que lo trae
  dentro, la celda vacía, el recorte del motivo y las otras navieras); el decorador corta sin tocar la página, con la
  línea en `log.txt` y en pantalla; sin nave o sin ruta, dicen eso; con el contenedor de las filas, pasa tal cual.
- `test_web.TestPanelCorridas.test_fila_de_maersk_con_otro_contenedor_no_abre_el_portal` y
  `test_consola.TestEjecutarReservas`, la misma: con una columna de contenedor en la planilla sintética, la fila que
  pide «20 DRY» queda NO ENVIADA en pantalla, en `log.txt` y en la planilla; sola, no abre el navegador; en ONE no
  cuenta; y en la consola, la celda vacía con la columna también corta.
- `test_clics.TestReeferMaersk` (6), con una página falsa que anota en orden la apertura del campo, cada captura y cada
  clic: la opción es la medida, con U+00B4; elige la única con el texto entero, con «Standard (40')» antes y otra que
  la trae dentro; sin una sola no pulsa nada; el campo o el clic que fallan cortan; por el decorador, NO ENVIADA con
  las dos capturas; y `reservar_maersk` la llama una vez, en `if es_reefer:`, entre el tipo de contenedor y la
  temperatura, antes de la guarda.

**Fotos que cambiaron a propósito:** `test_clics.TestSinClicACiegas.test_cada_reservador_que_corta_esta_decorado` (el
decorador nuevo de MAERSK); `test_evidencia.TestCadaReservadorLaDeja.test_solo_ahi` (la evidencia de las dos listas
sale de `_mk_elegir_unica`); la línea de `log.txt` del tipo de contenedor en `TestContenedorMaersk`; y la fila de
`TestSinSugerenciaNoSigue`, que trae ahora el contenedor que los dos lectores les dan a las filas (sin él, MAERSK
cortaba antes de la ruta).

**Las mutaciones:** 31 nuevas (`e63-*`), y cinco reescritas sobre el código nuevo (cuatro del encargo 62 y
`maersk-sin-decorador`). El chequeo de anclas de toda la lista (`mut_viejos.py`): 2.231 mutaciones, 785 pruebas, 0
problemas. Compilan las 45 que tocan lo que cambió: las 31 nuevas, las 11 del encargo 62 y las 3 que quitan un
decorador de MAERSK (la reescrita y las de la fila sin nave y sin ruta).

**El censo del área** (`alcance_censo.py`, `lanzar_censo_e63.py`): las 31 del encargo, las 11 del 62 (su ayudante es
ahora el de las dos listas) y la reescrita del decorador; las que caen a 15 líneas o menos de lo que cambió en
`AQUASHIELD.py`; y las que nombran una prueba cuyo camino cambió: los decoradores de MAERSK, la fila sin nave y la sin
ruta, las pruebas de los dos orquestadores que apartan filas, las dos listas, `test_registro` y `test_candado`. Dejé
fuera las 36 que nombran solo `test_solo_ahi` por otra evidencia: las que tocan las dos listas ya están adentro.
**238 mutaciones, 368 pares, 98 pruebas: los 368 muerden.** El control (la copia sin mutar) pasa, y la foto de los
4.881 originales, 0 cambios. De las 22:25 a las 23:03, con el equipo despierto.

**La suite:** `tests/correr.py` (con `correr_sin_tope.py`), sobre el árbol que se commitea: **785 pruebas, OK, en
1.114 s**, de las 23:03 a las 23:25, con 0 cambios en las 4.881 entradas fotografiadas de los originales. Sin
suspensiones: el único evento de energía en ese lapso es un Kernel-Power 105 (el cargador), a las 23:11.

## FRENA SI

**«Alguna reserva de MAERSK que llegó a la guarda habría quedado NO ENVIADA con estas reglas»: no salta con lo
medido.** Las 7 que llegaron a la guarda (las 5 del 21-09, la del 24-09 y la del 02-10):
- **Los ajustes reefer:** las 7 eligieron «Standard (40´)», con el mismo U+00B4 que la regla. Con la regla nueva la
  elegirían igual si era la única con ese texto en su lista: no está medido, porque ninguna lista se guardó. Si no lo
  era, la regla corta sin pulsar y con la evidencia.
- **El contenedor de la fila:** ni `log.txt` ni la evidencia lo guardan, y las planillas de esas fechas no están en el
  equipo. Lo que sí está: las 7 escribieron «40 Reefer» y siguieron por los ajustes reefer, así que su texto traía
  «40» y «REEF», «RF» o «RH»; y la única planilla del equipo no tiene la columna, con lo que los dos lectores dan «40
  HC REEFER». Que pidieran justo ese texto es lo más probable, no un hecho medido.

## Lo decides tú

1. **La celda vacía en la consola:** con una columna de contenedor y la celda vacía, el panel le da «40 HC REEFER» y la
   consola no: la fila queda NO ENVIADA («la fila no dice qué contenedor pide»). Que la consola haga lo mismo que el
   panel es un cambio en su lector, que solo cambias tú.
2. **Cómo se escribe el contenedor:** la regla acepta «40 HC REEFER» sin distinguir mayúsculas y con los espacios de a
   uno; «40HC REEFER», «40' HC REEFER» o «40 HC RF» quedan NO ENVIADA. Si las planillas van a traer otras formas del
   mismo contenedor, dime cuáles.
3. **El panel no marca la fila antes de correr:** la de MAERSK con otro contenedor queda NO ENVIADA al correr, no en la
   tabla antes (como sí la sin nave o sin ruta). Marcarla es un cambio chico en el panel.
4. **Código que ya no se alcanza:** con la regla, MAERSK siempre trae «40 HC REEFER», así que sus ramas sin reefer (la
   palabra «High» y el peso de 20.000 kg sin reefer) no corren nunca. Quitarlas es limpieza.

## El push

**No lo subo:** el repositorio es público (subir publica), y los lanzadores de los colegas traen código de GitHub. Sube
`main` con dos commits; el bloque va al final del mensaje de cierre. `estable` no cambia: la avanzas tú.

## Re-medir

Todo corre desde `scratchpad\e63`, en Git Bash, después de `source entorno_e63.sh`, con Python 3.13.

| Número | Comando |
|---|---|
| Lo que eligió MAERSK en los ajustes reefer, con sus caracteres, y si llegó a la guarda | `python medir_reefer.py` |
| El contenedor de las filas (con respaldos y `logs/`) | `python medir_planillas.py` |
| La regla nueva sobre las planillas, con los dos lectores | `python medir_regla.py` |
| El camino real de los ajustes reefer, con el control del código de antes | `python sonda_reefer.py` |
| El camino real del tipo de contenedor (encargo 62), sobre el ayudante común | `python sonda_contenedor.py` |
| Las pruebas nuevas | `cd tests; python -m unittest test_clics.TestReeferMaersk test_ayudantes.TestOtroContenedorMaersk` |
| Las anclas de las mutaciones | `python mut_viejos.py e63- e62- maersk-sin-decorador` |
| El censo del área | `python alcance_censo.py`; `python lanzar_censo_e63.py` (aparte; escribe `censo_e63.txt`) |

## NO retroceder

- **En MAERSK, las dos listas de contenedor se eligen por su texto entero, y solo si hay una:** nunca «la primera que
  trae…», nunca la primera de la lista.
- **Una fila de MAERSK con otro contenedor no entra al portal:** el programa no sabe reservar otro.
- **Las dos listas eligen con un solo ayudante,** `_mk_elegir_unica`: no una copia por lista.

## Defectos de instrumento que me cacé

1. **Mi vigilancia del censo lo dio por terminado al minuto:** buscaba el PID en la primera columna de `ps -W`, que es
   el número de Git Bash, y el de Windows es la cuarta (WINPID). Antes de creerle, miré los procesos: el censo seguía
   vivo. Lo corregí y lo probé en las dos direcciones (el censo vivo se ve; un PID que no existe, no) antes de volver
   a vigilar.
2. **Una sonda de las etiquetas de `log.txt` imprimió valores en mi propia salida:** para ver qué líneas trae un bloque
   de MAERSK, tomé el texto antes de los dos puntos, y en algunas líneas el valor va antes («Origen '…'», «nave '…'»).
   Salieron en la terminal de esta sesión, una vez, el nombre de una nave y nombres de ciudades de destino. No
   quedaron en ningún archivo ni en este informe. Desde ahí, cada sonda imprime solo textos que calzan con una forma
   fija (una opción del portal) o conteos.
3. **Mi primer mensaje para «ninguna fila pide ese contenedor» empezaba igual que el de la fila sin ruta,** y dos
   mutaciones viejas dejaron de encontrar su texto una sola vez. Lo vio el chequeo de anclas; cambié el mensaje.
4. **La herramienta Bash juntó los pares de barras invertidas de un parche:** un `\\n` llegó como salto de línea, y el
   parche no encontró su texto (no escribió nada: cada reemplazo afirma que su texto viejo aparece una vez). Lo
   escribí con Write, como dice el entorno de la máquina.
5. **El filtro de la vigilancia de la suite no dejaba pasar su línea de resultado** («SUITE: exit=0 · Ran …»): esperaba
   «Ran» al principio de la línea. Lo vi porque el latido contó una línea más; el aviso de fin trae igual las últimas
   líneas de la salida.

## Premisas del encargo que se refutaron

- Ninguna. «Las filas llegan con «40 HC REEFER»» vale para las planillas de este equipo, que no traen la columna; con
  la columna y la celda vacía, la consola da la celda vacía (va a «Lo decides tú»).

## Residual

| # | Lo que queda | Condición de reapertura |
|---|---|---|
| 1 | Si la lista de los ajustes reefer trae una sola «Standard (40´)» no está medido: la primera corrida lo dice, con su evidencia | La primera corrida de MAERSK |
| 2 | Qué contenedor decían las filas de las 7 reservas que llegaron a la guarda no está guardado | No se puede reabrir: las planillas de esas fechas no están |
| 3 | La celda vacía con la columna: la consola corta y el panel no | Si decides que la consola haga lo del panel |
| 4 | Otras formas de escribir el mismo contenedor quedan NO ENVIADA | Si una planilla las trae |
| 5 | El clic en la opción reefer y la apertura del campo no están probados en el portal | La primera corrida de MAERSK |
| 6 | Las ramas sin reefer de MAERSK ya no se alcanzan | Si decides quitarlas |
| 7 | Las revisiones que pide ECC no se lanzaron | Si las pides |

## Reglas de método (v20)

- **Aplicadas:** las 21 universales. En especial:
  - la unidad la fija el sujeto: cada fila de MAERSK, no cada corrida;
  - el control positivo que aborta, en las cuatro sondas;
  - se mide sobre el camino real: los dos orquestadores de verdad con una planilla sintética, Playwright de verdad
    sobre la lista, y el control es el código de antes corrido tal cual (no una paráfrasis), que sobrevive al cambio;
  - todo salto lleva su contador: 0 carpetas sin `log.txt`, 0 bloques sin la línea reefer, 0 planillas descartadas;
  - el negativo que muerde: cada prueba nueva con su mutación, y el censo del área;
  - fuente única: las dos listas con un solo ayudante;
  - frenar en lo que es tuyo: la celda vacía en la consola, otras formas del contenedor, la marca en el panel.
- **Las del módulo** (`CLAUDE.md`): `test_candado` no cambia; ningún clic nuevo; casos sintéticos; la sonda de
  secretos antes de cada commit; el correo noreply de autor y de committer; las planillas y `logs/` solo se leen, y
  este informe no trae ningún dato de ellas salvo textos de opciones del portal, tipos de contenedor y conteos.
- **El push:** el repositorio es público: no subo, entrego el bloque.
- **Pieza 8:** opcional; este informe es Markdown y no lo rendericé.

## Lo que dio en el repo

Dos commits en `main`, sin push (el push lo haces tú):

- `5574d1f` fix: MAERSK corta la fila que pide otro contenedor, y en los ajustes reefer elige la única opción
  «Standard (40´)» (`AQUASHIELD.py`, y en `tests/`: `test_ayudantes.py`, `test_clics.py`, `test_consola.py`,
  `test_evidencia.py`, `test_web.py` y `mutaciones.py`);
- el commit siguiente, docs: `CLAUDE.md`, `LEEME.md` y este informe.

Los dos llevan de autor y de committer el correo noreply del repo, y la sonda de secretos dio 0 antes de cada uno.
