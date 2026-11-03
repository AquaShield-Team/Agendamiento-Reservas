# CICLO-named-customer-rutas-cma-y-version · Encargo 93: «Named Customer», el REVISAR de CMA-CGM, las esperas fijas, el residual del 92 y la versión en el panel

> **metodo-ciclo v39** (la misma del disco). Base: `main` en `4664942`, árbol limpio; GitHub, medido con `ls-remote` el
> 2026-11-02 a las 23:55: `main` en `4664942` y `estable` en `b39c95c`. `estable` no se tocó. **Siete commits:** los
> cinco frentes, los arreglos de las dos revisiones y este informe. **No se subió nada:** el bloque de push y el de
> `estable`, en PowerShell, están al final. Sin datos de clientes ni de la cuenta: los log.txt, el HTML guardado y
> `config.json` se leyeron en su lugar, en solo lectura y en memoria, y de ahí salieron solo cuentas, segundos y
> estados; las pruebas usan datos inventados.

## Qué se pidió y qué salió

| Frente | Commit | Qué salió |
|---|---|---|
| **1.** «Named Customer», opción (a) | `c227383` | Elige «Direct Input» por su texto; si no está, NO ENVIADA. Dos opciones con el mismo código, NO ENVIADA. **Probado en el portal esta noche:** la lista trajo `Select \| Direct Input`, eligió «Direct Input», y la fila llegó a OK-EJEMPLO |
| **2.** El REVISAR de CMA-CGM | `51b0d2f` | **La nave sí estaba en la página y no la leíamos:** la tarjeta del único «Seleccionar» subía hasta la lista entera, con otra ruta, y no leía su primer tramo. Arreglado; en las 7 listas guardadas, las dos de hoy pasan a elegir su ruta y las demás pulsan el mismo botón de antes. El motivo de la nave que no está lo dice para el colega |
| **3.** Clics y esperas fijas | `549974b` | Cinco esperas fijas del camino de cada fila, cambiadas por esperar su condición con el mismo tope. Medido en el portal: HYUNDAI, 4,1 s menos por fila; MAERSK, 1,6 s; MSC, 0. ONE y CMA-CGM no se pudieron medir (abajo). Ningún clic de sobra que quitar |
| **4.** El residual del 92 | `33dabd6` | «Named Customer» y «Sales Person» se vuelven a mirar antes de seguir, y `_hmm_select_por_texto` lee y elige con el mismo localizador |
| **5.** Local igual al clon, y la versión en el panel | `562f729` | `tests/igual_que_github.py` y «versión <rama> · <commit>» en el panel. Demostrada con `main` (abajo) |
| Las revisiones | `ed23303` | Lo que encontraron la de código y la de seguridad, arreglado |

**Ningún FRENA SI saltó.** El de CMA-CGM pedía no inventar una regla de qué nave elegir: no hizo falta, la regla de
siempre ya elige la ruta en cuanto la lectura ve su primer tramo. El de las esperas no se gatilló: las tres navieras que
se pudieron correr llegaron a OK-EJEMPLO con el código nuevo; ONE y CMA-CGM quedan para la prueba conjunta.

## Frente 2 · el REVISAR de CMA-CGM

El 02-11, en tus corridas de las 13:34 y las 14:30, la lista de CMA-CGM traía dos rutas con la nave en su primer tramo y
**una sola con su botón «Seleccionar»**. La lectura (`_JS_CMA_RUTAS`) arma la tarjeta de cada botón subiendo desde él
hasta encontrar otro botón; con un solo botón, subía hasta la lista entera, con las dos rutas, y no podía leer «el»
primer tramo. Quedaba REVISAR, «no disponible», con «Sin nombre».

- **El arreglo:** la tarjeta no sube a un bloque con los detalles de otra ruta, ni pasa de su ruta a la lista de rutas
  (`ul.travel-list`; esto último, de la revisión de seguridad).
