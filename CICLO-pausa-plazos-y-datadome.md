# Encargo 55: la pausa del panel en log.txt, toda lectura de CMA-CGM con plazo, y DataDome a mitad de una reserva

Base: `Agendamiento Reservas` @ `54db6cb` · árbol limpio (al empezar, 2026-10-06).

## En resumen

- **La pausa del panel queda en `log.txt`** (decisión de Marcelo). Cuando el panel le pide al operador resolver algo,
  `log.txt` anota cuándo empieza y por qué (el mismo mensaje que ve el operador), y cuándo termina y cómo: con
  «Ya lo resolví», con «Detener» o a los 10 minutos sin respuesta, con los segundos que duró. Hasta ahora, de la pausa
  del deslizador de CMA, `log.txt` no decía nada, y de las demás, solo «PAUSA: esperando acción manual del
  operador...», sin el porqué ni el final: lo demás lo veía el registro del panel, que no se guarda. El 06-10, a las
  14:26, `log.txt` quedó 6 minutos sin escribir, y no se sabe con qué botón terminó esa pausa. Con «Detener», además,
  el registro del panel decía «Continuando (paso manual resuelto)»; ya no.
- **Toda lectura de las páginas de CMA-CGM tiene plazo** (decisión de Marcelo). Medido sin red en Chrome 154: con la
  página ocupada, o con una navegación que no termina, no vuelven seis lecturas de Playwright: `page.evaluate`,
  `title`, `content`, `count`, `is_visible` y `evaluate_all`.
  - `is_visible` tampoco vuelve a los 30 s de su plazo por omisión: ese plazo no corre.
  - Toda lectura a la que se le da `timeout` se rinde a su plazo, a los 1,5 s.
  - En lo que corre desde el login y la reserva de CMA había **57 lecturas sin plazo**, en 20 funciones. Ahora
    quedan 10, en 6 funciones, y ninguna corre en CMA sin una lectura con plazo que contestó justo antes, salvo una
    que CMA no alcanza (sección 1). El JavaScript, el título y el texto se leen con plazo. `count()` e `is_visible()`,
    que Playwright no deja leer con plazo, se leen solo si la página contesta antes una pregunta con plazo.
  - **Dos plazos.** Lo que mira si DataDome está sigue con los 1,5 s del encargo 54. Las demás lecturas de la reserva
    y del login usan el plazo por omisión de Playwright, 30 s, el mismo que en la reserva ya tenían `text_content`,
    `input_value` e `is_disabled`. Mi primera versión leía todo con 1,5 s. Mi revisión, leyendo el código, encontró
    que así una página ocupada un momento cambiaba lo que el programa hacía. Por ejemplo, si el JavaScript de los
    comentarios no vuelve, la reserva sigue sin ellos. Antes, el programa esperaba a la página. **El valor de 30 s
    lo decides tú** (residual).
  - **Una lectura sin respuesta no decide una elección.** Donde contar 0 o «no se ve» cambiaría lo que el programa
    elige, o le haría pulsar algo, la falta de respuesta no decide. Son tres lugares:
    - la sugerencia con «ramp» del lugar de entrega: la vuelta se repite;
    - «Añadir dirección de entrega»: no se pulsa;
    - la opción de «Tamaño y tipo»: el paso corta, y el motivo dice que la página no contestó.
- **DataDome a mitad de una reserva de CMA-CGM** (decisión de Marcelo). Lo reconoce el mismo detector del encargo 54,
  sin abrir el portal: el primer FRENA SI no se cumple.
  - Las 60 páginas de Click & Book guardadas en `logs/` cargan la etiqueta de DataDome, y con la opción
    `ajaxListenerPath: true`. Según la documentación pública de DataDome, con esa opción, cuando DataDome bloquea un
    pedido de la página, la etiqueta muestra su desafío en la misma página (el deslizador, la verificación del
    dispositivo o el bloqueo), y al dejarla pasar la recarga.
  - La reserva mira si DataDome está entre un paso y otro, y justo antes de la evidencia de la guarda. Su decorador
    también lo mira cuando la reserva se corta o queda REVISAR.
  - **Con el bloqueo, o con una verificación que no deja pasar en 30 s, CMA-CGM se detiene igual que en la portada:**
    NO ENVIADA con el motivo, la captura y el HTML, sin reintentar. Las otras filas de CMA quedan NO ENVIADA sin
    volver al portal, y las otras navieras siguen.
  - **El deslizador lo sigue pasando el operador.**
  - **Si DataDome deja pasar la página, la fila igual termina, NO ENVIADA.** Su motivo dice dónde apareció DataDome, y
    la corrida sigue con la fila que viene. Según la documentación de DataDome, al dejar pasar recarga la página (sin
    medir en el portal), y se pierde lo que se había llenado: seguir sería volver a intentarla. Es lo que decidí aquí,
    y **lo decides tú** (residual).
- **Sin clics nuevos, y el disfraz sin tocar:** el segundo FRENA SI no se cumple. Lo que corre desde el login y la
  reserva de CMA hace las mismas 66 acciones que antes. 0 líneas del diff del programa y de las pruebas nombran
  `STEALTH_JS`, `_args_chrome`, `ignore_default_args`, `_lanzar_navegador`, el sandbox o `resolver_cma_slider`; la
  misma búsqueda encuentra 12 líneas en el programa de `54db6cb`. `test_candado` no cambió y pasa.
- **Antes y después, con las mismas páginas falsas, contra `54db6cb`** (detalle en la sección 4):
  - **La pausa:** antes, de la del deslizador `log.txt` no decía nada, y de la de `pausa_manual`, solo que empezaba.
    Ahora anota su motivo y cómo terminó.
  - **Un corte en el origen con el bloqueo encima:** antes, la fila quedaba NO ENVIADA por «no encontré la
    sugerencia», y la fila siguiente volvía al portal. Ahora CMA-CGM se detiene con el motivo del bloqueo, y la
    siguiente no vuelve.
  - **REVISAR con la verificación encima:** antes quedaba REVISAR. Ahora es NO ENVIADA, por DataDome.
