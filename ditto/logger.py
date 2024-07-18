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


class NothingFilter(logging.Filter):
    def filter(self, record):
        return True


class SimulatorFilter(logging.Filter):
    def filter(self, record):
        if record.name in {'ditto.simulation.simulator'}:
            return True
        else:
            return False


class NetworkFilter(logging.Filter):
    def filter(self, record):
        if (record.name in {'ditto.network.netOperator', 'ditto.network.netContainer', 'ditto.blockdag.blockdag'}) \
                and (record.args[0] == 'network'):
            return True
        else:
            return False


class MinerFilter(logging.Filter):
    def __init__(self, miner_name: str = ""):
        super().__init__()
        self.miner_name = miner_name

    def filter(self, record):
        if record.name in {'ditto.nodes.miner', 'ditto.blockdag.blockdag'} \
                and (self.miner_name in record.args):
            return True
        else:
            return False


class Logger:
    LOGGER_FILTER = NothingFilter()
    LOGGER_LEVEL = logging.INFO
    LOGGER_HANDLE = None
    LOGGER_FORMAT = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s')

    # logging.basicConfig(format='[%(asctime)s] %(levelname)s - '
    #                            '[Location] %(name)s:%(lineno)d - '
    #                            '[%(funcName)s] %(message)s',
    #                     datefmt='%Y-%m-%d %H:%M:%S')

    def __init__(self, name: str):
        self._logger = logging.getLogger(name)
        if Logger.LOGGER_HANDLE is not None:
            self._console = Logger.LOGGER_HANDLE
            self._console.setFormatter(Logger.LOGGER_FORMAT)
            self._logger.addHandler(self._console)

    def getLogger(self) -> logging.Logger:
        self._logger.setLevel(Logger.LOGGER_LEVEL)
        self._logger.addFilter(Logger.LOGGER_FILTER)

        return self._logger
