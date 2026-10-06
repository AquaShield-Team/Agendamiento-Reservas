# Encargo 54: CMA-CGM se detiene si restringe el acceso o su página no termina de cargar

Base: `Agendamiento Reservas` @ `58ef1db` · árbol limpio (al empezar, 2026-10-06).

## En resumen

- **Lo que pasó a las 14:26, medido sin abrir el portal.** La corrida de «Solo iniciar sesión» empezó a las 14:26:19,
  y la portada cargó en 1,1 s, respondiendo 403. Era la verificación del dispositivo de DataDome: el OCR de la captura
  lee «Verificación del dispositivo ...». A los 5 s, a las 14:26:44, la página se recargó sola, volvió a responder 403,
  y quedó sin ningún marco de DataDome: esa es la página en blanco. El programa la dio por un desafío y pidió al
  operador que deslizara. La pausa del panel espera hasta 10 minutos sin escribir en `log.txt`: por eso el registro
  calla 6 minutos, hasta que el navegador se cerró, a las 14:32:35. Medido en el `log.txt` de la corrida, el historial
  del perfil, sus archivos de sesión y la captura.
- **A las 09:57, el acceso restringido** salió en el marco `geo.captcha-delivery.com/captcha/` de DataDome, con `t=fe`
  en su dirección: la dirección no dice que sea un bloqueo. Lo dice el texto, «El acceso está restringido
  temporalmente».
- **Las tres páginas de DataDome se reconocen sin abrir el portal** (el primer FRENA SI no se cumple). En `logs/` no
  hay ningún HTML de DataDome (0 de 887 HTML). Pero las 11 capturas de su verificación, leídas con OCR, dan el texto
  de cada página: el deslizador en 9, el acceso restringido en 1 y la verificación del dispositivo en 1. Los archivos de
  sesión del perfil dan el código HTTP de cada navegación (403 en las 4 que guardan, todas del 06-10) y la dirección
  de cada marco.
- **Cuánto tarda la portada normalmente:** de 1,1 a 3,7 s (mediana 2,0 s), en los 23 inicios de sesión de CMA de
  `logs/`, hasta el fin de su carga. Lo siguiente llega a lo más a los 7,0 s. El plazo es de **30 s** (unas 8 veces lo
  más largo medido), el mismo que Playwright ya le daba a la portada.
- **Hecho (decisión de Marcelo).** CMA-CGM se detiene, sin reintentar ni recargar, en tres casos:
  - con la página del acceso restringido, enseguida;
  - si la portada no responde en 30 s;
  - si DataDome se queda 30 s en su verificación o en una página vacía.

  Cada fila de CMA queda NO ENVIADA con un motivo que lo dice, y quedan la captura y el HTML. Las otras navieras siguen.
  El deslizador lo sigue pasando el operador, como antes. No hay ningún clic nuevo.
- **Antes y después, con las mismas páginas falsas** (contra `58ef1db`):
  - Con el acceso restringido, el programa de antes le pedía al operador que deslizara, y seguía esperando. El de ahora
    se detiene sin pedirle nada.
  - Con la verificación que queda vacía, el de antes, tras la pausa, daba la verificación por superada y seguía a
    buscar el menú en una página en blanco. El de ahora espera 30 s y se detiene.
- **Medido sin red, en Chrome 154 con el sandbox:** el detector de antes lee los marcos con `frame.evaluate`, que no
  tiene plazo; con un marco que no responde, no volvió en 40 s. Ahora todo lo que lee el detector tiene plazo: se rinde
  a los 1,5 s, y una lectura normal tarda de 0,01 a 0,15 s.
- **El disfraz no se tocó** (el segundo FRENA SI no se cumple): 0 líneas del diff nombran `STEALTH_JS`,
  `_args_chrome`, `ignore_default_args`, `_lanzar_navegador`, el sandbox o `resolver_cma_slider`. `test_candado` no
  cambió y pasa.
- **La suite pasa:** 642 pruebas (eran 617) en 987 s, y 0 cambios en los originales. **Mutaciones:** 1.919 (entran 54,
  cambian 4). **El censo de las áreas del cambio:**
  157 mutaciones y 209 pares, y todos muerden.

