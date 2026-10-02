# CICLO · El Shipper de MAERSK con dos clics, los feriados de Chile, REVISAR solo sin nave, y sin Escape ni el respaldo de «Review booking»

**Módulo:** Agendamiento Reservas · **Encargo 38** · **Fecha:** 2026-09-29 · **Método:** skill `metodo-ciclo` v14 ·
**Commits** (locales; el repo no tiene remoto, así que no hay push que entregar):
- `a189084`: «Review booking» por su texto, y sin él NO ENVIADA;
- `793cbf0`: sin la tecla Escape después del Shipper;
- `f4728e3`: antes del botón final, REVISAR solo si la nave no está;
- `cbda5be`: los feriados de Chile no son días hábiles para el retiro;
- `bae8c44`: el Shipper elige a AQUACHILE con dos clics identificados;
- `e51a786`: lo que encontró la revisión de código;
- y el de este informe, con `CLAUDE.md` al día.

**Base: `C:\dev\Agendamiento Reservas` @ `62ab849` · árbol limpio** (pieza 9). Lo medido sale del HTML de «Additional
details» del 27-09 (`mk_f10_sin_objetivo.html`), el único que hay de esa pantalla, y del código en `62ab849`.

> Datos reales solo en lectura. El HTML se abrió en un Chromium sin red y sin el JavaScript de la página, y lo que no es
> de la interfaz se imprimió tapado. Para abrirlo, cada sonda copiaba ese HTML, sin sus scripts, a una carpeta nueva de
> `%TEMP%`, y no la borraba: al cerrar se borraron por su nombre las 11 que quedaban (7 de este encargo, 1 del 37 y 3
> del 36), y ahora cada sonda borra la suya al terminar (pieza 4, 13). En este informe no van nombres de naves, viajes,
> puertos, depósitos, partes ni números de reserva; de las partes, solo si traen a AQUACHILE, la empresa que opera el
> programa. No se miró ninguna captura.

**Resumen.**
- **El Shipper, con los dos clics que decidiste.** Si la tarjeta «Shipper» no trae a AQUACHILE, el programa pulsa su
  «Add» y, en el buscador titulado «Shipper», el único resultado con AQUACHILE. Después comprueba que la tarjeta lo
  muestre y que el buscador se haya cerrado; si algo no se cumple, NO ENVIADA con su HTML, sin otro clic.
  - Ninguno de tus dos FRENA SI se cumple con lo medido: el buscador es uno solo, sus resultados se ven sin buscar y no
    tiene botón de confirmar.
  - **Sin medir, y es el riesgo de la prueba:** si el clic en el resultado lo elige y si el buscador se cierra solo al
    elegir. Antes, después del Shipper, se pulsaba la tecla Escape, que se quitó; no está medido si el buscador se
    cerraba por ella o solo. Si la tarjeta no queda con AQUACHILE o el buscador sigue abierto, MAERSK corta ahí y su
    HTML lo mide (pregunta 2).
- **Los feriados de Chile** no son días hábiles para el retiro, con la librería holidays. **En esta máquina no está
  instalada, y los `.bat` no la instalan:** sin ella, avisa y sigue de lunes a viernes (pregunta 1).
- **REVISAR, solo si la nave no está.** El formulario que no abre y el que queda incompleto (con lo que el portal pide)
  quedan NO ENVIADA. La rama de la búsqueda de salidas que no termina también dice NO ENVIADA, pero no se alcanza, y
  nunca se alcanzó: `_mk_desenlace_sailing` no devuelve «indefinido». A los 45 s sigue a buscar la nave y, si no la
  encuentra, la reserva queda REVISAR, como nave que no está. En los 21 `log.txt` de `logs/` no pasó nunca (pregunta 4).
- **Sin la tecla Escape** después del Shipper, y **sin el respaldo que pulsaba `<html>`**: «Review booking» es el único
  botón con ese texto a la vista, y si no está o no acepta el clic, NO ENVIADA con el motivo exacto.
- **La revisión de código** encontró 4 hallazgos medios y 8 bajos, sin críticos ni altos. El más serio: la red no veía
  el regreso de lo que quité si volvía envuelto en un `try`. Quedaron corregidos en el commit 6, salvo tres: instalar la
  librería (tu pregunta 1), y `CLAUDE.md` y el mensaje de `793cbf0` sobre el teclado, que se corrigen en el commit de
  este informe.
- **La revisión de este informe** encontró 1 hallazgo alto (la búsqueda de salidas, arriba), 6 medios y 10 bajos.
  Quedaron corregidos aquí, y tres comentarios del código y de las pruebas, en el commit de este informe.
- **Nada de esto se probó en el portal.** `test_candado` no cambia.

## Veredicto del PASO 0, por parte del encargo

| Parte | Veredicto | Qué quedó |
|---|---|---|
| El Shipper con dos clics (opción b) | **CICLO** | `bae8c44` y `e51a786` |
| FRENA SI: el buscador del Shipper no se puede identificar sin ambigüedad con el HTML guardado | **NOTA:** no se cumple: es uno solo, con su ventana titulada «Shipper», y sus resultados se ven sin buscar | El programa lo exige al elegir: si no, corta |
| FRENA SI: elegir a AQUACHILE exige un clic distinto de esos dos | **NOTA** en lo medido: el buscador no tiene botón de confirmar. Lo demás lo mide la corrida: si el clic en el resultado lo elige y si el buscador se cierra solo | Si no queda elegido o no se cierra, corta sin otro clic (pregunta 2) |
| Los feriados de Chile (librería holidays) | **CICLO** | `cbda5be` y `e51a786` |
| Los REVISAR de MAERSK antes del botón final, NO ENVIADA | **CICLO** para el formulario que no abre y el que queda incompleto. Para la búsqueda de salidas que no termina, **DESCARTE:** su REVISAR no se alcanzaba; y **PREGUNTA:** si a los 45 s corta | `f4728e3` y `e51a786`; pregunta 4 |
| Se quita la tecla Escape después del Shipper | **CICLO** | `793cbf0`; en `e51a786`, la página falsa del Shipper anota cualquier tecla |
| Se elimina el respaldo de «Review booking» que pulsa `<html>` | **CICLO** | `a189084` y `e51a786` |
| `test_candado` no cambia | **NOTA:** se cumple | Sin cambios |

## Lo medido

