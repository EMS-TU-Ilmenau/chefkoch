# import chefkoch
import threading
import multiprocessing.process
import copy
import time
from multiprocessing.pool import ThreadPool as Pool

pool_size = 8


class Worker(threading.Thread):
    """
    Executive abstraction of a job
    """

    def __init__(self, resultitem):
        """
        initializes the worker

        Parameters
        ----------
        resultitem(item.result)
            associated resultitem to the job

        """
        threading.Thread.__init__(self)
        self.status = (0, 0)
        # (not prepared, not executable)
        # print(self.getName(), ": Am born now")
        self.resultitem = resultitem
        self.checkPrerequisites()

    def start(self):
        """
        executes this job
        """
        self.resultitem.execute()

    def checkPrerequisites(self):
        """
        calls resultitems checkPrerequisites and sets own status accordingly
        """
        if self.resultitem.checkPrerequisites():
            self.status = (1, 1)  # ("prepared", "executable")
            # print(self.getName(), ": updated status[1] to executable")
        else:
            self.status = (1, 0)  # ("prepared", "not executable")
            # print(self.getName(), ": updated status[1] to not executable")


class Scheduler:
    """
    Responsible for scheduling the single jobs to fulfill
    the plan.
    """

    def __init__(self, plan):
        """
        initializes the scheduler object

        Parameters
        ----------
        plan(recipe.plan):
            plan object which is to be executed

        """
        self.__update("initializing")
        self.plan = plan
        self.pool = Pool(pool_size)
        self.plan.completeJoblist()
        self.joblist = copy.copy(self.plan.joblist)
        self.prepareWorkers()
        self.status = "initializing finished"

    def prepareWorkers(self):
        """
        Updates the items of self.joblist from holding
        step name [0] and resultItem [1] to hold a worker Object
        """
        self.__update("preparing Workers")
        for priority in range(len(self.joblist) - 1, -1, -1):
            # self.joblist.append()
            for job in range(len(self.joblist[priority])):
                self.joblist[priority][job] = Worker(
                    self.joblist[priority][job][1]
                )
        for priority in self.joblist:
            for job in priority:
                self.pool.apply_async(job.checkPrerequisites())
        self.__update("ready")

    def doWork(self):
        """
        start execution (the cooking process)
        """
        self.__update("working")

        for priority in range(len(self.joblist), 0, -1):
            for job in self.joblist[priority - 1]:
                job.start()

    def __update(self, toAssign):
        """
        update current status of scheduler
        """
        self.status = toAssign
