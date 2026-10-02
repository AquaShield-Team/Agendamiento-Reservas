# CICLO · Los cuatro puntos de MAERSK antes de la prueba: holidays en los lanzadores, un solo «Continue», el «Close» del buscador y la búsqueda de salidas sin su rama muerta; la casilla del resultado, en FRENO

**Módulo:** Agendamiento Reservas · **Encargo 39** · **Fecha:** 2026-09-29 · **Método:** skill `metodo-ciclo` v14 ·
**Commits** (locales; el repo no tiene remoto, así que no hay push que entregar):
- `a44ba13`: los lanzadores instalan holidays si falta, sin frenar sin red;
- `35f4c53`: la búsqueda de salidas no corta, sin la rama que nunca se alcanzaba;
- `767e27b`: «Continue» de «Recommended services», solo si hay uno a la vista;
- `4b48792`: el «Close» del buscador del Shipper, solo con AQUACHILE en la tarjeta;
- `c9c5402`: lo que encontró la revisión de código;
- y el de este informe, con `CLAUDE.md` al día.

**Base: `C:\dev\Agendamiento Reservas` @ `7a38598` · árbol limpio** (pieza 9). Lo medido sale del HTML de «Additional
details» del 27-09 (`mk_f10_sin_objetivo.html`), de las 6 capturas y los `log.txt` de «Recommended services», y del
código en `7a38598`.

> Datos reales solo en lectura. Las sondas de este encargo leen el HTML y los `log.txt` en su lugar, sin copiarlos ni
> abrir un navegador (`html.parser`), y las capturas con OCR, sin mirarlas. Imprimen etiquetas de interfaz, nombres de
> atributos y cuentas: en este informe no van nombres de naves, viajes, puertos, depósitos, partes, códigos ni números
> de reserva; de las partes, solo si traen a AQUACHILE, la empresa que opera el programa. No se miró ninguna captura.

**Resumen.**
- **La casilla del resultado: FRENO, se cumple tu FRENA SI.** En el HTML del 27-09 los 3 resultados del buscador van
  sueltos en un mismo contenedor, casilla y `label` alternados; la casilla queda fuera del `label`, sin un envoltorio
  por resultado y sin nada que la una a él (el `label` no tiene `for`, ni el `id` de la casilla aparece en su `label` ni
  en su tarjeta). Solo la identifican su posición (va justo antes del `label`) y un calce parcial: su `id` termina con
  las 3 cifras visibles del código de la tarjeta; las dos coinciden 1:1 en los 3 resultados. Lo que activa el freno es
  que no está dentro del resultado. No la pulso: si el clic en el resultado no lo elige, la reserva corta como hoy
  (pregunta 1).
- **holidays en los `.bat`:** los dos la instalan si falta, antes de abrir el panel, con `--timeout 5 --retries 0`. Sin
  red, `pip` se rindió en 6 s ante un índice que no responde; sin esos límites, en 69 s. Con red, al abrir tu prueba del
  29-09 a las 14:58, la instaló (0.105).
- **«Continue» de «Recommended services»:** se pulsa solo si hay exactamente uno a la vista; con cero o más de uno, NO
  ENVIADA con lo que el portal pide. Su HTML no está medido: ninguna corrida guardó esa pantalla, y en sus 6 capturas no
  se ve; el programa lo pulsó por su texto en las 6.
- **El «Close» del buscador:** si después del resultado la tarjeta ya muestra a AQUACHILE y el buscador sigue abierto,
  pulsa su único «Close» (medido: uno solo en la página, en la cabecera de la ventana del buscador) y comprueba que se
  cerró; si no, NO ENVIADA con su HTML.
- **La búsqueda de salidas no corta:** se quitó la rama a NO ENVIADA que nunca se alcanzaba; a los 45 s sigue a buscar
  la nave, y si no aparece, REVISAR, como siempre. Pero esa espera nunca decide: en los 14 desenlaces de `logs/`, la
  búsqueda terminó a los 2 s por un «Book» a la vista. En tu prueba de las 15:03, con «no sailings for your search» en
  la página y sin ningún «Book» de una salida, lo más probable es que ese «Book» fuera el enlace del encabezado o el
  pie: la fila quedó REVISAR, no SIN-CUPO (pregunta 3).
- **La revisión de código** encontró 2 hallazgos medios y 7 bajos, sin críticos ni altos, y confirmó el FRENO de la
  casilla. El commit 5 (`c9c5402`) suma las pruebas del «Close» con 0 o 2 tarjetas «Shipper», corrige el motivo de su
  relectura y deja la evidencia `mk_f<fila>_cerrar` antes de pulsarlo; `CLAUDE.md` va en el commit de este informe, y lo
  demás queda en el residual.
- **Nada de esto se probó en el portal.** `test_candado` no cambia.

## Veredicto del PASO 0, por parte del encargo

| Parte | Veredicto | Qué quedó |
|---|---|---|
| holidays en los `.bat`, sin frenar sin red | **CICLO** | `a44ba13` |
| Shipper: la casilla del mismo resultado de AQUACHILE, si el clic en el resultado no lo eligió | **PREGUNTA (FRENO):** se cumple tu FRENA SI: la casilla no está dentro del resultado y solo la identifican su posición o 3 cifras del código | Sin cambios: corta como hoy (pregunta 1) |
| Shipper: el «Close» del buscador, solo si la tarjeta ya muestra AQUACHILE | **CICLO:** medido, uno solo | `4b48792` y `c9c5402` |
| «Continue» de «Recommended services», solo si hay exactamente uno | **CICLO:** su HTML no está medido | `767e27b` |
| La búsqueda de salidas no corta; se quita la rama a NO ENVIADA | **CICLO** | `35f4c53` |
| `test_candado` no cambia | **NOTA:** se cumple | Sin cambios |

