# CICLO · Escritura de resultados en la planilla

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-23 · **Método:** skill `metodo-ciclo` v12 ·
**Base:** `d86fbca` · **Commits:** `8feabdb`, `fba3bc3`, `1acc08b`, `ce1825d` y el de este informe
(locales, sin push).

> Sin datos reales: las planillas reales se midieron **solo en estructura** (encabezados, conteos y
> colisiones). La sonda nunca imprimió el valor de una celda, y un encabezado solo se mostraba si era idéntico
> a uno de la planilla sintética. Los ejemplos de este informe son sintéticos.

## Veredicto

- **FRENO en CONSOLIDADO.** Ninguna columna de CONSOLIDADO identifica la reserva sin ambigüedad, ni en la
  planilla real ni en la copia que subiste al panel; tampoco la fila completa. El defecto sigue abierto: la
  clave la decides tú. Abajo están las columnas, las colisiones medidas y tres opciones.
- **Arreglados, cada uno en su commit:** el «SIN EMITIR» de la consola, la columna Estado en la P y los
  errores de escritura que se perdían en silencio. Además, la **copia de respaldo** que decidiste para la
  consola.
- **Cómo leí el freno.** «Y para» lo apliqué al defecto de CONSOLIDADO. Los otros tres ya estaban decididos y
  no dependen de la clave, así que seguí con ellos. Si preferías que el freno detuviera todo el ciclo, los 4
  commits son locales y se deshacen sin tocar nada más.
- **Los otros dos FRENA SI no se cumplieron:**
  - Solo cambiaron su expectativa las 3 pruebas que fotografiaban el defecto que se arreglaba (lista abajo).
  - La lectura no se tocó: `leer_reservas`, `leer_filas` y `_mapear` están iguales. `_columna_estado` llama
    a `_mapear`, pero no la cambia.
- **PASO 0: CICLO**, con un freno parcial.

## CONSOLIDADO: la medición que frena

**Qué hace hoy la descarga del panel** (`_planilla_con_resultados`): escribe los resultados en la hoja que se
corrió y **también en CONSOLIDADO, en los mismos números de fila**. Medido sobre la planilla real: de las 30
reservas de las 6 hojas de naviera, **25 caerían sobre otra reserva de CONSOLIDADO**. Las 5 de ONE coinciden
solo porque ONE es el primer bloque de CONSOLIDADO.

**Columnas de CONSOLIDADO y colisiones.** Las dos planillas reales tienen los mismos 9 encabezados que la
sintética, en la fila 4, y 30 reservas en CONSOLIDADO. «En colisión» cuenta las filas cuyo valor se repite en
otra fila.

| Columna | Real (raíz): distintos / filas en colisión | Real (subida al panel): distintos / en colisión | Sintética: distintos / en colisión |
|---|---|---|---|
| A Naviera | 6 / 30 | 6 / 30 | 7 / 0 |
| B Pto. Embarque | 3 / 30 | 3 / 30 | 1 / 7 |
| C Puerto Descarga | 6 / 30 | 6 / 30 | 4 / 4 |
| D Destino Final | 6 / 30 | 6 / 30 | 4 / 4 |
| E NAVE | 6 / 30 | 5 / 30 | 7 / 0 |
| F Viaje | 7 / 30 | 6 / 30 | 7 / 0 |
| G Contrato / Cotización | 5 / 30 | 5 / 30 | 2 / 0 (5 vacías) |
| H Estado | 1 / 30 | 2 / 30 | vacía |
| I N° de reserva emitida | 26 / 5 | 25 / 0 (5 vacías) | vacía |
| **Fila completa** (los 14 campos del lector) | **7 / 30** | **6 / 30** | 7 / 0 |

- **Ninguna columna sirve de clave.** Todas las de datos colisionan en las 30 filas.
- **«N° de reserva emitida» tampoco sirve,** aunque en la copia subida no colisione: es la **salida** del
  robot. Una reserva que todavía no se emite no tiene número, así que no sirve para ubicar dónde escribir su
  resultado. En la planilla de la raíz, además, 5 filas colisionan.
- **Ni la fila completa distingue:** hay 30 reservas con solo 7 contenidos distintos (6 en la copia
  subida). Son reservas iguales para la misma nave y viaje.
