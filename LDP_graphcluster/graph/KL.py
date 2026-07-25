"""
Kernighan-Lin (KL) graph partitioning algorithm for community detection.

The Kernighan-Lin algorithm is a heuristic for finding partitions of graphs.
It iteratively swaps pairs of nodes between two communities to minimize
the edge cut between them.

Reference:
- Kernighan, B. W., & Lin, S. (1970). An efficient heuristic procedure for
  partitioning graphs. The Bell system technical journal, 49(2), 291-307.
"""

import networkx as nx
import numpy as np
from typing import List, Tuple, Dict, Optional, Set
import random


class KernighanLin:
    """
    Kernighan-Lin graph partitioning algorithm.

    This implementation supports partitioning a graph into k communities
    through recursive bisection.
    """

    def __init__(self, max_iterations: int = 100, seed: int = 42):
        """
        Initialize the Kernighan-Lin algorithm.

        Args:
            max_iterations: Maximum number of iterations per bisection
            seed: Random seed for reproducibility
        """
        self.max_iterations = max_iterations
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)

    def bisection(
            self,
            graph: nx.Graph,
            initial_partition: Optional[Tuple[Set, Set]] = None
    ) -> Tuple[Set, Set]:
        """
        Partition a graph into two communities using the KL algorithm.

        Args:
            graph: Input graph
            initial_partition: Optional initial partition (A, B)

        Returns:
            Tuple of two sets representing the bisection
        """
        nodes = list(graph.nodes())
        n = len(nodes)

        # Initialize partition if not provided
        if initial_partition is None:
            # Random bisection
            shuffled = nodes.copy()
            random.shuffle(shuffled)
            mid = n // 2
            A = set(shuffled[:mid])
            B = set(shuffled[mid:])
        else:
            A, B = initial_partition
            A = set(A)
            B = set(B)

        # Ensure both partitions are non-empty
        if not A or not B:
            # Fallback to random split
            shuffled = nodes.copy()
            random.shuffle(shuffled)
            mid = n // 2
            A = set(shuffled[:max(1, mid)])
            B = set(shuffled[mid:])
            if not B:
                B = {shuffled[-1]}
                A.remove(shuffled[-1])

        best_gain = 0
        best_A, best_B = A.copy(), B.copy()

        for iteration in range(self.max_iterations):
            # Compute gains for all nodes
            gains = self._compute_gains(graph, A, B)

            # Sort nodes by gain
            sorted_nodes = sorted(gains.keys(), key=lambda x: gains[x], reverse=True)

            # Track swapped nodes
            swapped = set()
            total_gain = 0
            current_A, current_B = A.copy(), B.copy()

            # Perform sequence of swaps
            for _ in range(min(len(A), len(B))):
                # Find best pair to swap
                best_pair = None
                best_pair_gain = -float('inf')

                for u in current_A:
                    if u in swapped:
                        continue
                    for v in current_B:
                        if v in swapped:
                            continue
                        # Gain of swapping u and v
                        gain = gains.get(u, 0) + gains.get(v, 0) - 2 * self._edge_weight(graph, u, v)
                        if gain > best_pair_gain:
                            best_pair_gain = gain
                            best_pair = (u, v)

                if best_pair is None:
                    break

                u, v = best_pair
                # Perform swap
                current_A.remove(u)
                current_B.remove(v)
                current_A.add(v)
                current_B.add(u)
                swapped.add(u)
                swapped.add(v)

                total_gain += best_pair_gain

                # Update gains for affected nodes
                gains = self._compute_gains(graph, current_A, current_B)

            # Check if this iteration improved the partition
            if total_gain > best_gain:
                best_gain = total_gain
                best_A, best_B = current_A.copy(), current_B.copy()
            else:
                # No improvement, stop
                break

        return best_A, best_B

    def _compute_gains(self, graph: nx.Graph, A: Set, B: Set) -> Dict:
        """
        Compute the gain for each node.

        Gain of a node = external edges - internal edges
        Moving a node with high gain to the other community reduces the cut.
        """
        gains = {}

        for node in A:
            internal = sum(1 for neighbor in graph.neighbors(node) if neighbor in A)
            external = sum(1 for neighbor in graph.neighbors(node) if neighbor in B)
            gains[node] = external - internal

        for node in B:
            internal = sum(1 for neighbor in graph.neighbors(node) if neighbor in B)
            external = sum(1 for neighbor in graph.neighbors(node) if neighbor in A)
            gains[node] = external - internal

        return gains

    def _edge_weight(self, graph: nx.Graph, u: int, v: int) -> float:
        """Get edge weight between u and v (1 if exists, 0 otherwise)."""
        return 1.0 if graph.has_edge(u, v) else 0.0

    def cluster(
            self,
            graph: nx.Graph,
            num_clusters: int = 2
    ) -> Dict[int, int]:
        """
        Partition the graph into k communities using recursive bisection.

        Args:
            graph: Input graph
            num_clusters: Number of clusters to produce

        Returns:
            Dictionary mapping node to cluster label (0 to num_clusters-1)
        """
        if num_clusters <= 1:
            return {node: 0 for node in graph.nodes()}

        # Use recursive bisection
        # Start with all nodes in one partition
        all_nodes = set(graph.nodes())
        partitions = [all_nodes]

        while len(partitions) < num_clusters:
            # Find the largest partition to split
            largest_idx = max(range(len(partitions)), key=lambda i: len(partitions[i]))
            largest = partitions[largest_idx]

            if len(largest) < 2:
                break

            # Create subgraph for this partition
            subgraph = graph.subgraph(largest)

            # Perform bisection
            A, B = self.bisection(subgraph)

            # Replace the largest partition with A and B
            partitions.pop(largest_idx)
            if A:
                partitions.append(A)
            if B:
                partitions.append(B)

        # Assign labels
        labels = {}
        for label, partition in enumerate(partitions):
            for node in partition:
                labels[node] = label

        # Assign any remaining nodes to the nearest cluster
        for node in graph.nodes():
            if node not in labels:
                # Find the cluster with the most connections
                neighbor_counts = {}
                for label, partition in enumerate(partitions):
                    count = sum(1 for neighbor in graph.neighbors(node) if neighbor in partition)
                    neighbor_counts[label] = count
                labels[node] = max(neighbor_counts, key=neighbor_counts.get)

        return labels