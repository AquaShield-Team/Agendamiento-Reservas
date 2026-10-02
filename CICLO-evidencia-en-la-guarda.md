# CICLO · Evidencia en la guarda del candado

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-24 · **Método:** skill `metodo-ciclo` v12 ·
**Base:** `00970d4` · **Commits** (locales, sin push; el repo no tiene remoto):
- `7b3e3e2` la evidencia en la guarda de las seis navieras;
- `c802389` el HTML junto a la captura del paso sin objetivo;
- `1ccf195` la poda del HTML de más de 30 días;
- el de este informe.

> Sin datos reales. De `logs/` solo se contaron carpetas, extensiones y el ancho y alto de las capturas, nunca
> su contenido. Los nombres de carpeta se imprimieron con su forma (letras y dígitos reemplazados). Las
> pruebas usan páginas falsas y carpetas sintéticas; el experimento de la captura, una página sintética.

## Veredicto

- **Hecho en las seis navieras.** Justo antes de la guarda, se abra o no el candado, cada reserva deja
  `<nav>_f<fila>_guarda.png`, con la página completa, y el HTML completo de la página y de cada marco, con sus
  raíces shadow (`<nav>_f<fila>_guarda.html` y `_marco<n>.html`). Queda en la carpeta de la corrida, dentro de
  `logs/`. Los prefijos son los de las capturas: `one`, `msc`, `cma`, `cosco`, `hmm` y `mk`.
- **El paso que corta por objetivo no encontrado** deja ahora también su HTML junto a su captura
  `<nav>_f<fila>_sin_objetivo.png`.
- **Sin clics, sin navegación y sin esperas.** Si guardar falla, lo avisa en pantalla y en `log.txt` y la
  reserva sigue igual.
- **La poda** borra solo los `.html` de las carpetas de corrida con más de 30 días. `log.txt` y las capturas no
  se borran nunca, y las 4 corridas de referencia de los generadores no se tocan, con una prueba que lo vigila.
- **`test_candado` y `test_clics` pasan sin cambiar su expectativa.** Ninguna expectativa de una prueba que ya
  existía cambió.
- **Ningún FRENA SI se cumplió.** El primero lo miré de cerca: la captura de página completa dispara un evento
  `resize` en la página, sin cambiarle el tamaño. Detalle y por qué no es un freno, abajo.
- **Censo completo final sobre `1ccf195`:** **pasó.** Corrió de 14:55 a 15:24, con el árbol limpio antes y
  después. La copia sin mutar pasa las 236 pruebas. Las 438 mutaciones, en 526 pares, muerden todas, y no queda
  ninguna prueba sin mutación. 0 cambios en los originales.

**PASO 0: CICLO.**

## Lo medido antes de tocar código

1. **La evidencia de hoy solo existe después del envío.** `_guardar_evidencia` se llama solo desde
   `_resultado_envio`, después de la guarda (`test_envio` lo vigila). En `logs/` hay 6 carpetas de corrida, con
   316 capturas, 6 `log.txt` y **0 HTML**.
2. **La página completa antes de la guarda es nueva.** Cada reservador ya toma una captura `full=True` justo
   antes de su guarda. Pero `full=True` solo da la página completa con `AQUASHIELD_CAPTURA_FULL` o
   `AQUASHIELD_DESCUBRIR`. En `logs/`, **0 de 44** capturas de antes de la guarda son de página completa (1 de
   316 en total, de otro paso). Se midió por la proporción alto/ancho del PNG.
