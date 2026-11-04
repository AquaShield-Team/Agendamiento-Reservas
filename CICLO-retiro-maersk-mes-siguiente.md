# Encargo 97 · Las corridas de hoy y la fecha de retiro de MAERSK en el mes siguiente

**Base:** `AquaShield-Team/Agendamiento-Reservas` @ `d68e3f0` · árbol limpio al recibir el encargo. El cambio y este
informe van en el commit que le sigue. En GitHub, `main` en `d68e3f0` y `estable` en `77d5801` (`ls-remote`, al abrir),
como dice el registro. Hecho con `metodo-ciclo` v40, la misma del disco.

Datos: los `log.txt` y los HTML del calendario de `logs/` y de `1. pruebas`, que git no sigue, y dos corridas en modo
prueba que hice hoy desde este equipo con la fila de MAERSK de tu planilla de hoy. Las naves, los puertos y los números
de cotización no van en este informe; el operador va como `<operador>`.

## Lo que salió

| Pregunta | Respuesta |
|---|---|
| ¿Tus 6 corridas de hoy corrieron con `d68e3f0` y llegaron a OK-EJEMPLO de verdad? | Sí. Son las 6 filas de una corrida (una por naviera), con «Versión del programa: main · d68e3f0» y «modo prueba», y cada una llegó a su paso final y a OK-EJEMPLO. Lo único fuera de lo común son tres avisos que ya eran así (sección 1). |
| ¿El programa pasa el calendario al mes siguiente? | Sí, con su único «Next month», a lo más un mes y nunca hacia atrás. Elige con la regla, que no cambia, y comprueba que el calendario muestre el día que sigue y que la tarjeta muestre el elegido (sección 2). |
| ¿Hay HTML guardado del calendario de fin de mes? | No: en este equipo no hay ninguna corrida de MAERSK del 29 al 31 de octubre. Hay calendarios de octubre y de noviembre con la misma forma, y con ellos el recorrido de un viernes 30-10 se probó sin red (sección 3). |
| ¿El calendario deja avanzar de mes sin elegir antes otra cosa? | Sí. En el portal, con «hoy» simulado el 30-11, el programa pulsó «Next month» con el calendario recién abierto, y en medio segundo mostró diciembre. Ninguno de los dos FRENA SI se cumple (sección 4). |

## 1. Las corridas de hoy

En `logs/` hay una sola corrida de hoy antes de este encargo: `web_todas_<operador>_20261104_110104`, de las 11:01 a
las 11:08, con la hoja CONSOLIDADO y 6 reservas, una por naviera. Leído su `log.txt` entero (471 líneas):

- La línea 3 dice «Versión del programa: main · d68e3f0», y la 2, «modo prueba», sin ninguna llave abierta.
- Cada fila llegó a su paso final y se detuvo antes del botón de envío, con OK-EJEMPLO:

  | Naviera | Paso final | Resultado |
  |---|---|---|
  | ONE | Review Booking | OK-EJEMPLO |
  | MSC | Summary | OK-EJEMPLO |
  | CMA-CGM | Envío de la reserva | OK-EJEMPLO |
  | COSCO | Booking Details | OK-EJEMPLO |
  | HYUNDAI | Review & Book | OK-EJEMPLO |
  | MAERSK | Review booking | OK-EJEMPLO |

