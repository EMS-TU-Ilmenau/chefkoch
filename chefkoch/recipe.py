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
import yaml

# logs need to be imported this way to not write logs.logger all the time
from .logs import *


# constants
# built-in functions that can be called as a simulation step inside a node
BUILT_INS = ["collect"]


class Plan:
    """

    """

    nodes: list = []
    constructiontree: dict = {}

    def __init__(self, recipe, *targets):
        """
        Initialize Plan Object over a given recipe and calculation targets
        :param recipe: recipe object
        :param targets: calculation targets given as string (name of the node),
                        int (list index of the node in recipe object)
                        or node object
        """
        # targets = []
        if len(targets) == 0:
            self.nodes = recipe
        else:
            for target in targets:
                if type(target) == str or type(target) == int:
                    targetnode = recipe[target]
                elif type(target) == Node:
                    targetnode = target
                tree = self.createConstructionTree(recipe, target)
                self.constructiontree[targetnode.name] = tree

    def createConstructionTree(self, recipe, target):
        """
        build recursively a construction tree based on a recipe and a target
        :param recipe:
        :param target: calculation target given as string (name of the node),
                        int (list index of the node in recipe object)
                        or node object
        :return:
        """
        constructiontree = {}
        if type(target) == str or type(target) == int:
            node = recipe[target]
        elif type(target) == Node:
            node = targetiagram
        if node not in self.nodes:
            self.nodes.append(node)
        for inputKey, inputValue in node.inputs.items():
            children = recipe.inputIsOutput(inputValue)
            for child in children:
                if child.name not in self.constructiontree.keys():
                    constructiontree[inputValue] = self.createConstructionTree(
                        recipe, child
                    )
                else:
                    constructiontree[inputValue] = self.constructiontree[
                        child.name
                    ]
        return constructiontree


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
        for inputKey, inputValue in (
            self[item].inputs.items()
            if type(item) == int
            else item.inputs.items()
        ):
            prerequisites = self.inputIsOutput(inputValue)
            if len(prerequisites) > 0:
                ret.extend(prerequisites)
                for i in prerequisites:
                    # print("i is: ")
                    # print(i.name)
                    ret.extend(self.getPrerequisits(i))
        return ret

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

    def findCircles(self):
        """
        Makes list of all nodes, which are those who only have flavour
        parameters as inputs.
        Then starts depth-first search for every root node. If there is a way
        back to a previously visited node, there is a warning about a circle.

        Raises
        -------
        RecursionError:
            If there is a circle in the recipe that would cause an
            endless recursion.
        """
        rootNodes = []
        # 1. Make list of all root nodes
        # 1.1. Make set of all inputs that refere to the flavour file
        all_ins = set([])
        for node in self.nodes:
            all_ins.update(node.inputs.values())
        flavour_inputs = set(i for i in all_ins if i.startswith("flavour."))
        # TODO neue Möglichkeit für startswith auf Mengen finden
        # 1.2. If all inputs of a node are in there, node is root node.
        for node in self.nodes:
            node_inputs = set(node.inputs.values())
            if (node_inputs & flavour_inputs) == node_inputs:
                # in that case all of node's inputs start with flavour.
                rootNodes.append(node)
        logger.debug("Root Nodes:")
        # 2. Start depth-first-search for every such node.
        for node in rootNodes:
            logger.debug(node.name)
            nodesOnTheWay = []
            # do recursive depth-first search
            if self.recursiveDFS(node, nodesOnTheWay):
                raise RecursionError(
                    "The recipe contains a circle reachable from " + node.name
                )
        return

    def recursiveDFS(self, node, nodesOnTheWay):
        """
        Recursive Depth First Search finding circles.

        Parameters
        ------------
        node (Node):
            The node, the DFS starts in.
        nodesOnTheWay (Node[]):
            Previously visited nodes. If a node in there can be revisited \
            by going deeper into the graph, there is a circle.

        Returns
        -------
        returns:
            `True` if there is a circle. False elsewise.
        """
        namesOnTheWay = ""
        for nodeOTW in nodesOnTheWay:
            namesOnTheWay = namesOnTheWay + " " + nodeOTW.name
        logger.debug(
            "Executing rDFS for " + node.name + " and " + namesOnTheWay
        )
        if node in nodesOnTheWay:
            warnings.warn(
                "The recipe contains a circle along "
                + namesOnTheWay
                + node.name
                + " and can therefore"
                + " not be executed."
            )
            return True
        nodesOnTheWay.append(node)
        # this only gets longer in deeper recursion levels
        # no need to bring nodes from deeper levels up.
        for key in node.outputs:
            output = node.outputs[key]
            # output might be used by several other nodes
            for nextNode in self.nodes:
                # to search for the values in a dict instead of their keys
                # we need to invert it
                invertedInputDict = dict(
                    map(reversed, nextNode.inputs.items())
                )
                if output in invertedInputDict:
                    logger.debug(
                        "Taking the edge from "
                        + node.name
                        + " to "
                        + nextNode.name
                    )
                    if self.recursiveDFS(nextNode, nodesOnTheWay):
                        return True  # a circle was found
                    # else continue with next node
        # after all outgoing edges where tested, remove current node
        nodesOnTheWay.remove(node)
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
        step_obj = StepSource(stepsource)
        self.step = step_obj.step
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
                "You are using python 3, but don't worry, we make it work."
            )
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


