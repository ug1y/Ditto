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
from abc import ABC, abstractmethod
from enum import Enum
from typing import Set, List

from ditto.blockdag import BlockDAG, TypeAlias


class StatusType(Enum):
    # Define the status of a block.
    INVALID = 0  # invalid block means the block is not in the blockdag.
    UNCLEAR = 1  # unclear block means the block is not processed yet.
    EXCLUDE = 2  # exclude block means the block is excluded by consensus.
    DECIDED = 3  # decided block means the block is decided by consensus.


class ConsusIface(ABC):
    """
    Consensus determination interface.
    """

    def __init__(self, blockdag: BlockDAG):
        """
        Rely on the blockdag object with only read operation.
        """
        self.blockdag = blockdag

    @abstractmethod
    def get_block_status(self, bid) -> StatusType:
        """
        Get the block status including invalid, unclear, exclude, and decided.
        :param bid:
        :return: StatusType
        """
        pass

    @abstractmethod
    def get_decided_blocks(self) -> Set[TypeAlias.BlockID]:
        """
        Get the decided blocks that is already on consensus.
        :return: Set[TypeAlias.BlockID]
        """
        pass

    @abstractmethod
    def sort_finished_blocks(self, filter_decided: bool = True) -> List[TypeAlias.BlockID]:
        """
        Sort the finished blocks filtering decided status or containing excluded status.
        :return: List[TypeAlias.BlockID]
        """
        pass