- **La suite pasa:** 676 pruebas en 670 s, y 0 cambios en los originales. **Mutaciones:** 2.004 (entran 85, se
  reescriben 48). **El censo de las áreas del cambio:** 502 mutaciones y 679 pares, y muerden 678. El que no era una
  prueba del encargo 54 que el decorador nuevo tapaba. La reforcé, y las 8 mutaciones que la nombran (16 pares)
  muerden.

## 1. Lo que se midió antes de cambiar nada

### La pausa de las 14:26

En el `log.txt` de esa corrida de «Solo iniciar sesión» (16 líneas, de las 14:26:19 a las 14:32:38; leído con
`log_1426.py`, que tapa el operador y las rutas), en orden:

- **14:26:41:** «CMA CGM muestra verificación de seguridad (DataDome: 'Desliza hacia la derecha')», y su captura;
- **6 minutos sin ninguna línea;**
- **14:32:38:** «ERROR inesperado: Page.wait_for_timeout: Target page, context or browser has been closed», y el
  login terminó REVISAR («tardó 359,7 s»).

`_cma_esperar_desafio` llamaba directamente a la pausa del panel (`on_pausa`), y la pausa del panel solo escribe en el
registro del panel, que no se guarda. Cuando terminó, la espera del deslizador siguió, y su primera espera falló porque
el navegador ya se había cerrado (a las 14:32:35: encargo 54). Las demás pausas del panel pasan por `pausa_manual`, que
dejaba en `log.txt` una sola línea, «PAUSA: esperando acción manual del operador...», sin el porqué ni el final.

Qué botón la terminó no queda en ningún lado. Desde este encargo, `log.txt` lo dice.

La pausa termina de tres maneras, todas en `_web_pausa`:

- con «Ya lo resolví» (`/api/continuar`);
- con «Detener» (`/api/detener`, que también suelta la pausa);
- o a los 10 minutos (300 vueltas de 2 s).

Hasta este encargo, con «Detener» el registro del panel decía «▸ Continuando (paso manual resuelto)». Las dos señales
quedaban puestas, y la pausa miraba primero la de continuar.

### Qué lecturas de Playwright no tienen plazo

Medido sin red, con páginas locales inventadas, en Chrome 154 (canal chrome, sandbox activado) y Playwright 1.58.0. Se
probaron 20 lecturas en 3 casos, cada par en su propio proceso, con un tope de afuera de 25 s: 60 corridas en 651 s
(`medir_lecturas.py`, `correr_lecturas.py`).

| lectura | página ocupada (su JavaScript en un bucle) | navegación que no termina | un marco de otro sitio ocupado |
|---|---|---|---|
| `page.evaluate` (con o sin argumento), `title`, `content` | no vuelve | no vuelve | 0,01 s |
| `count` (también con `filter` o `:visible`) | no vuelve | no vuelve | 0,02 s |
| `is_visible` | no vuelve (ni a los 48 s) | no vuelve (ni a los 52 s) | 0,03 s |
| `evaluate_all` | no vuelve | no vuelve | 0,05 s |
| `text_content`, `inner_text`, `input_value`, `get_attribute`, `is_disabled` con `timeout=1500` | TimeoutError, 1,5 s | TimeoutError, 1,5 s | 0,03 a 0,06 s |
| `wait_for_selector` y `locator(':root').evaluate` con `timeout=1500` | TimeoutError, 1,5 s | TimeoutError, 1,5 s | 0,05 s |
| `screenshot(timeout=1500)` | TimeoutError, 1,5 s | TimeoutError, 1,5 s | TimeoutError, 1,5 s |
| `page.url`, `page.frames` | 0,00 s | 0,00 s | 0,00 s |
| `wait_for_timeout(500)` | 0,52 s | 0,52 s | — |

Otras cuatro mediciones:

- **`text_content()` sin `timeout`** (el plazo de Playwright por omisión) se rindió a los 30,02 s con la página ocupada.
- **La pregunta con plazo** (`locator(':root').evaluate("() => true", timeout=1500)`) volvió en 0,04 s con la página
  libre, y se rindió a los 1,5 s en los otros dos casos.
- **El plazo de un localizador es el de encontrar el documento:** un JavaScript que corre 4 s, con `timeout=1500`,
  volvió a los 4,08 s con su valor.
- **Un JavaScript con argumento**, envuelto como `(_raiz, arg) => (<js>\n)(arg)`, volvió en 0,05 s con su valor.
  También cuando termina en un comentario.

Del código de Playwright 1.58 (`playwright/_impl`): `count()` y `title()` se piden sin plazo. `is_visible()` se pide con
el plazo por omisión, pero su lectura no se corta (medido arriba).

### Las lecturas de CMA, en el código

`inventario.py` mira lo que corre desde `login_cma` y `reservar_cma`: las funciones del módulo, contados sus
decoradores, y los métodos de `Registro` que usan. Antes, con `git show HEAD:AQUASHIELD.py`; ahora, con el archivo del
árbol (`contar_head.py` reparte las de antes por grupo):

| clase de llamada | antes (`54db6cb`) | ahora |
|---|---|---|
| funciones del módulo que corren | 79 | 88 |
| lecturas sin plazo | 57, en 20 funciones | 10, en 6 funciones |
| lecturas con el plazo de Playwright o uno dado | 18 | 20 |
| acciones (clics, teclas, escritura, navegación) | 66 | 66 |

Las 57 de antes:

- 5 del detector de antes (`_cma_es_robotcheck`): el título y el JavaScript de cada marco y de la página;
- 3 del login: el título y dos JavaScript;
- 40 de la reserva: `count()` (19), `is_visible()` (9) y `page.evaluate` (12, también el JavaScript que pulsa o
  escribe);
- 9 de los ayudantes comunes que CMA usa: `texto_pagina`, `click_si_existe`, la evidencia y, después de la guarda,
  `_pulsar_boton` y el número de la confirmación.

Las 10 de ahora:

- `count()` en `_cma_cuantos` e `is_visible()` en `_cma_se_ve`, detrás de la pregunta con plazo;
- en `_pulsar_boton`, `count()` e `is_visible()`, detrás de la pregunta cuando CMA le pasa el plazo, y sus dos
  `evaluate`, en la rama sin plazo, la de las otras navieras;
