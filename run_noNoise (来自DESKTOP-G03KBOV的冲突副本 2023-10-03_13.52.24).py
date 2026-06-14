import time

import community
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

from graph.CommunityDetection import CommunityDetection
from graph.CommunityMetrics import CommunityMetrics
from graph.LDPGen import LDPGen
from graph.LF_GDPR import RRPerturbation, LouvainClustering
from graph.louvain import LouvainAlgorithm
from graph2.GCC_cluster import GCC_Run
from graph2.GCC_cluster_LDP import GCC_LDP_Run
from sklearn.cluster import SpectralClustering

from graph2.compressed_set_LDP import draw_spring, cluster_list_To_mapping


def calculate_metrics(graph, clusters, ground_truth):
    metrics_list = []

    metrics_calculator = CommunityMetrics(graph, clusters, ground_truth)

    # Calculate and output metrics
    # print("Modularity:", metrics_calculator.modularity())
    metrics_list.append(metrics_calculator.modularity())

    # print("Normalized Mutual Information:", metrics_calculator.normalized_mutual_info())
    metrics_list.append(metrics_calculator.normalized_mutual_info())

    # print("F1 Score:", metrics_calculator.f1())
    metrics_list.append(metrics_calculator.f1())

    # print("Adjusted Rand Index:", metrics_calculator.adjusted_rand_index())
    metrics_list.append(metrics_calculator.adjusted_rand_index())

    # print("Adjusted Mutual Information:", metrics_calculator.adjusted_mutual_info())
    metrics_list.append(metrics_calculator.adjusted_mutual_info())

    # print("Relative Entropy:", metrics_calculator.relative_entropy())
    metrics_list.append(metrics_calculator.relative_entropy())

    return metrics_list


def print_metricsMean_to_file(output_file, n_clu, means_metrics, Algorithm, RunTime):
    with open(output_file, 'a') as file:
        file.write("Algorithm, n_clu, #--- {} ---- {} ----#\n".format(Algorithm, n_clu))
        file.write("RunTime: {}\n".format(RunTime))
        # file.write("ground_truth: {}\n".format(ground_truth))
        # file.write("clusters: {}\n".format(clusters))
        file.write("Modularity: {}\n".format(means_metrics[0]))
        file.write("Normalized Mutual Information: {}\n".format(means_metrics[1]))
        file.write("F1 Score: {}\n".format(means_metrics[2]))
        file.write("Adjusted Rand Index: {}\n".format(means_metrics[3]))
        file.write("Adjusted Mutual Information: {}\n".format(means_metrics[4]))
        file.write("Relative Entropy: {}\n".format(means_metrics[5]))
        file.write("\n")  # 添加一个空行来分隔不同的追加记录


def print_metricsMax_to_file(output_file, n_clu, max_metrics, Algorithm, RunTime):
    with open(output_file, 'a') as file:
        file.write("Algorithm, n_clu, #--- {} ---- {} ----# \n".format(Algorithm, n_clu))
        file.write("RunTime: {}\n".format(RunTime))
        # file.write("ground_truth: {}\n".format(ground_truth))
        # file.write("clusters: {}\n".format(clusters))
        file.write("Modularity: {}\n".format(max_metrics[0]))
        file.write("Normalized Mutual Information: {}\n".format(max_metrics[1]))
        file.write("F1 Score: {}\n".format(max_metrics[2]))
        file.write("Adjusted Rand Index: {}\n".format(max_metrics[3]))
        file.write("Adjusted Mutual Information: {}\n".format(max_metrics[4]))
        file.write("Relative Entropy: {}\n".format(max_metrics[5]))
        file.write("\n")  # 添加一个空行来分隔不同的追加记录


def print_metrics(graph, clusters, ground_truth):
    metrics_calculator = CommunityMetrics(graph, clusters, ground_truth)

    print("ground_truth:", ground_truth)
    print("clusters:", clusters)

    # Calculate and output metrics
    print("Modularity:", metrics_calculator.modularity())
    print("Normalized Mutual Information:", metrics_calculator.normalized_mutual_info())
    print("F1 Score:", metrics_calculator.f1())
    print("Adjusted Rand Index:", metrics_calculator.adjusted_rand_index())
    print("Adjusted Mutual Information:", metrics_calculator.adjusted_mutual_info())
    print("Relative Entropy:", metrics_calculator.relative_entropy())


