# CICLO · ONE y MAERSK eligen la nave, y el panel no dice «Confirmada» en modo prueba

**Módulo:** Agendamiento Reservas · **Encargo 34** · **Fecha:** 2026-09-27 · **Método:** skill `metodo-ciclo` v14 ·
**Commits** (locales; el repo no tiene remoto, así que no hay push que entregar): uno por cambio, `a07d465` (MAERSK:
el «Book» por su atributo label), `3997485` (ONE: la directa primero) y `4ae4fd6` (panel y planilla: «lista para
emitir»); y el de este informe, con `CLAUDE.md` al día.

**Base: `C:\dev\Agendamiento Reservas` @ `0046a10` · árbol limpio** (pieza 9). Las mediciones de `logs/` se hicieron
sobre las dos corridas de hoy con el lanzador de prueba (`web_todas_<operador>_20260927_183240` y `…_184055`, la más
reciente) y sobre las listas guardadas antes.

> Datos reales solo en lectura. `logs/` se leyó sin copiarlo: los `log.txt`, dos capturas (la de ONE y la de MAERSK
> donde se detuvieron, mirándolas, porque el encargo lo pide) y los HTML guardados, en un Chrome sin red y sin el
> JavaScript de la página, con el JavaScript del propio programa. En este informe no van nombres de naves ni viajes:
> la nave de cada fila se comparó solo en memoria.

**Resumen.** Las dos naves estaban en el portal, y en la primera lista: ni ONE ni MAERSK tenían que ampliar. Ninguna
de las hipótesis del encargo era la causa: el viaje y la palabra entera calzaron, y las tarjetas ya estaban cargadas.
- **ONE** encontró la nave en 4 salidas del mismo día. Dos tenían el mismo menor tránsito: una directa y una con
  transbordo. La regla de la próxima salida no desempata y la reserva quedó NO ENVIADA. Corregido con tu decisión: la
  regla de HYUNDAI, la directa primero (`3997485`).
- **MAERSK** encontró la salida pedida, con su «Book», pero el programa no lo veía: el texto del `mc-button` está dentro
  de su raíz shadow, y se contaba por el texto. Daba 0 «Book» en todas las tarjetas, y la reserva quedó NO ENVIADA con
  «la salida pedida ya no se puede reservar». Corregido: se cuenta por su atributo `label` (`a07d465`). **Lo mismo pasó
  en las dos corridas del 26-09**: la «salida sin Book» de `CICLO-ampliar-la-busqueda.md` no existía.
- **El panel** decía «✓ Confirmada» en toda fila OK-EJEMPLO. Ahora la columna dice «lista para emitir», igual que la
  planilla descargada, y la píldora y el estado final cuentan aparte las emitidas y las listas (`4ae4fd6`).
- Ningún clic nuevo antes de la guarda; `test_candado` no cambió. Nada de esto se probó en los portales: esa prueba la
  corres tú (abajo, «Cómo probarlo»).

## Veredicto del PASO 0, por parte del encargo

| Parte | Veredicto | Qué quedó |
|---|---|---|
| ONE corta en la elección de nave | **CICLO**, con una **PREGUNTA** de negocio que respondiste (la regla de HYUNDAI) | `3997485` |
| MAERSK corta en la elección de nave | **CICLO** | `a07d465` |
| Hipótesis: el filtro del viaje o la palabra entera cortan antes de ampliar | **DESCARTE:** en las dos, la nave y el viaje calzaron | Nada |
| Hipótesis: la lista se lee antes de que carguen las tarjetas | **DESCARTE:** ONE leyó 32 tarjetas a la vista; en MAERSK, el mismo lector da 0 «Book» también sobre el HTML guardado, que ya las trae | Nada |
| FRENA SI: la causa exige un clic nuevo antes de la guarda | **No se cumplió:** los dos arreglos cambian qué se lee y qué se elige; el clic del «Book» de MAERSK y el de la tarjeta de ONE ya existían | Nada |
| FRENA SI: tras ampliar, la nave no aparece | **No se cumplió:** las dos naves estaban en la primera lista, sin ampliar | Nada |
| «✓ Confirmada» en las OK-EJEMPLO | **CICLO**, y el contador, con tu decisión | `4ae4fd6` |

