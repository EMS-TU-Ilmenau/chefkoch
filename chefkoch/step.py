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
    """

    def __init__(self):
        pass


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
