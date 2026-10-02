# CICLO · La cola de siete ítems decididos

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-25 · **Método:** skill `metodo-ciclo` v13 ·
**Base:** `cc6e2f2` (último de código: `86d6e63`) · **Commits** (locales, sin push; el repo no tiene remoto): uno por
ítem con código, `50e3f04` (ítem 3), `fc7de54` (ítem 4), `0e15b8a` (ítem 5), `0af2d5b` (ítem 6) y `6339e38` (ítem 7),
y el de este informe. Los ítems 1 y 2 frenaron y no tienen commit.

> Sin datos reales. `logs/`, la planilla y `config.json` se midieron en solo lectura, con sondas que imprimen
> conteos, etiquetas de interfaz, formas enmascaradas y hashes. Nunca salen naves, puertos, fechas, contratos ni el
> nombre del operador.

## Los siete ítems

| # | Ítem | Resultado | Commit | Qué se midió, o qué falta |
|---|---|---|---|---|
| 1 | La nave calza solo con todas sus palabras, en las seis | **FRENO** | — | Exigirlo deja sin calzar las 5 reservas EMITIDA de HYUNDAI del 21, que hoy sí calzan: sus tarjetas traen la primera palabra de la nave de la planilla y otra segunda palabra |
| 2 | Desempate por tránsito y después por transbordos | **FRENO** | — | El tránsito se lee en las cuatro. Los transbordos no se pueden contar en ONE (solo dice «Direct» o «Transshipment») ni en MAERSK (no los muestra) |
| 3 | HYUNDAI y CMA guardan su lista de salidas al leerla | Hecho | `50e3f04` | `hmm_f<fila>_naves`, y `cma_f<fila>_rutas` (y `_rutas_mas`), con la captura de la ventana y el HTML |
| 4 | MAERSK busca desde hoy; si no puede, desde mañana y avisa | **FRENO**: queda mañana, con el aviso | `fc7de54` | Ninguno de los 125 HTML guardados trae el campo de fecha de MAERSK: sin el portal no se sabe si acepta hoy |
| 5 | La regla cuenta desde el día de carga, o desde hoy | Hecho | `0e15b8a` | Confirma la interpretación. ONE era la única que contaba siempre desde hoy; ahora usa `_desde`, como las demás |
| 6 | La sonda bloquea el nombre o el apellido del operador | Hecho | `0af2d5b` | 0 en el staging. En el historial, los 72 commits hasta `9710ae2` lo traen y los posteriores no |
| 7 | El panel de escritorio escribe `config.json` de forma atómica | Hecho | `6339e38` | Los dos paneles usan `_escribir_config`, con el reintento de `_reemplazar` |

## Ítem 1 · FRENO: la nave con todas sus palabras

**Cómo calza hoy cada naviera** (medido en el código de `6339e38`):

| Naviera | Dónde | Regla de hoy | ¿Todas las palabras? |
|---|---|---|---|
| MSC | `reservar_msc` | Todas las palabras de la nave, en cualquier orden | Sí |
| MAERSK | `_JS_MK_SALIDAS` | Todas, en orden | Sí |
| COSCO | `reservar_cosco` | Todas las de la nave y el viaje. Si ninguna fila calza, todas las de la nave (otro viaje del mismo barco) | Sí, las de la nave |
| CMA | `_cma_seleccionar_itinerario` | Todas, o todas menos los prefijos de naviera («MSC», «CMA», «CGM», «HMM», «ONE», «COSCO», «MV»). Toma la primera ruta que calza | Casi: sin los prefijos |
| ONE | `_JS_ONE_TARJETAS_NAVE` | La nave entera, o sin su última palabra, o la última palabra sola si tiene 4 letras o más. La última se toma por viaje si tiene de 3 a 10 letras o dígitos | No (hallazgo 2 del informe anterior) |
| HYUNDAI | `_JS_HMM_INDICE_NAVE` | Todas, **o solo la primera**; pulsa la primera tarjeta que calza | No (hallazgo 1) |

**El freno, medido en `logs/`:**
- 9 carpetas de corrida, las 9 con `log.txt`; 0 descartadas. Solo la del 21 tiene reservas EMITIDA: 20, de ONE (5),
  COSCO (5), HYUNDAI (5) y MAERSK (5).
- **COSCO y MAERSK:** el texto que el log guardó de cada elección trae todas las palabras de la nave de su fila. La
  regla no les cambia nada.
