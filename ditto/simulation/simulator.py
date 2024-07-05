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
import numpy as np
from simpy.util import start_delayed

from .. import logger
from ditto.network import NetOperator
from ditto.nodes import ReferIface, ConsusIface
from ditto.blockdag import DAGType, TypeAlias, Block

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
        self._env = sp.Environment(initial_time=1)
        self._network: NetOperator
        self._counter: int

        # Record the initial variables.
        self.__net_factory = net_factory
        self.__blockdag_type = blockdag_type
        self.__number_of_miners = number_of_miners
        self.__reference_class = reference_class
        self.__consensus_class = consensus_class
        self.__block_creation_rate = block_creation_rate
        self.__propagation_delay_parameter = propagation_delay_parameter

        self._process_init()

        self._stopped: sp.Event = self._env.event().succeed()  # Mark if running a simulation instance.
        self._paused: sp.Event = self._env.event().succeed()  # Control the stop and resume of the simulation.
        self._factor: float = 0  # The factor to adjust the simulation speed.

        self._logger = logger.getLogger(__name__)  # Logger for this class.

    def set_factor(self, factor: float):
        """
        Set the simulation factor.
        :param factor: float
        """
        print("set the factor to " + str(factor) + " at " + str(self._env.now))
        self._factor = factor
        last_time = self._env.now + factor
        if factor > 0:
            self._env = sp.RealtimeEnvironment(initial_time=last_time, factor=factor, strict=False)
        else:
            self._env = sp.Environment(initial_time=last_time)

        self._process_load()
        if self._stopped.triggered:
            self._stopped = self._env.event().succeed()
        else:
            self._stopped = self._env.event()
        if self._paused.triggered:
            self._paused = self._env.event().succeed()
        else:
            self._paused = self._env.event()

    def get_network(self) -> NetOperator:
        """
        Get the blockdag network.
        :return: NetOperator
        """
        return self._network

    def _network_running_init(self):
        self._network = self.__net_factory(self.__blockdag_type, self.__number_of_miners,
                                           self.__reference_class, self.__consensus_class,
                                           self.__block_creation_rate, self.__propagation_delay_parameter)
        self._network.set_simulator(self)

    def _network_running_process(self):
        """
        Running the network, generating blocks at a poisson rate.
        """
        while True:
            miner = self._network.get_random_miner()
            block = miner.mine_block()
            dd = np.random.poisson(self._network.block_creation_rate) * (self._factor if self._factor > 0 else 1.0)
            print(self._env.now, block, dd)
            yield self._env.timeout(dd)

    def _counter_init(self):
        self._counter = 0

    def _counter_process(self):
        while True:
            self._counter += 1
            print(self._env.now, self._counter)
            # if self._env.now == 10:
            #     self.pause()
            # if self._env.now == 20:
            #     self.stop()
            yield self._env.timeout(1 * (self._factor if self._factor > 0 else 1.0))

    def _process_init(self):
        # self._counter_init()
        self._network_running_init()

    def _process_load(self):
        # self._env.process(self._counter_process())
        self._env.process(self._network_running_process())

    def _run_simulation(self, steps: int):
        self._env.run(until=sp.events.AnyOf(self._env, [
            self._env.timeout(steps * (self._factor if self._factor > 0 else 1.0)),
            self._paused, self._stopped
        ]))

    def start(self, steps: int):
        """
        Start the simulation, only execute once until stop.
        """
        if self._stopped.triggered:
            # Reset the parameters.
            self._process_init()
            self._process_load()

            self._stopped = self._env.event()  # A new instance is initiated.
            self._paused = self._env.event()
            self._factor = 0

            print("start a simulation")
            self._run_simulation(steps)
        else:
            print("the simulation is already running")

    def pause(self):
        """
        Pause the simulation, allow to change some parameters.
        """
        if self._stopped.triggered:
            print("the simulation is stopped")
            return

        if not self._paused.triggered:
            print("pause the simulation")
            self._paused.succeed()
        else:
            print("the simulation is already paused")

    def resume(self, steps: int):
        """
        Resume the simulation, disable any changes when running.
        """
        if self._stopped.triggered:
            print("the simulation is stopped")
            return

        if self._paused.triggered:
            print("resume the simulation from " + str(self._env.now))
            self._paused = self._env.event()
            self._run_simulation(steps)
        else:
            print("the simulation does not need to resume")

    def stop(self):
        """
        Stop the simulation, reset all history data and wait for starting again.
        """
        if not self._stopped.triggered:
            self._stopped.succeed()
            self._env = sp.Environment(initial_time=1)
            print("stop the simulation")
            # TODO: 此处输出模拟结果

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
