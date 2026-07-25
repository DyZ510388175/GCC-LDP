import networkx as nx
from collections import Counter


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
        for i, compressed_set in enumerate(self.compressed_sets):
            adjacency_vector = self.calculate_adjacency_vector(i)
            for j, val in enumerate(adjacency_vector):
                if val == 1:
                    adjacency_frequencies[j] += 1
        return adjacency_frequencies

    def calculate_pair_frequencies(self, pair_nodes):
        pair_frequencies = Counter()
        for i, compressed_set in enumerate(self.compressed_sets):
            adjacency_vector = self.calculate_adjacency_vector(i)
            for pair in pair_nodes:
                j, k = pair
                if adjacency_vector[j] == adjacency_vector[k] == 1:
                    pair_frequencies[pair] += 1
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



if __name__ == "__main__":
    karate_graph = nx.karate_club_graph()
    threshold = 5

    gem_algo = GEMAlgorithm(karate_graph, threshold)
    compressed_sets = gem_algo.gem_first_round()
    print(compressed_sets)


