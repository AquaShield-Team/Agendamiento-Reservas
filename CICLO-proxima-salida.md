# CICLO · La corrida «todas» con candado cerrado y la regla de la próxima salida

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-25 · **Método:** skill `metodo-ciclo` v13 ·
**Base:** `71eff24` (último de código: `135e765`) · **Commits** (locales, sin push; el repo no tiene remoto): uno por
naviera cambiada, `384d3ce` (COSCO), `8927e1f` (MSC), `16d3583` (ONE) y `86d6e63` (MAERSK), y el de este informe.

> Sin datos reales. La corrida se midió en su carpeta de `logs/` y en solo lectura, con sondas que imprimen conteos,
> estados y textos del programa, etiquetas de interfaz y desfases en días; las naves, los puertos, las fechas y los
> contratos nunca salen. La planilla del panel se leyó con el lector del programa y nunca se guardó.

## El candado aguantó

La carpeta de corrida más reciente es la corrida «todas» del 2026-09-25 a las 13:47. Tiene 91 archivos y un `log.txt`
de 321 líneas, y es posterior a `71eff24`, que es de las 13:34.

- Estados: 3 OK-EJEMPLO, 2 REVISAR y 1 NO ENVIADA. **0 EMITIDA y 0 ENVIADA.**
- 0 líneas de la rama de emisión y 0 archivos `_confirmado`.
- Los 3 que llegaron a su guarda (MSC, CMA y HYUNDAI) dicen «Me DETENGO» y dejaron su `_guarda.*`.

El primer freno no se cumplió: ningún clic en el envío final.

## Las seis navieras

| Naviera (fila) | Estado | Dónde terminó | Avisos |
|---|---|---|---|
| ONE (5) | REVISAR | Itinerarios: la nave de la fila no está entre las 32 tarjetas | Ninguno. La espera nueva vio las 32 tarjetas en 4,5 s. «NO encontré la nave por el nombre exacto» |
| MSC (10) | OK-EJEMPLO | Summary, su guarda | Ninguno |
| CMA (15) | OK-EJEMPLO | «Envío de la reserva», su guarda | ⚠ «No pude confirmar la ruta»: «Validar ruta» sin respuesta en 12 s, como el 25 a las 00:29 |
| COSCO (20) | NO ENVIADA | Lista de itinerarios: 2 calzan con la nave | ✗ «la fila no trae día de carga» |
| HYUNDAI (25) | OK-EJEMPLO | Review & Book, su guarda | Ninguno a la vista, pero armó la reserva con **otra nave** (hallazgo 1) |
| MAERSK (30) | REVISAR | «Select sailing»: la nave de la fila no está entre las salidas | ⚠ «la fila no trae un día de carga que se entienda, así que busco las salidas desde mañana» |

## Los pendientes

### MAERSK: FRENO, no llegó a la revisión

- Se detuvo en «Select sailing». De las 2 palabras de la nave de la fila, la distintiva aparece 0 veces entre las 4
  salidas de la lista. No hubo revisión, así que el freno de «NO ENVIADA en la revisión porque el portal no avanzó sin
  fecha de retiro» no aplica.
- **La casilla de términos no se puede identificar:** sigue faltando el HTML de la revisión. «El último checkbox»
  sigue como estaba, con su FRENO.
- **Qué falta:** una fila cuya nave esté entre las salidas que MAERSK deja reservar.
- De las 4 salidas, las 3 de mañana tenían vencido el plazo de ingreso («Gate-in deadline», ayer) y no traían «Book».
  Solo la cuarta, a 9 días, se podía reservar.

### COSCO: hecho en `384d3ce`

- **La regla, sobre la lista medida:** los 2 itinerarios de la nave de la fila salen el mismo día, a 3 días de la
  corrida, con distinto transbordo: llegan a los 42 y a los 51 días. La próxima salida empata, así que la reserva sigue
  NO ENVIADA con la lista, ahora por ese motivo y no por el día de carga.
