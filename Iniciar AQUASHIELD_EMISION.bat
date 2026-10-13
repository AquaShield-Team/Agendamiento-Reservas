@echo off
REM ============================================================
REM  AQUASHIELD - Lanzador Principal (Modo Emision Real)
REM  Doble clic para abrir el panel en modo emision sin consola.
REM  Las reservas seleccionadas se enviaran y confirmaran formalmente.
REM ============================================================
REM Todo va en un solo bloque que termina en "exit /b": cmd lo lee entero antes de correrlo, asi que si la
REM actualizacion cambia este archivo mientras corre, sigue con lo que ya leyo y no lee el nuevo a la mitad.
cd /d "%~dp0"
(
  REM Al abrir, trae la ultima version de la rama estable: actualizar.py. Sin red, o si algo lo impide, sigue con
  REM la version que tiene, y el panel lo dice. Sale con 3 solo si una actualizacion quedo a medias: no se abre.
  python actualizar.py
  if errorlevel 3 (
    pause
    exit /b 3
  )

  REM Si falta Playwright u openpyxl, los instala una sola vez
  python -c "import playwright" 2>nul || python -m pip install --user --upgrade playwright
  python -c "import openpyxl" 2>nul || python -m pip install --user openpyxl

  REM Sin playwright u openpyxl el panel no abre: lo dice y espera una tecla, en vez de cerrarse sin decir nada.
  python -c "import playwright, openpyxl" 2>nul
  if errorlevel 1 (
    echo.
    echo AQUASHIELD no puede abrir: faltan las librerias playwright u openpyxl de Python, y no se pudieron instalar.
    echo Revisa la conexion a internet y vuelve a abrirlo. Si sigue igual, escribe esto en PowerShell:
    echo   python -m pip install --user playwright openpyxl
    echo.
    pause
    exit /b 1
  )

  REM Si falta holidays, los feriados de Chile para la fecha de retiro de MAERSK, la instala. Sin red, pip se
  REM rinde en segundos y el panel abre igual; sin la libreria, el programa lo avisa y sigue de lunes a viernes.
  python -c "import holidays" 2>nul || python -m pip install --user --disable-pip-version-check --timeout 5 --retries 0 holidays

  REM Abre el panel en modo emision, sin ventana negra de consola
  start "" pythonw "AQUASHIELD_EMISION.py"
  exit /b 0
)
