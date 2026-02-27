"""
Team Clustering Service
Realiza clustering jerárquico de equipos basado en estadísticas de posiciones
"""

from typing import Any

import numpy as np
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
from scipy.spatial.distance import pdist


class TeamClustering:
    """
    Servicio para realizar clustering jerárquico de equipos de fútbol
    basado en sus estadísticas en la tabla de posiciones.
    """

    @staticmethod
    def prepare_features(standings: list[dict[str, Any]]) -> tuple[np.ndarray, list[str]]:
        """
        Prepara las características de los equipos para el clustering.

        Features utilizadas:
        - Puntos por partido jugado (normalizado)
        - Diferencia de goles por partido
        - Goles a favor por partido
        - Goles en contra por partido
        - Porcentaje de victorias
        - Porcentaje de empates
        - Porcentaje de derrotas

        Args:
            standings: Lista de entradas de la tabla de posiciones

        Returns:
            Tuple con la matriz de características y lista de nombres de equipos
        """
        features = []
        team_names = []

        for entry in standings:
            team_names.append(entry["team"]["name"])

            played = max(entry.get("playedGames", 1), 1)  # Evitar división por cero
            points = entry.get("points", 0)
            goals_for = entry.get("goalsFor", 0)
            goals_against = entry.get("goalsAgainst", 0)
            goal_difference = entry.get("goalDifference", 0)
            won = entry.get("won", 0)
            draw = entry.get("draw", 0)
            lost = entry.get("lost", 0)

            # Calcular características normalizadas
            points_per_game = points / played
            goals_for_per_game = goals_for / played
            goals_against_per_game = goals_against / played
            goal_diff_per_game = goal_difference / played
            win_rate = won / played
            draw_rate = draw / played
            loss_rate = lost / played

            # Crear vector de características
            feature_vector = [
                points_per_game,
                goal_diff_per_game,
                goals_for_per_game,
                goals_against_per_game,
                win_rate,
                draw_rate,
                loss_rate,
            ]

            features.append(feature_vector)

        return np.array(features), team_names

    @staticmethod
    def perform_clustering(
        standings: list[dict[str, Any]], n_clusters: int = 4, method: str = "ward"
    ) -> dict[str, Any]:
        """
        Realiza clustering jerárquico de los equipos.

        Args:
            standings: Lista de entradas de la tabla de posiciones
            n_clusters: Número de clusters deseados (por defecto 4)
            method: Método de linkage ('ward', 'complete', 'average', 'single')

        Returns:
            Diccionario con los resultados del clustering incluyendo:
            - linkage_matrix: Matriz de linkage para el dendrograma
            - clusters: Asignación de cluster para cada equipo
            - teams: Lista de equipos con su cluster asignado
            - cluster_info: Información estadística de cada cluster
        """
        if len(standings) < 2:
            raise ValueError("Se necesitan al menos 2 equipos para realizar clustering")

        # Preparar características
        features, team_names = TeamClustering.prepare_features(standings)

        # Normalizar características (importante para métodos como ward)
        if method == "ward":
            # Ward requiere datos normalizados
            from sklearn.preprocessing import StandardScaler

            scaler = StandardScaler()
            features_normalized = scaler.fit_transform(features)
            # Para ward, podemos pasar los datos directamente (no necesita pdist)
            linkage_matrix = linkage(features_normalized, method=method)
        else:
            # Para otros métodos, calcular matriz de distancias primero
            distance_matrix = pdist(features, metric="euclidean")
            linkage_matrix = linkage(distance_matrix, method=method)

        # Asignar clusters
        cluster_labels = fcluster(linkage_matrix, n_clusters, criterion="maxclust")

        # Obtener datos del dendrograma para visualización
        dendrogram_data = dendrogram(
            linkage_matrix,
            labels=team_names,
            no_plot=True,  # No generar plot, solo obtener datos
            get_leaves=True,
        )

        # Organizar equipos por cluster
        teams_by_cluster = []
        for idx, team_name in enumerate(team_names):
            teams_by_cluster.append(
                {
                    "name": team_name,
                    "cluster": int(cluster_labels[idx]),
                    "position": standings[idx].get("position", idx + 1),
                    "points": standings[idx].get("points", 0),
                    "goalDifference": standings[idx].get("goalDifference", 0),
                }
            )

        # Calcular estadísticas por cluster
        cluster_info = TeamClustering._calculate_cluster_stats(teams_by_cluster, n_clusters)

        # Preparar datos del dendrograma para el frontend
        # Calcular posiciones X de cada hoja para mapeo correcto
        # En scipy.dendrogram, las hojas están ordenadas de izquierda a derecha
        # según el array 'leaves', y sus posiciones X están en los valores únicos de icoord
        leaf_positions = {}

        if dendrogram_data.get("leaves") and dendrogram_data.get("icoord"):
            # Recopilar todas las posiciones X del dendrograma
            all_x_values = []
            for icoord in dendrogram_data["icoord"]:
                all_x_values.extend(icoord)

            # Encontrar valores únicos y ordenarlos (estos son los puntos donde están las hojas)
            unique_x = sorted(set(all_x_values))

            # Las hojas en scipy están ordenadas de izquierda a derecha
            # Mapear cada hoja (por su índice en leaves) a su posición X
            # Las primeras hojas tienen las posiciones X más pequeñas
            n_leaves = len(dendrogram_data["leaves"])

            if len(unique_x) >= n_leaves:
                # Usar las primeras n_leaves posiciones X (las más a la izquierda)
                for pos, leaf_idx in enumerate(dendrogram_data["leaves"]):
                    leaf_positions[leaf_idx] = unique_x[pos]
            else:
                # Fallback: distribución uniforme basada en el rango
                min_x = min(unique_x) if unique_x else 0
                max_x = max(unique_x) if unique_x else n_leaves * 10
                for pos, leaf_idx in enumerate(dendrogram_data["leaves"]):
                    if pos < len(unique_x):
                        leaf_positions[leaf_idx] = unique_x[pos]
                    else:
                        # Distribución uniforme para hojas adicionales
                        leaf_positions[leaf_idx] = (
                            min_x + (pos * (max_x - min_x) / (n_leaves - 1))
                            if n_leaves > 1
                            else min_x
                        )

        dendrogram_plot = {
            "leaves": dendrogram_data["leaves"],
            "ivl": dendrogram_data["ivl"],  # Etiquetas de las hojas
            "icoord": dendrogram_data["icoord"],  # Coordenadas X del dendrograma
            "dcoord": dendrogram_data["dcoord"],  # Coordenadas Y (altura) del dendrograma
            "leaf_x_positions": leaf_positions,  # Mapeo de hoja -> posición X
        }

        return {
            "linkage_matrix": linkage_matrix.tolist(),  # Convertir a lista para JSON
            "clusters": cluster_labels.tolist(),
            "teams": teams_by_cluster,
            "cluster_info": cluster_info,
            "dendrogram": dendrogram_plot,
            "n_clusters": n_clusters,
            "method": method,
            "n_teams": len(team_names),
        }

    @staticmethod
    def _calculate_cluster_stats(
        teams_by_cluster: list[dict[str, Any]], n_clusters: int
    ) -> list[dict[str, Any]]:
        """
        Calcula estadísticas descriptivas para cada cluster.

        Args:
            teams_by_cluster: Lista de equipos con su cluster asignado
            n_clusters: Número de clusters

        Returns:
            Lista de diccionarios con estadísticas por cluster
        """
        cluster_stats = []

        for cluster_id in range(1, n_clusters + 1):
            cluster_teams = [t for t in teams_by_cluster if t["cluster"] == cluster_id]

            if not cluster_teams:
                continue

            points = [t["points"] for t in cluster_teams]
            goal_diffs = [t["goalDifference"] for t in cluster_teams]

            cluster_stats.append(
                {
                    "cluster_id": cluster_id,
                    "n_teams": len(cluster_teams),
                    "teams": [t["name"] for t in cluster_teams],
                    "avg_points": float(np.mean(points)),
                    "min_points": int(np.min(points)),
                    "max_points": int(np.max(points)),
                    "avg_goal_difference": float(np.mean(goal_diffs)),
                    "description": TeamClustering._generate_cluster_description(
                        cluster_id, points, goal_diffs
                    ),
                }
            )

        return cluster_stats

    @staticmethod
    def _generate_cluster_description(
        cluster_id: int, points: list[float], goal_diffs: list[float]
    ) -> str:
        """
        Genera una descripción textual del cluster basado en sus estadísticas.

        Args:
            cluster_id: ID del cluster
            points: Lista de puntos de los equipos del cluster
            goal_diffs: Lista de diferencias de goles

        Returns:
            Descripción del cluster
        """
        avg_points = np.mean(points)
        avg_goal_diff = np.mean(goal_diffs)

        if avg_points >= 2.0 and avg_goal_diff > 0:
            return "Equipos de élite: Alto rendimiento ofensivo y defensivo"
        elif avg_points >= 1.5 and avg_goal_diff > 0:
            return "Equipos competitivos: Buen balance ofensivo-defensivo"
        elif avg_points >= 1.0:
            return "Equipos medios: Rendimiento promedio"
        elif avg_points >= 0.5:
            return "Equipos en lucha: Necesitan mejorar para evitar descenso"
        else:
            return "Equipos en dificultades: Riesgo de descenso"
