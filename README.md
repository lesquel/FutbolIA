# ⚽ FutbolIA - Predicciones Deportivas con IA

<div align="center">

![FutbolIA Logo](https://img.shields.io/badge/FutbolIA-🏆-00ff9d?style=for-the-badge)
![Version](https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.13+-yellow?style=for-the-badge&logo=python)
![React Native](https://img.shields.io/badge/React_Native-Expo-61DAFB?style=for-the-badge&logo=react)

**Tu oráculo deportivo impulsado por Inteligencia Artificial**

[🚀 Demo](#-inicio-rápido) • [📖 Documentación](#-documentación) • [🤝 Contribuir](#-contribuir)

</div>

---

## 🎯 ¿Qué es FutbolIA?

FutbolIA es una plataforma de predicciones deportivas que utiliza **Dixie**, una IA analista de élite, para predecir resultados de partidos de fútbol combinando:

- 🧠 **DeepSeek V3** - Modelo de lenguaje avanzado
- **ChromaDB RAG** - Base de datos vectorial con atributos de jugadores tipo FIFA
- ⚽ **Datos en tiempo real** - Integración con APIs de fútbol
- 📱 **App Multiplataforma** - iOS, Android y Web

---

## 📂 Estructura del Monorepo

```
FutbolIA/
├── futbolia-backend/      # 🖥️ API FastAPI + Python
│   ├── src/
│   │   ├── core/          # Configuración
│   │   ├── domain/        # Entidades
│   │   ├── infrastructure/# DB, LLM, APIs
│   │   ├── use_cases/     # Lógica de negocio
│   │   └── presentation/  # Rutas API
│   ├── .env.template      # ⚙️ Variables de entorno
│   └── README.md          # 📖 Documentación backend
│
└── futbolia-mobile/       # 📱 App React Native + Expo
    ├── app/               # Pantallas (Expo Router)
    ├── src/
    │   ├── components/    # UI Components
    │   ├── services/      # API Client
    │   ├── theme/         # Estilos
    │   └── i18n/          # Traducciones
    ├── .env.template      # ⚙️ Variables de entorno
    └── README.md          # 📖 Documentación frontend
```

---

## 🚀 Inicio Rápido

### Prerrequisitos

- **Python 3.13+** con [uv](https://docs.astral.sh/uv/)
- **Node.js 18+** con [Bun](https://bun.sh/)
- **MongoDB** (local o [Atlas](https://www.mongodb.com/atlas))
- **DeepSeek API Key** ([obtener aquí](https://platform.deepseek.com/))

### 1️⃣ Clonar el proyecto

```bash
git clone https://github.com/tu-usuario/futbolia.git
cd FutbolIA
```

### 2️⃣ Configurar Backend

```bash
cd futbolia-backend

# Instalar dependencias
uv sync

# Configurar variables de entorno
cp .env.template .env
# Editar .env con tus valores (especialmente JWT_SECRET_KEY y DEEPSEEK_API_KEY)

# Iniciar servidor
uv run python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 3️⃣ Configurar Frontend

```bash
cd futbolia-mobile

# Instalar dependencias
bun install

# Configurar variables de entorno
cp .env.template .env
# Editar EXPO_PUBLIC_API_URL con tu IP local

# Iniciar app
bun start
```

### 4️⃣ ¡Listo! 🎉

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend Web**: http://localhost:8081
- **Expo Go**: Escanear QR code

---

## ⚙️ Configuración de Variables de Entorno

### Backend (`.env`)

```env
# 🔐 SEGURIDAD - OBLIGATORIO CAMBIAR EN PRODUCCIÓN
JWT_SECRET_KEY=tu_clave_secreta_generada_aqui

# 🤖 IA - Para predicciones reales
DEEPSEEK_API_KEY=tu_api_key_de_deepseek

# 🗄️ BASE DE DATOS
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=futbolia

# 🌐 SERVIDOR
ENVIRONMENT=development
PORT=8000
```

### Frontend (`.env`)

```env
# 🌐 API
EXPO_PUBLIC_API_URL=http://TU_IP_LOCAL:8000/api/v1

# 🎨 PREFERENCIAS
EXPO_PUBLIC_DEFAULT_LANGUAGE=es
EXPO_PUBLIC_DEFAULT_THEME=dark
```

---

## 🔄 Flujo de la Aplicación

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO DE PREDICCIÓN                       │
└─────────────────────────────────────────────────────────────┘

  📱 Usuario                  🖥️ Backend                 🤖 Dixie
      │                           │                         │
      │  1. Selecciona equipos    │                         │
      │─────────────────────────▶│                         │
      │                           │                         │
      │                           │  2. Busca jugadores     │
      │                           │     en ChromaDB (RAG)   │
      │                           │─────────────────────▶  │
      │                           │                         │
      │                           │  3. Genera análisis     │
      │                           │◀─────────────────────  │
      │                           │                         │
      │                           │  4. Guarda en MongoDB   │
      │                           │                         │
      │  5. Muestra predicción    │                         │
      │◀─────────────────────────│                         │
      │                           │                         │
      │  • Ganador: Real Madrid   │                         │
      │  • Marcador: 2-1          │                         │
      │  • Confianza: 75%         │                         │
      │  • Análisis táctico       │                         │
```

---

## 🏗️ Arquitectura Técnica

### Backend - Clean Architecture

```
┌────────────────────────────────────────────┐
│              PRESENTATION                   │
│         (FastAPI Routes)                   │
├────────────────────────────────────────────┤
│               USE CASES                     │
│      (AuthUseCase, PredictionUseCase)      │
├────────────────────────────────────────────┤
│             INFRASTRUCTURE                  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐     │
│  │ MongoDB │ │ChromaDB │ │DeepSeek │     │
│  └─────────┘ └─────────┘ └─────────┘     │
├────────────────────────────────────────────┤
│                 DOMAIN                      │
│    (User, Team, Player, Prediction)        │
└────────────────────────────────────────────┘
```

### Frontend - Component Architecture

```
┌────────────────────────────────────────────┐
│                 SCREENS                     │
│    (Home, Predict, History, Settings)      │
├────────────────────────────────────────────┤
│              COMPONENTS                     │
│  ┌─────────────┐  ┌─────────────────────┐ │
│  │     UI      │  │      Features       │ │
│  │ ThemedView  │  │ PredictionCard     │ │
│  │ Button      │  │ TeamSelector       │ │
│  │ Card        │  │ DixieChat          │ │
│  └─────────────┘  └─────────────────────┘ │
├────────────────────────────────────────────┤
│              SERVICES                       │
│           (API Client)                     │
├────────────────────────────────────────────┤
│            PROVIDERS                        │
│    (Theme, i18n, Navigation)              │
└────────────────────────────────────────────┘
```

---

## 📱 Capturas de Pantalla

| Home                       | Predict                       | History             | Settings                 |
| -------------------------- | ----------------------------- | ------------------- | ------------------------ |
| Home - Partidos destacados | Predict - Selector de equipos | History - Historial | Settings - Configuración |

---

## Tecnologías

### Backend

- **FastAPI** - Framework web moderno y rápido
- **MongoDB + Motor** - Base de datos NoSQL async
- **ChromaDB** - Vector database para RAG
- **DeepSeek** - LLM para análisis (Dixie)
- **JWT** - Autenticación segura
- **Pydantic** - Validación de datos

### Frontend

- **React Native** - Framework para aplicaciones móviles
- **Expo SDK 54** - React Native framework
- **Expo Router** - Navegación basada en archivos
- **NativeWind** - Tailwind CSS para React Native
- **i18next** - Internacionalización
- **AsyncStorage** - Almacenamiento local

---

## 📖 Documentación

- [Backend README](./futbolia-backend/README.md) - Documentación completa del API
- [Frontend README](./futbolia-mobile/README.md) - Documentación de la app
- [API Docs](http://localhost:8000/docs) - Swagger UI (cuando el servidor está corriendo)

---

## 🧪 Testing

```bash
# Backend tests
cd futbolia-backend
uv run pytest

# Frontend tests
cd futbolia-mobile
bun test
```

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: nueva característica'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto fue creado para **Casa Abierta ULEAM 2025** - Minería de Datos - 5to Semestre

---

## 👥 Equipo

<div align="center">

**FutbolIA - Proyecto Dixie**

🏆 _Tu oráculo deportivo de élite_

</div>

uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

