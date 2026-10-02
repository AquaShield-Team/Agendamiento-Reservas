# Encargo 45 · El login de MSC y la corrida del 01-10

**Base:** `C:\dev\Agendamiento Reservas` @ `7b33924` · árbol limpio.

La corrida del 01-10 usó el código de `503718b` (hoy en `historial-local`). Entre los dos, `login_msc`,
`reservar_maersk`, sus ayudantes, el panel y la consola son iguales: lo que cambió en el encargo 44 son los contratos,
COSCO y HYUNDAI (el diff de `AQUASHIELD.py` no toca esas secciones). Medido con `metodo-ciclo` v15.

**La corrida del 01-10** son dos carpetas de `logs/`: el modo login de las seis navieras (16:02:21 a 16:07:29) y la
corrida completa de la hoja CONSOLIDADO, con las filas 5 a 10 (16:07:44 a 16:14:20).

## En resumen

- **MAERSK:** la nave estaba. El programa la eligió y no pulsó su «Book», porque la tarjeta había quedado arriba de la
  ventana; después dijo que la nave «no está en los itinerarios», que es falso. Ningún plazo cortó el flujo. Es solo
  diagnóstico: el código de MAERSK no cambió.
- **MSC:** tu hipótesis de la espera se confirmó; la de la URL guardada, no; y la de la protección contra robots no se
  puede decidir con lo guardado. Con eso aplican tus tres decisiones (la primera ya se cumplía). Desde ahora, después
  del error, el login espera como mucho unos 30 s más, en lugar de 2 a 3 minutos y medio, y no vuelve a iniciar sesión.
- **ONE, CMA-CGM, COSCO y HYUNDAI:** armadas hasta su pantalla final, sin emitir.
- **La planilla del 01-10 no traía ninguna fila sin puerto de carga:** el panel no tenía nada que marcar.

## MAERSK (solo diagnóstico)

Una sola fila, la 10 de CONSOLIDADO.

| Pregunta | Respuesta medida |
|---|---|
| Paso en que se detuvo | «Select sailing», al pulsar el «Book» de la salida elegida |
| Estado y motivo | REVISAR · «me detuve en «Select sailing»: la nave '…' no está en los itinerarios (…)». El motivo es falso: la nave estaba |
| Origen elegido frente a su celda | La celda trae solo la ciudad. Eligió «ciudad, Chile», la única Container Yard con la forma de la regla: 34 sugerencias traían el prefijo, 1 era Container Yard |
| Destino elegido frente a su celda | La celda (destino final) trae solo la ciudad. Eligió «ciudad (ciudad), país»: sin el paréntesis, su parte antes de la coma es la ciudad. Era la única exacta: 3 sugerencias con el prefijo, 1 Container Yard |
| ¿La búsqueda trajo salidas? | Sí: 14 tarjetas después de dos «Search more sailing options», 13 con fecha (3, 11, 18 y 25-10) y 1 sin fecha ni «Book» |
| ¿La nave estaba? | Sí: en 3 tarjetas idénticas (las 7, 8 y 9), las tres del 18-10 y con su «Book». El programa las contó como una y eligió la 7 |
| Hasta qué fecha buscó | Hasta el 25-10-2026, la última salida cargada. No hacía falta más: la nave ya estaba |
| ¿Venció una espera antes de un clic? | No. Las tarifas cargaron en 6,3 s, las dos «Search more sailing options» se pulsaron a las 16:14:12 y 16:14:17, la lista con la nave se leyó a las 16:14:18, y el intento de pulsar el «Book» duró 0,1 s. La única espera vencida fue la de la carga del login (línea 386, «esperando 7.0s (carga) [sin señal]»), y siguió con «Ya había una sesión activa» |
| ¿Qué hizo después? | No cerró nada ni esperó: dejó la evidencia (`mk_f10_5_nave`, `mk_f10_detenida` y su HTML) y devolvió REVISAR |

Las líneas del log, con la nave tapada:

```
417 [16:14:18 + 394.0s]     3 tarjetas de la nave; 2 son copias de otra, con el HTML entero idéntico: cuentan como una sola salida (quedan 1)
418 [16:14:18 + 394.1s]     no pude pulsar el «Book» de la salida elegida
422 [16:14:19 + 394.4s] · Me detuve en «Select sailing»: la nave de la fila no está en los itinerarios de MAERSK.
423 [16:14:19 + 394.4s] · Reserva 1: REVISAR (MAERSK: me detuve en «Select sailing»: la nave '‹nave›' no está en los itinerarios (…))
```

