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
from ditto.simulation import Simulator
from ditto.nodes import ConsusIface, StatusType
from ditto.blockdag import BlockDAG


class StatsRecorder:
    """
    The statistics recorder to record the statistics of the simulation.
    """

    def __init__(self, sim: Simulator, dag: BlockDAG, cons: ConsusIface):
        self._sim: Simulator = sim
        self._dag: BlockDAG = dag
        self._cons: ConsusIface = cons

    def get_consus_algo_name(self) -> str:
        return self._cons.algo_name

    def get_network_scale(self) -> int:
        return len(self._sim.network)

    def get_block_creation_interval(self) -> float:
        return self._sim.network.block_creation_interval

    def get_block_propagation_delay(self) -> float:
        return self._sim.network.propagation_delay_parameter

    def get_total_created_blocks(self) -> int:
        return len(self._dag)

    def compute_throughput(self):
        # Eliminate the effect of the block interval, use the unit of sim time.
        blk_interval = self._sim.network.block_creation_interval

        cur_time = self._sim.env.now
        processed = self._cons.get_processed_blocks()
        dec_blks = self._cons.get_processed_blocks(StatusType.DECIDED)

        # Return the relative processing rate, the relative decided rate
        # return ((len(processed), len(processed) / cur_time * blk_interval),
        #         (len(dec_blks), len(dec_blks) / cur_time * blk_interval))

        return len(dec_blks) / cur_time * blk_interval

    def compute_latency(self):
        # Eliminate the effect of the block interval, use the unit of sim time.
        blk_interval = self._sim.network.block_creation_interval

        dec_blks = self._cons.get_processed_blocks(StatusType.DECIDED)
        latencies = dict()
        for b in dec_blks - self._dag.column_blocks[0]:
            latencies[b] = (int(self._dag[self._cons.consus_logs[b][0]].data) - int(self._dag[b].data)) / blk_interval

        average_latency = (sum(latencies.values()) / len(latencies.values())) if len(latencies.values()) > 0 else 0.0
        # return average_latency, latencies
        return average_latency

    def compute_change_dist(self):
        processed_blks = self._cons.get_processed_blocks()

        cdist = dict()
        for b in processed_blks:
            c = len(self._cons.consus_logs[b]) if b in self._cons.consus_logs else 0
            if c not in cdist:
                cdist[c] = 0
            cdist[c] += 1

        ratio = cdist[1] / sum([v for k, v in cdist.items() if k > 0]) if 1 in cdist else 0.0
        # return ratio, dict(sorted(cdist.items()))
        return ratio

    def output_info(self, is_print: bool = True):
        info = f"The Consensus Algorithm: {self.get_consus_algo_name()}\n"
        info += f"The Network Scale (miners): {self.get_network_scale()}\n"
        info += f"The Block Creation Interval: {self.get_block_creation_interval()}\n"
        info += f"The Block Propagation Delay: {self.get_block_propagation_delay()}\n"
        if is_print:
            print(info)
        return info

    def output_stats(self, is_print: bool = True):
        stats = f"The total created blocks: {self.get_total_created_blocks()}\n"
        stats += f"The Simulated Throughput: {self.compute_throughput()}\n"
        stats += f"The Simulated Latency: {self.compute_latency()}\n"
        stats += f"The Simulated Change Distribution: {self.compute_change_dist()}\n"
        if is_print:
            print(stats)
        return stats
