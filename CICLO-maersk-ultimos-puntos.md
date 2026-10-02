# CICLO · Los últimos puntos de MAERSK: la referencia por su name, el Shipper sin clics a ciegas (FRENO), nunca fin de semana y más cortes

**Módulo:** Agendamiento Reservas · **Encargo 37** · **Fecha:** 2026-09-28 · **Método:** skill `metodo-ciclo` v14 ·
**Commits** (locales; el repo no tiene remoto, así que no hay push que entregar):
- `75e3ec6`: «Booking Information» sin avanzar;
- `16edb0e`: la tarjeta ilegible;
- `d87220d`: nunca fin de semana;
- `f3d3a05`: la referencia por su name;
- `9092bff`: el Shipper por su tarjeta y la foto con «.last»;
- `db93ad6`: lo que encontró la revisión de código, incluida la premisa del Shipper, que estaba mal medida;
- y el de este informe, con `CLAUDE.md` al día y dos comentarios corregidos (pieza 8).

**Base: `C:\dev\Agendamiento Reservas` @ `ac6b092` · árbol limpio** (pieza 9). Lo medido sale del HTML de «Additional
details» del 27-09 (`mk_f10_sin_objetivo.html`), de los `log.txt` de las 9 corridas con MAERSK y de las 6 capturas
`_5c_details`. **El HTML y las capturas son de después de los clics a ciegas del Shipper**, y los `log.txt` no anotan
cómo estaba la tarjeta antes (pieza 4, 1).

> Datos reales solo en lectura. Los HTML se abrieron en un Chromium sin red y sin el JavaScript de la página; las
> capturas se leyeron con OCR, sin mirarlas. En este informe no van nombres de naves, viajes, puertos, depósitos,
> partes ni números de reserva; de las partes, solo si traen a AQUACHILE, la empresa que opera el programa.

**Resumen.**
- **El Shipper: se cumple tu FRENA SI, y lo más probable es que MAERSK corte ahí en la prueba de las seis navieras.**
  - El código de antes pulsaba a ciegas el primer «+ Add» de la página y después «el último elemento con AQUACHILE».
  - Lo más probable es que el Shipper venga vacío, y que esos clics fueran los que elegían a AQUACHILE: el «Add» del
    Shipper era el primero de la página, y el último elemento con AQUACHILE era su resultado en el buscador de partes.
    - En el HTML del 27-09, guardado después de esos clics, el buscador tiene su ventana titulada «Shipper», con
      AQUACHILE entre sus resultados, y hoy el último elemento con AQUACHILE está dentro del buscador.
    - El 21-09, las 5 filas anotaron «shipper=AQUACHILE», y todo indica que vino de la rama que pulsaba (en «Lo
      medido»).
    - Si el Shipper hubiera venido lleno, el primer «+ Add» habría sido el de «Inward Forwarder», y AQUACHILE habría
      quedado ahí: esa tarjeta está vacía.
    - No está medido de forma directa: ninguna corrida guardó la tarjeta antes de esos clics, y el título «Shipper» del
      buscador podría ser su valor por defecto.
  - Ahora el programa lee la tarjeta «Shipper» por lo que es y no pulsa nada a ciegas. Si AQUACHILE no está, corta (NO
    ENVIADA) y deja el HTML de esa pantalla; si la tarjeta viene vacía, trae justo lo que falta medir: su «Add».
  - Elegirlo pide pulsar ese «Add», que ninguna corrida guardó: tu FRENA SI. Decides tú (pregunta 1).
- **Mi primera medición dijo lo contrario** («AQUACHILE ya venía»): tomé como estado de partida lo que quedó después de
  los clics. Lo cazó la revisión de código. El mensaje de `9092bff` lleva esa premisa, y el de `db93ad6` escribe la
  corrección como un hecho, cuando es la explicación más probable (pieza 4, 1).
- **La referencia de retiro, por su name:** el único textarea a la vista con `name="haulageReference"`, medido. El
  «primer textarea» de antes era, el 27-09, el campo oculto del asistente «Ask Maersk»; ese día la referencia llegó a su
  campo por un respaldo, la etiqueta. A MAERSK ya no le queda ninguna forma genérica en la foto de clics.
- **La foto ve «.last» sin paréntesis, y «.nth(-1)».** La única forma nueva que habría visto era la del Shipper.
- **La fecha de retiro, nunca sábado ni domingo.** Con el calendario del 21-09 (inferido), el lunes 28 en vez del
  domingo 27, si el 28 está habilitado.
- **Más caminos a NO ENVIADA, todos sin pulsar nada más:** «Booking Information» que no avanza (con lo que el portal
  pide y su HTML), la tarjeta de la fecha ilegible, la referencia sin un solo campo o sin poder escribirse, y el Shipper
  sin una sola tarjeta o sin AQUACHILE.
- **Las carpetas de censos cortados en `%TEMP%`:** borré las 29 que habían dejado corridas anteriores de la red (18
  vacías, 15 744 archivos, 2,78 GB), por su prefijo `aquashield_mut_` y sin ningún `correr.py` vivo en la máquina, sin
  fallas.
- **Nada de esto se probó en el portal.** `test_candado` no cambia.

## Veredicto del PASO 0, por parte del encargo

