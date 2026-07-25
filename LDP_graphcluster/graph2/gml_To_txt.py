import networkx as nx

# football

# 从 GML 文件中读取图数据
G = nx.read_gml('C:/Users/HP/Desktop/数据集/原数据集/football.gml')

# 指定要保存的文本文件路径
output_file = 'C:/Users/HP/Desktop/数据集/原数据集/football.txt'

# 创建一个字典来映射节点标签到数字
node_mapping = {node_label: idx for idx, node_label in enumerate(G.nodes())}

# 创建一个文本文件来保存转换后的边数据
with open(output_file, 'w') as file:
    for edge in G.edges():
        # 获取边的两个节点
        node1, node2 = edge
        # 将节点标签转换为数字
        node1_idx = node_mapping[node1]
        node2_idx = node_mapping[node2]
        # 将转换后的边数据写入文本文件
        file.write(f"{node1_idx},{node2_idx}\n")

print("Conversion complete. Edge data saved in output.txt.")

