import networkx as nx
import numpy as np

class GraphConverter:
    def __init__(self, graph=None, adjacency_matrix=None):
        if graph is not None:
            self.graph = graph
        elif adjacency_matrix is not None:
            self.graph = nx.Graph(adjacency_matrix)

    def create_karate_club_graph(self):
        self.graph = nx.karate_club_graph()
        return self.graph

    def get_adjacency_matrix(self):
        return nx.adjacency_matrix(self.graph).toarray()

if __name__ == '__main__':

    # 创建 GraphConverter 实例
    converter = GraphConverter()

    # 创建 karate_club 图
    karate_graph = converter.create_karate_club_graph()

    # 获取邻接矩阵
    adj_matrix = converter.get_adjacency_matrix()

    print("Karate Club Graph:")
    print(karate_graph.nodes())
    print(karate_graph.edges())

    print("\nAdjacency Matrix:")
    print(adj_matrix)
