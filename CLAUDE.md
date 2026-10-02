# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es

AQUASHIELD · Agendamiento de Reservas (AquaChile): robot que lee una planilla Excel de reservas y, con
Playwright sobre el Chrome instalado, entra a seis portales navieros (ONE, MSC, CMA-CGM, COSCO,
HYUNDAI/HMM y MAERSK), arma cada booking y devuelve la planilla con el estado y el N° de reserva.
Todo el programa vive en **un solo archivo, `AQUASHIELD.py` (~12 900 líneas)**. No hay
`requirements.txt` ni linter; hay una red de verificación offline en `tests/` (ver su sección).

## Git y GitHub

Repo git desde el 2026-09-23. **Se publica en GitHub como repo público,** `AquaShield-Team/Agendamiento-Reservas`, **sin
licencia: todos los derechos reservados** (decisiones de Marcelo, encargo 44, `CICLO-publicar-el-repo.md`).
- **Se publica solo `main`,** que empieza con un commit huérfano: el árbol limpio, sin el historial anterior. Su autor y
  su committer son `Marcelo Ramirez <269565694+1992MARS@users.noreply.github.com>`, el correo noreply de su cuenta de
  GitHub, que es público a propósito.
- **`historial-local` guarda el historial anterior** (del 2026-09-23 al commit del informe del encargo 44) y **nunca se
  sube, como ninguna etiqueta**: trae el nombre del operador hasta `9710ae2`, el correo de la empresa en cada commit y,
  en versiones viejas, los contratos, el código de Shipper de HYUNDAI, los generadores y la ruta del usuario de Windows.
  Los hashes de commit que citan este archivo, los `CICLO-*.md` y los comentarios del código hasta el encargo 44 son de
  esa rama: en GitHub no existen, y en este equipo se leen con `git show <hash>`.
- **Cada commit va con el correo noreply,** de autor y de committer: un commit con otro correo lo publicaría. Desde el
  encargo 44 es el `user.email` propio de este repo (decisión de Marcelo; `git config --local user.email`), porque la
  configuración global de este equipo trae el correo de la empresa. `.git/config` no viaja: en otro clon, se fija antes
  del primer commit. **El push lo hace Marcelo,** solo de `main` (`metodo-ciclo`); antes,
  `git log origin/main..main --format='%ae %ce'` tiene que mostrar solo ese correo.

`.gitignore` es una **lista blanca**: todo lo de la raíz queda fuera salvo lo nombrado con `!/…`, porque la carpeta
convive con `config.json`, `perfiles/`, `logs/`, planillas, manuales, videos y capturas de reservas reales, y con los
generadores de material y el logo, que salieron del repo en el encargo 44 (ver «Archivos que no son código de la app»).
Para versionar un archivo nuevo, agrégalo como `!/nombre` en `.gitignore`; nunca versiones planillas, capturas, volcados
`*_dump.html` ni imágenes: la sonda de secretos bloquea los `.png`, `.jpg`, `.jpeg`, `.gif` y `.webm`, y los
generadores. `.gitattributes` fija LF (`core.autocrlf=true` de esta máquina los devolvería con CRLF). El procedimiento
inicial y sus sondas están en `CICLO-repo-inicial.md`.

La rama es `main`; hasta el 2026-09-25 se llamó `master`. **El nombre del operador no va en ningún archivo versionado**
(`CICLO-cola-cuatro-items.md`):
- en rutas de ejemplo e informes, usa `<operador>`: las carpetas de `logs/` lo llevan en su nombre;
- en `CORRIDAS_DE_REFERENCIA` y en las generadoras, usa `*`;
- donde el programa lo necesita, lo toma de `config.json`;
- la sonda de secretos bloquea el commit que lo traiga (`CICLO-cola-siete-items.md`).

**Tampoco van datos de la cuenta ni de las personas** (encargo 44): ni contratos ni el código de Shipper de HYUNDAI (van
en `config.json` → opciones: `contratos_por_defecto` y `codigo_shipper_hyundai`), ni correos, teléfonos, naves, viajes o
números de reserva reales, ni rutas con el usuario de Windows. **Los datos de la empresa con que el programa llena los
formularios se publican tal como están** (decisión de Marcelo, encargo 44: sacarlos cambiaría lo que hace): el nombre de
la empresa (AQUACHILE, que MAERSK busca en el Shipper y HYUNDAI en su modal; «AQUACHILE S.A.», el Shipper de COSCO y el
cliente de MAERSK), la dirección, la ciudad y el país de la planta para COSCO, la descripción de la carga y su código
HS. El nombre de Marcelo queda en «decisión de Marcelo» y, completo, en el pie del panel (decisión suya, encargo 44).

## ⚠ Candado de emisión: lo más importante

Por defecto **nada se emite**: cada `reservar_*` llena el formulario completo y se detiene justo antes
del botón final (Submit / *Enviar el booking*), devolviendo `("OK-EJEMPLO", ...)`. Emitir crea
**reservas reales e irreversibles** en los portales de las navieras.

`es_modo_emision()` activa la emisión si se cumple **cualquiera** de estas condiciones:
- variable `AQUASHIELD_EMITIR=1` (es lo que hace `AQUASHIELD_EMISION.py` / `Iniciar AQUASHIELD_EMISION.bat`);
- un argumento `emitir`, `--emitir`, `produccion` o `--produccion` en `sys.argv`;
- `"emitir_reservas": true` en `config.json → opciones`. **Solo el booleano `true`** abre (desde el
  2026-09-23): cualquier otro valor (texto, número, `"true"` entre comillas, `null`) deja el candado
  cerrado y avisa con `_avisar_llave_config`, por el `Registro` de la corrida en curso o, sin corrida,
  por la consola y el registro del panel web.

Al probar, nunca uses el lanzador de emisión ni ninguna de esas tres vías sin que Marcelo lo pida
explícitamente. Cualquier cambio en un `reservar_*` tiene que conservar la rama
`if not es_modo_emision(): return ("OK-EJEMPLO", ...)` antes de pulsar el botón final.

**Después de la guarda** (decisión de Marcelo, `CICLO-estado-tras-envio.md`), cada reservador pulsa el
mismo botón de antes con `_pulsar_boton` (que dice si pulsó), guarda en `error` lo que falle y termina en
`return _resultado_envio(...)`, que decide con lo que el programa vio:
- `EMITIDA`: solo con la confirmación y un número con la forma medida de la naviera (`FORMA_BOOKING`).
- `ENVIADA – REVISAR EN PORTAL`: se pulsó (o el clic pudo salir) y no hubo confirmación reconocible, el
  portal mostró un error o el programa falló después de pulsar.
- `NO ENVIADA`: el botón no estaba, o el portal marcó errores de validación (con los campos).

Antes de decidir, `_guardar_evidencia` deja la captura y el HTML completo de la página y de cada marco
(con raíces shadow) en la carpeta de la corrida. No la llames antes de la guarda ni le agregues clics:
`test_envio.TestReservadores` lo vigila. Ese HTML lo arma `_JS_HTML_COMPLETO` con `_JS_HTML_ENTERO` (las raíces shadow
y la etiqueta de apertura), que comparte con la lectura de las tarjetas de salida de MAERSK (encargo 43).

**En la guarda** (`CICLO-evidencia-en-la-guarda.md`), se abra o no el candado, cada reservador deja
`_evidencia_antes_de_la_guarda(page, reg, f"<nav>_f{f}_guarda")` justo antes de `if not es_modo_emision():`:
la captura de la página completa y el mismo HTML, para medir con el candado cerrado.
- Solo lee: ni clics, ni navegación, ni esperas. Va como sentencia suelta: su resultado no decide nada.
- Nunca corta el flujo: si algo falla, lo avisa en pantalla y en `log.txt`.
- La captura de página completa dispara en la página un `resize` del mismo tamaño (medido en Chrome 153).
- `test_evidencia` lo vigila; no le agregues esperas ni clics.
- CMA la deja también con el panel Reefer abierto y tras guardarlo (`cma_f<fila>_reefer_panel` y
  `_reefer_guardado`), con la captura de la ventana, porque ahí el flujo sigue (`CICLO-cma-reefer-y-fecha-maersk.md`).
- La dejan también, con la captura de la ventana, donde la reserva se detiene antes de la guarda
  (`CICLO-cola-nueve-items.md`, `CICLO-proxima-salida.md`). `test_evidencia.test_solo_ahi` fija quién la llama:
  - MAERSK sin nave o sin una sola salida, desde el encargo 40 también en SIN-CUPO y desde el 46 con la nave y sin
    poder pulsar su «Book» (`_mk_detenida`: `mk_f<fila>_detenida`; que SIN-CUPO la deje lo vigila
    `test_clics.TestMaersk.test_sin_cupo_deja_la_evidencia_de_select_sailing`, y el «Book»,
    `test_el_book_sin_pulsar_queda_no_enviada_con_evidencia`);
  - ONE cuando no llega a Review Booking o no le queda una sola salida (`one_f<fila>_detenida`);
  - COSCO sin un solo itinerario para la nave (`cosco_f<fila>_itinerarios`) y, desde el encargo 48, sin el formulario
    de New Booking (`_cosco_sin_formulario`: `cosco_f<fila>_sin_formulario`);
  - MSC sin una sola salida para la nave (`msc_f<fila>_itinerarios`).
- HYUNDAI la deja justo antes de escribir el Remark (`hmm_f<fila>_remark`), con la captura de la ventana
  (`CICLO-evidencia-remark-hyundai.md`); con ella se identificó el campo (`CICLO-pendientes-con-evidencia.md`).
  `test_solo_ahi` la cuenta, y `TestEvidenciaRemarkHyundai` corre esa llamada y el Remark, tal como están, sobre una
  página falsa.
- HYUNDAI y CMA la dejan también al leer su lista de salidas, con la captura de la ventana: `hmm_f<fila>_naves`, y
  `cma_f<fila>_rutas` (y `_rutas_mas`, `_rutas_mas2`… tras cada «Cargar N siguientes resultados»). Con el de HYUNDAI
  se midió su tarjeta, y desde el encargo 32 aplica la próxima salida; la de CMA todavía espera el suyo
  (`CICLO-cola-siete-items.md`).
- CMA la deja también al terminar la espera que ya existe tras «Validar ruta», después de leer su aviso, con la
  captura de la ventana: `cma_f<fila>_validar_<modo>`, uno por intento (`CICLO-cola-tres-items.md`). Va después
  del aviso para que esa lectura, que decide el camino, siga en el mismo instante.
- HYUNDAI la deja también con el modal «Alternate Vessel Option» a la vista, antes de marcar que no quiere otra nave,
  con la captura de la ventana: `hmm_f<fila>_otra_nave`; y si el modal sigue después del OK,
  `hmm_f<fila>_otra_nave_sigue` (`CICLO-ampliar-la-busqueda.md`; ver «Solo la nave que la fila pide»). Ese HTML no trae
  qué opción está marcada (el atributo `checked` no refleja el estado): eso se ve en la captura.
- HYUNDAI la deja también con la lista ampliada, después de elegir más semanas en «Duration»: `hmm_f<fila>_naves_mas`,
  con la captura de la ventana (`CICLO-ampliar-la-busqueda.md`).
- MAERSK la deja también, con la captura de la ventana, en «Booking Information», en la fecha de retiro y en los
  términos (`CICLO-maersk-retiro-y-terminos.md` y `CICLO-maersk-ultimos-puntos.md`; ver «MAERSK elige la fecha de
  retiro»):
  - si «Booking Information» no avanza: `mk_f<fila>_booking`, porque los avisos de esa pantalla no están medidos;
  - con el calendario abierto, antes de elegir el día: `mk_f<fila>_calendario`, el único HTML que puede medir el
    calendario;
  - si la tarjeta no queda con la fecha elegida o no se puede leer: `mk_f<fila>_retiro`;
  - con el buscador de partes del Shipper abierto, antes de elegir a AQUACHILE: `mk_f<fila>_buscador`, el único HTML que
    puede medir el buscador abierto; si el Shipper no queda elegido: `mk_f<fila>_shipper`; si «Review booking» está a la
    vista pero no acepta el clic: `mk_f<fila>_revision`; y en «Booking Information» incompleta, `mk_f<fila>_booking`,
    como cuando no avanza (`CICLO-maersk-shipper-y-cortes.md`);
  - si «Continue» de «Recommended services» está a la vista pero no acepta el clic: `mk_f<fila>_servicios`; y con el
    buscador del Shipper abierto y AQUACHILE en la tarjeta, antes de su «Close»: `mk_f<fila>_cerrar`, el único HTML que
    puede medir ese estado (`CICLO-maersk-cuatro-puntos.md`);
  - si el clic en el resultado del buscador no elige a AQUACHILE, antes de pulsar su casilla: `mk_f<fila>_casilla`, el
    único HTML que puede medir ese estado (`CICLO-maersk-busqueda-vacia.md`);
  - en la revisión, antes de marcar la casilla de los términos: `mk_f<fila>_terminos`.
