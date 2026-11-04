# Encargo 96 · El contrato por defecto, en gris, en Credenciales

**Base:** `AquaShield-Team/Agendamiento-Reservas` @ `6c5d68a` · árbol limpio al recibir el encargo. El cambio y este
informe van en el commit que le sigue. En GitHub, `main` en `6c5d68a` y `estable` en `77d5801` (`ls-remote`, al abrir),
como dice el registro. Hecho con `metodo-ciclo` v40, la misma del disco.

Datos: todo inventado. Los contratos de las pruebas y de los paneles de prueba son de la forma `CT-USA-1`; no se leyó el
`config.json` de este equipo.

## Lo que salió

| Pregunta | Respuesta |
|---|---|
| ¿La casilla «Contrato» vacía muestra el contrato por defecto? | Sí, en gris, «por defecto: …», en ONE, MSC y HYUNDAI, si `contratos_por_defecto` trae uno para esa naviera. Sin uno, la casilla queda como antes (sección 1). |
| ¿Se guarda en la fila del operador? | No: es el texto de ayuda de la casilla, no su valor. Al guardar, la casilla vacía se guarda vacía (medido en las pruebas y en un navegador; sección 2). |
| ¿Y ONE, que tiene dos? | Los muestra los dos: «por defecto: USA … · otros …». Su casilla reemplaza solo el de los destinos USA (sección 3). |

## 1. Qué cambió

- `GET /api/credenciales` trae, con cada naviera, `por_defecto`: el texto «por defecto: …», o vacío
  (`_contrato_por_defecto_a_la_vista`). Lo arma con las mismas funciones con que lo usa cada reservador:
  `_contrato_por_defecto` para ONE (`one_usa` y `one_otros`) y MSC (`msc`), y `_hmm_contrato` para HYUNDAI, que no
  cuenta un contrato sin ninguna letra ni cifra. Así, lo que muestra la casilla es lo que el programa usaría.
- Sin avisar si falta la llave: el aviso de `_contrato_por_defecto` caería en el `log.txt` de una corrida en curso (como
  el aviso de HYUNDAI del encargo 95).
- Cada contrato, como lo muestran los motivos de HYUNDAI (`_hmm_contrato_a_la_vista`): los espacios de a uno, hasta 40
  caracteres, y cada carácter de control o invisible como «?».
- La página (`abrirCred`) lo pone como `placeholder` de la casilla, y el mismo texto en su `title` (se lee entero al
  pasar el mouse). El gris es el que ya tenían los textos de ayuda de Credenciales («sin clave»): `--text-muted`, en
  cursiva.
- El cuadro pasó de 860 a 960 px y la columna Contrato al 36 % (sección 3).

## 2. Medido en un navegador

Con una copia del programa en una sandbox (`soporte.cargar`, `.trabajo/e96/panel_cred.py`), contratos por defecto
inventados, en el navegador integrado de la app (Chromium):
- con los cuatro contratos por defecto, ONE, MSC y HYUNDAI muestran su texto en gris, y CMA-CGM, COSCO y MAERSK, nada;
- después de «Guardar», `GET /api/credenciales` da el contrato vacío en las seis navieras del operador;
- sin contratos por defecto (`panel_cred.py vacio`), ninguna casilla lleva texto de ayuda ni `title`;
- contraste del gris sobre el fondo de la casilla: 5,65 en el tema claro y 4,82 en el oscuro (mínimo, 4,5);
- la página no desborda a 1366, 1024 ni 375 px.

## 3. ONE y el ancho de la casilla

**ONE tiene dos contratos por defecto, y su casilla reemplaza solo uno.** `_determinar_contrato_one` toma, para un
destino de Estados Unidos, `contrato_usa` de las credenciales, después la casilla y después `one_usa`; para los demás
destinos, `contrato_otros` de las credenciales y después `one_otros`, nunca la casilla. Por eso la casilla de ONE dice
los dos, con su rótulo: «por defecto: USA … · otros …». La regla no cambió; si la casilla debería reemplazar también el
de los demás destinos es una decisión del dueño (abajo).

