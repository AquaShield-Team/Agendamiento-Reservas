# Encargo 51 · El modo de cada corrida, los lanzadores, un solo rescate en el login de MSC y las URL sin su consulta

Base: `C:\dev\Agendamiento Reservas` @ `aba1233` · árbol limpio.

## En resumen

- **Hasta hoy, el lanzador de prueba sí podía conectarse a un panel abierto en modo emisión** (va primero, como
  pediste).
  Pasaba cuando ese panel estaba armando reservas: el lanzador lo abría en el navegador y no levantaba el suyo. Y con
  un panel del otro modo ocioso, le pedía que se apagara y tomaba su puerto: una pestaña suya que quedara abierta
  seguía hablando con el panel nuevo, del otro modo, con el aviso de modo de antes. Lo medí sin red en los 8 casos
  (abajo). **Desde este encargo, un lanzador que encuentra un panel en el otro modo avisa en una ventana y no corre.**
- **La emisión de CMA-CGM que repetiste hoy no está en este equipo.** La corrida más reciente de `logs/` sigue siendo
  la del 02-10 a las 18:52, la del encargo 50. Desde el 02-10 a las 18:54 no hay una carpeta nueva en `logs/`, nadie
  subió una planilla al panel y el navegador del programa no se abrió. No hay una confirmación de CMA-CGM que medir:
  `FORMA_BOOKING` no cambió.
- **Cada corrida dice al empezar con qué candado corre y por cuál llave**, en `log.txt` y en el registro del panel.
- **MSC tiene un solo camino de rescate**: ante cualquier error del inicio de sesión que no se resuelva, un solo
  intento más desde el principio, nunca un tercero, y la clave a lo más dos veces en total.
- **La línea «URL:» de `log.txt` va sin la consulta en las seis navieras.** Los `log.txt` ya guardados no se tocaron.
- **Ningún FRENA SI se cumplió**: CMA-CGM no emitió ninguna reserva, `test_candado` no cambió y pasa, y el rescate de
  MSC escribe la clave a lo más dos veces (una prueba recorre las 85 formas en que pueden terminar los dos intentos).
- **La revisión del subagente**, en un clon dentro de la carpeta del encargo: aprobado con observaciones, sin hallazgos
  de severidad alta. Arreglé los dos medios y los bajos que eran de pocas líneas, entre ellos uno grave en su efecto:
  el lanzador todavía podía cerrar a la fuerza un panel del otro modo que tardara en contestar (punto 6).

## 1. El lanzador con un panel abierto en el otro modo

### Lo que hacía hasta hoy (medido)

`lanzar_web` miraba solo su puerto base (8765). Si ahí respondía un panel de AQUASHIELD, hacía lo mismo sin importar
su modo: si estaba ocupado, abría ese panel en el navegador y terminaba; si estaba ocioso, le pedía que se apagara
(`/api/apagar`) y levantaba el suyo en ese puerto.

Lo medí sin red y sin efectos reales (`experimento_lanzador.py`). El panel abierto era un proceso con una copia del
programa de `aba1233` en una carpeta aislada, con su modo puesto a mano: su función del candado devolvía verdadero o
falso, y no se abrió ninguna llave. El lanzador era otra copia, en el mismo modo o en el otro. El navegador no se abrió
(se anotó qué dirección abriría), y netstat y taskkill no corrieron. Puerto libre elegido por el sistema, nunca el
8765. Universo: los 8 casos (panel en prueba o en emisión, ocioso u ocupado; lanzador en el mismo modo o en el otro).

| Panel abierto | Lanzador | Antes (`aba1233`) | Ahora |
|---|---|---|---|
| prueba, ocioso | emisión | lo apaga y toma su puerto: el puerto pasa a responder en **modo EMISIÓN** | avisa y no corre; el panel sigue en prueba |
| prueba, ocupado | emisión | **abre el panel de prueba** en el navegador y no levanta el suyo | avisa y no corre |
| emisión, ocioso | prueba | lo apaga y toma su puerto: el puerto pasa a responder en modo prueba | avisa y no corre; el panel sigue en emisión |
| emisión, ocupado | prueba | **abre el panel de emisión** en el navegador y no levanta el suyo | avisa y no corre |
| prueba, ocioso | prueba | lo apaga y toma su puerto | igual |
| prueba, ocupado | prueba | lo abre en el navegador | igual |
| emisión, ocioso | emisión | lo apaga y toma su puerto | igual |
| emisión, ocupado | emisión | lo abre en el navegador | igual |

Dos de los casos son peligrosos:
- **Lanzador de prueba con un panel de emisión ocupado:** lo abre. La pestaña nueva pinta el aviso de modo emisión,
  porque lo lee al cargar, pero quien abrió el lanzador de prueba cree estar en modo prueba.
- **Lanzador de emisión con un panel de prueba ocioso:** lo apaga y toma su puerto. Si la pestaña del panel de prueba
  seguía abierta, su aviso dice «Modo Seguro», pero ahora habla con un panel que emite. Según el código del panel, que
  le pide todo a su mismo puerto, bastaba volver a subir la planilla en esa pestaña y armar las reservas para emitir
  creyendo que era una prueba (esto último no lo medí).