- Las seis navieras la dejan también antes de pulsar una sugerencia de origen o de destino, cuando el ayudante ve la
  que pulsaría, con la captura de la ventana (decisión de Marcelo, encargo 41, `CICLO-origen-y-destino.md`):
  `<nav>_f<fila>_origen` y `_destino`; CMA, con su modo (`cma_f<fila>_origen_<modo>`, `_destino_<modo>` y
  `_entrega_<modo>`, el lugar de entrega), y MAERSK y COSCO, si vuelven a escribir la ciudad, `_reintento`.
  - Una vez por lista, justo antes del clic que ya daba: la regla con que elige cada una no cambió. El commodity de ONE
    y el contrato de COSCO usan los mismos ayudantes y no la dejan.
  - ONE, MSC, HYUNDAI y COSCO eligen y pulsan en un mismo JavaScript, que ahora, con sus argumentos en una lista, pulsa
    solo con la marca true (el de ONE y el de COSCO aceptan todavía el texto solo, y pulsan, pero el programa ya no los
    llama así): el ayudante lo corre antes con la marca false, que pone `_sugerencia_sin_pulsar`, y si esa lectura
    falla, no la deja y elige igual. MAERSK y CMA miran con el localizador con que pulsan.
  - Después del clic, `_avisar_lista_distinta` avisa si pulsó sin dejarla (la lista apareció entre la lectura y el
    clic, o la lectura falló) o si la lista cambió mientras la guardaba, y el clic eligió de otra: la evidencia toma su
    tiempo, y el clic sale después. Compara el texto de cada una; en ONE, `_texto_de_la_sugerencia` le quita la
    etiqueta, la clase y la posición que agrega su JavaScript, que cambian sin que cambie la sugerencia (la clase la lee
    después del clic).
  - Si no ven ninguna sugerencia que elegir, la dejan igual, con el mismo nombre, al terminar la espera que ya tenían y
    sin clics ni esperas nuevas (`_evidencia_sin_sugerencia`; decisión de Marcelo, encargo 42,
    `CICLO-maersk-y-fila-sin-ruta.md`): MAERSK y COSCO, también la de su segunda espera, `_reintento`; el puerto de CMA,
    antes del Tab con que lee lo que quedó. `log.txt` dice «evidencia sin una sugerencia que elegir en …».
  - Si la lista se cierra mientras se guarda la evidencia (no medido), el clic ya no la encuentra: MAERSK y COSCO
    vuelven a escribir la ciudad, y si el ayudante no elige ninguna, desde el encargo 42 la fila queda NO ENVIADA en las
    seis (hasta ahí, el destino de COSCO, MAERSK, HYUNDAI y el lugar de entrega de CMA seguían sin el campo). MAERSK y
    CMA esperan antes hasta 30 s, el plazo de Playwright, porque leen el texto de la sugerencia después de la evidencia.
    Y ONE podría pulsar otro elemento con el texto: su JavaScript no mira solo la lista.
  - La vigila `test_evidencia.TestListaDeSugerencias`, cuya página falsa anota todo lo que se le hace (el campo, lo
    escrito, cada espera, cada tecla, cada clic), y `test_solo_ahi` cuenta los 7 ayudantes y
    `_evidencia_sin_sugerencia`. Desde el encargo 43, esa página separa el texto de cada sugerencia de su raíz shadow
    (el tipo de lugar), como Playwright, y su sugerencia sintética trae la forma de la regla de MAERSK.

**Antes de la guarda no hay clics a ciegas** (`CICLO-clics-a-ciegas.md`), y eso también corre con el candado
cerrado:
- Cada paso busca su objetivo por su texto, su etiqueta o un selector propio. Nunca por «el primero» o «el
  último» visible de un selector genérico.
- Si no lo encuentra, `raise ObjetivoNoEncontrado(paso, buscaba)`. Deriva de `BaseException` para que ningún
  `except Exception` se lo trague. Con `pide=`, lo que el portal pide en esa pantalla, leído de ella (en MAERSK,
  `_mk_lo_que_pide`): el motivo empieza por «el portal pide: …» (`CICLO-maersk-retiro-y-terminos.md`).
- El decorador `_sin_clic_a_ciegas("<prefijo>")` del reservador lo convierte en NO ENVIADA, con el paso, lo que
  buscaba, la captura `<nav>_f<fila>_sin_objetivo` y su HTML.
- Después de la guarda nada corta: un ayudante que corre en los dos lados recibe `antes_de_la_guarda=False`.
- **La fila sin puerto de carga o sin destino** (decisión de Marcelo, encargo 42, `CICLO-maersk-y-fila-sin-ruta.md`):
  queda NO ENVIADA sin entrar al portal la fila con nave cuyo puerto de carga o cuyo destino (el final o, si viene
  vacío, el original) no trae, antes de la primera coma, una palabra: dos letras o números seguidos, de cualquier
  alfabeto (`_falta_en_la_fila`, `_ciudad_de`). En el puerto de carga, la palabra se mide también en el puerto
  normalizado sin el país en ninguna posición (`_puerto_de_carga`, que usan la regla y el origen de COSCO; ahí las
  letras son A-Z sin tildes y números): «CHILE», «X CHILE», «CHILE X» o «№» no son un puerto (revisiones del encargo 42;
  con «X CHILE», COSCO buscaba «X»). Desde el encargo 43, «CL» también es el país, igual que «CHILE»
  (`PAIS_DEL_PUERTO`; desde el 46, COSCO también lo quita al final del puerto que busca), y «-» en el destino final,
  sin otra cosa, es la celda vacía: los dos lectores lo leen así (`_destino_final_de`), y el destino pasa a ser el
  original (decisiones de Marcelo, `CICLO-maersk-elige-exacto.md`). El
  motivo es «a la fila le falta el puerto de carga» o «a la fila le falta el destino» (`FILA_SIN_PUERTO`,
  `FILA_SIN_DESTINO`, `_sin_ruta`). Desde el encargo 43, el panel web la marca antes de correr, en la celda que le
  falta, y la cuenta aparte, como la fila sin nave (`sin_puerto` y `sin_destino` de `/api/filas`). El panel y la consola
  la apartan antes de abrir el navegador, como la fila sin nave, y cada reservador lleva `_con_la_ruta_de_la_fila`, por
  dentro de `_con_la_nave_de_la_fila`. Los lectores no la apartan: `leer_filas` salta solo la fila sin puerto de carga
  ni nave. Hasta el encargo 42, con el texto vacío los siete ayudantes de origen, destino y lugar de entrega pulsaban
  una sugerencia a la vista (medido en un Chromium local); con «-» o «X», ONE, MSC, HYUNDAI y el destino de COSCO
  pulsaban la que lo trajera (MAERSK y CMA, probablemente; sin medir). Desde entonces ninguno escribe ni pulsa sin una
  palabra: corta (`_TEXTO_DE_LA_FILA`). El de COSCO llena también el contrato, que va tal como viene, así que corta solo
  con el texto vacío; el origen y el destino se los pasa ya cortados quien lo llama.
- **Sin una sugerencia elegida, NO ENVIADA** (misma decisión): si el ayudante de origen, destino o lugar de entrega no
  elige ninguna, cada reservador corta con `ObjetivoNoEncontrado` («no encontré una sugerencia que elegir para «…»»;
  ONE, MSC, el puerto de CMA y el origen de COSCO, si no ven ninguna, cortan antes con su propio texto, y MAERSK, desde
  el encargo 43, dentro de `_mk_ciudad`, con lo que buscaba), y ninguna naviera sigue; CMA, sin probar el modo
  siguiente. Hasta el encargo 42, MAERSK, HYUNDAI, el destino de COSCO y el lugar de entrega de CMA seguían sin el
  campo, y ONE y MSC, si fallaban al escribir. `_cma_puerto` corta él mismo si no elige: los cortes de `reservar_cma`
  por su False (hasta ahí, una rama REVISAR) no se alcanzan, y quedan de resguardo. En el modo ramp de CMA, el motivo
  del lugar de entrega dice también el aviso con que CMA rechazó el puerto. Lo vigila
  `test_clics.TestSinSugerenciaNoSigue`, que corre los seis reservadores hasta su ruta y exige que, después del ayudante
  que no eligió, nada pase en la página (su página falsa anota cada acción de sus localizadores, de la página, del
  teclado y del mouse, cada dirección y cada JavaScript, menos el que guarda el HTML de la evidencia, y en COSCO lo que
  se corre en su marco). Cada ayudante que no eligió lo dice (False o `""`) o corta él mismo (ONE y MSC sin sugerencia a
  la vista, y el puerto de CMA y MAERSK siempre): lo vigilan `test_sin_sugerencias_deja_la_evidencia_igual` y
  `test_si_el_campo_falla_no_elige`.
- `test_clics` fotografía las formas de clic genérico antes de la guarda, con los ayudantes, el JavaScript que
  `test_candado` no mira y las constantes con que se arma ese JavaScript. Una forma nueva hace caer la red.
  - Lee el texto fuente, docstrings y comentarios incluidos: un docstring que nombre una forma genérica también la
    hace caer.
  - «ultimo-por-posicion» calza «.last» también sin paréntesis delante («loc.last») y «.nth(-1)»: hasta el encargo 37
    veía solo «).last», y así no veía el Shipper de MAERSK (`CICLO-maersk-ultimos-puntos.md`).
  - «primero-por-textContent» (encargo 38): el primer elemento cuyo `textContent` calza, elegido con `.find`. Así era el
    respaldo de «Review booking» que pulsaba `<html>`, y la foto no lo veía. Queda permitido donde ya estaba: dos en
    COSCO (`_JS_COSCO_AUTO_PICK`, entre las sugerencias de la ciudad). El respaldo de «Continue» en «Recommended
    services» de MAERSK, que también la tenía, se quitó en el encargo 39 (`CICLO-maersk-cuatro-puntos.md`).
- Nada de lo que corre antes de la guarda atrapa `ObjetivoNoEncontrado`, `BaseException` ni todo (un `except`
  desnudo): se tragaría el corte. Lo vigila `test_clics.TestSinClicACiegas.test_nada_se_traga_el_corte` (encargo 37),
  que mira los `except`: no ve un `contextlib.suppress`.
- La misma regla vale para el teclado y los textarea (`CICLO-cola-nueve-items.md`):
  - nada se elige con flecha abajo y Enter;
  - nada se escribe en «el primer textarea»;
  - la foto incluye esas formas: `teclado-flecha`, `textarea-en-js` y `textarea-o-control`;
  - COSCO también lleva `_sin_clic_a_ciegas("cosco")`.
- CMA busca la temperatura solo dentro del único panel Reefer visible y solo por su etiqueta «Temperature» (el
  `.el-form-item` con esa `.el-form-item__label`). Guarda con el único «Guardar» a la vista, que tiene que ser de ese
  panel (`CICLO-pendientes-con-evidencia.md`). Si falta algo, corta.
  - Hasta `1ed40f4` miraba el primer diálogo de la página, que era uno oculto.
  - Hasta `1e8d510` también le bastaban un placeholder o un «°C», y el guardado caía a un clic por JavaScript en
    cualquier cajón.
  - El detector de paneles es uno solo, `_JS_CMA_PANELES_VISIBLES`.
- **Ampliar la búsqueda** (decisiones de Marcelo, `CICLO-ampliar-la-busqueda.md` y `CICLO-ampliar-msc-y-cma.md`) trae
  clics nuevos antes de la guarda, cada uno por su texto: en MAERSK, el único botón con el nombre accesible
  «Search more sailing options» (`MK_BOTON_MAS`, exacto); en COSCO, el único campo «Sailing Within N Weeks» y su opción
  más larga; en HYUNDAI, en «Duration» (`#srchSelWeeks`, por su id), la opción más larga por su texto; y en CMA, el
  único enlace o botón a la vista «Cargar N siguientes resultados» (`CMA_CARGAR_MAS`). Después, COSCO y HYUNDAI vuelven
  a buscar con el botón de búsqueda que ya usaban; MAERSK y CMA cargan más en la misma lista. MSC baja por su lista sin
  pulsar nada (`_JS_MSC_BAJAR`). ONE no amplía: de `05cfdb7` a `924485a` abría su selector «N weeks». En el modal de
  HYUNDAI, la opción «I do not want to choose an alternate vessel» y su «OK» (ver «Solo la nave que la fila pide»). El
  «Book Now» de HYUNDAI, que ya se pulsaba, vuelve a leer su tarjeta antes de pulsarse (`_JS_HMM_CLIC_TARJETA`).
  Los otros clics nuevos antes de la guarda son los tres de la fecha de retiro de MAERSK y los de su Shipper: dos, el
  «Close» del buscador solo si la tarjeta ya muestra a AQUACHILE y la casilla del resultado solo si su posición y su
  código apuntan a la misma (abajo).
- **MAERSK marca los términos por su texto** (decisión de Marcelo, `CICLO-maersk-retiro-y-terminos.md`): la única
  casilla a la vista cuyo texto entero es «I have read and accept all the terms and conditions of this booking»
  (`MK_TERMINOS`), leído con OCR en las capturas de la revisión del 21-09; su HTML se guardó por primera vez el
  2026-10-02 (`mk_f10_terminos`). `_mk_marcar_terminos` baja al final, deja `mk_f<fila>_terminos` y, solo si sabe que
  está sin marcar, pulsa su `input` con un clic de JavaScript. El 21-09 la marcó un clic del mouse en el centro del
  `mc-checkbox`, pero ahí puede estar el enlace de «terms and conditions». El de JavaScript se probó en el portal el
  2026-10-02 (encargo 49, `CICLO-corridas-de-la-tarde-02-10.md`): la casilla, sin marcar en `mk_f10_terminos`, quedó
  marcada en el HTML de la guarda. Después pide una sola casilla, marcada y en la misma dirección; si no, NO ENVIADA
  sin otro clic. Hasta el encargo 36 era «el último checkbox», por cuatro vías (FRENO, cerrado): así se marcó el 21-09.
  A MAERSK ya no le queda ninguna forma genérica en la foto: el respaldo de «Continue» (`primero-por-textContent`) se
  quitó en el encargo 39.
