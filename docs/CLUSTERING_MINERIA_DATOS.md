# 🔬 Minería de Datos: Clustering Jerárquico de Equipos de Fútbol

## 📋 Descripción General

Este documento describe la implementación del sistema de clustering jerárquico para el análisis de equipos de fútbol utilizando técnicas de minería de datos. Este módulo forma parte de FutbolIA y está diseñado para demostrar aplicaciones prácticas de minería de datos en eventos académicos como casas abiertas.

---

## 🎯 Objetivos

- **Clasificar equipos** según su rendimiento en la tabla de posiciones
- **Identificar patrones** en las características de rendimiento
- **Visualizar relaciones** jerárquicas entre equipos mediante dendrogramas
- **Demostrar técnicas** de minería de datos aplicadas al análisis deportivo

---

## 🔍 ¿Qué es el Clustering Jerárquico?

El **clustering jerárquico** es una técnica de minería de datos no supervisada que agrupa elementos similares en clusters basándose en sus características. A diferencia del clustering K-means, el clustering jerárquico no requiere especificar el número de clusters de antemano y muestra la estructura completa de agrupación mediante un dendrograma.

### Características Principales:

- **No supervisado**: No requiere etiquetas predefinidas
- **Jerárquico**: Muestra relaciones a múltiples niveles
- **Visualizable**: El dendrograma permite ver la estructura completa
- **Interpretable**: Los clusters tienen significado práctico

---

## 📊 Características Analizadas

El sistema analiza las siguientes características de cada equipo en la tabla de posiciones:

### 1. **Puntos por Partido Jugado** (normalizado)
- Indicador de rendimiento general
- Calculado como: `puntos / partidos_jugados`

### 2. **Diferencia de Goles por Partido**
- Mide la dominancia ofensiva/defensiva
- Calculado como: `(goles_a_favor - goles_en_contra) / partidos_jugados`

### 3. **Goles a Favor por Partido**
- Efectividad ofensiva
- Calculado como: `goles_a_favor / partidos_jugados`

### 4. **Goles en Contra por Partido**
- Efectividad defensiva
- Calculado como: `goles_en_contra / partidos_jugados`

### 5. **Tasa de Victoria**
- Porcentaje de partidos ganados
- Calculado como: `partidos_ganados / partidos_jugados`

### 6. **Tasa de Empate**
- Porcentaje de partidos empatados
- Calculado como: `partidos_empatados / partidos_jugados`

### 7. **Tasa de Derrota**
- Porcentaje de partidos perdidos
- Calculado como: `partidos_perdidos / partidos_jugados`

---

## 🔗 Métodos de Linkage

El clustering jerárquico utiliza diferentes métodos de linkage (enlace) para determinar cómo se calculan las distancias entre clusters:

### 1. **Ward** (Recomendado) ⭐
- **Características**: Minimiza la varianza dentro de los clusters
- **Ventajas**: Produce clusters compactos y bien separados
- **Cuándo usar**: Cuando se busca minimizar la varianza intra-cluster
- **Fórmula**: Minimiza `Σ(varianza dentro de cada cluster)`

### 2. **Complete (Máxima Distancia)**
- **Características**: Usa la distancia máxima entre puntos de clusters
- **Ventajas**: Garantiza que todos los puntos dentro de un cluster estén cerca
- **Cuándo usar**: Cuando se requiere cohesión estricta
- **Fórmula**: `max(d(p1, p2))` donde p1 ∈ C1, p2 ∈ C2

### 3. **Average (Distancia Promedio)**
- **Características**: Usa la distancia promedio entre todos los pares de puntos
- **Ventajas**: Balance entre cohesión y separación
- **Cuándo usar**: Cuando se busca un equilibrio
- **Fórmula**: `promedio(d(p1, p2))` para todos los pares

### 4. **Single (Distancia Mínima)**
- **Características**: Usa la distancia mínima entre puntos de clusters
- **Ventajas**: Útil para detectar clusters alargados
- **Cuándo usar**: Cuando se esperan clusters no esféricos
- **Fórmula**: `min(d(p1, p2))` donde p1 ∈ C1, p2 ∈ C2

---

## 🌳 Dendrograma

El **dendrograma** es una representación visual en forma de árbol que muestra cómo se agrupan los equipos jerárquicamente.

### Interpretación:

- **Eje X**: Equipos individuales (hojas del árbol)
- **Eje Y**: Distancia o altura de fusión (cuando más alto, más diferentes)
- **Nodos**: Puntos donde se fusionan clusters
- **Altura**: Indica la distancia a la que se fusionan clusters