"""处理图数据。使节点编号从0开始。"""


def processing_indexOfnodes(graph):
    # 从外部文本文件中读取图数据并创建 G2
    G2 = graph
    # G2 = nx.read_edgelist('../dataset/karate2.txt')

    # 创建一个新的图 G，节点从0开始编号
    G = nx.Graph()

    # 遍历 G2 中的所有节点，并将它们添加到 G 中，同时更新节点编号
    node_mapping = {}
    for idx, node in enumerate(G2.nodes()):
        G.add_node(idx)  # 添加新的节点，编号从0开始
        node_mapping[node] = idx  # 记录节点映射关系

    # 遍历 G2 中的所有边，并将它们添加到 G 中，同时更新边的节点编号
    for edge in G2.edges():
        node1, node2 = edge
        new_node1 = node_mapping[node1]
        new_node2 = node_mapping[node2]
        G.add_edge(new_node1, new_node2)  # 添加新的边，使用更新后的节点编号

    # 现在，G 和 G2 具有相同的结构，但节点从0开始编号，并且边的节点编号也已更新。
    return G


"""将算法结果{0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 1}
            转换为[{0, 1, 2, 3, 4, 5, 6}, {7}]"""


def convert_res_To_clsuterlist(input_dict):
    # 创建一个空字典来存放结果
    result_dict = {}

    # 遍历原始字典的键值对
    for key, value in input_dict.items():
        # 如果值在结果字典中不存在，创建一个新的集合
        if value not in result_dict:
            result_dict[value] = set()
        # 将键添加到相应值的集合中
        result_dict[value].add(key)

    # 获取结果字典的值，这将是包含相同值的键的集合
    result = list(result_dict.values())

    return result