## Lo medido

**La casilla de cada resultado del buscador**, en el HTML del 27-09 (`casilla_forma.py`, `casilla_relacion.py`,
`casilla_codigo.py`; sin navegador):
- Los 3 resultados van en un solo `div.party-search-results`, cuyos 6 hijos son, en orden, casilla y `label`
  alternados: `input.party-card__input`, `label.party-card__label`, tres veces. No hay un envoltorio por resultado.
- La casilla trae `class`, `id`, `name` (igual a su `id`), `style` (vacío) y `type="radio"`; sin `value`. Los 3 `id`
  son distintos. El `label` trae solo `class`: sin `for`. Su tarjeta (`mc-c-party-card`) no tiene `id`.
- Ni el `id` ni el `name` de una casilla aparecen, enteros ni como parte, en ningún atributo de su `label`, de su
  tarjeta ni de lo que tienen adentro, ni en los de otro resultado.
- Lo único que los une, además de la posición: las 3 cifras visibles del código de cada tarjeta (con asteriscos) son el
  final del `id` de su casilla, en los 3, y no aparecen en el `id` de otra.

**El «Close» del buscador** (`cerrar_forma.py`): en toda la página hay un solo `mc-button` con `label="Close"` o
`data-cy="close"`, y está en el buscador: `mc-c-party-finder` › raíz shadow › `mc-modal` › raíz shadow › `dialog` ›
`header`. Trae `label="Close"`, `data-cy="close"`, `icon="times"` y `hiddenlabel` (el texto no se ve; su botón interno
lleva `aria-label="Close"`). La ventana (`mc-modal`) trae `backdropcloseactiondisabled`, y su `dialog` no está abierto
en ese HTML.

**«Continue» de «Recommended services»:**
- Ningún HTML guardado es de esa pantalla (`servicios_evidencia.py`, `servicios_html.py`). Antes de tu prueba (medido de
  14:05 a 14:11), de 261 `.html` en `logs/`, 0 ilegibles, 13 traen «Recommended services» o «additional-services»: 5 de
  MSC y 8 de MAERSK. Los 8 de MAERSK son de la lista de salidas (7) o de «Additional details» (1), donde aparece en la
  barra de pasos, y ninguno trae un `mc-button` con `label="Continue"`. Después de tu prueba son 319 y 15 (6 de MSC y 9
  de MAERSK), y sigue sin haber uno de esa pantalla.
- En sus 6 capturas (`mk_f<fila>_5b_services.png`: 5 del 21-09 y 1 del 27-09, de 1929×1044), el OCR no lee ningún
  «Continue», ni en los botones de color ni en la imagen entera; sí lee el título de la pantalla (`continuar_ocr.py`,
  `continuar_boton.py`). Lo más probable es que el botón quede fuera de lo capturado.
- En los `log.txt` (`continuar_log.py`): las 6 veces que MAERSK entró a esa pantalla anotó «pulsado 'Continue' en
  Recommended services», el camino de Playwright y no el respaldo en JavaScript, y las 6 siguió a «Additional details».

**La búsqueda de salidas** (`salidas_prueba.py`, por la revisión del informe): en los 23 `log.txt` de `logs/`, 14
desenlaces de `_mk_desenlace_sailing`, los 14 por «itinerarios y botones Book en pantalla», a los 2,1 o 2,3 s; ninguno
por tarifas, por «no hay zarpes» ni a los 45 s. En tu corrida de las 15:03, la fila de MAERSK anotó ese «Book» a los 2,1
s y quedó REVISAR, sin salida con fecha. Su HTML (`mk_f10_detenida.html`) trae «no sailings for your search», ningún
`mc-button` con `label="Book"` ni «Transit time», y un enlace «Book» a `/booking/new`. El detector acepta un botón o un
enlace «Book» a la vista más abajo de 100 px: lo más probable es que calzara con ese enlace, pero su posición a los 2,1
s no está medida.

**`pip` sin red** (`pip_sin_red.py`: un índice HTTPS que no responde, `192.0.2.1`, o un nombre que no resuelve,
`.invalid`; con `--isolated` y un paquete que no existe, para no instalar nada):

| Caso | Con `--timeout 5 --retries 0` | Sin límites |
|---|---|---|
| Nombre que no resuelve | 0,8 s | 8,4 s (5 reintentos) |
| Dirección que no responde | 6,0 s | 68,9 s (5 reintentos) |

**El código en `7a38598`:**
- los dos `.bat` instalan `playwright` y `openpyxl` si faltan, cada uno con una línea
  `python -c "import …" 2>nul || python -m pip install --user …`, y después abren el panel; están en LF, como todo el
  repo;
- el «Continue» de «Recommended services» tomaba el primer `mc-button`, `button`, `[role=button]` o enlace con ese
  texto (`.first`) y, si no lo pulsaba, por JavaScript el primer elemento a la vista con ese texto; si tampoco, seguía
  sin cortar;
- `test_candado` solo pide que cada `.bat` lance su programa y que el seguro no nombre la emisión, y fotografía en
  `reservar_maersk` los textos «Continue to book» y «MAERSK: no se abrió el formulario /book/».

## Cómo quedó cada punto

**1. holidays en los lanzadores** (`a44ba13`): antes de abrir el panel, los dos `.bat` corren esta línea:

```bat
python -c "import holidays" 2>nul || python -m pip install --user --disable-pip-version-check --timeout 5 --retries 0 holidays
```