- **Medido sin red** con la lectura de antes y la de ahora, en un Chromium, sobre las 7 listas guardadas (del 08-10 al
  02-11; `.trabajo/e93/medir_cma_antes_despues.py`): las 2 de hoy pasan de «no elige» a elegir la ruta de la nave, y las
  5 demás pulsan el mismo botón que antes.
- **El mensaje para el colega**, si la nave no está: «el portal no ofrece la nave … en ninguna de las N rutas que deja
  elegir» (o «en la única ruta…»), o «el portal muestra la nave … en N ruta(s) que no deja elegir (sin el botón
  «Seleccionar»)…», con hasta dónde buscó, las rutas que deja elegir y «No elegí otra nave: revisa la nave de la fila,
  o elige la ruta en el portal».
- **No probado en el portal:** esta noche CMA-CGM pidió el deslizador de DataDome a los 12 s, y la corrida se detuvo
  (no lo resuelvo yo). Queda para la prueba conjunta.

## Frente 3 · las esperas fijas

Medí en los log.txt de las corridas reales dónde se va el tiempo de cada fila (`.trabajo/e93/medir_huecos.py`,
`esperas_contexto.py`): casi todo es el portal. Las esperas largas que quedan van después de la guarda (no se tocan) o
en los inicios de sesión. **Ningún clic sobra:** cada uno ya busca su objetivo por su texto, y los que parecían de más
(cerrar el banner de cookies, el OK del modal de otra nave) los pide el portal.

Se cambiaron cinco, todas con el mismo tope de antes: si la condición llega antes, sigue antes; si no, espera lo mismo.

| Naviera | Antes | Ahora |
|---|---|---|
| ONE | 1,3 s fijos en cada desplegable | Hasta que se vean más opciones candidatas que antes de abrirlo, y dos cuentas iguales seguidas |
| MSC | El «Next» se miraba cada 1,2 s | Cada 0,3 s, hasta los mismos 12 s |
| HYUNDAI | 2 + 1,5 s tras «Book Now»; 2,5 s tras el «Apply» del Shipper | El OK del modal de otra nave a la vista; el Shipper escrito y un contrato en la lista |
| MAERSK | 1,5 s antes de leer la lista reefer | Hasta que la lista muestre una opción |
| CMA-CGM | 2 s al abrir el panel Reefer | Un solo panel a la vista con su «Temperature» (leído con plazo) |

**COSCO no se tocó:** su inicio de sesión pide el validador al operador, así que su modo prueba no lo puedo correr.

**El tiempo por naviera, medido en el portal** (segundos por fila que llegó a la guarda; el «antes», tus corridas de hoy
con el código de antes; el «después», mis corridas de esta noche con el código nuevo, misma planilla y misma fila):

| Naviera | Antes | Después | Lo que ganó el cambio, paso a paso |
|---|---|---|---|
| HYUNDAI | 55 y 54 | 44 | **−4,1 s**: del «Book Now» al modal, de 3,6 a 1,0 s; del Shipper al contrato, de 3,0 a 1,5 s. El resto de la diferencia es el portal (el paso 1 cargó 15 s más rápido) |
| MAERSK | 61 y 56 | 57 | **−1,6 s**: del tipo de contenedor a la lista reefer, de 3,2 a 1,6 s |
| MSC | 38 y 36 | 40 | **0**: el «Next» siempre estaba habilitado al primer vistazo. Los 3 s de más son el portal, antes de ese paso |
| ONE | 40 y 54 | — | Sin medir: la fila quedó REVISAR antes de los desplegables (el portal no mostró la nave en sus 8 semanas; a las 13:34 pasó lo mismo) |
| CMA-CGM | 63 | — | Sin medir: DataDome pidió el deslizador |
| COSCO | 32 | — | Sin cambios |

- **Las corridas:** en modo prueba, por la API del panel abierto desde el repo vivo, sin abrir una pestaña en tu
  navegador y con el candado cerrado (el panel lo dijo, y el script abortaba si no). Una fila por naviera. La primera,
  con ONE, MSC, HYUNDAI y MAERSK; MAERSK quedó NO ENVIADA en el origen, porque el formulario no cargó en 7 s («[sin
  señal]») y el campo no aceptó el clic: es antes de lo que cambié, y sola, enseguida, llegó a OK-EJEMPLO.