## ONE · la nave estaba; el empate era entre la directa y una con transbordo (`3997485`)

**Lo que dicen `log.txt` y el HTML** (las dos corridas de hoy, iguales): 32 tarjetas a la vista en 4 s; la nave de la
fila, con su viaje, en 4 de ellas, las 4 con salida el mismo día. `_JS_ONE_TARJETAS_NAVE` las encuentra, con su único
botón de reserva. El motivo de la NO ENVIADA: «4 de las 4 opciones salen el …, y 2 de ellas tienen el menor tiempo de
tránsito, 38 días». Esas dos tienen la misma salida y la misma llegada; una dice «Direct» y la otra «Transshipment». La
ventana se cerró 0,3 s después de leer la lista: ONE no amplía (decisión del encargo 33), y aquí no hacía falta.

**Medido en las 4 listas de ONE guardadas** (25 y 27-09), con el JavaScript del programa: 128 tarjetas; cada una trae
un solo elemento `TransshipmentInfo_transshipment-container`, con «Direct» o «Transshipment»; cada lista, 8 naves, y
cada nave, 4 salidas del mismo día con una sola directa. Con la regla de hasta hoy (el menor tránsito), 8 de las 32
empatan (la directa con una con transbordo) y 24 eligen. Con la de HYUNDAI (la directa primero), eligen las 32, y en 6
de ellas cambia la elegida: la directa llega 1 día después que la con transbordo que se elegía. Te lo pregunté con esos
números y elegiste la de HYUNDAI.

**Cambio.**
- `_hmm_directas_primero` pasa a ser `_directas_primero`, común, con el lector de fechas de cada naviera
  (`_hmm_salidas`, `_one_salidas`). HYUNDAI la llama igual que antes.
- `_JS_ONE_TARJETAS_NAVE` lee `directa`: true con «Direct», false con «Transshipment», null si no hay uno solo o dice
  otra cosa (que cuenta como con transbordo), como `_JS_HMM_TARJETAS`.
- `reservar_one` la aplica entre `_desde` y `_proxima_salida`, sobre las tarjetas con un solo botón. `log.txt` lo dice:
  «4 salidas de la nave salen el …: prefiero la directa; descarto 3 con transbordo».
- `_JS_ONE_CLIC_TARJETA` vuelve a leer la tarjeta elegida antes de pulsar, como HYUNDAI desde `96a0d2b`: calza con la
  nave, sale el día elegido y es directa o no como la elegida. Si no, no pulsa, y `log.txt` lo dice. Hasta hoy pulsaba
  la i-ésima sin volver a leerla; ahora dos tarjetas de la misma nave y el mismo día pueden diferir solo en eso.

**Sobre lo guardado, con el código nuevo** (`one_elige.py`): elige en las 32 naves, la directa en las 32; el clic
pulsa la elegida en las 32, y con la directa cambiada (control) no pulsa en ninguna. En la fila de hoy, la directa de
38 días.

## MAERSK · la salida pedida tenía su «Book», y el programa no lo veía (`a07d465`)

**Lo que dicen `log.txt` y el HTML** (las dos corridas de hoy, iguales): «Select sailing» cargó en 2 s («itinerarios y
botones Book en pantalla»); 6 salidas; la nave de la fila con su viaje en una sola; y «1 salida(s) de la nave sin un
solo «Book»: el portal no deja reservarlas», y NO ENVIADA con «la salida pedida ya no se puede reservar». La captura
muestra el «Book» en las tarjetas a la vista. Con el viaje en la fila y esa salida «sin Book», el programa no amplía
(decisión del encargo 32): por eso se cerró a los 4 s, sin bajar.

**La causa, medida en el HTML guardado** (`mk_book.js`, con control positivo de raíz shadow): el «Book» de cada salida
es un `mc-button label="Book" data-test="sailings-book-btn"`, y su texto está dentro de su raíz shadow, en el botón de
adentro (`aria-label="Book"`). El `textContent` del `mc-button` viene vacío, y `_JS_MK_SALIDAS` contaba el «Book» por
ese texto. En los 6 HTML de «Select sailing» guardados (25 al 27-09):

