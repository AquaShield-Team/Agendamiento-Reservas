# CICLO · CONSOLIDADO sin espejo y cierre de la escritura de la planilla

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-23 · **Método:** skill `metodo-ciclo` v12 ·
**Base:** `4f5f355` · **Commits:** `0242321`, `aaca5f1`, `921aa6d`, `90791b1` y el de este informe
(locales, sin push).

> Sin datos reales: las dos planillas reales se midieron **solo en estructura**, contando fórmulas y valores
> por hoja y columna. La sonda nunca imprimió una celda ni el texto de una fórmula. Los ejemplos son
> sintéticos.

## Veredicto

- **Hecho lo que decidiste, en 4 commits:**
  1. La descarga del panel escribe solo en la hoja que se corrió (opción C).
  2. La descarga avisa lo que no pudo escribir, en pantalla y en `log.txt`.
  3. Una sola copia de respaldo por corrida, también con «todas».
  4. Se conservan las 10 copias más recientes y se borran solo las que calzan exacto con el nombre.
- **Ningún FRENA SI se cumplió.** Los tres se evaluaron midiendo:
  - **Fórmulas en CONSOLIDADO: 0.** No hay ninguna en las dos planillas reales, ni en CONSOLIDADO ni en otra
    hoja, y tampoco hay nombres definidos: todas las celdas son valores. El control positivo (2 fórmulas
    inyectadas en una copia sintética) las encontró.
  - **C no cambia qué hojas lee el panel.** Lo leen `_hojas_del_libro`, `_filas_de_hoja` y `leer_filas`,
    que están intactas. Solo cambió qué hojas escribe `_planilla_con_resultados`.
  - **La poda no puede alcanzar otra cosa que una copia.** Solo mira archivos de la carpeta de la planilla
    cuyo nombre calza exacto con el patrón. El programa crea esos nombres en un solo lugar
    (`respaldar_planilla`). Una prueba con 10 señuelos, todos más viejos que las copias, comprueba que
    ninguno se toca.
- **Solo 1 prueba cambió su expectativa:** la que fotografiaba el espejo en CONSOLIDADO. La lectura de la
  planilla no se tocó.
- **PASO 0: CICLO, cerrado.**

## Lo medido antes de cambiar

| Qué | Cómo | Resultado |
|---|---|---|
| Fórmulas en las planillas reales | openpyxl sin `data_only`: celdas `data_type 'f'`, fórmulas de arreglo y de tabla, y textos que empiezan con «=», por hoja y columna | **0 fórmulas en los dos libros** (7 hojas cada uno, 0 nombres definidos). En CONSOLIDADO las 30 celdas de Estado (H) son valores |
| Control positivo | La sintética con `=ONE!H5` en H5 y `=1+1` en I6 de CONSOLIDADO | 2 de 2 encontradas |
| Qué lee el panel | Revisar quién abre la planilla | `/api/planilla` → `_hojas_del_libro` y `/api/filas` → `_filas_de_hoja`, las dos con `leer_filas`. La descarga es la única que escribe |
| Copias de respaldo en la raíz hoy | `os.scandir` de la raíz | 32 entradas; **0** calzan con el patrón y 0 dicen «respaldo» sin calzar |
| Quién llama a `ejecutar_reservas` | Grep | `main()` (una naviera, o las seis seguidas con «todas») y la ventana Tkinter (una naviera por corrida) |

## Los cambios