- **MAERSK pulsa «Continue» de «Recommended services» solo si hay uno a la vista** (decisión de Marcelo, encargo 39,
  `CICLO-maersk-cuatro-puntos.md`; `_mk_continuar_servicios`, `_JS_MK_CONTINUAR`, `MK_CONTINUAR`; desde el encargo 40,
  con el ayudante `_mk_pulsar_unico`): un `mc-button` (por su `label` o su texto), un `button`, un enlace o
  `role="button"`, con ese texto entero, sin distinguir mayúsculas y a la vista; el botón interno de un `mc-button` es
  el mismo control. Lo busca hasta `MK_INTENTOS_CONTINUAR` veces, una por segundo, y pulsa lo que
  `_JS_MK_CONTINUAR_PULSAR` vuelve a leer justo antes; si «Additional details» ya apareció, sigue. Con cero o más de
  uno, NO ENVIADA (`ObjetivoNoEncontrado`, con lo que el portal pide); si no acepta el clic, lo reintenta en la vuelta
  siguiente, y si no lo acepta en ninguna, NO ENVIADA con `mk_f<fila>_servicios`. Su HTML no está medido: ninguna
  corrida guardó esa pantalla, y en sus 6 capturas no se ve; el programa lo pulsó por su texto las 6 veces. Hasta el
  encargo 39 pulsaba el primero con ese texto o, por JavaScript, el primer elemento a la vista con ese texto, y si no
  encontraba ninguno seguía sin cortar.
- **MAERSK pasa a la selección de nave con un solo «Continue to book» o «Continue» a la vista** (decisión de Marcelo,
  encargo 40, `CICLO-maersk-busqueda-vacia.md`; `_mk_continuar_a_la_nave`): el único control a la vista cuyo texto
  entero es uno de los dos, leído como el «Continue» de «Recommended services» y con su mismo ayudante
  (`_mk_pulsar_unico`: `_JS_MK_CONTINUAR` recibe una lista de textos). Con cero o más de uno, NO ENVIADA
  (`ObjetivoNoEncontrado`, con lo que el portal pide); si está y no acepta el clic, lo reintenta en la vuelta siguiente,
  y si no lo acepta en ninguna, formulario incompleto (`_mk_formulario_incompleto`, `mk_f<fila>_booking`). Medido con
  OCR en las 11 capturas legibles de esa pantalla, del 21 al 27-09 (de 14; las otras 3, del 26 y el 29-09, el OCR no las
  reconoce): un solo botón, «Continue to book», al pie; en el HTML de la selección de nave del 29-09, que todavía trae
  el formulario, es un `mc-button` con `label="Continue to book"` y su botón interno. «Continue to book» sigue escrito
  en `reservar_maersk`, donde `test_candado` lo fotografía. Hasta el encargo 40 tomaba el primer botón cuyo nombre
  accesible traía «Continue to book» (`get_by_role(...).first`) y lo pulsaba solo si estaba habilitado; si no, o si el
  clic fallaba, lo mismo con «Continue»: no elegía entre los que se veían. Los comentarios del código todavía lo
  describen como «el primer botón habilitado… sin mirar si se veía» (residual de `CICLO-maersk-busqueda-vacia.md`).
- **MAERSK escribe la referencia y lee el Shipper por lo que son** (decisiones de Marcelo,
  `CICLO-maersk-ultimos-puntos.md`). La referencia de retiro va en el único `textarea[name='haulageReference']` a la
  vista (`MK_REFERENCIA`, `_mk_referencia_de_retiro`, medido el 27-09); sin uno solo, corta. El Shipper se lee en la
  única tarjeta `mc-c-party-card` a la vista con `title="Shipper"` (`_mk_shipper`, `_JS_MK_SHIPPER`; la espera hasta
  `MK_ESPERA_SHIPPER` s): si trae a AQUACHILE (`MK_EMPRESA`), no pulsa nada; si no hay una sola tarjeta, corta sin
  pulsar nada.
  - **Si no trae a AQUACHILE, lo elige con dos clics** (decisión de Marcelo, encargo 38,
    `CICLO-maersk-shipper-y-cortes.md`; `_mk_elegir_shipper`): el único «Add» a la vista de esa tarjeta, por su texto
    (`MK_AGREGAR`), y en el buscador de partes titulado «Shipper» el único resultado a la vista con AQUACHILE. Cada clic
    va sobre lo que `_JS_MK_SHIPPER_PULSAR` vuelve a leer justo antes. Antes de elegir espera, hasta
    `MK_ESPERA_BUSCADOR` s, que la lista tenga un resultado con AQUACHILE y se quede quieta en dos lecturas
    (`_mk_resultados_quietos`: llega de a poco; si no se queda quieta, decide con la última lectura), y deja
    `mk_f<fila>_buscador`. Después comprueba, hasta `MK_ESPERA_SHIPPER` s, que la tarjeta lo muestre y que el buscador
    se haya cerrado: ni sus resultados ni su encabezado a la vista (`abierto`); si la tarjeta ya lo muestra y el
    buscador sigue abierto, lo cierra con su «Close», y si la tarjeta no lo muestra, pulsa la casilla del resultado (los
    dos, abajo). Si algo no se cumple, NO ENVIADA sin otro clic, con `mk_f<fila>_shipper` y su motivo: buscar o cambiar
    de pestaña serían clics que no están permitidos. Sin un solo «Add» (la tarjeta llena con otro, por ejemplo), corta
    antes de pulsar nada (`ObjetivoNoEncontrado`, `mk_f<fila>_sin_objetivo`).
  - AQUACHILE se busca como palabra entera en el `party__info` de cada parte, que trae el nombre y, adentro, el código
    (`party__code`; medido en las 2 tarjetas llenas y en los 3 resultados, donde el código no trae letras); la dirección
    no cuenta. El texto se lee nodo por nodo, con las raíces shadow de adentro (`mkTextoHondo`): el `textContent`
    pegaría el título de la tarjeta al nombre.
  - Medido en el HTML del 27-09, guardado después de los clics de antes: cada tarjeta vacía trae un solo mc-button «Add»
    (`data-cy="addButton"`) en su raíz shadow, y el de la tarjeta del Shipper vacía se infiere de las otras 8; el
    buscador es uno solo (`mc-c-party-finder`), con su ventana titulada «Shipper» y la pestaña «Previously used» activa,
    sus resultados se ven sin buscar (cada uno un `label` con su `mc-c-party-card`, sin `for`, con su casilla de opción
    al lado) y no tiene botón de confirmar. El `button` interno del «Add» lleva como `aria-label` el nombre del ícono:
    por su nombre accesible no se encuentra. La tarjeta se identifica por su `title`, que traen las 10: las 8 vacías
    comparten un mismo `id`.
  - **El «Close» del buscador** (decisión de Marcelo, encargo 39, `CICLO-maersk-cuatro-puntos.md`;
    `_mk_cerrar_buscador`, `MK_CERRAR`): si después del resultado la tarjeta ya muestra a AQUACHILE y el buscador sigue
    abierto, pulsa su único «Close» a la vista, un `mc-button` con `label="Close"` (medido: uno solo en la página, en la
    cabecera de la ventana del buscador, con `data-cy="close"` y el texto oculto), que `_JS_MK_SHIPPER_PULSAR` da solo
    si la tarjeta sigue mostrándolo. Antes deja `mk_f<fila>_cerrar`; después comprueba, hasta `MK_ESPERA_SHIPPER` s, que
    se cerró y que la tarjeta lo sigue mostrando. Si no, NO ENVIADA con `mk_f<fila>_shipper`. Sin AQUACHILE en la
    tarjeta (o sin una sola tarjeta «Shipper»), no lo pulsa.
  - **La casilla del resultado** (decisión de Marcelo, encargo 40, `CICLO-maersk-busqueda-vacia.md`;
    `_mk_marcar_casilla`, `_JS_MK_SHIPPER_CASILLA`, `_JS_MK_SHIPPER_MARCAR`; en el encargo 39, un FRENO). En el HTML del
    27-09, los 3 resultados van sueltos en un solo `div.party-search-results`, casilla (`input.party-card__input`,
    radio, con `id` y `name` iguales) y `label` alternados; la casilla queda fuera del `label`, que no tiene `for`. Si
    el clic en el resultado no lo elige (la única tarjeta «Shipper» sigue sin AQUACHILE), la pulsa solo si su posición
    (la que va justo antes del `label`, en un contenedor de casillas y `label` alternados) y las cifras del código (la
    única cuyo `id` termina con las cifras que muestra el `party__code` de la tarjeta) apuntan a la misma; sobre el
    árbol del 27-09 en un Chromium sin red, con la ventana del buscador abierta a mano (en el HTML guardado está
    cerrada), coinciden. El clic es de JavaScript en el `input`, que la vuelve a leer justo antes, como la casilla de
    los términos, porque su estilo no está en el HTML guardado. Antes deja `mk_f<fila>_casilla`, y después anota si
    estaba marcada, vuelve a comprobar la tarjeta y, si el buscador sigue abierto, pulsa su «Close». Si no coinciden, NO
    ENVIADA con `mk_f<fila>_shipper`, y el motivo dice por qué. No está probado en el portal.
  - **Medido una vez, el 2026-10-02** (encargo 49, `CICLO-corridas-de-la-tarde-02-10.md`): el clic en el resultado (va
    al `label`, que no tiene `for`; la casilla de opción está a su lado) eligió a AQUACHILE, y el buscador se cerró
    solo. Ni la casilla ni el «Close» hicieron falta, y siguen sin probarse en el portal. Hasta el encargo 38, después
    del Shipper se pulsaba la tecla Escape, y se quitó (decisión de Marcelo); no está medido si el buscador se cerraba
    por ella o solo. Si la tarjeta no queda con AQUACHILE, ni con su casilla, o el buscador sigue abierto y su «Close»
    no lo cierra, la reserva queda NO ENVIADA ahí, y su HTML lo mide.
  - En el encargo 37 cortaba sin pulsar nada (FRENO, cerrado): el HTML del 27-09 es de después de los clics de antes, y
    lo más probable es que ellos eligieran a AQUACHILE, porque el Shipper viene vacío (no medido).
  - Un HTML guardado en un corte es de después de todo lo que el programa pulsó antes: no es el estado de partida. Así
    se midió mal el Shipper en el encargo 37, y se concluyó que AQUACHILE ya venía.
  - Hasta el encargo 37 la referencia iba en «el primer textarea», que el 27-09 era el campo oculto del asistente «Ask
    Maersk», y llegaba a su campo por el respaldo de la etiqueta; y el Shipper se buscaba en el `textContent` del primer
    `div` con «Parties», que no ve las raíces shadow, así que siempre pulsaba el primer «+ Add» de la página y el último
    elemento con AQUACHILE.
- **HYUNDAI escribe el Remark en el campo de su recuadro:** el único textarea del formulario titulado «Remark (n / m)»
  (`_JS_HMM_REMARK`), medido en `hmm_f<fila>_remark.html` (`CICLO-pendientes-con-evidencia.md`). Hasta `e423a38` iba
  al primer textarea visible (FRENO). Si no lo encuentra, corta: `reservar_hyundai` lleva `_sin_clic_a_ciegas("hmm")`.
- **ONE avanza su asistente con el «Next» de cada pantalla** (`_one_siguiente`, `_JS_ONE_SIGUIENTE`;
  `CICLO-cola-seis-items.md`): el único botón a la vista con el texto «Next» o «Siguiente», medido con OCR en las
  capturas del 2026-09-21 y en la corrida del 2026-09-26 con candado cerrado, que encontró uno solo en cada una de las
  tres pantallas (`CICLO-inicio-de-todas.md`). Si el asistente no está en ese paso, si el «Next» está en una ventana
  emergente o si no hay uno solo, corta; si la búsqueda falla, corta sin reintentar. Hasta `f68ce6c` era el clic
  genérico `_JS_CLICK_BTN`. Ese clic queda solo en el envío de ONE y de MSC, después de la guarda, y la foto de
  `test_clics` lo ve (`primero-que-calce-el-texto`). `_one_esta_en_paso('booking-parties')` también da verdadero en
  Search Schedule, porque la barra de pasos nombra «Booking Parties».
- **MSC sin `_JS_CLICK_BTN` antes de su guarda** (`CICLO-inicio-de-todas.md`): en su login (`_msc_entrar`), el «Next» y
  el de entrar, solo por su texto (decisión de Marcelo, `CICLO-cierre-de-frenos.md`; hasta `4948e16` el de entrar
  también podía ser el primer `button[type=submit]` de la página). Si no encuentra uno, lo anota y no pulsa nada, y la
  verificación de la sesión dice si entró. «Search Schedule» va con `_msc_buscar_itinerarios`, que corta si no encuentra
  el botón. Hasta `c4df3ab` los tres caían a `_JS_CLICK_BTN`. El login no está en el universo de la foto: lo vigila
  `test_login_sin_clic_generico`.
- **COSCO elige el puerto de carga de la fila** (`_cosco_puerto_de_carga`, `CICLO-cola-seis-items.md`): la celda del
  puerto de carga normalizada (`_cosco_puerto_de_la_celda`, `CICLO-inicio-de-todas.md`: la parte antes de la primera
  coma, en mayúsculas, sin tildes, con todo signo como separador y sin el país al final: «CHILE» o, desde el encargo
  46, «CL»), traducida por `MAPA_PUERTOS_COSCO` o tal como quedó, con la sugerencia de Chile que calce en «Origin
  City». Si COSCO no la sugiere, o si la celda viene vacía o solo con el país, corta como objetivo no encontrado (NO
  ENVIADA, `cosco_f<fila>_sin_objetivo`). Hasta `f68ce6c` caía al puerto fijo «Lirquen»; hasta `c4df3ab`, «CORONEL,
  CHILE» o «Lirquén» no se traducían; hasta el encargo 46, «CORONEL CL» se buscaba tal cual (decisión de Marcelo,
  `CICLO-maersk-pulsa-el-book.md`).
