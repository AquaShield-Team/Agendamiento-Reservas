# Encargo 57: los cortes de CMA-CGM, las pausas del panel, «Detener» en «Solo iniciar sesión» y la prueba de puertos

Base: `Agendamiento Reservas` @ `d97c163` · árbol limpio (al empezar, 2026-10-07).

## En resumen

- **El tamaño y tipo, el peso, el panel Reefer y «I Agree» de CMA-CGM cortan si fallan** (decisión de Marcelo).
  - Si el programa falla antes de terminar uno de esos pasos (un JavaScript que falla o no vuelve en 30 s, un clic o
    una espera que fallan), la fila queda NO ENVIADA con el motivo, la captura y el HTML del paso, como los
    comentarios del encargo 56.
  - Ninguna reserva llega al botón final sin la temperatura guardada: el panel Reefer corta si falla antes de pulsar
    su «Guardar».
  - Hasta ahora, cuando no encontraban lo que buscaban ya cortaban; las otras fallas las anotaban en `log.txt` («…
    err») y la reserva seguía sin el paso, hasta quedar «lista para emitir».
  - En `logs/` no pasó nunca: las 14 reservas de CMA-CGM que llegaron a la guarda hicieron los cuatro pasos, sin una
    falla anotada (primer FRENA SI: no se cumple). El cambio es preventivo.
  - Lo que falla después de terminar el paso sigue como antes: se anota y la reserva sigue.
- **Cada pausa del panel Tkinter espera su propia respuesta** (decisión de Marcelo). Hasta ahora, después del primer
  «Ya lo resolví» de una corrida, las pausas que seguían no esperaban: las de MSC, COSCO y MAERSK, y la del
  deslizador de CMA-CGM (medido sin abrir el panel, con su método compilado suelto).
- **La pausa del deslizador termina sola solo con dos lecturas seguidas sin DataDome** (decisión de Marcelo), con
  2 s entre una y otra. El bloqueo sigue deteniendo CMA-CGM con una sola lectura.
- **«Detener» en «Solo iniciar sesión» cierra el navegador y no sigue con los inicios de sesión que faltan** (decisión
  de Marcelo). Hasta ahora soltaba solo la pausa en curso: los inicios de sesión seguían, y el navegador quedaba
  abierto.
- **`test_puerto_que_se_suelta_mientras_pregunta` (encargo 52) ya no depende del reloj del equipo**, y vigila lo mismo.
  - Medí por qué fallaba: con la CPU ocupada, la segunda pregunta del lanzador volvía con el reset de la conexión, y
    el lanzador probaba el puerto un instante antes de que Windows lo soltara. Tomaba el siguiente en 5 de 30
    corridas del mismo caso, y en 0 de 20 con el equipo quieto.
  - Ahora el puerto se suelta dentro de esa segunda pregunta, con un `_panel_en` falso. Con la misma carga, la prueba
    nueva pasó 20 de 20, y la vieja 18 de 20.
  - El lanzador no cambió (segundo FRENA SI: no se cumple).
- **Se mantienen:** sin clics nuevos (la foto de clics de `test_clics` no cambió), `test_candado` sin cambios, y nada
  toca el disfraz del navegador ni la protección.
- **Lo decides tú** (el detalle, en el residual):
  1. Que el panel Reefer compruebe que el portal guardó la temperatura (hoy corta si el programa falla antes del
     «Guardar», pero si el portal no la guarda sin dar error, no lo ve). En los 9 HTML guardados tras «Guardar», el
     cajón del panel ya no está, la insignia «to complete» desapareció y la temperatura se ve; antes, en los 10 del
     panel abierto, la insignia estaba. Las 5 reservas del 21-09 no tienen HTML, así que no puedo afirmar que la
     comprobación no las habría cortado. Propongo que sí, con esa señal.
  2. La mercancía (el HS 030313) y la cantidad de CMA-CGM siguen anotando su falla y la reserva sigue: no estaban en la
     decisión. Propongo que corten como los otros.
  3. El lanzador, cuando la segunda pregunta vuelve y el puerto se suelta un instante después, toma el puerto
     siguiente (medido arriba). Propongo que vuelva a probar el puerto unos instantes, como ya hace con el panel ocioso.
