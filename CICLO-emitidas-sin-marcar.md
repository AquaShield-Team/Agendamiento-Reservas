# CICLO · Reservas que salieron según los logs pero la planilla no marca como emitidas

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-23 · **Método:** skill `metodo-ciclo` v12 ·
**Base:** `0d895a3` · **Commit:** el de este informe (local, sin push). **No se modificó código, ni planillas
ni logs**: el cruce leyó los archivos como bytes en memoria y, al terminar, los 8 archivos (2 planillas y 6
logs) tenían la misma huella.

> Sin datos reales. Este informe da hoja, número de fila, confianza y conteos. Las corridas van como c1…c6.
> Los números de booking, las naves, los destinos, las fechas y el operador están solo en el detalle local
> (abajo), que queda fuera de git.

## Veredicto

- **14 cruces sospechosos en 10 filas, todos en la copia de la planilla que se subió al panel.** En la
  planilla de la raíz, **0**: sus 39 filas cruzadas dicen EMITIDA.
- **Ninguna sospechosa tiene un número de booking válido en el log:**
  - 13 son **EMITIDA sin número válido**: el log dice EMITIDA, pero trae «en proceso» o una palabra de la
    página que el extractor de entonces tomó por número.
  - 1 es un **ERROR tras pulsar Submit** (COSCO), que pudo haber emitido.
  - Con el criterio literal del encargo (EMITIDA **con** número), hay 10 reservas: HYUNDAI y MAERSK, filas
    25 a 34 de CONSOLIDADO. Tienen **0 sospechosas**: en las dos planillas dicen EMITIDA y su N° es el mismo
    del log.
- **Confirmar las 14 exige el portal.** Solo ahí se ve si esas reservas existen, y cuántas veces. Yo no
  entré a ningún portal. El detalle para que las revises está en `revision_local/`, fuera de git.
- **Los dos FRENA SI no se cumplieron, y dejo mi lectura del primero:**
  - Marcar una fila como sospechosa no necesitó el portal: sale de cruzar el log con la planilla. Lo que exige
    el portal es confirmar la sospecha, que es tu paso. Si querías que eso frenara el ciclo, el informe es lo
    único que se commiteó y el detalle ya está en tu disco.
  - El archivo de detalle queda fuera de lo versionado: `git check-ignore` lo atribuye a `/*` (línea 6 del
    `.gitignore`), y `git status` no muestra nada nuevo.
- **Hay además posibles reservas repetidas en COSCO,** que conviene mirar en el mismo viaje al portal (más
  abajo).

## Las filas sospechosas

| Planilla | Hoja | Fila | Corridas que la dan por salida (clase en el log) | Confianza | Qué dice su estado |
|---|---|---|---|---|---|
| subida al panel | COSCO | 5 | c2 (EMITIDA sin número válido), c3 (**ERROR tras Submit**), c4 (EMITIDA sin número válido) | número y contenido | formato de consola: OK-EJEMPLO · SIN EMITIR |
| subida al panel | COSCO | 6 | c2, c4 (EMITIDA sin número válido) | número y contenido | formato de consola: OK-EJEMPLO · SIN EMITIR |
| subida al panel | COSCO | 7 | c2, c4 (EMITIDA sin número válido) | número y contenido | formato de consola: OK-EJEMPLO · SIN EMITIR |
| subida al panel | COSCO | 8 | c4 (EMITIDA sin número válido) | número y contenido | formato de consola: OK-EJEMPLO · SIN EMITIR |
| subida al panel | COSCO | 9 | c4 (EMITIDA sin número válido) | número y contenido | formato de consola: OK-EJEMPLO · SIN EMITIR |
| subida al panel | CONSOLIDADO | 20 a 24 | c6 (EMITIDA sin número válido) | número y contenido | un texto manual de una palabra, sin «EMITIDA» |

Son 10 filas y 14 cruces, porque las filas 5 a 7 de COSCO aparecen en más de una corrida. **Ninguna** tiene
el estado vacío ni en la P.

**Qué significa el texto de las filas 5 a 9 de COSCO.** Tiene el formato que escribe la **consola**
(«SOLICITUD i · OK-EJEMPLO · … · SIN EMITIR»): una corrida en modo seguro dejó esas filas como «armadas sin
emitir». Pero en `logs/` no hay **ninguna** corrida de consola, así que esa corrida no dejó log aquí y no se
puede saber si fue antes o después de las corridas del panel que las dan por salidas. **No es** el defecto de
«SIN EMITIR con EMITIDA» corregido en `8feabdb`: el estado dice OK-EJEMPLO, no EMITIDA.

## Posibles reservas repetidas (para mirar en el portal)

- **COSCO, filas 5, 6 y 7 de la hoja COSCO:** EMITIDA en **dos** corridas (c2 y c4). La fila 5 tiene además
  un ERROR tras Submit en c3. Esa fila pudo generar hasta 3 envíos.
- **CONSOLIDADO, filas 20 a 24 (COSCO, c6):** tienen el mismo contenido que las filas 5 a 9 de la hoja COSCO.
  Pueden ser las mismas cinco reservas enviadas otra vez, o reservas distintas iguales; offline no se
  distingue, porque el contenido se repite entre reservas (ciclo anterior: 30 reservas con 7 contenidos
  distintos).

