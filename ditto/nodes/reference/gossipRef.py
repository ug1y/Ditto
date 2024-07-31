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

from .referIface import ReferIface


class GossipRef(ReferIface):

    def __init__(self, miner_name: TypeAlias.MinerName, genesis_block: Block, blockdag: BlockDAG):
        super().__init__(miner_name, genesis_block, blockdag)
        if self.blockdag.graph_type != DAGType.PARALLEL:
            raise ValueError("The gossip reference strategy is only for parallel blockDAG.")

    def can_referred(self) -> bool:
        row_blocks = self.blockdag.get_mined_blocks(self.miner_name)
        row_blocks.add(hash(self.genesis_block))
        last_row_block_id = max(row_blocks)
        if len(self.blockdag.leaves_blocks - {last_row_block_id}) > 0:
            return True
        else:
            return False

    def get_virtual_pivot_ref(self) -> TypeAlias.BlockID | None:
        row_blocks = self.blockdag.get_mined_blocks(self.miner_name)
        row_blocks.add(hash(self.genesis_block))
        return max(row_blocks)

    def get_virtual_common_refs(self) -> Set[TypeAlias.BlockID]:
        row_blocks = self.blockdag.get_mined_blocks(self.miner_name)
        row_blocks.add(hash(self.genesis_block))
        last_row_block_id = max(row_blocks)

        peer_block_ids = self.blockdag.leaves_blocks - {last_row_block_id}
        if len(peer_block_ids) > 0:
            return {max(peer_block_ids)}
        else:
            return set()

    def get_virtual_new_height(self) -> TypeAlias.BlockHeight:
        row_block = self.blockdag[self.get_virtual_pivot_ref()]
        peer_block = self.blockdag[list(self.get_virtual_common_refs())[0]]

        return max(row_block.height, peer_block.height) + 1
