# CICLO · Solo la nave que la fila pide

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-26 · **Método:** skill `metodo-ciclo` v13 ·
**Base:** `a198645` (último de código: `be6a86f`) · **Commits** (locales; el repo no tiene remoto): uno por ítem,
`dd0cfff` (ítem 1), `44a7331` (ítem 2) y `714cbaa` (ítem 3), y el de este informe.

> Sin datos reales. `logs/`, las planillas y `config.json` se midieron en solo lectura. Las sondas imprimen conteos,
> etiquetas de interfaz, formas enmascaradas y nombres de archivo del programa. Las capturas se leyeron con OCR sin
> mirarlas, y la sonda imprime solo cuántas palabras de la nave encontró. Nunca salen naves, puertos, contratos ni el
> nombre del operador.

La regla de los tres ítems, decidida por Marcelo: **el programa nunca reserva una nave que la fila no pidió.**

## Los tres ítems

| # | Ítem | Resultado | Commit | Freno |
|---|---|---|---|---|
| 1 | Una sola lista de comodines para las seis. La fila vacía o con un comodín queda NO ENVIADA, sin abrir el portal | Hecho | `dd0cfff` | El ítem no traía freno propio |
| 2 | Se elimina `AQUASHIELD_PRIMERA_NAVE` y cualquier otro atajo que reserve sin calzar la nave | Hecho: 5 atajos eliminados en 5 navieras. Otros casos que todavía pueden dejar pasar otra nave quedan en el residual | `44a7331` | El ítem no traía freno propio |
| 3 | HYUNDAI deja de aceptar el modal «Alternate Vessel Option» | Hecho | `714cbaa` | **No se activó.** El freno era parar si el modal aparecía también con la nave pedida en la lista. En las 8 reservas con el modal, la nave pedida no estaba en la lista |

Cada ítem pasó por una revisión que buscó fallas a propósito antes de su commit: tres revisores con enfoques distintos
en los ítems 1 y 2, y dos en el 3. Encontraron huecos reales en los tres; están en cada ítem y en la pieza 4.

**Convención de este informe y de los comentarios del código:** «hasta `a198645`» quiere decir «antes del encargo 28».
Lo que cambió el ítem 2 todavía estaba igual en `dd0cfff`, y lo que cambió el ítem 3, en `44a7331`; aun así, se dice
«hasta `a198645`» también en esos casos.

## Ítem 1 · La fila sin nave

**Lo que reconocía cada lugar hasta `a198645`**, medido en el código:

| Dónde | Qué reconocía como fila sin nave | Qué hacía |
|---|---|---|
| CMA (`_cma_seleccionar_itinerario`) | La celda vacía, y la celda entera AUTO, CUALQUIERA, LIBRE, N/A, NINGUNA, NONE o «-» | Cortaba al elegir el itinerario (NO ENVIADA), después de abrir el portal, validar la ruta y llenar la carga |
| HYUNDAI (`reservar_hyundai`) | La celda vacía o con «completar» | OMITIDO, sin ir al portal, pero con el navegador abierto y la sesión iniciada |
| HYUNDAI (`_JS_HMM_INDICE_NAVE`) | Quitaba de la nave AUTO, PRIMERA, DISPONIBLE, CUALQUIERA, NW2, VIAJE, V., VOY y las palabras de una letra | Con una nave hecha solo de esas: REVISAR «no encontrada», con el portal abierto |
| ONE y COSCO | La celda vacía | OMITIDO, sin ir al portal, con el navegador abierto |
| MSC y MAERSK | Nada | Entraban al portal y no calzaba ninguna tarjeta |
| El panel web, en su JavaScript (`JS_INDEX`) | La celda vacía, y la que dice MANUAL | Las dejaba sin marcar («esas se omiten»): no llegaban al servidor ni a la planilla |
| El lector del panel (`leer_filas`) | «completar» | La convierte en celda vacía (este encargo no cambió el lector) |

**Las planillas reales:** con la regla nueva, **0 de 150 filas** quedan sin nave (`regla_en_planillas.py`). Son las 60
filas de cada libro con el lector del panel (la raíz y la copia del panel: 30 en CONSOLIDADO y 5 en cada hoja de
naviera) y las 30 de las seis hojas de naviera de la raíz con el lector de la consola, que no lee CONSOLIDADO. La regla
nueva no cambia ninguna fila real medida.

**Lo hecho:**
- **Una sola lista,** `NAVES_COMODIN`: AUTO, CUALQUIERA, LIBRE, NINGUNA, NONE, PRIMERA y DISPONIBLE. Junta los
  comodines de CMA y los de HYUNDAI.
  - N/A y «-» no hacen falta, porque no traen palabras (abajo).
  - NW2, VIAJE, V. y VOY no son comodines: el ítem 2 hace que HYUNDAI deje de quitarlos.
- **Una sola regla,** `_fila_sin_nave`. La fila no pide nave si su texto trae «completar» en cualquier parte, o si no
  trae ninguna palabra de 2 o más letras o dígitos que no sea un comodín.
  - Las palabras se separan por cualquier signo, y las de una letra no cuentan, porque ninguna naviera las busca.
  - Así, «N/A», «-», «(AUTO)», «PRIMERA/DISPONIBLE» y «AUTO X» no piden nave.
