# CICLO · MSC y CMA amplían la búsqueda, y HYUNDAI prefiere la directa

**Módulo:** Agendamiento Reservas · **Encargo 33** · **Fecha:** 2026-09-27 · **Método:** skill `metodo-ciclo` v14 ·
**Commits** (locales; el repo no tiene remoto, así que no hay push que entregar): uno por ítem, `38aa08d` (ONE no pasa
de 8 semanas), `a37373f` (HYUNDAI: la directa primero), `ff76fea` (MSC: bajar por la lista) y `2044222` (CMA: «Cargar N
siguientes resultados»); dos que salieron de la revisión del informe, `96a0d2b` (HYUNDAI: el «Book Now» comprueba que
sea la directa) y `922e91d` (CMA: dice por qué dejó de cargar rutas); y el de este informe.

**Base: `C:\dev\Agendamiento Reservas` @ `924485a` · árbol limpio** (pieza 9). Las mediciones de `logs/` se hicieron
sobre esa base. No hubo corridas nuevas desde el 26-09: `logs/` sigue con las mismas 15 carpetas.

> Sin datos reales. `logs/`, las planillas y `config.json` se midieron en solo lectura, con sondas que imprimen
> conteos, booleanos, etiquetas de la interfaz, días relativos y formas enmascaradas (A por letra, 9 por cifra). La nave
> de una fila se comparó solo en memoria. Las capturas se leyeron con OCR sin mirarlas. Los HTML guardados se leyeron
> en un Chromium sin red y sin el JavaScript de la página.

**Resumen:** todo está implementado y probado sin abrir los portales. Ninguna de estas cuatro se probó en el portal con
este código: esa prueba la corres tú (abajo, «Cómo probarlo»).
- **MSC** baja por la lista si la nave no está, sin pulsar nada, hasta encontrarla o hasta que no lleguen tarjetas
  nuevas.
- **CMA** pulsa «Cargar N siguientes resultados», por ese texto, las veces que haga falta, hasta encontrar la nave o
  hasta que el enlace desaparezca. Es el único clic nuevo antes de la guarda, y reemplaza el de la Nota H23.
- **El calce de CMA no se tocó, y tu freno no se cumplió** en lo que hay guardado: la nave que sale de Chile está en la
  tarjeta, como «Buque principal», y el comparador del programa (`_JS_CMA_RUTAS`, con el texto de toda la tarjeta)
  la encuentra. Es un solo caso medido (la misma fila en tres corridas), con los detalles abiertos.
- **HYUNDAI** prefiere la directa entre las salidas del mismo día; solo si todas tienen transbordo, decide el tránsito.
  En las dos listas guardadas, ahora elige la 6.ª (directa, 35 días de tránsito) y no la 5.ª (con transbordo, 33).
  Antes de pulsar, comprueba que la tarjeta siga siendo la directa elegida.
- **ONE** ya no pasa de 8 semanas: se quitó la prueba de una opción más larga.
- **La fecha de salida** no se cambia en ningún portal para buscar más lejos: no había nada que cambiar.
- `test_candado` no cambió.

## Veredicto del PASO 0, por parte del encargo

| Parte | Veredicto | Qué quedó |
|---|---|---|
| MSC: bajar por la lista | **CICLO** | `ff76fea` |
| CMA: «Cargar N siguientes resultados» | **CICLO**, con el texto que diste (no está en lo guardado) | `2044222`, y `922e91d` para sus motivos |
| CMA: ¿es el mismo «Mostrar más viajes» de hoy? | **DESCARTE:** no lo es (abajo) | El clic de la Nota H23 se reemplazó en `2044222` |
| CMA: dónde está la nave que sale de Chile, y contra qué compara el programa | **NOTA:** en la tarjeta, como «Buque principal»; el programa compara con el texto de toda la tarjeta. Tu freno no se cumple | Nada cambió en el calce |
| HYUNDAI: la directa primero | **CICLO** | `a37373f`, y `96a0d2b` para el clic |
| ONE: no pasa de 8 semanas | **CICLO** | `38aa08d` |
| No cambiar la fecha de salida en ningún portal | **NOTA:** ninguno la cambia para ampliar | Nada |
| La prueba con el lanzador de prueba | **PREGUNTA:** la corres tú | Sin correr |

## CMA · dónde está la nave, y contra qué compara el programa (tu freno)

**Qué hay guardado.** La lista de «Route choices» nunca quedó entera en `logs/`: `cma_f<fila>_rutas` se guarda desde
`50e3f04`, y ninguna corrida posterior llegó a la lista. Pero en 8 de los 44 HTML de CMA (la corrida del 24-09, en el
panel Reefer y en el paso sin objetivo; y las dos del 25-09, en el panel Reefer, la guarda y el Reefer guardado) sigue
en la página la tarjeta elegida, con sus detalles abiertos, dos veces (dos `.wrap-card`, ninguna dentro de la otra, con
la misma fecha de salida). Las tres corridas buscaron la misma nave: es **un solo caso**, y con una sola ruta.

