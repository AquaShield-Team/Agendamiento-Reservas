# Encargo 47 · La corrida del 02-10: MSC vuelve a recargar; MAERSK y COSCO, frenados

**Base:** `C:\dev\Agendamiento Reservas` @ `16f6332` · árbol limpio.

Medido con `metodo-ciclo` v15 sobre lo guardado en `logs/`: 30 carpetas de corrida, 0 que no calzan con el patrón del
programa. Las dos del 02-10 son la de solo login de las 11:52 y la corrida de las 11:55 (terminó a las 12:00:37), las
dos sobre `16f6332`, que se commiteó a las 11:50. Nada de este encargo abrió un portal.

## En resumen

- **MSC:** el «Next» del login dio un 502, y la ida única a eBooking del encargo 45 llevó a la portada de myMSC, sin la
  sesión: la fila quedó NO ENVIADA. Es el caso que decidiste: vuelve la recarga de esa página, una sola vez, sin
  reenviar la clave ni otro intento de inicio de sesión. Es una regresión del encargo 45, que la había quitado.
- **MAERSK:** no es una regresión. Encontró la nave, pulsó su «Book» (donde se detuvo el 01-10), pasó «Recommended
  services» y se detuvo en el calendario de la fecha de retiro: su lector, del encargo 36, que ninguna corrida había
  alcanzado, no reconoce cómo trae el mes y el año. FRENO: lo reporto y no lo corrijo.
- **COSCO:** no es una regresión. El formulario de New Booking no mostró sus campos en 31 s, y quedó REVISAR antes de
  buscar salidas; el 01-10, con el mismo código en ese tramo, apareció al instante. Confirmar la causa exige el portal.
  FRENO.
- **Las naves:** tu sospecha no se confirma. En las cuatro navieras que mostraron salidas (ONE, CMA-CGM, HYUNDAI y
  MAERSK), la nave de su fila estaba, con salida del 18 al 24 de octubre. MSC y COSCO no mostraron salidas, por la
  sesión y por el formulario; el 01-10 sus naves estaban, con salida el 25-10 y el 06-10. **No hice la copia de la
  planilla.**
- Sin clics nuevos (la recarga es una navegación), y `test_candado` no cambia. La suite pasa con 569 pruebas, y el
  censo completo muerde con sus 1691 mutaciones.

## MSC

### Qué pasó