- **Verificación:** 15 pruebas nuevas (713 en total) y 33 mutaciones nuevas (2.073); la suite pasa (713, OK,
  484 s), y los dos censos muerden: el chico, 85 de 85 pares, y el de las áreas del cambio, 543 de 543.

## 1. Lo que se midió antes de cambiar nada

### Las reservas de CMA-CGM que llegaron a la guarda (primer FRENA SI)

`sondeo_guarda.py`, sobre todo `log.txt` bajo `logs/`: 37 leídos. Una reserva de CMA es el bloque que empieza en su
línea «[CMA fila N]»; llegó a la guarda si trae «Me DETENGO en 'Envío de la reserva'» o «EMISIÓN: Pulsando 'Enviar el
booking'». Solo cuenta textos fijos del programa: no imprime carpetas, naves ni nada de la planilla o del portal.

| | reservas |
|---|---|
| bloques de CMA | 22 |
| llegaron a la guarda | 14 (5 del 21-09, con la emisión de entonces, y 9 del 25-09 al 02-10) |
| …con el tamaño y tipo elegido / el peso escrito / la temperatura guardada / «I Agree» marcada | 14 / 14 / 14 / 14 |
| …con «tamaño y tipo err», «peso err», «ajustes reefer err», «check agree err» o «info extra:» | **0** |
| …con un reintento de la información extra | 0 (los 5 reintentos de `logs/` son de reservas que no llegaron) |
| líneas de esos pasos fuera de un bloque (descartadas) | 0 |

Las 14 siguen la misma secuencia: información extra (tamaño, peso, mercancía, soluciones), panel Reefer (temperatura y
«guardados»), comentarios, «I Agree» y la guarda. **Ninguna habría quedado NO ENVIADA con los cortes nuevos**: los
cortes saltan solo donde antes se anotaba una de esas fallas, y no hay ninguna.

Las 8 que no llegaron a la guarda (`sondeo_guarda.py`, sus bloques):

- **5, del 21-09 a las 14:58, hicieron la información extra dos veces:** la mercancía y «Mostrar soluciones
  disponibles» fallaron, y el programa la reintentó. En los dos intentos, el tamaño y el peso salieron bien: con el
  cambio, tampoco habrían cortado ahí. No llegaron al panel Reefer.
- **1, del 24-09, terminó en el panel Reefer** sin anotar la temperatura ni una falla de ese paso («ajustes reefer
  err»): no es un caso de los cortes nuevos.
- **2, del 26-09, no llegaron a ninguno de esos pasos.**

### Lo que muestran los HTML del panel Reefer

`sondeo_reefer_html.py` y `clases_panel.py`, sobre los HTML de `logs/` (solo cuentan marcas fijas del portal):

| HTML | archivos | cajón `reefer-drawer` | insignia «to complete» | «-20 °C» |
|---|---|---|---|---|
| el panel abierto (`cma_f*_reefer_panel`) | 10 | 9 | 10 | 0 |
| tras «Guardar» (`cma_f*_reefer_guardado`) | 9 | 0 | 0 | 9 |
| la guarda (`cma_f*_guarda`) | 9 | 0 | 0 | 9 |

Es la señal con que se podría comprobar que el portal guardó la temperatura (Lo decides tú, 1). No la usé: no estaba
en la decisión, y las 5 reservas del 21-09, sin HTML, no permiten afirmar que no habría cortado ninguna.

### La prueba de puertos

`medir_puerto.py` corre el mismo caso de la prueba (un ocupante que acepta sin contestar y suelta el puerto a los 2 s,
con `threading.Timer`) sobre la copia del programa, y anota cada pregunta del lanzador.

| | corridas | tomó el puerto base | tomó el siguiente |
|---|---|---|---|
| con el equipo quieto | 20 | 20 | 0 |
| con la CPU ocupada (16 procesos girando, en 12 núcleos: `carga.py`) | 30 | 25 | 5 |

En las 5 que fallaron, el camino es el mismo: la primera pregunta vence al segundo, el puerto sigue tomado, la segunda
pregunta vuelve a los 2 s con `ConnectionResetError` (el ocupante cerró), y el lanzador prueba el puerto enseguida y
todavía no se puede enlazar: lo da por de otro programa. En una corrida que pasó, el mismo puerto se pudo enlazar
0,22 s después. Lo que vigila la prueba (que el lanzador vuelva a probar el puerto después de la segunda pregunta) no
depende de ese instante.

