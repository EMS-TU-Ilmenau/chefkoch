"""
Definition of the different simulation steps available.
"""
import chefkoch.core
from chefkoch.item import Item, Resource
from chefkoch.container import JSONContainer
from chefkoch.fridge import *
from abc import ABC, abstractmethod
import importlib
import inspect
import sys


class Step(Item, ABC):
    """
    A single simulation step
    """

    def __init__(self, shelf, dependencies):
        """
        Initializes the logfile for this step and the
        name-mapping
        """
        self.logfile = None
        self.mapping = dependencies
        # this will change
        super().__init__(shelf, None, JSONContainer())


class StepResource(Step, ABC):
    """
    Specifies the function to be executed inside a node in the recipe.
    """

    def __init__(self, shelf, dependencies):
        """
        Tests the step source if it is a recipe, a python executable or
        a built-in function and initialises it if so.

        Parameters
        ----------
        stepsource (str):
            file path to a sub-recipe, a python executable or the name \
            of a built-in function

        Raises
        ------
        TypeError:
            If the string does not match any of the above.
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

    def executeStep(self):
        # maybe check resource
        pass


class StepPython(StepResource):
    """
    A simulation step specified in a Python-file
    """

    def __init__(self, shelf, dependencies):
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
        super().__init__(shelf, dependencies)
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
        # will probably be useful
        super().executeStep()
        if self.found:
            print("going to execute the step")
            # getting the signature of execute
            sig = inspect.signature(self.module.execute)
            print(sig)

            calldic = {}  # initialise calldictionary
            # filling the dictionary with the specific values
            for x in sig._parameters.values():
                calldic[str(x)] = self.shelf.fridge.getItem(str(x))

            # execute the function
            result = self.module.execute(**calldic)
            print(result)
            # TODO: process result


class StepShell(StepResource):
    """
    A simulation step specified in a shell-skript
    """

    def __init__(self, path):
        pass


class StepSubRecipe(StepResource):
    """
    A simulation step where a SubRecipe is cooked
    """

    def __init__(self):
        pass


class StepBuiltIn(Item, ABC):
    pass


class StepBuiltInCollect(StepBuiltIn):
    pass
