import numpy as np


def read_data(file_path):
    # 读取数据
    data = np.loadtxt(file_path, dtype=int)
    return data


def calculate_degrees(edges):
    # 计算每个节点的度数
    node_degrees = {}
    for edge in edges:
        for node in edge:
            if node in node_degrees:
                node_degrees[node] += 1
            else:
                node_degrees[node] = 1
    return node_degrees


def calculate_ratio(node_degrees, X):
    # 计算度数大于 X 的节点数量
    num_nodes_greater_than_X = sum(1 for degree in node_degrees.values() if degree > X)
    # 计算总节点数
    total_nodes = len(node_degrees)
    # 计算比例
    ratio = num_nodes_greater_than_X / total_nodes if total_nodes > 0 else 0
    return num_nodes_greater_than_X, total_nodes, ratio


def main():
    "facebook_combined.txt 度数大于 20 的节点占总节点数的比例: 56.40%"
    "email.txt 度数大于 10 的节点占总节点数的比例: 56.22%"
    "musae_PTBR_edges.txt 度数大于 15 的节点占总节点数的比例: 52.51%"
    file_path = '../dataset/musae_PTBR_edges.txt'  # 替换为你的数据文件路径
    X = 15  # 设定边数阈值 X

    # 读取数据
    edges = read_data(file_path)

    # 计算每个节点的度数
    node_degrees = calculate_degrees(edges)

    # 计算比例
    num_nodes_greater_than_X, total_nodes, ratio = calculate_ratio(node_degrees, X)

    # 输出结果
    print(f'度数大于 {X} 的节点数: {num_nodes_greater_than_X}')
    print(f'总节点数: {total_nodes}')
    print(f'度数大于 {X} 的节点占总节点数的比例: {ratio * 100:.2f}%')


if __name__ == '__main__':
    main()
