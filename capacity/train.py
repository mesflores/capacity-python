"""Train object """

import simpy

class Train(object):
    """ Basic train service object """
    def __init__(self, location, network):
        # pointer to the object we live in
        self.network = network

        # Usage and cap info
        self.capacity = 4
        self.riders = simpy.Container(self.network.env, self.capacity, 0)

        # set the location
        self.location = location

        # Start running the train
        self.run_line_action = self.network.env.process(self.run_line())

    def output_riders(self):
        """This function just prints the current riders"""
        print("Riders: %d"%(self.riders.level))

    def run_line(self):
        """Run line as dictated by the network """

        # Run Forever right now
        while True:
            # Collect as many passangers as you can from a location
            curr_station = self.network.station_dict[self.location]
            boarding = min(curr_station.load.level, self.capacity - self.riders.level)
            # Board the train
            curr_station.load.get(boarding)
            self.riders.put(boarding)

            print("Train boarded %d at %d"%(boarding, self.location))

            # Drive to the next station
            # XXX hard code for example, this should consult the line and graph accordingly
            src = self.location
            if src == 1:
                dst = 2
            else:
                dst = 1
            # XXX XXX XXX

            distance = self.network.get_distance(src, dst)
            yield self.network.env.timeout(distance)
            self.location = dst

            print("Train emptied %d at %d"%(self.riders.level, self.location))
            # Drop passangers off. Assumes every one wants off here...
            self.riders.get(self.riders.level)

            # Repeat...
