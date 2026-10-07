# Encargo 56: los comentarios de CMA-CGM que fallan cortan, la pausa del deslizador termina sola, y una revisión

Base: `Agendamiento Reservas` @ `a6159b3` · árbol limpio (al empezar, 2026-10-06).

## En resumen

- **Si los comentarios de CMA-CGM no se escriben, la fila no sigue** (decisión de Marcelo).
  - Si algo falla antes de escribirlos, la fila queda NO ENVIADA, con el motivo, la captura y el HTML del paso. Eso
    incluye el JavaScript que los busca y escribe (también si no vuelve en 30 s) y el campo que vio el localizador,
    que era el otro camino por el que la reserva seguía sin ellos.
  - Hasta ahora, el programa lo anotaba en `log.txt` («comentarios err») y la reserva seguía sin ellos, hasta quedar
    «lista para emitir»; con el candado abierto, se habría enviado así.
  - En `logs/` no pasó nunca: los 14 comentarios los escribió el JavaScript. El cambio es preventivo.
  - Lo que falla después de escribirlos sigue como antes: se anota y la reserva sigue.
- **La pausa del deslizador termina sola** (decisión de Marcelo).
  - Mientras espera al operador, el panel mira la página cada 2 s, con lo mismo que ya miraba la espera de después.
    En `logs/`, las 8 esperas que eso dio por superadas terminaron con la sesión iniciada.
  - Si DataDome deja pasar la página, la corrida sigue sin que el operador pulse «Ya lo resolví». Si la bloquea,
    CMA-CGM se detiene, como hoy.
  - Hasta ahora, mientras el operador no pulsaba el botón, el programa no miraba la página.
  - Vale para el panel web y para el Tkinter. Sin panel, en la consola, la espera ya miraba la página.
- **«Detener» corta la espera** (decisión de Marcelo), sin volver a mirar la página.
  - El login de CMA queda sin sesión, y la fila en curso, DETENIDO, «Cancelado por el operador», como en las otras
    navieras.
  - Hasta ahora, la espera volvía a mirar la página que el panel cerraba. Su espera fallaba con la página cerrada o,
    si se cerraba entre la espera y la lectura, anotaba «Verificación de CMA CGM superada ✓» sin serlo (medido sin
    red, con páginas falsas, contra `a6159b3`).
- **Se mantienen** el plazo de 30 s y NO ENVIADA sin reintento cuando DataDome deja pasar a mitad de una reserva.
- **Ninguno de los FRENA SI se cumplió.**
  - Reconocer que DataDome dejó pasar la página no exigió abrir el portal: es lo que ya hacía la espera de después.
  - Nada toca el disfraz del navegador: ni `STEALTH_JS`, ni `_args_chrome`, ni el lanzador.
  - Sin clics nuevos (la foto de clics de `test_clics` no cambió), y `test_candado` no cambió.
- **La revisión** (decisión de Marcelo): un subagente revisó, en un clon dentro de la carpeta del encargo, el cambio de
  este ciclo y el del encargo 55. No encontró nada grave. Encontró una inconsistencia que
  decides tú (abajo), y lo documental que encontró está corregido; lo demás va al residual (sección 3).
- **Lo decides tú** (el detalle, en el residual):
  1. Que el Reefer (la temperatura y su «Guardar»), «I Agree», el tamaño y tipo, y el peso también corten si
     fallan, como ahora los comentarios. Hoy se anotan y la fila sigue: con el candado abierto, la reserva
     llegaría al botón final sin, por ejemplo, la temperatura guardada. En `logs/` no pasó nunca. Propongo que
     sí.
  2. Arreglar el panel Tkinter: después del primer «Ya lo resolví» de una corrida, sus pausas siguientes no
     esperan (ya pasaba). Propongo que sí: es una línea, pero cambia también las pausas de COSCO y MSC en ese
     panel.
  3. Que la pausa del deslizador pida dos lecturas seguidas sin DataDome antes de terminar sola, por si una
     sola cae en un instante de paso (no medido).
  4. Que «Detener» detenga también «Solo iniciar sesión»: hoy corta solo la espera y las pausas.
- **Verificación:** 22 pruebas nuevas (698 en total), la suite pasa, y los dos censos muerden: el chico, 62 de 62
  pares, y el de las áreas del cambio, 449 de 449. En una de las tres corridas de la suite falló una prueba de
  puertos del encargo 52, que depende del tiempo y ya fallaba a ratos antes de este cambio (sección 4).

## 1. Lo que se midió antes de cambiar nada

### Los comentarios de CMA, en `logs/`

`sondeo_logs.py`, sobre todo `log.txt` bajo `logs/`: 37 archivos, 37 leídos, 0 ilegibles.

