# Encargo 94 · Los logs del colega: HYUNDAI, los dos puertos de MSC y lo que se arregló

**Base:** `AquaShield-Team/Agendamiento-Reservas` @ `77d5801` · árbol limpio. En GitHub, `main` y `estable` estaban
en `77d5801` (`ls-remote`, al empezar). Hecho con `metodo-ciclo` v40: la sesión tenía cargada la v39 y la volvió a
cargar al recibir el encargo, antes de trabajar.

Datos: las 8 corridas de `1. pruebas\web_todas_usuario1_20261103_102413` (el 03-11, de 09:27 a 10:24), que git no sigue
(`.gitignore`, regla `/*`; 0 archivos versionados bajo `1. pruebas`). Son datos reales: las naves, los lugares, las
reservas y los clientes de esas corridas no van en este informe ni en ningún archivo del repo; van en el chat. Aquí los
lugares van con su rol («el puerto de descarga») o con un nombre inventado de la misma forma («PUERTO BETA [XXBET]»).

## Lo que salió

| Pregunta | Respuesta |
|---|---|
| ¿Con qué versión corrió el colega? | Las 6 corridas de modo prueba (desde las 09:44), con `77d5801`. Las 2 de EMISIÓN (09:27 y 09:35, solo ONE), con una versión anterior (sección 1). |
| ¿Por qué HYUNDAI no emite? | Ninguna fila de HYUNDAI llega a la guarda: las 4 (una por corrida de prueba) quedan NO ENVIADA en «Contract No» porque su equipo no tiene un contrato de HYUNDAI configurado. No es lectura, ni espera, ni el portal (sección 2). |
| ¿Por qué MSC con dos puertos reconoce unos y otros no? | Dos errores de lectura del programa y uno de espera, medidos en el HTML del portal; ninguno es una regla de comparación entre nombres distintos (sección 3). Arreglados y probados en el portal. |
| ¿Algo más en los logs? | ONE elige como origen un lugar de otro país cuando la celda trae solo la ciudad (5 corridas): con la celda entera, arreglado; con la ciudad sola, decide Marcelo (sección 4). |

## 1. Con qué versión corrió el colega

`log.txt` no anota la versión (el panel la muestra desde `77d5801`, pero no queda en el registro). Se dedujo de lo que
escribe solo un código:

- **Las 6 corridas de modo prueba (09:44, 09:57, 10:08, 10:19, 10:20 y 10:24) corrieron `77d5801`:** las 4 que pasan
  por CMA-CGM traen el motivo nuevo de la nave que el portal no ofrece («el portal no ofrece la nave … en ninguna de las
  N rutas que deja elegir … No elegí otra nave»), del frente 2 del encargo 93, y de lo publicado solo `77d5801` lo trae
  (`estable` estaba antes en `b39c95c` y `main` en `4664942`). Y los cinco desplegables de ONE tardan 8,6 s por fila
  (4 corridas), con la espera con condición del frente 3.
- **Las 2 corridas de EMISIÓN (09:27 y 09:35) corrieron una versión anterior:** los mismos cinco desplegables tardan
  12,6 s por fila (8 filas), con la espera fija de 1,3 s de antes del encargo 93. Lo más probable, sin medir: ese
  panel se abrió antes de que `estable` llegara a `77d5801`. Las dos corrieron solo ONE: no cambian el diagnóstico de
  HYUNDAI ni el de MSC.

Sonda: `.trabajo/e94/tiempos_one.py` (los segundos entre los desplegables, por fila).

## 2. HYUNDAI: en qué paso cae cada fila y por qué

Una fila de HYUNDAI en cada corrida de prueba (09:44, 09:57, 10:08 y 10:24); ninguna en las de EMISIÓN.

| Paso | Qué pasó, en las 4 |
|---|---|
| Inicio de sesión | Entra (va a su página de login, encargo 71). |
| Paso 1, «Booking Reference» | El formulario llega (en la de las 10:24, a los 18,4 s; el tope es 30 s, encargo 76). |
| Paso 2, ruta y nave | Origen y destino elegidos; la nave de la fila, con su «Book Now»; el modal «Alternate Vessel Option», con «no quiero otra nave» y su OK. |
| Paso 3, «Customer & Contract» | Contract Holder y el Shipper desde su ventana, bien. |
| **«Contract No»** | **NO ENVIADA:** «no encontré un contrato (se escribe en el panel → Credenciales → HYUNDAI → columna Contrato)». En el paso 2, «sin contrato en las credenciales ni en config.json». |

