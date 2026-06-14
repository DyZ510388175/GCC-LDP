from collections import defaultdict

import networkx as nx
import community
import pandas as pd
import matplotlib.pyplot as plt

from graph2.GCC_cluster import GCC_Run
from graph2.GCC_cluster_LDP import GCC_cluster_LDP, item_clusters_to_clusters
from graph2.compressed_set_LDP import CompressedSet,\
    GCC_Compressed_LDP_Run_and_output_res, get_all_subitems
from run_GCC_LDP import processing_indexOfnodes


def draw_spring(G, com):
    pos = nx.spring_layout(G)  # 节点的布局为spring型
    NodeId = list(G.nodes())
    node_size = [G.degree(i) ** 1.2 * 100 for i in NodeId]  # 节点大小
    plt.figure(figsize=(6, 4))  # 图片大小


    nx.draw(G, pos, with_labels=True, node_size=node_size, node_color='w', node_shape='.')
    # color_list = ['pink', 'orange', 'r', 'g', 'b', 'y', 'm', 'gray', 'black', 'c', 'brown']
    color_list = ['#F94C10', '#F8DE22', '#900C3F', 'pink', 'orange', 'r', 'slateblue', 'dodgerblue', 'khaki', 'tomato',
                  'g', 'b', 'y', 'm', 'gray',
                  'black', 'c', 'brown',
                  'purple', 'teal', 'gold', 'silver', 'navy', 'indigo', 'coral', 'lime', 'maroon',
                  'olive', 'aquamarine', 'sienna', 'orchid', 'turquoise', 'crimson', 'peru', 'salmon',
                  'chartreuse', 'darkviolet', 'rosybrown',
                  'seagreen', 'mediumseagreen', 'mediumslateblue', 'darkorange', 'slategray', 'mediumblue',
                  'cadetblue', 'mediumaquamarine', 'darkseagreen', 'darkturquoise', 'palegreen', 'orangered']
    node_sizes = {}
    for i in range(len(com)):
        nx.draw_networkx_nodes(G, pos, node_size=[node_sizes.get(node, 600) for node in com[i]],
                               nodelist=com[i % len(color_list)], node_color=color_list[i % len(color_list)])
    plt.show()


"""绘制压缩图"""


def merge_and_draw(G, node_partion):
    # 创建一个新的图对象
    merged_G = G.copy()
    str_list = []

    for item in node_partion[1]:
        # 合并指定的节点
        merged_node_id = ", ".join(map(str, item))
        merged_G.add_node(merged_node_id)
        # print('item:', item)
        str_list.append(merged_node_id)

        # 连接新合并的节点与其他节点
        for node in item:
            # print('node:', node)
            neighbors = list(G.neighbors(node))
            merged_G.add_edges_from(
                [(merged_node_id, neighbor) for neighbor in neighbors if neighbor in node_partion[0]])

        # 移除原始节点
        merged_G.remove_nodes_from(item)

    node_partion[1] = str_list
    # print('node_partion:', node_partion)

    # 使用spring布局
    pos = nx.spring_layout(merged_G)

    # 设置节点大小
    # node_size = [merged_G.degree(node) * 100 for node in merged_G.nodes()]
    node_size = []
    for node in merged_G.nodes():
        if isinstance(node, str):
            # print('type(node):', type(node))
            node_size.append(200)
        else:
            node_size.append(100)
    # print('node_size:', node_size)

    # 绘制图
    plt.figure(figsize=(6, 4))
    nx.draw(merged_G, pos, with_labels=True, node_size=node_size, node_color='w', node_shape='.')

    # 根据社区分配着色
    color_list = ['#FFF7D4', '#FFD95A', 'orange', 'r', 'slateblue', 'dodgerblue', 'khaki', 'tomato', 'g', 'b', 'y', 'm',
                  'gray',
                  'black', 'c', 'brown']

    node_sizes = {}  # 如果没有提供节点大小的字典，默认为空字典
    for i in range(len(node_partion)):
        # nx.draw_networkx_nodes(merged_G, pos, node_size=node_size_nx[i], nodelist=node_partion[i % len(color_list)],
        #                        node_color=color_list[i % len(color_list)])
        # nx.draw_networkx_nodes(merged_G, pos, node_size=[node_sizes.get(node, len(str(node))*300) for node in node_partion[i]], nodelist=node_partion[i % len(color_list)],
        #                        node_color=color_list[i % len(color_list)])
        nx.draw_networkx_nodes(merged_G, pos,
                               node_size=[node_sizes.get(node, 600) if isinstance(node, int) else len(str(node)) * 300
                                          for node in node_partion[i]],
                               nodelist=node_partion[i % len(color_list)],
                               node_color=color_list[i % len(color_list)])

    plt.show()


