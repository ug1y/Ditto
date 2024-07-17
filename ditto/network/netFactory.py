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
from ditto.nodes import Miner, ReferIface, ConsusIface
from ditto.blockdag import DAGType, BlockDAG

from .netOperator import NetOperator


def PeerNet(blockdag_type: DAGType, number_of_miners: int,
            reference_class: type[ReferIface], consensus_class: type[ConsusIface],
            block_creation_rate: float, propagation_delay_parameter: float) -> NetOperator:
    """Peer to peer network in which the number of neighbors is half of network scale."""

    net = NetOperator(BlockDAG(blockdag_type), propagation_delay_parameter, block_creation_rate)
    b1 = net.init_network().pop()

    for c in range(number_of_miners):
        name = 'Miner' + str(c + 1)
        miner = Miner(name, BlockDAG(blockdag_type), int(number_of_miners / 3 + 1))
        miner.pre_launch(b1, reference_class, consensus_class)
        net.add_miner(miner)

    for i in net:
        net[i].discover_peer()

    return net