3. **Qué le hace a la página cada forma de guardar evidencia.** Página sintética, el Chrome instalado (153)
   abierto como lo abre el programa (`no_viewport`, `_args_chrome()`), y cada acción con los contadores en cero:

   | Acción | `resize` | Otros eventos y cambios |
   |---|---|---|
   | HTML con `_JS_HTML_COMPLETO` | 0 | 0 mutaciones del DOM |
   | `page.content()` | 0 | 0 |
   | Captura de la ventana (la de hoy) | 0 | 2 mutaciones: Playwright oculta el cursor de texto y lo repone |
   | Captura de página completa | **1** (y 1 del `visualViewport`) | las mismas 2 mutaciones |
   | Control: `set_viewport_size` | 1 | el alto cambia de 849 a 700 |

   Con la captura de página completa, el alto que ve la página no cambia (muestreado en cada cuadro). Tampoco
   cambian el scroll, el foco, el valor del campo, las media queries ni el `IntersectionObserver`: nada que
   dispare una carga perezosa. Salió igual con Chrome oculto y visible. El control positivo (`set_viewport_size`)
   sí cambia el alto; sin él, el experimento aborta.
4. **Una unión de Windows se ve como carpeta.** En Python 3.13, para una unión `is_dir(follow_symlinks=False)`
   da True e `is_symlink()` da False; solo `is_junction()` la delata. Sin esa revisión, la poda saldría de
   `logs/`: la mutación que la quita borra un archivo de afuera a través de la unión.
5. **Las carpetas que nombran los generadores:** 5. Las 4 con forma de carpeta de corrida son las de referencia.
   La quinta, `cma_dev`, no existe y no tiene fecha: la poda no la mira nunca.

## El freno que miré de cerca

El FRENA SI dice: «guardar la evidencia exige esperar o interactuar con la página de un modo que cambie el flujo
antes de la guarda».

- **El HTML no toca nada:** 0 eventos, 0 mutaciones.
- **La captura de página completa sí hace algo que la de la ventana no hace:** dispara un evento `resize`, con
  el mismo tamaño. Los manejadores de `resize` del portal corren, pero ven las mismas medidas de antes.
- **Por qué no lo tomo como freno:** en la página medida no cambia nada: ni el tamaño, ni el scroll, ni el foco,
  ni los valores. El programa tampoco espera a la página: la captura tarda lo que tarda. En la página sintética
  fueron 0,11 s; en portales largos, entre 1 y 4 s, según la nota del propio programa (no lo volví a medir).
  - Con el candado cerrado, después de la evidencia solo viene el `return` de la guarda: no hay flujo que
    cambiar.
  - Con el candado abierto, lo siguiente es el clic en el botón de envío por su selector.
- **Lo que no está medido:** un portal cuyo JavaScript reaccione a un `resize` del mismo tamaño. Antes de abrir
  el candado, decide si mantienes la página completa o pasas a la captura de la ventana, que no dispara nada.
  Es un cambio de una línea. Mi recomendación es mantenerla: el evento no movió nada medible, y la primera
  corrida con el candado cerrado deja en la misma carpeta la captura del paso anterior y la de la guarda para
  compararlas.

## Qué cambió

**`7b3e3e2` · la evidencia en la guarda:**
- `_evidencia_antes_de_la_guarda(page, reg, nombre)`: la captura de la página completa y el HTML de la página y
  de cada marco. Nunca levanta una excepción: si algo falla, lo avisa y vuelve.
- Seis llamadas, cada una como sentencia suelta justo antes de `if not es_modo_emision():`. En ONE va dentro de
  «si llegó a Review Booking», donde está su guarda. En COSCO va después del «Detener» del operador.
- `_guardar_html_completo`: el HTML de la página y de los marcos, ahora fuente única de la evidencia tras el
  envío y de la de la guarda.
- `Registro.captura(..., pagina_entera=True)` pide la página completa sin la variable de entorno, y la captura
  devuelve si la guardó.

**`c802389` · el paso sin objetivo:** `_sin_clic_a_ciegas` usa la misma función, con la captura de la ventana
(como antes) y el HTML.

**`1ccf195` · la poda:**
- `podar_html`: solo carpetas directas de `logs/` con la forma de `carpeta_corrida`, que no sean de referencia,
  ni enlaces ni uniones. Dentro, solo los archivos directos terminados en `.html`. La antigüedad sale de la fecha
  del nombre.
- `CORRIDAS_DE_REFERENCIA`: las 4 carpetas de los generadores.
- `_podar_html_viejo`: corre al empezar cada corrida de reservas, por consola y por el panel web. Avisa lo que
  borró y lo que no pudo borrar, y nunca detiene la corrida.