Si ya está, no hace nada; sin red, se rinde en segundos y el panel abre igual. Si no queda, el programa avisa y sigue de
lunes a viernes, como ya hacía. `LEEME.md` lo dice en su primer paso. El 29-09 a las 14:58, al abrir el panel para tu
prueba, instaló holidays 0.105: la primera medición con red.

**2. La búsqueda de salidas** (`35f4c53`): se quitó la rama a NO ENVIADA para «indefinido». A los 45 s,
`_mk_desenlace_sailing` dice «con-zarpes» (así desde el primer commit, `14aa9ef`) y la reserva sigue a elegir la nave;
si no aparece, REVISAR por `_mk_sin_nave`.

**3. «Continue» de «Recommended services»** (`767e27b`; `_mk_continuar_servicios`, `_JS_MK_CONTINUAR`,
`MK_CONTINUAR`):
- Un «Continue» es un `mc-button` (por su `label` o su texto), un `button`, un enlace o lo que tenga `role="button"`,
  con ese texto entero, sin distinguir mayúsculas y a la vista. Lo que está dentro de otro (el botón interno de un
  `mc-button`) es el mismo control: se cuentan controles, no elementos.
- Lo busca hasta 15 veces (`MK_INTENTOS_CONTINUAR`), una por segundo. Con exactamente uno, lo pulsa con Playwright
  sobre lo que `_JS_MK_CONTINUAR_PULSAR` vuelve a leer justo antes («uno y ningún otro»).
- Si «Additional details» ya apareció (un clic que falló pudo haber salido), sigue sin pulsar.
- Con cero o más de uno: «Recommended services de MAERSK: no encontré un solo botón «Continue» a la vista, por su texto,
  en 15 intentos (había N), así que no pulsé nada» (y antes, «el portal pide: …», si `_mk_lo_que_pide` lee algo), NO
  ENVIADA con `mk_f<fila>_sin_objetivo`. Si en el último intento, al volver a leer, ya no era uno solo, el motivo lo
  dice.
- Si está, pero no acepta el clic: NO ENVIADA con ese motivo y `mk_f<fila>_servicios`.
- `reservar_maersk` corta si la ayuda devuelve el corte. La foto de clics ya no permite a MAERSK la forma «el primero
  cuyo `textContent` calza»: si el respaldo vuelve, la red cae.

**4. El «Close» del buscador** (`4b48792` y `c9c5402`; `_mk_cerrar_buscador`, `MK_CERRAR`):
- Después del resultado, si la tarjeta «Shipper» ya muestra a AQUACHILE y el buscador sigue abierto al cabo de 5 s,
  pulsa su «Close»: el único `mc-button` a la vista del buscador con `label="Close"`.
- Antes de pulsarlo deja `mk_f<fila>_cerrar`, el único HTML que puede medir ese estado: el del 27-09 tiene el buscador
  cerrado.
- `_JS_MK_SHIPPER_PULSAR` lo vuelve a leer justo antes y lo da solo si hay una sola tarjeta «Shipper» y sigue mostrando
  a AQUACHILE. Si no lo da, el motivo dice las dos razones posibles: «ya no había un solo «Close» a la vista en el
  buscador, o la tarjeta «Shipper» ya no mostraba a AQUACHILE».
- Comprueba, hasta 5 s, que el buscador se cerró y que la tarjeta lo sigue mostrando.
- Si no hay un solo «Close» a la vista, si el clic falla, o si después el buscador sigue abierto, la tarjeta ya no lo
  muestra o no se puede leer: NO ENVIADA con `mk_f<fila>_shipper`, sin otro clic.
- Si la tarjeta no muestra a AQUACHILE, no pulsa el «Close», aunque el buscador siga abierto con uno a la vista.

**5. La casilla del resultado: sin cambios (FRENO).** Si el clic en el resultado no lo elige, la reserva corta como
hoy: «…pulsé el resultado con AQUACHILE del buscador, pero la tarjeta «Shipper» no lo muestra…», con
`mk_f<fila>_shipper`.

## Cómo probarlo

Con **`Iniciar AQUASHIELD.bat`**; nunca con `Iniciar AQUASHIELD_EMISION.bat`. Antes, revisa que `config.json` no traiga
`"emitir_reservas": true` en «opciones», que no esté definida la variable `AQUASHIELD_EMITIR` (la abren 1, true, si o
yes) y que el programa no se lance con el argumento `emitir` o `produccion`: con cualquiera de las tres llaves, se
emite.

- **Tu prueba de las 15:03 corrió con el código de `767e27b`:** sin el «Close» ni lo del commit 5. Ese panel ya se
  cerró, y al volver a abrirlo con el `.bat` carga lo último; si alguna vez queda uno abierto de antes, ciérralo y
  vuelve a abrirlo.
- **Al arrancar,** si falta holidays, la ventana del `.bat` muestra a `pip` instalándola; en esta máquina ya quedó
  instalada. La fecha de retiro salta los feriados de Chile: «Fecha de retiro: … es feriado en Chile.».
- **En el `log.txt` de una fila de MAERSK:** «pulsado 'Continue' en Recommended services»; en el Shipper, si no venía,
  «Shipper: pulsé el «Add»…», «Shipper: pulsé el resultado con AQUACHILE del buscador», si hizo falta «Shipper: pulsé el
  «Close» del buscador», y «Shipper: elegí a AQUACHILE en el buscador, y la tarjeta «Shipper» lo muestra».
