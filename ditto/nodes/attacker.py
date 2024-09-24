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
from collections import deque
from typing import Deque

from ditto.nodes import Miner
from ditto.blockdag import BlockDAG, TypeAlias, Block, BlockType
from ditto.nodes.reference import ReferIface


class Attacker(Miner):

    def __init__(self, name: TypeAlias.MinerName, blockdag: BlockDAG, attack_flag: bool = False):
        super().__init__(name, blockdag)
        self._blocks_to_attack_queue: Deque[Block] = deque()  # Selfish blocks to attack.
        self._attack_flag: bool = attack_flag  # The flag to start the attack.
        self._target_block_id: TypeAlias.BlockID = 0  # The first block when starting the attack.

    def __repr__(self):
        return "Attacker(name=" + repr(self._name) + \
            ", blockdag=" + repr(self._blockdag) + \
            ", blocks_queue=" + str({hash(b) for b in self._blocks_to_attack_queue}) + ")"

    @property
    def attack_flag(self) -> bool:
        return self._attack_flag

    @attack_flag.setter
    def attack_flag(self, flag: bool):
        self._attack_flag = flag

    def _broadcast_blocks_queue(self):
        """
        Broadcast all selfish blocks in the queue.

        If the attack is success, sending them to neighbors.
        :return:
        """
        pass

    def set_refer_handler(self, refer_class: type[ReferIface]):
        """
        Set the reference handler, passing blocks_deque to the refer class.
        :param refer_class: type[ReferIface]
        """
        self._refer_handler = refer_class(self._name, self._genesis_block, self._blockdag,
                                          self._blocks_to_attack_queue)

    def broadcast_block(self, block: Block):
        """
        Rewrite the block broadcasting method.

        Do not forward the added block to neighbors.

        The attacker is a network black hole.
        :param block: Block
        """
        if self._attack_flag and block.miner == self._name:
            self.network.add_block(block)  # Add the malicious block to the network.
            self._blocks_to_attack_queue.append(block)  # Add it to the block queue.

        self._broadcast_blocks_queue()  # Try to complete the attack.

    def create_new_block(self) -> Block:
        """
        Rewrite the block creation method.

        Once attacking start, new malicious blocks will be added to the queue.
        :return: Block
        """
        if not self._attack_flag or len(self._blocks_to_attack_queue) == 0:
            return super().create_new_block()

        return Block(bid=self.network.get_next_block_id(), btype=BlockType.MINED, miner=self.name,
                     pref=self.refer_handler.get_virtual_pivot_ref(is_malicious=True),
                     crefs=self.refer_handler.get_virtual_common_refs(is_malicious=True),
                     height=self.refer_handler.get_virtual_new_height(is_malicious=True))

