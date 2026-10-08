# Encargo 58: la temperatura guardada de CMA-CGM, la mercancía, el puerto que se suelta tarde y el login del 08-10

Base: `Agendamiento Reservas` @ `38142be` · árbol limpio (al empezar, 2026-10-08).

## En resumen

- **CMA-CGM comprueba que el portal guardó la temperatura** (decisión de Marcelo).
  - Después del «Guardar» del panel Reefer y de su evidencia, el programa lee la página hasta 20 veces, cada 0,5 s,
    sin clics ni teclas.
  - La da por guardada solo con las tres señales medidas en los HTML guardados:
    - el cajón del panel ya no está;
    - la insignia de la fila Reefer ya no dice «to complete»;
    - la carga muestra en «Operando en» la temperatura que se escribió.
  - Si no, la fila queda NO ENVIADA con el motivo (lo que faltó), la captura y el HTML del paso.
  - Medido corriendo la comprobación en un Chromium sin red sobre los HTML reales:
    - da por guardada la temperatura en los 9 de después del «Guardar» y en los 9 de la guarda;
    - corta en los 10 con el panel abierto.
- **La mercancía (HS 030313) corta si el programa falla antes de elegirla** (decisión de Marcelo), como el tamaño, el
  peso, el panel Reefer y «I Agree» del encargo 57. Hasta ahora anotaba «mercancía err» y la reserva seguía sin ella.
- **La cantidad no se cambió: se cumple el primer FRENA SI.**
  - El paso de la cantidad nunca encontró su campo: sus selectores no calzan con el del portal (medido en los 59 HTML
    guardados con el formulario).
  - En las 14 reservas que llegaron a la guarda, `log.txt` no trae ni una línea «cantidad:», y fueron con el 1 del
    portal.
  - Que corte «igual que los otros pasos» (que cortan cuando no encuentran lo suyo) las habría dejado NO ENVIADA a las
    14. Lo decides tú (Lo decides tú, 1).
- **El lanzador vuelve a probar el puerto unos instantes antes de saltarlo** (decisión de Marcelo), sin cerrar a nadie.
  - Lo prueba hasta 1 s, cada 0,05 s, solo enlazándolo.
  - Medido sin red: Windows suelta el puerto a los 11 ms o menos después del reset, y el `bind` hecho enseguida falló
    en 3 de 20 corridas con el equipo quieto y en 8 de 40 con la CPU ocupada.
  - Hasta ahora lo probaba una sola vez, y tomaba el siguiente.
- **El inicio de sesión de CMA-CGM del 08-10, solo lectura** (sección 4):
  - apareció el deslizador;
  - la pausa terminó con «Ya lo resolví», a los 4 s, no sola;
  - CMA-CGM tardó 26,4 s, de abrir el portal a «Sesión iniciada»;
  - actuaron piezas de los encargos 54, 55 y 56: la espera a que DataDome terminara de cargar (2,6 s, y mostró el
    deslizador), y las líneas de la pausa en `log.txt`;
  - de las del 57 no hay rastro: ni «Detener» ni la pausa que termina sola entraron en juego.
- **Los dos FRENA SI:**
  - **Primero, se cumple, por la cantidad.**
    - Con la comprobación de la temperatura, ninguna de las 9 reservas medibles (de las 14) habría quedado NO ENVIADA.
    - Las otras 5, del 21-09, no tienen HTML, y el OCR de sus capturas no pasó su control: quedan sin medir.
    - Con el corte de la mercancía, ninguna: las 14 la eligieron.
    - Con un corte de la cantidad como el de los otros pasos, las 14 (por eso no lo hice).
  - **Segundo, no se cumple:** la comprobación usa solo señales que están en los HTML guardados; no mira si algo se ve,
    porque eso no está en el HTML.
- Sin clics nuevos; `test_candado` no cambió; nada toca el disfraz del navegador ni la protección.

## 1. Lo que se midió antes de cambiar nada

### Las señales de la temperatura guardada

`estructura_reefer.py`, `senales_reefer.py` y `operando_en.py` sobre los HTML guardados de CMA en `logs/`:
`cma_f*_reefer_panel` (el panel abierto, antes de «Guardar»), `cma_f*_reefer_guardado` (1,5 s después de pulsarlo) y
`cma_f*_guarda`.