| después de «CMA · Ingresando comentarios adicionales...» | pasos |
|---|---|
| «comentario: …» (los escribió el JavaScript) | 14 |
| «comentario (vía locator): …» | 0 |
| «comentarios err: …» (falló, y la reserva siguió sin ellos) | 0 |
| otro paso enseguida, o sin línea de resultado | 0 |
| **total** | **14** |

El fallo que la decisión cubre no se vio nunca. El cambio es preventivo: el plazo de 30 s del encargo 55 lo hizo
posible también cuando la página no contesta.

### La espera del deslizador, en `logs/`

Del mismo sondeo y de `sondeo_sin_desenlace.py`, `sondeo_error.py` y `sondeo_duracion.py` (solo cuentan: no imprimen
nombres de carpeta ni líneas).

| pedidos de deslizar la flecha | 11 |
|---|---|
| superados («Verificación de CMA CGM superada ✓») | 8 |
| agotados (180 s) | 0 |
| detenidos por el operador | 0 |
| sin desenlace en `log.txt` | 3 |

- **Las 8 superadas** terminaron con la sesión iniciada: el reconocimiento que ahora usa también la pausa acertó las
  8 veces que se usó. Ninguna pasó por un aviso de espera: las 8 se vieron superadas antes de los 5 s de la espera de
  después, porque el operador pulsaba «Ya lo resolví» cuando ya había pasado. Del pedido a «superada», 7, 8, 10, 10,
  20, 22, 76 y 92 s (mediana 20 s): eso tardó cada pausa, más un segundo. Las 8 fueron con la pausa del panel (sin
  ella, la espera habría anotado sus avisos): 5 en «Solo iniciar sesión» y 3 al armar reservas.
- **Las 3 sin desenlace** son todas del 06-10, en «Solo iniciar sesión»:
  - 09:56:25: el log termina a las 09:57:25, con 10 avisos de espera;
  - 09:57:52: 2 avisos, y a las 09:58:10, «ERROR inesperado» en `Page.wait_for_timeout`, con la página cerrada;
  - 14:26:41: ningún aviso, y a las 14:32:38 el mismo error, con la página cerrada.

  En «Solo iniciar sesión», «Detener» no cierra el navegador (leído en el código): esas dos páginas no las cerró
  «Detener» (premisas refutadas).
- **Pausas del encargo 55 en `log.txt`:** 0. No hubo corridas desde entonces.

### Antes y después, sin red

`contra_head.py`, con las páginas falsas de `tests/test_datadome.py` y la pausa de verdad del panel web, sobre las
fuentes de `a6159b3` y sobre las de hoy.

| caso | antes (`a6159b3`) | ahora |
|---|---|---|
| el JavaScript de los comentarios falla | `_cma_comentarios` devuelve False, y la fila llega a la guarda: OK-EJEMPLO, sin captura ni HTML del paso | corta, y la fila queda NO ENVIADA con `cma_f9_sin_objetivo.png`, su HTML y el motivo |
| DataDome deja pasar a los 6 s; el operador pulsaría «Ya lo resolví» a los 20 s | la pausa dura 20 s, sin leer la página; después, 1 s de espera y «superada» | la pausa termina sola a los 6 s («DataDome dejó pasar la página»), con 12 lecturas con plazo, y la espera de después no corre |
| DataDome restringe el acceso a los 4 s | se ve a los 20 s, después del botón | se ve a los 4 s: CMA-CGM se detiene |
| «Detener» a los 4 s; el panel cierra el navegador | la espera de después falla con la página cerrada (`Page.wait_for_timeout`), como en `logs/` el 06-10 | `CmaCancelada`, sin ninguna lectura ni espera después de «Detener» |
| «Ya lo resolví», y en la espera de después «Detener», que cierra el navegador justo después de esa espera | «Verificación de CMA CGM superada ✓», y True | `CmaCancelada` |

## 2. Lo que cambió

### Los comentarios

- `_cma_comentarios` lleva la cuenta de si ya los escribió: el JavaScript dijo que sí, o el localizador los escribió.
- Si algo falla antes, corta con `ObjetivoNoEncontrado`, con lo que falló. Cuenta lo que falle al correr el
  JavaScript, también por no volver en 30 s, al mirar si se ve el campo del localizador, o al escribirlo.
- El corte lo convierte en NO ENVIADA `_sin_clic_a_ciegas`, que ya envolvía a `reservar_cma`, con la captura y el HTML
  del paso. Antes, `_cma_si_se_detuvo` mira si DataDome está: si lo está, decide DataDome.
- El motivo, en la planilla: «Comentarios de CMA: no encontré el campo de comentarios (…), porque el programa falló al
  buscarlo o escribirlo (RuntimeError: …), así que no pulsé nada. La reserva no se envió; revisa ese paso en el
  portal.» Empieza por «no encontré» porque así arma su texto `_sin_clic_a_ciegas`.
