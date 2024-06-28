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
from ditto.blockdag import BlockDAG, DAGType, TypeAlias
from ..referIface import ReferIface


class SimpleRef(ReferIface):
    """
    Reference all leaves of the blockDAG.

    Only for divergence blockDAG.
    """

    def __init__(self, blockdag: BlockDAG):
        super().__init__(blockdag)
        if self.blockdag.get_graph_type() != DAGType.DIVERGENCE:
            raise ValueError("The simple reference strategy is only for divergence blockDAG.")

    def get_virtual_pivot_ref(self) -> TypeAlias.BlockID | None:
        return None

    def get_virtual_common_refs(self) -> set[TypeAlias.BlockID]:
        return self.blockdag.get_leaves_blocks().copy()

    def get_virtual_new_height(self) -> TypeAlias.BlockHeight:
        leaves = self.blockdag.get_leaves_blocks()
        return max(self.blockdag[lid].height for lid in leaves) + 1