## 1. Lo que pasó a las 09:57 y a las 14:26

Medido en `logs/` (37 carpetas de corrida, 0 que no calcen con el patrón del programa), en el historial del perfil del
programa (`perfiles/<operador>/Default/History`, leído inmutable), en sus archivos de sesión
(`perfiles/<operador>/Default/Sessions/`, formato SNSS, leídos solo para leer) y, con OCR, en las capturas. No miré
ninguna captura real: el OCR imprime solo las líneas sin cifras y sin las palabras de 16 caracteres o más, así que no
salen la IP ni el ID de la página.

| hora | qué pasó | de dónde sale |
|---|---|---|
| 09:57:47 | INICIO, solo CMA-CGM; el navegador abre en 1,1 s | `log.txt` |
| 09:57:50 | la portada responde **403**; marco `geo.captcha-delivery.com/captcha/` con `t=fe` | archivo de sesión |
| 09:57:52 | «El acceso está restringido temporalmente»; el programa lo toma por un desafío y pide la pausa | captura (OCR) y `log.txt` |
| 09:58:01–06 | «esperando que deslices la flecha» (5 s y 10 s) | `log.txt` |
| 09:58:08 | una recarga (transición «reload»): **403** y el mismo marco | historial y archivo de sesión |
| 09:58:10 | el navegador se cierra; «Target page, context or browser has been closed»; REVISAR | `log.txt` |
| 14:26:19 | INICIO, solo CMA-CGM; el navegador tarda **19,3 s** en abrir (a las 09:57, 1,1 s) | `log.txt` |
| 14:26:39 | la portada responde **403** en 1,1 s; marco `geo.captcha-delivery.com/interstitial/` | `log.txt` y archivo de sesión |
| 14:26:41 | «Verificación del dispositivo ...»; la captura es 99 % blanca | captura (OCR) |
| 14:26:41 | el programa lo toma por un desafío y pide la pausa; desde ahí, 0 líneas en `log.txt` | `log.txt` |
| 14:26:44 | la página se recarga sola (en el historial, «link»: la pidió la página, no el programa): **403**, y su estado no trae ningún marco | historial y archivo de sesión |
| 14:32:35 | el navegador se cierra, tras 351,7 s en esa página | historial y archivos de sesión |
| 14:32:38 | termina la pausa; «Target page, context or browser has been closed»; REVISAR | `log.txt` |

- **Por qué el registro calla 6 minutos:** en el panel, la pausa (`_web_pausa`) espera hasta 10 minutos a que el
  operador pulse «Ya lo resolví» o «Detener», y lo escribe solo en el registro del panel, no en `log.txt`. A las
  09:57 la pausa terminó a los 4 s, por la hora de la primera línea de la espera que sigue, la de 180 s, que sí anota
  cada 5 s.
- **Por qué la página quedó en blanco:** a las 14:26:44 la página recargada respondió 403, y Chrome no guardó en su
  estado ningún marco: el de DataDome no llegó a cargarse. La captura de las 14:26:41 es de antes de la recarga.
- **El historial no guarda los marcos.** Chrome no anota en `History` las navegaciones de un marco: 0 visitas a
  `captcha-delivery.com` desde el 01-09, en 6.711. Sus direcciones salen de los archivos de sesión.
- **Si esa corrida ya usaba el código del encargo 53** (el sandbox, en commit desde las 12:26), no está medido: las
  líneas de `log.txt` del inicio de sesión no cambiaron con él. El navegador tardó 19,3 s en abrir, y a las 09:57,
  1,1 s; la causa no está medida. Los 403 los decide el servidor, antes de que la página se dibuje.

## 2. Cómo se reconoce cada página de DataDome, sin abrir el portal

En `logs/` no hay ningún HTML de una página de DataDome: de 887 HTML (299 de CMA), 0 traen `captcha-delivery`. Lo que
sí hay son las 11 capturas de su verificación (`cma_robot_desafio`, del 24-09 al 06-10), leídas con OCR, y los
archivos de sesión del perfil.

