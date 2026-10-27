# CICLO-insignia-emision · Encargo 85: la insignia «EMISIÓN REAL» vuelve a fondo lleno

> **metodo-ciclo v39.** Base: `main` en `e9ecb98`, árbol limpio. **Dos commits:** el cambio (`b84c789`) y este informe. **No se
> subió nada:** el bloque de push está al final. Sin datos de clientes: todo lo medido es del panel con su API falsa.

## Qué se pidió y qué salió

El encargo: la insignia «EMISIÓN REAL» del panel vuelve a fondo lleno, con un rojo de la paleta que pase 4,5:1 con su texto y se
siga leyendo como alerta, no como naranja; «MODO SEGURO» se queda con borde. Con su FRENA: si ningún rojo de la paleta pasa 4,5:1
sin dejar de leerse como alerta, o si el cambio toca algo fuera del panel.

**Cayó en el FRENA, y lo decidiste tú:** la paleta de aquachile-brand no trae ningún rojo (abajo). Te mandé una lámina con el panel
real en claro y en oscuro y dos fondos llenos posibles, y elegiste el **óxido `#A8441E`** con texto blanco, en los dos temas.

## Paso 0: la paleta no trae un rojo (medido)

`candidatos.py` (en `.trabajo/e85/`, sin versionar) usa las funciones de la skill (`medir_contraste.py`: `ratio`, `paleta`,
`en_paleta`), con un control que aborta: el rojo de antes, `#EF4444` con blanco, tiene que dar 3,76, el número del encargo 84 (dio
3,76).

- **Los 8 literales de `colores.md`** y la variante oscura del error: ninguno tiene matiz de rojo. El color de error de la paleta
  es el **ocre `#C76728`** (Pantone 158 C, «naranja tierra», 23,8°): con blanco da **3,89**; con el texto del tema, 1,98.
- **Los rangos que el verificador acepta como paleta** (cada literal ±8°): el único que toca el rojo (0° a 15°) es el del acento,
  desde 14,7°, y el acento no se toca nunca. Por la definición de la propia skill, un derivado a ±8° «se lee como el mismo color»:
  ningún color de la paleta se lee rojo.
- **Lo más rojo que admite con margen:** el ocre llevado al borde de su rango, 16,5°, y oscurecido hasta pasar 4,5 con blanco:
  `#A8441E`, **5,98**. Es un color derivado, no el literal del manual.

La lámina (`.trabajo/e85/lamina-insignia-emision.png`, sin versionar), medida en píxel con `par_en_pixel` de la skill sobre el panel
extraído: hoy (borde) 6,65 en claro y 10,35 en oscuro; **A, el óxido, 5,98 y 5,98**; B, el ocre de error tal cual con texto oscuro,
4,74 y 5,80, pero se lee naranja.

## El cambio · `b84c789`

- **`AQUASHIELD.py`, solo dentro de `CSS_INDEX`:**
  - `.modo-insignia.emision { background: #A8441E; border-color: #A8441E; border-width: 2px; color: #FFFFFF; }`;
  - la regla del neutro en oscuro pasa de `body:not(.light-theme) .modo-insignia` a `body:not(.light-theme) .modo-insignia.seguro`.
    Hasta acá se la ponía a las dos insignias, y en oscuro la de emisión habría perdido el fondo;
  - el borde de 2 px (MODO SEGURO tiene 1) las distingue en el alto contraste de Windows (`forced-colors`), que les pone el mismo
    fondo, el mismo texto y el mismo color de borde (medido en Chromium por la revisión de seguridad);
  - MODO SEGURO no cambia. Ni Python fuera del literal, ni `app.js`, ni el HTML, ni el candado.
- **La prueba,** `test_marca.TestBloqueEnElPanel.test_en_modo_emision_la_insignia_va_llena_en_los_dos_temas`:
  - lee la cascada de las reglas que nombran a la insignia (o solo `.emision` o `.seguro`), en cada tema, por especificidad y
    orden, y exige el óxido lleno con blanco (5,98) y borde de 2 px en los dos temas, y MODO SEGURO con su borde y, en oscuro,
    con el neutro exacto;
  - cae ante lo que no sabe leer: una forma de selector nueva, una regla en `@media`, un `!important` o una propiedad fuera de su
    lista (`background-color`, por ejemplo); el atajo `border` cuenta como su color;
  - una guarda (`reglas_genericas_sobre_la_nota`), con su control positivo y negativo, cae ante una regla genérica con fondo, borde
    o color que alcanzaría a la insignia sin nombrarla (`span`, `*`, un selector de atributo, o algo así bajo `#nota-modo`,
    `.rs-nota` o `.rs-version`).
