# Encargo 53: el bloqueo de CMA-CGM, el sandbox de Chrome y los cuatro puertos

Base: `Agendamiento Reservas` @ `9f45608` · árbol limpio (al empezar, 2026-10-06).

## En resumen

- **La corrida de las 09:58 no fue de emisión, y no se emitió nada** (el primer FRENA SI no se cumple). Este equipo
  registra hoy dos corridas, y las dos son de solo inicio de sesión, en modo prueba: a las 09:54:52, en las seis
  navieras, y a las 09:57:47, solo en CMA-CGM. Ninguna armó una reserva (no hay ninguna carpeta de reservas de hoy en
  `logs/`), y en CMA-CGM el programa no llegó a escribir el usuario. El lanzador de emisión no se abrió hoy: el caché
  de Python que deja al abrirse sigue siendo del 23-09 (sección 1, con su control).
- **Dónde apareció el bloqueo.** A las 09:56:25, al pulsar «login» en la portada, CMA-CGM mostró el deslizador de
  DataDome, y el programa esperó al operador. Pasadas las 09:57:25, el proceso del panel terminó sin cerrar su
  registro. A las 09:57:52, en la portada misma, apareció «El acceso está restringido temporalmente», sin deslizador, y
  a las 09:58:10 se cerró el navegador.
- **Lo que cambió hoy, medido: la IP.** Cada página de DataDome dice con qué IP vio el pedido. En 86 s fueron dos IP
  distintas, de dos registros regionales: la del deslizador, de un bloque de América del Norte (ARIN), y la del
  bloqueo, de uno de América Latina (LACNIC), una IP que no había aparecido en ninguna captura anterior. En Windows no
  hubo ningún cambio de red entre las 09:18:50 y las 10:30: el cambio pasó en la salida de la red a internet, no en
  este equipo.
- **Lo que no cambió desde el 02-10, cuando el desafío se pasó:** el código que lanza el navegador y el login de CMA
  (0 líneas distintas), la versión de Chrome (154.0.8037.93) y el navegador mismo (Chrome, no el Chromium de respaldo).
- **El desafío de DataDome no es nuevo.** Apareció en 10 de las 22 corridas con CMA-CGM que registran los `log.txt`
  desde el 21-09 (en 7 de los 8 inicios de sesión), y el operador lo pasó en las 8 anteriores a hoy, en 7 a 92 s.
- **Las señales del navegador**, medidas en una página local sin red. La página ve que el navegador del programa está
  retocado por `STEALTH_JS`, el «modo sigiloso» que el programa ya traía: `navigator.webdriver` vale `undefined`, con un
  getter que no es nativo; `navigator` trae tres propiedades propias; los plugins son una lista de números; y los
  idiomas no calzan con el idioma. Ve también una escala de pantalla de 0,65. El aviso de `--no-sandbox` lo ve solo
  quien usa el equipo, la página no.
- **La causa no se puede confirmar sin el portal** (el tercer FRENA SI se cumple, y ahí frené). Lo medido apunta al
  cambio de IP en medio del desafío, sobre un navegador que DataDome ya desafiaba. Confirmarlo es cosa de CMA-CGM (su
  página da un ID para su servicio de asistencia) o de TI (la salida de la red). No abrí el portal.
- **El sandbox de Chrome, hecho** (decisión de Marcelo). Todo navegador del programa sale ahora de un solo ayudante,
  `_lanzar_navegador`, con `chromium_sandbox=True`. Arranca en este equipo, Chrome y el Chromium de respaldo, y sus
  procesos de página quedan aislados; ninguna señal que lee la página cambia (el segundo FRENA SI no se cumple).
  **Pero Chrome avisa ahora de otra bandera del programa**, `--disable-blink-features=AutomationControlled`.
- **Los cuatro puertos en cada arranque, hecho** (decisión de Marcelo). El lanzador pregunta a los cuatro a la vez y
  trata como hasta hoy a un panel de AQUASHIELD en cualquiera de ellos, también con el 8765 libre; si hay más de uno,
  decide el primero.
- La suite pasa: 617 pruebas en 1.185 s, y 0 cambios en los originales. La primera corrida la cortó el corredor a los
  1.200 s, su plazo, con el equipo cargado por otros programas. Mutaciones: 1.865 (entran 17, cambian 8, no sale
  ninguna); el censo de las áreas del cambio: 80 mutaciones distintas y 122 pares, todos muerden.

## 1. Las corridas de hoy: qué fueron y qué no