### Ejemplo de Lectura:

```
    ┌─────┐
    │  A  │──────┐
    └─────┘      │
                 ├─────────┐
    ┌─────┐      │         │
    │  B  │──────┘         │
    └─────┘                │
                           ├────── Cluster 1
    ┌─────┐                │
    │  C  │────────────┐   │
    └─────┘            │   │
                       ├───┘
    ┌─────┐            │
    │  D  │────────────┘
    └─────┘
```

En este ejemplo:
- **A y B** están muy cerca (se fusionan a baja altura)
- **C y D** están cerca (se fusionan a baja altura)
- **El cluster (A,B)** y **(C,D)** están más separados (se fusionan a mayor altura)

---

## 💻 Implementación Técnica

### Backend (Python)

#### Dependencias:
```python
numpy>=1.26.0          # Operaciones numéricas
scikit-learn>=1.3.0    # Preprocesamiento y normalización
scipy>=1.11.0          # Clustering jerárquico
```

#### Estructura del Código:

```python
# 1. Preparar características
features, team_names = TeamClustering.prepare_features(standings)

# 2. Normalizar (especialmente para Ward)
features = StandardScaler().fit_transform(features)

# 3. Calcular matriz de distancias
distance_matrix = pdist(features, metric='euclidean')

# 4. Realizar linkage jerárquico
linkage_matrix = linkage(distance_matrix, method='ward')

# 5. Asignar clusters
cluster_labels = fcluster(linkage_matrix, n_clusters, criterion='maxclust')

# 6. Generar dendrograma
dendrogram_data = dendrogram(linkage_matrix, labels=team_names, no_plot=True)
```

#### Endpoint API:

```
GET /api/v1/leagues/clustering
Query Parameters:
  - league: Código de liga (PL, PD, SA, BL1, FL1)
  - n_clusters: Número de clusters deseados (2-10)
  - method: Método de linkage (ward, complete, average, single)
```

### Frontend (React Native)

#### Componentes Principales:

1. **ClusteringScreen**: Pantalla principal con controles y visualización
2. **DendrogramChart**: Componente SVG para renderizar el dendrograma
3. **ClusterInfo**: Muestra estadísticas descriptivas por cluster

#### Tecnologías:

- **react-native-svg**: Renderizado del dendrograma
- **Expo Router**: Navegación por tabs
- **TypeScript**: Tipado estático

---

## 📈 Interpretación de Resultados

### Tipos de Clusters Identificados:

1. **Equipos de Élite** 🏆
   - Alto rendimiento ofensivo y defensivo
   - Puntos promedio > 2.0 por partido
   - Diferencia de goles positiva y alta

2. **Equipos Competitivos** ⚽
   - Buen balance ofensivo-defensivo
   - Puntos promedio entre 1.5-2.0
   - Diferencia de goles positiva

3. **Equipos Medios** 📊
   - Rendimiento promedio
   - Puntos promedio entre 1.0-1.5
   - Diferencia de goles cercana a cero

4. **Equipos en Lucha** ⚠️
   - Necesitan mejorar
   - Puntos promedio entre 0.5-1.0
   - Diferencia de goles negativa

5. **Equipos en Dificultades** 🔻
   - Riesgo de descenso
   - Puntos promedio < 0.5
   - Diferencia de goles muy negativa

---

## 🎓 Aplicaciones Educativas

Este módulo es ideal para demostrar en casas abiertas porque:

### 1. **Conceptos de Minería de Datos**
- Clustering no supervisado
- Distancias y métricas
- Normalización de datos
- Evaluación de clusters

### 2. **Visualización de Datos**
- Dendrogramas jerárquicos
- Representación de relaciones
- Análisis exploratorio

### 3. **Aplicaciones Prácticas**
- Análisis deportivo
- Segmentación de clientes (analogía)
- Identificación de patrones

### 4. **Programación y Tecnologías**
- Python para análisis de datos
- APIs RESTful
- Visualización web/móvil
- Arquitectura de sistemas

---

## 🧪 Casos de Uso

### Ejemplo 1: Identificar Equipos Similares
**Objetivo**: Encontrar equipos con características de rendimiento similares

**Proceso**:
1. Seleccionar número de clusters (ej: 4)
2. Elegir método Ward
3. Analizar equipos dentro del mismo cluster

**Resultado**: Equipos agrupados por similitud en puntos, goles y tasas de victoria

