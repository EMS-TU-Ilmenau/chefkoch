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
The recipe file entered by the user declares all the steps taken in the
simulation and the dependencies in form of exchanged data
between the steps. The Recipe module holds all classes and functions
needed to parse a YAML file into a recipe object and check integrity.
"""


from __future__ import unicode_literals
import os
import io
import platform
import json
import sys
import warnings
from graph import Graph

from chefkoch.container import YAMLContainer, JSONContainer

# logs need to be imported this way to not write logs.logger all the time
from .logs import *


# constants
# built-in functions that can be called as a simulation step inside a node
BUILT_INS = ["collect"]


class Plan:
    """

    """

    nodes = []
    constructiontree = {}
    required = []
    remaining = []
    targets = []

    def __init__(self, recipe, *targets):
        """
        Initialize Plan Object over a given recipe and calculation targets
        :param recipe: recipe object
        :param targets: calculation targets given as string (name of the node),
                        int (list index of the node in recipe object)
                        or node object
        """
        # targets = []
        self.recipe = recipe
        if len(targets) == 0:
            self.nodes = recipe
        else:
            self.targets.append(targets)
            for target in targets:
                if type(target) == str or type(target) == int:
                    targetnode = recipe[target]
                elif type(target) == Node:
                    targetnode = target
                self.constructiontree[targetnode.name] = \
                    self.createConstructionTree(
                    recipe, target
                )
        for node in self.nodes:
            # for i in range(len(node.inputs)):
            #     inputKey, inputValue = node.inputs
            for inputValue in node.inputs.values():
                if inputValue not in self.required:
                    self.required.append(inputValue)
        self.remaining = self.required.copy()
# self.requi()
####################################################

    # def createConstructionTree(self, recipe, target):
    #     """
    #     build recursively a construction tree based on a recipe and a target
    #     :param recipe:
    #     :param target: calculation target given as string (name of the node),
    #                     int (list index of the node in recipe object)
    #                     or node object
    #     :return:
    #     """
    #     tree = {}
    #     if type(target) == str or type(target) == int:
    #         node = recipe[target]
    #     elif type(target) == Node:
    #         node = target
    #     for inputKey, inputValue in node.inputs.items():
    #         children = recipe.inputIsOutput(inputValue)
    #         for child in children:
    #             if child.name in self.targets:
    #                 self.targets.remove(child.name)
    #             if child.name not in self.constructiontree.keys():
    #                 tree[child.name] = self.createConstructionTree(
    #                     recipe, child
    #                 )
    #             else:
    #                 tree[child.name] = self.constructiontree[child.name]
    #                 self.constructiontree.pop(child.name)
    #     if node not in self.nodes:
    #         self.nodes.append(node)
    #     return tree

    # def requi(self):
    #     for root in self.constructiontree.values():
    #         # print(root)
    #         self.buildNodes(root)
    #         self.required.append(self.recipe[root.key])
    #
    # def buildNodes(self, node):
    #     print(type(node))
    #     print(node)
    #     if node.values:
    #         for value in node.values():
    #             self.buildNodes(value)
    #             print("build " + value.keys())
    #             self.required.append(self.recipe[value.keys()])
    #     else:
    #         self.required.append(self.recipe[node.keys()])
    #         print("test " + node.key())


class Recipe:
    """
    A recipe is the workflow representation of a simulation. It is struktured
    as a list of nodes of class Node. The nodes already contain information
    about the data flow and dependencies in the workflow, so there is not
    explicit representation of edges or dependencies needed.
    """

    nodes = []

    def __init__(self, nodelist):
        """
        Initialises a recipe by appending the `nodelist` to `nodes`.

        Parameters
        ------------
        nodelist (Node[]):
            list of simulation steps as Node[]
        """
        self.nodes = nodelist
        self.graph = Graph()
        self.makeGraph()
        # TODO: Making sure, that nodelist is a list of type Node
        # TODO: Therefore initialise each Node in nodelist as an
        # instance of class Node.

    def __getitem__(self, item):
        """

        :param item:
        :return:
        """
        if type(item) == int:
            return self.nodes[item]
        if type(item) == str:
            for node in self.nodes:
                if node.name == item:
                    return node
