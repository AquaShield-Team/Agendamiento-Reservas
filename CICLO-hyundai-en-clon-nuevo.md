# Encargo 70 · Por qué HYUNDAI abre otra página en un clon nuevo de `estable`

**Base:** `C:\dev\Agendamiento Reservas` @ `a2998b0` · árbol limpio al empezar.

Diagnóstico sin portal, con `metodo-ciclo` v28: al empezar, la sesión tenía cargada la v26 y el archivo decía v28, así
que la volví a invocar antes de medir. Todo se midió sin abrir ningún portal ni tocar `config.json`: el código, la forma
de `config.json` y de la plantilla (solo los nombres de las claves y las direcciones), `logs/`, y el programa corriendo
sin red en una copia aislada.

**Al abrir el ciclo:** el código es el mismo en los tres lados. `main` local, `origin/main` y `origin/estable` están en
`a2998b0` (medido con `ls-remote` al empezar). El informe del encargo 69 dejaba `estable` en `582924d`, con el bloque
para avanzarla después de probar; ya la avanzaste. Ninguna librería de terceros viaja en el HTML del panel: lo único que
carga es lo propio (`/app.js`, `/estilo.css` y `/fuentes.css`), así que no hay avisos de seguridad que consultar.

## En resumen

- **La causa: la dirección del login de HYUNDAI sale de `config.json`.**
  - `login_hyundai` va a la llave `url` de las credenciales de HYUNDAI del operador, y solo si no la tiene, a la página
    del login de e-service: `creds.get("url") or "https://www.hmm21.com/e-service/auth/login.do"`.
  - La plantilla, `config.example.json`, trae en esa llave la portada general, **`https://www.hmm21.com/`**, en sus dos
    operadores, `usuario1` y `usuario2`.
  - El `config.json` de este equipo trae, en el operador de las corridas, la del login,
    `https://www.hmm21.com/e-service/auth/login.do`. El otro operador de este `config.json` trae la portada, como la
    plantilla.
- **En un clon nuevo, el panel crea `config.json` desde la plantilla** (encargo 61), y no muestra ni cambia esa llave.
  Si el colega escribe sus credenciales en `usuario1` o en `usuario2`, la llave queda.
  - Medido por el camino del panel, sin red: con `usuario1`, HYUNDAI va a la portada.
  - Con un operador creado desde Credenciales, que nace sin esa llave, va al login.
- **La página de reservas no sale de `config.json`:** `BookingStepByStep1.do` está escrita en el programa. Lo que cambia
  es la primera página, la del inicio de sesión.
- **Qué hace la portada no está medido:** hace falta el portal.
  - En la portada, el programa busca el campo del usuario y trata de escribir el usuario y la clave.
  - Después pulsa el primer botón o enlace «Login», o el primer `input[type=submit]`, de los que tenga la página.
  - Si no termina en una página de e-service, el login dice «No confirmé la sesión». El panel anota «No se pudo iniciar
    sesión en HYUNDAI; no proceso sus reservas», y las filas de HYUNDAI quedan sin estado. El navegador queda donde
    terminó.
- **La condición de freno se cumple para el arreglo:** cambiar la plantilla la decides tú. Abajo van las opciones y mi
  recomendación. Es un encargo de diagnóstico, sin Modo autónomo, así que no cambié nada.

## De dónde sale la dirección de cada naviera

Universo: las 13 direcciones de portal escritas en `AQUASHIELD.py` y las 25 líneas que leen las credenciales de una
naviera (`creds.get(`, `creds[` y `(creds or {})`). Solo dos leen la llave `url`:
- la de `login_hyundai`, que es el control: tiene que aparecer, y aparece;
- la de `_login_portal`, el andamiaje para navieras nuevas, que no lo llama nadie (0 llamadas).

