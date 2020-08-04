import chefkoch

class Worker:

    def __init__(self, scheduler):
        self.scheduler = scheduler


class Scheduler:
    """
    Responsible for scheduling the single jobs to fulfill
    th plan.
    """

    def __init__(self, chef, plan):
        self.chef = chef
        self.plan = plan

    def update():
        """
        update current status of scheduler
        """
        pass
