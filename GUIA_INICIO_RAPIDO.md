# 🚀 Guía de Inicio Rápido - FutbolIA

Guía paso a paso para arrancar el proyecto localmente con todas las mejoras implementadas.

---

## Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.13+** con [uv](https://docs.astral.sh/uv/) (gestor de paquetes)
- **Node.js 18+** (para el frontend)
- **MongoDB** (local o Atlas) - Base de datos para usuarios y predicciones
- **DeepSeek API Key** ([obtener aquí](https://platform.deepseek.com/)) - Para las predicciones con IA (opcional)

> **💡 Explicación detallada:**
> 
> **MongoDB**: Es la base de datos donde se guardan:
> - 👤 **Usuarios**: credenciales, preferencias, historial
> - 🔮 **Predicciones**: todas las predicciones que haces con Dixie
> - **Estadísticas**: precisión de Dixie, equipos favoritos
> 
> Puedes usar MongoDB de dos formas:
> - **Local**: Instalar MongoDB en tu computadora (gratis)
> - **Atlas**: MongoDB en la nube (gratis hasta 512MB) - [MongoDB Atlas](https://www.mongodb.com/atlas)
> 
> **DeepSeek API Key**: Es la clave para usar el modelo de IA "Dixie" que hace las predicciones inteligentes.
> - ✅ **Con API Key**: Predicciones reales y análisis detallados con IA
> - ⚠️ **Sin API Key**: El sistema funciona pero usa respuestas "mock" (simuladas)
> 
> Es **opcional** pero **altamente recomendado** para tener predicciones reales. Puedes obtener una clave gratuita en [platform.deepseek.com](https://platform.deepseek.com/)

---

## 🔧 Configuración del Backend

### 1. Navegar al directorio del backend

```bash
cd futbolia-backend
```

### 2. Instalar dependencias con uv

```bash
# Si no tienes uv instalado:
pip install uv

# IMPORTANTE: No uses "pip install uv sync"
# El comando correcto es "uv sync" (uv es el comando, sync es el subcomando)
# Instalar dependencias del proyecto
uv sync
```

> **⚠️ Error común**: No ejecutes `pip install uv sync`. 
> - ❌ Incorrecto: `pip install uv sync` (intenta instalar un paquete llamado "sync")
> - ✅ Correcto: `pip install uv` (instala uv) y luego `uv sync` (sincroniza dependencias)

### 3. Crear archivo de variables de entorno

Crea un archivo `.env` en `futbolia-backend/` con el siguiente contenido:

```env
# 🔐 SEGURIDAD - OBLIGATORIO CAMBIAR EN PRODUCCIÓN
JWT_SECRET_KEY=tu_clave_secreta_super_segura_aqui_cambiar_en_produccion

# 🤖 IA - Para predicciones reales (obtener en https://platform.deepseek.com/)
DEEPSEEK_API_KEY=tu_api_key_de_deepseek_aqui

# 🗄️ BASE DE DATOS
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=futbolia

# 🌐 SERVIDOR
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# ⚽ APIs DE FÚTBOL (Opcionales - el sistema funciona sin ellas)
# API-Football (api-sports.io) - 100 requests/day gratis
API_FOOTBALL_KEY=tu_api_key_opcional

# Football-Data.org - 10 requests/min gratis
FOOTBALL_DATA_API_KEY=tu_api_key_opcional

# 🌍 CORS (para desarrollo local)
CORS_ORIGINS=http://localhost:3000,http://localhost:8081,http://localhost:19006,exp://localhost:8081,*

# ⏱️ Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

**Nota importante**: 
- Cambia `JWT_SECRET_KEY` por una clave segura (puedes generar una con: `openssl rand -hex 32`)
- Si no tienes `DEEPSEEK_API_KEY`, el sistema funcionará pero usará respuestas mock

### 4. Iniciar MongoDB (si es local)

```bash
# En Windows (si tienes MongoDB instalado como servicio, ya está corriendo)
# Verifica que esté corriendo en: mongodb://localhost:27017

# En Linux/Mac:
# mongod
```

### 5. Iniciar el servidor backend

```bash
# Desde futbolia-backend/
uv run python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en:
- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📱 Configuración del Frontend

### 1. Navegar al directorio del frontend

```bash
# Desde la raíz del proyecto
cd futbolia-mobile
```

### 2. Instalar dependencias

```bash
# Usando npm (o bun si lo prefieres)
npm install

# O con bun:
# bun install
```

**Nota**: La dependencia `lucide-react-native` ya está incluida en `package.json` gracias a las mejoras implementadas.

### 3. Crear archivo de variables de entorno

Crea un archivo `.env` en `futbolia-mobile/` con el siguiente contenido:

```env
# 🌐 URL del Backend API
# IMPORTANTE: Cambia TU_IP_LOCAL por tu IP local (ej: 192.168.1.100)
# Para encontrarla en Windows: ipconfig
# Para encontrarla en Linux/Mac: ifconfig o ip addr
EXPO_PUBLIC_API_URL=http://TU_IP_LOCAL:8000/api/v1

# 🎨 Preferencias (Opcionales)
EXPO_PUBLIC_DEFAULT_LANGUAGE=es
EXPO_PUBLIC_DEFAULT_THEME=dark
```

**Cómo encontrar tu IP local:**

- **Windows**: Abre CMD y ejecuta `ipconfig`, busca "IPv4 Address"
- **Linux/Mac**: Ejecuta `ifconfig` o `ip addr`, busca la IP de tu interfaz de red

**Ejemplo**:
```env
EXPO_PUBLIC_API_URL=http://192.168.1.100:8000/api/v1
```

### 4. Iniciar el servidor de desarrollo

```bash
# Desde futbolia-mobile/
npm start

# O con bun:
# bun start
```

Esto abrirá Expo DevTools. Puedes:
- Presionar `w` para abrir en el navegador web
- Escanear el QR con Expo Go en tu móvil
- Presionar `a` para Android o `i` para iOS (si tienes emuladores)

---

## ✅ Verificación

### Backend

1. Abre http://localhost:8000/health en tu navegador
2. Deberías ver:
```json
{
  "status": "healthy",
  "database": "connected",
  "vectorstore": "X players"
}
```

3. Abre http://localhost:8000/docs para ver la documentación interactiva

### Frontend

1. La app debería cargar sin errores
2. Los iconos de Lucide deberían aparecer correctamente (ya no emojis)
3. Las búsquedas deberían tener debouncing (esperar 500ms antes de buscar)

---

## 🐛 Solución de Problemas

### Backend no inicia

- **Error de MongoDB**: Verifica que MongoDB esté corriendo
  ```bash
  # Verificar conexión
  mongosh mongodb://localhost:27017
  ```

- **Error de dependencias**: Reinstala con `uv sync`

- **Error de puerto ocupado**: Cambia el puerto en `.env` o mata el proceso:
  ```bash
  # Windows
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F
  
  # Linux/Mac
  lsof -ti:8000 | xargs kill
  ```

### Frontend no conecta con Backend

- **Error de CORS**: Verifica que `CORS_ORIGINS` en el backend incluya tu IP
- **Error de conexión**: 
  - Verifica que el backend esté corriendo
  - Verifica que `EXPO_PUBLIC_API_URL` tenga la IP correcta (no `localhost`)
  - Verifica el firewall de Windows

### Iconos no aparecen

- Asegúrate de que `lucide-react-native` esté instalado:
  ```bash
  npm install lucide-react-native
  ```

---

## 🎯 Nuevas Características Implementadas

### ✨ Mejoras de Rendimiento

1. **Sistema de Caché TTL** en el backend:
   - Caché de equipos: 2 horas
   - Caché de plantillas: 30 minutos
   - Caché de predicciones: 5 minutos
   - Reduce llamadas a APIs externas

2. **Optimizaciones React**:
   - `React.memo` en componentes pesados
   - `useMemo` y `useCallback` para evitar re-renders
   - Debouncing en búsquedas (500ms)

### 🎨 Mejoras de UI

1. **Iconos Lucide React Native**:
   - Reemplazo de todos los emojis por iconos profesionales
   - Iconos consistentes en toda la app
   - Mejor accesibilidad

2. **Mejor UX**:
   - Feedback visual mejorado
   - Animaciones suaves
   - Componentes optimizados

---

## 📝 Comandos Útiles

### Backend

```bash
# Iniciar servidor en modo desarrollo
uv run python -m uvicorn src.main:app --reload

# Ver logs detallados
uv run python -m uvicorn src.main:app --reload --log-level debug

# Ejecutar tests (si los hay)
uv run pytest
```

### Frontend

```bash
# Iniciar servidor de desarrollo
npm start

# Limpiar caché y reiniciar
npm start -- --clear

# Build para web
npm run build:web
```

---

## 🔄 Flujo de Trabajo Recomendado

1. **Inicia el backend primero**:
   ```bash
   cd futbolia-backend
   uv run python -m uvicorn src.main:app --reload
   ```

2. **Luego inicia el frontend** (en otra terminal):
   ```bash
   cd futbolia-mobile
   npm start
   ```

3. **Abre la app** en tu dispositivo o navegador

---

## 📚 Recursos Adicionales

- [Documentación Backend](./futbolia-backend/README.md)
- [Documentación Técnica](./futbolia-backend/TECHNICAL_DOCUMENTATION.md)
- [Documentación Frontend](./futbolia-mobile/README.md)

---

## 🆘 ¿Necesitas Ayuda?

Si encuentras problemas:

1. Verifica que todas las dependencias estén instaladas
2. Verifica que MongoDB esté corriendo
3. Verifica que las variables de entorno estén correctas
4. Revisa los logs del backend y frontend para errores específicos

---

¡Listo! 🎉 Tu proyecto debería estar funcionando con todas las mejoras implementadas.