- **Cruce con las hojas:** cada una de las 30 reservas de las hojas de naviera calza con **más de una** fila
  de CONSOLIDADO, por cualquier columna y por la fila completa.

**Lo que sí calza: la posición.** En las dos planillas reales, CONSOLIDADO es la concatenación de las 6 hojas
en el mismo orden. La k-ésima reserva de cada hoja coincide en los 13 campos con la k-ésima fila de esa
naviera en CONSOLIDADO: **30 de 30**. Pero es un supuesto sobre cómo se arma CONSOLIDADO, no una columna. En la
sintética no se cumple: 2 iguales, 4 distintas y 11 sin par.

**La decisión es tuya.** Tres opciones:

| Opción | Qué hace | A favor | En contra |
|---|---|---|---|
| **A · Columna de ID** | Una columna nueva, por ejemplo «ID reserva», única en cada hoja y en CONSOLIDADO; la descarga ubica la fila por ella | Robusta aunque se ordene o se filtre | Operaciones tiene que llenarla, y el lector tiene que leerla (otro frente, porque toca la lectura) |
| **B · Posición verificada** | La k-ésima reserva de la naviera en CONSOLIDADO, escribiendo solo si esa fila tiene el mismo contenido; si no, avisa y no escribe | Funciona con la planilla de hoy (30/30); nunca escribe sobre una fila distinta | Si alguien reordena filas idénticas, un resultado puede ir a su gemela. Hay que rehacer el CONSOLIDADO sintético, que hoy no es la concatenación, y eso mueve las fotos de los lectores |
| **C · No espejar** | Si corres una hoja de naviera, la descarga escribe solo esa hoja; si corres CONSOLIDADO, solo CONSOLIDADO | La más simple; no puede escribir sobre otra reserva; es lo mismo que ya pasa al revés | CONSOLIDADO deja de actualizarse cuando corres una hoja de naviera |

Mi recomendación es **C**: es la única que no depende de un supuesto. B conviene si necesitas que
CONSOLIDADO se actualice desde las hojas.

## Los arreglos

| # | Defecto (medido en HEAD `d86fbca`) | Ahora | Commit |
|---|---|---|---|
| 1 | La consola terminaba el texto en «· SIN EMITIR» con cualquier estado, también con EMITIDA | «SIN EMITIR» solo con OK-EJEMPLO. Un ERROR o un REVISAR puede venir **después** del botón final (COSCO devuelve ERROR «tras pulsar Submit»), y ahí afirmar «sin emitir» sería falso | `8feabdb` |
| 2 | Sin columna «Estado», «Estado (Robot)» caía en la P (16) y no en la M (13): el bucle que la buscaba con `ws.cell()` creaba celdas y corría `max_column` | `_columna_estado` la ubica por su encabezado con `_mapear`. Si no existe, la crea en la fila de encabezados, en la siguiente al último encabezado y nunca antes de la M (`COL_ESTADO_MINIMA`). No depende de `max_column` | `fba3bc3` |
| 3 | `escribir_estado` se tragaba cualquier error (`except Exception: pass`) y, si faltaba la hoja, volvía sin escribir: con la planilla abierta en Excel, el resultado se perdía | Levanta `ErrorEscritura` con el motivo en español. `ejecutar_reservas` avisa por fila, con el texto para anotarlo a mano, sigue con la corrida y cuenta en el resumen las filas que no quedaron | `1acc08b` |
| 4 | (Decisión nueva) Copia de respaldo antes de escribir | `respaldar_planilla()`: una copia por corrida, justo antes de la primera escritura, junto a la planilla: «Reservas AQUASHIELD - respaldo AAAA-MM-DD HHMMSS.xlsx» (« (2)» si coincide el segundo). **Si la copia falla, no escribe.** Queda fuera de git por `*.xlsx` (comprobado con `git check-ignore`), y `encontrar_archivo_reservas` no la confunde con la planilla | `ce1825d` |

**Cómo se ve un error** (sintético, planilla de solo lectura):