- **La medición no es limpia del todo:** OneDrive sincronizaba (casi un núcleo de 12) durante las mías, y tus corridas
  de la tarde coincidieron con los censos de este encargo. Las ganancias de la tabla salen de comparar el mismo paso en
  las dos corridas, no del total, que mueve el portal.

## Frente 5 · igual que GitHub, y la versión en el panel

- **El panel** muestra «versión <rama> · <commit>» en la barra de Credenciales, tomada al cargar el programa: es la del
  código que corre. LEEME.md se lo explica al colega (el mismo commit, lo mismo; la rama puede ser otra).
- **`python tests/igual_que_github.py [--rama main|estable] [--sin-suite] [--dejar]`:** clona la rama desde GitHub
  dentro de `.trabajo/igual-que-github/`, compara el commit, el árbol, cada archivo versionado byte a byte y los cambios
  sin commitear, y corre la suite en el clon. Solo `main` o `estable`, y solo si `origin` es el repo del programa: la
  suite corre el código bajado, con tu usuario.
- **La demostración con `main`, ahora:** dice DISTINTO, y es lo correcto: en GitHub `main` está en `4664942`, y aquí, siete
  commits adelante sin subir. El resultado completo, con la suite en el clon, va en el mensaje de cierre
  (`.trabajo/e93/demo_igual_main.out`). **Después de tu push, corre lo mismo: tiene que decir IGUAL** (y con `--rama
  estable` en el equipo del colega, después de mover `estable`).

## Las revisiones

| Revisión | Hallazgos | Qué se hizo |
|---|---|---|
| Código | 0 críticos o altos; 2 MEDIAS (la espera de ONE con un texto de otro campo; la versión del panel, leída en cada pedido); 5 BAJAS | Las 2 MEDIAS y 4 BAJAS, arregladas. La quinta (`_hmm_select_por_texto` elige por valor sin mirar después qué quedó) ya estaba antes: al residual. **Aprobado** |
| Seguridad | 0 críticos o altos; 3 MEDIAS (la de ONE; CMA-CGM con una ruta sin sus detalles; la herramienta corría código bajado con todo el entorno); 5 BAJAS | Todas arregladas salvo la de `_hmm_select_por_texto`, la misma de arriba |

- **Lo que propuso la revisión de seguridad para CMA-CGM no entró:** cortar por el resumen de cada ruta (`.wrap-card`).
  Medido sobre las 7 listas guardadas, ninguna elegía: cada ruta del portal trae dos resúmenes. Va en su lugar la regla
  de la lista de rutas, que da lo mismo que la del frente 2.
- **Ante la ventana del Shipper de HYUNDAI volvió la espera fija de 1,2 s:** su fila se busca en toda la página, y sin
  la espera podía tomarse una de fuera de la ventana.

Los revisores trabajaron en un clon (`.trabajo/e93/rev`), sin tocar el repo vivo.

## Compuertas

Todas sobre el árbol de cada commit, en clones congelados, con el temporal en la ruta corta de la carpeta del encargo y
el plazo de la suite en 7.200 s (`con_mas_plazo.py`).

| Commit | Suite | Censo de lo que tocó (`censo_ids.py` con `ids_tocados.py`) |
|---|---|---|
| `c227383` (1) | 1.048 pruebas, OK | 28 mutaciones, 37 pares, todos muerden |
| `51b0d2f` (2) | 1.050, OK | 12 y 12 |
| `33dabd6` (4) | 1.055, OK | 41 y 47 |
| `562f729` (5) | 1.076, OK | 43 y 43 |
| `549974b` (3) | 1.086, OK | 31 y 37 |
| `ed23303` (revisiones) | 1.090, OK | 80 mutaciones y 86 pares, todos muerden; y las 3 de la herramienta que faltaban, 3 de 3 |

