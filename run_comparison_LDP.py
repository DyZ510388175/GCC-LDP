import time

import community
import networkx as nx
import matplotlib.pyplot as plt

from graph.CommunityDetection import CommunityDetection
from graph.CommunityMetrics import CommunityMetrics
from graph.LDPGen import LDPGen
from graph.LF_GDPR import RRPerturbation, LouvainClustering
from graph.louvain import LouvainAlgorithm
from graph2.GCC_cluster import GCC_Run
from graph2.GCC_cluster_LDP import GCC_LDP_Run

from graph2.compressed_set_LDP import draw_spring, cluster_list_To_mapping


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


def print_metricsMax_to_file(output_file, max_metrics, Algorithm, RunTime, privacy_budget, threshold_d, threshold_beta):
    with open(output_file, 'a') as file:
        file.write("Algorithm, privacy_budget, #--- {} ---- {}----# \n".format(Algorithm, privacy_budget, ))
        file.write("threshold_d,threshold_beta: {} {}\n".format(threshold_d, threshold_beta))
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


def print_metricsMean_to_file(output_file, means_metrics, Algorithm, RunTime, privacy_budget, threshold_d,
                              threshold_beta):
    with open(output_file, 'a') as file:
        file.write("Algorithm, privacy_budget, #--- {} ---- {}----#\n".format(Algorithm, privacy_budget, ))
        file.write("threshold_d,threshold_beta: {} {}\n".format(threshold_d, threshold_beta))
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


