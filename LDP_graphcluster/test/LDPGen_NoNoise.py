import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import random

class LDPGen_NoNoise:
    def __init__(self, graph, num_clusters):
        self.graph = graph
        self.num_clusters = num_clusters
        self.num_nodes = len(graph)
        self.clusters = self.initialize_clusters()
        self.degree_vectors = self.calculate_degree_vectors()
        self.cluster_centers = self.initialize_cluster_centers()

    def initialize_clusters(self):
        nodes_per_cluster = self.num_nodes // self.num_clusters
        clusters = []
        nodes = list(self.graph.nodes())
        for _ in range(self.num_clusters - 1):
            cluster = np.random.choice(nodes, size=nodes_per_cluster, replace=False)
            clusters.append(cluster)
            nodes = [node for node in nodes if node not in cluster]
        clusters.append(nodes)
        return clusters

    def calculate_degree_vectors(self):
        degree_vectors = np.zeros((self.num_nodes, self.num_clusters))
        for node in self.graph.nodes():
            degree_vector = np.zeros(self.num_clusters)
            for i, cluster in enumerate(self.clusters):
                degree_vector[i] = sum(1 for neighbor in self.graph.neighbors(node) if neighbor in cluster)
            degree_vectors[node] = tuple(degree_vector)
        return degree_vectors

    def initialize_cluster_centers(self):
        cluster_centers = []
        for cluster_nodes in self.clusters:
            center_node = np.random.choice(cluster_nodes)
            cluster_centers.append(self.degree_vectors[center_node])
        return np.array(cluster_centers)

    def kmeans(self, max_iterations=7):
        for _ in range(max_iterations):
            new_clusters = [[] for _ in range(self.num_clusters)]

            for node_idx in range(self.num_nodes):
                distances = np.sum(np.abs(self.cluster_centers - self.degree_vectors[node_idx]), axis=1)
                min_dist_idx = np.argmin(distances)
                new_clusters[min_dist_idx].append(node_idx)

            new_cluster_centers = []
            for cluster_nodes in new_clusters:
                if cluster_nodes:
                    cluster_vectors = self.degree_vectors[cluster_nodes]
                    cluster_center = np.mean(cluster_vectors, axis=0) if len(cluster_nodes) > 0 else np.zeros(self.num_clusters)
                    new_cluster_centers.append(cluster_center)
                else:
                    new_cluster_centers.append(random.choice(self.degree_vectors))
            if np.array_equal(new_clusters, self.clusters) and np.allclose(new_cluster_centers, self.cluster_centers):
                break

            self.clusters = new_clusters
            self.cluster_centers = np.array(new_cluster_centers)

def draw_spring(G, com):
    pos = nx.spring_layout(G)  # 节点的布局为spring型
    NodeId = list(G.nodes())
    node_size = [G.degree(i) ** 1.2 * 90 for i in NodeId]  # 节点大小
    plt.figure(figsize=(8, 6))  # 图片大小
    nx.draw(G, pos, with_labels=True, node_size=node_size, node_color='w', node_shape='.')
    color_list = ['pink', 'orange', 'r', 'g', 'b', 'y', 'm', 'gray', 'black', 'c', 'brown']
    for i in range(len(com)):
        nx.draw_networkx_nodes(G, pos, nodelist=com[i], node_color=color_list[i])
    plt.show()

# Example usage
G = nx.Graph()
G.add_edges_from([(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)])

num_clusters = 2

graph_clustering = LDPGen_NoNoise(G, num_clusters)
graph_clustering.kmeans()

for i, cluster in enumerate(graph_clustering.clusters):
    print(f"Cluster {i+1}: {cluster}")

# draw_spring(G, list(graph_clustering.clusters))
