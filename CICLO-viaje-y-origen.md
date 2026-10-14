# Encargo 66 · El viaje de la fila en las seis navieras, y el panel que atiende solo a su página

**Base:** `C:\dev\Agendamiento Reservas` @ `2f68e0c` · árbol limpio al empezar.

Con `metodo-ciclo` v24 (el encabezado del archivo dice v24, la misma que la sesión tenía cargada). Lo guardado en
`logs/` se midió sin abrir ningún portal: `log.txt`, el HTML de las listas cargado en un Chromium sin red y, donde no
hay HTML, el OCR de las capturas, sin mirarlas. Ningún valor de la planilla ni de una corrida va en este informe: del
viaje, su forma (cada letra, A; cada cifra, 9).

## En resumen

- **Las seis navieras eligen ahora solo una salida que traiga el viaje de la fila,** con la regla de palabra entera
  que ya usaban MAERSK y COSCO. Si la nave está y ninguna de sus salidas lo trae, la fila queda NO ENVIADA, con el
  motivo, la captura y el HTML de la lista, sin elegir otra. Si la fila no trae viaje, todo sigue como antes.
- **No se activó el primer FRENA:** de las 62 reservas de ONE, MSC, HYUNDAI y CMA-CGM que llegaron a la guarda en
  `logs/`, ninguna de las medibles que llevaba el viaje de su fila habría quedado NO ENVIADA. En las cuatro, el portal
  muestra el viaje como una palabra suelta y escrito como en la planilla. Diez no se pueden medir: la planilla de esos
  días ya no está en el equipo. Están en «Las reservas guardadas».
- **El panel atiende solo a su propia página:** a `/api/` le hace falta una marca de la sesión que el panel pone en su
  página al servirla, y el pedido tiene que venir de su propio origen. Una página de otro sitio abierta en el mismo
  navegador ya no puede subirle una planilla, cambiar credenciales, armar una corrida ni apagarlo.
- **No se activó el segundo FRENA:** busqué cada uso del panel que no viene de su página, y ninguno se rompe. El
  lanzador lee la marca de la página del panel que ya está abierto. Una pestaña que quedó abierta de un panel que se
  reinició la renueva sola. La descarga va con la marca. El operador no ve nada distinto.
- **Sin clics nuevos:** el cambio solo quita clics (ya no elige otra salida). Lo único que se repite en un caso donde
  antes no pasaba es ampliar la búsqueda cuando la nave está sin el viaje: HYUNDAI y CMA-CGM con sus mismos botones,
  MSC bajando por la lista. Así lo hacían ya MAERSK y COSCO (ver «Lo decides tú»).
- **`test_candado` no cambió.** La suite pasa (817 OK); en el censo del área, de 875 pares muerden todos, después
  de un repaso (abajo); y el panel lo probé también en un navegador de verdad.

## Las reservas guardadas (el primer FRENA)

La pregunta: ¿alguna reserva que llegó a la guarda con el viaje de su fila habría quedado NO ENVIADA con la regla?
Para responderla hacen falta dos cosas por reserva: el viaje de su fila y el texto de la salida que eligió.

- **El universo:** las reservas de `logs/` que llegaron a la guarda (OK-EJEMPLO o EMITIDA): 91 en 23 corridas, 62 de
  ellas de ONE, MSC, HYUNDAI y CMA-CGM, en 19 corridas. MAERSK y COSCO ya comparaban el viaje. De las 45 carpetas de
  `logs/`, 15 son de solo iniciar sesión, y de las 30 con reservas, 23 traen alguna que llegó a la guarda.
- **El viaje de la fila:** de la planilla que hay en el equipo (la copia del 14-10, igual a la del 08-10). Trae dos
  hojas: CONSOLIDADO, las filas de las corridas desde el 26-09, y «respaldo», la CONSOLIDADO de 30 filas del 21 al
  25-09. Una reserva cuenta como medible solo si la nave de su fila en esa hoja es la de su cabecera en `log.txt`.
- **El texto de la salida elegida:** el que anotó `log.txt` (ONE, MSC y HYUNDAI anotan el enlace o el campo de la nave,
  con su viaje), el HTML de la lista corrido con el JavaScript del programa (CMA anota solo la nave; HYUNDAI, para
  rehacer la elección entera) o, sin nada de eso, el OCR de las capturas (las del 21-09).
