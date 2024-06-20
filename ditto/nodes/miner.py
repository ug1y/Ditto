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
import logging
import networkx as nx

from ..network import Network
from ..blockdag import BlockDAG, Block, BlockType


class Miner:
    """
    An implementation of an honest miner, connecting peers and generating blocks.
    """

    def __init__(self, name: Block.MinerName, blockdag: BlockDAG, max_peer_num: float):
        self._name = name  # The unique name of the miner, used to identify it.
        self._blockdag = blockdag  # The local view of blockDAG hold by the miner.
        self._max_peer_num = max_peer_num  # The maximum number of peers the miner connects.

        self._genesis_block = 0  # The genesis block the miner followed by.
        self._network = None  # Network object handler, used to connect peers and broadcast blocks.

        self._mined_blocks = set()  # Record the set of blocks mined by the miner.
        self._block_queue = nx.DiGraph()  # A graph for the received blocks that lack parents.

        logging.basicConfig(level=logging.DEBUG,
                            format='[%(asctime)s] %(levelname)s - [Module] %(name)s - '
                                   '[Location] %(filename)s:%(lineno)d - [%(funcName)s] %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        self._logger = logging.getLogger(__name__)  # Logger for this class.

    def __contains__(self, bid: Block.BlockID) -> bool:
        return bid in self._blockdag

    def __str__(self):
        return "Miner " + str(self._name) + \
            ", holding " + str(self._blockdag) + \
            ", connecting to " + str(len(self.get_neighbors())) + " neighbors."

    def __repr__(self):
        return "Miner(name=" + repr(self._name) + \
            ", blockdag=" + repr(self._blockdag) + \
            ", max_peer_num=" + repr(self._max_peer_num) + ")"

    def set_genesis_block(self, block: Block):
        """
        Set the genesis block for the miner.
        :param block: Block
        """
        if self._genesis_block == 0 \
                and block.type == BlockType.GENESIS \
                and self._blockdag.add_block(block):
            self._genesis_block = hash(block)

    def set_network(self, network: Network):
        """
        Set the global network handler.
        :param network:
        """
        self._network = network

    def get_name(self) -> Block.MinerName:
        """
        Get the unique miner name.
        :return: MinerName
        """
        return self._name

    def get_genesis_block(self) -> Block.BlockID:
        """
        Get the genesis block id for the miner.
        :return: BlockID
        """
        return self._genesis_block

    def get_mined_blocks(self) -> set[Block.BlockID]:
        """
        Get the set of blocks mined by the miner.
        :return: set[BlockID]
        """
        return self._mined_blocks

    def get_neighbors(self) -> set[Block.MinerName]:
        """
        Get the connected neighbors.
        :return: set[MinerName]
        """
        return set()  # TODO: 有待网络模块实现

    def send_block(self, receiver: Block.MinerName, bid: Block.BlockID):
        """
        Send an existing block to other miner.
        :param receiver: MinerName
        :param bid: BlockID
        """
        if bid in self._blockdag:
            print("Send block " + str(self._blockdag[bid]) + " to " + str(receiver))
        else:
            self._logger.warning("Miner " + str(self._name) + " does not have block " + str(bid))

    def mine_block(self) -> Block | None:
        """
        Mine a new block to extend dag.
        :return: Block
        """
        # TODO: 有待完善
        block = Block(bid=self._network.get_next_block_id(),
                      type=BlockType.MINED,
                      miner=self._name,
                      pref=None,
                      crefs=self._blockdag.get_leaves_blocks().copy(),
                      height=max(self._blockdag[lid].height for lid in self._blockdag.get_leaves_blocks()) + 1)
        return block

    def add_block(self, block: Block) -> bool:
        """
        Add a block from network to sync dag.
        :param block: Block
        :return: bool
        """
        # TODO: 有待完善
        if hash(block) in self._blockdag:
            return True

        return self._blockdag.add_block(block)

    def discover_peer(self):
        """
        Connect random peer miners till to the max peer number.
        """
        # TODO: 有待完善
        pass

    def connect_peer(self, peer_name: Block.MinerName, delay: float) -> bool:
        """
        Set the connection with the specified peer miner symmetrically.
        :param peer_name: MinerName
        :param delay: float
        :return: bool
        """
        # TODO: 有待完善
        pass

    def remove_peer(self, peer_name: Block.MinerName) -> bool:
        """
        Cut off the connection with the specified peer miner.
        :param peer_name: MinerName
        :return: bool
        """
        # TODO: 有待完善
        pass