- **Las mutaciones (13), cada una tumba la prueba:** la insignia vuelve al borde; el neutro en oscuro vuelve a las dos; sin el texto
  blanco; el ocre literal; llena solo en claro; MODO SEGURO lleno; el neutro escrito como `background-color`; el borde de MODO SEGURO
  por el atajo; una regla genérica sobre la nota; MODO SEGURO sin su neutro en oscuro; el borde de 1 px; el neutro por la segunda
  clase; el texto oscuro desde la nota.
- **`CLAUDE.md`:** «Interfaz y marca» dice cómo va cada insignia y por qué el óxido y el borde de 2 px, y cuántos tintes mide hoy el
  verificador; «Red de verificación» suma que el temporal de la suite va en una ruta sin espacios (abajo); el número de pruebas.

## Las compuertas, sobre el árbol del commit

Corridas por `ayudante-mecanico` con el envoltorio de salida literal; leí cada archivo (en `.trabajo/e85/salidas/`, sin
versionar). Sin eventos de espera de Windows (Kernel-Power 506/507) entre las 14:10 y las 15:00, cuando corrieron las tres últimas.

| compuerta | resultado |
|---|---|
| Censo de mutaciones (`--filtro insignia`) | 19 mutaciones, 19 pares, cada una tumba su prueba por su motivo; 1.000 pruebas, 0 sin mutación; foto de los originales sin cambios; `RESULTADO: OK`, exit 0 |
| Verificador de marca (aquachile-brand v48) sobre el panel extraído | todos los chequeos en OK, salvo `tinte-estado` en SIN DECIDIR por los 4 discos de íconos del encargo 84 (exit 2); `contraste-texto`: 198 textos medidos en píxel en los dos temas, con el estado del modo EMISIÓN, 0 que no llegan; la insignia de EMISIÓN, opaca, ya no es candidata de `tinte-estado` |
| Suite completa | `Ran 1000 tests in 1593.520s · OK`, foto sin cambios, `RESULTADO: OK`, exit 0 (con el tope de la corrida subido a 3.600 s: con el de 1.200, se habría cortado) |
| Sonda de secretos | 0 con `--dry-run` y 0 después del `git add` |
| Guarda de datos (hook pre-commit) | 0 hallazgos en los 123 archivos que se commitean |
| Guarda de datos sobre el mensaje del commit | 1: la línea `Co-Authored-By`, la dirección pública de atribución de Anthropic, la misma que ya llevan los tres commits del encargo 84 (no es un dato) |

## Revisiones (Opus, en un clon sin remoto dentro de la carpeta del encargo, de a una)

- **Código:** 0 críticos, 0 altos, 1 medio y 3 bajos; aprobado. Todos arreglados en el mismo commit:
  - el medio: la prueba no veía la forma larga de una propiedad (`background-color` en una regla de oscuro le quitaba el relleno a
    la insignia, medido en Chromium, y la prueba pasaba); ahora cae ante una propiedad que no sabe leer;
  - una regla genérica que alcanza a la insignia sin nombrarla (la guarda nueva); el neutro de MODO SEGURO en oscuro sin fijar (ahora
    con su valor exacto); tres textos desfasados (un comentario de la prueba, el número de tintes en `CLAUDE.md` y el mensaje del
    commit).
- **Seguridad:** 0 críticos, 0 altos, 0 medios y 2 bajos, los dos arreglados:
  - en alto contraste, las dos insignias quedaban iguales salvo el texto (el borde de 2 px);
  - una regla que alcanza a la insignia por su segunda clase (`.emision`) o le cambia el color del texto desde la nota; la cascada
    ahora toma también esos selectores, y la guarda mira el color y el borde.
  - Sus expresiones regulares no tienen retroceso exponencial: el peor caso armado es cuadrático (4,4 s con 344 KB de reglas), y sobre
    el CSS real tardan 4 ms. La guarda de datos sobre los archivos tocados: 0 hallazgos.
