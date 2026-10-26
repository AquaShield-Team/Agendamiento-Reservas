# Encargo 82 · Las fallas del colega del 23-10 y del 26-10: diagnóstico, y los dos arreglos de MSC

**Fecha:** 2026-10-26 · **Método:** `metodo-ciclo` v38, en Modo autónomo (por omisión).

Base: `Agendamiento Reservas` @ `c647a88` · árbol limpio · `origin/main` y `origin/estable` también en `c647a88`
(medido con `ls-remote`).

**Commits,** en `main` y sin push (lo pidió el encargo, y el repo es público), uno por causa del programa:
- `c1ee372`, causa B: MSC cierra la lista de un puerto que quedó abierta antes de «Search Schedule»;
- `cc0e2ac`, causa A: MSC vuelve a escribir el HS Code una vez si el portal no ofrece ninguna sugerencia;
- el de este informe.

## Lo que pidió el encargo

Diagnosticar las fallas del uso real del colega (el viernes 23-10, más de 100 reservas y 5 fallaron; hoy 26-10, HYUNDAI
dio error) y arreglar lo técnico y reversible, un commit por causa, con prueba, mutación y revisión de código. Separar lo
del programa de lo de la planilla, del portal o del `config.json` del colega. **FRENA SI** un arreglo cambia una regla
de negocio o un estado que ve el equipo, o toca el camino de una naviera que hoy funciona bien: frena solo esa causa.

**Los datos:** los dos `log.txt` y la evidencia del colega, en `1. pruebas/`. Antes de nada se comprobó con git que esa
carpeta está ignorada: `git check-ignore -v` la da por la regla `/*` de la lista blanca de `.gitignore` (línea 6), y
`git status --ignored` la muestra solo como ignorada. Son datos reales: no entran al repo, a los commits ni a este
informe. Las sondas imprimen solo cuentas, textos fijos del programa y del portal, y números de fila; las pruebas usan
datos inventados.

## La versión que corrió

**El viernes no corrió `c647a88`.** El log del 23-10 empieza a las 09:59, y `c647a88` se commiteó ese día a las 20:51.
Por los textos fijos que escribe el programa (cuántas veces sale cada uno en el log, y desde qué commit está o dejó de
estar en el código, con `git log -S`):
- «todavía no sabe reconocer la confirmación de», 44 veces: el texto de antes de `719280c` (encargo 77, 22-10 19:07);
- «no identifiqué su Submit sin ambigüedad», 11 veces: no está en `c647a88` (lo quitó `b71e804`, encargo 78).

Así que el viernes corrió una versión anterior a `719280c`. **Las 22 filas de CMA-CGM y de COSCO que quedaron ENVIADA –
REVISAR EN PORTAL son lo esperado de esa versión** (no reconocía la confirmación de ninguna de las dos), no una falla
nueva. Con `c647a88` habrían salido EMITIDA – CONFIRMAR POR CORREO si la página mostró la frase de envío, o ENVIADA –
REVISAR EN PORTAL si no (encargos 77 y 78).

La versión del 26-10 no se puede saber por sus textos: el log no trae ninguno que distinga.

## El viernes 23-10: 102 reservas, modo EMISIÓN

El candado estaba abierto (la variable del lanzador de emisión): **las reservas se enviaron de verdad.**

| Naviera | EMITIDA | ENVIADA – REVISAR EN PORTAL | NO ENVIADA |
|---|---|---|---|
| ONE | 19 | | |
| MSC | 33 | | 3 |
| CMA-CGM | | 11 | |
| COSCO | | 11 | |
| MAERSK | 23 | | 2 |
| **Total (102)** | **75** | **22** | **5** |

### Las 5 NO ENVIADA, por causa