**Lo que cambia de comportamiento:**

| Qué | Antes | Ahora |
|---|---|---|
| Antes de la guarda, en las seis navieras | la captura del paso, de la ventana | además, `<nav>_f<fila>_guarda.png` (página completa) y su HTML |
| Paso sin objetivo (ONE, MSC y CMA) | `<nav>_f<fila>_sin_objetivo.png` | además, su HTML |
| `log.txt` y pantalla | — | «evidencia en la guarda: … N de M HTML …»; si algo falla, «⚠ … La reserva sigue igual; si necesitas medir esta pantalla, vuelve a correr la fila con el candado cerrado.» |
| `.html` en `logs/` | no se borraban (no había) | al empezar una corrida de reservas se borran los de más de 30 días; aviso «Borré N HTML de evidencia…» |
| Tiempo por reserva | — | una captura de página completa más (1 a 4 s en portales largos, según la nota del programa) y el HTML |

**Sin clics nuevos.** El estado de cada reserva no cambia: la evidencia es una sentencia suelta cuyo resultado
no decide nada.

## Las expectativas

- **De las pruebas que ya existían, ninguna cambió.** `test_candado`, `test_clics` y `test_envio` pasan tal
  cual.
- **Una prueba nueva cambió entre commits:** `test_evidencia.TestCadaReservadorLaDeja.test_solo_ahi`.
  - Antes (`7b3e3e2`): los seis reservadores, cada uno con su prefijo.
  - Después (`c802389`): los seis y `_sin_clic_a_ciegas`. La llamada exacta de cada reservador la siguen mirando
    sus seis pruebas.
- **Mutaciones que existían y solo cambiaron su texto «viejo»** (el mismo defecto, anclado donde quedó el
  código):

  | Mutación | «viejo» antes | «viejo» ahora |
  |---|---|---|
  | `evidencia-sin-captura` y `evidencia-captura-de-pagina-entera` | la captura seguida de `principal` | la línea de la captura sola |
  | `evidencia-sin-contador` | `y {guardados} de {1 + len(marcos)} HTML` | `evidencia del envío: {nombre}.png y {guardados} de {total} HTML` |
  | `evidencia-falla-callada` y `evidencia-un-fallo-corta` | el aviso con «tras el envío» fijo | el aviso con `{momento}` |
  | `evidencia-antes-de-la-guarda` | anclada a la captura `msc_f{f}_5_summary` | anclada a la evidencia de la guarda de MSC; mete igual `_guardar_evidencia` antes de la guarda |
  | `corte-sin-captura` | la línea `reg.captura(... _sin_objetivo)` | la llamada a la evidencia del decorador |
  | `poda-antiguedad-por-fecha-de-archivo` (respaldos) | `key=lambda e: e.name)` | lo mismo, precedido de su línea de `PATRON_RESPALDO` |
  | `poda-sin-aviso-de-borrados` (respaldos) | `if borrados: reg.info(` | lo mismo, más «Borré {len(borrados)} copia(s)» |

  Las dos de respaldos quedaron ambiguas porque el código nuevo repite esos trozos. Lo delató el prechequeo,
  antes del censo.

## Los defectos inyectados

42 mutaciones nuevas, cada una con su prueba:
- **21 de la guarda:** la captura de la ventana en vez de la página completa, sin HTML, otro JavaScript, una
  espera o una tecla, sin protección, un aviso callado, la evidencia quitada de cada una de las seis navieras,
  movida dentro de la guarda, sin la fila, usada para decidir, o llamada también tras el envío.
- **3 del paso sin objetivo:** sin HTML, con la página completa, y sin protección.
- **18 de la poda:**
  - qué borra: todo, recursivo, sin antigüedad, con 29 o 31 días;
  - dónde: un patrón flojo, siguiendo uniones o enlaces, la referencia tocada o una que falta;
  - los errores: uno que corta o que se calla, sin `logs/`;
  - la corrida: sin aviso, una falla que la corta, un error callado, sin la llamada en la consola o en la web.

