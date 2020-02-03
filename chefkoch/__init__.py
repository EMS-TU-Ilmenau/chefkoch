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

    def inputIntegrity(self):
        """
        Tests if there is exactly one incoming edge to every input. Warns, if there is no incoming edge. Excludes nodes from recipe, that have no
        incoming edge for a node or have uncomputable inputs because of missing inputs in parent nodes.
        Inputs:
             -
        Outputs:
            err         String. "" if everything was correct. Else error message.
            warn        String. "" if everything was correct. Else error message.
        """
        err = ''
        warn = ''
        # 1. make unique list of outputs
        outputs_of_all_nodes = []
        for node in self.nodes:
            for key in node.outputs:
                output = node.outputs[key]
                if output in outputs_of_all_nodes:
                    err = err + 'The output ' + output + ' of node ' + node.name + ' has the same name as an output decalred before. '
                else:
                    outputs_of_all_nodes.append(output)
        # 2. see if inputs are from flavour, are file paths to existing files or are in output list
        try_again = True
        while try_again == True:
            unreachable_nodes = []    
            for node in self.nodes:
                nodeIsValid = True
                for key in node.inputs:
                    input = node.inputs[key]
                    inputIsValid = False
                    if input in outputs_of_all_nodes or input.startswith('flavour.'):
                        inputIsValid = True
                    else:
                        try:
                            with open(input) as f:
                                forget = file.readline(f)
                                inputIsValid = True
                        except IOError:
                            pass
                    if not inputIsValid:
                        nodeIsValid = False
                if not nodeIsValid:
                    unreachable_nodes.append(node)
                
        # 3. Delete unreachable nodes and unreachable outputs and do it all over again.
            try_again = (len(unreachable_nodes)>0)
            for node in unreachable_nodes:
                warn = warn + 'Node ' + node.name + ' or one of its previous nodes has an invalid input and therefore cannot be computed. '
                for key in node.outputs:
                    output = node.outputs[key]
                    outputs_of_all_nodes.remove(output)
                self.nodes.remove(node)         

        # 4. Loop until all nodes are reachable
        return err, warn




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
    jsonData, err = openjson(filename)
    if err != None:
        print(err)
        return
    recipe, err = jsonToRecipe(jsonData)
    if err != None:
        print(err)
        return
    printRecipe(recipe)
    recipe.inputIntegrity()

def openjson(filename):                   # todo also work with strings as input
    """
    Opens a JSON file, makes sure it is valid JSON and the file exists at the given path.
    Inputs:
        filename    string
    Outputs:
        data        dictionary or list depending on the outer structure of the JSON file
        err         Error message string, None if everything worked fine
    """
    try:
        f = open(filename, 'r')
        data = json.load(f)                 # That's the whole file at once. Hope files dont get too big
        f.close()
    except IOError as err:                         # TODO somehow this does not catch a file does not exist error
        return (None, "The file path or file name is incorrect.")      
    except ValueError as err:
        return (None, "This is no valid JSON file. Try deleting comments.")

    return (data, None)               

def jsonToRecipe(data):
    """
    Takes a dictionary or list of interpreted JSON and parses it into an object of class Recipe.
    Inputs:
        data        dictionary or list depending on the outer structure of the JSON file
    Outputs:
        recipe      object of class Recipe
        err         Error message string, None if everything worked fine
    """
    if not isinstance(data, dict):
        return (None, 'Function jsonToRecipe expects dictionary as input.')
    recipe = Recipe([])                     # Do not initialise with None because None has no type and therefore no append
        
    for node in data['nodes']:
        try:
            newNode = Node(node['name'], node['inputs'], node['outputs'], node['stepsource'])
            recipe.nodes.append(newNode)
        except TypeError as errorMessage:
            return (None, errorMessage)
        except Exception as err:
           return (None, 'An error occured.')

    return (recipe, None)

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
