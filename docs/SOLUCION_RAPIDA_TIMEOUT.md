# ⚡ Solución Rápida: ERR_CONNECTION_TIMED_OUT

## 🔴 Problema
Todas las peticiones al backend fallan con `ERR_CONNECTION_TIMED_OUT`:
- `192.168.90.209:8000/api/v1/teams/with-players`
- `192.168.90.209:8000/api/v1/auth/register`
- etc.

## ✅ Solución (2 minutos)

### Paso 1: Abrir Puerto en Firewall

**Opción A: Script Automático (Recomendado)**

1. **Click derecho** en `abrir-puerto-firewall.bat`
2. Selecciona **"Ejecutar como administrador"**
3. Espera a que termine

**Opción B: Manual (PowerShell como Administrador)**

```powershell
New-NetFirewallRule -DisplayName "FutbolIA Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

**Opción C: CMD como Administrador**

```cmd
netsh advfirewall firewall add rule name="FutbolIA Backend" dir=in action=allow protocol=TCP localport=8000
```

### Paso 2: Verificar que Funciona

Abre tu navegador y visita:

```
http://192.168.90.209:8000/api/v1/health
```

**Deberías ver:**
```json
{
  "status": "healthy",
  "database": "connected",
  "vectorstore": "X players"
}
```

### Paso 3: Reiniciar Frontend

Si el backend responde correctamente:

1. **Detén el frontend** (Ctrl+C)
2. **Reinícialo:**
   ```bash
   cd futbolia-mobile
   bun start --clear
   ```

## 🎯 ¿Por qué pasa esto?

- ✅ El backend **SÍ está corriendo** (puerto 8000 en LISTENING)
- ❌ El **firewall de Windows** bloquea conexiones desde otras IPs
- ✅ `localhost` funciona, pero la IP local (`192.168.90.209`) no

**Solución:** Abrir el puerto 8000 en el firewall permite que otros dispositivos se conecten.

## 🔍 Verificación

**Antes de abrir el firewall:**
- ✅ `http://localhost:8000/api/v1/health` → Funciona
- ❌ `http://192.168.90.209:8000/api/v1/health` → ERR_CONNECTION_TIMED_OUT

**Después de abrir el firewall:**
- ✅ `http://localhost:8000/api/v1/health` → Funciona
- ✅ `http://192.168.90.209:8000/api/v1/health` → Funciona ✅

## 📝 Notas

- El script solo necesita ejecutarse **una vez**
- Si cambias de red WiFi, puede que necesites verificar la IP nuevamente
- El puerto permanecerá abierto hasta que lo cierres manualmente