| señal | panel abierto (10) | tras «Guardar» (9) | guarda (9) |
|---|---|---|---|
| un elemento con la clase `reefer-drawer` (el cajón) | 9 (el del 24-09 no: era el panel oculto de `CICLO-cola-nueve-items.md`) | 0 | 0 |
| botones «Modifique el reefer» | 1 en cada uno | 1 | 1 |
| la `.capsule` de la `.capsule-container` de ese botón | «to complete» (clase `error-light`) en los 10 | «completed» (clase `completed`) en los 9 | «completed» en los 9 |
| `.cargo-wrapper--info-details-item` con `<dt>` «Operando en» | 0 | 1, con `<dd>` «-20 °C» | 1, con «-20 °C» |
| «°C» en toda la página | 0 | 1 (ese) | 1 (ese) |

La temperatura no está en la fila de la insignia, como se esperaba, sino en el detalle de la carga, con el rótulo
«Operando en». La primera sonda la buscaba por un `<dt>` con «temperat» y abortó por su control (defecto 1).

### Las reservas de CMA-CGM que llegaron a la guarda (primer FRENA SI)

`sondeo_guarda.py` (la del encargo 57, con la cantidad y la mercancía): 38 `log.txt` leídos, 22 bloques de CMA, **14 en
la guarda**, 0 líneas descartadas.

| paso | de las 14 |
|---|---|
| tamaño y tipo, peso, Reefer guardado, «I Agree» | 14 |
| mercancía elegida («mercancía seleccionada:») | 14; «mercancía err», 0 |
| **cantidad escrita («cantidad:»)** | **0** |

Las 14: 5 del 21-09 a las 16:54 (las que se emitieron, sin HTML) y 9 del 25-09 al 02-10 (con HTML).

- **La temperatura:** las 9 con HTML, corridas por la comprobación nueva (`calce_temperatura.py`, abajo): 0 cortadas.
  - Las 5 del 21-09 no tienen HTML.
  - Probé leer sus capturas de la revisión (`cma_f*_5_review.png`) con OCR (`ocr_revision.py`), y no se pudo: su
    control no pasó (defecto 2). Esas 5 quedan sin medir.
- **La mercancía:** las 14 la eligieron. Las 5 reservas del 21-09 a las 14:58, que no llegaron a la guarda, anotaron
  «mercancía err» y reintentaron la información extra (encargo 57). Con el corte, quedan NO ENVIADA en ese primer
  intento.
- **La cantidad:** el paso nunca la escribió. `cantidad_html.py`, sobre los 59 HTML guardados que traen el formulario
  de la carga («Peso por contenedor»):
  - ninguno trae lo que buscan sus selectores: `.el-input-number input` (0), `input[role=spinbutton]` (0) ni un
    placeholder «Cantidad» (0);
  - los 59 traen un `.el-form-item` con la etiqueta «Cantidad» y, adentro, un `input` sin tipo, sin clase y sin
    placeholder; en los 10 del panel abierto, su atributo `value` es «1»;
  - la planilla de hoy no trae una columna de cantidad (0 encabezados con «cant» o «qty» en sus 2 hojas), así que el
    programa siempre pide 1, que es lo que el portal ya trae.

  Si el paso cortara cuando no encuentra su campo, como los otros, las 14 habrían quedado NO ENVIADA. Por eso no lo
  toqué.

### El puerto que Windows suelta un instante tarde

`medir_suelta.py`: un ocupante escucha sin aceptar, un `urlopen` le pregunta, otro hilo lo cierra a los 0,5 s, y al
volver la pregunta se prueba el `bind` cada 10 ms.

| equipo | corridas | volvieron con reset | el primer `bind` falló | se pudo enlazar a los |
|---|---|---|---|---|
| quieto | 20 | 20 | 3 | 11 ms o menos |
| con `carga.py 16` | 40 | 40 | 8 | 11 ms o menos |

En el encargo 57, en el caso de la prueba (el `Timer` de 2 s), una corrida soltó el puerto a los 0,22 s. Por eso el
lanzador lo vuelve a probar hasta 1 s (hipótesis: unas 90 veces lo más largo de esta medición).

### Antes y después, sin red

`contra_head.py`, con las fuentes de `38142be` y con las del árbol, sobre las páginas falsas de las pruebas:

| caso | antes (`38142be`) | ahora |
|---|---|---|
| el panel Reefer sigue abierto tras «Guardar» | OK-EJEMPLO, «siguió hasta la guarda» (0 lecturas) | NO ENVIADA, «Temperatura guardada de CMA: … el panel Reefer sigue en la página» (20 lecturas) |
| el campo de la mercancía no se deja pulsar | OK-EJEMPLO, con «mercancía err» en `log.txt` | NO ENVIADA, «Mercancía de CMA: … porque el programa falló al buscarla o elegirla» |
| el puerto se suelta un instante después de la segunda pregunta | tomó el puerto siguiente (1 prueba) | tomó el suyo (3 pruebas) |

