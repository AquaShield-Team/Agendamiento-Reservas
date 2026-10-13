@echo off
REM ============================================================
REM  AQUASHIELD - Lanzador Principal (Modo Seguro)
REM  Doble clic para abrir el panel de control web.
REM  Las reservas se completan al 100% y se detienen antes de emitir.
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

  REM Si falta holidays, los feriados de Chile para la fecha de retiro de MAERSK, la instala. Sin red, pip se
  REM rinde en segundos y el panel abre igual; sin la libreria, el programa lo avisa y sigue de lunes a viernes.
  python -c "import holidays" 2>nul || python -m pip install --user --disable-pip-version-check --timeout 5 --retries 0 holidays

  REM Abre el panel, sin ventana negra de consola
  start "" pythonw "AQUASHIELD.py"
  exit /b 0
)
