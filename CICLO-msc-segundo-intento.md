# Encargo 50 · MSC hace un solo intento más y deja la evidencia del error; COSCO dice cuándo traduce el puerto; la emisión de CMA-CGM que no fue

**Base:** `C:\dev\Agendamiento Reservas` @ `20b5dcd` · árbol limpio.

Hecho con `metodo-ciclo` v15. No abrí ningún portal ni usé el lanzador de emisión. Lo que medí sobre lo guardado (en
`logs/`, en el historial del perfil del programa y en las planillas) va enmascarado: los informes no llevan valores de
clientes ni números de pedido.

## En resumen

- **CMA-CGM no emitió.** La corrida más reciente de `logs/`, la del 02-10 a las 18:52, solo con la fila de CMA-CGM, se
  detuvo en la guarda, «SIN emitir», igual que la de las 16:50. No se emitió ninguna reserva, no hubo número que
  capturar, y la fila quedó «lista para emitir». El proceso que la corrió no tenía abierta ninguna de las tres llaves
  del candado. Aun emitiendo, CMA-CGM no llega a EMITIDA: no tiene forma medida del número.
- **MSC, ante el error después de la clave:** sin la ida a eBooking, hace un solo intento más de inicio de sesión,
  completo y desde el principio, y nunca un tercero. La clave se escribe a lo más dos veces. Si el segundo también
  falla, cada fila de MSC queda NO ENVIADA con un motivo propio. Con cualquier otro error no reintenta, como hasta hoy.
  La recarga del encargo 47 sigue igual.
- **MSC, la evidencia:** el programa escucha la red de la página durante el inicio de sesión, sin clics. Cada error deja
  en `log.txt` la respuesta que lo trajo: la dirección sin parámetros, el código HTTP, el nombre de cada cabecera y el
  valor solo de las que nombran al servidor o a una protección contra robots. Deja también su captura y su HTML, salvo
  el HTML que traiga el usuario o la clave.
- **COSCO** sigue con `MAPA_PUERTOS_COSCO`, pero cuando el mapa cambia el puerto de la fila por otro, la pantalla,
  `log.txt` y el motivo dicen desde qué puerto se arma la reserva. Con tu cambio de la planilla, la fila de COSCO ya no se
  traduce.
- **El contexto de negocio** quedó en `CLAUDE.md`: la reserva solo asegura el espacio en la nave, y la agencia de aduana
  pone después el cliente, el peso y el producto.
- **Fuera del encargo, y lo decides tú:** la línea «URL:» que el programa ya escribía en `log.txt` guarda el usuario de
  COSCO en 40 líneas y el código de autorización de ONE en 7.

## FRENA SI, uno por uno

| Condición | Qué medí | Resultado |
|---|---|---|
| El intento extra obligaría a escribir la clave más de dos veces | Cada intento escribe la clave a lo más una vez (`rellenar`, sin reintento), y hay a lo más dos intentos (`MSC_INTENTOS`) | No frena. La prueba con los dos intentos fallidos cuenta 2 |
| Lo guardado muestra un aviso de bloqueo de la cuenta o de intentos fallidos | 1.189 líneas de `log.txt` en los inicios de sesión de MSC, 30 capturas `msc_*` por OCR y 367 títulos de páginas de MSC y b2clogin en el historial del perfil, con controles positivos | No frena: 0 avisos |
| La evidencia expondría en `log.txt` una cookie, un token o una credencial | La línea nueva va sin consulta ni usuario de la dirección, y solo con el valor de las cabeceras de una lista sin cookies ni identificadores. Probada con valores inventados | No frena. El HTML que repite el usuario no se guarda (abajo) |
| La corrida de CMA-CGM emitió más de una reserva | La corrida, sus archivos y el historial del perfil | No frena: no emitió ninguna |

## CMA-CGM: la corrida de las 18:52 no emitió

Es la corrida más reciente de `logs/`: `web_todas_…_20261002_185236`, de 18:52:36 a 18:54:12, con la hoja CONSOLIDADO y
una reserva, la fila de CMA-CGM. No hay carpetas posteriores (34 en `logs/`, 0 que no calcen con su patrón).

