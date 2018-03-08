""" A basic normally distributed delay"""

import numpy as np

class train_delay(object):
    """ Create a normaly distributed delay value """
    def __init__(self, loc, scale):
        """Save the paramenters"""

        self.loc = loc
        self.scale = scale
        
    def generate_delay(self, source, dest):
        """Draw a value for the delay"""
        return abs(np.random.normal(self.loc, self.scale))

def instantiate(parameters):
    """Instantiation instructions"""
    return lambda: train_delay(parameters["location"],
                               parameters["scale"])