- **Antes de abrir el navegador:**
  - El panel web y la consola apartan esas filas, y cada una queda NO ENVIADA con el motivo «la fila no trae una nave
    para reservar». El motivo sale en pantalla y en `log.txt`, con «escribe la nave en la planilla y vuelve a armar la
    reserva», y en la planilla.
  - Si ninguna fila de la naviera trae nave, no se abre el navegador ni se entra al portal.
  - En la consola, cada fila conserva su número de solicitud y el resumen va en el orden de la hoja. Con
    `AQUASHIELD_SOLO_PRIMERA` se toca una sola fila, igual que antes.
  - En la consola, ONE y MSC toman la nave de la columna F cuando la celda viene vacía, así que esa fila no se aparta:
    está en el residual.
- **En los seis reservadores,** `_con_la_nave_de_la_fila`: si una fila sin nave llega por otro camino, queda NO ENVIADA
  sin tocar la página. Se borraron los OMITIDO de ONE, COSCO y HYUNDAI. CMA decide con la regla compartida, y el
  JavaScript de HYUNDAI ya no quita sus comodines.
- **El panel web:**
  - `/api/filas` dice, fila por fila, si trae nave (`sin_nave`), con la misma regla.
  - La tabla marca por defecto también las filas sin nave, para que queden NO ENVIADA en la planilla. Solo las que dicen
    MANUAL quedan sin marcar.
  - El aviso dice «N reserva(s) no traen una nave para reservar: quedan NO ENVIADA, sin entrar al portal. Escribe la
    nave en la planilla si quieres reservarlas.»
  - Hasta `a198645`, la fila vacía quedaba sin marcar y nunca llegaba a la planilla. Lo encontró la revisión: las
    pruebas llamaban a `/api/correr` directo y no pasaban por el panel.

## Ítem 2 · Los atajos

El barrido leyó entero el código de cada naviera y de los orquestadores, con un agente por naviera, y la revisión buscó
lo que faltaba.

**Eliminados:**

| Naviera | El atajo | Cuánto se usó, medido | Ahora |
|---|---|---|---|
| MAERSK | `AQUASHIELD_PRIMERA_NAVE`: sin nave que calzara, la primera salida que se podía reservar | Ningún archivo del repo la fija; si alguna corrida la tuvo puesta, no queda registro | La variable no existe; sin calce, «no se encontró» |
| HYUNDAI | Su lista `ignore` quitaba palabras de la nave antes de calzar: con «HMM NW2» quedaba solo el prefijo, que traen todas sus naves | 0 filas reales con esas palabras | Se exigen todas las palabras. Los comodines salieron en el ítem 1, y NW2, VIAJE, V. y VOY, en este |
| ONE | «Vessel Information» («click Next to select a new vessel»): lo cerraba con su primer botón, «Next» incluido, y seguía | `_cerrar_modal_one` no dejó ninguna línea de cierre en los 9 `log.txt`, 4 de ellos con reservas de ONE. El cierre que se hacía justo antes de pulsar la tarjeta no deja línea: ese uso no se puede medir | Si lo detecta, no pulsa nada en él: antes de la guarda, la reserva queda NO ENVIADA con evidencia (`one_f<fila>_sin_objetivo`). Justo antes de pulsar la tarjeta, si hay un diálogo abierto, lo cierra solo con «Cancel», «Cancelar», «Close» o «Cerrar», nunca con «Next» |
| MSC | Sin «Vessel / Voyage», comparaba con los primeros 40 caracteres de la tarjeta | 0 de 79 tarjetas guardadas sin su campo | Sin campo, sin nave: no calza |
| COSCO | Sin su fila a 8 niveles, o si la primera con «Service» y «Vessel» traía otro «Book now», leía ese contenedor y se quedaba con la nave de otro itinerario | 0 de 8 «Book now» guardados: los 8 tienen su fila, con uno solo | Sin su fila, sin nave: no calza |

**Encontrados y no eliminados.** No son atajos que se salten el calce: son límites del propio calce, o caminos que tocan
algo que el encargo prohíbe tocar. Mientras sigan, en esos casos el programa todavía puede reservar otra nave u otra
salida. Están en el residual para que decidas:
- las filas con solo el prefijo de la naviera;
- el calce por parte del texto y las palabras de una letra;
- el clic por posición, sin volver a leer la tarjeta;
- el diálogo genérico de ONE, que acepta OK;
- la ruta preseleccionada de CMA;
- el calce con toda la tarjeta en CMA y HYUNDAI;
- el lector de la consola, que toma la nave de la columna F;
- el viaje, que en COSCO y MAERSK cae a otro de la misma nave;
- el origen de COSCO, que cae a un puerto fijo del código.

## Ítem 3 · HYUNDAI y «Alternate Vessel Option»

**Lo medido, en solo lectura:**
- **Universo:** las 9 carpetas de `logs/`, todas con `log.txt`; 0 descartadas.
- **El modal:** `log.txt` registra 8 veces que el programa pulsó el OK del modal (`#vesselOptionSubmit`), una por cada
  reserva de HYUNDAI que llegó a elegir nave.
  - Son 5 de la corrida del 21 de septiembre (filas 25 a 29) y 3 de otras tres corridas, una del 24 y dos del 25, las
    tres con la fila 25.
  - Ninguna reserva de HYUNDAI llegó a elegir nave sin el modal.