- El texto de lo que busca va una sola vez, `CMA_CAMPO_COMENTARIOS`: lo usan los dos cortes.
- Lo que falle después de escribirlos (la espera de 0,8 s, por ejemplo) se anota y la reserva sigue, como antes.
- Lo cosmético se sigue tragando: la espera a que se cierre el cajón y el JavaScript que quita la selección azul. Con
  la página que no contesta, ese JavaScript gasta sus 30 s, y el de los comentarios otros 30: corta al minuto.

### La pausa del deslizador

- **El panel recibe qué mirar.** `_pausa_del_panel` acepta `hasta`, una función sin argumentos, y se la pasa al panel.
  Solo la usa el deslizador de CMA: las pausas de COSCO, MSC y las demás siguen igual.
- **Panel web** (`_web_pausa`): después de cada espera de 2 s, si ningún botón soltó la pausa, llama a `hasta`. En la
  vuelta siguiente, después de mirar «Detener» y «Ya lo resolví», termina con lo que devolvió. Con un botón ya
  pulsado no lo llama: «Detener» también suelta la pausa, y así no lee la página que el panel cierra. La pausa vence a
  los 10 minutos de reloj: con lo que tarda en leer, 300 vueltas pasarían de 10 minutos.
- **Panel Tkinter** (`_pausa`): espera «Ya lo resolví» de a 2 s, y entre una espera y otra llama a `hasta`. Si devuelve
  algo, lo dice por su cola, que apaga el botón, y termina.
- **Qué se mira** (`_cma_como_quedo`): lo que ya miraba la espera de después, ahora en una sola función para las dos.
  Si `_cma_es_robotcheck` ya no ve a DataDome y la página sigue abierta, DataDome dejó pasar la página; si
  `_cma_datadome` ve el bloqueo, lo restringió; si no, nada. Todo con plazo (1,5 s por lectura), sin tocar la página.
- **La espera** (`_cma_pedir_deslizador`): si la pausa terminó sola, no corre la espera de después. Con la página que
  pasó, «superada» y sigue; con el bloqueo, `_cma_detener`, como antes. Si terminó con «Ya lo resolví» o al vencer,
  la espera de después corre como antes, hasta 180 s.
- **Una página cerrada no dejó pasar nada.** Antes, si el navegador se cerraba entre la espera y la lectura, el
  detector no veía a DataDome y la espera la daba por superada.

### «Detener»

- `_cma_si_pulso_detener` corta si la pausa terminó con «Detener», o si el «Detener» del panel web está pulsado (lo
  mira como ya lo hacía `reservar_cosco`). Lo dice en `log.txt` y levanta `CmaCancelada`, sin leer la página.
- La espera de después lo mira al empezar cada vuelta, si su espera falla (el panel cerró el navegador) y después de
  leer: lo leído mientras el panel lo cerraba no vale.
- `CmaCancelada` deriva de `CmaDetenida`. El login la ataja igual que antes (`_cma_login_se_detiene`: sin sesión) y no
  deja motivo en el Registro. El reservador (`_cma_si_se_detuvo`) deja la fila DETENIDO, «Cancelado por el operador»,
  el mismo estado y el mismo texto que COSCO y el trabajador del panel con «Detener».
- Es una excepción, y no un False, porque la espera corre también dentro de `_ir_al_form`, que se traga toda
  `Exception`; `CmaDetenida` ya es `BaseException`, y nada antes de la guarda se la traga (la regla del módulo).

## 3. La revisión

### Cómo se hizo

- **Un subagente** (`code-reviewer`), en un clon de `edc4202` dentro de la carpeta del encargo (`git clone
  --no-hardlinks`: 82 archivos, sin `logs/`, `config.json` ni `perfiles/`), sobre el rango `54db6cb..edc4202`: el
  encargo 55 (`eba3d71`, `a6159b3`) y este (`f04cba3`, `edc4202`).
- **Lo que se le pidió:** solo leer, en el clon, sin correr pruebas ni el programa; buscar errores de comportamiento
  contra lo decidido, regresiones, pruebas que no prueban y documentos que no calzan con el código; confirmar cada
  sospecha en el código; y devolver cada hallazgo con su camino, su gravedad y qué tan seguro está, los descartados y
  su cobertura.
- **Lo que leyó:** el diff entero del rango, `tests/test_datadome.py`, el informe del encargo 55, `LEEME.md`, las
  partes de `AQUASHIELD.py` que tocó el rango y sus vecinas, y los diffs de las demás pruebas. No leyó el código de las
  otras navieras fuera del rango, ni `tests/correr.py`, ni `tests/sonda_secretos.py`.
