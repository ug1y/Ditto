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

from ditto.nodes import Miner, ReferIface, ConsusIface
from ditto.blockdag import DAGType, BlockDAG

from .netOperator import NetOperator


class NetFactory:
    def __init__(self, logger: logging.Logger = None):
        self._logger = logger

    def PeerNet(self, blockdag_type: DAGType, number_of_miners: int,
                reference_class: type[ReferIface], consensus_class: type[ConsusIface],
                block_creation_rate: float, propagation_delay_parameter: float) -> NetOperator:
        """Peer to peer network in which the number of neighbors is half of network scale."""
        dag_for_net = BlockDAG(blockdag_type)
        dag_for_net.set_logger(self._logger)

        net = NetOperator(dag_for_net, propagation_delay_parameter, block_creation_rate)
        net.set_logger(self._logger)
        net.set_consus_handler(consensus_class)

        b1 = net.init_network().pop()

        for c in range(number_of_miners):
            name = 'Miner' + str(c + 1)

            dag_for_miner = BlockDAG(blockdag_type)
            dag_for_miner.set_logger(self._logger)

            miner = Miner(name, dag_for_miner, int(number_of_miners / 3 + 1))
            miner.set_logger(self._logger)

            miner.pre_launch(b1, reference_class, consensus_class)
            net.add_miner(miner)

        for i in net:
            net[i].discover_peer()

        return net