- en `click_si_existe`, el `evaluate` de la rama sin plazo;
- en `_guardar_html_completo`, el `evaluate` de la rama sin plazo, y `content()`, que con plazo corre solo si la lectura
  con plazo del HTML contestó, pero vacía (así desde el encargo 54);
- en `numero_tras_envio`, el `evaluate`, que CMA no alcanza: sin forma medida (`FORMA_BOOKING`), vuelve antes de leer.

Las acciones son las mismas 66: el cambio no agrega ningún clic.

### DataDome en las páginas de Click & Book

Medido en `logs/` sin abrir el portal (`html_cma.py`, `opcion_dd.py`). Universo: 887 HTML, 299 de ellos de CMA
(empiezan por «cma»), 0 ilegibles.

- **Las 60 páginas principales de CMA cargan la etiqueta de DataDome** (`js.datadome.co/tags.js`): todos los HTML que
  no son de un marco. Todas la cargan con una sola opción, `ajaxListenerPath: true`. Los otros 239 son de sus marcos, y
  no la traen.
- **El detector de antes no daría DataDome en ninguno de los 299:** ni sus palabras en el texto a la vista, ni su
  título, ni un iframe de desafío.
- **Lo que dice la documentación pública de DataDome** (sin medir en el portal):
  - `ajaxListenerPath` vale `true` por omisión: escucha los pedidos al mismo sitio y, si DataDome bloquea uno, la
    etiqueta muestra el desafío: el deslizador, la verificación del dispositivo o el bloqueo.
  - `disableAutoRefreshOnCaptchaPassed` vale `false`: al pasar el desafío, la etiqueta **recarga la página**.
  - `replayAfterChallenge` vale `false`: el pedido bloqueado no se repite.
  - `abortAsyncOnChallengeDisplay` vale `true`: el pedido bloqueado se aborta.

  La leí con la herramienta de lectura web, que resume: es lo afirmado por la documentación, no lo medido. Las páginas:
  - https://docs.datadome.co/docs/protect-singlepage-app
  - https://docs.datadome.co/docs/javascript-tag-customization
  - https://docs.datadome.co/docs/how-to-configure-the-javascript-tag
- **Por eso el detector del encargo 54 (`_cma_datadome`) sirve a mitad de la reserva.** Reconoce el desafío por la
  dirección de su marco (`captcha-delivery.com`, `/interstitial/`) y por sus frases, no por la página donde aparece.
- **El primer FRENA SI no se cumple:** reconocerlo no exige abrir el portal.

## 2. Lo que cambió

### La pausa del panel, en `log.txt`

`_pausa_del_panel` es la pausa del panel con sus líneas en `log.txt`. La usan `pausa_manual`, cuando hay un panel, y el
deslizador de CMA. Sus líneas:

- al empezar: «⏸ PAUSA: espero al operador. Por qué: <el mensaje que ve el operador>»;
- si terminó con «Ya lo resolví»: «▶ La pausa terminó a los N s: el operador pulsó «Ya lo resolví».»;
- si se cortó: «⛔ La pausa se cortó a los N s: …», con «el operador pulsó «Detener»» o «pasaron 10 minutos sin que el
  operador la resolviera»;
- si el panel no dice cómo terminó (el panel Tkinter): «▶ La pausa terminó a los N s.»;
- si el panel falla: «⛔ La pausa se cortó a los N s: falló el panel (…)», y la falla sigue su camino.

La hora la pone el Registro en cada línea.

`_web_pausa` devuelve ahora cómo terminó (`PAUSA_RESUELTA`, `PAUSA_DETENIDA`, `PAUSA_VENCIDA`). Mira «Detener» primero,
y con él ya no dice «Continuando». Sin panel, en la consola, `pausa_manual` hace lo mismo que antes.

### Toda lectura de CMA-CGM, con plazo

- **Dos plazos.** Las lecturas de la reserva y del login van con `CMA_PLAZO_MS` (30 s), el plazo por omisión de
  Playwright: el mismo que en la reserva ya tenían `text_content`, `input_value` e `is_disabled`, y con el que
  `text_content()` se rindió a los 30,02 s con la página ocupada (medido). Las que miran qué muestra DataDome, y el
  título de la verificación del dispositivo en el login, siguen con `CMA_LECTURA_MS` (1,5 s, encargo 54).
  - Con 1,5 s en la reserva, que fue mi primera versión, una página ocupada un momento cambiaba lo que el programa
    hacía, y antes la esperaba. Lo encontré revisando el código, sin medirlo en el portal: si el JavaScript de los
    comentarios no vuelve, `_cma_comentarios` lo anota y devuelve False, y `reservar_cma` sigue sin comentarios; si
    `count()` no contesta al buscar la sugerencia con «ramp», la regla cae a la primera de la lista.
- **El JavaScript** va por `_cma_js`: con plazo (`_evaluar_con_plazo`). Si no puede, levanta el error, como
  `page.evaluate`, y quien lo llama lo ataja como antes. Vale también para el que pulsa o escribe: es la misma
  llamada. Con argumento, `_evaluar_con_plazo` lo envuelve: el localizador le da primero su elemento.
- **El título y el texto** se leen con `_cma_leer`: el detector de antes y el título del login, con `CMA_LECTURA_MS`;
  el aviso de mantenimiento, con `CMA_PLAZO_MS`, porque con 1,5 s el de una página que todavía carga no se vería.
- **`count()` e `is_visible()`** van por `_cma_cuantos` y `_cma_se_ve`. Antes de cada una se le pregunta a la página,
  con plazo, si contesta (`_cma_responde`, `_responde`). Si no contesta, cuentan 0 y no se ve, como cuando Playwright
  no encontraba nada: donde se busca algo para pulsarlo o llenarlo, eso no pulsa nada.
