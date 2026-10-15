# Encargo 68 · La corrida de prueba del 15-10: por qué CMA-CGM y MAERSK quedaron NO ENVIADA

**Base:** `C:\dev\Agendamiento Reservas` @ `582924d` · árbol limpio al empezar.

Con `metodo-ciclo` v24: el encabezado del archivo dice v24, la misma versión que tenía cargada la sesión. Todo se midió
sin abrir ningún portal: `logs/` y el HTML que guardó el programa, cargado en un Chromium sin red. Las capturas, solo
por OCR, sin mirarlas. Solo diagnóstico: no cambié código. Lo único que escribí fuera de la carpeta del encargo es la
copia de la planilla que pediste, y este informe con `CLAUDE.md`.

## En resumen

- **CMA-CGM (fila 7): el viaje de la fila ya no se ofrece.** La nave sí está, en 2 de las 6 rutas que mostró el portal,
  pero con otro viaje. El viaje de la fila no aparece en ninguna ruta, ni hoy ni ayer.
  - Ya hice la copia que pediste: **«Reservas AQUASHIELD - CMA-CGM vigente 15-10.xlsx»**, junto a la original.
  - En la copia cambian solo la nave y el viaje de esa fila: ahora son los de la salida vigente más próxima, la del
    26-10.
  - Con la copia, el programa elegiría esa ruta en la lista de hoy (medido sin red).
- **MAERSK (fila 10): FRENA, porque la causa no es la nave ni el viaje.** El portal ofreció la nave con el viaje de la
  fila, con su «Book», y el programa la eligió. Pero esa salida cierra hoy a las 21:00 la entrega del contenedor
  («GATE-IN DEADLINE»).
  - Por eso el calendario de retiro habilitó un solo día: hoy, 15-10.
  - La regla pide el primer día hábil después de hoy, el 16-10, así que la fila quedó NO ENVIADA sin elegir día.
  - Ayer, con la misma salida, el calendario dejaba el 15-10, y llegó a la guarda.
  - No cambié la fila: **lo decides tú** (opciones, abajo).
- **Las cuatro que llegaron a la guarda calzan con su fila:** ONE, MSC, COSCO y HYUNDAI.
  - Calzan en nave, viaje, puerto de carga, destino, contenedor, peso, temperatura, commodity y contrato.
  - En las cuatro, el viaje elegido es el de la fila.
- **Lo del encargo 67 funcionó por primera vez en el portal:**
  - MSC volvió a leer la tarjeta elegida antes del clic, la encontró igual y pulsó.
  - CMA-CGM leyó el primer tramo de sus 6 rutas: ninguna quedó sin leer.

## La corrida

| Qué | Medido |
|---|---|
| Carpeta | `web_todas_…_20261015_082903`, de 08:29:03 a 08:38:16 |
| Programa | El de `582924d`. El panel se abrió a las 08:26:51 (`logs/actualizacion.json`), y `AQUASHIELD.py` es el blob de HEAD, sin cambios desde el 14-10 a las 23:09 |
| Candado | Cerrado: la segunda línea de `log.txt` dice «modo prueba, sin ninguna de sus tres llaves abierta» |
| Planilla | La copia que guardó el panel a las 08:27, igual byte a byte a `Reservas AQUASHIELD.xlsx` (del 08-10), la misma de ayer. Hoja CONSOLIDADO, filas 5 a 10, una por naviera |
| Inicio de sesión | ONE y HYUNDAI, sin pausas; MSC, al primer intento; COSCO resolvió solo su rompecabezas; CMA-CGM mostró el deslizador de DataDome y lo pasaste en 14 s; MAERSK ya tenía la sesión abierta |