**La causa es la segunda de las tres: la nave estaba y el programa no la eligió.** Más preciso: la eligió, pero no
pulsó su «Book».
- **El localizador sí encuentra el «Book».** Sobre el HTML guardado, el de `_mk_pulsar_book` da 2 en la tarjeta 7: el
  `mc-button` y su botón de adentro.
- **El filtro que lo descartó es la altura.** `_mk_pulsar_book` pulsa un «Book» solo si su borde de arriba está a más
  de 100 px del borde de arriba de la ventana, y lo mira antes de traerlo a la vista.
- **La captura de la ventana muestra la posición.** La tomada justo después (`mk_f10_5_nave`, 16:14:18) tiene a la
  vista fechas del 25-10 y ninguna del 18-10. Las tarjetas de la nave estaban más arriba, fuera de la ventana, que había
  quedado abajo, junto a «Search more sailing options».
- **Es la explicación más probable, no una medición:** la altura del botón en ese instante no se guarda. La apoyan la
  captura y que el localizador sí encuentra el botón.
- **El motivo queda mal por cómo se encadena.** Cuando no pulsa, `_mk_elegir_nave` devuelve lo mismo que «la nave no
  está» (`("", None, None)`), y `reservar_maersk` sigue por esa rama (`_mk_sin_nave`).

**Por qué apareció ahora.** La reserva de la fila 10 del 01-10 corrió por primera vez el 30-09 a las 15:31, con la
misma lista: 14 tarjetas, los mismos grupos de copias y la nave en las 7, 8 y 9. Ese día, las tres copias eran un empate
y la fila quedó NO ENVIADA. El encargo 43 las hizo contar como una sola y pulsar el «Book» de la primera (tu decisión).
La primera es la de más arriba, y quedó fuera de la ventana.

**Frente al 27-09.** La fila 10 del 27-09 era otra reserva: el mismo puerto de carga, pero otra nave y otro destino.
- **A las 21:15, su nave apareció tras un solo «Search more»,** en una sola tarjeta (la 6.ª de 6). El «Book» se pulsó, y
  la reserva se detuvo más adelante, en la revisión («no encontré la pantalla de revisión»).
- **A las 18:32 y 18:40,** el programa de entonces contaba el «Book» por su texto y no lo vio: «la salida pedida ya no
  se puede reservar». Eso se corrigió en el encargo 34.

**Lo que se podría hacer, y no se hizo** (el encargo pide solo el diagnóstico; queda en el residual):
- traer el «Book» a la vista antes de mirar su altura;
- que un «Book» que no se pudo pulsar dé su propio motivo («no pude pulsar el «Book» de la salida elegida»), y no el de
  la nave que no está.

## MSC

### Desde dónde parte el inicio de sesión

- **El código:** `login_msc` abre `https://www.mymsc.com/` (`_msc_abrir`), escribe el usuario, pulsa «Next» por su
  texto, escribe la clave y pulsa el botón de entrar por su texto. No hay ninguna URL de `/authorize` guardada: en el
  `AQUASHIELD.py` de `503718b`, `b2clogin` aparece solo en la sesión de COSCO, y `oauth2` y `nonce`, en ninguna parte.
  `_JS_MSC_LOGIN`, que pulsaría «Log in to myMSC», está definido y nadie lo usa.
- **`config.json`:** las credenciales de MSC traen solo usuario, clave y contrato. La única URL de inicio de sesión
  guardada es la `url` de MAERSK del primer operador: una página de `accounts.maersk.com` con `nonce` y
  `code_challenge` fijos, que el programa no lee. Solo leen `url` el login de HYUNDAI y el andamiaje `_login_portal`.
- **El perfil del navegador:**
  - `Preferences` no pide restaurar páginas al arrancar: `restore_on_startup` no está y `startup_urls` va vacío.
  - Los archivos de `Sessions` guardan 3 direcciones de `/authorize` de b2clogin, pero en el historial de pestañas, no
    para abrirlas.
  - En el historial (`History`, del 24-08 al 01-10), los 60 TriggerOidcLogin vinieron del «Next» o de una recarga del
    programa; ninguno se escribió.
  - Cada `/authorize` trae su propio `state` y su `nonce`: el 01-10, 9 visitas con `state` tienen 7 valores distintos,
    y las 2 repetidas son la vuelta de su propio `/authorize`.