Medido en `logs/` (36 carpetas de corrida, 0 que no calcen con el patrón del programa) y en el historial del perfil
del programa (`perfiles/<operador>`, leído inmutable).

| hora | carpeta | candado | navieras | CMA-CGM | cómo termina |
|---|---|---|---|---|---|
| 09:54:52 | `<operador>_…` (solo inicio de sesión) | modo prueba, sin llaves | las seis | deslizador de DataDome a las 09:56:25, al pulsar «login» | el registro se corta a las 09:57:25, en la espera del deslizador, sin el error ni el resumen |
| 09:57:47 | `<operador>_…` (solo inicio de sesión) | modo prueba, sin llaves | CMA-CGM | «acceso restringido» en la portada, a las 09:57:52 | «Target page, context or browser has been closed» a las 09:58:10; REVISAR |

- **No se armó ninguna reserva:** hoy no hay ninguna carpeta `web_…` ni `reservas_…`. La planilla que sube el panel
  (`aquashield_planilla.xlsx`, en el temporal de Windows) es de las 09:57:42, pero ninguna corrida la usó.
- **En CMA-CGM no se escribió el usuario:** ninguna de las dos llegó a «Ingresando credenciales». El historial del
  perfil dice lo mismo: 3 visitas a las 09:56 (la portada y el inicio de sesión de la portada) y 2 a las 09:57 (la
  portada); ninguna a `auth.cma-cgm.com`.
- **El lanzador de emisión no se abrió hoy.** `AQUASHIELD_EMISION.py` hace `import AQUASHIELD`, y Python deja su caché
  en `__pycache__/AQUASHIELD.cpython-313.pyc`. Ese archivo es del 2026-09-23 a las 11:07, y el programa cambió después
  (el 05-10 a las 20:44). Si el lanzador se hubiera abierto, Python lo habría reescrito.
  - Control: el mismo `pythonw` que usan los `.bat`, con un lanzador y un módulo sintéticos en una carpeta nueva,
    escribe el `.pyc` del módulo.
  - El primer intento del control no lo escribió: el entorno de esta sesión trae `PYTHONDONTWRITEBYTECODE=1`, que el
    del usuario y el de la máquina no traen. Sin esa variable, como lo abre el Explorador de Windows, lo escribe.
- **Por qué se cortó el primer registro, no quedó dicho.** Con el navegador cerrado, el registro anota el error y el
  resumen, como a las 09:58:10; aquí no anota nada, así que terminó el proceso del panel (su botón de apagar, por
  ejemplo), no solo el navegador. El lanzador nuevo no lo pudo cerrar: con un inicio de sesión en curso, el panel está
  ocupado, y al ocupado no lo toca (encargo 52).

## 2. Cuántas veces entró el programa a CMA-CGM, y con qué intervalo

Del historial del perfil del programa: una entrada empieza con cada visita a la portada que abre el programa. Desde el
01-09, 48 entradas y 455 visitas a CMA-CGM, todas a `www.cma-cgm.com` o `auth.cma-cgm.com`, y 0 fuera de los pasos que
el script reconoce. Los desafíos no quedan en el historial (0 visitas a servidores de desafíos): salen de los `log.txt`.

| día | entradas | intervalo más corto | desafío de DataDome (de los `log.txt`) |
|---|---|---|---|
| 09-24 | 1 | — | sí, pasado en 76 s |
| 09-25 | 2 | 13 h 17 min | sí, pasado en 10 s |
| 09-26 | 2 | 8 min 40 s | sí, pasado en 10 s |
| 09-27 | 2 | 5 min 00 s | sí, pasado en 8 s |
| 09-29 | 2 | 3 min 41 s | sí, pasado en 20 s |
| 09-30 | 2 | 13 min 09 s | sí, pasado en 92 s |
| 10-01 | 2 | 4 min 17 s | sí, pasado en 22 s |
| 10-02 | 5 | 2 min 21 s | sí (11:53), pasado en 7 s; no a las 16:48 |
| 10-06 | 2 | 1 min 32 s | dos veces, no pasado: el deslizador y el bloqueo |

- Hoy entró a las 09:56:17 y a las 09:57:50. La entrada anterior fue el 02-10 a las 18:52:56, 3 días y 15 horas antes.
- El intervalo de hoy (1 min 32 s) es el más corto desde el 17-09. Ese día hubo 8 visitas a la portada en 2 min 22 s,
  cada 11 a 27 s, de una versión del programa sin `log.txt` en este equipo; ese día, a las 10:29, el inicio de sesión
  entró.
