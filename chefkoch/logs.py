# -*- coding: utf-8 -*-
# Copyright 2019 Christoph Wagner
#     https://www.tu-ilmenau.de/it-ems/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

r"""
Settings for logging in whole project. Include with

`from logs import *`

so that the code is copied into each module and the __name__ variable
references the module name. This way, each module has it's own logger.
Using the normal import would set __name__ to "logs" each time.
Having seperate loggers for each submodule enables to set for
example different logging levels for each module and other explicit
settings.
"""
import logging
import warnings

logging.captureWarnings(True)
warnings.filterwarnings("always", category=UserWarning)
# Set up logging for everything inside this module
logger = logging.getLogger("py.warnings")
# this is important when importing modules
# a logger can only be configured once within a project
# so we need a new logger in each module
# __name__ is either "main" or the name of the module if imported
logger.setLevel(logging.INFO)
# log levels are ascending: debug, info, warn, err, crit
# setting lvl to debug basically says log everything
# logging.basicConfig configues the root Looger. Never share root Logger.

formatter = logging.Formatter(
    "%(levelname)s:%(asctime)s:%(lineno)d:%(message)s"
)

file_handler = logging.FileHandler("test.log")
file_handler.setLevel(logging.ERROR)  # only write logs that are error or worse
file_handler.setFormatter(formatter)

#warn_handler = logging.captureWarnings(True)

# to output errs and warns into file, but debug to console, do:
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
# no lvl specified -> print every log to console

logger.addHandler(file_handler)
logger.addHandler(stream_handler)
#logger.addHandler(warn_handler)

# Integrating warning.warn to automatically log raised warnings
logging.captureWarnings(True)