### Lo que explica la corrida del 02-10

La corrida de CMA-CGM de las 18:52 del 02-10 corrió en modo prueba (encargo 50). La planilla se subió al panel a las
18:52:29, siete segundos antes de que empezara. De los 8 casos medidos, el único en que un lanzador de emisión abierto
con el panel de prueba vivo termina en una corrida de prueba es el del **panel de prueba ocupado**: el lanzador abre
ese panel y no levanta el suyo. Con el panel de prueba ocioso, el lanzador de emisión lo habría apagado, y la planilla
subida a las 18:52:29 habría ido a un panel que emite. Quedan dos caminos que no medí: que el panel de prueba no
alcanzara a responder en 1 s y no se pudiera cerrar (el lanzador de emisión habría abierto el suyo en el 8766, y la
pestaña vieja seguiría en el de prueba), o que el lanzador de emisión no llegara a abrir su panel. Qué lanzador se
abrió ese día, y cuándo, no queda en ninguna parte.

### El cambio

`lanzar_web` pregunta antes el modo del panel que encuentra en su puerto (`_panel_en`: su `/api/estado` y el
`modo_emision` de su `/api/config`, el mismo con que el panel pinta su aviso). Si está en el otro modo, o no dice en
cuál (su `/api/config` falla, o no trae un `true` o un `false`), **avisa y no corre**: no se conecta a ese panel, no lo
cierra y no abre otro. En el mismo modo, todo sigue como antes.

El aviso va a la consola y a una ventana, como el de `main()` cuando el panel web no abre: los `.bat` lanzan con
`pythonw`, sin consola. Dice en qué modo está el panel abierto, en qué modo lo abriría este lanzador y cómo cerrarlo.
Por ejemplo:

> Ya hay un panel de AQUASHIELD abierto en modo prueba (sin emitir), en http://127.0.0.1:8765/, y este lanzador lo
> abriría en modo EMISIÓN (reservas reales). Para no mezclar los modos, no me conecto a ese panel, no lo cierro y no
> abro otro. Ciérralo con su botón rojo de apagar, arriba a la derecha, o cerrando su pestaña y esperando unos dos
> minutos, y vuelve a abrir este lanzador.

Si el panel abierto tiene una corrida en curso (de reservas o de solo login), el aviso dice además que espere a que
termine: su botón de apagar cortaría la corrida, y el vigilante de inactividad no lo apaga mientras corre.

**Un panel que tarda en contestar tampoco se cierra** (lo encontró la revisión del subagente, punto 6). Si el panel del
otro modo no alcanzaba a contestar en 1 s (con la máquina cargada), el lanzador no lo reconocía, no podía tomar el
puerto y caía al camino de siempre: cerrar a la fuerza (`taskkill /F`) a quien lo tenía. Ahora, si el puerto sigue
ocupado y al arrancar nadie contestó como AQUASHIELD, antes de cerrar a quien lo tiene le vuelve a preguntar, hasta
`PANEL_ESPERA_LARGA` s (5; hipótesis, no medido cuánto tarda un panel así). Si contesta, decide igual que al arrancar
(`_ceder_al_previo`); si tampoco contesta, sigue como siempre (residual). Esa segunda pregunta solo pasa con el puerto
ocupado: con el puerto libre, el lanzador no espera nada más.

Medido después del cambio, con el mismo experimento: en los 4 casos del otro modo, un solo aviso; el lanzador no
levantó su servidor, no abrió el navegador, no llamó a netstat ni a taskkill, y el panel abierto siguió vivo, en su
modo y con su estado. En los 4 del mismo modo, lo mismo que antes. `test_candado` no cambió: el lanzador consulta el
candado dentro de `lanzar_web`, que ya estaba entre las funciones que lo consultan.

## 2. La emisión de CMA-CGM de hoy

No hay una corrida de hoy en `logs/` de esta carpeta, que es la única copia del programa en este equipo. Lo medido
(solo fechas de modificación y nombres, sin abrir ningún archivo de datos):

- `logs/`: 1.920 archivos en 34 carpetas de corrida; desde el 2026-10-03, 0. Los más nuevos son del 02-10 a las
  18:54:12.
- La planilla que el panel guarda al subirla (`aquashield_planilla.xlsx`, en el temporal de Windows) es del 02-10 a
  las 18:52:29. Una corrida del panel necesita subir la planilla: hoy no se subió ninguna.
- El historial del perfil del programa (`perfiles/`, el Chrome con que corre) es del 02-10 a las 18:54:12: el
  navegador del programa no se abrió desde entonces.
- Copias del programa: busqué `AQUASHIELD.py` y `AQUASHIELD_EMISION.py` en `C:\dev` (sin entrar a `_SECRETOS`), en el
  Escritorio, en Documentos, en Descargas y en OneDrive, hasta 4 niveles: hay una sola, esta.
- La fecha de la última ejecución de `pythonw` (Prefetch de Windows) no se puede leer sin permisos de administrador: no
  sé si hoy se abrió un lanzador.

