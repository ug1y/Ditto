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

import numpy as np

from ditto.simulation import NetSimulation
from ditto.nodes import Miner, ConsusIface
from ditto.blockdag import TypeAlias, Block, BlockDAG, DAGType, BlockType

from .netContainer import NetContainer


class NetOperator(NetContainer):
    """
    The actual network operator to deploy miners.

    Set a simulator to simulate network delay.
    """

    # Dictionary key for the hash rate.
    HASH_RATE_KEY = "hash_rate"
    # Dictionary key for the hash rate.
    MINER_DATA_KEY = "miner_data"

    def __init__(self, total_blockdag: BlockDAG,
                 propagation_delay_parameter: float = 30.0,
                 block_creation_rate: float = 60.0):
        super().__init__(propagation_delay_parameter)

        self._block_creation_rate = block_creation_rate  # The block creation rate of the network.
        self._total_blockdag = total_blockdag  # The total blockDAG of the network.
        self._simulator: NetSimulation = None  # The simulator to simulate network delay.

        self._consus_handler: ConsusIface = None

    def __getitem__(self, miner: TypeAlias.MinerName) -> Miner:
        return self.network_graph.nodes[miner][NetOperator.MINER_DATA_KEY]

    def __repr__(self):
        return "NetOperator(inc_block_id=" + repr(self._inc_block_id) + \
            ", network_graph=" + repr(self.network_graph) + \
            ", total_blockdag= " + repr(self._total_blockdag) + ")"

    @property
    def block_creation_rate(self) -> float:
        """
        Get the block creation rate of the network.
        :return: float
        """
        return self._block_creation_rate

    @property
    def total_blockdag(self) -> BlockDAG:
        """
        Get the total blockDAG of the network.
        :return: BlockDAG
        """
        return self._total_blockdag

    @property
    def consus_handler(self) -> ConsusIface:
        """
        Get the consensus handler.
        :return: ConsusIface
        """
        return self._consus_handler

    def add_miner(self, miner: Miner, hash_rate: float = 10.0):
        """
        Add a miner into the network.
        :param miner: Miner
        :param hash_rate: float
        :return: bool
        """
        if miner.blockdag.graph_type != self.get_blockdag_type():
            if self._logger is not None:
                self._logger.warning("%s: Add miner %s failed, blockDAG type mismatch.",
                                     self.FOR_LOG_NAME, str(miner.name))
            return

        miner_name = miner.name
        self.network_graph.add_node(miner_name)
        self.network_graph.nodes[miner_name][NetOperator.MINER_DATA_KEY] = miner
        self.network_graph.nodes[miner_name][NetOperator.HASH_RATE_KEY] = hash_rate
        miner.set_network(self)  # The miner must set network handler before mining new blocks.
        if self._logger is not None:
            self._logger.info("%s: Add miner %s with hash rate " + str(hash_rate),
                              self.FOR_LOG_NAME, str(miner_name))

    def del_miner(self, miner_name: TypeAlias.MinerName):
        """
        Delete the miner from the network.
        :param miner_name: TypeAlias.MinerName
        :return: bool
        """
        self.network_graph.remove_node(miner_name)

    def send_block(self, source_miner: TypeAlias.MinerName, target_miner: TypeAlias.MinerName, block: Block):
        """
        Send the given block to the given miner.
        :param source_miner: TypeAlias.MinerName
        :param target_miner: TypeAlias.MinerName
        :param block: Block
        """
        if source_miner not in self.network_graph or target_miner not in self.network_graph:
            return

        sender = self[source_miner]
        receiver = self[target_miner]
        if hash(block) in sender:
            if self._logger is not None:
                self._logger.info("%s: Sending block " + str(hash(block)) + " from %s to %s.",
                                  self.FOR_LOG_NAME, str(source_miner), str(target_miner))
            # Use the simulator to simulate network delay.
            delay = self.get_delay(source_miner, target_miner)
            if self._simulator is not None and delay > 0:
                self._simulator.send_block_with_delay(source_miner, target_miner, block, delay)
            else:
                receiver.add_block(block)
                receiver.sync_block()

    def broadcast_block(self, source_miner: TypeAlias.MinerName, block: Block):
        """
        Broadcast the given block from the miner to its peers.
        :param source_miner: TypeAlias.MinerName
        :param block: Block
        """
        if hash(block) not in self._total_blockdag:
            self._total_blockdag.add_block(block)  # Every new mined block will be added to the total blockDAG.
            if self._consus_handler is not None:
                self._consus_handler.execute_consensus()  # Execute the consensus algorithm.

        if self._logger is not None:
            self._logger.info("%s: Miner %s broadcasts block " + str(hash(block)),
                              self.FOR_LOG_NAME, str(source_miner))
        peers = self.get_neighbors(source_miner)
        for peer_name in peers:
            self.send_block(source_miner, peer_name, block)

    def fetch_block(self, target_miner: TypeAlias.MinerName, bid: TypeAlias.BlockID):
        """
        Retrieves the block with the given ID from the network for the given miner.
        :param target_miner: TypeAlias.MinerName
        :param bid: TypeAlias.BlockID
        """
        if self._logger is not None:
            self._logger.info("%s: Miner %s fetches block " + str(bid),
                              self.FOR_LOG_NAME, str(target_miner))
        for peer_name in self.get_neighbors(target_miner):
            self.send_block(peer_name, target_miner, self._total_blockdag[bid])

    def get_random_miner(self, by_hash_rate: bool = False) -> Miner:
        """
        # Get a random miner from the network subject to the hash rate distribution or not.
        :param by_hash_rate: bool
        :return: TypeAlias.MinerName
        """
        miners = []
        hash_rates = []
        total_hash_rate = 0
        for miner_name in self:
            miners.append(miner_name)
            miner_hash_rate = self.network_graph.nodes[miner_name][NetOperator.HASH_RATE_KEY]
            hash_rates.append(miner_hash_rate)
            total_hash_rate += miner_hash_rate

        if by_hash_rate:
            miner_name = np.random.choice(miners, p=np.array(hash_rates) / total_hash_rate)
        else:
            miner_name = np.random.choice(miners)
        return self[miner_name]

    def get_blockdag_type(self) -> DAGType:
        return self._total_blockdag.graph_type

    def set_simulator(self, simulator):
        self._simulator = simulator

    def init_network(self, genesis_block_num: int = 1) -> Set[Block]:
        """
        Initialize the network, and return the genesis block.
        :param genesis_block_num: int
        :return: Set[Block]
        """
        if self.get_blockdag_type() in {DAGType.DIVERGENCE, DAGType.CONVERGENCE} and genesis_block_num != 1:
            if self._logger is not None:
                self._logger.warning("%s: " + str(self.get_blockdag_type().name) +
                                     "blockDAG is allowed to have only one genesis block.", self.FOR_LOG_NAME)
            return set()

        genesis_blocks = set()
        for i in range(genesis_block_num):
            block = Block(bid=self.get_next_block_id(), btype=BlockType.GENESIS, height=1)
            genesis_blocks.add(block)
            self._total_blockdag.add_block(block)
        return genesis_blocks

    def set_consus_handler(self, consus_class: type[ConsusIface]):
        """
        Set the consensus handler.
        :param consus_class: type[ConsusIface]
        """
        if consus_class is not None:
            self._consus_handler = consus_class(self._total_blockdag)