- **MAERSK elige la fecha de retiro con la regla de Marcelo** (`CICLO-maersk-retiro-y-terminos.md`): el primer día hábil
  después del día en que se corre el programa (`_mk_dia_de_retiro`, `_mk_dia_habil`: de lunes a viernes y sin los
  feriados de Chile) y, si no está habilitado en el calendario, el siguiente día hábil habilitado
  (`_mk_elegir_dia_de_retiro`): nunca un sábado, un domingo ni un feriado (decisiones de Marcelo, encargo 37,
  `CICLO-maersk-ultimos-puntos.md`, y encargo 38, `CICLO-maersk-shipper-y-cortes.md`; hasta el encargo 37, el siguiente
  habilitado, aunque fuera fin de semana, y hasta el 38, los feriados contaban como hábiles).
  - **Los feriados salen de la librería holidays** (`_feriados_de_chile`: `holidays.country_holidays("CL")`, de este año
    y del siguiente, copiados a un diccionario dentro del `try`, porque la librería calcula cada año recién al
    consultarlo). No viene con Python: los `.bat` la instalan si falta, sin frenar el arranque sin red (encargo 39; el
    29-09 así quedó instalada, la 0.105). Si no está o falla, avisa una vez por corrida (`_avisar_en_pantalla_y_log`) y
    sigue de lunes a viernes. El log dice qué feriados saltó (`_mk_feriados_saltados`). Las pruebas usan una librería
    falsa: la de verdad no se probó.
  - **El portal no avanza sin ella** (medido el 2026-09-27, `CICLO-maersk-fecha-de-retiro.md`): «Additional details»
    marca «Pick up date cannot be left blank» y la revisión no aparece. Del 24-09 (`0f1507e`) al encargo 36 no se
    elegía. El 21-09, el código de antes de `0f1507e` pulsó el primer día que veía habilitado, el domingo 27, en las 5
    filas, y las 5 llegaron a la revisión.
  - `_mk_fecha_de_retiro`, antes de la referencia, con tres clics: «Choose another date» (`MK_OTRA_FECHA`, el único a la
    vista, y ningún «Done» antes de abrir), el día por su fecha y el «Done» del calendario (`_JS_MK_LISTO`), nunca otro.
    Deja `mk_f<fila>_calendario` antes de elegir, anota en `log.txt` los avisos de cargos (la reserva sigue) y comprueba
    la tarjeta (`_mk_comprobar_retiro`, que la espera hasta 5 s mientras siga sin fecha o no la pueda leer): sin fecha,
    con otra o sin poder leerla, NO ENVIADA con `mk_f<fila>_retiro` (hasta el encargo 37, si no se podía leer, avisaba
    y seguía).
  - **El calendario, medido el 2026-10-02** en `mk_f10_calendario.html`, el primero que guardó una corrida
    (`CICLO-msc-recarga-y-corrida-02-10.md`). `mkCalendario` (`_JS_MK_DIAS`) lo reconoce por su único «Done» a la vista
    con al menos 28 días alrededor, y da la fecha de cada día por un atributo que la trae entera, por la leyenda de su
    mes o, sin una leyenda, por su cabecera (abajo), sin los números de semana (`/week(?!end)/`) ni los días de otro
    mes. Si el día no se identifica, no está a la vista o el calendario no aparece, NO ENVIADA sin otro clic: cambiar de
    mes es un clic que no está permitido (FRENO).
    - Lo medido: va en un `mc-modal` («Container pick-up details»); el mes y el año, en dos `mc-button` de su cabecera
      (`label` «October» y «2026»), sin una leyenda que traiga los dos; cada día, un `mc-button` con su número por
      `label` y, adentro, un `button` con el número por `aria-label` y `disabled` si no se puede elegir.
    - **El mes y el año de la cabecera** (decisión de Marcelo, encargo 48, `CICLO-calendario-cosco-y-cma.md`): sin una
      leyenda, un solo botón a la vista cuyo nombre (`label`, `aria-label` o texto) es un mes en inglés y uno solo cuyo
      nombre es un año de 4 cifras, y solo si los días, sin los marcados de otro mes, van del 1 al último de ese mes,
      una vez cada uno. Si no, ningún día tiene fecha, y NO ENVIADA, como antes. `log.txt` lo dice («cabecera: 31»).
    - Hasta el encargo 48 el lector no le ponía fecha a ninguno (0 de 31), y la fila del 02-10 quedó NO ENVIADA ahí. Con
      ese calendario (5 días habilitados, del lunes 12 al viernes 16 de octubre), la regla elige el 13: el 05-10 no
      estaba habilitado, y el 12 es feriado en Chile (medido sin red sobre el HTML guardado). La tarde del 02-10, en el
      portal, lo leyó por su cabecera, eligió el 13 con los mismos días habilitados, y la tarjeta lo mostró (encargo 49,
      `CICLO-corridas-de-la-tarde-02-10.md`).
  - «Review booking» es el único mc-button a la vista con ese texto (`_mk_pulsar_revision`, `MK_REVISION`; en el HTML
    del 27-09, el mc-button y su botón interno son el mismo control), buscado hasta `MK_INTENTOS_REVISION` veces. Sin
    uno solo, NO ENVIADA (`ObjetivoNoEncontrado`, con lo que el portal pide); si está pero no acepta el clic, NO ENVIADA
    con ese motivo y `mk_f<fila>_revision`; si un clic falló pero la revisión ya apareció, sigue. Hasta el encargo 38,
    un respaldo en JavaScript pulsaba el primer elemento a la vista cuyo texto lo traía, que era `<html>` (decisión de
    Marcelo, `CICLO-maersk-shipper-y-cortes.md`).
  - Si la revisión no aparece, `_mk_esperar_revision` corta y la reserva queda NO ENVIADA, con el decorador
    `_sin_clic_a_ciegas("mk")`. Así no marca casillas en otra pantalla ni dice «armada hasta Review». El motivo empieza
    por lo que el portal pide (`_mk_lo_que_pide`): los campos que nombra el resumen «Please correct the following
    errors» en los enlaces «#…» de su pie, y el `body` de los demás avisos de error; el 27-09, «Pickup date («Pick up
    date cannot be left blank»)». «Booking Information» que no avanza queda NO ENVIADA (`_mk_booking_sin_avanzar`;
    hasta el encargo 37, REVISAR), con el mismo lector, y deja `mk_f<fila>_booking`.
  - **Antes del botón final, MAERSK devuelve REVISAR solo si la nave de la fila no está** (`_mk_sin_nave`; decisión de
    Marcelo, encargo 38, `CICLO-maersk-shipper-y-cortes.md`): el formulario que no abre y el que queda incompleto
    (`_mk_formulario_incompleto`, con lo que el portal pide y `mk_f<fila>_booking`) quedan NO ENVIADA; hasta el encargo
    38, REVISAR. `test_clics.TestMaersk.test_revisar_solo_si_la_nave_no_esta` lo vigila, por el texto de cada rama. La
    búsqueda de salidas que no termina no corta (decisión de Marcelo, encargo 39): a los 45 s, `_mk_desenlace_sailing`
    dice «con-zarpes» y la reserva sigue a buscar la nave; la rama a NO ENVIADA para «indefinido», que nunca se
    alcanzaba, se quitó (`test_la_busqueda_de_salidas_no_corta`). El «Book» con que el detector da la búsqueda por
    terminada es solo el de una tarjeta de salida, leída con `_JS_MK_SALIDAS`, como la lista (decisión de Marcelo,
    encargo 40, `CICLO-maersk-busqueda-vacia.md`); con «no sailings for your search», SIN-CUPO, con el aviso del portal
    y `mk_f<fila>_detenida`. Hasta el encargo 40 bastaba cualquier botón o enlace «Book» a la vista más abajo de 100 px,
    y en los 14 desenlaces de `logs/` terminó así, a los 2 s: el 29-09, lo más probable es que con uno de los 3 enlaces
    «Book» a `/booking/new` del encabezado o el pie, que trae cada una de las 9 páginas de MAERSK guardadas, y la fila
    quedó REVISAR. La señal de tarifas (un importe «USD» a la vista) sigue: en las 8 páginas de «Select sailing»
    guardadas, los 52 importes van dentro de una tarjeta. Como la lista, el detector no mira si la tarjeta se ve. El
    REVISAR de la guarda de MAERSK no se alcanza (sin nave, la función ya volvió), y `test_candado` lo fotografía:
    queda. El texto «MAERSK: no se abrió el formulario /book/» va en su propio literal por lo mismo. Desde el encargo
    41, el motivo de SIN-CUPO dice también el origen y el destino con que buscó (`_mk_motivo_sin_cupo`, decisión de
    Marcelo, `CICLO-origen-y-destino.md`): de cada campo, la sugerencia que pulsó `_mk_ciudad` y, si el campo no quedó
    con ella, lo que quedó (`_mk_ruta_buscada`; desde el encargo 43 queda con ella, salvo mayúsculas, tildes o
    espacios de más: si no, `_mk_ciudad` corta); sin la palabra «elegida», porque el registro del panel pinta de verde
    la línea que la trae (`clase`, en `JS_INDEX`).
  - **El origen y el destino, con la regla de Marcelo** (encargo 43, `CICLO-maersk-elige-exacto.md`; de los encargos 40
    al 42, un FRENO). `_mk_ciudad` escribe la ciudad (la parte de la celda antes de la primera coma), espera las
    sugerencias que traen sus primeros 5 caracteres ASCII, sin tildes (la Ñ como N; hasta el encargo 46, la letra con
    tilde y la ñ se caían) y con los espacios de a uno (`_mk_sugerencias`), y pulsa, entre las Container Yard, la única
    cuya parte antes de la primera coma, sin lo que
    va entre paréntesis, es lo escrito, sin distinguir mayúsculas ni tildes y con los espacios de a uno
    (`_mk_las_exactas`, `_mk_base`, `_mk_plano`; los signos cuentan, y los paréntesis se quitan solo de la sugerencia).
    «Container Yard» está en la raíz shadow de la opción, donde lo ve el filtro de Playwright y no `text_content`
    (`MK_CONTAINER_YARD`): la Store Door gemela, con el mismo texto, no cuenta. Decide con la lista quieta (dos lecturas
    iguales seguidas de sus Container Yard, como `_mk_resultados_quietos`). Después comprueba que el campo quedó con el
    texto entero de la sugerencia, comparado como la regla (`_mk_plano`) y leído hasta `MK_LECTURAS_CAMPO` veces (5,
    cada 0,4 s; hipótesis). Si no hay una sola, o el campo no calza, vuelve a escribir una vez y, si tampoco, corta él
    mismo, con lo que buscaba (`_mk_sin_una_exacta`, la sugerencia en el campo, la lista o el campo): NO ENVIADA con
    `mk_f<fila>_sin_objetivo`. Elige de la lista que dejó en la evidencia: si al dejarla no había una sola, en esa
    vuelta no pulsa. Hasta el encargo 43 pulsaba la primera con «container yard» o, si no había, la primera, y miraba
    solo que el campo trajera los 4 primeros caracteres, que lo tecleado también trae: el 29-09 y el 30-09 a las 15:21,
    la fila 10 eligió «ciudad + 1 palabra, país» en vez de «ciudad, país» (la del 27-09, que encontró la nave), y la
    búsqueda volvió vacía.
    - Medido sin red con el código del encargo 43: en las 4 listas del 30-09, la regla elige la sugerencia que el
      informe del encargo 42 da por correcta. En `logs/`, 30 de las 32 elecciones de MAERSK tienen su forma (las 2 que
      no, los dos destinos equivocados); en las 6 reservas que llegaron a la guarda, el destino la tiene, pero su lista
      no se guardó: si era la única no está medido.
    - El país no viene aparte en la lista: la raíz shadow trae el tipo de lugar y su sigla (CY o SD), y cada Container
      Yard viene repetida, con el mismo texto, como Store Door (medido el 30-09, `CICLO-maersk-y-fila-sin-ruta.md`). Las
      otras cinco navieras eligen como antes: CMA, la primera con los mismos 5 caracteres, que desde el encargo 48 arma
      como MAERSK, sin tildes y con la Ñ como N (`_prefijo_de_la_lista`; decisión de Marcelo,
      `CICLO-calendario-cosco-y-cma.md`), y el lugar de entrega, la primera con «ramp»; ONE, la que trae la ciudad y
      está más arriba; HYUNDAI, la primera que la trae; MSC, la más
      corta a la vista que la trae; y COSCO, en el origen la que dice Chile y en el destino la que empieza con la ciudad
      y una coma, o la primera.
  - La fecha de zarpe: el día de carga de la planilla o, si falta o no se entiende, «Select tomorrow», y entonces
    avisa que busca desde mañana y no desde hoy (`_mk_fecha`). Marcelo decidió que busque desde hoy, pero sin el
    portal no se sabe si lo acepta (FRENO, `CICLO-cola-siete-items.md`). También avisa si el portal no aceptó la
    fecha escrita; una celda ilegible la avisa `_avisar_dia_carga`.

## Ejecutar y verificar

Requiere Python 3.13 (de Microsoft Store en esta máquina), `playwright`, `openpyxl` y `holidays` (los `.bat` los
instalan si faltan; holidays con `--timeout 5 --retries 0`, para no frenar el arranque sin red: así se rinde en unos
6 s, y sin esos límites tardó 69 s, medido el 2026-09-29). `opencv-python` + `numpy` solo para el puzzle de COSCO
(import perezoso).