**El texto de ONE no cabía.** Medido en Chromium, con el cuadro de 860 px y las tres columnas iguales: a 1366 px la
casilla dejaba 218 px para el texto, y «por defecto: USA ABC1234567 · otros ABC1234567» (dos códigos de 10 caracteres,
el largo de los contratos de la cuenta) pide 282. Con el cuadro a 960 px y la columna Contrato al 36 %, deja 297 px, y a
1024 px, 290; Usuario y Clave pasan de 236 a 247 px. En un teléfono (375 px) el cuadro queda igual de apretado que
antes, sin desbordar la página; el texto entero sigue en el `title`.

## 4. Las compuertas

Cada una en un clon de `.trabajo/e96` con el árbol del commit (`clon_compuerta.py`, que compara cada archivo con el del
repo vivo por su blob), con `compuerta.py`: la suite entera (`tests/correr.py`, con el plazo de 7.200 s) y después el
censo de las mutaciones que tocan lo cambiado o nombran una prueba que cambió. Las corrió el ayudante mecánico, con el
envoltorio de salida literal.

**c1** (el cambio con los arreglos de las revisiones; 2026-11-04, de 08:58 a 09:46):
- Censo: 20 mutaciones (las 18 del encargo, y `cred-expone-la-clave` y `e61-credenciales-sin-operador-calla`, que
  tocan el mismo código), 22 pares: **los 22 muerden**, y el control sin mutar pasa. Originales sin cambios.
- Suite: **1.115 pruebas, 2 fallas**, en 2.586 s:
  - `test_ayudantes.TestContratosPorDefecto.test_el_programa_ya_no_los_trae`: una foto de quién le pide un contrato a
    `_contrato_por_defecto`, y `_contrato_por_defecto_a_la_vista` es un llamador nuevo. Mío: no corrí esa clase antes
    de la compuerta. La foto se actualizó en el mismo cambio, y la clase pasa.
  - `test_web.TestArranqueDelPanel.test_panel_en_el_puerto_siguiente_como_hoy` (panel de prueba, ocioso): el panel de
    un proceso hijo no contestó en sus 40 s. El cambio no toca el arranque. El equipo estaba cargado por otras dos
    sesiones (la suite de Control Congelado, desde las 09:18, y un censo de Fresco), y esta suite tardó 2.586 s, el
    doble de lo normal; sin eventos de espera de Windows en la ventana (0 de Kernel-Power, con el control del día en
    98). Sola, la prueba falló 1 de 3 veces, y cada vuelta tardó de 90 a 122 s: `CLAUDE.md` ya anota que con el equipo
    cargado tarda de 100 a 134 s.

**c2** (con la foto actualizada; de 09:57 a 10:44, con las otras dos sesiones todavía corriendo):
- Suite: **1.115 pruebas, OK** (1 saltada, la de siempre), en 2.543 s. Originales sin cambios.
- Censo: 27 mutaciones (las 20 de c1 y las 7 que nombran la foto de los contratos, sumadas a mano), 31 pares: **los 31
  muerden**, y el control sin mutar pasa.
- Después de c2 solo cambió este informe (las secciones 4 y de defectos). La guarda de datos y la sonda de secretos
  se corrieron sobre el árbol final, antes del commit, y el hook de la guarda, sobre el índice del commit.

## 5. Las revisiones

Las dos, en clones de `.trabajo/e96` (`revision2` y `revision3`), sobre el cambio antes de los arreglos de abajo.

**Código (`code-reviewer`): aprueba, sin CRÍTICO, ALTO ni MEDIO.** Comprobó que cada naviera muestra lo que usa su
reservador, que las 18 anclas nuevas aparecen una vez y compilan, y aplicó a mano 4 mutaciones: las 4 tumban su prueba.
Cuatro BAJOS:
- HYUNDAI con «-» en la casilla: al RESIDUAL (ya pasaba antes).
- ONE con `contrato_usa` o `contrato_otros` del operador: al RESIDUAL.
- `e96-msc-avisa` caía por un `JSONDecodeError` (el 500 no es JSON), no por su aserción: arreglado, la prueba lee
  primero el estado y el texto, y su mensaje dice por qué.
- Una línea de 123 caracteres en `test_web.py`: arreglada. El `CLAUDE.md` (que su clon no traía todavía) y el número
  de pruebas, actualizados.

