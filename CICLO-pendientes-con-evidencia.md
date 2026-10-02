# CICLO · Los pendientes de CMA, MAERSK y HYUNDAI, con la evidencia de la corrida «todas»

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-25 · **Método:** skill `metodo-ciclo` v13 ·
**Base:** `1e8d510` (último de código: `eb94499`) · **Commits** (locales, sin push; el repo no tiene remoto): uno por
naviera cambiada, `e423a38` (CMA) y `72f932c` (HYUNDAI), y el de este informe.

> Sin datos reales. La corrida se midió en su carpeta de `logs/` y en solo lectura, con sondas que imprimen conteos,
> estados del programa, etiquetas y textos de interfaz con los dígitos y las palabras en mayúsculas enmascarados.
> Aquí no van naves, rutas, fechas de itinerarios, contratos ni nombres.

## El candado aguantó

La carpeta de corrida más reciente es la corrida «todas» del 2026-09-25 a las 00:29: 90 archivos, un `log.txt` de 320
líneas y 44 HTML. Es posterior a `eb94499`: trae `hmm_f25_remark.*`, que solo ese código deja.

- Estados: 3 OK-EJEMPLO, 2 REVISAR y 1 NO ENVIADA. **0 EMITIDA y 0 ENVIADA.**
- 0 líneas de la rama de emisión («MODO EMISIÓN REAL», «EMISIÓN: Pulsando…») y 0 archivos `_confirmado`.
- Los 3 que llegaron a su guarda (MSC, CMA y HYUNDAI) dicen «Me DETENGO» y dejaron su `_guarda.*`. Los otros 3 se
  detuvieron antes de la guarda.

El primer freno no se cumplió: ningún clic en el envío final.

## Las seis navieras

| Naviera (fila) | Estado | Dónde terminó | Avisos |
|---|---|---|---|
| ONE (5) | REVISAR | Itinerarios: la nave de la fila no está entre los 32 resultados | La espera de resultados salió «sin señal» a los 8 s; la lista llegó después |
| MSC (10) | OK-EJEMPLO | Summary, su guarda | Ninguno a la vista. «The Quote is expired», «Instant Booking…» y «Required» siguen en la página, ocultos, como el 24 |
| CMA (15) | OK-EJEMPLO | «Envío de la reserva», su guarda | ⚠ «No pude confirmar la ruta» (el portal no respondió a «Validar ruta»). A la vista: «Completar la configuración de Recogida vacía mejorará el tiempo de procesamiento de su reserva.» |
| COSCO (20) | NO ENVIADA | Lista de itinerarios: 2 calzan con la nave y la fila no trae día de carga | ✗ ese motivo. El puzzle del login se resolvió al tercer intento |
| HYUNDAI (25) | OK-EJEMPLO | Review & Book, su guarda | Ninguno |
| MAERSK (30) | REVISAR | «Select sailing»: la nave de la fila no está entre las 5 salidas | Buscó desde mañana: la fila no trae un día de carga legible |

## Los pendientes

### CMA: hecho en `e423a38`

Medido en `cma_f15_reefer_panel.html`, `_reefer_guardado.html` y `_guarda.html`:
- **El panel:** 1 visible de 12 candidatos del selector (`reefer-drawer el-drawer rtl open`). Trae 8 campos y un
  textarea: Modo Reefer, Temperature, Unidad, Ventilación, Deshumidificación, Atmósfera controlada, Genset requerido y
  Tratamiento de frío. **Solo el bloque `.el-form-item` cuya `.el-form-item__label` dice «Temperature» es el de la
  temperatura.**
- **El botón de guardar:** el panel trae «Guardar» y «Cancelar», y ese «Guardar» es el único de la página.
- **La sección queda completa:** la insignia del renglón Reefer pasa de «to complete» a «completed».
- **«I Agree» existe en la revisión:** es una casilla obligatoria del bloque de alerta de «Envío de la reserva». Al
  marcarla, el bloque sale del HTML: la guarda ya no la trae. **El paso se queda.**
- **El aviso «Faltan algunos ajustes para carga(s) especial(es)»:** está a la vista con el panel abierto y desaparece
  al guardarlo.
- **El freno no se cumplió:** el panel quedó completo solo con la temperatura, que sale de `config.json`, y sin clics
  nuevos.