class StepSource:
    """
    Specifies the function to be executed inside a node in the recipe.
    """

    def __init__(self, stepsource):
        """
        Tests the step source if it is a recipe, a python executable or
        a built-in function and initialises it if so.

        Parameters
        ----------
        stepsource (str):
            file path to a sub-recipe, a python executable or the name \
            of a built-in function

        Raises
        ------
        TypeError:
            If the string does not match any of the above.
        """
        # testing if step is built-in; JSON file or python function
        extension = os.path.splitext(stepsource)[1]
        if extension == ".py":
            self.step = stepsource
        elif extension == ".json":
            self.step = stepsource
        elif str(stepsource) in BUILT_INS:
            self.step = stepsource
            # done: research on assigning functions as attributes
            # (so that it can be accessed no matter where the object
            # is used)
        else:
            raise TypeError(
                "Stepsource : "
                + str(stepsource)
                + ". Must be a Python file, another recipe "
                + "or a build-in function."
            )


class Flavour(dict):
    """
    The Flavour class extends the dictionary class and holds the parsed flavour
    file. The flavour file is the collection of all paramters needed for the
    simulation and all their values the simulation should be executed with. The
    goal is to find the best parameter combination. Paramter can have a constant
    value, a list of values or a range. They can also be files.
    """

    def tostring(self):
        """
        Converts the data held inside the flavour object into a string.

        Returns
        ----------
        String that holds structured content of the flavour object
        """
        content = "The flavour file contains: "
        for key in self:
            content += "\n  " + self[key].tostring()
        return content

    # todo overwrite return of the parameter values list so that
    # flavour["param_name"] returns flavour["param_name"][0] if there is only
    # one element in the list


class FileParamValue:
    """
    A single parameter value which is a file, defined by filepath and optional
    key/passphrase to the file.
    """

    key = ""  #: Saves optional passphrase to the given file, defaults to "".
    file = ""  #: Saves the filepath, if the given file exists, defaults to "".

    def __init__(self, filepath, key):
        """
        Initialises a new parameter value, that holds a file.

        Parameters
        ----------
        filepath (str):
            file path as given in flavour.json or flacour.yaml
        key (str or None):
            optional key or passphrase to the file

        Raises
        -------
        IOError:
            In case, the filepath is None or the path does not exist, there \
            is an IOError raised and the functions returns.
        """
        logger.debug("Creating new FileParamValue")
        logger.debug("Filepath (dict): " + str(filepath))
        logger.debug("Key (dict): " + str(key))
        self.key = key
        logger.debug("Key: " + str(self.key))
        if filepath is None:
            raise IOError("The filepath is None.")
            return
        if os.path.isfile(filepath):
            self.file = filepath
            logger.debug("Filepath: " + str(self.file))
        else:
            warnings.warn("The file " + filepath + " does not exist.")
            raise IOError("The file " + filepath + " does not exist.")
            return

    def tostring(self):
        """
        Returns a printable and formatted string that shows the
        FileParamValue and its values.

        Returns
        -------
        String that holds structured information on the FileParamValue
        """
        content = "Value is following file: \n  "
        content += self.file + "\n  Key: " + str(self.key)
        return content


