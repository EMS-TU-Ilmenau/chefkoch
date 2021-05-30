# import chefkoch
import threading
import multiprocessing.process
import copy
import time
from multiprocessing.pool import ThreadPool as Pool
import random

pool_size = 8


class Worker(threading.Thread):
    def __init__(self, resultitem):
        threading.Thread.__init__(self)
        # threading.
        self.status = (0, 0)
        print(self.getName(), ": Am born now")  # (not prepared, not ready)
        # self.scheduler = scheduler
        self.resultitem = resultitem
        # self.fridge
        # if self.resultitem.dependencies.data
        self.checkPrerequisites(0)

    def start(self):
        self.execute()

    def execute(self):
        self.resultitem.execute()

    def checkPrerequisites(self, t):
        if t:
            time.sleep(t)
        if self.resultitem.checkPrerequisites():
            self.status = (1, 1)  # ("prepared", "ready")
            print(self.getName(), ": updated status[1] to ready")
        else:
            self.status = (1, 0)  # ("prepared", "not ready")
            print(self.getName(), ": updated status[1] to not ready")


class Scheduler:
    """
    Responsible for scheduling the single jobs to fulfill
    th plan.
    """

    def __init__(self, plan):
        self.__update("initializing")
        self.plan = plan
        self.pool = Pool(pool_size)
        self.plan.completeJoblist()
        self.joblist = copy.copy(self.plan.joblist)
        self.prepareWorkers()
        self.status = "ready"


    def prepareWorkers(self):
        self.__update("preparing Workers")
        for priority in range(len(self.joblist) - 1, -1, -1):
            # self.joblist.append()
            for job in range(len(self.joblist[priority])):
                self.joblist[priority][job] = Worker(
                    self.joblist[priority][job][1]
                )
        for priority in self.joblist:
            for job in priority:
                self.pool.apply_async(
                    job.checkPrerequisites(random.randint(0, 0))
                )
        self.__update("ready")

    def doWork(self):
        self.__update("working")

        for priority in range(len(self.joblist), 0, -1):
            threads = []
            for job in self.joblist[priority - 1]:
                job.execute()
            print(priority, " is finished")

    def __update(self, toAssign):
        """
        update current status of scheduler
        """
        self.status = toAssign
