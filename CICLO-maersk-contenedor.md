# Encargo 62 · MAERSK elige el contenedor de la fila: la única opción «40 Reefer High»

**Base:** `C:\dev\Agendamiento Reservas` @ `455c0fd` · árbol limpio al empezar.

Con `metodo-ciclo` v20 (la versión del archivo; la sesión la tenía cargada). Sin abrir ningún portal y sin red.

## En resumen

- **MAERSK ya no pulsa la primera opción que trae «40» y «Reefer»:** pulsa la única cuyo texto entero es «40 Reefer
  High». Si la lista no trae exactamente una, la fila queda NO ENVIADA, con el motivo (cuántas había y cuáles), la
  captura y el HTML, sin pulsar nada.
- **Antes de elegir deja la evidencia de la lista** (`mk_f<fila>_contenedor`: la captura de la ventana y el HTML con
  sus raíces shadow), como las listas de sugerencias. La primera vez que se guarda esa lista.
- **Ninguna de las dos condiciones de freno salta:** las 7 reservas de MAERSK que llegaron a la guarda eligieron «40
  Reefer High», y las 36 filas de las dos planillas de este equipo traen «40 HC REEFER» (40 pies, reefer, high cube).
  Lo que no se pudo medir: si la lista traía una sola «40 Reefer High» (nunca se guardó).
- **Medido con Playwright de verdad, sin red, sobre una página que imita el campo:** el código de este encargo elige
  «40 Reefer High» aunque la lista ponga primero «40 Reefer Standard Shipper own»; el de antes, sobre la misma página,
  eligió esa, como el 08-10.

## Paso 0

- **Lo que hacía `_mk_contenedor`:** escribe «40 Reefer» en «Select container type and size», espera 1,2 s, y en hasta
  8 lecturas pulsa la primera opción a la vista que trae «40» y «Reefer» (`cand.first.click`). Anota «contenedor tipo:»
  con lo que leyó de esa opción (`text_content`, sin raíces shadow, recortado a 30 caracteres).
- **Ninguna prueba lo tocaba:** 0 menciones de `_mk_contenedor` o de su campo en `tests/`.
- **Junto a él hay otra lista, «Select reefer container type and size»** (los ajustes reefer), que también pulsa la
  primera con «40». No es de este encargo: va a «Lo decides tú».
- **Veredicto:** CICLO.

## Lo medido antes de cambiar nada

**Las elecciones de MAERSK en `logs/`** (`medir_contenedor.py`): cada bloque «[MAERSK fila N]» de cada `log.txt`, con su
«contenedor tipo:» y si llegó a la guarda. La guarda se reconoce por su evidencia (`mk_f<N>_guarda.*`) o por su línea
en `log.txt`, y el 21-09, antes del candado, por la emisión. 0 carpetas sin `log.txt`; 0 bloques sin línea de
contenedor. Control positivo que aborta: las 2 corridas del 08-10 con «40 Reefer Standard Shipper own» tienen que
aparecer, y aparecen.

| Qué | Resultado |
|---|---|
| Filas de MAERSK que llegaron al contenedor | 21, en 17 corridas, del 21-09 al 08-10 |
| La opción que pulsó | «40 Reefer High» en 19 (del 21-09 al 02-10); «40 Reefer Standard Shipper own» en 2 (08-10) |
| Las que llegaron a la guarda | 7: las 5 del 21-09 (emitidas, antes del candado), la del 24-09 y la del 02-10. Las 7, «40 Reefer High» |
| Con la regla nueva | Las 7 habrían elegido la misma, si en su lista era la única con ese texto: eso no está medido |
| La lista de los ajustes reefer | «Standard (40´)» en las 21 |

**El contenedor de las filas** (`medir_planillas.py`, con el lector del panel, `leer_filas`, de una copia del
programa): las planillas de la carpeta del programa (1) y la última subida al panel (1). Ninguna tiene una columna de
contenedor, así que sus 36 filas (6 en CONSOLIDADO y 30 en la otra hoja, en cada una) traen el valor por omisión del
lector: «40 HC REEFER», el contenedor de 40 pies, reefer, high cube. Control positivo que aborta: una planilla
sintética con una columna «Tipo contenedor» y «20 DRY» sale con ese valor.

