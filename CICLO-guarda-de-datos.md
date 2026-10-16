# Encargo 72 · El repo público, sin razones sociales de clientes, y una guarda que no las deja volver

**Base:** `C:\dev\Agendamiento Reservas` @ `bccaf67` · árbol limpio al empezar.

Cambio de código en **Modo autónomo**, con `metodo-ciclo` v29. La sesión traía cargada la v28, así que volví a invocar
la skill antes de medir. No se abrió ningún portal, y `config.json` solo lo leyó la sonda de secretos.

**Al abrir el ciclo:**
- **Ninguna otra sesión trabajaba en el repo** (el primer FRENA del encargo):
  - las 4 sesiones activas tienen su carpeta en otros módulos (Termógrafo, Validador HC, Second Brain y Fresco);
  - ningún proceso nombra el repo en su línea de comandos, salvo el de la propia consulta;
  - y ningún archivo de la carpeta cambió después del último commit: 0 de 5.616. El control: con la hora de ayer a las
    22:00, la misma sonda ve los 5 del encargo 71.
- **Lo publicado contra el registro:** `ls-remote` da `main` y `estable` en `bccaf67`, el informe 71. Ya lo subiste y
  avanzaste `estable`, como vio la auditoría.
- **Ninguna librería de terceros viaja en el HTML del panel:** no hay avisos de seguridad que consultar.
- **La auditoría, medida otra vez:** una copia de su `datos_reales.py` sobre `HEAD` da lo mismo que su informe:
  - 14 razones sociales, todas en `tests/test_clics.py`;
  - el nombre del dueño en 3 archivos, publicado por tu decisión (encargo 44);
  - y un «correo» que es el usuario y la clave inventados de una dirección de prueba, que ella ya descartó.

## En resumen

- **Las dos razones sociales ya no están en `HEAD`.** Eran las otras partes del buscador del Shipper de MAERSK, en dos
  pruebas de `test_clics`. Pasaron a «PARTE UNO» y «PARTE DOS», con una nota que dice que son inventadas, y las pruebas
  siguen mordiendo.
- **Una guarda de datos reales, en la suite y en un hook pre-commit:** `tests/guarda_datos.py`. Es la guarda de razones
  sociales de Carga NEPPEX, portada a Python, con los datos de este programa que tienen forma de dato real. Dice el
  tipo, el archivo y la línea, nunca el valor.
- **Antes y después, con la guarda final:** la base daba 67 hallazgos y `HEAD` da 0.
  - 14 son las dos razones sociales.
  - 47 son números de reserva inventados de las pruebas. Medí que no son reales y los reescribí con las cifras a la
    vista.
  - 6 son falsos positivos de la forma jurídica, que reescribí.
- **La propia empresa se queda, como excepción declarada:** «AQUACHILE S.A.», como la escribe el programa en los
  formularios. Pasan también, por valor exacto, el nombre del dueño y su correo noreply (encargo 44).
- **La historia publicada todavía trae los dos nombres,** desde el 01-10. Sacarlos es reescribir la historia de un repo
  público, y eso lo decides tú (abajo, en «Lo que decides tú»).
- **No se activó ningún FRENA:**
  - ninguna otra sesión trabajaba en el repo;
  - y no apareció otro dato real en lo versionado: los 47 números de reserva no están en ninguno de los 1.396 archivos
    que el programa dejó en este equipo, que sí traen 15 números reales con esa forma.
- **Las dos revisiones** no encontraron nada CRITICAL ni HIGH. Arreglé sus 8 MEDIUM y los LOW baratos, cada uno con su
  prueba y su mutación. La de código dijo «APROBAR CON CAMBIOS», y esos cambios son el segundo commit.
- **Tres commits en `main`, sin push:** el repo es público, y entrego el bloque. `estable` no se movió.

## Las dos razones sociales

Estaban en `test_js_casilla` y `test_js_shipper`, de `test_clics.TestMaersk`: 14 apariciones en 12 líneas, entre la 8646
y la 8756. La auditoría contó 15 en 13 con su expresión, que ve una tercera forma, de 6 caracteres; la guarda de este
encargo ve las mismas dos que el barrido del coordinador.
- Hacen de **otras partes** en la lista del buscador de partes: resultados que no son AQUACHILE. Nada en el código
  depende de su texto, salvo que no traigan a AQUACHILE como palabra entera.