- **Lo que el programa llamaba ETD era el CY Cutoff.** La fila que leía trae una sola fecha, la del cutoff (a 2 días).
  La salida y la llegada van arriba en la tarjeta, como «Sep27 (Sun)», sin año. La regla del encargo 21 (la ETD igual
  al día de carga) comparaba con el cutoff.
- El cambio:
  - la lista lee la salida y la llegada de la tarjeta, con el año deducido por el día de la semana;
  - elige la próxima salida y, si no queda una sola, NO ENVIADA con la lista.

### ONE: hecho en `16d3583`

- **La espera nueva vio las tarjetas:** 32, a los 4,5 s.
- **No llegó a Review Booking:** la nave de la fila no está entre las 32 tarjetas. Aparece 0 veces entera, 0 sin el
  viaje y 0 el viaje solo.
- El cambio, sobre la tarjeta medida (clase `ResultCard_card__*`):
  - su salida (elemento con clase `textStyle-h5`), su nave y su único botón de reserva;
  - se elige la próxima salida entre las tarjetas de la nave;
  - hasta 8927e1f se pulsaba el botón del elemento más chico que traía la nave, fuera cual fuera su salida.

### MSC: llega a su guarda; hecho en `8927e1f`

- Llegó a Summary, su guarda. En la revisión, la nave de la fila aparece entera.
- **El «hoy + 18 días», medido:**
  - En el código, es el valor por defecto de `_msc_fecha_futura` desde el primer commit, sin comentario ni registro.
  - En la evidencia, el campo de fecha del portal viene con la fecha de hoy y sin mínimo, y solo exige que sea una fecha.
    Ningún texto habla de plazo.
  - Buscando a +18, la lista trajo 27 salidas desde +2 días.
  - **El portal no lo exige:** MSC busca desde hoy, como las demás.
- La regla de la próxima salida se aplica sobre la ETD de cada tarjeta («ETD dd MMM aaaa»). En esta corrida, la nave de
  la fila estaba en 1 de las 27 tarjetas: la regla elige la misma.

### HYUNDAI: llega a su guarda, pero con otra nave

- Llegó a Review & Book, su guarda. **En esa pantalla, «Vessel / Voyage» muestra una nave con la primera palabra de la de
  la fila y otra segunda palabra** (hallazgo 1).
- **La regla, FRENO:** falta el HTML de la lista de naves («Select Vessel»). La corrida solo guardó su captura, así que
  no se puede medir dónde va la fecha de cada salida.

### CMA: llega a su guarda

- Llegó a «Envío de la reserva», su guarda, y en la revisión aparece la nave de la fila.
- **La regla, FRENO:** falta el HTML de «Route choices» con sus opciones. Los HTML guardados (el panel Reefer, lo guardado y
  la guarda) traen solo los botones «Seleccionar» y «Deseleccionar» juntos, sin tarjetas ni fechas.

## La regla de la próxima salida

Decidida por Marcelo: las reservas se emiten el día en que se corre el programa; entre varias salidas de la nave de la
fila se reserva la próxima a partir de hoy; si quedan opciones empatadas, NO ENVIADA con la lista guardada, y nunca se
elige a ciegas.

**Cómo quedó** (fuente única, en `AQUASHIELD.py`):
- `_desde`: hoy, o el día de carga si la fila lo trae y es posterior. MSC mira también el de retiro.
- `_proxima_salida`: de las salidas de la nave, la próxima desde esa fecha. Si no queda una sola, dice por qué:
  - «empate»;
  - «sin-fecha», si alguna no trae una fecha que se pueda leer;
  - «ninguna», si todas ya salieron.
- `_por_que_sin_salida`: ese motivo en palabras, para el NO ENVIADA.

**Dónde se aplica:**

