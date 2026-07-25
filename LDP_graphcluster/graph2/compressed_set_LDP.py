import math
from collections import defaultdict
import numpy as np

import networkx as nx
import matplotlib.pyplot as plt


class CompressedSet:
    def __init__(self, graph):
        self.graph = graph
        # self.compressed_set = [str(node) for node in list(self.graph.nodes())]

    def get_initial_compressed_set(self):
        nodes = list(self.graph.nodes())
        compressed_set = [str(node) for node in nodes]
        return compressed_set

    def merge_compress_sets(self, items_above_threshold, preprocess_pair_connectionStrength_custom):
        # 初始化压缩集合字典
        compressed_dict = {item: set([item]) for item in items_above_threshold}
        # print('compressed_dict:', compressed_dict)
        # for s, nodes in compressed_dict.items():
        #     print('s, nodes:', s, nodes)

        # print('preprocess_pair_frequencies_custom:', preprocess_pair_frequencies_custom)
        # 合并节点对
        for pair, count in preprocess_pair_connectionStrength_custom.items():
            # print('pair:', pair)
            node_a, node_b = pair
            # print('node_a, node_b:', node_a, node_b)
            merged_set = f"({node_a}) U ({node_b})"

            # 找到node_a和node_b所在的压缩集合
            set_a = next((s for s, nodes in compressed_dict.items() if node_a in nodes), None)
            set_b = next((s for s, nodes in compressed_dict.items() if node_b in nodes), None)

            # 如果两个节点都在不同的压缩集合中，则合并这两个压缩集合
            if set_a and set_b and set_a != set_b:
                compressed_dict[merged_set] = compressed_dict[set_a].union(compressed_dict[set_b])
                del compressed_dict[set_a]
                del compressed_dict[set_b]
        return list(compressed_dict.keys())

    """---------------------根据压缩集合计算邻接向量-----------------------"""

    def get_adjacency_vectors_custom(self, compressed_set, privacy_budget):
        adjacency_vectors_custom = []
        for node in self.graph:
            # print("compressed_set:", compressed_set)
            adjacency_vector_custom = []
            for i, comp_set in enumerate(compressed_set):
                # print("i, comp_set", i, comp_set)
                adjacency_vector_custom.append(self.get_value(node, comp_set, privacy_budget))
            # print("adjacency_vector_custom:", adjacency_vector_custom)
            # print(len(adjacency_vector_custom))
            adjacency_vectors_custom.append(adjacency_vector_custom)
        return adjacency_vectors_custom

    def get_value(self, node, comp_set, privacy_budget):
        # You should implement your own logic to check if 'node' has an edge with nodes in 'sub_set'
        # For example: return True if any(n in sub_set for n in [node1, node2, ...])
        count = 0
        for j, sub_set in enumerate(get_subitems(comp_set)):
            # print("j, sub_set", j, sub_set)
            # print('self.get_all_subitems(sub_set):',self.get_all_subitems(sub_set))
            if any(self.graph.has_edge(node, int(n)) for n in get_all_subitems(sub_set)):
                count += 1
        return k_random_response(count, [0, 1, 2], privacy_budget)

    """------------------计算压缩集合每一项的频数，用于校正上一轮压缩是否正确。以及构建节点对，（然后计算节点对频率），指导项进一步压缩。--------------------------"""

    """adjacency_frequencies: {'0': [16, 0], '1': [9, 0]}。压缩项：[索引，1的数量，2的数量]"""

    # 计算每一项的频率
    def calculate_item_frequencies_custom(self, adjacency_vectors_custom, compressed_set, pre_item_frequencies_dict,
                                          privacy_budget):
        item_frequencies_custom = dict()
        # print("self.compressed_set", self.compressed_set)

        for i, compressed_set in enumerate(compressed_set):
            # print(compressed_set[0])
            count_1 = 0
            count_2 = 0
            for adjacency_vector_custom in adjacency_vectors_custom:
                if adjacency_vector_custom[i] == 1:
                    # print("val:", adjacency_vector_custom[i])
                    # print(type(adjacency_vector_custom[i]))
                    count_1 += 1
                elif adjacency_vector_custom[i] == 2:
                    count_2 += 1
            # 项的频数估计
            q = 1 / (np.e ** privacy_budget + 2)
            p = np.e ** privacy_budget / (np.e ** privacy_budget + 2)
            count_1 = (count_1 - q) / (p - q)
            count_2 = (count_2 - q) / (p - q)
            # 如果pre_item_frequencies_dict为空，则是第一轮迭代，不需要一致性校正
            if not pre_item_frequencies_dict:
                f12_frequencies = {str(compressed_set): [count_1, count_2]}
                item_frequencies_custom.update(f12_frequencies)
            else:
                correct_count_1, correct_count_2 = self.correct_item_frequencies(compressed_set, count_1, count_2,
                                                                                 pre_item_frequencies_dict)
                f12_frequencies = {str(compressed_set): [correct_count_1, correct_count_2]}
                item_frequencies_custom.update(f12_frequencies)
        return item_frequencies_custom

    def correct_item_frequencies(self, compressed_set, count_1, count_2, pre_item_frequencies_dict):
        itemA, itemB = get_subitems(compressed_set)
        count_sum_1 = pre_item_frequencies_dict[itemA] + pre_item_frequencies_dict[itemB] - count_2
        count_sum_2 = count_1 + count_2
        correct_sum = 1 / 4 * count_sum_1 + 3 / 4 * count_sum_2

        count_2_1 = pre_item_frequencies_dict[itemA] + pre_item_frequencies_dict[itemB] - count_sum_2
        count_2_2 = count_2

        correct_count_2 = 4 / 15 * count_2_1 + 11 / 15 * count_2_2

        return correct_sum - correct_count_2, correct_count_2

    # 获取成对节点。只要项频数大于阈值d，即参与构建成对节点。
    def get_pair_items(self, compressed_set, adjacency_vectors_custom, item_frequencies, items_above_threshold,
                       threshold_beta):
        # 第一步，获取候选成对节点。只要项频数大于阈值d，即参与构建成对节点。
        items_list = list(items_above_threshold)
        pair_items = [(item1, item2) for idx, item1 in enumerate(items_list) for item2 in
                      items_list[idx + 1:]]

        # 第2步，获取候选成对节点的公共邻居数。
        pair_connectionStrength_custom = self.calculate_pair_connectionStrength_custom(compressed_set,
                                                                                       adjacency_vectors_custom,
                                                                                       item_frequencies,
                                                                                       pair_items)
        # print('pair_connectionStrength_custom:', pair_connectionStrength_custom)
        # 第3步，根据连接强度和阈值beta筛选候选成对节点
        preprocess_pair_connectionStrength_custom = self.preprocess_item_pairs(pair_connectionStrength_custom,
                                                                               threshold_beta)
        # print('preprocess_pair_connectionStrength_custom:', preprocess_pair_connectionStrength_custom)

        return preprocess_pair_connectionStrength_custom

    # 计算节点对连接强度
    '''pair_frequencies_custom, {('8', '30'): 2, ('8', '4'): 1}'''

    def calculate_pair_connectionStrength_custom(self, compressed_set, adjacency_vectors_custom, item_frequencies,
                                                 pair_items):
        # print('adjacency_vectors_custom:', adjacency_vectors_custom)
        # print('compressed_set:', compressed_set)
        compressed_list = list(compressed_set)
        pair_connectionStrength_custom = dict()
        # print(type(pair_items))
        for pair in pair_items:
            dict_j, dict_k = pair
            # print('pair:', pair)
            # print('dict_j:', dict_j)
            # print('type(dict_j):', type(dict_j))
            for v_dix, adjacency_vector in enumerate(adjacency_vectors_custom):
                # print('adjacency_vector:', adjacency_vector)
                # print('type(adjacency_vector):', type(adjacency_vector))
                idx_dict_j = compressed_list.index(dict_j)
                idx_dict_k = compressed_list.index(dict_k)
                if str(v_dix) not in dict_j and str(v_dix) not in dict_k and adjacency_vector[idx_dict_j] != 0 and \
                        adjacency_vector[idx_dict_k] != 0:
                    if pair in pair_connectionStrength_custom:
                        pair_connectionStrength_custom[pair] += 1
                    else:
                        pair_connectionStrength_custom[pair] = 1
            if pair in pair_connectionStrength_custom:
                connectionStrength = pair_connectionStrength_custom[pair] / (
                        sum(item_frequencies[dict_j]) + sum(item_frequencies[dict_k]) - pair_connectionStrength_custom[
                    pair])

                pair_connectionStrength_custom[pair] = round(connectionStrength, 3)
                # print('pair_items:',pair_items)
                # print('pair_connectionStrength_custom:',pair_connectionStrength_custom)
                # print('sum(item_frequencies[dict_j]):',sum(item_frequencies[dict_j]))
                # print('pair_connectionStrength_custom[pair]:', pair_connectionStrength_custom[pair])

        return pair_connectionStrength_custom

    def calculate_pair_connection_and_Strength_custom(self, compressed_set, adjacency_vectors_custom, item_frequencies,
                                                      pair_items):
        # print('adjacency_vectors_custom:', adjacency_vectors_custom)
        # print('len(adjacency_vectors_custom):', len(adjacency_vectors_custom))
        compressed_list = list(compressed_set)
        pair_connection_custom = dict()
        pair_connectionStrength_custom = dict()
        # print(type(pair_items))
        for pair in pair_items:
            dict_j, dict_k = pair
            # print('pair:', pair)
            # print('dict_j:', dict_j)
            # print('type(dict_j):', type(dict_j))
            # print('self.calculate_pair_connection_custom(dict_j, dict_k):',
            #       self.calculate_pair_connection_custom(compressed_set, adjacency_vectors_custom, dict_j, dict_k))
            # print('self.calculate_pair_connection_custom(dict_k, dict_j):',
            #       self.calculate_pair_connection_custom(compressed_set, adjacency_vectors_custom, dict_k, dict_j))
            for adjacency_vector in adjacency_vectors_custom:
                # print('adjacency_vector:', adjacency_vector)
                # print('type(adjacency_vector):', type(adjacency_vector))
                if adjacency_vector[compressed_list.index(dict_j)] != 0 and adjacency_vector[
                    compressed_list.index(dict_k)] != 0:
                    if pair in pair_connection_custom:
                        pair_connection_custom[pair] += 1
                    else:
                        pair_connection_custom[pair] = 1
            if pair in pair_connection_custom:
                connectionStrength = pair_connectionStrength_custom[pair] / (
                        sum(item_frequencies[dict_j]) + sum(item_frequencies[dict_k]) - pair_connectionStrength_custom[
                    pair])

                pair_connectionStrength_custom[pair] = round(connectionStrength, 3)
                # print('pair_items:',pair_items)
                # print('pair_connectionStrength_custom:',pair_connectionStrength_custom)
                # print('sum(item_frequencies[dict_j]):',sum(item_frequencies[dict_j]))
                # print('pair_connectionStrength_custom[pair]:', pair_connectionStrength_custom[pair])

        return pair_connection_custom, pair_connectionStrength_custom

    """---------------------删除高频节点对中具有重复子项的节点-----------------------"""
    '''pair_frequencies_custom, {('8', '30'): 2, ('8', '4'): 1}'''

    # 删除高频节点对中具有重复子项的节点。删除连接强度小于阈值beta的成对节点。
    def preprocess_item_pairs(self, pair_connectionStrength_custom, threshold_beta):
        subitems = set()
        new_sorted_item_pairs = {}
        # 将节点对按照计数从大到小排序
        sorted_item_pairs = sorted(pair_connectionStrength_custom.items(), key=lambda x: x[1], reverse=True)
        # print('sorted_item_pairs:', sorted_item_pairs)

        # Create a mapping of subitems to their corresponding pairs
        for key, value in sorted_item_pairs:
            # subitems = get_subitems(pair)
            # print('subitems,get_subitems(pair):', subitems, get_subitems(pair))
            # print('key[0],key[1]:', key[0], key[1])
            flag = True
            temp_subitems = set()
            if value < threshold_beta:
                break
            for k in key:
                temp_subitems.add(k)
                if k in subitems:
                    flag = False
                    break
            # print('temp_subitems:',temp_subitems)
            if flag:
                subitems.update(temp_subitems)
                new_sorted_item_pairs.update({key: value})

        return new_sorted_item_pairs

    """------------------调整压缩集合。根据频数校正合并项是否正确，以及需要进一步压缩项。--------------------------"""

    def adjust_compressed_set_custom(self, compressed_set, adjacency_vectors_custom, item_frequencies, threshold_d,
                                     threshold_beta):
        items_above_threshold = set()
        items_under_threshold = set()

        # 计算节点的连接边数，并校正前一阶段的成对节点是否正确。
        # print('adjacency_frequencies:', item_frequencies)
        for item, frequencies_list in item_frequencies.items():
            # print('item,frequencies_list:', item, frequencies_list)
            # print(len(item))
            if len(item) == 1 and frequencies_list[0] < threshold_d:  # 项中只包含1个节点，则判断它的连接边数
                items_under_threshold.add(item)
            elif len(item) > 1 and frequencies_list[1] < threshold_beta:  # 项中包含多个节点，则校正它的连接强度
                items_under_threshold.update(get_subitems(item))
            else:
                items_above_threshold.add(item)
        # print('items_under_threshold,items_above_threshold:', items_under_threshold, items_above_threshold)

        # 将连接边数大于阈值的项进行预合并。（连接强度大于阈值threshold_beta）
        "{('5', '4'): 0.75, ('3', '7'): 0.429, ('8', '9'): 0.4, ('0', '1'): 0.389}"
        preprocess_pair_connectionStrength_custom = self.get_pair_items(compressed_set, adjacency_vectors_custom,
                                                                        item_frequencies, items_above_threshold,
                                                                        threshold_beta)
        # print('pair_items:', pair_items)

        # pair_frequencies_custom = self.calculate_pair_frequencies_custom(compressed_set, adjacency_vectors_custom,
        #                                                                  pair_items)
        # # print('pair_frequencies_custom:', pair_frequencies_custom)
        #
        # preprocess_pair_frequencies_custom = self.preprocess_item_pairs(pair_frequencies_custom, threshold_beta)
        # # print('preprocess_pair_frequencies_custom:', preprocess_pair_frequencies_custom)

        new_items_above_threshold = self.merge_compress_sets(items_above_threshold,
                                                             preprocess_pair_connectionStrength_custom)
        # print('new_items_above_threshold: ', new_items_above_threshold)
        # print('items_under_threshold,new_items_above_threshold:', items_under_threshold, new_items_above_threshold)

        return new_items_above_threshold + list(items_under_threshold)


