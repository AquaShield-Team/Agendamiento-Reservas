# CICLO · Carpetas de corrida con nombre único: aplicado

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-24 · **Método:** skill `metodo-ciclo` v12 ·
**Base:** `393f504` · **Commits:** `648e5f1` (el cambio) y el de este informe, locales y sin push.

> Sin datos reales: los casos de prueba son sintéticos y ningún log real se abrió en este ciclo. La
> medición previa está en `CICLO-carpetas-unicas.md`.

## Veredicto: LISTO

No se cumplió ningún FRENA SI. Sobre `648e5f1`, con el árbol limpio e igual al commit:
- **La red completa pasó 10 de 10 corridas seguidas:** 189 pruebas cada una, 0 cambios en los originales.
- **El censo completo pasó una vez:** 352 mutaciones, 413 pares, todos muerden, 0 pruebas sin mutación.
- **La sonda de secretos dio 0** en el árbol y en el staging del commit.

**PASO 0: CICLO** (la decisión ya estaba tomada; faltaba aplicarla y medirla).

## Qué cambió

- **`carpeta_corrida(prefijo)`**, junto a `LOGS`:
  - Arma `<prefijo>_<AAAAmmdd_HHMMSS>` y crea la carpeta **en exclusiva** (`mkdir` sin `exist_ok`).
  - Si ya existe, prueba `_2`, `_3`… hasta que una se crea.
  - Sin choque, el nombre es el de antes.
- **Los tres lugares que creaban carpetas la usan:** `ejecutar_login` (`<usuario>`), `ejecutar_reservas`
  (`reservas_<naviera>_<usuario>`) y `_web_worker` (`web_<naviera u hoja>_<usuario>`).
- **`ejecutar_reservas` conserva su `ts`:** además del nombre de la carpeta, arma la referencia de ejemplo
  `EJ<HHMMSS><n>` que va en la planilla (ver el defecto de instrumento 1).
- **No cambió nada que busque carpetas:** los generadores nombran a mano sus 4 corridas de referencia, y el
  panel usa la ruta guardada (`CICLO-carpetas-unicas.md`).

## Las expectativas que cambiaron (solo estas dos)

| Prueba | Antes | Después |
|---|---|---|
| `test_web.TestPanelCorridas.test_corrida_de_una_hoja` | El nombre calza con `^web_one_op_prueba_\d{8}_\d{6}$` | Calza con `^web_one_op_prueba_\d{8}_\d{6}(_\d+)?$`, y la carpeta no estaba entre las de `logs/` antes de la corrida |
| `test_consola.TestEjecutarReservas.test_reservas_por_consola` | El nombre calza con `^reservas_cma_op_prueba_\d{8}_\d{6}$` | Calza con `^reservas_cma_op_prueba_\d{8}_\d{6}(_\d+)?$`, y la carpeta no estaba antes de la corrida |

**Ninguna otra expectativa cambió.** `test_login_por_consola` sigue con `^op_prueba_\d{8}_\d{6}$`, y
`test_todas_deja_una_sola_copia` con `(6, 1, 5)`.

## Las pruebas nuevas, con el reloj detenido

`soporte.reloj_detenido(mod)` cambia el nombre `datetime` del programa en la sandbox por un espejo del
módulo, cuyo `datetime.now()` devuelve siempre el mismo segundo. El `datetime` de Python no se toca. Así,
dos corridas seguidas chocan siempre, no según el reloj.

| Prueba | Qué fija |
|---|---|
| `test_consola.TestCarpetaCorrida.test_mismo_segundo_da_carpetas_distintas` | Tres llamadas en el mismo segundo dan `…_030405`, `…_030405_2` y `…_030405_3`, en ese orden alfabético. Otro prefijo en el mismo segundo sale sin sufijo |
| `test_consola.TestCarpetaCorrida.test_consola_en_el_mismo_segundo` | Dos `ejecutar_reservas` seguidas: dos carpetas (la segunda con `_2`), cada log con una sola línea «INICIO» |
| `test_consola.TestCarpetaCorrida.test_login_en_el_mismo_segundo` | Igual, con `ejecutar_login` |
| `test_web.TestPanelCorridas.test_dos_corridas_en_el_mismo_segundo` | Igual, con dos corridas del panel web |

## Los defectos inyectados

**Censo filtrado antes del commit:** 13 mutaciones y 22 pares. Son las 10 de la tabla más 3 ajenas que calzan con el filtro «carpeta»: `poda-toma-carpetas`, `poda-entra-a-subcarpetas` y `volcado-a-otra-carpeta`. **Todas muerden**, cada una por el motivo esperado. Control: la copia sin mutar pasa.

