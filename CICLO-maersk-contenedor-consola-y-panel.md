# Encargo 64 · El contenedor vacío en la consola, la marca del panel y MAERSK sin las ramas que ya no se alcanzaban

**Base:** `C:\dev\Agendamiento Reservas` @ `98cbbcb` · árbol limpio al empezar.

Con `metodo-ciclo` v23: el encabezado del archivo decía v23 y la sesión tenía cargada la v20, así que volví a invocar
la skill antes de medir. Sin abrir ningún portal y sin red.

## En resumen

- **Con una columna de contenedor y la celda vacía, la consola le da «40 HC REEFER», igual que el panel.** Los dos
  lectores lo toman ahora de la misma constante (`CONTENEDOR_DE_LAS_FILAS`). Una celda con solo espacios cuenta como
  vacía en los dos. Otra forma de escribirlo («40HC REEFER», «40' HC REEFER») sigue quedando NO ENVIADA.
- **El panel marca antes de correr la fila de MAERSK que pide otro contenedor,** como ya marca la fila sin ruta: al
  lado de «Reserva N» dice «otro contenedor: …» con el que pide, y el registro las cuenta aparte con un aviso. Sigue
  marcada para correr, así que queda NO ENVIADA con su motivo y llega a la planilla.
- **MAERSK ya no tiene ramas para un contenedor que no es reefer.** Eran seis, no dos como decía el informe del
  encargo 63 (ver «Premisas»). Con el decorador del 63, a `reservar_maersk` solo llega la fila con «40 HC REEFER», y
  ninguna se alcanzaba.
- **Ninguna condición de freno salta.** Las 21 filas de MAERSK de `logs/`, y las 7 que llegaron a la guarda, pasaron
  por el lado reefer de cada rama. Y no hay otro camino al cuerpo del reservador: por el camino real, el reservador
  de antes y el de ahora hacen exactamente lo mismo con 14 formas del contenedor (ver «FRENA SI»).

## Paso 0

Lo que hacía el código en `98cbbcb`, leído y medido:

- **La consola** (`leer_reservas`): sin la columna de contenedor, «40 HC REEFER»; con la columna, el texto de la celda,
  y la celda vacía quedaba vacía. **El panel** (`leer_filas`): la celda vacía también daba «40 HC REEFER».
  Medido sin red, con los dos lectores sobre una planilla sintética: con la celda vacía, con `None` o con tres
  espacios, la consola daba `''` y el panel `'40 HC REEFER'`; con otro texto, los dos lo mismo.
- **Las marcas del panel** (`/api/filas`, `_con_su_marca`): `sin_nave`, `manual`, `sin_puerto` y `sin_destino`. La
  fila con otro contenedor no tenía marca: quedaba NO ENVIADA recién al correr. La tabla no muestra el contenedor.
- **Las ramas de MAERSK según el contenedor**, todas en `reservar_maersk` y `_mk_contenedor`, con
  `es_reefer = "REEF" in cont or "RF" in cont or "RH" in cont`:
  1. los términos del commodity: SALMON, FISH, SEAFOOD con reefer; FISH y GOODS sin reefer;
  2. la opción del commodity: con reefer, el salmón congelado o una opción congelada; sin reefer, la primera, sin
     mirar;
  3. el control de temperatura, solo con reefer;
  4. la palabra que se escribe en el tipo de contenedor: el tamaño («45», «40» o «20») y «Reefer», o «High» con «HC»
     o «HIGH», o «40» sin nada;
  5. el peso: el de `config.json` con reefer, y 20.000 kg sin reefer;
  6. los ajustes reefer (tipo, temperatura y genset), solo con reefer.
- **Quién llega a ese cuerpo:** `reservar_maersk` lleva cuatro decoradores, y el más interno,
  `_mk_con_el_contenedor_de_la_fila`, deja pasar solo la fila cuyo contenedor, sin distinguir mayúsculas y con los
  espacios de a uno, es «40 HC REEFER». Esa fila trae siempre «REEF» y «40», y no trae «45» ni «20», así que toma
  siempre el lado reefer de las seis ramas.

Veredicto del paso 0: **CICLO** en las tres partes.

## Lo medido antes de cambiar nada

**Por qué lado pasó cada fila guardada** (`medir_ramas.py`; universo: cada bloque «[MAERSK fila N]» de los `log.txt`
de `logs/`, 0 carpetas sin `log.txt` descartadas; control positivo que aborta: las 21 filas y las 7 de la guarda de
los encargos 62 y 63):

| | filas | primer término | algún «GOODS» | control de temperatura | peso | «reefer cont» / «reefer temp» / genset |
|---|---|---|---|---|---|---|
| todas | 21 | SALMON en 21 | 0 | 21 | 22500 en 14, sin peso en el log en 7 | 21 / 21 / 21 |
| las de la guarda | 7 | SALMON en 7 | 0 | 7 | 22500 en 7 | 7 / 7 / 7 |

Las 7 sin peso en el log se cortaron antes de anotarlo; ninguna dice 20000. En las seis ramas, todas las filas
pasaron por el lado reefer.

**Otro camino al cuerpo** (leído en el código de `98cbbcb`):

- `reservar_maersk` se nombra solo en `RESERVADORES`, que usan los dos orquestadores (`ejecutar_reservas` y
  `_web_worker`); ambos llaman al reservador decorado.
- `_mk_contenedor` lo llama solo `reservar_maersk`.
- El contenedor de la fila lo escriben solo los dos lectores, y entre el decorador y el cuerpo no corre nada que lo
  cambie.
- El otro `es_reefer` del programa es de HYUNDAI (`_hmm_llenar_detalles`), y no se toca.

## Lo que cambió

En `AQUASHIELD.py`:

- **Los lectores:** `leer_reservas` da `CONTENEDOR_DE_LAS_FILAS` a la celda vacía, y `leer_filas` usa la misma
  constante en vez del texto escrito aparte.
- **La marca:**
  - `_con_su_marca(fila, nav)` agrega `otro_contenedor`, lo que diga `_otro_contenedor`, solo si la fila trae nave y
    ruta: es el orden en que los orquestadores apartan las filas, y la fila sin nave o sin ruta lleva la marca de su
    motivo.
  - La naviera de cada fila sale de `_nav_de_la_fila` (nueva): la de la hoja o, en CONSOLIDADO, la de su columna
    Naviera. `_web_worker` reparte las filas de CONSOLIDADO con la misma función, así que hay una sola regla.
  - La página muestra «otro contenedor: …» junto a «Reserva N», con el contenedor escapado, y avisa cuántas son en el
    registro. El estilo es el de la marca sin ruta.
- **MAERSK:** `reservar_maersk` y `_mk_contenedor` ya no leen el contenedor de la fila.
  - Los términos del commodity son siempre SALMON, FISH y SEAFOOD, con el filtro del salmón congelado.
  - El control de temperatura y los ajustes reefer corren siempre.
  - La palabra del tipo es `MK_PALABRA_CONTENEDOR` («40 Reefer»), la misma de antes, ahora fija.
  - El peso es siempre el de `config.json` (`_peso_reefer`).
  - `_mk_contenedor(page, reserva, reg, det)` pierde el argumento `es_reefer`.

Sin clics nuevos: los que quedan son los mismos de antes, en el mismo orden (lo mide la sonda de abajo). `test_candado`
no cambió.

## El camino real

`sonda_ramas.py` corre el `reservar_maersk` decorado, el de `RESERVADORES`, de `98cbbcb` y del árbol de trabajo. Cada
uno corre en su sandbox (`soporte.cargar`) sobre una página falsa que anota cada acción, desde el principio hasta la
fecha (ahí corta). Los ayudantes que hablan con el portal y que el encargo no toca anotan lo que reciben. La sonda
compara las acciones, lo que se escribe en pantalla y en `log.txt`, el detalle y lo que devuelve cada uno.

- **Control positivo que aborta:** con `_otro_contenedor` apagado en los dos (el decorador deja pasar todo), «20 DRY»
  tiene que dar huellas distintas, y «40 HC REEFER» iguales. Dio 18 diferencias con «20 DRY» (31 pasos el de antes,
  43 el de ahora: el de antes escribe FISH, pulsa la primera opción y se salta el control y los ajustes) y 0 con «40
  HC REEFER» (43 pasos).
- **Por el camino real, con los cuatro decoradores:** 14 contenedores, 0 descartados, **0 con huellas distintas**.
  - Llegan a la fecha, con 43 pasos iguales: «40 HC REEFER», «40 hc reefer», « 40  HC⇥REEFER », con espacios
    duros, y «40 Hc ReEfEr».
  - Quedan NO ENVIADA sin tocar la página, igual en los dos: «20 DRY», «40HC REEFER», «40' HC REEFER», «40 HC RF», la
    celda vacía, `None`, «45 HC REEFER», «40 HIGH CUBE» y «40 DRY HC».
- **Los dos lectores**, con una columna «Tipo contenedor» en MAERSK:

  | celda | antes: consola / panel | ahora: consola / panel |
  |---|---|---|
  | vacía, `None` o «   » | `''` / «40 HC REEFER» | «40 HC REEFER» / «40 HC REEFER» |
  | «40 HC REEFER», «20 DRY», «40hc reefer», 40 | iguales en los dos | iguales en los dos |
  | sin la columna | «40 HC REEFER» / «40 HC REEFER» | igual |

## Pruebas, mutaciones, censo y suite

- **Pruebas nuevas (6):**
  - `test_clics.TestMaerskSoloReefer`:
    - `test_la_fila_hace_siempre_lo_de_un_reefer` corre el reservador decorado hasta la fecha, con «40 HC REEFER» y
      con « 40 hc  reefer ». Verifica SALMON, el salmón congelado, el control de temperatura, «40 Reefer», 22500, -20,
      los ajustes reefer y el genset.
    - `test_sin_ramas_por_el_contenedor` es una foto: ni `reservar_maersk` ni `_mk_contenedor` leen el contenedor ni
      traen «GOODS», «20000» o «REEF», y los pasos reefer van sin condición.
  - `test_planilla.TestContenedorDeLaFila.test_los_dos_lectores_dan_el_mismo_contenedor`.
  - `test_consola.TestEjecutarReservas.test_fila_de_maersk_con_la_celda_vacia_va_al_portal`.
  - `test_web.TestPanelCorridas.test_filas_dicen_si_piden_otro_contenedor`, en MAERSK, ONE y CONSOLIDADO, y con la
    fila sin nave o sin destino.
  - `test_envio.TestLecturaDelPanel.test_marca_y_cuenta_aparte_las_filas_con_otro_contenedor`, que corre en Node la
    marca de la tabla, con el contenedor escapado.
- **Fotos al día, a propósito:**
  - las llamadas a `_mk_contenedor` sin `es_reefer`;
  - `_mk_elegir_reefer` sin condición;
  - el peso de `TestContenedorMaersk`, que ahora tiene que ser 22500;
  - la segunda mitad de la prueba de la consola del 63, con «40HC REEFER» en vez de la celda vacía: ahora la celda
    vacía va al portal;
  - el estilo de la marca sin ruta.
- **La foto que solo ve la foto:** una rama que volviera a mirar el contenedor, por ejemplo los ajustes reefer dentro
  de `if "REEF" in …`, no cambia lo que hace ninguna fila que llega al reservador, porque siempre es reefer. Por eso
  `test_sin_ramas_por_el_contenedor` es una foto, y sus tres mutaciones (`e64-vuelve-*`) las ve solo ella.
- **Mutaciones:**
  - 20 nuevas (`e64-*`).
  - 6 viejas con su texto viejo al día: el contenedor sin la columna, el reparto de CONSOLIDADO, el peso de una sola
    fuente, el estilo de la marca sin ruta y las dos «como antes» de las dos listas.
  - 2 con otras pruebas: `e63-la-celda-vacia-pasa` ya no la ve la prueba de la consola, porque ningún lector da la
    celda vacía; `e63-otro-contenedor-de-las-filas` la ven también la página y los lectores.
  - El chequeo previo de todas (`mut_viejos.py`): 2.251 mutaciones y 791 pruebas, cada texto viejo una sola vez, las
    26 tocadas compilan, toda prueba con su mutación y 0 problemas.
- **El censo del área** (`alcance_censo.py`, `lanzar_censo_e64.py`, aparte y con el equipo despierto):
  - qué entró: las 20 del encargo, las del 62 y el 63, las 4 viejas con su texto viejo al día que no son de esos
    encargos, las que caen a 15 líneas o menos de lo que cambió en `AQUASHIELD.py`, y las que nombran una prueba
    cuyo camino cambió. Esas son los dos lectores (`test_planilla` entero), la consola que reserva, las marcas y el
    reparto del panel, el reservador de MAERSK y sus listas, `test_candado`, el peso y la regla del contenedor;
  - **377 mutaciones, 573 pares y 183 pruebas: los 573 muerden.** El control (la copia sin mutar) pasa, y la foto de
    los 4.882 originales da 0 cambios. Corrió de las 00:21 a las 00:46 del 14-10.
- **La suite:** `tests/correr.py` (con `correr_sin_tope.py`), sobre el árbol que se commitea: **791 pruebas, OK, en
  696 s**, de las 00:46 a las 01:05 del 14-10, con 0 cambios en las 4.882 entradas fotografiadas de los originales. Sin
  suspensiones ni reinicios: 0 eventos de Kernel-Power desde las 00:20, y la misma consulta sobre los últimos 3 días
  encuentra 23, entre ellos 3 suspensiones (506 y 507).

## FRENA SI

1. **«Quitar las ramas cambiaría lo que hace alguna reserva guardada que llegó a la guarda»: no salta.** Las 7
   reservas de MAERSK que llegaron a la guarda pasaron por el lado reefer de cada rama:
   - SALMON primero;
   - el control de temperatura marcado;
   - 22500 kg;
   - los ajustes reefer, su temperatura y el genset.

   Las ramas quitadas son el otro lado. Y para cualquier fila que llegue al reservador, el de antes y el de ahora
   hacen lo mismo, paso por paso («El camino real»).
2. **«Alguna de esas ramas sí se alcanza por otro camino»: no salta.** El único camino al cuerpo es el reservador
   decorado, que solo deja pasar «40 HC REEFER», y con esa fila el de antes toma siempre el lado reefer. Con 14 formas
   del contenedor, 0 diferencias, y el control muestra que la sonda sí ve las ramas cuando se alcanzan.

## Lo decides tú

1. **Dónde va la marca:** junto a «Reserva N», porque la tabla no muestra el contenedor (la marca sin ruta va en la
   celda que le falta). Si prefieres una columna «Contenedor» en la tabla, es un cambio chico en la página.
2. **Dos lecturas de la fila que MAERSK tampoco usa**, fuera de este encargo: `reservar_maersk` mira
   `reserva["commodity"]` y `_mk_contenedor` mira `reserva["peso"]`, pero ningún lector pone esas llaves. Siempre van
   los términos fijos y el peso de `config.json`. Quitarlas es limpieza, como la de este encargo.

## El push

**No lo subo:** el repositorio es público (subir publica), y los lanzadores de los colegas traen código de GitHub
(`actualizar.py`, desde `estable`). Sube `main` con dos commits; el bloque va al final del mensaje de cierre.
`estable` no cambia: la avanzas tú.

## Re-medir

Con `TEMP`, `TMP` y `TMPDIR` en la carpeta de trabajo, como en `entorno_e64.sh`:

- `python medir_ramas.py`: por qué lado de cada rama pasó cada fila de MAERSK de `logs/`.
- `python sonda_ramas.py`: el reservador de antes y el de ahora por el camino real, y los dos lectores. Antes hace
  falta `git show 98cbbcb:AQUASHIELD.py > viejo/AQUASHIELD.py`.
- `python mut_viejos.py e64-`: el chequeo previo de todas las mutaciones.
- `python alcance_censo.py` y `python lanzar_censo_e64.py`: el censo del área, aparte.
- `python tests/correr.py`: la suite (con el equipo cargado, `correr_sin_tope.py`, que le da 7200 s).
- `python -m unittest test_clics.TestMaerskSoloReefer test_planilla.TestContenedorDeLaFila`, desde `tests/`: las
  pruebas nuevas de MAERSK y de los lectores.

## NO retroceder

- **No vuelvas a dejar vacía la celda vacía en la consola:** con la columna, la fila quedaba NO ENVIADA en la consola
  y no en el panel. Es decisión de Marcelo, y la vigilan `TestContenedorDeLaFila` y la prueba de la consola.
- **No vuelvas a poner en `reservar_maersk` una rama que mire el contenedor:** el decorador decide, y una rama así no
  la ve ninguna prueba de comportamiento, solo la foto.
- **La marca del panel sale de `/api/filas`, con la regla del programa:** no la decidas en la página.

## Defectos de instrumento que me cacé

- **Dos pruebas nuevas cayeron en la primera corrida por error mío:**
  - `dict(celdas, **{…})` con claves que no son texto;
  - suponer que la consola escribe el detalle al final, cuando escribe más campos y termina en «· SIN EMITIR».
  Las corregí y pasan.
- **Otra vez la herramienta Bash juntó `\\n`** en un script escrito con un heredoc: la aserción de «una sola vez» lo
  frenó antes de escribir nada. Lo rehíce con la herramienta Write, como dice la fila del entorno.
- **Un reemplazo con Edit dejó pegado al final de una línea el resto de la línea vieja** (166 caracteres, en
  `CLAUDE.md`). Lo vio el chequeo del diff (`revisar_diff.py`) y lo partí.
- **Medí el largo de las líneas con `awk`**, que cuenta bytes en esta máquina (la fila del entorno lo dice). Lo
  rehíce con Python.

## Premisas del encargo que se refutaron

- **«Las ramas sin reefer» eran seis, no dos.** El informe del encargo 63 («Lo decides tú», 4) nombraba la palabra
  «High» y los 20.000 kg. Faltaban los términos FISH y GOODS, la primera opción sin mirar, el control de temperatura y
  los ajustes reefer. Se quitaron las seis: el encargo pide las ramas para contenedores que no son reefer, y las seis
  lo son.

## Residual

| # | Lo que queda | Condición de reapertura |
|---|---|---|
| 1 | La marca va junto a «Reserva N», no en una columna del contenedor | Si prefieres una columna |
| 2 | `reserva["commodity"]` y `reserva["peso"]` no los pone ningún lector, y MAERSK los mira | Si decides quitarlos |
| 3 | El aviso de la página repite «40 HC REEFER» como texto. Lo ata `test_marca_y_cuenta_aparte_las_filas_con_otro_contenedor`, y la mutación del contenedor de las filas la ve | Si el contenedor de las filas cambia |
| 4 | `_otro_contenedor` sigue cortando el contenedor vacío, que ningún lector da: el decorador mira cualquier reserva que le llegue | No hace falta reabrirlo |
| 5 | Del encargo 63: si la lista de los ajustes reefer trae una sola «Standard (40´)», y el clic en el portal | La primera corrida de MAERSK |
| 6 | Las revisiones que pide ECC no se lanzaron | Si las pides |

## Reglas de método (v23)

- **Aplicadas:** las 21 universales. En especial:
  - el control positivo que aborta, en las dos sondas (las 21 y 7 filas de `logs/`; «20 DRY» con el decorador
    abierto);
  - medir por el camino real: el reservador decorado, el de `RESERVADORES`, y no `_mk_contenedor` suelto. El control
    sobrevive al cambio, porque compara el de antes, que tiene las ramas, con el de ahora;
  - la unidad la fija el sujeto: cada fila de MAERSK, no cada corrida;
  - todo registro es una hipótesis: mi informe del 63 contaba dos ramas, y eran seis;
  - fuente única: una constante para los dos lectores y una función para la naviera de la fila. La copia del texto en
    la página está atada por su prueba, como `NOMBRE_DEL_MODO`;
  - el cambio y su guardián juntos: cada pieza nueva con su prueba y su mutación;
  - cada reemplazo, una sola vez, y LF sin BOM en todo lo escrito.
- **Las del módulo** (`CLAUDE.md`): las pruebas son fotos y se actualizan en el mismo cambio, toda prueba nueva con su
  mutación, nunca importar `AQUASHIELD.py` desde la raíz ni usar el 8765, la sonda de secretos antes de cada commit y
  `test_candado` sin cambios.
- **Choques:** las reglas de ECC piden anotaciones de tipo y revisiones automáticas. Mandan las reglas permanentes y
  el estilo del módulo: no las agregué, y las revisiones se proponen.

## Lo que dio en el repo

Dos commits en `main`, sin push (el push lo haces tú):

- `fc4352d` fix: la consola lee como el panel el contenedor vacío, el panel marca la fila de MAERSK con otro
  contenedor, y MAERSK sin las ramas que ya no se alcanzaban (`AQUASHIELD.py`, y en `tests/`:
  `test_clics.py`, `test_consola.py`, `test_envio.py`, `test_planilla.py`, `test_web.py` y `mutaciones.py`);
- el commit siguiente, docs: `CLAUDE.md`, `LEEME.md` y este informe.

Los dos llevan de autor y de committer el correo noreply del repo, y la sonda de secretos dio 0 antes de cada uno.
