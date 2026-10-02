# CICLO · Red de verificación offline de AQUASHIELD

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-23 · **Método:** skill `metodo-ciclo` v12 ·
**Commits:** `986e060`, `6f235c1`, `9b28d93`, `e99cf61` y el de este cierre · **Remoto:** ninguno; no hubo push.

> Sin datos reales: los casos son sintéticos (estructura de los reales, valores inventados), el operador
> aparece como `<op1>` y los valores de empresa escritos en el código se comparan por hash. Los logs reales
> se leyeron solo como referencia local y no se copió nada de ellos.

## Veredicto

**No se cumplió ninguna condición de FRENA SI.** Así quedó cada una:

1. **No hizo falta tocar `AQUASHIELD.py`.** Todo se probó sobre una COPIA del programa en una carpeta
   aislada, con dobles para lo que está fuera del programa (Playwright, `subprocess`, `webbrowser`,
   `tempfile`, `tkinter.messagebox`) o reemplazando en memoria variables globales del módulo (`NAVIERAS`,
   `RESERVADORES`, `sync_playwright`, `time`). El programa tiene el mismo hash antes y después de cada corrida.
2. **Lo que solo se puede verificar contra un portal no se intentó.** Son el login y el llenado de las seis
   navieras y el JavaScript que se inyecta en las páginas, y quedan en la columna «no verificable offline»
   de la cobertura por naviera. Leí este freno como «no lo hagas; repórtalo», porque el mismo encargo pide
   listar lo que no se puede verificar offline. Si la idea era detener todo el ciclo en el primer caso,
   el ciclo pasó de ese punto: dímelo y lo reviso.
3. **Ejecutar el programa en las pruebas no disparó efectos reales.** Las trampas registraron 0 disparos
   en toda la suite. Las 622 entradas de los originales (raíz, `logs/`, `perfiles/` y la planilla
   temporal del panel real) salieron iguales en cada corrida. El cierre forzado de procesos y el navegador
   se probaron solo con dobles.

**Una PREGUNTA para ti:** el candado se abre con **cualquiera** de las tres llaves; no hace falta que estén
las tres. La red lo registra así (`test_basta_una_llave_de_tres`). Con las tres apagadas no emite en
ninguna de las 540 combinaciones probadas. Si «sus tres llaves» quería decir que tienen que estar las tres
encendidas, el programa hoy no lo cumple, y cambiarlo es tocar `AQUASHIELD.py`: otro frente.

**PASO 0: CICLO, cerrado.**

## Cómo se corre

```powershell
python tests\correr.py                  # suite (~80 s) + foto de los originales antes y después
python tests\correr.py --mutaciones     # censo: cada defecto inyectado tiene que tumbar su prueba
python tests\correr.py --todo           # las dos cosas (8-10 min)
python tests\sonda_secretos.py --dry-run  # antes de git add; y sin argumentos, después
```

## Qué hay en la red

| Módulo | Pruebas | Pares mutación-prueba | Qué fotografía |
|---|---|---|---|
| `test_arnes` | 4 | 9 | Importar el programa no abre navegador, no lanza procesos ni hilos, no sale a la red y no escribe archivos; las rutas de trabajo caen en la sandbox; el candado está cerrado al cargar, aunque falte `config.json` |
| `test_candado` | 17 | 20 | La tabla de verdad de `es_modo_emision`; quién consulta el candado; la guarda de cada reservador; los lanzadores `.py` y `.bat` |
| `test_planilla` | 25 | 44 | Los dos lectores por naviera y por hoja, sus diferencias, cómo escribe la consola y la descarga del panel |
| `test_booking` | 13 | 14 | `extraer_numero_booking` por naviera y `_extraer_bkg_limpio` |
| `test_ayudantes` | 12 | 16 | Ayudantes puros por naviera, incluido el cálculo del puzzle de COSCO con imágenes sintéticas |
| `test_registro` | 4 | 7 | Cada naviera en `NAVIERAS`, `RESERVADORES`, `HOJA_ALIAS` y en la secuencia del worker web; cómo se traduce una hoja o un texto a su naviera |
| `test_web` | 22 | 32 | El panel en un puerto propio: rutas, credenciales, planilla, corridas, pausa, detener, modo login y arranque |
| `test_consola` | 17 | 28 | `main()`, `ejecutar_reservas`, `ejecutar_login`, `Registro`, capturas, pausas, argumentos de Chrome y volcados HTML |
| **Total** | **114** | **170** (150 mutaciones) | |