- Ninguna línea dice REVISAR, ERROR, DETENIDO, NO ENVIADA ni Traceback.
- Busqué también avisos, errores atrapados, reintentos y esperas sin señal. Lo que aparece ya era así:
  - **CMA-CGM**, «⚠ No pude confirmar la ruta: el portal no respondió a «Validar ruta»». Medido en los 21 `log.txt` con
    CMA-CGM de `logs/` y `1. pruebas`: desde el 25-09 pasa en 28 de 28 pulsaciones, también en las del colega del 23-10
    que emitieron. El programa sigue con la carga y la ruta, como siempre.
  - **COSCO**, «error en auto-solver: No module named 'cv2'» tres veces, y después la pausa: `opencv-python` no está en
    `requirements.txt` (encargo 84), así que el rompecabezas lo pasa el operador. La pausa duró 4 s.
  - **HYUNDAI**, «Contract No (Paso 2): sin opción que calce exacto con el contrato (calzan 0 de 0); queda el del
    portal»: la lista del paso 2 viene vacía (encargo 91), y el contrato se elige y se comprueba en el paso 3.
  - **MAERSK**, «busco las salidas desde mañana, no desde hoy» (el FRENO de la fecha de zarpe, de siempre), y la fecha
    de retiro: el jueves 5 no estaba habilitado, y eligió el siguiente día hábil habilitado, el lunes 9, que la tarjeta
    mostró.

Nada que decirte antes del frente 2.

## 2. Qué cambió

- **`_mk_falta_otro_mes`**: si para elegir con la regla hacen falta días después del último que muestra el calendario.
  Es así si el día que toca cae después de él, o si todos los días hábiles desde el que toca hasta él están identificados
  y deshabilitados. Con el día que toca antes del primero que muestra, no: nunca hacia atrás. Con un día hábil sin su
  fecha en medio, tampoco: la regla corta ahí, como antes.
- **`_mk_mes_siguiente`**: pulsa el único «Next month» habilitado (`_JS_MK_MES_SIGUIENTE`, que vuelve a leer el
  calendario) y espera hasta `MK_ESPERA_CALENDARIO` s (10) que el calendario muestre el día que sigue al último que
  mostraba, identificado por su fecha. Deja la evidencia `mk_f<fila>_calendario_siguiente`. Si no hay un solo «Next
  month» habilitado, si falla el clic o si el calendario no pasa al mes siguiente, NO ENVIADA, sin otro clic.
- **En `mkCalendario`** (`_JS_MK_DIAS`), «Next month» es el único control a la vista de la raíz del calendario que se
  llama así (su `label`, su `aria-label` o su texto); el `button` de adentro del `mc-button` es el mismo control. Se
  pulsa ese `button` de más adentro, solo si nada en él está deshabilitado. `_JS_MK_CALENDARIO` dice además cuántos hay
  (`siguientes`), para el motivo.
- **`_mk_fecha_de_retiro`**: con `_mk_falta_otro_mes`, pasa de mes a lo más `MK_MESES_ADELANTE` (1) vez y elige con
  la regla entre los días de los dos meses. Del mes nuevo suma solo los días posteriores al último del anterior
  (`_mk_despues_de`). Después, el día, el «Done» y la tarjeta, como siempre: `_mk_comprobar_retiro` exige que la tarjeta
  muestre el día elegido, o NO ENVIADA.
- **Dos lecturas quietas** (de las revisiones): antes de pasar de mes, el programa vuelve a leer el calendario hasta que
  dos lecturas seguidas digan lo mismo (`_mk_calendario_quieto`, `_mk_mismos_dias`), y decide con esa. En el mes nuevo,
  espera dos lecturas iguales con el día que sigue. Si en 10 s no se queda quieto, NO ENVIADA. El caso normal, sin pasar
  de mes, lee como antes.
- **El plazo de entrega:** si el de la tarjeta («Gate-in deadline») vence en el mes que se ve, no pasa de mes, porque
  ningún día del siguiente serviría. Si además es anterior al día que toca, el motivo es el del plazo, como antes. Si no,
  uno nuevo: no hay un día hábil habilitado hasta fin de mes, y no pasa al siguiente por el plazo.
- **Los motivos que decían «cambiar de mes es un clic que no está permitido»** dicen ahora «el calendario no se pasa
  más de un mes adelante («Next month») ni hacia atrás».

## 3. Lo medido sin red

