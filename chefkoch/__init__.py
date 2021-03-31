#!/usr/bin/env python
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
# any time you change the init, make sure to re-install the chef command
# with pip

r"""
Introduction
============

Chefkoch is currently under development. The tool is aiming to help with
structuring simulation code. Chefkoch takes a "recipe" and a "flavour"
file. The recipe is the general workflow of the simulation. It
contains simulation steps and the dependencies between the steps. The
flavour file holds possible parameter sets to execute the simulation with.
Chefkoch takes care of the execution of the simulations with all parameters
and of saving the results consistently.

Read about the general design of chefkoch in our :ref:`architecture` section.
A detailed descriptions of the classes will soon appear in out :ref:`classes`
section.
"""

import os
import io
import platform
import json

# import xxhash
import sys

from .recipe import *

# define package version (gets overwritten by setup script)
from .version import __version__ as version

from .core import Chefkoch
