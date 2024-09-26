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

from ditto.blockdag import TypeAlias, Block, BlockDAG, DAGType

from ditto.nodes.reference import ReferIface


class LeavesRef(ReferIface):
    """
    Reference all leaves of the blockDAG.

    Only for divergence blockDAG.
    """

    def __init__(self, miner_name: TypeAlias.MinerName, genesis_block: Block, blockdag: BlockDAG):
        super().__init__(miner_name, genesis_block, blockdag)
        if self.blockdag.graph_type != DAGType.DIVERGENCE:
            raise ValueError("The leaves reference strategy is only for divergence blockDAG.")

    def can_referred(self) -> bool:
        return True

    def get_virtual_pivot_ref(self, *args, **kwargs) -> TypeAlias.BlockID | None:
        return None

    def get_virtual_common_refs(self, *args, **kwargs) -> Set[TypeAlias.BlockID]:
        return self.blockdag.leaves_blocks.copy()

    def get_virtual_new_height(self, *args, **kwargs) -> TypeAlias.BlockHeight:
        leaves = self.get_virtual_common_refs()
        return max(self.blockdag[lid].height for lid in leaves) + 1
