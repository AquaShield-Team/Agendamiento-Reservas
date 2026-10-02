# CICLO · MAERSK en la prueba de hoy y la fila sin ruta: por qué falló MAERSK (sin corregir), y la fila sin puerto de carga o sin destino queda NO ENVIADA sin entrar al portal

**Módulo:** Agendamiento Reservas · **Encargo 42** · **Fecha:** 2026-09-30 · **Método:** skill `metodo-ciclo` v14 ·
**Commits** (locales; el repo no tiene remoto, así que no hay push que entregar):
- `509a83c`: la fila con nave y sin puerto de carga o sin destino queda NO ENVIADA sin entrar al portal;
- `0c2c070`: sin una sugerencia elegida en el origen, el destino o el lugar de entrega, NO ENVIADA;
- `e49461f`: sin una sugerencia que elegir, la evidencia de la lista queda igual;
- `3d9923e`: lo que encontró la revisión de código (una celda sin una palabra tampoco trae la ruta, y lo demás);
- `5bb3bf0`: lo que encontró la revisión del informe (la palabra del puerto de carga se pide sin contar el país);
- `7ca9a98`: lo que encontró la revisión final («CHILE X» tampoco trae el puerto, y la prueba ve todo lo que se hace en
  la página);
- y el de este informe, con `CLAUDE.md` al día.

**Base: `C:\dev\Agendamiento Reservas` @ `e02653c` · árbol limpio** (pieza 9). Lo medido sale de los `log.txt`, el HTML
y las capturas (con OCR, sin mirarlas) de las dos corridas de hoy, de las corridas de la fila 10 del 27-09 y del 29-09,
de las 8 listas de salidas de MAERSK guardadas, de los 97 bloques de reserva de `logs/` y del código en `e02653c`.

> Datos reales solo en lectura. Las sondas leen los `log.txt`, el HTML, las capturas y las planillas en su lugar, sin
> copiarlos, e imprimen formas, cuentas, fechas y booleanos: en este informe no van nombres de naves, viajes, puertos,
> países de una fila, partes, códigos ni números de reserva. El único país que nombro es Chile, que ya está en el
> código. No se miró ninguna captura.

**Resumen.**
- **MAERSK falló por dos causas distintas, una en cada corrida de hoy.** No las corregí: el encargo pedía el diagnóstico
  (preguntas 1 y 2).
  - **A las 15:21, SIN-CUPO, lo más probable por el destino.** Con la misma celda que el 27-09, eligió «ciudad + 1
    palabra, país» en vez de «ciudad, país», y la búsqueda volvió vacía. `_mk_ciudad` toma la primera sugerencia de tipo
    «Container Yard», y en la lista del portal esa iba antes que la del 27-09, también Container Yard. Es lo mismo que
    el 29-09. Que con la otra la búsqueda trajera la nave hoy no está probado: así fue el 27-09.
  - **A las 15:31, con la fila 10 ya cambiada (otro destino y otra nave), NO ENVIADA por un empate.** La búsqueda
    encontró la nave, pero su salida vino en 3 tarjetas idénticas (el mismo texto entero y el mismo HTML, byte a byte),
    y el tránsito no desempata. En 7 de las 8 listas de salidas guardadas (todas menos la del 24-09) hay tarjetas
    repetidas así.
- **Las listas de sugerencias ya se miden,** y responden la pregunta 1 del encargo 41:
  - el país no viene aparte: la raíz shadow de cada opción trae el tipo de lugar y su sigla (CY o SD), no el país;
  - cada sugerencia Container Yard viene dos veces con el mismo texto, una Container Yard y otra Store Door; las demás,
    una vez;
  - la celda del origen no trae el país, y 7 sugerencias distintas tienen la forma de tu regla. Una regla medida en las
    4 listas elige en cada una la sugerencia con que la búsqueda encontró la nave, el 27-09 o hoy a las 15:31 (pregunta
    1).
- **Los cuatro avisos de la evidencia:** 0 de cada uno en las 15 listas de hoy, salvo «una captura sin la lista»: 5
  capturas que el OCR no confirma (su HTML sí trae la lista; pregunta 4). **Las otras cinco navieras** quedaron
  OK-EJEMPLO.
- **La fila sin puerto de carga o sin destino** queda NO ENVIADA sin entrar al portal, con tu motivo, en las seis
  navieras y por los dos caminos: el panel, que lee con `leer_filas`, y la consola, con `leer_reservas` (commit 1; los
  lectores no cambian). **Si el ayudante de origen, destino o lugar de entrega no elige sugerencia**, NO ENVIADA, y
  ninguna naviera sigue (commit 2). **Sin sugerencia que elegir, la evidencia queda igual**, con el mismo nombre (commit
  3). Y ninguno de los siete ayudantes escribe ni pulsa con el texto vacío: medido, cada uno pulsaba una sugerencia a la
  vista (la primera; el lugar de entrega de CMA, la primera «ramp»).
- **Tres revisiones encontraron lo que se me había pasado, y lo corregí (commits 4 a 6).** Lo más importante: «-», «X»,
  «CHILE», «X CHILE» o «CHILE X» en el puerto de carga pasaban como si trajeran la ruta. Ahora la regla pide una palabra
  antes de la primera coma, y en el puerto de carga, sin contar «CHILE» en ninguna posición. Lo que queda está en el
  residual.
- **Tu FRENA SI no se cumple:** de las 66 reservas de `logs/` que llegaron a la guarda, ninguna habría quedado NO
  ENVIADA con las reglas nuevas, y las seis navieras usan el puerto de carga y el destino.
- **Sin clics nuevos** (182 antes y después), y `test_candado` no cambia. La red queda en 537 pruebas y 1586 mutaciones
  en 1911 pares, y en el censo completo sobre `7ca9a98` muerden todas.
- **Nada de esto se probó en el portal.**

## Veredicto del PASO 0, por parte del encargo

| Parte | Veredicto | Qué quedó |
|---|---|---|
| Por qué falló MAERSK en la prueba de hoy | **NOTA:** dos causas medidas, una por corrida | Sin corregir (preguntas 1 y 2) |
| Las listas de MAERSK: cuántas sugerencias, si el país viene aparte y cuántas cumplen la regla | **NOTA:** medido; el país no viene aparte | Pregunta 1 |
| Comparar con el 27-09 | **NOTA:** misma celda; eligió otra opción de la lista | — |
| Los cuatro avisos de la evidencia | **NOTA:** 0, salvo 5 capturas sin confirmar | Pregunta 4 |
| Las otras cinco navieras | **NOTA:** OK-EJEMPLO las cinco | — |
| La fila con nave y sin puerto de carga o sin destino, NO ENVIADA sin entrar al portal | **CICLO** | `509a83c` |
| El ayudante que no eligió sugerencia, NO ENVIADA, y ninguna naviera sigue | **CICLO** | `0c2c070` |
| La evidencia cuando no hay sugerencia que elegir | **CICLO** | `e49461f` |
| Lo que encontró la revisión de código (una celda sin una palabra, lo que devuelve el ayudante que no eligió, y lo demás) | **CICLO** | `3d9923e`; residual, en la pieza 6 |
| Lo que encontró la revisión del informe (la palabra del puerto de carga, sin el país; y cifras del informe) | **CICLO** | `5bb3bf0`; residual, en la pieza 6 |
| Lo que encontró la revisión final («CHILE X», «№» y lo que la prueba no veía en la página) | **CICLO** | `7ca9a98`; «CL», pregunta 6 |
| Tu FRENA SI | **NOTA:** no se cumple (0 de 66 reservas en la guarda; las seis usan puerto y destino) | — |
| Sin clics nuevos; `test_candado` no cambia | **NOTA:** se cumple (182 antes y después) | Sin cambios |

## Parte 1 · MAERSK en la corrida de prueba de hoy (solo diagnóstico)

### Las corridas de hoy

En `logs/` hay tres carpetas de hoy: un inicio de sesión (15:10) y dos corridas del panel, las dos con la hoja de todas
las navieras.
- **15:21:** seis reservas, una por naviera, de la fila 5 a la 10; la de MAERSK es la fila 10.
- **15:31:** solo MAERSK, la fila 10, después de que la planilla cambió: la de la raíz se guardó a las 15:30:59, y el
  panel recibió su copia a las 15:31:13. Entre las dos corridas, la fila 10 cambió su celda de destino, lo que se
  escribió en el destino y su nave (comparados normalizados, sin imprimirlos).
- **Las dos dejaron las listas** (`mk_f10_origen` y `mk_f10_destino`). El panel corría código del commit `448e3e4` o
  posterior: ONE anota la sugerencia que pulsó con su texto, y eso lo agregó `448e3e4`. Lo más probable es que fuera el
  de `e3e0a76`, el último commit que cambió `AQUASHIELD.py` antes de las corridas (a las 12:49; el siguiente, `509a83c`,
  es de las 16:57), que es el mismo programa de `e02653c`: el primer inicio de sesión de hoy fue a las 15:10. A qué hora
  arrancó el panel no está medido.