- **Si corta, el motivo dice dónde:**
  - «Continue»: «✗ NO ENVIADA · Recommended services de MAERSK: … No encontré un solo botón «Continue» a la vista …
    (había N)…», con `mk_f<fila>_sin_objetivo`: ese HTML es el primero que mide la pantalla;
  - el «Close»: «…el buscador siguió abierto y no hay un solo «Close» a la vista en él (había N)…» o «…pulsé el «Close»
    del buscador, pero siguió abierto…», con `mk_f<fila>_shipper`;
  - el resultado que no se elige: «…pulsé el resultado con AQUACHILE del buscador, pero la tarjeta «Shipper» no lo
    muestra…», con `mk_f<fila>_shipper` (pregunta 1).

En tu corrida de las 15:03, MAERSK no llegó a «Recommended services» ni al Shipper: quedó REVISAR en «Select sailing»,
con «no sailings for your search» en la página (pregunta 3). Para lo demás, dime qué corrida fue y leo su evidencia en
`logs/`.

## Qué decides tú

1. **La casilla del resultado (FRENO).** No está dentro del resultado de AQUACHILE: va justo antes de su `label`, en un
   contenedor que comparten los 3 resultados, y nada la une a él más que esa posición y que su `id` termina con las 3
   cifras visibles del código de la tarjeta. Si el clic en el resultado no lo elige, ¿cómo sigo?
   - **Por su posición:** la casilla (`input.party-card__input`) que va justo antes del `label` de AQUACHILE, en ese
     contenedor, comprobando que todo el contenedor sea casilla y `label` alternados.
   - **Por su posición y el código:** lo mismo, y además que su `id` termine con las cifras visibles del código de la
     tarjeta de AQUACHILE, y con ninguna otra.
   - **Que corte, como hoy.**
   Si eliges pulsarla, falta también cómo: su estilo no está en el HTML guardado, así que no se sabe si se ve; la
   casilla de los términos se marca con un clic de JavaScript en su `input`.
2. **El paso a la selección de nave.** Para salir de «Booking Information», el programa pulsa el primer botón habilitado
   cuyo nombre accesible contiene «Continue to book» o, si no, «Continue» (`get_by_role(..., exact=False).first`), sin
   mirar si se ve. La foto de clics no lo ve (`.first` no es una de sus formas). ¿Le aplico la misma regla que a
   «Continue» (solo si hay uno a la vista)? `test_candado` fotografía ese texto, así que conservaría su literal.
3. **El detector de salidas.** `_mk_desenlace_sailing` da la búsqueda por terminada con cualquier botón o enlace «Book»
   a la vista más abajo de 100 px. En los 14 desenlaces de `logs/` terminó así, a los 2 s. En tu prueba, la página decía
   «no sailings for your search» y no traía ningún «Book» de una salida, pero sí el enlace «Book» del encabezado o el
   pie, y la fila quedó REVISAR en vez de SIN-CUPO. ¿Lo dejo así, o cuento solo el `mc-button` con `label="Book"` de una
   salida, como ya hace la lista (`_JS_MK_SALIDAS`)?

## Re-medir (pieza 1)

Las sondas son de solo lectura y no se versionan, porque leen datos reales. Quedaron en el scratchpad de esta sesión
(`$env:TEMP\claude\<proyecto>\<sesión>\scratchpad\e39`), que puede limpiarse; sin ellas, estos números no se re-miden.
Las que miden abortan si no pasa su control positivo, salvo `pip_sin_red.py` (sin control: por eso pasó el defecto de la
pieza 4, 1), `servicios_html.py` (su control es el de `servicios_evidencia.py`) y `red_por_commit.py`; y todas leen en
su lugar, sin copiar el HTML ni los `log.txt`.
- **`casilla_forma.py`:** con `html.parser`, en el HTML del 27-09, cada resultado del buscador (el `label` con su
  tarjeta): el envoltorio más cercano que trae casillas, cuántas casillas y `label` trae, y sus hermanos; y los botones
  del buscador, con sus atributos de interfaz. Los textos que no son de interfaz salen como su largo. Su control: un
  buscador sintético con cada casilla y su `label` en su propio envoltorio.
- **`casilla_relacion.py`:** en `div.party-search-results`, los hijos en orden, los pares casilla + `label`, sus clases
  y nombres de atributos, y si el `id` o el `name` de cada casilla aparecen, enteros o como parte, en los atributos de
  su `label`, de su tarjeta o de otro resultado. Su control: un `label` con `for` igual al `id` de su casilla.
- **`casilla_codigo.py`:** si las cifras visibles del código de cada tarjeta calzan con el final del `id` de su casilla,
  y con el de otras, y el `style` de cada casilla. Solo largos y booleanos. Su control: una tarjeta sintética cuyo
  código enmascarado calza.
- **`cerrar_forma.py`:** los `mc-button` con `label="Close"` o `data-cy="close"` de toda la página y del buscador, su
  ruta desde el buscador y sus atributos; y la ventana del buscador. Su control: un «Close» sintético dentro del
  buscador y otro fuera.
- **`servicios_evidencia.py` y `servicios_html.py`:** las capturas `*_5b_services.png` por carpeta, y los `.html` que
  traen «Recommended services» o «additional-services», con la dirección `/book/…` de la página y cuántos «Continue»
  traen. Su control: tiene que haber alguna captura de esa pantalla.
- **`continuar_ocr.py` y `continuar_boton.py`:** con OCR, sin mirar, los «Continue» de las 6 capturas, por botón de
  color (el método de `e29/one_botones.py`) y en la imagen entera; y las palabras de interfaz del botón que se lee. Sus
  controles: una imagen sintética con un «Continue» blanco sobre azul y otro oscuro sobre blanco, y, por captura, que se
  lea el título de la pantalla.
- **`continuar_log.py`:** en los `log.txt`, las entradas a «Recommended services», los «Continue» pulsados y los pasos a
  «Additional details». Su control: tiene que haber alguna entrada.
