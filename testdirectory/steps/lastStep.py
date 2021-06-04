import numpy as np

def execute(data, multiplier):
    # beampattern = np.load(beampatternLog)
    result = np.sum(data) * multiplier
    # np.save('./beampatternLin',result)
    return {
        'result' : result
    }