La primera vuelta de esta revisión se trabó (10 minutos sin avanzar, sin informe); no dejó procesos ni cambios en su
clon, y se relanzó con un tope de 5 minutos por comando.

**Seguridad (`security-reviewer`): sin CRÍTICO, ALTO ni MEDIO.** Probó el servidor de una copia en sandbox: `esc`
escapa el texto en el atributo, otra página no puede leer la respuesta (403 en cinco formas de pedirla de afuera), no
cae ninguna línea en el registro de una corrida, y los tipos raros y los controles Unicode dan vacío o «?». La guarda de
datos sobre su clon: 136 archivos, 0 hallazgos. Tres BAJOS, los tres al RESIDUAL: los contratos por defecto salen por
la API a otro programa del equipo, un contrato enorme hace lento el cuadro, y los rellenos invisibles que Python cuenta
como letras. Pidió aclarar que los «10 caracteres» del comentario del CSS son de códigos inventados: aclarado. Y que la
sonda de secretos se corra en el repo vivo antes del commit, porque su clon no tiene `config.json`: está en la sección 4.

## Decisiones que tomé solo

| Decisión | Por qué |
|---|---|
| ONE muestra los dos contratos por defecto, con su rótulo «USA» y «otros». | ONE tiene dos (`one_usa` y `one_otros`), y el formato «por defecto: <número>» no alcanza para dos sin decir cuál es cuál. Con la casilla vacía, el programa usa uno o el otro según el destino. |
| El mismo texto va en el `title` de la casilla. | Si el cuadro es angosto, el texto de ayuda se corta; al pasar el mouse se lee entero. |
| El cuadro pasó a 960 px, y la columna Contrato al 36 %. | El texto de ONE no cabía (sección 3). Es CSS y se revierte en dos líneas. Desde 1024 px de pantalla, Usuario y Clave no pierden ancho; en una ventana más angosta pierden unos píxeles. |
| HYUNDAI muestra el suyo solo si tiene una letra o una cifra; MSC muestra lo que traiga (también «-»). | Es lo que usa cada uno: `_hmm_contrato` no cuenta un contrato sin letras ni cifras, y MSC escribe en el portal lo que traiga la llave. |
| No avisa si falta la llave. | Su aviso caería en el `log.txt` de una corrida en curso. |
| El panel Tkinter de respaldo no cambia. | Sus casillas (`Entry`) no tienen texto de ayuda; habría que simularlo con texto y color, y eso cambia lo que se guarda. |

## Lo que decides tú

- **La casilla «Contrato» de ONE reemplaza solo el contrato de los destinos USA.** Para los demás destinos, el programa
  usa siempre `one_otros` (o `contrato_otros`, si alguien lo escribió a mano en `config.json`), escribas lo que escribas
  en la casilla. ¿Lo dejo así, o quieres que la casilla reemplace los dos? Es una regla de negocio y no la toqué.

## RESIDUAL

- **Las llaves `contrato_usa` y `contrato_otros` de las credenciales de ONE** no están en la plantilla ni en el panel.
  Si un `config.json` las trajera, mandarían sobre el contrato por defecto que muestra la casilla de ONE, y la casilla
  no lo diría. Se reabre si alguna aparece (el panel no las escribe; no se leyó el `config.json` de este equipo).
- **Una casilla de HYUNDAI sin ninguna letra ni cifra** («-», o solo caracteres invisibles) no muestra el texto gris,
  porque tiene un valor, y el programa usa igual el contrato por defecto: `_hmm_contrato` no la cuenta (revisión de
  código, BAJO). Ya pasaba antes del cambio. Si alguien escribe «-» para decir «sin contrato», reserva con el de
  `contratos_por_defecto` sin que nada lo diga. Se reabre si se ve en un equipo; el arreglo sería mostrar el contrato
  por defecto también ahí, fuera del texto de ayuda.
- **En un teléfono** el cuadro queda apretado, como antes. El programa se usa en el escritorio.
- **Los contratos por defecto salen ahora por `/api/credenciales`** (revisión de seguridad, BAJO). Una página de otro
  sitio no los puede leer (la revisión lo probó: 403 sin la marca, con otro `Origin`, con `Origin: null`, con
  `Sec-Fetch-Site: cross-site` y con otro `Host`), pero otro programa de este equipo sí: es el límite que el panel ya
  tenía («protege del navegador, no de otro programa de este equipo»), y la misma API ya devolvía el contrato de cada
  operador. Se reabre si el equipo pasa a ser compartido.
