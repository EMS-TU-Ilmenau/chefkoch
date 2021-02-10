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
import itertools
import hashlib
import copy
from graph import Graph
from collections import ChainMap

import chefkoch.fridge

from chefkoch.container import YAMLContainer, JSONContainer

# logs need to be imported this way to not write logs.logger all the time
# from .logs import *


# constants
# built-in functions that can be called as a simulation step inside a node
BUILT_INS = ["collect"]


class ResultItem:
    def __init__(self, step, JsonContainer):
        self.step = step
        self.JsonContainer = JsonContainer

    def execute(self):
        pass


class Plan:
    """"""

    nodes = []
    items = []
    # constructiontree = {}
    # required = []
    # remaining = []
    # targets = []

    def __init__(self, recipe, *targets, fridge=None):
        """
        Initialize Plan Object over a given recipe and calculation targets
        :param recipe: recipe object
        :param targets: calculation targets given as string (name of the node),
                        int (list index of the node in recipe object)
                        or node object
        """
        # targets = []
        # self.recipe = recipe
        # self.subGraph = Graph()
        self.nodelist = []
        self.flavours = {}
        self.variants = JSONContainer()
        # self.variants["test"] = "12345"
        if fridge is not None:
            self.fridge = fridge

        if len(targets) == 0:
            targets = self.fillTargets(recipe)

        for target in targets:
            if target[:4] != "item":
                for targetitem in recipe.graph.nodes(from_node=target):
                    self.nodelist.extend(
                        self.getSubGraphNodes(recipe, targetitem)
                    )
            else:
                self.nodelist.extend(self.getSubGraphNodes(recipe, target))
        # print(nodelist)
        self.subGraph = recipe.graph.subgraph_from_nodes(self.nodelist)
        for node in self.nodelist:
            if node[:4] == "item":
                # print(type(node))
                self.items.append(node[5:])
            else:
                # print(type(node))
                self.nodes.append(node)

        if fridge is not None:
            # self.planIt()
            self.getFlavours()
        self.makeNormalGraph()

        self.startingItems = list(
            x[5:] for x in self.subGraph.nodes(in_degree=0)
        )

        # test = self.crossLists(([1,2,3,4], [5, 6, 7, 8]
        # , ["a", "b", "c", "d"]))
        # test2 = list(itertools.product(*[[1,2,3,4]
        # , [5, 6, 7, 8], ["a", "b", "c", "d"]]))
        # for el in test2:
        #     print(el)
        # pass
        for node in self.graph.nodes(out_degree=0):
            self.buildVariants(node)
        # self.variants = [JSONContainer()]
        print(None)

    def isItemNode(self, node):
        """
        Checks if a node has the prefix "item."
        """
        if node[0:5] == "item.":
            return True
        else:
            return False

    def makeNormalGraph(self):
        """
        Removes Itemnodes from self.subgraph and directly connects the
        surrounding nodes producing the self.graph object
        """
        self.graph = copy.deepcopy(self.subGraph)
        for node in self.graph.nodes():
            if self.isItemNode(node):
                ends = self.graph.nodes(from_node=node)
                starts = self.graph.nodes(to_node=node)
                for x in starts:
                    for y in ends:
                        self.graph.add_edge(x, y)
                self.graph.del_node(node)

    def buildVariants(self, node):
        children = self.graph.nodes(to_node=node)

        if len(children) > 0:  # and len(self.variants) > 0:
            if node not in self.variants:
                childs = {}  # inputs in form of child nodes
                inputs = {}  # direct inputs from resources/flavours
                ret = {}
                for child in children:
                    self.buildVariants(child)
                    # if child in self.variants:
                    # inputs[child] = self.variants[child]
                    childs[child] = list(
                        child + "/" + str(x) for x in self.variants[child]
                    )
                for input in self.graph.node(node).inputs.values():
                    if input in self.flavours.keys():
                        inputs[input] = {
                            x: None for x in self.flavours[input].items
                        }
                    elif input in self.startingItems:
                        inputs[input] = ["self"]
                # g = inputs + childs
                # h = list(inputs.values())
                # h. append(*list(childs.values()))
                accordance = self.checkAccordance(childs, list(inputs))
                accorded = {}
                if len(accordance) > 0:
                    for accordanceKey in accordance.keys():
                        accorded[accordanceKey] = self.matchInputs(
                            accordanceKey,
                            self.variants,
                            accordance[accordanceKey],
                        )
                else:
                    inputs.update(childs)
                # inputs.update(childs)

                if str(node) == "anotherStep":
                    print("anotherStep")
                for input in accorded:
                    for inputValue in accorded[input]:
                        inputs[input][inputValue] = {}
                crossed = list(itertools.product(*list(inputs.values())))
                # crossed.append()
                for c in crossed:
                    k = tuple(inputs.keys())
                    ret[hash((k, c))] = [{k[i]: c[i]} for i in range(len(k))]
                for item in ret.items():
                    # for
                    # for i in range(len(item)):
                    # print()
                    # for input in item.items():
                    # if inputKey
                    for child in children:
                        for variant in self.variants[child].items():
                            if variant[1] == item[1]:
                                ret[item[0]].append(
                                    {child: child + "/" + str(variant[0])}
                                )
                                break
                self.reHash(ret)
                self.variants[node] = ret

                # print(inputs)
        elif len(children) == 0:
            # self.variants[node] = self.flavours[node].items
            inputs = {}
            ret = {}
            # a = self.graph.node(node)
            for input in self.graph.node(node).inputs.values():
                if input in self.flavours:
                    inputs[input] = self.flavours[input].items
                else:
                    inputs[input] = ["self"]
            crossed = list(itertools.product(*list(inputs.values())))
            for c in crossed:
                k = tuple(inputs.keys())
                ret[hash((k, c))] = [{k[i]: c[i]} for i in range(len(k))]
            self.variants[node] = ret
            pass

    def reHash(self, dict):
        ret = {}
        for value in dict.values():
            c = tuple([x.values() for x in value])
            k = tuple(value.keys())
            ret[hash((k, c))] = value
        return ret

    def matchInputs(self, input, data, map):
        """
        Matches the variants of the same inputs from child nodes and direct
        inputs with help of a given map
        """
        ret = {}
        if len(map) > 0:
            for key in map.keys():
                if map[key] == input:
                    for hashkey in data[key]:
                        n = dict(ChainMap(*data[key][hashkey]))
                        if n[input] in ret:
                            ret[n[input]].append(key + "/" + str(hashkey))
                        else:
                            ret[n[input]] = [key + "/" + str(hashkey)]
                        # print(hashkey)
                else:
                    ret = self.matchInputs(input, data[map[key]], map[key])
        return ret

    def checkAccordance(self, childdict, inputlist):
        """
        Checks and maps if the inputs of the children of a
        node and the nodes inputs are matching

        """
        accordance = {}
        for child in list(childdict):
            for input in inputlist:
                if child == input:
                    accordance[child] = child
            x = self.variants[child]
            # z = next(iter(x))
            # y = x[z]
            # if
            if x is not None:
                y = x[next(iter(x))]
                y2 = dict(ChainMap(*y))
                e = self.checkAccordance(y2, inputlist)
                if e != {}:
                    for input in inputlist:
                        if input in e:
                            accordance[input] = {child: e[input]}
        return accordance

    # def crossLists(self, list):
    #     ret = []
    #     if len(list) == 1:
    #         ret.extend(list[0][:])
    #         return ret
    #     # elif len(list) == 2:
    #     #     return [(x, y) for x in list[0] for y in list[1]]
    #     elif len(list) >= 2:
    #         d = list[1:]
    #         z = self.crossLists(d)
    #         ret.extend([(x, y) for x in list[0] for y in z])
    #         return ret

    def getFlavours(self):
        for node in self.nodelist:
            if node[5:] in self.fridge.shelves:
                # print(type(self.fridge.shelves[node[5:]]))
                # x = type(self.fridge.shelves[node[5:]])
                if (
                    type(self.fridge.shelves[node[5:]])
                    == chefkoch.fridge.FlavourShelf
                ):
                    # self.flavours.append(fridge.shelfs[node[5:]])
                    self.flavours[node[5:]] = self.fridge.shelves[node[5:]]
                    self.subGraph.add_node(node, self.fridge.shelves[node[5:]])

    # def planIt(self):
    #     for self.subGraph

    def fillTargets(self, recipe):
        targets = []
        for endnode in recipe.graph.nodes(out_degree=0):
            targets.append(endnode)
        return targets

    def getItems(self):
        """
        Returns every item which is an input or output of a node

        :return: list of String
        """
        return self.items

    def getSubGraphNodes(self, recipe, target):
        """
        Creates a list of nodes needed to calculate the target object

        :param recipe: recipe object
        :param target: string (name of the target node)
        :return: list of nodes
        """
        nodelist = []
        for startingnode in recipe.graph.nodes(in_degree=0):
            print(startingnode, type(startingnode))
            print(recipe.graph.all_paths(startingnode, target))
            for liste in recipe.graph.all_paths(startingnode, target):
                nodelist.extend(liste)
        return nodelist


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

    def getPrerequisits(self, item):
        """
        Returns all nodes required to calculate a given item of the recipe
        :param item:
        :return: List of nodes
        """
        ret = []
        for previousNode in self.graph.nodes(to_node=item):
            ret.append(previousNode)
            ret.append(self.getPrerequisits(previousNode))
        return ret

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
        if len(self.graph.components()) > 1:
            raise ImportError(
                "One or more Nodes are not " "reachable from the others"
            )

        # 4. Loop until all nodes are reachable
        return None, None

    ########################

    def makeGraph(self):
        """
        Builds a Graph according to the recipe nodes saved in self.nodes
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
        # try:
        #     name_obj = Name(name)
        #     self.name = name_obj.name  # Willi, ist das wirklich so gemeint?
        # except TypeError as err:
        #     pass
        # testing the input to be delivered in a dict
        if not (isinstance(inputdict, dict)):
            raise TypeError(
                "The input of node "
                + str(name)
                + ' must be of the format {"name as in'
                + ' step": value, ...}'
            )
            return
        self.name = name
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
            logger.debug(
                "You are using python 3, " "but don't worry, we make it work."
            )
            """
            pass
        if not (isinstance(name, str) or is_unicode):
            raise TypeError("The name of a node must be a string.")
        if not self.is_ascii(name):
            raise ValueError("The name of a node must be ascii.")
        self.name = name"""

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
    recipe.makeGraph()
    if recipe.graph.has_cycles():
        raise Exception("There is a Cycle in your recipe, please check")
    recipe.inputIntegrity()
    # recipe.findCircles()
    # printRecipe(recipe)
    return recipe


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
    if (
        not isinstance(data, dict)
        and not isinstance(data, YAMLContainer)
        and not isinstance(data, JSONContainer)
    ):
        raise TypeError("Function dictToRecipe expects dictionary as input.")
    recipe = Recipe([])
    for node in data.items():
        # print("node: ", node[0], node[1], " ", type(node[0]), len(node))
        # #, node.inputs, node.outputs)
        try:
            newNode = Node(
                node[0],
                node[1]["inputs"],
                node[1]["outputs"],
                node[1]["resource"],
                node[1]["type"],
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