- **Salvo donde eso cambiaría la elección** (`si_no_responde`): ahí la lectura sin respuesta no decide.
  - En el lugar de entrega, la regla es la primera sugerencia con «ramp», y si no hay, la primera. Si la página no
    contesta al buscar las de «ramp», en esa vuelta no se elige, y la vuelta se repite.
  - «Añadir dirección de entrega» se pulsa si su campo no se ve. Si la página no contesta, el campo cuenta como visto,
    y no se pulsa. Si el campo no está, el paso no lo encuentra, y la reserva se corta.
  - En «Tamaño y tipo», sin respuesta no se elige con esa lectura, ni con la segunda forma de buscar la opción, ni con
    su JavaScript de respaldo. El paso corta, NO ENVIADA, y el motivo termina «porque la página no contestó en 30 s»
    (`CMA_SIN_RESPUESTA`).
  - Revisé, leyendo el código, las 21 llamadas de CMA a `_cma_cuantos` y `_cma_se_ve`: 4 están en esos tres lugares.
    En las otras 17, un 0 o un «no se ve» no pulsa nada: la vuelta se repite, el paso corta, o el paso se salta como
    cuando no estaba.
- **Los ayudantes comunes reciben `plazo_ms`, y CMA se lo pasa:**
  - la evidencia: `_evidencia_antes_de_la_guarda`, `_evidencia_sin_sugerencia` y `_sin_clic_a_ciegas("cma", …)`;
  - el botón de entrar del login: `click_si_existe`;
  - después de la guarda: `_pulsar_boton`, `_resultado_envio` y `_guardar_evidencia`.

  Con las otras navieras no reciben plazo, y leen como antes. Después de la guarda solo se agregó la pregunta: si la
  página no contesta, CMA no pulsa el botón final, y la reserva queda NO ENVIADA (residual 17). El número de la
  confirmación (`numero_tras_envio`) CMA no lo lee: sin forma medida, vuelve antes de leer.
- **Las que ya tenían el plazo de Playwright lo conservan** (30 s): `text_content`, `input_value`, `is_disabled`, las
  esperas y las capturas. El `evaluate` del «Guardar» del panel Reefer, que es de un localizador y tenía ese plazo
  por omisión, ahora lo dice: `timeout=CMA_PLAZO_MS`, el mismo valor.

### DataDome a mitad de una reserva

- **`_cma_datadome_a_mitad`** solo lee y espera. Sin DataDome, no hace nada. Con él, hace lo mismo que la portada:
  - con el bloqueo, o con una verificación (o una página vacía) que no deja pasar en `CMA_ESPERA_PORTADA` (30 s),
    detiene la corrida (`_cma_detener`);
  - con el deslizador, o con otra página suya, se lo pide al operador (`_cma_pedir_deslizador`, que es la espera de
    antes, sacada de `_cma_esperar_desafio`).

  Si DataDome deja pasar la página, o el operador no desliza en `CMA_ESPERA_DESLIZADOR` (180 s), la fila termina:
  `_cma_interrumpir` deja su línea y su evidencia, `cma_f<fila>_datadome`, con plazo y sin las credenciales, y levanta
  `CmaInterrumpida`. Esa excepción deriva de `CmaDetenida`, pero no deja el motivo en el Registro, así que las filas
  que siguen van al portal. El motivo es `CMA_INTERRUMPIDA`: «DataDome interrumpió la reserva <dónde> (<cómo>). La
  reserva no se envió y no se volvió a intentar (la captura y el HTML, en la carpeta de la corrida)».
- **Dónde se mira**, en `reservar_cma`, siempre antes de la guarda:
  - tras el origen;
  - tras el destino (y el lugar de entrega);
  - tras «Validar ruta», después del camino de su aviso;
  - tras la información de la carga;
  - tras elegir la ruta;
  - tras el panel Reefer;
  - y en «Envío de la reserva», justo antes de la evidencia de la guarda.

  En el decorador (`_cma_si_se_detuvo`), cuando la reserva se corta (`ObjetivoNoEncontrado`) o queda REVISAR. El corte
  no se traga: si DataDome no está, sigue hasta `_sin_clic_a_ciegas`. Los errores no se miran, porque de un error no se
  sabe si salió antes de la guarda. El corte y REVISAR salen solo antes de ella, y así el decorador nunca mira después
  de la guarda (lo vigilan dos pruebas).
- **Al abrir el formulario**, si el deslizador no se pasa en 180 s, la fila también termina (`al abrir el formulario`).
  Hasta ahora la reserva seguía y se cortaba en el origen, y con el decorador nuevo eso habría vuelto a pedirle al
  operador que deslizara.

## 3. Lo que hace ahora

| qué pasa en una reserva de CMA-CGM | qué hace el programa | la fila | las filas de CMA que siguen |
|---|---|---|---|
| DataDome no aparece | nada nuevo: solo lee, con plazo | como antes | como antes |
| el acceso restringido, en cualquier paso | se detiene, con la captura y el HTML | NO ENVIADA (bloqueo) | NO ENVIADA, sin volver al portal |
| la verificación, que no deja pasar en 30 s | espera 30 s y se detiene | NO ENVIADA (no terminó de cargar) | NO ENVIADA, sin volver al portal |
| la verificación, que deja pasar | espera y termina la fila | NO ENVIADA (DataDome la interrumpió) | van al portal |
| el deslizador | se lo pide al operador, con la pausa en `log.txt` | NO ENVIADA (lo deslizó, o no en 180 s) | van al portal |
| un paso no encuentra su objetivo, sin DataDome | como antes | NO ENVIADA (el paso) | como antes |
| la página no contesta una lectura de la reserva en 30 s | la lectura cuenta como vacía, y nada se pulsa por eso | como antes, sin quedarse colgado | como antes |
| la página no contesta al elegir la sugerencia con «ramp», «Añadir dirección de entrega» o «Tamaño y tipo» | no elige con esa lectura | la vuelta se repite, o NO ENVIADA (el paso) | como antes |

## 4. Antes y después

`contra_head.py`, sin navegador ni red, con las páginas falsas de `tests/test_datadome.py`. Corre el programa de
`54db6cb` y el del árbol, cargados desde una copia:

