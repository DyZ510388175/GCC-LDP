from collections import deque
import random

import networkx as nx

from graph2.compressed_set_LDP import CompressedSet, GCC_Compressed_LDP_Run_and_output_res, cluster_list_To_mapping, \
    compressed_set_to_clusters, draw_spring, get_all_subitems


class GCC_cluster_LDP:
    def __init__(self, compressed_set, adjacency_vectors, item_frequencies):
        self.compressed_set = compressed_set
        self.adjacency_vectors = adjacency_vectors
        self.item_frequencies = item_frequencies

    """将最终压缩集合项按着阈值threshold_d进行划分"""

    def division_compressed_set(self, compressed_set, item_frequencies, threshold_d):
        items_above_threshold = set()
        items_under_threshold = set()

        for item, frequencies_list in item_frequencies.items():

            if len(item) == 1 and frequencies_list[0] < threshold_d:  # 项中只包含1个节点，则判断它的连接边数
                items_under_threshold.add(item)
            else:
                items_above_threshold.add(item)

        return items_above_threshold, items_under_threshold

    """对于items_above_threshold，计算中心性，获取中心项，并进行中心扩展"""
    """2023-8-30 计算中心性，获取中心项，并进行中心扩展"""
    """计算中心性指标。密度=项的频数，item1重要性：权重*邻居频数。其中，权重=item的子项与邻居的连接数/邻居的频数"""

    # 获取item的邻居和连接数 [{'16': 2, '19': 3},{...}]
    # def get_item_neighborhood_and_connectionNum(self, compressed_set, adjacency_vectors_custom):
    #     item_neighborhood_listOfdicts = [{} for _ in range(len(compressed_set))]
    #     compressed_list = list(compressed_set)
    #     for idx1, item1 in enumerate(compressed_list):
    #         for idx2 in range(idx1 + 1, len(compressed_list)):
    #             item2 = compressed_list[idx2]
    #             # print('idx1, item1:', idx1, item1)
    #             # print('idx2, item2:', idx2, item2)
    #             for adjacency_vector in adjacency_vectors_custom:
    #                 # print('adjacency_vector:', adjacency_vector)
    #                 # print('type(adjacency_vector):', type(adjacency_vector))
    #                 if adjacency_vector[idx1] != 0 and adjacency_vector[idx2] != 0:
    #                     if item2 in item_neighborhood_listOfdicts[idx1]:
    #                         item_neighborhood_listOfdicts[idx1][item2] += 1
    #                     else:
    #                         item_neighborhood_listOfdicts[idx1][item2] = 1
    #
    #                     if item1 in item_neighborhood_listOfdicts[idx2]:
    #                         item_neighborhood_listOfdicts[idx2][item1] += 1
    #                     else:
    #                         item_neighborhood_listOfdicts[idx2][item1] = 1
    #     return item_neighborhood_listOfdicts

    """get_item_neighborhood_and_connectionNum"""

    # def get_item_neighborhood_and_connectionNum(self, compressed_set, adjacency_vectors_custom):
    #     # 用于计算中心性指标
    #     item_neighborhood_listOfdicts = [{} for _ in range(len(compressed_set))]
    #     compressed_list = list(compressed_set)
    #     for idx1, item1 in enumerate(compressed_list):
    #         for idx2 in range(idx1 + 1, len(compressed_list)):
    #             item2 = compressed_list[idx2]
    #             # print('idx1, item1:', idx1, item1)
    #             # print('idx2, item2:', idx2, item2)
    #             for v_idx, adjacency_vector in enumerate(adjacency_vectors_custom):
    #                 # print('adjacency_vector:', adjacency_vector)
    #                 # print('type(adjacency_vector):', type(adjacency_vector))
    #                 # if str(v_idx) not in item1 and str(v_idx) not in item2 and adjacency_vector[idx1] != 0 and \
    #                 #         adjacency_vector[idx2] != 0:
    #                 if adjacency_vector[idx1] != 0 and adjacency_vector[idx2] != 0:
    #                 # if str(v_idx) in item1 or str(v_idx) in item2 and adjacency_vector[idx1] != 0 and \
    #                 #                 adjacency_vector[idx2] != 0:
    #                 # if str(v_idx) not in item1 and str(v_idx) not in item2:
    #                     if adjacency_vector[idx1] != 0 and adjacency_vector[idx2] != 0:
    #                         if item2 in item_neighborhood_listOfdicts[idx1]:
    #                             item_neighborhood_listOfdicts[idx1][item2] += 1
    #                         else:
    #                             item_neighborhood_listOfdicts[idx1][item2] = 1
    #
    #                         if item1 in item_neighborhood_listOfdicts[idx2]:
    #                             item_neighborhood_listOfdicts[idx2][item1] += 1
    #                         else:
    #                             item_neighborhood_listOfdicts[idx2][item1] = 1
    #
    #     print('adjacency_vectors_custom:', adjacency_vectors_custom)
    #     print('item_neighborhood_listOfdicts:', item_neighborhood_listOfdicts)
    #     return item_neighborhood_listOfdicts

    """2023-9-2 get_item_neighborhood_and_connectionNum"""

    # 修改：A的邻居为B，B的邻居中也应该包括A
    def get_item_neighborhood_and_connectionNum(self, compressed_set, adjacency_vectors_custom):
        # 用于计算中心性指标
        item_neighborhood_listOfdicts = [{} for _ in range(len(compressed_set))]
        compressed_list = list(compressed_set)
        for idx1, item1 in enumerate(compressed_list):
            for idx2, item2 in enumerate(compressed_list):
                if idx1 != idx2:
                    item2 = compressed_list[idx2]
                    # print('idx1, item1:', idx1, item1)
                    # print('idx2, item2:', idx2, item2)
                    nodes = get_all_subitems(item1)
                    for node in nodes:
                        if adjacency_vectors_custom[int(node)][idx2] != 0:
                            if item2 in item_neighborhood_listOfdicts[idx1]:
                                item_neighborhood_listOfdicts[idx1][item2] += adjacency_vectors_custom[int(node)][idx2]
                            else:
                                item_neighborhood_listOfdicts[idx1][item2] = adjacency_vectors_custom[int(node)][idx2]

        # print('adjacency_vectors_custom:', adjacency_vectors_custom)
        # print('item_neighborhood_listOfdicts:', item_neighborhood_listOfdicts)
        return item_neighborhood_listOfdicts

    def get_item_neighborhood_and_connectionNum2(self, compressed_set, adjacency_vectors_custom):
        # 用于计算中心性指标
        item_neighborhood_listOfdicts = [{} for _ in range(len(compressed_set))]
        # 用于计算相似性
        item_neighborhood_listOfdicts2 = [{} for _ in range(len(compressed_set))]
        compressed_list = list(compressed_set)
        for idx1, item1 in enumerate(compressed_list):
            for idx2 in range(idx1 + 1, len(compressed_list)):
                item2 = compressed_list[idx2]
                # print('idx1, item1:', idx1, item1)
                # print('idx2, item2:', idx2, item2)
                for v_idx, adjacency_vector in enumerate(adjacency_vectors_custom):
                    # print('adjacency_vector:', adjacency_vector)
                    # print('type(adjacency_vector):', type(adjacency_vector))
                    # if str(v_idx) not in item1 and str(v_idx) not in item2 and adjacency_vector[idx1] != 0 and \
                    #         adjacency_vector[idx2] != 0:
                    if adjacency_vector[idx1] != 0 and adjacency_vector[idx2] != 0:
                        # if str(v_idx) in item1 or str(v_idx) in item2 and adjacency_vector[idx1] != 0 and \
                        #                 adjacency_vector[idx2] != 0:
                        # if str(v_idx) in item1 or str(v_idx) in item2:
                        #     if adjacency_vector[idx1] != 0 and adjacency_vector[idx2] != 0:
                        if item2 in item_neighborhood_listOfdicts[idx1]:
                            item_neighborhood_listOfdicts[idx1][item2] += 1
                        else:
                            item_neighborhood_listOfdicts[idx1][item2] = 1

                        if item1 in item_neighborhood_listOfdicts[idx2]:
                            item_neighborhood_listOfdicts[idx2][item1] += 1
                        else:
                            item_neighborhood_listOfdicts[idx2][item1] = 1

                    direct_connection = 0
                    if adjacency_vector[idx1] != 0 and adjacency_vector[idx2] != 0:
                        if item2 in item_neighborhood_listOfdicts2[idx1]:
                            item_neighborhood_listOfdicts2[idx1][item2] += 1
                        else:
                            item_neighborhood_listOfdicts2[idx1][item2] = 1

                        if item1 in item_neighborhood_listOfdicts2[idx2]:
                            item_neighborhood_listOfdicts2[idx2][item1] += 1
                        else:
                            item_neighborhood_listOfdicts2[idx2][item1] = 1

        # print('adjacency_vectors_custom:', adjacency_vectors_custom)
        # print('item_neighborhood_listOfdicts:', item_neighborhood_listOfdicts)
        return item_neighborhood_listOfdicts

    # 计算中心性指数 {'27': 100.0, '13': 170.0}
    def get_items_centrality_index(self, item_neighborhood_listOfdicts, item_frequencies):

        items_centrality_index_listOfdicts = dict()

        '''item_frequencies:'12': [2, 0], '22': [2, 0]'''
        # print('item_frequencies:', item_frequencies)
        for idx, pair in enumerate(item_frequencies.items()):
            item, frequencies = pair
            '''idx, pair: 2 ('14', [2, 0]) #### item, frequencies: 14 [2, 0]'''
            # print('idx, pair:', idx, pair)
            # print('item, frequencies:', item, frequencies)
            D_item = sum(item_frequencies[item])  # 密度
            I_item = 0  # 重要性
            # print('D_item:', D_item)
            for neighbor, connection in item_neighborhood_listOfdicts[idx].items():
                '''neighbor, connection: 16 1'''
                # print('neighbor, connection:', neighbor, connection)
                I_W = min(connection / sum(item_frequencies[neighbor]), 1)
                # print('I_W:', I_W)
                I_item += I_W * sum(item_frequencies[neighbor])

            items_centrality_index_listOfdicts.update({item: D_item * I_item})

        return items_centrality_index_listOfdicts

    # 获取拐点的索引位置 [2, 10, 14]
    def find_turning_points(self, sequence):
        turning_points = []
        # print('sequence:', sequence)

        for i in range(1, len(sequence) - 1):
            # if (sequence[i] > sequence[i - 1] and sequence[i] > sequence[i + 1]) or \
            #         (sequence[i] < sequence[i - 1] and sequence[i] < sequence[i + 1]):
            if (sequence[i] > sequence[i - 1] and sequence[i] > sequence[i + 1]):
                turning_points.append(i)

        return turning_points

    # 根据拐点划分项。['31', '13', '23'] [...]
    def slice_dict_by_turning_points(self, sorted_items_centrality_index_listOfdicts, turning_points):
        dict_part1 = {}
        dict_part2 = {}

        # print('turning_points:',turning_points)

        for slice_idx in turning_points:
            dict_part1 = sorted_items_centrality_index_listOfdicts[0:slice_idx + 1]
            dict_part2 = sorted_items_centrality_index_listOfdicts[slice_idx + 1::]
            if len(dict_part1) != 1:
                # print('len(dict_part1):', len(dict_part1))
                break
        print('dict_part:', dict_part1)

        return [item1[0] for item1 in dict_part1], [item2[0] for item2 in dict_part2]

    def get_clusterCenter_and_otherItems(self, items_centrality_index_listOfdicts):

        secondorder_difference = []

        # 第1步，对中心性指数进行排序，并生成二阶差序列
        sorted_items_centrality_index_listOfdicts = sorted(items_centrality_index_listOfdicts.items(),
                                                           key=lambda x: x[1], reverse=True)
        if len(sorted_items_centrality_index_listOfdicts) < 4:
            print('sorted_items_centrality_index_listOfdicts:',sorted_items_centrality_index_listOfdicts)
            return [item1[0] for item1 in sorted_items_centrality_index_listOfdicts[0:1]], [item2[0] for item2 in sorted_items_centrality_index_listOfdicts[1::]]

        """sorted_items_centrality_index_listOfdicts: ('32', 492.0), ('31', 234.0)"""
        # print('sorted_items_centrality_index_listOfdicts:', sorted_items_centrality_index_listOfdicts)
        for idx in range(len(items_centrality_index_listOfdicts) - 2):
            secondorder_difference.append(abs((sorted_items_centrality_index_listOfdicts[idx][1] -
                                               sorted_items_centrality_index_listOfdicts[idx + 1][1]) - (
                                                      sorted_items_centrality_index_listOfdicts[idx + 1][1] -
                                                      sorted_items_centrality_index_listOfdicts[idx + 2][1])))
        """secondorder_difference: [682.0, 53.0, 194.0, 59.0]"""
        # print('secondorder_difference:', secondorder_difference)

        # 第2步，根据二阶差拐点，划分项。
        turning_points = self.find_turning_points(secondorder_difference)
        if not turning_points:
            print("turning_points is empty!!!")
            # print('sorted_items_centrality_index_listOfdicts:',sorted_items_centrality_index_listOfdicts)
            return [item1[0] for item1 in sorted_items_centrality_index_listOfdicts[0:2]], [item2[0] for item2 in sorted_items_centrality_index_listOfdicts[2::]]

        # print('turning_points:', turning_points)
        clusterCenter, otherItems = self.slice_dict_by_turning_points(sorted_items_centrality_index_listOfdicts,
                                                                      turning_points)
        return clusterCenter, otherItems

    """对于节点v,计算其邻居属于簇C的数量，邻居的邻居属于簇C的数量，"""

    # 以簇中心为基础，生成初始簇。
    def get_init_clusters(self, clusterCenter):
        init_clusters = []
        for element in clusterCenter:
            cluster = [element]
            init_clusters.append(cluster)
        return init_clusters

    # 计算item与簇间的相似性。对于节点v,计算其邻居属于簇C的数量，邻居的邻居属于簇C的数量
    def calculate_similarity_itemBcluster(self, item, compressed_set, item_cluster, item_neighborhood_and_connectionNum,
                                          item_frequencies):
        compressed_list = list(compressed_set)
        item_idx = compressed_list.index(item)
        neighborhood_in_Cluster_Num = 0
        nneighborhood_in_Cluster_Num = 0

        for neighborhood, connection in item_neighborhood_and_connectionNum[item_idx].items():
            if neighborhood in item_cluster:
                neighborhood_in_Cluster_Num += 1

                # 邻居的邻居属于簇C的数量
                for nneighborhood, cconnection in item_neighborhood_and_connectionNum[
                    compressed_list.index(neighborhood)].items():
                    if nneighborhood in item_neighborhood_and_connectionNum[item_idx] and nneighborhood in item_cluster:
                        nneighborhood_in_Cluster_Num += 1

        # print('neighborhood_in_Cluster_Num:', neighborhood_in_Cluster_Num)
        # print('sum(item_frequencies[item_idx]:', sum(item_frequencies[item]))
        return (neighborhood_in_Cluster_Num + nneighborhood_in_Cluster_Num) / sum(item_frequencies[item])

    def calculate_similarity_itemBcluster_BFS2(self, item, item_neighbor, compressed_set, item_cluster,
                                               item_neighborhood_and_connectionNum,
                                               item_frequencies):
        compressed_list = list(compressed_set)
        item_idx = compressed_list.index(item)
        neighborhood_in_Cluster_Num = 0
        nneighborhood_in_Cluster_Num = 0

        if item_neighbor in item_neighborhood_and_connectionNum[item_idx]:
            neighborhood_in_Cluster_Num += 1

        for neighborhood, connection in item_neighborhood_and_connectionNum[item_idx].items():
            if neighborhood in item_cluster:
                neighborhood_in_Cluster_Num += 1

                # 邻居的邻居属于簇C的数量
                for nneighborhood, cconnection in item_neighborhood_and_connectionNum[
                    compressed_list.index(neighborhood)].items():
                    if nneighborhood in item_neighborhood_and_connectionNum[item_idx] and nneighborhood in item_cluster:
                        nneighborhood_in_Cluster_Num += 1

        # print('neighborhood_in_Cluster_Num:', neighborhood_in_Cluster_Num)
        # print('sum(item_frequencies[item_idx]:', sum(item_frequencies[item]))
        return (neighborhood_in_Cluster_Num + nneighborhood_in_Cluster_Num) / sum(item_frequencies[item])

    # 计算item与所有簇间的相似性
    def calculate_similarity_itemBclusters(self, item, compressed_set, item_clusters,
                                           item_neighborhood_and_connectionNum,
                                           item_frequencies):
        compressed_list = list(compressed_set)
        item_idx = compressed_list.index(item)
        similaritys = []
        neighborhood_in_Cluster_Num = [0] * len(item_clusters)
        nneighborhood_in_Cluster_Num = [0] * len(item_clusters)
        # print('neighborhood_in_Cluster_Num:',neighborhood_in_Cluster_Num)

        for cluster_idx, cluster in enumerate(item_clusters):
            for neighborhood, connection in item_neighborhood_and_connectionNum[item_idx].items():
                if neighborhood in cluster:
                    # print('neighborhood, cluster:', neighborhood, cluster)
                    neighborhood_in_Cluster_Num[cluster_idx] += 1

                    # 邻居的邻居属于簇C的数量
                    for nneighborhood, cconnection in item_neighborhood_and_connectionNum[
                        compressed_list.index(neighborhood)].items():
                        if nneighborhood in item_neighborhood_and_connectionNum[item_idx] and nneighborhood in cluster:
                            nneighborhood_in_Cluster_Num[cluster_idx] += 0.5

        # print('neighborhood_in_Cluster_Num:', neighborhood_in_Cluster_Num)
        # print('sum(item_frequencies[item_idx]:', sum(item_frequencies[item]))

        # 查找具有最大相似度的簇
        max_s_index = 0
        max_s = 0
        for idx in range(len(item_clusters)):
            s = (neighborhood_in_Cluster_Num[idx] + nneighborhood_in_Cluster_Num[idx]) / sum(item_frequencies[item])
            # s = (neighborhood_in_Cluster_Num[idx]) / sum(item_frequencies[item])
            similaritys.append(s)
            # print('neighborhood_in_Cluster_Num[idx],sum(item_frequencies[item]:', neighborhood_in_Cluster_Num[idx],
            #       sum(item_frequencies[item]))
        return similaritys

    # 中心扩展。计算节点与每个簇的相似性，然后将节点划分到相似性最大的簇中
    # def center_extension(self, clusterCenter, otherItems, threshold_s, compressed_set,
    #                      item_neighborhood_and_connectionNum, item_frequencies):
    #     compressed_list = list(compressed_set)
    #     item_clusters = self.get_init_clusters(clusterCenter)
    #     # print('item_clusters:',item_clusters)
    #     while otherItems:
    #         for o_item in otherItems:
    #             similaritys = self.calculate_similarity_itemBclusters(o_item, compressed_set,
    #                                                                   item_clusters,
    #                                                                   item_neighborhood_and_connectionNum,
    #                                                                   item_frequencies)
    #             print('similaritys:', similaritys)
    #             if not all(s == similaritys[0] for s in similaritys):
    #                 item_clusters[similaritys.index(max(similaritys))].append(o_item)
    #                 otherItems.remove(o_item)
    #             else:
    #                 item_clusters[random.randint(0, len(item_clusters) - 1)].append(o_item)
    #                 otherItems.remove(o_item)
    #         if len(otherItems) == 0:
    #             break
    #             # print('similaritys:',similaritys)
    #         # print('item_clusters:', item_clusters)
    #
    #     return item_clusters

    # def center_extension(self, clusterCenter, otherItems, threshold_s, compressed_set,
    #                      item_neighborhood_and_connectionNum, item_frequencies):
    #     compressed_list = list(compressed_set)
    #     item_clusters = self.get_init_clusters(clusterCenter)
    #     # print('item_clusters:',item_clusters)
    #     pre_len = 0
    #     while otherItems:
    #         for o_item in otherItems:
    #             similaritys = self.calculate_similarity_itemBclusters(o_item, compressed_set,
    #                                                                   item_clusters,
    #                                                                   item_neighborhood_and_connectionNum,
    #                                                                   item_frequencies)
    #             print('o_item, similaritys:', o_item, similaritys)
    #             if all(s == similaritys[0] for s in similaritys):
    #                 continue
    #             else:
    #                 item_clusters[similaritys.index(max(similaritys))].append(o_item)
    #                 otherItems.remove(o_item)
    #         if len(otherItems) == 0:
    #             break
    #             # print('similaritys:',similaritys)
    #         if pre_len == len(otherItems):
    #             break
    #         pre_len = len(otherItems)
    #         print('item_clusters:', item_clusters)
    #
    #     # 如果项与各个簇相似性一样，则随机分配。
    #     while otherItems:
    #         for o_item in otherItems:
    #             item_clusters[random.randint(0, len(item_clusters) - 1)].append(o_item)
    #             otherItems.remove(o_item)
    #         if len(otherItems) == 0:
    #             break
    #     return item_clusters

    """2023-9-2"""

    # 修改：1.如果节点与多个簇具有相同的相似度，则稍后再判断。2.对与一直不能区分的节点，将其分配到较大簇中。3.如果两个簇之间存在较强的连接，则合并。
    # def center_extension(self, clusterCenter, otherItems, threshold_s, compressed_set,
    #                      item_neighborhood_and_connectionNum, item_frequencies):
    #     compressed_list = list(compressed_set)
    #     item_clusters = self.get_init_clusters(clusterCenter)
    #     similaritys_dict = dict()  # 用于存储非簇中心项的相似度 {'(6) U ((4) U (5))': [0.16666666666666666, 0.0, 0.0]}
    #     clusters_connection_dict = dict()  # 用于指导簇合并。{(0, 1): 2}
    #     # print('item_clusters:',item_clusters)
    #     pre_len = 0
    #     while otherItems:
    #         for o_item in otherItems:
    #             similaritys = self.calculate_similarity_itemBclusters(o_item, compressed_set,
    #                                                                   item_clusters,
    #                                                                   item_neighborhood_and_connectionNum,
    #                                                                   item_frequencies)
    #             # print('o_item, similaritys:', o_item, similaritys)
    #             max_similarity = max(similaritys)
    #             if o_item in similaritys_dict:
    #                 similaritys_dict[o_item] = similaritys
    #             else:
    #                 similaritys_dict.update({o_item: similaritys})
    #             if similaritys.count(max_similarity) != 1:
    #                 continue
    #             else:
    #                 item_clusters[similaritys.index(max(similaritys))].append(o_item)
    #                 otherItems.remove(o_item)
    #         if len(otherItems) == 0:
    #             break
    #             # print('similaritys:',similaritys)
    #         if pre_len == len(otherItems):
    #             break
    #         pre_len = len(otherItems)
    #         print('item_clusters:', item_clusters)
    #
    #     # 如果项与各个簇相似性一样，则随机分配。
    #     while otherItems:
    #         for o_item in otherItems:
    #             # 计算簇之间的联系
    #             sublist = similaritys_dict[o_item]
    #             max_value = max(sublist)
    #             max_indices = [i for i, value in enumerate(sublist) if value == max_value]
    #
    #             for index1 in max_indices:
    #                 for index2 in max_indices:
    #                     if index1 < index2:
    #                         clusters_connection_dict[(index1, index2)] = clusters_connection_dict.get((index1, index2),
    #                                                                                                   0) + 1
    #
    #             # 将项分配给较大的簇
    #             max_indices = [i for i, value in enumerate(sublist) if value == max_value]
    #             max_length_index = max(max_indices, key=lambda i: len(item_clusters[i]))
    #
    #             item_clusters[max_length_index].append(o_item)
    #             otherItems.remove(o_item)
    #
    #         if len(otherItems) == 0:
    #             break
    #
    #     # 合并簇
    #     print('clusters_connection_dict:', clusters_connection_dict)
    #     # 遍历连接强度字典
    #     for (cluster_idx1, cluster_idx2), connections in clusters_connection_dict.items():
    #         if connections > min(len(item_clusters[cluster_idx1]), len(item_clusters[cluster_idx2])):
    #             # 合并连接强度大于阈值的两个簇
    #             merged_cluster = item_clusters[cluster_idx1] + item_clusters[cluster_idx2]
    #             # 移除原来的簇
    #             item_clusters.pop(cluster_idx1)
    #             item_clusters.pop(cluster_idx2 - 1)  # 注意减1，因为前一个合并导致了列表长度的减小
    #             # 添加新的合并簇
    #             item_clusters.append(merged_cluster)
    #
    #     # print('similaritys_dict:', similaritys_dict)
    #     return item_clusters

    """2023-9-3"""

    # 修改：在9-2基础上，1.修改了簇合并算法. 2.修改第一轮分配。如果节点与所有簇相似度都为0，则创建新簇。
    def center_extension(self, clusterCenter, otherItems, threshold_s, compressed_set,
                         item_neighborhood_and_connectionNum, item_frequencies):
        compressed_list = list(compressed_set)
        item_clusters = self.get_init_clusters(clusterCenter)
        similaritys_dict = dict()  # 用于存储非簇中心项的相似度 {'(6) U ((4) U (5))': [0.16666666666666666, 0.0, 0.0]}
        clusters_connection_dict = dict()  # 用于指导簇合并。{(0, 1): 2}
        # print('item_clusters:',item_clusters)
        pre_len = 0
        while otherItems:
            for o_item in otherItems:
                similaritys = self.calculate_similarity_itemBclusters(o_item, compressed_set,
                                                                      item_clusters,
                                                                      item_neighborhood_and_connectionNum,
                                                                      item_frequencies)
                # print('o_item, similaritys:', o_item, similaritys)
                max_similarity = max(similaritys)
                if o_item in similaritys_dict:
                    similaritys_dict[o_item] = similaritys
                else:
                    similaritys_dict.update({o_item: similaritys})

                if max_similarity == 0:
                    item_clusters.append([o_item])
                    otherItems.remove(o_item)
                else:
                    if similaritys.count(max_similarity) != 1:
                        continue
                    else:
                        item_clusters[similaritys.index(max(similaritys))].append(o_item)
                        otherItems.remove(o_item)
            if len(otherItems) == 0:
                break
                # print('similaritys:',similaritys)
            if pre_len == len(otherItems):
                break
            pre_len = len(otherItems)
            print('1.根据最大相似度分配。item_clusters:', item_clusters)

        # 如果项与各个簇相似性一样，则将其分配给较大规模的簇。
        while otherItems:
            for o_item in otherItems:
                # 计算簇之间的联系
                sublist = similaritys_dict[o_item]
                max_value = max(sublist)
                # 最大相似度所在位置的索引
                max_indices = [i for i, value in enumerate(sublist) if value == max_value]

                # 统计簇间的连接数
                for index1 in max_indices:
                    for index2 in max_indices:
                        if index1 < index2:
                            clusters_connection_dict[(index1, index2)] = clusters_connection_dict.get((index1, index2),
                                                                                                      0) + 1

                # 将项分配给较大的簇
                # max_indices = [i for i, value in enumerate(sublist) if value == max_value]
                # max_length_index = max(max_indices, key=lambda i: len(item_clusters[i]))
                #
                # item_clusters[max_length_index].append(o_item)

                # 将项随机分配给各簇
                item_clusters[random.choice(max_indices)].append(o_item)

                otherItems.remove(o_item)

            if len(otherItems) == 0:
                break

            print('2.根据最大簇规模分配。item_clusters:', item_clusters)

        # 合并簇
        def merge_clusters(clusters, connections):
            merged_clusters = list(clusters)
            new_clusters_index = list(range(len(clusters)))

            # 创建一个映射，将节点映射到其所在的簇索引
            node_to_cluster = {}
            for cluster_index, cluster in enumerate(clusters):
                for node in cluster:
                    node_to_cluster[node] = cluster_index

            # print('merged_clusters:', merged_clusters)
            # print('node_to_cluster:', node_to_cluster)
            # print('new_clusters_index:', new_clusters_index)

            for connection, connection_strength in connections.items():
                cluster_index1, cluster_index2 = connection
                if new_clusters_index[cluster_index1] != new_clusters_index[
                    cluster_index2] and connection_strength >= min(
                    len(item_clusters[new_clusters_index[cluster_index1]]),
                    len(item_clusters[new_clusters_index[cluster_index2]])):
                    if cluster_index1 == new_clusters_index[cluster_index1] and cluster_index2 == new_clusters_index[
                        cluster_index2]:
                        # 合并 cluster2 到 cluster1
                        merged_clusters[cluster_index1] += merged_clusters[cluster_index2]
                        # 清除 cluster2 中的节点映射
                        for node in merged_clusters[cluster_index2]:
                            node_to_cluster[node] = cluster_index1
                        merged_clusters[cluster_index2] = []  # 清空 cluster2

                        # 合并后，更改簇的索引，使其指向合并的簇
                        new_clusters_index[cluster_index2] = cluster_index1
                    elif cluster_index1 != new_clusters_index[cluster_index1] and cluster_index2 == new_clusters_index[
                        cluster_index2]:
                        # 合并 cluster2 到 cluster1
                        merged_clusters[new_clusters_index[cluster_index1]] += merged_clusters[cluster_index2]
                        # 清除 cluster2 中的节点映射
                        for node in merged_clusters[cluster_index2]:
                            node_to_cluster[node] = new_clusters_index[cluster_index1]
                        merged_clusters[cluster_index2] = []  # 清空 cluster2

                        # 合并后，更改簇的索引，使其指向合并的簇
                        new_clusters_index[cluster_index2] = new_clusters_index[cluster_index1]

                    elif cluster_index1 == new_clusters_index[cluster_index1] and cluster_index2 != new_clusters_index[
                        cluster_index2]:
                        # 合并 cluster2 到 cluster1
                        merged_clusters[new_clusters_index[cluster_index2]] += merged_clusters[cluster_index1]
                        # 清除 cluster2 中的节点映射
                        for node in merged_clusters[cluster_index1]:
                            node_to_cluster[node] = new_clusters_index[cluster_index2]
                        merged_clusters[cluster_index1] = []  # 清空 cluster2

                        # 合并后，更改簇的索引，使其指向合并的簇
                        new_clusters_index[cluster_index1] = new_clusters_index[cluster_index2]
                    else:
                        # 合并 cluster2 到 cluster1
                        merged_clusters[new_clusters_index[cluster_index1]] += merged_clusters[
                            new_clusters_index[cluster_index2]]
                        # 清除 cluster2 中的节点映射
                        for node in merged_clusters[new_clusters_index[cluster_index2]]:
                            node_to_cluster[node] = new_clusters_index[cluster_index1]
                        merged_clusters[new_clusters_index[cluster_index2]] = []  # 清空 cluster2

                        # 合并后，更改簇的索引，使其指向合并的簇
                        new_clusters_index[cluster_index2] = new_clusters_index[cluster_index1]
                # print('connection,new_clusters_index,merged_clusters:', connection, new_clusters_index, merged_clusters)
            # 去除已合并的簇和空簇
            merged_clusters = [cluster for cluster in merged_clusters if cluster]
            # print('clusters_connection_dict:', clusters_connection_dict)
            print('3.根据连接数合并簇。merged_clusters:', merged_clusters)
            # print('node_to_cluster:', node_to_cluster)

            return merged_clusters

        item_clusters = merge_clusters(item_clusters, clusters_connection_dict)

        # print('similaritys_dict:', similaritys_dict)
        return item_clusters

    # 中心扩展。广度优先
    def center_extension_BFS(self, clusterCenter, otherItems, threshold_s, compressed_set,
                             item_neighborhood_and_connectionNum, item_frequencies):
        compressed_list = list(compressed_set)
        item_clusters = self.get_init_clusters(clusterCenter)

        visited = set()

        def merge_clusters(cluster1, cluster2):
            for item in cluster2:
                cluster1.append(item)

        for center_idx, center in enumerate(item_clusters):
            queue = deque()
            queue.append(center[0])
            visited.add(center[0])
            while queue:
                current_node = queue.popleft()
                current_node_idx = compressed_list.index(current_node)

                for neighbor, connection in item_neighborhood_and_connectionNum[current_node_idx].items():
                    if neighbor not in visited:
                        similarity = self.calculate_similarity_itemBcluster(neighbor, compressed_set,
                                                                            item_clusters[center_idx],
                                                                            item_neighborhood_and_connectionNum,
                                                                            item_frequencies)
                        # print(f"{neighbor},similarity:", neighbor, similarity)
                        if similarity > threshold_s:
                            queue.append(neighbor)
                            visited.add(neighbor)
                            item_clusters[center_idx].append(neighbor)

                        # 检查连接节点是否属于不同的簇，如果是则合并簇
                        for i, cluster in enumerate(item_clusters):
                            if i != center_idx:
                                similarity = self.calculate_similarity_itemBcluster(neighbor, compressed_set,
                                                                                    item_clusters[i],
                                                                                    item_neighborhood_and_connectionNum,
                                                                                    item_frequencies)
                                if similarity > threshold_s:
                                    merge_clusters(item_clusters[center_idx], cluster)
                                    del item_clusters[i]

                # # 创建新的簇
                # for node in otherItems:
                #     is_connected = False
                #     for center in cluster_centers:
                #         if node in neighbor_dict[cluster_centers.index(center)]:
                #             is_connected = True
                #             break
                #     if not is_connected:
                #         clusters[len(clusters)] = set([node])

        return item_clusters

    # 中心扩展。广度优先
    def center_extension_BFS2(self, clusterCenter, otherItems, threshold_s, compressed_set,
                              item_neighborhood_and_connectionNum, item_frequencies):
        compressed_list = list(compressed_set)
        item_clusters = self.get_init_clusters(clusterCenter)

        visited = set()

        def merge_clusters(cluster1, cluster2):
            for item in cluster2:
                cluster1.append(item)

        for center_idx, center in enumerate(item_clusters):
            queue = deque()
            queue.append(center[0])
            visited.add(center[0])
            while queue:
                current_node = queue.popleft()
                current_node_idx = compressed_list.index(current_node)

                for neighbor, connection in item_neighborhood_and_connectionNum[current_node_idx].items():
                    if neighbor not in visited:
                        similarity = self.calculate_similarity_itemBcluster(neighbor, compressed_set,
                                                                            item_clusters[center_idx],
                                                                            item_neighborhood_and_connectionNum,
                                                                            item_frequencies)
                        # print(f"{neighbor},similarity:", neighbor, similarity)
                        if similarity > threshold_s:
                            queue.append(neighbor)
                            visited.add(neighbor)
                            item_clusters[center_idx].append(neighbor)

                        # 检查连接节点是否属于不同的簇，如果是则合并簇
                        for i, cluster in enumerate(item_clusters):
                            if i != center_idx:
                                similarity = self.calculate_similarity_itemBcluster(neighbor, compressed_set,
                                                                                    item_clusters[i],
                                                                                    item_neighborhood_and_connectionNum,
                                                                                    item_frequencies)
                                if similarity > threshold_s:
                                    merge_clusters(item_clusters[center_idx], cluster)
                                    del item_clusters[i]

                # # 创建新的簇
                # for node in otherItems:
                #     is_connected = False
                #     for center in cluster_centers:
                #         if node in neighbor_dict[cluster_centers.index(center)]:
                #             is_connected = True
                #             break
                #     if not is_connected:
                #         clusters[len(clusters)] = set([node])

        return item_clusters


