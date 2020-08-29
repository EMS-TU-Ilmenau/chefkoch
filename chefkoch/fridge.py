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
        if self.chef.configuration["options"]["directory"]:
            if not os.path.exists(path):
                os.makedirs(path)
            else:
                warnings.warn("there already exists a directory: " + path)

    def makeRessources(self, Ressources):
        """
        initialises the Ressources
        """
        for element in Ressources:
            # FlavourShelf wird angelegt
            shelf = ItemShelf(self, element)
            self.shelfs[element] = shelf
            # dann legen wir ein Item an
            ressource = chefkoch.item.Ressource(
                self.shelfs[element], Ressources[element]
            )
            name = zlib.adler32(Ressources[element].encode("utf-8"))
            self.shelfs[element].items[name] = ressource
            print(self.shelfs[element].items)

    def makeFlavours(self, Flavours):
        """
        initializes the different flavours
        """
        # machen wir erstmal nur einen FlavourShelf
        shelf = FlavourShelf(self, "flavours")
        self.shelfs["flavours"] = shelf
        self.shelfs["flavours"].makeFullList(Flavours)


class Shelf(ABC):
    """
    Abstrakte Basis-Klasse für die unterschiedlichen shelfs
    """

    def __init__(self, fridge, name):
        self.items = dict()
        self.fridge = fridge
        self.path = fridge.basePath + "/fridge/" + str(name)
        self.fridge.makeDirectory(self.path)


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
    def ranges(self, f):
        if f["type"] == "lin":
            vals = numpy.arange(f["start"], f["stop"]+1, f["step"])
            return vals
        elif f["type"] == "log":
            if "base" in f:
                base = f["base"]
            else:
                base = 10

            start = math.log(ast.literal_eval(f["start"]), base)
            stop = math.log(ast.literal_eval(f["stop"]), base)
            vals = numpy.logspace(start, stop, num=f["count"])
            return vals

    def makeFullList(self, Flavours):
        for x in Flavours:
            if isinstance(Flavours[x], list):
                if (isinstance(Flavours[x][0], dict)):
                    vals = []
                    for elem in Flavours[x]:
                        vals.append(self.ranges(elem))
                    self.items[x] = vals
                else:
                    self.items[x] = Flavours[x]

            elif isinstance(Flavours[x], dict):
                print("difficult")
                vals = []
                f = Flavours[x]
                self.items[x] = self.ranges(f)
        print(self.items)
