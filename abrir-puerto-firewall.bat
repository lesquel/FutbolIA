@echo off
echo ========================================
echo   Abrir Puerto 8000 en Firewall Windows
echo   FutbolIA Backend
echo ========================================
echo.
echo Este script requiere permisos de Administrador
echo.
pause

echo.
echo Abriendo puerto 8000 en el firewall...
netsh advfirewall firewall add rule name="FutbolIA Backend" dir=in action=allow protocol=TCP localport=8000

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Puerto 8000 abierto correctamente!
    echo.
    echo Verificando regla creada...
    netsh advfirewall firewall show rule name="FutbolIA Backend"
    echo.
    echo ✅ Listo! El backend ahora deberia ser accesible desde otros dispositivos.
) else (
    echo.
    echo ❌ Error al abrir el puerto. Asegurate de ejecutar como Administrador.
)

echo.
pause