class Param:
    """
    A parameter with all values attached to it.
    """

    # todo: make Param class extend list so that Param returns Param.values
    values = []  #: All possible values of the parameter

    def __init__(self, name, entry):
        """
        Creates a new paramter from the data gotten from the flavour file.

        Parameters
        ----------
        name (str):
            name as provided as in flavour file
        entry (dict):
            if the falvour file was a dict, it was flavour['name']
        """
        self.values = []
        logger.debug("Creating a new parameter " + str(name))
        self.name = name
        if type(entry) is not list:  # a single value so to say
            logger.debug("It has a single value: " + str(entry))
            self.appendEntry(entry)
        else:
            logger.debug("It has more than one value.")
            for sub_entry in entry:  # the entry in the json file
                self.appendEntry(sub_entry)
        logger.debug("Fin.")

    def appendFileParam(self, entry):
        """
        Appends a file parameter given in the JSON or YAML data to the
        Param.values list.

        Parameters
        ----------
        entry (dict):
            dict with fields type, file and key

        Raises
        ------
        ValueError:
            If there is no 'file' field to the entry or if the given file \
            path does not exist
        """
        try:
            newValue = FileParamValue(entry["file"], entry["key"])
            self.values.append(newValue)
            logger.debug("Appending " + str(newValue) + newValue.tostring())
        except KeyError as err:
            # KeyError because the key-field is missing, in this case ignore
            # todo: different possible exceptions
            logger.exception(
                "Either the file or the key field of the "
                + "entry are missing."
            )
            # only abort if the file is missing. Missing keyword is possible.
            try:
                forgetfile = entry["file"]
            except KeyError as err:
                raise ValueError("There is no file given to the file param!")
                # todo: is it important to have a value error or can I change
                # it to KeyError?
            pass
        except IOError as err:
            # given filepath does not exist, so stop execution
            raise ValueError("The filepath to the file param does not exist.")
            # todo ValueError is catched somewhere. Rename to IOError there!

    def appendValuesFromRange(self, entry):
        """
        Appends all values within a range given in the JSON or YAML data to
        Param.values

        Parameters
        ----------
        entry (dict):
            dict with fields start, stop and step.

        Raises
        ------
        KeyError:
            If a field of the entry is missing.
        """
        logger.debug("More values are given by a range.")
        try:
            i = entry["start"]
            stop = entry["stop"]
            step = entry["step"]
        except KeyError as err:
            raise KeyError(
                "The start, stop or step field of "
                + str(entry)
                + "are missing."
            )
        valid_start = isinstance(i, int) or isinstance(i, float)
        valid_stop = isinstance(stop, int) or isinstance(stop, float)
        valid_step = isinstance(step, int) or isinstance(step, float)
        valid = valid_start and valid_step and valid_stop
        if not valid:
            warnings.warn(
                "The start, step and stop value of a parameter range"
                + " need to by of type int or float, so an empty list"
                + " was appended! Check for correctness!"
            )
            return
        # get the direction of the range before using <= or >=
        if i < stop and step > 0:
            # add all values within range
            while i <= stop:
                logger.debug("Adding value " + str(i))
                self.values.append(i)
                i = i + step
        elif i > stop and step < 0:
            # add all values within range
            while i >= stop:
                logger.debug("Adding value " + str(i))
                self.values.append(i)
                i = i + step
        else:
            warnings.warn(
                "The start "
                + str(i)
                + ", stop "
                + str(stop)
                + " and step "
                + str(step)
                + " of the range leave an empty list for"
                + " this paramter. Please check if this is intended."
            )

    def appendEntry(self, entry):
        """
        Appends a single entry within the JSON or YAML data received from the
        flavour file.

        Parameters
        ----------
        entry (dict):
            file or range or any other value
        """
        try:
            type = entry["type"]
        except KeyError as err:
            logger.debug(
                "There is no type specified to this entry. It will"
                + " be interpreted and appended as a dictionary."
            )
            self.values.append(entry)
            return
        except TypeError as err:
            # entry is not a dictionary
            logger.debug(
                "The entry is not a dictionary. It is appended normally."
            )
            self.values.append(entry)
            return
        # if there is a type to the entry, test if it is known
        logger.debug("It is of type " + type)
        if type == "file":
            try:
                self.appendFileParam(entry)
            # todo: capture and handle this exception inside appenFileParam
            except ValueError as err:
                pass
        elif type == "range":
            self.appendValuesFromRange(entry)
        else:
            # allow everything else by default, value could also be a list.
            warnings.warn(
                "There is a type specified to "
                + str(entry)
                + ", but neither 'range' nor 'file'. It will be "
                + "appended as a dictionary."
            )
            self.values.append(entry)

    def tostring(self):
        """
        Returns a printable and formatted string that shows the Parameter
        and its values.

        Returns
        -------
            String thta holds the content of the parameter
        """
        content = "Parameter name: " + self.name + "\n  "
        for value in self.values:
            if type(value) is FileParamValue:
                for line in value.tostring.split():
                    content += "  " + value.tostring()
            else:
                content += "  " + str(value) + "\n  "
        return content


