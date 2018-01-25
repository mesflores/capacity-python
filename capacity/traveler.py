"""Traveler.py -- the basic traveler class"""

class Traveler(object):
    """Traveler on the system """
    def __init__(self):
        self.start = None
        self.dest = None

    def _select_destination(self):
        """Determine where the passenget should go """
        # Ideally this should do something clever based on the start location
        # ie known trips. But for now, it will pick randomly!
