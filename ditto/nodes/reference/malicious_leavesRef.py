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
from typing import Deque

from ditto.blockdag import TypeAlias, Block, BlockDAG
from ditto.nodes.reference import LeavesRef, SelfishHolder


class MaliciousLeavesRef(LeavesRef, SelfishHolder):

    def __init__(self, miner_name: TypeAlias.MinerName, genesis_block: Block, blockdag: BlockDAG,
                 blocks_queue: Deque[Block]):
        LeavesRef.__init__(self, miner_name, genesis_block, blockdag)
        SelfishHolder.__init__(self, blocks_queue)

    def get_virtual_common_refs(self, is_malicious: bool = False) -> set[TypeAlias.BlockID]:
        if not is_malicious:
            return LeavesRef.get_virtual_common_refs(self)
        else:
            return {hash(self.blocks_queue[-1])} & LeavesRef.get_virtual_common_refs(self)

    def get_virtual_new_height(self, is_malicious: bool = False) -> TypeAlias.BlockHeight:
        if not is_malicious:
            return LeavesRef.get_virtual_new_height(self)
        else:
            leaves = self.get_virtual_common_refs(is_malicious=True)
            return max(self.blockdag[lid].height for lid in leaves) + 1