## Conteos

| | Planilla de la raíz | Copia subida al panel |
|---|---|---|
| Cruces (reservas del universo × planilla) | 39 | 39 |
| **Sospechosas** | **0** | **14** (13 EMITIDA sin número válido, 1 ERROR tras Submit) |
| Confianza: número y contenido | 32 | 39 |
| Confianza: solo número | 7 (difiere la **nave**: CONSOLIDADO 5, 6 y 30 a 34) | 0 |
| Confianza: no calza | 0 | 0 |
| Estado: dice EMITIDA | 39 | 25 |
| Estado: SIN EMITIR (consola, OK-EJEMPLO) | 0 | 9 |
| Estado: otro texto (manual) | 0 | 5 |
| Estado vacío | 0 | 0 |
| Columnas M y P | vacías en las 39 | vacías en las 39 |
| N° de la fila frente al log (las 10 con número) | 10 iguales | 10 iguales |

Las 7 filas de la raíz con «solo número» dicen EMITIDA y tienen el mismo N° que el log: no son sospechosas,
pero **su nave cambió después de la corrida**. Si se revisa una, conviene mirar esa diferencia.

## Universo y cobertura (pieza 3)

- **Corridas:** las 6 carpetas de `logs/`, todas del panel web (`web_*`); **0 de consola**.
- **Reservas en los logs:** 46 secciones de reserva, y cada una tiene su línea de resultado. **Control:** el
  parser encontró 46 y un conteo independiente de las líneas de resultado dio 46. Quedaron 0 sin fila y 0 sin
  resultado; si no calzaba, el script abortaba.

| Clase en el log | Reservas | En el universo |
|---|---|---|
| EMITIDA con número válido | 10 | sí (el criterio literal del encargo) |
| EMITIDA sin número válido («en proceso», «Ver captura» o una palabra de la página) | 28 | sí (ver abajo) |
| ERROR tras Submit | 1 | sí |
| REVISAR (antes de la guarda) | 6 | no: no hubo envío |
| DETENIDO por el operador (antes de la guarda) | 1 | no: no hubo envío |

- **Por qué incluí las 28 sin número.** El encargo pedía las EMITIDA **con** número, pero la TAREA es
  encontrar las reservas que **según los logs salieron**, y estas el log las da como emitidas. Van separadas
  en todos los conteos. Con el criterio literal, el resultado es **0 sospechosas**.
- **Qué es «número válido»:** de 8 a 18 letras o dígitos, con al menos un dígito. Así quedan fuera «en
  proceso», «Ver captura», «Consultar portal» y las palabras sueltas de la página.
- **Las planillas:** la de la raíz y la copia que el panel guardó en `%TEMP%` al subirla. Esa copia es **solo
  la última subida**: las anteriores se sobrescribieron, así que no se sabe con qué archivo corrió cada
  corrida. **No se buscaron** planillas fuera del proyecto.
- **Las columnas de estado:**
  - Leí la M (13), la P (16) y toda columna cuyo encabezado diga «estado»; en las dos planillas es la H.
  - Leí además la columna «N° de reserva emitida», para ver si contradice al log. Esa columna la agregué yo;
    el encargo no la pedía.
- **Cuándo una fila es sospechosa:**
  - Si el log dice EMITIDA, la fila es sospechosa cuando su estado no dice EMITIDA (dice SIN EMITIR, está
    vacío o dice otra cosa) o cuando su N° es distinto del número del log.
  - Si el log dice ERROR tras Submit, la fila es sospechosa cuando su estado la da por no enviada (SIN
    EMITIR, OK-EJEMPLO, REVISAR, DETENIDO, vacío u otro texto).
- **Confianza:**
  - «Número y contenido» significa que la fila es una reserva y que el origen, el destino y la nave que
    anotó el log coinciden con la fila de hoy.
  - «Solo número» significa que la fila es una reserva pero algún campo cambió.
  - «No calza» significa que la hoja no está o que esa fila no es una reserva.
  - El destino se compara contra el final, el original o la forma «original / final», que es como lo anota
    CMA.

## Re-medir (pieza 1)

```powershell
python revision_local\cruce_emitidas.py revision_local\emitidas_segun_logs_2026-09-23.md
```

- **Qué hace el script:** vive en la misma carpeta local que el detalle, fuera de git, y no contiene datos.
  Lee los logs y las dos planillas a memoria con `leer_filas` de una copia del programa en sandbox. Imprime
  solo estructura, reescribe el detalle y verifica al final, por huella, que ningún archivo cambió.
- **Si faltan esos archivos,** el informe describe cada regla (universo, clases, número válido, confianza y
  sospecha) para rehacerlo.

## NO retroceder (pieza 2)

- **No vuelvas a correr en modo emisión las filas 5 a 9 de COSCO ni las 20 a 24 de CONSOLIDADO sin revisar
  antes el portal:** ya hay hasta dos envíos por fila, más un ERROR tras Submit.