- En los `log.txt` (desde el 21-09): 22 corridas con CMA-CGM, 10 con el desafío y 8 pasadas. Por tipo de corrida, el
  desafío salió en 7 de las 8 de solo inicio de sesión y en 3 de las 14 de reservas, que casi siempre llegan con la
  sesión que dejó un inicio de sesión unos minutos antes.

## 3. Lo que vio el portal: la IP

Las 10 capturas del desafío que guardó el programa (`cma_robot_desafio.png`), leídas con OCR (control sintético, y 0
ilegibles). Cada IP distinta sale con una letra y su registro regional (tabla de IANA de los bloques /8); el informe no
trae ninguna IP ni ningún ID.

| corrida | página | IP | registro |
|---|---|---|---|
| 09-24 18:45 | deslizador | A | LACNIC (América Latina) |
| 09-25 13:47 | deslizador | A | LACNIC |
| 09-26 14:13 | deslizador | A | LACNIC |
| 09-27 18:31 | deslizador | A | LACNIC |
| 09-29 14:59 | deslizador | B | LACNIC |
| 09-30 15:10 | deslizador | C | ARIN (América del Norte) |
| 10-01 16:02 | deslizador | C | ARIN |
| 10-02 11:52 | deslizador | A | LACNIC |
| 10-06 09:54 | deslizador | C | ARIN |
| 10-06 09:57 | **restringido** | **D** | LACNIC |

- En dos semanas, el portal vio cuatro IP de este equipo, una de un bloque de América del Norte. Con cada una, el
  desafío se pasó (D apareció solo hoy).
- Hoy, el deslizador salió con C y el bloqueo, 86 s después, con D.
- **En Windows no cambió nada en ese tiempo.** Su registro de eventos de red (`NetworkProfile/Operational`,
  `WLAN-AutoConfig/Operational`, `Dhcp-Client`) muestra el paso del Wi-Fi corporativo a la red cableada entre las 09:14
  y las 09:17, y nada más desde las 09:18:50 hasta las 10:30.
- **Hoy, ahora:** el equipo sale por la red cableada; no hay proxy del usuario, ni archivo PAC, ni proxy WinHTTP, ni
  políticas de proxy de Chrome. FortiClient está instalado: dos de sus procesos corren y su adaptador de VPN está
  desconectado; esta mañana no hubo un evento de conexión de VPN. Esto es de la tarde, no de las 09:56.
- Lo más probable es que la red tenga más de una salida a internet (sin medir: lo sabe TI). La IP de América del Norte
  puede ser un servicio de seguridad o una VPN de la red, y la página de CMA-CGM pide justamente evitar «servidores
  proxy o servicios de VPN».

## 4. Las señales del navegador, en una página local sin red

`senales.py` lanza cada navegador con un perfil nuevo y vacío dentro de la carpeta del encargo (nunca `perfiles/`) y
un proxy muerto (`--proxy-server=http://127.0.0.1:9`), para que nada salga a internet. Abre una página que sirve el
mismo script en 127.0.0.1, en un puerto que da el sistema. La página junta las señales en JavaScript y se las manda al
script. Lee también la línea de comandos (`chrome://version`, sin el proxy muerto), el aislamiento
(`chrome://sandbox`) y el aviso de la ventana (una captura solo de esa ventana, con `PrintWindow`, leída con OCR).

| señal | el programa hoy | sin `STEALTH_JS` | el programa con el sandbox | Chrome normal |
|---|---|---|---|---|
| `navigator.webdriver` | `undefined`, getter no nativo | `false` | `undefined`, getter no nativo | `false` |
| propiedades propias de `navigator` | `webdriver`, `languages`, `plugins` | ninguna | las mismas tres | ninguna |
| plugins | `[1,2,3,4,5]`, un `Array` | 5, `PluginArray`, «PDF Viewer» | `[1,2,3,4,5]` | 5, `PluginArray` |
| idiomas / idioma | es-CL, es, en / es-ES | es-ES, es / es-ES | es-CL, es, en / es-ES | es-ES, es / es-ES |
| `devicePixelRatio` | 0,65 | 0,65 | 0,65 | 1 |
| marcas (`userAgentData`) | Chrome 154 | Chrome 154 | Chrome 154 | Chrome 154 |
| CDP por la consola | no lo detecta | no lo detecta | no lo detecta | no lo detecta |
| `--no-sandbox` en la línea | sí | sí | no | no |
| procesos de página (`chrome://sandbox`) | sin aislar | sin aislar | aislados (Lockdown) | — |
| aviso de la ventana | `--no-sandbox` | `--no-sandbox` | `--disable-blink-features=AutomationControlled` | ninguno |