- **El camino real** (historial del perfil):
  1. www.mymsc.com y la portada `/myMSC/`, con el campo del usuario;
  2. «Next» y `/myMSC/Account/TriggerOidcLogin`;
  3. `identityserver.msc.com/connect/authorize`, con su `state` y su `nonce`;
  4. `/Account/Login` y `/External/Challenge`;
  5. `mscciam.b2clogin.com/…/oauth2/v2.0/authorize`, que pide la clave;
  6. «confirmed»: b2clogin aceptó las credenciales;
  7. la vuelta a `identityserver.msc.com/signin-aad-b2c` (el `redirect_uri` de las 55 direcciones de b2clogin), y de
     ahí `/External/Callback` y `/connect/authorize/callback`;
  8. la vuelta a myMSC (`redirect_uri` `https://www.mymsc.com/mymsc/`): `/myMSC/Account/OidcLoginCallBack` y
     `/myMSC/welcome`.

### Las tres hipótesis

**1. La URL de `/authorize` con `state` y `nonce` fijos: se descartó.**
- **Ni el código, ni `config.json`, ni el perfil hacen partir el login de una URL guardada** (arriba).
- **Cada inicio de sesión generó su `state` y su `nonce` en la misma sesión.**
- **identityserver no rechazó la vuelta a `/signin-aad-b2c`:** las 54 veces que b2clogin aceptó las credenciales, el
  historial sigue con `/External/Callback` y `/connect/authorize/callback`.
- **Lo que falla es el salto siguiente, a www.mymsc.com.** La página de error de Chrome lo nombra en las 3 capturas
  legibles que la muestran (OCR): «www.mymsc.com no puede procesar esta solicitud».

**2. La espera de unos 5 minutos: se confirmó.**
- **En la corrida completa,** el inicio de sesión de MSC tardó 73 s.
  - El primer intento falló a las 16:08:46, en la vuelta a myMSC, y el programa lo reconoció a las 16:08:56, después
    de tres vueltas de 3 s.
  - Al reintentar, la sesión llegó a las 16:09:06, sin pedir la clave: el historial dice OidcLoginCallBack y welcome.
  - El programa siguió hasta las 16:09:46 esperando el campo de la contraseña (15 s), queriendo escribirla (12 s),
    buscando el botón de entrar (5 s) y asentando (5 s).
  - La captura `msc_paso_email`, de las 16:09:24, muestra myMSC con la sesión iniciada (OCR). Lo mismo el 27-09 y el
    29-09.
- **En el modo login,** tardó 214 s (16:02:36 a 16:06:11).
  - El error llegó a las 16:02:51, en la vuelta a myMSC. Siguieron tres vueltas de 3 s y dos reintentos completos, de
    unos 100 y 90 s, casi todo esperando campos que no estaban: el usuario 12 s, el «Next» 5 s, la contraseña 15 y
    12 s, el botón 5 s, el asiento 5 s y otra vez tres vueltas de 3 s.
  - Terminó diciendo «Sesión iniciada.» sobre la página de error del propio MSC: «unable to complete your request»
    sale, por OCR, en `msc_paso_email` (16:05:48) y en `msc_final` (16:06:11), y el historial no tiene vuelta a myMSC
    después de las 16:02:51.
  - `_msc_logueado` tomaba como sesión cualquier página de mymsc.com sin el formulario.
  - Es lo que viste a las 16:05.
- **Qué esperaba cada plazo, en el código de `503718b`:**

| Paso | Espera | Qué esperaba |
|---|---|---|
| Abrir myMSC | `goto` (30 s de Playwright) y hasta 6 s | Un campo de texto |
| Usuario | hasta 12 s | `#UserName` o `input[type=email]` |
| «Next» | hasta 5 s, y 3 s fijos | El botón por su texto |
| Contraseña | hasta 15 s | `input[type=password]` |
| Si veía el 502 ahí | 3 s, recarga, 4 s, y otra vez usuario, «Next», 3 s y contraseña | Lo mismo |
| Escribir la clave | hasta 12 s | `input[type=password]` |
| Botón de entrar | hasta 5 s | Login, Sign In, Next o Iniciar |
| Asentar | hasta 5 s | Un enlace a eBooking o welcome, o un `nav` |
| Verificar | 3 vueltas de 3 s | Que no se vea el formulario |
| Reintentos | hasta 2 más, con 3 s entre cada uno | Todo lo anterior otra vez |

  Ninguna de esas esperas miraba si ya había llegado la sesión o el error.

**3. La protección contra robots: lo guardado no permite decidirlo.**
- **Lo que hay:**
  - las cookies del perfil son de Akamai (`ak_bmsc`, `AKA_A2`) y de Citrix NetScaler (`citrix_ns_id…`) en
    `.mymsc.com`, y de Cloudflare (`__cf_bm`) en `assets.msc.com`;
  - la página de error de Chrome nombra a www.mymsc.com;
  - no se guarda el estado, las cabeceras ni el cuerpo de la respuesta que falla.
