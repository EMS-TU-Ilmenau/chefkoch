"""
Starts and controls the main functionality of Chefkoch.
It is also responsible for logging everything.
"""

import chefkoch.fridge as fridge
import chefkoch.scheduler as scheduler

# from scheduler import Scheduler
import chefkoch.recipe as recipe

# from recipe import Recipe
from chefkoch.container import YAMLContainer
from chefkoch.container import JSONContainer
import ast
import chefkoch.step as step

# das ist eine bezaubernde Idee
import os
import sys
import logging
import warnings


class Whitelist(logging.Filter):
    def __init__(self, *whitelist):
        self.whitelist = [logging.Filter(name) for name in whitelist]

    def filter(self, record):
        return any(f.filter(record) for f in self.whitelist)


class Logger:
    """
    creates a logfile
    """

    formatter = "%(asctime)s - %(levelname)s - %(message)s"

    def __init__(self, options, path):
        """
        creates the basic logger which can be called from all instances
        If the directory-options is set to false, there will be only
        one log-file which collects all logging-information

        Parameters
        ----------
        options(dic):
            options specified in configuration
        """
        # too look up the options later
        self.options = options
        # main path
        self.path = path

        # standard initialzing
        filepath = self.path + "/chef.log"

        if self.options["directory"]:
            if os.path.isfile(filepath):
                os.remove(filepath)

            handlerFile = logging.FileHandler(filename=filepath, mode="a")
            handlerFile.addFilter(Whitelist("chefkoch.core", "chefkoch.fridge"))
        else:
            handlerFile = logging.FileHandler(filename=filepath, mode="w")
        console = logging.StreamHandler()
        logging.basicConfig(
            format=Logger.formatter,
            level=Logger.loglevel(self, self.options["logLevel"]),
            handlers=[handlerFile, console],
        )

    def logspec(self, name, filename):
        """
        specifies the logs for the different steps
        wird später nochmal etwas überarbeitet

        Parameters
        ----------
        name(str):
            the name of this logger
        filename(str):
            filepath to this particular log-file
        """
        print(name)
        if self.options["directory"]:
            logger = logging.getLogger(name)

            if name in ["chefkoch.core", "chefkoch.fridge"]:
                return logger
            else:
                handler = logging.FileHandler(filename, mode="w")
                form = logging.Formatter(Logger.formatter)
                handler.setFormatter(form)
                # this will be later changed according to the options
                # Logger.loglevel(self, handler, self.options["logLevel"])

                # we will need a correct working filter
                filter_test = logging.Filter(name=str(name))
                handler.addFilter(filter_test)
                logger.addHandler(handler)
                return logger
        else:
            newLogger = logging.getLogger("main")
            return newLogger

    def loglevel(self, level):
        """
        Hilfsfunktion um ein bestimmtes loglevel zu setzen
        vllt geht das schöner
        könnte man später noch nach main Logger und file-loggers differenzieren
        """
        if level == "INFO":
            return logging.INFO
        elif level == "DEBUG":
            return logging.DEBUG
        elif level == "WARNING":
            return logging.WARNING
        elif level == "ERROR":
            return logging.ERROR
        elif level == "CRITICAL":
            return logging.CRITICAL
        else:
            # raise an error here
            print("Something is rotten in the state of denmark")
        # return handler


class Configuration:
    """
    Manages the configurations specified in the configuration file
    """

    def __getitem__(self, keyname):
        """
        Retrieve a configuration item

        Returns
        -------
        returns:
            configuration item
        """
        return self.items[keyname]

    def output(self, filename):
        if self.items["options"]["configOut"]:
            container = JSONContainer()
            container.data = self.items
            container.save(filename)

    def __init__(self, container, path, arguments):
        """
        Load of configuration of specified in cheffile

        Parameters
        ----------
        filename(string):
            file, that specifies configuration
        """
        self.file = container

        self.items = dict()
        # TODO: Standardinitialisierungen

        # import cheffile with extra-options
        # vllt nochmal eine Read-Data-Funktion für sich wiederholenden Code
        # oder besser gliedern
        for element in self.file.data:
            # checking for the options
            if arguments[element] is not None:
                if element == "options":
                    # options extra eingeladen, um sie zu überschreiben
                    if ".yml" in self.file.data[element]:
                        help = YAMLContainer(path + self.file.data[element])
                        self.items[element] = help.data
                    else:
                        self.items[element] = self.file.data["options"]

                    for x in arguments["options"]:
                        x = x.split("=")
                        self.items[element][x[0]] = ast.literal_eval(x[1])
                else:
                    # filepath für Alternatives yml
                    # muss nochmal schöner aufgeteilt werden
                    help = YAMLContainer(path + self.file.data[element])
                    self.items[element] = help.data
            else:
                if ".yml" in self.file.data[element]:
                    help = YAMLContainer(path + self.file.data[element])
                    self.items[element] = help.data
                else:
                    self.items[element] = self.file.data[element]
        # adding target if existing
        if arguments["targets"] is None:
            self.items["targets"] = "all"
        else:
            self.items["targets"] = arguments["targets"]
        # vllt nochmal an andere Stelle speichern, aber über eine Zusatsoption
        self.output(path + "/" + "Configtest.json")


class Chefkoch:
    """
    main instance
    """

    def __init__(self, firstpath, arguments):
        """
        Initializes everything according to he Cheffile and the needed
        components

        Parameters
        ----------
        path(string):
            specifies path of project directory

        arguments(args*):
            extra configuration settings, specified in commandline

        """
        # loading the correct path
        path = os.path.abspath(firstpath)
        sys.path.append(str(path) + "/steps/")
        # loading the cheffile
        if arguments["cheffile"] is not None:
            self.cheffile = YAMLContainer(arguments["cheffile"])
        else:
            self.cheffile = YAMLContainer(path + "/cheffile.yml")
        # generate the configuration-item
        # using the path to main directory
        self.configuration = Configuration(self.cheffile, path, arguments)

        # cheffile legt noch Änderungen an logger fest
        self.logger = Logger(self.configuration["options"], path)
        corelogger = self.logger.logspec(__name__, path + "/chef.log")
        corelogger.warn("CHEF: " + "This is maybe a bad idea!")

        # generate the fridge
        self.fridge = fridge.Fridge(self.configuration, path, self.logger)

        # generate Resource-Shelfs from configuration
        # print(self.configuration.items["resource"])
        self.fridge.makeResources(self.configuration.items["resource"], False)

        # generate the flavour-shelf
        # print(self.configuration.items["flavour"])
        self.fridge.makeFlavours(self.configuration.items["flavour"])

        # dealing with configuration.recipe
        # print(self.configuration.items["recipe"])
        self.fridge.makeResources(self.configuration.items["recipe"], True)

        # print(type(self.configuration.items["recipe"]))
        # self.recipe = recipe.readrecipe(self.configuration.items["recipe"])
        # beinhaltet den kompletten Namen
        # alle Namen im Namespace -> konsistent
        # baut erst Flavour-Resource und step auf

        # testing from the steps
        teststep = step.StepPython(
            self.fridge.shelves["compute_a"],
            {},
            self.logger,
        )
        teststep.executeStep()

        teststep = step.StepPython(
            self.fridge.shelves["anotherStep"],
            {},
            self.logger,
        )
        teststep.executeStep()

        print("This is your evil overlord")
        print("(͠≖ ͜ʖ͠≖)👌")

    def cook(self, *targets):
        """
        starts the cooking process

        Parameters
        ----------
        targets(str):
            things/steps that should be cooked

        """
        self.Plan = None
        # output-shelfs
        self.scheduler = None
        pass