| Parte | Veredicto | Qué quedó |
|---|---|---|
| La referencia de retiro por lo que es | **CICLO** | `f3d3a05` |
| El Shipper por lo que es | **CICLO:** leer si AQUACHILE viene, en su tarjeta | `9092bff`, corregido en `db93ad6` |
| FRENA SI: identificar el Shipper exige un dato o un clic no medido | **PREGUNTA:** se cumple para elegirlo; pide el «Add» de la tarjeta vacía, que no tiene HTML | El programa corta sin pulsar nada; decides tú |
| La foto detecta «.last» sin paréntesis | **CICLO** | `9092bff`, más «.nth(-1)» en `db93ad6` |
| Nunca sábado ni domingo | **CICLO** | `d87220d` |
| FRENA SI: la regla del día hábil no se puede aplicar con lo que muestra el calendario | **NOTA:** no se puede medir antes, porque el calendario sigue sin HTML; si en la corrida no puede aplicarla, el programa frena | El corte de siempre, con su motivo |
| «Booking Information» sin avanzar: NO ENVIADA | **CICLO** | `75e3ec6` |
| La tarjeta ilegible: NO ENVIADA | **CICLO** | `16edb0e`, corregido en `db93ad6` |
| Borrar las carpetas de censos cortados, por su prefijo | **CICLO** | Borradas las 29, sin fallas |
| `test_candado` no cambia | **NOTA:** se cumple | Sin cambios |

## Lo medido

**Los `log.txt`** (`shipper_logs.py`): 21 en `logs/`: 9 con reservas de MAERSK, 12 sin MAERSK (saltados) y 0
ilegibles. Las 9 traen 13 filas de MAERSK; 6 llegaron a «Additional details»: las 5 del 21-09 y la del 27-09.
- En las 6, la referencia quedó escrita por el respaldo, «haulage reference completada (label)»; nunca por el primer
  localizador.
- «Shipper/Booked By ya asignado» no aparece ni una vez, con 0 corridas descartadas.
- El 21-09, las 5 filas traen «shipper=AQUACHILE».
  - El código que corrió ese día no está versionado: el primer commit, `14aa9ef`, es del 23-09. Con ese código, cuyas
    frases calzan con ese `log.txt`, «shipper=…» se anotaba en dos ramas: la de «ya asignado» y la que pulsaba.
  - Como «ya asignado» no aparece nunca, lo más probable es que viniera de la que pulsaba: primero el «+ Add» y después
    el último elemento con AQUACHILE, y solo si ese clic salía.
  - El 27-09 no se ve: esa fila terminó en el corte de la revisión, que no lo anota.

**El HTML de «Additional details» del 27-09**, guardado después de esos clics (`partes_real.py`, `partes_forma.py`,
`textarea_real.py`, `buscador_real.py`, `buscador_botones.js`):
- **La referencia:** tres elementos llevan `name="haulageReference"`: el `mc-textarea` (a la vista, con la etiqueta
  «Enter haulage reference (optional)»), un `input` oculto y el `textarea` de su raíz shadow, a la vista.
  `textarea[name='haulageReference']` da 1, a la vista. La etiqueta exacta da 0 (el programa usaba una expresión, que da
  1). El localizador de antes calzaba con 2 textarea, y su primero era el campo oculto del asistente «Ask Maersk».
- **Las tarjetas `mc-c-party-card`:** 13.
  - 10 son las partes, todas a la vista, cada una con su parte en el atributo `title` («Booked By», «Shipper»,
    «Consignee»…).
  - Las 2 llenas, «Booked By» y «Shipper», traen a AQUACHILE en su raíz shadow; las 8 vacías tienen su «Add».
  - La del Shipper tiene `title="Shipper"`, `id="shipper"` y los botones «Remove» y «Change customer».
  - Las otras 3 son los resultados del buscador: ocultas y sin `title`.
- **El buscador de partes:** uno solo (`mc-c-party-finder`), con su ventana (`mc-modal`) cerrada y titulada «Shipper».
  - Trae 3 resultados, cada uno una tarjeta dentro de un `label`, y 1 de ellos con AQUACHILE.
  - Sus controles son un botón «Close», dos pestañas («Search» y otra) y «Cancel» como acción secundaria. No tiene botón
    de confirmar.
- **Lo que miraba el programa:** el primer `div, section, mc-card` con «Parties» es el `div.main`. Su `textContent`, de
  739 caracteres, no trae a AQUACHILE; su texto con las raíces shadow, sí. Por eso nunca concluía que estaba.
- **Los clics de antes, sobre esta página:** el primer «+ Add» cae hoy en la tarjeta «Inward Forwarder», porque la del
  Shipper ya está llena; de los 20 elementos con AQUACHILE que calzan con su filtro, el último está hoy dentro del
  buscador, oculto.

**Las capturas `_5c_details`, por OCR y sin mirarlas** (`ocr_partes.py`), también posteriores a esos clics: en las 6,
AQUACHILE aparece en 3 líneas: una sin parte cerca (lo más probable, el encabezado de la cuenta), una junto a «Booked
By» y otra junto a «Shipper». Ninguna junto a «Forwarder».

**Lo que eso dice.** Lo más probable es que el Shipper viniera vacío y que su «Add» fuera el primero de la página.
Entonces el último elemento con AQUACHILE era su resultado en el buscador de partes, y el clic en él lo eligió:
- el 21-09, «shipper=AQUACHILE» exige que ese clic haya salido; en el HTML del 27-09, el último elemento con AQUACHILE
  está hoy dentro del buscador, oculto: lo más probable es que, al pulsarlo, el buscador estuviera abierto;