| # | Antes (hasta el commit anterior) | Ahora | Commit |
|---|---|---|---|
| 1 | La descarga escribía también en CONSOLIDADO con los números de fila de la hoja corrida. Si la hoja no estaba en el libro, escribía en la primera | Escribe **solo** en la hoja que se corrió. Si corriste CONSOLIDADO, solo en CONSOLIDADO; si la hoja no está, no escribe nada (y el cambio 2 lo avisa) | `0242321` |
| 2 | Cada fila de la descarga callaba su error (`except Exception: pass`). Una hoja ausente o sin encabezados se saltaba sin decir nada | Todo lo que no se escribió se avisa al final, una línea por resultado con el texto para anotarlo a mano, más un resumen con las filas. Va por un `Registro` sobre el `log.txt` de la última corrida con `on_log=_wlog`, el registro que muestra el panel. Sin corrida, por la consola y el panel. La descarga se entrega igual con lo que sí se pudo escribir | `aaca5f1` |
| 3 | «todas» por consola dejaba una copia por naviera: 6 por corrida | `main()` marca la corrida «todas» (`_CORRIDA_CONSOLA`) y las seis navieras comparten una copia. La primera que escribe la hace; las otras anotan en su log «La copia de respaldo de esta corrida ya está: …». Al terminar, aunque falle, la marca se quita | `921aa6d` |
| 4 | Nadie borraba las copias | Al dejar la copia nueva, `podar_respaldos` conserva las **10 más recientes**, según la fecha y hora **del nombre**, y borra las demás. Avisa cuántas borró y cada una que no pudo borrar. Si la poda falla entera, avisa y la corrida sigue escribiendo | `90791b1` |

**Cómo se ve un aviso de la descarga** (sintético):

> · ⚠ No pude escribir en la planilla descargada el resultado de la fila 1: error inesperado (AttributeError:
> 'MergedCell' object attribute 'value' is read-only). Anótalo a mano: EMITIDA · BKGFALSO07 · x
>
> · ⚠ 1 resultado(s) no quedaron en la planilla descargada (filas 1); cada uno está arriba en este log.

**Qué puede borrar la poda, y qué no.** Solo borra un **archivo** (no una carpeta ni un enlace) que esté
**en la carpeta de la planilla**, sin entrar a subcarpetas, y cuyo nombre calce **exacto** (`re.fullmatch`,
distinguiendo mayúsculas) con `Reservas AQUASHIELD - respaldo AAAA-MM-DD HHMMSS.xlsx`. La prueba pone 10
señuelos, más viejos que todas las copias para que cualquier criterio flojo los borre primero, y exige que
queden todos:

| Señuelo | Por qué no calza |
|---|---|
| `… 000000 (2).xlsx` | Tiene sufijo de colisión |
| `reservas aquashield - respaldo …` | Está en minúsculas |
| `….xlsm` | Otra extensión |
| `….xlsx.bak` | Tiene cola después de `.xlsx` |
| `Agendamientos - respaldo …` | Es de otra planilla |
| `Copia de Reservas AQUASHIELD - respaldo …` | Tiene prefijo |
| `… 2025-1-1 …` | Formato de fecha distinto |
| `Reservas AQUASHIELD.xlsx` y `config.json` | No son copias |
| Un archivo con nombre exacto dentro de `sub/` | Está en una subcarpeta |
| Una **carpeta** con nombre exacto | No es un archivo |

## La prueba que cambió su expectativa

| Prueba | Antes | Después |
|---|---|---|
| `test_planilla.TestEscritura.test_web_descarga_es_copia_y_pisa_consolidado`, que pasa a llamarse `test_web_descarga_es_copia_y_solo_escribe_la_hoja_corrida` (`0242321`) | Además de ONE H5/I5/H7, exigía CONSOLIDADO H7 = «OK-EJEMPLO · armada sin emitir» y H5/I5 = «EMITIDA»/«BKGFALSO01» (la fila 7 de CONSOLIDADO es de CMA CGM) | Exige que cambien **solo** ONE H5, I5 y H7. Ahora compara el libro entero, antes y después de la descarga |

