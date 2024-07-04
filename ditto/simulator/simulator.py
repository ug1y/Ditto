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
from abc import ABC, abstractmethod

import simpy as sp


class NetSimulation(ABC):
    """
    Simulator handler for network.
    """

    @abstractmethod
    def send_block_with_delay(self):
        """
        Simulate network delay to send a block between miners.
        """
        pass


class Simulator(NetSimulation):
    """
    Simulate the blockDAG running.
    """

    def __init__(self,
                 network_template,
                 number_of_miners: int,
                 block_creation_rate: float,
                 propagation_delay_parameter: float):
        """
        Initialize the simulator and network environment.
        """

    def send_block_with_delay(self):
        pass