"""K-RR"""


def k_random_response(value, values, epsilon):
    """
    the k-random response
    :param value: current value
    :param values: the possible value
    :param epsilon: privacy budget
    :return:
    """
    if not isinstance(values, list):
        raise Exception("The values should be list")
    if value not in values:
        raise Exception("Errors in k-random response")
    p = np.e ** epsilon / (np.e ** epsilon + len(values) - 1)
    if np.random.random() < p:
        return value
    values.remove(value)
    return values[np.random.randint(low=0, high=len(values))]  # low ~ high-1范围内随机取值


"""获取压缩集合 项的子集"""


def get_subitems(item):
    subitems = []
    current_subitem = ""
    inside_brackets = 0

    for char in item:
        if char == '(':
            if inside_brackets > 0:
                current_subitem += char
            inside_brackets += 1
        elif char == ')':
            inside_brackets -= 1
            if inside_brackets > 0:
                current_subitem += char
        elif char == 'U' and inside_brackets == 0:
            if current_subitem:
                subitems.append(current_subitem.strip())  # Remove spaces
                current_subitem = ""
        else:
            current_subitem += char

    if current_subitem:
        subitems.append(current_subitem.strip())  # Remove spaces

    return subitems


def get_all_subitems(item):
    subitems = []
    current_subitem = ""
    stack = []
    seen_subitems = set()

    for i, char in enumerate(item):
        if char == '(':
            if current_subitem:
                stack.append(current_subitem)
                current_subitem = ""
            stack.append('(')
        elif char == ')':
            if current_subitem:
                if current_subitem not in seen_subitems:
                    subitems.append(current_subitem)
                    seen_subitems.add(current_subitem)
                current_subitem = ""

            while stack and stack[-1] != '(':
                subitem = stack.pop()
                if subitem != 'U':
                    if subitem not in seen_subitems:
                        subitems.append(subitem)
                        seen_subitems.add(subitem)
            # Pop the '('
            stack.pop()
        elif char == ' ':
            if current_subitem:
                stack.append(current_subitem)
                current_subitem = ""
        elif char == 'U':
            if i + 1 < len(item) and item[i + 1] == ' ':
                if current_subitem:
                    if current_subitem not in seen_subitems:
                        subitems.append(current_subitem)
                        seen_subitems.add(current_subitem)
                current_subitem = ""
            else:
                current_subitem += char
        else:
            current_subitem += char

    if current_subitem and current_subitem not in seen_subitems:
        subitems.append(current_subitem)

    return subitems