`medir_puerto.py` (la del encargo 57, el caso de la prueba con el `Timer`), con el equipo cargado por otros programas
(88 % de CPU): tomaron el puerto base 30 de 30 con `38142be` y 30 de 30 con el árbol. Así la carrera no apareció, y esa
medición no distingue; la distingue la prueba nueva, que hace el instante sin reloj.

## 2. Lo que cambió

### La temperatura guardada

- `_JS_CMA_TEMPERATURA_GUARDADA` lee las tres señales:
  - cuántos `.reefer-drawer` hay;
  - cuántos botones «Modifique el reefer», y del único, las `.capsule` de su `.capsule-container`;
  - el texto del `<dd>` que sigue a cada `<dt>` «Operando en» de `.cargo-wrapper--info-details-item`.
- `_cma_lo_que_falta_de_la_temperatura` decide qué falta:
  - el panel que sigue;
  - no un solo botón;
  - la fila sin su insignia;
  - «to complete»;
  - ninguna temperatura, o más de una;
  - una que no se puede comparar, u otra.
- `_cma_temperatura_guardada` lee hasta `CMA_LECTURAS_TEMPERATURA` (20) veces, cada 0,5 s. Si no, corta con
  `ObjetivoNoEncontrado`: «Temperatura guardada de CMA», con lo que faltó en la última lectura.
- La comprobación va después de la evidencia `cma_f<fila>_reefer_guardado` (la que midió las señales) y antes del
  Escape con que el paso cierra lo que quede.
- Lo que falla entre el «Guardar» y la comprobación, o la comprobación misma, corta con `_cma_fallo`, «… o comprobar que
  quedó guardada».
- Después de comprobarla solo queda el Escape, que ya no cortaba. Hasta ahora, lo que fallaba después del «Guardar» se
  anotaba («ajustes reefer err») y la reserva seguía.

### La mercancía

`_cma_completar_info_extra`: la falla antes de elegir la sugerencia corta con `_cma_fallo`, con `CMA_MERCANCIA`. Lo
que busca ya era una sola constante en el corte por no encontrarla. Después de elegirla no queda nada que pueda fallar.
También corta si su campo no está: el programa prueba su placeholder en inglés, y en el portal esa espera vence.

### El lanzador

`_puerto_se_suelta(puerto)` prueba `_puerto_libre` cada 0,05 s hasta `PUERTO_SE_SUELTA` (1 s). `quien`, en
`lanzar_web`, lo usa después de la segunda pregunta, en vez de una sola prueba. Solo enlaza el puerto un instante: a
quien lo tiene no lo cierra. Con un programa que tiene el puerto y no contesta, el lanzador tarda 1 s más en saltarlo.

## 3. Pruebas, mutaciones, suite y censos

### Las pruebas nuevas (10)

| dónde | prueba | qué vigila |
|---|---|---|
| `test_clics.TestCma` | `test_lo_que_falta_para_dar_la_temperatura_por_guardada` | lo que decide con cada lectura: lo medido después del «Guardar» pasa (también con coma decimal, otra temperatura de la fila o sin insignia); el panel, «to complete», no un solo botón, la fila sin insignia, ninguna o dos temperaturas, otra, o una que no se compara, no |
| | `test_js_temperatura_guardada_por_lo_medido` | el JavaScript, en Node, sobre documentos falsos con la forma medida: el cajón, la insignia del único botón, solo el `<dd>` que sigue a «Operando en» |
| | `test_reefer_sin_la_temperatura_guardada_corta` | sin las señales, 20 lecturas cada 0,5 s y el corte con lo que faltó, sin otro clic ni el Escape |
| | `test_reefer_con_la_temperatura_guardada_sigue` | con ellas, sigue (en la lectura 1, 4 o 20) y lo dice en `log.txt`; el Escape que falla después no corta |
| | `test_la_comprobacion_que_falla_corta` | la lectura que falla o no vuelve corta con `_cma_fallo` |
| | `test_mercancia_que_falla_corta` | el clic en su campo, o en el de su placeholder en inglés, que falla: corta, sin «mercancía err» |
| | `test_la_temperatura_y_la_mercancia_dejan_la_fila_no_enviada_con_su_evidencia` | con los decoradores de `reservar_cma`: NO ENVIADA, el motivo literal, la captura y el HTML, y nada sigue |
| | `test_la_comprobacion_va_tras_la_evidencia_y_antes_del_escape` | el orden en `_cma_ajustes_reefer`: «Guardar», la evidencia, la comprobación, el Escape |
| `test_web.TestArranqueDelPanel` | `test_puerto_que_windows_suelta_un_instante_despues` | el lanzador de verdad toma su puerto cuando Windows lo suelta dos pruebas después del reset (un `_puerto_libre` falso, sin reloj) |
| | `test_puerto_se_suelta_prueba_unos_instantes` | `_puerto_se_suelta` con un reloj falso: 21 pruebas, 20 esperas de 0,05 s, y el ocupante sigue escuchando; libre, una sola prueba |

