# CICLO · La cola de cuatro ítems: día de carga, espera de ONE, guardado de credenciales y el nombre fuera del repo

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-25 · **Método:** skill `metodo-ciclo` v13 ·
**Base:** `ecbdfaa` (último de código: `72f932c`) · **Commits** (locales, sin push; el repo no tiene remoto): uno por
ítem, `e16beb6`, `45f2171`, `9710ae2` y `135e765`, y el de este informe. **La rama se llama `main`** desde este encargo.

> Sin datos reales. La planilla, `logs/` y `config.json` se midieron en solo lectura, con sondas que imprimen conteos,
> formas y nombres de campo del código. El nombre del operador no se escribe en ninguna parte: las sondas lo leen de
> `config.json` al correr y lo enmascaran como «T1» y «T2».

## Los cuatro ítems

| # | Ítem | Veredicto | Commit | Qué cambió | Freno |
|---|---|---|---|---|---|
| 1 | Día de carga | CICLO, con la premisa refutada | `e16beb6` | Un solo lector de fechas, `_fecha_planilla`, que entiende la hora y las formas de Excel. Aviso cuando la celda no es fecha. MAERSK avisa cuando busca desde mañana | No se cumplió: la planilla real no tiene la columna, así que no trae formatos que puedan ser ambiguos |
| 2 | Espera de ONE | CICLO | `45f2171` | La espera reconoce las tarjetas de itinerario por su estructura medida y dice cuántas llegaron o qué pasó | No tenía |
| 3 | `test_guardar_credenciales` | CICLO: la causa está en el programa | `9710ae2` | `_reemplazar` reintenta `os.replace` cuando Windows lo niega un instante | No se cumplió: se reprodujo, 47 de 900 |
| 4 | El nombre fuera de lo versionado | CICLO | `135e765` y la rama | El nombre en pantalla de COSCO sale de `config.json`, las corridas de referencia llevan `*`, la plantilla usa un marcador neutro y la búsqueda final da 0 | No se cumplió: la llave nueva es opcional y la config de antes carga igual |

La red pasó de 267 a 281 pruebas, de 559 a 585 mutaciones y de 675 a 710 pares:

| Commit | Pruebas | Mutaciones | Pares |
|---|---|---|---|
| `ecbdfaa` (base) | 267 | 559 | 675 |
| `e16beb6` (ítem 1) | 271 | 569 | 690 |
| `45f2171` (ítem 2) | 274 | 574 | 696 |
| `9710ae2` (ítem 3) | 277 | 578 | 701 |
| `135e765` (ítem 4) | 281 | 585 | 710 |

`test_candado` no cambió en ningún commit, y la guarda de ninguna naviera cambió.

## Ítem 1 · El día de carga (`e16beb6`)

**Medido primero, solo formatos:** las dos copias de la planilla son el mismo archivo: la del panel en `%TEMP%` y
`Reservas AQUASHIELD.xlsx`. Tiene 7 hojas, con el encabezado en la fila 4, y **ninguna trae columna de día de
carga**. El lector ubica en cada una 9 campos: naviera, puerto de embarque, destino original, destino final, nave,
viaje, cotización o contrato, estado y N° de reserva emitida. COSCO trae 8, sin la última. Por eso COSCO y MAERSK no tenían día de
carga el 25, y no por la hora.
El freno pedía parar si algún formato de la columna era ambiguo. Sin columna no hay formatos que medir, así que no se
cumplió.

Aun así se hizo lo decidido:
- **Un solo lector**, `_fecha_planilla`, para las cinco navieras que usan el día de carga: MSC, COSCO, HYUNDAI, MAERSK y
  CMA. ONE no lo usa. Entiende:
  - la fecha de Excel (`datetime` o `date`) y su número de serie (5 dígitos, días desde el 30-12-1899);
  - los textos AAAA-MM-DD y DD-MM-AAAA (con `-`, `/` o `.`, y año de 2 o 4 dígitos), con o sin hora. Los textos se leen
    **con el día primero, como siempre** en este programa;
  - una fecha que no existe, como el 31 de febrero, no cuenta.
