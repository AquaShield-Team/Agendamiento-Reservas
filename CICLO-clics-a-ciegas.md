# CICLO · Clics a ciegas antes de la guarda del candado

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-24 · **Método:** skill `metodo-ciclo` v12 ·
**Base:** `83067a1` · **Commits** (locales, sin push):
- `462d7cb` ONE (con el mecanismo común y la prueba);
- `f3476c0` MSC;
- `9b1c77c` CMA;
- `a08490b` COSCO;
- `cee7297` HYUNDAI;
- el de este informe.

**MAERSK: FRENO, sin cambios.**

> Sin datos reales. De los logs solo se contaron caminos (qué rama tomó cada clic) y se imprimió el conteo,
> nunca la línea. Las capturas se miraron en su lugar. Los casos de prueba son sintéticos.

## Veredicto

- **Cinco navieras, hechas.** ONE, MSC y CMA ya no tienen clics genéricos antes de la guarda. Si un paso no
  encuentra su objetivo por su identificación propia, no pulsa nada: el paso y lo que buscaba quedan en
  pantalla y en `log.txt`, con una captura, y la reserva queda **NO ENVIADA**. COSCO y HYUNDAI no tenían
  clics genéricos; se corrigieron sus mensajes de «hecho» que se escribían sin saber si hubo clic.
- **MAERSK: FRENO** (el primer FRENA SI). Dos respaldos genéricos fueron el camino de sus 5 reservas
  exitosas, y la evidencia no alcanza para dar con su objetivo específico. Quitarlos la rompería (detalle
  abajo).
- **La red suma `test_clics`:** falla si reaparece una forma de clic genérico antes de la guarda, con sus
  defectos inyectados.
- **Censo completo final sobre `cee7297`:** **pasó.** Corrió de 12:12 a 12:35, con el árbol limpio antes y después. La copia sin mutar pasa las 215 pruebas. Las 396 mutaciones, en 471 pares, muerden todas, y no queda ninguna prueba sin mutación. 0 cambios en los originales.

**PASO 0: CICLO** (con un FRENO parcial en MAERSK).

## La regla de clasificación

Un clic o marcado antes de la guarda es:
- **Específico** si el elemento que pulsa se filtró por algo propio de él:
  - su texto, su valor, o un atributo propio (id, name, placeholder, aria-label, data-*);
  - la etiqueta de su campo;
  - un dato de la reserva (la nave, la ciudad, el código).

  Si quedan varios candidatos, tomar el primero está permitido. La holgura del patrón no cambia la clase: un
  texto parcial sigue siendo específico. Los holgados van al residual.
- **Genérico** si sale por posición («el primero», «el último», `[0]`, `[n-1]`) entre candidatos que no se
  filtraron por nada que lo nombre:
  - solo etiqueta HTML, tipo, rol o clase de componente;
  - un ancestro cualquiera que contiene un texto (`div:has-text(...)`, `closest('div')`);
  - cuando el paso elige entre alternativas (itinerarios, sugerencias, días, Origen y Destino) y el filtro no
    las distingue, como «Seleccionar» en cada fila.

Con esta regla, cada uno de los 162 sitios quedó clasificado sin ambigüedad.

## El censo

**Universo:** en cada `reservar_*`, lo que corre antes de la guarda, más todas las funciones del módulo que
eso llama (transitivamente) y el JavaScript inyectado que nombran. Se contaron los clics de Python (`click`,
`check`, `set_checked`, `dispatch_event`, `tap`, `dblclick`) y los de JavaScript (`.click()`,
`dispatchEvent` de mouse, `.checked =`). **162 sitios distintos** (dos son compartidos).

| Naviera | Sitios | Genéricos | ¿Fue el camino de reservas exitosas? | Qué se hizo |
|---|---|---|---|---|
| ONE | 24 | 3 | No. El contrato se eligió por su texto en 5 de 5; el cierre genérico del modal no se usó nunca. Del campo del contrato, el log no dice por qué camino se llenó | `462d7cb`: se quitan |
| MSC | 16 | 2 | No. El HS Code, por el texto del salmón en 5 de 5; el Commodity no corrió | `f3476c0`: se quitan |
| CMA | 31 | 11 | No hubo reservas exitosas de CMA | `9b1c77c`: se quitan |
| COSCO | 14 | 0 | — | `a08490b`: 2 mensajes |
| HYUNDAI | 33 | 0 | — | `cee7297`: 4 mensajes |
| MAERSK | 46 | 11 | **Sí, dos** (abajo) | **FRENO** |

