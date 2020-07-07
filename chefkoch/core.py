"""
Starts and controls the main functionality of Chefkoch.
It is also responsible for logging everything.
"""

import chefkoch.fridge as fridge
import chefkoch.scheduler as scheduler
# from scheduler import Scheduler
# import recipe
# from recipe import Recipe
from chefkoch.container import YAMLContainer
import ast


class Logger:
    """
    creates a logfile
    """

    def __init__(self, filename):
        """
        Create a logfile and use this container for logging.

        Parameters
        ----------
        filename(string):
            name of logfile

        """
        pass

    def log(self, level, message, *objects):
        """
        Creates a log entry

        Parameters
        ----------
        level(int):
            type and importance of log-message

        message(string):
            log-message

        objects():
            describes the used objects
        """
        pass


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
        return this.items[keyname]

    def __init__(self, filename, arguments):
        """
        Load of configuration of specified in cheffile

        Parameters
        ----------
        filename(string):
            file, that specifies configuration
        """
        self.file = YAMLContainer(filename)
        self.items = dict()
        self.items["options"] = self.file.data
        if (arguments['option'] is not None):
            for x in arguments["option"]:
                x = x.split("=")
                self.items["options"][x[0]] = ast.literal_eval(x[1])
        print(self.items)


class Chefkoch:
    """
    main instance
    """

    def __init__(self, path, arguments):
        """
        Initializes everything according to he Cheffile and the needed
        components

        Parameters
        ----------
        path(string):
            specifies path of project directory

        """
        # aus Testzwecken sind meisten Werte mit null initialisiert
        # self.basePath = cheffile
        self.cheffile = YAMLContainer((path+"/cheffile.yml"))
        self.configuration = Configuration(self.cheffile["options"], arguments)
        self.recipe = None
        # veraltete Version mit Festlegungen für fridge und pantry
        self.fridge = fridge.Fridge(self, (path+"/fridge"), 
        (path+"/resources"))
        self.logger = None
        self.scheduler = None
        print("This is your evil overlord")

    def cook(self, *targets):
        """
        starts the cooking process

        Parameters
        ----------
        targets(str):
            things/steps that should be cooked

        """
        pass


class Name(str):
    SEPARATOR = '.'

    def __init__(self, *tokens):
        pass
