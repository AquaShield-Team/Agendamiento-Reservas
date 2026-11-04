# Encargo 95 · ONE con la ciudad sola, el contrato de HYUNDAI y la versión en log.txt

**Base:** `AquaShield-Team/Agendamiento-Reservas` @ `a0e27c9` · árbol limpio al recibir el encargo. El cambio va en
`b95e68a`, y este informe, en el commit que le sigue. En GitHub, `main`
en `a0e27c9` y `estable` en `77d5801` (`ls-remote`). Hecho con `metodo-ciclo` v40, la misma del disco.

Datos: las corridas de `logs/` y de `1. pruebas`, que git no sigue, y las corridas en modo prueba que hice el 03-11 desde
este equipo. Las naves y los puertos van con su rol o con un nombre inventado de la misma forma. El contrato de la
cuenta, el nombre del operador y los de las personas no van en este informe ni en ningún archivo del repo: el valor del
contrato se dijo solo en el chat.

## Lo que salió

| Pregunta | Respuesta |
|---|---|
| ONE con la ciudad sola | Elige con la regla de MAERSK, y en el origen solo la de Chile. Si no queda una sola, NO ENVIADA con la regla en el motivo. Medido en 66 listas guardadas y probado en el portal (sección 3). |
| HYUNDAI sin contrato | La decisión de dejar el campo vacío se midió en el portal y no funciona: sin un contrato real, HYUNDAI no deja armar la reserva. Marcelo decidió exigirlo y avisarlo antes de correr: hecho (sección 4). |
| La versión en log.txt | Cada corrida dice, después de su candado, «Versión del programa: <rama> · <commit>» (sección 5). |
| ¿Por qué el colega emitió con una versión vieja? | Emitió con un panel que había abierto antes de que `estable` avanzara. Su lanzador de emisión sí se actualiza desde `estable`: el FRENA SI no se cumple (sección 1). |
| Los 9 informes sin commitear | No existen: los 93 `CICLO-*.md` del repo están versionados (sección 2). |

## 1. Las dos corridas de EMISIÓN del colega

- `estable` pasó a `77d5801` el 03-11 a las 09:31:12, hora de Chile (la actividad de la rama en la API de GitHub).
- Las dos corridas de EMISIÓN del colega son de las 09:27 y las 09:35, y solo traían ONE. La de las 09:27 empezó antes
  de que `estable` avanzara. La de las 09:35 corrió en el mismo panel, abierto antes del push: el panel carga el código
  al abrirse y no lo vuelve a leer. Sus tiempos de ONE son los del código de antes (la sugerencia de ONE, a los 12,6 s
  de escribir; con `77d5801`, a los 8,6 s, como en la corrida de prueba de las 09:44, abierta después).
- Los dos `.bat` corren `actualizar.py` antes de abrir el panel, hoy y en `b39c95c`, la versión de `estable` anterior
  (leído en los dos archivos de cada versión). Así que **el lanzador de emisión sí se actualiza desde `estable`**: el
  colega emitió antes de actualizar, porque no volvió a abrir el programa.
- Para que una versión nueva corra, hay que cerrar el panel y volver a abrirlo con el `.bat`. Desde este encargo,
  log.txt dice la versión de cada corrida (sección 5), y ya no hace falta deducirla.

## 2. Los 9 informes sin commitear

Premisa refutada. Al recibir el encargo, `git status` de este repo estaba limpio, y en la carpeta hay 93
`CICLO-*.md`, los 93 versionados (`git ls-files`). En ningún otro repo de `C:\dev` quedaban 9 informes sin commitear.
No hubo nada que commitear.

## 3. ONE con la ciudad sola (decisión de Marcelo)

**La regla.** Si ninguna opción de la lista dice la celda entera (encargo 94), ONE elige la única opción de la lista a la
vista (`role="option"`, ni tarjeta ni dentro de una de reservas frecuentes) que cumple tres condiciones:

- su texto antes de la primera coma es la ciudad escrita, sin tildes, en mayúsculas y con los espacios de a uno, como
  `_mk_plano` de MAERSK;
