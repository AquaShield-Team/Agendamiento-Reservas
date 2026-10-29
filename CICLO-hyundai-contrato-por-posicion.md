# CICLO-hyundai-contrato-por-posicion · Encargo 89: «Contract No» de HYUNDAI elige solo la opción del contrato configurado

> **metodo-ciclo v39** (la misma del disco al empezar; la sesión se compactó a mitad y la volvió a cargar: la misma v39).
> Base: `main` en `50c5cd5`, árbol limpio al empezar (`50c5cd5` ya estaba en GitHub: lo subiste el 28-10). **Dos
> commits:** el cambio (`60bbd25`) y este informe. **No se subió nada:** el bloque de push está al final. Sin datos de
> clientes ni de la cuenta: los log.txt y `config.json` se leyeron en su lugar, en solo lectura y en
> memoria, y de ahí salieron solo cuentas; las pruebas usan contratos inventados.

## Qué se pidió y qué salió

El encargo, sobre las dos cosas que dejó el encargo 88: (1) con un contrato configurado que no está entre las opciones de
«Contract No», el paso 3 ya no elige la primera opción real por su posición: NO ENVIADA, sin pulsar nada, con un motivo que
dice qué contrato buscó; con el contrato en la lista, se elige ese; sin contrato, NO ENVIADA, como antes. (2) Los motivos de
«Contract No» dicen dónde se escribe el contrato: «panel → Credenciales → HYUNDAI → columna Contrato», en vez de config.json.
Medir que ninguna corrida guardada que llega a la guarda cambie de resultado; prueba y mutación de los tres casos; revisión
de código; commit sin push. FRENA SI el cambio toca otra naviera, o una corrida guardada que llega a la guarda pasa a NO
ENVIADA.

Después, **la decisión de Marcelo sobre lo que encontró la revisión de seguridad** (el ciclo se frenó a preguntarla): (a)
comparar el contrato entero contra el código de la opción, no «el texto de la opción lo contiene»; medir antes las 20 filas
que llegaron a la guarda y frenar si alguna cambia; leer qué opción quedó elegida después de elegir; el contrato del motivo,
saneado; que el paso 2 le quite los espacios al contrato, como el paso 3; y «Named Customer» y «HMM Sales Person», que
también eligen por posición, al residual, con lo que haría falta saber para elegirlos bien.

**No cayó en ningún FRENA.** Las 20 filas de HYUNDAI que llegaron a la guarda eligen la misma opción con la regla nueva
(abajo), y el cambio no toca otra naviera: todo está en `_hmm_elegir_contrato`, sus tres ayudantes nuevos y las dos líneas
del contrato de `reservar_hyundai`.

## Paso 0 (medido)

- **Las filas de HYUNDAI guardadas** (`.trabajo/e89/medir.py`): 50 log.txt de `logs/` y de «1. pruebas», 0 descartados, 29
  filas de HYUNDAI en 18 corridas. Las 20 que llegaron a la guarda (15 OK-EJEMPLO y 5 EMITIDA del 21-09) eligieron el
  contrato configurado, la única opción real de la lista («Contract No: '…'»). Las otras 9 quedaron NO ENVIADA antes: 7
  sin contrato (las del colega, encargo 88) y 2 sin llegar a «Contract No». **Ninguna eligió por posición** («Contract No
  (primera real)»), ni siguió sin elegir (0 «sin opción», 0 «err»). Control positivo que aborta: la corrida del 28-10 de
  este equipo, 3 elegidas que llegan a la guarda, y la del colega, 2 sin contrato.
- **Antes de la regla exacta** (`.trabajo/e89/medir_exacto.py`; `config.json` leído en memoria, sin imprimir nada), en las
  20 filas que llegaron a la guarda:
  - el valor que eligió el programa es el código de su única opción real (el texto antes de « - »), y la opción trae esa
    forma, «código - (…)»: 20 de 20;
  - el contrato configurado hoy para el operador de la corrida es ese código, entero: 20 de 20;
  - con la regla exacta, una sola opción tiene ese código, la misma: 20 de 20.

  **Ninguna cambia de resultado.** El control en la otra dirección: con el contrato sin su último carácter, la regla de
  antes («contiene») elegía en las 20 y la exacta en ninguna. Control positivo que aborta: las 3 filas de la corrida del
  28-10, y el total de 20. **LÍMITE:** el contrato configurado en una corrida vieja pudo ser otro; se midió el de hoy.