**Fotos que cambiaron a propósito:**
- `test_reefer_que_falla_antes_de_guardar_corta` y
  `test_los_cuatro_que_fallan_dejan_la_fila_no_enviada_con_su_evidencia`: el motivo dice «… o comprobar que quedó
  guardada».
- `test_lo_que_falla_despues_de_guardar_el_reefer_sigue_como_antes` pasó a
  `test_lo_que_falla_entre_el_guardar_y_la_comprobacion_corta`: lo que fallaba después del «Guardar» se anotaba, y
  ahora corta.
- `test_lo_que_buscan` suma lo que buscan la mercancía y la comprobación.
- Las tres de `test_evidencia.TestEvidenciaReefer`: una lectura más, sin clics ni teclas, entre la evidencia de lo
  guardado y el Escape.

**Los falsos que cambiaron:**
- `PaginaCmaQueNoPulsa`: también el localizador por placeholder.
- Nuevo, `PaginaCmaQueGuarda`: la comprobación lee lo que se le dé y anota cada espera.
- El panel falso de `test_evidencia`: responde lo medido después del «Guardar».

### Las mutaciones

- **30 nuevas** (`e58-*`):
  - la comprobación quitada, antes de la evidencia o tragándose su falla;
  - el clic o la espera de después del «Guardar» que se tragan, y el Escape que corta;
  - cada señal sin mirar o mirada de otra forma, en Python y en el JavaScript;
  - una lectura, cada 2 s, una espera de más, o sin decirlo;
  - la mercancía que sigue, o lo que buscan con otro texto;
  - el lanzador que prueba una vez, sin esperar, cada medio segundo o sin ver que se soltó.
- **3 reancladas:** `teclado-cma-mercancia`, `e52-lanzador-no-vuelve-a-probar` y `e57-reefer-falla-sigue`.
- **2 retiradas:** `e57-reefer-guardado-corta` y `e57-reefer-guardado-antes-del-clic`. Anclaban en la bandera
  `guardado`, que ya no existe; las reemplazan `e58-reefer-espera-tras-guardar-se-traga` y `e58-reefer-clic-se-traga`.
- `mut_viejos.py`: 2.101 mutaciones, 723 pruebas, 0 problemas (cada texto viejo una sola vez, las nuevas compilan, toda
  prueba con su mutación).

### Los censos

- **Chico** (`censo_mini.py`, 54 mutaciones, 85 pares): no llegó a correr las mutaciones. Su control, la copia sin
  mutar, no pasó, por la prueba del reloj (defecto 8), y se detuvo sin reportar nada.
- **De las áreas del cambio** (`alcance_censo.py`, `lanzar_censo_e58.py`), de las 10:03 a las 12:59, con el equipo
  al 85-100 % por otras sesiones. Su selección:
  - las nuevas (30) y las reancladas (3);
  - las que caen en las 6 funciones que cambiaron (53);
  - las que nombran una prueba cuyo camino cambió.

  En total, 416 mutaciones, 614 pares y 198 pruebas. El control pasa, y **613 de 614 muerden**.
  - El que no, `e58-reefer-espera-tras-guardar-se-traga`, era el caso incompleto del defecto 9.
  - Completada la prueba, `censo_par.py` corrió las 2 mutaciones que la nombran: **4 de 4 pares muerden**, con 0
    cambios en los originales.
  - En la foto de los originales del censo de las áreas hubo **2 cambios que no son del censo:**
    `Reservas AQUASHIELD.xlsx` cambió a las 10:24, y su archivo de bloqueo de Excel (`~$…`), que ya estaba al empezar,
    se borró.
  - Alguien tenía la planilla abierta en Excel. Las pruebas corren sobre copias en una sandbox y no escriben en la
    raíz. No la toqué.

### La suite

`tests/correr.py` (con `correr_sin_tope.py`: el plazo de la corrida entera en 7.200 s), sobre el árbol que se commitea:
**723 pruebas, OK, en 1.259 s**, de las 13:08 a las 13:29, con 0 cambios en las 4.529 entradas fotografiadas de
los originales.

