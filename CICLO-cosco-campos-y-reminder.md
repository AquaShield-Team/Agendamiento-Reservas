# CICLO · COSCO: los campos obligatorios y la ventana Reminder

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-24 · **Método:** skill `metodo-ciclo` v12 ·
**Base:** `215e38a` · **Commits:** solo el de este informe (local, sin push). **No se tocó el código.**

> Sin datos reales. Los logs, las capturas y las planillas se leyeron en su lugar y en solo lectura. De las
> planillas se leyeron los encabezados, no los valores (con una excepción, en los defectos de instrumento).
> Este informe describe formas y nombres de campos, nunca una reserva.

## Veredicto: FRENO

Se cumplen **dos** de los tres FRENA SI. Paré sin cambiar nada: ni el llenado de los campos ni el clic del
Reminder.

1. **Ningún dato obligatorio está en la planilla.** Ni el peso bruto, ni la temperatura, ni la ventilación
   tienen columna en ninguna hoja de las dos planillas reales, y ninguno se deriva de las columnas que hay.
   Hoy el peso y la temperatura salen de **constantes del código**, y la ventilación no se llena.
   **De dónde salen lo decides tú** (abajo, las opciones).
2. **La causa del Reminder no se puede determinar con la evidencia guardada.** Las 6 capturas muestran la
   ventana abierta bajo la máscara de carga de COSCO, pero no se sabe cuál de los «Submit» pulsó el
   programa, ni si el envío salió. Eso está en el HTML, y de esas corridas no hay HTML.
3. **Sin clics nuevos antes de la guarda: no aplica.** No hice ningún cambio.

**Aunque el Reminder se pudiera arreglar solo, no lo hice.** Un Reminder que avanza hace que los envíos
de COSCO lleguen a confirmación con el peso y la temperatura que hoy salen de constantes, justo el dato cuyo
origen queda por decidir.

**PASO 0: FRENO (PREGUNTA).**

## Los campos: qué pasó en los 8 envíos con errores

**La causa, medida: el programa llenaba antes de que cargara el formulario, en una versión anterior del
código.** Hoy ya no pasa.

| Corridas | Fecha | Espera de «Booking Details» en el log | Al llenar cantidad, peso y temperatura | Resultado |
|---|---|---|---|---|
| c6 y c2 | 21 y 22 de septiembre | No existía | «no encontré el campo» en los tres, en 8 de 8 reservas (y en el shipper en 4, en la descripción de la carga en 1) | Los 8 envíos, con errores de validación |
| c3 y c4 | 23 de septiembre | «Booking Details listo» en las 6 | «ok» en los tres, en las 6 | Pasó la validación y apareció el Reminder |

**Lo que muestran las capturas:**
- **En c2, la captura «detalles»,** tomada justo antes de llenar, muestra todavía los resultados de la
  búsqueda de naves, con la máscara de carga encima: el formulario Booking Details no existía. Los campos
  de más abajo (Remark y el correo) sí salen llenos en la captura siguiente, porque se llenaron después,
  con el formulario ya cargado.
- **En c4, la captura «4b_shipper»** muestra el contenedor con la cantidad, el tipo 40RQ Hi-Cube
  refrigerado y el peso en kilos, el shipper con calle, ciudad y país, la temperatura en Celsius y el
  generador «Not Required». Ningún mensaje en rojo.

**Qué intenta llenar el programa y con qué dato:**

| Campo | Cómo lo busca (en el marco del formulario) | Con qué dato | ¿Está en la planilla? |
|---|---|---|---|
| Quantity | Por placeholder («quantity»), si no por etiqueta, si no el primer campo que vale 0; teclea el valor | La columna de cantidad; si no hay, 1 | No hay columna: siempre 1 |
| Gross Weight | Por placeholder («gross weight»), si no por etiqueta, si no por JavaScript; lo reintenta antes de Submit si quedó vacío | `PESO_REEFER`, una constante del código, en kilos por contenedor | **No** |
| Temperature | Por placeholder («temperature»), si no por etiqueta | La columna de temperatura si la hay; si no, `TEMP_REEFER`, una constante del código | **No** |
| Ventilation | **No lo intenta** | Nada | **No** |

