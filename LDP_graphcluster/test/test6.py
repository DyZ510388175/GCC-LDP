import networkx as nx
from collections import Counter

# 创建 Karate Club 图
karate_graph = nx.karate_club_graph()
print(nx.adjacency_matrix(karate_graph))

# 阈值，用于确定频数大于阈值的对应节点
threshold = 5

# 初始化压缩集合，每个节点作为一个单独的集合
compressed_sets = [{node} for node in karate_graph.nodes()]


# 计算节点的邻接向量
def calculate_adjacency_vector(node, compressed_sets):
    adjacency_vector = [1 if karate_graph.has_edge(node, n) else 0 for compressed_set in compressed_sets for n in
                        compressed_set]
    return adjacency_vector


# 计算邻接向量频数
def calculate_adjacency_frequencies(compressed_sets):
    adjacency_frequencies = Counter()

    for i, compressed_set in enumerate(compressed_sets):
        adjacency_vector = calculate_adjacency_vector(i, compressed_sets)
        for j, val in enumerate(adjacency_vector):
            if val == 1:
                adjacency_frequencies[j] += 1

    return adjacency_frequencies


# 计算成对节点的频数
def calculate_pair_frequencies(compressed_sets, pair_nodes):
    pair_frequencies = Counter()

    for i, compressed_set in enumerate(compressed_sets):
        adjacency_vector = calculate_adjacency_vector(i, compressed_sets)
        for pair in pair_nodes:
            j, k = pair
            if adjacency_vector[j] == adjacency_vector[k] == 1:
                pair_frequencies[pair] += 1

    return pair_frequencies


# 计算邻接向量频数，找出频数大于阈值的节点
adjacency_frequencies = calculate_adjacency_frequencies(compressed_sets)
nodes_above_threshold = [node for node, freq in adjacency_frequencies.items() if freq > threshold]

# 将频数大于阈值的对应节点两两组成对节点
pair_nodes = [(node1, node2) for idx, node1 in enumerate(nodes_above_threshold) for node2 in
              nodes_above_threshold[idx + 1:]]

# 计算成对节点的频数
pair_frequencies = calculate_pair_frequencies(compressed_sets, pair_nodes)

# 打印成对节点和其频数
for pair, freq in pair_frequencies.items():
    print(f"Pair {pair}: Frequency {freq}")