- En todas, la foto de los originales sin cambios y 0 pruebas sin mutación (al final).
- **Anclas:** cada texto viejo de las 3.006 mutaciones aparece una vez en su archivo (`.trabajo/e92/anclas.py`).
- **Sonda de secretos** en el repo vivo, después de pasar los commits: `--staging`, 133 entradas, 0; `--dry-run`, 0.
- **Guarda de datos reales:** el hook en cada commit, 0. Sobre los mensajes de los commits, 0, salvo el correo de la
  línea del coautor, la dirección de atribución de Anthropic, que traen también los 20 commits ya publicados. Sobre
  este informe, 0.
- **Medido en el portal:** HYUNDAI, MSC y MAERSK, OK-EJEMPLO con el código nuevo.

## Decisiones que tomé solo

| Decisión | Por qué |
|---|---|
| Un commit más, con los arreglos de las dos revisiones | Tocaban cuatro frentes a la vez |
| Rehacer los commits de los frentes 1, 2 y 5 en el clon de trabajo | Sus censos encontraron una prueba sin mutación o una mutación que no mordía; nada estaba publicado |
| La regla de la lista de rutas en CMA-CGM, y no la del resumen | La del resumen, medida, dejaba de elegir en todas las listas reales |
| Volver a poner la espera fija ante la ventana del Shipper de HYUNDAI | Sin ella podía elegir una fila de fuera de la ventana |
| COSCO sin cambios en sus esperas | No puedo correr su modo prueba (el validador lo resuelve una persona) |
| La herramienta solo con `main` o `estable`, y solo con el repo del programa | Corre el código bajado de GitHub |
| Correr el modo prueba yo mismo, por la API del panel, una fila por naviera | Lo permitía el encargo; sin abrir una pestaña en tu navegador |

## Lo que salió mal

- **El equipo durmió de las 17:55 a las 19:53** (Kernel-Power 506 y 507, después de un cambio de fuente de energía), y
  la suite del frente 4 venció su plazo dormida. Se repitió con el equipo despierto, y pasó.
- **Tres compuertas encontraron huecos de prueba** (una prueba sin mutación en el frente 1 y otra en el 5, y una
  mutación que no mordía en el 2): cada commit se rehízo con lo que faltaba y su censo dio verde.
- **Las pruebas del frente 3 corrieron una vez con su salida tapada por un filtro:** se repitieron con la salida a un
  archivo.
- **La primera corrida en el portal abortó** por un error mío al leer la lista de hojas del panel; se corrigió y se
  repitió enseguida.
- **La compilación de todas las mutaciones,** lanzada junto a una suite, tardaba más de una hora: la detuve (el conteo
  de anclas ya había dado verde, y cada censo compila lo que corre).

## Residual

- **ONE y CMA-CGM, sin probar en el portal con sus esperas nuevas** (sus filas no llegaron a ese paso): la prueba
  conjunta.
- **`_hmm_select_por_texto` elige por valor** sin mirar si otra opción comparte ese valor ni qué quedó (de antes; las
  dos revisiones).
- **Las comprobaciones de «Named Customer» y «Sales Person»** miran un solo instante.
- **La espera de la ventana del Shipper de HYUNDAI** sigue fija: acotar su búsqueda a la ventana es otro cambio.
- **COSCO:** sus esperas, sin tocar.

## La prueba conjunta en el portal

Siempre con el lanzador de prueba, `Iniciar AQUASHIELD.bat`, nunca con el de emisión: cada fila tiene que terminar en
OK-EJEMPLO. Lo que hay que ver está en log.txt de la corrida (`logs\web_…\log.txt`). Ninguna necesita emitir.

**0. La versión:** el panel muestra «versión main · ed23303» (o el commit de este informe); en el equipo del colega,
después de mover `estable`, «versión estable · <el mismo commit>».