**La tarjeta** (`div.wrap-card`), tapada:
- el origen: su fecha, el puerto chileno y su terminal;
- sus datos, en un `dl`: «Port Cut-off», **«Buque principal»** (una palabra), «Primer servicio» (tres palabras con una
  cifra: el nombre de un servicio, no de una nave) y «Ref. de viaje»;
- el destino, el tramo en camión, el tránsito, las emisiones y **«vía Callao»** (el transbordo);
- los botones «Seleccionar» y «Deseleccionar», y «Mostrar detalles».

**Los detalles** («Mostrar detalles», abiertos en esas páginas), en orden: el puerto chileno → el primer tramo, con su
«Buque», su servicio y su viaje → Callao → el transbordo → el segundo tramo, con otro «Buque» → el destino.

**Medido** (la nave de la fila sale del `log.txt` de la misma corrida, «CMA · Buscando nave '…' en Route choices», y
se usa solo en memoria). Las cuatro primeras filas, con las sondas propias (`cma_calce.py`, `cma_tramos.py` y
`cma_tramos_esqueleto.py`) en los 5 HTML del panel Reefer y de la guarda; la última, con el JavaScript del programa
(`cma_rutas_programa.py`) en los 8:

| Dónde | ¿Trae la nave de la fila? |
|---|---|
| «Buque principal» de la tarjeta | **Sí**, en los 5 HTML |
| «Primer servicio» | No |
| El «Buque» del primer tramo de los detalles (el que sale de Chile) | Sí |
| El «Buque» del segundo tramo (desde Callao) | No |
| El comparador del programa, `_JS_CMA_RUTAS` de `2044222` (la tarjeta de `getCard`, con `innerText`) | **Calza**, en los 8 HTML; su tarjeta llega a «Buque principal» a 3 niveles del botón |

Así, la nave que sale de Chile se ve en la tarjeta, no solo en «Mostrar detalles», y el comparador del programa la
encuentra: **tu freno no se cumple**, y el calce no se tocó. Con tres matices, que quedan en el residual:
- es un caso, con los detalles abiertos y una sola ruta: en la lista en vivo, los detalles están cerrados, y que
  «Buque principal» se vea igual se deduce de dónde está en la página, no está medido;
- si en otra ruta «Buque principal» fuera el buque del tramo desde Callao, la tarjeta no traería la nave que sale de
  Chile: esa ruta no calzaría, o, peor, calzaría una ruta donde la nave de la fila es solo el buque desde Callao, y el
  programa pulsaría la primera que calza;
- el programa compara con toda la tarjeta, no con «Buque principal»: una ruta cuyo «Primer servicio» trajera las
  palabras de la nave también calzaría. Calzar solo con «Buque principal» lo decides tú (pregunta 2); la nave medida
  es de una sola palabra, así que falta ver si el portal muestra el prefijo («CMA CGM …») cuando la fila lo trae.

## CMA · «Cargar N siguientes resultados» (`2044222`)

**Medido:**
- **No es el «Mostrar más viajes» de hoy.** El clic de la Nota H23 pulsaba, una vez, el primer `button` o `a` a la
  vista cuyo texto trajera «mostrar más», «ver más», «show more» o «más viajes»: con esa expresión nunca habría pulsado
  «Cargar N siguientes resultados». Ninguno de los 44 HTML de CMA trae un `button` o `a` que calce con una u otra
  expresión (`cma_mas.py`), y en `logs/` el clic nunca se pulsó: en las corridas que llegaron a la lista, la nave
  estaba de entrada.
- **El enlace no está en lo guardado.** Los 44 HTML son de después de elegir la ruta (la lista queda con la tarjeta
  elegida), y las 39 capturas de la lista y de sus pasos vecinos son de la ventana (1929×1044): el enlace va al final.
  El OCR, además, lee
  muy poco en ellas (1 «Seleccionar» por captura como mucho). El texto es el que diste.
- **La fecha de cada tarjeta**, para decir hasta dónde buscó: la primera `.date` de la tarjeta, con la forma
  «Lunes, 05-oct-2026»: el día de la semana y el mes en español (medidos: lunes, miércoles, viernes, oct, nov), en las
  40 fechas de las 10 `.wrap-card` de los 5 HTML del panel Reefer y de la guarda (`cma_fechas_forma.py`). Es la fecha
  de la tarjeta elegida; la de la lista no está medida.

**Cambio.** Si la nave no está en la lista, `_cma_seleccionar_itinerario`:
1. cuenta las rutas (`_JS_CMA_CONTAR`: los «Seleccionar» o «Deseleccionar» a la vista);
2. busca el único enlace o botón a la vista cuyo texto entero es «Cargar N siguientes resultados», con cualquier N
   (`CMA_CARGAR_MAS`, `_cma_enlace_mas`); si hay dos, no pulsa ninguno;
