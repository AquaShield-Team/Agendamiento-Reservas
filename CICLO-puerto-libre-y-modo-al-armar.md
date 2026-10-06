# Encargo 52 · El lanzador no cierra a otro programa, y el panel mira su modo antes de armar

Base: `C:\dev\Agendamiento Reservas` @ `3a8fbf3` · árbol limpio.

## En resumen

- **Hasta hoy, el lanzador sí habría cerrado a la fuerza a `servidor_sync.py`.** Lo medí sin tocarlo:
  - escucha en `127.0.0.1:8765`, y con un dueño así el panel no puede enlazar el puerto;
  - el `netstat | findstr` del lanzador, corrido sin el taskkill, da su pid;
  - y el lanzador de `3a8fbf3`, ante un programa ajeno igual (un `http.server` que contesta 404), le pidió a taskkill
    que lo cerrara.

  **Desde este encargo, el lanzador no cierra a nadie:** prueba el puerto siguiente, hasta el 8768, y el registro del
  panel dice por qué.
- **Los paneles de AQUASHIELD se tratan como hasta hoy, en cualquiera de los cuatro puertos:** en el otro modo, avisa y
  no corre; en el mismo, al ocupado lo abre en el navegador, y al ocioso le pide que se apague y toma su puerto.
- **Una diferencia, que decidí dentro del encargo: al panel ocioso que no suelta su puerto tampoco lo cierra.**
  - Hasta hoy, a los 0,6 s le pedía a taskkill que cerrara a todos los que siguieran en el puerto, por los pid que
    daba netstat. Eso no distingue al panel de otro programa que escuche en el mismo puerto (uno en `0.0.0.0`, con el
    panel encima en `127.0.0.1`), o que lo haya tomado justo después.
  - Ahora espera a que lo suelte, hasta 5 s: sin carga, lo suelta a los 0,52 s (medido 5 veces). Si no lo suelta,
    prueba el siguiente.
  - Si prefieres que lo cierre, se puede hacer solo con el pid que contestó como AQUASHIELD: queda como propuesta.
- **Un hallazgo del camino: que el puerto se pueda enlazar no dice que esté libre.** Si un programa escucha en todas las
  direcciones (`0.0.0.0`), se le puede enlazar encima `127.0.0.1`, y lo que llega por ahí pasa al panel (medido). Por
  eso, el lanzador ya no usa un puerto donde contestó otro programa, aunque pudiera enlazarlo.
- **El panel vuelve a leer su modo antes de armar las reservas.** Si no es el que muestra la página, no arma y avisa que
  hay que recargarla (F5).
  - Lo mira la página, antes de tocar la tabla.
  - Lo vuelve a mirar el servidor al recibir la corrida: la página le manda el modo que muestra.
  - Una página que no lo manda, como una pestaña de antes de este encargo, tampoco arma.
- **Ningún FRENA SI se cumplió.**
  - Usar otro puerto no rompe nada que dependa del 8765: ni los `.bat`, ni `AQUASHIELD_EMISION.py`, ni las pruebas lo
    nombran, y la página le pide todo a su propio puerto.
  - Lo que sí cambia, y te lo digo: el tema y el nombre que la página guarda en el navegador son de cada puerto, y un
    marcador al 8765 llevaría al otro programa.
  - `test_candado` no cambió, y pasa.
- **El censo completo de mutaciones: 1.848 mutaciones y 2.252 pares, todos muerden**, y ninguna prueba queda sin su
  mutación. El primero se cortó a las 2 horas, por el tope de la herramienta; lo relancé aparte y terminó (abajo).
- Las pruebas pasan de 598 a 608, y la suite completa pasa: 608 pruebas en 512 s, con los 4.470 originales sin
  cambios.

## 1. El lanzador y el programa que tiene el 8765

### Lo que hacía hasta hoy (medido)

Medí quién escucha sin hablarle a nadie (`quien_escucha.py`: netstat, la lista de procesos y, de cada uno, el nombre de
su programa y de su script, sin rutas ni argumentos). Del 8765 al 8768 había uno solo: `python3.13.exe`, con
`servidor_sync.py`, en el 8765 y en `127.0.0.1`.

Después medí qué pasa cuando un segundo socket quiere enlazarse a `127.0.0.1` en un puerto donde otro ya escucha
(`enlaces.py`). Usé sockets propios, en puertos al azar y nunca del 8765 al 8768: 12 combinaciones de dirección y
opción del primero y del segundo.

