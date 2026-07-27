import networkx as nx
import community
import numpy as np
from typing import Dict, Optional, List, Union
from scipy.sparse import random

class RRPerturbation:
    def __init__(self, adjacency_matrix, privacy_budget):
        self.adjacency_matrix = adjacency_matrix
        self.privacy_budget = privacy_budget

    def perturb(self):
        perturbed_adjacency_matrix = self.adjacency_matrix.copy()
        num_nodes = perturbed_adjacency_matrix.shape[0]

        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                original_value = perturbed_adjacency_matrix[i, j]
                p = np.e**self.privacy_budget/(1+np.e**self.privacy_budget)
                if original_value == 1:
                    perturbed_adjacency_matrix[i, j] = np.random.choice([1, 0], p=[p, 1 - p])
                    perturbed_adjacency_matrix[j, i] = perturbed_adjacency_matrix[i, j]
                else:
                    perturbed_adjacency_matrix[i, j] = np.random.choice([1, 0], p=[1 - p, p])
                    perturbed_adjacency_matrix[j, i] = perturbed_adjacency_matrix[i, j]

        return perturbed_adjacency_matrix

class DegreePerturbation:
    """
    Laplace mechanism for degree perturbation.

    Each node's degree is perturbed by adding Laplace noise:
        d̃ = d + Lap(0, Δf/ε)

    where Δf = 1 (sensitivity of degree query) and ε is the privacy budget.

    This satisfies ε-LDP for degree information.
    """

    def __init__(self, degrees, privacy_budget):
        """
        Initialize the Laplace degree perturbation mechanism.

        Args:
            degrees: Array of true node degrees (length n)
            privacy_budget: Privacy budget for degree perturbation (ε_deg > 0)
        """
        self.degrees = np.array(degrees)
        self.privacy_budget = privacy_budget
        self.n = len(degrees)
        self.sensitivity = 1.0  # Degree sensitivity is 1
        self.scale = self.sensitivity / privacy_budget

    def perturb(self):
        """
        Perturb node degrees using the Laplace mechanism.

        Returns:
            Perturbed degree values (clipped to valid range [0, n-1])
        """
        # Add Laplace noise
        noise = np.random.laplace(0, self.scale, self.n)
        perturbed = self.degrees + noise

        # Clip to valid degree range [0, n-1]
        perturbed = np.clip(perturbed, 0, self.n - 1)

        # Round to integers (degrees must be integers)
        perturbed = np.round(perturbed).astype(int)

        return perturbed


class LouvainClustering:
    """
    Louvain community detection on a graph with optional perturbed degree information.

    If perturbed_degrees is provided, it uses these values instead of
    the graph's internal degrees in modularity calculations.
    """

    def __init__(
        self,
        adjacency_matrix: np.ndarray,
        perturbed_degrees: Optional[Dict[int, float]] = None
    ):
        """
        Initialize Louvain clustering.

        Args:
            adjacency_matrix: n x n adjacency matrix
            perturbed_degrees: Dict mapping node -> perturbed degree value.
                               If None, uses graph's internal degrees.
        """
        self.adjacency_matrix = adjacency_matrix
        self.perturbed_degrees = perturbed_degrees
        self.graph = nx.Graph(adjacency_matrix)
        self.m = self.graph.size(weight="weight")

    def get_degree(self, node: int) -> float:
        """
        Get the degree of a node, using perturbed degree if available.

        Args:
            node: Node identifier

        Returns:
            Degree value (perturbed if available, otherwise internal)
        """
        if self.perturbed_degrees is not None and node in self.perturbed_degrees:
            return float(self.perturbed_degrees[node])
        else:
            return float(self.graph.degree(node, weight="weight"))

    def run(self) -> Dict[int, int]:
        """
        Run Louvain community detection using perturbed degrees if available.

        Returns:
            Dictionary mapping node -> community label
        """
        # Initialize each node in its own community
        partition = {node: node for node in self.graph.nodes()}
        modularity = -1

        while True:
            # Phase 1: Local moving of nodes to maximize modularity
            moved = False
            for node in self.graph.nodes():
                current_community = partition[node]
                best_community = current_community
                max_delta_q = 0

                deg_node = self.get_degree(node)

                for neighbor in self.graph.neighbors(node):
                    if partition[neighbor] != current_community:
                        deg_neighbor = self.get_degree(neighbor)
                        delta_q = (
                            deg_node
                            - deg_node * deg_neighbor / (2 * self.m + 1e-8)
                        )
                        if delta_q > max_delta_q:
                            max_delta_q = delta_q
                            best_community = partition[neighbor]

                if best_community != current_community:
                    partition[node] = best_community
                    moved = True

            # Phase 2: Aggregate nodes into communities
            communities = {}
            for node, community in partition.items():
                if community not in communities:
                    communities[community] = [node]
                else:
                    communities[community].append(node)

            # Calculate modularity
            new_modularity = self.calculate_modularity(communities)
            if new_modularity - modularity < 1e-6:
                break

            modularity = new_modularity

        return partition

    def calculate_modularity(self, communities: Dict[int, List[int]]) -> float:
        """
        Calculate modularity using perturbed degrees if available.

        Args:
            communities: Dictionary mapping community -> list of nodes

        Returns:
            Modularity value
        """
        modularity = 0
        m = self.m

        if m == 0:
            return 0

        for community, nodes in communities.items():
            community_deg_sum = sum(self.get_degree(node) for node in nodes)
            for node in nodes:
                deg_node = self.get_degree(node)
                modularity += (deg_node / (2 * m)) - (community_deg_sum / (2 * m)) ** 2

        return modularity

if __name__ == '__main__':

    # 创建一个大规模的networkx图（这里只是一个示例，你需要根据你的数据集来创建图）
    # G = nx.erdos_renyi_graph(n=10000, p=0.01)
    G = nx.karate_club_graph()
    adjacency_matrix = nx.adjacency_matrix(G).toarray()

    # 隐私预算（假设为0.1，你可以根据实际情况进行调整）
    privacy_budget = 0.1

    # 创建 EpsilonRRPerturbation 实例并进行扰动
    rr_perturber = RRPerturbation(adjacency_matrix, privacy_budget)
    perturbed_adjacency_matrix = rr_perturber.perturb()

    # 创建 LouvainClustering 实例
    clustering_algo = LouvainClustering(perturbed_adjacency_matrix)

    # 运行 Louvain 算法进行社区划分
    partition = clustering_algo.run()

    # 输出社区标签
    print("Community Labels:", partition)