3. lo pulsa con clic real y espera hasta `CMA_ESPERA_MAS` (20 s, hipótesis) a que haya más rutas (`_cma_ampliar`);
4. deja la evidencia de la lista nueva (`cma_f<fila>_rutas_mas`, `_rutas_mas2`…), vuelve a leerla, y repite hasta
   encontrar la nave, hasta que el enlace desaparezca o no lleguen rutas nuevas, o hasta el tope `AMPLIAR_MAX` (12).

Si la nave no aparece, el aviso dice hasta qué fecha buscó y por qué dejó de cargar: «CMA: nave '…' no disponible en el
portal: busqué hasta el DD-MM-AAAA, la última salida que mostró el portal, y …», con «ya no vi el enlace «Cargar …
siguientes resultados»» (`CMA_SIN_ENLACE`: el enlace desapareció, o nunca tuvo ese texto), «pulsé «Cargar … siguientes
resultados» y no llegaron rutas nuevas en 20 s», o el tope (`922e91d`; hasta `2044222`, los dos primeros decían «el
portal no deja ampliar más la búsqueda»). Sin palabras de nave en la fila, no pulsa nada. El calce y la regla de elegir
la primera tarjeta que calza no cambiaron.

## MSC · bajar por la lista (`ff76fea`)

**Medido:** en los 5 `log.txt` de MSC con itinerarios (del 21 al 26-09; `msc_cargados.py`), al cargar la lista ya
había **25 a 27 itinerarios con su «Select» a la vista** (`_JS_MSC_COUNT_SCHED`, que cuenta solo los dibujados), antes
de bajar: según tú, en pantalla se ven 4 o 5, pero el resto ya está en la página, y el programa los lee. En el HTML de
la guarda, 26 o 27 tarjetas, de +2 a +84 días (encargo 32). Si al bajar llegan más, **no está medido**.

**Cambio.** Si la nave no está en lo que leyó, `reservar_msc`:
1. baja por la lista con `_JS_MSC_BAJAR`, sin pulsar nada: lleva al final cada ancestro de las tarjetas que tenga
   desplazamiento, y la ventana;
2. espera hasta `MSC_ESPERA_MAS` (15 s, hipótesis) a que haya más tarjetas con su «Select» a la vista (`_msc_bajar`);
3. vuelve a leer la lista, y repite hasta encontrar la nave, hasta que no lleguen tarjetas nuevas, o hasta el tope
   `AMPLIAR_MAX` (12).

Si la nave no aparece, el REVISAR dice hasta qué fecha buscó. `log.txt` dirá si llegaron más: «búsqueda ampliada: N ->
M itinerarios».

## HYUNDAI · la directa primero (`a37373f`)

**Medido** en las 2 listas guardadas del 26-09 (`hmm_esqueleto.py`, `hmm_directa.py`): cada tarjeta dice si es directa
en `div.place-transshipment > .transshipment-line > .mid-state`, con un solo texto, «Direct» o «Transshipment». Las 6
tarjetas de cada lista: directa, transbordo, directa, transbordo, transbordo, directa. Las dos que traen la nave de la
fila salen el mismo día (+27): la 5.ª, con transbordo, con 33 días de tránsito; la 6.ª, directa, con 35.

**Cambio.** `_JS_HMM_TARJETAS` lee `directa` del único `.mid-state` de la tarjeta (true, false, o null si no hay uno
solo o dice otra cosa). Antes de la próxima salida, `_hmm_directas_primero` mira las del día de la próxima salida: si
alguna es directa, descarta las con transbordo de ese día y lo anota («2 salidas de la nave salen el DD-MM-AAAA:
prefiero la directa; descarto 1 con transbordo»); si todas tienen transbordo, o todas son directas, decide el tránsito,
como antes. Una tarjeta que no dice si es directa cuenta como con transbordo. La directa solo desempata el mismo día:
una con transbordo que sale antes gana. La regla común de la próxima salida no cambió.

Con esto, en las dos listas guardadas elige la 6.ª (directa, 35 días de tránsito); hasta `924485a` elegía la 5.ª
(con transbordo, 33 días). Antes de pulsar su «Book Now», `_JS_HMM_CLIC_TARJETA` vuelve a leer la tarjeta y comprueba,
además de su «1st Vessel» y su salida, que sea directa o no como la elegida (`96a0d2b`; lo pidió la revisión del
informe: dos tarjetas del mismo día y la misma nave pueden diferir solo en eso).

## ONE · no pasa de 8 semanas (`38aa08d`)

