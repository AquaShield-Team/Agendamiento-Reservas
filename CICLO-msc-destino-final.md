# CICLO-msc-destino-final · Encargo 86: MSC con un puerto de descarga y otro destino final

> **metodo-ciclo v39** (recargada al empezar: la sesión venía compactada). Base: `main` en `b39c95c`, árbol limpio. **Dos
> commits:** el cambio (`6667404`) y este informe. **No se subió nada:** el bloque de push está al final. Sin datos de
> clientes: los datos reales del ejemplo (el video, la planilla y la corrida del 23-10) se leyeron en su carpeta, que git
> ignora, y no salió de ahí ningún valor; las pruebas usan nombres inventados.

## Qué se pidió y qué salió

El encargo: que MSC reserve destinos con el puerto de descarga y el lugar de entrega final distintos (el ejemplo del dueño:
un puerto de Tailandia y una ciudad tierra adentro), con la misma lectura que ya usa CMA-CGM; la sugerencia del campo nuevo,
solo si calza sin ambigüedad, y si no, NO ENVIADA; el camino de un solo puerto, igual; prueba y mutación de los dos caminos,
revisión de código, commit sin push. Con su FRENA: si la planilla no deja saber cuál es el puerto y cuál el destino final, si
el campo del portal no se ve en el video, o si el cambio toca otra naviera.

**No cayó en ningún FRENA** (lo medido, abajo): la planilla los trae en dos columnas con su encabezado; el campo se ve en el
video, en «Route Details»; y CMA-CGM no se tocó (su regla se lee desde una prueba).

**Queda una decisión tuya** (al final): la revisión de seguridad marcó como ALTA, de negocio, que la lectura de CMA-CGM separa
también dos maneras de escribir el mismo puerto.

## Paso 0 (medido)

- **La carpeta del ejemplo, `1. pruebas`, está fuera de git:** `git check-ignore` la da por la lista blanca (`.gitignore:6:/*`),
  con 0 archivos seguidos y 0 commits que la nombren (`git log --all`). Trae el video (57 s), la planilla y una carpeta de la
  corrida del 23-10 del equipo de un colega.
- **El video** (`.trabajo/e86/cuadros.py` y `tramo.py`; los cuadros quedan en `.trabajo/e86/cuadros`, sin versionar): un
  cuadro cada 0,5 s (115 leídos, 11 distintos del anterior), y uno por segundo del tramo de los 26 a los 53 s (28). En «Route
  Details», con el puerto de descarga ya elegido, aparece debajo el grupo **Port | Ramp / Barge | Door**; el dueño pulsa
  **Door**, elige **TRUCK** en «Select on-carriage mode» (las opciones: TRUCK, TRUCK/RAIL y TRUCK/BARGE), y en **«Intermodal
  Details - Final destination» › «Destination»** («Enter a Location») escribe el comienzo de la ciudad y elige la única
  sugerencia que queda; «Destination Postal Code» queda vacío; después, «Search Schedule».
- **La planilla** (`.trabajo/e86/planilla.py`; imprime los encabezados y solo los lugares): hoja CONSOLIDADO, 15 filas de MSC,
  con «Puerto Descarga» y «Destino Final» en columnas aparte. 5 filas con el par del ejemplo, 2 con otro par distinto, y 8 con
  el mismo valor en las dos. **La forma calza con la lectura de CMA-CGM:** `tiene_ramp_separado` (en `reservar_cma`) lee
  justamente esas dos columnas, y si difieren, las muestra en log.txt como «PUERTO / DESTINO».
- **Los ids del portal** (una búsqueda en línea, sin script guardado; el fragmento, sin los valores de sus campos, quedó en el
  clon de revisión, `DOM-ruta-msc.html`): de los 994 HTML de MSC guardados (846 en `1. pruebas` y 148 en `logs/`), **165 traen la sección,
  escondida**: los radios `onMode` del puerto de descarga (`#onPort_`, `#onRailBarge_`, `#onDoor_`, cada uno con su etiqueta
  `…Label`), el combobox de Kendo del modo (`#OnCarriageMode`, `data-text-field="Name"`) y el del destino
  (`#BookingCarriage_DestinationLocationId`, que busca en el servidor, `filter: startswith`, desde 3 letras).