> · ⚠ No pude escribir el resultado de la fila 5 en la planilla: «Reservas AQUASHIELD.xlsx» está abierta en otro
> programa (¿Excel?) o es de solo lectura; ciérrala y vuelve a correr. Anótalo a mano: SOLICITUD 1 · OK-EJEMPLO · …
>
> · ⚠ 2 resultado(s) no quedaron en la planilla (filas 5, 6); cada uno está arriba en este log.

Sale por el `Registro` de la corrida, así que queda en `log.txt`, en la consola y en la ventana Tkinter si la
corrida se lanzó desde ahí. La prueba verifica los tres destinos.

## Pruebas que cambiaron su expectativa

Solo estas tres. Cada una fotografiaba el defecto que se arregló en su commit:

| Prueba | Antes | Después |
|---|---|---|
| `test_consola.TestEjecutarReservas.test_reservas_por_consola` (`8feabdb`) | La fila EMITIDA terminaba en `· Booking: FALSO777 · SIN EMITIR` | Termina en `· Booking: FALSO777`. La fila OK-EJEMPLO no cambió |
| `test_planilla.TestEscritura.test_consola_sin_columna_estado_crea_una` (`fba3bc3`) | «Estado (Robot)» y el valor en P4/P5; M4 vacía | En M4/M5; P4 vacía |
| `test_planilla.TestEscritura.test_consola_error_silencioso`, que pasa a llamarse `test_consola_error_de_escritura_se_levanta` (`1acc08b`) | `escribir_estado` devolvía `None` sin avisar | Levanta `ErrorEscritura`: «no encontré «Reservas AQUASHIELD.xlsx» junto al programa» |

Además, sin cambiar ninguna expectativa:
- `ConPlanilla.setUp` de `test_consola` borra los respaldos que dejaron las pruebas anteriores, para que cada
  prueba cuente solo los suyos.
- El docstring de `test_consola` ya no dice que el «SIN EMITIR» se fotografía.

**Pruebas nuevas (9):**
- `test_sin_emitir_solo_si_volvio_sin_emitir`
- `test_consola_columna_nueva_no_depende_de_max_column`
- `test_consola_encabezado_en_otra_fila`
- `test_consola_errores_de_escritura_en_espanol`
- `test_error_de_escritura_se_muestra_y_queda_en_el_log`
- `test_respaldo_antes_de_escribir`
- `test_sin_respaldo_no_escribe`
- `test_respaldos_no_se_pisan`
- `test_sin_escrituras_no_deja_respaldo`

**Mutaciones:**
- **26 nuevas** (158 + 26 − 1 = 183). Entre ellas está cada defecto de antes tal como era: la cola «SIN
  EMITIR» siempre, el corrimiento a la P y el error que se calla.
- **1 retirada:** `escribir-avisa-errores`, que inyectaba el `raise` que ahora es lo correcto.
- **4 ajustadas al código nuevo,** con el mismo defecto: `consola-sin-aviso-sin-emitir`,
  `escribir-otro-encabezado`, `escribir-otra-columna-nueva` y `escribir-guarda-en-otra-parte`.

## Universo y cobertura (pieza 3)

- **Planillas medidas:**
  - La real de la raíz y la copia que el panel guardó al subirla, en `%TEMP%`. En la carpeta del proyecto hay
    **1** `.xlsx`, contado con Glob `**/*.xlsx`.
  - Cada una tiene 7 hojas, con encabezados en la fila 4 idénticos a los sintéticos, 30 reservas en
    CONSOLIDADO y 5 en cada hoja de naviera.
  - También se midió la sintética.
  - **No se buscaron** planillas fuera del proyecto (Descargas, correo).
- **La consola en la planilla real:** todas sus hojas tienen «Estado» en la H. La rama que creaba la columna
  (el defecto de la P) **nunca se ejecutaba** con la planilla real de hoy; habría aparecido con una hoja sin
  «Estado».
- **Control positivo de la sonda:** sobre la sintética reprodujo la estructura conocida (9 encabezados, 7
  reservas en CONSOLIDADO) y el cruce que la red ya fotografiaba: la fila 7 de CONSOLIDADO es de CMA.
- **La red, commit por commit** (cada uno con la suite completa, el censo completo y la sonda de secretos en 0
  sobre el staging):

