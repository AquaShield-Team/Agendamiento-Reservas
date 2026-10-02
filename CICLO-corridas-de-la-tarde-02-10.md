# Encargo 49 · Las corridas de la tarde del 02-10: el inicio de sesión de MSC y la pantalla final de cada naviera

**Base:** `C:\dev\Agendamiento Reservas` @ `46eb63d` · árbol limpio.

Solo diagnóstico, medido con `metodo-ciclo` v15 sobre lo guardado en `logs/` y en el historial del perfil del programa.
No cambié código ni abrí ningún portal. Las corridas de la tarde, las tres sobre `46eb63d`:

| Corrida | Carpeta | Qué pasó |
|---|---|---|
| «Solo iniciar sesión», las seis navieras | `…_20261002_164745`, de 16:47:45 a 16:49:31 | Las seis en un mismo Chrome; MSC quedó REVISAR |
| Las seis reservas | `web_todas_…_20261002_165010`, de 16:50:10 a 16:55:38 | ONE, CMA-CGM, COSCO, HYUNDAI y MAERSK llegaron a la guarda; MSC quedó NO ENVIADA |
| Solo MSC | `web_todas_…_20261002_165608`, de 16:56:08 a 16:57:03 | MSC llegó a la guarda |

La planilla es la copia que guardó el panel a las 16:50:03, igual byte a byte a `Reservas AQUASHIELD.xlsx` (del 30-09):
la hoja CONSOLIDADO, filas 5 a 10, una por naviera, las seis con nave, viaje y contrato. No trae columnas de
contenedor, temperatura, peso ni día de carga, así que el programa usa «40 HC REEFER» y 1 contenedor, y la temperatura
y el peso de `config.json` (−20 °C y 22 500 kg).

## En resumen

- **MSC, en la corrida de las seis:** no hubo 502 tras el «Next». El usuario y la clave pasaron, b2clogin e
  identityserver los aceptaron, y el 502 llegó después, en la vuelta a myMSC. La recarga del encargo 47 no actuó,
  porque es solo para el error tras el «Next». La ida única a eBooking llevó a la portada, sin la sesión, y la fila
  quedó NO ENVIADA. El inicio de sesión tardó 16,6 s.
- **Solo MSC, cinco minutos después:** la vuelta a myMSC funcionó, el inicio de sesión tardó 18,2 s y la reserva llegó
  a la guarda.
- **«Solo iniciar sesión» no dejó la sesión de MSC:** su MSC falló igual, en la vuelta a myMSC. Que haya hecho fallar
  al siguiente no se ve en los números; confirmarlo exige el portal.
- **Las seis pantallas finales calzan con su fila** en la nave, el viaje, el destino, el contenedor, la temperatura, el
  peso y el commodity. Hay dos diferencias, y las dos son reglas del programa que decides tú:
  - **COSCO armó la reserva desde otro puerto de carga:** el de su fila está en `MAPA_PUERTOS_COSCO`, que lo traduce a
    otro (el mismo de las filas de CMA-CGM y HYUNDAI).
  - **ONE declara «FISH FILLET,MEAT FRE/CHI/FRO, SALMONIDAE»,** la primera sugerencia que trae «SALMON». MSC, CMA-CGM y
    COSCO declaran salmón del Atlántico entero congelado (HS 030313).
- **Lo que la pantalla final no muestra** lo comprobé en una captura anterior o en `log.txt`: la temperatura y el peso
  de ONE, COSCO y HYUNDAI (la temperatura de HYUNDAI, solo en `log.txt`), el commodity de COSCO, y la nave y el viaje
  de MAERSK.
- **MAERSK eligió el 13-10 como fecha de retiro.** Hoy es viernes 02-10, y el primer día hábil después es el lunes
  05-10, que no estaba habilitado. Estaban habilitados del 12 al 16, y el 12 es feriado. El lector del calendario del
  encargo 48 funcionó en el portal.

## MSC

### Los tres inicios de sesión de la tarde

