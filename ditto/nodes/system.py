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
from dataclasses import dataclass

from ditto.blockdag import DAGType

from ditto.nodes.reference import ReferIface, ChainRef, LeavesRef, GossipRef
from ditto.nodes.consensus import ConsusIface, NakamotoCons, PhantomCons, ULBlockDAGCons, PikavoltCons
from ditto.nodes.reference import MaliciousChainRef, MaliciousLeavesRef


@dataclass
class SystemParams:
    """
    Wrap the key parameters of the simulated system.
    """
    dag_type: DAGType
    refer_rule: type[ReferIface]
    consus_algo: type[ConsusIface]
    malicious_ref: type[ReferIface] = None


Systems = {
    'Nakamoto': SystemParams(DAGType.CONVERGENCE, ChainRef, NakamotoCons, MaliciousChainRef),
    'Phantom': SystemParams(DAGType.DIVERGENCE, LeavesRef, PhantomCons, MaliciousLeavesRef),
    'ULBlockDAG': SystemParams(DAGType.DIVERGENCE, LeavesRef, ULBlockDAGCons, MaliciousLeavesRef),
    'Pikavolt': SystemParams(DAGType.DIVERGENCE, LeavesRef, PikavoltCons, MaliciousLeavesRef),
    'Hashgraph': SystemParams(DAGType.PARALLEL, GossipRef, None),
}
