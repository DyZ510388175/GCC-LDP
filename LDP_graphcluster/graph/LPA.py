"""
Label Propagation Algorithm (LPA) for community detection.

LPA is a simple and fast community detection algorithm where each node
adopts the most frequent label among its neighbors. The algorithm is
asynchronous and probabilistic.

Reference:
- Raghavan, U. N., Albert, R., & Kumara, S. (2007). Near linear time
  algorithm to detect community structures in large-scale networks.
  Physical Review E, 76(3), 036106.
"""

import networkx as nx
import numpy as np
from typing import List, Dict, Set, Optional
import random
from collections import Counter


class LabelPropagation:
    """
    Label Propagation Algorithm for community detection.

    The algorithm initializes each node with a unique label and iteratively
    updates each node's label to the most frequent label among its neighbors.
    """

    def __init__(self, max_iterations: int = 100, seed: int = 42):
        """
        Initialize the Label Propagation algorithm.

        Args:
            max_iterations: Maximum number of iterations
            seed: Random seed for reproducibility
        """
        self.max_iterations = max_iterations
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)

    def cluster(
            self,
            graph: nx.Graph,
            num_clusters: Optional[int] = None
    ) -> Dict[int, int]:
        """
        Detect communities using label propagation.

        Note: LPA does not require specifying the number of clusters;
        the number of communities is determined automatically.

        Args:
            graph: Input graph
            num_clusters: Ignored for LPA (communities are determined automatically)

        Returns:
            Dictionary mapping node to cluster label
        """
        # Initialize labels: each node gets a unique label
        labels = {node: i for i, node in enumerate(graph.nodes())}

        # Get nodes in random order for each iteration
        nodes = list(graph.nodes())

        for iteration in range(self.max_iterations):
            # Shuffle nodes for asynchronous update
            random.shuffle(nodes)

            changed = False

            for node in nodes:
                # Get labels of neighbors
                neighbor_labels = []
                for neighbor in graph.neighbors(node):
                    if neighbor in labels:
                        neighbor_labels.append(labels[neighbor])

                if not neighbor_labels:
                    continue

                # Find the most frequent label among neighbors
                label_counts = Counter(neighbor_labels)
                max_count = max(label_counts.values())

                # Get all labels with the maximum count
                top_labels = [lbl for lbl, cnt in label_counts.items() if cnt == max_count]

                # Randomly select one of the top labels
                new_label = random.choice(top_labels)

                if labels[node] != new_label:
                    labels[node] = new_label
                    changed = True

            # Stop if no label changed
            if not changed:
                break

        # Compress labels to consecutive integers
        unique_labels = sorted(set(labels.values()))
        label_mapping = {old: new for new, old in enumerate(unique_labels)}
        return {node: label_mapping[label] for node, label in labels.items()}


class FastLabelPropagation:
    """
    Fast Label Propagation Algorithm (NetworkX implementation wrapper).

    Uses NetworkX's built-in asynchronous label propagation for better
    performance on large graphs.
    """

    def __init__(self, seed: int = 42):
        """
        Initialize the Fast Label Propagation algorithm.

        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)

    def cluster(
            self,
            graph: nx.Graph,
            num_clusters: Optional[int] = None
    ) -> Dict[int, int]:
        """
        Detect communities using NetworkX's fast label propagation.

        Args:
            graph: Input graph
            num_clusters: Ignored

        Returns:
            Dictionary mapping node to cluster label
        """
        try:
            # Use NetworkX's asynchronous label propagation
            from networkx.algorithms.community import asyn_lpa_communities

            communities = list(asyn_lpa_communities(graph, seed=self.seed))

            # Assign labels
            labels = {}
            for label, community in enumerate(communities):
                for node in community:
                    labels[node] = label

            return labels

        except ImportError:
            # Fallback to custom implementation
            lpa = LabelPropagation(seed=self.seed)
            return lpa.cluster(graph)