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


def print_metrics_to_file(graph, clusters, ground_truth, output_file, threshold_d, threshold_beta):
    metrics_calculator = CommunityMetrics(graph, clusters, ground_truth)

    with open(output_file, 'a') as file:
        file.write("threshold_d,threshold_beta: {} {}\n".format(threshold_d, threshold_beta))
        # file.write("ground_truth: {}\n".format(ground_truth))
        # file.write("clusters: {}\n".format(clusters))
        file.write("Modularity: {}\n".format(metrics_calculator.modularity()))
        file.write("Normalized Mutual Information: {}\n".format(metrics_calculator.normalized_mutual_info()))
        file.write("F1 Score: {}\n".format(metrics_calculator.f1()))
        file.write("Adjusted Rand Index: {}\n".format(metrics_calculator.adjusted_rand_index()))
        file.write("Adjusted Mutual Information: {}\n".format(metrics_calculator.adjusted_mutual_info()))
        file.write("Relative Entropy: {}\n".format(metrics_calculator.relative_entropy()))
        file.write("\n")  # 添加一个空行来分隔不同的追加记录


def print_metricsMax_to_file(output_file, max_metrics, threshold_d, threshold_beta):
    with open(output_file, 'a') as file:
        file.write("threshold_d,threshold_beta: {} {}\n".format(threshold_d, threshold_beta))
        # file.write("ground_truth: {}\n".format(ground_truth))
        # file.write("clusters: {}\n".format(clusters))
        file.write("Modularity: {}\n".format(max_metrics[0]))
        file.write("Normalized Mutual Information: {}\n".format(max_metrics[1]))
        file.write("F1 Score: {}\n".format(max_metrics[2]))
        file.write("Adjusted Rand Index: {}\n".format(max_metrics[3]))
        file.write("Adjusted Mutual Information: {}\n".format(max_metrics[4]))
        file.write("Relative Entropy: {}\n".format(max_metrics[5]))
        file.write("\n")  # 添加一个空行来分隔不同的追加记录


def print_metricsMean_to_file(output_file, means_metrics, threshold_d, threshold_beta):
    with open(output_file, 'a') as file:
        file.write("threshold_d,threshold_beta: {} {}\n".format(threshold_d, threshold_beta))
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

    privacy_budget = 5
    loop_max = 10  # 算法循环次数

    # G = nx.karate_club_graph()

    # 从外部文本文件中读取图数据并创建 G2
    # gemsec_deezer facebook_combined Email-Enron CA-CondMat musae_ES_edges_sample musae_git_edges_sample CA-HepTh_sample
    # musae_PTBR_edges_sample
    # 测试数据集
    filename = ['musae_PTBR_edges_sample', 'facebook_combined_sample', 'musae_ES_edges_sample']
    # filename = ['karate', 'email_sample', 'gemsec_deezer_sample', 'facebook_combined_sample', 'Email-Enron_sample',
    #             'CA-CondMat_sample', 'musae_ES_edges_sample', 'musae_git_edges_sample', 'CA-HepTh_sample', 'musae_PTBR_edges_sample']
    threshold_ds = [5, 10, 15, 20, 25]  # 设置外围节点阈值
    threshold_betas = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5]  # 设置连接强度阈值
    for file_idx, file in enumerate(filename):
        read_G = nx.read_edgelist('dataset/' + file + '.txt')
        G = processing_indexOfnodes(read_G)

        """-----------------2.数据真实标签----------------------------------------------------"""
        for t_d in threshold_ds:
            for t_beta in threshold_betas:
                threshold_d = t_d  # 设置外围节点阈值
                threshold_beta = t_beta  # 设置连接强度阈值
                threshold_s = 2.5  # 设置相似度阈值
                clusters = GCC_Run(G, threshold_d, threshold_beta, threshold_s)

                ground_truth = cluster_list_To_mapping(clusters)

                """簇格式转化"""
                ground_truth = []
                for idx, cluster in enumerate(clusters):
                    for element in cluster:
                        ground_truth.insert(element, idx)

                metrics_lists = []  # 存储多次循环的指标值
                metrics_list_mean = []  # 存储指标的均值
                metrics_list_max = []  # 存储指标的最大值
                for loop in range(loop_max):
                    """-----------------3.聚类算法----------------------------------------------------"""
                    print("---------GCC-LDP Start!----filename, threshold_d, threshold_beta, loop:{} {} {} {}\n".format(
                        file, threshold_d, threshold_beta, loop))
                    "3.3 GCC-LDP"
                    # 聚簇
                    clusters = GCC_LDP_Run(G, threshold_d, threshold_beta, threshold_s, privacy_budget)
                    # draw_spring(G, clusters)
                    GCC_LDP_result = cluster_list_To_mapping(clusters)
                    # print('ground_truth:', ground_truth)
                    # print('GCC_LDP_result:', GCC_LDP_result)
                    print("---------GCC-LDP END------------")

                    """-----------------4.结果评估----------------------------------------------------"""
                    "4.3 GCC-LDP"
                    print("----------GCC-LDP Result------------")
                    # Create CommunityMetrics instance
                    metrics_lists.append(calculate_metrics(G, GCC_LDP_result, ground_truth))

                    # output_file = 'output/' + file + '.txt'
                    # print_metrics_to_file(G, GCC_LDP_result, ground_truth, output_file, threshold_d, threshold_beta)

                # 获取每列的最大值
                max_metrics = [max(row) for row in zip(*metrics_lists)]

                # 获取每列的均值
                mean_values = [sum(row) / len(row) for row in zip(*metrics_lists)]

                output_file_max = 'output/' + 'parameter_' + file + '_max.txt'
                output_file_mean = 'output/' + 'parameter_' + file + '_mean.txt'
                print_metricsMax_to_file(output_file_max, max_metrics, threshold_d, threshold_beta)
                print_metricsMean_to_file(output_file_mean, mean_values, threshold_d, threshold_beta)

                # print('max_metrics:', max_metrics)
                # print('mean_values:', mean_values)
