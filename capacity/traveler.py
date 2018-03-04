"""Traveler.py -- the basic traveler class"""

import collections
import csv
import logging
import random

from capacity.conf import TRAVELER_STATS_FILE

class PassengerState(object):
    """A state machine to keep track of passenger experience"""
    def __init__(self, time, start, dest):
        # States
        # waiting - waiting for a vehicle at a stop
        # riding - on a moving vehicle
        # transferring - moveing between two stations

        # NOTE: maybe this doesn't need to be here, could just point up?
        self.start = start
        self.dest = dest

        self.state = "waiting"
        self.time_record = collections.defaultdict(list)
        self.time = time

    def change_state(self, state, curr_time):
        """ Advance the state """

        # First, let's compute the time difference
        time_delta = curr_time - self.time

        # Log that time delta
        self.time_record[self.state].append(time_delta)

        # Go ahead and set the new state and reset the timer
        self.state = state
        self.time = curr_time

    def write_log(self):
        """ Write the travelers info to the stat file"""
        with open(TRAVELER_STATS_FILE, 'a') as stat_file:
            travel_writer = csv.writer(stat_file)
            # Every row starts with the start and destnation
            row = [self.start, self.dest]
            # This uses a static list so that the order is fixed
            for state in ["waiting", "riding", "transferring"]:
                state_total = sum(self.time_record[state])
                row.append(state_total)
            travel_writer.writerow(row)

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

        # Passenger state machine
        self.state = PassengerState(self.network.env.now, self.start, self.dest)

        logging.info("[%d] person at %s going to %s",
                     network.env.now, self.start, self.dest)

    def _select_destination(self):
        """Determine where the passenget should go """
        # Ideally this should do something clever based on the start location
        # ie known trips. But for now, it will pick randomly!
        station_dict = self.network.station_dict

        stations = list(station_dict.keys())
        # XXX XXX XXX XXX XXX Remove me!
        stations = [x for x in stations if isinstance(x, int) or x.startswith("801")]
        weights = [station_dict[x].in_popularity for x in stations]

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
        self.state.change_state("riding", self.network.env.now)

    def arrived(self):
        """ If you arrive at destination, log info"""
        self.state.change_state("waiting", self.network.env.now)

        # Write out the log
        self.state.write_log()