**El error de la ventilación.** El mensaje del portal es uno solo: «Temperature/Ventilation is required».
En los 6 envíos con la temperatura llena, el portal aceptó el formulario sin ventilación. Así que con la
temperatura basta; lo medido es el resultado, no una regla escrita del portal.

**De dónde podría salir cada dato** (lo decides tú):

| Dato | Hoy | Opciones |
|---|---|---|
| Peso bruto | La constante `PESO_REEFER` (la misma cifra fija usan ONE, MSC y HYUNDAI) | (a) Una columna nueva en la planilla, por ejemplo «Peso bruto (kg)». (b) Seguir con la constante: `CLAUDE.md` dice que se acordó con operaciones, pero no encontré dónde quedó escrito ese acuerdo |
| Temperatura | La constante `TEMP_REEFER`, salvo que la hoja traiga una columna de temperatura | (a) Una columna «Temperatura»: el lector del panel ya la lee si existe (`leer_filas`), y el de la consola no. (b) Seguir con la constante |
| Ventilación | No se llena | (a) No llenarla: el portal no la pidió cuando había temperatura. (b) Una columna nueva. (c) Un valor fijo, como hacen ONE («0») y HYUNDAI («0% CLOSED») |

## El Reminder: qué se ve y por qué no se sabe la causa

**Qué es la ventana.** Aparece después del Submit del formulario. **Solo informa**: «To complete your
booking request, please submit below document(s) before deadline», con dos íconos de documento:
- «Shipping Instruction/BL Master» y «Verified Gross Mass», los dos con «Submit before SI Cutoff».
- Los botones «Submit» y «Back».
- **No tiene casillas que marcar.**

**Qué pulsa el programa** (después de la guarda, en `_cosco_esperar_resultado`). Los tres caminos eligen
**el último «Submit» del documento**:
1. **Playwright, con clic forzado:** el último de `.el-dialog:has-text('Reminder') button:has-text('Submit')`,
   `[role=dialog]:has-text('Reminder') button:has-text('Submit')` y
   `div:has-text('To complete your booking request') button:has-text('Submit')`. El tercero toma **cualquier
   `div` que contenga ese texto**, y eso incluye los contenedores de toda la página: el «último Submit»
   puede ser el del formulario, y no el de la ventana.
2. **Playwright,** si no: el último de todos los botones «Submit».
3. **JavaScript,** en la segunda fase: el último botón visible que dice «submit».

**Qué pasó, reserva por reserva** (c4; la de c3 falló por el error del programa medido en
`CICLO-estado-tras-envio.md`):

| Reserva | Primera fase (hasta 15 s) | Segunda fase | Duración | Al final |
|---|---|---|---|---|
| 1, 3 y 5 | No vio la ventana | Volvió a pulsar el «último Submit» 37, 45 y 40 veces | 85 a 86 s | Ventana abierta bajo la máscara |
| 2 | La vio y pulsó por Playwright 1 vez | 45 veces | 87 s | Igual |
| 4 | La vio y pulsó por Playwright 4 veces (la ventana seguía) | 45 veces | 92 s | Igual |

**En las capturas del final:** toda la página, **incluida la ventana**, está bajo la máscara de carga de
COSCO (el barco), y el Submit del formulario tiene el ícono de carga.

**Por qué no se sabe la causa.** Con las capturas y el log caben dos explicaciones que piden arreglos
distintos:
- **(a)** Los clics caen en el Submit equivocado (el del formulario, en carga) o en la máscara, y el de la
  ventana nunca se pulsa. El arreglo sería elegir el botón dentro de la ventana.