- **El HTML del paso 3 no se guardó nunca:** en los 1.122 HTML de `logs/`, 0 listas `#selContractNo` (los 42 `select` con
  «contract» en su id son `cboContractNoForAlternativeRoute`, de la lista de naves del paso 2). Lo que se sabe de la lista
  de «Contract No» sale de la línea «Contract No opciones» de log.txt, que trae hasta 6.

### Premisas que se corrigieron

- **«Elige la primera real» no era la única forma de elegir mal:** con la regla «el texto lo contiene», un contrato escrito a
  medias elegía otro que lo contenía, y dos contratos donde uno es prefijo del otro («CT-1» y «CT-12») daban NO ENVIADA por
  ambiguos (revisión de seguridad). La decisión (a) cierra las dos.
- **Hasta el encargo 88, CLAUDE.md decía que el corte sin contrato era «antes de Booking Details»:** es en Booking
  Details, en «Contract No» (lo corrigió el 88; se repite aquí porque este encargo escribe sobre ese corte).
- **Las 5 EMITIDA del 21-09 terminan su fila con «· fila N: …»,** no con «· Reserva N: …»: la primera versión de
  `medir_exacto.py` contó 15 filas a la guarda y no 20 (abajo, «Lo que salió mal»).

## El cambio · `60bbd25`

- **`_hmm_elegir_contrato`** (en el paso 3, en el lugar del bucle que leía las opciones y caía a «la primera real»):
  - lee las opciones de `#selContractNo` hasta que llegue la del contrato, hasta `HMM_LECTURAS_CONTRATO` veces (15) cada
    0,4 s: 6 s, como antes; hasta ahí, la espera se cortaba con la primera lectura que traía una opción real, aunque la del
    contrato llegara después;
  - elige solo la única opción cuyo código (`_hmm_codigo_del_contrato`: el texto antes del primer « - », sin espacios en
    los extremos, en mayúsculas) es el contrato configurado entero (`_hmm_contratos_que_calzan`), sin contar «Select»,
    «Dummy» ni «Direct Input» (`HMM_NO_SON_CONTRATO`);
  - después de elegirla, lee la lista y comprueba que quedó elegida esa misma (el texto de la opción de `selectedIndex`,
    `_JS_HMM_CONTRATO_ELEGIDO`); si quedó otra, log.txt dice cuál, saneada;
  - corta (NO ENVIADA, `ObjetivoNoEncontrado`, `hmm_f<fila>_sin_objetivo`) si la lista no trae ningún contrato, si
    ninguna opción tiene el código, si lo tienen dos, si la lista no acepta la elección, si queda con otra opción o si no
    se puede leer cuál quedó.
- **Los motivos** dicen dónde se escribe el contrato (`HMM_DONDE_VA_EL_CONTRATO`) cuando se corrige escribiéndolo (sin
  contrato, y con uno que no está), y muestran el contrato saneado (`_hmm_contrato_a_la_vista`: los espacios de a uno,
  hasta 40 caracteres, y cada carácter de control, de formato, privado o sin asignar como «?», como el contenedor y el
  destino final). Con la lista sin contratos, o con dos opciones del mismo código, no mandan a corregir el contrato, que
  puede estar bien. La cola del decorador («revisa ese paso en el portal»), común a las seis navieras, no cambió.
- **El paso 2 y el paso 3 le quitan los espacios de los extremos al contrato de las credenciales,** como ONE, MSC y
  CMA-CGM; uno de solo espacios cuenta como ninguno (en el paso 2, hasta ahí, se lo pasaba a la lista tal cual).
- **Pruebas:** `test_ayudantes.TestContratoDeHyundai`, 11 pruebas; diez sobre una página falsa que anota cada lectura, cada
  elección, cada comprobación y cada espera, y lo inesperado (en una lista que la prueba exige vacía, porque el programa se
  tragaría una excepción en su `try`): la única opción (también llegando tarde, en minúsculas y con el contrato con
  espacios), el contrato entero (un fragmento y un prefijo no calzan; con su opción y otra que la contiene, elige la suya),
  el que no está, la lista sin contratos, las opciones que no son un contrato, dos con el mismo código, la lista que no
  acepta, la que queda con otra (también una opción de otro contrato que contiene la del contrato y va antes) o no se
  puede leer, el motivo saneado, y los seis motivos y las dos líneas del contrato, leídos del código. La undécima corre
  en Node los dos JavaScript que leen la lista. `TestContratosPorDefecto.test_hyundai_sin_contrato_no_elige_a_ciegas`
  pasó a exigir la llamada a `_hmm_elegir_contrato` después del corte.