- **Se detuvo en la guarda.** La línea 67 de su `log.txt` dice «Me DETENGO en 'Envío de la reserva' antes de emitir (NO
  se pulsa Enviar el booking)», y la 68, «OK-EJEMPLO (CMA armada hasta Envío de la reserva…); SIN emitir».
- **No hay rastro de un envío.** De sus 55 archivos, el último es la guarda, a las 18:54:12. No hay ninguno de la
  confirmación (`cma_f7_6_confirmado`), que la rama de emisión deja siempre. El navegador se cerró al terminar
  (`ctx.close()`), y la última visita del perfil del programa es de las 18:53:10, en Click & Book; después, ninguna.
- **Paso por paso, fue igual que la corrida de prueba de las 16:50:** el mismo origen, el mismo POD y el mismo lugar de
  entrega; «Validar ruta» sin respuesta en 12 s; el contenedor, el peso, la mercancía, la nave y el panel Reefer; el
  comentario, «I Agree» y la guarda. Ningún paso se comportó distinto, porque las dos corrieron en modo prueba.
- **Dónde quedó anotada:** en el panel, la fila quedó «lista para emitir» (OK-EJEMPLO). Si descargaste la planilla, su
  Estado dice «OK-EJEMPLO · CMA armada hasta Envío de la reserva…; SIN emitir», y su N° de reserva, «lista para emitir».
  La planilla de la raíz no la escribe el panel: su última modificación es de las 18:51:40, antes de la corrida.
- **Por qué no emitió:** `es_modo_emision()` dio falso en la guarda. El lanzador de emisión pone `AQUASHIELD_EMITIR=1`
  antes de cargar el programa, y nada en el código la borra, así que esa corrida la hizo un proceso que no venía del
  lanzador de emisión. Cuál fue no se puede saber con lo guardado: `log.txt` no dice con qué candado corre, y el panel
  lo muestra solo al cargar la página (el aviso rojo «MODO EMISIÓN REAL ACTIVO» o el verde «Modo Seguro Activo»). Hoy
  no queda ningún proceso de AQUASHIELD vivo.
- **Aun emitiendo, no habría quedado EMITIDA:** CMA-CGM no tiene forma medida del número (`FORMA_BOOKING`), así que su
  mejor estado es «ENVIADA – REVISAR EN PORTAL», sin número en el panel ni en la planilla. La captura y el HTML de su
  confirmación servirían para medir esa forma.
- Si en el portal de CMA-CGM hay una reserva de esa tarde, no salió de esta corrida del programa. Confirmarlo exige
  abrir el portal, y no lo hice.

## MSC: un solo intento más, y solo tras el error después de la clave

### Lo que hace ahora

```
abrir myMSC → usuario → «Next» ─┬─ sesión ─────────────────────────────────────────────→ sesión
                                ├─ error → recarga una vez (encargo 47) ─┬─ clave → …
                                │                                        └─ error → fin: NO ENVIADA (MSC_SIN_SESION)
                                └─ clave → botón de entrar ─┬─ sesión → sesión
                                                            ├─ nada en 30 s → fin: NO ENVIADA (MSC_SIN_SESION)
                                                            └─ error ⇒ evidencia ⇒ segundo intento, desde el principio
segundo intento: lo mismo, una vez; si no deja la sesión → fin: NO ENVIADA (MSC_SIN_SESION_TRAS_DOS)
```

- **El segundo intento** abre otra vez www.mymsc.com, escribe el usuario, pulsa «Next» y, si aparece el campo, escribe
  la clave por segunda y última vez. Si identityserver todavía tiene la sesión, entra sin pedirla: así entró, en 3 de 6
  casos con esta falla, la pasada siguiente del código de antes del encargo 45.
- **La ida a eBooking salió**, también tras los otros errores: no rescató la sesión en ninguno de los 4 casos medidos, y
  dos eran tras el «Next». Para esos errores, el desenlace medido es el mismo de hasta hoy (NO ENVIADA), sin ese paso.