### Antes y después, sin red

`contra_head.py`, con las páginas falsas de `tests/test_clics.py` y `tests/test_datadome.py`, la pausa de verdad del
panel web y el método `_pausa` del panel Tkinter compilado suelto, sobre las fuentes de `d97c163` y sobre las de hoy.

| caso | antes (`d97c163`) | ahora |
|---|---|---|
| el JavaScript del tamaño y tipo falla, y el resto de la página está | «tamaño y tipo err», y la fila llega a la guarda: OK-EJEMPLO | NO ENVIADA, con el motivo, la captura y el HTML del paso |
| el del peso falla | «peso err», OK-EJEMPLO | NO ENVIADA |
| el de la temperatura del Reefer falla | «ajustes reefer err», OK-EJEMPLO | NO ENVIADA |
| el que baja hasta «I Agree» falla | «check agree err», OK-EJEMPLO | NO ENVIADA |
| DataDome deja de verse una lectura (a los 4 s) y vuelve, y después deja pasar | la pausa termina a los 4 s, y la lectura siguiente ve a DataDome otra vez | termina a los 10 s, con la página sin DataDome |
| dos pausas del Tkinter, cada «Ya lo resolví» en la segunda espera de su pausa | la segunda vuelve en su primera espera, sin su «Ya lo resolví» | cada una espera el suyo |
| «Solo iniciar sesión» con ONE, MSC y COSCO, «Detener» en la pausa de ONE | entra también a MSC y COSCO, el navegador sigue abierto, el panel dice «Sesiones abiertas.» (8 s) | solo ONE, el navegador cerrado cuando la pausa vuelve, «Detenido.» (2 s) |

## 2. Lo que cambió

### Los cuatro pasos de CMA-CGM

- **Un solo corte para todos:** `_cma_fallo(paso, buscaba, qué hacía, la falla)` arma el `ObjetivoNoEncontrado` con lo
  que el paso buscaba y la falla. Lo usan los comentarios (el texto de su motivo no cambió) y los cuatro pasos nuevos.
  Lo que busca cada uno va una sola vez: `CMA_TAMANO_Y_TIPO`, `CMA_CAMPO_PESO`, `CMA_REEFER_GUARDADO` y
  `CMA_CASILLA_I_AGREE` (los dos primeros y el último ya eran el texto de su corte por objetivo no encontrado).
- **Cada paso lleva la cuenta de si ya terminó,** como los comentarios: el tamaño y tipo, si eligió la opción; el panel
  Reefer, si pulsó el «Guardar» del panel; «I Agree», si la marcó. Si algo falla antes, corta; si falla después, lo
  anota y sigue, como antes. En el peso no queda nada después de escribirlo: toda falla corta.
- **«I Agree» va en su propio paso,** `_cma_i_agree_en_el_envio` (el Escape, bajar al final y marcarla), para poder
  probarlo solo. Hasta ahora era un bloque dentro de `reservar_cma`; el texto de la pantalla y lo que hace no
  cambiaron.
- El corte lo convierte en NO ENVIADA `_sin_clic_a_ciegas`, que ya envolvía a `reservar_cma`, con la captura
  `cma_f<fila>_sin_objetivo` y su HTML. El motivo, en la planilla, por ejemplo: «Ajustes Reefer de CMA: no encontré el
  panel Reefer con su temperatura guardada (por el botón «Modifique el reefer», la etiqueta «Temperature» y su
  «Guardar»), porque el programa falló al abrir el panel, escribir la temperatura o guardarla (RuntimeError: …), así
  que no pulsé nada. La reserva no se envió; revisa ese paso en el portal.»
- La información extra se reintenta una vez si «Mostrar soluciones disponibles» falla. En el reintento, una falla del
  tamaño o del peso ahora también corta. En `logs/` hubo 5, el 21-09, y en los 5 el tamaño y el peso salieron bien.

### La pausa del deslizador

- `_cma_vigia(page)` es lo que la pausa mira ahora (el `hasta` de `_pausa_del_panel`): lo mismo que
  `_cma_como_quedo`, pero «DataDome dejó pasar la página» lo dice recién en la segunda lectura seguida que lo ve
  (`CMA_LECTURAS_PARA_SEGUIR`). Una lectura con DataDome, o con la página cerrada, vuelve a contar desde cero. El
  bloqueo, con una.
