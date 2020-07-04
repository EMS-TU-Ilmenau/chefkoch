"""
Starts and controls the main functionality of Chefkoch.
It is also responsible for logging everything.
"""

import fridge
import scheduler
# from scheduler import Scheduler
# import recipe
# from recipe import Recipe


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
        pass

    def __init__(self, filename):
        """
        Load of configuration of specified in cheffile

        Parameters
        ----------
        filename(string):
            file, that specifies configuration
        """
        self.items


class Chefkoch:
    """
    main instance
    """

    def __init__(self, cheffile):
        """
        Initializes everything according to he Cheffile and the needed
        components

        Parameters
        ----------
        cheffile(string):
            specifies path of cheffile

        """
        self.basePath
        self.configuration
        self.recipe
        self.fridge
        self.logger
        self.scheduler

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