| página | capturas | lo que dice (OCR) | su marco | HTTP |
|---|---|---|---|---|
| el deslizador | 9 (del 24-09 al 06-10 a las 09:56) | «Nos aseguramos de que nos dirigimos a usted, y no a un robot.» y «Desliza hacia la derecha para asegurar tu acceso» | (no quedó en los archivos de sesión) | — |
| el acceso restringido | 1 (06-10, 09:57:52) | «El acceso está restringido temporalmente» | `geo.captcha-delivery.com/captcha/`, `t=fe` | 403 |
| la verificación del dispositivo | 1 (06-10, 14:26:41) | «Verificación del dispositivo ...» y «El contenido solicitado estará disponible después de la verificación.» | `geo.captcha-delivery.com/interstitial/` | 403 |
| la página vacía | 0 (no hay captura) | — | ninguno | 403 |

- **El deslizador y el acceso restringido dicen también «El bloqueo actual puede ser el resultado de diferentes
  causas»:** el bloqueo se reconoce por «restringido temporalmente», no por «bloqueo». Con «bloqueo», el deslizador se
  leería como acceso restringido, y su mutación lo muerde.
- **El valor `t=fe` de la dirección no distingue el acceso restringido:** lo trae su marco. El marco del deslizador no
  quedó en los archivos de sesión (Chrome conserva las últimas 2), así que no se pudo comparar.
- **El texto está en el marco de DataDome**, que es de otro sitio: Chrome lo aísla en otro proceso. Playwright lo lee
  igual (medido sin red, abajo). Que el texto real esté en el HTML del marco, y no dibujado, no está medido en el
  portal. Si no se pudiera leer, el marco cuenta como sin texto: la página queda como «vacía», y la corrida se detiene
  a los 30 s, con el motivo de la página que no terminó de cargar.

## 3. Cuánto tarda la portada normalmente

Medido en los 23 inicios de sesión de CMA de `logs/` (0 sin la línea de la carga, 0 carpetas sin `log.txt`), desde
«Abriendo cma-cgm.com...», que el programa escribe justo antes de navegar:

| tramo | n | mínimo | mediana | p90 | máximo |
|---|---|---|---|---|---|
| hasta el fin de la carga (`domcontentloaded` y la espera del título) | 23 | 1,1 s | 2,0 s | 3,1 s | 3,7 s |
| hasta «Abriendo menú de acceso» (sin DataDome en la portada) | 21 | 3,3 s | 4,4 s | — | 7,0 s |
| hasta el desafío (DataDome en la portada: 09:57 y 14:26 del 06-10) | 2 | 3,1 s | — | — | 3,7 s |

- La espera del título («home lista tras») no esperó en ninguno: 0 de 23.
- En el historial, la portada estuvo de 4,6 a 9,4 s antes del clic en «login», en los inicios de sesión normales.
- **El plazo: 30 s** (`CMA_ESPERA_PORTADA`, hipótesis): unas 8 veces lo más largo medido (3,7 s). DataDome tardó 5 s en
  recargar la página desde su verificación, en la única vez medida, así que el plazo le da 6 veces eso. Es también el
  plazo que Playwright le da a toda navegación (30 s, `DEFAULT_PLAYWRIGHT_TIMEOUT`, en `lib/utils/isomorphic/time.js`
  de Playwright 1.58): la portada no tenía otro.

## 4. Lo que hace el programa ahora

**El detector** (`_cma_datadome`) mira, sin pulsar ni navegar ni esperar, el texto de cada marco de la página y el
código HTTP del documento. De ahí dice qué muestra la página:

- **«bloqueo»**, el acceso restringido: algún marco dice «restringido temporalmente»;
- **«deslizador»**: algún marco dice «desliza hacia la derecha»;
- **«verificacion»**: el marco `/interstitial/` de DataDome, o su texto «verificación del dispositivo»;
- **«vacia»**: un documento 403 sin el marco de DataDome, o con su marco sin texto;
- **«otra»**: su marco, con un texto que no es ninguno de esos;
- **«»**: sin DataDome.

Cada lectura tiene plazo (1,5 s), y un marco que no responde cuenta como sin texto.

**La espera de DataDome** (`_cma_esperar_desafio`, la de siempre), antes de pedirle nada al operador:

- **Con el acceso restringido**, detiene la corrida de CMA enseguida.
- **Con la verificación o la página vacía**, espera hasta 30 s, mirando una vez por segundo y sin tocar nada.
  - Si DataDome deja pasar la página, sigue: «DataDome dejó pasar la página; sigo».
  - Si muestra el deslizador, se lo pide al operador, como antes.
  - Si no sale de ahí, detiene la corrida.
- **Con el deslizador, o con otra página de DataDome**, como antes: la pausa y la espera de 180 s. Si mientras tanto
  la página pasa al acceso restringido, detiene la corrida.

**La portada** tiene 30 s para cargar. Si no carga, la corrida de CMA se detiene. Hasta ahora, al vencer ese mismo
plazo de Playwright, el login terminaba con un error inesperado, y las filas quedaban sin estado.

**El detector de antes** (`_cma_es_robotcheck`), que decide si hay que esperar a DataDome, da ahora por página de
DataDome a todo documento que respondió 403, sin leer sus marcos. Así ve también la página vacía de las 14:26:44, que
el de antes daba por superada.

**La detención** (`_cma_detener`):

- dice en pantalla y en `log.txt`: «⛔ CMA-CGM restringió el acceso: su página dice «El acceso está restringido
  temporalmente». Me detengo sin reintentar ni recargar la página.» (o «La página de CMA-CGM no terminó de cargar en
  30 s (…)»);
- anota la dirección, sin su consulta;
- guarda la captura de la ventana, con un plazo de 5 s, y el HTML de la página y de cada marco, con plazo, sin el que
  traiga el usuario o la clave;
- deja el motivo en el Registro.

Después:

- **En el login**, no hay sesión, y la corrida sigue con la naviera siguiente.
- **En el panel y en la consola**, cada fila de CMA queda NO ENVIADA con el motivo, como las de MSC sin sesión.
- **En una reserva**, la fila queda NO ENVIADA, y las filas de CMA que siguen en la misma corrida, también, sin volver
  al portal: no se prueba el otro modo ni la fila siguiente.

Los motivos, en la planilla y en el panel:

- «CMA-CGM restringió el acceso: su página dice «El acceso está restringido temporalmente». La reserva no se envió, y
  el programa se detuvo sin reintentar ni recargar la página (la captura y el HTML, en la carpeta de la corrida)»;
- «la página de CMA-CGM no terminó de cargar en 30 s (la portada no respondió | DataDome no terminó de verificar el
  navegador | la página de DataDome quedó vacía). La reserva no se envió, …».

**En «Solo iniciar sesión»**, CMA-CGM detenida queda REVISAR, como un login que no entró, con su línea y su evidencia,
y las otras navieras siguen.

**Sin clics nuevos:** el detector y la evidencia solo leen, y la espera es la de la página (`wait_for_timeout`). Las
páginas falsas de las pruebas no tienen recarga, clics ni teclado: si el programa los usara, la prueba caería. La foto
de los clics genéricos de `test_clics` pasa sin cambios.

## 5. Medido sin red, en Chrome 154 con el sandbox

Con páginas locales inventadas que imitan lo medido: un documento 403 con el título «cma-cgm.com» y un marco de otro
sitio (`localhost` contra `127.0.0.1`) con las frases que leyó el OCR. Chrome se abrió con las opciones de
`_lanzar_navegador` (canal chrome, sandbox, `_args_chrome`, sin `--enable-automation`). Para la portada que no
responde, `www.cma-cgm.com` apuntaba a un puerto local que acepta la conexión y no contesta. Todo otro nombre no
existía (`--host-resolver-rules`), así que nada salió a la red.

**El instrumento:**

| lectura | marco que responde | marco que no responde (un bucle sin fin) |
|---|---|---|
| `frame.locator(':root').evaluate(js, timeout=1500)` (el texto, el HTML) | de 0,01 a 0,15 s | TimeoutError a los 1,5 s |
| `frame.evaluate(js)` (lo que usaba el detector de antes) | — | **no volvió en 40 s** (lo corté) |
| `page.screenshot()` | — | espera los 30 s de Playwright |
| `responseStatus` de la navegación | 403 y 200, como el `page.goto` | — |