| caso | antes (`54db6cb`) | ahora |
|---|---|---|
| `pausa_manual` con el panel, que termina con «Detener» | `log.txt`: «PAUSA: esperando acción manual del operador...», y nada más | «⏸ PAUSA: espero al operador. Por qué: <el mensaje>» y «⛔ La pausa se cortó a los 0 s: el operador pulsó «Detener».» |
| el deslizador de CMA en la portada, que el operador pasa | «CMA CGM muestra verificación de seguridad…» y nada de la pausa | lo mismo, y «⏸ PAUSA: … Por qué: CMA CGM: desliza la flecha…» y «▶ La pausa terminó a los 0 s: el operador pulsó «Ya lo resolví».» |
| la fila 9 se corta en el origen con el acceso restringido encima de Click & Book; después, la fila 10 | la reserva corre las dos filas, y las dos quedan NO ENVIADA por «no encontré la sugerencia del puerto»; de la página de la fila 9 lee 2 veces sin plazo | la reserva corre solo la fila 9; las dos quedan NO ENVIADA por el acceso restringido, con la captura y el HTML, y la fila 10 no vuelve al portal; de la página de la fila 9 lee 6 veces, todas con plazo |
| la fila 9 queda REVISAR con la verificación de DataDome encima, que deja pasar a los 2 s; la fila 10 queda REVISAR sin DataDome | las dos, REVISAR | la fila 9, NO ENVIADA: «DataDome interrumpió la reserva antes de quedar para revisar (dejó pasar la página después de su verificación)…», con `cma_f9_datadome`; la fila 10, REVISAR, como antes |

Los dos programas corren con la misma reserva falsa (la del corte y la de REVISAR), envuelta en sus decoradores de
cada versión, y con el mismo reloj falso. El nombre de la nave y el del puerto son inventados.

## 5. Pruebas, mutaciones, suite y censo

- **Pruebas nuevas, 34** (de 642 a 676):
  - en `test_datadome`: `TestLecturasConPlazo` (9), `TestSinRespuestaNoDecide` (3), `TestDataDomeAMitad` (9) y
    `TestReservaConDataDome` (9);
  - en `test_consola`: la pausa en `log.txt`, con cada final (1);
  - en `test_web`: `TestPausaDelPanel`, con cómo termina `_web_pausa` (3).
- **Las tres elecciones sin respuesta** (`TestSinRespuestaNoDecide`) corren el ayudante de verdad sobre una página
  falsa que contesta o no la pregunta con plazo, pregunta por pregunta (`PaginaQueContesta`). Cada una trae su control:
  con la página que contesta, el ayudante elige y pulsa como siempre.

  Además, `test_pausa_y_continuar` y `test_detener` (`test_web`) miran lo que devuelve la pausa,
  `test_deslizador_como_antes` (`test_datadome`) mira su pausa en `log.txt`, y
  `test_bloqueo_en_click_and_book_queda_no_enviada_y_no_sigue`, del encargo 54, exige una sola detención y ningún paso
  después (la reforcé después del censo).
- **La foto de las lecturas** (`test_ninguna_lectura_de_cma_sin_plazo`) recorre lo que corre desde `login_cma` y
  `reservar_cma`. Exige que las lecturas sin plazo de Playwright estén solo detrás de la pregunta con plazo, o en la
  rama sin plazo de los ayudantes comunes, y que CMA los llame con `plazo_ms`. Revertir cualquier lectura, o quitar el
  `plazo_ms` de una llamada, la hace caer.
- **Las páginas falsas leen por `locator(':root')`**, como el programa (`soporte.RaizFalsa`): dicen que la página
  responde, dan su título y responden lo demás con el `evaluate` de la página. Las que anotan cada JavaScript no
  anotan las dos lecturas con que CMA mira DataDome, como no anotan el HTML de la evidencia.
- **Fotos al día:**
  - el decorador de CMA, con su plazo;
  - la evidencia de la guarda y la de «Validar ruta», con plazo;
  - el envío de CMA, con plazo;
  - los pasos de CMA reemplazados en `test_clics`: su `_cma_esperar_desafio` falso dice que DataDome dejó pasar (hasta
    ahora nadie miraba lo que devolvía);
  - el JavaScript de los comentarios, buscado en cualquier argumento.
- **Mutaciones: 2.004** (eran 1.919). Entran 85, una al menos por prueba nueva: 71 con el primer cambio y 14 con la
  revisión. Se reescriben, con sus mismos ids y pruebas, las 48 anteriores que el cambio dejó sin ancla: 46 con el
  primer cambio (varias, arreglando la constante que nombran) y 2 con la revisión. La revisión movió también, al
  nombre nuevo del plazo o al código nuevo, las anclas de 12 mutaciones del encargo y de 28 de esas 46. `mut_viejos.py`
  da 0 problemas: cada texto viejo, una vez; las 85, compiladas; toda prueba, con su mutación.
- **La suite:** 676 pruebas, OK, en 670 s (672 s con la foto), y 0 cambios en las 4.542 entradas fotografiadas de los
  originales, sobre el árbol que se commitea: con el ajuste de la revisión, la prueba reforzada después del censo y
  `CLAUDE.md` y `LEEME.md` al día. Antes de reforzarla, la misma suite había pasado en 509 s
  (`correr_sin_tope.py`, la suite de siempre con el plazo de la corrida entera en 7.200 s). La primera versión también
  pasaba: 671 pruebas en 616 s. Después del ajuste corrieron antes `test_datadome` y `test_envio` (93 pruebas) y el
  censo chico.
- **El censo chico** (`censo_mini.py`), antes de la suite: las 14 mutaciones de la revisión y las 6 anclas que
  reescribí a mano. 20 mutaciones, 26 pares y 11 pruebas: el control (la copia sin mutar) pasa, los 26 pares muerden,
  0 no muerden, y 0 cambios en las 4.542 entradas fotografiadas de los originales.