## 4. El inicio de sesión de CMA-CGM del 08-10 (solo lectura)

La corrida más reciente de `logs/` (`login_hoy.py`, que enmascara el operador, los correos, las IP y las cifras
largas): «Solo iniciar sesión» del panel web, solo con CMA-CGM, a las 08:35:47. Es del panel web porque su línea de fin
de pausa dice «el operador pulsó «Ya lo resolví»», que solo escribe ese panel.

| momento | qué pasó |
|---|---|
| +0,0 s | INICIO, y la línea del candado: «modo prueba» (encargo 51) |
| +17,8 s | abre `cma-cgm.com`; Chrome, no el respaldo (en las otras corridas de solo login, de 1,1 a 23,3 s hasta el primer portal) |
| +20,8 s | «CMA CGM muestra la verificación del navegador de DataDome, o una página vacía: espero hasta 30 s…» (encargo 54), con la captura `cma_verificacion.png` |
| +23,4 s | DataDome muestra el deslizador («Desliza hacia la derecha»), con la captura `cma_robot_desafio.png` |
| +23,4 s | «⏸ PAUSA: espero al operador. Por qué: …» (encargo 55) |
| +27,5 s | «▶ La pausa terminó a los 4 s: el operador pulsó «Ya lo resolví».» (encargos 55 y 56) |
| +29,3 s | «Verificación de CMA CGM superada ✓» |
| +30,8 a +42,1 s | menú, «Log in», formulario, credenciales, clic |
| +44,3 s | «Sesión iniciada.», «[CMA-CGM] resultado=OK (tardó 26.4s)» |

- **Apareció el deslizador.** Antes, la página mostró la verificación del navegador o una página vacía, y el programa
  esperó, sin tocar nada, a que DataDome terminara de cargar: a los 2,6 s mostró el deslizador.
- **La pausa terminó con «Ya lo resolví», a los 4 s,** no sola.
  - Desde el encargo 57, para terminar sola la pausa necesita dos lecturas seguidas sin DataDome, cada 2 s. En 4 s
    caben dos lecturas, y mientras DataDome seguía a la vista no podía terminar.
  - 1,8 s después, la espera de siempre vio la verificación superada.
- **El inicio de sesión tardó 26,4 s** en CMA-CGM (44,3 s la corrida entera, con 17,8 s para abrir Chrome).
  - Las 5 corridas de solo login anteriores con el deslizador superado tardaron 20,8; 23,9; 36,6; 38,7 y 108,4 s (de
    abrir el portal a la sesión).
  - Las 3 del 06-10 no entraron: la del bloqueo, una sin final y una de 359,7 s.
  - Es la primera que entra después del bloqueo del 06-10.
- **Las piezas que actuaron:**

  | encargo | pieza | qué hizo |
  |---|---|---|
  | 51 | la línea del candado | dijo «modo prueba» |
  | 53 | Chrome con el sandbox, por `_lanzar_navegador` | abrió Chrome, no el respaldo (el sandbox no deja rastro en `log.txt`) |
  | 54 | `_cma_datadome` | vio la verificación o la página vacía: no detuvo nada |
  | 54 | la espera de la portada (`CMA_ESPERA_PORTADA`) | esperó 2,6 s, hasta el deslizador |
  | 55 | las líneas de la pausa (`_pausa_del_panel`) | el porqué, el final y los segundos |
  | 55 | las lecturas con plazo | no dejan rastro: ninguna se rindió |
  | 56 | la pausa que termina sola y el vigía | estaban; no terminó sola, porque el operador pulsó antes |
  | 56 | «Detener» en la espera | no se usó |
  | 57 | las dos lecturas seguidas | si el panel ya corría con el código del 57, no se distingue en `log.txt` |
  | 57 | «Detener» en solo login | no se usó |

  - El `AQUASHIELD.py` en disco a esa hora ya era el del encargo 57 (escrito el 07-10 a las 23:37).
  - Si el panel se abrió antes, con el código del 56, no lo sé: ningún proceso suyo seguía vivo, y la página no lo
    dice.
- No hubo bloqueo, ni «restringido temporalmente», ni detención. Las capturas no las miré: solo sus nombres.

## Re-medir

Todo en `e58/` (carpeta del encargo), con `source entorno_e58.sh` antes.