- **Lo que pesa, sin probar nada:**
  - con el mismo perfil y el mismo lanzamiento, antes del 21-09 las 35 tandas del historial con TriggerOidcLogin
    llegaron a myMSC en su primera pasada; desde el 21-09, 10 de 16, y una vez más TriggerOidcLogin ni respondió;
  - después de una falla en la vuelta a myMSC, la pasada siguiente entró sin pedir la clave en 3 de los 6 inicios de
    sesión con esa falla, y en uno más a la tercera. Cada una tardó de 3 a 5 s.
- **Lo que faltaría para decidirlo:**
  - la respuesta que falla, con su estado, sus cabeceras y su cuerpo. Una traza de Playwright con la red serviría, pero
    `AQUASHIELD_TRAZA=1` solo la graba en las reservas por consola, no en el panel ni en el modo login;
  - un login a mano en un Chrome normal, en el mismo momento en que falla el del programa;
  - y, para mirar el lado de `--no-sandbox`, una corrida sin esa bandera. **Las tres exigen abrir el portal o cambiar
    cómo se lanza el navegador: FRENA SI, no se hizo.**

### Cuánto tardó el inicio de sesión de MSC en cada corrida

Las 15 de `logs/`, cruzadas con el historial del perfil:
- «Pasadas» son los intentos dentro de un mismo inicio de sesión, separados por cada vuelta del programa a
  www.mymsc.com.
- «502 en TriggerOidcLogin» es el error tras el «Next».
- «Vuelta a myMSC» es el salto de identityserver a www.mymsc.com.

| Fecha | Modo | Segundos | El programa dijo | Lo que dice el historial | ¿Había sesión? |
|---|---|---:|---|---|---|
| 21-09 15:02 | panel | 55 | No confirmé la sesión | falla en TriggerOidcLogin (502) | no |
| 21-09 16:31 | panel | 66 | Sesión iniciada | sesión, tras recargar el 502 de TriggerOidcLogin | sí |
| 24-09 18:46 | panel | 65 | Sesión iniciada | sesión, tras recargar el 502 de TriggerOidcLogin | sí |
| 25-09 00:30 | panel | 22 | Sesión iniciada | sesión | sí |
| 25-09 13:48 | panel | 24 | Sesión iniciada | sesión | sí |
| 26-09 14:14 | panel | 67 | No confirmé la sesión | falla en la vuelta a myMSC, tras recargar el 502 | no |
| 26-09 14:20 | panel | 22 | Sesión iniciada | sesión | sí |
| 27-09 18:27 | login | 122 | Sesión iniciada | falla en la vuelta, tras recargar el 502 → sesión | sí |
| 27-09 18:33 | panel | 177 | Sesión iniciada | falla en la vuelta → falla en TriggerOidcLogin → sesión | sí |
| 29-09 15:00 | login | 81 | Sesión iniciada | falla en la vuelta → sesión | sí |
| 29-09 15:04 | panel | 24 | Sesión iniciada | sesión | sí |
| 30-09 15:11 | login | 21 | Sesión iniciada | sesión | sí |
| 30-09 15:22 | panel | 64 | Sesión iniciada | sesión, tras recargar el 502 de TriggerOidcLogin | sí |
| 01-10 16:02 | login | 214 | **Sesión iniciada** | falla en la vuelta → falla tras TriggerOidcLogin, dos veces | **no** |
| 01-10 16:08 | panel | 73 | Sesión iniciada | falla en la vuelta → sesión | sí |

- **Sin error, tardó de 21 a 24 s** (5 de 15). **Con error, de 55 a 214 s** (10 de 15). El más largo es de 3 min 34 s;
  el modo login completo del 01-10, con las seis navieras, duró 5 min 8 s.
- **Errores:**
  - 8 inicios de sesión tuvieron el 502 tras el «Next»;
  - 6 tuvieron la falla de la vuelta a myMSC;
  - ninguno pidió una validación (captcha).
- **No logró entrar en 3** (21-09 15:02, 26-09 14:14 y 01-10 16:02). En el último, el programa dijo lo contrario.
- **El programa reconocía la página de error de Chrome** (por «502» o «no puede procesar»), **pero no la del propio
  MSC**: con ella esperaba hasta vencer cada plazo, y al final la daba por sesión.
