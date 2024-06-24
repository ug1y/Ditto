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
from collections import deque

import networkx as nx

from ditto.network import Network
from ditto.blockdag import BlockDAG, Block, BlockType
from .referIface import ReferIface
from .consusIface import ConsusIface


class Miner:
    """
    An implementation of an honest miner, connecting peers and generating blocks.
    """

    # Dictionary key for the block's data.
    _QUEUE_BLOCK_DATA_KEY = "queue_block_data"

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

        self._refer_handler = None
        self._consus_handler = None

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
                and block.btype == BlockType.GENESIS \
                and self._blockdag.add_block(block):
            self._genesis_block = hash(block)

    def set_network(self, network: Network):
        """
        Set the global network handler.
        :param network: Network
        """
        self._network = network

    def set_refer_handler(self, refer_class: type[ReferIface]):
        """
        Set the reference handler.
        :param refer_class
        """
        self._refer_handler = refer_class(self._blockdag)

    def set_consus_handler(self, consus_class: type[ConsusIface]):
        """
        Set the consensus handler.
        :param consus_class
        """
        self._consus_handler = consus_class(self._blockdag)

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
        if self._network is None:
            self._logger.warning("Miner " + str(self._name) + " does not have network handler.")
            return set()

        return set()  # TODO: 有待网络模块实现

    def mine_block(self) -> Block | None:
        """
        Mine a new block to extend dag.
        :return: Block
        """
        if self._network is None:
            self._logger.warning("Miner " + str(self._name) + " does not have network handler.")
            return None
        if self._genesis_block == 0:
            self._logger.warning("Miner " + str(self._name) + " should set a genesis block before mining.")
            return None
        if self._refer_handler is None:
            self._logger.warning("Miner " + str(self._name) + " does not have reference handler.")
            return None

        # Use the reference handler to select the pref and crefs.
        block = Block(bid=self._network.get_next_block_id(),
                      btype=BlockType.MINED,
                      miner=self._name,
                      pref=self._refer_handler.get_virtual_pivot_ref(),
                      crefs=self._refer_handler.get_virtual_common_refs(),
                      height=self._refer_handler.get_virtual_new_height())

        # TODO: 从交易池中拿交易来构建新区块

        if not self.add_block(block):  # The block will be broadcast by _basic_block_add.
            return None

        self._mined_blocks.add(hash(block))
        return block

    def add_block(self, block: Block) -> bool:
        """
        Add a block from network to sync dag.
        :param block: Block
        :return: bool
        """
        if hash(block) in self._blockdag:
            return True

        if self._add_to_block_queue(block):
            return False

        if hash(block) in self._block_queue:
            return self._cascade_block_add(block)

        return self._basic_block_add(block)

    def _add_to_block_queue(self, block: Block) -> bool:
        """
        Add the given block to the block queue if its parents are missing.
        :param block: Block
        :return: bool
        """
        missing_parents = False
        for parent_bid in block.get_parents():
            if parent_bid not in self._blockdag:
                missing_parents = True
                if parent_bid not in self._block_queue:
                    # TODO 向网络请求缺失的父块
                    self._block_queue.add_node(parent_bid)
                    self._block_queue.nodes[parent_bid][Miner._QUEUE_BLOCK_DATA_KEY] = None
                self._block_queue.add_edge(block.bid, parent_bid)

        if missing_parents:
            self._block_queue.nodes[hash(block)][Miner._QUEUE_BLOCK_DATA_KEY] = block
            return True

        return False

    def _basic_block_add(self, block: Block) -> bool:
        """
        Add the given block to the dag without checking its parents.
        :param block: Block
        :return: bool
        """
        if self._blockdag.add_block(block):
            # TODO: 广播新添加的区块给邻居
            return True
        return False

    def _cascade_block_add(self, block: Block) -> bool:
        """
        Add the supplementary block from the block queue to the dag in a cascade way.
        :param block: Block
        :return: bool
        """
        self._block_queue.nodes[hash(block)][Miner._QUEUE_BLOCK_DATA_KEY] = block
        add_queue = deque([hash(block)])
        while add_queue:
            cur_block_bid = add_queue.popleft()
            if cur_block_bid not in self._block_queue:
                continue
            cur_block = self._block_queue.nodes[cur_block_bid][Miner._QUEUE_BLOCK_DATA_KEY]
            if cur_block is not None:
                parents = cur_block.get_parents()
                for parent_bid in parents:
                    if parent_bid not in self._blockdag:
                        continue
                add_queue.extend(self._block_queue.predecessors(hash(cur_block)))
                self._block_queue.remove_node(hash(cur_block))
                if not self._basic_block_add(cur_block):
                    return False
        return True

    def discover_peer(self):
        """
        Connect random peer miners till to the max peer number.
        """
        # TODO: 有待完善，直接调用网络模块
        pass

    def connect_peer(self, peer_name: Block.MinerName, delay: float) -> bool:
        """
        Set the connection with the specified peer miner symmetrically.
        :param peer_name: MinerName
        :param delay: float
        :return: bool
        """
        # TODO: 有待完善，直接调用网络模块
        pass

    def remove_peer(self, peer_name: Block.MinerName) -> bool:
        """
        Cut off the connection with the specified peer miner.
        :param peer_name: MinerName
        :return: bool
        """
        # TODO: 有待完善，直接调用网络模块
        pass