- **¿La nave pedida estaba en la lista?** Se leyó con OCR (Tesseract, sin mirar la imagen) la captura de la lista,
  `hmm_f<fila>_2_naves.png`, de las 8. La nave pedida tiene 2 palabras: el prefijo de la naviera y el nombre.
  - En las 8, la lista trae el prefijo y **no trae el nombre**, ni una palabra que se diferencie de él en 1 o 2 letras.
  - Control por fila: en cada una de las 8, la captura trae 7 de las 9 palabras de la tarjeta pulsada que no son de la
    nave pedida. Esa tarjeta tenía que estar en la lista, así que el OCR sí la leía.
  - Control global: una imagen sintética «HMM NAVE UNO» se lee entera.
  - **Premisa:** la nave pedida sale de la copia actual de la planilla del panel, por su número de fila, porque HYUNDAI
    no deja en `log.txt` la nave que busca. Que esas filas no cambiaron entre el 21 y hoy es una premisa, no una
    medición.
- **Qué nave quedó:** la captura de la revisión (8 de 8) y el HTML de la guarda (3 de 3) traen el prefijo de la nave
  pedida y no su nombre, y sí palabras de la tarjeta elegida. La reserva quedaba armada con otra nave.
- **El HTML guardado** (10 archivos de HYUNDAI, de la guarda y del Remark) no trae el modal: se cierra antes. Qué dice
  el modal no se pudo medir.

**El freno no se activó, pero solo porque no hubo casos:** ninguna de las 8 reservas con el modal tenía la nave pedida
en la lista. Las 8 eligieron otra nave porque calzaban solo por la primera palabra, el prefijo de la naviera, algo que
el programa aceptó hasta `9051f43`. Con las reglas de hoy, esas 8 habrían quedado en REVISAR, «nave no encontrada»,
antes del modal. Si el modal sale también con la nave pedida, se sabrá en la próxima prueba de HYUNDAI.

**Lo hecho:**
- `_hmm_ofrece_otra_nave` reemplaza a `_hmm_modal_ok`. Mira el botón del modal como antes, en los mismos dos lugares y
  en el mismo momento:
  - tras la espera de 1,5 s que sigue al paso que elige la nave («Book Now», o la tarjeta y «NEXT - Booking Details»);
  - y otra vez si Booking Details no aparece en 12 s.
- Si el modal está a la vista, no pulsa nada en él. Deja la captura de la ventana y el HTML (`hmm_f<fila>_otra_nave`,
  con `_evidencia_antes_de_la_guarda`), y la reserva queda NO ENVIADA. Si guardar la evidencia falla, lo avisa y la
  reserva queda NO ENVIADA igual.
- El aviso en pantalla dice solo lo medido: «HYUNDAI mostró el modal “Alternate Vessel Option”. No pulso nada en él».
- El motivo que queda en la planilla, «HYUNDAI ofreció otra nave en lugar de la pedida», es el que decidiste, aunque
  dice más de lo medido: todavía no se sabe si el modal sale también con la nave pedida.

## Expectativas que cambiaron (antes → ahora)

| Prueba | Antes | Ahora |
|---|---|---|
| `test_clics.TestSinClicACiegas.test_cada_reservador_que_corta_esta_decorado` | `[_sin_clic_a_ciegas(p)]` | `[_con_la_nave_de_la_fila, _sin_clic_a_ciegas(p)]` |
| `test_web.TestPanelCorridas.test_corrida_de_una_hoja` | Las filas 5 y 7 (la 7 volvía EMITIDA del reservador) | La 5 y la 6: la 7 no trae nave |
| `test_web.TestPanelCorridas.test_corrida_con_estados_tras_el_envio` | 5 NO ENVIADA, 6 ENVIADA – REVISAR y 7 EMITIDA, del reservador | 5 EMITIDA y 6 ENVIADA – REVISAR, del reservador; 7 NO ENVIADA «la fila no trae una nave para reservar», del panel |
| `test_web.TestPanelCorridas.test_login_fallido_no_reserva` | Sin resultados | La 6, sin nave, NO ENVIADA antes del login |
| `test_web.TestPanelCorridas.test_corrida_sin_filas_no_abre_el_navegador` | — | Además, exige que no salga el aviso de las filas sin nave |
| `test_consola`: `test_sin_emitir_solo_si_volvio_sin_emitir` y `test_estados_tras_el_envio_en_la_planilla` | La fila 10 traía «NAVE POR COMPLETAR» y llegaba al reservador | Lo que se espera no cambia; cambia el dato: la prueba le da una nave a la fila 10, porque con la regla nueva «completar» la deja sin nave |
| `test_clics.TestHyundai.test_js_nave_con_todas_sus_palabras` | «PRIMERA DISPONIBLE»: sin_nave; «HMM NW2», «HMM VOY», «HMM VIAJE» y «HMM V.»: la primera tarjeta | no_encontrada en todas |
| `test_clics.TestMaersk.test_elige_la_proxima_salida_que_se_puede_reservar` | Con `AQUASHIELD_PRIMERA_NAVE`: `[("book", 1)]` | Ninguna, y «no se encontró» |
| `test_clics.TestOne.test_js_clic_solo_el_boton_de_la_tarjeta_elegida` | Con un diálogo abierto que traía «Next» o «Siguiente»: pulsaba ese botón y el de la tarjeta | Solo el botón de la tarjeta |
| `test_clics.TestMsc.test_js_naves_lee_la_etd_y_la_eta` | Tarjeta sin su campo: los 40 caracteres | Nave vacía |
| `test_clics.TestCosco.test_js_lista_lee_la_salida_y_la_llegada_de_la_tarjeta` | Botón sin su fila: la nave del otro itinerario | Ninguna |
| `test_evidencia.TestCadaReservadorLaDeja.test_solo_ahi` | Sin `_hmm_ofrece_otra_nave` (pulsaba el OK sin dejar evidencia) | Con ella |

