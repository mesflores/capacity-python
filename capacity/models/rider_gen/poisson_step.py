"""A weighted poisson arrival"""

import numpy as np

def poisson_arrival(scale):
    """ Pull from exp to see next arrival time """
    return np.random.exponential(scale=scale)

class rider_gen(object):
    """Generate exponetial weights, ie poisson"""
    def __init__(self, magnitude):
        """save params"""
        self.magnitude = magnitude

    def generate_delay(self, current_tod, popularity):
        """ Generate the delay"""

        return  int(poisson_arrival(self.tod_weight(current_tod,
                                                    popularity)))

    def tod_weight(self, current_tod, popularity):
        """Check the current tod and popularity, generate accordingly"""
        magnitude = self.magnitude
        # If < 5 AM potentially wait a while
        if current_tod < 18000:
            rate = 1000
            # Ok if its early in the morning, fixed popularity, doesn't matter where you are
            return rate
        # If morning rush, small weight, ends 10Am
        elif current_tod < 40000:
            # let's try and smooth this out a little bit
            rate = magnitude * 1
        # Midday, quiet down
        elif current_tod < 61200:
            rate = magnitude * 2
        # Evening rush
        elif current_tod < 68400:
            rate = magnitude * 1
        elif current_tod < 86400:
            # Taper off to 100
            dropoff = (magnitude * 10)*((float(current_tod)- 68400)/(86400-68500))
            rate = (magnitude * 1) + dropoff
        else:
            rate = 0

        # Ok now we need to weight the value
        if popularity == 0:
            pop = .001 # epsilon?
        else:
            pop = popularity

        return float(rate)/pop

def instantiate(parameters):
    """Instantiation instructions"""
    return lambda: rider_gen(parameters["magnitude"])
