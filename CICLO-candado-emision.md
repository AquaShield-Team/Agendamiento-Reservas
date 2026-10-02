# CICLO · Blindaje del candado de emisión

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-23 · **Método:** skill `metodo-ciclo` v12 ·
**Commit:** el de este cierre (local, sin push) · **Base:** `76b3607`.

> Sin datos reales: los valores de ejemplo del aviso son genéricos. Las corridas de `logs/` se leyeron en
> su lugar y en solo lectura; de ellas este informe cita **qué pantalla** se vio en cada paso, nunca naves,
> rutas, números de reserva ni personas.

## Veredicto

- **Llave de config arreglada.** `emitir_reservas` abre el candado **solo con el booleano JSON `true`**.
  Cualquier otro valor (texto, número, `"true"` entre comillas, `null`, lista u objeto) deja el candado
  cerrado y avisa en pantalla y en el log, en español con tuteo. Las otras dos llaves y la regla de que
  cualquiera de las tres abre quedaron igual.
- **HYUNDAI: ninguno de los 10 textos previos a la guarda envía la reserva.** Cinco no son acciones
  (mensajes de log, rótulos y motivos de espera); dos son esperas a que aparezca una pantalla; los otros
  tres son pasos intermedios: la elección del itinerario, la aceptación del aviso reefer y el avance a
  Review. La evidencia está en el código y en las 5 reservas de la única corrida de HYUNDAI que hay en
  `logs/`. Tiene límites, que declaro abajo, pero ninguno es una señal de envío.
- **No se cumplió ningún FRENA SI:**
  - la evidencia alcanza para descartar el envío antes de la guarda;
  - el arreglo cambia solo la lectura de la llave y el aviso que se decidió. El anotado de los registros
    abiertos es la vía del aviso hacia el log; va declarado aparte.
- **PASO 0: CICLO, cerrado.**

## El arreglo de la llave

| Valor de `emitir_reservas` | Antes | Ahora |
|---|---|---|
| `true` (booleano) | abre | abre, sin aviso |
| `false` o clave ausente | cerrado | cerrado, sin aviso |
| `"false"` (texto) | **abría** | cerrado y avisa |
| `"true"` (texto) | **abría** | cerrado y avisa |
| `1` y otros números distintos de 0, textos no vacíos | **abrían** | cerrado y avisa |
| `0`, `""`, `null`, `[]`, `{}` | cerrado, en silencio | cerrado y avisa |

**El aviso** (el valor va escrito tal como está en el JSON):

> ⚠ Candado de emisión: en config.json, «emitir_reservas» vale "false" y solo se abre con true (sin
> comillas). Lo dejé cerrado: no se emite ninguna reserva. Si quieres emitir, escribe true; si no, false.

**Dónde aparece.** El programa consulta el candado en dos momentos: al cargar el panel web (`/api/config`)
y en la guarda de cada reserva.
- Con una corrida en curso, el aviso sale por el `Registro` de la corrida: queda en su `log.txt`, en su
  consola y en la pantalla que la muestre (el registro del panel web o la ventana Tkinter).
- Sin corrida, por ejemplo al abrir el panel, sale por la consola y por el registro del panel web, que se
  ve en pantalla en menos de un segundo.

**Lo que cambió en `AQUASHIELD.py`** (36 líneas agregadas y 2 cambiadas; LF conservado; compila):
1. En `es_modo_emision()`, la rama de config: `valor is True` abre; `valor is not False` avisa. El orden
   sigue siendo entorno, argumento y config, y nada más cambió en la función.
2. Una función nueva, `_avisar_llave_config(valor)`, que arma y reparte el aviso.
3. `Registro` anota en un `WeakSet` los registros abiertos y los saca en `cerrar()`. Es la vía del aviso
   hacia el log de la corrida; el resto de `Registro` no cambió.
4. `import weakref`.

**Lo que no cambió:** las llaves de entorno y de argumento, la regla de que basta una llave, las 6 guardas
y quién consulta el candado. La red lo demuestra: todas las pruebas anteriores pasan sin tocarse, salvo las
2 que fotografiaban la lectura vieja, que se reemplazaron en el mismo cambio.

**En la red:**
- Se reemplazaron `test_llave_config_sola_abre` (el 1 abría) y `test_config_con_texto_false_abre` por
  `test_llave_config_abre_solo_con_true` y `test_llave_config_con_otro_valor_no_abre_y_avisa`, que prueba
  9 valores con el texto exacto del aviso en pantalla y en consola.
- Se agregaron `test_aviso_va_al_log_de_la_corrida` (el aviso entra al `log.txt` y a la pantalla de la
  corrida, y vuelve al panel al cerrarla) y `test_llave_invalida_se_avisa_en_pantalla`, que va de punta a
  punta: con `"true"` entre comillas, el panel dice «Modo Seguro» y muestra el aviso en su registro.
