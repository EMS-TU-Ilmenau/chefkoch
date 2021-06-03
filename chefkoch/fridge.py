"""
The fridge is responsible for storing the data and steps and checking if
they are still up-to-date.
"""
# from chefkoch.core import Logger
import warnings

from chefkoch.container import JSONContainer
import chefkoch.item
import chefkoch.step

import os

import zlib
import numpy
import math
import ast
from abc import ABC, abstractmethod


class Fridge:
    """
    The fridge stores all items or steps in chefkoch with metadata.
    It's also responsible to initializes the resources and flavours
    and create the folder structure if needed.
    """

    def __init__(self, config, basePath, logger):
        """
        Instantiate Directory as Fridge

        Parameters
        ----------
        config(Configuration):
            the configuration of this project

        basePath(str):
            filepath to main directory of this experiment

        logger(Logger):
            main-logger instance, own logger is derived from that

        """
        # self.chef = chef
        self.config = config
        self.shelves = dict()
        self.basePath = basePath
        self.mainlogger = logger
        self.logger = logger.logspec(__name__, self.basePath + "/chef.log")
        self.logger.info("FRIDGE: we hardcode our problems")
        self.makeDirectory(self.basePath + "/fridge")

    def update(self):
        """
        Updates the internal item map
        """
        # not sure if this is somehting we need
        pass

    # def addMap(self, graph):
    #     for

    """
    def checkItem(self, item):
        # checks if the item exists and maybe if the hash is still valid
        # do we need this -> Item has this function
        pass
    """

    def distributeMaps(self, map):
        for key in map.keys():
            self.shelves[key].items["step"].addMap(map[key])

    def makeDirectory(self, path):
        """
        creates the directory in the specified path, if the option
        is enabled

        Parameters
        ----------
        path(str):
            describes path to the directory
        """
        if self.config["options"]["directory"]:
            if not os.path.exists(path):
                os.makedirs(path)
            else:
                self.logger.warn(
                    "FRIDGE: there already exists a directory: " + path
                )
                # warnings.warn("there already exists a directory: " + path)

    def makeResources(self, Resources, recipe):
        """
        initialises the Resources specified in recipe and the cheffile

        Parameters
        ----------
        Resources(dict):
            dictionary with the Resources

        recipe(bool):
            describes, if the recources are from the recipe
        """
        for element in Resources:
            # FlavourShelf wird angelegt
            shelf = ItemShelf(self, element)
            self.shelves[element] = shelf
            if recipe:
                resource = chefkoch.item.Resource(
                    self.shelves[element],
                    self.basePath + "/" + Resources[element]["resource"],
                )
                name = resource.createHash()

            else:
                resource = chefkoch.item.Resource(
                    self.shelves[element],
                    self.basePath + "/" + Resources[element],
                )
                name = resource.createHash()

            self.shelves[element].items[name] = resource

            if recipe:
                # step initialisieren, gib hier mainlogger
                if Resources[element]["type"] == "python":
                    step = chefkoch.step.StepPython(shelf, self.mainlogger)
                elif Resources[element]["type"] == "shell":
                    step = chefkoch.step.StepShell(shelf, self.mainlogger)
                else:
                    print("This step isn't defined yet or you did smth wrong")

                self.shelves[element].items["step"] = step

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
            self.shelves[x].printFlavour()

    def makeItemShelves(self, outputs):
        """
        creates the necessary itemshelfs for the given outputs. It logs an
        error, if the output already exists in fridge.

        Parameters
        ----------
        outputs(list):
            list that contains the names of the different shelfs

        """
        for x in outputs:
            if x in self.shelves:
                self.logger.error(x + " already exists in this fridge!")
                # brauche ich da eine Exception-Nachricht?
                raise Exception(x + " already exists in this fridge!")
            shelf = ItemShelf(self, x)
            self.shelves[x] = shelf

    def getItem(self, name):
        """
        prototpye function for getting the correct item
        maybe needs some checks later, like is it still valid

        neue Überarbeitung

        Parameters
        ----------
        name(str):
            name of the wanted item
        """
        # needs some checks if item is up-to-date
        if name not in self.shelves:
            self.logger.critical(name + " doesn't exist in this fridge")
            raise Exception(name + " doesn't exist in this fridge")
        else:
            if isinstance(self.shelves[name], FlavourShelf):
                return self.shelves[name].items
            elif isinstance(self.shelves[name], ItemShelf):
                # prototypmäßig, erstmal die unpraktischere Variante
                if "result" in self.shelves[name].items:
                    return self.shelves[name].items["result"]
                else:
                    for x in self.shelves[name].items:
                        if isinstance(
                            self.shelves[name].items[x], chefkoch.item.Resource
                        ):
                            print("I return a resource")
                            return self.shelves[name].items[x]
            else:
                self.logger.error("This shelf doesn't exist")

    def getShelf(self, name):
        """
        returns the wanted shelf
        """
        if name in self.shelves:
            # check if still empty?
            return self.shelves[str(name)]
        else:
            return None

    def getShelfs(self, type):
        if type == "item":
            return [i for i in self.shelves if type(i) == ItemShelf]
        elif type == "flavour":
            return [i for i in self.shelves if type(i) == FlavourShelf]

    def makeResults(self, resultlist):
        self.resultlist = []
        for priority in resultlist:
            for result in priority:
                h = self.shelves[result[0]]
                g = chefkoch.item.Result(
                    self.shelves[result[0]], None, result[1]
                )
                h.items[result[1]["hash"]] = g

        # bekommt Liste von results die angelegt werden sollen (vom Plan)
        # legt entsprechende Result-items an mit übergeben dependencies
        # und Namen das hashs über dependencies
        # legt sie im entsprechenden Item-Shelf (von output) an und sortiert
        # den richtigen Step dazu, der sich unter [stepname]["step"] finden
        # lassen sollte
        # gibt eine Liste aller Result-Items zurück, die dann an den Scheduler
        # gegeben werden soll
        pass