- **Si la celda trae algo que no es fecha,** `_avisar_dia_carga` lo avisa en pantalla y en `log.txt` al empezar la
  reserva, y la naviera sigue como si la fila no la trajera:
  - MAERSK busca desde mañana;
  - COSCO aplica su regla: con más de un itinerario para la nave queda NO ENVIADA con la lista;
  - MSC usa el día de retiro.
- **MAERSK avisa cuando busca desde mañana** (`_mk_fecha`): si la fila no trae un día que se entienda, o si no pudo
  escribirlo en el portal. Hasta `ecbdfaa` lo hacía sin avisar.
- No cambia qué columnas ni qué filas leen los lectores.

## Ítem 2 · La espera de resultados de ONE (`45f2171`)

**Medido** en el HTML de la parada de ONE de la corrida del 25 y en la fuente de Playwright 1.58.0: `wait_for_selector`
mira **solo el primer elemento que calza** con el selector, en orden de documento. El selector de antes era
`mag-card, [class*=schedule], [class*=result], [data-booking-step]`, y lo primero que calzaba era la lista del
autocompletado de puertos (`SearchMenu_search-menu-result`). Esa lista está vacía y nunca se ve, así que la espera vencía
siempre, aunque había 32 tarjetas a la vista. En `logs/` venció las 7 de 7 veces que corrió ONE, también el 21, cuando
ONE reservó.

**El cambio:** `_one_esperar_resultados` espera las tarjetas de itinerario por su estructura medida,
`[class*='ResultCard_card']`, y al terminar dice lo que pasó. No hace clics ni usa el teclado:
- «itinerarios: n tarjeta(s) a la vista», con el tiempo que tardó;
- si vence porque llegaron tarjetas y la primera no se ve, lo dice, y busca la nave igual;
- si vence porque no llegó ninguna, también lo dice, y busca la nave igual.

Ya no dice «sin señal».

## Ítem 3 · La prueba de guardar credenciales (`9710ae2`)

**Reproducido:**
- Sin el arreglo, la prueba aislada pasó 20 de 20 veces y `test_web` completo, 5 de 5.
- Repetida en ráfaga, la secuencia de la prueba dio **47 de 900** POST a `/api/credenciales` con un 500. El cuerpo era
  texto, «[WinError 5] Acceso denegado: 'config.json.tmp' -> 'config.json'», y la prueba lo leía como JSON. Esa es la
  falla de 1 de cada 12 suites.

**La causa es del programa:** `os.replace` falla si otro proceso tiene abierto el archivo un instante. Qué proceso es no
se midió; la hipótesis es el antivirus.

**El arreglo:** `_reemplazar` reintenta hasta 20 veces, con 50 ms entre un intento y otro, y solo ante `PermissionError`.
Si Windows lo sigue negando, el error sube y el panel lo muestra como antes; cualquier otro error sube de inmediato.

**Después del arreglo:**
- la misma ráfaga dio 0 de 900;
- `test_web` completo pasó **10 de 10** veces seguidas, y la suite completa, **3 de 3** (277 pruebas);
- `test_guardar_credenciales` no cambió: no se aflojó lo que verifica.

## Ítem 4 · El nombre del operador fuera de lo versionado (`135e765` y la rama `main`)

**Dónde estaba**, en `9710ae2`: el nombre, 72 veces, y el apellido, 1, en 11 archivos versionados.
- En la clave de la plantilla.
- En las rutas de las corridas de referencia: el programa, las cuatro generadoras, un informe y `CLAUDE.md`.
- En la heurística de sesión de COSCO, que tenía el apellido.
- En comentarios, la ayuda del panel Tkinter, los textos del video tutorial y la red de pruebas.

