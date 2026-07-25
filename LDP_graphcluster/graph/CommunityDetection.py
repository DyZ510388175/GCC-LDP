import networkx as nx
import community  # 需要安装 python-louvain 库

class CommunityDetection:
    def __init__(self, graph):
        self.graph = graph

    def louvain_partition(self):
        partition = community.best_partition(self.graph)
        return list(partition.values())

if __name__ == '__main__':

    # 创建一个networkx图（这里只是一个示例，你需要根据你的数据集来创建图）
    G = nx.Graph()
    G.add_edges_from([(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 5)])

    # 创建 CommunityDetection 的实例
    community_detector = CommunityDetection(G)

    # 使用 Louvain 算法进行社区划分
    community_labels = community_detector.louvain_partition()

    # 输出社区标签
    print(community_labels)
