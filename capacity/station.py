"""Basic Station object """

import simpy

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

        # Stations start at 0 load
        self.load = simpy.Container(self.network.env, init=0)

        # Popularity
        self.out_popularity = 20 # Likelihood of stopping here
        self.in_popularity = 100 # Arrivals

        # Placeholder position
        self.pos = None

        # Go ahead and start their action proccesses
        self.gen_load_action = self.network.env.process(self.gen_load())

    def gen_load(self):
        """ Add incoming load"""
        while True:
            self.load.put(1)
            # Generate load based on poisson arrivals
            #TODO: I dunno pick a better one
            gap = int(utils.poisson_arrival(self.in_popularity))
            yield self.network.env.timeout(gap)

    def set_pos(self, pos):
        """ Set position with tuple"""
        self.pos = pos

    def print_load(self):
        """ Output the load"""
        print(self.load)
