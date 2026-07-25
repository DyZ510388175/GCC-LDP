import networkx as nx
import community
from sklearn.metrics.cluster import normalized_mutual_info_score, adjusted_rand_score, adjusted_mutual_info_score
from sklearn.metrics import f1_score
from scipy.stats import entropy

class CommunityMetrics:
    def __init__(self, graph, predicted_partition, ground_truth=None):
        self.graph = graph
        self.predicted_partition = predicted_partition
        self.ground_truth = ground_truth

    def modularity(self):
        return community.modularity(self.predicted_partition, self.graph)

    def normalized_mutual_info(self):
        if self.ground_truth is None:
            raise ValueError("Ground truth labels are required for NMI calculation.")
        return normalized_mutual_info_score(self.ground_truth, list(self.predicted_partition.values()))

    def f1(self):
        if self.ground_truth is None:
            raise ValueError("Ground truth labels are required for F1 calculation.")
        return f1_score(self.ground_truth, list(self.predicted_partition.values()), average='weighted')

    def adjusted_rand_index(self):
        if self.ground_truth is None:
            raise ValueError("Ground truth labels are required for ARI calculation.")
        return adjusted_rand_score(self.ground_truth, list(self.predicted_partition.values()))

    def adjusted_mutual_info(self):
        if self.ground_truth is None:
            raise ValueError("Ground truth labels are required for AMI calculation.")
        return adjusted_mutual_info_score(self.ground_truth, list(self.predicted_partition.values()))

    def relative_entropy(self):
        if self.ground_truth is None:
            raise ValueError("Ground truth labels are required for RE calculation.")
        unique_labels = len(set(self.predicted_partition.values()))
        predicted_probs = [list(self.predicted_partition.values()).count(i) / len(self.predicted_partition) for i in range(unique_labels)]
        ground_truth_probs = [self.ground_truth.count(i) / len(self.ground_truth) for i in range(unique_labels)]
        return entropy(ground_truth_probs, predicted_probs)

if __name__ == '__main__':

    # Create a networkx graph (this is just an example, you need to create the graph based on your dataset)
    G = nx.Graph()
    G.add_edges_from([(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 5)])

    # Use Louvain algorithm for community detection
    partition = community.best_partition(G)

    # Ground truth labels (provide your own ground truth labels)
    ground_truth = [0, 0, 1, 2, 2, 2]

    # Create CommunityMetrics instance
    metrics_calculator = CommunityMetrics(G, partition, ground_truth)

    # Calculate and output metrics
    print("Modularity:", metrics_calculator.modularity())
    print("Normalized Mutual Information:", metrics_calculator.normalized_mutual_info())
    print("F1 Score:", metrics_calculator.f1())
    print("Adjusted Rand Index:", metrics_calculator.adjusted_rand_index())
    print("Adjusted Mutual Information:", metrics_calculator.adjusted_mutual_info())
    print("Relative Entropy:", metrics_calculator.relative_entropy())