if __name__ == '__main__':
    """-----------------1.全局参数----------------------------------------------------"""
    loop_max = 1  # 算法循环次数

    # 从外部文本文件中读取图数据并创建 G2
    # 测试数据集
    # dolphins email_sample musae_ES_edges_sample musae_git_edges_sample CA-HepTh_sample musae_PTBR_edges_sample
    filename = ['musae_PTBR_edges_sample']
    threshold_ds = [1]  # 设置外围节点阈值
    threshold_betas = [0.4]  # 设置连接强度阈值

    """gemsec_deezer_sample CA-CondMat_sample"""
    # filename = ['karate', 'email_sample', 'gemsec_deezer_sample', 'facebook_combined_sample', 'Email-Enron_sample',
    #             'CA-CondMat_sample', 'musae_ES_edges_sample', 'musae_git_edges_sample', 'CA-HepTh_sample', 'musae_PTBR_edges_sample']
    # threshold_ds = [1, 3, 1, 3, 2, 2, 3, 2, 1, 4]  # 设置外围节点阈值
    # threshold_betas = [0.2, 0.8, 0.1, 0.2, 0.8, 0.8, 0.8, 0.2, 0.2, 0.4]  # 设置连接强度阈值

    # 测试示例
    # privacy_budgets = [10]  # 设置隐私预算
    privacy_budgets = [1, 2, 4, 8, 16, 32, 64]  # 设置隐私预算

    for file_idx, file in enumerate(filename):
        read_G = nx.read_edgelist('dataset/' + file + '.txt')
        G = processing_indexOfnodes(read_G)
        """-----------------2.数据真实标签----------------------------------------------------"""
        print("-------get ground_truth Start!!!!!------------")
        # 为graph分配标签
        threshold_d = threshold_ds[file_idx]  # 设置外围节点阈值
        threshold_beta = threshold_betas[file_idx]  # 设置连接强度阈值
        threshold_s = 2.5  # 设置相似度阈值
        clusters = GCC_Run(G, threshold_d, threshold_beta, threshold_s)

        ground_truth = cluster_list_To_mapping(clusters)
        """簇格式转化"""
        ground_truth = []
        for idx, cluster in enumerate(clusters):
            for element in cluster:
                ground_truth.insert(element, idx)

        print("-------get ground_truth END!!!!!------------")

        for privacy_budget in privacy_budgets:
            "3.1 LF_GDPR" "3.2 LDPGen" "3.3 GCC"
            LF_GDPR_metrics_lists = []  # 存储多次循环的指标值
            LF_GDPR_metrics_list_mean = []  # 存储指标的均值
            LF_GDPR_metrics_list_max = []  # 存储指标的最大值
            LF_GDPR_RunTime_sum = 0  # 记录运行时间

            LDPGen_metrics_lists = []  # 存储多次循环的指标值
            LDPGen_metrics_list_mean = []  # 存储指标的均值
            LDPGen_metrics_list_max = []  # 存储指标的最大值
            LDPGen_RunTime_sum = 0  # 记录运行时间

            GCC_metrics_lists = []  # 存储多次循环的指标值
            GCC_metrics_list_mean = []  # 存储指标的均值
            GCC_metrics_list_max = []  # 存储指标的最大值
            GCC_RunTime_sum = 0  # 记录运行时间

            for loop in range(loop_max):
                """-----------------3.聚类算法----------------------------------------------------"""
                "3.1 LF-GDPR"
                timeStart_LF_GDPR = time.time()
                # graph聚类
                adjacency_matrix = nx.adjacency_matrix(G).toarray()
                # 创建 EpsilonRRPerturbation 实例并进行扰动
                rr_perturber = RRPerturbation(adjacency_matrix, privacy_budget / 2)
                perturbed_adjacency_matrix = rr_perturber.perturb()
                # 创建 LouvainClustering 实例
                clustering_algo = LouvainClustering(perturbed_adjacency_matrix)
                # 运行 Louvain 算法进行社区划分
                LF_GDPR_result = clustering_algo.run()
                print('LF_GDPR_result:', LF_GDPR_result)
                print('ground_truth:', ground_truth)

                timeEnd_LF_GDPR = time.time()

                # print('LF_GDPR_result:',LF_GDPR_result)
                # draw_spring(G, convert_res_To_clsuterlist(LF_GDPR_result))
                print("---------LF-GDPR END------------")

                "3.2 LDPGen"
                timeStart_LDPGen = time.time()
                # 簇数量
                num_clusters = 2
                # 聚簇
                graph_clustering = LDPGen(G, num_clusters, privacy_budget)
                graph_clustering.kmeans()
                # print(graph_clustering.clusters)
                LDPGen_result = graph_clustering.get_community_partition()

                timeEnd_LDPGen = time.time()

                print("---------LDPGen END------------")

                "3.3 GCC-LDP"
                timeStart_GCC = time.time()
                # 聚簇
                clusters = GCC_LDP_Run(G, threshold_d, threshold_beta, threshold_s, privacy_budget)
                # draw_spring(G, clusters)
                timeEnd_GCC = time.time()

                GCC_LDP_result = cluster_list_To_mapping(clusters)

                print("---------GCC-LDP END------------")

                """-----------------4.结果评估----------------------------------------------------"""
                "4.1 LF-GDPR"
                print("----------LF_GDPR Result------------")
                # Create CommunityMetrics instance
                # print_metrics(G, LF_GDPR_result, ground_truth)
                LF_GDPR_metrics_lists.append(calculate_metrics(G, LF_GDPR_result, ground_truth))
                LF_GDPR_RunTime_sum += timeEnd_LF_GDPR - timeStart_LF_GDPR

                "4.2 LDPGen"
                print("----------LDPGen Result------------")
                # Create CommunityMetrics instance
                # print_metrics(G, LDPGen_result, ground_truth)
                LDPGen_metrics_lists.append(calculate_metrics(G, LDPGen_result, ground_truth))
                LDPGen_RunTime_sum += timeEnd_LDPGen - timeStart_LDPGen

                "4.3 GCC-LDP"
                print("----------GCC-LDP Result------------")
                # Create CommunityMetrics instance
                # print_metrics(G, GCC_LDP_result, ground_truth)
                GCC_metrics_lists.append(calculate_metrics(G, GCC_LDP_result, ground_truth))
                GCC_RunTime_sum += timeEnd_GCC - timeStart_GCC

            "输出结果"
            "5.1 LF_GDPR" "5.2 LDPGen" "5.3 GCC"
            "5.1 LF_GDPR"
            # 获取每列的最大值
            LF_GDPR_max_metrics = [max(row) for row in zip(*LF_GDPR_metrics_lists)]

            # 获取每列的均值
            LF_GDPR_mean_values = [sum(row) / len(row) for row in zip(*LF_GDPR_metrics_lists)]

            output_file_max = 'output/' + 'comparison_' + file + '_max.txt'
            output_file_mean = 'output/' + 'comparison_' + file + '_mean.txt'
            print_metricsMax_to_file(output_file_max, LF_GDPR_max_metrics, 'LF_GDPR',
                                     LF_GDPR_RunTime_sum / loop_max, privacy_budget, threshold_d,
                                     threshold_beta)
            print_metricsMean_to_file(output_file_mean, LF_GDPR_mean_values, 'LF_GDPR',
                                      LF_GDPR_RunTime_sum / loop_max, privacy_budget, threshold_d,
                                      threshold_beta)

            "5.2 LDPGen"
            # 获取每列的最大值
            LDPGen_max_metrics = [max(row) for row in zip(*LDPGen_metrics_lists)]

            # 获取每列的均值
            LDPGen_mean_values = [sum(row) / len(row) for row in zip(*LDPGen_metrics_lists)]

            output_file_max = 'output/' + 'comparison_' + file + '_max.txt'
            output_file_mean = 'output/' + 'comparison_' + file + '_mean.txt'
            print_metricsMax_to_file(output_file_max, LDPGen_max_metrics, 'LDPGen',
                                     LDPGen_RunTime_sum / loop_max, privacy_budget, threshold_d, threshold_beta)
            print_metricsMean_to_file(output_file_mean, LDPGen_mean_values, 'LDPGen',
                                      LDPGen_RunTime_sum / loop_max, privacy_budget, threshold_d,
                                      threshold_beta)

            "5.3 GCC"
            # 获取每列的最大值
            GCC_max_metrics = [max(row) for row in zip(*GCC_metrics_lists)]

            # 获取每列的均值
            GCC_mean_values = [sum(row) / len(row) for row in zip(*GCC_metrics_lists)]

            output_file_max = 'output/' + 'comparison_' + file + '_max.txt'
            output_file_mean = 'output/' + 'comparison_' + file + '_mean.txt'
            print_metricsMax_to_file(output_file_max, GCC_max_metrics, 'GCC', GCC_RunTime_sum / loop_max,
                                     privacy_budget, threshold_d, threshold_beta)
            print_metricsMean_to_file(output_file_mean, GCC_mean_values, 'GCC', GCC_RunTime_sum / loop_max,
                                      privacy_budget, threshold_d, threshold_beta)
