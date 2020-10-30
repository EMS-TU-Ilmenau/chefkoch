"""
The fridge is responsible for storing the data and steps and checking if
they are still up-to-date.
"""
from chefkoch.container import JSONContainer
import chefkoch.item
import os
import warnings
import zlib
import numpy
import math
import ast
from abc import ABC, abstractmethod


class Fridge:
    """
    The fridge stores all items or steps in chefkoch with metadata

    """

    # def __init__(self, chef, basePath):
    def __init__(self, config, basePath):
        """
        Instantiate Directory as Fridge

        Parameters
        ----------
        chef(Chefkoch):
            gets an instance of chef

        basePath(str):
            filepath to main directory of this experiment

        """
        # self.chef = chef
        self.config = config
        self.shelves = dict()
        self.basePath = basePath
        self.makeDirectory(self.basePath + "/fridge")

    def update(self):
        """
        Updates the internal item map
        """
        # not sure if this is somehting we need
        pass

    def checkItem(self, item):
        """
        checks if the item exists and maybe if the hash is still valid
        """
        # do we need this -> Item has this function
        pass

    def makeDirectory(self, path):
        """
        creates the directories, if the option is enabled

        Parameters
        ----------
        path(str):
            describes path to the directory
        """
        if self.config["options"]["directory"]:
            if not os.path.exists(path):
                os.makedirs(path)
            else:
                warnings.warn("there already exists a directory: " + path)

    def makeResources(self, Resources, recipe):
        """
        initialises the Resources

        Parameters
        ----------
        Resources(dict):
            dictionary with the Resources

        recipe(bool):
            describes, if the recources are from the recipe
        """
        # print(Resources)
        for element in Resources:
            # FlavourShelf wird angelegt
            shelf = ItemShelf(self, element)
            self.shelves[element] = shelf
            if recipe:
                resource = chefkoch.item.Resource(
                    self.shelves[element],
                    self.basePath + "/" + Resources[element]["resource"],
                )
                # print(self.basePath + "/" + Resources[element]["resource"])
                name = resource.createHash()
            else:
                print(Resources[element])
                resource = chefkoch.item.Resource(
                    self.shelves[element],
                    self.basePath + "/" + Resources[element],
                )
                # print(self.basePath + "/" + Resources[element])
                name = zlib.adler32(Resources[element].encode("utf-8"))
                # the real code, can't use to test
                # name = resource.createHash()

            self.shelves[element].items[name] = resource

    def makeFlavours(self, Flavours):
        """
        initializes the flavour-shelves for the given flavours

        Parameters
        ----------
        Flavours(dict):
            dictionary with the different flavours

        """
        for x in Flavours:
            shelf = FlavourShelf(self, x)
            self.shelves[x] = shelf
            self.shelves[x].makeFullList(Flavours[x])
            # optional printing of the different Flavours in a json
            self.shelves[x].printFlavour(x)

    def makeItemShelves(self, outputs):
        """
        creates the necessary itemshelfs for outputs

        Parameters
        ----------
        outputs(list):
            list that contains the names of the different shelfs

        """
        for x in outputs:
            if x in self.shelves:
                raise Exception(x + " already exists in this fridge!")
            shelf = ItemShelf(self, x)
            self.shelves[x] = shelf

    def getItem(self, name):
        """
        prototpye function for getting the correct item
        maybe needs some checks later, like is it still valid

        Parameters
        ----------
        name(str):
            name of the wanted item
        """
        if name not in self.shelves:
            raise Exception(name + " doesn't exist in this fridge")
        else:
            if isinstance(self.shelves[name], FlavourShelf):
                return self.shelves[name].items
            elif isinstance(self.shelves[name], ItemShelf):
                print("this is a wip")
                # prototypmäßig, erstmal die unpraktischere Variante
                if "result" in self.shelves[name].items:
                    return self.shelves[name].items["result"]
                else:
                    raise Error(f"item {name} doesn't exist")
            else:
                print("you have a really strange shelf there")

    def getShelf(self, name):
        """
        returns the correct shelf
        Maybe an other shelf
        """
        if name in self.shelves:
            # check if still empty?
            return self.shelves[str(name)]
        else:
            return None


class Shelf(ABC):
    """
    abstract base-class for the different shelves
    """

    def __init__(self, fridge, name):
        self.items = dict()
        self.fridge = fridge
        self.path = fridge.basePath + "/fridge/" + str(name)
        self.fridge.makeDirectory(self.path)

    def __len__(self):
        return len(self.items)

    def __next__(self):
        return next(self.iterator)

    def __iter__(self):
        self.iterator = iter(self.items)
        return iter(self.items)


class ItemShelf(Shelf):
    """
    A container for items of a similar kind
    Resultate von Berechnungen
    """

    def find(self, name):
        if name in self.items:
            return self.items[name]
        else:
            return None

    def addItem(self, item):
        # erstmal zum Hinzufügen von results, vllt später noch
        # für etwas anderes geeignet
        # something like checking, if it isn't there
        # packen wir es mal unter result
        if "result" in self.items:
            print("Woowie, you alreade have a result")
        else:
            print("added item")
            self.items["result"] = item


class FlavourShelf(Shelf):
    """
    A container for different Flavours
    """

    def ranges(self, f):
        """
        translates the logarithmic-range-entries to valuelists

        Parameters:
        -----------
        f(dict):
            dictionary that specifies a range
        """
        if f["type"] == "lin":
            # dealing with linear ranges
            vals = numpy.arange(f["start"], f["stop"] + 1, f["step"]).tolist()
            return vals
        elif f["type"] == "log":
            # dealing with logarithmic ranges
            # first specify base
            if "base" in f:
                base = f["base"]
            else:
                base = 10

            start = math.log(ast.literal_eval(f["start"]), base)
            stop = math.log(ast.literal_eval(f["stop"]), base)
            vals = numpy.logspace(start, stop, num=f["count"])
            return vals

    def makeFullList(self, Flavours):
        """
        parses the flavour dictionary and translates it to value lists

        Parameters:
        -----------
        Flavours(dict):
            flavour dictionary from flavour-file

        """
        if isinstance(Flavours, list):
            if isinstance(Flavours[0], dict):
                vals = []
                for elem in Flavours:
                    vals.extend(self.ranges(elem))
                self.items = vals
            else:
                self.items = Flavours

        elif isinstance(Flavours, dict):
            f = Flavours
            self.items = self.ranges(f)
        # print(self.items)

    def printFlavour(self, name):
        # wieso habe ich hier einen Namen??
        if self.fridge.config["options"]["directory"]:
            if os.path.exists(self.path):
                container = JSONContainer(None, self.items)
                hashName = container.hash()
                container.save(self.path + "/" + hashName + ".json")
            else:
                warnings.warn(
                    "unable to print these flavours, there is no directory"
                )