- Los dos arrancaron en su worktree y lo dejaron limpio; `git worktree list` quedó solo con `main`.

## Decisiones tomadas (Modo autónomo)

| Decisión | Por qué | Cómo deshacerla |
|---|---|---|
| El neutro de oscuro solo para MODO SEGURO | La regla común le quitaba el fondo a la de emisión en oscuro | Volver a `body:not(.light-theme) .modo-insignia` |
| Borde de 2 px, del mismo color que el fondo | La distingue de MODO SEGURO en el alto contraste de Windows | `border-width` fuera, y su aserción y su mutación |
| La prueba lee la cascada, no solo el texto de la regla | El encargo pide que vaya llena en los dos temas; un `count` de la regla no ve una regla de oscuro que la pise | — |
| Se mantiene la marca `aquashield:estado` de la regla de emisión | Ya no es una veladura (`tinte-estado` no la mira), pero si alguien vuelve a una, queda declarada | Quitar el comentario |
| El tope de la corrida entera de la suite, 3.600 s en vez de 1.200, solo para las corridas de este ciclo | Otras dos sesiones cargaban el equipo y la segunda corrida se cortó a los 1.200 s sin resultado | Correr `tests/correr.py` tal cual |

## Lo que salió mal, y lo medido de la máquina

- **La primera suite no terminó, y no te avisé:** el equipo entró en espera a las 06:15:51 (Kernel-Power 506, con un cambio de fuente
  de energía, 105, a las 06:15:45), despertó un instante a las 07:06 y siguió en espera hasta las 08:28:46 (507). La suite, lanzada a
  las 06:11 en segundo plano, se cortó al despertar, por las 2 horas de reloj de la herramienta, sin escribir nada. El ayudante que la
  corría quedó «sin progreso» y su aviso llegó como falla; **lo contesté sin leerlo** («No response requested»), y te enteraste
  cuando preguntaste, unas 4 horas después. Desde ahí: el pedido de mantener el equipo despierto de la app, y el aviso se lee.
- **La segunda se cortó en el tope de 1.200 s del corredor,** sin suspensión (0 eventos de espera entre las 12:25 y las 12:55), con
  un censo de Modulo-Seguros y pruebas de Modulo IVV corriendo a la vez (de otras sesiones; no se tocaron).
- **La tercera dio 13 fallos que eran del temporal, no del cambio:** puse `TEMP` en `C:\dev\Agendamiento Reservas\.trabajo\…`, con
  un espacio, y `test_entorno.TestElBatAbreConElEntornoPropio` cae así en sus 5 casos con el `.venv` (5 fallos en 20 s); con la misma
  carpeta por su nombre corto, `C:\dev\AGENDA~1\…`, pasa (OK en 16 s). Lo probable, sin medir: la prueba le da a pip su carpeta de
  ruedas en `PIP_FIND_LINKS`, y pip parte esa variable en los espacios. El preparador real no la usa, y el caso de la prueba con la
  carpeta del programa con espacios pasa. Queda en `CLAUDE.md`. La cuarta, con el temporal corto, pasó entera (1.000 OK, 969 s).
- **Los revisores con `isolation: "worktree"` crean `.claude/worktrees` en la raíz del repo,** y queda vacía al terminar. La foto
  del corredor anota solo que esa carpeta existe, así que una carpeta que aparece a mitad de una suite la haría caer; con la carpeta
  ya creada, no.
- **Una prueba de la guarda nueva leía mal un selector de atributo con `~`** (`[class~=emision]`): se partía por el combinador. Lo vio
  su propio control, y los corchetes se vacían antes de cortar. Y la primera versión de la guarda con «border» tomaba el
  `border-radius` de `:focus-visible` por un borde; ahora mira solo el fondo, el color y el borde (color, ancho o estilo).

## Re-medir

Con el Python de la Tienda (el `python` del PATH no trae playwright) y el temporal en una ruta sin espacios:

```bash
python tests/correr.py
python tests/correr.py --mutaciones --filtro insignia
python tests/marca/extraer_panel.py <carpeta nueva>
python ~/.claude/skills/aquachile-brand/snippet/verificar-modulo.py <esa carpeta>
```