## Cobertura por naviera

Las «funciones ejecutadas» se midieron con `AQUASHIELD_COBERTURA`: son las funciones de nivel superior de
cada naviera que la suite llega a ejecutar. En total, **38 de 135**.

| Naviera | Verificado offline | No verificable offline | Funciones ejecutadas |
|---|---|---|---|
| ONE | La guarda del candado; el número de booking (`SCLG…`, «Booking Reference»); la elección de contrato (EE. UU. u otros mercados, por hash); la lectura de su hoja (regla de la columna 6); alias y registro; la orquestación con dobles | El login (sesión persistente); todo Quick Booking (autocompletados, desplegables, contrato, rango de 8 semanas, elección de nave); Review; la rama de emisión | 1 de 12 |
| MSC | La guarda; el número (`EBKG…`, «eBooking number», «Booking reference»); la fecha futura; la lectura de su hoja (columna D y el viaje con «NX»); el registro | El login y las cookies OneTrust; el datepicker y los desplegables Kendo; el HS Code; el contenedor; los comentarios; Summary | 1 de 16 |
| CMA-CGM | La guarda (sus 2 textos «Book» previos son una docstring y un log); el número (rama propia); la fecha dd/mm/aaaa; el detector anti-bot con páginas falsas; la lectura; el registro | El login; el slider de DataDome; Click & Book; la elección de itinerario; los ajustes reefer; los comentarios | 2 de 14 |
| COSCO | La guarda; el número (con la validación y el descarte de «Templates»); el resumen y la normalización; **el cálculo del hueco del puzzle con imágenes sintéticas**; la lectura; la escritura en «Estado (Robot)» | El login E-LINES y el validador real (el arrastre); el iframe `bkg2`; los autocompletados; Booking Details; el diálogo «Reminder» | 3 de 18 |
| HYUNDAI | La guarda (con sus 10 textos intermedios registrados); el número (`SCLA…`, «Bkg No»); el alias «HMM»; la lectura | El login HMM; «Book Now»; el aviso reefer; Container & Cargo; Review & Book. **Offline no se puede confirmar que ningún paso previo a la guarda envíe algo** | 0 de 9 |
| MAERSK | La guarda (devuelve `OK-EJEMPLO` o `REVISAR`); el número (`27…`, «Your booking»); la fecha «DD MMM YYYY»; el cliente por defecto (por hash); la lectura; el alias «Maersk Line» | El login OIDC y las cookies; GenSet; el contenedor; la elección de sailing | 2 de 16 |
| Común | El candado; los lectores y la escritura; el panel web entero; la consola; `Registro`; los argumentos de Chrome; los volcados HTML | Los ayudantes que manejan la página (`esperar_hasta`, `rellenar`, los autocompletados: 16 funciones); el panel Tkinter y la marca dibujada (`lanzar_panel`, `isotipo`, `logotipo`, `_familia`); el andamiaje `_login_portal` | 29 de 50 |

## Rarezas registradas (no se corrigió ninguna)

1. **El candado se abre con una sola llave de las tres** (ver la PREGUNTA). Además, `"emitir_reservas": "false"`
   escrito como texto también abre.
2. **Guardas:** cada reservador tiene exactamente una, y los botones de envío final están después de ella.
   HYUNDAI tiene 10 textos «Book Now», «Confirm» o «Review & Book» antes de su guarda: son pasos
   intermedios, fotografiados y no verificados.
3. **Lectores:** sobre la misma hoja no leen lo mismo.
   - La consola descarta la fila de nota; el panel web la lee como reserva.
   - La consola lee como reserva un encabezado repetido; el panel web lo salta.
   - La consola descarta una fila que solo trae una nave con coma; el panel web la lee.
   - En ONE, la consola toma el viaje como nave y pisa el destino final.
   - La consola conserva una nave «POR COMPLETAR»; el panel web la deja vacía.
   - Solo el panel web devuelve los campos `naviera` y `temp`.
   - Un título que contenga «origen» engaña a la consola (toma esa fila como encabezado) y no al panel web.
4. **La consola escribe sobre la planilla original.** Si falta la columna Estado, la crea en la columna 16
   de una hoja de 9: `ws.cell()` crea celdas mientras busca. Además se traga los errores sin avisar.
5. **La descarga del panel devuelve una copia,** pero escribe los mismos números de fila también en
   `CONSOLIDADO`, donde corresponden a otras reservas.
