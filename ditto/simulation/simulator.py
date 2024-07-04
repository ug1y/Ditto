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
import simpy as sp

from .. import logger
from ditto.network import NetOperator
from ditto.nodes import ReferIface, ConsusIface
from ditto.blockdag import DAGType

from .netSimulation import NetSimulation


class Simulator(NetSimulation):
    """
    Simulate the blockDAG running.
    """

    def __init__(self,
                 net_factory,
                 blockdag_type: DAGType,
                 number_of_miners: int,
                 reference_class: type[ReferIface],
                 consensus_class: type[ConsusIface],
                 block_creation_rate: float,
                 propagation_delay_parameter: float):
        """
        Initialize the simulator and network environment.
        """
        self._env = sp.RealtimeEnvironment()

        self._network: NetOperator = net_factory(blockdag_type, number_of_miners,
                                                 reference_class, consensus_class,
                                                 block_creation_rate, propagation_delay_parameter)

        self._startup: bool = False  # Mark if running a simulation instance.
        self._control: bool = False  # Control the stop and resume of the simulation.
        self._factor: float = 1.0  # The factor to adjust the simulation speed.

        self._logger = logger.getLogger(__name__)  # Logger for this class.

    def set_factor(self, factor: float):
        """
        Set the simulation factor.
        :param factor: float
        """
        self._factor = factor

    def get_network(self) -> NetOperator:
        """
        Get the blockdag network.
        :return: NetOperator
        """
        return self._network

    def send_block_with_delay(self):
        pass
