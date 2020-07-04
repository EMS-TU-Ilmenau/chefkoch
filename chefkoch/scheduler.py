import chefkoch


class Job:
    """
    A job which represents the execution of a step.
    It is scheduled by the scheduler
    """
    def __init__(self, scheduler, step):
        self.scheduler = scheduler
        self.setp = step


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