- Se quitó 1 mutación, cuyo texto ya no existe, y se agregaron 9, una por cada pieza nueva: la condición,
  el aviso, su texto, su consola, su panel, la vía por el Registro, el anotado y el desanotado.

## HYUNDAI: dictamen de los 10 textos previos a la guarda

La guarda de HYUNDAI está en Review & Book. El único botón que crea la reserva es «Create NOW», y el
código solo lo pulsa **después** de la guarda.

| # | Texto (como lo fotografía la red) | Qué hace en el código | Evidencia en la corrida | Dictamen |
|---|---|---|---|---|
| 1 | `button:has-text('Book Now'), a:has-text('Book Now'…` (2 lugares) | Espera y comprueba que aparezca la lista de itinerarios; no hace clic | La captura del paso 02 muestra «Sailing Schedule Result» con un botón «Book Now» por itinerario | Espera, sin acción |
| 2 | `botón Book Now` | Rótulo del itinerario elegido, para el log y el detalle | — | Texto, sin acción |
| 3 | `nave elegida y botón Book Now presionado:` | Mensaje de log. El clic real a «Book Now» está en el JavaScript `_JS_HMM_INDICE_NAVE` y elige la salida | Tras el clic sigue el aviso «Alternate Vessel Option» y la captura del paso 03 dice «Booking Input (NEW)»: un formulario vacío | **Paso intermedio** (elegir itinerario) |
| 4 | `button:has-text('Confirm'), .btn:has-text('Confirm…` (2 lugares) | Clic al «Confirm» del aviso «Warning (Reefer Undertaking)», después de NEXT a Additional Information | En 5 de 5 reservas el log dice «Confirmado (Confirm)». La captura del paso 04, tomada después, dice «Booking Input (NEW)», con «NEXT - Review & Book» y «Save for Later» sin pulsar | **Paso intermedio** (aceptar el aviso reefer) |
| 5 | `Modal 'Warning (Reefer Undertaking)': Confirmado (` | Mensaje de log | — | Texto, sin acción |
| 6 | `()=>{ const btns = [...document.querySelectorAll('` | Respaldo en JavaScript del mismo «Confirm»: pulsa el primer elemento visible cuyo texto es exactamente «confirm» | No se usó en ninguna de las 5 reservas (siempre bastó el clic normal). En la captura del paso 04 no queda ningún «Confirm» visible | **Paso intermedio**; su camino no se observó en la práctica |
| 7 | `Paso 5 · Avanzando a Review & Book...` | Mensaje de log | — | Texto, sin acción |
| 8 | `NEXT - Review & Book` | Clic de navegación al paso 05 | La captura del paso 05, tomada justo antes de la guarda, dice «Booking Input (NEW)», sin número y con «Create NOW» pendiente. Así en la primera y en la última reserva | **Paso intermedio** (navegar) |
| 9 | `-> Review & Book` | Motivo de ese mismo clic, para el log | — | Texto, sin acción |
| 10 | `pantalla Review & Book` | Motivo de la espera a que aparezca «Create NOW»; espera, no hace clic (`esperar_hasta` solo usa `wait_for_selector`) | — | Espera, sin acción |

**Otros clics antes de la guarda**, que no están en la lista de 10 porque sus textos no dicen «Book» ni
«Confirm»:
- los NEXT entre pasos y «Retrieve», que busca itinerarios;
- el OK del aviso «Alternate Vessel Option» (`#vesselOptionSubmit`: el «Submit» es parte del id del botón,
  no un envío);
- la selección de embarcador y de mercadería en sus ventanas;
- radios y la opción «Non-waste».

Todos ocurren en pantallas que siguen diciendo «Booking Input (NEW)».

**Evidencia decisiva:**
1. En las 5 reservas de la corrida del 21-09, hecha en modo emisión real, el número de reserva aparece
   **solo después** de «Create NOW», con el aviso del propio portal: «A Tentative Booking has been created».
2. Las capturas de los pasos 02 a 05 dicen «Booking Input (NEW)». La del paso 05 muestra «Create NOW» sin
   pulsar.
3. En todo el código de HYUNDAI no hay ningún clic a «Save for Later» (borrador), a «Save as Template» ni a
   «Create». Antes de la guarda, «Create NOW» solo aparece como algo que se espera.

**Límites de la evidencia** (ninguno es una señal de envío):
- Offline no se ve el estado del servidor de HMM (si guardara algo en silencio, no se vería).
- El respaldo JavaScript del «Confirm» no se ejecutó en ninguna corrida.
- Hay una sola corrida de HYUNDAI, en modo emisión; no hay ninguna en modo seguro que permita revisar
  después «My Export» en el portal.
- De las 5 capturas del paso 05 miré la primera y la última; las otras 3 las respalda el log, que repite la
  misma secuencia.

## Universo y cobertura (pieza 3)