**Pruebas nuevas (8):**
- `test_web_descarga_de_consolidado_solo_escribe_consolidado`
- `test_web_descarga_de_hoja_que_no_esta_no_escribe`
- `test_web_descarga_avisa_lo_que_no_escribe` (los tres motivos, más el caso sin corrida)
- `test_descarga_avisa_en_pantalla_y_en_el_log`, de punta a punta por `/api/descargar` y `/api/estado`
- `test_todas_deja_una_sola_copia`
- `test_poda_deja_las_10_mas_recientes_y_nada_mas`
- `test_respaldo_poda_las_antiguas`, con una copia de solo lectura que no se puede borrar
- `test_si_la_poda_falla_igual_escribe`

**Mutaciones:**
- **28 nuevas.** Entre ellas está cada defecto de antes tal como era: el espejo en CONSOLIDADO, la hoja
  ausente escrita en la primera, el error de la fila callado y una copia por naviera.
- **1 retirada:** `descarga-sin-consolidado`, cuya línea ya no existe.
- **5 ajustadas al código nuevo,** con el mismo defecto: `respaldo-no-se-hace`, `respaldo-en-cada-fila`,
  `respaldo-despues-de-escribir`, `respaldo-sin-aviso` y `respaldo-aunque-no-se-escriba`.
- **2 que solo cambiaron de prueba,** porque la suya se renombró: `descarga-otro-texto-emitida` y
  `descarga-toca-el-archivo`.

## Universo y cobertura (pieza 3)

- **Planillas medidas:** la real de la raíz y la copia que guardó el panel en `%TEMP%` (7 hojas cada una:
  30 reservas en CONSOLIDADO y 5 por hoja de naviera), más la sintética y su copia con las 2 fórmulas del
  control positivo. **No se buscaron** planillas fuera del proyecto.
- **La red, commit por commit.** Cada commit pasó la suite completa, el censo completo y la sonda de
  secretos en 0 sobre el staging; los originales no cambiaron en ninguna corrida.

| Commit | Pruebas | Mutaciones | Pares mutación-prueba | Sin mutación | Motivos vacíos |
|---|---|---|---|---|---|
| base `4f5f355` | 125 | 183 | 213 | 0 | — |
| `0242321` | 127 | 185 | 215 | 0 | 0 |
| `aaca5f1` | 129 | 194 | 229 | 0 | 0 |
| `921aa6d` | 130 | 197 | 232 | 0 | 0 |
| `90791b1` | 133 | 210 | 245 | 0 | 0 |

## Re-medir (pieza 1)

```powershell
python tests\correr.py --todo
python tests\sonda_secretos.py --dry-run
cd tests; python -m unittest test_planilla.TestEscritura test_web.TestPanelPlanilla test_consola.TestEjecutarReservas
```

- **Las fórmulas:** abrir cada libro con openpyxl, una vez sin `data_only` para ver las fórmulas y otra con
  `data_only` para ubicar los encabezados con `leer_filas`. Contar por hoja y columna las celdas con fórmula
  y con valor, sin imprimir contenido, con el control positivo de 2 fórmulas inyectadas.
- **El script** fue de un solo uso y quedó fuera del repo (`sonda_formulas.py`).

## NO retroceder (pieza 2)

- **No vuelvas a espejar en CONSOLIDADO:** los números de fila de una hoja de naviera no son los de
  CONSOLIDADO, y ninguna columna identifica la reserva (medido en el ciclo anterior).
- **No vuelvas a escribir en otra hoja cuando falta la corrida:** si la hoja no está, no se escribe y se
  avisa.
- **No aflojes el patrón de la poda** (`search`, `match`, `re.I`, `os.walk` o un `glob` con comodín): cada
  una de esas variantes borra un señuelo en la red.
- **No ordenes las copias por la fecha del archivo:** copiar o mover una copia cambia esa fecha; la del
  nombre no cambia.

## Defectos de instrumento cazados (pieza 4)

1. **En el commit `0242321` encadené el commit a la sonda sin condicionarlo** (`;` en vez de parar si la
   sonda no daba 0). La sonda dio 0 en las dos pasadas, así que no hubo daño. Desde `aaca5f1`, el commit va
   en una llamada aparte, después de leer la sonda.
