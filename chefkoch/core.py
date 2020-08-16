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
from chefkoch.container import JSONContainer
import ast
import chefkoch.step as step


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
        return self.items[keyname]

    def output(self, filename):
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

        # einlesen der cheffile mit Extraoptionen
        # vllt nochmal eine Read-Data-Funktion für sich wiederholenden Code
        # oder besser gliedern
        for element in self.file.data:
            # prüfe dort auch die entsprechenden options
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
        # vllt nochmal an andere Stelle speichern, aber über eine Zusatsoption
        self.output(path + "/" + "test.json")


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

        arguments(args*):
            extra configuration settings, specified in commandline

        """
        # Laden des entsprechenden Cheffiles
        if arguments["cheffile"] is not None:
            self.cheffile = YAMLContainer(arguments["cheffile"])
        else:
            self.cheffile = YAMLContainer(path + "/cheffile.yml")

        # Erstellen des entsprechenden Konfigurations-Items
        # erstmal mit path
        self.configuration = Configuration(self.cheffile, path, arguments)
        # Erstellen der passenden fridge -> Verweis zu Konfiguration
        self.fridge = fridge.Fridge(self, path)
        # legt hier die Resource-Shelfs an, mit Namen aus der Konfiguration
        print(self.configuration.items["resource"])
        # self.fridge.makeResources(self.configuration.items["resource"])
        self.recipe = None  # beinhaltet den kompletten Namen
        # alle Namen im Namespace -> konsistent
        # baut erst Flavour-Resource und step auf
        # festgelegte Stelle für Fridge, durch Config mglweiser änderbar
        self.logger = None
        self.scheduler = None
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
        pass


class Name(str):
    SEPARATOR = "."

    def __init__(self, *tokens):
        pass
