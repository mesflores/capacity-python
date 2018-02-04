"""stats.py basic statistics collection and output """

import logging
import os
import os.path

class NetworkStats(object):
    """Object for collecting stats info"""
    def __init__(self):

        self.total_boardings = 0
        self.station_boardings = {}

        # Place we dump everything
        self.out_file = None

        # Last reset
        self.last_reset = None

    def init_output(self, out_file):
        """Set the output file """
        self.out_file = out_file
        # delete if it exists
        if os.path.isfile(out_file):
            os.remove(out_file)

    def add_station(self, station):
        """ Add a station to the station list """
        self.station_boardings[station] = 0

    def reset_all(self, time):
        """ Reset all counters to 0 """
        self.total_boardings = 0
        for station in self.station_boardings:
            self.station_boardings[station] = 0

        # Set the timer to now
        self.last_reset = time

    def log_boarding(self, station, boarding):
        """Record a boarding"""
        # Add the total
        self.total_boardings += boarding
        # Add this station
        self.station_boardings[station] += boarding

    def periodic_output(self, env, interval=3600, station_filter=None):
        """ loop to handle regular stat output """
        while True:
            # Dump stats
            self.output_stats(env.now, station_filter)
            # reset it all
            self.reset_all(env.now)

            yield env.timeout(interval)

    def output_stats(self, time, station_filter=None):
        """Dump all the useful stats"""
        if self.out_file is None:
            logging.warning("Called output with no output file set!")
            return

        with open(self.out_file, 'a') as out_f:
            # Dump the totals
            out_f.write("%d, %d\n"%(time,
                                    self.total_boardings))
            # Dump each station
            for station in self.station_boardings:
                # Did  wed get a filter?
                if station_filter and station_filter not in str(station):
                    continue
                out_f.write("\t%s\t\t%d\n"%(station,
                                            self.station_boardings[station]))