2. **La sonda de fórmulas nació sin control positivo:** un 0 de una sonda que nunca vio una fórmula no
   distingue «no hay» de «no las ve». Le agregué la copia sintética con 2 fórmulas **antes** de correrla
   sobre las reales.
3. **Cinco pares de este ciclo (3 mutaciones de la descarga) caen por `FileNotFoundError`, no por un fallo
   de aserción.** Con la mutación, el `log.txt` no llega a crearse porque no se escribe ningún aviso: la
   prueba cae justo por lo que vigila. Revisados uno por uno. Los otros 2 pares con ese motivo en el censo
   vienen de ciclos anteriores.

## Premisas del encargo contrastadas (pieza 5)

- **«En ese mismo bucle cada fila calla sus errores»:** confirmada. Además había otros tres saltos mudos: la
  hoja sin encabezados, la hoja ausente y la caída a la primera hoja del libro. Los tres se cerraron.
- **«La consola deja una copia por hoja (6 en una corrida todas)»:** confirmada. La mutación que devuelve el
  código viejo deja exactamente 6.
- **«Nadie las borra»:** confirmada. No había código que borrara copias.
- **«Las 30 colisionan; 25 de 30 sobre otra reserva»:** no se volvió a medir. Con C ya no se escribe en
  CONSOLIDADO desde una hoja de naviera, así que el número dejó de importar. La estructura sí se re-midió:
  30 reservas en CONSOLIDADO y 5 por hoja, igual que antes.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| CONSOLIDADO no se actualiza cuando corres una hoja de naviera | Es la opción C, decidida | …se necesita CONSOLIDADO al día: hace falta la columna de ID (opción A) |
| Las copias con sufijo « (2)» y las de otra planilla («Agendamientos - respaldo …») nunca se podan | El patrón decidido es exacto | …se acumulan |
| Un archivo que alguien nombre exacto como una copia se trata como copia | Es la definición decidida | …alguien guarda algo con ese nombre |
| La ventana Tkinter tiene «todas» solo para login; sus reservas son de una naviera por vez | No se tocó | …se le agrega «todas» a las reservas |
| La descarga todavía calla dos cosas cosméticas: copiar el estilo del encabezado nuevo y el ancho de columna | No pierden resultados | …un ancho o un estilo falla y alguien lo nota |
| `wb.save` de la consola no es atómico | La copia de respaldo lo cubre (viene del ciclo anterior) | …aparece una planilla dañada |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v12**:
- **PASO 0 y re-medir contra HEAD:** base de 125 pruebas en `4f5f355` antes de tocar nada.
- **Control positivo que aborta:** las 2 fórmulas inyectadas; y la suite sin mutar en cada censo.
- **Todo salto silencioso lleva contador:** los avisos y el resumen de la descarga, y el conteo de copias
  borradas y de las que no se pudieron borrar.
- **El negativo tiene que morder, de a uno por llamada:** 30 mutaciones nuevas o ajustadas.
- **Lo inocuo y lo peligroso conviven en la misma familia:** los señuelos de la poda separan copia de no
  copia en cada eje que un criterio flojo confundiría.
- **El cambio y su guardián, en el mismo commit.**
- **FRENAR:** los tres FRENA SI se evaluaron midiendo; ninguno se cumplió.
- **El push se entrega, no se hace:** no hay remoto, así que no hay nada que entregar.

Reglas propias del módulo (`CLAUDE.md`, la red): programa en sandbox, nunca el puerto 8765, toda prueba con
su mutación, las fotos se actualizan en el mismo cambio y la sonda antes de cada commit. **Choques:
ninguno.**

## Entregable (pieza 8)

Este `.md`, sin renderizar, y `CLAUDE.md` al día (la escritura de la descarga, las copias y la poda). Pasan
la sonda de staging antes de su commit.