def compressed_set_to_clusters(compressed_set):
    clusters = []
    for item in compressed_set:
        # print('get_all_subitems(item):',get_all_subitems(item))
        cluster = {int(node) for node in get_all_subitems(item)}
        clusters.append(cluster)
    return clusters


"""--------聚簇结果可视化----------"""


def draw_spring(G, com):
    pos = nx.spring_layout(G)  # 节点的布局为spring型
    NodeId = list(G.nodes())
    node_size = [G.degree(i) ** 1.2 * 90 for i in NodeId]  # 节点大小
    plt.figure(figsize=(8, 6))  # 图片大小
    nx.draw(G, pos, with_labels=True, node_size=node_size, node_color='w', node_shape='.')
    # color_list = ['pink', 'orange', 'r', 'g', 'b', 'y', 'm', 'gray', 'black', 'c', 'brown']
    color_list = ['pink', 'orange', 'r', 'slateblue', 'dodgerblue', 'khaki', 'tomato', 'g', 'b', 'y', 'm', 'gray',
                  'black', 'c', 'brown',
                  'purple', 'teal', 'gold', 'silver', 'navy', 'indigo', 'coral', 'lime', 'maroon',
                  'olive', 'aquamarine', 'sienna', 'orchid', 'turquoise', 'crimson', 'peru', 'salmon',
                  'chartreuse', 'darkviolet', 'rosybrown',
                  'seagreen', 'mediumseagreen', 'mediumslateblue', 'darkorange', 'slategray', 'mediumblue',
                  'cadetblue', 'mediumaquamarine', 'darkseagreen', 'darkturquoise', 'palegreen', 'orangered']
    for i in range(len(com)):
        nx.draw_networkx_nodes(G, pos, nodelist=com[i % len(color_list)], node_color=color_list[i % len(color_list)])
    plt.show()