### Premisas que se refutaron (o se corrigieron)

- **«YOKOHAMA / TOKYO» no es una celda:** ni la planilla ni el código traen un «X / Y» en una celda. Es como CMA-CGM muestra en
  log.txt las dos columnas cuando difieren (`dest_display`). Su lectura es de dos columnas, y la planilla del ejemplo las trae
  así.
- **La regla de los puertos de MSC no es «solo si calza sin ambigüedad»:** `_msc_puerto` pulsa la más corta de las sugerencias
  que traen la ciudad. El campo nuevo pide una sola, como pidió el encargo; los puertos no cambiaron.
- **Hasta este encargo, MSC escribía el destino final en «Port of Discharge»** (`destino_final or destino_orig`): con el par del
  ejemplo, buscaba la ciudad tierra adentro como puerto.

## El cambio · `6667404`

Todo en `reservar_msc` y sus ayudantes nuevos, antes de la guarda del candado; ninguna otra naviera:

- **`_msc_destino_separado`:** la lectura de CMA-CGM, `(puerto, final)` si los dos traen texto y ninguno está contenido en el
  otro, sin distinguir mayúsculas; si no, `None`. `test_la_misma_lectura_que_cma` corre la regla de CMA-CGM, leída de su
  código con `ast`, sobre los mismos casos.
- **Con los dos:** en «Port of Discharge» va el puerto de descarga (la parte antes de su primera coma, con los espacios de a
  uno), y después `_msc_destino_final`: «Door» por su id y su texto (`#onDoor_Label`, que dice «Door»), «TRUCK» como la única
  opción que lo dice entero, y en «Destination» la ciudad del destino final con la única sugerencia que **empieza por ella como
  palabra entera** (`_msc_calza_el_destino`). Cada paso comprueba lo que dejó (Door activa por la clase de su etiqueta o su radio
  marcado, y el campo del modo a la vista; TRUCK en su campo y «Destination» a la vista; la sugerencia en el campo), con
  lecturas de plazo 1 s; si algo no está, no es uno solo o no queda, `ObjetivoNoEncontrado`: NO ENVIADA, sin pulsar nada más.
  Deja la evidencia de las dos listas (`msc_f<fila>_modo`, `msc_f<fila>_destino_final`). log.txt anota las dos señales de
  «Door», para que tu primera prueba diga cuál se mueve.
- **Antes de «Search Schedule»**, las listas del modo y del destino entran en el cierre de listas abiertas del encargo 82
  (`_msc_buscar_itinerarios(page, reg, listas)`; por omisión, los dos puertos, como antes).
- **Con un solo puerto** (iguales, uno dentro del otro, el final vacío o «-»), nada cambia: el mismo texto en «Port of
  Discharge», la misma línea de log.txt y las mismas listas (`test_los_dos_caminos`).
- **Pruebas:** `test_clics.TestDestinoFinalMsc` (5: la lectura contra la de CMA-CGM, los dos caminos de `reservar_msc`, la
  página con los ids medidos, cada corte sin seguir, y las listas antes de buscar) y `test_planilla.TestDestinoSeparadoMsc` (los
  dos lectores separan las mismas filas). Tres fotos cambiaron a propósito: la llamada a `_msc_buscar_itinerarios`, el caso de
  MSC de `TestSinSugerenciaNoSigue` (con dos puertos, ahora busca el de descarga; se sumó el de uno solo) y la lista de quién
  deja evidencia (`_msc_elegir_de_lista`). **33 mutaciones** `e86-*`, y las anclas de tres viejas (`msc-busca-sin-el-ayudante`,
  `e82-lista-no-se-mira`, `e82-lista-sin-plazo-del-cierre`) pasaron a la llamada nueva.
- **`CLAUDE.md`:** el punto de MSC con su destino final, la lista de las NO ENVIADA y el número de pruebas.

## Las compuertas, sobre el árbol del commit

