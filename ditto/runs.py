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

from ditto import config
from ditto.blockdag import BlockDAG
from ditto.network import NetFactory, SelectNetTemplate
from ditto.nodes import Systems, Miner, Attacker
from ditto.simulation import StatsRecorder, Simulator


def run_server(port: int = 5006):
    print('Opening Bokeh application on http://localhost:' + str(port) + '/')
    os.environ['PYTHONPATH'] = os.getcwd()  # Add the current working directory to the PYTHONPATH
    os.system('bokeh serve --show ' + os.path.join('ditto', 'interaction') + ' --port ' + str(port))


def run_simulation(until: int = 100, net_template: str = 'PeerNet', cons_method: str = 'Nakamoto',
                   scale: int = 6, rate: float = 10.0, delay: float = 30.0):
    mylogger = config.create_logger(log_level=logging.WARNING)
    factory = NetFactory(mylogger)
    net = SelectNetTemplate(factory, net_name=net_template, system_params=Systems[cons_method], number_of_miners=scale,
                            block_creation_rate=rate, propagation_delay_parameter=delay)

    sim = Simulator(net)
    sim.set_logger(mylogger)
    sim.run(until)

    print("Simulation Done!\n")
    # print(f"The simulation parameters: (Network='{net_template}', Consensus='{cons_method}', "
    #       f"Scale='{scale}', Rate='{rate}', Delay='{delay}')")
    print("Total blockDAG:", repr(net.total_blockdag))

    # if net.consus_handler is not None:
    #     print("The consensus blocks set:", net.consus_handler.get_processed_blocks(StatusType.DECIDED))
    #     print("The finished blocks sorted:", net.consus_handler.sort_finished_blocks())
    #     print("The consensus change logs:", net.consus_handler.consus_logs)

    if net.consus_handler is not None:
        srd = StatsRecorder(sim, net.total_blockdag, net.consus_handler)
        print("\nStatistical Records:")
        print("[Consensus Algorithm]", srd.get_consus_algo_name())
        print("[Network Scale]", srd.get_network_scale())
        print("[Block Creation Rate]", srd.get_block_creation_rate())
        print("[Block Propagation Delay]", srd.get_block_propagation_delay_())

        print("The simulated throughput: ", srd.compute_throughput())
        print("The simulated latency: ", srd.compute_latency())
        print("The simulated change distribution: ", srd.compute_change_dist())


def run_with_attack():
    mylogger = config.create_logger()
    factory = NetFactory(mylogger)
    params = Systems["Nakamoto"]
    net = SelectNetTemplate(factory, net_name="PeerNet", system_params=params, number_of_miners=5,
                            block_creation_rate=10, propagation_delay_parameter=30)

    dag_for_attacker = BlockDAG(params.dag_type)
    dag_for_attacker.set_logger(mylogger)
    attacker = Attacker("Attacker", dag_for_attacker)
    attacker.set_logger(mylogger)

    attacker.pre_launch(list(net.genesis_blocks)[0], params.malicious_ref, net, params.consus_algo)
    net.add_miner(attacker, 40.0)
    print(repr(attacker))
    print(attacker.refer_handler.blocks_queue)

    for m in net:
        if m != attacker.name:
            net[m].connect_peer(attacker.name, 0.0)

    print([(m, net.get_miner_hash_rate(m)) for m in net])
    print([(e[0], e[1], net.get_connect_delay_time(e)) for e in net.network_graph.edges])

    sim = Simulator(net)
    sim.set_logger(mylogger)
    sim.run(100)

    if net.consus_handler is not None:
        srd = StatsRecorder(sim, net.total_blockdag, net.consus_handler)
        print("\nStatistical Records:")
        print("[Consensus Algorithm]", srd.get_consus_algo_name())
        print("[Network Scale]", srd.get_network_scale())
        print("[Block Creation Rate]", srd.get_block_creation_rate())
        print("[Block Propagation Delay]", srd.get_block_propagation_delay_())

        print("The simulated throughput: ", srd.compute_throughput())
        print("The simulated latency: ", srd.compute_latency())
        print("The simulated change distribution: ", srd.compute_change_dist())


if __name__ == '__main__':
    run_with_attack()