- **La regla, por el camino real:** el programa de este encargo, cargado del árbol de trabajo en una sandbox, con su
  `_trae_el_viaje` y su JavaScript.

| Naviera | Llegaron a la guarda | Medibles: la regla deja la que eligió | No llevaban el viaje de su fila | No medibles |
|---|---|---|---|---|
| ONE | 14 | **14 de 14**: 9 por `log.txt`; las 5 EMITIDA del 21-09, por OCR (el viaje entero en la captura de la salida y en la de la revisión) | — | — |
| MSC | 16 | **10 de 10**: las 5 EMITIDA del 21-09, las 3 del 24 y 25-09, y las del 08 y el 14-10 | — | 6, del 26-09 al 02-10 |
| HYUNDAI | 16 | **8 de 8**: del 27-09 al 14-10; el código nuevo, sobre la lista guardada, elige la misma tarjeta | 8, del 21 al 25-09: **otra nave** | — |
| CMA-CGM | 16 | **11 de 11**: 6 por el HTML de la lista (del 30-09 al 08-10); las 5 EMITIDA del 21-09, por OCR | 1, la del 14-10: **otro viaje** | 4: 25-09 (dos) y 27 y 29-09 |

- **Las 8 de HYUNDAI con otra nave** (5 EMITIDA del 21-09, una del 24 y dos del 25-09): la salida elegida trae la
  primera palabra de la nave de la fila, el prefijo de la naviera, y no la segunda; la guarda del 24 y el 25-09 dice
  lo mismo. Es el defecto que se corrigió en `9051f43` («HYUNDAI aceptaba la primera palabra»). No llegaron a la guarda
  con el viaje de su fila: la regla nueva no las afecta en lo que pregunta el FRENA.
- **La de CMA-CGM del 14-10** eligió otro viaje, el caso del encargo 65: la regla la corta, como pediste.
- **Las 10 del 21-09 medidas por OCR** (5 de ONE y 5 de CMA-CGM, sin HTML): el viaje de la fila está entero, junto a la
  nave, en la captura de la salida elegida (ONE) o de la lista (CMA-CGM). Lo que miden es la forma: el portal lo escribe
  como la planilla. En CMA-CGM, la captura muestra la lista, y cuál de sus tarjetas se pulsó no se lee en ella.
- **Las 6 de MSC no medibles:** la fila 6 de CONSOLIDADO de esos días traía otra nave, y esa planilla ya no está. En su
  «Vessel / Voyage», el viaje del portal va como una palabra suelta, de forma AA999A, la misma de todos los viajes de
  MSC de las dos hojas.
- **Las 4 de CMA-CGM no medibles:** el 27 y el 29-09, la lista traía la nave solo con un viaje de forma AA9999A99, y la
  fila de esos días ya no está. Si pedía ese viaje, la regla lo encuentra: va como palabra suelta en la tarjeta. Si
  pedía otro, se armó con otro viaje. Las del 25-09 no tienen la lista guardada, y en su pantalla final no está el viaje
  de la fila de «respaldo», ni entero ni como parte de una palabra.
- **La forma, en las cuatro:** el viaje que muestra el portal es una palabra suelta. En ONE, en el enlace de la nave
  («NAVE VIAJE»); en MSC, en «Vessel / Voyage»; en HYUNDAI, entre paréntesis en «1st Vessel»; en CMA-CGM, en «Ref. de
  viaje». En ninguna reserva medible la planilla lo escribe distinto: con prefijo, ceros de más o un separador.
- **Controles que abortan:** COSCO, que ya comparaba el viaje, da SÍ en sus 15 reservas con la planilla de su corrida;
  una página sintética de CMA-CGM con la nave en dos tarjetas, la segunda con el viaje, elige la segunda; el OCR
  encuentra el viaje de la fila en las 3 reservas de COSCO del 22-09.

## Los usos del panel (el segundo FRENA)

El panel ahora rechaza con un 403 todo pedido que no viene de su página. Busqué quién más le habla, en el repo
(`actualizar.py`, los dos `.bat`, `AQUASHIELD_EMISION.py`, las pruebas) y en los generadores que están fuera de él. Le
hablan el navegador y el lanzador, nada más. Así queda cada uso:

