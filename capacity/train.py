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
        #if index + 1 == len(self.stops) - 1:
        #    print("Reversing route...")
        #    self.stops = list(reversed(self.stops))
        #    index = 0

        # Go to the next one
        index += 1

        return self.stops[index]

    def check_route(self, current):
        """ If you're at the end of the line, flip it"""

        if current == self.stops[-1]:
            self.stops = list(reversed(self.stops))

    def get_next(self, current):
        """Return the next stop, but dont change anything"""
        index = self.stops.index(current)
        # If its the end of the line
        if index == len(self.stops) - 1:
            # Next is none, so...
            return None

        # Otherwise, spit it out
        return self.stops[index + 1]

class Train(object):
    """ Basic train service object """
    def __init__(self, location, network, route, run):
        # pointer to the object we live in
        self.network = network

        self.run = run

        # Usage and cap info
        #self.riders = simpy.Container(self.network.env, self.capacity, 0)
        #self.riders = simpy.FilterStore(self.network.env, self.capacity)
        self.riders = []

        # set the location
        self.location = location

        # set the route
        self.route = route

        # Start running the train
        self.run_line_action = self.network.env.process(self.run_line())

        if not hasattr(self, "capacity"):
            self.capacity = 10

    def get_next_stop(self):
        """Where is this train headed to next? """
        return self.route.get_next(self.location)

    def output_riders(self):
        """This function just prints the current riders"""
        print("Riders: %d"%(len(self.riders)))

    def should_board(self, rider):
        """Called by the filterstore at the station  to see which riders whould
        get on the train """

        # Here, we should check to see if the next stop for the train is the
        # next stop for the passanger

        # Where is the train going next?
        next_train_stop = self.get_next_stop()

        # If this train is at the last stop, no boarding
        if next_train_stop is None:
            print("Not boarding because last stop!")
            return False


        # Where do they want to be next?
        next_route_stop = rider.get_next_stop()

        # This train will take you closer!
        # TODO: Someday in the future this should have the riders pick routes and just use those
        # instead of playing games with the routes
        if next_route_stop == next_train_stop:
            return True

        # This train wont!
        return False

    def should_alight(self, rider):
        """Should the rider get off here?"""

        # Are we there?
        if rider.dest == self.location:
            return True

        # TODO: Implement transfers
        return False

    def run_line(self):
        """Run line as dictated by the network """

        # Run Forever right now

        prev_station = 0 # TODO What track does a run start on?

        while True:
            # First figure out what track we are at?
            # Which track will we be entering on?
            track = self.network.station_dict[self.location].get_next_track(prev_station)

            with track.request() as track_req:
                start = self.network.env.now
                yield track_req
                stop = self.network.env.now

                if (stop - start) > 0:
                    print(stop - start)

                # ARRIVE AT NEW STATION
                ########## Alighting ###########################
                # Figure out who should get off here
                exiting = []
                for rider in self.riders:
                    # Check if they should
                    if self.should_alight(rider):
                        exiting.append(rider)

                # Remove them all from the train
                for rider in exiting:
                    self.riders.remove(rider)

                logging.info("[%d][%s] Train emptied %d at %s",
                             self.network.env.now,
                             self.run,
                             len(exiting),
                             self.network.get_name(self.location))

                # TODO That should take some time...
                yield self.network.env.timeout(1)

                # Route control:
                # Reverse the route if needed
                self.route.check_route(self.location)


                ########## Boarding ###########################
                # Collect as many passangers as you can from a location
                curr_station = self.network.station_dict[self.location]

                # Take everybody here that needs to get on
                boarding = []
                for passanger in curr_station.passanger_load:
                    # SHould they get on this train?
                    if self.should_board(passanger):
                        # Is there room?
                        room = self.capacity - len(self.riders)
                        # The train is full
                        if room == 0:
                            logging.info("[%d][%s] Train full at %s",
                                         self.network.env.now,
                                         self.run,
                                         self.location)
                            break
                        # Get on the train
                        boarding.append(passanger)
                # Remove from station...
                for passanger in boarding:
                    curr_station.passanger_load.remove(passanger)
                    self.riders.append(passanger)

                # Log increases
                self.network.stats.log_boarding(self.location, len(boarding))

                logging.info("[%d][%s] Train boarded %d at %s",
                             self.network.env.now,
                             self.run,
                             len(boarding), self.network.get_name(self.location))

                # TODO: Boarding should consume some time
                yield self.network.env.timeout(1)

            # Here we've left the station, so we have relinquished the track we were holding

            # Drive to the next station
            src = self.location
            dst = self.route.goto_next(src)

            # Pay the appropriate time penalty...
            distance = self.network.get_distance(src, dst)
            yield self.network.env.timeout(distance)

            # Update the locations accordingly
            prev_station = src
            self.location = dst

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
    def __init__(self, location, network, route, run, cars):
        # Set the capacity accordingly
        self.capacity = 68 * cars #NOTE: Assume 3 cars for now

        # super
        super().__init__(location, network, route, run)
