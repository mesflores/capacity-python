"""A constant value alighting delay"""

class alighting_delay(object):
    """Return a constant value"""
    def __init__(self, value):
        """save params"""
        self.value = value

    def generate_delay(self, location, riders):
        """Return the value, ignore location, riders"""
        return self.value

def instantiate(parameters):
    """Instantiation instructions"""
    return lambda: alighting_delay(parameters["value"])