**El HTML de «Additional details» del 27-09** (`shipper_forma.py`, `shipper_detalle.py`), guardado después de los clics
a ciegas de antes: el buscador está cerrado y la tarjeta del Shipper, llena.
- **Las tarjetas de partes:** 10 a la vista, cada una con su `title`. De `id`, las 2 llenas traen cada una el suyo, y
  las 8 vacías comparten uno mismo: 3 distintos en 10 (`partes_estructura.py`). La del Shipper, `title="Shipper"` e
  `id="shipper"`, trae a AQUACHILE. Las 8 vacías tienen un solo `mc-button` «Add» en su raíz shadow (`header` de su
  `article#party-card`, `data-cy="addButton"`). El `button` interno de ese «Add» lleva como `aria-label` el nombre del
  ícono: por su nombre accesible no se encuentra (`mc-button[label='Add']` da 0), y por su texto da 8, uno por tarjeta.
- **El buscador de partes:** uno solo, `mc-c-party-finder`, en la página. Su ventana (`mc-modal`) está en su raíz
  shadow, cerrada.
  - Su encabezado (`slot="heading"`) dice «Shipper».
  - Tiene dos pestañas, «Previously used» (activa, `data-cy="favourite-tab"`) y «Search».
  - Sus 3 resultados están en `mc-c-party-finder-search-results`, dentro de `div#favourite-parties`: cada uno es un
    `label` con su `mc-c-party-card` (`data-cy="party-card--search-result"`), al lado de su `input type="radio"` y sin
    `for`. Uno trae a AQUACHILE.
  - Sus botones: «Close», los de las dos pestañas y «Cancel» (`slot="secondaryAction"`). No tiene botón de confirmar.
- **«Review booking»:** el localizador de `62ab849` calza con 2 elementos, los dos a la vista: el `mc-button` con
  `label="Review booking"` y su botón interno, el mismo control; ningún paso de la barra. El de ahora, solo `mc-button`,
  calza con 1 (lo midió la revisión del informe).

**El JavaScript nuevo sobre ese HTML** (`shipper_js_real.py`: las constantes se sacan por AST, sin importar el programa,
de una copia de `bae8c44` con el cambio 6 sin commitear; su JavaScript del Shipper es el de `e51a786`, `js_igual.py`):
- como se guardó: la tarjeta «Shipper» trae a AQUACHILE como palabra entera, no tiene «Add», y el buscador no muestra
  resultados ni título;
- con el `dialog` del buscador abierto a mano: 3 resultados, 1 con AQUACHILE, y el título «Shipper»; el segundo clic
  iría a ese `label`;
- con la tarjeta «Consignee» (vacía) en lugar del Shipper: un solo «Add», y el primer clic iría a ese `mc-button`.

**El código en `62ab849`:**
- los REVISAR de MAERSK antes de la guarda son 4 en el texto: el formulario que no abre, el que queda incompleto, la
  búsqueda de salidas que no termina y la nave que no está (`_mk_sin_nave`). Se alcanzan 3: el de la búsqueda no, porque
  `_mk_desenlace_sailing` solo devuelve «sin-zarpes» o «con-zarpes», y a los 45 s anota «procedo a buscar naves» y
  devuelve «con-zarpes»; así desde el primer commit, `14aa9ef`. El de la guarda tampoco se alcanza: sin nave, la función
  ya volvió;
- `test_candado` fotografía en `reservar_maersk`, antes de la guarda, los textos «Continue to book» y «MAERSK: no se
  abrió el formulario /book/»;
- en el cuerpo de `reservar_maersk`, el único `page.keyboard` era la tecla Escape. Además escribe con `type()`, una
  tecla por carácter, el commodity; y lo que llama escribe con `type()` el puerto (`_mk_ciudad`), el contenedor
  (`_mk_contenedor`) y la fecha de zarpe (`_mk_fecha`), que además cierra su selector con Escape;
- el respaldo de «Review booking» recorría la página desde `document` y pulsaba el primer elemento con caja cuyo
  `textContent` traía «Review booking»: `<html>`, cuyo texto es el de toda la página.

**Lo que midió la revisión de código, y medí de nuevo** (`nombre_parte.py`, `foto_textcontent.py`):
- el nombre de cada parte va en su elemento `party__info`: uno en cada una de las 2 tarjetas llenas y de los 3
  resultados, y AQUACHILE aparece solo ahí, nunca en la dirección; las tarjetas vacías no lo tienen. Dentro de cada
  `party__info` va también el código de la parte (`party__code`, en los 5), y ninguno trae letras
  (`partes_estructura.py`, por la revisión del informe);
- la forma «el primero cuyo `textContent` calza» (la del respaldo que pulsaba `<html>`) aparece en 3 lugares antes de
  la guarda: dos en COSCO, entre las sugerencias de la ciudad, y el respaldo de «Continue» de MAERSK.

**La librería holidays:** no está instalada en esta máquina, y los `.bat` instalan solo `playwright` y `openpyxl`.

**Los `log.txt` de `logs/`** (`salidas_45s.py`, por la revisión del informe): de 21, 9 traen búsquedas de salidas de
MAERSK, y las 13 terminaron con sus botones «Book» a la vista; ninguna a los 45 s, ninguna por «no hay zarpes» y ninguna
por sus tarifas.

## Cómo quedó cada punto

**1. «Review booking»** (`_mk_pulsar_revision`, `MK_REVISION`): el único `mc-button` a la vista con ese texto, buscado
hasta 15 veces, una por segundo, y pulsado con Playwright, sin clics por JavaScript.
- Si no hay uno solo: «Review booking de MAERSK: el portal pide: …. No encontré un solo botón «Review booking» a la
  vista, por su texto, en 15 intentos (había N), así que no pulsé nada», NO ENVIADA con `mk_f<fila>_sin_objetivo`.
- Si está, pero no acepta el clic: «MAERSK: el botón «Review booking» estaba a la vista, pero no aceptó el clic (…); no
  pulsé nada más…», con `mk_f<fila>_revision`.
- Si un clic falló, pero la revisión ya apareció (pudo haber salido), sigue.
- Hasta su revisión tomaba el primero entre botones y enlaces, visible o no, y decía «no encontré» también cuando no
  aceptaba el clic.

**2. Sin la tecla Escape** después del Shipper: el cuerpo de `reservar_maersk` ya no pulsa teclas con `page.keyboard`.
Sigue escribiendo con `type()`: el commodity en su cuerpo, y el puerto, el contenedor y la fecha de zarpe en lo que
llama; la fecha de zarpe (`_mk_fecha`) además cierra su selector con Escape, como antes. La prueba mira solo
`page.keyboard` en el cuerpo, y la página falsa del Shipper anota cualquier tecla.