| Hora | Paso | Lo que vio el programa |
|---|---|---|
| 11:55:47 | «Login MSC» | |
| 11:55:51 | La portada de myMSC, y el usuario escrito | www.mymsc.com/myMSC/ |
| 11:55:52 | «Next» (el clic tardó 0,8 s) | En su primera mirada, la página de error de Chrome (chrome-error://chromewebdata/). Su captura, `msc_error`, dice por OCR «Esta página no funciona», «www.mymsc.com no puede procesar esta solicitud ahora» y «HTTP ERROR 502» |
| 11:55:52 | La ida única a eBooking (encargo 45) | |
| 11:55:54 | Terminó la espera | La portada de myMSC con una consulta en la dirección; `msc_final` dice por OCR «Welcome to myMSC» y «No account yet? Sign Up Now»: el formulario de login, sin la sesión |
| 11:55:54 | NO ENVIADA, con `MSC_SIN_SESION` | |

- **Cuánto tardó el inicio de sesión:** 7,1 s, de «Login MSC» al NO ENVIADA. El de solo login de las 11:52 hizo lo
  mismo, paso por paso, en 7,4 s.
- **¿Error al volver de b2clogin?** No: no llegó a b2clogin. El historial del perfil guarda, de cada uno de los dos
  logins del 02-10, solo cuatro visitas: la portada (www.mymsc.com, que lleva a /myMSC/) y, 4 s después, eBooking, que
  volvió a la portada. Ni TriggerOidcLogin, ni identityserver, ni b2clogin: Chrome no guarda una navegación que
  terminó en su página de error, igual que en las recargas viejas, donde TriggerOidcLogin aparece recién con la
  recarga. El error lo dio www.mymsc.com en la primera navegación tras el «Next», que en los logins que funcionan es
  TriggerOidcLogin: uno de los dos lugares donde el encargo 45 lo midió.
- **¿La ida a eBooking dejó la sesión?** No: es la primera vez que se mide, y en los dos logins llevó a la portada.
- **La nave de su fila:** sin sesión, no hubo salidas en esta corrida. El 01-10 estaba, con ETD el 25-10.

### Por qué la recarga

Hasta el encargo 45, tras el 502 del «Next», el programa avisaba y recargaba esa página. En `logs/` hay 9 recargas
(del 21-09 al 01-10): todas avisaron 18 o 19 s después del «Next» y recargaron 3 s más tarde. El historial del perfil
guarda 8 de esas 9. La que falta es del 27-09: lo más probable es que volviera a dar el error, que Chrome no guarda
(después, el programa no vio el campo de la clave).

| Las 8 recargas guardadas | Cuántas |
|---|---|
| De TriggerOidcLogin, que siguieron solas hasta la página de la clave en b2clogin | 5 |
| De TriggerOidcLogin, que siguieron solas por identityserver, sin pedir la clave | 2 |
| De esas 7, terminaron en la sesión sin otro intento después de la recarga | 4: 3 con la clave escrita por primera vez después de la recarga (21-09, 24-09 y 30-09) y 1 sin pedirla (27-09, en el tercer intento de ese login) |
| La del 01-10 a las 16:05, que terminó en la página de error del propio MSC (su captura, OCR del encargo 45) | 1 |
| Que volvieron al campo del usuario | 0 |

En las 3 que dejaron la sesión con la clave, el código viejo buscó primero el campo del usuario, que no apareció en 12
s, y después el de la clave, que encontró en 0,1 s o menos.

### El cambio

- `_msc_recargar`: si tras el «Next» llega el error, espera `MSC_PAUSA_RECARGA` s (20: lo que tardaba el código de
  antes; es una hipótesis), recarga esa página una sola vez y espera lo primero que llegue: el campo de la clave, la
  sesión o el error, con la misma espera del encargo 45 (unos 30 s).
- No escribe ni pulsa nada. La clave nunca se envió antes (el error sale antes de su página): si aparece su campo, la
  escribe `_msc_entrar`, como siempre, por primera vez. Si vuelve el campo del usuario, no lo escribe (sería otro
  intento): la espera termina sin nada, y el login, sin la sesión.
- Si el error sigue, la ida única a eBooking del encargo 45, y nada más. El error del botón de entrar no recarga: va
  directo a eBooking, como hasta hoy.
- **Espera solo el campo de la clave.** La primera versión esperaba la clave y el usuario con un solo selector, y la
  cambié antes de la compuerta: Playwright mira solo el primer elemento que calza (`.first`), y si en la página de la
  clave el primero fuera un campo de correo oculto, no vería la clave. Es lo que hacía el código viejo, que esperaba la
  clave sola.
- Lo que dice la pantalla, con el tiempo de la constante:

  > ⚠ MSC mostró una página de error al pulsar «Next». Espero 20 s y recargo esa página una sola vez, como antes del
  > encargo 45, sin volver a escribir el usuario.

  Y deja la captura `msc_error_next` antes de recargar.

### Lo que vigila el cambio

- `test_clics.TestMsc.test_tras_el_error_del_next_recarga_una_vez`, con sus cuatro desenlaces: la recarga lleva a la
  clave, que escribe por primera vez, y llega la sesión; la recarga deja la sesión; vuelve el campo del usuario, y no
  lo escribe ni pulsa «Next» (espera la clave hasta el tope y no da la sesión por iniciada); y sigue el error: una sola
  recarga y la ida a eBooking. Fija también la pausa, el aviso y las capturas.
- **La página falsa del login anota cada recarga, también la que no se espera.** Hasta hoy, su docstring decía que una
  recarga inesperada «revienta»: no es así, porque `_msc_recargar` atrapa la falla de la recarga y la anota en el log.
  Ahora toda prueba del login que compara lo que hizo el programa la ve.
- La foto del 502 tras el «Next» de `test_ante_el_error_va_una_vez_a_ebooking_y_no_reintenta` pasa a tener la recarga,
  y `_msc_recargar` entra en las funciones que mira `test_login_sin_clic_generico`.
- 10 mutaciones nuevas (`msc-recarga-*`): sin recargar, sin llamarla tras el «Next», dos veces, también tras el error
  del botón de entrar, sin la pausa, con otra pausa, volviendo a escribir el usuario, esperando también el campo del
  usuario, sin el aviso y sin la captura.
- **La compuerta, en dos pasos.** En una copia de `16f6332` con el cambio: la suite, 569 pruebas, OK, en 276 s (1
  saltada: la que necesita los generadores, que no están en el repo), y el censo de `TestMsc`, 77 mutaciones y 88 pares
  mutación-prueba, y los 88 muerden. En la raíz, lo mismo: 569 pruebas, OK, en 276 s, el mismo censo, y 0 cambios en
  los 4284 originales fotografiados.
- **El censo completo, sobre `6942eca`:** 1691 mutaciones y 2027 pares mutación-prueba, y los 2027 muerden; 0 pruebas
  sin mutación y 0 cambios en los originales, en 66 minutos.

## MAERSK

### Dónde se detuvo

| Hora | Paso |
|---|---|
| 11:59:42 | «Ya había una sesión activa»; el formulario, el origen y el destino |
| 12:00:07 | «Select sailing»; dos veces «Search more sailing options» |
| 12:00:23 | 3 tarjetas de la nave, 2 copias idénticas de la otra: una sola salida |
| 12:00:24 | «nave seleccionada», sale el 18 Oct 2026, 08:30 |
| 12:00:26 | «Recommended services», y su «Continue» a las 12:00:31 |
| 12:00:36 | «Additional details»: «el primer día hábil después de hoy es el 05-10-2026 (lunes)»; «Choose another date» |
| 12:00:36 | El calendario: «31 días, 0 con su fecha»; NO ENVIADA, sin otro clic |

- **¿Encontró la nave?** Sí, después de ampliar la búsqueda dos veces: 3 tarjetas de la nave, 2 copias idénticas de
  la otra, del 18-10. Con viaje en la fila, el programa elige solo entre las salidas que lo traen.
- **¿Trajo la tarjeta a la vista y pulsó el «Book»?** Sí. `_mk_pulsar_book` siempre trae la tarjeta antes de mirar la
  altura del «Book» (no lo anota), y `log.txt` dice «nave seleccionada» solo cuando lo pulsó; si no, desde el encargo
  46 diría «no pude pulsar el «Book» de la salida elegida». Después, la captura `mk_f10_5b_services` muestra, por OCR,
  «Recommended services». Es el paso donde se detuvo el 01-10.
- **¿Dónde se detuvo?** En «Additional details», en la fecha de retiro: el calendario abrió, y el programa no pudo
  ponerle fecha a ninguno de sus días.

### La causa: el calendario, medido por primera vez

`mk_f10_calendario.html` es el primer HTML del calendario que guarda una corrida (11 archivos con ese nombre en
`logs/`, todos de esta corrida): ninguna había llegado a la fecha de retiro con este código, del encargo 36. Leído sin
red, con el JavaScript del programa:

- va dentro de un `mc-modal` titulado «Container pick-up details»;
- el mes y el año están en dos `mc-button` de su cabecera, con `label` «October» y «2026», junto a «Previous month» y
  «Next month»; no hay una leyenda que traiga los dos;
- cada día es un `mc-button` con su número por `label` y, adentro, un `button` con el número por `aria-label` (sin el
  mes ni el año) y `disabled` si no se puede elegir.

`mkCalendario` le pone fecha a un día por un atributo que la traiga entera o por la leyenda de su mes: aquí no hay
ninguno de los dos, y da 0 de 31, lo mismo que dijo `log.txt`. **No es una regresión:** ninguno de los 17 trozos que
cambiaron en `AQUASHIELD.py` entre `7b33924` y `16f6332` toca el calendario.

Lo que habría elegido: ese día había 5 días habilitados, del lunes 12 al viernes 16 de octubre. Con tu regla, el primer
día hábil después del 02-10 es el 05-10, que no estaba habilitado; el siguiente habilitado es el 12, feriado en Chile
(«Día del Encuentro de dos Mundos», según la librería holidays 0.105 instalada); así que el 13.

**Propuesta (decides tú):** que `mkCalendario` lea el mes y el año de esos dos botones de la cabecera, solo si hay uno
de cada uno en el calendario, con el nombre del mes en inglés y el año de 4 cifras; si no, NO ENVIADA, como hoy. Sale de
un solo HTML, y no es un clic nuevo.

## COSCO

- **Hasta dónde llegó:** el login (con el puzzle resuelto solo) y el Dashboard, a las 11:57:39. A las 11:57:44 abrió
  New Booking, encontró el marco del formulario (bkg2) y esperó su campo «Origin City» 20 vueltas de 1,5 s. No apareció:
  a las 11:58:15, REVISAR, «el formulario de COSCO no cargó los campos a tiempo».
- **Lo que mostraba:** la captura `cosco_f8_1_choose` dice, por OCR, la cabecera del portal, «Return to Classic…» y los
  pasos «Choose Service» y «Booking Details», sin el formulario. La del 01-10, en el mismo paso, trae «Pickup»,
  «Contract Nu…», «Cargo Nat…», «Sailing Schedule», «POL», «POD» y «Search By…». En ese punto el programa no guarda el
  HTML (solo con `AQUASHIELD_DESCUBRIR`).
- **¿La nave? ¿Hasta qué fecha buscó?** No buscó: se detuvo antes de llenar «Choose Service». El 01-10, buscando desde
  ese día con «Sailing Within 2» semanas, la nave estaba en 2 itinerarios, los dos con ETD el 06-10.
- **¿La tocó un cambio de los encargos 45 o 46?** No. El «CL» al final del puerto (`_cosco_puerto_de_la_celda`) corre
  en «Choose Service», después del formulario: no se alcanzó. Del `goto` de New Booking a la espera del formulario, el
  código es el mismo que corrió el 01-10 a las 16:12 (`503718b`, el commit vigente a esa hora): de los 30 trozos que
  cambiaron en `AQUASHIELD.py` desde entonces, el único dentro de `reservar_cosco` es un comentario sobre el contrato,
  más abajo.
- **La causa:** el portal no dibujó su formulario en 31 s. Por qué, no se sabe sin el portal. FRENO.

**Propuesta (decides tú):** guardar la captura y el HTML de la página y de sus marcos en ese REVISAR, como en los otros
puntos donde una reserva se detiene, para medir la próxima vez qué mostraba.

## ONE

Llegó a la guarda a las 11:55:46, con la reserva lista y sin emitir. La nave de su fila estaba: 4 salidas de la nave,
del mismo día, el 21-10, y eligió una con el viaje de la fila.

## CMA-CGM

Llegó a la guarda a las 11:57:12, con la reserva lista y sin emitir. La nave de su fila estaba: 4 de las 8 rutas de
su lista guardada, las 4 del 19-10 y con el viaje de la fila.

## HYUNDAI

Llegó a la guarda a las 11:59:32, con la reserva lista y sin emitir. La nave de su fila estaba: 2 de las 6 tarjetas
de su lista guardada (por su «1st Vessel»), las 2 del 24-10 y reservables, y eligió la del viaje de la fila.

## Las naves de la planilla

La planilla es `Reservas AQUASHIELD.xlsx`, modificada por última vez el 30-09 a las 15:30, igual byte a byte a la
copia que guardó el panel a las 11:54. Una fila por naviera (las filas 5 a 10 de CONSOLIDADO), las seis con nave y con
viaje. Las salidas, de lo que guardó la corrida: la lista de CMA-CGM y la de HYUNDAI en su HTML, leídas con el lector
del programa; ONE y MAERSK no guardan la lista cuando siguen, y su `log.txt` anota la elección, que calza con la nave de
la fila.

| Naviera | ¿La nave entre las salidas de esta corrida? | Su salida | ¿Ya zarpó? |
|---|---|---|---|
| ONE | Sí: 4 salidas de la nave, el mismo día; eligió una con el viaje de la fila | 21-10 | No |
| MSC | Sin salidas: la sesión no quedó iniciada. El 01-10 estaba, con ETD el 25-10 | (25-10, el 01-10) | No, según la lista del 01-10 |
| CMA-CGM | Sí: 4 de las 8 rutas, las 4 con el viaje de la fila | 19-10 | No |
| COSCO | Sin salidas: el formulario no cargó. El 01-10 estaba, en 2 itinerarios | (06-10, el 01-10) | No, según la lista del 01-10 |
| HYUNDAI | Sí: 2 de las 6 tarjetas (por su «1st Vessel»), las 2 reservables; eligió la del viaje de la fila | 24-10 | No |
| MAERSK | Sí: 3 tarjetas, 2 copias idénticas de la otra; el programa, con viaje en la fila, elige solo entre las que lo traen | 18-10 | No |

## La copia de la planilla

**No la hice:** ninguna nave se confirmó como no disponible. En las cuatro con salidas, la nave estaba y sale después
del 02-10; MSC y COSCO no mostraron salidas, por la sesión y por el formulario, y su fila quedaría igual de todos modos.

Si algún día hace falta una copia con otro nombre: en el panel web (`Iniciar AQUASHIELD.bat`), se elige en el campo de
la planilla. La consola no la vería: lee solo `Reservas AQUASHIELD.xlsx` (o, si falta,
`Planilla_Estandar_AQUASHIELD.xlsx` o `Agendamientos.xlsx`) junto al programa.

## FRENA SI

- **MAERSK y COSCO:** sus causas no son una regresión, ni el caso de MSC, ni una nave que ya no estaba. Las reporto con
  su evidencia, arriba, y no las corrijo: las propuestas las decides tú.
- **COSCO:** confirmar su causa exige abrir el portal. No lo abrí.
- **La copia de la planilla:** ninguna fila necesitó una salida vigente, porque no se hizo la copia.
- **MSC sí se corrigió:** es el caso que decidiste. La recarga es una navegación, no un clic: `test_candado` y la foto
  de `test_clics` no cambian.

## Re-medir

Todo corre desde `scratchpad\e47`, en Git Bash, después de `source entorno_e47.sh` (`TMPDIR`, `TEMP` y `TMP` dentro
de la carpeta), con `python3.13`. Ningún script imprime valores de la planilla ni de la cuenta.

| Número | Script |
|---|---|
| Carpetas de `logs/` | `python3.13 corridas.py 20261001` |
| Cada log, con la máscara | `python3.13 ver_log.py <AAAAmmdd_HHMMSS> [desde] [hasta] [regex]`; su control, `python3.13 control_mascara.py` |
| El historial del perfil (los logins de MSC y sus recargas) | `python3.13 historial_msc.py [MM-DD]` |
| Las 9 recargas viejas y su tiempo desde el «Next» | `python3.13 recargas_msc.py` |
| El texto de las capturas (OCR, con la máscara) | `python3.13 ocr_capturas.py <AAAAmmdd_HHMMSS> <captura.png>…` |
| El calendario de MAERSK: 31 días, 0 con su fecha, sus atributos | `python3.13 calendario_mk.py` |
| Su cabecera («October», «2026») y sus botones | `python3.13 t/cal_bloque.py t/cal_bloque.js` |
| Sus días habilitados | `python3.13 t/cal_hab_run.py t/cal_hab.js` |
| Los feriados de octubre | `python3.13 t/feriados_oct.py` |
| Las naves de la planilla en las listas | `python3.13 naves_e47.py` (su salida, en `salida_naves_e47.txt`) |
| La planilla y la copia del panel | `python3.13 t/planilla_igual.py` |
| Lo que cambió en `AQUASHIELD.py` en los encargos 45 y 46, y desde el código del 01-10 | `python3.13 diff_enmascarado.py 7b33924 16f6332 <patrón>`; `python3.13 diff_enmascarado.py 503718b 16f6332 <patrón>` |
| El commit vigente el 01-10 a las 16:07 | `python3.13 t/log_enmascarado.py "2026-10-01 10:00" "2026-10-02 00:00"` |
| La suite y el censo | `bash precenso.sh <etiqueta> <filtros…>`, `bash gate.sh <etiqueta> <filtros…>`, `bash censo.sh` |

## NO retroceder

- **Tras el error del «Next», una sola recarga, sin escribir el usuario:** volver a escribirlo, o recargar otra vez,
  sería otro intento de inicio de sesión, que decidiste no hacer.
- **Tras la recarga se espera solo el campo de la clave:** un selector con la clave y el usuario miraría solo el primero
  que calce en la página.
- **Si el error sigue, la ida única a eBooking del encargo 45, y nada más.**
- **La página falsa del login anota cada recarga:** sin eso, una recarga de más no hace caer ninguna prueba.

## Defectos de instrumento que me cacé

- **Un `git diff` sin máscara imprimió dos contratos**, que el código viejo traía en comentarios (antes del encargo
  44). Salió solo en una salida de herramienta de esta sesión, no en un archivo ni en el informe. Desde ahí, todo diff
  del código viejo pasa por `diff_enmascarado.py`.
- **Mi primera versión de la recarga esperaba la clave y el usuario con un solo selector.** Lo vi al releer lo que
  hacía el código viejo después de recargar, antes de la compuerta, y la cambié: el censo de esa versión no terminó (lo
  detuve) y su suite había pasado.
- **La página falsa del login no avisaba de una recarga inesperada,** aunque su docstring decía que sí.
- **Mi sonda del calendario tomaba como raíz el ancestro común más lejano (`<html>`)** y no el más cercano; la corregí
  antes de usar su descripción.
- **Mi sonda de las recargas viejas no veía las del modo de solo login;** ahora las reconoce por el selector del «Next»
  de MSC.
- **El OCR no corría después de cargar la máscara:** el arnés de las pruebas, que la máscara usa, bloquea los procesos.
  Corre antes.
- **`sort` de Git Bash está bloqueado por Defender** (ya estaba en el catálogo de la máquina); usé Python.

## Premisas del encargo que se refutaron

- **«Las naves de la planilla ya no están disponibles»:** no en las cuatro navieras que mostraron salidas; en MSC y
  COSCO, esta corrida no lo puede decir, por razones que no son la nave.
- **«Si hubo error al volver de b2clogin»:** el error salió antes, tras el «Next»; no llegó a b2clogin.
- **«Corregir solo lo que sea una regresión de los encargos 45 y 46»:** se cumplió en MSC; MAERSK y COSCO no son
  regresiones. MAERSK pasó el «Book», donde se detuvo el 01-10, y llegó a un código que ninguna corrida había
  alcanzado. Si sin el encargo 46 lo habría pulsado no se sabe: dónde estaba la tarjeta antes de traerla no se anota.
- **«La corrida más reciente»:** hubo dos ese día: también la de solo login de las 11:52, con el mismo error de MSC.

## Residual

| Qué | Por qué no se hizo | Se reabre si |
|---|---|---|
| Que la recarga deje la sesión en el portal | Este encargo no abre portales | MSC vuelve a dar el 502 tras el «Next»: `log.txt` dice «MSC mostró una página de error al pulsar «Next»» y lo que vino después |
| `MSC_PAUSA_RECARGA` = 20 s | Es una hipótesis: lo que tardaba el código viejo | Tras la recarga vuelve el error: otro valor lo decides tú |
| El lector del calendario de MAERSK | FRENO: no es una regresión; la propuesta está arriba | Lo decides |
| Lo que sigue al calendario en MAERSK: la referencia, el Shipper, «Review booking» y los términos | Con el código de hoy, ninguna corrida llegó ahí; la del 27-09 a las 21:15, con el de antes, llenó la referencia y el Shipper, y sin la fecha de retiro no llegó a la revisión | Se corrige el calendario y corres la fila |
| El formulario de COSCO sin campos | FRENO: la causa exige el portal; la propuesta de guardar el HTML está arriba | Lo decides, o se repite |
| Si vuelve el campo del usuario tras la recarga, el login queda sin la sesión | Es tu decisión: sin otro intento | Lo decides |
| Por qué MSC da el 502 tras el «Next» desde el 21-09 | Falta la respuesta del portal (estado, cabeceras, cuerpo), como en el encargo 45 | Lo encargas |
| Una revisión del cambio por un subagente (los agentes que pide ECC) | Se proponen, no se lanzan | Lo decides: correría en un clon dentro de la carpeta del encargo |

## Reglas de método aplicadas

`metodo-ciclo` v15, con las reglas permanentes de `~/.claude/CLAUDE.md`:
- **Todo salto silencioso lleva contador:** 30 carpetas y 0 que no calzan; 9 recargas viejas en `logs/` y 8 en el
  historial, con la que falta explicada; 31 días y 0 con su fecha; 17 trozos del diff de los encargos 45 y 46, y 0 en
  el calendario; 30 desde el código del 01-10, y 0 en el tramo de COSCO.
- **Control positivo que aborta:** la máscara, el OCR (con su imagen sintética), el calendario sintético con 31 fechas,
  el HTML del 02-10 que tiene que dar lo que dijo `log.txt`, las 5 recargas conocidas y las 6 filas con nave.
- **El negativo tiene que morder:** las 10 mutaciones nuevas en el censo filtrado y en el completo.
- **Todo registro es una hipótesis:** el docstring de la página falsa («revienta») no era cierto, y el «no medido» de
  CLAUDE.md sobre el calendario pasó a medido.
- **Re-medir contra HEAD; el cambio y su guardián, en la misma operación.**
- **Frenar si la decisión es de negocio; lo que está fuera del encargo se propone:** MAERSK, COSCO y la revisión.
- **Todo entregable declara su base:** la primera línea.

**Choques:** las reglas de Python de ECC piden pytest, anotaciones de tipos y black; el repo usa `unittest` y su propio
estilo, y seguí el del repo (mandan las reglas permanentes y `metodo-ciclo`). Entre las reglas del método, ninguno.

## Lo que dio en el repo

- `6942eca` fix(msc): vuelve la recarga tras el error del «Next», una sola vez y sin reenviar la clave;
- y el de este informe, con `CLAUDE.md` al día.

El push lo haces tú. Los comandos, con el hash esperado, van en el mensaje final del encargo: este informe va dentro
del commit y no puede citar su propio hash.