- **Lo nuestro (lectura, espera, «Named Customer», «Contract No», «Sales Person»): nada.** «Named Customer» y «Sales
  Person» no se alcanzaron: van después de «Contract No».
- **El portal: nada.** La lista «Contract No» del colega trae, en las 4, 4 opciones y una sola real, y el código de
  esa real es el mismo contrato de HYUNDAI que tiene configurado este equipo (comparado en memoria, sin imprimirlo:
  `.trabajo/e94/contrato_hmm.py`). Con ese contrato en sus credenciales, la regla del encargo 89 la elige.
- **Modo:** falla en modo prueba (las 4). En EMISIÓN no corrió HYUNDAI en estas corridas; con la misma configuración
  cae en el mismo paso, que va antes de la guarda y no depende del candado. Es lo mismo que el encargo 88 encontró en
  sus corridas del 26 y el 28-10.
- **Qué hacer:** el colega escribe el contrato en el panel, Credenciales, columna «Contrato» de la fila de HYUNDAI, del
  operador con que corre. `LEEME.md` lo dice ahora en «Credenciales y opciones».
- El FRENA SI («HYUNDAI falla por algo del portal que no se puede reproducir sin emitir») no saltó: no es del portal.

## 3. MSC con dos puertos: cada caso que falló, letra por letra

Lo que la celda dice, lo que el programa escribió en el buscador del portal y lo que el portal muestra en el HTML
guardado (`.trabajo/e94/listas_msc.py` y `crudo_destino.py`, sobre el HTML de cada corrida). La comparación letra por
letra con los nombres reales va en el chat.

| Corrida, fila | Campo | La celda | Qué escribió el programa | Qué muestra el portal | Qué la dejó afuera |
|---|---|---|---|---|---|
| 09:57, 3 filas | Puerto de descarga | El nombre con su código entre corchetes, igual letra por letra al de la lista del portal | La celda entera, con el código | Con el código, ninguna lista (el HTML no la trae); con el nombre solo, una opción: la de la celda | **Lectura:** el buscador busca por el nombre, y el programa le escribía también el código |
| 10:08 y 10:24, 1 fila | Destino final | El nombre con dos espacios seguidos entre la ciudad y la sigla de su estado, igual al del portal | La ciudad con los espacios de a uno | La opción con los dos espacios (y otra del mismo estilo en la misma lista) | **Lectura:** el buscador empieza por lo escrito, letra por letra, y el programa juntaba los espacios |
| 09:44, 1 fila | Destino final | La ciudad sola | La ciudad | 4 lugares que empiezan por ella | **La regla de siempre:** pide una sola, y calzan 3 (la regla no se tocó). **Y espera:** decidió con 8 opciones que respondían a lo escrito a medias |
| 09:44, 1 fila | Destino final | La ciudad sola | La ciudad | 2 terminales que empiezan por ella | **La regla de siempre:** pide una sola. El colega escribió después el nombre del terminal, y la fila llegó a OK-EJEMPLO |

No hubo diferencias de tildes, mayúsculas (se comparan sin distinguirlas), guiones ni nombre del país: en los casos
de lectura, la celda era el texto del portal, letra por letra. Ningún arreglo decide que dos nombres distintos sean el
mismo puerto: el FRENA SI no saltó. Los dos casos de la regla («una sola») siguen NO ENVIADA, y su motivo trae la lista:
qué lugar es el de la fila lo escribe el operador.

## 4. El resto de las corridas