| Naviera | Inicio de sesión | Reservas | ¿Sale de `config.json`? |
|---|---|---|---|
| ONE | `https://ecomm.one-line.com/one-ecom/booking/quick-booking` (`login_one`) | la misma, `?step=search-schedule` (`reservar_one`) | no |
| MSC | `https://www.mymsc.com/` (`_msc_abrir`) | `https://www.mymsc.com/myMSC/booking/main` (`MSC_EBOOKING`, `reservar_msc`) | no |
| CMA-CGM | `https://www.cma-cgm.com/` (`login_cma`) | `https://www.cma-cgm.com/ebusiness/shipment/request` (`reservar_cma`) | no |
| COSCO | `https://elines.coscoshipping.com/ebusiness/Dashboard`, y si no, `/ebusiness/` (`login_cosco`) | `https://elines.coscoshipping.com/ebusiness/bookingrequest/` (`reservar_cosco`) | no |
| HYUNDAI | **la `url` de sus credenciales**, o `https://www.hmm21.com/e-service/auth/login.do` (`login_hyundai`) | `https://www.hmm21.com/e-service/export/bookingrequest/BookingStepByStep1.do` (`reservar_hyundai`) | **sí, la del inicio de sesión** |
| MAERSK | `https://www.maersk.com/book/` (`login_maersk`) | la misma (`_mk_listo_para_reservar`) | no: tiene su `url` en las credenciales, pero no la lee nadie |

## Qué cambia entre este `config.json` y la plantilla

Con `forma_config.py`, que imprime solo los nombres de las claves, el tipo de cada valor, si viene vacío, y las
direcciones sin su consulta. Los operadores van numerados, porque su nombre puede ser el de una persona. Su control: la
`url` de HYUNDAI de la plantilla tiene que aparecer, y aparece. La plantilla tiene 72 claves, y este `config.json`, 75.

**Las llaves `url`, las únicas direcciones de los dos archivos** (4 en cada uno):

| Llave | Plantilla | `config.json` de este equipo |
|---|---|---|
| operador 1 · `hyundai/url` | `https://www.hmm21.com/` | `https://www.hmm21.com/e-service/auth/login.do` |
| operador 1 · `maersk/url` | `https://www.maersk.com/` | `https://accounts.maersk.com/ocean-maeu/auth/login` (sin su consulta) |
| operador 2 · `hyundai/url` | `https://www.hmm21.com/` | `https://www.hmm21.com/` |
| operador 2 · `maersk/url` | `https://www.maersk.com/` | `https://www.maersk.com/` |

El operador 1 es el de las corridas de este equipo.

**Lo demás que cambia, y qué hace en cada naviera** con la plantilla:

| Naviera | En la plantilla | Qué hace el programa |
|---|---|---|
| ONE | sin `contrato_usa` ni `contrato_otros`, que este equipo trae en el operador 1; `contratos_por_defecto` vacíos | elige «Otros contratos» sin escribir uno (encargo 44) |
| MSC | contrato vacío, en las credenciales y en `contratos_por_defecto` | deja vacío el campo del contrato |
| CMA-CGM | contrato vacío | no escribe la cotización («sin 'contrato' en config.json; CMA lo exige») y sigue a «Validar ruta» |
| COSCO | contrato y `nombre_en_pantalla` vacíos | queda el primer contrato de la cuenta, el que pone el portal; reconoce la sesión por la empresa |
| HYUNDAI | `url`: la portada; contrato vacío, en las credenciales y en `contratos_por_defecto`; `codigo_shipper_hyundai` vacío | va a la portada; si llegara a Booking Details, **queda NO ENVIADA en «Contract No»** (encargo 44); busca el Shipper solo por el nombre |
| MAERSK | `url`: otra, pero no la lee nadie | igual que aquí |

- En «opciones», la plantilla trae `segundos_visible`, que lee solo el panel Tkinter.
- Este equipo trae, además, `espera_seg`, que no lee nadie, y `emitir_reservas`, que no es `true`: el candado está
  cerrado.
- Lo demás son las credenciales, llenas aquí y vacías en la plantilla.

## Por el camino real, sin red

`sonda_login_clon.py` corre así:
1. Copia el programa a una carpeta aislada, sin `config.json` y con la plantilla al lado, como en un clon nuevo
   (`tests/soporte.cargar`).
2. Su panel web, en un puerto que da el sistema, crea `config.json` al pedir `/api/config`, como en el equipo del
   colega.
3. Con `/api/credenciales`, guarda credenciales inventadas para HYUNDAI y MAERSK en `usuario1` y en un operador nuevo.
4. Corre «Solo iniciar sesión» (`ejecutar_login`, que lee `config.json` como el panel) con un Playwright falso. Su
   página anota cada dirección a la que va y cada objetivo que busca, y no tiene ningún elemento.