- **El censo de las áreas del cambio** (`alcance_censo.py`, `censo_e55.py`) toma la unión de cuatro grupos:
  - las 85 del encargo;
  - las 48 reescritas;
  - las que caen en las funciones que cambiaron (197);
  - las que nombran una prueba cuyo camino cambió: las de CMA, las de la pausa, las fotos de los decoradores y de la
    evidencia (478).

  Son 502 mutaciones y 679 pares, sobre el árbol final. Corrió aparte (`lanzar_censo_e55.py`), de las 21:09 a las
  21:45. El control (la copia sin mutar, 196 pruebas) pasa, y hay 0 cambios en las 4.542 entradas fotografiadas de
  los originales. **Muerden 678 de los 679 pares.** El que no, `e54-detenida-de-exception` contra
  `test_datadome.TestReservaCma.test_bloqueo_en_click_and_book_queda_no_enviada_y_no_sigue`, es una mutación del
  encargo 54 que, con el cambio, esa prueba dejó de ver: el corredor da FALLA por ese par.
  - La mutación vuelve `CmaDetenida` una `Exception` común, y `_ir_al_form` se traga la detención al abrir el
    formulario. Desde este encargo, la reserva sigue al origen, se corta, y el decorador mira DataDome, lo encuentra y
    detiene otra vez, con el mismo resultado: el decorador nuevo tapaba la mutación (la quinta lectura de un negativo
    vacuo: enmascarado por la pieza que corre después).
  - Reforcé la prueba: la detención ocurre una sola vez, al abrir el formulario, y ningún paso corre después (ni una
    segunda línea «⛔ CMA-CGM restringió el acceso», ni «DataDome apareció a mitad de la reserva»).
  - El censo de las 8 mutaciones que nombran esa prueba (`censo_click_book.py`: 16 pares, 7 pruebas): el control
    pasa, **los 16 pares muerden**, también ese, y 0 cambios en los originales.

## Re-medir

Todo en `e55/` (carpeta del encargo), con `source entorno_e55.sh` antes.

| qué | cómo |
|---|---|
| las lecturas de Playwright (la tabla de la sección 1) | `python correr_lecturas.py 25` (escribe `lecturas.txt`); un par suelto: `python ../e54/con_tope.py 50 python medir_lecturas.py <caso> <lectura>` |
| las lecturas de CMA, antes y ahora | `python inventario.py` (HEAD), `python contar_head.py` (su reparto, sobre `inventario_head.txt`) y `python inventario.py "C:/dev/Agendamiento Reservas/AQUASHIELD.py"` |
| la etiqueta de DataDome en Click & Book | `python html_cma.py`, `python opcion_dd.py` |
| la pausa de las 14:26 | `python log_1426.py` (tapa el operador, las rutas, los correos y las consultas) |
| antes y después | `python contra_head.py fuentes_head` y `python contra_head.py fuentes_arbol` |
| las anclas de las mutaciones | `python mut_viejos.py e55` |
| el censo chico de la revisión | `python censo_mini.py` (escribe en la salida; 20 mutaciones, 26 pares) |
| el censo de la prueba reforzada | `python censo_click_book.py` (8 mutaciones, 16 pares) |
| las 21 llamadas que cuentan o miran si algo se ve | `grep -n "_cma_se_ve(page\|_cma_cuantos(page" AQUASHIELD.py` (en el repo; 23 con las dos definiciones) |
| el alcance del censo | `python alcance_censo.py` |
| la suite | `python tests/correr.py` (en el repo) |
| el censo | `python lanzar_censo_e55.py` (aparte, sin ventana; escribe `censo_e55.txt`) |

## NO retroceder

- **Lo que lee de las páginas de CMA-CGM va con plazo,** y no vuelve a `page.evaluate`, `title()`, `content()` ni a un
  `count()` o `is_visible()` sin la pregunta antes. Con la página ocupada, o con una navegación que no termina, no
  vuelven, y la corrida se queda colgada sin escribir nada.
- **Las lecturas de la reserva no vuelven a 1,5 s sin medir cuánto puede estar ocupada una página de CMA.** Con 1,5 s,
  una página ocupada un momento cambiaba lo que el programa hacía: los comentarios se saltaban, y la sugerencia con
  «ramp» caía a la primera.
- **Una lectura que no contesta no decide una elección:** la sugerencia con «ramp», «Añadir dirección de entrega» y la
  opción de «Tamaño y tipo» no se eligen ni se pulsan con ella (`si_no_responde`).
- **El decorador de CMA mira DataDome solo en el corte y en REVISAR,** que salen antes de la guarda. Si mirara también
  los errores o los otros resultados, podría convertir en NO ENVIADA una reserva cuyo envío salió.
- **El corte se vuelve a levantar** después de mirar DataDome: si no, se tragaría el corte.
- **La fila que DataDome interrumpió no se vuelve a intentar** dentro de la misma fila: la página se recarga, y
  seguir sería llenar de nuevo.
- **`_web_pausa` mira «Detener» antes que «Ya lo resolví»:** los dos sueltan la pausa.
- **La prueba del bloqueo al abrir Click & Book exige una sola detención y ningún paso después**
  (`test_bloqueo_en_click_and_book_queda_no_enviada_y_no_sigue`): sin eso, el decorador nuevo tapa una detención que
  la reserva se trague (lo encontró el censo).

## Defectos de instrumento

1. **Imprimí, en la salida de una herramienta, líneas de `log.txt` con el nombre del operador.** Venía en la línea de
   inicio y en las rutas. Fue en la primera versión de `log_1426.py`, que solo tapaba correos y cifras. Lo corregí: el
   script tapa `usuario=` y toda ruta, y no imprime si queda una ruta. El nombre no está en ningún archivo ni en este
   informe.
2. **La herramienta Bash convirtió `\\n` en un salto de línea** dentro de una edición de `medir_lecturas.py`, que no
   compiló. Ya está en el entorno de la máquina. Lo rehíce con la herramienta de edición.
3. **Dos Chrome a la vez dieron un `goto` vencido a los 15 s**, antes de la lectura. Repetido solo, midió. No se usa el
   resultado de la corrida en paralelo.
4. **Mi primera prueba de «REVISAR solo antes de la guarda» miraba el número de línea.** El REVISAR que va después del
   bucle de los modos está en una línea posterior a la guarda, pero sale solo si ningún modo llegó a ella. La prueba
   mira ahora lo que importa: la guarda termina la reserva por sus dos ramas, y ningún REVISAR está en ellas.
5. **En `mutaciones.py`, `SC` y `RS` nombran otra clase al final del archivo** (se reasignan más abajo). Una mutación
   nueva nombró una prueba que no existe. `mut_viejos.py` lo encontró, y ahora va con el nombre entero.
