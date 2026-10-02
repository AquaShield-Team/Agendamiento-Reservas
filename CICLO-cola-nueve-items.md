# CICLO · La cola de nueve ítems, en un loop autónomo

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-24 · **Método:** skill `metodo-ciclo` v12 ·
**Base:** `e34b906` (último de código: `e910bf1`) · **Commits** (locales, sin push; el repo no tiene remoto): uno
por ítem, `2cabddf` a `cad1ae0`, y el de este informe.

> Sin datos reales. Lo de `logs/` se midió en su lugar y en solo lectura, con instrumentos que imprimen conteos,
> etiquetas HTML, clases y placeholders, nunca textos de reservas. Aquí no van naves, rutas, contratos ni nombres.
> `config.json` recibió dos llaves nuevas sin que ningún valor suyo pasara por la sesión.

## Los nueve ítems

| # | Ítem | Estado | Commit | Expectativas que cambiaron |
|---|---|---|---|---|
| 1 | MAERSK sin nave dice que llegó a la revisión | Hecho | `2cabddf` | `test_evidencia.test_solo_ahi` |
| 2 | CMA da la ruta por validada sin respuesta del portal | Hecho | `1ed40f4` | Ninguna |
| 3 | La temperatura de CMA mira el primer diálogo de la página | Hecho | `4884157` | 3 pruebas y 3 mutaciones de la temperatura |
| 4 | El CONTROL de COSCO dice «Size Type: VACÍO» | Hecho | `94e4102` | `test_clics.PERMITIDOS` |
| 5 | COSCO toma el primero de dos itinerarios | Hecho | `456a758` | `test_evidencia.test_solo_ahi` |
| 6 | ONE no guarda HTML si no llega a Review Booking | Hecho | `fb63271` | `test_evidencia.test_solo_ahi` |
| 7 | Teclado a ciegas y primer textarea | Hecho, con un **FRENO parcial**: el Remark de HYUNDAI | `9e5285c` | La foto de `test_clics`, `CORTAN` y 2 pruebas |
| 8 | Peso y temperatura a `config.json` | Hecho; el freno no aplicó | `42247d4` | `sinteticos.config` y 1 mutación |
| 9 | Limpieza | Hecho | `cad1ae0` | 2 pruebas; 12 pruebas y 10 mutaciones borradas |

**La red:** 246 pruebas, 468 mutaciones y 568 pares al empezar. Por ítem, la suite pasó por 248, 250, 251, 253,
256, 258, 265, 271 y 261 pruebas.

**El censo completo final, sobre `cad1ae0`, pasó:**
- la suite: 261 pruebas, OK;
- la copia sin mutar: pasa;
- 539 mutaciones y 648 pares: los 648 muerden;
- 0 pruebas sin mutación;
- 0 cambios en los originales (1779 entradas fotografiadas).

**Los frenos:**
- **Ítem 5:** no frenó. El lector que ya existe da `dia_carga`, y `_cosco_fecha_fila` lo lee con el lector de fechas
  de CMA.
- **Ítem 7:** frenó en un solo sitio. HYUNDAI escribe el Remark en el primer textarea visible:
  - las 5 reservas con confirmación de la corrida del 2026-09-21 pasaron por ahí (5 «Remark corporativo … (ok)»);
  - ningún HTML muestra esa pantalla: la guarda de HYUNDAI es en Review & Book, donde el Remark ya no es un campo.

  Queda igual, fotografiado en `test_clics` como FRENO. El resto del ítem se hizo.
- **Ítem 8:** no frenó. La temperatura vale lo mismo en las seis navieras (ver sus premisas).
- **FRENA TODO:** no se cumplió. `test_candado` no cambió en ningún commit, y la guarda de cada reservador quedó igual.

## Lo que hace ahora cada ítem

**1 · MAERSK sin nave (`2cabddf`).** Si `_mk_elegir_nave` no encuentra la nave, `_mk_sin_nave`:
- deja la captura y el HTML de esa pantalla (`mk_f<fila>_detenida`);
- escribe «Me detuve en «Select sailing»…»;
- devuelve REVISAR con ese paso.