### Ejemplo 2: Analizar Estructura de la Liga
**Objetivo**: Entender la distribución de rendimiento en la liga

**Proceso**:
1. Usar 5-6 clusters
2. Visualizar dendrograma completo
3. Identificar grupos de equipos

**Resultado**: Visión clara de equipos de élite, medios, y en dificultades

### Ejemplo 3: Comparar Métodos de Linkage
**Objetivo**: Ver cómo diferentes métodos afectan la agrupación

**Proceso**:
1. Analizar con Ward
2. Analizar con Complete
3. Comparar resultados

**Resultado**: Entendimiento de cómo cada método agrupa los datos

---

## 📚 Referencias Técnicas

### Algoritmos:
- **Hierarchical Clustering**: Algoritmo aglomerativo (bottom-up)
- **Linkage Methods**: Ward, Complete, Average, Single
- **Distance Metrics**: Distancia euclidiana

### Bibliotecas:
- **scipy.cluster.hierarchy**: Implementación de clustering jerárquico
- **scipy.spatial.distance**: Cálculo de distancias
- **sklearn.preprocessing**: Normalización de datos

### Métricas:
- **Silhouette Score**: (Opcional) Mide la calidad de clusters
- **Cophenetic Correlation**: (Opcional) Mide la preservación de distancias

---

## 🔧 Configuración y Uso

### Backend:

```bash
# Instalar dependencias
cd futbolia-backend
uv pip install -r pyproject.toml

# Ejecutar servidor
uvicorn src.main:app --reload
```

### Frontend:

```bash
# Instalar dependencias
cd futbolia-mobile
npm install

# Ejecutar app
npm start
```

### Ejemplo de Request:

```bash
curl "http://localhost:8000/api/v1/leagues/clustering?league=PL&n_clusters=4&method=ward"
```

---

## 📊 Ejemplo de Respuesta

```json
{
  "success": true,
  "data": {
    "n_clusters": 4,
    "method": "ward",
    "n_teams": 20,
    "teams": [
      {
        "name": "Liverpool",
        "cluster": 1,
        "position": 1,
        "points": 47,
        "goalDifference": 30
      },
      ...
    ],
    "cluster_info": [
      {
        "cluster_id": 1,
        "n_teams": 5,
        "description": "Equipos de élite: Alto rendimiento ofensivo y defensivo",
        "teams": ["Liverpool", "Arsenal", ...],
        "avg_points": 42.4,
        "avg_goal_difference": 20.2
      },
      ...
    ],
    "dendrogram": {
      "leaves": [0, 1, 2, ...],
      "ivl": ["Liverpool", "Arsenal", ...],
      "icoord": [[...], [...]],
      "dcoord": [[...], [...]]
    }
  }
}
```

---

## 🎯 Conclusiones

El sistema de clustering jerárquico en FutbolIA demuestra:

1. **Aplicación práctica** de técnicas de minería de datos
2. **Visualización efectiva** de relaciones complejas
3. **Análisis exploratorio** de datos deportivos
4. **Integración** entre backend de análisis y frontend visual

Este módulo es ideal para:
- ✅ Casas abiertas y demostraciones académicas
- ✅ Enseñanza de minería de datos
- ✅ Proyectos de análisis de datos
- ✅ Aplicaciones de clustering en dominios reales

---

## 📝 Notas para Presentaciones

### Puntos Clave a Destacar:

1. **Problema Real**: Analizar equipos de fútbol usando datos reales
2. **Técnica Aplicada**: Clustering jerárquico (minería de datos)
3. **Visualización**: Dendrograma interactivo
4. **Interpretación**: Clusters tienen significado práctico
5. **Tecnologías**: Python + React Native + APIs

### Preguntas Frecuentes:

**Q: ¿Por qué clustering jerárquico y no K-means?**  
A: El clustering jerárquico muestra la estructura completa y permite ver relaciones a múltiples niveles, además de no requerir especificar el número de clusters de antemano.

**Q: ¿Qué hace el método Ward?**  
A: Ward minimiza la varianza dentro de los clusters, produciendo grupos compactos y bien separados.

**Q: ¿Cómo se interpreta el dendrograma?**  
A: Equipos más cercanos en el eje X y que se fusionan a menor altura son más similares. La altura indica la "distancia" entre grupos.

**Q: ¿Por qué normalizar los datos?**  
A: La normalización asegura que todas las características tengan la misma escala, evitando que una característica domine sobre otras.

---

**Documento creado para FutbolIA - Sistema de Minería de Datos**  
*Última actualización: 2025*