- si el Shipper hubiera venido lleno, el primer «+ Add» habría sido el de «Inward Forwarder», y AQUACHILE habría quedado
  ahí: esa tarjeta está vacía, y el OCR no pone a AQUACHILE junto a «Forwarder».

No está medido de forma directa: ninguna corrida guardó la tarjeta antes de esos clics, y el título «Shipper» del
buscador podría ser su valor por defecto (sin el JavaScript de la página no se distingue).

**La foto de clics** (`foto_last.py`, con el detector de `tests/test_clics.py`, sobre la base `ac6b092`): con «.last»
también sin paréntesis delante, la única forma nueva en el universo de la foto era `loc_aqua.last` del Shipper. En todo
`AQUASHIELD.py` no había otro `.last` sin paréntesis ni ningún `.nth(-1)`.

## Cómo quedó cada punto

**1. «Booking Information» sin avanzar** (`_mk_booking_sin_avanzar`): NO ENVIADA con «MAERSK: en «Booking
Information», el portal no dejó avanzar y pide: …; no pulsé nada más y la reserva no se envió (…)», o «…no pude leer qué
pide». Deja la evidencia `mk_f<fila>_booking`: los avisos de esa pantalla no están medidos. La prueba ahora corre el
ayudante; hasta ahí solo miraba la forma del código.

**2. La tarjeta ilegible** (`_mk_comprobar_retiro`): la espera hasta 5 s mientras siga sin fecha, sin tarjeta o sin
poder leerla (hasta `9092bff`, solo mientras seguía sin fecha). Si no, «MAERSK: elegí el DD-MM-AAAA en el calendario,
pero no pude leer qué fecha muestra la tarjeta; no pulsé nada más y la reserva no se envió», con «(no la encontré)» si
no hay tarjeta y «(no pude leer la página: …)» si la lectura falla; y la evidencia `mk_f<fila>_retiro`, la misma de los
otros dos cortes.

**3. Nunca sábado ni domingo** (`_mk_elegir_dia_de_retiro`): del día que toca en adelante, salta los sábados y domingos
sin pedirles su fecha, porque nunca se eligen, y elige el primer día hábil habilitado. Si hasta el último día a la vista
no hay uno, corta como antes: «no hay un día hábil habilitado del … al …, el último que muestra el calendario, y cambiar
de mes es un clic que no está permitido». Los feriados siguen contando como hábiles.

**4. La referencia de retiro** (`_mk_referencia_de_retiro`, `MK_REFERENCIA`): escribe en el único
`textarea[name='haulageReference']` a la vista.
- Sin uno solo, corta sin escribir: «Referencia de retiro de MAERSK: no encontré un solo campo «haulageReference» a la
  vista (había N), así que no pulsé nada…», con `mk_f<fila>_sin_objetivo`. Si la lectura falla, en lugar de «había N»
  dice «no pude leer la página: …».
- Si la escritura falla: «MAERSK: falló la escritura de la referencia de retiro (…); no pulsé nada más…», sin evidencia
  (residual).

**5. El Shipper** (`_mk_shipper`, `_JS_MK_SHIPPER`): busca la única tarjeta `mc-c-party-card` a la vista con
`title="Shipper"` y lee su texto con el de su raíz shadow; la espera hasta 5 s (`MK_ESPERA_SHIPPER`, hipótesis).
- Si trae a AQUACHILE: «Shipper: AQUACHILE ya viene en la tarjeta «Shipper»; no pulsé nada».
- Si no hay una sola: «Shipper de MAERSK: no encontré una sola tarjeta «Shipper» a la vista (había N), así que no pulsé
  nada…», o «no pude leer la página: …» si la lectura falla.
- Si no trae a AQUACHILE (lo más probable): «Shipper de MAERSK: no encontré a AQUACHILE en la tarjeta «Shipper»:
  elegirlo pide clics que no están medidos, así que no pulsé nada…».
- Los dos cortes son NO ENVIADA, con `mk_f<fila>_sin_objetivo`. Si la tarjeta viene vacía, ese HTML la trae con su
  «Add».

**6. La foto** (`tests/test_clics.py`, «ultimo-por-posicion»): calza también «.last» sin paréntesis delante y
«.nth(-1)». Lee el texto fuente del universo, docstrings y comentarios incluidos (pieza 4, 7).
- Una prueba nueva, `test_nada_se_traga_el_corte`, vigila que ningún `except` de lo que corre antes de la guarda atrape
  el corte: ni `ObjetivoNoEncontrado`, ni `BaseException`, ni un `except` desnudo.
- No ve un `try` que envuelva la guarda ni un `contextlib.suppress`; hoy no hay ninguno (medido por la revisión).

**7. Las carpetas de `%TEMP%`:** `tests/correr.py` crea su carpeta de trabajo, `aquashield_mut_*`, en `%TEMP%` al
importarse y la borra en el `finally` de `main`. Ese `finally` no corre si el proceso se mata, y calla si no puede
borrarla (`ignore_errors=True`). Adentro solo hay archivos versionados: las fuentes del programa, mutadas o no
(`AQUASHIELD.py`, `AQUASHIELD_EMISION.py`, los dos `.bat` y `config.example.json`, la plantilla sin claves), y el
archivo mutado de cada mutación de otro archivo (la sonda de secretos, `LEEME.md` o un generador).
- Había 30: 29 de corridas anteriores, del 24 al 28-09, y la del censo completo, que corría y se borró sola al terminar.
- Con el censo terminado, `borrar_mut.py contar` no vio ningún `correr.py` vivo en la máquina. Entonces
  `borrar_mut.py borrar` borró las 29 por su prefijo, sin fallas y sin reintentar, y ya no queda ninguna.