def readrecipe(filename):
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
    data = {}
    type = filename[-4:]
    if type == "yaml":
        data = openyaml(filename)
    recipe = dictToRecipe(data)
    recipe.inputIntegrity()
    recipe.findCircles()
    printRecipe(recipe)
    return recipe


def readflavour(filename):
    """
    Opens a YAML file and parses it into a flavour object. Then outputs
    the data inside the flavour file.

    Parameters
    ----------
    filename (str):
        file path

    Returns
    --------
    flavour - object of type flavour.
    :rtype: Flavour
    """
    data = {}
    type = filename[-4:]
    if type == "yaml":
        data = openyaml(filename)
    flavour = dictToFlavour(data)
    print(flavour.tostring())
    # todo: input Integrity checks
    return flavour


def openyaml(filename):
    """
    Opens a YAML file, makes sure it is valid YAML and the file exists
    at the given path. Loads the whole file at once. File should there-
    fore not be too big.

    Parameters
    ----------
    filename (str):
        file path

    Returns
    --------
    data - dict or list depending on YAML structure

    Raises
    ------
    IOError:
        If the file path or file name are incorrect.
    ValueError:
        If the given file is no valid YAML format.
    """
    if not os.path.isfile(filename):
        raise IOError("The file path or file name is incorrect.")
    with open(filename) as f:
        try:
            data = yaml.load(f, Loader=yaml.SafeLoader)
            # That's the whole file at once. Hope files dont get too big
        except ValueError as err:
            raise ValueError("This is no valid YAML file.")

    return data


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
    if not isinstance(data, dict):
        raise TypeError("Function dictToRecipe expects dictionary as input.")
    recipe = Recipe([])
    for node in data["nodes"]:
        try:
            newNode = Node(
                node["name"],
                node["inputs"],
                node["outputs"],
                node["stepsource"],
            )
            recipe.nodes.append(newNode)
        except KeyError as err:
            raise KeyError("Error while parsing data into recipe object.")

    return recipe


def dictToFlavour(data):
    """
    Turns data loaded from a yaml file into a flavour object.

    Parameters
    ----------
    data (dict or list):
        dict or list depending on yaml file.

    Returns
    -------
    flavour - object of class Flavour
    :rtype: Flavour

    Raises
    ------
    TypeError:
        If some data to the flavour file is missing.
    Exception:
        If some random error should occur.
    """
    # todo: if the flavour file has an entry that misses the "type" field, there
    # should be a warning and this parameter should be skipped instead of
    # having a random key error
    if not isinstance(data, dict):
        raise TypeError(
            "Function dictToFlavour expects a dictionary as input."
        )
    flavour = Flavour({})
    for param in data:
        try:
            newParam = Param(
                param,  # name which is also key
                data[param],  # will be handled in Param init
            )
            if len(newParam.values) > 0:
                flavour[param] = newParam  # new entry to dict
            else:
                warnings.warn(
                    "The parameter "
                    + param
                    + " has no valid"
                    + " value and will be excluded from the flavour."
                )
        except TypeError as errorMessage:
            raise TypeError(errorMessage)
        except Exception as err:
            raise Exception("Error while parsing data into flavour object.")

    return flavour


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
def readfile(type, filename):
    """
    Wrapper function that calls either `readrecipe` or `readflavour`
    depending on the parameter `type`.

    Parameters
    ----------
    type (str):
        Type of YAML file that should be converted into a \
        dictionary: {"recipe", "flavour"}

    Returns
    -------
    Recipe or Flavour object depending on the `type` parameter.

    Raises
    ------
    TypeError:
        If type is none of the above.

    """
    if type == "recipe":
        return readrecipe(filename)
    if type == "flavour":
        return readflavour(filename)
    else:
        raise TypeError(
            "The function readyaml only takes 'recipe' or"
            + "'flavour' as type."
        )


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