| qué | cómo |
|---|---|
| las señales en los HTML del panel Reefer | `python estructura_reefer.py`, `python senales_reefer.py` (aborta: defecto 1) y `python operando_en.py` |
| la comprobación nueva sobre los HTML reales | `python calce_temperatura.py` (Chromium sin red, el JavaScript y la decisión del programa) |
| las 5 del 21-09 por OCR | `python ocr_revision.py` (aborta su control: defecto 2) |
| las reservas que llegaron a la guarda | `python sondeo_guarda.py` |
| el campo de la cantidad | `python cantidad_html.py` |
| cuánto tarda Windows en soltar el puerto | `python medir_suelta.py 20`; con carga, `python carga.py 16 90` en paralelo y `python medir_suelta.py 40` |
| el caso de la prueba del 57, viejo y nuevo | `python medir_puerto.py 30 fuentes_head` y `python medir_puerto.py 30 fuentes_arbol` |
| antes y después | `python contra_head.py fuentes_head` y `python contra_head.py fuentes_arbol` (`git -c core.autocrlf=false show 38142be:AQUASHIELD.py`, y la copia del árbol) |
| el inicio de sesión del 08-10 | `python login_hoy.py` y `python logins_cma.py` |
| las anclas de las mutaciones | `python mut_viejos.py <ids>` |
| los censos | `python alcance_censo.py`; `python lanzar_censo_e58.py` (aparte, sin ventana; escribe `censo_e58.txt`); `python censo_par.py` |
| la suite | `python tests/correr.py` en el repo |
| que nada toca el disfraz ni el candado | `git diff 38142be -- AQUASHIELD.py` sin `STEALTH_JS`, `_args_chrome`, `_lanzar_navegador` ni `ignore_default_args`; `git diff 38142be -- tests/test_candado.py` vacío |

## NO retroceder

- **La temperatura no se da por guardada con solo pulsar «Guardar»:** con el candado abierto, una reserva podría
  enviarse sin ella si el portal no la guardó sin avisar.
- **Las señales salen de lo que trae el HTML guardado,** no de si algo se ve: así se pueden medir sin abrir el portal.
- **La comprobación va después de la evidencia de lo guardado y antes del Escape:** lee lo mismo que se midió.
- **La mercancía no vuelve a tragarse su falla.**
- **El lanzador no da un puerto por ajeno con una sola prueba** después de un reset.

## Defectos de instrumento

1. **La primera versión de `senales_reefer.py` buscaba la temperatura por un `<dt>` que dijera «temperat»,** y no hay
   ninguno: el rótulo es «Operando en». Su control positivo (una temperatura en cada HTML de después del «Guardar»)
   abortó, como debía, y no usé lo que había contado. `dl_temp.py` mostró la estructura alrededor del único «°C», y
   `operando_en.py`, con ese rótulo, pasa su control.
2. **El OCR de las capturas no pudo medir las 5 reservas del 21-09.** No encontró ninguna de las marcas («completed»,
   «to complete», «Operando en») en las 14 capturas de la revisión, tampoco en las 9 cuyo HTML sí las trae. Su
   control, las 9 capturas de la guarda (de página completa), tampoco pasó: no lee «Operando en» en ninguna. No reporto
   lo que dio como medición: esas 5 quedan sin medir.
3. **Un `cd tests` en primer plano volvió a mover la sesión a `tests/`** (ya me pasó en los encargos 56 y 57). Desde
   ahí, los comandos van con ruta absoluta, o con el `cd` dentro de un subshell.
4. **Tres veces la herramienta Bash juntó los pares de barras invertidas de un heredoc** (la copia de `medir_puerto.py`,
   un arreglo de `mutaciones.py` y uno del script de `CLAUDE.md`). Las dos primeras no escribieron nada: su aserción
   de coincidencia única falló antes. La tercera escribió el script con una línea de 153 caracteres, que vio el control
   de largo antes de tocar `CLAUDE.md`. Las tres las rehice con Edit o Write.
5. **Edité `AQUASHIELD.py` (la simplificación del `except` del Reefer) mientras corría la primera tanda de pruebas.**
   No era `tests/correr.py` ni un censo, pero las clases que cargaron el programa después del cambio corrieron con el
   código nuevo. No usé esa tanda como compuerta: solo para ver qué fotos caían (las 7 esperadas), y volví a correr.
6. **Una prueba nueva exigía que `log.txt` no trajera «err», y «cerrado» lo trae** (el aviso de la evidencia que no se
   pudo guardar dice «vuelve a correr la fila con el candado cerrado»). Cayó en su primera corrida, y ahora busca
   «ajustes reefer err».
7. **Una mutación nueva no compilaba** (`e58-escape-que-falla-corta` dejaba un `except` sin su `try`). La vio
   `mut_viejos.py` antes del censo, y la reescribí.