- No tocó `%TEMP%\aquashield_planilla.xlsx`, la copia de la planilla del panel web, porque su prefijo es otro.
- La nota quedó en `CLAUDE.md`.

## Cómo probarlo

Con **`Iniciar AQUASHIELD.bat`**; nunca con `Iniciar AQUASHIELD_EMISION.bat`. Antes, revisa que `config.json` no traiga
`"emitir_reservas": true` en «opciones» y que no esté definida la variable `AQUASHIELD_EMITIR` (la abren 1, true, si o
yes): con cualquiera de las tres llaves, se emite. Corre una o más filas de MAERSK con su nave.

En `log.txt`, en «Additional details», después de la fecha de retiro:
1. «haulage reference completada: '…'»;
2. si el Shipper viene vacío, lo más probable: «✗ NO ENVIADA · Shipper de MAERSK: no encontré a AQUACHILE en la tarjeta
   «Shipper»…», con `mk_f<fila>_sin_objetivo`. Es el resultado esperado mientras dure el FRENO, y su HTML es el que
   falta medir;
3. si AQUACHILE ya viene: «Shipper: AQUACHILE ya viene en la tarjeta «Shipper»; no pulsé nada», y sigue a la revisión.

Si el día que toca no está habilitado: «Fecha de retiro: el … no está habilitado en el calendario: elijo el siguiente
día hábil habilitado, el … (día)», nunca un sábado ni un domingo. Lo demás, como en `CICLO-maersk-retiro-y-terminos.md`.
Dime qué corrida fue y leo su evidencia en `logs/`.

## Qué decides tú

1. **Cómo sigue el Shipper.**
   - **a) Ir a la prueba así.** Si AQUACHILE no viene, MAERSK corta en el Shipper y, si la tarjeta viene vacía, deja su
     HTML con el «Add». Con
     ese HTML, el próximo encargo implementa la elección con todo medido. Es lo que pide tu FRENA SI, y lo recomiendo;
     el costo es que en esta prueba MAERSK no llega a la revisión.
   - **b) Autorizar ya dos clics identificados:** el «Add» de la tarjeta «Shipper» y el único resultado con AQUACHILE en
     el buscador titulado «Shipper». Después comprobaría que la tarjeta quedó con AQUACHILE y, si no, cortaría.
     - Medido en el HTML del 27-09: el buscador y su resultado. El buscador no tiene botón de confirmar; después del
       clic de antes y de Escape, la tarjeta mostraba a AQUACHILE en las 6 capturas.
     - Sin medir: el «Add» de la tarjeta vacía. Se infiere de las otras 8 partes vacías (el mismo componente).
   - **c) Mirar tú en el portal, sin pulsar nada,** si la tarjeta «Shipper» viene vacía al llegar a «Additional
     details». Confirma o descarta la explicación antes de la prueba, y no cambia el programa.
2. **Los feriados cuentan como días hábiles.** Tu regla es de lunes a viernes. Si quieres que no cuenten, hace falta la
   lista de feriados.
3. **Otros REVISAR de MAERSK antes de la guarda:** el formulario que no abre o queda incompleto, la búsqueda de salidas
   que no termina y la nave que no está (esta, REVISAR por tu decisión, `CICLO-ampliar-la-busqueda.md`). ¿Pasamos
   alguno a NO ENVIADA, como «Booking Information»?
4. **La tecla Escape después del Shipper.** Servía para cerrar el buscador que abría el «+ Add»; ahora nada se abre ahí.
   La dejé, porque no se pidió quitarla. ¿La saco?

## Re-medir (pieza 1)

Las sondas son de solo lectura y no se versionan, porque leen datos reales. Quedaron en el scratchpad de esta sesión
(`$env:TEMP\claude\<proyecto>\<sesión>\scratchpad\e37`), que puede limpiarse; sin ellas, estos números no se re-miden.
Todas abortan si no pasa su control positivo, salvo las que solo cuentan o copian: `temp_mut.py`, `lista_mut.py`,
`red_por_commit.py`, `copia.py` y `anclas.py`.
- **`shipper_logs.py`:** por corrida de MAERSK, cuántas veces aparece en `log.txt` cada paso de «Additional details»
  (filas, la referencia y su respaldo, el Shipper, «shipper=AQUACHILE», «Review booking»), con los `log.txt` sin MAERSK
  y los ilegibles contados. Imprime solo la fecha de la carpeta. Su control: un log sintético con cada frase una vez.
- **`partes_real.py`:** sobre el HTML del 27-09, los elementos con `name="haulageReference"`, lo que miraba el programa
  para el Shipper, los «+ Add» y, de cada tarjeta, si se ve y si trae a AQUACHILE, con los textos tapados. Su control:
  una tarjeta sintética con el nombre solo en su raíz shadow.
- **`partes_forma.py`:** la forma de las tarjetas «Booked By», «Shipper» y «Consignee»: sus atributos y el árbol de su
  raíz shadow, con los textos que no son de la interfaz tapados. Su control: una tarjeta sintética con su título.
- **`buscador_real.py`:** el buscador de partes (su ventana, su encabezado, sus resultados), la tarjeta del Shipper, y
  dónde caen hoy los dos clics de antes. Su control: un buscador sintético en raíces shadow.