«Reservas exitosas» son las que tienen confirmación medida en sus capturas (`CICLO-numero-booking.md`): 5 de
ONE, 5 de MSC, 5 de HYUNDAI y 5 de MAERSK. Las EMITIDA de CMA y COSCO de los logs viejos no lo son.

## MAERSK: el freno

De sus 11 genéricos, dos fueron el camino de sus 5 reservas exitosas:

1. **Los términos y condiciones.** Los cuatro caminos son genéricos:
   - el último `input[type=checkbox]`;
   - el último `role=checkbox`;
   - el último `mc-checkbox`;
   - un JavaScript que marca el último checkbox del documento. Corre **siempre**, aunque ya se haya marcado.

   Las 5 reservas pasaron por «el último `mc-checkbox`», y después por ese JavaScript.

   **Lo que muestra la captura de revisión:** hay dos casillas, «Add additional email receiver» y la de
   términos («I have read and accept all the terms and conditions of this booking»). El programa acertó
   porque la de términos estaba abajo.

   **Por qué no alcanza la evidencia:** se ve el texto, pero no si el componente lo expone como texto o como
   atributo. Un selector por ese texto podría no calzar, y MAERSK quedaría NO ENVIADA en todas sus reservas.
2. **La fecha de retiro:** «el primer día habilitado» del calendario, en 5 de 5. El respaldo en JavaScript
   elige un día entre el 10 y el 28, o el primero. No hay un objetivo que medir: **qué día corresponde es
   una decisión** (de la planilla, una regla, u otra).

Los otros 9 genéricos de MAERSK **no** fueron ese camino:
- las ciudades por su id, aunque no consta si alguna vez cayeron al respaldo;
- el Commodity, por texto en 5 de 5;
- el contenedor reefer, por «40» en 5 de 5;
- la referencia, por su etiqueta en 5 de 5;
- la nave, por la jerarquía de su texto en 5 de 5.

Se quedan como están porque el freno es por naviera. La foto de `test_clics` los tiene anotados como
pendientes.

## Qué cambió

**El mecanismo común (`462d7cb`):**
- **`ObjetivoNoEncontrado(paso, buscaba)`:** deriva de `BaseException` a propósito. El camino tiene muchos
  `except Exception: pass` que se lo tragarían, y la reserva seguiría a ciegas.
- **El decorador `_sin_clic_a_ciegas("<prefijo>")`** en cada reservador que puede cortar. Convierte el corte
  en `("NO ENVIADA", "<paso>: no encontré <lo que buscaba>, así que no pulsé nada. La reserva no se envió;
  revisa ese paso en el portal.")`, con la captura `<nav>_f<fila>_sin_objetivo.png`.
- **Después de la guarda nada corta,** porque el envío pudo haber salido. El único ayudante que corre en los
  dos lados, el cierre del modal de ONE, recibe `antes_de_la_guarda=False` después de Submit: no pulsa a
  ciegas y solo lo anota.

**Lo que cambia de comportamiento:**