| El que ya escucha | El segundo, en `127.0.0.1` (sin opción, como el panel, o con `SO_EXCLUSIVEADDRUSE`) |
|---|---|
| en `127.0.0.1`, sin opción, con `SO_REUSEADDR` o con `SO_EXCLUSIVEADDRUSE` | falla (10048) |
| en `0.0.0.0`, sin opción o con `SO_REUSEADDR` | **se enlaza, y una conexión a `127.0.0.1` le llega al segundo** |
| en `0.0.0.0`, con `SO_EXCLUSIVEADDRUSE` | falla (10013) |

El control: el servidor del panel (`_Srv`, sin `SO_REUSEADDR`) no se enlazó al puerto de un `http.server` corriente en
`127.0.0.1` (10048).

Con `servidor_sync.py` en `127.0.0.1:8765`, el panel no puede enlazar el 8765. Ahí, el lanzador de `3a8fbf3` hacía
esto:

1. le preguntaba por `/api/estado`, con 1 s de plazo, y otra vez con 5 s;
2. como no contestaba como AQUASHIELD, buscaba con `netstat | findstr` el pid de quien escuchaba en el puerto;
3. y le pedía a taskkill que lo cerrara a la fuerza (`taskkill /F`).

Lo medí sin red (`experimento_ajeno.py`). El programa ajeno era un `http.server` que contesta 404, en `127.0.0.1`, y
el lanzador era una copia del programa en una carpeta aislada. netstat y taskkill no corrieron: el falso solo anotaba.
El lanzador preguntó dos veces, llamó a netstat y pidió `taskkill /F /PID` del pid que netstat le dio. Como el taskkill
era falso, el ajeno siguió vivo y el panel abrió en el puerto siguiente. Con el taskkill de verdad, lo habría cerrado y
tomado su puerto.

El `netstat | findstr` de `_liberar_puerto`, corrido tal cual pero sin el taskkill (`findstr_hoy.py`), encontró hoy
una línea y un pid en el 8765. Era el de `servidor_sync.py`.

### El cambio

`lanzar_web` busca su puerto desde el 8765 hasta el 8768 (`PUERTOS_DEL_PANEL`). En cada uno pregunta quién está, con
`_panel_en`, que ahora distingue tres respuestas:
- **nadie** (`None`): nadie contesta en 1 s;
- **otro programa** (`False`): contesta con otro código HTTP, sin hablar HTTP, o con un `/api/estado` que no trae
  «corriendo»;
- **un panel de AQUASHIELD**: su estado y su modo, como hasta hoy.

Con lo que encuentra en cada puerto, hace esto:
- **Si no contesta nadie**, enlaza el puerto. Si está tomado, le vuelve a preguntar con más paciencia (hasta
  `PANEL_ESPERA_LARGA`, 5 s), como desde la revisión del encargo 51: un panel del otro modo que tarda en contestar avisa
  y no corre. Si tampoco contesta nadie, prueba otra vez el puerto, por si se soltó mientras tanto.
- **Si contesta otro programa, no lo cierra:** lo dice en el registro del panel («El puerto 8765 lo tiene otro
  programa, que no contesta como AQUASHIELD: no lo cerré.») y prueba el siguiente. No usa ese puerto aunque pudiera
  enlazarlo: es el caso de `0.0.0.0` de la tabla.
- **Si contesta un panel de AQUASHIELD**, decide `_ceder_al_previo`, como hasta hoy en el 8765:
  - en el otro modo, o sin decir en cuál, avisa y no corre;
  - en el mismo y ocupado, lo abre en el navegador;
  - en el mismo y ocioso, le pide que se apague y toma su puerto (punto 2).

Si los cuatro están tomados, `lanzar_web` falla y `main()` abre el panel Tkinter, como antes.

Antes y después, sin red y con los mismos falsos (`experimento_despues.py`, 3 veces cada caso):

| El puerto base | `3a8fbf3` | Ahora |
|---|---|---|
| libre | lo toma a los 1,0 o 1,1 s, sin llamar a nadie | igual: 1,0 s |
| lo tiene un programa que contesta 404 | le pregunta dos veces, llama a netstat y pide `taskkill /F`. Con el falso, a los 0,5 s abre en el siguiente; con el de verdad, lo habría cerrado y tomado el base | le pregunta una vez, no llama a nadie y abre en el siguiente a los 1,0 s |
| lo tiene un programa que acepta y calla | lo mismo, a los 6,5 o 6,6 s | no llama a nadie y abre en el siguiente a los 7,1 s (1 s y 5 s de sus dos preguntas, y 1 s de la del siguiente) |

