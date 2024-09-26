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
import os
import simpy

from ditto import config
from ditto.blockdag import BlockDAG
from ditto.network import NetFactory
from ditto.nodes import Systems, Attacker
from ditto.simulation import StatsRecorder, Simulator


def run_server(port: int = 5006):
    print('Opening Bokeh application on http://localhost:' + str(port) + '/')
    os.environ['PYTHONPATH'] = os.getcwd()  # Add the current working directory to the PYTHONPATH
    os.system('bokeh serve --show ' + os.path.join('ditto', 'interaction') + ' --port ' + str(port))


def run_simulation(net_template: str = 'PeerNet', cons_method: str = 'Nakamoto',
                   scale: int = 6, rate: float = 10.0,
                   interval: float = 10.0, delay: float = 30.0,
                   until: int = 100):
    mylogger = config.create_logger(log_level=logging.WARNING)
    factory = NetFactory(mylogger)
    net = factory.select_template(net_name=net_template, system_params=Systems[cons_method],
                                  number_of_miners=scale, computing_hash_rate=rate,
                                  block_creation_interval=interval, propagation_delay_parameter=delay)

    sim = Simulator(net)
    sim.set_logger(mylogger)
    sim.run(until)
    print(f"Simulation Done at {sim.env.now}!\n")
    # print("Total blockDAG:", repr(net.total_blockdag))

    if net.consus_handler is not None:
        srd = StatsRecorder(sim, net.total_blockdag, net.consus_handler)

        print("===== Simulation Information =====")
        srd.output_info()

        print("===== Statistical Records =====")
        srd.output_stats()


def run_with_attack(net_template: str = 'PeerNet', cons_method: str = 'Nakamoto',
                    scale: int = 6, rate: float = 10.0,
                    interval: float = 10.0, delay: float = 30.0,
                    until: int = 100, times: int = 0, power: float = 0.3):
    mylogger = config.create_logger(log_level=logging.WARNING)
    factory = NetFactory(mylogger)
    params = Systems[cons_method]
    net = factory.select_template(net_name=net_template, system_params=params,
                                  number_of_miners=scale - 1, computing_hash_rate=rate,
                                  block_creation_interval=interval, propagation_delay_parameter=delay)

    dag_for_attacker = BlockDAG(params.dag_type)
    dag_for_attacker.set_logger(mylogger)
    attacker = Attacker("Attacker", dag_for_attacker, True)
    attacker.set_logger(mylogger)

    attacker.pre_launch(list(net.genesis_blocks)[0], params.malicious_ref, net, params.consus_algo)
    malicious_rate = sum([net.get_miner_hash_rate(m) for m in net]) * power / (1 - power)
    net.add_miner(attacker, malicious_rate)

    # Add attacker to the network.
    attack_delay = 0.0
    for m in net:
        if m != attacker.name:
            net[m].connect_peer(attacker.name, attack_delay)

    sim = Simulator(net)
    sim.set_logger(mylogger)
    # Set attack event to the simulation.
    attack_event = sim.env.event()
    attacker.set_attack_event(attack_event, times)
    sim.run(until=simpy.events.AnyOf(sim.env, [attack_event, sim.env.timeout(until)]))
    print(f"Simulation Done at {sim.env.now}!\n")
    # print("Total blockDAG:", repr(net.total_blockdag))

    if net.consus_handler is not None:
        srd = StatsRecorder(sim, net.total_blockdag, net.consus_handler)

        print("===== Attacker Capabilities =====")
        print("Malicious Miner Number:", 1)
        print("Malicious Network Delay:", attack_delay)
        print("Malicious Power Ratio:", power)
        print()

        print("===== Simulation Information =====")
        srd.output_info()

        print("===== Statistical Records =====")
        srd.output_stats()


if __name__ == '__main__':
    run_with_attack()