| Naviera · fila | Resultado | Dónde terminó |
|---|---|---|
| ONE · 5 | OK-EJEMPLO, «lista para emitir» | «Review Booking», 08:30:21 |
| MSC · 6 | OK-EJEMPLO | «Summary», 08:31:54 |
| CMA-CGM · 7 | **NO ENVIADA** | «Route choices», 08:33:33 |
| COSCO · 8 | OK-EJEMPLO | «Booking Details», 08:34:54 |
| HYUNDAI · 9 | OK-EJEMPLO | «Review & Book», 08:37:13 |
| MAERSK · 10 | **NO ENVIADA** | «Additional details», la fecha de retiro, 08:38:15 |

## CMA-CGM · fila 7: el viaje de la fila ya no se ofrece

**El motivo** (`log.txt`, línea 202): «no elegí ruta para esa nave: ninguna de las 2 opciones de la nave trae el viaje
de la fila (busqué hasta el 09-11-2026, la última salida que mostró el portal, y ya no vi el enlace «Cargar …
siguientes resultados»)».

**El paso:** en «Route choices», después de pulsar una vez «Cargar … siguientes resultados» (4 rutas, y después 6).
Antes pasó por el origen, el destino, la rampa, la carga y la mercancía sin problemas. «Validar ruta» no contestó en
12 s, como en las 15 corridas de `logs/` que pasan por ese paso: no decide nada.

**Por el camino real.** Corrí sin red el `_JS_CMA_RUTAS` de `582924d` sobre las dos listas que guardó
(`cma_f7_rutas.html` y `cma_f7_rutas_mas.html`), con las palabras de la nave y del viaje de la fila. Las armé como las
arma `_cma_seleccionar_itinerario`.
- **Con el viaje:** no elige ninguna. 2 rutas traen la nave, y 0 quedan sin leer.
- **Con la nave sola:** elegiría la 3.ª, la que eligió ayer, antes del encargo 66.

| Ruta | Sale | Cut-off | Nave del primer tramo | ¿Su «Ref. de viaje» es el de la fila? | ¿El viaje de la fila en algún lugar de la tarjeta? |
|---|---|---|---|---|---|
| 1 | 26-10 | 20-10, 21:00 | otra | no | no |
| 2 | 26-10 | 20-10, 21:00 | otra (la misma de la 1, con el mismo viaje) | no | no |
| 3 | 02-11 | 27-10, 21:00 | **la de la fila** | no | no |
| 4 | 02-11 | 27-10, 21:00 | **la de la fila** | no | no |
| 5 | 09-11 | 03-11, 21:00 | otra (la de la 1) | no | no |
| 6 | 09-11 | 03-11, 21:00 | otra (la de la 1) | no | no |

- **Cada ruta es de la fila:** las 6 traen la ciudad de su puerto de carga, la de su puerto de descarga y la de su
  destino final. La búsqueda fue con los tres.
- **Cada ruta tiene dos tramos.** El viaje de la fila no aparece como palabra entera en el texto de ninguna tarjeta: ni
  en el primer tramo, ni en el segundo, ni en el resumen.
- **Ayer (14-10, a las 08:35:52) la lista traía las mismas 4 primeras rutas,** y tampoco el viaje de la fila.
- **El 02-10 sí estaba:** CMA eligió la ruta con ese viaje, que salía el 19-10 (encargo 65). El viaje de la fila tiene
  la misma forma que los del portal (AA99A9A99).
- **El encargo 65 lo infirió:** la fila pide una salida anterior que el portal ya no ofrece.

### La copia de la planilla

- **Nombre:** **«Reservas AQUASHIELD - CMA-CGM vigente 15-10.xlsx»**, en `C:\dev\Agendamiento Reservas`, junto a la
  original.
  - Queda fuera de git (`*.xlsx`).
  - No calza con el patrón de los respaldos que poda el programa (`PATRON_RESPALDO`).
- **La original no cambió:** su sha256 es el mismo antes y después.
- **Qué cambia:** en la hoja CONSOLIDADO, fila 7 (CMA-CGM), solo la nave (E7) y el viaje (F7).
  - Comparé las 396 celdas de las dos hojas de la copia con las de la original: difieren solo esas dos.
  - La hoja «respaldo» no se tocó.