### Fila 10 a las 15:21: SIN-CUPO, lo más probable por el destino

- **Dónde se detuvo:** en «Select sailing», esperando el resultado de la búsqueda. A los 17,5 s, el portal respondió «no
  sailings for your search».
- **Estado y motivo:** SIN-CUPO. El motivo trae lo que dice el portal, el origen y el destino con que buscó, y el
  formulario completo, con la evidencia `mk_f10_detenida`.
- **Origen:** la celda trae 2 palabras, sin país; escribió esas 2 y eligió «esas 2 palabras, Chile», de tipo Container
  Yard, que es la primera de las 34 de su lista.
- **Destino:** la celda trae «ciudad, país»; escribió la ciudad y eligió **«ciudad + 1 palabra, país»**, Container Yard:
  la cuarta de las 8 de su lista. La sexta es «ciudad, país», también Container Yard: es la que eligió el 27-09, y esa
  corrida encontró la nave. Si hoy con la sexta la búsqueda habría traído la nave no está probado.
- **Por qué eligió la cuarta:** `_mk_ciudad` toma, entre las sugerencias que traen los 5 primeros caracteres de lo
  escrito, la primera con «container yard», y la cuarta va antes que la sexta. Ese texto está en la raíz shadow de cada
  opción, donde lo ve el filtro de Playwright; `log.txt` anota el texto de la opción sin su raíz shadow, y por eso
  «container yard» nunca apareció en `logs/` (CICLO-maersk-busqueda-vacia.md lo daba por ausente). Simulada sobre las 4
  listas guardadas hoy, la regla del programa da en las 4 la opción que `log.txt` dice que pulsó.
- **El 29-09**, con la misma celda, eligió la misma sugerencia que hoy (por su texto en `log.txt`; esa corrida no guardó
  la lista), y la fila quedó REVISAR (encargo 40).

### Fila 10 a las 15:31: NO ENVIADA por un empate de tarjetas repetidas

- **Dónde se detuvo:** en «Select sailing», eligiendo la salida. Esta vez la búsqueda trajo salidas, y la nave apareció
  después de dos «Search more sailing options», en 3 tarjetas.
- **Estado y motivo:** NO ENVIADA. El motivo dice que las 3 opciones salen el 18-10-2026 y tienen el mismo tránsito, 54
  días y 3 horas, así que el tránsito no desempata, y pide elegir la salida en el portal.
- **Las 3 son la misma tarjeta repetida.** Leídas con el `_JS_MK_SALIDAS` del programa, en un Chromium sin red, su texto
  entero es idéntico: 305 caracteres con la salida, la llegada, la nave y su viaje, el «Gate-in» y la tarifa. También es
  idéntico su HTML, byte a byte, sin un atributo que las distinga. Van seguidas: son la 8.ª, la 9.ª y la 10.ª de 14.
- **No es de hoy:** 7 de las 8 listas de salidas guardadas (todas desde el 25-09; la del 24-09, no) traen tarjetas
  repetidas, idénticas en su HTML, en 12 grupos de 2 o 3. Dos de ellas, las del 27-09 a las 18:32 y a las 18:40, sin
  haber pulsado «Search more». El 27-09 a las 21:15, la salida de la nave vino una sola vez.
- **El destino de esta corrida:** la celda trae 1 palabra; eligió «palabra (palabra), país», Container Yard, la primera
  de las 3 de su lista. Ninguna de las 3 tiene la forma de tu regla, porque todas traen algo en medio.

### Frente al 27-09, cuando la fila 10 encontró su nave

El 27-09 a las 21:15, el 29-09 a las 15:03 y hoy a las 15:21, la fila 10 trae la misma celda de destino, escribe lo
mismo y pide la misma nave. El 27-09 eligió «ciudad, país» (hoy, la sexta), encontró la nave con una sola salida, el
11-10, y siguió hasta la revisión, donde cortó por otra causa, ya corregida. El 29-09 y hoy eligió la cuarta, y la
búsqueda volvió vacía. La regla del programa es la misma en las tres corridas: lo que cambió es la lista del portal, el
orden de sus opciones o que la cuarta no estaba el 27-09 (esa corrida no guardó la lista).

### Las listas de sugerencias: la medición que pedía la pregunta 1 del encargo 41

| Lista | Sugerencias | Con la forma de tu regla | Textos distintos con la forma | De ellos, Container Yard |
|---|---|---|---|---|
| Origen (15:21 y 15:31, iguales) | 34 | 8 | 7 | 1 |
| Destino, 15:21 | 8 (y 1 de otra lista del formulario) | 2 | 1 | 1 |
| Destino, 15:31 | 3 (y 1 de otra lista) | 0 | 0 | 0 |

En esta tabla, el país es lo que va después de la última coma. Con la lista de países de la sonda del encargo 40, el
origen da 5 en vez de 8.

- **El país no viene aparte.** El texto de cada opción es lo que se escribió (en un `mark`) y el resto en un `span`, con
  el país al final. La raíz shadow trae otras dos cosas: el tipo de lugar, «Container Yard» o «Store Door», y su sigla,
  CY o SD, en las 79 opciones. Así que tu FRENO del encargo 41 sigue en pie: sin una lista de países, el programa solo
  puede tomar lo que va después de la última coma.
- **Cada sugerencia Container Yard viene dos veces con el mismo texto a la vista:** una Container Yard y otra Store
  Door. Son 5 pares en las 4 listas (4 textos distintos, porque las dos del origen son iguales): uno en cada origen, dos
  en el destino de las 15:21 y uno en el de las 15:31. Las demás sugerencias vienen una vez, como Store Door. Así, «la
  única» por el texto no se cumple justo en las Container Yard; por el texto y el tipo, sí.
- **La celda de origen no trae el país,** y su texto viene en la lista con varios: con tu regla tal como está, 7
  sugerencias distintas cumplen la forma, y solo 1 es Container Yard.
- **Tu regla más «solo Container Yard»** habría elegido el origen de siempre y, a las 15:21, el destino del 27-09 (la
  sexta). A las 15:31 no habría elegido ninguna, y la fila habría quedado NO ENVIADA, aunque esa búsqueda sí encontró la
  nave.

### Los cuatro avisos de la evidencia

Hoy quedaron 15 listas: 13 a las 15:21 y 2 a las 15:31.
1. «Pulsé una sugerencia sin dejar la evidencia»: 0.
2. «La lista cambió mientras guardaba su evidencia»: 0.
3. **Una captura sin la lista:** la lista está en el HTML de las 15, con la sugerencia que se pulsó. En la captura, que
   medí con OCR ampliado ×3 y sin mirarla, la palabra de la sugerencia pulsada se lee 2 o más veces en 10 de las 15: se
   ve la lista. En 5 se lee 0 o 1 vez, y con el OCR de texto disperso tampoco se aclara (solo una llega a 2 lecturas, y
   solo ampliada ×2): `msc_f6_origen`, `msc_f6_destino`, `cosco_f8_origen`, `hmm_f9_origen` y `hmm_f9_destino`, de las
   15:21. Esas 5 no las puedo confirmar: míralas tú.
4. **Una fila sin sugerencia justo después de su evidencia:** 0. Después de las 15 evidencias, la fila pulsó una
   sugerencia.

Ninguna evidencia quedó incompleta.

### Las otras cinco navieras (15:21)

- **ONE,** fila 5: OK-EJEMPLO, armada hasta Review.
- **MSC,** fila 6: OK-EJEMPLO, armada hasta Summary.
- **CMA,** fila 7: OK-EJEMPLO, armada hasta Envío de la reserva, con el aviso de que el portal no respondió a «Validar
  ruta»; siguió, como está previsto.
- **COSCO,** fila 8: OK-EJEMPLO, armada hasta Booking Details.
- **HYUNDAI,** fila 9: OK-EJEMPLO, armada hasta Review & Book.

## Parte 2 · La fila sin puerto de carga o sin destino

### Lo medido antes de cambiar nada

- **Los lectores.** `leer_filas`, el del panel, salta una fila solo si le faltan a la vez el puerto de carga y la nave.
  `leer_reservas`, el de la consola, la toma si trae puerto de carga, o una nave de menos de 40 caracteres sin «,» ni
  «;», o un destino original. Por los dos caminos, la fila con nave y sin puerto de carga o sin destino llegaba a los
  reservadores.