- La espera de después de la pausa (con «Ya lo resolví» o al vencer) sigue con una lectura, como desde el encargo 54:
  la decisión es para la pausa que termina sola.

### La pausa del panel Tkinter

- `_pausa` apaga `ev_pausa` antes de pedir la respuesta. Va antes de avisar por la cola, que es lo que enciende «Ya lo
  resolví»: un clic del operador no puede caer entre los dos y perderse. Un clic que llegó cuando no había pausa (el
  botón sigue encendido 100 ms después de una pausa que terminó sola) ya no suelta la pausa siguiente.

### «Detener» en «Solo iniciar sesión»

- `ejecutar_login` recibe `se_detuvo` (si se pulsó «Detener») y `al_abrir` (recibe el navegador apenas se abre). Antes
  de cada inicio de sesión mira `se_detuvo`; con «Detener», no sigue, lo dice en `log.txt` («⛔ Detenido por el
  operador: cierro el navegador y no sigo con MSC, COSCO.»), no espera para cerrar y cierra el navegador.
- Si el inicio de sesión en curso se cae porque «Detener» le cerró el navegador, lo anota como cortado por «Detener», y
  no como un error del portal ni con una captura de la página cerrada.
- `_web_worker_login` deja el navegador en `_WEB["ctx"]`, como las reservas, para que `/api/detener` lo cierre, y al
  terminar el panel dice «Detenido.».
- La consola y el panel Tkinter no tienen «Detener»: no le pasan nada, y siguen como antes.

### La prueba de puertos

- El ocupante escucha sin contestar, y un `_panel_en` falso para ese puerto dice que nadie contestó; en la segunda
  pregunta (la de `PANEL_ESPERA_LARGA`), primero suelta el puerto. `_puerto_libre` y `_enlazar` son los de verdad. La
  prueba exige además que el lanzador haya preguntado dos veces, con 1 s y con `PANEL_ESPERA_LARGA`.
- Lo que vigilaba (la mutación `e52-lanzador-no-vuelve-a-probar`) lo sigue vigilando; y una mutación nueva,
  `e57-lanzador-no-vuelve-a-preguntar`, la segunda pregunta.

## 3. Pruebas, mutaciones, suite y censos

### Las pruebas nuevas (15)

| dónde | prueba | qué vigila |
|---|---|---|
| `test_clics.TestCma` | `test_tamano_y_tipo_que_falla_corta` | el JavaScript del tamaño falla (o no vuelve), o falla la espera tras abrir el desplegable: corta, con la falla en el motivo |
| | `test_lo_que_falla_despues_de_elegir_el_tamano_sigue_como_antes` | elegida la opción, la espera que falla se anota y el paso sigue |
| | `test_peso_que_falla_corta` | el JavaScript del peso falla o no vuelve: corta |
| | `test_reefer_que_falla_antes_de_guardar_corta` | falla el JavaScript de la temperatura, o el clic en el «Guardar» del panel: corta, sin «guardados» |
| | `test_lo_que_falla_despues_de_guardar_el_reefer_sigue_como_antes` | después de «Guardar», la falla se anota y devuelve False, como antes |
| | `test_i_agree_que_falla_corta` | falla antes de marcarla: corta; sin la casilla, corta como antes |
| | `test_i_agree_como_antes` | la marca, y lo que falla después se anota y sigue |
| | `test_los_cuatro_que_fallan_dejan_la_fila_no_enviada_con_su_evidencia` | con los decoradores de `reservar_cma`: NO ENVIADA, el motivo literal, la captura y el HTML, y nada sigue |
| | `test_lo_que_buscan` | el texto de lo que busca cada paso, que llega a la planilla |
| | `test_reservar_cma_corre_los_pasos_que_cortan_antes_de_la_guarda` | `reservar_cma` corre los cuatro pasos (y los comentarios) antes de la guarda |
| `test_datadome.TestPausaQueTerminaSola` | `test_una_lectura_sin_datadome_no_basta` | una lectura sin DataDome y otra con él: la pausa no termina hasta dos seguidas |
| | `test_el_vigia_cuenta_las_lecturas_seguidas` | lo que dice `_cma_vigia` en cada lectura, y el bloqueo con una |
| `test_web.TestPausaDelPanelTkinter` | `test_cada_pausa_espera_su_respuesta` | dos pausas seguidas, cada una con su «Ya lo resolví» |
| `test_web.TestPanelCorridas` | `test_detener_en_solo_iniciar_sesion` | el panel web de verdad: «Detener» en la pausa de ONE, MSC y COSCO no se intentan, el navegador en `_WEB["ctx"]`, «Detenido.» |
| `test_consola.TestEjecutarLogin` | `test_solo_login_con_detener_no_sigue` | `ejecutar_login` con `se_detuvo`: no sigue, no espera, cierra, y la caída por «Detener» no es un error |

