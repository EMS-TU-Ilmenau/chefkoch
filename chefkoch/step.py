"""
Definition of the different simulation steps available.
They are derived from items.
"""
from chefkoch.item import Item, Resource, Result
from chefkoch.container import JSONContainer
from abc import ABC, abstractmethod

import os
import importlib
import inspect
import types
import subprocess
import shlex

# finding imported modules -> dependencies
# try:
#     import builtins
# except ImportError:
#     import __builtin__ as builtins
#
# def get_builtins():
#     a = builtins
#     return list(filter(lambda x: not x.startswith('_'), a))
#
# primitive2 = (int, float, str, bool, list, dict, set, object,  )
# primitive = get_builtins()


class Step(Item, ABC):
    """
    The abstract base class of the different simulation steps.
    It is also derived from Item.
    """

    def __init__(self, shelf):
        """
        Initializes the logfile for this step and the
        name-mapping.

        Parameters
        ----------
        shelf(Shelf):
            the shelf the item belongs to
        """
        # this will change
        super().__init__(shelf, None, JSONContainer())


class StepResource(Step, ABC):
    """
    Abstract class for steps depending on resources
    """

    def __init__(self, shelf, logger):
        """
        Initliazes the step

        Parameters
        ----------
        shelf (Shelf):
            contains the shelf, which the step belongs to

        logger(Logger):
            logger-class to get a module-specific logger

        """
        super().__init__(shelf)

        # ich bin mir nicht sicher, ob das von Nöten ist
        # get the correct item from the shelf
        for x in shelf.items:
            if isinstance(shelf.items[x], Resource):
                self.resource = shelf.items[x]
                break

        # logging
        self.logger = logger.logspec(
            shelf.name, shelf.path + "/" + shelf.name + ".log"
        )

    # def executeStep(self):
    #     # maybe check resource
    #     pass


class StepPython(StepResource):
    """
    A simulation step specified in a Python-file
    """

    def __init__(self, shelf, logger):
        # steps bekommen keine depencies
        """
        initializes a Python-Step

        Parameters
        ----------
        shelf(str):
            shelf of the specific step
            will probably changed, that the step gets its
            resource directly from the fridge

        logger(Logger):
            main Logger-class
        """
        # prototype implementation
        super().__init__(shelf, logger)
        self.logger.info("STEP_(" + shelf.name + "): This might work")
        # read the module-name
        mod_name, file_ext = os.path.splitext(
            os.path.split(self.resource.path)[-1]
        )
        # importing correct module
        print(mod_name)
        try:
            self.module = importlib.__import__(mod_name)
        except ImportError as err:
            self.logger.error("STEP_(" + shelf.name + "): ", err)

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
            self.logger.critical(
                "STEP_(" + shelf.name + "): There is no execute"
            )
        self.map = {}
            # raise Exception("There is no execute in " + str(mod_name))

    def executeStep(self, dependencies):
        # Parameter zum Berechnen müssen übergeben
        """
        executes this python-step
        """
        # super().executeStep()
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
                # a = list(self.map.keys())
                if str(x) in self.map.keys():
                    y = self.map[str(x)]
                    itemHash = dependencies.data["inputs"][y].split("/")[1]
                    shelf = self.shelf.fridge.getShelf(y)
                    item = shelf.items[itemHash].result["result"]
                else:
                    # y = x
                    # if str(x) == "z":
                    #     print("str(x) == \"z\"")
                    item = dependencies.data["inputs"][str(x)]

                # if str(x) == "beampatternLog":
                #     print("str(x) == beampatternLog")
                # item = self.shelf.fridge.getItem(str(y))
                if hasattr(item, "type"):
                # if item.type == "numpy":
                    calldic[str(x)] = item.getContent()
                # elif isinstance(item, types.BuiltinFunctionType):
                #     pass
                else:
                    calldic[str(x)] = item


            # execute the function
            ret = self.module.execute(**calldic)
            # if type(ret) == dict:
            #     print(ret)
            return ret
            # das result muss in den ouput-Shelf!
            # result = Result(self.shelf, r, JSONContainer(data={}))
            # correct behaivour, bit still missing the outputs
            # shelf = self.shelf.fridge.getShelf(self.dependencies["outputs"])
            # shelf.addItem(result)
            # self.shelf.addItem(result)

        else:
            raise Exception(
                "Can't execute "
                + str(self.shelf.name)
                + " there is no execute"
            )

    def addMap(self, map):
        self.map = map


class StepShell(StepResource):
    """
    A simulation step specified in a shell-skript
    """

    def __init__(self, shelf, logger):
        """
        initializes the Shell-Step
        """
        super().__inti__(shelf, logger)
        # get the correct path from the resource
        self.script = self.resource.path

    def executeStep(self):
        """
        executes this shell-step
        """
        super().executeStep()
        # vielleicht
        """
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
        """


class StepSubRecipe(StepResource):
    """
    A simulation step where a SubRecipe is cooked
    """

    def __init__(self, shelf, logger):
        super().__init__(shelf, logger)
        # inputs-> just check if they are there
        pass


class StepBuiltIn(Item, ABC):
    pass


class StepBuiltInCollect(StepBuiltIn):
    pass