def item_clusters_to_clusters(item_clusters):
    clusters = []
    for cluster in item_clusters:
        tempcluster = []
        for item in cluster:
            # print('get_all_subitems(item):',get_all_subitems(item))
            item_to_nodes = {int(node) for node in get_all_subitems(item)}
            tempcluster.extend(item_to_nodes)
        clusters.append(tempcluster)
    # print('item_clusters_to_clusters:',clusters)
    return clusters


"调整空间，1。邻居的判断。2 相似度的计算"


def GCC_LDP_Run(graph, threshold_d, threshold_beta, threshold_s, privacy_budget):
    # graph = nx.karate_club_graph()
    # threshold_d = 1  # 设置外围节点阈值
    # threshold_beta = 0.1  # 设置连接强度阈值
    # threshold_s = 1  # 设置相似度阈值

    compressed_set, adjacency_vectors, item_frequencies = GCC_Compressed_LDP_Run_and_output_res(graph, threshold_d,
                                                                                                threshold_beta,
                                                                                                privacy_budget)
    # print('compressed_set:', compressed_set)
    # print('adjacency_vectors:', adjacency_vectors)
    # print('item_frequencies:', item_frequencies)

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
    clusters = gcc_cluster.center_extension(clusterCenter, otherItems, threshold_s, compressed_set,
                                            item_neighborhood_and_connectionNum, item_frequencies)
    print('item_clusters:', clusters)

    clusters = item_clusters_to_clusters(clusters)
    # format_clusters = cluster_list_To_mapping(item_clusters_to_clusters(clusters))
    # print('format_clusters:', format_clusters)

    return clusters


