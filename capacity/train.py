"""Train object """
import datetime
import logging

import numpy as np

class Route(object):
    """ Container object which describes a route """
    def __init__(self, steps):

        # Steps is a list of pairs:
        # (stop, time), ...
        # Where time is the time it is scheduled to arrive
        self.stops = steps

        # We can infer these
        self.origin = steps[0]
        self.terminal = steps[-1]

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

        # Only return the stop itself for now
        return self.stops[index]

    def get_next(self, current):
        """Return the next stop, but dont change anything"""
        index = self.stops.index(current)
        # If its the end of the line
        if index == len(self.stops) - 1:
            # Next is none, so...
            return None

        # Otherwise, spit it out
        return self.stops[index + 1]

    def check_route(self, current):
        index = self.stops.index(current)
        if index == (len(self.stops) - 1):
            return False
        return True


class Train(object):
    """ Basic train service object """
    def __init__(self, network, route, run):
        # pointer to the object we live in
        self.network = network

        self.run = run

        # Usage and cap info
        #self.riders = simpy.Container(self.network.env, self.capacity, 0)
        #self.riders = simpy.FilterStore(self.network.env, self.capacity)
        self.riders = []

        # set the location
        self.location = route.origin

        # set the route
        self.route = route

        # Start running the train
        self.run_line_action = self.network.env.process(self.run_line())

        # Set up any models you may need
        # Boarding delay
        self.boarding_delay = network.config["boarding_delay"]()
        self.alighting_delay = network.config["alighting_delay"]()

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
        # next stop for the passenger

        # Where is the train going next?
        next_train_stop = self.get_next_stop()[0]

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
        if rider.dest == self.location[0]:
            return True

        # Do we need to transfer?
        next_train_stop = self.get_next_stop()
        if next_train_stop == None or next_train_stop[0] != rider.get_next_stop():
            return True

        # Ok if we here:
        #  1) Not at destination
        #  2) Next stop exists and is riders next
        # Stay on the train!
        return False

    def run_line(self):
        """Run line as dictated by the network """

        # Wait until your scheduled time
        start_date = datetime.datetime.strptime(self.location[1], "%Y%m%d %H:%M:%S")
        # How long until you start?
        schedule_pause = start_date.timestamp() - self.network.env.now

        # Sleep it off until you are supposed to start
        yield self.network.env.timeout(schedule_pause)
            
        # Just hardcode a start
        prev_station = (0, 0)

        while True:
            # First figure out what track we are at?
            # Which track will we be entering on?
            track = self.network.station_dict[self.location[0]].get_next_track(prev_station[0])

            with track.request() as track_req:
                start = self.network.env.now
                yield track_req
                stop = self.network.env.now

                if (stop - start) > 0:
                    print(stop - start)

                # ARRIVE AT NEW STATION
                ########## Alighting ###########################
                # Figure out who should get off here
                curr_station = self.network.station_dict[self.location[0]]
                exiting = []
                for rider in self.riders:
                    # Check if they should
                    if self.should_alight(rider):
                        exiting.append(rider)

                # Remove them all from the train
                for rider in exiting:
                    self.riders.remove(rider)
                    # If this was their destination, they arrived!
                    if rider.dest == self.location[0]:
                        rider.arrived()
                        continue
                    # Otherwise, we need to transfer, possibly at a different station
                    transfer = rider.check_transfer()
                    
                    if transfer is not None:
                        # They should go there
                        # Is it last stop?
                        if self.rider.dest == transfer:
                            rider.arrived()
                            continue
                        transfer_station = self.network.station_dict[transfer]
                        rider.route_index += 1
                        # TODO: Edge cast, that was their destination
                        transfer_station.passenger_load.append(rider)
                    else:
                        # They should stay here
                        curr_station.passenger_load.append(rider)
                        

                logging.info("[%d][%s] Train emptied %d at %s",
                             self.network.env.now,
                             self.run,
                             len(exiting),
                             self.network.get_name(self.location[0]))

                # That should take some time...
                a_delay = self.alighting_delay.generate_delay(self.location[0], len(exiting))
                yield self.network.env.timeout(a_delay)

                # Route control:
                # NOTE: For the moment trains are entirely determined by the schedule -- at the end of your route, you just vanish
                if not self.route.check_route(self.location):
                    # Just leave, it's over
                    return

                ########## Boarding ###########################
                # Collect as many passengers as you can from a location
                curr_station = self.network.station_dict[self.location[0]]

                # Take everybody here that needs to get on
                boarding = []
                for passenger in curr_station.passenger_load:
                    # SHould they get on this train?
                    if self.should_board(passenger):
                        # Is there room?
                        room = self.capacity - len(self.riders)
                        # The train is full
                        if room == 0:
                            logging.info("[%d][%s] Train full at %s",
                                         self.network.env.now,
                                         self.run,
                                         self.location[0])
                            break
                        # Get on the train
                        boarding.append(passenger)
                # Remove from station...
                for passenger in boarding:
                    curr_station.passenger_load.remove(passenger)
                    self.riders.append(passenger)
                    passenger.board_vehicle()

                # Log increases
                self.network.stats.log_boarding(self.location[0], len(boarding))

                logging.info("[%d][%s] Train boarded %d at %s",
                             self.network.env.now,
                             self.run,
                             len(boarding), self.network.get_name(self.location[0]))

                # Boarding should consume some time
                b_delay = self.boarding_delay.generate_delay(self.location[0], len(boarding))
                yield self.network.env.timeout(b_delay)

            # Here we've left the station, so we have relinquished the track we were holding

            # Drive to the next station
            src = self.location
            dst = self.route.goto_next(src)

            # Pay the appropriate time penalty...
            distance = self.network.get_distance(src[0], dst[0])
            yield self.network.env.timeout(distance)

            # Update the locations accordingly
            prev_station = src
            self.location = dst
            # Scoot everybody on the train along
            for rider in self.riders:
                rider.route_index += 1

            # Repeat...

    def sample_departures(self, dst):
        """ Figure out how many people get off here """
        # What's the stations out_pop?
        out_pop = self.network.station_dict[dst].out_popularity

        depart = np.random.zipf(1+float(out_pop)/100)

        return depart

class KS_P3010(Train):
    """ A KinkiSharyo P 3010 """
    def __init__(self, network, route, run, cars):
        # Set the capacity accordingly
        self.capacity = 68 * cars #NOTE: Assume 3 cars for now

        # super
        super().__init__(network, route, run)

class Breda_A650(Train):
    """ A Breda A650 Heavy Rail Car """
    def __init__(self, network, route, run, cars):
        # Set the capacity accordingly
        self.capacity = 180 * cars #NOTE: Assume 3 cars for now

        # super
        super().__init__(network, route, run)