- **Qué salida:** la vigente más próxima entre las cinco primeras que mostró hoy el portal.
  - Las cinco primeras son las rutas 1 a 5, en el orden de la lista: primero mostró 4 y después cargó 2 más.
  - Las cinco estaban vigentes: su cut-off era posterior a la lectura de hoy, a las 08:33.
  - La más próxima sale el 26-10. Son las rutas 1 y 2, que traen la misma nave y el mismo viaje en su primer tramo, así
    que la fila queda determinada sin elegir entre ellas.
  - **No es la nave de la fila.** La de la fila sale el 02-11 (rutas 3 y 4). Seguí tu regla, la salida más próxima, y no
    la nave.
- **Cómo quedó escrita:** la nave y el viaje van tal como los trae el portal en el «Buque» y la «Ref. de viaje» de ese
  primer tramo.
  - La nave nueva es de una palabra; la de la fila tenía dos.
  - El viaje nuevo tiene la misma forma que el de la fila.
- **Verificado por el camino real:**
  - leí la copia con `leer_filas` del programa: solo cambian la nave y el viaje de la fila 7, que sigue siendo de
    CMA-CGM y no es una fila «sin nave»;
  - con sus palabras, `_JS_CMA_RUTAS` sobre la lista de hoy pulsa la 1.ª ruta; con la fila de la original, ninguna, que
    es lo que pasó hoy.
- **Entre la 1 y la 2, el programa elige la 1, la primera de la lista.** Comparten el primer tramo y difieren en el
  segundo, que es otra nave y otro viaje. La 1 llega el 28-11; la 2, el 04-12.
- **Escrita con openpyxl,** como escribe la planilla el propio panel (`_planilla_con_resultados`), en una copia de
  trabajo que verifiqué antes de ponerla en su lugar.
  - Conserva las dos hojas, las celdas combinadas y el ancho de las columnas.
  - Guarda los textos dentro de cada hoja y no en una tabla compartida, que es como escribe openpyxl, y pesa 8.777 bytes
    en vez de 12.697.
  - La original no traía validaciones ni formato condicional.
- **Vence pronto:** el cut-off de esa salida es el 20-10 a las 21:00. Después, la fila de la copia volvería a quedar NO
  ENVIADA.

## MAERSK · fila 10: FRENA, la causa no es la nave ni el viaje

**El motivo** (`log.txt`, línea 415): «abrí el calendario de la fecha de retiro, pero no hay un día hábil habilitado del
16-10-2026 al 31-10-2026, el último que muestra el calendario, y cambiar de mes es un clic que no está permitido; no
pulsé nada más y la reserva no se envió».

**El paso:** «Additional details», la fecha de retiro. Antes, todo salió bien:
- el origen y el destino;
- «40 Reefer High» (1 de 2 opciones) y «Standard (40´)» (1 de 3);
- la búsqueda «desde mañana», como siempre (el freno del encargo 37);
- la elección de la salida y «Recommended services».

**La nave y el viaje sí se ofrecían:**
- **Lo que dice `log.txt`:** «2 salida(s) de la nave sin un solo «Book»: el portal no deja reservarlas» y «nave
  seleccionada: …, sale 17 Oct 2026, 20:30». MAERSK elige una salida solo si trae el viaje de la fila.
- **El OCR de `mk_f10_5_nave.png`** (la lista al elegir) encuentra 3 tarjetas con la nave de la fila, y las 3 traen el
  viaje de la fila.
  - En la columna «GATE-IN DEADLINE», las 3 dicen «15 Oct 2026, 21:00».
  - Llegan en tres fechas distintas, y una dice «Vessel sold out».