| | Tarjetas | Con el `mc-button` «Book» (sin `disabled`) | Sin ningún «Book» | «Book» como texto |
|---|---|---|---|---|
| 25-09 (2 corridas) | 5 y 5 | 1 y 1 | 4 y 4 | 0 |
| 26-09 (2 corridas) | 14 y 16 | 13 y 15 | 1 y 1 | 0 |
| 27-09 (2 corridas) | 6 y 6 | 6 y 6 | 0 | 0 |
| **Total** | **52** | **42** | **10** | **0** |

El lector de hasta hoy da 0 en las 52. **La salida pedida de las corridas del 26 y del 27-09 es la misma, y trae su
«Book» en las cuatro.** Playwright sí lo veía: la espera de «Select sailing» lo busca con `has_text`, que entra en las
raíces shadow, y lo encontró («itinerarios y botones Book en pantalla»); `_mk_pulsar_book` lo busca igual.

**Cambio.** `_JS_MK_SALIDAS` cuenta el «Book» por el atributo `label` del `mc-button`, o por su texto si lo trae.
Con el lector nuevo, las 42 dan 1 y las 10, 0; la salida pedida, 1 en las cuatro corridas. Con eso, `_mk_elegir_nave`
elige esa salida y pulsa su «Book» con `_mk_pulsar_book`, que no cambió. **La decisión de «la salida pedida ya no se
puede reservar» sigue:** en lo guardado hay 10 tarjetas sin ningún «Book», y ahí aplica.

## Panel y planilla · «lista para emitir» (`4ae4fd6`)

**Qué pasaba.** El panel lee la OK-EJEMPLO como «emitida» (`lecturaEstado`), y toda fila «emitida» sin número decía
«✓ Confirmada» en la columna «N° reserva emitida». Además, la píldora contaba las OK-EJEMPLO en «N de M emitidas ✓» y el
estado final decía «N de M reserva(s) emitidas con éxito». La planilla descargada dejaba esa celda vacía. Una EMITIDA
siempre trae su número (`_resultado_envio` solo la da con la forma medida), así que «Confirmada» solo salía en filas
que no se emitieron.

**Cambio.**
- `_texto_n_reserva` es la fuente única del texto de esa columna: el número de una EMITIDA; «lista para emitir»
  (`LISTA_PARA_EMITIR`) en la OK-EJEMPLO; nada en los demás estados. La planilla lo escribe; `/api/estado` lo manda en
  `n_reserva`, y el panel lo muestra tal cual.
- `lecturaEstado` lee la OK-EJEMPLO como «lista». La fila se ve como antes (el chip «ok (previa)» y la fila en verde).
- `cuentaCorrida` cuenta aparte: «3 de 5 listas para emitir»; con emitidas, «2 de 5 emitidas»; con las dos, «1 de 5
  emitidas · 2 de 5 listas para emitir». El estado final dice «Terminó: …» con esa misma cuenta.
- «Confirmada» no queda en ningún texto del panel. Con un número real, la columna muestra el número, como antes.
- El color de «lista para emitir» es `--text-secondary`, que el CSS define.

## Lo nuevo sobre el HTML guardado

`sonda.py` abre cada HTML por `file://`, sin sus `<script>` y sin red, para que el parser arme las raíces shadow
declarativas, y corre ahí las constantes `_JS_*` del programa, sacadas con `ast` (sin importar el módulo). Su control
positivo (un `mc-button` sintético con el texto solo en su raíz shadow) aborta si la raíz no se arma.
- **MAERSK** (`_JS_MK_SALIDAS` de `0046a10` y de `a07d465`): la tabla de arriba.
- **ONE** (`one_elige.py`, con una copia del programa importada en el scratchpad): las 32 naves, arriba.

**Lo que no prueba:** que el portal responda igual en vivo, que `_mk_pulsar_book` pulse el «Book» de esa tarjeta, y
lo que viene después: MAERSK no llega a la revisión desde el 24-09, y ahí sigue el FRENO de sus términos y condiciones
(«el último checkbox»). Eso es la corrida en vivo.

## Cómo probarlo (con el lanzador de prueba, candado cerrado)

