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
5. Si un portal pide resolver un validador (CMA o COSCO), resuélvelo en el navegador y pulsa **Ya lo resolví**.
6. Al terminar, **DESCARGAR RESULTADOS** te da la planilla con el estado de cada fila.

**SOLO INICIAR SESIÓN** entra a los portales y los deja abiertos para trabajar a mano. **DETENER** corta la
corrida en curso.

El Chrome que abre el programa muestra arriba un aviso de una bandera que no admite
(`--disable-blink-features=AutomationControlled`): esa bandera la pone el programa, y el aviso se cierra con su ✕.

Si MSC muestra una página de error al iniciar sesión (al abrir su portada, al pulsar «Next» si recargarla no lo
arregla, o después de aceptar el usuario y la clave), el programa hace un solo intento más de inicio de sesión, desde
el principio, y nunca un tercero: la clave se escribe a lo más dos veces. Si no llega ni la sesión ni un error (con la
clave equivocada, por ejemplo), no vuelve a intentarlo, para no arriesgar la cuenta. Si la sesión no queda iniciada,
las filas de MSC quedan NO ENVIADA con el motivo: vuelve a armarlas más tarde. Cada error deja en la carpeta de la
corrida su captura y lo que respondió el portal.

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

## Credenciales y opciones

Usuario, clave y contrato de cada naviera se guardan en `config.json`, junto al programa y en texto plano. Se
editan desde el panel, en **Credenciales de los portales**. `config.example.json` es la plantilla, sin
credenciales.

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
| `config.json` | Credenciales y opciones. No lo compartas: trae las claves. |
| `config.example.json` | Plantilla de `config.json`, sin credenciales. |
| `logs\` | Una carpeta por corrida, con `log.txt`, las capturas y el HTML de la evidencia. Trae datos reales. |
| `perfiles\` | Los perfiles de Chrome con las sesiones iniciadas. No los borres. |

## Notas

- Usa el **Chrome** instalado en el equipo; si no está, usa Chromium.
- Si el panel web no abre, `python AQUASHIELD.py panel` abre el panel clásico de respaldo.
- Cuando algo falle, la carpeta de la corrida en `logs\` (su `log.txt` y sus capturas) dice qué pasó.
