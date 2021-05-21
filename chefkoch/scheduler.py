# import chefkoch
import threading
import multiprocessing.process
import copy
import time
from multiprocessing.pool import ThreadPool as Pool
from concurrent.futures import ThreadPoolExecutor
import random
import multiprocessing

pool_size = multiprocessing.cpu_count()

class TWorker(threading.Thread):
    def __init__(self, resultitem):
        threading.Thread.__init__(self)
        # threading.
        # super.__init__(self)
        self.status = (0, 0)
        print(self.getName(), ": Am born now")   # (not prepared, not ready)
        # self.scheduler = scheduler
        self.resultitem = resultitem
        # self.fridge
        # if self.resultitem.dependencies.data
        self.checkPrerequisites(0)

    def run(self):
        # super.run()
        # threading.Thread.
        # self.checkPrerequisites(2)
        self.resultitem.execute()

    def execute(self):
        self.resultitem.execute()

    def checkPrerequisites(self, t):
        if t:
            time.sleep(t)
        if self.resultitem.checkPrerequisites():
            self.status = (1, 1)    # ("prepared", "ready")
            print(self.getName(), ": updated status[1] to ready")
        else:
            self.status = (1, 0)    # ("prepared", "not ready")
            print(self.getName(), ": updated status[1] to not ready")


class Worker():
    def __init__(self, resultitem):
        # threading.Thread.__init__(self)
        # threading.
        self.status = (0, 0)
        print(self.getName(), ": Am born now")   # (not prepared, not ready)
        # self.scheduler = scheduler
        self.resultitem = resultitem
        # self.fridge
        # if self.resultitem.dependencies.data
        self.checkPrerequisites(0)


    def execute(self):
        self.resultitem.execute()

    def checkPrerequisites(self, t):
        if t:
            time.sleep(t)
        if self.resultitem.checkPrerequisites():
            self.status = (1, 1)    # ("prepared", "ready")
            print(self.getName(), ": updated status[1] to ready")
        else:
            self.status = (1, 0)    # ("prepared", "not ready")
            print(self.getName(), ": updated status[1] to not ready")

    # class PWorker(multiprocessing.process):
    #     def __init__(self, resultitem):
    #         # threading.Thread.__init__(self)
    #         # multiprocessing.process
    #         # threading.
    #         self.status = (0, 0)
    #         print(self.getName(), ": Am born now")  # (not prepared, not ready)
    #         # self.scheduler = scheduler
    #         self.resultitem = resultitem
    #         # self.fridge
    #         # if self.resultitem.dependencies.data
    #         self.checkPrerequisites(0)
    #
    #     def execute(self):
    #         self.resultitem.execute()
    #
    #     def checkPrerequisites(self, t):
    #         if t:
    #             time.sleep(t)
    #         if self.resultitem.checkPrerequisites():
    #             self.status = (1, 1)  # ("prepared", "ready")
    #             print(self.getName(), ": updated status[1] to ready")
    #         else:
    #             self.status = (1, 0)  # ("prepared", "not ready")
    #             print(self.getName(), ": updated status[1] to not ready")

    # def checkPrerequisites(self):
    #     if len(self.resultitem.dependencies.data["inputs"]) > 0:
    #         for item in self.resultitem.dependencies.data["inputs"][0].items():
    #             pass
    #     pass

    # def checkItem(self, item):


class Scheduler:
    """
    Responsible for scheduling the single jobs to fulfill
    th plan.
    """

    def __init__(self, plan):
        self.__update("initializing")
        self.plan = plan
        self.pool = Pool(pool_size)
        self.exe = ThreadPoolExecutor(max_workers=pool_size)
        self.plan.completeJoblist()
        self.joblist = copy.copy(self.plan.joblist)   # self.plan.joblist
        self.prepareWorkers()
        self.status = "ready"
        self.actPriority = -1

        # self.__update("working")
        # pass

    def prepareWorkers(self):
        self.__update("preparing Workers")
        self.actPriority = len(self.joblist) - 1
        for priority in range(len(self.joblist) - 1, -1, -1):
            # self.joblist.append()
            for job in range(len(self.joblist[priority])):
                # self.joblist.append(threading.Thread(target=Worker(job[1])))
                # job.append(threading.Thread(target=Worker(job[1])))
                self.joblist[priority][job] = TWorker(self.joblist[priority][job][1])
                # Worker(self.joblist[priority][job][1]))
        # for priority in self.joblist:
        #     # self.pool.
        #     for job in priority:
        #         # job.
        #         self.pool.apply_async(job.checkPrerequisites(random.randint(0,3)))
                # pool.applyjob.checkPrerequisites()
                # job.checkPrerequisites()
        self.__update("ready")

    def doWork(self):
        self.__update("working")
        start = time.time()
        # for priority in range(len(self.joblist), 0, -1):
        #     threads = []
        #     for job in self.joblist[priority-1]:
        #         # thread =
        #         threads.append(threading.Thread(target=job.checkPrerequisites(1)))
        #     for t in threads:
        #         t.start()
        #     for t in threads:
        #         t.join()

        for priority in range(len(self.joblist), 0, -1):
            threads = []
            for job in self.joblist[priority-1]:
                job.start()
                threads.append(job)
            for t in threads:
                t.join()
            print(priority, " is finished")
            pass

        pass
            # futures = []
            # for i in self.joblist[priority-1]:
            #     pass
            # self.pool.
            # while len(self.joblist[priority-1]) > 0:
            #     job = iter(self.joblist[priority-1])
            #     x = next(job)
            #     x.run()




    def __update(self, toAssign):
        """
        update current status of scheduler
        """
        self.status = toAssign