| Naviera | Qué se vio | De quién es |
|---|---|---|
| ONE | Con la celda del puerto de carga con la ciudad sola (4 corridas) y con la celda entera («<puerto>, CHILE (CY)», 1), eligió como origen un lugar de España cuyo nombre empieza igual: la primera de 9 sugerencias (6 de España; la de Chile, la 7.ª). Sin salidas desde ahí, la fila quedó REVISAR, «nave no encontrada». | **Lectura**, con la celda entera: arreglado (sección 5). **La regla**, con la ciudad sola: decide Marcelo (más abajo). |
| ONE | En la corrida de EMISIÓN de las 09:27 (versión anterior), la primera fila después de iniciar sesión no recibió la sugerencia del destino en los 3,6 s que el programa la espera; las 8 filas siguientes, con el mismo destino, sí. NO ENVIADA. | Probablemente el portal, la primera vez (sin medir). Residual. |
| ONE | 8 reservas EMITIDA en las dos corridas de EMISIÓN. | — |
| CMA-CGM | REVISAR en las 4: el portal no ofrece la nave en esa ruta. La nave no aparece en ninguno de los 4 HTML de la lista de rutas; el control, la nave que sí ofrece, aparece 4 veces en cada uno (`.trabajo/e94/cma_nave_en_rutas.py`). | El portal, o la nave de la fila. |
| MSC | REVISAR en algunas rutas: la nave de la fila no está entre las que el portal ofrece. | La planilla o el portal. |
| COSCO | OK-EJEMPLO en las 4. El intento automático del validador falla por la librería de imágenes, y el operador lo resuelve. | Conocido (encargo 84: sumar esa librería lo decide Marcelo). |
| MAERSK | OK-EJEMPLO en las 4. | — |

## 5. Lo que se arregló (commit `74f0854`)

1. **MSC, puertos con el código del portal** (`_msc_puerto`, `_msc_sin_codigo`): si la celda trae el código entre
   corchetes, se escribe el nombre sin el código, y el JavaScript busca la celda entera: elige solo la sugerencia que la
   dice entera; si el portal no la ofrece, NO ENVIADA, como antes. Sin código, nada cambia. Una celda que es solo el
   código no se escribe: NO ENVIADA, como una celda sin una palabra. El nombre va con los espacios de a uno: un salto
   de línea sería la tecla Enter en la lista.
2. **MSC, destino final con los espacios de la celda** (`_msc_destino_final`): se escribe la ciudad con sus espacios,
   sin el código; todo otro blanco (un salto de línea, un tabulador, un espacio duro), con los espacios de su lado, pasa
   a un espacio. Si así la lista no trae nada, se escribe una vez con los espacios de a uno (`otra_vez`); con más de 8
   espacios de más (`MSC_ESPACIOS_DE_MAS`), de entrada. Se compara como antes, con los espacios de a uno, y si la celda
   trae el código, al final o antes de su primera coma, la opción tiene que terminar con ese código (`_msc_codigo`);
   con dos códigos distintos, NO ENVIADA sin pulsar nada. Las dos expresiones regulares empiezan solo donde empieza una
   racha de blancos, para que una celda con miles de espacios no tarde segundos.
3. **MSC, la lista de «Destination» al día** (`_msc_elegir_de_lista` con `al_dia`, `_msc_lista_quieta`,
   `_msc_empieza_por`): dos lecturas iguales valen solo si todas sus opciones empiezan por lo escrito, que es como
   filtra el portal; si no llega a una así en 8 s, decide con la última, como antes, y log.txt lo dice.
4. **ONE, la sugerencia que dice la celda entera** (`_JS_PICK_SUGGESTION`, `_fill_port`, `_fill_autocomplete`): si una
   opción de la lista (`role="option"`) dice la celda entera, elige esa, también si la lista la deja más abajo de los
   850 px que miran las candidatas de siempre, y nunca una tarjeta ni una dentro de una de reservas frecuentes. Con la
   ciudad sola, como antes. En los 23 HTML de ONE guardados, `role="option"` lo llevan solo los botones de su lista, y
   ninguno de los 93 elementos de las tarjetas frecuentes. Si la celda trae algo después de la coma y ninguna opción la
   dice entera, log.txt lo dice. La ciudad va con los espacios de a uno.

Los puntos 1, 2 y 4 en su forma final salieron de las revisiones de código y de seguridad (sección 8). Medido
(`espacios_puertos.py`): escribir los puertos de MSC y de ONE con los espacios de a uno no cambia lo que se teclea en
ninguna de las 73 celdas de las planillas ni de las 155 líneas de ruta de MSC y ONE de los log.txt.