## Lo que cambió

- **`_mk_elegir_contenedor`** (lo llama `_mk_contenedor`, que sigue llenando la cantidad y el peso como antes):
  - escribe en el campo lo mismo que antes («40 Reefer»), sin clics nuevos;
  - lee las opciones a la vista (`mc-option:visible`, su texto en una línea, sin la raíz shadow, como lo leía el
    programa) hasta que dos lecturas seguidas den lo mismo, hasta `MK_LECTURAS_CONTENEDOR` veces (12, cada 0,5 s;
    hipótesis): la lista puede llegar de a poco, como la de las sugerencias;
  - deja la evidencia `mk_f<fila>_contenedor`, con la lista o sin ella;
  - elige la única cuyo texto entero es `MK_CONTENEDOR`, «40 Reefer High», tal cual (con los espacios de a uno).
    «40 Reefer High Shipper own», «40 reefer high» o «40 Reefer High Cube» no son esa;
  - antes de pulsar, vuelve a leer la lista: si ya no es la que guardó en la evidencia, no pulsa;
  - si no hay exactamente una, si la lista cambió, si el campo no acepta lo escrito o si la opción no acepta el clic,
    corta (`ObjetivoNoEncontrado`, «Tipo de contenedor de MAERSK»): el decorador de `reservar_maersk` deja la fila NO
    ENVIADA, con la captura y el HTML del paso (`mk_f<fila>_sin_objetivo`). Hasta ahí, si algo fallaba, lo anotaba
    («contenedor err») y la reserva seguía sin el tipo.
- `log.txt` dice cuántas opciones dicen «40 Reefer High» y de cuántas, y después «contenedor tipo: 40 Reefer High»
  como siempre.
- **Lo que no cambió:** lo que se escribe en el campo, la cantidad, el peso, los ajustes reefer y todo lo demás de
  MAERSK. Nada para disfrazar el navegador. `test_candado` no cambió y pasa.

## El camino real, en un Chromium sin red

`sonda_contenedor.py`: el `_mk_contenedor` de este árbol y, de control, el de `455c0fd`, cada uno en una copia aparte,
con Playwright de verdad sobre una página local. Al escribir, la página muestra a los 0,6 s una lista de `mc-option`,
cada una con una raíz shadow que le agrega un código, y a los 1,2 s agrega una opción más. Un clic deja la opción en el
campo.

| Lista | Este encargo | El de antes |
|---|---|---|
| «…Standard Shipper own», «…High Shipper own» y, al final y tarde, «40 Reefer High» | «40 Reefer High»; la evidencia trae las 3 opciones y sus raíces shadow | «40 Reefer Standard Shipper own» |
| Sin «40 Reefer High» | No pulsa: «hay 0 entre 2: …»; el campo queda con lo escrito | «40 Reefer Standard Shipper own» |
| Dos «40 Reefer High» | No pulsa: «hay 2 entre 2: …» | La primera |

El control (el de antes elige «40 Reefer Standard Shipper own», como el 08-10) aborta la sonda si no se da.

## Pruebas, mutaciones, censo y suite

**Las pruebas nuevas (8)**, en `test_clics.TestContenedorMaersk`, con una página falsa que anota en orden lo escrito,
cada captura y cada clic, y lo que no espera:
- el contenedor es el de las filas;
- elige la única con el texto entero, con la que elegía la regla de antes primera en la lista y otras que traen «40
  Reefer High» dentro de otro texto;
- espera la lista quieta;
- sin una sola, no pulsa nada (sin lista, ninguna, dos, otra mayúscula, otro texto), y deja la evidencia;
- si la lista cambia mientras guarda la evidencia, no elige;
- el campo o el clic que fallan cortan;
- por el decorador, la fila queda NO ENVIADA con el motivo y las dos capturas;
- `reservar_maersk` lo llama una vez, antes de la guarda.