- **La clave se escribió una sola vez en 14 de los 15 inicios de sesión, y ninguna en 1:** los reintentos nunca la
  volvieron a enviar, porque el campo no apareció.

### Frente a las otras cinco navieras

Medido en los `log.txt` de `logs/` (28 carpetas, 0 sin log). Va del encabezado del login de cada naviera a su línea de
resultado.

| Naviera | Logins | Segundos (mín · mediana · máx) | 01-10, modo login | 01-10, corrida completa |
|---|---:|---|---:|---:|
| ONE | 17 | 4 · 11 · 33 | 14 | 4 (ya había sesión) |
| **MSC** | 15 | **21 · 65 · 214** | **214** | **73** |
| CMA-CGM | 15 | 14 · 24 · 108 | 37 | 15 |
| COSCO | 16 | 26 · 30 · 40 | 29 | 26 |
| HYUNDAI | 14 | 4 · 5 · 10 | 4 | 4 |
| MAERSK | 18 | 2 · 7 · 8 (siempre con la sesión ya iniciada) | 8 | 8 |

### Lo de CMA o COSCO: credenciales y página forzada

No hay registro de cuándo se hizo: la mayoría está en el código desde el primer commit (`14aa9ef`, 23-09). Lo que hay:
- **COSCO** va directo al tablero (`/ebusiness/Dashboard`); si la sesión sigue, no inicia sesión.
  - Reconoce la sesión por el nombre con que el portal muestra al operador (`nombre_en_pantalla`, agregado a sus
    credenciales en `config.json` el 25-09, `CICLO-cola-cuatro-items.md`) o por «aquachile» junto a «logout».
  - Su última espera termina apenas ve la sesión: hasta 240 s, mirando cada 3 s.
- **HYUNDAI** abre la página de login que dicen sus credenciales (la llave `url`), si la traen.
- **MAERSK** va directo a la página protegida `/book/`. La `url` de sus credenciales no se usa.
- **CMA** no tiene nada de eso.

**Si aplica a MSC:**
- **Lo de forzar la página ya lo hacía:** abre www.mymsc.com y mira primero si hay sesión.
- **Lo que COSCO tiene y MSC no:** reconocer la sesión por algo que la prueba, y una espera que termina apenas llega.
  Eso es lo que agrega el cambio, por la página (`/myMSC/welcome`), sin tocar las credenciales.
- **Guardar una URL de `/authorize`, como la `url` de MAERSK, no serviría:** `state` y `nonce` son de un solo uso. Y el
  `redirect_uri` no se cambia.

### El aviso de `--no-sandbox`

- **Sale de Playwright, no del programa.** En Playwright 1.58.0, `lib/server/chromium/chromium.js` hace
  `if (options.chromiumSandbox !== true) chromeArguments.push("--no-sandbox")`.
- **El programa nunca lo pide:** lanza el navegador sin `chromium_sandbox` en sus tres `launch_persistent_context`
  (modo login, reservas por consola y panel), y `_args_chrome()` no agrega esa bandera.
- **Chrome muestra el aviso por esa bandera.** Quitarla es cambiar cómo se lanza el navegador: lo decides tú.

### El cambio: tus tres decisiones

1. **«El inicio de sesión parte de la página de MSC, con su botón de entrar identificado por su texto, nunca de una URL
   guardada»: ya se cumplía.** No cambió nada de eso.
2. **«La espera termina con el éxito o con el error, lo que llegue primero».**
   - **`_msc_esperar`** mira la página cada 0,5 s, hasta 60 veces (unos 30 s), y termina con lo primero que llega: la
     sesión, el error o el campo siguiente.
   - **El tope es una hipótesis:** 3 veces lo más largo medido. Desde que b2clogin acepta la clave hasta la vuelta a
     myMSC pasan de 2 a 10 s en 48 pasadas; sin b2clogin, de 3 a 5 s en 4.
   - **La sesión se reconoce por su página** (`_msc_sesion`): `/myMSC/welcome`, donde terminan las 53 vueltas a myMSC
     del historial, o eBooking.
   - **El error se reconoce por la página de error de Chrome** (su dirección `chrome-error://`, o sus textos «502» y «no
     puede procesar»), **o por la del propio MSC** («unable to complete your request»).
   - **Ninguna de las 9 capturas legibles de myMSC con sesión trae «502» en su texto.** Igual la sesión se mira antes
     que el error.
