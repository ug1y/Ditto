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
from enum import Enum


class TypeAlias:
    """
    Type aliases, no practical use.
    """
    BlockID = int
    TransactionID = int
    MinerName = str
    BlockHeight = int
    BlockSize = float


class BlockType(Enum):
    """
    Define different types of blocks.
    """
    ORPHAN = 0  # orphan block
    GENESIS = 1  # genesis block
    MINED = 2  # mined block


class TransactionType(Enum):
    """
    Define different types of transactions.
    """
    REGULAR = 0  # regular transaction
    REPEATED = 1  # repeated transaction
    CONFLICT = 2  # conflict transaction


class DAGType(Enum):
    """
    Define different types of blockDAG.
    """
    DIVERGENCE = 0  # divergence blockDAG
    PARALLEL = 1  # parallel blockDAG
    CONVERGENCE = 2  # convergence blockDAG


class EdgeType(Enum):
    """
    Define different types of edges in the blockDAG.
    """
    PIVOT = 0  # pivot edge by pivot reference.
    COMMON = 1  # common edge by common reference.
