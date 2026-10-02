# Encargo 46 · MAERSK pulsa el «Book» de la salida que eligió

**Base:** `C:\dev\Agendamiento Reservas` @ `9995517` · árbol limpio.

Medido con `metodo-ciclo` v15 sobre lo guardado en `logs/`: 28 carpetas de corrida, 0 que no calzan con el patrón del
programa, y ninguna nueva desde el encargo 45 (la última es la del 01-10 a las 16:07). Nada de este encargo abrió un
portal.

## En resumen

- **El «Book»:** antes de mirar a qué altura está el «Book» de la salida elegida, MAERSK trae su tarjeta a la vista; la
  regla de los 100 px se mantiene y se aplica después. Si aun así no lo pulsa, la fila queda NO ENVIADA, con la captura
  y el HTML de «Select sailing», y el motivo dice que la nave estaba, qué salida eligió y por qué no pudo pulsarlo. Ya
  no sigue por la rama de la nave que no está.
- **La tilde y la ñ:** el prefijo con que MAERSK reconoce su lista toma la letra con tilde como la letra sin ella, y la
  «Ñ» como «N». «Igual a lo escrito» sigue sin distinguir tildes.
- **COSCO:** quita también un «CL» al final del puerto, igual que «CHILE».
- **Las 5 capturas del encargo 42:** cerradas como nota, después de volver a medir su HTML.
- **FRENA SI no se cumplió:** traer la tarjeta no necesita un clic ni una tecla, y ninguna de las 71 reservas guardadas
  que llegaron a la guarda cambia de estado con estos cambios.
- Sin clics nuevos, y `test_candado` no cambia. La suite pasa con 568 pruebas, y el censo completo muerde con
  sus 1681 mutaciones.

## El «Book» de MAERSK

### Lo que se sabía, y lo que se midió hoy

El encargo 45 midió que el 01-10 la nave estaba en 3 tarjetas idénticas del 18-10 (las 7, 8 y 9 de 14), que el
programa eligió la 7 y que no pulsó su «Book». La altura de ese «Book» en ese instante no se guarda: que la tarjeta
había quedado arriba de la ventana lo dicen la captura de después y el código. Hoy medí, con OCR y sin mirar las
capturas, la geometría de esa pantalla:

| Qué | Medido |
|---|---|
| Alto de la ventana | 1449 a 1606 px CSS, en las 44 capturas de «Select sailing» de 13 corridas |
| De una tarjeta a la siguiente | 400 a 422 px CSS, en las 5 capturas con dos tarjetas legibles (25-09, 30-09 y 01-10) |
| El «Book» dentro de su tarjeta | 93 a 100 px más abajo que su «Route & other details», que va debajo del encabezado de la tarjeta |
| La ventana del 01-10, justo después | Dos tarjetas con «Book», a 138 y 558 px, y fechas del 25-10, ninguna del 18-10: la 7 estaba al menos tres tarjetas más arriba |

Con eso, la tarjeta 7 del 01-10 estaba entera fuera de la ventana, por arriba. Traída a la vista, Playwright la centra,
y su «Book» queda hacia la mitad de la ventana, lejos de los 100 px. Lo más probable es que ahora lo pulse; si después
la reserva sigue, no se sabe sin el portal.

### El cambio

- `_mk_pulsar_book` trae la tarjeta de la salida elegida a la vista con `scroll_into_view_if_needed` de Playwright, el
  mismo con que ya traía el «Book» antes de pulsarlo: desplaza la página, sin clics ni teclas. Después aplica la regla
  de siempre (un «Book» a la vista, a más de 100 px del borde de arriba) y pulsa una sola vez.
- Si no lo pulsa, dice por qué, de una de cuatro formas: no pudo traer la tarjeta; con la tarjeta a la vista, el
  «Book» quedó a N px del borde de arriba; el clic falló (con el error); o la tarjeta no trae un «Book» a la vista.