6. **Número de booking:**
   - Un «27» en cualquier parte del texto mete a cualquier naviera en la rama de MAERSK.
   - `_extraer_bkg_limpio` devuelve «Templates» como si fuera un número.
7. **Ayudantes por naviera:**
   - Fuera de EE. UU., ONE ignora el `contrato` general de las credenciales.
   - La fecha de CMA acepta el mes 13.
   - «MSC ONE» se asigna a ONE.
8. **Panel web:**
   - Una corrida sin filas elegidas igual abre el navegador y hace login.
   - El modo login deja el navegador abierto 6 s.
   - Al arrancar, cierra con `taskkill /F` al proceso que ocupe el puerto base. Antes le pide apagarse a
     una instancia AQUASHIELD ociosa y cede ante una ocupada.
   - El relevo espera un tiempo fijo de 0,6 s; si la instancia previa tarda más en soltar el puerto, usa
     el siguiente.
   - Al apagarse no cierra su socket.
9. **Consola:**
   - Escribe «SIN EMITIR» en la planilla aunque la reserva vuelva `EMITIDA`.
   - El modo login abre el navegador aunque ninguna naviera pedida tenga credenciales.

## Universo y cobertura (pieza 3)

- **Pruebas:** 114. Mutaciones: 150, que forman 170 pares mutación-prueba, y los 170 muerden. Hay 0
  pruebas sin mutación. La copia sin mutar pasa las 114.
- **Motivos revisados:** 170 de 170. Hay 157 `AssertionError`, 3 trampas y 10 excepciones esperadas: un
  tipo de error cambiado, 3 claves y 3 archivos que faltan, 2 errores de la página falsa que dejan de
  atraparse y 1 hijo que no termina.
- **Funciones:** 38 de 135 de nivel superior ejecutadas (tabla anterior).
- **Candado:** 540 combinaciones con las tres llaves apagadas y 0 emiten. La tabla de verdad completa tiene
  8 casos, y cada llave se probó sola con 7 u 8 valores.
- **Originales:** 622 entradas (623 desde que existe este informe), sin cambios en ninguna de las
  corridas completas.
- **Secretos:** la sonda sobre el staging dio 0 antes de cada uno de los commits.

## Re-medir (pieza 1)

Los comandos de «Cómo se corre». Para la cobertura por función:
`$env:AQUASHIELD_COBERTURA = "$env:TEMP\cob"; python tests\correr.py` y después une los archivos
`cob.<pid>`. Las pruebas, las mutaciones y el arnés están versionados en `tests/`.

## NO retroceder (pieza 2)

- **Nunca importes `AQUASHIELD.py` desde la raíz en una prueba:** desde ahí, `BASE` apunta a la planilla,
  `config.json` y `perfiles/` reales. Siempre usa `soporte.cargar()`.
- **No saques las trampas ni cambies su orden:** Playwright y `asyncio` se importan antes de reemplazar
  `subprocess.Popen`, porque `asyncio` hereda de esa clase.
- **Nunca uses el puerto 8765 en una prueba.**
- **Las pruebas son fotos:** si corriges una rareza, su prueba cae a propósito. Actualiza la foto en el
  mismo cambio y decláralo.
- **Toda prueba nueva necesita su mutación:** el censo falla si no la tiene.

## Defectos de instrumento cazados (pieza 4)

1. **La trampa de `Popen` era una función, y `asyncio` necesita una clase de la cual heredar.** Pasó a ser
   una subclase, y Playwright y `asyncio` se importan antes de instalar las trampas.
2. **Usé `sort` de Git Bash, que Defender bloquea en esta máquina.** Lo reemplacé por Python.
3. **Mi script de fotografía borró su propio argumento `--trampa`:** el arnés limpia `sys.argv` para
   apagar la llave del argumento.
4. **Rutas cortas 8.3 contra rutas largas** (`USUARI~1.XXX`): la sandbox ahora nace con la ruta resuelta.
5. **Tres mutaciones no mordían porque otro patrón de la misma función recuperaba el mismo número.** Les
   faltaba un caso; se completaron. Es la lectura (b) de la regla del negativo vacuo.
6. **`extraer_numero_booking` tiene dos `try` que se tapan entre sí** (lectura (e)). Se midió que cada capa
   sola no muerde, así que la mutación apaga las dos. El corredor ahora acepta mutaciones de varios cambios.
7. **Edité el arnés durante un censo, y esa corrida dejó de valer como puerta.** Se repitió entera, y por
   eso las iteraciones 4 y 5 van en un solo commit.