Así que **no emitió**, y no puedo decir por qué no corrió: o se hizo en otro equipo, o el panel no llegó a armar la
reserva. No hay confirmación que medir, y `FORMA_BOOKING` sigue sin CMA-CGM: su mejor estado sigue siendo «ENVIADA –
REVISAR EN PORTAL». La próxima emisión dejará al empezar, en su `log.txt`, con qué candado corrió (punto 3), y con un
panel de prueba abierto el lanzador de emisión ya no se conecta a él.

## 3. Cada corrida dice con qué candado corre

Al empezar, justo después de su línea de INICIO, cada corrida anota en `log.txt` y en su pantalla una de estas dos
líneas (`_anotar_candado`):

- `🛡️ Candado de emisión cerrado: modo prueba, sin ninguna de sus tres llaves abierta (la variable AQUASHIELD_EMITIR,
  un argumento emitir o produccion, y emitir_reservas en config.json). Cada reserva se detiene antes del botón final,
  sin emitir.`
- `🔴 Candado de emisión abierto: modo EMISIÓN, por <llaves>. Cada reserva que llegue al botón final se envía a la
  naviera.` Cada llave se dice así: «la variable AQUASHIELD_EMITIR=1 (la que pone el lanzador de emisión,
  AQUASHIELD_EMISION.py)», «el argumento «--emitir» del programa» o «config.json → opciones → emitir_reservas: true»; si
  hay más de una, todas, unidas por «y».

Va en las tres corridas: las de reservas del panel (`_web_worker`), las de la consola (`ejecutar_reservas`) y las de
solo login (`ejecutar_login`, también desde el panel). La de solo login no emite, pero es el mismo programa, en el mismo
modo.

**Una sola regla.** `test_candado.test_llamadas_al_candado` fija quién llama a `es_modo_emision`: los reservadores y el
panel. Si la línea de la corrida lo llamara, esa prueba cambiaría, y eso es un FRENA SI. Por eso las llaves las mira
una función nueva, `_llaves_abiertas`, y `es_modo_emision` pasó a ser `bool(_llaves_abiertas())`: la misma regla, en
el mismo orden, y se detiene en la primera llave abierta, como siempre (con otra llave abierta, no lee config.json ni
avisa de su valor). La línea de la corrida mira las tres (`todas=True`), pero de un valor inválido de config.json avisa
solo si ninguna otra llave abrió el candado, como el candado. Con otra llave abierta, el aviso («Lo dejé cerrado: no se
emite ninguna reserva») quedaba justo encima de «modo EMISIÓN» (lo encontró la revisión). Así no hay dos copias de la
regla.
- `test_candado` no cambió y pasa: el candado se comporta igual.
- Sus 6 mutaciones que tocaban el cuerpo de `es_modo_emision` se reescribieron sobre el código nuevo, con la misma
  intención y las mismas pruebas de `test_candado` y `test_arnes`; el censo dice si siguen cayendo (abajo).
- `test_modo.test_el_candado_sale_de_las_llaves` vigila que `es_modo_emision` no mire una llave por su cuenta, y
  `test_cada_llave_dicha_y_el_mismo_candado` recorre 64 combinaciones de las tres llaves: lo dicho y el candado
  coinciden en todas.

## 4. MSC: un solo camino de rescate

Ante cualquier error del portal en el inicio de sesión que no se resuelva, el login hace un solo intento más, completo
y desde el principio, y nunca un tercero (`MSC_INTENTOS`, 2). Los errores son tres (`MSC_ERRORES`):

| Dónde aparece el error | Antes de este encargo | Ahora |
|---|---|---|
| al abrir la portada | no reintentaba | un intento más |
| tras el «Next»: el 502 de TriggerOidcLogin, o el de la vuelta a myMSC que llega justo tras el «Next», sin pedir la clave | recargaba una vez (encargo 47) y, si seguía el error, no reintentaba | recarga igual; si la recarga no trae el campo de la clave ni la sesión, un intento más |
| tras el «Next», y la recarga trae de vuelta el campo del usuario | no reintentaba | un intento más |
| después de la clave, al pulsar el botón de entrar | un intento más (encargo 50) | igual |
| no llega ni la sesión ni el error (la clave equivocada, por ejemplo) | no reintentaba | igual: no es un error del portal |

**La clave se escribe a lo más dos veces en total**: una por intento, y a lo más dos intentos.
`test_la_clave_a_lo_mas_dos_veces` lo comprueba en las 85 combinaciones de cómo pueden terminar los intentos. Hay 13
formas de terminar un intento; las 7 que no son un error no reintentan, y las 6 que sí, con cada una de las 13 en el
segundo intento: 7 + 6 × 13 = 85. En todas, la prueba cuenta cuántas veces se abre myMSC y cuántas se escribe la
clave, si queda la sesión y, si no, el motivo.

