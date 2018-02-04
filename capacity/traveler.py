"""Traveler.py -- the basic traveler class"""

import logging

class Passenger(object):
    """Traveler on the system """
    def __init__(self, start, network):
        self.network = network

        # Start and destination
        self.start = start
        self.dest = None
    
        # Current location
        self.location = start

        # A list of  steps in a route and the current position in the route
        self.route = None
        self.route_index = None

        # Choose a destination
        self._select_destination()
        # Pick a route there
        self._route_to_dest()

        logging.info("[%d] person at %s going to %s",
                      network.env.now, self.start, self.dest)

    def _select_destination(self):
        """Determine where the passenget should go """
        # Ideally this should do something clever based on the start location
        # ie known trips. But for now, it will pick randomly!

        self.dest = 1 

   
    def _route_to_dest(self):
        """ Determine how to get to the destination """
        # Ask the network
        self.route = self.network.determine_route(self.start, self.dest)
        # Set the index to where we are now
        self.route_index = 0

    def get_next_stop(self):
        """ Where is next? """
        return self.route[self.route_index + 1]

    def arrived(self):
        """ If you arrive at destination, log info"""
        #TODO: Collect final stats
        pass