Con `.trabajo/e97/medir_calendarios.py`: la lectura del programa, de una copia de `AQUASHIELD.py`, sobre cada
`mk_f*_calendario*.html` guardado, en un Chromium sin red. Su control positivo es el calendario de hoy, que tiene que dar
lo que dice su `log.txt` (30 días del 1 al 30 de noviembre, 5 habilitados), o aborta: dio eso.

- **35 calendarios** (32 antes de las corridas de este encargo, y 3 de ellas): 27 de octubre (el 14 y el 15 en este
  equipo, y 25 filas del colega el 23), 7 de noviembre (del 2 al 4) y 1 de diciembre, el de la sonda.
- **Cada uno abre en el mes de su corrida**, con solo los días de ese mes (30 o 31, todos con su fecha por la cabecera),
  sin días de otros meses.
- **Cada uno trae un solo `mc-button` «Next month»** (`id="nextButton"`), a la vista y sin `disabled`, con su `button`
  de adentro de `aria-label` «Next month»; lo mismo con «Previous month». `_JS_MK_MES_SIGUIENTE` da ese `button` en los
  35.
- **No hay ninguna corrida de MAERSK del 29 al 31 de octubre en este equipo** (ni en `logs/` ni en `1. pruebas`): el HTML
  de la que falló no está. El más cercano es el del colega del 23-10, que habilitaba del 26 al 30 de octubre.
- **El recorrido de fin de mes, con HTML real y las funciones del programa**, para un viernes 30-10 simulado. El paso de
  mes no se puede dar en un HTML guardado, porque no corre el código del portal: se simula cargando el de noviembre.
  - El calendario de octubre: el del 23-10 y el del 15-10. `_mk_falta_otro_mes` da que hace falta el mes siguiente,
    porque el día que toca, el lunes 2-11, no está a la vista.
  - «Next month»: `_JS_MK_MES_SIGUIENTE` da el `button` de `#nextButton`, a la vista y habilitado.
  - El calendario de noviembre, el del 04-11: muestra el 1-11, el día que sigue al último de octubre.
  - La regla elige el lunes 9, porque el 2 no está habilitado en ese calendario, y `_JS_MK_DIA_DE_RETIRO` encuentra su
    botón. Los dos pares, en verde.

## 4. En el portal, en modo prueba

Dos corridas desde este equipo, con la fila de MAERSK de tu planilla de hoy. Las dos con el programa del repo vivo y sus
perfiles, en un panel de prueba abierto en otro rango de puertos (del 28765 en adelante), para no tocar los paneles que
escuchaban en el 8765 y el 8766. Las dos con el candado cerrado, porque el panel aborta si no.

- **El caso normal, con la fecha de hoy** (`web_todas_<operador>_20261104_113309`): **OK-EJEMPLO**, en 86 s. El
  calendario abrió en noviembre. El jueves 5 no estaba habilitado, y eligió el lunes 9, sin «Next month». La tarjeta lo
  mostró. Es lo mismo que tu corrida de las 11:01.
- **La sonda del mes siguiente** (`web_todas_<operador>_20261104_113504`): la misma fila, con la fecha de retiro
  corriendo como si hoy fuera el lunes 30-11. Fue solo en la memoria de ese panel (`vivo_panel.py mes`), y sin el plazo
  de entrega de la tarjeta, que la habría dejado sin pasar de mes.
  - El día que toca era el martes 1-12.
  - El calendario abrió en noviembre, y el programa pulsó «Next month» enseguida, sin elegir nada antes.
  - En 0,5 s el calendario mostró diciembre: 31 días por su cabecera, ninguno habilitado. Se ve así en
    `mk_f10_calendario_siguiente.png`: todos los días en gris.
  - La fila quedó **NO ENVIADA**, con el motivo del plazo de entrega («el último día habilitado en el calendario de
    retiro es el 13-11-2026»). En esa salida no se puede retirar en diciembre. Es lo esperado en una fecha simulada.