- **HYUNDAI:** el log no trae la nave de su fila, así que se comparó con la planilla actual del panel:
  - las 5 tarjetas elegidas traen la primera palabra de la nave de la planilla y, en vez de la segunda, otra palabra;
  - es la misma otra palabra (comparada por hash) en las 4 corridas que eligieron una tarjeta de HYUNDAI: el 21, el 24
    y las dos del 25;
  - las dos copias de la planilla son del 23 en adelante y traen la misma nave en las filas 25 a 29.

  Con todas las palabras, esas 5 tarjetas dejan de calzar con la nave que la planilla trae hoy, y hoy sí calzan.
- **ONE:** el texto que el log guardó de su elección no trae ninguna palabra de la nave de la fila. No se puede decir
  si sus 5 reservas calzarían.

**Lo que decides tú:** revisa en el portal de HMM qué nave llevan las 5 reservas del 21.
- Si llevan la nave con la otra segunda palabra, eran de otro buque, y exigir todas las palabras es lo correcto.
- Si la planilla del 21 traía esa otra nave, las reservas estaban bien y la regla tampoco las habría roto.

En los dos casos, el ítem se implementa sin cambiar el plan: el camino de «nave no encontrada» de cada naviera ya existe
y devuelve REVISAR con las naves ofrecidas. El freno vale para el ítem entero, así que no se tocó ninguna naviera.

## Ítem 2 · FRENO: el desempate

Medido en las listas guardadas de la corrida del 25 a las 13:47:

| Naviera | Tarjetas | Tiempo de tránsito | Transbordos |
|---|---|---|---|
| COSCO | 4 | El número y «Days», en textos separados, en las 4 | Las naves de «Vessel / Voyage»: 2 por tarjeta. Si cada nave es un tramo, 1 transbordo |
| ONE | 32 | «NN day(s)» en las 32 | «Direct» (8) o «Transshipment» (24), sin cuántos |
| MSC | 27 | «ETD», «ETA» y los días de tránsito, en las 27 | «Route» dice «Transhipment» en las 27, y un bloque «Transhipment via» con 4 fechas y un puerto |
| MAERSK | 5 | «Transit time», «NN days N hours» | No los muestra: solo un enlace a los detalles de la ruta, que habría que abrir |

- En ONE, «Transshipment» no dice si son uno o varios. En MAERSK, leerlos pide un clic nuevo.
- El desempate va en el ayudante compartido, así que el freno vale para las cuatro. No se tocó `_proxima_salida`.

**Cuánto resolvería el tránsito solo**, en los empates medidos (misma nave y mismo día de salida; la nave, por hash):
- **COSCO:** 2 empates de 2 tarjetas. El menor tránsito deja una sola en los 2.
- **ONE:** 8 empates de 4 tarjetas. El menor tránsito deja una sola en 6. En los otros 2 empata también el tránsito.
- MSC y MAERSK: 0 empates (MSC, 27 días distintos; MAERSK, 1 sola salida con «Book»).

**Lo que decides tú**, con lo medido:
- **(a)** Desempatar solo por el menor tránsito y, si también empata, NO ENVIADA con la lista. Se puede implementar con lo
  que muestran las cuatro.
- **(b)** Contar como 1 transbordo el «Transshipment» de ONE y 0 el «Direct».
- **(c)** En MAERSK, abrir los detalles de la ruta: un clic nuevo antes de la guarda.

## Ítem 3 · Hecho en `50e3f04`: la evidencia de las listas de HYUNDAI y CMA

- **HYUNDAI:** tras esperar la lista de naves y antes de leerla, deja `hmm_f<fila>_naves`.
- **CMA:** antes de cada lectura de «Route choices», deja `cma_f<fila>_rutas`. Si pidió «Mostrar más viajes», deja
  también `cma_f<fila>_rutas_mas`.
- Las dos, con el mecanismo de siempre: la captura de la ventana y el HTML, sin clics, teclas, esperas ni navegación
  nuevas. Si la evidencia falla, se avisa y la reserva sigue.
- La regla de la próxima salida no se les aplica todavía: espera ese HTML.

## Ítem 4 · FRENO, con el aviso: MAERSK busca desde mañana

- Se revisaron los 125 HTML guardados en `logs/` y junto al programa. Ninguno trae el campo de fecha de MAERSK, ni
  «Select tomorrow», ni su calendario: el formulario de la reserva nunca se guardó en HTML.