**3. REVISAR, solo si la nave no está.** Pasan a NO ENVIADA, con «no pulsé nada más y la reserva no se envió»:
- el formulario que no abre: «MAERSK: no se abrió el formulario /book/» (el texto queda en su propio literal, porque
  `test_candado` lo fotografía);
- el formulario incompleto: «MAERSK: formulario incompleto, y el portal pide: …» (`_mk_formulario_incompleto`, con
  `_mk_lo_que_pide`), o «…, y no vi qué pide el portal», con la evidencia de esa pantalla, `mk_f<fila>_booking`.

El formulario que no abre deja su captura, como antes (`mk_f<fila>_0_sinform`). La rama de la búsqueda de salidas que no
termina también pasó a NO ENVIADA («MAERSK: el portal no terminó de buscar zarpes»), pero no se alcanza: a los 45 s,
`_mk_desenlace_sailing` sigue, `_mk_elegir_nave` busca la nave ampliando la búsqueda, y si no aparece, la reserva queda
REVISAR por `_mk_sin_nave`. Que corte a los 45 s lo decides tú (pregunta 4). Una prueba vigila que, en todo lo que corre
antes de la guarda, el único REVISAR sea el de `_mk_sin_nave`; compara el texto de cada rama, no si se alcanza.

**4. Los feriados** (`_feriados_de_chile`, `_mk_dia_habil`): un día hábil es de lunes a viernes y no es feriado de
Chile, según `holidays.country_holidays("CL")`, de este año y del siguiente, copiados dentro del `try`: la librería
calcula cada año recién al consultarlo, y un fallo ahí escapaba como ERROR.
- Vale para el primer día hábil después de hoy y para el siguiente día hábil habilitado del calendario.
- El log dice qué feriados saltó: «Fecha de retiro: el primer día hábil después de hoy es el 13-10-2026 (martes); el
  12-10-2026 (…) es feriado en Chile.».
- Si la librería no está o falla: «⚠ No pude usar los feriados de Chile de la librería holidays (…): la fecha de retiro
  de MAERSK sigue de lunes a viernes, sin feriados. Se instala con «python -m pip install --user holidays».», una vez
  por corrida.

**5. El Shipper** (`_mk_shipper`, `_mk_elegir_shipper`, `_JS_MK_SHIPPER`, `_JS_MK_SHIPPER_PULSAR`):
- Si la única tarjeta «Shipper» a la vista trae a AQUACHILE como palabra entera, no pulsa nada, como antes.
- Si no lo trae, pulsa su único «Add» a la vista, por su texto. Sin uno solo (la tarjeta llena con otro, por ejemplo),
  corta antes de pulsar: «…no encontré a AQUACHILE en la tarjeta «Shipper», ni un solo «Add» a la vista en ella para
  elegirlo…».
- Espera hasta 10 s (`MK_ESPERA_BUSCADOR`, hipótesis) a que el buscador muestre un resultado con AQUACHILE y su lista se
  quede quieta en dos lecturas seguidas (`_mk_resultados_quietos`), porque los resultados pueden llegar de a poco. Si en
  10 s no se queda quieta, decide con la última lectura. Deja `mk_f<fila>_buscador`: el único HTML que puede medir el
  buscador abierto.
- En el buscador titulado «Shipper», pulsa el único resultado a la vista con AQUACHILE: el `label` que lo envuelve. No
  está medido si ese clic lo elige: el `label` no tiene `for`, y la casilla de opción está a su lado, fuera de él.
- Comprueba, hasta 5 s, que la tarjeta lo muestre y que el buscador se haya cerrado: ni sus resultados ni su encabezado
  a la vista, en cualquier pestaña.
- Cada clic va sobre lo que `_JS_MK_SHIPPER_PULSAR` vuelve a leer justo antes.
- Si algo no se cumple, NO ENVIADA sin otro clic, con `mk_f<fila>_shipper` y el motivo: el buscador sin resultados, sin
  el título, sin un solo resultado con AQUACHILE, la tarjeta que no lo muestra, el buscador que sigue abierto («cerrarlo
  es un clic que no está permitido»), o un clic que falla. Todos terminan en «no pulsé nada más y la reserva no se
  envió», nunca en «no pulsé nada». Los que vienen después de un clic dicen cuál («pulsé el «Add»…», «pulsé el
  resultado…»); los otros nombran lo que falló: la relectura justo antes de un clic («…ya no era uno solo a la vista»),
  el clic que falla («falló el clic en…») y el buscador que siguió abierto.
- AQUACHILE se busca como palabra entera en el `party__info` de cada parte, que trae el nombre y, adentro, el código
  (`party__code`; en el HTML del 27-09, sin letras); la dirección no cuenta. El texto se lee nodo por nodo, con las
  raíces shadow de adentro (`mkTextoHondo`).

## Cómo probarlo

Con **`Iniciar AQUASHIELD.bat`**; nunca con `Iniciar AQUASHIELD_EMISION.bat`. Antes, revisa que `config.json` no traiga
`"emitir_reservas": true` en «opciones» y que no esté definida la variable `AQUASHIELD_EMITIR` (la abren 1, true, si o
yes): con cualquiera de las tres llaves, se emite. Si quieres los feriados, instala antes la librería (pregunta 1).

En el `log.txt` de una fila de MAERSK, en «Additional details»:
1. «Fecha de retiro: el primer día hábil después de hoy es el …», con los feriados que saltó. Sin la librería, antes de
   esa línea sale el aviso «⚠ No pude usar los feriados de Chile…», una vez por corrida;
2. «haulage reference completada: '…'»;
3. el Shipper, lo más probable: «Shipper: pulsé el «Add» de la tarjeta «Shipper»», la evidencia `mk_f<fila>_buscador`,
   «Shipper: pulsé el resultado con AQUACHILE del buscador» y «Shipper: elegí a AQUACHILE en el buscador, y la tarjeta
   «Shipper» lo muestra»; o, si ya venía, «Shipper: AQUACHILE ya viene en la tarjeta «Shipper»; no pulsé nada»;
4. «pulsado 'Review booking'» y la revisión.

Si el Shipper corta, el motivo dice dónde:
- el buscador no se cierra solo: «✗ NO ENVIADA · MAERSK: la tarjeta «Shipper» ya muestra a AQUACHILE, pero el buscador
  siguió abierto…», con `mk_f<fila>_shipper`;