- **Pasaron a «PARTE UNO» y «PARTE DOS», sin forma jurídica:** como en NEPPEX, ni una razón social inventada pasa la
  guarda. Una nota en cada prueba dice que son inventadas y por qué.
- Las dos pruebas siguen con sus mismos casos y sus mismas salidas esperadas, y pasan. Sus 25 y 24 mutaciones siguen
  mordiendo, todas (lo midió la revisión de código; y en el censo del área, abajo).
- El cambio no imprimió los nombres en ningún momento: los reemplazó un script que los encuentra con la guarda y valida
  las 14 apariciones antes de escribir.

## La guarda

`tests/guarda_datos.py`. Su docstring trae todo lo que sigue, con sus límites.

**Qué busca,** en el texto y en el nombre de cada archivo:
- una **razón social**: un nombre seguido de una forma jurídica, o precedido de una de las que van delante. Es la guarda
  9 de NEPPEX (`tools/armar-pages.mjs` en `0b47898`), portada a Python con sus mismas formas, separadores y nombre;
- un **RUT** o un **contenedor** con su dígito bien calculado (módulo 11 e ISO 6346);
- un **correo** y un **teléfono chileno**;
- un **número de reserva** con la forma con que el programa lo lee: SCLG, EBKG o SCLA y 8 cifras (`FORMA_BOOKING`);
  9 cifras que empiezan con 27 (MAERSK, en `_extraer_bkg_limpio`); o 9 cifras detrás de «Booking number»;
- un **BL**, un **pedido** de AquaChile y una **IP** pública;
- un **nombre con su apellido**: un nombre de pila de la lista de la auditoría y una palabra con mayúscula.

Frena también **un archivo binario**, que no puede leer. Y un archivo cuyo nombre trae un dato sale en el informe como
«‹un nombre con un dato›», con su carpeta.

**Lo que pasa,** declarado y con su contador al lado del resultado:
- **Por valor exacto (`PERMITIDOS`; la suite fija la lista):** «AQUACHILE S.A.»; el nombre del dueño como autor de los
  commits, y completo, como en el pie del panel; y su correo noreply. Un nombre ajeno escrito delante del propio frena,
  igual que el propio en una frase que empieza con mayúscula, o con otra palabra pegada: se reescribe el texto, y la
  lista no crece.
- **Un número inventado,** solo con las cifras a la vista: todas iguales, o seguidas de a una (de MAERSK, las 7 que
  siguen al 27).
