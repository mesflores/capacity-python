"""A constant value boarding delay"""

class boarding_delay(object):
    """Return a constant value"""
    def __init__(self, value):
        """save params"""
        self.value = value

    def generate_delay(self, location):
        """Return the value, ignore location"""
        return self.value

def instantiate(parameters):
    """Instantiation instructions"""
    return lambda: boarding_delay(parameters["value"])