| | «Solo iniciar sesión» (16:48) | Las seis reservas (16:50) | Solo MSC (16:56) |
|---|---|---|---|
| Duración, de «Login MSC» al desenlace | 18,7 s | 16,6 s | 18,2 s |
| El «Next» | Pasó: el campo de la clave apareció 2,8 s después | Pasó, 2,7 s después | Pasó, 2,2 s después |
| ¿502 tras el «Next»? | No | No | No |
| La clave | Escrita una vez; b2clogin la aceptó | Igual | Igual |
| La vuelta a myMSC | 502, 4,1 s después del botón de entrar | 502, 3,8 s después | Funcionó: `/myMSC/welcome`, 6,9 s después |
| ¿Actuó la recarga del encargo 47? | No | No | No hizo falta |
| Lo que siguió | La ida única a eBooking, que llevó a la portada | Igual | La reserva |
| Desenlace | REVISAR (es el modo de solo login) | **NO ENVIADA**, con `MSC_SIN_SESION` | Llegó a la guarda a las 16:57:02 |

- **De dónde sale cada paso:**
  - el `log.txt` de cada corrida;
  - el historial del perfil, que guarda cada navegación con su hora. En los dos inicios fallidos trae la aceptación de
    la clave en b2clogin y la vuelta a identityserver, y no trae la vuelta a myMSC (`OidcLoginCallBack`): Chrome no
    guarda una navegación que terminó en su página de error. En el que funcionó, la vuelta a myMSC llegó 4 s después
    de la de identityserver, y siguió `welcome`;
  - las capturas, por OCR y sin mirarlas. En las dos corridas fallidas, `msc_error` dice «Esta página no funciona», «La
    página www.mymsc.com no puede procesar esta solicitud ahora» y «HTTP ERROR 502». `msc_final` dice «Welcome to
    myMSC» y «No account yet? Sign Up Now»: es la portada, con el formulario y sin la sesión.
- **Qué la dejó NO ENVIADA:** el 502 en la vuelta a myMSC, después de la clave. Ante ese error, el programa hace lo que
  decidiste en el encargo 45: va una sola vez a eBooking, no vuelve a iniciar sesión y, sin la sesión, deja la fila NO
  ENVIADA. No es una regresión.
- **La recarga del encargo 47 sigue sin probarse en el portal:** solo actúa con el error tras el «Next», y esta tarde
  ese error no salió.

### La ida a eBooking, medida

Ya son cuatro las veces que la ida única a eBooking siguió a un error, y las cuatro llevó a la portada sin la sesión:
las dos de la mañana (tras el 502 del «Next», encargo 47) y las dos de esta tarde (tras el 502 de la vuelta). Lo único
medido que rescató la sesión tras un 502 en la vuelta fue la pasada siguiente del código de antes del encargo 45. Esa
pasada volvía a escribir el usuario y a pulsar «Next», e identityserver, que todavía tenía la sesión, no pidió la clave:
así entró en 3 de los 6 inicios de sesión con esa falla, y en uno más a la tercera pasada (encargo 45). Es otro intento
de inicio de sesión, que decidiste no hacer, así que queda en el residual.

### ¿Influyó haber usado «Solo iniciar sesión» antes?

- **No dejó una sesión que sirviera:** su MSC falló igual, en la vuelta a myMSC. «Solo iniciar sesión» entra a las seis
  navieras en un mismo Chrome y lo cierra 6 s después de terminar. La corrida de las reservas abre otro Chrome para
  cada naviera, con el mismo perfil. A los 2 min 25 s, el MSC de la corrida volvió a pedir el usuario y la clave.
- **Que lo haya hecho fallar no se ve en los números.** Esto dice el historial del perfil sobre los 15 inicios de
  sesión de MSC desde el 26-09, clasificados por cómo terminó su primera pasada (un 502 recargado cuenta como falla):

  | Antes del inicio de sesión | Cuántos | Fallaron |
  |---|---:|---:|
  | Más de una hora sin MSC (el primero de cada tanda) | 7 | 6 |
  | Un «Solo iniciar sesión», de 2 a 12 min antes | 6 | 5 |
  | Una corrida del panel, 4 o 5 min antes | 2 | 0 |

  El primero de cada tanda falla casi siempre, venga o no de un «Solo iniciar sesión». Los dos que vinieron tras una
  corrida del panel entraron; uno es el de esta tarde. Son pocos para separar una causa, y antes del 21-09 los 35
  entraron en su primera pasada, con cualquier pausa. Confirmarlo exige el portal: es el FRENA SI, y no lo hice.