Ya no escribe «Me DETENGO en Review booking» ni «armada hasta Review». Los demás mensajes de avance de MAERSK ya
se escribían solo si su paso ocurría.

**2 · CMA ruta (`1ed40f4`).** `_validar` devuelve lo que vio el portal. `_cma_anunciar_ruta` da la ruta por validada
solo con itinerarios o un aviso. Si `_cma_esperar_resultado` venció, o no se pudo pulsar «Validar ruta», avisa «No
pude confirmar la ruta: …», con la causa, en pantalla y en `log.txt`, y sigue sin cortar.

**3 · CMA temperatura (`4884157`).** `_JS_CMA_REEFER_TEMPERATURA`:
- cuenta solo los cajones y diálogos visibles; si hay uno dentro de otro, cuenta el de afuera;
- busca el campo solo en el único panel visible, por su etiqueta o su placeholder;
- devuelve `'ok'`, `'sin-panel'`, `'varios-paneles'` o `'sin-campo'`.

Con cualquier respuesta que no sea `'ok'` corta como objetivo no encontrado, con lo que faltó. Ya no busca por
placeholder en toda la página.

**4 · COSCO Size Type (`94e4102`).**
- `_JS_COSCO_LEER_DESPLEGABLE` lee el texto visible del único desplegable que lleva la etiqueta en su placeholder.
  Si no lo encuentra, se lee con `_JS_COSCO_ETQ_LEER`, como en «Choose Service».
- Si tampoco así, el CONTROL escribe «? Size Type: no pude leer» y «OJO: no pude leer Size Type en '<etapa>'»,
  nunca «VACÍO».
- `_JS_COSCO_ETQ_LEER` no cambió: también lo usan los pasos que llenan el formulario.

**5 · COSCO itinerarios (`456a758`).**
- Con más de uno, `_cosco_elegir_itinerario` elige el único cuya ETD es el día de carga de la fila.
- Si la fila no trae fecha, o si ninguno o más de uno tiene esa ETD, `_cosco_itinerario_ambiguo`:
  - deja la captura y el HTML de la lista (`cosco_f<fila>_itinerarios`);
  - devuelve NO ENVIADA: «COSCO: hay más de un itinerario para esa nave (…): <por qué>».
- Nunca elige el primero.

**6 · ONE (`fb63271`).** `_one_detenida` deja la captura y el HTML (`one_f<fila>_detenida`) en sus dos REVISAR: la nave
no está, o el asistente quedó en otro paso. Lo hace con el mecanismo de la guarda, sin clics ni esperas.

**7 · Teclado y textarea (`9e5285c`).** Donde elegía con flecha abajo y Enter, ahora corta como objetivo no
encontrado, con NO ENVIADA, motivo, captura y HTML:
- ONE: el autocompletado de origen, destino y commodity.
- MSC: el puerto, y el HS Code y el Kendo cuando no hay sugerencias.
- CMA: el puerto, si tras el clic y Tab no está el código; «Tamaño y tipo»; la mercancía.
- COSCO: el autocompletado por etiqueta. `reservar_cosco` lleva ahora `_sin_clic_a_ciegas("cosco")`.

Además, los comentarios de CMA se escriben solo en el campo con su placeholder o su etiqueta; si no está, corta.
`test_clics` suma tres formas a su foto: `teclado-flecha`, `textarea-en-js` y `textarea-o-control`.

**8 · Peso y temperatura (`42247d4`).**
- `config.json → opciones` trae `peso_reefer_kg: 22500` y `temperatura_reefer_c: -20`, y `config.example.json`
  también.
- `_peso_reefer` y `_temperatura_reefer` los leen. Si una llave falta o no es un número, usan el valor de siempre
  y lo avisan una vez por corrida.
- Las seis navieras usan esos lectores. Se quitaron el «22500» escrito aparte de ONE y MSC y el «-20» de respaldo
  de MSC.
- `_avisar_en_pantalla_y_log` es ahora el único canal de avisos, y el de `emitir_reservas` sale igual que antes.

**9 · Limpieza (`cad1ae0`).**
- Se borró `extraer_numero_booking`, con sus 12 pruebas.
- El simulador ya no nombra `logs/cma_dev`: usa la captura del formulario de la corrida de CMA del 2026-09-21.
  `SIMULADOR_AQUASHIELD.html` no se regeneró.