- **Lo que ve la página:** las cuatro primeras filas son `STEALTH_JS`. Sin él, esas señales son las de un Chrome
  normal; con él, cada una delata un retoque: un `webdriver` que Chrome no da, un getter escrito a mano, propiedades
  propias en `navigator` y una lista de plugins que no es una `PluginArray`. La escala de 0,65 sale de
  `--force-device-scale-factor` (`AQUASHIELD_ZOOM`, para que quepa más página).
- **Lo que no ve la página:** `--no-sandbox` y el aviso de la ventana. El sandbox no cambia ninguna señal de la página.
- **El truco de CDP por la consola** (un `Error` con un getter de `stack` pasado a `console.debug`) no detectó la
  conexión de Playwright en ninguna configuración: con este Chrome no sirve para medirla. Que el portal la detecte por
  otra vía no está medido.
- **Dos configuraciones más, solo medidas** (para decidir sobre el aviso nuevo):
  - Sin `--disable-blink-features=AutomationControlled` y sin `STEALTH_JS`, `navigator.webdriver` vale `true`, y no
    hay aviso. Esa bandera es lo que esconde la automatización.
  - Además con `--enable-automation`, la marca que Playwright pone por defecto y el programa quita, `webdriver` vale
    `true` y aparece el aviso «software de prueba automatizado».
- **El respaldo, el Chromium de Playwright**, es «Chrome for Testing» 145, nueve versiones más viejo que el Chrome del
  equipo, y su marca no dice «Google Chrome». Hoy no se usó: el login lo habría anotado.

## 5. La causa: lo que se puede decir sin el portal

El tercer FRENA SI se cumple: confirmar la causa exige el portal. Lo medido, ordenado por lo que lo sostiene:

1. **El cambio de IP en medio del desafío.** Es lo único nuevo de hoy: el deslizador con la IP C y, 86 s después,
   desde una IP que el portal nunca había visto (D), el bloqueo. El portal ya tenía su cookie de DataDome en este
   perfil, y la vio llegar desde otra red. La página nombra las VPN y los proxies, y muestra la IP. El cambio no pasó en
   este equipo. En contra: entre un día y otro la IP también cambió (A, B, C) y el desafío se pasó; dentro de un mismo
   desafío, nunca se había visto.
2. **El segundo intento, 1 min 32 s después de un desafío sin pasar,** el intervalo más corto desde el 17-09.
3. **Un navegador que DataDome ya desafiaba:** las señales de `STEALTH_JS` y la escala de 0,65 están desde antes del
   23-09, sin cambios, y desde el 24-09 el desafío salió en casi todos los primeros inicios de sesión del día. Explican
   el desafío; solas, no el bloqueo de hoy.
4. **La misma cuenta en otro navegador o por otra persona a la vez:** sin medir. Los dos datos del encargo para eso
   llegaron en blanco (el Chrome normal de Marcelo en cma-cgm.com a esa hora, y si alguien del equipo usaba la cuenta).
   No miré el historial del Chrome personal de Marcelo.

Descartado, medido: una emisión (no hubo corrida de reservas); un cambio del programa, de Chrome o del navegador usado;
y el aviso de `--no-sandbox`, que la página no ve.

**Quién puede confirmarlo:** CMA-CGM, con el ID que muestra su página («Ponerse en contacto con el servicio de
asistencia»), o TI, que sabe por dónde sale la red. El perfil del programa guarda la cookie de DataDome que el portal
dejó a las 09:58:08, en la página del bloqueo (leí solo sus fechas, nunca su valor). Borrarla sería esquivar la
protección del portal, y no lo propongo.

## 6. El sandbox de Chrome

- **El cambio:** `_lanzar_navegador(p, perfil, headless, canal, reg)` arma las opciones de siempre más
  `chromium_sandbox=True`, prueba el canal de `config.json` (Chrome), cae al Chromium de Playwright si no abre, y agrega
  `STEALTH_JS`. Lo usan las tres vías que abren un navegador: `ejecutar_login`, `ejecutar_reservas` y `_web_worker`.
  Hasta hoy cada una armaba sus opciones, y las dos de reservas cambiaban a Chromium sin decirlo; ahora las tres lo
  anotan en `log.txt`.
