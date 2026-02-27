# 📊 Flujo de Datos: Equipos y Ligas

## 🔄 Resumen del Flujo Actual

La aplicación obtiene información de equipos con sus ligas a través de múltiples fuentes con un sistema de fallback inteligente.

## 1️⃣ Frontend (React Native)

### Endpoints Utilizados

```typescript
// Obtener equipos con jugadores
teamsApi.getTeamsWithPlayers()
// GET /api/v1/teams/with-players

// Buscar equipos
teamsApi.search(query, searchApi=true, limit=20)
// GET /api/v1/teams/search?q={query}&search_api=true&limit=20
```

### Estructura de Datos Recibida

```typescript
interface TeamSearchResult {
  id: string;
  name: string;
  short_name: string;
  logo_url: string;
  country: string;
  league: string;        // ⚠️ Actualmente puede estar vacío
  has_players: boolean;
  player_count: number;
  source?: string;       // "mongodb" | "chromadb" | "external_api"
}
```

## 2️⃣ Backend (FastAPI)

### Endpoint: `/teams/search`

**Flujo de búsqueda:**

1. **Base de Datos Local (MongoDB)**
   - Busca equipos guardados por usuarios
   - Incluye: `name`, `league`, `country`, `logo_url`

2. **ChromaDB (Equipos con Jugadores)**
   - Busca en equipos principales europeos
   - Lista hardcodeada: Real Madrid, Manchester City, Barcelona, etc.
   - ⚠️ **Problema**: No extrae la liga de ChromaDB

3. **APIs Externas (UnifiedAPIClient)**
   - Usa sistema de fallback con 3 APIs:
     - **TheSportsDB** (primero, gratis, 100k req/día)
     - **Football-Data.org** (segundo, gratis, 10 req/min)
     - **API-Football** (tercero, 100 req/día gratis)

### Endpoint: `/teams/with-players`

**Flujo:**

1. **Cache (5 minutos)**
   - Verifica si hay datos en caché
   - Si existe, retorna inmediatamente

2. **MongoDB**
   - Obtiene equipos que tienen `player_count > 0`
   - Incluye: `league`, `country`, `logo_url`

3. **ChromaDB (Fallback)**
   - Solo si hay menos de 10 equipos en MongoDB
   - Busca en equipos principales
   - ⚠️ **Problema**: No extrae la liga

## 3️⃣ APIs Externas

### TheSportsDB (Prioridad 1)

**Endpoint usado:**
```
GET https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={team_name}
```

**Respuesta típica:**
```json
{
  "teams": [{
    "idTeam": "133602",
    "strTeam": "Real Madrid",
    "strTeamShort": "RMA",
    "strTeamBadge": "https://...",
    "strCountry": "Spain",
    "strStadium": "Santiago Bernabéu",
    "strLeague": "La Liga",           // ✅ Información de liga disponible
    "strLeague2": "UEFA Champions League",
    "strLeague3": "..."
  }]
}
```

**⚠️ Problema actual:**
- El código en `api_selector.py` NO extrae `strLeague` de TheSportsDB
- Solo extrae: `name`, `logo_url`, `country`, `venue`
- El campo `league` queda vacío (`""`)

### Football-Data.org (Prioridad 2)

**Endpoint usado:**
```
GET https://api.football-data.org/v4/teams
```

**Respuesta:**
```json
{
  "teams": [{
    "id": 65,
    "name": "Manchester City",
    "shortName": "Man City",
    "crest": "https://...",
    "address": "...",
    "website": "...",
    "founded": 1880,
    "clubColors": "...",
    "venue": "...",
    "area": {
      "id": 2072,
      "name": "England",
      "code": "ENG"
    }
  }]
}
```

**⚠️ Problema:**
- No incluye información de liga directamente
- Necesita buscar en competiciones (`/competitions/{league}/teams`)

### API-Football (Prioridad 3)

**Endpoint usado:**
```
GET https://v3.football.api-sports.io/teams?search={team_name}
```

**Respuesta:**
```json
{
  "response": [{
    "team": {
      "id": 50,
      "name": "Manchester City",
      "code": "MCI",
      "country": "England",
      "founded": 1880,
      "national": false,
      "logo": "https://...",
      "venue": {
        "id": 555,
        "name": "Etihad Stadium",
        "address": "...",
        "city": "...",
        "capacity": 55097
      }
    }
  }]
}
```

**⚠️ Problema:**
- No incluye información de liga directamente
- Necesita buscar en ligas específicas

## 🔍 Problemas Identificados

### 1. Campo `league` Vacío

**Ubicación del problema:**

```python
# futbolia-backend/src/infrastructure/external_api/api_selector.py
# Línea 36-43
return Team(
    id=f"tsdb_{team_data.get('idTeam')}",
    name=team_data.get("strTeam", team_name),
    short_name=team_data.get("strTeamShort", ...),
    logo_url=team_data.get("strTeamBadge", ""),
    country=team_data.get("strCountry", ""),
    venue=team_data.get("strStadium", ""),
    # ❌ FALTA: league=team_data.get("strLeague", "")
)
```

### 2. ChromaDB No Tiene Información de Liga

- Los jugadores en ChromaDB solo tienen: `name`, `team`, `position`, `attributes`
- No se almacena información de liga
- Los equipos principales están hardcodeados sin liga

### 3. MongoDB Puede Tener Liga Vacía

- Si un equipo se crea desde una API externa sin liga, se guarda con `league=""`
- No hay validación ni búsqueda automática de liga

## ✅ Soluciones Propuestas

### Solución 1: Extraer Liga de TheSportsDB

```python
# En api_selector.py
return Team(
    id=f"tsdb_{team_data.get('idTeam')}",
    name=team_data.get("strTeam", team_name),
    short_name=team_data.get("strTeamShort", ...),
    logo_url=team_data.get("strTeamBadge", ""),
    country=team_data.get("strCountry", ""),
    venue=team_data.get("strStadium", ""),
    league=team_data.get("strLeague", ""),  # ✅ Agregar esto
)
```

### Solución 2: Mapear Equipos Principales a Ligas

```python
# En team_routes.py
LEAGUE_MAPPING = {
    "Real Madrid": "La Liga",
    "Barcelona": "La Liga",
    "Atletico Madrid": "La Liga",
    "Manchester City": "Premier League",
    "Liverpool": "Premier League",
    "Arsenal": "Premier League",
    "Chelsea": "Premier League",
    "Tottenham": "Premier League",
    "Bayern Munich": "Bundesliga",
    "Borussia Dortmund": "Bundesliga",
    "RB Leipzig": "Bundesliga",
    "Inter Milan": "Serie A",
    "AC Milan": "Serie A",
    "Juventus": "Serie A",
    "Napoli": "Serie A",
    "Paris Saint-Germain": "Ligue 1",
}
```

### Solución 3: Buscar Liga en Football-Data.org

- Iterar sobre competiciones conocidas
- Buscar el equipo en cada competición
- Extraer la liga cuando se encuentre

## 📝 Resumen

**Estado actual:**
- ✅ Las APIs externas SÍ tienen información de liga
- ❌ El código NO la extrae correctamente
- ❌ El campo `league` queda vacío en muchos casos
- ⚠️ Solo equipos guardados manualmente en MongoDB tienen liga

**Próximos pasos:**
1. Extraer `strLeague` de TheSportsDB
2. Mapear equipos principales a sus ligas
3. Mejorar búsqueda de liga en otras APIs
4. Validar y completar ligas en MongoDB