**Lo que no se pudo probar en el portal hoy:** elegir un día después de pasar de mes. Para eso el día que toca tiene que
estar en el mes siguiente y habilitado, y hoy el portal habilita del 9 al 13 de noviembre para esta salida. Lo cubren el
recorrido con HTML real (sección 3) y las pruebas con el último día hábil de noviembre, un viernes de fin de mes y el 31
de diciembre (sección 5). La primera vez que pase de verdad será el 30-11, si hay una fila de MAERSK; su `log.txt` dirá
«pulsado 'Next month'» y la fecha elegida.

Las dos corridas se repitieron con el código final, después de los arreglos de las revisiones (sección 6):
- **el caso normal** (`web_todas_<operador>_20261104_115645`): OK-EJEMPLO en 82 s, otra vez el lunes 9 sin pasar de mes.
  Esta vez el portal habilitaba 4 días, no 5: es su ventana, no el programa;
- **la sonda** (`web_todas_<operador>_20261104_115829`):
  - volvió a leer noviembre antes de pasar de mes, y la lectura era la misma;
  - pulsó «Next month» y leyó diciembre dos veces iguales en 1,1 s;
  - quedó NO ENVIADA con el motivo del plazo, como la primera.

## 5. Las pruebas

En `test_clics.TestRetiroMaersk`, con la página falsa de la fecha de retiro, que ahora tiene varios meses, «Next month»
y lecturas que cambian:

- **`test_pasa_al_mes_siguiente`**, los tres casos pedidos:
  - el último día hábil de un mes: el lunes 30-11, y elige el martes 1-12;
  - un viernes de fin de mes: el 30-10. El día que toca es el lunes 2-11; con los días que habilitaban los calendarios
    de noviembre (del 9 al 13), elige el 9, y con el 2 habilitado, el 2;
  - el 31 de diciembre: el 1 de enero del año siguiente y, con los feriados de Chile (Año Nuevo), el lunes 4 de enero.
  - Además, el siguiente día hábil habilitado que cruza de mes (el 25-11, sin días desde el 26: el 1-12), y una celda de
    noviembre en la vista de diciembre que no pisa la del mes propio.
  - En cada uno, los clics («Choose another date», «Next month», el día, «Done»), las dos evidencias, la fecha en la
    tarjeta y las esperas.
- **`test_el_caso_normal_no_pasa_de_mes`**, el negativo: con el día que toca, o el siguiente habilitado, en el mes que se
  ve, los tres clics de siempre y ninguna evidencia del mes siguiente. Como la corrida de hoy: del jueves 5 al lunes 9.
- **`test_falta_otro_mes`**: cuándo hace falta el mes siguiente, y cuándo no (nunca hacia atrás, un sábado o un feriado
  habilitado no cuentan, un día sin su fecha corta).
- **`test_cortes_al_pasar_de_mes`**: sin un solo «Next month», si buscarlo o pulsarlo falla, si el calendario no pasa de
  mes (lo espera 10 s), y con el día que toca antes del primero que se ve; en cada uno, NO ENVIADA sin otro clic.
- **`test_lecturas_a_medio_cargar`** y **`test_el_plazo_frena_el_paso_de_mes`**: los arreglos de las revisiones.
- **`test_js_mes_siguiente`**, en Node, con la forma medida: el `button` de adentro del único «Next month»; y nada si está
  deshabilitado (por atributo, `aria-disabled` o la clase), si hay dos, si está oculto, si está fuera del calendario, o si
  el botón de adentro se llama de otro modo, está oculto o son dos.
- Cambiaron a propósito, porque decían «cambiar de mes es un clic que no está permitido»: `test_elige_el_dia_con_la_regla`,
  `test_sin_el_dia_por_su_fecha_no_pulsa_el_dia` y `test_el_motivo_dice_el_plazo_de_entrega`. Y `test_solo_ahi`, de
  `test_evidencia`, suma la evidencia nueva.

## 6. Las revisiones

Las dos, en clones de `.trabajo/e97` (`revision1` y `revision2`), sobre el cambio antes de sus arreglos.