El cambio:
- La temperatura se busca solo por esa etiqueta, dentro del único panel visible. Ya no bastan su placeholder, un «°C»
  ni la palabra dentro de otra etiqueta, y con dos «Temperature» corta sin elegir.
- Se guarda con el único «Guardar» a la vista, y solo si es de ese panel. Se quitó el respaldo por JavaScript, que
  pulsaba el primer «Guardar», «Save», «Confirm» o «Confirmar» de cualquier cajón, también de uno oculto: era un
  residual de `CICLO-cola-nueve-items.md`.
- La escritura de la temperatura y el clic de Playwright en «Guardar» son los mismos de antes.

### HYUNDAI: hecho en `72f932c`

Medido en `hmm_f25_remark.html`:
- La pantalla trae 10 textarea y 9 están ocultos: el Remark de carga especial y 8 de commodity.
- El visible no tiene id, name ni clase: no hay atributo propio.
- Su etiqueta es el título del recuadro, el `.box-title` «Remark (n / m)» con su contador de caracteres. El formulario
  que los contiene trae ese solo título y ese solo textarea.
- El marco trae un chat de ayuda, con sus propios textarea. El Remark nunca se escribió ahí.

El cambio: el Remark se escribe en el único textarea del formulario con ese título (`_JS_HMM_REMARK`, desde
`_hmm_remark`), igual que antes: foco, valor y los eventos input y change, sin clics. Si falta el título, hay más de
uno, el formulario no trae un solo campo o el campo está oculto, no escribe en otro y corta. `reservar_hyundai` lleva
`_sin_clic_a_ciegas("hmm")`, así que la reserva queda NO ENVIADA con captura y HTML. **Se cierra el FRENO del encargo
21.** Nunca se usa el `style`.

### MAERSK: FRENO, la evidencia no alcanza

- **No llegó a la revisión:** se detuvo en «Select sailing», en REVISAR, sin la fecha de retiro. El freno de «NO ENVIADA
  en la revisión porque el portal no avanzó» no aplica: no hubo revisión.
- **La casilla de términos no se puede identificar:** falta el HTML de la revisión (`mk_f<fila>_guarda.html`). «El
  último checkbox» sigue como estaba, con su FRENO.
- **Qué falta:** una corrida en que MAERSK llegue a la revisión, con una fila cuya nave esté en las salidas del portal
  y con día de carga.

### COSCO: reportado

Quedó NO ENVIADA con la lista guardada (`cosco_f20_itinerarios.*`). Calzan 2 itinerarios con la nave, los dos con
transbordo, y la fila no trae día de carga para elegir: es la regla que decidiste en el encargo 21. No eligió ninguno.

### ONE: reportado

No llegó a Review Booking. La lista de resultados cargó entera: 32 tarjetas, con su nave y su viaje. La nave de la fila
no está: 0 veces entera, 0 sin el viaje, 0 el viaje solo, y su palabra distintiva no aparece ni una vez.

## Hallazgos nuevos (se reportan; no se implementan)

1. **Las naves de ONE y MAERSK no estaban en los itinerarios del portal.** No es el programa comparando mal:
   - en ONE, la palabra distintiva de la nave aparece 0 veces en 32 resultados;
   - en MAERSK, 0 veces en 5 salidas.
2. **Las filas de COSCO y MAERSK no traían un día de carga legible.** COSCO no pudo elegir entre dos itinerarios, y
   MAERSK buscó desde mañana.
3. **CMA sugiere completar la «Recogida vacía».** «Configuración de liberación de vacío» queda «Not Filled» antes y
   después. El aviso de carga especial no la pide, y el portal dice que completarla «mejorará el tiempo de
   procesamiento».
4. **El panel Reefer de CMA tiene su clase propia, `reefer-drawer`.** Hoy se reconoce por ser el único visible.
5. **En ONE, la espera de resultados vence a los 8 s «sin señal».** En esta corrida la lista llegó después. No se midió
   si ya estaba cuando se buscó la nave.

## Expectativas que cambiaron (antes → ahora)

