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
Introduction
------------

Please tune in soon for an update.
"""
import os
import io
import platform
import json
# import xxhash

# define package version (gets overwritten by setup script)
from .version import __version__ as version

# classes to put json data into

class Recipe:

    def __init__(self, nodelist):
        # todo make sure, that nodelist is a list of type Node
        self.nodes = nodelist

class Node:
    
    def __init__(self, name, inputdict, outputdict, stepsource):
        self.name = name                    # todo make sure to be a string
        self.inputs = inputdict             # todo make sure to be a dict; replace strings by values in flavour?
        self.outputs = outputdict           # todo make sure to be dict
        self.step = stepsource              # todo make switch-case and asign a function as attribute (so that it can be accessed no matter where the object is used)
#        if stepsource ends with .py
#            self.step = stepsource 
#        elif stepsource == "collect"
#            self.step = chef.collect
#        elif stepsource ends with .json
#            self.step = drösel recipe auf
        
def readjson(filename): 
    """
    Opens a JSON file and parses it into a recipe object. Then outputs the data inside the recipe.
    """
    with open(filename, 'r') as f:
        data = json.load(f)                 # That's the whole file at once. Hope files dont get too big

    recipe = Recipe([])                     # Do not initialise with None because None has no type and therefore no append
    for node in data['nodes']:
        newNode = Node(node['name'], node['inputs'], node['outputs'], node['stepsource'])
        recipe.nodes.append(newNode)

    print(recipe.nodes)
    for node in recipe.nodes:
        print("Nodename:")
        print("  " + str(node.name))        
        print("Inputs:")
        for input in node.inputs:
            print("  " + input + "\t" + str(node.inputs[input]))
        print("Outputs:")
        for output in node.outputs:
            print("  " + output + "\t" + str(node.outputs[output]))
        print("Executes:")
        print("  " + str(node.step))
        print("\n")
