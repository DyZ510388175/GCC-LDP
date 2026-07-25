import networkx as nx
from collections import Counter
import numpy as np
import json


class GEMAlgorithm:
    def __init__(self, graph, threshold):
        self.graph = graph
        self.threshold = threshold
        self.compressed_sets = [{node} for node in self.graph.nodes()]

    def calculate_adjacency_vector(self, node):
        adjacency_vector = [1 if self.graph.has_edge(node, n) else 0 for compressed_set in self.compressed_sets for n in
                            compressed_set]
        return adjacency_vector

    def calculate_adjacency_frequencies(self):
        adjacency_frequencies = Counter()
        # print("self.compressed_sets", self.compressed_sets)
        for i, compressed_set in enumerate(self.compressed_sets):
            adjacency_vector = self.calculate_adjacency_vector(i)
            # print("adjacency_vector:", adjacency_vector)
            for j, val in enumerate(adjacency_vector):
                if val == 1:
                    adjacency_frequencies[j] += 1
        print("adjacency_frequencies:", adjacency_frequencies)
        return adjacency_frequencies

    def calculate_pair_frequencies(self, pair_nodes):
        pair_frequencies = Counter()
        for i, compressed_set in enumerate(self.compressed_sets):
            adjacency_vector = self.calculate_adjacency_vector(i)
            # print("adjacency_vector:", adjacency_vector)
            for pair in pair_nodes:
                # print(pair)
                j, k = pair
                if adjacency_vector[j] == adjacency_vector[k] == 1:
                    pair_frequencies[pair] += 1
        print("pair_frequencies:", pair_frequencies)
        return pair_frequencies

    def merge_subsets_with_high_frequency_pairs(self, high_frequency_pairs):
        merged_pairs = set()
        for pair in high_frequency_pairs:
            i, j = pair
            if i not in merged_pairs and j not in merged_pairs:
                new_comp_set = self.compressed_sets[i].union(self.compressed_sets[j])
                self.compressed_sets[i] = new_comp_set
                self.compressed_sets[j] = set()
                merged_pairs.add(j)

    def gem_first_round(self):
        adjacency_frequencies = self.calculate_adjacency_frequencies()
        nodes_above_threshold = [node for node, freq in adjacency_frequencies.items() if freq > self.threshold]
        pair_nodes = [(node1, node2) for idx, node1 in enumerate(nodes_above_threshold) for node2 in
                      nodes_above_threshold[idx + 1:]]
        pair_frequencies = self.calculate_pair_frequencies(pair_nodes)
        high_frequency_pairs = [pair for pair, freq in pair_frequencies.items() if freq > self.threshold]
        high_frequency_pairs.sort(key=lambda x: pair_frequencies[x], reverse=True)
        self.merge_subsets_with_high_frequency_pairs(high_frequency_pairs)
        self.compressed_sets = [comp_set for comp_set in self.compressed_sets if len(comp_set) > 0]

        # 返回修改后的压缩集合
        return self.get_compressed_sets()

    def get_compressed_sets(self):
        result = list()
        for i, comp_set in enumerate(self.compressed_sets):
            if len(comp_set) > 0:
                result.append([set([element]) for element in comp_set])
        return result

    def print_compressed_sets(self):
        for i, comp_set in enumerate(self.compressed_sets):
            if len(comp_set) > 0:
                formatted_set = [set([element]) for element in comp_set]
                print(f"Compressed Set {i}: {formatted_set}")

    """-----迭代压缩------------------------------------------------------------------------------------------"""

    # 根据压缩集合计算邻接向量
    def calculate_adjacency_vectors_custom(self, compressed_sets):
        adjacency_vectors_custom = []
        for node in self.graph:
            # print("compressed_sets:", compressed_sets)
            adjacency_vector_custom = []
            for i, comp_set in enumerate(compressed_sets):
                # print("i, comp_set", i, comp_set)
                adjacency_vector_custom.append(self.get_value(node, comp_set))
            # print("adjacency_vector_custom:", adjacency_vector_custom)
            # print(len(adjacency_vector_custom))
            adjacency_vectors_custom.append(adjacency_vector_custom)
        return adjacency_vectors_custom

    def get_value(self, node, comp_set):
        # You should implement your own logic to check if 'node' has an edge with nodes in 'sub_set'
        # For example: return True if any(n in sub_set for n in [node1, node2, ...])
        count = 0
        for j, sub_set in enumerate(comp_set):
            # print("j, sub_set", j, sub_set)
            if any(self.graph.has_edge(node, n) for n in sub_set):
                count += 1
        return count

    # 计算邻接向量每一位的频数，校正压缩集合。
    def calculate_adjacency_frequencies_custom(self, adjacency_vectors_custom, compressed_sets):
        adjacency_frequencies_custom = []
        # print("self.compressed_sets", self.compressed_sets)

        for i, compressed_set in enumerate(compressed_sets):
            # print(compressed_sets[0])
            count_1 = 0
            count_2 = 0
            for adjacency_vector_custom in adjacency_vectors_custom:
                if adjacency_vector_custom[i] == 1:
                    # print("val:", adjacency_vector_custom[i])
                    # print(type(adjacency_vector_custom[i]))
                    count_1 += 1
                elif adjacency_vector_custom[i] == 2:
                    count_2 += 1
            f12_frequencies = {str(compressed_set) + '_1': count_1, str(compressed_set) + '_2': count_2}
            adjacency_frequencies_custom.append(f12_frequencies)
        return adjacency_frequencies_custom

    # 校正压缩集合，将频数小于阈值的项进行拆分
    # def correct_compressed_set(self, compressed_set, freq_list, threshold):
    #     new_compressed_set = []
    #
    #     for i, item_set in enumerate(compressed_set):
    #         new_item_sets = []
    #
    #         index = str(item_set) + '_2'
    #         if len(item_set) > 1:
    #             if freq_list[i][index] < threshold:
    #                 for subset in item_set:
    #                     new_item_sets.append([subset])
    #             else:
    #                 new_item_sets.append(item_set)
    #         else:
    #             new_item_sets.append(item_set)
    #
    #         for new_item_set in new_item_sets:
    #             new_compressed_set.append(new_item_set)
    #
    #     return new_compressed_set
    def correct_compressed_set(self, compressed_sets, adjacency_frequencies_custom, threshold):
        new_compressed_sets = []

        # 用于构建候选节点对, item_set_above_threshold=[{0:[{0}, {1}]}], 字典结构：{序号，item}
        item_set_above_threshold = []

        for i, item_set in enumerate(compressed_sets):
            new_item_sets = []

            index = str(item_set) + '_2'
            if len(item_set) > 1:
                if adjacency_frequencies_custom[i][index] < threshold:
                    for subset in item_set:
                        new_item_sets.append([subset])
                else:
                    new_item_sets.append(item_set)
                    item_set_above_threshold.append({i: item_set})
            else:
                new_item_sets.append(item_set)
                if adjacency_frequencies_custom[i][str(item_set) + '_1'] > threshold:
                    item_set_above_threshold.append({i: item_set})

            for new_item_set in new_item_sets:
                new_compressed_sets.append(new_item_set)

        #
        pair_items = [(item1, item2) for idx, item1 in enumerate(item_set_above_threshold) for item2 in
                      item_set_above_threshold[idx + 1:]]

        return new_compressed_sets, pair_items

    def calculate_pair_frequencies_custom(self, adjacency_vectors_custom, pair_items):
        pair_frequencies_custom = Counter()
        # print(type(pair_items))
        for pair in pair_items:
            dict_j, dict_k = pair
            # print('pair:', pair)
            # print(type(pair))
            # print(type(dict_j))
            # print("j,k:", j, k)
            for adjacency_vector in adjacency_vectors_custom:
                # print(adjacency_vectors_custom[next(iter(dict_j))])
                if adjacency_vector[next(iter(dict_j))] != 0 and adjacency_vector[next(iter(dict_k))] != 0:
                    pair_frequencies_custom[json.dumps(pair, default=custom_encoder)] += 1
        # print("pair_frequencies_custom:", pair_frequencies_custom)
        return pair_frequencies_custom

    def merge_subsets_with_high_frequency_pairs_custom(self, pair_frequencies_custom):
        high_frequency_pairs = [pair for pair, freq in pair_frequencies_custom.items() if freq > self.threshold]
        high_frequency_pairs.sort(key=lambda x: pair_frequencies_custom[x], reverse=True)
        print('high_frequency_pairs:', high_frequency_pairs)

        merged_pairs = set()
        for pair in high_frequency_pairs:
            # print('pair:', pair)
            # print('type(pair):', type(pair))
            # print('tuple(pair):', tuple(pair))
            # print('type(tuple(pair)):', type(tuple(pair)))
            # print(json.loads(pair, object_hook=custom_decoder))
            i, j = json.loads(pair, object_hook=custom_decoder)
            # print(i,j)
            if i not in merged_pairs and j not in merged_pairs:
                new_comp_set = self.compressed_sets[i].union(self.compressed_sets[j])
                self.compressed_sets[i] = new_comp_set
                self.compressed_sets[j] = set()
                merged_pairs.add(j)

