"""
The items are the Objects stored in the Fridge

"""
from chefkoch.container import JSONContainer
import chefkoch.core
import chefkoch.tarball
import os
import warnings
import hashlib
from abc import ABC, abstractmethod
import numpy as np
import pickle

# TODO: das Ganze mal vernünftig aufdröseln


class Item(ABC):
    """
    An item represent a piece of data, either an input or an output of a step
    """

    def __init__(self, shelf, dict=None, container=None):
        # zugeordneter Shelf
        self.shelf = shelf
        if container is not None:
            self.dependencies = container
        elif dict is not None:
            # für Result
            self.dependencies = JSONContainer(data=dict)
            self.createHash()
            self.dependencies.save(self.hash)

    def createHash(self):
        """
        create a hashfile for the dataset
        """
        # over dependencies, so it would be
        self.hash = self.dependencies.hash()

    def checkHash(self):
        """
        Check if the hashfile is still valid

        Returns:
        --------
        returns:
            true,....

        """
        if self.hash == self.dependencies.hash():
            return True
        else:
            print(f"this hash isn't accurate anymore")
            return False

    def check(self):
        """
        Checks if the file and it's refLog exists and if the refLog itself is
        unchanged

        Returns:
        --------
        returns:
            true,....

        """
        # only check if directory=True and probably also check if log exists
        # in incorporate a checkHash
        if os.path.isfile(self.shelf.path + "/" + self.hashName + ".json"):
            return True
        else:
            return False


class Result(Item):
    """
    contains the result from a specific step
    may need the step?
    printing of the result
    """

    def __init__(self, shelf, result, dependencies):
        super().__init__(shelf, dict=dependencies)
        self.result = result
        path = self.shelf.path + "/" + self.hash
        # besser ändern, dass nur result-shelfs ausgegeben werden
        if self.shelf.fridge.config["options"]["directory"]:
            with open(path, "wb") as handle:
                pickle.dump(
                    self.result, handle, protocol=pickle.HIGHEST_PROTOCOL
                )
        print("this is a result!")


class Resource(Item):
    """
    A resource needed for a specific step
    """

    def __init__(self, shelf, path):
        """
        initializes Ressource

        Parameters
        ----------
        shelf(Shelf):
            the item belongs to this shelf

        path(str):
            Path to the Ressource
        """
        # später mit item abstrahiert
        # super().__init__(self, shelf, path)
        self.shelf = shelf
        self.path = path

        name, file_ext = os.path.splitext(os.path.split(self.path)[-1])
        if file_ext == ".npy":
            self.type = "numpy"
            print(self.type)
        elif file_ext == ".py":
            self.type = "python"
        else:
            print("so weit bin ich noch nicht")

        # Hashing; not good programming style
        self.hash = self.createHash()

        if shelf.fridge.config["options"]["directory"]:
            # problems with paths
            # print(self.shelf.path + "/" + str(self.hash))
            # print(os.path.isfile(self.shelf.path + "/" + str(self.hash)))
            if os.path.isfile(self.shelf.path + "/" + self.hash):
                print("This path exists")
                # os.replace(self.path, self.shelf.path + "/test.txt")
            else:
                os.symlink(self.path, self.shelf.path + "/" + self.hash)
                # pass

    def createHash(self):
        """
        creates a hash over the resource

        Returns
        .......
        hashname(str):
            sha256 hash over the content of the resource-file
        """
        print(self.path)
        BLOCK_SIZE = 65536  # 64 kb
        file_hash = hashlib.sha256()
        if self.type is "numpy":
            content = self.getContent()
            file_hash.update(content.data)
            hashname = file_hash.hexdigest()
        else:
            with open(self.path, "rb") as f:
                fblock = f.read(BLOCK_SIZE)
                while len(fblock) > 0:
                    file_hash.update(fblock)
                    fblock = f.read(BLOCK_SIZE)

            hashname = file_hash.hexdigest()
        return hashname

    def getContent(self):
        """
        this function returns the correct data type, if the ressource
        isn't of type python-file
        """
        if self.type is "numpy":
            data = np.load(self.path)
            copy = np.copy(data)
            np.save(self.path, data)
            # print("es ist wieder da: " + str(os.path.islink(self.path)))
            return copy
        else:
            print("I've no idea")

    def __str__(self):
        # just for debugging purposes
        return f"this item is a ressource with path {self.path}"
