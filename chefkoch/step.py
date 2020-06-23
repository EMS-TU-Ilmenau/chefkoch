"""
Definition of the different simulation steps available.
"""
import core
from fridge import Item


class Step(Item):
    """
    A single simulation step.
    """

    def __init__(self):
        """
        Initializes the logfile for this step and the
        name-mapping
        """
        self.logfile
        self.mapping


class StepPython(Step):
    """
    A simulation step specified in a Python-file
    """

    def __init__(self):
        pass


class StepShell(Step):
    """
    A simulation step specified in a shell-command ??
    """
    def __init__(self):
        pass


class StepSubRecipe(Step):
    """
    A simulation step where a SubRecipe is cooked
    """

    def __init__(self):
        pass