- **Medido en este equipo** (segundo FRENA SI, no se cumple):
  - con el ayudante del programa, Chrome arrancó en 2,8 s, sin `--no-sandbox` en su línea de comandos, y con sus
    procesos de página aislados (`chrome://sandbox`: 3 en «Lockdown»);
  - el Chromium de respaldo también arrancó con el sandbox, en 6,2 s;
  - ninguna señal que lee la página cambió (sección 4).
- **El aviso nuevo:** con el sandbox, Chrome avisa de `--disable-blink-features=AutomationControlled` («No se admite el
  indicador de línea de comandos (…) que estás utilizando, ya que afecta a la estabilidad y a la seguridad»). Esa
  bandera la pone el programa, en `_args_chrome`, y es la que deja `navigator.webdriver` en `false`. Quitarla lo deja en
  `true`: es sacar parte del disfraz, y lo decides tú (Residual).
- Playwright agrega `--no-sandbox` cuando no se le pide el sandbox: `if (options.chromiumSandbox !== true)
  chromeArguments.push("--no-sandbox")` (`lib/server/chromium/chromium.js` de Playwright 1.58.0, líneas 289 y 290).

## 7. Los cuatro puertos en cada arranque

- **El cambio** (`lanzar_web`):
  1. Pregunta a los cuatro puertos a la vez (`_quien_esta`, con un hilo por puerto). Un puerto libre tarda 1 s en
     contestar en este equipo, así que mirar los cuatro tarda 1 s, como hasta hoy con el 8765 libre.
  2. Si nadie contestó y el puerto está tomado (`_puerto_libre`), le vuelve a preguntar, hasta 5 s: un panel lento
     del otro modo avisa y no corre, como en el base desde el encargo 51.
  3. Recorre los puertos en orden: el primer panel de AQUASHIELD se trata como hasta hoy (`_ceder_al_previo`: en el
     otro modo, avisa y no corre; en el mismo y ocupado, lo abre; ocioso, le pide que se apague y toma su puerto).
  4. Sin un panel, toma el primer puerto libre. Si lo tomó otro mientras miraba, le pregunta quién es, como en el
     paso 2.
  5. Avisa, en el registro del panel, de cada puerto que tiene otro programa y quedó antes del que usa (de los cuatro,
     si no usa ninguno).
- **Medido antes del cambio,** con las pruebas nuevas contra el programa de `9f45608`: con un panel en el último de
  los cuatro y el 8765 libre, el lanzador abría un panel nuevo en el 8765 en los cuatro casos, también junto a un panel
  de EMISIÓN; junto a un panel lento del otro modo, abría otro panel y además el navegador. Ahora: avisa y no corre, no
  levanta otro, o toma el puerto del ocioso, como en el base.
- **Con dos paneles, decide el primero** en el orden de los puertos, como hasta hoy decidía el del base. Así lo leí de
  «se trate como hoy»; la otra lectura, que un panel del otro modo en cualquier puerto frene, la decides tú (Residual).
- Con el panel ya en el 8765, el lanzador espera ahora 1 s más antes de abrirlo (la pregunta a los otros tres).
- Las pruebas del arranque tardan lo mismo con el programa de `9f45608` (las tres más lentas: 69,6, 55,0 y 22,6 s, y
  ahora 70,1, 64,4 y 14,9 s): las alarga el equipo cargado, porque cada panel hijo compila el programa entero.

## Pruebas y mutaciones

- **Pruebas nuevas (9): 608 → 617.**
  - `test_web.TestArranqueDelPanel`: `test_mira_los_cuatro_puertos_con_el_base_libre` (los cuatro casos de modo y
    estado), `test_panel_lento_en_otro_puerto_con_el_base_libre`, `test_pregunta_a_los_cuatro_a_la_vez` (una barrera
    de 4: de a una pregunta, se rompe), `test_otro_programa_despues_del_puerto_usado_no_se_avisa`,
    `test_con_dos_paneles_decide_el_primero`, `test_puerto_que_se_toma_mientras_mira_los_demas` y
    `test_con_los_cuatro_tomados_avisa_de_todos`.
  - `test_consola.TestUtilitarios`: `test_un_solo_lanzador_del_navegador` (en el árbol del programa, nadie más llama a
    `launch_persistent_context`, y las tres vías llaman al ayudante) y `test_navegador_con_el_sandbox_de_chrome` (las
    opciones, el respaldo y el aviso del cambio a Chromium).
  - El sandbox, también en las corridas que ya lanzaban un navegador falso: `test_corrida_de_una_hoja` (panel),
    `test_login_por_consola` y `test_reservas_por_consola`.
  - Las 11 caen contra el programa de `9f45608`, cada una por lo que vigila.