| Dónde | Antes | Después |
|---|---|---|
| ONE · ventana emergente | Pulsaba el primer botón visible del diálogo | Solo su botón por texto o su ícono (aria-label o clase «close»); si no, NO ENVIADA (después de la guarda, solo lo anota) |
| ONE · contrato | Si no estaban el de la reserva ni «Otros contratos», elegía la primera opción | NO ENVIADA |
| ONE · campo del contrato | Sin `name=contractNo`, escribía en el primer campo del formulario | NO ENVIADA |
| MSC · HS Code | Si no estaba el salmón, la primera sugerencia | NO ENVIADA si hay sugerencias y ninguna es el salmón (espera hasta el final por si llega) |
| MSC · Commodity | Si ninguna contenía el texto, la primera sugerencia | NO ENVIADA |
| CMA · Tamaño y tipo | El primer desplegable de la página | Por su etiqueta o su placeholder; si no, NO ENVIADA |
| CMA · peso | El primer campo de cualquier bloque con el texto | Por su etiqueta o su placeholder; si no, NO ENVIADA |
| CMA · itinerario sin nave | El primer «Seleccionar» | NO ENVIADA |
| CMA · Reefer | El primer botón de un bloque con «Reefer», el primer campo del panel, el botón principal de cualquier ventana | Por su texto o su etiqueta; si no, NO ENVIADA en cada paso |
| CMA · «guardados (vía JS)» | Siempre | Solo si el JavaScript pulsó |
| CMA · «I Agree» | La primera casilla visible de la página | Por su texto; si no, NO ENVIADA |
| COSCO · «Copy from my profile» | 'ok' aunque el clic fallara | 'fallo', y prueba el clic de Playwright |
| COSCO · desplegables | «<campo> = '<opción>'» aunque ningún clic ocurriera | «no pude pulsar la opción» |
| HYUNDAI · Dangerous, Chemical, Non-waste | «(js)» aunque no hubiera casilla | «no encontré …; no marqué nada» |
| HYUNDAI · aviso por correo | «activado» siempre | «activado», «ya estaba activado» o «no encontré #emailChk» |

**Sin clics nuevos.** Varios JavaScript pasaron a constantes para correrlos en Node, y cuatro bloques
pasaron a ayudantes (`_cma_marcar_i_agree`, `_hmm_marcar_no`, `_hmm_aviso_correo`, `_hmm_no_residuo`), con el
mismo clic de antes.

## Qué tienes que saber antes de tu próxima prueba con el candado cerrado

- **CMA quedará NO ENVIADA.** Si pasa la sección Reefer, cortará en «I Agree»: en las 5 reservas medidas
  ninguna captura muestra esa casilla, y el log decía «marcado» porque se marcaba la primera casilla de la
  página. Si esa casilla no existe en CMA, el paso sobra; **quitarlo lo decides tú**.
- **CMA sin nave en la fila:** NO ENVIADA, en vez del primer itinerario.
- **ONE:** si el campo del contrato no tiene `name=contractNo`, quedará NO ENVIADA en ese paso. El log no
  dice cuál de los dos caminos llenó el contrato en las 5 reservas exitosas.
- **En cada caso,** el log dice «✗ NO ENVIADA · <paso>: no encontré <lo que buscaba>…», y en la carpeta de la
  corrida queda `<nav>_f<fila>_sin_objetivo.png` con la pantalla de ese momento.

## Las expectativas

- **Ninguna expectativa de la red cambió.** `test_candado` pasa con la misma `ANTES_ESPERADO`, y `test_envio`
  sin cambios.
- **Lo nuevo es `test_clics` (26 pruebas),** con estas piezas:
  - el mecanismo;
  - que cada reservador que corta esté decorado;
  - que nada que corta se llame después de la guarda sin `antes_de_la_guarda=False`;
  - la foto de las formas de clic genérico antes de la guarda;
  - por naviera, los JavaScript en Node y los cortes con páginas falsas.
- **La foto se achicó en cada commit** (antes y después, en formas genéricas encontradas):

| Commit | Formas en la foto | Cambio |
|---|---|---|
| `462d7cb` | 41 | La primera foto: 10 de MAERSK (pendientes por el freno), 17 de MSC y CMA (pendientes de su commit) y 14 permitidas con su motivo |
| `f3476c0` | 39 | −2 de MSC |
| `9b1c77c` | 24 | −15 de CMA (el mensaje de ese commit dice 14: es un error mío, son 15) |
| `a08490b` | 24 | La de «Copy from my profile» pasa a su constante |
| `cee7297` | 24 | Sin cambio |

- **`tests/correr.py`:** el motivo de una mutación reconoce `ObjetivoNoEncontrado` (antes salía vacío).

## Los defectos inyectados

- **Censos filtrados, uno por commit, antes de cada commit:**

