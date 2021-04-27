# import chefkoch
import threading
import copy


class Worker:
    def __init__(self, resultitem):
        # self.scheduler = scheduler
        self.resultitem = resultitem
        # self.fridge
        # if self.resultitem.dependencies.data
        if self.resultitem.checkPrerequisites():
            self.status = ("prepared", "ready")
        else:
            self.status = ("prepared", "not ready")

    def execute(self):
        self.resultitem.execute()

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
        self.plan.completeJoblist()
        self.joblist = copy.copy(self.plan.joblist)   # self.plan.joblist
        self.prepareWorkers()
        self.status = "ready"

        # self.__update("working")
        # pass

    def prepareWorkers(self):
        self.__update("preparing Workers")
        for priority in range(len(self.joblist)):
            # self.joblist.append()
            for job in range(len(self.joblist[priority])):
                # self.joblist.append(threading.Thread(target=Worker(job[1])))
                # job.append(threading.Thread(target=Worker(job[1])))
                self.joblist[priority][job] = \
                    threading.Thread(
                        target=Worker(
                            self.joblist[priority][job][1]))
        # self.__update("ready")
        pass

    def doWork(self):
        self.__update("working")


    def __update(self, toAssign):
        """
        update current status of scheduler
        """
        self.status = toAssign