3. **«Ante el error, una sola navegación a la página del portal desde la que sigue el programa…».**
   - `_msc_tras_el_error` lo dice en el log, deja `msc_error`, va una vez a eBooking (`MSC_EBOOKING`, la página que
     `reservar_msc` abre primero, ahora con la misma constante) y espera la sesión, el error o el formulario de login.
   - Solo la sesión cuenta. Sin ella, `login_msc` devuelve falso y no hay otro intento: `MSC_REINTENTOS_502` y la
     recarga tras el «Next» salieron.
   - El panel y la consola dejan cada fila de MSC NO ENVIADA con el motivo `MSC_SIN_SESION`: «no quedó iniciada la
     sesión de MSC: la reserva no se envió, y el inicio de sesión no se reintentó, para no arriesgar la cuenta (el
     detalle, en log.txt)».
   - Con las otras navieras, un login fallido sigue como antes: la fila queda sin estado.

**Lo que tienes que saber antes de usarlo:**
- **Los reintentos sí servían.** De los 10 inicios de sesión con error, 7 terminaron con la sesión gracias a la recarga
  o a los reintentos, y ninguno volvió a enviar la clave.
- **Con tu regla, esos casos dependen de que la ida a eBooking deje la sesión, y eso no está medido.** Si no la deja,
  la fila de MSC queda NO ENVIADA.
- **Las primeras corridas lo van a decir.** En `log.txt`, la línea «⚠ MSC mostró una página de error…» y lo que sigue;
  en el historial del perfil, si aparece OidcLoginCallBack después de eBooking.

### Lo que vigila el cambio

`test_error_502` y `test_login_reintenta_tras_un_502` salieron con el comportamiento que vigilaban, y sus 12 mutaciones
también. Las pruebas nuevas:

| Prueba | Qué vigila |
|---|---|
| `test_clics.TestMsc.test_error_del_portal` | Las dos páginas de error, por dirección y por texto, y que una página ilegible no sea el error |
| `test_clics.TestMsc.test_sesion_solo_en_su_pagina` | La sesión solo en `/myMSC/welcome` y eBooking de www.mymsc.com; nunca en la portada, en la página de error de MSC, en identityserver ni en b2clogin |
| `test_clics.TestMsc.test_login_termina_con_lo_primero_que_llega` | Cada espera termina apenas llega la sesión o el campo, el tope es de 30 s, la sesión previa no escribe nada y la validación pausa una vez |
| `test_clics.TestMsc.test_ante_el_error_va_una_vez_a_ebooking_y_no_reintenta` | Un solo `goto` a eBooking, ningún usuario ni clave de nuevo, y sin sesión no la da por iniciada |
| `test_web.TestPanelCorridas.test_login_fallido_de_msc_queda_no_enviada` | La fila de MSC NO ENVIADA con su motivo, en el panel |
| `test_consola.TestEjecutarReservas.test_login_fallido_de_msc_queda_no_enviada` | Lo mismo en la planilla, con su copia de respaldo |

- **Las tres pruebas del login fallido de otra naviera pasaron de MSC a ONE y HYUNDAI.** Siguen vigilando lo de antes:
  la fila queda sin estado y la planilla no se toca.
- **`test_login_sin_clic_generico` mira las funciones nuevas.**
- **Cada prueba nueva tiene sus mutaciones:** 27 nuevas.
- **La compuerta, antes del commit:** primero en una copia del repo y después en la raíz.
  - La suite dio 563 pruebas OK (en la raíz, 283 s) y 0 cambios en los archivos reales.
  - El censo filtrado mató todas las mutaciones de sus cuatro filtros: las pruebas de MSC, 67; el login fallido, 5; las
    escrituras sin respaldo, 1; la fila sin sesión, 3. 0 pruebas quedaron sin mutación.
- **El censo completo sobre `c0148f8`:** 1668 mutaciones en 2003 pares con las 563 pruebas: todas muerden,
  0 pruebas sin mutación y 0 cambios en los archivos reales (del 01-10 a las 23:26 al 02-10 a la 01:00, 94 min).
- **`test_candado` no cambió.**

## ONE, CMA-CGM, COSCO y HYUNDAI

- **ONE (fila 5):** OK-EJEMPLO, armada hasta Review, sin emitir. La sesión ya estaba iniciada (4 s).
- **CMA-CGM (fila 7):** OK-EJEMPLO, armada hasta «Envío de la reserva». Dejó el aviso «el portal no respondió a
  «Validar ruta»» y siguió sin darla por validada. El login tardó 15 s.
- **COSCO (fila 8):** OK-EJEMPLO, armada hasta Booking Details. El puzzle se resolvió solo y el login tardó 26 s.
- **HYUNDAI (fila 9):** OK-EJEMPLO, armada hasta Review & Book. Marcó en «Alternate Vessel Option» que no quiere otra
  nave, y el login tardó 4 s.