| Commit | Mutaciones nuevas | Pares | Resultado |
|---|---|---|---|
| `462d7cb` | 12 (5 del mecanismo, 7 de ONE) | 16 | Todas muerden, por su motivo |
| `f3476c0` | 7 | 9 | Todas muerden |
| `9b1c77c` | 16 | 24 | Todas muerden |
| `a08490b` | 3 | 3 | Todas muerden |
| `cee7297` | 6 | 6 | Todas muerden |

- **Cada forma genérica quitada tiene su mutación que la devuelve,** y la tumban dos pruebas: la de su
  naviera y la foto. Por ejemplo, con «.el-select input» de vuelta, CMA pulsa ese desplegable y corta
  recién en el peso.
- **La red:** de 189 pruebas, 352 mutaciones y 413 pares, a **215 pruebas, 396 mutaciones y 471 pares.**

## Re-medir (pieza 1)

```powershell
python tests\correr.py
python tests\correr.py --mutaciones
python -m unittest test_clics      # desde tests\
```

- **El censo de sitios:** recorrer con AST lo que corre antes de la guarda (`test_clics.universo`) y contar
  los clics de Python y de JavaScript. Da 162.
- **Los caminos de las reservas exitosas:** contar en `logs/*/log.txt` los mensajes que delatan cada rama.
  Algunos ejemplos:
  - «resultado selección 'otros'»;
  - «HS Code … seleccionado»;
  - «términos y condiciones aceptados (mc click)»;
  - «fecha de retiro seleccionada en modal (locator)».

  Solo conteos.
- **Los mensajes de «hecho» sin saber:** buscar un `evaluate` suelto con un JavaScript que pulsa, seguido de
  un `reg.info`. Da 5 sobre `83067a1` (control positivo) y 0 hoy.

## NO retroceder (pieza 2)

- **No devuelvas ningún respaldo genérico:** la foto de `test_clics` cae.
- **No hagas que `ObjetivoNoEncontrado` herede de `Exception`:** un `except Exception: pass` del camino se lo
  tragaría.
- **No llames después de la guarda a un ayudante que corta** sin `antes_de_la_guarda=False`: marcaría NO
  ENVIADA un envío que pudo haber salido. `test_clics` lo vigila.
- **No quites los genéricos de MAERSK** sin decidir los dos de arriba.

## Premisas del encargo contrastadas (pieza 5)

- **«En CMA hay tres respaldos que pulsan sin identificar su objetivo»:** confirmada, y eran más. Son 11
  genéricos en CMA: los tres medidos y otros ocho (Tamaño y tipo, peso, itinerario sin nave, más caminos del
  lápiz, la temperatura y el guardar).
- **«"guardados (vía JS)" se escribe aunque no se haya pulsado nada»:** confirmada. Había seis mensajes más
  así: cuatro en HYUNDAI y dos en COSCO.
- **«test_candado no ve ninguno de estos clics»:** confirmada. Mira solo los textos dentro de cada
  `reservar_*`. `test_clics` recorre sus ayudantes y el JavaScript.
- **La decisión «si el objetivo no se encuentra, NO ENVIADA»:** aplicada en cada genérico quitado, antes de
  la guarda. Después de la guarda no se corta: ahí el envío pudo haber salido.

## Universo y cobertura (pieza 3)

- **Reservadores:** 6 de 6; lo que corre antes de su guarda, con sus ayudantes y su JavaScript.
- **Fuera del universo, declarado:** los flujos de login, que corren antes de `reservar_*` y no pasan por la
  guarda. No se midieron.
- **Logs:** las 6 carpetas de `logs/`. Reservas exitosas: 20 (5 por naviera en ONE, MSC, HYUNDAI y MAERSK).
- **Capturas miradas:** la de revisión de MAERSK (fila 30).

## Defectos de instrumento cazados (pieza 4)

1. **El censo contaba código de después de la guarda.** En ONE y CMA la guarda está dentro de un bucle, y mi
   primer recorte tomaba el bucle entero. Lo delató `_pulsar_boton` apareciendo antes de la guarda. Lo
   corregí recortando las sentencias que contienen la guarda.
2. **`dispatchEvent` de más.** Contaba también los eventos `input` y `change` que acompañan una escritura.
   Lo acoté a eventos de mouse: de 213 sitios a 162.
3. **La barra invertida de Bash, tres veces.** Aparecieron en un patrón del escaneo de generadores, en una
   marca de prueba y en un script. Los reescribí con archivos.