Se quitó la ampliación que agregó `05cfdb7`: si la nave no estaba, abría el selector «N weeks» y probaba una opción de
más de 8 semanas (`_JS_ONE_SEMANAS`, `_one_semanas`, `_one_ampliar`, `_one_esperar_mas`, y su entrada en la foto de
`test_clics`). Quedan `_JS_ONE_FECHAS` y `_one_fechas`, del mismo commit, para decir hasta qué fecha buscó. ONE sigue
eligiendo 8 semanas antes de buscar, por la nota de la planilla. Si la nave no está, REVISAR con «busqué hasta el
DD-MM-AAAA, la última salida que mostró el portal, y no amplío más allá de las 8 semanas que pide la nota de la
planilla» (`ONE_SOLO_8`).

## La fecha de salida

Ningún portal mueve la fecha de salida para buscar más lejos. Las que escriben una fecha escriben la de siempre: MSC,
hoy, o el día de carga (o el de retiro) si es posterior; CMA, HYUNDAI y MAERSK, el día de carga si la fila lo trae
(MAERSK, si no, «Select tomorrow»). No se tocó.

## Lo nuevo sobre el HTML guardado (`validar_e33.py`)

Corre lo del commit `2044222` sobre los HTML guardados, sin red y sin el JavaScript de la página. Su control (una
tarjeta sintética de cada naviera) aborta si no da lo esperado. Los dos commits siguientes no cambian lo que mide.

- **HYUNDAI:** en las dos listas, `directa` por tarjeta da directa, transbordo, directa, transbordo, transbordo y
  directa; traen la nave la 5.ª y la 6.ª; `_hmm_directas_primero` y la próxima salida eligen la 6.ª, la directa, y lo
  anotan.
- **CMA:** en los 5 HTML del panel Reefer y de la guarda, `_JS_CMA_FECHAS` lee las 2 `.wrap-card` y
  `_cma_fecha_tarjeta` lee sus 2 fechas, iguales (+17 o +18 días); `_JS_CMA_CONTAR` da 1 ruta; `_cma_enlace_mas`, 0
  enlaces: la lista ya estaba cerrada.
- **MSC:** en los 4 HTML de la guarda, `_JS_MSC_BAJAR` encuentra 26 o 27 tarjetas, las mismas que lee `_JS_MSC_NAVES`.

**Lo que no prueba:** que el portal responda (que MSC cargue más al bajar, que el enlace de CMA exista con ese texto y
cargue más rutas). Eso es la corrida en vivo.

## Cómo probarlo (con el lanzador de prueba, candado cerrado)

1. Cierra el panel si está abierto y ábrelo con `Iniciar AQUASHIELD.bat` (nunca con el de emisión).
2. Corre, con el candado cerrado, una fila por naviera; para ver la ampliación, con una nave que no esté entre las
   primeras salidas.
3. Lo que puede aparecer en `log.txt`:
   - **MSC:** «bajo por la lista de itinerarios para que MSC cargue más» y «búsqueda ampliada: N -> M itinerarios»;
   - **CMA:** «CMA · pulso «Cargar … siguientes resultados» para buscar la nave» y «búsqueda ampliada: N -> M rutas»;
     si deja de cargar, «ya no vi el enlace…» o «pulsé… y no llegaron rutas nuevas en 20 s»; y en la carpeta,
     `cma_f<fila>_rutas.html` (la lista tal como carga, por primera vez) y `_rutas_mas`, `_rutas_mas2`…;
   - **HYUNDAI:** «… prefiero la directa; descarto N con transbordo»;
   - si la nave no aparece: REVISAR con «busqué hasta el DD-MM-AAAA…».