- **Mutaciones:** 28 del encargo 89; las anclas de `contrato-hyundai-fijo` y `hyundai-paso2-sin-guarda`, a las líneas
  nuevas del contrato.
- **CLAUDE.md:** el punto de `contratos_por_defecto` (la regla, los motivos, lo medido, lo residual), la lista de motivos de
  NO ENVIADA y el número de pruebas.

## Compuertas

| compuerta | resultado |
|---|---|
| Censo de mutaciones (`--filtro e89-`), el final | 28 mutaciones, 29 pares, los 29 muerden; control (la copia sin mutar, 12 pruebas) pasa; 1.020 pruebas, 0 sin mutación; foto de los originales sin cambios; `RESULTADO: OK`, exit 0 |
| Censo de las que miran el contrato de HYUNDAI desde antes (`--filtro test_hyundai_sin_contrato_no_elige_a_ciegas` y `--filtro contrato-hyundai-fijo`) | 3 mutaciones y 3 pares, y 1 y 1: todos muerden; foto sin cambios; `RESULTADO: OK`, exit 0 en los dos. Corrieron sobre la versión anterior a la segunda revisión de código; lo que cambió después no toca sus anclas ni sus pruebas |
| Suite completa, la final, sobre el árbol del commit | `Ran 1020 tests in 1812.829s · OK`, foto de los originales sin cambios, `RESULTADO: OK`, exit 0 (con el tope de la corrida subido a 3.600 s, como en los encargos 85 a 87) |
| Suite completa, la primera | Detenida a los 2 minutos para arreglar lo de la segunda revisión de código; no dio resultado |
| Las pruebas que leen lo versionado, con este informe preparado | `test_guarda_datos` y `test_sonda`: `Ran 32 tests · OK`. La suite completa no se repitió para el commit del informe: no toca código ni pruebas |
| Sonda de secretos | 0 con `--dry-run` y 0 después del `git add`, en los dos commits |
| Guarda de datos (hook pre-commit) | 0 hallazgos en los 127 archivos del cambio |
| Guarda de datos sobre los mensajes de los commits y el informe | 1 en cada mensaje: la línea `Co-Authored-By`, la dirección pública de atribución, como en los commits de antes (no es un dato); 0 en el informe |

Los censos y las suites los corrió un ayudante, uno detrás de otro, con el envoltorio de la salida literal; las salidas las
leí yo, en `.trabajo/e89/` (`censo_*.out`, `suite2.out`). Mientras corrían, otra sesión (Control Congelado) corría su
propio censo: los tiempos de esta tabla son de reloj, no una medición de tiempo.

## Las revisiones

Una a la vez, cada una sobre un clon en `.trabajo/e89/clon`, sin remoto.