- **Con el texto vacío, los siete ayudantes pulsan a ciegas.** Corrí las funciones del programa, de una copia de
  `e02653c`, sobre una página local en un Chromium sin red: un campo y una lista de dos sugerencias a la vista, que
  anotan cada clic. Así el filtro de texto es el de Playwright de verdad, y no uno imitado: la expresión vacía calza con
  cualquier elemento. Con el texto vacío pulsaron la primera sugerencia ONE, MSC, HYUNDAI, el destino de COSCO, MAERSK y
  el puerto de CMA; el lugar de entrega de CMA pulsó la primera «ramp». El origen de COSCO también lo haría, pero con la
  celda vacía no se llega a llamarlo: `_cosco_puerto_de_la_celda` corta antes. La revisión del encargo 41 lo había
  reproducido en Node para cuatro de ellos; MAERSK y CMA estaban sin medir.
- **Sin ninguna lista a la vista,** ONE, MSC y el puerto de CMA cortaban (NO ENVIADA). MAERSK devolvía vacío, HYUNDAI y
  el destino de COSCO devolvían False, y el lugar de entrega de CMA, un texto vacío: en esos cuatro casos, la reserva
  seguía sin el campo. Además, si ONE o MSC fallaban al escribir, devolvían False y la reserva seguía. `reservar_cma`
  tenía una rama que daba REVISAR si el origen no quedaba elegido, pero no se alcanzaba: `_cma_puerto` corta él mismo
  (lo encontró la revisión; B1, más abajo).
- **La condición de freno, medida antes de cambiar nada.** No se cumple ninguna de las dos:
  - las seis navieras usan el puerto de carga y el destino para reservar, y CMA, además, el lugar de entrega en sus
    modos ramp: ninguna los salta;
  - de las 97 reservas de `logs/`, 66 llegaron a la guarda (CMA 10, COSCO 18, MSC 12, ONE 9, HYUNDAI 11, MAERSK 6), y
    ninguna habría quedado NO ENVIADA con las reglas nuevas. Ninguna traía vacía la celda del puerto o del destino, y en
    todas, los ayudantes eligieron sugerencia. Las líneas de los ayudantes de todo `logs/` tienen 32 formas; las que
    dicen que no eligieron son 3 (dos de CMA y una de COSCO), y ninguna es de una reserva que llegó a la guarda.

### Cómo quedó

- **Commit 1 (`509a83c`): la fila con nave y sin puerto de carga o sin destino queda NO ENVIADA sin entrar al portal.**
  - La regla, `_falta_en_la_fila`: el puerto de carga, y el destino (el final o, si viene vacío, el original), tienen
    que traer texto antes de la primera coma, con el que cada naviera busca su sugerencia. Así, «, CHILE» no trae el
    puerto. Desde los commits 4 a 6, una palabra, y en el puerto de carga sin contar «CHILE» en ninguna posición: «-»,
    «X», «CHILE», «X CHILE» o «CHILE X» tampoco (`_puerto_de_carga`).
  - El motivo, «a la fila le falta el puerto de carga» o «a la fila le falta el destino», queda en pantalla, en
    `log.txt` y en la planilla, como el de la fila sin nave: «✗ fila 6: NO ENVIADA · a la fila le falta el puerto de
    carga. No entro al portal por ella: escribe el puerto de carga en la planilla y vuelve a armar la reserva.»
  - El panel web y la consola la apartan antes de abrir el navegador, después de las filas sin nave; si ninguna fila con
    nave trae la ruta, no lo abren. En CONSOLIDADO, cada fila con su naviera, una sola vez.
  - Cada reservador lleva `_con_la_ruta_de_la_fila`, por dentro de `_con_la_nave_de_la_fila`: cuida cualquier otro
    camino, sin tocar la página. Una fila sin nave y sin la ruta dice «sin nave».
- **Commit 2 (`0c2c070`): sin una sugerencia elegida en el origen, el destino o el lugar de entrega, NO ENVIADA.**
  - Cada reservador corta con `ObjetivoNoEncontrado`, y `_sin_clic_a_ciegas` deja la NO ENVIADA con la captura del paso
    y su HTML. El motivo: «Destino de HYUNDAI: no encontré una sugerencia que elegir para «…», así que no pulsé nada. La
    reserva no se envió; revisa ese paso en el portal.» En MAERSK, «… una sugerencia para «…» que quedara en el campo».
  - Ninguna naviera sigue: ni al campo siguiente, ni CMA a su modo siguiente.
  - La rama de `reservar_cma` que daba REVISAR si el origen no quedaba elegido («el puerto de carga no quedo
    seleccionado») es ahora un corte NO ENVIADA. Ni la rama ni el corte se alcanzan: `_cma_puerto` corta él mismo (B1).
  - Con el texto vacío antes de la primera coma, ninguno de los siete ayudantes escribe ni pulsa nada: corta (desde el
    commit 4, también sin una palabra). Los orquestadores ya apartan esas filas, así que esto cuida lo que ellos no ven:
    en CMA, el destino original, que usa cuando trae un lugar de entrega aparte, y cualquier otro camino.
  - `_ciudad_de` es una sola regla para la parte de una celda con que se busca la sugerencia, y la usan
    `_falta_en_la_fila` y los motivos. Lo que se escribe varía: HYUNDAI escribe la celda entera, y el origen de COSCO,
    el puerto normalizado.
- **Commit 3 (`e49461f`): sin una sugerencia que elegir, la evidencia de la lista queda igual.** Los siete ayudantes la
  dejan con `_evidencia_sin_sugerencia` (la captura de la ventana y el HTML de la página y de sus marcos), con el mismo
  nombre que cuando la hay (`<nav>_f<fila>_origen`, `_destino`; en CMA, con su modo), al terminar la espera que ya
  tenían. MAERSK y COSCO, que vuelven a escribir la ciudad, dejan también la de su segunda espera, `_reintento`. El
  puerto de CMA la deja antes del Tab con que lee lo que quedó. `log.txt` dice «evidencia sin una sugerencia que elegir
  en …».
- **Commit 4 (`3d9923e`): lo que encontró la revisión de código** (el detalle, en «Las revisiones»).
  - La regla de la fila y los topes de los ayudantes piden una palabra (dos letras o números seguidos) antes de la
    primera coma, y el puerto de carga, algo más que «CHILE»: «-», «?» o «X» pasaban, y ONE, MSC, HYUNDAI y el destino
    de COSCO pulsaban la sugerencia que los trajera (y, por cómo filtran, probablemente también MAERSK y CMA; sin
    medir).
  - Lo que devuelve cada ayudante que no eligió, y que después de él nada pase en la página, quedan vigilados por las
    pruebas.
  - En el modo ramp de CMA, el motivo del lugar de entrega dice también el aviso con que CMA rechazó el puerto.
  - Comentarios, docstrings y el texto del tope, al día.
- **Commit 5 (`5bb3bf0`): lo que encontró la revisión del informe** (el detalle, en «Las revisiones»).
  - La palabra del puerto de carga se pide al puerto ya sin el país, en la regla de la fila y en el origen de COSCO: con
    «X CHILE», la palabra del commit 4 era «CHILE», la fila pasaba y COSCO buscaba «X».
  - La página falsa de `TestSinSugerenciaNoSigue` anota también el JavaScript que se corre y los localizadores de
    `get_by_text`, `get_by_role`, `get_by_placeholder` y `get_by_label`.
  - Los docstrings que generalizaban «lo que se escribe», al día.
- **Commit 6 (`7ca9a98`): lo que encontró la revisión final** (el detalle, en «Las revisiones»).
  - La palabra del puerto de carga se mide en la celda tal como viene y en el puerto normalizado sin «CHILE» en ninguna
    posición, con un solo ayudante, `_puerto_de_carga`, para la regla de la fila y el origen de COSCO: «CHILE X» pasaba
    (su palabra era el país), y desde el commit 5 también «№», que al normalizarse da «NO».
  - La página falsa de `TestSinSugerenciaNoSigue` anota también el teclado, el mouse y las acciones de la página, y el
    marco de COSCO anota en la misma lista: un reservador que siguiera por ahí pasaba la prueba.
  - El docstring de `_falta_en_la_fila` decía mal quiénes no miraban si eligieron.
- **Sin clics nuevos:** 182 llamadas a clic o tecla en `e02653c` y 182 después de los seis commits, contadas por función
  y constante; solo hay 9 nombres nuevos, y ninguno cambia su cuenta. `test_candado` no cambió, y pasa.

## La red y el gate de cada commit

Cada commit se probó antes en una copia de su base (la suite y el precenso de sus filtros) y después en la raíz (el
gate: la suite completa y el censo filtrado de las mutaciones nuevas o tocadas y de las que nombran pruebas que
cambiaron). En la tabla, las mutaciones y los pares del gate van sin repetir: una mutación que entra por dos filtros se
cuenta una vez (`gates_distintos.py`; sumando por filtro, como los imprime el corredor, son 106 en 167, 92 en 125, 65 en
112, 158 en 216, 57 en 97 y 100 en 142).