| compuerta | resultado |
|---|---|
| Censo de mutaciones (`--filtro e86-`) | 33 mutaciones, 37 pares, los 37 muerden; control (la copia sin mutar, 8 pruebas) pasa; 1.006 pruebas, 0 sin mutación; foto de los originales sin cambios; `RESULTADO: OK`, exit 0 |
| Censo de las mutaciones viejas que cambiaron de ancla (`--filtro e82-lista` y `--filtro msc-busca`) | 11 mutaciones y 13 pares, y 5 mutaciones y 6 pares: todos muerden; foto sin cambios; `RESULTADO: OK`, exit 0 en los dos |
| Suite completa | `Ran 1006 tests in 2006.187s · OK`, foto sin cambios, `RESULTADO: OK`, exit 0 (con el tope de la corrida subido a 3.600 s: con el de 1.200, se habría cortado) |
| Sonda de secretos | 0 con `--dry-run` y 0 después del `git add` |
| Guarda de datos (hook pre-commit) | 0 hallazgos en los 124 archivos que se commitean |
| Guarda de datos sobre los mensajes de los commits | 1 en cada uno: la línea `Co-Authored-By`, la dirección pública de atribución, como en los commits de antes (no es un dato) |

El primer censo, antes de las revisiones, dio los 27 pares de entonces mordiendo, pero `FALLA` por la foto de los originales:
755 cambios, de una corrida real del panel en el mismo rato y de la carpeta del worktree de un revisor (abajo, «Lo que salió
mal»). Los censos y la suite de esta tabla corrieron con el equipo sin otra corrida del panel y sin worktrees: foto sin
cambios.

## Revisiones (Opus, en un clon sin remoto dentro de la carpeta del encargo, de a una)

**Código — APROBADO:** 0 críticos, 0 altos, 3 medios, 6 bajos. Corrió 60 pruebas y el censo en el clon (27 de 27 pares).
- Corregidos: el medio 1 (Door se comprobaba con el radio, que Knockout puede no marcar: lo había visto yo leyendo el HTML y lo
  confirmó), el medio 3 (la ciudad, como palabra entera), el bajo 5 (plazos de las lecturas), parte del 6 (la coma del puerto y
  los clics que fallan, con su prueba) y el 9 (el docstring de la evidencia y los nombres del ejemplo).
- No corregidos: el medio 2 (es la decisión de abajo), el bajo 4 (un comodín en «Puerto Descarga» separa y corta en el portal:
  igual que CMA-CGM), el 7 (los textos del cierre de listas dicen «el puerto elegido»: cambiarlos cambia el log del camino de un
  solo puerto), el 8 (el detalle de «lista para emitir» no dice que va con destino final: su texto lo fotografía
  `test_candado`).

**Seguridad:** 0 críticos, 1 alto (de negocio), 4 medios, 4 bajos. El candado, sin hallazgos: nada nuevo llega al botón final,
y `test_candado` pasa sin tocarse. Corrió 78 pruebas.
- Corregidos: el medio 1 (la sugerencia tiene que **empezar** por la ciudad, con un borde de palabra de cualquier alfabeto:
  «PARANA» no calza con «PARANAGUA, PARANA, …»), el medio 3 (el puerto separado, con los espacios de a uno: un salto de línea en
  la celda sería la tecla Enter al escribirlo) y el bajo 2 (los nombres de prueba que conservaban pedazos del par real).
- No corregidos: el alto 1 y la parte de «-» del medio 2 (la decisión de abajo); el resto del medio 2 (con un texto que no es un
  puerto en «Puerto Descarga», la regla de `_msc_puerto` pulsa la más corta que lo trae: es la regla de los puertos, que el
  encargo no cambia); el medio 4 (nada comprueba en «Summary» que la reserva siga con Door y su destino: lo mide tu primera
  prueba en el HTML de la guarda); y los bajos 1, 3 y 4 (residual).

## Decisiones que tomé solo

