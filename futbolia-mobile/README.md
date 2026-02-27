# 📱 FutPredicIA Mobile - React Native App

Aplicación móvil multiplataforma para FutPredicIA, construida con Expo y React Native.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Flujo de la Aplicación](#-flujo-de-la-aplicación)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Ejecución](#-ejecución)
- [Estructura del Proyecto](#-estructura-del-proyecto)

---

## ✨ Características

- 🎨 **Tema Oscuro/Claro** - Diseño moderno con verde neón y azul profundo
- 🌍 **Multiidioma** - Español e Inglés
- 📱 **Multiplataforma** - iOS, Android y Web
- 🔮 **Predicciones IA** - Integración con Dixie AI
- 📊 **Historial** - Registro de todas tus predicciones
- 🏆 **Diseño Responsivo** - Adaptado a móvil y tablet
- 📶 **Modo Offline** - Acceso a favoritos y caché de predicciones sin internet

---

## 🔄 Flujo de la Aplicación

### Diagrama de Pantallas

```
┌─────────────────────────────────────────────────────────────┐
│                    APP NAVIGATION FLOW                       │
└─────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │   App Start     │
                    │   _layout.tsx   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              │              ▼
    ┌─────────────────┐     │    ┌─────────────────┐
    │  ThemeProvider  │     │    │    i18n Init    │
    │ (Dark/Light)    │     │    │   (ES/EN)       │
    └────────┬────────┘     │    └────────┬────────┘
             │              │             │
             └──────────────┼─────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Tab Layout  │
                    │ (tabs)/_layout│
                    └───────┬───────┘
                            │
        ┌───────────┬───────┼───────┬───────────┐
        │           │       │       │           │
        ▼           ▼       ▼       ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
   │  🏠     │ │  🔮     │ │  📊     │ │  ⚙️     │
   │  Home   │ │ Predict │ │ History │ │Settings │
   │ index   │ │ predict │ │ history │ │settings │
   └─────────┘ └─────────┘ └─────────┘ └─────────┘
```

### Flujo de Usuario Principal

```
┌─────────────────────────────────────────────────────────────┐
│                   USER JOURNEY FLOW                          │
└─────────────────────────────────────────────────────────────┘

    Usuario abre la app
           │
           ▼
    ┌─────────────────┐
    │   HOME SCREEN   │
    │ ────────────────│
    │ • Ver partidos  │
    │   destacados    │
    │ • Saludo Dixie  │
    │ • Quick actions │
    └────────┬────────┘
             │
             │ Tap "Predecir"
             ▼
    ┌─────────────────┐
    │ PREDICT SCREEN  │
    │ ────────────────│
    │ 1. Seleccionar  │
    │    equipo local │──────┐
    │                 │      │
    │ 2. Seleccionar  │      │ Modal TeamSelector
    │    equipo visit.│◀─────┘
    │                 │
    │ 3. Tap "Predecir│
    │    con Dixie"   │
    └────────┬────────┘
             │
             │ Loading animation
             ▼
    ┌─────────────────┐
    │   API CALL      │
    │ ────────────────│
    │ POST /predict   │
    │ {home, away}    │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ PREDICTION CARD │
    │ ────────────────│
    │ • Ganador       │
    │ • Marcador      │
    │ • Confianza %   │
    │ • Análisis      │
    │ • Key factors   │
    │                 │
    │ [Guardar]       │
    │ [Nueva predic.] │
    └────────┬────────┘
             │
             │ Tap "Ver historial"
             ▼
    ┌─────────────────┐
    │ HISTORY SCREEN  │
    │ ────────────────│
    │ • Lista de      │
    │   predicciones  │
    │ • Estadísticas  │
    │ • Filtros       │
    └─────────────────┘
```

### Flujo de Datos

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA FLOW                                │
└─────────────────────────────────────────────────────────────┘

  ┌───────────────────────────────────────────────────────┐
  │                    REACT NATIVE APP                    │
  │  ┌─────────────────────────────────────────────────┐  │
  │  │                   SCREENS                        │  │
  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐           │  │
  │  │  │  Home   │ │ Predict │ │ History │           │  │
  │  │  └────┬────┘ └────┬────┘ └────┬────┘           │  │
  │  └───────┼───────────┼───────────┼─────────────────┘  │
  │          │           │           │                     │
  │          └───────────┼───────────┘                     │
  │                      │                                 │
  │                      ▼                                 │
  │  ┌─────────────────────────────────────────────────┐  │
  │  │              API SERVICE                         │  │
  │  │         (src/services/api.ts)                   │  │
  │  │  ┌─────────────┐  ┌─────────────────────────┐  │  │
  │  │  │ authApi     │  │ predictionsApi          │  │  │
  │  │  │ • login()   │  │ • predict()             │  │  │
  │  │  │ • register()│  │ • getHistory()          │  │  │
  │  │  │ • getMe()   │  │ • getMatches()          │  │  │
  │  │  └─────────────┘  └─────────────────────────┘  │  │
  │  └────────────────────────┬────────────────────────┘  │
  │                           │                           │
  │  ┌────────────────────────┼────────────────────────┐  │
  │  │         LOCAL STORAGE (AsyncStorage)            │  │
  │  │  • JWT Token                                    │  │
  │  │  • Theme preference                             │  │
  │  │  • Language preference                          │  │
  │  └─────────────────────────────────────────────────┘  │
  └───────────────────────────┬───────────────────────────┘
                              │
                              │ HTTP/HTTPS
                              ▼
                    ┌─────────────────┐
                    │  BACKEND API    │
                    │  localhost:8000 │
                    └─────────────────┘
```

---

## 🚀 Instalación

### Prerrequisitos

- Node.js 18+ o Bun
- Expo CLI
- iOS Simulator (Mac) o Android Emulator

### Pasos

```bash
# 1. Navegar al directorio
cd futbolia-mobile

# 2. Instalar dependencias
bun install

# 3. Copiar configuración
cp .env.template .env

# 4. Editar .env con la URL del backend
# EXPO_PUBLIC_API_URL=http://TU_IP_LOCAL:8000/api/v1
```

---

## ⚙️ Configuración

### Variables de Entorno

| Variable                       | Descripción        | Ejemplo                            |
| ------------------------------ | ------------------ | ---------------------------------- |
| `EXPO_PUBLIC_API_URL`          | URL del backend    | `http://192.168.1.100:8000/api/v1` |
| `EXPO_PUBLIC_DEFAULT_LANGUAGE` | Idioma por defecto | `es`                               |
| `EXPO_PUBLIC_DEFAULT_THEME`    | Tema por defecto   | `dark`                             |

### Encontrar tu IP Local

```bash
# Windows
ipconfig

# Mac/Linux
ifconfig | grep "inet "

# Usar esa IP en EXPO_PUBLIC_API_URL
# Ejemplo: http://192.168.1.100:8000/api/v1
```

---

## ▶️ Ejecución

### Desarrollo

```bash
# Iniciar Expo
bun start

# Opciones disponibles:
# - Presiona 'w' para abrir en Web
# - Presiona 'a' para abrir en Android
# - Presiona 'i' para abrir en iOS
# - Escanea el QR con Expo Go (móvil)
```

### Limpiar caché

```bash
bunx expo start --clear
```

### Build de producción

```bash
# Build para todas las plataformas
bunx expo build

# Build específico
eas build --platform android
eas build --platform ios
```

---

## 📁 Estructura del Proyecto

```
futbolia-mobile/
├── app/                       # Rutas (Expo Router)
│   ├── _layout.tsx           # Layout principal
│   ├── modal.tsx             # Modal de información
│   ├── +html.tsx             # HTML wrapper (web)
│   ├── +not-found.tsx        # Página 404
│   └── (tabs)/               # Tab navigation
│       ├── _layout.tsx       # Layout de tabs
│       ├── index.tsx         # 🏠 Home
│       ├── predict.tsx       # 🔮 Predict
│       ├── history.tsx       # 📊 History
│       └── settings.tsx      # ⚙️ Settings
│
├── src/
│   ├── components/
│   │   ├── ui/               # Componentes base
│   │   │   ├── ThemedView.tsx
│   │   │   ├── ThemedText.tsx
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── ConfidenceRing.tsx
│   │   │   └── TeamBadge.tsx
│   │   │
│   │   └── features/         # Componentes de negocio
│   │       ├── MatchCard.tsx
│   │       ├── PredictionCard.tsx
│   │       ├── TeamSelector.tsx
│   │       └── DixieChat.tsx
│   │
│   ├── services/
│   │   └── api.ts            # Cliente API
│   │
│   ├── theme/
│   │   ├── colors.ts         # Paleta de colores
│   │   └── ThemeContext.tsx  # Context de tema
│   │
│   └── i18n/
│       ├── i18n.ts           # Configuración i18n
│       └── locales/
│           ├── es.json       # Español
│           └── en.json       # English
│
├── assets/
│   ├── fonts/
│   └── images/
│
├── .env.template             # Template de variables
├── app.json                  # Configuración Expo
├── babel.config.js           # Babel config
├── metro.config.js           # Metro bundler
├── tailwind.config.js        # Tailwind/NativeWind
├── tsconfig.json             # TypeScript config
└── package.json              # Dependencias
```

---

## 🎨 Sistema de Diseño

### Colores

```typescript
// Tema Oscuro (default)
{
  primary: '#00ff9d',      // Verde neón
  background: '#0a0f0d',   // Negro verdoso
  surface: '#141a17',      // Gris oscuro
  text: '#ffffff',         // Blanco
  textSecondary: '#9ca3af' // Gris
}

// Tema Claro
{
  primary: '#00cc7e',      // Verde
  background: '#f8faf9',   // Casi blanco
  surface: '#ffffff',      // Blanco
  text: '#1f2937',         // Casi negro
  textSecondary: '#6b7280' // Gris
}
```

### Componentes UI

| Componente       | Descripción                                       |
| ---------------- | ------------------------------------------------- |
| `ThemedView`     | View con colores del tema                         |
| `ThemedText`     | Text con tipografía del tema                      |
| `Button`         | Botón con variantes (primary, secondary, outline) |
| `Card`           | Tarjeta contenedora                               |
| `Input`          | Campo de texto estilizado                         |
| `ConfidenceRing` | Círculo de porcentaje SVG                         |
| `TeamBadge`      | Badge de equipo con logo                          |

---

## 🌍 Internacionalización

### Idiomas Soportados

- 🇪🇸 Español (es) - Default
- 🇺🇸 English (en)

### Agregar traducciones

```typescript
// src/i18n/locales/es.json
{
  "home": {
    "title": "Bienvenido a FutbolIA",
    "subtitle": "Tu oráculo deportivo"
  }
}

// Uso en componentes
const { t } = useTranslation();
<Text>{t('home.title')}</Text>
```

---

## 🔒 Seguridad

### Implementada

- ✅ Token JWT almacenado en AsyncStorage
- ✅ Headers de autorización automáticos
- ✅ Validación de respuestas API
- ✅ Manejo de errores de red

### Recomendaciones

1. **No almacenar datos sensibles** en el código
2. **Usar HTTPS** en producción
3. **Validar inputs** del usuario
4. **Manejar expiración** de tokens

---

## 🧪 Testing

```bash
# Ejecutar tests
bun test
```

---

## 📝 Licencia

Casa Abierta ULEAM 2025 - Minería de Datos - 5to Semestre

---

## 👥 Autores

- Proyecto FutbolIA - Dixie AI
