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

from ditto.network import NetContainer
from ditto.blockdag import TypeAlias, BlockDAG

from ditto.nodes.consensus import ConsusIface


class NakamotoCons(ConsusIface):
    """
    In nakamoto consensus, blocks with depth of 6 can be safely decided.
    """

    def __init__(self, network: NetContainer, blockdag: BlockDAG):
        super().__init__(network, blockdag)
        self._safe_depth = 6

    def execute_consensus(self, bid: TypeAlias.BlockID):
        return self._longest_chain(self.blockdag.graph(), self.blockdag.column_blocks, self._safe_depth)

    def _longest_chain(self, graph: nx.DiGraph, columns: List[Set[TypeAlias.BlockID]], depth: int) \
            -> (Set[TypeAlias.BlockID], List[TypeAlias.BlockID]):
        # Check the safe depth.
        if len(columns) <= depth:
            return set(), list()

        picked_bid = min(columns[-1])  # Pick the block in the longest chain.
        # Find the last block in the longest chain within the safe depth.
        last_bid = [bid for bid in columns[-1 - depth] if nx.has_path(graph, picked_bid, bid)][0]

        cons_blocks = set(nx.descendants(graph, last_bid)).union({last_bid})
        sorted_blocks = [n for c in columns[:-1 - depth + 1] for n in sorted(c)]

        return cons_blocks, sorted_blocks


if __name__ == '__main__':
    print("Nakamoto Consensus.")
    g = nx.DiGraph()

    g.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
    g.add_edges_from([(2, 1), (3, 2), (4, 3), (5, 3), (6, 3), (7, 6),
                      (8, 7), (9, 8), (10, 9), (11, 9), (12, 11), (13, 12)])

    colunms = [{1}, {2}, {3}, {4, 5, 6}, {7}, {8}, {9}, {10, 11}, {12}, {13}]

    cons = NakamotoCons(network=None, blockdag=None)
    print(colunms[-1 - 6])
    print(cons._longest_chain(g, colunms, 6))

    g = nx.DiGraph()
    g.add_nodes_from([1, 2, 3, 4, 5, 6])
    g.add_edges_from([(2, 1), (3, 2), (4, 3), (5, 4), (6, 5)])
    colunms = [{1}, {2}, {3}, {4}, {5}, {6}]
    print(cons._longest_chain(g, colunms, 6))
