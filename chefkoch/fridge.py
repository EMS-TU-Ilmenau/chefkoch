"""
The fridge is responsible for storing the data and steps and checking if
they are still up-to-date.
"""
from chefkoch.container import JSONContainer
import chefkoch.core


class Item:
    """
    An item represent a piece of data, either an input or an output of a step
    """

    def __init__(self, shelf, name):
        self.name = name
        self.refLog = JSONContainer()
        self.refLog.save(name)
        self.shelf = shelf

    def createHash():
        """
        create a hashfile for the main file object
        """
        pass

    def checkHash():
        """
        Check if the hashfile is still valid

        Returns:
        --------
        returns:
            true,....

        """
        pass

    def check():
        """
        Checks if the file and it's refLog exists and if the refLog itself is
        unchanged

        Returns:
        --------
        returns:
            true,....

        """
        pass


class Resource(Item):
    """
    Resources used to create a specific item
    """

    def __init__(self):
        pass


class FridgeShelf:
    """
    A container for items of a similar kind
    """

    def __init__(self, fridge):
        self.items = dict()
        self.fridge = fridge
        pass

    def find():
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
        self.basePath = basePath
        self.shelfs = dict()
        pass

    def update():
        """
        Updates the internal item map
        """
        pass