6. **Mi script que muestra las mutaciones sin ancla** buscó el texto viejo de todas en `AQUASHIELD.py`, también el de
   las que mutan otro archivo, y las listó como rotas. El chequeo de verdad (`ver_rotas.py`, `mut_viejos.py`) mira el
   archivo de cada una.
7. **Supuse, leyendo el código de Playwright, que `is_visible` tenía el plazo por omisión (30 s).** Medido, no vuelve
   ni a los 48 s. Lo trato como sin plazo.
8. **El borrador de este informe contaba mal las lecturas de antes:** decía 24 funciones (contaba también las que solo
   tienen lecturas con plazo), y en la reserva 20 `count()`, 10 `is_visible()` y 14 `page.evaluate`. Recontado con
   `contar_head.py` sobre la misma salida del inventario: 20 funciones, y 19, 9 y 12; el total, 57, era el mismo.
9. **Mi primera versión leía la reserva con 1,5 s, y eso cambiaba lo que el programa hacía.** La suite pasaba (671
   pruebas), y el censo de las áreas del cambio ya corría. Lo encontré al revisar el diff antes del commit, leyendo
   cada lugar donde una lectura que no contesta decide algo: los comentarios que se saltan, la sugerencia con «ramp»
   que cae a la primera, «Añadir dirección de entrega» que se pulsa. Ninguna prueba lo veía: las páginas falsas
   siempre contestan. Ahora hay dos plazos, y las tres elecciones no se deciden sin respuesta, con sus pruebas.
10. **Detuve el censo que corría sobre esa versión** a los 8 minutos, mientras preparaba sus copias, sin ningún par
    corrido: cerré su proceso y su hijo (`taskkill /T`), comprobé que no quedara ninguno (0) y borré su carpeta de
    trabajo (169 entradas, 0 fallas).
11. **Dos scripts de edición se detuvieron después de escribir una parte.** `aplicar_plazo.py` escribió sus
    ediciones ancladas y se detuvo en su cuenta del reemplazo global, que esperaba 15 y halló 16: la firma nueva de
    `_cma_leer` también traía ese texto. `aplicar_plazo2.py` hizo el resto, dejando fuera esa firma.
    `aplicar_plazo_pruebas.py` escribió tres archivos y se detuvo en el cuarto por dos líneas de más de 120
    caracteres. Lo corregí para que saltara lo ya escrito, y lo volví a correr. Otro, `aplicar_plazo_mut.py`, se
    detuvo antes de escribir, por una línea larga. Su primera versión suponía un formato que una mutación no tenía, y
    la reescribí antes de correrla.
12. **El decorador nuevo tapaba una prueba del encargo 54,** y solo lo vio el censo: la suite pasaba. Una detención
    que la reserva se tragara al abrir el formulario la volvía a encontrar el decorador al cortarse el paso siguiente,
    con el mismo resultado. Reforcé la prueba (sección 5).

## Premisas refutadas

1. **«El detector de antes todavía lee sin plazo las páginas de CMA-CGM que no son 403».** Es cierto, pero no era lo
   único: había 57 lecturas sin plazo en lo que corre desde el login y la reserva de CMA. Además, `count()` e
   `is_visible()` no tienen plazo en Playwright: no hay cómo dárselo, y van detrás de una pregunta con plazo.
2. **«Todo lo que lee tiene plazo»** (encargo 54, en `CLAUDE.md` y en `_evaluar_con_plazo`). El plazo de un localizador
   es el de encontrar el documento. Un JavaScript que ya empezó no se corta: uno de 4 s volvió a los 4,1 s. Vale con
   la página que no responde, que es el caso medido en el encargo 54.
3. **«Si mientras espera al operador la página pasa al bloqueo, también detiene»** (encargo 54, `CLAUDE.md`). En el
   panel, la espera del deslizador empieza cuando el operador pulsa «Ya lo resolví»: mientras la pausa sigue, el
   programa no mira la página. `CLAUDE.md` y los docstrings lo dicen ahora así.
4. **«Como las del encargo 54», con su mismo plazo, no servía para la reserva.** El mecanismo es el mismo (un
   localizador de `:root` con `timeout`), pero los 1,5 s del encargo 54 son para mirar si DataDome está, y ahí no
   poder leer cuenta como sin texto. En la reserva, no poder leer en 1,5 s cambiaba lo que el programa hacía con una
   página que solo estaba ocupada (sección 2). La reserva usa el plazo de Playwright, 30 s.
5. **«DataDome a mitad de una reserva no está cubierto».** El desafío al abrir Click & Book ya lo miraba
   `_ir_al_form`, desde antes del encargo 54. Lo que no se miraba era el desafío encima del formulario (el de un pedido
   de la página) y los caminos en que la reserva se corta o queda REVISAR.

## Residual