class Shelf(ABC):
    """
    Abstract base-class for the different shelves. They store the different
    variations of the items.
    """

    def __init__(self, fridge, name):
        """
        initalizes a shelf, with a given name and a specified path.

        Parameters
        ----------
        fridge(Fridge):
            the fridge-class
        name(str):
            name of a certain shelf
        """
        self.items = dict()
        self.fridge = fridge
        self.path = fridge.basePath + "/fridge/" + str(name)
        self.fridge.makeDirectory(self.path)
        self.name = name
        # maybe needs another file to find items by their used attributes
        # like another dictionary or something
        # iterative could be an option, cause we don't have to much
        # items in one shelf
        self.admin = None

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
    Represents results from computations.
    """

    def find(self, name):
        """
        find a certain item in the fridgeshelf

        Parameters
        ----------
        name(str):
            name of wanted item

        Returns
        --------
        item(Item);if it's exists
        """
        # might be extended with admin-dic
        if name in self.items:
            return self.items[name]
        else:
            return None

    def addItem(self, item):
        """
        Adds an item to the shelf, if they didn't exist prior

        Parameters
        ----------
            item(Item): item to be added to this shelf
        """
        # erstmal zum Hinzufügen von results, vllt später noch
        # für etwas anderes geeignet
        # something like checking, if it isn't there
        # this won't work, when we have multiple result
        if "result" in self.items:
            print("Woowie, you alreade have a result")
        else:
            print("added item")
            self.items["result"] = item


class FlavourShelf(Shelf):
    """
    A shelf-variant that contains different Flavours in dictionary-form.
    """

    def ranges(self, f):
        """
        translates the linear- and logarithmic-range-entries to valuelists.

        Parameters:
        -----------
        f(dict):
            dictionary that specifies a range

        Returns
        --------
        vals(list):
            contains the translated numeric values
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
        # probably needs some checks for correct input
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

    def printFlavour(self):
        """
        allows to print flavours to a JSON-File in the correct directory,
        if the directory option is enabled
        """
        if self.fridge.config["options"]["directory"]:
            if os.path.exists(self.path):
                container = JSONContainer(None, self.items)
                hashName = container.hash()
                container.save(self.path + "/" + hashName + ".json")
            else:
                warnings.warn(
                    "unable to print these flavours, there is no directory"
                )