- Como pide el encargo, queda la fecha de mañana, y `_mk_fecha` ahora avisa en pantalla y en `log.txt`: «busco las
  salidas desde mañana, no desde hoy: todavía no sé si el portal acepta la fecha de hoy».
- Con día de carga, lo escribe como antes, sin aviso; si el portal no lo acepta, avisa como antes.

## Ítem 5 · Hecho en `0e15b8a`: desde el día de carga, o desde hoy

- Confirma lo que interpreté en `CICLO-proxima-salida.md`: `_desde` da el día de carga si la fila lo trae y es posterior
  a hoy, y si no, hoy.
- ONE era la excepción: contaba siempre desde hoy. Ahora usa `_desde(reserva)`, y avisa con `_avisar_dia_carga`, como
  las demás, la celda que no se entiende como fecha.
- No cambia qué columnas ni qué filas lee el lector: el día de carga ya lo leía `_fecha_planilla`.

## Ítem 6 · Hecho en `0af2d5b`: la sonda bloquea el nombre del operador

- **Los términos** salen de `config.json`: cada palabra de 4 letras o más de la clave del operador, de su descripción y
  del `nombre_en_pantalla` de COSCO. La plantilla no cuenta (clave `usuario<n>`, descripción «rellenar»). Hoy dan 2
  términos, y 0 palabras cortas quedan sin buscar.
- **La búsqueda:** cada término por separado, sin mayúsculas ni tildes, en UTF-8 y UTF-16, en la ruta y en el
  contenido. Antes buscaba la descripción entera, así que el apellido solo no aparecía.
- **Bloquea** en el staging, en `--dry-run` y en los negativos. En `--almacen` solo informa: el historial hasta
  `9710ae2` trae el nombre y no se reescribió.
- **Control C2 que aborta con 2:** sin términos, o si la búsqueda no los encuentra en `config.json`.
- **Modo nuevo `--negativo-nombre`:** corrido a mano, 2 entradas falsas y salida 1.
- **La salida nunca imprime el nombre:** una ruta que lo trae sale como «(ruta con el nombre del operador)».
- `tests/correr.py` crea la subcarpeta del archivo mutado, para que el censo pueda mutar `tests/sonda_secretos.py`.

Medido con la búsqueda nueva:
- el staging de `0e15b8a`, `0af2d5b` y `6339e38`: 0 entradas con el nombre;
- el almacén: 94 blobs con el nombre, todos del historial;
- los 82 commits de `main`: los 72 hasta `9710ae2` inclusive lo traen en 8 o 9 archivos, y los 10 posteriores en ninguno.

## Ítem 7 · Hecho en `6339e38`: config.json atómico en los dos paneles

- `_escribir_config(cfg, ruta)` escribe a `.json.tmp` y después `_reemplazar`, que reintenta hasta 20 veces si Windows
  niega el reemplazo. El formato es el de antes: UTF-8 sin escapar, con sangría de 2.
- Lo usan `/api/credenciales`, que lo hacía en línea, y `guardar()` del panel de escritorio, que abría `config.json` con
  `open(w)`. `open(w)` trunca al abrir: un fallo a mitad dejaba el archivo vacío.
- Si el reemplazo sigue negado, el panel de escritorio muestra «No pude guardar», como antes, y `config.json` queda
  como estaba.

## Expectativas que cambiaron (antes → ahora)

| Commit | Prueba | Antes | Ahora |
|---|---|---|---|
| Ítem 3 | `test_evidencia.TestCadaReservadorLaDeja.test_solo_ahi` | `reservar_hyundai` la deja 2 veces; `_cma_seleccionar_itinerario`, 0 | 3 y 1 |
| Ítem 4 | `test_ayudantes.TestFechas.test_maersk_avisa_solo_si_no_pudo_escribir_la_fecha` | Sin día de carga, o ilegible: sin aviso | Pasa a `test_maersk_avisa_cuando_no_busca_desde_hoy`: avisa que busca desde mañana |
| Ítem 5 | `test_clics.TestOne.test_reservar_one_elige_la_proxima_salida` | `desde = datetime.date.today()` | `desde = _desde(reserva)` |
| Ítem 5 | `test_ayudantes.TestFechas.test_cada_naviera_que_usa_la_fecha_avisa_y_la_lee_con_el_mismo_lector` | 5 navieras llaman a `_avisar_dia_carga` | 6: se suma `reservar_one` |

