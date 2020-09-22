"""
Definition of the different simulation steps available.
"""
import chefkoch.core
from chefkoch.item import Item
from abc import ABC, abstractmethod


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
        self.dependencies = dict()


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

    def __init__(self):
        pass


class StepShell(StepResource):
    """
    A simulation step specified in a shell-command ??
    """

    def __init__(self):
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