- **El motivo de las filas** lo deja el login en la corrida (`_motivo_sin_sesion`): tras los dos intentos, «no quedó
  iniciada la sesión de MSC: el portal dio un error al volver a myMSC después de aceptar el usuario y la clave, y el
  único intento más, desde el principio, tampoco dejó la sesión. La reserva no se envió (el detalle, en log.txt)». Sin
  segundo intento, el de siempre.
- **Lo que no cambió:** el «Next» y el botón de entrar se pulsan por su texto, como antes; no hay clics nuevos. La
  recarga tras el error del «Next» es la del encargo 47. «Solo iniciar sesión» usa el mismo `login_msc`, así que también
  hace el segundo intento.

### Cómo lo leí

- **«Ese 502» es el error que aparece después del botón de entrar,** cuando b2clogin e identityserver ya aceptaron el
  usuario y la clave. El error tras el «Next» lo trata la recarga del encargo 47, que no cambia.
- **Si el 502 de la vuelta a myMSC llega justo tras el «Next»** (cuando identityserver todavía tiene la sesión y no pide
  la clave), el programa lo toma como el error del «Next»: recarga una vez y no hace el segundo intento. La línea nueva
  de `log.txt` dirá qué dirección falló en cada caso.

## MSC: la evidencia del error

### Lo que anota `log.txt`

Cada vez que aparece la página de error (en la portada, tras el «Next», tras la recarga o tras la clave, en cada
intento), una línea como esta, que sale de la prueba con datos inventados:

```
respuesta que trajo la página de error: POST https://www.mymsc.com/myMSC/Account/OidcLoginCallBack · HTTP 502 ·
falla de red: net::ERR_HTTP_RESPONSE_CODE_FAILURE · cabeceras (6): content-length, content-type, server, set-cookie,
via, x-azure-ref · server: PasarelaDePrueba/1.0 · via: 1.1 proxy-de-prueba
```

- **La dirección**, sin su consulta, su fragmento ni un usuario o una clave en ella: solo el servidor y la ruta.
- **El código HTTP** y, si Chrome la dio por fallida, su falla de red. Sin una respuesta HTTP, solo la falla.
- **El nombre de todas las cabeceras**, también `set-cookie`, y **el valor solo de estas:** `server`, `via`,
  `x-powered-by`, `x-cache`, `x-cdn`, `x-served-by`, `cf-cache-status`, `cf-mitigated`, `x-datadome` y
  `akamai-cache-status`. Nombran al servidor o a una protección contra robots. Un identificador de petición o de
  cliente (`cf-ray`, `x-azure-ref`, `x-datadome-cid`…) va solo con su nombre, que ya dice de quién es. Cada valor va
  recortado a 80 caracteres.
- Toma la última respuesta que falló (código 400 o más) desde la línea anterior. Si ninguna falló, como cuando la
  página de error de MSC llega con código 200, lo dice y da la última.
- Además, la dirección de la página sin su consulta, su captura (`msc_error_portada`, `msc_error_next`,
  `msc_error_recarga` o `msc_error_clave`, con «_2» en el segundo intento) y su HTML.

### La base, medida sin red y con datos inventados

Un servidor local en 127.0.0.1 respondió 502 sin cuerpo a un envío de formulario (como la vuelta a myMSC) y a un GET con
el usuario en la consulta (como TriggerOidcLogin), y 502 con cuerpo a otro GET. En Chrome sin interfaz, con un perfil
temporal dentro de la carpeta del encargo:

- **Playwright entrega la respuesta 502**, con su código y sus cabeceras, y después una falla de red
  `net::ERR_HTTP_RESPONSE_CODE_FAILURE`. La página queda en `chrome-error://chromewebdata/`. Con cuerpo, solo la
  respuesta.
- **`headers` no trae `set-cookie`, y `all_headers()` sí.** El programa usa `all_headers()` para los nombres; si falla,
  usa `headers` y lo dice.
- **El HTML de la página de error de Chrome tras el GET trae la dirección entera, con el usuario.** Tras el POST, no
  trae la dirección.

En el historial del perfil, TriggerOidcLogin trae el usuario en `usernameLoginHint` en sus 119 visitas, y la vuelta a
myMSC (`OidcLoginCallBack`) no trae consulta en ninguna de sus 107. Por eso:

