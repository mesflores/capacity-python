"""Traveler.py -- the basic traveler class"""

import logging
import random

class PassangerState(object):
    """A state machine to keep track of passanger experience"""
    def __init__(self):
        # States
        # waiting - waiting for a vehicle at a stop
        # riding - on a moving vehicle
        # transferring - moveing between two stations

        self.state = "waiting"

        self.time_waiting = []
        self.time_riding = []
        self.time_transferring = []

 

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

        # Passanger state machine
        self.state = "Waiting"
        self.time = network.env.now

        # Some statistics
        self.time_waiting = []
        self.time_riding = []

        logging.info("[%d] person at %s going to %s",
                     network.env.now, self.start, self.dest)

    def _select_destination(self):
        """Determine where the passenget should go """
        # Ideally this should do something clever based on the start location
        # ie known trips. But for now, it will pick randomly!
        station_dict = self.network.station_dict

        stations = list(station_dict.keys())
        weights = [station_dict[x].in_popularity for x in station_dict]

        # pick using the given weight distributions
        self.dest = random.choices(stations, weights=weights)[0]

        return

    def _route_to_dest(self):
        """ Determine how to get to the destination """
        # Ask the network
        self.route = self.network.determine_route(self.start, self.dest)
        # Set the index to where we are now
        self.route_index = 0

    def get_next_stop(self):
        """ Where is next? """
        return self.route[self.route_index + 1]

    def board_vehicle(self): 
        """ Record some stats marking boarding """

    def arrived(self):
        """ If you arrive at destination, log info"""
        #TODO: Collect final stats
        pass
