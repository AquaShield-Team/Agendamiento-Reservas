# CICLO · Pendientes de ONE, CMA, COSCO y MAERSK con la evidencia de la guarda

**Módulo:** Agendamiento Reservas · **Fecha:** 2026-09-24 · **Método:** skill `metodo-ciclo` v12 ·
**Base:** `50dd24b` · **Commits:** solo el de este informe (local, sin push; el repo no tiene remoto).

> Sin datos reales. No se abrió ningún archivo de `logs/`: solo se listaron nombres de archivo y fechas de
> carpeta. De la copia del Escritorio se leyeron solo la fecha, la huella y dos nombres de función de su
> `AQUASHIELD.py`.

## Veredicto

**FRENO en las cuatro navieras.** La evidencia de la guarda no existe:
- no hay ningún `<nav>_f<fila>_guarda.*` ni `_sin_objetivo.*`, ni en `logs/` ni en ningún otro lugar de la
  máquina;
- la corrida más reciente, en los dos `logs/` que hay, es del 2026-09-23 a las 09:25. La evidencia de la guarda
  existe en el código desde `7b3e3e2`, del 2026-09-24.

Es el FRENA SI «la evidencia de alguna naviera no alcanza para decidir sin ambigüedad», en las cuatro:

| Naviera | Qué pendiente | Qué falta |
|---|---|---|
| ONE | el campo del contrato | la corrida: la línea «contrato ONE: escrito … en Otros Contratos ✓» o, si corta, `one_f<fila>_sin_objetivo.html` |
| CMA | «I Agree», el panel Reefer y el aviso «Faltan algunos ajustes…» | `cma_f<fila>_guarda.html` o `_sin_objetivo.html` |
| COSCO | Booking Details completo, sin «… is required» | `cosco_f<fila>_guarda.html` y su marco `bkg2` |
| MAERSK | la casilla de términos por su texto | `mk_f<fila>_guarda.html`, con las raíces shadow |

**No implementé nada:** ningún pendiente se decide sin su evidencia, y la decisión de la fecha de retiro cae
entera en MAERSK, cuyo freno pide ver el formulario (abajo). Sin commits de código.

**PASO 0: DESCARTE.** La premisa, que la corrida existe, es falsa.

## Lo medido

1. **`logs/` del repo:** 6 carpetas de corrida, la más nueva del 2026-09-23 09:25. Hay 0 HTML y 0 archivos de
   guarda o de paso sin objetivo.
2. **Búsqueda amplia:** `C:\dev` y la carpeta del usuario, 105 581 directorios. Resultado: 0 archivos de
   evidencia y 2 carpetas `logs/` con corridas.
3. **La otra copia está en el Escritorio de OneDrive** (`…\Escritorio\AQUASHIELD\Agendamiento Reservas`):
   - su `AQUASHIELD.py` es del 2026-09-23 10:04, con otra huella, y no tiene `_evidencia_antes_de_la_guarda` ni
     `ObjetivoNoEncontrado`;
   - tiene su propio `Iniciar AQUASHIELD.bat` y su propio `config.json`;
   - su `logs/` tiene las mismas 6 corridas y 0 HTML.

   Una corrida lanzada desde esa copia **no dejaría evidencia**, y además corre sin los cambios de los últimos
   encargos (clics a ciegas y evidencia). Pero su `logs/` tampoco tiene corridas nuevas, así que la fila no se
   corrió ahí.
4. **La fecha de retiro solo la elige MAERSK.** Lo medí leyendo los seis reservadores:
   - MAERSK marca el primer día habilitado del selector «Pick-up date», en «Additional details»;
   - «Door Pickup = CY» de COSCO es un tipo de servicio, no una fecha;
   - las demás fechas son de zarpe o de búsqueda de itinerario. MSC busca con el día de carga de la planilla y,
     si falta, con su día de retiro; no llena ningún campo de retiro.

   Tu decisión («el programa no la elige en ninguna naviera») toca, entonces, solo a MAERSK.
5. **El peso ya es 22 500 en las seis:** CMA, COSCO, HYUNDAI y MAERSK lo toman de `PESO_REEFER`, y ONE y MSC
   lo escriben como literal. No hay nada que cambiar.

## Lo que hace falta para cerrar

1. **Corre desde la copia del repo:** `C:\dev\Agendamiento Reservas\Iniciar AQUASHIELD.bat`. Si abres el
   programa desde el Escritorio, corres la copia vieja, que no deja evidencia.