| Causa | Filas | Paso | De quién es |
|---|---|---|---|
| **A** · MSC: el portal no ofreció ninguna sugerencia del HS Code en 7 s | 2 de 35 que llegaron al HS Code | Paso 3, «Harmonized Code» | Del portal (no contestó a tiempo); el programa no reintentaba. **Arreglado** (commit `cc0e2ac`) |
| **B** · MSC: la lista de sugerencias del destino quedó abierta encima de «Search Schedule» | 1 de 36 | Paso 2, «Search Schedule» | Del programa con el portal: el clic esperó 30 s sin poder darse, y el motivo decía «no encontré el botón». **Arreglado** (commit `c1ee372`) |
| **C** · MAERSK: el buscador del Shipper se abrió con otra pantalla, titulada «Search/Add party» | 2 de 25 | «Additional details», el Shipper | Del portal: una pantalla nueva del buscador. **FRENO:** aceptarla cambia una regla de Marcelo (encargo 38). Es la pregunta 1 |

Ninguna es de la planilla ni del `config.json` del colega.

**A · El HS Code de MSC** (filas con motivo «HS Code de MSC: no encontré la sugerencia del salmón…: el portal no ofreció
ninguna»):
- En las 33 filas que siguieron, el programa eligió el salmón de 1,5 a 2,1 s después de escribir «030313»; en las 17 de
  `logs/` de este equipo, lo mismo (1,5 a 2,1 s). En las 2 que cortaron, a los 7,4 y 7,5 s, sin ninguna sugerencia.
- Su captura y su HTML: el campo dice «030313», con el foco, y no hay ninguna lista a la vista (la lista del HS Code, 0
  elementos). El portal no contestó, o contestó tarde: no se sabe cuál.
- Las dos fueron en momentos distintos de la corrida (a los 16 y a los 32 minutos), con filas que sí la recibieron
  antes y después: no es una fila ni un destino.

**B · «Search Schedule» de MSC** (motivo «no encontré el botón «Search Schedule» o «Buscar»»):
- Las otras 35 filas lo pulsaron en 0,1 s. Esta, a los 30,0 s, «clic NO (no apareció)».
- Su captura y su HTML del corte: el botón está a la vista, y encima está abierta la lista del destino, con más de 100
  puertos (la lista completa, con el elegido marcado). En la captura de justo antes del clic (`msc_f<fila>_2a_ruta`) la
  lista se estaba abriendo, y el campo ya decía el puerto elegido.
- Lo que pasó en el programa: `click_si_existe` esperó a que el botón se viera (se veía) y lo pulsó con el clic de
  Playwright, que esperó sus 30 s a que el botón recibiera el clic: la lista lo tapaba. Al vencer, el programa lo anotó
  como «no apareció», y el motivo dijo «no encontré el botón». **El motivo era engañoso: el botón estaba.**
- En el HTML: abierta, el campo trae aria-expanded="true" y la lista se ve (los 36 HTML de las sugerencias del destino, y
  el del corte); cerrada, «false» y escondida (los dos puertos en los 33 HTML de la guarda).
- Por qué la lista se volvió a abrir no se sabe (pasó en 1 de 36).

**C · El buscador del Shipper de MAERSK** (motivo «pulsé el «Add» de la tarjeta «Shipper», pero el buscador que se abrió
no está titulado «Shipper»»):
- Las 25 filas pulsaron el «Add» de la tarjeta «Shipper» (AQUACHILE no venía puesta), y el buscador se abrió en 1,1 a
  1,7 s en todas.
- En 23, el buscador medido en el encargo 38: titulado «Shipper», con la pestaña «Previously used». En 2, otra pantalla:
  titulada «Search/Add party», con las pestañas «Favourite» y «Search», el texto «Click a card to add party.» y un botón
  «Cancel». Traía 3 tarjetas, una con AQUACHILE (el lector del programa la reconoce: `resultados=3`, `con_empresa=1`).
- Las dos filas con la pantalla nueva no fueron seguidas (la 1.ª y la 10.ª de MAERSK). En `logs/` de este equipo, 0 de
  20 HTML de buscador la traen.
- El programa hizo lo que manda la regla del encargo 38: no eligió nada en un buscador que no dice «Shipper», y la fila
  quedó NO ENVIADA.

### Lo que no es del programa: qué tiene que hacer el colega