"""簇格式转化。[{28}, {24, 26}, {25}, {19}] to {19: 0, 24: 1, 25: 2, 26: 1, 28: 2}"""


def cluster_list_To_mapping(clusters_list):
    cluster_mapping = {}  # 用于存储节点到簇索引的映射

    for cluster_idx, cluster in enumerate(clusters_list):
        for node in cluster:
            cluster_mapping[node] = cluster_idx

    # 按节点的顺序排序字典
    sorted_cluster_mapping = {k: v for k, v in sorted(cluster_mapping.items())}
    return sorted_cluster_mapping


def GCC_Compressed_LDP_Run_and_output_res(graph, threshold_d, threshold_beta, privacy_budget):
    compressed_set_handler = CompressedSet(graph)

    # 初始压缩集合
    compressed_set = compressed_set_handler.get_initial_compressed_set()

    adjacency_vectors = []
    item_frequencies = []

    previous_compressed_set = set()  # 用于存储上一次迭代的压缩集合

    h = math.log(((3 * len(graph.nodes()) / 2 + 1) * 2 * len(graph.edges())) - max(
        (len(graph.edges()) - len(graph.nodes())) * (len(graph.nodes()) - 1), 0) / (
                         len(graph.nodes()) * (len(graph.nodes()) - 1)))
    # print('h:', h)
    max_iterations = math.floor(h)  # 设置最大迭代次数
    pre_item_frequencies_dict = dict()  # 用于存储上一次迭代中项的频率

    for iteration in range(max_iterations):
        adjacency_vectors = compressed_set_handler.get_adjacency_vectors_custom(
            compressed_set, privacy_budget)
        item_frequencies = compressed_set_handler.calculate_item_frequencies_custom(adjacency_vectors,
                                                                                    compressed_set,
                                                                                    pre_item_frequencies_dict,
                                                                                    privacy_budget)
        new_compressed_set = compressed_set_handler.adjust_compressed_set_custom(compressed_set, adjacency_vectors,
                                                                                 item_frequencies,
                                                                                 threshold_d, threshold_beta)
        if new_compressed_set == previous_compressed_set or iteration == max_iterations - 1:
            break  # 结束循环

        compressed_set = new_compressed_set
        previous_compressed_set = compressed_set  # 更新上一次迭代的压缩集合
    # print('compressed_set:', compressed_set)
    clusters = compressed_set_to_clusters(compressed_set)  # 压缩集合转簇
    # print('clusters:', clusters)
    return previous_compressed_set, adjacency_vectors, item_frequencies