| Decisión | Por qué | Cómo deshacerla |
|---|---|---|
| «Door» y «TRUCK» | Así lo hizo el dueño en el video; hay también «Ramp / Barge» y TRUCK/RAIL o TRUCK/BARGE | `MSC_DESCARGA_A_PUERTA` y `MSC_EN_CAMION` |
| El destino, solo con una sugerencia que empieza por la ciudad como palabra entera | El encargo pide «sin ambigüedad»; el servidor filtra por «empieza por» | `_msc_calza_el_destino` |
| «Door» activa por la clase de su etiqueta o por su radio | Su clic lo maneja Knockout, que por omisión le quita al navegador su acción: el radio puede no marcarse | La condición en `_msc_destino_final` |
| CMA-CGM no se toca: la regla vive en las dos, y una prueba las compara | Unificarla en una función es tocar CMA-CGM, que el encargo frena | Mover `tiene_ramp_separado` a `_msc_destino_separado`, con tu visto bueno |
| El puerto separado, con los espacios de a uno; el de un solo puerto, como estaba | El camino de un solo puerto no cambia (el encargo) | El `" ".join(...split())` del puerto |
| Lecturas con plazo de 1 s en las comprobaciones | Sin plazo, cada lectura podía esperar 30 s, y diez vueltas, unos 5 minutos | Quitar `timeout=1000` |
| El ejemplo, sin nombres de lugares en el código y en `CLAUDE.md` | Es una ruta de un embarque real en un repo público | — |
| El tope de la suite, 3.600 s | Con el equipo cargado, la corrida pasa los 1.200 s (encargo 85) | Correr `tests/correr.py` tal cual |

## Lo que salió mal, y me toca a mí

- **Lancé la revisión de código con su worktree mientras corría el primer censo:** el arnés creó `.claude/worktrees` en la raíz,
  y la foto de los originales lo contó (1 de sus cambios). Los otros 754 eran de una corrida real del panel en el mismo rato (a
  las 10:44, HYUNDAI, 3 reservas, en modo prueba: no la lancé yo, no pasó por MSC y no corrió el código nuevo), que podó HTML
  viejos de `logs/` y abrió Chrome con su perfil. Ese censo dio 27 de 27 pares que muerden, pero «FALLA» por la foto; el que
  vale es el final, sin worktrees.
- **El árbol vivo tenía el cambio sin commitear** mientras esa corrida real abría el panel. No tocó MSC, pero si hubiera
  armado una fila de MSC, habría corrido código sin revisar.
- **Un comando con un `cd` de más:** la guardia lo frenó antes de correr.
- **Las anclas de tres mutaciones, con la herramienta Bash:** juntó los pares de barras invertidas, el script buscó otra cosa y
  su `assert` lo frenó sin escribir nada; lo rehice desde un archivo.
- **Dos mutaciones que no iban a morder** (una equivalente, `e86-separa-sin-final`, y la primera versión de
  `e86-modo-sin-comprobar`): las saqué o corregí antes de correr el censo. Y un ancla que también estaba en MAERSK
  (`if textos and textos == anterior`), que vio mi comprobación de «una sola vez».
- **Una prueba comprobaba las líneas del log de otra corrida** (reasigné `log` antes del bucle); la vio la corrida de las
  pruebas.

## Re-medir

Con el Python de la Tienda (el `python` del PATH no trae playwright ni openpyxl) y el temporal en una ruta sin espacios:

```bash
python tests/correr.py
python tests/correr.py --mutaciones --filtro e86-
cd tests && python -m unittest test_clics.TestDestinoFinalMsc test_planilla.TestDestinoSeparadoMsc
```

- Los ids del portal: buscar `Intermodal`, `onDoor_`, `OnCarriageMode` y `BookingCarriage_DestinationLocationId` en los HTML de
  MSC de `logs/` (de la guarda o de las sugerencias del destino): 165 de 994 los traían.
- La planilla del ejemplo: `.trabajo/e86/planilla.py` (sin versionar; imprime encabezados y lugares, nunca otra columna).

## NO retroceder

- **Con un solo puerto, el camino de siempre:** el destino en «Port of Discharge», la misma línea de log.txt y las listas de los
  dos puertos (`test_los_dos_caminos`, y las mutaciones `e86-nunca-separa` y `e86-buscar-sin-sus-listas`).
- **El destino final, solo con una sugerencia que empieza por la ciudad como palabra entera:** nunca la primera de varias, ni la
  que la trae en otro lugar.
- **Cada paso comprueba lo que dejó y corta sin seguir:** ningún clic después de un corte (`test_cada_paso_corta_sin_seguir`
  compara la lista entera de lo que se hizo en la página).
- **La regla de separación es la de CMA-CGM:** si cambia en una, la prueba compara las dos y cae.

## Residual

