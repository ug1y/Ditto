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
import time
from typing import Union

import simpy as sp
import numpy as np
from simpy import Event
from simpy.core import SimTime
from simpy.util import start_delayed

from ditto.network import NetOperator
from ditto.blockdag import TypeAlias, Block

from ditto.simulation.netSimulation import NetSimulation


class Simulator(NetSimulation):
    """
    Simulate the blockDAG running.
    """

    FOR_LOG_NAME = "simulator"

    def __init__(self, network: NetOperator, factor: float = 0):
        """
        Initialize the simulator and network environment.
        """
        self._env = sp.RealtimeEnvironment(factor=factor, strict=False) \
            if factor > 0 else sp.Environment()
        self._network = network
        self._factor = factor  # The factor to adjust the simulation speed.

        self._logger: logging.Logger = None  # Logger for this class.

        self._network.set_simulator(self)  # Enable network transmission delay.
        self._process_load()  # Load simulation process.

        self._counter = 0  # Use for test simulation.

    def set_logger(self, logger: logging.Logger):
        self._logger = logger

    @property
    def network(self) -> NetOperator:
        """
        Get the blockdag network.
        :return: NetOperator
        """
        return self._network

    @property
    def now(self) -> SimTime:
        """
        Get the current simulation time.
        """
        return self._env.now

    def _network_process(self):
        """
        Running the network, generating blocks at a poisson rate.
        """
        while True:
            miner = self._network.get_random_miner()
            start = time.time()
            block = miner.mine_block()
            block.data = self.now
            end = time.time()
            next_mining_wait = np.random.poisson(self._network.block_creation_rate) * \
                               (self._factor if self._factor > 0 else 1)

            # print("current time: %3.f , next wait: %2.f, mining: %s" % (self._env.now, next_mining_wait, block))
            if self._logger is not None:
                self._logger.info("%s: At simulation time %3.f, it selects %s who mines %s, costs %.3f ms.",
                                  self.FOR_LOG_NAME, self._env.now, miner.name, block, (end - start) * 1000)
            yield self._env.timeout(next_mining_wait)

    def _counter_process(self):
        while True:
            self._counter += 1
            next_counting_wait = 1 * (self._factor if self._factor > 0 else 1)
            print(self._env.now, self._counter)
            yield self._env.timeout(next_counting_wait)

    def _process_load(self):
        # self._env.process(self._counter_process())
        self._env.process(self._network_process())

    def step(self):
        """
        Execute one step of the simulation.
        """
        self._env.step()

    def run(self, until: Union[SimTime, Event, None] = None):
        """
        Execute until the given time.
        """
        self._env.run(until)

    def send_block_with_delay(self, source_miner: TypeAlias.MinerName, target_miner: TypeAlias.MinerName,
                              block: Block, delay: float):
        """
        Simulate network delay to send a block between miners.
        :param source_miner: TypeAlias.MinerName
        :param target_miner: TypeAlias.MinerName
        :param block: Block
        :param delay: float
        """

        def send_block_process(env):
            receiver = self._network[target_miner]
            receiver.add_block(block)
            receiver.sync_block()
            yield env.timeout(0)

        start_delayed(self._env, send_block_process(self._env), delay)