**Pruebas nuevas (17):**
- en `test_ayudantes`, `TestFilaSinNave` (4);
- en `test_web`, `test_fila_sin_nave_no_abre_el_portal`, `test_fila_sin_nave_en_consolidado` y
  `test_filas_dicen_si_traen_nave`;
- en `test_consola`, `test_fila_sin_nave_no_abre_el_portal` y
  `test_fila_sin_nave_con_login_fallido_o_solo_la_primera`;
- en `test_envio`, `test_marca_por_defecto_tambien_las_filas_sin_nave`;
- en `test_clics`, `test_js_vessel_information_nunca_next` y `test_vessel_information_corta_antes_de_la_guarda`;
- en `test_evidencia`, `TestOtraNaveHyundai` (5).

**`test_candado` no cambió:** su archivo no cambió en ninguno de los tres commits, y pasó en cada gate.

**Mutaciones:**
- **Entran 71:** 46 en el ítem 1, 11 en el 2 y 14 en el 3.
- **Sale una:** `mk-prueba-no-elige`, porque su texto ya no existe. La reemplaza `mk-vuelve-la-primera-nave`, que repone
  el atajo en su lugar de siempre.
- **Se reanclaron ocho de la base:**
  - seis de la consola (tres `consola-*` y tres `respaldo-*`), porque la escritura por fila se movió a `anotar`;
  - `one-sin-aviso-de-fecha` y `one-clic-sin-dialogo`.
- Además, `hmm-vuelve-sus-comodines`, nueva del ítem 1, se reancló en el ítem 2.

## Veredicto por naviera: ¿lista para una emisión real de prueba?

| Naviera | Veredicto | Qué le falta |
|---|---|---|
| **MSC** | **Casi lista** | Una corrida con candado cerrado, ahora que busca desde hoy, para ver en vivo la próxima salida y que la nave calce con su campo «Vessel / Voyage». Tiene forma medida de confirmación: puede llegar a EMITIDA |
| **ONE** | **Casi lista** | Una fila cuya nave esté en la búsqueda, escrita como en el enlace de su tarjeta, que llegue a Review Booking. Si ONE muestra «Vessel Information», ahora corta. Tiene forma medida |
| **COSCO** | **No para emitir:** nunca llega a EMITIDA | Le falta la forma medida de su confirmación: tras el envío quedaría en ENVIADA – REVISAR EN PORTAL. Para la prueba con candado cerrado sí está casi lista: el desempate por el tránsito ya resuelve sus 2 empates medidos |
| **HYUNDAI** | No | **Si el modal sale siempre, ninguna reserva de HYUNDAI pasa: todas quedan NO ENVIADA.** Hace falta una prueba con la nave pedida en su lista para saberlo. Le falta además el HTML de su lista (`hmm_f<fila>_naves`) para calzar con el campo de la nave y aplicar la próxima salida |
| **CMA** | No | «Validar ruta» sigue sin respuesta, falta su lista (`cma_f<fila>_rutas`) y no tiene forma medida: nunca llega a EMITIDA |
| **MAERSK** | No | Como ya no existe el atajo `AQUASHIELD_PRIMERA_NAVE`, necesita una fila cuya nave tenga una salida con «Book» para llegar a la revisión y medir la casilla de términos (FRENO) |

## Qué fila elegir en cada naviera para la próxima prueba con candado cerrado

- Una fila por naviera en CONSOLIDADO, con el lanzador normal, nunca el de emisión.
- Elige cada nave en el portal el mismo día de la corrida, en la ruta de la fila, y escríbela **con todas las palabras
  con que el portal la muestra**:
  - nunca vacía, con «completar» ni con un comodín: quedaría NO ENVIADA sin entrar al portal;
  - nunca solo con el prefijo de la naviera («MSC», «HMM»): calzaría con cualquier nave suya (residual).
- **Suma una fila de control sin nave,** con la celda de la nave vacía, en cualquier naviera. En el panel tiene que
  aparecer marcada por defecto. Al correr, tiene que quedar NO ENVIADA con «la fila no trae una nave para reservar», sin
  que el programa entre al portal por ella; el portal se abre igual por la otra fila de esa naviera.

