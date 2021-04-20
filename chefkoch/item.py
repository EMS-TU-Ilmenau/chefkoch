"""
The items are the Objects stored in the Fridge.
Items is an abstract class, representing resources, results and
the different steps
"""

from chefkoch.container import JSONContainer

# import chefkoch.core
import chefkoch.tarball
import os
import warnings
import hashlib
from abc import ABC, abstractmethod
import numpy as np
import pickle
import chefkoch.tarball as tarball
from checksumdir import dirhash

# TODO: das Ganze mal vernünftig aufdröseln


class Item(ABC):
    """
    An item is an abstract class, that represent a piece of data,
    either an input or an output of a step.
    """

    def __init__(self, shelf, dicti: dict = None, container=None):
        """
        initialises the Item-class

        Parameters
        ----------
            shelf(Shelf):
                the shelf the item belongs to
            dicti(dict):
                the dependencies stored into a dictionary
            container(JSONcontainer):
                information already stored into a JSON-Container
        """
        # zugeordneter Shelf
        self.shelf = shelf
        if container is not None:
            # self.shelf = shelf
            self.dependencies = container
        elif dicti is not None:
            # für Result
            self.dependencies = JSONContainer(data=dicti)
            self.hash = self.createHash()
            if self.shelf.fridge.config["options"]["directory"]:
                self.dependencies.save(
                    self.shelf.path + "/" + self.hash + ".json"
                )

    def createHash(self):
        """
        create a hashfile for the dataset using the depedencies
        """
        # over dependencies, so it would be
        return self.dependencies.hash()

    def checkHash(self):
        """
        Check if the hashfile is still valid, by checking the
        if the hash is unchanged

        Returns:
        --------
        bool:
            true, when self.hash still equals the dependency-hash

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
        bool:
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
    Contains the result from a specific step
    """

    # may need a step, that it can execute
    # name vom JSON-Container
    def __init__(self, shelf, result, dependencies):
        """
        Initializes the Result
        Parameters
        ----------
        shelf(Shelf):
            the result belongs to this shelf

        result(dict):
            the result-values

        dependencies(dict):
            the dependencies from this result
        """
        super().__init__(shelf, dicti=dependencies.data)
        self.result = result
        path = self.shelf.path + "/" + self.hash
        # besser ändern, dass nur result-shelfs ausgegeben werden
        if self.shelf.fridge.config["options"]["directory"]:
            with open(path, "wb") as handle:
                pickle.dump(
                    self.result, handle, protocol=pickle.HIGHEST_PROTOCOL
                )
        # print("this is a result!")

    def execute(self):
        # sucht richtige Parameter
        # führt step aus
        pass

    def checkPrerequisites(self):
        for item in self.dependencies.data["inputs"].items():
            # i = item.items()

            h = self.shelf.fridge.shelves[item[0]]
            x = h.items[item[1].split("/")[1]].result
            if x == None:
                pass
            pass


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
        self.shelf = shelf
        self.path = path

        if os.path.isdir(self.path):
            # keine Ahnung, wie wir das vernünftig verarbeiten wollen
            # print("This is a directory")
            self.type = "dir"
        else:
            name, file_ext = os.path.splitext(os.path.split(self.path)[-1])
            if file_ext == ".npy":
                self.type = "numpy"
                # print(self.type)
            elif file_ext == ".py":
                self.type = "python"
            else:
                print("so weit bin ich noch nicht")

        # Hashing; not good programming style
        self.resourceHash = self.createResourceHash()
        data = {"hash": self.resourceHash}
        super().__init__(shelf, data, None)

        # I'm not sure where to put the tarball in this workflow
        if (
            self.type == "dir"
            and self.shelf.fridge.config["options"]["directory"]
        ):
            listing = []
            with os.scandir(self.path) as entries:
                for entry in entries:
                    listing.append(entry)
                    # print(entry)
            self.tarball = tarball.Tarball(
                self.shelf.path + "/" + self.resourceHash, listing
            )

        if shelf.fridge.config["options"]["directory"]:
            if os.path.isfile(
                self.shelf.path + "/" + self.hash
            ) or os.path.isdir(self.shelf.path + "/" + self.hash):
                print("This path should be replaced later")
                # das ist der falsche Code duh
                # os.replace(self.path, self.shelf.path + self.hash)
            else:
                os.symlink(self.path, self.shelf.path + "/" + self.hash)
                # pass

    def createResourceHash(self):
        """
        creates a hash over the resource

        Returns
        -------
        hashname(str):
            sha256 hash over the content of the resource-file
        """
        # print(self.path)
        BLOCK_SIZE = 65536  # 64 kb
        file_hash = hashlib.sha256()
        if self.type == "numpy":
            content = self.getContent()
            file_hash.update(content.data)
            hashname = file_hash.hexdigest()
        elif self.type is "dir":
            # maybe needs more excludes
            hashname = dirhash(
                self.path, "sha256", excluded_extensions=["pyc"]
            )
            return hashname
        else:
            with open(self.path, "rb") as f:
                fblock = f.read(BLOCK_SIZE)
                while len(fblock) > 0:
                    file_hash.update(fblock)
                    fblock = f.read(BLOCK_SIZE)

            hashname = file_hash.hexdigest()
        # print("hashname of ressource: " + hashname)
        return hashname

    def getContent(self):
        """
        this function returns the correct data type, if the ressource
        isn't of type python-file
        """
        if self.type == "numpy":
            data = np.load(self.path)
            copy = np.copy(data)
            np.save(self.path, data)
            # print("es ist wieder da: " + str(os.path.islink(self.path)))
            return copy
        elif self.type is "dir":
            pass
        else:
            print("I've no idea")

    def __str__(self):
        # just for debugging purposes
        return f"this item is a ressource with path {self.path}"