| Revisión | Hallazgo | Qué se hizo |
|---|---|---|
| Código (primera) | El motivo culpaba al contrato configurado cuando la lista no había cargado ningún contrato | Arreglado: ese caso tiene su motivo, sin mandar a corregir el contrato |
| Código (primera) | El contrato de las credenciales iba con sus espacios | Arreglado: sin los espacios de los extremos, como en ONE, MSC y CMA-CGM |
| Código (primera) | Tres mutaciones sobrevivían (sin esperar entre lecturas, una opción en minúsculas, un contrato de solo espacios) | Casos nuevos que las muerden |
| Código (primera) | La página falsa lanzaba con lo inesperado, y el programa se lo tragaba | Lo anota, y la prueba exige la lista vacía |
| Código (primera) | El texto de los motivos y de CLAUDE.md | Al día |
| Código (primera) | Residual: la única opción se decidía sobre la lectura de Python, y `_hmm_select_por_texto` vuelve a leer y elige la primera que contiene el texto | Cerrado con la decisión (a): la lista se lee después de elegir |
| Seguridad | MEDIA: con «el texto lo contiene», un contrato escrito a medias elegía otro | Decisión de Marcelo, (a): el contrato entero contra el código de la opción |
| Seguridad | MEDIA-BAJA: no se miraba qué opción quedaba elegida | Arreglado: la lista se lee después de elegir |
| Seguridad | BAJA: el motivo mostraba el contrato tal como venía, y un carácter de control rompe la fila en la planilla | Arreglado: el contrato va saneado |
| Seguridad | BAJA: el paso 2 no le quitaba los espacios al contrato | Arreglado |
| Seguridad | Info: «Named Customer» y «HMM Sales Person» eligen la primera opción real, por su posición | Residual, por decisión de Marcelo (abajo) |
| Código (segunda, sobre la regla exacta) | MEDIA: la comprobación de la opción elegida corre en JavaScript que ninguna prueba ejecutaba (la página falsa lo reconoce por su texto); leer el valor en vez del texto dejaría NO ENVIADA cada fila de HYUNDAI con la red en verde | Arreglado: los dos JavaScript que leen la lista son constantes (`_JS_HMM_CONTRATOS`, `_JS_HMM_CONTRATO_ELEGIDO`), y una prueba los corre en Node, con 3 mutaciones |
| Código (segunda) | BAJA: el ejemplo del residual en CLAUDE.md no podía pasar (las dos opciones tenían el mismo código) | Corregido, con una prueba del caso real, sin forzar la lectura: una opción de otro contrato que contiene entera la del contrato y va antes da NO ENVIADA |
| Código (segunda) | BAJA: el contrato escrito como el texto entero de la opción queda NO ENVIADA, y el motivo no decía qué es el código | El motivo lo dice («su texto antes de « - »»); aceptar también el texto entero lo decides tú |
| Código (segunda) | BAJA: si queda otra opción, log.txt no decía cuál | Arreglado: log.txt dice cuál quedó, saneada |
| Código (segunda) | BAJA: un comentario decía la regla de antes | Al día |
| Seguridad (segunda) | BAJA: el contrato se comprueba una sola vez; si el portal lo volviera a «Select» después (en su `change`, o con Named Customer), nada lo vería antes de la guarda | Residual, propuesto: volver a leerlo antes de «NEXT - Additional Information». No está medido que el portal lo haga, y antes no había ninguna comprobación |
| Seguridad (segunda) | BAJA: que la opción sea única se decide con la primera lectura que la trae, no con la lista quieta | Residual, propuesto: dos lecturas iguales seguidas, como `_mk_resultados_quietos`. Solo pesa si el portal llena la lista por partes (no medido) |
| Seguridad (segunda) | BAJA: el paso 2 sigue eligiendo por «contiene», y traga sus errores | Residual: el contrato final lo elige y lo comprueba el paso 3; qué cambia el del paso 2 no está medido |
| Seguridad (segunda) | Info: la comprobación compara el texto, no el valor; `.upper()` iguala formas Unicode distintas; Python y JavaScript no recortan los mismos espacios; un mensaje de error de Playwright con saltos de línea parte una línea de log.txt | Residual. Todos del lado seguro (NO ENVIADA de más) o con la lista cambiando entre lectura y elección; el de log.txt es el patrón de todo el archivo |
| Seguridad (segunda) | Info: el contrato ahora llega a la planilla y al panel, en el motivo de esa NO ENVIADA | Lo pidió el encargo («un motivo que diga qué contrato se buscó»); va saneado y con tope. Si la planilla sale del equipo y prefieres que no lo muestre, es una línea |

## Decisiones que tomé (Modo autónomo)

| Decisión | Por qué | Cómo se deshace |
|---|---|---|
| El código de una opción es su texto antes del primer « - » | Es la forma de las 20 opciones medidas, y el valor que eligió el programa es ese código en las 20; una opción sin « - » es entera su código | `_hmm_codigo_del_contrato` |
| Dos opciones con el mismo código dan NO ENVIADA, y el motivo no manda a corregir el contrato | Escribirlo de otra forma no las distingue; elegir una sería por su posición | Una condición en `_hmm_elegir_contrato` |
| La comprobación compara el texto entero de la opción elegida con el de la opción del contrato | Es lo más estricto que se puede leer; si quedó otra, la fila no sigue | — |
| Si la comprobación no puede leer la lista, NO ENVIADA | No se sabe qué contrato quedó | — |
| El contrato del motivo, con tope de 40 caracteres | Como el contenedor; el motivo va a la planilla | `_hmm_contrato_a_la_vista` |
| Las 4 mutaciones de MAERSK con el ancla doble, al residual | Las duplicó el código de MSC del encargo 86; no son de este encargo | Extender su ancla con una línea propia |
| Los dos JavaScript que leen la lista, a constantes corridas en Node | La MEDIA de la segunda revisión de código: el programa los corre y ninguna prueba los ejecutaba | — |
| Los BAJA y los Info de la segunda revisión de seguridad, al residual, sin tocar el código | El método deja documentar los BAJA y cerrar; los tres parten de algo del portal que no está medido, y cambiarlos pedía repetir el censo y la suite | Están propuestos en el residual |

