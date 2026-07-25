import networkx as nx
import community as community_louvain
import matplotlib.pyplot as plt
from networkx.algorithms.community import kernighan_lin_bisection

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

G = nx.karate_club_graph()
com = list(kernighan_lin_bisection(G))
print(com)
print('社区数量', len(com))
# 社区数量 2
draw_spring(G, com)