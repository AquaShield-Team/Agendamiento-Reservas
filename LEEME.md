# AQUASHIELD · Agendamiento de Reservas

Robot que lee la planilla de reservas y, con el Chrome del equipo, entra a los portales de ONE, MSC, CMA-CGM,
COSCO, HYUNDAI (HMM) y MAERSK y arma cada booking. Al terminar, puedes descargar la planilla con el estado de
cada fila y, si se emitió, su N° de reserva.

## Uso normal

1. Doble clic a **`Iniciar AQUASHIELD.bat`**. La primera vez instala Playwright, openpyxl y holidays (los feriados de
   Chile para la fecha de retiro de MAERSK) si faltan; sin red, holidays queda para otra vez y el panel abre igual.
   Después abre el panel en el navegador, en `http://127.0.0.1:8765` o, si ese puerto lo tiene otro programa, en el
   siguiente libre, hasta el 8768: a ese programa no lo cierra, y el registro del panel lo dice. Si ya hay un panel de
   AQUASHIELD abierto en alguno de esos cuatro puertos, lo trata como si estuviera en el 8765.
2. En **PLANILLA DE RESERVAS**, arrastra el `.xlsx` o haz clic para elegirlo.
3. Elige la **Naviera** (la hoja de la planilla) y el **Operador**, y marca las filas que quieres correr
   (**todas** y **ninguna** ayudan).
4. Pulsa **ARMAR LAS RESERVAS**. El avance queda en el **Registro operativo detallado**.
5. Si un portal pide resolver un validador (CMA o COSCO), resuélvelo en el navegador y pulsa **Ya lo resolví**. Con el
   deslizador de CMA no hace falta pulsarlo: cuando el portal te deja pasar, el programa sigue solo.
6. Al terminar, **DESCARGAR RESULTADOS** te da la planilla con el estado de cada fila.

**SOLO INICIAR SESIÓN** entra a los portales y los deja abiertos para trabajar a mano. **DETENER** corta la
corrida en curso; en **SOLO INICIAR SESIÓN**, cierra el navegador y no entra a los portales que faltaban.

El Chrome que abre el programa muestra arriba un aviso de una bandera que no admite
(`--disable-blink-features=AutomationControlled`): esa bandera la pone el programa, y el aviso se cierra con su ✕.

Si MSC muestra una página de error al iniciar sesión (al abrir su portada, al pulsar «Next» si recargarla no lo
arregla, o después de aceptar el usuario y la clave), el programa hace un solo intento más de inicio de sesión, desde
el principio, y nunca un tercero: la clave se escribe a lo más dos veces. Si no llega ni la sesión ni un error (con la
clave equivocada, por ejemplo), no vuelve a intentarlo, para no arriesgar la cuenta. Si la sesión no queda iniciada,
las filas de MSC quedan NO ENVIADA con el motivo: vuelve a armarlas más tarde. Cada error deja en la carpeta de la
corrida su captura y lo que respondió el portal.

Si CMA-CGM muestra «El acceso está restringido temporalmente», o su página no termina de cargar en 30 s (la portada,
o la verificación del navegador que a veces muestra antes del deslizador), el programa deja CMA-CGM por esa corrida,
sin reintentar ni recargar: sus filas quedan NO ENVIADA con el motivo, y sigue con las otras navieras. La captura y el
HTML quedan en la carpeta de la corrida. El deslizador lo sigues pasando tú, como siempre: cuando el portal te deja
pasar (el programa lo comprueba dos veces seguidas, con 2 s entre una y otra), sigue solo, sin esperar «Ya lo
resolví», y si mientras tanto restringe el acceso, deja CMA-CGM igual. **DETENER** corta esa espera: si estaba
armando una reserva, esa fila queda DETENIDO.

Lo mismo a mitad de una reserva de CMA-CGM: si aparece el acceso restringido, o su verificación no deja pasar en 30 s,
el programa deja CMA-CGM por esa corrida. Si a mitad de una reserva te pide deslizar la flecha, la deslizas tú; esa
reserva igual queda NO ENVIADA, porque, según DataDome, al dejarte pasar la página se vuelve a cargar y se pierde lo
que se había llenado, y el programa sigue con la fila siguiente.

Si en una reserva de CMA-CGM falla el tamaño y tipo del contenedor, su peso, la mercancía (el código 030313), la
temperatura del Reefer, la casilla «I Agree» o los comentarios, esa fila queda NO ENVIADA, con el motivo, la captura y
el HTML del paso: no se arma sin ellos. Después de guardar la temperatura, el programa mira que la página la muestre
guardada (el panel Reefer cerrado, sin «to complete» y con la temperatura en «Operando en»); si no, también queda NO
ENVIADA. Cada fila es una reserva de un contenedor: el programa no escribe la cantidad, y si el campo «Cantidad» de
CMA-CGM no dice 1, la fila queda NO ENVIADA.

