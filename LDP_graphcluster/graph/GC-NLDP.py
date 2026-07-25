"""
GC-NLDP: A graph clustering algorithm with local differential privacy.

GC-NLDP is a node-LDP based graph clustering framework that:
1. Uses silhouette coefficient for node aggregation to form initial clusters
2. Implements a cluster-based perturbation mechanism with adaptive noise
3. Develops a feedback loop between clients and curator for iterative optimization

Reference:
- Fu, N., Ni, W., Zhang, S., Hou, L., & Zhang, D. (2023). GC-NLDP:
  A graph clustering algorithm with local differential privacy.
  Computers & Security, 124, 102967.
"""

import networkx as nx
import numpy as np
from typing import List, Dict, Tuple, Set, Optional
import random
from collections import Counter, defaultdict
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans


class GCNLDP:
    """
    GC-NLDP: Node-LDP based graph clustering with feedback loop.

    The algorithm operates in two stages:
    1. Initial clustering using silhouette-based node aggregation
    2. Iterative refinement through client-curator feedback
    """

    def __init__(
            self,
            epsilon: float = 1.0,
            max_iterations: int = 30,
            feedback_rounds: int = 5,
            min_cluster_size: int = 3,
            seed: int = 42
    ):
        """
        Initialize the GC-NLDP algorithm.

        Args:
            epsilon: Privacy budget for node-LDP
            max_iterations: Maximum number of iterations for refinement
            feedback_rounds: Number of feedback rounds
            min_cluster_size: Minimum size of a cluster
            seed: Random seed for reproducibility
        """
        self.epsilon = epsilon
        self.max_iterations = max_iterations
        self.feedback_rounds = feedback_rounds
        self.min_cluster_size = min_cluster_size
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)

    def cluster(
            self,
            graph: nx.Graph,
            num_clusters: Optional[int] = None
    ) -> Dict[int, int]:
        """
        Cluster the graph using GC-NLDP.

        Args:
            graph: Input graph
            num_clusters: Number of clusters (if None, estimated automatically)

        Returns:
            Dictionary mapping node to cluster label
        """
        # Stage 1: Initial clustering
        initial_labels = self._initial_clustering(graph, num_clusters)

        # Stage 2: Feedback-based refinement
        refined_labels = self._refine_clusters(graph, initial_labels)

        # Compress labels
        unique_labels = sorted(set(refined_labels.values()))
        label_mapping = {old: new for new, old in enumerate(unique_labels)}
        return {node: label_mapping[label] for node, label in refined_labels.items()}

    def _initial_clustering(
            self,
            graph: nx.Graph,
            num_clusters: Optional[int] = None
    ) -> Dict[int, int]:
        """
        Stage 1: Initial clustering using silhouette-based node aggregation.

        This method:
        1. Computes node embeddings using spectral methods
        2. Uses silhouette coefficient to determine optimal number of clusters
        3. Performs K-means clustering
        """
        n = len(graph.nodes())
        nodes = list(graph.nodes())

        if n == 0:
            return {}

        if n < self.min_cluster_size:
            return {node: 0 for node in nodes}

        # Compute node embeddings using adjacency matrix
        adj = nx.adjacency_matrix(graph).toarray()

        # Use spectral embedding
        try:
            from sklearn.manifold import SpectralEmbedding

            embedding = SpectralEmbedding(
                n_components=min(50, n - 1),
                random_state=self.seed
            )
            features = embedding.fit_transform(adj)
        except ImportError:
            # Fallback: use degree and neighbor statistics
            features = self._compute_node_features(graph)

        # Determine number of clusters if not provided
        if num_clusters is None:
            num_clusters = self._estimate_clusters(graph, features)

        num_clusters = max(1, min(num_clusters, n))

        # K-means clustering
        try:
            from sklearn.cluster import KMeans

            kmeans = KMeans(
                n_clusters=num_clusters,
                random_state=self.seed,
                n_init=10
            )
            labels = kmeans.fit_predict(features)

        except ImportError:
            # Fallback: use connected components
            labels = self._cluster_by_components(graph)
            return {node: label for node, label in zip(nodes, labels)}

        # Merge small clusters
        labels = self._merge_small_clusters(graph, nodes, labels)

        return {node: label for node, label in zip(nodes, labels)}

    def _compute_node_features(self, graph: nx.Graph) -> np.ndarray:
        """Compute node features from graph structure."""
        nodes = list(graph.nodes())
        n = len(nodes)
        node_to_idx = {node: i for i, node in enumerate(nodes)}

        features = []
        for node in nodes:
            # Degree
            deg = graph.degree(node)

            # Neighbor degree sum
            neighbor_deg_sum = sum(graph.degree(neighbor) for neighbor in graph.neighbors(node))

            # Clustering coefficient
            try:
                cc = nx.clustering(graph, node)
            except:
                cc = 0

            features.append([deg, neighbor_deg_sum, cc])

        # Normalize
        features = np.array(features)
        if features.shape[1] > 0:
            means = features.mean(axis=0)
            stds = features.std(axis=0)
            stds[stds == 0] = 1
            features = (features - means) / stds

        return features

    def _estimate_clusters(self, graph: nx.Graph, features: np.ndarray) -> int:
        """Estimate the number of clusters using silhouette coefficient."""
        n = len(features)

        if n <= 2:
            return 1

        max_clusters = min(20, n // 2)

        try:
            from sklearn.cluster import KMeans

            best_score = -1
            best_k = 2

            for k in range(2, max_clusters + 1):
                kmeans = KMeans(n_clusters=k, random_state=self.seed, n_init=10)
                labels = kmeans.fit_predict(features)

                if len(set(labels)) < 2:
                    continue

                try:
                    score = silhouette_score(features, labels)
                    if score > best_score:
                        best_score = score
                        best_k = k
                except:
                    continue

            return best_k

        except ImportError:
            # Default: use 2 clusters or connected components
            return min(2, n)

    def _merge_small_clusters(
            self,
            graph: nx.Graph,
            nodes: List,
            labels: np.ndarray
    ) -> np.ndarray:
        """Merge clusters that are too small."""
        label_counts = Counter(labels)

        # Find small clusters
        small_clusters = [lbl for lbl, cnt in label_counts.items() if cnt < self.min_cluster_size]

        if not small_clusters:
            return labels

        # Map each node to its cluster
        node_to_label = {node: label for node, label in zip(nodes, labels)}

        # For each small cluster, merge with the most connected larger cluster
        for small_label in small_clusters:
            small_nodes = [node for node, lbl in node_to_label.items() if lbl == small_label]

            if not small_nodes:
                continue

            # Find the best cluster to merge into
            best_label = None
            best_connections = -1

            for node in small_nodes:
                for neighbor in graph.neighbors(node):
                    if neighbor in node_to_label:
                        neighbor_label = node_to_label[neighbor]
                        if neighbor_label != small_label and neighbor_label not in small_clusters:
                            connections = sum(
                                1 for n2 in small_nodes
                                if graph.has_edge(n2, neighbor)
                            )
                            if connections > best_connections:
                                best_connections = connections
                                best_label = neighbor_label

            if best_label is not None:
                # Merge into best_label
                for node in small_nodes:
                    node_to_label[node] = best_label
            else:
                # Keep as is
                pass

        return np.array([node_to_label[node] for node in nodes])

    def _cluster_by_components(self, graph: nx.Graph) -> np.ndarray:
        """Fallback clustering using connected components."""
        components = list(nx.connected_components(graph))
        labels = np.zeros(len(graph.nodes()), dtype=int)
        node_list = list(graph.nodes())

        for label, component in enumerate(components):
            for node in component:
                labels[node_list.index(node)] = label

        return labels

    def _refine_clusters(
            self,
            graph: nx.Graph,
            initial_labels: Dict[int, int]
    ) -> Dict[int, int]:
        """
        Stage 2: Refine clusters through feedback loop.

        The feedback loop iteratively:
        1. Collects node-cluster similarity information from clients
        2. Updates cluster assignments
        3. Refines the perturbation mechanism
        """
        labels = initial_labels.copy()
        nodes = list(graph.nodes())

        # Get unique clusters
        unique_labels = set(labels.values())
        clusters = {label: [node for node, lbl in labels.items() if lbl == label]
                    for label in unique_labels}

        for iteration in range(self.feedback_rounds):
            # Compute node-cluster similarities (with LDP noise)
            similarities = self._compute_similarities(graph, labels, clusters)

            # Update cluster assignments based on similarities
            new_labels = {}
            for node in nodes:
                if node in similarities:
                    # Find the most similar cluster
                    node_sims = similarities[node]
                    if node_sims:
                        best_label = max(node_sims, key=node_sims.get)
                        new_labels[node] = best_label
                    else:
                        new_labels[node] = labels[node]
                else:
                    new_labels[node] = labels[node]

            # Check for convergence
            changes = sum(1 for node in nodes if new_labels.get(node) != labels.get(node))

            # Update labels
            labels = new_labels

            # Rebuild clusters
            clusters = {label: [node for node, lbl in labels.items() if lbl == label]
                        for label in set(labels.values())}

            # Remove empty clusters
            clusters = {k: v for k, v in clusters.items() if v}

            if changes == 0:
                break

        return labels

    def _compute_similarities(
            self,
            graph: nx.Graph,
            labels: Dict[int, int],
            clusters: Dict[int, List]
    ) -> Dict[int, Dict[int, float]]:
        """
        Compute node-cluster similarities with LDP noise.

        Similarity is based on the proportion of neighbors in each cluster.
        """
        node_to_label = labels
        similarities = {}

        # Sensitivity for LDP
        sensitivity = 1.0
        scale = sensitivity / (self.epsilon / self.feedback_rounds)

        for node in graph.nodes():
            # Count neighbors in each cluster
            cluster_counts = defaultdict(int)
            total_neighbors = 0

            for neighbor in graph.neighbors(node):
                total_neighbors += 1
                if neighbor in node_to_label:
                    cluster_counts[node_to_label[neighbor]] += 1

            # Compute similarity scores
            node_sims = {}
            for label, cluster_nodes in clusters.items():
                if total_neighbors > 0:
                    # Proportion of neighbors in this cluster
                    sim = cluster_counts.get(label, 0) / total_neighbors
                else:
                    # Isolated node: equal similarity to all clusters
                    sim = 1.0 / len(clusters) if clusters else 0

                # Add Laplace noise for LDP
                noise = np.random.laplace(0, scale)
                node_sims[label] = max(0, min(1, sim + noise))

            similarities[node] = node_sims

        return similarities

    def _compute_silhouette(
            self,
            graph: nx.Graph,
            labels: Dict[int, int]
    ) -> float:
        """
        Compute silhouette coefficient for the current clustering.

        Uses graph distance (shortest path length) as the distance metric.
        """
        try:
            # Compute all-pairs shortest paths
            nodes = list(graph.nodes())
            n = len(nodes)
            node_to_idx = {node: i for i, node in enumerate(nodes)}

            # Distance matrix
            dist_matrix = np.zeros((n, n))
            for i, u in enumerate(nodes):
                for j, v in enumerate(nodes):
                    if i != j:
                        try:
                            dist_matrix[i, j] = nx.shortest_path_length(graph, u, v)
                        except nx.NetworkXNoPath:
                            dist_matrix[i, j] = n  # Large distance for disconnected

            # Get labels in node order
            label_list = [labels[node] for node in nodes]

            if len(set(label_list)) < 2:
                return -1

            return silhouette_score(dist_matrix, label_list, metric='precomputed')

        except Exception:
            return -1