## Lo que salió mal

- **Un aviso que no leí.** Cuando terminó la primera revisión de seguridad, contesté su aviso sin leer su resultado, y
  lo leí recién cuando preguntaste si el trabajo seguía corriendo. Es el paso 4 del cierre de metodo-ciclo.
- **La primera versión de `medir_exacto.py` contó 15 filas a la guarda, no 20:** las 5 EMITIDA del 21-09 cierran su fila
  con «· fila N: …». Lo vi al comparar con `medir.py`, y la sonda quedó con un control que aborta si no son 20.
- **Supuse que el HTML del paso 3 estaba guardado** (con la evidencia del Remark): en `logs/` no hay ninguna lista
  «Contract No». La sonda lo dice, y lo de la lista sale de log.txt.
- **La comprobación nueva salió con su JavaScript sin probar:** la página falsa la reconocía por su texto, el patrón de
  las demás pruebas de HYUNDAI. Lo encontró la segunda revisión de código, con una mutación que no caía.
- **Lancé la suite antes de que terminara la revisión de código,** y hubo que detenerla para arreglar lo que encontró:
  se repitió entera después. La detuve y busqué sus procesos por la línea de comandos: no quedó ninguno (el único
  `correr_literal` vivo era de otra sesión, de Control Congelado, y no lo toqué).
- **El ayudante del primer censo dejó un script de espera fuera de la carpeta del encargo,** en la carpeta temporal de
  la sesión. Se borró en la limpieza.
- **En la primera parte del ciclo, una salida de mis herramientas mostró en la transcripción valores de la cuenta**
  (contratos, y el nombre del operador en las rutas de `logs/`). No quedaron en ningún archivo versionado ni en este
  informe: las sondas de este informe imprimen solo cuentas.
- **Escribí que `50c5cd5` no había subido, por lo que recordaba la sesión, sin mirar `origin/main`:** lo subiste el 28-10
  a las 17:32. Lo vi al cerrar, con `git log origin/main..main`, y el commit de este informe se rehízo antes de subir
  (no estaba en el servidor).
- **Las guardas de la herramienta rechazaron a los revisores** un `export` con `GIT_CEILING_DIRECTORIES` y un comando con
  `$LOCALAPPDATA` como programa; corrieron con un lanzador en Python (la fila del 2026-10-15 de la máquina).

## Residual

- **«Named Customer» (`#actualShipperCode`) y «HMM Sales Person» (`#hmmSalesmanCd`)**, en el mismo paso 3, siguen eligiendo
  la primera opción real, por su posición (decisión de Marcelo: un ciclo propio). Para elegirlos bien hace falta saber,
  medido en el HTML del paso 3, que no se guarda nunca (habría que guardarlo con la evidencia de la guarda o con una corrida
  en modo prueba que se detenga ahí), y con Marcelo: cuántas opciones traen; cuál corresponde a AquaChile y por qué texto
  se reconoce; si dependen del Shipper o del contrato elegido; y si el portal ya trae una elegida. **Condición de
  reapertura:** que Marcelo lo encargue.
- **Una opción de otro contrato cuyo texto contiene entero el de la opción del contrato** («XCT-1 - (GA)» antes de
  «CT-1 - (GA)»), si está antes en la lista, la elige `_hmm_select_por_texto`, y la comprobación deja la fila NO ENVIADA,
  con la lista del portal en el otro contrato y sin pulsar nada más: el lado seguro, pero sin reserva. No se vio.
  **Reapertura:** si pasa, elegir la opción por su índice o por su texto exacto, y comprobar después su índice, su texto
  y su valor (eso cerraría también el Info de la comprobación por texto).