- **El HTML que traiga el usuario o la clave no se guarda** (tal cual o codificados para una dirección, sin distinguir
  mayúsculas). `log.txt` lo dice, sin decir cuál. El del error tras la clave sí se guarda; el del error tras el «Next»,
  probablemente no.
- **Las direcciones del inicio de sesión de MSC van a `log.txt` sin su consulta,** y lo dice («(sin su consulta)»). Hasta
  hoy, `_msc_recargar` anotaba la dirección entera después de la recarga, que podía ser la de b2clogin con el usuario.

## COSCO: el puerto traducido, en pantalla, en `log.txt` y en el motivo

- **Cuándo traduce:** cuando el mapa cambia el puerto de la fila por otro puerto, como hacen 3 de sus 8 entradas. No
  cuando solo cambia cómo se escribe el mismo: con o sin tilde, con «PUERTO» delante o con el país detrás. La regla
  compara palabras: todas las del puerto del mapa tienen que estar en las de la fila. Los nombres de cada entrada están
  en `CLAUDE.md` y en el código.
- **Qué dice:** con la sugerencia ya elegida en «Origin City», la pantalla y `log.txt` dicen «⚠ COSCO: el puerto de carga
  de la fila, «…», lo traduce MAPA_PUERTOS_COSCO a «…»: la reserva se arma desde «…».» Además, el motivo de la reserva,
  sea cual sea su estado, termina con «puerto de carga: COSCO la arma desde «…»; la fila dice «…»
  (MAPA_PUERTOS_COSCO)». Así llega al panel y a la planilla.
- **Tu planilla:** en las dos copias (la de la raíz y la que subió el panel a las 18:52), la fila de COSCO trae el mismo
  puerto de carga que las de CMA-CGM y HYUNDAI, y el mapa no lo traduce. La próxima corrida de COSCO no mostrará el
  aviso. Las filas de ONE y MSC siguen con el otro puerto, pero ellas no usan el mapa.

## El contexto de negocio, en `CLAUDE.md`

Quedó en «Qué es»: la reserva solo asegura el espacio de los contenedores en la nave, y la agencia de aduana pone
después el cliente, el peso y el producto correctos. Por eso la descripción de la carga, el HS 030313 y el peso de
22.500 kg son los mismos en todas, y está bien que ONE declare otra descripción de salmón. En «Planilla Excel», el
peso dice lo mismo.

## Fuera del encargo: `log.txt` ya guardaba el usuario de COSCO y el código de ONE

Al medir qué parámetros trae cada dirección que el programa escribe en `log.txt` (34 de 34 leídos), encontré la línea
«URL:» que escribe `reg.url` desde siempre, con la dirección entera:

- **40 líneas, en 11 días,** con la dirección de inicio de sesión de COSCO, cuyo `login_hint` es un usuario de
  `config.json` (comparado en memoria, sin imprimirlo).
- **7 líneas, en 5 días,** con la vuelta de ONE (`o-callback`) y su `code` (45 caracteres) y su `state` (87). Un código
  de autorización caduca en minutos y se usa una vez.

No es la evidencia nueva ni lo cambié: toca a las seis navieras. Lo propongo en el residual. El login de MSC ya no
escribe sus direcciones con la consulta.

## Las pruebas y las mutaciones

- **8 pruebas nuevas y una que sale** (de 573 a 580):

  | Prueba | Qué vigila |
  |---|---|
  | `test_clics.TestMsc.test_tras_el_error_despues_de_la_clave_un_solo_intento_mas` | El segundo intento, desde el principio y sin eBooking; la clave dos veces como mucho; nunca un tercero; las capturas con «_2»; el motivo, y que no quede para el login siguiente |
  | `test_clics.TestMsc.test_otros_errores_no_reintentan` | El error en la portada, el del «Next» tras la recarga y la espera vencida: sin otro intento ni eBooking |
  | `test_clics.TestMsc.test_el_error_deja_su_respuesta_y_su_evidencia` | La línea de `log.txt` tras la clave y tras el «Next»; el HTML con el usuario no se guarda, y ningún archivo de la corrida trae el usuario, la clave, la cookie ni la consulta; deja de escuchar al terminar |
  | `test_clics.TestMsc.test_respuesta_del_error_sin_valores_de_sesion` | Cuál respuesta elige, que ignore otros marcos y otros tipos, el valor solo de la lista, el recorte, sin repetir, la dirección sin consulta |
  | `test_clics.TestMsc.test_html_sin_el_usuario_ni_la_clave` | `_guardar_html_completo` con `sin` y `_textos_de_la_cuenta` |
  | `test_clics.TestCosco.test_puerto_traducido_lo_dicen_el_log_y_el_motivo` | Cuándo traduce, el aviso, la nota, el decorador y su lugar |
  | `test_web…` y `test_consola…test_login_de_msc_deja_su_motivo` | Las filas toman el motivo que dejó el login |