- termina en «(CY)», el patio de contenedores;
- en el origen, su última parte antes del paréntesis es CHILE (`ONE_PAIS_DEL_ORIGEN`);
- si la celda trae país (lo que va después de su última coma, sin el paréntesis del final), la opción es de ese país.
  Esta última la decidió Marcelo después de la revisión de seguridad (sección 7).

Si no queda una sola, no pulsa nada y la fila queda NO ENVIADA, con la regla y cuántas la cumplían en el motivo. Hasta
ahí elegía la de más arriba que traía la ciudad: el 03-11 eso fue un lugar de otro país. log.txt dice cuándo eligió con
esta regla. El commodity sigue con la regla de siempre.

**Mira las opciones de la lista, no las candidatas de siempre.** Las candidatas exigen el texto escrito tal cual, con sus
tildes, y no pasan de 55 caracteres. Con ellas, una ciudad escrita con tilde no calzaría aunque la regla quite las tildes,
ni un nombre largo. Lo cambié después de la primera corrida en el portal, y la segunda ya corrió con esto.

**Medido antes del cambio** (`.trabajo/e95/medir_one.py`): la regla sobre el HTML guardado de cada lista, contra la
elección que anotó su log.txt. Control positivo que aborta: la corrida del colega de las 10:24 tiene que dar la de Chile
(CY) en el origen.

| Listas de ONE guardadas | Eligen la misma | Cambian | Sin su elección en log.txt |
|---|---|---|---|
| 66 (de `logs/` y de «1. pruebas») | 57 | 8 | 1 |

Las 8 que cambian son todas el origen con la ciudad sola de las corridas del 03-11, las que habían elegido un lugar de otro
país; ahora eligen el de Chile (CY). Ninguna fila que hoy funciona cambia. Después del cambio suman 4 listas, las de mis
corridas en el portal, todas con la regla.

**Probado en el portal, en modo prueba**, con la ciudad sola en el origen y la nave de una corrida del 03-11: eligió la de
Chile (CY), el destino también por la regla, y llegó a OK-EJEMPLO, en dos corridas (16:03 y 16:08). Antes, con la misma
celda, quedaba REVISAR, «nave no encontrada». Con el código final, a las 20:24, con el país en las dos celdas y sin
«(CY)» (así ninguna opción dice la celda entera): eligió la de Chile (CY) en el origen y la del país de la celda en el
destino, y llegó a OK-EJEMPLO.

**Las pruebas:** la regla en Node, caso por caso (`test_js_one_con_la_ciudad_sola_la_regla_de_maersk`), con la
comparación sin tildes contra `_mk_plano` en los dos sentidos; el recorrido por `_fill_port` y el motivo del corte
(`test_clics.TestOne`); y que `reservar_one` le dice a cada puerto su lugar.

## 4. HYUNDAI sin contrato: la decisión, la medición y lo que quedó

**La decisión que llegó a mitad del encargo:** «Contract No.» es opcional en el portal (no lleva asterisco), y la empresa
no usa contrato; sin contrato, el campo queda vacío y la reserva sigue. Así lo hice (y quitó el aviso previo), y lo probé
en el portal antes de cerrar, como pedía el encargo.

**Lo que midió el portal**, en modo prueba, con la misma fila de HYUNDAI y la misma nave; cada variante, solo en la
memoria del proceso de prueba, sin cambiar la regla del repo ni `config.json`:

| «Contract No.» | «Named Customer» | La mercancía (salmón) | Resultado |
|---|---|---|---|
| el contrato configurado (control, 16:19) | «Direct Input» | la encuentra | OK-EJEMPLO, en 84 s |
| vacío, la regla nueva (16:03) | solo «Select» | — | NO ENVIADA en «Named Customer» |
| vacío, sin tocar «Named Customer» (16:08) | solo «Select» | la búsqueda vuelve vacía | no pasa a «Additional Information» |
| «Dummy» (16:13) | «Direct Input» | vuelve vacía | no pasa |
| «Dummy», con Contract Holder «Not Available» (16:16) | «Direct Input» | vuelve vacía | no pasa |