def GCC_Compressed_Run(graph, threshold_d, threshold_beta):
    compressed_set_handler = CompressedSet(graph)

    # 初始压缩集合
    compressed_set = compressed_set_handler.get_initial_compressed_set()

    previous_compressed_set = set()  # 用于存储上一次迭代的压缩集合
    max_iterations = 10  # 设置最大迭代次数

    for iteration in range(max_iterations):
        adjacency_vectors = compressed_set_handler.get_adjacency_vectors_custom(
            compressed_set)
        item_frequencies = compressed_set_handler.calculate_item_frequencies_custom(adjacency_vectors,
                                                                                    compressed_set)
        new_compressed_set = compressed_set_handler.adjust_compressed_set_custom(compressed_set, adjacency_vectors,
                                                                                 item_frequencies,
                                                                                 threshold_d, threshold_beta)
        if new_compressed_set == previous_compressed_set or iteration == max_iterations - 1:
            break  # 结束循环

        compressed_set = new_compressed_set
        previous_compressed_set = compressed_set  # 更新上一次迭代的压缩集合
    # print('compressed_set:', compressed_set)
    clusters = compressed_set_handler.compressed_set_to_clusters(compressed_set)  # 压缩集合转簇
    # print('clusters:', clusters)
    return cluster_list_To_mapping(clusters)