- `_mk_elegir_nave` devuelve ese caso aparte, con la salida elegida y el porqué, y `reservar_maersk` lo lleva a
  `_mk_book_sin_pulsar`: deja `mk_f<fila>_detenida` (la captura de la ventana y el HTML) y la fila queda NO ENVIADA.
  El motivo, con datos inventados:

  > MAERSK: la nave 'MAERSK NAVE' estaba en «Select sailing» y elegí su salida (sale 18 Oct 2026, 08:30), pero no pude
  > pulsar su «Book»: con su tarjeta a la vista, el «Book» quedó a 50 px del borde de arriba de la ventana, y lo pulso
  > solo si está a más de 100 px. No pulsé nada más, y la reserva no se envió
- **Si el clic en el «Book» falla:** hasta ahora la falla subía, y la fila quedaba ERROR con el texto de Playwright;
  ahora queda NO ENVIADA con ese motivo. No se prueba el otro elemento del mismo control: sería un clic nuevo.
- Cierra las dos filas de MAERSK del residual del encargo 45: el «Book» a la vista, con su propio motivo, y cuál de las
  copias pulsar, que deja de importar para la altura: la que se pulsa, la primera, se trae a la vista.

**Probado sin portal, con el código del cambio.** Sobre una página sintética con la forma medida (tarjetas de 400 px
cada 420, el «Book» con su raíz shadow 140 px debajo del borde de la tarjeta, una ventana de 1449 px), en el Chromium
de Playwright y sin red:

| La tarjeta 7, antes | La página se movió | El «Book» quedó a | `_mk_pulsar_book` |
|---|---|---|---|
| Entera, a 300 px | 0 px | 441 px | lo pulsó, un clic |
| A medias por arriba, a −100 px | −100 px (la pega al borde de arriba) | 141 px | lo pulsó, un clic |
| A medias por abajo, a 1300 px | 251 px (la pega al borde de abajo) | 1190 px | lo pulsó, un clic |
| Fuera, arriba, a −1500 px (como el 01-10) | −2024 px (la centra) | 665 px | lo pulsó, un clic |
| Fuera, abajo, a 2600 px | 2076 px (la centra) | 665 px | lo pulsó, un clic |
| Fuera, arriba, y sin caja propia (`display: contents`) | −2149 px | 664 px | lo pulsó, un clic |

La última fila importa porque los estilos de `mc-card` no viajan en el HTML guardado: si la tarjeta no tuviera caja
propia, Playwright la trae igual.

## La tilde y la ñ en la lista de MAERSK

`_mk_sugerencias` arma el prefijo con `_mk_plano`, la misma función con que la regla compara lo escrito con cada
sugerencia: sin tildes, la «Ñ» como «N» y con los espacios de a uno. Otra letra fuera de ASCII se cae, como antes.

- **Hasta ahora**, la letra con tilde y la ñ se caían: con una de ellas entre la segunda y la quinta letra, el prefijo
  no estaba en ninguna sugerencia, y la fila quedaba NO ENVIADA en ese campo («PEÑA ALFA» esperaba «PEA A»). Con la
  letra con tilde en la primera, la lista se reconocía igual.
- **Lo que se escribe en el campo no cambia:** sigue con sus tildes.
- **La sugerencia se mira como viene:** en las 6 listas de MAERSK de `logs/`, ninguna de sus 119 opciones trae una
  letra fuera de ASCII.

## COSCO y «CL»

`_cosco_puerto_de_la_celda` quita al final el país, «CHILE» o «CL», las veces que venga: «CORONEL CL», «Coronel - CL»
y «CORONEL CHILE CL» buscan «Lirquen», como «CORONEL, CHILE». En medio del nombre, el país queda. Usa la misma tupla
(`PAIS_DEL_PUERTO`) con que `_puerto_de_carga` decide si la fila trae el puerto, y esa decisión no cambia: en las 89
filas con cabecera de `logs/`, de las seis navieras, dice lo mismo.

## Las 5 capturas del encargo 42: nota

`msc_f6_origen`, `msc_f6_destino`, `cosco_f8_origen`, `hmm_f9_origen` y `hmm_f9_destino`, del 30-09 a las 15:21. Antes
de cerrarlas volví a medir su HTML:
- en las 5, el JavaScript del propio programa (el de `_msc_puerto`, el de `_hmm_autocomplete` y `_JS_COSCO_AUTO_PICK`),
  corrido sin pulsar sobre el HTML guardado, elige la sugerencia que `log.txt` dice que se pulsó;