## Las seis pantallas finales

**Cómo se comparó.** La pantalla final es la de la guarda: `<nav>_f<fila>_guarda.html` (la página y sus marcos) y su
captura. Cada HTML se cargó en un Chromium sin red y sin el JavaScript de la página. Cada campo se leyó por su etiqueta
y se comparó con la fila usando las funciones del programa:
- la nave, con todas sus palabras, cada una como palabra entera (`_trae_la_nave`);
- el viaje, como palabra entera (`_palabra_en`);
- el puerto y el destino, por la ciudad (la parte antes de la coma), sin tildes ni signos (`_norm_ctrl`).

A veces la pantalla final no trae un campo, o su HTML no guarda lo escrito en un campo de texto. Entonces la tabla dice
de dónde sale el dato: una captura anterior de la misma reserva (por OCR, sin mirarla) o `log.txt`. Fueron 63
lecturas, y ninguna faltó en su fuente. El informe no imprime la nave, el viaje, el puerto ni el destino: dice si
calzan.

### ONE · fila 5 · «Review Booking»

| Campo | En la pantalla final | ¿Calza? |
|---|---|---|
| Nave | «Vessel/ Voyage» | Sí, la de la fila |
| Viaje | «Vessel/ Voyage» | Sí, el de la fila |
| Puerto de carga | «From» (CY) | Sí |
| Destino | «To» (CY) | Sí (el destino final de la fila es igual al original) |
| Contenedor | «REEFER 40FT High Cube x 1» | Sí |
| Temperatura | No está en «Review Booking» | Sí: −20 °C en la captura del paso anterior (`one_f5_8_carga`) y en `log.txt` |
| Peso | No está | Sí: 22 500 kg en la misma captura y en `log.txt` |
| Commodity | «FISH FILLET,MEAT FRE/CHI/FRO, SALMONIDAE» | Es lo que da la regla; ver «El commodity de ONE», abajo |

Sale el 21-10: de las 4 salidas de la nave ese día, eligió la directa. La captura de la guarda muestra, por OCR, lo
mismo que el HTML.

### MSC · fila 6 · «Summary» (la corrida de las 16:56)

| Campo | En la pantalla final | ¿Calza? |
|---|---|---|
| Nave | «Sailing Schedule Request» | Sí |
| Viaje | Junto a la nave | Sí |
| Puerto de carga | «Route Details», con su código de puerto | Sí |
| Destino | «Route Details» | Sí |
| Contenedor | «40' high cube reefer», «x 1» | Sí |
| Temperatura | −20 °C | Sí |
| Peso | «Gross Cargo Weight», 22 500 kgs | Sí |
| Commodity | El HS 030313 | Sí, el del programa. En el paso 3 eligió «Atlantic salmon (Salmo salar)…» y escribió «FROZEN SALMON SALAR» (`log.txt`) |

Sale el 25-10. Su captura es de letra chica: el OCR lee los dos puertos, el contenedor, la temperatura y las fechas,
pero no la nave ni el viaje.

### CMA-CGM · fila 7 · «Envío de la reserva»

| Campo | En la pantalla final | ¿Calza? |
|---|---|---|
| Nave | «Buque principal» de la ruta elegida | Sí |
| Viaje | «Ref. de viaje» | Sí |
| Puerto de carga | El campo «Puerto de carga» y el resumen | Sí |
| Destino | «Puerto de descarga» y «Rampa» (el lugar de entrega) | Sí: son el puerto de descarga y el destino final de la fila, que en esta fila son distintos; CMA usa los dos |
| Contenedor | «1 x 40' Reefer High Cube» | Sí |
| Temperatura | «Operando en −20 °C» | Sí |
| Peso | «Peso neto total (suma del peso de todos los contenedores) 22500 KGM» | Sí, el valor; ver «Las diferencias, juntas» |
| Commodity | «Frozen Atlantic salmon (Salmo salar)…», con el HS 030313 | Sí, la sugerencia del HS del programa |

Sale el 19-10, con transbordo. La captura de la guarda (la página entera) muestra, por OCR, la nave y el viaje, los
puertos, la rampa, el contenedor, la temperatura y el commodity; el peso no lo lee.

