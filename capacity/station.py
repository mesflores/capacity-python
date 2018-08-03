"""Basic Station object """

import simpy

import capacity.traveler as traveler
import capacity.utils as utils

def tod_weight(current_tod, popularity):
    """ Determine the scale factor based on TOD"""
    # let's start with some stupid hard rules 

    magnitude = 1.5

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
        self.out_popularity = .5 # Likelihood of stopping here
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
            gap = int(utils.poisson_arrival(tod_weight(self.network.env.now, self.out_popularity)))
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