- **`pip_sin_red.py <caso>`:** cuánto tarda `pip` en rendirse contra un índice HTTPS que no responde o un nombre que no
  resuelve, con y sin límites, con `--isolated` y un paquete que no existe.
- **`vigila_prueba.py`:** avisa cuando ya no hay un Chrome con un perfil de `perfiles/` (sin imprimir su ruta).
- **`salidas_prueba.py`:** en los `log.txt` de `logs/`, los desenlaces de `_mk_desenlace_sailing` y su segundo; en tu
  corrida de las 15:03, el paso de MAERSK; y en su HTML, los `mc-button` «Book», «Transit time», «no sailings for your
  search» y los enlaces «Book» con el comienzo de su dirección. Su control: la corrida tiene que traer pasos de MAERSK.
- **La instalación de holidays:** `python -c "import holidays"`, con su versión y la fecha de su carpeta en el site del
  usuario: 0.105, del 29-09 a las 14:58.
- **`copia.py [rev]`, `anclas.py <copia>` y `largas_copia.py <copia>`**, **`precenso.sh`**, **`gate.sh`**,
  **`censo.sh`**, **`commit.sh`** y **`red_por_commit.py`**: los del encargo 38, con la ruta de este.
- **Los cambios:** `aplicar_h1.py`, `aplicar_h2.py` (y `arreglo_h2.py`), `aplicar_h3.py` (con `h3_codigo.txt`,
  `h3_tramo.txt`, `h3_pruebas.txt` y `h3_mutaciones.txt`), `aplicar_h4.py` (con `h4_funcion.txt`, `h4_pruebas.txt` y
  `h4_mutaciones.txt`), `aplicar_h5.py` y `aplicar_docs39.py`, todos con `comun.py`: cada viejo, exactamente una vez,
  y escritura en
  binario, LF.

La red versionada, desde `C:\dev\Agendamiento Reservas`: `python tests/correr.py` (la suite, unos 5 min),
`python tests/correr.py --mutaciones --filtro <texto>` (`mk-continuar`, `mk-shipper`, `bat-`…) y
`python tests/correr.py --mutaciones` (el censo completo).

## NO retroceder (pieza 2)

- **No pulses la casilla del resultado sin la decisión de Marcelo:** no está dentro del resultado; solo la ubican su
  posición y 3 cifras del código.
- **No cuentes «Continue» por elementos:** el `mc-button` y su botón interno son el mismo control; se cuentan controles.
- **No busques el «Close» por su texto visible:** va oculto (`hiddenlabel`). Va por su `label`, y solo dentro del
  buscador.
- **No pulses el «Close» si la tarjeta no muestra a AQUACHILE:** lo decidió Marcelo, y lo vigilan Python y el
  JavaScript que vuelve a leer justo antes.
- **No vuelvas a la rama «indefinido» de la búsqueda de salidas:** `_mk_desenlace_sailing` no la devuelve.
- **No quites `--timeout 5 --retries 0` de la línea de holidays:** sin ellos, con un índice que no responde, `pip` tardó
  69 s en rendirse, y el panel abre después.
- **No midas `pip` sin red contra un índice `http://`:** lo descarta por inseguro sin intentar conectar, y todo tarda
  lo mismo (pieza 4, 1).
- **Cuando un cambio mueve el texto de una ancla, revisa a mano las mutaciones que siguen calzando una vez:** pueden
  haber pasado a otra función sin que `anclas.py` lo note (pieza 4, 5).

## Universo y cobertura (pieza 3)

- **HTML:** el de «Additional details» del 27-09; de él, los 3 resultados, las 3 casillas, los 4 `mc-button` del
  buscador («Close», las dos pestañas y «Cancel») y sus 4 botones internos, y el único «Close» de la página. En `logs/`,
  antes de tu prueba (de 14:05 a 14:11), 261 `.html`, 0 ilegibles, ninguno de «Recommended services» y solo ese con el
  buscador. Tu prueba sumó 58: son 319, ninguno de esa pantalla, y 2 con el buscador; el segundo es de tu corrida
  (cerrado, con un solo «Close» y sin resultados, según la revisión del informe).
- **Capturas:** las 6 de «Recommended services» (5 del 21-09, 1 del 27-09), con OCR, sin mirar.
- **`log.txt`:** los 21 de `logs/` antes de tu prueba, 0 ilegibles, con 6 entradas a «Recommended services»; después,
  23, con 14 desenlaces de la búsqueda de salidas (`salidas_prueba.py`).
- **Código:** `reservar_maersk` y lo que llama antes de su guarda; los dos `.bat`.
- **No medido:**
  - el HTML de «Recommended services»: cuántos «Continue» hay a la vista y de qué tipo;
  - si la casilla de un resultado se ve (su `style` viene vacío) y si el clic en el `label` elige la parte;
  - que el «Close» cierre el buscador en el portal;
  - `pip` sin red de verdad: se simuló con un índice que no responde y un nombre que no resuelve;
  - qué «Book» vio el detector de salidas a los 2,1 s en tu corrida: su posición no está en el HTML guardado.

## Defectos de instrumento cazados (pieza 4)

1. **Mi primera medición de `pip` sin red usaba un índice `http://`:** `pip` lo descarta por inseguro sin intentar
   conectar, y los cuatro casos daban 0,7 s. Lo vi al leer la salida entera de `pip`; con `https://` sí intenta, y ahí
   salen 6 s contra 69 s. La primera lectura, 4,5 s, era el arranque en frío de Python.
2. **El control de `continuar_ocr.py` esperaba que la lectura de la imagen entera viera el «Continue» blanco sobre
   azul:** no lo ve, como ya estaba registrado en el encargo 29. El control abortó, como debía, y se corrigió lo que
   esperaba.