- Una corrida sin filas elegidas no abre el navegador ni entra al portal, y avisa «⚠ No hay filas elegidas…».
- `LEEME.md` describe el programa real.

## Expectativas que cambiaron (antes → ahora)

- **`test_candado`:** no cambió en ningún commit.
- **`test_evidencia.test_solo_ahi`**, quién llama a `_evidencia_antes_de_la_guarda`:
  - antes: los seis reservadores, `_sin_clic_a_ciegas` y las dos de `_cma_ajustes_reefer`;
  - ahora: además `_mk_sin_nave` (ítem 1), `_cosco_itinerario_ambiguo` (5) y `_one_detenida` (6).
- **`test_clics.TestCma.test_js_temperatura_solo_por_su_etiqueta`** (3):
  - antes: `true` o `false` sobre el contenedor que devolvía `querySelector`;
  - ahora: `'ok'` o `'sin-campo'` sobre paneles con su visibilidad, más un caso por placeholder.
- **`test_clics.TestCma.test_reefer_corta_en_cada_paso_sin_pulsar_a_ciegas`** (3):
  - antes: el JavaScript devolvía `false` y la página no tenía campos;
  - ahora: cada respuesta que no es `'ok'` corta con su motivo, aunque la página tenga campos con esa etiqueta, y el
    guardado se prueba con `'ok'`.
- **`test_evidencia.PanelReefer`** (3): el JavaScript de la temperatura responde `'ok'` (antes, `True`).
- **Las mutaciones `cma-reefer-temperatura-el-primer-campo`, `-el-primer-input` y `-no-corta`** (3): apuntan al código
  nuevo.
- **`test_clics.PERMITIDOS`:**
  - ítem 4: suma `_JS_COSCO_LEER_DESPLEGABLE` «clase-de-componente», NO ES CLIC (lee por su placeholder);
  - ítem 7: `_cma_comentarios` pasa de «primero-sin-filtro» y «textarea-cualquiera» (residual) a «textarea-en-js»
    (ESPECÍFICO), y suma el Remark de HYUNDAI (FRENO, 2 formas).
- **`test_clics.GENERICOS`** (7): suma `teclado-flecha`, `textarea-en-js` y `textarea-o-control`.
- **`test_clics.TestSinClicACiegas.CORTAN`** (7): suma `reservar_cosco`.
- **`test_clics.TestMsc.test_hs_sin_salmon_corta`** (7): sin sugerencias, antes seguía con el teclado; ahora corta.
- **`test_clics.TestCma.test_tamano_y_tipo_no_abre_el_primer_desplegable`** (7): antes miraba solo el paso; ahora
  exige también lo que buscaba. El corte nuevo de la opción tiene el mismo paso y tapaba a `cma-tamano-no-corta`.
- **`sinteticos.config`** (8): antes sin las dos llaves; ahora con 22500 y -20, como la configuración real.
- **La mutación `reefer-ignora-la-constante`** (8): de `.strip() or TEMP_REEFER` a `.strip() or _temperatura_reefer()`.
- **`test_web`** (9): `test_corrida_sin_filas_igual_entra_al_portal` pasa a `test_corrida_sin_filas_no_abre_el_navegador`.
  - Antes: 1 navegador y 1 login.
  - Ahora: 0 y 0, con el aviso, en ONE y en CONSOLIDADO.
- **`test_evidencia.test_son_las_que_nombran_los_generadores`** (9): antes `["cma_dev"]` fuera de las corridas; ahora
  `[]`. Lee el generador de la copia de las fuentes si la trae.
- **`test_booking.TestExtraerNumero`** (9): borrada, con sus 12 pruebas.
- **Las mutaciones del lector viejo** (9):
  - 10 borradas;
  - 6 pierden su prueba de `TestExtraerNumero` y conservan la de `numero_tras_envio`;
  - `extractor-hyundai-vuelve-a-la-cadena` y `extractor-maersk-vuelve-a-la-cadena` pasan a `hyundai-sin-forma-medida`
    y `maersk-sin-forma-medida`, sobre `numero_tras_envio`.