- **Las pruebas que cambiaron**, porque fotografiaban la ida a eBooking o los decoradores:
  - `test_ante_el_error_va_una_vez_a_ebooking_y_no_reintenta` se reemplazó por las dos primeras;
  - en `test_tras_el_error_del_next_recarga_una_vez`, tras la recarga fallida ya no hay eBooking;
  - `test_login_sin_clic_generico` suma las funciones nuevas, y fija que la escucha y la evidencia no pulsen ni naveguen;
  - `test_cada_reservador_que_corta_esta_decorado` suma el decorador de COSCO.
- **La página falsa del login** ahora escucha como Playwright y emite lo medido sin red: la respuesta 502 y su falla de
  red; tras el «Next», con el usuario en la dirección. Las credenciales del login falso son inventadas.
- **Mutaciones:** de 1.713 a 1.765.
  - Entran 59 (`e50-…`): 50 del inicio de sesión de MSC, su evidencia y su motivo, y 9 de COSCO.
  - Salen las 7 del encargo 45 que mutaban la ida a eBooking.
  - 7 cambian su texto o su prueba: 5 del inicio de sesión de MSC, y las dos del origen de COSCO, que ahora nombran
    también la línea de la celda.
- **`test_candado` no cambió y pasa.**

## Re-medir

Los scripts están en la carpeta del encargo (`scratchpad/e50`), con `source entorno_e50.sh` (TEMP, TMP y TMPDIR dentro
de ella). Ninguno imprime un valor de la planilla ni de `config.json`: `mascara.py` enmascara y aborta si se le escapa
uno.

| Qué | Comando | Resultado |
|---|---|---|
| Las corridas de `logs/` desde el 02-10 | `python3.13 corridas.py 20261002` | 34 carpetas, 0 que no calcen; la última, 18:52:36 |
| El `log.txt` de la corrida de CMA-CGM | `python3.13 ver_log.py 20261002_185236` | 69 líneas; la 67 y la 68, la guarda «SIN emitir» |
| El tramo de CMA-CGM de la corrida de las 16:50 | `python3.13 ver_log.py 20261002_165010 82 160` | Los mismos pasos |
| El perfil después de las 18:50 | `python3.13 historial_cma.py "2026-10-02 18:50" cma-cgm` | Última visita, 18:53:10 |
| Los parámetros de cada paso del login de MSC, por nombre | `python3.13 parametros_msc.py` | TriggerOidcLogin: `usernameLoginHint` en 119 de 119; vuelta a myMSC: sin consulta en 107 |
| Los parámetros de las direcciones de `log.txt` | `python3.13 urls_en_logs.py` y `python3.13 hint_cosco.py` | 34 de 34 leídos; 40 con el usuario de COSCO, 7 con el código de ONE |
| Avisos de bloqueo o de intentos fallidos | `python3.13 bloqueo_msc.py` | 0 en 1.189 líneas, 30 capturas y 367 títulos; controles, pasan |
| El 502 en Chrome, sin red | `python3.13 experimento_502.py` | Lo de «La base, medida sin red» |
| La fila de COSCO en las dos planillas | `python3.13 puerto_cosco_planilla.py` | El mismo puerto que CMA-CGM y HYUNDAI; no se traduce |
| Todas las mutaciones, sin correr pruebas | `python3.13 mut_viejos.py e50- msc-espera-sin-el-error msc-recarga-tras-cualquier-error msc-recarga-sin-captura cosco-origen-sin-pedir cosco-origen-palabra-antes` | 1.765; 0 problemas |
| La suite | `python tests/correr.py` | 580 pruebas, OK, en 580 s; los 4.469 originales, sin cambios. Tardó el doble que en el encargo 49: otra sesión corría pruebas en el HUB a la vez |
| El censo de lo nuevo | `python tests/correr.py --mutaciones --filtro e50-` | 58 mutaciones, 74 pares: todos muerden |
| El censo de lo viejo que toca el cambio | `--filtro TestMsc.`, `cosco-origen`, `cosco-sin-decorador` y `login_fallido` | 116 mutaciones y 141 pares; 20 y 20; 4 y 7; 7 y 8: todos muerden |
| El censo de la prueba que amplié al final, con la mutación 59 | `--filtro respuesta_del_error_sin_valores` | 18 mutaciones, 25 pares: todos muerden |

