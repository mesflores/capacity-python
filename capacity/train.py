"""Train object """

import logging

import numpy as np
import simpy

class Route(object):
    """ Container object which describes a route """
    def __init__(self, origin, terminal, steps):
        self.origin = origin
        self.terminal = terminal

        self.stops = steps

    def goto_next(self, current):
        """ get the next stop """
        # Get the index, as stops must be unique
        index = self.stops.index(current)

        # If its the last stop, reverse, for now I guess
        if index == len(self.stops) - 1:
            self.stops = list(reversed(self.stops))
            index = 0

        # Go to the next one
        index += 1

        return self.stops[index]

class Train(object):
    """ Basic train service object """
    def __init__(self, location, network, route):
        # pointer to the object we live in
        self.network = network

        # Usage and cap info
        #self.riders = simpy.Container(self.network.env, self.capacity, 0)
        self.riders = simpy.FilterStore(self.network.env, self.capacity)

        # set the location
        self.location = location

        # set the route
        self.route = route

        # Start running the train
        self.run_line_action = self.network.env.process(self.run_line())

    def get_next_stop(self):
        """Where is this train headed to next? """
        # TODO Write this...
        raise NotImplementedError

    def output_riders(self):
        """This function just prints the current riders"""
        print("Riders: %d"%(len(self.riders.items)))

    def should_board(self, rider):
        """Called by the filterstore at the station  to see which riders whould
        get on the train """

        # Here, we should check to see if the next stop for the train is the
        # next stop for the passanger

        # Where do they want to be next?
        next_route_stop = rider.get_next_stop()

        # Where is the train going next?
        next_train_stop = self.get_next_stop()

        # This train will take you closer!
        # TODO: Someday in the future this should have the riders pick routes and just use those
        # instead of playing games with the routes
        if next_route_stop == next_train_stop:
            return True

        # This train wont!
        return False

    def run_line(self):
        """Run line as dictated by the network """

        # Run Forever right now
        while True:
            # Collect as many passangers as you can from a location
            curr_station = self.network.station_dict[self.location]
            boarding = min(curr_station.load.level, self.capacity - self.riders.level)
            # Board the train
            if boarding > 0:
                curr_station.load.get(boarding)
                self.riders.put(boarding)

                # Log increases
                self.network.stats.log_boarding(self.location, boarding)

            logging.info("[%d] Train boarded %d at %s",
                         self.network.env.now,
                         boarding, self.network.get_name(self.location))

            # Drive to the next station
            src = self.location
            dst = self.route.goto_next(src)

            distance = self.network.get_distance(src, dst)
            yield self.network.env.timeout(distance)

            self.location = dst

            logging.info("[%d] Train emptied %d at %s",
                         self.network.env.now,
                         self.riders.level,
                         self.network.get_name(self.location))
            # Drop passangers off.
            drop_count = min(self.riders.level, self.sample_departures(self.location))
            if drop_count > 0:
                self.riders.get(drop_count)

            # Repeat...

    def sample_departures(self, dst):
        """ Figure out how many people get off here """
        # What's the stations out_pop?
        out_pop = self.network.station_dict[dst].out_popularity

        # TODO: pick something real
        depart = np.random.zipf(1+float(out_pop)/100)

        return depart

class KS_P3010(Train):
    """ A KinkiSharyo P 3010 """
    def __init__(self, location, network, route, cars):
        # Set the capacity accordingly
        self.capacity = 68 * cars #NOTE: Assume 3 cars for now

        # super
        super().__init__(location, network, route)
