import networkx as nx
import numpy as np
import community  # 需要安装 python-louvain 库

# 创建一个networkx图（这里只是一个示例，你需要根据你的数据集来创建图）
G = nx.Graph()
G.add_edges_from([(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 5)])

# 使用Louvain算法进行社区划分
partition = community.best_partition(G)

# 将划分结果转化为列表形式的社区标签
community_labels = list(partition.values())

# 输出格式为列表的字符串
ground_truth_str = "ground_truth = " + str(community_labels)
print(ground_truth_str)