| Uso | Antes | Ahora | Cómo lo medí |
|---|---|---|---|
| Abrir el panel desde el lanzador, un marcador o un enlace | Abre | Abre | `test_la_pagina_trae_su_marca_y_no_va_dentro_de_otra` |
| La página: cargar, sondear, subir la planilla, armar, detener, credenciales | Atiende | Atiende: cada pedido lleva la marca | `test_cada_pedido_con_la_marca_y_una_renovacion` (Node) y las de `test_web`, que hablan con el panel como la página |
| `localhost` en lugar de `127.0.0.1` | Atiende | Atiende | `test_con_la_marca_desde_su_pagina_atiende` |
| La descarga de la planilla | Una navegación a `/api/descargar` | Un pedido con la marca; el archivo se guarda con el mismo nombre | `test_la_descarga_con_la_marca` (Node) |
| El lanzador ante un panel abierto: pregunta su estado y su modo, y al ocioso le pide que se apague | Atiende | Atiende: el lanzador lee la marca de su página | `test_el_lanzador_pregunta_con_la_marca` y el relevo de siempre, con el panel en otro proceso |
| El lanzador ante un panel de antes del encargo 66 | Atiende | Atiende: sin marca en su página, pregunta como antes | Las pruebas del arranque con paneles falsos |
| Una pestaña abierta de un panel que se reinició | Seguía funcionando | Sigue: con el 403, lee la marca nueva de la página del panel y repite el pedido una vez | `test_cada_pedido_con_la_marca_y_una_renovacion` |
| Una página de otro sitio, o el panel dentro de otra página | Atendía | 403 | `test_pedido_ajeno`, `test_de_otro_origen_no_atiende_aunque_traiga_la_marca`, `test_api_sin_la_marca_no_atiende` |

**Medido también en un navegador de verdad** (el Chromium del panel lateral de la app), con un panel de prueba: el
programa del árbol de trabajo en una sandbox, con su configuración sintética, en el puerto 40411.

- **La página, como siempre:** cargó, pintó su modo y sondeó cada segundo, todo con 200. Su marca tiene 43 caracteres.
  Un pedido sin la marca dio 403, y la descarga, con la marca, pasó el control (400 «No hay planilla cargada.», porque
  no había planilla).
- **Desde otro origen** (la misma página abierta en `localhost:40411`, que para el navegador es otro sitio que
  `127.0.0.1:40411`): `POST /api/apagar` sin la marca, en el modo que no pide permiso al navegador, dio 403. Con ella,
  el navegador no lo mandó: antes preguntó con un `OPTIONS`, el panel no lo atiende (501), y el pedido se cortó. Pedir
  `/api/apagar` como imagen dio 403, y la página dentro de un marco, 403. El panel siguió vivo. Desde `localhost` hacia
  `localhost`, su propia página, atendió.
- **El reinicio:** apagué el panel desde su página y levanté otro en el mismo puerto, con otra marca. La pestaña que
  quedó abierta recibió 403 en seis sondeos seguidos, leyó la marca nueva de la página y siguió con 200. Su estado
  volvió a «Listo.» sin recargarla.

**Lo único que cambia, y solo una vez:** una pestaña abierta antes de que un equipo se actualice a esta versión tiene la
página vieja, que no manda la marca. Al reabrir el lanzador, el panel nuevo la rechaza, y ella deja de actualizarse; el
lanzador abre una pestaña nueva, que funciona. Si alguien usa la vieja, ve el texto del 403: «El panel no atiende este
pedido: no viene de su propia página. Si es la tuya, recárgala (F5).»

## Lo que cambió

**El viaje de la fila** (`_trae_el_viaje`, `_palabras_del_viaje`): cada palabra del viaje, entera y sin distinguir
mayúsculas, en lo que la salida muestra de su nave; su JavaScript calza con `_traeLaNave` y esas palabras. Sin viaje en
la fila, no hay nada que comparar.

- **ONE:** en el enlace de la nave de la tarjeta; su clic lo vuelve a leer antes de pulsar. No amplía: lo decide en sus
  8 semanas, y la lista queda en `one_f<fila>_detenida`.
- **MSC:** en «Vessel / Voyage» (`_msc_es_la_pedida`); baja por la lista también con la nave sin el viaje, y la lista
  queda en `msc_f<fila>_itinerarios`.