Medido antes del cambio (`.trabajo/e94/medir_celdas.py`, con el lector del panel): en las 90 filas de las 4 planillas
del equipo y de «1. pruebas» y en las 191 líneas de ruta de los log.txt de `logs/` y de «1. pruebas», las únicas celdas
que cambian lo que el programa escribe o elige son las del colega (3 puertos con código, 3 destinos con dos espacios o
con código, 2 celdas enteras de ONE). En las del equipo, ninguna: ninguna fila que hoy funciona cambia.

## 6. Probado en el portal, en modo prueba, desde este equipo

Con una planilla de trabajo en `.trabajo/e94` (solo naves y lugares, borrada al cerrar), el panel del programa sin abrir
pestaña (`.trabajo/e94/vivo_lanzar.py`) y su API (`vivo_correr.py`), con el candado cerrado:

| Fila | Antes (en el equipo del colega) | Ahora |
|---|---|---|
| MSC, puerto de descarga con código y destino final de dos espacios | NO ENVIADA (puerto de descarga) | OK-EJEMPLO |
| MSC, puerto de descarga con código y destino final con código | NO ENVIADA (puerto de descarga) | OK-EJEMPLO |
| MSC, puerto de descarga con código y destino final con código (otro país) | NO ENVIADA (puerto de descarga) | OK-EJEMPLO |
| MSC, control: el destino final con la ciudad sola (3 lugares) | NO ENVIADA, decidida con 8 opciones a medias | NO ENVIADA, decidida con las 4 de la ciudad |
| ONE, la celda entera | REVISAR (origen de España) | **Primera prueba:** REVISAR igual. **Después del arreglo del tope de 850 px:** el origen de Chile (CY), la nave encontrada, OK-EJEMPLO |
| ONE, control: la ciudad sola | REVISAR (origen de España) | REVISAR, igual (la regla no cambió) |

La primera prueba de ONE mostró que el arreglo no alcanzaba: la sugerencia de Chile estaba a 866 px, debajo del tope de
850 px con que el JavaScript junta las candidatas. Con la sugerencia entera buscada también ahí, la segunda prueba eligió
la de Chile.

## 7. Compuertas

Sobre el árbol del commit `74f0854` (`5b27c1d`), en un clon dentro de `.trabajo/e94` (`compuerta2`), con el árbol
comparado con el índice del repo vivo antes de commitear (iguales), y con el envoltorio de salida literal de
`metodo-ciclo`:

| Compuerta | Resultado | Salida |
|---|---|---|
| Suite entera (`con_mas_plazo.py`, 7.200 s) | 1096 pruebas, OK (1 saltada), en 1557 s; los 106 originales, sin cambios | `suite_fix4.out` |
| Censo de las mutaciones que tocan el cambio (`ids_tocados.py` sobre `77d5801..HEAD`, y el prefijo `e94`) | 82 mutaciones y 92 pares: todos muerden, cada uno por su aserción; el control (la copia sin mutar) pasa; los originales, sin cambios | `censo_fix4.out` |
| Anclas de `tests/mutaciones.py` (`e92/anclas.py`) | 3061 mutaciones, cada texto viejo una vez; las 112 que tocan el cambio compilan | consola |
| Guarda de datos reales (hook pre-commit) | 0 hallazgos en 134 archivos | consola |
| Sonda de secretos (`--dry-run` y después de `git add`) | 0 y 0 | `sonda_dry4.out`, `sonda4.out` |

Las dos mutaciones de las expresiones regulares muerden por tiempo: con la expresión de antes, la prueba de los 50.000
espacios tardó 29 s y 5,6 s, contra un tope de 2 s y 1 s, y con la de ahora pasa por debajo. Que la de antes tarde
más no depende de la carga del equipo; que la de ahora quede bajo el tope, sí, y el tope lo deja de sobra (0,04 s con
un millón de espacios, medido con el equipo ocupado).

