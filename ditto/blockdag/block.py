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
from collections.abc import Hashable
from typing import AbstractSet, Tuple
from enum import Enum


class BlockType(Enum):
    """
    Define different types of blocks.
    """
    ORPHAN = 0  # orphan block
    GENESIS = 1  # genesis block
    MINED = 2  # mined block


class Block(Hashable):
    """
    An implementation of a generic Block.

    Global ID of a block - the hash of the block.
    """

    # Type aliases, no practical use.
    BlockID = int
    MinerName = str
    BlockHeight = int
    BlockSize = float

    def __init__(self, block_id: BlockID = 0,
                 block_type: BlockType = BlockType.ORPHAN,
                 miner_name: MinerName = None,
                 pivot_reference: BlockID = None,
                 common_references: AbstractSet[BlockID] = frozenset(),
                 block_height: BlockHeight = 0,
                 block_size: BlockSize = 0,
                 transactions: Tuple[str] = tuple(),
                 block_data: Hashable = None):
        """
        Constructor, the basic method to initialize a block.
        :param block_id: the unique ID of the block.
        :param block_type: the type of the block, see BlockType.
        :param miner_name: the name of the miner who mined the block.
        :param pivot_reference: the block reference from the pivot chain.
        :param common_references: the blocks reference in the blockDAG.
        :param block_height: the height of the block in the blockDAG.
        :param block_size: the size of the block to simulate network latency.
        :param transactions: the special transaction marks in the block.
        :param block_data: optional, additional data included in the block.
        """

        # Basic parameters
        self._bid = block_id
        self._type = block_type
        self._miner = miner_name
        self._pref = pivot_reference
        self._crefs = common_references
        self._height = block_height
        # Advanced parameters
        self._size = block_size
        self._txs = transactions
        self._data = block_data

    def get_parents(self):
        """
        Get the parents of the block.
        The first item is the pivot reference if the blockDAG type is convergence.
        :return: the bids of the block's parent blocks.
        """
        if self._pref is None:
            return list(self._crefs)
        else:
            return [self._pref] + list(self._crefs)

    def __hash__(self) -> int:
        return self._bid

    def __str__(self):
        return "{Block: " + str(self._bid) + \
            ", Type: " + str(self._type.name) + \
            ", Miner: " + str(self._miner) + \
            ", Parents: " + str(self.get_parents()) + \
            ", Height: " + str(self._height) + "}"