## La fila sin puerto de carga

La planilla del 01-10 (la copia que el panel guardó a las 16:02) no traía ninguna:
- CONSOLIDADO tiene 6 filas, de la 5 a la 10, y otra hoja trae 30;
- con la regla del programa (`_con_su_marca` sobre `leer_filas`), 0 quedan sin puerto de carga, 0 sin destino y 0 sin
  nave;
- ninguna fila con algo escrito queda fuera del lector.

El panel no tenía nada que marcar. Que lo marca lo vigila `test_web.test_filas_dicen_si_traen_la_ruta` (encargo 43); en
el portal no se vio.

## Re-medir

Todo corre desde `scratchpad\e45`, en Git Bash, después de `source entorno_e45.sh` (`TMPDIR`, `TEMP` y `TMP` dentro de
la carpeta), con `python3.13`. Ningún script imprime valores.

| Número | Script |
|---|---|
| Carpetas de `logs/` | `python3.13 corridas.py 20260927` |
| Cada log, con la máscara (operador, credenciales, contratos, naves, viajes, reservas, ciudades) | `python3.13 ver_log.py <AAAAmmdd_HHMMSS> [desde] [hasta] [regex]`; su control, `python3.13 control_mascara.py` |
| Cada login de las seis navieras | `python3.13 logins.py MSC` |
| El perfil: Preferences, Sessions, History, Cookies | `python3.13 perfil_msc.py 2026-10-01` |
| Las tandas del historial | `python3.13 historial_msc.py` |
| Logins de `logs/` frente al historial | `python3.13 msc_tabla.py` |
| La vuelta de b2clogin y la de identityserver | `python3.13 redirect_msc.py` |
| Las claves escritas por login | `python3.13 claves_msc.py` |
| Antes y después del 21-09; los logins del 01-10 | `python3.13 resumen_extra.py` |
| Los tiempos de cada paso; el «502» en las capturas con sesión | `python3.13 tiempos_msc.py` |
| OCR de las capturas del login de MSC | `python3.13 ocr_msc.py` |
| La lista de MAERSK sin red, y el origen y el destino | `python3.13 mk_sonda.py` |
| OCR de la ventana de MAERSK | `python3.13 ocr_mk.py 20261001_160744 20260930_153126 20260927_211531` |
| Las marcas de la planilla | `python3.13 planilla_marcas.py` |
| La suite y el censo | `bash gate.sh <etiqueta> <filtros…>`; `bash censo.sh` |

## NO retroceder

- **La sesión de MSC se reconoce por su página, no por la ausencia del formulario:** la ausencia dio por iniciada una
  sesión que no existía.
- **El error se reconoce también por la página de error del propio MSC:** sin eso, el programa esperaba hasta el tope
  sobre ella.
- **Tras el error del login de MSC no hay reintentos:** es tu decisión, por el riesgo de bloquear la cuenta. Si se
  quiere volver a reintentar, se decide con lo que midan las próximas corridas.

## Defectos de instrumento que me cacé

- **La máscara no veía las naves que muestra el portal y la planilla no trae** (la de un transbordo de COSCO). Una salió
  en una salida de herramienta de esta sesión, no en el informe. Se agregaron los patrones de nave y de viaje del
  portal.
- **El filtro de `ver_log.py` corría sobre la línea sin su número,** así que daba 0 líneas. Se corrigió.
- **Para listar las capturas del login excluí `msc_f*`, que también dejaba fuera `msc_final`:** daba 6 en vez de 21. Se
  cambió por `msc_f<número>_`.
- **Cuatro scripts corrían su `main()` al importarse.** Se les puso la guarda.
- **En la prueba de la consola esperé las filas 5 a 7, y el lector de la consola da también la 8:** el encabezado
  repetido de la hoja sintética, como fotografía `test_planilla`. Se ajustó la prueba, no el lector.
- **El `goto` de la página falsa dejaba la página de error a la vista,** y la espera terminaba con el error. El real
  termina en la página que carga; la falsa ahora también.

## Premisas del encargo que se refutaron

- **«La fila 10 del 27-09 sí encontró su nave»:** era otra reserva, con otra nave y otro destino. La del 01-10 corrió
  antes solo el 30-09 a las 15:31, y quedó NO ENVIADA por el empate de las tres copias.
