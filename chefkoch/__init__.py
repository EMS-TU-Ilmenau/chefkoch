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

# constants
# build-in functions that can be called as a simulation step inside a node
BUILD_INS = ["collect"]


# classes to put json data into

class Recipe:
    """
    A recipe is the workflow representation of a simulation. It is struktured as a list of nodes of class Node. The nodes already contain information
    about the data flow and dependencies in the workflow, so there is not explicit representation of edges or dependencies needed.
    """
    nodes = []
    def __init__(self, nodelist):
        self.nodes = nodelist
        # Making sure, that nodelist is a list of type Node
        try:
            emptyNode = Node("nodeName", {"i": "input"}, {"o": "output"}, "collect")
            self.nodes.append(emptyNode)
            self.nodes.pop()
        except:
            raise TypeError("Class Recipe expects a list to be initialised with.")

class Node:
    """
    A node encapsules a simulation step within a recipe. The step can be realised by a python file, a sub-recipe or a build-in function.
    Each node also has a name, a dict of inputs and a dict of outputs. To the inputdict, the key is the same input name that the step takes, 
    the value is where the input comes from. To the outputdict, the key is the name the step uses, the value is the name under which the
    output is available to other nodes in the recipe (the same name used as value in another inputdict).
    """
    def __init__(self, name, inputdict, outputdict, stepsource):
        # testing the name to be a string              # todo Do Willi a favor and make name optional for everything but subrecipes
        if not (type(name) == unicode or type(name) == str):
            raise TypeError('The name of a node must be a string.')
            return
        self.name = name               
        # testing the input to be delivered in a dict
        if not (type(inputdict) == dict):
            raise TypeError('The input of node ' + str(name) + ' must be of the format {\"name as in step\": value, ...}')
            return
        self.inputs = inputdict                         # todo replace strings by values in flavour?
        # testing the output to be delivered in a dict
        if not (type(outputdict) == dict):
            raise TypeError('The output of node ' + str(name) + ' must be of the format {\"name as in step\": value, ...}')
            return
        self.outputs = outputdict           
        # testing if step is build-in or python function
        if str(stepsource).endswith(".py"):
            self.step = stepsource                      # todo asign a function as attribute (so that it can be accessed no matter where the object is used)
        elif str(stepsource).endswith(".json"):
            self.step = stepsource
        elif str(stepsource) in BUILD_INS:
            self.step = stepsource
        else:
            raise TypeError('Stepsource to node ' + str(name) + ': ' + str(stepsource) + '. Must be a Python file, another recipe or a build-in function.')
        

def readjson(filename): 
    """
    Opens a JSON file and parses it into a recipe object. Then outputs the data inside the recipe.
    Inputs:
        filename    string
    Outputs:
        None
    """
    jsonData = openjson(filename)
    recipe = jsonToRecipe(jsonData)
    printRecipe(recipe)

def openjson(filename):
    """
    Opens a JSON file, makes sure it is valid JSON and the file exists at the given path.
    Inputs:
        filename    string
    Outputs:
        data        dictionary or list depending on the outer structure of the JSON file
    """
    try:
        f = open(filename, 'r')
        data = json.load(f)                 # That's the whole file at once. Hope files dont get too big
        print(data)
        f.close()
    except IOError:                         # TODO somehow this does not catch a file does not exist error
       print("The file path or file name is incorrect.")
       return
    except ValueError:
       print("This is no valid JSON file. Try deleting comments.")
       return

    return data               

def jsonToRecipe(data):
    """
    Takes a dictionary or list of interpreted JSON and parses it into an object of class Recipe.
    Inputs:
        data        dictionary or list depending on the outer structure of the JSON file
    Outputs:
        recipe      object of class Recipe
    """
    recipe = Recipe([])                     # Do not initialise with None because None has no type and therefore no append
    for node in data['nodes']:
        try:
            newNode = Node(node['name'], node['inputs'], node['outputs'], node['stepsource'])
            recipe.nodes.append(newNode)
        except TypeError as errorMessage:
            print(errorMessage)
            return
        except:
            pass
            return

    return recipe

def printRecipe(recipe):
    """
    Prints the information held inside a Recipe object.
    Inputs:
        recipe      object of class Recipe
    Outputs:
        console output
    """
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