**El cambio:**
- **COSCO** reconoce la sesión con `_cosco_sesion_activa`. En las páginas `/ebusiness/` que no son el tablero, busca el
  nombre con que el portal muestra al operador. Ahora lo toma de `nombre_en_pantalla`, en sus credenciales de COSCO de
  `config.json`. Es opcional: sin él, reconoce la sesión por «aquachile», que ya era la otra mitad de la heurística.
- **`config.json` real** se puso al día con escritura atómica y sin mostrar valores:
  - el campo se agregó en las 2 credenciales de COSCO: la del primer operador, con el nombre que tenía el código, y la
    otra, vacía;
  - todo lo demás quedó igual, fin de línea CRLF incluido;
  - antes de escribir se comprobó que el archivo daba la ida y vuelta idéntica con su formato.
- **`config.example.json`** trae «usuario1» y «usuario2», con `nombre_en_pantalla` vacío.
- **Las corridas de referencia** (`CORRIDAS_DE_REFERENCIA`) llevan `*` en lugar del operador, y `_es_de_referencia` las
  reconoce con `fnmatchcase`: calzan con cualquier operador, pero solo en su naviera, fecha y hora.
- **Las generadoras** resuelven el `*` con `glob` desde `_ruta`: las 53 rutas llegan al mismo archivo real que en
  `9710ae2` (53 de 53, 0 descartadas).
- **Los comentarios, la ayuda, `CLAUDE.md` y el informe** usan `<operador>` o `usuario1`.
- **La rama** pasó de `master` a `main` con `git branch -m`. El repo no tiene remoto, así que no había nada que
  actualizar en otro lado.
- **El historial no se reescribió.**

**La búsqueda final:**
- Los términos salen de `config.json`: la clave de cada operador, las palabras de su descripción y su nombre en
  pantalla.
- En los 52 archivos versionados de `135e765`, el nombre y el apellido dan **0**, con 0 archivos descartados.
- **Control positivo:** la misma búsqueda sobre `9710ae2` da 72 y 1.
- Los otros tres términos son genéricos, y no se cuentan como nombre:
  - «usuario2», la clave del segundo operador;
  - dos palabras comunes de su descripción.
- En los metadatos de los 72 commits (autor, quien commitea, sus correos y el mensaje), el nombre y el apellido dan
  0.
- La sonda de secretos ya traía un chequeo informativo del nombre, y dio 0 sobre el staging.

## Expectativas que cambiaron (antes → ahora)

| Prueba | Antes | Ahora |
|---|---|---|
| `test_ayudantes.TestFechas` (sus casos) | «2026-13-01» daba «01/13/2026» en CMA | Da «»: no es una fecha. Se suman casos con hora, número de serie, `datetime` y `date` |
| `test_evidencia.TestCorridasDeReferencia.nombradas` | Leía `logs/([A-Za-z0-9_]+)/` en las generadoras | Lee `logs/([A-Za-z0-9_*]+)/`: acepta el `*` |
| `test_evidencia.TestCorridasDeReferencia.test_la_poda_no_las_toca` | Creaba cada corrida de referencia con su nombre exacto, el del operador | La crea con dos operadores sintéticos, `op_prueba` y `otro_op`, y la poda no toca ninguna |

- Ítems 2 y 3: ninguna expectativa cambió.
- Mutaciones borradas: 3 del ítem 1, que miraban los lectores viejos: `cma-fecha-otro-siglo`,
  `cosco-itinerario-fecha-con-hora` y `cosco-itinerario-fecha-al-reves`.
- Mutaciones puestas al día, porque su texto viejo cambió:
  - `cred-no-reemplaza-el-archivo` (ítem 3) apunta a `_reemplazar`;
  - `poda-toca-referencia`, `referencia-falta-una` y `limpieza-simulador-nombra-cma-dev` (ítem 4): las dos últimas
    nombraban al operador.