- el clic en el resultado no lo elige: «✗ NO ENVIADA · MAERSK: pulsé el resultado con AQUACHILE del buscador, pero la
  tarjeta «Shipper» no lo muestra…», con `mk_f<fila>_shipper`;
- el «Add» no está como se infirió: «✗ NO ENVIADA · Shipper de MAERSK: no encontré a AQUACHILE en la tarjeta «Shipper»,
  ni un solo «Add» a la vista en ella para elegirlo (había N), así que no pulsé nada…», con `mk_f<fila>_sin_objetivo`.

Dime qué corrida fue y leo su evidencia en `logs/`.

## Qué decides tú

1. **La librería holidays.** No viene con Python, no la instalan los `.bat` y en esta máquina no está: sin ella, la
   fecha de retiro sigue de lunes a viernes y lo avisa. Puedes instalarla con `python -m pip install --user holidays`, o
   te sumo una línea a cada `.bat`, como las de `playwright` y `openpyxl`, para que se instale sola si falta. Te
   recomiendo lo segundo.
2. **Si el buscador del Shipper no se cierra solo, o si el clic no elige el resultado.** Antes, después del Shipper, se
   pulsaba la tecla Escape, que se quitó; no está medido si el buscador se cerraba por ella o solo al elegir. Si en la
   prueba queda abierto, la reserva corta ahí, con su HTML: ¿autorizas entonces su «Close» (un tercer clic, identificado
   por su texto), o prefieres que corte? Y si el clic en el resultado no lo elige, porque la casilla de opción está al
   lado del `label` y no adentro, ¿pulso esa casilla en su lugar, o prefieres que corte?
3. **El respaldo de «Continue» en «Recommended services».** Si no encuentra el botón por su texto, pulsa por JavaScript
   el primer elemento a la vista cuyo texto entero es «Continue». No pulsa `<html>`, porque pide el texto entero, pero
   es la misma forma que el de «Review booking». Desde este encargo la foto de clics lo ve, y quedó permitido hasta que
   decidas. ¿Lo quito igual?
4. **La búsqueda de salidas que no termina.** A los 45 s, MAERSK sigue a buscar la nave como si hubiera salidas, y así
   fue siempre; si no la encuentra, la reserva queda REVISAR, como nave que no está. En los `log.txt` guardados no pasó
   nunca: las 13 búsquedas terminaron con sus botones «Book» a la vista. ¿Quieres que a los 45 s corte, NO ENVIADA con
   «el portal no terminó de buscar zarpes»? La rama ya está escrita; falta que la espera la devuelva.

## Re-medir (pieza 1)

Las sondas son de solo lectura y no se versionan, porque leen datos reales. Quedaron en el scratchpad de esta sesión
(`$env:TEMP\claude\<proyecto>\<sesión>\scratchpad\e38`), que puede limpiarse; sin ellas, estos números no se re-miden.
Las que miden abortan si no pasa su control positivo. Las que abren el HTML en un Chromium lo copian, sin sus scripts, a
una carpeta nueva de `%TEMP%`, y desde el cierre la borran al terminar, también si abortan.
- **`shipper_forma.py`:** sobre el HTML del 27-09, cada `mc-c-party-card` (su `title`, su `id`, si se ve, si trae a
  AQUACHILE y sus botones), el buscador (su ventana, sus pestañas, un resultado) y los localizadores que usaría el
  programa, con su cuenta y cuántos se ven. Lo que no es de la interfaz, tapado. Su control: una tarjeta sintética con
  su «Add» y un buscador con un resultado en raíces shadow declarativas, para los localizadores y para las funciones en
  JavaScript.
- **`shipper_detalle.py`:** lo que toma el localizador de «Review booking», el encabezado del buscador, dónde están sus
  resultados y sus casillas de opción, y el `data-cy` de los «Add». Su control: una página sintética con un paso de la
  barra y un botón «Review booking», y un buscador con su encabezado.
- **`shipper_js_real.py <copia>`:** `_JS_MK_SHIPPER` y `_JS_MK_SHIPPER_PULSAR`, sacados por AST de la copia, sobre el
  HTML del 27-09: como se guardó, con el `dialog` del buscador abierto a mano y con la tarjeta «Consignee». Su control:
  una página sintética con una tarjeta vacía con «Add» y un buscador abierto. Se corrió sobre `copia_105454`, la de
  `bae8c44` con el cambio 6 sin commitear.
- **`js_igual.py <rev>`:** si el JavaScript del Shipper de cada copia del scratchpad es el de un commit, por AST.
  `copia_105454` da el de `e51a786`. Su control: el commit tiene que traer las constantes.
- **`nombre_parte.py`:** en cada `mc-c-party-card` del HTML del 27-09, cuántos `party__info` tiene y si AQUACHILE está
  en ellos o fuera. Su control: una tarjeta sintética con el nombre en su `party__info` y la empresa también en la
  dirección. No separa el código de la parte, que va adentro: eso lo mide `partes_estructura.py`.
- **`partes_estructura.py`:** sin navegador (`html.parser`), en el HTML del 27-09: si el código de cada parte
  (`party__code`) va dentro de su `party__info` y si trae letras, y los `id` de las tarjetas con `title`, llenas o
  vacías; y en `logs/`, las carpetas, los `.html`, cuántos no se leen y cuántos traen la pantalla de partes. Solo
  cuentas y la fecha de las carpetas. Sus controles: una página sintética con un código adentro y otro afuera, y el HTML
  conocido tiene que traer la pantalla de partes.
- **`salidas_45s.py`:** en los `log.txt` de `logs/`, cuántas búsquedas de salidas de MAERSK terminaron por cada camino
  de `_mk_desenlace_sailing`, por los textos que escribe el programa. Solo cuentas. Aborta si no encuentra ninguna.
- **`foto_textcontent.py <copia de bae8c44>`:** con el detector de la foto de `tests/test_clics.py`, dónde calza la
  forma «el primero cuyo `textContent` calza»: 3 formas nuevas. Sobre `e51a786` da 0, porque la foto ya la trae. Sus
  controles: la foto de la copia tiene que dar exactamente `PERMITIDOS`, y la forma tiene que calzar con el respaldo de
  `62ab849`.
- **`copia.py [rev]`, `anclas.py <copia>` y `largas_copia.py <copia>`:** una copia del repo (`git archive`, leído con
  `tarfile`), las mutaciones cuya ancla no aparece exactamente una vez y las líneas nuevas de más de 120. Solo cuentan o
  copian.