**El cambio, de verdad** (con `CMA_ESPERA_PORTADA` en 5 s, para no esperar 30):

| página | qué hizo | cuándo |
|---|---|---|
| normal (200) | siguió enseguida, sin evidencia | — |
| acceso restringido | se detuvo; captura y 2 de 2 HTML | 0,3 s después de verla |
| deslizador | le pidió la pausa al operador, como antes | enseguida |
| verificación que no termina | esperó el plazo y se detuvo; «DataDome no terminó de verificar el navegador» | al vencer el plazo |
| verificación que pasa a una página normal a los 3 s | «DataDome dejó pasar la página; sigo» | unos 2 s después de verla |
| verificación que a los 3 s queda vacía (las 14:26) | esperó el plazo y se detuvo; «la página de DataDome quedó vacía» | al vencer el plazo |
| 403 vacía | ídem | al vencer el plazo |
| marco que no responde | se detuvo; sin captura (vence su plazo) y 1 de 2 HTML | 14,4 s la prueba entera (con el plazo de Playwright en la captura, 69,5 s) |
| portada que no responde (login) | se detuvo; «la portada no respondió» | 13,0 s la prueba entera (con el plazo de Playwright en la captura, 30,3 s) |

- **El plazo de la captura salió de esta medición.** En la primera vuelta, con el plazo de Playwright, la captura de
  la ventana esperaba 30 s con un marco que no responde: la detención tardaba 69,5 s. Ahora la captura de CMA detenida
  tiene 5 s (`CMA_CAPTURA_MS`; `Registro.captura` acepta un plazo). Además, el plazo de la verificación empieza a contar
  al verla, y no después de su captura.
- **Con la portada que no responde, la evidencia queda vacía:** mientras la navegación sigue pendiente, Playwright
  espera a que termine para capturar y para leer el HTML. Con el plazo de Playwright, la captura llegó a los 25 s; con
  el de 5 s, no hubo captura ni HTML, y `log.txt` lo dice. No hay página que guardar.
- En ningún HTML guardado quedaron las credenciales (inventadas) que llevaba la corrida.

## 6. Antes y después, con las mismas páginas falsas

`contra_head.py` corre `login_cma` con las páginas falsas de `tests/test_datadome.py` y un reloj falso, sobre el
programa de `58ef1db` y sobre el de ahora. La espera del deslizador cuenta con el reloj de verdad: la página falsa
corta a las 100 esperas.

| caso | antes (`58ef1db`) | ahora |
|---|---|---|
| la portada bloqueada (09:57) | «muestra verificación de seguridad»; le pide al operador que deslice, y sigue esperando (100 esperas, cortado) | se detiene, sin pedirle nada: «⛔ CMA-CGM restringió el acceso…» |
| la verificación y, a los 5 s, la página vacía (14:26) | le pide al operador; con la página vacía, «Verificación de CMA CGM superada ✓» y «Abriendo menú de acceso…» en una página en blanco | espera 30 s y se detiene: «⛔ La página de CMA-CGM no terminó de cargar en 30 s (la página de DataDome quedó vacía)…» |

## Pruebas y mutaciones

- **25 pruebas nuevas** (de 617 a 642):
  - `tests/test_datadome.py`, 21, con su página falsa de DataDome:
    - qué muestra cada página;
    - que lee solo con plazo;
    - el código HTTP;
    - el 403 en el detector de antes;
    - lo medido;
    - la detención con el acceso restringido, enseguida;
    - la verificación que no termina, y la que termina;
    - la página vacía, como a las 14:26;
    - el deslizador y otra página de DataDome, como antes;
    - lo que solo ve el detector de antes;
    - el acceso restringido mientras espera al operador;
    - la evidencia, con plazo y sin las credenciales;
    - la portada que no responde;
    - la portada bloqueada, sin buscar el menú;
    - otra falla del login, que sale como antes;
    - la reserva bloqueada en Click & Book, y la fila siguiente sin volver al portal;
    - que nada de lo que detiene CMA corre después de la guarda.
  - `tests/test_web.py`, 2: CMA detenida en el login deja sus filas NO ENVIADA, y no frena a las otras navieras.
  - `tests/test_consola.py`, 2: lo mismo en la planilla, y en «Solo iniciar sesión».