- Mutaciones nuevas: 13, 5, 4 y 7, una tanda por ítem.
- Pruebas nuevas: 4, 3, 3 y 4, y un caso nuevo en `TestMSC`.

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\correr.py --mutaciones --filtro fecha
python tests\correr.py --mutaciones --filtro one-espera
python tests\correr.py --mutaciones --filtro reemplazar
python tests\correr.py --mutaciones --filtro cosco-sesion
python tests\correr.py --mutaciones --filtro TestCorridasDeReferencia
python tests\correr.py --todo
git branch --show-current
```

Las sondas son de solo lectura y viven fuera del repo. Cada una aborta si su control no da lo esperado:
- **La planilla:**
  - la forma de cada celda del día de carga, sin valores;
  - los campos que ubica `_mapear` en cada hoja;
  - las tres columnas agregadas **en memoria**, con fechas sintéticas. El libro nunca se guarda.
- **ONE:** en el HTML de la parada, el primer elemento de cada selector en orden de documento, y las tarjetas; en
  `logs/`, cómo terminó cada espera.
- **Credenciales:** la secuencia de la prueba en ráfaga, 900 POST, contando las respuestas que no son JSON.
- **El nombre:**
  - en los archivos, los términos de `config.json`, enmascarados; el universo es `git ls-files` o el árbol de un
    commit;
  - en los metadatos de todos los commits.
- **Las generadoras:** cada literal `logs/…` de `9710ae2` contra su patrón nuevo, resuelto con `glob`.
- **`config.json`:** solo conteos, con la ida y vuelta comprobada antes de escribir.
- **La red por commit:** pruebas, mutaciones y pares leídos de git. El control es la base del encargo:
  267, 559 y 675.

## NO retroceder (pieza 2)

- **No le vuelvas a dar a una naviera su propio lector de fechas.** La fuente es una sola, `_fecha_planilla`; si no,
  cae `test_cada_naviera_que_usa_la_fecha_avisa_y_la_lee_con_el_mismo_lector`.
- **No esperes con un selector genérico.** `wait_for_selector` mira solo el primer elemento que calza, y el genérico de
  ONE calzaba primero con una lista vacía.
- **No vuelvas a un `os.replace` pelado en `/api/credenciales`.** Windows lo niega en ráfagas.
- **No escribas el nombre del operador en un archivo versionado.** En su lugar:
  - `<operador>` en rutas de ejemplo e informes;
  - `*` en `CORRIDAS_DE_REFERENCIA` y en las generadoras;
  - `config.json` si el programa lo necesita.

  Las carpetas de `logs/` llevan el nombre: al citarlas en un informe, cámbialo por `<operador>`.
- **No cambies `_es_de_referencia` a una comparación exacta.** La poda borraría el HTML de las corridas de referencia.
- **No quites `nombre_en_pantalla`.** Sin él, COSCO reconoce la sesión solo por el texto de la empresa.

## Premisas del encargo contrastadas (pieza 5)

- **Ítem 1, «no traían un día de carga legible, porque `_mk_fecha_txt` no reconoce fechas con hora»:** refutada como
  causa. La columna no existe en ninguna hoja. Que los lectores viejos no entendían la hora era cierto, pero no fue lo
  que pasó el 25.
- **Ítem 1, «MAERSK buscó desde mañana sin avisar»:** confirmada. Ahora avisa.
- **Ítem 2, «vence a los 8 s sin verlos, aunque la página mostraba 32 resultados»:** confirmada. La causa medida es que
  la espera mira solo el primer elemento que calza.
- **Ítem 3, «falló 1 de 12 veces (la respuesta no fue JSON)»:** confirmada: un 500 con texto. Solo sale en ráfagas: 0
  fallas en 20 corridas aisladas y 5 de `test_web`, y 47 de 900 en la ráfaga.
- **Ítem 4, dónde estaba el nombre** (plantilla, rutas de ejemplo, heurística de COSCO, comentarios y ayudas):
  confirmada, y además en un informe, `CLAUDE.md`, los textos del video tutorial y la red de pruebas.
- **El estado de partida** (`72f932c`, `ecbdfaa`, 267, 559 y 675): confirmado.

## Universo y cobertura (pieza 3)

- **Planilla:** 2 copias, que son el mismo archivo. Cada una tiene 7 hojas: CONSOLIDADO con 30 filas leídas y cada
  naviera con 5. 0 hojas con día de carga, y 0 celdas descartadas.
- **ONE:** el HTML de la parada del 25 y las 7 corridas de ONE en `logs/`.
- **Credenciales:**
  - 900 POST antes del arreglo y 900 después;
  - 20 corridas aisladas y 5 de `test_web` antes;
  - 10 de `test_web` y 3 suites después.
- **El nombre:** 52 archivos versionados, con 0 descartados: cada uno se leyó como UTF-8 o, si no, latin-1. Además, los
  72 commits.
- **Generadoras:** 53 rutas y 0 descartadas.
- **No medido:**
  - el lector de consola (`leer_reservas`) con la columna nueva: medirlo exige guardar una copia de la planilla real;
  - qué proceso tiene `config.json` cuando Windows niega el reemplazo;
  - la espera de ONE en una corrida viva: se midió contra el HTML guardado y una página sintética.

## Defectos de instrumento cazados (pieza 4)

1. **El guion del ítem 4 abortó en su aserción de coincidencia única.** Un comentario traía el nombre con mayúscula. No
   escribió nada; se corrigió con una búsqueda sin distinguir mayúsculas.
2. **La sonda del nombre enmascaraba mal:** un término quedaba dentro de la máscara de otro. Se corrigió aplicando
   primero los términos más largos, con máscaras «T<n>».
3. **La sonda de las generadoras no podía emparejar los literales:** la docstring de `_ruta` también nombra `logs/`. Se
   excluyeron los literales con espacios.
4. **Un `git diff` mostró en la consola líneas viejas con el nombre.** Fue solo salida de la herramienta, nunca en un
   archivo ni en un mensaje. Desde ahí, los diffs se miraron con el visor enmascarado.
5. **Usé `sort` en una tubería**, que las reglas de esta máquina prohíben en Git Bash. Solo contaba corridas en OK, y el
   número sale igual del conteo de archivos: 20 de 20.
6. **Ítem 1:**
   - `re` no está importado a nivel de módulo: se usó su alias `_re_mk`;
   - escribí mal el hash de un «Hasta», y se corrigió antes del commit;
   - la mutación `reefer-bool-es-numero` dejó de ser única por la guarda de los booleanos, y se ancló con un comentario
     en la misma línea;
   - una prueba afirmaba «sin `strptime`» en todo el archivo, pero la poda lo usa: se acotó a los cinco lectores.
7. **Ítem 3:** la mutación `cred-no-reemplaza-el-archivo` dejó de calzar con el cambio, y se puso al día.
8. **La herramienta Bash cambió `\\` por `\` en un heredoc.** Ya estaba registrado; esa edición se rehízo con Edit.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| **El historial trae el nombre**: el contenido de los commits hasta `9710ae2`. Un push lo lleva al remoto | El encargo dice que el historial no se reescribe | …decides reescribirlo antes del primer push, lo que cambia todos los hashes |
| Nada impide que el nombre vuelva a un archivo: la sonda de secretos lo busca como dato informativo y solo con la descripción completa | Hallazgo: cambiar el gate de cada commit es tu decisión | …quieres que la sonda bloquee el commit |
| `crear_simulador_html.py` y `crear_video_tutorial.py` traen números de booking, una nave y rutas que parecen reales | Hallazgo, fuera del encargo, que pedía solo el nombre | …el remoto no debe llevarlos: se decide antes del primer push |
| `init.defaultBranch` de git en esta máquina sigue en `master` | Es configuración global, fuera del repo | …un repo nuevo debe nacer en `main` |
| El panel Tkinter escribe `config.json` sin escritura atómica; el web sí la usa | Hallazgo | …decides arreglarlo |
| Los textos de fecha se leen con el día primero: «07-10-2026» es el 7 de octubre | Convención de siempre en este programa | …la planilla trae fechas con el mes primero |
| El lector de consola no se midió con la columna nueva | Es el camino antiguo | …usas la consola con esa planilla |
| La espera de ONE, sin medir en una corrida viva | No hubo corrida desde el cambio | …la próxima corrida de ONE dice algo inesperado |
| Un `ResourceWarning` por un socket sin cerrar en 1 de las 10 corridas de `test_web` | No es falla; no se investigó | …vuelve a salir o cae una prueba |
| La hoja COSCO no tiene la columna «N° de reserva emitida» | Es la estructura de la planilla | …emites con COSCO: la descarga avisará que no puede escribirla |
| Los residuales de `CICLO-pendientes-con-evidencia.md` | No son parte de este encargo | …según cada fila de ese informe |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v13**:
- **PASO 0 con veredicto:** CICLO en los cuatro. En el ítem 1 se refutó la premisa, y aun así se hizo lo decidido.
- **Re-medir contra HEAD antes de diseñar:** la red del encargo se verificó en `ecbdfaa`, y el nombre se contó en
  `9710ae2` antes de cambiar nada.
- **Control positivo que aborta:** en cada sonda. La del nombre aborta si no encuentra un término sintético; la de la
  red, si la base no da 267, 559 y 675.
- **Todo salto silencioso lleva contador:** 0 descartados en el nombre (52 archivos), en las generadoras (53 rutas) y en
  la planilla.
- **La unidad la fija el sujeto:** la espera decide por el primer elemento que calza, así que se midió el primero en
  orden de documento, no cuántos calzan. La falla de credenciales se contó por POST, y el nombre, por archivo y por
  término.
- **Un chequeo de sintaxis no prueba el contrato:** las generadoras parseaban; se midió que sus 53 rutas llegan al mismo
  archivo.
- **El negativo tiene que morder:** el censo filtrado en cada commit y el censo completo al final.
- **Fuente única:** `_fecha_planilla` para las cinco navieras, y el nombre, en `config.json`.
- **El cambio y su guardián en la misma operación:** cada cambio con su prueba y su mutación, en el mismo commit.
- **Cada reemplazo afirma su viejo una vez, escritura atómica y EOL:**
  - un guion abortó en su aserción;
  - `config.json` se escribió con temporal y `os.replace`, tras comprobar la ida y vuelta, y conservó CRLF;
  - cada blob commiteado quedó igual al árbol, con 0 CR.
- **FRENAR cuando la decisión es de negocio:** reescribir el historial, bloquear el nombre en la sonda y los datos de
  las generadoras quedan reportados, no hechos.
- **Declarar las premisas refutadas:** la del ítem 1.
- **Choque, sin freno:** el encargo pide un commit por ítem, pero el cambio de rama no es un commit. Se hizo después del
  commit del ítem 4.

Reglas del módulo:
- casos sintéticos;
- la sonda de secretos antes de cada commit;
- nada de `logs/` en el repo;
- los textos nuevos en español con tuteo;
- y desde este encargo, el nombre del operador en ningún archivo versionado.

## Entregable (pieza 8)

Este `.md`, sin renderizar, y `CLAUDE.md` al día.

**Gates** (en cada uno, la sonda de secretos dio 0 sobre el staging; entre paréntesis, mutaciones y pares de cada
censo filtrado, y muerden todos):

| Commit | Suite completa | Censos filtrados |
|---|---|---|
| Ítem 1, `e16beb6` | 271 en verde, 0 cambios en los originales | `fecha` (18 y 24), `cosco-itinerario` (8 y 9), `TestMSC` (2 y 2), `mk-manana` (2 y 2) |
| Ítem 2, `45f2171` | 274 en verde | `one-espera` (4 y 5), `one-sin-la-espera` (1 y 1), `TestOne` (16 y 22), la foto de clics genéricos (27 y 51) |
| Ítem 3, `9710ae2` | 277 en verde | `reemplazar` (3 y 4), `credenciales-sin-reintento` (1 y 1), `cred-no-reemplaza` (1 y 1), `TestPanelCredenciales` (8 y 9) |
| Ítem 4, `135e765` | 281 en verde | `cosco-sesion` (3 y 3), `cosco-login` (1 y 1), `referencia` (4 y 7), `plantilla` (2 y 2), `poda` (32 y 35), `limpieza-simulador` (1 y 1), `TestCorridasDeReferencia` (6 y 10), `TestCOSCO` (9 y 9) |

En el ítem 3, además, `test_web` pasó 10 de 10 y la suite 3 de 3. En el ítem 4, el chequeo informativo del nombre de
la sonda también dio 0.

- **Censo completo final sobre `135e765`:** pasó, en 44 minutos.
  - 281 pruebas en verde, y el control (la copia sin mutar) pasa;
  - 585 mutaciones y 710 pares, y muerden todos;
  - 0 pruebas sin mutación y 0 cambios en los originales.
- **El commit de este informe** solo agrega este `.md` y cambia `CLAUDE.md`, que ninguna prueba lee. La suite
  completa corrió con los dos ya cambiados: 281 en verde y 0 cambios en los originales.

## Para tu próxima prueba con el candado cerrado: qué preparar en la planilla

**Agrega en cada hoja que vayas a correr una columna «Día de carga».** Si corres «todas» desde CONSOLIDADO, agrégala
ahí.
- Hoy no existe en ninguna de las 7 hojas.
- El encabezado va en la misma fila que los otros, hoy la 4, y en cualquier posición. El lector la ubica por el texto
  «día de carga», con o sin tilde.
- **Formato:** una celda con formato de fecha de Excel. Es lo más seguro, porque no deja dudas entre día y mes.
  - También sirven el texto DD-MM-AAAA, con el día primero, o AAAA-MM-DD, con o sin hora, y el número de serie de Excel.
  - Cualquier otra cosa se avisa en pantalla y en `log.txt`, y la fila sigue como si no la trajera.
- **Qué día poner en cada naviera:**
  - **COSCO:** la ETD exacta del itinerario que quieres. Si la nave tiene más de un itinerario, elige el de ese día; si
    no queda uno solo, la reserva queda NO ENVIADA con la lista.
  - **MAERSK:** el día de zarpe. Sin él, busca desde mañana y lo avisa.
  - **MSC:** al menos 3 días después del día de la prueba. Si no, usa hoy más 18 días.
  - **HYUNDAI y CMA:** la escriben en la búsqueda, como fecha de zarpe en HYUNDAI y como fecha «desde» en CMA. Sin ella,
    dejan la que trae el portal.
  - **ONE:** no la usa.

**Columnas opcionales:**
- **«Día de retiro»** (el encabezado tiene que contener «retiro»): MSC la usa si el día de carga falta o no se
  entiende. Lleva el mismo formato.
- **«Temperatura»**, en °C y como número, por ejemplo -18. Si falta, se usa `temperatura_reefer_c` de `config.json`.

**La nave:** escríbela como aparece en los itinerarios del portal. El 25, ni ONE ni MAERSK la encontraron.

**Medido en memoria con los encabezados reales:** agregar las tres columnas al final de cada hoja no mueve ninguno de los
9 campos que el lector ya ubica. Lee las mismas filas, 30 en CONSOLIDADO y 5 en cada naviera. Entiende las cuatro formas
de fecha en todas las filas, y ninguna queda ilegible.

**En `config.json` no tienes que hacer nada.** `nombre_en_pantalla` ya está en las credenciales de COSCO del primer
operador. Si COSCO no reconoce la sesión de otro operador, llena el suyo con el nombre que muestra el portal.
