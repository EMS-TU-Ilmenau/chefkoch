import numpy as np


def execute(beampatternLog):
    # beampattern = np.load(beampatternLog)
    result = 10**(beampatternLog/10)
    # np.save('./beampatternLin',result)
    return {
        'result' : result
    }