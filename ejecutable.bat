@echo off
chcp 65001 > nul
title TheMutation - Humanizador de Texto IA

echo =======================================================================
echo          🧬 TheMutation — Humanizador de Texto con IA (v0.2.0)
echo =======================================================================
echo.

cd /d "%~dp0humanizer-backend"

IF NOT EXIST ".venv" (
    echo [INFO] Creando entorno virtual de Python (.venv)...
    python -m venv .venv
    echo [INFO] Instalando dependencias del proyecto...
    call .venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install -e ".[dev]"
) ELSE (
    echo [INFO] Entorno virtual (.venv) detectado.
    call .venv\Scripts\activate.bat
)

echo.
echo [INFO] Iniciando servidor web FastAPI en http://localhost:8000/ui ...
echo [INFO] Abriendo la interfaz web en su navegador predeterminado...
echo.

timeout /t 2 /nobreak > nul
start http://localhost:8000/ui

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