- **HYUNDAI:** en «1st Vessel», donde el viaje va entre paréntesis (`_hmm_es_la_pedida`); su clic lo vuelve a leer;
  amplía «Duration» también con la nave sin el viaje, y la lista queda en `hmm_f<fila>_naves` y `_naves_mas`. En la
  interfaz anterior (sin «Book Now»), la tarjeta tiene que traer también las palabras del viaje.
- **CMA-CGM:** en el texto de la tarjeta (`_JS_CMA_RUTAS`, que pulsa en el mismo JavaScript); carga más rutas también
  con la nave sin el viaje, y la lista queda en `cma_f<fila>_rutas` y `_mas…`. El motivo dice además hasta qué fecha
  buscó.
- El motivo, en las cuatro: «ninguna de las N opciones de la nave trae el viaje de la fila», el mismo de MAERSK y COSCO.
- `_y_el_transito` cuenta las salidas empatadas con una suma en lugar de `list.count`: mismo resultado, y la foto de las
  lecturas sin plazo de CMA-CGM ya no la confunde con el `count` de Playwright (ver «Defectos de instrumento»).

**El panel** (`_pedido_ajeno`):

- **La marca de la sesión:** al arrancar, cada panel crea una al azar (`secrets.token_urlsafe(32)`, 43 caracteres) y la
  pone en su página. La página la manda en la cabecera `X-AquaShield-Sesion` con cada pedido a `/api/`, y el panel la
  compara con `hmac.compare_digest`. El navegador no le deja a una página de otro sitio leer la del panel, así que no
  puede saberla.
- **El origen:** el `Host` tiene que ser `127.0.0.1` o `localhost` con el puerto del panel; una dirección de otro sitio
  que apunte a esta máquina no llega. El `Origin`, si viene, tiene que ser el de su página, y `Sec-Fetch-Site`, si
  viene, `same-origin`. Su página se abre desde cualquier lado, pero no dentro de otra: `Sec-Fetch-Dest`,
  `X-Frame-Options: DENY` y `frame-ancestors 'none'`. Un pedido sin esas cabeceras, como el del lanzador, pasa solo con
  la marca.
- **El lanzador** (`_sesion_del_panel`) lee la marca de la página del panel antes de preguntarle, y con ella le pide
  que se apague. Si su página no la trae (un panel de antes), pregunta como antes.
- **La página** manda la marca con cada pedido (`pedir`), y si el panel contesta 403, lee la marca de la página del
  panel y repite el pedido una sola vez (`renovarSesion`). La descarga va por ahí.

## Decisiones que tomé

No es Modo autónomo: estas son decisiones de implementación dentro de lo que decidiste, y van aquí para que las veas.

| Decisión | Por qué |
|---|---|
| HYUNDAI y CMA-CGM amplían y MSC baja por la lista también cuando la nave está sin el viaje de la fila | Es lo que hacen MAERSK y COSCO desde el encargo 32: «si no se ofrece» se decide después de mirar lo que el portal deja ver. Son sus mismos botones, por su texto; ninguna forma de clic nueva |
| El lanzador lee la marca de la página del panel, como la página | Sin marca, el lanzador tomaría por «otro programa» a cada panel abierto, y abriría otro al lado. Quien puede leer la página del panel ya es la página o un programa de este equipo |
| La pestaña de un panel reiniciado renueva la marca sola, una vez | Sin eso, cada vez que el lanzador renueva un panel ocioso, la pestaña que quedó abierta dejaría de funcionar. Solo una página del mismo origen puede leer la marca nueva |
| La descarga, por un pedido y no por una navegación | Una navegación no puede llevar la marca, y la alternativa, ponerla en la dirección, la dejaría en el historial del navegador |
| Un pedido sin `Origin` ni `Sec-Fetch-*` pasa con la marca | Así habla el lanzador, y así hablaría un navegador viejo; la marca sola ya no la tiene otra página |
| `_msc_es_la_pedida` compara el campo tal como lo lee la página | Normalizarlo como `reservar_msc` no cambiaba nada (la regla ya separa por cualquier signo y no distingue mayúsculas): era una línea sin guardián posible |

## Lo decides tú

- **Si HYUNDAI, CMA-CGM y MSC deben ampliar también por el viaje.** Hoy sí (arriba). Si prefieres que, con la nave a la
  vista sin ese viaje, corten sin pulsar «Duration», «Cargar … siguientes resultados» ni bajar, es una línea en cada
  una.