### COSCO · fila 8 · «Booking Details»

El formulario va en un marco (`cosco_f8_guarda_marco2.html`). Su HTML trae el itinerario y la opción elegida de cada
lista, pero no lo escrito en los campos de texto. La captura de la guarda, del tamaño de la ventana, muestra solo el pie
del formulario. Lo demás sale de la captura `cosco_f8_4b_shipper` (por OCR) y del CONTROL que el programa anota en
`log.txt`: lo lee del formulario en vivo, 1 s antes de la guarda.

| Campo | En la pantalla final | ¿Calza? |
|---|---|---|
| Nave | «Shipping Schedule Info», el primer tramo | Sí |
| Viaje | El primer tramo | Sí |
| Puerto de carga | El del itinerario | **No:** es otro puerto (abajo) |
| Destino | El del itinerario | Sí |
| Contenedor | «Size Type», con la opción elegida «40RQ - 40' Hi-Cube Refrigerated Container» | Sí; 1 contenedor, según el CONTROL |
| Temperatura | No está en el HTML | Sí: −20 Celsius en la captura y en el CONTROL |
| Peso | No está en el HTML | Sí: 22 500 Kilograms en la captura y en el CONTROL |
| Commodity | No está en el HTML ni en una captura | En el CONTROL: «Frozen / Freeze Fish» y el HS 030313, las constantes del programa |

- **El puerto de carga.** La celda de la fila está en `MAPA_PUERTOS_COSCO`, que la traduce a otro puerto: el mismo de
  las filas de CMA-CGM y HYUNDAI. COSCO lo buscó en «Origin City» y armó la reserva desde ahí. Es la regla del
  programa, y el mapa tiene las mismas 8 entradas desde el primer commit de `AQUASHIELD.py` (23-09). Si COSCO ofrece el
  puerto de la fila no se sabe sin el portal.
- Sale el 06-10, con transbordo y 42 días de tránsito: de los 2 itinerarios de la nave ese día, eligió el de menor
  tránsito. Su «CY Cutoff» es el domingo 04-10 a las 15:00. El formulario muestra el aviso «Your current allocation
  needs further confirmation…»: la reserva quedaría sujeta a la confirmación del portal.

### HYUNDAI · fila 9 · «Review & Book»

