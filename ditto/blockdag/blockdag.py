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
from collections.abc import Collection
from typing import Iterator
import networkx as nx

from .block import Block


class BlockDAG(Collection):
    """
    An implementation of a generic BlockDAG, organizing blocks in a collection.

    Support to build the type of divergence, parallel, and convergence DAG.
    """

    # Dictionary key for the block's data.
    BLOCK_DATA_KEY = "block_data"

    def __init__(self):
        self._G = nx.DiGraph()  # A networkx directed graph object.
        self._leaves = set()  # Set of all the leaves in the graph.
        self._cluster = list(set())  # List of the set of blocks in the specified height.

    def __contains__(self, bid: type(Block.BlockID)) -> bool:
        return bid in self._G

    def __getitem__(self, bid):
        return self._G[bid][self.BLOCK_DATA_KEY]

    def __iter__(self) -> Iterator[Block]:
        return iter(self._G)

    def __len__(self) -> int:
        return len(self._G)

    def __str__(self):
        return str(self._G)

    def __repr__(self):
        return "BlockDAG(G=" + repr(self._G) + \
            ", leaves=" + repr(self._leaves) + \
            ", cluster=" + repr(self._cluster) + ")"
