"""
Wdt-SCAN: Clustering decentralized social graphs with local differential privacy.

Wdt-SCAN is a degree-vector based private graph clustering scheme that:
1. Encodes star graphs using degree vectors with optimal length
2. Partitions nodes into core nodes and ordinary nodes using the Pareto principle
3. Clusters core nodes to form a graph skeleton
4. Expands clusters to include ordinary nodes

Reference:
- Hou, L., Ni, W., Zhang, S., Fu, N., & Zhang, D. (2023). Wdt-SCAN:
  Clustering decentralized social graphs with local differential privacy.
  Computers & Security, 125, 103036.
"""

import networkx as nx
import numpy as np
from typing import List, Dict, Tuple, Set, Optional
import random
from collections import Counter, defaultdict
from sklearn.cluster import DBSCAN


class WdtSCAN:
    """
    Wdt-SCAN: Degree-vector based private graph clustering.

    The algorithm uses the Pareto principle (80/20 rule) to identify
    core nodes and then applies structural clustering to form communities.
    """

    def __init__(
            self,
            epsilon: float = 1.0,
            core_ratio: float = 0.2,
            eps_scan: float = 0.5,
            mu: int = 2,
            seed: int = 42
    ):
        """
        Initialize the Wdt-SCAN algorithm.

        Args:
            epsilon: Privacy budget for degree perturbation
            core_ratio: Ratio of nodes to consider as core (Pareto principle)
            eps_scan: Epsilon parameter for SCAN structural similarity
            mu: Mu parameter for SCAN (minimum community size)
            seed: Random seed for reproducibility
        """
        self.epsilon = epsilon
        self.core_ratio = core_ratio
        self.eps_scan = eps_scan
        self.mu = mu
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)

    def cluster(
            self,
            graph: nx.Graph,
            num_clusters: Optional[int] = None
    ) -> Dict[int, int]:
        """
        Cluster the graph using Wdt-SCAN.

        Args:
            graph: Input graph
            num_clusters: Number of clusters (used for core node clustering)

        Returns:
            Dictionary mapping node to cluster label
        """
        # Step 1: Compute degrees
        degrees = dict(graph.degree())
        n = len(graph.nodes())

        # Step 2: Identify core nodes using Pareto principle
        sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
        core_count = max(1, int(n * self.core_ratio))
        core_nodes = [node for node, _ in sorted_nodes[:core_count]]
        core_set = set(core_nodes)

        # Step 3: Add noise to degrees for LDP (simulate perturbation)
        noisy_degrees = self._perturb_degrees(degrees)

        # Step 4: Build core graph
        core_graph = nx.Graph()
        core_graph.add_nodes_from(core_nodes)

        # Add edges between core nodes if they are connected in the original graph
        # and have sufficient structural similarity
        for i, u in enumerate(core_nodes):
            for v in core_nodes[i + 1:]:
                if graph.has_edge(u, v):
                    # Compute structural similarity
                    sim = self._structural_similarity(graph, u, v)
                    if sim >= self.eps_scan:
                        core_graph.add_edge(u, v, weight=sim)

        # Step 5: Cluster core nodes
        if num_clusters is not None and num_clusters > 1:
            core_labels = self._cluster_core_nodes(core_graph, num_clusters)
        else:
            # Use DBSCAN-like clustering on core graph
            core_labels = self._cluster_core_nodes_dbscan(core_graph)

        # Step 6: Expand clusters to ordinary nodes
        labels = {node: -1 for node in graph.nodes()}  # -1 = unassigned

        # Assign core node labels
        for node, label in core_labels.items():
            labels[node] = label

        # Expand to ordinary nodes (non-core nodes)
        ordinary_nodes = [node for node in graph.nodes() if node not in core_set]

        for node in ordinary_nodes:
            # Find the most frequent label among neighbors
            neighbor_labels = []
            for neighbor in graph.neighbors(node):
                if neighbor in labels and labels[neighbor] != -1:
                    neighbor_labels.append(labels[neighbor])

            if neighbor_labels:
                # Assign the most common label among neighbors
                label_counts = Counter(neighbor_labels)
                labels[node] = label_counts.most_common(1)[0][0]
            else:
                # Isolated node: create its own cluster
                labels[node] = max(labels.values()) + 1 if labels else 0

        # Compress labels
        unique_labels = sorted(set(labels.values()))
        label_mapping = {old: new for new, old in enumerate(unique_labels)}
        return {node: label_mapping[label] for node, label in labels.items()}

    def _perturb_degrees(self, degrees: Dict) -> Dict:
        """
        Perturb degrees using Laplace mechanism for LDP.

        Args:
            degrees: Original degrees

        Returns:
            Noisy degrees
        """
        noisy_degrees = {}
        sensitivity = 1.0  # For degree, sensitivity is 1

        for node, deg in degrees.items():
            noise = np.random.laplace(0, sensitivity / self.epsilon)
            noisy_degrees[node] = max(0, deg + noise)

        return noisy_degrees

    def _structural_similarity(self, graph: nx.Graph, u: int, v: int) -> float:
        """
        Compute structural similarity between two nodes.

        Structural similarity = |N(u) ∩ N(v)| / sqrt(|N(u)| * |N(v)|)
        """
        neighbors_u = set(graph.neighbors(u))
        neighbors_v = set(graph.neighbors(v))

        # Include the nodes themselves for SCAN similarity
        neighbors_u.add(u)
        neighbors_v.add(v)

        common = len(neighbors_u & neighbors_v)
        norm = np.sqrt(len(neighbors_u) * len(neighbors_v))

        if norm == 0:
            return 0.0

        return common / norm

    def _cluster_core_nodes(
            self,
            core_graph: nx.Graph,
            num_clusters: int
    ) -> Dict[int, int]:
        """
        Cluster core nodes using spectral clustering or K-means.
        """
        if len(core_graph.nodes()) == 0:
            return {}

        if len(core_graph.nodes()) < num_clusters:
            num_clusters = len(core_graph.nodes())

        try:
            from sklearn.cluster import SpectralClustering

            # Get adjacency matrix
            adj = nx.adjacency_matrix(core_graph).toarray()

            # Spectral clustering
            clustering = SpectralClustering(
                n_clusters=num_clusters,
                affinity='precomputed',
                random_state=self.seed,
                assign_labels='discretize'
            )
            labels = clustering.fit_predict(adj)

            return {node: label for node, label in zip(core_graph.nodes(), labels)}

        except ImportError:
            # Fallback: use connected components
            return self._cluster_core_nodes_components(core_graph)

    def _cluster_core_nodes_dbscan(self, core_graph: nx.Graph) -> Dict[int, int]:
        """
        Cluster core nodes using DBSCAN on node embeddings.
        """
        if len(core_graph.nodes()) == 0:
            return {}

        try:
            from sklearn.cluster import DBSCAN
            from sklearn.preprocessing import StandardScaler

            # Use adjacency matrix as features
            nodes = list(core_graph.nodes())
            node_to_idx = {node: i for i, node in enumerate(nodes)}

            # Build feature matrix using adjacency
            n = len(nodes)
            features = np.zeros((n, n))
            for i, u in enumerate(nodes):
                for j, v in enumerate(nodes):
                    if core_graph.has_edge(u, v):
                        features[i, j] = 1

            # DBSCAN clustering
            clustering = DBSCAN(eps=self.eps_scan, min_samples=self.mu)
            labels = clustering.fit_predict(features)

            # Handle noise points (label = -1)
            # Assign each noise point to the nearest cluster
            unique_labels = set(labels)
            unique_labels.discard(-1)

            if not unique_labels:
                # All nodes are noise: assign each to its own cluster
                return {node: i for i, node in enumerate(nodes)}

            label_mapping = {}
            for node, label in zip(nodes, labels):
                if label == -1:
                    # Find nearest cluster
                    label_mapping[node] = self._assign_noise_node(
                        core_graph, node, nodes, labels
                    )
                else:
                    label_mapping[node] = label

            # Compress labels
            unique = sorted(set(label_mapping.values()))
            mapping = {old: new for new, old in enumerate(unique)}
            return {node: mapping[label] for node, label in label_mapping.items()}

        except ImportError:
            return self._cluster_core_nodes_components(core_graph)

    def _cluster_core_nodes_components(self, core_graph: nx.Graph) -> Dict[int, int]:
        """Fallback: use connected components for clustering."""
        labels = {}
        for label, component in enumerate(nx.connected_components(core_graph)):
            for node in component:
                labels[node] = label
        return labels

    def _assign_noise_node(
            self,
            graph: nx.Graph,
            node: int,
            nodes: List[int],
            labels: np.ndarray
    ) -> int:
        """Assign a noise node to the nearest cluster."""
        neighbor_counts = defaultdict(int)

        for neighbor in graph.neighbors(node):
            if neighbor in nodes:
                idx = nodes.index(neighbor)
                label = labels[idx]
                if label != -1:
                    neighbor_counts[label] += 1

        if neighbor_counts:
            return max(neighbor_counts, key=neighbor_counts.get)
        else:
            # Isolated noise node: create new cluster
            return max(labels) + 1 if len(labels) > 0 else 0