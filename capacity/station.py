"""Basic Station object """

import simpy

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

        # Go ahead and start their action proccesses
        self.gen_load_action = self.network.env.process(self.gen_load())

    def gen_load(self):
        """ Add incoming load"""
        while True:
            self.load.put(1)
            # How often to generate load?
            print("Load at %s is %d"%(self.name, self.load.level))
            yield self.network.env.timeout(2)

    def set_pos(self, lat, lon):
        """ Set the physical location of the station """
        self.pos = (lat, lon)
    def set_pos(self, pos):
        """ Set position with tuple"""
        self.pos = pos

    def print_load(self):
        """ Output the load"""
        print(self.load)