- **`precenso.sh <copia> <etiqueta> <filtro>…`:** el censo de cada filtro en una copia, antes del gate.
- **`red_por_commit.py <rev>…`:** pruebas, mutaciones y pares de cada commit, con `git show`.
- **Los cambios y los gates:** `aplicar_k1.py` a `aplicar_k5.py` (con `k5_codigo.py` y `k5_pruebas.py`), `aplicar_k6.py`
  (con `k6_codigo.py`, `k6_pruebas.py` y `k6_shipper_pruebas.py`), `aplicar_docs38.py` y `aplicar_comentarios38.py`,
  todos con `comun.py` (cada viejo, exactamente una vez, y escritura en binario, LF); `gate.sh`, `censo.sh` y
  `commit.sh`.

La red versionada, desde `C:\dev\Agendamiento Reservas`: `python tests/correr.py` (la suite, de 4 a 7 min en esta
máquina), `python tests/correr.py --mutaciones --filtro <texto>` (el censo de lo que nombra ese texto: `mk-shipper`,
`mk-feriados`, `TestRetiroMaersk`…) y `python tests/correr.py --mutaciones` (el censo completo).

## NO retroceder (pieza 2)

- **No busques el «Add» por su nombre accesible:** su botón interno lleva como `aria-label` el nombre del ícono. Por su
  texto, dentro de la tarjeta, es uno solo.
- **No identifiques la tarjeta de una parte por su `id`:** en el HTML del 27-09, las 8 vacías comparten uno mismo. El
  `title` está en las 10 y distingue a cada parte.
- **No leas el texto de una tarjeta de parte con `textContent`:** pega el título al nombre («ShipperAQUACHILE…»), y la
  palabra entera deja de calzar. Se lee nodo por nodo.
- **No cortes con `ObjetivoNoEncontrado` después de pulsar algo:** su motivo dice «no pulsé nada». Después del «Add», el
  corte dice qué se pulsó.
- **No esperes el primer resultado del buscador:** pueden llegar de a poco. Se espera el que trae a AQUACHILE, y antes
  de pulsar se vuelve a leer que sea uno solo.
- **No cierres el buscador con otra tecla o clic sin la decisión de Marcelo** (pregunta 2).
- **No vuelvas a pulsar por JavaScript «el primer elemento cuyo texto trae…»:** en «Review booking» era `<html>`.
- **No hagas que una prueba dependa de lo que la máquina tenga instalado:** las del retiro usan una librería holidays
  falsa.
- **No hagas que una página falsa avise de lo inesperado solo levantando una excepción:** el programa se la traga en un
  `try`. Que lo anote, y que la prueba exija la lista vacía.
- **No des por cerrado el buscador solo porque no se ven sus resultados:** en otra pestaña sigue abierto, con su
  encabezado a la vista.
- **No busques a la empresa en todo el texto de una parte:** su dirección podría traerla. Va en su `party__info`, que
  trae también el código.
- **No cambies el texto «MAERSK: no se abrió el formulario /book/» sin su literal propio:** `test_candado` lo
  fotografía.

## Universo y cobertura (pieza 3)

- **HTML:** 1 página de «Additional details», la del 27-09: 13 `mc-c-party-card` (10 partes a la vista, 8 vacías con su
  «Add», y los 3 resultados del buscador, ocultos); 1 buscador; 2 elementos con «Review booking». No hay otra página de
  esa pantalla en `logs/`: de 261 `.html` en 21 carpetas (la última, del 27-09), 0 ilegibles, solo esa trae tarjetas de
  partes y su buscador (`partes_estructura.py`).
- **`log.txt`:** los 21 de `logs/`, 0 ilegibles; 9 con búsquedas de salidas de MAERSK, 13 búsquedas (`salidas_45s.py`).
- **Código:** `reservar_maersk` y lo que llama antes de su guarda (el universo de la foto de clics), para los REVISAR;
  y, para el teclado, el cuerpo de `reservar_maersk` y las funciones `_mk_*` (`page.keyboard` y `type()`).
- **No medido:**
  - la tarjeta «Shipper» vacía, con su «Add»: se infiere de las otras 8;
  - el buscador abierto de verdad: si su título «Shipper» es el de la parte o su valor por defecto, y si se cierra solo
    al elegir;
  - si el clic en el `label` de un resultado lo elige: el `label` no tiene `for`, y la casilla de opción está a su lado;
  - la librería holidays de verdad: las pruebas usan una falsa;
  - las pantallas de los dos REVISAR que pasaron a NO ENVIADA y se alcanzan: no hay HTML de ninguna; la del formulario
    incompleto lo dejará (`mk_f<fila>_booking`).

## Defectos de instrumento cazados (pieza 4)

1. **La primera sonda del Shipper no entraba en la raíz shadow del propio elemento:** daba «sin AQUACHILE» en el Booked
   By y el Shipper, que lo traen, y ningún botón en ninguna tarjeta. Su control miraba solo los localizadores de
   Playwright, no sus funciones en JavaScript. Lo cazó el caso conocido (las dos tarjetas llenas), y el control ahora
   cubre las dos cosas.