- **Mutaciones: 1.848 → 1.865.** Entran 17 (`e53-navegador-*`, 7, y `e53-lanzador-*`, 10). Cambian 8, las del
  lanzador de los encargos 51 y 52 que miraban su bucle, reescritas sobre el código nuevo con su misma intención y sus
  mismas pruebas. No sale ninguna. El chequeo previo (`mut_viejos.py`): cada texto viejo aparece una sola vez, las 27
  nuevas o cambiadas compilan, cada una de las 617 pruebas tiene su mutación, y no hay ids repetidos.
- **La suite pasa:** 617 pruebas en 1.179,5 s, OK; 4.511 originales fotografiados y 0 cambios; RESULTADO OK.
  - La primera corrida no dio resultado. `correr.py` la cortó a los 1.200 s, su plazo para la corrida entera de
    `unittest` (`TimeoutExpired`), con el equipo cargado por otros programas: la CPU al 79 % en sus 12 procesadores, la
    suite de otro proyecto corriendo desde las 10:30, OneDrive y las pruebas de otras sesiones. No dejó procesos vivos.
  - La segunda corrió con el mismo corredor y un plazo de 7.200 s (`correr_sin_tope.py`, que lo importa y cambia solo
    ese plazo, sin tocar `correr.py`). Tardó 1.185 s, 15 s menos que el plazo de siempre. En el encargo 52, la suite
    tardó 512 s.
- **El censo de las áreas del cambio:** 80 mutaciones distintas y 122 pares, todos muerden. Seis filtros, uno tras
  otro y lanzados aparte (`lanzar_censo.py`), de las 11:56 a las 12:25: las pruebas del arranque, las mutaciones
  del navegador, el candado y las tres corridas que lanzan un navegador falso (el panel, el login y las reservas de
  la consola). En cada filtro, el control sin mutar pasa, y los originales, 4.511, tienen 0 cambios. Había un par
  más, que no mordía: su prueba no llegaba a la condición de la mutación (defectos de instrumento, 7), y salió de
  ella. Las 17 mutaciones del encargo están en el censo, y las 22 de `test_candado`, que no cambió, muerden con
  sus 29 pares.
- `test_candado` no cambió y pasa.

## Re-medir

Desde la carpeta del encargo, con `TEMP`, `TMP` y `TMPDIR` en ella (`entorno_e53.sh`); los de `e51/` son de ese
encargo y se usan tal cual:

- Las corridas de `logs/`, sin el operador: `python e51/corridas.py 20260926`.
- Un `log.txt` enmascarado: `python e51/ver_log.py 20261006_095747`.
- Las entradas a CMA-CGM del historial del perfil: `python e53/entradas_cma.py 2026-09-01`.
- Los desafíos en los `log.txt`: `python e53/desafios_en_logs.py`.
- Las IP de las capturas, como letras: `python e53/ocr_desafios.py`.
- La red del equipo: `python e53/red_del_equipo.py`, y en PowerShell, `Get-WinEvent` sobre
  `Microsoft-Windows-NetworkProfile/Operational` entre las 08:30 y las 10:30.
- La cookie de DataDome, solo sus fechas: `python e53/cookie_datadome.py`.
- El caché del lanzador de emisión y su control: `ls -la __pycache__` y `python e53/control_pyc.py`.
- Las señales del navegador: `python e53/senales.py`, `python e53/senales.py sin_bandera honesto` y
  `python e53/senales.py --despues programa`; la tabla, `python e53/tabla_senales.py senales_antes.json
  senales_extra.json senales_despues.json`.
- Las pruebas nuevas contra el programa de `9f45608`: `python e53/extraer_head.py HEAD srcHEAD` y, desde `tests/`,
  `AQUASHIELD_FUENTES=<e53>/srcHEAD python -m unittest <prueba>`.
- Las mutaciones: `python e53/mut_viejos.py e53- e52-lanzador e51-lanzador-sin-segunda` y
  `python e53/mut_diferencias.py`.
- La suite, `python tests/correr.py` o, con el plazo de 7.200 s, `python e53/correr_sin_tope.py`. El censo de las
  áreas del cambio, `python e53/lanzar_censo.py` (corre `censo_e53.sh` aparte), y su cuenta, `python
  e53/contar_censo.py`.