8. **Escribí una prueba que dependía del reloj, justo lo que la regla del encargo 57 prohíbe.**
   `test_puerto_se_suelta_prueba_unos_instantes` contaba las pruebas del puerto en 1 s de reloj de verdad (de 10 a
   25).
   - Con el equipo al 84 % por otras sesiones, entraron 5.
   - El control del censo chico (la copia sin mutar) no pasó, y el censo se detuvo sin reportar nada, como debía.
   - Ahora corre con un reloj falso, que avanza solo con sus esperas: 21 pruebas y 20 esperas de 0,05 s, siempre.
   - Ese censo chico no lo volví a correr: el de las áreas del cambio lo contiene entero.
9. **Un negativo vacuo, enmascarado por la pieza que corre después** (la lectura (e) de la regla).
   - En el censo, `e58-reefer-espera-tras-guardar-se-traga` no mordió a
     `test_lo_que_falla_entre_el_guardar_y_la_comprobacion_corta`.
   - Esa prueba hacía fallar toda espera posterior al «Guardar». Con la espera de 1,5 s tragada, fallaba la primera
     espera de la comprobación, y el corte salía igual, con el mismo motivo.
   - La pieza no sobraba: el caso estaba incompleto.
   - Ahora la página de la prueba muestra la temperatura guardada, así que solo esa espera decide. Volví a correr ese
     par solo (abajo).

## Premisas refutadas

1. **«La cantidad de CMA-CGM corta igual que los otros pasos si falla antes de terminar»** daba por hecho que el paso
   hacía algo. No: nunca encontró su campo, porque sus selectores no calzan con el del portal (sección 1). En las 14
   reservas que llegaron a la guarda no escribió nada, y la reserva fue con el 1 que el portal ya trae. La planilla de
   hoy tampoco trae una columna de cantidad.
2. **«Se ve la temperatura»** después del «Guardar»: está en el HTML, en el detalle de la carga, con el rótulo «Operando
   en», y no en la fila de la insignia. Si se ve no lo dice el HTML guardado; la comprobación mira que esté, y no si se
   ve (segundo FRENA SI).

## Lo decides tú

1. **La cantidad de CMA-CGM** (primer FRENA SI). Hoy el paso no hace nada: no encuentra su campo y sigue sin
   decirlo. Opciones:
   - (a) que busque el campo por su etiqueta «Cantidad» (el `input` del `.el-form-item` con esa etiqueta, medido en los
     59 HTML), escriba la cantidad de la fila solo si es otra, y corte como los otros pasos si no lo encuentra o falla.
     Con la planilla de hoy, escribiría 1 donde ya hay 1;
   - (b) dejarlo como está, y que `log.txt` diga que no vio el campo;
   - (c) quitar el paso: la planilla no trae cantidad, y el portal ya trae 1.

   Propongo (a), solo si la planilla va a traer una cantidad; si no, (c).

## Residual

| # | qué queda | por qué | se reabre si |
|---|---|---|---|
| 1 | **La cantidad** sigue sin encontrar su campo y sin cortar (Lo decides tú, 1) | primer FRENA SI: cortar «igual que los otros pasos» habría dejado NO ENVIADA a las 14 | lo decides |
| 2 | Las 5 reservas del 21-09 que llegaron a la guarda no se pudieron medir con la comprobación de la temperatura | no tienen HTML, y el OCR de sus capturas no pasó su control (defecto 2) | — |
| 3 | La comprobación mira si las señales están en el HTML, no si se ven. Si el portal dejara el cajón del panel oculto en la página después de guardar (no pasó en los 9 medidos), cortaría una reserva que sí guardó | lo que se ve no está en el HTML guardado (segundo FRENA SI) | una reserva corta con «el panel Reefer sigue en la página» y su captura lo muestra cerrado |
| 4 | Si la insignia de la fila Reefer desapareciera del todo, esa señal pasa: la decisión pide que «to complete» desaparezca, no que diga «completed». La temperatura en «Operando en» sigue haciendo falta | la decisión | lo pides con «completed» |
| 5 | 20 lecturas, cada 0,5 s (unos 10 s), es una hipótesis: en los 9 medidos, las señales ya estaban a los 1,5 s | no está medido con el portal lento | una reserva corta con lo que faltaba y su HTML muestra la temperatura guardada |
| 6 | El motivo de este corte también dice «así que no pulsé nada», aunque ya se pulsó «Guardar» | el texto fijo de `_sin_clic_a_ciegas` (residual 6 del encargo 57) | lo pides con un motivo propio |
| 7 | Con un programa que tiene el puerto y no contesta, el lanzador tarda 1 s más en saltarlo | el precio de volver a probarlo | molesta al abrir el panel |
| 8 | La carrera de verdad no apareció con el equipo cargado por otros programas (30 de 30 con el lanzador viejo y con el nuevo); la distingue la prueba nueva, sin reloj | no volví a cargar la CPU a propósito: había otras sesiones corriendo sus pruebas | — |
| 9 | Del inicio de sesión del 08-10, `log.txt` no distingue si el panel corría con el código del encargo 56 o del 57 | la pausa terminó con «Ya lo resolví» antes de que el vigía pudiera decidir | — |
| 10 | Del encargo 57 siguen abiertos sus residuales 4, 6 (el 6 de aquí), 7, 8, 9 y 10. Este encargo cerró sus 1 y 3, y su 2 a medias (la mercancía; la cantidad, aquí 1) | — | — |
| 11 | Más revisiones de ECC (python-reviewer, security-reviewer, una revisión del cambio por un subagente) | se proponen, no se lanzan; este encargo no pidió revisión | las pides |
| 12 | El censo es el de las áreas del cambio, no el completo (2.101 mutaciones) | el completo pasa de 2 h, y el equipo estaba cargado | lo pides |

