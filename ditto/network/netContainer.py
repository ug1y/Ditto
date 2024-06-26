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
import random
from abc import abstractmethod
from typing import Set, Collection, Iterator

import networkx as nx
import numpy as np

from ditto.blockdag import TypeAlias, Block


class NetContainer(Collection):
    """
    A generic network container with network graph.

    Provide the interface for the miner.
    """

    # Dictionary key for the delay time.
    _DELAY_TIME_KEY = "delay_time"

    def __init__(self, propagation_delay_parameter: float = 1.0):
        self._inc_block_id: TypeAlias.BlockID = 0  # The global block id in the network.
        self.network_graph = nx.Graph()  # The network graph.
        self.propagation_delay_parameter = propagation_delay_parameter  # The delay parameters for the network

    def __contains__(self, miner_name: type(TypeAlias.MinerName)) -> bool:
        return miner_name in self.network_graph

    def __iter__(self) -> Iterator[TypeAlias.MinerName]:
        return iter(self.network_graph)

    def __len__(self) -> int:
        return len(self.network_graph)

    def __str__(self):
        return str(self.network_graph)

    def __repr__(self):
        return "NetContainer(inc_block_id=" + repr(self._inc_block_id) + \
            ", network_graph=" + repr(self.network_graph) + ")"

    def get_next_block_id(self) -> TypeAlias.BlockID:
        """
        Get the next block id from the global network.
        :return: TypeAlias.BlockID
        """
        self._inc_block_id += 1
        return self._inc_block_id

    def connect_peer(self, miner_name: TypeAlias.MinerName, peer_name: TypeAlias.MinerName, delay: float) -> bool:
        """
        Set the connection between two miners symmetrically.
        :param miner_name: TypeAlias.MinerName
        :param peer_name: TypeAlias.MinerName
        :param delay: float
        :return: bool
        """
        if miner_name not in self.network_graph or peer_name not in self.network_graph:
            return False

        self.network_graph.add_edge(miner_name, peer_name)
        self.network_graph.edges[(miner_name, peer_name)][NetContainer._DELAY_TIME_KEY] = delay
        return True

    def remove_peer(self, miner_name: TypeAlias.MinerName, peer_name: TypeAlias.MinerName) -> bool:
        """
        Cut off the connection between two miners.
        :param miner_name: TypeAlias.MinerName
        :param peer_name: TypeAlias.MinerName
        :return: bool
        """
        if miner_name not in self.network_graph or peer_name not in self.network_graph:
            return False

        self.network_graph.remove_edge(miner_name, peer_name)
        return True

    def discover_peer(self, miner_name: TypeAlias.MinerName, max_peer_num: int | float) -> Set[TypeAlias.MinerName]:
        """
        Connect random miners till to the max peer number.
        :param miner_name: TypeAlias.MinerName
        :param max_peer_num: int | float
        :return: Set[TypeAlias.MinerName]
        """
        new_peers = set()
        cur_peers = set(self.network_graph.neighbors(miner_name)) | {miner_name}
        while len(new_peers) < min(len(self.network_graph) - len(cur_peers), max_peer_num - len(cur_peers) + 1):
            potential_peer = random.choice(list(self.network_graph.nodes()))
            if potential_peer not in cur_peers:
                new_peers.add(potential_peer)

        return new_peers

    def get_neighbors(self, miner_name: TypeAlias.MinerName) -> Set[TypeAlias.MinerName]:
        """
        Get the connected neighbors of the specified miner.
        :param miner_name: TypeAlias.MinerName
        :return: Set[TypeAlias.MinerName]
        """
        if miner_name not in self.network_graph:
            return set()
        return set(self.network_graph.neighbors(miner_name))

    def get_delay(self, miner_name: TypeAlias.MinerName, peer_name: TypeAlias.MinerName) -> float:
        """
        Get the actual delay between two miners.
        if there is an edge between the miners, generate a random delay.
        :param miner_name: TypeAlias.MinerName
        :param peer_name: TypeAlias.MinerName
        :return: float
        """
        if self.network_graph.has_edge(miner_name, peer_name):
            return self.network_graph[(miner_name, peer_name)][NetContainer._DELAY_TIME_KEY]

        return np.random.poisson(self.propagation_delay_parameter)

    @abstractmethod
    def send_block(self, source_miner: TypeAlias.MinerName, target_miner: TypeAlias.MinerName, block: Block):
        """
        Send a block from the source miner to the target miner.
        :param source_miner: TypeAlias.MinerName
        :param target_miner: TypeAlias.MinerName
        :param block: Block
        """
        pass

    @abstractmethod
    def broadcast_block(self, source_miner: TypeAlias.MinerName, block: Block):
        """
        Broadcast a block from the source miner to its neighbors.
        :param source_miner: TypeAlias.MinerName
        :param block: Block
        """
        pass

    @abstractmethod
    def fetch_block(self, target_miner: TypeAlias.MinerName, bid: TypeAlias.BlockID):
        """
        Retrieve the block with the given block id from its neighbors in the network.
        :param target_miner: TypeAlias.MinerName
        :param bid: TypeAlias.BlockID
        """
        pass