#########################

    def getPrerequisits(self, item):
        """
        Returns all nodes required to calculate a given item of the recipe
        :param item:
        :return: List of nodes
        """
        ret = []
        for inputKey, inputValue in (
            self[item].inputs.items()
            if type(item) == int else item.inputs.items()
        ):
            prerequisites = self.inputIsOutput(inputValue)
            if len(prerequisites) > 0:
                ret.extend(prerequisites)
                for i in prerequisites:
                    # print("i is: ")
                    # print(i.name)
                    ret.extend(self.getPrerequisits(i))
        return ret
##################################

    def inputIsOutput(self, input):
        """
        Checks if given input is also output of other nodes and returns them
        :param input: name of the ipnut
        :return: list of nodes
        """
        ret = []
        for node in self.nodes:
            for outputKey, outputValue in node.outputs.items():
                if input == outputValue:
                    if node not in ret:
                        ret.append(node)
        return ret
##################################

    def inputIsValid(self, input):
        """
        Checks if a given input name is valid. An input is valid if it
        can be found either in the flavour file or is a file itself.
        It is also valid if it is an output name of another node, but this
        will not be checked.

        Parameters
        ----------
        input (str):
            The input that is to be tested

        Returns
        -------
        True if the input is valid.
        """
        if os.path.isfile(input):
            return True
        prefix = os.path.splitext(input)[0]
        if prefix == "flavour":
            return True
        else:
            return False

    def inputIntegrity(self):
        """
        Tests if there is exactly one incoming edge to every input.
        Warns, if there is no incoming edge. Excludes nodes from recipe,
        that have no incoming edge for a node or have uncomputable inputs
        because of missing inputs in parent nodes.

        Raises
        -------
        NameError:
            If two or more outputs share the same name.
        """
        # 1. make unique list of outputs
        outputs_of_all_nodes = set([])
        for node in self.nodes:
            node_outputs = set(node.outputs.values())
            # & is the intersection of sets
            if len(node_outputs & outputs_of_all_nodes) > 0:
                raise NameError(
                    "The output "
                    + str(node_outputs & outputs_of_all_nodes)
                    + " of node "
                    + node.name
                    + " has the same name as an output declared before. "
                )
            else:
                outputs_of_all_nodes.update(node_outputs)
        # 2. see if inputs are from flavour, are file paths to existing files
        # or are in output list
        try_again = True
        while try_again:
            unreachable_nodes = set([])
            for node in self.nodes:
                nodeIsValid = True
                node_inputs = set(node.inputs.values())
                for input in node_inputs.difference(outputs_of_all_nodes):
                    if not self.inputIsValid(input):
                        nodeIsValid = False
                if not nodeIsValid:
                    unreachable_nodes.add(node)
            # 3. Delete unreachable nodes and unreachable outputs and do
            # it again.
            try_again = len(unreachable_nodes) > 0
            for node in unreachable_nodes:
                warnings.warn(
                    "Node "
                    + node.name
                    + " or one of its previous nodes has an invalid input"
                    + " and therefore cannot be computed. "
                )
                node_outputs = set(node.outputs.values())
                outputs_of_all_nodes.difference_update(node_outputs)
                self.nodes.remove(node)

        # 4. Loop until all nodes are reachable
        return None, None