**Fotos que cambiaron a propósito:** `test_termina_sola_cuando_datadome_deja_pasar` (la pausa termina a los 8 s y no a
los 6) y `test_a_mitad_de_la_reserva` (a los 6 y no a los 4), por las dos lecturas; y
`test_puerto_que_se_suelta_mientras_pregunta`, sin reloj (sección 2). Los falsos que cambiaron: `PaginaCmaQueFalla`
(falla con el JavaScript que se le diga), `EventoTkinter` (varios «Ya lo resolví», y `clear` como un
`threading.Event`), y `corta` (con el nombre de su carpeta, para que el `log.txt` de una prueba no traiga líneas de
otra). Nuevos: `PaginaCmaQueNoPulsa` y `espera_que_falla_tras`.

### Las mutaciones

- **33 nuevas** (`e57-*`), una o más por prueba nueva: cada corte que no corta o que corta también después, cada paso
  dado por terminado antes de tiempo, `reservar_cma` sin el paso de «I Agree», el motivo sin la falla o con otro
  texto, lo que busca cada paso con otro texto, el vigía con una lectura, sin volver a cero o con el bloqueo en dos,
  la pausa del Tkinter sin apagar su evento, «Detener» sin mirar, sin pasar el navegador, sin decirlo o con la lista
  mal, y el lanzador que no vuelve a preguntar.
- **8 reancladas**, porque el cambio movió su texto: `login-cierra-antes`, `cma-i-agree-no-corta`,
  `teclado-cma-tamano`, `e53-navegador-login-sin-el-ayudante`, `e56-comentarios-falla-sigue`,
  `e56-comentarios-motivo-sin-la-falla` (ahora deja el motivo sin la falla, en vez de romper la llamada),
  `e56-comentarios-otro-paso` y `e56-deslizador-sin-vigia`.
- `mut_viejos.py`: 2.073 mutaciones, 713 pruebas, 0 problemas (cada texto viejo una sola vez, las 44 nuevas o
  reancladas compilan, toda prueba con su mutación).

### Los censos

- **Chico** (`censo_mini.py`): las 33 nuevas, las 8 reancladas y las que nombran una prueba que este encargo cambió:
  50 mutaciones, 85 pares, 32 pruebas. El control pasa; **85 de 85 muerden**; 0 cambios en las 4.544 entradas de los
  originales.
- **De las áreas del cambio** (`alcance_censo.py`, `lanzar_censo_e57.py`): las nuevas (33), las reancladas (8), las
  que caen en las 14 funciones que cambiaron (97) y las que nombran una prueba cuyo camino cambió (365): 376
  mutaciones, 543 pares, 180 pruebas. El control pasa; **543 de 543 muerden**; 0 cambios en los originales. Corrió
  aparte, de las 23:39 a las 00:04.

### La suite

`tests/correr.py` (con `correr_sin_tope.py`: el plazo de la corrida entera en 7.200 s), sobre el árbol que se commitea:
**713 pruebas, OK, en 484 s**, con 0 cambios en las 4.544 entradas fotografiadas de los originales.

### La prueba de puertos, con carga

`repetir_prueba.py`, 20 veces cada una, con `carga.py` (16 procesos girando) en paralelo: **la nueva pasó 20 de 20; la
de `d97c163`, 18 de 20.**

## Re-medir

Todo en `e57/` (carpeta del encargo), con `source entorno_e57.sh` antes.