## NO retroceder

- **No vuelvas a la ida a eBooking** tras un error del inicio de sesión de MSC: no dejó la sesión en ninguno de los 4
  casos medidos.
- **No hagas un tercer intento de inicio de sesión en MSC,** ni el segundo tras otro error que no sea el de después de
  la clave: es tu decisión, por el riesgo de bloquear la cuenta.
- **No anotes en `log.txt` el valor de una cabecera fuera de `MSC_CABECERAS_CON_VALOR`,** ni sumes a esa lista una de
  cookies, de autorización o un identificador. La prueba lo vigila.
- **No guardes el HTML de la página de error sin la guarda del usuario y la clave:** tras el «Next», trae el usuario.

## Defectos de instrumento

- **`--filtro` del censo solo prepara las mutaciones elegidas:** una vieja cuyo texto ya no calza no se ve. Escribí
  `mut_viejos.py`, que cuenta el texto viejo de todas sin correr pruebas, y encontró 4 rotas por el cambio de COSCO:
  - dos pedían seguidos los decoradores de `reservar_cosco`, y yo había puesto el nuevo entre ellos: lo puse por fuera
    de todos, que también lo deja por fuera de `_sin_clic_a_ciegas`, y la foto de los decoradores lo cuenta;
  - dos nombraban la línea `puerto = _puerto_de_carga(celda)`, que `_cosco_traduccion` repite: ahora nombran también la
    línea de antes.
- **`mut_viejos.py` compilaba el programa en cada una de las mutaciones,** y a los 10 minutos no había terminado.
  Lo detuve, comprobé que no quedara su proceso, y ahora compila solo las nuevas o cambiadas.
- **En `bloqueo_msc.py`, la primera versión imprimía los títulos** de las páginas que calzaran, y un título puede traer
  un dato. Antes de correrla la cambié para que imprima solo su largo.
- **Mis pruebas, antes de pasar:** la respuesta falsa sacaba sus `headers` de `all_headers`, y al anular esta, la
  prueba anulaba las dos; un recorte que conté mal (74 «x» en vez de 70); y la de COSCO usaba el `log.txt` común de la
  clase, donde las demás pruebas ahora también dejan el aviso (17 en vez de 1).
- **Volví a usar `sort`,** que Defender bloquea, al contar los motivos del censo: «Permission denied». Lo conté con
  Python.
- **Un `python -c` sin `PYTHONIOENCODING`** cayó al imprimir un «✗» en la consola cp1252.
- **Mi relectura del código encontró un borde:** `_msc_respuesta_del_error` con `escucha=None` (el valor por defecto de
  `_msc_entrar` y `_msc_recargar`, que hoy no usa nadie) se caía. Ahora lo dice, como una página que no deja escuchar,
  con su prueba y su mutación, la 59.

## Premisas refutadas

- **«Marcelo hizo la primera emisión real de CMA-CGM con el launcher de emisión.»** La corrida más reciente de
  `logs/` no emitió: se detuvo en la guarda con el candado cerrado.
- **«Confirmar que quedó EMITIDA y que el número capturado es el del portal».** Aun emitiendo, CMA-CGM no puede llegar a
  EMITIDA ni capturar un número: no tiene forma medida.

