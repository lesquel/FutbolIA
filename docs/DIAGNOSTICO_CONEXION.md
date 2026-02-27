# 🔍 Diagnóstico: ERR_CONNECTION_TIMED_OUT

## Estado Actual
✅ **Backend está corriendo** - El puerto 8000 está en LISTENING
❌ **Frontend no puede conectarse** - ERR_CONNECTION_TIMED_OUT

## 🔧 Solución Rápida

### Paso 1: Verificar que el Backend Responda

Abre tu navegador y prueba estas URLs:

1. **Desde la misma computadora:**
   ```
   http://localhost:8000/api/v1/health
   http://127.0.0.1:8000/api/v1/health
   ```

2. **Desde la IP local:**
   ```
   http://192.168.90.209:8000/api/v1/health
   ```

**Si `localhost` funciona pero la IP no**, el problema es el **firewall de Windows**.

### Paso 2: Abrir Puerto en Firewall de Windows

Ejecuta estos comandos en **PowerShell como Administrador**:

```powershell
# Permitir puerto 8000 en el firewall
New-NetFirewallRule -DisplayName "FutbolIA Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow

# Verificar que se creó la regla
Get-NetFirewallRule -DisplayName "FutbolIA Backend"
```

**O manualmente:**

1. Abre "Firewall de Windows Defender" (busca en el menú inicio)
2. Click en "Configuración avanzada"
3. Click en "Reglas de entrada" → "Nueva regla"
4. Selecciona "Puerto" → Siguiente
5. TCP → Puerto específico: `8000` → Siguiente
6. "Permitir la conexión" → Siguiente
7. Marca todas las casillas (Dominio, Privada, Pública) → Siguiente
8. Nombre: "FutbolIA Backend" → Finalizar

### Paso 3: Verificar que el Backend Esté Escuchando Correctamente

Asegúrate de que el backend esté iniciado con:

```bash
cd futbolia-backend
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Importante:** Debe decir `--host 0.0.0.0` (no `127.0.0.1` o `localhost`)

### Paso 4: Probar Conexión con curl o PowerShell

**Desde PowerShell:**
```powershell
# Probar desde localhost
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health"

# Probar desde la IP
Invoke-WebRequest -Uri "http://192.168.90.209:8000/api/v1/health"
```

Si el primero funciona pero el segundo no, es definitivamente el firewall.

### Paso 5: Verificar Red

Asegúrate de que:
- ✅ Tu computadora y el dispositivo móvil estén en la **misma red WiFi**
- ✅ La IP `192.168.90.209` sea la correcta (ejecuta `ipconfig` para verificar)
- ✅ No haya un proxy o VPN bloqueando las conexiones

## 🎯 Solución Completa (Script)

Crea un archivo `abrir-puerto-firewall.bat` y ejecútalo como Administrador:

```batch
@echo off
echo Abriendo puerto 8000 en el firewall de Windows...
netsh advfirewall firewall add rule name="FutbolIA Backend" dir=in action=allow protocol=TCP localport=8000
echo.
echo Puerto 8000 abierto correctamente!
echo.
echo Verificando regla...
netsh advfirewall firewall show rule name="FutbolIA Backend"
pause
```

## ✅ Verificación Final

Después de abrir el firewall:

1. **Reinicia el backend** (Ctrl+C y vuelve a iniciarlo)
2. **Prueba desde el navegador:**
   ```
   http://192.168.90.209:8000/api/v1/health
   ```
3. **Deberías ver:**
   ```json
   {
     "status": "healthy",
     "database": "connected",
     "vectorstore": "X players"
   }
   ```
4. **Si funciona**, el frontend debería conectarse correctamente.

## 🆘 Si Aún No Funciona

1. **Verifica la IP actual:**
   ```cmd
   ipconfig
   ```
   Asegúrate de que `192.168.90.209` sea tu IP actual.

2. **Prueba con otra IP:**
   - Si tu IP cambió, actualiza el `.env` del frontend

3. **Verifica que no haya otro firewall:**
   - Antivirus (Windows Defender, Avast, etc.)
   - Router con firewall activo

4. **Prueba desde otro dispositivo:**
   - Abre `http://192.168.90.209:8000/api/v1/health` desde tu móvil en el navegador
   - Si funciona, el problema es en Expo/React Native, no en el backend