| Mutación | Qué rompe | La tumban |
|---|---|---|
| `carpeta-comparte-si-existe` (nueva) | `mkdir(exist_ok=True)`: vuelve a compartir | Las 4 pruebas nuevas |
| `carpeta-sufijo-desde-uno` (nueva) | El primer sufijo es `_1` | Las 4 pruebas nuevas |
| `carpeta-sufijo-sin-guion` (nueva) | `…_0304052` | `test_mismo_segundo_da_carpetas_distintas` |
| `carpeta-sin-segundos` (nueva) | El nombre va al minuto | `test_mismo_segundo…`, `test_login_por_consola`, `test_reservas_por_consola`, `test_corrida_de_una_hoja` |
| `login-arma-su-carpeta` (nueva) | El login vuelve a armar su nombre a mano, como hasta `393f504` | `test_login_en_el_mismo_segundo` |
| `consola-arma-su-carpeta` (nueva) | Lo mismo en la consola | `test_consola_en_el_mismo_segundo` |
| `web-arma-su-carpeta` (nueva) | Lo mismo en el panel | `test_dos_corridas_en_el_mismo_segundo` |
| `consola-otra-carpeta-de-log` (reescrita) | Otro prefijo; su texto viejo cambió, el defecto es el mismo | `test_reservas_por_consola` |
| `login-otra-carpeta` (reescrita) | Idem | `test_login_por_consola` |
| `login-acepta-operador-desconocido` (reescrita) | Su texto de contexto incluía las dos líneas que cambiaron; el defecto es el mismo | `test_operador_desconocido` |

**La condición «la carpeta no existía antes de la corrida» no tiene mutación en el censo, y no puede
tenerla:**
- El censo corre cada prueba sola, y una prueba sola no tiene corrida anterior con la que chocar.
- Para ver que muerde, la corrí junto a la prueba anterior de su clase, con el defecto que vuelve a armar el
  nombre a mano, 5 veces por caso.
- Cae por la aserción nueva, «… unexpectedly found in …».

| Par de pruebas | Con el defecto | Control, sin defecto |
|---|---|---|
| `test_corrida_con_estados_tras_el_envio` + `test_corrida_de_una_hoja` | 1 de 5 | 0 de 5 |
| `test_error_de_escritura_se_muestra_y_queda_en_el_log` + `test_reservas_por_consola` | 5 de 5 | 0 de 5 |

Que caiga depende de que las dos corridas coincidan en el segundo. Lo que la vigila de forma determinista
son las cuatro pruebas con el reloj detenido.

## La red sobre el commit

Lanzadas en un proceso aparte, una detrás de otra, entre las 10:03 y las 10:41, sobre `648e5f1`. Al final, el árbol seguía limpio.

| Corrida | Pruebas | Duración | Cambios en los originales |
|---|---|---|---|
| 1 | 189 de 189 | 130 s | 0 |
| 2 | 189 de 189 | 138 s | 0 |
| 3 | 189 de 189 | 149 s | 0 |
| 4 | 189 de 189 | 174 s | 0 |
| 5 | 189 de 189 | 154 s | 0 |
| 6 | 189 de 189 | 144 s | 0 |
| 7 | 189 de 189 | 138 s | 0 |
| 8 | 189 de 189 | 132 s | 0 |
| 9 | 189 de 189 | 152 s | 0 |
| 10 | 189 de 189 | 141 s | 0 |

**Censo completo, una vez:** la copia sin mutar pasa las 189. Las 352 mutaciones, en 413 pares, muerden todas, y no queda ninguna prueba sin mutación. 0 cambios en los originales.

| Red | Antes (`393f504`) | Ahora (`648e5f1`) |
|---|---|---|
| Pruebas | 185 | 189 |
| Mutaciones | 345 | 352 |
| Pares | 397 | 413 |
| Corridas completas que pasan | 1 de 5 | 10 de 10 |

## FRENA SI

- **Otra prueba intermitente en las 10 corridas:** no. Las 10 pasaron enteras: ninguna prueba falló ni una vez.
- **Cambiar la expectativa de otra prueba:** no. Cambiaron solo las dos decididas, y las otras 183 que ya existían quedaron igual. Las 3 mutaciones reescritas no son expectativas: su texto viejo cambió y el defecto que inyectan es el mismo.

## Premisas del encargo contrastadas (pieza 5)

- **«`test_todas_deja_una_sola_copia` falla 4 de 5 por la misma causa»:** resuelta. Pasó en las 10 corridas; antes pasaba 1 de 5. Su expectativa `(6, 1, 5)` no cambió: con el nombre único, la carpeta de ONE de «todas» es nueva aunque caiga en el mismo segundo que otra.
- **«Sin choque, el nombre sale igual que hoy»:** confirmada. La fija `test_mismo_segundo_da_carpetas_distintas`
  (otro prefijo, sin sufijo). También las tres pruebas que miran el formato: siguen calzando con `\d{6}` cuando
  no hay choque.