Su control: el mismo camino, con la `url` de HYUNDAI que trae este equipo, tiene que ir a ella, y va. Ningún efecto
real: 0 intentos de abrir un navegador, un proceso o la red.

| Operador | `hyundai/url` en `config.json` | Primera dirección de HYUNDAI | Primera de MAERSK |
|---|---|---|---|
| `usuario1`, de la plantilla (`usuario2` trae lo mismo) | `https://www.hmm21.com/` | **`https://www.hmm21.com/`** | `https://www.maersk.com/book/` |
| uno nuevo, creado desde Credenciales | sin la llave | `https://www.hmm21.com/e-service/auth/login.do` | `https://www.maersk.com/book/` |
| control: la de este equipo | `https://www.hmm21.com/e-service/auth/login.do` | `https://www.hmm21.com/e-service/auth/login.do` | — |

En la página sin elementos, el login de HYUNDAI hizo estos cuatro pasos:
1. Esperó el campo del usuario.
2. Intentó escribir el usuario y la clave.
3. Buscó para pulsar `button:has-text('Login'), a:has-text('Login'), input[type='submit']`.
4. Esperó el tablero, y dio la sesión por no iniciada.

Con una página que trae algo para ese selector, lo pulsó: es el primero de un selector genérico, sea lo que sea. El
resultado de MAERSK con la página falsa no dice nada: solo cuenta su dirección.

## Lo que dice `logs/` de este equipo

Con `logs_hyundai.py`, que no imprime nombres de carpeta, solo la fecha. Universo: 46 `log.txt`, todos leídos (0 sin
poder leer). Tienen 22 inicios de sesión de HYUNDAI, del 21-09 al 15-10, y ninguno sin su línea «URL:». Su control: hay
logins con la sesión iniciada.

- **Los 22 terminaron dentro de e-service con la sesión iniciada:** 21 en `e-service/general/DashBoard.do`, y uno, el
  21-09, en `e-service/general/login/pwChange2.do`.
- **En los 22 encontró el campo del usuario** (`campo OK '#userId…'`) y pulsó el «Login» del formulario.
- **Ninguno encontró una sesión ya abierta** («Ya había una sesión activa.»: 0). El perfil de Chrome no se saltó el
  login en ninguno: no es lo que decide la página.
- **`log.txt` no anota la primera dirección del login:** `reg.url` va solo al final. Por eso, en el equipo del colega,
  lo que delata la portada es `campo ERROR '#userId…'`, y la última línea «URL:» del login, con `hyundai_final.png`.

## Los archivos ignorados o sin seguimiento que el programa usa al correr

| Archivo | Para qué | ¿Decide la página? |
|---|---|---|
| `config.json` | lo lee cada corrida: credenciales, opciones y la `url` de HYUNDAI. El panel web lo crea desde la plantilla si falta | **sí, la del login de HYUNDAI** |
| `perfiles/<operador>/` | el perfil de Chrome, con sus cookies y sesiones: uno por operador, nuevo para un operador nuevo | no: decide si ya hay una sesión abierta (aquí, 0 de 22) |
| `logs/` | cada corrida escribe ahí; el panel lee `logs/actualizacion.json` (su aviso al abrir) y la poda borra el HTML viejo | no |
| `Reservas AQUASHIELD.xlsx` (o `Planilla_Estandar_AQUASHIELD.xlsx`, `Agendamientos.xlsx`) | la planilla del modo consola | no |
| `%TEMP%\aquashield_planilla.xlsx` y `aquashield_read_*` | la copia de la planilla que se sube al panel, fuera de la carpeta | no |
| `*_dump.html` en la raíz | lo escribe el reconocimiento de MSC (`_guardar_html`); no se lee | no |

- **No los usa el programa:** los generadores, los videos, los manuales, el logo y `revision_local/`. No los nombra
  `AQUASHIELD.py`, ni `actualizar.py`, ni los `.bat`.
- **Fuera de la carpeta:** Chrome instalado, o el Chromium de Playwright, y los paquetes `playwright`, `openpyxl` y
  `holidays`.

## Lo decides tú

La condición de freno se cumple para la opción 1: cambia qué trae `config.example.json`.

1. **Cambiar la plantilla:** que la `url` de HYUNDAI sea la del login, o quitar la llave (y la de MAERSK, que no se
   usa).
   - Arregla los clones que se hagan desde ahora.
   - No arregla un `config.json` ya creado: el panel solo lo crea si falta, y el del colega seguiría con la portada.
