"""
The fridge is responsible for storing the data and steps and checking if
they are still up-to-date.
"""
from chefkoch.container import JSONContainer
import chefkoch.core
import chefkoch.tarball
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
        if not os.path.exists(basePath + "/fridge"):
            os.makedirs(basePath + "/fridge")
        else:
            warnings.warn("there already exists a directory: " + self.basePath)
        """
        # Testzwecke
        shelf = FridgeShelf(self, "A")
        self.shelfs["test"] = shelf
        self.shelfs["test"].items["Titem"] = Item(shelf)
        # print(self.shelfs["test"].items["Titem"].check())
        shelf = FridgeShelf(self, "B")
        self.shelfs["test"] = shelf
        self.shelfs["test"].items["Titem1"] = Item(shelf)
        # print(self.shelfs["test"].items["Titem"].refLog
        # == self.shelfs["test"].items["Titem"].refLog)
        """

    def update(self):
        """
        Updates the internal item map
        """
        pass

    def checkItem(self, name, container):
        """
        WIP
        """
        pass


class Shelf(ABC):
    """
    Abstrakte Basis-Klasse für die unterschiedlichen shelfs
    """

    def __init__(self, fridge, name):
        self.items = dict()
        self.fridge = fridge
        self.path = fridge.basePath + "/fridge/" + str(name)
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        else:
            warnings.warn("there already exists a directory: " + self.path)


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
