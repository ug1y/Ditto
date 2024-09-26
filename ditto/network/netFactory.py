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

import numpy

from ditto.nodes import Miner, SystemParams
from ditto.blockdag import BlockDAG, DAGType

from ditto.network.netOperator import NetOperator


def PeerNet(net: NetOperator) -> NetOperator:
    """Peer to peer network in which the number of neighbors is one-third of network scale."""
    for miner in net:
        net[miner].max_peer_num = int(len(net) / 3 + 1)
        net[miner].discover_peer()

    return net


def FullNet(net: NetOperator) -> NetOperator:
    """Full connected network in which the miners are all connected to each other."""
    for miner in net:
        net[miner].max_peer_num = 0
        net[miner].discover_peer()

    return net


def RingNet(net: NetOperator) -> NetOperator:
    """Ring network in which the miners connecting from start to end."""
    miners = list(net)
    net[miners[0]].connect_peer(miners[-1])
    for i in range(1, len(miners)):
        # net[miners[i]].max_peer_num = 2
        net[miners[i]].connect_peer(miners[i - 1])

    return net


def StarNet(net: NetOperator) -> NetOperator:
    """Star network in which the miners are all connected to the first miner."""
    miners = list(net)
    for i in range(1, len(miners)):
        net[miners[i]].connect_peer(miners[0])

    return net


def TreeNet(net: NetOperator) -> NetOperator:
    """Tree network in which the miners are connected to form a binary tree."""
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


class NetFactory:
    NetTemplates = {
        'PeerNet': PeerNet,
        'FullNet': FullNet,
        'RingNet': RingNet,
        'StarNet': StarNet,
        'TreeNet': TreeNet
    }

    def __init__(self, logger: logging.Logger = None):
        self._logger = logger

    def select_template(self, net_name, *args, **kwargs) -> NetOperator:
        if net_name in self.NetTemplates.keys():
            return self.NetTemplates[net_name](self._basic_net_init(*args, **kwargs))
        else:
            raise AttributeError('NetTemplates %s not found' % net_name)

    def _basic_net_init(self, system_params: SystemParams, number_of_miners: int, computing_hash_rate: float,
                        block_creation_interval: float, propagation_delay_parameter: float) -> NetOperator:
        """Initialize the basic network."""
        dag_for_net = BlockDAG(system_params.dag_type)
        dag_for_net.set_logger(self._logger)

        net = NetOperator(dag_for_net, propagation_delay_parameter, block_creation_interval)
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
            net.add_miner(miner, numpy.random.poisson(computing_hash_rate))

        return net