4. **Un conteo de CR imposible.** `grep -c $'\r'` dio todas las líneas de los archivos; en binario eran 0.
5. **La forma «textarea» quedó corta.** No veía selectores con comillas simples adentro. La corregí, con
   control en los casos de MAERSK y CMA.
6. **Motivos vacíos en el censo.** El corredor no reconocía la excepción nueva.
7. **Un script en el scratchpad importó la red y quedó bajo sus trampas** (`subprocess` bloqueado). Lo
   reordené.
8. **El barrido de mensajes ve una sola forma.** Los dos casos de COSCO los encontré leyendo.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| MAERSK: términos y condiciones, y fecha de retiro | FRENO: camino de sus 5 reservas exitosas, sin objetivo específico medible | …una corrida deja el HTML de la revisión (el checkbox) y decides qué fecha de retiro corresponde |
| MAERSK: sus otros 9 genéricos | El freno es por naviera | …se reabre MAERSK |
| CMA: «I Agree» probablemente no existe | Con el código de hoy, CMA queda NO ENVIADA ahí | …decides quitar el paso o una prueba muestra la casilla |
| ONE: el camino del campo del contrato | El log no lo distingue | …tu prueba con el candado cerrado pasa o corta en «Contrato de ONE» |
| Los flujos de login | Fuera del universo | …se decide auditarlos |
| 9 selecciones a ciegas por teclado (ArrowDown + Enter) antes de la guarda: ONE 1, MSC 3, CMA 4, COSCO 1 | No son clics | …se decide tratarlas igual |
| Una escritura a ciegas: los comentarios de CMA van al primer `textarea` si no encuentran el suyo | No es un clic | …se decide tratarla igual |
| Específicos con patrón holgado: el placeholder «Seleccionar» de CMA, `input[value*='Non']` de HYUNDAI, «general» en el desplegable de ONE | La regla clasifica por la clase del criterio | …uno pulsa lo que no era |
| COSCO: «Shipper final = …» usa el valor por defecto si el campo quedó vacío | Es un mensaje de valor, no de clic | …se decide |
| El detector ve formas, no intención: un `.first` sobre un localizador sin filtrar, en otra sentencia, no lo ve | Límite de un detector estático | …aparece uno que la foto no ve |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v12**:
- **El censo de guardianes:** apagar cada pieza (cada forma quitada vuelve por mutación) y contar lo que cae.
- **El negativo tiene que morder, de a uno por proceso:** censos filtrados por commit.
- **Control positivo que aborta:** el censo de sitios (los 3 clics medidos de CMA), el barrido de mensajes
  (los 5 conocidos) y los conteos de caminos.
- **La unidad la fija el sujeto:** el sitio de clic para el censo, y la reserva exitosa para decidir si un
  genérico fue su camino.
- **Todo registro es una hipótesis:** los mensajes de «hecho» del propio programa, siete de ellos falsos
  posibles.
- **FRENAR cuando la decisión es de negocio:** MAERSK (qué fecha de retiro corresponde; el checkbox sin
  evidencia) y CMA («I Agree»).
- **El cambio y su guardián en la misma operación:** cada commit con sus pruebas y mutaciones.
- **El EOL se preserva y se verifica:** en binario, en cada commit.
- **Se declaran el residual y las premisas.**

Reglas propias del módulo (`CLAUDE.md`): las pruebas son fotos, toda prueba nueva lleva su mutación, casos
sintéticos, y la sonda antes de cada commit.

**Choques entre reglas:** uno. «Cada genérico quitado corta la reserva» choca con los pasos opcionales:
cerrar una ventana que no está no debe cortar. Lo resolví cortando solo donde antes se habría pulsado a
ciegas. En ONE, por ejemplo, si el diálogo no tiene botones visibles, sigue como antes.

## Entregable (pieza 8)

Este `.md`, sin renderizar, y `CLAUDE.md` puesto al día:
- el mecanismo;
- la prueba nueva;
- NO ENVIADA también antes de la guarda;
- la nota de los clics de CMA de `CICLO-cma-reefer.md`, que ya no es cierta;
- la red en 215 pruebas.