- Los ítems 6 y 7 no cambian ninguna expectativa: solo suman pruebas.
- **`test_candado` no cambió**, ni ninguna pieza de la guarda y el envío. Medido con `ast` entre `cc6e2f2` y `6339e38`:
  cambiaron 8 piezas de nivel superior de `AQUASHIELD.py`:
  - `_cma_seleccionar_itinerario`, `_desde`, `_escribir_config`, `_mk_fecha`, `lanzar_panel`, `lanzar_web`,
    `reservar_hyundai` y `reservar_one`;
  - ninguna del lector de la planilla;
  - ninguna de la guarda (`es_modo_emision`, `_resultado_envio`, `_pulsar_boton`, las evidencias, `_sin_clic_a_ciegas`).
- La foto de clics genéricos (`test_clics`) no cambió: no hay clics nuevos.

**La red, por commit:**

| Commit | Pruebas | Mutaciones | Pares |
|---|---|---|---|
| `cc6e2f2` (base) | 301 | 640 | 768 |
| `50e3f04` (ítem 3) | 306 | 646 | 778 |
| `fc7de54` (ítem 4) | 306 | 647 | 779 |
| `0e15b8a` (ítem 5) | 306 | 648 | 780 |
| `0af2d5b` (ítem 6) | 314 | 663 | 803 |
| `6339e38` (ítem 7) | 317 | 667 | 811 |

- Mutaciones puestas al día porque su texto viejo cambió: 2 de MAERSK (ítem 4), 1 de ONE (ítem 5) y 1 del reemplazo de
  credenciales (ítem 7). Ninguna borrada.
- Mutaciones nuevas sobre otro archivo que `AQUASHIELD.py`: las 15 de la sonda, sobre `tests/sonda_secretos.py`.

## Veredicto por naviera: ¿lista para una emisión real de prueba?

| Naviera | Veredicto | Qué le falta |
|---|---|---|
| **MSC** | **Casi lista** | Lo mismo que antes: una corrida con candado cerrado con la búsqueda desde hoy (`8927e1f`) para ver que elige la próxima salida en vivo. Calza la nave con todas sus palabras y tiene forma medida de confirmación, así que puede llegar a EMITIDA |
| **CMA** | No | Que «Validar ruta» responda, y la regla de la próxima salida sobre «Route choices», cuyo HTML ahora se guarda. Toma la primera ruta que calza y acepta la nave sin sus prefijos. Sin forma medida, tras el envío queda en ENVIADA – REVISAR EN PORTAL |
| **HYUNDAI** | **No** | Que la nave calce con todas sus palabras: FRENO hasta que revises en el portal las 5 reservas del 21. Después, la regla sobre su lista de naves, que ahora se guarda |
| **COSCO** | No | Tu decisión del desempate: con el menor tránsito solo, sus 2 empates medidos se resuelven. Sin forma medida, nunca llega a EMITIDA |
| **ONE** | No | Una fila cuya nave esté en la búsqueda; tu decisión del desempate (el tránsito resuelve 6 de sus 8 empates); y que calce con la nave entera (ítem 1) |
| **MAERSK** | No | Una fila cuya nave tenga una salida con «Book», para llegar a la revisión y medir la casilla de términos (FRENO); y saber si el portal acepta la fecha de hoy: por ahora busca desde mañana y lo avisa |

## Cómo elegir las filas para la próxima prueba con candado cerrado

La corrida sirve si cada naviera llega lo más lejos posible y deja la evidencia que falta. Una fila por naviera en
CONSOLIDADO, como la del 25, con el lanzador normal, nunca el de emisión. La planilla no cambia: sin día de carga,
todas cuentan desde hoy, y MAERSK desde mañana.

**Para todas:** elige la nave en el portal el mismo día de la corrida, en la ruta de la fila (el mismo origen y
destino). Escríbela con todas las palabras con que el portal la muestra en su lista.