- **Tardó 27 minutos,** mientras corría el censo de las áreas del cambio.
- **Se desvió en una cosa:** escribió dos archivos de trabajo con salida de `git diff` en la carpeta del encargo, fuera
  del clon, aunque se le pidió solo leer. No tocó el clon ni el repo vivo (`git status`, vacío). Los borré al limpiar.

### Lo que encontró, y qué hice

Ningún hallazgo ALTO; uno MEDIO y cuatro BAJOS. Verifiqué cada uno en el código.

1. **MEDIA: Reefer, «I Agree», el tamaño y tipo, y el peso siguen el patrón que este encargo cerró en los
   comentarios:** si fallan, se anota y la fila sigue.
   - **Verificado:** `_cma_ajustes_reefer` se traga toda falla y devuelve False, y `reservar_cma` no mira ese False.
     El paso de «I Agree» va en un `try` que se traga la falla del JavaScript que lo precede, y entonces «I Agree» ni
     se intenta. El tamaño y el peso, igual.
   - **Desde el encargo 55,** también si la página no contesta en 30 s: antes de él, esa lectura no volvía.
   - **Con el candado abierto,** la reserva llegaría al botón final sin, por ejemplo, la temperatura guardada.
   - **En `logs/` no pasó nunca** (`sondeo_otras_fallas.py`, sobre 37 `log.txt`):

     | paso | corrió | lo hizo | cortado por «no encontré» | falla tragada |
     |---|---|---|---|---|
     | Reefer | 15 | 14 | 1 | 0 |
     | «I Agree» | 14 | 14 | 0 | 0 |
     | tamaño y tipo | 25 | 25 | 0 | 0 |
     | peso | 25 | 25 | 0 | 0 |

   - **Qué hice:** nada en el código. Es la misma decisión de los comentarios, para otros pasos: la decides tú
     (residual 1).
2. **BAJA: en el panel Tkinter, después del primer «Ya lo resolví» de una corrida, las pausas que siguen no esperan.**
   - Su evento queda marcado (se limpia solo al empezar la corrida), y `log.txt` dice «terminó a los 0 s» sin que
     nadie pulsara.
   - Al terminar sola, la pausa apaga el botón, pero su etiqueta sigue pidiéndolo.
   - **Verificado.** Ya pasaba antes de este encargo. La espera de 180 s de después sí espera y mira la página: no se
     pierde ninguna reserva.
   - **Qué hice:** lo propongo (residual 2). El arreglo es una línea, pero cambia también las pausas de COSCO y MSC
     en el panel de respaldo, que el encargo no tocaba.
3. **BAJA (plausible): una sola lectura sin DataDome termina la pausa.**
   - Si cae en un instante de paso, sin su marco, la pausa terminaría antes de tiempo. A mitad de una reserva, el
     motivo diría «el operador deslizó la flecha».
   - **Verificado:** es el mismo reconocimiento que ya usaba la espera de después, con una lectura (8 de 8 en `logs/`).
     Lo nuevo es que ahora corre también mientras el operador desliza.
   - **Los instantes de paso de DataDome no están medidos:** hace falta el portal.
   - **Si pasa en el login,** el paso siguiente vuelve a ver el deslizador y pide otra pausa. A mitad de una reserva,
     la fila queda NO ENVIADA igual.
   - **Qué hice:** lo propongo (residual 3): pedir dos lecturas seguidas.
4. **BAJA: con el candado abierto, si la página no contesta antes del botón final, el motivo dice «no estaba en la
   pantalla».**
   - **Verificado.** Es el residual 17 del encargo 55, y sigue (residual 11).
5. **BAJA: documentos que no calzaban.**
   - El informe de este encargo todavía no estaba en el repo, y el código y las pruebas ya lo citaban: es este.
   - El informe del encargo 55 lista como abiertos sus residuales 5, 9 y 10, que este cerró: lo dice el residual 12.
   - `_pausa_del_panel` y `CLAUDE.md` decían que el panel Tkinter no dice cómo terminó su pausa. Con `hasta`, lo
     dice: lo corregí.
   - `CLAUDE.md` decía que `AQUASHIELD.py` tiene «~12 900 líneas», y son 16.001: lo corregí (~16 000). Era anterior al
     rango, de una línea.
   - El docstring cambia solo texto: las anclas de las mutaciones siguen (0 problemas) y la suite corrió de nuevo
     (sección 4).

**Lo que descartó**, cada cosa con su lectura del código:
- **Los comentarios:** sus cuatro caminos cortan o escriben.
- **La pausa:** termina solo con un botón, a los 10 minutos o con los dos valores del vigía. «Detener» se mira
  primero, y lo leído mientras cierra no vale.
- **Lo que no pasa:**
  - ninguna lectura de CMA sin plazo fuera de las de siempre;
  - nada que detenga o corte después de la guarda;
  - nada que se trague el corte;
  - ningún clic nuevo, y nada del disfraz;
  - las pausas de COSCO y MSC, como antes.
