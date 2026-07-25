import random
import networkx as nx

'''使其按着度从大到小的顺序截取节点。'''
# 假设您有一个名为 G 的社交图，可以使用 nx.read_edgelist 读取图数据
# gemsec_deezer facebook_combined Email-Enron CA-CondMat musae_ES_edges musae_git_edges CA-HepTh musae_PTBR_edges
# G = nx.read_edgelist('../dataset/facebook_combined.txt')
filename = 'musae_PTBR_edges'
G = nx.read_edgelist('C:/Users/HP/Desktop/数据集/原数据集/'+filename+'.txt')

# 获取所有节点
all_nodes = list(G.nodes())
node_degrees = dict(G.degree())

# 按节点的度从大到小排序
sorted_nodes = sorted(all_nodes, key=lambda x: -node_degrees[x])

# 计算要采样的节点数量（10%）
sample_size = int(len(sorted_nodes) * 0.03)

# 随机抽样前sample_size个节点
sampled_nodes = random.sample(sorted_nodes[:sample_size], sample_size)

# 构建包含采样节点的子图
sampled_subgraph = G.subgraph(sampled_nodes).copy()  # 创建子图的副本

# 获取采样节点的邻居节点
sampled_neighbors = set()
for node in sampled_nodes:
    sampled_neighbors.update(list(G.neighbors(node)))

# 将采样节点及其邻居节点放入一个集合中
sampled_nodes_and_neighbors = set(sampled_nodes)
# sampled_nodes_and_neighbors.update(sampled_neighbors)
print('len(sampled_nodes_and_neighbors):', len(sampled_nodes_and_neighbors))

# 删除非采样节点与非采样节点之间的边
edges_to_remove = []
for node1, node2 in G.edges():
    if node1 not in sampled_nodes_and_neighbors or node2 not in sampled_nodes_and_neighbors:
        edges_to_remove.append((node1, node2))

G.remove_edges_from(edges_to_remove)

# 获取节点顺序
node_order = list(sampled_subgraph.nodes())
print('len(node_order):', len(node_order))

# 创建节点映射，将节点重新编号为连续的0开始的整数
node_mapping = {old_node: idx for idx, old_node in enumerate(node_order)}

# 生成重新编号后的边数据
new_edges = [(node_mapping[edge[0]], node_mapping[edge[1]]) for edge in sampled_subgraph.edges()]
print('len(sampled_subgraph.edges()):', len(sampled_subgraph.edges()))
print('len(new_edges):', len(new_edges))

# 创建存储边数据的文件
# filename = "../dataset/sampled_edges.txt"
path = 'C:/Users/HP/Desktop/数据集/采样数据集/'+filename+'_sample.txt'

# 打开文件以写入模式
with open(path, 'w') as file:
    # 按节点顺序将重新编号后的边数据写入文件中，每行一个边
    for edge in new_edges:
        file.write(f"{edge[0]} {edge[1]}\n")

print(f"Sampled edges saved to {filename}")
