"""
Definition of the different simulation steps available.
"""
import chefkoch.core
from chefkoch.item import Item
from abc import ABC, abstractmethod


class Step(Item):
    """
    A single simulation step.
    """

    def __init__(self, shelf):
        """
        Initializes the logfile for this step and the
        name-mapping
        """
        self.logfile = None
        self.mapping = None
        self.dependencies = dict()  # funktioniert das so?


class StepPython(Step):
    """
    A simulation step specified in a Python-file
    """

    def __init__(self):
        super().__init__()
        pass


class StepShell(Step):
    """
    A simulation step specified in a shell-command ??
    """

    def __init__(self):
        super().__init__()
        pass


class StepSubRecipe(Step):
    """
    A simulation step where a SubRecipe is cooked
    """

    def __init__(self):
        super().__init__()
        pass


# class StepBuiltIn(ABC, Item):
#    pass
# class StepBuiltInCollect(StepBuiltIn):
#    pass
