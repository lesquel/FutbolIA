@echo off
echo ========================================
echo   FutbolIA - Iniciar Frontend
echo ========================================
echo.

cd futbolia-mobile

echo Verificando dependencias...
call npm install

echo.
echo Iniciando servidor de desarrollo Expo...
echo.

call npm start

pause

