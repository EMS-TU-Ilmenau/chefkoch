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
# built-in functions that can be called as a simulation step inside a node
BUILT_INS = ["collect"]


# classes to put json data into

class Recipe:
    """
    A recipe is the workflow representation of a simulation. It is struktured
    as a list of nodes of class Node. The nodes already contain information
    about the data flow and dependencies in the workflow, so there is not
    explicit representation of edges or dependencies needed.
    """
    nodes = []

    def __init__(self, nodelist):
        self.nodes = nodelist
        # Making sure, that nodelist is a list of type Node
        try:
            emptyNode = Node(
                "nodeName",
                {"i": "input"},
                {"o": "output"},
                "collect")
            self.nodes.append(emptyNode)
            self.nodes.pop()
        except Exception as exc:         # mit Klasse
            raise TypeError("""Class Recipe expects a list to be
                initialised with.""")

    def inputIntegrity(self):
        """
        Tests if there is exactly one incoming edge to every input.
        Warns, if there is no incoming edge. Excludes nodes from recipe,
        that have no incoming edge for a node or have uncomputable inputs
        because of missing inputs in parent nodes.
        Inputs:
             -
        Outputs:
            err         String. None if correct. Else error message.
            warn        String. None if correct. Else error message.
        """
        err = None
        warn = None
        # 1. make unique list of outputs
        outputs_of_all_nodes = []
        for node in self.nodes:
            for key in node.outputs:
                output = node.outputs[key]
                if output in outputs_of_all_nodes:
                    #  ("" if err is None else err) + "bla"
                    # exception überschreiben für warns
                    err = (("" if err is None else err) + 'The output ' +
                           output + ' of node ' + node.name +
                           ' has the same name as an output decalred before. ')
                else:
                    outputs_of_all_nodes.append(output)
        # 2. see if inputs are from flavour, are file paths to existing files
        # or are in output list
        try_again = True
        while try_again:
            unreachable_nodes = []
            for node in self.nodes:
                nodeIsValid = True
                for key in node.inputs:
                    input = node.inputs[key]
                    # to do: Werte direkt zulassen, nicht nur über flavour
                    # WARN schmeißen
                    # python logs verwenden: kein flavour, kein output, also
                    # interpretiert als string
                    # chef analyse (from log)
                    inputIsValid = False
                    if (input in outputs_of_all_nodes or
                            input.startswith('flavour.')):    # use name class
                        inputIsValid = True
                    else:
                        try:                # os.path os.isfile ?
                            with open(input) as f:
                                forget = file.readline(f)
                                inputIsValid = True
                        except IOError:
                            pass
                    if not inputIsValid:
                        nodeIsValid = False
                if not nodeIsValid:
                    unreachable_nodes.append(node)

        # 3. Delete unreachable nodes and unreachable outputs and do it again.
            try_again = (len(unreachable_nodes)>0)
            for node in unreachable_nodes:
                warn = (("" if warn is None else warn) + 'Node ' + node.name +
                        ' or one of its previous nodes has an invalid input' +
                        ' and therefore cannot be computed. ')
                for key in node.outputs:
                    output = node.outputs[key]
                    outputs_of_all_nodes.remove(output)

                # outputs_of_all_nodes.remove(node.outputs.values())
                # # <-- if remove can remove a list of objects
                # keys_to_remove = [val for val in node.outputs.values()
                # if val in output_of_all_nodes]
                # outputs_of_all_nodes = [oo for oo in outputs_of_all_nodes
                # if oo not in node.outputs.values()]
                self.nodes.remove(node)

        # 4. Loop until all nodes are reachable
        return err, warn

    def findCircles(self):
        """
        Makes list of all nodes, that have only flavour parameters as inputs.
        Then starts depth-first search for every root node. If there is a way
        back to a previously visited node, there is a warning about a circle.
        Inputs:
            none
        Outputs:
            err         String about circle or "" if everything is correct
        """
        rootNodes = []
        # 1. Make list of all nodes that only have flavour inputs.
        for node in self.nodes:
            isRootNode = True
            for key in node.inputs:
                input = node.inputs[key]
                if not input.startswith("flavour."):
                    isRootNode = False
                    break
            rootNodes.append(node)

        print("Root Nodes:")
        # 2. Start depth-first-search for every such node.
        for node in rootNodes:
            print(node.name)
            nodesOnTheWay = []
            # do recursive depth-first search
            if self.recursiveDFS(node, nodesOnTheWay):
                return str("The recipe contains a circle reachable from " +
                           node.name)
        return ""

    def recursiveDFS(self, node, nodesOnTheWay):
        """
        Recursive Depth First Search finding circles.
        Inputs:
            node            The node, the DFS starts in.
            nodesOnTheWay   Previously visited nodes. If a node in there can
                            be visited by going deeper into the graph,
                            there is a circle.
        Outputs:
            bool            True if there is a circle. False elsewise.
        """
        namesOnTheWay = ""
        for nodeOTW in nodesOnTheWay:
            namesOnTheWay = namesOnTheWay + " " + nodeOTW.name
        print("Executing rDFS for " + node.name + " and " +
              namesOnTheWay)
        if node in nodesOnTheWay:
            print("circle closed at " + node.name)
            return True # we found a circle
        nodesOnTheWay.append(node)
        # this only gets longer in deeper recursion levels
        # no need to bring nodes from deeper levels up.
        for key in node.outputs:
            output = node.outputs[key]
            # output might be used by several other nodes
            for nextNode in self.nodes:
                # to search for the values in a dict instead of their keys
                # we need to invert it
                invertedInputDict = dict(map(reversed, nextNode.inputs.items()))
                if output in invertedInputDict:
                    print("Taking the edge from " + node.name + " to " +
                          nextNode.name)
                    if self.recursiveDFS(nextNode, nodesOnTheWay):
                        return True # a circle was found
                    # else continue with next node
        # if there is no circle from none of the outputs
        return False