```bash
python AQUASHIELD.py                          # panel web en http://127.0.0.1:8765 (modo normal)
python AQUASHIELD.py panel                    # panel Tkinter clásico (respaldo)
python AQUASHIELD.py <operador> one           # solo login; <naviera> o 'todas'; deja el navegador abierto
python AQUASHIELD.py <operador> cosco reservas  # reservas desde 'Reservas AQUASHIELD.xlsx' (sin emitir)
python tests/correr.py                        # red de verificación offline (de 5 a 12 min, 30-09 y 01-10); ver abajo
python -m playwright show-trace "logs\<carpeta>\traza.zip"
```

- Los `.bat` lanzan con `pythonw` (sin consola): los `print` no se ven; todo queda en `logs\`.
- Al arrancar, `lanzar_web` pide a una instancia previa ociosa que se apague y, si el puerto 8765 sigue
  ocupado, **mata con `taskkill` el proceso que lo escucha**; después prueba 8766–8768. Tiene un
  watchdog que apaga el servidor tras 90 s sin sondeos de `/api/estado`.
- Para depurar un portal sin correr toda la planilla: `AQUASHIELD_SOLO_PRIMERA=1` (solo en el modo
  consola `reservas`) y `AQUASHIELD_TRAZA=1`.

Variables de entorno de afinamiento (todas opcionales): `AQUASHIELD_DESCUBRIR` (vuelca opciones de
desplegables/HTML de campos y captura página completa), `AQUASHIELD_CAPTURA_FULL`, `AQUASHIELD_ZOOM`
(factor de escala de Chrome, 0.5–1, por defecto 0.65), `AQUASHIELD_LOGIN_MAX` (espera del login COSCO,
240 s), `AQUASHIELD_PAUSA_SEG`, `AQUASHIELD_AUTOCLOSE`, `AQUASHIELD_GENSET`. `AQUASHIELD_PRIMERA_NAVE` ya no
existe: en MAERSK tomaba la primera salida que se podía reservar, sin calzar la nave (`CICLO-solo-la-nave-pedida.md`).

## Red de verificación offline (`tests/`)

Fotografía lo que el programa hace HOY (rarezas incluidas) sin abrir ningún portal. `unittest` de la
biblioteca estándar; 573 pruebas al 2026-10-02 (el corredor imprime el número vigente), y cada una tiene
al menos un defecto inyectado que la tumba. `test_envio` corre en **Node** el JavaScript que decide (la
lectura del estado en el panel y los de COSCO) sobre un `document` falso: sin Node, esas pruebas fallan.

```bash
python tests/correr.py                 # suite; también compara una foto de los originales antes y después
python tests/correr.py --mutaciones    # censo: cada mutación de tests/mutaciones.py debe tumbar su prueba
python tests/correr.py --todo          # las dos cosas (más de una hora; el censo solo, 52 a 97 min del 28-09 al 01-10)
cd tests && python -m unittest test_planilla.TestLectorWeb.test_web_one    # una sola prueba
```

- **Nunca importes `AQUASHIELD.py` desde la raíz en una prueba**: usa `soporte.cargar()`, que carga una
  COPIA en una sandbox del temporal. Desde la raíz, `BASE` apunta a la planilla, `config.json` y
  `perfiles/` reales. El arnés trae trampas (navegador, procesos, red externa y Playwright levantan
  `EfectoReal`) y exige las tres llaves del candado apagadas antes y después de cada prueba.
- **Nunca uses el puerto 8765** en una prueba: `lanzar_web` cierra con `taskkill /F` a quien lo ocupe.
- Una página falsa no avisa de lo inesperado solo levantando una excepción: el programa se la traga en su `try`. Que lo
  anote, y que la prueba exija esa lista vacía (`PaginaRevision` y `PaginaShipper` de `test_clics`, del encargo 38, y
  `SoloLee` de `test_evidencia`, de antes). Lo mismo con lo esperado: una página falsa que acepta cualquier acción sin
  anotarla deja pasar a un reservador que sigue cuando no debía (`PaginaHastaLaRuta` de `test_clics` anota, desde el
  encargo 42, cada acción de sus localizadores, de la página, del teclado y del mouse, y cada JavaScript, sin un
  `__getattr__` general: lo que no tiene sigue fallando). Y una prueba no depende de lo que la máquina tenga instalado:
  las del retiro usan una librería holidays falsa.
- `tests/correr.py` crea al empezar su carpeta de trabajo en `%TEMP%` (`aquashield_mut_*`) y la borra en un `finally`,
  que no corre si el proceso se mata y calla si no puede borrarla (`ignore_errors=True`): una corrida cortada la deja.
  Se borran por su prefijo, sin ninguna corrida viva (encargo 37: 29 carpetas y 2,78 GB de copias de las fuentes del
  programa, mutadas o no).
- Las sandboxes de las pruebas (`aquashield_red_*`) las borra `soporte` al salir de cada proceso, y calla si no puede
  (`ignore_errors=True`); un proceso que se mata no borra la suya. El 30-09 a las 12:32 había 1408, del 24 al 30-09
  (3453 archivos, 1,15 GB): 470 completas y 938 a medio borrar, vacías o con otra cosa. Las 7 de ese día están
  completas, una por cada corrida completa
  de la suite o del control del censo: lo más probable, por el código, es
  `test_web.TestArranqueDelPanel.test_instancia_previa_ocupada_no_se_toca`, que termina con `hijo.kill()` a un hijo que
  creó la suya con `soporte.cargar()` (encargo 41, `CICLO-origen-y-destino.md`; la causa, medida a medias).
- El control del censo (la copia sin mutar, con las pruebas elegidas) corre por tandas (`por_tandas`): Windows no crea
  un proceso con una línea de comando de más de 32.767 caracteres (WinError 206), y con las 520 pruebas en una sola, el
  censo completo se cayó a los 2 minutos (encargo 41, `CICLO-origen-y-destino.md`).
- Una prueba que lee un archivo del programa (el `.py`, los `.bat`, `config.example.json`) lo lee de
  `soporte.FUENTES`, no de la raíz: el censo deja ahí la copia mutada, y desde la raíz su mutación no muerde.
- Las pruebas son fotos: si corriges una rareza del programa, su prueba cae a propósito; actualiza la
  foto en el mismo cambio. Toda prueba nueva necesita su mutación en `tests/mutaciones.py` (el censo
  falla si no). Casos sintéticos solamente: nunca copies logs ni datos reales; los valores de empresa
  que quedan en el código (el nombre de la empresa) se comparan por hash. Los contratos y el código de Shipper de
  HYUNDAI ya no están en el código (encargo 44): sus pruebas los ponen en una configuración sintética, y no se
  comparan por hash (el de un código corto se revierte probando).
- Antes de cada commit: `python tests/sonda_secretos.py --dry-run`, `git add` y
  `python tests/sonda_secretos.py`; las dos tienen que dar 0 (`CICLO-cola-siete-items.md`).
  - Bloquea las claves y los usuarios de `config.json`, las rutas prohibidas y el nombre o el apellido del
    operador: cada palabra de 4 letras o más de su clave, su descripción y su `nombre_en_pantalla`, sin
    mayúsculas ni tildes. La plantilla no cuenta.
  - Desde el encargo 44 bloquea también los contratos y los datos de la cuenta de `config.json` (`datos_de_cuenta`:
    los `contrato*` de cada naviera, `contratos_por_defecto` y `codigo_shipper_hyundai`), los generadores de
    material (`crear_*.py`, `generar_manuales.py`) y las imágenes: `IMAGENES_PERMITIDAS` quedó vacía.
  - En `--almacen` el nombre y los datos de la cuenta solo informan: `historial-local` los trae. Ese modo no mira
    las rutas: cada objeto va por su tipo y su hash.
  - `--negativo-clave`, `--negativo-ruta` y `--negativo-nombre` tienen que dar 1.
  - `test_sonda` la carga de `soporte.FUENTES / "tests"` si el censo dejó ahí su copia mutada; si no, del repo.
- Cobertura de funciones (opcional): `AQUASHIELD_COBERTURA=<prefijo>` escribe `<prefijo>.<pid>` con las
  funciones ejecutadas. No cubre: los flujos de login y reserva en los portales, el JavaScript inyectado
  (`_JS_*`) ni el panel Tkinter. Detalle y cobertura por naviera en `CICLO-red-verificacion.md`.

## Arquitectura de `AQUASHIELD.py`

El archivo está dividido en secciones con encabezados `# ====…` (búscalas con Grep; los números de
línea cambian). De arriba hacia abajo:

1. **Constantes por defecto** acordadas con operaciones (`TEMP_REEFER`, `PESO_REEFER`, `COSCO_*`) y el
   candado `es_modo_emision()`.
   - Los avisos que no son de un paso salen por `_avisar_en_pantalla_y_log`: por la corrida en curso o, sin
     corrida, por la consola y el panel. Son el de la llave de emitir y el del peso y la temperatura de
     `config.json`.
   - ONE, MSC, HYUNDAI y MAERSK tienen **forma medida** en sus capturas (`FORMA_BOOKING`: la etiqueta de la
     confirmación y el número con su prefijo y sus dígitos). `numero_tras_envio` la busca en la página, sus marcos
     y las raíces shadow, y reintenta hasta 15 s.
   - CMA y COSCO no tienen forma medida: sus capturas tras el envío no muestran confirmación
     (`CICLO-numero-booking.md`). Por eso **nunca llegan a EMITIDA** hasta que se midan.
   - El lector viejo, `extraer_numero_booking`, se borró (`CICLO-cola-nueve-items.md`).
   - Después viene `_resultado_envio` (ver el candado).
2. **`Registro`**: log con marca de tiempo a `log.txt` + callback `on_log`; `captura()` guarda PNG en la
   misma carpeta. Usa `reg.paso()` / `reg.info()`, no `print`.
3. **Utilidades**: `esperar_hasta` (espera condicional; prefiérela a `esperar`, que duerme fijo),
   `click_si_existe`, `rellenar`, `pausa_manual` (pide intervención humana vía `on_pausa`).
4. **Login por naviera** `login_<x>(page, creds, reg, on_pausa=None) -> bool`, registrados en
   `NAVIERAS = {clave: (nombre, login)}`. CMA tiene DataDome (slider) y COSCO un validador tipo puzzle:
   se intenta resolver solo y, si no, se pausa hasta que el operador pulse «Ya lo resolví». Medido en las corridas
   del 2026-09-21 al 26 (`CICLO-inicio-de-todas.md`) y decidido en `CICLO-cierre-de-frenos.md`:
   - ONE: después del login, `login_one` espera `ONE_TRAS_LOGIN`, www.one-line.com/one-ecom/…, donde terminaron los 4
     logins nuevos medidos. Hasta `4948e16` esperaba ecomm.one-line.com/one-ecom, que ya no aparece: la espera vencía a
     los 25 s («no confirmé redirect en 25s») y cada login tardaba unos 32 s.
   - MSC (decisiones de Marcelo, encargo 45, `CICLO-login-msc-y-maersk.md`): `login_msc` parte de www.mymsc.com,
     pulsa el «Next» y el de entrar por su texto (`_msc_entrar`), y cada espera termina con lo primero que llega: la
     sesión, el error del portal o el campo que sigue (`_msc_esperar`, cada `MSC_SONDEO` s hasta `MSC_SONDEOS` veces,
     unos 30 s; hipótesis). La sesión se reconoce por su página (`_msc_sesion`: /myMSC/welcome o eBooking), y el error,
     por la página de error de Chrome o la del propio MSC (`_msc_error`, `MSC_TEXTOS_DE_ERROR`).
     - **El error tras el «Next»** (el 502 de TriggerOidcLogin): espera `MSC_PAUSA_RECARGA` s (20; hipótesis), recarga
       esa página una sola vez y espera solo el campo de la clave, la sesión o el error (`_msc_recargar`; decisión de
       Marcelo, encargo 47, `CICLO-msc-recarga-y-corrida-02-10.md`). No escribe ni pulsa nada: la clave, si aparece su
       campo, la escribe `_msc_entrar` por primera vez; si vuelve el campo del usuario, no lo escribe, y el login queda
       sin la sesión. El usuario no se espera con el mismo selector: `.first` miraría solo el primer campo de la página.
       La página falsa del login anota cada recarga, también la que no se espera, porque `_msc_recargar` atrapa su
       falla.
     - Ante el error (el que sigue tras la recarga, o el del botón de entrar) va una sola vez a eBooking
       (`MSC_EBOOKING`) y comprueba la sesión (`_msc_tras_el_error`); no vuelve a iniciar sesión, porque el portal
       podría bloquear la cuenta. Sin la sesión, cada fila de MSC queda NO ENVIADA con `MSC_SIN_SESION`, en el panel y
       en la consola (`SIN_SESION`; con las otras navieras, sigue sin estado).
     - Hasta el encargo 45 repetía el login hasta 2 veces tras un 502 (`MSC_REINTENTOS_502`) y recargaba si salía tras
       el «Next»: el 2026-10-01 tardó 214 s y dio por iniciada una sesión que no existía, porque `_msc_logueado`
       aceptaba la página de error de MSC. La recarga y los reintentos dejaron la sesión en 7 de los 10 logins con error
       de logs/, sin volver a enviar la clave. Del encargo 45 al 47 no recargaba: el 2026-10-02 por la mañana, en los 2
       logins (el de solo login y el de la corrida), el «Next» dio el 502 y la ida a eBooking llevó a la portada de
       myMSC, sin la sesión.
     - La tarde del 2026-10-02, con la recarga (encargo 49, `CICLO-corridas-de-la-tarde-02-10.md`), el «Next» pasó en
       los 3 logins, así que la recarga no actuó. En 2 (el de solo login y el de la corrida de las seis), el 502 llegó
       en la vuelta a myMSC, después de la clave, y la ida a eBooking llevó otra vez a la portada; el tercero, 5 min
       después, entró. Tras un error, la ida a eBooking no dejó la sesión en ninguna de las 4 veces medidas.
     - Medido en el historial del perfil: b2clogin acepta la clave e identityserver acepta su vuelta; el error lo da
       www.mymsc.com, en TriggerOidcLogin tras el «Next» o en la vuelta desde identityserver. Antes del 21-09, 35 de 35
       logins llegaron a myMSC en su primera pasada; desde entonces, 10 de 16 hasta el 01-10, y 1 de 5 el 02-10. Si es
       la protección contra robots, no está medido: falta la respuesta del portal (estado, cabeceras, cuerpo).
   - CMA: con el aviso «We are improving the eBusiness area» (mantenimiento), el login entra, pero Click & Book no
     carga. `reservar_cma` lo reconoce apenas abre Click & Book (`_cma_en_mantenimiento`), y la fila queda NO ENVIADA
     con `CMA_MANTENIMIENTO`, «el portal de CMA está en mantenimiento», y la captura `cma_f<fila>_mantenimiento`. Hasta
     `4948e16` cortaba en el Origen, con un motivo que hablaba de la sugerencia del puerto.