Preguntarle a un puerto donde nadie escucha tarda 1 s en este equipo (encargo 51), y el lanzador lo paga una vez: en
el primer puerto libre que encuentra.

### Lo que cambia en otro puerto (el primer FRENA SI)

Busqué qué depende del 8765:
- todos los archivos versionados (`git grep 8765`);
- los lanzadores y los scripts de la raíz que no se versionan;
- y el JavaScript del panel.

| Dónde | Qué hace con el 8765 | ¿Se rompe en otro puerto? |
|---|---|---|
| `AQUASHIELD.py` | es el puerto base de `lanzar_web` | no: busca desde ahí |
| los dos `.bat` y `AQUASHIELD_EMISION.py` | no lo nombran | no |
| las pruebas | no lo usan (regla del módulo) | no |
| el JavaScript del panel | le pide todo a su propio puerto (rutas relativas) | no |
| lo que la página guarda en el navegador: el tema (`aq-tema`) y el nombre de quien la usa (`mars_reservas_usuario`) | el navegador lo guarda por origen, y el puerto es parte del origen | **cambia**: en el 8766 empiezan de nuevo, y se guardan aparte |
| un marcador del navegador al 8765 | — | **cambia**: llevaría al otro programa |
| `LEEME.md` y `CLAUDE.md` | decían «el panel en el 8765» | los actualicé |
| los manuales y el video tutorial (`generar_manuales.py` y `crear_video_tutorial.py`, fuera del repo) | lo nombran: 2 y 3 líneas | no se rompe nada; dicen el puerto de siempre. Los generadores no los toqué |
| los informes `CICLO-*.md` | lo nombran como historia | no |

Nada que funcione hoy depende del 8765. Además, el código de `3a8fbf3` ya abría el panel en el 8766, el 8767 o el
8768 cuando no podía liberar el 8765. Por eso no frené.

## 2. El panel ocioso que se apaga

Medí cuánto tarda un panel ocioso en soltar su puerto después de su `/api/apagar` (`experimento_ajeno.py`). Era un
proceso con una copia del programa, y probé enlazar su puerto cada 50 ms. Las 5 veces lo soltó a los 0,52 o 0,53 s, y
su proceso terminó entre los 0,58 y los 0,69 s.

Hasta hoy, el lanzador esperaba 0,6 s después de pedirle que se apagara y probaba el puerto. Si seguía tomado, le
pedía a taskkill que cerrara a quien lo tuviera, por el pid que daba netstat. Ese pid no tiene por qué ser solo el del
panel, y `_liberar_puerto` cerraba a todos los que netstat daba en el puerto:
- un puerto puede tener dos que escuchan: un programa en `0.0.0.0` y el panel encima, en `127.0.0.1` (la tabla del
  punto 1);
- y entre la pregunta y el taskkill, el panel puede soltar el puerto y otro programa tomarlo.

Lo que no pasa, y lo medí (`compartir.py`): con el panel escuchando primero en `127.0.0.1`, otro programa no puede
enlazarse a su puerto ni con `SO_REUSEADDR` (10013), ni sin opción o con `SO_EXCLUSIVEADDRUSE` (10048).

Para que el lanzador **nunca** cierre a la fuerza a un programa que no es AQUASHIELD, ya no llama a taskkill. Ahora
espera a que el panel suelte su puerto, probándolo cada 0,1 s, hasta `PANEL_ESPERA_LARGA` (5 s). Si no lo suelta,
lo dice («El panel de AQUASHIELD del puerto … no lo soltó en 5 s, después de pedirle que se apagara: no lo cerré.») y
prueba el siguiente.

Con lo medido, el trato que ves no cambia: le pide que se apague y toma su puerto. Lo único distinto es el panel que no
se apaga en 5 s: hasta hoy lo cerraba, y ahora queda abierto y el nuevo abre en el siguiente puerto. Si lo quieres
cerrado, la propuesta es cerrarlo solo si su pid es el que contestó como AQUASHIELD (residual).

## 3. El modo, antes de armar las reservas

La página pinta su aviso de modo al cargar, con el `modo_emision` de `/api/config`, y no lo vuelve a mirar. Una pestaña
que quedó abierta mientras su panel se cerraba, y otro del otro modo se abría en el mismo puerto, seguía mostrando el
aviso de antes. Desde ella se podían armar reservas en el otro modo (sospecha 1 de la revisión del encargo 51).