class Node:
    """
    A node encapsules a simulation step within a recipe. The step can
    be realised by a python file, a sub-recipe or a built-in function.
    Each node also has a name, a dict of inputs and a dict of outputs.
    To the inputdict, the key is the same input name that the step takes,
    the value is where the input comes from. To the outputdict, the key
    is the name the step uses, the value is the name under which the
    output is available to other nodes in the recipe (the same name used
    as value in another inputdict).
    """
    def __init__(self, name, inputdict, outputdict, stepsource):
        # testing the name to be a string
        # # todo Do Willi a favor and make name optional except subrecipes
        if not (type(name) == unicode or type(name) == str):
            # todo: checken, wie das in python gemacht werden sollte
            # (python 2/3, unicode checks, ...). `six` kümmert sich um
            # solche py2/3 kompatibilitäts-Geschichten und bietet für
            # viele Fälle checks an
            raise TypeError('The name of a node must be a string.')
            # todo: lass den check die Name-Klasse machen, am Besten
            # auch mit Prüfung, dass Namen nur aus einem engen
            # Characterset kommen dürfen
            return
        self.name = name
        # testing the input to be delivered in a dict
        if not (type(inputdict) == dict):
            # todo: 'if inputdict is not dict', allerdings auch
            # problematisch weil das keine Vererbung erkennt.
            # Besser: isinstance(inputdict, dict), um auch vererbte
            # Dictionaries erkennen zu können
            raise TypeError('The input of node ' + str(name) +
                            ' must be of the format {\"name as in ' +
                            'step\": value, ...}')
            return
        self.inputs = inputdict
        # todo replace strings by values in flavour?
        # testing the output to be delivered in a dict
        if not (type(outputdict) == dict):
            raise TypeError('The output of node ' + str(name) +
                            ' must be of the format {\"name as in ' +
                            'step\": value, ...}')
            return
        self.outputs = outputdict
        # testing if step is built-in or python function
        if str(stepsource).endswith(".py"):
            self.step = stepsource
            # todo asign a function as attribute (so that it can be
            # accessed no matter where the object is used)
        elif str(stepsource).endswith(".json"):
            # todo: os.path.splitext(filename)[:-1]
            self.step = stepsource
        elif str(stepsource) in BUILT_INS:
            self.step = stepsource
        else:
            raise TypeError('Stepsource to node ' + str(name) +
                            ': ' + str(stepsource) +
                            '. Must be a Python file, another recipe ' +
                            'or a build-in function.')


def readjson(filename):
    """
    Opens a JSON file and parses it into a recipe object. Then outputs
    the data inside the recipe.
    Inputs:
        filename    string
    Outputs:
        None
    """
    jsonData, err = openjson(filename)
    if err is not None:
        print(err)
        return
    recipe, err = jsonToRecipe(jsonData)
    if err is not None:
        print(err)
        return
    printRecipe(recipe)
    recipe.inputIntegrity()


def openjson(filename):
    # todo also work with strings as input
    """
    Opens a JSON file, makes sure it is valid JSON and the file exists
    at the given path.
    Inputs:
        filename    string
    Outputs:
        data        dict or list depending on JSON structure
        err         Error message string, None if everything worked fine
    """
    try:
        f = open(filename, 'r')
        data = json.load(f)
        # That's the whole file at once. Hope files dont get too big
        f.close()
    except IOError as err:
        # TODO somehow this does not catch a file does not exist error
        return (None, "The file path or file name is incorrect.")
    except ValueError as err:
        return (None, "This is no valid JSON file. Try deleting comments.")

    return (data, None)


def jsonToRecipe(data):
    """
    Takes a dictionary or list of interpreted JSON and parses it into an object
    of class Recipe.
    Inputs:
        data        dict or list depending on the outer structure of JSON file
    Outputs:
        recipe      object of class Recipe
        err         Error message string, None if everything worked fine
    """
    if not isinstance(data, dict):
        return (None, 'Function jsonToRecipe expects dictionary as input.')
    recipe = Recipe([])
    for node in data['nodes']:
        try:
            newNode = Node(
                node['name'],
                node['inputs'],
                node['outputs'],
                node['stepsource'])
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
