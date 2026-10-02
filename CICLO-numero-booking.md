# CICLO · El número de booking real después de emitir

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-23 · **Método:** skill `metodo-ciclo` v12 ·
**Base:** `4fac99f` · **Commits:** `08dd388` (ONE), `1968ac2` (MSC) y el de este informe (locales, sin
push).

> Sin datos reales. Las capturas de `logs/` se miraron en su lugar y en solo lectura. Este informe describe
> **la forma** del número («4 letras fijas + 8 dígitos»), nunca un número. Los casos de prueba usan números
> inventados con esa forma. Ninguna captura, HTML ni booking real entra al repo.

## Veredicto

- **ONE y MSC, arreglados.** Las dos muestran el número en la pantalla de confirmación, junto a su etiqueta y
  sin otro código cerca. Ahora el programa acepta **solo esa forma**. Si no la encuentra, deja la reserva en
  EMITIDA con el aviso de buscar el número en el portal, en el log y en el texto que va a la planilla.
- **CMA y COSCO: FRENO.** En **ninguna** captura posterior al envío aparece un número. Tampoco una pantalla
  de confirmación. Paré con las dos. Qué muestran en su lugar está abajo, y **cambia lo que se creía de esas
  reservas.**
- **El tratamiento del ERROR de COSCO tras Submit** (posible emisión, no error simple) **no se hizo**: cae
  bajo el freno de COSCO.
- **Los otros dos FRENA SI no se cumplieron:**
  - En ONE y MSC el número ya está en la pantalla que se captura: no hace falta ningún clic ni navegación.
  - Su forma (etiqueta + prefijo + 8 dígitos) no se confunde con ningún otro código de esa pantalla.
- **PASO 0: CICLO**, con freno en 2 de las 4 navieras.

## Lo medido: dónde muestra cada naviera el número tras el envío

**Fuentes:**
- **Las capturas:** «confirmado» de cada reserva y «final» de cada corrida.
- **Los logs:** las líneas desde el clic de envío hasta el resultado.
- **HTML guardado:** 0 en `logs/` y 0 volcados de portal en la raíz, así que las capturas son la única vista
  de la pantalla.
- **Capturas duplicadas:** las agrupé por huella y miré cada una distinta.

| Naviera | Reservas EMITIDA en los logs | Capturas tras el envío (distintas / miradas) | Qué muestra la pantalla | Qué tomó el extractor |
|---|---|---|---|---|
| **ONE** | 5 (c6) | 5 / 5 | «Your booking has been successfully submitted!», etiqueta **«Booking Reference No.»** y debajo **«SCLG» + 8 dígitos**. No hay otro código en esa pantalla | Nada: «en proceso» |
| **MSC** | 5 (c5) | 5 / 5 | Ventana «Your eBooking request has been successfully created and submitted for agency confirmation», etiqueta **«Your eBooking number is :»** y debajo **«EBKG» + 8 dígitos**. Aclara que queda «pending MSC agency confirmation» | Nada: «en proceso» |
| **CMA** | 5 (c1) | 2 / 2 (5 capturas) | **La misma página de revisión de la reserva** (partes, pago, servicios), con «Reefer: TO COMPLETE» y «Configuración de liberación de vacío: NOT FILLED». No hay confirmación. La captura final es el tablero de cliente, con envíos anteriores | Nada: «Ver captura» |
| **COSCO** | 13 (c2: 3, c4: 5, c6: 5) + 1 ERROR tras Submit (c3) | 11 / 11 (14 capturas) | Dos pantallas, ninguna de confirmación. **(a)** El formulario **con errores de validación** («Please input at least 1 container», «Gross Weight is required», «Temperature/Ventilation is required», «Shipper/City/Country is required»): en c2 y c6, 8 reservas. **(b)** La ventana **«Reminder»** («To complete your booking request, please submit below document(s) before deadline»: Shipping Instruction y VGM) **todavía abierta**, con el portal cargando: en c3 y c4, 6 reservas. En c4 el programa pulsó el Submit de esa ventana durante unos 70 s, sin que apareciera la confirmación | c2 «Templates» (la etiqueta «Booking Template» del formulario); c6 «COPYRIGHT» (el pie de página); c4 nada |

**Por qué el extractor no vio el número de ONE y MSC,** aunque sus patrones calzaban con el texto: en los
dos, la captura y la lectura ocurren en el mismo segundo y la pantalla ya muestra el número. Luego el texto
no estaba en `document.body.innerText` de la página principal. Sin HTML guardado no se puede saber si estaba
en un marco, en una raíz shadow o si la lectura falló. El arreglo cubre las tres causas: lee la página, cada
marco y las raíces shadow, y reintenta.