2. **Cambiar el programa, sin tocar la plantilla:** que `login_hyundai` vaya siempre a su login, como ya hace MAERSK,
   que no lee su `url`.
   - Arregla también los `config.json` ya creados, el del colega incluido.
   - La llave `url` de HYUNDAI dejaría de usarse.
   - No cambia lo que el equipo del colega ve al abrir el lanzador: cambia adónde va el login de HYUNDAI.
   - Llega a los colegas cuando avances `estable`. Es código: lo haría en un ciclo, con su prueba y su mutación, si me
     lo pides.
3. **Sin cambiar nada, para el colega hoy:** dos caminos.
   - Crear su propio operador en Credenciales y escribir ahí sus claves. Ese operador nace sin la llave `url`, y su
     perfil de Chrome también es nuevo.
   - O cambiar en su `config.json` la `url` de HYUNDAI por la del login.

**Mi recomendación: la 2.** Arregla al colega que ya clonó y a los que vengan, sin tocar la plantilla. Si además quieres
la plantilla limpia, la 1 también.

**Después del login, el colega va a llegar al contrato.** Sin un contrato de HYUNDAI en sus credenciales ni en
`contratos_por_defecto`, la reserva queda NO ENVIADA en «Contract No» (decisión del encargo 44). Credenciales tiene un
campo «contrato» por naviera.

## Premisas del encargo

- **«La dirección de HYUNDAI, o algo que decide a qué página entra, sale de `config.json`»:** confirmada para la del
  inicio de sesión, por la llave `url`. La de reservas no: está escrita en el programa.
- **«…o de un archivo ignorado o del perfil de Chrome»:** el perfil no decide la dirección. Aquí, ninguno de los 22
  inicios de sesión encontró una sesión ya abierta.
- **«En un clon limpio cae en la página general»:** confirmada en el camino del programa para `usuario1` y `usuario2`, y
  refutada para un operador nuevo, que va al login. Qué muestra la portada, sin medir.
- **«No tiene `contratos_por_defecto` ni el código de Shipper»:** tiene las llaves, vacías. El efecto es el mismo.
- **«El código es idéntico en los tres lados»:** confirmada, `a2998b0`.

## Residual

- **Qué muestra y adónde lleva la portada de HMM, sin medir.** Se reabre con el `log.txt` del colega:
  `campo ERROR '#userId…'`, lo que dice la línea del clic en «Login», la última «URL:» del login y `hyundai_final.png`.
  También se reabre con una corrida tuya con `usuario1` de la plantilla.
- **Propuesta: el clic del login de HYUNDAI.** Pulsa el primero de un selector genérico: un botón o enlace «Login», o
  cualquier `input[type=submit]`. Si no, pulsa por JavaScript el primer elemento cuyo texto es «log in».
  - En la página del login es su botón. En otra página, cualquiera.
  - La regla de los clics a ciegas vale para las reservas antes de la guarda, y no alcanza a los inicios de sesión.
  - El de MSC ya pulsa solo por su texto (`CICLO-cierre-de-frenos.md`).
  - Se reabre si lo encargas.
- **Propuesta: el contrato de HYUNDAI en Booking Details.** Si el contrato configurado no está entre las opciones,
  elige la primera real, por su posición (`Contract No (primera real)`).
  - No lo dicen `CLAUDE.md` ni las pruebas.
  - En `logs/` no pasó nunca: 0 de 53 líneas «Contract No». En 17, el contrato se eligió por su texto.
  - Se reabre si lo encargas.
- **Sin uso:** la llave `url` de MAERSK, `_login_portal` y `opciones/espera_seg`. Se reabre si lo encargas.

## Defectos de instrumento y errores míos

- **Imprimí un número de contrato de HYUNDAI en la consola de esta sesión.** Contaba las líneas «Contract No» de
  `logs/` cortadas a 40 caracteres, y el número cabía. No quedó en ningún archivo del repo ni de la carpeta del encargo.
  Desde ahí, conté por el texto fijo de cada línea, sin su valor.
