"""
Scheduler
"""

import chefkoch.core
import chefkoch.recipe
import chefkoch.step

class Scheduler:
    """
    Scheduler Class
    """

    def __init__(self, chef, plan):
        """
        Initialize Scheduler Object
        :param chef:
        :param plan:
        """

        self.chef = chef
        self.plan = plan

    def update(self):
        """
        Uodate current status of scheduler
        :return:
        """

class Job:
    """
    Job Class
    """

    # scheduler: Scheduler
    # step: chefkoch.step.Step

    def __init__(self):
        """
        Initialize Job Class
        """
        pass