Tres compuertas anteriores se detuvieron sin terminar porque el código cambió con las revisiones: la del primer commit
(su suite pasó, 1094 pruebas), la del segundo (detenida al llegar la revisión de seguridad) y la del tercero (detenida
por la guarda, defecto 7). Ningún proceso suyo quedó vivo.

## 8. Revisiones

Las dos, en un clon dentro de `.trabajo/e94` (nunca en el repo vivo), de a una: primero la de código, y después la de
seguridad sobre el código con sus arreglos.

**Revisión de código** (`code-reviewer`, Opus), sobre el primer commit del arreglo:

| Severidad | Hallazgo | Qué se hizo |
|---|---|---|
| MEDIA | El destino final con los espacios de la celda rompía una celda con un espacio de más por error, que antes funcionaba. | El reintento con los espacios de a uno (`otra_vez`), y la expresión de los blancos que se lleva también los espacios de su lado. |
| MEDIA | ONE, sin el tope de 850 px, podía elegir cualquier texto de la página que dijera la celda entera. | Solo entre las opciones de la lista (`role="option"`), medido en los 23 HTML de ONE. |
| BAJA | La palabra de la celda se miraba antes de quitar el código: «X [XXGAM 10]» se escribía «X». | La palabra se mira sin el código. |
| BAJA | El código de la celda no se exigía en la opción del destino final. | Se exige (`_msc_codigo`). |
| BAJA | `_destino_separado` no conoce el código del portal. | Medido sin cambios en ninguna fila; es tuya (RESIDUAL). |
| BAJA | Faltaban mutantes: la lectura de ONE que nunca pulsa y la tarjeta frecuente por su ancestro. | Agregados, con sus casos en la prueba de Node. |

**Revisión de seguridad** (`security-reviewer`, Opus), sobre el commit con los arreglos de la de código:

| Severidad | Hallazgo | Qué se hizo |
|---|---|---|
| MEDIA (regresión, medida) | Con el código antes de la primera coma («CIUDAD GAMMA [XXGAM 20], PAIS»), el destino final elegía otro lugar, que la base no elegía. | El código se toma también de ahí; con dos distintos, NO ENVIADA. Su sonda, sobre el código nuevo: NO ENVIADA. |
| BAJA | Las dos expresiones nuevas tardaban en proporción al cuadrado de una racha de espacios (13 s con 32.767). | Miran hacia atrás: lineales (0,0006 s con 20.000; 0,04 s con un millón), con el mismo resultado. |
| BAJA | El destino final escribía cada espacio de la celda: con miles, minutos. | Con más de 8 espacios de más, de a uno de entrada. |
| BAJA | La celda entera de ONE no tenía el filtro de clases de la regla de siempre: una tarjeta con el rol de opción ganaba. | Con el filtro. |
| BAJA (de antes) | ONE elige con la regla de siempre sin avisar cuando la celda nombra el país y ninguna opción la dice entera. | log.txt lo dice. Cambiar la regla, tuyo. |
| BAJA (de antes) | Un salto de línea en el puerto de carga de MSC y en los puertos de ONE se escribía como la tecla Enter. | Con los espacios de a uno; medido sin cambios en ninguna fila. |
| Informativo | El reintento puede elegir un homónimo escrito con un solo espacio. | RESIDUAL: la base escribía siempre así. |

Lo que la revisión de seguridad dio por bueno, medido: el candado no cambió (28 pruebas de `test_candado`,
`TestSinClicACiegas`, `TestSinSugerenciaNoSigue` y `test_solo_ahi`); la lectura de ONE nunca pulsa; ningún corte se
traga; nada de la planilla entra a un JavaScript ni a una expresión regular; los caracteres invisibles del destino
quedan NO ENVIADA; y la guarda de datos reales da 0 hallazgos en los 134 archivos.

## Decisiones que tomé solo

