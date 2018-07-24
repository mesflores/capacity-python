"""Basic Station object """

import simpy

import capacity.traveler as traveler
import capacity.utils as utils

class Station(object):
    """basic Station object """
    def __init__(self, station_id, name, network):
        """ Create a new station with given ID"""
        # Keep a pointer to the network object you live in
        self.network = network

        # Station Meta data
        self.station_id = station_id
        self.name = name

        # Stations have infinite capacity. Fine for now...
        #self.passenger_load = simpy.FilterStore(self.network.env)
        self.passenger_load = []

        # Tracks
        # For now assume every station has two tracks (will get fancy, someday)
        # Track from the the lower indexed station
        self.track_a = simpy.Resource(network.env, capacity=1)
        # Track from the higher indexed station
        self.track_b = simpy.Resource(network.env, capacity=1)


        # Popularity
        self.out_popularity = 20 # Likelihood of stopping here
        self.in_popularity = 10 # Arrivals

        # Placeholder position
        self.pos = None

        # Go ahead and start their action proccesses
        self.gen_load_action = self.network.env.process(self.gen_load())

    def gen_load(self):
        """ Add incoming load"""
        while True:
            # Generate a new passenger
            new_pass = traveler.Passenger(self.station_id, self.network)

            if new_pass.dest != self.station_id:
                # Put them into the local store
                #self.passenger_load.put(new_pass)
                self.passenger_load.append(new_pass)

            # Generate load based on poisson arrivals
            #TODO: I dunno pick a better one
            gap = int(utils.poisson_arrival(self.in_popularity))
            yield self.network.env.timeout(gap)

    def set_pos(self, pos):
        """ Set position with tuple"""
        self.pos = pos

    def print_load(self):
        """ Output the load"""
        print(len(self.passenger_load))

    def get_next_track(self, src):
        """Figure out what track it would need to get here from src"""
        # Check the station ordering, give the right track
        # WARN: this int cast might be dangerous
        if int(src) < int(self.station_id):
            # Came from a lower station
            return self.track_a

        return self.track_b