- **No tomes «EMITIDA» del log como prueba de que hay número:** en 28 de 38 EMITIDA no lo hay. Hoy el
  extractor ya descarta «Templates» y «COPYRIGHT», pero estas corridas son anteriores.
- **No compares el destino de CMA contra una sola columna:** CMA anota «original / final».

## Defectos de instrumento cazados (pieza 4)

1. **La comparación de destino era demasiado estricta:** no conocía la forma «original / final» de CMA. Las
   10 filas de la hoja CMA-CGM (5 por planilla) salían como «solo número» cuando sí calzan. Lo detecté al
   pedir **qué campo** difería. La corrección sale de leer `reservar_cma`.
2. **Al renombrar la clase «SIN EMITIR»,** la regla del ERROR tras Submit dejó de reconocerla y las
   sospechosas bajaron de 14 a 13. Lo detecté comparando con la corrida anterior del script y lo corregí
   (`startswith`).
3. **En el detalle, el número crudo de las EMITIDA de COSCO salía «nada»** porque la palabra estaba en otra
   línea de la sección. Ahora se busca en toda la sección. Las clases no cambiaron (10, 28 y 1), porque esas
   palabras no tienen dígitos.

## Premisas del encargo contrastadas (pieza 5)

- **«logs/ trae 6 corridas, 5 con reservas EMITIDA»:** confirmada. Además, las 6 son del panel web; ninguna
  es de consola.
- **«Los logs nombran la fila de cada reserva»:** confirmada en 46 de 46, con dos formatos: `[NAV fila N]`
  en c1 a c5 y «Reserva i/n (fila N)» en la cabecera de c6. HYUNDAI no anota origen y destino en la línea de
  la fila, pero sí en «Origen '…'» y «Destino '…'».
- **«Hasta 8feabdb la consola escribía SIN EMITIR aunque volviera EMITIDA»:** en estas planillas, **0
  casos**. Los 9 «SIN EMITIR» dicen OK-EJEMPLO: salen de una corrida en modo seguro, no del defecto.
- **«Hasta fba3bc3 el estado podía caer en la P»:** **0 casos**. La P y la M están vacías en las 78 filas
  cruzadas, y todas las hojas reales tienen «Estado» en la H, así que la rama del defecto no se ejecutaba.
- **«El ERROR de COSCO tras pulsar Submit puede haber emitido»:** hay **1** caso (c3, fila 5 de COSCO), pero
  no es el tiempo agotado: es un error interno del programa (un `NameError`) justo después de pulsar Submit.
  Igual de incierto.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| Confirmar las 14 sospechosas y las posibles repetidas | Solo el portal lo dice | …revisas el portal con el detalle local |
| Los números de las 28 EMITIDA sin número | El log no los tiene; en CMA dice «Ver captura» y en el detalle está el nombre de la captura | …se leen las capturas o el portal |
| Qué corrida de consola escribió las filas 5 a 9 de COSCO y cuándo | No dejó log en `logs/` | …aparece su carpeta de log |
| Con qué planilla corrió cada corrida del panel | La copia de `%TEMP%` es solo la última subida | …aparecen las planillas subidas antes |
| Las 7 filas de la raíz cuya nave cambió después de la corrida | Dicen EMITIDA con el N° correcto; la nave pudo corregirse a mano | …el portal muestra otra nave para ese booking |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v12**:
- **PASO 0 y re-medir:** conté las corridas y las clases antes de cruzar.
- **Control positivo que aborta:** el parser contra un conteo independiente de las líneas de resultado.
- **Todo salto silencioso lleva contador:** las 7 reservas fuera del universo, contadas y con su motivo; 0 sin
  fila.
- **La unidad la fija el sujeto:** la reserva de una corrida frente a una fila de una planilla (78 cruces
  sobre 39 reservas), no la fila sola.
- **Lo inocuo y lo peligroso conviven en la misma familia:** EMITIDA con número frente a EMITIDA con una
  palabra de la página, separadas en todos los conteos.
- **Todo registro es una hipótesis:** «EMITIDA» en el log no prueba el envío cuando el número es basura.
- **Se declaran el residual y las premisas.**
- **FRENAR:** ninguna condición se cumplió; la lectura del primer freno está arriba.
- **El push se entrega, no se hace:** no hay remoto, así que no hay nada que entregar.

Reglas propias del módulo (`CLAUDE.md`): no importar el programa desde la raíz (se usó `soporte.cargar()`),
no copiar logs ni datos reales al repo y la sonda antes del commit. **Choques: ninguno.**

## Entregable (pieza 8)

- **Este `.md`, versionado.** Pasa la sonda de staging antes de su commit.
- **El detalle local, `revision_local/emitidas_segun_logs_2026-09-23.md`, no versionado.** Tiene una línea por
  reserva, primero las sospechosas, con:
  - la fecha de la corrida y la naviera;
  - la hoja y la fila;
  - la clase y el booking del log, o el texto crudo si no hay número;
  - el origen, el destino y la nave;
  - las últimas capturas;
  - lo que dice la fila en cada planilla, con su confianza.
