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
from typing import Set

import networkx as nx

from ditto.network import NetContainer
from ditto.blockdag import BlockDAG, Block, BlockType, TypeAlias

from .reference import ReferIface
from .consensus import ConsusIface


class Miner:
    """
    An implementation of an honest miner, connecting peers and generating blocks.
    """

    # Dictionary key for the block's data.
    QUEUE_BLOCK_DATA_KEY = "queue_block_data"

    def __init__(self, name: TypeAlias.MinerName, blockdag: BlockDAG, max_peer_num: int = 0):
        self._name = name  # The unique name of the miner, used to identify it.
        self._blockdag = blockdag  # The local view of blockDAG hold by the miner.
        self._max_peer_num = max_peer_num  # The maximum number of peers the miner connects.

        self._genesis_block: Block = None  # The genesis block the miner followed by.
        self._latest_block: Block = None  # The latest block the miner received.
        self._network: NetContainer = None  # Network object handler, used to connect peers and broadcast blocks.

        self._mined_blocks = set()  # Record the set of blocks mined by the miner.
        self._block_queue = nx.DiGraph()  # A graph for the received blocks that lack parents.

        self._logger: logging.Logger = None  # Logger for this class.

        self._refer_handler: ReferIface = None
        self._consus_handler: ConsusIface = None

    def set_logger(self, logger: logging.Logger):
        self._logger = logger

    def __contains__(self, bid: TypeAlias.BlockID) -> bool:
        return bid in self._blockdag

    def __str__(self):
        return "Miner " + str(self._name) + \
            ", holding " + str(self._blockdag) + \
            ", connecting to " + str(len(self.get_neighbors())) + " neighbors."

    def __repr__(self):
        return "Miner(name=" + repr(self._name) + \
            ", blockdag=" + repr(self._blockdag) + \
            ", max_peer_num=" + repr(self.max_peer_num) + ")"

    def set_genesis_block(self, block: Block):
        """
        Set the genesis block for the miner.
        :param block: Block
        """
        if self._genesis_block is None \
                and block.btype == BlockType.GENESIS \
                and self._blockdag.add_block(block):
            self._genesis_block = block
            self._latest_block = block

    def set_network(self, network: NetContainer):
        """
        Set the global network handler.
        :param network: NetContainer
        """
        self._network = network

    def set_refer_handler(self, refer_class: type[ReferIface]):
        """
        Set the reference handler.
        :param refer_class: type[ReferIface]
        """
        self._refer_handler = refer_class(self._name, self._genesis_block, self._blockdag)

    def set_consus_handler(self, consus_class: type[ConsusIface]):
        """
        Set the consensus handler.
        :param consus_class: type[ConsusIface]
        """
        if consus_class is not None:
            self._consus_handler = consus_class(self._network, self._blockdag)

    def pre_launch(self, genesis_block: Block,
                   refer_class: type[ReferIface],
                   network: NetContainer = None,
                   consus_class: type[ConsusIface] = None):
        """
        Prepare the miner for launch.
        :param genesis_block: Block
        :param refer_class: type[ReferIface]
        :param network: NetContainer
        :param consus_class: type[ConsusIface]
        """
        self.set_genesis_block(genesis_block)
        self.set_refer_handler(refer_class)
        self.set_network(network)  # The miner must set network handler before mining new blocks.
        self.set_consus_handler(consus_class)

    @property
    def name(self) -> TypeAlias.MinerName:
        """
        Get the unique miner name.
        :return: MinerName
        """
        return self._name

    @property
    def blockdag(self) -> BlockDAG:
        """
        Get the local view of blockDAG hold by the miner.
        :return: BlockDAG
        """
        return self._blockdag

    @property
    def max_peer_num(self) -> int:
        """
        Get the maximum number of peers the miner connects.
        :return: int
        """
        return self._max_peer_num

    @max_peer_num.setter
    def max_peer_num(self, max_peer_num: int):
        """
        Set the maximum number of peers the miner connects.
        :param max_peer_num: int
        """
        self._max_peer_num = max_peer_num

    @property
    def genesis_block(self) -> Block:
        """
        Get the genesis block of the miner.
        :return: BlockID
        """
        return self._genesis_block

    @property
    def latest_block(self) -> Block:
        """
        Get the latest block of the miner.
        :return: BlockID
        """
        return self._latest_block

    @property
    def network(self) -> NetContainer:
        """
        Get the network handler.
        :return: NetContainer
        """
        return self._network

    @property
    def mined_blocks(self) -> Set[TypeAlias.BlockID]:
        """
        Get the set of blocks mined by the miner.
        :return: set[BlockID]
        """
        return self._mined_blocks

    @property
    def refer_handler(self) -> ReferIface:
        """
        Get the reference handler.
        :return: ReferIface
        """
        return self._refer_handler

    @property
    def consus_handler(self) -> ConsusIface:
        """
        Get the consensus handler.
        :return: ConsusIface
        """
        return self._consus_handler

    def get_neighbors(self) -> Set[TypeAlias.MinerName]:
        """
        Get the connected neighbors.
        :return: set[MinerName]
        """
        if self._network is None:
            if self._logger is not None:
                self._logger.warning("%s: Network handler is not set.", self._name)
            return set()

        return self._network.get_neighbors(self._name)

    def mine_block(self) -> Block | None:
        """
        Mine a new block to extend dag.
        :return: Block
        """
        if self._network is None:
            if self._logger is not None:
                self._logger.warning("%s: Network handler is not set.", self._name)
            return None
        if self._genesis_block is None:
            if self._logger is not None:
                self._logger.warning("%s: genesis block should be set before mining.", self._name)
            return None
        if self.refer_handler is None:
            if self._logger is not None:
                self._logger.warning("%s: Reference handler is not set.", self._name)
            return None

        # Check the references before generate a new block.
        if not self.refer_handler.can_referred():
            # Broadcast the latest block to try to sync network.
            self.broadcast_block(self._latest_block)
            return None

        # Use the reference handler to select the pref and crefs.
        block = Block(bid=self._network.get_next_block_id(),
                      btype=BlockType.MINED,
                      miner=self._name,
                      pref=self.refer_handler.get_virtual_pivot_ref(),
                      crefs=self.refer_handler.get_virtual_common_refs(),
                      height=self.refer_handler.get_virtual_new_height())

        # TODO: 从交易池中拿交易来构建新区块

        if self._logger is not None:
            self._logger.info("%s: Mined a new block %d.", self._name, hash(block))

        if not self.add_block(block):  # The block will be broadcast by _basic_block_add.
            return None

        self._mined_blocks.add(hash(block))
        return block

    def sync_block(self):
        """
        Sync the missing blocks in the queue and fetch them.
        """
        missing_blocks = set()
        for queue_bid in self._block_queue.nodes():
            if self._block_queue.nodes[queue_bid][Miner.QUEUE_BLOCK_DATA_KEY] is None:
                missing_blocks.add(queue_bid)

        for missing_block in missing_blocks:
            if self._block_queue.nodes[missing_block][Miner.QUEUE_BLOCK_DATA_KEY] is None:  # Avoid duplicated fetch.
                # Fetch the missing parent from network.
                # self._network.fetch_block(self._name, missing_block)
                self.fetch_block(missing_block)

    def add_block(self, block: Block) -> bool:
        """
        Add a block from network to sync dag.
        :param block: Block
        :return: bool
        """
        if self._logger is not None:
            self._logger.debug("%s: Received a new block %d and tries to add it.", self._name, hash(block))

        if not self._is_valid_block(block):
            return False

        if hash(block) in self._blockdag:
            return True

        if self._add_to_block_queue(block):
            return False

        if hash(block) in self._block_queue:
            return self._cascade_block_add(block)

        return self._basic_block_add(block)

    def _is_valid_block(self, block: Block) -> bool:
        """
        Check if the given block is valid.
        :param block: Block
        :return: bool
        """
        if block is None or block.btype == BlockType.ORPHAN or \
                block.crefs is None or block.height == 0:
            return False

        return True

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
                    self._block_queue.add_node(parent_bid)
                    self._block_queue.nodes[parent_bid][Miner.QUEUE_BLOCK_DATA_KEY] = None
                self._block_queue.add_edge(block.bid, parent_bid)

        if missing_parents:
            self._block_queue.nodes[hash(block)][Miner.QUEUE_BLOCK_DATA_KEY] = block
            return True

        return False

    def _basic_block_add(self, block: Block) -> bool:
        """
        Add the given block to the dag without checking its parents.
        :param block: Block
        :return: bool
        """
        # if self._consus_handler is None:
        #     if self._logger is not None:
        #         self._logger.warning("%s: Consensus handler is not set.", self._name)
        #     return False

        if self._blockdag.add_block(block):
            if self._logger is not None:
                self._logger.info("%s: Successfully added the block %d and broadcasts it.", self._name, hash(block))
            # record the latest block.
            self._latest_block = block
            # broadcast the block to neighbors.
            self.broadcast_block(block)
            # execute the consensus
            if self._consus_handler is not None:
                self._consus_handler.execute_consensus()
            return True
        return False

    def _cascade_block_add(self, block: Block) -> bool:
        """
        Add the supplementary block from the block queue to the dag in a cascade way.
        :param block: Block
        :return: bool
        """
        self._block_queue.nodes[hash(block)][Miner.QUEUE_BLOCK_DATA_KEY] = block
        add_queue = deque([hash(block)])
        while add_queue:
            cur_block_bid = add_queue.popleft()
            if cur_block_bid not in self._block_queue:
                continue
            cur_block = self._block_queue.nodes[cur_block_bid][Miner.QUEUE_BLOCK_DATA_KEY]
            if cur_block is not None:
                parents = cur_block.get_parents()
                for parent_bid in parents:
                    if parent_bid not in self._blockdag:
                        break
                else:  # Require that all parents are already in blockdag.
                    add_queue.extend(self._block_queue.predecessors(hash(cur_block)))
                    self._block_queue.remove_node(hash(cur_block))
                    if not self._basic_block_add(cur_block):
                        return False
        return True

    def discover_peer(self) -> int:
        """
        Connect random peer miners till to the max peer number.
        """
        count = 0
        new_peers = self._network.discover_peer(self._name, self.max_peer_num)
        for new_peer in new_peers:
            if self._network.connect_peer(self._name, new_peer, self._network.get_delay(self._name, new_peer)):
                count += 1
        return count

    def connect_peer(self, peer_name: TypeAlias.MinerName, delay: float = -1) -> bool:
        """
        Set the connection with the specified peer miner symmetrically.
        :param peer_name: TypeAlias.MinerName
        :param delay: float
        :return: bool
        """
        if self._network is None:
            if self._logger is not None:
                self._logger.warning("%s: Network handler is not set.", self._name)
            return False
        if delay < 0:
            delay = self._network.get_delay(self._name, peer_name)
        if self._logger is not None:
            self._logger.info("%s: Connects to %s with delay %.1f.", self._name, peer_name, delay)
        return self._network.connect_peer(self._name, peer_name, delay)

    def remove_peer(self, peer_name: TypeAlias.MinerName) -> bool:
        """
        Cut off the connection with the specified peer miner.
        :param peer_name: TypeAlias.MinerName
        :return: bool
        """
        if self._network is None:
            if self._logger is not None:
                self._logger.warning("%s: Network handler is not set.", self._name)
            return False
        if self._logger is not None:
            self._logger.info("%s: Disconnects with %s.", self._name, peer_name)
        return self._network.remove_peer(self._name, peer_name)

    def send_block(self, target_miner: TypeAlias.MinerName, block: Block):
        """
        Wrap the send_block method in the network handler.
        :param target_miner: TypeAlias.MinerName
        :param block: Block
        :return: bool
        """
        if self._network is None:
            if self._logger is not None:
                self._logger.warning("%s: Network handler is not set.", self._name)
            return
        self._network.send_block(self._name, target_miner, block)

    def broadcast_block(self, block: Block):
        """
        Wrap the broadcast_block method in the network handler.
        :param block: Block
        :return: bool
        """
        if self._network is None:
            if self._logger is not None:
                self._logger.warning("%s: Network handler is not set.", self._name)
            return
        self._network.broadcast_block(self._name, block)

    def fetch_block(self, bid: TypeAlias.BlockID):
        """
        Wrap the fetch_block method in the network handler.
        :param bid: TypeAlias.BlockID
        :return: bool
        """
        if self._network is None:
            if self._logger is not None:
                self._logger.warning("%s: Network handler is not set.", self._name)
            return
        self._network.fetch_block(self._name, bid)