**Foto que cambió a propósito:** `test_evidencia.TestCadaReservadorLaDeja.test_solo_ahi` cuenta a
`_mk_elegir_contenedor` entre los que dejan evidencia.

**Las mutaciones:** 11 nuevas (`e62-*`). El chequeo de anclas de toda la lista (`mut_viejos.py`): 2.200 mutaciones, 773
pruebas, 0 problemas.

**El censo del área** (`alcance_censo.py`, `lanzar_censo_e62.py`): las 11 del encargo, las que caen a 15 líneas
o menos de lo que cambió en `AQUASHIELD.py`, y las que nombran una prueba cuyo camino cambió (la clase nueva, la
foto de quién deja evidencia, el decorador y `test_candado`). **108 mutaciones, 182 pares, 78 pruebas: los 182
muerden.** El control (la copia sin mutar) pasa, y la foto de los 4.880 originales, 0 cambios. De las 17:14 a las
17:47.

**La suite:** `tests/correr.py` (con `correr_sin_tope.py`), sobre el árbol que se commitea: **773 pruebas, OK, en
786 s**, de las 19:51 a las 20:05, con 0 cambios en las 4.880 entradas fotografiadas de los originales. Un primer
intento, desde las 17:47, no vale: el equipo entró en suspensión (Modern Standby, Kernel-Power 506 y 507) de las
17:56 a las 19:50, con la suite a medias; lo corté y lo volví a correr. En el segundo, ninguna suspensión.

## FRENA SI

- **Una reserva de MAERSK que llegó a la guarda habría quedado NO ENVIADA:** no salta. Las 7 eligieron «40 Reefer
  High», el texto entero que leyó el programa (14 caracteres, menos de los 30 del recorte). Con la regla nueva, la
  elegirían igual si era la única con ese texto en su lista. Eso no se puede medir: la lista no se guardó nunca. Si no
  lo era, la regla corta, sin pulsar, con la evidencia que ahora sí queda.
- **Una fila con un contenedor que no corresponde a «40 Reefer High»:** no salta. Las 36 filas de las planillas de este
  equipo traen «40 HC REEFER», el valor por omisión del lector: ninguna tiene columna de contenedor.

## Lo decides tú

1. **El contenedor de la fila no se mira:** MAERSK elige «40 Reefer High» siempre, como decidiste. Si un día una
   planilla trae una columna de contenedor con otro valor («20 DRY», por ejemplo), MAERSK igual reservaría un 40 Reefer
   High. Si una fila con otro contenedor tiene que quedar NO ENVIADA, es un cambio chico.
2. **La lista de los ajustes reefer** («Select reefer container type and size») sigue pulsando la primera opción con
   «40». Fue «Standard (40´)» en las 21 filas de `logs/`. Si quieres la misma regla (la única con un texto dado, con su
   evidencia), dime el texto.

## El push

**No lo subo:** el repositorio es público (subir publica), y los lanzadores de los colegas traen código de GitHub. Sube
`main` con dos commits; el bloque va al final del mensaje de cierre. `estable` no cambia: la avanzas tú.

## Re-medir

Todo corre desde `scratchpad\e62`, en Git Bash, después de `source entorno_e62.sh`, con Python 3.13.

| Número | Comando |
|---|---|
| Lo que eligió MAERSK en `logs/` y si llegó a la guarda | `python medir_contenedor.py` |
| El contenedor de las filas | `python medir_planillas.py` |
| El camino real, con el control del código de antes | `python sonda_contenedor.py` |
| Las pruebas nuevas | `cd tests; python -m unittest test_clics.TestContenedorMaersk` |
| Las anclas de las mutaciones | `python ../e61/mut_viejos.py e62-` |
| El censo del área | `python alcance_censo.py`; `python lanzar_censo_e62.py` (aparte; escribe `censo_e62.txt`) |

## NO retroceder

