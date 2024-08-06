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
import threading
import time
from typing import List, Set

import networkx as nx

from ditto.network import NetContainer
from ditto.blockdag import TypeAlias, BlockDAG

from ditto.nodes.consensus import ConsusIface, StatusType


class PhantomCons(ConsusIface):
    """
    In phantom consensus, blocks are cumulatively added to a blue set by maximum k-cluster algorithm.
    """

    def __init__(self, network: NetContainer, blockdag: BlockDAG):
        super().__init__(network, blockdag)
        self._k = 3
        self._blue_set = {}
        self._ordered_list = {}

        self._latest_blue_set = set()
        self._latest_ordered_list = list()

        self._thread_lock = False

    def _consensus_thread(self):
        if self._thread_lock:
            self._latest_blue_set, self._latest_ordered_list = self._order_dag(self.blockdag.graph(), self._k)
            self._thread_lock = False

    def execute_consensus(self):

        # if not self._thread_lock:
        #     self._thread_lock = True
        #     thread_consensus = threading.Thread(target=self._consensus_thread)
        #     thread_consensus.start()

        self._latest_blue_set, self._latest_ordered_list = self._order_dag(self.blockdag.graph(), self._k)

    def block_status(self, bid) -> StatusType:
        if bid not in self.blockdag:
            return StatusType.INVALID
        elif bid not in self._latest_ordered_list:
            return StatusType.UNCLEAR
        elif bid in self._latest_blue_set:
            return StatusType.DECIDED
        else:
            return StatusType.EXCLUDE

    def get_processed_blocks(self, status: StatusType = None) -> Set[TypeAlias.BlockID]:
        if status is None:
            return set(self._latest_ordered_list)

        if status == StatusType.DECIDED:
            return set(self._latest_blue_set)
        elif status == StatusType.EXCLUDE:
            return set(self._latest_ordered_list) - set(self._latest_blue_set)

        return set()

    def sort_finished_blocks(self, status: StatusType = None) -> List[TypeAlias.BlockID]:
        if status is None:
            return list(self._latest_ordered_list)

        if status == StatusType.DECIDED:
            return sorted(self._latest_blue_set)
        elif status == StatusType.EXCLUDE:
            return sorted(set(self._latest_ordered_list) - set(self._latest_blue_set))

        return list()

    def _order_dag(self, graph: nx.DiGraph, k: int) -> (Set[TypeAlias.BlockID], List[TypeAlias.BlockID]):
        if len(graph) == 1:
            genesis_bid = list(graph.nodes)[0]
            return {genesis_bid}, [genesis_bid]

        tips = sorted([nod for nod, ind in graph.in_degree if ind == 0])
        sel_len = 0
        sel_node = tips[0]
        for node in tips:
            if node not in self._blue_set:
                blue, ordered = self._order_dag(self._get_past(graph, node), k)
                self._blue_set[node] = blue
                self._ordered_list[node] = ordered

            blue_nodes = self._blue_set[node]
            if len(blue_nodes) > sel_len:
                sel_len = len(blue_nodes)
                sel_node = node

        blue_set_g = self._blue_set[sel_node].copy()
        ordered_list_g = self._ordered_list[sel_node].copy()

        blue_set_g.add(sel_node)
        ordered_list_g.append(sel_node)

        for node in sorted(self._get_anticone(sel_node, graph)):
            if len(blue_set_g & self._get_anticone(node, graph)) <= k:
                blue_set_g.add(node)
            ordered_list_g.append(node)

        return blue_set_g, sorted(ordered_list_g)

    def _get_anticone(self, bid: TypeAlias.BlockID, graph: nx.DiGraph) -> Set[TypeAlias.BlockID]:
        # Require that the bid is in the graph.
        cone = {bid}.union(nx.descendants(graph, bid)).union(nx.ancestors(graph, bid))
        return set(graph.nodes).difference(cone)

    def _get_past(self, graph: nx.DiGraph, bid: TypeAlias.BlockID) -> nx.DiGraph:
        # Require that the bid is in the graph.
        views = nx.descendants(graph, bid)
        return graph.subgraph(views)


if __name__ == "__main__":
    print("Phantom Consensus.")
    g = nx.DiGraph()
    # The same graph of Figure 2 in the paper.
    g.add_nodes_from(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K'])
    g.add_edges_from([('B', 'A'), ('C', 'A'), ('D', 'A'), ('E', 'A'),
                      ('F', 'B'), ('J', 'B'), ('F', 'C'), ('G', 'C'),
                      ('I', 'D'), ('G', 'D'), ('K', 'D'), ('J', 'E'), ('H', 'E'),
                      ('I', 'F'), ('J', 'G'), ('K', 'H')])

    cons = PhantomCons(network=None, blockdag=None)
    print("The anticone set of node D is: ",
          sorted(cons._get_anticone('D', g)))  # The result should be {'B', 'C', 'E', 'F', 'H'}

    sg = cons._get_past(g, 'K')
    print("past graph of node K: ", sorted(sg.nodes), sg.edges)  # The result should be {'A', 'D', 'E', 'H'}

    print(cons._order_dag(g, 3))
    print(cons._get_anticone('E', g))

    print("blueset: ", cons._blue_set)
    print("orderedlist: ", cons._ordered_list)
