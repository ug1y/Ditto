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
from collections.abc import Collection
from enum import Enum
from typing import Iterator
import networkx as nx

from .block import Block


class DAGType(Enum):
    """
    Define different types of blockDAG.
    """
    DIVERGENCE = 0  # divergence blockDAG
    PARALLEL = 1  # parallel blockDAG
    CONVERGENCE = 2  # convergence blockDAG


class BlockDAG(Collection):
    """
    An implementation of a generic BlockDAG, organizing blocks in a collection.

    Support to build the type of divergence, parallel, and convergence DAG.
    """

    # Dictionary key for the block's data.
    BLOCK_DATA_KEY = "block_data"

    # Type aliases, no practical use.
    BlockID = int

    def __init__(self, gtype: DAGType = DAGType.DIVERGENCE):
        self._G = nx.DiGraph()  # A networkx directed graph object.
        self._gtype = gtype  # The type of the blockDAG.
        self._leaves = set()  # Set of all the leaves in the graph.
        self._column = list(set())  # List of the set of blocks in the specified height.

    def __contains__(self, bid: type(Block.BlockID)) -> bool:
        return bid in self._G

    def __getitem__(self, bid):
        return self._G[bid][self.BLOCK_DATA_KEY]

    def __iter__(self) -> Iterator[Block]:
        return iter(self._G)

    def __len__(self) -> int:
        return len(self._G)

    def __str__(self):
        return str(self._G)

    def __repr__(self):
        return "BlockDAG(G=" + repr(self._G) + \
            ", type=" + repr(self._gtype) + \
            ", leaves=" + repr(self._leaves) + \
            ", cluster=" + repr(self._column) + ")"

    def get_graph_type(self) -> DAGType:
        """
        Get the type of the blockDAG.
        :return: DIVERGENCE=0 or PARALLEL=1 or CONVERGENCE=2.
        """
        return self._gtype

    def get_virtual_parents(self) -> set[BlockID]:
        """
        Get the set of blocks located in the leaves of the graph.
        :return: set[BlockID].
        """
        return self._leaves

    def get_column_blocks(self, height: int = 0) -> set[BlockID]:
        """
        Get the set of blocks at specified height of the graph.
        :return: set[BlockID].
        """
        return self._column[height]

    def get_pivot_chain(self, bid: BlockID) -> list[BlockID]:
        """
        Get the pivot chain if the graph type is convergence or parallel.
        :return: list[BlockID].
        """
        if self._gtype == DAGType.DIVERGENCE:
            return []
        # TODO 通过枢纽引用回溯到创世区块形成一条单链返回。
        return []

    def add_block(self, block: Block) -> bool:
        """
        Add a block into the graph.
        :return: true or false.
        """
        if self._G.has_node(block.bid):
            return False
        # TODO 添加新区块，检查是否满足图结构类型要求。
        self._G.add_node(block.bid, **{self.BLOCK_DATA_KEY: block})
        return True