- las de MSC y HYUNDAI están en la página, y la de COSCO, en su marco 2.

Lo que la captura mostraba en pantalla no se mide sin mirarla: el OCR no lo confirmó, y el HTML dice que la lista
estaba, con esa sugerencia.

## FRENA SI

**Traer la tarjeta a la vista no necesita un clic ni una tecla.** `scroll_into_view_if_needed` desplaza la página
desde el protocolo del navegador (`DOM.scrollIntoViewIfNeeded`), sin eventos de mouse ni de teclado.

**Ninguna reserva guardada que llegó a la guarda cambia de estado.** Las conté con la regla del encargo 42: de las 103
reservas de `logs/` (0 sin estado final), 71 llegaron a la guarda: CMA-CGM 11, COSCO 19, MSC 13, ONE 10, HYUNDAI 12 y
MAERSK 6.
- **El «Book».** De las 6 de MAERSK, 5 (las del 21-09) pulsaron el «Book» de su salida, y 1 (la del 24-09) no llegó a
  uno: la nave no estaba. Con el cambio, toda reserva que pulsó su «Book» lo sigue pulsando, porque después de traer la
  tarjeta su «Book» queda siempre a más de 100 px del borde de arriba, mientras la tarjeta mida menos que la ventana
  (medido: 400 a 422 px, frente a 1449 a 1606):
  - si la tarjeta se veía entera, no se mueve: su borde de arriba está en la ventana, y el texto del «Book» va de 93 a
    100 px más abajo que el de «Route & other details», que a su vez va debajo del encabezado de la tarjeta, con sus
    fechas y su nave;
  - si se veía a medias por arriba, Playwright la pega al borde de arriba, con la misma cuenta;
  - si se veía a medias por abajo, la pega al borde de abajo, y queda entera;
  - si estaba fuera, la centra.

  En la página sintética de arriba, desde las cinco posiciones, el «Book» quedó entre 141 y 1190 px. El código que
  corrió el 21-09 no está en git (el repo empieza el 23-09), así que esta cuenta no depende de cómo pulsaba entonces.
- **El prefijo.** Cambia solo si la ciudad trae una letra con tilde o una ñ entre sus primeros caracteres: 0 de las 34
  ciudades que escribió MAERSK traen una letra fuera de ASCII.
- **«CL».** Cambia solo lo que COSCO busca, y solo si el puerto termina en «CL»: 0 de sus 24 reservas cambian. En 23,
  `log.txt` anota lo que escribió en «Origin City», y es lo que da `9995517`.

Las otras dos de MAERSK que llegaron a la elección de la nave no llegaron a la guarda: la del 27-09 a las 21:15 pulsó su
«Book» y se detuvo en la revisión, y la del 01-10 es la que no lo pulsó.

## Lo que vigila el cambio

- En `test_clics.TestMaersk`, cuatro pruebas nuevas:
  - `test_trae_la_tarjeta_a_la_vista_antes_de_mirar_el_book`: con una página falsa que anota cada acción, primero trae
    la tarjeta, después mira la altura y pulsa una vez; a 80 o a 100 px no pulsa; y las otras tres formas del porqué;
  - `test_el_book_que_no_pudo_pulsar_vuelve_con_la_salida_y_el_porque`;
  - `test_el_book_sin_pulsar_queda_no_enviada_con_evidencia`;
  - `test_el_book_sin_pulsar_no_sigue_por_la_nave_que_no_esta`.