La red pasa de 215 pruebas, 396 mutaciones y 471 pares a **236 pruebas, 438 mutaciones y 526 pares**.

Gate de cada commit:
- la suite completa, verde;
- el censo filtrado a las mutaciones nuevas y modificadas, todas mordiendo por su razón;
- la sonda de secretos en 0 sobre el árbol y el staging.

| Commit | Suite | Censo filtrado |
|---|---|---|
| `7b3e3e2` | 227 pruebas | «evidencia»: 43 mutaciones, 56 pares · «captura»: 18 y 24 |
| `c802389` | 229 pruebas | «corte-»: 8 y 10 · «test_solo_ahi»: 8 y 15 |
| `1ccf195` | 236 pruebas | «poda-»: 30 y 31 · «referencia-»: 1 y 2 |

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\correr.py --mutaciones
python -m unittest test_evidencia      # desde tests\
```

- **`logs/`:** recorrer las entradas directas de `logs/` y los archivos de cada carpeta, y contar por
  extensión. Leer el ancho y el alto de cada PNG de su cabecera, y llamar «página completa» a la que es más alta
  que 0,6 veces su ancho.
- **El experimento de la captura:**
  - una página sintética con contadores de `resize`, `scroll`, `focus`, `blur`, media query,
    `IntersectionObserver` y mutaciones, cargada con `set_content`, sin red ni puerto;
  - el Chrome instalado, con `no_viewport` y `_args_chrome()`, y un perfil temporal;
  - cada acción con los contadores en cero, y `set_viewport_size` como control positivo.
- **La unión:** `_winapi.CreateJunction` en una carpeta temporal, y mirar `is_dir(follow_symlinks=False)`,
  `is_symlink()` e `is_junction()`.
- **Las carpetas de los generadores:** `logs/([A-Za-z0-9_]+)/` sobre los 4 generadores.
  `TestCorridasDeReferencia` lo hace en cada corrida de la red.

## NO retroceder (pieza 2)

- **No llames `_guardar_evidencia` antes de la guarda.** Espera el número de reserva y decide con lo que ve;
  antes de la guarda va `_evidencia_antes_de_la_guarda`, que solo lee.
- **No le agregues a `_evidencia_antes_de_la_guarda` una espera, una tecla, un clic ni otro JavaScript:**
  `test_solo_lee_sin_clics_ni_navegacion_ni_esperas` cae.
- **No uses su resultado para decidir.** Es una sentencia suelta; si falla, la reserva sigue igual.
- **En la poda, no quites `is_junction()`:** medido, una unión se ve como carpeta y la poda saldría de `logs/`.
- **No hagas recursiva la poda, no la hagas por la fecha del archivo y no saques una corrida de
  `CORRIDAS_DE_REFERENCIA`** mientras un generador la nombre.

## Premisas del encargo contrastadas (pieza 5)

- **«La evidencia HTML y captura solo se guarda después del envío»:** confirmada. Solo la llama
  `_resultado_envio`, y en `logs/` hay 0 HTML.
- **«Sin clics ni navegación»:** se cumple. Lo que no se cumple del todo es «solo lee»: la captura de página
  completa dispara un `resize` del mismo tamaño, medido y declarado arriba. La captura de la ventana, la de
  siempre, ya cambiaba dos veces el estilo del cursor de texto y lo reponía.
- **«Las 4 corridas de referencia de los generadores»:** confirmada. Son 4 con forma de corrida. Los generadores
  nombran una quinta carpeta, `cma_dev`, que no existe y que la poda no puede alcanzar.
- **«Una captura de página completa»:** hoy la captura de antes de la guarda es de la ventana (0 de 44 de página
  completa). La de la guarda es la primera de página completa antes de la guarda sin la variable de entorno.

## Universo y cobertura (pieza 3)

- **Reservadores:** 6 de 6 dejan la evidencia en la guarda. Pasos sin objetivo: los 3 reservadores que cortan
  (ONE, MSC y CMA); COSCO, HYUNDAI y MAERSK no cortan.
- **`logs/`:** 6 entradas, las 6 carpetas de corrida, sin uniones ni enlaces. Dentro: 316 PNG, 6 `log.txt`, 0
  HTML y 0 subcarpetas. Descartados: 0.
- **Generadores:** 4 de 4 leídos; 5 carpetas nombradas.
- **El experimento:** una página sintética, un Chrome (153), oculto y visible. **No se midió sobre los portales
  reales**, porque exigiría correrlos.

## Defectos de instrumento cazados (pieza 4)

1. **El patrón de los generadores tragaba código.** `logs[/\\]+([^/\\"']+)` también calzaba con la clave
   `"logs": [` y se llevaba las líneas siguientes. Lo acoté a `logs/([A-Za-z0-9_]+)/`.
2. **«Página completa» por el alto confundía la escala.** 5 capturas de MSC salían de página completa por ser
   más altas que la ventana, pero eran la ventana a escala 1,5 (2893 × 1566 contra 1929 × 1044). Lo corregí
   midiendo la proporción: 0 de 44.
3. **El código de salida tras una tubería.** En el commit `c802389` leí `$?` después de `| tail`, que da el código
   de `tail` y no el de la sonda. La salida mostraba 0 hallazgos. La volví a correr sin tubería sobre el mismo
   contenido: 0 y 0. En `1ccf195` la capturé bien. Me volvió a pasar al revisar el voseo de este informe
   (`grep … | head`). Ahí vale lo que se imprime, y no se imprimió ninguna línea.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| El `resize` de la captura de página completa en los portales reales | Medido solo en una página sintética | …un portal cambia entre la captura del paso y la de la guarda, o decides la captura de la ventana antes de abrir el candado |
| 1 a 4 s más por reserva | La captura de página completa de un portal largo (nota del programa, no re-medida) | …el tiempo de una corrida molesta |
| El HTML de un marco puede esperar a que el marco tenga su contexto (Playwright no pone plazo a `evaluate`) | Igual que la evidencia tras el envío desde `CICLO-estado-tras-envio.md`; nunca se vio | …una corrida se queda en «evidencia en la guarda» |
| El panel Reefer de CMA queda en HTML solo si CMA corta en un paso Reefer, o si el panel sigue en la página en la guarda | La decisión fue la guarda y los pasos que cortan | …su HTML no aparece en ninguno de los dos |
| ONE que no llega a Review Booking no deja evidencia de guarda | No llega a su guarda | …hace falta medir ese caso |
| La copia de los 4 nombres en `CORRIDAS_DE_REFERENCIA` | Ver el choque de reglas abajo | …cambia un generador: la prueba cae |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v12**:
- **PASO 0 antes de tocar código:** la evidencia de hoy, las capturas de `logs/`, el experimento, la unión y los
  generadores.
- **Control positivo que aborta:** `set_viewport_size` en el experimento, y «el instrumento no ve las carpetas
  de los generadores» en la prueba de referencia.
- **Todo salto silencioso lleva contador:** 0 descartados en `logs/`, y la poda cuenta lo que no pudo borrar.
- **El negativo tiene que morder, de a uno por proceso:** censos filtrados por commit, con el motivo de cada
  mutación revisado.
- **El censo de guardianes:** cada pieza nueva tiene al menos una mutación que la apaga.
- **Un chequeo de sintaxis no prueba el contrato:** las pruebas cargan el programa y corren la evidencia y la
  poda sobre páginas y carpetas falsas.
- **El cambio y su guardián en la misma operación:** cada commit con sus pruebas y mutaciones.
- **Cada reemplazo afirma su viejo una vez, y el EOL se verifica en binario:** con el prechequeo, y CR = 0 en
  cada commit.
- **Todo registro es una hipótesis:** la nota «1 a 4 s» del programa se cita como nota y no como medición mía.
- **Se declaran el residual y las premisas.**

Reglas propias del módulo (`CLAUDE.md`):
- las pruebas son fotos;
- toda prueba nueva lleva su mutación;
- casos sintéticos;
- nunca se importa el programa desde la raíz;
- la sonda antes de cada commit.

**Choques entre reglas:** uno. «Fuente única, no copia verificada» pediría que la poda leyera la lista de
referencia de los generadores. Pero los generadores no son parte del programa, que puede correr empaquetado y
sin ellos, y cambiarlos queda fuera del encargo. Lo resolví con una copia verificada:
`CORRIDAS_DE_REFERENCIA` en el programa y una prueba que la compara en las dos direcciones con lo que nombran
los generadores. Si alguien cambia un generador, la red cae.

## Entregable (pieza 8)

Este `.md`, sin renderizar, y `CLAUDE.md` puesto al día:
- la evidencia en la guarda;
- el HTML del paso sin objetivo;
- la poda y las corridas de referencia;
- la red en 236 pruebas.

## Lo que tienes que correr

**Primero, confirma que el candado está cerrado:**
1. Abre el programa con `Iniciar AQUASHIELD.bat`, nunca con `Iniciar AQUASHIELD_EMISION.bat`.
2. En `config.json`, `opciones → emitir_reservas` tiene que estar en `false` o no estar.
3. Recarga el panel justo antes de correr. Arriba tiene que decir **«🛡️ Modo Seguro Activo»**. Si dice «🔴 MODO
   EMISIÓN REAL ACTIVO», no corras: alguna de las tres llaves está abierta. Ese aviso lo calcula el mismo
   proceso que va a correr las reservas, con las tres llaves: la variable de entorno, el argumento y
   `config.json`.
4. Al terminar, cada fila que llegó a la guarda dice en el registro «Me DETENGO en … (NO se pulsa …)». Esa línea
   confirma que el candado estaba cerrado. «DETENER» no sirve de control: «🔴 MODO EMISIÓN REAL» sale justo
   antes del clic de envío. Por eso el paso 3 es el que cuenta.

**Después, corre una fila en cada naviera: ONE, CMA, COSCO y MAERSK.** Pueden ser cuatro corridas de una hoja o
una hoja CONSOLIDADO con las cuatro filas. En CMA elige una fila con nave: sin nave, corta antes, en el
itinerario.

**Los archivos que van a quedar**, en `logs\web_<nav>_<usuario>_<AAAAmmdd_HHMMSS>\` (o en una sola carpeta
`web_todas_…` si corres CONSOLIDADO):

| Naviera | Si llega a la guarda | Si corta antes | Lo que se mide ahí |
|---|---|---|---|
| ONE | `one_f<fila>_guarda.png`, `.html` y `_marco<n>.html` | `one_f<fila>_sin_objetivo.png` y `.html` | Si corta en «Contrato de ONE», ese HTML muestra el campo real. Si el log dice «contrato ONE: escrito … en Otros Contratos ✓», el campo tiene `name=contractNo`. |
| CMA | `cma_f<fila>_guarda.*` | `cma_f<fila>_sin_objetivo.*` | Si corta en «I Agree», el HTML de la revisión sin la casilla. Si corta en un paso Reefer, el panel Reefer. Si llega a la guarda, la revisión completa. |
| COSCO | `cosco_f<fila>_guarda.*`, con el formulario `bkg2` como marco | — (COSCO no corta) | Los campos de Booking Details antes de Submit. |
| MAERSK | `mk_f<fila>_guarda.*` | — (MAERSK no corta) | Las dos casillas de la revisión con sus raíces shadow, para elegir la de términos por su texto. |

- **En `log.txt`**, la línea «evidencia en la guarda: … N de M HTML (…; K sin raíces shadow)» dice si se guardó
  todo. Si K es mayor que 0, ese HTML no trae las raíces shadow.
- **Los `.html` se borran solos a los 30 días.** Si los necesitas más tiempo, cópialos fuera de `logs/` y fuera
  del repo. Traen datos reales: nunca al repo.
- **Cuando termines, avísame y mido sobre esos HTML.**