1. **Revisar en el portal las 22 filas de CMA-CGM y de COSCO que quedaron ENVIADA – REVISAR EN PORTAL.** Se enviaron de
   verdad. Si la reserva quedó creada, anotar su número en la planilla; si no, hacerla de nuevo. Con la versión de hoy
   (`estable` en `c647a88`), las de COSCO y CMA-CGM con la frase de envío en la página salen EMITIDA – CONFIRMAR POR
   CORREO, con su número.
2. **Las 5 NO ENVIADA no se enviaron:** las 3 de MSC se pueden volver a correr cuando `estable` traiga los arreglos de
   este encargo (o hacerlas a mano); las 2 de MAERSK, a mano en el portal, hasta que Marcelo decida la pregunta 1.
3. **Tener el programa al día:** se actualiza solo desde `estable` al abrirlo con los `.bat` (encargo 60), siempre que el
   clon esté en la rama `estable`.

## Hoy 26-10: HYUNDAI, modo prueba

5 reservas, todas de HYUNDAI, con el candado cerrado: **las 5 NO ENVIADA, en el mismo paso:** «Contract No de HYUNDAI: no
encontré un contrato en las credenciales o en config.json → opciones → contratos_por_defecto → hyundai».
- **No es del programa: es el `config.json` del colega.** Su operador no tiene contrato de HYUNDAI en las credenciales,
  y `contratos_por_defecto → hyundai` está vacío (como en la plantilla, `config.example.json`, desde el encargo 44). El
  programa corta ahí a propósito: elegir un contrato sin saber cuál sería por su posición (decisión de Marcelo, encargo
  44).
- **No es el mismo error que ninguno del viernes:** el viernes no hubo filas de HYUNDAI.
- **Qué tiene que hacer el colega:** en el panel, **Credenciales → HYUNDAI → Contrato**, escribir el contrato de su
  cuenta y guardar; o en `config.json`, en `opciones → contratos_por_defecto → hyundai`. El número lo da Marcelo o la
  cuenta de HYUNDAI; no va en el repo.

## Causa B: la lista del puerto que quedó abierta

`_msc_cerrar_listas_abiertas`, al principio de `_msc_buscar_itinerarios`:
- **Lee, sin tocar nada,** si la lista de cada puerto está abierta (`_JS_MSC_LISTAS_DE_PUERTOS`: aria-expanded="true"
  en su campo, o la lista a la vista; `MSC_PUERTOS`, los dos combobox de Kendo de la ruta) y el texto de su campo.
- **Con las dos cerradas, sigue al clic:** el camino de siempre no cambia, salvo esa lectura (una prueba lo fija:
  una lectura y el clic, sin esperas ni líneas en el log). Si la lectura falla, sigue al clic, como antes.
- **Si una está abierta,** la cierra con el método de su combobox (`_JS_MSC_CERRAR_LISTA`: `close()`, que según la
  documentación de Kendo solo esconde la lista y no elige nada), espera 0,6 s y vuelve a leer. Si no pudo volver a leer,
  si sigue abierta o si el texto del campo cambió, **NO ENVIADA sin pulsar «Search Schedule»**, con el porqué en el
  motivo («Search Schedule de MSC: no encontré la lista de sugerencias de «Port of Discharge» cerrada, con el puerto
  elegido en su campo: quedó abierta (puede tapar el botón) y, al cerrarla, sigue abierta…»).
- **No cambia ningún estado ni regla:** la fila que hoy funciona hace lo mismo; la que hoy quedaba NO ENVIADA a los 30 s
  sigue, si la lista se cierra con el puerto elegido, y si no, queda NO ENVIADA enseguida y con el motivo verdadero.
- **Que `close()` cierre la lista en el portal sin cambiar el puerto no está probado en el portal:** por eso la
  comprobación de después. Medido sin red: con un combobox falso, `close()` se llama una vez y nada más.

## Causa A: el HS Code sin sugerencias