1. Cierra el panel si está abierto y ábrelo con `Iniciar AQUASHIELD.bat` (nunca con el de emisión).
2. Corre las mismas dos filas de hoy (ONE y MAERSK).
3. Lo que debería aparecer:
   - **ONE:** «4 salidas de la nave salen el …: prefiero la directa; descarto 3 con transbordo», «nave encontrada y
     seleccionada», y el asistente hasta la guarda: OK-EJEMPLO. Si en cambio dice «no pulsé el botón de la tarjeta
     elegida: al volver a leer la lista…», avísame.
   - **MAERSK:** ya no «sin un solo «Book»»; «nave seleccionada: …», y después la revisión. Si llega, deja
     `mk_f<fila>_guarda.html`: con eso se puede dar con el objetivo específico de los términos y condiciones (tu FRENO).
     Si la revisión no aparece, NO ENVIADA con «Revisión de MAERSK».
   - **El panel:** en las OK-EJEMPLO, «lista para emitir» en la columna, y la píldora «N de M listas para emitir ✓».
     La planilla descargada, lo mismo en «N° de reserva emitida».

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\correr.py --mutaciones --filtro TestOne
python tests\correr.py --mutaciones --filtro TestHyundai
python tests\correr.py --mutaciones --filtro TestMaersk
python tests\correr.py --mutaciones --filtro TestLecturaDelPanel
python tests\correr.py --mutaciones --filtro TestPanelPlanilla
python tests\correr.py --todo
```

Las sondas son de solo lectura y no se versionan, porque leen datos reales. Quedaron en el scratchpad de esta sesión
(`$env:TEMP\claude\<proyecto>\<sesión>\scratchpad`), que puede limpiarse; sin ellas, estos números no se re-miden.
- **`sonda.py <html> <constante o .js> [argumento] [--programa <ruta>]`:** corre un JavaScript del programa, o uno de
  la sonda, sobre un HTML guardado. Control positivo de raíz shadow.
- **`mk_book.js`:** por tarjeta de MAERSK, el «Book» por texto, por `label` y dentro de la raíz shadow, y si está
  deshabilitado.
- **`one_modo.js` y `one_simula.py`:** las tarjetas de ONE con su «Direct» o «Transshipment», y la regla de hoy contra
  la de la directa, por nave.
- **`one_elige.py <AQUASHIELD.py> <html>…`:** lo que elige y pulsa el código de ese archivo, con el control de la
  directa cambiada.
- **`anclas.py <raíz> [prefijos]`:** que el texto viejo de cada mutación aparezca una vez, y que compilen las de esos
  prefijos.

En PowerShell: `$env:PYTHONIOENCODING='utf-8'` y después `python "<scratchpad>\<sonda>.py" …`, desde
`C:\dev\Agendamiento Reservas`.

## NO retroceder (pieza 2)

- **No vuelvas a contar el «Book» de MAERSK por el texto del `mc-button`:** viene vacío; el texto está en su raíz
  shadow. Por el `label`.
- **No trates una salida de MAERSK como «ya no se puede reservar» sin mirar el `label`:** así se leyeron mal las
  corridas del 26 y del 27-09.
- **No modeles el «Book» de MAERSK con el texto a la vista en una página falsa ni en el control de una sonda:** es la
  forma que dejó pasar el defecto.
- **No vuelvas a desempatar en ONE solo por el tránsito cuando una del mismo día es directa,** ni a pulsar su tarjeta
  sin volver a leerla.
- **No copies la regla de la directa por naviera:** es una sola, `_directas_primero`.
- **No vuelvas a mostrar «Confirmada» ni a contar como emitida una OK-EJEMPLO,** y no escribas el texto de esa columna
  en otro lugar que `_texto_n_reserva`.

## Universo y cobertura (pieza 3)

- **`logs/`:** 19 carpetas, todas con `log.txt`; las dos de hoy son las más recientes.
- **ONE:** 4 HTML con la lista (25-09 ×2, 27-09 ×2): 128 tarjetas, 32 naves (8 por lista, en gran parte las mismas entre
  corridas); 1 caso de la fila (la misma en las dos corridas de hoy).
- **MAERSK:** 6 HTML de «Select sailing» (25, 26 y 27-09, dos por día): 52 tarjetas; la salida pedida, en 4 de ellos
  (la misma fila el 26 y el 27-09).
- **Capturas:** 2 miradas (`one_f5_detenida.png` y `mk_f10_detenida.png` de la corrida de las 18:40).
- **No medido:** el portal en vivo después del cambio; la revisión de MAERSK; una lista de ONE sin directa o con dos.

## Defectos de instrumento cazados (pieza 4)

1. **El «Book» de MAERSK, ciego desde el 25-09** (el defecto del programa, que también fue de instrumento). La sonda
   `mk_lista.py` de `CICLO-ampliar-la-busqueda.md` medía con el propio `_JS_MK_SALIDAS`, y su control positivo era una
   tarjeta sintética con `<button>Book</button>`, el texto a la vista: una forma que ninguna lista guardada trae. El
   control pasaba, y la sonda leía «sin Book» donde había. El comentario del programa («todo eso está fuera de las
   raíces shadow», medido el 25-09) decía lo mismo. Un instrumento roto no solo acepta algo malo: **hizo abandonar algo
   bueno**, y se tomó una decisión de negocio sobre esa lectura. Cazado midiendo con tres lecturas a la vez (por
   texto, por `label` y dentro de la raíz shadow), con un control positivo que tiene la forma real: el texto solo en la
   raíz shadow.
2. **Mi primer lector de las tarjetas de ONE** (`one_tarjetas.py`, con `HTMLParser`) perdió la pila de etiquetas y dio
   32 tarjetas con solo «Origin» y la fecha, sin la nave. Descartado: se midió con el JavaScript del programa en Chrome.
3. **Mi primera sonda cargaba el HTML con `set_content`,** que puede no armar las raíces shadow declarativas. Se cambió
   a `file://` sin `<script>`, con control positivo de raíz shadow.
