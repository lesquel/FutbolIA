# 🔧 Solución: Error CORS y 401 Unauthorized

## Problema
```
Failed to load resource: the server responded with a status of 401 (Unauthorized)
Access to fetch at 'http://192.168.1.101:8000/api/v1/predictions/matches?league_id=39' 
from origin 'http://localhost:8081' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## ✅ Solución

### Paso 1: Verificar Configuración de CORS en Backend

Asegúrate de que `futbolia-backend/.env` tenga:

```env
CORS_ORIGINS=*
```

O específicamente:

```env
CORS_ORIGINS=http://localhost:8081,http://127.0.0.1:8081,http://localhost:3000,http://localhost:19006,exp://localhost:8081,*
```

### Paso 2: Reiniciar el Backend

**IMPORTANTE:** Después de cambiar CORS, debes reiniciar el backend:

```bash
# Detén el backend (Ctrl+C)
# Luego reinícialo:
cd futbolia-backend
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Paso 3: Verificar que el Endpoint No Requiere Autenticación

El endpoint `/api/v1/predictions/matches` **NO requiere autenticación** (es público).

Si ves 401, puede ser porque:
- El backend está cacheando una respuesta anterior
- Hay un middleware que está bloqueando
- El frontend está enviando un token inválido

**Solución:** Reinicia el backend y limpia la caché del navegador.

### Paso 4: Probar Manualmente

Abre tu navegador y visita:

```
http://192.168.1.101:8000/api/v1/predictions/matches?league_id=39
```

**Deberías ver:**
```json
{
  "success": true,
  "data": {
    "matches": [...]
  }
}
```

**Si ves 401 o CORS error**, el problema está en el backend.

### Paso 5: Verificar Logs del Backend

Cuando hagas una petición, deberías ver en los logs del backend:

```
✅ [INFO] Incoming GET request
   📊 Data: {'path': '/api/v1/predictions/matches', 'client': '192.168.1.101'}
```

Si no ves estos logs, la petición no está llegando al backend (problema de red/firewall).

## 🔍 Diagnóstico

### Verificar CORS en el Backend

El backend ahora incluye `http://localhost:8081` por defecto. Si aún tienes problemas:

1. **Verifica que el backend esté usando la configuración correcta:**
   - Debe decir en los logs: `CORS configuration` con los orígenes permitidos

2. **Prueba con curl o Postman:**
   ```bash
   curl -H "Origin: http://localhost:8081" \
        -H "Access-Control-Request-Method: GET" \
        -X OPTIONS \
        http://192.168.1.101:8000/api/v1/predictions/matches
   ```

3. **Verifica que no haya otro servidor corriendo en el puerto 8000**

## ✅ Cambios Realizados

1. ✅ Mejorada configuración de CORS para incluir `http://localhost:8081`
2. ✅ Agregado logging de CORS para debugging
3. ✅ Mejorado manejo de headers CORS
4. ✅ Verificado que `/predictions/matches` no requiere autenticación

## 🎯 Próximos Pasos

1. **Reinicia el backend** con los cambios
2. **Limpia la caché del navegador** (Ctrl+Shift+R)
3. **Prueba nuevamente** desde el frontend

Si aún tienes problemas, verifica:
- Que el backend esté corriendo
- Que la IP sea correcta (`192.168.1.101`)
- Que no haya firewall bloqueando