`_msc_set_hscode` (con `_msc_escribir_hs` y `MSC_SONDEOS_HS`):
- **Como antes,** escribe «030313», lee la lista cada 0,5 s hasta 14 veces (7 s) y elige solo la sugerencia del salmón.
- **Si en la 14.ª lectura no hay ninguna sugerencia a la vista,** borra el campo y lo vuelve a escribir, **una sola
  vez**, y lee otras 14. Si tampoco, NO ENVIADA con el mismo motivo de antes. Si en la 14.ª hay otras sin el salmón, no
  lo vuelve a escribir: NO ENVIADA, como antes. Como antes, decide con la última lectura.
- **Si algo falla desde que lo vuelve a escribir** (un clic, una tecla, una lectura), NO ENVIADA, con lo que falló en el
  motivo: el campo pudo quedar borrado, y sin esa escritura la fila habría quedado NO ENVIADA (revisión de código, M1).
- **Con la sugerencia en las primeras 14 lecturas, el camino no cambia** (una prueba fija las acciones y las esperas de
  ese camino).
- **No cambia ningún estado ni regla:** el salmón sigue siendo la única sugerencia que se elige, y sin él la fila queda
  NO ENVIADA.
- **Que escribirlo otra vez traiga la lista es una hipótesis** (no está probado en el portal): si el portal perdió el
  pedido, el segundo lo vuelve a pedir; si contestó tarde, la segunda espera ve la lista igual. Si el portal no
  contesta en 14 s, la fila queda NO ENVIADA, como hoy, unos 8 s más tarde.

## Causa C: el buscador nuevo de MAERSK (FRENO)

No se cambió nada. Aceptar la pantalla «Search/Add party» cambia la regla del encargo 38 (el buscador tiene que estar
titulado «Shipper»), y su forma de elegir y de cerrarse no está medida: es la pregunta 1. Mientras tanto, esas filas
quedan NO ENVIADA sin elegir nada, que es el lado seguro.

## Las suites

Sobre el árbol de cada commit, en un clon sin remoto y antes de commitearlo, con `TEMP`, `TMP` y `TMPDIR` en la carpeta
del encargo y el tope de 3.600 s de la corrida de unittest (como el encargo 76):

| Corrida | Resultado |
|---|---|
| Causa B: el censo de las mutaciones del encargo (`--filtro e82`, con las 3 de su revisión) | 20 mutaciones, 22 pares (15 de la causa B y las 5 del HS Code de entonces): todos muerden. Originales: 0 cambios |
| Causa B: el censo de las mutaciones de `test_search_schedule_sin_boton_corta` | 4 mutaciones, 5 pares: todos muerden |
| Causa B: la suite completa (árbol de `c1ee372`) | 898 pruebas, OK (1 omitida), 2.100 s. Originales: 0 cambios |
| Causa A: el censo de las mutaciones del HS Code (`--filtro hs`: las 4 de antes y las 9 nuevas) | 13 mutaciones, 15 pares: todos muerden. Originales: 0 cambios |
| Causa A: la suite completa (árbol de `cc0e2ac`) | 900 pruebas, OK (1 omitida), 2.141 s. Originales: 0 cambios |

Las compuertas de cada commit, en 0: la sonda de secretos (antes y después de agregar al índice), el barrido de datos
reales del encargo 72 sobre lo agregado y sobre el mensaje, **un barrido nuevo con las palabras de los datos del colega**
(`barrido_colega.py`: las de sus dos `log.txt` y las de los botones de su portal que el repo no trae en la base, 1.817;
0 líneas con coincidencias en cada commit y en cada mensaje), y la guarda de datos del hook. En el de este informe, el
barrido del encargo 72 da 5 líneas (esta explicación incluida), y las 5 son falsos positivos: lo que calza es una palabra de 5 letras del nombre de
una nave que está dentro de «AQUACHILE», el nombre de la empresa, que se publica a propósito (sin «AQUACHILE», 0 líneas;
medido sin imprimir el valor).

## Las revisiones de código

Una por diff, cada una con `code-reviewer` en un clon sin remoto, de a una.