- **El tipo de contenedor de MAERSK se elige por su texto entero, y solo si hay uno:** nunca «la primera que trae…».
- **La lista se guarda antes de elegir,** con la lista o sin ella.
- **Si la lista cambió mientras se guardaba, no se pulsa:** no se elige de una lista distinta de la que quedó.

## Defectos de instrumento que me cacé

1. **La primera medición de la guarda daba solo 2 reservas:** buscaba la evidencia de la guarda o la línea con que se
   detiene, que no existían el 21-09; esas 5 filas pasaron la guarda y se emitieron. Con la emisión como señal, 7.
2. **Mi primera página falsa no esperaba el peso,** que `_mk_contenedor` llena después del tipo: lo anotaba como
   prohibido. Ahora lo acepta y lo anota aparte.
3. **Mi primer alcance del censo nombraba todas las pruebas de MAERSK** (489 mutaciones): ninguna llega a
   `_mk_contenedor`. Lo acoté a las que sí (108).
4. **Un `head -20` cortó el resumen de una corrida de pruebas:** las líneas de registro que dicen «Error:» pasaban el
   filtro. La volví a correr con la salida a un archivo.

## Premisas del encargo que se refutaron

- Ninguna. «Las 15 corridas anteriores» son 15 corridas con 19 filas de MAERSK (la del 21-09 trae 5).

## Residual

| # | Lo que queda | Condición de reapertura |
|---|---|---|
| 1 | Si la lista de MAERSK trae una sola «40 Reefer High» no está medido: la primera corrida lo dice, con su evidencia | La primera corrida de MAERSK |
| 2 | La lista quieta con dos lecturas iguales y 12 lecturas como tope son hipótesis | Si una corrida corta con la lista a medias |
| 3 | Si la lista cambia mientras se guarda la evidencia, la fila queda NO ENVIADA, aunque siguiera trayendo una sola «40 Reefer High» | Si pasa |
| 4 | Una mayúscula distinta («40 reefer high») deja la fila NO ENVIADA: la regla es el texto entero, tal cual | Si MAERSK cambia el texto |
| 5 | El clic en la opción no está probado en el portal | La primera corrida de MAERSK |
| 6 | Las revisiones que pide ECC no se lanzaron | Si las pides |
| 7 | Una suspensión del equipo invalida la suite (su plazo es de reloj): le pasó al primer intento | Si se corre con el equipo sin atender |


## Reglas de método (v20)

- **Aplicadas:** las 21 universales. En especial:
  - la unidad la fija el sujeto: cada fila de MAERSK, no cada corrida;
  - el control positivo que aborta, en las tres sondas;
  - se mide sobre el camino real (Playwright de verdad, con raíces shadow y una lista que llega tarde), y el control
    sobrevive al cambio: es el código de antes sobre la misma página;
  - todo salto lleva su contador: 0 carpetas sin `log.txt`, 0 bloques sin contenedor;
  - el negativo que muerde: cada prueba nueva con su mutación, y el censo del área;
  - frenar en lo que es tuyo: el contenedor de la fila y la lista de los ajustes reefer.
- **Las del módulo** (`CLAUDE.md`): `test_candado` no cambia; ningún clic nuevo; casos sintéticos; la sonda de
  secretos antes de cada commit; el correo noreply de autor y de committer; las planillas y `logs/` solo se leen, y
  este informe no trae ningún dato de ellas salvo tipos de contenedor y conteos.
- **El push:** el repositorio es público: no subo, entrego el bloque.
- **Pieza 8:** opcional; este informe es Markdown y no lo rendericé.

## Lo que dio en el repo

Dos commits en `main`, sin push (el push lo haces tú):

- `400678c` fix: MAERSK elige la única opción «40 Reefer High», con la evidencia de la lista (`AQUASHIELD.py`, y en
  `tests/`: `test_clics.py`, `test_evidencia.py` y `mutaciones.py`);
- el commit siguiente, docs: `CLAUDE.md`, `LEEME.md` y este informe.

Los dos llevan de autor y de committer el correo noreply del repo, y la sonda de secretos dio 0 antes de cada uno.