**El calendario, por el camino real.** Corrí sin red el `_JS_MK_CALENDARIO` de `582924d` sobre
`mk_f10_calendario.html`:
- da 31 días de octubre de 2026, los 31 con su fecha, leídos por la cabecera;
- **habilitado, uno solo: el 15-10, hoy.**

La regla (`_mk_dia_de_retiro` y `_mk_elegir_dia_de_retiro`, decisión tuya de los encargos 37 y 38) pide el primer día
hábil después de hoy, el viernes 16-10, que no es feriado: los de octubre son el 12 y el 31, según holidays 0.105. Desde
el 16 no hay ningún día habilitado.

**Ayer (14-10, a las 08:34:22), con la misma salida:**
- el calendario habilitaba el 14 y el 15;
- la regla eligió el 15, y la fila llegó a la guarda;
- el OCR de esa lista lee el mismo plazo, a las 21:00 (el día, con un carácter dudoso: «45 Oct»).

El portal también movió la salida: ayer decía 18-10 a las 08:30 (encargo 65); hoy, 17-10 a las 20:30.

**Lo que pasó, en una línea:** la salida de la fila sigue a la venta, pero su contenedor hay que entregarlo hoy. La
regla del programa nunca retira hoy, así que desde hoy esa salida no se puede armar.

**Por qué no cambié la fila:**
- es la condición de freno del encargo («la causa de alguna no es la nave ni el viaje»);
- aunque decidas tratarla como CMA-CGM, las cinco primeras salidas de hoy no están en lo guardado. MAERSK guarda el HTML
  de su lista solo cuando se detiene en ella (`mk_f<fila>_detenida`). La captura de antes (`mk_f10_4_sailing.png`) se
  tomó con la lista todavía vacía, y la de la elección (`mk_f10_5_nave.png`) muestra solo las 3 tarjetas de la nave.
  Elegir la salida de reemplazo exigiría abrir el portal, que es la otra condición de freno.

## Las cuatro que llegaron a la guarda

**Cómo se comparó, igual que en los encargos 49 y 65.**
- **La pantalla final** es la de la guarda, `<nav>_f<fila>_guarda.html`: la página y sus marcos. Cada HTML se cargó en
  un Chromium sin red y sin el JavaScript de la página, y cada campo se leyó por su etiqueta.
- **La comparación con la fila** usa las funciones del programa: `_trae_la_nave`, `_palabra_en` y `_norm_ctrl`.
- **Si la pantalla final no trae un campo,** la fuente es una captura anterior (OCR) o `log.txt`.
- **El comparador aborta** si un campo no aparece en su fuente, y no faltó ninguno.
- **Este informe no imprime** la nave, el viaje, el puerto ni el destino: dice si calzan.

| Campo | ONE · 5 | MSC · 6 | COSCO · 8 | HYUNDAI · 9 |
|---|---|---|---|---|
| Nave | Sí | Sí | Sí (1.er tramo) | Sí («1st Vessel») |
| Viaje | Sí | Sí | Sí | Sí. En la pantalla final va pegado a un código de 4 letras, como el 02-10 y el 14-10; en la lista donde lo eligió va entre paréntesis, como palabra entera (`log.txt`, línea 317) |
| Puerto de carga | Sí | Sí | Sí (el mapa de COSCO no lo cambia) | Sí (recepción y carga) |
| Destino | Sí | Sí | Sí | Sí (descarga y entrega) |
| Contenedor | «REEFER 40FT High Cube x 1» | «40' high cube reefer», x 1 | «40RQ - 40' Hi-Cube Refrigerated Container», 1 | «RF/4H X 1» |
| Temperatura | −20, en la captura de la carga y en `log.txt` | −20 °C | −20, en el CONTROL de `log.txt` | −20, solo en `log.txt` |
| Peso | 22 500, en la captura y en `log.txt` | 22 500 kgs | 22 500, en la captura y en el CONTROL | 22 500, solo en `log.txt` |
| Commodity | «FISH FILLET,MEAT FRE/CHI/FRO, SALMONIDAE» | El HS 030313 | «Frozen / Freeze Fish» y el HS, en el CONTROL | «SALMON» |
| Contrato | El de la celda | El de la celda | El de la celda | El de `config.json`, dentro del texto de la celda, como el 02-10 y el 14-10 |
| Salida | 26-10, la directa de las 4 de la nave; llega el 02-12 | ETD 03-11; ETA 12-12 | ETD 20-10, con transbordo, 33 días; CY Cutoff el domingo 18-10 a las 15:00 | ETD 29-10; cut-off 26-10 |