- **Mía, del informe anterior, refutada:** dije que `test_login_por_consola` «es la única prueba de su
  clase». No es así: `TestEjecutarLogin` tiene 4. No choca por otra razón: es la primera de su clase en
  orden alfabético, y las otras tres no corren antes. La conclusión se mantiene; la razón era falsa.

## Universo y cobertura (pieza 3)

- **Código:** los 3 lugares que crean carpetas de corrida (un análisis AST confirmó que los tres llaman a
  `carpeta_corrida` y que ninguno usa un `ts` que ya no existe).
- **Pruebas:** 189 (185 más las 4 nuevas). Mutaciones: 352 (345 más 7). Pares: 413 (397 más 16).
- **Fin de línea:** los 5 archivos tocados siguen en LF, comparados en binario con `HEAD`.

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\correr.py --mutaciones
python tests\correr.py --mutaciones --filtro carpeta
python tests\sonda_secretos.py --dry-run
```

- **Las 10 corridas:** `tests\correr.py` diez veces seguidas sobre un árbol limpio igual a `648e5f1`, cada
  una con su salida, y después `--mutaciones` una vez.
- **La condición «no existía»:** correr el par de pruebas de la tabla con la mutación aplicada a una copia,
  usando `preparar_fuentes` y `correr_unittest` del corredor.

## NO retroceder (pieza 2)

- **No cambies el `mkdir` exclusivo por mirar si existe y después crear:** dos corridas simultáneas podrían
  elegir el mismo nombre.
- **No quites la condición «la carpeta no existía»** de las dos pruebas: es la que habría destapado el choque.
- **No quites el `ts` de `ejecutar_reservas`:** arma la referencia de ejemplo de la planilla.
- **`reloj_detenido` cambia solo el nombre `datetime` del programa en la sandbox.** Si alguien lo cambia por
  el `datetime` de Python, el reloj se detiene para todo el proceso de la prueba.

## Defectos de instrumento cazados (pieza 4)

1. **Casi rompo la consola.** Al pasar `ejecutar_reservas` a `carpeta_corrida` quité la línea del `ts`. La
   función lo usa más abajo para la referencia de ejemplo: habría reventado con `NameError` en cada reserva.
   Lo cazó un análisis AST de los usos de `ts`, antes de correr ninguna prueba.
2. **Una razón falsa en mi informe anterior** (la de `test_login_por_consola`, arriba en premisas).
3. **La frecuencia de la demostración no es la de la red.** El par del panel chocó 1 de 5 corriendo como
   proceso aparte y 4 de 5 dentro de su clase (ciclo anterior): el arranque de cada proceso mueve los
   tiempos. La demostración prueba que la condición muerde, no con qué frecuencia.
4. **Un cero que no era cero.** Las salidas de las 10 corridas las escribió PowerShell en UTF-16, y mi primer `grep` sobre ellas no encontró ninguna línea. Lo cacé porque el resumen, leído con `Select-String`, sí decía «RESULTADO: OK» en las 10. Las volví a leer con Python, decodificando UTF-16.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| La condición «no existía» no tiene mutación en el censo | El censo corre cada prueba sola; su guardián determinista son las 4 pruebas con reloj detenido | …el censo aprende a correr pares |
| Las copias de respaldo usan « (2)» y las carpetas `_2` | Decisión: `_2` sigue el estilo del nombre de carpeta | …se quiere un solo estilo |
| El simulador nombra `logs/cma_dev`, que no existe | Fuera del encargo | …se regenera el simulador |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v12**:
- **El cambio y su guardián, en la misma operación:** la función, sus cuatro pruebas y sus siete mutaciones
  van en el mismo commit.
- **El negativo tiene que morder, de a uno:** censo filtrado, un par por proceso.
- **Un negativo vacuo delata un caso incompleto:** la condición «no existía» no puede morder sola (b: el caso
  aislado no tiene choque). Su caso completo es el par de pruebas; el guardián determinista es el reloj
  detenido.
- **Cada reemplazo afirma que su viejo aparece una vez:** el prechequeo de las 352 mutaciones.
- **El EOL se preserva y se verifica:** en binario contra `HEAD`.
- **Declarar las premisas refutadas:** incluida una mía.
- **El push se entrega, no se hace:** no hay remoto.

Reglas propias del módulo (`CLAUDE.md`): las pruebas son fotos, y cada expectativa que cambia va con su antes
y después. Toda prueba nueva lleva su mutación. Casos sintéticos, y la sonda antes de cada commit.

**Choques entre reglas:** ninguno.

## Entregable (pieza 8)

Este `.md`, sin renderizar, y `CLAUDE.md` puesto al día: la nota de la prueba que dependía del reloj se
borra, la sección de `logs/` dice cómo se nombran las carpetas, y la red pasa a 189 pruebas.
