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
from dataclasses import dataclass
from typing import Set, Tuple
from enum import Enum

from transaction import Transaction


class BlockType(Enum):
    """
    Define different types of blocks.
    """
    ORPHAN = 0  # orphan block
    GENESIS = 1  # genesis block
    MINED = 2  # mined block


@dataclass
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

    # Basic parameters controlled by simulation module.
    bid: BlockID = 0  # The unique ID of the block.
    type: BlockType = BlockType.ORPHAN  # The type of the block, see BlockType.
    miner: MinerName = None  # The name of the miner who mined the block.

    # Crucial parameters controlled by nodes module.
    pref: BlockID = None  # The block reference from the pivot chain.
    crefs: Set[BlockID] = frozenset()  # The blocks reference in the blockDAG.
    height: BlockHeight = 0  # The height of the block in the blockDAG.

    # Advanced parameters controlled by interaction module.
    size: BlockSize = 0  # The size of the block to simulate network latency.
    txs: Tuple[Transaction] = tuple()  # The special transaction marks in the block.
    data: Hashable = None  # Optional, additional data included in the block.

    def get_parents(self):
        """
        Get the parents of the block.
        The first item is the pivot reference if the blockDAG type is convergence.
        :return: the bids of the block's parent blocks.
        """
        if self.pref is None:
            return list(self.crefs)
        else:
            return [self.pref] + list(self.crefs)

    def __hash__(self) -> int:
        return self.bid

    def __str__(self):
        return "{Block: " + str(self.bid) + \
            ", Type: " + str(self.type.name) + \
            ", Miner: " + str(self.miner) + \
            ", Parents: " + str(self.get_parents()) + \
            ", Height: " + str(self.height) + "}"