- **Un correo de un dominio reservado** para ejemplos (`.invalid`, `.test`, `example.com`…), y el usuario y la clave de
  una dirección (con «://» en el mismo token), que mira la sonda de secretos.
- **Una IP** que no es pública.
- **Por propiedad:** la tipografía PT Sans, un nombre de una sola letra, letras sueltas (el logo del panel Tkinter,
  «A Q U A S H I E L D») y una lista de formas separadas por comas.

**Lo que no ve:** un nombre de cliente sin forma jurídica o en minúscula, una nave, un viaje, un contrato, una dirección
postal, un número de reserva de CMA-CGM o de COSCO, y un dato pegado a otra palabra, partido en dos líneas o armado en
el código. La lista entera está en el docstring.

**Lo que cambié del modelo de NEPPEX, y por qué:**

| Cambio | Por qué |
|---|---|
| Mira todo lo versionado, no una página | Acá se publica el repo entero |
| La propia empresa entre comillas, «» o detrás de un signo se aparta antes de buscar | En el código va pegada a un identificador (`COSCO_SHIPPER = "AQUACHILE S.A."`), y el nombre de la regla la tomaba entera. Detrás de un espacio, no se aparta |
| La tipografía PT mira solo la palabra que sigue | NEPPEX mira las cinco que siguen; en un comentario del CSS del panel, la frase de la línea de abajo empieza con mayúscula |
| Letras sueltas y lista de formas, por propiedad | El logo del panel, y las listas de formas de la propia guarda y de su documentación |
| Las formas de la propia guarda, entre dos marcas de su archivo, no cuentan para la razón social | Escritas, son su propio hallazgo. Solo ahí, solo esa regla, y la suite fija el bloque por su huella |
| Se apartan el base64 y los hashes | El base64 de las tipografías forma palabras al azar, y un hash da un número con forma de pedido (NEPPEX lo midió) |
| NFC antes de buscar, y Windows-1252 si no es UTF-8 | El `re` de Python no tiene la clase de las marcas combinantes que usa NEPPEX |
| Los otros datos, además de la razón social, y un binario frena | Son los de este programa: números de reserva, contenedores, correos |

## Antes y después

La guarda final, sobre un clon de la base (`bccaf67`) y sobre lo que versiona `HEAD`:

| Tipo | Archivo | Antes | Después |
|---|---|---|---|
| razón social | `tests/test_clics.py` | 17: las dos de la auditoría (14) y la ruta inventada de tres pruebas (3) | 0 |
| razón social | `tests/mutaciones.py` | 2: la variable `JSC` | 0 |
| razón social | `AQUASHIELD.py` | 1: la sigla de una aplicación de una sola página, en un docstring | 0 |
| número de reserva | `tests/test_booking.py` | 37 | 0 |
| número de reserva | `test_envio`, `test_web`, `test_consola` y `test_planilla` | 10 | 0 |
| **total** | | **67** | **0** |

Sobre `HEAD`, además: 104 archivos leídos, 0 binarios, 0 descartados y 0 ausentes. Pasan, por valor exacto, la propia
empresa 18 veces, el nombre del dueño 5 y su correo 3. Pasan, declarados, 47 números inventados a la vista y los saltos
por propiedad de su docstring, cada uno con su contador.

## Lo que la guarda frenaba y no era un dato real

- **Los 47 números de reserva de las pruebas son inventados.**
  - `test_booking.py` lo dice («Números inventados con la forma medida»).
  - Lo medí: los 25 números de las pruebas con esa forma (los de 8 cifras, sus variantes de 7 y 9, y los de MAERSK)
    no están en ninguno de los 1.396 archivos de texto de `logs/` ni en las 2 planillas de la carpeta. El control:
    esos archivos traen 15 números reales con la forma medida, y la búsqueda encuentra el primero.
  - Pasaron a números con las cifras a la vista, con su misma forma y su mismo largo: 14 distintos de 8 cifras y 5 de
    MAERSK, en 51 reemplazos. Cada número viejo pasó a uno nuevo distinto, en todas sus apariciones.
- **Seis falsos positivos de la forma jurídica,** reescritos como hace NEPPEX, sin aflojar la regla:
  - en tres pruebas, la ruta inventada `ruta=A-B`, que para la guarda es una forma de dos letras. Pasó a `ruta=A-C`,
    del mismo largo;
  - una variable `JSC` en `mutaciones.py`, una forma que va delante. Pasó a `JS_LISTA_COSCO`;
  - la sigla de «aplicación de una sola página» en un docstring de `_mk_paso_actual`, que es la de una sociedad por
    acciones. Ahora dice las palabras.

## El hook

`.githooks/pre-commit` y `.githooks/pre-merge-commit`, los de NEPPEX con esta guarda en lugar de su regla de pedidos.
- Corren `python -I tests/guarda_datos.py --pre-commit`, que lee **solo el índice que git le pasa al hook**
  (`GIT_INDEX_FILE`), con `git commit -a` o con rutas también, después de sus controles.
- **Fallan cerrados:** sin `python`, sin la guarda, sin el índice, con un detector roto, con una entrada que no se puede
  leer o con un binario, frenan. Cada caso tiene su prueba.
- **No viajan en el clon:** se activan una vez por clon, con `git config core.hooksPath .githooks`. En este equipo
  quedaron activados, y los commits de este encargo pasaron por él.
- **`core.hooksPath` es relativo al árbol abierto:** en una rama sin `.githooks/` (como `historial-local`) el hook no
  corre, y git no avisa. Está declarado en el hook y en `CLAUDE.md`.
- Van en LF, en ASCII y ejecutables (`100755`), como los de NEPPEX.
- **No corren la sonda de secretos:** ella necesita `config.json`, y un clon sin él frenaría todo commit. Se sigue
  corriendo a mano antes de cada commit; `CLAUDE.md` decía que «bloquea», y ahora dice cómo es.

## Las pruebas y su censo

`tests/test_guarda_datos.py`, 19 pruebas:
- **el detector:** sus 48 muestras dan cada una lo suyo; cada forma de las listas y cada separador frenan; los dígitos
  verificadores coinciden con un cálculo aparte; la lista de permitidos está fija y sale del programa (el Shipper de
  COSCO y el pie del panel) y de `CLAUDE.md` (el autor); el bloque de las formas está fijo por su huella; y el informe
  nunca trae un valor, tampoco el de un nombre de archivo;
- **la lectura:** un repo inventado con un caso de cada forma de entrar (lo seguido, lo nuevo, lo que el índice guarda
  distinto, lo borrado, lo ignorado, un binario, UTF-16, Windows-1252, un nombre de archivo y una unión que sale del
  repo), y la lectura del índice, con uno aparte como el de `git commit -a`;
- **los límites:** un git que no termina se mata con su árbol y la guarda no se queda esperando; y un archivo hecho para
  colgarla (una tira larga de espacios y 20.000 hallazgos) no la cuelga;
- **lo versionado:** la guarda sobre lo que git versionaría da 0 hallazgos y 0 binarios, y tiene que ver a la propia
  empresa en el programa (si no la ve, dejó de leer);
- **el hook, con commits de verdad** en un repo inventado: frena un commit con una razón social, deja pasar uno limpio,
  lee el índice que se commitea y no el árbol, frena el commit de un merge, frena sin la guarda o sin `python`, va en LF
  y en ASCII, y `.gitignore` lo versiona.

**44 mutaciones nuevas** (`e72-`), cada una con las pruebas que tiene que tumbar.
- **El censo del área, sobre el primer commit:** 209 mutaciones y 278 pares. Entran:
  - las 21 mutaciones de ese commit;
  - las que nombran una prueba cuyo método cambió (87);
  - las que caen a 15 líneas o menos del cambio de `AQUASHIELD.py`, o nombran las fotos que leen el texto del programa
    o `test_candado` (96);
  - y las que nombran la variable renombrada (6).

  Muerden los 278, y la foto de los originales del clon (82 entradas) no cambió: RESULTADO OK.
- **Las 44 del encargo, sobre el árbol del segundo commit, antes de commitearlo:** 50 pares. Muerden los 50, y la foto
  de los originales del repo (5.578 entradas) no cambió: RESULTADO OK.
- **El chequeo de las 2.418 mutaciones del archivo da 0 problemas:** cada texto viejo aparece una vez, ningún id se
  repite, y cada una de las 853 pruebas tiene su mutación.

## Las revisiones

Una de seguridad y una de código, sobre `bccaf67..80345b9`.
- Cada una trabajó sobre un **clon de verdad, sin remoto** (`e72\clon`), como pide la v29. Arrancó en su worktree,
  que el arnés creó otra vez en `bccaf67`, sin correr nada ahí. Leyó el clon, y corrió las pruebas con un script que no
  usa git (`correr_en_clon.py`).
- El cambio les llegó como archivo (`cambio72.diff`), con las dos razones sociales que salen tapadas. Las 14 las tapó
  un script que las ve con la guarda, y su control exige las 14 en 12 líneas.
- Las dos dejaron su worktree limpio (`status` vacío), y el clon, sin remoto.

**Ninguna encontró nada CRITICAL ni HIGH.** La de código: «APROBAR CON CAMBIOS».

| Hallazgo | De | Severidad | Qué hice |
|---|---|---|---|
| Un nombre de archivo con un dato salía entero, en el informe, el hook y la suite | las dos | MEDIUM | arreglado: «‹un nombre con un dato›», con su carpeta; prueba y mutación |
| Un binario pasaba contado, sin frenar (una planilla comprimida con una razón social adentro, un PDF) | seguridad | MEDIUM | arreglado: frena, y la suite exige 0 binarios |
| Un correo pegado a «:» pasaba como el usuario de una dirección | las dos | MEDIUM | arreglado: pide «://» en el mismo token; muestra y mutación |
| El plazo de git no se cumplía con un hijo vivo: 300 s con un plazo de 4 | seguridad | MEDIUM | arreglado: taskkill del árbol, y la última lectura con plazo; prueba con un proceso falso |
| La expresión de la etiqueta de reserva retrocedía sin fin con una tira de espacios: 64.000, 46 s | seguridad | MEDIUM | arreglado: los espacios con tope; prueba |
| `dv_rut` sin un guardián aparte: la muestra usaba el mismo cálculo | código | MEDIUM | arreglado: contra un cálculo aparte y valores conocidos; lo mismo con ISO 6346 |
| La falla cerrada del hook y de la guarda, sin prueba | código | MEDIUM | arreglado: sin `python`, sin la guarda, sin índice y con el detector roto, cada una con su prueba y su mutación |
| Las formas y los separadores, casi sin muestra | código | MEDIUM | arreglado: una prueba con cada forma y cada separador |
| La revisión era cuadrática con muchos hallazgos: 60.000, 46 s | seguridad | LOW | arreglado: las líneas se cuentan una vez |
| El hook corre la guarda del árbol abierto, no la de HEAD, y sin `python -I` | seguridad | LOW | `-I`, sí; lo de HEAD, al residual |
| `core.hooksPath` relativo al árbol abierto; el hook es opcional; sin `commit-msg` ni `pre-push` | las dos | LOW | declarado en el hook y en `CLAUDE.md`; lo demás, al residual |
| Lo que el detector no ve: minúsculas, Windows-1252, invisibles, iniciales, permitidos con algo pegado, el teléfono con 0, datos pegados | las dos | LOW | arreglados los baratos (Windows-1252, invisibles, iniciales, permitidos exactos, teléfono con 0); el resto, declarado en el docstring |
| La suite necesita un repo de git de verdad | código | LOW | declarado en `CLAUDE.md` |
| Líneas de más de 120 caracteres | código | LOW | arreglado |
| Guardianes chicos: la línea del hallazgo, cifras iguales, el `except ValueError` de la IP, las marcas, la línea de `.gitignore` | código | LOW | arreglado: cada uno con su caso |
| El bloque entre las marcas no se revisa | código | INFO | fijado por su huella en la suite |
| La NFC, sin su porqué | código | INFO | declarado |
| Un nombre con salto de línea desalinearía `_lote` | seguridad | INFO | no se puede crear en Windows, y el hook lee por sha; queda |
| El diff, limpio | seguridad | INFO | — |

**Lo que corrió cada una:**
- **Seguridad:** las 11 pruebas de la guarda en el clon; sondas del detector con valores inventados; más de 40 casos de
  rendimiento, cada uno en un proceso aparte y con plazo; el hook sobre repos inventados en una ruta con espacios; y la
  guarda sobre los 104 archivos del clon: 0.
- **Código:** las pruebas del área en el clon (234 OK); el censo de las 21 mutaciones de entonces (27 pares, todos
  muerden) y el de las dos pruebas del buscador (25 y 24, todas muerden); unas 70 mutaciones propias en proceso; y el
  hook en 8 escenarios (subcarpeta, commit parcial, `--amend`, worktree, borrado, tildes y espacios, 200.000 líneas y
  un merge).

## Decisiones que tomé solo

| Decisión | Por qué |
|---|---|
| Los nombres inventados van sin forma jurídica | Como en NEPPEX: ni una razón social inventada pasa la guarda, y la prueba no la necesita |
| La guarda busca también los datos de este programa, no solo razones sociales | El encargo pide datos con forma real, y los números de reserva son el dato real más propio del programa |
| Los números inventados de las pruebas pasan a cifras a la vista | Con la guarda, un número con forma de reserva frena salvo que se vea inventado. Antes medí que no eran reales |
| Las excepciones son cuatro, por valor exacto | La propia empresa, como pide el encargo, y el nombre y el correo del dueño, publicados por tu decisión del encargo 44 |
| Seis falsos positivos se reescribieron en el texto, sin aflojar la regla | Es lo que hace NEPPEX, y cada uno es una palabra o una sigla |
| Las desviaciones del detector de NEPPEX (la tabla de arriba) | Cada una con su porqué; NEPPEX mira una página, y acá es el repo entero |
| Un binario frena | La guarda no lo puede leer, y el repo es público. Hoy no hay ninguno |
| El hook no corre la sonda de secretos | Necesita `config.json`; `CLAUDE.md` ahora lo dice |
| El hook corre la guarda del árbol abierto, no la de HEAD | Como NEPPEX. El hook no es una barrera contra quien commitea: `--no-verify` lo saltea. Va al residual |
| Activé el hook en este equipo | Sin eso, el hook está pero no corre; es la configuración local del repo (`core.hooksPath`) |
| Arreglé los MEDIUM de las revisiones y los LOW baratos | Es técnico y reversible, y cada uno lleva su prueba |
| Corregí el voseo de `.gitignore` («agregalo») | Estaba en un archivo que el encargo ya tocaba |
| No reescribí la historia | Es pública e irreversible en el remoto: lo decides tú |

## Lo que el cambio no toca

- **Lo que hace el programa:** en `AQUASHIELD.py` cambia una palabra de un docstring. Ningún reservador, ningún login y
  ningún paso del panel cambian.
- **`test_candado`:** no está en el diff, y pasa.
- **Los datos de la empresa en los formularios** se quedan, como excepción declarada.
- **La historia publicada** (abajo).

## Antes de cada commit

Desde este encargo la suite lee todo lo versionado, este informe también: por eso corrió completa antes de cada uno de
los tres commits, sobre su árbol.

- **El arreglo (`80345b9`):**
  - la suite completa: 845 OK, sin cambios en los 5.578 originales. Corrió dos veces: la primera antes de sacar de la
    guarda la palabra del operador (en mis errores), y la segunda sobre el árbol final;
  - la guarda, a mano y en el hook: 0 hallazgos;
  - la sonda de secretos: 0 en seco y después del `git add`;
  - el barrido por valor: 8 líneas, todas solo con la palabra «chile» (de «chileno» y «AquaChile»), que es parte de
    una nave de `logs/`. Lo medí línea por línea, sin mostrar valores. En el mensaje, 0.
  - El censo del área corrió después, sobre un clon de este commit (arriba).
- **Lo de las revisiones (`ea4f774`):**
  - la suite completa: 853 OK, sin cambios en los 5.578 originales;
  - el censo de las 44 mutaciones del encargo: 50 de 50 pares;
  - el chequeo de las 2.418 mutaciones: 0 problemas;
  - la guarda y el hook: 0 hallazgos; la sonda de secretos: 0 y 0; el barrido: 0 en las 426 líneas y en el mensaje.
- **Este informe:** la suite completa, sobre el árbol con él: 853 OK, sin cambios en los originales. La guarda, la sonda
  de secretos y el barrido, sobre él y su mensaje: 0, salvo 10 líneas del barrido, solo con la palabra «chile».

En los tres mensajes, la guarda ve solo la línea `Co-Authored-By`, con el correo noreply de Anthropic. Es la atribución
que pide la herramienta y no es un dato de una persona; la guarda no lee los mensajes (no hay `commit-msg`).

## Premisas del encargo

- **«2 razones sociales en una prueba, usadas como distractores»:** confirmada. La auditoría contó 15 apariciones en 13
  líneas con su expresión; la guarda ve 14 en 12, de las mismas dos.
- **«Sin declararse inventadas»:** confirmada. Nada en el registro ni en la prueba lo decía.
- **«Modelo: Carga NEPPEX 0b47898»:** su hook frena números de pedido, no razones sociales; su guarda de razones
  sociales mira solo la página publicada. Porté las dos piezas: el hook y la lectura del índice de un lado, y el
  detector de razones sociales del otro.
- **«Que no puedan volver a entrar»:** cumplida en lo que la guarda ve. Lo que no ve está arriba y en el residual.

## Lo que decides tú

- **La historia publicada todavía trae los dos nombres.** Entraron en `main` con el commit huérfano `7b33924`, el
  01-10, y están en cada commit hasta `bccaf67`. Sacarlos es reescribir la historia de `main` y de `estable` en un repo
  público:
  - un push forzado, que los clones de los colegas no aceptarían como avance rápido;
  - y GitHub puede haberlos guardado en su caché.

  Si lo decides, es un encargo aparte.

## Residual

- **Lo que la guarda no ve** (arriba, y entero en su docstring). Se reabre si aparece un dato así en lo versionado.
- **La lista de nombres de pila** es la de la auditoría, menos una palabra (abajo, en mis errores). Un nombre que no
  está en la lista no se ve.
- **El hook corre la guarda del árbol abierto** (LOW de la revisión de seguridad): una rama que la debilite se revisa
  con la guarda debilitada. Sacarla de HEAD es posible; se reabre si lo encargas.
- **Sin `commit-msg` ni `pre-push`:** los mensajes de commit, las ramas y las etiquetas no los mira la guarda. Los
  mensajes los barre el cierre de cada ciclo. Se reabre si lo encargas.
- **El hook no corre en `cherry-pick`, `rebase`, `revert` ni `am`,** como en NEPPEX: lo cubre la suite. Un dato
  commiteado con `--no-verify` y limpiado después queda en la historia, y la suite no lee la historia.
- **Los equipos de los colegas** reciben `.githooks/` sin activarlo; no commitean.
- **Lo que la auditoría dejó para este módulo y no es de este encargo:** el `cd tests && …` de `CLAUDE.md`, el puerto
  8770, los tiempos sin latido, el tamaño de `CLAUDE.md`, el manual viejo y la marca del panel. Cada uno se reabre si
  lo encargas.

## Defectos de instrumento y errores míos

- **Porté la lista de nombres de pila de la auditoría sin mirarla: traía una palabra del nombre del operador.**
  - La vio el barrido por valor antes del primer commit, y salió de la lista sin que se imprimiera.
  - No está en ningún commit. La primera suite corrió con ella, y la repetí sobre el árbol final.
- **Dos controles míos esperaban 13 líneas, y son 12:** copié la cuenta de la auditoría, que sale de otra expresión.
  Los dos abortaron, y los corregí con la mía.
- **El diff tapado para los revisores tapaba 10 de 14:** una cadena vacía (`''`) corría el emparejado de las comillas.
  Lo vio su control, que exige 14; lo arreglé, y su control final mira cada cadena.
- **El primer control del detector abortó:** el contador guardaba ceros, y las muestras salían «varios». Lo arreglé.
- **El reetiquetado de lo que viene del índice cambiaba también los hallazgos del árbol.** Lo vi leyendo, antes de
  correrlo, y lo arreglé.
- **Mi prueba del detector roto ponía la función nueva después del bloque que corre el hook,** y no actuaba. La prueba
  cayó, y la moví.
- **Usé `sort` de Git Bash** (Defender lo bloquea; dio «Permission denied» y no corrió nada) y **`awk` para medir el
  largo de las líneas** (cuenta bytes). Las dos filas ya están en «Entorno»; lo rehíce con Python.
- **Escribí cuatro veces por heredoc código con barras invertidas,** contra la fila de «Entorno». Dos dieron un aviso
  de Python (y el resultado salió bien, comprobado en el archivo), otra un reemplazo que no calzó, y otra, `sed` con
  una ruta de Windows, deformó la ruta del pedido a los revisores. Las cuatro las vio algo: el aviso, la aserción o la
  lectura del archivo.
- **Mi primer nombre nuevo para la variable de `mutaciones.py` ya existía.** La aserción del script lo frenó antes de
  escribir.
- **El primer cruce de los números corrió en primer plano** y pasó a segundo plano solo; terminó en unos 4 minutos.
- **Una sonda corrió git después de importar la máscara del barrido,** que trae el arnés de las pruebas y su trampa.
  Lo moví antes.
- **Git Bash murió al arrancar, una vez, cuando iba a commitear lo de las revisiones** («fatal error - add_item …
  errno 1»). No corrió nada del comando: lo comprobé con `git log` y `git status` desde PowerShell, y commiteé desde
  ahí. Lo sumé como fila en «Entorno» de `~/.claude/CLAUDE.md`.

## Re-medir

Todo corre desde `scratchpad\e72`, en Git Bash, con `TEMP`, `TMP` y `TMPDIR` en `e72\t`. Ningún script imprime un valor.

| Número | Script |
|---|---|
| Otra sesión en el repo | `python recientes.py <raíz> "<AAAA-MM-DD HH:MM>"` |
| La auditoría, otra vez | `python sondas_auditoria\datos_reales.py <repo> <salida> --revs HEAD`, y `contexto.py` |
| Dónde estaban las dos razones sociales, tapadas | `python ver_rs.py <repo> <rev> tests/test_clics.py 8600 8770` |
| Los números de reserva contra lo real | `python borrador\cruce72.py <repo> <rev>` |
| La guarda, a mano, y sobre la base | `python tests\guarda_datos.py`, y `python medir_antes.py` |
| La conversión | `python convertir72.py <raíz> [--escribir]`, `acortar72.py`, `quitar_operador.py <raíz> [--ver]` |
| `CLAUDE.md` | `python aplicar_claude72.py <raíz>` |
| Las mutaciones | `python mut_viejos.py <raíz>`, `alcance_e72.py <raíz> [propias]` y `lanzar_censo_e72.py <salida> <raíz> [propias]` |
| La suite, aparte | `python lanzar_suite_e72.py` |
| El barrido por valor | `python barrido\barrido_e72.py --cached`, `<rango>`, `--mensajes <rango>` o `--texto <archivo>`; `diag_barrido72.py` y `solo_chile.py` |
| La guarda sobre un texto | `python guarda_sobre.py <raíz> <archivo>` |
| El diff para los revisores | `python diff_tapado.py <clon> <base> <salida>` |

## NO retroceder

- **Ningún valor inventado con la forma de un dato real entra con otra forma:** las cifras a la vista y sin forma
  jurídica. La guarda frena los demás, en la suite y en el hook.
- **La lista de permitidos no crece con nombres de clientes.** La suite la fija contra el programa y `CLAUDE.md`.
- **El bloque de las formas no cambia sin cambiar su huella** en el mismo commit.
- **El hook no se saltea** salvo a propósito, con `--no-verify`.

## Reglas de método aplicadas

`metodo-ciclo` v29 (la versión del archivo; la sesión traía la v28, y volví a invocar la skill antes de medir) y las
reglas del módulo (`CLAUDE.md`).

- **Paso 0:** barrí el registro por el tema (la auditoría, su anexo, `CLAUDE.md` y la sonda de secretos). Veredicto:
  **CICLO**: el problema estaba medido, y el encargo ya decidía qué hacer.
- **Al abrir:** comparé lo publicado con su registro, y miré las librerías del HTML (arriba).
- **Re-medir contra HEAD antes de diseñar:** corrí otra vez la sonda de la auditoría, y calibré la guarda sobre `HEAD`
  antes de decidir sus excepciones.
- **Control positivo que aborta,** en cada sonda: el detector y sus muestras; la lectura y el índice, con repos
  inventados; el cruce de los números, que tiene que encontrar uno real; el barrido, con un valor vigilado; la medición
  de la base, que tiene que ver las 14 apariciones; y el diff tapado, que tiene que tapar las 14.
- **Todo salto silencioso con su contador:** cada cosa que pasa sale con su número, al lado del resultado.
- **Un dato en duda se trata como real:** las dos razones sociales, por el encargo; y los números de reserva, hasta
  medir que no lo eran.
- **Sobre el camino real:** la guarda corre sobre el repo de verdad en la suite, y el hook con commits de verdad.
- **El negativo muerde, de a uno:** cada mutación en su corrida del censo; el del área y el de las propias, con su
  alcance declarado.
- **El cambio y su guardián en la misma operación:** la guarda, sus pruebas, sus mutaciones y el hook van juntos.
- **Fuente única:** los permitidos se comparan contra el programa y `CLAUDE.md`; las formas de los ejemplos viven con
  las formas.
- **Cada reemplazo, una vez, y el EOL preservado:** cada texto viejo se contó antes de escribir; LF y 0 CR. La escritura
  fue en el mismo archivo, con el contenido ya validado y leído de vuelta (el plan B de «Entorno»: la app retiene
  archivos del repo).
- **Antes de cada commit, todas las suites:** el resultado de cada commit está arriba.
- **Los revisores, en un clon de verdad, sin remoto,** nunca en el repo vivo ni en su worktree (v29).
- **Rutas absolutas y ningún comando detrás de un `cd`;** el temporal en `e72\t`; la limpieza del cierre vive dentro de
  la carpeta que borra, y la probé antes con un testigo.
- **Una medición de tiempo, solo con el equipo a solas** (v29): este ciclo no da tiempos como medición. Corrieron
  otras 4 sesiones, y los tiempos que nombro (la suite, el hook) son solo de referencia.
- **Del módulo:** ningún portal; `config.json` solo lo leyó la sonda de secretos; ninguna prueba importa
  `AQUASHIELD.py` desde la raíz, ni usa el puerto 8765; la sonda de secretos y el barrido antes de cada commit; el
  correo noreply.
- **Choques:** ninguno entre `metodo-ciclo` y el módulo. Las reglas de ECC piden pytest y anotaciones de tipo; el
  módulo usa `unittest` y su propio estilo, y mandan las del módulo.

## El repo

Tres commits en `main`, sin push: el repo es público, así que subir publica, y entrego el bloque.

- **`80345b9`:** las dos razones sociales fuera, la guarda, sus pruebas, sus mutaciones, el hook, los valores
  reescritos, `.gitignore` y `CLAUDE.md`.
- **`ea4f774`:** lo de las dos revisiones.
- **El de este informe.**

Los tres llevan de autor y de committer el correo noreply del repo, y pasaron por el hook. `estable` no se movió:
llega a los colegas cuando la avances.