| Prueba | Antes | Ahora |
|---|---|---|
| `test_clics.TestCma.test_js_temperatura_solo_por_su_etiqueta` | «Temperatura (°C)» o un placeholder «Temperature» daban «ok» | Solo la etiqueta «Temperature»; placeholder, «°C» o la palabra en otra etiqueta dan «sin-campo», y dos dan «varios-campos» |
| `test_clics.TestCma.test_js_temperatura_solo_en_el_panel_visible` | Campos sueltos con su texto | Los mismos casos, con bloques `.el-form-item` y su etiqueta, como se midió |
| `test_clics.TestCma.test_js_guardar_dice_si_pulso` | El JavaScript pulsaba el primer «Guardar/Save/Confirm/Confirmar» de cualquier cajón | Pasa a `test_js_guardar_solo_si_es_del_panel_visible`: no pulsa y dice si el botón es del panel visible |
| `test_clics.TestCma.test_reefer_corta_en_cada_paso_sin_pulsar_a_ciegas` | El motivo decía «por su etiqueta o su placeholder»; guardar cortaba si no había botón | El motivo nuevo, el caso «varios-campos», y guardar corta también si el «Guardar» a la vista no es del panel; mira el filtro pedido |
| `test_evidencia.TestEvidenciaReefer` | Guardar era un clic; `test_tambien_si_guarda_el_javascript` | Guardar pregunta primero si es del panel; esa prueba pasa a `test_sin_el_guardar_del_panel_no_pulsa_ni_deja_lo_guardado` |
| `test_clics.universo` (la foto) | Seguía las constantes que nombran las funciones | Sigue también las que usan esas constantes para armarse. La foto no cambió |
| `test_clics.PERMITIDOS` | 2 formas del FRENO del Remark (`reservar_hyundai`: `textarea-en-js` y `textarea-o-control`) | 1 forma específica (`_JS_HMM_REMARK`, `textarea-en-js`) |
| `test_clics.TestSinClicACiegas.CORTAN` | 5 reservadores | 6: se agrega `reservar_hyundai` |
| `test_evidencia.TestEvidenciaRemarkHyundai` | Buscaba el `try` que escribía el Remark | Busca la sentencia `_hmm_remark(page, reg)`; los eventos no cambian |

- `test_candado` no cambió en ningún commit.
- La red pasó de 264 a 267 pruebas, de 543 a 559 mutaciones y de 657 a 675 pares.
- Mutaciones de CMA:
  - 7 borradas: miraban el placeholder, el JavaScript que pulsaba o el guardado por JavaScript.
  - 3 puestas al día: la del panel anidado, la del orden de la evidencia y la lista de pruebas de la evidencia.
  - 11 nuevas.
