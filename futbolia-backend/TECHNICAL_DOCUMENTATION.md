# 🏆 FutbolIA - Documentación Técnica Detallada

## 📌 Descripción General

FutbolIA es una plataforma avanzada de predicción de fútbol que utiliza Inteligencia Artificial (IA) y Recuperación Aumentada por Generación (RAG) para proporcionar análisis tácticos y predicciones precisas. El sistema combina datos estadísticos en tiempo real con atributos detallados de jugadores para alimentar a "Dixie", un modelo de lenguaje especializado en análisis deportivo.

---

## 🏗️ Arquitectura del Sistema

El proyecto sigue los principios de **Clean Architecture**, separando las responsabilidades en capas bien definidas para facilitar el mantenimiento y la escalabilidad.

### 1. Capa de Dominio (`src/domain`)

- **Entidades**: Define los objetos de negocio principales como `Team`, `Player`, `Prediction` y `User`.
- **Reglas de Negocio**: Lógica pura que no depende de marcos externos.

### 2. Capa de Casos de Uso (`src/use_cases`)

- **Predicción**: Orquestación del flujo de RAG (búsqueda en ChromaDB + consulta a DeepSeek).
- **Autenticación**: Gestión de registro, login y validación de JWT.
- **Gestión de Equipos**: Lógica para crear y buscar equipos.

### 3. Capa de Infraestructura (`src/infrastructure`)

- **Base de Datos (MongoDB)**: Almacenamiento persistente de usuarios, equipos creados por usuarios e historial de predicciones.
- **Base de Datos Vectorial (ChromaDB)**: Almacenamiento de embeddings de atributos de jugadores (FIFA/FC24 stats) para búsqueda semántica y RAG.
- **LLM (DeepSeek/Dixie)**: Integración con la API de DeepSeek para la generación de análisis en lenguaje natural.
- **APIs Externas**: Cliente para `API-Football` (Football-Data.org) para obtener resultados y alineaciones reales.

### 4. Capa de Presentación (`src/presentation`)

- **FastAPI**: Definición de rutas RESTful, validación de esquemas con Pydantic y documentación automática con Swagger.

---

## 🧠 Implementación de RAG con ChromaDB

Una de las características más potentes de FutbolIA es su sistema de **Generación Aumentada por Recuperación (RAG)**.

### ¿Cómo funciona?

1. **Almacenamiento**: Los atributos de miles de jugadores (ritmo, tiro, pase, defensa, etc.) se vectorizan y almacenan en ChromaDB.
2. **Recuperación**: Cuando se solicita una predicción entre el Equipo A y el Equipo B, el sistema busca en ChromaDB los perfiles de los jugadores de ambos equipos.
3. **Contexto**: Estos perfiles se inyectan en el "Prompt" enviado a la IA.
4. **Generación**: Dixie no solo "adivina", sino que analiza: _"El Equipo A tiene una ventaja en velocidad por las bandas (Pace medio 88) frente a la defensa lenta del Equipo B (Pace medio 72)"_.

### Mejoras de Precisión

- Se implementó una búsqueda de **coincidencia exacta** para evitar que jugadores de selecciones nacionales o equipos con nombres similares se mezclen.
- Se añadió persistencia para que los jugadores generados por IA se guarden automáticamente en ChromaDB, mejorando la base de conocimientos con cada consulta.

---

## 🤖 Dixie AI: El Oráculo Deportivo

Dixie es la personalidad de IA diseñada para FutbolIA.

- **Modelo**: DeepSeek-Chat (optimizado para razonamiento lógico).
- **Capacidades**:
  - Análisis de forma reciente (últimos 5 partidos).
  - Comparación línea por línea (Portería, Defensa, Medio, Ataque).
  - Factor de localía y presión psicológica.
  - Generación de marcadores probables con porcentaje de confianza.

---

## 📊 Sistema de Estadísticas y Dixie Stats

Se implementó un sistema de seguimiento para medir la efectividad de la IA:

- **Registro de Predicciones**: Cada predicción se guarda con su nivel de confianza.
- **Validación de Resultados**: (En desarrollo) Un worker que compara las predicciones con resultados reales para calcular el % de acierto.
- **Leaderboard**: Identifica qué equipos son más "predecibles" o exitosos bajo el análisis de Dixie.

---

## 🛡️ Seguridad y Rendimiento

### 1. Rate Limiting

Para proteger la API y controlar los costos de LLM, se implementó un middleware de **Sliding Window**:

- **General**: 60 peticiones por minuto.
- **Predicciones**: 10 peticiones por minuto por usuario.
- **Generación de Jugadores**: 5 peticiones por minuto.

### 2. Logging Estructurado