3. **Usé `sort` en Git Bash**, que Defender bloquea: solo afectó cómo se mostraba una salida.
4. **El código nuevo de «Continue» repetía textos que eran el ancla de 4 mutaciones viejas** (de «Review booking» y
   del Shipper), y una ancla mía calzaba también con otro JavaScript: 5 anclas dobles. Las cazó `anclas.py` en la
   copia, y cambié el código nuevo para no repetirlas, sin tocar las viejas.
5. **Dos mutaciones del encargo 38 habrían cambiado de lugar sin avisar:** su ancla, el corte de «el buscador siguió
   abierto», seguía calzando una vez, pero en `_mk_cerrar_buscador`, donde ya no prueban lo que dicen. `anclas.py` no
   lo ve, porque solo cuenta. Se reanclaron en la llamada al «Close».
6. **Líneas de más de 120** en el código, las pruebas y las mutaciones: las cazó `largas_copia.py` antes de cada gate.
7. **La foto de los originales cayó dos veces por tu prueba, y la segunda también por una mala lectura mía:** primero,
   por el archivo de bloqueo de Excel (`~$Reservas AQUASHIELD.xlsx`, al abrir la planilla). A las 14:59 lo leí como algo
   que no era una prueba y relancé en la raíz el censo de `test_solo_ahi`, que corrió hasta las 15:04, en paralelo con
   tu login y tu corrida, y cayó otra vez: 862 cambios, 853 en `perfiles/` y 9 archivos nuevos en `logs/`, los de tu
   login. Los pares mordían todos las dos veces; el commit 3 se hizo con esa salvedad, y el gate de `c9c5402` volvió a
   censar `test_solo_ahi` (60/60) sin cambios en los originales. Lo cazó la revisión del informe.
8. **El mensaje de `35f4c53` dice que `f4728e3` agregó la rama «indefinido»:** existía desde `14aa9ef`, con REVISAR;
   `f4728e3` solo la pasó a NO ENVIADA. Lo cazó la revisión de código; el mensaje se corrige aquí.
9. **Mis pruebas del «Close» no cubrían 0 ni 2 tarjetas «Shipper»:** con ellas, dos defectos de la guarda del clic
   (pulsarlo con «la empresa no es falso», o con dos tarjetas si una trae a AQUACHILE) pasaban la red. Lo cazó la
   revisión de código, y el commit 5 suma esos casos y sus mutaciones.

## Premisas del encargo contrastadas (pieza 5)

- **«La casilla del mismo resultado de AQUACHILE»:** no se cumple en la forma pedida. La casilla no está dentro del
  resultado: va antes de su `label`, en un contenedor que comparten los 3. La posición y 3 cifras del código la unen a
  él, 1:1 en los 3, pero no la contienen (FRENO, pregunta 1).
- **«El «Close» del buscador, solo si la tarjeta ya muestra AQUACHILE»:** confirmada: hay uno solo, identificable por su
  `label`, dentro del buscador.
- **«Continue… exactamente uno a la vista»:** no se pudo contrastar: su HTML no está medido. Se implementó la regla, y
  el primer corte deja el HTML que la mide.
- **«holidays… sin frenar el arranque si no hay red»:** confirmada con una red simulada: 6 s. Y con red, el 29-09 a las
  14:58, al abrir tu prueba, la línea instaló holidays 0.105.
- **«Se quita la rama a NO ENVIADA que nunca se alcanza»:** confirmada: `_mk_desenlace_sailing` no devuelve
  «indefinido» desde `14aa9ef`.
- **«La búsqueda de salidas no corta a los 45 s»:** matizada. En los 14 desenlaces anotados en `logs/`, la búsqueda
  terminó a los 2,1 o 2,3 s por un «Book» a la vista, nunca por la espera. En tu prueba del 29-09, con «no sailings for
  your search» en la página y sin ningún «Book» de una salida, la fila quedó REVISAR y no SIN-CUPO; lo más probable es
  que el detector calzara con el enlace «Book» del encabezado o el pie (pregunta 3).
- **FRENA SI:** se cumple para la casilla.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| Si el clic en el resultado no elige la parte, la reserva queda NO ENVIADA; no se pulsa su casilla | FRENO: la casilla no está dentro del resultado | …decides cómo identificarla (pregunta 1) |
| El HTML de «Recommended services» no está medido | Ninguna corrida lo guardó; en las capturas el botón no se ve | …una corrida corta ahí y deja `mk_f<fila>_sin_objetivo` |
| El paso a la selección de nave pulsa el primer botón «Continue to book» o «Continue» | Fuera del encargo; `test_candado` fotografía ese texto | …lo decides (pregunta 2) |
| El «Close» no se probó en el portal | Sin corrida con el buscador abierto | …la prueba lo muestra |
| `pip` sin red no se probó con la red cortada de verdad | Se simuló con un índice que no responde | …un arranque sin red tarda más de unos segundos |
| La casilla podría no verse: su `style` viene vacío | Las reglas que la alcanzan no están en el HTML guardado: sus 9 `<style>` no la nombran, los 5 `<link>` son externos y los estilos de las raíces shadow no quedan en él | …se decide pulsarla |
| El detector de salidas da la búsqueda por terminada con cualquier «Book» a la vista, también el enlace del encabezado o el pie; así, «no hay zarpes» (SIN-CUPO) casi no se alcanza | Fuera del encargo; medido en tu prueba | …lo decides (pregunta 3) |
| La línea de holidays de los `.bat` tiene 126 columnas | La regla de 120 se mide en los `.py`; partirla con `^` o sacar un flag a un `set` cambiaría lo que vigila `TestLanzadores` | …se decide igualarla |
| Si el buscador se cierra solo justo entre la última lectura y el clic, la relectura no da el «Close» y la reserva corta, con el Shipper bien puesto | Antes cortaba siempre; aceptarlo pide otra lectura sin clic | …pasa en una corrida |
| Después de «Continue» no se comprueba que el portal avanzó: si no avanza, el corte llega en la revisión, con su motivo | Así era antes | …se quiere el motivo exacto de ese paso |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v14**.
- **PASO 0 con sus cuatro valores:** CICLO en holidays, «Continue», el «Close» y la rama de la búsqueda; PREGUNTA
  (FRENO) en la casilla; NOTA en `test_candado`.
