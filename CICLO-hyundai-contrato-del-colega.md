# CICLO-hyundai-contrato-del-colega · Encargo 88: por qué HYUNDAI falla en el equipo del colega

> **metodo-ciclo v39.** Base: `main` en `82dbb47`, árbol limpio. **Veredicto del paso 0: NOTA** (medido, y no es del
> programa): no hay arreglo de código. **Un commit:** este informe y una corrección de CLAUDE.md. **No se subió nada.** Sin
> datos de clientes: las corridas se leyeron en su lugar, en solo lectura; el contrato, la nave y el operador no salen de
> ahí (las cifras del contrato se compararon en memoria y se imprimieron tapadas).

## Qué se pidió

Comparar la corrida de HYUNDAI del colega (28-10, 10:21, en «1. pruebas») con la más reciente de este equipo (28-10,
10:44, en `logs/`, modo prueba), paso por paso, hasta donde se separan; decir si es del programa o del equipo del colega;
y, aparte, cómo le fue a la fila de MSC con destino final de la corrida de este equipo. FRENA SI el arreglo cambia la regla
de «Contract No» o un estado que ve el equipo, o toca otra naviera.

## Lo medido

- **La carpeta del colega sigue fuera de git:** `git check-ignore` la da por la lista blanca (`.gitignore:6:/*`), con 0
  archivos seguidos y 0 commits que nombren «1. pruebas».
- **Es la misma versión del programa para HYUNDAI.** El colega se actualiza desde `estable`, que está en `b39c95c`
  (encargo 85); este equipo corre `main`. Entre los dos, ninguna línea cambiada de `AQUASHIELD.py` toca HYUNDAI (los
  cambios son de MSC, CMA-CGM y el panel). Por los textos fijos de los dos log.txt (`.trabajo/e88/comparar.py`: cada línea
  sin la hora, los números ni los valores), los 33 moldes del colega están también en la corrida de este equipo, salvo los
  dos del corte.
- **Las dos corridas van igual hasta «Contract No»:** el mismo login (la página de login, sesión en el tablero),
  «Booking Reference», «Select Vessel» (origen, destino, la nave por su «1st Vessel», el modal «Alternate Vessel
  Option»), y en «Booking Details», el Contract Holder y el Shipper elegido desde su modal.
- **Ahí se separan.** En este equipo, el programa lee las opciones de «Contract No», elige el contrato de `config.json` y
  sigue hasta la guarda: 3 filas OK-EJEMPLO. En el del colega, sus 2 filas quedan NO ENVIADA con «Contract No de HYUNDAI:
  no encontré un contrato en las credenciales o en config.json → opciones → contratos_por_defecto → hyundai», y ya en el
  paso 2 el log dice «sin contrato en las credenciales ni en config.json; queda el del portal».
- **Su portal ofrecía el mismo contrato** (`.trabajo/e88/contratos.py`): en el HTML de su corte, el campo
  `#selContractNo` trae una sola opción real, además de «Select», «Dummy» y «Direct Input», y es la misma que muestra la
  línea «Contract No opciones» de las 3 filas de este equipo (comparadas en memoria). No es la cuenta ni el portal: es el
  `config.json` del colega, que el panel creó desde la plantilla, con el contrato vacío (encargo 61).
- **Es lo mismo que el 26-10:** las 5 filas de HYUNDAI de esa corrida quedaron NO ENVIADA por el mismo corte. **La del
  23-10 guardada aquí no tiene HYUNDAI** (sus navieras son ONE, MSC, CMA-CGM, COSCO y MAERSK): esa parte de la premisa no
  se pudo confirmar con lo que hay en este equipo.

### Premisa que se corrigió

- **CLAUDE.md decía que HYUNDAI sin contrato «corta antes de Booking Details».** Corta en «Booking Details», en «Contract
  No», después del Contract Holder y del Shipper, sin pulsar nada más. Corregido, con lo que tiene que hacer un equipo
  nuevo.

## Lo que tiene que hacer el colega

**En el panel, Credenciales → la fila de HYUNDAI de su operador → columna «Contrato»: escribir el código del contrato
que su portal muestra en «Contract No» (el mismo de este equipo, sin el « - (GA)» del final), y Guardar.**

## La fila de MSC con destino final

**No hay ninguna en `logs/` de este equipo:** desde el encargo 86 hay una sola corrida (la de las 10:44 del 28-10), y es
solo de HYUNDAI. La última corrida con MSC es del 15-10, anterior al cambio. La prueba en el portal de «Door», «TRUCK» y
el destino elegido sigue pendiente.

## Decisiones que tomé (Modo autónomo)

| Decisión | Por qué |
|---|---|
| No cambiar el programa | Es el `config.json` del colega; el código de HYUNDAI es el mismo, y cualquier cambio en el corte sería cambiar la regla de «Contract No» (FRENA) |
| Corregir CLAUDE.md | Decía «antes de Booking Details», y lo medido dice que el corte está en ese paso |
| No revisión de código | No hay diff de código: solo este informe y CLAUDE.md |

## Residual

- **Con un contrato configurado que no está entre las opciones, el paso 3 elige la primera real, por su posición**
  (`Contract No (primera real)`). Ya estaba registrado (encargos 70 y 71) y sigue: cambiarlo es la regla de «Contract
  No». No se vio en lo medido.
- El motivo de la NO ENVIADA nombra `config.json`, no la columna «Contrato» de Credenciales del panel, que es donde el
  operador lo escribe. Cambiar ese texto cambia lo que ve el equipo (FRENA): queda para que lo decidas.

## Compuertas

| compuerta | resultado |
|---|---|
| Pruebas que leen los documentos | `test_guarda_datos` y `test_sonda`: `Ran 32 tests · OK`. La suite completa no se corrió: el commit no toca código ni pruebas (este informe y CLAUDE.md) |
| Sonda de secretos | 0 con `--dry-run` y 0 después del `git add` |
| Guarda de datos (hook pre-commit) | a mano, sobre lo que git versionaría: 0 hallazgos en 127 archivos; y el hook, al commitear |

## Push

Un commit de `main` sin subir: este. Con el correo noreply de autor y de committer. Antes de subir, en una consola:

```bash
git -C "C:\dev\Agendamiento Reservas" log origin/main..main --format="%h %ae %ce %s"
```

Tiene que mostrar solo el correo noreply en las dos columnas. Después:

```bash
git -C "C:\dev\Agendamiento Reservas" push origin main
git -C "C:\dev\Agendamiento Reservas" rev-parse main
git -C "C:\dev\Agendamiento Reservas" ls-remote origin refs/heads/main
```

Los dos hashes tienen que ser iguales. `estable` no se movió, y este commit no cambia nada de lo que corre en los equipos.