| Naviera | Qué se ordena | Qué cuenta como salida | Si no queda una sola |
|---|---|---|---|
| COSCO | la salida de la tarjeta, «Sep27 (Sun)» | cada itinerario con la nave | NO ENVIADA con `cosco_f<fila>_itinerarios` |
| MSC | la ETD de la tarjeta | las tarjetas con la nave y su «Select» | NO ENVIADA con `msc_f<fila>_itinerarios` |
| ONE | la primera fecha `textStyle-h5` de la tarjeta | las tarjetas con la nave y un solo botón de reserva | NO ENVIADA con `one_f<fila>_detenida` |
| MAERSK | «Departure» de la salida | las salidas con la nave y un solo «Book» | NO ENVIADA con `mk_f<fila>_detenida` |
| HYUNDAI y CMA | — | — | FRENO: falta el HTML de su lista |

**Cuánto empata**, medido en las listas guardadas de esta corrida:
- **ONE:** los 7 días de salida tienen de 4 a 8 tarjetas, casi siempre de la misma nave. Son la misma salida con otro
  transbordo, así que la regla empata.
- **COSCO:** los 2 días de salida tienen 2 tarjetas cada uno, de la misma nave: también empata.
- **MSC:** 27 tarjetas en 27 días distintos, sin ningún empate.
- **MAERSK:** las 3 salidas de mañana, de la misma nave, no traen «Book» y no cuentan; la cuarta, sí.

**Con la regla tal como está, ONE y COSCO quedan NO ENVIADA casi siempre.** Desempatar entre transbordos de la misma
salida es decisión tuya (hallazgo 4).

**Lo que interpreté**, y cambia si decides otra cosa:
- Si la fila trae día de carga, cuenta desde ese día. La planilla hoy no lo trae, así que en la práctica es desde hoy.
  ONE cuenta siempre desde hoy: nunca usó el día de carga.
- Solo cuentan las salidas que el portal deja reservar: con su «Book» o su «Select».
- Una opción sola se elige aunque su fecha no se pueda leer; una sola que ya salió, no.

## Hallazgos nuevos (se reportan; no se implementan)

1. **HYUNDAI armó la reserva con otra nave.** `_JS_HMM_INDICE_NAVE` acepta una tarjeta con todas las palabras de la
   nave **o solo con la primera**, y pulsó la primera tarjeta que traía esa palabra.
   - La revisión muestra una nave con la primera palabra de la fila y otra segunda.
   - Con el candado cerrado no pasó nada. Con la emisión abierta, habría reservado otro buque.
   - Pedir todas las palabras, como hace MSC, lo arregla; es un cambio chico.
2. **ONE tiene el mismo patrón, latente.**
   - Si la nave de la planilla termina en una palabra de 3 a 10 letras o dígitos, el programa la toma por el viaje y
     busca también el resto por separado.
   - Con una nave «ONE NOMBRE», buscaría «ONE» solo, y eso calza con cualquier tarjeta que lo traiga en su texto.
   - `16d3583` conservó tal cual esa forma de calzar.
3. **MAERSK busca desde mañana** («Select tomorrow») cuando la fila no trae fecha. Con «las reservas se emiten el día en
   que se corre el programa», una salida de hoy no entra en la búsqueda. No se cambió: el encargo pedía medir solo el
   «+18» de MSC.
4. **Con la regla, ONE y COSCO empatan casi siempre:** son la misma salida con distinto transbordo. Un desempate posible
   es el menor tránsito, que las dos tarjetas traen, pero es decisión tuya.
5. **CMA sigue sin confirmar la ruta:** «Validar ruta» no responde en 12 s, igual que en la corrida anterior.

## Expectativas que cambiaron (antes → ahora)

