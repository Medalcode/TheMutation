@echo off
title TheMutation - Humanizador de Texto IA

echo =======================================================================
echo           TheMutation - Humanizador de Texto con IA (v0.2.0)
echo =======================================================================
echo.

cd /d "%~dp0humanizer-backend"

if exist ".venv\Scripts\python.exe" goto START_SERVER

echo [INFO] Creando entorno virtual de Python (.venv)...
python -m venv .venv
call .\.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -e .[dev]

:START_SERVER
echo [INFO] Entorno virtual activado.
echo.
echo [INFO] Iniciando servidor web FastAPI en http://localhost:8000/ui ...
echo [INFO] Abriendo la interfaz web en su navegador predeterminado...
echo.

start "" "http://localhost:8000/ui"

.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
