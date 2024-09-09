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
import networkx as nx

from ditto.blockdag import BlockDAG, TypeAlias
from ditto.network import NetContainer
from ditto.nodes.consensus import ConsusIface


class PikavoltCons(ConsusIface):
    """
    The proposed scheme, using confirmed blocks to denote vertex which is a set of blocks.
    Any two vertices define a weighted edge via intersection of their sets.

    Pikavolt uses the notion of clustering coefficient to define the extent of convergence.
    The modularity and x-means techniques are used to find the clusters.
    """

    def __init__(self, network: NetContainer, blockdag: BlockDAG):
        super().__init__(network, blockdag)
        self._d = 6
        self._height = 0
        self._col_dec_set = []
        self._col_ord_lst = []

    def execute_consensus(self):
        self.decided_set, self.ordered_list = self._compute_cluster(self.blockdag.graph(),
                                                                    self.blockdag.column_blocks,
                                                                    self._d)

    def _scale(self, bids: set | frozenset | TypeAlias.BlockID, graph: nx.DiGraph) -> int:
        """ Return the number of ancestors of the block or blocks. """
        bids = {bids} if isinstance(bids, TypeAlias.BlockID) else set(bids)
        return len({a for bid in bids for a in nx.ancestors(graph, bid)})

    def _weight(self, bids1: set | frozenset | TypeAlias.BlockID,
                bids2: set | frozenset | TypeAlias.BlockID, graph: nx.DiGraph) -> int:
        """ Return the number of common ancestors of the blocks. """
        bids1 = {bids1} if isinstance(bids1, TypeAlias.BlockID) else set(bids1)
        c1 = {a for bid in bids1 for a in nx.ancestors(graph, bid)}
        bids2 = {bids2} if isinstance(bids2, TypeAlias.BlockID) else set(bids2)
        c2 = {a for bid in bids2 for a in nx.ancestors(graph, bid)}
        return len(c1 & c2)

    def _coefficient(self, bids: set, graph: nx.DiGraph) -> float:
        """
        The number of common ancestors divided by the minimum number of ancestors.
        The division is treat as clustering coefficient.
        """
        if len(bids) == 1:
            return 1.0
        cur_wei = sum([self._weight(bi, bj, graph)
                       for bi in bids for bj in bids if bi != bj]) / 2
        max_wei = sum([min(self._scale(bi, graph), self._scale(bj, graph))
                       for bi in bids for bj in bids if bi != bj]) / 2
        if max_wei == 0:
            return 0.0
        return cur_wei / max_wei

    def _binary_clustering(self, bids: set, graph: nx.DiGraph) -> set:
        """
        The binary clustering algorithm.
        :param bids:
        :param graph:
        :return:
        """
        if len(bids) <= 2:
            return {frozenset({b}) if isinstance(b, TypeAlias.BlockID) else frozenset(b) for b in bids}
        lst = [(self._weight(bi, bj, graph), min(self._scale(bi, graph), self._scale(bj, graph)), (bi, bj))
               for bi in bids for bj in bids if bi != bj]
        lst.sort(key=lambda x: (x[0], x[1]), reverse=True)
        com1, com2 = lst[0][2]
        new_bids = set(bids)
        new_bids.difference_update({com1, com2})
        com1u2 = frozenset()
        com1u2 = com1u2.union(frozenset({com1}) if isinstance(com1, TypeAlias.BlockID) else frozenset(com1))
        com1u2 = com1u2.union(frozenset({com2}) if isinstance(com2, TypeAlias.BlockID) else frozenset(com2))
        new_bids.add(com1u2)
        # new_bids.add(frozenset(com1).union(frozenset(com2)))
        return self._binary_clustering(new_bids, graph)

    def _extend_clustering(self, bids: set, graph: nx.DiGraph) -> list:
        if len(bids) == 1:
            return [bids]

        res = [bids]

        while True:
            # The value without binary clustering
            curr = res[0]
            val_curr = self._coefficient(curr, graph) * self._scale(curr, graph)

            # The value with binary clustering
            clas = self._binary_clustering(curr, graph)
            val_clas = (sum([self._coefficient(bs, graph) * self._scale(bs, graph) for bs in clas])
                        - 2 * pow(self._coefficient(clas, graph), 2) * self._scale(curr, graph))

            if val_clas > val_curr:  # The condition to stop binary clustering
                c1 = clas.pop()
                c2 = clas.pop()
                if self._coefficient(c1, graph) * self._scale(c1, graph) < \
                        self._coefficient(c2, graph) * self._scale(c2, graph):
                    c1, c2 = c2, c1
                res = [c1, c2] + res[1:]
            else:
                break

        return res

    def _compute_cluster(self, graph: nx.DiGraph, columns: list[set[TypeAlias.BlockID]], d: int):
        i = self._height - d
        # blue_set = self.decided_set
        # ord_list = self.ordered_list
        while i < len(columns):
            i = i + 1
            if i < d:
                continue
            x = i - d
            nodes_i = {n for c in columns[:i] for n in c}
            nodes_x = {n for c in columns[:x] for n in c}
            g = graph.subgraph(nodes_i - nodes_x)

            r = self._extend_clustering(columns[x], g)

            # blue_set.update(r[0])
            # ord_list.extend(sorted(r[0]))
            # ord_list.extend(sorted(columns[x] - set(r[0])))

            if len(self._col_dec_set) <= x:
                self._col_dec_set.append(r[0])
            else:
                self._col_dec_set[x] = r[0]

            if len(self._col_ord_lst) <= x:
                self._col_ord_lst.append(sorted(r[0]) + sorted(columns[x] - set(r[0])))
            else:
                self._col_ord_lst[x] = sorted(r[0]) + sorted(columns[x] - set(r[0]))

        self._height = len(columns)

        return {d for st in self._col_dec_set for d in st}, [o for lt in self._col_ord_lst for o in lt]


if __name__ == "__main__":
    print("Pikavolt Consensus.")
    g = nx.DiGraph()
    # The same graph of Phantom example.
    g.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    g.add_edges_from([(2, 1), (3, 1), (4, 1), (5, 1),
                      (6, 2), (10, 2), (6, 3), (7, 3),
                      (9, 4), (7, 4), (11, 4), (10, 5), (8, 5),
                      (9, 6), (10, 7), (11, 8)])
    cols = [{1}, {2, 3, 4, 5}, {6, 7, 8}, {9, 10, 11}]

    cons = PikavoltCons(network=None, blockdag=None)

    # print(cons._scale(2, g))

    # print(cons._weight(5, frozenset({2, 3}), g))

    # print(cons._coefficient({5, frozenset({2, 3})}, g))

    # print(cons._binary_clustering({2, 3, 4, 5}, g))

    print(cons._extend_clustering({2, 3, 5}, g))

    g.add_edges_from([(12, 9), (12, 10), (12, 11), (13, 9), (13, 10), (13, 11)])

    print(cons._extend_clustering({2, 3, 5}, g))

    # print(cons._compute_cluster(g, cols, 2))