- **Los hilos:** `hasta` corre en el hilo del navegador, y no con el candado del panel tomado.
- **Las anclas y los conteos:**
  - las 36 mutaciones nuevas, cada texto viejo una vez;
  - las 698 pruebas, las que dice `CLAUDE.md`;
  - los commits, sin CR y con el correo noreply.
- **Lo que no pudo verificar:** que `/api/detener` cierre de verdad el navegador desde otro hilo (la API síncrona de
  Playwright no es para varios hilos). El corte no depende de eso: mira el «Detener» del panel. Va al residual 6.

## 4. Pruebas, mutaciones, suite y censos

- **Pruebas nuevas, 22** (de 676 a 698):
  - en `test_datadome`, `TestPausaQueTerminaSola` (11): con la pausa de verdad del panel web y una espera falsa que
    avanza la página, la pausa termina sola cuando DataDome deja pasar, cuando bloquea y a mitad de una reserva; sigue
    esperando sin cambios; «Detener» la corta sin ninguna lectura después, también en la espera de después y con el
    navegador ya cerrado; una pausa que dice «Detener» basta; la fila queda DETENIDO y el login sin sesión; una página
    cerrada no dejó pasar nada; y lo medido;
  - en `test_web`, `TestPausaDelPanel` (4 más): la pausa termina con lo que dice `hasta`; con un botón pulsado no mira;
    «Detener» va antes que lo que vio; con `hasta`, vence a los 10 minutos de reloj;
  - en `test_web`, `TestPausaDelPanelTkinter` (3): termina sola, «Ya lo resolví» como antes, y la cola apaga el botón.
    El panel no se abre en una prueba: `metodo_del_panel_tkinter` compila suelto el método de su clase `Panel` desde
    las fuentes del programa, y lo corre con un `self` falso;
  - en `test_clics`, `TestCma` (4): los comentarios que fallan cortan (con una falla del JavaScript y con el plazo
    vencido), también si el localizador no escribe; lo que falla después de escribirlos sigue como antes; y la fila,
    con los decoradores de `reservar_cma`, queda NO ENVIADA con el motivo, la captura y el HTML.
- **Pruebas que cambiaron:**
  - `test_comentarios_sin_su_campo_corta` compara ahora el texto entero de lo que buscaba, para que una mutación de
    `CMA_CAMPO_COMENTARIOS` muerda;
  - `test_lo_que_detiene_no_corre_despues_de_la_guarda` cuenta también `CmaCancelada`, y exige que la espera del
    deslizador esté entre lo que detiene: sigue sin nada después de la guarda;
  - las pausas falsas de `test_datadome` reciben `hasta`;
  - la página falsa de DataDome puede estar cerrada (sus lecturas fallan, como las de Playwright) y corre algo en
    cada espera (`al_esperar`).
- **Mutaciones: 2.040** (eran 2.004). Entran 36, una al menos por prueba nueva, y se reescriben 4 que el cambio dejó
  sin ancla, con sus mismos ids: el campo de los comentarios que no corta, el bloqueo en la espera del deslizador (en
  dos mutaciones, ahora una en `_cma_como_quedo` y otra donde la espera se detiene) y la pausa del deslizador sin
  anotar. `mut_viejos.py` da 0 problemas: cada texto viejo, una vez; las 40, compiladas; toda prueba, con su mutación.
- **El censo chico** (`censo_mini.py`), antes de la suite: las 36 nuevas y las 4 reescritas. 40 mutaciones, 62 pares
  y 28 pruebas: el control pasa, **muerden los 62**, y 0 cambios en las 4.543 entradas fotografiadas de los
  originales.
- **La suite:** 698 pruebas, OK, en 509 s (511 s con la foto), y 0 cambios en las 4.543 entradas fotografiadas, sobre
  el árbol que se commiteó en `f04cba3` (`correr_sin_tope.py`: la suite de siempre, con el plazo de la corrida entera
  en 7.200 s). Después de lo documental de la revisión, corrió dos veces más sobre el árbol final:
  - la primera dio 697 de 698, con una falla en `test_web.TestArranqueDelPanel`
    `.test_puerto_que_se_suelta_mientras_pregunta`: el lanzador tomó el puerto siguiente (27614 en vez de 27613);
  - la segunda, **698 pruebas, OK, en 472 s** (473 s con la foto); las dos, con 0 cambios en las 4.543 entradas
    fotografiadas de los originales.

  Esa prueba es del encargo 52 (`db70949`), depende del tiempo (el ocupante suelta el puerto a los 2 s, mientras el
  lanzador le vuelve a preguntar) y este encargo no la toca. Corrida sola 10 veces, pasó 8 sobre el árbol de hoy y
  6 sobre las fuentes de `a6159b3`; justo después, la CPU estaba entre el 2 y el 30 % (residual 15).
