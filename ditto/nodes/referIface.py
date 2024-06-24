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

from abc import ABC, abstractmethod
from typing import Set

from ditto.blockdag import BlockDAG, TypeAlias


class ReferIface(ABC):
    """
    Reference strategies interface.
    """

    def __init__(self, blockdag: BlockDAG):
        """
        Rely on the blockdag object with only read operation.
        """
        self.blockdag = blockdag

    @abstractmethod
    def get_virtual_pivot_ref(self) -> TypeAlias.BlockID | None:
        """
        Get the virtual pivot ref where the divergence blockDAG return None.
        :return: TypeAlias.BlockID | None
        """
        pass

    @abstractmethod
    def get_virtual_common_refs(self) -> Set[TypeAlias.BlockID]:
        """
        Get the virtual common refs by different strategies.
        :return: Set[TypeAlias.BlockID]
        """
        pass

    @abstractmethod
    def get_virtual_new_height(self) -> TypeAlias.BlockHeight:
        """
        Get the virtual new height if adopt this strategy.
        :return: TypeAlias.BlockHeight
        """
        pass
