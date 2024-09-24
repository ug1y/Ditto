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
from ditto.nodes.reference import ChainRef, SelfishHolder


class MaliciousChainRef(ChainRef, SelfishHolder):
    """
    The attacker holds the malicious chain reference.
    """

    def __init__(self, miner_name: TypeAlias.MinerName, genesis_block: Block, blockdag: BlockDAG,
                 blocks_queue: Deque[Block]):
        ChainRef.__init__(self, miner_name, genesis_block, blockdag)
        SelfishHolder.__init__(self, blocks_queue)

    def get_virtual_pivot_ref(self, is_malicious: bool = False) -> TypeAlias.BlockID | None:
        if not is_malicious:
            return ChainRef.get_virtual_pivot_ref(self)
        else:
            return hash(self.blocks_queue[-1])

    def get_virtual_new_height(self, is_malicious: bool = False) -> TypeAlias.BlockHeight:
        if not is_malicious:
            return ChainRef.get_virtual_new_height(self)
        else:
            return self.blockdag[self.get_virtual_pivot_ref(is_malicious=True)].height + 1