- **Un contrato por defecto enorme** (revisión de seguridad, BAJO): `_hmm_contrato_a_la_vista` sanea el texto entero
  antes de cortarlo a 40, y cada pedido vuelve a leer `config.json`. Medido por la revisión: con 5 millones de
  caracteres, el cuadro tarda 2,27 s en abrir (0,028 s con uno normal). Requiere escribir así `config.json` a mano. Se
  reabre si se ve.
- **Rellenos invisibles que Python cuenta como letras** (U+3164, U+115F, U+FFA0; revisión de seguridad, BAJO): con un
  contrato de HYUNDAI hecho solo de ellos, la casilla mostraría «por defecto: » y algo invisible. Ya pasaba antes del
  cambio, en la regla de `_hmm_contrato` (el aviso del encargo 95 lo cuenta como contrato, y la fila entra al portal):
  arreglarlo cambia esa regla y los saneadores comunes, y va en su propio encargo.

## Re-medir

- Las pruebas: `python -m unittest test_web.TestPanelCredenciales test_envio.TestLoQueFaltaALaVista`, desde `tests`.
- Las anclas de las mutaciones: `python .trabajo/e92/anclas.py`.
- El navegador: `python .trabajo/e96/panel_cred.py` (o `vacio`), con `TEMP`, `TMP` y `TMPDIR` en `.trabajo/e96/tmp`,
  y abrir la dirección que imprime.

## NO retroceder

- **El texto gris es el `placeholder`, nunca el `value`:** si fuera el valor, «Guardar» lo escribiría en la fila del
  operador, y desde ahí mandaría sobre el contrato por defecto aunque este cambie después.
- **`por_defecto` sale de las funciones que usa cada reservador** (`_contrato_por_defecto` y `_hmm_contrato`), no de
  una lectura propia de `config.json`: así lo que se muestra es lo que se usaría.

## Defectos de instrumento que me cacé

- **Antes de la compuerta corrí solo las clases que cambié, y no la foto de quién llama a `_contrato_por_defecto`**
  (`test_el_programa_ya_no_los_trae`), que el cambio movía: la vio la compuerta c1. Al tocar una función común, corre
  también las pruebas que la nombran.
- **El selector de mutaciones mira el cuerpo de cada prueba,** no las constantes del módulo que lee: con la foto
  actualizada en `LLAMADAS_CONTRATO`, no eligió las 7 mutaciones que nombran esa prueba. Se sumaron a mano a c2.
- **Mi primer panel de prueba no arrancó:** `soporte.cargar` devuelve la copia del programa y su carpeta, y lo tomé por
  el programa solo. Se vio en su salida, antes de abrir nada.
- **La primera vuelta de la revisión de código se trabó** 10 minutos sin avanzar y sin informe. No dejó procesos ni
  cambios en su clon; la segunda, con un tope de 5 minutos por comando, terminó.

## Premisas del encargo que se refutaron

- Ninguna. El encargo dice «para todas las navieras que tienen contratos_por_defecto (ONE, MSC y HYUNDAI)», y son esas
  tres; ONE tiene dos, y por eso su texto los dice los dos.

## Reglas aplicadas

`metodo-ciclo` v40: la base en una línea; control positivo y negativo (la casilla con y sin contrato por defecto); el
negativo tiene que morder (cada prueba nueva con su mutación, y las mutaciones censadas); se mide sobre el camino real
(el panel servido por una copia del programa, en un navegador); antes del commit, la suite entera sobre el árbol del
commit; las dos revisiones, cada una en un clon; el barrido de datos reales sobre lo que sube y sobre el mensaje del
commit; nada fuera de la carpeta del encargo (`TEMP`, `TMP` y `TMPDIR` en `.trabajo/e96/tmp`); la limpieza del cierre
dentro de la carpeta que borra. Del repo, las de `CLAUDE.md`: la API nunca devuelve la clave, las pruebas cargan una
copia del programa (`soporte.cargar`), nunca el puerto 8765, y cada prueba nueva con su mutación. No chocaron.
