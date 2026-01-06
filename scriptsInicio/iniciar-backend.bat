@echo off
echo ========================================
echo   FutbolIA - Iniciar Backend
echo ========================================
echo.

cd futbolia-backend

echo Verificando dependencias...
uv sync

echo.
echo Iniciando servidor backend...
echo API disponible en: http://localhost:8000
echo Documentacion en: http://localhost:8000/docs
echo.

uv run python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

pause