- En esa pantalla, «Contract No.» lleva el asterisco rojo de obligatorio (en la captura, y `label required` y `required`
  en el HTML), y «Named Customer», no. El portal pide el orden «Contract No. → Named Customer → Commodity», y su texto
  dice que sin contrato se elija «Dummy» con «Not Available»: también lo medí, y tampoco deja.
- Sin un contrato, la ventana de búsqueda de la mercancía queda abierta y vacía, tapa la cantidad y la temperatura, y
  NEXT no avanza.
- **Las reservas de HYUNDAI de Marcelo que llegaron a OK-EJEMPLO** (19 en `logs/` hasta las 16:00 del 03-11) llevaron
  todas el mismo contrato, el de su configuración. De la fila no salió nunca: HYUNDAI no lee el contrato de la planilla.
  Hasta el 2026-10-01 a las 17:23 salió de sus credenciales o del valor que el programa traía escrito. Desde entonces
  sale de sus credenciales o de `contratos_por_defecto`, y cuál de las dos no se sabe sin leer `config.json`, que no
  se leyó. Se recomendó no sacarlo.

**La decisión con la medición:** Marcelo eligió «exigir el contrato y avisar». Quedó así:

- **La regla de `a0e27c9`:** sin contrato, NO ENVIADA en «Contract No», con el motivo que dice dónde se escribe. Con
  uno, como hasta ahora.
- **El contrato sale de un solo ayudante,** `_hmm_contrato`: el de las credenciales, sin los espacios de los extremos,
  o el de `contratos_por_defecto`. Lo usan los pasos 2 y 3 y el panel, así que el aviso dice lo mismo que la reserva.
- **El panel avisa antes de correr:**
  - `/api/config` trae qué operadores no tienen un contrato de HYUNDAI (`sin_contrato`; solo los nombres, el contrato
    no sale);
  - `/api/filas` marca las filas de HYUNDAI con nave y ruta (`pide_contrato`);
  - la página marca esas filas con «sin contrato de HYUNDAI», en su celda «Contrato / Cot.», si el operador elegido no
    tiene uno, y lo dice a la vista, bajo la nota del modo, con dónde se escribe;
  - lo vuelve a pintar al cambiar de operador y al guardar las credenciales, y al armar lo repite con las filas
    elegidas.
- **La corrida no cambia:** esas filas entran al portal y quedan NO ENVIADA en «Contract No», con su motivo.
- El LEEME lo dice así.

## 5. La versión en log.txt

Después de la línea del candado, cada corrida (de reservas, en el panel o en la consola, y de solo login) escribe
«Versión del programa: <rama> · <commit>», la misma que muestra el panel (`VERSION_GIT`, leída al cargar el programa), o
«sin datos de git». En el portal, las corridas de las 16:03 en adelante la trajeron. Lo vigilan `test_modo` y las pruebas
del candado al empezar de `test_web` y `test_consola`.

## 6. Compuertas

**La primera compuerta (`c1`, sobre el primer commit) no dio resultado.** Su suite empezó a las 17:11, y el equipo entró
en espera de las 17:43 a las 20:13 (Kernel-Power 105, cambio de fuente de energía, y 506 y 507), lo que le gana al
pedido de mantenerlo despierto: probablemente se desenchufó o se cerró la tapa. Una suite con ese hueco no vale, y era
del árbol anterior a los arreglos de las revisiones: la detuve (`cerrar_arbol.py`, por su línea de comandos) y corrí
una sola, sobre el árbol final.

**La compuerta 2**, sobre el árbol con los arreglos de las dos revisiones (de 20:26 a 21:20, con 0 eventos de espera
del equipo en ese tramo):

- **La suite:** 1.104 pruebas, OK (1 saltada), en 2.184 s; la foto de los 108 originales, sin cambios.
- **El censo:** 117 mutaciones y 136 pares; 115 muerden. **Dos no muerden:** `e94-one-celda-con-mayusculas` y
  `e94-one-celda-sin-juntar-espacios`, del encargo 94, sobre `test_js_one_elige_la_que_dice_la_celda_entera`.
  - Con esas mutaciones, la celda entera deja de reconocerse.
  - Desde este encargo, la regla de MAERSK elige ahí la misma opción, y la lectura sin pulsar no distingue por cuál
    regla eligió.
  - Le sumé a la prueba un caso que pulsa y mira la marca, « ENTERA» o « REGLA».