2. Confirma arriba en el panel «🛡️ Modo Seguro Activo», y corre una fila en ONE, CMA (con nave), COSCO y MAERSK.
3. La evidencia queda en `C:\dev\Agendamiento Reservas\logs\web_<nav>_<usuario>_<fecha>\`. Con eso, vuelve a
   mandar este mismo encargo.

**Dos límites que conviene decidir antes de esa corrida:**
- **La fecha de MAERSK no se puede medir con el código de hoy.** El programa elige la fecha antes de la
  revisión, así que la evidencia de la guarda mostraría la revisión con la fecha ya puesta y no diría si el
  formulario deja avanzar sin ella. Para medirlo hace falta una corrida que no la elija.
  - Mi recomendación: aplicar ya tu regla en MAERSK (dejar el campo sin tocar) y medir con el candado cerrado.
    Si el portal no deja avanzar, MAERSK queda en REVISAR y la evidencia de la guarda muestra dónde se detuvo;
    ahí se revierte, como pide el freno. Con el candado cerrado no se emite nada.
  - Es tu decisión, porque aplica la regla antes de medir.
- **El panel Reefer de CMA solo queda medido si CMA corta en un paso Reefer, o si el panel sigue en la página
  en la guarda.** Si pasa Reefer sin cortar y el panel ya no está, sus campos y su botón de guardar seguirán sin
  medir. Si lo quieres asegurado, hace falta decidir una evidencia más en ese paso.

## Re-medir (pieza 1)

- **La evidencia:** listar las carpetas de `logs/` con su fecha y buscar nombres
  `_f<n>_(guarda|sin_objetivo)(_marco<n>)?.(html|png)`. El patrón tiene control positivo: calza con 6 nombres
  sintéticos de evidencia y con ninguno de 4 que no lo son.
- **La búsqueda amplia:** `os.walk` sobre `C:\dev` y la carpeta del usuario, con el mismo patrón, contando las
  carpetas `logs/` que tienen carpetas de corrida.
- **Las dos copias:** la huella sha256, la fecha y la presencia de `_evidencia_antes_de_la_guarda` y
  `ObjetivoNoEncontrado` en cada `AQUASHIELD.py`.
- **La fecha:** buscar «retiro», «pickup» y «fecha» en los reservadores y leer cada sitio.

## NO retroceder (pieza 2)

- **No implementes un pendiente sin su evidencia:** es el freno de este encargo.
- **No quites la fecha de MAERSK sin decidir cómo medirla:** es el camino de sus 5 reservas exitosas.
- **Para medir, no corras desde la copia del Escritorio:** no deja evidencia.

## Premisas del encargo contrastadas (pieza 5)

- **«Marcelo corrió una fila con el candado cerrado… la evidencia está en las carpetas de corrida más
  recientes»:** refutada. No hay corridas después del 2026-09-23 09:25 en ninguno de los dos `logs/`, ni
  evidencia de guarda en la máquina.
- **«El peso es siempre 22500»:** confirmada en el código de hoy.
- **«La fecha de retiro … no la elige en ninguna naviera»:** hoy la elige solo MAERSK.

## Universo y cobertura (pieza 3)

- **Búsqueda:** 105 581 directorios de `C:\dev` y de la carpeta del usuario, con los archivos de OneDrive
  incluidos.
- **Excluidos:** `node_modules`, `.git`, `__pycache__`, `site-packages`, las cachés, los perfiles de
  Microsoft, Google y Mozilla, `Packages` y las sandboxes de la red. Ninguno aloja un `logs/` del programa.
- **Fuera del universo:** otras máquinas. Si la fila se corrió en otro equipo, su evidencia está allá.

## Defectos de instrumento cazados (pieza 4)

Ninguno nuevo. El patrón de la búsqueda se validó con su control positivo antes de dar el cero por bueno.

## Residual (pieza 6)

| Qué queda | Por qué | Se reabre si… |
|---|---|---|
| Los pendientes de ONE, CMA, COSCO y MAERSK | Falta la evidencia | …hay una corrida desde la copia del repo |
| La fecha de retiro de MAERSK | Con el código de hoy la evidencia no la mide | …decides cómo medirla (arriba) |
| El panel Reefer de CMA, si no corta ahí | La evidencia es solo en la guarda y en los cortes | …decides una evidencia más en ese paso |
| Dos copias del programa (repo y Escritorio), cada una con su `config.json` | La del Escritorio está detenida en el 2026-09-23 | …decides cuál es la que se usa |
| La temperatura: si una hoja trae columna de temperatura, se usa por fila | Hoy ninguna hoja la trae, así que en la práctica es única (`TEMP_REEFER`) | …una hoja trae esa columna |

## Reglas de método aplicadas (pieza 7)

Skill `metodo-ciclo` **v12**:
- **PASO 0 de cuatro valores:** DESCARTE, porque la premisa era falsa.
- **FRENAR:** los cuatro pendientes necesitan evidencia, y dos decisiones son tuyas (cómo medir la fecha de
  MAERSK y si se suma evidencia en el paso Reefer).
- **Control positivo que aborta:** el patrón de la búsqueda, antes de leer su cero.
- **El universo se declara:** los directorios recorridos y los excluidos.
- **Todo registro es una hipótesis:** el encargo daba la corrida por hecha y no lo estaba.

**Gate:** no hubo commits de código. El censo completo de `1ccf195` (15:24: 438 mutaciones, 526 pares, 236
pruebas) sigue vigente: desde entonces solo cambiaron archivos `.md`. La sonda de secretos corre sobre el
staging de este informe.

## Entregable (pieza 8)

Este `.md`, sin renderizar. `CLAUDE.md` no cambia.