- **En el borrador de este informe, dos datos estaban mal.** Le atribuí a CMA-CGM un comentario del código de COSCO
  («el portal rellena el primer contrato de la cuenta»), y conté 22 lecturas de `creds` con un patrón que no veía
  `(creds or {})`. Son 25. Lo vi al revisar el informe contra el código, antes del commit.
- **Un `python -c` con barras invertidas falló en Git Bash:** la herramienta junta los pares de barras (fila de
  «Entorno»). No cambió nada: lo escribí en un archivo, `copiar_de_e69.py`.

## Re-medir

Todo corre desde `scratchpad\e70`, en Git Bash, después de `source entorno_e70.sh`. Ningún script imprime usuarios,
claves, contratos ni nombres de operador.

| Número | Script |
|---|---|
| La forma de `config.json` y de la plantilla, y sus llaves `url` | `python forma_config.py` |
| La primera dirección de HYUNDAI y de MAERSK en un clon nuevo, por el panel | `python sonda_login_clon.py` |
| Los 22 inicios de sesión de HYUNDAI en `logs/` | `python logs_hyundai.py` |
| Las direcciones y las lecturas de `creds` | `grep -n -o -E 'https?://[^ "]+' AQUASHIELD.py` y `grep -n -E 'creds\.get\(\|creds\[\|\(creds or \{\}\)' AQUASHIELD.py` |
| La suite, aparte | `python lanzar_suite_e70.py` |

## NO retroceder

No hay cambio de código que retroceder. Lo que no hay que deshacer al arreglarlo:
- **La página de reservas de HYUNDAI va escrita en el programa:** no pasa a depender de `config.json`.
- **El panel crea `config.json` desde la plantilla, byte a byte** (encargo 61). Un arreglo que cambie la plantilla no
  cambia esa copia.

## Reglas de método aplicadas

`metodo-ciclo` v28 (la v26 estaba cargada al empezar; la volví a invocar antes de medir) y las reglas del módulo
(`CLAUDE.md`). No chocaron entre sí.

- **Paso 0:** el registro barrido por el tema. La `url` de la plantilla aparece solo en `CICLO-repo-inicial.md`, donde
  la limpieza de la plantilla comprobaba que no cambiara ninguna `url`. Ningún informe dice qué hace con el login de
  HYUNDAI. Veredicto: **PREGUNTA**. La causa está medida; el arreglo lo decides tú.
- **Al abrir:** lo publicado comparado con su registro, y las librerías del HTML (arriba).
- **Control positivo que aborta,** en las tres sondas: la `url` de la plantilla, la dirección de este equipo por el
  camino del panel, y un login con la sesión iniciada en `logs/`.
- **Todo salto silencioso con su contador:** 0 `log.txt` sin poder leer y 0 inicios de sesión sin su línea «URL:».
- **La unidad la fija el sujeto:** cada inicio de sesión de HYUNDAI, no cada carpeta de corrida.
- **Sobre el camino real:** el programa entero en una copia, con su panel creando `config.json` y «Solo iniciar
  sesión» leyéndolo. No llamé a `login_hyundai` con unas credenciales armadas a mano.
- **Antes del commit, todas las suites:** la suite completa sobre la base, con el resultado abajo. El commit suma solo
  este informe y `CLAUDE.md`. Comprobé que ninguna prueba los lee: de los `.md`, la suite lee solo `LEEME.md`, que no
  cambia, y la foto de los originales mira sus bytes, no su contenido.
- **Rutas absolutas y ningún comando detrás de un `cd`;** el temporal de todo lo que corrió, en `e70\t`; la limpieza del
  cierre, dentro de la carpeta que borra, probada antes con un testigo.
- **Del módulo:** ningún portal, `config.json` sin tocar, ninguna prueba que importe `AQUASHIELD.py` desde la raíz,
  nunca el puerto 8765, la sonda de secretos y el barrido antes del commit, y el correo noreply.
- **Sin Modo autónomo:** diagnóstico sin arreglo, y sin revisiones. No hubo cambio de código que revisar.

## El repo

Un commit en `main`, sin push: el repo es público, así que el push lo haces tú.

- Trae este informe y, en `CLAUDE.md`, de dónde sale la dirección del login de HYUNDAI.
- Lleva de autor y de committer el correo noreply del repo.
- Antes del commit, la sonda de secretos dio 0, y el barrido de datos reales dio 0, en las líneas agregadas y en el
  mensaje del commit.