########################

    def makeGraph(self):
        """

        :param dict:
        :return:
        """
        for node in self.nodes:
            print("adding node: " + node.name)
            self.graph.add_node(node.name, node)
            for input in node.inputs.values():
                if "item." + input not in self.graph:
                    print("adding input: " + "item." + input)
                    self.graph.add_node("item." + input)
                self.graph.add_edge("item." + input, node.name)
            for output in node.outputs.values():
                if "item." + output not in self.graph:
                    print("adding output: " + "item." + output)
                    self.graph.add_node("item." + output)
                self.graph.add_edge(node.name, "item." + output)

        print(self.graph.to_dict())


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

    def __init__(self, name, inputdict, outputdict, stepsource, steptype):
        """
        Initializes a node of the recipe. A node represents a simulation
        step.

        Parameters
        ----------
        name (str):
            Name of the simulation step.
        inputdict (dict):
            Dictionary of all inputs needed to execute this step.
        outputdict (dict):
            Dictionary of all outputs of the simulation step.
        stepsource (str):
            Information on how to execute this step.

        Raises
        ------
        TypeError:
            If the input or output of a node are not given as a dict.
        """
        # for empty name enter "" into recipe
        # unicode and string needed
        try:
            name_obj = Name(name)
            self.name = name_obj.name  # Willi, ist das wirklich so gemeint?
        except TypeError as err:
            pass
        # testing the input to be delivered in a dict
        if not (isinstance(inputdict, dict)):
            raise TypeError(
                "The input of node "
                + str(name)
                + ' must be of the format {"name as in'
                + ' step": value, ...}'
            )
            return
        self.inputs = inputdict
        # later replace strings by values in flavour?
        # testing the output to be delivered in a dict
        if not (type(outputdict) == dict):
            raise TypeError(
                "The output of node "
                + str(name)
                + ' must be of the format {"name as in '
                + 'step": value, ...}'
            )
            return
        self.outputs = outputdict
        # step_obj = StepSource(stepsource)
        self.step = stepsource
        self.type = steptype
        # todo abort in higher level and ignore whole node


class Name:
    """
    Name convention for the name of a node inside the recipe.
    """

    def __init__(self, name):
        """
        Takes a string or unicode and saves it if it is pure ascii.

        Parameters
        ----------
        name (str or unicode):
            Name to be checked and saved

        Raises
        ------
        TypeError:
            If `name` is has another type.
        ValueError:
            If `name` contains non-ascii characters.
        """
        is_unicode = False
        try:
            is_unicode = isinstance(name, unicode)
        except NameError as mimimi:
            logger.debug(mimimi)
            logger.debug("You are using python 3, "
                         "but don't worry, we make it work.")
            pass
        if not (isinstance(name, str) or is_unicode):
            raise TypeError("The name of a node must be a string.")
        if not self.is_ascii(name):
            raise ValueError("The name of a node must be ascii.")
        self.name = name

    def is_ascii(self, name):
        """
        Checks if string consists of only ascii characters.

        Parameters
        ----------
        name (str or unicode):
            string

        Returns
        -------
        `True`, if name only contains ascii characters.
        """
        return all(ord(c) < 128 for c in name)


# class StepSource:
#     """
#     Specifies the function to be executed inside a node in the recipe.
#     """
#
#     def __init__(self, stepsource):
#         """
#         Tests the step source if it is a recipe, a python executable or
#         a built-in function and initialises it if so.
#
#         Parameters
#         ----------
#         stepsource (str):
#             file path to a sub-recipe, a python executable or the name \
#             of a built-in function
#
#         Raises
#         ------
#         TypeError:
#             If the string does not match any of the above.
#         """
#         # testing if step is built-in; JSON file or python function
#         extension = os.path.splitext(stepsource)[1]
#         if extension == ".py":
#             self.step = stepsource
#         elif extension == ".json":
#             self.step = stepsource
#         elif str(stepsource) in BUILT_INS:
#             self.step = stepsource
#             # done: research on assigning functions as attributes
#             # (so that it can be accessed no matter where the object
#             # is used)
#         else:
#             raise TypeError(
#                 "Stepsource : "
#                 + str(stepsource)
#                 + ". Must be a Python file, another recipe "
#                 + "or a build-in function."
#             )


def readrecipe(dict):
    """
    Opens a YAML file and parses it into a recipe object. Then outputs
    the data inside the recipe.

    Parameters
    ----------
    filename (str):
        file path

    Returns
    -------
    Object of class Recipe
    :rtype: Recipe
    """

    recipe = dictToRecipe(dict)
    recipe.inputIntegrity()
    recipe.makeGraph()
    if recipe.graph.has_cycles():
        raise Exception("There is a Cycle in your recipe, please check")
    # recipe.findCircles()
    # printRecipe(recipe)
    return recipe