En MAERSK, el tipo de contenedor es siempre «40 Reefer High», el de las filas, y en los ajustes reefer, «Standard
(40´)». Antes de elegir cada uno, el programa guarda la lista de opciones (su captura y su HTML, en la carpeta de la
corrida); si la lista no trae exactamente una, la fila queda NO ENVIADA, con el motivo, sin pulsar nada. Si la planilla
trae una columna de contenedor y una fila de MAERSK pide otro que «40 HC REEFER», esa fila queda NO ENVIADA, con el
motivo, sin entrar al portal: resérvala a mano. El panel la marca antes de correr, junto a «Reserva N» («otro
contenedor: …»). Una celda vacía en esa columna vale «40 HC REEFER», en el panel y en la consola.

Si la fila trae viaje, las seis navieras reservan solo una salida con ese viaje. Si el portal ya no lo ofrece (pasó
su cierre, por ejemplo), la fila queda NO ENVIADA, con el motivo («ninguna de las opciones de la nave trae el viaje de
la fila»), y la lista que mostró el portal queda en la carpeta de la corrida: corrige el viaje en la planilla y vuelve a
armarla.

Cuando el panel te pide resolver algo en el navegador («Te toca a ti»), `log.txt` anota cuándo empezó la pausa, por
qué, y cuándo terminó: si pulsaste «Ya lo resolví» o «Detener», si pasaron 10 minutos sin respuesta o, con el
deslizador de CMA, si el portal te dejó pasar o restringió el acceso.

## Instalar y mantenerlo al día

El programa se instala como un clon del repositorio, en la rama **`estable`**. Esa rama la avanza solo Marcelo,
después de probar; los cambios de cada día van a `main`, que los equipos de uso no reciben. El repositorio es público:
no hace falta una cuenta de GitHub, y el programa nunca pide ni guarda una clave para actualizarse.

**Para instalarlo** hacen falta Python 3.13, Git for Windows y Chrome. En PowerShell, en la carpeta donde quieras
dejarlo (aquí, `C:\AQUASHIELD`):

```
git clone -b estable https://github.com/AquaShield-Team/Agendamiento-Reservas.git "C:\AQUASHIELD"
```

Si git contesta «Remote branch estable not found», Marcelo todavía no creó la rama: avísale. Después, abre
`Iniciar AQUASHIELD.bat` con doble clic. La primera vez, la ventana negra instala las librerías de Python que faltan
(hace falta internet); si no puede, lo dice y espera una tecla, sin abrir el panel. Al abrirse, el panel crea
`config.json` desde `config.example.json`, sin credenciales, y lo dice en un aviso bajo la nota del modo: escribe las
tuyas en Credenciales (ver «Credenciales y opciones»). Si al panel le falta algo para empezar, ese aviso dice qué y cómo
resolverlo.

Si ya tenías un clon en `main`, pásalo a `estable` en la misma carpeta, sin perder tu `config.json`, tus perfiles ni
tus registros (git no los versiona):

```
git -C "C:\AQUASHIELD" fetch origin
git -C "C:\AQUASHIELD" switch estable
```

**Cada vez que lo abres**, los dos lanzadores (`actualizar.py`) traen la última versión de `estable` antes de abrir el
panel, y el registro del panel dice qué pasó: que se actualizó, que ya estaba al día, o por qué no lo hizo. Si no se
actualiza, el panel abre igual, con la versión que tiene el equipo. No se actualiza:
- sin red, o si GitHub no contesta;
- si cambiaste un archivo del programa, o si la versión nueva trae un archivo o una carpeta con el nombre de algo tuyo
  de esta carpeta: no lo pisa. Avísale a Marcelo;
- si la carpeta no está en la rama `estable`. Así, el equipo de desarrollo de Marcelo, en `main`, nunca se actualiza
  solo.