- **Una foto al día:** `test_cada_reservador_que_corta_esta_decorado` suma el decorador de CMA detenida, por dentro de
  los demás.
- **El arnés:** la captura falsa de `soporte.PaginaFalsa` acepta el plazo.
- **Mutaciones: 54 nuevas** (`e54-…`), y **4 reescritas** sobre las líneas que cambiaron, con el mismo id, la misma
  intención y las mismas pruebas:
  - los dos bucles de las filas sin la sesión (`msc-sin-sesion-panel-sin-estado` y
    `msc-sin-sesion-consola-sin-estado`);
  - el motivo de `_motivo_sin_sesion` (`e50-motivo-sin-sesion-fijo`);
  - la captura de la página entera (`captura-no-fuerza-la-pagina-entera`).

  De 1.865 a 1.919. Todas pasan el chequeo previo (`mut_viejos.py`: su texto viejo una sola vez, compilan, 0 pruebas
  sin mutación, 0 ids repetidos).
- **La suite pasa:** 642 pruebas en 987 s (de las 15:48 a las 16:11, con el plazo de 7.200 s), y 0 cambios en los
  4.541 originales fotografiados.
- **El censo de las áreas del cambio** (`alcance_censo.py`), 157 mutaciones y 209 pares:
  - las 54 nuevas;
  - las 4 reescritas;
  - las que caen en las funciones que cambiaron (en las grandes, a 15 líneas o menos de una línea cambiada);
  - las que nombran una prueba cuyo camino cambió.

  El resultado: 157 mutaciones distintas y 209 pares, y todos muerden (0 por tiempo agotado; el par más lento, 24 s),
  con el control de la copia sin mutar en verde y 0 cambios en los originales (de las 16:11 a las 16:31).

## Re-medir

Desde la carpeta del encargo, con `TEMP`, `TMP` y `TMPDIR` en ella (`entorno_e54.sh`); los de `e51/` y `e53/` son de
esos encargos y se usan tal cual:

- Las corridas de `logs/`: `python e51/corridas.py 20261005`; un `log.txt` enmascarado: `python e51/ver_log.py
  20261006_142619`.
- Las visitas a CMA del historial del perfil, con su duración: `python e54/portada_historial.py 2026-10-06`; las de
  DataDome (0: el historial no guarda los marcos): `python e54/desafios_historial.py 2026-09-01`.
- El código HTTP y los marcos de cada navegación, de los archivos de sesión: `python e54/sesiones_cma.py`.
- El texto de las capturas de DataDome, sin IP ni ID: `python e54/ocr_cma.py` y `python e54/ocr_cma.py --texto
  20261006_095452 20261006_095747 20261006_142619`.
- Cuánto tarda la portada: `python e54/portada_en_logs.py`.
- Los HTML de DataDome en `logs/` (0) y que el diff no toca el disfraz: los dos conteos de la sección «En resumen»,
  con `git diff 58ef1db -- AQUASHIELD.py`.
- El instrumento en Chrome, sin red: `python e54/medir_instrumento.py`, `python e54/con_tope.py 40 python -u
  e54/medir_instrumento.py --evaluar` y `python e54/medir_html.py`.
- El cambio en Chrome, sin red: `python e54/con_tope.py 400 python -u e54/simular_cma.py`.
- Antes y después: `python e54/contra_head.py <e54>/srcHEAD "C:\dev\Agendamiento Reservas"` (srcHEAD, con `git show
  58ef1db:<archivo>`).
- Las mutaciones: `python e54/mut_viejos.py e54- msc-sin-sesion e50-motivo-sin-sesion-fijo captura-no-fuerza`; el
  alcance del censo, `python e54/alcance_censo.py`.
- La suite: `python tests/correr.py` o, con el plazo de 7.200 s, `python e54/correr_sin_tope.py`; el censo de las
  áreas del cambio, `python e54/censo_e54.py`.

## NO retroceder