**La compuerta 3**, sobre el árbol del commit `b95e68a` (de 21:23 a 22:03; en ese tramo, solo un cambio de fuente de
energía, Kernel-Power 105, sin espera del equipo):

- **La suite:** 1.104 pruebas, OK (1 saltada), en 2.310 s; los originales, sin cambios.
- **El censo:** las 11 mutaciones que nombran la prueba cambiada, 11 muerden, también las dos de antes.

Las 115 mutaciones de la compuerta 2 que mordían no se repitieron: la compuerta 3 cambió solo esa prueba. Después del
clon de la compuerta 3 cambiaron solo el `CLAUDE.md` (el número de pruebas) y este informe, y el código y las pruebas
commiteados son, blob por blob, los que probó.

Antes del commit: la sonda de secretos dio 0 en seco y sobre el índice. La guarda de datos reales del hook dio 0
hallazgos, en 135 archivos.

## 7. Revisiones

**Revisión de código** (`code-reviewer`, Opus), en un clon, sobre el primer commit del cambio: nada crítico ni alto, y
cinco hallazgos bajos.

| Hallazgo | Qué hice |
|---|---|
| Al armar, el aviso del contrato usaba la lista de operadores sin contrato de cuando se abrió la página: con `config.json` cambiado a mano, o credenciales guardadas desde otra pestaña, el aviso mentía hasta recargar. | Arreglado: al armar, la página la vuelve a leer de `/api/config` (`leerSinContrato`). |
| El aviso de «Armar», con una parte de las filas, no se borraba al cambiar a un operador con contrato: no quedaba anotado como el del contrato. | Arreglado: `pintarContrato` recibe las filas y anota el aviso que pinta. |
| `/api/config` podía escribir el aviso de la llave `contratos_por_defecto` que falta en el log.txt de una corrida en curso. | Arreglado: el panel pregunta sin avisar (`avisar=False`). |
| ONE, destino: la regla mira el nombre antes de la coma y «(CY)», no el país de la celda; con la celda «PUERTO X, PAIS A (CY)» y solo «PUERTO X, PAIS B (CY)» en la lista, la elige. | No se cambió: es la regla que Marcelo decidió (la de MAERSK, que compara la parte antes de la coma). Antes del encargo, ahí elegía la de más arriba. Residual. |
| ONE pulsa con la primera lectura que da una sola ganadora; MAERSK espera dos lecturas iguales de la lista. Si ONE mostrara una lista a medias con un tope, podría pulsar una de dos. | No se cambió: no está medido que ONE responda a lo escrito a medias ni que limite su lista. En las 66 listas guardadas, ninguna. Propuesta en el RESIDUAL. |

Comprobó en Node: las dos ganadoras (no pulsa), las ocultas, las que no son de la lista, las tarjetas, la Ñ y las tildes,
el commodity igual que antes, y que nada actúa después de la guarda.

**Revisión de seguridad** (`security-reviewer`, Opus), en otro clon, sobre el árbol con los arreglos de la de código:
nada crítico ni alto. Que el contrato, la clave y el usuario no salen por la API nueva ni por el motivo, que no hay
inyección de HTML (el aviso va por `textContent`), que la línea de versión solo lleva la rama y el commit, y que nada
actúa después de la guarda: leído y, la regla de ONE, ejecutado en Node.