**Causa B: APROBAR CON CAMBIOS**, sin CRITICAL ni HIGH.
- Corrió `test_clics.TestMsc` y la foto de clics genéricos (36, OK), `TestSinClicACiegas`, la evidencia y el candado
  (32, OK); las 12 mutaciones de entonces muerden; la guarda de datos sobre lo agregado, 0.
- Con las listas cerradas, el camino no cambia salvo una lectura; `close()` de Kendo, según su documentación, solo
  cierra la lista (lo que supone sin la versión del portal, lo separa); ningún `except` se traga el corte; no toca a otra
  naviera ni cambia un estado.

| # | Hallazgo | Qué hice |
|---|---|---|
| L1 | Sin prueba: el cierre que lanza una excepción, dos listas abiertas con una que no se cierra, y la duración de la espera (3 mutaciones suyas sobrevivían) | Las tres pruebas y sus tres mutaciones (`e82-lista-cierre-sin-try`, `-comprueba-solo-la-primera`, `-sin-plazo-del-cierre`), que muerden |
| L2 | La comprobación mira el texto del campo, no el valor interno del combobox | Al RESIDUAL: sin un caso que lo dispare |
| L3 | Un comentario daba por hecho lo que `close()` hace en el portal | Dice que es lo de la documentación de Kendo y que no está probado en el portal |
| L4 | Quedan ventanas: una lista que se abre después de la lectura, o después de la relectura | Al RESIDUAL: del tamaño del problema de hoy, y no empeoran nada |

**Causa A: APROBAR CON CAMBIOS**, sin CRITICAL ni HIGH.
- Corrió `TestMsc` y la foto (37, OK); las 5 mutaciones nuevas y las 4 de antes del HS Code muerden; las 2.602
  mutaciones tienen su texto una sola vez; los archivos sin CRLF, BOM ni invisibles; con la sugerencia en las primeras
  14 lecturas, el camino no cambia; la segunda escritura no puede elegir otra cosa que el salmón.

| # | Hallazgo | Qué hice |
|---|---|---|
| M1 | Si la segunda escritura (o una lectura de después) fallaba, el `except` general devolvía False y la reserva seguía con el HS Code borrado; sin esa escritura, la fila habría quedado NO ENVIADA | Desde que lo vuelve a escribir, lo que falle corta (NO ENVIADA, con lo que falló en el motivo); antes, como antes. Prueba nueva (`test_hs_si_falla_al_volver_a_escribirlo_corta`) y dos mutaciones |
| L1 | El código decide con la 14.ª lectura, y el docstring y `CLAUDE.md` decían «en esas 14»; las lecturas mezcladas no tenían prueba | El texto dice «en la 14.ª lectura»; dos casos de lecturas mezcladas y una mutación (`e82-hs-decide-con-cualquier-lectura`) |
| L2 | Ninguna mutación escribía de verdad una tercera vez | `e82-hs-tercera-escritura`, que muerde |
| L3 | Las referencias a este informe, que no existía | Este commit |

Los arreglos de las dos revisiones no tuvieron otra vuelta: van con sus pruebas y sus mutaciones en el censo.

## Decisiones que tomé solo

| Decisión | Por qué |
|---|---|
| Causa B: cerrar la lista con el método de su combobox, no con Escape ni con un clic | No pulsa ni elige nada; Escape lo quitó Marcelo en MAERSK (encargo 38); después se comprueba que se cerró y que el campo dice lo mismo |
| Causa B: mirar las listas justo antes de «Search Schedule», no después de elegir cada puerto | La de la fila se abrió más de un segundo después de elegir; con las listas cerradas, el camino solo suma una lectura |
| Causa B: con cualquier duda después de cerrarla, NO ENVIADA sin pulsar | Es lo que esa fila ya era, pero enseguida y con el motivo verdadero |
| Causa A: volver a escribirlo una vez, en vez de esperar más | Si el portal perdió el pedido, esperar no lo trae; y si contesta tarde, la segunda espera la ve igual |
| Causa A: decidir con la última lectura, como antes | No cambiar lo que hace una fila que hoy funciona |
| Causa C: FRENO | Aceptar la pantalla nueva cambia una regla de Marcelo (encargo 38): la pregunta 1 |
| HYUNDAI: no tocar el programa | El corte sin contrato es una decisión de Marcelo (encargo 44); lo resuelve el colega en su configuración |
| No arreglar el «no apareció» de `click_si_existe` cuando algo tapa el botón | Lo usan las seis navieras: toca caminos que funcionan. Al RESIDUAL |

