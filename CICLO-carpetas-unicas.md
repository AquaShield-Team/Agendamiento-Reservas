# CICLO · Carpetas de corrida con nombre único

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-24 · **Método:** skill `metodo-ciclo` v12 ·
**Base:** `f9e1251` · **Commits:** solo el de este informe (local, sin push). **No se tocó el código.**

> Sin datos reales. De los logs reales solo se contaron líneas; ningún nombre de carpeta real sale en este
> informe. Las mediciones sobre la red se hicieron con envoltorios en memoria, sin tocar `tests/`.

## Veredicto: FRENO

Se cumple el primer FRENA SI. **El nombre único rompe dos pruebas que fijan el nombre de la carpeta**, y no se
resuelve sin cambiar lo que esas pruebas esperan. Paré antes de tocar el programa.

Las dos pruebas **ya chocan hoy sin enterarse**: su corrida cae en el mismo segundo que la de una prueba
anterior, comparten carpeta y log, y pasan igual. Medido sobre el código de hoy, en 5 corridas de sus clases:

| Prueba | Qué espera del nombre | Corrida anterior con el mismo prefijo, en su misma sandbox | Choques en 5 corridas |
|---|---|---|---|
| `test_web.TestPanelCorridas.test_corrida_de_una_hoja` | `^web_one_op_prueba_\d{8}_\d{6}$` | La prueba justo anterior (`test_corrida_con_estados_tras_el_envio`) | **4** |
| `test_consola.TestEjecutarReservas.test_reservas_por_consola` | `^reservas_cma_op_prueba_\d{8}_\d{6}$` | Seis pruebas antes (`test_error_de_escritura_se_muestra_y_queda_en_el_log`) | **1** |

Con el sufijo, cada choque da una carpeta nueva `…_2`, y esas dos expectativas caen. Con la frecuencia
medida, «10 de 10 corridas seguidas» no se cumpliría. **Cambiarlas lo decides tú** (abajo, el antes y el
después).

**PASO 0: FRENO (PREGUNTA).**

## Qué crea las carpetas de corrida

| Lugar | Nombre de la carpeta |
|---|---|
| `ejecutar_login` (consola, solo login) | `<usuario>_<AAAAmmdd_HHMMSS>` |
| `ejecutar_reservas` (consola) | `reservas_<naviera>_<usuario>_<AAAAmmdd_HHMMSS>` |
| `_web_worker` (panel web) | `web_<naviera u hoja>_<usuario>_<AAAAmmdd_HHMMSS>` |

**Qué pasa hoy si dos corridas caen en el mismo segundo.** `Registro` crea la carpeta con `exist_ok=True` y
abre `log.txt` para agregar. La segunda corrida escribe en el log de la primera. Sus capturas y su HTML van a
la misma carpeta: si se llaman igual (misma naviera, misma fila, mismo paso), **la segunda pisa la
evidencia de la primera**. No solo se mezclan.

## Qué no se rompe

- **Los generadores** (manuales, simulador y los dos videos):
  - Nombran a mano las 4 corridas de referencia, y **ninguno busca carpetas de forma dinámica**: 0 lecturas
    con `glob`, `listdir`, `iterdir`, `scandir` o `walk` sobre `logs`.
  - Control positivo: el patrón encontró la carpeta de MSC que se sabe que el simulador nombra.
  - Esas carpetas ya existen y no cambian de nombre.
- **El panel:** guarda la ruta de la corrida (`_WEB["carpeta"]` en el web, `ultima_carpeta` en el Tkinter) y
  la usa tal cual. Nunca arma ni lee el nombre.
- **`test_consola.TestEjecutarLogin.test_login_por_consola`**, que también fija el nombre
  (`^op_prueba_\d{8}_\d{6}$`): es la única prueba de su clase, con sandbox propia, así que su carpeta es la
  primera y no puede chocar.
- **`test_consola.test_todas_deja_una_sola_copia`:** con el nombre único pasa siempre. La carpeta de ONE de
  «todas» sería nueva (`…_2`) y entraría en la resta de conjuntos. Su expectativa `(6, 1, 5)` no cambia.
- **Las dos carpetas de nombre fijo** que crean `test_web` y `test_planilla` (`web_one_prueba_descarga`)
  las arma la prueba, no el programa.

## Las expectativas que cambiarían (para tu decisión)