Si el segundo intento también falla, las filas de MSC quedan NO ENVIADA con un motivo que dice cómo terminó cada
intento, por ejemplo: «no quedó iniciada la sesión de MSC: el portal dio un error al abrir su portada, y el único
intento más, desde el principio, tampoco dejó la sesión (otro error al pulsar «Next», y su recarga no lo arregló). La
reserva no se envió (el detalle, en log.txt)». El login deja ese motivo ya antes del segundo intento: si el segundo se
corta (con «Detener», por ejemplo), el motivo dice «se cortó antes de terminar», y no «el inicio de sesión no se
reintentó», que era falso (lo encontró la revisión).

La recarga del encargo 47 sigue: es lo que resolvía el 502 de TriggerOidcLogin antes del encargo 45, sin volver a
escribir nada. El rescate empieza solo si la recarga no lo resuelve. Tampoco hay clics nuevos: el segundo intento repite
los del primero.

## 5. La línea «URL:» sin su consulta

`Registro.url`, que usan las seis navieras, escribe la dirección sin su consulta (lo que va desde «?») ni su fragmento
(desde «#»), y sin un usuario o una clave antes del servidor, y dice qué quitó: «URL: https://… (sin su consulta)». Lo
hace `_sin_consulta`, que reemplaza a `_msc_sin_consulta` y a `_msc_url`, del login de MSC (encargo 50). El fragmento va
también porque puede traer un token; en `logs/` no había ninguno. La otra línea con «URL:», la del avance de MAERSK,
igual.

Medido en los 34 `log.txt` de `logs/`, sin imprimir un solo valor (`urls_por_linea.py`, `urls_sensibles.py`):
- de las 255 líneas con una dirección, 237 son «URL:» y 18, el avance de MAERSK; no hay otras formas;
- de las 237, 104 traían consulta, y 58 un valor de la cuenta o de la sesión: 40, el usuario de COSCO (`login_hint`),
  y 18, el estado o el código del inicio de sesión de ONE (7 en www.one-line.com, con `code` y `state`, y 11 en
  auth.one-line.com, con `state` y `code_challenge`);
- ninguna traía fragmento, y las 18 de MAERSK no traían consulta.

Los `log.txt` ya guardados no se tocaron: esas 58 líneas siguen ahí. `test_toda_linea_url_va_sin_consulta` vigila que
ninguna línea con «URL:» escriba una dirección sin pasar por `_sin_consulta`.

**Una línea más, sin «URL:»** (lo encontró la revisión): cuando el asistente de ONE no llegaba a su última pantalla,
`reservar_one` escribía la dirección entera, con su consulta, en `log.txt` y en el motivo, que llega a la planilla. En
`logs/` no hay ninguna (0 de 34). Ahora ONE escribe de su dirección solo el paso del asistente, o la dirección sin su
consulta (`_one_paso_de_la_url`). `test_ninguna_direccion_con_su_consulta_a_un_mensaje` rastrea en todo el programa que
ninguna dirección llegue con su consulta a una línea de `log.txt` ni al motivo de una reserva, también a través de una
variable; su control positivo, una función inventada que lo hace, cae.

## 6. La revisión del subagente

Pedida por el encargo antes de cerrar el ciclo. Un subagente revisor trabajó en un clon de `main` dentro de la carpeta
del encargo, con sus temporales también ahí; no tocó el repo vivo. Revisó el commit `cb3f1c3` contra `aba1233`. La
primera vez se cortó sin entregar nada (10 minutos sin avanzar, probablemente esperando una corrida de pruebas mientras
el censo ocupaba la máquina); la segunda le pedí comprobar con scripts cortos, y entregó.

**Veredicto: aprobado con observaciones.** 0 hallazgos de severidad alta, 2 medios, 5 bajos y 6 sospechas. Lo que
comprobó sin encontrar nada:
- `es_modo_emision` da lo mismo que en `aba1233` en 4.480 combinaciones (20 valores de la variable × 14 argumentos ×
  16 estados de config.json), con las mismas lecturas de config.json y los mismos avisos;
- la clave de MSC, a lo más dos veces por cualquier camino, sin tercer intento, y sin reintento sin un error;
- el lanzador, en los casos que cubren las pruebas; y 0 voseos en lo agregado.

| # | Hallazgo | Severidad | Qué hice |
|---|---|---|---|
| 1 | El lanzador todavía podía cerrar a la fuerza un panel del otro modo que tardara más de 1 s en contestar | media | arreglado: la segunda pregunta, de hasta 5 s (punto 1); prueba nueva |
| 2 | Con otra llave abierta y config.json inválido, `log.txt` decía «no se emite ninguna reserva» justo encima de «modo EMISIÓN» | media | arreglado: ese aviso, solo sin otra llave abierta (punto 3) |
| 3 | `reservar_one` escribía la dirección entera en `log.txt` y en el motivo | baja | arreglado (punto 5), con el rastreo de todo el programa |
| 4 | El corte tras el argumento `--emitir` no tenía prueba que lo cuidara | baja | cubierto: la prueba cuenta las lecturas de config.json con la variable y con el argumento; dos mutaciones nuevas |
| 5 | Si el segundo intento de MSC se cortaba, el motivo decía «no se reintentó» | baja | arreglado (punto 4); prueba nueva |
| 6 | Casos borde de `_sin_consulta` | baja | IPv6: arreglado (los corchetes); un puerto inválido da «no pude leer la dirección» (seguro, se queda); `data:` y `;jsessionid` quedan como residual (0 de 255 direcciones en `logs/`); el aviso del lanzador decía «armando reservas» también con una corrida de solo login: ahora dice «una corrida en curso» |
| 7 | Calidad de las pruebas | baja | la línea de avance de MAERSK tiene ahora prueba de comportamiento; las pruebas del motivo de MSC en el panel y la consola usan un motivo ya armado; los paneles hijo de las pruebas se apagan por su botón en vez de matarlos, así borran su sandbox |
| S1 | El aviso de modo del panel se pinta solo al cargar la página: una pestaña que sobrevive a su panel puede quedar hablando con otro panel, del otro modo, en el mismo puerto | sospecha | propuesta (residual y «Decides tú») |
| S2 | Dos lanzadores abiertos a la vez | sospecha | residual: improbable |
| S3 | Si fallan a la vez la consola y la ventana, el lanzador no muestra nada (y no toca nada) | sospecha | residual |
| S4 | Con un panel del mismo modo ocupado cuyo `/api/config` falla, el lanzador ahora avisa en vez de abrirlo | sospecha | se queda: es lo seguro |
| S5 | La cabecera de cada HTML de evidencia trae la dirección entera de la página | sospecha | residual: es `logs/*.html`, no `log.txt` |
| S6 | El texto de una excepción de Playwright puede traer una dirección | sospecha | residual: 0 en `logs/` |

## Pruebas y mutaciones

- 18 pruebas nuevas y una que cambia de nombre (de 580 a 598):
  - `test_modo.py` (nuevo): las llaves, la regla única, el corte en la primera llave (con las lecturas de config.json
    contadas) y la línea de cada modo;
  - `test_web`: el lanzador ante un panel en el otro modo, uno que no dice el suyo, uno lento del otro modo, el mismo
    modo de emisión y el aviso en una ventana; y la línea del candado en una corrida del panel;
  - `test_consola`: la línea del candado en la consola y en el login; la línea «URL:» (con IPv6 y el avance de
    MAERSK); el paso de ONE; y el rastreo de las direcciones en los mensajes;
  - `test_clics`: `test_la_clave_a_lo_mas_dos_veces` y `test_segundo_intento_cortado_deja_su_motivo`, y
    `test_otros_errores_no_reintentan` pasa a `test_cualquier_error_un_solo_intento_mas`.
- Mutaciones: de 1.765 a 1.823. Entran 59 del encargo 51 (45 del cambio y 14 de la revisión); sale una, la del aviso
  del error antes de la clave, que ya no existe; y 25 cambian su texto o su prueba.
  - 21 cambian su texto, porque el código que mutan cambió de forma: las 6 del cuerpo del candado, las 2 del arranque
    del panel (el panel previo ocupado y el que busca al dueño del puerto), las 2 de la poda al empezar, las 2 de la
    recarga de MSC y 9 del encargo 50. Su intención es la misma.
  - Las que nombraban `test_otros_errores_no_reintentan` pasan a la prueba nueva, y a 4 se les suma una prueba nueva
    (`test_la_clave_a_lo_mas_dos_veces` o `test_url_sin_consulta`).
  - Primer censo, sobre `cb3f1c3`, de las siete áreas del cambio: **207 mutaciones distintas, todas muerden** (279
    pares mutación-prueba distintos). Entre ellas, las 6 del candado, que siguen cayendo con `test_candado` sin
    cambios. De las 81 parejas de las 45 nuevas, 78 caen por su aserción, y 3 por lo que provoca la mutación: en dos,
    el panel previo nunca se apaga y la espera de la prueba vence; en la otra, el aviso revienta con un modo que no es
    `true` ni `false`.
  - Segundo censo, sobre las correcciones de la revisión: **134 mutaciones distintas, todas muerden** (193 pares
    distintos), en las áreas que tocó la revisión. Las 14 nuevas caen por su aserción.
- El arnés (`soporte.py`): la ventana de aviso de tkinter es una trampa. Sin ella, una mutación que hiciera avisar al
  lanzador abriría una ventana de verdad y dejaría la prueba esperando un clic.

## Re-medir

Los scripts de medición son del encargo y no se versionan (viven en su carpeta). Ninguno imprime un valor real: solo
fechas, conteos, nombres de parámetros o estados.

| Número | Cómo se re-mide | Universo |
|---|---|---|
| ninguna corrida desde el 02-10 a las 18:54 | `corridas.py 20261002` y `recientes.py 20261003`: las carpetas de `logs/`, la fecha de la planilla del panel y la del historial del perfil | las 34 carpetas de corrida de `logs/` (0 que no calcen con el patrón) y sus 1.920 archivos |
| una sola copia del programa | `otras_copias.py`: `AQUASHIELD.py` o `AQUASHIELD_EMISION.py` en `C:\dev` (sin `_SECRETOS`), el Escritorio, Documentos, Descargas y OneDrive, hasta 4 niveles | control: encuentra esta copia |
| los 8 casos del lanzador, antes y después | `experimento_lanzador.py <srcaba>` (el programa de `aba1233`) y `experimento_lanzador.py <raíz>` | 8 casos; control: los 4 del mismo modo dan lo que ya fijaban `test_instancia_previa_*` |
| 1 s por puerto cerrado | `puerto_cerrado.py` | 5 puertos libres |
| 237 líneas «URL:», 104 con consulta, 58 con un valor de la cuenta o de la sesión | `urls_por_linea.py` y `urls_sensibles.py` | los 34 `log.txt` de `logs/`; 0 sin leer |
| 0 líneas «URL dice» de ONE | `url_dice.py` | los mismos 34 |
| quién tenía abierto `AQUASHIELD.py` | `quien_lo_tiene.py <ruta>` (Administrador de reinicio de Windows) | el archivo |
| la suite: 594 pruebas, OK, 697 s, sobre `cb3f1c3`; y 598, OK, 369 s, después de la revisión; las dos veces, 4.469 originales y 0 cambios | `python tests/correr.py` | toda la suite |
| 1.823 mutaciones con su texto viejo una sola vez, y toda prueba con su mutación | `mut_viejos.py e51- e50-msc config- previa- puerto-` | todo el catálogo (compila las 126 nombradas) |
| entran 59, sale 1, cambian 25 | `mut_diferencias.py aba1233` | todo el catálogo |
| el primer censo: 207 mutaciones distintas, 279 pares distintos, todos muerden | `censo_e51.sh` (siete filtros de `tests/correr.py --mutaciones --filtro`: `e51-`, `TestMsc.`, `TestCandado.`, `TestArnes.`, `TestArranqueDelPanel.`, `poda-no-corre` y `TestUtilitarios.`), sobre `cb3f1c3` | las 45 nuevas, las 24 que cambiaron hasta ahí y todas las que nombran una prueba de esas clases; en cada filtro, el control sin mutar pasa y los 4.469 originales quedan sin cambios |
| el segundo censo: 134 mutaciones distintas, 193 pares distintos, todos muerden | `ronda2.sh` (la suite y cinco filtros: `e51-`, `e50-msc`, `TestCandado.`, `TestArranqueDelPanel.` y `TestUtilitarios.`), después de la revisión | las 59 del encargo, las del login de MSC del encargo 50 y todas las que nombran una prueba de esas clases; en cada filtro, el control sin mutar pasa y los 4.469 originales quedan sin cambios |
| las sondas de secretos en 0 | `python tests/sonda_secretos.py --dry-run` y, con el staging, sin `--dry-run` | el árbol y el staging de cada commit |

## NO retroceder

- **El lanzador no se conecta a un panel del otro modo, ni lo cierra:** volver a cerrarlo, o a abrirlo en el navegador,
  deja otra vez una pestaña con el aviso de un modo hablando con un panel del otro (medido arriba).
- **`es_modo_emision` es `bool(_llaves_abiertas())`:** si el candado vuelve a mirar las llaves por su cuenta, la línea
  de cada corrida puede decir un modo y la guarda usar otro.
- **La línea de la corrida no llama a `es_modo_emision`:** `test_candado.test_llamadas_al_candado` lo fija.
- **La clave de MSC, a lo más dos veces:** un tercer intento, o un rescate que vuelva a escribirla en el mismo intento,
  arriesga la cuenta.
- **Sin un error del portal, MSC no reintenta:** puede ser la clave equivocada.
- **La segunda pregunta antes de cerrar a quien tiene el puerto:** sin ella, un panel del otro modo que tarda en
  contestar se cierra a la fuerza, y con él su corrida.
- **Del config.json inválido, la línea de la corrida avisa solo sin otra llave abierta:** con otra llave abierta, el
  aviso dice «no se emite ninguna reserva» y la corrida emite.
- **Ninguna dirección con su consulta en un mensaje** (`_sin_consulta`, `_one_paso_de_la_url`): la consulta trae el
  usuario o el código del inicio de sesión, y el motivo llega a la planilla.

## Defectos de instrumento

- **El encargo 50 contó 7 líneas de ONE con un valor de la sesión; son 18.** Contó solo las de www.one-line.com, con
  `code` y `state`, y no vio las 11 de auth.one-line.com, con `state` y `code_challenge`. Re-medido aquí por parámetro y
  por servidor (`urls_sensibles.py`). CLAUDE.md queda con 18.
- **Las pruebas del login de MSC podían leer el `log.txt` de otra prueba** (del encargo 50, visto aquí).
  - `login_falso` numeraba sus corridas con un contador que volvía a 1 en cada prueba, y la sandbox es de la clase, así
    que la corrida 3 de una prueba escribía en el mismo `log.txt` que la corrida 3 de otra.
  - Un `assertIn` podía encontrar la línea de otra prueba, y un `assertNotIn` caer por ella: así cayó una prueba del
    encargo 50 cuando la nueva, por orden alfabético, corrió antes que ella.
  - Desde este encargo, el contador es de la clase, y cada login falso escribe en su propia carpeta.
- **La prueba nueva del login por consola chocaba en el mismo segundo con otra.** Usaba el mismo operador que
  `test_login_por_consola`, que pide su carpeta sin «_2». Pasó a usar el operador sin credenciales.
- **El chequeo de las líneas de más de 120 columnas no miraba los bloques grandes** que el script de las pruebas pone de
  una vez (`reemplazar_tramo`, `anexar`): cuatro líneas largas pasaron hasta que lo agregué.
- **La herramienta Bash convierte `\\` en `\` también dentro de un heredoc** (ya anotado en el entorno): una corrección
  hecha así no calzó, y la hice con el editor.
- **Mis pruebas del candado no cuidaban el corte tras el argumento `--emitir`**, ni el aviso de config.json con otra
  llave abierta: los encontró la revisión, con una mutación suya que pasaba 11 de 11 pruebas. Ahora la prueba cuenta
  las lecturas de config.json.
- **La primera revisión del subagente se cortó sin entregar nada** (10 minutos sin avanzar). Lo más probable es que
  esperara una corrida de pruebas larga mientras el censo ocupaba la máquina. La relancé pidiéndole comprobar con
  scripts cortos.
- **No pude reemplazar `AQUASHIELD.py` de forma atómica, las dos veces que lo cambié:** la app de Claude lo tenía
  abierto sin dejar reemplazarlo, la primera vez durante más de 2 minutos (lo nombró el Administrador de reinicio de
  Windows). Lo escribí en el mismo archivo, ya validado, y lo verifiqué: las dos veces quedó idéntico, byte a byte, a la
  copia que pasó las pruebas. Anotado en el entorno de la máquina.

## Premisas refutadas

- «Marcelo repitió hoy la emisión (la corrida más reciente en logs/)»: la más reciente sigue siendo la del 02-10, y en
  este equipo no hay rastro de una corrida de hoy.

## Residual

| Qué queda | Por qué no se hizo | Se reabre si |
|---|---|---|
| La forma del número de CMA-CGM (`FORMA_BOOKING`) | no hubo una emisión que medir | hay una corrida de CMA-CGM con el candado abierto: su `log.txt` lo dirá al empezar |
| **El lanzador cierra a la fuerza (`taskkill /F`) a cualquier programa que escuche en el 8765 y no conteste como AQUASHIELD**, después de preguntarle dos veces (1 s y 5 s). Hoy hay uno: otro programa, que no es de AQUASHIELD, escucha ahí desde esta tarde; según el código, si abres AQUASHIELD ahora, el lanzador lo cierra (no lo probé: no es nuestro). También cerraría un panel de AQUASHIELD que no contestara en 5 s | es otro frente (propuesta): que el lanzador no cierre un proceso que no contesta como AQUASHIELD y use el puerto siguiente | Marcelo lo encarga |
| El lanzador solo mira el 8765: no ve un panel en 8766–8768 | preguntarle a cada puerto cerrado cuesta 1 s; el lanzador solo se conecta al 8765 | aparece un caso con dos paneles a la vez |
| **Una pestaña que sobrevive a su panel** (se cerró solo, se cayó o lo cerraron) sigue preguntando a su puerto: si después se abre ahí un panel del otro modo, su aviso de modo es el de antes, y desde ella se puede armar reservas. El lanzador ya no provoca ese relevo, pero puede pasar de otras formas (sospecha 1 de la revisión) | el aviso se pinta al cargar la página (`/api/config`); cambiarlo es otro frente (propuesta: que `/api/estado` diga el modo, o una marca de cada panel, y que la pestaña se recargue o avise si cambia). La línea del candado de cada corrida ya dice el modo real | Marcelo lo encarga |
| MSC: sin un error del portal (no llega ni la sesión ni el error) no reintenta | puede ser la clave equivocada: reintentar sería otro intento fallido | Marcelo decide reintentar también ahí (la clave seguiría a lo más dos veces) |
| `_sin_consulta` deja el contenido de una dirección `data:` y los parámetros de ruta (`;jsessionid=…`) | 0 de 255 direcciones en `logs/` traen uno u otro, y el programa no navega a `data:` | aparece una |
| Los 58 valores en los `log.txt` ya guardados | decisión de Marcelo: no se tocan | Marcelo decide limpiarlos |
| `lanzar_web` no cierra su socket al apagarse (`server_close`): las pruebas lo muestran como `ResourceWarning` | es de antes, y el proceso termina enseguida | molesta en un caso real |
| Lo nuevo no se probó en los portales ni con los lanzadores de verdad | todo se midió sin red | la primera corrida real: su `log.txt` dirá el candado; el lanzador, si encuentra un panel del otro modo, mostrará la ventana |
| Dos lanzadores abiertos a la vez pueden cruzarse: preguntar y tomar el puerto no es atómico, y el segundo puede cerrar al primero | improbable (sospecha 2 de la revisión) | pasa |
| Si fallan a la vez la consola y la ventana del aviso, el lanzador no muestra nada (y no toca nada) | con `pythonw`, la ventana es lo único visible; no está medido que falle | un doble clic que no hace nada |
| La cabecera de cada HTML de evidencia trae la dirección entera de la página y de cada marco | es `logs/*.html`, no `log.txt`, y queda fuera de la decisión de Marcelo (sospecha 5) | Marcelo lo encarga |
| El texto de una excepción de Playwright puede traer una dirección a `log.txt` («ERROR en login: …») | 0 en `logs/`: las 255 direcciones de los 34 `log.txt` son «URL:» o el avance de MAERSK (sospecha 6) | aparece una |
| El censo completo (1.823 mutaciones, más de una hora) | se corrieron los de las áreas del cambio, antes y después de la revisión | Marcelo lo pide, o el próximo cambio grande del candado |

## Reglas

Contra **metodo-ciclo v15**. De la Parte 1:
- **Paso 0 con cuatro veredictos:** la emisión de CMA-CGM dio NOTA (medido: no hubo corrida); el lanzador, el modo de
  cada corrida, MSC y las URL dieron CICLO.
- **Todo salto silencioso lleva contador** y **control positivo que aborta:** cada sonda dice su universo y lo que no
  pudo leer (0 en todas), y su control: el experimento del lanzador reproduce en el mismo modo lo que ya fijan
  `test_instancia_previa_*`; la búsqueda de copias encuentra esta; las sondas de `logs/` encuentran las 237 líneas
  «URL:» que el encargo 50 ya había visto.
- **Re-medir contra HEAD antes de diseñar:** re-medí las líneas «URL:» del encargo 50, y salieron 18 de ONE, no 7.
- **El negativo tiene que morder, de a uno por llamada** y **el censo de guardianes:** cada mutación corre sola, con su
  prueba; las 45 nuevas y las 24 que cambiaron entran en el censo.
- **Fuente única:** `es_modo_emision` sale de `_llaves_abiertas`, y `_sin_consulta` reemplaza a las dos funciones del
  login de MSC.
- **Cada reemplazo afirma que su viejo aparece una vez, y la escritura es atómica** y **el EOL se preserva y se
  verifica:** todas las ediciones son ancladas, en LF, y cada archivo commiteado tiene 0 CR.
- **El cambio y su guardián en la misma operación:** cada cambio va con sus pruebas y sus mutaciones en el mismo
  commit.
- **El residual se declara** y **las premisas refutadas:** arriba.
- **Frenar cuando la decisión es de negocio:** el cierre a la fuerza de otro programa en el 8765, el aviso de modo de
  una pestaña vieja y reintentar sin un error quedan como propuestas.

Fuera de la Parte 1: el encargo en TAREA / DATOS / FRENA SI; **el alcance** (lo de fuera se propone: de la revisión,
arreglé lo de pocas líneas ligado al encargo, y las sospechas que abren otro frente quedan como propuestas); **el
entorno** (dos filas nuevas en `~/.claude/CLAUDE.md`: la app de Claude que retiene un archivo, y el segundo que cuesta
un puerto cerrado); y **el push se entrega**. La revisión del subagente la pidió el encargo; las que el plugin ECC pide
solo, no se lanzaron.

Del módulo (`CLAUDE.md`): `test_candado` no cambia; ninguna prueba importa el programa desde la raíz ni usa el 8765;
toda prueba nueva con su mutación; la sonda de secretos, en 0 antes de cada commit; el correo noreply de autor y de
committer; datos de prueba inventados; nada fuera de la carpeta del encargo (temporales, clon del revisor).

**Choques:**
- *Escritura atómica* contra *la app de Claude reteniendo `AQUASHIELD.py`*: escribí en el mismo archivo, validado
  antes, verificado después byte a byte contra la copia que pasó las pruebas, con git de respaldo.
- *Fuente única* contra *test_candado no cambia*: `test_llamadas_al_candado` no deja que la línea de la corrida llame a
  `es_modo_emision`. No hubo que frenar: las llaves las mira `_llaves_abiertas`, y el candado sale de ella.
- *Nada fuera de la carpeta del encargo* contra *el entorno se anota en `~/.claude/CLAUDE.md`*: la regla de la carpeta
  es para los temporales, la memoria de Claude Code y los clones; las dos filas del entorno van donde el método dice.

## Lo que dio en el repo

Tres commits sobre `aba1233`, con el correo noreply de autor y de committer, y la sonda de secretos en 0 antes y
después de cada `git add`:
- `cb3f1c3` fix: cada corrida dice su candado, el lanzador no se conecta a un panel del otro modo, un solo rescate en
  el login de MSC y la línea «URL:» sin su consulta;
- `9b4eac0` fix: lo que encontró la revisión del encargo 51 (el lanzador ante un panel lento, el aviso de config.json,
  el paso de ONE y el motivo de MSC);
- el commit de este informe, con `CLAUDE.md` y `LEEME.md` al día.

Fuera del repo, en `~/.claude/CLAUDE.md` («Entorno Windows de esta máquina»), dos filas nuevas: la app de Claude que
retiene un archivo del repo, y el segundo que cuesta preguntarle a un puerto cerrado.
