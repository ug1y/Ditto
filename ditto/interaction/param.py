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
from dataclasses import dataclass

from bokeh.models import TextAreaInput


class ConsoleHandler(logging.Handler):
    def __init__(self, console: TextAreaInput):
        super().__init__()
        self._console = console

    def emit(self, record: logging.LogRecord) -> None:
        self._console.value = self.format(record) + "\n" + self._console.value


@dataclass
class ParamsConfig:
    file_name: str
    file_path: str
    miner_num: int
    block_rate: float
    prop_delay: float


SystemRef = {
    'Nakamoto': ParamsConfig(file_name='2008_Bitcoin', file_path='interaction/static/papers/2008_Bitcoin.pdf',
                            miner_num=6, block_rate=10.0, prop_delay=10.0),
    'Phantom': ParamsConfig(file_name='2021_Phantom', file_path='interaction/static/papers/2021_Phantom.pdf',
                            miner_num=6, block_rate=10.0, prop_delay=30.0),
    'ULBlockDAG': ParamsConfig(file_name='2020_ULBlockDAG', file_path='interaction/static/papers/2020_ULBlockDAG.pdf',
                               miner_num=6, block_rate=10.0, prop_delay=30.0),
    'Pikavolt': ParamsConfig(file_name='2024_Pikavolt', file_path='interaction/static/papers/2024_Pikavolt.htm',
                             miner_num=6, block_rate=10.0, prop_delay=30.0),
}
