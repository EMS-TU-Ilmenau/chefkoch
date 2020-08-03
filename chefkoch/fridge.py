"""
The fridge is responsible for storing the data and steps and checking if
they are still up-to-date.
"""
from chefkoch.container import JSONContainer
import chefkoch.core
import chefkoch.tarball
import chefkoch.item
import os
import warnings
import zlib
from abc import ABC, abstractmethod


class Fridge:
    """
    The fridge stores all items or steps in chefkoch with metadata

    """

    def __init__(self, chef, basePath):
        """
        Instantiate Directory as Fridge

        Parameters
        ----------
        chef(Chefkoch):
            gets an instance of chef

        basePath(str):
            filepath to main directory of this experiment

        """
        self.chef = chef
        self.shelfs = dict()
        self.basePath = basePath
        self.makeDirectory(self.basePath + "/fridge")
        """
        # Testzwecke
        shelf = ItemShelf(self, "A")
        self.shelfs["test"] = shelf
        self.shelfs["test"].items["Titem"] = chefkoch.item.Resource(shelf)
        # print(self.shelfs["test"].items["Titem"].check())
        shelf = ItemShelf(self, "B")
        self.shelfs["test"] = shelf
        self.shelfs["test"].items["Titem1"] = chefkoch.item.Resource(shelf)
        # print(self.shelfs["test"].items["Titem"].refLog
        # == self.shelfs["test"].items["Titem"].refLog)
        """

    def update(self):
        """
        Updates the internal item map
        """
        pass

    def checkItem(self, item):
        """
        WIP
        Ist diese Funktion überhaupt sinnvoll?
        """
        pass

    def makeDirectory(self, path):
        """
        creates the directories, if the option is enabled

        Parameters
        ----------
        path(str):
            describes path to the directory
        """
        if self.chef.configuration["directory"]:
            if not os.path.exists(path):
                os.makedirs(path)
            else:
                warnings.warn("there already exists a directory: " + path)


class Shelf(ABC):
    """
    Abstrakte Basis-Klasse für die unterschiedlichen shelfs
    """

    def __init__(self, fridge, name):
        self.items = dict()
        self.fridge = fridge
        self.path = fridge.basePath + "/fridge/" + str(name)
        self.fridge.makeDirectory(self.path)
        self.name = name


class ItemShelf(Shelf):
    """
    A container for items of a similar kind
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

    # müsste vielleicht auch noch abstrakt werden
    pass


class FlavourLogarithmicRange(FlavourShelf):
    """
    """

    def __init__(self, start, stop, step):
        pass


class FlavourLinearRange(FlavourShelf):
    """
    """

    def __init__(self, start, stop, step):
        pass
