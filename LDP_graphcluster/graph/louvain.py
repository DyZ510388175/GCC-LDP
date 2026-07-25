import networkx as nx
import numpy as np
from sklearn.metrics.cluster import normalized_mutual_info_score
import matplotlib.pyplot as plt

class LouvainAlgorithm:
    def __init__(self, graph):
        self.graph = graph
    def run(self):
        # Initialize each node in its own community
        partition = {node: node for node in self.graph.nodes()}
        modularity = -1  # Initial modularity value
        while True:
            # Phase 1: Local moving of nodes to maximize modularity
            moved = False
            for node in self.graph.nodes():
                current_community = partition[node]
                best_community = current_community
                max_delta_q = 0
                for neighbor in self.graph.neighbors(node):
                    if partition[neighbor] != current_community:
                        # Calculate the change in modularity if node moves to neighbor's community
                        delta_q = (
                            self.graph.degree(node, weight="weight")
                            - self.graph.degree(node, weight="weight")
                            * self.graph.degree(neighbor, weight="weight")
                            / (2 * self.graph.size(weight="weight"))
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

    def calculate_modularity(self, communities):
        modularity = 0
        m = self.graph.size(weight="weight")
        for community, nodes in communities.items():
            for node in nodes:
                ki = self.graph.degree(node, weight="weight")
                community_sum = sum(
                    self.graph.degree(neighbor, weight="weight") for neighbor in nodes
                )
                modularity += (ki - (community_sum / (2 * m))) / (2 * m)
        return modularity

if __name__ == '__main__':

    # 创建一个networkx图
    # G = nx.Graph()
    # G.add_edges_from([(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 5)])
    G = nx.karate_club_graph()

    # 假设每个节点的真实社区分配
    # ground_truth = [0, 0, 0, 1, 1, 2, 2, 2]
    ground_truth = [0, 0, 1, 2, 2, 2]

    # 运行Louvain算法
    louvain_algorithm = LouvainAlgorithm(G)
    partition = louvain_algorithm.run()
    print(partition)


    # 绘制结果图
    pos = nx.spring_layout(G)
    colors = [partition[node] for node in G.nodes()]

    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, node_color=colors, with_labels=True, cmap=plt.cm.get_cmap("viridis", max(partition.values()) + 1))
    plt.title("Louvain Algorithm Result")
    plt.show()