5. **Reserva por naviera** `reservar_<x>(page, reserva, creds, reg, on_pausa=None) -> (estado, detalle)`,
   registrados en `RESERVADORES`. Cada una trae sus helpers con prefijo (`_one_*`, `_msc_*`,
   `_cosco_*`, `_hmm_*`, `_mk_*` para MAERSK, `_cma_*`) y constantes JS inyectadas `_JS_<NAV>_*`.
   Estados antes de la guarda: `OK-EJEMPLO`, `REVISAR`, `ERROR`, `DETENIDO`, `SIN-CUPO` (MAERSK, con «no sailings for
   your search»; el panel lo pinta «sin cupo» desde el encargo 40: hasta ahí mostraba «SIN-CUPO», pero dejaba el N° en
   «procesando…» y la fila marcada en curso), y `NO ENVIADA` cuando un paso no encuentra su objetivo
   (`ObjetivoNoEncontrado`, ver el candado), cuando no queda una sola salida, cuando CMA está en mantenimiento, cuando
   la salida pedida ya no se puede reservar (MAERSK), cuando MAERSK no abre el formulario, lo deja incompleto, no puede
   pulsar un solo «Continue to book» o «Continue» para pasar a la selección de nave, no avanza en «Booking Information»,
   no puede pulsar el «Book» de la salida elegida, aunque la nave esté (encargo 46), no puede pulsar un solo «Continue»
   en «Recommended services», elegir la fecha de retiro, escribir la referencia, elegir a AQUACHILE como Shipper,
   pulsar «Review booking» o marcar la casilla de los términos, cuando la fila no pide
   una nave o HYUNDAI no ofrece mantenerla (ver «Solo la nave que la fila pide»), o cuando a la fila con nave le falta
   el puerto de carga o el destino, o un ayudante de origen, destino o lugar de entrega no eligió ninguna sugerencia
   (ver «Antes de la guarda no hay clics a ciegas», encargo 42), cuando el login de MSC no deja la sesión iniciada
   (encargo 45), o cuando New Booking de COSCO no muestra su formulario (encargo 48). `REVISAR`, entre otros (en MAERSK
   y en COSCO, solo ese), cuando la nave no apareció ni ampliando la búsqueda: el motivo dice hasta qué fecha buscó (ver
   «Ampliar la búsqueda»). Después: `EMITIDA`, `ENVIADA – REVISAR EN PORTAL`,
   `NO ENVIADA`. El panel los pinta con
   `lecturaEstado` (en `JS_INDEX`):
   un estado nuevo necesita su rama ahí. `OK-EJEMPLO` es «lista», no «emitida»: la columna «N° reserva emitida» dice
   «lista para emitir» y la píldora la cuenta aparte (`cuentaCorrida`); hasta el encargo 34 decía «✓ Confirmada».
   COSCO espera el resultado en `_cosco_esperar_resultado` (`CICLO-revision-corrida-completa.md`):
   - pulsa **una sola vez** el «Submit» que está dentro de la ventana «Reminder», identificada por su título y su
     texto (`_JS_COSCO_SUBMIT_DEL_REMINDER`). Nunca «el último Submit» de la página: las reservas se creaban igual;
   - después solo espera, hasta `COSCO_ESPERA_CONFIRMACION_SEG` (180 s, hipótesis no medida);
   - separa los errores de validación (`_JS_COSCO_ERRORES`) del aviso del portal.

   Antes de la guarda, COSCO:
   - Espera que el formulario de New Booking (su marco bkg2) muestre «Origin City», hasta 20 vueltas de 1,5 s. Sin el
     marco o sin el campo, NO ENVIADA, con lo que faltó y los segundos desde que abrió New Booking, y deja la captura de
     la ventana y el HTML de la página y de sus marcos (`_cosco_sin_formulario`, `cosco_f<fila>_sin_formulario`;
     decisión de Marcelo, encargo 48, `CICLO-calendario-cosco-y-cma.md`). En `reservar_cosco`, REVISAR queda solo para
     la nave no encontrada (`test_revisar_solo_si_la_nave_no_esta`). Hasta el encargo 48 quedaba REVISAR, y el HTML no
     se guardaba (sin los campos, solo con `AQUASHIELD_DESCUBRIR`): así quedó el 2026-10-02, con la página mostrando sus
     pasos sin el formulario (`CICLO-msc-recarga-y-corrida-02-10.md`).
   - Con más de un itinerario para la nave, elige la próxima salida (`_cosco_elegir_itinerario`, ver abajo). Si no
     queda uno solo, NO ENVIADA con la lista en la evidencia, y nunca el primero.
   - Su CONTROL lee Size Type por el texto visible del desplegable. Si no puede, dice «no pude leer», nunca «VACÍO».
   - Esto está en `CICLO-cola-nueve-items.md`.

   ONE espera los itinerarios por sus tarjetas (`_ONE_TARJETAS`) en `_one_esperar_resultados`
   (`CICLO-cola-cuatro-items.md`). `wait_for_selector` mira solo el primer elemento que calza, así que una
   espera no lleva selectores genéricos: el de antes calzaba primero con una lista vacía y vencía siempre.

   **La próxima salida** (decisión de Marcelo, `CICLO-proxima-salida.md`): entre varias salidas de la nave de la
   fila, `_proxima_salida` elige la próxima desde `_desde` (hoy, o el día de carga si la fila lo trae y es
   posterior; ONE también, desde `0e15b8a`). Entre las del mismo día, la de menor tiempo de tránsito
   (`_menor_transito`; los transbordos no cuentan, `CICLO-cola-tres-items.md`); cada naviera pasa el suyo
   (`_one_transito`, `_msc_transito`, `_cosco_transito`, `_mk_transito`, `_hmm_transito`), y uno que no se lee, o de
   cero o menos, no sirve (`_transito_legible`). Cuando el tránsito decide, `_anotar_desempate` lo deja en `log.txt`.
   Con empate (el mismo tránsito, o uno que no se lee), sin fecha legible o todas ya salidas, la reserva queda NO
   ENVIADA con la lista, y el motivo dice por qué el tránsito no desempató; nunca se elige la primera ni la última.
   Solo cuentan las salidas que el portal deja reservar. Las tarjetas de «Select sailing» de MAERSK vienen a veces
   repetidas, idénticas en su HTML entero, con sus raíces shadow (7 de las 8 listas guardadas, todas desde el 25-09, en
   12 grupos; el 30-09 a las 15:31, la salida de la nave, 3 veces, y la reserva quedó NO ENVIADA por el empate). Desde
   el encargo 43 cuentan como una sola salida, y se pulsa el «Book» de la primera (`_mk_sin_repetidas`, con el «igual»
   que da `_JS_MK_SALIDAS` cuando se le piden `iguales`; decisión de Marcelo, `CICLO-maersk-elige-exacto.md`). El HTML
   entero se arma como el de la evidencia (`_JS_HTML_ENTERO`). Si difieren en cualquier cosa, o el HTML de una no se
   pudo leer, cuentan aparte y el empate sigue.
   - Si la fila trae viaje y ninguna salida de la nave lo trae, MAERSK (`_mk_elegir_nave`) y COSCO
     (`_cosco_sin_el_viaje`) no eligen: la reserva queda NO ENVIADA con la lista, y el motivo dice «ninguna de las N
     opciones de la nave trae el viaje de la fila» (decisión de Marcelo, `CICLO-cierre-de-frenos.md`). Hasta `4948e16`
     elegían entre todas las de la nave, sin avisarlo. Desde el encargo 32 cortan después de ampliar la búsqueda; hasta
     `4cae528`, con lo primero que veían.
   - MAERSK, si el viaje de la fila está, pero solo en salidas sin «Book», no amplía: NO ENVIADA con
     `SALIDA_NO_RESERVABLE`, «la salida pedida ya no se puede reservar» (decisión de Marcelo,
     `CICLO-ampliar-la-busqueda.md`). Sin viaje en la fila, lo mismo si, ampliada la búsqueda, la nave está solo sin
     «Book». Hasta `4cae528` quedaba REVISAR, como una nave que no está: así terminaron las dos corridas del 26-09.
     **Pero en esas dos, y en las dos del 27-09, la salida pedida sí traía su «Book»:** el `mc-button` lleva su texto
     dentro de su raíz shadow y el programa lo contaba por el texto, que viene vacío; daba 0 en las 52 tarjetas de las 6
     listas guardadas. Desde `a07d465` se cuenta por su atributo `label` (`_JS_MK_SALIDAS`; encargo 34,
     `CICLO-one-y-maersk-eligen-la-nave.md`). La decisión sigue: en lo guardado, 10 tarjetas no traen ningún «Book».
   - COSCO: la salida de la tarjeta, «Sep27 (Sun)», con el año por el día de la semana (`_cosco_fecha_tarjeta`).
     La única fecha de la fila es el CY Cutoff: hasta `135e765` se leía como la ETD. El tránsito es la llegada menos
     la salida de la tarjeta, solo si trae exactamente dos fechas.
   - MSC: la ETD de su tarjeta. Busca desde `_msc_desde`, hoy; hasta `384d3ce`, desde hoy + 18. El tránsito es la
     ETA menos la ETD, solo si la tarjeta trae una sola ETA.
   - ONE: lee sus tarjetas con `_JS_ONE_TARJETAS_NAVE` y pulsa con `_JS_ONE_CLIC_TARJETA`. El tránsito es la
     llegada menos la salida, sus dos fechas textStyle-h5. Desde el encargo 34, la directa primero, como HYUNDAI
     (abajo). Cada tarjeta lo dice en su único elemento `TransshipmentInfo_transshipment-container`, «Direct» o
     «Transshipment» (medido en las 128 tarjetas de las 4 listas guardadas: cada nave, 4 salidas del mismo día y una
     sola directa), y `_JS_ONE_CLIC_TARJETA` vuelve a leer la elegida antes de pulsar: la nave, la salida y si es
     directa.
   - MAERSK: lee sus salidas con `_JS_MK_SALIDAS` y pulsa el «Book» de la elegida (`_mk_pulsar_book`). El tránsito es
     su «Transit time», con días y horas. El «Book» se cuenta por el atributo `label` del `mc-button` (arriba).
     `_mk_pulsar_book` trae a la vista la tarjeta de la elegida (`scroll_into_view_if_needed`, sin clics ni teclas) y
     después pulsa su «Book» solo si está a más de 100 px del borde de arriba de la ventana (decisión de Marcelo,
     encargo 46, `CICLO-maersk-pulsa-el-book.md`). Si aun así no lo pulsa, la fila queda NO ENVIADA con
     `mk_f<fila>_detenida` y un motivo que dice que la nave estaba y por qué no pudo (`_mk_book_sin_pulsar`). Hasta el
     encargo 46 miraba la altura antes de traerla y, si no pulsaba, seguía por la rama de la nave que no está: así quedó
     REVISAR, con «no está en los itinerarios», la fila del 2026-10-01, cuya salida elegida, la primera de 3 copias,
     había quedado arriba de la ventana (encargo 45, `CICLO-login-msc-y-maersk.md`). Si la tarjeta (`mc-card`) no
     tuviera caja propia (sus estilos no viajan en el HTML guardado), Playwright la trae igual: medido con
     `display: contents` en una página sintética (`CICLO-maersk-pulsa-el-book.md`).
   - Medido en las listas del 2026-09-25: en ONE, MSC y COSCO el tránsito que muestra la tarjeta es la llegada menos
     la salida en todas; en MAERSK, 4 horas menos, porque cada fecha va en la hora de su puerto.
   - HYUNDAI (desde el encargo 32, `CICLO-ampliar-la-busqueda.md`): entre las tarjetas cuya «1st Vessel» es la nave de
     la fila y se pueden reservar (`_hmm_elegir_nave`). La salida y la llegada son las fechas de sus dos
     `.place-content` (`_JS_HMM_TARJETAS`); el tránsito, la llegada menos la salida, que es el «N Days» de la tarjeta en
     las 12 medidas del 26-09. Hasta `924485a` elegía ahí la 5.ª, que llega antes que la 6.ª el mismo día. Hasta
     `4cae528` pulsaba la primera en la página cuyo texto traía la nave (la 4.ª, que la trae como «Main Vessel»).
     Pulsa el «Book Now» de la elegida solo si, al volver a leer la lista en el mismo JavaScript, esa tarjeta sigue
     siendo la elegida: su «1st Vessel» calza, se puede reservar, sale el mismo día y es directa o no como la elegida
     (`_JS_HMM_CLIC_TARJETA`; lo de la directa, desde `96a0d2b`).
     Desde el encargo 33 (decisión de Marcelo, `CICLO-ampliar-msc-y-cma.md`), entre las del día de la próxima salida,
     la directa: si alguna lo es, las con transbordo de ese día se descartan (`_directas_primero`, común con ONE
     desde el encargo 34; hasta entonces `_hmm_directas_primero`), y solo si todas tienen transbordo decide el
     tránsito. Cada tarjeta lo dice en su único `.mid-state`, «Direct» o «Transshipment» (medido en las 12 del 26-09);
     una que no lo dice cuenta como con transbordo. Así, en las dos listas guardadas elige
     la 6.ª (directa, 35 días de tránsito) y no la 5.ª (con transbordo, 33).
   - CMA todavía no la aplica: falta el HTML de su lista, que se guarda desde `50e3f04`.
   - Con la regla, ONE y COSCO empataban casi siempre: la misma salida con otro transbordo. El tránsito resuelve
     los 2 empates medidos de COSCO y 6 de los 8 de ONE (`CICLO-cola-siete-items.md`). En ONE quedaban empates entre la
     directa y una con transbordo del mismo tránsito (8 de 32 naves en las 4 listas guardadas; así quedaron NO ENVIADA
     las dos corridas del 27-09): desde el encargo 34 los resuelve la directa, decisión de Marcelo
     (`CICLO-one-y-maersk-eligen-la-nave.md`). En 6 de las 32, la directa llega 1 día después que la que elegía el
     tránsito.

   **Ampliar la búsqueda** (decisiones de Marcelo, `CICLO-ampliar-la-busqueda.md` y `CICLO-ampliar-msc-y-cma.md`): si
   la nave de la fila no está en lo que el portal muestra de entrada, la naviera amplía su lista como su portal lo
   permite (una opción o un enlace, por su texto; MSC, bajando por la lista, sin pulsar nada) y vuelve a leerla, hasta
   encontrarla o hasta que el portal no deje ampliar más. Si no aparece, REVISAR, y el motivo dice hasta qué fecha buscó
   (la última salida que mostró el portal, `_hasta_donde_busque`) y por qué dejó de ampliar (`NO_AMPLIA_MAS`, o por qué
   no pudo). ONE no amplía.
   - MAERSK (`_mk_ampliar`): «Search more sailing options», tanda por tanda. Espera hasta `MK_ESPERA_MAS` (40 s,
     hipótesis) a que se habilite, porque mientras carga el portal lo deshabilita, y otro tanto a que lleguen salidas
     nuevas. Si no hay botón o no llega ninguna nueva, el portal no deja más. Tope, `AMPLIAR_MAX` (12 tandas,
     hipótesis). Con viaje en la fila, busca esa salida. Hasta `4cae528`: 3 tandas de 7 s, y el 25-09 se rindió con el
     botón cargando. Si al dejar de ampliar la nave está, pero no la salida pedida, anota por qué dejó de ampliar
     («dejé de ampliar la búsqueda: …»): el motivo de la NO ENVIADA no lo dice.
   - COSCO (`_cosco_ampliar`): elige en «Sailing Within N Weeks» la opción más larga (medido: de 2 a 8, con 2 elegida),
     con clic real, y vuelve a buscar con «Search Service», una vez; también si la nave está sin el viaje de la fila.
     Reconoce el campo por su lista de opciones, que nombra en `aria-controls`, y las semanas elegidas por la marca de
     la opción (`_JS_COSCO_SEMANAS`): el valor del campo no queda en el HTML guardado.
   - ONE: busca las 8 semanas que pide la nota de la planilla, y si la nave no está, REVISAR con la fecha y
     `ONE_SOLO_8` (decisión de Marcelo, `CICLO-ampliar-msc-y-cma.md`). De `05cfdb7` a `924485a` probaba una opción de
     más de 8 semanas.
   - HYUNDAI (`_hmm_ampliar`): elige en «Duration» (`#srchSelWeeks`, de 1 a 8 semanas) la más larga y vuelve a buscar
     con «Retrieve».
   - MSC (`_msc_bajar`): no tiene botón de ampliar; según Marcelo, las demás naves aparecen al bajar por la lista.
     `_JS_MSC_BAJAR` lleva al final cada ancestro de las tarjetas con desplazamiento, y la ventana, sin pulsar nada;
     después espera hasta `MSC_ESPERA_MAS` (15 s, hipótesis) tarjetas nuevas con su «Select» a la vista, y repite hasta
     `AMPLIAR_MAX`. Medido en los `log.txt` del 21 al 26-09: al cargar ya traía 25 a 27 itinerarios con su «Select» a la
     vista, aunque en pantalla se vean 4 o 5; si al bajar llegan más, no está medido.
   - CMA (`_cma_ampliar`): pulsa «Cargar N siguientes resultados» (N cambia), el único enlace o botón a la vista con ese
     texto entero (`CMA_CARGAR_MAS`), hasta encontrar la nave o hasta que el enlace desaparezca, con `AMPLIAR_MAX`, y
     espera hasta `CMA_ESPERA_MAS` (20 s, hipótesis) rutas nuevas. Si deja de cargar, el motivo dice por qué:
     `CMA_SIN_ENLACE` («ya no vi el enlace…»), que pulsó y no llegaron rutas nuevas, o el tope (hasta `2044222`, «el
     portal no deja ampliar más» para los dos primeros). El texto es dato de Marcelo: ninguna corrida guardó la lista
     entera. La fecha de cada ruta es la primera `.date` de su `.wrap-card`, con la forma «Lunes, 05-oct-2026»
     (`_cma_fecha_tarjeta`). Hasta `ff76fea` pulsaba una vez el primer botón o enlace con «mostrar más», «ver más»,
     «show more» o «más viajes» (Nota H23), que por su expresión nunca habría pulsado este enlace y en `logs/` nunca se
     pulsó.

   **La nave con todas sus palabras** (decisiones de Marcelo, `CICLO-cola-tres-items.md` y `CICLO-cola-seis-items.md`):
   en las seis navieras, una tarjeta calza con la nave solo si trae todas las palabras de la nave de la fila, cada una
   como palabra entera y sin distinguir mayúsculas; sin palabras de nave, ninguna. Palabra entera: sin una letra o un
   número de `_LETRAS_DE_NAVE` pegado antes ni después («ANNA» no calza con «SAVANNAH»). Si ninguna calza, cada
   naviera sigue su camino de nave no encontrada.
   - Un solo ayudante: `_trae_la_nave` en Python (lo usan MSC y COSCO; COSCO, también para el viaje; MAERSK calza su
     viaje con `_palabraEn`) y
     `_JS_TRAE_LA_NAVE` al principio del JavaScript de ONE, HYUNDAI, MAERSK y CMA (`_JS_CMA_RUTAS`).
     `test_la_misma_regla_en_javascript` vigila que den lo mismo. Hasta `f68ce6c` bastaba que cada palabra fuera parte
     del texto.
   - Con qué compara cada una:
     - MSC, el campo «Vessel / Voyage» (`_trae_la_nave`);
     - ONE, el enlace de la nave de su tarjeta;
     - COSCO, una sola de sus naves de «Vessel / Voyage» (`_cosco_calzan`);
     - MAERSK, el valor de «Vessel/voyage», en orden, y su viaje también como palabra entera (hasta `c4df3ab`,
       como parte del texto);
     - HYUNDAI, el valor de «1st Vessel» de su tarjeta, la nave que sale de Chile (`_JS_HMM_TARJETAS`; decisión de
       Marcelo, `CICLO-ampliar-la-busqueda.md`). Hasta `4cae528`, el texto de toda la tarjeta: la nave de la fila estaba
       como MAIN VESSEL en una tarjeta, como 1ST VESSEL en otra y en los dos en una tercera. `_JS_HMM_INDICE_NAVE` queda
       solo para la interfaz anterior (`a.preview-area`);
     - CMA, todavía el texto de toda la tarjeta. Medido en un caso (la misma fila en las corridas del 24 y el 25-09,
       con los detalles abiertos, `CICLO-ampliar-msc-y-cma.md`): la nave que sale de Chile es el valor de «Buque
       principal» de la tarjeta, y también el «Buque» del primer tramo de «Mostrar detalles», desde el puerto chileno
       hasta Callao; «Primer servicio» es el nombre de un servicio; y `_JS_CMA_RUTAS` la encuentra. Calzar solo con
       «Buque principal» lo decide Marcelo.
   - Hasta `9051f43`: HYUNDAI aceptaba la primera palabra, que en la planilla es el prefijo de la naviera (así armó
     reservas con otro buque); ONE, la nave sin su última palabra o esa palabra sola; CMA, la nave sin sus prefijos;
     y MSC, COSCO y ONE calzaban con todas las tarjetas si la fila no traía palabras de nave.

   **Solo la nave que la fila pide** (decisiones de Marcelo, `CICLO-solo-la-nave-pedida.md` y
   `CICLO-cola-seis-items.md`): el programa nunca reserva una nave que la fila no pidió.
   - Una fila sin nave queda NO ENVIADA con el motivo «la fila no trae una nave para reservar», en pantalla, en
     `log.txt` y en la planilla, sin abrir el portal. Sin nave es (`_fila_sin_nave`): vacía, con «completar», con
     MANUAL, o sin una palabra de dos letras o números o más que no sea comodín ni prefijo de naviera. Las dos listas
     valen para las seis navieras: `NAVES_COMODIN` (AUTO, CUALQUIERA, LIBRE, NINGUNA, NONE, PRIMERA y DISPONIBLE) y
     `NAVES_PREFIJO` (MSC, CMA, CGM, HMM, ONE, COSCO, MV, HYUNDAI y MAERSK, los que se midieron en el código; MV no
     es una naviera, está porque venía en la lista medida; y CSCL y SHIPPING, por decisión de Marcelo en
     `CICLO-inicio-de-todas.md`: COSCO SHIPPING entra como sus dos palabras, igual que CMA CGM).
   - MANUAL, como palabra entera (`_fila_manual`, con `_palabra_en`; hasta `c4df3ab` bastaba que fuera parte del texto,
     y «MANUALMENTE» era MANUAL), tiene su propio motivo: «la fila está marcada para
     hacerse a mano». `/api/filas` trae las marcas `sin_nave`, `manual` y, desde el encargo 43, `sin_puerto` y
     `sin_destino` (`_con_su_marca`). El panel marca por
     defecto las filas sin nave que no son MANUAL, para que queden NO ENVIADA en la planilla, y deja sin marcar las
     MANUAL (`marcadaPorDefecto` usa `f.manual`).
   - El panel web y la consola apartan esas filas antes de abrir el navegador, y no lo abren si ninguna trae nave. Los
     seis reservadores llevan además `_con_la_nave_de_la_fila` y, por dentro, `_con_la_ruta_de_la_fila`, que corta la
     fila con nave y sin puerto de carga o sin destino (encargo 42; ver «Antes de la guarda no hay clics a ciegas»).
   - La consola ya no toma la nave de la columna F en ONE y MSC cuando la celda de la nave viene vacía, o si la hoja
     no tiene columna de nave: esa fila queda sin nave (`nave_de_la_f`). La F sigue decidiendo si la fila es una nota,
     si entra a la lista y el destino de ONE. Del lector de la consola no cambió nada más: es la única excepción que
     Marcelo autorizó en el encargo 29.
   - Ningún atajo elige sin calzar: MAERSK ya no tiene `AQUASHIELD_PRIMERA_NAVE`, HYUNDAI no quita palabras de la nave
     antes de calzar, MSC compara solo con «Vessel / Voyage» y COSCO solo con la fila de ese «Book now».
   - ONE no pulsa nada en «Vessel Information» (la nave pasó su cut-off y el portal ofrece elegir otra): antes de la
     guarda corta, NO ENVIADA, con su evidencia `one_f<fila>_sin_objetivo`.
   - El modal «Alternate Vessel Option» de HYUNDAI pregunta qué hacer si la nave pedida no estuviera disponible (Any,
     If within N weeks, o «I do not want to choose an alternate vessel»), y según la captura trae «Any» marcada. El
     programa lo mira al elegir la nave y, si Booking Details no aparece, otra vez. Si está, deja
     `hmm_f<fila>_otra_nave`, marca «I do not want to choose an alternate vessel» por su texto, comprueba que quedó
     marcada, y pulsa su único «OK» (`_hmm_mantener_nave`; decisión de Marcelo, `CICLO-ampliar-la-busqueda.md`):
     - si no hay exactamente una opción con ese texto, NO ENVIADA con `HMM_SIN_OPCION`, «HYUNDAI no ofreció la opción
       de mantener la nave pedida; la reserva no se envió»; si el clic no la deja marcada, o no hay un solo «OK», NO
       ENVIADA sin pulsar OK; si un clic falla, ERROR, como cualquier falla antes de la guarda;
     - si después del OK Booking Details no aparece y el modal sigue, no pulsa nada más: NO ENVIADA con `HMM_NO_AVANZO`
       y `hmm_f<fila>_otra_nave_sigue` (FRENO de Marcelo: si marcar la opción no deja avanzar sin otro clic, se frena).
       Si el modal apareció recién en la segunda mirada, lo mira una tercera vez para eso. Si el modal se cerró y
       Booking Details no aparece, REVISAR «HYUNDAI: no avanzó al paso Booking Details», como antes.
     Salió en las 8 reservas guardadas que llegaron a elegir nave, con otra nave elegida, y el 2026-09-26 también con
     la pedida. Hasta
     `a198645` el programa pulsaba el OK con lo que viniera marcado; hasta `4cae528` no pulsaba nada y cortaba, con
     «HYUNDAI ofreció otra nave en lugar de la pedida». El modal medido: tres radios `vessel-option`, cada uno en un
     `label.radio-area` con su texto, y `#vesselOptionSubmit` («OK»), sin `disabled`.
   - Hasta `a198645`: ONE y COSCO devolvían OMITIDO con la celda vacía, y HYUNDAI también con «completar». CMA tenía su
     propia lista y cortaba después de abrir el portal. El panel dejaba la fila vacía sin marcar.