8. **El filtro de motivos no reconocía el tiempo agotado,** y un motivo quedó vacío. Se amplió.
9. **Una instancia previa en el mismo proceso no suelta el puerto,** porque el programa no cierra el socket.
   El relevo se probó con la instancia previa en un proceso hijo que carga el arnés.
10. **Precauciones del corredor:** una mutación que no compila se marca como inválida en vez de contar como
    mordida, y cada caída muestra su motivo.
11. **El arnés registraba sus sandboxes pero no las borraba.** Al cerrar el ciclo había 1321 carpetas y
    930 MB en `%TEMP%`, todas copias del programa con datos sintéticos. Ahora cada proceso borra las suyas
    al salir: tras un censo completo quedaron 20 restos parciales, que también se borraron. La planilla
    temporal del panel real no se tocó.

## Premisas del encargo contrastadas (pieza 5)

- **«Dos lectores que se comportan distinto» (observado, no medido):** confirmado y medido. Las diferencias
  están en la rareza 3.
- **«El panel web devuelve una copia y la consola escribe sobre `Reservas AQUASHIELD.xlsx`»:** confirmado.
  Hay algo nuevo: la copia también pisa filas de `CONSOLIDADO`.
- **«Al arrancar se cierra a la fuerza lo que ocupe el puerto 8765»:** confirmado, con precisión. Solo
  ocurre si falla el enlace al puerto base, y antes intenta relevar o respetar a una instancia AQUASHIELD.
  Después prueba los puertos 8766 a 8768.
- **«Verificar que no emite en ninguna combinación sin sus tres llaves»:** con las tres apagadas, 0 de 540.
  Pero basta una para emitir (la PREGUNTA).
- **Registro contrastado:** `CLAUDE.md` decía que `py_compile` era la única verificación y que no había
  pruebas. Se actualizó en este cierre.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| Los flujos de login y reserva de las seis navieras (76 de las 85 funciones de navieras sin ejecutar) | Necesitan el portal; el encargo lo prohíbe | …hay un entorno de pruebas de una naviera, o páginas HTML sintéticas que imiten sus formularios |
| El JavaScript inyectado (`_JS_*`) | Hace falta un navegador, aunque sea sin ventana; el encargo lo prohíbe | …se acepta un Chromium sin ventana contra HTML sintético local |
| El panel Tkinter y la marca dibujada | Abren una ventana | …se cambia `lanzar_panel` o la identidad visual |
| El watchdog de 90 s | Exige esperas largas o reemplazar el reloj dentro del hilo del servidor | …se toca el apagado automático |
| Los pasos previos a la guarda en HYUNDAI | Registrados, sin forma de comprobar offline qué hacen | …aparece una duda de emisión en HYUNDAI |
| La rama de emisión de cada reservador | Por diseño, no se ejecuta nunca en la red | …se cambia la guarda |
| La carrera del relevo (0,6 s) | La prueba acepta el puerto base o el siguiente | …se cambia el arranque |
| Unos 20 restos de sandbox por cada censo completo, en `%TEMP%` | Archivos todavía abiertos al salir (Windows no deja borrarlos) o procesos hijos terminados a la fuerza | …los restos crecen; se pueden borrar a mano las carpetas `aquashield_red_*` |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v12**:
- **Control positivo que aborta:** la copia sin mutar tiene que pasar; la sonda de secretos; la lectura del
  staging; el arranque real.
- **El negativo tiene que morder, de a uno por llamada:** los 170 pares corren cada uno en su propio proceso.
- **Un negativo vacuo delata un caso incompleto:** lecturas (b) y (e), en los defectos 5 y 6.
- **Censo:** va de la prueba a su mutación; en sentido inverso, de la pieza del programa a la prueba que la
  vigila, lo mide la cobertura (38 de 135).
- **Un chequeo de sintaxis no prueba el contrato:** las pruebas ejecutan el programa; la compilación solo
  sirve para invalidar mutaciones rotas.
- **Todo registro es una hipótesis:** las observaciones del `/init`, contrastadas.
- **Re-medir contra HEAD, declarar el residual y las premisas refutadas.**
- **FRENAR:** la pregunta sobre cuántas llaves abren el candado queda para ti.
- **El push se entrega, no se hace:** no hay remoto, así que no hay nada que entregar.

El módulo no tiene reglas de método propias; su `CLAUDE.md` ahora documenta la red. **Choques: ninguno.**

## Entregable (pieza 8)

Este `.md`, sin renderizar. Pasa la sonda de staging antes de su commit.
