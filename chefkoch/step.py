"""
Definition of the different simulation steps available.
"""
from chefkoch.item import Item, Resource, Result
from chefkoch.container import JSONContainer
from chefkoch.fridge import *
from abc import ABC, abstractmethod

# wenn ich das zum Loggen brauche
import chefkoch.core

# alternative
import logging

import importlib
import inspect
import subprocess
import shlex


class Step(Item, ABC):
    """
    A single simulation step
    """

    def __init__(self, shelf, dependencies):
        """
        Initializes the logfile for this step and the
        name-mapping
        """
        self.mapping = dependencies
        # this will change
        super().__init__(shelf, None, JSONContainer())
        """
        self.logfile = chefkoch.core.Logger(
            __name__, self.shelf.path + "/step.log"
        )
        self.logfile.log.debug(
            f"This is a debug message with dependencies {self.mapping}"
        )
        """


class StepResource(Step, ABC):
    """
    Abstract class for steps depending on resources
    """

    def __init__(self, shelf, dependencies, logger):
        """
        Initliazes the step

        Parameters
        ----------
        shelf (Shelf):
            contains the shelf, which the step belongs to

        dependencies(dict):
            contains all dependencies, which were needed to create the step

        """
        super().__init__(shelf, dependencies)

        # check if it is an Itemshelf
        if isinstance(shelf, FlavourShelf):
            raise Exception("can't get Ressources from a flavourshelf!")

        # ich bin mir nicht sicher, ob das von Nöten ist
        # get the correct item from the shelf
        for x in shelf.items:
            if isinstance(shelf.items[x], Resource):
                self.resource = shelf.items[x]
                break

        self.logger = logger.logspec(
            shelf.name, shelf.path + "/" + shelf.name + ".log"
        )

    def executeStep(self):
        # maybe check resource
        pass

    def createLogger(self):
        # can change the path later
        print(self.shelf.path + "/step.log")
        pass


class StepPython(StepResource):
    """
    A simulation step specified in a Python-file
    """

    def __init__(self, shelf, dependencies, logger):
        """
        initializes a Python-Step

        Parameters
        ----------
        shelf(str):
            shelf of the specific step
            will probably changed, that the step gets its
            resource directly from the fridge
        dependencies(dict):
            inputs and ouptuts of this step
        """
        # prototype implementation
        super().__init__(shelf, dependencies, logger)
        # self.logger.warn("This might work")
        # read the module-name
        mod_name, file_ext = os.path.splitext(
            os.path.split(self.resource.path)[-1]
        )
        # importing correct module
        try:
            self.module = importlib.__import__(mod_name)
        except ImportError as err:
            print("Error:", err)

        print(mod_name)
        # get all function-names
        functionlist = inspect.getmembers(
            self.module, predicate=inspect.isfunction
        )

        # check if the "execute"-Function exists
        self.found = False
        for p in functionlist:
            if p[0] == "execute":
                self.found = True

        # else raise exception
        if self.found is False:
            raise Exception("There is no execute in " + str(mod_name))

    def executeStep(self):
        super().executeStep()
        if self.found:
            print("going to execute the step")
            # getting the signature of execute
            sig = inspect.signature(self.module.execute)
            # print(sig)

            calldic = {}  # initialise calldictionary
            # filling the dictionary with the specific values
            # should test if it's a flavour shelf (than everything is allright)
            # or if it's an Itemshelf -> then we need the result-Item
            for x in sig._parameters.values():
                calldic[str(x)] = self.shelf.fridge.getItem(str(x))

            # execute the function
            r = self.module.execute(**calldic)
            # print(r)
            # das muss aber noch ordentlich in den shelf eingeordnet werden
            # result_hash als namen, aber irgendwie auch doof?
            # das result muss in den ouput-Shelf!
            result = Result(self.shelf, r)
            # correct behaivour, bit still missing the outputs
            # shelf = self.shelf.fridge.getShelf(self.dependencies["outputs"])
            # shelf.addItem(result)
            self.shelf.addItem(result)


class StepShell(StepResource):
    """
    A simulation step specified in a shell-skript
    """

    def __init__(self, shelf, dependencies, logger):
        super().__inti__(shelf, dependencies, logger)
        # get the correct path from the resource
        self.script = self.resource.path

    def executeStep(self):
        super().executeStep()
        # vielleicht
        self.ins = ""
        for x in dependencies["inputs"]:
            self.ins = ins + " "
            self.ins = ins + str(self.shelf.fridge.getItem(str(x)))

        script = self.resource.path
        subprocess.call(shlex.split(self.script + self.ins))
        # TODO: Result im Output-Ordner suchen
        # von dependencies den output bekommen
        output = self.dependencies["output"]
        # und dann über fridge-getItem das korrekte Item holen
        # wenn es denn in dem shelf gelanden ist
        # das braucht nochmal extra Spezifikation
        # so funktioniert das noch nicht
        result = Result(self.path, self.shelf.fridge.getItem(str(output)))
        self.shelf.addItem(result)


class StepSubRecipe(StepResource):
    """
    A simulation step where a SubRecipe is cooked
    """

    def __init__(self, shelf, dependencies, logger):
        super().__init__(shelf, dependencies, logger)
        # inputs-> just check if they are there
        pass


class StepBuiltIn(Item, ABC):
    pass


class StepBuiltInCollect(StepBuiltIn):
    pass
