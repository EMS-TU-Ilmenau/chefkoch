"""
Definition of the different simulation steps available.
"""
import chefkoch.core
from chefkoch.item import Item
from chefkoch.container import JSONContainer
from abc import ABC, abstractmethod
import inspect


class Step(Item, ABC):
    """
    A single simulation step
    """

    @abstractmethod
    def __init__(self, shelf):
        """
        Initializes the logfile for this step and the
        name-mapping
        """
        self.logfile = None
        self.mapping = None
        self.dependencies = JSONContainer()


class StepResource(Step, ABC):
    """
    Specifies the function to be executed inside a node in the recipe.
    """

    """
    def __init__(self, stepsource):
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

        # testing if step is built-in; JSON file or python function
        extension = os.path.splitext(stepsource)[1]
        if extension == ".py":
            self.step = stepsource
        elif extension == ".json":
            self.step = stepsource
        elif str(stepsource) in BUILT_INS:
            self.step = stepsource
            # done: research on assigning functions as attributes
            # (so that it can be accessed no matter where the object
            # is used)
        else:
            raise TypeError(
                "Stepsource : "
                + str(stepsource)
                + ". Must be a Python file, another recipe "
                + "or a build-in function."
    """


class StepPython(StepResource):
    """
    A simulation step specified in a Python-file
    """

    def __init__(self, path):
        """
        initializes a Python-Step

        Parameters
        ----------
        path(str):
            path to the python-module
        """
        # prototype implementation
        mod_name, file_ext = os.path.splitext(os.path.split(path)[-1])
        # importing correct module
        test = importlib.__import__(mod_name)
        print(mod_name)
        list = inspect.getmembers(test, predicate=inspect.isfunction)

        # aktuell nur für Korrektur
        found = False
        for p in list:
            if p[0] == "execute":
                found = True

        if found:
            print("able to execute")
            # getting the signature
            # how to get the correct parameters?
            # example dic
            dic = {"a": 10, "b": 20}
            calldic = {}
            # filling the dictionary with the specific values
            for x in sig.parameteres.values():
                # let's call it dic for now
                calldic[str(x)] = dic[str(x)]

            # not sure if executing should be a different option
            # if it is done later
            test.execute(**calldic)
        else:
            warnings.warn("There is no execute in this module: " + path)


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
