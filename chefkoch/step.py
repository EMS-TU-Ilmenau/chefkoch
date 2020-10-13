"""
Definition of the different simulation steps available.
"""
import chefkoch.core
from chefkoch.item import Item
from chefkoch.container import JSONContainer
from chefkoch.fridge import *
from abc import ABC, abstractmethod
import inspect


class Step(Item, ABC):
    """
    A single simulation step
    """

    @abstractmethod
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

    @abstractmethod
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
        # self.resource = step

        # einmal ein wahrscheinlich unnötiger check
        if isinstance(shelf, FlavourShelf):
            raise Exception("can't get Ressources from a flavourshelf!")

        # ich bin mir nicht sicher, ob das von Nöten ist
        for x in shelf.items:
            if isinstance(x, Resource):
                self.resource = x
                break

    @abstractmethod
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
        # this will be changed a bit, bc we use the path of the resource
        mod_name, file_ext = os.path.splitext(
            os.path.split(self.resource.path)[-1]
        )
        # importing correct module
        self.module = importlib.__import__(mod_name)
        print(mod_name)
        functionlist = inspect.getmembers(
            self.module, predicate=inspect.isfunction
        )

        # aktuell nur für Korrektur
        self.found = False
        for p in functionlist:
            if p[0] == "execute":
                self.found = True

        if self.found is False:
            raise Exception("There is no execute in " + str(mod_name))

    def executeStep():
        if self.found:
            print("going to execute the step")
            # getting the signature
            # how to get the correct parameters?
            # with self.shelf.fridge
            # example dic
            # dic = {"a": 10, "b": 20}
            calldic = {}
            # filling the dictionary with the specific values
            for x in sig.parameteres.values():
                # let's call it dic for now
                # calldic[str(x)] = dic[str(x)]
                calldic[str(x)] = self.shelf.fridge.getItem(str(x))

            # not sure if executing should be a different option
            # if it is done later
            result = self.module.execute(**calldic)


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