- La suite, con el equipo cargado, puede pasar los 1.200 s que le da el corredor (este ciclo: 1.603 s): con otras sesiones corriendo,
  se corre cuando terminen, o con el tope subido, como `.trabajo/e85/suite_con_mas_plazo.py` (sin versionar; cambia solo ese tope).
- El contraste del óxido con blanco, con la fórmula de la skill: `ratio((168, 68, 30), (255, 255, 255))` de `medir_contraste.py`, 5,98;
  y el del rojo anterior, `#EF4444`, 3,76 (el control de `candidatos.py`).

## NO retroceder

- **La regla del neutro en oscuro va solo en `.modo-insignia.seguro`.** Si vuelve a `.modo-insignia`, la insignia de EMISIÓN pierde su
  fondo en oscuro: la prueba nueva cae (las mutaciones `e85-emision-neutra-en-oscuro` y `e85-oscuro-con-background-color`).
- **El borde de la de EMISIÓN, de 2 px.** Con 1 px, en el alto contraste de Windows las dos insignias quedan iguales salvo el texto.
- **El óxido no se aclara** para acercarlo al naranja ni se cambia por un rojo de fuera de la paleta sin una decisión tuya: es la que
  tomaste en este encargo, mirando la lámina.

## Residual

- **Que el óxido «se lea como alerta» lo decidiste tú mirando la lámina:** no hay una medición de eso. Es un color derivado del ocre
  en el borde de los ±8°; si la skill cambia ese margen, el verificador podría dejar de darlo por paleta.
- La guarda de la prueba no ve una regla que alcance a la insignia por otro antepasado de la nota (`body:not(.light-theme) .rs-panel
  span`, que sí ganaría); está en su docstring. El verificador de marca tampoco la vería en oscuro, porque el texto blanco sobre el
  panel oscuro pasa 4,5.
- El aviso de EMISIÓN se vio con la API falsa del estado declarado, no con la emisión abierta de verdad (el candado sigue cerrado), ni
  con el alto contraste de Windows en el panel real (lo midió la revisión de seguridad en Chromium).
- `tinte-estado`, SIN DECIDIR: los mismos 4 discos detrás de íconos del encargo 84.

## El push (no se subió nada)

Los dos commits, de `main`, con el correo noreply de autor y de committer. Antes de subir, en una consola:

```bash
git -C "C:\dev\Agendamiento Reservas" log origin/main..main --format="%h %ae %ce %s"
```

Tiene que mostrar solo el correo noreply en las dos columnas (van también los tres commits del encargo 84, si no los subiste).
Después:

```bash
git -C "C:\dev\Agendamiento Reservas" push origin main
git -C "C:\dev\Agendamiento Reservas" rev-parse main
git -C "C:\dev\Agendamiento Reservas" ls-remote origin refs/heads/main
```

Los dos hashes tienen que ser iguales. **`estable` no se movió.**

## Declaración de método

**metodo-ciclo v39** (recargada al empezar: la sesión venía compactada). Se aplicó: paso 0 medido con las funciones de la skill y su
control; el FRENA, con lo medido y tu decisión antes de tocar nada; el cambio y su guardián en el mismo commit, con mutaciones que
muerden; el verificador de marca sobre el panel extraído; la suite entera sobre el árbol del commit; las revisiones de código y de
seguridad (Opus), en un clon, de a una; la sonda de secretos y la guarda de datos sobre lo commiteado y sobre los mensajes; ningún push.
Lo mecánico (los censos, el verificador y las suites) lo corrió `ayudante-mecanico` con el envoltorio de salida literal, y leí cada
archivo; la sonda de secretos, la guarda sobre el mensaje y las dos corridas aisladas de `test_entorno` las corrí yo (son de segundos,
y las dos de `test_entorno` eran para diagnosticar). **La lista de tareas no se llevó:** esta sesión no tiene la herramienta. No se
escribió en la memoria de Claude Code. La fila del temporal con espacios quedó en el `CLAUDE.md` del módulo y no en «Entorno Windows de
esta máquina»: es de cómo corren las pruebas de este repo, y su causa no está medida.