| Decisión | Por qué |
|---|---|
| Escribir el puerto de MSC sin el código y elegir la sugerencia que dice la celda entera | Es leer bien la celda: el texto es el del portal, letra por letra; no se iguala nada distinto. Sin código, nada cambia. |
| Escribir el destino final con los espacios de la celda y comparar con los de a uno | El buscador del portal es literal; la comparación con los espacios de a uno ya era la regla (encargos 86 y 87). Un salto de línea sigue pasando a espacio, porque escrito sería una tecla. |
| Si la lista no llega a estar al día en 8 s, decidir con la última | Es lo de antes: el arreglo solo agrega una condición para dar la lista por quieta; no corta filas nuevas. |
| ONE: la celda entera también debajo de los 850 px, y nunca una tarjeta frecuente | El portal la dejó a 866 px (medido en la prueba); las tarjetas frecuentes podrían traer el mismo texto, y su exclusión ya estaba en la regla de siempre. |
| ONE: la celda entera solo entre las opciones de la lista (`role="option"`) | La revisión de código vio que, sin el tope de 850 px, cualquier texto de la página que dijera lo mismo podía ganar. En lo medido, solo los botones de la lista llevan ese rol. |
| MSC: si con los espacios de la celda la lista no trae nada, escribirla una vez con los de a uno | Una celda con un espacio de más por error funcionaba antes del arreglo (revisión de código); así no se pierde. |
| MSC: con el código en la celda del destino final, la opción tiene que terminar con ese código | El código es lo que dice cuál de los lugares del mismo nombre es; escribirlo y no exigirlo dejaba elegir otro (revisión de código). |
| MSC: el código del destino final también antes de la coma, y NO ENVIADA con dos distintos | La revisión de seguridad midió que con el código antes de la coma la primera versión elegía otro lugar, que la base no elegía. |
| MSC: las expresiones regulares, mirando hacia atrás; y con más de 8 espacios de más, el destino de a uno | Una celda con miles de espacios tardaba segundos en la expresión y minutos en escribirse; con el arreglo, el resultado es el mismo (200.000 entradas al azar, medido por el revisor) y el tiempo, lineal. |
| MSC y ONE: los puertos con los espacios de a uno | Un salto de línea en la celda era la tecla Enter en la lista, lo que la regla del programa prohíbe. Medido: no cambia ninguna fila. |
| ONE: la celda entera con el filtro de clases de siempre, y log.txt cuando no la encuentra | La revisión de seguridad midió que una tarjeta con el rol de opción ganaba; y elegir con la regla de siempre teniendo la celda entera no quedaba escrito. |
| No tocar `_destino_separado` con el código del portal | Es la regla de CMA-CGM y MSC sobre cuándo dos nombres son el mismo lugar: es tuya. Medido: no cambia ninguna fila (RESIDUAL). |
| No cambiar la regla de ONE con la ciudad sola | Es elegir entre lugares distintos: decide Marcelo. |
| `LEEME.md`: dónde va el contrato de HYUNDAI y cómo escribir los puertos de MSC | Es lo que le falta al colega para correr; no cambia el programa. |
| Probar en el portal con una planilla de trabajo con naves y lugares | El encargo deja correr el modo prueba; sin clientes, pedidos ni reservas, y borrada al cerrar. |

## Lo que decide Marcelo

**ONE, el origen con la ciudad sola en la celda** (4 corridas del colega): la regla de ONE es «la sugerencia que trae la
ciudad y está más arriba», y ONE lista primero 6 lugares de España cuyo nombre empieza igual. Opciones:

- **(a) La regla de MAERSK** (encargo 43): la sugerencia cuyo nombre antes de la coma es la ciudad, entera, y entre
  esas, la de patio de contenedores (CY). En el caso del colega elige la de Chile (CY).
- **(b) En el origen, solo las de Chile**, como COSCO («en el origen la que dice Chile»).
- **(c) Dejarla como está:** el operador escribe la celda entera («<puerto>, CHILE (CY)»), que desde este encargo
  funciona.

Mi recomendación es (a), porque es la regla que ya decidiste para MAERSK y no depende del país.

## Prueba conjunta antes de mover `estable`

Con el lanzador de prueba, nunca el de emisión, en el equipo del colega:

1. **HYUNDAI:** escribe el contrato en Credenciales y corre una fila. Tiene que pasar «Contract No» y elegir «Direct
   Input» en «Named Customer» (encargo 93), y llegar a OK-EJEMPLO.
2. **MSC con dos puertos:** las filas con los puertos copiados del portal, con código o sin él y con los espacios del
   portal. Tienen que llegar a OK-EJEMPLO; la que trae la ciudad sola, con varios lugares, sigue NO ENVIADA con la lista
   en el motivo.
