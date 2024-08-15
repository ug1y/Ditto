#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2024 Hao Yin

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from typing import List, Set

import networkx as nx
import numpy as np

from ditto.blockdag import TypeAlias, BlockDAG
from ditto.network import NetContainer

from ditto.nodes.consensus import ConsusIface


class ULBlockDAGCons(ConsusIface):
    """
    In UL-BlockDAG consensus, the number of confirmations acts as a sliding window.
    """

    def __init__(self, network: NetContainer, blockdag: BlockDAG):
        super().__init__(network, blockdag)
        self._k = 6

    def execute_consensus(self):
        self.decided_set, self.ordered_list = self._find_list_order(self.blockdag.graph(),
                                                                    self.blockdag.column_blocks,
                                                                    self._k)

    def _find_clusters(self, graph: nx.DiGraph) -> (Set[TypeAlias.BlockID], Set[TypeAlias.BlockID]):
        nodelist = sorted(graph.nodes)
        #  Construct the adjacency matrix
        adj = nx.to_numpy_array(graph, nodelist=nodelist)
        # Compute the symmetric adjacency matrix
        sym_adj = adj + adj.T
        # Compute the degree matrix
        deg = np.diag(np.sum(sym_adj, axis=1))
        # Compute the Laplacian matrix
        lap = deg - sym_adj

        # Compute the eigenvalues and eigenvectors
        eigenvalues, eigenvectors = np.linalg.eig(lap)
        # Get the 2nd smallest eigenvalue
        sort_eigen = sorted(zip(eigenvalues, eigenvectors), key=lambda pair: pair[0])
        if len(sort_eigen) < 2:
            return set(nodelist), set()
        second_value, second_vector = sort_eigen[1]

        # Get the clusters of binary classification
        c1, c2 = set(), set()
        for i, x in enumerate(second_vector):
            if x >= 0:
                c1.add(nodelist[i])
            else:
                c2.add(nodelist[i])

        # C1 is classified to blue set, and C2 is classified to red set
        return c1, c2

    def _find_list_order(self, graph: nx.DiGraph, columns: List[Set[TypeAlias.BlockID]], k: int) \
            -> (Set[TypeAlias.BlockID], List[TypeAlias.BlockID]):
        # The code is followed the algorithm in the paper.
        # However, the example figure seems to be different from the algorithm.
        # It is so wired.
        i, x = 0, 0
        blue_list = set(columns[0])
        ord_list = list(columns[0])
        while i < len(columns):
            i = i + 1
            if i > k:
                x = x + 1
            # Get the blocks with the height less than i
            nodes_i = {n for c in columns[:i] for n in c}
            # Get the blocks with the height less than x
            nodes_x = {n for c in columns[:x] for n in c} if x > 0 else set()
            # Get the graph in the windows of k
            nodes_k = nodes_i - nodes_x
            g = graph.subgraph(nodes_k)

            # Find the clusters
            c1, c2 = self._find_clusters(g)

            if x > 0:
                blue_list.update(c1 & columns[x])
                ord_list.extend(sorted(columns[x]))

        return blue_list, ord_list

    def _find_list_order_by_figure(self, graph: nx.DiGraph, columns: List[Set[TypeAlias.BlockID]], k: int) \
            -> (Set[TypeAlias.BlockID], List[TypeAlias.BlockID]):
        # If using the whole graph to find the clusters, it will be slow with the size of the graph.
        # By testing, the effect is similar to the algorithm by the sliding window.
        i = len(columns)
        x = i - k if i > k else 0
        # Get the confirmed blocks
        nodes_c = {n for c in columns[:x+1] for n in c}
        # Find the clusters
        c1, c2 = self._find_clusters(graph)

        blue_list = c1 & nodes_c
        ord_list = [n for c in columns[:x+1] for n in sorted(c)]

        return blue_list, ord_list


if __name__ == '__main__':
    G = nx.DiGraph()
    G.add_edges_from([(2, 1), (3, 1), (6, 1), (4, 2), (5, 2), (4, 3), (5, 3)])

    cons = ULBlockDAGCons(network=None, blockdag=None)
    print(cons._find_clusters(G))

    G = nx.DiGraph()
    G.add_edges_from([(3, 0), (1, 0), (2, 0),
                      (5, 3), (5, 1), (4, 3), (4, 1), (4, 2), (6, 1), (6, 2),
                      (8, 5), (8, 4), (7, 5), (7, 4), (7, 6), (9, 4), (9, 6),
                      (11, 8), (11, 7), (10, 8), (10, 7), (10, 9),
                      (12, 10), (12, 11), (13, 10), (13, 11), (14, 10), (14, 11),
                      (15, 0), (16, 15), (17, 16), (18, 17), (19, 18),
                      (20, 12), (20, 13), (20, 14),
                      (21, 12), (21, 13), (21, 14), (21, 19),
                      (22, 13), (22, 14), (22, 19),
                      (23, 20), (23, 21), (23, 22),
                      (25, 20), (25, 21), (24, 21), (24, 22)])
    cols = [{0}, {1, 2, 3, 15}, {4, 5, 6, 16}, {7, 8, 9, 17}, {10, 11, 18}, {12, 13, 14, 19},
            {20, 21, 22}, {23, 24, 25}]

    print(cons._find_list_order(G, cols, 5))

    print(cons._find_list_order_by_figure(G, cols, 5))