## FRENO: CMA y COSCO

**CMA.** El número no aparece en ninguna de las 5 capturas tras el envío. En su lugar está la página de
revisión, igual que antes de enviar. El programa solo pulsa «Enviar el booking» **si el botón está visible**
y devuelve EMITIDA en cualquier caso, así que estas 5 capturas **no prueban que el envío haya ocurrido**.

**COSCO.** El número no aparece en ninguna de las 14 capturas.
- En 8, el formulario seguía con errores de validación: **el envío no pasó**. El extractor tomó una palabra
  de la página, y por eso quedaron EMITIDA con «Templates» o «COPYRIGHT».
- En 6, la ventana «Reminder» seguía abierta. COSCO pide confirmar ahí que el Shipping Instruction y el VGM
  se entregarán antes del corte. No se ve ninguna confirmación posterior.

**Qué cambia esto del ciclo anterior** (`CICLO-emitidas-sin-marcar.md`). Esas 14 filas sospechosas eran
todas de COSCO (las 5 de CONSOLIDADO 20 a 24 y las filas 5 a 9 de la hoja COSCO). Ahora las capturas indican
que **varias de esas «EMITIDA» probablemente no se enviaron**: en c2 y c6 el formulario tenía errores. Las de
c3 y c4 quedaron en la ventana Reminder, **sin confirmar**. El portal sigue siendo lo único que lo decide.

**Lo que decides tú:** si el número de CMA y COSCO se busca en otra pantalla del portal (el tablero o la
lista de reservas) y cómo se confirma el envío en cada una. Mi recomendación, antes de volver a emitir en
esas dos navieras:
- **Que el programa exija ver la pantalla de confirmación para dar la reserva por EMITIDA.** Hoy devuelve
  EMITIDA sin verla.
- **Que se revisen en el portal las reservas de c1, c2, c3, c4 y c6,** para saber cuáles existen.

## Los cambios (ONE y MSC)

| Pieza | Qué hace |
|---|---|
| `FORMA_BOOKING` | La forma medida de cada naviera. ONE: etiqueta «Booking Reference No.» + `SCLG` + 8 dígitos. MSC: «Your eBooking number is :» + `EBKG` + 8 dígitos. La etiqueta ignora mayúsculas; el número, no. Hay un límite de palabra después de los 8 dígitos |
| `numero_tras_envio` | Lee el texto visible de la página, **de cada marco** y **de las raíces shadow** abiertas, y reintenta **cada segundo hasta 15 s** (`BKG_ESPERA_SEG`). Solo lee: ni clics ni navegación. Un marco que no se deja leer no tapa a los demás |
| `_emitida` | Si hay número: `EMITIDA` y «<naviera> emitida con éxito (Booking: <número>)». Si no: `EMITIDA` y «<naviera>: se pulsó el envío, pero la pantalla de confirmación no mostró el número. Búscalo en el portal y anótalo en la planilla.», en el log con «⚠». Ese texto llega a la planilla por el mismo camino de siempre: la consola lo escribe en el reporte y la descarga del panel, en Estado. **Nunca** «en proceso» ni «Consultar portal» |
| `extraer_numero_booking` | Para ONE y MSC, solo la forma medida. Ya no caen a los patrones de otras navieras, y una «sclg» o «ebkg» en el texto ya no mete a otra naviera en su rama |
| `reservar_one` / `reservar_msc` | Después de su guarda devuelven `_emitida(...)`. **Lo que se pulsa antes de la guarda no cambió**: la red lo fotografía |

## Pruebas que cambiaron su expectativa

Cada una fotografiaba el defecto que se arregla en su commit:

| Prueba | Antes | Después |
|---|---|---|
| `test_booking.TestExtraerNumero.test_one` (`08dd388`) | Aceptaba «ABC1234567» tras «Booking Reference No.» y una «SCLG» + 8 dígitos sin etiqueta | Las dos dan `""`. Se agrega el caso con la forma medida, que da el número |
| `test_booking.TestExtraerNumero.test_msc` (`1968ac2`) | Aceptaba «EBKG» + 7 dígitos, «Booking reference: MSCFALSO123» y una «EBKG» suelta | Los tres dan `""`. Se agrega el caso con la forma medida, que da el número |

**Una prueba cambió de entrada, no de expectativa:**
- `test_booking.TestExtraerNumero.test_pagina_que_falla_devuelve_vacio` (`08dd388`): usaba «one» y ahora usa
  «cma». Con «one» ya no pasaba por las dos capas que su mutación apaga, así que la mutación habría quedado
  vacía. La expectativa sigue siendo `""`.