3. **ONE:** la fila con la celda entera del origen tiene que elegir el de Chile. Con la ciudad sola, sigue como antes,
   hasta tu decisión.
4. **Las demás** (COSCO, MAERSK, CMA-CGM), como en sus corridas del 03-11.

## RESIDUAL

- **ONE con la ciudad sola:** sigue eligiendo el primer lugar de la lista. Se reabre con la decisión de arriba.
- **Un destino final escrito con un espacio donde el portal pone dos** («Ciudad ST» para «Ciudad␣␣ST») sigue sin traer
  nada: el buscador del portal es literal, y el reintento solo junta espacios, no los agrega. Se reabre si una celda
  escrita así hace falta.
- **`_destino_separado` no conoce el código del portal:** con el código en una celda y el país en la otra («PUERTO BETA
  [XXBET]» y «PUERTO BETA, PAIS»), la fila va por el camino de dos. Medido (`separado_codigo.py`): en las 43 filas de
  MSC y CMA-CGM de las planillas y en las 66 líneas de ruta con el destino aparte (9 con código), no cambia ninguna. Es
  tu regla (encargo 87); se reabre si lo decides.
- **La regla de ONE con la celda entera vale para cualquier celda con algo después de la coma,** no solo las del
  portal: si una opción de la lista dice esa celda entera, gana. Lo acota que tiene que ser una opción de la lista y su
  texto completo.
- **ONE busca la celda entera en toda la página, sin el tope de los 850 px:** entre las opciones de la lista
  (`role="option"`) y sin tarjetas, pero no solo en la lista abierta del campo que llena, y su clic de JavaScript no
  necesita que se vea. En lo medido, solo los botones de la lista llevan ese rol. Se reabre si una página trae otro.
- **El reintento del destino final, con los espacios de a uno, puede elegir un homónimo escrito con un solo espacio**
  si la primera lista vino vacía porque el portal tardó y la celda no trae código. La base escribía siempre así: no es
  peor que antes (revisión de seguridad).
- **`MSC_ESPACIOS_DE_MAS` (8) es una hipótesis:** en lo medido, el portal escribe un lugar con un espacio de más.
- **El puerto de descarga de MSC se sigue escribiendo con los espacios de a uno:** ningún puerto medido trae dos
  espacios. Se reabre con uno.
- **La primera fila de ONE después de iniciar sesión** pudo no recibir la sugerencia del destino en 3,6 s (1 vez, en la
  versión anterior). Se reabre si vuelve a pasar con `77d5801` o después.
- **HYUNDAI no avisa antes de correr** que falta el contrato: la fila entra al portal y corta en el paso 3 (unos 40 s).
  Propuesta: que el panel lo marque antes de correr, como la fila sin nave. Se reabre si lo encargas.
- **`log.txt` no anota la versión** del programa. Propuesta: una línea con la versión junto al modo, al empezar cada
  corrida. Se reabre si lo encargas.

## Re-medir

Todas en `.trabajo/e94` (git las ignora), sobre las corridas de `1. pruebas`:
- `filas.py`: cada reserva de cada corrida, con su estado. `avisos.py`: los avisos y errores, agrupados.
- `tiempos_one.py`: la versión, por los tiempos de ONE. `contrato_hmm.py`: la lista «Contract No», sin imprimir contratos.
- `listas_msc.py` y `crudo_destino.py`: las listas de MSC en el HTML, con sus espacios. `kendo_destino.py`: la
  configuración del buscador de «Destination». `lista_one.py` y `boton_one.py`: las sugerencias de ONE.
- `cma_nave_en_rutas.py <nave> <control>`: la nave de la fila en las listas de rutas de CMA-CGM.
- `medir_celdas.py`: qué filas cambian con los arreglos. `separado_codigo.py`: si el código del portal cambia el
  camino de `_destino_separado` en alguna fila. `espacios_puertos.py`: si escribir los puertos con los espacios de a
  uno cambia lo que se teclea. `tiempo_regex.py`: el tiempo de las dos expresiones regulares con rachas de espacios.