4. **Escribí en el comentario de `_JS_MK_SALIDAS` «41 tarjetas, 36 con»** antes de medirlo; medido, 52 y 42. Corregido
   antes del commit. En el mismo comentario iba el nombre real de la nave: sacado antes del commit.
5. **La herramienta Bash convirtió `\\n` en `\n`** en el script que agregaba las mutaciones de ONE (el defecto conocido
   del entorno). La aserción de coincidencia única lo frenó antes de escribir; se rehízo con un archivo.
6. **Usé `sort` y `timeout` de Git Bash,** que Defender bloquea (`CLAUDE.md` global). Sin efecto en los resultados.
7. **`anclas.py` leía el programa una vez por mutación y compilaba las 1097:** no terminó en 6 minutos; se detuvo y se
   reescribió (una lectura; compila solo las del cambio).
8. **El cambio de ONE rompió 8 anclas del censo:** 7 mutaciones de HYUNDAI cuyo texto ahora también está en el
   JavaScript de ONE, y `one-tarjetas-sin-botones`. Lo cazó `anclas.py` antes del commit; se re-anclaron con el contexto
   de su naviera, mutando lo mismo que antes.
9. **Mi prueba del panel buscaba «Confirmada» en todo `JS_INDEX`** y cayó por mi propio comentario, que la nombra. Ahora
   mira el código sin los comentarios.
10. **Dos ediciones de `CLAUDE.md` cortaron una línea a la mitad** y la juntaron con la siguiente (líneas de 169 y 185
    caracteres). Reacomodadas antes del commit.
11. **El censo filtrado sobre el estado de ONE se detuvo sin terminar** (terminó `TestOne`; `TestHyundai` y `TestMaersk`
    no), porque después vino el commit del panel y el censo completo lo cubre. Las mutaciones de MAERSK (`a07d465`) se
    censaron recién en el censo completo, no antes de su commit.
12. **La prueba de MAERSK modelaba un «Book» que el portal no usa** (el texto a la vista, igual que el control de
    `mk_lista.py`): por eso pasaba con el lector ciego. La página falsa ahora trae la forma medida (`label`, texto
    vacío), y la de texto queda como un caso aparte.

## Premisas del encargo contrastadas (pieza 5)

- **«El filtro del viaje o el calce por palabra entera cortan antes de ampliar»:** no. En ONE, 4 tarjetas calzan con la
  nave y el viaje; en MAERSK, la salida calza con la nave y con el viaje.
- **«La lista se lee antes de que carguen las tarjetas»:** no. ONE leyó 32 tarjetas a la vista; en MAERSK, el lector da
  0 «Book» también sobre el HTML guardado, donde están.
- **«La ventana se cerró a los ~2 s, sin bajar ni ampliar»:** sí, y por diseño: ONE no amplía, y MAERSK no amplía si la
  salida pedida está sin «Book». Las dos cortaron con la primera lectura, porque la nave estaba.