- **La fila 7 de CMA-CGM** sigue con un viaje que el portal ya no ofrece: con este cambio, la próxima corrida la deja NO
  ENVIADA en lugar de armarla con otro viaje. Para probar CMA-CGM hasta la guarda, cámbiale el viaje por uno que esté
  en su lista.

## Verificación

- **La suite, sobre lo que se commitea:**
  817 pruebas OK en 776 s (`tests/correr.py`, lanzada aparte a las 19:25); la foto de los 5.253 originales, 0 cambios.
  Antes había pasado entera una vez (817 OK en 1.289 s), antes de los tres últimos cambios: el nombre de una variable
  de `_y_el_transito`, la espera de 40 s de una prueba del arranque y el caso nuevo de
  `test_panel_en_dice_quien_contesta`.
- **El censo del área** (`alcance_censo.py`, `censo_e66.py`), lanzado aparte y en su tercer intento (los dos primeros
  cayeron en su control: ver «Defectos de instrumento»):
  - **Qué entró:** las 58 mutaciones del encargo y las 13 re-ancladas; las que caen a 15 líneas o menos de una línea
    cambiada de `AQUASHIELD.py`; y las que nombran una prueba cuyo camino cambió: la elección de la salida de ONE, MSC,
    HYUNDAI y CMA-CGM (`TestOne`, `TestMsc`, `TestHyundai`, `TestCma`), el panel que pide la marca y el arranque
    (`TestPanelSoloSuPagina`, `TestArranqueDelPanel`, `TestPanelRutas`), la página que la manda, la regla de la nave y
    del viaje, `test_candado`, y las de `test_datadome` que corren `reservar_cma`. Las demás de `test_web` hablan con el
    panel por `soporte.Servidor`, que manda la marca: las corre la suite.
  - **668 mutaciones, 875 pares y 255 pruebas: el control pasa, y muerden 874.** Las 58 del encargo muerden todas.
  - **La que no mordía** era vieja, `e52-panel-en-cierre-como-nadie`, y la dejó así mi cambio: el lanzador lee la página
    antes de `/api/estado`, y esa lectura ya decidía el caso de su prueba. Le agregué a la prueba el caso de una página
    que contesta y un `/api/estado` que cierra sin contestar, y sumé la mutación de la rama nueva
    (`e66-pagina-cierra-como-nadie`).
  - **El equipo entró en reposo de 17:53 a 18:38** (eventos 506 y 507 de Kernel-Power), con el censo andando: cuatro
    pares vencieron su plazo de 240 s y salieron «muerde» por tiempo, no por su prueba.
  - **El repaso** (`censo_e66_repaso.py`): esas cuatro, la vieja con su prueba nueva y la mutación nueva, 7 pares:
    muerden los 7.
  - En los tres intentos y en el repaso, la foto de los 5.253 originales dio 0 cambios.
- **El chequeo de las 2.321 mutaciones** (`mut_viejos.py`): el texto viejo de cada una aparece una sola vez, las 72
  nuevas o re-ancladas (59 y 13) compilan, y cada una de las 817 pruebas tiene al menos una mutación.
- **La prueba en un navegador de verdad,** en «Los usos del panel».
- **El barrido de datos reales** (`barrido_diff.py`) sobre las 1.162 líneas agregadas del commit del arreglo, con los
  71 valores de 4 caracteres o más de la planilla, los `log.txt` y `config.json`, y su control (un valor de la
  planilla puesto a mano, que encuentra): 1 línea, un comentario de `AQUASHIELD.py` que nombra el país, que la máscara
  vigila porque va en el nombre de una nave de un `log.txt`; el programa publicado ya lo trae en 95 líneas. Ningún
  otro.

## Residual

- **MSC no vuelve a leer la tarjeta antes de su clic** (`_JS_MSC_CLIC_NAVE` pulsa la i-ésima): si la lista se
  repintara entre la lectura y el clic, pulsaría otra. Ya era así con la nave; ONE, HYUNDAI y CMA-CGM sí la vuelven a
  leer. Se reabre si lo encargas.
- **10 reservas guardadas no se pudieron medir** (6 de MSC y 4 de CMA-CGM): la planilla de esos días ya no está. Se
  reabre si aparece esa planilla.
- **El panel no se probó contra otro navegador que Chromium:** Chrome y Edge mandan `Sec-Fetch-*` y `Origin`; un
  navegador que no los mande pasa con la marca, igual que el lanzador. Se reabre si el equipo usa otro.