| qué | cómo |
|---|---|
| las reservas de CMA que llegaron a la guarda | `python sondeo_guarda.py` |
| los HTML del panel Reefer | `python sondeo_reefer_html.py` y `python clases_panel.py` |
| la prueba de puertos, el caso replicado | `python medir_puerto.py 20`; con carga, `python carga.py 16 200` en paralelo, y `python medir_puerto.py 30` |
| la prueba de puertos, nueva y vieja, con carga | `python repetir_prueba.py "<repo>/tests" test_web.TestArranqueDelPanel.test_puerto_que_se_suelta_mientras_pregunta 20`, y con `tests_d97c163` (la vieja), con `AQUASHIELD_FUENTES` en el repo |
| antes y después | `python contra_head.py fuentes_head` y `python contra_head.py fuentes_arbol` (las fuentes: `git show d97c163:AQUASHIELD.py`, y la copia del árbol) |
| las anclas de las mutaciones | `python mut_viejos.py e57-` |
| el censo chico | `python censo_mini.py` |
| el alcance del censo | `python alcance_censo.py` |
| el censo | `python lanzar_censo_e57.py` (aparte, sin ventana; escribe `censo_e57.txt`) |
| la suite | `python tests/correr.py` en el repo |
| que nada toca el disfraz ni el candado | `git diff d97c163 -- AQUASHIELD.py` sin `STEALTH_JS`, `_args_chrome`, `_lanzar_navegador` ni `ignore_default_args`; `git diff d97c163 -- tests/test_candado.py` vacío |

## NO retroceder

- **Los cuatro pasos de CMA-CGM no vuelven a tragarse su falla.** Con el candado abierto, la reserva llegaría al botón
  final sin la temperatura, el tamaño, el peso o «I Agree».
- **El corte lo arma una sola función, `_cma_fallo`,** y lo que busca cada paso va en una sola constante.
- **«I Agree» sigue en su propio paso:** dentro de `reservar_cma` no se podía probar solo.
- **La pausa del deslizador termina sola con dos lecturas seguidas,** y el bloqueo con una.
- **Cada pausa del Tkinter apaga su evento antes de avisar por la cola,** no después.
- **En «Solo iniciar sesión», el navegador va a `_WEB["ctx"]`:** sin eso, «Detener» no tiene qué cerrar.
- **La prueba de puertos no vuelve a esperar con el reloj** a que otro hilo suelte el puerto.

## Defectos de instrumento

1. **Imprimí en la salida de una herramienta el comienzo del nombre de 5 carpetas de `logs/`, que en las del login es
   el nombre del operador.** Fue un `ls` de `logs/` con un `sed` que debía dejar solo el tipo y la fecha, y no lo
   hizo. Quedó solo en la salida de esa herramienta en esta sesión: no está en ningún archivo, ni en este informe, ni
   en un commit. Después de eso, todo lo de `logs/` lo leí con Python, imprimiendo solo cuentas y fechas.
2. **La primera versión de `sondeo_reefer_html.py` buscaba el cajón del panel por la clase de Element UI
   (`el-drawer__wrapper`), que esa página no trae** (es Element Plus). Su control positivo abortó, como debía, y no
   usé lo que había contado. `clases_panel.py` contó las clases que sí trae, y la sonda corregida busca `reefer-drawer`:
   pasa su control y da la tabla de la sección 1.
3. **El primer «antes y después» del tamaño y tipo no probaba nada:** con la opción a la vista, el programa la elegía
   por el localizador y nunca corría el JavaScript que fallaba, así que las dos versiones daban OK-EJEMPLO. Lo vi en
   la salida (sin «tamaño y tipo err» en la de antes) y quité la opción de la vista en ese caso.
4. **Un `cd tests` en primer plano movió la sesión a `tests/`,** como dice el entorno de la máquina (ya me pasó en el
   encargo 56). Desde ahí, los comandos van con ruta absoluta.
5. **Dos reemplazos de `CLAUDE.md` y `LEEME.md` dejaron líneas de 157 y 156 caracteres:** su texto viejo terminaba a
   mitad de una línea, y el control de largo de mi script miraba solo el texto nuevo. Lo vio el control sobre el
   diff entero, antes del censo, y partí las dos líneas.
6. **Un `python` por heredoc con barras invertidas** (el alcance del censo) dio avisos de escape: la herramienta junta
   los pares de barras. El archivo no llegó a escribirse (su aserción final falló antes, por ser demasiado estricta), y
   lo escribí entero con Write.
