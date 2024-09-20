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
import uuid


class NothingFilter(logging.Filter):
    def filter(self, record):
        return True


class SimulatorFilter(logging.Filter):
    def filter(self, record):
        if record.args[0] == 'simulator':
            return True
        else:
            return False


class NetworkFilter(logging.Filter):
    def filter(self, record):
        if record.args[0] == 'network':
            return True
        else:
            return False


class MinerFilter(logging.Filter):
    def __init__(self, miner_name: str = ""):
        super().__init__()
        self.miner_name = miner_name

    def filter(self, record):
        if record.args[0] == self.miner_name:
            return True
        else:
            return False


def create_logger(log_handler: logging.Handler = logging.StreamHandler(),
                  log_filter: logging.Filter = SimulatorFilter(),
                  log_level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(str(uuid.uuid4()))
    log_handler.setFormatter(logging.Formatter(fmt='[%(levelname)s] %(message)s'))
    logger.addHandler(log_handler)
    logger.addFilter(log_filter)
    logger.setLevel(log_level)
    return logger