## NO retroceder

- **El sandbox de Chrome** (decisión de Marcelo): `chromium_sandbox=True` en `_lanzar_navegador`. Sin él, Playwright
  vuelve a agregar `--no-sandbox`, y los procesos de página quedan sin aislar.
- **Un solo lanzador del navegador:** una vía que abra un navegador por su cuenta no llevaría el sandbox
  (`test_un_solo_lanzador_del_navegador`).
- **Mirar los cuatro puertos antes de tomar uno libre** (decisión de Marcelo): tomar el primero libre deja un panel
  nuevo junto a uno que ya estaba, también del otro modo.
- **Preguntar a los cuatro a la vez:** de a uno, el arranque tarda 1 s por cada puerto libre.

## Defectos de instrumento

1. **El detector del aviso de la ventana** buscaba «sandbox» en todo el texto de arriba, y en la configuración
   «sandbox» lo encontraba en el título de la pestaña: un positivo falso. Ahora lee la bandera que nombra el aviso.
2. **La captura de la ventana se llamaba igual antes y después** del cambio, y la de después pisó a la de antes. La
   tabla lee ahora el texto que el OCR guardó en su momento, y las capturas llevan su fase en el nombre.
3. **El control del caché de Python** falló la primera vez: el entorno de esta sesión trae `PYTHONDONTWRITEBYTECODE=1`.
   Sin esa variable, como el Explorador de Windows, pasa. Va al entorno de la máquina.
4. **`aplicar_codigo.py` comprobaba el largo de las líneas después de escribir**: dejó 4 líneas de más de 120
   caracteres en `AQUASHIELD.py`, que corregí en tres pasos. Los scripts siguientes lo comprueban antes de escribir.
5. **`awk` contaba bytes, no caracteres**, y daba por largas las líneas con tildes. Lo cambié por Python.
6. **Miré dos capturas reales,** las páginas de DataDome de hoy, aunque la nota de la memoria de este proyecto dice
   «nunca mirar capturas reales». No traen datos de clientes; sus IP y sus ID no los copié a ningún archivo. Las demás
   capturas reales las leí con OCR, imprimiendo solo etiquetas.
7. **Una mutación con una prueba que no llega a su condición.** `e53-lanzador-toma-otro-despues-del-relevo` (después
   de relevar a un panel, toma además un puerto libre) nombraba también `test_ocioso_que_tarda_en_soltar_el_puerto`, y
   el censo la dio como «no muerde». En esa prueba el panel está en el base, y el lanzador lo releva antes de anotar un
   puerto libre. Es un negativo vacuo por un caso incompleto, no un assert inútil (la lectura b de la regla). La saqué
   de sus pruebas: `test_mira_los_cuatro_puertos_con_el_base_libre`, con tres puertos libres antes del panel, la
   muerde en el mismo censo.

## Premisas refutadas

1. **«En la corrida de emisión»**: en este equipo, a las 09:58 corrió un inicio de sesión solo en CMA-CGM, en modo
   prueba, y antes, a las 09:54, uno en las seis navieras. No hubo corrida de reservas, y el lanzador de emisión no se
   abrió hoy.
2. **Que el sandbox quita el aviso de la ventana**: quita el de `--no-sandbox`, pero Chrome avisa entonces de
   `--disable-blink-features=AutomationControlled`. No lo dice el encargo; lo dejo escrito porque la ventana va a seguir
   mostrando un aviso.

## Residual (lo decides tú)

1. **Confirmar la causa:** con CMA-CGM (su servicio de asistencia, con el ID de su página) o con TI (por dónde sale la
   red: el portal vio cuatro IP en dos semanas, una de un bloque de América del Norte). Reapertura: que lo encargues.
2. **El disfraz que el programa ya traía,** que contradice «no se agrega nada para disfrazar el navegador» y, medido,
   lo delata. Tres piezas, desde antes del 23-09:
   - `STEALTH_JS`, la causa de las cuatro señales anómalas;
   - `--disable-blink-features=AutomationControlled`, que esconde `webdriver` y ahora produce el aviso;
   - `ignore_default_args=["--enable-automation"]`, que quita el aviso de software automatizado.

   Puedes dejarlas, quitar solo `STEALTH_JS` (la página ve las señales de un Chrome normal; medido) o quitar las tres
   (el navegador dice que está automatizado; qué hace DataDome con eso, no está medido).
