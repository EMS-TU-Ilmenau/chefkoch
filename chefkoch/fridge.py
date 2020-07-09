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


class Item:
    """
    An item represent a piece of data, either an input or an output of a step
    """

    def __init__(self, shelf):
        # zugeordneter Shelf
        self.shelf = shelf
        # legt passenden JSON-Container an
        # muss wahrscheinlich nochmal ausgelagert werden
        if (True):  # falls es ein neuer Container ist
            self.refLog = JSONContainer()
            self.refLog["test"] = "hua"
            self.hashName = self.refLog.hash()
            self.refLog.save((self.shelf.path + "/" + self.hashName + ".json"))
        else:  # ansonsten neuen Container
            self.refLog = JSONContainer()

    def createHash(self):
        """
        create a hashfile for the dataset
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

    def jsonHash(self, input):
        """
        makes a hash over the jsonfile, to check if it already exists
        """
        hashName = zlib.adler32(json_object.encode('utf-8'))
        # return str(hashName)
        return None

    def check(self):
        """
        Checks if the file and it's refLog exists and if the refLog itself is
        unchanged

        Returns:
        --------
        returns:
            true,....

        """
        if (os.path.isfile(self.shelf.path + "/" + self.hashName + ".json")):
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

    def __init__(self, fridge, name):
        self.items = dict()
        self.fridge = fridge
        self.path = fridge.basePath + "/fridge/" + name
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        else:
            warnings.warn(
                "there already exists a directory: "
                + self.path
            )

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

        # Testzwecke
        shelf = FridgeShelf(self, "A")
        self.shelfs["test"] = shelf
        self.shelfs["test"].items["Titem"] = Item(shelf)
        print(self.shelfs["test"].items["Titem"].check())

    def update(self):
        """
        Updates the internal item map
        """
        pass
