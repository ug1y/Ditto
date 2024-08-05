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

from ditto.network import NetContainer
from ditto.blockdag import TypeAlias, BlockDAG

from ditto.nodes.consensus import ConsusIface, StatusType


class NakamotoCons(ConsusIface):
    """
    In nakamoto consensus, blocks with depth of 6 can be safely decided.
    """

    def __init__(self, network: NetContainer, blockdag: BlockDAG):
        super().__init__(network, blockdag)
        self._blocks_marked = dict()
        self._sorted_blocks = list()
        self._height_pointer = 0
        self._safe_depth = 6

    def execute_consensus(self):
        old_height_pointer = self._height_pointer
        self._height_pointer = len(self.blockdag.column_blocks)  # Update the height pointer.

        cur_height = old_height_pointer - self._safe_depth
        tar_height = self._height_pointer - self._safe_depth
        if tar_height < 0:  # Not reach the safe depth.
            return 0

        if self._height_pointer == old_height_pointer:
            return tar_height

        potential_bid = self._max_hash_power(self.blockdag.leaves_blocks)
        pivot_chain = self.blockdag.get_pivot_chain(potential_bid)

        for h in range(max(0, cur_height), tar_height):
            col_bids = self.blockdag.column_blocks[h]
            sor_bids = sorted(col_bids)  # Sort all blocks by hash value.
            for bid in sor_bids:  # Mark the decided and excluded blocks.
                if bid in pivot_chain:
                    self._blocks_marked[bid] = StatusType.DECIDED
                else:
                    self._blocks_marked[bid] = StatusType.EXCLUDE
            self._sorted_blocks.extend(sor_bids)


    def block_status(self, bid) -> StatusType:
        if bid not in self.blockdag:
            return StatusType.INVALID
        elif bid not in self._blocks_marked:
            return StatusType.UNCLEAR
        else:
            return self._blocks_marked[bid]

    def get_processed_blocks(self, status: StatusType = None) -> Set[TypeAlias.BlockID]:
        if status is None:
            return set(self._blocks_marked.keys())

        processed_bids = set()
        for bid, bst in self._blocks_marked.items():
            if status == bst:
                processed_bids.add(bid)
        return processed_bids

    def sort_finished_blocks(self, status: StatusType = None) -> List[TypeAlias.BlockID]:
        if status is None:
            return self._sorted_blocks.copy()

        return [bid for bid in self._sorted_blocks if self._blocks_marked[bid] == status]

    def _max_hash_power(self, bids: Set[TypeAlias.BlockID]) -> TypeAlias.BlockID:
        max_height = len(self.blockdag.column_blocks)
        sel_bids = set()
        for bid in bids:
            if self.blockdag[bid].height == max_height:
                sel_bids.add(bid)
        return min(sel_bids)


if __name__ == '__main__':
    print("Nakamoto Consensus.")