**Código (`code-reviewer`): aprueba, sin CRÍTICO, ALTO ni MEDIO.** Comprobó que elige bien en fin de mes, de diciembre a
enero y con feriados, que no pasa dos meses ni vuelve atrás, y que no elige un día que ya no está a la vista. Cuatro
BAJOS, arreglados:
- la decisión de pasar de mes con la primera lectura (el MEDIO de seguridad, abajo);
- dos mutaciones que no mordían: la espera sin su `break` (la prueba fija ahora las esperas) y el plazo justo el día que
  toca (casos nuevos en `test_el_plazo_frena_el_paso_de_mes`);
- el freno por el plazo, más angosto que su comentario (ahora, hasta fin del mes que se ve);
- documentación con «tres clics» y «32 calendarios».

**Seguridad (`security-reviewer`): sin CRÍTICO ni ALTO; un MEDIO, arreglado.**
- **MEDIO, una lectura a medio cargar:** el programa decidía pasar de mes con una sola lectura del calendario. Si el
  portal pintara los días antes de su disponibilidad (no medido), una lectura con todo deshabilitado lo llevaría al mes
  siguiente, y elegiría un día que no es el de la regla, sin NO ENVIADA. Lo reprodujo con las funciones del programa.
  Arreglo: dos lecturas quietas antes de pasar de mes y en el mes nuevo, o NO ENVIADA.
- BAJOS arreglados:
  - del mes nuevo, solo los días posteriores al último del anterior;
  - el botón de adentro, uno solo, a la vista y con su nombre;
  - «deshabilitado» también por la clase;
  - el plazo de entrega hasta fin del mes que se ve;
  - `siguientes` como número.
- Al RESIDUAL: `_texto_error` en los motivos nuevos, que es el mismo patrón de antes.
- Preguntó si pasar de mes cuando en el mes que se ve no queda un día habilitado es lo que quieres: va en «Lo que decides
  tú».
- Corrió la guarda de datos sobre su clon: 138 archivos, 0 hallazgos.

## 7. Las compuertas

En un clon de `.trabajo/e97` con el árbol del commit (`clon_compuerta.py`, que compara cada archivo con el del repo vivo
por su blob), con `compuerta.py`: la suite entera y el censo de las mutaciones que tocan lo cambiado o nombran una
prueba que cambió. La corrió el ayudante mecánico, con el envoltorio de salida literal.

**c1** (2026-11-04, de 12:01 a 12:56):
- **Suite: 1.122 pruebas, OK** (1 saltada, la de siempre), en 2.272 s. Originales sin cambios.
- **Censo:** 90 mutaciones (las 36 del encargo y 54 que tocan lo mismo o nombran una prueba que cambió), 149 pares.
  - **Los 149 muerden**, y el control sin mutar pasa.
  - El resultado es FALLA por 3 pares que la mutación dice vigilar y no hace caer:
    - **`e97-hacia-atras`** no tumba `test_falta_otro_mes` ni `test_cortes_al_pasar_de_mes`. Es una mutación
      equivalente: quitaba de `_mk_falta_otro_mes` la condición «el día que toca antes del primero a la vista». El día
      que toca siempre es hábil, y antes del primero a la vista es un día hábil sin su fecha, que la línea siguiente ya
      da por «no». Se quitó la mutación, y la condición quedó, porque dice la intención y no cambia lo que hace.
    - **`mk-retiro-cambia-de-mes`**, del encargo 36, no tumba `test_sin_el_dia_por_su_fecha_no_pulsa_el_dia`: este
      encargo le sacó a esa prueba el caso «el día que toca no está a la vista», porque ahora pasa de mes. El mismo
      camino lo recorre `test_cortes_al_pasar_de_mes` (el calendario abierto en un mes posterior), y la mutación vigila
      ahora esa prueba.

**c2** (solo el censo de `mk-retiro-cambia-de-mes`, con su prueba nueva, en un clon nuevo con el árbol final): los 2
pares muerden, el control pasa y ninguna prueba queda sin mutación.