7. **Escribí en el borrador de este informe, sin medirlo, que las 8 reservas que no llegaron a la guarda se cortaron
   antes de esos pasos y que el reintento de la información extra no había ocurrido nunca.** Lo medí antes del
   commit: 5 la reintentaron, con el tamaño y el peso bien en los dos intentos (sección 1). La conclusión del primer
   FRENA SI no cambia.

## Premisas refutadas

1. **«Reefer, «I Agree», tamaño y tipo, y peso: si fallan, la fila queda NO ENVIADA»** daba a entender que hoy siempre
   seguían. No: cuando no encontraban lo que buscaban ya cortaban, desde `83067a1` (`CICLO-clics-a-ciegas.md`),
   porque `ObjetivoNoEncontrado` no lo atrapa ningún `except Exception`. Lo que se tragaban eran las otras fallas: un
   JavaScript que falla o no vuelve, un clic que no sale, una espera que falla. El hallazgo del encargo 56 decía «se
   tragan su falla» sin esa distinción.
2. **La prueba de puertos «depende del reloj»:** sí, pero no de los 2 s del `threading.Timer` en sí. Lo que falla es
   el instante entre el reset que recibe la segunda pregunta y el momento en que Windows suelta el puerto, que con la
   CPU ocupada llega tarde (sección 1). Ese instante también lo tiene el lanzador de verdad (Lo decides tú, 3).

## Residual

| # | qué queda | por qué | se reabre si |
|---|---|---|---|
| 1 | **Decides tú:** el panel Reefer no comprueba que el portal guardó la temperatura; si el portal no la guarda sin dar error, la reserva sigue. Señal medida en `logs/`: tras «Guardar», sin el cajón `reefer-drawer`, sin «to complete» y con la temperatura (9 de 9) | no estaba en la decisión, y las 5 reservas del 21-09 no tienen HTML: no puedo afirmar que la comprobación no las habría cortado | lo pides (propuesta: que corte si, tras «Guardar», el cajón o «to complete» siguen) |
| 2 | **Decides tú:** la mercancía (HS 030313) y la cantidad de CMA-CGM siguen anotando su falla («mercancía err») y la reserva sigue. En `logs/`, 0 fallas en las 14 que llegaron a la guarda | no estaban en la decisión | lo pides (propuesta: que corten como los otros) |
| 3 | **Decides tú:** el lanzador, si la segunda pregunta vuelve y el puerto se suelta un instante después, toma el siguiente (5 de 30 con la CPU ocupada) | el encargo pidió estabilizar la prueba sin cambiar el lanzador | lo pides (propuesta: volver a probar el `bind` unos instantes, como `_enlazar` con el panel ocioso) |
| 4 | Si la información extra no se ve (o leerla falla), el tamaño y el peso no corren y la reserva sigue, como antes. En `logs/`, las 14 que llegaron a la guarda la vieron | no es una falla del paso: el programa decide que el portal no la pide | una reserva llega a la guarda sin «Completando información extra» |
| 5 | En el reintento de la información extra, una falla del tamaño o del peso ahora corta, aunque el primer intento los hubiera dejado. En `logs/`, 5 reintentos (21-09), con el tamaño y el peso bien en los dos intentos | consecuencia directa de la decisión | pasa en una corrida |
| 6 | El motivo de estos cortes dice «así que no pulsé nada», aunque el paso ya hubiera pulsado algo (abrir el panel Reefer, por ejemplo) | es el texto fijo de `_sin_clic_a_ciegas` (residual 8 del encargo 56) | lo pides con un motivo propio |
| 7 | Mientras dura la pausa del deslizador, el programa lee la página cada 2 s; con dos lecturas, la pausa termina 2 s más tarde que en el encargo 56. Si DataDome reacciona a esas lecturas, o si una lectura sola caía de verdad en un instante de paso, no está medido | hace falta el portal | una pausa termina sola y el paso siguiente encuentra a DataDome |
| 8 | En «Solo iniciar sesión», si «Detener» llega después del último inicio de sesión, durante los 6 s en que el navegador queda abierto, lo cierra `/api/detener`, pero la espera de 6 s sigue y `log.txt` no lo dice (leído en el código) | ventana corta; el navegador se cierra igual | confunde al operador |
| 9 | La consola (`python AQUASHIELD.py <operador> <naviera>`) y el panel Tkinter no tienen «Detener»: siguen como antes | no se pidió | lo pides |
| 10 | Que `/api/detener` cierre de verdad el navegador desde otro hilo sigue sin medir con Chrome (residual 6 del encargo 56); aquí se midió con el navegador falso de las pruebas | hace falta abrir Chrome | una corrida con «Detener» deja el navegador abierto |
| 11 | Del encargo 56 siguen abiertos sus residuales 4, 6, 7, 8, 9, 10 y 11. Este encargo cerró sus 1, 2, 3, 5 y 15 (lo que decidiste) | — | — |
| 12 | Más revisiones de ECC (python-reviewer, security-reviewer, una revisión del cambio por un subagente) | se proponen, no se lanzan; este encargo no pidió revisión | las pides |
| 13 | El censo es el de las áreas del cambio, no el completo (2.073 mutaciones) | el completo pasa de 2 h | lo pides |