Ahora el panel lo vuelve a leer en dos lugares:

- **La página.** Guarda el modo con que pintó su aviso (`MODO_PAGINA`). Al pulsar **ARMAR LAS RESERVAS**, antes de tocar
  la tabla, vuelve a leer `/api/config` (`mismoModo`). Si no es el mismo, o el panel no dice uno, no arma y lo dice en
  el registro:

  > No armé las reservas: esta página muestra el modo prueba (sin emitir), y el panel está en modo EMISIÓN (reservas
  > reales). Recarga la página (F5) para ver el modo del panel, y vuelve a armarlas.

- **El servidor.** La página le manda el modo que muestra (`modo`, en `/api/correr`), y el servidor lo compara con el
  suyo. Si no es el mismo, o la página no lo manda, contesta 409 y no arma (`_modo_de_la_pagina`):

  > No armé las reservas: este panel está en modo EMISIÓN (reservas reales), y la página muestra el modo prueba (sin
  > emitir). Recarga la página (F5) para ver el modo del panel, y vuelve a armarlas.

  Así queda cubierta también una pestaña con el JavaScript de antes de este encargo, que no hace la primera pregunta: no
  manda el modo, y el panel no arma.

El servidor lee su modo con `_llaves_abiertas`, la misma regla del candado, como la línea de cada corrida.
`test_candado.test_llamadas_al_candado` fija quién llama a `es_modo_emision`, y no cambió.
`test_modo.test_el_candado_sale_de_las_llaves` vigila que `es_modo_emision` sea `bool(_llaves_abiertas())`.

Los nombres de los modos salen de `NOMBRE_DEL_MODO`, el mismo del aviso del lanzador. El JavaScript los repite, y su
prueba compara su texto con el de esa constante.

El aviso de modo sigue sin repintarse solo: lo hace la recarga. Solo iniciar sesión (**SOLO INICIAR SESIÓN**) no
pregunta el modo, porque no arma reservas.

## 4. Las pruebas del arranque, en puertos propios

Windows reparte seguidos los puertos de `bind(("127.0.0.1", 0))`: 30 pedidos dieron 30 puertos consecutivos
(`puertos_del_sistema.py`), en su rango dinámico, desde el 49152 (`netsh`). Las pruebas toman así su puerto
(`soporte.puerto_libre`), y el censo corre 4 a la vez. Dos de ellas pueden quedar en puertos vecinos, y el lanzador,
que ahora prueba el puerto siguiente, podría dar con el panel de otra prueba y pedirle que se apague.

Por eso, las pruebas del arranque usan `puertos_seguidos`: un puerto al azar entre el 20000 y el 39999, con sus cuatro
seguidos libres, fuera de los que reparte el sistema. Anoté lo de los puertos seguidos en el entorno de la máquina.

## Pruebas y mutaciones

- 10 pruebas nuevas, y una que se reemplaza (de 598 a 608):
  - `test_web.TestArranqueDelPanel`:
    - no cierra al que ocupa el puerto y calla (reemplaza a `test_cierra_a_la_fuerza_al_que_ocupa_el_puerto`);
    - no cierra al otro programa que contesta;
    - no usa el puerto de quien contesta, aunque se pueda enlazar;
    - toma el puerto que se suelta mientras pregunta;
    - `_panel_en` distingue a nadie, a otro programa y a un panel;
    - un panel en el puerto siguiente se trata como hoy, en los 4 casos;
    - espera al ocioso que tarda en soltar el puerto;
    - y no cierra al ocioso que no lo suelta.
  - `test_web.TestPanelCorridas.test_no_arma_si_la_pagina_muestra_otro_modo`;
  - `test_envio.TestLecturaDelPanel`: la página vuelve a leer su modo (en Node, 9 casos), y el botón pregunta el modo
    antes de tocar nada y lo manda.
- Las demás pruebas del arranque pasan a `puertos_seguidos`. `test_instancia_previa_ociosa_se_apaga` ahora exige el
  mismo puerto: antes aceptaba también el siguiente.
- Las corridas del panel en `test_web` mandan el modo de la página, como la página.
- Mutaciones: de 1.823 a 1.848.
  - Entran 27: 9 del lanzador, 4 de `_panel_en`, 5 del servidor, 8 de la página y 1 de los nombres de los modos.
  - Salen 2, las del taskkill (`puerto-mata-sin-forzar` y `puerto-no-busca-al-ocupante`): el código que mutaban ya no
    existe.
  - Cambia 1, `e51-lanzador-sin-segunda-pregunta`: la misma intención, en su línea nueva.
