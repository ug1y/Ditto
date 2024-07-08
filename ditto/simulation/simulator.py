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
from ditto.blockdag import TypeAlias, Block

from .netSimulation import NetSimulation


class Simulator(NetSimulation):
    """
    Simulate the blockDAG running.
    """

    def __init__(self, network: NetOperator, factor: float = 0):
        """
        Initialize the simulator and network environment.
        """
        self._env = sp.RealtimeEnvironment(initial_time=1, factor=factor, strict=False) \
            if factor > 0 else sp.Environment(initial_time=1)
        self._network = network
        self._network.set_simulator(self)

        self._started: bool = False  # Mark if started a simulation instance.
        self._stopped: sp.Event = self._env.event()  # Mark if stopped the simulation instance.
        self._paused: sp.Event = self._env.event()  # Control the stop and resume of the simulation.

        self._correct = -1  # The offset of the simulation steps.
        self._factor = factor  # The factor to adjust the simulation speed.

        self._logger = logger.getLogger(__name__)  # Logger for this class.

        self._counter = 0  # Use for test simulation.

    def set_factor(self, factor: float):
        """
        Set the simulation factor.
        :param factor: float
        """
        print("set the factor to " + str(factor) + " at " + str(self._env.now))
        self._correct = -1
        self._factor = factor
        last_time = self._env.now + factor if self._paused.triggered else self._env.now
        self._env = sp.RealtimeEnvironment(initial_time=last_time, factor=factor, strict=False) \
            if factor > 0 else sp.Environment(initial_time=last_time)
        self._stopped = self._env.event().succeed() if self._stopped.triggered else self._env.event()
        self._paused = self._env.event().succeed() if self._paused.triggered else self._env.event()
        if self._started:
            self._process_load()

    def get_network(self) -> NetOperator:
        """
        Get the blockdag network.
        :return: NetOperator
        """
        return self._network

    def _network_running_process(self):
        """
        Running the network, generating blocks at a poisson rate.
        """
        while True:
            miner = self._network.get_random_miner()
            block = miner.mine_block()
            next_mining_wait = np.random.poisson(self._network.block_creation_rate) * (self._factor if self._factor > 0 else 1)
            print("current time: %3.f , next wait: %2.f, mining: %s" % (self._env.now, next_mining_wait, block))
            yield self._env.timeout(next_mining_wait)

    def _counter_process(self):
        while True:
            self._counter += 1
            print(self._env.now, self._counter)
            if self._env.now == 5:
                self.pause()
            if self._env.now == 20:
                self.stop()
            yield self._env.timeout(1 * (self._factor if self._factor > 0 else 1))

    def _process_load(self):
        # self._env.process(self._counter_process())
        self._env.process(self._network_running_process())

    def _run_simulation(self, steps: int):
        self._env.run(until=sp.events.AnyOf(self._env, [
            self._env.timeout((steps + self._correct) * (self._factor if self._factor > 0 else 1)),
            self._paused, self._stopped
        ]))

        if not self._stopped.triggered:
            self.pause()

    def start(self, steps: int):
        """
        Start the simulation, only execute once until stop.
        """
        if self._stopped.triggered:
            print("the simulation is stopped")
            return

        if not self._started:
            # Load process.
            self._process_load()

            print("start a simulation")
            self._started = True
            self._run_simulation(steps)
            self._correct = 0
        else:
            print("the simulation is already running")

    def pause(self):
        """
        Pause the simulation, allow to change some parameters.
        """
        if not self._started:
            print("the simulation is not started")
            return
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
        if not self._started:
            print("the simulation is not started")
            return
        if self._stopped.triggered:
            print("the simulation is stopped")
            return

        if self._paused.triggered:
            print("resume the simulation from " + str(self._env.now))
            self._paused = self._env.event()
            self._run_simulation(steps)
            self._correct = 0
        else:
            print("the simulation does not need to resume")

    def stop(self):
        """
        Stop the simulation, reset all history data and wait for starting again.
        """
        if not self._stopped.triggered:
            print("stop the simulation")
            self._stopped.succeed()
            # Output the result
            print("network:", str(self._network.network_graph.nodes))
            print("blockdag:", repr(self._network.total_blockdag))

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