## Reglas de método (v16)

- **Aplicadas:** las 20 universales. En especial:
  - el contador al lado de cada cero: en `logs/`, 37 de 37 leídos, 22 bloques de CMA, 14 en la guarda, 0 fallas y 0
    descartados; 0 problemas de anclas en 2.073 mutaciones; 0 cambios en las entradas fotografiadas de los originales;
  - el control positivo que aborta: cada sonda de `logs/`, `medir_puerto.py`, `repetir_prueba.py` y `mut_viejos.py`.
    El de `sondeo_reefer_html.py` abortó de verdad (defecto 2), y no usé su número;
  - el negativo que muerde: cada prueba nueva con su mutación, y los dos censos; y la prueba de puertos vieja, medida
    con la misma carga que la nueva (18 de 20 contra 20 de 20);
  - re-medir contra HEAD: el antes y después, con las fuentes de `d97c163`, y el sondeo de `logs/` del primer FRENA SI;
  - un gate en cero prueba contención, no correctitud: además de la suite, las pruebas que corren los decoradores de
    `reservar_cma`, la pausa de verdad del panel web y el panel web en «Solo iniciar sesión»;
  - fuente única: `_cma_fallo` para los cinco cortes, una constante por lo que busca cada paso, y `_cma_vigia` sobre
    `_cma_como_quedo`;
  - el cambio y su guardián en la misma operación; cada reemplazo, una sola vez y validado antes de escribir; el EOL,
    LF (0 CR);
  - frenar en lo que es de Marcelo: lo que encontré fuera del encargo va al residual como propuesta.
- **Las del módulo** (`CLAUDE.md`): `test_candado` no cambia; ningún clic nuevo; nada se traga el corte; casos
  sintéticos; nunca el puerto 8765 en una prueba; la sonda de secretos antes de cada commit; el correo noreply de autor
  y de committer.
- **Choques:**
  - **ECC pide lanzar revisores y agentes solos;** las reglas permanentes dicen que se proponen. Este encargo no pidió
    revisión: no lancé ninguna, y quedan propuestas (residual 12).
  - **«Nada fuera de la carpeta del encargo»** y **«las sesiones pueden agregar filas en Entorno Windows»:** sumé una
    fila a `~/.claude/CLAUDE.md`, la del puerto que se suelta tarde, medida en este ciclo; nada más fuera de la carpeta
    del encargo.
- **Pieza 8 (el entregable renderizado y mirado):** opcional; este informe es Markdown y no lo rendericé.

## Lo que dio en el repo

Dos commits en `main`, sin push (el push lo haces tú):

- `0c45653` fix: el programa y las pruebas (`AQUASHIELD.py` y, en `tests/`, `mutaciones.py`, `test_clics.py`,
  `test_consola.py`, `test_datadome.py` y `test_web.py`);
- el commit siguiente, docs: `CLAUDE.md`, `LEEME.md` y este informe.

Los dos llevan de autor y de committer el correo noreply del repo, y la sonda de secretos dio 0 antes de cada uno.

El entorno de la máquina (`~/.claude/CLAUDE.md`, «Entorno Windows») lleva una fila nueva, medida aquí: el puerto que
Windows suelta un instante después del reset, con la CPU ocupada (sección 1).
