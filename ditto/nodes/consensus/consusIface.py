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

from ditto.network import NetContainer
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

    def __init__(self, network: NetContainer, blockdag: BlockDAG):
        """
        Rely on the blockdag object with only read operation.
        """
        self.network = network
        self.blockdag = blockdag
        self.decided_set = set()
        self.ordered_list = list()

    @abstractmethod
    def execute_consensus(self, bid: TypeAlias.BlockID):
        """
        Triggered by a block, the consensus instance should be implemented this method.

        Update the variables of `decided_set` and `ordered_list`.

        :param bid: TypeAlias.BlockID
        """
        pass

    def block_status(self, bid: TypeAlias.BlockID) -> StatusType:
        """
        Get the block status including INVALID, UNCLEAR, EXCLUDE, and DECIDED.

        :param bid: TypeAlias.BlockID
        :return: StatusType
        """
        if bid not in self.blockdag:
            return StatusType.INVALID
        elif bid not in self.ordered_list:
            return StatusType.UNCLEAR
        elif bid in self.decided_set:
            return StatusType.DECIDED
        else:
            return StatusType.EXCLUDE

    def get_processed_blocks(self, status: StatusType = None) -> Set[TypeAlias.BlockID]:
        """
        Get the processed blocks that is already on consensus.

        If status is None, return all the processed blocks. Supported status: EXCLUDE, DECIDED.

        :param status: StatusType
        :return: Set[TypeAlias.BlockID]
        """
        if status is None:
            return set(self.ordered_list)

        if status == StatusType.DECIDED:
            return set(self.decided_set)
        elif status == StatusType.EXCLUDE:
            return set(self.ordered_list) - set(self.decided_set)

        return set()

    def sort_finished_blocks(self, status: StatusType = None) -> List[TypeAlias.BlockID]:
        """
        Sort the finished blocks that is already on consensus.

        If status is None, return all the sorted blocks. Supported status: EXCLUDE, DECIDED.

        :param status: StatusType
        :return: List[TypeAlias.BlockID]
        """
        if status is None:
            return list(self.ordered_list)

        if status == StatusType.DECIDED:
            return [n for n in self.ordered_list if n in self.decided_set]

        elif status == StatusType.EXCLUDE:
            return [n for n in self.ordered_list if n not in self.decided_set]

        return list()
