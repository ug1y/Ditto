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
import numpy as np

from ditto.blockdag import TypeAlias, Block, BlockDAG, DAGType
from ditto.nodes import Miner
from .netContainer import NetContainer


class NetOperator(NetContainer):
    """
    The actual network operator to deploy miners.

    Set a simulator to simulate network delay.
    """

    # Dictionary key for the hash rate.
    _HASH_RATE_KEY = "hash_rate"
    # Dictionary key for the hash rate.
    _MINER_DATA_KEY = "miner_data"

    def __init__(self, total_blockdag: BlockDAG, delay_parameter: float = 1.0):
        super().__init__(delay_parameter)

        self._total_blockdag = total_blockdag  # The total blockDAG of the network.
        self._simulator = None  # The simulator to simulate network delay.

    def __getitem__(self, miner: TypeAlias.MinerName) -> Miner:
        return self.network_graph.nodes[miner][NetOperator._MINER_DATA_KEY]

    def add_miner(self, miner: Miner, hash_rate: float = 1.0):
        """
        Add a miner into the network.
        :param miner: Miner
        :param hash_rate: float
        :return: bool
        """
        miner_name = miner.get_name()
        self.network_graph.add_node(miner_name)
        self.network_graph.nodes[miner_name][NetOperator._MINER_DATA_KEY] = miner
        self.network_graph.nodes[miner_name][NetOperator._HASH_RATE_KEY] = hash_rate

    def del_miner(self, miner_name: TypeAlias.MinerName):
        """
        Delete the miner from the network.
        :param miner_name: TypeAlias.MinerName
        :return: bool
        """
        self.network_graph.remove_node(miner_name)

    def send_block(self, source_miner: TypeAlias.MinerName, target_miner: TypeAlias.MinerName, block: Block):
        pass

    def broadcast_block(self, source_miner: TypeAlias.MinerName, block: Block):
        pass

    def fetch_block(self, target_miner: TypeAlias.MinerName, bid: TypeAlias.BlockID):
        pass

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
            miner_hash_rate = self.network_graph.nodes[miner_name][NetOperator._HASH_RATE_KEY]
            hash_rates.append(miner_hash_rate)
            total_hash_rate += miner_hash_rate

        if by_hash_rate:
            miner_name = np.random.choice(miners, p=np.array(hash_rates) / total_hash_rate)
        else:
            miner_name = np.random.choice(miners)
        return self[miner_name]

    def get_blockdag_type(self) -> DAGType:
        return self._total_blockdag.get_graph_type()

    def set_simulator(self, simulator):
        self._simulator = simulator