| Naviera | Qué fila elegir | Qué evidencia va a dejar |
|---|---|---|
| **HYUNDAI (la más importante)** | Una nave que **sí esté** en su lista para esa ruta y ese día, con el prefijo y el nombre como la muestra el portal | `hmm_f<fila>_naves` (la lista). Si sale el modal: `hmm_f<fila>_otra_nave`, y la fila queda NO ENVIADA; así se sabrá si el modal sale también con la nave pedida. Si no sale: `hmm_f<fila>_remark` y `hmm_f<fila>_guarda` |
| ONE | La nave como la trae el enlace de su tarjeta, con una salida que no sea de hoy ni de mañana, para que el cierre de recepción (cut-off) esté vigente | `one_f<fila>_guarda` (Review Booking); `one_f<fila>_detenida` con la lista si no queda una sola salida; `one_f<fila>_sin_objetivo` si ONE muestra «Vessel Information» |
| MSC | Cualquier nave de su lista para esa ruta, con su prefijo («MSC …») | `msc_f<fila>_guarda` (Summary) |
| COSCO | Una nave con su itinerario; si hay dos el mismo día, el tránsito elige | `cosco_f<fila>_guarda`, o `cosco_f<fila>_itinerarios` si empatan |
| MAERSK | Una nave con una salida que traiga «Book» (el plazo «Gate-in deadline» vigente) | `mk_f<fila>_guarda`: la revisión, con la casilla de términos por identificar |
| CMA | Cualquier nave con ruta ese día | `cma_f<fila>_rutas`, `cma_f<fila>_validar_<modo>`, los del panel Reefer y `cma_f<fila>_guarda` |

**Después de la corrida, lo primero:** revisa que ninguna fila haya quedado en EMITIDA ni en ENVIADA – REVISAR EN
PORTAL, y que no haya capturas `*_confirmado`. Después, revisa `hmm_f*_otra_nave` (con la línea «nave elegida» del
mismo `log.txt`), `hmm_f*_naves`, `cma_f*_rutas`, `cma_f*_validar_*` y la revisión de MAERSK, si la reserva llegó a
ella.

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\correr.py --mutaciones --filtro sin-nave
python tests\correr.py --mutaciones --filtro comodines
python tests\correr.py --mutaciones --filtro panel-
python tests\correr.py --mutaciones --filtro filas-
python tests\correr.py --mutaciones --filtro consola-
python tests\correr.py --mutaciones --filtro respaldo-
python tests\correr.py --mutaciones --filtro one-sin-aviso
python tests\correr.py --mutaciones --filtro mk-vuelve
python tests\correr.py --mutaciones --filtro hmm-vuelve
python tests\correr.py --mutaciones --filtro one-vessel
python tests\correr.py --mutaciones --filtro one-clic
python tests\correr.py --mutaciones --filtro msc-nave-del
python tests\correr.py --mutaciones --filtro cosco-fila
python tests\correr.py --mutaciones --filtro hmm-otra-nave
python tests\correr.py --todo
```

Las sondas son de solo lectura y no se versionan, porque leen datos reales. Quedaron en la carpeta temporal de la
sesión (`scratchpad\e28`) y se corren desde la raíz con `python <sonda>.py`. Cada una aborta si su control no da lo
esperado, salvo el chequeo que se anota en la pieza 4.
- **`modal_hmm.py`, el modal en `logs/`:** en cada reserva de HYUNDAI (identificada por su captura `hmm_f<fila>_1_ref`),
  si `log.txt` registra que el programa pulsó el OK del modal, si hubo tarjeta elegida y si llegó a Booking Details.
- **`modal_dom.py`, el HTML de HYUNDAI:** si trae `#vesselOptionSubmit` o «Alternate».
- **`lista_hmm.py`, la lista de HYUNDAI con OCR:**
  - cuántas palabras de la nave pedida y de la tarjeta elegida hay en la captura de la lista, en la de la revisión y en
    el HTML de la guarda;
  - y cuántas palabras de la lista se diferencian en 1 o 2 letras de las que faltan.
- **Las planillas:**
  - `formas_nave.py` y `formas_consola.py` dan la forma de la nave por hoja, con los dos lectores;
  - `regla_en_planillas.py` cuenta las filas sin nave con `_fila_sin_nave`, cargado desde una copia.
- **`respaldos_dom.py` y `cosco_un_boton.py`, los caminos alternativos cuando falta el campo o la fila:**
  - si cada tarjeta de MSC trae su «Vessel Voyage … ETD»;
  - y si cada «Book now» de COSCO tiene su fila a 8 niveles o menos, con un solo «Book now».
- **`dialogos_one.py`:** cuántas líneas «cerré un modal emergente» hay en los `log.txt`.
- **`e26\red_por_commit.py` y `e26\funciones_cambiadas.py`:** la red por commit y las piezas cambiadas, leídas de git
  con `ast`.

## NO retroceder (pieza 2)

- **No vuelvas a dejar que una fila sin nave llegue al portal** ni que quede OMITIDO: tiene que quedar NO ENVIADA con su
  motivo, también en la planilla.
- **No vuelvas a tener dos listas de comodines, ni una regla por naviera:** `NAVES_COMODIN` y `_fila_sin_nave` son las
  únicas. `test_una_sola_regla` lo vigila.
- **No vuelvas a dejar sin marcar en el panel la fila sin nave:** así no llegaba a la planilla.
- **No vuelvas a quitar palabras de la nave antes de calzar,** ni con una lista `ignore` ni con otra.
- **No vuelvas a pulsar nada en «Vessel Information» de ONE ni en «Alternate Vessel Option» de HYUNDAI** antes de la
  guarda.