- Las fotos de `_mk_elegir_nave` pasan a su cuarto valor: 8 comparaciones y la línea que lo recibe.
- En `test_evidencia.TestListaDeSugerencias`, `test_maersk_reconoce_la_lista_con_una_tilde_en_las_primeras_letras`.
- En `test_clics.TestCosco.test_puerto_de_carga_sin_sugerencia_corta`, 5 celdas con «CL» y 4 normalizaciones más.
- 13 mutaciones nuevas, y 9 reancladas en las líneas que cambiaron, con las mismas pruebas.
- **La compuerta, en dos pasos.** En una copia de `9995517` con el cambio: la suite, 568 pruebas, OK, en 669 s (1
  saltada: la que necesita los generadores, que no están en el repo); y el censo de `TestMaersk` (145 mutaciones),
  `cosco-origen` (20) y `mk-prefijo` (2), y todas muerden. En la raíz, lo mismo: 568 pruebas, OK, en 625 s, el mismo
  censo, y 0 cambios en los 4122 originales fotografiados.
- **El censo completo, sobre `5c6ff4b`:** 1681 mutaciones y 2017 pares mutación-prueba, y los 2017 muerden; 0 pruebas
  sin mutación y 0 cambios en los originales, en 77 minutos.

## Re-medir

Todo corre desde `scratchpad\e46`, en Git Bash, después de `source entorno_e46.sh` (`TMPDIR`, `TEMP` y `TMP` dentro
de la carpeta), con `python3.13`. Ningún script imprime valores de la planilla ni de la cuenta.

| Número | Script |
|---|---|
| Carpetas de `logs/` | `python3.13 corridas.py 20260901` |
| Las reservas que llegaron a la guarda, y qué cambia en cada una | `python3.13 freno_e46.py` |
| Las opciones de las listas de MAERSK con letras fuera de ASCII | `python3.13 listas_tildes.py` |
| Alto de la ventana y «Book» de «Select sailing» (OCR) | `python3.13 ocr_mk46.py` |
| El «Book» dentro de su tarjeta (OCR) | `python3.13 ocr_etiquetas_mk.py` |
| La tarjeta traída a la vista y `_mk_pulsar_book`, sobre la página sintética | `python3.13 alineacion_scroll.py` |
| Las 5 capturas del encargo 42 | `python3.13 cinco_capturas.py` |
| Cada log, con la máscara | `python3.13 ver_log.py <AAAAmmdd_HHMMSS> [desde] [hasta] [regex]`; su control, `python3.13 control_mascara.py` |
| La suite y el censo | `bash precenso.sh <etiqueta> <filtros…>`, `bash gate.sh <etiqueta> <filtros…>`, `bash censo.sh` |

## NO retroceder

- **La tarjeta se trae a la vista antes de mirar la altura del «Book»:** mirada antes, una tarjeta que quedó arriba de
  la ventana nunca se pulsa.
- **Un «Book» que no se pudo pulsar no sigue por la rama de la nave que no está:** el motivo diría que la nave no está.
- **Un solo clic en el «Book»:** si falla, no se prueba el otro elemento del mismo control.
- **El prefijo de MAERSK, sin tildes; y COSCO, sin «CL» al final:** son tus decisiones.

## Defectos de instrumento que me cacé

- **La máscara dejó pasar el nombre de una nave del 21-09.** La planilla de esa corrida ya no está, y la línea «nave
  seleccionada (locator jerarquía): …» no la tapaba. Salió solo en una salida de herramienta de esta sesión, no en un
  archivo ni en el informe. Ahora la máscara suma la cabecera y la nave elegida de cada `log.txt`, y su control
  enmascara las 5 líneas de ese día.
- **Mi sonda del freno contaba el «Book» pulsado solo con la forma nueva del log** («nave seleccionada:»), y daba que
  ninguna de las 6 de MAERSK que llegaron a la guarda había llegado a un «Book»: las 5 del 21-09 lo anotan con la forma
  vieja. La corregí antes de usar el número.
- **El OCR lee también palabras «Book» que no son de una tarjeta,** en otra columna de la pantalla; las separé por su
  columna.
- **Una prueba nueva miraba todo el `log.txt` de su corrida,** que otras pruebas de la misma clase también escriben, y
  falló por sus líneas. Ahora mira solo su última línea.
- **El script de las pruebas escribía un archivo antes de comprobar el largo de las líneas del siguiente,** y lo dejaba
  a medias en la copia. Cada intento siguiente se hizo sobre una copia nueva.
