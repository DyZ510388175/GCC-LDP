import networkx as nx
import community
import numpy as np
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

class LouvainClustering:
    def __init__(self, adjacency_matrix):
        self.adjacency_matrix = adjacency_matrix

    def run(self):
        graph = nx.Graph(self.adjacency_matrix)
        partition = community.best_partition(graph)
        return partition

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
