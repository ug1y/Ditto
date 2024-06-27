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


class NetFilter(logging.Filter):
    def filter(self, record):
        if (record.name == 'ditto.network.netOperator' or record.name == 'ditto.network.netContainer'
                or record.name == 'ditto.blockdag.blockdag') and (record.args[0] == 'network'):
            return True
        else:
            return False


class MinerFilter(logging.Filter):
    def __init__(self, miner_name: str = ""):
        super().__init__()
        self.miner_name = miner_name

    def filter(self, record):
        if (record.name == 'ditto.nodes.miner' or record.name == 'ditto.blockdag.blockdag') \
                and (record.args[0] == self.miner_name):
            return True
        else:
            return False


LOGGER_FILTER = MinerFilter("testMiner1")
LOGGER_LEVEL = logging.DEBUG

logging.basicConfig(level=LOGGER_LEVEL,
                    format='[%(asctime)s] %(levelname)s - '
                           '[Location] %(name)s:%(lineno)d - '
                           '[%(funcName)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def getLogger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.addFilter(LOGGER_FILTER)
    return logger
