import numpy as np


def execute(beampatternLog):
    beampattern = np.load(beampatternLog)
    result = 10**(beampattern/10)
    # np.save('./beampatternLin',result)
    return result