- **Reconocer el acceso restringido por «restringido temporalmente»**, no por «bloqueo»: el deslizador también dice «El
  bloqueo actual…», y se leería como acceso restringido.
- **Leer los marcos con plazo** (`_evaluar_con_plazo`): `frame.evaluate` no vuelve si el marco no responde.
- **Un documento 403 es de DataDome** en `_cma_es_robotcheck`: sin eso, la página vacía de las 14:26:44 pasaba por
  superada, y el login seguía en una página en blanco.
- **`CmaDetenida` deriva de `BaseException`**, como `ObjetivoNoEncontrado`: los `except Exception` del login y de la
  reserva se la tragarían, y la reserva seguiría con el modo siguiente.
- **El decorador de la reserva mira primero si CMA ya se detuvo:** sin eso, cada fila de CMA volvería al portal, y
  sería un reintento por fila.
- **El plazo de la verificación cuenta desde que se ve**, y la captura de CMA detenida tiene el suyo: sin eso, la
  detención esperaba el plazo de Playwright (69,5 s medidos).

## Defectos de instrumento

1. **El historial del perfil no guarda los marcos.** La primera sonda buscó en `History` las visitas a
   `captcha-delivery.com` y dio 0, un cero por construcción: Chrome no anota ahí las navegaciones de un marco. Las
   direcciones de los marcos y el código HTTP salieron de los archivos de sesión.
2. **Un `python -` con heredoc, sin el entorno del encargo** (`PYTHONIOENCODING`), no leyó bien la «ú» de «menú»: su
   texto viejo no calzó, y el script abortó antes de escribir. El script pasó a un archivo, escrito con Write.
3. **La primera medición del cambio en Chrome** mostró que la captura de la ventana esperaba los 30 s de Playwright con
   un marco que no responde: la detención tardaba 69,5 s. Lo corregí en el código (el plazo de la captura), no en el
   instrumento; queda aquí porque lo encontró la medición, no las pruebas.
4. **El reloj falso de las pruebas** se instalaba después de crear el Registro: las horas relativas de la salida
   salían negativas. Ahora el Registro nace con el reloj falso.
5. **El chequeo del largo de las líneas, antes de escribir,** frenó dos veces: 5 líneas en el cambio del código y 10 en
   el bloque de mutaciones. No se escribió nada hasta repartirlas (es el arreglo del defecto 4 del encargo 53).

## Premisas refutadas

1. **«La portada quedó cargando en blanco varios minutos»:** la portada cargó en 1,1 s, y respondió 403 con la
   verificación del dispositivo de DataDome. Lo que quedó en blanco fue la página que DataDome recargó a los 5 s,
   también 403, sin su marco. El programa estaba en la pausa del panel, esperando al operador. Y la corrida fue de las
   14:26:19 a las 14:32:38, no a las 14:30.
2. **Que la portada «no termine de cargar» se mida con su carga:** en los 23 inicios de sesión medidos, la portada
   cargó siempre, de 1,1 a 3,7 s, y a las 14:26 también. Lo que no terminaba era la verificación de DataDome. Por eso
   el plazo vale para las dos cosas: la portada, y la verificación o la página vacía de DataDome.

## Residual (lo decides tú)

1. **La causa de lo que mostró DataDome hoy** (el acceso restringido a las 09:57; la verificación y la página vacía a
   las 14:26) no se confirma sin el portal, como en el encargo 53. Que tu Chrome normal entrara sin problema apunta al
   perfil o al navegador del programa, no a la red; no está medido. Reapertura: que lo encargues.
2. **Si la corrida de las 14:26 ya usaba el sandbox** del encargo 53, y por qué el navegador tardó 19,3 s en abrir, no
   está medido.
3. **El texto de DataDome en otro idioma:** lo medido está en español (el idioma de Chrome en este equipo). Si DataDome
   lo mostrara en inglés, el acceso restringido sería «otra» página, e iría al operador, como antes.
4. **Que el texto del marco real se lea con `innerText`** no está medido en el portal. Si no se pudiera, la página
   quedaría como vacía, y la corrida se detendría a los 30 s con el motivo de la página que no terminó de cargar.
