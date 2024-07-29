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

from ditto.nodes import Miner, SystemParams
from ditto.blockdag import BlockDAG

from .netOperator import NetOperator


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
        genesis_block = net.init_network().pop()

        for c in range(number_of_miners):
            name = 'Miner' + str(c + 1)

            dag_for_miner = BlockDAG(system_params.dag_type)
            dag_for_miner.set_logger(self._logger)

            miner = Miner(name, dag_for_miner)
            miner.set_logger(self._logger)

            miner.pre_launch(genesis_block, system_params.refer_rule, system_params.consus_algo)
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

        return net