if __name__ == "__main__":
    graph = nx.karate_club_graph()
    threshold_d = 1  # 设置外围节点阈值
    threshold_beta = 0.1  # 设置连接强度阈值

    compressed_set_handler = CompressedSet(graph)

    # 初始压缩集合
    compressed_set = compressed_set_handler.get_initial_compressed_set()
    adjacency_vectors = []

    print("-----Initial Compressed Sets---------")
    print('Initial Compressed Sets:', compressed_set)

    max_iterations = 10  # 设置最大迭代次数

    for _ in range(max_iterations):
        adjacency_vectors = compressed_set_handler.get_adjacency_vectors_custom(
            compressed_set)
        item_frequencies = compressed_set_handler.calculate_item_frequencies_custom(adjacency_vectors,
                                                                                    compressed_set)
        compressed_set = compressed_set_handler.adjust_compressed_set_custom(compressed_set, adjacency_vectors,
                                                                             item_frequencies,
                                                                             threshold_d, threshold_beta)
    print('compressed_set:', compressed_set)

    clusters = compressed_set_to_clusters(compressed_set)  # 压缩集合转簇
    print('clusters:', compressed_set_to_clusters(compressed_set))

    # 计算簇的数量和节点数
    num_clusters = len(clusters)
    total_nodes = sum(len(cluster) for cluster in clusters)
    print(f"Number of Clusters: {num_clusters}")
    print(f"Total Number of Nodes: {total_nodes}")

    draw_spring(graph, clusters)  # 簇可视化

    # adjacency_vectors = compressed_set_handler.get_adjacency_vectors_custom(
    #     compressed_set)
    # adjacency_frequencies = compressed_set_handler.calculate_adjacency_frequencies_custom(adjacency_vectors,
    #                                                                                       compressed_set)
    # print('adjacency_vectors:', adjacency_vectors)
    # print('adjacency_frequencies:', adjacency_frequencies)
    #
    # # adjust_compressed_set_custom 测试1
    # adjust_compressed_set = compressed_set_handler.adjust_compressed_set_custom(compressed_set, adjacency_vectors,
    #                                                                             adjacency_frequencies, threshold_value)
    # print('adjust_compressed_set:', adjust_compressed_set)
    #
    # # adjust_compressed_set_custom 测试2
    # # items_under_threshold, items_above_threshold = compressed_set_handler.adjust_compressed_set_custom(
    # #     compressed_set, adjacency_vectors, adjacency_frequencies, threshold_value)
    # # print('items_under_threshold, items_above_threshold:', items_under_threshold, items_above_threshold)
    #
    # # Merge example: merge nodes by threshold
    # print("------Compressed Sets--------")
    # # 输入节点对和阈值
    # input_node_pairs = {('1', '2'): 3, ('(1) U (2)', '3'): 5, ('(1) U (2)', '4'): 4}
    #
    # # 合并压缩集合
    # result_compressed_set = compressed_set_handler.merge_compress_sets(compressed_set,
    #                                                                    input_node_pairs)
    # # 输出结果
    # print('result_compress_sets:', result_compressed_set)
    #
    # # 合并压缩集合
    # result_compressed_set2 = compressed_set_handler.merge_compress_sets(result_compressed_set, input_node_pairs)
    # # 输出结果
    # print('result_compress_sets2:', result_compressed_set2)
    #
    # adjacency_vectors = compressed_set_handler.get_adjacency_vectors_custom(result_compressed_set2)
    # print('adjacency_vectors', adjacency_vectors)
    #
    # adjacency_frequencies = compressed_set_handler.calculate_adjacency_frequencies_custom(adjacency_vectors,
    #                                                                                       result_compressed_set2)
    # print('adjacency_frequencies:', adjacency_frequencies)
    #
    # adjust_compressed_set = compressed_set_handler.adjust_compressed_set_custom(
    #     result_compressed_set2, adjacency_vectors, adjacency_frequencies, threshold_value)
    # print('adjust_compressed_set:', adjust_compressed_set)