- **El censo de las áreas del cambio** (`alcance_censo.py`, `censo_e56.py`): la unión de las 36 del encargo, las 4
  reescritas, las que caen en las funciones que cambiaron (59) y las que nombran una prueba cuyo camino cambió (las de
  CMA y las de la pausa, 318). Son 319 mutaciones, 449 pares y 147 pruebas, sobre
  el árbol commiteado. Corrió aparte (`lanzar_censo_e56.py`), de las 23:06 a las 23:24, mientras el revisor
  trabajaba en el clon. El control (la copia sin mutar, 147 pruebas) pasa, **muerden los 449 pares**, ninguno da
  FALLA, y hay 0 cambios en las 4.543 entradas fotografiadas de los originales.

## Re-medir

Todo en `e56/` (carpeta del encargo), con `source entorno_e56.sh` antes.

| qué | cómo |
|---|---|
| los comentarios y las esperas del deslizador en `logs/` | `python sondeo_logs.py` |
| las 3 esperas sin desenlace | `python sondeo_sin_desenlace.py` y `python sondeo_error.py` |
| cuánto tardó cada espera superada | `python sondeo_duracion.py` |
| las fallas que se tragan el Reefer, «I Agree», el tamaño y el peso (hallazgo 1) | `python sondeo_otras_fallas.py` |
| lo que se le pidió al revisor | `encargo_revisor_listo.md` |
| antes y después | `python contra_head.py fuentes_head` y `python contra_head.py fuentes_arbol` (las fuentes: `git show a6159b3:AQUASHIELD.py`, y la copia del árbol) |
| las anclas de las mutaciones | `python mut_viejos.py e56` |
| el censo chico | `python censo_mini.py` (40 mutaciones, 62 pares) |
| el alcance del censo | `python alcance_censo.py` |
| el censo | `python lanzar_censo_e56.py` (aparte, sin ventana; escribe `censo_e56.txt`) |
| la suite | `python correr_sin_tope.py` (o `python tests/correr.py` en el repo) |
| que nada toca el disfraz ni el candado | `git diff a6159b3 -- AQUASHIELD.py` sin `STEALTH_JS`, `_args_chrome`, `_lanzar_navegador` ni `ignore_default_args`; `git diff a6159b3 -- tests/test_candado.py` vacío |

## NO retroceder

- **Los comentarios de CMA no vuelven a tragarse su falla.** Si no se escribieron, la fila no sigue: con el candado
  abierto se habría enviado sin ellos.
- **La pausa del deslizador mira la página mientras espera, con lo mismo que la espera de después** (`_cma_como_quedo`):
  una sola función para las dos, y no otro reconocimiento sin medir.
- **Una página cerrada no cuenta como que DataDome dejó pasar.**
- **«Detener» va antes que lo que la pausa haya visto, y con un botón ya pulsado la pausa no lee la página:** lo que
  se lee mientras el panel cierra el navegador no vale.
- **`CmaCancelada` sigue siendo `BaseException`** (por `CmaDetenida`): `_ir_al_form` se traga toda `Exception`, y la
  fila quedaría NO ENVIADA con el motivo del paso siguiente.
- **Con `hasta`, la pausa del panel web vence por reloj**, no solo por vueltas.

## Defectos de instrumento

1. **Usé `sort` de Git Bash, que Defender bloquea**, en una tubería que contaba los resultados del censo chico. Salió
   «Permission denied» y no contó nada. El conteo lo hice con `grep -c`, y ningún número depende de esa tubería. Está
   en el entorno de la máquina: no se usa.
2. **Mi sondeo de las esperas sin desenlace iba a imprimir el comienzo del nombre de cada carpeta,** y en las del
   login ese comienzo es el nombre del operador. Lo vi antes de correrlo: imprime solo «web», «reservas» u «otro
   (login)». El nombre no se imprimió.
3. **Mi primer control del largo de las líneas las pasó por una tubería de Git Bash a Python,** que las leyó en cp1252:
   cada tilde y cada eñe contaban dos, y dio 12 líneas largas que no lo eran. Lo rehíce leyendo el archivo en UTF-8
   (`largas.py`): quedaba una, de 122 caracteres, y la partí.
4. **El primer docstring de `_cma_si_pulso_detener` atribuía a «Detener» las dos esperas de `logs/` que fallaron con
   la página cerrada.** En «Solo iniciar sesión», «Detener» no cierra el navegador, y una de las dos ni siquiera era
   la primera espera. Lo corregí antes del commit: el docstring ya no cita `logs/`.