- **«Las dos naves existen en esos portales»:** sí, y en la primera lista.
- **De `CICLO-ampliar-la-busqueda.md`, «26-09: el viaje de la fila estaba solo en una salida sin «Book»»:** falso. Esa
  salida traía su «Book» (pieza 4, 1). La regla que se decidió sobre eso sigue siendo válida para las salidas sin
  «Book», que existen (10 en lo guardado).

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| Nada se probó en los portales | La corrida la corres tú | …me dices que corrió |
| MAERSK no llega a la revisión desde el 24-09; ahí sigue «el último checkbox» de los términos y condiciones (tu FRENO) | Falta el HTML de la revisión | …la corrida deja `mk_f<fila>_guarda.html` |
| `_mk_pulsar_book` no cambió: que pulse el «Book» de esa tarjeta está inferido (la espera de «Select sailing» lo encuentra con la misma forma), no probado | Hace falta el portal | …`log.txt` dice «no pude pulsar el «Book» de la salida elegida» |
| ONE: en 6 de 32 naves, la directa llega 1 día después que la que elegía el tránsito | Tu decisión | …prefieres el tránsito cuando la con transbordo llega antes |
| ONE: una tarjeta sin su «Direct» o «Transshipment» cuenta como con transbordo | Las 128 medidas lo traen | …aparece una sin él |
| ONE: el clic compara la nave de la fila con la tarjeta usando la misma regla de calce; si el portal re-dibuja la lista entre leer y pulsar, no pulsa y queda REVISAR «nave no encontrada» | Falla sin clic | …`log.txt` dice «no pulsé el botón de la tarjeta elegida» |
| El panel: el «detenido» usa `var(--muted)`, que el CSS no define | Ya estaba así; no es de este encargo | …se toca el estilo del panel |
| El panel: la OK-EJEMPLO sigue con el chip «ok (previa)» y la fila en verde | El encargo pide el texto de la columna y el contador | …prefieres otro chip |
| La consola (`escribir_estado`) no escribe «N° de reserva emitida» | Solo escribe el Estado, con «SIN EMITIR» en la OK-EJEMPLO | …la consola vuelve a usarse para reservar |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v14**.
- **PASO 0 con sus cuatro valores:** CICLO (ONE, MAERSK, el panel), DESCARTE (las dos hipótesis) y PREGUNTA (la regla
  de ONE); NOTA no salió.
- **FRENAR cuando la decisión es de negocio:** qué salida elige ONE entre la directa y la con transbordo. Te lo pregunté
  con lo medido (8 empates, 6 elecciones que cambian) y respondiste; también si el contador entraba.
- **Re-medir contra HEAD antes de diseñar:** los dos cortes se midieron con el JavaScript de `0046a10` sobre el HTML de
  hoy; los arreglos, con el de su commit.
- **Control positivo que aborta, en las dos direcciones:** la raíz shadow sintética en `sonda.py`; y en MAERSK, 10
  tarjetas sin «Book» que el lector nuevo sigue dando en 0; en ONE, el clic con la directa cambiada no pulsa.
- **El mismo defecto también alarma:** el «Book» ciego no solo cortó reservas; llevó a una decisión de negocio sobre
  un dato falso (pieza 4, 1; pieza 5).
- **La unidad la fija el sujeto:** la regla decide por nave: se contó por nave (32), no por tarjeta (128).
- **Todo salto silencioso lleva contador:** 52 tarjetas de MAERSK, 42 con «Book» y 10 sin; 128 de ONE, 1 elemento de
  directa en cada una.
- **Todo registro es una hipótesis:** el comentario del programa («fuera de las raíces shadow») y el informe del
  encargo 32 («sin Book») resultaron falsos.