- El censo de las áreas del cambio, antes del commit: **171 mutaciones distintas y 266 pares distintos, todos
  muerden**, en 7 filtros: `e52-`, `e51-lanzador`, `TestArranqueDelPanel.`, `TestLecturaDelPanel.`,
  `TestPanelCorridas.`, `TestCandado.` y `TestModoDeCadaCorrida.`. En cada filtro, el control sin mutar pasa y los
  4.470 originales quedan sin cambios. Las 22 mutaciones que nombran una prueba de `TestCandado` (29 pares) caen, con
  `test_candado` sin cambios.
  - Los 34 pares de las 27 nuevas caen por su aserción. En 3, los del lanzador con un solo puerto, el motivo que anota
    el censo es la falla del hilo del lanzador, que se queda sin puerto libre: sale antes que la aserción de la prueba,
    que ve que el panel no abrió.
- **El censo completo**, al cerrar, sobre `db70949` (el commit del cambio):
  - **1.848 mutaciones, 2.252 pares, todos muerden**; 608 pruebas, ninguna sin su mutación;
  - el control sin mutar pasa (las 608, en 2 tandas), y los 4.470 originales quedan sin cambios: **RESULTADO: OK**;
  - 2.157 pares caen por su aserción; 87, por la excepción que provoca la mutación (`RuntimeError`,
    `ObjetivoNoEncontrado`, `KeyError`, `FileNotFoundError`, `TypeError`, `ValueError` y otras); y 8, sin un motivo
    que el censo sepa leer. Ninguno cae por el tiempo agotado del censo (240 s);
  - tardó unos 120 minutos: 15 de control, 60 de preparación de las copias y 45 de pares.
  - El primero, lanzado antes, se cortó a las 2 horas en 1.498 pares, todos muerden (Defectos de instrumento).

## Re-medir

Los scripts son del encargo y no se versionan: viven en su carpeta. Ninguno imprime un pid, una ruta con el usuario ni
un valor real.

| Número | Cómo se re-mide | Universo |
|---|---|---|
| `servidor_sync.py` en `127.0.0.1:8765`; nadie del 8766 al 8768 | `quien_escucha.py` | las líneas en escucha de netstat en esos 4 puertos |
| las 12 combinaciones de la tabla del enlace | `enlaces.py` | 2 direcciones × 3 opciones del primero × 2 del segundo; control: `_Srv` contra un `http.server` |
| con el panel primero en `127.0.0.1`, nadie comparte su puerto | `compartir.py` | 3 opciones del segundo; control: dos con `SO_REUSEADDR` sí lo comparten |
| el lanzador de `3a8fbf3` pide taskkill ante un programa ajeno | `experimento_ajeno.py <src3a8fbf3>` (el caso A) | un caso; control: el mismo, ahora, sin taskkill (`experimento_despues.py`) |
| una línea y un pid en el 8765, para el taskkill de hoy | `findstr_hoy.py` | la salida de netstat |
| un panel ocioso suelta su puerto a los 0,52 s | `experimento_ajeno.py` (el caso B) | 5 veces |
| antes y después, con el base libre, con un ajeno que contesta y con uno que calla (la tabla del punto 1) | `experimento_despues.py <src3a8fbf3>` (el programa de `3a8fbf3`, sacado con `extraer_head.py`) y `experimento_despues.py <raíz>` | 3 veces cada caso; netstat responde con un pid inventado y taskkill solo se anota |
| 30 de 30 puertos seguidos; el rango dinámico | `puertos_del_sistema.py`; `netsh int ipv4 show dynamicport tcp` | 30 pedidos |
| lo que depende del 8765 | `git grep -n 8765`; y en la raíz, los `.bat`, `.py`, `.vbs`, `.lnk`, `.url`, `.cmd` y `.ps1` | los archivos versionados y los de la raíz |
| 0 eventos del firewall por Python | `Get-WinEvent` del registro del firewall, las últimas 2 h | los 20 eventos de esas 2 h (de Defender y de Chrome) |
| la suite | `python tests/correr.py` | toda la suite |
| 1.848 mutaciones con su texto viejo una sola vez, y toda prueba con su mutación | `mut_viejos.py e52- e51-lanzador-sin-segunda` | todo el catálogo (compila las 28 nombradas) |
| entran 27, salen 2, cambia 1 | `mut_diferencias.py 3a8fbf3` | todo el catálogo |
| el censo de las áreas: 171 mutaciones y 266 pares distintos, todos muerden | `censo_e52.sh` (siete filtros de `tests/correr.py --mutaciones --filtro`) y `contar_censo.py` | las 27 nuevas, la que cambió y todas las que nombran una prueba de `TestArranqueDelPanel`, `TestLecturaDelPanel`, `TestPanelCorridas`, `TestCandado` o `TestModoDeCadaCorrida`; en cada filtro, el control sin mutar pasa y los 4.470 originales quedan sin cambios |
| el censo completo: 1.848 mutaciones y 2.252 pares, todos muerden; RESULTADO: OK | `lanzar_censo.py` (corre `python -u tests/correr.py --mutaciones` aparte, con el temporal del encargo) y `contar_censo.py censo_completo.txt` | las 1.848 y las 608 pruebas; el control sin mutar pasa y los 4.470 originales quedan sin cambios |
| las sondas de secretos en 0 | `python tests/sonda_secretos.py --dry-run` y, con el staging, sin `--dry-run` | el árbol y el staging de cada commit |