- **No está probado en el portal:** que «Door» se active con el clic en su etiqueta, que «TRUCK» quede, que «Destination»
  traiga una sola sugerencia para la ciudad del ejemplo, ni que la salida y la reserva sigan con el destino final hasta la
  guarda. Lo mide tu prueba en modo prueba: log.txt dice las dos señales de «Door», y quedan las evidencias `msc_f<fila>_modo`,
  `_destino_final`, `_guarda`.
- **El otro par de la planilla** (2 filas) ahora también se separa; si el portal sugiere su destino final, no está medido. Y la
  regla no distingue otro puerto de una puerta tierra adentro: el modo es siempre «TRUCK».
- **Nada comprueba en «Summary»** que la reserva siga con Door y su destino (revisión de seguridad, medio 4); y el detalle de
  «lista para emitir» no dice que va con destino final (revisión de código, bajo 8): los dos son propuestas.
- **Un salto de línea en la celda de un puerto, en el camino de un solo puerto,** sigue llegando a `type()` como antes (pasa
  también en el puerto de carga); se corrigió solo en el puerto separado, porque el otro camino no cambia.
- Los bajos de seguridad: el motivo repite textos del portal y de la planilla sin quitar caracteres de control (patrón que ya
  existía); «una sola» se mide entre las sugerencias a la vista (si el servidor corta la lista, no se sabe); y la consola, con
  «Puerto Descarga» vacío, toma la columna D por su posición (ya era así).
- La regla de separación vive en dos lugares (MSC y CMA-CGM); la prueba las compara, pero no es una sola fuente.

## Lo que decides tú

**¿La separación compara los nombres tal como vienen o normalizados?** (revisión de seguridad, alto 1, y la parte de «-» del
medio 2.) Con la lectura de CMA-CGM, que es la que pediste, se separan también dos maneras de escribir el mismo lugar:
«SHANGHAI, CN» y «SHANGHAI, CHINA», un espacio antes de la coma, dos espacios, «HAIPHONG» y «HAI PHONG». Separar, en MSC, es
armar un tramo en camión hasta esa ciudad; si «Destination» trae una sola sugerencia, la fila queda «lista para emitir» con
entrega a puerta. Y «-» en «Puerto Descarga» separa y corta en el portal, cuando en «Destino Final» cuenta como vacío.
- (a) Dejarla así, igual a CMA-CGM (hoy).
- (b) Comparar las ciudades normalizadas (la parte antes de la coma, espacios de a uno, sin tildes ni signos, «-» como vacío)
  en MSC **y en CMA-CGM**: toca CMA-CGM.
- (c) Normalizar solo en MSC: deja de ser la misma lectura.
- Aparte, en cualquiera: que el panel marque antes de correr las filas que irán con destino final aparte, como las de otro
  contenedor.

## El push (no se subió nada)

Los dos commits, de `main`, con el correo noreply de autor y de committer. Antes de subir, en una consola:

```bash
git -C "C:\dev\Agendamiento Reservas" log origin/main..main --format="%h %ae %ce %s"
```

Tiene que mostrar solo el correo noreply en las dos columnas (van también los commits de los encargos 84 y 85, si no los
subiste). Después:

```bash
git -C "C:\dev\Agendamiento Reservas" push origin main
git -C "C:\dev\Agendamiento Reservas" rev-parse main
git -C "C:\dev\Agendamiento Reservas" ls-remote origin refs/heads/main
```

Los dos hashes tienen que ser iguales. **`estable` no se movió:** el cambio les llega a los colegas solo cuando la avances
tú, después de probar MSC en modo prueba.

## Declaración de método

**metodo-ciclo v39** (recargada al empezar: la sesión venía compactada). Se aplicó: paso 0 medido, con su universo (los
cuadros, las filas, los 994 HTML); los FRENA mirados antes de tocar código; el cambio y su guardián en el mismo commit, con
mutaciones que muerden y su control; las revisiones de código y de seguridad (Opus), en un clon sin remoto, de a una; el censo y
la suite sobre el árbol del commit; la sonda de secretos y la guarda de datos sobre lo commiteado y sobre los mensajes; ningún
push. Lo mecánico (los censos y la suite) lo corrió `ayudante-mecanico` con el envoltorio de salida literal, y leí cada
archivo; las pruebas sueltas y las sondas las corrí yo (son de segundos). **La lista de tareas no se llevó:** esta sesión no
tiene la herramienta. No se escribió en la memoria de Claude Code.
