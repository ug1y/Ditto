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
import logging
from collections.abc import Collection
from typing import Iterator, Any, Set, List
import networkx as nx

from .block import Block, BlockType
from .typedef import TypeAlias, DAGType, EdgeType


def caller_info() -> str:
    """

    :return: str
    """
    import inspect
    stack = inspect.stack()
    caller_frame = stack[2]
    caller_module = caller_frame.frame.f_globals['__name__']
    if caller_module == '__main__':
        return "main"
    if caller_module == "ditto.network.netOperator" or caller_module == "ditto.network.netContainer":
        return "network"
    if caller_module == "ditto.nodes.miner":
        caller_object = caller_frame.frame.f_locals['self']
        return caller_object.name
    return ""


class BlockDAG(Collection):
    """
    An implementation of a generic BlockDAG, organizing blocks in a collection.

    Support to build the type of divergence, parallel, and convergence DAG.
    """

    # Dictionary key for the block's data.
    BLOCK_DATA_KEY = "block_data"
    # Dictionary key for the edge's type.
    EDGE_TYPE_KEY = "edge_type"

    def __init__(self, gtype: DAGType = DAGType.DIVERGENCE):
        self._dag = nx.DiGraph()  # A networkx directed graph object.
        self._gtype = gtype  # The type of the blockDAG.
        self._leaves = set()  # Set of all the leaves in the graph.
        self._column = list(set())  # List of the set of blocks in the specified height.

        self._logger: logging.Logger = None  # Logger for this class.

    def set_logger(self, logger: logging.Logger):
        self._logger = logger

    def __contains__(self, bid: type(TypeAlias.BlockID)) -> bool:
        return bid in self._dag

    def __iter__(self) -> Iterator[Block]:
        return iter(self._dag)

    def __len__(self) -> int:
        return len(self._dag)

    def __getitem__(self, bid) -> Block:
        return self._dag.nodes[bid][BlockDAG.BLOCK_DATA_KEY]

    def __str__(self):
        return str(self._dag)

    def __repr__(self):
        return "BlockDAG(type=" + repr(self._gtype) + \
            ", leaves=" + repr(self._leaves) + \
            ", cluster=" + repr(self._column) + ")"

    @property
    def graph_type(self) -> DAGType:
        """
        Get the type of the blockDAG.
        :return: DIVERGENCE=0 or PARALLEL=1 or CONVERGENCE=2.
        """
        return self._gtype

    @property
    def leaves_blocks(self) -> Set[TypeAlias.BlockID]:
        """
        Get the set of blocks located in the leaves of the graph.
        :return: list[TypeAlias.BlockID].
        """
        return self._leaves

    @property
    def column_blocks(self) -> List[Set[TypeAlias.BlockID]]:
        """
        Get the list of the set of blocks in the specified height of the graph.
        :return: list[Set[TypeAlias.BlockID]].
        """
        return self._column

    def get_pivot_chain(self, bid: TypeAlias.BlockID) -> List[TypeAlias.BlockID]:
        """
        Get the pivot chain if the graph type is convergence or parallel.
        :param bid: BlockID.
        :return: list[TypeAlias.BlockID].
        """
        if self._gtype == DAGType.DIVERGENCE:
            if self._logger is not None:
                self._logger.warning("%s: The divergence graph has no pivot chain.", caller_info())
            return []
        if bid not in self._dag:
            if self._logger is not None:
                self._logger.warning("%s: Block " + str(bid) + " does not exist.", caller_info())
            return []

        # Get the pivot chain.
        chain = []
        while True:
            chain.insert(0, bid)
            bid = self._dag.nodes[bid][BlockDAG.BLOCK_DATA_KEY].pref
            if bid is None:
                break
        return chain

    def add_block(self, block: Block) -> bool:
        """
        Add a block into the graph.
        :param block: Block.
        :return: true or false.
        """

        # Check the object type.
        if type(block) is not Block:
            if self._logger is not None:
                self._logger.warning("%s: Input is not an instance of Block.", caller_info())
            return False

        # Check if the block already exists.
        if self._dag.has_node(block.bid):
            if self._logger is not None:
                self._logger.warning("%s: Block " + str(block.bid) + " already exists.", caller_info())
            return False

        # Skip the orphan block.
        if block.btype == BlockType.ORPHAN:
            if self._logger is not None:
                self._logger.warning("%s: Orphan block cannot be added.", caller_info())
            return False

        # Handle the genesis block.
        if block.btype == BlockType.GENESIS:
            # Check the key data fields of the block.
            if block.miner is not None or block.pref is not None or len(block.crefs) != 0:
                if self._logger is not None:
                    self._logger.warning("%s: Genesis block must be empty.", caller_info())
                return False
            if block.height != 1:
                if self._logger is not None:
                    self._logger.warning("%s: Genesis block must be at height 1.", caller_info())
                return False
            # Except parallel graph, the divergence or convergence graph has only one genesis block.
            if self._gtype == DAGType.DIVERGENCE or self._gtype == DAGType.CONVERGENCE:
                if len(self._column) > 0 and len(self._column[0]) > 0:
                    if self._logger is not None:
                        self._logger.warning("%s: " + str(self._gtype.name) +
                                             "graph is only allowed to have one genesis block.",
                                             caller_info())
                    return False

            # Add the block into the graph.
            self._dag.add_node(block.bid)
            self._dag.nodes[block.bid][BlockDAG.BLOCK_DATA_KEY] = block
            self._leaves.add(block.bid)
            if len(self._column) == 0:
                self._column.append(set())
            self._column[0].add(block.bid)
            if self._logger is not None:
                self._logger.debug("%s: Genesis block " + str(block.bid) + " added.", caller_info())
            return True

        # Handle the mined block.
        if block.btype == BlockType.MINED:
            if block.miner is None:
                if self._logger is not None:
                    self._logger.warning("%s: Mined block must have a miner.", caller_info())
                return False

            # Check the key data fields of the block in the divergence graph.
            if self._gtype == DAGType.DIVERGENCE:
                if block.pref is not None:
                    if self._logger is not None:
                        self._logger.warning("%s: The block in " + str(self._gtype.name) +
                                             " graph has no pivot parent.", caller_info())
                    return False
                if len(block.crefs) == 0:
                    if self._logger is not None:
                        self._logger.warning("%s: The block in " + str(self._gtype.name) +
                                             " graph must have at least one reference.", caller_info())
                    return False
                max_h = 0
                for cref in block.crefs:
                    if cref not in self._dag:
                        if self._logger is not None:
                            self._logger.warning("%s: The referenced block " + str(cref) +
                                                 " does not exist.", caller_info())
                        return False
                    max_h = max(self._dag.nodes[cref][BlockDAG.BLOCK_DATA_KEY].height, max_h)
                if block.height != max_h + 1:
                    if self._logger is not None:
                        self._logger.warning("%s: Incorrect height of the mined block.", caller_info())
                    return False

            # Check the key data fields of the block in the parallel and convergence graph.
            elif self._gtype == DAGType.PARALLEL or self._gtype == DAGType.CONVERGENCE:
                if block.pref is None:
                    if self._logger is not None:
                        self._logger.warning("%s: The block in " + str(self._gtype.name) +
                                             " graph must have a pivot parent.", caller_info())
                    return False
                if block.pref not in self._dag:
                    if self._logger is not None:
                        self._logger.warning("%s: The pivot parent " + str(block.pref) +
                                             " does not exist.", caller_info())
                    return False
                if block.pref in block.crefs:
                    if self._logger is not None:
                        self._logger.warning("%s: The pivot parent is repeated in common references.", caller_info())
                    return False
                max_h = 0
                for cref in block.crefs:
                    if cref not in self._dag:
                        if self._logger is not None:
                            self._logger.warning("%s: The referenced block " + str(cref) +
                                                 " does not exist.", caller_info())
                        return False
                    max_h = max(self._dag.nodes[cref][BlockDAG.BLOCK_DATA_KEY].height, max_h)
                par_h = self._dag.nodes[block.pref][BlockDAG.BLOCK_DATA_KEY].height
                if max_h > par_h and self._gtype == DAGType.CONVERGENCE:
                    if self._logger is not None:
                        self._logger.warning("%s: Invalid height of the mined block.", caller_info())
                    return False
                if block.height != max(par_h, max_h) + 1:
                    if self._logger is not None:
                        self._logger.warning("%s: Incorrect height of the mined block.", caller_info())
                    return False

            # Add the block into the graph.
            self._dag.add_node(block.bid)
            self._dag.nodes[block.bid][BlockDAG.BLOCK_DATA_KEY] = block
            if block.pref is not None:
                self._dag.add_edge(block.bid, block.pref)
                self._dag.edges[(block.bid, block.pref)][BlockDAG.EDGE_TYPE_KEY] = EdgeType.PIVOT
                if block.pref in self._leaves:
                    self._leaves.remove(block.pref)
            for cref in block.crefs:
                self._dag.add_edge(block.bid, cref)
                self._dag.edges[(block.bid, cref)][BlockDAG.EDGE_TYPE_KEY] = EdgeType.COMMON
                if cref in self._leaves:
                    self._leaves.remove(cref)
            self._leaves.add(block.bid)
            if len(self._column) < block.height:
                self._column.append(set())
            self._column[block.height - 1].add(block.bid)
            if self._logger is not None:
                self._logger.debug("%s: Mined block " + str(block.bid) + " added.", caller_info())
            return True

        return False

    def cut_block(self, bid: TypeAlias.BlockID) -> bool | Any:
        """
        Cut the specified block and its related successors in the graph.
        :param bid: BlockID.
        :return: bool.
        """
        if bid not in self._dag:
            if self._logger is not None:
                self._logger.warning("%s: Block " + str(bid) + " does not exist.", caller_info())
            return False

        if bid not in self._leaves:
            for d in list(self.predecessors(bid)):
                if self.cut_block(d) is False:
                    return False

        b = self._dag.nodes[bid][BlockDAG.BLOCK_DATA_KEY]

        self._dag.remove_node(bid)
        self._leaves.remove(bid)
        self._column[b.height - 1].remove(bid)

        ps = b.get_parents()
        for p in ps:
            if len(list(self.predecessors(p))) == 0:
                self._leaves.add(p)
        if len(self._column[b.height - 1]) == 0:
            self._column.pop(b.height - 1)

        if self._logger is not None:
            self._logger.debug("%s: Block " + str(bid) + " has been cut.", caller_info())
        return True

    def ask_block(self, bid: TypeAlias.BlockID) -> Block | None:
        """
        Ask the specified block data in the graph.
        :param bid: BlockID.
        :return: Block.
        """
        if bid not in self._dag:
            if self._logger is not None:
                self._logger.warning("%s: Block " + str(bid) + " does not exist.", caller_info())
            return None
        return self._dag.nodes[bid][BlockDAG.BLOCK_DATA_KEY]

    def predecessors(self, bid: TypeAlias.BlockID) -> Iterator[TypeAlias.BlockID]:
        """
        Wrapper of the predecessors method in networkx.
        :param bid: BlockID.
        :return: Iterator[BlockID].
        """
        return self._dag.predecessors(bid)

    def successors(self, bid: TypeAlias.BlockID) -> Iterator[TypeAlias.BlockID]:
        """
        Wrapper of the successors method in networkx.
        :param bid: BlockID.
        :return: Iterator[BlockID].
        """
        return self._dag.successors(bid)

    def has_path(self, source: TypeAlias.BlockID, target: TypeAlias.BlockID) -> bool:
        """
        Wrapper of the has_path method in networkx.
        :param source: BlockID.
        :param target: BlockID.
        :return: bool.
        """
        return nx.has_path(self._dag, source, target)

    def graph(self) -> nx.DiGraph:
        """
        See the whole graph.
        :return: nx.DiGraph.
        """
        return self._dag.copy()

    def subgraph(self, bid: TypeAlias.BlockID) -> nx.DiGraph | None:
        """
        See the subgraph from the specified block.
        :param bid: BlockID.
        :return:
        """
        if bid not in self._dag:
            if self._logger is not None:
                self._logger.warning("%s: Block " + str(bid) + " does not exist.", caller_info())
            return None
        views = set()
        queue = [bid]
        while len(queue) > 0:
            q = queue.pop(0)
            views.add(q)
            queue.extend(self.successors(q))
        return self._dag.subgraph(views)