- **(b)** El primer clic sí envió, y COSCO seguía procesando cuando el programa dejó de esperar. El arreglo
  sería esperar más, no pulsar más.

Para separarlas hace falta el HTML: dónde está la ventana (página o marco), qué botón es el último, dónde
vive la máscara. Desde `2c2ed4f`, cada envío guarda ese HTML de la página y de cada marco. También lo
resuelve el portal: si las 5 reservas de c4 existen, es (b).

## Qué mirar en la captura de tu prueba con el candado cerrado

Con el candado cerrado, COSCO llega hasta Booking Details y se detiene antes de Submit. Para confirmar que
los campos se llenan (como en c3 y c4, y no como en c2 y c6), mira en la carpeta de la corrida:

1. **`cosco_f<fila>_4b_shipper.png`**, la ventana que muestra Container Info, Party y Cargo Information:
   - **Quantity:** la cantidad de la fila (o 1).
   - **Size Type:** «40RQ - 40' Hi-Cube Refrigerated Container».
   - **Gross Weight (Per Container):** un número en «Kilograms». Hoy es la constante: **fíjate si es el que
     corresponde**; esa es la decisión pendiente.
   - **Shipper, Street, City y Chile:** llenos.
   - **Temperature:** el valor con «Celsius»; **Generator Set:** «Not Required».
   - **Ningún texto rojo «… is required»** en esa zona.
2. **`cosco_f<fila>_4_detalles.png`:** tiene que mostrar el formulario Booking Details. Si muestra los
   resultados de búsqueda con el barco cargando, se repitió lo de c2 y c6.
3. **En `log.txt`**, después de «Cargando Booking Details»:
   - Tiene que decir **«Booking Details listo (…s)»**, y no «tardó en responder».
   - Tiene que decir **«Quantity='…': ok», «Gross Weight='…': ok» y «Temperature='…': ok»**, y ningún «no
     encontré el campo».
   - **No te fíes del «✗ Size Type: VACÍO» del CONTROL:** ese control lee mal ese campo (sale vacío en las 14
     reservas, también en las 6 donde la captura lo muestra lleno).

## Premisas del encargo contrastadas (pieza 5)

- **«8 quedaron con errores de validación»:** confirmada. Pero son las dos corridas más viejas, del 21 y el
  22, de antes de que existiera la espera de Booking Details. En las 6 del 23 los campos quedaron llenos.
  **El problema de llenado de esos 8 ya no está en el código de hoy;** lo que queda abierto es de dónde
  salen los datos.
- **«En al menos uno, Ventilation»:** el mensaje es «Temperature/Ventilation is required», uno solo. Con la
  temperatura llena, el portal no pidió ventilación.
- **«Pulsó su Submit durante unos 70 segundos»:** entre 85 y 92 s por reserva, con 37 a 45 clics por
  JavaScript y hasta 4 por Playwright.
- **«Con qué dato de la planilla»:** con ninguno. Los tres datos vienen de constantes o no se llenan.

## Universo y cobertura (pieza 3)

- **Corridas de COSCO:** 4 de 4 (c2, c3, c4 y c6), 14 reservas. Leí el log de cada una, desde «Paso 2»
  hasta el resultado.
- **Capturas:** las agrupé por huella y miré:
  - las de «detalles» y «carga» de la fila 5 de c2;
  - la «4b_shipper» de la fila 5 de c4;
  - la «confirmado» de la fila 6 de c4, con un recorte temporal de la ventana, borrado después.
  - Las 11 «confirmado» distintas ya las había mirado enteras en `CICLO-numero-booking.md`.
- **Planillas:** las 2 reales (la de la carpeta del programa y la copia que sube el panel). Las 7 hojas de
  cada una tienen las mismas 9 columnas.
- **Código:** `reservar_cosco` antes de la guarda (el llenado), `_cosco_fill_id`, `_cosco_fill_etq` y
  `_cosco_esperar_resultado` (el Reminder).