| Commit | Pruebas | Mutaciones | Pares mutación-prueba | Sin mutación | Motivos vacíos |
|---|---|---|---|---|---|
| base `d86fbca` | 116 | 158 | 182 | 0 | — |
| `8feabdb` | 117 | 160 | 186 | 0 | 0 |
| `fba3bc3` | 119 | 164 | 193 | 0 | 0 |
| `1acc08b` | 121 | 173 | 202 | 0 | 0 (1 antes de arreglar el instrumento) |
| `ce1825d` | 125 | 183 | 213 | 0 | 0 |

Todos los pares muerden, y la suite sin mutar pasa en cada commit. Los originales no cambiaron en ninguna de
las corridas válidas (la única que sí, más abajo).

## Re-medir (pieza 1)

```powershell
python tests\correr.py --todo
python tests\sonda_secretos.py --dry-run
cd tests; python -m unittest test_consola.TestEjecutarReservas test_planilla.TestEscritura
```

- **Las colisiones de CONSOLIDADO:** en solo lectura, con `leer_filas` de una copia en sandbox (el arnés),
  contar por columna las filas no vacías, los valores distintos y las filas en colisión, sin imprimir valores.
  El cruce por posición es la k-ésima reserva de cada hoja contra la k-ésima fila de esa naviera en
  CONSOLIDADO.
- **Los scripts** fueron de un solo uso y quedaron fuera del repo (`sonda_clave.py`, `sonda_ordinal.py`).
  Para rehacerlos basta con la descripción de arriba.

## NO retroceder (pieza 2)

- **No vuelvas a buscar columnas con `ws.cell()` más allá de `max_column`:** openpyxl crea la celda y corre
  la hoja; así la columna nueva caía en la P.
- **No escribas «SIN EMITIR» sin haber visto OK-EJEMPLO:** en COSCO, un ERROR puede llegar después de
  Submit, con la reserva quizá emitida. Un «sin emitir» falso invita a reenviarla y duplicarla.
- **No vuelvas a silenciar `escribir_estado`:** el caso típico, la planilla abierta en Excel, es justo el
  que perdía el resultado.
- **No escribas sobre la planilla sin la copia:** si `respaldar_planilla()` falla, no se escribe.
- **No ubiques la fila de CONSOLIDADO por el número de fila de otra hoja,** ni por el contenido a secas:
  las dos cosas están medidas como ambiguas.

## Defectos de instrumento cazados (pieza 4)

1. **Edité `AQUASHIELD.py` mientras corría la línea base.** Las pruebas cargan el programa al empezar cada
   clase, así que esa corrida mezcló las dos versiones. El corredor lo detectó («las fuentes del programa
   cambiaron durante la corrida», FALLA). Repetí la base sobre un `git archive` de HEAD: 116 OK. Desde ahí,
   ninguna fuente se editó con una corrida en marcha.
2. **Motivo vacío en el censo.** `motivo()` de `correr.py` reconocía una lista fija de excepciones, y la del
   programa llega como `aquashield_prueba_N.ErrorEscritura:`, así que 1 par quedó sin motivo auditable. Le
   agregué un respaldo que reconoce cualquier `…Error`, `…Exception` o `…Escritura`, con control positivo y
   negativo, y repetí el censo: 0 vacíos. Va en `1acc08b`.
3. **Mi chequeo rápido de mutaciones miraba solo `AQUASHIELD.py`:** dio 3 falsas alarmas, las mutaciones de
   los lanzadores, que apuntan a otros archivos. Las descarté leyéndolas; la autoridad es el censo.
4. **La sonda de posición corrió en paralelo con un censo.** La suite tardó 161 s en vez de ~78. El
   resultado no cambió: la sonda solo lee, y los originales no cambiaron.
5. **Para no filtrar datos reales,** la sonda de CONSOLIDADO se corrigió antes de correrla: imprime un
   encabezado solo si es idéntico a uno sintético y nunca un valor de celda.

## Premisas del encargo contrastadas (pieza 5)

- **«La consola escribe SIN EMITIR aunque vuelva EMITIDA»:** confirmada en HEAD. También pasaba con ERROR y
  REVISAR, y el caso de COSCO («ERROR tras pulsar Submit») lo volvía peligroso, no solo inexacto.