| Campo | En la pantalla final | ¿Calza? |
|---|---|---|
| Nave | «Vessel / Voyage» | Sí |
| Viaje | Entre paréntesis, pegado a 4 letras | Sí, pero no como palabra suelta: el portal le antepone su código de servicio. En la lista de salidas venía solo |
| Puerto de carga | «Port of Loading» y «Place of Receipt» | Sí |
| Destino | «Port of Discharging» y «Place of Delivery» | Sí |
| Contenedor | «RF/4H X 1» | Sí (reefer, 40' high cube) |
| Temperatura | No está en «Review & Book» | Solo en `log.txt` (−20 °C): la captura del paso anterior no deja leer el valor |
| Peso | No está | Sí: 22 500 en la captura del paso anterior (OCR a escala 3) y en `log.txt` |
| Commodity | «SALMON» | Sí, la regla |

Sale el 24-10: de las 2 salidas de la nave ese día, eligió la directa. La captura de la guarda muestra, por OCR, lo
mismo que el HTML.

### MAERSK · fila 10 · «Review booking»

| Campo | En la pantalla final | ¿Calza? |
|---|---|---|
| Nave | No está, ni en su HTML ni en su captura | Sí, en la lista de salidas al elegirla (`mk_f10_5_nave`, por OCR: las 3 tarjetas del 18-10 traen la nave y el viaje de la fila) y en `log.txt` |
| Viaje | No está | Sí, en la misma captura |
| Puerto de carga | «From», Container Yard | Sí |
| Destino | «To», Container Yard | Sí: es el destino final de la fila, como dice su regla. Su puerto de descarga, que es otro, no aparece |
| Contenedor | «40 Reefer High», cantidad 1 | Sí |
| Temperatura | −20 ºC | Sí |
| Peso | 22 500 kg | Sí |
| Commodity | «Salmon, frozen, fish» | Sí, la regla |

- Sale el 18-10 a las 08:30. Las 3 tarjetas de la nave eran copias de una sola salida.
- La captura de la guarda (la página entera) muestra, por OCR, lo mismo que el HTML, y tampoco trae la nave ni el viaje.
- Los términos quedaron marcados: la casilla está sin marcar en `mk_f10_terminos` y marcada en el HTML de la guarda. Es
  la primera vez que el clic de JavaScript se prueba en el portal.
- El Shipper quedó con AQUACHILE con el clic en el resultado, y el buscador se cerró solo: ni la casilla ni el «Close»
  hicieron falta.

### La fecha de retiro de MAERSK: el 13-10

| Paso | Lo que pasó |
|---|---|
| La regla | El primer día hábil después de hoy, viernes 02-10: el lunes 05-10 |
| El calendario | Octubre de 2026, leído por su cabecera (el lector del encargo 48): 31 días, con habilitados del lunes 12 al viernes 16 |
| El 05-10 | No estaba habilitado, así que toca el siguiente día hábil habilitado |
| El 12-10 | Habilitado, pero feriado en Chile («Día del Encuentro de dos Mundos», según holidays 0.105) |
| El elegido | El martes 13-10: pulsó el 13 y el «Done», y la tarjeta de «Additional details» muestra «13 October 2026» |

- El 13-10 es anterior al cierre de recepción de esa salida (el 16-10 a las 02:30).
- Leído sin red con el código de `46eb63d`, el calendario guardado esta tarde da lo mismo que dijo `log.txt` y elige el
  13.
- El mensaje de `log.txt` no nombra el feriado: es un residual del encargo 48.

### Las diferencias, juntas

| Naviera | Qué | ¿Lo decide una regla? |
|---|---|---|
| COSCO | El puerto de carga no es el de la fila | Sí, `MAPA_PUERTOS_COSCO`. Mantenerlo o no lo decides tú |
| ONE | Declara filete de salmónido; las demás, salmón entero congelado | Sí: la primera sugerencia de «SALMON». Cuál corresponde lo decides tú |
| CMA-CGM | Su resumen llama «peso neto» a los 22 500 kg, que para el programa son el peso bruto | Es la etiqueta del portal; el campo del formulario dice «Peso total» |
| HYUNDAI | El viaje va pegado al código de servicio | Es el formato del portal: el viaje de la fila está |
| MAERSK | El destino es el final de la fila, no su puerto de descarga | Sí: su regla toma el destino final |

**El commodity de ONE.** Hay 13 capturas del paso «Container & Cargo» de ONE en `logs/`, del 21-09 al 02-10. En 12, ONE
dejó «FISH FILLET,MEAT FRE/CHI/FRO, SALMONIDAE». En la otra, del 26-09 a las 14:13, dejó «FISH FILLET,MEAT
FRE/CHI/FRO, PACIFIC SALMON, ATLANTIC SALMON AND DANUBE SALMON». O sea, la regla depende del orden en que el portal
muestra las sugerencias.

**El contrato, aparte.** No es uno de los ocho campos, pero la fila lo trae:
- en ONE, MSC, CMA-CGM y COSCO, la pantalla muestra el de la celda;
- en HYUNDAI, el de `config.json` (`contratos_por_defecto`), que está dentro del texto de la celda;
- en MAERSK, la celda no trae un número de contrato y el programa no la usa: la pantalla muestra el que puso el portal.

## FRENA SI

Nada exigió abrir un portal. Lo que no se puede confirmar sin él queda dicho como no confirmado y pasa al residual: por
qué MSC da el 502, si un inicio de sesión previo lo provoca y si COSCO ofrece el puerto de la fila.

## Re-medir

Todo corre desde `scratchpad\e49`, en Git Bash, después de `source entorno_e49.sh` (`TMPDIR`, `TEMP` y `TMP` dentro de
la carpeta), con Python 3.13. Ningún script imprime valores de la planilla ni de la cuenta: pasan por `mascara.py`.

| Número | Script |
|---|---|
| Las carpetas de `logs/` | `python corridas.py 20261002` |
| Cada log, con la máscara | `python ver_log.py <AAAAmmdd_HHMMSS> [desde] [hasta] [regex]`; su control, `python control_mascara.py` |
| Los pasos del login de MSC en el historial del perfil | `python historial_msc.py 10-01` |
| Las fallas de MSC según la pausa | `python pausas_msc.py` |
| El texto de las capturas (OCR) | `python ocr_capturas.py <AAAAmmdd_HHMMSS> <captura.png>…` (`OCR_FACTOR=3` para la letra chica); por bandas y con lista blanca, `python ocr_campos.py …` |
| La planilla y la ficha de cada fila | `python filas_e49.py`; `python fichas_e49.py` |
| El texto de un HTML, con sus raíces shadow | `python texto_html.py <AAAAmmdd_HHMMSS> <archivo.html> [--marcos]` |
| Los ocho campos y el contrato, uno por uno | `python calce_e49.py` |
| Las opciones elegidas en el formulario de COSCO | `python t/cosco_elegidos.py` |
| El calendario y la fecha de retiro de MAERSK | `python calendario_e49.py` |
| El commodity de ONE en las 13 capturas | `python commodity_one.py` |
| La forma del contrato de MAERSK y de HYUNDAI | `python t/formas_contrato_mk.py` |

## NO retroceder

Este encargo no cambió el programa. Lo que no hay que retroceder es de la medición:
- **La ida a eBooking no rescató la sesión de MSC en ninguna de las 4 veces medidas.** No cuentes con ella como rescate
  sin medirla otra vez.
- **El HTML de una guarda no trae lo escrito en un campo de texto.** En COSCO, el peso, la temperatura y el commodity
  se comprueban con la captura del paso anterior y con el CONTROL de `log.txt`, no con ese HTML.

## Defectos de instrumento que me cacé

- **La máscara dejaba pasar cosas que no vienen de la planilla:**
  - los viajes de las otras naves de MSC, que mezclan letras y cifras, y los códigos de puerto;
  - la nave de otra salida de MAERSK, que lleva «MAERSK» al final del nombre;
  - otra palabra del nombre que muestra HYUNDAI junto al del operador, y el nombre de una persona del portal;
  - trozos que el OCR lee a medias, como el final de un contrato o un correo.

  Salieron solo en salidas de herramienta de esta sesión, no en un archivo del repo ni en este informe. Les sumé
  reglas a la máscara, y el OCR de los campos imprime solo líneas de una lista blanca (`ocr_campos.py`).
- **El volcado de HTML tapaba en cascada:** la línea que reemplazaba tras una etiqueta de nave traía la palabra «nave»,
  y tapaba también la siguiente.
- **`calce_e49.py`:**
  - cortaba la ciudad sin el corchete, y el puerto de MSC, con su código entre corchetes, daba «no calza» en falso;
  - buscaba el contrato por defecto de HYUNDAI por una ruta de `config.json` que no existe, y daba «no» sin mirar;
  - esperaba «fila N» en `log.txt`, pero HYUNDAI no la anota (ahora la reconoce por el nombre de su evidencia).

  Los tres los corregí antes de concluir.
- **`pausas_msc.py` contaba como sesión un 502 recargado:** Chrome no guarda el TriggerOidcLogin que dio el error, y
  sí su recarga. Ahora mira la transición de esa visita.
- **Usé `sort` de Git Bash una vez**, que Defender bloquea (ya estaba en el catálogo de la máquina). Lo vi por el
  «Permission denied», y seguí con Python.
- **Edité este informe mientras corría la suite,** y su foto de los originales lo marcó como cambiado: 573 pruebas OK
  y «cambios: 1». La volví a correr con el informe cerrado.

## Premisas del encargo que se refutaron

- **«MAERSK por primera vez»:** es la primera vez que MAERSK se detiene en la guarda con todo armado y sin emitir: la
  primera OK-EJEMPLO de MAERSK en `logs/`. Antes llegó a su pantalla final 6 veces, con el código de entonces:
  - el 21-09, 5 reservas pasaron la revisión y se emitieron, porque esa corrida tenía la emisión abierta
    (`CICLO-emitidas-sin-marcar.md`);
  - el 24-09, una llegó a la guarda y quedó REVISAR: no encontró la nave («nave=no-encontrada») y siguió igual.
- **El 502 tras el «Next»:** esta tarde no lo hubo. El 502 llegó después de la clave, en la vuelta a myMSC.

## Residual

| Qué | Por qué no se hizo | Se reabre si |
|---|---|---|
| Por qué MSC da el 502 (tras el «Next» o en la vuelta a myMSC), y si un inicio de sesión previo influye | Falta la respuesta del portal: estado, cabeceras y cuerpo | Lo encargas: una traza con la red, o un login a mano a la vez que el del programa |
| La recarga del encargo 47, en el portal | Esta tarde no hubo 502 tras el «Next» | Vuelve ese 502: `log.txt` dice «MSC mostró una página de error al pulsar «Next»» |
| Rescatar la sesión tras el 502 en la vuelta a myMSC | La ida a eBooking no la dejó (0 de 4); lo único medido que la rescató es otro intento de inicio de sesión, que decidiste no hacer | Lo decides tú |
| COSCO y `MAPA_PUERTOS_COSCO` | Es una regla del programa; si COSCO ofrece el puerto de la fila no se sabe sin el portal | Lo decides tú |
| El commodity de ONE | Es una regla del programa (la sugerencia más arriba); cuál corresponde es una decisión de negocio | Lo decides tú |
| La temperatura de HYUNDAI en pantalla | Ni «Review & Book» ni la captura del paso anterior la muestran; solo `log.txt` | Lo encargas: guardar el HTML de «Booking Details» |
| El «CY Cutoff» de COSCO, el domingo 04-10 a las 15:00 | La regla elige la próxima salida y no mira el cierre de recepción | Lo decides tú |
| La casilla del resultado y el «Close» del Shipper de MAERSK | No hicieron falta: siguen sin probarse en el portal | El clic en el resultado no lo elige, o el buscador no se cierra solo |

## Reglas de método aplicadas

`metodo-ciclo` v15, con las reglas permanentes de `~/.claude/CLAUDE.md`:
- **Todo salto silencioso lleva contador:** 33 carpetas de corrida y 0 que no calzan; 64 tandas en el historial, 60
  clasificadas y 4 de antes de la primera con TriggerOidcLogin; 63 lecturas de campos y 0 que faltaran; 13 capturas
  del commodity de ONE y 0 ilegibles.
- **Control positivo que aborta:**
  - la máscara: sus 69 valores salen cambiados, y la nave de la corrida del 21-09 también;
  - el OCR, con su imagen sintética, y el volcado de HTML, con una raíz shadow sintética;
  - el calendario tiene que dar lo que dijo `log.txt`, y el historial, las tres clases de esta tarde;
  - el commodity de ONE tiene que dar lo que dijo `log.txt`, y las filas tienen que ser la 5 a la 10, con nave y viaje.
- **La unidad de la medición la fija el sujeto:** el inicio de sesión (la tanda del historial), no la corrida; y el
  campo, no la página.
- **Todo registro es una hipótesis:** `CLAUDE.md` decía «no está probado en el portal» del clic de los términos, y
  «sin medir» del clic en el resultado del Shipper. Las dos cosas pasaron a medidas, y la premisa de MAERSK se corrigió.
- **Re-medir contra HEAD:** todo se leyó con el código de `46eb63d`, el que corrió.
- **Frenar si la decisión es de negocio, y lo que está fuera del encargo se propone:** COSCO, ONE y el rescate de MSC
  van al residual.

**Choques:** las reglas de Python de ECC piden pytest, anotaciones de tipos y black; el repo usa `unittest` y su propio
estilo, y las sondas siguieron el del repo (mandan las reglas permanentes y `metodo-ciclo`). Las revisiones y los
agentes que pide ECC no se lanzaron. Entre las reglas del método, ninguno.

## Lo que dio en el repo

- Este informe, en un solo commit con `CLAUDE.md` al día:
  - MSC la tarde del 02-10, y el «1 de 5 el 02-10» del historial;
  - el clic de JavaScript de los términos de MAERSK, probado en el portal;
  - el clic en el resultado del Shipper, que lo eligió con el buscador cerrado solo;
  - el calendario por su cabecera, que funcionó en el portal.
- Ningún cambio de código.

El push lo haces tú. Los comandos, con el hash esperado, van en el mensaje final del encargo: este informe va dentro del
commit y no puede citar su propio hash.