- **El negativo tiene que morder:** en cada commit, sus mutaciones; al cerrar, el censo completo.
- **El cambio y su guardián en la misma operación:** cada commit trae sus pruebas y sus mutaciones.
- **Fuente única:** `_directas_primero` (HYUNDAI y ONE) y `_texto_n_reserva` (panel y planilla).
- **Cada reemplazo afirma su viejo una vez; escritura atómica; el EOL se preserva:** 0 CRLF en los archivos tocados.
- **Verificación adversarial:** una revisión del código de los tres commits, sin hallazgos (pieza 8).
- **Choques entre reglas:**
  1. **«Sin clics nuevos antes de la guarda» contra arreglar MAERSK:** con el «Book» visible, el programa lo pulsa y
     sigue hasta la revisión, donde marca «el último checkbox». Los dos clics ya existían (el segundo, con tu FRENO);
     no hay clic nuevo, pero es la primera vez desde el 24-09 que ese camino corre.
  2. **«Encontrar la causa y corregirla» contra «FRENAR cuando la decisión es de negocio»:** en ONE, la corrección era
     elegir una regla; se preguntó.
  3. **La directa «solo en HYUNDAI» del encargo 33 contra ONE:** ahora es de las dos, por tu decisión, con una sola
     pieza.

Reglas del módulo: casos sintéticos (ningún nombre de nave ni viaje real en el repo); la sonda de secretos antes de
cada commit; nada de `logs/` en el repo; `test_candado` sin cambios; los textos en español con tuteo.

## Entregable (pieza 8)

- **Este `.md`:** no se convirtió en página; se leyó como texto.
- **`CLAUDE.md` al día,** en el mismo commit.

**La red por commit** (contada de `tests/mutaciones.py` y de las pruebas de cada commit; la de `4ae4fd6`, la del censo):

| Commit | Pruebas | Mutaciones | Pares |
|---|---|---|---|
| `0046a10` (base) | 410 | 1082 | 1307 |
| `a07d465` (MAERSK) | 411 | 1084 | 1310 |
| `3997485` (ONE) | 413 | 1097 | 1324 |
| `4ae4fd6` (panel) | 415 | 1107 | 1337 |

**Gates.** En los tres, la sonda de secretos dio 0 sobre el árbol y sobre lo agregado con `git add`, y 0 CRLF.

| Commit | Antes del commit | Después |
|---|---|---|
| Base, `0046a10` | Suite completa sobre una copia: 410 en verde, 0 cambios en los originales (406 s) | |
| MAERSK, `a07d465` | `test_clics.TestMaersk`: 20 en verde | Censo completo (abajo) |
| ONE, `3997485` | `test_ayudantes`, `test_clics` y `test_evidencia`: 219 en verde; `anclas.py`: 1097 mutaciones, 0 con problemas; censo `TestOne` sobre una copia idéntica (mismo hash): 97 mutaciones y 115 pares, todos muerden, 413 pruebas, 0 sin mutación | Censo completo |
| Panel, `4ae4fd6` | `test_envio.TestLecturaDelPanel`, `test_planilla`, `test_web` y `test_booking`: 91, con 1 caída por mi propia prueba (pieza 4, 9), arreglada y vuelta a correr (`TestLecturaDelPanel`, 4 en verde); `anclas.py`: 1107, 0 con problemas | Censo completo |

**Batería completa** (`correr.py --todo`) sobre una copia de `4ae4fd6`, el último commit de código, el 27-09 de 20:04
a 20:40: la suite, 415 en verde (225 s); el control (la copia sin mutar) pasa; 1107 mutaciones y 1337 pares
mutación-prueba, **los 1337 muerden**, 0 pruebas sin mutación y 0 cambios en los originales. Se corrió sobre una copia
para poder seguir con el informe en el repo mientras tanto: la foto de los originales fallaría si la raíz cambia.

**Revisión adversarial** de los tres commits (un agente, solo lectura, con las pruebas de ONE, MAERSK, HYUNDAI,
`test_candado`, el panel y la planilla): 0 críticos, 0 altos, 0 medios y 0 bajos con evidencia. Revisó en especial
que el `esBook` nuevo no pueda contar dos «Book» y colar un clic (el llamador exige `book == 1`: con 2, la tarjeta no
cuenta), que el `null` de la directa se compare igual en la lectura y en el clic, que el orden en `reservar_one` sea el
de HYUNDAI y que ningún otro estado empiece con «OK». Anotó el `--muted` sin definir, que ya estaba en el residual.

## Qué decides tú

1. **Corre la prueba** con el lanzador de prueba (arriba) y avísame: si MAERSK llega a la revisión, con su HTML se
   puede cerrar el FRENO de los términos y condiciones.