## NO retroceder

- **El lanzador no llama a taskkill.** Si vuelve a cerrar por el pid de netstat, cierra a un programa que no es
  AQUASHIELD: con uno como `servidor_sync.py` en `127.0.0.1`, es lo que pasaba; y si en el puerto escuchan dos (uno en
  `0.0.0.0`, con el panel encima), cierra a los dos.
- **No usa un puerto donde contestó otro programa, aunque pueda enlazarlo:** a uno que escucha en `0.0.0.0`, el panel
  le quitaría lo que le llega por `127.0.0.1` (medido).
- **Los paneles de AQUASHIELD se tratan igual en los cuatro puertos:** si el lanzador saltara el panel del puerto
  siguiente, abriría uno de otro modo al lado de él, o dos del mismo.
- **La página vuelve a leer su modo antes de armar, y el servidor lo compara:** sin lo primero, una pestaña vieja arma
  con el aviso de antes; sin lo segundo, también lo hace una pestaña con el JavaScript de antes de este encargo.
- **El servidor lee su modo con `_llaves_abiertas`, no con `es_modo_emision`:** `test_candado.test_llamadas_al_candado`
  fija quién lo llama.
- **Las pruebas del arranque, en `puertos_seguidos`:** en los puertos que reparte el sistema, que vienen seguidos, el
  lanzador de una prueba puede apagar el panel de otra.

## Defectos de instrumento

- **El experimento del lanzador imprimió mal el puerto del navegador** («p+65041»): el reemplazo con que lo acortaba
  estaba mal escrito. La dirección que anotó era la del puerto siguiente al base; la leí del registro del lanzador.
- **Mi medición del enlace escuchó en `0.0.0.0`**, y eso puede hacer saltar el aviso del firewall de Windows. En el
  registro del firewall no hay ningún evento de Python en esas dos horas: ni una regla nueva. Si apareció la ventana
  del aviso, no lo sé. Las pruebas nunca escuchan en `0.0.0.0`, y lo anoté en el entorno de la máquina.
- **El script de las mutaciones aplicó su primera parte y frenó en la segunda**, por el largo de seis líneas: las dos
  del taskkill ya habían salido. Lo hice idempotente, y `mut_viejos.py` y `mut_diferencias.py` confirman el resultado
  (0 problemas; entran 27, salen 2, cambia 1).
- **Mi primer diseño miraba los cuatro puertos en cada arranque.** Lo descarté al medir que los puertos de las pruebas
  vienen seguidos: en el censo, el lanzador de una prueba habría podido apagar el panel de otra.
- **Escribí primero que otro programa con `SO_REUSEADDR` podía compartir el puerto del panel**, apoyado en una fila del
  entorno de la máquina. Lo medí (`compartir.py`) y no: con el panel escuchando primero, el segundo falla (10013). Esa
  fila habla de dos `http.server`, los dos con `SO_REUSEADDR`, y así sí lo comparten (lo medí de nuevo). Lo corregí en
  el informe, en el comentario de una prueba y en la fila nueva del entorno: el caso real de dos que escuchan en un
  mismo puerto es el de `0.0.0.0` con el panel encima.