Desde c1 cambiaron solo `tests/mutaciones.py` (esas dos entradas; ninguna prueba de la suite lo lee), el número de
pruebas de `CLAUDE.md` y este informe. `AQUASHIELD.py` y las pruebas son los de c1, blob por blob.

## Decisiones que tomé solo

| Decisión | Por qué |
|---|---|
| A lo más un mes adelante (`MK_MESES_ADELANTE` = 1), y nunca hacia atrás. | El día que toca cae, a lo más, en el mes que sigue al de hoy, y los 35 calendarios guardados abren en el mes de su corrida. Un segundo mes serviría solo si en todo el siguiente no hubiera un día habilitado, y entonces el plazo de entrega ya pasó. |
| También pasa de mes si en el que se ve no queda un día hábil habilitado desde el que toca. | Es la regla de siempre («si no está habilitado, el siguiente día hábil habilitado»); hasta ahora cortaba ahí solo porque cambiar de mes era un clic no permitido, y tu encargo lo permite. La pregunta va abajo. |
| Si el plazo de entrega de la tarjeta vence en el mes que se ve, no pasa de mes. | Ningún día del mes siguiente serviría: el contenedor se retira antes de entregarlo. Es un clic menos, y el motivo lo dice. |
| Dos lecturas quietas antes de pasar de mes y en el mes nuevo; si no, NO ENVIADA. | La revisión de seguridad lo pidió: una lectura a medio cargar no debe mover la fecha de retiro. El caso normal no cambia. |
| La sonda en el portal con «hoy» simulado el 30-11 y sin el plazo de la tarjeta, solo en la memoria del panel de prueba. | Era la única forma de pulsar «Next month» en el portal hoy. En modo prueba, y en un panel aparte, sin tocar los tuyos. |

## Lo que decides tú

- **¿Pasar de mes también cuando el día que toca está en el mes que se ve, pero desde él no queda un día hábil
  habilitado hasta fin de mes?** Hoy lo hace: busca el siguiente día hábil habilitado en el mes que sigue (por ejemplo, el
  25-11 con el 26 y el resto de noviembre deshabilitados: elige el 1-12). La otra opción es pasar de mes solo cuando el
  día que toca cae en el mes siguiente, y en ese caso dejar la fila NO ENVIADA, como antes. En las corridas guardadas no
  pasó: la ventana habilitada siempre estaba en el mes de la corrida.

## RESIDUAL

- **Elegir un día después de pasar de mes no está probado en el portal** (sección 4): se reabre con la primera fila de
  MAERSK a fin de mes, mirando en su `log.txt` «pulsado 'Next month'», la fecha elegida y «la tarjeta muestra».
- **El caso normal decide con la primera lectura del calendario**, como antes: si el portal pintara los días antes de su
  disponibilidad, podría tomar el siguiente día hábil habilitado en vez del que toca, dentro del mismo mes. No medido;
  las dos lecturas quietas se agregaron solo donde el cambio podía mover la fecha a otro mes. Se reabre si una corrida
  elige un día después del que toca con el que toca habilitado en su calendario guardado.
- **Los motivos nuevos llevan el texto de la excepción** (`_texto_error`), que solo junta los espacios, como el resto de
  MAERSK: un mensaje con un carácter de control llegaría a la planilla (revisión de seguridad, BAJO; otro encargo, para
  todo el programa).
- **La línea «Versión del programa» no ve los cambios sin commitear:** las corridas en el portal de este encargo dicen
  `main · d68e3f0` con el código nuevo en el árbol. Es lo de siempre (`VERSION_GIT` lee HEAD).

## Re-medir

- Las pruebas: `python -m unittest test_clics.TestRetiroMaersk test_evidencia.TestCadaReservadorLaDeja`, desde `tests`.
- Los calendarios guardados y el recorrido de fin de mes: `python .trabajo/e97/medir_calendarios.py --nuevo`, con el
  Python de la Tienda (el que tiene playwright).