**Cómo eligió cada una el viaje:**
- **ONE:** de 36 tarjetas, 4 salidas de la nave el 26-10, y prefirió la directa.
- **MSC:** de 29 itinerarios. **Volvió a leer la tarjeta antes del clic y pulsó** (encargo 67): si no, la fila habría
  quedado NO ENVIADA.
- **COSCO:** 2 itinerarios con la nave. Eligió la próxima salida, el 20-10, y entre las 2 de ese día, la de menor
  tránsito: 33 días, contra 48.
- **HYUNDAI:** la «1st Vessel» de la fila, que sale el 29-10. Marcó «I do not want to choose an alternate vessel» en el
  modal y pulsó OK.

## Otras cosas que vi

- **ONE dejó incompleta la evidencia de las sugerencias de Origen:** 3 de 4 HTML, porque un marco se cerró mientras lo
  guardaba (`TargetClosedError`). Así lo dice `log.txt`. La reserva siguió igual, como manda la evidencia.
- **HYUNDAI no encontró el contrato de la celda en el Paso 2** («sin opción»), como ayer. En el Paso 3 eligió el de
  `config.json`.
- **Entre COSCO y HYUNDAI pasaron 93 s** (08:34:54 a 08:36:27) sin líneas en `log.txt`; ayer, 1 s. No cambió ningún
  resultado, y no lo investigué (residual).
- **Las salidas de las filas de prueba están cerca.**
  - COSCO: su CY Cutoff es el domingo 18-10.
  - La copia de CMA-CGM: su cut-off es el 20-10.
  - HYUNDAI: su cut-off es el 26-10.
  - Con la planilla del 08-10, las próximas corridas de prueba irán quedando NO ENVIADA. Es una inferencia por las
    fechas, no algo medido.

## Lo decides tú

1. **MAERSK, una salida que cierra la entrega del contenedor el mismo día de la corrida.** Opciones:
   - **Tratarla como CMA-CGM:** cambiar la nave y el viaje de la fila 10 por los de una salida posterior. Para elegirla
     hay que mirar la lista del portal, que no quedó guardada. La miras tú, o lo encargas con una corrida.
   - **Que MAERSK pueda retirar el mismo día** cuando su plazo vence ese día. Es cambiar la regla de los encargos 37 y
     38, y es código.
   - **Que MAERSK corte antes, al elegir la salida,** con un motivo claro: «la salida cierra hoy la entrega del
     contenedor». Hoy lo descubre recién en el calendario, después de llenar todo. Es código.
   - **Dejarla así.** Con una fila vigente, la regla funciona, como ayer.
2. **La copia de CMA-CGM** sirve hasta el 20-10 a las 21:00. Si la quieres para más días, se puede tomar otra salida,
   pero tu regla dice «la más próxima».

## Residual