- **«La descarga escribe CONSOLIDADO con los números de fila de la hoja elegida»:** confirmada. Sobre la
  planilla real, 25 de 30 resultados caerían sobre otra reserva.
- **«escribir_estado deja el estado en la P en vez de la M»:** confirmada en la sintética. Matiz: con la
  planilla real de hoy no se ejecutaba, porque todas sus hojas tienen «Estado».
- **«Se traga las excepciones sin avisar»:** confirmada. Además, la hoja faltante volvía en silencio sin
  lanzar nada.
- **«Medir qué columna identifica la reserva en CONSOLIDADO»:** ninguna. Es el freno.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| CONSOLIDADO recibe resultados con números de fila ajenos | Freno: la clave la decides tú | …eliges A, B o C |
| En la descarga del panel, el `except Exception: pass` de cada fila sigue callando errores | Está en el mismo bucle que CONSOLIDADO y va con su arreglo | …se arregla CONSOLIDADO |
| `wb.save` escribe la planilla sin atomicidad | Un corte a mitad podría dañarla; ahora hay copia de respaldo | …aparece una planilla dañada |
| Los respaldos se acumulan: uno por corrida de consola, 6 en una corrida «todas» | Nadie los borra | …la carpeta se llena |
| El texto de la consola dice «ref(ej) EJ…» también en una EMITIDA | Es la referencia de la solicitud, no un estado; el encargo apuntaba a «SIN EMITIR» | …alguien lo lee como «ejemplo» |
| Los errores inesperados muestran el tipo y el texto de Python (en inglés) dentro del mensaje en español | No hay traducción para todo; los casos conocidos (abierta, falta, hoja, encabezados) van en español | …aparece un caso frecuente sin traducir |
| Una hoja sin encabezados reconocibles ahora da error; antes escribía en la fila 4 | Es un error que se ve, en lugar de una escritura a ciegas | …una planilla real no tiene encabezados |
| La M como columna mínima (`COL_ESTADO_MINIMA`) viene de la intención original | No se midió si alguna planilla usa las columnas J a L sin encabezado | …una hoja sin «Estado» tiene datos en J a L |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v12**:
- **PASO 0 y re-medir contra HEAD:** base limpia sobre `git archive`.
- **La unidad la fija el sujeto:** la reserva, no la celda. Por eso se probaron columna, fila completa y
  posición.
- **Control positivo que aborta:** la sintética en la sonda; la copia sin mutar en cada censo.
- **Todo salto silencioso lleva contador:** el resumen cuenta las filas no escritas, y en el censo se
  vigilaron los motivos vacíos.
- **El negativo tiene que morder, de a uno por llamada:** 213 pares.
- **El cambio y su guardián, en el mismo commit.**
- **Se declaran las premisas y el residual.**
- **FRENAR cuando la decisión es de negocio:** la clave de CONSOLIDADO.
- **El push se entrega, no se hace:** no hay remoto, así que no hay nada que entregar.

**Revisión independiente.** Un revisor leyó el diff `d86fbca..ce1825d` en solo lectura: **0 defectos
confirmados**. Dejó dos dudas, las dos ya declaradas:
- Una corrida «todas» deja un respaldo por naviera (está en el residual).
- Un REVISAR anterior a la guarda, como una nave de MAERSK que no aparece, ya no lleva «SIN EMITIR». Es así
  por diseño: solo OK-EJEMPLO lo garantiza, y el detalle de esa fila sigue diciendo «SIN emitir».

Reglas propias del módulo (`CLAUDE.md`, la red): programa en sandbox, nunca el puerto 8765, toda prueba con
su mutación, las pruebas son fotos que se actualizan en el mismo cambio, y la sonda antes de cada commit.

**Choques:** «y para» del freno contra «un commit por defecto» del loop. Lo resolví limitando el freno a su
defecto; está declarado arriba para que lo corrijas si no era eso.

## Entregable (pieza 8)

Este `.md`, sin renderizar, y `CLAUDE.md` al día: el camino consola, el defecto abierto de CONSOLIDADO y el
número de pruebas. Pasan la sonda de staging antes de su commit.