| Naviera | Qué fila elegir | Qué deja para medir |
|---|---|---|
| MSC | Cualquier nave de su lista para esa ruta. Es la candidata para la primera emisión real de prueba | Que la regla elige la próxima salida desde hoy y llega a Summary |
| MAERSK | Una nave cuya salida traiga «Book», con el plazo de ingreso («Gate-in deadline») vigente. El 25, las 3 salidas de mañana ya no lo traían y la de 9 días sí | El HTML de la revisión, para la casilla de términos (`mk_f<fila>_guarda`) |
| HYUNDAI | Mientras no decidas el ítem 1, una nave cuya primera palabra no traiga ninguna otra nave de la lista: así la regla de hoy y la de todas las palabras eligen la misma tarjeta | `hmm_f<fila>_naves`, para la regla de la próxima salida |
| CMA | Cualquier nave con ruta ese día | `cma_f<fila>_rutas`, y si «Validar ruta» responde |
| COSCO | Si puedes, una nave con un solo itinerario en su próxima salida. Si trae dos, como las del 25, queda NO ENVIADA con la lista | `cosco_f<fila>_itinerarios`, con el tránsito de cada uno para el desempate |
| ONE | Una nave que esté entre las tarjetas de la búsqueda, escrita como en la tarjeta. Si su día trae 4 tarjetas, como el 25, queda NO ENVIADA por empate | `one_f<fila>_detenida`, con el tránsito y «Direct» o «Transshipment» de cada tarjeta |

