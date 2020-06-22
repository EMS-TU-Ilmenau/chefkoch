"""
The fridge is responsible for storing the data and steps and checking if 
they are still up-to-date.
"""
import container
from core import Chefkoch

#Resource vorläufig mit angefügt
class Resource(Item):
    """
    Resources used to create a specific item
    """
    def __init__(self):
        pass

class Item:
    """
    An item represent a piece of data, either an input or an output of a step
    """
    def __init__(self, fridge, name):
        self.fridge = fridge
        self.name
        self.refLog 
        pass

    def createHash():
        """
        create a hashfile for the main file object
        """
        pass

    def checkHash():
        """
        Check if the hashfile is still valid ?

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

class HyperItem:
    """
    Eine Art
    """
    def __init__(self):
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


        basePath(str):
            filepath to main directory of this experiment

        """
        self.chef = chef
        self basePath = basePath
        self.items   
        pass

    def update():
        """
        Updates the internal item map
        """
        pass