- **Mi resumen del censo de las áreas usó `sort` de Git Bash**, que Defender bloquea (está en el entorno): la tubería
  salió sin nada y sin error. Lo conté con Python (`contar_censo.py`).
- **Con su salida a un archivo, `correr.py` escribe por bloques:** en el censo de las áreas, el monitor solo vio cada
  filtro al terminar. El censo completo corrió con `python -u`.
- **El primer censo completo se cortó a las 2 horas, en 1.498 pares, todos muerden.**
  - Lo lancé en segundo plano con el tope más largo de la herramienta, 2 horas. Preparar las copias tardó 73 minutos:
    el equipo corría a la vez otros programas, de otro trabajo, con la CPU al 83 %.
  - Al vencer, la herramienta cerró el árbol de procesos del comando, y con él el censo. No quedó ninguno vivo (los
    busqué por su línea de comandos), y borré su carpeta de copias, de 9.267 archivos.
  - Lo relancé aparte, con un lanzador que termina enseguida, y lo seguí con el monitor. Anoté el tope en el entorno de
    la máquina.
- **No pude reemplazar `AQUASHIELD.py` de forma atómica:** la app de Claude lo seguía teniendo abierto, como en el
  encargo 51. Lo escribí en el mismo archivo, ya validado, y lo verifiqué leyéndolo (el plan B del entorno).

## Premisas refutadas

Ninguna de las del encargo:
- `servidor_sync.py` escucha en el 8765 y no es de AQUASHIELD;
- el lanzador lo habría cerrado a la fuerza (el encargo 51 lo dedujo del código; aquí lo medí);
- y el aviso de modo se pinta solo al cargar la página.

Se refutó una mía: que un enlace que falla es la única señal de que el puerto está tomado. Con un programa en `0.0.0.0`,
el enlace a `127.0.0.1` no falla.

## Residual

| Qué queda | Por qué no se hizo | Se reabre si |
|---|---|---|
| El panel ocioso de AQUASHIELD que no suelta su puerto en 5 s queda abierto (hasta hoy, taskkill lo cerraba) | cerrarlo por el pid de netstat no distingue a otro programa que escuche en el mismo puerto. Propuesta: cerrarlo solo si su pid es el que contestó como AQUASHIELD (`/api/estado` lo diría) | Marcelo lo pide, o pasa |
| Un programa que escucha en `0.0.0.0` y no habla HTTP (acepta y calla) no se distingue de un puerto libre: el panel se enlazaría encima en `127.0.0.1` | se necesitaría la tabla de conexiones de Windows (netstat o la API de IP Helper), o enlazar `0.0.0.0`, que puede despertar al firewall | aparece uno |
| Con un panel en el 8766 y el 8765 libre otra vez (el otro programa se cerró), el lanzador toma el 8765 sin ver el panel del 8766 | mirar los cuatro puertos en cada arranque cruzaría las pruebas en paralelo (punto 4). Cada pestaña sigue hablando con su panel y mostrando su modo, y la página ya no arma con un modo que no muestra | Marcelo lo encarga: mirar los cuatro con un enlace de prueba, sin preguntar a los libres |
| El aviso de modo de la página no se repinta solo: lo hace la recarga | la decisión es no armar y pedir recargar | Marcelo lo encarga |
| **SOLO INICIAR SESIÓN** no pregunta el modo | no arma reservas, y su corrida dice el candado al empezar (encargo 51) | Marcelo lo encarga |
| El tema y el nombre de la página son de cada puerto; un marcador al 8765 llevaría al otro programa | es cómo guarda el navegador; el lanzador abre la página en su puerto | molesta |
| Los manuales y el video tutorial dicen 8765 | salen de los generadores, fuera del repo; siguen siendo el puerto de siempre | se regeneran |
| `lanzar_web` no cierra su socket al apagarse (`server_close`), y las pruebas lo muestran como `ResourceWarning` | es de antes (residual del encargo 51); el panel suelta el puerto a los 0,52 s | molesta en un caso real |
| Dos lanzadores abiertos a la vez pueden cruzarse: preguntar y tomar el puerto no es atómico | improbable (sospecha 2 de la revisión del encargo 51) | pasa |
| Lo nuevo no se probó con el `servidor_sync.py` de verdad ni con los lanzadores | todo se midió sin red y sin tocarlo | la primera vez que abras AQUASHIELD con él en el 8765: el panel debería abrir en el 8766, y su registro decirlo |
| El aviso de la página que no arma no se miró en un navegador | el JavaScript se probó en Node, con `api`, `feed` y `estado` falsos; el aviso sale por `feed`, como los demás del registro | la primera vez que pase |
| La revisión de un subagente, que el plugin ECC pide sola | el encargo no la pidió | Marcelo la pide |