## Errores propios, y cómo se vieron

| Error | Cómo se vio | Qué hice |
|---|---|---|
| Tres sondas imprimieron valores reales en la salida de la herramienta, en esta sesión: nombres de puertos (un tapado que solo miraba palabras en mayúscula), números de reserva (el estado de una fila, con su número) y el nombre de pila con que el portal muestra a quien inició sesión (el texto de un botón) | Al leer su salida | No salieron de la sesión: no están en el repo, en los commits ni en este informe. Las sondas siguientes tapan las palabras con mayúscula inicial y lo que va entre «», y no imprimen los botones del encabezado; y el barrido nuevo vigila esas palabras en lo que se commitea |
| Lancé la suite del primer arreglo sin su parte del `CLAUDE.md`, y después sobre un árbol que la revisión cambió | Al armar el commit | Las detuve, cerré por PID los procesos que la detención dejó vivos, y la corrí sobre el árbol final |
| Una mutación del primer arreglo nombraba una prueba que no podía morder, otra no cambiaba lo que hace el programa, y una sobrevivió (`e82-js-lista-sin-aria`) | Las dos primeras, al releerlas; la tercera, el censo | Quitadas o corregidas; la tercera, con un caso más en la prueba del JavaScript |
| Dos mutaciones del HS Code quedaron con su texto viejo desactualizado, al agregar una línea en medio | El censo («aparece 0 veces») | Al día; el censo, en verde |
| La sonda del Python (`-I`) no veía las librerías del usuario, y con el Python de la Store como padre, el de python.org las veía | El control positivo abortó, y la medición directa desde Bash dio otra cosa | Medido desde Bash, sin `-I` (abajo, «El Python de esta máquina») |

## El Python de esta máquina (para el entorno)

Medido el 2026-10-26 en este equipo, desde la herramienta Bash:
- `python` es el **3.13.15 de python.org** (`%LOCALAPPDATA%\Programs\Python\Python313`, carpeta creada el 2026-10-21 a las
  18:50), que va en el PATH del usuario antes del alias de la Store. **No trae playwright, openpyxl ni holidays.**
- El de la Store (`%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe`, 3.13.14) sí. Este encargo corrió todo con él.
- Lanzado como hijo del Python de la Store, el de python.org sí encuentra las tres librerías: una medición hecha así
  engaña.
- Para AQUASHIELD en este equipo: los `.bat` llaman `python` y `pythonw` del PATH, así que el próximo arranque usaría el
  de python.org, y los `.bat` le instalarían las librerías (`pip install --user`, con red). No lo probé.

## Preguntas para Marcelo

1. **¿Qué hago con la pantalla nueva del buscador del Shipper de MAERSK, «Search/Add party»?** El portal la mostró en 2
   de 25 filas (una pantalla de pruebas del portal, o el cambio que viene). Se abre desde el mismo «Add» de la tarjeta
   «Shipper», trae las tarjetas de las partes (una con AQUACHILE), las pestañas «Favourite» y «Search», el texto «Click
   a card to add party.» y un botón «Cancel».
   - (a) **Aceptarla en su propio encargo** (recomendado): la misma regla (una sola tarjeta con AQUACHILE, y después
     comprobar que la tarjeta «Shipper» la muestra), con la forma de elegir y de cerrar medida en los 2 HTML del colega.
     Cambia la regla del encargo 38, que pide el título «Shipper».
   - (b) **Dejarla así:** NO ENVIADA sin elegir nada, y esas filas a mano.

**Para que los arreglos lleguen al colega:** `c1ee372` y `cc0e2ac` están en `main`, sin subir. Le llegan cuando
subas `main` y avances `estable` (las dos cosas son tuyas; `estable`, después de probar).