| # | qué queda | por qué | se reabre si |
|---|---|---|---|
| 1 | Entre la pregunta con plazo y `count()` o `is_visible()` queda un instante sin plazo | Playwright no da otra forma de leerlos | una corrida queda colgada en una de esas lecturas |
| 2 | Un JavaScript que ya empezó no se corta | el plazo del localizador es el de encontrar el documento (medido) | una lectura de CMA tarda más que su plazo |
| 3 | **Decides tú:** el plazo de las lecturas de la reserva y del login es el de Playwright, 30 s (`CMA_PLAZO_MS`; hipótesis) | es el que ya tenían las otras lecturas de la reserva; con 1,5 s, una página ocupada un momento cambiaba lo que hacía el programa (leído en el código) | prefieres otro valor, o se mide cuánto puede estar ocupada una página de CMA sin estar colgada |
| 4 | En una página colgada, cada lectura de la reserva espera hasta 30 s: un paso que lee varias veces puede tardar minutos en cortar sin escribir en `log.txt` (el lugar de entrega da hasta 14 vueltas) | es el costo de esperar, como antes, a la página que solo está ocupada | una corrida queda varios minutos sin escribir |
| 5 | Si el JavaScript de los comentarios falla (ahora también si no vuelve en 30 s), la reserva sigue sin ellos y puede quedar «lista para emitir»; con el candado abierto, se enviaría sin ellos | así era antes con cualquier falla de ese JavaScript: no es de este encargo | **lo decides tú:** que esa falla corte la reserva (propuesta) |
| 6 | Sin respuesta en 30 s, sin pulsar nada: el enlace «Cargar N siguientes resultados» cuenta como que no está (REVISAR, «ya no vi el enlace…»); el aviso tras «Validar ruta», como sin aviso (la ruta se da por aceptada, como ya pasaba sin respuesta del portal); y la información extra de la carga, como que no apareció (el paso se salta, como cuando no estaba) | no pulsan nada, pero el motivo o el camino dicen otra cosa que lo que pasó | una corrida lo muestra |
| 7 | **Decides tú:** la fila que DataDome dejó pasar a mitad de camino termina NO ENVIADA y no se vuelve a intentar | al dejar pasar, DataDome recarga la página (su documentación) y se pierde lo llenado; seguir sería llenar de nuevo | prefieres que la fila vuelva a empezar, o que siga |
| 8 | La recarga tras el desafío no está medida en CMA | hace falta el portal | DataDome aparece a mitad de una reserva: la evidencia `cma_f<fila>_datadome` lo mide |
| 9 | En el panel, mientras la pausa del deslizador sigue, el programa no mira la página: el bloqueo se ve recién cuando el operador pulsa «Ya lo resolví» | la pausa del panel espera el botón | **lo decides tú:** que la pausa termine sola cuando DataDome deja pasar o bloquea (propuesta) |
| 10 | Con «Detener» en la pausa del deslizador, la espera del deslizador igual vuelve a mirar la página, que el panel ya cerró: su primera espera falla, y lo que queda lo decide quien atrapa esa falla (leído en el código, sin medir). En la portada, REVISAR, como a las 14:26; a mitad de una reserva, DETENIDO, por el panel; al abrir el formulario, `_ir_al_form` se traga la falla, y la reserva sigue hasta el paso siguiente, que queda NO ENVIADA. Si el navegador se cierra entre dos lecturas, puede anotar antes «Verificación de CMA CGM superada ✓» | en la portada y al abrir el formulario era así antes; ahora la pausa dice que se cortó | se pide que «Detener» termine la espera sin volver a mirar la página (propuesta) |
| 11 | El panel Tkinter no dice cómo terminó su pausa | la decisión habla del panel web; el Tkinter es el respaldo | se pide también para el Tkinter |
| 12 | Las frases de DataDome en otro idioma no se reconocen: van al operador como «otra página» | lo medido está en español (encargo 54) | DataDome aparece en inglés |
| 13 | Si DataDome desafía cada fila, el operador pasa el deslizador una vez por fila, y cada una queda NO ENVIADA | es lo decidido: el deslizador lo pasa el operador, y no detiene | prefieres que el segundo deslizador seguido detenga CMA |
| 14 | Click & Book que no carga al abrir el formulario: su `goto` tiene el plazo de Playwright (30 s), y si vence la reserva se corta en el origen, como antes | no es DataDome; la decisión de no cargar es la de la portada | se pide para el formulario |
| 15 | El censo es el de las áreas del cambio, no el completo | el completo tarda más de 2 h | se pide el censo completo |
| 16 | Revisiones de ECC (code-reviewer, python-reviewer) | se proponen, no se lanzan | las pides |
| 17 | Con el candado abierto, si la página no contesta justo antes del botón final, CMA no lo pulsa y la fila queda NO ENVIADA con el motivo de siempre, «no estaba en la pantalla»: no dice que la página no contestó | `_resultado_envio` no distingue por qué no se pulsó; CMA nunca llegó a emitir | CMA emite y se ve ese motivo |

## Reglas de método (v16)

- **Aplicadas:** las 20 universales. En especial:
  - el contador al lado de cada cero: 0 ilegibles, 0 anclas rotas, 0 problemas;
  - el control positivo: el de `mut_viejos.py`, y el caso de la página libre en la medición de lecturas;
  - el negativo que muerde: cada prueba nueva, con su mutación;
  - re-medir contra HEAD: el inventario, sobre `git show HEAD:AQUASHIELD.py`;
  - el residual y las premisas refutadas, declarados;
  - un gate en cero prueba contención, no correctitud: la suite pasaba con la primera versión, y no veía lo que la
    revisión encontró (las páginas falsas siempre contestan); por eso las pruebas nuevas usan una que no contesta;
  - el cambio y su guardián en la misma operación;
  - cada reemplazo, una sola vez y escrito de forma atómica;
  - el EOL, preservado (LF).
- **Las del módulo** (`CLAUDE.md`): `test_candado` no cambia; ningún clic nuevo; nada atrapa el corte sin volver a
  levantarlo; casos sintéticos; la sonda de secretos antes de cada commit.
- **Choques:**
  - **ECC pide lanzar revisores y agentes;** las reglas permanentes dicen que se proponen. Mandan las permanentes: se
    proponen (residual 16).
  - **La regla del módulo «nada de lo que corre antes de la guarda atrapa `ObjetivoNoEncontrado`».** El decorador de
    CMA lo atrapa solo para mirar DataDome, y lo vuelve a levantar. No se traga el corte, que es lo que la regla
    cuida, y lo vigila su prueba (`test_el_decorador_no_se_traga_el_corte`). Lo declaro, y `CLAUDE.md` lo dice.
  - **Las frases de DataDome en las pruebas** son las del OCR del encargo 54, sin IP ni ID.

## Lo que dio en el repo

Dos commits en `main`, sin push (el push lo haces tú):

- `eba3d71` fix: el programa y las pruebas (`AQUASHIELD.py` y, en `tests/`, `mutaciones.py`, `soporte.py`,
  `test_ayudantes.py`, `test_clics.py`, `test_consola.py`, `test_datadome.py`, `test_envio.py`,
  `test_evidencia.py` y `test_web.py`);
- el commit siguiente, docs: este informe, y `CLAUDE.md` y `LEEME.md` al día.

Los dos llevan de autor y de committer el correo noreply del repo. La sonda de secretos dio 0 en el árbol y en el
staging, y cada archivo commiteado es igual al del árbol, sin CR.

En el entorno de la máquina (`~/.claude/CLAUDE.md`, «Entorno Windows de esta máquina») sumé una fila: qué lecturas de
Playwright no tienen plazo, medido aquí, y su plan B (la pregunta con plazo antes).