- **Lo que propone la segunda revisión de seguridad, sin medir en el portal** (las tres BAJA): volver a leer el contrato
  elegido antes de «NEXT - Additional Information»; decidir que la opción es única con dos lecturas iguales seguidas; y
  aplicar la regla del paso 3 al paso 2. **Reapertura:** que lo encargues, o que una corrida muestre la lista llenándose
  por partes o el contrato volviendo a «Select».
- **Un contrato escrito como el texto entero de la opción** («CT-1 - (GA)») queda NO ENVIADA; antes del cambio se elegía.
  **Reapertura:** que decidas aceptarlo también.
- **Que dos opciones con el mismo código den NO ENVIADA lo decidió el ciclo,** no Marcelo. En lo medido, la lista trajo
  siempre una sola opción real.
- **El JavaScript con que `_hmm_select_por_texto` elige no lo corre ninguna prueba:** la página falsa lo imita, como en las
  demás pruebas de HYUNDAI. Lo que hace de más (elegir otra opción) lo ve la comprobación, cuyo JavaScript sí corre en
  Node.
- **4 mutaciones de MAERSK tienen el ancla dos veces en el programa** (`e62-sin-juntar-los-espacios`,
  `e62-sin-esperar-la-lista-quieta`, `e62-elige-de-otra-lista` y `e65-clic-por-posicion`): el código de MSC del encargo 86
  (`6667404`, `_msc_opciones` y lo que sigue) copió esas líneas de MAERSK. El censo completo daría error en esas 4 («el
  texto viejo aparece 2 veces»); los censos filtrados de los encargos 86 a 89 no las corrían. **Reapertura:** el próximo
  censo completo, o extender cada ancla con una línea que solo tenga MAERSK.
- **No está probado en el portal:** la regla no pulsa nada nuevo; la comprobación solo lee.

## Re-medir

- Las filas guardadas: `python .trabajo/e89/medir.py` y `python .trabajo/e89/medir_exacto.py` (con el Python de la Tienda;
  leen `logs/`, «1. pruebas» y `config.json` en solo lectura, e imprimen cuentas).
- Las pruebas: `python -m unittest test_ayudantes.TestContratoDeHyundai test_ayudantes.TestContratosPorDefecto`, desde
  `tests/`.
- El censo: `python tests/correr.py --mutaciones --filtro e89-` (y `--filtro test_hyundai_sin_contrato_no_elige_a_ciegas`,
  `--filtro contrato-hyundai-fijo`).

## NO retroceder

- No volver a «el texto de la opción contiene el contrato»: un contrato escrito a medias elige otro.
- No volver a elegir la primera opción real, ni a seguir sin comprobar qué opción quedó elegida.
- No mostrar el contrato sin sanear en un motivo: va a la planilla.

## Reglas aplicadas

metodo-ciclo v39: el paso 0 con universo, cobertura y control positivo que aborta (los dos controles de `medir_exacto.py`,
uno en cada dirección); FRENAR cuando la decisión es de negocio (la regla «contiene», que se le preguntó a Marcelo); el
negativo que muerde, de a uno (el censo); el cambio y su guardián en la misma operación; todas las suites antes de cada
commit; los revisores en un clon; el modo autónomo, con su tabla; el ayudante mecánico para el censo y la suite, con la
salida literal, leída por la sesión; la limpieza dentro de la carpeta que borra. No chocaron con las reglas del módulo
(CLAUDE.md: el candado, las pruebas como fotos, cada prueba con su mutación, datos inventados).

## Push

Dos commits de `main` sin subir: `60bbd25` (el cambio) y este informe. Los dos, con el correo noreply de autor y de
committer. Antes de subir, en una consola:

```bash
git -C "C:\dev\Agendamiento Reservas" log origin/main..main --format="%h %ae %ce %s"
```

Tiene que mostrar solo el correo noreply en las dos columnas. Después:

```bash
git -C "C:\dev\Agendamiento Reservas" push origin main
git -C "C:\dev\Agendamiento Reservas" rev-parse main
git -C "C:\dev\Agendamiento Reservas" ls-remote origin refs/heads/main
```

Los dos hashes tienen que ser iguales. **`estable` no se movió:** el cambio les llega a los colegas solo cuando la avances
tú, después de probar HYUNDAI en modo prueba. Con él, un equipo sin el contrato de HYUNDAI escrito, o con uno que el
portal no ofrece, queda NO ENVIADA en «Contract No», con el motivo que dice dónde escribirlo.