- **FRENAR cuando la decisión es de negocio:** la casilla (se cumple el FRENA SI) y el paso a la selección de nave
  quedan como preguntas.
- **Control positivo que aborta:** en cada sonda que mide, salvo tres (pieza 1). El de `continuar_ocr.py` abortó por una
  expectativa mía equivocada (pieza 4, 2), y a `pip_sin_red.py` le faltaba: por eso pasó el índice `http://` (pieza 4,
  1).
- **El negativo tiene que morder:** cada prueba nueva con su mutación; un precenso en una copia antes de cada gate, el
  censo filtrado en cada commit y el completo en el último.
- **Todo registro es una hipótesis:** «el HTML guardado muestra la casilla dentro del resultado» no se supuso; se midió,
  y no. «Continue» no está medido, y así se dice.
- **Un cero solo vale con su contador:** 0 «Continue» en 6 capturas, con el título leído en las 6; 0 HTML de esa
  pantalla, de 261 `.html` y 0 ilegibles antes de tu prueba, y de 319 después.
- **Re-medir contra HEAD:** el código se leyó en `7a38598`, y cada cambio se probó sobre una copia de su commit padre.
- **Fuente única:** `_JS_MK_CONTINUAR_LEER` para contar y para pulsar; `_MK_ARGS_SHIPPER` con `MK_CERRAR`.
- **Cada reemplazo, exactamente una vez, y el EOL preservado:** anclas únicas; 0 CR en cada commit; los `.bat`, en LF.
  La escritura no es atómica: `comun.py` valida todas las anclas antes de escribir, pero escribe con `write_bytes` sobre
  el archivo (desviación declarada; git guarda la versión anterior).
- **El cambio y su guardián, juntos:** cada commit con sus pruebas y sus mutaciones, y las reancladas en el mismo
  commit.
- **Choques entre reglas:**
  1. **«La casilla del mismo resultado» contra el FRENA SI:** medido que no está dentro, gana el freno: no se pulsa.
  2. **«test_candado no cambia» contra el paso «Continue» en `reservar_maersk`:** la regla va en una ayuda aparte y la
     foto de `test_candado` no cambia.
  3. **«No cargar el equipo ni tocar la raíz» contra tu prueba en paralelo:** a las 14:59 leí el bloqueo de Excel como
     algo que no era una prueba y relancé el censo de `test_solo_ahi`; corrió hasta las 15:04, en paralelo con tu login
     y tu corrida, y volvió a caer (pieza 4, 7). Desde las 15:04 hasta que cerraste Chrome (15:10) no apliqué cambios ni
     lancé censos; el commit 3 no tocó el árbol, y tu prueba usó el código de `767e27b`.

Reglas del módulo: nada de `logs/` en el repo; ningún nombre de nave, viaje, puerto, depósito, parte, código ni
operador, ni número de reserva, en este informe; `test_candado` sin cambios; la sonda de secretos antes de cada commit;
los textos en español con tuteo.

## Entregable (pieza 8)

- **Este `.md`:** no se convirtió en página; se leyó como texto.
- **`CLAUDE.md` al día,** en el commit de este informe: holidays en los `.bat` y en los requisitos, el «Continue» de
  «Recommended services», el «Close» del buscador y el FRENO de la casilla, la búsqueda de salidas sin su rama y lo
  medido de su detector (pregunta 3), la evidencia `mk_f<fila>_servicios` y `mk_f<fila>_cerrar`, la foto sin la forma
  de MAERSK, los estados y el número de pruebas.
- **La red, commit por commit:**

| Commit | Pruebas | Mutaciones | Pares |
|---|---|---|---|
| `7a38598` (base) | 477 | 1326 | 1584 |
| `a44ba13` | 478 | 1331 | 1589 |
| `35f4c53` | 480 | 1331 | 1589 |
| `767e27b` | 490 | 1352 | 1612 |
| `4b48792` | 492 | 1361 | 1622 |
| `c9c5402` | 492 | 1365 | 1627 |

- **El gate de cada commit:** la suite completa en verde y los censos filtrados (pares mutación-prueba que muerden /
  pares), ninguno que no muerda; todos en OK, salvo `test_solo_ahi` de `767e27b`, que dio FALLA dos veces por los
  originales (pieza 4, 7), con sus 58 pares mordiendo.

| Commit | Suite | Censos filtrados |
|---|---|---|
| `a44ba13` | 478 | bat- 7/7 · TestLanzadores 9/9 |
| `35f4c53` | 480 | mk-zarpes 3/3 · test_los_cortes_antes_de_la_nave_son_no_enviada 4/4 · test_revisar_solo_si_la_nave_no_esta 6/6 |
| `767e27b` | 490 | mk-continuar 23/23 · TestFotoDeClicsGenericos 63/63 · test_solo_ahi 58/58 (los originales cambiaron por tu prueba: pieza 4, 7) |
| `4b48792` | 492 | mk-shipper 61/61 · TestShipperMaersk 62/62 |
| `c9c5402` | 492 | mk-shipper 66/66 · TestShipperMaersk 67/67 · test_solo_ahi 60/60 |