| Commit | Prueba | Antes | Ahora |
|---|---|---|---|
| COSCO | `test_clics.TestCosco.test_itinerario_por_el_dia_de_carga_nunca_el_primero` | La única con ETD igual al día de carga | Pasa a `test_itinerario_la_proxima_salida_nunca_el_primero`: la próxima desde hoy, o desde el día de carga |
| COSCO | `…TestCosco.test_itinerario_ambiguo_queda_no_enviada_con_evidencia` | Motivos del día de carga | Los de la regla: empate, sin fecha legible, ninguna vigente |
| COSCO | `…TestCosco.test_reservar_cosco_no_toma_el_primero` | `elegido = …`; NO ENVIADA solo con varios | `elegido, motivo = …`; NO ENVIADA siempre que no quede uno; cada itinerario con su salida antes de elegir |
| COSCO | Un solo itinerario que ya salió | Se elegía | No se elige: NO ENVIADA |
| COSCO y MSC | `test_ayudantes.TestFechas`, lectores del día de carga | `_cosco_fecha_fila` y `_msc_fecha_futura` | `_desde` |
| MSC | `test_ayudantes.TestMSC.test_fecha_futura_msc` | Hoy + 18 sin fecha, pasada o a 2 días | Pasa a `test_desde_msc`: hoy, y el día de carga aunque sea a 2 días |
| MSC | `test_evidencia.…test_solo_ahi` | — | Se suma `_msc_salida_ambigua` |
| ONE | `test_clics.PERMITIDOS` (la foto) | («reservar_one», «_JS_ONE_SELECT_NAVE», «ultimo-por-posicion»): 2 | Lo mismo en `_JS_ONE_TARJETAS_NAVE`; se suma («reservar_one», «_JS_ONE_CLIC_TARJETA», «primero-sin-filtro»): 1, ESPECÍFICO |
| MAERSK | `test_ayudantes.TestFechas.test_maersk_avisa_cuando_busca_desde_manana` | Sin fecha o ilegible: ⚠ «la fila no trae un día de carga…» | Pasa a `test_maersk_avisa_solo_si_no_pudo_escribir_la_fecha`: sin aviso; avisa si no pudo escribirla |
| MAERSK | `test_evidencia.…test_solo_ahi` | `_mk_sin_nave` | `_mk_detenida`, que comparten la nave que no está y el empate |

- `test_candado` no cambió en ningún commit, ni la guarda de ninguna naviera.
- No hay clics nuevos antes de la guarda: cada clic es el de antes, sobre la opción elegida.
- La red pasó de 281 a 301 pruebas, de 585 a 640 mutaciones y de 710 a 768 pares:

| Commit | Pruebas | Mutaciones | Pares |
|---|---|---|---|
| `71eff24` (base) | 281 | 585 | 710 |
| `384d3ce` (COSCO) | 287 | 601 | 726 |
| `8927e1f` (MSC) | 291 | 611 | 737 |
| `16d3583` (ONE) | 296 | 625 | 751 |
| `86d6e63` (MAERSK) | 301 | 640 | 768 |