- **`sonda.py buscador_botones.js <html>`:** los controles del buscador (pestañas y botones) con su etiqueta si es de la
  interfaz. El control es el de `sonda.py`.
- **`textarea_real.py`** (en `scratchpad\e36`): qué textarea tomaba el localizador de antes, y qué daba su respaldo.
- **`ocr_partes.py`:** en las 6 capturas `_5c_details`, las líneas del OCR con AQUACHILE y la parte que tienen cerca.
  Sus controles: una imagen sintética, y que cada captura traiga «Parties» o «Pick-up date».
- **`foto_last.py`:** el detector de la foto, sacado de `tests/test_clics.py`, con «.last» también sin paréntesis. Su
  control: la foto tiene que dar exactamente `PERMITIDOS`. Contra HEAD aborta, porque la foto ya calza «.last»: córrela
  sobre una copia de `ac6b092` (`copia.py ac6b092`, con su `RAIZ` apuntando ahí).
- **`copia.py [rev]` y `anclas.py <copia>`:** una copia del repo (`git archive`, leído con `tarfile`) para probar cada
  cambio sin tocar la raíz; y las mutaciones cuya ancla no aparece exactamente una vez, con las líneas nuevas de más de
  120.
- **`temp_mut.py [carpeta a dejar fuera]`:** las carpetas `aquashield_mut_*` de `%TEMP%`, con sus archivos y bytes; y
  **`lista_mut.py`**, las mismas con su fecha de creación, para reconocer la de un censo que está corriendo.
- **`borrar_mut.py contar|borrar`:** cuenta esas carpetas y los `correr.py` vivos en la máquina (por su línea de
  comandos), y con «borrar» las borra por su prefijo, sin reintentar, solo si no hay ninguno vivo. Su control: con el
  censo corriendo, «contar» tiene que verlo (dio 1); se corre a mano.
- **`red_por_commit.py <rev>…`:** pruebas, mutaciones y pares de cada commit, con `git show`.
- **Los cambios y los gates:** `aplicar_k1.py` a `aplicar_k6.py` (ediciones con anclas únicas), `aplicar_docs37.py`,
  `gate.sh`, `censo.sh` y `commit.sh`.

La red versionada, desde `C:\dev\Agendamiento Reservas`: `python tests/correr.py` (la suite, de 4 a 5 min),
`python tests/correr.py --mutaciones --filtro <texto>` (el censo de lo que nombra ese texto: `shipper`, `referencia`,
`TestRetiroMaersk`…) y `python tests/correr.py --mutaciones` (el censo completo).

## NO retroceder (pieza 2)

- **No tomes como estado de partida lo que guardó un corte:** es posterior a todo lo que el programa pulsó antes. Así
  concluí que AQUACHILE venía como Shipper.
- **No busques a la empresa en el `textContent` de la página:** el nombre de cada parte va en la raíz shadow de su
  tarjeta, y así el programa concluía siempre que AQUACHILE no estaba.
- **No pulses «+ Add» por posición:** el primero de la página es el de la primera parte vacía, sea cual sea. Y el del
  Shipper, solo con tu decisión (FRENO).
- **No vuelvas a «el primer textarea» para la referencia:** el 27-09 era el campo oculto del asistente «Ask Maersk».
- **No busques la referencia por su etiqueta exacta:** «Enter haulage reference (optional)» da 0 en el HTML medido; su
  name da 1.
- **No vuelvas a aceptar un sábado o un domingo como fecha de retiro.**
- **No dejes seguir una tarjeta ilegible ni «Booking Information» sin avanzar en REVISAR:** son decisiones de Marcelo.
- **No atrapes `ObjetivoNoEncontrado` ni `BaseException` antes de la guarda:** te tragarías el corte.
- **No nombres una forma genérica en un docstring ni en un comentario del universo de la foto:** la foto lee el texto
  fuente y cae.
- **No vuelvas a limitar «ultimo-por-posicion» a «).last»:** así no veía el Shipper.

## Universo y cobertura (pieza 3)

- **`log.txt`:** 21 en `logs/`: 9 con reservas de MAERSK (13 filas), 12 sin MAERSK y 0 ilegibles; 6 llegaron a
  «Additional details» (5 del 21-09 y 1 del 27-09). No hay corridas nuevas desde el 27-09.
- **HTML:** 1 página de «Additional details», la del 27-09: 3 elementos con `name="haulageReference"`; 13 tarjetas (las
  10 partes, a la vista, y los 3 resultados del buscador, ocultos); 8 «+ Add»; 1 buscador. Las otras 7 páginas de MAERSK
  son de «Select sailing».
- **Capturas:** las 6 `_5c_details`, por OCR y sin mirarlas.
- **La foto:** el universo de los seis reservadores, con sus ayudantes y las constantes que nombran; para «.last» sin
  paréntesis, además, todo `AQUASHIELD.py`.
- **`%TEMP%`:** 30 carpetas `aquashield_mut_*` antes de borrar: 29 de corridas anteriores, del 24 al 28-09 (11 con
  archivos y 18 vacías), y la del censo completo, que se borró sola al terminar. Nada más en el repo usa ese prefijo.