**1. CMA-CGM, la fila que quedaba REVISAR hoy** (frentes 2 y 3; el deslizador lo pasas tú):
- `itinerario CMA: …` y la fila sigue hasta OK-EJEMPLO, en vez de REVISAR «no disponible».
- Si la nave de verdad no está: el motivo nuevo, «el portal no ofrece la nave …» o «el portal muestra la nave … en N
  ruta(s) que no deja elegir…».
- En el panel Reefer: `temperatura reefer: …` y `ajustes reefer guardados`, sin cortes.

**2. ONE, una fila con la nave a la vista** (frente 3):
- `Type -> REEFER`, `Size -> 40FT High Cube`, `ContTipoSize -> …`, `Genset -> No` y `Nature -> Frozen`: ninguna con
  «NINGUNA de». Si una falla, avísame: esa espera vuelve a la fija y `estable` no se mueve.

**3. HYUNDAI** (frentes 1, 3 y 4): `Named Customer opciones: Select | Direct Input`, `Named Customer: 'Direct Input'`,
y las líneas «la lista quedó con …» después de elegir y antes de seguir, de «Named Customer», «HMM Sales Person» y
«Contract No». La fila, OK-EJEMPLO.

**4. MAERSK y MSC:** OK-EJEMPLO, como esta noche.

**5. COSCO:** como siempre (no cambió).

## Re-medir

- **El tiempo de ONE y de CMA-CGM** con sus esperas nuevas: `.trabajo/e93/medir_tiempos.py` sobre la corrida de la
  prueba conjunta.
- **IGUAL después del push:** `python tests/igual_que_github.py --rama main`.

## NO retroceder

- **Una espera fija se cambia por su condición con el mismo tope,** y la condición es la misma búsqueda del paso que
  sigue, contada contra lo que ya se veía antes (`_esperar_que`).
- **La tarjeta de una ruta de CMA-CGM no sube a un bloque con otra ruta** (por sus detalles, o pasando a la lista).
- **La versión del panel es la del arranque** (`VERSION_GIT`), no la de la carpeta en cada pedido.

## Reglas aplicadas

PASO 0 con veredicto por frente (CICLO en los cinco). Control positivo que aborta en cada sonda (el de CMA-CGM abortó
con la regla del resumen, y por eso no entró). Censo relativo a lo que tocó cada commit. Revisores en un clon. Datos
solo como cuentas, segundos y estados. Guarda de datos sobre los mensajes y el informe. Una medición de tiempo, con sus
salvedades dichas. Ningún comando detrás de un `cd`. Lista de tareas: esta sesión no tiene la herramienta.

## El bloque de push

El repo es público: lo subes tú. El hash que tiene que quedar en `main` es el del commit de este informe, que no puede
ir dentro de su propio commit: está en el mensaje con que cierro el ciclo.

```powershell
git -C "C:\dev\Agendamiento Reservas" log origin/main..main --format="%h %ae %ce %s"
git -C "C:\dev\Agendamiento Reservas" push origin main
git -C "C:\dev\Agendamiento Reservas" rev-parse main
git -C "C:\dev\Agendamiento Reservas" ls-remote origin refs/heads/main
```

- El primer comando tiene que mostrar 7 commits (`c227383`, `51b0d2f`, `33dabd6`, `562f729`, `549974b`, `ed23303` y
  el del informe), cada uno solo con el correo noreply, como autor y como committer.
- Después de subir, `rev-parse` y `ls-remote` tienen que dar el mismo hash.

## El bloque para mover `estable`, después de la prueba conjunta

Solo si las filas de la prueba conjunta terminaron en OK-EJEMPLO. `<commit>` es el de este informe (el mismo de
`main` después del push):

```powershell
git -C "C:\dev\Agendamiento Reservas" fetch origin
git -C "C:\dev\Agendamiento Reservas" log --oneline origin/estable..<commit>
git -C "C:\dev\Agendamiento Reservas" push origin <commit>:refs/heads/estable
git -C "C:\dev\Agendamiento Reservas" ls-remote origin refs/heads/estable
```