- **No vuelvas a comparar con otra cosa que la nave** cuando falta su campo o su fila (MSC y COSCO).
- **No vuelvas a poner un atajo que elija la primera salida.** La regla es que el programa nunca reserve una nave que
  la fila no pidió; los casos que todavía quedan están en el residual.

## Universo y cobertura (pieza 3)

- **`logs/`:** 9 carpetas, las 9 con `log.txt`; 0 descartadas. Reservas de HYUNDAI que llegaron a elegir nave: 8.
  Capturas de su lista: 8 de 8. HTML de HYUNDAI: 10, de la guarda y del Remark; ninguno de la lista.
- **El HTML de las demás:** MSC, 18 archivos con 79 tarjetas; COSCO, 15 archivos con 8 «Book now».
- **Las planillas:**
  - el lector del panel leyó los 2 libros (la raíz y la copia del panel), con sus 7 hojas cada uno y 60 filas por libro,
    y no dejó ninguna hoja sin leer;
  - el de la consola leyó 30 filas, las de las seis hojas de naviera de la raíz: no lee CONSOLIDADO ni la copia del
    panel.
- **El código:** el barrido leyó las seis navieras y los orquestadores, con 8 agentes: uno por naviera, uno para lo común
  y uno para el mapa de pruebas.
- **Git:** las funciones de nivel superior cambiadas en cada commit, con `ast`.
  - Los lectores de la planilla (`leer_filas`, `leer_reservas`, `_mapear`, `_filas_de_hoja`), `es_modo_emision` y
    `_resultado_envio` son idénticos en los tres.
  - De `_evidencia_antes_de_la_guarda`, solo cambió su comentario de ayuda (el docstring): el cuerpo y la firma son
    idénticos.
- **No medido:**
  - qué muestra el modal «Alternate Vessel Option» (no está en el HTML), y si sale también con la nave pedida;
  - el HTML de la lista de HYUNDAI y de CMA;
  - «Vessel Information» de ONE en una corrida real.

## Defectos de instrumento cazados (pieza 4)

1. **Las pruebas del panel no pasaban por el panel.** Llamaban a `/api/correr` directo, y el JavaScript del panel tenía
   su propia regla: dejaba sin marcar la fila vacía, que nunca llegaba a la planilla. Lo cazó la revisión del ítem 1.
   Ahora `/api/filas` trae `sin_nave`, y una prueba en Node fija la selección.
2. **Nada probaba la mitad del decorador que deja pasar la fila con nave.** Una mutación que cortara todas las
   reservas sobrevivía. Se sumó `test_con_nave_pasa_igual`, con tres mutaciones.
3. **`_fila_sin_nave` separaba solo por espacios:** «AUTO.», «PRIMERA/DISPONIBLE» y «AUTO X» pedían una nave. Ahora
   separa las palabras como las navieras.
4. **En el primer censo del ítem 1, tres mutaciones no mordían.** Eran casos incompletos, no comprobaciones que no
   sirvieran:
   - Sin `.upper()`, las minúsculas no forman palabras. Por eso un comodín en minúsculas («auto») quedaba sin nave con
     el defecto y sin él. La mata una nave con minúsculas, «Ñandú», que con el defecto quedaría sin nave.
   - El orden del resumen no se veía, porque la fila sin nave iba primero en la hoja.
   - El control viejo de «sin filas elegidas» quedó tapado por el nuevo, «ninguna fila trae nave», que corre después
     sobre las mismas filas. La prueba ahora exige además que no salga el aviso de las filas sin nave (lectura (e):
     enmascarado por la pieza que corre después).
5. **La revisión del ítem 2 encontró dos arreglos a medias:**
   - COSCO aceptaba como fila un contenedor con otro «Book now»;
   - ONE cerraba «Vessel Information» con «Cancel» y seguía.

   Los dos se completaron antes del commit, con su medición en el HTML guardado.
6. **La revisión del ítem 3 encontró dos huecos:**
   - nada fijaba dónde van los dos cortes: ahora `test_los_dos_cortes_en_su_lugar` los ubica y los corre tal como están;
   - la prueba de que ningún otro código toca el botón del modal miraba solo dentro de las funciones: ahora
     `test_la_reserva_queda_no_enviada_con_el_motivo` mira todo el módulo.