if __name__ == '__main__':
    """-----------------1.全局参数----------------------------------------------------"""
    loop_max = 1
    """karate, facebook_combined"""
    filename = ['facebook_combined']

    for file_idx, file in enumerate(filename):
        n_clusters = 40  # 设定最大社区数量
        n_clu = 1  # 设定社区数变量

        while n_clu < n_clusters:
            read_G = nx.read_edgelist('dataset/' + file + '.txt')
            G = processing_indexOfnodes(read_G)
            """-----------------2.数据真实标签----------------------------------------------------"""
            # 为graph分配标签
            # 获取邻接矩阵
            adj_matrix = nx.to_numpy_matrix(G)
            # 使用谱聚类进行社区检测
            spectral = SpectralClustering(n_clusters=n_clusters, affinity='nearest_neighbors')
            # ground_truth = spectral.fit_predict(adj_matrix)
            labels = spectral.fit_predict(adj_matrix)

            """簇格式转化"""
            ground_truth = []
            for idx in range(len(labels)):
                ground_truth.insert(idx, labels[idx])
            print('ground_truth:', ground_truth)

            """-----------------3.聚类算法----------------------------------------------------"""
            '''kernighan_lin_bisection算法'''
            "3.1 KernighanLin" "3.2 LabelPropagation" "3.3 Louvain"
            KernighanLin_metrics_lists = []  # 存储多次循环的指标值
            KernighanLin_metrics_list_mean = []  # 存储指标的均值
            KernighanLin_metrics_list_max = []  # 存储指标的最大值
            KernighanLin_RunTime_sum = 0  # 记录运行时间

            LabelPropagation_metrics_lists = []  # 存储多次循环的指标值
            LabelPropagation_metrics_list_mean = []  # 存储指标的均值
            LabelPropagation_metrics_list_max = []  # 存储指标的最大值
            LabelPropagation_RunTime_sum = 0  # 记录运行时间

            Louvain_metrics_lists = []  # 存储多次循环的指标值
            Louvain_metrics_list_mean = []  # 存储指标的均值
            Louvain_metrics_list_max = []  # 存储指标的最大值
            Louvain_RunTime_sum = 0  # 记录运行时间

            for loop in range(loop_max):
                """Kernighan-Lin算法是一种基于最小割的贪心算法"""
                KernighanLin_timeStart = time.time()
                KernighanLin_clusters = list(nx.algorithms.community.kernighan_lin_bisection(G))
                KernighanLin_timeEnd = time.time()
                print('KernighanLin_clusters:', KernighanLin_clusters)
                # draw_spring(G, clusters)
                """簇格式转化"""
                KernighanLin_result = dict()
                for idx, cluster in enumerate(KernighanLin_clusters):
                    for element in cluster:
                        KernighanLin_result.update({element: idx})
                print('KernighanLin_result:', KernighanLin_result)
                KernighanLin_metrics_lists.append(calculate_metrics(G, KernighanLin_result, ground_truth))
                KernighanLin_RunTime_sum += KernighanLin_timeEnd - KernighanLin_timeStart

                """label_propagation_communities标签传播算法"""
                LabelPropagation_timeStart = time.time()
                LabelPropagation_clusters = list(nx.algorithms.community.label_propagation_communities(G))
                LabelPropagation_timeEnd = time.time()
                print('LabelPropagation_clusters:', LabelPropagation_clusters)
                # draw_spring(G, clusters)
                """簇格式转化"""
                LabelPropagation_result = dict()
                for idx, cluster in enumerate(LabelPropagation_clusters):
                    for element in cluster:
                        LabelPropagation_result.update({element: idx})
                print('LabelPropagation_result:', LabelPropagation_result)
                LabelPropagation_metrics_lists.append(calculate_metrics(G, LabelPropagation_result, ground_truth))
                LabelPropagation_RunTime_sum += LabelPropagation_timeEnd - LabelPropagation_timeStart

                """Louvain Algorithm标签传播算法"""
                Louvain_timeStart = time.time()
                Louvain_result = community.best_partition(G) #{0: 1, 1: 1, 2: 1}
                Louvain_timeEnd = time.time()
                Louvain_metrics_lists.append(calculate_metrics(G, Louvain_result, ground_truth))
                Louvain_RunTime_sum += Louvain_timeEnd - Louvain_timeStart

            """-----------------4.结果评估----------------------------------------------------"""
            "输出结果"
            "5.1 KernighanLin" "5.2 LDPGen" "5.3 GCC"
            "5.1 KernighanLin"
            # 获取每列的最大值
            KernighanLin_max_metrics = [max(row) for row in zip(*KernighanLin_metrics_lists)]

            # 获取每列的均值
            KernighanLin_mean_values = [sum(row) / len(row) for row in zip(*KernighanLin_metrics_lists)]

            output_file_max = 'output/' + 'noNoise_' + file + '_max.txt'
            output_file_mean = 'output/' + 'noNoise_' + file + '_mean.txt'
            print_metricsMax_to_file(output_file_max, n_clu, KernighanLin_max_metrics, 'KernighanLin',
                                     KernighanLin_RunTime_sum / loop_max)
            print_metricsMean_to_file(output_file_mean, n_clu, KernighanLin_mean_values, 'KernighanLin',
                                      KernighanLin_RunTime_sum / loop_max)

            "5.2 LabelPropagation"
            # 获取每列的最大值
            LabelPropagation_max_metrics = [max(row) for row in zip(*LabelPropagation_metrics_lists)]

            # 获取每列的均值
            LabelPropagation_mean_values = [sum(row) / len(row) for row in zip(*LabelPropagation_metrics_lists)]

            output_file_max = 'output/' + 'noNoise_' + file + '_max.txt'
            output_file_mean = 'output/' + 'noNoise_' + file + '_mean.txt'
            print_metricsMax_to_file(output_file_max, n_clu, LabelPropagation_max_metrics, 'LabelPropagation',
                                     LabelPropagation_RunTime_sum / loop_max)
            print_metricsMean_to_file(output_file_mean, n_clu, LabelPropagation_mean_values, 'LabelPropagation',
                                      LabelPropagation_RunTime_sum / loop_max)

            "5.3 Louvain"
            # 获取每列的最大值
            Louvain_max_metrics = [max(row) for row in zip(*Louvain_metrics_lists)]

            # 获取每列的均值
            Louvain_mean_values = [sum(row) / len(row) for row in zip(*Louvain_metrics_lists)]

            output_file_max = 'output/' + 'noNoise_' + file + '_max.txt'
            output_file_mean = 'output/' + 'noNoise_' + file + '_mean.txt'
            print_metricsMax_to_file(output_file_max, n_clu, Louvain_max_metrics, 'Louvain', Louvain_RunTime_sum / loop_max)
            print_metricsMean_to_file(output_file_mean, n_clu, Louvain_mean_values, 'Louvain', Louvain_RunTime_sum / loop_max)

            n_clu += 2