| Qué | Por qué no se hizo | Se reabre si |
|---|---|---|
| La fila de MAERSK en la copia | FRENA: la causa no es la nave ni el viaje, y la salida de reemplazo no está en lo guardado | Decides cómo (arriba) |
| MAERSK no mira el «GATE-IN DEADLINE» al elegir la salida | Es código, y el encargo es solo diagnóstico | Lo encargas |
| MAERSK no guarda el HTML de su lista de salidas cuando elige (sí cuando se detiene) | Es código | Lo encargas: con él, lo de hoy se habría medido entero sin OCR |
| La fecha de zarpe de MAERSK, «desde mañana» | El freno del encargo 37 | Lo pruebas en el portal |
| CMA-CGM y COSCO no llegan a EMITIDA | Falta medir su confirmación (`FORMA_BOOKING`) | Haya una confirmación real guardada |
| Las salidas de las demás filas de prueba vencen entre el 18 y el 26-10 | No se pidió | Antes de la próxima corrida de prueba |
| Los 93 s sin líneas entre COSCO y HYUNDAI | No cambió ningún resultado, y el encargo no lo pedía | Vuelva a pasar, o una corrida se corte ahí |

## FRENA SI

- **«La causa de alguna no es la nave ni el viaje»: se cumple en MAERSK.** La reporté con su evidencia y no cambié su
  fila.
- **«Confirmar algo exige abrir un portal desde el programa»:**
  - no hizo falta para nada de lo medido;
  - haría falta para elegir la salida de reemplazo de MAERSK, si decides tratarla como CMA-CGM.

## Premisas que se cayeron

- **«La nave o el viaje ya no se ofrecen»** vale para CMA-CGM, no para MAERSK. MAERSK ofreció la nave con el viaje de la
  fila, y con su «Book». Lo que vence hoy es el plazo para entregar el contenedor.

## Defectos de instrumento y errores míos

- **Imprimí una vez el nombre del operador en mi consola.** Listé las carpetas de `logs/` con una expresión que tapaba
  el operador en las carpetas de reservas, pero no en las de inicio de sesión, cuyo nombre empieza por el usuario. Quedó
  solo en la salida de esa herramienta: ningún archivo lo trae, y desde ahí listé con el script.
- **La máscara dejó pasar a la salida de mis scripts datos del portal que no están en la planilla:**
  - una palabra de la nave del transbordo de COSCO (como en el encargo 65);
  - el código de 4 letras pegado al viaje de HYUNDAI;
  - el nombre y la dirección del depósito de retiro de MAERSK.

  Quedaron solo en la carpeta del encargo.
- **Bash me juntó tres veces las barras invertidas de un heredoc.** Los tres fallaron sin dar ningún resultado, y los
  rehice con Write o Edit. Es la regla conocida del entorno, y la volví a pisar.
- **La primera medición de las rutas de CMA-CGM leía el texto con `textContent`,** que pega el de elementos vecinos, y
  su control abortó. Ahora lee `innerText`, como el programa.
- **Una aserción comparó la ruta corta 8.3 con la larga** (`volcar_e68.py`) y abortó; ahora resuelve las dos.
- **Un `cd` en primer plano movió la sesión a `logs/`** durante un comando; la devolví a la raíz.

## Re-medir

Todo corre desde `scratchpad\e68`, en Git Bash, después de `source entorno_e68.sh`, que pone `TMPDIR`, `TEMP` y `TMP`
dentro de la carpeta. Ningún script imprime valores de la planilla ni de la cuenta: pasan por `mascara.py` (la de los
encargos 49 y 65, con el programa de `582924d`), o imprimen solo sí/no, fechas y formas.

| Número | Script |
|---|---|
| El `log.txt` de la corrida, con la máscara | `python ver_log.py 20261015_082903` |
| Las filas de la planilla | `python filas_e68.py` |
| El JavaScript del programa y las filas, para las sondas | `python volcar_e68.py <t\volcado.json> [planilla]` |
| Las rutas de CMA-CGM, hoy y ayer, y la salida más próxima | `python cma_e68.py` |
| Las rutas 1 y 2 de CMA-CGM | `python cma_1y2.py` |
| Los puertos de la fila en cada ruta de CMA-CGM | `python destino_cma.py` |
| La copia de la planilla (no la pisa si ya existe) | `python copia_e68.py` |
| La copia, por el camino real | `python verificar_copia.py` |
| El calendario y la salida de MAERSK, hoy o ayer | `python mk_e68.py [20261014_083422]` |
| El texto de un HTML guardado, enmascarado | `python texto_html.py 20261015_082903 <nombre.html>` |
| El OCR de una captura, enmascarado | `python ocr_buscar.py 20261015_082903 <regex> <captura.png>[@escala]` |
| Las cuatro pantallas finales | `python calce_e68.py` (se arma con `armar_calce.py` desde `calce_e65.py`) |