- **La red no cambió:** 185 pruebas, 345 mutaciones, 397 pares (censo de `2c2ed4f`; este commit solo
  agrega documentos).

## Re-medir (pieza 1)

```powershell
python tests\sonda_secretos.py --dry-run
```

- **La causa de los campos:** en `logs/`, contar por corrida de COSCO las líneas «Booking Details listo»,
  «Cargando Booking Details» y «no encontré el campo».
- **El Reminder:** en el log de c4, las líneas desde «MODO EMISIÓN REAL» hasta «Reserva i:»; en las
  capturas «confirmado», la ventana bajo la máscara.
- **Las columnas:** leer solo la fila de encabezados de cada hoja con `_mapear`, no «la fila más larga»
  (ver el defecto 1).

## NO retroceder (pieza 2)

- **No quites la espera de Booking Details** (la de «Booking Details listo»): sin ella se repite lo de c2 y
  c6. **No tiene guardián en la red** (va al residual).
- **No inventes un valor por defecto** para un dato obligatorio que la planilla no trae.
- **No arregles el Reminder pulsando más ni más fuerte** sin el HTML: si la causa es (b), cada clic de más
  vuelve a pulsar sobre un envío en curso.

## Defectos de instrumento cazados (pieza 4)

1. **Una fila de datos reales en mi sesión.** Para buscar los encabezados tomé «la fila con más celdas» de
   las primeras 14. En la hoja COSCO de la planilla de la carpeta, esa fila era de datos, e imprimí en la
   sesión los valores de una reserva real. No quedó en ningún archivo. Lo correcto es `_mapear`, que elige
   por encabezados reconocidos.
2. **Una coincidencia falsa en la búsqueda de columnas.** El «°» de «N° de reserva emitida» calzó con mi
   patrón de temperatura. La cacé al leer los nombres.
3. **El control del propio programa lee mal un campo.** `_cosco_control` informa «Size Type: VACÍO» en las
   14 reservas, y la captura lo muestra lleno. Cualquier diagnóstico que se apoye en ese control se
   equivoca en ese campo.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| De dónde salen el peso bruto, la temperatura y la ventilación | FRENO: no están en la planilla | …decides la fuente (columna nueva, constante o nada) |
| El Reminder no avanza | FRENO: la causa no se ve sin el HTML | …una corrida con emisión deja su HTML (desde `2c2ed4f`), o el portal dice si las 5 de c4 existen |
| La espera de Booking Details no tiene guardián en la red | Es flujo antes de la guarda y en el portal; offline no corre | …se toca el llenado de COSCO |
| `_cosco_control` lee mal «Size Type» | Afecta solo al aviso del log | …se toca el control |
| Las 5 reservas de c4 y la de c3 | Nadie sabe si se crearon | …se revisan en el portal (`CICLO-numero-booking.md`) |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v12**:
- **PASO 0 con veredicto de cuatro valores:** FRENO (PREGUNTA).
- **Todo registro es una hipótesis:**
  - «Constantes acordadas con operaciones» (`CLAUDE.md`) no tiene respaldo escrito que encontrara.
  - El control del programa miente en un campo.
- **Re-medir contra HEAD:** el código de hoy ya espera el formulario; el defecto del encargo venía de una
  versión anterior.
- **La unidad la fija el sujeto:** la reserva, con su log y sus capturas, no la corrida.
- **FRENAR cuando la decisión es de negocio:** la fuente de los datos.
- **Se declaran el residual y las premisas.**
- **El push se entrega, no se hace:** no hay remoto.

Reglas propias del módulo (`CLAUDE.md`): casos sintéticos, la sonda antes del commit y los logs en solo
lectura.

**Choques:** ninguno. El freno cae antes de cualquier cambio.

## Entregable (pieza 8)

Este `.md`, sin renderizar, y `CLAUDE.md` con una línea sobre los datos que la planilla no trae. Pasan la
sonda de staging antes de su commit.
