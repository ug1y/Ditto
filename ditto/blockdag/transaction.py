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
from collections.abc import Hashable
from dataclasses import dataclass
from typing import Set

from .typedef import TypeAlias, TransactionType


@dataclass
class Transaction(Hashable):
    """
    An implementation of a marked Transaction.

    Transaction ID of a transaction - the hash of the transaction.
    """

    # Basic parameters controlled by interaction module.
    txid: TypeAlias.TransactionID = 0  # The unique ID of the transaction.
    ttype: TransactionType = TransactionType.REGULAR  # The type of the transaction, see TransactionType.
    blks: Set[TypeAlias.BlockID] = frozenset()  # The blocks that contain the transaction in the blockDAG.
    note: Hashable = None  # Optional, additional note recorded in the transaction.

    def __hash__(self) -> int:
        return self.txid

    def __str__(self):
        return "{Transaction: " + str(self.txid) + \
            ", Type: " + str(self.ttype.name) + \
            ", Related Blocks: " + str(list(self.blks)) + "}"
