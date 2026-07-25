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
    G2=graph
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
    # G = nx.karate_club_graph()

    # 从外部文本文件中读取图数据并创建 G2
    # karate sampled_edges
    read_G = nx.read_edgelist('dataset/sampled_edges.txt')
    G = processing_indexOfnodes(read_G)

    print('len(G.nodes):', len(G.nodes))
    print('G.edges:', G.edges)
    print('G.nodes:', G.nodes)

    """-----------------2.数据真实标签----------------------------------------------------"""
    # 为graph分配标签
    '''kernighan_lin_bisection算法'''
    # clusters = list(nx.algorithms.community.kernighan_lin_bisection(G))
    # draw_spring(G, clusters)
    """簇格式转化"""
    # ground_truth = []
    # for idx, cluster in enumerate(clusters):
    #     for element in cluster:
    #         ground_truth.insert(element, idx)
    """label_propagation_communities标签传播算法"""
    # clusters = list(nx.algorithms.community.label_propagation_communities(G))
    # print('clusters:', clusters)
    # draw_spring(G, clusters)
    """簇格式转化"""
    # ground_truth = []
    # for idx, cluster in enumerate(clusters):
    #     for element in cluster:
    #         ground_truth.insert(element, idx)

    """Louvain Algorithm标签传播算法"""
    # clusters = community.best_partition(G)
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

    # draw_spring(G, format_clusters)

    "GCC-LDP"
    threshold_d = 2  # 设置外围节点阈值
    threshold_beta = 0.05  # 设置连接强度阈值
    threshold_s = 2.5  # 设置相似度阈值
    clusters = GCC_Run(G, threshold_d, threshold_beta, threshold_s)

    ground_truth = cluster_list_To_mapping(clusters)
    """簇格式转化"""
    ground_truth = []
    for idx, cluster in enumerate(clusters):
        for element in cluster:
            ground_truth.insert(element, idx)

    """-----------------3.聚类算法----------------------------------------------------"""
    "3.1 LF-GDPR"
    # graph聚类
    adjacency_matrix = nx.adjacency_matrix(G).toarray()
    # 创建 EpsilonRRPerturbation 实例并进行扰动
    rr_perturber = RRPerturbation(adjacency_matrix, privacy_budget / 2)
    perturbed_adjacency_matrix = rr_perturber.perturb()
    # 创建 LouvainClustering 实例
    clustering_algo = LouvainClustering(perturbed_adjacency_matrix)
    # 运行 Louvain 算法进行社区划分
    LF_GDPR_result = clustering_algo.run()

    # print('LF_GDPR_result:',LF_GDPR_result)
    # draw_spring(G, convert_res_To_clsuterlist(LF_GDPR_result))
    print("---------LF-GDPR END------------")

    "3.2 LDPGen"
    # 簇数量
    num_clusters = 2
    # 聚簇
    graph_clustering = LDPGen(G, num_clusters, privacy_budget)
    graph_clustering.kmeans()
    # print(graph_clustering.clusters)
    LDPGen_result = graph_clustering.get_community_partition()

    print("---------LDPGen END------------")

    "3.3 GCC-LDP"
    # 聚簇
    # GCC_LDP_result = GCC_LDP_Run(G, threshold_d=1, threshold_beta=0.1)
    # graph = nx.karate_club_graph()
    threshold_d = 1  # 设置外围节点阈值
    threshold_beta = 0.1  # 设置连接强度阈值
    threshold_s = 2.5  # 设置相似度阈值
    clusters = GCC_LDP_Run(G, threshold_d, threshold_beta, threshold_s, privacy_budget)
    draw_spring(G, clusters)

    GCC_LDP_result = cluster_list_To_mapping(clusters)

    print("---------GCC-LDP END------------")

    """-----------------4.结果评估----------------------------------------------------"""
    "4.1 LF-GDPR"
    print("----------LF_GDPR Result------------")
    # Create CommunityMetrics instance
    print_metrics(G, LF_GDPR_result, ground_truth)

    "4.2 LDPGen"
    print("----------LDPGen Result------------")
    # Create CommunityMetrics instance
    print_metrics(G, LDPGen_result, ground_truth)

    "4.3 GCC-LDP"
    print("----------GCC-LDP Result------------")
    # Create CommunityMetrics instance
    print_metrics(G, GCC_LDP_result, ground_truth)