| Hallazgo | Qué hice |
|---|---|
| **Medio.** ONE, destino con país en la celda: con «VALENCIA, SPAIN» y solo «VALENCIA, CARABOBO, VENEZUELA (CY)» en la lista, la elegía y armaba la reserva a otro país. | Pregunté: Marcelo decidió exigir el país de la celda cuando lo trae. Hecho, con sus pruebas y mutaciones. Medido antes (`.trabajo/e95/medir_pais.py`): de las 70 listas guardadas, 4 celdas traen país, todas orígenes de Chile, y no cambia ninguna. |
| Bajo. El motivo nuevo llevaba la ciudad de la planilla sin sanear; un carácter de control no se escribe en la planilla. | Arreglado: la ciudad y el país van con `_destino_a_la_vista`, también en el motivo de siempre del autocompletado y en log.txt. |
| Bajo. «Una sola» se decide con una lectura, sin esperar la lista quieta (el mismo de la revisión de código). | Residual, con la propuesta. |
| Bajo. La rama de la celda entera (encargo 94) toma la de más arriba si dos opciones la dicen igual. | Residual: dos opciones con el mismo texto no se vieron en las listas guardadas. |
| Bajo. La regla cuenta todas las opciones de la página, no solo la lista del campo, y «a la vista» es `offsetParent`. | Residual: en los 23 HTML de ONE medidos, `role=option` lo llevan solo los botones de su lista; y otra lista suma ganadoras, lo que lleva a NO ENVIADA. |
| Bajo. Si Windows niega un instante la lectura de `config.json`, el panel podría marcar a un operador sin contrato. | Residual: solo el aviso; la reserva lee el contrato otra vez al correr. |

## 8. Después del cierre: la fila de HYUNDAI sin contrato no entra al portal

**La decisión de Marcelo:** una fila de HYUNDAI cuyo operador no tiene contrato queda NO ENVIADA sin entrar al portal,
igual que la fila sin nave, con el motivo claro en el panel. El contrato de su configuración se queda.

**Lo que quedó:**
- `_falta_el_contrato` da el motivo si la naviera es HYUNDAI y `_hmm_contrato` no da un contrato: «el operador no tiene
  un contrato de HYUNDAI, y sin él el portal no deja armar la reserva: se escribe en el panel → Credenciales → HYUNDAI →
  columna Contrato». No nombra al operador ni dice un contrato, porque va a la planilla.
- El panel web y la consola apartan esas filas antes de abrir el navegador, después de la fila que pide otro contenedor,
  y las dejan NO ENVIADA con el motivo, en pantalla, en log.txt y en la planilla (`_sin_el_contrato`). Sin contrato, no
  abren el navegador para HYUNDAI.
- `reservar_hyundai` lleva `_hmm_con_el_contrato`, por dentro de todos sus decoradores, como el del contenedor de MAERSK:
  cuida cualquier otro camino. El corte de «Contract No» queda de resguardo.
- El aviso de la página dice «quedan NO ENVIADA, sin entrar al portal».

**Probado en el portal, en modo prueba, desde este equipo**, con la fila de HYUNDAI de siempre:
- sin contrato (solo en la memoria del proceso de prueba): NO ENVIADA a los 2 s, con el motivo, sin abrir el navegador;
- con el contrato configurado: OK-EJEMPLO a los 78 s, como antes.

**Las pruebas:** `test_ayudantes.TestSinContratoHyundai` (el motivo, el decorador sin tocar la página, la fila sin nave o
sin ruta, y con contrato pasa igual), `test_web` y `test_consola` (`test_hyundai_sin_contrato_no_abre_el_portal`: sin
contrato no se abre el navegador, y con contrato va al portal), la lista de decoradores de `test_clics` y el aviso de
`test_envio`. Corridas antes de la compuerta: las 551 pruebas de `test_clics`, `test_ayudantes` y `test_evidencia`, OK.

**Revisión de código** (`code-reviewer`, Opus), en un clon: aprobado, nada crítico, alto ni medio, y tres hallazgos
bajos, los tres arreglados.

| Hallazgo | Qué hice |
|---|---|
| Ninguna prueba corría CONSOLIDADO con un operador sin contrato: el panel podía apartar también las filas de las otras navieras sin que nada cayera. | Arreglado: en el panel, CONSOLIDADO con el operador sin contrato aparta solo la fila de HYUNDAI; en la consola, el mismo operador en ONE va al portal. Con sus mutaciones. |
| Con un `config.json` sin la llave de `contratos_por_defecto`, salía «sigo sin contrato por defecto» y, justo después, la fila no seguía. | Arreglado: la fila que no entra pregunta sin avisar; su motivo dice dónde se escribe el contrato. |
| Un párrafo del `CLAUDE.md` seguía describiendo el corte en «Contract No» como vigente. | Arreglado. |

La primera compuerta de esta parte la detuve, porque corría sobre el árbol de antes de estos arreglos.