| Prueba | Antes | Después (propuesta) |
|---|---|---|
| `test_corrida_de_una_hoja` | El nombre calza con `^web_one_op_prueba_\d{8}_\d{6}$` | Calza con `^web_one_op_prueba_\d{8}_\d{6}(_\d+)?$`, **y** la carpeta no existía antes de la corrida |
| `test_reservas_por_consola` | El nombre calza con `^reservas_cma_op_prueba_\d{8}_\d{6}$` | Calza con `^reservas_cma_op_prueba_\d{8}_\d{6}(_\d+)?$`, **y** la carpeta no existía antes de la corrida |

La segunda condición es la que hoy falta: con ella, esas pruebas habrían destapado el choque.

**La alternativa que no cambia esas dos expectativas** es que las pruebas no choquen: una sandbox por prueba
en vez de una por clase. Toca el arnés de toda la red; también es decisión tuya.

## El cambio, listo para aplicar cuando decidas

- **Una sola función**, `carpeta_corrida(prefijo)`, que usan los tres lugares:
  - Arma `<prefijo>_<AAAAmmdd_HHMMSS>` y **crea la carpeta en ese momento, en exclusiva**.
  - Si ya existe, prueba `_2`, `_3`…
  - Crearla en exclusiva evita que dos corridas simultáneas elijan el mismo nombre, cosa que mirar si existe
    y crearla después no garantiza.
- **Sin choque, el nombre es idéntico al de hoy.** El orden alfabético sigue siendo cronológico: `…_091534`,
  `…_091534_2`, `…_091535`.
- **Precedente:** `respaldar_planilla` ya hace lo mismo con las copias de respaldo, con « (2)», y
  `test_respaldos_no_se_pisan` lo vigila. Para carpetas propongo `_2`, que sigue el estilo de guiones bajos
  del nombre; si prefieres « (2)», es el mismo cambio.
- **Pruebas y defectos inyectados:**
  - Una prueba por cada uno de los tres lugares, con el reloj fijo en un segundo: dos corridas seguidas dan
    dos carpetas, la segunda con `_2`, cada log con un solo «INICIO».
  - Mutaciones: la función sin sufijo, la función con `exist_ok`, y cada lugar de vuelta a su nombre armado
    a mano.
- **Listo** sería: la red completa 10 de 10 seguidas sobre el commit y el censo completo una vez.

## FRENA 2 (otra prueba intermitente): no se llegó

No hay commit que correr 10 veces. Lo que ya está medido sobre HEAD (`CICLO-cma-reefer.md`): en 5 corridas de
la red completa, la única prueba que falló fue `test_todas_deja_una_sola_copia` (4 de 5). Los dos choques de
arriba no fallan hoy: se vuelven fallas recién con el nombre único.

## Premisas del encargo contrastadas (pieza 5)

- **«Esa prueba falla 4 de 5 veces sobre HEAD; la causa se verificó con un control»:** es lo medido en el
  ciclo anterior; no la volví a correr.
- **«Hipótesis no medida: lo mismo puede pasar en uso real, mezclando su evidencia»:**
  - **El mecanismo está confirmado.** En el código: `exist_ok=True` más el log abierto para agregar. En la red:
    las dos corridas del panel compartieron carpeta y log en 4 de 5 corridas.
  - **Es peor que mezclar:** una captura o un HTML con el mismo nombre se pisan.
  - **En uso real no pasó:** en las 6 carpetas de `logs/`, cada log tiene una sola línea «INICIO». Control
    positivo: el mismo contador da 2 en la carpeta compartida de la red y 1 en una propia.
- **Implícita: que solo `test_todas_deja_una_sola_copia` depende de esto.** Refutada: dos pruebas más comparten
  carpeta hoy (4 de 5 y 1 de 5) y pasan porque no miran adentro.
- **«Sin cambiar cómo los generadores ubican las 4 corridas de referencia»:** confirmada; no las toca. Aparte,
  el simulador nombra una quinta carpeta, `logs/cma_dev`, que no está entre las 6 de `logs/`. Va al residual.

## Universo y cobertura (pieza 3)

- **Código:**
  - Las 6 menciones de `LOGS` en `AQUASHIELD.py`: 3 crean carpetas de corrida (la tabla de arriba), 1 la
    define y 2 son el respaldo del panel Tkinter, que abre la última carpeta o `logs/`.
  - Quién lee la carpeta de una corrida: `_WEB["carpeta"]` y `ultima_carpeta`, por ruta.
  - `podar_respaldos` recorre la carpeta de la planilla, no `logs/`.