- Mutaciones de HYUNDAI: 12 nuevas.

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\correr.py --mutaciones --filtro reefer
python tests\correr.py --mutaciones --filtro hmm-
python tests\correr.py --mutaciones
```

Las sondas de la corrida son de solo lectura y viven fuera del repo. Cada una aborta si su control sintético no da lo
esperado:
- **El candado:** estados por naviera, «Me DETENGO», líneas de la rama de emisión y archivos `_confirmado`.
- **El log:** cada línea contra las plantillas de mensaje del programa; lo que no es del programa sale con su largo.
- **CMA:**
  - los paneles del selector del programa, con los ocultos por su marcado;
  - los campos del panel de afuera, con su etiqueta, y sus botones;
  - «I Agree», su casilla y su bloque;
  - el renglón Reefer y el aviso de ajustes.
- **HYUNDAI:** cada textarea con sus atributos y si está oculto, y el ancestro común del título «Remark (n / m)» y el
  textarea visible.
- **ONE y MAERSK:** la nave sale del log y nunca se imprime; se cuenta en la pantalla donde se detuvieron.
- **COSCO:** el tipo de motivo de NO ENVIADA y los candidatos, sin nave, servicio ni fecha.
- **Avisos:** los elementos de aviso de cada pantalla de parada y si están ocultos por su marcado.

## NO retroceder (pieza 2)

- **No vuelvas a buscar la temperatura de CMA por placeholder, «°C» o el texto del bloque:** caen
  `test_js_temperatura_solo_por_su_etiqueta` y sus mutaciones.
- **No vuelvas a guardar el panel por JavaScript en cualquier cajón:** pulsaba también en los ocultos.
- **No separes el detector de paneles de CMA en dos copias:** es una sola fuente, `_JS_CMA_PANELES_VISIBLES`, y la foto la
  sigue.
- **No vuelvas a escribir el Remark de HYUNDAI en el primer textarea visible:** su recuadro está medido.
- **No quites `_sin_clic_a_ciegas("hmm")`:** sin él, el corte del Remark no deja NO ENVIADA.
- **No quites el paso «I Agree» de CMA:** existe y es obligatorio.

## Premisas del encargo contrastadas (pieza 5)

- **«La carpeta de corrida más reciente»:** confirmada. Existe, es del 2026-09-25 y corrió con el código de `eb94499`.
- **«ONE y MAERSK con naves vigentes en sus itinerarios»:** refutada para las pantallas que mostró el portal. En ninguna
  de las dos aparece la nave de la fila.
- **«hmm_f<fila>_remark.*»:** confirmada: 1 captura y 2 de 2 HTML.
- **«Si «I Agree» no existe en la revisión, el paso se quita»:** existe. El paso se queda.
- **«El aviso «Faltan algunos ajustes…»»:** afinada. Está con el panel abierto y desaparece al guardarlo.
- **«COSCO: la lista guardada si quedó NO ENVIADA»:** confirmada, con el motivo «la fila no trae día de carga».

## Universo y cobertura (pieza 3)

- **La corrida:** 1 carpeta, 90 archivos y un `log.txt` de 320 líneas.
  - 315 líneas calzan con una plantilla del programa y 5 no, una tras cada login; 0 continuaciones.
  - 44 HTML: CMA 15 (el panel, lo guardado y la guarda, con sus 4 marcos), MAERSK 10, MSC 6, COSCO 5, ONE 4 y
    HYUNDAI 4.
- **Descartados:** 0 archivos sin leer en todas las sondas.
- **No medido:**
  - la revisión de MAERSK;
  - si la lista de ONE estaba cuando se buscó la nave;
  - la visibilidad real: las sondas la infieren del marcado (`display:none`, `hidden`, clases de ocultar), no de la
    página viva.

## Defectos de instrumento cazados (pieza 4)

1. **El control positivo de la sonda del panel de CMA abortó.** Esperaba 2 paneles, pero `[class*="drawer"]` calza
   también con el envoltorio y el encabezado del cajón: salen 5 candidatos. Se corrigió la expectativa, no el
   instrumento, porque es lo mismo que hace el JavaScript del programa.
2. **Una sonda imprimió en la consola una ruta real, en el texto de un botón.** No salió de la sesión. Desde ahí, las
   sondas enmascaran también las palabras en mayúsculas.
3. **Iba a importar una sonda desde otra**, lo que corre su código principal (ya registrado en el encargo 21). Se
   copiaron las funciones.
4. **Usé `sort`, que Defender bloquea**, y **la herramienta Bash cambió `\\n` por `\n` dentro de un heredoc.** Los dos
   ya estaban registrados. El guion afectado se detuvo en su aserción sin escribir nada.
5. **El generador de mutaciones de HYUNDAI abortó.** La línea del evento «input» también aparece, con más sangría, en
   otro JavaScript: como subcadena, salía 2 veces. Se ancló con la línea anterior.
6. **Al separar el detector de paneles, la foto de `test_clics` dejaba de verlo:** solo seguía las constantes que
   nombran las funciones. Se amplió en el mismo commit, con la mutación `cma-reefer-paneles-con-clic-generico` que la
   vigila.
7. **En HYUNDAI escribí primero «Hasta 1e8d510».** El último commit con el Remark viejo era `e423a38`, y se corrigió
   antes del commit.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| MAERSK marca «el último checkbox» de los términos | FRENO: la corrida no llegó a la revisión | …una corrida de MAERSK llega a la revisión y deja `mk_f<fila>_guarda.html` |
| La temperatura y «Guardar» de CMA solo como se midieron («Temperature», «Guardar») | Objetivo medido; si el portal cambia de idioma, corta con NO ENVIADA y su evidencia | …una corrida corta ahí por el idioma |
| El panel de CMA se reconoce por ser el único visible, no por `reefer-drawer` | Hallazgo nuevo: el encargo pide el panel visible | …decides usar su clase |
| La «Recogida vacía» de CMA sin completar | Sugerencia del portal, no obligatoria según su texto | …decides completarla |
| Las naves de ONE y MAERSK y el día de carga de COSCO y MAERSK | Datos de la planilla o del portal, no del código | …una corrida con esos datos completos |
| La espera de resultados de ONE (8 s) | No se midió si la lista estaba cuando se buscó la nave | …una nave que sí está no se encuentra |
| Un `style` vacío en el HTML de la evidencia (encargo 22) | Hipótesis sin medir | …alguien identifica un campo por su `style` |
| Los residuales de `CICLO-cola-nueve-items.md` que este encargo no tocó | No son parte de este encargo | …según cada fila de ese informe |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v13**:
- **PASO 0 con veredicto:** CICLO para CMA y HYUNDAI, y NOTA para COSCO y ONE. MAERSK cumplió el freno del encargo:
  la evidencia no alcanza.
- **Re-medir contra HEAD antes de diseñar:** la corrida es posterior a `eb94499`, que era el código de HEAD al empezar,
  y los cambios se diseñaron sobre ese código.
- **Control positivo que aborta:** en cada sonda. Abortaron dos y se corrigieron antes de leer sus números.
- **Todo salto silencioso lleva contador:** 0 archivos descartados; 5 líneas del log sin plantilla, contadas.
- **La unidad la fija el sujeto:** el Remark y la temperatura son un campo; se contó por campo y por nodo.
- **El negativo tiene que morder:** censo filtrado en cada commit, con el motivo de cada mutación nueva revisado.
- **Fuente única:** el detector de paneles de CMA.
- **El cambio y su guardián en la misma operación:** la foto se amplió en el mismo commit en que apareció la constante
  que no veía.
- **Cada reemplazo afirma su viejo una vez, y el EOL se preserva:** dos guiones abortaron en su aserción; CR en 0.
- **FRENAR cuando la decisión es de negocio:** los hallazgos quedan reportados, no implementados.
- **Choque, sin freno:** «un commit por naviera» y el cambio de la foto, que sirve a todas. La foto fue con CMA, que es
  la que la necesitó.

Reglas del módulo: casos sintéticos que imitan la estructura medida, la sonda de secretos antes de cada commit, nada de
`logs/` en el repo y los textos nuevos en español con tuteo.

## Entregable (pieza 8)

Este `.md`, sin renderizar, y `CLAUDE.md` al día.

**Gates:**
- **CMA (`e423a38`):**
  - la suite completa, 264 en verde y 0 cambios en los originales;
  - los censos de `reefer` (58 mutaciones y 68 pares), `TestCma` (41 y 54) y la foto (25 y 47), y muerden todos;
  - la sonda de secretos en 0 sobre el staging.
- **HYUNDAI (`72f932c`):**
  - la suite completa, 267 en verde y 0 cambios;
  - los censos de `hmm-` (23 y 30), `TestHyundai` (16 y 17), la evidencia del Remark (5 y 11), la foto (27 y 51) y
    el decorador (7 y 8), y muerden todos;
  - la sonda en 0.
- **Censo completo final sobre `72f932c`:** pasó, en 39 minutos.
  - 267 pruebas en verde, y el control (la copia sin mutar) pasa;
  - 559 mutaciones y 675 pares, y muerden todos;
  - 0 pruebas sin mutación y 0 cambios en los originales.
- **El commit de este informe** solo agrega este `.md` y cambia `CLAUDE.md`, que ninguna prueba lee.

**Para tu próxima prueba con el candado cerrado,** una corrida «todas» con una fila por naviera:
- **MAERSK:** una fila cuya nave esté en las salidas del portal, y con día de carga. Así llega a la revisión y deja
  el HTML de los términos.
- **ONE:** una fila cuya nave aparezca en los resultados de su ruta.
- **COSCO:** una fila con día de carga. Elige el itinerario cuya ETD sea ese día, o queda NO ENVIADA con la lista.
- **CMA (15) y HYUNDAI (25):** de control de lo nuevo. CMA escribe la temperatura por su etiqueta y guarda con el
  «Guardar» del panel. HYUNDAI escribe el Remark en su recuadro.
- **MSC (10):** de control.
