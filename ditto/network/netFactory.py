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

import numpy as np

from ditto.nodes import Miner, SystemParams
from ditto.blockdag import BlockDAG, DAGType

from ditto.network.netOperator import NetOperator


class NetFactory:
    def __init__(self, logger: logging.Logger = None):
        self._logger = logger

    def _basic_net_init(self, system_params: SystemParams, number_of_miners: int,
                        block_creation_rate: float, propagation_delay_parameter: float) -> NetOperator:
        """Initialize the basic network."""
        dag_for_net = BlockDAG(system_params.dag_type)
        dag_for_net.set_logger(self._logger)

        net = NetOperator(dag_for_net, propagation_delay_parameter, block_creation_rate)
        net.set_logger(self._logger)
        net.set_consus_handler(system_params.consus_algo)

        if system_params.dag_type == DAGType.PARALLEL:
            genesis_blocks = list(net.init_network(number_of_miners))
        else:
            genesis_blocks = list(net.init_network(1)) * number_of_miners

        for c in range(number_of_miners):
            name = 'Miner' + str(c + 1)

            dag_for_miner = BlockDAG(system_params.dag_type)
            dag_for_miner.set_logger(self._logger)

            miner = Miner(name, dag_for_miner)
            miner.set_logger(self._logger)

            if system_params.dag_type == DAGType.PARALLEL:
                genesis_blocks[c].miner = miner.name  # parallel blockdag record miner name in genesis blocks.

            miner.pre_launch(genesis_blocks[c], system_params.refer_rule, net, system_params.consus_algo)
            net.add_miner(miner)

        return net

    def PeerNet(self, system_params: SystemParams, number_of_miners: int,
                block_creation_rate: float, propagation_delay_parameter: float) -> NetOperator:
        """Peer to peer network in which the number of neighbors is one-third of network scale."""
        net = self._basic_net_init(system_params, number_of_miners, block_creation_rate, propagation_delay_parameter)

        for miner in net:
            net[miner].max_peer_num = int(number_of_miners / 3 + 1)
            net[miner].discover_peer()

        return net

    def FullNet(self, system_params: SystemParams, number_of_miners: int,
                block_creation_rate: float, propagation_delay_parameter: float) -> NetOperator:
        """Full connected network in which the miners are all connected to each other."""
        net = self._basic_net_init(system_params, number_of_miners, block_creation_rate, propagation_delay_parameter)

        for miner in net:
            net[miner].max_peer_num = 0
            net[miner].discover_peer()

        return net

    def RingNet(self, system_params: SystemParams, number_of_miners: int,
                block_creation_rate: float, propagation_delay_parameter: float) -> NetOperator:
        """Ring network in which the miners connecting from start to end."""
        net = self._basic_net_init(system_params, number_of_miners, block_creation_rate, propagation_delay_parameter)

        miners = list(net)
        net[miners[0]].connect_peer(miners[-1])
        for i in range(1, len(miners)):
            # net[miners[i]].max_peer_num = 2
            net[miners[i]].connect_peer(miners[i - 1])

        return net

    # def RandomNet(self, system_params: SystemParams, number_of_miners: int,
    #               block_creation_rate: float, propagation_delay_parameter: float) -> NetOperator:
    #     """Random network in which the miners are connected to random numbers of miners."""
    #     net = self._basic_net_init(system_params, number_of_miners, block_creation_rate, propagation_delay_parameter)
    #
    #     for miner in net:
    #         net[miner].max_peer_num = np.random.randint(low=1, high=number_of_miners)
    #         net[miner].discover_peer()
    #
    #     return net

    def StarNet(self, system_params: SystemParams, number_of_miners: int,
                block_creation_rate: float, propagation_delay_parameter: float) -> NetOperator:
        """Star network in which the miners are all connected to the first miner."""
        net = self._basic_net_init(system_params, number_of_miners, block_creation_rate, propagation_delay_parameter)

        miners = list(net)
        for i in range(1, len(miners)):
            net[miners[i]].connect_peer(miners[0])

        return net

    # def LineNet(self, system_params: SystemParams, number_of_miners: int,
    #             block_creation_rate: float, propagation_delay_parameter: float) -> NetOperator:
    #     """ Line network in which the miners are connected to the previous miner in a line."""
    #     net = self._basic_net_init(system_params, number_of_miners, block_creation_rate, propagation_delay_parameter)
    #
    #     miners = list(net)
    #     for i in range(1, len(miners)):
    #         net[miners[i]].connect_peer(miners[i - 1])
    #
    #     return net

    def TreeNet(self, system_params: SystemParams, number_of_miners: int,
                block_creation_rate: float, propagation_delay_parameter: float) -> NetOperator:
        """Tree network in which the miners are connected to form a binary tree."""
        net = self._basic_net_init(system_params, number_of_miners, block_creation_rate, propagation_delay_parameter)

        miners = list(net)
        q = [miners[0]]
        b = 2

        for i in range(1, len(miners)):
            miner = q[0]
            net[miner].connect_peer(miners[i])
            q.append(miners[i])
            b -= 1
            if b == 0:
                q.pop(0)
                b = 2

        return net


def SelectNetTemplate(factory: NetFactory, net_name, *args, **kwargs) -> NetOperator:
    net_to_use = getattr(factory, net_name)
    if callable(net_to_use):
        return net_to_use(*args, **kwargs)
    else:
        raise AttributeError('NetFactory attribute %s not found' % net_name)