**Revisión de seguridad** (`security-reviewer`, Opus), en otro clon, sobre el árbol con esos arreglos: nada crítico ni
alto. El cambio solo agrega salidas tempranas con NO ENVIADA, no toca el candado, y el motivo no lleva el contrato, la
clave, el usuario ni el nombre del operador. Tres hallazgos bajos:

| Hallazgo | Qué hice |
|---|---|
| Un contrato que no es texto (una lista, `true`, escrito a mano en `config.json`) o solo de caracteres invisibles (pegado en Credenciales) pasaba el filtro: la fila entraba al portal y se cortaba en el paso 3. | Arreglado: `_hmm_contrato` cuenta solo un texto o un número con al menos una letra o una cifra, en las credenciales y en `contratos_por_defecto`. Con sus pruebas y mutaciones. |
| Si `config.json` no se lee en ese instante, o su `contratos_por_defecto → hyundai` no es texto, y el operador usa ese contrato, todas las filas de HYUNDAI de la corrida quedan NO ENVIADA con el motivo que manda al panel, sin aviso de que `config.json` está mal. | Residual: falla hacia el lado seguro, y la plantilla trae la llave como texto. |
| El docstring del decorador decía que «cuida cualquier otro camino», pero corre después del inicio de sesión. | Arreglado: lo dice. |

**La compuerta 5**, sobre el árbol con los arreglos de las dos revisiones (de 22:51 a 23:43, sin eventos de espera del
equipo; corrían a la vez suites de otras sesiones, de Control Congelado y de Fresco):

- **La suite:** 1.110 pruebas, OK (1 saltada); los originales, sin cambios.
- **El censo:** 64 mutaciones, 63 muerden. **No muerde `e95b-contrato-invisible`:** la última comprobación de
  `_hmm_contrato` también descarta un contrato invisible, así que la prueba no distinguía la primera.
  - La primera hace falta en un solo caso: el contrato propio es invisible y hay uno de verdad en
    `contratos_por_defecto`, que es el que va.
  - Le sumé ese caso a la prueba.

**La compuerta 6**, sobre el árbol que se commitea (de 23:46 a 00:17, sin eventos de espera del equipo):

- **La suite:** 1.110 pruebas, OK (1 saltada); los originales, sin cambios.
- **El censo:** las 6 mutaciones que nombran la prueba cambiada, 6 muerden, también `e95b-contrato-invisible`.

Antes del commit, la sonda de secretos y la guarda de datos reales del hook (sección 6, el mismo procedimiento).

## Decisiones que tomé solo

- Le pregunté a Marcelo dos veces a mitad del ciclo, con lo medido: qué regla dejar para HYUNDAI sin contrato (sección 4)
  y si exigir el país de la celda en ONE (sección 7).
- La regla de ONE mira las opciones de la lista a la vista, no las candidatas de siempre (sección 3).
- Medí «Dummy» y «Not Available» con «Dummy» antes de llevarle la decisión a Marcelo, solo en memoria y en modo prueba.
- La marca de la fila sin contrato va en la celda «Contrato / Cot.», no junto a «Reserva N»: ahí ya va la del
  contenedor, y la de HYUNDAI es del contrato.
- El aviso del contrato, al cambiar a un operador que lo tiene, se borra de la vista solo si sigue siendo el suyo: si ya
  hay otro aviso a la vista, no se toca.

## Lo que decide Marcelo

- **Si la fila de HYUNDAI sin contrato debe quedar NO ENVIADA sin entrar al portal,** como la fila sin nave. Marcelo lo
  decidió después del cierre: no entra (sección 8).
- **Que no saques el contrato de tu configuración:** según lo medido, sin él HYUNDAI no arma ninguna reserva.

## RESIDUAL

- El aviso del panel no se probó en un navegador: lo cubren las pruebas en Node (la función y la marca) y las de la API.
- La comparación sin tildes del JavaScript de ONE y `_mk_plano` coinciden en los textos probados. Una marca de Unicode
  con clase de combinación 0 (raras en nombres de lugares) se quita en JavaScript y no en Python.