- **La herramienta Bash cambió las barras invertidas de un script de ajuste;** lo hice con Edit.
- **Iba a dejar como riesgo que una tarjeta sin caja propia no se pudiera traer,** por lo que recordaba del código de
  Playwright. Medido en la página sintética, se trae: salió del residual.

## Premisas del encargo que se matizaron

- **«Medido: … la tarjeta había quedado arriba»:** lo medido es la ventana de después y el código; la altura del «Book»
  en ese instante no se guarda. La geometría de hoy lo hace muy probable, pero no es una medición del botón.
- **«Una tilde o una ñ en las primeras letras»:** fallaba entre la segunda y la quinta; en la primera, la lista ya se
  reconocía.
- **«El HTML de cada una trae la lista con la sugerencia marcada»:** se confirmó al re-medirlo, con la sugerencia que se
  pulsó. En HYUNDAI no es un `li` (0 `li` con su texto), y el programa la encuentra igual.

## Residual

| Qué | Por qué no se hizo | Se reabre si |
|---|---|---|
| Que pulsar el «Book» después de traer la tarjeta funcione en el portal | Este encargo no abre portales | Corres la fila con el lanzador de prueba: `log.txt` dice «nave seleccionada» o el motivo nuevo |
| Detener la corrida justo mientras trae la tarjeta o pulsa el «Book» deja la fila NO ENVIADA, no DETENIDO | Es una fracción de segundo; ya pasa así en el origen, el destino y «Review booking» de MAERSK, que atrapan la falla | Lo decides |
| CMA arma su prefijo como MAERSK hasta hoy: la letra con tilde y la ñ se caen (`_cma_puerto` y `_cma_entrega`) | Tu decisión fue para MAERSK | Lo encargas |
| Una sugerencia de MAERSK con tilde en sus primeras letras no se reconocería | 0 de las 119 opciones guardadas traen una letra fuera de ASCII | Una fila con tilde queda NO ENVIADA con «una sugerencia para «…»» |
| Si MAERSK encuentra una ciudad escrita con tilde | Se sigue escribiendo con sus tildes; 0 de las 34 escritas las traen | Lo mismo |

## Reglas de método aplicadas

`metodo-ciclo` v15, con las reglas permanentes de `~/.claude/CLAUDE.md`:
- **Todo salto silencioso lleva contador:** 28 carpetas y 0 que no calzan; 103 reservas y 0 sin estado final; 44
  capturas y 2 sin «Book» legible; 6 listas y 119 opciones; las 18 mutaciones de otra forma, que mi chequeo de anclas
  no mide, las mide el censo.
- **Control positivo que aborta:** la máscara (con la línea del 21-09), el OCR, los controles sintéticos de cada sonda,
  lo que COSCO escribió el 01-10 y `cosco_f8_destino`, la lista que el OCR sí confirmó.
- **El negativo tiene que morder:** el censo filtrado y el completo.
- **Todo registro es una hipótesis:** las 5 capturas se cerraron después de re-medirlas, y el «medido» del encargo
  sobre la altura del «Book» quedó como lo que es.
- **Re-medir contra HEAD; fuente única** (`_mk_plano` para el prefijo, `PAIS_DEL_PUERTO` para COSCO); **el cambio y su
  guardián, en la misma operación.**
- **Frenar si la decisión es de negocio; lo que está fuera del encargo se propone:** CMA, y lo que pasa al detener.
- **Todo entregable declara su base:** la primera línea.

**Choques:** ninguno entre las reglas. Los agentes que pide ECC no se lanzaron: una revisión del cambio por un
subagente, en un clon dentro de la carpeta del encargo, queda a tu decisión.

## Lo que dio en el repo

- `5c6ff4b` fix(maersk): el «Book» de la salida elegida, con su tarjeta a la vista; si no se pulsa, NO ENVIADA;
- y el de este informe, con `CLAUDE.md` al día.

El push lo haces tú. Los comandos, con el hash esperado, van en el mensaje final del encargo: este informe va dentro
del commit y no puede citar su propio hash.