if __name__ == '__main__':
    graph = nx.karate_club_graph()
    threshold_d = 1  # 设置外围节点阈值
    threshold_beta = 0.1  # 设置连接强度阈值
    threshold_s = 0.1  # 设置相似度阈值

    compressed_set, adjacency_vectors, item_frequencies = GCC_Compressed_LDP_Run_and_output_res(graph, threshold_d,
                                                                                                threshold_beta)
    print('compressed_set:', compressed_set)
    print('adjacency_vectors:', adjacency_vectors)
    print('item_frequencies:', item_frequencies)

    gcc_cluster = GCC_cluster_LDP(compressed_set, adjacency_vectors, item_frequencies)

    # 获取邻居和连接数
    item_neighborhood_and_connectionNum = gcc_cluster.get_item_neighborhood_and_connectionNum(compressed_set,
                                                                                              adjacency_vectors)
    print('item_neighborhood_and_connectionNum:', item_neighborhood_and_connectionNum)

    # 获取中心性指数
    items_centrality_index = gcc_cluster.get_items_centrality_index(item_neighborhood_and_connectionNum,
                                                                    item_frequencies)
    print('items_centrality_index:', items_centrality_index)

    # 获取簇中心和其它项
    clusterCenter, otherItems = gcc_cluster.get_clusterCenter_and_otherItems(items_centrality_index)
    print('clusterCenter, otherItems:', clusterCenter, otherItems)

    # 簇中心扩展
    clusters = gcc_cluster.center_extension(clusterCenter, otherItems, threshold_s, compressed_set,
                                            item_neighborhood_and_connectionNum, item_frequencies)
    print('clusters:', clusters)

    draw_spring(graph, item_clusters_to_clusters(clusters))  # 簇可视化

    format_clusters = cluster_list_To_mapping(item_clusters_to_clusters(clusters))
    print('format_clusters:', format_clusters)
