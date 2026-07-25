import networkx as nx
import matplotlib.pyplot as plt


def merge_and_draw(G, node_partition, node_sizes=None):
    # 创建一个新的图对象
    merged_G = G.copy()
    str_list = []

    for item in node_partition[1]:
        # 合并指定的节点
        merged_node_id = ", ".join(map(str, item))
        merged_G.add_node(merged_node_id)
        str_list.append(merged_node_id)

        # 连接新合并的节点与其他节点
        for node in item:
            neighbors = list(G.neighbors(node))
            merged_G.add_edges_from(
                [(merged_node_id, neighbor) for neighbor in neighbors if neighbor in node_partition[0]])

        # 移除原始节点
        merged_G.remove_nodes_from(item)

    node_partition[1] = str_list

    # 使用 spring 布局
    pos = nx.spring_layout(merged_G)

    # 设置节点的形状，默认为圆形
    node_shape = {}
    for node in merged_G.nodes():
        node_shape[node] = 'o'

    # 绘制图，根据节点的形状和大小
    plt.figure(figsize=(8, 6))
    color_list = ['#F94C10', '#F8DE22', 'orange', 'r', 'slateblue', 'dodgerblue', 'khaki', 'tomato', 'g', 'b', 'y', 'm',
                  'gray',
                  'black', 'c', 'brown']

    if node_sizes is None:
        node_sizes = {}  # 如果没有提供节点大小的字典，默认为空字典

    for i in range(len(node_partition)):
        nx.draw_networkx_nodes(merged_G, pos, node_size=[
            node_sizes.get(node, 600) if isinstance(node, int) else len(str(node)) * 100 for node in node_partition[i]
        ], nodelist=node_partition[i % len(color_list)], node_color=color_list[i % len(color_list)],
                               node_shape=[node_shape[node] for node in node_partition[i]])

    plt.show()


# 示例用法：
G = nx.Graph()
# 添加节点和边
# ...
node_partition = (nodes, communities)  # 替换为实际的节点和社区分配

# 创建节点大小的字典，其中键是节点名称，值是节点大小
node_sizes = {'Node1': 200, 'Node2': 300, 'Node3': 400}  # 替换为您的节点名称和大小
merge_and_draw(G, node_partition, node_sizes)
