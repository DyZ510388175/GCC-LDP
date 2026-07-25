import networkx as nx
import networkx.algorithms as algos
import matplotlib.pyplot as plt

from graph.GraphConverter import GraphConverter

"""
1 创建图形
    G = nx.Graph()
2 清空图
    G.clear()
3 karate数据集
    G=nx.karate_club_graph()
4 节点数
    G.number_of_nodes()
"""
# ../dataset/facebook_combined.txt
G = nx.karate_club_graph()

# 创建 GraphConverter 实例
converter = GraphConverter()
# 创建 karate_club 图
karate_graph = converter.create_karate_club_graph()
# 获取邻接矩阵
adj_matrix = converter.get_adjacency_matrix()
print(nx.adjacency_matrix(G))
print(nx.adjacency_matrix(G).toarray())

for v in G:
    print(G.nodes[v])

# G=nx.read_edgelist('../dataset/karate2.txt', comments='#', create_using=nx.Graph())

# print(G.number_of_nodes())
# print(cluster)

# nx.draw(G, with_labels=True)
data = G[0]
nx.draw(G, with_labels=True,node_color=data.y)
# plt.show()

