import chefkoch


class Worker:
    def __init__(self, scheduler):
        self.scheduler = scheduler


class Scheduler:
    """
    Responsible for scheduling the single jobs to fulfill
    th plan.
    """

    def __init__(self, plan):
        # self.chef = chef
        self.plan = plan
        self.plan.completeJoblist()

    def update(self):
        """
        update current status of scheduler
        """
        pass