| Commit | Pruebas | Mutaciones | Pares | Gate en la raíz |
|---|---|---|---|---|
| `e02653c` (base) | 525 | 1479 | 1765 | — |
| `509a83c` (la fila sin ruta) | 532 | 1510 | 1824 | suite de 532 en verde; 3 filtros, 94 mutaciones en 143 pares: todas muerden |
| `0c2c070` (sin sugerencia elegida) | 534 | 1536 | 1852 | suite de 534 en verde; 7 filtros, 85 mutaciones en 117 pares: todas muerden |
| `e49461f` (la evidencia sin sugerencia) | 534 | 1548 | 1865 | suite de 534 en verde; 4 filtros, 52 mutaciones en 97 pares: todas muerden |
| `3d9923e` (lo de la revisión de código) | 537 | 1575 | 1897 | suite de 537 en verde; 3 filtros, 153 mutaciones en 200 pares: todas muerden |
| `5bb3bf0` (lo de la revisión del informe) | 537 | 1579 | 1903 | suite de 537 en verde; 2 filtros, 55 mutaciones en 90 pares: todas muerden |
| `7ca9a98` (lo de la revisión final) | 537 | 1586 | 1911 | suite de 537 en verde; 4 filtros, 79 mutaciones en 115 pares: todas muerden |

En los seis gates: 0 tiempos agotados, 0 pruebas sin mutación y los originales sin cambios. El primer gate del commit 2
se cayó por la suspensión del equipo (de 17:19 a 19:52, eventos 506 y 507 de Kernel-Power): el corredor corta el
`unittest` a los 1200 s de reloj, y ese reloj contó las 2,5 horas. Lo repetí entero, y pasó.

**Los censos completos.** Sobre `7ca9a98`, el último commit de código: 1586 mutaciones en 1911 pares, y todos muerden.
Duró 62 minutos (unos 5 de control, 30 de preparación y 28 de pares). Antes, sobre `5bb3bf0`: 1579 mutaciones en 1903
pares, todos muerden, en 82 minutos (unos 11 de control, 35 de preparación y 36 de pares). En los dos: 0 pruebas sin
mutación, 0 tiempos agotados del corredor, los originales sin cambios y ninguna suspensión (0 eventos de Kernel-Power;
la misma consulta encuentra los 6 eventos de la suspensión de la tarde). En los dos, una mordida trae «TimeoutExpired»
en su motivo: es la espera de la propia prueba (`previa-ociosa-no-se-apaga`: la instancia previa del panel no se apaga),
y en el censo del encargo 41 mordió igual. El censo de `3d9923e` lo detuve en su preparación, cuando la revisión del
informe encontró el hueco que corrige el commit 5 (en «Las revisiones»).

## Cómo probarlo

1. Abre `Iniciar AQUASHIELD.bat` con las tres llaves de emisión cerradas. Si el panel estaba abierto, ciérralo y vuelve
   a abrirlo: el programa se carga al arrancar.
2. **La fila sin ruta:** en una copia de la planilla, deja una fila con nave y sin puerto de carga (vacío, «, CHILE»,
   «CHILE», «X CHILE», «CHILE X» o «-»), y otra con nave y sin destino (vacías las dos columnas, el puerto de descarga y
   el destino final, o con «-» en el destino final). Córrelas: tienen que quedar NO ENVIADA con «a la fila le falta el
   puerto de carga» o «a la fila le falta el destino», en el panel, en `log.txt` y en la planilla descargada, y si no
   hay otra fila de esa naviera, sin abrir el navegador.
