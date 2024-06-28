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
from typing import Set, List

from ditto.blockdag import TypeAlias
from ..consusIface import ConsusIface, StatusType


# Test for interface, useless.

class CCC(ConsusIface):

    def get_block_status(self, bid) -> StatusType:
        pass

    def get_decided_blocks(self) -> Set[TypeAlias.BlockID]:
        pass

    def sort_finished_blocks(self, filter_decided: bool = False) -> List[TypeAlias.BlockID]:
        pass