- La prueba en el portal: `planilla.py`, `vivo_lanzar.py` y `vivo_correr.py 8765 <planilla> CONSOLIDADO ONE,MSC <salida>`.
- La compuerta: `compuerta.py <sufijo> <ids>` (la suite y el censo, con el envoltorio de salida literal).

## NO retroceder

- **No escribir la celda entera de un puerto de MSC en el buscador:** con el código del portal, no trae nada.
- **No juntar los espacios del destino final al escribirlo:** el portal escribe algunos lugares con dos.
- **No dar por quieta la lista de «Destination» con dos lecturas iguales solamente:** puede ser la de lo escrito a
  medias.
- **No buscar la sugerencia entera de ONE solo entre las de arriba de los 850 px:** el portal la dejó a 866. Y no
  buscarla fuera de las opciones de la lista (`role="option"`): sin el tope, cualquier texto de la página competiría.
- **No escribir el destino final sin reintento:** una celda con un espacio de más por error funcionaba antes.

## Defectos de instrumento que me cacé

1. **Copié a archivos versionados nombres de lugares de las corridas del colega** (docstrings, `CLAUDE.md`, datos de las
   pruebas), antes del commit. Los cambié por nombres inventados de la misma forma y por roles, y lo comprobé con una
   búsqueda de cada nombre en los archivos del commit (0).
2. **La primera versión del arreglo de ONE no servía en el portal:** la probé con una lista donde todas las sugerencias
   quedaban arriba, y la del portal estaba a 866 px. Lo vio la prueba en el portal; la prueba en Node suma ahora ese
   caso.
3. **Un `sed` con barras invertidas** no cambió una ruta (la herramienta Bash junta los pares); lo corregí con Edit.
4. **Un `cd` y un `timeout` sueltos** en dos comandos: los frenaron las guardias, y los reescribí sin ellos.
5. **La sonda de secretos con una tubería** dio el código de salida de `tail`; la repetí con `pipefail` (0 y 0).
6. **Escribí en `CLAUDE.md` un ejemplo de `_destino_separado` sin comprobarlo** («PUERTO BETA [XXBET]» y «PUERTO
   BETA»): con esas dos celdas, una contiene a la otra, y la regla no las separa. Lo corregí leyendo la función, y la
   sonda que lo mide (`separado_codigo.py`) abortó la primera vez por su control: las planillas del colega no traen las
   filas con código (salen de sus log.txt). Le sumé la planilla de la prueba en vivo y las líneas de ruta.
7. **Escribí una prueba con dos letras mayúsculas sueltas delante de una racha de espacios,** y la guarda de datos
   reales las leyó como una forma jurídica (2 hallazgos). Lo vio la guarda antes del commit, y ya había lanzado la
   compuerta sobre ese árbol, que habría caído en `test_guarda_datos`. La detuve, cambié el texto por «PUERTO … BETA» y
   la volví a lanzar. La guarda se corre antes de lanzar la compuerta, no después. (Al citarlas en este informe, la
   guarda volvió a frenar el commit: aquí van sin citar.)

## Premisas del encargo que se refutaron

- **«HYUNDAI no le emite»:** no llega a la guarda en ninguna fila, por la configuración de su equipo; ni el código ni
  el portal.
- **«En MSC unos puertos se reconocen y otros no» como una regla de comparación:** en los casos que fallaban, la celda
  era el texto del portal, letra por letra. Fallaba lo que el programa escribía en el buscador (el código, los espacios)
  y una espera. Los otros dos casos son la regla de siempre, que pide un solo lugar.

## Reglas aplicadas (pieza 7)

`metodo-ciclo` v40: el control positivo que aborta (en cada sonda), «Se mide sobre el camino real» (las listas en el
HTML del portal y la prueba en el portal), el negativo que muerde (una mutación por parte nueva), «Un número fijo deja de
morder» (la medición de filas que cambian, sobre todo el universo), los datos reales fuera de los archivos, los
revisores en un clon, antes de cada commit todas las suites, el push con `subir`. Del módulo: el candado (nunca
EMISIÓN), «antes de la guarda no hay clics a ciegas», la guarda de datos y la sonda de secretos. Sin choques.
