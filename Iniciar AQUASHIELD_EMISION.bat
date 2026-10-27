@echo off
REM ============================================================
REM  AQUASHIELD - Lanzador Principal (Modo Emision Real)
REM  Doble clic para abrir el panel en modo emision sin consola.
REM  Las reservas seleccionadas se enviaran y confirmaran formalmente.
REM ============================================================
REM Todo va en un solo bloque que termina en "exit /b": cmd lo lee entero antes de correrlo, asi que si la
REM actualizacion cambia este archivo mientras corre, sigue con lo que ya leyo y no lee el nuevo a la mitad.
REM ASCII a proposito: la consola de Windows no lee otra cosa en un .bat. Lo que se ve con tildes lo escribe Python.
cd /d "%~dp0"
(
  title AquaShield - Modulo Reservas - EMISION
  REM Sin esta variable, cmd corre un .bat de esta carpeta por su nombre solo.
  set "NoDefaultCurrentDirectoryInExePath=1"

  REM 1. Python 3.11 o mas nuevo. Si falta, lo ofrece instalar con winget, solo para este usuario y sin permisos de
  REM administrador, y pregunta antes. Sin respuesta en 60 segundos, no instala nada.
  python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
  if not errorlevel 0 cmd /c exit 1
  if errorlevel 1 (
    echo.
    echo   AQUASHIELD necesita Python 3.11 o mas nuevo, y este equipo no lo tiene.
    where $PATH:winget >nul 2>nul
    if errorlevel 1 (
      echo   Para instalarlo: abre Microsoft Store, busca Python 3.13 y presiona Obtener. Despues vuelve a abrir AQUASHIELD.
    ) else (
      echo   Puedo instalarlo con winget, solo para este usuario y sin permisos de administrador.
      echo   Si dices que si, winget acepta los terminos de uso del paquete y de su fuente.
      choice /c SN /n /t 60 /d N /m "  Falta Python. Lo instalo ahora? (S/N) "
      if errorlevel 2 (
        echo   Para instalarlo: abre Microsoft Store, busca Python 3.13 y presiona Obtener. Despues vuelve a abrir AQUASHIELD.
      ) else if errorlevel 1 (
        winget install --id Python.Python.3.13 -e --scope user --architecture x64 --source winget --silent --accept-package-agreements --accept-source-agreements --disable-interactivity
        if not errorlevel 0 cmd /c exit 1
        if errorlevel 1 (
          echo   No se pudo con winget. Para instalarlo: abre Microsoft Store, busca Python 3.13 y presiona Obtener. Despues vuelve a abrir AQUASHIELD.
        ) else (
          echo   Python quedo instalado. Cierra esta ventana y vuelve a abrir AQUASHIELD.
        )
      ) else (
        echo   Para instalarlo: abre Microsoft Store, busca Python 3.13 y presiona Obtener. Despues vuelve a abrir AQUASHIELD.
      )
    )
    echo.
    pause
    exit /b 1
  )

  REM 2. Git. Sin el, AQUASHIELD abre igual pero no se actualiza solo. Lo ofrece instalar igual que Python, pero una sola
  REM vez: la marca logs\.git-preguntado evita esperar la respuesta, hasta 60 segundos, en cada inicio.
  where $PATH:git >nul 2>nul
  if errorlevel 1 if not exist "logs\.git-preguntado" (
    echo.
    echo   Este equipo no tiene Git: AQUASHIELD abre, pero no se va a poder actualizar solo.
    where $PATH:winget >nul 2>nul
    if errorlevel 1 (
      echo   Para instalarlo: entra a https://git-scm.com/download/win y corre el instalador. Despues vuelve a abrir AQUASHIELD.
    ) else (
      echo   Puedo intentar instalarlo con winget, solo para este usuario. Si Windows pide permisos de administrador y no los tienes, no se instala.
      echo   Si dices que si, winget acepta los terminos de uso del paquete y de su fuente.
      choice /c SN /n /t 60 /d N /m "  Falta Git. Lo instalo ahora? (S/N) "
      if errorlevel 2 (
        echo   Para instalarlo: entra a https://git-scm.com/download/win y corre el instalador. Despues vuelve a abrir AQUASHIELD.
      ) else if errorlevel 1 (
        winget install --id Git.Git -e --scope user --source winget --silent --accept-package-agreements --accept-source-agreements --disable-interactivity
        if not errorlevel 0 cmd /c exit 1
        if errorlevel 1 (
          echo   No se pudo con winget. Para instalarlo: entra a https://git-scm.com/download/win y corre el instalador. Despues vuelve a abrir AQUASHIELD.
        ) else (
          echo   Git quedo instalado: la proxima vez que abras AQUASHIELD se actualiza.
        )
      ) else (
        echo   Para instalarlo: entra a https://git-scm.com/download/win y corre el instalador. Despues vuelve a abrir AQUASHIELD.
      )
    )
    echo.
    if not exist "logs" mkdir "logs"
    type nul > "logs\.git-preguntado"
  )

  REM 3. Al abrir, trae la ultima version de la rama estable: actualizar.py. Sin red, o si algo lo impide, sigue con
  REM la version que tiene, y el panel lo dice. Sale con 3 solo si una actualizacion quedo a medias: no se abre.
  python actualizar.py
  if errorlevel 3 (
    pause
    exit /b 3
  )

  REM 4. Deja listas las librerias del programa en su entorno propio, la carpeta .venv de esta carpeta: preparar_entorno.py
  REM las instala solo la primera vez, o si cambiaron, sin terminal y sin permisos de administrador. Sale con 0 si el
  REM entorno propio esta listo, con 10 si abre con el Python del equipo porque este ya tiene todo, y con 11 si no se
  REM puede abrir: lo explica en pantalla. Cualquier otro codigo, de 12 en adelante o de 1 a 9, es una falla del propio
  REM preparador: la primera linea de abajo pasa los de 12 en adelante al 1, y el 1 a 9 abre solo con un Python completo.
  python -I preparar_entorno.py
  if not errorlevel 0 cmd /c exit 1
  if errorlevel 12 cmd /c exit 1
  if errorlevel 11 (
    echo.
    pause
    exit /b 1
  )
  if errorlevel 10 (
    REM El Python del equipo tiene todo lo que el programa usa: se abre con ese.
  ) else if errorlevel 1 (
    REM preparar_entorno.py fallo por algo que nadie previo: se abre solo si el Python del equipo ya tiene las librerias.
    python -c "import playwright.sync_api, openpyxl" 2>nul
    if errorlevel 1 (
      echo.
      echo AQUASHIELD no puede abrir: fallo la preparacion de las librerias. Avisa a quien te dio el programa.
      echo.
      pause
      exit /b 1
    )
  ) else (
    REM Sin las comillas del PATH: una entrada entre comillas con un parentesis en el nombre, como la de Program Files x86,
    REM cerraria las comillas de este set y su parentesis cerraria el bloque entero antes de correr nada.
    set "PATH=%~dp0.venv\Scripts;%PATH:"=%"
  )

  REM Abre el panel en modo emision, sin ventana negra de consola
  start "" pythonw "AQUASHIELD_EMISION.py"
  exit /b 0
)