- **Evidencia de HYUNDAI:** 6 carpetas en `logs/`, y HYUNDAI aparece en 1: la corrida «todas» del 21-09,
  con 5 reservas y 36 capturas. Hay 0 archivos HTML guardados y 0 trazas.
  - Del log se leyeron las 281 líneas de la sección HYUNDAI: 5 de 5 reservas con la misma secuencia.
  - Capturas miradas: los pasos 02, 03, 04, 05 y 06 de la fila 25, y el paso 05 de la fila 29.
- **Código:** los 10 textos; 40 líneas con clics o eventos antes de la guarda (más el clic dentro de
  `_JS_HMM_INDICE_NAVE`); 0 clics a guardar o crear.
- **Red:** 116 pruebas; 158 mutaciones; 182 pares, todos muerden; 0 pruebas sin
  mutación. La copia sin mutar pasa. Los originales no cambiaron en ninguna corrida completa.
- **Secretos:** la sonda sobre el staging dio 0 antes del commit.

## Re-medir (pieza 1)

```powershell
python tests\correr.py --todo
python tests\sonda_secretos.py --dry-run
cd tests; python -m unittest test_candado test_web.TestPanelRutas.test_llave_invalida_se_avisa_en_pantalla
```

Para HYUNDAI: la sección entre «INICIANDO HYUNDAI» e «INICIANDO MAERSK» del `log.txt` de la corrida
«todas» del 21-09, y sus capturas `hmm_f25_*` y `hmm_f29_5_review`, leídas en su lugar.

## NO retroceder (pieza 2)

- **No vuelvas a leer la llave como verdadero o falso a secas** (`if valor:`): así era como el texto
  «false» abría el candado.
- **No pulses «Save for Later» ni «Save as Template» en HYUNDAI antes de la guarda:** dejarían algo
  guardado en el portal.
- **Todo texto nuevo antes de una guarda tumba la prueba de esa guarda,** porque la red fotografía la lista.
  Antes de actualizar la foto, hay que dictaminarlo como en este informe.

## Defectos de instrumento cazados (pieza 4)

1. **Copié 5 capturas reales de HYUNDAI a `%TEMP%` para mirarlas.** No hacía falta: se leen en su lugar. La
   copia se borró en seguida.
2. **Mi expresión para buscar botones de envío atrapó mensajes de log y motivos de espera.** 5 de los 10
   «textos» no son acciones, y el dictamen los separa. Al revés, la expresión no veía clics como NEXT o el
   OK de «Alternate Vessel Option», que se revisaron aparte.

## Premisas del encargo contrastadas (pieza 5)

- **«HYUNDAI tiene 10 textos Book Now/Confirm antes de su guarda y no se sabe si alguno envía»:** eran 10
  textos, pero solo 3 acciones reales (Book Now, el Confirm del aviso reefer y el NEXT a Review). Ninguna
  envía.
- **«"emitir_reservas": "false" lo abre»:** confirmado antes del arreglo. También abrían el número 1 y
  `"true"` entre comillas. Ahora no abre ninguno.
- **«Con las tres apagadas no emitió en 540 combinaciones»:** sigue igual. Ahora, además, los valores 0 y
  "" de esas combinaciones avisan.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| El estado del servidor de HMM tras los pasos intermedios | No se ve offline | …en «My Export» de HMM aparece una reserva que nadie creó con «Create NOW» |
| El respaldo JavaScript del «Confirm» de HYUNDAI | No se ejecutó en la corrida | …el log de una corrida dice «Confirmado (js)» |
| Si la llave de entorno o la de argumento abren, la de config no se lee y su valor inválido no se avisa | El orden de las llaves no cambió, por decisión | …se quiere avisar siempre que la config sea inválida |
| El aviso se repite en cada consulta del candado: cada reserva y cada carga del panel | Es simple y no se pierde ninguno | …resulta ruidoso |
| El camino de emisión después de cada guarda | Por diseño, la red nunca lo ejecuta | …se cambia una guarda |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v12**:
- **Re-medir contra HEAD antes de diseñar;** el PASO 0 revisó el panel y los logs.
- **El cambio y su guardián, en la misma operación:** cada pieza nueva entra con su prueba y su mutación.
- **El negativo tiene que morder, de a uno por llamada.**
- **Control positivo que aborta:** la copia sin mutar pasa.
- **Todo registro es una hipótesis:** los 10 textos, contrastados uno por uno.
- **La unidad de la medición la fija el sujeto:** el sujeto es la acción, no el texto; por eso se separan
  los clics de los mensajes.
- **Se declaran el residual y las premisas refutadas.**
- **FRENAR:** se evaluó con evidencia y no hizo falta.
- **El push se entrega, no se hace:** no hay remoto, así que no hay nada que entregar.

Reglas propias del módulo, las de `CLAUDE.md` para la red: nunca importar el programa desde la raíz, nunca
el puerto 8765, toda prueba con su mutación y la sonda antes del commit. **Choques: ninguno.**

## Entregable (pieza 8)

Este `.md`, sin renderizar. Pasa la sonda de staging antes de su commit.