- Del encargo 65 siguen: leer el campo del contenedor después del clic en MAERSK; una prueba de la consola de HYUNDAI
  con la celda del contenedor vacía; «Cant. contenedores» como columna del contenedor; `_match_nav_key` con «Maersk
  (phone)»; MAERSK busca salidas «desde mañana»; CMA y COSCO sin `FORMA_BOOKING`.
- Las revisiones de código y de seguridad de este diff no se lanzaron: el encargo no es Modo autónomo. Las propongo
  antes de avanzar `estable`, sobre todo la de seguridad del panel.

## FRENA SI

- **El primero** (una reserva guardada que llegó a la guarda con su viaje y la regla cortaría): no se activó. En las 43
  medibles, ninguna; en las 4 navieras, el viaje del portal es una palabra suelta escrita como en la planilla.
- **El segundo** (validar el origen rompe un uso legítimo): no se activó. Cada uso de la tabla sigue funcionando; el
  único cambio es la pestaña vieja la primera vez que un equipo se actualiza.

## Premisas

- «Solo MAERSK y COSCO comparan el viaje»: **confirmada,** y un comentario de `reservar_msc` decía lo contrario
  («Solo se acepta la que calza con nave Y viaje»), sin que el código lo hiciera. Ahora es cierto.
- «En ONE, MSC y HYUNDAI hoy coincidió»: confirmada para el 14-10, y para todas las medibles desde el 21-09. Las 8 de
  HYUNDAI del 21 al 25-09, en cambio, se armaron con otra nave (el defecto ya corregido en `9051f43`).
- «El panel no valida de dónde le llegan los pedidos»: confirmada, y era más que eso. Atendía `GET /api/apagar`, que una
  imagen de otra página podía pedir, y un `POST` sin preflight (texto plano) podía armar una corrida con el modo que la
  página dijera.

## Defectos de instrumento (míos)

- **La primera sonda dio por medidas las reservas viejas con la planilla de hoy.** Tomaba el viaje de la fila de hoy
  si la nave coincidía, y COSCO, que ya comparaba el viaje, salía «NO» del 26-09 al 02-10: su fila tenía otro viaje
  esos días. Desde ahí, solo cuentan como medibles las reservas cuya fila es la de su corrida, y COSCO quedó de control.
- **El control de MAERSK no servía:** su `log.txt` anota solo la nave, no el viaje. Lo cambié por COSCO.
- **CMA-CGM anota solo la nave:** su regla, medida con su `log.txt`, daba «NO» en todas. Se midió en el HTML de su
  lista.
- **Un comando imprimió en mi pantalla el nombre del operador**, que los `log.txt` de solo login traen en su primera
  línea. No quedó en ningún archivo ni en este informe.
- **Bash juntó las barras invertidas** de un `sed` y de un heredoc (dos veces): las dos fallaron antes de escribir, y lo
  hice con Write o Edit.
- **La primera corrida de las pruebas del panel usaba el servidor de prueba con el módulo:** el panel de un proceso
  hijo no tiene módulo, y sus pruebas no habrían podido leer la marca. La corté antes de que terminara, y no dejó
  procesos vivos (lo comprobé por línea de comandos); `soporte.Servidor` lee ahora la marca de la página por su cuenta.
- **El lanzador no pedía apagarse a un panel de antes** si no podía leer su página: la lectura y el pedido iban en el
  mismo `try`. Lo vi en esa misma corrida, con los paneles falsos del arranque, y lo separé.
- Una prueba nueva comparaba `ast.unparse` con un texto escrito a mano, y `unparse` pone paréntesis en `not`: falló, y
  ahora compara con el `unparse` del texto esperado.
- **Corrí primero solo los módulos que creí afectados, y el censo cayó en su control** por uno que no había corrido:
  `test_datadome.test_ninguna_lectura_de_cma_sin_plazo` mira, sin correrlo, todo lo que alcanza `reservar_cma`, y con
  la regla nueva alcanza `_por_que_sin_salida` y, por ella, `_y_el_transito`, cuyo `tiempos.count(…)` (una lista) tomó
  por el `count` de Playwright. Cambié esa cuenta por una suma equivalente, y desde ahí la suite entera va antes que el
  censo. El censo no tocó nada: su foto de los originales dio 0 cambios.