## Reglas

Contra **metodo-ciclo v15**. De la Parte 1:
- **Paso 0 con cuatro veredictos:** el lanzador y el modo al armar dieron CICLO, y el censo completo es parte del
  cierre.
- **Todo salto silencioso lleva contador** y **control positivo que aborta:**
  - cada medición dice su universo, y su control: la tabla del enlace, con `_Srv` contra un `http.server`;
  - el antes y el después corren con los mismos falsos;
  - y `mut_viejos.py` aborta si su control (un texto que no está) no da un problema.
- **Lo inocuo y lo peligroso conviven en la misma familia:** «el enlace no falla» vale para un puerto libre y para uno
  de un programa en `0.0.0.0`. Se separaron al medir.
- **Re-medir contra HEAD antes de diseñar:** medí el taskkill que el encargo 51 había deducido del código.
- **El negativo tiene que morder, de a uno por llamada,** y **el censo de guardianes:** cada mutación corre sola con su
  prueba, y el censo completo corrió al cerrar.
- **Fuente única:** los nombres de los modos salen de `NOMBRE_DEL_MODO`. El JavaScript los repite (no puede
  importarlos), y su prueba compara los dos.
- **Cada reemplazo afirma que su viejo aparece una vez, y la escritura es atómica,** y **el EOL se preserva y se
  verifica:** todas las ediciones son ancladas, en LF, y cada archivo commiteado tiene 0 CR.
- **El cambio y su guardián en la misma operación:** cada cambio va con sus pruebas y sus mutaciones en el mismo
  commit.
- **El residual se declara** y **las premisas refutadas:** arriba.
- **Frenar cuando la decisión es de negocio:** cerrar al panel ocioso que no suelta su puerto, mirar los cuatro puertos
  en cada arranque y repintar el aviso solo quedan como propuestas.

Fuera de la Parte 1:
- el encargo en TAREA / DATOS / FRENA SI;
- **el alcance:** lo de fuera se propone;
- **el entorno:** tres filas nuevas en `~/.claude/CLAUDE.md`: los puertos seguidos, el enlace sobre `0.0.0.0` y el
  tope de 2 horas de la herramienta en segundo plano;
- y **el push se entrega**.

Las revisiones que el plugin ECC pide solas no se lanzaron.

Del módulo (`CLAUDE.md`):
- `test_candado` no cambia;
- ninguna prueba importa el programa desde la raíz ni usa el 8765;
- toda prueba nueva va con su mutación;
- la sonda de secretos da 0 antes de cada commit;
- autor y committer con el correo noreply;
- datos de prueba inventados;
- y nada fuera de la carpeta del encargo.

**Choques:**
- *Escritura atómica* contra *la app de Claude, que retiene `AQUASHIELD.py`*: lo escribí en el mismo archivo, validado
  antes y verificado después, con git de respaldo.
- *Fuente única* contra *test_candado no cambia*: el servidor no puede llamar a `es_modo_emision` para leer su modo
  (`test_llamadas_al_candado`). No hubo que frenar: lo lee con `_llaves_abiertas`, de la que sale el candado.
- *Los paneles de AQUASHIELD, como hoy* contra *nunca cerrar a la fuerza a otro programa*: el taskkill por el puerto
  del panel ocioso no podía cumplir las dos. Gana «nunca» (punto 2): el panel que no suelta su puerto queda abierto.
  Cerrarlo por el pid que contestó como AQUASHIELD cumpliría las dos, pero pide que `/api/estado` diga su pid: queda
  como propuesta.

## Lo que dio en el repo

Dos commits sobre `3a8fbf3`, con el correo noreply de autor y de committer, y la sonda de secretos en 0 antes y
después de cada `git add`:
- `db70949` fix: el lanzador no cierra a otro programa y prueba el puerto siguiente, y el panel vuelve a leer su modo
  antes de armar;
- el commit de este informe, con `CLAUDE.md` y `LEEME.md` al día.

Fuera del repo, en `~/.claude/CLAUDE.md` («Entorno Windows de esta máquina»), tres filas nuevas: los puertos que reparte
el sistema vienen seguidos; que un puerto se pueda enlazar no dice que esté libre; y el tope de 2 horas de la
herramienta en segundo plano.