- **No medido:**
  - la tarjeta «Shipper» antes de los clics de antes, con su «Add»: todo lo guardado es posterior;
  - si el título «Shipper» del buscador es su valor por defecto;
  - qué hace el portal al pulsar el resultado del buscador: no hay botón de confirmar, y después del clic de antes y de
    Escape, la tarjeta mostraba a AQUACHILE en las 6 capturas;
  - el campo de la referencia el 21-09: ese día no se guardaba HTML, y su `log.txt` dice que calzó la etiqueta;
  - el calendario, la tarjeta con una fecha y la revisión, que siguen sin HTML (`CICLO-maersk-retiro-y-terminos.md`).

## Defectos de instrumento cazados (pieza 4)

1. **Medí el Shipper después de los clics de antes y lo tomé como el estado de partida.** El HTML del 27-09 y las 6
   capturas son posteriores a esos clics, y concluí que AQUACHILE «ya venía».
   - Lo cazó la revisión de código, con tres datos que verifiqué: el buscador titulado «Shipper», el último elemento con
     AQUACHILE hoy dentro del buscador, y las 5 «shipper=AQUACHILE» del 21-09.
   - El mensaje de `9092bff` afirma la premisa equivocada. El de `db93ad6`, el comentario del código y un docstring de
     prueba escribieron la corrección como un hecho, cuando es la explicación más probable. El comentario y el
     docstring se corrigieron en el commit de este informe; los mensajes, aquí.
   - El código de `9092bff` no pulsa nada, así que el error no cambia lo que hace: cambia lo que se esperaba de él
     (MAERSK corta en el Shipper).
2. **Conté las 13 tarjetas como 13 partes:** 3 son los resultados ocultos del buscador, sin `title`. Lo cazó la revisión
   del informe.
3. **Mi primera sonda imprimió en mi consola el nombre del operador:** para rotular las carpetas de `logs/` tomé parte
   de su nombre, que lo lleva. No está en ningún archivo del repo ni en este informe; las sondas siguientes imprimen
   solo la fecha.
4. **El primer gate del cambio 1 empezó con líneas nuevas de más de 120** (un docstring, un comentario y dos
   mutaciones). Lo vi con el gate corriendo: lo paré, cerré sus 6 procesos por su PID, corregí y lo volví a correr.
