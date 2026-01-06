@echo off
echo ========================================
echo   FutbolIA - Configuracion Inicial
echo ========================================
echo.

echo Este script te ayudara a configurar el proyecto...
echo.

REM Verificar Python
echo [1/4] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado
    echo Instala Python 3.13+ desde https://www.python.org/
    pause
    exit /b 1
)

REM Verificar uv
echo [2/4] Verificando uv...
uv --version
if %errorlevel% neq 0 (
    echo uv no encontrado. Instalando...
    pip install uv
)

REM Verificar Node.js
echo [3/4] Verificando Node.js...
node --version
if %errorlevel% neq 0 (
    echo ERROR: Node.js no esta instalado
    echo Instala Node.js 18+ desde https://nodejs.org/
    pause
    exit /b 1
)

REM Verificar MongoDB
echo [4/4] Verificando MongoDB...
mongosh --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ADVERTENCIA: MongoDB no encontrado en PATH
    echo Asegurate de tener MongoDB instalado y corriendo
    echo O usa MongoDB Atlas (cloud)
)

echo.
echo ========================================
echo   Configuracion de Variables de Entorno
echo ========================================
echo.

REM Backend .env
if not exist "futbolia-backend\.env" (
    echo Creando futbolia-backend\.env...
    (
        echo # JWT Secret Key - CAMBIAR EN PRODUCCION
        echo JWT_SECRET_KEY=clave-secreta-cambiar-en-produccion
        echo.
        echo # DeepSeek API Key - Obtener en https://platform.deepseek.com/
        echo DEEPSEEK_API_KEY=
        echo.
        echo # MongoDB
        echo MONGODB_URI=mongodb://localhost:27017
        echo MONGODB_DATABASE=futbolia
        echo.
        echo # Servidor
        echo ENVIRONMENT=development
        echo HOST=0.0.0.0
        echo PORT=8000
        echo.
        echo # CORS
        echo CORS_ORIGINS=http://localhost:3000,http://localhost:8081,http://localhost:19006,exp://localhost:8081,*
    ) > futbolia-backend\.env
    echo ✓ Archivo .env del backend creado
    echo   IMPORTANTE: Edita futbolia-backend\.env y agrega tus API keys
) else (
    echo ✓ futbolia-backend\.env ya existe
)

REM Frontend .env
if not exist "futbolia-mobile\.env" (
    echo.
    echo Creando futbolia-mobile\.env...
    
    REM Obtener IP local
    for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
        set LOCAL_IP=%%a
        set LOCAL_IP=!LOCAL_IP: =!
        goto :found_ip
    )
    :found_ip
    
    (
        echo # URL del Backend API
        echo EXPO_PUBLIC_API_URL=http://%LOCAL_IP%:8000/api/v1
        echo.
        echo # Preferencias
        echo EXPO_PUBLIC_DEFAULT_LANGUAGE=es
        echo EXPO_PUBLIC_DEFAULT_THEME=dark
    ) > futbolia-mobile\.env
    echo ✓ Archivo .env del frontend creado con IP: %LOCAL_IP%
    echo   Si la IP es incorrecta, edita futbolia-mobile\.env
) else (
    echo ✓ futbolia-mobile\.env ya existe
)

echo.
echo ========================================
echo   Instalando Dependencias
echo ========================================
echo.

REM Backend
echo [Backend] Instalando dependencias Python...
cd futbolia-backend
uv sync
cd ..

REM Frontend
echo [Frontend] Instalando dependencias Node.js...
cd futbolia-mobile
call npm install
cd ..

echo.
echo ========================================
echo   Configuracion Completada!
echo ========================================
echo.
echo Siguientes pasos:
echo 1. Edita futbolia-backend\.env y agrega:
echo    - JWT_SECRET_KEY (genera una clave segura)
echo    - DEEPSEEK_API_KEY (opcional pero recomendado)
echo.
echo 2. Asegurate de que MongoDB este corriendo
echo.
echo 3. Inicia el backend con: iniciar-backend.bat
echo.
echo 4. Inicia el frontend con: iniciar-frontend.bat
echo.
pause