## NO retroceder

- **La original no se toca:** la copia es otro archivo, y `copia_e68.py` no pisa una copia que ya exista.
- **La fila de MAERSK no se cambia sin tu decisión:** su causa no es la que el encargo autorizó a corregir.
- **Lo de CMA-CGM no es un defecto del programa:** cortó como debía (encargo 66) y leyó las 6 rutas (encargo 67). Con la
  regla de antes del encargo 66 habría armado la reserva con otro viaje, como ayer.

## Reglas de método aplicadas

`metodo-ciclo` v24, y las reglas del módulo (`CLAUDE.md`). Sin choques entre ellas.

- **Control positivo que aborta:**
  - la máscara aborta si le queda un valor;
  - el comparador de las pantallas finales aborta si un campo falta;
  - las sondas de CMA-CGM, con una página sintética de tres rutas; abortó una vez, y corregí la sonda;
  - la del calendario exige los 31 días que dice `log.txt`;
  - la del OCR de MAERSK exige encontrar la nave elegida;
  - la de la copia aborta si cambia otra celda o la original.
- **Se mide sobre el camino real:** el JavaScript del programa (`_JS_CMA_RUTAS`, `_JS_MK_CALENDARIO`) sobre el HTML
  guardado, y `leer_filas` sobre las planillas, también sobre la copia.
- **La unidad la fija el sujeto:** el veredicto es por reserva, y cada campo, por su fuente.
- **Universo y cobertura:**
  - de CMA-CGM, las 2 listas de hoy (6 rutas) y la de ayer (4);
  - de MAERSK, el calendario de hoy y el de ayer, y 2 capturas por día;
  - de la copia, las 396 celdas.
- **Residual, premisas y FRENA:** declarados arriba.
- **Del módulo:**
  - ningún portal, y nada de la emisión;
  - las sondas cargan el programa con `soporte`, nunca desde la raíz;
  - datos inventados o enmascarados en el informe;
  - la sonda de secretos y el barrido antes del commit;
  - el correo noreply.

## Lo que decidí yo

- **El nombre de la copia,** que dice qué cambia y no calza con el patrón de los respaldos.
- **«Las cinco primeras que mostró hoy el portal»:** las cinco primeras de la lista completa, en su orden.
  **«Vigente»:** con su cut-off posterior a la lectura de hoy.
- **La nave y el viaje, tal como los escribe el portal** en el primer tramo. Así CMA-CGM los reconoce (verificado),
  aunque la nave nueva tenga una palabra y la de la fila tuviera dos.
- **Las tres líneas de `CLAUDE.md`:** lo medido hoy en el portal (el clic de MSC, el primer tramo de CMA-CGM y el
  calendario de MAERSK), sin cambiar ninguna regla.

## El repo

Un commit en `main`, sin push (el repo es público; el push lo haces tú): este informe y `CLAUDE.md`. No cambia código ni
pruebas, así que no corrí la suite ni el censo: el código es el de `582924d`, que pasó 828 pruebas en el encargo 67.
Lleva de autor y de committer el correo noreply del repo. La sonda de secretos y el barrido de datos reales dieron 0
antes del commit.

En GitHub, `main` y `estable` están en `582924d` (medido con `ls-remote` al empezar), así que los equipos de los colegas
ya corren el código del encargo 67.