5. **Un `cd tests` en primer plano movió la sesión a `tests/`,** como dice el entorno de la máquina. Desde ahí, los
   comandos van con ruta absoluta.
6. **Dos pruebas nuevas habrían caído por sus falsos, no por el programa.** La que deja vencer la pausa pasaba el tope
   de 100 esperas de la página falsa: le di 400, como a las otras que esperan 180 s. La de la cola del Tkinter no le
   daba a su `self` falso el `procesar_cola` que se vuelve a programar. Las arreglé antes de correrlas.

## Premisas refutadas

1. **El informe del encargo 55 daba a entender que a las 14:26 la página la había cerrado «Detener»** (su residual 10:
   «la espera … vuelve a mirar la página, que el panel ya cerró … En la portada, REVISAR, como a las 14:26»). Esa
   espera fue en «Solo iniciar sesión», y ahí «Detener» no cierra el navegador: `/api/detener` cierra el contexto que
   registran las reservas (`_WEB["ctx"]`), y el login no lo registra (leído en el código). La página de las 14:32 se
   cerró por otra vía, que no está medida. Lo que el encargo 55 dejó «leído en el código, sin medir» (que con
   «Detener» la espera vuelve a mirar la página y falla, o la da por superada) quedó medido sin red, con páginas
   falsas, contra `a6159b3` (sección 1).
2. **«Si el JavaScript de los comentarios de CMA-CGM falla»: no era el único camino.** El campo que vio el
   localizador, si no se dejaba escribir, también dejaba la reserva sin comentarios, y también corta. Y en `logs/`
   no pasó nunca (0 de 14): no es una falla observada, y el cambio es preventivo.

## Residual

| # | qué queda | por qué | se reabre si |
|---|---|---|---|
| 1 | **Decides tú:** el Reefer (la temperatura y su «Guardar»), «I Agree», el tamaño y tipo, y el peso, si fallan, se anotan y la fila sigue (hallazgo 1). En `logs/`, nunca pasó | la decisión fue para los comentarios | decides que corten como ellos (propuesta: sí, con motivo, captura y HTML) |
| 2 | **Decides tú:** en el panel Tkinter, después del primer «Ya lo resolví» de una corrida, las pausas que siguen no esperan, y al terminar sola su etiqueta sigue pidiendo el botón (hallazgo 2; ya pasaba) | el arreglo cambia también las pausas de COSCO y MSC en el panel de respaldo | lo pides (propuesta: limpiar el evento al empezar cada pausa) |
| 3 | **Decides tú:** una sola lectura sin DataDome termina la pausa (hallazgo 3) | los instantes de paso de DataDome no están medidos | una pausa termina sola y el paso siguiente encuentra a DataDome (propuesta: dos lecturas seguidas) |
| 4 | Mientras dura la pausa, el programa lee la página cada 2 s (la espera de después ya leía cada 1 s): si DataDome reacciona a esas lecturas no está medido | hace falta el portal | una corrida muestra un bloqueo justo después de deslizar |
| 5 | **Decides tú:** en «Solo iniciar sesión», «Detener» no cierra el navegador ni detiene los inicios de sesión que siguen: corta solo la espera del deslizador y las pausas (leído en el código; ya pasaba) | fuera del encargo | lo pides |
| 6 | Que `/api/detener` cierre de verdad el navegador desde otro hilo no está medido | código anterior; el corte no depende de eso | una corrida con «Detener» deja el navegador abierto |
| 7 | Al terminar sola, la pausa desaparece del panel web, pero la línea de estado sigue diciendo «Te toca a ti…» hasta el estado siguiente, como después de «Ya lo resolví» (leído en el código) | ya pasaba con el botón | confunde al operador |
| 8 | El motivo del corte de los comentarios empieza por «no encontré el campo…», aunque el JavaScript lo haya encontrado y fallado después | es el texto de `_sin_clic_a_ciegas`, común a todos los cortes | lo pides con un motivo propio |
| 9 | «Detener» en el segundo y medio que la espera se da después de «superada», o en otra espera de `_ir_al_form`: `_ir_al_form` se traga la falla de la página, y la fila puede quedar NO ENVIADA con el motivo del paso siguiente, en vez de DETENIDO (leído en el código) | una ventana corta; arreglarlo es tocar `_ir_al_form` | pasa en una corrida |
| 10 | Con el deslizador a la vista y nadie que lo pase, la pausa vence a los 10 minutos y la espera de después sigue 180 s: unos 13 minutos antes de NO ENVIADA, como antes | no se pidió | lo pides más corto |
| 11 | Con el candado abierto, si la página no contesta antes del botón final, el motivo dice «no estaba en la pantalla» (hallazgo 4; residual 17 del encargo 55) | `_resultado_envio` no distingue por qué no se pulsó; CMA nunca llegó a emitir | CMA emite y se ve ese motivo |
| 12 | Del encargo 55 siguen abiertos sus residuales 1, 2, 4, 6, 8, 12, 13 y 14, y el 11 en parte (el Tkinter dice cómo terminó su pausa solo cuando termina sola). Este encargo cerró sus 3 y 7 (los decidiste: se mantienen) y sus 5, 9 y 10 (los comentarios, la pausa que termina sola y «Detener») | — | — |
| 13 | Más revisiones de ECC (python-reviewer, security-reviewer) | se proponen, no se lanzan; el encargo pidió una, y es la de la sección 3 | las pides |
| 14 | El censo es el de las áreas del cambio, no el completo (2.040 mutaciones) | el completo pasa de 2 h | lo pides |
| 15 | `test_puerto_que_se_suelta_mientras_pregunta` (encargo 52) falla a ratos: depende de que el ocupante suelte el puerto a los 2 s mientras el lanzador le vuelve a preguntar. Corrida sola 10 veces, pasó 8 sobre el árbol de hoy y 6 sobre las fuentes de `a6159b3` | no la toca este encargo | lo pides (propuesta: medir en qué momento decide el lanzador y darle margen al ocupante) |