5. **La herramienta Bash convirtió `\\` en `\`** en un script de reemplazo: la aserción de ancla única lo frenó antes de
   escribir, y lo rehíce con Edit.
6. **Escribir `AQUASHIELD.py` justo después de un `git checkout` falló una vez con «Invalid argument».** El archivo
   quedó intacto (igual a HEAD) y el reintento pasó. La causa probable, el antivirus, no la medí.
7. **Mi docstring de `_mk_shipper` decía «(loc_aqua.last)»,** y la foto, que lee el texto fuente, lo cazó como una forma
   genérica nueva. Lo reescribí, y la lección quedó en `CLAUDE.md`.
8. **El cambio 4 dejó sin ancla una mutación del encargo 36** (`maersk-vuelve-el-primer-dia`). La cazó `anclas.py` en la
   copia, antes del gate, y la mutación pasó al comentario nuevo.
9. **Dos errores míos en las sondas del buscador:** `buscador_real.py` tenía dos identificadores iguales en su
   JavaScript y falló a la primera, sin imprimir nada de la página; y conté sus controles como botones, cuando «Search»
   y otra son pestañas.

## Premisas del encargo contrastadas (pieza 5)

- **«Shipper: cuando AQUACHILE no viene asignado, hoy se pulsa el último elemento que contiene AQUACHILE»:**
  confirmada, y con más. Lo más probable es que nunca viniera asignado. Y aunque viniera, el programa no lo habría
  visto (las raíces shadow), así que esa rama corría siempre: primero el primer «+ Add» de la página y después ese
  elemento.
- **«La referencia se escribe en «el primer textarea», que en el HTML del 27-09 es el campo oculto del asistente»:**
  confirmada, con un matiz: como ese campo no estaba a la vista, el programa no escribió ahí. El 27-09 escribió en el
  campo correcto, por el respaldo de la etiqueta (medido); el 21-09, el `log.txt` dice que también por la etiqueta. El
  riesgo era con el asistente abierto.
- **«Su name o su etiqueta, medidos en ese HTML»:** el name, sí (1 a la vista); la etiqueta exacta, no (0).
- **«La foto de clics tiene que detectar también «.last» sin paréntesis»:** hecho. En el universo había una sola, la
  del Shipper.
- **FRENA SI del Shipper:** se cumple para elegirlo. **FRENA SI del día hábil:** no se pudo contrastar, porque el
  calendario sigue sin HTML.
- **«Se borran las carpetas de censos cortados en %TEMP%, solo las de la red, por su prefijo»:** confirmada, con un
  matiz. Las 11 con archivos son de censos: solo el censo copia fuentes ahí. Las 18 vacías pueden ser de cualquier
  corrida de `correr.py`, también de la suite, cortada antes de su `finally` o con un borrado que falló sin avisar
  (`ignore_errors=True`). Todas llevan el prefijo que pone `tests/correr.py`, lo único que lo usa.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| Elegir a AQUACHILE como Shipper: el programa corta, NO ENVIADA; lo más probable es que MAERSK no llegue a la revisión | FRENO: el «Add» de la tarjeta vacía no está medido | …eliges a, b o c (pregunta 1) |
| Que el Shipper venga vacío es la explicación más probable, no una medición | Todo lo guardado es posterior a los clics de antes | …la prueba o tu mirada al portal lo muestran |
| Si falla la escritura de la referencia, no queda evidencia | La del paso queda solo si no hay un solo campo | …pasa en una corrida |
| `test_nada_se_traga_el_corte` no ve un `try` que envuelva la guarda ni un `contextlib.suppress` | Mira los `except` del universo; hoy no hay ninguno de esos | …aparece uno |
| El texto «haulageReference» del motivo no sale de `MK_REFERENCIA` | Menor | …cambia el name del campo |
| Los feriados cuentan como días hábiles | Tu regla es de lunes a viernes | …me das la lista (pregunta 2) |
| Otros REVISAR de MAERSK antes de la guarda | Fuera del encargo | …lo decides (pregunta 3) |
| La tecla Escape después del Shipper | No se pidió quitarla | …lo decides (pregunta 4) |
| El respaldo en JavaScript de «Review booking» pulsa el primer elemento cuyo texto lo trae, que es `<html>`, y la foto no lo ve | De antes y fuera del encargo (lo vio la revisión) | …la tarea aparte lo mide (te la propongo) |
| El Shipper se compara con AQUACHILE, no con el cliente de la fila (`_mk_cliente`) | Como antes | …una fila trae otro cliente |
| `MK_ESPERA_SHIPPER` (5 s) es una hipótesis | Sin medir | …la prueba muestra otra cosa |
| El calendario, la tarjeta con una fecha y la revisión siguen sin HTML; el clic de JavaScript en la casilla, sin probar | Del encargo 36 | …la prueba los deja |
| Si falla el clic en «Choose another date», no queda evidencia | Del encargo 36 | …pasa en una corrida |
| Las otras navieras no dicen lo que pide el portal | El encargo 36 era de MAERSK | …otra naviera lo necesita |
| `tests/correr.py` borra su carpeta de `%TEMP%` con `ignore_errors=True`: si no puede, la deja sin avisar, y de dónde salieron las 18 vacías no está medido | Fuera del encargo, que pedía borrarlas | …vuelven a juntarse carpetas |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v14**.
- **PASO 0 con sus cuatro valores:** CICLO en las seis partes; PREGUNTA para el FRENA SI del Shipper; NOTA para el del
  día hábil (no se puede medir antes) y para `test_candado`.
- **FRENAR cuando la decisión es de negocio:** elegir el Shipper, los feriados, los otros REVISAR y la tecla Escape
  quedan como preguntas.
- **Control positivo que aborta:** en cada sonda que mide (pieza 1).
- **Todo salto silencioso lleva contador:** 21 `log.txt`: 9 con MAERSK, 12 saltados, 0 ilegibles; 13 filas, 6 en
  «Additional details»; 0 «ya asignado» con 0 corridas descartadas; 5 «shipper=AQUACHILE».
- **El negativo tiene que morder:** cada prueba nueva con su mutación; un precenso de las mutaciones nuevas en una copia
  antes de los gates; el censo filtrado en cada commit, y el completo en el último.
- **Todo registro es una hipótesis, también el mío:** «AQUACHILE ya viene» era mi lectura de un estado posterior a los
  clics, y no tenía sustento. La revisión adversarial la corrigió, y la corrección también es una hipótesis: la más
  probable, no una medición.
- **Re-medir contra HEAD:** el código se leyó en `ac6b092`, y cada cambio se probó sobre una copia de su commit padre.
- **Fuente única:** una constante por objetivo identificado (`MK_REFERENCIA`, `MK_SHIPPER`, `MK_EMPRESA`), y el
  JavaScript del Shipper sobre el mismo recorrido (`_JS_MK_RECORRER`).
- **Cada reemplazo, exactamente una vez, y el EOL preservado:** ediciones con anclas únicas; 0 CR en cada commit.
- **El cambio y su guardián, juntos:** cada commit con sus pruebas y sus mutaciones.
- **Choques entre reglas:**
  1. **«Se identifica por lo que es, medido» contra «FRENA SI no hay HTML de esa pantalla»:** leer la tarjeta está
     medido en su forma llena; la vacía se infiere de las otras 8 partes vacías, y elegirlo no está medido. El programa
     lee la tarjeta y, si no viene, corta sin pulsar: el FRENA SI queda en la corrida, como el del calendario en el
     encargo 36.
  2. **«Cerrar los últimos puntos antes de la prueba» contra el FRENA SI:** con el FRENO, MAERSK probablemente no llega
     a la revisión en esa prueba. No lo resolví por ti: es la pregunta 1.
  3. **«La foto tiene que detectar .last» contra mis propios docstrings:** la foto lee el texto fuente; reescribí el
     mío.

Reglas del módulo: nada de `logs/` en el repo; ningún nombre de nave, viaje, puerto, depósito, parte ni operador, ni
número de reserva, en este informe; `test_candado` sin cambios; la sonda de secretos antes de cada commit; los textos en
español con tuteo.

## Entregable (pieza 8)

- **Este `.md`:** no se convirtió en página; se leyó como texto.
- **`CLAUDE.md` al día,** en el commit de este informe: la referencia y el Shipper (con el FRENO), la foto con «.last»,
  «.nth(-1)» y lo que lee, «nada se traga el corte», nunca fin de semana, los cortes, `mk_f<fila>_booking`, los estados,
  el número de pruebas y las carpetas de `%TEMP%`.
- **En el mismo commit, dos cambios que no tocan el código:** el comentario del Shipper en `AQUASHIELD.py` y el
  docstring de `TestShipperMaersk`, que afirmaban como hecho que los clics de antes eligieron a AQUACHILE; ahora dicen
  que es lo más probable. Son posteriores al censo completo; ninguna mutación tiene su ancla en esas líneas, y su gate
  fue la suite completa: 457 pruebas en OK en 232 s, con 0 cambios en los 2894 originales.
- **La red, commit por commit:**

| Commit | Pruebas | Mutaciones | Pares |
|---|---|---|---|
| `ac6b092` (base) | 443 | 1216 | 1464 |
| `75e3ec6` | 444 | 1219 | 1468 |
| `16edb0e` | 444 | 1221 | 1471 |
| `d87220d` | 444 | 1223 | 1474 |
| `f3d3a05` | 449 | 1230 | 1483 |
| `9092bff` | 455 | 1242 | 1495 |
| `db93ad6` | 457 | 1251 | 1504 |

- **El gate de cada commit:** la suite completa en verde, con 0 cambios en los originales, y los censos filtrados
  (mutaciones / pares), todos en OK:

| Commit | Suite | Censos filtrados |
|---|---|---|
| `75e3ec6` | 444 | TestMaersk 87/112 · TestCadaReservadorLaDeja 27/57 |
| `16edb0e` | 444 | TestRetiroMaersk 70/84 · TestCadaReservadorLaDeja 28/59 |
| `d87220d` | 444 | TestRetiroMaersk 72/87 |
| `f3d3a05` | 449 | referencia 13/18 · TestFotoDeClicsGenericos 31/59 |
| `9092bff` | 455 | shipper 12/12 · TestFotoDeClicsGenericos 32/60 |
| `db93ad6` | 457 | shipper 16/16 · referencia 16/21 · TestRetiroMaersk 74/89 · TestSinClicACiegas 22/31 · TestFotoDeClicsGenericos 33/61 |

- **Antes de los gates,** las mutaciones nuevas de los cambios 3 a 5 se censaron en una copia de `75e3ec6` con los
  cambios 2 a 5: shipper 12/12, referencia 13/18, fin de semana 1/2 y sábado 2/2, todas en OK.
- **El censo completo sobre `db93ad6`:** 1251 mutaciones y 1504 pares, y todas muerden: 0 que no muerden y 0 con tiempo
  agotado. Son 457 pruebas, 0 sin mutación, y el control (la copia sin mutar) pasa. Hubo 0 cambios en los 2894
  originales fotografiados.
  - Duró 52 min 37 s, sin suspensión del equipo: 0 eventos de Kernel-Power entre las 22:10 y las 23:10, y la misma
    consulta sí encuentra los de la tarde.
  - Tampoco se tocó la raíz mientras corría.
- **Cada commit:** la sonda de secretos dio 0 sobre el árbol y 0 sobre lo agregado, y 0 CR en los archivos commiteados.
- **La revisión de código:** un agente, en solo lectura, con páginas sintéticas en Node y en un Chromium sin red, y con
  el HTML real del 27-09.
  - Resultado: 0 críticos, 1 alto (probable), 1 medio y 3 bajos. Confirmó que lo que corre después de la guarda no
    cambió en ninguna naviera.
  - **El alto:** la premisa del Shipper (pieza 4, 1). Lo verifiqué y corregí lo que sí se podía: el comentario, el
    docstring y una espera acotada. Elegir queda en tu pregunta 1.
  - **El medio:** la tarjeta ilegible cortaba a la primera lectura; ahora espera hasta 5 s.
  - **Los bajos:**
    - la red no veía un corte tragado por quien llama; ahora sí, con `test_nada_se_traga_el_corte`, y la foto ve
      «.nth(-1)»;
    - los motivos decían «había 0» cuando la lectura fallaba;
    - `CLAUDE.md` estaba desfasado.
  - Todo quedó en `db93ad6`, salvo `CLAUDE.md`, que va en el commit de este informe.
  - **Fuera del diff,** vio el respaldo de «Review booking» que pulsa `<html>` (residual) y la tecla Escape sin
    propósito (pregunta 4).
- **La revisión adversarial de este informe:** un agente, en solo lectura y con sus propias sondas (sin mirar capturas).
  - Confirmó los conteos de `log.txt`, lo medido en el HTML del 27-09 y las tablas de red y de gates, sin voseo ni datos
    reales. Y agregó dos datos que refuerzan la explicación del Shipper (en «Lo que eso dice»).
  - Trajo 2 hallazgos altos, 5 medios y 14 bajos, verificados y corregidos en esta versión.
  - **Los altos:** la explicación nueva escrita como hecho (pieza 4, 1) y las 13 tarjetas contadas como partes (pieza 4,
    2).
  - **Los medios:** «hasta `db93ad6`»; la pieza 1 (una sonda que aborta contra HEAD, un conteo sin sonda, una ruta y los
    controles); el veredicto de `%TEMP%` puesto antes de borrar; la inferencia del 21-09; y los valores del PASO 0 y los
    descartados.
  - **Los bajos:**
    - los controles del buscador, el calendario del 21-09 (inferido) y dos «medido» que eran inferidos;
    - predicciones escritas como hechos y los caminos a NO ENVIADA;
    - los comentarios que lee la foto, dos preguntas y `AQUASHIELD_EMITIR`;
    - lo que leyó la revisión de código, el precenso, la redacción, el alcance de `test_nada_se_traga_el_corte` y el
      motivo de la referencia.