6. **Orquestador de consola**: `cargar_config`, `ejecutar_login`, `ejecutar_reservas`.
7. **Panel Tkinter** `lanzar_panel()` con la identidad visual en `MARCA` (respaldo).
8. **Index web** (sección añadida después; reimporta con alias `_json`, `_th`, `_time`, `_os`, `_re`,
   `_dt`, respeta ese estilo ahí): servidor `http.server` local, estado compartido `_WEB` protegido por
   `_LOCK`, `_web_worker` en un hilo (un contexto de Playwright por naviera) y la API `/api/config`,
   `/api/credenciales`, `/api/planilla`, `/api/filas`, `/api/correr`, `/api/login`, `/api/estado`,
   `/api/continuar`, `/api/detener`, `/api/descargar`, `/api/apagar`. Una corrida sin filas elegidas no abre el
   navegador ni entra a ningún portal, y lo avisa.
9. **Front-end embebido**: `HTML_INDEX`, `JS_INDEX`, `CSS_INDEX` y `CSS_FUENTES` son strings de
   Python servidos desde memoria (el `.exe` debe quedar autocontenido). `CSS_FUENTES` lleva fuentes
   woff2 en base64 en líneas gigantes: **el Read falla si el rango las incluye** (cerca del final,
   justo antes de `main()`); lee esa zona con Grep o `sed -n 'a,bp' | cut -c1-200`.