- En el portal: `.trabajo/e97/vivo_lanzar.py [mes]` y `.trabajo/e97/vivo_correr.py <puerto> <planilla> CONSOLIDADO
  MAERSK <salida.json>`, con una planilla que tenga una fila de MAERSK.

## NO retroceder

- **Pasar de mes, solo con el único «Next month» habilitado de la raíz del calendario**, y después comprobar que el
  calendario muestre el día que sigue: un clic en otro control movería el calendario a cualquier parte.
- **Nunca hacia atrás, y a lo más un mes.**
- **Dos lecturas quietas antes de pasar de mes y en el mes nuevo**: una lectura a medio cargar podría mover la fecha de
  retiro a otro mes sin que la fila quede NO ENVIADA.
- **La tarjeta tiene que mostrar el día elegido** (`_mk_comprobar_retiro`), también después de pasar de mes.

## Defectos de instrumento que me cacé

- **La primera versión de `test_el_caso_normal_no_pasa_de_mes` buscó «Next month» en un `log.txt` que compartían varias
  pruebas de la clase** (todas nombraban «retiro_1» su carpeta). Desde este encargo, cada corrida de la clase tiene su
  carpeta.
- **En la prueba en Node, ocultar el `mc-button` no ocultaba su `button` de adentro**, y en el navegador sí: la prueba
  daba por visible un «Next month» oculto. Ahora el ayudante oculta los dos.
- **Mi primer «hueco» de prueba quitaba el último día del mes**, así que no quedaba en medio, y el programa pasaba de mes
  con razón. Ahora el hueco está en medio.
- **Un ancla de mutación vieja (`mk-retiro-no-espera-el-calendario`) quedó repetida** por la espera nueva, que tiene la
  misma forma; lo vio el contador de anclas antes del censo, y lleva ahora una línea más de contexto.
- **Escribí una mutación equivalente (`e97-hacia-atras`)**, sobre una condición que no cambia nada, y al cambiar una
  prueba vieja dejé a otra mutación vigilando un caso que ya no estaba (`mk-retiro-cambia-de-mes`). Los vio el censo
  (sección 7). Al sacar un caso de una prueba, mira qué mutaciones la nombran.

## Premisas del encargo que se refutaron

- **«Busca en logs\ el HTML del calendario de las corridas de MAERSK de fines de octubre que fallaron»:** no está. En
  este equipo no hay ninguna corrida de MAERSK del 29 al 31 de octubre, ni en `logs/` ni en `1. pruebas`. La falla que
  cuentas no se puede leer aquí; la prueba se hizo con los calendarios de octubre y de noviembre que sí están, que tienen
  la misma forma, y en el portal con una fecha simulada.
- El FRENA SI de ese punto pedía, además, que la prueba solo se pudiera hacer en el portal a fin de mes: no hizo falta.

## Reglas aplicadas

`metodo-ciclo` v40: la base en una línea; PASO 0 de un módulo que publica (lo publicado coincide con el registro:
`main` en `d68e3f0` y `estable` en `77d5801`); control positivo que aborta en la sonda de los calendarios; el negativo
tiene que morder (cada prueba nueva con su mutación, censadas); se mide sobre el camino real (el portal, en modo prueba,
y el JavaScript del programa sobre el HTML real); las dos revisiones, cada una en un clon; antes del commit, la suite
entera sobre el árbol del commit; el barrido de datos reales sobre lo que sube y sobre el mensaje del commit; nada fuera
de la carpeta del encargo; la limpieza dentro de la carpeta que borra. Del repo: el candado (nunca EMISIÓN; los paneles de
prueba abortan si está abierto), antes de la guarda no hay clics a ciegas, nunca el puerto 8765, las pruebas cargan una
copia del programa, cada prueba nueva con su mutación, y los datos reales solo en el chat. No chocaron.
