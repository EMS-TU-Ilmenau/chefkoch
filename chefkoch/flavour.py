# -*- coding: utf-8 -*-


r"""
The flavour file entered by the user specifies all parameters that the simulation
should be executed for and their possible values or value ranges.
The Flavour Module contains all classes and functions needed to parse a json file
into a flavour object.
"""
# classes to put recipe json data into

import os
import io
import platform
import json
# logs need to be included this way, because __name__ will be the unique name of each logger
from chefkoch.logs import *

class Flavour:
    """
    The flavour file is the collection of all paramters needed for the simulation and all
    their values the simulation should be executed with. The goal is to find the best
    parameter combination. Paramter can have a contant value, a list of values or a range.
    They can also be files.
    """
    params = []

    def __init__(self, paramlist):
        self.params = paramlist
        # Making sure that paramlist is a list of type Param


class Param:
    """
    A parameter with all values attached to it.
    """
    values = []
    file = None

    def __init__(self, name, undistinguishable_list):
        self.name = name
        self.values.append(values)
        if type is 'range':
            # get all values and append or keep object for memory reasons?
            return
        if type is 'file':
            # one value is a file path. But how do I keep this apart from a string value?
            return


# same thing as in recipe module. todo: find better way to group classes and funcs
def openjson(filename):
    """
    Opens a JSON file, makes sure it is valid JSON and the file exists
    at the given path. Loads the whole file at once. File should there-
    fore not be too big.
    Inputs:
        filename    string
    Outputs:
        data        dict or list depending on JSON structure
        err         Error message string, None if everything worked fine
    """
    if not os.path.isfile(filename):
        return (None, "The file path or file name is incorrect.")
    with open(filename) as f:
        try:
            data = json.load(f)
            # That's the whole file at once. Hope files dont get too big
        except ValueError as err:
            return (None, "This is no valid JSON file. Try deleting comments.")
        
    return (data, None)

def jsonToFlavour(data):
    """
    Turns data loaded from a json file into a flavour object.
    Inputs:
        data        dict or list depending on json file.
    Outputs:
        
    """