- **Esa suma repitió el ancla de una mutación vieja** (`transito-el-mayor`, `menor = min(tiempos)`): lo vi en el alcance
  del censo ya lanzado, lo corté a los pocos segundos (sin cambios en el repo) y le cambié el nombre a la variable. Las
  132 pruebas de `test_datadome` y `test_ayudantes` pasaron con el nombre nuevo.
- **El segundo intento del censo cayó en su control por tiempo:** `test_panel_en_otro_modo_avisa_y_no_corre` espera 20 s
  a que conteste el panel de un proceso hijo, y con el equipo cargado no llegó. La prueba sola pasó dos veces (100 y
  134 s, con sus cuatro hijos). Le subí la espera a 40 s (`_esperar`, solo en la prueba); en la suite había pasado.

## Re-medir

- Las reservas guardadas, sin red y sin valores (en la carpeta del encargo): `calce_viaje.py` (los textos de
  `log.txt`), `rutas_viaje.py` (CMA-CGM sobre su HTML), `ocr_viaje.py` (las del 21-09, por OCR), `dudosas.py` (las de
  MSC y HYUNDAI sin su fila) y `camino_real.py` (la regla nueva, del árbol de trabajo, sobre todas).
- `python tests/correr.py` (la suite) y `python tests/correr.py --mutaciones --filtro e66-` (el censo de las mutaciones
  del encargo). El censo del área, con `alcance_censo.py` y `censo_e66.py`.
- Las pruebas del encargo: `test_ayudantes.TestViajeDeLaFila`, `test_clics.TestOne`, `TestMsc`, `TestHyundai`,
  `TestCma`, `test_web.TestPanelSoloSuPagina`, `test_web.TestArranqueDelPanel.test_el_lanzador_pregunta_con_la_marca` y
  `test_envio.TestMarcaDeLaSesion`.

## NO retroceder

- **Que una naviera elija por la nave sola cuando la fila trae viaje.** Es lo que armó la reserva de CMA-CGM del 14-10
  con otro viaje, «lista para emitir».
- **Que `/api/` atienda sin la marca, o que la marca vaya en la dirección.** Sin ella, cualquier página abierta en el
  navegador del operador puede armar una corrida; en la dirección, queda en el historial.
- **Que la descarga vuelva a ser una navegación:** no puede llevar la marca.
- **Que el lanzador pregunte sin leer antes la página:** tomaría a cada panel nuevo por otro programa y abriría otro.

## Reglas aplicadas

`metodo-ciclo` v24: el control positivo que aborta (en cada sonda: COSCO, la página sintética de CMA-CGM, el OCR de
COSCO, la máscara), la unidad de la medición (la reserva, no la corrida), medir por el camino real (la regla del árbol
de trabajo sobre lo guardado), el negativo que muerde (cada prueba nueva con su mutación, y el censo), fuente única
(la regla del viaje, una para las cuatro; la cabecera y la forma de la marca, comparadas entre Python, JavaScript y
`soporte`), cada reemplazo una sola vez y escritura atómica, el residual declarado, frenar cuando la decisión es de
negocio, y el cierre sin esperas vivas. Las del módulo: `test_candado` no cambia, ninguna prueba importa
`AQUASHIELD.py` de la raíz ni usa el puerto 8765, el mensaje de commit en un archivo UTF-8 sin BOM, la sonda de secretos
antes de cada commit, el correo noreply. No chocaron entre sí.

## El repo

Dos commits en `main`, sin push (el push lo haces tú):

- `0e816c6` fix: el viaje de la fila en las seis navieras y el panel que atiende solo a su página (`AQUASHIELD.py`, y en
  `tests/`: `soporte.py`, `test_ayudantes.py`, `test_clics.py`, `test_envio.py`, `test_web.py` y `mutaciones.py`);
- el commit siguiente, docs: `CLAUDE.md`, `LEEME.md` y este informe.

Los dos llevan de autor y de committer el correo noreply del repo, y la sonda de secretos dio 0 antes de cada uno. No
subí porque el repo es público: la consulta de control (`github/gitignore`) dio `false` y la del repo, `false`. En
GitHub, `main` y `estable` están en `2f68e0c`, la base de este encargo (medido con `ls-remote` al cerrar). Así, los
equipos de los colegas corren hoy el código en que ONE, MSC, HYUNDAI y CMA-CGM no miran el viaje: `estable` la avanzas
tú, después de subir `main` y de probar.