- **«Los 5 minutos»:** el inicio de sesión de MSC más largo de `logs/` tardó 214 s (3 min 34 s). Lo más cercano a 5
  minutos es el modo login completo del 01-10, con las seis navieras (5 min 8 s).
- **La hipótesis de la URL guardada:** se descartó (arriba). La vuelta a `/signin-aad-b2c` sí es la de b2clogin, e
  identityserver la aceptó las 54 veces.
- **«El programa queda esperando después de aceptar el inicio de sesión»:** queda esperando, pero sobre todo en los
  reintentos. La espera tras el error en sí era de 9 a 10 s; lo largo eran las dos vueltas completas que seguían.
- **No llegaron las capturas que adjuntaste:** en el mensaje hay solo texto. Se usaron las del programa (`msc_*.png`).

## Residual

| Qué | Por qué no se hizo | Se reabre si |
|---|---|---|
| MAERSK: traer el «Book» a la vista antes de mirar su altura, y que un clic que no sale tenga su propio motivo | El encargo pide solo el diagnóstico | Lo encargas |
| MAERSK: cuál de las copias idénticas pulsar | Es tu decisión del encargo 43 (la primera); con el arreglo de arriba, la primera serviría | Lo encargas |
| Si la ida a eBooking deja la sesión tras el error | No se mide sin el portal | Las próximas corridas: `log.txt` e historial |
| La protección contra robots | Falta la respuesta que falla y un control a mano (FRENA SI) | Corres tú, con la traza o con un login a mano en paralelo |
| La traza de Playwright solo existe en las reservas por consola | Fuera del encargo | Lo encargas, para medir el punto anterior desde el panel |
| `--no-sandbox` | Cambiar cómo se lanza el navegador lo decides tú | Lo decides |
| El tope de 30 s del login de MSC | Hipótesis: 3 veces lo más largo medido | Una corrida lo mide distinto |
| La fila NO ENVIADA sin sesión, para las otras cinco navieras | Tu decisión fue para MSC | Lo decides |
| La `url` de MAERSK en `config.json`, con su `nonce` fijo, que el programa no usa | Es tu `config.json` | Decides borrarla |
| `_JS_MSC_LOGIN`, definido y sin uso | Fuera del encargo | Lo encargas |
| El lector de la consola lee el encabezado repetido como una fila | Ya estaba fotografiado | Lo encargas |

## Reglas de método aplicadas

`metodo-ciclo` v15, con las reglas permanentes de `~/.claude/CLAUDE.md`:
- **Todo salto silencioso lleva contador:** 28 carpetas y 0 sin log; 21 capturas y 7 ilegibles; 15 de 15 logins con su
  tanda en el historial.
- **Control positivo que aborta:** la máscara, el OCR, la lista sintética de MAERSK, el grupo [7, 8, 9] del 30-09 y el
  control del 01-10 en el cruce con el historial.
- **El negativo tiene que morder:** el censo filtrado y el completo.
- **Todo registro es una hipótesis:** se re-midió cada número heredado, y así se refutaron las premisas de arriba.
- **Re-medir contra HEAD; el residual; las premisas refutadas; fuente única:** `MSC_EBOOKING`, para el login y
  `reservar_msc`.
- **El cambio y su guardián, en la misma operación.**
- **Frenar si la decisión es de negocio:** los arreglos de MAERSK, `--no-sandbox` y la traza.
- **Lo que está fuera del encargo se propone:** los arreglos de MAERSK, la traza en el panel y lo demás del residual.
  Entraron, por estar ligados a tu tercera decisión, la fila NO ENVIADA también en la consola y una nota en `LEEME.md`
  para el operador.
- **Todo entregable declara su base:** la primera línea.

**Choques, y cómo se resolvieron:**
- **Leer el perfil del navegador.** Este encargo lo pide, y en el anterior no se leía `perfiles/`. Se leyó solo para
  medir, sin abrir claves, formularios ni valores de cookies, con las bases en modo inmutable.
- **Leer la copia de la planilla en el temporal de Windows,** fuera de la carpeta del encargo: solo lectura, sin
  copiarla.
- **Los agentes que pide ECC no se lanzaron:** se proponen. Una revisión del cambio por un subagente, en un clon dentro
  de la carpeta del encargo, queda a tu decisión.

## Lo que dio en el repo

- `c0148f8` fix(msc): el login termina cada espera con la sesión o el error, y no reintenta;
- y el de este informe, con `CLAUDE.md` y `LEEME.md` al día.

El push lo haces tú. Los comandos, con el hash esperado, van en el mensaje final del encargo: este informe va
dentro del commit y no puede citar su propio hash.