- Mutaciones borradas: 4 de COSCO, que miraban la comparación con el día de carga.
- Mutaciones puestas al día, porque su texto viejo cambió: 2 de COSCO, 2 de MSC y 3 de MAERSK.
- Mutaciones ancladas con más contexto, porque el código nuevo repetía su texto: 2, `cosco-itinerario-sin-lista` y
  `msc-etd-mes-desde-cero`.

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\correr.py --mutaciones --filtro proxima
python tests\correr.py --mutaciones --filtro cosco-
python tests\correr.py --mutaciones --filtro msc-
python tests\correr.py --mutaciones --filtro one-
python tests\correr.py --mutaciones --filtro mk-
python tests\correr.py --todo
```

Las sondas son de solo lectura y viven fuera del repo. Cada una aborta si su control sintético no da lo esperado:
- **El candado:** estados por naviera, «Me DETENGO», líneas de la rama de emisión y archivos `_confirmado`.
- **El log:** cada línea contra las plantillas del programa; lo que no es del programa sale con su largo.
- **Las naves:** la de cada fila sale del log, o de la planilla del panel para HYUNDAI, y nunca se imprime; se cuenta por
  palabra en cada pantalla.
- **Las listas:** en cada una, la tarjeta de cada salida, sus etiquetas y el desfase en días de cada fecha:
  - COSCO: su «MonDD (Dow)» y su cutoff;
  - MSC: su ETD;
  - ONE: sus `textStyle-h5`;
  - MAERSK: su «Departure», su «Book» y si vive dentro de una raíz shadow.
- **Los empates:** por lista, cuántas tarjetas y cuántas naves distintas por día de salida, con las naves comparadas por
  hash.
- **La fecha de MSC:** los atributos de su campo, su calendario y los textos de plazo.

## NO retroceder (pieza 2)

- **No vuelvas a leer como ETD de COSCO la primera fecha de la fila:** es el CY Cutoff.
- **No elijas la primera ni la última opción de la nave:** `_proxima_salida` es la fuente única. Si no queda una sola, NO
  ENVIADA con la lista.
- **No vuelvas a buscar MSC desde hoy + 18:** el portal no lo exige, y dejaba fuera las salidas de las dos semanas y media
  siguientes.
- **No vuelvas a avisar en MAERSK la falta del día de carga:** en esta planilla es lo normal. Una celda ilegible la avisa
  `_avisar_dia_carga`.
- **No vuelvas a pulsar en ONE el botón del elemento más chico con la nave:** la tarjeta es `ResultCard_card__*`, y su
  botón, el único que trae.

## Premisas del encargo contrastadas (pieza 5)

- **«La carpeta de corrida más reciente»:** confirmada. Existe, es del 2026-09-25 a las 13:47 y corrió con el código de
  `71eff24`.
- **«Naves de ONE y MAERSK tomadas de los itinerarios vigentes del portal»:** refutada para las pantallas que mostró el
  portal. En ninguna de las dos aparece la nave de la fila.
- **«MSC, HYUNDAI y CMA siguen llegando a su guarda»:** confirmada para las tres, pero HYUNDAI llegó con otra nave.
- **«El aviso «la fila no trae día de carga»»:** confirmada en dos lugares: el aviso de MAERSK y el motivo de COSCO.
  Se quitaron los dos.
- **«De dónde sale el «hoy + 18» de MSC»:** del valor por defecto de una función, sin registro. El portal no lo exige.
- **«COSCO, la regla sobre la lista medida»:** aplicada. Empata, y de paso salió que su «ETD» era el CY Cutoff.

## Universo y cobertura (pieza 3)

- **La corrida:** 1 carpeta, con 91 archivos y un `log.txt` de 321 líneas.
  - 315 líneas calzan con una plantilla del programa y 6 no: 5, una tras cada login, y el aviso de MAERSK, que se armaba
    sumando textos. 0 continuaciones.
  - 44 HTML: CMA 15, MAERSK 10, MSC 6, COSCO 5, ONE 4 y HYUNDAI 4.
- **Descartados:** 0 archivos sin leer en todas las sondas.
- **Las listas:** ONE 32 tarjetas, MSC 27, COSCO 4 y MAERSK 5, de las que 1 estaba cargando.
- **No medido:**
  - la lista de naves de HYUNDAI y «Route choices» de CMA: no hay HTML;
  - la búsqueda de MSC desde hoy, en una corrida viva: el cambio es posterior;
  - la visibilidad real: las sondas la infieren del marcado.

## Defectos de instrumento cazados (pieza 4)

1. **Cuatro controles positivos abortaron por un error mío en el caso sintético:**
   - puse las listas de MSC y CMA en un mismo HTML;
   - repetí «Book» en el anfitrión y en su plantilla;
   - supuse una sola fila de HYUNDAI, y CONSOLIDADO trae 5;
   - en MAERSK, la «tarjeta» deducida por un solo «Book» resultó ser el encabezado del sitio.

   En los cuatro casos se corrigió el caso o la forma de medir, antes de leer los números.
2. **La máscara de la sonda de HYUNDAI dejó pasar a la consola el prefijo de un código de viaje.**
   - Se corrigió. Al corregirla, la herramienta Bash cambió `\\` por `\` en un heredoc (ya registrado), la aserción lo
     detuvo sin escribir nada, y la sonda vieja volvió a correr porque no encadené con `&&`.
   - Nada de eso salió de la consola.
3. **El lector del log muestra los valores que están escritos en el código,** como los contratos. Salieron en la consola,
   no en archivos.
4. **Escribí mal el hash del «Hasta» de MSC:** puse `71eff24` y era `384d3ce`. Quedó en `8927e1f` y se corrigió en
   `16d3583`.
5. **El primer gate de COSCO falló:** mis casos nuevos perdieron la hora y el DD-MM-AAAA, y `fecha-sin-hora` y
   `fecha-mes-primero` dejaron de morder. Se agregaron esos casos. Como además edité una prueba con ese censo corriendo,
   el gate se repitió entero.
6. **En Windows, los archivos de salida del censo para `TestMsc` y `TestMSC` son el mismo:** uno pisó al otro. Los dos
   terminaron en 0, y la cifra de `TestMsc` (17 mutaciones y 23 pares) se recontó sobre `8927e1f`.
7. **Dos mutaciones dejaron de calzar una sola vez y una constante quedó repetida:** el prechequeo y un grep lo cazaron
   antes del gate.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| HYUNDAI acepta la nave por su primera palabra | Hallazgo; el encargo pide reportarlo | …decides que pida todas las palabras |
| HYUNDAI y CMA sin la regla de la próxima salida | FRENO: falta el HTML de su lista | …una corrida deja ese HTML, o decides que se guarde |
| ONE y COSCO empatan casi siempre | La regla empata entre transbordos de la misma salida | …decides un desempate |
| MAERSK marca «el último checkbox» de los términos | FRENO: la corrida no llegó a la revisión | …una corrida de MAERSK llega a la revisión |
| MAERSK busca desde mañana | No era parte del encargo | …quieres que busque desde hoy |
| ONE puede calzar la nave por una parte de su nombre | Hallazgo latente: se conservó la forma de calzar | …decides que exija la nave entera |
| CMA no confirma la ruta | El portal no responde a «Validar ruta» | …decides qué hacer sin esa confirmación |
| El día de carga, si alguien agrega la columna, cuenta desde ese día | Mi interpretación | …decides otra |
| CMA y COSCO sin forma medida de confirmación | Nunca llegan a EMITIDA | …una emisión real deja su confirmación |
| Los residuales de `CICLO-cola-cuatro-items.md` y anteriores | No son parte de este encargo | …según cada fila de esos informes |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v13**:
- **PASO 0 con veredicto:**
  - CICLO para COSCO, MSC, ONE y MAERSK;
  - NOTA para CMA y HYUNDAI, que llegan a su guarda;
  - FRENO para la casilla de MAERSK y para la regla en HYUNDAI y CMA.
- **Re-medir contra HEAD antes de diseñar:** la corrida es posterior a `71eff24`, y la base del encargo se verificó
  (281, 585 y 710).
- **Control positivo que aborta:** en cada sonda. Abortaron cuatro, y se corrigieron antes de leer sus números.
- **Todo salto silencioso lleva contador:** 0 archivos descartados; 6 líneas del log sin plantilla, contadas.
- **La unidad la fija el sujeto:** la regla decide por salida, así que se contó por tarjeta y por día de salida, no por
  página.
- **Todo registro es una hipótesis:**
  - el nombre «etd» del código era el cutoff;
  - el «+18» no tenía registro que lo respaldara.
- **El negativo tiene que morder:** censo filtrado en cada commit, y el censo completo al final.
- **Fuente única:** `_proxima_salida`, `_desde`, `_por_que_sin_salida`, `_MESES_EN` y `_mk_detenida`.
- **El cambio y su guardián en la misma operación:** cada cambio con su prueba y su mutación en el mismo commit.
- **Cada reemplazo afirma su viejo una vez, y el EOL se preserva:**
  - el guion de MAERSK afirmó cada texto;
  - el prechequeo cazó 3 textos que calzaban más de una vez;
  - todos los archivos quedaron con 0 CR.
- **FRENAR cuando la decisión es de negocio:** el desempate, la nave de HYUNDAI y buscar MAERSK desde hoy quedan
  reportados, no hechos.
- **Declarar las premisas refutadas:** las naves «vigentes» de ONE y MAERSK.
- **Choque, sin freno:**
  - «un commit por naviera» chocó con corregir el hash de MSC, que fue en el commit de ONE, declarado;
  - los ayudantes compartidos entraron con COSCO, la primera naviera que los usó.

Reglas del módulo:
- casos sintéticos que imitan la estructura medida;
- la sonda de secretos antes de cada commit;
- nada de `logs/` en el repo;
- el nombre del operador en ningún archivo versionado;
- los textos nuevos en español con tuteo.

## Entregable (pieza 8)

Este `.md`, sin renderizar, y `CLAUDE.md` al día.

**Gates** (en cada uno, la sonda de secretos dio 0 sobre el staging; entre paréntesis, mutaciones y pares de cada censo
filtrado, y muerden todos):

| Commit | Suite completa | Censos filtrados |
|---|---|---|
| COSCO, `384d3ce` | 287 en verde, 0 cambios en los originales | `cosco-itinerario` (8 y 9), `cosco-tarjeta` (2 y 2), `cosco-salida` (2 y 2), `cosco-js` (13 y 13), `proxima` (9 y 13), `desde-` (5 y 8), `motivo-` (3 y 3), `TestCosco` (37 y 49), los lectores del día de carga (2 y 2), `fecha-sin-hora` (1 y 3), `fecha-mes-primero` (1 y 3) |
| MSC, `8927e1f` | 291 en verde | `msc-` (39 y 47), `desde-` (9 y 12), `cosco-itinerario-sin-lista` (1 y 1), `TestMsc` (17 y 23), `TestMSC` (4 y 4), `test_solo_ahi` (15 y 31), los lectores (2 y 2), `cosco-tarjeta` (2 y 2) |
| ONE, `16d3583` | 296 en verde | `one-` (52 y 59), `TestOne` (30 y 36), la foto de clics genéricos (27 y 51) |
| MAERSK, `86d6e63` | 301 en verde | `mk-` (17 y 19), `maersk-` (33 y 38), `TestMaersk` (26 y 32), la fecha de salida (1 y 1), `msc-etd` (1 y 1), `test_solo_ahi` (16 y 34), el aviso (2 y 2), la foto (27 y 51) |

- **Censo completo final sobre `86d6e63`:** pasó, en 26 minutos.
  - 301 pruebas en verde, y el control (la copia sin mutar) pasa;
  - 640 mutaciones y 768 pares, y muerden todos;
  - 0 pruebas sin mutación y 0 cambios en los originales.
- **El commit de este informe** solo agrega este `.md` y cambia `CLAUDE.md`, que ninguna prueba lee. La suite
  completa corrió con los dos ya cambiados: 301 en verde y 0 cambios en los originales.

## Veredicto por naviera: ¿lista para una emisión real de prueba?

| Naviera | Veredicto | Qué le falta |
|---|---|---|
| **MSC** | **Casi lista** | Una corrida con candado cerrado con la búsqueda desde hoy (cambió en `8927e1f`), para ver que elige la próxima salida en vivo. Llega a su guarda con la nave de la fila y tiene forma medida de confirmación, así que puede llegar a EMITIDA |
| **CMA** | No | Confirmar la ruta, porque «Validar ruta» no responde, y el HTML de «Route choices» para aplicar la regla. Sin forma medida, tras el envío queda en ENVIADA – REVISAR EN PORTAL |
| **HYUNDAI** | **No** | Que la nave calce con todas sus palabras: en esta corrida armó la reserva con otra nave. Después, el HTML de su lista de naves para aplicar la regla |
| **COSCO** | No | Tu decisión de desempate: la próxima salida de la nave tiene 2 transbordos y queda NO ENVIADA. Sin forma medida, nunca llega a EMITIDA |
| **ONE** | No | Una fila cuya nave esté en la búsqueda, y tu decisión de desempate: cada salida tiene de 4 a 8 transbordos |
| **MAERSK** | No | Una fila cuya nave esté entre las salidas que se pueden reservar, y el HTML de la revisión para la casilla de términos (FRENO) |
