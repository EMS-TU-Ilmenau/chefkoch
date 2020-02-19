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
# any time you change the init, make sure to re-install the chef command with pip

r"""
Introduction
------------

Please tune in soon for an update.
"""

import os
import io
import platform
import json
# import xxhash
import sys
sys.path.append('../chefkoch')
import recipe


# define package version (gets overwritten by setup script)
from .version import __version__ as version

# called by typing "chef read /file/path/.."
def readjson(type, filename):
    if type == "recipe":
        return recipe.readrecipe(filename)
    if type == "flavour":
        return recipe.readflavour(filename)