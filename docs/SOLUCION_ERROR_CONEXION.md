# 🔧 Solución: Error de Conexión con el Backend

## Problema
```
Error de conexión: Failed to fetch. Verifique que el servidor en http://192.168.90.209:8000/api/v1 sea accesible.
```

## 🔍 Diagnóstico Paso a Paso

### 1. Verificar que el Backend esté Corriendo

Abre una terminal y ejecuta:

```bash
# Navegar al backend
cd futbolia-backend

# Verificar que el servidor esté corriendo
# Deberías ver algo como: "Uvicorn running on http://0.0.0.0:8000"
```

Si no está corriendo, inícialo:

```bash
# Desde futbolia-backend/
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Verificar la IP Local Correcta

El frontend está configurado para usar `192.168.90.209`. Verifica que esta sea tu IP actual:

**Windows:**
```cmd
ipconfig
# Busca "IPv4 Address" en "Ethernet adapter" o "Wireless LAN adapter"
```

**Mac/Linux:**
```bash
ifconfig | grep "inet "
# O
ip addr show | grep "inet "
```

**Si tu IP es diferente**, actualiza la configuración del frontend.

### 3. Configurar la URL del API en el Frontend

#### Opción A: Usando archivo `.env` (Recomendado)

1. Crea un archivo `.env` en `futbolia-mobile/`:

```env
EXPO_PUBLIC_API_URL=http://TU_IP_LOCAL:8000/api/v1
```

**Ejemplo si tu IP es `192.168.1.100`:**
```env
EXPO_PUBLIC_API_URL=http://192.168.1.100:8000/api/v1
```

2. Reinicia Expo:
```bash
# Detén el servidor (Ctrl+C) y reinicia
cd futbolia-mobile
bun start --clear
```

#### Opción B: Modificar directamente `api.ts`

Edita `futbolia-mobile/src/services/api.ts`:

```typescript
const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL || "http://TU_IP_LOCAL:8000/api/v1";
```

Reemplaza `TU_IP_LOCAL` con tu IP real.

### 4. Verificar CORS en el Backend

El backend debe permitir conexiones desde tu IP. Edita `futbolia-backend/.env`:

```env
# Agrega tu IP local a CORS_ORIGINS
CORS_ORIGINS=http://localhost:3000,http://localhost:8081,http://localhost:19006,exp://localhost:8081,http://192.168.90.209:8081,*
```

O simplemente usa `*` para desarrollo (permite todas las conexiones):

```env
CORS_ORIGINS=*
```

**Reinicia el backend** después de cambiar CORS.

### 5. Verificar Firewall ⚠️ **MUY IMPORTANTE**

El error `ERR_CONNECTION_TIMED_OUT` generalmente es causado por el **firewall de Windows bloqueando el puerto 8000**.

**Solución rápida (PowerShell como Administrador):**
```powershell
# Abrir puerto 8000 en el firewall
New-NetFirewallRule -DisplayName "FutbolIA Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

**O con CMD (como Administrador):**
```cmd
netsh advfirewall firewall add rule name="FutbolIA Backend" dir=in action=allow protocol=TCP localport=8000
```

**Verificar que se creó:**
```powershell
Get-NetFirewallRule -DisplayName "FutbolIA Backend"
```

**Si el backend responde en `localhost` pero no en la IP local, es definitivamente el firewall.**

**Mac:**
```bash
# Verificar si el puerto está abierto
lsof -i :8000
```

**Linux:**
```bash
# Verificar firewall
sudo ufw status
# Si está activo, permitir puerto 8000
sudo ufw allow 8000
```

### 6. Probar la Conexión Manualmente

Abre tu navegador y visita:

```
http://192.168.90.209:8000/api/v1/health
```

O:

```
http://localhost:8000/api/v1/health
```

Deberías ver una respuesta JSON. Si no funciona, el backend no está accesible.

### 7. Si usas Expo Go en el Móvil

Si estás probando en un dispositivo móvil físico con Expo Go:

1. **Asegúrate de que el móvil y la computadora estén en la misma red WiFi**
2. **Usa la IP de tu computadora** (no `localhost` o `127.0.0.1`)
3. **Verifica que el backend esté escuchando en `0.0.0.0`** (no solo `localhost`)

En `futbolia-backend/.env`:
```env
HOST=0.0.0.0  # Esto permite conexiones desde cualquier IP de la red
PORT=8000
```

## ✅ Solución Rápida (Resumen)

1. **Inicia el backend:**
   ```bash
   cd futbolia-backend
   uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Obtén tu IP local:**
   ```bash
   # Windows
   ipconfig
   
   # Mac/Linux
   ifconfig | grep "inet "
   ```

3. **Crea `.env` en `futbolia-mobile/`:**
   ```env
   EXPO_PUBLIC_API_URL=http://TU_IP:8000/api/v1
   ```

4. **Actualiza CORS en `futbolia-backend/.env`:**
   ```env
   CORS_ORIGINS=*
   ```

5. **Reinicia ambos servidores**

## 🆘 Si Aún No Funciona

1. **Verifica que ambos estén en la misma red WiFi**
2. **Prueba con `localhost` si estás en emulador/simulador:**
   ```env
   EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1
   ```
3. **Revisa los logs del backend** para ver errores
4. **Prueba con curl o Postman** para verificar que el backend responde

## 📝 Notas Importantes

- **Para desarrollo local**: Usa tu IP local (ej: `192.168.1.100`)
- **Para emulador Android**: Usa `10.0.2.2` en lugar de `localhost`
- **Para simulador iOS**: Usa `localhost` o `127.0.0.1`
- **Para dispositivo físico**: Usa la IP de tu computadora en la red local