- **Antes de cada gate,** las mutaciones nuevas se censaron en una copia (`precenso.sh`): `bat-` 7/7; `mk-zarpes` 3/3,
  los cortes 4/4 y REVISAR 6/6; `mk-continuar` 23/23, la foto 63/63 y `test_solo_ahi` 58/58; `mk-shipper` 61/61 y
  `TestShipperMaersk` 62/62; y en el commit 5, `mk-shipper` 66/66, `TestShipperMaersk` 67/67 y `test_solo_ahi` 60/60.
  Ninguna dejó de morder.
- **El censo completo sobre `c9c5402`:** 1365 mutaciones y 1627 pares, con las 492 pruebas y 0 sin mutación: los
  1627 muerden, ninguno con el tiempo agotado; 3395 originales fotografiados y 0 cambios; RESULTADO: OK. Duró unos
  73 min (de 16:15 a 17:28), sin ningún evento de Kernel-Power en ese lapso; el control, de 11:00 a 11:56, ve los 5
  del reinicio de las 11:37 (el 109 de apagado, el 577, el 125 y dos 521).
- **Cada commit:** la sonda de secretos dio 0 sobre el árbol y 0 sobre lo agregado, y 0 CR en los archivos commiteados.
- **La revisión de código:** un agente, en solo lectura, con sondas propias sobre el árbol, una copia con el commit 4 y
  el HTML del 27-09 (en su lugar); sin la suite ni censos, porque corría tu prueba.
  - Resultado: 0 críticos, 0 altos, 2 medios y 7 bajos.
  - Confirmó: el FRENO de la casilla (la adyacencia no es ambigua en ese HTML, pero es por posición); el «Close» medido;
    que «Continue» cuenta controles (sobre el árbol real, su JavaScript da 1 «Review booking», 1 «Close» y 8 «Add»); que
    el «Close» no se puede pulsar sin AQUACHILE en la tarjeta; que «indefinido» nunca se devolvió en los 116 commits que
    tocaron `AQUASHIELD.py` hasta `767e27b` (118 hasta `c9c5402`, según la revisión del informe); que nada cambió
    después de la guarda y que `test_candado` es idéntico; que ninguna de las 1361 mutaciones cambió de función (su
    sonda comparó dónde calza cada ancla en `7a38598` y después); y que las 492 pruebas tienen su mutación.
  - **Los medios:** la regla del «Close» sin probar con 0 o 2 tarjetas «Shipper», con dos defectos plausibles que
    pasaban la red (pieza 4, 9); y `CLAUDE.md` desfasado.
  - **Los bajos:** el motivo de la relectura del «Close»; la línea de 126 columnas de los `.bat`; dos docstrings; el
    mensaje de `35f4c53` (pieza 4, 8); que no había evidencia del estado que justifica el «Close»; una carrera si el
    buscador se cierra solo justo antes del clic; y que después de «Continue» no se comprueba que el portal avanzó.
  - Quedó en `c9c5402`: los casos de 0 y 2 tarjetas con sus 2 mutaciones, el motivo, la evidencia `mk_f<fila>_cerrar`
    (con su mutación y `test_solo_ahi`) y los docstrings. `CLAUDE.md` va en el commit de este informe; el mensaje de
    `35f4c53` se corrige aquí; lo demás, en el residual.
  - **Fuera del alcance,** vio el paso a la selección de nave (pregunta 2).
- **La revisión adversarial de este informe:** un agente, en solo lectura, con sondas propias que tapan lo que es dato;
  sin la suite ni censos, porque corría el censo completo.
  - Resultado: 1 alto, 5 medios y 11 bajos.
  - **El alto:** el informe no había leído tu corrida de las 15:03, y ahí la búsqueda de salidas mostró que su detector
    termina con cualquier «Book» a la vista, probablemente el enlace del encabezado o el pie (Resumen, pieza 5 y
    pregunta 3).
  - **Los medios:** las cuentas de `logs/` eran de antes de tu prueba; el choque 3 de la pieza 7 era falso, porque
    relancé un censo durante tu prueba (pieza 4, 7); tres sondas sin control positivo; la frase del gate (son pares, no
    mutaciones, y faltaba la FALLA de `test_solo_ahi` de `767e27b`); y las hojas de estilo del HTML guardado.
  - **Los bajos:** cuántos botones tiene el buscador; `aplicar_h5.py` y la medición de holidays en la pieza 1; «el botón
    queda fuera de lo capturado», que es una inferencia; los 69 s, que son de `pip` solo; «tu panel sigue abierto»; los
    116 commits; la pregunta 2 (el nombre que «contiene», y habilitado); los motivos de «Continue»; «refutada»; la
    escritura de `comun.py`, que no es atómica; y la tercera llave del candado.
  - Verifiqué el alto y los medios antes de corregirlos: la búsqueda con `salidas_prueba.py` (14 desenlaces, y en tu
    corrida «no sailings for your search», 0 «Book» de una salida y un enlace a `/booking/new`); `logs/` con
    `partes_estructura.py` y `servicios_evidencia.py` (319 `.html`, 2 con el buscador, 15 con la pantalla nombrada); los
    862 cambios de la segunda caída; y que tu panel ya estaba cerrado. Todo quedó corregido en este informe.
  - Confirmó lo demás: la base, la red por commit, los gates y los precensos, la línea de los `.bat`, los tiempos de
    `pip`, cada punto de «Cómo quedó» contra el código de `c9c5402`, lo medido en el HTML, las anclas y el resumen de la
    revisión de código.