- **La mutación `worker-sin-filas-no-entra`** (9): pasa a `worker-sin-filas-entra-igual` y `worker-sin-filas-no-avisa`.

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\correr.py --mutaciones
python tests\correr.py --mutaciones --filtro cosco-itinerario
```

Cada ítem se commiteó con su puerta: la suite completa, el censo filtrado a sus mutaciones nuevas o modificadas y
la sonda de secretos en 0 sobre el staging. Las sondas de la medición son de solo lectura y viven fuera del repo:
- **Ítem 3:** en `cma_f15_reefer_panel.html` de la corrida del 24, 9 contenedores calzan con el selector del
  JavaScript, y 0 en sus 4 marcos. Con el panel cerrado, los 9 están ocultos:
  - 2 por su clase `u-hidden`;
  - 1 dentro del centro de preferencias de cookies, con `ot-hide`;
  - el resto por un `display:none` propio o de su contenedor.

  Control positivo: el diálogo `u-hidden` medido en el encargo 20.
- **Ítem 4:** el CONTROL de Size Type, por etapa, en los 7 logs (5 con COSCO): «Choose Service» ✓ en 16 de 16,
  «Booking Details» ✗ VACÍO en 15 de 15. En el HTML de la guarda de COSCO:
  - la etiqueta es un `<p>` de la fila de encabezados;
  - el desplegable, un `input` de solo lectura con placeholder «Please select Size Type» en otra fila;
  - subiendo tres niveles desde la etiqueta, como hace `_campo`, hay 0 controles.
- **Ítem 7:** en los 7 logs, 0 marcas de los respaldos de teclado:
  - ONE: «sin sugerencia -> teclado»;
  - MSC: «': teclado» y «confirmado con teclado»;
  - COSCO: «(teclado)»;
  - CMA: «vía teclado ArrowDown» y «seleccionada con Enter».

  En COSCO, las 25 sugerencias quedaron con el primer clic: 0 con eventos de puntero y 0 con el perfil. HYUNDAI:
  5 «Remark corporativo … (ok)» con 5 confirmaciones en la corrida del 21. En el HTML de su guarda, 8 textareas de
  commodity y el Remark como texto de solo lectura. Control positivo: cada marca contra su línea sintética.
- **Ítem 8:** las seis navieras toman la temperatura de `_temp_reserva`. Antes de escribir, `config.json` hizo ida
  y vuelta idéntica con sangría 2 y CRLF. Después, lo demás quedó igual, comparado como datos, sin imprimir valores.

## NO retroceder (pieza 2)

- **No vuelvas a elegir con el teclado antes de la guarda:** la forma `teclado-flecha` tumba la foto de
  `test_clics`.
- **No vuelvas a tomar el primero de varios itinerarios de COSCO:** la ETD tiene que ser el día de carga, o NO
  ENVIADA.
- **No busques la temperatura de CMA fuera del panel visible:** el primer contenedor de la página era uno oculto.
- **No escribas el peso ni la temperatura de siempre en otro lugar:** viven en `config.json`, con un solo lector y
  sus constantes como valor por defecto.
- **No dupliques el canal de avisos:** `_avisar_en_pantalla_y_log` sirve a los dos.
- **Una prueba que lee un archivo del programa lo lee de `soporte.FUENTES`:** si no, su mutación no muerde.

## Premisas del encargo contrastadas (pieza 5)

- **Ítem 1, «dice que llegó a la revisión»:** confirmada.
- **Ítem 2, «el vencimiento no se detecta»:** confirmada. `_validar` devolvía «ok» siempre.
- **Ítem 3, «el primer diálogo de la página era uno oculto»:** confirmada. Además, con el panel cerrado no hay
  ningún contenedor visible: el panel abierto debería ser el único.
- **Ítem 4, «el control no sabe leer ese select»:** afinada. No es que lo lea mal: en Booking Details nunca lo
  encuentra, y en «Choose Service» lo lee bien.
- **Ítem 5, «el lector que ya existe»:** confirmada. `leer_filas` da `dia_carga`, y es la fecha de zarpe que usan
  CMA, MSC, HYUNDAI y MAERSK.
- **Ítem 7, «si la evidencia muestra que una reserva exitosa pasó por esa selección»:**
  - para el teclado, no pasó ninguna: 0 marcas;
  - para el primer textarea, sí: el Remark de HYUNDAI. De ahí el freno.
  - Los comentarios de CMA escribieron por JavaScript en las 5 reservas del 21, pero el log no dice si fue por el
    placeholder o por el primer textarea, y CMA no tiene confirmación medida. Se aplicó la regla.
- **Ítem 8, «el peso ya está medido en 22500 en las seis»:** confirmada. Cuatro por `PESO_REEFER`, y ONE y MSC con
  la cifra escrita aparte. La temperatura también vale lo mismo en las seis.
- **Ítem 9, «ningún reservador usa extraer_numero_booking»:** confirmada. Sus 12 pruebas y 10 mutaciones solo lo
  vigilaban a él.

## Universo y cobertura (pieza 3)

- **`logs/`:** 7 carpetas con `log.txt` (0 sin él). HTML de una sola corrida, la del 24:
  - el panel Reefer de CMA (5 archivos);
  - la guarda de COSCO (5);
  - la guarda de HYUNDAI (2).
- **Código:** al empezar, 12 sitios de teclado o textarea en lo que corre antes de la guarda de los seis
  reservadores, con sus ayudantes. Al cerrar, la foto de `test_clics` cuenta:
  - 0 formas de teclado;
  - 3 de textarea: las 2 del Remark de HYUNDAI (FRENO) y la de los comentarios de CMA, que ahora busca por
    placeholder o etiqueta (ESPECÍFICO).

  El instrumento de la medición ya no sirve para recontar: su control positivo era el ArrowDown de CMA, que se
  quitó, y aborta.
- **No medido:**
  - el panel Reefer de CMA abierto;
  - la lista de itinerarios de COSCO: hasta ahora no quedaba en la evidencia;
  - la pantalla Additional Info de HYUNDAI.

## Defectos de instrumento cazados (pieza 4)

1. **`Path.write_text` escribió CRLF en un archivo del repo.** Git lo normalizó al commitear. Desde entonces, los
   archivos del repo se escriben con `write_bytes`.
2. **La herramienta Bash cambia `\\n` por `\n` también dentro de un heredoc.** Pasó dos veces: un texto de prueba
   quedó sin cerrar y un reemplazo no calzó. Los scripts con barras invertidas van por Write.
3. **El lector de Size Type abortó dos veces en su control positivo:**
   - la etiqueta tiene su asterisco en otro elemento;
   - importar la primera sonda desde la segunda corrió su código principal.
4. **La marca «Remark» contaba también el campo Remark del CONTROL de COSCO.** Se midió aparte, por «Remark
   corporativo».
5. **Una prueba leía `config.example.json` de la raíz real y no de la copia mutada.** Su mutación no mordió en la
   puerta del ítem 8: ahora lee de `soporte.FUENTES`.
6. **Una mutación vieja quedó tapada por un corte nuevo con el mismo paso:** `cma-tamano-no-corta`. El censo de la
   puerta del ítem 7 la cazó. Es la lectura (e) del negativo vacuo, y se corrigió haciendo que la prueba exija lo que
   buscaba.
7. **Copié la lógica de `_avisar_llave_config` para el aviso nuevo:** tres mutaciones viejas quedaron con su texto
   dos veces. Se juntó en una sola fuente, `_avisar_en_pantalla_y_log`.
8. **Editar un generador de mutaciones por reemplazo de texto falló por los escapes.** Se reescribió entero.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| HYUNDAI escribe el Remark en el primer textarea visible | FRENO: fue camino de reservas confirmadas y ningún HTML muestra ese campo | …decides dejar evidencia en Additional Info, o una corrida la trae |
| Los genéricos de MAERSK (términos y condiciones) | FRENO anterior (`CICLO-clics-a-ciegas.md`) | …el HTML de la revisión de MAERSK |
| El panel Reefer de CMA se reconoce por ser el único visible, no por su título | Su HTML abierto no se ha medido | …`cma_f<fila>_reefer_panel.html` con el panel abierto |
| COSCO elige solo con la ETD igual al día de carga, sin tolerancia | Una tolerancia es decisión de negocio | …decides una |
| CMA corta en la primera falla del puerto de destino y no prueba el segundo modo | Antes, el teclado elegía otra cosa | …una corrida corta ahí y el segundo modo habría servido |
| COSCO corta al primer clic que no queda, sin reintentar | 25 de 25 quedaron con el primer clic | …una corrida corta ahí |
| El REVISAR «el puerto de carga no quedo seleccionado» de CMA ya no se alcanza | `_cma_puerto` ahora corta antes | …se toca la ruta de CMA |
| El CONTROL de COSCO dice VACÍO en otros campos que no encuentra | El ítem 4 era Size Type (Gross Weight: 8 «VACÍO» en corridas viejas) | …un VACÍO que la captura desmiente |
| `_JS_CMA_REEFER_GUARDAR` busca el botón en cualquier cajón, también en los ocultos | Fuera del ítem 3 | …se toca el guardado del panel |
| `SIMULADOR_AQUASHIELD.html` sin regenerar | El encargo pedía corregir la referencia | …se regenera el simulador |
| `test_web.TestPanelCredenciales.test_guardar_credenciales` falló una vez | 1 de 12 suites completas: la segunda respuesta de `/api/credenciales` no fue JSON; aislada, 3 de 3 bien. Hipótesis sin medir: una carrera entre la escritura atómica y una lectura de `config.json` | …vuelve a fallar |
| El 502 de MSC y el contrato de HYUNDAI en el paso 3 | El encargo dice que no se tocan | …decides tocarlos |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v12**:
- **PASO 0 con veredicto:** CICLO en los nueve. Cada freno por ítem se midió antes de tocar el código: el 5 y el 8
  no frenaron; el 7 frenó en un sitio.
- **Control positivo que aborta:** en cada sonda. Abortaron dos y se corrigieron antes de leer sus números.
- **El negativo tiene que morder:** censo filtrado en cada commit, con el motivo de cada mutación revisado.
- **Un negativo vacuo delata un caso incompleto:** `cma-tamano-no-corta`, lectura (e), enmascarado por el corte
  nuevo.
- **Fuente única:** el peso, la temperatura y el canal de avisos.
- **Cada reemplazo afirma su viejo una vez, con escritura atómica:** `config.json` y los generadores de mutaciones.
- **El EOL se preserva y se verifica:** CR en 0 en cada commit, y `config.json` con su CRLF.
- **El cambio y su guardián en la misma operación, y se declaran el residual y las premisas.**
- **Choque, sin freno:** la fuente única del canal de avisos tocó `_avisar_llave_config`, que está junto al candado.
  Su comportamiento no cambió y `test_candado` tampoco. No se cumplió el FRENA TODO.

Reglas del módulo: casos sintéticos, sonda de secretos antes de cada commit, nada de `logs/` en el repo, y textos
nuevos en español con tuteo.

## Entregable (pieza 8)

Este `.md`, sin renderizar, y `CLAUDE.md` al día.

**Para tu próxima prueba con el candado cerrado,** una corrida «todas» con una fila por naviera, como la del 24:
- **ONE (fila 5):** si la nave sigue sin aparecer, deja `one_f5_detenida.*` con la pantalla de itinerarios.
- **CMA (fila 15):** el panel Reefer debería abrirse (`d938cd1`). La temperatura se busca solo en él, y
  `cma_f15_reefer_panel.*` lo muestra abierto. Si corta, el motivo dice si faltó el panel, sobró uno o faltó el
  campo.
- **COSCO (fila 20):** tuvo dos itinerarios. Ahora elige por el día de carga o queda NO ENVIADA con
  `cosco_f20_itinerarios.*`, que por primera vez muestra la lista. El CONTROL dirá ✓ o «no pude leer» en Size Type.
- **MAERSK:** cambia la fila 30 por una cuya nave esté en los itinerarios. Si no, se detiene en «Select sailing» con
  `mk_f30_detenida.*`.
- **MSC (fila 10) y HYUNDAI (fila 25):** de control. MSC ya no tiene respaldos de teclado. HYUNDAI sigue igual.