"""json 编码解码"""
def custom_encoder(obj):
    if isinstance(obj, set):
        return list(obj)
    return obj

# 自定义解码函数
def custom_decoder(dct):
    for key, value in dct.items():
        if isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, list):
                    value[i] = set(item)
        dct[key] = value
    return dct

if __name__ == "__main__":
    karate_graph = nx.karate_club_graph()
    # 节点成对合并阈值
    threshold = 5

    """第1轮 收集邻接向量，调整压缩集合"""
    gem_algo = GEMAlgorithm(karate_graph, threshold)
    compressed_sets = gem_algo.gem_first_round()
    print("main_compressed_sets:", compressed_sets)

    """第2轮 根据压缩向量收集邻接向量(每一位的取值与前一轮不同)，校正压缩集合，继续压缩"""
    # 计算邻接向量
    adjacency_vectors_custom = gem_algo.calculate_adjacency_vectors_custom(compressed_sets)
    print("Custom Adjacency Vectors:")
    print(adjacency_vectors_custom)

    adjacency_frequencies_custom = gem_algo.calculate_adjacency_frequencies_custom(adjacency_vectors_custom,
                                                                                   compressed_sets)
    print("main_adjacency_frequencies_custom:")
    print(adjacency_frequencies_custom)

    # correct_compressed_set = gem_algo.correct_compressed_set(compressed_sets, adjacency_frequencies_custom, threshold)
    correct_compressed_set, pair_items = gem_algo.correct_compressed_set(compressed_sets, adjacency_frequencies_custom,
                                                                         threshold)
    print("correct_compressed_set:")
    print(correct_compressed_set)
    print("pair_items:")
    print(pair_items)

    pair_frequencies_custom = gem_algo.calculate_pair_frequencies_custom(adjacency_vectors_custom,
                                                                         pair_items)
    print("pair_frequencies_custom:")
    print(pair_frequencies_custom)

    adjust_compressed_set = gem_algo.merge_subsets_with_high_frequency_pairs_custom(pair_frequencies_custom)
    print("pair_frequencies_custom:")
    print(pair_frequencies_custom)