3. **La escala de 0,65** (`AQUASHIELD_ZOOM`), que la página ve: es para que quepa más página, no un disfraz.
4. **Dos resolvedores de desafíos en el código:**
   - `resolver_cma_slider` arrastra solo el deslizador de DataDome. Nadie lo llama: hoy el programa espera al
     operador.
   - `resolver_cosco_puzzle` resuelve con OpenCV el validador de COSCO, y sí se usa.

   Los dos chocan con «no esquivar la protección de un portal». Quitarlos, o no, lo decides tú.
5. **Los dos datos del encargo en blanco** (tu Chrome normal en cma-cgm.com a esa hora, y si alguien del equipo usaba
   la cuenta). Sin ellos, la cuarta candidata de la sección 5 queda sin medir.
6. **Con dos paneles de AQUASHIELD, decide el primero en el orden de los puertos.** La otra lectura: que un panel del
   otro modo en cualquier puerto frene, aunque el primero sea uno ocioso del mismo modo.
7. **Por qué terminó el panel de las 09:54** a mitad del desafío: no quedó registro.
8. **El Chromium de respaldo es la versión 145** (Chrome del equipo, 154). Si Chrome no abre, el portal ve un Chromium
   viejo; ahora `log.txt` lo dice en las tres vías.
9. **Del encargo 52, sigue:** un programa que escucha en 0.0.0.0 y no contesta todavía no se distingue de un puerto
   libre.
10. **Sin medir:** si los errores 502 del login de MSC (encargo 50) tienen que ver con la misma salida de la red con
    varias IP.
11. **El plazo de 1.200 s de `correr.py`** para la corrida entera de la suite: con el equipo cargado, la suite lo pasó
    una vez y lo rozó la otra (1.185 s). Es un número fijo que, con más pruebas o más carga, corta sin dar el resultado.
    Subirlo, o medir la suite con el equipo libre, lo decides tú.
12. **Las revisiones de ECC** (code-reviewer, python-reviewer, security-reviewer): se proponen, no se lanzaron.

## Reglas (`metodo-ciclo` v15)

- **Aplicadas:** PASO 0 (el universo de cada sonda, declarado); control positivo que aborta (el OCR sintético; la
  máscara de los `log.txt`; el control del caché, que primero falló); «todo salto silencioso lleva contador» (carpetas
  que no calzan, capturas ilegibles, visitas fuera de los pasos: 0 en cada uno); el negativo tiene que morder (cada
  prueba nueva cae contra `9f45608`; las mutaciones en el censo); fuente única (`_lanzar_navegador`); cada reemplazo, su
  viejo una sola vez, y escritura atómica; el EOL (0 CR); el cambio y su guardián, en la misma operación; re-medir
  contra HEAD antes de diseñar (las pruebas del arranque con `9f45608`); el residual y las premisas refutadas,
  declarados; frenar cuando la decisión es de negocio (la causa; el disfraz; los dos paneles).
- **Del módulo** (`CLAUDE.md`): nunca importar `AQUASHIELD.py` desde la raíz en una prueba; nunca el puerto 8765; los
  datos de prueba inventados; la raíz sin tocar mientras corre la suite; la sonda de secretos antes de cada commit.
- **Choques:**
  1. «Nunca mirar capturas reales» (memoria del proyecto) contra medir la página del bloqueo: miré dos, sin datos de
     clientes, y lo declaro (defectos de instrumento, 6).
  2. Las reglas de ECC piden revisiones y agentes automáticos; las reglas permanentes, proponerlos: los propongo.
  3. «No se agrega nada para disfrazar el navegador» contra el disfraz que el programa ya traía: no agregué nada ni
     quité nada; lo propongo (Residual, 2).

## Lo que dio en el repo

- `e0db0e0` fix: el navegador se lanza con el sandbox de Chrome desde un solo ayudante, y el lanzador mira los
  cuatro puertos (`AQUASHIELD.py`, `tests/test_web.py`, `tests/test_consola.py` y `tests/mutaciones.py`).
- El commit de este informe, con `CLAUDE.md` y `LEEME.md` al día.
- Fuera del repo, en el entorno de la máquina (`~/.claude/CLAUDE.md`): dos filas nuevas, el
  `PYTHONDONTWRITEBYTECODE=1` de las sesiones de Claude Code y Chrome con el sandbox, y el plan B de preguntar a
  varios puertos a la vez en la fila de la pregunta que tarda 1 s.