## Residual

| Qué quedó | Por qué | Cuándo se reabre |
|---|---|---|
| **La línea «URL:» de `log.txt` guarda el usuario de COSCO (40 líneas) y el código de ONE (7)** | Toca a las seis navieras y no es del encargo: es `reg.url`. Arreglarlo es quitar la consulta en una línea | Lo encargas: la consulta fuera en todas, y si se limpian o no los `log.txt` viejos |
| El 502 de la vuelta a myMSC justo tras el «Next» no hace el segundo intento | Tu decisión habla del error después de la clave; ese caso pasa sin escribirla (identityserver con la sesión) | Lo decides, con lo que diga la línea nueva de `log.txt` |
| El error tras el «Next» que sigue después de la recarga no hace el segundo intento | Igual: el segundo intento es para el error después de la clave | Lo decides |
| `log.txt` no dice con qué candado corre una corrida | Por eso no se puede saber con qué lanzador se hizo la de las 18:52 | Lo encargas: una línea con el candado al empezar cada corrida |
| El aviso del modo en el panel se pinta solo al cargar la página | Una pestaña vieja puede mostrar un modo y hablar con un servidor del otro | Lo encargas |
| La forma del número de CMA-CGM (`FORMA_BOOKING`) | Ninguna corrida guardó una confirmación de CMA-CGM | La primera emisión real de CMA-CGM deja `cma_f<fila>_6_confirmado` |
| La línea nueva y el segundo intento, en el portal | Sin portal no se prueban | El próximo error de MSC: su línea en `log.txt` y su captura |
| El HTML del error tras el «Next» no se guarda | Trae el usuario en la dirección | Si lo quieres, con la consulta borrada antes de guardarlo |
| La revisión por un subagente | Las revisiones se proponen, no se lanzan solas | Lo pides |
| El censo completo (1.765 mutaciones, cerca de una hora) | Corrí el de lo nuevo y el de lo viejo que toca el cambio, y conté el texto de todas | Lo pides, o antes de la próxima versión |

## Reglas

- **`metodo-ciclo` v15:**
  - re-medir contra `HEAD` (la base, `20b5dcd`, ya estaba en `origin`);
  - control positivo que aborta, en cada sonda (la máscara, el OCR, los avisos de bloqueo, `_cosco_traduccion` y
    `mut_viejos.py`);
  - contador al lado de cada cero (34 de 34 `log.txt` leídos, 1.765 mutaciones con 0 problemas);
  - el negativo tiene que morder, de a uno: el censo;
  - el cambio y su guardián en el mismo commit;
  - cada reemplazo afirma que su texto viejo aparece una sola vez (`comun.py`), con el EOL verificado (0 CR);
  - frenar en lo que es de negocio: lo que interpreté va arriba y en el residual;
  - el alcance: lo que encontré fuera del encargo va como propuesta.
- **Las del módulo, en `CLAUDE.md`:**
  - `test_candado` no cambia y pasa;
  - ningún clic nuevo: la escucha y la evidencia solo leen, y una prueba lo vigila;
  - cada prueba nueva con su mutación;
  - la sonda de secretos antes de cada commit;
  - nada de `logs/`, `config.json`, planillas ni `perfiles/` en el repo, y `perfiles/` solo leído (SQLite inmutable).
- **Las permanentes:** el push lo haces tú; nada fuera de la carpeta del encargo; datos de prueba inventados; no se
  reporta el estado de los servidores MCP.
- **Choques:** ECC pide lanzar un revisor después de cambiar código, programar con objetos inmutables y otras cosas;
  mandan las reglas permanentes y `metodo-ciclo`. La revisión queda propuesta, y seguí el estilo del repo.

## Lo que dio en el repo

- `6f0edc9` fix: MSC, un solo intento más tras el error después de la clave y la evidencia del error; COSCO avisa el
  puerto traducido;
- y el de este informe, con `CLAUDE.md` al día.

El push lo haces tú. Los comandos, con el hash esperado, van en el mensaje final del encargo: este informe va dentro
del commit y no puede citar su propio hash.