3. **Sin sugerencia:** no se provoca a propósito. Si una fila queda NO ENVIADA en su origen, su destino o su lugar de
   entrega (el motivo empieza con el campo: «Origen de …», «Destino de …», «Port of Load de MSC», «Lugar de entrega de
   CMA»…), en su carpeta de `logs\` están `<nav>_f<fila>_origen` o `_destino` (la lista, o la pantalla sin ella) y
   `<nav>_f<fila>_sin_objetivo`.
4. **MAERSK:** cómo elige no cambió. Mientras decides las preguntas 1 y 2, la fila 10 puede volver a dar SIN-CUPO, o NO
   ENVIADA por el empate, según lo que traiga el portal.

Avísame si una fila que trae puerto de carga y destino queda NO ENVIADA por la ruta.

## Qué decides tú

1. **El destino de MAERSK a las 15:21, y la regla del encargo 41.** El programa eligió «ciudad + 1 palabra, país» porque
   toma la primera sugerencia con «container yard», y en la lista del portal esa iba antes que «ciudad, país» (también
   Container Yard), la que encontró la nave el 27-09. Con las listas de hoy, tu regla tal como está no alcanza: cada
   Container Yard viene repetida, con el mismo texto, como Store Door; el país no viene aparte; y la celda del origen no
   trae el país (7 sugerencias distintas tienen la forma). Opciones, con lo medido en las 4 listas de hoy (2 de ellas,
   las del origen, iguales):
   - **Entre las Container Yard, la única cuya parte antes de la primera coma, sin lo que va entre paréntesis, es lo que
     se escribió; si no hay una sola, NO ENVIADA** (recomendada). En las 4 listas elige lo que funcionó: el origen de
     siempre, a las 15:21 el destino del 27-09 (la sexta de su lista) y a las 15:31 el que encontró la nave. No mira el
     país, y está medida en solo 3 listas distintas.
   - **Tu regla tal como la decidiste, pero solo entre las Container Yard,** con el país como lo que va después de la
     última coma: elige lo mismo en el origen y a las 15:21, y a las 15:31 ninguna, porque esa sugerencia trae la ciudad
     repetida entre paréntesis en medio: la fila habría quedado NO ENVIADA, aunque esa búsqueda encontró la nave.
   - El país escrito en la celda, siempre: el origen de la fila 10 no lo trae.
   - Dejar la regla como está y que el operador revise el destino cuando MAERSK dé SIN-CUPO: el motivo ya dice con qué
     destino buscó.
2. **El empate de MAERSK a las 15:31.** Las 3 salidas de la nave son la misma tarjeta repetida: idénticas en su texto y
   en su HTML, sin nada que las distinga. En 7 de las 8 listas guardadas (todas menos la del 24-09) hay tarjetas así.
   Opciones:
   - **Tratar como una sola salida las tarjetas idénticas (el mismo texto entero) y pulsar el «Book» de la primera de
     ellas** (recomendada): no es elegir entre opciones distintas, porque no hay diferencia que medir. Sin medir si el
     portal arma la misma reserva con cualquiera de ellas.
   - Dejarlo como está: NO ENVIADA, y la reserva se hace a mano.
3. **El panel y la fila sin ruta.** La fila sin nave se ve marcada en el panel antes de correr («sin nave») y cuenta
   aparte; la fila sin puerto de carga o sin destino no: queda NO ENVIADA recién al correr, con su motivo. ¿La marcamos
   igual en el panel?
4. **Las 5 capturas que no puedo confirmar:** `msc_f6_origen`, `msc_f6_destino`, `cosco_f8_origen`, `hmm_f9_origen` y
   `hmm_f9_destino`, de la corrida de las 15:21. Su HTML trae la lista con la sugerencia pulsada; en la captura, el OCR
   no la lee. Si alguna salió sin la lista, dímelo y mido por qué.
5. **Una fila con «-» en el destino final y un puerto de descarga válido** queda NO ENVIADA con «a la fila le falta el
   destino»: el destino es el final, si viene, y las navieras buscarían «-». Si en la planilla «-» quiere decir «igual
   al puerto de descarga», dímelo y lo tomo así.
6. **«CL» solo en el puerto de carga** pasa como un puerto: es la sigla de Chile. COSCO buscaría «CL», y en CMA calza
   con el código de cualquier puerto de Chile. ¿Cuenta como «solo el país», igual que «CHILE»?

## Re-medir (pieza 1)

Las sondas son de solo lectura y no se versionan. Quedaron en el scratchpad de esta sesión
(`$env:TEMP\claude\<proyecto>\<sesión>\scratchpad\e42`), que puede limpiarse; sin ellas, estos números no se re-miden.
Cada una declara su universo y su control positivo, que aborta si no pasa, y sus salidas quedaron en
`salida_<sonda>.txt`, en la misma carpeta (solo formas, cuentas, fechas y booleanos). Las que leen datos reales de
`logs/` o de las planillas lo dicen:
- **`corridas.py [día]`** (lee `logs/`): las carpetas de corrida de un día, con su tipo, su naviera, cuántos archivos y
  cuántas evidencias de lista. No imprime el nombre de la carpeta, que lleva el del operador.
- **`horarios_hoy.py [día]`** (lee `logs/` y las fechas de las planillas): la hora de cada carpeta del día por su tipo
  (inicio de sesión o corrida del panel) y la de modificación de las planillas de la raíz, de la copia que recibe el
  panel y de `AQUASHIELD.py`, sin nombres. Control: las dos corridas del panel que ve `corridas.py`.
- **`sondas_otra_vez.sh`:** vuelve a correr las sondas que no habían guardado su salida (lo encontró la revisión del
  informe), y anota en `sondas_otra_vez.resumen.txt` cómo terminó cada una.
- **`esqueleto.py <fecha_hora> [naviera|todas] [filas] [--todo]`** (lee `logs/` y las planillas): el esqueleto de cada
  línea de `log.txt`, con las palabras del vocabulario del programa y todo lo demás tapado, y las palabras de las filas
  de datos de las planillas tapadas siempre. Aborta antes de imprimir una línea que quedaría con una de ellas.
  `control_esqueleto.py` la prueba con líneas sintéticas.
- **`listas_mk.py`** (lee `logs/`): cada lista de sugerencias de MAERSK guardada, con la forma de cada opción frente a
  su celda, las dos maneras de reconocer el país (A, la lista de la sonda del encargo 40; B, lo que va después de la
  última coma), cómo reparte su texto y cuál se pulsó. Control: una página sintética.
- **`sombras_mk.py`, `slots_mk.py` y `pais_aparte.py`** (leen `logs/`): los dos textos de la raíz shadow de cada opción
  (el tipo de lugar y su sigla), la regla del programa simulada (control: da la pulsada en las 4 listas), los textos
  repetidos, y el país frente a la sigla.
- **`comparar_f10.py`** (lee `logs/`): la fila 10 en las corridas del 27-09, el 29-09 y hoy, comparada sin imprimirla, y
  a qué opción de las listas de hoy corresponde lo que eligió cada una. Control: la de las 15:21 cae en la cuarta de su
  lista.
- **`empate_mk.py`, `duplicadas_mk.py` y `empate_html.py`** (leen `logs/`, en un Chromium sin red): las salidas de la
  nave leídas con el `_JS_MK_SALIDAS` del programa (control: las mismas que dice `log.txt`), las tarjetas repetidas en
  las 8 listas guardadas, y si su HTML es idéntico (control, en las dos: el grupo de 3 de hoy a las 15:31).
- **`reglas_mk.py`** (lee `logs/`): las dos reglas candidatas de la pregunta 1 sobre las 4 listas. Control: la A da la
  sexta en el destino de las 15:21.
- **`avisos_lista.py` y `ocr_disperso.py`** (leen `logs/`, capturas con OCR y sin mirarlas): los avisos de la evidencia
  en `log.txt`, la sugerencia pulsada en el HTML de cada evidencia, y cuántas veces lee el OCR su primera palabra en la
  captura. Controles: una imagen sintética, y el HTML del origen de MAERSK.
- **`freno_guarda.py` y `variantes_sugerencia.py`** (leen `logs/`): las reservas que llegaron a la guarda y si alguna
  calza con una regla nueva; y las formas de todas las líneas de los ayudantes, para ver que los patrones reconocen las
  reales. Control: tres bloques sintéticos.
- **`freno_m1.py` y `freno_m1b.py`** (leen `logs/`): la condición de freno con la regla del commit 4 (una palabra antes
  de la primera coma, y el puerto de carga con algo más que el país). La primera mira la cabecera de cada reserva; la
  segunda, el destino original de CMA cuando el lugar de entrega va aparte, y lo que escribió cada ayudante. Controles:
  cabeceras y líneas sintéticas con «-», «X» y «CHILE».
- **`vacio_mk_cma.py <copia>` y `vacio_otros.py <copia>`** (sin datos reales): los siete ayudantes del programa, de una
  copia, con el texto vacío, sobre una página local en un Chromium sin red. Control: con el texto de una sugerencia,
  cada uno pulsa esa.
- **`freno_c5.py` y `freno_c6.py`** (leen `logs/`): `freno_m1.py` con la regla del commit 5 (la palabra, pedida al
  puerto sin el país) y con la del commit 6 (en la celda y en el puerto sin «CHILE» en ninguna posición). Controles: las
  mismas cabeceras sintéticas, más «X CHILE» y, en la del 6, «CHILE X» y «CHILE PUERTO».
- **`gates_distintos.py`** (sin datos reales): cuántas mutaciones y pares distintos corrió el gate de cada commit, con
  la regla de filtro del corredor sobre `tests/mutaciones.py` de ese commit. Control: cada filtro da lo que imprimió su
  gate.
- **`antes_pasaba_c6.py`** (sin datos reales): de a una, en una copia de `5bb3bf0`, las mutaciones del commit 6 que
  siguen por la página, con la prueba de ese commit. Control: sin mutar pasa, y con `page.evaluate` cae.
- **`antes_pasaba.py`** (sin datos reales): una copia de `e49461f` con tres mutaciones a la vez (B2 y dos de M2, de la
  revisión de código), y su suite entera. Control: la copia sin mutar pasa las tres pruebas que la revisión nombró.
- **`clics_por_funcion.py <árbol> [base]`:** las llamadas a clic y a tecla por función y constante (del encargo 41).
- **`ver.py <archivo> <desde> <hasta>`:** un tramo del código con los códigos tapados (pieza 4, 1).
- **Las herramientas del gate:** `copia.py`; `aplicar_c1.py` a `aplicar_c6.py`, los `_pruebas.py` de los tres primeros y
  `aplicar_c6_mutaciones.py` (cada viejo, exactamente una vez; escritura atómica, en binario y LF); las pruebas de los
  commits 4 a 6 las escribí con Edit en la copia, y cada copia pasó a la raíz después de comprobar que solo cambiaban
  sus archivos; `anclas.py` (las anclas de las mutaciones y las líneas nuevas de más de 120); y `precenso.sh`,
  `suite_y_precenso.sh`, `gate.sh`, `censo.sh` y `commit.sh`, los del encargo 41 con la ruta de este.

La red versionada, desde `C:\dev\Agendamiento Reservas`:
- `python tests/correr.py`: la suite;
- `python tests/correr.py --mutaciones --filtro <texto>`: el censo de un filtro (`ruta-`, `sin-sugerencia-`, `vacio-`,
  `sin-lista-`, `no-eligio-`, `TestFilaSinRuta`…);
- `python tests/correr.py --mutaciones`: el censo completo.

## NO retroceder (pieza 2)

- **La fila sin ruta se aparta antes de abrir el navegador,** como la fila sin nave, y el decorador de cada reservador
  la corta sin tocar la página: con el texto vacío, cada ayudante pulsaba la primera sugerencia a la vista.
- **La regla mira la parte antes de la primera coma, con la que las navieras buscan, no la celda entera, y pide una
  palabra; en el puerto de carga, también en el puerto normalizado sin «CHILE» en ninguna posición:** «, CHILE», «-»,
  «X», «CHILE», «X CHILE», «CHILE X» o «№» no son un puerto. `_ciudad_de` para todo, y `_puerto_de_carga` para el puerto
  de carga, que cuenta las letras ya normalizadas (A-Z sin tildes y números: el puerto de carga es de Chile).
- **El ayudante de COSCO corta solo con el texto vacío:** llena también el contrato, que va tal como viene. El origen y
  el destino se los pasa ya cortados quien lo llama.
- **La nave va primero:** la fila sin nave dice eso aunque tampoco traiga la ruta (`_con_la_ruta_de_la_fila`, por dentro
  de `_con_la_nave_de_la_fila`).
- **Sin una sugerencia elegida, NO ENVIADA, sin seguir:** un campo sin elegir hacía buscar otra ruta que la de la fila,
  y en CMA, probar el modo siguiente ya no cambia eso.
- **Ningún ayudante escribe ni pulsa sin una palabra,** aunque los orquestadores ya aparten la fila: cuida lo que ellos
  no ven (el destino original de CMA).
- **Después del ayudante que no eligió, nada en la página:** la página falsa de `TestSinSugerenciaNoSigue` anota cada
  acción de sus localizadores, de la página, del teclado y del mouse, cada dirección y cada JavaScript (menos el que
  guarda el HTML de la evidencia), y en COSCO lo que se corre en su marco; si se la vuelve a hacer muda, un reservador
  que siga escribiendo pasa sin que se vea.
- **La evidencia sin sugerencia va al terminar la espera que ya existía,** sin esperas ni clics nuevos, y con el mismo
  nombre que cuando hay lista; la del puerto de CMA, antes del Tab, que ya cambia la pantalla.

## Universo y cobertura (pieza 3)

- **El diagnóstico de MAERSK:** las dos corridas de hoy, las dos con una sola reserva de MAERSK, la fila 10. De la
  comparación, las 4 corridas de esa fila con cabecera (27-09 a las 21:15, 29-09 a las 15:03 y las dos de hoy).
- **Las listas de sugerencias:** 4 de MAERSK, de 3 textos distintos (las dos del origen son iguales), con 79 opciones
  que traen sus dos textos en la raíz shadow y 2 que no (la opción del origen que queda en otra lista del formulario).
  Son las únicas que hay: las corridas anteriores no las guardaban. La regla candidata A está medida en 3 listas
  distintas.
- **Las listas de salidas:** las 8 páginas de «Select sailing» guardadas en `logs/`, del 24-09 al 30-09.
- **Las evidencias de hoy:** 15 listas, de las seis navieras; 15 HTML leídos y 15 capturas medidas con OCR, 10 de ellas
  confirmadas.
- **La condición de freno:** 97 reservas en los `log.txt` de `logs/` (0 sin estado final), 66 de ellas llegaron a la
  guarda. Las líneas de los ayudantes de todas, agrupadas en 32 formas.
- **El texto vacío** se midió en una página local, no en el portal: si cada portal muestra una lista con el campo vacío
  no está medido. Por eso el tope va en cada ayudante, y no depende de eso.

## Defectos de instrumento cazados (pieza 4)

1. **Leer `reservar_one` con `sed` imprimió en mi terminal los dos códigos de contrato de ONE** que el programa trae en
   un comentario. No quedaron en ningún archivo. Desde ahí leí el código con `ver.py`, que tapa los códigos.
2. **La primera corrida real de `esqueleto.py` abortó antes de imprimir:** las celdas de la planilla traen los nombres
   de las navieras y los encabezados, y el servidor de una URL calzaba con uno. La red de seguridad (ninguna palabra de
   la planilla en lo que se imprime) la detuvo. Desde ahí, la planilla aporta solo sus filas de datos y los nombres de
   las navieras quedan a la vista.
3. **`corridas.py` contó 10 evidencias de lista a las 15:21, y eran 13:** no ve las de CMA, que llevan dos tramos en el
   nombre (`_ramp_separado`). Las 13 salen de `log.txt`.
4. **Supuse que el segundo texto de la raíz shadow era el código del país,** y no: son las iniciales del tipo de lugar
   (CY o SD), en las 79 opciones. Lo medí antes de escribirlo.
5. **El primer OCR de las capturas, sin ampliar, no leía la palabra en 5 de 15;** ampliado ×3, en 10 de 15 la lee dos
   veces o más, y las otras 5 siguen sin confirmar, también con OCR de texto disperso. No las di por buenas.
6. **Una sonda imprimió en mi terminal países de las sugerencias,** entre ellos el del destino de la fila 10: son
   países, no puertos, pero no van a este informe ni a ningún archivo.
7. **`listas_mk.py` mezclaba al principio el texto de la raíz shadow con el de la opción,** y así la pulsada «no estaba»
   en su lista. Separé los dos, y la pulsada aparece en las 4.
8. **`empate_mk.py` no cargaba el JavaScript del programa** (le faltaba una constante con que se arma): ahora evalúa
   todas las asignaciones de nivel superior, como la sonda de la casilla del encargo 40.
9. **La herramienta Bash volvió a comerse barras invertidas** en un script que editaba otro (`\\n`); la aserción de su
   ancla lo detuvo antes de escribir, y lo reescribí con Edit. Y un ancla de `aplicar_c3.py` calzaba dos veces (otra
   función de MSC tiene la misma forma): también la detuvo su aserción.
10. **Di por hecho que el origen de CMA sin elegir daba REVISAR,** por una rama de `reservar_cma`, sin mirar que
    `_cma_puerto` nunca devuelve False. Lo dijo el mensaje del commit 2; lo encontró la revisión (B1), no yo.
11. **`freno_m1.py` medía el destino de CMA solo en su lugar de entrega final:** con el lugar de entrega aparte, la
    cabecera trae los dos, y el original (el que va al POD) quedaba fuera. Lo vi al decidir qué mira el tope de
    `_cma_puerto`, y lo midió `freno_m1b.py`: 0 de 10.
12. **`Path.write_text` dejó con CRLF un borrador de este informe** (104 líneas): en Windows convierte cada salto de
    línea. Lo vi antes de armarlo y lo devolví a LF; desde ahí, los borradores los edito con `comun.py`, en binario.
13. **Mi monitor del censo completo avisaba solo cuando cambiaba la cuenta de pares:** mientras el corredor prepara las
    copias, esa cuenta no cambia, el monitor quedaba mudo y la sesión podía quedar ociosa (y el equipo, suspenderse). Lo
    rearmé para avisar cada 3 minutos.

## Premisas del encargo contrastadas (pieza 5)

- **«La corrida de prueba de hoy (la más reciente en logs/)»:** hay dos, y la más reciente (15:31) ya traía otra fila
  10: otro destino y otra nave. El diagnóstico cubre las dos: fallaron por causas distintas.
- **Que la corrida hubiera dejado las listas:** las dejó, así que la sospecha de código viejo no aplica. El panel corría
  código de `448e3e4` o posterior (desde ahí ONE anota la sugerencia con su texto; las listas se guardan desde
  `5a21f31`); si era anterior a `e02653c` no lo sé, aunque lo más probable es que fuera el de `e3e0a76`, el mismo
  programa de `e02653c` (parte 1).
- **Lo que midió la revisión del encargo 41, se cumple:** `leer_filas` salta una fila solo si le faltan el puerto de
  carga y la nave, y con el texto vacío ONE, MSC, HYUNDAI y el destino de COSCO pulsan a ciegas; lo volví a medir en un
  Chromium con las funciones del programa, no en Node. MAERSK y CMA también pulsan (medido ahora).
- **«reservar_maersk no valida lo que devuelve _mk_ciudad y reservar_cosco no mira lo que devuelve
  _cosco_autocomplete»:** se cumple, y era más ancho: tampoco miraban HYUNDAI (sus dos campos), el lugar de entrega de
  CMA ni el error al escribir de ONE y de MSC.
- **Refutada, una frase de `CLAUDE.md`:** decía que «container yard» «en `logs/` nunca apareció», y se leía como que las
  sugerencias no lo traen. Sí lo traen: está en la raíz shadow de una o dos opciones de cada lista, y `log.txt` no lo
  anota porque guarda el texto de la opción sin su raíz shadow.
- **La condición de tu FRENO del encargo 41 sigue:** el país no viene aparte.

## Residual (pieza 6)

| Qué | Por qué queda | Se reabre si |
|---|---|---|
| Cómo elige MAERSK su origen y su destino (el destino de las 15:21) | es tuyo: el encargo pedía solo el diagnóstico | decides la regla (pregunta 1) |
| El empate de MAERSK con tarjetas repetidas (las 15:31) | ídem | decides qué hacer con las tarjetas idénticas (pregunta 2) |
| El panel no marca la fila sin ruta antes de correr, como la sin nave | tu decisión dice «NO ENVIADA sin entrar al portal», y eso ya se cumple | pregunta 3 |
| 5 capturas de lista que el OCR no confirma | no miro capturas reales | las miras tú (pregunta 4) |
| Si cada portal muestra una lista con el campo vacío | medido en una página local, no en el portal | una fila llega al portal con una celda vacía: ya no debería, y el tope de cada ayudante lo cubre igual |
| El tope sin una palabra no deja la lista (no escribe nada): queda la captura del paso sin objetivo | no hay lista que medir | — |
| En `_mk_ruta_buscada`, la rama «ninguna sugerencia quedó en el campo» ya no se alcanza desde `reservar_maersk` (su docstring lo dice) | es inofensiva y tiene su prueba | se toca el motivo de SIN-CUPO |
| Los cortes de `reservar_cma` cuando `_cma_puerto` no elige no se alcanzan: él corta antes, con su motivo | son resguardo, si cambia `_cma_puerto` | — |
| La cola del corte, «así que no pulsé nada… revisa ese paso en el portal», no es exacta en todos (MAERSK sí pulsó si la sugerencia no quedó; sin el campo, no faltaba la sugerencia; con «, PUERTO», dice que falta el puerto) | es de `_sin_clic_a_ciegas`, común a todos los cortes: cambiarla toca los seis reservadores | decides cambiar el texto de esos motivos |
| Una fila con «-» en el destino final y un puerto de descarga válido queda NO ENVIADA por «falta el destino» | las navieras buscarían «-» | decides qué quiere decir «-» (pregunta 5) |
| «CL» solo, la sigla de Chile, pasa como puerto de carga: COSCO buscaría «CL», y en CMA calza con el código de cualquier puerto de Chile | no sé si en la planilla quiere decir «solo el país» | pregunta 6 |
| El contrato de COSCO (la cotización de la fila o el de `config.json`) se escribe tal como viene: con «-», lo escribiría y podría pulsar una sugerencia que lo traiga (sin medir) | fuera del encargo, que es sobre el origen, el destino y el lugar de entrega | una fila trae una cotización así |
| Las sandboxes `aquashield_red_*` de `%TEMP%` | el encargo dice que no se tocan: son la evidencia de otra tarea | esa tarea |

El residual del encargo 41 sigue igual, salvo sus filas del texto vacío (pregunta 5 de ese informe, cerrada aquí) y la
de «sin sugerencia no dejan nada» (su pregunta 3, cerrada aquí).

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v14**, y las reglas propias del módulo, las de su `CLAUDE.md`. No chocaron entre sí.
- **Frenar cuando la decisión es de negocio:** la regla de MAERSK y el empate son tuyos (preguntas 1 y 2): el encargo
  pedía el diagnóstico, y no cambié la regla. Lo demás, que tenías decidido, siguió.
- **El FRENA SI, medido antes de cambiar nada:** las dos condiciones, con sus sondas (`freno_guarda.py` y la lectura de
  los seis reservadores), antes del commit 1.
- **Control positivo que aborta:** cada sonda trae el suyo; el de `esqueleto.py` abortó en su primera corrida real, y el
  defecto era de la sonda (pieza 4, 2).
- **Un cero solo vale con sus descartados:** «0 reservas calzan» va con 97 reservas, 0 sin estado final y 66 en la
  guarda, y con el universo de las líneas de los ayudantes, donde los patrones sí calzan con las 3 reales que dicen que
  no eligieron.
- **La unidad la fija el sujeto:** la regla de MAERSK decide por lista de sugerencias (4, de 3 textos), el empate por
  tarjeta (y por su HTML), la regla de la fila por fila, y «sin clics nuevos» por llamada a clic o tecla.
- **Re-medir contra HEAD antes de diseñar:** lo que traía la revisión del encargo 41 (el texto vacío en Node) lo volví a
  medir con las funciones del programa en un Chromium, y encontré lo mismo más MAERSK y CMA.
- **Todo registro es una hipótesis hasta que se contrasta:** también `CLAUDE.md` («container yard» nunca apareció), lo
  que yo supuse (la sigla del país; pieza 4, 4) y mis propias notas: «6 de las 8» y «cada lugar viene dos veces»
  salieron de ellas y no de las salidas de las sondas, y la revisión del informe los corrigió contra esas salidas.
- **El negativo tiene que morder:** cada prueba nueva trae sus mutaciones, y el precenso en una copia antes de cada
  gate.
- **Un negativo vacuo delata un caso incompleto:** la mutación que llena la cotización de CMA antes de cortar pasaba,
  porque la página falsa se tragaba las acciones (B2). No era la aserción: era el caso, que no anotaba lo que se hacía.
  Y el caso (e), la pieza que corre después tapa a la de antes: `_puerto_de_carga` tapaba dos mutaciones de
  `_cosco_puerto_de_la_celda`, y su prueba pasó a mirar la normalización directo.
- **Un gate en cero prueba contención, no correctitud:** el efecto lo prueban las pruebas funcionales: los seis
  reservadores corren de verdad hasta su ruta (TestSinSugerenciaNoSigue), y los siete ayudantes, sobre la página falsa
  que anota cada clic, espera y tecla.
- **Fuente única:** la parte de una celda con que se busca es `_ciudad_de`, y el puerto de carga, `_puerto_de_carga`,
  que usan la regla de la fila y el origen de COSCO; la evidencia sin lista, `_evidencia_sin_sugerencia`.
- **Cada reemplazo afirma su viejo una vez, la escritura es atómica y el EOL se preserva:** los `aplicar_*.py`, con
  `comun.py`; cada commit sale sin CR.
- **El cambio y su guardián, en la misma operación:** cada commit trae su código, sus pruebas y sus mutaciones.
- **Del módulo:** el candado no se toca y `test_candado` no cambia; antes de la guarda, ni clics a ciegas ni clics
  nuevos (182 antes y después); la evidencia solo lee y nunca corta; las pruebas cargan la copia de `soporte.cargar()` y
  nunca usan el puerto 8765; la sonda de secretos antes de cada commit; los datos de `logs/` y de las planillas, solo en
  lectura y sin imprimirlos; ninguna captura mirada.

## Entregable (pieza 8)

- Este informe, `CICLO-maersk-y-fila-sin-ruta.md`, y `CLAUDE.md` al día, en el commit de documentación.
- La forma de los dos, medida con `revisar_informe.py` (del encargo 41): los bytes (sin CR, NUL, BOM ni caracteres
  invisibles), las líneas de prosa de más de 120, los códigos partidos entre dos líneas, el voseo y las marcas sin
  llenar. En los dos, 0 de cada cosa, salvo dos líneas largas de `CLAUDE.md` que ya estaban en `e02653c`.
- El informe lo revisaron dos agentes contra sus fuentes, y el código, tres (abajo). No lo miré renderizado: la pieza es
  opcional mientras R22 sea candidata.

## Las revisiones

**La revisión de código** (un agente, de solo lectura, sobre los commits 1 a 3, con su diff frente a `e02653c` y una
copia del árbol; el primero se detuvo con la suspensión del equipo y lo relancé): 0 críticos, 0 altos, 2 medios y 7
bajos. Comprobé cada uno en el código antes de corregirlo. Lo que dijo de la red de antes lo medí en dos (B2 y M2), con
tres mutaciones: la de B2 (CMA llena la cotización antes de cortar) y dos de M2 (HYUNDAI y ONE dicen que eligieron),
puestas a la vez en una copia de `e49461f`. Su suite entera pasaba (534 en verde); con las pruebas del commit 4, las
tres muerden. El commit 4 (`3d9923e`) corrige lo que era del encargo; lo demás queda en el residual:

- **M1 (medio): una celda sin una palabra pasaba.** La regla de la fila y los topes de los ayudantes miraban solo el
  texto vacío. Con «-», «?» o «X» antes de la primera coma, ONE, MSC, HYUNDAI y el destino de COSCO escribían ese texto
  y pulsaban cualquier sugerencia que lo trajera (la revisión lo reprodujo en Node con «-»; por cómo filtran,
  probablemente también MAERSK y CMA, sin medir). Y un puerto de carga con solo el país, «CHILE», también pasaba, salvo
  en COSCO, que ya lo cortaba. Así quedó:
  - `_ciudad_de` pide dos letras o números seguidos, de cualquier alfabeto; si no los encuentra, da vacío. Lo usan la
    regla de la fila, los topes de los ayudantes y los motivos.
  - El puerto de carga tiene que traer algo más que el país: se mide con la misma normalización con que COSCO ya lo
    cortaba (`_cosco_puerto_de_la_celda`).
  - MAERSK y CMA toman la ciudad con `_ciudad_de`. El ayudante de COSCO también llena el contrato, que va tal como
    viene, así que corta solo con el texto vacío; el origen y el destino se los pasa ya cortados con `_ciudad_de` quien
    lo llama.
  - El FRENO, medido otra vez con la regla nueva: ninguna de las 66 reservas que llegaron a la guarda habría cambiado.
    Tampoco el destino original de CMA, que va al POD cuando el lugar de entrega va aparte y que la regla de la fila no
    mira, en ninguna de las 10 reservas de CMA con lugar de entrega aparte. Lo mismo con los 114 textos que los
    ayudantes anotaron en `log.txt` al escribir.
- **M2 (medio): nada miraba lo que devuelve el ayudante que no eligió.** Según la revisión, una mutación que le hiciera
  decir «elegí» seguía pasando la red en HYUNDAI, en el lugar de entrega de CMA y en el error al escribir de ONE y de
  MSC; lo medí en HYUNDAI y en ONE (arriba). Ahora la prueba de la lista vacía lo exige, y una prueba nueva, con un
  campo que no responde, lo exige en los siete.
- **B1 (bajo): el origen de CMA nunca daba REVISAR.** Lo dicen el mensaje del commit 2 y un comentario. `reservar_cma`
  tenía esa rama, pero `_cma_puerto` corta él mismo si no elige, así que no se alcanzaba. Los cortes que la reemplazan
  tampoco se alcanzan, y quedan como resguardo. Corregí el comentario y las pruebas; el mensaje del commit 2 ya no se
  puede cambiar, y la corrección va en el del commit 4.
- **B2 (bajo): la página falsa se tragaba las acciones.** En `TestSinSugerenciaNoSigue`, un reservador que siguiera
  usando la página después del ayudante que no eligió pasaba la prueba. Por ejemplo, si CMA llenaba la cotización antes
  de cortar, nada lo detectaba. Ahora la página anota cada acción, cada tecla y cada dirección (desde el commit 5,
  también el JavaScript y los `get_by_*`, y desde el 6, el teclado, el mouse, las acciones de la página y el marco de
  COSCO), y la prueba exige que después de ese ayudante no pase nada. La mutación que llena la cotización antes de
  cortar ahora hace caer la prueba.
- **B3 (bajo): motivos que confunden.** Corregí uno: el texto del tope decía «en la celda de la fila» y ahora dice «de
  la planilla», que es donde se arregla. Los otros quedan en el residual. La cola «así que no pulsé nada… revisa ese
  paso en el portal» es de `_sin_clic_a_ciegas`, y la comparten todos sus cortes. En MAERSK, cuando la sugerencia
  pulsada no quedó en el campo, sí pulsó. Cuando falta el campo y no la sugerencia, «no encontré una sugerencia» no es
  exacto. Y con «, PUERTO» (el puerto después de la coma), el motivo dice que falta el puerto, porque se busca con lo de
  antes de la coma.
- **B4 (bajo): una rama muerta en `_mk_ruta_buscada`,** «ninguna sugerencia quedó en el campo». Queda, con su prueba, y
  su docstring dice que `reservar_maersk` ya no la alcanza.
- **B5 (bajo): textos atrasados.** Actualicé los docstrings de `_falta_en_la_fila` y `_evidencia_sin_sugerencia` y el
  comentario de `AQUASHIELD_SOLO_PRIMERA`. `CLAUDE.md` y este informe van en el commit de documentación. Una observación
  de la revisión no se cumple: `.gitignore` sí versiona los `CICLO-*.md` (`!/CICLO-*.md`).
- **B6 (bajo): en el modo ramp de CMA, el motivo perdía el aviso del portal.** Si el portal no cubre el puerto («no
  matching»), CMA prueba el modo ramp. Si ahí no elige el lugar de entrega, ahora el motivo dice también lo que avisó
  CMA con el puerto.
- **B7 (bajo): el riesgo de NO ENVIADA nuevas, sin medir en la revisión.** Estaba medido desde el paso 0 (0 de 66), y lo
  volví a medir con la regla del commit 4.

**La revisión de este informe** (otro agente, de solo lectura, sobre el informe preliminar, el commit 4 y el `CLAUDE.md`
nuevo, sin correr nada pesado): 0 altos, 4 medios y 9 bajos. Verifiqué cada uno contra el código o contra las salidas
guardadas, y todos se sostienen. El censo completo de `3d9923e`, que corría mientras tanto, lo detuve en su preparación
(729 de 1575 copias): el commit 5 cambia el código, y el censo vale sobre el último. Cerré sus procesos por PID, después
de comprobar su línea de comando, y borré su carpeta de trabajo.
- **M1, «X CHILE» pasaba:** la regla del commit 4 pedía la palabra a la celda entera y quitaba el país después. Con «X
  CHILE», la palabra era «CHILE», la fila pasaba y COSCO buscaba «X» (lo reprodujo corriendo las dos funciones
  aisladas). El commit 5 pide la palabra al puerto ya sin el país, en la regla y en el origen de COSCO. El FRENO, otra
  vez: 0 de 66.
- **M2 y M3, dos cifras que copié de mis notas y no de las salidas:** las tarjetas repetidas están en 7 de las 8 listas,
  no en 6 (todas menos la del 24-09), y son dos las del 27-09 sin «Search more», no una. Y no «cada lugar» viene dos
  veces: solo cada Container Yard, repetida como Store Door (5 pares en las 4 listas, con 4 textos distintos). Lo
  corregí en el resumen, la parte 1, las preguntas y `CLAUDE.md`. La pregunta 1 no cambia: «la única» por el texto sigue
  sin cumplirse justo en las Container Yard.
- **M4, nueve sondas sin su salida guardada:** las volví a correr guardándola (`sondas_otra_vez.sh`, más `freno_m1.py` y
  `horarios_hoy.py` para los horarios de hoy), y dicen lo mismo que el informe. En el OCR de texto disperso, una de las
  5 capturas (`hmm_f9_destino`) llega a 2 lecturas, pero solo ampliada ×2 (×3, 1): sigue sin confirmar. «Más de 12
  países» no tenía respaldo, y la saqué: no cambia nada. Y al volver a medir vi que el informe daba la hora de
  `AQUASHIELD.py` como prueba del código con que corrió el panel, pero esa hora cambió con el commit 4: ahora lo dice
  por los commits.
- **Los 9 bajos:**
  1. las cuentas de los gates sumaban las mutaciones que entran por dos filtros: ahora van sin repetir
     (`gates_distintos.py`);
  2. la página falsa no anotaba el JavaScript ni los `get_by_*`: ahora sí (commit 5);
  3. «lo que se escribe» generalizaba (HYUNDAI escribe la celda entera, y el origen de COSCO, el puerto normalizado:
     `_ciudad_de` es la parte con que se busca); los cortes de ONE, MSC, el puerto de CMA y el origen de COSCO, cuando
     el ayudante corta él mismo, no dicen «no encontré una sugerencia que elegir»; y MAERSK corta también si la
     sugerencia que pulsó no quedó en el campo;
  4. MAERSK y CMA probablemente también pulsaban con «-» (sin medir), y «en los siete» no valía para el lugar de entrega
     de CMA, que pulsó la «ramp»;
  5. «los dos lectores» eran los dos caminos: los lectores no cambian;
  6. la premisa del código del panel no se seguía (pieza 5);
  7. cuando escribí «lo revisaron dos agentes», la segunda revisión todavía no estaba, y «tres de ellos» eran dos
     hallazgos medidos con tres mutaciones;
  8. la numeración de las opciones mezclaba la que empieza en cero con la que empieza en uno (ahora van con ordinales),
     y cuatro frases confundían: lo que funcionó y en qué corridas, la refutación de `CLAUDE.md`, lo que dará la fila 10
     y «SIN-CUPO por el destino», que no está probado;
  9. una fila con «-» en el destino final: la pregunta 5.

**La revisión final** (otro agente, de solo lectura, sobre el commit 5, el informe corregido y el `CLAUDE.md` nuevo, en
la copia del commit de documentación; corrió pruebas puntuales en esa copia y mutantes en su propia carpeta): 0 altos, 1
medio y 7 bajos. Verifiqué cada uno, y todos se sostienen. El commit 6 (`7ca9a98`) corrige el medio y los dos bajos del
código; lo demás, en el informe y en `CLAUDE.md`:
- **M1, la página falsa no veía el teclado, el mouse, `select_option` ni el marco de COSCO:** midió 4 mutantes que
  seguían por esas vías después del ayudante que no eligió, y pasaban la prueba. Ahora la página los anota (sin un
  `__getattr__` general, porque lo que no tiene tiene que seguir fallando), el marco de COSCO anota en la misma lista, y
  cada vía tiene su mutación.
- **B1, la mutación de `get_by_text` del commit 5 no medía lo que decía:** caía también con la página de antes, por el
  `AttributeError`. Ahora va en un try, como el código real, y solo la página nueva la hace caer.
- **B2 y B3, la regla del puerto:** solo descontaba «CHILE» al final («CHILE X», «Chile - X» o «CHILE 1» pasaban), y el
  commit 5 había dejado de mirar la celda tal como viene, así que «№», que al normalizarse da «NO», pasaba. El commit 6
  mide la palabra en la celda y en el puerto normalizado sin «CHILE» en ninguna posición (`_puerto_de_carga`). El FRENO,
  otra vez: 0 de 66. «CL» solo sigue pasando: es la pregunta 6.
- **B4 y B5, dos datos:** son 5 pares de textos repetidos en las 4 listas, no 4; y «las posiciones 7, 8 y 9» eran
  índices que empiezan en cero: son la 8.ª, la 9.ª y la 10.ª.
- **B6, `CLAUDE.md` y un docstring:** «ninguna corrida guardó una lista» valía hasta el 29-09; entre los cortes con
  texto propio faltaba el origen de COSCO; «con «-» o «X», la que lo trajera» se leía como medido en los siete; y el
  docstring de `_falta_en_la_fila` decía mal quiénes no miraban si eligieron (corregido en el commit 6).
- **B7, detalles del informe:** faltaban `aplicar_c5.py` y cómo se escribieron las pruebas; los bajos de la revisión
  anterior no estaban numerados; «los 6 de la tarde» se leía como una hora; y las listas se guardan desde `5a21f31`, no
  desde `448e3e4`.
- **Lo que encontró el precenso del commit 6:** dos mutaciones viejas de `_cosco_puerto_de_la_celda`
  (`cosco-origen-busca-el-pais-solo` y `cosco-origen-un-solo-chile`) ya no mordían: con «CHILE» solo o «CHILE CHILE»,
  `_puerto_de_carga` corta igual, y tapa lo que ellas rompen. Su prueba mira ahora directo el contrato de la
  normalización, y «CORONEL CHILE CHILE», que con la segunda cambia lo que escribe COSCO.
- **Lo que medí de la red de antes:** con la prueba de `5bb3bf0`, las vías del teclado, el mouse, `select_option` y el
  marco de COSCO pasaban (`antes_pasaba_c6.py`); con la del commit 6, muerden.