**Después de la corrida, lo primero:** que ninguna fila quedó en EMITIDA ni en ENVIADA, y que no hay archivos
`_confirmado`. Después, los HTML nuevos: `hmm_f*_naves`, `cma_f*_rutas` y la revisión de MAERSK, si llegó.

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\correr.py --mutaciones --filtro hmm-lista
python tests\correr.py --mutaciones --filtro cma-rutas
python tests\correr.py --mutaciones --filtro mk-
python tests\correr.py --mutaciones --filtro one-
python tests\correr.py --mutaciones --filtro sonda-
python tests\correr.py --mutaciones --filtro config-
python tests\correr.py --todo
python tests\sonda_secretos.py --negativo-nombre
python tests\sonda_secretos.py --almacen
```

- `--negativo-nombre` tiene que dar 1. `--almacen` da 0 e informa los blobs del historial con el nombre.

Las sondas son de solo lectura y viven fuera del repo. Cada una aborta si su control sintético no da lo esperado:
- **Las reservas exitosas:** por corrida y naviera, si el texto que el log guardó de cada elección trae todas las
  palabras de la nave de su fila, solo la primera o ninguna. HYUNDAI, contra la planilla actual del panel.
- **HYUNDAI:** la nave de las filas 25 a 29 en las dos copias de la planilla, por hash. De cada tarjeta elegida, dónde
  aparece la primera palabra y el hash de la que sigue.
- **El tránsito y los transbordos:** la forma enmascarada de una tarjeta por naviera, y qué indicadores trae cada una.
- **El desempate por tránsito:** por (día de salida, nave por hash), cuántos grupos empatan y en cuántos el menor
  tránsito es único.
- **El nombre del operador:** su forma en `config.json` (largos y fuentes, nunca el texto), y qué commits lo traen, con
  la búsqueda de la sonda.
- **La red por commit y las piezas cambiadas:** leídas de git, con `ast`.

## NO retroceder (pieza 2)

- **No vuelvas a escribir `config.json` con `open(w)`:** lo trunca al abrir. Los dos paneles usan `_escribir_config`.
- **No vuelvas a dejar informativo el nombre del operador en la sonda,** salvo en `--almacen`. Tampoco vuelvas a
  buscarlo como la descripción entera: el apellido solo pasaba.
- **No saques la evidencia de las listas de HYUNDAI y CMA:** es lo que falta para aplicarles la regla.
- **No le des a ONE su propio «desde»:** usa `_desde`, como las demás.
- **No quites el aviso de MAERSK** mientras no se sepa si el portal acepta la fecha de hoy.

## Premisas del encargo contrastadas (pieza 5)

- **«La base: 301 pruebas, 640 mutaciones y 768 pares en `cc6e2f2`»:** confirmada. Es el control de la sonda de la red
  por commit.
- **«`_JS_HMM_INDICE_NAVE` acepta una tarjeta que traiga solo la primera palabra»:** confirmada.
- **«Como ya hace MSC»:** confirmada. MAERSK y COSCO también exigen todas; CMA, todas menos los prefijos de naviera.
- **«Si ninguna tarjeta calza, el camino de nave no encontrada que ya tiene cada naviera»:** confirmada. Las seis lo
  tienen y devuelven REVISAR.
- **Que los transbordos se pueden leer:** refutada en ONE y en MAERSK. El tránsito sí se lee en las cuatro.
- **«Todavía no hay HTML de esa lista» (HYUNDAI y CMA):** confirmada.
- **«La interpretación del informe» (ítem 5):** confirmada, con una excepción que el informe ya declaraba: ONE contaba
  siempre desde hoy.
- **«Hoy solo informa» (ítem 6):** confirmada. Además, buscaba la descripción entera, no el nombre y el apellido por
  separado.
- **«El mismo reintento que ya usa el panel web» (ítem 7):** confirmada: `_reemplazar`, hasta 20 intentos.

## Universo y cobertura (pieza 3)

- **`logs/`:** 9 carpetas de corrida, las 9 con `log.txt`; 0 descartadas. 1 con reservas EMITIDA: 20.
- **Los HTML:** 125, en `logs/` y junto al programa, para el campo de fecha de MAERSK. 0 lo traen.
- **Las listas del 25:** ONE 32 tarjetas, MSC 27, COSCO 4 y MAERSK 5. En el desempate, 0 tarjetas descartadas sin
  salida, nave o tránsito legible.
- **`config.json`:** 2 operadores. Uno es de la plantilla (clave `usuario<n>`, descripción «rellenar») y no cuenta.
  El otro da 2 términos.
- **Git:** 82 commits de `main`, 290 blobs leídos, 0 entradas descartadas. El almacén: 514 objetos.
- **No medido:**
  - si el portal de MAERSK acepta la fecha de hoy: falta el HTML de su formulario;
  - qué nave llevan las 5 reservas de HYUNDAI del 21: está en el portal, no en `logs/`;
  - cuántos transbordos tiene un «Transshipment» de ONE;
  - el panel de escritorio corriendo: su prueba lee el código con `ast`, porque la red no abre Tkinter.

## Defectos de instrumento cazados (pieza 4)

1. **Mi lector del tránsito de COSCO descartó las 4 tarjetas:** buscaba «NN Days» en un solo texto, y COSCO pone el
   número y «Days» en textos separados. El contador de descartadas lo mostró; se corrigió antes de leer el número.
2. **Un filtro del censo del ítem 5 no calzó con ninguna mutación** (lo escribí mal). Con 0 pruebas, el control corrió
   la suite entera, que pasó. No aportó nada: el gate se apoya en los otros cuatro filtros, que muerden todos.
3. **El cambio del ítem 3 hizo caer `test_clics.TestCma.test_itinerario_sin_nave_no_elige_el_primero`:** el nombre de
   la evidencia leía `reserva['fila']`, y esa prueba no trae fila. Se usó `reserva.get('fila', '')` y una mutación lo
   vigila.
4. **Mi barrido de voseo marcó «elegía»:** es un imperfecto, no un voseo. Falso positivo.
5. **La sonda vieja del nombre no separaba nombre y apellido ni quitaba tildes.** Se volvió a medir el historial con la
   búsqueda nueva: dio 0 en todo lo posterior a `9710ae2`, igual que antes.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| HYUNDAI acepta la nave por su primera palabra; ONE, por partes; CMA, sin los prefijos | FRENO del ítem 1 | …revisas en el portal las 5 reservas del 21, o decides aplicar la regla igual |
| ONE y COSCO empatan | FRENO del ítem 2 | …eliges (a), (b) o (c) |
| MAERSK busca desde mañana | FRENO del ítem 4 | …una corrida guarda el HTML de su formulario, o miras en el portal si deja elegir hoy |
| HYUNDAI y CMA sin la regla de la próxima salida | Falta el HTML de su lista | …una corrida deja `hmm_f*_naves` y `cma_f*_rutas` |
| MAERSK marca «el último checkbox» de los términos | FRENO: ninguna corrida llegó a la revisión | …una corrida de MAERSK llega a la revisión |
| CMA no confirma la ruta | «Validar ruta» no responde | …decides qué hacer sin esa confirmación |
| CMA y COSCO sin forma medida de confirmación | Nunca llegan a EMITIDA | …una emisión real deja su confirmación |
| Si el reemplazo sigue negado, queda `config.json.tmp` al lado de `config.json` | Así lo hacía el panel web; el ítem pedía su mismo comportamiento | …quieres que se borre al fallar (está fuera de git y la sonda lo prohíbe) |
| Los 72 commits hasta `9710ae2` traen el nombre del operador | No se reescribió el historial | …se agrega un remoto: un push los lleva |
| Los residuales de `CICLO-proxima-salida.md` y anteriores | No son parte de este encargo | …según cada fila de esos informes |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v13**:
- **PASO 0 con veredicto, por ítem:**
  - CICLO para los ítems 3, 5, 6 y 7;
  - FRENO para el 1 y el 2: medido, sin código;
  - FRENO para el 4, con la parte que el encargo pedía en ese caso: la fecha de mañana, con el aviso.
- **Re-medir contra HEAD antes de diseñar:** la base del encargo (301, 640 y 768) es el control de la sonda de la red.
- **Control positivo que aborta:** en cada sonda, y en la sonda de secretos, el C2 nuevo.
- **Todo salto silencioso lleva contador:**
  - 0 carpetas, 0 tarjetas y 0 entradas de git descartadas;
  - las palabras cortas del nombre, contadas y publicadas por la sonda.
- **La unidad la fija el sujeto:** el desempate decide entre tarjetas de la misma nave y el mismo día, así que se contó
  por ese grupo.
- **Todo registro es una hipótesis:** el comentario «ONE no usa el día de carga» y la sonda «informativa» se
  contrastaron con el código.
- **El negativo tiene que morder:** un censo filtrado en cada commit, `--negativo-nombre` a mano, y el censo completo al
  final.
- **Fuente única:**
  - `_desde` también para ONE;
  - `_escribir_config` para los dos paneles;
  - los términos del nombre salen de `config.json`, sin copia.
- **El cambio y su guardián en la misma operación:** cada cambio, con su prueba y su mutación en el mismo commit.
- **Cada reemplazo afirma su viejo una vez, y el EOL se preserva:** el prechequeo antes de cada gate; 0 CR en cada
  archivo commiteado.
- **FRENAR cuando la decisión es de negocio:** los ítems 1, 2 y 4.
- **Declarar las premisas refutadas:** los transbordos de ONE y MAERSK.
- **Choque, sin freno:**
  - «un commit por ítem» y los ítems con freno: el 4 tiene commit, porque el encargo pedía la fecha de mañana con el
    aviso; el 1 y el 2 no;
  - el cambio de `tests/correr.py` entró con el ítem 6, que lo necesitaba para su censo.

Reglas del módulo:
- casos sintéticos que imitan la estructura medida;
- la sonda de secretos antes de cada commit, ya bloqueando el nombre desde el ítem 6;
- nada de `logs/` en el repo;
- el nombre del operador en ningún archivo versionado;
- los textos nuevos en español con tuteo.

## Entregable (pieza 8)

Este `.md`, sin renderizar, y `CLAUDE.md` al día.

**Gates** (en cada uno, la sonda de secretos dio 0 sobre el staging; entre paréntesis, mutaciones y pares de cada censo
filtrado, y muerden todos):

| Commit | Suite completa | Censos filtrados |
|---|---|---|
| Ítem 3, `50e3f04` | 306 en verde, 0 cambios en los originales | `TestCma` (42 y 55), `TestEvidenciaListaHyundai` (3 y 5), `TestEvidenciaRutasCma` (2 y 4), `cma-rutas` (3 y 5), `hmm-lista` (3 y 5), `test_solo_ahi` (18 y 39) |
| Ítem 4, `fc7de54` | 306 en verde | `TestFechas` (14 y 20), `mk-hoy` (1 y 1), `mk-manana` (2 y 2), el aviso de MAERSK (3 y 3) |
| Ítem 5, `0e15b8a` | 306 en verde | `one-desde` (1 y 1), `one-sin-aviso` (1 y 1), la elección de ONE (4 y 4), los lectores del día de carga (3 y 3) |
| Ítem 6, `0af2d5b` | 314 en verde | `sonda-` (15 y 23) |
| Ítem 7, `6339e38` | 317 en verde | `config-` (11 y 17), `credenciales-sin-reintento` (1 y 2), `cred-no-reemplaza` (1 y 1), `reemplazar-` (3 y 4), `TestPanelCredenciales` (12 y 17) |

- **Censo completo final sobre `6339e38`:** pasó, en 43 minutos.
  - 317 pruebas en verde, y el control (la copia sin mutar) pasa;
  - 667 mutaciones y 811 pares, y muerden todos;
  - 0 pruebas sin mutación y 0 cambios en los originales.
- **El commit de este informe** solo agrega este `.md` y cambia `CLAUDE.md`, que ninguna prueba lee. La suite
  completa corrió con los dos ya cambiados: 317 en verde y 0 cambios en los originales.
