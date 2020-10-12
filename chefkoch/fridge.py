"""
The fridge is responsible for storing the data and steps and checking if
they are still up-to-date.
"""
from chefkoch.container import JSONContainer
import chefkoch.core
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
        self.shelfs = dict()
        self.basePath = basePath
        self.makeDirectory(self.basePath + "/fridge")

    def update(self):
        """
        Updates the internal item map
        """
        pass

    def checkItem(self, item):
        """
        WIP, sollte man auseinandernehmen und wieder vernünftig zusammenbauen
        Ist diese Funktion überhaupt sinnvoll?
        man bekommt ein Item und entweder wird der entsprechende Itemshelf
        anegelegt und das Item darin angelegt oder oder es existiert bereits
        -> prüft erstmal nicht auf Konsistenz, da mache ich eine Extra-Funktion
        -> also nur, gibt es Shelf mit dem Item schon: False
        -> gibt es den nicht, wird er angelegt und das Item eingeordnet: True
        Problem: brauche dem entsprechend Namen
        """
        """
        if (item.shelf.name in self.shelfs):
            # wenn es unter den Namen einen Ordner gibt
            # erstmal grob
            item = self.shelfs[name].items[name]  # dann holen wir uns das Item
            # speichern den Pfad zu der existierenden Json
            itempath = self.shelfs[name].path + "/" + str(name) + ".json"
            # überprüfen Dateigröße
            if JSONContainer(itempath) == container:
                # das ist schon das passende Item
                return (item, None)
            else:
                # Hashkollision
                # create new Item mit anderem Namen und neuem shelf
                # erstmal mit Indizes dann
                i = 1  # zähler
            begin = self.shelfs[name].path + "/" + str(name) + "_"
            end = false
            # gehe die shelfs mit den Indizes durch
            while (str(name) + "_" + str(i)) in self.shelfs:
                if JSONContainer(begin + i + ".json") == container:
                    # wenn passende Item gefunden
                    end = true
                    break
                else:
                    i += 1

            name = name + "_" + i
            if end:
                # wir können passendes Item zurückgeben
                return (self.shelfs[name].items[name], None)
            else:
                # wir müssen einen neuen Shelf für das Item zurückgeben
                shelf = FridgeShelf(self, name)
                self.shelfs[name] = shelf
                return (None, self.shelfs[name])

        else:
            # wenn es das noch gar nicht gibt,
            # wird neuer Shelf angelegt und der Namen des Shelfs zurückgegeben
            shelf = FridgeShelf(self, name)
            self.shelfs[name] = shelf
            return (None, self.shelfs[name])
    """

    def makeDirectory(self, path):
        """
        creates the directories, if the option is enabled

        Parameters
        ----------
        path(str):
            describes path to the directory
        """
        # if self.chef.configuration["options"]["directory"]:
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
            self.shelfs[element] = shelf
            if recipe:
                resource = chefkoch.item.Resource(
                    self.shelfs[element], Resources[element]["resource"]
                )
                name = zlib.adler32(
                    Resources[element]["resource"].encode("utf-8")
                )
                # not correct
                # name = resource.createHash()
            else:
                resource = chefkoch.item.Resource(
                    self.shelfs[element], Resources[element]
                )
                name = zlib.adler32(Resources[element].encode("utf-8"))
                # the real code, can't use to test
                # name = resource.createHash()

            self.shelfs[element].items[name] = resource
            print(element)
            print(self.shelfs[element].items)

    def makeFlavours(self, Flavours):
        """
        initializes the flavour-shelves for the given flavours

        Parameters
        ----------
        Flavours(dict):
            dictionary with the different flavours

        """
        # shelf = FlavourShelf(self, "flavours")
        # vllt will man es ja doch irgendwann mal schön machen
        for x in Flavours:
            shelf = FlavourShelf(self, x)
            self.shelfs[x] = shelf
            self.shelfs[x].makeFullList(Flavours[x])
            # optional printing of the different Flavours in a json
            self.shelfs[x].printFlavour(x)

    def makeItemShelves(self, outputs):
        """
        creates the necessary itemshelfs

        Parameters
        ----------
        outputs(list):
            list that contains the names of the different shelfs

        """
        for x in outputs:
            if x in self.shelfs:
                raise Exception(x + " already exists in this fridge!")
            shelf = ItemShelf(self, x)
            self.shelfs[x] = shelf


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


class FlavourShelf(Shelf):
    """
    A container for different Flavours
    """

    def ranges(self, f):
        """
        translates the log-range-entries to valuelists

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
            print("difficult")
            f = Flavours
            self.items = self.ranges(f)
        # print(self.items)

    def printFlavour(self, name):
        if self.fridge.config["options"]["directory"]:
            if os.path.exists(self.path):
                container = JSONContainer(None, self.items)
                hashName = container.hash()
                container.save(self.path + "/" + hashName + ".json")
            else:
                warnings.warn(
                    "unable to print these flavours, there is no directory"
                )