7. **La herramienta Bash cambia `\\` por `\`:** un aplicador de mutaciones no encontró su texto y abortó sin escribir.
   Se reescribió con Write. Otro error de escape, en el ítem 2, se cazó antes de correr.
8. **Una prueba de tiempos,** `test_instancia_previa_ociosa_se_apaga`, cayó una vez con la máquina cargada por corridas
   de otras sesiones. Pasó en 4 corridas sueltas y en la repetición del gate.
9. **Una expectativa de ONE estaba mal escrita:** en la página falsa, el botón de la tarjeta va antes que el del
   diálogo. Se cazó al correrla.
10. **`sort` de Git Bash está bloqueado por Defender:** un conteo lo usó, y se rehízo con Python.
11. **El prechequeo con filtro vacío tardó más de 40 minutos con la máquina cargada:** se detuvo, y se usaron filtros
    por mutación. La unicidad de todos los textos viejos se comprueba igual.
12. **`formas_consola.py` compara `BASE` con la ruta corta del temporal y da False,** aunque leyó la copia (resueltas
    son la misma ruta). Ese chequeo no aborta. La sonda nueva, `regla_en_planillas.py`, compara las dos rutas
    resueltas y aborta si no coinciden.
13. **El OCR:** su control por fila son las palabras de la tarjeta elegida, que se pulsó y tuvo que estar en la lista.
    Sin ese control, «el nombre no está» podía ser un error de lectura.
14. **Dos cifras del borrador de este informe no respaldadas** las cazó su revisión: «con un solo "Book now"» en COSCO
    (se midió aparte, sin guardar la sonda) y «ninguna fila real cambia», que la sonda de formas no aplicaba con la
    regla nueva. Las dos quedaron medidas con sondas guardadas: `cosco_un_boton.py` y `regla_en_planillas.py`.

## Premisas del encargo contrastadas (pieza 5)

- **«La base: 339 pruebas, 744 mutaciones y 897 pares en `a198645`»:** confirmada.
- **«Se mide qué comodines reconocen hoy CMA y HYUNDAI»:** confirmada, y más.
  - Eran cinco lugares en los reservadores (CMA, dos en HYUNDAI, ONE y COSCO), más dos en el panel (su JavaScript y
    `leer_filas`).
  - HYUNDAI los reconocía en dos lugares, con dos efectos distintos.
- **«`AQUASHIELD_PRIMERA_NAVE` de MAERSK»:** confirmada. Era el único lector de esa variable, y ninguna otra variable
  cambia cómo se elige una nave.
- **«Cualquier otro atajo»:** aparecieron 4 más, en HYUNDAI, ONE, MSC y COSCO. Se eliminaron y se reportan.
- **«Hoy el programa acepta el modal antes de la guarda»:** confirmada, 8 de 8.
- **«HYUNDAI ofreció otra nave»:** parcial. En las 8, la nave elegida era otra, pero no está medido qué ofrece el modal
  ni si sale con la nave pedida. El motivo quedó como se decidió, y el aviso en pantalla dice solo lo medido.
- **Premisa de la medición del ítem 3:** la nave pedida de cada una de las 8 reservas sale de la copia actual de la
  planilla, por su número de fila. Que esas filas no cambiaron desde el 21 no se midió.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| **HYUNDAI: si el modal sale siempre, ninguna reserva pasa** | La evidencia no trae una reserva con la nave pedida en la lista | …la próxima prueba deja `hmm_f*_otra_nave` con la nave pedida elegida. Entonces decides qué hacer con el modal |
| Una fila con solo el prefijo de la naviera («MSC», «CMA CGM», «HMM», «COSCO», «MAERSK», «ONE») calza con cualquier nave suya | No es un comodín medido; 0 filas reales así | …decides si esos prefijos son comodines |
| El calce por parte del texto («ALFA» calza en «ALFABETO»), y las palabras de una letra, que no se buscan. «NA» pide una nave | Es la regla decidida en `CICLO-cola-tres-items.md` | …decides el calce por palabra entera |
| El clic por posición no vuelve a leer la tarjeta (ONE, MSC, COSCO y MAERSK). HYUNDAI, cuando su portal muestra la versión anterior de la lista, cuenta también las tarjetas ocultas | No se midió que la lista cambie entre la lectura y el clic | …una evidencia muestra otra nave en la guarda |
| ONE: el diálogo genérico acepta OK, Accept o Aceptar. Un «Vessel Information» que saliera entre la revisión y un «Next» del asistente podría recibir ese clic | El clic genérico (`_JS_CLICK_BTN`) lo usan también el login y el envío después de la guarda: cambiarlo habría tocado ese envío | …una corrida lo muestra, o decides otro clic para el asistente |
| CMA: una ruta preseleccionada (con «Deseleccionar») no se verifica. CMA y HYUNDAI calzan con toda la tarjeta, y la de HYUNDAI es el primer contenedor con la marca de ruta, sin exigir un solo «Book Now» | Falta el HTML de sus listas | …se miden `cma_f*_rutas` y `hmm_f*_naves` |
| La consola toma la nave de la columna F en ONE y MSC si la celda viene vacía | El encargo prohíbe tocar qué columnas lee el lector; 0 filas reales vacías | …decides tocar el lector |
| MANUAL: el panel la deja sin marcar, y no está en `NAVES_COMODIN` | No era un comodín medido de CMA ni de HYUNDAI | …decides si es comodín |
| El viaje: COSCO cae a la misma nave con otro viaje, y MAERSK también, si ninguna salida trae el viaje pedido | Es la misma nave | …decides que el viaje también se exija |
| COSCO: si el puerto de carga no se selecciona, busca desde un puerto fijo del código y no desde el de la fila | No es otra nave, pero sí otra salida | …decides cortar en vez de cambiar el origen |
| MSC y COSCO: si no leen la nave, el mensaje dice «no está» y lista entradas vacías | El estado no reserva: es el lado seguro | …decides el texto |
| El programa no vuelve a leer la nave en la pantalla de revisión | La evidencia de la guarda permite medirlo después | …decides verificarla antes de la guarda |
| CMA: la rama de su comodín quedó detrás del decorador, y sus dos pruebas cubren código que ya no se alcanza. Las mutaciones que reponen la lista de CMA y la regla de HYUNDAI solo las mata la foto de `test_una_sola_regla` | Se dejó como defensa | …decides quitarla |
| El aviso del mecanismo de evidencia dice «la reserva sigue igual» también donde la reserva corta | Es el texto de siempre del mecanismo | …decides otro texto |
| Los residuales de `CICLO-cola-tres-items.md` y anteriores, salvo los que cierra este encargo: la lista `ignore` de HYUNDAI, `AQUASHIELD_PRIMERA_NAVE`, el modal «Alternate Vessel Option» y los comodines de CMA y HYUNDAI | No son parte de este encargo | …según cada fila de esos informes |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v13**:
- **PASO 0 con veredicto:** CICLO para los tres ítems. El freno del ítem 3 se midió antes de tocar su código, y no se
  activó.
- **Re-medir contra HEAD:** la base del encargo, con `red_por_commit.py`.
- **Control positivo que aborta:** en cada sonda (logs, OCR, planillas, HTML), salvo el chequeo de la pieza 4, punto 12.
- **Todo salto silencioso lleva contador:** 0 carpetas descartadas, las hojas de cada lector y las filas de cada uno.
- **La unidad la fija el sujeto:**
  - el modal decide por reserva, y se midió por reserva;
  - la fila sin nave, por fila;
  - los caminos alternativos, por tarjeta y por botón.
- **Todo registro es una hipótesis:**
  - «HYUNDAI ofreció otra nave» se contrastó y quedó parcial;
  - «CMA y HYUNDAI» resultaron ser siete lugares.
- **El negativo tiene que morder:**
  - en cada commit, un censo filtrado a las mutaciones nuevas y a las que apuntan a pruebas cambiadas, repetido tras
    cada revisión;
  - el censo completo al final.

  Los tres negativos vacuos del primer censo eran casos incompletos (lecturas (b) y (e)).
- **Un gate en cero prueba contención:** por eso cada ítem pasó por una revisión adversarial.
- **Fuente única:** `NAVES_COMODIN` y `_fila_sin_nave`, usadas por los dos orquestadores, el decorador, CMA y
  `/api/filas`.
- **El cambio y su guardián en la misma operación; cada reemplazo afirma su viejo una vez; el EOL se preserva:**
  - los aplicadores afirmaron cada texto y abortaron cuando no calzó;
  - todos los archivos de los commits tienen 0 CR.
- **FRENAR cuando la decisión es de negocio:** lo del residual queda reportado, no hecho. El motivo del ítem 3 no se
  cambió, aunque dice más de lo medido.
- **Choques entre lo pedido y lo prohibido, resueltos sin frenar el encargo:**
  - el ítem 2 pedía eliminar todo atajo, y el encargo prohíbe tocar el lector: el camino de la columna F queda
    reportado;
  - cambiar el clic genérico de ONE habría tocado el envío después de la guarda, y tocarlo obliga a FRENAR TODO: por
    eso no se cambió, y queda reportado.

Reglas del módulo:
- casos sintéticos que imitan la estructura medida;
- la sonda de secretos antes de cada commit, que bloquea el nombre del operador;
- nada de `logs/` en el repo;
- los textos nuevos en español con tuteo.

## Entregable (pieza 8)

Este `.md` (no se convirtió en página) y `CLAUDE.md` al día.

**La red por commit** (`red_por_commit.py`):

| Commit | Pruebas | Mutaciones | Pares |
|---|---|---|---|
| `a198645` (base) | 339 | 744 | 897 |
| `dd0cfff` (ítem 1) | 349 | 790 | 961 |
| `44a7331` (ítem 2) | 351 | 800 | 971 |
| `714cbaa` (ítem 3) | 356 | 814 | 986 |

**Gates.**
- En cada gate, la suite completa pasó con 0 cambios en los originales, y la sonda de secretos dio 0 sobre lo agregado
  con `git add`.
- Los censos filtran por mutación: las nuevas, las reancladas y las que apuntan a una prueba cambiada.
- El ítem 1 corrió su gate después de su revisión. Tras corregir los 3 negativos vacuos, repitió la suite y los 2
  filtros que los contenían; la tabla trae los dos.
- Los ítems 2 y 3 corrieron su gate dos veces, antes y después de su revisión; la tabla trae el segundo.

| Commit | Suite completa | Censos filtrados |
|---|---|---|
| Ítem 1, `dd0cfff` | 349 en verde. El primer intento cayó por la prueba de tiempos (pieza 4) | 16 filtros, 143 mutaciones y 185 pares; 3 no mordieron y se corrigieron. En la repetición, `sin-nave` (39 mutaciones y 55 pares) y `worker-sin-filas` (2 y 2): todas muerden |
| Ítem 2, `44a7331` | 351 en verde | 31 filtros, 32 mutaciones y 34 pares; todas muerden |
| Ítem 3, `714cbaa` | 356 en verde | 33 filtros, 33 mutaciones y 57 pares; todas muerden |

- **Censo completo final sobre `714cbaa`:** pasó, en 32 minutos.
  - 356 pruebas en verde, y la copia de control, sin mutar, pasa;
  - 814 mutaciones y 986 pares: los 986 muerden;
  - 0 pruebas sin mutación y 0 cambios en los 2312 archivos originales fotografiados.