**Pruebas nuevas (12):**
- ONE (`08dd388`):
  - `test_una_sclg_ya_no_mete_a_otra_naviera_en_one`
  - `test_forma_medida_de_one`
  - `test_lee_los_marcos`
  - `test_un_marco_que_falla_no_tapa_a_los_demas`
  - `test_reintenta_hasta_que_aparece`
  - `test_sin_numero_espera_lo_justo`
  - `test_naviera_sin_forma_medida_no_lee`
  - `test_emitida_con_numero`
  - `test_emitida_sin_numero_avisa_sin_relleno`
  - `test_reservadores_usan_la_forma_medida`
- MSC (`1968ac2`):
  - `test_una_ebkg_ya_no_mete_a_otra_naviera_en_msc`
  - `test_forma_medida_de_msc`
  - además, `test_reservadores_usan_la_forma_medida` suma a MSC.

**Mutaciones:**
- **26 nuevas:** 18 de ONE y 8 de MSC.
  - Cada rasgo de la forma: etiqueta, prefijo, dígitos, límite de palabra y mayúsculas.
  - La lectura: los marcos, los reintentos, la espera, el marco que falla y el JavaScript shadow.
  - La vuelta de la «sclg» y la «ebkg» que metían a otras navieras.
  - El relleno y el aviso.
  - Cada reservador volviendo al extractor viejo.
- **2 retiradas,** porque sus patrones ya no existen: `booking-one-sin-sclg` y `booking-msc-sin-ebkg`.
- **1 ajustada al nuevo final del extractor:** `booking-pagina-que-falla-revienta`.

## Universo y cobertura (pieza 3)

- **Corridas:** las 6 de `logs/`. Todas son del panel web.
- **Reservas EMITIDA:** 38. De ellas, 28 son de CMA, COSCO, ONE y MSC, y 10 de HYUNDAI y MAERSK (fuera del
  encargo: ya traían número). Más 1 ERROR tras Submit de COSCO.
- **Capturas tras el envío:** 29 de las cuatro navieras (5 CMA, 14 COSCO, 5 ONE, 5 MSC), con 23 distintas por
  huella. Miré **16 enteras**: las 2 de CMA, las 11 de COSCO, 1 de ONE y 2 de MSC, más las «final» de CMA y
  COSCO y la de error de c3. Las **7 restantes** (4 de ONE y 3 de MSC) las miré en el recorte de su
  ventana de confirmación, que es donde está el número.
- **Para medir la forma de los números** hice dos imágenes temporales en el scratchpad (fuera del repo), con
  recortes de las ventanas de confirmación, y las borré al terminar de leerlas. Ningún número real se copió
  a otro archivo.
- **La red:**

| Commit | Pruebas | Mutaciones | Pares mutación-prueba | Sin mutación | Motivos vacíos |
|---|---|---|---|---|---|
| base `4fac99f` | 133 | 210 | 245 | 0 | 0 |
| `08dd388` (ONE) | 143 | 227 | 264 | 0 | 0 |
| `1968ac2` (MSC) | 145 | 234 | 273 | 0 | 0 |

Cada commit pasó la suite completa, el censo completo y la sonda de secretos en 0 sobre el staging, y los
originales no cambiaron en ninguna corrida. Las pruebas no contienen ningún número real: lo comprobé
buscando la forma de los números medidos.

## Re-medir (pieza 1)

```powershell
python tests\correr.py --todo
python tests\sonda_secretos.py --dry-run
cd tests; python -m unittest test_booking
```

- **Para la medición:** agrupar por huella SHA-256 las capturas `*_confirmado.png` de cada carpeta de
  `logs/` y mirar una de cada grupo, junto con la `*_final.png` y las `error_*.png`.
- **En el log de cada reserva:** las líneas desde «MODO EMISIÓN» o «EMISIÓN:» hasta «Reserva i:».

## NO retroceder (pieza 2)

- **No vuelvas a aceptar en ONE ni en MSC un código que no tenga la forma medida:** la etiqueta, el prefijo y
  8 dígitos.
- **No vuelvas a leer solo `document.body.innerText`** para el número: así se perdieron los 10 números que sí
  estaban en pantalla.
- **No vuelvas a escribir «en proceso» ni «Consultar portal»** cuando no hay número: el aviso dice qué hacer.
- **No des por EMITIDA una reserva de CMA o COSCO por lo que diga su log:** sus capturas no muestran ningún
  envío confirmado.

## Defectos de instrumento cazados (pieza 4)