## Reglas de método (v16)

- **Aplicadas:** las 20 universales. En especial:
  - el contador al lado de cada cero: en `logs/`, 37 de 37 leídos y 0 ilegibles, y cada tabla suma su total (14
    pasos, 11 pedidos); 0 problemas de anclas en 2.040 mutaciones; 0 cambios en las 4.543 entradas fotografiadas;
  - el control positivo: el sondeo de `logs/` aborta si no encuentra su caso conocido; `mut_viejos.py`, con su
    mutación sintética; y el vigilante del censo, que reconoció vivo su proceso y no un pid inventado;
  - el negativo que muerde: cada prueba nueva con su mutación, y los dos censos;
  - re-medir contra HEAD: el antes y después, con las fuentes de `a6159b3`;
  - un gate en cero prueba contención, no correctitud: además de la suite, las pruebas que corren la pausa de verdad
    del panel y el censo;
  - fuente única: `_cma_como_quedo` para la pausa y para la espera de después, y `CMA_CAMPO_COMENTARIOS`;
  - el cambio y su guardián en la misma operación; cada reemplazo, una sola vez y validado antes de escribir; el EOL,
    LF (0 CR);
  - el residual y las premisas refutadas, declarados; y frenar en lo que es de Marcelo: lo que encontré fuera del
    encargo va al residual como propuesta.
- **Las del módulo** (`CLAUDE.md`): `test_candado` no cambia; ningún clic nuevo; nada se traga el corte; casos
  sintéticos; la sonda de secretos antes de cada commit; el correo noreply de autor y de committer.
- **Choques:**
  - **ECC pide lanzar revisores y agentes solos;** las reglas permanentes dicen que se proponen. Este encargo pidió una
    revisión por un subagente: la lancé, una sola, y las demás quedan propuestas (residual).
  - **«Los revisores nunca trabajan en el repo vivo».** El revisor trabajó en un clon dentro de la carpeta del encargo.
    La herramienta lo arranca en el directorio de la sesión, que es el del repo vivo: le di solo rutas del clon y la
    orden de no abrir el repo vivo. El repo vivo quedó sin cambios (`git status` vacío).
  - **«Nada atrapa el corte».** El decorador de CMA ataja `CmaCancelada` para dejar la fila DETENIDO, como ya atajaba
    `CmaDetenida`; `ObjetivoNoEncontrado` lo sigue volviendo a levantar (`test_nada_se_traga_el_corte` y
    `test_el_decorador_no_se_traga_el_corte` pasan).
- **Pieza 8 (el entregable renderizado y mirado):** opcional; este informe es Markdown y no lo rendericé.

## Lo que dio en el repo

Tres commits en `main`, sin push (el push lo haces tú):

- `f04cba3` fix: el programa y las pruebas (`AQUASHIELD.py` y, en `tests/`, `mutaciones.py`, `test_clics.py`,
  `test_datadome.py` y `test_web.py`);
- `edc4202` docs: `CLAUDE.md` y `LEEME.md` al día, antes de la revisión, para que la revisión los viera;
- el commit siguiente, docs: este informe, y lo documental que encontró la revisión (el docstring de
  `_pausa_del_panel` y dos lugares de `CLAUDE.md`).

Los tres llevan de autor y de committer el correo noreply del repo. La sonda de secretos dio 0 en el árbol y en el
staging, y cada archivo commiteado es igual al del árbol, sin CR.

El entorno de la máquina (`~/.claude/CLAUDE.md`) no lleva filas nuevas: lo que falló aquí (el `sort` de Git Bash y el
`cd` que mueve la sesión) ya estaba.