- **Generadores:** los 4 archivos, 5 carpetas nombradas (las 4 de referencia y `cma_dev`), 0 lecturas
  dinámicas.
- **Pruebas:** 3 aserciones sobre el formato del nombre, 1 `glob` sobre `reservas_*` (la de «todas») y 2
  carpetas de nombre fijo creadas por las propias pruebas.
- **Choques medidos:** 5 corridas de `TestPanelCorridas` y de `TestEjecutarReservas`, que es donde viven las
  dos pruebas que fijan el nombre y que pueden chocar. No medí en la red completa: cada clase tiene su propia
  sandbox, y el orden dentro de la clase es el mismo.
- **Logs reales:** 6 de 6 carpetas, contando líneas; nada de su contenido salió a la pantalla.

## Re-medir (pieza 1)

- **Los lugares que crean carpetas:** buscar `LOGS` y `strftime("%Y%m%d_%H%M%S")` en `AQUASHIELD.py`.
- **Los choques:** envolver en memoria `test_corrida_de_una_hoja` y `test_reservas_por_consola`:
  1. Antes de la prueba, anotar las carpetas de su prefijo que ya existen en la sandbox.
  2. Después, ver si la carpeta de la corrida estaba entre ellas.
  3. Correr sus dos clases 5 veces.
  - Da 4 y 1.
- **Los logs reales:** contar «· INICIO ·» en cada `logs/*/log.txt`. Da 1 en las 6. Control: la carpeta
  compartida de `test_corrida_de_una_hoja` da 2.
- **Los generadores:** buscar `logs/<carpeta>` y lecturas dinámicas de carpetas en los 4 archivos.

## NO retroceder (pieza 2)

- **No lo arregles en la prueba** (aflojando el `glob`, esperando un segundo o separando sandboxes) sin tu
  decisión: el programa comparte carpeta también en uso real, y ahí pisa evidencia.
- **No resuelvas el choque con el segundo siguiente libre:** el nombre diría una hora que no es.
- **No crees la carpeta después de mirar si existe:** dos corridas simultáneas podrían elegir el mismo nombre.
  Va en exclusiva.

## Defectos de instrumento cazados (pieza 4)

1. **La barra invertida de Bash.** Mi primer escaneo de los generadores llevaba `[/\\]` y la herramienta lo
   dejó en `[/\]`. Falló con un error, no con un cero: lo reescribí como archivo.
2. **Un detector que adivina una carpeta.** `test_reservas_por_consola` guarda su carpeta en una variable
   local. Para saber cuál era, el envoltorio toma la carpeta de su prefijo con el log más reciente. En un
   choque es la compartida, que es la que se acaba de escribir: el 1 de 5 es correcto, pero depende de esa
   suposición.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| El nombre único de las carpetas de corrida | FRENO: rompe dos expectativas | …decides el antes y el después de arriba, o la sandbox por prueba |
| `test_todas_deja_una_sola_copia` sigue fallando (4 de 5) | Se arregla con el cambio de arriba | …se aplica el cambio |
| Dos pruebas comparten carpeta sin enterarse | Idem | …se aplica el cambio con la condición «la carpeta no existía» |
| El simulador nombra `logs/cma_dev`, que no está en `logs/` | Fuera del encargo | …se regenera el simulador |
| Otra prueba intermitente | No medido sobre un commit (5 corridas de HEAD: ninguna otra) | …se corren las 10 del cambio |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v12**:
- **PASO 0 con veredicto de cuatro valores:** FRENO (PREGUNTA).
- **Control positivo:** en el escaneo de los generadores y en el contador de «INICIO».
- **Todo salto silencioso lleva contador:** las dos pruebas que chocan pasan en silencio. El conteo de choques
  es su contador.
- **Un número fijo deja de morder:** el nombre al segundo alcanzaba mientras las corridas tardaban más de un
  segundo entre sí.
- **Declarar las premisas refutadas:** la prueba de «todas» no era la única afectada.
- **FRENAR cuando la decisión es de negocio:** cambiar lo que esperan dos pruebas.
- **El push se entrega, no se hace:** no hay remoto.

Reglas propias del módulo (`CLAUDE.md`): las pruebas son fotos (un cambio de expectativa va con su antes y
después), casos sintéticos y la sonda antes del commit.

**Choques entre reglas:** ninguno. El freno cae antes del cambio.

## Entregable (pieza 8)

Este `.md`, sin renderizar, y la nota de `CLAUDE.md` sobre la prueba que depende del reloj, puesta al día.
Pasan la sonda de staging antes de su commit.
