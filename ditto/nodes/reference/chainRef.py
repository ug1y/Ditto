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
from typing import Set

from ditto.blockdag import TypeAlias, BlockDAG, DAGType

from .referIface import ReferIface


def _min_hash_value(bids: Set[TypeAlias.BlockID]) -> TypeAlias.BlockID:
    return min(bids)


class ChainRef(ReferIface):
    """
    For convergence blockDAG to simulate the Bitcoin blockchain.
    """
    def __init__(self, blockdag: BlockDAG):
        super().__init__(blockdag)
        if self.blockdag.graph_type != DAGType.CONVERGENCE:
            raise ValueError("The chain reference strategy is only for convergence blockDAG.")

    def get_virtual_pivot_ref(self) -> TypeAlias.BlockID | None:
        return self._max_hash_power(self.blockdag.leaves_blocks)

    def get_virtual_common_refs(self) -> Set[TypeAlias.BlockID]:
        return set()

    def get_virtual_new_height(self) -> TypeAlias.BlockHeight:
        vp = self.get_virtual_pivot_ref()
        return self.blockdag[vp].height + 1

    def _max_hash_power(self, bids: Set[TypeAlias.BlockID]) -> TypeAlias.BlockID:
        max_height = len(self.blockdag.column_blocks)
        sel_bids = set()
        for bid in bids:
            if self.blockdag[bid].height == max_height:
                sel_bids.add(bid)
        return min(sel_bids)
