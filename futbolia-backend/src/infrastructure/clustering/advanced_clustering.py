"""
Advanced Clustering Module
Técnicas avanzadas de clustering para análisis de equipos y jugadores
Incluye K-Means, DBSCAN, y análisis de silueta
"""
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, silhouette_samples
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import pdist

from src.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ClusteringResult:
    """Resultado de clustering con métricas"""
    labels: List[int]
    n_clusters: int
    silhouette_score: float
    inertia: Optional[float] = None  # Solo para K-Means
    noise_points: int = 0  # Solo para DBSCAN
    cluster_sizes: Dict[int, int] = None
    cluster_centers: Optional[np.ndarray] = None
    method: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "labels": self.labels,
            "n_clusters": self.n_clusters,
            "silhouette_score": round(self.silhouette_score, 4),
            "inertia": round(self.inertia, 4) if self.inertia else None,
            "noise_points": self.noise_points,
            "cluster_sizes": self.cluster_sizes,
            "method": self.method,
        }


class AdvancedClustering:
    """
    Clustering avanzado para análisis de equipos de fútbol
    
    Algoritmos disponibles:
    - K-Means: Para grupos bien definidos y esféricos
    - DBSCAN: Para detectar outliers y clusters de forma arbitraria
    - Jerárquico: Para visualización y análisis de similitud
    
    Features utilizadas:
    - Puntos por partido
    - Diferencia de goles por partido
    - Goles a favor/contra por partido
    - Tasa de victoria/empate/derrota
    - Posesión promedio (si disponible)
    """
    
    @staticmethod
    def prepare_features(
        standings: List[Dict[str, Any]],
        feature_set: str = "standard"
    ) -> Tuple[np.ndarray, List[str], List[str]]:
        """
        Preparar matriz de características para clustering
        
        Args:
            standings: Datos de tabla de posiciones
            feature_set: 'standard', 'extended', 'offensive', 'defensive'
            
        Returns:
            Tuple con: matriz de features, nombres de equipos, nombres de features
        """
        features = []
        team_names = []
        
        # Definir features según el conjunto seleccionado
        feature_configs = {
            "standard": [
                ("points_per_game", lambda e, p: e.get("points", 0) / p),
                ("goal_diff_per_game", lambda e, p: e.get("goalDifference", 0) / p),
                ("win_rate", lambda e, p: e.get("won", 0) / p),
                ("goals_per_game", lambda e, p: e.get("goalsFor", 0) / p),
            ],
            "extended": [
                ("points_per_game", lambda e, p: e.get("points", 0) / p),
                ("goal_diff_per_game", lambda e, p: e.get("goalDifference", 0) / p),
                ("win_rate", lambda e, p: e.get("won", 0) / p),
                ("draw_rate", lambda e, p: e.get("draw", 0) / p),
                ("loss_rate", lambda e, p: e.get("lost", 0) / p),
                ("goals_per_game", lambda e, p: e.get("goalsFor", 0) / p),
                ("goals_against_per_game", lambda e, p: e.get("goalsAgainst", 0) / p),
            ],
            "offensive": [
                ("goals_per_game", lambda e, p: e.get("goalsFor", 0) / p),
                ("win_rate", lambda e, p: e.get("won", 0) / p),
                ("points_per_game", lambda e, p: e.get("points", 0) / p),
            ],
            "defensive": [
                ("goals_against_per_game", lambda e, p: e.get("goalsAgainst", 0) / p),
                ("clean_sheet_rate", lambda e, p: 1 - (e.get("goalsAgainst", 0) / max(p * 2, 1))),
                ("loss_rate", lambda e, p: e.get("lost", 0) / p),
            ],
        }
        
        config = feature_configs.get(feature_set, feature_configs["standard"])
        feature_names = [name for name, _ in config]
        
        for entry in standings:
            team_info = entry.get("team", {})
            team_name = team_info.get("name", f"Team_{len(team_names)}")
            team_names.append(team_name)
            
            played = max(entry.get("playedGames", 1), 1)
            
            feature_vector = [func(entry, played) for _, func in config]
            features.append(feature_vector)
        
        return np.array(features), team_names, feature_names
    
    @staticmethod
    def kmeans_clustering(
        standings: List[Dict[str, Any]],
        n_clusters: int = 4,
        feature_set: str = "standard",
        random_state: int = 42
    ) -> Dict[str, Any]:
        """
        K-Means clustering de equipos
        
        Args:
            standings: Datos de tabla de posiciones
            n_clusters: Número de clusters (default 4: élite, alto, medio, bajo)
            feature_set: Conjunto de features a usar
            random_state: Semilla para reproducibilidad
            
        Returns:
            Resultado detallado del clustering
        """
        if len(standings) < n_clusters:
            raise ValueError(f"Se necesitan al menos {n_clusters} equipos")
        
        # Preparar features
        features, team_names, feature_names = AdvancedClustering.prepare_features(
            standings, feature_set
        )
        
        # Normalizar features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Aplicar K-Means
        kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=random_state,
            n_init=10,
            max_iter=300
        )
        labels = kmeans.fit_predict(features_scaled)
        
        # Calcular métricas
        silhouette_avg = silhouette_score(features_scaled, labels)
        silhouette_values = silhouette_samples(features_scaled, labels)
        
        # Organizar resultados por cluster
        cluster_sizes = {}
        teams_by_cluster = []
        
        for idx, (team_name, label) in enumerate(zip(team_names, labels)):
            cluster_id = int(label) + 1  # Clusters 1-indexed
            
            if cluster_id not in cluster_sizes:
                cluster_sizes[cluster_id] = 0
            cluster_sizes[cluster_id] += 1
            
            teams_by_cluster.append({
                "name": team_name,
                "cluster": cluster_id,
                "silhouette": round(float(silhouette_values[idx]), 4),
                "features": {
                    name: round(float(features[idx][i]), 4)
                    for i, name in enumerate(feature_names)
                },
                "position": standings[idx].get("position", idx + 1),
                "points": standings[idx].get("points", 0),
            })
        
        # Calcular centroides desnormalizados
        centroids = scaler.inverse_transform(kmeans.cluster_centers_)
        
        # Generar descripciones de clusters
        cluster_info = AdvancedClustering._generate_cluster_descriptions(
            centroids, feature_names, cluster_sizes
        )
        
        return {
            "method": "kmeans",
            "n_clusters": n_clusters,
            "feature_set": feature_set,
            "silhouette_score": round(float(silhouette_avg), 4),
            "inertia": round(float(kmeans.inertia_), 4),
            "teams": teams_by_cluster,
            "cluster_info": cluster_info,
            "cluster_centers": centroids.tolist(),
            "feature_names": feature_names,
        }
    
    @staticmethod
    def dbscan_clustering(
        standings: List[Dict[str, Any]],
        eps: float = 0.5,
        min_samples: int = 2,
        feature_set: str = "standard"
    ) -> Dict[str, Any]:
        """
        DBSCAN clustering para detectar outliers y clusters irregulares
        
        Args:
            standings: Datos de tabla de posiciones
            eps: Distancia máxima entre puntos de un cluster
            min_samples: Mínimo de puntos para formar un cluster
            feature_set: Conjunto de features a usar
            
        Returns:
            Resultado del clustering con detección de outliers
        """
        if len(standings) < min_samples:
            raise ValueError(f"Se necesitan al menos {min_samples} equipos")
        
        # Preparar features
        features, team_names, feature_names = AdvancedClustering.prepare_features(
            standings, feature_set
        )
        
        # Normalizar features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Aplicar DBSCAN
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(features_scaled)
        
        # Contar clusters y outliers
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = list(labels).count(-1)
        
        # Calcular silhouette solo si hay más de un cluster y no todo es ruido
        valid_labels = labels[labels >= 0]
        valid_features = features_scaled[labels >= 0]
        
        if n_clusters > 1 and len(valid_labels) > n_clusters:
            silhouette_avg = silhouette_score(valid_features, valid_labels)
        else:
            silhouette_avg = 0.0
        
        # Organizar resultados
        cluster_sizes = {}
        teams_by_cluster = []
        outliers = []
        
        for idx, (team_name, label) in enumerate(zip(team_names, labels)):
            cluster_id = int(label) + 1 if label >= 0 else -1  # -1 para outliers
            
            team_data = {
                "name": team_name,
                "cluster": cluster_id,
                "is_outlier": label == -1,
                "features": {
                    name: round(float(features[idx][i]), 4)
                    for i, name in enumerate(feature_names)
                },
                "position": standings[idx].get("position", idx + 1),
                "points": standings[idx].get("points", 0),
            }
            
            if label == -1:
                outliers.append(team_data)
            else:
                teams_by_cluster.append(team_data)
                if cluster_id not in cluster_sizes:
                    cluster_sizes[cluster_id] = 0
                cluster_sizes[cluster_id] += 1
        
        return {
            "method": "dbscan",
            "eps": eps,
            "min_samples": min_samples,
            "feature_set": feature_set,
            "n_clusters": n_clusters,
            "noise_points": n_noise,
            "silhouette_score": round(float(silhouette_avg), 4),
            "teams": teams_by_cluster,
            "outliers": outliers,
            "cluster_sizes": cluster_sizes,
            "feature_names": feature_names,
            "interpretation": AdvancedClustering._interpret_dbscan_results(
                n_clusters, n_noise, len(standings)
            ),
        }
    
    @staticmethod
    def find_optimal_clusters(
        standings: List[Dict[str, Any]],
        max_clusters: int = 8,
        feature_set: str = "standard"
    ) -> Dict[str, Any]:
        """
        Encontrar número óptimo de clusters usando método del codo y silhouette
        
        Args:
            standings: Datos de tabla de posiciones
            max_clusters: Máximo de clusters a probar
            feature_set: Conjunto de features a usar
            
        Returns:
            Análisis con recomendación de clusters óptimos
        """
        if len(standings) < 3:
            return {"error": "Se necesitan al menos 3 equipos"}
        
        # Preparar features
        features, team_names, feature_names = AdvancedClustering.prepare_features(
            standings, feature_set
        )
        
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        max_clusters = min(max_clusters, len(standings) - 1)
        
        results = {
            "elbow_method": [],
            "silhouette_method": [],
            "recommended_clusters": 0,
        }
        
        best_silhouette = -1
        best_k = 2
        
        for k in range(2, max_clusters + 1):
            # K-Means para este k
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(features_scaled)
            
            # Inertia (método del codo)
            results["elbow_method"].append({
                "k": k,
                "inertia": round(float(kmeans.inertia_), 4)
            })
            
            # Silhouette score
            if k < len(standings):
                silhouette = silhouette_score(features_scaled, labels)
                results["silhouette_method"].append({
                    "k": k,
                    "silhouette": round(float(silhouette), 4)
                })
                
                if silhouette > best_silhouette:
                    best_silhouette = silhouette
                    best_k = k
        
        results["recommended_clusters"] = best_k
        results["best_silhouette_score"] = round(best_silhouette, 4)
        results["interpretation"] = AdvancedClustering._interpret_optimal_clusters(
            best_k, best_silhouette, len(standings)
        )
        
        return results
    
    @staticmethod
    def player_clustering(
        players: List[Dict[str, Any]],
        n_clusters: int = 5,
        position_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Clustering de jugadores basado en atributos
        
        Args:
            players: Lista de jugadores con atributos
            n_clusters: Número de clusters
            position_filter: Filtrar por posición ('GK', 'DEF', 'MID', 'FWD')
            
        Returns:
            Resultado del clustering de jugadores
        """
        # Filtrar por posición si se especifica
        if position_filter:
            players = [
                p for p in players 
                if position_filter.lower() in p.get("position", "").lower()
            ]
        
        if len(players) < n_clusters:
            return {"error": f"Se necesitan al menos {n_clusters} jugadores"}
        
        # Extraer features numéricas disponibles
        feature_names = ["overall_rating", "pace", "shooting", "passing", "dribbling", "defending", "physical"]
        
        features = []
        player_names = []
        
        for player in players:
            player_features = []
            valid = True
            
            for feature in feature_names:
                value = player.get(feature)
                if value is None:
                    valid = False
                    break
                player_features.append(float(value))
            
            if valid:
                features.append(player_features)
                player_names.append(player.get("name", "Unknown"))
        
        if len(features) < n_clusters:
            return {"error": "No hay suficientes jugadores con datos completos"}
        
        # Normalizar y clustering
        features_array = np.array(features)
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features_array)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(features_scaled)
        
        silhouette_avg = silhouette_score(features_scaled, labels)
        
        # Organizar resultados
        players_by_cluster = []
        for idx, (name, label) in enumerate(zip(player_names, labels)):
            players_by_cluster.append({
                "name": name,
                "cluster": int(label) + 1,
                "attributes": {
                    feat: round(features_array[idx][i], 1)
                    for i, feat in enumerate(feature_names)
                }
            })
        
        return {
            "method": "kmeans",
            "n_clusters": n_clusters,
            "position_filter": position_filter,
            "players_analyzed": len(features),
            "silhouette_score": round(float(silhouette_avg), 4),
            "players": players_by_cluster,
            "feature_names": feature_names,
        }
    
    @staticmethod
    def _generate_cluster_descriptions(
        centroids: np.ndarray,
        feature_names: List[str],
        cluster_sizes: Dict[int, int]
    ) -> List[Dict[str, Any]]:
        """Generar descripciones interpretables de cada cluster"""
        descriptions = []
        
        # Ordenar clusters por rendimiento (primer feature suele ser points_per_game)
        cluster_order = sorted(
            range(len(centroids)),
            key=lambda i: centroids[i][0],
            reverse=True
        )
        
        tier_names = ["Élite", "Competitivo", "Medio", "En lucha", "En dificultades"]
        tier_descriptions = [
            "Equipos de máximo nivel con rendimiento excepcional",
            "Equipos fuertes con buenos resultados",
            "Equipos con rendimiento promedio de la liga",
            "Equipos que necesitan mejorar para competir",
            "Equipos con dificultades y riesgo de descenso"
        ]
        
        for rank, cluster_idx in enumerate(cluster_order):
            cluster_id = cluster_idx + 1
            centroid = centroids[cluster_idx]
            
            tier_idx = min(rank, len(tier_names) - 1)
            
            # Características destacadas
            feature_values = {
                name: round(float(centroid[i]), 3)
                for i, name in enumerate(feature_names)
            }
            
            descriptions.append({
                "cluster_id": cluster_id,
                "tier_name": tier_names[tier_idx],
                "description": tier_descriptions[tier_idx],
                "n_teams": cluster_sizes.get(cluster_id, 0),
                "centroid_values": feature_values,
                "rank": rank + 1,
            })
        
        return descriptions
    
    @staticmethod
    def _interpret_dbscan_results(
        n_clusters: int,
        n_noise: int,
        total_teams: int
    ) -> str:
        """Interpretar resultados de DBSCAN"""
        noise_ratio = n_noise / total_teams if total_teams > 0 else 0
        
        if n_clusters == 0:
            return "No se encontraron clusters definidos. Considera ajustar eps o min_samples."
        elif noise_ratio > 0.3:
            return f"Alta cantidad de outliers ({n_noise} de {total_teams}). La liga tiene equipos muy diversos."
        elif n_noise == 0:
            return f"Todos los equipos pertenecen a {n_clusters} grupos bien definidos."
        else:
            return f"{n_clusters} grupos identificados con {n_noise} equipos atípicos."
    
    @staticmethod
    def _interpret_optimal_clusters(
        k: int,
        silhouette: float,
        n_teams: int
    ) -> str:
        """Interpretar recomendación de clusters óptimos"""
        if silhouette > 0.5:
            quality = "excelente"
        elif silhouette > 0.25:
            quality = "buena"
        else:
            quality = "moderada"
        
        if k == 2:
            desc = "División binaria (élite vs resto)"
        elif k == 3:
            desc = "Tres niveles (alto, medio, bajo)"
        elif k == 4:
            desc = "Cuatro tiers típicos de liga"
        elif k == 5:
            desc = "Clasificación detallada en 5 niveles"
        else:
            desc = f"Clasificación granular en {k} grupos"
        
        return f"Se recomienda {k} clusters con {quality} separación. {desc}."