## RESIDUAL

| Qué | Condición de reapertura |
|---|---|
| **Por qué la lista del destino de MSC se volvió a abrir** no se sabe (1 de 36). Una lista que se abra después de la lectura de antes de «Search Schedule», o una cerrada en la primera lectura que se abra antes de la segunda, no se ve (revisión de B, L4) | Otra fila con el mismo corte |
| **`close()` de Kendo en el portal** no está probado; la comprobación mira el texto del campo, no el valor interno del combobox (revisión de B, L2) | La primera fila que lo use: su log dice «la cierro sin elegir nada» y si el campo siguió igual |
| **Que volver a escribir el HS Code traiga la lista** es una hipótesis | La primera fila que lo use: su log dice «lo vuelvo a escribir» |
| **El HS Code que falla antes de volver a escribirlo** lo anota («HS Code err») y la reserva sigue sin él, como antes del encargo (lo vio la revisión de A) | Si Marcelo quiere que también corte; toca el camino de siempre de MSC |
| **`click_si_existe` dice «no apareció»** cuando el botón está a la vista y algo lo tapa (el clic de Playwright vence a los 30 s): el motivo «no encontré el botón» engaña | Un encargo propio: lo usan las seis navieras |
| **La lectura de las listas de MSC no tiene plazo**, como las otras de MSC: con la página colgada no vuelve | Si MSC se cuelga ahí |
| **Las 22 de CMA-CGM y COSCO del viernes** se enviaron y quedaron REVISAR: las revisa el colega en el portal | — |
| **El contrato de HYUNDAI del colega** | Cuando lo cargue, la corrida de HYUNDAI pasa ese paso |

## Re-medir

1. `python -B -P <e82>/resultados.py`: los estados por naviera y los motivos de cada corrida del colega, tapados.
2. `python -B -P <e82>/tiempos_hs.py` y `tiempos_shipper.py`: los tiempos del HS Code, de «Search Schedule» y del
   buscador del Shipper, por fila. `historia.py`: lo mismo en `logs/` de este equipo.
3. `python -B -P <e82>/sonda_pod.py` y `sonda_buscador.py`: la lista abierta y el título del buscador en los HTML del
   colega, con el JavaScript del programa.
4. Desde `tests/`: `python -m unittest test_clics.TestMsc`; y `python tests/correr.py --mutaciones --filtro e82`.

`<e82>` es la carpeta del encargo en el scratchpad de la sesión. No se versiona: las sondas leen la evidencia del colega
y `logs/`, que son datos reales, e imprimen solo cuentas, textos fijos y números de fila. Corren con el Python de la
Store (el `python` del PATH no trae playwright).

## NO retroceder

- **Con una lista de puertos de MSC abierta, nunca se pulsa «Search Schedule»:** se cierra sin elegir nada y se
  comprueba, o la fila queda NO ENVIADA.
- **El HS Code de MSC se escribe a lo más dos veces,** y solo la sugerencia del salmón se elige.
- **Un buscador del Shipper de MAERSK que no dice «Shipper» no se usa** mientras Marcelo no decida la pregunta 1.

## Reglas de método aplicadas

`metodo-ciclo` v38 (la misma del disco al empezar):
- los datos reales, solo leídos: la carpeta ignorada comprobada antes de nada, las sondas con su control positivo que
  aborta y con salidas tapadas, y un barrido de esos datos sobre lo que se commitea;
- el diagnóstico separa lo del programa de lo del portal y del colega, con la versión que corrió medida por sus textos;
- el FRENA SI, por causa: la C se frena y las demás siguen;
- cada caso con su prueba y su mutación; una revisión de código por diff, en un clon sin remoto, de a una;
- todas las suites antes de cada commit, sobre el árbol del commit;
- lo que está fuera del encargo se propone (el RESIDUAL), la base, sin push y el cierre sin esperas vivas.

Las del módulo: `test_candado` sin cambios, ningún dato real en lo versionado, y la sonda de secretos y la guarda antes
de cada commit.