Tu `config.json`, tus perfiles de Chrome, tus registros (`logs\`) y tus planillas no se tocan. Si la ventana negra dice
que la actualización quedó a medias y no abre el panel, cierra el programa que tenga abierto un archivo de la carpeta
(un editor, por ejemplo) y vuelve a abrirlo.

**Cómo avanza Marcelo la rama `estable`.** Cuando una versión de `main` está probada, la publica en `estable` desde su
equipo, en PowerShell (`<commit>` es el de la versión probada; la primera vez, el mismo comando crea la rama):

```
git -C "C:\dev\Agendamiento Reservas" fetch origin
git -C "C:\dev\Agendamiento Reservas" log --oneline origin/estable..<commit>
git -C "C:\dev\Agendamiento Reservas" push origin <commit>:refs/heads/estable
git -C "C:\dev\Agendamiento Reservas" ls-remote --heads origin estable
```

El `log` muestra lo que van a recibir los equipos. `estable` solo avanza: el commit nuevo tiene que venir después del
que tiene (git rechaza el `push` si no, y no se fuerza). Un equipo con una `estable` que ya no se continúa deja de
actualizarse hasta que alguien lo arregle a mano.

## Modo seguro y emisión

Con `Iniciar AQUASHIELD.bat` **nada se emite**: cada reserva se llena completa y se detiene antes del botón que
la confirma. La emisión la haces tú, en el portal.

`Iniciar AQUASHIELD_EMISION.bat` abre el mismo panel en **modo emisión**: pulsa el botón final y crea reservas
reales e irreversibles. Úsalo solo cuando corresponda.

Cada corrida dice al empezar, en el registro del panel y en su `log.txt`, en qué modo corre y por qué. Si ya hay un
panel abierto en el otro modo, el lanzador avisa y no abre nada: cierra ese panel con su botón rojo de apagar, arriba
a la derecha, o cerrando su pestaña y esperando unos dos minutos, y vuelve a abrir el lanzador. Si ese panel está
armando reservas, espera antes a que termine.

Antes de armar las reservas, el panel vuelve a mirar en qué modo está: si no es el que muestra la página (por ejemplo,
una pestaña que quedó abierta de un panel que se cerró, mientras se abría otro en el otro modo), no arma nada y te pide
recargarla (F5).

El panel atiende solo a su propia página: otra página abierta en el mismo navegador no puede subirle una planilla,
cambiar las credenciales, armar reservas ni apagarlo. Si alguna vez dice que un pedido «no viene de su propia página»,
recárgala (F5).

## Credenciales y opciones

Usuario, clave y contrato de cada naviera se guardan en `config.json`, junto al programa y en texto plano. Se
editan desde el panel, en **Credenciales de los portales** (la llave, arriba a la derecha). `config.example.json` es
la plantilla, sin credenciales: si falta `config.json`, el panel lo crea desde ella. Si `config.json` no se puede leer
(por ejemplo, después de editarlo a mano), el panel lo dice, con la línea donde está el error, y no arma reservas hasta
que se corrija.

En `config.json`, dentro de «opciones», están también el peso bruto por contenedor reefer (`peso_reefer_kg`,
22500) y la temperatura reefer (`temperatura_reefer_c`, -20). La temperatura de la planilla, si la fila la trae,
manda sobre la de `config.json`. Si falta una de esas llaves, el programa usa ese mismo valor y lo avisa.

También en «opciones»:
- `contratos_por_defecto`: el contrato que va cuando ni la fila ni las credenciales traen uno, para ONE a Estados
  Unidos (`one_usa`) y a otros mercados (`one_otros`), MSC (`msc`) y HYUNDAI (`hyundai`). Sin contrato, la reserva
  de HYUNDAI queda NO ENVIADA.
- `codigo_shipper_hyundai`: el código de la empresa como Shipper en HYUNDAI. Sin él, se busca solo por el nombre.

En la plantilla vienen vacíos. Si falta una de esas llaves, el programa sigue sin ella y lo avisa.

## Archivos

| Archivo | Para qué |
|---|---|
| `Iniciar AQUASHIELD.bat` | Abre el panel en modo seguro (no emite). |
| `Iniciar AQUASHIELD_EMISION.bat` | Abre el panel en modo emisión (reservas reales). |
| `AQUASHIELD.py` | El programa. |
| `AQUASHIELD_EMISION.py` | Arranca el programa en modo emisión. |
| `actualizar.py` | Trae la última versión de la rama `estable` al abrir (lo corren los dos lanzadores). |
| `config.json` | Credenciales y opciones. No lo compartas: trae las claves. |
| `config.example.json` | Plantilla de `config.json`, sin credenciales. |
| `logs\` | Una carpeta por corrida, con `log.txt`, las capturas y el HTML de la evidencia. Trae datos reales. |
| `perfiles\` | Los perfiles de Chrome con las sesiones iniciadas. No los borres. |

## Notas

- Usa el **Chrome** instalado en el equipo; si no está, usa Chromium.
- Si el panel web no abre, `python AQUASHIELD.py panel` abre el panel clásico de respaldo.
- Cuando algo falle, la carpeta de la corrida en `logs\` (su `log.txt` y sus capturas) dice qué pasó.
