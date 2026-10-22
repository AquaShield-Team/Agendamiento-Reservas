# Encargo 76 · HYUNDAI: el NEXT de «Booking Reference» se pulsaba antes de que cargara el formulario

**Fecha:** 2026-10-22 · **Método:** `metodo-ciclo` v36, en Modo autónomo (por omisión).

Base: `Agendamiento Reservas` @ `ab9819f` · árbol limpio. `origin/main` y `origin/estable` estaban en el mismo commit.

**Commits,** en `main` y sin push (el repo es público: el bloque lo lleva Marcelo): `8f61d7c`, el arreglo, su red y
`CLAUDE.md`, con lo de las dos revisiones; y el de este informe.

## Qué pasó

El 22-10, en el equipo de un colega, la reserva de HYUNDAI quedó REVISAR («no se abrió el paso Select Vessel»):

| Segundo | Lo que pasó |
|---|---|
| 350,6 | sesión iniciada |
| 357,8 | «esperando 6.0s (cargar Booking Step by Step) [sin señal]»: el formulario del paso 01 no apareció en 6 s |
| 357,9 | captura `hmm_f9_1_ref`: **la página sin el formulario**, solo la barra de pasos y el botón «NEXT - Select Vessel» |
| 358,0 | «NEXT ok (role) -> Select Vessel»: el clic salió, sobre esa página |
| 373,2 | «No avanzó a Select Vessel (no apareció #schOriginText)», tras 15 vueltas de 1 s |
| 373,3 | captura `hmm_f9_2x_sinpaso2`: **el formulario ya cargado** («Booking Input (NEW)»), en el paso 01, con su NEXT |

**La causa es de tiempo:** el formulario llegó después del clic. El NEXT se pulsó sobre una página que todavía no lo
tenía, y no avanzó; cuando el formulario apareció, nadie volvió a pulsar.

**No es otro formulario, ni un aviso del portal, ni otra cuenta** (las tres salidas del FRENA SI):
- **El formulario es el mismo:** la captura `hmm_f9_1_ref` del 15-10 de este equipo, con el formulario cargado, es
  igual a la `hmm_f9_2x_sinpaso2` del colega: el mismo título, los mismos campos, el mismo NEXT.
- **La cuenta es la misma:** las dos capturas muestran el mismo usuario en la cabecera del portal.
- **Ningún aviso:** la captura de página completa del 2x no muestra ninguna ventana ni mensaje del portal.

## PASO 0

- **El registro:** `CLAUDE.md` no decía nada del paso 01 de HYUNDAI. El código esperaba
  `#previousBkgNo, #referenceNo0` 6 s (`esperar_hasta`, que sigue sin fallar si no llega), pulsaba
  «NEXT - Select Vessel» una vez (`_hmm_realclick`) y miraba 15 veces, una por segundo, si se veía `#schOriginText`.
- **Re-medí contra HEAD (`ab9819f`):** el mismo código que corrió el colega (base del encargo).
- **Veredicto: CICLO.**

## Lo medido

**1. El paso 01 en este equipo** (`medir_paso1.py`, sobre los `log.txt` de `logs/`; control: el log del colega, por la
misma sonda, da su caso, «SIN SEÑAL» y «no-avanzo» a los 15,2 s):

| | Corridas | Mínimo | Máximo |
|---|---|---|---|
| Espera del formulario, con señal | 19 de 19 | 0,5 s | 4,1 s |
| Espera del formulario, «[sin señal]» | **0** | | |
| Del NEXT al paso 02 | 19 de 19 | 1,0 s | 1,5 s |
| No avanzó | **0** | | |

46 `log.txt` leídos, 19 esperas emparejadas, 0 descartadas; del 21-09 al 15-10. «[sin señal]» no se vio nunca en este
equipo. El paso 02 se mira una vez por segundo, así que «1,0 a 1,5 s» es lo que tardó en verse, con ese grano.

El 21-10, en el equipo del colega, el paso avanzó en 1,4 s: lo dice el encargo, no lo medí (ese log no está).

**2. Cómo se distingue el paso 01 del 02** (`estructura_paso.py`, sobre los HTML de HYUNDAI guardados en `logs/`;
control: las 11 listas de naves traen `#schOriginText`): **0 de 59** páginas guardadas de los pasos 02 a 05 traen
`#previousBkgNo` o `#referenceNo0`, y **0 de 59** traen un botón «NEXT - Select Vessel». No hay ningún HTML del paso
01: nunca se guardó (solo su captura, `hmm_f<fila>_1_ref.png`).

## El arreglo

- **El formulario se espera hasta 30 s** (`HMM_ESPERA_PASO1`; hasta ahora, 6): en este equipo llegó en 4,1 s como
  mucho, así que en lo normal no cambia nada (`esperar_hasta` vuelve apenas lo ve). Si no llega, pulsa el NEXT igual,
  como antes.
- **Si después del NEXT la página sigue en el paso 01 con su formulario a la vista,** deja la evidencia
  (`hmm_f<fila>_paso1`: la captura de la ventana y el HTML) y **vuelve a pulsar ese NEXT, una sola vez**
  (`_hmm_reintentar_paso2`):
  - «sigue en el paso 01» es: un campo del formulario (`HMM_PASO1`) se ve, después de las 15 vueltas sin
    `#schOriginText`;
  - el NEXT es el único botón a la vista con el nombre «NEXT - Select Vessel», buscado por su rol, como el primer clic
    (`_hmm_realclick`), y cada uno tomado (`element_handle`) antes de mirar si se ve: se pulsa el que se vio. Con 0 o
    más de uno a la vista, no pulsa nada y lo dice;
  - después del clic, otras 15 vueltas. Si tampoco llega, REVISAR, como antes. **El reintento pulsa una sola vez.**
- **Sin el formulario a la vista, no lo vuelve a pulsar:** pulsar sin él es justo lo que no avanzó el 22-10.
- **Si el paso 02 llegó** mientras guardaba la evidencia o buscaba el NEXT, no pulsa y sigue; **si el clic da un
  error**, pudo salir igual (una navegación lenta vence su plazo), y espera el paso 02 sin otro clic. Las dos, de las
  revisiones (abajo).
- `log.txt` lo dice: «sigue en «Booking Reference», con su formulario a la vista: busco su NEXT para pulsarlo otra
  vez, una sola vez», y «NEXT ok (role) -> Select Vessel, el clic del reintento» (o por qué no pulsó).
- Nada cambia antes ni después: la dirección de Booking Step by Step, la captura `_1_ref`, el primer clic, el
  REVISAR con `_2x_sinpaso2`, y todo desde el paso 02.

Con el arreglo, el caso del 22-10 no llega al segundo clic: la espera empezó en el segundo 351,8 (la línea del 357,8
dice que esperó 6,0 s), y a los 373,3 el formulario ya estaba, así que llegó a lo más 21,5 s después de empezar a
esperarlo; la espera de 30 s lo habría visto. El segundo clic es la red para lo que no se vio: el clic que sale justo
cuando el formulario se arma, o un formulario que tarda más de 30 s y llega antes de que terminen las 15 vueltas.

**Lo que cuesta:** nada en lo normal. Con un formulario que no llega, 30 s antes del NEXT en vez de 6; y con el segundo
clic, una evidencia y hasta 15 s más antes del REVISAR.

## La red

- **Nueve pruebas nuevas** en `test_clics.TestHyundai` (`test_el_paso1_*`), por el camino real: `reservar_hyundai`
  entero, con sus decoradores y su `esperar_hasta` de verdad, sobre `PaginaPaso1Hmm`, una página falsa con reloj (cada
  espera lo avanza). Su formulario aparece a los N s; un clic sin el formulario no avanza, como el 22-10; con él, avanza
  o no según el caso. La corrida sigue hasta el origen del paso 02, donde `_hmm_autocomplete` no elige: la fila queda NO
  ENVIADA ahí, y así se ve que llegó.
  - **El caso del 22-10** (el formulario a los 10 s): una espera de 29,6 s por `HMM_PASO1`, un clic, con el
    formulario, y llega. **Su control:** con la espera de antes y sin el segundo clic, la misma página da lo del 22-10:
    «[sin señal]», un clic sin el formulario y REVISAR.
  - **El primer clic que no avanza:** la evidencia `hmm_f9_paso1` (la ventana y su HTML), en ese orden antes del
    segundo clic, y llega.
  - **Los dos que no avanzan:** REVISAR, con su `_2x_sinpaso2`, y nunca un tercero.
  - **Sin el formulario** (no llega nunca): un clic, a los 30 s, y REVISAR, sin segundo clic ni evidencia.
  - **Con 0 o 2 NEXT a la vista:** la evidencia, «no volví a pulsar … hay N a la vista, no uno», y REVISAR.
  - **Lo de siempre:** un clic y el paso 02, sin evidencia.
  - **De las revisiones:** el paso 02 que llega mientras se guarda la evidencia, o mientras se busca el NEXT (sigue,
    sin otro clic); y el clic del reintento que da un error (espera el paso 02: llega, o REVISAR, sin un tercero).
  - En todas, cada botón que se busca es el NEXT por su rol, con su nombre; ningún clic va a una posición sin tomar el
    elemento; y no corre ningún otro JavaScript que el del HTML de la evidencia.
- `test_evidencia.test_solo_ahi` cuenta el llamador nuevo de la evidencia.
- **Catorce mutaciones** (bloque e76 de `tests/mutaciones.py`): la espera de antes; otra señal; sin el segundo clic; con
  un tercero; dándolo por bueno sin mirar si llegó; sin mirar el formulario; con cualquier cantidad de NEXT; sin el
  nombre del NEXT; sin la evidencia; sin mirar el paso 02; y, de las revisiones, sin mirar el paso 02 después de la
  evidencia, pulsando la posición, sin esperar después de un clic con error y sin mirar el paso 02 cuando no pulsa.
  **El censo: 14 mutaciones, 17 pares, los 17 muerden;** control sin mutar, verde; los originales, sin cambios (5.582
  entradas). Las dos primeras versiones del censo, en «Defectos».

## Revisión de código

`code-reviewer`, en un clon sin remoto dentro de la carpeta del encargo, con el commit a revisar (su worktree de
arranque quedó vacío). Corrió 27 + 98 + 491 pruebas sobre el clon y el censo de las mutaciones e76, todo verde.
**Veredicto: APROBAR**, con cuatro LOW:

| Hallazgo | Qué hice |
|---|---|
| **L1.** Si el paso 02 llega mientras se guarda la evidencia (1 a 4 s), el segundo clic no ve ningún NEXT y la fila queda REVISAR con la página ya en el paso 02 (lo comprobó con una página falsa) | **Arreglado:** después de la evidencia mira si el paso 02 llegó, y entonces no pulsa y sigue. Su prueba (`test_el_paso1_no_vuelve_a_pulsar_si_el_paso2_llego`) y su mutación |
| **L2.** Con la página sin el formulario, cada fila paga hasta 24 s más que antes antes del mismo REVISAR | Declarado arriba («Lo que cuesta») y en el RESIDUAL: 30 es una hipótesis |
| **L3.** La espera mira solo el primer campo de la lista (`wait_for_selector`), y el segundo clic cuenta cualquiera de los dos | Al RESIDUAL: en las 19 corridas la señal llegó; el segundo clic cubre el caso |
| **L4.** Nada distinguía pulsar el elemento tomado (`element_handle`) de pulsar la posición, y su mutación sobrevivía; la de «cualquier cantidad de NEXT» muere solo por el texto, porque el desempaquetado `(boton,) = vistos` tampoco deja pulsar; el mensaje decía «vuelvo a pulsar» antes de saber si había un NEXT | **Arreglado:** la página falsa no deja pulsar una posición, con su mutación (`e76-paso1-clic-por-su-posicion`); el mensaje dice ahora «busco su NEXT para pulsarlo otra vez». La doble guarda del desempaquetado queda, declarada |

Con eso, **12 mutaciones y 15 pares, los 15 muerden** (control verde; originales sin cambios), y 63 pruebas de HYUNDAI,
`test_candado`, la foto de clics genéricos, los cortes y la evidencia, OK.

## Revisión de seguridad

`security-reviewer`, en el mismo clon, con el commit que ya traía lo de la revisión de código (su worktree de arranque
quedó vacío). Midió en un Chromium local, sin red, cómo calza `get_by_role` con 21 formas de botón, y corrió las
funciones reales del clon sobre páginas inventadas. **Veredicto: APROBAR CON CAMBIOS**, ninguno de seguridad: «El
reintento no puede avanzar con datos que no son de la fila ni pulsar otro botón que el pedido, salvo que el propio
portal lo disfrace. […] Nada llega a la guarda por esta vía.»

| Hallazgo | Qué hice |
|---|---|
| **MEDIUM-1.** Si el clic del reintento sale pero Playwright da un error (una navegación lenta vence su plazo de 4,5 s; lo midió con una de 6 s), devolvía False sin esperar, y la fila quedaba REVISAR con el paso 02 llegando después | **Arreglado:** si el clic da un error, espera el paso 02 como después de un clic, sin otro, y `log.txt` lo dice. Su prueba (`test_el_paso1_si_el_clic_del_reintento_da_error_espera_el_paso2`, que llega y que no) y su mutación |
| **LOW-1.** Si el paso 02 llega mientras busca el NEXT, ve 0 y queda REVISAR | **Arreglado:** cuando el reintento no pulsa (0 o más de un NEXT, o la búsqueda falla), mira si el paso 02 llegó, y entonces sigue (`_hmm_sin_reintento`). Su prueba y su mutación |
| **LOW-2.** `exact=False` calza por subcadena y sin mayúsculas: un único botón a la vista con ese nombre dentro de otro («Go back (NEXT - Select Vessel)»), o un `div role=button`, se pulsaría; también los de `opacity:0` o `disabled` cuentan como a la vista | Al RESIDUAL: es el mismo criterio que el primer clic, solo el portal puede poner ese botón, y sin un HTML del paso 01 no se puede medir su nombre exacto. La evidencia nueva lo trae |
| **LOW-3.** «Nunca un tercer clic» vale para el reintento: el primer clic (`_hmm_realclick`, sin cambios) tiene sus respaldos por texto y por JavaScript | **Arreglado el texto:** `log.txt` dice «el clic del reintento» (no «el segundo y último»), y `CLAUDE.md`, que el reintento pulsa una sola vez y que el primer clic es el de siempre |
| **LOW-4.** Un paso 02 lento que llega después de las 15 vueltas recibe dos clics (lo midió con uno a los 17 s) | Al RESIDUAL: en el paso 01, que no envía nada, es inocuo; si el portal reprocesa el paso 02, no se pudo medir |
| **LOW-5.** El elemento se tomaba después de mirar cuál se veía, por su posición | **Arreglado:** cada NEXT se toma (`element_handle`) antes de mirar si se ve, y se pulsa el tomado. La mutación de pulsar la posición sigue mordiendo |
| INFO: la evidencia nueva guarda lo que guardan las otras de HYUNDAI (el marcado, la cabecera de la sesión; no el valor de un campo, ni usuario ni clave: el programa no los escribe en este paso); los tres `except` nuevos son `Exception` y no se tragan un corte; 0 datos reales en lo agregado, con la guarda del repo (control: 1) | Nada |

Con eso, **14 mutaciones y 17 pares, los 17 muerden** (control verde; originales sin cambios), y las 30 pruebas de
`TestHyundai`, OK.

## Las suites

- **Antes de `8f61d7c`, sobre su árbol:** la suite completa, **867 pruebas, OK** en 887 s, y la foto de los
  originales, sin cambios (5.581 entradas). Con `suite_sin_tope.py`, que corre `tests/correr.py` tal cual con el tope
  de la corrida de unittest en 3.600 s (con 1.200, en el encargo 73 una corrida con el equipo cargado se cortó sin
  resultado). El equipo, despierto (pedido a la app); no es una medición de tiempo.
- La sonda de secretos (`--dry-run` y sobre el índice), el barrido de valores reales sobre lo agregado y sobre el
  mensaje del commit (control: ok; 0 líneas), y la guarda del hook pre-commit: los cuatro en 0.
- **Este informe va en un commit aparte.** De las pruebas, solo la guarda de datos reales lo lee (lo versionado), y la
  corre el hook sobre el índice de ese commit; ninguna otra lee los `CICLO-*.md`.

## Decisiones que tomé solo

| Decisión | Por qué |
|---|---|
| Esperar el formulario hasta 30 s (hipótesis) | 7 veces lo más largo medido aquí (4,1 s), y el 22-10 llegó a lo más a los 21,5 s; en lo normal no cuesta nada |
| Si el formulario no llega, pulsar el NEXT igual, como antes | Es lo que hacía el programa; no pulsarlo cambiaría el camino que ya existe sin un caso medido que lo pida |
| El segundo clic solo con un campo del formulario a la vista | Pulsar sin el formulario es lo que no avanzó el 22-10; así no se repite lo mismo |
| El segundo clic: el único NEXT a la vista, por su rol y su nombre, tomado con `element_handle` antes de mirar si se ve | Es «ese NEXT» del encargo: el mismo botón que busca el primer clic, sin elegir entre varios (LOW-5 de seguridad) |
| La evidencia `hmm_f<fila>_paso1` antes del segundo clic | Es el primer HTML del paso 01: si el segundo clic tampoco basta, con él se mide la página |
| Si el paso 02 llegó mientras guardaba la evidencia o buscaba el NEXT, seguir sin pulsar | L1 de código y LOW-1 de seguridad: si no, un falso REVISAR con la página ya en el paso 02 |
| Si el clic del reintento da un error, esperar el paso 02 sin otro clic | MEDIUM-1 de seguridad: el clic pudo salir (una navegación lenta vence el plazo); esperar no agrega ningún clic |
| `exact=False` y el primer clic, como estaban | El mismo criterio que ya tenía el primer clic; acotarlos sin el HTML del paso 01 sería a ciegas (LOW-2 y LOW-3, al RESIDUAL) |
| Las constantes (`HMM_PASO1`, `HMM_NEXT_PASO1`, `HMM_ESPERA_PASO1`, `HMM_VUELTAS_PASO2`) fuera de `reservar_hyundai` | Una sola fuente para el código y sus pruebas; `test_candado` no cambió, y lo que fotografía antes de la guarda sigue igual |

## Defectos de instrumento que me cacé

1. **Dos mutaciones mías no compilaban:** dejaban un `try:` sin cuerpo. El censo lo dijo («la mutación deja
   AQUASHIELD.py sin compilar») y las reescribí con un `pass`; en la segunda corrida, las 10 mordían.
2. **Volví a escribir barras invertidas por Bash** (el patrón de la fecha en la sonda de tiempos), contra la fila de
   «Entorno». Esta vez el resultado quedó bien, pero por suerte: el reemplazo del script que lo hizo se armó con
   barras que la herramienta juntó. Es la cuarta vez en estos encargos.
3. **La sonda de tiempos no leía la fecha de la carpeta** en su primera versión (buscaba AAAA-MM-DD y la carpeta trae
   AAAAMMDD): los tiempos estaban bien, la fecha salía «?». La arreglé antes de usar el resultado.
4. **Le afirmé al revisor algo que el código no hacía:** que `element_handle` evitaba pulsar otro botón si la lista
   cambiaba. Lo tomaba después de elegir por posición, y ninguna prueba lo distinguía (L4 de código y LOW-5 de
   seguridad). Ahora toma cada elemento antes de mirar si se ve, y la página falsa no deja pulsar una posición.
5. **Una prueba con el nombre de una clase que no existe** (`TestDejaLaEvidencia`) en la primera corrida: el error lo
   dijo, y la clase es `TestCadaReservadorLaDeja`.

## Premisas que se refutaron

1. **La evidencia no estaba en la carpeta del encargo** (`…\Escritorio\evidencia-colega-22-10` no existe): estaba en
   Descargas, con el log como «log 1.txt». La encontré recorriendo el perfil (1.055.986 archivos, 0 sin leer; control:
   las 288 capturas `hmm_f…` de `logs/`).
2. **Las capturas dicen lo contrario de lo que dice el encargo:** en `hmm_f9_1_ref` el formulario **no** está (solo la
   barra de pasos y el NEXT), y en `hmm_f9_2x_sinpaso2` **sí** está, cargado. No «desapareció»: llegó tarde. Es lo que
   confirma la hipótesis de tiempo.

La hipótesis del encargo («el clic llegó antes de que la página estuviera lista») se confirmó.

## RESIDUAL

| Qué | Condición de reapertura |
|---|---|
| **Por qué el formulario tardó en el equipo del colega** (red, portal, el equipo) | No se midió: si vuelve a pasar, `log.txt` dice cuánto esperó y si hizo falta el segundo clic, y `hmm_f<fila>_paso1` trae el HTML |
| **Los 30 s son una hipótesis** (L2): con la página sin el formulario, cada fila de HYUNDAI paga hasta 24 s más antes del mismo REVISAR | Si una corrida muestra el formulario después de 30 s, o el costo molesta |
| **La espera mira solo el primer campo de la lista** (L3, `wait_for_selector`) | Si una cuenta muestra el primero oculto: el segundo clic lo cubre, pero la espera tardaría sus 30 s |
| **El primer clic sigue siendo el de antes** (`_hmm_realclick`, con su respaldo por texto y por JavaScript; LOW-3 de seguridad) | Fuera del encargo; en las 20 corridas medidas pulsó por su rol |
| **El NEXT se busca por subcadena** (`exact=False`, LOW-2 de seguridad): un único botón a la vista cuyo nombre lo contenga se pulsaría | Cuando haya un `hmm_f<fila>_paso1.html`: con él se mide el nombre exacto y se puede acotar (`exact=True`, o dentro del contenedor del paso 01) |
| **Un paso 02 lento que llega después de las 15 vueltas recibe dos clics** (LOW-4 de seguridad); en el paso 01, que no envía nada, es inocuo | Si se ve que el portal reprocesa el paso 02 con el segundo clic |
| **El desempaquetado `(boton,) = vistos` también impide pulsar con 0 o más de uno:** la mutación del conteo muere por su mensaje o por la excepción, no por un clic | Ninguna: es una segunda guarda |
| **COSCO en el equipo del colega no tiene `opencv`** («No module named 'cv2'» en las tres vueltas del puzzle; el operador lo resolvió a mano): los `.bat` no lo instalan, y el import es perezoso, como dice `CLAUDE.md` | Fuera del encargo: si se quiere el puzzle automático allá, es otro encargo |
| **Dato lateral:** en el mismo log, MAERSK eligió el destino con paréntesis de la fila, con la regla de los encargos 73 a 75 | Ninguna |

## Re-medir

1. `python <e76>/medir_paso1.py` (las esperas del paso 01 en `logs/`); con la ruta de un `log.txt`, el de ese log (el
   del colega: «SIN SEÑAL» y «no-avanzo» a los 15,2 s).
2. `python <e76>/estructura_paso.py` (los HTML de HYUNDAI de `logs/`: campos del paso 01 y su NEXT en los pasos 02 a
   05).
3. `python <e76>/buscar_evidencia.py <raíces…> "<repo>\logs"` (la evidencia del colega; el último argumento es el
   control).
4. Las pruebas, desde `tests/`: `python -m unittest test_clics.TestHyundai test_evidencia.TestCadaReservadorLaDeja`; y
   `python tests/correr.py --mutaciones --filtro e76`.

`<e76>` es la carpeta del encargo en el scratchpad de la sesión: no se versiona, porque las sondas leen `logs/` y la
evidencia del colega, que son datos reales.

## NO retroceder

- **El NEXT de «Booking Reference» no se pulsa sin esperar el formulario** el tiempo de `HMM_ESPERA_PASO1`: con 6 s,
  el 22-10 se pulsó sin él y la fila quedó REVISAR.
- **El segundo clic, solo con el formulario a la vista, sobre el único NEXT y una sola vez:** pulsar sin el formulario
  no avanza, y un clic de más en un asistente de reservas no se hace a ciegas.
- **Antes de dar el paso por fallado, mirar si el paso 02 llegó,** y después de un clic con error, esperarlo: si no,
  un falso REVISAR con la página ya en el paso 02.

## Reglas de método aplicadas

`metodo-ciclo` v36: re-medir contra HEAD, control positivo que aborta (las tres sondas), la unidad de la medición (la
espera de cada reserva, no la corrida), se mide sobre el camino real (`reservar_hyundai` entero sobre la página falsa,
con su `esperar_hasta` de verdad), el negativo tiene que morder (el censo e76), el cambio y su guardián en la misma
operación, todas las suites antes del commit, los revisores en un clon sin remoto (de a uno), las premisas refutadas, el
RESIDUAL, la base, el push (repo público: se entrega el bloque) y el cierre sin esperas vivas. Las del módulo: las de
`CLAUDE.md` (`test_candado` sin cambios, ningún dato real en lo versionado, la sonda de secretos y la guarda antes de
cada commit). No chocaron.