1. **Leí solo el primer motivo de un censo en FALLA.** El primer censo de ONE falló por dos cosas: una
   prueba sin mutación y una mutación cuyo texto ya no existía. Arreglé la primera, volví a correr y recién
   ahí vi la segunda. Desde entonces leo todas las líneas `ERROR:` antes de corregir.
2. **Un negativo que se habría vuelto vacío.** Al mandar «one» por `numero_tras_envio`, la prueba de la
   página que falla ya no pasaba por las capas que su mutación apaga. La cambié a «cma».
3. **Un caso incompleto (lectura b del negativo vacío).** `msc-forma-sin-etiqueta` no mordía a `test_msc`,
   porque la prueba no tenía una «EBKG» con 8 dígitos sin etiqueta. Agregué ese caso.
4. **Una aserción demasiado débil, corregida antes de correr.** Buscar la palabra «shadowRoot» en el
   JavaScript no habría caído con la mutación que apaga esa rama. Ahora se fija la condición exacta.
5. **Dos imágenes temporales con recortes de capturas reales en el scratchpad.** Las necesité para contar los
   dígitos y las borré en cuanto las leí. La primera salió vacía por coordenadas mal escaladas y la rehíce.

## Premisas del encargo contrastadas (pieza 5)

- **«Las 28 de CMA, COSCO, ONE y MSC quedaron con en proceso o con una palabra de la página»:** confirmada.
  Pero **no es solo un problema del extractor.** En ONE y MSC el número estaba en pantalla y el extractor no
  lo leyó. En CMA y COSCO **no hubo pantalla de confirmación**.
- **«En COSCO hubo un ERROR justo después de pulsar Submit que pudo haber emitido»:** la captura de ese caso
  (c3) muestra la ventana Reminder abierta, no una confirmación. Sigue sin saberse si emitió.
- **«Ya fotografiado: _extraer_bkg_limpio acepta Templates, y un 27 mete a cualquier naviera en MAERSK»:**
  sigue igual. Las dos tocan a CMA y COSCO (frenadas) y no a ONE ni a MSC, que ya no pasan por esos
  patrones: van al residual.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| El número de CMA y COSCO | FRENO: no aparece en ninguna captura tras el envío | …decides en qué pantalla buscarlo |
| El ERROR de COSCO tras Submit como posible emisión | Cae bajo el freno de COSCO | …se reabre COSCO |
| CMA y COSCO devuelven EMITIDA sin haber visto una confirmación | No es el número: es el estado; fuera del encargo | …se decide exigir la confirmación |
| `_extraer_bkg_limpio` acepta «Templates», y un «27» mete a CMA o COSCO en la rama de MAERSK | Solo afecta a navieras frenadas | …se reabre CMA o COSCO |
| La causa exacta de que `innerText` no viera el número (marco, raíz shadow o lectura fallida) | Sin HTML guardado no se ve offline | …una corrida real de ONE o MSC vuelve a quedar sin número pese a la lectura nueva |
| El JavaScript que lee las raíces shadow no corre en la red | La red es offline y la página es falsa: se fija la forma del JavaScript, no su efecto | …se prueba contra un navegador |
| La forma medida sale de 5 capturas por naviera | Si el portal cambia la forma, el número no se toma y el aviso pide buscarlo (no se toma uno malo) | …aparece el aviso en una corrida real con confirmación en pantalla |
| Los números de las 10 reservas de ONE y MSC de `logs/` | Están en sus capturas, pero no se copiaron a ningún archivo | …los quieres en la planilla: están en `one_f5…9_11_confirmado.png` y `msc_f5…9_6_confirmado.png` |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v12**:
- **PASO 0 y re-medir:** cada captura distinta, por huella.
- **Todo registro es una hipótesis:** «EMITIDA» en el log no probaba el envío.
- **La unidad la fija el sujeto:** la pantalla tras el envío, no la línea del log.
- **FRENAR cuando la decisión es de negocio:** CMA y COSCO.
- **El negativo tiene que morder, de a uno por llamada.**
- **El cambio y su guardián, en el mismo commit.**
- **Lo inocuo y lo peligroso conviven en la misma familia:** la etiqueta separa el número de otros códigos.
- **Se declaran el residual y las premisas.**
- **El push se entrega, no se hace:** no hay remoto, así que no hay nada que entregar.

Reglas propias del módulo (`CLAUDE.md`): sandbox, las fotos se actualizan en el mismo cambio, casos
sintéticos y la sonda antes de cada commit. **Choques:** «un commit por naviera» contra el freno de dos
navieras. Lo resolví con commits solo para ONE y MSC.

## Entregable (pieza 8)

Este `.md`, sin renderizar, y `CLAUDE.md` al día. Pasan la sonda de staging antes de su commit.
