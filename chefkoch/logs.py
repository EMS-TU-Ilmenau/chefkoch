# -*- coding: utf-8 -*-

r"""
Settings for logging in whole project. Include with
from logs import *
so that the code is copied into each module and the __name__ variable
references the module name. This way, each module has it's own logger.
Using the normal import would set __name__ to "logs" each time.
TODO: Explain why one logger is not sufficient.
"""
import logging

# Set up logging for everything inside this module
logger = logging.getLogger(__name__)
# this is important when importing modules
# a logger can only be configured once within a project
# so we need a new logger in each module
# __name__ is either "main" or the name of the module if imported
logger.setLevel(logging.DEBUG) 
# log levels are ascending: debug, info, warn, err, crit
# setting lvl to debug basically says log everything
# logging.basicConfig configues the root Looger. Never share root Logger.

formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(lineno)d:%(message)s')

file_handler = logging.FileHandler('test.log')
file_handler.setLevel(logging.ERROR) # only write logs that are error or worse
file_handler.setFormatter(formatter)

# to output errs and warns into file, but debug to console, do:
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
# no lvl specified -> print every log to console

logger.addHandler(file_handler)
logger.addHandler(stream_handler)