5. **La pausa del panel no se escribe en `log.txt`**, y por eso el registro de las 14:26 calla 6 minutos. Escribirla
   ahí es un cambio fuera del encargo: lo propongo.
6. **El detector de antes todavía lee sin plazo las páginas que no son 403** (las de CMA): un marco de CMA que no
   respondiera lo dejaría esperando. No pasó en ningún inicio de sesión de `logs/`; lo propongo.
7. **Las otras cuatro llamadas del login a la espera de DataDome**, las del menú, se detienen igual, porque es la misma
   función; pero sin una prueba que pase por cada una.
8. **Lo que no cubre:**
   - el deslizador que el operador no pasa en 180 s (sigue como antes: «Tiempo de espera agotado», y las filas sin
     estado);
   - Click & Book que no carga (su navegación sigue con el plazo de Playwright, y la reserva sigue como antes);
   - DataDome a mitad de una reserva, ya cargado Click & Book.
9. **Del encargo 53, sigue:** el disfraz que el programa ya traía, los dos resolvedores de desafíos y la escala de
   0,65.
10. **Las revisiones de ECC** (code-reviewer, python-reviewer, security-reviewer): se proponen, no se lanzaron.

## Reglas (`metodo-ciclo` v16)

- **Aplicadas:**
  - PASO 0: el universo de cada sonda, declarado, y re-medir contra HEAD antes de diseñar (las corridas de hoy, la
    carga de la portada, el antes y después contra `58ef1db`);
  - control positivo que aborta: el OCR con su imagen sintética; los archivos de sesión, que abortan si no leen ningún
    código HTTP de la portada; el instrumento en Chrome, con un marco que responde y uno que no;
  - «todo salto silencioso lleva contador»: carpetas sin `log.txt`, inicios sin la línea de la carga, capturas que no
    se abren, comandos de sesión de otro tipo; 0 o contados en cada uno;
  - el negativo tiene que morder: las mutaciones en el censo, y el antes y después contra `58ef1db`;
  - fuente única: un solo detector y una sola detención para el login y la reserva, y `_guardar_html_completo` con un
    plazo en vez de una copia;
  - cada reemplazo, su viejo una sola vez, escritura atómica, y el largo de las líneas antes de escribir;
  - el EOL: 0 CR;
  - el cambio y su guardián, en la misma operación;
  - el residual y las premisas refutadas, declarados;
  - frenar cuando la decisión es de negocio: la causa, el disfraz y lo que está fuera del encargo, propuesto.
- **Del módulo** (`CLAUDE.md`):
  - nunca importar `AQUASHIELD.py` desde la raíz en una prueba;
  - nunca el puerto 8765;
  - los datos de prueba inventados;
  - la raíz sin tocar mientras corre la suite;
  - la sonda de secretos antes de cada commit;
  - `test_candado`, sin cambios.
- **Choques:**
  1. Las reglas de ECC piden revisiones y agentes automáticos; las reglas permanentes, proponerlos: los propongo.
  2. «Datos de prueba inventados» y las frases de DataDome en las pruebas: son las que el OCR leyó en sus páginas, sin
     IP ni ID, y no son datos de clientes. Las pruebas del aviso de mantenimiento de CMA ya usan su texto así.
- No miré ninguna captura real en este encargo: el OCR imprime solo el texto sin cifras.

## Lo que dio en el repo

- `7a4b456` fix: CMA-CGM se detiene sin reintentar si restringe el acceso o su página no termina de cargar
  (`AQUASHIELD.py`, `tests/test_datadome.py`, `tests/test_web.py`, `tests/test_consola.py`, `tests/test_clics.py`,
  `tests/soporte.py` y `tests/mutaciones.py`).
- El commit de este informe, con `CLAUDE.md` y `LEEME.md` al día.
- Fuera del repo, en el entorno de la máquina (`~/.claude/CLAUDE.md`), dos filas nuevas:
  - `frame.evaluate` sin plazo con un marco que no responde, y su plan B;
  - los archivos de sesión de Chrome, que guardan el código HTTP de cada navegación y la dirección de cada marco, que
    el historial no guarda.