## Reglas de método (v16)

- **Aplicadas:** las 20 universales. En especial:
  - el contador al lado de cada cero: en `logs/`, 38 de 38 leídos, 22 bloques de CMA, 14 en la guarda, 0 descartados;
    «cantidad:» 0 de 14; en los HTML, 9 de 9 y 10 de 10 por señal; 0 problemas de anclas en 2.101 mutaciones;
  - el control positivo que aborta: cada sonda de `logs/`, `calce_temperatura.py` (en las dos direcciones: los
    guardados no cortan y los abiertos sí), `medir_suelta.py` y `mut_viejos.py`. El de `senales_reefer.py` y el del OCR
    abortaron de verdad (defectos 1 y 2), y no usé sus números;
  - la unidad la fija el sujeto: la comprobación decide por reserva, y se midió por HTML de reserva (uno por paso);
  - el negativo que muerde: cada prueba nueva con su mutación, el censo de las áreas y el del par que no mordía; y
    el negativo vacuo leído como caso incompleto, no como pieza que sobra (defecto 9);
  - re-medir contra HEAD: el antes y después, con las fuentes de `38142be`;
  - un gate en cero prueba contención, no correctitud: además de la suite, la comprobación corrida sobre los HTML
    reales y las pruebas que corren los decoradores de `reservar_cma`;
  - fuente única: `_cma_fallo` también para la mercancía, `CMA_MERCANCIA` en sus dos cortes, y la comprobación en una
    sola función;
  - el cambio y su guardián en la misma operación; cada reemplazo, una sola vez y validado antes de escribir; el EOL,
    LF (0 CR);
  - frenar en lo que es de Marcelo: la cantidad.
- **Las del módulo** (`CLAUDE.md`): `test_candado` no cambia; ningún clic nuevo; nada se traga el corte; casos
  sintéticos; nunca el puerto 8765 en una prueba; la sonda de secretos antes de cada commit; el correo noreply de autor
  y de committer; las capturas reales no se miran (el OCR solo imprime si trae cada marca).
- **Choques:**
  - **ECC pide lanzar revisores y agentes solos;** las reglas permanentes dicen que se proponen. Este encargo no pidió
    revisión: no lancé ninguna, y quedan propuestas (residual 11).
  - **«Nada fuera de la carpeta del encargo»** y **«las sesiones pueden agregar filas en Entorno Windows»:** completé la
    fila del puerto que se suelta tarde (`~/.claude/CLAUDE.md`), la del encargo 57, con lo medido aquí; nada más fuera
    de la carpeta del encargo.
- **Pieza 8 (el entregable renderizado y mirado):** opcional; este informe es Markdown y no lo rendericé.

## Lo que dio en el repo

Dos commits en `main`, sin push (el push lo haces tú):

- `5378c48` fix: el programa y las pruebas (`AQUASHIELD.py` y, en `tests/`, `mutaciones.py`, `test_clics.py`,
  `test_evidencia.py` y `test_web.py`);
- el commit siguiente, docs: `CLAUDE.md`, `LEEME.md` y este informe.

Los dos llevan de autor y de committer el correo noreply del repo, y la sonda de secretos dio 0 antes de cada uno.

El entorno de la máquina (`~/.claude/CLAUDE.md`, «Entorno Windows») suma, en la fila del puerto que se suelta tarde
(encargo 57), lo medido aquí: cuánto tarda en soltarse y que el lanzador ya lo vuelve a probar.