- ONE con la ciudad sola corta si su destino no se ofrece como «(CY)». En las 66 listas, todos los destinos lo traían.
- Que la búsqueda de la mercancía de HYUNDAI dependa del contrato se midió con una fila, un día y cuatro variantes.
- Las marcas «sin contrato de HYUNDAI» de la tabla se repintan al cargar la hoja, al cambiar de operador, al guardar las
  credenciales y al armar: un `config.json` editado a mano con el panel abierto se ve en el siguiente de esos momentos.
  Abrir Credenciales y cancelar borra el aviso de la vista; las marcas de las filas quedan.
- La rama de la celda entera toma la de más arriba si dos opciones dicen la celda igual, y la regla cuenta las opciones
  de toda la página, no solo las de la lista del campo (revisión de seguridad; ver la tabla de la sección 7).
- Una lectura de `config.json` que falla un instante puede marcar a un operador sin contrato, y, desde la segunda
  parte, dejar NO ENVIADA, sin entrar al portal, cada fila de HYUNDAI de esa corrida cuyo operador usa el contrato de
  `contratos_por_defecto` (revisión de seguridad de la segunda parte): el lado seguro.
- ONE pulsa con la primera lectura que da una sola ganadora. Propuesta: esperar dos lecturas iguales, como MAERSK, si
  algún día se ve una lista a medias.
- Una celda de más de 55 caracteres nunca llega a «dice la celda entera» (las candidatas no pasan de 55; encargo 94): cae
  en la regla de MAERSK.

## Re-medir

- ONE: `.trabajo/e95/medir_one.py` sobre las listas nuevas (sale con el control de las 10:24 del 03-11).
- HYUNDAI: si el portal cambia su pantalla del paso 3, volver a mirar el asterisco de «Contract No.» y la mercancía sin
  contrato.

## NO retroceder

- ONE con la ciudad sola no vuelve a «la de más arriba que trae la ciudad»: el 03-11 eligió otro país en 5 corridas.
- HYUNDAI no sigue sin contrato: el portal no deja armar la reserva.

## Defectos de instrumento que me cacé

- La prueba de `_hmm_contrato` no distinguía las dos comprobaciones del contrato invisible: lo vio el censo de la
  compuerta 5, con una mutación que no mordía (sección 8).
- La prueba de la celda entera de ONE (encargo 94) dejó de distinguir la celda entera de la regla nueva, que elige la
  misma opción: lo vio el censo, con dos mutaciones que no mordían (sección 6).
- `medir_pais.py` tomaba la celda desde el primer corchete de la línea de log.txt, el de la hora, y no desde el de la
  fila: su control positivo (la de Chile en el origen del colega de las 10:24) abortó, y lo corregí.
- `medir_one.py`, en su primera versión, tomaba la elección de la fila siguiente cuando una fila no tenía la suya:
  ahora se detiene en la línea de la fila que sigue.
- `contrato_hmm.py` no encontró ninguna reserva de HYUNDAI en su primera versión (sus filas no van como «[fila N]»),
  y su control positivo abortó: ahora recorre los bloques «Reserva i/n».
- El primer envoltorio de la medición sin «Named Customer» habría roto las llamadas posicionales a
  `_hmm_comprobar_la_unica`: lo vi al leerlo, antes de correrlo.
- La lectura de las etiquetas del paso 3 de HYUNDAI con expresiones regulares no dijo cuál era obligatoria: lo dijeron
  el HTML crudo de cada etiqueta y la captura.

## Premisas del encargo que se refutaron

- «Contract No. es opcional en el portal (no lleva asterisco)»: lleva el asterisco, y sin contrato el portal no deja
  armar la reserva.
- «Los 9 informes de ciclo que la limpieza dejó sin commitear»: no hay ninguno.

## Reglas aplicadas (pieza 7)

`metodo-ciclo` v40: control positivo que aborta en cada sonda (`medir_one.py`, `contrato_hmm.py`, `puertos.py`,
`obligatorios.py`, `etiquetas.py`); la medición sobre el camino real (el portal, en modo prueba, con el control con el
contrato configurado); FRENAR ante una decisión de negocio cuya premisa la medición contradice; datos reales solo en el
chat; los revisores en un clon; la compuerta sobre el árbol del commit; nunca EMISIÓN.