10. **`main()`**: despacha entre consola, panel y web (si la web falla, cae al panel Tkinter).

Todo navegador se abre con `launch_persistent_context` sobre `perfiles/<usuario>` (sesiones y cookies
de los portales), canal `chrome` con fallback a Chromium, `STEALTH_JS` y `_args_chrome()`. Playwright le agrega
`--no-sandbox` porque no se le pasa `chromium_sandbox=True` (`lib/server/chromium/chromium.js` de Playwright 1.58.0): de
ahí el aviso de Chrome por esa bandera. Cambiarlo es cambiar cómo se lanza el navegador: lo decide Marcelo (encargo 45).

### Agregar o tocar una naviera

Una naviera nueva debe quedar en **todos** estos lugares: `NAVIERAS`, `RESERVADORES`, `HOJA_ALIAS`,
`_match_nav_key` y la lista `navs_secuencia` de `_web_worker`. Tras su guarda, `_pulsar_boton` y
`_resultado_envio`. Su forma en `FORMA_BOOKING` entra solo **medida** en capturas o HTML de una
confirmación real; sin ella, la naviera nunca llega a EMITIDA.
`_login_portal(nombre, url)` sirve de andamiaje (abre el portal y espera login manual).
Las capturas siguen el patrón `<nav>_f<fila>_<n>_<paso>.png`.

## Planilla Excel

- **Hoja = naviera** según `HOJA_ALIAS` (`ONE`, `MSC`, `CMA-CGM`, `COSCO`, `HYUNDAI`/`HMM`, `MAERSK`).
  Una hoja `CONSOLIDADO`/`TODAS`/`GENERAL` corre todas las navieras y reparte por la columna `Naviera`.
- Las columnas se ubican **por texto del encabezado, no por posición** (`_CAMPOS` + `_mapear`, la
  fila de encabezado se detecta sola; en la muestra es la fila 4). El orden de `_CAMPOS` importa: lo
  más específico primero.
- **Hay dos lectores distintos**: `leer_filas` (camino web, el que se usa hoy; soporta `naviera` y
  `temp`) y `leer_reservas` (camino consola/Tkinter, heurísticas antiguas con columnas fijas). Si
  cambias cómo se interpreta una columna, revisa ambos. `leer_reservas` ya no da la nave desde la columna F
  (`nave_de_la_f`, `CICLO-cola-seis-items.md`). «-» en el destino final, sin otra cosa, lo leen los dos como la celda
  vacía, con una sola función (`_destino_final_de`, encargo 43).
- **El día de carga lo lee un solo lector,** `_fecha_planilla` (`CICLO-cola-cuatro-items.md`).
  - Lo usan las seis: COSCO, MSC y ONE por `_desde` (ONE desde `0e15b8a`), y HYUNDAI, MAERSK y CMA. No le des
    a una naviera su propio lector.
  - Entiende la fecha de Excel, su número de serie y los textos AAAA-MM-DD y DD-MM-AAAA (el día primero),
    con o sin hora. Una fecha que no existe no cuenta.
  - Si la celda trae otra cosa, `_avisar_dia_carga` lo avisa, y la naviera sigue como si la fila no la
    trajera.
- Camino web: la planilla subida se copia a `%TEMP%\aquashield_planilla.xlsx` y los resultados se
  descargan con `/api/descargar` (`_planilla_con_resultados` rellena Estado y N° de reserva emitida).
  Escribe **solo en la hoja que se corrió** (si corriste CONSOLIDADO, solo en CONSOLIDADO): no espejes
  en CONSOLIDADO, porque sus números de fila son otras reservas y ninguna columna las identifica
  (`CICLO-escritura-planilla.md`, `CICLO-consolidado-y-respaldos.md`). Lo que no puede escribir lo avisa
  `_avisar_descarga` en el registro del panel y en el `log.txt` de la última corrida. «N° de reserva
  emitida» lleva el número solo con una EMITIDA: `_extraer_bkg_limpio` devuelve vacío con cualquier otro estado. Su
  texto sale de `_texto_n_reserva`, la misma fuente de la columna del panel (`n_reserva` de `/api/estado`): el número,
  «lista para emitir» en la OK-EJEMPLO (`LISTA_PARA_EMITIR`) y nada en los demás (encargo 34).
- Ningún lector lee el **valor** de la columna de estado (los dos la ubican y nada más); por eso los
  estados nuevos no cambian qué filas se leen (`test_planilla.TestEstadosNuevos`). Si un lector empieza a
  leerlo, antes decide con Marcelo qué hacer con las filas ENVIADA – REVISAR EN PORTAL.
- La planilla **no trae peso bruto, temperatura, ventilación ni día de carga** (medido el 2026-09-25).
  - Las 7 hojas tienen las mismas 9 columnas, salvo COSCO, que trae 8: le falta «N° de reserva emitida».
  - El peso sale de `config.json → opciones → peso_reefer_kg` (`_peso_reefer`), en las seis navieras.
  - La temperatura sale de una columna de temperatura si la hoja la tiene; si no, de
    `config.json → opciones → temperatura_reefer_c` (`_temperatura_reefer`).
  - Si una de esas llaves falta o no es un número, se usa `PESO_REEFER` o `TEMP_REEFER` y se avisa una vez por
    corrida (`CICLO-cola-nueve-items.md`). No escribas esas cifras en otro lugar.
  - La ventilación la llenan ONE y HYUNDAI con un valor fijo; COSCO no la llena.
  - De dónde deben salir lo decide Marcelo (`CICLO-cosco-campos-y-reminder.md`). No agregues otro valor por
    defecto.
- Camino consola: `escribir_estado` escribe directo sobre `Reservas AQUASHIELD.xlsx` junto al programa,
  en la columna que ubica `_columna_estado` por su encabezado (sin «Estado», crea «Estado (Robot)» tras el
  último encabezado y nunca antes de la M). Antes de la primera escritura de cada corrida deja **una**
  copia, «<planilla> - respaldo AAAA-MM-DD HHMMSS.xlsx», al lado y fuera de git por `*.xlsx`; con
  «todas», las seis navieras la comparten por `_CORRIDA_CONSOLA`. Sin copia no escribe. Después,
  `podar_respaldos` conserva las 10 más recientes según el nombre y borra solo archivos de esa carpeta que
  calcen exacto con `PATRON_RESPALDO`; no aflojes ese patrón. Un error de escritura levanta
  `ErrorEscritura` (mensaje en español) y `ejecutar_reservas` lo avisa por el `Registro` y lo cuenta en
  el resumen; no lo silencies. Solo `OK-EJEMPLO` lleva «SIN EMITIR» en el texto escrito.

## Credenciales

`config.json` guarda usuario/clave/contrato por operador y naviera en texto plano y queda fuera de git.
`config.example.json` es la plantilla versionada: misma estructura, con usuario, clave y contrato vacíos
(vacíos a propósito: el modo login salta la naviera sin usuario y el panel muestra que no hay clave
guardada; un marcador tipo `TU_CLAVE` se teclearía en el portal real y el panel lo daría por clave).
Nunca la regeneres copiando `config.json`. No muestres las credenciales ni las copies a otros archivos ni a logs. La API web nunca devuelve la clave (solo `tiene_clave`); mantén esa regla. Al
guardar, los dos paneles escriben con `_escribir_config`, de forma atómica: `.json.tmp` y después `_reemplazar`,
que reintenta `os.replace` hasta 20 veces si Windows lo niega un instante. Hasta `0af2d5b`, el panel de
escritorio abría `config.json` con `open(w)`, que lo trunca al abrir (`CICLO-cola-siete-items.md`). Todo
operador nace con todas las navieras. En
«opciones», las dos plantillas traen también `peso_reefer_kg` (22500) y `temperatura_reefer_c` (-20).

Desde el encargo 44, «opciones» trae también lo que el programa traía escrito y es de la cuenta:
- `contratos_por_defecto` (`one_usa`, `one_otros`, `msc` y `hyundai`): el contrato que va cuando ni la fila ni las
  credenciales traen uno (`_contrato_por_defecto`; HYUNDAI no mira la fila). Sin contrato, ONE elige «Otros
  contratos» sin escribir uno y MSC deja el campo vacío; HYUNDAI no elige ninguno en el paso 2 y corta antes de
  Booking Details (NO ENVIADA, `ObjetivoNoEncontrado`): elegir uno sería por su posición.
- `codigo_shipper_hyundai` (`_codigo_shipper_hyundai`): el código con que HYUNDAI identifica a la empresa como
  Shipper. Sin él, el modal busca el Shipper solo por el nombre y el respaldo en JavaScript no escribe el código.

Las dos llaves van vacías en `config.example.json`; el `config.json` de este equipo trae los valores que el programa
tenía. Si falta una, o no es un texto, el programa sigue sin ella y lo avisa una vez por corrida.

Los operadores de la plantilla son «usuario1» y «usuario2». Las credenciales de COSCO pueden traer
`nombre_en_pantalla`: el nombre con que el portal muestra al operador. `_cosco_sesion_activa` lo busca para
reconocer la sesión. Es opcional y en la plantilla va vacío: sin él, reconoce la sesión por la empresa.

## Archivos que no son código de la app

- `perfiles/`: perfiles de Chrome con sesiones iniciadas. No borrar ni modificar.
- `logs/web_<nav>_<usuario>_<fecha>/`: `log.txt` + capturas por corrida y, desde el encargo del estado
  tras el envío, el HTML de cada envío (`<captura>.html` y `<captura>_marco<n>.html`), y desde
  `CICLO-evidencia-en-la-guarda.md` el de la guarda y el de los pasos sin objetivo. Tiene datos reales:
  nunca lo versiones ni lo copies al repo. Las crea `carpeta_corrida`, que usan el panel web (`web_…`), la
  consola (`reservas_<nav>_<usuario>_…`) y el login (`<usuario>_…`). La fecha va al segundo; si ese nombre ya
  existe, agrega `_2`, `_3`…, así cada corrida tiene su carpeta (`CICLO-carpetas-unicas-aplicado.md`). No
  vuelvas a armar el nombre a mano. **Algunas carpetas están referenciadas a mano** por los
  generadores de abajo, con `*` en lugar del operador (`_es_de_referencia` y `_ruta`); no limpies `logs/` sin
  revisarlos.
- **La poda del HTML** (`podar_html`, al empezar cada corrida de reservas) borra los `.html` de las carpetas
  de corrida con más de 30 días, según la fecha del nombre, y nada más.
  - Nunca toca `log.txt`, las capturas ni las subcarpetas.
  - Nunca toca las `CORRIDAS_DE_REFERENCIA` de los generadores: `test_evidencia` vigila que la poda las respete y,
    en un equipo con los generadores, que sean las que ellos nombran (sin ellos, esa prueba se salta).
  - No sigue enlaces ni uniones: una unión de Windows se ve como carpeta, así que no quites `is_junction()`.
- Generadores de material (Pillow, OpenCV, python-docx; fuentes de `C:\Windows\Fonts`):
  `crear_simulador_html.py` → `SIMULADOR_AQUASHIELD.html`; `crear_video_demostracion.py` y
  `crear_video_tutorial.py` → los `.mp4`; `generar_manuales.py` → los dos `Manual_*.docx`. **Desde el encargo 44
  están en el equipo y no en el repo**, como el logo `logo_aquachile_dark.png` que usa `generar_manuales.py`: traen
  datos de la empresa y de las personas (decisión de Marcelo). Siguen funcionando aquí, sin versionar.
- `LEEME.md` es la guía del operador y describe el programa real. `test_consola.TestLeeme` vigila que nombre
  solo lanzadores y programas que existen. El código soporta ejecutarse empaquetado (`sys.frozen` → `BASE` =
  carpeta del ejecutable), aunque hoy no hay `.exe`.

## Interfaz y marca

Cualquier cambio visual (index web, panel Tkinter, manuales, videos) sigue el skill `aquachile-brand`:
Pantone 7545 C `#445563` como corporativo y naranja 021 C `#EB5F0A` solo como acento. Los textos de la
interfaz y los logs van en español.
