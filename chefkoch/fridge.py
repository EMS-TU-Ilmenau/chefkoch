"""
The fridge is responsible for storing the data and steps and checking if
they are still up-to-date.
"""
from chefkoch.container import JSONContainer
import chefkoch.core
import os
import warnings


class Item:
    """
    An item represent a piece of data, either an input or an output of a step
    """

    def __init__(self, shelf, name):
        # zugeordneter Shelf
        self.shelf = shelf
        # Name + Pfad anlegen
        self.name = (self.shelf.fridge.basePath + "/fridge/" + name + ".json")
        # legt passende JSON an
        self.refLog = JSONContainer()
        self.refLog.save(self.name)

    def createHash(self):
        """
        create a hashfile for the main file object
        """
        pass

    def checkHash(self):
        """
        Check if the hashfile is still valid

        Returns:
        --------
        returns:
            true,....

        """
        pass

    def check(self):
        """
        Checks if the file and it's refLog exists and if the refLog itself is
        unchanged

        Returns:
        --------
        returns:
            true,....

        """
        if (os.path.isfile(self.name + ".json")):
            return True
        else:
            return False


class Resource(Item):
    """
    Resources used to create a specific item
    """

    def __init__(self, basePath):
        pass


class FridgeShelf:
    """
    A container for items of a similar kind
    """

    def __init__(self, fridge):
        self.items = dict()
        self.fridge = fridge
        pass

    def find(self):
        pass


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
            warnings.warn(
                "there already exists a directory: "
                + self.basePath
            )
        # anlegen des Ordners für resourcen
        # keine Ahnung, ob der da bleibt
        if not os.path.exists(basePath + "/resource"):
            os.makedirs(basePath + "/resource")
        else:
            warnings.warn(
                "there already exists a directory: "
                + self.basePath
            )

        # Testzwecke
        shelf = FridgeShelf(self)
        self.shelfs["test"] = shelf
        self.shelfs["test"].items["Titem"] = Item(shelf, "A")
        print(self.shelfs["test"].items["Titem"].check())

    def update(self):
        """
        Updates the internal item map
        """
        pass