def merge_center_and_draw(G, node_partion, centers):
    # 创建一个新的图对象
    merged_G = G.copy()
    str_list = []

    for item in node_partion[1]:
        # 合并指定的节点
        merged_node_id = ", ".join(map(str, item))
        merged_G.add_node(merged_node_id)
        print('item:', item)
        str_list.append(merged_node_id)

        # 连接新合并的节点与其他节点
        for node in item:
            # print('node:', node)
            neighbors = list(G.neighbors(node))
            merged_G.add_edges_from(
                [(merged_node_id, neighbor) for neighbor in neighbors if neighbor in node_partion[0]])

        # 移除原始节点
        merged_G.remove_nodes_from(item)

        # 更新中心列表
        for c in range(len(centers)):
            # 检查元素是否需要替换
            if item == centers[c]:
                # 如果需要替换，将元素替换为新值
                centers[c] = merged_node_id

    node_partion[1] = str_list
    # print('node_partion:', node_partion)

    # 使用spring布局
    pos = nx.spring_layout(merged_G)

    # 设置节点大小
    # node_size = [merged_G.degree(node) * 100 for node in merged_G.nodes()]
    node_size = []
    for node in merged_G.nodes():
        if isinstance(node, str):
            # print('type(node):', type(node))
            node_size.append(200)
        else:
            node_size.append(100)
    # print('node_size:', node_size)

    # 绘制图
    plt.figure(figsize=(6, 4))
    nx.draw(merged_G, pos, with_labels=True, node_size=node_size, node_color='w', node_shape='.')

    # 根据社区分配着色
    color_list = ['#FFF7D4', '#FFD95A', 'orange', 'r', 'slateblue', 'dodgerblue', 'khaki', 'tomato', 'g', 'b', 'y', 'm',
                  'gray',
                  'black', 'c', 'brown', '#F94C10','#F8DE22']

    node_sizes = {}  # 如果没有提供节点大小的字典，默认为空字典
    node_shapes = []  # 如果没有提供节点大小的字典，默认为空字典

    # for i in range(len(node_partion)):
    #     # nx.draw_networkx_nodes(merged_G, pos, node_size=node_size_nx[i], nodelist=node_partion[i % len(color_list)],
    #     #                        node_color=color_list[i % len(color_list)])
    #     # nx.draw_networkx_nodes(merged_G, pos, node_size=[node_sizes.get(node, len(str(node))*300) for node in node_partion[i]], nodelist=node_partion[i % len(color_list)],
    #     #                        node_color=color_list[i % len(color_list)])
    #     nx.draw_networkx_nodes(merged_G, pos,
    #                            node_size=[node_sizes.get(node, 600) if isinstance(node, int) else len(str(node)) * 300
    #                                       for node in node_partion[i]],
    #                            node_shape=['h' if node in centers else 'o' for node in node_partion[i]],
    #                            nodelist=node_partion[i % len(color_list)],
    #                            node_color=color_list[i % len(color_list)])

    c_idx = 1
    for i in range(len(node_partion)):
        node_shapes = ['h' if str(node) in centers else 'o' for node in node_partion[i]]
        node_sizes = [node_sizes.get(node, 600) if isinstance(node, int) else len(str(node)) * 300 for node in
                      node_partion[i]]
        node_colors = []
        for node in node_partion[i] :
            if str(node) in centers:
                node_colors.append(color_list[len(color_list)-c_idx])
                c_idx += 1
            else:
                node_colors.append(color_list[i % len(color_list)])

        # node_colors = [color_list[len(color_list)-1] if str(node) in centers else color_list[i % len(color_list)] for
        #                node in node_partion[i]]
        print('centers:', centers)
        print('node_shapes:', node_shapes)

        for j, node in enumerate(node_partion[i % len(color_list)]):
            nx.draw_networkx_nodes(merged_G, pos,
                                   node_size=node_sizes[j],
                                   node_shape=node_shapes[j],
                                   nodelist=[node],
                                   node_color=node_colors[j])

    plt.show()


def compressed_set_to_clusters(compressed_set):
    nodes_partion = []
    nodes_no_compressed = []
    nodes_compressed = []
    for item in compressed_set:
        # print('get_all_subitems(item):',get_all_subitems(item))
        sub_nodes = get_all_subitems(item)
        if len(sub_nodes) != 1:
            cluster = [int(node) for node in sub_nodes]
            nodes_compressed.append(cluster)
        else:
            # print('sub_nodes:', sub_nodes)
            nodes_no_compressed.append(int(sub_nodes[0]))
    nodes_partion.append(nodes_no_compressed)
    nodes_partion.append(nodes_compressed)
    return nodes_partion


def compressed_centers_to_clusters(compressed_set, centers):
    nodes_partion = []
    nodes_no_compressed = []
    nodes_compressed = []
    for item in compressed_set:
        # print('get_all_subitems(item):',get_all_subitems(item))
        sub_nodes = get_all_subitems(item)
        if len(sub_nodes) != 1:
            cluster = [int(node) for node in sub_nodes]
            nodes_compressed.append(cluster)

            # 更新中心列表
            for c in range(len(centers)):
                # 检查元素是否需要替换
                if item == centers[c]:
                    # 如果需要替换，将元素替换为新值
                    centers[c] = cluster
        else:
            # print('sub_nodes:', sub_nodes)
            nodes_no_compressed.append(int(sub_nodes[0]))
    nodes_partion.append(nodes_no_compressed)
    nodes_partion.append(nodes_compressed)
    return nodes_partion, centers