# def readflavour(filename):
#     """
#     Opens a YAML file and parses it into a flavour object. Then outputs
#     the data inside the flavour file.
#
#     Parameters
#     ----------
#     filename (str):
#         file path
#
#     Returns
#     --------
#     flavour - object of type flavour.
#     :rtype: Flavour
#     """
#     data = {}
#     type = filename[-4:]
#     if type == "yaml":
#         data = openyaml(filename)
#     flavour = dictToFlavour(data)
#     print(flavour.tostring())
#     # todo: input Integrity checks
#     return flavour


# def openyaml(filename): #containern
#     """
#     Opens a YAML file, makes sure it is valid YAML and the file exists
#     at the given path. Loads the whole file at once. File should there-
#     fore not be too big.
#
#     Parameters
#     ----------
#     filename (str):
#         file path
#
#     Returns
#     --------
#     data - dict or list depending on YAML structure
#
#     Raises
#     ------
#     IOError:
#         If the file path or file name are incorrect.
#     ValueError:
#         If the given file is no valid YAML format.
#     """
#     if not os.path.isfile(filename):
#         raise IOError("The file path or file name is incorrect.")
#     with open(filename) as f:
#         try:
#             data = yaml.load(f, Loader=yaml.SafeLoader)
#             # That's the whole file at once. Hope files dont get too big
#         except ValueError as err:
#             raise ValueError("This is no valid YAML file.")
#
#     return data


def dictToRecipe(data):
    """
    Takes a dictionary or list of interpreted YAML
    and parses it into an object of class Recipe.

    Parameters
    ----------
    data (dict or list):
        dict or list depending on the outer structure of YAML file

    Returns
    -------
    recipe - object of class Recipe \n
    :rtype: Recipe

    Raises
    -------
    TypeError:
        If data ist not of type dictionary.
    Exception:
        Error while parsing YAML data into recipe object.
    """
    if not isinstance(data, dict) and \
            not isinstance(data, YAMLContainer) and \
            not isinstance(data, JSONContainer):
        raise TypeError("Function dictToRecipe expects dictionary as input.")
    recipe = Recipe([])
    for node in data.items(): #["nodes"]:
        # print("node: ", node[0], node[1], " ", type(node[0]), len(node)) #, node.inputs, node.outputs)
        try:
            newNode = Node(
                node[0], node[1]["inputs"],
                node[1]["outputs"], node[1]["resource"],
                node[1]["type"]
            )
            recipe.nodes.append(newNode)
        except KeyError as err:
            raise KeyError("Error while parsing data into recipe object.")

    return recipe


def printRecipe(recipe):
    """
    Prints the information held inside a Recipe object to the console.

    Parameters
    ----------
    recipe (Recipe):
        object of class Recipe
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


# called by typing "chef read /file/path/.."
# def readfile(type, filename):
#     """
#     Wrapper function that calls either `readrecipe` or `readflavour`
#     depending on the parameter `type`.
#
#     Parameters
#     ----------
#     type (str):
#         Type of YAML file that should be converted into a \
#         dictionary: {"recipe", "flavour"}
#
#     Returns
#     -------
#     Recipe or Flavour object depending on the `type` parameter.
#
#     Raises
#     ------
#     TypeError:
#         If type is none of the above.
#
#     """
#     if type == "recipe":
#         return readrecipe(filename)
#     if type == "flavour":
#         return readflavour(filename)
#     else:
#         raise TypeError(
#             "The function readyaml only takes
#             'recipe' or" + "'flavour' as type."
#         )
#

# def readyaml(type, filename):
#     """
#     Wrapper function that calls either `readrecipe` or `readflavour`
#     depending on the parameter `type`.
#
#     Parameters
#     ----------
#     type (str):
#         Type of YAML-file that should be converted into a \
#         dictionary: {"recipe", "flavour"}
#
#     Returns
#     -------
#     Recipe or Flavour object depending on the `type` parameter.
#
#     Raises
#     ------
#     TypeError:
#         If type is none of the above.
#
#     """
#     if type == "recipe":
#         return readrecipe(filename)
#     if type == "flavour":
#         return readflavour(filename)
#     else:
#         raise TypeError(
#             "The function parameter type hase to be 'recipe' or"
#             + "'flavour'."
#         )
