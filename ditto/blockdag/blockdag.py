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
from enum import Enum
from typing import Iterator
import networkx as nx

from .block import Block, BlockType


class DAGType(Enum):
    """
    Define different types of blockDAG.
    """
    DIVERGENCE = 0  # divergence blockDAG
    PARALLEL = 1  # parallel blockDAG
    CONVERGENCE = 2  # convergence blockDAG


class EdgeType(Enum):
    """
    Define different types of edges in the blockDAG.
    """
    PIVOT = 0  # pivot edge by pivot reference.
    COMMON = 1  # common edge by common reference.


class BlockDAG(Collection):
    """
    An implementation of a generic BlockDAG, organizing blocks in a collection.

    Support to build the type of divergence, parallel, and convergence DAG.
    """

    # Dictionary key for the block's data.
    BLOCK_DATA_KEY = "block_data"
    # Dictionary key for the edge's type.
    EDGE_TYPE_KEY = "edge_type"

    # Type aliases, no practical use.
    BlockID = int

    def __init__(self, gtype: DAGType = DAGType.DIVERGENCE):
        self._G = nx.DiGraph()  # A networkx directed graph object.
        self._gtype = gtype  # The type of the blockDAG.
        self._leaves = set()  # Set of all the leaves in the graph.
        self._column = list(set())  # List of the set of blocks in the specified height.

        logging.basicConfig(level=logging.DEBUG,
                            format='[%(asctime)s] %(levelname)s - [Module] %(name)s - '
                                   '[Location] %(filename)s:%(lineno)d - [%(funcName)s] %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        self._logger = logging.getLogger(__name__)  # Logger for this class.

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

        # Check the object type.
        if type(block) is not Block:
            self._logger.warning("Input is not an instance of Block.")
            return False

        # Check if the block already exists.
        if self._G.has_node(block.bid):
            self._logger.warning("Block " + str(block.bid) + " already exists.")
            return False

        # Skip the orphan block.
        if block.type == BlockType.ORPHAN:
            self._logger.warning("Orphan block cannot be added.")
            return False

        # Handle the genesis block.
        if block.type == BlockType.GENESIS:
            if block.miner is not None or block.pref is not None or len(block.crefs) != 0:
                self._logger.warning("Genesis block must be empty.")
                return False
            if block.height != 1:
                self._logger.warning("Genesis block must be at height 1.")
                return False
            self._G.add_node(block.bid)
            self._G.nodes[block.bid][self.BLOCK_DATA_KEY] = block
            self._leaves.add(block.bid)
            if len(self._column) == 0:
                self._column.append(set())
            self._column[0].add(block.bid)
            return True

        # Handle the mined block.
        if block.type == BlockType.MINED:
            if block.miner is None:
                self._logger.warning("Mined block must have a miner.")
                return False
            if self._gtype == DAGType.DIVERGENCE:
                # Check the key data fields of the block.
                if block.pref is not None:
                    self._logger.warning("The block in divergence graph has no pivot parent.")
                    return False
                if len(block.crefs) == 0:
                    self._logger.warning("The block in divergence graph must have at least one reference.")
                    return False
                max_h = 0
                for cref in block.crefs:
                    if cref not in self._G:
                        self._logger.warning("The referenced block " + str(cref) + " does not exist.")
                        return False
                    max_h = max(self._G.nodes[cref][self.BLOCK_DATA_KEY].height, max_h)
                if block.height != max_h + 1:
                    self._logger.warning("Incorrect height of the mined block.")
                    return False
                # Add the block into the graph.
                self._G.add_node(block.bid)
                self._G.nodes[block.bid][self.BLOCK_DATA_KEY] = block
                for cref in block.crefs:
                    self._G.add_edge(block.bid, cref)
                    self._G.edges[block.bid, cref][self.EDGE_TYPE_KEY] = EdgeType.COMMON
                    if cref in self._leaves:
                        self._leaves.remove(cref)
                self._leaves.add(block.bid)
                if len(self._column) < block.height:
                    self._column.append(set())
                self._column[block.height - 1].add(block.bid)
                return True
            else:
                pass  # TODO 添加挖掘的新区块（平行型图和收敛型图）。
            return True
        return False