def Read_nodeAndlable_excel(excel_file):
    # 读取Excel文件
    # excel_file = '../dataset/football_label.xls'
    df = pd.read_excel(excel_file)

    # 创建一个字典，用于存储簇和其对应的节点标号
    clusters = {}

    # 遍历每一行数据
    for index, row in df.iterrows():
        node_label = row['节点标号']  # 假设 '节点标号' 是 Excel 文件中节点标号所在的列名
        cluster_number = row['簇号']  # 假设 '簇号' 是 Excel 文件中簇号所在的列名

        # 如果簇号已经在字典中，将节点标号添加到对应的簇
        if cluster_number in clusters:
            clusters[cluster_number].append(node_label)
        else:
            # 否则创建一个新的簇
            clusters[cluster_number] = [node_label]

    # 将字典中的簇结果输出为所需格式
    cluster_list = [cluster for cluster in clusters.values()]

    return cluster_list


if __name__ == "__main__":
    # file = 'football'
    # read_G = nx.read_edgelist('dataset/' + file + '.txt')
    # graph = processing_indexOfnodes(read_G)
    graph = nx.karate_club_graph()

    threshold_d = 1  # 设置外围节点阈值
    threshold_beta = 0.2  # 设置连接强度阈值
    threshold_s = 0.4
    privacy_budget = 10

    """不加噪音的簇"""
    # 为graph分配标签
    '''kernighan_lin_bisection算法'''
    clusters = list(nx.algorithms.community.kernighan_lin_bisection(graph))
    draw_spring(graph, clusters)
    """簇格式转化"""
    # ground_truth = []
    # for idx, cluster in enumerate(clusters):
    #     for element in cluster:
    #         ground_truth.insert(element, idx)
    """label_propagation_communities标签传播算法"""
    # clusters = list(nx.algorithms.community.label_propagation_communities(graph))
    # print('clusters:', clusters)
    # draw_spring(graph, clusters)
    """簇格式转化"""
    # ground_truth = []
    # for idx, cluster in enumerate(clusters):
    #     for element in cluster:
    #         ground_truth.insert(element, idx)

    """Louvain Algorithm标签传播算法"""
    # clusters = community.best_partition(graph)
    # print('clusters:', clusters) #将元素的键{0: 1, 1: 1, 2: 1}
    # ground_truth = list(clusters.values())
    # print('ground_truth:', ground_truth)
    # # 使用 defaultdict 分组
    # grouped = defaultdict(set)
    # for key, value in clusters.items():
    #     grouped[value].add(key)
    #
    # # 将分组结果转换为指定的输出格式
    # format_clusters = [set(group) for group in grouped.values()]
    #
    # draw_spring(graph, format_clusters)

    """加噪音的簇"""
    # 获取压缩集合
    compressed_set, adjacency_vectors, item_frequencies = GCC_Compressed_LDP_Run_and_output_res(graph, threshold_d,
                                                                                                threshold_beta,
                                                                                                privacy_budget)

    print('compressed_set:', compressed_set)
    gcc_cluster = GCC_cluster_LDP(compressed_set, adjacency_vectors, item_frequencies)

    # 获取邻居和连接数
    item_neighborhood_and_connectionNum = gcc_cluster.get_item_neighborhood_and_connectionNum(compressed_set,
                                                                                              adjacency_vectors)
    # print('item_neighborhood_and_connectionNum:', item_neighborhood_and_connectionNum)

    # 获取中心性指数
    items_centrality_index = gcc_cluster.get_items_centrality_index(item_neighborhood_and_connectionNum,
                                                                    item_frequencies)
    # print('items_centrality_index:', items_centrality_index)

    # 获取簇中心和其它项
    clusterCenter, otherItems = gcc_cluster.get_clusterCenter_and_otherItems(items_centrality_index)
    print('clusterCenter, otherItems:', clusterCenter, otherItems)

    # 簇中心扩展
    clusters_LDP = gcc_cluster.center_extension(clusterCenter, otherItems, threshold_s, compressed_set,
                                                item_neighborhood_and_connectionNum, item_frequencies)
    print('item_clusters:', clusters)

    # 获取压缩集合
    clusters_LDP = item_clusters_to_clusters(clusters_LDP)

    # draw_spring(graph, clusters)  # 簇可视化
    # draw_spring(graph, compressed_set_to_clusters(compressed_set))  # 簇可视化
    print('compressed_set_to_clusters(compressed_set):', compressed_set_to_clusters(compressed_set))
    """绘制压缩图"""
    merge_and_draw(graph, compressed_set_to_clusters(compressed_set))

    """绘制压缩图+中心"""
    nodes_partition, centers = compressed_centers_to_clusters(compressed_set, clusterCenter)
    merge_center_and_draw(graph, nodes_partition, centers)

    """绘制聚类图"""
    draw_spring(graph, clusters_LDP)  # 簇可视化