4. Con eso mido lo que falta: si MSC carga más al bajar, el texto real del enlace de CMA y su lista entera, y el calce
   de CMA en más de un caso.

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\correr.py --mutaciones --filtro TestOne
python tests\correr.py --mutaciones --filtro TestHyundai
python tests\correr.py --mutaciones --filtro TestNaveCompleta
python tests\correr.py --mutaciones --filtro TestMsc
python tests\correr.py --mutaciones --filtro TestCma
python tests\correr.py --mutaciones --filtro TestEvidenciaRutasCma
python tests\correr.py --mutaciones --filtro TestFotoDeClicsGenericos
python tests\correr.py --mutaciones --filtro TestCadaReservadorLaDeja
python tests\correr.py --todo
```

Las sondas son de solo lectura y no se versionan, porque leen datos reales. Quedaron en `scratchpad\e33`, que puede
limpiarse; sin ellas, estos números no se re-miden. Todas tienen un control positivo que aborta:
- **`cma_etiquetas.py`:** las etiquetas de la lista de rutas en cada HTML de CMA.
- **`cma_tarjeta.py` y `cma_tramos_esqueleto.py`:** el esqueleto tapado de la tarjeta elegida y de sus tramos.
- **`cma_calce.py` y `cma_tramos.py`:** dónde está la nave de la fila (la del `log.txt` de la corrida), por campo y por
  tramo, y cuántas naves distintas hay entre las corridas.
- **`cma_rutas_programa.py <commit>`:** el calce con el propio `_JS_CMA_RUTAS` del programa, y las `.wrap-card`.
- **`cma_fechas_forma.py`:** las palabras y la forma de las fechas de la tarjeta.
- **`msc_cargados.py`:** los «itinerarios cargados» de los `log.txt` de MSC.
- **`cma_mas.py`:** los `button` o `a` que calzan con el clic de la Nota H23 o con «Cargar N siguientes resultados».
- **`cma_ocr.py`:** las etiquetas en las capturas de la lista, con OCR.
- **`hmm_esqueleto.py` y `hmm_directa.py`:** las tarjetas de HYUNDAI y su «Direct» o «Transshipment».
- **`validar_e33.py <commit>`:** lo nuevo de ese commit sobre el HTML guardado.

En PowerShell, cada una se corre con `$env:PYTHONIOENCODING='utf-8'` y después
`python "$env:TEMP\claude\C--dev-Agendamiento-Reservas\<sesión>\scratchpad\e33\<sonda>.py"`.

## NO retroceder (pieza 2)

- **No vuelvas a pulsar en CMA «el primero» con «mostrar más» o «ver más»:** el enlace va por su texto entero, y uno
  solo.
- **No amplíes MSC con un clic:** baja por la lista.
- **No vuelvas a elegir en HYUNDAI la de menor tránsito si la otra del mismo día es directa,** ni a pulsar su «Book
  Now» sin comprobar que sea la directa elegida.
- **No vuelvas a ampliar ONE más allá de 8 semanas.**
- **No cambies el calce de CMA sin tu decisión:** hoy compara con el texto de toda la tarjeta.
- **No vuelvas a decir en CMA «el portal no deja ampliar más» cuando solo no se vio el enlace.**

## Universo y cobertura (pieza 3)

- **`logs/`:** 15 carpetas, todas con `log.txt`; ninguna nueva desde el 26-09.
- **CMA:** 44 HTML y 39 capturas de la lista y de sus pasos vecinos; 8 HTML con la tarjeta elegida (3 corridas, 1 nave
  distinta), 5 de ellos del panel Reefer y de la guarda; 0 HTML con la lista entera; 40 fechas en sus 10 `.wrap-card`.
- **MSC:** 5 `log.txt` con «itinerarios cargados» (9 valores: 25 a 27).
- **HYUNDAI:** 2 listas de 6 tarjetas, las 12 con un solo `.mid-state`.
- **No medido:** el enlace «Cargar N siguientes resultados» y la lista entera de CMA, con sus fechas; si MSC carga más
  al bajar; el calce de CMA en otras rutas y con los detalles cerrados.

## Defectos de instrumento cazados (pieza 4)

1. **Las filas de CMA de esas corridas ya no están en las planillas** (`cma_tarjeta.py` daba «fila con nave: False»):
   la nave se tomó del `log.txt` de la misma corrida.
2. **`cma_tramos.py` no veía los tramos:** buscaba `dl > dt`, y cada `dt` está dentro de un `div` del `dl`. Dio 0
   tramos; se cambió a buscar los `dt` del tramo.
3. **`hmm_directa.py` no veía «Direct» ni «Transshipment»:** los buscaba dentro de `.transshipment-line-day`, y están
   en su hermano `.mid-state`. Se buscaron primero por su texto y sus ancestros.
4. **El OCR casi no lee las capturas de CMA** (1 «Seleccionar» como mucho, 0 «Buque principal»): no sirve para decir
   que algo no está. Se usó solo para confirmar que son de la ventana.
5. **Cuatro anclas de mutaciones repetidas**, cazadas por `anclas.py` en la copia antes de cada gate: en HYUNDAI, una
   línea igual a una de `_proxima_salida`; en MSC, tres iguales a las de MAERSK y al calce de MSC. Se renombraron las
   variables.
6. **Una prueba nueva de HYUNDAI caía sin motivo:** `elegir_hmm` dejaba todas las corridas de las pruebas en la misma
   carpeta, y el `log.txt` traía lo de otras. Ahora cada prueba tiene la suya.
7. **Un filtro mal nombrado:** `TestNaveCompleta` está en `test_ayudantes`, no en `test_clics`.
8. **La herramienta Bash convierte `\\` en `\`:** un ajuste escrito en un heredoc no calzó; se pasó a archivos escritos
   con Write.
9. **Cuatro líneas de más de 120 columnas** en el código, cazadas con `git diff` después de lanzar la compuerta de CMA:
   se detuvo, se partieron y se volvió a lanzar.
10. **`reacomodar_md.py` escribe CRLF** y reacomodó dos párrafos de `CLAUDE.md` que el encargo no toca: se volvió a LF
    y esos dos párrafos se devolvieron a su texto de git (`restaurar_claude.py`).
11. **Una mutación de CMA no mordía una de sus dos pruebas** (`cma-cargar-con-las-mismas` en
    `test_y_otra_tras_cada_carga`, donde «>» y «>=» dan lo mismo): quedó solo con la prueba que la distingue, y la
    compuerta de CMA se volvió a correr.
12. **El calce de CMA se había medido con la tarjeta de la sonda, no con la del programa:** `cma_calce.py` toma el menor
    ancestro con «Buque principal»; `_JS_CMA_RUTAS` arma la suya con `getCard` y compara su `innerText`. Lo cazó la
    revisión del informe; se corrió el JavaScript del programa (`cma_rutas_programa.py`) y dio lo mismo.
13. **`msc_cargados.py` contaba en el texto crudo una tarjeta de MSC más que el DOM** (27 y 28 contra 26 y 27): esas se
    cuentan con el JavaScript del programa (`validar_e33.py`), y la sonda quedó solo con los `log.txt`.
14. **El censo completo sobre `2044222` se detuvo** para correrlo sobre el último commit de código.

## Premisas del encargo contrastadas (pieza 5)

- **«MSC: las demás naves aparecen al bajar en la lista»:** en pantalla se ven 4 o 5, pero la página ya trae 25 a 27
  con su «Select» dibujado, y el programa ya los lee sin bajar. Si al bajar llegan más, no está medido: el cambio está
  hecho igual, como lo decidiste.
- **«CMA: medir si es el mismo "Mostrar más viajes" que se pulsa hoy»:** no lo es (arriba).
- **«La tarjeta de CMA muestra "Buque principal", "Primer servicio" y rutas vía Callao o Chancay»:** sí, en el caso
  guardado (vía Callao). «Primer servicio» es un servicio, como dijiste.
- **«La nave de la fila es siempre la que sale de Chile»:** en el caso guardado, es el primer tramo, y es también el
  «Buque principal» de la tarjeta.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| El calce de CMA compara con el texto de toda la tarjeta, no con «Buque principal» | Tu freno no se cumplió en el caso medido; cambiarlo lo decides tú | …decides calzar solo con «Buque principal» (pregunta 2) |
| El calce de CMA está medido en un solo caso | Las tres corridas buscaron la misma nave | …una corrida deja `cma_f<fila>_rutas` con otras rutas |
| El texto «Cargar N siguientes resultados» no está medido; si es otro, CMA no pulsa nada y queda REVISAR con la fecha y «ya no vi el enlace…» | Ninguna corrida guardó la lista entera | …la corrida en vivo deja `cma_f<fila>_rutas.html` |
| CMA: si «Cargar» reemplazara la lista en vez de sumarle, las rutas no aumentarían y dejaría de cargar sin leer la nueva («pulsé… y no llegaron rutas nuevas») | Se espera que sume, como dice su texto; no está medido | …`log.txt` dice «no llegaron rutas nuevas» con el enlace todavía a la vista |
| CMA: el calce por toda la tarjeta podría elegir una ruta donde la nave de la fila es solo el buque desde Callao | En el caso medido, «Buque principal» es la nave que sale de Chile | …decides calzar solo con «Buque principal», o aparece esa ruta |
| CMA: la fecha para «busqué hasta el…» es la de la tarjeta elegida; la de la lista no está medida. Si no se lee, el motivo dice «el portal no mostró ninguna salida con fecha» | No hay HTML de la lista | …la corrida en vivo deja `cma_f<fila>_rutas.html` |
| «Las veces que haga falta» y «hasta que no aparezcan tarjetas nuevas» tienen el tope `AMPLIAR_MAX` (12) y una espera por tanda (choque 6) | Un tope de seguridad, como en MAERSK | …una lista real necesita más de 12 cargas |
| CMA sigue eligiendo la primera tarjeta que calza, no la próxima salida | Falta el HTML de su lista | …ese HTML llega |
| Si MSC carga más al bajar, no está medido | Hace falta el portal | …la corrida en vivo lo muestra en `log.txt` |
| `MSC_ESPERA_MAS` (15 s) y `CMA_ESPERA_MAS` (20 s) son hipótesis; en el peor caso, 12 esperas: 3 y 4 minutos por fila | No hay medición; la nave suele estar entre las primeras cinco | …la corrida en vivo mide cuánto tardan |
| HYUNDAI: una tarjeta sin `.mid-state` cuenta como con transbordo | Las 12 medidas lo traen | …aparece una sin él |
| HYUNDAI: `_hmm_directas_primero` compara las tarjetas por su contenido (`not in`), no por su índice | Hoy cada una trae su `i`, distinto | …se mezclan dos lecturas de la lista |
| `_JS_CMA_CONTAR` cuenta «Seleccionar» y «Deseleccionar» a la vista | Así lee las rutas `_JS_CMA_RUTAS` | …el portal muestra los dos en una misma tarjeta |
| CMA: si el enlace fuera un botón dentro de un `a` (dos nodos con el mismo texto), `_cma_enlace_mas` vería dos y no pulsaría ninguno: REVISAR con la fecha | Falla sin clic; la forma del enlace no está medida | …`log.txt` dice «había 2 enlaces «Cargar … siguientes resultados»» |
| MSC: `_msc_bajar` compara las tarjetas con «Select» con todos los «Select» a la vista de la página (`_JS_MSC_COUNT_SCHED`); un «Select» fuera de las tarjetas contaría como una nueva | Al cargar, las dos cuentas dieron lo mismo (25 a 27 y 26 o 27); a lo más, 12 bajadas sin sentido y el motivo del tope | …`log.txt` dice «bajé por la lista 12 veces, el tope» |
| MSC: si la nave está pero su clic falla, el REVISAR dice «no está en MSC», sin la fecha | Era así antes; el clic no cambió | …prefieres otro motivo |
| Dos párrafos de `CLAUDE.md` con líneas de más de 120 (el puerto de COSCO y las credenciales) | Ya estaban así; el encargo no los toca | …un encargo los reescribe |
| ONE: `ONE_SOLO_8` dice «no amplío más allá de las 8 semanas», pero no comprueba que el selector haya quedado en 8: `_set_weeks_one` solo lo anota en `log.txt` | Era así antes | …`log.txt` dice «no encontró opción 8 semanas» |
| La prueba con el lanzador de prueba | La corres tú (arriba) | …me dices que corrió |
| Los residuales de `CICLO-ampliar-la-busqueda.md` que este encargo no tocó (MAERSK, COSCO, el modal de HYUNDAI) | Sin evidencia nueva | …según ese informe |

**Lo que este encargo cierra del anterior:** el freno de MSC y el de CMA (la opción de ampliar), la pregunta de ONE
(se queda en 8), la de HYUNDAI (la directa) y la de las fechas (no se cambian).

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v14**.
- **PASO 0 con sus cuatro valores** (CICLO, NOTA, DESCARTE y PREGUNTA): salieron los cuatro.
- **FRENAR cuando la decisión es de negocio y no de medición:** el calce de CMA; tu freno no se cumplió, así que se
  reporta lo medido y el cambio queda en tus manos.
- **Re-medir contra HEAD antes de diseñar:** lo guardado se midió con sondas propias y, después de la revisión del
  informe, con el JavaScript del programa (`cma_rutas_programa.py`); lo nuevo, con el de su commit (`validar_e33.py`).
- **Control positivo que aborta:** en cada sonda.
- **Todo salto silencioso lleva contador:** 44 HTML de CMA, 8 con la tarjeta (5 en las sondas propias), 0 con la
  lista; 39 capturas; 1 nave distinta.
- **La unidad la fija el sujeto:** el calce de CMA se contó por caso (1 nave), no por HTML (8) ni por corrida (3).
- **Todo registro es una hipótesis:** «MSC muestra 4 o 5» es lo que se ve; la página trae 25 a 27 (pieza 5).
- **El negativo tiene que morder:** en cada commit, el censo filtrado; al cerrar, el censo completo. Uno no mordía una
  de sus pruebas (pieza 4, 11).
- **El cambio y su guardián en la misma operación:** cada commit trae sus pruebas y mutaciones.
- **Fuente única:** `_hasta_donde_busque`, `NO_AMPLIA_MAS` y `AMPLIAR_MAX` para MSC y CMA; la regla común de la próxima
  salida no se tocó (HYUNDAI filtra antes).
- **Cada reemplazo afirma su viejo una vez; el EOL se preserva.**
- **Verificación adversarial:** dos revisiones del código y la de este informe.
  - Las dos del código aprobaron, sin nada grave. La de ONE y HYUNDAI dudó de que el `.mid-state` describa el viaje
    entero (medido: uno solo por tarjeta, en las 12) y dejó la comparación por contenido en el residual. La de MSC y
    CMA corrigió un docstring y dejó tres riesgos en el residual (el enlace anidado, el «Select» fuera de las tarjetas
    y el motivo cuando falla el clic de MSC).
  - La del informe cazó que el calce de CMA se había medido con la tarjeta de la sonda (se volvió a medir con la del
    programa: pieza 4, 12), dos cosas del código (el clic de HYUNDAI sin mirar la directa, `96a0d2b`; y los motivos de
    CMA, `922e91d`), riesgos que faltaban en el residual y varias cifras y textos.
- **Choques entre reglas:**
  1. **«MSC: bajar hasta que no aparezcan tarjetas nuevas» contra lo medido:** la página ya trae 25 a 27. Se hizo igual,
     como lo decidiste; `log.txt` dirá si bajar sirve.
  2. **«Medir si es el mismo "Mostrar más viajes"» contra «el único clic nuevo es el enlace»:** no es el mismo, y dejar
     los dos serían dos clics; el de la Nota H23 se quitó y el enlace lo reemplaza.
  3. **El FRENA SI de CMA contra «completar la búsqueda de CMA»:** el freno protege el calce, no el enlace. El freno no
     se cumplió, pero igual no se tocó el calce: el encargo no lo pide.
  4. **La directa en HYUNDAI contra la regla común de la próxima salida:** se aplica solo a HYUNDAI, antes de la regla y
     sin cambiarla. Dos directas del mismo día se desempatan por el tránsito, como dos con transbordo.
  5. **«Todo se prueba con el lanzador de prueba» contra lo que hago yo:** la corrida entra a los portales con las
     credenciales guardadas; la corres tú.
  6. **«Las veces que haga falta» y «hasta que no aparezcan tarjetas nuevas» contra una corrida que no termine:** MSC y
     CMA tienen el tope `AMPLIAR_MAX` (12), el mismo de MAERSK, y cada tanda espera lo suyo; CMA corta también si pulsó
     y no llegaron rutas en 20 s, o si hay dos enlaces. Cada corte lo dice el motivo.

Reglas del módulo: casos sintéticos; la sonda de secretos antes de cada commit; nada de `logs/` en el repo; el único
clic nuevo antes de la guarda, el enlace de CMA, por su texto; `test_candado` sin cambios; los textos en español con
tuteo.

## Entregable (pieza 8)

- **Este `.md`:** no se convirtió en página; se leyó como texto.
- **`CLAUDE.md` al día,** en el mismo commit.

**La red por commit:**

| Commit | Pruebas | Mutaciones | Pares |
|---|---|---|---|
| `924485a` (base) | 402 | 1053 | 1275 |
| `38aa08d` (ONE) | 400 | 1042 | 1264 |
| `a37373f` (HYUNDAI) | 402 | 1052 | 1274 |
| `ff76fea` (MSC) | 405 | 1061 | 1283 |
| `2044222` (CMA) | 410 | 1078 | 1302 |
| `96a0d2b` (HYUNDAI: el clic) | 410 | 1080 | 1304 |
| `922e91d` (CMA: los motivos) | 410 | 1082 | 1307 |

Contada de git con `scratchpad\e26\red_por_commit.py`, del encargo 26.

**Gates.** En cada uno, la suite completa pasó con 0 cambios en los originales, y la sonda de secretos dio 0 sobre el
árbol y sobre lo agregado con `git add`. Todas las mutaciones de cada censo muerden.

| Commit | Suite completa | Censos filtrados (mutaciones y pares) |
|---|---|---|
| ONE, `38aa08d` | 400 en verde | `TestOne`: 84 y 101; `TestFotoDeClicsGenericos`: 29 y 55 |
| HYUNDAI, `a37373f` | 402 en verde | `TestHyundai`: 68 y 76; `TestNaveCompleta`: 31 y 47 |
| MSC, `ff76fea` | 405 en verde | `TestMsc`: 55 y 66 |
| CMA, `2044222` | 410 en verde, tres veces: tras partir las líneas largas, tras ajustar una mutación y tras el docstring (pieza 4, 9 y 11) | `TestCma`: 76 y 95; `TestEvidenciaRutasCma`: 4 y 8; `TestFotoDeClicsGenericos`: 29 y 55; `TestCadaReservadorLaDeja`: 24 y 49; `TestHyundai`: 68 y 76 |
| HYUNDAI, el clic, `96a0d2b` | 410 en verde | `TestHyundai`: 70 y 78 |
| CMA, los motivos, `922e91d` | 410 en verde | `TestCma`: 78 y 98; `TestEvidenciaRutasCma`: 5 y 10 |

**Censo completo** sobre `922e91d`, el último commit de código: 1082 mutaciones y 1307 pares mutación-prueba, sobre 410
pruebas. Los 1307 pares muerden, no hay pruebas sin mutación, el control (la copia sin mutar) pasa y hay 0 cambios en
los originales. Corrió el 27-09, de 11:44 a 12:28. El de `2044222` se detuvo sin terminar, porque después vinieron dos
commits de código (pieza 4, 14).

## Qué decides tú

1. **Corre la prueba** con el lanzador de prueba (arriba) y avísame: con lo que deje en `logs/` mido la lista entera
   de CMA, el texto real de su enlace y si MSC carga más al bajar.
2. **CMA:** ¿calzo la nave solo con «Buque principal» de la tarjeta, en vez de con toda la tarjeta? En el caso medido es
   la nave que sale de Chile, pero es un solo caso, y de una palabra: si la fila trae «CMA CGM …», falta ver si el
   portal muestra el prefijo.
3. **CMA:** ¿aplico la próxima salida, como en las otras cinco, cuando tenga el HTML de su lista?