Sistema de logs profesional que diferencia entre entornos:

- **Desarrollo**: Logs coloridos y legibles.
- **Producción**: Logs en formato JSON para integración con sistemas de monitoreo (ELK Stack, Datadog).
- **Eventos Especiales**: Logs específicos para cada predicción generada, incluyendo equipos y confianza.

---

## 📱 Frontend y Modo Offline

La aplicación móvil (React Native/Expo) incluye una robusta gestión de estado offline:

- **Caché de Predicciones**: Las últimas 50 predicciones se guardan localmente en `AsyncStorage`.
- **Favoritos**: Los usuarios pueden marcar equipos para acceso rápido sin conexión.
- **Cola de Peticiones**: Si el usuario intenta predecir sin internet, la petición se encola para procesarse automáticamente al recuperar la conexión.

---

## 🐳 Infraestructura y Despliegue

El sistema está completamente contenedorizado:

- **Dockerfile**: Optimizado usando `uv` como gestor de paquetes (reduce el tiempo de build en un 80%).
- **Docker Compose**: Orquestación de la API y la base de datos MongoDB con volúmenes persistentes para ChromaDB.
- **Health Checks**: Monitoreo automático del estado del servicio.

---

## 🛠️ Organización de Archivos (Backend)

```text
src/
├── core/               # Configuración, Logger, Rate Limit
│   ├── config.py       # Variables de entorno y ajustes globales
│   ├── logger.py       # Sistema de logs estructurados (JSON/Color)
│   └── rate_limit.py   # Middleware de protección de API
├── domain/             # Entidades y modelos base
│   └── entities.py     # Definición de Team, Player, Prediction
├── infrastructure/     # Implementaciones externas
│   ├── db/             # MongoDB y Repositorios
│   │   ├── mongodb.py  # Conexión asíncrona con Motor
│   │   └── dixie_stats.py # Seguimiento de precisión de IA
│   ├── chromadb/       # Almacenamiento vectorial y RAG
│   │   ├── player_store.py # Lógica de búsqueda semántica
│   │   └── seed_data.py # Datos iniciales de jugadores top
│   ├── llm/            # Integración con Dixie (DeepSeek)
│   │   └── dixie.py    # Lógica de prompts y conexión con API
│   └── external_api/   # Clientes de APIs de fútbol
├── use_cases/          # Lógica de aplicación
│   ├── prediction.py   # Flujo principal de predicción
│   └── auth.py         # Lógica de tokens y usuarios
└── presentation/       # Rutas FastAPI y Esquemas
    ├── auth_routes.py  # Endpoints de seguridad
    ├── prediction_routes.py # Endpoints de predicción
    └── stats_routes.py # Endpoints de estadísticas y fuzzy search
```

---

## ⚙️ Infraestructura y Despliegue

### Dockerización Avanzada

- **Multi-stage Build**: Se utiliza una etapa de `builder` para instalar dependencias y una de `production` para ejecutar, resultando en una imagen ligera y segura.
- **Gestor UV**: Reemplaza a `pip` para instalaciones ultra-rápidas y gestión de entornos virtuales deterministas.
- **Seguridad**: La aplicación corre bajo un usuario no-root (`appuser`) para minimizar riesgos de seguridad.

### Persistencia de Datos

- **Volúmenes Docker**: Los datos de ChromaDB y MongoDB se almacenan en volúmenes persistentes (`futbolia-mongodb-data`, `futbolia-chromadb-data`), asegurando que la información no se pierda al reiniciar contenedores.

---

## 🔍 Detalles de Implementación Específicos

### Búsqueda Difusa (Fuzzy Search)

El sistema utiliza la librería `difflib` para calcular el ratio de similitud entre la entrada del usuario y una base de datos de más de 50 alias de equipos. Esto permite que si un usuario escribe "Real Madri", el sistema sugiera automáticamente "Real Madrid".

### Categorización de Equipos

Se ha mapeado manualmente una lista de equipos top a sus respectivas ligas y países, permitiendo que Dixie tenga contexto geográfico y de competición (e.g., saber que el Bayern Munich juega en la Bundesliga).

### Gestión de Memoria en ChromaDB

Para evitar el crecimiento desmedido, el sistema de seeding verifica la existencia de jugadores antes de insertarlos, y las búsquedas están limitadas por `n_results` para optimizar el tiempo de respuesta del LLM.

---

## 📝 Notas de Versión (v1.0.0)

- Implementación completa de RAG.
- Sistema de búsqueda difusa (Fuzzy Search) para nombres de equipos.
- Categorización de equipos por ligas y países.
- Soporte multiidioma (ES/EN).
- Persistencia de datos en MongoDB y ChromaDB.