2. **La herramienta Bash convirtió `\\` en `\`** en un parche del cambio 1: la aserción de ancla única lo frenó antes de
   escribir, y lo rehíce con Edit (el mismo defecto del encargo 37).
3. **La primera versión del cambio 4 hacía depender de la máquina a las pruebas del retiro:** sin la librería instalada,
   el aviso aparecía en su log y cayeron 4. Ahora usan una librería falsa.
4. **El cambio 4 dejó sin ancla 4 mutaciones de los encargos 36 y 37** (las del día hábil). Las cazó `anclas.py` en la
   copia, antes del gate, y se rehicieron sobre `_mk_dia_habil`.
5. **Una mutación de feriados no mordió en el precenso** (`mk-feriados-saltados-tambien-sabados`): la prueba no tenía un
   feriado en fin de semana. Era un caso incompleto: se sumó el sábado 19-09.
6. **Dos defectos de diseño del cambio 5, cazados antes de su gate:** el texto con `textContent` pegaba el título al
   nombre, y la espera del buscador se detenía con el primer resultado. Los dos se corrigieron con su prueba y su
   mutación.
7. **La red no veía el regreso de lo que quité si volvía envuelto en un `try`:** las páginas falsas avisaban de lo
   inesperado levantando una excepción, y el programa se la tragaba. La revisión lo reprodujo con el respaldo de
   `<html>`, la tecla Escape y un clic en «Close». Ahora las páginas falsas anotan lo inesperado, cada prueba exige esa
   lista vacía, y las mutaciones traen su `try`.
8. **Mi espera del buscador terminaba con el primer resultado con AQUACHILE, aunque la lista siguiera llegando,** así
   que «un solo resultado» podía no serlo; y dos motivos decían más de lo que el programa sabe: «elegí» cuando solo
   pulsó, y «no encontré» cuando «Review booking» estaba a la vista y no aceptaba el clic. Los cazó la revisión de
   código, y quedaron corregidos en `e51a786`.
9. **El mensaje de `793cbf0` dice «reservar_maersk ya no usa el teclado», y este informe lo repetía para su cuerpo:** el
   cuerpo ya no pulsa teclas con `page.keyboard`, pero escribe con `type()` el commodity, y lo que llama escribe el
   puerto, el contenedor y la fecha de zarpe, que además cierra su selector con Escape. Lo cazaron las dos revisiones.
   La prueba mira solo `page.keyboard`: su comentario se corrige en el commit de este informe, y el mensaje, aquí.
10. **«Antes lo cerraba la tecla Escape» se afirmó sin medir,** en el mensaje de `bae8c44`, en un comentario del código
    y en este informe: el HTML del 27-09 es de después del clic y de la tecla, así que no se sabe si el buscador se
    cerraba por ella o solo al elegir. Lo cazó la revisión del informe; el comentario se corrige en el commit de este
    informe, y el mensaje, aquí.
11. **Pasé a NO ENVIADA una rama que no se alcanza,** la de la búsqueda de salidas que no termina, y el informe la
    contaba como un corte nuevo. Mi prueba compara el texto de la rama por AST y no ve si se llega a ella. Lo cazó la
    revisión del informe (pregunta 4).
12. **Di por medidas dos cosas del HTML del 27-09 que no lo estaban:** que cada tarjeta trae su propio `id` (las 8
    vacías comparten uno) y que el código de la parte queda fuera de su `party__info` (va adentro). Mi sonda del nombre
    no separaba el código, y la de las tarjetas no contaba los `id` repetidos. Lo cazó la revisión del informe, y
    `partes_estructura.py` lo midió. El programa no cambia: usa el `title`, y en ese HTML el código no trae letras.
13. **Las sondas con Chromium copiaban el HTML a una carpeta nueva de `%TEMP%` y no la borraban:** quedaban 11 (7 de
    este encargo, 1 del 37 y 3 del 36), 9 con la copia del HTML real y 2 con una página de pocos cientos de bytes. Lo
    cazó la revisión del informe. Se borraron por su nombre, y ahora cada sonda borra la suya al terminar, también si
    aborta.
14. **Un cero sin su contador y un «cada» que no era cada uno:** «no hay otra página de esa pantalla en `logs/`», sin
    decir cuántas se miraron (ahora, 261 `.html`, 0 ilegibles); y «un precenso antes de cada gate», cuando el gate 1 no
    lo tuvo (`precenso.sh` nació después). Los cazó la revisión del informe.

## Premisas del encargo contrastadas (pieza 5)

- **«La estructura del buscador está en el HTML del 27-09»:** confirmada, con matices. Ese HTML es de después de los
  clics de antes: el buscador está cerrado y la tarjeta del Shipper, llena. El «Add» de la tarjeta del Shipper vacía se
  infiere de las otras 8, y el título «Shipper» podría ser el valor por defecto del buscador.
- **«La tarjeta, identificada por su title o id»:** confirmada para el `title`, que está en las 10 tarjetas y distingue
  a cada parte; refutada para el `id`: `id="shipper"` solo se midió en la tarjeta llena, y las 8 vacías comparten uno
  mismo. El programa usa el `title`, como ya lo hacía.
- **«El único resultado que calce con AQUACHILE por palabra entera»:** en el HTML guardado hay 3, y 1 lo trae.
- **«Los REVISAR de MAERSK antes del botón final»:** refutada en parte. En el texto eran 3, más el de la nave que no
  está; pero el de la búsqueda de salidas que no termina no se alcanza, así que los que pasaron a NO ENVIADA de verdad
  son 2 (pregunta 4). El de la guarda tampoco se alcanza, y `test_candado` lo fotografía: quedó.
- **«La librería holidays (instalable con pip)»:** sí, pero no está en esta máquina y los `.bat` no la instalan
  (pregunta 1).
- **«El respaldo de «Review booking» que pulsa `<html>`»:** confirmado leyendo el código: `<html>` era el primero con
  caja cuyo texto lo traía.
- **FRENA SI:** ninguno se cumple con lo medido. Quedan sin medir que el clic en el resultado lo elija y que el buscador
  se cierre solo; si no, la reserva corta sin otro clic (pregunta 2).

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| Si el buscador del Shipper no se cierra solo al elegir, la reserva queda NO ENVIADA ahí | Cerrarlo sería un tercer clic, no permitido | …la prueba lo muestra y decides (pregunta 2) |
| Si el clic en el `label` del resultado no elige la parte, la reserva queda NO ENVIADA ahí | El `label` no tiene `for`, y la casilla de opción está a su lado; pulsarla sería otro clic | …la prueba lo muestra y decides (pregunta 2) |
| El «Add» de la tarjeta del Shipper vacía se infiere de las otras 8 | Ninguna corrida guardó esa tarjeta vacía | …la prueba deja `mk_f<fila>_buscador` (el «Add» estaba) o, en el Shipper, `mk_f<fila>_sin_objetivo` (no estaba como se infirió) |
| El título «Shipper» del buscador podría ser su valor por defecto | Sin el JavaScript de la página no se distingue | …se abre para otra parte |
| Si AQUACHILE no está en «Previously used», corta | Buscarla serían más clics y escribir | …la cuenta del operador no lo trae |
| La librería holidays de verdad no se probó; no está instalada | Las pruebas usan una falsa | …la instalas (pregunta 1) |
| Solo los feriados nacionales de Chile | `country_holidays("CL")`, sin región | …hace falta un feriado regional |
| `MK_ESPERA_BUSCADOR` (10 s) es una hipótesis; si la lista no se queda quieta en ese tiempo, decide con la última lectura | Sin medir; el clic vuelve a leer, justo antes, que el resultado sea uno solo | …la prueba muestra otra cosa |
| El formulario que no abre deja su captura, no su HTML (`mk_f<fila>_0_sinform`) | Como antes | …hace falta medir esa pantalla |
| La búsqueda de salidas que no termina no corta: a los 45 s sigue a buscar la nave, y si no la encuentra, REVISAR; su rama NO ENVIADA no se alcanza | Así fue siempre (`14aa9ef`), y cortar ahí es tu decisión; en los `log.txt` guardados no pasó nunca | …decides que corte (pregunta 4) |
| El REVISAR de la guarda de MAERSK no se alcanza y quedó | `test_candado` lo fotografía | …se decide tocar la guarda |
| El respaldo en JavaScript de «Continue» en «Recommended services»; la foto ya lo ve, y está permitido | Fuera del encargo | …lo decides (pregunta 3) |
| Las otras navieras mantienen sus REVISAR antes de la guarda | El encargo era de MAERSK | …se decide lo mismo para ellas |
| Si «Review booking» está tapado, la espera puede pasar de 15 s: cada intento espera su clic | Los 15 intentos son por conteo, no por reloj | …tarda demasiado en una corrida |
| La empresa se busca en el `party__info` de cada parte, que trae también su código: si el portal cambia esa clase, MAERSK corta en el Shipper, y si un código trajera la palabra AQUACHILE, contaría | Medida el 27-09 en las 5 tarjetas con nombre: los códigos, sin letras | …el portal la cambia, o un código trae letras |
| `_mk_booking_sin_avanzar` sigue diciendo «no pude leer qué pide» también sin avisos a la vista | Del encargo 37 | …se unifica con «no vi» |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v14**.
- **PASO 0 con sus cuatro valores:** CICLO en las cinco partes (en la de los REVISAR, para el formulario que no abre y
  el incompleto); NOTA para los dos FRENA SI en lo medido (lo demás lo mide la corrida, pregunta 2) y para
  `test_candado`; DESCARTE y PREGUNTA para la búsqueda de salidas que no termina.
- **FRENAR cuando la decisión es de negocio:** la librería en los `.bat`, cerrar el buscador o pulsar la casilla del
  resultado, el respaldo de «Continue» y el corte a los 45 s quedan como preguntas.
- **Control positivo que aborta:** en cada sonda que mide (pieza 1); la primera del Shipper no lo tenía para sus
  funciones en JavaScript, y lo cazó el caso conocido (pieza 4, 1).
- **El negativo tiene que morder:** cada prueba nueva con su mutación; un precenso de las mutaciones nuevas en una copia
  antes de los gates 2 a 6, que cazó 5 casos incompletos (pieza 4, 5, y el Entregable); el censo filtrado en cada
  commit, y el completo en el último.
- **Todo registro es una hipótesis:** el HTML del 27-09 es posterior a los clics de antes; lo inferido (el «Add» de la
  tarjeta vacía, el cierre del buscador, el clic en el `label`) va como tal. También lo que yo di por medido: la
  revisión del informe lo cazó en la rama de la búsqueda, en la tecla Escape, en los `id` y en el código de la parte
  (pieza 4, 10 a 12).
- **Un cero solo vale con su contador:** el de «no hay otra página de esa pantalla en `logs/`» ahora va con el suyo
  (pieza 4, 14).
- **Un gate en cero prueba contención, no correctitud:** la prueba de la rama de la búsqueda compara su texto y pasa,
  aunque la rama no se alcance (pieza 4, 11).
- **Re-medir contra HEAD:** el código se leyó en `62ab849`, y cada cambio se probó sobre una copia de su commit padre.
- **Fuente única:** `_mk_dia_habil` para los dos lados del día hábil; `_MK_ARGS_SHIPPER` para las dos lecturas del
  Shipper; `_JS_TRAE_LA_NAVE` para la palabra entera; `MK_REVISION`.
- **Cada reemplazo, exactamente una vez, y el EOL preservado:** ediciones con anclas únicas; 0 CR en cada commit.
- **El cambio y su guardián, juntos:** cada commit con sus pruebas y sus mutaciones, y las mutaciones viejas que se
  anclaban en lo que cambió, rehechas en el mismo commit.
- **Choques entre reglas:**
  1. **«Solo dos clics nuevos» contra «el buscador puede quedar abierto»:** no se cierra con nada ni se pulsa la casilla
     del resultado; si queda abierto o sin elegir, la reserva corta y su HTML lo mide (pregunta 2).
  2. **«REVISAR solo para la nave que no está» contra «`test_candado` no cambia»:** el REVISAR de la guarda no se
     alcanza y `test_candado` lo fotografía, así que quedó; y el texto del formulario que no abre conserva su literal.
  3. **«Se usan los feriados de la librería» contra «las pruebas no dependen de la máquina»:** las pruebas usan una
     librería falsa, y la de verdad queda sin probar (residual).

Reglas del módulo: nada de `logs/` en el repo; ningún nombre de nave, viaje, puerto, depósito, parte ni operador, ni
número de reserva, en este informe; `test_candado` sin cambios; la sonda de secretos antes de cada commit; los textos en
español con tuteo.

## Entregable (pieza 8)

- **Este `.md`:** no se convirtió en página; se leyó como texto.
- **`CLAUDE.md` al día,** en el commit de este informe: el Shipper con sus dos clics (lo medido, lo inferido y lo que no
  se midió), el nombre por su `party__info`, «Review booking», los feriados y la librería, REVISAR solo sin nave, la
  evidencia nueva, la forma nueva de la foto, las páginas falsas que anotan, y el número de pruebas.
- **Tres comentarios corregidos,** en el mismo commit (`aplicar_comentarios38.py`): dos del código, el de la tecla
  Escape y el del `party__info`, y el de la prueba del teclado.
- **La red, commit por commit:**

| Commit | Pruebas | Mutaciones | Pares |
|---|---|---|---|
| `62ab849` (base) | 457 | 1251 | 1504 |
| `a189084` | 460 | 1260 | 1513 |
| `793cbf0` | 461 | 1261 | 1514 |
| `f4728e3` | 464 | 1267 | 1524 |
| `cbda5be` | 469 | 1277 | 1535 |
| `bae8c44` | 472 | 1306 | 1564 |
| `e51a786` | 477 | 1326 | 1584 |

- **El gate de cada commit:** la suite completa en verde, con 0 cambios en los originales, y los censos filtrados
  (mutaciones / pares), todos en OK. La máquina estuvo lenta: la suite tardó de 4 a 7 min.

| Commit | Suite | Censos filtrados |
|---|---|---|
| `a189084` | 460 | mk-revision 9/9 · TestFotoDeClicsGenericos 33/61 |
| `793cbf0` | 461 | vuelve-el-escape 1/1 |
| `f4728e3` | 464 | vuelve-a-revisar 4/7 · mk-incompleto 3/5 · mk-zarpes-sin-motivo 1/1 |
| `cbda5be` | 469 | TestRetiroMaersk 84/100 |
| `bae8c44` | 472 | mk-shipper 43/43 · maersk-shipper 3/3 · test_solo_ahi 25/56 · TestFotoDeClicsGenericos 33/61 · test_js_lo_que_pide 10/11 · TestRetiroMaersk 84/100 · test_js_casilla_por_su_texto 13/13 |
| `e51a786` | 477 | mk-revision 17/17 · mk-incompleto 4/6 · mk-feriados 12/13 · mk-shipper 51/51 · mk-foto-ve 1/1 · maersk-shipper 3/3 · test_solo_ahi 25/56 · TestFotoDeClicsGenericos 34/62 · TestRetiroMaersk 86/102 |

- **Antes de los gates 2 a 6** (el 1 no lo tuvo: `precenso.sh` nació después), las mutaciones nuevas se censaron en una
  copia. Ahí se cazaron 5 que no mordían: una de feriados (pieza 4, 5) y cuatro del commit 6 (la raíz shadow propia y
  las de adentro, el texto pegado y el título en la lista quieta). Eran casos incompletos, y las pruebas sumaron esos
  casos.
- **El censo completo sobre `e51a786`:** 1326 mutaciones y 1584 pares, con las 477 pruebas y 0 sin mutación: todas
  muerden, ninguna con tiempo agotado; 2895 originales fotografiados, 0 cambios; RESULTADO: OK. Duró 67 min (de 11:56 a
  13:04), sin suspensión: 0 eventos Kernel-Power, y la misma consulta encuentra los 5 del reinicio de las 11:37. El
  primero, lanzado a las 11:20, lo cortó ese reinicio del equipo (Kernel-Power 109) cuando solo había pasado su control;
  se volvió a correr desde cero, y la carpeta que dejó en `%TEMP%` se borró.
- **Cada commit:** la sonda de secretos dio 0 sobre el árbol y 0 sobre lo agregado, y 0 CR en los archivos commiteados.
- **El commit de este informe** (documentación y tres comentarios, sin cambios de código): la suite, 477 pruebas, en
  verde en 250 s, con 0 cambios en los 2896 originales (uno más que en el censo: este informe); los censos filtrados
  vuelve-el-escape 1/1 y mk-shipper 51/51, todos muerden; las 1326 anclas calzan una vez y ninguna línea nueva pasa de
  120 (`anclas.py` y `largas_copia.py`, en una copia).
- **La revisión de código:** un agente, en solo lectura, con páginas sintéticas en un Chromium sin red y con el HTML
  real del 27-09.
  - Resultado: 0 críticos, 0 altos, 4 medios y 8 bajos, casi todos reproducidos. Confirmó que después de la guarda no
    cambió nada, que `test_candado` sigue igual y en verde, y la API de holidays según su código fuente
    (`country_holidays("CL")` en español, con los años que se piden).
  - **Los medios:**
    - «Review booking» tapado: el motivo decía «no encontré… en 15 s» y tardaba unos 76 s;
    - el buscador se daba por cerrado sin mirar su encabezado;
    - la red no veía el regreso de lo quitado envuelto en un `try` (pieza 4, 7);
    - la librería no se instala (pregunta 1).
  - **Los bajos:**
    - los feriados que fallaban al calcular el año escapaban como ERROR;
    - «Review booking» tomaba el primero, visible o no;
    - «un solo resultado» se decidía con la lista a medias;
    - la empresa se buscaba también en la dirección;
    - un motivo decía «elegí» cuando solo pulsó;
    - el formulario incompleto decía «no pude leer» sin haber fallado, y no dejaba HTML;
    - el mensaje de `793cbf0` sobre el teclado (pieza 4, 9);
    - `CLAUDE.md` desfasado.
  - Todo quedó en `e51a786`, salvo la librería (pregunta 1), y `CLAUDE.md` y el mensaje de `793cbf0`, que se corrigen en
    el commit de este informe.
  - **Fuera del alcance,** vio el respaldo de «Continue» (pregunta 3).
- **La revisión adversarial de este informe:** un agente, en solo lectura, con sondas propias que abortan si no pasa su
  control, sobre el árbol, los commits y el HTML real del 27-09 (borró sus copias al terminar).
  - Resultado: 1 alto, 6 medios y 10 bajos, todos verificados.
  - **El alto:** la búsqueda de salidas que no termina nunca llega a su corte (Resumen y pregunta 4).
  - **Los medios:** «antes lo cerraba la tecla Escape», sin medir; el teclado en `reservar_maersk`, que escribe con
    `type()`; el código de la parte, dentro de su `party__info`; los `id` repetidos de las tarjetas vacías; una fila del
    Residual que contradecía el código; y el camino sin «Add», que faltaba en el Residual y en «Cómo probarlo».
  - **Los bajos:** la NOTA del segundo FRENA SI, que no estaba medido entero (el clic en el `label`); el precenso, que
    no hubo antes del gate 1; el «salvo uno» del Resumen; las dos líneas del paso 1 de «Cómo probarlo»; «sin JavaScript»
    y el localizador de «Review booking»; la pieza 1 (el contador de `logs/`, `comun.py`, la copia de
    `foto_textcontent.py` y la de `shipper_js_real.py`); los motivos del Shipper y la lista que no se queda quieta; la
    pieza 4, 8; las copias del HTML real en `%TEMP%`; y `Pantalla` por `SoloLee` en el borrador de `CLAUDE.md`.
  - Verifiqué cada uno antes de corregirlo: los `id`, el código de la parte y `logs/` los volví a medir con
    `partes_estructura.py`; la búsqueda de salidas, con `salidas_45s.py` y el código de `14aa9ef`; y el JavaScript
    medido, con `js_igual.py`. Todo quedó corregido en este informe; los comentarios del código (Escape y `party__info`)
    y el de la prueba del teclado, en el commit de este informe.
  - Confirmó lo demás: la red por commit, los gates, 0 CR, lo medido en el HTML, la foto de clics, `test_candado` sin
    cambios y nada cambiado después de la guarda. No pudo verificar las cifras de la revisión de código, la sonda de
    secretos (lee `config.json`), los puntos 1 a 3 de la pieza 4 ni que el árbol estuviera limpio en `62ab849`.
