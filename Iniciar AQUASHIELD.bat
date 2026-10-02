@echo off
REM ============================================================
REM  AQUASHIELD - Lanzador Principal (Modo Seguro)
REM  Doble clic para abrir el panel de control web.
REM  Las reservas se completan al 100% y se detienen antes de emitir.
REM ============================================================
cd /d "%~dp0"

REM Si falta Playwright u openpyxl, los instala una sola vez
python -c "import playwright" 2>nul || python -m pip install --user --upgrade playwright
python -c "import openpyxl" 2>nul || python -m pip install --user openpyxl

REM Si falta holidays (los feriados de Chile para la fecha de retiro de MAERSK), la instala. Sin red, pip se rinde en
REM segundos y el panel abre igual; sin la librería, el programa lo avisa y sigue de lunes a viernes.
python -c "import holidays" 2>nul || python -m pip install --user --disable-pip-version-check --timeout 5 --retries 0 holidays

REM Abre el panel (sin ventana negra de consola)
start "" pythonw "AQUASHIELD.py"
